"""Wellbeing Impact Score (WIS) conversion utilities.

Implements the conversion and aggregation rules defined in:
- Doc 67 Part 3 (WIS common metric)
- Doc 68 Part 4.3 (WIS conversion module)
"""

from __future__ import annotations

import math
from typing import Any

try:
    from scipy.stats import norm
except ImportError:  # pragma: no cover - exercised only when scipy is unavailable.
    norm = None


CONFIDENCE_WEIGHT_MAP: dict[str, float] = {
    "established": 1.0,
    "substantial": 1.0,
    "supported": 0.7,
    "partial": 0.7,
    "preliminary": 0.4,
    "expert_estimate": 0.4,
    "speculative": 0.2,
    "protocol": 0.2,
    "uncalibrated": 0.2,
}


def _clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def _norm_cdf(x: float) -> float:
    if norm is not None:
        return float(norm.cdf(x))
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def _resolve_weight(item: dict[str, Any]) -> float:
    raw_conf = item.get("calibration_confidence", item.get("confidence"))
    if isinstance(raw_conf, (int, float)):
        return max(0.0, float(raw_conf))
    if isinstance(raw_conf, str):
        return CONFIDENCE_WEIGHT_MAP.get(raw_conf.strip().lower(), 0.4)
    return 0.4


def cohens_d_to_wis(d: float) -> float:
    """Convert Cohen's d to WIS using the percentile-equivalent mapping."""
    return _clamp(_norm_cdf(float(d)) * 100.0)


def goldilocks_to_wis(value: float, zone_boundaries: dict) -> float:
    """Map a scalar value into WIS based on Goldilocks zone position.

    Expected boundaries:
    - optimal_min (required)
    - optimal_max (required)
    - extreme_low (optional)
    - extreme_high (optional)
    - optimal_point (optional)
    """
    optimal_min = float(zone_boundaries["optimal_min"])
    optimal_max = float(zone_boundaries["optimal_max"])
    if optimal_max <= optimal_min:
        raise ValueError("optimal_max must be greater than optimal_min")

    width = optimal_max - optimal_min
    extreme_low = float(zone_boundaries.get("extreme_low", optimal_min - width))
    extreme_high = float(zone_boundaries.get("extreme_high", optimal_max + width))
    optimal_point = zone_boundaries.get("optimal_point")
    if optimal_point is not None:
        optimal_point = float(optimal_point)

    x = float(value)

    # Extreme aversive zone (Doc 67: WIS 10-20)
    if x <= extreme_low or x >= extreme_high:
        return 15.0

    # Outside Goldilocks but not extreme (Doc 67: WIS 25-40)
    if x < optimal_min:
        span = max(optimal_min - extreme_low, 1e-9)
        t = (optimal_min - x) / span
        return _clamp(40.0 - (20.0 * t))
    if x > optimal_max:
        span = max(extreme_high - optimal_max, 1e-9)
        t = (x - optimal_max) / span
        return _clamp(40.0 - (20.0 * t))

    # In Goldilocks range: boundary (50-60) -> center (75-85)
    center = (optimal_min + optimal_max) / 2.0
    half_width = max(width / 2.0, 1e-9)
    rel_to_center = 1.0 - (abs(x - center) / half_width)
    base = 55.0 + (25.0 * _clamp(rel_to_center, 0.0, 1.0))

    # Optional optimal point bump toward 85-90.
    if optimal_point is not None and optimal_min <= optimal_point <= optimal_max:
        max_dist = max(abs(optimal_point - optimal_min), abs(optimal_max - optimal_point), 1e-9)
        optimal_proximity = 1.0 - (abs(x - optimal_point) / max_dist)
        base += 10.0 * _clamp(optimal_proximity, 0.0, 1.0)

    return _clamp(base)


def threshold_to_wis(value: float, threshold: float) -> float:
    """Map threshold distance to WIS using Doc 67 threshold buckets."""
    x = float(value)
    th = float(threshold)

    if th == 0.0:
        # Fall back to signed unit distance when threshold is zero.
        ratio = x
    else:
        ratio = (x - th) / abs(th)

    if ratio == 0.0:
        return 55.0

    # Below threshold by >50% (Doc 67: WIS 15-25)
    if ratio <= -0.5:
        if ratio <= -1.0:
            return 15.0
        t = (-ratio - 0.5) / 0.5
        return _clamp(25.0 - (10.0 * t))

    # Below threshold by <50% (Doc 67: WIS 30-45)
    if ratio < 0.0:
        t = (ratio + 0.5) / 0.5  # -0.5 -> 0, 0 -> 1
        return _clamp(30.0 + (15.0 * t))

    # Above threshold by moderate amount (Doc 67: WIS 65-75)
    if ratio < 0.5:
        t = ratio / 0.5
        return _clamp(65.0 + (10.0 * t))

    # Well above threshold (Doc 67: WIS 80-85)
    if ratio >= 1.5:
        return 85.0
    t = (ratio - 0.5) / 1.0
    return _clamp(80.0 + (5.0 * t))


def aggregate_domain_wis(template_scores: list[dict]) -> dict:
    """Aggregate template-level WIS scores via confidence-weighted average."""
    if not template_scores:
        return {
            "domain_wis": 0.0,
            "template_count": 0,
            "total_weight": 0.0,
            "method": "weighted_average",
        }

    weighted_sum = 0.0
    total_weight = 0.0

    for item in template_scores:
        if "wis" not in item:
            continue
        wis = _clamp(float(item["wis"]))
        weight = _resolve_weight(item)
        weighted_sum += wis * weight
        total_weight += weight

    if total_weight == 0.0:
        domain_wis = 0.0
    else:
        domain_wis = weighted_sum / total_weight

    return {
        "domain_wis": _clamp(domain_wis),
        "template_count": len(template_scores),
        "total_weight": total_weight,
        "method": "weighted_average",
    }


def aggregate_overall_wis(domain_scores: list[dict]) -> dict:
    """Aggregate domain-level WIS scores via geometric mean across domains."""
    values: list[float] = []
    severe_deficits: list[str] = []

    for item in domain_scores:
        if "domain_wis" in item:
            wis = float(item["domain_wis"])
        elif "wis" in item:
            wis = float(item["wis"])
        else:
            continue

        if wis < 0.0:
            raise ValueError("WIS values must be non-negative for geometric aggregation")
        values.append(wis)

        if wis < 30.0:
            domain_name = str(item.get("domain", f"domain_{len(values)}"))
            severe_deficits.append(domain_name)

    if not values:
        return {
            "overall_wis": 0.0,
            "domain_count": 0,
            "severe_deficits": [],
            "method": "geometric_mean",
        }

    if any(v == 0.0 for v in values):
        overall = 0.0
    else:
        overall = math.exp(sum(math.log(v) for v in values) / len(values))

    return {
        "overall_wis": _clamp(overall),
        "domain_count": len(values),
        "severe_deficits": severe_deficits,
        "method": "geometric_mean",
    }
