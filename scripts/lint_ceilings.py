#!/usr/bin/env python3
"""
Bridge Warrant Ceiling Lint Script (E-02)

Verifies that all calibrated templates respect bridge warrant ceiling priors.
Reports violations where confidence exceeds the ceiling for the warrant type.

Usage:
    python scripts/lint_ceilings.py              # Check all
    python scripts/lint_ceilings.py --verbose    # Show details
    python scripts/lint_ceilings.py --fix        # Cap violations to ceiling

Ceiling priors per OPUS_REVIEW_GUIDE.md:
    CONSTITUTIVE: 0.75
    MECHANISM: 0.60
    EMPIRICAL_COVARIANCE: 0.60
    FUNCTIONAL: 0.50
    CAPACITY: 0.45
    THEORETICAL_DEFAULT: 0.40
    ANALOGICAL: 0.35

Author: Claude Code (Feb 22, 2026)
Sprint: CC_REPAIR_SPRINT, Task E-02
"""

import argparse
import json
from pathlib import Path
from datetime import datetime, timezone
from dataclasses import dataclass, field


PROJECT_ROOT = Path(__file__).parent.parent
TEMPLATES_DIR = PROJECT_ROOT / "data" / "templates"

# Bridge warrant ceiling priors per OPUS_REVIEW_GUIDE.md
BRIDGE_CEILINGS = {
    "CONSTITUTIVE": 0.75,
    "MECHANISM": 0.60,
    "EMPIRICAL_COVARIANCE": 0.60,
    "FUNCTIONAL": 0.50,
    "CAPACITY": 0.45,
    "THEORETICAL_DEFAULT": 0.40,
    "ANALOGICAL": 0.35,
}


@dataclass
class LintResult:
    """Result for a single template."""
    template_id: str
    file_path: str
    bridge_warrant: str
    confidence: float
    ceiling: float
    violation: bool
    excess: float = 0.0


def get_confidence(data: dict) -> float | None:
    """Extract confidence value from various field names."""
    for key in ["confidence", "prior_confidence", "bridge_prior"]:
        if key in data and data[key] is not None:
            return float(data[key])
    return None


def get_bridge_warrant(data: dict) -> str | None:
    """Extract bridge warrant type from various field names."""
    for key in ["bridge_warrant", "bridge_warrant_type"]:
        if key in data and data[key]:
            return str(data[key]).upper()
    return None


def is_calibrated(data: dict) -> bool:
    """Check if template is calibrated."""
    if data.get("calibration_status") == "calibrated":
        return True
    if data.get("status") == "calibrated":
        return True
    if data.get("calibrated") is True:
        return True
    return False


def lint_template(file_path: Path) -> LintResult | None:
    """Lint a single template for ceiling violations."""
    try:
        with open(file_path) as f:
            data = json.load(f)
    except json.JSONDecodeError:
        return None

    # Only check calibrated templates
    if not is_calibrated(data):
        return None

    template_id = data.get("template_id", file_path.stem)
    confidence = get_confidence(data)
    bridge_warrant = get_bridge_warrant(data)

    # Skip if missing required fields
    if confidence is None or bridge_warrant is None:
        return None

    # Check ceiling
    ceiling = BRIDGE_CEILINGS.get(bridge_warrant)
    if ceiling is None:
        # Unknown warrant type
        return LintResult(
            template_id=template_id,
            file_path=str(file_path.relative_to(PROJECT_ROOT)),
            bridge_warrant=bridge_warrant,
            confidence=confidence,
            ceiling=-1,  # Unknown
            violation=False,
        )

    violation = confidence > ceiling
    excess = confidence - ceiling if violation else 0.0

    return LintResult(
        template_id=template_id,
        file_path=str(file_path.relative_to(PROJECT_ROOT)),
        bridge_warrant=bridge_warrant,
        confidence=confidence,
        ceiling=ceiling,
        violation=violation,
        excess=round(excess, 3),
    )


def fix_template(file_path: Path, ceiling: float) -> bool:
    """Cap confidence to ceiling value."""
    try:
        with open(file_path) as f:
            data = json.load(f)

        # Find and cap the confidence field
        for key in ["confidence", "prior_confidence", "bridge_prior"]:
            if key in data and data[key] is not None:
                if float(data[key]) > ceiling:
                    data[key] = ceiling

        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)

        return True
    except Exception:
        return False


def run_lint(verbose: bool = False, fix: bool = False) -> dict:
    """Run ceiling lint on all templates."""
    results = []
    violations = []
    fixed = []

    json_files = sorted(TEMPLATES_DIR.glob("*.json"))

    for file_path in json_files:
        result = lint_template(file_path)
        if result is None:
            continue

        results.append(result)

        if result.violation:
            violations.append(result)

            if fix:
                if fix_template(file_path, result.ceiling):
                    fixed.append(result)
                    if verbose:
                        print(f"FIXED: {result.template_id}")
                        print(f"  {result.bridge_warrant}: {result.confidence} -> {result.ceiling}")
            elif verbose:
                print(f"VIOLATION: {result.template_id}")
                print(f"  Warrant: {result.bridge_warrant} (ceiling: {result.ceiling})")
                print(f"  Confidence: {result.confidence} (excess: +{result.excess})")

    # Group violations by warrant type
    violations_by_warrant = {}
    for v in violations:
        warrant = v.bridge_warrant
        if warrant not in violations_by_warrant:
            violations_by_warrant[warrant] = []
        violations_by_warrant[warrant].append(v.template_id)

    summary = {
        "total_checked": len(results),
        "violations": len(violations),
        "fixed": len(fixed) if fix else 0,
        "violations_by_warrant": {k: len(v) for k, v in violations_by_warrant.items()},
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    return {
        "summary": summary,
        "violations": [
            {
                "template_id": v.template_id,
                "warrant": v.bridge_warrant,
                "confidence": v.confidence,
                "ceiling": v.ceiling,
                "excess": v.excess
            }
            for v in violations
        ]
    }


def main():
    parser = argparse.ArgumentParser(description="Lint CMR templates for ceiling violations")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed output")
    parser.add_argument("--fix", action="store_true", help="Cap violations to ceiling")
    args = parser.parse_args()

    print("Bridge Warrant Ceiling Lint (E-02)")
    print("=" * 50)
    print(f"Templates dir: {TEMPLATES_DIR}")
    print(f"Mode: {'FIX' if args.fix else 'CHECK'}")
    print()

    print("Ceiling priors:")
    for warrant, ceiling in sorted(BRIDGE_CEILINGS.items(), key=lambda x: -x[1]):
        print(f"  {warrant}: {ceiling}")
    print()

    report = run_lint(args.verbose, args.fix)

    # Print summary
    s = report["summary"]
    print(f"\n{'='*50}")
    print("SUMMARY")
    print(f"{'='*50}")
    print(f"Calibrated templates checked: {s['total_checked']}")
    print(f"Ceiling violations: {s['violations']}")

    if args.fix:
        print(f"Fixed: {s['fixed']}")

    if s['violations_by_warrant']:
        print(f"\nViolations by warrant type:")
        for warrant, count in sorted(s['violations_by_warrant'].items()):
            ceiling = BRIDGE_CEILINGS.get(warrant, "?")
            print(f"  {warrant} (ceiling {ceiling}): {count}")

    if report["violations"] and not args.verbose:
        print(f"\nRun with --verbose to see violation details")

    return 0 if s["violations"] == 0 else 1


if __name__ == "__main__":
    exit(main())
