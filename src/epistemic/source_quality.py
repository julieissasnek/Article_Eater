"""
Source Quality Computation (Sprint T2-2.5).

Computes composite source quality scores from component metrics.
Source quality is a weighted combination of:
- Methodological rigor
- Theoretical commitment (inverted - high commitment = lower quality)
- Independence of evidence
- Replication status

References:
- Epistemic vigilance: Sperber et al. (2010)
- Methodological quality: Cochrane GRADE framework
"""

from dataclasses import dataclass, field
from typing import Dict, Optional


# =============================================================================
# DEFAULT WEIGHTS
# =============================================================================

DEFAULT_SOURCE_QUALITY_WEIGHTS: Dict[str, float] = {
    "rigor": 0.40,           # Methodological rigor most important
    "commitment": 0.15,       # Theoretical commitment penalty
    "independence": 0.25,     # Independence of evidence
    "replication": 0.20,      # Replication status
}


# =============================================================================
# SOURCE QUALITY COMPUTATION
# =============================================================================

def compute_source_quality(
    methodological_rigor: float,      # [0, 1]
    theoretical_commitment: float,    # [0, 1] high = more potential bias
    independence_of_evidence: float,  # [0, 1]
    replication_status: float,        # [0, 1]
    weights: Optional[Dict[str, float]] = None
) -> float:
    """
    Compute weighted combination of source quality components.

    Source quality is the primary epistemic signal about evidence credibility.
    High source quality indicates: good methods, independent sources,
    replicated findings, and low a priori theoretical commitment.

    Args:
        methodological_rigor: Study design quality (randomization, blinding,
            sample size, pre-registration). Range [0, 1].
        theoretical_commitment: Degree of a priori theoretical bias in study
            design. INVERTED in score - high commitment reduces quality.
            Range [0, 1].
        independence_of_evidence: Whether studies are from independent labs/
            paradigms or clustered. Range [0, 1].
        replication_status: Has finding been replicated?
            0 = failed replication, 0.5 = unreplicated, 1 = replicated.
            Range [0, 1].
        weights: Optional weight dictionary. Defaults to DEFAULT_SOURCE_QUALITY_WEIGHTS.

    Returns:
        Composite source quality score in [0, 1].

    Example:
        >>> # High quality: good methods, independent, replicated, low commitment
        >>> compute_source_quality(0.9, 0.1, 0.9, 0.9)
        0.88

        >>> # Low quality: weak methods, single lab, unreplicated, high commitment
        >>> compute_source_quality(0.2, 0.9, 0.1, 0.0)
        0.225
    """
    if weights is None:
        weights = DEFAULT_SOURCE_QUALITY_WEIGHTS

    # Validate inputs are in [0, 1]
    for name, value in [
        ("methodological_rigor", methodological_rigor),
        ("theoretical_commitment", theoretical_commitment),
        ("independence_of_evidence", independence_of_evidence),
        ("replication_status", replication_status),
    ]:
        if not 0.0 <= value <= 1.0:
            raise ValueError(f"{name} must be in [0, 1], got {value}")

    # Compute weighted sum
    # Note: theoretical_commitment is INVERTED (high commitment = lower quality)
    quality = (
        weights["rigor"] * methodological_rigor +
        weights["commitment"] * (1.0 - theoretical_commitment) +
        weights["independence"] * independence_of_evidence +
        weights["replication"] * replication_status
    )

    # Ensure result is in [0, 1] (should be if weights sum to 1)
    return max(0.0, min(1.0, quality))


# =============================================================================
# SOURCE QUALITY RESULT DATACLASS
# =============================================================================

@dataclass
class SourceQualityResult:
    """
    Complete source quality assessment with component scores.

    Provides transparency about what contributed to the composite score.
    """
    composite_score: float
    methodological_rigor: float
    theoretical_commitment: float
    independence_of_evidence: float
    replication_status: float
    weights: Dict[str, float] = field(default_factory=lambda: DEFAULT_SOURCE_QUALITY_WEIGHTS.copy())

    # Component contributions (for explainability)
    rigor_contribution: float = 0.0
    commitment_contribution: float = 0.0
    independence_contribution: float = 0.0
    replication_contribution: float = 0.0

    def __post_init__(self):
        """Compute component contributions."""
        self.rigor_contribution = self.weights["rigor"] * self.methodological_rigor
        self.commitment_contribution = self.weights["commitment"] * (1.0 - self.theoretical_commitment)
        self.independence_contribution = self.weights["independence"] * self.independence_of_evidence
        self.replication_contribution = self.weights["replication"] * self.replication_status

    def to_dict(self) -> Dict:
        return {
            "composite_score": self.composite_score,
            "components": {
                "methodological_rigor": self.methodological_rigor,
                "theoretical_commitment": self.theoretical_commitment,
                "independence_of_evidence": self.independence_of_evidence,
                "replication_status": self.replication_status,
            },
            "contributions": {
                "rigor": self.rigor_contribution,
                "commitment": self.commitment_contribution,
                "independence": self.independence_contribution,
                "replication": self.replication_contribution,
            },
            "weights": self.weights,
        }

    @property
    def quality_level(self) -> str:
        """Categorical quality assessment."""
        if self.composite_score >= 0.8:
            return "high"
        elif self.composite_score >= 0.5:
            return "moderate"
        elif self.composite_score >= 0.3:
            return "low"
        else:
            return "very_low"


def compute_source_quality_detailed(
    methodological_rigor: float,
    theoretical_commitment: float,
    independence_of_evidence: float,
    replication_status: float,
    weights: Optional[Dict[str, float]] = None
) -> SourceQualityResult:
    """
    Compute source quality with full component breakdown.

    Returns a SourceQualityResult with explainability data.
    """
    if weights is None:
        weights = DEFAULT_SOURCE_QUALITY_WEIGHTS.copy()

    composite = compute_source_quality(
        methodological_rigor,
        theoretical_commitment,
        independence_of_evidence,
        replication_status,
        weights
    )

    return SourceQualityResult(
        composite_score=composite,
        methodological_rigor=methodological_rigor,
        theoretical_commitment=theoretical_commitment,
        independence_of_evidence=independence_of_evidence,
        replication_status=replication_status,
        weights=weights,
    )


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def high_quality_threshold() -> float:
    """Return the threshold for high quality classification."""
    return 0.8


def moderate_quality_threshold() -> float:
    """Return the threshold for moderate quality classification."""
    return 0.5


def classify_quality(score: float) -> str:
    """Classify a source quality score into categorical levels."""
    if score >= high_quality_threshold():
        return "high"
    elif score >= moderate_quality_threshold():
        return "moderate"
    elif score >= 0.3:
        return "low"
    else:
        return "very_low"
