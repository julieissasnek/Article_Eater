#!/usr/bin/env python3
"""
Add missing reverse interaction links for CX V12 sources (Docs 56-59).
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_DIR = ROOT / "data" / "templates"
AUDIT_JSON = ROOT / "data" / "review" / "cx_v12_bidirectional_audit_2026-02-17.json"

TEMPLATE_ID_PATTERN = re.compile(r"\b[A-Z][A-Z0-9]+(?:_[A-Z0-9]+)+_\d{3}\b")
DISPLAY_ID_PATTERN = re.compile(r"\b(?:SOC|TP|SC|AX|VF|VIEW|COL|OLF|MAT|L|M|E|T|CREA|DT)\d+\b")
NATURE_TEXT = (
    "Reverse link added by CX V12 S3 remediation to satisfy "
    "bidirectional interaction encoding."
)


@dataclass
class TemplateRecord:
    path: Path
    template_id: str
    display_id: str


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any, indent: int) -> None:
    path.write_text(
        json.dumps(payload, indent=indent, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def detect_indent(text: str) -> int:
    match = re.search(r"\n( +)\"", text)
    if not match:
        return 2
    return len(match.group(1))


def load_templates() -> list[TemplateRecord]:
    records: list[TemplateRecord] = []
    for path in sorted(TEMPLATE_DIR.glob("*.json")):
        try:
            data = read_json(path)
        except Exception:
            continue
        template_id = str(data.get("template_id") or path.stem)
        display_id = str(data.get("display_id") or "")
        records.append(
            TemplateRecord(path=path, template_id=template_id, display_id=display_id)
        )
    return records


def parse_interaction_refs(interaction: Any) -> tuple[set[str], set[str]]:
    template_ids: set[str] = set()
    display_ids: set[str] = set()

    def parse_text(text: str) -> None:
        for match in TEMPLATE_ID_PATTERN.findall(text):
            template_ids.add(match)
        for match in DISPLAY_ID_PATTERN.findall(text):
            display_ids.add(match)

    if isinstance(interaction, str):
        parse_text(interaction)
        return template_ids, display_ids

    if isinstance(interaction, dict):
        for key in ("template_id", "display_id", "template"):
            value = interaction.get(key)
            if isinstance(value, str):
                parse_text(value)

    return template_ids, display_ids


def has_interaction(
    interactions: list[Any], source_template_id: str, source_display_id: str
) -> bool:
    for interaction in interactions:
        template_ids, display_ids = parse_interaction_refs(interaction)
        if source_template_id in template_ids or source_display_id in display_ids:
            return True
    return False


def main() -> None:
    audit = read_json(AUDIT_JSON)
    missing_reverse_links = audit.get("missing_reverse_links", [])
    if not isinstance(missing_reverse_links, list):
        raise RuntimeError("missing_reverse_links must be a list in audit JSON")

    templates = load_templates()
    by_template_id = {record.template_id: record for record in templates}

    rows_by_target_file: dict[Path, list[dict[str, str]]] = {}
    unresolved = 0
    for row in missing_reverse_links:
        target_template_id = row.get("target_template_id")
        if not isinstance(target_template_id, str):
            unresolved += 1
            continue
        target_record = by_template_id.get(target_template_id)
        if target_record is None:
            unresolved += 1
            continue
        rows_by_target_file.setdefault(target_record.path, []).append(row)

    files_changed = 0
    links_added = 0

    for target_path, rows in rows_by_target_file.items():
        raw = target_path.read_text(encoding="utf-8")
        indent = detect_indent(raw)
        doc = json.loads(raw)
        interactions = doc.get("interactions")
        if not isinstance(interactions, list):
            interactions = []
            doc["interactions"] = interactions

        touched = False
        for row in rows:
            source_template_id = row.get("source_template_id")
            source_display_id = row.get("source_display_id")
            if not isinstance(source_template_id, str) or not isinstance(
                source_display_id, str
            ):
                continue
            if has_interaction(interactions, source_template_id, source_display_id):
                continue
            interactions.append(
                {
                    "template_id": source_template_id,
                    "display_id": source_display_id,
                    "nature": NATURE_TEXT,
                }
            )
            links_added += 1
            touched = True

        if touched:
            write_json(target_path, doc, indent)
            files_changed += 1
            print(f"updated {target_path.relative_to(ROOT)}")

    print(
        "summary:",
        f"files_changed={files_changed},",
        f"links_added={links_added},",
        f"unresolved={unresolved}",
    )


if __name__ == "__main__":
    main()
