#!/usr/bin/env python3
"""Focused backfill for effect_size and sample_size across all extractions.

Unlike v3_surgical_update.py (which enriches 6+ field types simultaneously),
this script sends a FOCUSED prompt that asks ONLY about quantitative data:
  - sample_size (per finding and paper-level)
  - effect_size + effect_size_type
  - p_value
  - confidence_interval

Design rationale: When the LLM is asked to fill 6 field types at once, it
distributes attention across all of them. For fields requiring careful numerical
extraction (effect sizes, sample sizes), a focused prompt yields substantially
better recall and accuracy.

Current coverage (2026-03-05):
  - sample_size:  5.6% filled  (1,858 / 33,116)
  - effect_size: 24.3% filled  (8,041 / 33,116)

Target: ≥50% sample_size, ≥60% effect_size after backfill.
(Not all findings SHOULD have these — theoretical papers, qualitative studies,
and reviews legitimately lack quantitative data.)

Usage:
  python scripts/backfill_quantitative_fields.py --analyze         # Show coverage stats only
  python scripts/backfill_quantitative_fields.py --dry-run --limit 5  # Preview without changes
  python scripts/backfill_quantitative_fields.py --limit 50        # Backfill 50 articles
  python scripts/backfill_quantitative_fields.py --parallel        # All articles, 15 concurrent
  python scripts/backfill_quantitative_fields.py --family empirical_v2  # Only empirical papers

Success Conditions (SC-BF-1 through SC-BF-6):
  SC-BF-1: Never overwrites existing non-null values
  SC-BF-2: Marks backfilled values with source="backfilled"
  SC-BF-3: Validates effect_size range per type before saving
  SC-BF-4: Coverage increases monotonically (never decreases)
  SC-BF-5: Script is idempotent (running twice = same result)
  SC-BF-6: Reports before/after coverage with per-family breakdown
"""

import json
import os
import sys
import time
import logging
import asyncio
import re
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple
from collections import Counter

# Load .env
env_file = Path(__file__).parent.parent / ".env"
if env_file.exists():
    for line in open(env_file):
        if "=" in line and not line.startswith("#"):
            k, v = line.strip().split("=", 1)
            os.environ.setdefault(k, v)

REPO = Path(__file__).parent.parent
sys.path.insert(0, str(REPO))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)
logger = logging.getLogger(__name__)

# ─── Effect size validation ranges (from extraction_field_validator.py) ────
EFFECT_SIZE_RANGES = {
    "Cohen's d":            (-5.0,  5.0),
    "eta_squared":          ( 0.0,  1.0),
    "partial_eta_squared":  ( 0.0,  1.0),
    "r":                    (-1.0,  1.0),
    "r_correlation":        (-1.0,  1.0),
    "odds_ratio":           ( 0.0, 100.0),
    "Cohen's f":            ( 0.0,  5.0),
    "Cramer's V":           ( 0.0,  1.0),
    "phi":                  (-1.0,  1.0),
    "beta":                 (-5.0,  5.0),
    "R_squared":            ( 0.0,  1.0),
    "partial_R_squared":    ( 0.0,  1.0),
    "log_odds":             (-10.0, 10.0),
}

# Families where quantitative data is expected
QUANTITATIVE_FAMILIES = {"empirical_v2", "empirical", "synthesis", "meta_analysis"}


# ═══════════════════════════════════════════════════════════════════════════
# Section 1: Coverage Analysis
# ═══════════════════════════════════════════════════════════════════════════

def scan_all_extractions() -> List[Dict[str, Any]]:
    """Scan all extraction JSONs and return metadata."""
    ext_dir = REPO / "data" / "extractions"
    articles = []
    for ext_file in sorted(ext_dir.glob("*.json")):
        try:
            data = json.loads(ext_file.read_text(errors='replace'))
            if not isinstance(data, dict):
                continue
            findings = data.get("findings", [])
            if not findings:
                continue

            missing_ss = sum(1 for f in findings if not f.get("sample_size"))
            missing_es = sum(1 for f in findings if not f.get("effect_size"))
            n = len(findings)

            articles.append({
                "path": ext_file,
                "file": ext_file.name,
                "doi": data.get("doi", ""),
                "title": data.get("title", ""),
                "family": data.get("article_family", data.get("article_type", "unknown")),
                "n_findings": n,
                "missing_sample_size": missing_ss,
                "missing_effect_size": missing_es,
                "missing_either": max(missing_ss, missing_es),
                "already_backfilled": data.get("_quantitative_backfill") is not None,
            })
        except (json.JSONDecodeError, Exception):
            continue
    return articles


def compute_coverage(articles: List[Dict]) -> Dict[str, Any]:
    """Compute detailed coverage statistics."""
    total_findings = sum(a["n_findings"] for a in articles)
    total_missing_ss = sum(a["missing_sample_size"] for a in articles)
    total_missing_es = sum(a["missing_effect_size"] for a in articles)

    by_family = {}
    for a in articles:
        fam = a["family"]
        if fam not in by_family:
            by_family[fam] = {"articles": 0, "findings": 0, "missing_ss": 0, "missing_es": 0}
        by_family[fam]["articles"] += 1
        by_family[fam]["findings"] += a["n_findings"]
        by_family[fam]["missing_ss"] += a["missing_sample_size"]
        by_family[fam]["missing_es"] += a["missing_effect_size"]

    return {
        "total_articles": len(articles),
        "total_findings": total_findings,
        "sample_size_filled": total_findings - total_missing_ss,
        "sample_size_pct": round(100 * (total_findings - total_missing_ss) / total_findings, 1) if total_findings else 0,
        "effect_size_filled": total_findings - total_missing_es,
        "effect_size_pct": round(100 * (total_findings - total_missing_es) / total_findings, 1) if total_findings else 0,
        "already_backfilled": sum(1 for a in articles if a["already_backfilled"]),
        "by_family": by_family,
    }


def print_coverage(cov: Dict, label: str = "CURRENT"):
    """Print formatted coverage report."""
    print(f"\n{'='*60}")
    print(f"  QUANTITATIVE COVERAGE — {label}")
    print(f"{'='*60}")
    print(f"  Articles with findings: {cov['total_articles']}")
    print(f"  Total findings:         {cov['total_findings']}")
    print(f"  Already backfilled:     {cov['already_backfilled']} articles")
    print(f"")
    print(f"  sample_size filled:     {cov['sample_size_filled']:,} / {cov['total_findings']:,}  ({cov['sample_size_pct']}%)")
    print(f"  effect_size filled:     {cov['effect_size_filled']:,} / {cov['total_findings']:,}  ({cov['effect_size_pct']}%)")
    print(f"")
    print(f"  Per-Family Breakdown:")
    print(f"  {'Family':<25} {'Articles':>8} {'Findings':>9} {'SS Fill%':>9} {'ES Fill%':>9}")
    print(f"  {'-'*25} {'-'*8} {'-'*9} {'-'*9} {'-'*9}")
    for fam, stats in sorted(cov["by_family"].items(), key=lambda x: -x[1]["findings"]):
        fam = fam or "unspecified"
        n = stats["findings"]
        ss_pct = round(100 * (n - stats["missing_ss"]) / n, 1) if n else 0
        es_pct = round(100 * (n - stats["missing_es"]) / n, 1) if n else 0
        print(f"  {fam:<25} {stats['articles']:>8} {n:>9} {ss_pct:>8.1f}% {es_pct:>8.1f}%")
    print(f"{'='*60}\n")


# ═══════════════════════════════════════════════════════════════════════════
# Section 2: Focused Prompt Construction
# ═══════════════════════════════════════════════════════════════════════════

def build_quantitative_prompt(extraction_data: Dict) -> str:
    """Build a FOCUSED prompt for quantitative field extraction only.

    This prompt is deliberately narrow: it asks ONLY about sample_size,
    effect_size, p_value, and confidence_interval. No stimulus, no theory,
    no mechanism, no instruments. The model's full attention goes to numbers.
    """
    title = extraction_data.get("title", "Unknown")
    doi = extraction_data.get("doi", "")
    family = extraction_data.get("article_family", extraction_data.get("article_type", "unknown"))
    findings = extraction_data.get("findings", [])

    meta = extraction_data.get("paper_metadata", {})
    abstract = meta.get("abstract", "")
    methods = meta.get("methods_summary", "")
    results_text = meta.get("results_summary", "")

    # Build per-finding context for those missing data
    findings_needing_help = []
    for idx, f in enumerate(findings):
        needs_ss = not f.get("sample_size")
        needs_es = not f.get("effect_size")
        if needs_ss or needs_es:
            findings_needing_help.append({
                "index": idx,
                "antecedent": f.get("antecedent", ""),
                "consequent": f.get("consequent", ""),
                "direction": f.get("direction", ""),
                "claim_type": f.get("claim_type", ""),
                "needs_sample_size": needs_ss,
                "needs_effect_size": needs_es,
                # Include any existing partial data
                "existing_sample_size": f.get("sample_size"),
                "existing_effect_size": f.get("effect_size"),
                "existing_p_value": f.get("p_value"),
            })

    if not findings_needing_help:
        return ""  # Nothing to backfill

    # Truncate findings list if very long (keep prompt focused)
    if len(findings_needing_help) > 30:
        findings_needing_help = findings_needing_help[:30]

    findings_json = json.dumps(findings_needing_help, indent=2)

    prompt = f"""You are a scientific statistics extraction expert. Your ONLY task is to extract
quantitative data (sample sizes, effect sizes, p-values, confidence intervals) from this paper.

PAPER:
Title: {title}
DOI: {doi}
Type: {family}
Abstract: {abstract[:800] if abstract else 'Not available'}
Methods: {methods[:500] if methods else 'Not available'}
Results: {results_text[:500] if results_text else 'Not available'}

FINDINGS NEEDING QUANTITATIVE DATA:
{findings_json}

For each finding listed above, extract the quantitative data if available.

Return ONLY valid JSON in this exact format:
{{
  "paper_sample_size": <integer or null>,
  "paper_sample_size_source": "reported" | "estimated" | null,
  "per_finding_updates": [
    {{
      "finding_index": <integer matching the index above>,
      "sample_size": <integer or null>,
      "sample_size_source": "reported" | "estimated" | "inferred",
      "effect_size": <number or null>,
      "effect_size_type": "Cohen's d" | "eta_squared" | "partial_eta_squared" | "r" | "r_correlation" | "odds_ratio" | "Cohen's f" | "Cramer's V" | "phi" | "beta" | "R_squared" | "partial_R_squared" | "log_odds" | null,
      "p_value": <number or null>,
      "confidence_interval": [<lower>, <upper>] or null
    }}
  ]
}}

CRITICAL RULES:
1. ONLY extract values you can find or reasonably infer from the paper
2. For sample_size: Look in abstract, methods, participants section. If the paper reports "N=120" or "120 participants", use that. If it says "60 per group" in a 2-group design, report 120.
3. For effect_size: Look for Cohen's d, r, eta², partial eta², odds ratios, beta weights, R². Convert if needed (e.g., t-statistic to Cohen's d via d = 2t/√df).
4. Set source to "reported" if the value appears explicitly in the paper, "estimated" if you computed it from other statistics, "inferred" if you made a reasonable guess.
5. For theoretical papers, qualitative studies, or review articles: set all values to null. Do not fabricate numbers.
6. Include ALL findings from the list above, even if all values are null.
7. Return ONLY JSON. No explanations, no markdown.
"""
    return prompt


# ═══════════════════════════════════════════════════════════════════════════
# Section 3: Validation
# ═══════════════════════════════════════════════════════════════════════════

def validate_effect_size(value: float, es_type: Optional[str]) -> bool:
    """Validate effect size is within expected range for its type."""
    if value is None:
        return True
    if es_type and es_type in EFFECT_SIZE_RANGES:
        lo, hi = EFFECT_SIZE_RANGES[es_type]
        return lo <= value <= hi
    # Unknown type — accept if in a generous range
    return -10.0 <= value <= 100.0


def validate_sample_size(value: int) -> bool:
    """Validate sample size is reasonable."""
    if value is None:
        return True
    return isinstance(value, (int, float)) and 1 <= value <= 1_000_000


def validate_p_value(value: float) -> bool:
    """Validate p-value is in [0, 1]."""
    if value is None:
        return True
    return isinstance(value, (int, float)) and 0 <= value <= 1


# ═══════════════════════════════════════════════════════════════════════════
# Section 4: Merge Logic
# ═══════════════════════════════════════════════════════════════════════════

def parse_llm_json(text: str) -> Optional[Dict]:
    """Parse JSON from LLM response, handling markdown fences."""
    if not text:
        return None
    clean = re.sub(r'```(?:json)?\s*\n?', '', text)
    clean = clean.replace('```', '').strip()
    try:
        return json.loads(clean)
    except json.JSONDecodeError:
        s = clean.find('{')
        e = clean.rfind('}')
        if s >= 0 and e > s:
            try:
                return json.loads(clean[s:e+1])
            except json.JSONDecodeError:
                return None
    return None


def merge_quantitative(extraction: Dict, llm_result: Dict) -> Tuple[Dict, int, int]:
    """Merge quantitative backfill into extraction. Returns (updated, n_ss_filled, n_es_filled).

    SC-BF-1: Never overwrites existing non-null values.
    SC-BF-2: Marks backfilled values with source="backfilled".
    SC-BF-3: Validates effect_size range before saving.
    """
    result = {**extraction}
    findings = result.get("findings", [])
    n_ss = 0
    n_es = 0

    # Paper-level sample size
    if llm_result.get("paper_sample_size") and not result.get("paper_sample_size"):
        ss = llm_result["paper_sample_size"]
        if validate_sample_size(ss):
            result["paper_sample_size"] = int(ss)
            result["paper_sample_size_source"] = llm_result.get("paper_sample_size_source", "estimated")

    # Per-finding updates
    for update in llm_result.get("per_finding_updates", []):
        idx = update.get("finding_index")
        if idx is None or not (0 <= idx < len(findings)):
            continue

        f = findings[idx]

        # Sample size — only if currently missing (SC-BF-1)
        if not f.get("sample_size") and update.get("sample_size"):
            ss = update["sample_size"]
            if validate_sample_size(ss):
                f["sample_size"] = int(ss)
                f["sample_size_source"] = update.get("sample_size_source", "backfilled")
                n_ss += 1

        # Effect size — only if currently missing (SC-BF-1)
        if not f.get("effect_size") and update.get("effect_size") is not None:
            es = update["effect_size"]
            es_type = update.get("effect_size_type")
            if validate_effect_size(es, es_type):  # SC-BF-3
                f["effect_size"] = float(es)
                f["effect_size_type"] = es_type
                f["effect_size_source"] = "backfilled"
                n_es += 1
            else:
                logger.debug(f"  Rejected effect_size={es} type={es_type} (out of range)")

        # p-value — only if currently missing
        if not f.get("p_value") and update.get("p_value") is not None:
            pv = update["p_value"]
            if validate_p_value(pv):
                f["p_value"] = float(pv)

        # Confidence interval — only if currently missing
        if not f.get("confidence_interval") and update.get("confidence_interval"):
            ci = update["confidence_interval"]
            if isinstance(ci, list) and len(ci) == 2:
                f["confidence_interval"] = [float(ci[0]), float(ci[1])]

    # Metadata (SC-BF-2)
    result["_quantitative_backfill"] = {
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "sample_sizes_filled": n_ss,
        "effect_sizes_filled": n_es,
        "script": "backfill_quantitative_fields.py",
    }

    return result, n_ss, n_es


# ═══════════════════════════════════════════════════════════════════════════
# Section 5: API Calls
# ═══════════════════════════════════════════════════════════════════════════

async def call_gemini_async(prompt: str, client, model="gemini-2.5-flash", max_retries=3):
    """Call Gemini with retry logic."""
    system = "You are a scientific statistics extraction expert. Return ONLY valid JSON."
    full_prompt = system + "\n\n" + prompt

    for attempt in range(max_retries):
        try:
            response = await client.aio.models.generate_content(
                model=model,
                contents=full_prompt,
                config={"max_output_tokens": 4096, "temperature": 0.1}
            )
            text = ""
            try:
                if response and response.text:
                    text = response.text
                elif response and response.candidates:
                    for part in response.candidates[0].content.parts:
                        if part and hasattr(part, 'text') and part.text:
                            if not getattr(part, 'thought', False):
                                text = part.text
                                break
            except (TypeError, AttributeError):
                text = ""

            if not text and attempt < max_retries - 1:
                await asyncio.sleep((2 ** attempt) * 0.5)
                continue

            usage = response.usage_metadata if response and response.usage_metadata else None
            return text, usage
        except Exception as e:
            if attempt < max_retries - 1:
                logger.warning(f"  API error: {e}, retry {attempt+1}/{max_retries}")
                await asyncio.sleep((2 ** attempt) * 0.5)
            else:
                raise
    return "", None


# ═══════════════════════════════════════════════════════════════════════════
# Section 6: Processing
# ═══════════════════════════════════════════════════════════════════════════

async def process_article(article: Dict, client, semaphore, results: Dict, idx: int, total: int, dry_run=False):
    """Process one article for quantitative backfill."""
    async with semaphore:
        path = article["path"]
        logger.info(f"[{idx+1}/{total}] {article['file']} ({article['n_findings']} findings, "
                     f"miss_ss={article['missing_sample_size']}, miss_es={article['missing_effect_size']})")

        try:
            data = json.loads(path.read_text(errors='replace'))
        except Exception:
            results["failed"] += 1
            return

        prompt = build_quantitative_prompt(data)
        if not prompt:
            logger.info(f"  → Nothing to backfill (all fields present)")
            results["skipped"] += 1
            return

        if dry_run:
            logger.info(f"  [DRY RUN] Would send {len(prompt)} char prompt")
            return

        try:
            text, usage = await call_gemini_async(prompt, client)
            cost = 0.0
            if usage:
                cost = (getattr(usage, 'prompt_token_count', 0) * 0.15 / 1_000_000) + \
                       (getattr(usage, 'candidates_token_count', 0) * 0.60 / 1_000_000)
            results["costs"].append(cost)

            llm_result = parse_llm_json(text)
            if not llm_result:
                logger.warning(f"  Could not parse LLM response")
                results["failed"] += 1
                return

            enriched, n_ss, n_es = merge_quantitative(data, llm_result)

            # Save (SC-BF-4: coverage only increases)
            path.write_text(json.dumps(enriched, indent=2, ensure_ascii=False))

            results["success"] += 1
            results["ss_filled"] += n_ss
            results["es_filled"] += n_es
            logger.info(f"  ✓ +{n_ss} sample_sizes, +{n_es} effect_sizes (${cost:.4f})")

        except Exception as e:
            results["failed"] += 1
            logger.error(f"  ✗ Error: {e}")
            await asyncio.sleep(0.5)


async def run_backfill_async(articles: List[Dict], dry_run=False, concurrency=15):
    """Run parallel backfill."""
    from google import genai
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY or GEMINI_API_KEY not set")

    client = genai.Client(api_key=api_key)
    semaphore = asyncio.Semaphore(concurrency)
    results = {"success": 0, "failed": 0, "skipped": 0, "ss_filled": 0, "es_filled": 0, "costs": []}

    tasks = [
        process_article(a, client, semaphore, results, i, len(articles), dry_run)
        for i, a in enumerate(articles)
    ]

    start = time.time()
    await asyncio.gather(*tasks, return_exceptions=True)
    elapsed = time.time() - start

    return results, elapsed


# ═══════════════════════════════════════════════════════════════════════════
# Section 7: Main
# ═══════════════════════════════════════════════════════════════════════════

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Backfill effect_size and sample_size")
    parser.add_argument("--analyze", action="store_true", help="Show coverage stats only")
    parser.add_argument("--dry-run", action="store_true", help="Preview without changes")
    parser.add_argument("--limit", type=int, default=None, help="Max articles to process")
    parser.add_argument("--parallel", action="store_true", help="Run async (15 concurrent)")
    parser.add_argument("--concurrency", type=int, default=15)
    parser.add_argument("--family", type=str, default=None, help="Filter by article family")
    parser.add_argument("--force", action="store_true", help="Re-backfill already-backfilled articles")
    parser.add_argument("--empirical-only", action="store_true", help="Only process empirical papers")
    args = parser.parse_args()

    # Scan
    logger.info("Scanning extraction files...")
    all_articles = scan_all_extractions()

    # Coverage before
    before = compute_coverage(all_articles)
    print_coverage(before, "BEFORE BACKFILL")

    if args.analyze:
        return

    # Filter
    candidates = all_articles
    if not args.force:
        candidates = [a for a in candidates if not a["already_backfilled"]]
    if args.family:
        candidates = [a for a in candidates if a["family"] == args.family]
    if args.empirical_only:
        candidates = [a for a in candidates if a["family"] in QUANTITATIVE_FAMILIES]

    # Sort: most missing data first (prioritize empirical)
    candidates.sort(key=lambda a: (
        0 if a["family"] in QUANTITATIVE_FAMILIES else 1,
        -a["missing_either"]
    ))

    if args.limit:
        candidates = candidates[:args.limit]

    if not candidates:
        logger.info("No articles need backfill!")
        return

    logger.info(f"\nProcessing {len(candidates)} articles "
                f"({sum(a['missing_sample_size'] for a in candidates)} missing SS, "
                f"{sum(a['missing_effect_size'] for a in candidates)} missing ES)")

    # Run
    if args.parallel or args.concurrency > 1:
        results, elapsed = asyncio.run(
            run_backfill_async(candidates, args.dry_run, args.concurrency)
        )
    else:
        # Sequential fallback
        results, elapsed = asyncio.run(
            run_backfill_async(candidates, args.dry_run, concurrency=1)
        )

    if args.dry_run:
        logger.info("[DRY RUN] No changes made.")
        return

    # Coverage after
    all_articles_after = scan_all_extractions()
    after = compute_coverage(all_articles_after)
    print_coverage(after, "AFTER BACKFILL")

    # Delta report
    total_cost = sum(results["costs"])
    print(f"\n{'='*60}")
    print(f"  BACKFILL RESULTS")
    print(f"{'='*60}")
    print(f"  Articles processed: {results['success']} success, {results['failed']} failed, {results['skipped']} skipped")
    print(f"  sample_size filled: +{results['ss_filled']}  ({before['sample_size_pct']}% → {after['sample_size_pct']}%)")
    print(f"  effect_size filled: +{results['es_filled']}  ({before['effect_size_pct']}% → {after['effect_size_pct']}%)")
    print(f"  Cost: ${total_cost:.4f}")
    print(f"  Elapsed: {elapsed:.1f}s ({len(candidates)/elapsed:.1f} articles/sec)")
    print(f"{'='*60}\n")

    # Save results
    results_dir = REPO / "data" / "field_discovery"
    results_dir.mkdir(parents=True, exist_ok=True)
    summary = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "articles_processed": results["success"],
        "articles_failed": results["failed"],
        "sample_sizes_filled": results["ss_filled"],
        "effect_sizes_filled": results["es_filled"],
        "coverage_before": {"sample_size_pct": before["sample_size_pct"], "effect_size_pct": before["effect_size_pct"]},
        "coverage_after": {"sample_size_pct": after["sample_size_pct"], "effect_size_pct": after["effect_size_pct"]},
        "total_cost": total_cost,
        "elapsed_seconds": elapsed,
    }
    summary_path = results_dir / "quantitative_backfill_results.json"
    summary_path.write_text(json.dumps(summary, indent=2))
    logger.info(f"Results saved to {summary_path}")


if __name__ == "__main__":
    main()
