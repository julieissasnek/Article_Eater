"""
CMR interaction matrix utilities.

Encodes known cross-template and within-template interaction effects for
Sprint 10 Task 2.3.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any


# Matrix 1: CREA2 interaction factors (Doc 65)
CREA2_INTERACTIONS = {
    "A": {"sub_additivity": 1.00, "convergent_penalty": 1.00},
    "B": {"sub_additivity": 1.00, "convergent_penalty": 1.00},
    "C": {"sub_additivity": 1.00, "convergent_penalty": 1.00},
    "A+B": {"sub_additivity": 0.84, "convergent_penalty": 1.15},
    "A+C": {"sub_additivity": 0.76, "convergent_penalty": 1.60},
    "B+C": {"sub_additivity": 0.80, "convergent_penalty": 1.10},
    "A+B+C": {"sub_additivity": 0.70, "convergent_penalty": 1.80},
}

# Matrix 2: convergence triad (L3 + MAT4 + VIEW1)
CONVERGENCE_TRIAD = {"L3", "MAT4", "VIEW1"}
CONVERGENCE_MULTIPLIERS = {2: 1.15, 3: 1.22}

# Matrix 3/4: pairwise interactions
PAIRWISE_INTERACTIONS = {
    frozenset({"VF1", "VF3"}): {
        "interaction_type": "checked_no_adjustment",
        "multiplier": 1.0,
        "note": "VF1 x VF3 additive; no adjustment",
    },
    frozenset({"VF3", "CREA2B"}): {
        "interaction_type": "single_chain",
        "from_template": "VF3",
        "to_template": "CREA2B",
        "compute_independently": False,
        "note": "Use VF3 output as CREA2B input",
    },
}


def _normalize_template_id(template_id: str) -> str:
    return template_id.strip().upper()


def get_interaction(template_a: str, template_b: str) -> dict | None:
    """Return interaction record if one exists, else None."""
    a = _normalize_template_id(template_a)
    b = _normalize_template_id(template_b)
    if a == b:
        return None

    pair = frozenset({a, b})
    if pair in PAIRWISE_INTERACTIONS:
        return deepcopy(PAIRWISE_INTERACTIONS[pair])

    if a in CONVERGENCE_TRIAD and b in CONVERGENCE_TRIAD:
        return {
            "interaction_type": "convergence_triad",
            "channels_active": 2,
            "multiplier": CONVERGENCE_MULTIPLIERS[2],
            "templates": sorted(CONVERGENCE_TRIAD),
        }

    return None


def _crea2_combo_key(score: dict[str, Any]) -> str | None:
    combo = score.get("channel_combo")
    if isinstance(combo, str) and combo:
        return combo

    active = score.get("active_channels")
    if isinstance(active, list) and active:
        parts = sorted(str(item).upper() for item in active)
        return "+".join(parts)

    return None


def apply_all_interactions(template_scores: list[dict]) -> list[dict]:
    """
    Apply known interaction effects and return adjusted score records.

    Each input item should include at minimum:
      {"template": str, "wis": float}
    """
    scores: list[dict[str, Any]] = deepcopy(template_scores)
    by_template: dict[str, dict[str, Any]] = {}

    for score in scores:
        template = _normalize_template_id(str(score.get("template", "")))
        if template:
            score["template"] = template
            score.setdefault("interaction_adjustments", [])
            by_template[template] = score

    # Matrix 1: CREA2 within-template adjustments
    crea2_score = by_template.get("CREA2")
    if crea2_score is not None:
        combo_key = _crea2_combo_key(crea2_score)
        if combo_key and combo_key in CREA2_INTERACTIONS:
            factors = CREA2_INTERACTIONS[combo_key]
            wis = float(crea2_score.get("wis", 0.0))
            adjusted = max(0.0, min(100.0, wis * factors["sub_additivity"]))
            crea2_score["wis"] = adjusted
            crea2_score["interaction_adjustments"].append(
                {
                    "type": "crea2_matrix",
                    "combo": combo_key,
                    "sub_additivity": factors["sub_additivity"],
                    "convergent_penalty": factors["convergent_penalty"],
                }
            )

    # Matrix 2: convergence triad multiplier
    active_triad = [name for name in CONVERGENCE_TRIAD if name in by_template]
    if len(active_triad) in CONVERGENCE_MULTIPLIERS:
        multiplier = CONVERGENCE_MULTIPLIERS[len(active_triad)]
        for template in active_triad:
            score = by_template[template]
            wis = float(score.get("wis", 0.0))
            score["wis"] = max(0.0, min(100.0, wis * multiplier))
            score["interaction_adjustments"].append(
                {
                    "type": "convergence_triad",
                    "channels_active": len(active_triad),
                    "multiplier": multiplier,
                    "templates": sorted(active_triad),
                }
            )

    # Matrix 3 and 4: pairwise checks
    if "VF1" in by_template and "VF3" in by_template:
        by_template["VF1"]["interaction_adjustments"].append(
            {
                "type": "checked_no_adjustment",
                "pair": ["VF1", "VF3"],
                "multiplier": 1.0,
            }
        )
        by_template["VF3"]["interaction_adjustments"].append(
            {
                "type": "checked_no_adjustment",
                "pair": ["VF1", "VF3"],
                "multiplier": 1.0,
            }
        )

    if "VF3" in by_template and "CREA2B" in by_template:
        by_template["CREA2B"]["interaction_adjustments"].append(
            {
                "type": "single_chain",
                "from_template": "VF3",
                "to_template": "CREA2B",
                "compute_independently": False,
            }
        )

    return scores

