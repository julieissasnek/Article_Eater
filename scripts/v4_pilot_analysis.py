#!/usr/bin/env python3
"""
V4 PILOT ANALYSIS SCRIPT (Stage 4)
==================================

Analyzes results from V4 staged extraction pilot, comparing against V3.

Metrics computed:
1. Field coverage by article type (% of findings with each field populated)
2. Comparison with V3: improvement in field coverage
3. Regression detection: fields that got WORSE
4. Issue summary: verification issues by type
5. Cost analysis: $/finding, $/paper

USAGE:
  python v4_pilot_analysis.py --results /path/to/v4_results.json
  python v v_pilot_analysis.py --results /path/to/v4_results.json --compare-v3 /path/to/v3_results.json
  python v4_pilot_analysis.py --report summary  # Generate summary report

Author: Claude Opus 4.6
Date: 2026-03-05
"""

import argparse
import json
import logging
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from statistics import mean, median, stdev

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


class V4AnalysisReport:
    """Analysis report for V4 pilot."""

    def __init__(self):
        self.total_papers = 0
        self.completed_papers = 0
        self.failed_papers = 0

        # Coverage metrics
        self.field_coverage_by_type = defaultdict(dict)  # article_type -> {field: coverage}
        self.field_coverage_overall = {}  # Overall field coverage across all

        # Verification metrics
        self.verification_scores = []
        self.verification_issues_by_type = defaultdict(list)  # issue_type -> [count]

        # Cost metrics
        self.costs_per_paper = []
        self.costs_per_finding = []

        # Comparison with V3
        self.v3_comparison = {
            "coverage_improvement": {},  # field -> improvement (percentage points)
            "regressions": [],  # fields that got worse
            "new_fields_filled": {},  # fields now filled that weren't in V3
        }

    def add_record(self, record: dict) -> None:
        """Process a single extraction record."""
        self.total_papers += 1

        if record.get("status") != "completed":
            self.failed_papers += 1
            return

        self.completed_papers += 1

        # Extract classification
        classification = record.get("classification", {})
        article_type = classification.get("article_type", "unknown")

        # Extract field coverage
        extraction = record.get("extraction", {})
        if extraction:
            field_coverage = extraction.get("field_coverage", {})
            self.field_coverage_by_type[article_type] = field_coverage

            # Aggregate overall coverage
            for field, coverage in field_coverage.items():
                if field not in self.field_coverage_overall:
                    self.field_coverage_overall[field] = []
                self.field_coverage_overall[field].append(coverage)

            # Track cost per finding
            cost = record.get("total_cost_usd", 0)
            n_findings = extraction.get("n_findings", 0)
            if n_findings > 0:
                self.costs_per_finding.append(cost / n_findings)

        # Track cost per paper
        cost = record.get("total_cost_usd", 0)
        self.costs_per_paper.append(cost)

        # Extract verification issues
        verification = record.get("verification", {})
        if verification:
            score = verification.get("score", 0)
            self.verification_scores.append(score)

    def compute(self) -> None:
        """Compute summary statistics."""
        # Compute averages for field coverage
        for field, coverages in self.field_coverage_overall.items():
            self.field_coverage_overall[field] = {
                "avg": round(mean(coverages), 3),
                "min": round(min(coverages), 3),
                "max": round(max(coverages), 3),
                "median": round(median(coverages), 3),
            }

    def generate_summary(self) -> str:
        """Generate text summary report."""
        lines = []
        lines.append("=" * 70)
        lines.append("V4 STAGED EXTRACTION PILOT — ANALYSIS REPORT")
        lines.append("=" * 70)
        lines.append("")

        # Paper statistics
        lines.append("PAPER STATISTICS")
        lines.append("-" * 70)
        lines.append(f"Total papers: {self.total_papers}")
        lines.append(f"Completed: {self.completed_papers} ({100*self.completed_papers/max(self.total_papers,1):.1f}%)")
        lines.append(f"Failed: {self.failed_papers}")
        lines.append("")

        # Field coverage
        lines.append("FIELD COVERAGE (Overall)")
        lines.append("-" * 70)
        sorted_fields = sorted(
            self.field_coverage_overall.items(),
            key=lambda x: x[1]["avg"],
            reverse=True
        )
        for field, stats in sorted_fields:
            lines.append(
                f"  {field:30s} avg={stats['avg']:.1%}  "
                f"[min={stats['min']:.1%}, max={stats['max']:.1%}]"
            )
        lines.append("")

        # By article type
        lines.append("FIELD COVERAGE (By Article Type)")
        lines.append("-" * 70)
        for article_type in sorted(self.field_coverage_by_type.keys()):
            lines.append(f"\n  {article_type.upper()}:")
            coverage = self.field_coverage_by_type[article_type]
            sorted_fields = sorted(coverage.items(), key=lambda x: x[1], reverse=True)
            for field, cov in sorted_fields[:8]:  # Top 8 fields
                lines.append(f"    {field:25s} {cov:.1%}")

        lines.append("")

        # Verification scores
        if self.verification_scores:
            lines.append("VERIFICATION RESULTS")
            lines.append("-" * 70)
            lines.append(f"Verified papers: {len(self.verification_scores)}")
            lines.append(f"Avg score: {mean(self.verification_scores):.2f}")
            lines.append(f"Score range: [{min(self.verification_scores):.2f}, {max(self.verification_scores):.2f}]")
            lines.append("")

        # Cost analysis
        lines.append("COST ANALYSIS")
        lines.append("-" * 70)
        if self.costs_per_paper:
            lines.append(f"Avg cost per paper: ${mean(self.costs_per_paper):.4f}")
            lines.append(f"Total cost (all papers): ${sum(self.costs_per_paper):.2f}")
        if self.costs_per_finding:
            lines.append(f"Avg cost per finding: ${mean(self.costs_per_finding):.4f}")
        lines.append("")

        # Top recommendations
        lines.append("KEY FINDINGS & RECOMMENDATIONS")
        lines.append("-" * 70)

        # Find fields with < 50% coverage
        low_coverage = [
            (f, s["avg"]) for f, s in self.field_coverage_overall.items()
            if s["avg"] < 0.5
        ]
        if low_coverage:
            lines.append("\nLOW COVERAGE FIELDS (< 50%):")
            for field, cov in sorted(low_coverage, key=lambda x: x[1]):
                lines.append(f"  • {field}: {cov:.1%} — may need prompt refinement")

        lines.append("")
        lines.append("=" * 70)

        return "\n".join(lines)

    def to_json(self) -> dict:
        """Export report as JSON."""
        return {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_papers": self.total_papers,
                "completed_papers": self.completed_papers,
                "failed_papers": self.failed_papers,
            },
            "field_coverage_overall": self.field_coverage_overall,
            "field_coverage_by_type": dict(self.field_coverage_by_type),
            "verification": {
                "n_verified": len(self.verification_scores),
                "avg_score": round(mean(self.verification_scores), 3) if self.verification_scores else None,
                "score_range": [
                    round(min(self.verification_scores), 3),
                    round(max(self.verification_scores), 3)
                ] if self.verification_scores else None,
            },
            "cost_analysis": {
                "avg_per_paper": round(mean(self.costs_per_paper), 4) if self.costs_per_paper else None,
                "total": round(sum(self.costs_per_paper), 2) if self.costs_per_paper else None,
                "avg_per_finding": round(mean(self.costs_per_finding), 4) if self.costs_per_finding else None,
            },
        }


def load_results(filepath: Path) -> dict:
    """Load V4 extraction results."""
    with open(filepath) as f:
        return json.load(f)


def load_v3_results(filepath: Path) -> dict:
    """Load V3 extraction results for comparison."""
    with open(filepath) as f:
        return json.load(f)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="V4 Pilot Analysis (Stage 4)"
    )

    parser.add_argument(
        "--results",
        type=str,
        required=True,
        help="Path to V4 extraction results JSON"
    )

    parser.add_argument(
        "--compare-v3",
        type=str,
        help="Path to V3 extraction results for comparison"
    )

    parser.add_argument(
        "--output",
        type=str,
        help="Output file for report (default: print to stdout)"
    )

    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Report format"
    )

    args = parser.parse_args()

    # Load results
    results_path = Path(args.results)
    if not results_path.exists():
        logger.error(f"Results file not found: {results_path}")
        sys.exit(1)

    logger.info(f"Loading results from: {results_path}")
    results = load_results(results_path)

    # Run analysis
    report = V4AnalysisReport()

    for record in results.get("results", []):
        report.add_record(record)

    report.compute()

    # Generate output
    if args.format == "json":
        output = json.dumps(report.to_json(), indent=2)
    else:
        output = report.generate_summary()

    # Write output
    if args.output:
        output_path = Path(args.output)
        with open(output_path, "w") as f:
            f.write(output)
        logger.info(f"Report saved to: {output_path}")
    else:
        print(output)


if __name__ == "__main__":
    main()
