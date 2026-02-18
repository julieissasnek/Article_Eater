"""Wellbeing Impact Score (WIS) conversion utilities.

Implements the conversion and aggregation rules defined in:
- Doc 67 Part 3 (WIS common metric)
- Doc 68 Part 4.3 (WIS conversion module)
- Sprint 13 Task 13.6 (Uncertainty-aware WIS)
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
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


# ==============================================================================
# Uncertainty-Aware WIS (Sprint 13 Task 13.6)
# ==============================================================================

# Uncertainty scaling by calibration status
CALIBRATION_UNCERTAINTY: dict[str, float] = {
    "established": 0.05,   # 5% uncertainty
    "substantial": 0.05,
    "supported": 0.10,
    "partial": 0.15,
    "preliminary": 0.20,
    "expert_estimate": 0.25,
    "speculative": 0.35,
    "protocol": 0.25,
    "uncalibrated": 0.50,  # 50% uncertainty
}

# Uncertainty scaling by measurement accessibility tier
TIER_UNCERTAINTY: dict[str, float] = {
    "A": 0.15,  # Visual observation - higher uncertainty
    "B": 0.10,  # Basic measurement
    "C": 0.05,  # Precision measurement
    "D": 0.03,  # Lab-grade measurement
}

# Uncertainty scaling by PE contribution type
PE_CONTRIBUTION_UNCERTAINTY: dict[str, float] = {
    "predictive": 0.05,       # Well-validated predictive model
    "explanatory": 0.10,      # Has explanatory backing
    "organizational": 0.15,   # Organizational heuristic
    "unknown": 0.20,
}


@dataclass
class UncertainWIS:
    """WIS score with uncertainty bounds."""

    wis: float
    wis_lower: float
    wis_upper: float
    confidence_width: float
    n_samples: int = 1000

    def to_dict(self) -> dict:
        return {
            "wis": self.wis,
            "wis_lower": self.wis_lower,
            "wis_upper": self.wis_upper,
            "confidence_width": self.confidence_width,
            "n_samples": self.n_samples,
        }


def _get_uncertainty_sd(
    base_wis: float,
    calibration_status: str | None = None,
    accessibility_tier: str | None = None,
    pe_contribution: str | None = None,
) -> float:
    """Compute combined uncertainty standard deviation."""
    # Parameter uncertainty from calibration
    cal_key = (calibration_status or "uncalibrated").lower().strip()
    param_uncertainty = CALIBRATION_UNCERTAINTY.get(cal_key, 0.25)

    # Measurement uncertainty from tier
    tier_key = (accessibility_tier or "A").upper().strip()
    meas_uncertainty = TIER_UNCERTAINTY.get(tier_key, 0.15)

    # Model uncertainty from PE contribution
    pe_key = (pe_contribution or "unknown").lower().strip()
    model_uncertainty = PE_CONTRIBUTION_UNCERTAINTY.get(pe_key, 0.15)

    # Combine uncertainties (root sum of squares)
    combined_uncertainty = math.sqrt(
        param_uncertainty ** 2 + meas_uncertainty ** 2 + model_uncertainty ** 2
    )

    # Convert to standard deviation in WIS units
    # Uncertainty is expressed as fraction of base WIS
    sd = base_wis * combined_uncertainty
    return max(sd, 1.0)  # Minimum 1 WIS point SD


def compute_uncertain_wis(
    base_wis: float,
    calibration_status: str | None = None,
    accessibility_tier: str | None = None,
    pe_contribution: str | None = None,
    n_samples: int = 1000,
    confidence_level: float = 0.95,
) -> UncertainWIS:
    """
    Compute WIS with uncertainty bounds using Monte Carlo sampling.

    Args:
        base_wis: Point estimate of WIS
        calibration_status: Template calibration status
        accessibility_tier: Input accessibility tier (A/B/C/D)
        pe_contribution: PE contribution type (predictive/explanatory/organizational)
        n_samples: Number of Monte Carlo samples
        confidence_level: Confidence level for bounds (default 0.95)

    Returns:
        UncertainWIS with point estimate and confidence interval
    """
    base_wis = _clamp(base_wis)
    sd = _get_uncertainty_sd(base_wis, calibration_status, accessibility_tier, pe_contribution)

    # Monte Carlo sampling
    samples = []
    for _ in range(n_samples):
        sample = random.gauss(base_wis, sd)
        samples.append(_clamp(sample))

    samples.sort()

    # Compute confidence interval
    alpha = 1.0 - confidence_level
    lower_idx = int(n_samples * (alpha / 2))
    upper_idx = int(n_samples * (1 - alpha / 2)) - 1
    lower_idx = max(0, min(lower_idx, n_samples - 1))
    upper_idx = max(0, min(upper_idx, n_samples - 1))

    wis_lower = samples[lower_idx]
    wis_upper = samples[upper_idx]

    return UncertainWIS(
        wis=base_wis,
        wis_lower=wis_lower,
        wis_upper=wis_upper,
        confidence_width=wis_upper - wis_lower,
        n_samples=n_samples,
    )


def aggregate_domain_wis_uncertain(
    template_scores: list[dict],
    n_samples: int = 1000,
    confidence_level: float = 0.95,
) -> dict:
    """
    Aggregate template-level WIS scores with uncertainty propagation.

    Each template score dict should include:
    - wis: float
    - calibration_confidence or confidence: str or float
    - accessibility_tier (optional): str
    - pe_contribution (optional): str

    Returns dict with domain_wis, domain_wis_lower, domain_wis_upper, confidence_width
    """
    if not template_scores:
        return {
            "domain_wis": 0.0,
            "domain_wis_lower": 0.0,
            "domain_wis_upper": 0.0,
            "confidence_width": 0.0,
            "template_count": 0,
            "method": "uncertain_weighted_average",
        }

    # Compute uncertain WIS for each template
    uncertain_scores = []
    weights = []
    for item in template_scores:
        if "wis" not in item:
            continue
        base_wis = _clamp(float(item["wis"]))
        weight = _resolve_weight(item)

        # Extract uncertainty parameters
        cal_status = item.get("calibration_status") or item.get("calibration_confidence")
        if isinstance(cal_status, (int, float)):
            cal_status = None  # numeric confidence doesn't map to status
        tier = item.get("accessibility_tier", "B")
        pe = item.get("pe_contribution")

        uncertain = compute_uncertain_wis(
            base_wis=base_wis,
            calibration_status=cal_status,
            accessibility_tier=tier,
            pe_contribution=pe,
            n_samples=n_samples,
        )
        uncertain_scores.append(uncertain)
        weights.append(weight)

    if not uncertain_scores:
        return {
            "domain_wis": 0.0,
            "domain_wis_lower": 0.0,
            "domain_wis_upper": 0.0,
            "confidence_width": 0.0,
            "template_count": 0,
            "method": "uncertain_weighted_average",
        }

    # Monte Carlo aggregation
    aggregated_samples = []
    for sample_idx in range(n_samples):
        # Sample from each template's distribution
        weighted_sum = 0.0
        total_weight = 0.0
        for i, (uncertain, weight) in enumerate(zip(uncertain_scores, weights)):
            sd = _get_uncertainty_sd(
                uncertain.wis,
                template_scores[i].get("calibration_status"),
                template_scores[i].get("accessibility_tier"),
                template_scores[i].get("pe_contribution"),
            )
            sampled_wis = _clamp(random.gauss(uncertain.wis, sd))
            weighted_sum += sampled_wis * weight
            total_weight += weight

        if total_weight > 0:
            aggregated_samples.append(weighted_sum / total_weight)
        else:
            aggregated_samples.append(0.0)

    aggregated_samples.sort()

    # Point estimate (weighted mean of point estimates)
    total_weight = sum(weights)
    if total_weight > 0:
        domain_wis = sum(u.wis * w for u, w in zip(uncertain_scores, weights)) / total_weight
    else:
        domain_wis = 0.0

    # Confidence interval
    alpha = 1.0 - confidence_level
    lower_idx = int(n_samples * (alpha / 2))
    upper_idx = int(n_samples * (1 - alpha / 2)) - 1
    lower_idx = max(0, min(lower_idx, n_samples - 1))
    upper_idx = max(0, min(upper_idx, n_samples - 1))

    return {
        "domain_wis": _clamp(domain_wis),
        "domain_wis_lower": _clamp(aggregated_samples[lower_idx]),
        "domain_wis_upper": _clamp(aggregated_samples[upper_idx]),
        "confidence_width": aggregated_samples[upper_idx] - aggregated_samples[lower_idx],
        "template_count": len(uncertain_scores),
        "total_weight": total_weight,
        "method": "uncertain_weighted_average",
    }


def aggregate_overall_wis_uncertain(
    domain_scores: list[dict],
    n_samples: int = 1000,
    confidence_level: float = 0.95,
) -> dict:
    """
    Aggregate domain-level WIS scores via geometric mean with uncertainty.

    Each domain score dict should include domain_wis (and optionally uncertainty params).

    Returns dict with overall_wis, overall_wis_lower, overall_wis_upper, confidence_width
    """
    if not domain_scores:
        return {
            "overall_wis": 0.0,
            "overall_wis_lower": 0.0,
            "overall_wis_upper": 0.0,
            "confidence_width": 0.0,
            "domain_count": 0,
            "severe_deficits": [],
            "method": "uncertain_geometric_mean",
        }

    # Extract domain WIS values and their uncertainty bounds
    domain_values = []
    for item in domain_scores:
        if "domain_wis" in item:
            wis = float(item["domain_wis"])
            lower = float(item.get("domain_wis_lower", wis * 0.8))
            upper = float(item.get("domain_wis_upper", wis * 1.2))
        elif "wis" in item:
            wis = float(item["wis"])
            lower = float(item.get("wis_lower", wis * 0.8))
            upper = float(item.get("wis_upper", wis * 1.2))
        else:
            continue

        domain_values.append({
            "wis": _clamp(wis, 0.1),  # Avoid zero for geometric mean
            "lower": _clamp(lower, 0.1),
            "upper": _clamp(upper),
            "name": str(item.get("domain", f"domain_{len(domain_values)}")),
        })

    if not domain_values:
        return {
            "overall_wis": 0.0,
            "overall_wis_lower": 0.0,
            "overall_wis_upper": 0.0,
            "confidence_width": 0.0,
            "domain_count": 0,
            "severe_deficits": [],
            "method": "uncertain_geometric_mean",
        }

    # Monte Carlo geometric mean sampling
    geo_samples = []
    for _ in range(n_samples):
        log_sum = 0.0
        for dv in domain_values:
            # Sample from uniform between lower and upper
            sampled = random.uniform(dv["lower"], dv["upper"])
            sampled = max(sampled, 0.1)  # Ensure positive
            log_sum += math.log(sampled)

        geo_mean = math.exp(log_sum / len(domain_values))
        geo_samples.append(_clamp(geo_mean))

    geo_samples.sort()

    # Point estimate (geometric mean of point estimates)
    if all(dv["wis"] > 0 for dv in domain_values):
        log_sum = sum(math.log(dv["wis"]) for dv in domain_values)
        overall_wis = math.exp(log_sum / len(domain_values))
    else:
        overall_wis = 0.0

    # Severe deficits
    severe_deficits = [dv["name"] for dv in domain_values if dv["wis"] < 30.0]

    # Confidence interval
    alpha = 1.0 - confidence_level
    lower_idx = int(n_samples * (alpha / 2))
    upper_idx = int(n_samples * (1 - alpha / 2)) - 1
    lower_idx = max(0, min(lower_idx, n_samples - 1))
    upper_idx = max(0, min(upper_idx, n_samples - 1))

    return {
        "overall_wis": _clamp(overall_wis),
        "overall_wis_lower": _clamp(geo_samples[lower_idx]),
        "overall_wis_upper": _clamp(geo_samples[upper_idx]),
        "confidence_width": geo_samples[upper_idx] - geo_samples[lower_idx],
        "domain_count": len(domain_values),
        "severe_deficits": severe_deficits,
        "method": "uncertain_geometric_mean",
    }


def get_uncertainty_breakdown(
    base_wis: float,
    calibration_status: str | None = None,
    accessibility_tier: str | None = None,
    pe_contribution: str | None = None,
) -> dict:
    """
    Get detailed breakdown of uncertainty sources.

    Returns dict showing contribution from each uncertainty source.
    """
    cal_key = (calibration_status or "uncalibrated").lower().strip()
    tier_key = (accessibility_tier or "A").upper().strip()
    pe_key = (pe_contribution or "unknown").lower().strip()

    param_uncertainty = CALIBRATION_UNCERTAINTY.get(cal_key, 0.25)
    meas_uncertainty = TIER_UNCERTAINTY.get(tier_key, 0.15)
    model_uncertainty = PE_CONTRIBUTION_UNCERTAINTY.get(pe_key, 0.15)

    combined = math.sqrt(
        param_uncertainty ** 2 + meas_uncertainty ** 2 + model_uncertainty ** 2
    )

    return {
        "base_wis": base_wis,
        "parameter_uncertainty": {
            "source": "calibration_status",
            "value": calibration_status or "uncalibrated",
            "uncertainty_fraction": param_uncertainty,
            "wis_sd": base_wis * param_uncertainty,
        },
        "measurement_uncertainty": {
            "source": "accessibility_tier",
            "value": accessibility_tier or "A",
            "uncertainty_fraction": meas_uncertainty,
            "wis_sd": base_wis * meas_uncertainty,
        },
        "model_uncertainty": {
            "source": "pe_contribution",
            "value": pe_contribution or "unknown",
            "uncertainty_fraction": model_uncertainty,
            "wis_sd": base_wis * model_uncertainty,
        },
        "combined_uncertainty_fraction": combined,
        "combined_wis_sd": base_wis * combined,
    }
