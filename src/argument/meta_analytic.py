"""
Meta-analytic links and summary aggregation.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class MetaAnalyticLink:
    """Link between a meta-analysis paper and one included study."""

    meta_paper_id: str
    included_paper_id: str
    effect_size: float
    effect_size_ci: Tuple[float, float]
    weight: float
    sample_size: int
    moderators: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MetaAnalyticSummary:
    """Aggregated meta-analytic summary for a target outcome."""

    meta_paper_id: str
    outcome_construct: str
    included_studies: List[MetaAnalyticLink]
    k: int
    total_n: int
    pooled_effect: float
    pooled_ci: Tuple[float, float]
    i_squared: float
    q_statistic: float
    tau_squared: float
    moderator_effects: Dict[str, Dict[str, float]] = field(default_factory=dict)
    publication_bias_detected: bool = False
    egger_test_p: Optional[float] = None
    trim_and_fill_adjusted: Optional[float] = None


class MetaAnalyticAggregator:
    """Creates `MetaAnalyticSummary` from study-level links."""

    def summarize(
        self,
        meta_paper_id: str,
        outcome_construct: str,
        included_studies: List[MetaAnalyticLink],
    ) -> MetaAnalyticSummary:
        k = len(included_studies)
        total_n = sum(max(0, link.sample_size) for link in included_studies)

        if not included_studies:
            return MetaAnalyticSummary(
                meta_paper_id=meta_paper_id,
                outcome_construct=outcome_construct,
                included_studies=[],
                k=0,
                total_n=0,
                pooled_effect=0.0,
                pooled_ci=(0.0, 0.0),
                i_squared=0.0,
                q_statistic=0.0,
                tau_squared=0.0,
                moderator_effects={},
                publication_bias_detected=False,
            )

        weights = [self._effective_weight(link) for link in included_studies]
        effects = [link.effect_size for link in included_studies]
        sum_w = sum(weights) or 1.0

        pooled = sum(w * e for w, e in zip(weights, effects)) / sum_w
        se_pooled = math.sqrt(1.0 / sum_w)
        pooled_ci = (pooled - 1.96 * se_pooled, pooled + 1.96 * se_pooled)

        q_stat = sum(w * ((e - pooled) ** 2) for w, e in zip(weights, effects))
        df = max(0, k - 1)
        i_sq = 0.0 if q_stat <= 0 or df == 0 else max(0.0, ((q_stat - df) / q_stat) * 100.0)
        tau_sq = self._tau_squared(weights, q_stat, df)

        moderator_effects = self._compute_moderator_effects(included_studies)
        publication_bias_detected = self._detect_publication_bias(included_studies)

        return MetaAnalyticSummary(
            meta_paper_id=meta_paper_id,
            outcome_construct=outcome_construct,
            included_studies=included_studies,
            k=k,
            total_n=total_n,
            pooled_effect=round(pooled, 4),
            pooled_ci=(round(pooled_ci[0], 4), round(pooled_ci[1], 4)),
            i_squared=round(i_sq, 2),
            q_statistic=round(q_stat, 4),
            tau_squared=round(tau_sq, 6),
            moderator_effects=moderator_effects,
            publication_bias_detected=publication_bias_detected,
        )

    def _effective_weight(self, link: MetaAnalyticLink) -> float:
        if link.weight and link.weight > 0:
            return float(link.weight)

        ci_low, ci_high = link.effect_size_ci
        ci_width = max(1e-6, ci_high - ci_low)
        se = ci_width / 3.92
        return 1.0 / max(1e-9, se**2)

    def _tau_squared(self, weights: List[float], q_stat: float, df: int) -> float:
        if df <= 0:
            return 0.0
        sum_w = sum(weights)
        if sum_w <= 0:
            return 0.0
        correction = sum_w - (sum(w**2 for w in weights) / sum_w)
        if correction <= 0:
            return 0.0
        return max(0.0, (q_stat - df) / correction)

    def _compute_moderator_effects(
        self,
        included_studies: List[MetaAnalyticLink],
    ) -> Dict[str, Dict[str, float]]:
        buckets: Dict[str, Dict[str, List[Tuple[float, float]]]] = {}

        for link in included_studies:
            w = self._effective_weight(link)
            for key, value in link.moderators.items():
                level = str(value)
                buckets.setdefault(key, {}).setdefault(level, []).append((link.effect_size, w))

        output: Dict[str, Dict[str, float]] = {}
        for moderator, levels in buckets.items():
            output[moderator] = {}
            for level, values in levels.items():
                total_w = sum(weight for _, weight in values) or 1.0
                pooled = sum(effect * weight for effect, weight in values) / total_w
                output[moderator][level] = round(pooled, 4)
        return output

    def _detect_publication_bias(self, included_studies: List[MetaAnalyticLink]) -> bool:
        if len(included_studies) < 5:
            return False

        small_studies = [link for link in included_studies if link.sample_size <= 80]
        if not small_studies:
            return False

        large_studies = [link for link in included_studies if link.sample_size > 80]
        if not large_studies:
            return False

        mean_small = sum(link.effect_size for link in small_studies) / len(small_studies)
        mean_large = sum(link.effect_size for link in large_studies) / len(large_studies)
        return abs(mean_small - mean_large) >= 0.2
