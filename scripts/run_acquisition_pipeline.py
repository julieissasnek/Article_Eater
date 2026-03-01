#!/usr/bin/env python3
"""
Unified Article Acquisition Pipeline — single entry-point for the full cycle.

Chains:
1. Refresh research queue from WoB gaps
2. Run automated Semantic Scholar searcher
3. Run scholar query expander
4. Run snowball expansion (citation graph)
5. Enrich new candidates via Semantic Scholar
6. Push un-PDF'd items to Zotero
7. Generate acquisition digest
8. Generate AI search prompts

Each step is idempotent and skippable via flags.

Usage:
  python scripts/run_acquisition_pipeline.py                # Run all steps
  python scripts/run_acquisition_pipeline.py --dry-run      # Preview only
  python scripts/run_acquisition_pipeline.py --skip enrich  # Skip enrichment
  python scripts/run_acquisition_pipeline.py --only digest prompts  # Run specific steps
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

ALL_STEPS = [
    "queue",       # Refresh research queue
    "search",      # Automated S2 searcher
    "expand",      # Scholar query expander
    "snowball",    # Snowball citation expansion
    "enrich",      # Semantic Scholar enrichment
    "zotero",      # Push to Zotero
    "digest",      # Generate acquisition digest
    "prompts",     # Generate AI search prompts
]


def run_step(name: str, cmd: list[str], dry_run: bool = False) -> bool:
    """Run a pipeline step, returning True on success."""
    print(f"\n{'='*60}")
    print(f"  STEP: {name}")
    print(f"{'='*60}")

    if dry_run:
        print(f"  [DRY-RUN] Would run: {' '.join(cmd)}")
        return True

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600,  # 10 min per step
            cwd=str(PROJECT_ROOT),
        )
        if result.stdout.strip():
            for line in result.stdout.strip().split("\n"):
                print(f"  {line}")
        if result.stderr.strip():
            for line in result.stderr.strip().split("\n"):
                print(f"  [stderr] {line}")
        if result.returncode != 0:
            print(f"  ⚠️  Step '{name}' exited with code {result.returncode}")
            return False
        print(f"  ✅  Step '{name}' completed successfully")
        return True
    except subprocess.TimeoutExpired:
        print(f"  ⏱  Step '{name}' timed out after 600s")
        return False
    except Exception as exc:
        print(f"  ❌  Step '{name}' failed: {exc}")
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dry-run", action="store_true", help="Preview without executing")
    parser.add_argument("--skip", nargs="+", choices=ALL_STEPS, default=[],
                        help="Steps to skip")
    parser.add_argument("--only", nargs="+", choices=ALL_STEPS,
                        help="Run only these steps")
    parser.add_argument("--top", type=int, default=40,
                        help="Limit for digest/prompts (default: 40)")
    args = parser.parse_args()

    steps_to_run = args.only if args.only else ALL_STEPS
    steps_to_run = [s for s in steps_to_run if s not in args.skip]

    py = sys.executable
    results: dict[str, bool] = {}
    start = time.monotonic()

    print(f"\n🚀 Article Acquisition Pipeline")
    print(f"   Steps: {', '.join(steps_to_run)}")
    print(f"   Mode:  {'DRY-RUN' if args.dry_run else 'LIVE'}")

    # 1. Refresh research queue
    if "queue" in steps_to_run:
        # The queue refresh is done via Python import since it's a service
        results["queue"] = run_step(
            "Refresh research queue",
            [py, "-c", (
                "import sys; sys.path.insert(0, '.'); "
                "from src.queue.service import ResearchQueueService; "
                "svc = ResearchQueueService(); "
                "targets = svc.refresh_queue(max_gaps=50); "
                "print(f'Queue refreshed: {len(targets)} targets')"
            )],
            dry_run=args.dry_run,
        )

    # 2. Automated S2 searcher
    if "search" in steps_to_run:
        results["search"] = run_step(
            "Automated Semantic Scholar search",
            [py, "-c", (
                "import sys; sys.path.insert(0, '.'); "
                "from src.queue.service import ResearchQueueService; "
                "from src.queue.automated_searcher import AutomatedQueueSearcher; "
                "svc = ResearchQueueService(); "
                "searcher = AutomatedQueueSearcher(svc); "
                "runs = searcher.run_once(); "
                "print(f'Searched {len(runs)} targets'); "
                "[print(f'  {r.target_id}: {r.n_candidates} candidates') for r in runs]"
            )],
            dry_run=args.dry_run,
        )

    # 3. Scholar query expander
    if "expand" in steps_to_run:
        script = PROJECT_ROOT / "scripts" / "scholar_query_expander.py"
        if script.exists():
            results["expand"] = run_step(
                "Scholar query expansion",
                [py, str(script), "scan", "--max-queries", "20"],
                dry_run=args.dry_run,
            )
        else:
            print(f"  ⚠️  Script not found: {script}")
            results["expand"] = False

    # 4. Snowball expansion
    if "snowball" in steps_to_run:
        script = PROJECT_ROOT / "scripts" / "snowball_expand_corpus.py"
        if script.exists():
            results["snowball"] = run_step(
                "Snowball citation expansion",
                [py, str(script), "run", "--min-citations", "2"],
                dry_run=args.dry_run,
            )
        else:
            print(f"  ⚠️  Script not found: {script}")
            results["snowball"] = False

    # 5. Semantic Scholar enrichment
    if "enrich" in steps_to_run:
        script = PROJECT_ROOT / "scripts" / "semantic_scholar_enrichment.py"
        if script.exists():
            results["enrich"] = run_step(
                "Semantic Scholar metadata enrichment",
                [py, str(script), "repair"],
                dry_run=args.dry_run,
            )
        else:
            print(f"  ⚠️  Script not found: {script}")
            results["enrich"] = False

    # 6. Zotero push
    if "zotero" in steps_to_run:
        zotero_args = [py, str(PROJECT_ROOT / "scripts" / "zotero_push.py")]
        if args.dry_run:
            zotero_args.append("--dry-run")
        results["zotero"] = run_step(
            "Zotero push",
            zotero_args,
            dry_run=False,  # zotero_push handles its own dry-run
        )

    # 7. Acquisition digest
    if "digest" in steps_to_run:
        results["digest"] = run_step(
            "Acquisition digest",
            [py, str(PROJECT_ROOT / "scripts" / "acquisition_digest.py"),
             "--top", str(args.top)],
            dry_run=args.dry_run,
        )

    # 8. AI search prompts
    if "prompts" in steps_to_run:
        results["prompts"] = run_step(
            "AI search prompts",
            [py, str(PROJECT_ROOT / "scripts" / "generate_ai_search_prompts.py"),
             "--top", str(args.top)],
            dry_run=args.dry_run,
        )

    # Summary
    elapsed = time.monotonic() - start
    print(f"\n{'='*60}")
    print(f"  PIPELINE SUMMARY")
    print(f"{'='*60}")
    passed = sum(1 for v in results.values() if v)
    failed = sum(1 for v in results.values() if not v)
    for step, ok in results.items():
        status = "✅" if ok else "❌"
        print(f"  {status} {step}")
    print(f"\n  {passed} passed, {failed} failed, {elapsed:.1f}s elapsed")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
