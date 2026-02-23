#!/usr/bin/env python3
"""Lint script for bridge warrant confidence ceilings (E-02)."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, List

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEMPLATES_DIR = PROJECT_ROOT / "data" / "templates"
REPORT_PATH = PROJECT_ROOT / "data" / "ceiling_violation_report.json"

CEILINGS = {
    "CONSTITUTIVE": 0.75,
    "MECHANISM": 0.60,
    "EMPIRICAL_COVARIANCE": 0.60,
    "FUNCTIONAL": 0.50,
    "CAPACITY": 0.45,
    "ANALOGICAL": 0.35,
    "THEORETICAL_DEFAULT": 0.40,
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

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def is_calibrated(template: dict[str, Any]) -> bool:
    status = (template.get("calibration_status") or template.get("status") or "").lower()
    if status == "calibrated":
        return True
    if template.get("calibrated") is True:
        return True
    return False


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

        if not is_calibrated(template):
            continue

        template_id = template.get("template_id") or path.stem
        panel = extract_panel(template)

        # Top-level bridge warrant
        violation = check_confidence(
            template_id,
            "bridge_warrant",
            template.get("bridge_warrant"),
            template.get("confidence"),
            panel,
        )
        if violation:
            violations.append(violation)

        # Mechanism chain steps
        chain = template.get("mechanism_chain") or template.get("mechanism_steps") or []
        for index, step in enumerate(chain, start=1):
            field_base = f"mechanism_chain[{index}]"
            step_warrant = step.get("warrant") or step.get("bridge_warrant")
            step_confidence = step.get("confidence")
            step_violation = check_confidence(
                template_id,
                f"{field_base}.confidence",
                step_warrant,
                step_confidence,
                panel,
            )
            if step_violation:
                violations.append(step_violation)

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
    parser = argparse.ArgumentParser(description="Lint bridge warrant confidence ceilings")
    parser.add_argument("--templates", default=TEMPLATES_DIR, help="Templates directory")
    parser.add_argument("--report", default=REPORT_PATH, help="Output report path")
    args = parser.parse_args()

    templates_dir = Path(args.templates)
    template_paths = sorted(templates_dir.glob("*.json"))
    violations = scan_templates(template_paths)
    total_templates = len(template_paths)
    calibrated_templates = len({v.template_id for v in violations})  # approx; re-evaluate below

    # Count actual calibrated templates for accuracy
    calibrated_count = 0
    for path in template_paths:
        try:
            template = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if is_calibrated(template):
            calibrated_count += 1

    write_report(total_templates, calibrated_count, violations, Path(args.report))

    templates_with_violations = {violation.template_id for violation in violations}
    print("Bridge Ceiling Lint (E-02)")
    print("==================================================")
    print(f"Templates scanned: {total_templates}")
    print(f"Calibrated templates: {calibrated_count}")
    print(f"Violations: {len(violations)} ({len(templates_with_violations)} templates)")
    for violation in violations:
        print(
            f"{violation.template_id.ljust(20)} | {violation.field_path.ljust(30)} | "
            f"{violation.warrant:<20} | conf={violation.confidence:.2f} <= ceil={violation.ceiling:.2f} (Δ={violation.delta:.3f})"
        )

    if violations:
        print(f"Report saved to {args.report}")
    else:
        print("No ceiling violations found.")


if __name__ == "__main__":
    main()
