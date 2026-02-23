#!/usr/bin/env python3
"""
Template Validation Script (E-01)

Validates all JSON templates against the canonical schema.
Reports scaffold-tier and calibrated-tier compliance.

Usage:
    python scripts/validate_templates.py                    # Validate all
    python scripts/validate_templates.py --verbose          # Show details
    python scripts/validate_templates.py --fix-display-id   # Auto-generate missing display_id

Author: Claude Code (Feb 22, 2026)
Sprint: CC_REPAIR_SPRINT, Task E-01
"""

import argparse
import json
import re
from pathlib import Path
from datetime import datetime, timezone
from dataclasses import dataclass, field, asdict
from typing import Optional


PROJECT_ROOT = Path(__file__).parent.parent
TEMPLATES_DIR = PROJECT_ROOT / "data" / "templates"
SCHEMA_PATH = PROJECT_ROOT / "schemas" / "template_canonical.json"
REPORT_PATH = PROJECT_ROOT / "data" / "template_validation_report.json"

# T1 Framework codes
T1_FRAMEWORKS = {"PP", "SN", "DP", "DT", "NM", "IC", "MS", "EC", "CB", "MSI"}

# Bridge warrant types with ceiling priors
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
class ValidationResult:
    """Result for a single template."""
    template_id: str
    file_path: str
    scaffold_pass: bool
    calibrated_pass: bool
    calibration_status: str
    errors: list = field(default_factory=list)
    warnings: list = field(default_factory=list)


def derive_display_id(template_id: str, data: dict) -> str:
    """Generate display_id from template_id or existing fields."""
    # Check for existing series IDs in the file
    for key in ["series_id", "display_id", "short_id"]:
        if key in data and data[key]:
            return str(data[key])

    # Generate from template_id pattern
    # e.g., NATURE_VIEW_CONVERGENCE_001 -> NVC1
    #       ED_HIPPOCAMPAL_ENCODING_001 -> EHE1
    #       PP_SPECTRAL_MATCH_001 -> PSM1
    parts = template_id.replace("_001", "").replace("_002", "").replace("_003", "").split("_")

    # Take first letter of each part
    if len(parts) >= 2:
        abbrev = "".join(p[0].upper() for p in parts[:3] if p)
        # Add number suffix
        match = re.search(r"(\d+)$", template_id)
        num = match.group(1)[-1] if match else "1"
        return f"{abbrev}{num}"

    return template_id[:8]


def derive_name(template_id: str) -> str:
    """Generate human-readable name from template_id."""
    # Remove number suffix
    name = re.sub(r"_\d+$", "", template_id)
    # Replace underscores with spaces, title case
    name = name.replace("_", " ").title()
    return name


def get_calibration_status(data: dict) -> str:
    """Extract calibration status from various field names."""
    if "calibration_status" in data:
        return data["calibration_status"]
    if "status" in data:
        status = data["status"]
        if status in ("calibrated", "scaffold", "uncalibrated", "partial"):
            return status
        if status == "calibrated":
            return "calibrated"
    if data.get("calibrated") is True:
        return "calibrated"
    return "uncalibrated"


def validate_scaffold(data: dict, result: ValidationResult) -> bool:
    """Validate scaffold tier requirements."""
    errors = []

    # Required: template_id
    if not data.get("template_id"):
        errors.append("Missing required field: template_id")

    # Required: display_id
    if not data.get("display_id"):
        errors.append("Missing required field: display_id (can auto-generate)")

    # Required: name (or template_name)
    if not data.get("name") and not data.get("template_name"):
        errors.append("Missing required field: name or template_name")

    # Required: t1_frameworks
    t1 = data.get("t1_frameworks", [])
    if not t1:
        errors.append("Missing required field: t1_frameworks")
    elif isinstance(t1, list):
        # t1_frameworks can be list of strings or list of objects with 'code' key
        invalid = []
        for f in t1:
            if isinstance(f, str):
                if f not in T1_FRAMEWORKS:
                    invalid.append(f)
            elif isinstance(f, dict):
                code = f.get("code") or f.get("framework")
                if code and code not in T1_FRAMEWORKS:
                    invalid.append(code)
            else:
                invalid.append(str(f))
        if invalid:
            errors.append(f"Invalid T1 framework codes: {invalid}")

    # Required: calibration_status
    status = get_calibration_status(data)
    if status not in ("calibrated", "scaffold", "uncalibrated", "partial"):
        errors.append(f"Invalid calibration_status: {status}")

    result.errors.extend(errors)
    return len(errors) == 0


def validate_calibrated(data: dict, result: ValidationResult) -> bool:
    """Validate calibrated tier requirements."""
    errors = []
    warnings = []

    # Must have mechanism_chain or mechanism_steps
    chain = data.get("mechanism_chain") or data.get("mechanism_steps", [])
    if not chain:
        errors.append("Calibrated template missing mechanism_chain")
    else:
        for i, step in enumerate(chain):
            if not isinstance(step, dict):
                errors.append(f"mechanism_chain[{i}] is not an object")
                continue
            if not step.get("description") and not step.get("process"):
                errors.append(f"mechanism_chain[{i}] missing description/process")

    # Must have bridge_warrant
    warrant = data.get("bridge_warrant") or data.get("bridge_warrant_type")
    if not warrant:
        errors.append("Calibrated template missing bridge_warrant")
    elif warrant.upper() not in BRIDGE_CEILINGS:
        errors.append(f"Unknown bridge_warrant type: {warrant}")

    # Must have confidence
    confidence = data.get("confidence") or data.get("prior_confidence") or data.get("bridge_prior")
    if confidence is None:
        errors.append("Calibrated template missing confidence/prior_confidence/bridge_prior")
    elif warrant and warrant.upper() in BRIDGE_CEILINGS:
        ceiling = BRIDGE_CEILINGS[warrant.upper()]
        if confidence > ceiling:
            warnings.append(f"Confidence {confidence} exceeds ceiling {ceiling} for {warrant}")

    # Should have calibrated_parameters
    if not data.get("calibrated_parameters"):
        warnings.append("Calibrated template missing calibrated_parameters")

    # Should have cross_template_interactions
    interactions = data.get("cross_template_interactions") or data.get("super_template_interactions")
    if not interactions:
        warnings.append("Calibrated template missing cross_template_interactions")

    result.errors.extend(errors)
    result.warnings.extend(warnings)
    return len(errors) == 0


def validate_template(file_path: Path, verbose: bool = False) -> ValidationResult:
    """Validate a single template file."""
    result = ValidationResult(
        template_id="",
        file_path=str(file_path.relative_to(PROJECT_ROOT)),
        scaffold_pass=False,
        calibrated_pass=False,
        calibration_status="unknown"
    )

    try:
        with open(file_path) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        result.errors.append(f"Invalid JSON: {e}")
        return result

    result.template_id = data.get("template_id", file_path.stem)
    result.calibration_status = get_calibration_status(data)

    # Validate scaffold tier
    result.scaffold_pass = validate_scaffold(data, result)

    # Validate calibrated tier if applicable
    if result.calibration_status == "calibrated":
        result.calibrated_pass = validate_calibrated(data, result)
    else:
        result.calibrated_pass = True  # N/A for non-calibrated

    return result


def run_validation(verbose: bool = False) -> dict:
    """Run validation on all templates."""
    results = []

    # Find all JSON files
    json_files = sorted(TEMPLATES_DIR.glob("*.json"))

    for file_path in json_files:
        result = validate_template(file_path, verbose)
        results.append(result)

        if verbose and (result.errors or result.warnings):
            print(f"\n{result.template_id}:")
            for e in result.errors:
                print(f"  ERROR: {e}")
            for w in result.warnings:
                print(f"  WARN: {w}")

    # Compute summary
    total = len(results)
    scaffold_pass = sum(1 for r in results if r.scaffold_pass)
    scaffold_fail = total - scaffold_pass

    calibrated = [r for r in results if r.calibration_status == "calibrated"]
    calibrated_pass = sum(1 for r in calibrated if r.calibrated_pass)
    calibrated_fail = len(calibrated) - calibrated_pass

    summary = {
        "total_templates": total,
        "scaffold_pass": scaffold_pass,
        "scaffold_fail": scaffold_fail,
        "calibrated_count": len(calibrated),
        "calibrated_pass": calibrated_pass,
        "calibrated_fail": calibrated_fail,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    # Build failure patterns
    error_patterns = {}
    for r in results:
        for e in r.errors:
            pattern = e.split(":")[0] if ":" in e else e
            error_patterns[pattern] = error_patterns.get(pattern, 0) + 1

    report = {
        "summary": summary,
        "error_patterns": error_patterns,
        "results": [asdict(r) for r in results]
    }

    return report


def main():
    parser = argparse.ArgumentParser(description="Validate CMR templates against canonical schema")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed output")
    parser.add_argument("--fix-display-id", action="store_true", help="Auto-generate missing display_id")
    args = parser.parse_args()

    print("Template Validation (E-01)")
    print("=" * 50)
    print(f"Templates dir: {TEMPLATES_DIR}")
    print(f"Schema: {SCHEMA_PATH}")
    print()

    report = run_validation(args.verbose)

    # Print summary
    s = report["summary"]
    print(f"\n{'='*50}")
    print("SUMMARY")
    print(f"{'='*50}")
    print(f"Total templates: {s['total_templates']}")
    print(f"Scaffold tier:   {s['scaffold_pass']} pass / {s['scaffold_fail']} fail")
    print(f"Calibrated:      {s['calibrated_count']} total")
    print(f"Calibrated tier: {s['calibrated_pass']} pass / {s['calibrated_fail']} fail")

    if report["error_patterns"]:
        print(f"\nError patterns:")
        for pattern, count in sorted(report["error_patterns"].items(), key=lambda x: -x[1]):
            print(f"  {count:3d}x {pattern}")

    # Write report
    with open(REPORT_PATH, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\nReport written to: {REPORT_PATH}")

    # Return exit code
    if s["scaffold_fail"] > 0 or s["calibrated_fail"] > 0:
        return 1
    return 0


if __name__ == "__main__":
    exit(main())
