#!/usr/bin/env python3
"""
Template Schema Migration Script (M-01)

Migrates all JSON templates to canonical schema format.
Applies field name normalization, adds missing required fields,
generates display_id and name where missing.

Usage:
    python scripts/migrate_templates.py                # Migrate all
    python scripts/migrate_templates.py --dry-run      # Preview changes
    python scripts/migrate_templates.py --verbose      # Show details

Author: Claude Code (Feb 22, 2026)
Sprint: CC_REPAIR_SPRINT, Task M-01
"""

import argparse
import json
import re
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Optional
from dataclasses import dataclass, field


PROJECT_ROOT = Path(__file__).parent.parent
TEMPLATES_DIR = PROJECT_ROOT / "data" / "templates"

# T1 Framework codes
T1_FRAMEWORKS = {"PP", "SN", "DP", "DT", "NM", "IC", "MS", "EC", "CB", "MSI"}

# Field name mappings (old -> canonical)
FIELD_MAPPINGS = {
    "mechanism_steps": "mechanism_chain",
    "bridge_warrant_type": "bridge_warrant",
    "super_template_interactions": "cross_template_interactions",
    "prior_confidence": "confidence",
    "architectural_modifier_coefficients": "architectural_modifiers",
}

# Status value mappings
STATUS_MAPPINGS = {
    "calibrated": "calibrated",
    "scaffold": "scaffold",
    "uncalibrated": "uncalibrated",
    "partial": "partial",
    "stub": "scaffold",
    "draft": "scaffold",
    "pending": "uncalibrated",
    "how-plausibly": "calibrated",  # maturity level indicating calibration
}


@dataclass
class MigrationResult:
    """Result for a single template migration."""
    file_path: str
    template_id: str
    changes: list = field(default_factory=list)
    errors: list = field(default_factory=list)
    migrated: bool = False


def derive_display_id(template_id: str, data: dict) -> str:
    """Generate display_id from template_id or existing fields."""
    # Check for existing series IDs in the file
    for key in ["series_id", "short_id"]:
        if key in data and data[key]:
            return str(data[key])

    # Known mappings for specific templates
    known_ids = {
        "NATURE_VIEW_CONVERGENCE_001": "VIEW1",
        "PP_SPECTRAL_MATCH_001": "T1",
        "PP_COMPLEXITY_GOLDILOCKS_002": "T2",
        "PP_RAPID_GIST_004": "T22",
        "LUM_CONTRAST_PE_001": "L1",
        "NM_THREAT_HPA_001": "T6",
        "IC_ALLOSTATIC_ANTICIPATION_001": "T7",
        "MULTIMODAL_PE_INTEGRATION_001": "T14",
        "SPATIAL_INTEGRATION_PE_001": "SC1",
        "ISOVIST_VISUAL_PREDICTION_001": "SC2",
        "ARCH_PROMENADE_TEMPORAL_PE_001": "SC3",
        "SPATIAL_SOCIAL_ENCOUNTER_001": "SC4",
        "VF1_CONTOUR_PE_001": "VF1",
        "VF2_VISUAL_RHYTHM_001": "VF2",
        "VF3_SPATIAL_PROPORTIONS_001": "VF3",
    }

    if template_id in known_ids:
        return known_ids[template_id]

    # Generate from template_id pattern
    # e.g., ED_HIPPOCAMPAL_ENCODING_001 -> EHE1
    parts = re.sub(r"_\d+$", "", template_id).split("_")

    # Take first letter of each significant part (skip short parts like "I")
    abbrev_parts = [p[0].upper() for p in parts if len(p) > 1][:4]
    abbrev = "".join(abbrev_parts)

    # Add number suffix from template_id
    match = re.search(r"(\d+)$", template_id)
    num = match.group(1)[-1] if match else "1"

    return f"{abbrev}{num}"


def derive_name(template_id: str) -> str:
    """Generate human-readable name from template_id."""
    # Remove number suffix
    name = re.sub(r"_\d+$", "", template_id)
    # Replace underscores with spaces, title case
    name = name.replace("_", " ").title()
    return name


def normalize_t1_frameworks(t1_list: list) -> list:
    """Normalize t1_frameworks to list of strings."""
    if not isinstance(t1_list, list):
        return []

    normalized = []
    for item in t1_list:
        if isinstance(item, str):
            # Handle format like "IC" or "ic"
            code = item.upper()
            if code in T1_FRAMEWORKS:
                normalized.append(code)
        elif isinstance(item, dict):
            # Handle format like {"code": "IC"} or {"framework": "IC"}
            code = item.get("code") or item.get("framework") or item.get("id")
            if code:
                code = code.upper()
                if code in T1_FRAMEWORKS:
                    normalized.append(code)

    return list(dict.fromkeys(normalized))  # Remove duplicates, preserve order


def get_calibration_status(data: dict) -> str:
    """Extract and normalize calibration status."""
    # Check explicit calibration_status first
    if "calibration_status" in data:
        status = data["calibration_status"]
        return STATUS_MAPPINGS.get(status, status)

    # Check legacy status field
    if "status" in data:
        status = data["status"]
        return STATUS_MAPPINGS.get(status, "uncalibrated")

    # Check boolean calibrated flag
    if data.get("calibrated") is True:
        return "calibrated"

    # Check maturity field
    maturity = data.get("maturity", "")
    if maturity in ("how-plausibly", "calibrated"):
        return "calibrated"

    return "uncalibrated"


def normalize_mechanism_chain(chain: Any) -> list:
    """Normalize mechanism_chain to list of step objects."""
    if not isinstance(chain, list):
        return []

    normalized = []
    for i, step in enumerate(chain):
        if isinstance(step, dict):
            # Already an object, keep it
            norm_step = dict(step)
            # Ensure step number
            if "step" not in norm_step and "step_number" not in norm_step:
                norm_step["step"] = i + 1
            normalized.append(norm_step)
        elif isinstance(step, str):
            # String step - convert to object
            normalized.append({
                "step": i + 1,
                "description": step
            })

    return normalized


def migrate_template(file_path: Path, dry_run: bool = False) -> MigrationResult:
    """Migrate a single template file."""
    result = MigrationResult(
        file_path=str(file_path.relative_to(PROJECT_ROOT)),
        template_id=""
    )

    try:
        with open(file_path) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        result.errors.append(f"Invalid JSON: {e}")
        return result

    original = json.dumps(data, sort_keys=True)
    result.template_id = data.get("template_id", file_path.stem)

    # Apply field name mappings
    for old_name, new_name in FIELD_MAPPINGS.items():
        if old_name in data and new_name not in data:
            data[new_name] = data.pop(old_name)
            result.changes.append(f"Renamed {old_name} -> {new_name}")

    # Ensure template_id
    if "template_id" not in data:
        data["template_id"] = file_path.stem
        result.changes.append(f"Added template_id: {data['template_id']}")

    # Ensure display_id
    if "display_id" not in data or not data["display_id"]:
        data["display_id"] = derive_display_id(data["template_id"], data)
        result.changes.append(f"Added display_id: {data['display_id']}")

    # Ensure name (check both name and template_name)
    if "name" not in data and "template_name" not in data:
        data["name"] = derive_name(data["template_id"])
        result.changes.append(f"Added name: {data['name']}")
    elif "template_name" in data and "name" not in data:
        data["name"] = data["template_name"]
        result.changes.append(f"Copied template_name to name")

    # Normalize t1_frameworks
    if "t1_frameworks" in data:
        old_t1 = data["t1_frameworks"]
        new_t1 = normalize_t1_frameworks(old_t1)
        if new_t1 != old_t1:
            data["t1_frameworks"] = new_t1
            result.changes.append(f"Normalized t1_frameworks: {old_t1} -> {new_t1}")
    else:
        # Try to infer from template_id prefix
        prefix = data["template_id"].split("_")[0].upper()
        if prefix in T1_FRAMEWORKS:
            data["t1_frameworks"] = [prefix]
            result.changes.append(f"Inferred t1_frameworks: [{prefix}]")
        else:
            data["t1_frameworks"] = []
            result.changes.append("Added empty t1_frameworks (needs manual review)")

    # Normalize calibration_status
    old_status = data.get("calibration_status") or data.get("status")
    new_status = get_calibration_status(data)
    if "calibration_status" not in data or data.get("calibration_status") != new_status:
        data["calibration_status"] = new_status
        if old_status != new_status:
            result.changes.append(f"Set calibration_status: {old_status} -> {new_status}")

    # Set panel_source from panel or panel_id if available
    if "panel_source" not in data:
        panel = data.get("panel_id") or data.get("panel")
        if panel:
            data["panel_source"] = panel
            result.changes.append(f"Added panel_source: {panel}")

    # Normalize mechanism_chain
    if "mechanism_chain" in data:
        old_chain = data["mechanism_chain"]
        new_chain = normalize_mechanism_chain(old_chain)
        if new_chain != old_chain:
            data["mechanism_chain"] = new_chain
            result.changes.append(f"Normalized mechanism_chain ({len(new_chain)} steps)")

    # Handle confidence field
    if "confidence" not in data:
        conf = data.get("bridge_prior") or data.get("prior_confidence")
        if conf is not None:
            data["confidence"] = conf
            result.changes.append(f"Copied {('bridge_prior' if 'bridge_prior' in data else 'prior_confidence')} to confidence")

    # Check if anything changed
    migrated = json.dumps(data, sort_keys=True)
    if migrated != original:
        result.migrated = True

        if not dry_run:
            # Write back
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)

    return result


def run_migration(dry_run: bool = False, verbose: bool = False) -> dict:
    """Run migration on all templates."""
    results = []

    json_files = sorted(TEMPLATES_DIR.glob("*.json"))

    for file_path in json_files:
        result = migrate_template(file_path, dry_run)
        results.append(result)

        if verbose and (result.changes or result.errors):
            status = "DRY-RUN" if dry_run else "MIGRATED" if result.migrated else "OK"
            print(f"\n[{status}] {result.template_id}")
            for c in result.changes:
                print(f"  + {c}")
            for e in result.errors:
                print(f"  ERROR: {e}")

    # Summary
    total = len(results)
    migrated = sum(1 for r in results if r.migrated)
    errors = sum(1 for r in results if r.errors)

    summary = {
        "total_templates": total,
        "migrated": migrated,
        "errors": errors,
        "dry_run": dry_run,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    # Change patterns
    change_patterns = {}
    for r in results:
        for c in r.changes:
            pattern = c.split(":")[0] if ":" in c else c.split(" ")[0]
            change_patterns[pattern] = change_patterns.get(pattern, 0) + 1

    return {
        "summary": summary,
        "change_patterns": change_patterns,
        "results": [{"template_id": r.template_id, "changes": r.changes, "errors": r.errors, "migrated": r.migrated} for r in results]
    }


def main():
    parser = argparse.ArgumentParser(description="Migrate CMR templates to canonical schema")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed output")
    args = parser.parse_args()

    print("Template Schema Migration (M-01)")
    print("=" * 50)
    print(f"Templates dir: {TEMPLATES_DIR}")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
    print()

    report = run_migration(args.dry_run, args.verbose)

    # Print summary
    s = report["summary"]
    print(f"\n{'='*50}")
    print("SUMMARY")
    print(f"{'='*50}")
    print(f"Total templates: {s['total_templates']}")
    print(f"Migrated:        {s['migrated']}")
    print(f"Errors:          {s['errors']}")

    if report["change_patterns"]:
        print(f"\nChange patterns:")
        for pattern, count in sorted(report["change_patterns"].items(), key=lambda x: -x[1]):
            print(f"  {count:3d}x {pattern}")

    if args.dry_run:
        print("\n[DRY RUN - no files modified]")
    else:
        print(f"\n{s['migrated']} templates updated.")

    return 0 if s["errors"] == 0 else 1


if __name__ == "__main__":
    exit(main())
