#!/usr/bin/env python3
"""
Template Count Reconciliation Script (E-04)

Reconciles template counts across multiple sources:
- JSON files in data/templates/
- Database tables (ae.db, web_persistence.db)
- TRANSFER document
- gap_tracker output

Usage:
    python scripts/reconcile_counts.py

Author: Claude Code (Feb 22, 2026)
Sprint: CC_REPAIR_SPRINT, Task E-04
"""

import json
import re
import sqlite3
from pathlib import Path
from datetime import datetime, timezone


PROJECT_ROOT = Path(__file__).parent.parent
TEMPLATES_DIR = PROJECT_ROOT / "data" / "templates"
AE_DB = PROJECT_ROOT / "data" / "ae.db"
WEB_DB_V1 = PROJECT_ROOT / "data" / "web_persistence.db"
WEB_DB_V2 = PROJECT_ROOT / "data" / "web_persistence_v2.db"
TRANSFER_DOC = PROJECT_ROOT / "docs" / "TRANSFER_Feb21_Session8_CORRECTED.md"
VALIDATION_REPORT = PROJECT_ROOT / "data" / "template_validation_report.json"


def count_json_files():
    """Count JSON template files."""
    json_files = list(TEMPLATES_DIR.glob("*.json"))

    # Count by calibration status
    calibrated = 0
    scaffold = 0
    uncalibrated = 0
    other = 0

    for f in json_files:
        try:
            data = json.load(open(f))
            status = data.get("calibration_status", data.get("status", "unknown"))
            if status == "calibrated":
                calibrated += 1
            elif status == "scaffold":
                scaffold += 1
            elif status == "uncalibrated":
                uncalibrated += 1
            else:
                other += 1
        except:
            other += 1

    return {
        "total": len(json_files),
        "calibrated": calibrated,
        "scaffold": scaffold,
        "uncalibrated": uncalibrated,
        "other": other
    }


def count_db_templates(db_path):
    """Count templates in a SQLite database."""
    if not db_path.exists():
        return {"error": f"Database not found: {db_path}"}

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check for templates table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='templates';")
        if not cursor.fetchone():
            # Try beliefs table
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='beliefs';")
            if cursor.fetchone():
                cursor.execute("SELECT COUNT(*) FROM beliefs;")
                count = cursor.fetchone()[0]
                conn.close()
                return {"beliefs": count, "templates": 0}
            conn.close()
            return {"error": "No templates or beliefs table found"}

        cursor.execute("SELECT COUNT(*) FROM templates;")
        total = cursor.fetchone()[0]

        # Try to count by calibration status
        try:
            cursor.execute("SELECT calibration_status, COUNT(*) FROM templates GROUP BY calibration_status;")
            by_status = {row[0]: row[1] for row in cursor.fetchall()}
        except:
            by_status = {}

        conn.close()
        return {"total": total, "by_status": by_status}
    except Exception as e:
        return {"error": str(e)}


def parse_transfer_doc():
    """Parse calibrated count from TRANSFER document."""
    if not TRANSFER_DOC.exists():
        return {"error": "TRANSFER doc not found"}

    content = TRANSFER_DOC.read_text()

    # Find the total calibrated count (use last match for cumulative total)
    matches = re.findall(r'\*\*Total\*\*.*?\*\*(\d+)\*\*', content)
    if matches:
        total = int(matches[-1])  # Last Total is the cumulative one
    else:
        total = None

    # Find remaining count
    remaining_match = re.search(r'\*\*Remaining\*\*:\s*\*\*(\d+)\*\*', content)
    remaining = int(remaining_match.group(1)) if remaining_match else None

    # Count panels
    panel_matches = re.findall(r'\|\s*(\w+-I)\s*\|.*?\|\s*(\d+)\s*\|', content)
    panels = {m[0]: int(m[1]) for m in panel_matches}

    return {
        "total_calibrated": total,
        "remaining": remaining,
        "panels": panels
    }


def parse_validation_report():
    """Parse counts from validation report."""
    if not VALIDATION_REPORT.exists():
        return {"error": "Validation report not found"}

    with open(VALIDATION_REPORT) as f:
        report = json.load(f)

    summary = report.get("summary", {})
    return {
        "total": summary.get("total_templates"),
        "calibrated": summary.get("calibrated_count"),
        "scaffold_pass": summary.get("scaffold_pass"),
        "scaffold_fail": summary.get("scaffold_fail"),
        "calibrated_pass": summary.get("calibrated_pass"),
        "calibrated_fail": summary.get("calibrated_fail")
    }


def reconcile():
    """Run full reconciliation."""
    print("Template Count Reconciliation (E-04)")
    print("=" * 60)
    print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
    print()

    # Source 1: JSON files
    print("SOURCE 1: JSON Files (data/templates/)")
    print("-" * 40)
    json_counts = count_json_files()
    if "error" in json_counts:
        print(f"  ERROR: {json_counts['error']}")
    else:
        print(f"  Total files: {json_counts['total']}")
        print(f"  Calibrated:  {json_counts['calibrated']}")
        print(f"  Scaffold:    {json_counts['scaffold']}")
        print(f"  Uncalibrated: {json_counts['uncalibrated']}")
        print(f"  Other:       {json_counts['other']}")
    print()

    # Source 2: ae.db
    print("SOURCE 2: ae.db (templates table)")
    print("-" * 40)
    ae_counts = count_db_templates(AE_DB)
    if "error" in ae_counts:
        print(f"  {ae_counts['error']}")
    else:
        print(f"  Total: {ae_counts.get('total', 'N/A')}")
        if ae_counts.get("by_status"):
            for status, count in ae_counts["by_status"].items():
                print(f"    {status}: {count}")
    print()

    # Source 3: web_persistence.db (v1)
    print("SOURCE 3: web_persistence.db (beliefs table)")
    print("-" * 40)
    web_v1_counts = count_db_templates(WEB_DB_V1)
    if "error" in web_v1_counts:
        print(f"  {web_v1_counts['error']}")
    else:
        print(f"  Beliefs: {web_v1_counts.get('beliefs', 'N/A')}")
        print(f"  Templates: {web_v1_counts.get('total', 'N/A')}")
    print()

    # Source 4: TRANSFER document
    print("SOURCE 4: TRANSFER Document")
    print("-" * 40)
    transfer_counts = parse_transfer_doc()
    if "error" in transfer_counts:
        print(f"  ERROR: {transfer_counts['error']}")
    else:
        print(f"  Total calibrated: {transfer_counts['total_calibrated']}")
        print(f"  Remaining: {transfer_counts['remaining']}")
        if transfer_counts.get("panels"):
            print("  Panels:")
            for panel, count in transfer_counts["panels"].items():
                print(f"    {panel}: {count}")
    print()

    # Source 5: Validation report
    print("SOURCE 5: Validation Report")
    print("-" * 40)
    val_counts = parse_validation_report()
    if "error" in val_counts:
        print(f"  ERROR: {val_counts['error']}")
    else:
        print(f"  Total templates: {val_counts['total']}")
        print(f"  Calibrated count: {val_counts['calibrated']}")
        print(f"  Scaffold pass: {val_counts['scaffold_pass']}")
        print(f"  Scaffold fail: {val_counts['scaffold_fail']}")
        print(f"  Calibrated pass: {val_counts['calibrated_pass']}")
        print(f"  Calibrated fail: {val_counts['calibrated_fail']}")
    print()

    # Reconciliation summary
    print("=" * 60)
    print("RECONCILIATION SUMMARY")
    print("=" * 60)

    discrepancies = []

    # Check JSON vs validation report
    if json_counts.get("total") != val_counts.get("total"):
        discrepancies.append(
            f"JSON files ({json_counts.get('total')}) != Validation report ({val_counts.get('total')})"
        )

    # Check JSON calibrated vs TRANSFER
    json_cal = json_counts.get("calibrated", 0)
    transfer_cal = transfer_counts.get("total_calibrated", 0)
    if json_cal != transfer_cal:
        discrepancies.append(
            f"JSON calibrated ({json_cal}) != TRANSFER doc ({transfer_cal})"
        )

    # Check validation calibrated vs JSON
    val_cal = val_counts.get("calibrated", 0)
    if json_cal != val_cal:
        discrepancies.append(
            f"JSON calibrated ({json_cal}) != Validation calibrated ({val_cal})"
        )

    if discrepancies:
        print("DISCREPANCIES FOUND:")
        for d in discrepancies:
            print(f"  - {d}")
    else:
        print("All sources agree on template counts.")

    print()
    print("RECOMMENDED COUNTS:")
    print(f"  Total templates: {json_counts.get('total', '?')}")
    print(f"  Calibrated: {json_counts.get('calibrated', '?')}")
    print()

    return len(discrepancies) == 0


if __name__ == "__main__":
    success = reconcile()
    exit(0 if success else 1)
