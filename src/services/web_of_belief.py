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
        """Whether we have good evidence for this credence."""
        return self.n_observations >= 3 and self.uncertainty < 0.2
    
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
        
        # Uncertainty decreases with evidence (but never to zero)
        new_uncertainty = self.uncertainty * (0.95 ** (weight * 0.5))
        new_uncertainty = max(0.05, new_uncertainty)  # Floor
        
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
    credence: Credence = field(default_factory=lambda: Credence(0.5, 0.4))

    # Entrenchment: how costly is it to revise this belief?
    # Higher = more central to the web, more connections
    entrenchment: float = 0.5

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

    def is_stub(self) -> bool:
        return self.status == BeliefStatus.STUB

    def is_anomalous(self) -> bool:
        return self.status == BeliefStatus.ANOMALOUS

    def to_dict(self) -> Dict[str, Any]:
        result = {
            'belief_id': self.belief_id,
            'content': self.content,
            'level': self.level.value,
            'status': self.status.value,
            'credence': self.credence.to_dict(),
            'entrenchment': self.entrenchment,
            'theory_id': self.theory_id,
            'n_sources': len(self.paper_ids),
            'domain': self.domain,
            'paper_ids': self.paper_ids.copy(),
            'tags': self.tags.copy(),
            'environment_id': self.environment_id,
            'outcome_id': self.outcome_id,
            'evidence_cluster_id': self.evidence_cluster_id,
        }
        if self.scope:
            result['scope'] = self.scope.to_dict()
        return result

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'Belief':
        """Create Belief from dictionary."""
        scope = None
        if 'scope' in d and d['scope']:
            scope = ScopeConditions.from_dict(d['scope'])

        credence_data = d.get('credence', {})
        if isinstance(credence_data, dict):
            credence = Credence(
                value=credence_data.get('credence', credence_data.get('value', 0.5)),
                uncertainty=credence_data.get('uncertainty', 0.4),
                n_supporting=credence_data.get('n_supporting', 0),
                n_contradicting=credence_data.get('n_contradicting', 0),
                n_observations=credence_data.get('n_observations', 0)
            )
        else:
            credence = Credence(0.5, 0.4)

        return cls(
            belief_id=d.get('belief_id', ''),
            content=d.get('content', ''),
            level=EpistemicLevel(d.get('level', 'empirical')),
            status=BeliefStatus(d.get('status', 'stub')),
            credence=credence,
            entrenchment=d.get('entrenchment', 0.5),
            paper_ids=d.get('paper_ids', []),
            theory_id=d.get('theory_id'),
            domain=d.get('domain', ''),
            tags=d.get('tags', []),
            scope=scope,
            environment_id=d.get('environment_id'),
            outcome_id=d.get('outcome_id'),
            evidence_cluster_id=d.get('evidence_cluster_id')
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
            'evidence_ids': self.evidence_ids.copy()
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'Constraint':
        causal_dir = d.get('causal_direction', 'unknown')
        try:
            causal_direction = CausalDirection(causal_dir)
        except ValueError:
            causal_direction = CausalDirection.UNKNOWN

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
            mediator=d.get('mediator')
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
        
        # History
        self.version: int = 0
        self.created_at = datetime.now(timezone.utc)
        self.last_updated = datetime.now(timezone.utc)
    
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
        belief = Belief(
            belief_id=belief_id,
            content=content,
            level=level,
            status=BeliefStatus.STUB,
            credence=Credence(initial_credence, 0.4),
            entrenchment=0.2,  # Stubs are not entrenched
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
        belief.entrenchment = 0.4  # Increase slightly
        
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
                
                # Adjust the less entrenched one
                if source.entrenchment < target.entrenchment:
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
        entrenchment=0.8,
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
        entrenchment=0.75,
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
        entrenchment=0.7,
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
        entrenchment=0.6
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
        entrenchment=0.55
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
