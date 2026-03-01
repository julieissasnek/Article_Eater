#!/usr/bin/env python3
"""Lint script for bridge warrant confidence ceilings (E-02).

This is the REPORTING-ONLY version. It does NOT auto-fix violations.
Instead, it reports violations and checks for the "ceiling_status" field
which flags steps that originally exceeded ceilings before restoration.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, List

from resolve_fields import resolve_field, get_confidence, get_bridge_warrant, get_panel_source, is_calibrated, get_mechanism_chain

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEMPLATES_DIR = PROJECT_ROOT / "data" / "templates"
REPORT_PATH = PROJECT_ROOT / "data" / "ceiling_violation_report.json"

CEILINGS = {
    "CONSTITUTIVE": 0.75,
    "MECHANISM": 0.60,
    "EMPIRICAL_ASSOCIATION": 0.60,
    "FUNCTIONAL": 0.50,
    "CAPACITY": 0.45,
    "ANALOGICAL": 0.35,
    "THEORY_DERIVED": 0.40,
}


@dataclass
class Violation:
    template_id: str
    field_path: str
    warrant: str
    confidence: float
    ceiling: float
    delta: float
    panel: str | None
    ceiling_status: str | None = None  # Will be "exceeds" if flagged for panel review
    ceiling_override_rationale: str | None = None  # Panel-documented reason for exceeding ceiling

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def is_calibrated_local(template: dict[str, Any]) -> bool:
    """Check if calibrated using canonical resolver."""
    return is_calibrated(template)


def normalize_warrant(value: str | None) -> str | None:
    if not value:
        return None
    return value.strip().upper()


def check_confidence(
    template_id: str,
    field: str,
    warrant_value: str | None,
    confidence_value: float | None,
    panel: str | None,
    ceiling_status: str | None = None,
    ceiling_override_rationale: str | None = None,
) -> Violation | None:
    if confidence_value is None or warrant_value is None:
        return None
    warrant = normalize_warrant(warrant_value)
    if not warrant:
        return None
    ceiling = CEILINGS.get(warrant)
    if ceiling is None:
        return None
    if confidence_value <= ceiling:
        return None
    return Violation(
        template_id=template_id,
        field_path=field,
        warrant=warrant,
        confidence=confidence_value,
        ceiling=ceiling,
        delta=confidence_value - ceiling,
        panel=panel,
        ceiling_status=ceiling_status,
        ceiling_override_rationale=ceiling_override_rationale,
    )


def extract_panel(template: dict[str, Any]) -> str | None:
    for key in ("panel_source", "panel", "panel_id", "source_panel"):
        value = template.get(key)
        if isinstance(value, str) and value:
            return value
    return None


def scan_templates(paths: Iterable[Path]) -> List[Violation]:
    violations: list[Violation] = []
    for path in paths:
        try:
            template = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            print(f"ERROR: Failed to parse {path.name}: {exc}")
            continue

        if not is_calibrated_local(template):
            continue

        try:
            template_id = template.get("template_id") or path.stem
            panel = extract_panel(template)

            # Top-level bridge warrant (use resolver)
            violation = check_confidence(
                template_id,
                "bridge_warrant",
                get_bridge_warrant(template),
                get_confidence(template),
                panel,
            )
            if violation:
                violations.append(violation)

            # Mechanism chain steps (use resolver)
            chain = get_mechanism_chain(template)
            for index, step in enumerate(chain, start=1):
                field_base = f"mechanism_chain[{index}]"
                step_warrant = resolve_field(step, "bridge_warrant") or resolve_field(step, "warrant")
                step_confidence = resolve_field(step, "confidence")
                ceiling_status = resolve_field(step, "ceiling_status")
                override_rationale = resolve_field(step, "ceiling_override_rationale")

                step_violation = check_confidence(
                    template_id,
                    f"{field_base}.confidence",
                    step_warrant,
                    step_confidence,
                    panel,
                    ceiling_status=ceiling_status,
                    ceiling_override_rationale=override_rationale,
                )
                if step_violation:
                    violations.append(step_violation)
        except Exception as e:
            # Skip corrupt entries gracefully
            print(f"SKIP (corrupt): {template_id} — {e}", file=__import__('sys').stderr)
            continue

    return violations


def write_report(total_templates: int, calibrated_templates: int, violations: List[Violation], output_path: Path) -> None:
    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_templates": total_templates,
        "calibrated_templates": calibrated_templates,
        "total_violations": len(violations),
        "violations": [violation.to_dict() for violation in violations],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Lint bridge warrant confidence ceilings (REPORTING ONLY)")
    parser.add_argument("--templates", default=TEMPLATES_DIR, help="Templates directory")
    parser.add_argument("--report", default=REPORT_PATH, help="Output report path")
    args = parser.parse_args()

    templates_dir = Path(args.templates)
    template_paths = sorted(templates_dir.glob("*.json"))
    violations = scan_templates(template_paths)
    total_templates = len(template_paths)

    # Count actual calibrated templates for accuracy
    calibrated_count = 0
    for path in template_paths:
        try:
            template = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if is_calibrated_local(template):
            calibrated_count += 1

    write_report(total_templates, calibrated_count, violations, Path(args.report))

    templates_with_violations = {violation.template_id for violation in violations}
    
    print("Bridge Ceiling Lint (E-02) - REPORTING ONLY")
    print("==================================================")
    print(f"Templates scanned: {total_templates}")
    print(f"Calibrated templates: {calibrated_count}")
    print(f"Violations: {len(violations)} ({len(templates_with_violations)} templates)")
    
    if violations:
        print("\nCEILING VIOLATIONS (reported but NOT auto-fixed):")
        print("-" * 120)
        
        # Separate by ceiling_status
        flagged = [v for v in violations if v.ceiling_status == "exceeds"]
        unflagged = [v for v in violations if v.ceiling_status != "exceeds"]
        
        if flagged:
            print(f"\nFLAGGED FOR PANEL REVIEW (ceiling_status='exceeds'): {len(flagged)}")
            for violation in flagged:
                status_marker = "★"  # Mark for panel attention
                print(
                    f"{status_marker} {violation.template_id.ljust(20)} | {violation.field_path.ljust(30)} | "
                    f"{violation.warrant:<20} | conf={violation.confidence:.2f} > ceil={violation.ceiling:.2f} (Δ={violation.delta:.3f})"
                )
        
        if unflagged:
            print(f"\nNOT FLAGGED (ceiling_status not set): {len(unflagged)}")
            for violation in unflagged:
                print(
                    f"  {violation.template_id.ljust(20)} | {violation.field_path.ljust(30)} | "
                    f"{violation.warrant:<20} | conf={violation.confidence:.2f} > ceil={violation.ceiling:.2f} (Δ={violation.delta:.3f})"
                )
        
        print(f"\nReport saved to {args.report}")
    else:
        print("No ceiling violations found.")
    
    print("\nNOTE: This script REPORTS violations but does NOT auto-fix them.")
    print("Violations flagged with ceiling_status='exceeds' have been restored")
    print("from their original (pre-clamp) values and should be reviewed by the panel.")


if __name__ == "__main__":
    main()
