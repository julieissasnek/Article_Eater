#!/usr/bin/env python3
"""
Gap Tracker Script (M-04)

Tracks template mechanism gaps using canonical schema fields.
Replaces legacy field checks with canonical field validation.

Usage:
    python scripts/gap_tracker.py --rebuild    # Rebuild registry from templates
    python scripts/gap_tracker.py --report     # Generate gap report
    python scripts/gap_tracker.py              # Default: report

Author: Refactored by Claude Code (Feb 22, 2026)
Sprint: CC_REPAIR_SPRINT, Task M-04
"""

import argparse
import json
from pathlib import Path
from datetime import datetime, timezone

from resolve_fields import resolve_field, get_mechanism_chain, get_calibration_status, get_panel_source


DATA_DIR = Path("data")
TEMPLATES_DIR = DATA_DIR / "templates"
REGISTRY_PATH = DATA_DIR / "gap_registry.json"


def is_gap(template: dict) -> list[str]:
    """
    Determine if a template has gaps using canonical schema fields.

    Canonical gap criteria:
    - calibration_status != "calibrated"
    - Missing or empty mechanism_chain
    - Missing calibrated_parameters
    - Missing bridge_warrant
    - Missing confidence

    Returns list of gap reasons, or empty list if no gaps.
    """
    reasons = []

    # Check calibration status (use resolver)
    status = get_calibration_status(template)

    if status != "calibrated":
        if status == "scaffold":
            reasons.append("scaffold_status")
        elif status == "uncalibrated" or status is None:
            reasons.append("uncalibrated")
        elif status == "partial":
            reasons.append("partial_calibration")
        else:
            reasons.append(f"unknown_status:{status}")

    # Check mechanism_chain (use resolver)
    mechanism = get_mechanism_chain(template)
    if not mechanism:
        reasons.append("missing_mechanism_chain")
    elif len(mechanism) < 2:
        reasons.append("incomplete_mechanism_chain")

    # Check calibrated_parameters
    params = template.get("calibrated_parameters")
    if not params or params == {}:
        reasons.append("missing_calibrated_parameters")

    # Check bridge_warrant (use resolver)
    warrant = resolve_field(template, "bridge_warrant")
    if not warrant:
        reasons.append("missing_bridge_warrant")

    # Check confidence (use resolver)
    confidence = resolve_field(template, "confidence")
    if confidence is None:
        reasons.append("missing_confidence")

    # Check for missing cross_template_interactions (expected for calibrated)
    if status == "calibrated":
        interactions = resolve_field(template, "cross_template_interactions")
        if not interactions:
            reasons.append("missing_cross_template_interactions")

    return reasons


def calculate_triage_score(template: dict, reasons: list[str]) -> tuple[int, str]:
    """
    Calculate triage severity score based on gap reasons.

    Scoring:
    - uncalibrated/scaffold status: +1
    - missing mechanism_chain: +4 (critical)
    - incomplete mechanism_chain: +2
    - missing calibrated_parameters: +3
    - missing bridge_warrant: +2
    - missing confidence: +1
    - missing cross_template_interactions: +1

    Levels:
    - High: score >= 7
    - Medium: score >= 4
    - Low: score >= 1
    - None: score == 0
    """
    score = 0

    if "uncalibrated" in reasons or "scaffold_status" in reasons:
        score += 1
    if "partial_calibration" in reasons:
        score += 2
    if "missing_mechanism_chain" in reasons:
        score += 4
    if "incomplete_mechanism_chain" in reasons:
        score += 2
    if "missing_calibrated_parameters" in reasons:
        score += 3
    if "missing_bridge_warrant" in reasons:
        score += 2
    if "missing_confidence" in reasons:
        score += 1
    if "missing_cross_template_interactions" in reasons:
        score += 1

    # Determine level
    if score >= 7:
        level = "High"
    elif score >= 4:
        level = "Medium"
    elif score >= 1:
        level = "Low"
    else:
        level = "None"

    return score, level


def rebuild_registry():
    """Rebuild gap registry from template JSON files."""
    registry = []

    if not TEMPLATES_DIR.exists():
        print(f"Error: Templates directory {TEMPLATES_DIR} does not exist.")
        return

    for file_path in TEMPLATES_DIR.glob("*.json"):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                template = json.load(f)
        except Exception as e:
            print(f"Warning: Failed to parse {file_path.name}: {e}")
            continue

        try:
            template_id = template.get("template_id", file_path.stem)
            reasons = is_gap(template)
            score, level = calculate_triage_score(template, reasons)

            # Get calibration status using resolver
            cal_status = get_calibration_status(template)

            # Get panel source using resolver
            panel_source = get_panel_source(template)

            # Count mechanism steps (use resolver)
            mechanism = get_mechanism_chain(template)
            mechanism_step_count = len(mechanism)

            # Count missing parameters in mechanism steps
            missing_step_params = 0
            for step in mechanism:
                if isinstance(step, dict):
                    if not resolve_field(step, "confidence"):
                        missing_step_params += 1

            entry = {
                "template_id": template_id,
                "display_id": template.get("display_id", ""),
                "name": template.get("name", "Unknown"),
                "t1_frameworks": template.get("t1_frameworks", []),
                "calibration_status": cal_status,
                "panel_source": panel_source,
                "calibrated_date": template.get("calibrated_date"),
                "gap_reasons": reasons,
                "mechanism_step_count": mechanism_step_count,
                "missing_step_params": missing_step_params,
                "triage_score": score,
                "triage_level": level,
            }
            registry.append(entry)
        except Exception as e:
            # Skip corrupt entries gracefully
            print(f"SKIP (corrupt): {template_id} — {e}", file=__import__('sys').stderr)
            continue

    # Sort by triage score descending
    registry.sort(key=lambda x: x["triage_score"], reverse=True)

    # Ensure data dir exists
    DATA_DIR.mkdir(exist_ok=True)
    with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2)

    # Summary
    calibrated = sum(1 for r in registry if r["calibration_status"] == "calibrated")
    high = sum(1 for r in registry if r["triage_level"] == "High")
    medium = sum(1 for r in registry if r["triage_level"] == "Medium")
    low = sum(1 for r in registry if r["triage_level"] == "Low")
    none = sum(1 for r in registry if r["triage_level"] == "None")

    print(f"Registry rebuilt with {len(registry)} templates.")
    print(f"  Calibrated: {calibrated}")
    print(f"  High severity: {high}")
    print(f"  Medium severity: {medium}")
    print(f"  Low severity: {low}")
    print(f"  No gaps: {none}")


def load_registry():
    """Load existing registry or rebuild if missing."""
    if not REGISTRY_PATH.exists():
        rebuild_registry()
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_registry(registry):
    """Save registry to disk."""
    with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2)


def report():
    """Generate and print gap registry report."""
    registry = load_registry()

    # Categorize
    calibrated = [r for r in registry if r["calibration_status"] == "calibrated"]
    uncalibrated = [r for r in registry if r["calibration_status"] != "calibrated"]

    high_sev = [r for r in uncalibrated if r["triage_level"] == "High"]
    med_sev = [r for r in uncalibrated if r["triage_level"] == "Medium"]
    low_sev = [r for r in uncalibrated if r["triage_level"] == "Low"]

    # Console summary
    print("=== Gap Registry Summary ===")
    print(f"Total Templates: {len(registry)}")
    print(f"  Calibrated:    {len(calibrated)}")
    print(f"  Uncalibrated:  {len(uncalibrated)}")
    print(f"    - High:      {len(high_sev)}")
    print(f"    - Medium:    {len(med_sev)}")
    print(f"    - Low:       {len(low_sev)}")
    print("============================")

    # Generate Markdown report
    report_lines = [
        "# Gap Registry Triage Report",
        "",
        f"**Generated:** {datetime.now(timezone.utc).isoformat()}",
        f"**Total Templates:** {len(registry)}",
        "",
        "## Summary",
        "",
        f"- **Calibrated:** {len(calibrated)}",
        f"- **High Severity:** {len(high_sev)}",
        f"- **Medium Severity:** {len(med_sev)}",
        f"- **Low Severity:** {len(low_sev)}",
        "",
        "## Scoring Criteria",
        "",
        "| Criterion | Points |",
        "|-----------|--------|",
        "| Missing mechanism_chain | +4 |",
        "| Missing calibrated_parameters | +3 |",
        "| Incomplete mechanism_chain | +2 |",
        "| Missing bridge_warrant | +2 |",
        "| Partial calibration | +2 |",
        "| Uncalibrated/scaffold status | +1 |",
        "| Missing confidence | +1 |",
        "| Missing cross_template_interactions | +1 |",
        "",
        "**Levels:** High (7+), Medium (4-6), Low (1-3)",
        "",
    ]

    def write_table(group, title):
        if not group:
            return
        report_lines.append(f"## {title} ({len(group)})")
        report_lines.append("")
        report_lines.append("| Template ID | Display | Gap Reasons | Score | Panel |")
        report_lines.append("|-------------|---------|-------------|-------|-------|")
        for r in group:
            tid = r["template_id"]
            display = r.get("display_id", "")
            reasons = ", ".join(r.get("gap_reasons", [])[:3])  # Truncate long lists
            if len(r.get("gap_reasons", [])) > 3:
                reasons += "..."
            score = r["triage_score"]
            panel = r.get("panel_source") or "-"
            report_lines.append(f"| {tid} | {display} | {reasons} | {score} | {panel} |")
        report_lines.append("")

    write_table(high_sev, "High Severity Gaps")
    write_table(med_sev, "Medium Severity Gaps")
    write_table(low_sev, "Low Severity Gaps")

    # Calibrated summary (just list, not full table)
    if calibrated:
        report_lines.append(f"## Calibrated Templates ({len(calibrated)})")
        report_lines.append("")
        report_lines.append("| Template ID | Display | Panel |")
        report_lines.append("|-------------|---------|-------|")
        for r in calibrated:
            tid = r["template_id"]
            display = r.get("display_id", "")
            panel = r.get("panel_source") or "-"
            report_lines.append(f"| {tid} | {display} | {panel} |")
        report_lines.append("")

    # Write report
    out_path = Path("docs/gap_registry_report.md")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(report_lines))
    print(f"Detailed report: {out_path}")


def mark_calibrated(template_id: str, panel_id: str, source_doc: str = None):
    """Mark a template as calibrated."""
    template_file = TEMPLATES_DIR / f"{template_id}.json"

    if template_file.exists():
        with open(template_file, "r", encoding="utf-8") as f:
            template = json.load(f)

        # Use canonical field names
        template["calibration_status"] = "calibrated"
        template["panel_source"] = panel_id
        template["calibrated_date"] = datetime.now(timezone.utc).isoformat()

        # Remove legacy fields if present
        if "status" in template:
            del template["status"]
        if "calibrated" in template:
            del template["calibrated"]

        if source_doc:
            if "panel_docs" not in template:
                template["panel_docs"] = []
            if source_doc not in template["panel_docs"]:
                template["panel_docs"].append(source_doc)

        with open(template_file, "w", encoding="utf-8") as f:
            json.dump(template, f, indent=2)

        print(f"Marked {template_id} as calibrated by panel {panel_id}.")
    else:
        print(f"Template file not found: {template_file}")


def export_for_panel(panel_id: str):
    """Export templates assigned to a specific panel."""
    registry = load_registry()
    assigned = [r for r in registry if r.get("panel_source") == panel_id]

    if not assigned:
        print(f"No templates found for panel {panel_id}.")
        return

    print(json.dumps(assigned, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Track template mechanism gaps (canonical schema)")
    parser.add_argument("--report", action="store_true", help="Print gap registry summary and generate report")
    parser.add_argument("--rebuild", action="store_true", help="Rebuild registry from data/templates/*.json")
    parser.add_argument("--mark-calibrated", metavar="TEMPLATE_ID", help="Mark a template as calibrated")
    parser.add_argument("--panel", metavar="PANEL_ID", help="Panel ID (required with --mark-calibrated)")
    parser.add_argument("--source", metavar="DOC_PATH", help="Source document path")
    parser.add_argument("--export-for-panel", metavar="PANEL_ID", help="Export templates for a panel")

    args = parser.parse_args()

    if args.rebuild:
        rebuild_registry()
    elif args.report:
        report()
    elif args.mark_calibrated:
        if not args.panel:
            print("--panel is required with --mark-calibrated")
            return
        mark_calibrated(args.mark_calibrated, args.panel, args.source)
    elif args.export_for_panel:
        export_for_panel(args.export_for_panel)
    else:
        # Default: report
        report()


if __name__ == "__main__":
    main()
