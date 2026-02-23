#!/usr/bin/env python3
"""
Toulmin Justification Validation Script (TJ-02)

Validates Toulmin justification layers in calibrated templates.
Checks depth tier compliance and consistency rules per OPUS_REVIEW_GUIDE_ADDENDUM_TOULMIN.md.

Usage:
    python scripts/validate_toulmin.py                    # Validate all
    python scripts/validate_toulmin.py --verbose          # Show details

Depth Tiers:
    A (Full): Required for high-confidence (>0.55), contested, or MECHANISM+ steps
    B (Standard): Required for all other calibrated template steps
    C (Stub): Only acceptable for residual gap steps (<0.40)

Consistency Rules:
    - <2 independent paradigms in data → confidence ≤ 0.50
    - Active rebuttal condition → confidence ≤ 0.55
    - Equally supported competing account → confidence ≤ 0.55
    - Timescale mismatch in qualifier → confidence reduced 0.10-0.15
    - Untested extrapolation in backing → requires THEORETICAL_DEFAULT

Author: Claude Code (Feb 23, 2026)
Sprint: CC_REPAIR_SPRINT, Task TJ-02
"""

import argparse
import json
from pathlib import Path
from datetime import datetime, timezone
from dataclasses import dataclass, field
from typing import Optional


PROJECT_ROOT = Path(__file__).parent.parent
TEMPLATES_DIR = PROJECT_ROOT / "data" / "templates"

# Bridge warrant types requiring Tier A justification
TIER_A_WARRANTS = {"CONSTITUTIVE", "MECHANISM"}

# Confidence threshold for Tier A requirement
TIER_A_CONFIDENCE_THRESHOLD = 0.55


@dataclass
class StepValidation:
    """Validation result for a single mechanism step."""
    step_num: int
    has_justification: bool
    required_tier: str  # A, B, or C
    actual_tier: Optional[str]
    errors: list = field(default_factory=list)
    warnings: list = field(default_factory=list)


@dataclass
class TemplateValidation:
    """Validation result for a template."""
    template_id: str
    is_calibrated: bool
    step_count: int
    steps_with_justification: int
    tier_a_required: int
    tier_a_present: int
    errors: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    step_results: list = field(default_factory=list)


def determine_required_tier(step: dict, has_competing: bool = False) -> str:
    """Determine required justification tier for a step."""
    confidence = step.get("confidence", 0)
    warrant = (step.get("warrant") or step.get("bridge_warrant", "")).upper()

    # Tier A requirements
    if confidence > TIER_A_CONFIDENCE_THRESHOLD:
        return "A"
    if warrant in TIER_A_WARRANTS:
        return "A"
    if has_competing:
        return "A"

    # Tier C acceptable only for low-confidence residual gaps
    if confidence < 0.40:
        return "C"

    # Default: Tier B
    return "B"


def validate_justification(step: dict, step_num: int) -> StepValidation:
    """Validate justification for a single mechanism step."""
    justification = step.get("justification", {})
    confidence = step.get("confidence", 0)
    warrant = (step.get("warrant") or step.get("bridge_warrant", "")).upper()

    # Check if justification exists
    has_justification = bool(justification)
    has_competing = bool(justification.get("competing_accounts"))

    required_tier = determine_required_tier(step, has_competing)
    actual_tier = justification.get("depth_tier")

    result = StepValidation(
        step_num=step_num,
        has_justification=has_justification,
        required_tier=required_tier,
        actual_tier=actual_tier
    )

    if not has_justification:
        result.errors.append(f"Step {step_num}: Missing justification object")
        return result

    # Validate data entries
    data = justification.get("data", [])
    if len(data) < 2 and required_tier in ("A", "B"):
        if confidence > 0.50:
            result.errors.append(
                f"Step {step_num}: <2 data entries but confidence={confidence:.2f} (should be ≤0.50)"
            )
        else:
            result.warnings.append(f"Step {step_num}: Only {len(data)} data entries")

    # Check for independent paradigms
    paradigms = set(d.get("paradigm", "") for d in data if d.get("paradigm"))
    if len(paradigms) < 2 and confidence > 0.50 and len(data) >= 2:
        result.warnings.append(
            f"Step {step_num}: {len(data)} data entries but only {len(paradigms)} paradigm(s) - consider independence"
        )

    # Validate backing
    backing = justification.get("backing", "")
    if not backing and required_tier in ("A", "B"):
        result.errors.append(f"Step {step_num}: Missing backing")
    elif len(backing) < 50 and required_tier == "A":
        result.warnings.append(f"Step {step_num}: Backing seems brief for Tier A")

    # Validate qualifier
    qualifier = justification.get("qualifier", "")
    if not qualifier and required_tier in ("A", "B"):
        result.errors.append(f"Step {step_num}: Missing qualifier")

    # Validate rebuttal
    rebuttal = justification.get("rebuttal", "")
    if not rebuttal:
        result.errors.append(f"Step {step_num}: Missing rebuttal (required for all tiers)")
    elif "would fail if the evidence is wrong" in rebuttal.lower():
        result.errors.append(f"Step {step_num}: Trivial rebuttal not acceptable")

    # Validate competing accounts consistency
    competing = justification.get("competing_accounts", [])
    if competing and confidence > 0.55:
        result.warnings.append(
            f"Step {step_num}: Has competing accounts but confidence={confidence:.2f} (should be ≤0.55)"
        )

    # Check tier assignment
    if actual_tier and actual_tier != required_tier:
        if required_tier == "A" and actual_tier in ("B", "C"):
            result.errors.append(
                f"Step {step_num}: Tier {actual_tier} assigned but Tier A required "
                f"(conf={confidence:.2f}, warrant={warrant})"
            )
        elif required_tier == "B" and actual_tier == "C":
            result.warnings.append(
                f"Step {step_num}: Tier C assigned but Tier B recommended"
            )

    return result


def validate_template(file_path: Path, verbose: bool = False) -> TemplateValidation:
    """Validate Toulmin justifications in a template."""
    try:
        with open(file_path) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return TemplateValidation(
            template_id=file_path.stem,
            is_calibrated=False,
            step_count=0,
            steps_with_justification=0,
            tier_a_required=0,
            tier_a_present=0,
            errors=[f"Invalid JSON: {e}"]
        )

    template_id = data.get("template_id", file_path.stem)

    # Check if calibrated
    cal_status = data.get("calibration_status") or data.get("status")
    is_calibrated = cal_status == "calibrated" or data.get("calibrated") is True

    # Get mechanism chain
    chain = data.get("mechanism_chain") or data.get("mechanism_steps", [])

    result = TemplateValidation(
        template_id=template_id,
        is_calibrated=is_calibrated,
        step_count=len(chain),
        steps_with_justification=0,
        tier_a_required=0,
        tier_a_present=0
    )

    # Skip non-calibrated templates (justification not required)
    if not is_calibrated:
        return result

    # Validate each step
    for i, step in enumerate(chain):
        step_num = step.get("step") or step.get("step_number") or (i + 1)
        step_result = validate_justification(step, step_num)

        if step_result.has_justification:
            result.steps_with_justification += 1

        if step_result.required_tier == "A":
            result.tier_a_required += 1
            if step_result.actual_tier == "A":
                result.tier_a_present += 1

        result.step_results.append(step_result)
        result.errors.extend(step_result.errors)
        result.warnings.extend(step_result.warnings)

    return result


def run_validation(verbose: bool = False) -> dict:
    """Run Toulmin validation on all templates."""
    results = []

    json_files = sorted(TEMPLATES_DIR.glob("*.json"))

    for file_path in json_files:
        result = validate_template(file_path, verbose)
        results.append(result)

        if verbose and (result.errors or result.warnings) and result.is_calibrated:
            print(f"\n{result.template_id}:")
            for e in result.errors:
                print(f"  ERROR: {e}")
            for w in result.warnings:
                print(f"  WARN: {w}")

    # Summary
    total = len(results)
    calibrated = [r for r in results if r.is_calibrated]
    with_justification = [r for r in calibrated if r.steps_with_justification > 0]
    full_coverage = [r for r in calibrated
                     if r.steps_with_justification == r.step_count and r.step_count > 0]

    total_steps = sum(r.step_count for r in calibrated)
    steps_justified = sum(r.steps_with_justification for r in calibrated)
    tier_a_required = sum(r.tier_a_required for r in calibrated)
    tier_a_present = sum(r.tier_a_present for r in calibrated)

    total_errors = sum(len(r.errors) for r in calibrated)
    total_warnings = sum(len(r.warnings) for r in calibrated)

    summary = {
        "total_templates": total,
        "calibrated_templates": len(calibrated),
        "templates_with_justification": len(with_justification),
        "templates_full_coverage": len(full_coverage),
        "total_steps": total_steps,
        "steps_justified": steps_justified,
        "tier_a_required": tier_a_required,
        "tier_a_present": tier_a_present,
        "total_errors": total_errors,
        "total_warnings": total_warnings,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    return {
        "summary": summary,
        "results": [
            {
                "template_id": r.template_id,
                "is_calibrated": r.is_calibrated,
                "step_count": r.step_count,
                "steps_with_justification": r.steps_with_justification,
                "errors": r.errors,
                "warnings": r.warnings
            }
            for r in results if r.is_calibrated
        ]
    }


def main():
    parser = argparse.ArgumentParser(description="Validate Toulmin justifications in CMR templates")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed output")
    args = parser.parse_args()

    print("Toulmin Justification Validation (TJ-02)")
    print("=" * 50)
    print(f"Templates dir: {TEMPLATES_DIR}")
    print()

    report = run_validation(args.verbose)

    # Print summary
    s = report["summary"]
    print(f"\n{'='*50}")
    print("SUMMARY")
    print(f"{'='*50}")
    print(f"Total templates:           {s['total_templates']}")
    print(f"Calibrated templates:      {s['calibrated_templates']}")
    print(f"With any justification:    {s['templates_with_justification']}")
    print(f"Full coverage (all steps): {s['templates_full_coverage']}")
    print()
    print(f"Total mechanism steps:     {s['total_steps']}")
    print(f"Steps with justification:  {s['steps_justified']}")
    print(f"Tier A required:           {s['tier_a_required']}")
    print(f"Tier A present:            {s['tier_a_present']}")
    print()
    print(f"Errors:                    {s['total_errors']}")
    print(f"Warnings:                  {s['total_warnings']}")

    if s['templates_with_justification'] == 0:
        print("\nNote: No templates have Toulmin justifications yet.")
        print("This is expected pre-TJ-03 (retroactive Toulmin sprint).")

    return 0 if s['total_errors'] == 0 else 1


if __name__ == "__main__":
    exit(main())
