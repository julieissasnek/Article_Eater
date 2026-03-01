#!/usr/bin/env python3
"""V3 Re-extraction using OpenAI GPT-4o for Tier 1 articles (zero findings)."""

import json
import os
import sys
import time
import logging
from pathlib import Path
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

REPO = Path(__file__).parent.parent
sys.path.insert(0, str(REPO))

from src.extraction.revised_prompts_v3 import get_prompt_for_family, PROMPT_MAP, FAMILY_MAP

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

def load_tier1_articles():
    """Load the 59 zero-finding articles."""
    tier1_path = REPO / "data" / "field_discovery" / "tier1_reextract.json"
    return json.loads(tier1_path.read_text())

def load_existing_extraction(filename):
    """Load the existing extraction file to get metadata."""
    ext_path = REPO / "data" / "extractions" / filename
    if ext_path.exists():
        return json.loads(ext_path.read_text(errors='replace'))
    return None

def build_reextraction_prompt(extraction_data, family_prompt):
    """Build a prompt using existing metadata + v3 prompt template."""
    title = extraction_data.get("title", "Unknown")
    authors = extraction_data.get("authors", [])
    doi = extraction_data.get("doi", "")
    article_type = extraction_data.get("article_type", "empirical")
    article_family = extraction_data.get("article_family", extraction_data.get("detected_family", "empirical"))

    # Get paper metadata if available
    meta = extraction_data.get("paper_metadata", {})
    abstract = meta.get("abstract", "")
    journal = meta.get("journal", extraction_data.get("journal", ""))
    year = meta.get("year", extraction_data.get("year", ""))

    context = f"""
Title: {title}
Authors: {', '.join(authors) if isinstance(authors, list) else authors}
DOI: {doi}
Journal: {journal}
Year: {year}
Article Type: {article_type}
Article Family: {article_family}

Abstract/Summary: {abstract if abstract else 'Not available'}
"""

    prompt = f"""You are an expert at extracting structured scientific findings from environmental psychology research papers.

Given the following paper metadata, extract all findings you can identify. Use your knowledge of the paper if you have encountered it in your training data.

{context}

{family_prompt}

IMPORTANT: Even if you have limited information, extract what you can. For papers you recognize, use your knowledge of the paper's findings. For papers you don't recognize, extract what can be inferred from the title and abstract.

Return valid JSON matching the extraction schema. If you truly cannot extract any findings, return the metadata with an empty findings array and explain in minimum_safe_summary why no findings could be extracted.
"""
    return prompt

def call_openai(prompt, model="gpt-4o"):
    """Call OpenAI API."""
    from openai import OpenAI

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not set")

    client = OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a scientific data extraction expert. Return ONLY valid JSON. No markdown code blocks."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1,
        max_tokens=4000,
        response_format={"type": "json_object"}
    )

    return response.choices[0].message.content, response.usage

def parse_extraction_response(response_text, original_data):
    """Parse LLM response and merge with original metadata."""
    try:
        extracted = json.loads(response_text)
    except json.JSONDecodeError:
        # Try to extract JSON from response
        import re
        match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if match:
            extracted = json.loads(match.group())
        else:
            return None

    # Merge with original metadata
    result = {**original_data}
    result["findings"] = extracted.get("findings", [])
    result["n_findings"] = len(result["findings"])
    result["domains"] = extracted.get("domains", original_data.get("domains", []))
    result["overall_theory_links"] = extracted.get("overall_theory_links", [])
    result["limitations"] = extracted.get("limitations", [])
    result["minimum_safe_summary"] = extracted.get("minimum_safe_summary", "")
    result["extracted_at"] = datetime.now(timezone.utc).isoformat()
    result["model"] = "gpt-4o"
    result["extraction_version"] = "v3.0"
    result["quality_action"] = "v3_reextracted"

    # Add v3 fields if present
    for field in ["stimulus_description", "stimulus_images", "theory_commitments",
                   "mechanism_chain", "molecule_ids", "instruments_used"]:
        if field in extracted:
            result[field] = extracted[field]

    return result

def run_reextraction(limit=None, dry_run=False):
    """Run v3 re-extraction on Tier 1 articles."""
    articles = load_tier1_articles()
    if limit:
        articles = articles[:limit]

    logger.info(f"Starting v3 re-extraction for {len(articles)} Tier 1 articles")

    results = {"success": 0, "failed": 0, "skipped": 0, "total_findings": 0, "costs": []}

    for i, article in enumerate(articles):
        filename = article["file"]
        doi = article.get("doi", "unknown")

        logger.info(f"[{i+1}/{len(articles)}] Processing {filename} (DOI: {doi})")

        # Load existing extraction
        existing = load_existing_extraction(filename)
        if not existing:
            logger.warning(f"  No existing extraction file found: {filename}")
            results["skipped"] += 1
            continue

        # Determine article family and get prompt
        family = existing.get("article_family", existing.get("detected_family", "empirical"))
        article_type = existing.get("article_type", existing.get("detected_article_type", "empirical"))

        try:
            family_prompt = get_prompt_for_family(article_type)
        except (KeyError, ValueError):
            family_prompt = get_prompt_for_family("empirical")

        # Build prompt
        prompt = build_reextraction_prompt(existing, family_prompt)

        if dry_run:
            logger.info(f"  [DRY RUN] Would extract with {len(prompt)} char prompt")
            continue

        try:
            # Call OpenAI
            response_text, usage = call_openai(prompt)
            cost = (usage.prompt_tokens * 2.5 / 1_000_000) + (usage.completion_tokens * 10 / 1_000_000)
            results["costs"].append(cost)

            # Parse response
            result = parse_extraction_response(response_text, existing)
            if result and result["n_findings"] > 0:
                # Save updated extraction
                output_path = REPO / "data" / "extractions" / filename
                output_path.write_text(json.dumps(result, indent=2, ensure_ascii=False))
                results["success"] += 1
                results["total_findings"] += result["n_findings"]
                logger.info(f"  ✓ Extracted {result['n_findings']} findings (${cost:.4f})")
            elif result:
                # Still no findings
                output_path = REPO / "data" / "extractions" / filename
                output_path.write_text(json.dumps(result, indent=2, ensure_ascii=False))
                results["failed"] += 1
                logger.info(f"  ✗ No findings extracted (${cost:.4f})")
            else:
                results["failed"] += 1
                logger.warning(f"  ✗ Failed to parse response")

            # Rate limiting
            time.sleep(0.5)

        except Exception as e:
            results["failed"] += 1
            logger.error(f"  ✗ Error: {e}")
            time.sleep(1)

    # Summary
    total_cost = sum(results["costs"])
    logger.info(f"\n=== V3 RE-EXTRACTION COMPLETE ===")
    logger.info(f"Success: {results['success']}/{len(articles)}")
    logger.info(f"Failed: {results['failed']}")
    logger.info(f"Skipped: {results['skipped']}")
    logger.info(f"Total findings: {results['total_findings']}")
    logger.info(f"Total cost: ${total_cost:.4f}")

    # Save results summary
    summary_path = REPO / "data" / "field_discovery" / "v3_reextraction_results.json"
    summary_path.write_text(json.dumps({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "articles_processed": len(articles),
        **results,
        "total_cost": total_cost
    }, indent=2))

    return results

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="V3 Re-extraction using OpenAI GPT-4o")
    parser.add_argument("--limit", type=int, help="Limit number of articles")
    parser.add_argument("--dry-run", action="store_true", help="Don't call API, just show what would happen")
    args = parser.parse_args()

    run_reextraction(limit=args.limit, dry_run=args.dry_run)
