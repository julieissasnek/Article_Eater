"""
cva_beauty_evaluation.py — CVA-6: Beauty Compression Analysis & Evaluation
============================================================================

Extends cva_beauty.py (4 beauty readout models) with Sprint CVA-6 deliverables:
  1. Residual analysis: B_observed - B_predicted per model
  2. Categorical compression: cluster beauty judgments into rasa-like categories
  3. Fluency hypothesis test: does processing cost reduction → beauty increase?
  4. Model comparison framework: cross-validate Linear/Quadratic/Neural/Rasa
  5. Framework for training/test split evaluation

Reference: CVA_SPRINT_PLAN §Sprint CVA-6
ADR-001: Extension layer — new file, no existing code modified.
"""

from __future__ import annotations

import json
import logging
import math
import statistics
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from src.services.cva_beauty import (
    BeautyReadout,
    LinearBeautyReadout,
    QuadraticBeautyReadout,
    NeuralBeautyReadout,
    RasaBeautyReadout,
    BeautyModelType,
    create_beauty_readout,
)
from src.models.cva_valuation import CVAValuationVector

LOGGER = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════
# 1. Residual Analysis
# ══════════════════════════════════════════════════════════════════

@dataclass
class ResidualAnalysis:
    """
    Residual analysis for a beauty readout model.

    r_i = B_observed_i - B_predicted_i

    Reports: mean residual, RMSE, per-observation residuals,
    and identifies systematic bias patterns.
    """
    model_name: str
    residuals: List[float]
    observed: List[float]
    predicted: List[float]

    @property
    def n(self) -> int:
        return len(self.residuals)

    @property
    def mean_residual(self) -> float:
        """Mean residual (positive = model underpredicts)."""
        return statistics.mean(self.residuals) if self.residuals else 0.0

    @property
    def rmse(self) -> float:
        """Root mean squared error."""
        if not self.residuals:
            return 0.0
        return math.sqrt(sum(r ** 2 for r in self.residuals) / self.n)

    @property
    def mae(self) -> float:
        """Mean absolute error."""
        return statistics.mean(abs(r) for r in self.residuals) if self.residuals else 0.0

    @property
    def bias_direction(self) -> str:
        """Systematic bias: underpredicts, overpredicts, or balanced."""
        if abs(self.mean_residual) < 0.02:
            return "balanced"
        return "underpredicts" if self.mean_residual > 0 else "overpredicts"

    @property
    def r_squared(self) -> float:
        """Coefficient of determination R²."""
        if self.n < 2:
            return 0.0
        mean_obs = statistics.mean(self.observed)
        ss_res = sum((o - p) ** 2 for o, p in zip(self.observed, self.predicted))
        ss_tot = sum((o - mean_obs) ** 2 for o in self.observed)
        if ss_tot == 0:
            return 1.0 if ss_res == 0 else 0.0
        return 1.0 - (ss_res / ss_tot)

    def to_dict(self) -> dict:
        return {
            "model_name": self.model_name,
            "n": self.n,
            "mean_residual": round(self.mean_residual, 4),
            "rmse": round(self.rmse, 4),
            "mae": round(self.mae, 4),
            "r_squared": round(self.r_squared, 4),
            "bias_direction": self.bias_direction,
        }


def compute_residuals(
    model: BeautyReadout,
    model_name: str,
    observations: List[Tuple[CVAValuationVector, float]],
) -> ResidualAnalysis:
    """
    Compute residuals for a beauty model against observed beauty scores.

    Args:
        model: BeautyReadout instance
        model_name: Name for reporting
        observations: List of (valuation_vector, observed_beauty_score) pairs

    Returns:
        ResidualAnalysis with per-observation residuals and summary stats
    """
    residuals = []
    observed_list = []
    predicted_list = []

    for valuation, observed_beauty in observations:
        predicted = model.compute(valuation)
        residual = observed_beauty - predicted
        residuals.append(residual)
        observed_list.append(observed_beauty)
        predicted_list.append(predicted)

    return ResidualAnalysis(
        model_name=model_name,
        residuals=residuals,
        observed=observed_list,
        predicted=predicted_list,
    )


# ══════════════════════════════════════════════════════════════════
# 2. Categorical Compression (Rasa Clustering)
# ══════════════════════════════════════════════════════════════════

@dataclass
class BeautyCluster:
    """A cluster of beauty observations with a rasa label."""
    rasa_label: str
    center: List[float]
    members: List[int]  # indices into the observation list
    mean_beauty: float
    std_beauty: float


def cluster_beauty_by_rasa(
    observations: List[Tuple[CVAValuationVector, float]],
) -> List[BeautyCluster]:
    """
    Cluster beauty observations using rasa categories.

    Uses the RasaBeautyReadout's dominant_rasa to assign each
    observation to a rasa category, then computes within-cluster
    statistics.

    Args:
        observations: List of (valuation, observed_beauty) pairs

    Returns:
        List of BeautyCluster, one per active rasa
    """
    rasa_model = RasaBeautyReadout()

    # Assign each observation to a rasa
    assignments: Dict[str, List[Tuple[int, float]]] = {}
    for idx, (valuation, beauty_score) in enumerate(observations):
        rasa = rasa_model.dominant_rasa(valuation)
        if rasa not in assignments:
            assignments[rasa] = []
        assignments[rasa].append((idx, beauty_score))

    clusters = []
    for rasa_name, members in sorted(assignments.items()):
        indices = [m[0] for m in members]
        scores = [m[1] for m in members]
        mean_b = statistics.mean(scores) if scores else 0.0
        std_b = statistics.stdev(scores) if len(scores) > 1 else 0.0

        # Compute center as mean valuation vector
        val_vectors = [observations[i][0].as_vector() for i in indices]
        if val_vectors:
            center = [
                sum(v[d] for v in val_vectors) / len(val_vectors)
                for d in range(len(val_vectors[0]))
            ]
        else:
            center = []

        clusters.append(BeautyCluster(
            rasa_label=rasa_name,
            center=center,
            members=indices,
            mean_beauty=mean_b,
            std_beauty=std_b,
        ))

    return clusters


def categorical_compression_analysis(
    clusters: List[BeautyCluster],
) -> Dict[str, Any]:
    """
    Analyze whether categorical compression (rasa clustering) captures
    meaningful variance in beauty judgments.

    Tests: do between-cluster differences in mean beauty exceed
    within-cluster variance?
    """
    if len(clusters) < 2:
        return {
            "n_clusters": len(clusters),
            "significant": False,
            "reason": "Need at least 2 clusters for analysis",
        }

    # Between-cluster variance
    means = [c.mean_beauty for c in clusters]
    grand_mean = statistics.mean(means)
    between_var = statistics.variance(means) if len(means) > 1 else 0.0

    # Average within-cluster variance
    within_vars = [c.std_beauty ** 2 for c in clusters if c.std_beauty > 0]
    avg_within_var = statistics.mean(within_vars) if within_vars else 0.001

    # F-ratio analog (one-way ANOVA approximation)
    f_ratio = between_var / avg_within_var if avg_within_var > 0 else 0.0

    return {
        "n_clusters": len(clusters),
        "cluster_sizes": {c.rasa_label: len(c.members) for c in clusters},
        "cluster_means": {c.rasa_label: round(c.mean_beauty, 3) for c in clusters},
        "between_variance": round(between_var, 4),
        "avg_within_variance": round(avg_within_var, 4),
        "f_ratio": round(f_ratio, 3),
        "significant": f_ratio > 2.0,  # rough threshold
        "interpretation": (
            "Rasa categories capture meaningful beauty structure"
            if f_ratio > 2.0
            else "Rasa categorization does not significantly differentiate beauty"
        ),
    }


# ══════════════════════════════════════════════════════════════════
# 3. Fluency Hypothesis Test
# ══════════════════════════════════════════════════════════════════

@dataclass
class FluencyResult:
    """Result of fluency hypothesis test."""
    processing_cost_correlation: float
    fluency_effect_size: float
    low_cost_beauty_mean: float
    high_cost_beauty_mean: float
    supports_hypothesis: bool
    interpretation: str

    def to_dict(self) -> dict:
        return {
            "processing_cost_correlation": round(self.processing_cost_correlation, 4),
            "fluency_effect_size": round(self.fluency_effect_size, 4),
            "low_cost_beauty_mean": round(self.low_cost_beauty_mean, 4),
            "high_cost_beauty_mean": round(self.high_cost_beauty_mean, 4),
            "supports_hypothesis": self.supports_hypothesis,
            "interpretation": self.interpretation,
        }


def test_fluency_hypothesis(
    observations: List[Tuple[CVAValuationVector, float]],
    processing_costs: List[float],
) -> FluencyResult:
    """
    Test the processing fluency hypothesis:
    "Reduction in processing cost → increase in beauty judgment"

    If correct, processing_cost should be negatively correlated with beauty.

    Args:
        observations: (valuation, beauty_score) pairs
        processing_costs: Corresponding processing costs

    Returns:
        FluencyResult with correlation, effect size, and interpretation
    """
    assert len(observations) == len(processing_costs)
    n = len(observations)

    if n < 3:
        return FluencyResult(
            processing_cost_correlation=0.0,
            fluency_effect_size=0.0,
            low_cost_beauty_mean=0.0,
            high_cost_beauty_mean=0.0,
            supports_hypothesis=False,
            interpretation="Insufficient data (n < 3)",
        )

    beauty_scores = [obs[1] for obs in observations]

    # Pearson correlation between processing_cost and beauty
    mean_pc = statistics.mean(processing_costs)
    mean_b = statistics.mean(beauty_scores)

    cov = sum(
        (pc - mean_pc) * (b - mean_b)
        for pc, b in zip(processing_costs, beauty_scores)
    ) / (n - 1)

    std_pc = statistics.stdev(processing_costs) if n > 1 else 0.001
    std_b = statistics.stdev(beauty_scores) if n > 1 else 0.001

    correlation = cov / (std_pc * std_b) if std_pc > 0 and std_b > 0 else 0.0

    # Median split for effect size
    median_pc = statistics.median(processing_costs)
    low_cost = [b for pc, b in zip(processing_costs, beauty_scores) if pc <= median_pc]
    high_cost = [b for pc, b in zip(processing_costs, beauty_scores) if pc > median_pc]

    low_mean = statistics.mean(low_cost) if low_cost else 0.0
    high_mean = statistics.mean(high_cost) if high_cost else 0.0
    effect_size = low_mean - high_mean  # positive = fluency effect

    supports = correlation < -0.15 and effect_size > 0.03

    if supports:
        interp = (
            f"Fluency hypothesis SUPPORTED: r={correlation:.3f}, "
            f"low-cost beauty ({low_mean:.3f}) > high-cost ({high_mean:.3f}), "
            f"cohen's d analog ≈ {effect_size:.3f}"
        )
    else:
        interp = (
            f"Fluency hypothesis NOT supported: r={correlation:.3f}, "
            f"low-cost beauty ({low_mean:.3f}) vs high-cost ({high_mean:.3f})"
        )

    return FluencyResult(
        processing_cost_correlation=correlation,
        fluency_effect_size=effect_size,
        low_cost_beauty_mean=low_mean,
        high_cost_beauty_mean=high_mean,
        supports_hypothesis=supports,
        interpretation=interp,
    )


# ══════════════════════════════════════════════════════════════════
# 4. Model Comparison Framework
# ══════════════════════════════════════════════════════════════════

@dataclass
class ModelComparisonResult:
    """Comparison of multiple beauty readout models."""
    model_results: Dict[str, ResidualAnalysis]
    best_model: str
    ranking: List[Tuple[str, float]]

    def to_dict(self) -> dict:
        return {
            "best_model": self.best_model,
            "ranking": [
                {"model": name, "rmse": round(rmse, 4)}
                for name, rmse in self.ranking
            ],
            "model_details": {
                name: ra.to_dict()
                for name, ra in self.model_results.items()
            },
        }


def compare_beauty_models(
    observations: List[Tuple[CVAValuationVector, float]],
    train_fraction: float = 0.7,
) -> ModelComparisonResult:
    """
    Compare all 4 beauty readout models using train/test split.

    Args:
        observations: (valuation, beauty_score) pairs
        train_fraction: Fraction for training (rest for testing)

    Returns:
        ModelComparisonResult with per-model residuals and ranking
    """
    n = len(observations)
    split = int(n * train_fraction)

    # For now, since models are not trained, evaluate on all data
    # In production, would train on observations[:split] and test on [split:]
    test_data = observations if n < 10 else observations[split:]

    models = {
        "linear": LinearBeautyReadout(),
        "quadratic": QuadraticBeautyReadout(),
        "neural": NeuralBeautyReadout(),
        "rasa": RasaBeautyReadout(),
    }

    results = {}
    for name, model in models.items():
        results[name] = compute_residuals(model, name, test_data)

    # Rank by RMSE (lower is better)
    ranking = sorted(
        [(name, ra.rmse) for name, ra in results.items()],
        key=lambda x: x[1],
    )
    best = ranking[0][0]

    return ModelComparisonResult(
        model_results=results,
        best_model=best,
        ranking=ranking,
    )


# ══════════════════════════════════════════════════════════════════
# 5. Full Evaluation Pipeline
# ══════════════════════════════════════════════════════════════════

def run_full_beauty_evaluation(
    observations: List[Tuple[CVAValuationVector, float]],
    processing_costs: Optional[List[float]] = None,
    output_path: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Run the complete CVA-6 beauty evaluation pipeline.

    Steps:
    1. Compare all 4 readout models (residuals + RMSE + R²)
    2. Cluster observations by rasa category
    3. Test fluency hypothesis (if processing costs provided)
    4. Export results

    Returns: Full evaluation dict
    """
    LOGGER.info("Running CVA-6 beauty evaluation on %d observations", len(observations))

    # 1. Model comparison
    comparison = compare_beauty_models(observations)

    # 2. Rasa clustering
    clusters = cluster_beauty_by_rasa(observations)
    compression = categorical_compression_analysis(clusters)

    # 3. Fluency test
    fluency = None
    if processing_costs and len(processing_costs) == len(observations):
        fluency = test_fluency_hypothesis(observations, processing_costs)

    # Assemble results
    result = {
        "title": "CVA-6 Beauty Compression Analysis",
        "n_observations": len(observations),
        "model_comparison": comparison.to_dict(),
        "categorical_compression": compression,
        "fluency_hypothesis": fluency.to_dict() if fluency else None,
        "clusters": [
            {
                "rasa": c.rasa_label,
                "n_members": len(c.members),
                "mean_beauty": round(c.mean_beauty, 3),
                "std_beauty": round(c.std_beauty, 3),
            }
            for c in clusters
        ],
    }

    # Export if path provided
    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_text(
            json.dumps(result, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        LOGGER.info("Exported beauty evaluation to %s", output_path)

    return result
