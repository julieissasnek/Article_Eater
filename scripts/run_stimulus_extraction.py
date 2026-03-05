#!/usr/bin/env python3
"""
Stimulus Description Re-Extraction — Backfill Missing Stimulus Data
=====================================================================

Runs through existing extraction JSONs and identifies findings that
need stimulus descriptions populated. For each article missing stimulus
data, queues a focused re-extraction that asks Gemini ONLY for the
stimulus_description and stimulus_images fields.

This is a SURGICAL update — it does NOT re-extract the entire paper.
It reads the existing extraction, identifies findings missing stimulus
data, and asks Gemini to fill in JUST the stimulus fields.

Usage:
    # Analysis only — show what needs backfill
    python scripts/run_stimulus_extraction.py --analyze

    # Run re-extraction on top 50 articles (most findings needing backfill)
    python scripts/run_stimulus_extraction.py --max-articles 50

    # Run for specific article types
    python scripts/run_stimulus_extraction.py --article-type empirical --max-articles 100

    # Dry run — show what would happen
    python scripts/run_stimulus_extraction.py --dry-run --max-articles 20

    # Monitor progress
    python scripts/run_stimulus_extraction.py --status

This script is designed to run in a SEPARATE terminal from card generation.
It can run alongside AG and CC card generation without conflicts.

Success Conditions:
    SC-STIM-1: Surgical extraction updates ONLY stimulus fields, preserving all other data
    SC-STIM-2: Updated findings pass ExtractionFieldValidator stimulus rules (ST1-ST6)
    SC-STIM-3: Coverage increases monotonically (never decreases) after backfill run
    SC-STIM-4: _stimulus_backfill metadata added to each updated article
    SC-STIM-5: Script is idempotent — running twice on same article produces same result
    SC-STIM-6: Analysis mode (--analyze) never modifies any files

Author: CW (Claude/Cowork)
Date: 2026-03-04
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)

# Sensory terms that indicate a finding should have stimulus_description
SENSORY_TERMS = {
    "light", "lighting", "lux", "illumin", "bright", "dark", "dim",
    "sound", "noise", "acoustic", "decibel", "dB", "music", "auditory",
    "room", "space", "office", "classroom", "hospital", "building",
    "color", "colour", "hue", "chromat", "CCT", "warm white", "cool white",
    "temperature", "thermal", "humid", "ventilat", "air quality",
    "smell", "odor", "scent", "fragrance", "aroma", "olfactory",
    "view", "window", "nature", "green", "plant", "biophil",
    "material", "wood", "concrete", "stone", "glass", "fabric", "texture",
    "ceiling", "floor", "wall", "furniture", "layout", "dimension",
    "VR", "virtual reality", "simulation", "rendering", "photo", "image",
}

# Focused re-extraction prompt for stimulus fields ONLY
STIMULUS_EXTRACTION_PROMPT = """
You are re-examining an already-extracted research paper to add MISSING stimulus description data.

The paper has already been fully extracted. The findings below are from that extraction.
Your ONLY job is to add stimulus_description and stimulus_images for each finding.

## What to Extract

For EACH finding listed below, provide:

1. **stimulus_description**: An object with:
   - primary_type: One of [visual_scene, soundscape, thermal, olfactory, spatial, lighting, material, mixed]
   - components: Array of objects, each with:
     - name: What this component is (e.g., "LED panel at 4000K, 500 lux")
     - category: One of [spatial, lighting, acoustic, thermal, olfactory, material, visual, social]
     - essential: true if this component is the independent variable, false if background
   - delivery_method: One of [in_situ, VR, photo, video, audio, imagined]
   - duration_seconds: Exposure duration (null if continuous/not measured)

2. **stimulus_images**: Array of objects with:
   - description: What the image shows
   - figure_ref: Paper reference (e.g., "Figure 2A")
   - image_type: One of [photo, rendering, diagram, floor_plan, graph]

## Critical Instructions

- DESCRIBE WHAT THE PARTICIPANT ACTUALLY EXPERIENCED. Not the abstract concept — the physical reality.
- For architectural studies: room dimensions, ceiling height, window area, material finishes, furniture
- For lighting studies: lux levels, CCT (Kelvin), spectrum info, fixture type, distribution pattern
- For acoustic studies: dB levels, frequency content, source type (traffic, HVAC, music, speech)
- For thermal studies: temperature °C, humidity %, air velocity, radiant vs. convective
- If the paper doesn't provide specific values, note "not specified in paper" but still describe what was used
- Reference figure numbers from the paper whenever possible
- Note if the stimulus was a real environment, photo, VR, or imagined

## Findings to Process

{findings_json}

## Output Format

Return a JSON array with one entry per finding:
```json
[
  {{
    "finding_index": 0,
    "stimulus_description": {{
      "primary_type": "lighting",
      "components": [
        {{"name": "LED panel, 4000K CCT, 500 lux at desk level", "category": "lighting", "essential": true}},
        {{"name": "Standard office, 3m x 4m, white walls", "category": "spatial", "essential": false}}
      ],
      "delivery_method": "in_situ",
      "duration_seconds": 3600
    }},
    "stimulus_images": [
      {{"description": "Photo of experimental office setup showing LED panel and participant workspace", "figure_ref": "Figure 1", "image_type": "photo"}}
    ]
  }}
]
```
"""


def load_extractions(extractions_dir: Path) -> List[Tuple[Path, Dict]]:
    """Load all extraction JSONs."""
    results = []
    for f in sorted(extractions_dir.glob("*.json")):
        try:
            with open(f) as fh:
                data = json.load(fh)
            if "findings" in data and len(data.get("findings", [])) > 0:
                results.append((f, data))
        except (json.JSONDecodeError, Exception) as e:
            logger.debug(f"Skipping {f.name}: {e}")
    return results


def needs_stimulus_backfill(finding: Dict) -> bool:
    """Check if a finding needs stimulus description backfill."""
    stim = finding.get("stimulus_description")
    if stim and isinstance(stim, dict) and stim.get("primary_type"):
        return False  # Already has stimulus data

    # Check if antecedent suggests sensory content
    antecedent = (finding.get("antecedent") or "").lower()
    for term in SENSORY_TERMS:
        if term.lower() in antecedent:
            return True

    return False


def analyze_extractions(extractions: List[Tuple[Path, Dict]]) -> Dict:
    """Analyze stimulus coverage across all extractions."""
    total_findings = 0
    findings_with_stimulus = 0
    findings_needing_backfill = 0
    articles_needing_backfill = []

    for path, data in extractions:
        article_needs = 0
        article_has = 0
        article_total = 0

        for finding in data.get("findings", []):
            total_findings += 1
            article_total += 1

            stim = finding.get("stimulus_description")
            if stim and isinstance(stim, dict) and stim.get("primary_type"):
                findings_with_stimulus += 1
                article_has += 1
            elif needs_stimulus_backfill(finding):
                findings_needing_backfill += 1
                article_needs += 1

        if article_needs > 0:
            articles_needing_backfill.append({
                "path": str(path),
                "doi": data.get("doi", path.stem),
                "title": data.get("title", "Unknown")[:80],
                "total_findings": article_total,
                "needs_backfill": article_needs,
                "has_stimulus": article_has,
            })

    # Sort by most findings needing backfill
    articles_needing_backfill.sort(key=lambda x: x["needs_backfill"], reverse=True)

    return {
        "total_articles": len(extractions),
        "total_findings": total_findings,
        "findings_with_stimulus": findings_with_stimulus,
        "findings_needing_backfill": findings_needing_backfill,
        "coverage_pct": round(findings_with_stimulus / max(total_findings, 1) * 100, 1),
        "articles_needing_backfill": len(articles_needing_backfill),
        "top_articles": articles_needing_backfill[:20],
    }


def run_surgical_extraction(
    article_path: Path,
    article_data: Dict,
    dry_run: bool = False,
) -> Dict:
    """
    Run surgical stimulus extraction for one article.

    This calls Gemini (or another extraction model) with ONLY the
    stimulus extraction prompt, not the full extraction prompt.
    """
    findings = article_data.get("findings", [])
    findings_to_process = []

    for i, finding in enumerate(findings):
        if needs_stimulus_backfill(finding):
            findings_to_process.append({
                "finding_index": i,
                "antecedent": finding.get("antecedent", ""),
                "consequent": finding.get("consequent", ""),
                "direction": finding.get("direction", ""),
                "source": finding.get("source", ""),
                "study_design": finding.get("study_design", ""),
            })

    if not findings_to_process:
        return {"status": "skip", "reason": "no findings need backfill"}

    if dry_run:
        return {
            "status": "dry_run",
            "findings_to_process": len(findings_to_process),
            "doi": article_data.get("doi", article_path.stem),
        }

    # Build the prompt
    prompt = STIMULUS_EXTRACTION_PROMPT.format(
        findings_json=json.dumps(findings_to_process, indent=2)
    )

    # Call extraction model (Gemini preferred for bulk, or session model)
    try:
        from src.services.llm_query_bridge import GoogleProvider, MODEL_REGISTRY
        provider = GoogleProvider()
        config = MODEL_REGISTRY.get("gemini-flash")  # Cheap, fast

        if provider and config:
            response_text, in_tok, out_tok = provider.complete(prompt, config)
        else:
            logger.warning("Google provider not available")
            return {"status": "error", "reason": "no provider"}

    except ImportError:
        logger.warning("llm_query_bridge not available for extraction")
        return {"status": "error", "reason": "import error"}
    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        return {"status": "error", "reason": str(e)}

    # Parse response
    try:
        # Extract JSON array from response
        json_start = response_text.find("[")
        json_end = response_text.rfind("]") + 1
        if json_start >= 0 and json_end > json_start:
            stimulus_data = json.loads(response_text[json_start:json_end])
        else:
            return {"status": "error", "reason": "no JSON in response"}
    except json.JSONDecodeError as e:
        return {"status": "error", "reason": f"JSON parse error: {e}"}

    # Apply stimulus data back to findings
    applied = 0
    for entry in stimulus_data:
        # Skip non-dict entries (malformed LLM response)
        if not isinstance(entry, dict):
            continue
        idx = entry.get("finding_index")
        if idx is not None and 0 <= idx < len(findings):
            if entry.get("stimulus_description"):
                findings[idx]["stimulus_description"] = entry["stimulus_description"]
                applied += 1
            if entry.get("stimulus_images"):
                findings[idx]["stimulus_images"] = entry["stimulus_images"]

    # Save updated extraction
    if applied > 0:
        article_data["findings"] = findings
        article_data["_stimulus_backfill"] = {
            "date": time.strftime("%Y-%m-%d"),
            "findings_updated": applied,
            "total_processed": len(findings_to_process),
        }
        with open(article_path, "w") as f:
            json.dump(article_data, f, indent=2)
        logger.info(f"Updated {applied}/{len(findings_to_process)} findings in {article_path.name}")

    return {
        "status": "success",
        "applied": applied,
        "processed": len(findings_to_process),
        "doi": article_data.get("doi", article_path.stem),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Stimulus description re-extraction (surgical backfill)"
    )
    parser.add_argument("--analyze", action="store_true", help="Analysis only")
    parser.add_argument("--dry-run", action="store_true", help="Show plan without executing")
    parser.add_argument("--max-articles", type=int, default=0, help="Max articles to process")
    parser.add_argument("--article-type", help="Filter by article type (e.g., empirical)")
    parser.add_argument("--status", action="store_true", help="Show current coverage status")
    parser.add_argument("--output", help="Save analysis to JSON file")

    args = parser.parse_args()

    extractions_dir = PROJECT_ROOT / "data" / "extractions"
    if not extractions_dir.exists():
        print(f"No extractions directory at {extractions_dir}")
        return

    # Load extractions
    logger.info("Loading extractions...")
    extractions = load_extractions(extractions_dir)
    logger.info(f"Loaded {len(extractions)} articles")

    # Filter by type if specified
    if args.article_type:
        extractions = [
            (p, d) for p, d in extractions
            if d.get("article_type", "").lower() == args.article_type.lower()
        ]
        logger.info(f"Filtered to {len(extractions)} {args.article_type} articles")

    # Analyze
    analysis = analyze_extractions(extractions)

    if args.analyze or args.status:
        print(f"\n{'='*60}")
        print(f"STIMULUS COVERAGE ANALYSIS")
        print(f"{'='*60}")
        print(f"  Total articles:            {analysis['total_articles']}")
        print(f"  Total findings:            {analysis['total_findings']}")
        print(f"  With stimulus description: {analysis['findings_with_stimulus']} "
              f"({analysis['coverage_pct']}%)")
        print(f"  Needing backfill:          {analysis['findings_needing_backfill']}")
        print(f"  Articles needing work:     {analysis['articles_needing_backfill']}")
        print(f"\nTop articles by backfill need:")
        for i, art in enumerate(analysis["top_articles"][:10], 1):
            print(f"  {i}. {art['doi'][:40]}")
            print(f"     {art['title']}")
            print(f"     {art['needs_backfill']}/{art['total_findings']} findings need stimulus")
        print(f"{'='*60}\n")

        if args.output:
            with open(args.output, "w") as f:
                json.dump(analysis, f, indent=2)
            print(f"Analysis saved to {args.output}")
        return

    # Run extraction
    articles_to_process = [
        (p, d) for p, d in extractions
        if any(needs_stimulus_backfill(f) for f in d.get("findings", []))
    ]
    articles_to_process.sort(
        key=lambda x: sum(1 for f in x[1].get("findings", []) if needs_stimulus_backfill(f)),
        reverse=True,
    )

    if args.max_articles > 0:
        articles_to_process = articles_to_process[:args.max_articles]

    print(f"\nProcessing {len(articles_to_process)} articles for stimulus extraction...")

    results = {"success": 0, "error": 0, "skip": 0, "dry_run": 0}
    total_applied = 0

    for i, (path, data) in enumerate(articles_to_process, 1):
        doi = data.get("doi", path.stem)
        logger.info(f"[{i}/{len(articles_to_process)}] {doi[:50]}")

        result = run_surgical_extraction(path, data, dry_run=args.dry_run)
        results[result["status"]] = results.get(result["status"], 0) + 1
        total_applied += result.get("applied", 0)

        if i % 10 == 0:
            logger.info(f"  Progress: {i}/{len(articles_to_process)}, "
                        f"{total_applied} findings updated")

    print(f"\n{'='*60}")
    print(f"STIMULUS EXTRACTION COMPLETE")
    print(f"{'='*60}")
    print(f"  Articles processed: {len(articles_to_process)}")
    print(f"  Successful:         {results.get('success', 0)}")
    print(f"  Errors:             {results.get('error', 0)}")
    print(f"  Findings updated:   {total_applied}")
    if args.dry_run:
        print(f"  (DRY RUN — no changes made)")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
