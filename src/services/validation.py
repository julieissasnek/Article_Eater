"""
Validation Infrastructure for Article Eater Post-Quinean.

Sprint 8.2-8.4: Phased validation protocol with gates, stratified LOO, and ecological validity.
Per expert panel consensus: Progressive validation as corpus grows.

This module provides:
1. ValidationPhase - Phases of validation as corpus grows
2. ValidationGate - Minimum requirements for each phase
3. EcologicalValidity - Enhanced lab vs field distinction (VR vs video)
4. StratifiedLOOReport - Leave-one-out with theory stratification
5. ValidationReport - Comprehensive validation metrics
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import math


# =============================================================================
# VALIDATION PHASES (Expert Panel: Simon)
# =============================================================================

class ValidationPhase(Enum):
    """
    Phases of validation, gated by corpus requirements.

    Per expert panel: Don't attempt sophisticated validation with small corpus.
    """
    PHASE_1_ANNOTATION = "annotation"      # N≥10: Gold Standard comparison
    PHASE_2_CALIBRATION = "calibration"    # N≥20: Credence calibration
    PHASE_3_LOO = "loo"                    # N≥30: Leave-one-out prediction
    PHASE_4_BRIDGES = "bridges"            # N≥50: Bridge validation


@dataclass
class ValidationGate:
    """
    Minimum requirements to enter a validation phase.

    Per expert panel: Gates prevent premature validation attempts.
    """
    phase: ValidationPhase
    min_papers: int
    min_connectivity: float  # Mean constraint degree
    min_lcc: float  # Largest connected component fraction

    def check(self, n_papers: int, connectivity: float, lcc_fraction: float) -> bool:
        """Check if gate requirements are met."""
        return (
            n_papers >= self.min_papers and
            connectivity >= self.min_connectivity and
            lcc_fraction >= self.min_lcc
        )


# Pre-defined validation gates per expert panel consensus
VALIDATION_GATES: Dict[ValidationPhase, ValidationGate] = {
    ValidationPhase.PHASE_1_ANNOTATION: ValidationGate(
        phase=ValidationPhase.PHASE_1_ANNOTATION,
        min_papers=10,
        min_connectivity=0.0,  # No connectivity requirement
        min_lcc=0.0            # No LCC requirement
    ),
    ValidationPhase.PHASE_2_CALIBRATION: ValidationGate(
        phase=ValidationPhase.PHASE_2_CALIBRATION,
        min_papers=20,
        min_connectivity=1.5,  # Average 1.5 constraints per belief
        min_lcc=0.5            # At least half connected
    ),
    ValidationPhase.PHASE_3_LOO: ValidationGate(
        phase=ValidationPhase.PHASE_3_LOO,
        min_papers=30,
        min_connectivity=2.0,
        min_lcc=0.7
    ),
    ValidationPhase.PHASE_4_BRIDGES: ValidationGate(
        phase=ValidationPhase.PHASE_4_BRIDGES,
        min_papers=50,
        min_connectivity=2.5,
        min_lcc=0.8
    ),
}


# =============================================================================
# ECOLOGICAL VALIDITY (Sprint 8.4 - Expert Panel: Kaplan)
# =============================================================================

class EcologicalValidity(Enum):
    """
    Ecological validity of study methodology.

    Sprint 8.4 (Kaplan): Distinguish VR from video, field from lab.
    Higher validity = findings more likely to generalize.
    """
    FIELD_NATURAL = "field_natural"       # Real environment, natural behavior
    FIELD_STRUCTURED = "field_structured" # Real environment, structured task
    LAB_VR = "lab_vr"                     # VR immersion (NEW distinction)
    LAB_VIDEO = "lab_video"               # Video walkthrough (NEW distinction)
    LAB_PHOTOS = "lab_photos"             # Static images
    LAB_ABSTRACT = "lab_abstract"         # No environment reference


# Panel Fix 5 (Kaplan): Ecological validity affects UNCERTAINTY, not credence.
# These values represent base validity - uncertainty is multiplied by 1/validity.
# Example: LAB_PHOTOS (0.65) → uncertainty factor = 1/0.65 ≈ 1.54
#          A credence with uncertainty=0.2 becomes uncertainty=0.31 (increased by 54%)
#
# Rationale: Lower ecological validity means we're less certain about generalizability,
# but it doesn't mean the effect size itself is smaller. The effect may be real,
# we just have more uncertainty about whether it applies outside the lab.
ECOLOGICAL_VALIDITY_WEIGHTS: Dict[EcologicalValidity, float] = {
    EcologicalValidity.FIELD_NATURAL: 1.0,      # No uncertainty increase
    EcologicalValidity.FIELD_STRUCTURED: 0.95,  # ~5% uncertainty increase
    EcologicalValidity.LAB_VR: 0.85,            # ~18% uncertainty increase
    EcologicalValidity.LAB_VIDEO: 0.75,         # ~33% uncertainty increase
    EcologicalValidity.LAB_PHOTOS: 0.65,        # ~54% uncertainty increase
    EcologicalValidity.LAB_ABSTRACT: 0.50,      # 100% uncertainty increase
}


def get_validity_weight(validity: EcologicalValidity) -> float:
    """
    Get base validity weight for ecological validity level.

    NOTE: This returns the base weight. To get uncertainty adjustment, use
    get_uncertainty_factor() instead.
    """
    return ECOLOGICAL_VALIDITY_WEIGHTS.get(validity, 0.5)


def get_uncertainty_factor(validity: EcologicalValidity) -> float:
    """
    Get uncertainty multiplication factor for ecological validity level.

    Panel Fix 5 (Kaplan): Lower ecological validity should increase uncertainty,
    not decrease credence. This preserves the effect size estimate while
    reflecting our reduced confidence in generalizability.

    Args:
        validity: The ecological validity level of the study

    Returns:
        Factor to multiply uncertainty by (always >= 1.0)

    Example:
        >>> get_uncertainty_factor(EcologicalValidity.LAB_PHOTOS)
        1.538...  # 0.65 base → 1/0.65 ≈ 1.54 factor
    """
    weight = ECOLOGICAL_VALIDITY_WEIGHTS.get(validity, 0.5)
    return 1.0 / weight


def apply_ecological_validity_to_credence(
    credence_value: float,
    credence_uncertainty: float,
    validity: EcologicalValidity
) -> tuple:
    """
    Apply ecological validity adjustment to a credence.

    Panel Fix 5 (Kaplan): Validity affects uncertainty, not the credence value.
    - credence_value stays the same
    - credence_uncertainty is multiplied by the uncertainty factor

    Args:
        credence_value: The credence value (0-1)
        credence_uncertainty: The meta-uncertainty about the credence
        validity: Ecological validity of the study

    Returns:
        Tuple of (adjusted_value, adjusted_uncertainty)
        Note: value is unchanged, only uncertainty is adjusted.
    """
    factor = get_uncertainty_factor(validity)
    adjusted_uncertainty = min(1.0, credence_uncertainty * factor)  # Cap at 1.0
    return (credence_value, adjusted_uncertainty)


def infer_ecological_validity(methodology_text: str) -> EcologicalValidity:
    """
    Infer ecological validity from methodology description.

    Uses keyword matching for common methodology indicators.
    """
    text = methodology_text.lower()

    # Field studies
    if any(k in text for k in ["field study", "naturalistic", "real environment", "in situ"]):
        if any(k in text for k in ["structured", "controlled", "task"]):
            return EcologicalValidity.FIELD_STRUCTURED
        return EcologicalValidity.FIELD_NATURAL

    # Lab studies with environment presentation
    if any(k in text for k in ["virtual reality", "vr ", "hmd", "immersive", "headset"]):
        return EcologicalValidity.LAB_VR

    if any(k in text for k in ["video", "walkthrough", "film", "movie"]):
        return EcologicalValidity.LAB_VIDEO

    if any(k in text for k in ["photo", "image", "picture", "slide"]):
        return EcologicalValidity.LAB_PHOTOS

    # Abstract/no environment
    return EcologicalValidity.LAB_ABSTRACT


# =============================================================================
# COHERENCE CONTRIBUTION (Panel Fix 2 - Expert Panel: Simon)
# =============================================================================

from typing import Literal

# Coherence contribution levels
CoherenceContribution = Literal["high", "medium", "low"]


@dataclass
class BeliefCoherenceAssessment:
    """
    Assessment of a belief's contribution to and from web coherence.

    Panel Fix 2 (Simon): Theoretical beliefs with low coherence contribution
    should be flagged for review, even if they pass F1 thresholds.
    """
    belief_id: str
    coherence_contribution: CoherenceContribution
    n_supporting_constraints: int
    n_contradicting_constraints: int
    mean_constraint_strength: float
    consistency_with_empirical: Optional[float]  # 0-1, how well it fits empirical beliefs
    flags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'belief_id': self.belief_id,
            'coherence_contribution': self.coherence_contribution,
            'n_supporting_constraints': self.n_supporting_constraints,
            'n_contradicting_constraints': self.n_contradicting_constraints,
            'mean_constraint_strength': self.mean_constraint_strength,
            'consistency_with_empirical': self.consistency_with_empirical,
            'flags': self.flags.copy()
        }


def compute_coherence_contribution(
    n_supporting: int,
    n_contradicting: int,
    mean_strength: float,
    consistency_with_empirical: Optional[float] = None
) -> CoherenceContribution:
    """
    Compute coherence contribution level for a belief.

    Panel Fix 2 (Simon): Even with low F1 thresholds for theoretical beliefs,
    we should flag those with weak coherence support for review.

    Criteria:
    - HIGH: 3+ supporting constraints, strong mean strength (>0.6), consistency ≥0.7
    - MEDIUM: 1-2 supporting constraints OR mean strength 0.4-0.6
    - LOW: 0 supporting constraints OR mean strength <0.4 OR consistency <0.5

    Args:
        n_supporting: Number of constraints supporting this belief
        n_contradicting: Number of constraints contradicting this belief
        mean_strength: Mean strength of supporting constraints (0-1)
        consistency_with_empirical: How well belief fits empirical findings (0-1)

    Returns:
        CoherenceContribution level ("high", "medium", or "low")
    """
    # Immediate LOW if no support or mostly contradicting
    if n_supporting == 0:
        return "low"

    if n_contradicting > n_supporting:
        return "low"

    # Check consistency with empirical findings
    if consistency_with_empirical is not None and consistency_with_empirical < 0.5:
        return "low"

    # HIGH requires multiple strong, consistent support
    if (n_supporting >= 3 and
        mean_strength >= 0.6 and
        (consistency_with_empirical is None or consistency_with_empirical >= 0.7)):
        return "high"

    # MEDIUM for moderate support
    if n_supporting >= 1 and mean_strength >= 0.4:
        return "medium"

    return "low"


def assess_theoretical_belief_coherence(
    belief_id: str,
    n_supporting: int,
    n_contradicting: int,
    mean_strength: float,
    consistency_with_empirical: Optional[float] = None
) -> BeliefCoherenceAssessment:
    """
    Assess a theoretical belief's coherence contribution.

    Panel Fix 2 (Simon): Flag low-coherence theoretical beliefs for review.

    Args:
        belief_id: The belief being assessed
        n_supporting: Number of supporting constraints
        n_contradicting: Number of contradicting constraints
        mean_strength: Mean strength of supporting constraints
        consistency_with_empirical: How well belief fits empirical findings

    Returns:
        BeliefCoherenceAssessment with contribution level and flags
    """
    contribution = compute_coherence_contribution(
        n_supporting, n_contradicting, mean_strength, consistency_with_empirical
    )

    flags = []

    # Generate warning flags for low-coherence theoretical beliefs
    if contribution == "low":
        flags.append("LOW_COHERENCE_THEORETICAL")
        if n_supporting == 0:
            flags.append("ISOLATED_NO_SUPPORT")
        if n_contradicting > n_supporting:
            flags.append("MORE_CONTRADICTING_THAN_SUPPORTING")
        if consistency_with_empirical is not None and consistency_with_empirical < 0.5:
            flags.append("INCONSISTENT_WITH_EMPIRICAL")

    return BeliefCoherenceAssessment(
        belief_id=belief_id,
        coherence_contribution=contribution,
        n_supporting_constraints=n_supporting,
        n_contradicting_constraints=n_contradicting,
        mean_constraint_strength=mean_strength,
        consistency_with_empirical=consistency_with_empirical,
        flags=flags
    )


# =============================================================================
# PREDICTION MODES (Sprint 8.3 - Expert Panel: Simon)
# =============================================================================

class PredictionMode(Enum):
    """How a prediction was generated in LOO validation."""
    DIRECT = "direct"           # Belief exists in master web
    CONSTRAINED = "constrained" # Inferred from connected beliefs
    NOVEL = "novel"             # No connection, prior only


@dataclass
class LOOMetrics:
    """Metrics from leave-one-out validation."""
    mae: float  # Mean absolute error
    rmse: float  # Root mean squared error
    in_range_rate: float  # Fraction within expected uncertainty
    n_predictions: int
    mode_counts: Dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'mae': self.mae,
            'rmse': self.rmse,
            'in_range_rate': self.in_range_rate,
            'n_predictions': self.n_predictions,
            'mode_counts': self.mode_counts.copy()
        }


@dataclass
class StratifiedLOOReport:
    """
    Leave-one-out validation with stratification by theory and paper type.

    Sprint 8.3 (Simon): Stratify to detect theory-specific issues.
    """
    overall: LOOMetrics
    by_theory: Dict[str, LOOMetrics] = field(default_factory=dict)
    single_theory_papers: Optional[LOOMetrics] = None
    multi_theory_papers: Optional[LOOMetrics] = None
    prediction_mode_distribution: Dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        result = {
            'overall': self.overall.to_dict(),
            'by_theory': {k: v.to_dict() for k, v in self.by_theory.items()},
            'prediction_mode_distribution': self.prediction_mode_distribution.copy()
        }
        if self.single_theory_papers:
            result['single_theory_papers'] = self.single_theory_papers.to_dict()
        if self.multi_theory_papers:
            result['multi_theory_papers'] = self.multi_theory_papers.to_dict()
        return result


# =============================================================================
# VALIDATION REPORT (Sprint 9.4 preview)
# =============================================================================

@dataclass
class ValidationReport:
    """
    Comprehensive validation metrics.

    Sprint 9.4 (Simon): Track metrics at multiple levels.
    """
    # Core metrics
    belief_recall: float = 0.0
    belief_precision: float = 0.0
    belief_f1: float = 0.0

    # Stratified F1 (per Simon)
    f1_by_level: Dict[str, float] = field(default_factory=dict)

    # Credence calibration
    credence_mae: float = 0.0
    credence_in_range: float = 0.0
    credence_by_level: Dict[str, float] = field(default_factory=dict)

    # Constraint metrics
    constraint_recall: float = 0.0
    constraint_precision: float = 0.0

    # Negative tests
    false_extractions: List[str] = field(default_factory=list)
    should_not_extract_violations: int = 0

    # Phase eligibility
    phases_passed: List[ValidationPhase] = field(default_factory=list)

    # Confidence
    corpus_version: str = ""
    statistical_power: str = "insufficient"  # "sufficient", "preliminary", "insufficient"

    def to_dict(self) -> Dict[str, Any]:
        return {
            'belief_recall': self.belief_recall,
            'belief_precision': self.belief_precision,
            'belief_f1': self.belief_f1,
            'f1_by_level': self.f1_by_level.copy(),
            'credence_mae': self.credence_mae,
            'credence_in_range': self.credence_in_range,
            'credence_by_level': self.credence_by_level.copy(),
            'constraint_recall': self.constraint_recall,
            'constraint_precision': self.constraint_precision,
            'false_extractions': self.false_extractions.copy(),
            'should_not_extract_violations': self.should_not_extract_violations,
            'phases_passed': [p.value for p in self.phases_passed],
            'corpus_version': self.corpus_version,
            'statistical_power': self.statistical_power
        }


# Pass thresholds per expert panel
PASS_THRESHOLDS: Dict[str, Dict[str, float]] = {
    "empirical": {"f1": 0.75, "credence_in_range": 0.75},
    "intermediate": {"f1": 0.65, "credence_in_range": 0.70},
    "theoretical": {"f1": 0.55, "credence_in_range": 0.65},
    "overall": {"f1": 0.70, "credence_in_range": 0.70},
}


def check_validation_passed(report: ValidationReport) -> bool:
    """
    Check if validation report meets pass thresholds at each level.

    Per expert panel (Simon): Must meet level-specific thresholds.
    """
    for level, thresholds in PASS_THRESHOLDS.items():
        if level == "overall":
            if report.belief_f1 < thresholds["f1"]:
                return False
            if report.credence_in_range < thresholds["credence_in_range"]:
                return False
        else:
            level_f1 = report.f1_by_level.get(level, 0)
            if level_f1 < thresholds["f1"]:
                return False

    # Must have zero "should not extract" violations
    return report.should_not_extract_violations == 0


# =============================================================================
# VALIDATION UTILITIES
# =============================================================================

def check_validation_eligibility(
    n_papers: int,
    mean_constraint_degree: float,
    lcc_fraction: float
) -> List[ValidationPhase]:
    """
    Return which validation phases the corpus is eligible for.

    Args:
        n_papers: Number of papers in corpus
        mean_constraint_degree: Average constraints per belief
        lcc_fraction: Fraction of beliefs in largest connected component

    Returns:
        List of eligible validation phases
    """
    eligible = []
    for phase, gate in VALIDATION_GATES.items():
        if gate.check(n_papers, mean_constraint_degree, lcc_fraction):
            eligible.append(phase)
    return eligible


def compute_mean_constraint_degree(n_beliefs: int, n_constraints: int) -> float:
    """Compute mean constraint degree (constraints per belief)."""
    if n_beliefs == 0:
        return 0.0
    # Each constraint connects 2 beliefs, so multiply by 2
    return (2 * n_constraints) / n_beliefs


def compute_loo_metrics(
    predictions: List[float],
    actuals: List[float],
    uncertainties: List[float],
    modes: List[str]
) -> LOOMetrics:
    """
    Compute leave-one-out metrics from predictions.

    Args:
        predictions: Predicted credences
        actuals: Actual credences from held-out paper
        uncertainties: Prediction uncertainties
        modes: Prediction mode for each prediction
    """
    if not predictions:
        return LOOMetrics(mae=0.0, rmse=0.0, in_range_rate=0.0, n_predictions=0)

    n = len(predictions)
    errors = [abs(p - a) for p, a in zip(predictions, actuals)]

    mae = sum(errors) / n
    rmse = math.sqrt(sum(e**2 for e in errors) / n)

    # In-range: prediction within uncertainty of actual
    in_range = sum(
        1 for p, a, u in zip(predictions, actuals, uncertainties)
        if abs(p - a) <= u
    )
    in_range_rate = in_range / n if n > 0 else 0.0

    # Mode distribution
    mode_counts = {}
    for m in modes:
        mode_counts[m] = mode_counts.get(m, 0) + 1

    return LOOMetrics(
        mae=mae,
        rmse=rmse,
        in_range_rate=in_range_rate,
        n_predictions=n,
        mode_counts=mode_counts
    )


# =============================================================================
# EXPORT
# =============================================================================

__all__ = [
    # Phases and gates
    "ValidationPhase",
    "ValidationGate",
    "VALIDATION_GATES",
    "check_validation_eligibility",

    # Ecological validity
    "EcologicalValidity",
    "ECOLOGICAL_VALIDITY_WEIGHTS",
    "get_validity_weight",
    "get_uncertainty_factor",  # Panel Fix 5
    "apply_ecological_validity_to_credence",  # Panel Fix 5
    "infer_ecological_validity",

    # Coherence contribution (Panel Fix 2)
    "CoherenceContribution",
    "BeliefCoherenceAssessment",
    "compute_coherence_contribution",
    "assess_theoretical_belief_coherence",

    # LOO validation
    "PredictionMode",
    "LOOMetrics",
    "StratifiedLOOReport",
    "compute_loo_metrics",

    # Validation report
    "ValidationReport",
    "PASS_THRESHOLDS",
    "check_validation_passed",

    # Utilities
    "compute_mean_constraint_degree",
]
