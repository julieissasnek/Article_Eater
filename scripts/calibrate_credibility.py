#!/usr/bin/env python3
"""
Credibility Testing Calibration Script.

Sprint D: TODO 1 Calibration and Tuning
Per Simon: Explicit calibration procedure with documented thresholds.

This script:
1. Loads Gold Standard corpus (expected to pass)
2. Loads Failure Standard corpus (expected to flag)
3. Runs credibility checks against both
4. Computes optimal thresholds
5. Generates calibration report

Usage:
    python scripts/calibrate_credibility.py

Output:
    docs/calibration/CREDIBILITY_CALIBRATION_REPORT_<date>.md

Date: January 20, 2026
"""

import sys
import yaml
import json
import logging
from pathlib import Path
from datetime import datetime, timezone
from dataclasses import dataclass, field
from typing import Dict, List, Any, Tuple, Optional

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.services.credibility_testing import (
    CredibilityTester,
    CredibilityReport,
    CredibilityFlag,
    Decision,
    calibrate_thresholds,
    CalibrationResult,
)
from src.services.web_of_belief import (
    Belief,
    Constraint,
    Credence,
    EpistemicLevel,
    BeliefStatus,
    ConstraintType,
    CausalDirection,
    ScopeConditions,
)

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


# =============================================================================
# DATA LOADERS
# =============================================================================

@dataclass
class TestCase:
    """A test case for calibration."""
    case_id: str
    category: str  # "gold_standard" or "failure_standard"
    expected_outcome: str  # "accept", "review", or "block"
    beliefs: List[Belief]
    constraints: List[Constraint]
    metadata: Dict[str, Any]


def load_gold_standard(gs_path: Path) -> List[TestCase]:
    """Load Gold Standard corpus as test cases (expected to PASS)."""
    test_cases = []
    annotations_dir = gs_path / "v1.0" / "annotations"

    if not annotations_dir.exists():
        logger.warning(f"Gold Standard annotations not found at {annotations_dir}")
        return []

    for yaml_file in annotations_dir.glob("*.yaml"):
        try:
            with open(yaml_file) as f:
                data = yaml.safe_load(f)

            paper_id = data.get('paper_id', yaml_file.stem)
            paper_meta = data.get('paper_characteristics', {})
            expected_beliefs = data.get('expected_beliefs', [])

            # Convert to Belief objects
            beliefs = []
            for eb in expected_beliefs:
                credence_range = eb.get('expected_credence', [0.5, 0.7])
                level_str = eb.get('epistemic_level', 'empirical')
                level_map = {
                    'theoretical': EpistemicLevel.THEORETICAL,
                    'intermediate': EpistemicLevel.INTERMEDIATE,
                    'empirical': EpistemicLevel.EMPIRICAL,
                    'observational': EpistemicLevel.OBSERVATIONAL,
                }

                scope = None
                if eb.get('scope'):
                    scope = ScopeConditions(
                        population=eb['scope'].get('population'),
                        setting=eb['scope'].get('setting'),
                        scope_specified=True
                    )

                beliefs.append(Belief(
                    belief_id=eb.get('id', f"{paper_id}_b{len(beliefs)}"),
                    content=eb.get('content', ''),
                    level=level_map.get(level_str, EpistemicLevel.EMPIRICAL),
                    credence=Credence(
                        value=(credence_range[0] + credence_range[1]) / 2,
                        uncertainty=0.2
                    ),
                    scope=scope,
                ))

            # Build metadata
            methodology_score = paper_meta.get('methodology_score', [0.5, 0.7])
            metadata = {
                'sample_size': 100,  # Default reasonable value for theory papers
                'study_design': paper_meta.get('type', 'theory'),
                'sample_description': 'general population',
                'effect_size': 0.5,  # Moderate effect
            }

            test_cases.append(TestCase(
                case_id=paper_id,
                category="gold_standard",
                expected_outcome="accept",  # Gold Standard should pass
                beliefs=beliefs,
                constraints=[],
                metadata=metadata,
            ))

            logger.info(f"Loaded Gold Standard: {paper_id} ({len(beliefs)} beliefs)")

        except Exception as e:
            logger.error(f"Error loading {yaml_file}: {e}")

    return test_cases


def load_failure_standard(fs_path: Path) -> List[TestCase]:
    """Load Failure Standard corpus as test cases (expected to FLAG)."""
    test_cases = []
    cases_dir = fs_path / "cases"

    if not cases_dir.exists():
        logger.warning(f"Failure Standard cases not found at {cases_dir}")
        return []

    for yaml_file in cases_dir.glob("*.yaml"):
        try:
            with open(yaml_file) as f:
                data = yaml.safe_load(f)

            case_id = data.get('case_id', yaml_file.stem)
            category = data.get('category', 'subtle')
            expected_decision = data.get('expected_decision', 'review')

            # Map expected_decision to expected_outcome
            # Preserve original for borderline detection
            original_expected = expected_decision
            if expected_decision == "block":
                expected_outcome = "block"
            elif expected_decision in ["review", "review_or_accept"]:
                expected_outcome = "review"
            elif expected_decision in ["accept_or_review"]:
                expected_outcome = "borderline"  # Can be accept OR review
            else:
                expected_outcome = "accept"

            # Convert beliefs
            beliefs = []
            for b in data.get('beliefs', []):
                level_str = b.get('level', 'empirical')
                level_map = {
                    'theoretical': EpistemicLevel.THEORETICAL,
                    'intermediate': EpistemicLevel.INTERMEDIATE,
                    'empirical': EpistemicLevel.EMPIRICAL,
                    'observational': EpistemicLevel.OBSERVATIONAL,
                }

                scope = None
                if b.get('scope'):
                    scope = ScopeConditions(
                        population=b['scope'].get('population'),
                        setting=b['scope'].get('setting'),
                        scope_specified=b['scope'].get('scope_specified', False)
                    )

                beliefs.append(Belief(
                    belief_id=b.get('belief_id', f"{case_id}_b{len(beliefs)}"),
                    content=b.get('content', ''),
                    level=level_map.get(level_str, EpistemicLevel.EMPIRICAL),
                    credence=Credence(
                        value=b.get('credence', 0.5),
                        uncertainty=b.get('uncertainty', 0.2)
                    ),
                    scope=scope,
                ))

            # Convert constraints
            constraints = []
            for c in data.get('constraints', []):
                causal_str = c.get('causal_direction', 'unknown')
                try:
                    causal_direction = CausalDirection(causal_str)
                except ValueError:
                    causal_direction = CausalDirection.UNKNOWN

                type_str = c.get('constraint_type', 'supports')
                type_map = {
                    'supports': ConstraintType.SUPPORTS,
                    'contradicts': ConstraintType.CONTRADICTS,
                    'explains': ConstraintType.EXPLAINS,
                }

                constraints.append(Constraint(
                    constraint_id=c.get('constraint_id', f"{case_id}_c{len(constraints)}"),
                    source_id=c.get('source_id', ''),
                    target_id=c.get('target_id', ''),
                    constraint_type=type_map.get(type_str, ConstraintType.SUPPORTS),
                    strength=c.get('strength', 0.5),
                    causal_direction=causal_direction,
                ))

            # Metadata
            meta = data.get('metadata', {})

            # Extract raw credence values to bypass Credence auto-clamping
            raw_credences = []
            for b in data.get('beliefs', []):
                raw_c = b.get('credence')
                if raw_c is not None:
                    raw_credences.append(raw_c)

            metadata = {
                'sample_size': meta.get('sample_size'),
                'study_design': meta.get('study_design'),
                'sample_description': meta.get('sample_description', ''),
                'effect_size': meta.get('effect_size'),
                'p_value': meta.get('p_value'),
                'confidence_interval': meta.get('confidence_interval'),
                'n_comparisons': meta.get('n_comparisons'),
                'n_significant': meta.get('n_significant'),
                'correction_applied': meta.get('correction_applied'),
                'raw_credences': raw_credences,  # For detecting 0/1 before clamping
                'subgroup_sizes': meta.get('subgroup_sizes', {}),  # For subgroup N check
            }

            test_cases.append(TestCase(
                case_id=case_id,
                category="failure_standard",
                expected_outcome=expected_outcome,
                beliefs=beliefs,
                constraints=constraints,
                metadata=metadata,
            ))

            logger.info(f"Loaded Failure Standard: {case_id} (expected: {expected_outcome})")

        except Exception as e:
            logger.error(f"Error loading {yaml_file}: {e}")

    return test_cases


# =============================================================================
# CALIBRATION RUNNER
# =============================================================================

@dataclass
class CalibrationRun:
    """Results of a calibration run."""
    timestamp: datetime
    n_gold_standard: int
    n_failure_standard: int

    # Performance metrics
    gold_standard_pass_rate: float  # Should be high (clean papers pass)
    failure_obvious_detection_rate: float  # Should be 100%
    failure_subtle_detection_rate: float  # Target: 80%

    # Detailed results
    gold_standard_results: List[Tuple[str, str, int]]  # (case_id, outcome, n_flags)
    failure_standard_results: List[Tuple[str, str, str, int]]  # (case_id, expected, actual, n_flags)

    # Calibrated thresholds
    calibration_results: Dict[str, CalibrationResult]

    # False positive / negative analysis
    false_positives: List[str]  # Gold Standard cases that were flagged
    false_negatives: List[str]  # Failure Standard cases that weren't flagged


def run_calibration(
    gold_standard_cases: List[TestCase],
    failure_standard_cases: List[TestCase]
) -> CalibrationRun:
    """Run calibration against both corpora."""
    tester = CredibilityTester()

    gold_results = []
    failure_results = []
    all_reports_with_labels = []
    false_positives = []
    false_negatives = []

    # Run against Gold Standard (should pass)
    logger.info("\n=== Running Gold Standard Cases ===")
    for case in gold_standard_cases:
        report = tester.evaluate(
            article_id=case.case_id,
            beliefs=case.beliefs,
            constraints=case.constraints,
            metadata=case.metadata
        )

        outcome = "accept" if report.is_clean else report.overall_decision.value
        gold_results.append((case.case_id, outcome, len(report.flags)))

        # Gold Standard should pass - if flagged, it's a false positive
        is_problem = False  # Gold Standard papers are NOT problems
        all_reports_with_labels.append((report, is_problem))

        if not report.is_clean:
            false_positives.append(case.case_id)
            logger.warning(f"  FALSE POSITIVE: {case.case_id} flagged with {len(report.flags)} flags")
        else:
            logger.info(f"  PASS: {case.case_id}")

    # Run against Failure Standard (should flag)
    logger.info("\n=== Running Failure Standard Cases ===")
    obvious_detected = 0
    obvious_total = 0
    subtle_detected = 0
    subtle_total = 0

    for case in failure_standard_cases:
        report = tester.evaluate(
            article_id=case.case_id,
            beliefs=case.beliefs,
            constraints=case.constraints,
            metadata=case.metadata
        )

        outcome = "accept" if report.is_clean else report.overall_decision.value
        failure_results.append((case.case_id, case.expected_outcome, outcome, len(report.flags)))

        # Failure Standard cases ARE problems
        is_problem = True
        all_reports_with_labels.append((report, is_problem))

        # Check detection
        if "obvious" in case.case_id or case.expected_outcome == "block":
            obvious_total += 1
            if not report.is_clean:
                obvious_detected += 1
                logger.info(f"  DETECTED (obvious): {case.case_id} - {outcome}")
            else:
                false_negatives.append(case.case_id)
                logger.error(f"  MISSED (obvious): {case.case_id}")
        else:
            # Handle borderline cases separately
            if case.expected_outcome == "borderline":
                # Borderline: both accept and review are acceptable
                if report.is_clean:
                    logger.info(f"  BORDERLINE (accept ok): {case.case_id} - accept")
                else:
                    logger.info(f"  BORDERLINE (flagged ok): {case.case_id} - {outcome}")
                # Don't count borderlines in subtle metrics
            else:
                subtle_total += 1
                if not report.is_clean:
                    subtle_detected += 1
                    logger.info(f"  DETECTED (subtle): {case.case_id} - {outcome}")
                else:
                    false_negatives.append(case.case_id)
                    logger.warning(f"  MISSED (subtle): {case.case_id}")

    # Compute metrics
    gold_pass_rate = sum(1 for r in gold_results if r[1] == "accept") / len(gold_results) if gold_results else 0
    obvious_rate = obvious_detected / obvious_total if obvious_total > 0 else 0
    subtle_rate = subtle_detected / subtle_total if subtle_total > 0 else 0

    # Run threshold calibration
    calibration_results = calibrate_thresholds(all_reports_with_labels, target_sensitivity=0.8)

    return CalibrationRun(
        timestamp=datetime.now(timezone.utc),
        n_gold_standard=len(gold_standard_cases),
        n_failure_standard=len(failure_standard_cases),
        gold_standard_pass_rate=gold_pass_rate,
        failure_obvious_detection_rate=obvious_rate,
        failure_subtle_detection_rate=subtle_rate,
        gold_standard_results=gold_results,
        failure_standard_results=failure_results,
        calibration_results=calibration_results,
        false_positives=false_positives,
        false_negatives=false_negatives,
    )


# =============================================================================
# REPORT GENERATION
# =============================================================================

def generate_report(run: CalibrationRun, output_path: Path) -> None:
    """Generate calibration report in markdown format."""
    report_lines = [
        "# Credibility Testing Calibration Report",
        "",
        f"**Date:** {run.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}",
        f"**Sprint:** D (TODO 1 Calibration)",
        "",
        "---",
        "",
        "## Executive Summary",
        "",
        f"| Metric | Value | Target |",
        f"|--------|-------|--------|",
        f"| Gold Standard Pass Rate | {run.gold_standard_pass_rate:.0%} | ≥90% |",
        f"| Obvious Failure Detection | {run.failure_obvious_detection_rate:.0%} | 100% |",
        f"| Subtle Failure Detection | {run.failure_subtle_detection_rate:.0%} | ≥80% |",
        f"| False Positives | {len(run.false_positives)} | 0 |",
        f"| False Negatives | {len(run.false_negatives)} | 0 |",
        "",
        "---",
        "",
        "## Corpus Statistics",
        "",
        f"- **Gold Standard cases:** {run.n_gold_standard}",
        f"- **Failure Standard cases:** {run.n_failure_standard}",
        f"- **Total test cases:** {run.n_gold_standard + run.n_failure_standard}",
        "",
        "---",
        "",
        "## Gold Standard Results (Expected: PASS)",
        "",
        "| Case ID | Outcome | Flags |",
        "|---------|---------|-------|",
    ]

    for case_id, outcome, n_flags in run.gold_standard_results:
        status = "✓" if outcome == "accept" else "✗"
        report_lines.append(f"| {case_id} | {status} {outcome} | {n_flags} |")

    report_lines.extend([
        "",
        "---",
        "",
        "## Failure Standard Results (Expected: FLAG)",
        "",
        "| Case ID | Expected | Actual | Flags | Status |",
        "|---------|----------|--------|-------|--------|",
    ])

    for case_id, expected, actual, n_flags in run.failure_standard_results:
        if expected == "borderline":
            # Borderline cases: both accept and flagged are OK
            status = "○ Borderline (ok)"
        elif actual != "accept" and expected in ["block", "review"]:
            status = "✓ Detected"
        elif actual == "accept":
            status = "✗ Missed"
        else:
            status = "✓ Detected"
        report_lines.append(f"| {case_id} | {expected} | {actual} | {n_flags} | {status} |")

    report_lines.extend([
        "",
        "---",
        "",
        "## Calibrated Thresholds",
        "",
        "Per Simon: Explicit threshold documentation with rationale.",
        "",
        "| Check Type | Threshold | Sensitivity | Specificity | N Samples |",
        "|------------|-----------|-------------|-------------|-----------|",
    ])

    for check_name, result in run.calibration_results.items():
        report_lines.append(
            f"| {check_name} | {result.optimal_threshold:.2f} | "
            f"{result.sensitivity:.0%} | {result.specificity:.0%} | {result.n_samples} |"
        )

    if run.false_positives:
        report_lines.extend([
            "",
            "---",
            "",
            "## False Positives (Gold Standard flagged incorrectly)",
            "",
        ])
        for fp in run.false_positives:
            report_lines.append(f"- {fp}")

    if run.false_negatives:
        report_lines.extend([
            "",
            "---",
            "",
            "## False Negatives (Failure Standard not detected)",
            "",
        ])
        for fn in run.false_negatives:
            report_lines.append(f"- {fn}")

    report_lines.extend([
        "",
        "---",
        "",
        "## Recommendations",
        "",
        "Based on calibration results:",
        "",
    ])

    if run.gold_standard_pass_rate < 0.9:
        report_lines.append("1. **Reduce false positives**: Gold Standard pass rate below 90%. Consider relaxing thresholds.")
    else:
        report_lines.append("1. **Gold Standard pass rate acceptable**: ≥90% of known-good papers pass.")

    if run.failure_obvious_detection_rate < 1.0:
        report_lines.append("2. **CRITICAL: Obvious failures missed**: All obvious failures must be detected.")
    else:
        report_lines.append("2. **Obvious failure detection complete**: 100% of obvious failures detected.")

    if run.failure_subtle_detection_rate < 0.8:
        report_lines.append(f"3. **Improve subtle detection**: Currently {run.failure_subtle_detection_rate:.0%}, target is 80%.")
    else:
        report_lines.append(f"3. **Subtle failure detection acceptable**: {run.failure_subtle_detection_rate:.0%} ≥ 80% target.")

    report_lines.extend([
        "",
        "---",
        "",
        "*Report generated by calibrate_credibility.py*",
    ])

    # Write report
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        f.write('\n'.join(report_lines))

    logger.info(f"\nReport written to: {output_path}")


# =============================================================================
# MAIN
# =============================================================================

def main():
    """Run calibration and generate report."""
    logger.info("=" * 60)
    logger.info("Credibility Testing Calibration")
    logger.info("Sprint D: TODO 1")
    logger.info("=" * 60)

    # Paths
    gs_path = PROJECT_ROOT / "gold_standard"
    fs_path = gs_path / "failure_standard"

    # Load corpora
    logger.info("\nLoading test corpora...")
    gold_standard_cases = load_gold_standard(gs_path)
    failure_standard_cases = load_failure_standard(fs_path)

    if not gold_standard_cases and not failure_standard_cases:
        logger.error("No test cases found!")
        return 1

    # Run calibration
    logger.info(f"\nRunning calibration with {len(gold_standard_cases)} gold + {len(failure_standard_cases)} failure cases...")
    run = run_calibration(gold_standard_cases, failure_standard_cases)

    # Generate report
    date_str = datetime.now().strftime("%Y_%m_%d")
    report_path = PROJECT_ROOT / "docs" / "calibration" / f"CREDIBILITY_CALIBRATION_REPORT_{date_str}.md"
    generate_report(run, report_path)

    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("CALIBRATION SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Gold Standard Pass Rate: {run.gold_standard_pass_rate:.0%}")
    logger.info(f"Obvious Failure Detection: {run.failure_obvious_detection_rate:.0%}")
    logger.info(f"Subtle Failure Detection: {run.failure_subtle_detection_rate:.0%}")
    logger.info(f"False Positives: {len(run.false_positives)}")
    logger.info(f"False Negatives: {len(run.false_negatives)}")

    # Return exit code based on critical failures
    if run.failure_obvious_detection_rate < 1.0:
        logger.error("FAIL: Not all obvious failures detected!")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
