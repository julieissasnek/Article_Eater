#!/usr/bin/env python3
"""Enrich template JSON files with required metadata defaults (Sprint 10 Task 3.4).

Adds missing fields only; never overwrites existing values:
- pe_contribution (default: "organizational")
- practical_accessibility (default: "B")
- dedup_status (Doc 67 map via template scanner classification)
- generation (T/M/AX=1, everything else=2)
- ecological_validation (default: false)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.cmr.template_scanner import classify_dedup_status

REQUIRED_FIELDS = (
    "pe_contribution",
    "practical_accessibility",
    "dedup_status",
    "generation",
    "ecological_validation",
)


def _extract_series(display_id: str) -> str:
    match = re.match(r"^([A-Z]+)", display_id or "")
    return match.group(1) if match else ""


def _infer_generation(series: str) -> int:
    return 1 if series in {"T", "M", "AX"} else 2


def enrich_template_data(data: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    updated = dict(data)
    added: list[str] = []

    display_id = str(updated.get("display_id", "")).strip()
    series = str(updated.get("series", "")).strip() or _extract_series(display_id)
    generation = _infer_generation(series)
    dedup_status, _ = classify_dedup_status(display_id, series, generation)

    if "pe_contribution" not in updated:
        updated["pe_contribution"] = "organizational"
        added.append("pe_contribution")

    if "practical_accessibility" not in updated:
        updated["practical_accessibility"] = "B"
        added.append("practical_accessibility")

    if "dedup_status" not in updated:
        updated["dedup_status"] = dedup_status
        added.append("dedup_status")

    if "generation" not in updated:
        updated["generation"] = generation
        added.append("generation")

    if "ecological_validation" not in updated:
        updated["ecological_validation"] = False
        added.append("ecological_validation")

    return updated, added


def enrich_templates_dir(templates_dir: Path) -> dict[str, Any]:
    json_files = sorted(templates_dir.glob("*.json"))
    changed_files = 0
    field_additions: Counter[str] = Counter()

    for path in json_files:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON in {path}: {exc}") from exc

        updated, added = enrich_template_data(data)
        if not added:
            continue

        changed_files += 1
        field_additions.update(added)
        path.write_text(json.dumps(updated, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    validation = validate_templates_dir(templates_dir)
    return {
        "total_files": len(json_files),
        "changed_files": changed_files,
        "field_additions": dict(field_additions),
        "validation": validation,
    }


def validate_templates_dir(templates_dir: Path) -> dict[str, Any]:
    json_files = sorted(templates_dir.glob("*.json"))
    missing: dict[str, list[str]] = {}
    parse_failures: list[str] = []

    for path in json_files:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            parse_failures.append(str(path))
            continue

        absent = [field for field in REQUIRED_FIELDS if field not in data]
        if absent:
            missing[str(path)] = absent

    return {
        "total_files": len(json_files),
        "parse_failures": parse_failures,
        "files_missing_required_fields": missing,
        "all_valid": not parse_failures and not missing,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Enrich template JSON files with required metadata fields.")
    parser.add_argument(
        "--templates-dir",
        default="data/templates",
        help="Path to template JSON directory (default: data/templates)",
    )
    args = parser.parse_args()

    templates_dir = Path(args.templates_dir)
    if not templates_dir.exists():
        print(f"ERROR: templates directory does not exist: {templates_dir}")
        return 1

    result = enrich_templates_dir(templates_dir)
    print(json.dumps(result, indent=2))

    return 0 if result["validation"]["all_valid"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
