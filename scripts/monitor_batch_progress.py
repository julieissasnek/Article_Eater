#!/usr/bin/env python3
"""
Batch Integration Progress Monitor
===================================
Watches data/integration_results/ for completed batch result files,
reports progress across all 11 batches, and recommends when to spin
up additional AG instances.

Usage:
    # One-shot status check
    python3 scripts/monitor_batch_progress.py

    # Continuous watch (polls every 30s)
    python3 scripts/monitor_batch_progress.py --watch

    # Custom poll interval (seconds)
    python3 scripts/monitor_batch_progress.py --watch --interval 60
"""

import argparse
import json
import glob
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = PROJECT_ROOT / "data" / "integration_results"
MANIFEST_PATH = PROJECT_ROOT / "data" / "extractions" / "batch_manifest.json"
EXTRACTIONS_DIR = PROJECT_ROOT / "data" / "extractions"

# ANSI colors
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"


def load_manifest():
    """Load the batch manifest to know expected batches."""
    with open(MANIFEST_PATH) as f:
        return json.load(f)


def scan_results():
    """Scan for completed batch result files."""
    results = {}
    pattern = str(RESULTS_DIR / "batch_*_results.json")
    for fpath in sorted(glob.glob(pattern)):
        fname = os.path.basename(fpath)
        # Extract batch number from filename
        try:
            batch_num = int(fname.split("_")[1])
        except (IndexError, ValueError):
            continue

        stat = os.stat(fpath)
        mtime = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
        size = stat.st_size

        try:
            with open(fpath) as f:
                raw = json.load(f)
        except (json.JSONDecodeError, OSError):
            raw = None

        # Handle two formats:
        # 1. Nested: {"batch_id": N, "summary": {...}, "papers": {doi: {...}, ...}}
        # 2. Flat:   {doi: {status, n_findings, ...}, ...}
        if raw and isinstance(raw, dict):
            summary = raw.get("summary")
            papers = raw.get("papers", raw)  # fall back to raw if no "papers" key
        else:
            summary = None
            papers = raw

        results[batch_num] = {
            "path": fpath,
            "size": size,
            "modified": mtime,
            "summary": summary,
            "papers": papers,
        }
    return results


def check_in_progress():
    """
    Check for signs of in-progress work:
    - Partial result files
    - Lock files
    - Work claims
    """
    indicators = {}

    # Check for work_claims (if the orchestrator uses them)
    claims_path = EXTRACTIONS_DIR / "work_claims.json"
    if claims_path.exists():
        try:
            with open(claims_path) as f:
                claims = json.load(f)
            if claims:
                indicators["work_claims"] = len(claims)
        except Exception as e:
            import logging; logging.getLogger(__name__).debug(f"Non-critical: {e}")

    # Check for partial/temp result files
    partial_pattern = str(RESULTS_DIR / "batch_*_partial*.json")
    partials = glob.glob(partial_pattern)
    if partials:
        indicators["partial_files"] = [os.path.basename(p) for p in partials]

    # Check for lock files
    lock_pattern = str(RESULTS_DIR / "*.lock")
    locks = glob.glob(lock_pattern)
    if locks:
        indicators["locks"] = [os.path.basename(l) for l in locks]

    return indicators


def compute_batch_stats(summary, papers):
    """Compute stats from a completed batch result.

    Uses the pre-computed summary if available, otherwise
    computes from the papers dict.
    """
    # Prefer pre-computed summary from the result file
    if summary and isinstance(summary, dict):
        return {
            "total_papers": summary.get("total_papers", 0),
            "integrated": summary.get("integrated", 0),
            "skipped": summary.get("skipped", 0),
            "errored": summary.get("failed", 0) + summary.get("errored", 0),
            "total_findings": summary.get("total_findings", 0),
            "integrated_findings": summary.get("integrated_findings", 0),
            "quality_distribution": summary.get("quality_distribution"),
        }

    # Fallback: compute from papers dict
    if not papers or not isinstance(papers, dict):
        return None

    # Filter to only dict entries (skip metadata keys)
    paper_entries = {k: v for k, v in papers.items() if isinstance(v, dict)}
    if not paper_entries:
        return None

    total = len(paper_entries)
    integrated = sum(1 for v in paper_entries.values() if v.get("status") == "integrated")
    skipped = sum(1 for v in paper_entries.values() if v.get("status") == "skipped")
    errored = sum(1 for v in paper_entries.values() if v.get("status") in ("error", "failed"))
    total_findings = sum(v.get("n_findings", 0) for v in paper_entries.values())
    total_integrated_findings = sum(v.get("n_integrated", 0) for v in paper_entries.values())

    return {
        "total_papers": total,
        "integrated": integrated,
        "skipped": skipped,
        "errored": errored,
        "total_findings": total_findings,
        "integrated_findings": total_integrated_findings,
    }


def print_status(manifest, results, in_progress):
    """Print a comprehensive status dashboard."""
    n_batches = manifest["n_batches"]
    total_papers = manifest["total_papers"]

    print(f"\n{BOLD}{'=' * 62}{RESET}")
    print(f"{BOLD}  📊 Paper Integration Batch Monitor{RESET}")
    print(f"{DIM}  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{RESET}")
    print(f"{BOLD}{'=' * 62}{RESET}\n")

    # Overall progress
    completed_batches = len(results)
    papers_processed = 0
    total_integrated = 0
    total_skipped = 0
    total_errored = 0
    total_findings_all = 0
    total_integrated_findings_all = 0

    for batch_num, result in results.items():
        stats = compute_batch_stats(result.get("summary"), result.get("papers"))
        if stats:
            papers_processed += stats["total_papers"]
            total_integrated += stats["integrated"]
            total_skipped += stats["skipped"]
            total_errored += stats["errored"]
            total_findings_all += stats["total_findings"]
            total_integrated_findings_all += stats["integrated_findings"]

    pct = (papers_processed / total_papers * 100) if total_papers else 0
    bar_width = 40
    filled = int(bar_width * pct / 100)
    bar = "█" * filled + "░" * (bar_width - filled)

    print(f"  Overall: {bar} {pct:.1f}%")
    print(f"  {papers_processed}/{total_papers} papers  |  "
          f"{completed_batches}/{n_batches} batches complete\n")

    if papers_processed > 0:
        print(f"  {GREEN}✓ Integrated:{RESET} {total_integrated}  "
              f"{YELLOW}⊘ Skipped:{RESET} {total_skipped}  "
              f"{RED}✗ Errors:{RESET} {total_errored}")
        print(f"  Findings: {total_integrated_findings_all} integrated "
              f"out of {total_findings_all} total\n")

    # Per-batch table
    print(f"  {BOLD}{'Batch':<8}{'Papers':<10}{'Status':<14}{'Integrated':<12}"
          f"{'Skipped':<10}{'Errors':<8}{'Modified':<20}{RESET}")
    print(f"  {'─' * 80}")

    for batch_info in manifest["batches"]:
        batch_id = batch_info["batch_id"]
        count = batch_info["count"]

        if batch_id in results:
            result = results[batch_id]
            stats = compute_batch_stats(result.get("summary"), result.get("papers"))
            if stats:
                status = f"{GREEN}✓ Done{RESET}"
                integrated = str(stats["integrated"])
                skipped = str(stats["skipped"])
                errored = str(stats["errored"]) if stats["errored"] else "—"
                modified = result["modified"].strftime("%H:%M:%S")
            else:
                status = f"{YELLOW}? Empty{RESET}"
                integrated = skipped = errored = "—"
                modified = result["modified"].strftime("%H:%M:%S")
        else:
            status = f"{DIM}⏳ Pending{RESET}"
            integrated = skipped = errored = modified = "—"

        print(f"  {batch_id:<8}{count:<10}{status:<24}{integrated:<12}"
              f"{skipped:<10}{errored:<8}{modified:<20}")

    # In-progress indicators
    if in_progress:
        print(f"\n  {CYAN}🔄 Activity Detected:{RESET}")
        for key, val in in_progress.items():
            print(f"    • {key}: {val}")

    # Recommendations
    print(f"\n  {BOLD}📋 Recommendations:{RESET}")
    pending_batches = [
        b["batch_id"] for b in manifest["batches"]
        if b["batch_id"] not in results
    ]

    if not pending_batches:
        print(f"  {GREEN}  🎉 All batches complete! Run the merge script.{RESET}")
    else:
        # Recommend based on concurrent safety (2-3 at a time)
        active_estimate = len(in_progress.get("locks", []))
        if active_estimate == 0:
            # No locks visible — check if we have any results at all
            if completed_batches == 0:
                print(f"    No batches running yet. Fire up 2-3 AG instances.")
                print(f"    Suggested first batches: {pending_batches[:3]}")
            else:
                can_start = min(3, len(pending_batches))
                next_batches = pending_batches[:can_start]
                print(f"    Previous batch(es) done. Start {can_start} more: {next_batches}")
        else:
            slots = max(0, 3 - active_estimate)
            if slots > 0:
                next_batches = pending_batches[:slots]
                print(f"    {active_estimate} batch(es) active. "
                      f"Can safely start {slots} more: {next_batches}")
            else:
                print(f"    {active_estimate} batch(es) active — "
                      f"wait for one to finish before starting more.")
        print(f"\n    Remaining batches: {pending_batches}")

    print(f"\n{BOLD}{'=' * 62}{RESET}\n")
    return completed_batches, n_batches


def watch_mode(interval):
    """Continuously poll for changes."""
    manifest = load_manifest()
    print(f"{CYAN}Watching for batch results every {interval}s... (Ctrl+C to stop){RESET}")

    prev_completed = -1
    while True:
        results = scan_results()
        in_progress = check_in_progress()

        # Clear screen for clean display
        os.system("clear" if os.name != "nt" else "cls")

        completed, total = print_status(manifest, results, in_progress)

        # Alert on new completions
        if prev_completed >= 0 and completed > prev_completed:
            new = completed - prev_completed
            print(f"\n  {GREEN}{BOLD}🔔 ALERT: {new} new batch(es) completed!{RESET}")
            remaining = total - completed
            if remaining > 0:
                print(f"  {YELLOW}  → Consider firing up another AG instance "
                      f"(batches {completed + 1}–{min(completed + 3, total)}){RESET}")

        prev_completed = completed

        if completed >= total:
            print(f"\n{GREEN}{BOLD}All batches complete! Exiting watch mode.{RESET}")
            break

        try:
            time.sleep(interval)
        except KeyboardInterrupt:
            print(f"\n{DIM}Watch stopped.{RESET}")
            break


def main():
    parser = argparse.ArgumentParser(description="Monitor paper integration batch progress")
    parser.add_argument("--watch", action="store_true", help="Continuous monitoring mode")
    parser.add_argument("--interval", type=int, default=30, help="Poll interval in seconds")
    args = parser.parse_args()

    # Ensure results directory exists
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    manifest = load_manifest()

    if args.watch:
        watch_mode(args.interval)
    else:
        results = scan_results()
        in_progress = check_in_progress()
        print_status(manifest, results, in_progress)


if __name__ == "__main__":
    main()
