#!/usr/bin/env python3
"""
Generate V12 Codex validation artifacts:
1) Schema validation for VIEW-II / CREA-II and related V12 metadata fields
2) Cross-reference reciprocity audit for Docs 56-59 source templates
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_DIR = ROOT / "data" / "templates"
REVIEW_DIR = ROOT / "data" / "review"
DOCS_DIR = ROOT / "docs"
DATE_TAG = "2026-02-17"


@dataclass
class TemplateRecord:
    path: Path
    data: Dict[str, Any]
    template_id: str
    display_id: str


@dataclass
class FieldSpec:
    name: str
    expected_display_ids: List[str]
    validator: Callable[[Any], Tuple[bool, str]]


def load_templates() -> List[TemplateRecord]:
    records: List[TemplateRecord] = []
    for path in sorted(TEMPLATE_DIR.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        template_id = str(data.get("template_id") or path.stem)
        display_id = str(data.get("display_id") or "")
        records.append(
            TemplateRecord(
                path=path,
                data=data,
                template_id=template_id,
                display_id=display_id,
            )
        )
    return records


def is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def validate_number_range(min_v: float, max_v: float) -> Callable[[Any], Tuple[bool, str]]:
    def _validate(value: Any) -> Tuple[bool, str]:
        if not is_number(value):
            return False, "expected numeric value"
        if value < min_v or value > max_v:
            return False, f"out of bounds [{min_v}, {max_v}]"
        return True, ""

    return _validate


def validate_non_empty_string(value: Any) -> Tuple[bool, str]:
    if isinstance(value, str) and value.strip():
        return True, ""
    return False, "expected non-empty string"


def validate_gate_range(value: Any) -> Tuple[bool, str]:
    if isinstance(value, dict):
        low = value.get("min")
        high = value.get("max")
    elif isinstance(value, (list, tuple)) and len(value) == 2:
        low, high = value
    else:
        return False, "expected {min,max} or [min,max]"

    if not is_number(low) or not is_number(high):
        return False, "range values must be numeric"
    if low > high:
        return False, "min greater than max"
    if low < 0.2 or high > 1.2:
        return False, "range outside [0.2, 1.2]"
    return True, ""


def validate_numeric_dict(min_v: float, max_v: float) -> Callable[[Any], Tuple[bool, str]]:
    def _validate(value: Any) -> Tuple[bool, str]:
        if not isinstance(value, dict) or not value:
            return False, "expected non-empty object"
        for key, item in value.items():
            if not is_number(item):
                return False, f"value for {key!r} must be numeric"
            if item < min_v or item > max_v:
                return False, f"value for {key!r} outside [{min_v}, {max_v}]"
        return True, ""

    return _validate


def validate_min_max_range(min_v: float, max_v: float) -> Callable[[Any], Tuple[bool, str]]:
    def _validate(value: Any) -> Tuple[bool, str]:
        if not isinstance(value, dict):
            return False, "expected object with min/max"
        low = value.get("min")
        high = value.get("max")
        if not is_number(low) or not is_number(high):
            return False, "min/max must be numeric"
        if low > high:
            return False, "min greater than max"
        if low < min_v or high > max_v:
            return False, f"range outside [{min_v}, {max_v}]"
        return True, ""

    return _validate


def validate_min_max_01(value: Any) -> Tuple[bool, str]:
    if not isinstance(value, dict):
        return False, "expected object with min/max"
    low = value.get("min")
    high = value.get("max")
    if not is_number(low) or not is_number(high):
        return False, "min/max must be numeric"
    if low > high:
        return False, "min greater than max"
    if low < 0.0 or high > 1.0:
        return False, "range outside [0.0, 1.0]"
    return True, ""


def validate_phase_durations(value: Any) -> Tuple[bool, str]:
    if not isinstance(value, dict):
        return False, "expected object with generation/selective/evaluation"
    required = ["generation", "selective", "evaluation"]
    missing = [k for k in required if k not in value]
    if missing:
        return False, f"missing phases: {', '.join(missing)}"
    for phase in required:
        item = value[phase]
        if not isinstance(item, dict):
            return False, f"{phase} must be object with mean/sd"
        mean = item.get("mean")
        sd = item.get("sd")
        if not is_number(mean) or not is_number(sd):
            return False, f"{phase} mean/sd must be numeric"
        if mean <= 0 or sd <= 0:
            return False, f"{phase} mean/sd must be positive"
    return True, ""


def validate_field_specs(templates: List[TemplateRecord]) -> Dict[str, Any]:
    specs = [
        FieldSpec("vqi_score", ["VIEW1"], validate_number_range(0.0, 100.0)),
        FieldSpec("synthetic_efficacy", ["VIEW1"], validate_numeric_dict(0.0, 1.2)),
        FieldSpec("ch5_gate_range", ["VIEW1"], validate_gate_range),
        FieldSpec(
            "blue_space_present",
            ["VIEW1"],
            lambda v: (isinstance(v, bool), "expected boolean"),
        ),
        FieldSpec("blue_bonus_multiplier", ["VIEW1"], validate_number_range(1.0, 1.25)),
        FieldSpec("pathway_d_values", ["CREA2"], validate_numeric_dict(-1.0, 1.0)),
        FieldSpec("combination_formula", ["CREA2"], validate_non_empty_string),
        FieldSpec(
            "creativity_goldilocks_ceiling",
            ["CREA1", "CREA2", "CREA3"],
            validate_number_range(0.0, 1.0),
        ),
        FieldSpec("two_pathway_optimum", ["CREA2"], validate_min_max_01),
        FieldSpec(
            "convergent_tradeoff_d",
            ["CREA1", "CREA2", "CREA3"],
            validate_numeric_dict(-1.0, 0.0),
        ),
        FieldSpec("phase_durations_s", ["CREA1"], validate_phase_durations),
        FieldSpec("walk_duration_optimal_min", ["CREA3"], validate_min_max_range(0, 120)),
        FieldSpec(
            "baseline_creativity_multiplier",
            ["CREA1", "CREA2", "CREA3"],
            validate_numeric_dict(0.0, 2.0),
        ),
        FieldSpec(
            "ecological_safety_gate",
            ["L3", "MAT4", "VIEW1"],
            validate_number_range(0.2, 1.2),
        ),
    ]

    by_display = {record.display_id: record for record in templates if record.display_id}

    result_fields: Dict[str, Any] = {}
    missing_total = 0
    invalid_total = 0

    for spec in specs:
        present_count = 0
        valid_count = 0
        invalid_count = 0
        invalid_entries = []
        displays_present = set()

        for record in templates:
            if spec.name not in record.data:
                continue

            present_count += 1
            if record.display_id:
                displays_present.add(record.display_id)

            ok, reason = spec.validator(record.data.get(spec.name))
            if ok:
                valid_count += 1
            else:
                invalid_count += 1
                invalid_entries.append(
                    {
                        "template_id": record.template_id,
                        "display_id": record.display_id,
                        "file": str(record.path.relative_to(ROOT)),
                        "reason": reason,
                        "value": record.data.get(spec.name),
                    }
                )

        missing_expected = []
        for display_id in spec.expected_display_ids:
            if display_id in by_display and display_id not in displays_present:
                missing_expected.append(display_id)

        missing_total += len(missing_expected)
        invalid_total += invalid_count

        result_fields[spec.name] = {
            "present_count": present_count,
            "valid_count": valid_count,
            "invalid_count": invalid_count,
            "expected_display_ids": spec.expected_display_ids,
            "missing_expected_display_ids": missing_expected,
            "invalid_entries": invalid_entries,
        }

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "template_files_scanned": len(templates),
        "fields": result_fields,
        "summary": {
            "missing_expected_total": missing_total,
            "invalid_values_total": invalid_total,
        },
    }


def interaction_candidates(item: Any) -> List[str]:
    if isinstance(item, str):
        return [item]
    if isinstance(item, dict):
        candidates = []
        for key in ("template_id", "template", "display_id"):
            value = item.get(key)
            if isinstance(value, str) and value.strip():
                candidates.append(value.strip())
        return candidates
    return []


def resolve_target(
    candidate: str,
    by_template_id: Dict[str, TemplateRecord],
    by_display_id: Dict[str, TemplateRecord],
) -> Optional[str]:
    if candidate in by_template_id:
        return candidate
    if candidate in by_display_id:
        return by_display_id[candidate].template_id
    return None


def run_v12_bidirectional_audit(templates: List[TemplateRecord]) -> Dict[str, Any]:
    source_display_ids = [
        "TP1",
        "TP2",
        "TP3",
        "TP4",
        "SOC1",
        "SOC2",
        "SOC3",
        "CREA1",
        "CREA2",
        "CREA3",
        "VIEW1",
    ]
    by_template_id = {record.template_id: record for record in templates}
    by_display_id = {record.display_id: record for record in templates if record.display_id}

    source_templates: List[TemplateRecord] = []
    source_missing: List[str] = []
    for display_id in source_display_ids:
        record = by_display_id.get(display_id)
        if record is None:
            source_missing.append(display_id)
        else:
            source_templates.append(record)

    all_edges = set()
    unresolved_targets = []

    for record in templates:
        interactions = record.data.get("interactions")
        if not isinstance(interactions, list):
            continue
        for item in interactions:
            candidates = interaction_candidates(item)
            resolved = None
            for candidate in candidates:
                resolved = resolve_target(candidate, by_template_id, by_display_id)
                if resolved:
                    break
            if resolved:
                all_edges.add((record.template_id, resolved))

    source_edges = []
    for record in source_templates:
        interactions = record.data.get("interactions")
        if not isinstance(interactions, list):
            continue
        for item in interactions:
            candidates = interaction_candidates(item)
            resolved = None
            chosen = None
            for candidate in candidates:
                maybe = resolve_target(candidate, by_template_id, by_display_id)
                if maybe:
                    resolved = maybe
                    chosen = candidate
                    break

            if not resolved:
                unresolved_targets.append(
                    {
                        "source_template_id": record.template_id,
                        "source_display_id": record.display_id,
                        "target_raw": candidates[0] if candidates else str(item),
                    }
                )
                continue

            source_edges.append(
                {
                    "source_template_id": record.template_id,
                    "source_display_id": record.display_id,
                    "target_template_id": resolved,
                    "target_raw": chosen,
                }
            )

    reciprocal_links = 0
    missing_reverse = []

    for edge in source_edges:
        source_id = edge["source_template_id"]
        target_id = edge["target_template_id"]
        if (target_id, source_id) in all_edges:
            reciprocal_links += 1
        else:
            target_display = (
                by_template_id.get(target_id).display_id
                if target_id in by_template_id
                else ""
            )
            missing_reverse.append(
                {
                    "source_template_id": source_id,
                    "source_display_id": edge["source_display_id"],
                    "target_template_id": target_id,
                    "target_display_id": target_display,
                }
            )

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_scope": {
            "docs": ["56", "57", "58", "59"],
            "source_display_ids": source_display_ids,
            "source_template_ids": [item.template_id for item in source_templates],
            "source_templates_found": len(source_templates),
            "source_templates_missing": source_missing,
        },
        "summary": {
            "source_edges_scanned": len(source_edges),
            "reciprocal_links": reciprocal_links,
            "missing_reverse_links": len(missing_reverse),
            "unresolved_targets": len(unresolved_targets),
        },
        "missing_reverse_links": missing_reverse,
        "unresolved_targets": unresolved_targets,
    }


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_schema_markdown(path: Path, payload: Dict[str, Any], json_path: Path) -> None:
    lines = [
        "# CX V12 Schema Validation Report",
        "",
        f"- Generated: {payload['generated_at']}",
        f"- Template files scanned: {payload['template_files_scanned']}",
        f"- Missing expected field assignments: {payload['summary']['missing_expected_total']}",
        f"- Invalid field values: {payload['summary']['invalid_values_total']}",
        "",
        "## Field Results",
        "",
        "| Field | Present | Valid | Invalid | Missing Expected Display IDs |",
        "|---|---:|---:|---:|---|",
    ]
    for name, result in payload["fields"].items():
        missing = ", ".join(result["missing_expected_display_ids"])
        lines.append(
            f"| `{name}` | {result['present_count']} | {result['valid_count']} | "
            f"{result['invalid_count']} | {missing} |"
        )

    lines.extend(
        [
            "",
            "## Findings",
            "",
        ]
    )
    for name, result in payload["fields"].items():
        missing = result["missing_expected_display_ids"]
        if missing:
            lines.append(
                f"- `{name}`: missing on expected templates {', '.join(missing)}."
            )
        if result["invalid_entries"]:
            lines.append(
                f"- `{name}`: invalid entries found ({len(result['invalid_entries'])})."
            )
    if not any(
        payload["fields"][field]["missing_expected_display_ids"]
        or payload["fields"][field]["invalid_entries"]
        for field in payload["fields"]
    ):
        lines.append("- No missing expected fields or invalid values detected.")

    lines.extend(
        [
            "",
            "## Artifacts",
            "",
            f"- JSON: `{json_path.relative_to(ROOT)}`",
            f"- Markdown: `{path.relative_to(ROOT)}`",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def write_audit_markdown(path: Path, payload: Dict[str, Any], json_path: Path) -> None:
    source_scope = payload["source_scope"]
    summary = payload["summary"]
    lines = [
        "# CX V12 Bidirectional Interaction Audit",
        "",
        f"- Generated: {payload['generated_at']}",
        "- Source docs: 56 (TP-II), 57 (SOC-II), 58 (CREA-II), 59 (VIEW-II)",
        (
            "- Source templates found: "
            f"{source_scope['source_templates_found']}/{len(source_scope['source_display_ids'])}"
        ),
        f"- Source edges scanned: {summary['source_edges_scanned']}",
        f"- Reciprocal links: {summary['reciprocal_links']}",
        f"- Missing reverse links: {summary['missing_reverse_links']}",
        f"- Unresolved targets: {summary['unresolved_targets']}",
        "",
        "## Artifacts",
        "",
        f"- JSON: `{json_path.relative_to(ROOT)}`",
        f"- Markdown: `{path.relative_to(ROOT)}`",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    templates = load_templates()

    schema_payload = validate_field_specs(templates)
    schema_json_path = REVIEW_DIR / f"cx_v12_schema_validation_{DATE_TAG}.json"
    schema_md_path = DOCS_DIR / f"cx_v12_schema_validation_report_{DATE_TAG}.md"
    write_json(schema_json_path, schema_payload)
    write_schema_markdown(schema_md_path, schema_payload, schema_json_path)

    audit_payload = run_v12_bidirectional_audit(templates)
    audit_json_path = REVIEW_DIR / f"cx_v12_bidirectional_audit_{DATE_TAG}.json"
    audit_md_path = DOCS_DIR / f"cx_v12_bidirectional_audit_report_{DATE_TAG}.md"
    write_json(audit_json_path, audit_payload)
    write_audit_markdown(audit_md_path, audit_payload, audit_json_path)

    print(f"Wrote: {schema_json_path.relative_to(ROOT)}")
    print(f"Wrote: {schema_md_path.relative_to(ROOT)}")
    print(f"Wrote: {audit_json_path.relative_to(ROOT)}")
    print(f"Wrote: {audit_md_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
