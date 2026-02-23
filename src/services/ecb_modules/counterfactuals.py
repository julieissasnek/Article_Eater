"""Extracted counterfactual and assessment structures from epistemic_causal_bridge.py (ARCH-5e).

Contains counterfactual query/result types, robustness analysis,
coherence/scope/contrast assessments, epistemic counterfactuals,
and epistemic gap structures.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

# Avoid circular imports — these are used for type hints only.
# The actual ContrastClass, PopulationContext etc. are in contrast_classes.py.


@dataclass
class CounterfactualQuery:
    """A counterfactual query with van Fraassen contrast specification."""
    query_id: str
    intervention: Dict[str, float]
    outcome_var: str
    evidence: Dict[str, float] = field(default_factory=dict)
    contrast_class: Optional[Any] = None  # ContrastClass
    target_contrast: Optional[Any] = None  # ConditionSpec
    alternative_interventions: List[Dict[str, float]] = field(default_factory=list)
    target_population: Optional[str] = None
    target_setting: Optional[str] = None
    target_individual: Optional[Any] = None  # IndividualDifferenceProfile

    def describe(self) -> str:
        parts = [f"If we set {self.intervention},"]
        parts.append(f"what would {self.outcome_var} be?")
        if self.contrast_class:
            parts.append(f"(Contrast: {self.contrast_class.describe()})")
        if self.target_population:
            parts.append(f"For: {self.target_population}")
        return " ".join(parts)


@dataclass
class TheoryCounterfactual:
    """Counterfactual result under a specific theory."""
    theory_id: str
    theory_credence: float
    estimate: float
    confidence_interval: Tuple[float, float]
    mechanism_path: List[str]
    supporting_beliefs: List[str]


@dataclass
class RobustnessAnalysis:
    """How robust is this counterfactual to belief revision?"""
    robustness_score: float
    min_revision_cost: float
    sensitive_beliefs: List[Dict[str, Any]]
    path_entrenchment: float


@dataclass
class CoherenceViolation:
    """A specific coherence violation."""
    violation_type: str
    description: str
    involved_beliefs: List[str]
    severity: float


@dataclass
class CoherenceAssessment:
    """Is this counterfactual coherent with the web?"""
    is_coherent: bool
    coherence_score: float
    violations: List[CoherenceViolation]
    required_co_revisions: List[Set[str]]


@dataclass
class ScopeAssessment:
    """Is this counterfactual within evidential scope?"""
    in_scope: bool
    scope_score: float
    population_match: float
    setting_match: float
    baseline_match: float
    extrapolation_warnings: List[str]
    suggested_penalty: float


@dataclass
class ContrastAssessment:
    """Van Fraassen assessment of contrast class transfer (ECB-3.1/3.2)."""
    source_contrast: Optional[Any] = None  # ContrastClass
    target_contrast: Optional[Any] = None  # ContrastClass
    similarity: float = 0.0
    baseline_differences: Dict[str, float] = field(default_factory=dict)
    meaning_differences: Dict[str, Tuple[str, str]] = field(default_factory=dict)
    transfer_type: Any = None  # ContrastTransferType
    transfer_type_str: str = ""
    adjustment_factor: float = 1.0
    warnings: List[str] = field(default_factory=list)
    is_defined: bool = True
    reason_undefined: Optional[str] = None


@dataclass
class EpistemicGap:
    """An epistemic gap identified during causal analysis (ECB-3.3)."""
    gap_type: str
    description: str
    severity: float
    belief_id: Optional[str] = None
    missing_evidence: Optional[str] = None
    target_population: Optional[str] = None
    target_variable: Optional[str] = None

    def to_voi_request(self) -> Dict[str, Any]:
        return {
            'gap_type': self.gap_type,
            'description': self.description,
            'severity': self.severity,
            'belief_id': self.belief_id,
            'missing_evidence': self.missing_evidence,
            'target_population': self.target_population,
            'target_variable': self.target_variable,
        }


@dataclass
class QuineanCounterfactualResult:
    """Complete counterfactual result with Quinean annotations (ECB-3.2)."""
    query: CounterfactualQuery
    point_estimate: float
    uncertainty: float
    theory_results: Dict[str, TheoryCounterfactual]
    robustness: RobustnessAnalysis
    coherence: CoherenceAssessment
    scope: ScopeAssessment
    contrast: ContrastAssessment
    epistemic_quality: float
    warnings: List[str]
    is_defined: bool = True
    reason_undefined: Optional[str] = None
    gaps: List[EpistemicGap] = field(default_factory=list)


@dataclass
class BeliefChange:
    """Change in a belief due to hypothetical evidence."""
    belief_id: str
    old_credence: float
    new_credence: float
    credence_delta: float
    old_status: Any  # BeliefStatus
    new_status: Any  # BeliefStatus
    status_changed: bool


@dataclass
class TheoryImpact:
    """Impact on a theory's standing."""
    theory_id: str
    old_probability: float
    new_probability: float
    direction: str


@dataclass
class EpistemicCounterfactualResult:
    """Result of 'What would we believe if...?' query."""
    hypothetical_evidence: Dict[str, Any]
    original_coherence: float
    hypothetical_coherence: float
    belief_changes: List[BeliefChange]
    major_shifts: List[BeliefChange]
    status_flips: List[BeliefChange]
    theory_impacts: Dict[str, TheoryImpact]


@dataclass
class ExcludedBelief:
    """Record of a belief excluded from causal model building (D2.6b)."""
    belief_id: str
    theory_id: str
    reason: str
    details: str
    credence: Optional[float] = None
    level: Optional[str] = None
    threshold_used: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'belief_id': self.belief_id,
            'theory_id': self.theory_id,
            'reason': self.reason,
            'details': self.details,
            'credence': self.credence,
            'level': self.level,
            'threshold_used': self.threshold_used,
        }


@dataclass
class GeneralizationAssessment:
    """Assessment of belief generalization across contexts."""
    belief_id: str
    source_context: Any  # PopulationContext
    target_context: Any  # PopulationContext
    target_individual: Optional[Any] = None
    similarity_score: float = 0.0
    generalization_type: str = ""
    adjustment_factor: float = 1.0
    original_estimate: float = 0.0
    generalized_estimate: float = 0.0
    generalization_uncertainty: float = 0.0
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


__all__ = [
    "CounterfactualQuery",
    "TheoryCounterfactual",
    "RobustnessAnalysis",
    "CoherenceViolation",
    "CoherenceAssessment",
    "ScopeAssessment",
    "ContrastAssessment",
    "EpistemicGap",
    "QuineanCounterfactualResult",
    "BeliefChange",
    "TheoryImpact",
    "EpistemicCounterfactualResult",
    "ExcludedBelief",
    "GeneralizationAssessment",
]
