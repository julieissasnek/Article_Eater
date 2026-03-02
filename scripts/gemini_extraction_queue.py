#!/usr/bin/env python3
"""Gemini Extraction Queue Manager.

Manages the extraction pipeline:
1. Loads triage results
2. Selects appropriate prompts per article type
3. Runs extraction with 2-run verification
4. Handles failures and retries
5. Tracks progress

Usage:
    python scripts/gemini_extraction_queue.py --type empirical --limit 10
    python scripts/gemini_extraction_queue.py --all --batch-size 50
    python scripts/gemini_extraction_queue.py --status
    python scripts/gemini_extraction_queue.py --resume
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

from google import genai
from google.genai import types

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# OC-3: Outcome Resolver Integration
try:
    from lib.outcome_resolver import resolve_outcome
    HAS_OUTCOME_RESOLVER = True
except ImportError:
    HAS_OUTCOME_RESOLVER = False

# Paths
AF_ROOT = Path("/Users/davidusa/REPOS/Article_Finder_v3_2_3")
PDF_DIR = AF_ROOT / "data" / "pdfs"
TRIAGE_FILE = PROJECT_ROOT / "data" / "triage" / "keyword_triage.json"
OUTPUT_DIR = PROJECT_ROOT / "data" / "extractions"
QUEUE_STATE_FILE = OUTPUT_DIR / "queue_state.json"

# Pricing per 1M tokens
PRICING = {
    "gemini-2.5-flash": {"input": 0.15, "output": 0.60},
    "gemini-2.5-pro": {"input": 1.25, "output": 10.00},
}


class ExtractionStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    NEEDS_VERIFICATION = "needs_verification"


@dataclass
class QueueItem:
    doi: str
    article_type: str
    pdf_path: str
    status: ExtractionStatus = ExtractionStatus.PENDING
    run1_result: dict | None = None
    run2_result: dict | None = None
    run3_result: dict | None = None
    final_result: dict | None = None
    error: str | None = None
    attempts: int = 0
    total_cost: float = 0.0
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str | None = None


# ============================================================================
# ARTICLE-TYPE-SPECIFIC PROMPTS
# ============================================================================

PROMPT_BASE = """You are extracting structured data from a scientific paper.
Return ONLY valid JSON. No explanations, no markdown code blocks.
If a field is not available, use null.

THEORETICAL FRAMEWORKS (identify which predict findings):
T1 Frameworks:
- PP: Predictive Processing (prediction error, precision, active inference)
- SN: Spatial Navigation / Cognitive Mapping (place cells, grid cells, hippocampus)
- DP: Dual-Process Evaluation (System 1/2, fluency, aesthetic response)
- DT: DMN/TPN Dynamics (default mode, task-positive, mind-wandering)
- NM: Neuromodulatory Systems (dopamine, cortisol, serotonin, oxytocin)
- IC: Interoceptive / Constructionist Affect (Barrett, body-budget, allostasis)
- MS: Memory Systems (episodic, semantic, procedural, working memory)
- EC: Embodied Cognition (enactivism, affordances, motor simulation)
- CB: Chronobiological Regulation (circadian, ultradian, melatonin, light)
- MSI: Multisensory Integration (binding, crossmodal, spatial attention)

Domain Theories:
- ART: Attention Restoration Theory (Kaplan - soft fascination, being away)
- SRT: Stress Recovery Theory (Ulrich - nature reduces stress)
- Biophilia: Innate affiliation with nature (Wilson, Kellert)
- Prospect-Refuge: Safe vantage points (Appleton)
- Privacy Regulation: Personal space control (Altman)

CNFA Domains (classify environmental features):
- A1_Materials: wood, concrete, stone, texture, biophilic materials
- A2_Spatial_Scale: ceiling height, volume, proportion, spaciousness
- A3_Spatial_Config: layout, wayfinding, circulation, space syntax
- A4_Light: daylight, illuminance, circadian, glare, window views
- A5_Acoustic: noise, reverberation, soundscape, speech privacy
- A6_Visual_Form: color, pattern, fractal, curvature, aesthetic
- A7_Haptic_Thermal: temperature, comfort, touch, HVAC
- A8_Social: privacy, collaboration, density, personal space
- A9_Task_Cognition: attention, memory, creativity, performance
- A10_Temporal: exposure duration, adaptation, circadian timing
"""

EMPIRICAL_PROMPT = PROMPT_BASE + """
This is an EMPIRICAL study (experiment, survey, field study).

Extract all statistical findings as a JSON object:
{
  "article_type": "empirical",
  "title": "paper title",
  "n_participants": number or null,
  "study_design": "experiment|survey|field_study|observational|case_study|mixed",
  "findings": [
    {
      "id": 1,
      "antecedent": "environmental feature (be specific, e.g., 'ceiling height > 3m' not just 'ceiling')",
      "consequent": "human response (be specific, e.g., 'creative ideation scores' not just 'creativity')",
      "direction": "increase|decrease|no_effect",
      "claim_type": "causal|associational|moderated|null",
      "measure_type": "physiological|behavioral|self_report|cognitive|performance",
      "p_value": "exact (e.g., 0.003) or threshold (e.g., <0.05)",
      "effect_size": number or null,
      "effect_size_type": "Cohen_d|r|eta_squared|beta|odds_ratio|null",
      "sample_size": number,
      "confidence_interval": [lower, upper] or null,
      "theory_links": ["PP", "SN", "DP", "DT", "NM", "IC", "MS", "EC", "CB", "MSI", "ART", "SRT", "Biophilia"],
      "mechanism": "theoretical explanation if mentioned",
      "source": "Table X or text",
      "quote": "exact supporting quote (max 100 chars)"
    }
  ],
  "domains": ["A1_Materials", "A4_Light", etc],
  "overall_theory_links": ["frameworks that guide this paper's hypotheses"],
  "stimuli": [
    {
      "type": "photograph|rendering|VR|video|physical_space|audio|other",
      "description": "what the stimulus showed (e.g., 'images of high vs low ceiling rooms')",
      "n_stimuli": number or null,
      "source": "Figure N or description location"
    }
  ],
  "tables": [
    {
      "table_id": "Table 1",
      "description": "what the table shows (e.g., 'regression coefficients for light on mood')",
      "key_stats": ["F(2,45)=3.2, p<.05", "R²=.24"]
    }
  ],
  "limitations": ["stated limitations"]
}

CRITICAL RULES:
1. theory_links MUST be populated for every finding - which frameworks predict this effect?
2. p_value and effect_size are CRITICAL - search tables, figures, text carefully
3. Extract EVERY finding including null results (direction="no_effect", claim_type="null")
4. Be specific with antecedent/consequent - include levels, thresholds, operationalizations
5. For regression: predictors = antecedent, criterion = consequent
6. For correlation: each significant cell is a separate finding
7. For ANOVA: each main effect and interaction is a finding
"""

META_ANALYSIS_PROMPT = PROMPT_BASE + """
This is a META-ANALYSIS (quantitative synthesis of multiple studies).

Extract pooled effects as a JSON object:
{
  "article_type": "meta_analysis",
  "title": "paper title",
  "k_studies": number of studies included,
  "total_n": total sample size,
  "pooled_effects": [
    {
      "id": 1,
      "antecedent": "intervention/exposure (be specific)",
      "consequent": "outcome (be specific)",
      "direction": "increase|decrease|no_effect",
      "effect_size": number,
      "effect_size_type": "SMD|d|r|OR|RR|HR",
      "ci_lower": number,
      "ci_upper": number,
      "p_value": "value",
      "k": number of studies for this effect,
      "I_squared": heterogeneity percentage,
      "theory_links": ["PP", "SN", "DP", "DT", "NM", "IC", "MS", "EC", "CB", "MSI", "ART", "SRT", "Biophilia"],
      "source": "Table/Figure reference"
    }
  ],
  "moderators": [
    {
      "variable": "moderator name",
      "effect": "description of moderation",
      "significant": true|false
    }
  ],
  "publication_bias": "assessment if reported",
  "domains": ["A1_Materials", "A4_Light", etc],
  "overall_theory_links": ["frameworks that guide this meta-analysis"]
}

NOTE: Populate theory_links when frameworks clearly apply; leave empty array [] if no theory is evident.
"""

SYSTEMATIC_REVIEW_PROMPT = PROMPT_BASE + """
This is a SYSTEMATIC REVIEW (structured literature synthesis).

Extract synthesized findings as a JSON object:
{
  "article_type": "systematic_review",
  "title": "paper title",
  "n_studies_included": number,
  "review_protocol": "PRISMA|other|not_specified",
  "findings": [
    {
      "id": 1,
      "antecedent": "factor (be specific)",
      "consequent": "outcome (be specific)",
      "direction": "increase|decrease|mixed|unclear",
      "evidence_strength": "strong|moderate|weak|inconsistent",
      "n_studies": number supporting this finding,
      "theory_links": ["PP", "SN", "DP", "DT", "NM", "IC", "MS", "EC", "CB", "MSI", "ART", "SRT", "Biophilia"],
      "key_citations": ["Author, Year"],
      "quote": "supporting synthesis statement"
    }
  ],
  "gaps": ["identified research gaps"],
  "quality_assessment": "description of bias/quality findings",
  "domains": ["A1_Materials", "A4_Light", etc],
  "overall_theory_links": ["frameworks that guide this review"]
}

NOTE: Populate theory_links when frameworks clearly apply; leave empty array [] if no theory is evident.
"""

NARRATIVE_REVIEW_PROMPT = PROMPT_BASE + """
This is a NARRATIVE REVIEW (literature overview/synthesis).

Extract key claims as a JSON object:
{
  "article_type": "narrative_review",
  "title": "paper title",
  "scope": "description of review scope",
  "findings": [
    {
      "id": 1,
      "antecedent": "factor (be specific)",
      "consequent": "outcome (be specific)",
      "direction": "increase|decrease|mixed|unclear",
      "evidence_basis": "cited|claimed|speculated",
      "theory_links": ["PP", "SN", "DP", "DT", "NM", "IC", "MS", "EC", "CB", "MSI", "ART", "SRT", "Biophilia"],
      "key_citations": ["Author, Year"],
      "quote": "supporting statement"
    }
  ],
  "mechanisms": [
    {
      "name": "theory/mechanism name",
      "description": "how it works",
      "theory_links": ["relevant framework codes"],
      "evidence_level": "established|proposed|speculative"
    }
  ],
  "future_directions": ["suggested research"],
  "domains": ["A1_Materials", "A4_Light", etc],
  "overall_theory_links": ["frameworks that guide this review"]
}

NOTE: Populate theory_links when frameworks clearly apply; leave empty array [] if no theory is evident.
"""

THEORETICAL_PROMPT = PROMPT_BASE + """
This is a THEORETICAL paper (framework, model, perspective).

Extract propositions as a JSON object:
{
  "article_type": "theoretical",
  "title": "paper title",
  "central_proposition": "main theoretical claim",
  "concepts": [
    {
      "name": "concept name",
      "definition": "how defined in paper"
    }
  ],
  "propositions": [
    {
      "id": 1,
      "antecedent": "proposed cause/factor (be specific)",
      "consequent": "proposed effect/outcome (be specific)",
      "direction": "increase|decrease|modulates",
      "mechanism": "how/why this works",
      "theory_links": ["PP", "SN", "DP", "DT", "NM", "IC", "MS", "EC", "CB", "MSI", "ART", "SRT", "Biophilia"],
      "testable": true|false,
      "quote": "supporting text"
    }
  ],
  "empirical_support": ["cited evidence if any"],
  "domains": ["A1_Materials", "A4_Light", etc],
  "overall_theory_links": ["frameworks that guide this paper"]
}

NOTE: Populate theory_links when frameworks clearly apply; leave empty array [] if no theory is evident.
"""

QUALITATIVE_PROMPT = PROMPT_BASE + """
This is a QUALITATIVE study (interviews, ethnography, phenomenology).

Extract themes as a JSON object:
{
  "article_type": "qualitative",
  "title": "paper title",
  "methodology": "interview|ethnography|grounded_theory|phenomenology|focus_group",
  "n_participants": number,
  "participant_description": "who was studied",
  "themes": [
    {
      "id": 1,
      "theme_name": "name of theme",
      "description": "what this theme means",
      "antecedents": ["contributing factors if identified"],
      "consequences": ["outcomes if identified"],
      "supporting_quotes": ["participant quote 1", "quote 2"],
      "saturation": "saturated|emerging|limited"
    }
  ],
  "transferability": "contexts where findings may apply",
  "domains": ["A1_Materials", "A4_Light", etc],
  "theory_links": ["identified frameworks, theories, or models guiding this work"]
}
"""

METHODS_PROMPT = PROMPT_BASE + """
This is a METHODS paper (protocol, instrument, guidelines).

Extract methodology details as a JSON object:
{
  "article_type": "methods",
  "title": "paper title",
  "method_type": "protocol|instrument|guidelines|validation",
  "target_construct": "what it measures/does",
  "components": [
    {
      "name": "component name",
      "description": "what it does",
      "validation": "how validated if reported"
    }
  ],
  "psychometric_properties": {
    "reliability": "value/description",
    "validity": "value/description"
  },
  "recommended_use": "how authors suggest using this",
  "domains": ["A1_Materials", "A4_Light", etc],
  "theory_links": ["identified frameworks, theories, or models guiding this work"]
}
"""

UNKNOWN_PROMPT = PROMPT_BASE + """
The article type is unknown. First classify it, then extract relevant information.

Return:
{
  "detected_article_type": "empirical|meta_analysis|systematic_review|narrative_review|theoretical|qualitative|methods|other",
  "classification_confidence": 0.0-1.0,
  "classification_signals": ["indicators that led to classification"],
  "title": "paper title",
  "key_claims": [
    {
      "claim": "main claim or finding",
      "antecedent": "factor/cause if identifiable (be specific)",
      "consequent": "outcome/effect if identifiable (be specific)",
      "direction": "increase|decrease|no_effect|unclear",
      "evidence_type": "statistical|cited|claimed|theoretical",
      "theory_links": ["PP", "SN", "DP", "DT", "NM", "IC", "MS", "EC", "CB", "MSI", "ART", "SRT", "Biophilia"],
      "quote": "supporting text"
    }
  ],
  "domains": ["A1_Materials", "A4_Light", etc],
  "overall_theory_links": ["frameworks that guide this paper"]
}

NOTE: Populate theory_links when frameworks clearly apply; leave empty array [] if no theory is evident.
"""

PROMPT_MAP = {
    "empirical": EMPIRICAL_PROMPT,
    "meta_analysis": META_ANALYSIS_PROMPT,
    "systematic_review": SYSTEMATIC_REVIEW_PROMPT,
    "narrative_review": NARRATIVE_REVIEW_PROMPT,
    "theoretical": THEORETICAL_PROMPT,
    "qualitative": QUALITATIVE_PROMPT,
    "methods": METHODS_PROMPT,
    "unknown": UNKNOWN_PROMPT,
}


def get_client() -> genai.Client:
    """Get configured Gemini client."""
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: Set GOOGLE_API_KEY or GEMINI_API_KEY")
        sys.exit(1)
    return genai.Client(api_key=api_key)


def load_queue() -> dict:
    """Load queue state from file."""
    if QUEUE_STATE_FILE.exists():
        with open(QUEUE_STATE_FILE) as f:
            return json.load(f)
    return {"items": [], "stats": {}, "last_updated": None}


def save_queue(state: dict):
    """Save queue state to file."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    state["last_updated"] = datetime.now(timezone.utc).isoformat()
    with open(QUEUE_STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def load_triage() -> dict:
    """Load triage results."""
    if not TRIAGE_FILE.exists():
        print(f"ERROR: Run triage_papers_keywords.py first")
        sys.exit(1)
    with open(TRIAGE_FILE) as f:
        return json.load(f)


def extract_paper(client: genai.Client, pdf_path: Path, article_type: str, model: str = "gemini-2.5-flash") -> dict:
    """Run extraction on a single paper."""
    start = time.time()

    if not pdf_path.exists():
        return {"success": False, "error": f"PDF not found: {pdf_path}"}

    prompt = PROMPT_MAP.get(article_type, UNKNOWN_PROMPT)

    try:
        # Upload PDF
        with open(pdf_path, "rb") as f:
            uploaded = client.files.upload(file=f, config={"mime_type": "application/pdf"})

        # Wait for processing
        while uploaded.state.name == "PROCESSING":
            time.sleep(1)
            uploaded = client.files.get(name=uploaded.name)

        if uploaded.state.name == "FAILED":
            return {"success": False, "error": "Upload failed"}

        # Generate
        response = client.models.generate_content(
            model=model,
            contents=[
                types.Part.from_uri(file_uri=uploaded.uri, mime_type="application/pdf"),
                prompt,
            ],
            config=types.GenerateContentConfig(
                temperature=0.1,
                max_output_tokens=65536,
            ),
        )

        elapsed = time.time() - start

        # Parse JSON
        text = response.text.strip()
        # Handle markdown code blocks
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])

        result = json.loads(text)

        # Add metadata
        usage = {}
        cost = 0.0
        if response.usage_metadata:
            m = response.usage_metadata
            pricing = PRICING.get(model, PRICING["gemini-2.5-flash"])
            cost = (m.prompt_token_count * pricing["input"] + m.candidates_token_count * pricing["output"]) / 1_000_000
            usage = {
                "input_tokens": m.prompt_token_count,
                "output_tokens": m.candidates_token_count,
                "cost_usd": round(cost, 6),
            }

        # Cleanup
        try:
            client.files.delete(name=uploaded.name)
        except Exception as e:
            import logging; logging.getLogger(__name__).debug(f"Non-critical: {e}")

        return {
            "success": True,
            "data": result,
            "usage": usage,
            "elapsed": round(elapsed, 1),
            "model": model,
        }

    except json.JSONDecodeError as e:
        return {"success": False, "error": f"JSON parse: {e}", "raw": text[:500] if "text" in dir() else None}
    except Exception as e:
        return {"success": False, "error": str(e)}


def compare_extractions(run1: dict, run2: dict) -> dict:
    """Compare two extraction runs for agreement."""
    if not run1.get("success") or not run2.get("success"):
        return {"agree": False, "reason": "one or both runs failed"}

    data1 = run1.get("data", {})
    data2 = run2.get("data", {})

    # Get findings from both
    findings1 = data1.get("findings", data1.get("pooled_effects", data1.get("themes", data1.get("propositions", data1.get("key_claims", [])))))
    findings2 = data2.get("findings", data2.get("pooled_effects", data2.get("themes", data2.get("propositions", data2.get("key_claims", [])))))

    if not findings1 and not findings2:
        return {"agree": True, "reason": "both empty", "n_findings": 0}

    # Check direction agreement for each finding
    disagreements = []
    for i, (f1, f2) in enumerate(zip(findings1, findings2)):
        d1 = f1.get("direction", "").lower()
        d2 = f2.get("direction", "").lower()
        if d1 and d2 and d1 != d2:
            disagreements.append({
                "index": i,
                "field": "direction",
                "run1": d1,
                "run2": d2,
            })

    agreement_rate = 1.0 - (len(disagreements) / max(len(findings1), len(findings2), 1))

    return {
        "agree": len(disagreements) == 0,
        "agreement_rate": round(agreement_rate, 2),
        "n_findings_run1": len(findings1),
        "n_findings_run2": len(findings2),
        "disagreements": disagreements,
    }


def merge_extractions(run1: dict, run2: dict, run3: dict | None = None) -> dict:
    """Merge extraction runs into final result."""
    # Prefer run1 data, but mark disagreements
    if run1.get("success"):
        merged = run1["data"].copy()
    elif run2.get("success"):
        merged = run2["data"].copy()
    else:
        return {"error": "all runs failed"}

    # Add verification metadata
    merged["_verification"] = {
        "n_runs": 3 if run3 else 2,
        "run1_success": run1.get("success", False),
        "run2_success": run2.get("success", False),
        "run3_success": run3.get("success", False) if run3 else None,
    }

    return merged


def resolve_outcomes_in_extraction(extraction_data: dict) -> int:
    """
    OC-3: Resolve outcome IDs in extraction data to canonical form.

    Iterates through claims and resolves any outcome IDs found in
    constructs.outcomes via the outcome resolver.

    Returns:
        Number of outcomes that were resolved to canonical form.
    """
    if not HAS_OUTCOME_RESOLVER:
        return 0

    resolved_count = 0
    claims = extraction_data.get("claims", [])
    for claim in claims:
        constructs = claim.get("constructs", {})
        outcomes = constructs.get("outcomes", [])
        for outcome in outcomes:
            raw_id = outcome.get("id")
            if raw_id:
                try:
                    resolved = resolve_outcome(str(raw_id))
                    if resolved:
                        canonical_id = resolved['canonical_id']
                        if canonical_id != raw_id:
                            outcome["id"] = canonical_id
                            outcome["resolution_method"] = "canonical_resolver"
                            print(f"  Resolved outcome: {raw_id} → {canonical_id}")
                            resolved_count += 1
                except Exception as e:
                    print(f"  Warning: Outcome resolution failed for {raw_id}: {e}")
    return resolved_count


def process_queue_item(client: genai.Client, item: QueueItem, verify: bool = True) -> QueueItem:
    """Process a single queue item with optional verification."""
    pdf_path = Path(item.pdf_path)

    print(f"  Run 1...")
    item.run1_result = extract_paper(client, pdf_path, item.article_type)
    item.total_cost += item.run1_result.get("usage", {}).get("cost_usd", 0)

    if not verify:
        item.final_result = item.run1_result.get("data") if item.run1_result.get("success") else None
        item.status = ExtractionStatus.COMPLETED if item.run1_result.get("success") else ExtractionStatus.FAILED
        item.updated_at = datetime.now(timezone.utc).isoformat()
        return item

    # Run 2 for verification
    print(f"  Run 2...")
    time.sleep(1)  # Brief pause
    item.run2_result = extract_paper(client, pdf_path, item.article_type)
    item.total_cost += item.run2_result.get("usage", {}).get("cost_usd", 0)

    # Compare
    comparison = compare_extractions(item.run1_result, item.run2_result)
    print(f"  Agreement: {comparison.get('agreement_rate', 0):.0%}")

    if comparison.get("agree"):
        item.final_result = merge_extractions(item.run1_result, item.run2_result)
        item.status = ExtractionStatus.COMPLETED
    else:
        # Run 3 tie-breaker
        print(f"  Run 3 (tie-breaker)...")
        time.sleep(1)
        item.run3_result = extract_paper(client, pdf_path, item.article_type, model="gemini-2.5-pro")
        item.total_cost += item.run3_result.get("usage", {}).get("cost_usd", 0)

        item.final_result = merge_extractions(item.run1_result, item.run2_result, item.run3_result)
        item.status = ExtractionStatus.COMPLETED

    if item.final_result is None or "error" in item.final_result:
        item.status = ExtractionStatus.FAILED
        item.error = item.final_result.get("error") if item.final_result else "No result"
    else:
        # OC-3: Resolve outcomes in final result
        try:
            resolved_outcomes = resolve_outcomes_in_extraction(item.final_result)
            if resolved_outcomes > 0:
                print(f"  OC-3: Resolved {resolved_outcomes} outcome IDs")
        except Exception as e:
            print(f"  Warning: OC-3 outcome resolution failed: {e}")

    item.updated_at = datetime.now(timezone.utc).isoformat()
    return item


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--type", choices=list(PROMPT_MAP.keys()), help="Process specific article type")
    parser.add_argument("--all", action="store_true", help="Process all types")
    parser.add_argument("--limit", type=int, default=10, help="Max papers to process")
    parser.add_argument("--no-verify", action="store_true", help="Skip 2-run verification")
    parser.add_argument("--status", action="store_true", help="Show queue status")
    parser.add_argument("--resume", action="store_true", help="Resume from saved state")
    parser.add_argument("--doi", help="Process single DOI")
    parser.add_argument("--model", default="gemini-2.5-flash",
                        help="Gemini model (gemini-2.5-flash, gemini-2.5-pro, gemini-3.1-pro)")
    args = parser.parse_args()

    if args.status:
        state = load_queue()
        print(f"Queue state: {len(state.get('items', []))} items")
        print(f"Last updated: {state.get('last_updated')}")
        stats = state.get("stats", {})
        for status, count in stats.items():
            print(f"  {status}: {count}")
        return

    # Load triage results
    triage = load_triage()
    extraction_queue = triage.get("extraction_queue", {})

    # Build work list
    work = []
    if args.doi:
        pdf_path = PDF_DIR / (args.doi.replace("/", "_") + ".pdf")
        article_type = "unknown"
        for t, dois in extraction_queue.items():
            if args.doi in dois:
                article_type = t
                break
        work.append({"doi": args.doi, "article_type": article_type, "pdf_path": str(pdf_path)})
    elif args.type:
        dois = extraction_queue.get(args.type, [])
        for doi in dois[:args.limit]:
            pdf_path = PDF_DIR / (doi.replace("/", "_") + ".pdf")
            work.append({"doi": doi, "article_type": args.type, "pdf_path": str(pdf_path)})
    elif args.all:
        for article_type, dois in extraction_queue.items():
            for doi in dois[:args.limit]:
                pdf_path = PDF_DIR / (doi.replace("/", "_") + ".pdf")
                work.append({"doi": doi, "article_type": article_type, "pdf_path": str(pdf_path)})

    if not work:
        print("No papers to process. Use --type, --all, or --doi")
        return

    print(f"Papers to process: {len(work)}")
    print(f"Verification: {'disabled' if args.no_verify else 'enabled (2-run)'}")

    # Initialize client
    client = get_client()

    # Process
    results = []
    total_cost = 0.0

    for i, paper in enumerate(work):
        print(f"\n[{i+1}/{len(work)}] {paper['doi'][:50]} ({paper['article_type']})")

        item = QueueItem(
            doi=paper["doi"],
            article_type=paper["article_type"],
            pdf_path=paper["pdf_path"],
        )

        item = process_queue_item(client, item, verify=not args.no_verify)
        results.append(item)
        total_cost += item.total_cost

        print(f"  Status: {item.status.value}")
        print(f"  Cost: ${item.total_cost:.4f}")

        # Save incrementally
        if (i + 1) % 5 == 0:
            OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            with open(OUTPUT_DIR / f"batch_{datetime.now().strftime('%Y%m%d_%H%M')}.json", "w") as f:
                json.dump([{
                    "doi": r.doi,
                    "article_type": r.article_type,
                    "status": r.status.value,
                    "final_result": r.final_result,
                    "total_cost": r.total_cost,
                } for r in results], f, indent=2)

    # Final summary
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"\n{'='*60}")
    print("EXTRACTION SUMMARY")
    print(f"{'='*60}")
    print(f"Total papers: {len(results)}")
    print(f"Completed: {sum(1 for r in results if r.status == ExtractionStatus.COMPLETED)}")
    print(f"Failed: {sum(1 for r in results if r.status == ExtractionStatus.FAILED)}")
    print(f"Total cost: ${total_cost:.4f}")

    # Save final results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = OUTPUT_DIR / f"extraction_{timestamp}.json"
    with open(output_file, "w") as f:
        json.dump({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_cost": round(total_cost, 4),
            "verification_enabled": not args.no_verify,
            "results": [{
                "doi": r.doi,
                "article_type": r.article_type,
                "status": r.status.value,
                "final_result": r.final_result,
                "run1_success": r.run1_result.get("success") if r.run1_result else None,
                "run2_success": r.run2_result.get("success") if r.run2_result else None,
                "run3_success": r.run3_result.get("success") if r.run3_result else None,
                "total_cost": r.total_cost,
                "error": r.error,
            } for r in results]
        }, f, indent=2)

    print(f"\nSaved to: {output_file}")

    # Run centrality scoring
    try:
        from centrality_weighting import CentralityAnalyzer

        print("\n" + "=" * 60)
        print("CENTRALITY SCORING")
        print("=" * 60)

        analyzer = CentralityAnalyzer()
        if analyzer.load_web():
            grade_counts = {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0}
            scored_results = []

            for r in results:
                if r.status == ExtractionStatus.COMPLETED and r.final_result:
                    adequacy = analyzer.score_article({
                        "doi": r.doi,
                        "article_type": r.article_type,
                        "final_result": r.final_result,
                    })
                    grade_counts[adequacy.adequacy_grade] += 1
                    scored_results.append({
                        "doi": r.doi,
                        "grade": adequacy.adequacy_grade,
                        "avg_score": round(adequacy.average_finding_score, 3),
                        "n_high": adequacy.n_high_centrality,
                        "n_findings": adequacy.n_findings,
                    })

            print(f"Grade distribution: {grade_counts}")
            print("Top articles:")
            for sr in sorted(scored_results, key=lambda x: -x["avg_score"])[:5]:
                print(f"  {sr['grade']}: {sr['doi'][:40]}... ({sr['n_findings']} findings, avg={sr['avg_score']})")

            # Save scored version
            scored_file = OUTPUT_DIR / f"scored_extraction_{timestamp}.json"
            with open(scored_file, "w") as f:
                json.dump({
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "grade_distribution": grade_counts,
                    "scored_results": scored_results,
                }, f, indent=2)
            print(f"\nScored results saved to: {scored_file}")
    except ImportError:
        print("\nCentrality scoring not available (import error)")
    except Exception as e:
        print(f"\nCentrality scoring failed: {e}")


if __name__ == "__main__":
    main()
