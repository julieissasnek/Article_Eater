"""
Article Eater - Quinean Web of Belief
=====================================

A coherentist epistemology for scientific knowledge synthesis.

This replaces the foundationalist theory → prediction → evidence model with
a Quinean web where:

1. No level has privileged epistemic status
2. Warrant flows in all directions (mutual constraint)
3. Coherence across the web is the criterion of acceptance
4. Even "observations" are uncertain and revisable
5. Findings can exist as "stubs" without theory attachment

The system seeks reflective equilibrium (Rawls): a state where our theoretical
commitments cohere with our empirical findings, with adjustment possible at
any level to achieve better overall coherence.

Key Differences from Standard Approaches:

FOUNDATIONALISM              COHERENTISM (this module)
--------------               -------------------------
Observations are bedrock     Observations are uncertain
Theory derives from data     Mutual constraint
Evidence confirms/refutes    Evidence shifts coherence
Theories are independent     Joint distribution over theory-worlds
Findings must attach to      Findings can be "stubs" awaiting
  predictions                  theoretical integration

Philosophical Foundations:
- Quine, W.V.O. (1951). Two Dogmas of Empiricism. Philosophical Review.
  [Citations: 15,000+]
- Rawls, J. (1971). A Theory of Justice. Harvard University Press.
  [Citations: 80,000+] — esp. "reflective equilibrium" in moral epistemology
- BonJour, L. (1985). The Structure of Empirical Knowledge. Harvard.
  [Citations: 2,000+]
- Thagard, P. (1989). Explanatory coherence. Behavioral and Brain Sciences.
  [Citations: 1,500+]
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple, Set
from datetime import datetime, timezone
import logging
import os

from src.services.web_of_belief_modules import (
    AnalysisContracts as _AnalysisContracts,
    CredenceAdjustment as _CredenceAdjustment,
    DEFAULT_LEVEL_WEIGHTS as _DEFAULT_ENTRENCHMENT_LEVEL_WEIGHTS,
    BeliefValueRecord as _BeliefValueRecord,
    CentralityInput as _CentralityInput,
    CoherenceResult as _CoherenceResult,
    ExperimentBeliefInput as _ExperimentBeliefInput,
    EntrenchmentInput as _EntrenchmentInput,
    build_evidence_input as _build_evidence_input,
    choose_adjustment_target as _choose_adjustment_target,
    compute_credence_adjustment as _compute_credence_adjustment,
    EpistemicValueInput as _EpistemicValueInput,
    compute_centrality as _compute_centrality,
    compute_entrenchment_components as _compute_entrenchment_components_contract,
    compute_epistemic_value as _compute_epistemic_value,
    compute_independence_score as _compute_independence_score,
    compute_severity_score as _compute_severity_score,
    estimate_resolution as _estimate_resolution_contract,
    empty_entrenchment_components as _empty_entrenchment_components,
    identify_scope_differences as _identify_scope_differences_contract,
    infer_experiment_type as _infer_experiment_type_contract,
    infer_test_focus_and_hypothesis as _infer_test_focus_and_hypothesis,
    init_updates_payload as _init_evidence_updates_payload,
    make_belief_update_record as _make_belief_update_record,
    make_temporal_update_record as _make_temporal_update_record,
    make_theory_world_update_records as _make_theory_world_update_records,
    ensure_theory_relevance as _ensure_theory_relevance,
    MutationContracts as _MutationContracts,
    suggest_contested_scope as _suggest_contested_scope_contract,
    suggest_scope as _suggest_scope_contract,
    sort_value_records as _sort_value_records,
    WebAnalysisOperations as _WebAnalysisOperations,
    WebMutationOperations as _WebMutationOperations,
    WebOfBeliefEngines as _WebOfBeliefEngines,
    WebOfBeliefState as _WebOfBeliefState,
)
from src.services.web_of_belief_components import (
    BeliefKind,
    BeliefStatus,
    CausalDirection,
    CredenceHistoryEntry,
    EnablingConditions,
    EpistemicLevel,
    EpistemicNodeSubtype,
    EvidenceQuality,
    InferenceType,
    NodeDomain,
    PathwayType,
    PESubtype,
    ReplicationStatus,
    ScopeConditions,
    SourceDepth,
    StudyDesign,
    STUDY_DESIGN_SEVERITY_WEIGHT,
    Constraint,
    TheoryWorld,
    UncertainQuantity,
)

logger = logging.getLogger(__name__)

# =============================================================================
# OPTIONAL: EPISTEMIC-CAUSAL BRIDGE (Sprint 1.5)
# =============================================================================
# The bridge integrates the Quinean epistemic layer with Pearlian causal inference.
# Import is optional to avoid circular dependencies and allow standalone use.

try:
    from src.services import epistemic_causal_bridge as ecb
    BRIDGE_AVAILABLE = True
except ImportError:
    ecb = None
    BRIDGE_AVAILABLE = False


# =============================================================================
# OPTIONAL: SOCIAL EPISTEMOLOGY (Sprint 2.5)
# =============================================================================
# Social epistemology constructs for community-relative credence and provenance.
# Import is optional to avoid circular dependencies.

try:
    from src.services import social_epistemology as se
    SOCIAL_EPISTEMOLOGY_AVAILABLE = True
except ImportError:
    se = None
    SOCIAL_EPISTEMOLOGY_AVAILABLE = False


# Types extracted to `src/services/web_of_belief_components` (ARCH-5d).


# =============================================================================
# UNCERTAIN BELIEF
# =============================================================================

@dataclass
class Credence:
    """
    Credence (degree of belief) with meta-uncertainty.
    
    Following the Quinean picture, we have uncertainty about our uncertainty.
    A belief might have credence 0.7, but we might also be uncertain about
    whether 0.7 is the right credence.
    """
    value: float  # 0 to 1
    uncertainty: float  # Meta-uncertainty about the credence itself
    
    # Evidence base
    n_supporting: int = 0
    n_contradicting: int = 0
    n_observations: int = 0
    
    def __post_init__(self):
        value = 0.5 if self.value is None else float(self.value)
        uncertainty = 0.5 if self.uncertainty is None else float(self.uncertainty)
        self.value = max(0.01, min(0.99, value))
        self.uncertainty = max(0.0, min(1.0, uncertainty))
    
    def confidence_interval(self, level: float = 0.95) -> Tuple[float, float]:
        """Credible interval for the credence itself."""
        # Use beta distribution intuition
        half_width = self.uncertainty * (1.96 if level == 0.95 else 2.576)
        return (
            max(0, self.value - half_width),
            min(1, self.value + half_width)
        )
    
    def is_well_established(self) -> bool:
        """Whether we have good evidence for this credence.

        Panel Review 2026-02-12 (Kahneman): Raised uncertainty threshold from 0.2
        to 0.35 to match the new uncertainty floor and prevent false confidence.
        """
        return self.n_observations >= 3 and self.uncertainty < 0.35
    
    def update(
        self,
        evidence_supports: Optional[bool],
        evidence_strength: float = 0.5,
        evidence_quality: float = 0.5
    ) -> 'Credence':
        """Bayesian update with new evidence."""
        # Update counts
        new_supporting = self.n_supporting + (1 if evidence_supports is True else 0)
        new_contradicting = self.n_contradicting + (1 if evidence_supports is False else 0)
        new_observations = self.n_observations + 1
        
        # Likelihood ratio
        weight = evidence_strength * evidence_quality
        if evidence_supports is True:
            lr = (0.6 + 0.4 * weight) / (0.4 - 0.2 * weight)
        elif evidence_supports is False:
            lr = (0.4 - 0.2 * weight) / (0.6 + 0.4 * weight)
        else:  # Null
            lr = 0.95  # Slight evidence against
        
        # Update credence
        prior_odds = self.value / (1 - self.value + 1e-10)
        posterior_odds = prior_odds * lr
        new_value = posterior_odds / (1 + posterior_odds)
        
        # Uncertainty decreases with evidence (but never to overconfident levels)
        # Panel Review 2026-02-12 (Kahneman): Raised floor from 0.05 to 0.25
        # to prevent overconfidence. Real uncertainty is MUCH larger than typical
        # point estimates suggest.
        new_uncertainty = self.uncertainty * (0.95 ** (weight * 0.5))
        new_uncertainty = max(0.25, new_uncertainty)  # Floor - prevent overconfidence
        
        return Credence(
            value=new_value,
            uncertainty=new_uncertainty,
            n_supporting=new_supporting,
            n_contradicting=new_contradicting,
            n_observations=new_observations
        )
    
    def to_dict(self) -> Dict[str, Any]:
        ci = self.confidence_interval()
        return {
            'credence': self.value,
            'uncertainty': self.uncertainty,
            'ci_95': [ci[0], ci[1]],
            'n_supporting': self.n_supporting,
            'n_contradicting': self.n_contradicting,
            'n_observations': self.n_observations
        }


# =============================================================================
# BELIEFS (Nodes in the Web)
# =============================================================================

@dataclass
class Belief:
    """
    A single belief in the web.

    Beliefs can exist at any epistemic level and may or may not be
    connected to other beliefs. A "stub" is a belief that exists but
    is not yet integrated into the theoretical structure.

    Sprint 6 additions:
    - scope: Conditions under which belief applies (per Cartwright)
    - environment_id: Canonical ID of environment feature (per Bates)
    - outcome_id: Canonical ID of outcome/DV (per Bates)

    Sprint 8 additions:
    - evidence_cluster_id: Groups beliefs from same study (prevents double-counting)
    """
    belief_id: str
    content: str  # What is believed

    # Position in the web
    level: EpistemicLevel
    status: BeliefStatus = BeliefStatus.STUB

    # Epistemic standing
    # Panel Review 2026-02-12 (Kahneman): Default uncertainty raised from 0.4 to 0.5
    # to reflect epistemic humility. Initial beliefs should have wide intervals.
    credence: Credence = field(default_factory=lambda: Credence(0.5, 0.5))

    # V23.0.0 BREAKING CHANGE: Entrenchment is now EMERGENT, not stored.
    # Per panel consultation (2026-02-08): Settable entrenchment violates
    # Quinean coherentism by creating hidden foundationalism.
    #
    # Entrenchment is now computed by WebOfBelief.get_entrenchment(belief_id)
    # using the Thagard formula: 40% connectivity + 30% level + 30% coherence_contrib
    #
    # This field is kept ONLY for backward compatibility with serialization.
    # It is NOT used in computation - use web.get_entrenchment(belief_id) instead.
    _legacy_entrenchment: float = 0.5  # For deserialization only, ignored in new code

    # For empirical/observational beliefs: source information
    paper_ids: List[str] = field(default_factory=list)

    # For theoretical beliefs: what theory (if any) does this belong to?
    theory_id: Optional[str] = None

    # Temporal parameters (uncertain) - only for causal beliefs
    temporal_params: Optional[Dict[str, 'UncertainQuantity']] = None

    # Metadata
    domain: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    tags: List[str] = field(default_factory=list)

    # Sprint 6: Scope conditions (Expert Panel: Cartwright)
    scope: Optional[ScopeConditions] = None
    scope_population: Optional[str] = None
    scope_context: Optional[str] = None
    scope_temporal: Optional[str] = None

    # Sprint 7: Canonical IDs for environment and outcome (Expert Panel: Bates)
    environment_id: Optional[str] = None  # e.g., "spatial.openness", "natural.vegetation"
    outcome_id: Optional[str] = None      # e.g., "psych.stress", "cog.attention"

    # Sprint 8: Evidence clustering (prevents double-counting multi-theory papers)
    evidence_cluster_id: Optional[str] = None  # e.g., "cluster:paper_123"

    # ARCH-3a: Source provenance for independence diagnostics.
    source_lab: Optional[str] = None
    source_institution: Optional[str] = None
    study_method: Optional[str] = None

    # ARCH-6a/6b: Evidence metrics and study design classification (Mayo).
    study_design: StudyDesign = StudyDesign.UNKNOWN
    evidence_quality: EvidenceQuality = EvidenceQuality.UNTESTED
    evidence_effect_size: Optional[float] = None
    evidence_p_value: Optional[float] = None
    evidence_sample_n: Optional[int] = None

    # Tier 1 additions (Expert Panel: Cartwright, Simon, Epistemologist)
    source_depth: SourceDepth = SourceDepth.FULL_TEXT  # How deeply was source analyzed?
    enabling_conditions: Optional[EnablingConditions] = None  # Activation requirements
    contested: bool = False  # True if credence oscillates (genuine disagreement)
    credence_history: List[CredenceHistoryEntry] = field(default_factory=list)

    # Sprint 1.6 additions (P-EC Panel: Synergies)
    inference_type: InferenceType = InferenceType.UNKNOWN  # How was this belief derived?
    belief_kind: BeliefKind = BeliefKind.EVIDENTIAL  # Functional role in the web

    # Sprint 2.5 additions (P-SE Panel: Social Epistemology)
    provenance: Optional[Any] = None  # BeliefProvenance, typed as Any to avoid circular import
    community_associations: Dict[str, float] = field(default_factory=dict)  # community_id → strength

    # =========================================================================
    # ARCH-4 V24.0.0: Formal Epistemic Calculus (composition fields)
    # =========================================================================
    # These fields enable gradual migration to the new data model:
    # - PropositionalContent (what is believed)
    # - EpistemicStatus (Spohn ranks + Pollock warrant)
    # - Provenance (Haack grounding + sources)
    #
    # Legacy fields (content, credence, etc.) are preserved for backward compat.
    # Use to_v2() and from_v2() for conversion.
    content_v2: Optional[Any] = None  # PropositionalContent
    status_v2: Optional[Any] = None   # EpistemicStatus
    provenance_v2: Optional[Any] = None  # Provenance (ARCH-4 version, not Sprint 2.5)

    # =========================================================================
    # EPISTEMIC TIER 2: Extended Fields (Sprints T2-1.8, T2-1.10, T2-4b)
    # =========================================================================

    # Task 1.8: Epistemic template fields (only for EPISTEMIC domain nodes)
    node_domain: Optional['NodeDomain'] = None               # Typed domain (replaces string 'domain')
    epistemic_subtype: Optional['EpistemicNodeSubtype'] = None  # E1-E4 template type
    derivation_path: Optional[List[str]] = None              # Tier 1 framework IDs this derives from
    core_claims: Optional[List[dict]] = None                 # [{text, citation, status}]
    bayesian_coherentist_mode: Optional[float] = None        # 0.0=Bayesian, 1.0=coherentist (E1 only)
    empirical_status: Optional[str] = None                   # well_established|supported|contested|speculative
    normative_weight: Optional[float] = None                 # 0.0=descriptive, 1.0=normative
    key_references: Optional[List[dict]] = None              # [{citation, year, google_scholar_count}]

    # Task 1.10: Argumentative fields (for all claim nodes)
    argument_for: Optional[str] = None            # Theoretical position this supports
    argument_against: Optional[str] = None        # Theoretical position this challenges
    adversarial_scrutiny_survived: Optional[bool] = None  # Tested by rival group?
    replication_type: Optional[str] = None        # original|direct_replication|conceptual_replication|meta_analysis
    pe_subtype: Optional['PESubtype'] = None      # If claim involves prediction error

    # Task 4b: Claim type bifurcation and ecological validity
    claim_type: Optional[str] = None              # ClaimType: evaluative_response | functional_effect
    effect_pathway: Optional['PathwayType'] = None  # How effect operates
    task_ecological_validity: Optional[float] = None  # [0, 1] composite validity score
    replication_status: Optional['ReplicationStatus'] = None  # Replication tracking

    def is_stub(self) -> bool:
        return self.status == BeliefStatus.STUB

    def is_anomalous(self) -> bool:
        return self.status == BeliefStatus.ANOMALOUS

    @property
    def entrenchment(self) -> float:
        """
        Backward-compatible property for entrenchment.

        V23.0.0: Entrenchment is now computed dynamically by WebOfBelief.get_entrenchment().
        This property returns _legacy_entrenchment for serialization compatibility.
        For accurate entrenchment, use web.get_entrenchment(belief_id) instead.
        """
        return self._legacy_entrenchment

    def record_credence_change(
        self,
        new_credence: float,
        triggered_by: Optional[str] = None,
        reason: str = ""
    ) -> None:
        """
        Record a credence change in history.

        Per expert panel (Simon): Track changes for stability detection.
        """
        # Calculate delta from last recorded value, not current credence
        if self.credence_history:
            old_credence = self.credence_history[-1].credence_value
        else:
            old_credence = self.credence.value
        delta = new_credence - old_credence

        entry = CredenceHistoryEntry(
            timestamp=datetime.now(timezone.utc),
            credence_value=new_credence,
            delta=delta,
            triggered_by=triggered_by,
            update_reason=reason
        )
        self.credence_history.append(entry)

        # Check for oscillation (crosses threshold > twice)
        self._check_oscillation()

    def _check_oscillation(self, threshold: float = 0.5, min_crossings: int = 3) -> None:
        """
        Detect if credence is oscillating across a threshold.

        Per expert panel (Epistemologist): Oscillation indicates genuine
        disagreement in the literature, not noise. Flag as contested.
        """
        if len(self.credence_history) < min_crossings + 1:
            return

        # Count threshold crossings in recent history
        recent = self.credence_history[-10:]  # Last 10 changes
        crossings = 0
        for i in range(1, len(recent)):
            prev = recent[i - 1].credence_value
            curr = recent[i].credence_value
            if (prev < threshold and curr >= threshold) or \
               (prev >= threshold and curr < threshold):
                crossings += 1

        if crossings >= min_crossings:
            self.contested = True

    def credence_stability(self, window: int = 5) -> float:
        """
        Calculate credence stability over recent history.

        Returns the maximum absolute delta in the last `window` updates.
        Lower values indicate more stability.

        Per expert panel (Simon): Use for stopping rules.
        """
        if len(self.credence_history) < window:
            return 1.0  # Not enough history, assume unstable

        recent = self.credence_history[-window:]
        max_delta = max(abs(entry.delta) for entry in recent)
        return max_delta

    def is_stable(self, threshold: float = 0.01, window: int = 5) -> bool:
        """
        Check if credence has stabilized.

        Per expert panel (Simon): Stable if max delta < threshold
        over the last `window` updates.
        """
        return self.credence_stability(window) < threshold

    def credence_range(self) -> Tuple[float, float]:
        """
        Return the range of credence values in history.

        Useful for contested beliefs where a point estimate is misleading.
        """
        if not self.credence_history:
            return (self.credence.value, self.credence.value)

        values = [entry.credence_value for entry in self.credence_history]
        return (min(values), max(values))

    # =========================================================================
    # SPRINT 1.6: INFERENCE AND VALUE METHODS
    # =========================================================================

    def infer_inference_type(self) -> InferenceType:
        """
        Infer the inference type based on belief characteristics.

        Sprint 1.6.1: Automatic classification heuristics.

        Rules:
        - EMPIRICAL/OBSERVATIONAL level → INDUCTIVE (data→generalization)
        - THEORETICAL level with high entrenchment → often ABDUCTIVE
        - INTERMEDIATE level with theory_id → DEDUCTIVE (theory→prediction)
        - Multiple source types → MIXED
        """
        if self.level in [EpistemicLevel.EMPIRICAL, EpistemicLevel.OBSERVATIONAL]:
            return InferenceType.INDUCTIVE
        elif self.level == EpistemicLevel.THEORETICAL:
            # Theoretical beliefs are often abductive (inference to best explanation)
            return InferenceType.ABDUCTIVE
        elif self.level == EpistemicLevel.INTERMEDIATE:
            if self.theory_id:
                # Derived from theory
                return InferenceType.DEDUCTIVE
            else:
                # Generalization without theory
                return InferenceType.INDUCTIVE
        return InferenceType.UNKNOWN

    def infer_belief_kind(self) -> BeliefKind:
        """
        Infer the belief kind based on characteristics.

        Sprint 1.6.2: Automatic classification heuristics.

        Rules:
        - Content mentions "mechanism", "causes", "pathway" → MECHANISTIC
        - Has paper_ids → EVIDENTIAL
        - THEORETICAL level → THEORETICAL
        - Content mentions "measure", "scale", "instrument" → METHODOLOGICAL
        """
        content_lower = self.content.lower()

        # Check for mechanism keywords
        mechanism_keywords = ['mechanism', 'causes', 'pathway', 'mediates', 'triggers']
        if any(kw in content_lower for kw in mechanism_keywords):
            return BeliefKind.MECHANISTIC

        # Check for methodological keywords
        method_keywords = ['measure', 'scale', 'instrument', 'operationalize', 'assess']
        if any(kw in content_lower for kw in method_keywords):
            return BeliefKind.METHODOLOGICAL

        # Level-based inference
        if self.level == EpistemicLevel.THEORETICAL:
            return BeliefKind.THEORETICAL
        elif self.level in [EpistemicLevel.EMPIRICAL, EpistemicLevel.OBSERVATIONAL]:
            return BeliefKind.EVIDENTIAL
        elif self.level == EpistemicLevel.INTERMEDIATE:
            # Could be mechanistic or bridge
            if 'bridge' in content_lower or 'transfer' in content_lower:
                return BeliefKind.BRIDGE
            return BeliefKind.MECHANISTIC

        return BeliefKind.EVIDENTIAL

    def auto_classify(self) -> None:
        """
        Automatically classify inference_type and belief_kind if unknown.

        Sprint 1.6: Call this after creating a belief to auto-populate
        classification fields.
        """
        if self.inference_type == InferenceType.UNKNOWN:
            self.inference_type = self.infer_inference_type()
        if self.belief_kind == BeliefKind.EVIDENTIAL:  # Default, might need updating
            inferred = self.infer_belief_kind()
            if inferred != BeliefKind.EVIDENTIAL or self.level != EpistemicLevel.EMPIRICAL:
                self.belief_kind = inferred

    def compute_severity(self, alpha: float = 0.05) -> float:
        """ARCH-6b: Approximate severe-testing score for this belief's evidence."""
        base = _compute_severity_score(
            credence=self.credence.value,
            uncertainty=self.credence.uncertainty,
            sample_n=self.evidence_sample_n,
            effect_size=self.evidence_effect_size,
            p_value=self.evidence_p_value,
            alpha=alpha,
        )
        # ARCH-6a: Study design modulates severity — an RCT finding
        # is more severely tested than an observational one, all else equal.
        design_weight = STUDY_DESIGN_SEVERITY_WEIGHT.get(
            self.study_design.value if isinstance(self.study_design, StudyDesign) else str(self.study_design),
            0.30,
        )
        return max(0.0, min(1.0, 0.6 * base + 0.4 * design_weight))

    def classify_evidence_quality(self) -> 'EvidenceQuality':
        """ARCH-6d: Auto-classify evidence quality based on severity and study design.

        Distinguishes 'consistent with' from 'severely tested by'.
        """
        severity = self.compute_severity()
        design = self.study_design

        if design in (StudyDesign.RCT, StudyDesign.META_ANALYSIS) and severity >= 0.50:
            return EvidenceQuality.SEVERELY_TESTED
        elif design in (StudyDesign.QUASI_EXPERIMENTAL,) and severity >= 0.45:
            return EvidenceQuality.MODERATELY_TESTED
        elif severity >= 0.40 and design not in (StudyDesign.THEORETICAL, StudyDesign.UNKNOWN):
            return EvidenceQuality.MODERATELY_TESTED
        elif self.evidence_effect_size is not None or self.evidence_p_value is not None:
            return EvidenceQuality.CONSISTENT_ONLY
        else:
            return EvidenceQuality.UNTESTED

    def severity_gate_check(self) -> Optional[str]:
        """ARCH-6c: Check if credence violates the severity gate.

        Returns None if OK, or a warning string if the belief has high
        credence (> 0.70) without adequate severe testing.
        """
        if self.credence.value <= 0.70:
            return None  # Gate only applies to high-credence beliefs
        quality = self.classify_evidence_quality()
        if quality in (EvidenceQuality.SEVERELY_TESTED, EvidenceQuality.MODERATELY_TESTED):
            return None  # Adequately tested
        severity = self.compute_severity()
        return (
            f"SEVERITY_GATE: Belief '{self.belief_id}' has credence "
            f"{self.credence.value:.2f} but evidence_quality={quality.value} "
            f"(severity={severity:.2f}, study_design={self.study_design.value}). "
            f"High credence requires at least MODERATELY_TESTED evidence."
        )

    # =========================================================================
    # SPRINT 2.5: SOCIAL EPISTEMOLOGY METHODS
    # =========================================================================

    def get_community_credence(self, community_id: str) -> Optional[float]:
        """
        Get credence from a specific community's perspective.

        Sprint 2.5: Community-relative credence per panel synthesis for SE-2.

        Args:
            community_id: The community to get credence for

        Returns:
            Credence value (0-1) or None if not available
        """
        if self.provenance and hasattr(self.provenance, 'get_community_credence'):
            return self.provenance.get_community_credence(community_id)
        return None

    def is_community_contested(self) -> bool:
        """
        Check if belief is contested across communities.

        Sprint 2.5: A belief is contested if communities have significantly
        different credences (spread > 0.2 per panel synthesis for SE-2).

        Returns:
            True if contested, False otherwise
        """
        if self.provenance and hasattr(self.provenance, 'is_contested'):
            return self.provenance.is_contested()
        return False

    def set_provenance(self, provenance: Any) -> None:
        """
        Set the provenance for this belief.

        Sprint 2.5: Provenance tracks who produced this belief and with what methods.

        Args:
            provenance: BeliefProvenance instance
        """
        self.provenance = provenance

    def add_community_association(self, community_id: str, strength: float) -> None:
        """
        Add or update a community association.

        Sprint 2.5: Track which communities this belief is associated with.

        Args:
            community_id: The community ID
            strength: Association strength (0-1)
        """
        self.community_associations[community_id] = max(0.0, min(1.0, strength))

    def to_dict(self, computed_entrenchment: Optional[float] = None) -> Dict[str, Any]:
        """
        Serialize belief to dictionary.

        Args:
            computed_entrenchment: Entrenchment value computed by WebOfBelief.
                                   If None, uses legacy value for backward compat.
        """
        # V23.0.0: Entrenchment is computed, not stored. Use provided value or legacy.
        entrenchment_value = computed_entrenchment if computed_entrenchment is not None else self._legacy_entrenchment
        result = {
            'belief_id': self.belief_id,
            'content': self.content,
            'level': self.level.value,
            'status': self.status.value,
            'credence': self.credence.to_dict(),
            'entrenchment': entrenchment_value,  # Computed value for serialization
            'theory_id': self.theory_id,
            'n_sources': len(self.paper_ids),
            'domain': self.domain,
            'paper_ids': self.paper_ids.copy(),
            'tags': self.tags.copy(),
            'environment_id': self.environment_id,
            'outcome_id': self.outcome_id,
            'evidence_cluster_id': self.evidence_cluster_id,
            'scope_population': self.scope_population,
            'scope_context': self.scope_context,
            'scope_temporal': self.scope_temporal,
            'source_lab': self.source_lab,
            'source_institution': self.source_institution,
            'study_method': self.study_method,
            'evidence_effect_size': self.evidence_effect_size,
            'evidence_p_value': self.evidence_p_value,
            'evidence_sample_n': self.evidence_sample_n,
            'severity': self.compute_severity(),
            'study_design': self.study_design.value if isinstance(self.study_design, StudyDesign) else str(self.study_design),
            'evidence_quality': self.classify_evidence_quality().value,
            'severity_gate_warning': self.severity_gate_check(),
            # Tier 1 additions
            'source_depth': self.source_depth.value,
            'contested': self.contested,
            # Sprint 1.6 additions
            'inference_type': self.inference_type.value,
            'belief_kind': self.belief_kind.value,
        }
        if self.scope:
            result['scope'] = self.scope.to_dict()
        if self.enabling_conditions:
            result['enabling_conditions'] = self.enabling_conditions.to_dict()
        if self.credence_history:
            result['credence_history'] = [h.to_dict() for h in self.credence_history]
        # Sprint 2.5 additions
        if self.provenance and hasattr(self.provenance, 'to_dict'):
            result['provenance'] = self.provenance.to_dict()
        if self.community_associations:
            result['community_associations'] = self.community_associations.copy()
        # ARCH-4 v2 composition fields
        if self.content_v2 and hasattr(self.content_v2, 'to_dict'):
            result['content_v2'] = self.content_v2.to_dict()
        if self.status_v2 and hasattr(self.status_v2, 'to_dict'):
            result['status_v2'] = self.status_v2.to_dict()
        if self.provenance_v2 and hasattr(self.provenance_v2, 'to_dict'):
            result['provenance_v2'] = self.provenance_v2.to_dict()
        return result

    # =========================================================================
    # ARCH-4 V24.0.0: V2 FORMAT CONVERSION METHODS
    # =========================================================================

    def to_v2(self) -> Dict[str, Any]:
        """
        Convert this belief to v2 format (PropositionalContent + EpistemicStatus + Provenance).

        Returns a dict with:
        - content: PropositionalContent as dict
        - status: EpistemicStatus as dict
        - provenance: Provenance (ARCH-4) as dict
        - id: belief_id (preserved)

        Note: Imports models dynamically to avoid circular imports.
        """
        # Dynamic import to avoid circular dependency
        from src.models.propositional_content import PropositionalContent, ContentType
        from src.models.epistemic_status import EpistemicStatus, RankPair, WarrantStatus
        from src.models.provenance import Provenance, Directness, JustificationStatus

        # Convert content
        content_type_map = {
            EpistemicLevel.THEORETICAL: ContentType.THEORETICAL,
            EpistemicLevel.INTERMEDIATE: ContentType.CAUSAL_CLAIM,
            EpistemicLevel.EMPIRICAL: ContentType.CORRELATIONAL_CLAIM,
            EpistemicLevel.OBSERVATIONAL: ContentType.OBSERVATIONAL,
        }
        content_v2 = PropositionalContent(
            proposition_id=self.belief_id,
            canonical_form=self.content,
            content_type=content_type_map.get(self.level, ContentType.CAUSAL_CLAIM),
            domain=self.domain or None
        )

        # Convert status (credence → ranks)
        ranks = RankPair.from_credence(self.credence.value, self.credence.uncertainty)
        warrant = WarrantStatus.WARRANTED if self.status != BeliefStatus.STUB else WarrantStatus.UNGROUNDED
        status_v2 = EpistemicStatus(
            ranks=ranks,
            warrant_status=warrant,
            prima_facie_warranted=(self.level == EpistemicLevel.OBSERVATIONAL)
        )

        # Convert provenance
        directness_map = {
            EpistemicLevel.OBSERVATIONAL: Directness.DIRECT,
            EpistemicLevel.EMPIRICAL: Directness.ONE_HOP,
            EpistemicLevel.INTERMEDIATE: Directness.MULTI_HOP,
            EpistemicLevel.THEORETICAL: Directness.THEORETICAL,
        }
        grounding_map = {
            EpistemicLevel.OBSERVATIONAL: 1.0,
            EpistemicLevel.EMPIRICAL: 0.7,
            EpistemicLevel.INTERMEDIATE: 0.4,
            EpistemicLevel.THEORETICAL: 0.2,
        }
        provenance_v2 = Provenance(
            grounding_score=grounding_map.get(self.level, 0.2),
            directness=directness_map.get(self.level, Directness.THEORETICAL),
            justification_status=JustificationStatus.WELL_JUSTIFIED
        )

        return {
            'id': self.belief_id,
            'content': content_v2.to_dict(),
            'status': status_v2.to_dict(),
            'provenance': provenance_v2.to_dict(),
            '_legacy': self.to_dict()  # Preserve for rollback
        }

    @classmethod
    def from_v2(cls, data: Dict[str, Any]) -> 'Belief':
        """
        Create Belief from v2 format data.

        Expects dict with content, status, provenance in v2 format.
        Falls back to _legacy field if present.
        """
        # If legacy data is present, use it for the core belief
        if '_legacy' in data:
            belief = cls.from_dict(data['_legacy'])
        else:
            # Create from v2 data
            from src.models.propositional_content import PropositionalContent
            from src.models.epistemic_status import EpistemicStatus
            from src.models.provenance import Provenance, Directness

            content = PropositionalContent.from_dict(data['content'])
            status = EpistemicStatus.from_dict(data['status'])
            prov = Provenance.from_dict(data['provenance'])

            # Map directness back to level
            directness_to_level = {
                Directness.DIRECT: EpistemicLevel.OBSERVATIONAL,
                Directness.ONE_HOP: EpistemicLevel.EMPIRICAL,
                Directness.MULTI_HOP: EpistemicLevel.INTERMEDIATE,
                Directness.THEORETICAL: EpistemicLevel.THEORETICAL,
            }

            # Convert ranks back to credence
            if status.ranks.neg_rank > status.ranks.rank:
                credence_value = 0.5 + (status.ranks.neg_rank - status.ranks.rank) / 10
            elif status.ranks.rank > status.ranks.neg_rank:
                credence_value = 0.5 - (status.ranks.rank - status.ranks.neg_rank) / 10
            else:
                credence_value = 0.5
            credence_value = max(0.05, min(0.95, credence_value))

            # Uncertainty from firmness
            firmness = status.ranks.firmness
            uncertainty = max(0.1, 1.0 - firmness / 5)

            belief = cls(
                belief_id=data.get('id', content.proposition_id),
                content=content.canonical_form,
                level=directness_to_level.get(prov.directness, EpistemicLevel.EMPIRICAL),
                status=BeliefStatus.ESTABLISHED,
                credence=Credence(value=credence_value, uncertainty=uncertainty),
                domain=content.domain or ''
            )

        # Store v2 data for later use
        if 'content' in data:
            from src.models.propositional_content import PropositionalContent
            belief.content_v2 = PropositionalContent.from_dict(data['content'])
        if 'status' in data:
            from src.models.epistemic_status import EpistemicStatus
            belief.status_v2 = EpistemicStatus.from_dict(data['status'])
        if 'provenance' in data:
            from src.models.provenance import Provenance
            belief.provenance_v2 = Provenance.from_dict(data['provenance'])

        return belief

    def has_v2_data(self) -> bool:
        """Check if this belief has v2 composition data."""
        return self.content_v2 is not None or self.status_v2 is not None or self.provenance_v2 is not None

    def get_rank_pair(self) -> Optional['RankPair']:
        """Get Spohn rank pair from v2 status, or compute from credence."""
        if self.status_v2 is not None:
            return self.status_v2.ranks

        # Compute from legacy credence
        from src.models.epistemic_status import RankPair
        return RankPair.from_credence(self.credence.value, self.credence.uncertainty)

    def get_warrant_status(self) -> Optional['WarrantStatus']:
        """Get Pollock warrant status from v2 status."""
        if self.status_v2 is not None:
            return self.status_v2.warrant_status
        return None

    def get_grounding_score(self) -> float:
        """Get Haack grounding score from v2 provenance, or estimate from level."""
        if self.provenance_v2 is not None:
            return self.provenance_v2.grounding_score

        # Estimate from level
        grounding_map = {
            EpistemicLevel.OBSERVATIONAL: 1.0,
            EpistemicLevel.EMPIRICAL: 0.7,
            EpistemicLevel.INTERMEDIATE: 0.4,
            EpistemicLevel.THEORETICAL: 0.2,
        }
        return grounding_map.get(self.level, 0.3)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'Belief':
        """Create Belief from dictionary."""
        scope = None
        if 'scope' in d and d['scope']:
            scope = ScopeConditions.from_dict(d['scope'])

        # Parse enabling conditions (Tier 1 addition)
        enabling_conditions = None
        if 'enabling_conditions' in d and d['enabling_conditions']:
            enabling_conditions = EnablingConditions.from_dict(d['enabling_conditions'])

        # Parse credence history (Tier 1 addition)
        credence_history = []
        if 'credence_history' in d and d['credence_history']:
            credence_history = [
                CredenceHistoryEntry.from_dict(h) for h in d['credence_history']
            ]

        # Parse source depth (Tier 1 addition)
        source_depth_str = d.get('source_depth', 'full_text')
        try:
            source_depth = SourceDepth(source_depth_str)
        except ValueError:
            source_depth = SourceDepth.FULL_TEXT

        # Parse inference type (Sprint 1.6 addition)
        inference_type_str = d.get('inference_type', 'unknown')
        try:
            inference_type = InferenceType(inference_type_str)
        except ValueError:
            inference_type = InferenceType.UNKNOWN

        # Parse belief kind (Sprint 1.6 addition)
        belief_kind_str = d.get('belief_kind', 'evidential')
        try:
            belief_kind = BeliefKind(belief_kind_str)
        except ValueError:
            belief_kind = BeliefKind.EVIDENTIAL

        # Parse provenance (Sprint 2.5 addition)
        provenance = None
        if 'provenance' in d and d['provenance'] and SOCIAL_EPISTEMOLOGY_AVAILABLE:
            provenance = se.BeliefProvenance.from_dict(d['provenance'])

        # Parse community associations (Sprint 2.5 addition)
        community_associations = d.get('community_associations', {})

        # Parse v2 composition fields (ARCH-4 addition)
        content_v2 = None
        status_v2 = None
        provenance_v2 = None
        if 'content_v2' in d and d['content_v2']:
            try:
                from src.models.propositional_content import PropositionalContent
                content_v2 = PropositionalContent.from_dict(d['content_v2'])
            except Exception:
                pass  # Graceful degradation
        if 'status_v2' in d and d['status_v2']:
            try:
                from src.models.epistemic_status import EpistemicStatus
                status_v2 = EpistemicStatus.from_dict(d['status_v2'])
            except Exception:
                pass
        if 'provenance_v2' in d and d['provenance_v2']:
            try:
                from src.models.provenance import Provenance
                provenance_v2 = Provenance.from_dict(d['provenance_v2'])
            except Exception:
                pass

        credence_data = d.get('credence', {})
        if isinstance(credence_data, dict):
            credence = Credence(
                value=credence_data.get('credence', credence_data.get('value', 0.5)),
                # Panel Review 2026-02-12 (Kahneman): Default uncertainty 0.5, not 0.4
                uncertainty=credence_data.get('uncertainty', 0.5),
                n_supporting=credence_data.get('n_supporting', 0),
                n_contradicting=credence_data.get('n_contradicting', 0),
                n_observations=credence_data.get('n_observations', 0)
            )
        else:
            credence = Credence(0.5, 0.5)  # Panel Review 2026-02-12: wider uncertainty

        return cls(
            belief_id=d.get('belief_id', ''),
            content=d.get('content', ''),
            level=EpistemicLevel(d.get('level', 'empirical')),
            status=BeliefStatus(d.get('status', 'stub')),
            credence=credence,
            _legacy_entrenchment=d.get('entrenchment', 0.5),  # V23.0.0: Legacy field for backward compat
            paper_ids=d.get('paper_ids', []),
            theory_id=d.get('theory_id'),
            domain=d.get('domain', ''),
            tags=d.get('tags', []),
            scope=scope,
            scope_population=d.get('scope_population'),
            scope_context=d.get('scope_context'),
            scope_temporal=d.get('scope_temporal'),
            environment_id=d.get('environment_id'),
            outcome_id=d.get('outcome_id'),
            evidence_cluster_id=d.get('evidence_cluster_id'),
            source_lab=d.get('source_lab'),
            source_institution=d.get('source_institution'),
            study_method=d.get('study_method'),
            evidence_effect_size=d.get('evidence_effect_size'),
            evidence_p_value=d.get('evidence_p_value'),
            evidence_sample_n=d.get('evidence_sample_n'),
            # Tier 1 additions
            source_depth=source_depth,
            enabling_conditions=enabling_conditions,
            contested=d.get('contested', False),
            credence_history=credence_history,
            # Sprint 1.6 additions
            inference_type=inference_type,
            belief_kind=belief_kind,
            # Sprint 2.5 additions
            provenance=provenance,
            community_associations=community_associations,
            # ARCH-4 v2 composition fields
            content_v2=content_v2,
            status_v2=status_v2,
            provenance_v2=provenance_v2
        )


# `UncertainQuantity`, `Constraint`, and `TheoryWorld` are now provided by
# `src/services/web_of_belief_components.graph_models`.


# =============================================================================
# THE WEB OF BELIEF
# =============================================================================

class WebOfBelief:
    """
    A Quinean web of belief with reflective equilibrium dynamics.
    
    Core principles:
    1. Beliefs at all levels are uncertain and revisable
    2. Coherence is assessed by constraint satisfaction
    3. Evidence can shift beliefs at any level
    4. Joint distribution over theory-worlds (not independent)
    5. Findings can exist as stubs without theory attachment
    6. System seeks reflective equilibrium
    """
    
    def __init__(self, domain: str = "neuroarchitecture"):
        # Facade-to-state architecture: mutable graph data lives in self._state.
        self._state = _WebOfBeliefState(domain=domain)
        self._engines = _WebOfBeliefEngines()
        self._mutations = _WebMutationOperations(
            _MutationContracts(
                belief_factory=Belief,
                constraint_factory=Constraint,
                credence_factory=Credence,
                credence_adjustment_factory=_CredenceAdjustment,
                choose_adjustment_target=_choose_adjustment_target,
                compute_credence_adjustment=_compute_credence_adjustment,
                build_evidence_input=_build_evidence_input,
                init_updates_payload=_init_evidence_updates_payload,
                make_belief_update_record=_make_belief_update_record,
                make_temporal_update_record=_make_temporal_update_record,
                make_theory_world_update_records=_make_theory_world_update_records,
                ensure_theory_relevance=_ensure_theory_relevance,
                status_stub=BeliefStatus.STUB,
                status_tentative=BeliefStatus.TENTATIVE,
                status_anomalous=BeliefStatus.ANOMALOUS,
                level_theoretical=EpistemicLevel.THEORETICAL,
                level_empirical=EpistemicLevel.EMPIRICAL,
                ctype_supports=ConstraintType.SUPPORTS,
                ctype_contradicts=ConstraintType.CONTRADICTS,
                ctype_instantiates=ConstraintType.INSTANTIATES,
                ctype_bridges=ConstraintType.BRIDGES,
                ctype_strong_tension=ConstraintType.STRONG_TENSION,
                causal_direction_mediated=CausalDirection.MEDIATED,
            )
        )
        self._analysis = _WebAnalysisOperations(
            _AnalysisContracts(
                credence_factory=Credence,
                centrality_input_factory=_CentralityInput,
                compute_centrality=_compute_centrality,
                epistemic_value_input_factory=_EpistemicValueInput,
                compute_epistemic_value=_compute_epistemic_value,
                belief_value_record_factory=_BeliefValueRecord,
                sort_value_records=_sort_value_records,
                compute_independence_score=_compute_independence_score,
                experiment_belief_input_factory=_ExperimentBeliefInput,
                infer_experiment_type=_infer_experiment_type_contract,
                infer_test_focus_and_hypothesis=_infer_test_focus_and_hypothesis,
                suggest_scope=_suggest_scope_contract,
                suggest_contested_scope=_suggest_contested_scope_contract,
                identify_scope_differences=_identify_scope_differences_contract,
                estimate_resolution=_estimate_resolution_contract,
                epistemic_levels=list(EpistemicLevel),
                level_theoretical=EpistemicLevel.THEORETICAL,
                level_empirical=EpistemicLevel.EMPIRICAL,
                level_observational=EpistemicLevel.OBSERVATIONAL,
                status_anomalous=BeliefStatus.ANOMALOUS,
            )
        )
        self._debug_invariants = os.getenv("WEB_OF_BELIEF_ASSERT_INVARIANTS", "").strip().lower() in {
            "1",
            "true",
            "yes",
            "on",
        }

        # Stable facade attributes (legacy/public compatibility).
        self.domain = domain
        self.beliefs: Dict[str, Belief] = self._state.beliefs
        self.constraints: Dict[str, Constraint] = self._state.constraints
        self.theory_ids: Set[str] = self._state.theory_ids
        self.theory_worlds: Dict[str, TheoryWorld] = self._state.theory_worlds
        self._beliefs_by_level: Dict[EpistemicLevel, List[str]] = self._state.beliefs_by_level
        self._beliefs_by_theory: Dict[str, List[str]] = self._state.beliefs_by_theory
        self._constraints_by_belief: Dict[str, List[str]] = self._state.constraints_by_belief
        self._stubs: Set[str] = self._state.stubs
        self._coherence_score: float = 0.5
        self._tensions: List[Dict[str, Any]] = self._state.tensions
        self._entrenchment_cache: Dict[str, float] = self._state.entrenchment_cache
        self._entrenchment_cache_valid: bool = False
        self.version: int = 0
        self.created_at = datetime.now(timezone.utc)
        self.last_updated = datetime.now(timezone.utc)
    
    # =========================================================================
    # ENTRENCHMENT (V23.0.0 - EMERGENT, NOT STORED)
    # =========================================================================

    # Level weights for entrenchment calculation (foundherentism)
    # Theoretical beliefs are naturally more entrenched, but this is soft -
    # a highly-connected observation can still outrank an isolated theory.
    _LEVEL_WEIGHTS: Dict[EpistemicLevel, float] = dict(
        _DEFAULT_ENTRENCHMENT_LEVEL_WEIGHTS
    )

    def get_entrenchment(self, belief_id: str) -> float:
        """
        Compute entrenchment for a belief (V23.0.0).

        Per panel consultation (2026-02-08):
        - Entrenchment is EMERGENT from web structure, not a stored property
        - Uses Thagard formula: connectivity (40%) + level (30%) + coherence_contrib (30%)
        - Cached with invalidation on constraint changes

        This replaces the old belief.entrenchment field which violated Quinean
        coherentism by creating hidden foundationalism.

        Args:
            belief_id: The belief to compute entrenchment for

        Returns:
            Entrenchment value (0.0 to 1.0)
        """
        if belief_id not in self.beliefs:
            return 0.0

        # Check cache
        if self._entrenchment_cache_valid and belief_id in self._entrenchment_cache:
            return self._entrenchment_cache[belief_id]

        # Compute entrenchment using Thagard formula
        entrenchment = self._compute_entrenchment(belief_id)

        # Cache result
        self._entrenchment_cache[belief_id] = entrenchment
        return entrenchment

    def _compute_entrenchment(self, belief_id: str) -> float:
        """
        Compute entrenchment using Thagard formula.

        Formula: 0.4 * connectivity + 0.3 * level_weight + 0.3 * coherence_contribution

        Per panel:
        - Thagard: Connectivity and level matter
        - Simon: Coherence contribution is expensive, use simplified proxy
        - Cartwright: Allow soft hierarchy but not hard foundationalism
        """
        components = self._compute_entrenchment_components(belief_id)
        return components["entrenchment"]

    def get_entrenchment_components(self, belief_id: str) -> Dict[str, Any]:
        """
        Return entrenchment component breakdown for monitoring.

        V23.0.0: Entrenchment is emergent. This exposes the inputs used
        in the Thagard formula for admin diagnostics and timeline tracking.
        """
        return self._compute_entrenchment_components(belief_id)

    def _compute_entrenchment_components(self, belief_id: str) -> Dict[str, Any]:
        """Compute component parts for entrenchment."""
        belief = self.beliefs.get(belief_id)
        if not belief:
            return _empty_entrenchment_components().to_dict()

        constraint_count = len(self._constraints_by_belief.get(belief_id, []))
        payload = _EntrenchmentInput(
            belief_id=belief_id,
            belief_level=belief.level,
            credence_value=belief.credence.value,
            credence_uncertainty=belief.credence.uncertainty,
            belief_status=belief.status,
            constraint_count=constraint_count,
        )
        try:
            components = _compute_entrenchment_components_contract(
                payload,
                self._LEVEL_WEIGHTS,
            )
        except ValueError as exc:
            logger.warning(
                "Entrenchment contract violation for %s: %s",
                belief_id,
                exc,
            )
            return _empty_entrenchment_components().to_dict()

        return components.to_dict()

    def _invalidate_entrenchment_cache(self) -> None:
        """Invalidate entrenchment cache (call when constraints change)."""
        self._entrenchment_cache_valid = False
        self._entrenchment_cache.clear()

    def _validate_entrenchment_cache(self) -> None:
        """Mark entrenchment cache as valid."""
        self._entrenchment_cache_valid = True

    def _assert_invariants_if_enabled(self) -> None:
        if self._debug_invariants:
            self.assert_invariants(raise_on_error=True)

    def assert_invariants(self, raise_on_error: bool = True) -> List[str]:
        """Check structural/probabilistic invariants for health monitoring."""
        errors: List[str] = []
        eps = 1e-6

        if not (0.0 - eps <= self._coherence_score <= 1.0 + eps):
            errors.append(f"coherence out of range: {self._coherence_score}")

        for belief_id, belief in self.beliefs.items():
            if belief.level not in EpistemicLevel:
                errors.append(f"belief {belief_id} has invalid level: {belief.level}")
            if belief.status not in BeliefStatus:
                errors.append(f"belief {belief_id} has invalid status: {belief.status}")
            if not (0.0 - eps <= belief.credence.value <= 1.0 + eps):
                errors.append(f"belief {belief_id} credence out of range: {belief.credence.value}")
            if not (0.0 - eps <= belief.credence.uncertainty <= 1.0 + eps):
                errors.append(
                    f"belief {belief_id} uncertainty out of range: {belief.credence.uncertainty}"
                )

        for level, belief_ids in self._beliefs_by_level.items():
            for belief_id in belief_ids:
                belief = self.beliefs.get(belief_id)
                if belief is None:
                    errors.append(f"missing belief in _beliefs_by_level: {belief_id}")
                    continue
                if belief.level != level:
                    errors.append(
                        f"belief-level mismatch for {belief_id}: idx={level}, belief={belief.level}"
                    )

        for theory_id, belief_ids in self._beliefs_by_theory.items():
            for belief_id in belief_ids:
                belief = self.beliefs.get(belief_id)
                if belief is None:
                    errors.append(f"missing belief in _beliefs_by_theory: {belief_id}")
                    continue
                if belief.theory_id != theory_id:
                    errors.append(
                        f"belief-theory mismatch for {belief_id}: idx={theory_id}, belief={belief.theory_id}"
                    )

        for belief_id in self._stubs:
            belief = self.beliefs.get(belief_id)
            if belief is None:
                errors.append(f"missing stub belief: {belief_id}")
                continue
            if belief.status != BeliefStatus.STUB:
                errors.append(f"stub set contains non-stub belief: {belief_id}")

        for constraint_id, constraint in self.constraints.items():
            if constraint.source_id not in self.beliefs:
                errors.append(f"constraint {constraint_id} missing source: {constraint.source_id}")
            if constraint.target_id not in self.beliefs:
                errors.append(f"constraint {constraint_id} missing target: {constraint.target_id}")
            if not (0.0 - eps <= float(constraint.strength) <= 1.0 + eps):
                errors.append(
                    f"constraint {constraint_id} strength out of range: {constraint.strength}"
                )
            source_constraints = self._constraints_by_belief.get(constraint.source_id, [])
            if constraint_id not in source_constraints:
                errors.append(
                    f"constraint {constraint_id} missing source index for {constraint.source_id}"
                )
            if constraint.bidirectional:
                target_constraints = self._constraints_by_belief.get(constraint.target_id, [])
                if constraint_id not in target_constraints:
                    errors.append(
                        f"constraint {constraint_id} missing target index for {constraint.target_id}"
                    )

        for belief_id, constraint_ids in self._constraints_by_belief.items():
            for constraint_id in constraint_ids:
                constraint = self.constraints.get(constraint_id)
                if constraint is None:
                    errors.append(
                        f"constraints_by_belief references missing constraint {constraint_id}"
                    )
                    continue
                if belief_id not in (constraint.source_id, constraint.target_id):
                    errors.append(
                        f"constraints_by_belief mismatch: {belief_id} not in {constraint_id}"
                    )

        for tension in self._tensions:
            source_id = tension.get("source")
            target_id = tension.get("target")
            if source_id not in self.beliefs:
                errors.append(f"tension source missing: {source_id}")
            if target_id not in self.beliefs:
                errors.append(f"tension target missing: {target_id}")

        if self.theory_worlds:
            total = sum(world.posterior for world in self.theory_worlds.values())
            if abs(total - 1.0) > eps:
                errors.append(f"theory world posterior total != 1.0: {total}")
            for world_id, world in self.theory_worlds.items():
                if world.posterior < -eps:
                    errors.append(f"negative posterior in world {world_id}: {world.posterior}")
            for theory_id in self.theory_ids:
                marginal = self.marginal_theory_probability(theory_id)
                if not (-eps <= marginal <= 1.0 + eps):
                    errors.append(
                        f"marginal out of range for {theory_id}: {marginal}"
                    )

        if errors and raise_on_error:
            raise AssertionError("Invariant violations: " + "; ".join(errors[:5]))
        return errors

    # =========================================================================
    # BELIEF MANAGEMENT
    # =========================================================================

    def add_belief(
        self,
        belief: Belief,
        connect_to: Optional[List[Tuple[str, ConstraintType, float]]] = None
    ) -> None:
        """
        Add a belief to the web.
        
        Args:
            belief: The belief to add
            connect_to: Optional list of (belief_id, constraint_type, strength)
                        for creating initial constraints
        """
        self._mutations.add_belief(self, belief=belief, connect_to=connect_to)
    
    def add_stub(
        self,
        belief_id: str,
        content: str,
        paper_id: str,
        level: EpistemicLevel = EpistemicLevel.EMPIRICAL,
        initial_credence: float = 0.5,
        tags: List[str] = None
    ) -> Belief:
        """
        Add an unintegrated finding (stub) to the web.
        
        Stubs are beliefs that exist but are not yet connected to the
        theoretical structure. They represent the "edge" of our knowledge
        that may eventually be integrated or may remain anomalous.
        """
        # V23.0.0: Entrenchment is now computed, not stored.
        # Stubs naturally have low entrenchment due to:
        # - Few constraints (low connectivity)
        # - STUB status (negative coherence contribution)
        # Panel Review 2026-02-12 (Kahneman): wider default uncertainty (0.5)
        belief = Belief(
            belief_id=belief_id,
            content=content,
            level=level,
            status=BeliefStatus.STUB,
            credence=Credence(initial_credence, 0.5),
            paper_ids=[paper_id],
            tags=tags or []
        )
        
        self.add_belief(belief)
        return belief
    
    def add_constraint(self, constraint: Constraint) -> None:
        """
        Add a constraint between beliefs.

        Per expert panel (Pearl): MEDIATED causal direction requires specification
        of the mediator variable for proper causal reasoning about blocking/confounding.
        """
        self._mutations.add_constraint(self, constraint=constraint)
    
    def integrate_stub(
        self,
        stub_id: str,
        theory_id: str,
        constraint_type: ConstraintType = ConstraintType.INSTANTIATES,
        constraint_strength: float = 0.5
    ) -> None:
        """
        Integrate a stub into the theoretical structure.
        
        This connects an orphan finding to a theory, changing its status
        from STUB to TENTATIVE.
        """
        self._mutations.integrate_stub(
            self,
            stub_id=stub_id,
            theory_id=theory_id,
            constraint_type=constraint_type,
            constraint_strength=constraint_strength,
        )

    def integrate_bridge(
        self,
        bridge,  # BridgeWarrant from bridge_warrants module
        create_constraints: bool = True
    ) -> Dict[str, Any]:
        """
        Integrate a bridge warrant into the web.

        Sprint 3: Bridge warrants create constraints between source and target beliefs.
        When a bridge is integrated:
        1. BRIDGES constraints are created between connected beliefs
        2. If bridge has failed, STRONG_TENSION constraints are created
        3. Web coherence is recalculated

        Args:
            bridge: BridgeWarrant instance from src/services/bridge_warrants
            create_constraints: Whether to create constraints (default True)

        Returns:
            Dict with integration summary
        """
        return self._mutations.integrate_bridge(
            self,
            bridge=bridge,
            create_constraints=create_constraints,
        )

    # =========================================================================
    # THEORY WORLDS
    # =========================================================================
    
    def register_theory(self, theory_id: str, prior: float = 0.5) -> None:
        """
        Register a theory and rebuild the world space.
        
        The world space is the set of all possible truth-value assignments
        to theories. With n theories, there are 2^n worlds.
        """
        if theory_id in self.theory_ids:
            return
        
        self.theory_ids.add(theory_id)
        self._rebuild_theory_worlds()
        self._assert_invariants_if_enabled()
    
    def _rebuild_theory_worlds(self) -> None:
        """Rebuild the space of theory worlds."""
        theory_priors: Dict[str, float] = {}
        for theory_id in self.theory_ids:
            theory_beliefs = [
                belief
                for belief in self.beliefs.values()
                if belief.theory_id == theory_id and belief.level == EpistemicLevel.THEORETICAL
            ]
            theory_priors[theory_id] = theory_beliefs[0].credence.value if theory_beliefs else 0.5
        self.theory_worlds = self._engines.theory_worlds.rebuild_worlds(
            theory_ids=self.theory_ids,
            theory_priors=theory_priors,
        )
    
    def _world_id(self, true_set: Set[str], false_set: Set[str]) -> str:
        """Generate canonical world ID."""
        return self._engines.theory_worlds.world_id(true_set, false_set)
    
    def update_theory_worlds(
        self,
        evidence_belief_id: str,
        theory_likelihoods: Dict[str, float]
    ) -> None:
        """
        Update the joint distribution over theory worlds.
        
        Args:
            evidence_belief_id: The evidence (belief) being incorporated
            theory_likelihoods: P(evidence | theory=true) for each theory
                               If theory not in dict, assume P=0.5
        """
        if not self.theory_worlds:
            return
        self._engines.theory_worlds.update_posteriors(
            worlds=self.theory_worlds,
            theory_ids=self.theory_ids,
            theory_likelihoods=theory_likelihoods,
        )
        self._assert_invariants_if_enabled()
    
    def marginal_theory_probability(self, theory_id: str) -> float:
        """
        Compute P(theory=true | all evidence).
        
        This is the marginal probability, summing over all worlds where
        the theory is true.
        """
        return self._engines.theory_worlds.marginal(
            worlds=self.theory_worlds,
            theory_id=theory_id,
            default=0.5,
        )
    
    def joint_probability(self, true_theories: Set[str]) -> float:
        """
        Compute P(these theories all true | evidence).
        """
        return self._engines.theory_worlds.joint(
            worlds=self.theory_worlds,
            true_theories=true_theories,
        )
    
    def conditional_probability(
        self,
        target_theory: str,
        given_theories: Dict[str, bool]
    ) -> float:
        """
        Compute P(target=true | given_theories, evidence).
        
        Example: P(SRT | ART=true, evidence)
        """
        return self._engines.theory_worlds.conditional(
            worlds=self.theory_worlds,
            target_theory=target_theory,
            given_theories=given_theories,
            default=0.5,
        )
    
    # =========================================================================
    # COHERENCE AND REFLECTIVE EQUILIBRIUM
    # =========================================================================
    
    def _update_coherence(self) -> None:
        """
        Compute overall coherence of the web.
        
        Coherence is high when:
        - Supporting constraints connect high-credence beliefs
        - Contradicting constraints connect to low-credence beliefs
        - Few tensions (high-credence beliefs in contradiction)
        """
        result: _CoherenceResult = self._engines.coherence.recompute(
            beliefs=self.beliefs,
            constraints=self.constraints.values(),
        )
        self._coherence_score = result.coherence_score
        self._tensions = result.tensions
    
    def seek_equilibrium(self, max_iterations: int = 10) -> Dict[str, Any]:
        """
        Iteratively adjust beliefs to improve coherence.
        
        This implements a simplified reflective equilibrium: beliefs that
        are in tension with many others get their credence adjusted.
        
        Returns:
            Summary of adjustments made
        """
        return self._mutations.seek_equilibrium(self, max_iterations=max_iterations)
    
    def coherence_score(self) -> float:
        return self._coherence_score
    
    def tensions(self) -> List[Dict[str, Any]]:
        return self._tensions.copy()

    # =========================================================================
    # VALUE COMPUTATION (Sprint 1.6.3 - P-EC Panel: Chang)
    # =========================================================================

    def belief_centrality(self, belief_id: str) -> float:
        """
        Compute centrality of a belief in the web.

        Sprint 1.6.3: Centrality measures how connected a belief is.
        High centrality = belief is crucial to the web structure.

        Per P-EC panel (Chang): Beliefs with high centrality have high
        "epistemic value" because revising them would cascade through the web.

        Returns:
            Normalized centrality score [0, 1]. 0 = no connections, 1 = highly connected.
        """
        return self._analysis.belief_centrality(self, belief_id)

    def belief_sensitivity(self, belief_id: str, delta: float = 0.1) -> float:
        """
        Estimate sensitivity of web coherence to changes in this belief.

        Sprint 1.6.3: Sensitivity measures how much coherence changes when
        this belief's credence changes by delta.

        Per P-EC panel (Chang): High sensitivity beliefs are "fragile points"
        - revising them would significantly affect overall coherence.

        Args:
            belief_id: The belief to test
            delta: Amount to perturb credence (default 0.1)

        Returns:
            Sensitivity score [0, 1]. Higher = coherence more sensitive to this belief.
        """
        return self._analysis.belief_sensitivity(self, belief_id, delta=delta)

    def belief_value(self, belief_id: str, centrality_weight: float = 0.5) -> float:
        """
        Compute combined epistemic value of a belief.

        Sprint 1.6.3: Value combines centrality (structural importance) and
        sensitivity (fragility). High-value beliefs are both central and sensitive.

        Per P-EC panel (Chang, SY-9): This metric identifies beliefs that are
        most worth investigating - they're structurally important AND their
        revision would significantly affect the web.

        Args:
            belief_id: The belief to evaluate
            centrality_weight: Weight for centrality vs sensitivity (default 0.5)

        Returns:
            Value score [0, 1]. Higher = more epistemically valuable.
        """
        return self._analysis.belief_value(self, belief_id, centrality_weight=centrality_weight)

    def beliefs_by_value(self, top_n: Optional[int] = None) -> List[Tuple[str, float, float, float]]:
        """
        Rank all beliefs by their epistemic value.

        Sprint 1.6.3: Returns beliefs sorted by value (descending).

        Args:
            top_n: Return only top N beliefs (None for all)

        Returns:
            List of (belief_id, value, centrality, sensitivity) tuples.
        """
        return self._analysis.beliefs_by_value(self, top_n=top_n)

    def compute_independence_score(
        self,
        belief_ids: Optional[List[str]] = None,
    ) -> Dict[str, float]:
        """
        ARCH-3b: Score evidential independence via lab × method × population diversity.

        Args:
            belief_ids: Optional subset of belief IDs. Defaults to all beliefs.
        """
        return self._analysis.compute_independence_score(self, belief_ids=belief_ids)

    def high_value_beliefs(self, threshold: float = 0.5) -> List[Dict[str, Any]]:
        """
        Get beliefs above a value threshold with details.

        Sprint 1.6.3: Convenience method for identifying investigation targets.

        Args:
            threshold: Minimum value to include (default 0.5)

        Returns:
            List of dicts with belief details and value metrics.
        """
        return self._analysis.high_value_beliefs(self, threshold=threshold)

    # =========================================================================
    # TENSION-RESOLVING EXPERIMENTS (Sprint 1.6.4)
    # =========================================================================

    def suggest_experiments(self, max_suggestions: int = 5) -> List[Dict[str, Any]]:
        """
        Suggest experiments that could resolve tensions in the web.

        Sprint 1.6.4: Analyzes current tensions and suggests empirical
        investigations that could help resolve them.

        Per P-EC panel: Tensions are epistemically valuable - they reveal
        where our knowledge is incomplete or contradictory. Experiments
        that resolve tensions have high Value of Information (VOI).

        Args:
            max_suggestions: Maximum number of suggestions to return

        Returns:
            List of experiment suggestions with details.
        """
        return self._analysis.suggest_experiments(self, max_suggestions=max_suggestions)

    def _generate_experiment_suggestion(
        self,
        source: Belief,
        target: Belief,
        tension: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Generate an experiment suggestion for a specific tension.

        Sprint 1.6.4: Creates structured experiment recommendations.
        """
        return self._analysis.generate_experiment_suggestion(self, source, target, tension)

    def _generate_contested_experiment(self, belief: Belief) -> Optional[Dict[str, Any]]:
        """
        Generate experiment suggestion for a contested belief.

        Sprint 1.6.4: Contested beliefs (oscillating credence) indicate
        genuine disagreement that experimentation could resolve.
        """
        return self._analysis.generate_contested_experiment(self, belief)

    def _to_experiment_input(self, belief: Belief) -> _ExperimentBeliefInput:
        return self._analysis.to_experiment_input(belief)

    def _infer_experiment_type(self, source: Belief, target: Belief) -> str:
        """Infer what type of experiment would address the tension."""
        return self._analysis.infer_experiment_type(source, target)

    def _suggest_scope(self, source: Belief, target: Belief) -> Dict[str, Any]:
        """Suggest scope conditions for the experiment."""
        return self._analysis.suggest_scope(source, target)

    def _suggest_contested_scope(self, belief: Belief) -> Dict[str, Any]:
        """Suggest scope for contested belief experiment."""
        return self._analysis.suggest_contested_scope(belief)

    def _identify_scope_differences(self, scopes: List[ScopeConditions]) -> List[str]:
        """Identify where scope conditions differ between beliefs."""
        return self._analysis.identify_scope_differences(scopes)

    def _estimate_resolution(self, source: Belief, target: Belief) -> Dict[str, Any]:
        """Estimate how the tension might be resolved."""
        return self._analysis.estimate_resolution(source, target)

    def get_research_priorities(self, top_n: int = 10) -> Dict[str, Any]:
        """
        Get research priorities combining tensions, high-value beliefs, and experiments.

        Sprint 1.6.4: Comprehensive research agenda based on web state.

        Returns:
            Dictionary with prioritized research directions.
        """
        return self._analysis.get_research_priorities(self, top_n=top_n)

    def _generate_research_directions(self) -> List[Dict[str, str]]:
        """Generate high-level research direction recommendations."""
        return self._analysis.generate_research_directions(self)

    # =========================================================================
    # EVIDENCE PROCESSING
    # =========================================================================

    def add_evidence(
        self,
        belief_id: str,
        content: str,
        paper_id: str,
        supports_beliefs: Dict[str, float] = None,  # belief_id -> strength
        contradicts_beliefs: Dict[str, float] = None,
        theory_relevance: Dict[str, float] = None,  # theory_id -> P(evidence|theory)
        observed_temporal: Dict[str, Tuple[float, float]] = None,  # param -> (value, se)
        moderator: Optional[str] = None,
        credence: float = 0.6
    ) -> Dict[str, Any]:
        """
        Add evidence to the web and propagate updates.
        
        This is the main entry point for new findings. Evidence:
        1. Creates a new belief (or updates existing)
        2. Updates credences of supported/contradicted beliefs
        3. Updates the joint distribution over theory worlds
        4. Updates temporal parameters if observed
        5. Recalculates coherence
        
        Returns:
            Summary of all updates
        """
        return self._mutations.add_evidence(
            self,
            belief_id=belief_id,
            content=content,
            paper_id=paper_id,
            supports_beliefs=supports_beliefs,
            contradicts_beliefs=contradicts_beliefs,
            theory_relevance=theory_relevance,
            observed_temporal=observed_temporal,
            moderator=moderator,
            credence=credence,
        )
    
    # =========================================================================
    # QUERIES
    # =========================================================================
    
    def get_stubs(self) -> List[Belief]:
        """Get all unintegrated findings."""
        return self._analysis.get_stubs(self)
    
    def get_anomalies(self) -> List[Belief]:
        """Get beliefs marked as anomalous."""
        return self._analysis.get_anomalies(self)
    
    def get_beliefs_by_level(self, level: EpistemicLevel) -> List[Belief]:
        """Get all beliefs at a given epistemic level."""
        return self._analysis.get_beliefs_by_level(self, level)
    
    def get_beliefs_for_theory(self, theory_id: str) -> List[Belief]:
        """Get all beliefs associated with a theory."""
        return self._analysis.get_beliefs_for_theory(self, theory_id)
    
    # =========================================================================
    # REPORTING
    # =========================================================================
    
    def summary(self) -> str:
        """Generate a human-readable summary."""
        return self._analysis.summary(self)
    
    def to_dict(self) -> Dict[str, Any]:
        return self._analysis.to_dict(self)

    # =========================================================================
    # EPISTEMIC-CAUSAL BRIDGE (Sprint 1.5)
    # =========================================================================

    def create_causal_bridge(self) -> 'ecb.EpistemicCausalBridge':
        """
        Create an epistemic-causal bridge for this web.

        The bridge integrates:
        1. Quinean epistemic layer (beliefs, credences, entrenchment)
        2. Pearlian causal layer (DAGs, SCMs, do-calculus)
        3. Van Fraassen contrast classes (population-relative meaning)

        Returns:
            EpistemicCausalBridge: Bridge instance connected to this web

        Raises:
            ImportError: If epistemic_causal_bridge module not available

        Example:
            bridge = web.create_causal_bridge()
            bridge.build_causal_models()
            result = bridge.counterfactual(
                intervention={"nature": 1.0},
                outcome="stress"
            )
        """
        if not BRIDGE_AVAILABLE:
            raise ImportError(
                "Epistemic-causal bridge not available. "
                "Ensure src/services/epistemic_causal_bridge.py exists."
            )
        return ecb.EpistemicCausalBridge(self)

    def counterfactual(
        self,
        intervention: Dict[str, float],
        outcome: str,
        evidence: Optional[Dict[str, float]] = None,
        credence_threshold: float = 0.5
    ) -> Any:
        """
        Convenience method for counterfactual queries.

        Builds causal models from the web and computes a counterfactual
        with full Quinean analysis (robustness, coherence, scope).

        Args:
            intervention: Dict mapping variable names to intervention values
            outcome: Name of the outcome variable to query
            evidence: Optional dict of observed evidence
            credence_threshold: Minimum credence for beliefs to include

        Returns:
            QuineanCounterfactualResult with point estimate, CI, and quality metrics

        Example:
            result = web.counterfactual(
                intervention={"nature_exposure": 1.0},
                outcome="stress_level"
            )
            print(result.summary())
        """
        if not BRIDGE_AVAILABLE:
            raise ImportError(
                "Epistemic-causal bridge not available. "
                "Ensure src/services/epistemic_causal_bridge.py exists."
            )

        bridge = ecb.EpistemicCausalBridge(self)
        bridge.build_causal_models(credence_threshold=credence_threshold)
        return bridge.counterfactual(
            intervention=intervention,
            outcome=outcome,
            evidence=evidence
        )

    def causal_bridge_available(self) -> bool:
        """Check if the epistemic-causal bridge module is available."""
        return BRIDGE_AVAILABLE

    def snapshot(self) -> 'WebOfBeliefSnapshot':
        """
        Create an immutable snapshot of the web for query operations.

        Per Lamport (panel validation 2026-01-22): Route handlers should use
        snapshots for reads to ensure consistency during query execution.

        The snapshot is taken at call time and will not reflect any subsequent
        changes to the web. This provides snapshot isolation semantics for
        query operations.

        Returns:
            WebOfBeliefSnapshot: A frozen copy of the web state
        """
        fields = self._engines.snapshots.build_fields(
            domain=self.domain,
            version=self.version,
            beliefs=self.beliefs,
            constraints=self.constraints,
            coherence_score=self._coherence_score,
            tensions=self._tensions,
            theory_ids=self.theory_ids,
            stubs=self._stubs,
        )
        return WebOfBeliefSnapshot(**fields)


# =============================================================================
# SNAPSHOT CLASS (Per Lamport, panel validation 2026-01-22)
# =============================================================================

@dataclass
class WebOfBeliefSnapshot:
    """
    Immutable snapshot of the web of belief for query operations.

    Per Lamport (panel validation 2026-01-22): Queries should operate on
    snapshot of web state to ensure consistency. This class provides:

    1. Read-only access to beliefs and constraints
    2. Snapshot isolation semantics (no mutations during query)
    3. Explicit snapshot timestamp for auditing

    Usage:
        web_snapshot = web.snapshot()
        # All query operations use web_snapshot
        beliefs = web_snapshot.beliefs  # Safe, immutable copy

    Note: This snapshot is a deep copy taken at snapshot() call time.
    It will NOT reflect any subsequent changes to the source web.
    """
    domain: str
    version: int
    beliefs: Dict[str, Belief]
    constraints: Dict[str, Constraint]
    coherence_score: float
    tensions: List[Dict[str, Any]]
    theory_ids: Set[str]
    stubs: Set[str]
    snapshot_at: datetime

    def get_beliefs_by_level(self, level: EpistemicLevel) -> List[Belief]:
        """Get all beliefs at a given epistemic level."""
        return [belief for belief in self.beliefs.values() if belief.level == level]

    def get_stubs(self) -> List[Belief]:
        """Get all unintegrated findings."""
        return [self.beliefs[belief_id] for belief_id in self.stubs if belief_id in self.beliefs]

    def get_anomalies(self) -> List[Belief]:
        """Get beliefs marked as anomalous."""
        return [belief for belief in self.beliefs.values() if belief.status == BeliefStatus.ANOMALOUS]

    def to_dict(self) -> Dict[str, Any]:
        return {
            'domain': self.domain,
            'version': self.version,
            'n_beliefs': len(self.beliefs),
            'n_constraints': len(self.constraints),
            'n_stubs': len(self.stubs),
            'coherence': self.coherence_score,
            'n_tensions': len(self.tensions),
            'snapshot_at': self.snapshot_at.isoformat()
        }


# =============================================================================
# FACTORY FOR NEUROARCHITECTURE DOMAIN
# =============================================================================

def create_neuroarchitecture_web() -> WebOfBelief:
    """Create a web of belief for the neuroarchitecture domain."""
    web = WebOfBelief(domain="neuroarchitecture")
    
    # Register theories
    web.register_theory("ART")
    web.register_theory("SRT")
    web.register_theory("BIOPHILIA")
    
    # Add theoretical-level beliefs (core commitments)
    
    # ART core
    art_core = Belief(
        belief_id="ART_core",
        content="Directed attention is a finite resource restored by natural environments",
        level=EpistemicLevel.THEORETICAL,
        status=BeliefStatus.ESTABLISHED,
        credence=Credence(0.75, 0.2),
        _legacy_entrenchment=0.8,
        theory_id="ART"
    )
    art_core.temporal_params = {
        'time_to_peak': UncertainQuantity(2400, 600, lower_bound=0),  # ~40 min
        'minimum_exposure': UncertainQuantity(1200, 300, lower_bound=0),  # ~20 min
        'decay_half_life': UncertainQuantity(7200, 1800, lower_bound=0)  # ~2 hr
    }
    web.add_belief(art_core)
    
    # SRT core
    srt_core = Belief(
        belief_id="SRT_core",
        content="Natural environments trigger rapid physiological stress recovery",
        level=EpistemicLevel.THEORETICAL,
        status=BeliefStatus.ESTABLISHED,
        credence=Credence(0.72, 0.22),
        _legacy_entrenchment=0.75,
        theory_id="SRT"
    )
    srt_core.temporal_params = {
        'time_to_peak': UncertainQuantity(1200, 300, lower_bound=0),  # ~20 min
        'onset_delay': UncertainQuantity(60, 30, lower_bound=0),  # ~1 min
        'decay_half_life': UncertainQuantity(2700, 900, lower_bound=0)  # ~45 min
    }
    web.add_belief(srt_core)
    
    # Biophilia core
    bio_core = Belief(
        belief_id="BIOPHILIA_core",
        content="Humans have evolved affiliative responses to natural stimuli",
        level=EpistemicLevel.THEORETICAL,
        status=BeliefStatus.ENTRENCHED,
        credence=Credence(0.68, 0.25),
        _legacy_entrenchment=0.7,
        theory_id="BIOPHILIA"
    )
    web.add_belief(bio_core)
    
    # Add intermediate-level beliefs (generalizations, not quite theory)
    
    nature_stress = Belief(
        belief_id="nature_reduces_stress",
        content="Exposure to natural environments reduces stress markers",
        level=EpistemicLevel.INTERMEDIATE,
        status=BeliefStatus.ESTABLISHED,
        credence=Credence(0.78, 0.15),
        _legacy_entrenchment=0.6
    )
    web.add_belief(nature_stress, connect_to=[
        ("SRT_core", ConstraintType.INSTANTIATES, 0.7),
        ("BIOPHILIA_core", ConstraintType.SUPPORTS, 0.5)
    ])
    
    nature_attention = Belief(
        belief_id="nature_restores_attention",
        content="Natural environments improve directed attention capacity",
        level=EpistemicLevel.INTERMEDIATE,
        status=BeliefStatus.ESTABLISHED,
        credence=Credence(0.72, 0.18),
        _legacy_entrenchment=0.55
    )
    web.add_belief(nature_attention, connect_to=[
        ("ART_core", ConstraintType.INSTANTIATES, 0.75)
    ])
    
    # Add some empirical stubs (unintegrated findings)
    
    web.add_stub(
        belief_id="stub_birdsong",
        content="Birdsong exposure reduced self-reported anxiety (d=0.35)",
        paper_id="paper:ratcliffe2013",
        initial_credence=0.6,
        tags=["auditory", "anxiety", "nature_sounds"]
    )
    
    web.add_stub(
        belief_id="stub_fractals",
        content="Viewing fractal patterns reduced physiological stress markers",
        paper_id="paper:taylor2006",
        initial_credence=0.55,
        tags=["visual", "fractals", "stress"]
    )
    
    web.add_stub(
        belief_id="stub_window_view",
        content="Hospital patients with nature views had shorter recovery times",
        paper_id="paper:ulrich1984",
        initial_credence=0.7,
        tags=["healthcare", "recovery", "windows"]
    )
    
    # Calculate initial coherence
    web._update_coherence()
    
    return web


if __name__ == "__main__":
    # Demo
    web = create_neuroarchitecture_web()
    
    print(web.summary())
    print("\n" + "="*60 + "\n")
    
    # Add some evidence
    updates = web.add_evidence(
        belief_id="ev_hartig2003",
        content="Nature walk improved attention (d=0.55) peaking at 35 min",
        paper_id="paper:hartig2003",
        supports_beliefs={"nature_restores_attention": 0.7, "ART_core": 0.5},
        theory_relevance={"ART": 0.75, "SRT": 0.55},
        observed_temporal={"time_to_peak": (2100, 300)}
    )
    
    print("After adding Hartig 2003:")
    print(f"  Belief updates: {len(updates['belief_updates'])}")
    print(f"  Theory updates: {updates['theory_world_updates']}")
    print(f"  Coherence: {updates['coherence_before']:.3f} -> {updates['coherence_after']:.3f}")
    
    print("\n" + web.summary())
