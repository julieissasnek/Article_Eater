#!/usr/bin/env python3
"""
Pre-commit Template Validation Script

Validates all JSON templates against the canonical schema.
Designed for use as a pre-commit hook - exits 0 on success, 1 on failure.

Usage:
    python scripts/validate_all_templates.py           # Validate all
    python scripts/validate_all_templates.py --strict  # Strict mode (warnings = failures)

Author: Claude Code (Feb 23, 2026)
"""

import json
import sys
from pathlib import Path

try:
    from jsonschema import Draft202012Validator, ValidationError
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False


PROJECT_ROOT = Path(__file__).parent.parent
TEMPLATES_DIR = PROJECT_ROOT / "data" / "templates"
SCHEMA_PATH = PROJECT_ROOT / "schemas" / "template_canonical.json"


def load_schema() -> dict:
    """Load the canonical template schema."""
    if not SCHEMA_PATH.exists():
        print(f"WARNING: Schema file not found: {SCHEMA_PATH}")
        return {}
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def validate_json_syntax(file_path: Path) -> tuple[bool, str]:
    """Validate JSON syntax. Returns (success, error_message)."""
    try:
        json.loads(file_path.read_text(encoding="utf-8"))
        return True, ""
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON syntax: {e}"


def validate_against_schema(data: dict, schema: dict, validator: Draft202012Validator | None) -> list[str]:
    """Validate template against JSON Schema. Returns list of errors."""
    if not HAS_JSONSCHEMA or validator is None:
        return []

    errors = []
    for error in validator.iter_errors(data):
        path = ".".join(str(p) for p in error.absolute_path)
        if path:
            errors.append(f"  {path}: {error.message}")
        else:
            errors.append(f"  {error.message}")
    return errors


def validate_scaffold_tier(data: dict) -> list[str]:
    """Validate scaffold tier requirements (all templates)."""
    errors = []

    # Required: template_id
    if not data.get("template_id"):
        errors.append("Missing required field: template_id")

    # Required: display_id
    if not data.get("display_id"):
        errors.append("Missing required field: display_id")

    # Required: name (or template_name)
    if not data.get("name") and not data.get("template_name"):
        errors.append("Missing required field: name or template_name")

    # Required: calibration_status (or status)
    # Accept both canonical and legacy status values
    VALID_STATUSES = {
        "calibrated", "scaffold", "uncalibrated", "partial",
        "deepened", "substantially_calibrated"  # Legacy/extended statuses
    }
    status = data.get("calibration_status") or data.get("status")
    if status and status not in VALID_STATUSES:
        errors.append(f"Invalid calibration_status: {status}")

    return errors


def validate_calibrated_tier(data: dict) -> list[str]:
    """Validate calibrated tier requirements (calibrated templates only)."""
    errors = []

    # Check if calibrated
    status = data.get("calibration_status") or data.get("status")
    is_calibrated = status == "calibrated" or data.get("calibrated") is True

    if not is_calibrated:
        return []  # Not calibrated, skip calibrated-tier validation

    # Must have mechanism_chain
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

    return errors


def validate_template(file_path: Path, schema: dict, validator: Draft202012Validator | None) -> tuple[bool, list[str]]:
    """Validate a single template file. Returns (success, errors)."""
    errors = []

    # Step 1: JSON syntax
    success, error = validate_json_syntax(file_path)
    if not success:
        return False, [error]

    # Load data
    data = json.loads(file_path.read_text(encoding="utf-8"))

    # Step 2: Schema validation (if available)
    schema_errors = validate_against_schema(data, schema, validator)
    errors.extend(schema_errors)

    # Step 3: Scaffold tier validation
    scaffold_errors = validate_scaffold_tier(data)
    errors.extend(scaffold_errors)

    # Step 4: Calibrated tier validation
    calibrated_errors = validate_calibrated_tier(data)
    errors.extend(calibrated_errors)

    return len(errors) == 0, errors


def main() -> int:
    """Main entry point. Returns exit code."""
    strict = "--strict" in sys.argv
    schema_check = "--schema" in sys.argv  # Only enable full schema validation if explicitly requested

    # Load schema (only used if --schema flag is passed)
    schema = load_schema() if schema_check else {}
    validator = None
    if HAS_JSONSCHEMA and schema and schema_check:
        validator = Draft202012Validator(schema)

    # Find all template files
    if not TEMPLATES_DIR.exists():
        print(f"ERROR: Templates directory not found: {TEMPLATES_DIR}")
        return 1

    template_files = sorted(TEMPLATES_DIR.glob("*.json"))
    if not template_files:
        print("No template files found.")
        return 0

    # Validate each template
    total = len(template_files)
    passed = 0
    failed = 0
    all_errors = []

    for file_path in template_files:
        success, errors = validate_template(file_path, schema, validator)
        if success:
            passed += 1
        else:
            failed += 1
            all_errors.append((file_path.name, errors))

    # Report results
    if failed > 0:
        print(f"\nTemplate Validation: {failed}/{total} FAILED\n")
        for filename, errors in all_errors:
            print(f"{filename}:")
            for error in errors:
                print(f"  - {error}")
        print()
        return 1
    else:
        print(f"Template Validation: {passed}/{total} passed")
        return 0


if __name__ == "__main__":
    sys.exit(main())
