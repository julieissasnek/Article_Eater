#!/usr/bin/env python3
"""V3 Surgical Update for existing articles with findings.

For articles that already have findings (n_findings > 0), we don't need full re-extraction.
Instead, we surgically add v3-specific fields:
  - theory_commitments (explicit theory links)
  - mechanism_chain (causal mechanisms with mechanism types)
  - instruments_used (specific measurement instrument names)
  - stimulus_description (detailed stimulus specifications)

This enriches existing extractions without re-extracting findings.
"""

import json
import os
import sys
import time
import logging
from pathlib import Path
from datetime import datetime, timezone
# Load .env if present
env_file = Path(__file__).parent.parent / ".env"
if env_file.exists():
    for line in open(env_file):
        if "=" in line and not line.startswith("#"):
            k, v = line.strip().split("=", 1)
            os.environ[k] = v

REPO = Path(__file__).parent.parent
sys.path.insert(0, str(REPO))

from src.extraction.revised_prompts_v3 import get_prompt_for_family

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

def find_extractions_with_findings(skip_v3=True):
    """Find all extraction files with n_findings > 0.
    
    Args:
        skip_v3: If True, skip articles already at extraction_version v3.0
    """
    ext_dir = REPO / "data" / "extractions"
    extractions_with_findings = []
    skipped_v3 = 0

    for ext_file in ext_dir.glob("*.json"):
        try:
            data = json.loads(ext_file.read_text(errors='replace'))
            # Skip if data is a list (malformed files)
            if not isinstance(data, dict):
                continue
            if data.get("n_findings", 0) > 0:
                # Skip already-enriched articles unless --force
                if skip_v3 and data.get("extraction_version") == "v3.0":
                    skipped_v3 += 1
                    continue
                extractions_with_findings.append({
                    "file": ext_file.name,
                    "path": ext_file,
                    "n_findings": data.get("n_findings"),
                    "article_type": data.get("article_type", "unknown"),
                    "doi": data.get("doi", "")
                })
        except json.JSONDecodeError:
            pass

    if skipped_v3:
        logger.info(f"Skipped {skipped_v3} articles already at v3.0 (use --force to re-enrich)")
    return extractions_with_findings

def build_surgical_update_prompt(extraction_data):
    """Build a focused prompt to extract v3 fields from existing findings."""
    title = extraction_data.get("title", "Unknown")
    authors = extraction_data.get("authors", [])
    doi = extraction_data.get("doi", "")
    n_findings = extraction_data.get("n_findings", 0)
    article_type = extraction_data.get("article_type", "empirical")

    # Get sample of findings to provide context
    findings = extraction_data.get("findings", [])
    sample_antecedent = findings[0].get("antecedent", "") if findings else ""
    sample_consequent = findings[0].get("consequent", "") if findings else ""

    meta = extraction_data.get("paper_metadata", {})
    abstract = meta.get("abstract", "")

    prompt = f"""You are enhancing a scientific extraction with v3-specific structured fields.

PAPER CONTEXT:
Title: {title}
DOI: {doi}
Article Type: {article_type}
N Findings Already Extracted: {n_findings}

Sample Finding (to understand scope):
  Antecedent: {sample_antecedent}
  Consequent: {sample_consequent}

Abstract: {abstract[:500] if abstract else 'Not available'}

Based on your knowledge of this paper (if you have encountered it), provide the following enrichments:

Return ONLY valid JSON with these OPTIONAL fields (all can be null if not applicable):

{{
  "stimulus_description": {{
    "environmental_features": ["list specific environmental stimuli used"],
    "duration_exposure": "e.g., '15 minutes' or 'continuous 8-hour workday'",
    "control_conditions": ["what control/comparison conditions were used"],
    "ecological_validity": "lab|semi-naturalistic|field"
  }},

  "theory_commitments": [
    {{
      "theory_name": "Attention Restoration Theory",
      "commitment_type": "tests|extends|contradicts|assumes|proposes",
      "specific_claim": "Natural environments restore directed attention better than urban environments"
    }}
  ],

  "mechanism_chain": {{
    "description": "Causal mechanism connecting antecedent to consequent",
    "steps": [
      {{
        "step": 1,
        "from_construct": "ceiling height",
        "to_construct": "perceived spaciousness",
        "mechanism_type": "perceptual|cognitive|affective|behavioral|neural|physiological",
        "evidence_strength": "direct|indirect|theoretical|assumed"
      }},
      {{
        "step": 2,
        "from_construct": "perceived spaciousness",
        "to_construct": "cognitive performance",
        "mechanism_type": "cognitive",
        "evidence_strength": "theoretical"
      }}
    ]
  }},

  "instruments_used": [
    {{
      "name": "PANAS",
      "construct": "positive and negative affect",
      "description": "20-item mood scale",
      "type": "self_report|behavioral|physiological|fmri|eeg|eye_tracking|actigraphy|other"
    }},
    {{
      "name": "NASA-TLX",
      "construct": "cognitive workload",
      "description": "Mental effort rating scale",
      "type": "self_report"
    }}
  ]
}}

IMPORTANT RULES:
- Only include fields where you can extract from the paper
- DO NOT invent instruments or theories not mentioned
- For theory_commitments, be explicit about HOW the paper uses the theory
- For mechanism_chain, only include if the paper describes causal mechanisms
- All lists should be specific and complete
- Return null for fields with insufficient information

Return ONLY valid JSON. No explanations, no markdown code blocks.
"""
    return prompt

def call_gemini_surgical(prompt, model="gemini-2.5-flash"):
    """Call Gemini API for surgical update."""
    from google import genai

    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY or GEMINI_API_KEY not set")

    client = genai.Client(api_key=api_key)

    full_prompt = ("You are a scientific data enrichment expert. "
                   "Return ONLY valid JSON with v3 fields.\n\n" + prompt)

    response = client.models.generate_content(
        model=model,
        contents=full_prompt,
        config={
            "max_output_tokens": 4096,
            "temperature": 0.1,
        }
    )

    # Extract text, handling thinking model parts
    text = ""
    if response.text:
        text = response.text
    elif response.candidates:
        for part in response.candidates[0].content.parts:
            if part.text and not getattr(part, 'thought', False):
                text = part.text
                break

    # Build usage-like object for cost tracking
    usage = response.usage_metadata if response.usage_metadata else None
    return text, usage

def merge_v3_fields(original_extraction, v3_enrichment):
    """Merge v3 fields into original extraction."""
    import re
    # Strip markdown code fences first
    clean = re.sub(r'```(?:json)?\s*\n?', '', v3_enrichment)
    clean = clean.replace('```', '').strip()
    try:
        enrichment = json.loads(clean)
    except json.JSONDecodeError:
        # Find JSON object in text
        s = clean.find('{')
        e = clean.rfind('}')
        if s >= 0 and e > s:
            try:
                enrichment = json.loads(clean[s:e+1])
            except json.JSONDecodeError:
                logger.warning(f"  Could not parse v3 enrichment JSON")
                return original_extraction
        else:
            logger.warning(f"  No JSON object found in v3 enrichment")
            return original_extraction

    # Merge v3 fields
    result = {**original_extraction}

    if enrichment.get("stimulus_description"):
        result["stimulus_description"] = enrichment["stimulus_description"]

    if enrichment.get("theory_commitments"):
        result["theory_commitments"] = enrichment["theory_commitments"]

    if enrichment.get("mechanism_chain"):
        result["mechanism_chain"] = enrichment["mechanism_chain"]

    if enrichment.get("instruments_used"):
        result["instruments_used"] = enrichment["instruments_used"]

    # Mark as surgically updated
    result["extraction_version"] = "v3.0"
    result["quality_action"] = "v3_surgical_update"
    result["surgical_update_at"] = datetime.now(timezone.utc).isoformat()

    return result

def run_surgical_update(limit=None, dry_run=False, force=False):
    """Run surgical v3 update on articles with existing findings."""
    articles = find_extractions_with_findings(skip_v3=not force)
    if limit:
        articles = articles[:limit]

    logger.info(f"Starting surgical v3 update for {len(articles)} articles")

    results = {"success": 0, "failed": 0, "total_enriched_fields": 0, "costs": []}

    for i, article in enumerate(articles):
        filename = article["file"]
        doi = article["doi"]

        logger.info(f"[{i+1}/{len(articles)}] Enriching {filename} ({article['n_findings']} findings, DOI: {doi})")

        # Load extraction
        try:
            extraction_data = json.loads(article["path"].read_text(errors='replace'))
        except Exception:  
            logger.warning(f"  Could not load extraction file")
            results["failed"] += 1
            continue

        # Build surgical prompt
        prompt = build_surgical_update_prompt(extraction_data)

        if dry_run:
            logger.info(f"  [DRY RUN] Would enrich with {len(prompt)} char prompt")
            continue

        try:
            # Call Gemini
            response_text, usage = call_gemini_surgical(prompt)
            cost = 0.0
            if usage:
                # Gemini 2.5 Flash pricing
                cost = (getattr(usage, 'prompt_token_count', 0) * 0.15 / 1_000_000) + \
                       (getattr(usage, 'candidates_token_count', 0) * 0.60 / 1_000_000)
            results["costs"].append(cost)

            # Merge and save
            enriched = merge_v3_fields(extraction_data, response_text)

            # Count enriched fields
            n_enriched = sum([
                1 if enriched.get("stimulus_description") else 0,
                1 if enriched.get("theory_commitments") else 0,
                1 if enriched.get("mechanism_chain") else 0,
                1 if enriched.get("instruments_used") else 0
            ])

            article["path"].write_text(json.dumps(enriched, indent=2, ensure_ascii=False))
            results["success"] += 1
            results["total_enriched_fields"] += n_enriched
            logger.info(f"  ✓ Enriched with {n_enriched} v3 fields (${cost:.4f})")

            # Rate limiting
            time.sleep(0.5)

        except Exception as e:
            results["failed"] += 1
            logger.error(f"  ✗ Error: {e}")
            time.sleep(1)

    # Summary
    total_cost = sum(results["costs"])
    logger.info(f"\n=== V3 SURGICAL UPDATE COMPLETE ===")
    logger.info(f"Success: {results['success']}/{len(articles)}")
    logger.info(f"Failed: {results['failed']}")
    logger.info(f"Total v3 fields enriched: {results['total_enriched_fields']}")
    logger.info(f"Total cost: ${total_cost:.4f}")

    # Save results summary
    summary_path = REPO / "data" / "field_discovery" / "v3_surgical_update_results.json"
    summary_path.write_text(json.dumps({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "articles_processed": len(articles),
        **results,
        "total_cost": total_cost
    }, indent=2))

    return results

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="V3 Surgical Update for existing extractions")
    parser.add_argument("--limit", type=int, help="Limit number of articles")
    parser.add_argument("--dry-run", action="store_true", help="Don't call API, just show what would happen")
    parser.add_argument("--force", action="store_true", help="Re-enrich articles already at v3.0")
    args = parser.parse_args()

    run_surgical_update(limit=args.limit, dry_run=args.dry_run, force=args.force)
