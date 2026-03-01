"""Interaction helpers for CMR template outputs.
"""

from __future__ import annotations

from itertools import combinations
from typing import Iterable

CREA2_INTERACTIONS = {
    "A": {"sub_additivity": 1.00, "convergent_penalty": 1.00},
    "B": {"sub_additivity": 1.00, "convergent_penalty": 1.00},
    "C": {"sub_additivity": 1.00, "convergent_penalty": 1.00},
    "A+B": {"sub_additivity": 0.84, "convergent_penalty": 1.15},
    "A+C": {"sub_additivity": 0.76, "convergent_penalty": 1.60},
    "B+C": {"sub_additivity": 0.80, "convergent_penalty": 1.10},
    "A+B+C": {"sub_additivity": 0.70, "convergent_penalty": 1.80},
}

CONVERGENCE_TRIAD = {"L3", "NMC1", "VIEW1"}
TRIAD_MULTIPLIERS = {2: 1.15, 3: 1.22}


def _normalize_pair(template_a: str, template_b: str) -> str:
    return "+".join(sorted((template_a, template_b)))


def get_interaction(template_a: str, template_b: str) -> dict | None:
    key = _normalize_pair(template_a, template_b)
    if key in CREA2_INTERACTIONS:
        return {"type": "crea2", **CREA2_INTERACTIONS[key]}
    if {template_a, template_b} == {"VF1", "VF3"}:
        return {"type": "vf_additive", "multiplier": 1.0, "status": "checked_no_adjustment"}
    if {template_a, template_b} == {"VF3", "CREA2B"}:
        return {"type": "vf3_chain", "single_chain": True}
    return None


def _clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def _apply_pair_interaction(score: dict, partner: str, record: dict) -> None:
    adjustments = score.setdefault("interaction_adjustments", [])
    if record["type"] == "crea2":
        factor = record["sub_additivity"]
        score["interaction_multiplier"] = score.get("interaction_multiplier", 1.0) * factor
        score["wis"] = _clamp(score["wis"] * factor)
        adjustments.append(
            {
                "type": "crea2",
                "partner": partner,
                "sub_additivity": factor,
                "convergent_penalty": record["convergent_penalty"],
            }
        )
    elif record["type"] == "vf3_chain":
        score["single_chain_with"] = partner
        adjustments.append({"type": "vf3_chain", "single_chain_with": partner})
    elif record["type"] == "vf_additive":
        adjustments.append(
            {
                "type": "vf_additive",
                "partner": partner,
                "multiplier": record["multiplier"],
                "status": record["status"],
            }
        )


def apply_all_interactions(template_scores: Iterable[dict]) -> list[dict]:
    scores = [{**score} for score in template_scores]
    name_to_score: dict[str, dict] = {}
    for score in scores:
        score.setdefault("interaction_adjustments", [])
        score.setdefault("interaction_multiplier", 1.0)
        name_to_score[score["template"]] = score

    active = set(name_to_score)
    triad_active = CONVERGENCE_TRIAD & active
    if len(triad_active) >= 2:
        multiplier = TRIAD_MULTIPLIERS.get(len(triad_active), 1.0)
        for template in triad_active:
            score = name_to_score[template]
            score["interaction_multiplier"] *= multiplier
            score["wis"] = _clamp(score["wis"] * multiplier)
            score["interaction_adjustments"].append(
                {"type": "convergence_triad", "multiplier": multiplier}
            )

    for template_a, template_b in combinations(active, 2):
        interaction = get_interaction(template_a, template_b)
        if not interaction:
            continue
        first = name_to_score[template_a]
        second = name_to_score[template_b]
        _apply_pair_interaction(first, template_b, interaction)
        _apply_pair_interaction(second, template_a, interaction)

    return [name_to_score[name] for name in [score["template"] for score in scores]]
