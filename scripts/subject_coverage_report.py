#!/usr/bin/env python3
"""Generate a snapshot of subject typing coverage from RuleGraph v2 events.

This script is intended to support governance and Ruthless-style reviews.
It reads the current graph store and subject overrides and emits a JSON
summary describing how many rules have key subject attributes populated.
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

from src.services.service_locator import get_graph_service
from src.services import admin_service


def compute_subject_coverage(events: list[dict], overrides: dict | None = None) -> dict:
    overrides = overrides or {}
    coverage_by_paper: dict[str, dict[str, int]] = {}
    global_totals = defaultdict(int)

    for ev in events:
        if ev.get("type") != "rulegraph_v2":
            continue
        paper_id = ev.get("paper_id", "<unknown>")
        paper_cov = coverage_by_paper.setdefault(
            paper_id,
            {
                "rules_total": 0,
                "with_age_band": 0,
                "with_culture_region": 0,
                "with_clinical_population": 0,
                "with_traits": 0,
                "with_moderators": 0,
            },
        )

        for r in ev.get("rules") or []:
            if not isinstance(r, dict):
                continue
            effective = admin_service._apply_subject_overrides_to_rule(paper_id, r, overrides)
            scope = effective.get("subject_scope") or {}
            moderators = effective.get("subject_moderators") or []

            demo = scope.get("demographics") or {}
            cult = scope.get("culture") or {}
            clin = scope.get("clinical_status") or {}
            traits = scope.get("traits_measured") or []

            has_age_band = bool(demo.get("age_band"))
            has_culture_region = bool(cult.get("region"))
            has_clinical_population = bool((clin.get("population") or "").strip())
            has_traits = any((t or {}).get("name") for t in traits)
            has_mods = bool(moderators)

            paper_cov["rules_total"] += 1
            global_totals["rules_total"] += 1
            if has_age_band:
                paper_cov["with_age_band"] += 1
                global_totals["with_age_band"] += 1
            if has_culture_region:
                paper_cov["with_culture_region"] += 1
                global_totals["with_culture_region"] += 1
            if has_clinical_population:
                paper_cov["with_clinical_population"] += 1
                global_totals["with_clinical_population"] += 1
            if has_traits:
                paper_cov["with_traits"] += 1
                global_totals["with_traits"] += 1
            if has_mods:
                paper_cov["with_moderators"] += 1
                global_totals["with_moderators"] += 1

    def _pct(num: int, den: int) -> float:
        return float(num) / float(den) if den else 0.0

    summary = {
        "global": {
            "rules_total": int(global_totals["rules_total"]),
            "with_age_band": int(global_totals["with_age_band"]),
            "with_culture_region": int(global_totals["with_culture_region"]),
            "with_clinical_population": int(global_totals["with_clinical_population"]),
            "with_traits": int(global_totals["with_traits"]),
            "with_moderators": int(global_totals["with_moderators"]),
        },
        "by_paper": {},
    }
    gt = summary["global"]["rules_total"]
    if gt:
        summary["global"]["pct_with_age_band"] = _pct(summary["global"]["with_age_band"], gt)
        summary["global"]["pct_with_culture_region"] = _pct(summary["global"]["with_culture_region"], gt)
        summary["global"]["pct_with_clinical_population"] = _pct(summary["global"]["with_clinical_population"], gt)
        summary["global"]["pct_with_traits"] = _pct(summary["global"]["with_traits"], gt)
        summary["global"]["pct_with_moderators"] = _pct(summary["global"]["with_moderators"], gt)
    else:
        summary["global"]["pct_with_age_band"] = 0.0
        summary["global"]["pct_with_culture_region"] = 0.0
        summary["global"]["pct_with_clinical_population"] = 0.0
        summary["global"]["pct_with_traits"] = 0.0
        summary["global"]["pct_with_moderators"] = 0.0

    for pid, cov in coverage_by_paper.items():
        rt = cov["rules_total"]
        entry = dict(cov)
        if rt:
            entry["pct_with_age_band"] = _pct(cov["with_age_band"], rt)
            entry["pct_with_culture_region"] = _pct(cov["with_culture_region"], rt)
            entry["pct_with_clinical_population"] = _pct(cov["with_clinical_population"], rt)
            entry["pct_with_traits"] = _pct(cov["with_traits"], rt)
            entry["pct_with_moderators"] = _pct(cov["with_moderators"], rt)
        else:
            entry["pct_with_age_band"] = 0.0
            entry["pct_with_culture_region"] = 0.0
            entry["pct_with_clinical_population"] = 0.0
            entry["pct_with_traits"] = 0.0
            entry["pct_with_moderators"] = 0.0
        summary["by_paper"][pid] = entry

    return summary


def main(output_path: str = "reports/subject_coverage_snapshot.json") -> None:
    store = get_graph_service()
    events = store.get_all_events()
    overrides = admin_service._load_subject_overrides()

    summary = compute_subject_coverage(events, overrides)
    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote subject coverage snapshot to {out_path}")


if __name__ == "__main__":
    main()
