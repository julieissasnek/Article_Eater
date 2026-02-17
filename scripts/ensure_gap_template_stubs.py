#!/usr/bin/env python3
"""Ensure Doc 67 gap templates exist as JSON stubs and TemplateRecord rows (Task 3.5)."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.enrich_template_json_fields import enrich_template_data
from src.cmr.models import TemplateRecord, create_tables, get_session

GAP_TEMPLATE_IDS = ["T4", "T6", "T7", "T10", "T14", "T15", "T17", "T18", "T23", "T28"]
GAP_STUB_NOTE = "Awaiting calibration panel. See Doc 67 Part 1 for recommended panel."


def _extract_series(display_id: str) -> str:
    match = re.match(r"^([A-Z]+)", display_id or "")
    return match.group(1) if match else "T"


def _ensure_json_stub(path: Path, display_id: str) -> tuple[dict[str, Any], bool]:
    changed = False
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
    else:
        data = {
            "template_id": f"{display_id}_GAP_STUB_001",
            "display_id": display_id,
            "name": f"{display_id} Gap Template Stub",
            "series": _extract_series(display_id),
            "calibration_status": "uncalibrated",
            "parameters": [
                {"name": "mechanism_stub", "description": f"{display_id} mechanism stub from Doc 67"}
            ],
            "gap_stub_note": GAP_STUB_NOTE,
            "source_docs": "67",
        }
        changed = True

    enriched, added = enrich_template_data(data)
    if added:
        changed = True
        data = enriched
    else:
        data = enriched

    # Per Task 3.5 these are explicit gap templates.
    if data.get("dedup_status") != "gap":
        data["dedup_status"] = "gap"
        changed = True

    if "gap_stub_note" not in data:
        data["gap_stub_note"] = GAP_STUB_NOTE
        changed = True

    if changed:
        path.write_text(json.dumps(data, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    return data, changed


def _upsert_template_record(db_path: str, json_path: Path, data: dict[str, Any]) -> str:
    session = get_session(db_path)
    try:
        display_id = str(data["display_id"])
        existing = session.query(TemplateRecord).filter_by(display_id=display_id).one_or_none()
        if existing is None:
            existing = TemplateRecord(
                template_id=str(data.get("template_id", f"{display_id}_GAP_STUB_001")),
                display_id=display_id,
                name=str(data.get("name", f"{display_id} Gap Template Stub")),
                series=str(data.get("series") or _extract_series(display_id)),
                generation=int(data.get("generation", 1)),
                dedup_status="gap",
                superseded_by=data.get("superseded_by"),
                pe_contribution=str(data.get("pe_contribution", "organizational")),
                maturity=str(data.get("overall_maturity") or data.get("maturity") or "speculative"),
                calibration_status=str(data.get("calibration_status", "uncalibrated")),
                practical_accessibility=str(data.get("practical_accessibility", "B")),
                ecological_validation=bool(data.get("ecological_validation", False)),
                json_path=str(json_path),
                source_docs=str(data.get("source_docs", "67")),
            )
            session.add(existing)
            action = "inserted"
        else:
            existing.template_id = str(data.get("template_id", existing.template_id))
            existing.name = str(data.get("name", existing.name))
            existing.series = str(data.get("series") or existing.series or _extract_series(display_id))
            existing.generation = int(data.get("generation", existing.generation or 1))
            existing.dedup_status = "gap"
            existing.superseded_by = data.get("superseded_by")
            existing.pe_contribution = str(data.get("pe_contribution", existing.pe_contribution))
            existing.maturity = str(data.get("overall_maturity") or data.get("maturity") or existing.maturity)
            existing.calibration_status = str(data.get("calibration_status", existing.calibration_status))
            existing.practical_accessibility = str(
                data.get("practical_accessibility", existing.practical_accessibility)
            )
            existing.ecological_validation = bool(data.get("ecological_validation", existing.ecological_validation))
            existing.json_path = str(json_path)
            existing.source_docs = str(data.get("source_docs", existing.source_docs))
            action = "updated"
        session.commit()
        return action
    finally:
        session.close()


def ensure_gap_template_stubs(templates_dir: Path, db_path: str) -> dict[str, Any]:
    create_tables(db_path)
    templates_dir.mkdir(parents=True, exist_ok=True)

    file_changes = 0
    db_inserts = 0
    db_updates = 0

    for display_id in GAP_TEMPLATE_IDS:
        path = templates_dir / f"{display_id}.json"
        data, changed = _ensure_json_stub(path, display_id)
        if changed:
            file_changes += 1

        action = _upsert_template_record(db_path, path, data)
        if action == "inserted":
            db_inserts += 1
        else:
            db_updates += 1

    return {
        "gap_templates_processed": len(GAP_TEMPLATE_IDS),
        "json_files_changed": file_changes,
        "db_inserts": db_inserts,
        "db_updates": db_updates,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Ensure gap template stubs and DB records.")
    parser.add_argument("--templates-dir", default="data/templates")
    parser.add_argument("--db-path", default="ae.db")
    args = parser.parse_args()

    result = ensure_gap_template_stubs(Path(args.templates_dir), args.db_path)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

