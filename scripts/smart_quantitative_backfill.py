#!/usr/bin/env python3
"""Smart Quantitative Backfill — Wave 7

Checks whether v3 surgical updates already included the quantitative_backfill
(sample_size + effect_size per finding). If not, runs a targeted pass to fill
ONLY that gap. If yes, reports before/after statistics and exits.

Usage:
    python3 scripts/smart_quantitative_backfill.py           # auto-detect + run
    python3 scripts/smart_quantitative_backfill.py --dry-run # just report, don't call API
    python3 scripts/smart_quantitative_backfill.py --limit 5 # test on 5 articles
"""

import json
import os
import sys
import time
import logging
import asyncio
from pathlib import Path
from datetime import datetime, timezone

# Load .env if present
env_file = Path(__file__).parent.parent / ".env"
if env_file.exists():
    try:
        for line in open(env_file):
            if "=" in line and not line.startswith("#"):
                k, v = line.strip().split("=", 1)
                os.environ[k] = v
    except PermissionError:
        pass  # Sandbox may block .env reading

REPO = Path(__file__).parent.parent
sys.path.insert(0, str(REPO))

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)


# ── Phase 1: Audit current state ──────────────────────────────────────

def audit_extractions():
    """Scan all extraction JSONs and classify their state."""
    ext_dir = REPO / "data" / "extractions"
    
    stats = {
        "total_files": 0,
        "files_with_findings": 0,
        "v3_count": 0,
        "not_v3_count": 0,
        "total_findings": 0,
        "findings_with_sample_size": 0,
        "findings_with_effect_size": 0,
        "findings_with_both": 0,
        "v3_with_backfill_marker": 0,      # Has quantitative_backfill_count field
        "v3_without_backfill_marker": 0,    # v3 but NO quantitative_backfill_count
        "needs_backfill": [],                # Files that need quantitative backfill
    }
    
    for ext_file in ext_dir.glob("*.json"):
        try:
            data = json.loads(ext_file.read_text(errors='replace'))
            if not isinstance(data, dict):
                continue
            stats["total_files"] += 1
            
            findings = data.get("findings", [])
            if not findings:
                continue
            stats["files_with_findings"] += 1
            
            is_v3 = data.get("extraction_version") == "v3.0"
            if is_v3:
                stats["v3_count"] += 1
            else:
                stats["not_v3_count"] += 1
            
            # Count quantitative field coverage
            file_has_gaps = False
            for f in findings:
                stats["total_findings"] += 1
                has_s = bool(f.get("sample_size"))
                has_e = bool(f.get("effect_size"))
                if has_s:
                    stats["findings_with_sample_size"] += 1
                if has_e:
                    stats["findings_with_effect_size"] += 1
                if has_s and has_e:
                    stats["findings_with_both"] += 1
                if not has_s:
                    file_has_gaps = True
            
            # Check for backfill marker
            if is_v3:
                if data.get("quantitative_backfill_count") is not None:
                    stats["v3_with_backfill_marker"] += 1
                else:
                    stats["v3_without_backfill_marker"] += 1
                    # Only queue for backfill if it has findings with missing sample_size
                    if file_has_gaps:
                        stats["needs_backfill"].append({
                            "file": ext_file.name,
                            "path": ext_file,
                            "n_findings": len(findings),
                            "doi": data.get("doi", ""),
                        })
        except (json.JSONDecodeError, Exception):
            pass
    
    return stats


def print_report(stats, label="CURRENT STATE"):
    """Pretty-print the audit report."""
    n = max(stats["total_findings"], 1)
    fw = max(stats["files_with_findings"], 1)
    
    print(f"\n{'='*60}")
    print(f"  📊 QUANTITATIVE BACKFILL REPORT — {label}")
    print(f"{'='*60}")
    print(f"  Extraction files:          {stats['total_files']}")
    print(f"  Files with findings:       {stats['files_with_findings']}")
    print(f"  Already v3.0:              {stats['v3_count']}")
    print(f"  Not yet v3.0:              {stats['not_v3_count']}")
    print(f"  Total findings:            {stats['total_findings']}")
    print(f"")
    print(f"  With sample_size:          {stats['findings_with_sample_size']} ({100*stats['findings_with_sample_size']//n}%)")
    print(f"  With effect_size:          {stats['findings_with_effect_size']} ({100*stats['findings_with_effect_size']//n}%)")
    print(f"  With BOTH:                 {stats['findings_with_both']} ({100*stats['findings_with_both']//n}%)")
    print(f"  MISSING sample_size:       {stats['total_findings'] - stats['findings_with_sample_size']}")
    print(f"")
    print(f"  v3 WITH backfill marker:   {stats['v3_with_backfill_marker']}")
    print(f"  v3 WITHOUT backfill:       {stats['v3_without_backfill_marker']}")
    print(f"  Files needing backfill:    {len(stats['needs_backfill'])}")
    print(f"{'='*60}\n")


# ── Phase 2: Run targeted backfill ────────────────────────────────────

def run_targeted_backfill(articles, dry_run=False, limit=None):
    """Run quantitative backfill ONLY on articles that need it (sequential)."""
    from scripts.v3_surgical_update import (
        build_surgical_update_prompt,
        call_gemini_surgical,
        merge_v3_fields,
    )

    if limit:
        articles = articles[:limit]

    logger.info(f"Starting targeted quantitative backfill for {len(articles)} articles")
    results = {"success": 0, "failed": 0, "total_backfilled_findings": 0, "costs": []}

    for i, article in enumerate(articles):
        filename = article["file"]
        doi = article["doi"]

        logger.info(f"[{i+1}/{len(articles)}] Backfilling {filename} ({article['n_findings']} findings, DOI: {doi})")

        try:
            extraction_data = json.loads(article["path"].read_text(errors='replace'))
        except Exception:
            logger.warning(f"  Could not load extraction file")
            results["failed"] += 1
            continue

        prompt = build_surgical_update_prompt(extraction_data)

        if dry_run:
            logger.info(f"  [DRY RUN] Would backfill with {len(prompt)} char prompt")
            continue

        try:
            response_text, usage = call_gemini_surgical(prompt)
            cost = 0.0
            if usage:
                cost = (getattr(usage, 'prompt_token_count', 0) * 0.15 / 1_000_000) + \
                       (getattr(usage, 'candidates_token_count', 0) * 0.60 / 1_000_000)
            results["costs"].append(cost)

            enriched = merge_v3_fields(extraction_data, response_text)

            backfill_count = enriched.get("quantitative_backfill_count", 0)
            results["total_backfilled_findings"] += backfill_count

            article["path"].write_text(json.dumps(enriched, indent=2, ensure_ascii=False))
            results["success"] += 1
            logger.info(f"  ✓ Backfilled {backfill_count} findings (${cost:.4f})")

            time.sleep(0.5)

        except Exception as e:
            results["failed"] += 1
            logger.error(f"  ✗ Error: {e}")
            time.sleep(1)

    total_cost = sum(results["costs"])
    logger.info(f"\n{'='*60}")
    logger.info(f"TARGETED BACKFILL COMPLETE")
    logger.info(f"  Success: {results['success']}/{len(articles)}")
    logger.info(f"  Failed: {results['failed']}")
    logger.info(f"  Findings backfilled: {results['total_backfilled_findings']}")
    logger.info(f"  Total cost: ${total_cost:.4f}")
    logger.info(f"{'='*60}")

    return results


async def process_article_async(article, client, semaphore, results, idx, total, build_prompt_fn, merge_fn):
    """Process a single article asynchronously for quantitative backfill."""
    from scripts.v3_surgical_update import call_gemini_surgical_async

    async with semaphore:
        filename = article["file"]
        doi = article["doi"]

        logger.info(f"[{idx+1}/{total}] Backfilling {filename} ({article['n_findings']} findings, DOI: {doi})")

        try:
            extraction_data = json.loads(article["path"].read_text(errors='replace'))
        except Exception:
            logger.warning(f"  Could not load extraction file: {filename}")
            results["failed"] += 1
            return

        prompt = build_prompt_fn(extraction_data)

        try:
            response_text, usage = await call_gemini_surgical_async(prompt, client)
            cost = 0.0
            if usage:
                cost = (getattr(usage, 'prompt_token_count', 0) * 0.15 / 1_000_000) + \
                       (getattr(usage, 'candidates_token_count', 0) * 0.60 / 1_000_000)
            results["costs"].append(cost)

            enriched = merge_fn(extraction_data, response_text)

            backfill_count = enriched.get("quantitative_backfill_count", 0)
            results["total_backfilled_findings"] += backfill_count

            article["path"].write_text(json.dumps(enriched, indent=2, ensure_ascii=False))
            results["success"] += 1
            logger.info(f"  ✓ [{idx+1}] Backfilled {backfill_count} findings (${cost:.4f})")

        except Exception as e:
            results["failed"] += 1
            logger.error(f"  ✗ [{idx+1}] Error: {e}")
            await asyncio.sleep(0.5)


async def run_targeted_backfill_async(articles, limit=None, concurrency=15):
    """Run quantitative backfill with async parallelization."""
    from google import genai
    from scripts.v3_surgical_update import build_surgical_update_prompt, merge_v3_fields

    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY or GEMINI_API_KEY not set")

    client = genai.Client(api_key=api_key)

    if limit:
        articles = articles[:limit]

    logger.info(f"Starting PARALLEL quantitative backfill for {len(articles)} articles (concurrency={concurrency})")

    results = {"success": 0, "failed": 0, "total_backfilled_findings": 0, "costs": []}
    semaphore = asyncio.Semaphore(concurrency)

    tasks = [
        process_article_async(
            article, client, semaphore, results, idx, len(articles),
            build_surgical_update_prompt, merge_v3_fields
        )
        for idx, article in enumerate(articles)
    ]

    start_time = time.time()
    await asyncio.gather(*tasks, return_exceptions=True)
    elapsed = time.time() - start_time

    total_cost = sum(results["costs"])
    articles_per_sec = len(articles) / elapsed if elapsed > 0 else 0

    logger.info(f"\n{'='*60}")
    logger.info(f"TARGETED BACKFILL COMPLETE (PARALLEL)")
    logger.info(f"  Success: {results['success']}/{len(articles)}")
    logger.info(f"  Failed: {results['failed']}")
    logger.info(f"  Findings backfilled: {results['total_backfilled_findings']}")
    logger.info(f"  Total cost: ${total_cost:.4f}")
    logger.info(f"  Elapsed: {elapsed:.1f}s ({articles_per_sec:.2f} articles/sec)")
    logger.info(f"{'='*60}")

    return results


# ── Main ──────────────────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Smart Quantitative Backfill")
    parser.add_argument("--dry-run", action="store_true", help="Report only, don't call API")
    parser.add_argument("--limit", type=int, help="Limit number of articles to backfill")
    parser.add_argument("--force", action="store_true", help="Run even if backfill markers exist")
    parser.add_argument("--parallel", action="store_true", help="Run with async parallelization (faster)")
    parser.add_argument("--concurrency", type=int, default=15, help="Max concurrent API calls (default: 15)")
    args = parser.parse_args()

    # Phase 1: Audit
    print("\n🔍 Phase 1: Auditing extraction data quality...\n")
    before_stats = audit_extractions()
    print_report(before_stats, "BEFORE")

    needs_backfill = before_stats["needs_backfill"]
    already_done = before_stats["v3_with_backfill_marker"]

    # Decision logic
    if already_done > 0 and len(needs_backfill) == 0:
        print("✅ ALL v3 articles already have quantitative backfill markers.")
        print(f"   {already_done} articles were processed with the new prompt.")
        print(f"   No further work needed. Exiting.\n")
        return

    if already_done > 0 and not args.force:
        print(f"⚠️  {already_done} articles already have backfill, {len(needs_backfill)} still need it.")
        print(f"   Running targeted backfill on the {len(needs_backfill)} remaining articles.\n")
    elif already_done == 0:
        print(f"📋 No backfill markers found — the previous surgical run used the OLD prompt.")
        print(f"   {len(needs_backfill)} articles need quantitative backfill.\n")

    if not needs_backfill:
        print("✅ No articles need backfill. All findings have sample_size. Exiting.\n")
        return

    # Phase 2: Run
    if args.dry_run:
        print(f"🏃 Phase 2: [DRY RUN] Would backfill {len(needs_backfill)} articles\n")
        run_targeted_backfill(needs_backfill, dry_run=True, limit=args.limit)
    elif args.parallel:
        print(f"🏃 Phase 2: Running PARALLEL quantitative backfill on {len(needs_backfill)} articles (concurrency={args.concurrency})...\n")
        asyncio.run(run_targeted_backfill_async(needs_backfill, limit=args.limit, concurrency=args.concurrency))
    else:
        print(f"🏃 Phase 2: Running quantitative backfill on {len(needs_backfill)} articles...\n")
        run_targeted_backfill(needs_backfill, dry_run=False, limit=args.limit)

    # Phase 3: Re-audit
    print("\n🔍 Phase 3: Re-auditing after backfill...\n")
    after_stats = audit_extractions()
    print_report(after_stats, "AFTER")

    # Delta
    delta_s = after_stats["findings_with_sample_size"] - before_stats["findings_with_sample_size"]
    delta_e = after_stats["findings_with_effect_size"] - before_stats["findings_with_effect_size"]
    print(f"📈 IMPROVEMENT:")
    print(f"   sample_size: +{delta_s} findings")
    print(f"   effect_size: +{delta_e} findings")
    print()


if __name__ == "__main__":
    main()
