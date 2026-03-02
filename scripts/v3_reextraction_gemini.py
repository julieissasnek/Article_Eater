#!/usr/bin/env python3
"""
V3 Re-extraction using Gemini 2.5 Flash — adapted from CW's OpenAI version.

Processes zero-finding articles using v3 prompts from revised_prompts_v3.py.
Uses Gemini API instead of OpenAI. Handles thinking-model output (code fences, etc).

Usage:
    PYTHONPATH=. /tmp/genai_venv/bin/python3 scripts/v3_reextraction_gemini.py
    PYTHONPATH=. /tmp/genai_venv/bin/python3 scripts/v3_reextraction_gemini.py --limit 5 --dry-run

Success Conditions:
    SC-H12-1: ≥50% of zero-finding articles re-extracted with findings
    SC-H12-2: <20% API errors
    SC-H12-3: Average ≥3 findings per successful extraction
    SC-H12-4: All output files are valid JSON
"""

import json
import os
import sys
import re
import time
import logging
from pathlib import Path
from datetime import datetime, timezone

REPO = Path(__file__).parent.parent
sys.path.insert(0, str(REPO))

# Load API key
for env_file in [REPO / ".env", Path("/tmp/.env_atlas")]:
    if env_file.exists():
        for line in open(env_file):
            if "=" in line and not line.startswith("#"):
                k, v = line.strip().split("=", 1)
                os.environ[k] = v

from src.extraction.revised_prompts_v3 import get_prompt_for_family

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[
        logging.FileHandler("/tmp/v3_reextract_gemini.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def load_tier1_articles():
    """Load zero-finding articles from tier1_reextract.json or scan extractions."""
    tier1_path = REPO / "data" / "field_discovery" / "tier1_reextract.json"
    if tier1_path.exists():
        return json.loads(tier1_path.read_text())
    
    # Fallback: scan for zero-finding extractions
    articles = []
    ext_dir = REPO / "data" / "extractions"
    for ef in sorted(ext_dir.glob("10.*.json")):
        try:
            data = json.load(open(ef))
            if not data.get("findings"):
                articles.append({"file": ef.name, "doi": data.get("doi", ef.stem)})
        except Exception as e:
            logger.debug(f"Non-critical: {e}")
    return articles


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

Abstract/Summary: {abstract if abstract else 'Not available'}
"""

    prompt = f"""You are an expert at extracting structured scientific findings from environmental psychology research papers.

Given the following paper metadata, extract all findings you can identify. Use your knowledge of the paper if you have encountered it in your training data.

{context}

{family_prompt}

IMPORTANT: Even if you have limited information, extract what you can. For papers you recognize, use your knowledge of the paper's findings. For papers you don't recognize, extract what can be inferred from the title and abstract.

Return ONLY valid JSON (no markdown code blocks). The JSON should match the extraction schema with a "findings" array. If you truly cannot extract any findings, return the metadata with an empty findings array and explain in minimum_safe_summary why.
"""
    return prompt


def call_gemini(prompt, model="gemini-2.5-flash"):
    """Call Gemini API with proper handling for thinking model output."""
    from google import genai
    
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY or GEMINI_API_KEY not set")
    
    client = genai.Client(api_key=api_key)
    
    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config={
            "max_output_tokens": 8192,
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
    
    return text


def parse_json_from_text(text):
    """Robust JSON extraction from model output."""
    if not text:
        return None
    # Strip markdown code fences
    clean = re.sub(r'```(?:json)?\s*\n?', '', text)
    clean = clean.replace('```', '').strip()
    # Try direct parse
    try:
        return json.loads(clean)
    except json.JSONDecodeError:
        pass
    # Find JSON object
    s = clean.find('{')
    e = clean.rfind('}')
    if s >= 0 and e > s:
        try:
            return json.loads(clean[s:e+1])
        except json.JSONDecodeError:
            pass
    return None


def parse_extraction_response(response_text, original_data):
    """Parse LLM response and merge with original metadata."""
    extracted = parse_json_from_text(response_text)
    if not extracted:
        return None
    
    result = {**original_data}
    result["findings"] = extracted.get("findings", [])
    result["n_findings"] = len(result["findings"])
    result["domains"] = extracted.get("domains", original_data.get("domains", []))
    result["overall_theory_links"] = extracted.get("overall_theory_links", [])
    result["limitations"] = extracted.get("limitations", [])
    result["minimum_safe_summary"] = extracted.get("minimum_safe_summary", "")
    result["extracted_at"] = datetime.now(timezone.utc).isoformat()
    result["model"] = "gemini-2.5-flash"
    result["extraction_version"] = "v3.0_gemini"
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
    
    logger.info(f"=== V3 RE-EXTRACTION (GEMINI) ===")
    logger.info(f"Starting v3 re-extraction for {len(articles)} Tier 1 articles")
    
    results = {"success": 0, "failed": 0, "skipped": 0, "parse_errors": 0,
               "total_findings": 0, "errors": []}
    
    for i, article in enumerate(articles):
        filename = article["file"]
        doi = article.get("doi", "unknown")
        
        logger.info(f"[{i+1}/{len(articles)}] Processing {filename} (DOI: {doi})")
        
        existing = load_existing_extraction(filename)
        if not existing:
            logger.warning(f"  No existing extraction file: {filename}")
            results["skipped"] += 1
            continue
        
        # Skip if already has findings (from previous re-extraction)
        if existing.get("findings") and existing.get("quality_action") == "v3_reextracted":
            logger.info(f"  Already re-extracted, skipping")
            results["skipped"] += 1
            continue
        
        # Get article family and prompt
        article_type = existing.get("article_type", existing.get("detected_article_type", "empirical"))
        try:
            family_prompt = get_prompt_for_family(article_type)
        except (KeyError, ValueError):
            family_prompt = get_prompt_for_family("empirical")
        
        prompt = build_reextraction_prompt(existing, family_prompt)
        
        if dry_run:
            logger.info(f"  [DRY RUN] Would extract with {len(prompt)} char prompt")
            continue
        
        try:
            response_text = call_gemini(prompt)
            
            result = parse_extraction_response(response_text, existing)
            if result and result["n_findings"] > 0:
                output_path = REPO / "data" / "extractions" / filename
                output_path.write_text(json.dumps(result, indent=2, ensure_ascii=False))
                results["success"] += 1
                results["total_findings"] += result["n_findings"]
                logger.info(f"  ✓ Extracted {result['n_findings']} findings")
            elif result:
                output_path = REPO / "data" / "extractions" / filename
                output_path.write_text(json.dumps(result, indent=2, ensure_ascii=False))
                results["failed"] += 1
                logger.info(f"  ✗ No findings extracted")
            else:
                results["parse_errors"] += 1
                logger.warning(f"  ✗ Failed to parse response")
            
            time.sleep(2)  # Rate limit
            
        except Exception as e:
            results["errors"].append(str(e))
            logger.error(f"  ✗ Error: {e}")
            time.sleep(3)
    
    # Summary
    total = len(articles) - results["skipped"]
    success_pct = 100 * results["success"] / total if total else 0
    error_pct = 100 * (len(results["errors"]) + results["parse_errors"]) / total if total else 0
    avg_findings = results["total_findings"] / results["success"] if results["success"] else 0
    
    logger.info(f"\n{'='*60}")
    logger.info(f"  V3 RE-EXTRACTION COMPLETE (GEMINI)")
    logger.info(f"{'='*60}")
    logger.info(f"  Total articles:    {len(articles)}")
    logger.info(f"  Processed:         {total}")
    logger.info(f"  Success:           {results['success']} ({success_pct:.0f}%)")
    logger.info(f"  Failed:            {results['failed']}")
    logger.info(f"  Parse errors:      {results['parse_errors']}")
    logger.info(f"  API errors:        {len(results['errors'])}")
    logger.info(f"  Total findings:    {results['total_findings']}")
    logger.info(f"  Avg findings/paper:{avg_findings:.1f}")
    logger.info(f"{'='*60}")
    
    # Success conditions
    sc1 = success_pct >= 50
    sc2 = error_pct < 20
    sc3 = avg_findings >= 3
    logger.info(f"\nSuccess conditions:")
    logger.info(f"  SC-H12-1 (≥50% success):    {'PASS' if sc1 else 'FAIL'} ({success_pct:.0f}%)")
    logger.info(f"  SC-H12-2 (<20% errors):      {'PASS' if sc2 else 'FAIL'} ({error_pct:.0f}%)")
    logger.info(f"  SC-H12-3 (≥3 avg findings):  {'PASS' if sc3 else 'FAIL'} ({avg_findings:.1f})")
    
    # Save results
    summary = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "model": "gemini-2.5-flash",
        "articles_total": len(articles),
        "processed": total,
        **{k: v for k, v in results.items() if k != "errors"},
        "error_count": len(results["errors"]),
        "success_pct": success_pct,
        "avg_findings": avg_findings,
        "success_conditions": {"sc1": sc1, "sc2": sc2, "sc3": sc3},
    }
    summary_path = REPO / "data" / "field_discovery" / "v3_reextraction_gemini_results.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2))
    
    return results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="V3 Re-extraction using Gemini")
    parser.add_argument("--limit", type=int, help="Limit number of articles")
    parser.add_argument("--dry-run", action="store_true", help="Don't call API")
    args = parser.parse_args()
    run_reextraction(limit=args.limit, dry_run=args.dry_run)
