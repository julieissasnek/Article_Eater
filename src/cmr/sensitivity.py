"""
Sensitivity Analysis Tool (Sprint 12 Task 12.20).

For each input feature, compute WIS delta from worst to best plausible value.
Rank features by impact. Include diminishing returns detection.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional
import copy
import random

from src.cmr.building_eval import evaluate_building


# Feature ranges: (worst, best, unit, description)
# These represent plausible ranges for typical buildings
FEATURE_RANGES: dict[str, dict[str, Any]] = {
    "ceiling_height_m": {
        "worst": 2.4,
        "best": 4.0,
        "unit": "m",
        "description": "Ceiling height",
        "category": "spatial",
    },
    "floor_area_m2": {
        "worst": 8.0,
        "best": 40.0,
        "unit": "m²",
        "description": "Floor area per person",
        "category": "spatial",
    },
    "illuminance_lux": {
        "worst": 150,
        "best": 500,
        "unit": "lux",
        "description": "Illuminance level",
        "category": "light",
    },
    "ambient_noise_dba": {
        "worst": 65,
        "best": 35,
        "unit": "dBA",
        "description": "Ambient noise level",
        "category": "acoustic",
        "inverted": True,  # Lower is better
    },
    "window_area_ratio": {
        "worst": 0.1,
        "best": 0.4,
        "unit": "ratio",
        "description": "Window-to-wall ratio",
        "category": "light",
    },
    "rt60_seconds": {
        "worst": 1.2,
        "best": 0.5,
        "unit": "s",
        "description": "Reverberation time",
        "category": "acoustic",
        "inverted": True,  # Lower is better for most spaces
    },
    "operative_temp_c": {
        "worst": 28.0,
        "best": 22.0,
        "unit": "°C",
        "description": "Operative temperature",
        "category": "thermal",
        "optimal": 22.0,  # Has optimal value
    },
    "density_m2_per_person": {
        "worst": 4.0,
        "best": 15.0,
        "unit": "m²/person",
        "description": "Space density",
        "category": "spatial",
    },
}

# Categorical features with impact estimates
CATEGORICAL_FEATURES: dict[str, dict[str, Any]] = {
    "has_nature_view": {
        "worst": False,
        "best": True,
        "description": "Nature view available",
        "category": "view",
        "estimated_delta": 12.0,
    },
    "view_content": {
        "worst": "interior_only",
        "best": "nature_with_water",
        "description": "View content quality",
        "category": "view",
        "estimated_delta": 15.0,
    },
    "primary_material": {
        "worst": "concrete",
        "best": "wood",
        "description": "Primary surface material",
        "category": "material",
        "estimated_delta": 8.0,
    },
    "privacy_visual": {
        "worst": "none",
        "best": "high",
        "description": "Visual privacy level",
        "category": "social",
        "estimated_delta": 6.0,
    },
    "privacy_acoustic": {
        "worst": "none",
        "best": "high",
        "description": "Acoustic privacy level",
        "category": "social",
        "estimated_delta": 8.0,
    },
}


@dataclass
class FeatureSensitivity:
    """Sensitivity analysis result for a single feature."""

    feature: str
    description: str
    category: str
    worst_value: Any
    best_value: Any
    unit: str
    wis_at_worst: float
    wis_at_best: float
    wis_delta: float
    expected_delta: float = 0.0
    improvement_probability: float = 0.5
    delta_ci_lower: float = 0.0
    delta_ci_upper: float = 0.0
    actionability_score: float = 0.0
    rank: int = 0
    diminishing_returns: bool = False
    diminishing_threshold: Optional[float] = None


@dataclass
class SensitivityResult:
    """Complete sensitivity analysis result."""

    baseline_wis: float
    feature_sensitivities: list[FeatureSensitivity] = field(default_factory=list)
    top_recommendation: str = ""
    top_feature: str = ""
    top_delta: float = 0.0
    top_probability: float = 0.0
    category_impacts: dict[str, float] = field(default_factory=dict)
    monte_carlo_samples: int = 1000


def _evaluate_with_feature(
    base_features: dict,
    occupant_profile: dict,
    feature_name: str,
    feature_value: Any,
    db_path: str = "ae.db",
) -> float:
    """Evaluate building with a specific feature value and return overall WIS."""
    features = copy.deepcopy(base_features)
    features[feature_name] = feature_value

    building_context = {
        "building_type": "sensitivity_analysis",
        "building_name": f"Sensitivity test: {feature_name}={feature_value}",
    }

    try:
        result = evaluate_building(
            building_context=building_context,
            measured_features=features,
            occupant_profile=occupant_profile,
            db_path=db_path,
        )
        return result.get("overall_wis", 50.0)
    except Exception:
        return 50.0  # Neutral on error


def _check_diminishing_returns(
    base_features: dict,
    occupant_profile: dict,
    feature_name: str,
    worst: float,
    best: float,
    db_path: str = "ae.db",
) -> tuple[bool, Optional[float]]:
    """Check if feature has diminishing returns by testing intermediate values."""
    if not isinstance(worst, (int, float)) or not isinstance(best, (int, float)):
        return False, None

    # Test 5 points from worst to best
    points = 5
    step = (best - worst) / (points - 1)
    values = [worst + i * step for i in range(points)]

    wis_values = []
    for val in values:
        wis = _evaluate_with_feature(base_features, occupant_profile, feature_name, val, db_path)
        wis_values.append((val, wis))

    # Check for diminishing returns: if last 20% of range gives < 20% of total improvement
    if len(wis_values) >= 3:
        total_improvement = wis_values[-1][1] - wis_values[0][1]
        if abs(total_improvement) < 1.0:
            return False, None

        last_segment_improvement = wis_values[-1][1] - wis_values[-2][1]
        first_segment_improvement = wis_values[1][1] - wis_values[0][1]

        # Diminishing returns if first segment improvement > 2x last segment improvement
        if abs(first_segment_improvement) > 0 and abs(last_segment_improvement) > 0:
            if first_segment_improvement / last_segment_improvement > 2.0:
                # Find approximate threshold where returns start diminishing
                threshold = values[len(values) // 2]
                return True, threshold

    return False, None


def _simulate_delta_distribution(
    wis_worst: float,
    wis_best: float,
    *,
    baseline_confidence: float,
    n_samples: int,
    seed: int,
) -> tuple[float, float, float, float]:
    """
    Estimate uncertainty-aware impact via Monte Carlo.

    Returns:
        (expected_delta, probability_improvement, ci_lower, ci_upper)
    """
    # Lower confidence widens the uncertainty on scenario outcomes.
    sigma = max(1.5, (1.0 - baseline_confidence) * 15.0)
    rng = random.Random(seed)
    deltas: list[float] = []
    for _ in range(n_samples):
        worst = rng.gauss(wis_worst, sigma)
        best = rng.gauss(wis_best, sigma)
        deltas.append(best - worst)

    deltas.sort()
    expected = sum(deltas) / len(deltas)
    improvement_probability = sum(1 for d in deltas if d > 0.0) / len(deltas)
    lower_idx = int(0.025 * len(deltas))
    upper_idx = int(0.975 * len(deltas)) - 1
    lower_idx = max(0, min(lower_idx, len(deltas) - 1))
    upper_idx = max(0, min(upper_idx, len(deltas) - 1))
    return expected, improvement_probability, deltas[lower_idx], deltas[upper_idx]


def analyze_sensitivity(
    measured_features: dict,
    occupant_profile: dict | None = None,
    db_path: str = "ae.db",
    check_diminishing: bool = True,
    monte_carlo_samples: int = 1000,
) -> SensitivityResult:
    """
    Analyze sensitivity of WIS to each input feature.

    For each feature with a defined range, computes the WIS delta from
    worst to best plausible value. Ranks features by impact.

    Args:
        measured_features: Current building measurements
        occupant_profile: Occupant characteristics (age, etc.)
        db_path: Path to database
        check_diminishing: Whether to check for diminishing returns (slower)

    Returns:
        SensitivityResult with ranked feature impacts
    """
    occupant_profile = occupant_profile or {"age": 35}

    # Compute baseline WIS
    building_context = {
        "building_type": "sensitivity_baseline",
        "building_name": "Sensitivity Analysis Baseline",
    }

    try:
        baseline_result = evaluate_building(
            building_context=building_context,
            measured_features=measured_features,
            occupant_profile=occupant_profile,
            db_path=db_path,
        )
        baseline_wis = baseline_result.get("overall_wis", 50.0)
        baseline_confidence = float(baseline_result.get("overall_confidence", 0.5))
    except Exception:
        baseline_wis = 50.0
        baseline_confidence = 0.5

    sensitivities: list[FeatureSensitivity] = []
    category_deltas: dict[str, list[float]] = {}

    # Analyze continuous features
    for feature_name, config in FEATURE_RANGES.items():
        worst = config["worst"]
        best = config["best"]
        unit = config.get("unit", "")
        description = config.get("description", feature_name)
        category = config.get("category", "other")

        # Compute WIS at worst and best
        wis_worst = _evaluate_with_feature(
            measured_features, occupant_profile, feature_name, worst, db_path
        )
        wis_best = _evaluate_with_feature(
            measured_features, occupant_profile, feature_name, best, db_path
        )

        wis_delta = wis_best - wis_worst
        expected_delta, improvement_probability, ci_lower, ci_upper = _simulate_delta_distribution(
            wis_worst,
            wis_best,
            baseline_confidence=baseline_confidence,
            n_samples=monte_carlo_samples,
            seed=abs(hash((feature_name, "continuous"))) % (2**32),
        )
        actionability_score = max(0.0, expected_delta) * improvement_probability

        # Check for diminishing returns on significant features
        diminishing = False
        threshold = None
        if check_diminishing and abs(wis_delta) > 3.0:
            diminishing, threshold = _check_diminishing_returns(
                measured_features, occupant_profile, feature_name, worst, best, db_path
            )

        sensitivity = FeatureSensitivity(
            feature=feature_name,
            description=description,
            category=category,
            worst_value=worst,
            best_value=best,
            unit=unit,
            wis_at_worst=wis_worst,
            wis_at_best=wis_best,
            wis_delta=wis_delta,
            expected_delta=expected_delta,
            improvement_probability=improvement_probability,
            delta_ci_lower=ci_lower,
            delta_ci_upper=ci_upper,
            actionability_score=actionability_score,
            diminishing_returns=diminishing,
            diminishing_threshold=threshold,
        )
        sensitivities.append(sensitivity)

        if category not in category_deltas:
            category_deltas[category] = []
        category_deltas[category].append(abs(wis_delta))

    # Analyze categorical features (estimate based on configured delta)
    for feature_name, config in CATEGORICAL_FEATURES.items():
        worst = config["worst"]
        best = config["best"]
        description = config.get("description", feature_name)
        category = config.get("category", "other")
        estimated_delta = config.get("estimated_delta", 5.0)

        # For categorical, we use the estimated delta directly
        # In a full implementation, we'd compute these too
        wis_worst = baseline_wis - estimated_delta / 2
        wis_best = baseline_wis + estimated_delta / 2
        expected_delta, improvement_probability, ci_lower, ci_upper = _simulate_delta_distribution(
            wis_worst,
            wis_best,
            baseline_confidence=baseline_confidence,
            n_samples=monte_carlo_samples,
            seed=abs(hash((feature_name, "categorical"))) % (2**32),
        )
        actionability_score = max(0.0, expected_delta) * improvement_probability

        sensitivity = FeatureSensitivity(
            feature=feature_name,
            description=description,
            category=category,
            worst_value=worst,
            best_value=best,
            unit="",
            wis_at_worst=wis_worst,
            wis_at_best=wis_best,
            wis_delta=estimated_delta,
            expected_delta=expected_delta,
            improvement_probability=improvement_probability,
            delta_ci_lower=ci_lower,
            delta_ci_upper=ci_upper,
            actionability_score=actionability_score,
        )
        sensitivities.append(sensitivity)

        if category not in category_deltas:
            category_deltas[category] = []
        category_deltas[category].append(estimated_delta)

    # Rank by actionability (expected improvement weighted by probability)
    sensitivities.sort(
        key=lambda s: (s.actionability_score, s.improvement_probability, abs(s.expected_delta)),
        reverse=True,
    )
    for i, s in enumerate(sensitivities):
        s.rank = i + 1

    # Compute category impacts
    category_impacts = {}
    for cat, deltas in category_deltas.items():
        category_impacts[cat] = sum(deltas) / len(deltas) if deltas else 0.0

    # Generate top recommendation
    top_feature = ""
    top_delta = 0.0
    top_probability = 0.0
    top_recommendation = ""

    if sensitivities:
        top = sensitivities[0]
        top_feature = top.feature
        top_delta = top.expected_delta
        top_probability = top.improvement_probability

        if top.diminishing_returns and top.diminishing_threshold is not None:
            top_recommendation = (
                f"If you can only change one thing, improve {top.description.lower()}. "
                f"Changing from {top.worst_value}{top.unit} to {top.best_value}{top.unit} "
                f"is estimated to improve WIS by {top.expected_delta:+.1f} points "
                f"with {top.improvement_probability * 100:.0f}% probability. "
                f"Note: Returns diminish after ~{top.diminishing_threshold:.1f}{top.unit}."
            )
        else:
            top_recommendation = (
                f"If you can only change one thing, improve {top.description.lower()}. "
                f"Changing from {top.worst_value}{top.unit} to {top.best_value}{top.unit} "
                f"is estimated to improve WIS by {top.expected_delta:+.1f} points "
                f"with {top.improvement_probability * 100:.0f}% probability."
            )

    return SensitivityResult(
        baseline_wis=baseline_wis,
        feature_sensitivities=sensitivities,
        top_recommendation=top_recommendation,
        top_feature=top_feature,
        top_delta=top_delta,
        top_probability=top_probability,
        category_impacts=category_impacts,
        monte_carlo_samples=monte_carlo_samples,
    )


def format_sensitivity_report(result: SensitivityResult) -> str:
    """Format sensitivity analysis as readable report."""
    lines = []
    lines.append("=" * 60)
    lines.append("SENSITIVITY ANALYSIS REPORT")
    lines.append("=" * 60)
    lines.append("")
    lines.append(f"Baseline WIS: {result.baseline_wis:.1f}")
    lines.append("")
    lines.append("-" * 60)
    lines.append("TOP RECOMMENDATION")
    lines.append("-" * 60)
    lines.append(result.top_recommendation)
    lines.append("")
    lines.append("-" * 60)
    lines.append("FEATURE IMPACT RANKING")
    lines.append("-" * 60)
    lines.append("")
    lines.append(f"{'Rank':<5} {'Feature':<25} {'E[Delta]':<10} {'P(+)':<8} {'Category':<12}")
    lines.append("-" * 60)

    for s in result.feature_sensitivities[:10]:  # Top 10
        delta_str = f"+{s.expected_delta:.1f}" if s.expected_delta >= 0 else f"{s.expected_delta:.1f}"
        prob_str = f"{s.improvement_probability * 100:>5.1f}%"
        dr_marker = " *" if s.diminishing_returns else ""
        lines.append(f"{s.rank:<5} {s.description:<25} {delta_str:<10} {prob_str:<8} {s.category:<12}{dr_marker}")

    lines.append("")
    lines.append("* = diminishing returns detected")
    lines.append("")
    lines.append("-" * 60)
    lines.append("CATEGORY SUMMARY")
    lines.append("-" * 60)

    for cat, impact in sorted(result.category_impacts.items(), key=lambda x: -x[1]):
        lines.append(f"  {cat:<15}: avg impact {impact:.1f} WIS points")

    lines.append("")
    lines.append("-" * 60)
    lines.append("INTERPRETATION GUIDE")
    lines.append("-" * 60)
    lines.append("  Delta > 10: Major impact - prioritize changes here")
    lines.append("  Delta 5-10: Moderate impact - good improvement opportunity")
    lines.append("  Delta < 5:  Minor impact - lower priority")
    lines.append("")

    return "\n".join(lines)


def get_quick_sensitivity(
    measured_features: dict,
    occupant_profile: dict | None = None,
) -> dict:
    """
    Quick sensitivity estimate without full evaluation.

    Uses heuristics based on template knowledge rather than
    running full evaluations. Much faster but less precise.

    Returns dict with top 3 recommendations.
    """
    occupant_profile = occupant_profile or {"age": 35}
    age = occupant_profile.get("age", 35)

    recommendations = []

    # Check ceiling height
    ceiling = measured_features.get("ceiling_height_m")
    if ceiling and ceiling < 2.8:
        impact = min(15.0, (2.8 - ceiling) * 10)
        recommendations.append({
            "feature": "ceiling_height_m",
            "current": ceiling,
            "recommendation": "Increase ceiling height if possible",
            "estimated_impact": impact,
        })

    # Check illuminance
    lux = measured_features.get("illuminance_lux")
    if lux:
        if lux < 300:
            impact = min(12.0, (300 - lux) / 30)
            recommendations.append({
                "feature": "illuminance_lux",
                "current": lux,
                "recommendation": "Increase lighting to 300-500 lux",
                "estimated_impact": impact,
            })
        elif lux > 1000:
            impact = min(8.0, (lux - 1000) / 200)
            recommendations.append({
                "feature": "illuminance_lux",
                "current": lux,
                "recommendation": "Reduce excessive lighting",
                "estimated_impact": impact,
            })

    # Check noise
    noise = measured_features.get("ambient_noise_dba")
    if noise and noise > 45:
        impact = min(15.0, (noise - 45) * 0.8)
        recommendations.append({
            "feature": "ambient_noise_dba",
            "current": noise,
            "recommendation": "Reduce ambient noise levels",
            "estimated_impact": impact,
        })

    # Check nature view
    has_view = measured_features.get("has_nature_view")
    if not has_view:
        recommendations.append({
            "feature": "has_nature_view",
            "current": False,
            "recommendation": "Add nature views or biophilic elements",
            "estimated_impact": 12.0,
        })

    # Check material
    material = measured_features.get("primary_material")
    if material and material.lower() in ["concrete", "metal"]:
        recommendations.append({
            "feature": "primary_material",
            "current": material,
            "recommendation": "Incorporate natural materials (wood, stone)",
            "estimated_impact": 8.0,
        })

    # Age-specific adjustments
    if age < 12:
        recommendations.append({
            "feature": "floor_area_m2",
            "current": measured_features.get("floor_area_m2"),
            "recommendation": "For children: ensure adequate play/movement space",
            "estimated_impact": 6.0,
        })
    elif age > 65:
        recommendations.append({
            "feature": "illuminance_lux",
            "current": measured_features.get("illuminance_lux"),
            "recommendation": "For older adults: increase lighting levels by 50%",
            "estimated_impact": 8.0,
        })

    # Sort by impact and return top 3
    recommendations.sort(key=lambda r: r["estimated_impact"], reverse=True)
    return {
        "quick_analysis": True,
        "recommendations": recommendations[:3],
        "top_recommendation": recommendations[0]["recommendation"] if recommendations else "No issues detected",
    }
