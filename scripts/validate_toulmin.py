#!/usr/bin/env python3
"""
Validate Toulmin justifications in MULTI-I templates.
Check that each mechanism step has all required justification fields.
"""

import json
from pathlib import Path

TEMPLATES_DIR = Path(__file__).parent.parent / "data" / "templates"

REQUIRED_JUSTIFICATION_FIELDS = [
    "data",
    "backing",
    "qualifier",
    "rebuttal",
    "competing_accounts",
    "depth_tier",
    "panel_debate_reference"
]

VALID_DEPTH_TIERS = ["A", "B", "C"]

def validate_justification(template_id: str, step: int, justification: dict) -> list:
    """Validate a single Toulmin justification object. Return list of errors."""
    errors = []

    # Check all required fields
    for field in REQUIRED_JUSTIFICATION_FIELDS:
        if field not in justification:
            errors.append(f"  {template_id} Step {step}: Missing field '{field}'")
        else:
            value = justification[field]
            # Check field types
            if field == "data":
                if not isinstance(value, list) or len(value) == 0:
                    errors.append(f"  {template_id} Step {step}: '{field}' must be non-empty list")
            elif field in ["backing", "qualifier", "rebuttal", "panel_debate_reference"]:
                if not isinstance(value, str) or len(value) < 10:
                    errors.append(f"  {template_id} Step {step}: '{field}' must be non-empty string (>10 chars)")
            elif field == "competing_accounts":
                if not isinstance(value, list) or len(value) == 0:
                    errors.append(f"  {template_id} Step {step}: '{field}' must be non-empty list")
            elif field == "depth_tier":
                if value not in VALID_DEPTH_TIERS:
                    errors.append(f"  {template_id} Step {step}: '{field}' must be one of {VALID_DEPTH_TIERS}, got '{value}'")

    return errors

def validate_template(template_path: Path) -> tuple:
    """Validate all justifications in a template. Return (errors, step_count)."""
    errors = []
    step_count = 0

    try:
        with open(template_path, 'r') as f:
            template = json.load(f)
    except Exception as e:
        return [f"  {template_path.name}: Failed to load JSON: {e}"], 0

    template_id = template.get("template_id", "UNKNOWN")
    mechanism_chain = template.get("mechanism_chain", [])

    if not mechanism_chain:
        return [f"  {template_id}: No mechanism_chain found"], 0

    for step_obj in mechanism_chain:
        step_num = step_obj.get("step")
        step_count += 1

        if "justification" not in step_obj:
            errors.append(f"  {template_id} Step {step_num}: No justification object")
            continue

        justification = step_obj["justification"]
        if justification is None:
            errors.append(f"  {template_id} Step {step_num}: justification is null")
            continue

        # Validate this justification
        step_errors = validate_justification(template_id, step_num, justification)
        errors.extend(step_errors)

    return errors, step_count

def main():
    """Validate all 9 MULTI-I templates."""
    target_templates = [
        "CROSSMODAL_CONGRUENCE_001.json",
        "CT_AFFECTIVE_TOUCH_001.json",
        "HAP_SURFACE_MATERIAL_001.json",
        "MATERIAL_AGING_TEMPORAL_DEPTH_001.json",
        "MATERIAL_CULTURAL_CONDITIONING_001.json",
        "MATERIAL_IDENTITY_INTEGRATION_001.json",
        "MSI_CONGRUENCY_PRINCIPLE_001.json",
        "MSI_INVERSE_EFFECTIVENESS_002.json",
        "NATURAL_MATERIAL_CONVERGENCE_001.json",
    ]

    print("=" * 80)
    print("MULTI-I TOULMIN VALIDATION REPORT")
    print("=" * 80)

    all_errors = []
    total_steps = 0

    for template_file in target_templates:
        template_path = TEMPLATES_DIR / template_file

        if not template_path.exists():
            print(f"\n✗ NOT FOUND: {template_file}")
            all_errors.append(f"File not found: {template_file}")
            continue

        errors, step_count = validate_template(template_path)
        total_steps += step_count

        if errors:
            print(f"\n✗ {template_file}")
            for error in errors:
                print(error)
            all_errors.extend(errors)
        else:
            print(f"✓ {template_file} ({step_count} steps)")

    print("\n" + "=" * 80)
    if all_errors:
        print(f"VALIDATION FAILED: {len(all_errors)} error(s) found")
        print("=" * 80)
        return 1
    else:
        print(f"✓ VALIDATION PASSED: {len(target_templates)} templates, {total_steps} mechanism steps")
        print("All justifications are complete and properly formatted.")
        print("=" * 80)
        return 0

if __name__ == "__main__":
    exit(main())
