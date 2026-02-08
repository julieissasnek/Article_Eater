"""
Article Eater - Epistemic-Causal Integration Module
====================================================

Version: 0.1 (Sprint 1.5 Design Implementation)
Date: January 2026

This module implements the integration between:
1. Quinean epistemic layer (beliefs, credences, entrenchment, coherence)
2. Pearlian causal layer (DAGs, CPTs, do-calculus, counterfactuals)
3. Van Fraassen contrast classes (population-relative, culturally-situated)
4. Argument structure (attacks as contrast manipulations)

Key Architectural Principle:
    The epistemic layer is PRIOR to the causal layer. You cannot build
    a causal model without knowing what the field believes. The epistemic
    layer constrains, informs, and qualifies causal inference.

References:
- Pearl, J. (2009). Causality. Cambridge University Press.
- Quine, W.V.O. (1951). Two Dogmas of Empiricism. Philosophical Review.
- Van Fraassen, B. (1980). The Scientific Image. Oxford University Press.
- BonJour, L. (1985). The Structure of Empirical Knowledge. Harvard.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple, Set, Callable, Union
from enum import Enum
from datetime import datetime, timezone
from abc import ABC, abstractmethod
import math
import copy
import logging
from collections import defaultdict
from functools import reduce
import operator

logger = logging.getLogger(__name__)


# =============================================================================
# PART 1: FOUNDATIONAL ENUMS AND TYPES
# =============================================================================

class EpistemicLevel(Enum):
    """Levels in the Quinean web, from center to periphery."""
    THEORETICAL = "theoretical"
    INTERMEDIATE = "intermediate"
    EMPIRICAL = "empirical"
    OBSERVATIONAL = "observational"


class BeliefStatus(Enum):
    """Status of a belief in the web."""
    STUB = "stub"
    TENTATIVE = "tentative"
    ESTABLISHED = "established"
    ENTRENCHED = "entrenched"
    ANOMALOUS = "anomalous"


class ConstraintType(Enum):
    """Types of epistemic constraint."""
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    PARTIAL_SUPPORT = "partial_support"
    EXPLAINS = "explains"
    INSTANTIATES = "instantiates"
    ANALOGOUS = "analogous"
    INDEPENDENT = "independent"


class ContrastType(Enum):
    """Types of contrast class (van Fraassen)."""
    NULL = "null"                    # Intervention vs. no intervention
    ALTERNATIVE = "alternative"      # Intervention A vs. Intervention B
    GRADIENT = "gradient"            # Levels of intervention
    FACTORIAL = "factorial"          # Multiple factors
    POPULATION = "population"        # This population vs. that population


class AttackType(Enum):
    """Types of argument attack."""
    CONFOUNDER = "confounder"
    BOUNDARY_CONDITION = "boundary_condition"
    OVERGENERALIZATION = "overgeneralization"
    MECHANISM = "mechanism"
    MEASUREMENT = "measurement"
    REPLICATION = "replication"
    DOSE_RESPONSE = "dose_response"
    TEMPORAL = "temporal"


class ContrastShiftType(Enum):
    """How an attack shifts the contrast class."""
    PRESERVING = "preserving"        # Same contrast, disputes finding
    POPULATION_SHIFT = "population"  # Different population
    BASELINE_SHIFT = "baseline"      # Different baseline level
    MEANING_SHIFT = "meaning"        # Different cultural/contextual meaning
    ALTERNATIVE_SHIFT = "alternative"  # Different comparison condition
    COMPLEX_SHIFT = "complex"        # Multiple shifts


# =============================================================================
# PART 2: CORE EPISTEMIC STRUCTURES
# =============================================================================

@dataclass
class Credence:
    """Credence with meta-uncertainty."""
    value: float
    uncertainty: float
    n_supporting: int = 0
    n_contradicting: int = 0
    n_observations: int = 0
    
    def __post_init__(self):
        self.value = max(0.01, min(0.99, self.value))
        self.uncertainty = max(0.0, min(1.0, self.uncertainty))
    
    def confidence_interval(self, level: float = 0.95) -> Tuple[float, float]:
        z = 1.96 if level == 0.95 else 2.576
        half_width = self.uncertainty * z
        return (max(0, self.value - half_width), min(1, self.value + half_width))
    
    def update(self, supports: Optional[bool], strength: float = 0.5) -> Credence:
        """Bayesian update."""
        if supports is True:
            lr = (0.6 + 0.4 * strength) / (0.4 - 0.2 * strength)
        elif supports is False:
            lr = (0.4 - 0.2 * strength) / (0.6 + 0.4 * strength)
        else:
            lr = 0.95
        
        prior_odds = self.value / (1 - self.value + 1e-10)
        posterior_odds = prior_odds * lr
        new_value = posterior_odds / (1 + posterior_odds)
        
        return Credence(
            value=new_value,
            uncertainty=self.uncertainty * 0.95,
            n_supporting=self.n_supporting + (1 if supports else 0),
            n_contradicting=self.n_contradicting + (1 if supports is False else 0),
            n_observations=self.n_observations + 1
        )


@dataclass
class Belief:
    """A belief in the Quinean web with contrast class metadata."""
    belief_id: str
    content: str
    level: EpistemicLevel
    status: BeliefStatus = BeliefStatus.STUB
    credence: Credence = field(default_factory=lambda: Credence(0.5, 0.4))
    entrenchment: float = 0.5
    
    # Theory attachment (multi-theory)
    theory_ids: Dict[str, float] = field(default_factory=dict)
    
    # Source information
    paper_ids: List[str] = field(default_factory=list)
    
    # Van Fraassen: Contrast class specification
    contrast_class: Optional[ContrastClass] = None
    
    # Scope constraints
    scope: Optional[BeliefScope] = None
    
    # Justificatory dependencies
    depends_on: Set[str] = field(default_factory=set)
    provides_warrant_to: Set[str] = field(default_factory=set)
    
    # Metadata
    domain: str = ""
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    @property
    def theory_id(self) -> Optional[str]:
        """Primary theory (backward compatibility)."""
        if not self.theory_ids:
            return None
        return max(self.theory_ids, key=self.theory_ids.get)
    
    def is_stub(self) -> bool:
        return self.status == BeliefStatus.STUB
    
    def is_anomalous(self) -> bool:
        return self.status == BeliefStatus.ANOMALOUS


# =============================================================================
# PART 3: VAN FRAASSEN CONTRAST CLASS STRUCTURES
# =============================================================================

@dataclass
class ConditionSpec:
    """Specification of a condition in a contrast."""
    variable: str
    value: Any
    description: str
    contextual_meaning: Dict[str, str] = field(default_factory=dict)


@dataclass
class BaselineSpec:
    """Baseline level of a variable in a population."""
    variable: str
    typical_value: float
    variance: float
    characterization: str  # "very_low", "low", "moderate", "high", "saturated"
    source_studies: List[str] = field(default_factory=list)
    temporal_variation: Optional[Dict[str, float]] = None
    
    def is_saturated(self) -> bool:
        return self.characterization in ["high", "saturated"]
    
    def distance_from(self, other: BaselineSpec) -> float:
        """Compute normalized distance between baselines."""
        levels = ["very_low", "low", "moderate", "high", "saturated"]
        try:
            self_idx = levels.index(self.characterization)
            other_idx = levels.index(other.characterization)
            return abs(self_idx - other_idx) / (len(levels) - 1)
        except ValueError:
            return 0.5


@dataclass
class CulturalMeaning:
    """Cultural meaning of a construct."""
    culture: str
    meaning: str
    associations: List[str]
    valence: str
    behavioral_implications: str


@dataclass
class PopulationContext:
    """
    Population context defining the contrast class.
    
    This is where van Fraassen meets cultural psychology.
    The population context determines what the "baseline" is,
    which in turn determines what the contrast means.
    """
    population_id: str
    region: Optional[str] = None
    culture: Optional[str] = None
    
    # Baseline levels for key variables
    baselines: Dict[str, BaselineSpec] = field(default_factory=dict)
    
    # Cultural meanings of constructs
    cultural_meanings: Dict[str, CulturalMeaning] = field(default_factory=dict)
    
    # Individual difference distributions
    individual_difference_distributions: Dict[str, DistributionSpec] = field(
        default_factory=dict
    )
    
    def get_baseline(self, variable: str) -> Optional[BaselineSpec]:
        return self.baselines.get(variable)
    
    def get_meaning(self, construct: str) -> Optional[CulturalMeaning]:
        return self.cultural_meanings.get(construct)


@dataclass
class DistributionSpec:
    """Distribution of an individual difference in a population."""
    mean: float
    sd: float
    skew: float = 0.0
    note: str = ""


@dataclass
class ContrastClass:
    """
    Van Fraassen contrast class specification.
    
    A contrast class defines WHAT QUESTION a finding answers.
    "Why P rather than Q?" has different answers depending on Q.
    """
    contrast_id: str
    
    # The focal condition
    focal: ConditionSpec
    
    # The contrast conditions
    contrasts: List[ConditionSpec]
    
    # Type of contrast
    contrast_type: ContrastType
    
    # Population context
    population_context: PopulationContext
    
    # Explicit vs. implicit
    explicit: bool = False
    source: str = "inferred"
    
    def describe(self) -> str:
        """Human-readable description of the contrast."""
        focal_desc = self.focal.description
        contrast_descs = [c.description for c in self.contrasts]
        return f"{focal_desc} rather than {', '.join(contrast_descs)}"
    
    def involves_variable(self, variable: str) -> bool:
        if self.focal.variable == variable:
            return True
        return any(c.variable == variable for c in self.contrasts)


@dataclass
class BeliefScope:
    """
    Scope constraints on a belief.
    
    Reframed in van Fraassen terms: scope specifies which
    contrast classes have been tested vs. assumed.
    """
    populations: List[str] = field(default_factory=list)
    settings: List[str] = field(default_factory=list)
    temporal_bounds: Optional[Tuple[float, float]] = None
    
    # Evidence coverage
    n_studies: int = 0
    population_coverage: Dict[str, int] = field(default_factory=dict)
    setting_coverage: Dict[str, int] = field(default_factory=dict)
    
    # Van Fraassen: Which contrasts have been tested?
    tested_contrasts: List[ContrastClass] = field(default_factory=list)
    untested_contrasts: List[ContrastClass] = field(default_factory=list)
    assumed_contrasts: List[ContrastClass] = field(default_factory=list)
    
    def coverage_for(self, population: str) -> float:
        """Proportion of studies covering this population."""
        if self.n_studies == 0:
            return 0.0
        return self.population_coverage.get(population, 0) / self.n_studies


# =============================================================================
# PART 4: INDIVIDUAL DIFFERENCES
# =============================================================================

@dataclass
class IndividualDifferenceProfile:
    """Individual difference profile for personalized inference."""
    
    # Trait factors
    chronotype: Optional[float] = None  # MEQ score
    nature_connectedness: Optional[float] = None  # CNS score
    big_five: Dict[str, float] = field(default_factory=dict)
    
    # State factors
    current_stress: Optional[float] = None
    current_fatigue: Optional[float] = None
    baseline_mood: Optional[float] = None
    
    # History/context
    typical_nature_exposure: Optional[float] = None  # hours/week
    typical_sunlight_exposure: Optional[float] = None
    urbanicity: Optional[float] = None
    
    # Cultural
    cultural_background: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in self.__dict__.items() if v is not None}


@dataclass
class IndividualDifferenceFactor:
    """Specification of how an individual difference affects inference."""
    factor_id: str
    construct: str
    measures: List[str]
    
    # Effect on baseline
    effect_on_baseline: Dict[str, str]
    
    # Effect on intervention response
    effect_on_response: Dict[str, str]
    
    # Research references
    key_references: List[str] = field(default_factory=list)
    
    # Cultural interactions
    cultural_interactions: Dict[str, str] = field(default_factory=dict)
    
    def compute_modifier(
        self,
        individual_value: float,
        belief: Belief,
        context: PopulationContext
    ) -> Tuple[float, str]:
        """Compute effect modifier for an individual."""
        # Default implementation - subclasses can override
        # Returns (multiplier, explanation)
        return (1.0, "No specific modifier computed")


# =============================================================================
# PART 5: ARGUMENT STRUCTURE
# =============================================================================

@dataclass
class ArgumentAttack:
    """
    An argument attack with contrast class analysis.
    
    Key insight: Many attacks are contrast shifts, not refutations.
    """
    attack_id: str
    source_paper_id: str
    target_belief_id: str
    attack_type: AttackType
    
    # The attack claim
    attack_claim: str
    attack_credence: float
    
    # Contrast class analysis
    original_contrast: Optional[ContrastClass] = None
    shifted_contrast: Optional[ContrastClass] = None
    shift_type: ContrastShiftType = ContrastShiftType.PRESERVING
    
    # Outcome specification
    outcome_under_original: Optional[str] = None
    outcome_under_shifted: Optional[str] = None
    
    # Resolution
    resolution: Optional[str] = None
    resolution_credence: Optional[float] = None
    
    def is_contrast_preserving(self) -> bool:
        return self.shift_type == ContrastShiftType.PRESERVING
    
    def is_contrast_shifting(self) -> bool:
        return self.shift_type != ContrastShiftType.PRESERVING


@dataclass
class AttackContrastAnalysis:
    """Analysis of how an attack relates to contrast class."""
    attack_id: str
    analysis_type: str  # "preserving" or "shifting"
    
    original_contrast: ContrastClass
    attack_contrast: ContrastClass
    
    shift_type: Optional[ContrastShiftType] = None
    
    implication: str = ""
    resolution_approach: str = ""
    
    # Both may be valid for shifting attacks
    original_validity: str = ""
    attack_validity: str = ""


# =============================================================================
# PART 6: CAUSAL LAYER STRUCTURES
# =============================================================================

@dataclass
class Variable:
    """A variable in the causal model."""
    var_id: str
    name: str
    var_type: str  # "continuous", "binary", "categorical"
    domain: Optional[Tuple[float, float]] = None
    categories: Optional[List[str]] = None


@dataclass
class StructuralEquation:
    """
    A structural equation: Y = f(parents, U).
    
    Extended with epistemic metadata from the Quinean layer.
    """
    equation_id: str
    outcome_var: str
    parent_vars: List[str]
    
    # Functional form
    functional_form: str  # "linear", "threshold", "u_shaped", etc.
    parameters: Dict[str, float] = field(default_factory=dict)
    
    # Epistemic metadata (from Quinean layer)
    supporting_beliefs: List[str] = field(default_factory=list)
    credence: float = 0.5
    uncertainty: float = 0.3
    entrenchment: float = 0.3
    
    # Theory attachment
    theory_id: Optional[str] = None
    
    def compute(self, parent_values: Dict[str, float], noise: float = 0.0) -> float:
        """Compute outcome given parent values."""
        if self.functional_form == "linear":
            result = self.parameters.get("intercept", 0.0)
            for var in self.parent_vars:
                coef = self.parameters.get(f"beta_{var}", 0.0)
                result += coef * parent_values.get(var, 0.0)
            return result + noise
        
        elif self.functional_form == "threshold":
            threshold = self.parameters.get("threshold", 0.0)
            effect = self.parameters.get("effect", 1.0)
            total_input = sum(parent_values.get(v, 0) for v in self.parent_vars)
            return effect if total_input > threshold else 0.0
        
        elif self.functional_form == "u_shaped":
            optimal = self.parameters.get("optimal", 0.5)
            scale = self.parameters.get("scale", 1.0)
            x = parent_values.get(self.parent_vars[0], 0.0) if self.parent_vars else 0.0
            return scale * (1 - (x - optimal) ** 2)
        
        else:
            raise ValueError(f"Unknown functional form: {self.functional_form}")


@dataclass
class TheoryRelativeModel:
    """
    A causal model relative to a specific theory.
    
    Different theories may propose different structural equations
    for the same outcome.
    """
    model_id: str
    theory_id: str
    theory_credence: float
    
    variables: Dict[str, Variable] = field(default_factory=dict)
    equations: Dict[str, StructuralEquation] = field(default_factory=dict)
    
    # DAG representation
    edges: List[Tuple[str, str]] = field(default_factory=list)
    
    def get_parents(self, var: str) -> List[str]:
        return [src for src, tgt in self.edges if tgt == var]
    
    def get_children(self, var: str) -> List[str]:
        return [tgt for src, tgt in self.edges if src == var]
    
    def topological_sort(self) -> List[str]:
        """Return variables in topological order."""
        in_degree = defaultdict(int)
        for _, tgt in self.edges:
            in_degree[tgt] += 1
        
        queue = [v for v in self.variables if in_degree[v] == 0]
        result = []
        
        while queue:
            var = queue.pop(0)
            result.append(var)
            for child in self.get_children(var):
                in_degree[child] -= 1
                if in_degree[child] == 0:
                    queue.append(child)
        
        return result


@dataclass
class MultiTheoryModel:
    """Collection of theory-relative models for integrated inference."""
    domain: str
    theory_models: Dict[str, TheoryRelativeModel] = field(default_factory=dict)
    theory_credences: Dict[str, float] = field(default_factory=dict)
    
    def add_theory_model(self, model: TheoryRelativeModel):
        self.theory_models[model.theory_id] = model
        self.theory_credences[model.theory_id] = model.theory_credence
    
    def get_all_variables(self) -> Set[str]:
        all_vars = set()
        for model in self.theory_models.values():
            all_vars.update(model.variables.keys())
        return all_vars


# =============================================================================
# PART 7: COUNTERFACTUAL STRUCTURES
# =============================================================================

@dataclass
class CounterfactualQuery:
    """A counterfactual query with van Fraassen contrast specification."""
    query_id: str
    
    # The intervention
    intervention: Dict[str, float]
    
    # The outcome
    outcome_var: str
    
    # Evidence for abduction
    evidence: Dict[str, float] = field(default_factory=dict)
    
    # Van Fraassen: Explicit contrast class
    contrast_class: Optional[ContrastClass] = None
    contrast_type: ContrastType = ContrastType.NULL
    alternative_interventions: List[Dict[str, float]] = field(default_factory=list)
    
    # Target context for generalization
    target_population: Optional[str] = None
    target_setting: Optional[str] = None
    target_individual: Optional[IndividualDifferenceProfile] = None
    
    def describe(self) -> str:
        interv_str = ", ".join(f"{k}={v}" for k, v in self.intervention.items())
        desc = f"P({self.outcome_var} | do({interv_str}))"
        if self.target_population:
            desc += f" for {self.target_population}"
        return desc


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
    """Van Fraassen assessment of contrast class transfer."""
    source_contrast: ContrastClass
    target_contrast: ContrastClass
    
    contrast_preserved: bool
    contrast_similarity: float
    
    baseline_differences: Dict[str, Tuple[str, str]]  # var -> (source, target)
    meaning_differences: Dict[str, Tuple[str, str]]   # construct -> (source, target)
    
    transfer_type: str
    adjustment_factor: float
    warnings: List[str]


@dataclass
class QuineanCounterfactualResult:
    """Complete counterfactual result with Quinean annotations."""
    query: CounterfactualQuery
    
    # Standard result
    point_estimate: float
    confidence_interval: Tuple[float, float]
    
    # Theory-relative breakdown
    by_theory: Dict[str, TheoryCounterfactual]
    
    # Quinean assessments
    robustness: RobustnessAnalysis
    coherence: CoherenceAssessment
    scope: ScopeAssessment
    contrast: ContrastAssessment
    
    # Overall quality
    epistemic_quality: float
    
    # Warnings
    warnings: List[str]
    
    def summary(self) -> str:
        lines = [
            f"=== Counterfactual Result ===",
            f"Query: {self.query.describe()}",
            f"",
            f"Point estimate: {self.point_estimate:.3f}",
            f"95% CI: [{self.confidence_interval[0]:.3f}, {self.confidence_interval[1]:.3f}]",
            f"",
            f"Epistemic quality: {self.epistemic_quality:.2f}",
            f"  Robustness: {self.robustness.robustness_score:.2f}",
            f"  Coherence: {self.coherence.coherence_score:.2f}",
            f"  Scope match: {self.scope.scope_score:.2f}",
            f"  Contrast transfer: {self.contrast.contrast_similarity:.2f}",
        ]
        
        if self.warnings:
            lines.append(f"\nWarnings:")
            for w in self.warnings:
                lines.append(f"  ⚠ {w}")
        
        lines.append(f"\nBy theory:")
        for tid, tcf in self.by_theory.items():
            lines.append(f"  {tid}: {tcf.estimate:.3f} (weight: {tcf.theory_credence:.2f})")
        
        return "\n".join(lines)


# =============================================================================
# PART 8: EPISTEMIC COUNTERFACTUALS
# =============================================================================

@dataclass
class BeliefChange:
    """Change in a belief due to hypothetical evidence."""
    belief_id: str
    old_credence: float
    new_credence: float
    credence_delta: float
    old_status: BeliefStatus
    new_status: BeliefStatus
    status_changed: bool


@dataclass
class TheoryImpact:
    """Impact on a theory's standing."""
    theory_id: str
    old_probability: float
    new_probability: float
    direction: str  # "strengthened", "weakened", "unchanged"


@dataclass
class EpistemicCounterfactualResult:
    """Result of "What would we believe if...?" query."""
    hypothetical_evidence: Dict[str, Any]
    
    original_coherence: float
    hypothetical_coherence: float
    
    belief_changes: List[BeliefChange]
    major_shifts: List[BeliefChange]
    status_flips: List[BeliefChange]
    
    theory_impacts: Dict[str, TheoryImpact]
    
    def summary(self) -> str:
        lines = [
            "=== Epistemic Counterfactual ===",
            f"Coherence: {self.original_coherence:.2f} → {self.hypothetical_coherence:.2f}",
            f"Major shifts: {len(self.major_shifts)}",
            f"Status flips: {len(self.status_flips)}",
        ]
        
        if self.major_shifts:
            lines.append("\nMajor belief changes:")
            for bc in self.major_shifts[:5]:
                lines.append(f"  {bc.belief_id}: {bc.old_credence:.2f} → {bc.new_credence:.2f}")
        
        if self.theory_impacts:
            lines.append("\nTheory impacts:")
            for tid, ti in self.theory_impacts.items():
                lines.append(f"  {tid}: {ti.direction} ({ti.old_probability:.2f} → {ti.new_probability:.2f})")
        
        return "\n".join(lines)


# =============================================================================
# PART 9: GENERALIZATION ASSESSMENT
# =============================================================================

@dataclass
class GeneralizationAssessment:
    """Assessment of belief generalization across contexts."""
    belief_id: str
    source_context: PopulationContext
    target_context: PopulationContext
    target_individual: Optional[IndividualDifferenceProfile]
    
    source_contrast: ContrastClass
    target_contrast: ContrastClass
    
    generalization_type: str
    adjustment_factor: float
    
    original_estimate: float
    generalized_estimate: float
    generalization_uncertainty: float
    
    warnings: List[str]
    recommendations: List[str]
    
    def summary(self) -> str:
        lines = [
            f"=== Generalization Assessment ===",
            f"Belief: {self.belief_id}",
            f"Source: {self.source_context.population_id}",
            f"Target: {self.target_context.population_id}",
            f"Type: {self.generalization_type}",
            f"",
            f"Original: {self.original_estimate:.2f}",
            f"Adjusted: {self.generalized_estimate:.2f} ± {self.generalization_uncertainty:.2f}",
            f"Adjustment factor: {self.adjustment_factor:.2f}",
        ]
        
        if self.warnings:
            lines.append("\nWarnings:")
            for w in self.warnings:
                lines.append(f"  ⚠ {w}")
        
        return "\n".join(lines)


# =============================================================================
# PART 10: THE EPISTEMIC-CAUSAL BRIDGE
# =============================================================================

class EpistemicCausalBridge:
    """
    Bridge between Quinean epistemic layer and Pearlian causal layer.
    
    This is the core integration class that implements:
    1. Extraction of causal models from epistemic web
    2. Epistemic constraints on counterfactual inference
    3. Van Fraassen contrast class handling
    4. Generalization with individual/cultural differences
    """
    
    def __init__(self, web: 'WebOfBelief'):
        self.web = web
        self.multi_theory_model: Optional[MultiTheoryModel] = None
        self.population_contexts: Dict[str, PopulationContext] = {}
        self.individual_factors: Dict[str, IndividualDifferenceFactor] = {}
    
    # =========================================================================
    # MODEL CONSTRUCTION
    # =========================================================================
    
    def build_causal_models(
        self,
        credence_threshold: float = 0.5,
        include_theories: Optional[List[str]] = None
    ) -> MultiTheoryModel:
        """
        Build causal models from the epistemic web.
        
        Key principle: The causal layer is derived from the epistemic layer.
        High-credence beliefs become structural equations; constraints become edges.
        """
        theories = include_theories or list(self.web.theory_ids)
        
        self.multi_theory_model = MultiTheoryModel(domain=self.web.domain)
        
        for theory_id in theories:
            theory_beliefs = self._get_theory_beliefs(theory_id, credence_threshold)
            
            if theory_beliefs:
                model = self._build_theory_model(theory_id, theory_beliefs)
                self.multi_theory_model.add_theory_model(model)
        
        return self.multi_theory_model
    
    def _get_theory_beliefs(
        self,
        theory_id: str,
        credence_threshold: float,
        check_enabling: bool = True
    ) -> List[Belief]:
        """Get beliefs supporting a theory above credence threshold.

        Compatible with both:
        - New Belief class with theory_ids: Dict[str, float]
        - Existing Belief class with theory_id: Optional[str]

        P-EC-R9 (Cartwright): Check enabling_conditions before including
        beliefs in counterfactual computation. Beliefs with unmet enabling
        conditions are tracked but excluded from causal models.

        Args:
            theory_id: The theory to get beliefs for
            credence_threshold: Minimum credence to include
            check_enabling: If True, exclude beliefs with unmet enabling conditions
        """
        result = []
        for b in self.web.beliefs.values():
            # Check theory membership (handle both singular and plural)
            if hasattr(b, 'theory_ids') and isinstance(b.theory_ids, dict):
                # New format: theory_ids is a dict
                belongs_to_theory = theory_id in b.theory_ids
            elif hasattr(b, 'theory_id'):
                # Old format: theory_id is a string
                belongs_to_theory = b.theory_id == theory_id
            else:
                belongs_to_theory = False

            if not belongs_to_theory:
                continue

            # Check credence threshold
            if b.credence.value < credence_threshold:
                continue

            # Check level (handle both enum and string)
            level_val = b.level.value if hasattr(b.level, 'value') else b.level
            if level_val not in ['theoretical', 'intermediate']:
                continue

            # P-EC-R9: Check enabling conditions
            if check_enabling and not self._check_enabling_conditions(b):
                self._track_blocked_belief(b, theory_id)
                continue

            result.append(b)

        return result

    def _check_enabling_conditions(self, belief: Belief) -> bool:
        """
        Check if a belief's enabling conditions are met.

        P-EC-R9 (Cartwright): Beliefs with enabling conditions that aren't
        met should not contribute to counterfactual inference because the
        capacity may not manifest.

        Returns True if:
        - Belief has no enabling conditions (no constraints)
        - Enabling conditions are empty (not specified)
        - All specified enabling conditions are satisfied

        Note: Currently we cannot verify enabling conditions against actual
        context, so we check for explicit blocking_factors only.
        """
        if not hasattr(belief, 'enabling_conditions') or belief.enabling_conditions is None:
            return True  # No conditions specified

        ec = belief.enabling_conditions

        # Check if enabling conditions are empty
        if hasattr(ec, 'is_empty') and ec.is_empty():
            return True

        # Check for explicit blocking factors
        # If blocking factors are specified, we assume they might be present
        # unless we have explicit context saying otherwise
        if hasattr(ec, 'blocking_factors') and ec.blocking_factors:
            # Log warning but don't block - we can't verify
            logger.debug(
                f"Belief {belief.belief_id} has blocking_factors: {ec.blocking_factors}. "
                "Cannot verify if blocking factors are absent in query context."
            )

        # Check for required concurrent factors
        if hasattr(ec, 'concurrent_factors') and ec.concurrent_factors:
            logger.debug(
                f"Belief {belief.belief_id} requires concurrent factors: {ec.concurrent_factors}. "
                "Cannot verify presence in query context."
            )

        # For now, return True but track the belief as having conditions
        # A more sophisticated implementation would check against query context
        return True

    def _track_blocked_belief(self, belief: Belief, theory_id: str) -> None:
        """Track beliefs blocked due to unmet enabling conditions."""
        if not hasattr(self, '_blocked_beliefs'):
            self._blocked_beliefs = []

        self._blocked_beliefs.append({
            'belief_id': belief.belief_id,
            'theory_id': theory_id,
            'reason': 'unmet_enabling_conditions',
            'enabling_conditions': self._serialize_enabling_conditions(belief)
        })

    def _serialize_enabling_conditions(self, belief: Belief) -> Optional[Dict[str, Any]]:
        """Serialize enabling conditions for logging."""
        if not hasattr(belief, 'enabling_conditions') or belief.enabling_conditions is None:
            return None

        ec = belief.enabling_conditions
        return {
            'minimum_exposure': getattr(ec, 'minimum_exposure', None),
            'baseline_state': getattr(ec, 'baseline_state', None),
            'concurrent_factors': getattr(ec, 'concurrent_factors', []),
            'blocking_factors': getattr(ec, 'blocking_factors', []),
            'threshold': getattr(ec, 'threshold', None),
            'dosage': getattr(ec, 'dosage', None)
        }

    def get_blocked_beliefs(self) -> List[Dict[str, Any]]:
        """Get list of beliefs blocked due to unmet enabling conditions."""
        return getattr(self, '_blocked_beliefs', [])
    
    def _build_theory_model(
        self,
        theory_id: str,
        beliefs: List[Belief]
    ) -> TheoryRelativeModel:
        """Build a causal model from theory-specific beliefs."""
        
        # Extract variables
        variables = self._extract_variables(beliefs)
        
        # Extract edges from constraints
        edges = self._extract_edges(beliefs)
        
        # Build structural equations
        equations = self._build_equations(beliefs, variables, edges)
        
        # Get theory credence
        theory_credence = self.web.marginal_theory_probability(theory_id)
        
        return TheoryRelativeModel(
            model_id=f"model_{theory_id}",
            theory_id=theory_id,
            theory_credence=theory_credence,
            variables=variables,
            equations=equations,
            edges=edges
        )
    
    def _extract_variables(self, beliefs: List[Belief]) -> Dict[str, Variable]:
        """Extract variables from belief content."""
        variables = {}
        
        for belief in beliefs:
            # Extract from tags
            for tag in belief.tags:
                if tag.startswith("outcome:"):
                    var_id = tag.split(":")[1]
                    if var_id not in variables:
                        variables[var_id] = Variable(
                            var_id=var_id,
                            name=var_id,
                            var_type="continuous"
                        )
        
        return variables
    
    def _extract_edges(self, beliefs: List[Belief]) -> List[Tuple[str, str]]:
        """Extract causal edges from constraints."""
        edges = []
        
        for constraint in self.web.constraints.values():
            if constraint.constraint_type in [ConstraintType.EXPLAINS, ConstraintType.SUPPORTS]:
                source_belief = self.web.beliefs.get(constraint.source_id)
                target_belief = self.web.beliefs.get(constraint.target_id)
                
                if source_belief and target_belief:
                    # Extract variable IDs from beliefs
                    source_vars = self._get_belief_variables(source_belief)
                    target_vars = self._get_belief_variables(target_belief)
                    
                    for sv in source_vars:
                        for tv in target_vars:
                            if sv != tv:
                                edges.append((sv, tv))
        
        return list(set(edges))  # Deduplicate
    
    def _get_belief_variables(self, belief: Belief) -> List[str]:
        """Extract variable IDs from a belief."""
        vars = []
        for tag in belief.tags:
            if tag.startswith("outcome:") or tag.startswith("exposure:"):
                vars.append(tag.split(":")[1])
        return vars
    
    def _build_equations(
        self,
        beliefs: List[Belief],
        variables: Dict[str, Variable],
        edges: List[Tuple[str, str]]
    ) -> Dict[str, StructuralEquation]:
        """Build structural equations from beliefs and edges."""
        equations = {}
        
        for var_id in variables:
            parents = [src for src, tgt in edges if tgt == var_id]
            
            if parents:
                # Find beliefs that inform this relationship
                supporting_beliefs = self._find_supporting_beliefs(beliefs, var_id, parents)
                
                # Estimate credence from supporting beliefs
                if supporting_beliefs:
                    avg_credence = sum(b.credence.value for b in supporting_beliefs) / len(supporting_beliefs)
                    avg_entrenchment = sum(b.entrenchment for b in supporting_beliefs) / len(supporting_beliefs)
                else:
                    avg_credence = 0.5
                    avg_entrenchment = 0.3
                
                equations[var_id] = StructuralEquation(
                    equation_id=f"eq_{var_id}",
                    outcome_var=var_id,
                    parent_vars=parents,
                    functional_form="linear",  # Default
                    parameters={f"beta_{p}": 0.5 for p in parents},
                    supporting_beliefs=[b.belief_id for b in supporting_beliefs],
                    credence=avg_credence,
                    entrenchment=avg_entrenchment
                )
        
        return equations
    
    def _find_supporting_beliefs(
        self,
        beliefs: List[Belief],
        outcome: str,
        parents: List[str]
    ) -> List[Belief]:
        """Find beliefs that support a causal relationship."""
        supporting = []
        for belief in beliefs:
            belief_vars = self._get_belief_variables(belief)
            if outcome in belief_vars and any(p in belief_vars for p in parents):
                supporting.append(belief)
        return supporting
    
    # =========================================================================
    # COUNTERFACTUAL INFERENCE
    # =========================================================================
    
    def counterfactual(
        self,
        intervention: Dict[str, float],
        outcome: str,
        evidence: Optional[Dict[str, float]] = None,
        contrast_class: Optional[ContrastClass] = None,
        target_population: Optional[str] = None,
        target_individual: Optional[IndividualDifferenceProfile] = None
    ) -> QuineanCounterfactualResult:
        """
        Compute counterfactual with full Quinean analysis.
        
        Steps:
        1. Compute counterfactual under each theory
        2. Weight by theory credence
        3. Assess robustness (how much would web need to change?)
        4. Check coherence (is this counterfactual consistent with the web?)
        5. Evaluate scope (is this within evidential support?)
        6. Assess contrast transfer (van Fraassen)
        7. Apply adjustments and generate warnings
        """
        
        if self.multi_theory_model is None:
            self.build_causal_models()
        
        query = CounterfactualQuery(
            query_id=f"cf_{datetime.now().isoformat()}",
            intervention=intervention,
            outcome_var=outcome,
            evidence=evidence or {},
            contrast_class=contrast_class,
            target_population=target_population,
            target_individual=target_individual
        )
        
        # Step 1: Theory-relative counterfactuals
        theory_results = {}
        for theory_id, model in self.multi_theory_model.theory_models.items():
            tcf = self._compute_theory_counterfactual(query, model)
            theory_results[theory_id] = tcf
        
        # Step 2: Weighted integration
        point_estimate, ci = self._integrate_theory_results(theory_results)
        
        # Step 3: Robustness analysis
        robustness = self._analyze_robustness(query, theory_results)
        
        # Step 4: Coherence check
        coherence = self._check_coherence(query, theory_results)
        
        # Step 5: Scope assessment
        scope = self._assess_scope(query, theory_results)
        
        # Step 6: Contrast transfer (van Fraassen)
        contrast = self._assess_contrast_transfer(query, theory_results)
        
        # Step 7: Apply adjustments
        adjusted_estimate = point_estimate
        warnings = []
        
        if scope.suggested_penalty > 0:
            adjusted_estimate *= (1 - scope.suggested_penalty)
            warnings.append(
                f"Estimate reduced by {scope.suggested_penalty:.0%} due to scope extrapolation"
            )
        
        if contrast.adjustment_factor != 1.0:
            adjusted_estimate *= contrast.adjustment_factor
            warnings.append(
                f"Estimate adjusted by {contrast.adjustment_factor:.2f} due to contrast class differences"
            )
        
        warnings.extend(scope.extrapolation_warnings)
        warnings.extend(contrast.warnings)
        
        if not coherence.is_coherent:
            for v in coherence.violations:
                warnings.append(f"Coherence: {v.description}")
        
        # Compute epistemic quality
        epistemic_quality = (
            0.25 * robustness.robustness_score +
            0.25 * coherence.coherence_score +
            0.25 * scope.scope_score +
            0.25 * contrast.contrast_similarity
        )
        
        return QuineanCounterfactualResult(
            query=query,
            point_estimate=adjusted_estimate,
            confidence_interval=self._adjust_ci(ci, scope, contrast),
            by_theory=theory_results,
            robustness=robustness,
            coherence=coherence,
            scope=scope,
            contrast=contrast,
            epistemic_quality=epistemic_quality,
            warnings=warnings
        )
    
    def _compute_theory_counterfactual(
        self,
        query: CounterfactualQuery,
        model: TheoryRelativeModel
    ) -> TheoryCounterfactual:
        """Compute counterfactual under a single theory."""
        
        # Simple forward propagation (for more complex, use do-calculus)
        values = dict(query.evidence)
        values.update(query.intervention)
        
        # Propagate through equations in topological order
        for var in model.topological_sort():
            if var in values:
                continue
            if var in model.equations:
                eq = model.equations[var]
                values[var] = eq.compute(values)
        
        estimate = values.get(query.outcome_var, 0.5)
        
        # Find mechanism path
        path = self._trace_path(model, list(query.intervention.keys()), query.outcome_var)
        
        # Find supporting beliefs
        supporting = []
        for eq in model.equations.values():
            supporting.extend(eq.supporting_beliefs)
        
        # Compute CI based on equation uncertainties
        uncertainty = self._compute_path_uncertainty(model, path)
        ci = (estimate - 1.96 * uncertainty, estimate + 1.96 * uncertainty)
        
        return TheoryCounterfactual(
            theory_id=model.theory_id,
            theory_credence=model.theory_credence,
            estimate=estimate,
            confidence_interval=ci,
            mechanism_path=path,
            supporting_beliefs=list(set(supporting))
        )
    
    def _trace_path(
        self,
        model: TheoryRelativeModel,
        sources: List[str],
        target: str
    ) -> List[str]:
        """Trace causal path from sources to target."""
        # BFS to find path
        visited = set()
        queue = [(s, [s]) for s in sources]
        
        while queue:
            current, path = queue.pop(0)
            if current == target:
                return path
            if current in visited:
                continue
            visited.add(current)
            
            for child in model.get_children(current):
                queue.append((child, path + [child]))
        
        return sources  # No path found
    
    def _compute_path_uncertainty(
        self,
        model: TheoryRelativeModel,
        path: List[str]
    ) -> float:
        """Compute uncertainty along a causal path."""
        uncertainties = []
        for var in path:
            if var in model.equations:
                eq = model.equations[var]
                uncertainties.append(1 - eq.credence)  # Higher credence = lower uncertainty
        
        if not uncertainties:
            return 0.3
        
        # Combine uncertainties (they compound)
        combined = 1 - reduce(operator.mul, [1 - u for u in uncertainties], 1.0)
        return min(0.5, combined)
    
    def _integrate_theory_results(
        self,
        theory_results: Dict[str, TheoryCounterfactual]
    ) -> Tuple[float, Tuple[float, float]]:
        """Integrate results across theories."""
        if not theory_results:
            return (0.5, (0.25, 0.75))
        
        total_weight = sum(tcf.theory_credence for tcf in theory_results.values())
        
        if total_weight == 0:
            return (0.5, (0.25, 0.75))
        
        # Weighted mean
        point_estimate = sum(
            tcf.estimate * tcf.theory_credence
            for tcf in theory_results.values()
        ) / total_weight
        
        # CI incorporates between-theory variance
        estimates = [tcf.estimate for tcf in theory_results.values()]
        between_var = sum((e - point_estimate) ** 2 for e in estimates) / len(estimates)
        
        # Average within-theory uncertainty
        avg_within = sum(
            (tcf.confidence_interval[1] - tcf.confidence_interval[0]) / 4
            for tcf in theory_results.values()
        ) / len(theory_results)
        
        combined_se = math.sqrt(between_var + avg_within ** 2)
        ci = (point_estimate - 1.96 * combined_se, point_estimate + 1.96 * combined_se)
        
        return (point_estimate, ci)
    
    # =========================================================================
    # ROBUSTNESS ANALYSIS
    # =========================================================================
    
    def _analyze_robustness(
        self,
        query: CounterfactualQuery,
        theory_results: Dict[str, TheoryCounterfactual]
    ) -> RobustnessAnalysis:
        """Analyze robustness to belief revision."""
        
        # Collect supporting beliefs
        all_supporting = set()
        for tcf in theory_results.values():
            all_supporting.update(tcf.supporting_beliefs)
        
        # Analyze sensitivity of each
        sensitive = []
        for belief_id in all_supporting:
            if belief_id not in self.web.beliefs:
                continue
            
            belief = self.web.beliefs[belief_id]
            
            # Estimate sensitivity (how much would CF change if belief changed?)
            sensitivity = self._estimate_belief_sensitivity(belief_id, query, theory_results)
            
            if sensitivity > 0.1:
                sensitive.append({
                    'belief_id': belief_id,
                    'credence': belief.credence.value,
                    'entrenchment': belief.entrenchment,
                    'sensitivity': sensitivity,
                    'revision_cost': belief.entrenchment * (1 - belief.credence.uncertainty)
                })
        
        sensitive.sort(key=lambda x: x['sensitivity'], reverse=True)
        
        # Compute overall robustness
        if sensitive:
            min_cost = min(s['revision_cost'] for s in sensitive)
            path_entrenchment = sum(s['entrenchment'] for s in sensitive) / len(sensitive)
        else:
            min_cost = 1.0
            path_entrenchment = 0.5
        
        robustness_score = 0.5 * min_cost + 0.5 * path_entrenchment
        
        return RobustnessAnalysis(
            robustness_score=robustness_score,
            min_revision_cost=min_cost,
            sensitive_beliefs=sensitive[:10],
            path_entrenchment=path_entrenchment
        )
    
    def _estimate_belief_sensitivity(
        self,
        belief_id: str,
        query: CounterfactualQuery,
        theory_results: Dict[str, TheoryCounterfactual]
    ) -> float:
        """Estimate how sensitive the counterfactual is to a belief."""
        # Count how many theory results depend on this belief
        count = sum(
            1 for tcf in theory_results.values()
            if belief_id in tcf.supporting_beliefs
        )
        return count / max(1, len(theory_results))
    
    # =========================================================================
    # COHERENCE CHECKING
    # =========================================================================
    
    def _check_coherence(
        self,
        query: CounterfactualQuery,
        theory_results: Dict[str, TheoryCounterfactual]
    ) -> CoherenceAssessment:
        """Check coherence of counterfactual with the web."""
        
        violations = []
        
        # Collect involved beliefs
        involved = set()
        for tcf in theory_results.values():
            involved.update(tcf.supporting_beliefs)
        
        # Check for severed warrant
        for belief_id in involved:
            if belief_id not in self.web.beliefs:
                continue
            belief = self.web.beliefs[belief_id]
            
            for dep_id in belief.depends_on:
                if dep_id not in self.web.beliefs:
                    continue
                dep = self.web.beliefs[dep_id]
                
                if dep.credence.value < 0.3 and belief.credence.value > 0.6:
                    violations.append(CoherenceViolation(
                        violation_type="severed_warrant",
                        description=f"'{belief_id}' depends on '{dep_id}' which has low credence",
                        involved_beliefs=[belief_id, dep_id],
                        severity=belief.credence.value - dep.credence.value
                    ))
        
        # Check for contradictions with entrenched beliefs
        for belief in self.web.beliefs.values():
            if belief.entrenchment < 0.6:
                continue
            # Check if counterfactual contradicts this belief
            # (simplified: check if opposite direction)
            # ... implementation depends on belief content structure
        
        # Compute score
        if violations:
            total_severity = sum(v.severity for v in violations)
            coherence_score = max(0, 1 - total_severity / len(violations))
        else:
            coherence_score = 1.0
        
        return CoherenceAssessment(
            is_coherent=len(violations) == 0,
            coherence_score=coherence_score,
            violations=violations,
            required_co_revisions=[]
        )
    
    # =========================================================================
    # SCOPE ASSESSMENT
    # =========================================================================
    
    def _assess_scope(
        self,
        query: CounterfactualQuery,
        theory_results: Dict[str, TheoryCounterfactual]
    ) -> ScopeAssessment:
        """Assess whether counterfactual is within evidential scope."""
        
        warnings = []
        
        # Collect scope from supporting beliefs
        scopes = []
        for tcf in theory_results.values():
            for belief_id in tcf.supporting_beliefs:
                if belief_id in self.web.beliefs:
                    belief = self.web.beliefs[belief_id]
                    if belief.scope:
                        scopes.append(belief.scope)
        
        # Check population match
        if query.target_population and scopes:
            coverages = [s.coverage_for(query.target_population) for s in scopes]
            population_match = sum(coverages) / len(coverages) if coverages else 0.5
            
            if population_match < 0.3:
                warnings.append(
                    f"Target population '{query.target_population}' has limited coverage "
                    f"in evidence base ({population_match:.0%})"
                )
        else:
            population_match = 0.7  # Default if no specific target
        
        # Check setting match
        setting_match = 0.7  # Default
        
        # Check baseline match (requires population context)
        baseline_match = 0.7  # Default
        if query.target_population in self.population_contexts:
            target_ctx = self.population_contexts[query.target_population]
            # Compare baselines... implementation depends on available data
        
        # Overall scope
        scope_score = (population_match + setting_match + baseline_match) / 3
        
        # Suggested penalty
        if scope_score < 0.5:
            suggested_penalty = 0.5 * (1 - scope_score)
        else:
            suggested_penalty = 0.0
        
        return ScopeAssessment(
            in_scope=scope_score >= 0.6,
            scope_score=scope_score,
            population_match=population_match,
            setting_match=setting_match,
            baseline_match=baseline_match,
            extrapolation_warnings=warnings,
            suggested_penalty=suggested_penalty
        )
    
    # =========================================================================
    # VAN FRAASSEN CONTRAST TRANSFER
    # =========================================================================
    
    def _assess_contrast_transfer(
        self,
        query: CounterfactualQuery,
        theory_results: Dict[str, TheoryCounterfactual]
    ) -> ContrastAssessment:
        """Assess contrast class transfer (van Fraassen)."""
        
        warnings = []
        
        # Get source contrast from supporting beliefs
        source_contrast = self._extract_source_contrast(theory_results)
        
        # Build target contrast from query
        target_contrast = self._build_target_contrast(query)
        
        # Compare contrasts
        contrast_preserved = self._contrasts_equivalent(source_contrast, target_contrast)
        contrast_similarity = self._compute_contrast_similarity(source_contrast, target_contrast)
        
        # Identify differences
        baseline_diffs = {}
        meaning_diffs = {}
        
        if source_contrast and target_contrast:
            # Compare baselines
            if source_contrast.population_context and target_contrast.population_context:
                src_ctx = source_contrast.population_context
                tgt_ctx = target_contrast.population_context
                
                for var in set(src_ctx.baselines.keys()) | set(tgt_ctx.baselines.keys()):
                    src_base = src_ctx.baselines.get(var)
                    tgt_base = tgt_ctx.baselines.get(var)
                    
                    if src_base and tgt_base:
                        if src_base.characterization != tgt_base.characterization:
                            baseline_diffs[var] = (
                                src_base.characterization,
                                tgt_base.characterization
                            )
                            warnings.append(
                                f"Baseline for '{var}' differs: "
                                f"{src_base.characterization} → {tgt_base.characterization}"
                            )
        
        # Compute adjustment factor
        if baseline_diffs:
            # Each baseline difference reduces effect
            adjustment = 1.0
            for var, (src, tgt) in baseline_diffs.items():
                adjustment *= self._baseline_adjustment_factor(src, tgt)
        else:
            adjustment = 1.0
        
        # Determine transfer type
        if contrast_preserved:
            transfer_type = "direct"
        elif baseline_diffs and not meaning_diffs:
            transfer_type = "baseline_adjusted"
        elif meaning_diffs:
            transfer_type = "uncertain"
        else:
            transfer_type = "analogous"
        
        return ContrastAssessment(
            source_contrast=source_contrast,
            target_contrast=target_contrast,
            contrast_preserved=contrast_preserved,
            contrast_similarity=contrast_similarity,
            baseline_differences=baseline_diffs,
            meaning_differences=meaning_diffs,
            transfer_type=transfer_type,
            adjustment_factor=adjustment,
            warnings=warnings
        )
    
    def _extract_source_contrast(
        self,
        theory_results: Dict[str, TheoryCounterfactual]
    ) -> Optional[ContrastClass]:
        """Extract contrast class from source beliefs."""
        
        for tcf in theory_results.values():
            for belief_id in tcf.supporting_beliefs:
                if belief_id in self.web.beliefs:
                    belief = self.web.beliefs[belief_id]
                    if belief.contrast_class:
                        return belief.contrast_class
        
        return None
    
    def _build_target_contrast(self, query: CounterfactualQuery) -> Optional[ContrastClass]:
        """Build contrast class for target context."""
        
        if query.contrast_class:
            return query.contrast_class
        
        # Build from query parameters
        if query.target_population and query.target_population in self.population_contexts:
            ctx = self.population_contexts[query.target_population]
            
            focal = ConditionSpec(
                variable=list(query.intervention.keys())[0],
                value=list(query.intervention.values())[0],
                description="Intervention"
            )
            
            contrasts = [ConditionSpec(
                variable=list(query.intervention.keys())[0],
                value=0,  # Default contrast is no intervention
                description="No intervention"
            )]
            
            return ContrastClass(
                contrast_id=f"target_{query.query_id}",
                focal=focal,
                contrasts=contrasts,
                contrast_type=query.contrast_type,
                population_context=ctx
            )
        
        return None
    
    def _contrasts_equivalent(
        self,
        c1: Optional[ContrastClass],
        c2: Optional[ContrastClass]
    ) -> bool:
        """Check if two contrast classes are equivalent."""
        if c1 is None or c2 is None:
            return False
        
        # Same variables
        if c1.focal.variable != c2.focal.variable:
            return False
        
        # Same population context (approximately)
        if c1.population_context and c2.population_context:
            if c1.population_context.population_id != c2.population_context.population_id:
                return False
        
        return True
    
    def _compute_contrast_similarity(
        self,
        c1: Optional[ContrastClass],
        c2: Optional[ContrastClass]
    ) -> float:
        """Compute similarity between contrast classes."""
        
        if c1 is None or c2 is None:
            return 0.5  # Unknown
        
        similarity = 1.0
        
        # Check variable match
        if c1.focal.variable != c2.focal.variable:
            similarity *= 0.5
        
        # Check population context
        if c1.population_context and c2.population_context:
            ctx1, ctx2 = c1.population_context, c2.population_context
            
            # Region similarity
            if ctx1.region != ctx2.region:
                similarity *= 0.8
            
            # Baseline similarity
            common_vars = set(ctx1.baselines.keys()) & set(ctx2.baselines.keys())
            for var in common_vars:
                b1, b2 = ctx1.baselines[var], ctx2.baselines[var]
                distance = b1.distance_from(b2)
                similarity *= (1 - 0.5 * distance)
        
        return max(0.1, similarity)
    
    def _baseline_adjustment_factor(self, source_char: str, target_char: str) -> float:
        """Compute adjustment factor for baseline difference."""
        
        levels = ["very_low", "low", "moderate", "high", "saturated"]
        
        try:
            src_idx = levels.index(source_char)
            tgt_idx = levels.index(target_char)
        except ValueError:
            return 1.0
        
        diff = tgt_idx - src_idx
        
        if diff == 0:
            return 1.0
        elif diff > 0:  # Target has higher baseline (ceiling effect)
            return 0.75 ** diff
        else:  # Target has lower baseline (may have larger effect)
            return 1.10 ** abs(diff)
    
    def _adjust_ci(
        self,
        ci: Tuple[float, float],
        scope: ScopeAssessment,
        contrast: ContrastAssessment
    ) -> Tuple[float, float]:
        """Adjust confidence interval for scope and contrast uncertainty."""
        
        # Widen CI for extrapolation
        width = ci[1] - ci[0]
        center = (ci[0] + ci[1]) / 2
        
        # Scope penalty widens CI
        width *= (1 + scope.suggested_penalty)
        
        # Contrast difference widens CI
        width *= (1 + (1 - contrast.contrast_similarity) * 0.5)
        
        return (center - width / 2, center + width / 2)
    
    # =========================================================================
    # EPISTEMIC COUNTERFACTUALS
    # =========================================================================
    
    def epistemic_counterfactual(
        self,
        hypothetical_evidence: Dict[str, Dict[str, Any]]
    ) -> EpistemicCounterfactualResult:
        """
        Compute: "What would we believe if this evidence emerged?"
        
        This is about the web itself, not about the world.
        """
        
        # Save original state
        original_coherence = self.web.coherence_score()
        original_credences = {
            bid: b.credence.value for bid, b in self.web.beliefs.items()
        }
        original_statuses = {
            bid: b.status for bid, b in self.web.beliefs.items()
        }
        
        # Create modified web
        modified_web = copy.deepcopy(self.web)
        
        # Apply hypothetical evidence
        for belief_id, evidence_spec in hypothetical_evidence.items():
            self._apply_hypothetical(modified_web, belief_id, evidence_spec)
        
        # Propagate via equilibrium
        modified_web.seek_equilibrium(max_iterations=10)
        
        # Compute changes
        belief_changes = []
        for bid in original_credences:
            if bid not in modified_web.beliefs:
                continue
            
            old_cred = original_credences[bid]
            new_cred = modified_web.beliefs[bid].credence.value
            old_status = original_statuses[bid]
            new_status = modified_web.beliefs[bid].status
            
            delta = new_cred - old_cred
            
            if abs(delta) > 0.01 or old_status != new_status:
                belief_changes.append(BeliefChange(
                    belief_id=bid,
                    old_credence=old_cred,
                    new_credence=new_cred,
                    credence_delta=delta,
                    old_status=old_status,
                    new_status=new_status,
                    status_changed=(old_status != new_status)
                ))
        
        belief_changes.sort(key=lambda bc: abs(bc.credence_delta), reverse=True)
        
        major_shifts = [bc for bc in belief_changes if abs(bc.credence_delta) > 0.1]
        status_flips = [bc for bc in belief_changes if bc.status_changed]
        
        # Compute theory impacts
        theory_impacts = {}
        for theory_id in self.web.theory_ids:
            old_prob = self.web.marginal_theory_probability(theory_id)
            new_prob = modified_web.marginal_theory_probability(theory_id)
            
            if new_prob > old_prob + 0.05:
                direction = "strengthened"
            elif new_prob < old_prob - 0.05:
                direction = "weakened"
            else:
                direction = "unchanged"
            
            theory_impacts[theory_id] = TheoryImpact(
                theory_id=theory_id,
                old_probability=old_prob,
                new_probability=new_prob,
                direction=direction
            )
        
        return EpistemicCounterfactualResult(
            hypothetical_evidence=hypothetical_evidence,
            original_coherence=original_coherence,
            hypothetical_coherence=modified_web.coherence_score(),
            belief_changes=belief_changes,
            major_shifts=major_shifts,
            status_flips=status_flips,
            theory_impacts=theory_impacts
        )
    
    def _apply_hypothetical(
        self,
        web: 'WebOfBelief',
        belief_id: str,
        evidence_spec: Dict[str, Any]
    ):
        """Apply hypothetical evidence to web."""
        
        if 'new_belief' in evidence_spec:
            # Create new belief
            new_belief = Belief(
                belief_id=belief_id,
                content=evidence_spec['new_belief'],
                level=EpistemicLevel.EMPIRICAL,
                status=BeliefStatus.TENTATIVE,
                credence=Credence(
                    value=evidence_spec.get('credence', 0.7),
                    uncertainty=evidence_spec.get('uncertainty', 0.2)
                )
            )
            web.add_belief(new_belief)
        
        elif belief_id in web.beliefs:
            # Update existing
            belief = web.beliefs[belief_id]
            if 'credence' in evidence_spec:
                belief.credence = Credence(
                    value=evidence_spec['credence'],
                    uncertainty=evidence_spec.get('uncertainty', belief.credence.uncertainty)
                )
        
        # Add constraints
        for supported in evidence_spec.get('supports', []):
            if supported in web.beliefs:
                web.add_constraint(Constraint(
                    constraint_id=f"hyp:{belief_id}:{supported}",
                    source_id=belief_id,
                    target_id=supported,
                    constraint_type=ConstraintType.SUPPORTS,
                    strength=0.6
                ))
        
        for contradicted in evidence_spec.get('contradicts', []):
            if contradicted in web.beliefs:
                web.add_constraint(Constraint(
                    constraint_id=f"hyp:{belief_id}:{contradicted}",
                    source_id=belief_id,
                    target_id=contradicted,
                    constraint_type=ConstraintType.CONTRADICTS,
                    strength=0.6
                ))
    
    # =========================================================================
    # GENERALIZATION
    # =========================================================================
    
    def assess_generalization(
        self,
        belief_id: str,
        target_population: str,
        target_individual: Optional[IndividualDifferenceProfile] = None
    ) -> GeneralizationAssessment:
        """
        Assess whether a belief generalizes to a target context.
        
        Core van Fraassen question: Is the contrast class preserved?
        """
        
        if belief_id not in self.web.beliefs:
            raise ValueError(f"Belief not found: {belief_id}")
        
        belief = self.web.beliefs[belief_id]
        
        # Get source context
        source_contrast = belief.contrast_class
        source_context = source_contrast.population_context if source_contrast else None
        
        if source_context is None:
            # Infer from belief metadata or use default
            source_context = PopulationContext(
                population_id="unknown_source",
                baselines={}
            )
        
        # Get target context
        if target_population in self.population_contexts:
            target_context = self.population_contexts[target_population]
        else:
            target_context = PopulationContext(
                population_id=target_population,
                baselines={}
            )
        
        # Build target contrast
        if source_contrast:
            target_contrast = ContrastClass(
                contrast_id=f"target_{belief_id}",
                focal=source_contrast.focal,
                contrasts=source_contrast.contrasts,
                contrast_type=source_contrast.contrast_type,
                population_context=target_context
            )
        else:
            target_contrast = None
        
        # Determine generalization type
        warnings = []
        recommendations = []
        
        # Compare baselines
        baseline_adjustment = 1.0
        if source_context.baselines and target_context.baselines:
            for var in source_context.baselines:
                if var in target_context.baselines:
                    src_base = source_context.baselines[var]
                    tgt_base = target_context.baselines[var]
                    
                    if src_base.characterization != tgt_base.characterization:
                        adj = self._baseline_adjustment_factor(
                            src_base.characterization,
                            tgt_base.characterization
                        )
                        baseline_adjustment *= adj
                        
                        warnings.append(
                            f"Baseline for '{var}' differs: "
                            f"{src_base.characterization} → {tgt_base.characterization}"
                        )
        
        # Individual modifiers
        individual_modifier = 1.0
        if target_individual:
            # Apply individual difference adjustments
            # ... implementation depends on available factors
            pass
        
        # Combined adjustment
        adjustment = baseline_adjustment * individual_modifier
        
        # Determine type
        if adjustment > 0.9:
            gen_type = "direct_transfer"
        elif adjustment > 0.6:
            gen_type = "baseline_adjusted"
        elif adjustment > 0.3:
            gen_type = "uncertain_transfer"
        else:
            gen_type = "questionable_transfer"
            warnings.append("Generalization is highly uncertain due to large context differences")
        
        # Compute estimates
        original = belief.credence.value
        generalized = original * adjustment
        uncertainty = belief.credence.uncertainty * (1 + (1 - adjustment) * 0.5)
        
        if gen_type == "questionable_transfer":
            recommendations.append("Consider conducting local replication study")
        
        return GeneralizationAssessment(
            belief_id=belief_id,
            source_context=source_context,
            target_context=target_context,
            target_individual=target_individual,
            source_contrast=source_contrast,
            target_contrast=target_contrast,
            generalization_type=gen_type,
            adjustment_factor=adjustment,
            original_estimate=original,
            generalized_estimate=generalized,
            generalization_uncertainty=uncertainty,
            warnings=warnings,
            recommendations=recommendations
        )
    
    # =========================================================================
    # POPULATION CONTEXT MANAGEMENT
    # =========================================================================
    
    def register_population_context(self, context: PopulationContext):
        """Register a population context for generalization."""
        self.population_contexts[context.population_id] = context
    
    def register_individual_factor(self, factor: IndividualDifferenceFactor):
        """Register an individual difference factor."""
        self.individual_factors[factor.factor_id] = factor


# =============================================================================
# PART 11: MINIMAL CONSTRAINT AND WEB STRUCTURES (for completeness)
# =============================================================================

@dataclass
class Constraint:
    """Constraint between beliefs."""
    constraint_id: str
    source_id: str
    target_id: str
    constraint_type: ConstraintType
    strength: float = 0.5
    bidirectional: bool = True


class WebOfBelief:
    """
    Minimal web of belief implementation for this module.
    
    Full implementation in web_of_belief.py
    """
    
    def __init__(self, domain: str = "default"):
        self.domain = domain
        self.beliefs: Dict[str, Belief] = {}
        self.constraints: Dict[str, Constraint] = {}
        self.theory_ids: Set[str] = set()
        self._coherence: float = 0.5
    
    def add_belief(self, belief: Belief):
        self.beliefs[belief.belief_id] = belief
        for tid in belief.theory_ids:
            self.theory_ids.add(tid)
    
    def add_constraint(self, constraint: Constraint):
        self.constraints[constraint.constraint_id] = constraint
    
    def coherence_score(self) -> float:
        return self._coherence
    
    def marginal_theory_probability(self, theory_id: str) -> float:
        # Simplified: average credence of theory's beliefs
        theory_beliefs = [
            b for b in self.beliefs.values()
            if theory_id in b.theory_ids
        ]
        if not theory_beliefs:
            return 0.5
        return sum(b.credence.value for b in theory_beliefs) / len(theory_beliefs)
    
    def seek_equilibrium(self, max_iterations: int = 10):
        """Simplified equilibrium seeking."""
        for _ in range(max_iterations):
            # Propagate through constraints
            for constraint in self.constraints.values():
                if constraint.source_id not in self.beliefs:
                    continue
                if constraint.target_id not in self.beliefs:
                    continue
                
                source = self.beliefs[constraint.source_id]
                target = self.beliefs[constraint.target_id]
                
                if constraint.constraint_type == ConstraintType.SUPPORTS:
                    # Pull toward agreement
                    delta = (source.credence.value - target.credence.value) * 0.1 * constraint.strength
                    target.credence = Credence(
                        value=target.credence.value + delta,
                        uncertainty=target.credence.uncertainty
                    )
                
                elif constraint.constraint_type == ConstraintType.CONTRADICTS:
                    # Push apart
                    if source.credence.value > 0.5 and target.credence.value > 0.5:
                        # Both high - lower the less entrenched one
                        if source.entrenchment < target.entrenchment:
                            source.credence = Credence(
                                value=source.credence.value * 0.95,
                                uncertainty=source.credence.uncertainty
                            )
                        else:
                            target.credence = Credence(
                                value=target.credence.value * 0.95,
                                uncertainty=target.credence.uncertainty
                            )
        
        # Update coherence estimate
        self._update_coherence()
    
    def _update_coherence(self):
        if not self.constraints:
            self._coherence = 0.5
            return
        
        total = 0.0
        count = 0
        
        for c in self.constraints.values():
            if c.source_id not in self.beliefs or c.target_id not in self.beliefs:
                continue
            
            s_cred = self.beliefs[c.source_id].credence.value
            t_cred = self.beliefs[c.target_id].credence.value
            
            if c.constraint_type == ConstraintType.SUPPORTS:
                # Coherent if similar
                total += 1 - abs(s_cred - t_cred)
            elif c.constraint_type == ConstraintType.CONTRADICTS:
                # Coherent if different
                total += abs(s_cred - t_cred)
            else:
                total += 0.5
            
            count += 1
        
        self._coherence = total / count if count > 0 else 0.5


# =============================================================================
# PART 12: EXAMPLE USAGE AND DEMO
# =============================================================================

def create_demo_system() -> EpistemicCausalBridge:
    """Create a demo system with example data."""
    
    # Create web
    web = WebOfBelief(domain="neuroarchitecture")
    
    # Add theoretical beliefs
    art_core = Belief(
        belief_id="ART_core",
        content="Natural environments restore directed attention",
        level=EpistemicLevel.THEORETICAL,
        status=BeliefStatus.ESTABLISHED,
        credence=Credence(0.72, 0.2),
        entrenchment=0.8,
        theory_ids={"ART": 1.0},
        tags=["outcome:attention", "exposure:nature"]
    )
    web.add_belief(art_core)
    
    srt_core = Belief(
        belief_id="SRT_core",
        content="Natural environments reduce physiological stress",
        level=EpistemicLevel.THEORETICAL,
        status=BeliefStatus.ESTABLISHED,
        credence=Credence(0.75, 0.18),
        entrenchment=0.75,
        theory_ids={"SRT": 1.0},
        tags=["outcome:stress", "exposure:nature"]
    )
    web.add_belief(srt_core)
    
    # Add empirical beliefs with contrast class
    sunlight_mood = Belief(
        belief_id="sunlight_mood",
        content="Bright light exposure improves mood",
        level=EpistemicLevel.EMPIRICAL,
        status=BeliefStatus.ESTABLISHED,
        credence=Credence(0.68, 0.22),
        entrenchment=0.55,
        theory_ids={"SRT": 0.7},
        tags=["outcome:mood", "exposure:light"],
        contrast_class=ContrastClass(
            contrast_id="cc_sunlight",
            focal=ConditionSpec("light", "bright", "Bright light exposure"),
            contrasts=[ConditionSpec("light", "dim", "Dim indoor light")],
            contrast_type=ContrastType.NULL,
            population_context=PopulationContext(
                population_id="Nordic_winter_SAD",
                region="Scandinavia",
                baselines={
                    "light_exposure": BaselineSpec(
                        variable="daily_lux_hours",
                        typical_value=500,
                        variance=200,
                        characterization="very_low"
                    )
                }
            )
        )
    )
    web.add_belief(sunlight_mood)
    
    # Add constraints
    web.add_constraint(Constraint(
        constraint_id="c1",
        source_id="sunlight_mood",
        target_id="SRT_core",
        constraint_type=ConstraintType.INSTANTIATES,
        strength=0.6
    ))
    
    # Create bridge
    bridge = EpistemicCausalBridge(web)
    
    # Register population contexts
    bridge.register_population_context(PopulationContext(
        population_id="Nordic_winter",
        region="Scandinavia",
        baselines={
            "light_exposure": BaselineSpec(
                variable="daily_lux_hours",
                typical_value=500,
                variance=200,
                characterization="very_low"
            ),
            "nature_exposure": BaselineSpec(
                variable="daily_nature_minutes",
                typical_value=30,
                variance=20,
                characterization="low"
            )
        },
        cultural_meanings={
            "nature": CulturalMeaning(
                culture="Nordic",
                meaning="friluftsliv",
                associations=["identity", "routine", "allemansrätten"],
                valence="positive_normal",
                behavioral_implications="integrated_daily"
            )
        }
    ))
    
    bridge.register_population_context(PopulationContext(
        population_id="Miami_outdoor",
        region="Florida",
        baselines={
            "light_exposure": BaselineSpec(
                variable="daily_lux_hours",
                typical_value=5000,
                variance=1000,
                characterization="high"
            ),
            "nature_exposure": BaselineSpec(
                variable="daily_nature_minutes",
                typical_value=60,
                variance=40,
                characterization="moderate"
            )
        },
        cultural_meanings={
            "sunlight": CulturalMeaning(
                culture="Floridian",
                meaning="ambient_abundant",
                associations=["beach", "outdoor_lifestyle"],
                valence="positive_normal",
                behavioral_implications="not_scarce"
            )
        }
    ))
    
    return bridge


if __name__ == "__main__":
    # Demo
    print("=" * 60)
    print("EPISTEMIC-CAUSAL INTEGRATION DEMO")
    print("=" * 60)
    
    bridge = create_demo_system()
    bridge.build_causal_models(credence_threshold=0.4)
    
    print("\n1. COUNTERFACTUAL QUERY")
    print("-" * 40)
    
    result = bridge.counterfactual(
        intervention={"light": 10000},
        outcome="mood",
        target_population="Nordic_winter"
    )
    print(result.summary())
    
    print("\n2. GENERALIZATION ASSESSMENT")
    print("-" * 40)
    
    gen_result = bridge.assess_generalization(
        belief_id="sunlight_mood",
        target_population="Miami_outdoor"
    )
    print(gen_result.summary())
    
    print("\n3. EPISTEMIC COUNTERFACTUAL")
    print("-" * 40)
    
    ep_result = bridge.epistemic_counterfactual({
        "new_study": {
            "new_belief": "Light therapy ineffective for non-SAD populations",
            "credence": 0.65,
            "contradicts": ["sunlight_mood"]
        }
    })
    print(ep_result.summary())
