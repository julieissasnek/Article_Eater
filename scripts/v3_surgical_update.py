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
import asyncio
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional
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

    # Check for data gaps — which fields are missing?
    missing_sample_sizes = sum(1 for f in findings if not f.get("sample_size"))
    missing_effect_sizes = sum(1 for f in findings if not f.get("effect_size"))

    meta = extraction_data.get("paper_metadata", {})
    abstract = meta.get("abstract", "")

    prompt = f"""You are enhancing a scientific extraction with v3-specific structured fields.

PAPER CONTEXT:
Title: {title}
DOI: {doi}
Article Type: {article_type}
N Findings Already Extracted: {n_findings}
Findings missing sample_size: {missing_sample_sizes}/{n_findings}
Findings missing effect_size: {missing_effect_sizes}/{n_findings}

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

  "stimulus_images": [
    {{
      "description": "brief description of what the image shows",
      "figure_ref": "Figure 1a, Table 2, etc.",
      "image_type": "photo|rendering|diagram|floor_plan|graph|stimulus_set"
    }}
  ],

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
    }}
  ],

  "quantitative_backfill": {{
    "paper_sample_size": null,
    "paper_sample_size_source": "reported|estimated|inferred",
    "per_finding_updates": [
      {{
        "finding_index": 0,
        "sample_size": 120,
        "sample_size_source": "reported|estimated|inferred",
        "effect_size": 0.45,
        "effect_size_type": "Cohen's d|eta_squared|partial_eta_squared|r|OR|beta|R_squared|null",
        "p_value": 0.003,
        "confidence_interval": [0.12, 0.78]
      }}
    ]
  }}
}}

IMPORTANT RULES:
- Only include fields where you can extract from the paper
- DO NOT invent instruments or theories not mentioned
- For theory_commitments, be explicit about HOW the paper uses the theory
- For mechanism_chain, only include if the paper describes causal mechanisms
- For quantitative_backfill: PRIORITIZE extracting sample_size and effect_size
  - If you know the paper's total N, set paper_sample_size
  - For each finding missing sample_size or effect_size, provide values if you can
  - Use finding_index (0-based) to map to existing findings
  - Mark source as "reported" if you recall the exact value, "estimated" if approximated
- For stimulus_images: describe any figures showing the experimental stimuli
- All lists should be specific and complete
- Return null for fields with insufficient information

Return ONLY valid JSON. No explanations, no markdown code blocks.
"""
    return prompt

def call_gemini_surgical(prompt, model="gemini-2.5-flash"):
    """Call Gemini API for surgical update (sync version)."""
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


async def call_gemini_surgical_async(prompt, client, model="gemini-2.5-flash", max_retries=3):
    """Call Gemini API for surgical update (async version with retry)."""
    full_prompt = ("You are a scientific data enrichment expert. "
                   "Return ONLY valid JSON with v3 fields.\n\n" + prompt)

    last_error = None
    for attempt in range(max_retries):
        try:
            response = await client.aio.models.generate_content(
                model=model,
                contents=full_prompt,
                config={
                    "max_output_tokens": 4096,
                    "temperature": 0.1,
                }
            )

            # Extract text with robust null handling
            text = ""
            try:
                if response and response.text:
                    text = response.text
                elif response and response.candidates:
                    candidates = response.candidates
                    if candidates and len(candidates) > 0:
                        candidate = candidates[0]
                        if candidate and hasattr(candidate, 'content') and candidate.content:
                            parts = getattr(candidate.content, 'parts', None)
                            if parts:
                                for part in parts:
                                    if part and hasattr(part, 'text') and part.text:
                                        if not getattr(part, 'thought', False):
                                            text = part.text
                                            break
            except (TypeError, AttributeError) as extract_err:
                # Text extraction failed - treat as empty response
                logger.debug(f"  Text extraction error: {extract_err}")
                text = ""

            # If we got empty response, retry
            if not text and attempt < max_retries - 1:
                wait_time = (2 ** attempt) * 0.5  # 0.5s, 1s, 2s
                logger.warning(f"  Empty response, retrying in {wait_time}s (attempt {attempt + 1}/{max_retries})")
                await asyncio.sleep(wait_time)
                continue

            usage = response.usage_metadata if response and response.usage_metadata else None
            return text, usage

        except Exception as e:
            last_error = e
            if attempt < max_retries - 1:
                wait_time = (2 ** attempt) * 0.5
                logger.warning(f"  API error: {e}, retrying in {wait_time}s (attempt {attempt + 1}/{max_retries})")
                await asyncio.sleep(wait_time)
            else:
                raise

    # Should not reach here, but just in case
    if last_error:
        raise last_error
    return "", None

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

    if enrichment.get("stimulus_images"):
        result["stimulus_images"] = enrichment["stimulus_images"]

    # ── Quantitative backfill (Wave 7) ──────────────────────────────
    qb = enrichment.get("quantitative_backfill")
    if qb:
        # Paper-level sample size
        if qb.get("paper_sample_size"):
            result["paper_sample_size"] = qb["paper_sample_size"]
            result["paper_sample_size_source"] = qb.get("paper_sample_size_source", "estimated")

        # Per-finding updates
        findings = result.get("findings", [])
        n_backfilled = 0
        for update in qb.get("per_finding_updates", []):
            idx = update.get("finding_index")
            if idx is not None and 0 <= idx < len(findings):
                f = findings[idx]
                # Only backfill missing fields — don't overwrite existing
                if not f.get("sample_size") and update.get("sample_size"):
                    f["sample_size"] = update["sample_size"]
                    f["sample_size_source"] = update.get("sample_size_source", "estimated")
                    n_backfilled += 1
                if not f.get("effect_size") and update.get("effect_size"):
                    f["effect_size"] = update["effect_size"]
                    f["effect_size_type"] = update.get("effect_size_type")
                if not f.get("p_value") and update.get("p_value"):
                    f["p_value"] = update["p_value"]
                if not f.get("confidence_interval") and update.get("confidence_interval"):
                    f["confidence_interval"] = update["confidence_interval"]

        if n_backfilled:
            result["quantitative_backfill_count"] = n_backfilled
            logger.info(f"  📊 Backfilled {n_backfilled} findings with sample_size/effect_size")

    # Mark as surgically updated
    result["extraction_version"] = "v3.0"
    result["quality_action"] = "v3_surgical_update"
    result["surgical_update_at"] = datetime.now(timezone.utc).isoformat()

    return result

async def process_article_async(article, client, semaphore, results, idx, total, dry_run=False):
    """Process a single article asynchronously."""
    async with semaphore:
        filename = article["file"]
        doi = article["doi"]

        logger.info(f"[{idx+1}/{total}] Enriching {filename} ({article['n_findings']} findings, DOI: {doi})")

        # Load extraction
        try:
            extraction_data = json.loads(article["path"].read_text(errors='replace'))
        except Exception:
            logger.warning(f"  Could not load extraction file: {filename}")
            results["failed"] += 1
            return

        # Build surgical prompt
        prompt = build_surgical_update_prompt(extraction_data)

        if dry_run:
            logger.info(f"  [DRY RUN] Would enrich with {len(prompt)} char prompt")
            return

        try:
            # Call Gemini async
            response_text, usage = await call_gemini_surgical_async(prompt, client)
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
            logger.info(f"  ✓ [{idx+1}] Enriched with {n_enriched} v3 fields (${cost:.4f})")

        except Exception as e:
            results["failed"] += 1
            logger.error(f"  ✗ [{idx+1}] Error: {e}")
            await asyncio.sleep(0.5)  # Brief pause on error


async def run_surgical_update_async(limit=None, dry_run=False, force=False, concurrency=15):
    """Run surgical v3 update on articles with existing findings (parallel version)."""
    from google import genai

    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY or GEMINI_API_KEY not set")

    client = genai.Client(api_key=api_key)

    articles = find_extractions_with_findings(skip_v3=not force)
    if limit:
        articles = articles[:limit]

    logger.info(f"Starting PARALLEL surgical v3 update for {len(articles)} articles (concurrency={concurrency})")

    # Thread-safe results using simple dict (asyncio is single-threaded)
    results = {"success": 0, "failed": 0, "total_enriched_fields": 0, "costs": []}

    # Semaphore to limit concurrency
    semaphore = asyncio.Semaphore(concurrency)

    # Create tasks for all articles
    tasks = [
        process_article_async(article, client, semaphore, results, idx, len(articles), dry_run)
        for idx, article in enumerate(articles)
    ]

    # Run all tasks with progress tracking
    start_time = time.time()
    await asyncio.gather(*tasks, return_exceptions=True)
    elapsed = time.time() - start_time

    # Summary
    total_cost = sum(results["costs"])
    articles_per_sec = len(articles) / elapsed if elapsed > 0 else 0
    logger.info(f"\n=== V3 SURGICAL UPDATE COMPLETE (PARALLEL) ===")
    logger.info(f"Success: {results['success']}/{len(articles)}")
    logger.info(f"Failed: {results['failed']}")
    logger.info(f"Total v3 fields enriched: {results['total_enriched_fields']}")
    logger.info(f"Total cost: ${total_cost:.4f}")
    logger.info(f"Elapsed time: {elapsed:.1f}s ({articles_per_sec:.2f} articles/sec)")

    # Save results summary
    summary_path = REPO / "data" / "field_discovery" / "v3_surgical_update_results.json"
    summary_path.write_text(json.dumps({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "articles_processed": len(articles),
        "concurrency": concurrency,
        "elapsed_seconds": elapsed,
        **results,
        "total_cost": total_cost
    }, indent=2))

    return results


def run_surgical_update(limit=None, dry_run=False, force=False, parallel=False, concurrency=15):
    """Run surgical v3 update on articles with existing findings."""
    if parallel:
        return asyncio.run(run_surgical_update_async(limit, dry_run, force, concurrency))

    # Original sequential version
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
    parser.add_argument("--parallel", action="store_true", help="Run with async parallelization (faster)")
    parser.add_argument("--concurrency", type=int, default=15, help="Max concurrent API calls (default: 15)")
    args = parser.parse_args()

    run_surgical_update(
        limit=args.limit,
        dry_run=args.dry_run,
        force=args.force,
        parallel=args.parallel,
        concurrency=args.concurrency
    )
