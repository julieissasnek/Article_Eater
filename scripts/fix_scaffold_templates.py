#!/usr/bin/env python3
"""
Fix Scaffold Templates Script

Reads failing scaffold templates and adds/fixes required fields with sensible defaults.

IMPORTANT: This script fixes structural issues, NOT missing domain data.

Fields fixed:
  - calibration_status: Normalize to standard value (scaffold, calibrated, uncalibrated)
  - display_id: Derive from filename if missing
  - mechanism_chain: Add empty array for calibrated templates
  - tier: Add "scaffold" if missing
  - name: Derive from template_id if missing

Fields NOT fixed (require manual panel assignment):
  - t1_frameworks: MUST be manually assigned — do not auto-populate with empty array
  - confidence values (reserved for panel calibration)
  - bridge_warrant (reserved for panel calibration)

Because these templates lack t1_frameworks, they will still fail scaffold-tier validation.
The purpose of this script is to clean up structural issues so the panel can focus on
domain-specific assignments.

Usage:
    python scripts/fix_scaffold_templates.py                 # Fix all failing templates
    python scripts/fix_scaffold_templates.py --verbose       # Show details
    python scripts/fix_scaffold_templates.py --dry-run       # Preview changes

Author: Claude Code (Feb 23, 2026)
Sprint: CC_REPAIR_SPRINT, Task E-02
"""

import argparse
import json
import re
from pathlib import Path
from datetime import datetime, timezone
from typing import Tuple, List

PROJECT_ROOT = Path(__file__).parent.parent
TEMPLATES_DIR = PROJECT_ROOT / "data" / "templates"
REPORT_PATH = PROJECT_ROOT / "data" / "template_validation_report.json"

# Standard calibration status values
VALID_CALIBRATION_STATUSES = {"calibrated", "scaffold", "uncalibrated", "partial"}


def derive_display_id(template_id: str, filename: str) -> str:
    """Generate display_id from filename or template_id."""
    # Prefer filename without extension
    stem = Path(filename).stem
    if stem and stem[0].isalpha():
        return stem
    
    # Fallback to deriving from template_id
    # e.g., NATURE_VIEW_CONVERGENCE_001 -> NVC1
    parts = template_id.replace("_001", "").replace("_002", "").replace("_003", "").split("_")
    if len(parts) >= 2:
        abbrev = "".join(p[0].upper() for p in parts[:3] if p)
        match = re.search(r"(\d+)$", template_id)
        num = match.group(1)[-1] if match else "1"
        return f"{abbrev}{num}"
    
    return template_id[:8]


def derive_name(template_id: str) -> str:
    """Generate human-readable name from template_id."""
    name = re.sub(r"_\d+$", "", template_id)
    name = name.replace("_", " ").title()
    return name


def normalize_calibration_status(status: str) -> str:
    """Normalize calibration status to standard values."""
    if not status:
        return "scaffold"
    
    status = status.lower().strip()
    
    # Already valid
    if status in VALID_CALIBRATION_STATUSES:
        return status
    
    # Map common variants to standard values
    if "deepened" in status or "deep" in status:
        return "calibrated"
    if "substantial" in status or "mostly" in status:
        return "partial"
    if "scaf" in status:
        return "scaffold"
    if "uncal" in status or "none" in status or "initial" in status:
        return "uncalibrated"
    
    # Default to scaffold if unrecognized
    print(f"  WARN: Unknown calibration_status '{status}' → 'scaffold'")
    return "scaffold"


def fix_template(file_path: Path, data: dict, verbose: bool = False) -> Tuple[dict, List[str]]:
    """
    Fix a template by fixing structural issues.
    
    NOTE: Does NOT add t1_frameworks — those must be manually assigned.
    
    Returns:
        (modified_data, changes_list)
    """
    changes = []
    filename = file_path.name
    template_id = data.get("template_id", file_path.stem)
    
    # Fix display_id
    if "display_id" not in data or not data["display_id"]:
        display_id = derive_display_id(template_id, filename)
        data["display_id"] = display_id
        changes.append(f"Generated display_id: {display_id}")
        if verbose:
            print(f"    + display_id: {display_id}")
    
    # Fix name
    if "name" not in data or not data["name"]:
        if "template_name" in data and data["template_name"]:
            data["name"] = data["template_name"]
            changes.append("Copied template_name → name")
            if verbose:
                print(f"    + name: {data['name']} (from template_name)")
        else:
            name = derive_name(template_id)
            data["name"] = name
            changes.append(f"Generated name: {name}")
            if verbose:
                print(f"    + name: {name}")
    
    # Fix calibration_status
    if "calibration_status" in data:
        current = data["calibration_status"]
        if current not in VALID_CALIBRATION_STATUSES:
            normalized = normalize_calibration_status(str(current))
            data["calibration_status"] = normalized
            changes.append(f"Normalized calibration_status: {current} → {normalized}")
            if verbose:
                print(f"    ~ calibration_status: {current} → {normalized}")
    else:
        data["calibration_status"] = "scaffold"
        changes.append("Added default calibration_status: scaffold")
        if verbose:
            print(f"    + calibration_status: scaffold")
    
    # Fix mechanism_chain (if it's marked as calibrated)
    if data.get("calibration_status") == "calibrated":
        if "mechanism_chain" not in data or not data["mechanism_chain"]:
            data["mechanism_chain"] = []
            changes.append("Added empty mechanism_chain array (calibrated template)")
            if verbose:
                print(f"    + mechanism_chain: []")
    
    # Fix tier
    if "tier" not in data or not data["tier"]:
        tier = "calibrated" if data.get("calibration_status") == "calibrated" else "scaffold"
        data["tier"] = tier
        changes.append(f"Added tier: {tier}")
        if verbose:
            print(f"    + tier: {tier}")
    
    # NOTE: We do NOT add t1_frameworks if missing
    # Those must be manually assigned by the panel
    if not data.get("t1_frameworks"):
        changes.append("⚠️  REQUIRES PANEL REVIEW: t1_frameworks must be manually assigned")
        if verbose:
            print(f"    ⚠️  t1_frameworks is empty — requires manual panel assignment")
    
    return data, changes


def process_templates(verbose: bool = False, dry_run: bool = False) -> dict:
    """
    Process all failing templates.
    
    Returns:
        Summary dict with statistics
    """
    # Load validation report to find failing templates
    if not REPORT_PATH.exists():
        print(f"ERROR: Validation report not found at {REPORT_PATH}")
        print("Run: python scripts/validate_templates.py")
        return {"error": "No report"}
    
    with open(REPORT_PATH) as f:
        report = json.load(f)
    
    failing_template_ids = {
        r["template_id"]: r["file_path"]
        for r in report["results"]
        if not r["scaffold_pass"]
    }
    
    print(f"Found {len(failing_template_ids)} failing scaffold templates")
    print()
    
    fixed = 0
    failed = 0
    total_changes = 0
    summary = {
        "fixed": 0,
        "failed": 0,
        "total_changes": 0,
        "requires_panel_review": 0,
        "by_template": {}
    }
    
    # Process each failing template
    for template_id, rel_path in sorted(failing_template_ids.items()):
        file_path = PROJECT_ROOT / rel_path
        
        if not file_path.exists():
            print(f"SKIP: {template_id} — file not found at {rel_path}")
            failed += 1
            continue
        
        try:
            # Load template
            with open(file_path) as f:
                data = json.load(f)
            
            # Fix it
            data, changes = fix_template(file_path, data, verbose)
            
            if verbose:
                print(f"{template_id}:")
                for change in changes:
                    print(f"  {change}")
            else:
                print(f"  {template_id}: {len(changes)} fix(es)")
            
            # Track if this needs panel review
            needs_panel = not data.get("t1_frameworks")
            if needs_panel:
                summary["requires_panel_review"] += 1
            
            # Write back (unless dry-run)
            if not dry_run:
                with open(file_path, "w") as f:
                    json.dump(data, f, indent=2)
            
            fixed += 1
            total_changes += len(changes)
            summary["by_template"][template_id] = {
                "file": rel_path,
                "changes": changes,
                "requires_panel_review": needs_panel
            }
        
        except Exception as e:
            print(f"ERROR: {template_id} — {e}")
            failed += 1
    
    summary["fixed"] = fixed
    summary["failed"] = failed
    summary["total_changes"] = total_changes
    summary["dry_run"] = dry_run
    
    return summary


def main():
    parser = argparse.ArgumentParser(description="Fix structural issues in failing scaffold templates")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed changes")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing")
    args = parser.parse_args()
    
    print("Fix Scaffold Templates (E-02)")
    print("=" * 60)
    print(f"Templates dir: {TEMPLATES_DIR}")
    print()
    print("NOTE: This script fixes structural issues (display_id, name, tier)")
    print("but does NOT auto-populate t1_frameworks — those require manual")
    print("assignment by the panel.")
    print()
    
    if args.dry_run:
        print("[DRY-RUN MODE - no files will be modified]")
        print()
    
    summary = process_templates(verbose=args.verbose, dry_run=args.dry_run)
    
    if "error" in summary:
        return 1
    
    # Print summary
    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Fixed:                    {summary['fixed']}")
    print(f"Failed:                   {summary['failed']}")
    print(f"Total changes:            {summary['total_changes']}")
    print(f"Requiring panel review:   {summary['requires_panel_review']}")
    print()
    print("NOTE: All 79 templates still lack t1_frameworks assignments.")
    print("These require panel review to map each template to its domain frameworks.")
    
    if args.dry_run:
        print("\n[DRY-RUN: No files were modified]")
    
    return 0 if summary['failed'] == 0 else 1


if __name__ == "__main__":
    exit(main())
