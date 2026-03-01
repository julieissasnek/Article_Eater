#!/usr/bin/env python3
"""
Run reflexes — CLI for local health checks and auto-repair.

Usage:
    python scripts/run_reflexes.py                  # Run all reflexes (detect-only)
    python scripts/run_reflexes.py --component extraction    # Run extraction reflexes only
    python scripts/run_reflexes.py --fix            # Run reflexes with auto-fix enabled
    python scripts/run_reflexes.py --trends         # Show health trends from overseer DB
    python scripts/run_reflexes.py --summary        # Show summary statistics

The script initializes all 10 reflexes, runs them, and prints a formatted summary table.
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime
from typing import List

# Add parent directories to path
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root))

from src.qa.reflex_system import (
    ReflexRegistry, ReflexResult, ReflexEvent,
    DirectionNormalizationReflex,
    VagueAntecedentDetectorReflex,
    MissingSampleSizeReflex,
    MalformedExtractionJsonReflex,
    ZeroFindingsExtractionReflex,
    OrphanedVocabTermsReflex,
    BrokenInstrumentIdReferencesReflex,
    StaleLookupTableReflex,
    OutOfRangeCalibrationParametersReflex,
    StaleExtractionFilesReflex,
)


def create_reflexes(repo_root: Path) -> ReflexRegistry:
    """Create and register all reflexes."""
    registry = ReflexRegistry(repo_root)

    # Extraction reflexes
    registry.register(DirectionNormalizationReflex(repo_root))
    registry.register(VagueAntecedentDetectorReflex(repo_root))
    registry.register(MissingSampleSizeReflex(repo_root))
    registry.register(MalformedExtractionJsonReflex(repo_root))
    registry.register(ZeroFindingsExtractionReflex(repo_root))

    # Schema reflexes
    registry.register(OrphanedVocabTermsReflex(repo_root))
    registry.register(BrokenInstrumentIdReferencesReflex(repo_root))
    registry.register(StaleLookupTableReflex(repo_root))

    # Calibration reflexes
    registry.register(OutOfRangeCalibrationParametersReflex(repo_root))

    # Pipeline reflexes
    registry.register(StaleExtractionFilesReflex(repo_root))

    return registry


def print_summary_table(results: List[ReflexResult]):
    """Print results in a nice summary table."""
    print("\n" + "=" * 120)
    print(f"REFLEX HEALTH CHECK — {datetime.now().isoformat()}")
    print("=" * 120)
    print(f"{'Reflex ID':<18} {'Status':<12} {'Detected':<10} {'Auto-Fixed':<12} {'Attention':<12} {'Component':<25}")
    print("-" * 120)

    for result in results:
        status = "PASS" if result.passed else ("FIXED" if result.auto_fixed else "FAIL")
        status_color = "✓" if result.passed else ("✔" if result.auto_fixed else "✗")

        reflex_id = result.reflex_id
        component = ""
        if result.event:
            component = result.event.component

        print(
            f"{reflex_id:<18} {status_color} {status:<10} "
            f"{'Yes' if result.detected_issue else 'No':<10} "
            f"{'Yes' if result.auto_fixed else 'No':<12} "
            f"{'Yes' if result.needs_attention else 'No':<12} "
            f"{component:<25}"
        )

    print("=" * 120)

    # Summary line
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    detected = sum(1 for r in results if r.detected_issue)
    fixed = sum(1 for r in results if r.auto_fixed)
    needs_attention = sum(1 for r in results if r.needs_attention)

    print(f"\nSummary: {passed}/{total} passed, {detected} detected issues, {fixed} auto-fixed, {needs_attention} need attention")
    print()


def print_health_trends(registry: ReflexRegistry):
    """Print health trends from overseer DB."""
    trends = registry.get_health_trends(days=7)

    print("\n" + "=" * 80)
    print("REFLEX HEALTH TRENDS (Last 7 days)")
    print("=" * 80)

    if not trends["days"]:
        print("No trend data available.")
        return

    print(f"{'Date':<12} {'Total Events':<15} {'Detected':<12} {'Auto-Fixed':<12} {'Unresolved':<12}")
    print("-" * 80)

    for day_data in trends["days"]:
        print(
            f"{day_data['date']:<12} {day_data['total']:<15} {day_data['detected']:<12} "
            f"{day_data['auto_fixed']:<12} {day_data['unresolved']:<12}"
        )

    print("-" * 80)
    summary = trends["summary"]
    print(f"{'TOTAL':<12} {summary['total_events']:<15} {summary['detected_count']:<12} "
          f"{summary['auto_fixed_count']:<12} {summary['unresolved_count']:<12}")

    status = "✓ Improving" if trends["improving"] else ("✗ Degrading" if trends["improving"] is False else "? Unknown")
    print(f"\nTrend Status: {status}\n")
    print("=" * 80 + "\n")


def print_summary_stats(registry: ReflexRegistry):
    """Print summary statistics."""
    stats = registry.get_summary_stats()

    print("\n" + "=" * 80)
    print("REFLEX SYSTEM SUMMARY STATISTICS")
    print("=" * 80)

    print(f"Total Events Logged: {stats.get('total_events', 0)}")
    print(f"Reflexes Registered: {stats.get('reflexes_registered', 0)}")

    severity = stats.get('severity_breakdown', {})
    print(f"\nEvents by Severity:")
    for sev in ["critical", "error", "warning", "info"]:
        count = severity.get(sev, 0)
        if count > 0:
            print(f"  {sev.upper():<12}: {count}")

    print(f"\nTop 10 Recurring Issues:")
    for issue in stats.get('top_recurring_issues', []):
        print(f"  {issue['reflex_id']:<18}: {issue['count']} events")

    print("\n" + "=" * 80 + "\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run reflexes for local health checks and auto-repair"
    )
    parser.add_argument(
        "--component",
        type=str,
        help="Run reflexes for a specific component only (e.g., 'extraction')"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Enable auto-fix mode (default: detect-only)"
    )
    parser.add_argument(
        "--trends",
        action="store_true",
        help="Show health trends from overseer DB"
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Show summary statistics"
    )

    args = parser.parse_args()

    # Create registry
    registry = create_reflexes(repo_root)

    # Show trends if requested
    if args.trends:
        print_health_trends(registry)
        return 0

    # Show summary if requested
    if args.summary:
        print_summary_stats(registry)
        return 0

    # Run reflexes
    if args.component:
        print(f"Running reflexes for component: {args.component}")
        results = registry.run_component(args.component)
    else:
        print("Running all reflexes...")
        results = registry.run_all()

    # Print summary table
    print_summary_table(results)

    # Return exit code based on results
    needs_attention = sum(1 for r in results if r.needs_attention)
    if needs_attention > 0:
        print(f"⚠ {needs_attention} issue(s) need attention\n")
        return 1

    print("✓ All health checks passed\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
