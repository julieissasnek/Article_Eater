"""Load template theory links from template causal links into a staging table."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from src.cmr.models import CMRStagingTheoryLink, create_tables, get_session


_THEORY_ALIASES = {
    "attention_restoration_theory": "ART",
    "stress_reduction_theory": "SRT",
    "prospect_refuge_theory": "BIOPHILIA",
    "biophilia": "BIOPHILIA",
    "art": "ART",
    "srt": "SRT",
}


def _normalize_theory_id(value: str | None) -> str:
    raw = (value or "").strip()
    if not raw:
        return ""
    key = raw.lower().replace("-", "_").replace(" ", "_")
    if key in _THEORY_ALIASES:
        return _THEORY_ALIASES[key]
    if len(raw) <= 6 and raw.isupper():
        return raw
    return raw.upper()


def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [str(item) for item in value if item is not None]
    return [str(value)]


def _collect_template_theories(payload: dict[str, Any]) -> list[str]:
    theories: set[str] = set()
    for key in ("framework_ids", "theory_links", "tier2_theory", "theory"):
        for raw in _as_list(payload.get(key)):
            normalized = _normalize_theory_id(raw)
            if normalized:
                theories.add(normalized)
    return sorted(theories)


def load_staging_theory_links(
    templates_dir: Path = Path("data/templates"),
    db_path: str = "ae.db",
    clear_existing: bool = True,
) -> dict[str, Any]:
    """Load one staging row per (template causal link x theory)."""
    create_tables(db_path)
    session = get_session(db_path)

    inserted = 0
    templates_scanned = 0
    templates_with_links = 0
    per_theory: Counter[str] = Counter()

    try:
        if clear_existing:
            session.query(CMRStagingTheoryLink).delete()
            session.commit()

        for template_path in sorted(templates_dir.glob("*.json")):
            templates_scanned += 1
            payload = json.loads(template_path.read_text(encoding="utf-8"))

            template_id = str(payload.get("template_id") or "").strip()
            display_id = str(payload.get("display_id") or "").strip()
            if not template_id or not display_id:
                continue

            causal_links = payload.get("causal_links", [])
            if not isinstance(causal_links, list) or not causal_links:
                continue
            templates_with_links += 1

            template_theories = _collect_template_theories(payload)
            if not template_theories:
                template_theories = ["UNSPECIFIED"]

            for link_index, link in enumerate(causal_links):
                if not isinstance(link, dict):
                    continue

                link_theories: set[str] = set()
                for key in ("theory", "theory_id", "tier2_theory"):
                    for raw in _as_list(link.get(key)):
                        normalized = _normalize_theory_id(raw)
                        if normalized:
                            link_theories.add(normalized)
                if not link_theories:
                    link_theories.update(template_theories)

                from_variable = link.get("from_variable") or link.get("from_entity")
                to_variable = link.get("to_variable") or link.get("to_entity")
                from_level = link.get("from_level")
                to_level = link.get("to_level")
                activity = link.get("activity")
                maturity = link.get("maturity")

                for theory_id in sorted(link_theories):
                    row = CMRStagingTheoryLink(
                        template_display_id=display_id,
                        template_id=template_id,
                        theory_id=theory_id,
                        link_index=link_index,
                        from_variable=str(from_variable) if from_variable else None,
                        to_variable=str(to_variable) if to_variable else None,
                        from_level=str(from_level) if from_level else None,
                        to_level=str(to_level) if to_level else None,
                        activity=str(activity) if activity else None,
                        maturity=str(maturity) if maturity else None,
                        source_json_path=str(template_path),
                    )
                    session.add(row)
                    inserted += 1
                    per_theory[theory_id] += 1

        session.commit()
    finally:
        session.close()

    return {
        "templates_scanned": templates_scanned,
        "templates_with_links": templates_with_links,
        "rows_inserted": inserted,
        "theory_counts": dict(sorted(per_theory.items())),
    }


def main() -> int:
    summary = load_staging_theory_links()
    print(
        f"Loaded {summary['rows_inserted']} staging theory links "
        f"from {summary['templates_with_links']} templates."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
