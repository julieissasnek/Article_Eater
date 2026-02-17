"""Building comparison mode (Sprint 12 Task 12.19)."""

from __future__ import annotations

from typing import Any

from src.cmr.building_eval import evaluate_building


def _domain_map(result: dict[str, Any]) -> dict[str, float]:
    mapped: dict[str, float] = {}
    for row in result.get("domain_scores", []) or []:
        domain = str(row.get("domain", ""))
        if not domain:
            continue
        mapped[domain] = float(row.get("wis", 0.0))
    return mapped


def compare_buildings(
    *,
    features_a: dict[str, Any],
    features_b: dict[str, Any],
    label_a: str = "Current",
    label_b: str = "Proposed",
    occupant_age: int = 35,
    db_path: str = "ae.db",
) -> dict[str, Any]:
    """Evaluate two building feature sets and compare outcomes."""
    eval_a = evaluate_building(
        building_context={"building_name": label_a},
        measured_features=features_a,
        occupant_profile={"age": occupant_age},
        db_path=db_path,
    )
    eval_b = evaluate_building(
        building_context={"building_name": label_b},
        measured_features=features_b,
        occupant_profile={"age": occupant_age},
        db_path=db_path,
    )

    domains_a = _domain_map(eval_a)
    domains_b = _domain_map(eval_b)
    all_domains = sorted(set(domains_a) | set(domains_b))

    domain_deltas = []
    for domain in all_domains:
        a_score = domains_a.get(domain, 0.0)
        b_score = domains_b.get(domain, 0.0)
        delta = b_score - a_score
        domain_deltas.append(
            {
                "domain": domain,
                "a_wis": round(a_score, 2),
                "b_wis": round(b_score, 2),
                "delta": round(delta, 2),
                "direction": "improved" if delta > 0 else ("regressed" if delta < 0 else "no_change"),
            }
        )

    domain_deltas.sort(key=lambda row: row["delta"], reverse=True)
    improvements = [row for row in domain_deltas if row["delta"] > 0][:3]
    regressions = sorted([row for row in domain_deltas if row["delta"] < 0], key=lambda row: row["delta"])[:3]

    active_a = set(eval_a.get("activated_templates", []) or [])
    active_b = set(eval_b.get("activated_templates", []) or [])

    overall_a = float(eval_a.get("overall_wis", 0.0))
    overall_b = float(eval_b.get("overall_wis", 0.0))
    overall_delta = overall_b - overall_a

    if overall_delta > 0:
        summary = f"{label_b} outperforms {label_a} by {overall_delta:.1f} WIS points."
    elif overall_delta < 0:
        summary = f"{label_b} underperforms {label_a} by {abs(overall_delta):.1f} WIS points."
    else:
        summary = f"{label_a} and {label_b} are tied on overall WIS."

    return {
        "labels": {"a": label_a, "b": label_b},
        "overall": {
            "a_wis": round(overall_a, 2),
            "b_wis": round(overall_b, 2),
            "delta": round(overall_delta, 2),
        },
        "per_domain_deltas": domain_deltas,
        "biggest_improvements": improvements,
        "biggest_regressions": regressions,
        "template_activity_changes": {
            "added_in_b": sorted(active_b - active_a),
            "removed_in_b": sorted(active_a - active_b),
            "shared_count": len(active_a & active_b),
        },
        "summary": summary,
        "evaluations": {"a": eval_a, "b": eval_b},
    }


__all__ = ["compare_buildings"]
