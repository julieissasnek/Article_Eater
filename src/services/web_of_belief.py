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
from typing import List, Dict, Any, Optional, Tuple, Set, FrozenSet
from enum import Enum
from datetime import datetime, timezone
import math
import json
import logging
from collections import defaultdict
from itertools import combinations
import copy

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


# =============================================================================
# EPISTEMIC LEVELS
# =============================================================================

class EpistemicLevel(Enum):
    """
    Levels in the web of belief, from center to periphery.
    
    Following Quine: beliefs near the center are more entrenched and
    we're more reluctant to revise them. But NOTHING is unrevisable.
    """
    THEORETICAL = "theoretical"      # Core theoretical commitments
    INTERMEDIATE = "intermediate"    # Generalizations, mechanisms
    EMPIRICAL = "empirical"          # Research findings
    OBSERVATIONAL = "observational"  # Direct measurements, observations


class BeliefStatus(Enum):
    """Status of a belief in the web."""
    STUB = "stub"                  # Exists but not yet integrated
    TENTATIVE = "tentative"        # Weakly held, easily revised
    ESTABLISHED = "established"    # Well-supported by coherence
    ENTRENCHED = "entrenched"      # Central, costly to revise
    ANOMALOUS = "anomalous"        # In tension with the web


class ConstraintType(Enum):
    """Types of constraint relationships between beliefs."""
    SUPPORTS = "supports"          # Positive coherence
    CONTRADICTS = "contradicts"    # Negative coherence
    EXPLAINS = "explains"          # Theoretical → empirical
    INSTANTIATES = "instantiates"  # Empirical → theoretical
    ANALOGOUS = "analogous"        # Similar structure
    INDEPENDENT = "independent"    # No direct constraint
    BRIDGES = "bridges"            # Sprint 3: Bridge warrant connection
    STRONG_TENSION = "strong_tension"  # Sprint 3: Strong tension from failed bridge
    SHARED_EVIDENCE = "shared_evidence"  # Sprint 8: Same study supports both beliefs

    # Sprint T2-1.3: Epistemic link types
    EPISTEMIC_DERIVATION = "epistemic_derivation"        # Tier 1 → Tier 2 template
    EPISTEMIC_CROSS_TEMPLATE = "epistemic_cross_template"  # Between Tier 2 templates
    EPISTEMIC_MEDIATION = "epistemic_mediation"          # Claim mediated by interpretation
    COHERENCE_SUPPORT = "coherence_support"              # A increases coherence of B
    COHERENCE_TENSION = "coherence_tension"              # A decreases coherence of B
    ARGUMENTATIVE_SUPPORT = "argumentative_support"      # Finding supports via argument
    ARGUMENTATIVE_CHALLENGE = "argumentative_challenge"  # Finding challenges via argument
    GENERALIZABILITY_WARRANT = "generalizability_warrant"  # Type A → Type B (Sprint T2-4b)


# =============================================================================
# INFERENCE TYPE (Sprint 1.6 - P-EC Panel: Synergies)
# =============================================================================

class InferenceType(Enum):
    """
    Type of inference that produced or supports a belief.

    Sprint 1.6.1: Mark beliefs by their inferential origin.

    - INDUCTIVE: Generalization from observations (empirical → general)
    - DEDUCTIVE: Derived from theory (theory → prediction)
    - ABDUCTIVE: Inference to best explanation (data → theory)
    - MIXED: Multiple inference types combined
    - UNKNOWN: Not yet classified
    """
    INDUCTIVE = "inductive"        # Data → generalization
    DEDUCTIVE = "deductive"        # Theory → prediction
    ABDUCTIVE = "abductive"        # Data → best explanation
    MIXED = "mixed"                # Multiple types
    UNKNOWN = "unknown"            # Not classified


class BeliefKind(Enum):
    """
    Functional type of belief in the web.

    Sprint 1.6.2: Mark beliefs by their functional role.

    - MECHANISTIC: Describes causal mechanism (how X causes Y)
    - EVIDENTIAL: Reports empirical finding (X was observed)
    - THEORETICAL: Core theoretical commitment (X is fundamental)
    - METHODOLOGICAL: About measurement or methods
    - BRIDGE: Connects domains (per Cartwright's capacities)
    """
    MECHANISTIC = "mechanistic"    # Causal mechanism
    EVIDENTIAL = "evidential"      # Empirical finding
    THEORETICAL = "theoretical"    # Core commitment
    METHODOLOGICAL = "methodological"  # About methods
    BRIDGE = "bridge"              # Cross-domain connection


# =============================================================================
# CAUSAL DIRECTION (Sprint 6 - Expert Panel: Pearl)
# =============================================================================

class CausalDirection(Enum):
    """
    Causal direction for constraint relationships.

    Per expert panel (Pearl): Distinguish correlation from causation.
    Default is CORRELATIONAL for empirical, UNKNOWN for theoretical.

    Sprint 6 addition: MEDIATED for indirect causal paths.
    """
    UNKNOWN = "unknown"              # Default for theoretical claims
    CORRELATIONAL = "correlational"  # Default for empirical findings
    FORWARD = "forward"              # source → target (experimental evidence)
    REVERSE = "reverse"              # target → source
    BIDIRECTIONAL = "bidirectional"  # mutual causation
    COMMON_CAUSE = "common_cause"    # C → A, C → B (confound)
    MEDIATED = "mediated"            # A → M → B (indirect causal path)


# =============================================================================
# SOURCE DEPTH (Tier 1 - Panel: Cartwright)
# =============================================================================

class SourceDepth(Enum):
    """
    Depth of source material used for extraction.

    Per expert panel (Cartwright): Causal claims from abstracts should be
    treated with more skepticism than those from full-text analysis.
    """
    FULL_TEXT = "full_text"      # Complete paper analyzed
    ABSTRACT = "abstract"        # Only abstract available
    METADATA = "metadata"        # Only title/keywords/structured data


# =============================================================================
# EPISTEMIC TIER 2: NODE DOMAIN (Sprint T2-1.1)
# =============================================================================

class NodeDomain(str, Enum):
    """
    Knowledge domain for nodes in the web.

    Sprint T2-1.1: Enable epistemic meta-level nodes that reason about
    the web itself (coherence, source quality, reflexive monitoring).

    Existing domains are CNFA research areas. EPISTEMIC is the meta-level
    domain for beliefs ABOUT beliefs and the web structure.
    """
    BASIC_SCIENCE = "basic_science"              # Neuroscience, physiology
    ENVIRONMENTAL_PSYCHOLOGY = "environmental_psychology"  # ART, SRT, Biophilia
    METHODOLOGY = "methodology"                  # Research methods, validity
    CNFA = "cnfa"                                # Cognitive neuroscience of architecture
    EPISTEMIC = "epistemic"                      # Meta-level: beliefs about beliefs


# =============================================================================
# EPISTEMIC TIER 2: NODE SUBTYPES (Sprint T2-1.2)
# =============================================================================

class EpistemicNodeSubtype(str, Enum):
    """
    Subtypes for EPISTEMIC domain nodes.

    Sprint T2-1.2: Four templates for epistemic reasoning:
    - E1: Coherence and belief maintenance (Quinean web dynamics)
    - E2: Social epistemics (community credence, contestation)
    - E3: Epistemic emotions (curiosity, certainty, doubt signals)
    - E4: Reflective equilibrium (theory-evidence balance)
    """
    E1_COHERENCE_BELIEF_MAINTENANCE = "e1_coherence_belief_maintenance"
    E2_SOCIAL_EPISTEMICS = "e2_social_epistemics"
    E3_EPISTEMIC_EMOTIONS = "e3_epistemic_emotions"
    E4_REFLECTIVE_EQUILIBRIUM = "e4_reflective_equilibrium"


# =============================================================================
# EPISTEMIC TIER 2: PATHWAY TYPE (Sprint T2-1.4)
# =============================================================================

class PathwayType(str, Enum):
    """
    Effect pathway classification for causal edges.

    Sprint T2-1.4: Distinguish how environmental features affect outcomes:
    - SUBPERSONAL: Direct physiological effects (no interpretation needed)
    - PERSONAL_EPISTEMIC: Fully interpretation-mediated (requires cognition)
    - MIXED: Both pathways active (e.g., lighting affects circadian AND mood)

    Critical for validity assessment: photo studies cannot capture subpersonal
    pathways (no thermal, acoustic, circadian channels).
    """
    SUBPERSONAL = "subpersonal"              # Direct physiological, no interpretation
    PERSONAL_EPISTEMIC = "personal_epistemic"  # Fully interpretation-mediated
    MIXED = "mixed"                          # Both channels active


# =============================================================================
# EPISTEMIC TIER 2: REPLICATION STATUS (Sprint T2-1.5)
# =============================================================================

class ReplicationStatus(str, Enum):
    """
    Replication status of empirical claims.

    Sprint T2-1.5: Track whether findings have been independently replicated.
    Critical for source quality assessment and structural bias detection.
    """
    REPLICATED = "replicated"                    # Successfully replicated by independent lab
    PARTIALLY_REPLICATED = "partially_replicated"  # Some but not all conditions replicated
    UNREPLICATED = "unreplicated"                # Not yet attempted
    FAILED_REPLICATION = "failed_replication"    # Attempted and failed


# =============================================================================
# EPISTEMIC TIER 2: PREDICTION ERROR SUBTYPE (Sprint T2-1.6)
# =============================================================================

class PESubtype(str, Enum):
    """
    Subtypes of prediction error in environmental cognition.

    Sprint T2-1.6: When environment violates expectations, what type of
    prediction was violated?

    - FUNCTIONAL_PE: Affordance mismatch (what the space is for)
    - NAVIGATIONAL_PE: Spatial model mismatch (where things are)
    - SOCIAL_PE: Social script mismatch (who belongs, appropriate behavior)
    """
    FUNCTIONAL_PE = "functional_pe"      # Affordance mismatch
    NAVIGATIONAL_PE = "navigational_pe"  # Spatial model mismatch
    SOCIAL_PE = "social_pe"              # Social script mismatch


# =============================================================================
# SCOPE CONDITIONS (Sprint 6 - Expert Panel: Cartwright)
# =============================================================================

@dataclass
class ScopeConditions:
    """
    Scope conditions for beliefs.

    Per expert panel (Cartwright): Most "contradictions" are scope boundaries.
    Track conditions under which findings apply.

    Panel Fix 3 (Cartwright): Unknown scope ≠ Universal scope.
    Papers that don't specify scope shouldn't be assumed to apply everywhere.
    - scope_specified=False: Paper didn't report scope conditions (unknown)
    - scope_specified=True: Paper explicitly reported these scope conditions
    """
    population: Optional[str] = None      # "adults", "children", "clinical", "healthy"
    setting: Optional[str] = None         # "lab", "field", "simulated", "vr"
    duration: Optional[str] = None        # "acute", "chronic", "single_exposure"
    measurement: Optional[str] = None     # "self_report", "physiological", "behavioral"
    geography: Optional[str] = None       # "urban", "rural", "Western", "global"
    moderators: List[str] = field(default_factory=list)

    # Panel Fix 3: Distinguish between "unknown scope" and "specified scope"
    scope_specified: bool = False  # Was scope explicitly reported in paper?

    def to_dict(self) -> Dict[str, Any]:
        return {
            'population': self.population,
            'setting': self.setting,
            'duration': self.duration,
            'measurement': self.measurement,
            'geography': self.geography,
            'moderators': self.moderators.copy(),
            'scope_specified': self.scope_specified
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'ScopeConditions':
        return cls(
            population=d.get('population'),
            setting=d.get('setting'),
            duration=d.get('duration'),
            measurement=d.get('measurement'),
            geography=d.get('geography'),
            moderators=d.get('moderators', []),
            scope_specified=d.get('scope_specified', False)
        )


# =============================================================================
# ENABLING CONDITIONS (Tier 1 - Panel: Cartwright)
# =============================================================================

@dataclass
class EnablingConditions:
    """
    Enabling conditions for a belief to manifest its effect.

    Per expert panel (Cartwright): Distinct from scope conditions.
    - Scope: "This finding applies to office settings" (domain restriction)
    - Enabling: "This effect requires >30 min exposure" (activation requirement)

    Without enabling conditions, the system cannot explain why findings
    sometimes fail to replicate (mechanism blocked vs. absent).

    Panel Review (R1): Added temporal_order and dose_response per Cartwright.
    """
    minimum_exposure: Optional[str] = None     # e.g., ">30 minutes"
    baseline_state: Optional[str] = None       # e.g., "non-depressed baseline"
    concurrent_factors: List[str] = field(default_factory=list)  # Must be present
    blocking_factors: List[str] = field(default_factory=list)    # Must be absent
    threshold: Optional[str] = None            # e.g., ">300 lux illuminance"
    dosage: Optional[str] = None               # e.g., "daily exposure"
    # R1 additions (Cartwright)
    temporal_order: Optional[str] = None       # e.g., "exposure precedes outcome by >1 hour"
    dose_response: Optional[bool] = None       # Does effect scale with dosage?
    # PA-2 (Cartwright): Explicit list of acceptable dosage patterns
    # Instead of implicit hierarchy (daily > weekly), explicitly list what satisfies.
    # e.g., ["daily", "continuous", "twice_daily"] means these patterns satisfy "daily".
    # If None, falls back to exact match checking.
    dosage_satisfies: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'minimum_exposure': self.minimum_exposure,
            'baseline_state': self.baseline_state,
            'concurrent_factors': self.concurrent_factors.copy(),
            'blocking_factors': self.blocking_factors.copy(),
            'threshold': self.threshold,
            'dosage': self.dosage,
            'dosage_satisfies': self.dosage_satisfies.copy(),  # PA-2
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'EnablingConditions':
        return cls(
            minimum_exposure=d.get('minimum_exposure'),
            baseline_state=d.get('baseline_state'),
            concurrent_factors=d.get('concurrent_factors', []),
            blocking_factors=d.get('blocking_factors', []),
            threshold=d.get('threshold'),
            dosage=d.get('dosage'),
            dosage_satisfies=d.get('dosage_satisfies', []),  # PA-2
        )

    def is_empty(self) -> bool:
        """Check if any enabling conditions are specified."""
        return (
            self.minimum_exposure is None and
            self.baseline_state is None and
            len(self.concurrent_factors) == 0 and
            len(self.blocking_factors) == 0 and
            self.threshold is None and
            self.dosage is None
        )


# =============================================================================
# CREDENCE HISTORY (Tier 1 - Panel: Simon, Epistemologist)
# =============================================================================

@dataclass
class CredenceHistoryEntry:
    """
    A single entry in a belief's credence history.

    Used for stability tracking and oscillation detection.
    Per expert panel (Simon): Track credence changes to detect when
    the web has stabilized given available evidence.
    """
    timestamp: datetime
    credence_value: float
    delta: float                    # Change from previous value
    triggered_by: Optional[str]     # Paper ID that caused update
    update_reason: str = ""         # Brief description of why

    def to_dict(self) -> Dict[str, Any]:
        return {
            'timestamp': self.timestamp.isoformat(),
            'credence_value': self.credence_value,
            'delta': self.delta,
            'triggered_by': self.triggered_by,
            'update_reason': self.update_reason
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'CredenceHistoryEntry':
        ts = d.get('timestamp')
        if isinstance(ts, str):
            ts = datetime.fromisoformat(ts)
        elif ts is None:
            ts = datetime.now(timezone.utc)
        return cls(
            timestamp=ts,
            credence_value=d.get('credence_value', 0.5),
            delta=d.get('delta', 0.0),
            triggered_by=d.get('triggered_by'),
            update_reason=d.get('update_reason', '')
        )


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
        self.value = max(0.01, min(0.99, self.value))
        self.uncertainty = max(0.0, min(1.0, self.uncertainty))
    
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

    # Sprint 7: Canonical IDs for environment and outcome (Expert Panel: Bates)
    environment_id: Optional[str] = None  # e.g., "spatial.openness", "natural.vegetation"
    outcome_id: Optional[str] = None      # e.g., "psych.stress", "cog.attention"

    # Sprint 8: Evidence clustering (prevents double-counting multi-theory papers)
    evidence_cluster_id: Optional[str] = None  # e.g., "cluster:paper_123"

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
            environment_id=d.get('environment_id'),
            outcome_id=d.get('outcome_id'),
            evidence_cluster_id=d.get('evidence_cluster_id'),
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


@dataclass
class UncertainQuantity:
    """A quantity with uncertainty that can be refined by evidence."""
    estimate: float
    standard_error: float
    n_observations: int = 0
    lower_bound: Optional[float] = None
    upper_bound: Optional[float] = None
    
    # Track by moderator values
    by_moderator: Dict[str, 'UncertainQuantity'] = field(default_factory=dict)
    
    def update(self, observed: float, obs_se: float, weight: float = 1.0,
               moderator_key: Optional[str] = None) -> 'UncertainQuantity':
        """Update with new observation, optionally tracking by moderator."""
        
        # Update main estimate
        if self.n_observations == 0:
            new_estimate = observed
            new_se = obs_se
        else:
            prior_precision = 1 / (self.standard_error ** 2 + 1e-10)
            obs_precision = weight / (obs_se ** 2 + 1e-10)
            post_precision = prior_precision + obs_precision
            new_estimate = (prior_precision * self.estimate + obs_precision * observed) / post_precision
            new_se = 1 / math.sqrt(post_precision)
        
        # Apply bounds
        if self.lower_bound is not None:
            new_estimate = max(new_estimate, self.lower_bound)
        if self.upper_bound is not None:
            new_estimate = min(new_estimate, self.upper_bound)
        
        result = UncertainQuantity(
            estimate=new_estimate,
            standard_error=new_se,
            n_observations=self.n_observations + 1,
            lower_bound=self.lower_bound,
            upper_bound=self.upper_bound,
            by_moderator=copy.deepcopy(self.by_moderator)
        )
        
        # Also update moderator-specific estimate
        if moderator_key:
            if moderator_key not in result.by_moderator:
                result.by_moderator[moderator_key] = UncertainQuantity(
                    estimate=observed, standard_error=obs_se, n_observations=1,
                    lower_bound=self.lower_bound, upper_bound=self.upper_bound
                )
            else:
                result.by_moderator[moderator_key] = result.by_moderator[moderator_key].update(
                    observed, obs_se, weight
                )
        
        return result
    
    def heterogeneity(self) -> float:
        """Estimate heterogeneity across moderator values."""
        if len(self.by_moderator) < 2:
            return 0.0
        
        estimates = [uq.estimate for uq in self.by_moderator.values()]
        mean_est = sum(estimates) / len(estimates)
        variance = sum((e - mean_est) ** 2 for e in estimates) / len(estimates)
        
        # Return coefficient of variation
        if mean_est == 0:
            return 0.0
        return math.sqrt(variance) / abs(mean_est)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'estimate': self.estimate,
            'se': self.standard_error,
            'n': self.n_observations,
            'heterogeneity': self.heterogeneity(),
            'by_moderator': {k: v.estimate for k, v in self.by_moderator.items()}
        }


# =============================================================================
# CONSTRAINTS (Edges in the Web)
# =============================================================================

@dataclass
class Constraint:
    """
    A constraint relationship between beliefs.

    In a coherentist epistemology, beliefs constrain each other.
    The web is "tight" when constraints are satisfied, "loose" when
    there are tensions.

    Sprint 6 additions:
    - causal_direction: Direction of causal claim (per Pearl)
    - causal_evidence: Type of evidence supporting causal claim
    - mediator: For MEDIATED direction, what's the intervening variable?
    """
    constraint_id: str
    source_id: str
    target_id: str

    constraint_type: ConstraintType

    # Strength: how much does source constrain target?
    strength: float = 0.5  # 0 to 1

    # Bidirectional? Most constraints are.
    bidirectional: bool = True

    # Evidence for this constraint
    evidence_ids: List[str] = field(default_factory=list)

    # Sprint 6: Causal direction (Expert Panel: Pearl)
    causal_direction: CausalDirection = CausalDirection.UNKNOWN
    causal_evidence: Optional[str] = None  # "experimental", "longitudinal", "cross_sectional", "theoretical"
    mediator: Optional[str] = None  # For MEDIATED: what's the M?

    # Sprint T2-1.9: Effect pathway (for BN edges)
    pathway_type: Optional['PathwayType'] = None  # subpersonal | personal_epistemic | mixed

    def to_dict(self) -> Dict[str, Any]:
        return {
            'constraint_id': self.constraint_id,
            'source': self.source_id,
            'target': self.target_id,
            'type': self.constraint_type.value,
            'strength': self.strength,
            'bidirectional': self.bidirectional,
            'causal_direction': self.causal_direction.value,
            'causal_evidence': self.causal_evidence,
            'mediator': self.mediator,
            'evidence_ids': self.evidence_ids.copy(),
            'pathway_type': self.pathway_type.value if self.pathway_type else None
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'Constraint':
        causal_dir = d.get('causal_direction', 'unknown')
        try:
            causal_direction = CausalDirection(causal_dir)
        except ValueError:
            causal_direction = CausalDirection.UNKNOWN

        # Parse pathway_type
        pathway_type = None
        if d.get('pathway_type'):
            try:
                pathway_type = PathwayType(d['pathway_type'])
            except ValueError:
                pathway_type = None

        return cls(
            constraint_id=d.get('constraint_id', f"c:{d.get('source')}:{d.get('target')}"),
            source_id=d.get('source', d.get('source_id')),
            target_id=d.get('target', d.get('target_id')),
            constraint_type=ConstraintType(d.get('type', 'supports')),
            strength=d.get('strength', 0.5),
            bidirectional=d.get('bidirectional', True),
            evidence_ids=d.get('evidence_ids', []),
            causal_direction=causal_direction,
            causal_evidence=d.get('causal_evidence'),
            mediator=d.get('mediator'),
            pathway_type=pathway_type
        )


# =============================================================================
# THEORY WORLDS
# =============================================================================

@dataclass
class TheoryWorld:
    """
    A possible world defined by which theories are true.
    
    Instead of independent P(theory_i | evidence) for each theory,
    we maintain a joint distribution over theory combinations:
    
    P(ART ∧ SRT | evidence)      - Both true
    P(ART ∧ ¬SRT | evidence)     - ART only
    P(¬ART ∧ SRT | evidence)     - SRT only  
    P(¬ART ∧ ¬SRT | evidence)    - Neither true
    
    This captures the fact that theories are not independent—evidence
    for one may be evidence for or against another.
    """
    world_id: str
    
    # Which theories are true in this world?
    theories_true: FrozenSet[str]
    theories_false: FrozenSet[str]
    
    # Prior probability of this world
    prior: float = 0.0
    
    # Posterior probability given evidence
    posterior: float = 0.0
    
    # Log-likelihood under this world
    log_likelihood: float = 0.0
    
    def __hash__(self):
        return hash(self.world_id)
    
    def contains_theory(self, theory_id: str) -> Optional[bool]:
        """Is theory true (True), false (False), or unspecified (None)?"""
        if theory_id in self.theories_true:
            return True
        elif theory_id in self.theories_false:
            return False
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'world_id': self.world_id,
            'theories_true': list(self.theories_true),
            'theories_false': list(self.theories_false),
            'prior': self.prior,
            'posterior': self.posterior
        }


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
        self.domain = domain
        
        # Beliefs (nodes)
        self.beliefs: Dict[str, Belief] = {}
        
        # Constraints (edges)
        self.constraints: Dict[str, Constraint] = {}
        
        # Theory worlds (joint distribution)
        self.theory_ids: Set[str] = set()
        self.theory_worlds: Dict[str, TheoryWorld] = {}
        
        # Indices
        self._beliefs_by_level: Dict[EpistemicLevel, List[str]] = defaultdict(list)
        self._beliefs_by_theory: Dict[str, List[str]] = defaultdict(list)
        self._constraints_by_belief: Dict[str, List[str]] = defaultdict(list)
        self._stubs: Set[str] = set()  # Unintegrated findings
        
        # Coherence tracking
        self._coherence_score: float = 0.5
        self._tensions: List[Dict[str, Any]] = []

        # V23.0.0: Entrenchment cache (emergent, not stored)
        # Per panel consultation (2026-02-08): Entrenchment is computed dynamically
        # using Thagard formula: 40% connectivity + 30% level + 30% coherence_contrib
        self._entrenchment_cache: Dict[str, float] = {}
        self._entrenchment_cache_valid: bool = False

        # History
        self.version: int = 0
        self.created_at = datetime.now(timezone.utc)
        self.last_updated = datetime.now(timezone.utc)
    
    # =========================================================================
    # ENTRENCHMENT (V23.0.0 - EMERGENT, NOT STORED)
    # =========================================================================

    # Level weights for entrenchment calculation (foundherentism)
    # Theoretical beliefs are naturally more entrenched, but this is soft -
    # a highly-connected observation can still outrank an isolated theory.
    _LEVEL_WEIGHTS: Dict[EpistemicLevel, float] = {
        EpistemicLevel.THEORETICAL: 0.8,
        EpistemicLevel.INTERMEDIATE: 0.5,
        EpistemicLevel.EMPIRICAL: 0.3,
        EpistemicLevel.OBSERVATIONAL: 0.2,
    }

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
            return {
                "entrenchment": 0.0,
                "connectivity": 0.0,
                "level_weight": 0.0,
                "coherence_contrib": 0.0,
                "constraint_count": 0,
            }

        # Factor 1: Connectivity (40%)
        # Number of constraints involving this belief, saturating at 10
        constraint_ids = self._constraints_by_belief.get(belief_id, [])
        constraint_count = len(constraint_ids)
        connectivity = min(1.0, constraint_count / 10.0)

        # Factor 2: Epistemic level weight (30%)
        # Soft hierarchy: theories naturally more entrenched but not absolutely
        level_weight = self._LEVEL_WEIGHTS.get(belief.level, 0.3)

        # Factor 3: Coherence contribution proxy (30%)
        # Full computation is expensive. Use simplified proxy:
        # - High credence + low uncertainty = contributes positively
        # - Status ESTABLISHED or ENTRENCHED (legacy) = higher contribution
        credence_factor = belief.credence.value * (1 - belief.credence.uncertainty)

        status_bonus = {
            BeliefStatus.ESTABLISHED: 0.2,
            BeliefStatus.ENTRENCHED: 0.3,  # Legacy status, still meaningful
            BeliefStatus.TENTATIVE: 0.0,
            BeliefStatus.STUB: -0.1,
            BeliefStatus.ANOMALOUS: -0.2,
        }.get(belief.status, 0.0)

        coherence_contrib = max(0.0, min(1.0, credence_factor + status_bonus))

        # Combine with weights
        entrenchment = (
            0.4 * connectivity +
            0.3 * level_weight +
            0.3 * coherence_contrib
        )

        return {
            "entrenchment": max(0.0, min(1.0, entrenchment)),
            "connectivity": connectivity,
            "level_weight": level_weight,
            "coherence_contrib": coherence_contrib,
            "constraint_count": constraint_count,
        }

    def _invalidate_entrenchment_cache(self) -> None:
        """Invalidate entrenchment cache (call when constraints change)."""
        self._entrenchment_cache_valid = False
        self._entrenchment_cache.clear()

    def _validate_entrenchment_cache(self) -> None:
        """Mark entrenchment cache as valid."""
        self._entrenchment_cache_valid = True

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
        self.beliefs[belief.belief_id] = belief
        self._beliefs_by_level[belief.level].append(belief.belief_id)
        
        if belief.theory_id:
            self._beliefs_by_theory[belief.theory_id].append(belief.belief_id)
        
        if belief.is_stub():
            self._stubs.add(belief.belief_id)
        
        # Create constraints
        if connect_to:
            for target_id, ctype, strength in connect_to:
                if target_id in self.beliefs:
                    self.add_constraint(Constraint(
                        constraint_id=f"c:{belief.belief_id}:{target_id}",
                        source_id=belief.belief_id,
                        target_id=target_id,
                        constraint_type=ctype,
                        strength=strength
                    ))
        
        self.version += 1
        logger.debug(f"Added belief: {belief.belief_id} at level {belief.level.value}")
    
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
        # Panel Fix 1: Require mediator for MEDIATED causal direction
        if constraint.causal_direction == CausalDirection.MEDIATED:
            if constraint.mediator is None:
                raise ValueError(
                    f"MEDIATED causal direction requires mediator specification. "
                    f"Constraint {constraint.constraint_id}: source={constraint.source_id}, "
                    f"target={constraint.target_id}. Please specify what M mediates the "
                    f"relationship (A→M→B)."
                )

        self.constraints[constraint.constraint_id] = constraint
        self._constraints_by_belief[constraint.source_id].append(constraint.constraint_id)

        if constraint.bidirectional:
            self._constraints_by_belief[constraint.target_id].append(constraint.constraint_id)

        # V23.0.0: Invalidate entrenchment cache when constraints change
        self._invalidate_entrenchment_cache()

        # Recalculate coherence
        self._update_coherence()
    
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
        if stub_id not in self.beliefs:
            raise ValueError(f"Belief not found: {stub_id}")
        
        belief = self.beliefs[stub_id]
        
        if belief.status != BeliefStatus.STUB:
            logger.warning(f"Belief {stub_id} is not a stub")
            return
        
        # Update belief
        belief.theory_id = theory_id
        belief.status = BeliefStatus.TENTATIVE
        # V23.0.0: Entrenchment now computed, not stored.
        # Integration naturally increases entrenchment via:
        # - New constraints (higher connectivity)
        # - TENTATIVE status (better than STUB)

        self._stubs.discard(stub_id)
        self._beliefs_by_theory[theory_id].append(stub_id)
        
        # Find theoretical beliefs from this theory to connect to
        theory_beliefs = [
            bid for bid in self._beliefs_by_theory.get(theory_id, [])
            if self.beliefs[bid].level == EpistemicLevel.THEORETICAL
        ]
        
        for theory_belief_id in theory_beliefs:
            self.add_constraint(Constraint(
                constraint_id=f"c:{stub_id}:{theory_belief_id}",
                source_id=stub_id,
                target_id=theory_belief_id,
                constraint_type=constraint_type,
                strength=constraint_strength
            ))
        
        logger.info(f"Integrated stub {stub_id} into theory {theory_id}")

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
        result = {
            "bridge_id": bridge.bridge_id,
            "constraints_created": 0,
            "tensions_created": 0,
            "coherence_impact": 0.0
        }

        coherence_before = self._coherence_score

        if not create_constraints:
            return result

        # Create constraints between source and target beliefs
        source_beliefs = [bid for bid in bridge.source_beliefs if bid in self.beliefs]
        target_beliefs = [bid for bid in bridge.target_beliefs if bid in self.beliefs]

        # Determine constraint type based on bridge status
        if bridge.status.value == "failed":
            # Failed bridge creates strong tension
            constraint_type = ConstraintType.STRONG_TENSION
            strength = 0.9  # Strong tension
        else:
            constraint_type = ConstraintType.BRIDGES
            strength = bridge.confidence

        # Create constraints from source to target beliefs
        for source_id in source_beliefs:
            for target_id in target_beliefs:
                constraint_id = f"c:bridge:{bridge.bridge_id}:{source_id}:{target_id}"

                # Skip if constraint already exists
                if constraint_id in self.constraints:
                    continue

                constraint = Constraint(
                    constraint_id=constraint_id,
                    source_id=source_id,
                    target_id=target_id,
                    constraint_type=constraint_type,
                    strength=strength,
                    bidirectional=True,
                    evidence_ids=[bridge.bridge_id]
                )

                self.add_constraint(constraint)
                result["constraints_created"] += 1

                if constraint_type == ConstraintType.STRONG_TENSION:
                    result["tensions_created"] += 1

        # If bridge failed, also create tensions with disconfirming evidence
        if bridge.failure_record:
            for evidence_id in bridge.failure_record.disconfirming_evidence:
                if evidence_id not in self.beliefs:
                    continue

                for source_id in source_beliefs:
                    tension_id = f"c:tension:{bridge.bridge_id}:{source_id}:{evidence_id}"
                    if tension_id in self.constraints:
                        continue

                    tension = Constraint(
                        constraint_id=tension_id,
                        source_id=source_id,
                        target_id=evidence_id,
                        constraint_type=ConstraintType.CONTRADICTS,
                        strength=0.8,
                        bidirectional=True,
                        evidence_ids=[bridge.bridge_id]
                    )

                    self.add_constraint(tension)
                    result["tensions_created"] += 1

        # Recalculate coherence
        self._update_coherence()
        result["coherence_impact"] = self._coherence_score - coherence_before

        self.version += 1
        logger.info(f"Integrated bridge {bridge.bridge_id}: {result['constraints_created']} constraints, {result['tensions_created']} tensions")

        return result

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
    
    def _rebuild_theory_worlds(self) -> None:
        """Rebuild the space of theory worlds."""
        self.theory_worlds = {}
        theory_list = sorted(self.theory_ids)
        n = len(theory_list)
        
        if n == 0:
            return
        
        # Generate all 2^n combinations
        for i in range(2 ** n):
            true_theories = set()
            false_theories = set()
            
            for j, theory_id in enumerate(theory_list):
                if (i >> j) & 1:
                    true_theories.add(theory_id)
                else:
                    false_theories.add(theory_id)
            
            world_id = self._world_id(true_theories, false_theories)
            
            # Prior: assume independence initially
            prior = 1.0
            for theory_id in theory_list:
                # Use any existing credence, otherwise 0.5
                theory_beliefs = [
                    b for b in self.beliefs.values()
                    if b.theory_id == theory_id and b.level == EpistemicLevel.THEORETICAL
                ]
                if theory_beliefs:
                    p = theory_beliefs[0].credence.value
                else:
                    p = 0.5
                
                if theory_id in true_theories:
                    prior *= p
                else:
                    prior *= (1 - p)
            
            self.theory_worlds[world_id] = TheoryWorld(
                world_id=world_id,
                theories_true=frozenset(true_theories),
                theories_false=frozenset(false_theories),
                prior=prior,
                posterior=prior
            )
    
    def _world_id(self, true_set: Set[str], false_set: Set[str]) -> str:
        """Generate canonical world ID."""
        true_str = ",".join(sorted(true_set)) if true_set else "∅"
        false_str = ",".join(sorted(false_set)) if false_set else "∅"
        return f"[+{true_str}][-{false_str}]"
    
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
        
        total = 0.0
        
        for world_id, world in self.theory_worlds.items():
            # Compute P(evidence | world)
            likelihood = 1.0
            for theory_id in self.theory_ids:
                if theory_id in theory_likelihoods:
                    p_given_true = theory_likelihoods[theory_id]
                    p_given_false = 1 - p_given_true  # Simplification
                    
                    if theory_id in world.theories_true:
                        likelihood *= p_given_true
                    else:
                        likelihood *= p_given_false
            
            # Bayes: P(world | evidence) ∝ P(evidence | world) * P(world)
            world.posterior = world.prior * likelihood
            world.log_likelihood += math.log(likelihood + 1e-10)
            total += world.posterior
        
        # Normalize
        if total > 0:
            for world in self.theory_worlds.values():
                world.posterior /= total
                world.prior = world.posterior  # For next update
    
    def marginal_theory_probability(self, theory_id: str) -> float:
        """
        Compute P(theory=true | all evidence).
        
        This is the marginal probability, summing over all worlds where
        the theory is true.
        """
        if not self.theory_worlds:
            return 0.5
        
        return sum(
            world.posterior
            for world in self.theory_worlds.values()
            if theory_id in world.theories_true
        )
    
    def joint_probability(self, true_theories: Set[str]) -> float:
        """
        Compute P(these theories all true | evidence).
        """
        if not self.theory_worlds:
            return 0.5 ** len(true_theories)
        
        return sum(
            world.posterior
            for world in self.theory_worlds.values()
            if true_theories <= world.theories_true
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
        if not self.theory_worlds:
            return 0.5
        
        numerator = 0.0
        denominator = 0.0
        
        for world in self.theory_worlds.values():
            # Check if world matches given conditions
            matches_given = all(
                (theory_id in world.theories_true) == is_true
                for theory_id, is_true in given_theories.items()
            )
            
            if matches_given:
                denominator += world.posterior
                if target_theory in world.theories_true:
                    numerator += world.posterior
        
        if denominator == 0:
            return 0.5
        return numerator / denominator
    
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
        if not self.constraints:
            self._coherence_score = 0.5
            self._tensions = []
            return
        
        total_coherence = 0.0
        n_constraints = 0
        tensions = []
        
        for constraint in self.constraints.values():
            source = self.beliefs.get(constraint.source_id)
            target = self.beliefs.get(constraint.target_id)
            
            if not source or not target:
                continue
            
            n_constraints += 1
            source_cred = source.credence.value
            target_cred = target.credence.value
            
            if constraint.constraint_type == ConstraintType.SUPPORTS:
                # Coherent if both high or both low
                agreement = 1 - abs(source_cred - target_cred)
                local_coherence = agreement * constraint.strength
                
            elif constraint.constraint_type == ConstraintType.CONTRADICTS:
                # Coherent if one high and one low
                disagreement = abs(source_cred - target_cred)
                local_coherence = disagreement * constraint.strength
                
                # Tension if both are high credence
                if source_cred > 0.6 and target_cred > 0.6:
                    tensions.append({
                        'source': constraint.source_id,
                        'target': constraint.target_id,
                        'source_credence': source_cred,
                        'target_credence': target_cred,
                        'type': 'contradiction_tension'
                    })
                    
            elif constraint.constraint_type in [ConstraintType.EXPLAINS, ConstraintType.INSTANTIATES]:
                # Explanatory coherence
                local_coherence = (source_cred * target_cred) * constraint.strength

            elif constraint.constraint_type == ConstraintType.BRIDGES:
                # Sprint 3: Bridge constraints - coherent if both connected beliefs align
                agreement = 1 - abs(source_cred - target_cred)
                local_coherence = agreement * constraint.strength * 0.8  # Slightly less than direct support

            elif constraint.constraint_type == ConstraintType.STRONG_TENSION:
                # Sprint 3: Strong tension from failed bridges
                # Similar to contradicts but with higher penalty
                disagreement = abs(source_cred - target_cred)
                local_coherence = disagreement * constraint.strength * 0.5  # Penalty for unresolved tension

                # Strong tension if both are high credence (failed bridge with strong beliefs)
                if source_cred > 0.5 and target_cred > 0.5:
                    tensions.append({
                        'source': constraint.source_id,
                        'target': constraint.target_id,
                        'source_credence': source_cred,
                        'target_credence': target_cred,
                        'type': 'bridge_failure_tension'
                    })

            else:
                local_coherence = 0.5 * constraint.strength
            
            total_coherence += local_coherence
        
        self._coherence_score = total_coherence / n_constraints if n_constraints > 0 else 0.5
        self._tensions = tensions
    
    def seek_equilibrium(self, max_iterations: int = 10) -> Dict[str, Any]:
        """
        Iteratively adjust beliefs to improve coherence.
        
        This implements a simplified reflective equilibrium: beliefs that
        are in tension with many others get their credence adjusted.
        
        Returns:
            Summary of adjustments made
        """
        adjustments = []
        
        for iteration in range(max_iterations):
            self._update_coherence()
            
            if not self._tensions:
                break
            
            # For each tension, adjust the less entrenched belief
            for tension in self._tensions[:3]:  # Limit per iteration
                source = self.beliefs[tension['source']]
                target = self.beliefs[tension['target']]
                
                # Adjust the less entrenched one (V23: emergent entrenchment)
                source_entrenchment = self.get_entrenchment(source.belief_id)
                target_entrenchment = self.get_entrenchment(target.belief_id)
                if source_entrenchment < target_entrenchment:
                    to_adjust = source
                    reason = f"in contradiction with more entrenched {target.belief_id}"
                else:
                    to_adjust = target
                    reason = f"in contradiction with more entrenched {source.belief_id}"
                
                old_cred = to_adjust.credence.value
                
                # Reduce credence
                to_adjust.credence = Credence(
                    value=to_adjust.credence.value * 0.85,
                    uncertainty=min(0.5, to_adjust.credence.uncertainty * 1.1),
                    n_supporting=to_adjust.credence.n_supporting,
                    n_contradicting=to_adjust.credence.n_contradicting + 1,
                    n_observations=to_adjust.credence.n_observations
                )
                
                # Mark as anomalous if credence drops low
                if to_adjust.credence.value < 0.3:
                    to_adjust.status = BeliefStatus.ANOMALOUS
                
                adjustments.append({
                    'belief_id': to_adjust.belief_id,
                    'old_credence': old_cred,
                    'new_credence': to_adjust.credence.value,
                    'reason': reason,
                    'iteration': iteration
                })
        
        self._update_coherence()
        
        return {
            'iterations': iteration + 1,
            'final_coherence': self._coherence_score,
            'remaining_tensions': len(self._tensions),
            'adjustments': adjustments
        }
    
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
        if belief_id not in self.beliefs:
            return 0.0

        # Count constraints where this belief is source or target
        constraint_count = 0
        for constraint in self.constraints.values():
            if constraint.source_id == belief_id or constraint.target_id == belief_id:
                constraint_count += 1

        if not self.constraints:
            return 0.0

        # Normalize by max possible connections (all other beliefs)
        max_connections = len(self.beliefs) - 1
        if max_connections <= 0:
            return 0.0

        # Centrality is proportion of possible connections realized
        # Cap at 1.0 in case there are multiple constraints to same belief
        centrality = min(1.0, constraint_count / max_connections)
        return centrality

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
        if belief_id not in self.beliefs:
            return 0.0

        belief = self.beliefs[belief_id]
        original_credence = belief.credence.value
        original_coherence = self._coherence_score

        # Perturb up (if possible) or down
        if original_credence + delta <= 1.0:
            test_credence = original_credence + delta
        else:
            test_credence = original_credence - delta

        # Temporarily change credence
        belief.credence = Credence(
            value=test_credence,
            uncertainty=belief.credence.uncertainty,
            n_supporting=belief.credence.n_supporting,
            n_contradicting=belief.credence.n_contradicting,
            n_observations=belief.credence.n_observations
        )

        # Recompute coherence
        self._update_coherence()
        new_coherence = self._coherence_score

        # Restore original credence
        belief.credence = Credence(
            value=original_credence,
            uncertainty=belief.credence.uncertainty,
            n_supporting=belief.credence.n_supporting,
            n_contradicting=belief.credence.n_contradicting,
            n_observations=belief.credence.n_observations
        )

        # Restore original coherence
        self._update_coherence()

        # Sensitivity is absolute change in coherence per unit delta
        # Normalize to [0, 1] range (max coherence change is 1.0)
        sensitivity = abs(new_coherence - original_coherence) / delta
        return min(1.0, sensitivity)

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
        centrality = self.belief_centrality(belief_id)
        sensitivity = self.belief_sensitivity(belief_id)

        sensitivity_weight = 1.0 - centrality_weight
        value = centrality_weight * centrality + sensitivity_weight * sensitivity
        return value

    def beliefs_by_value(self, top_n: Optional[int] = None) -> List[Tuple[str, float, float, float]]:
        """
        Rank all beliefs by their epistemic value.

        Sprint 1.6.3: Returns beliefs sorted by value (descending).

        Args:
            top_n: Return only top N beliefs (None for all)

        Returns:
            List of (belief_id, value, centrality, sensitivity) tuples.
        """
        results = []
        for belief_id in self.beliefs:
            centrality = self.belief_centrality(belief_id)
            sensitivity = self.belief_sensitivity(belief_id)
            value = 0.5 * centrality + 0.5 * sensitivity
            results.append((belief_id, value, centrality, sensitivity))

        # Sort by value descending
        results.sort(key=lambda x: x[1], reverse=True)

        if top_n is not None:
            return results[:top_n]
        return results

    def high_value_beliefs(self, threshold: float = 0.5) -> List[Dict[str, Any]]:
        """
        Get beliefs above a value threshold with details.

        Sprint 1.6.3: Convenience method for identifying investigation targets.

        Args:
            threshold: Minimum value to include (default 0.5)

        Returns:
            List of dicts with belief details and value metrics.
        """
        results = []
        for belief_id, value, centrality, sensitivity in self.beliefs_by_value():
            if value < threshold:
                break  # Already sorted, no more above threshold

            belief = self.beliefs[belief_id]
            results.append({
                'belief_id': belief_id,
                'content': belief.content,
                'level': belief.level.value,
                'credence': belief.credence.value,
                'entrenchment': belief.entrenchment,
                'value': value,
                'centrality': centrality,
                'sensitivity': sensitivity,
                'inference_type': belief.inference_type.value,
                'belief_kind': belief.belief_kind.value
            })

        return results

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
        self._update_coherence()  # Ensure tensions are current
        suggestions = []

        for tension in self._tensions[:max_suggestions]:
            source = self.beliefs.get(tension['source'])
            target = self.beliefs.get(tension['target'])

            if not source or not target:
                continue

            suggestion = self._generate_experiment_suggestion(source, target, tension)
            if suggestion:
                suggestions.append(suggestion)

        # Also suggest experiments for high-value contested beliefs
        contested = [b for b in self.beliefs.values() if b.contested]
        for belief in contested[:max_suggestions - len(suggestions)]:
            if len(suggestions) >= max_suggestions:
                break
            suggestion = self._generate_contested_experiment(belief)
            if suggestion:
                suggestions.append(suggestion)

        return suggestions

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
        # Determine experiment type based on belief levels
        exp_type = self._infer_experiment_type(source, target)

        # Identify what would need to be tested
        if source.level == EpistemicLevel.THEORETICAL and target.level == EpistemicLevel.EMPIRICAL:
            # Theory-data conflict: need to test the theoretical prediction
            test_focus = "theoretical_prediction"
            hypothesis = f"Test whether {source.content} correctly predicts {target.content}"
        elif source.level == target.level == EpistemicLevel.EMPIRICAL:
            # Conflicting empirical findings: need replication
            test_focus = "replication"
            hypothesis = f"Replicate to determine whether {source.content} or {target.content} holds"
        elif source.level == EpistemicLevel.INTERMEDIATE:
            # Mechanism conflict: need mechanism test
            test_focus = "mechanism"
            hypothesis = f"Test the mechanism: does {source.content} explain {target.content}?"
        else:
            test_focus = "general"
            hypothesis = f"Investigate conflict between {source.belief_id} and {target.belief_id}"

        # Estimate priority based on belief values
        priority = max(
            self.belief_value(source.belief_id),
            self.belief_value(target.belief_id)
        )

        # Generate scope suggestions
        scope_suggestion = self._suggest_scope(source, target)

        return {
            'experiment_id': f"exp:tension:{source.belief_id}:{target.belief_id}",
            'type': exp_type,
            'tension_type': tension.get('type', 'unknown'),
            'test_focus': test_focus,
            'hypothesis': hypothesis,
            'source_belief': {
                'id': source.belief_id,
                'content': source.content,
                'credence': source.credence.value,
                'level': source.level.value
            },
            'target_belief': {
                'id': target.belief_id,
                'content': target.content,
                'credence': target.credence.value,
                'level': target.level.value
            },
            'priority': priority,
            'scope_suggestion': scope_suggestion,
            'expected_resolution': self._estimate_resolution(source, target)
        }

    def _generate_contested_experiment(self, belief: Belief) -> Optional[Dict[str, Any]]:
        """
        Generate experiment suggestion for a contested belief.

        Sprint 1.6.4: Contested beliefs (oscillating credence) indicate
        genuine disagreement that experimentation could resolve.
        """
        credence_range = belief.credence_range()

        return {
            'experiment_id': f"exp:contested:{belief.belief_id}",
            'type': 'replication_study',
            'tension_type': 'credence_oscillation',
            'test_focus': 'replication',
            'hypothesis': f"Determine stable credence for: {belief.content}",
            'source_belief': {
                'id': belief.belief_id,
                'content': belief.content,
                'credence': belief.credence.value,
                'credence_range': credence_range,
                'level': belief.level.value
            },
            'target_belief': None,  # No target for contested belief
            'priority': self.belief_value(belief.belief_id),
            'scope_suggestion': self._suggest_contested_scope(belief),
            'expected_resolution': {
                'if_confirmed': f"Credence stabilizes above {credence_range[1]:.2f}",
                'if_refuted': f"Credence stabilizes below {credence_range[0]:.2f}",
                'uncertainty_reduction': abs(credence_range[1] - credence_range[0])
            }
        }

    def _infer_experiment_type(self, source: Belief, target: Belief) -> str:
        """Infer what type of experiment would address the tension."""
        levels = {source.level, target.level}

        if EpistemicLevel.OBSERVATIONAL in levels:
            return 'measurement_study'
        elif EpistemicLevel.THEORETICAL in levels and EpistemicLevel.EMPIRICAL in levels:
            return 'hypothesis_test'
        elif levels == {EpistemicLevel.EMPIRICAL}:
            return 'replication_study'
        elif EpistemicLevel.INTERMEDIATE in levels:
            return 'mechanism_study'
        else:
            return 'exploratory_study'

    def _suggest_scope(self, source: Belief, target: Belief) -> Dict[str, Any]:
        """Suggest scope conditions for the experiment."""
        # Combine scope conditions from both beliefs
        scopes = [source.scope, target.scope]
        scopes = [s for s in scopes if s is not None]

        if not scopes:
            return {
                'population': 'unspecified',
                'setting': 'unspecified',
                'note': 'Neither belief specifies scope - consider multiple settings'
            }

        # Find common scope elements
        populations = [s.population for s in scopes if s.population]
        settings = [s.setting for s in scopes if s.setting]

        return {
            'population': populations[0] if populations else 'unspecified',
            'setting': settings[0] if settings else 'unspecified',
            'should_vary': self._identify_scope_differences(scopes),
            'note': 'Test under conditions specified by both beliefs'
        }

    def _suggest_contested_scope(self, belief: Belief) -> Dict[str, Any]:
        """Suggest scope for contested belief experiment."""
        if belief.scope:
            return {
                'population': belief.scope.population or 'unspecified',
                'setting': belief.scope.setting or 'unspecified',
                'note': 'Replicate across multiple contexts to test generalizability'
            }
        return {
            'population': 'unspecified',
            'setting': 'unspecified',
            'note': 'Scope not specified - systematic replication recommended'
        }

    def _identify_scope_differences(self, scopes: List[ScopeConditions]) -> List[str]:
        """Identify where scope conditions differ between beliefs."""
        differences = []
        if len(scopes) < 2:
            return differences

        s1, s2 = scopes[0], scopes[1]
        if s1.population != s2.population:
            differences.append('population')
        if s1.setting != s2.setting:
            differences.append('setting')
        if s1.duration != s2.duration:
            differences.append('duration')
        if s1.measurement != s2.measurement:
            differences.append('measurement')

        return differences

    def _estimate_resolution(self, source: Belief, target: Belief) -> Dict[str, Any]:
        """Estimate how the tension might be resolved."""
        return {
            'if_source_confirmed': f"{source.belief_id} credence increases, {target.belief_id} decreases",
            'if_target_confirmed': f"{target.belief_id} credence increases, {source.belief_id} decreases",
            'if_scope_boundary': "Both may be correct in different contexts",
            'entrenchment_impact': {
                'source': source.entrenchment,
                'target': target.entrenchment,
                'easier_to_revise': source.belief_id if source.entrenchment < target.entrenchment else target.belief_id
            }
        }

    def get_research_priorities(self, top_n: int = 10) -> Dict[str, Any]:
        """
        Get research priorities combining tensions, high-value beliefs, and experiments.

        Sprint 1.6.4: Comprehensive research agenda based on web state.

        Returns:
            Dictionary with prioritized research directions.
        """
        self._update_coherence()

        return {
            'web_coherence': self._coherence_score,
            'n_tensions': len(self._tensions),
            'n_contested': sum(1 for b in self.beliefs.values() if b.contested),
            'suggested_experiments': self.suggest_experiments(max_suggestions=top_n),
            'high_value_beliefs': self.high_value_beliefs(threshold=0.3)[:top_n],
            'research_directions': self._generate_research_directions()
        }

    def _generate_research_directions(self) -> List[Dict[str, str]]:
        """Generate high-level research direction recommendations."""
        directions = []

        # Based on tension types
        tension_types = defaultdict(int)
        for t in self._tensions:
            tension_types[t.get('type', 'unknown')] += 1

        if tension_types['contradiction_tension'] > 0:
            directions.append({
                'direction': 'Resolve contradictory findings',
                'rationale': f"{tension_types['contradiction_tension']} pairs of high-credence beliefs contradict each other",
                'approach': 'Systematic replication with scope variation'
            })

        if tension_types['bridge_failure_tension'] > 0:
            directions.append({
                'direction': 'Strengthen knowledge transfer',
                'rationale': f"{tension_types['bridge_failure_tension']} bridge relationships have failed",
                'approach': 'Test enabling conditions for knowledge transfer'
            })

        # Based on belief distribution
        levels = defaultdict(int)
        for b in self.beliefs.values():
            levels[b.level] += 1

        if levels[EpistemicLevel.THEORETICAL] > levels[EpistemicLevel.EMPIRICAL]:
            directions.append({
                'direction': 'More empirical testing needed',
                'rationale': 'More theoretical than empirical beliefs',
                'approach': 'Design experiments to test theoretical predictions'
            })

        if levels[EpistemicLevel.OBSERVATIONAL] == 0:
            directions.append({
                'direction': 'Add observational grounding',
                'rationale': 'No observational-level beliefs',
                'approach': 'Conduct direct measurement studies'
            })

        return directions

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
        updates = {
            'belief_updates': [],
            'theory_world_updates': {},
            'temporal_updates': [],
            'coherence_before': self._coherence_score,
            'coherence_after': 0.0
        }
        
        supports_beliefs = supports_beliefs or {}
        contradicts_beliefs = contradicts_beliefs or {}
        theory_relevance = theory_relevance or {}
        observed_temporal = observed_temporal or {}
        
        # Create or update the evidence belief
        if belief_id in self.beliefs:
            evidence_belief = self.beliefs[belief_id]
            evidence_belief.paper_ids.append(paper_id)
            # Increase credence with replication
            evidence_belief.credence = evidence_belief.credence.update(
                True, 0.6, 0.7
            )
        else:
            evidence_belief = Belief(
                belief_id=belief_id,
                content=content,
                level=EpistemicLevel.EMPIRICAL,
                status=BeliefStatus.STUB if not (supports_beliefs or contradicts_beliefs) else BeliefStatus.TENTATIVE,
                credence=Credence(credence, 0.35),
                paper_ids=[paper_id]
            )
            self.add_belief(evidence_belief)
        
        # Update supported beliefs
        for target_id, strength in supports_beliefs.items():
            if target_id not in self.beliefs:
                continue
            
            target = self.beliefs[target_id]
            old_cred = target.credence.value
            target.credence = target.credence.update(True, strength, evidence_belief.credence.value)
            
            updates['belief_updates'].append({
                'belief_id': target_id,
                'direction': 'supported',
                'old_credence': old_cred,
                'new_credence': target.credence.value
            })
            
            # Add supporting constraint
            self.add_constraint(Constraint(
                constraint_id=f"c:{belief_id}:{target_id}",
                source_id=belief_id,
                target_id=target_id,
                constraint_type=ConstraintType.SUPPORTS,
                strength=strength
            ))
            
            # If target has a theory, mark evidence as relevant
            if target.theory_id and target.theory_id not in theory_relevance:
                theory_relevance[target.theory_id] = 0.5 + 0.3 * strength
        
        # Update contradicted beliefs
        for target_id, strength in contradicts_beliefs.items():
            if target_id not in self.beliefs:
                continue
            
            target = self.beliefs[target_id]
            old_cred = target.credence.value
            target.credence = target.credence.update(False, strength, evidence_belief.credence.value)
            
            updates['belief_updates'].append({
                'belief_id': target_id,
                'direction': 'contradicted',
                'old_credence': old_cred,
                'new_credence': target.credence.value
            })
            
            # Add contradicting constraint
            self.add_constraint(Constraint(
                constraint_id=f"c:{belief_id}:{target_id}",
                source_id=belief_id,
                target_id=target_id,
                constraint_type=ConstraintType.CONTRADICTS,
                strength=strength
            ))
            
            # Update theory relevance (evidence against)
            if target.theory_id and target.theory_id not in theory_relevance:
                theory_relevance[target.theory_id] = 0.5 - 0.3 * strength
        
        # Update theory worlds
        if theory_relevance:
            old_marginals = {tid: self.marginal_theory_probability(tid) for tid in self.theory_ids}
            self.update_theory_worlds(belief_id, theory_relevance)
            new_marginals = {tid: self.marginal_theory_probability(tid) for tid in self.theory_ids}
            
            updates['theory_world_updates'] = {
                tid: {'old': old_marginals.get(tid, 0.5), 'new': new_marginals.get(tid, 0.5)}
                for tid in self.theory_ids
            }
        
        # Update temporal parameters
        for param_name, (value, se) in observed_temporal.items():
            # Find beliefs with this temporal parameter
            for belief in self.beliefs.values():
                if belief.temporal_params and param_name in belief.temporal_params:
                    old_est = belief.temporal_params[param_name].estimate
                    belief.temporal_params[param_name] = belief.temporal_params[param_name].update(
                        value, se, weight=evidence_belief.credence.value, moderator_key=moderator
                    )
                    updates['temporal_updates'].append({
                        'belief_id': belief.belief_id,
                        'parameter': param_name,
                        'old_estimate': old_est,
                        'new_estimate': belief.temporal_params[param_name].estimate,
                        'moderator': moderator
                    })
        
        # Update coherence
        self._update_coherence()
        updates['coherence_after'] = self._coherence_score
        
        self.version += 1
        self.last_updated = datetime.now(timezone.utc)
        
        return updates
    
    # =========================================================================
    # QUERIES
    # =========================================================================
    
    def get_stubs(self) -> List[Belief]:
        """Get all unintegrated findings."""
        return [self.beliefs[bid] for bid in self._stubs if bid in self.beliefs]
    
    def get_anomalies(self) -> List[Belief]:
        """Get beliefs marked as anomalous."""
        return [b for b in self.beliefs.values() if b.status == BeliefStatus.ANOMALOUS]
    
    def get_beliefs_by_level(self, level: EpistemicLevel) -> List[Belief]:
        """Get all beliefs at a given epistemic level."""
        return [
            self.beliefs[bid]
            for bid in self._beliefs_by_level.get(level, [])
            if bid in self.beliefs
        ]
    
    def get_beliefs_for_theory(self, theory_id: str) -> List[Belief]:
        """Get all beliefs associated with a theory."""
        return [
            self.beliefs[bid]
            for bid in self._beliefs_by_theory.get(theory_id, [])
            if bid in self.beliefs
        ]
    
    # =========================================================================
    # REPORTING
    # =========================================================================
    
    def summary(self) -> str:
        """Generate a human-readable summary."""
        lines = [
            "# Web of Belief Summary",
            f"Domain: {self.domain}",
            f"Version: {self.version}",
            f"Coherence: {self._coherence_score:.3f}",
            f"Tensions: {len(self._tensions)}",
            "",
            "## Beliefs by Level",
        ]
        
        for level in EpistemicLevel:
            beliefs = self.get_beliefs_by_level(level)
            lines.append(f"\n### {level.value.title()} ({len(beliefs)})")
            for b in sorted(beliefs, key=lambda x: x.credence.value, reverse=True)[:5]:
                lines.append(
                    f"  - [{b.credence.value:.2f}] {b.content[:60]}..."
                    if len(b.content) > 60 else f"  - [{b.credence.value:.2f}] {b.content}"
                )
        
        if self._stubs:
            lines.append(f"\n## Stubs (Unintegrated Findings): {len(self._stubs)}")
            for stub_id in list(self._stubs)[:5]:
                stub = self.beliefs[stub_id]
                lines.append(f"  - {stub.content[:60]}...")
        
        if self.theory_worlds:
            lines.append("\n## Theory Probabilities")
            for theory_id in sorted(self.theory_ids):
                p = self.marginal_theory_probability(theory_id)
                lines.append(f"  - P({theory_id}) = {p:.3f}")
            
            lines.append("\n## Joint Distribution (top 5 worlds)")
            sorted_worlds = sorted(
                self.theory_worlds.values(),
                key=lambda w: w.posterior,
                reverse=True
            )[:5]
            for world in sorted_worlds:
                lines.append(f"  - {world.world_id}: P={world.posterior:.3f}")
        
        if self._tensions:
            lines.append("\n## Tensions")
            for t in self._tensions[:5]:
                lines.append(f"  - {t['source']} vs {t['target']}")
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'domain': self.domain,
            'version': self.version,
            'n_beliefs': len(self.beliefs),
            'n_constraints': len(self.constraints),
            'n_stubs': len(self._stubs),
            'coherence': self._coherence_score,
            'n_tensions': len(self._tensions),
            'theory_marginals': {
                tid: self.marginal_theory_probability(tid)
                for tid in self.theory_ids
            }
        }

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
        return WebOfBeliefSnapshot(
            domain=self.domain,
            version=self.version,
            beliefs=copy.deepcopy(self.beliefs),
            constraints=copy.deepcopy(self.constraints),
            coherence_score=self._coherence_score,
            tensions=copy.deepcopy(self._tensions),
            theory_ids=copy.deepcopy(self.theory_ids),
            stubs=copy.deepcopy(self._stubs),
            snapshot_at=datetime.now(timezone.utc)
        )


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
        return [b for b in self.beliefs.values() if b.level == level]

    def get_stubs(self) -> List[Belief]:
        """Get all unintegrated findings."""
        return [self.beliefs[bid] for bid in self.stubs if bid in self.beliefs]

    def get_anomalies(self) -> List[Belief]:
        """Get beliefs marked as anomalous."""
        return [b for b in self.beliefs.values() if b.status == BeliefStatus.ANOMALOUS]

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
