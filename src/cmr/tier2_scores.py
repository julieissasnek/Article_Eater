"""Tier 2 construct scoring from Tier 1 template WIS (Sprint 12 Task 12.15)."""

from __future__ import annotations

from typing import Any

from src.cmr.reduction_api import reduce_theory


def compute_tier2_scores(
    template_wis: dict[str, float],
    *,
    theories: tuple[str, ...] = ("ART", "SRT", "Biophilia"),
) -> dict[str, dict[str, float]]:
    """
    Compute Tier 2 construct scores from template WIS values.

    For each construct:
      score = sum(template_wis * coverage) / sum(coverage_present)
    """
    normalized_wis = {str(k).strip().upper(): float(v) for k, v in template_wis.items()}
    tier2_scores: dict[str, dict[str, float]] = {}

    for theory in theories:
        reductions = reduce_theory(theory)
        if not reductions:
            continue

        theory_scores: dict[str, float] = {}
        for reduction in reductions:
            construct = str(reduction.get("construct", "")).strip()
            if not construct:
                continue

            weighted_sum = 0.0
            total_weight = 0.0
            for mapping in reduction.get("template_mappings", []) or []:
                template_id = str(mapping.get("template_id", "")).strip().upper()
                try:
                    coverage = float(mapping.get("coverage", 0.0) or 0.0)
                except (TypeError, ValueError):
                    coverage = 0.0

                if coverage <= 0.0:
                    continue
                if template_id not in normalized_wis:
                    continue

                weighted_sum += normalized_wis[template_id] * coverage
                total_weight += coverage

            if total_weight > 0.0:
                theory_scores[construct] = round(weighted_sum / total_weight, 1)

        if theory_scores:
            tier2_scores[theory] = theory_scores

    return tier2_scores


__all__ = ["compute_tier2_scores"]
