"""
Epistemic Orchestrator (ARCH-4 Integration).

Integrates the P2-P6 services with WebOfBelief to provide
full formal epistemic calculus capabilities.

This orchestrator ties together:
- WebOfBelief (existing Quinean web)
- RankingService (P2: Spohn)
- WarrantService (P3: Pollock)
- GroundingService (P4: Haack)
- GraphConfidenceService (P5: Pearl)

Usage:
    >>> from services.epistemic_orchestrator import EpistemicOrchestrator
    >>> orchestrator = EpistemicOrchestrator(web)
    >>> state = orchestrator.compute_full_state()
    >>> print(state.warranted_beliefs)
    >>> print(state.invariant_violations)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Any, Tuple, TYPE_CHECKING
from datetime import datetime, timezone
import logging

if TYPE_CHECKING:
    from src.services.web_of_belief import WebOfBelief

from src.services.ranking_service import (
    RankingService,
    RankPair,
    RankingResult
)
from src.services.warrant_service import (
    WarrantService,
    WarrantStatus,
    DefeatRelation,
    WarrantResult,
    DefeatType
)
from src.services.grounding_service import (
    GroundingService,
    GroundingResult,
    ExperientialClaim,
    JustificationStatus
)
from src.services.graph_confidence_service import (
    GraphConfidenceService,
    GraphConfidenceResult,
    IdentifiabilityStatus
)

logger = logging.getLogger(__name__)


@dataclass
class EpistemicState:
    """
    Complete epistemic state computed from WebOfBelief.

    Combines outputs from all P2-P6 services.
    """
    # From P2: Ranking
    ranks: Dict[str, RankPair]
    ranking_result: RankingResult

    # From P3: Warrant
    warranted_beliefs: Set[str]
    defeated_beliefs: Set[str]
    suspended_beliefs: Set[str]
    warrant_result: WarrantResult

    # From P4: Grounding
    grounded_beliefs: Set[str]
    ungrounded_beliefs: Set[str]
    grounding_result: GroundingResult

    # From P5: Graph Confidence
    graph_confidence_result: GraphConfidenceResult

    # Combined
    invariant_violations: List[str]
    computed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def is_consistent(self) -> bool:
        """Check if state has no invariant violations."""
        return len(self.invariant_violations) == 0

    @property
    def summary(self) -> Dict[str, Any]:
        """Summary statistics."""
        return {
            "total_beliefs": len(self.ranks),
            "warranted": len(self.warranted_beliefs),
            "defeated": len(self.defeated_beliefs),
            "grounded": len(self.grounded_beliefs),
            "ungrounded": len(self.ungrounded_beliefs),
            "violations": len(self.invariant_violations),
            "is_consistent": self.is_consistent
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ranks": {k: v.to_dict() for k, v in self.ranks.items()},
            "warranted_beliefs": list(self.warranted_beliefs),
            "defeated_beliefs": list(self.defeated_beliefs),
            "grounded_beliefs": list(self.grounded_beliefs),
            "invariant_violations": self.invariant_violations,
            "summary": self.summary,
            "computed_at": self.computed_at.isoformat()
        }


class EpistemicOrchestrator:
    """
    Orchestrates P2-P6 epistemic services with WebOfBelief.

    Provides a unified interface for computing and maintaining
    formal epistemic state according to the panel-approved architecture.

    Usage:
        >>> orchestrator = EpistemicOrchestrator(web)
        >>> state = orchestrator.compute_full_state()
        >>>
        >>> # Check invariants
        >>> if not state.is_consistent:
        ...     for v in state.invariant_violations:
        ...         print(f"Violation: {v}")
        >>>
        >>> # Get edge confidence for causal inference
        >>> conf = state.graph_confidence_result.edge_confidences
    """

    def __init__(
        self,
        web: "WebOfBelief",
        ranking_service: Optional[RankingService] = None,
        warrant_service: Optional[WarrantService] = None,
        grounding_service: Optional[GroundingService] = None,
        graph_confidence_service: Optional[GraphConfidenceService] = None
    ):
        """
        Initialize orchestrator with WebOfBelief and services.

        Args:
            web: WebOfBelief instance
            ranking_service: Optional custom RankingService
            warrant_service: Optional custom WarrantService
            grounding_service: Optional custom GroundingService
            graph_confidence_service: Optional custom GraphConfidenceService
        """
        self.web = web
        self.ranking_service = ranking_service or RankingService()
        self.warrant_service = warrant_service or WarrantService()
        self.grounding_service = grounding_service or GroundingService()
        self.graph_confidence_service = graph_confidence_service or GraphConfidenceService()

        # Cache
        self._cached_state: Optional[EpistemicState] = None
        self._cache_valid: bool = False

    def invalidate_cache(self):
        """Invalidate cached state (call after web changes)."""
        self._cache_valid = False
        self._cached_state = None

    def compute_full_state(
        self,
        defeat_relations: Optional[List[DefeatRelation]] = None,
        experiential_claims: Optional[Dict[str, List[ExperientialClaim]]] = None,
        force_recompute: bool = False
    ) -> EpistemicState:
        """
        Compute full epistemic state from WebOfBelief.

        This runs all P2-P6 services in sequence:
        1. P2: Compute ranks from credences
        2. P3: Compute warrant status with defeat
        3. P4: Compute grounding with experiential basis
        4. P5: Compute graph confidence for causal bridge

        Args:
            defeat_relations: Explicit defeat relations (auto-extracted if None)
            experiential_claims: Experiential claims per belief
            force_recompute: Force recomputation even if cached

        Returns:
            EpistemicState with all computed values
        """
        if self._cache_valid and not force_recompute and self._cached_state:
            return self._cached_state

        logger.debug(f"Computing full epistemic state for {len(self.web.beliefs)} beliefs")

        # Extract defeat relations from constraints if not provided
        if defeat_relations is None:
            defeat_relations = self._extract_defeat_relations()

        # Identify observational beliefs
        observational = self._identify_observational()

        # P2: Compute ranks
        ranking_result = self.ranking_service.compute_ranks(
            self.web,
            warranted_beliefs=set(),  # First pass without warrant info
            defeat_relations=[(d.defeater_id, d.defeated_id) for d in defeat_relations]
        )

        # P3: Compute warrant
        warrant_result = self.warrant_service.compute_warrant(
            self.web,
            ranking_result.ranks,
            defeat_relations,
            observational_beliefs=observational
        )

        # P2 again: Recompute ranks with warrant info (tiered computation)
        ranking_result = self.ranking_service.compute_ranks(
            self.web,
            warranted_beliefs=warrant_result.warranted,
            defeat_relations=[(d.defeater_id, d.defeated_id) for d in defeat_relations]
        )

        # P4: Compute grounding
        grounding_result = self.grounding_service.compute_grounding(
            self.web,
            warranted_beliefs=warrant_result.warranted,
            experiential_claims=experiential_claims
        )

        # P5: Compute graph confidence
        graph_confidence_result = self.graph_confidence_service.compute_confidence(
            self.web,
            ranking_result.ranks,
            warrant_result.warranted,
            grounding_result.scores
        )

        # Collect all violations
        all_violations = []
        all_violations.extend(ranking_result.violations)
        all_violations.extend(warrant_result.violations)
        all_violations.extend(grounding_result.violations)
        all_violations.extend(graph_confidence_result.violations)

        state = EpistemicState(
            ranks=ranking_result.ranks,
            ranking_result=ranking_result,
            warranted_beliefs=warrant_result.warranted,
            defeated_beliefs=warrant_result.defeated,
            suspended_beliefs=warrant_result.suspended,
            warrant_result=warrant_result,
            grounded_beliefs=grounding_result.grounded_beliefs,
            ungrounded_beliefs=grounding_result.ungrounded_beliefs,
            grounding_result=grounding_result,
            graph_confidence_result=graph_confidence_result,
            invariant_violations=all_violations
        )

        # Cache
        self._cached_state = state
        self._cache_valid = True

        logger.info(f"Epistemic state computed: {state.summary}")

        return state

    def _extract_defeat_relations(self) -> List[DefeatRelation]:
        """Extract defeat relations from web constraints."""
        relations = []

        for constraint in self.web.constraints.values():
            ctype = constraint.constraint_type.value if hasattr(constraint.constraint_type, 'value') else str(constraint.constraint_type)

            if ctype == "CONTRADICTS":
                # Mutual defeat (both rebut each other)
                relations.append(DefeatRelation(
                    defeater_id=constraint.source_id,
                    defeated_id=constraint.target_id,
                    defeat_type=DefeatType.REBUTTING
                ))
                relations.append(DefeatRelation(
                    defeater_id=constraint.target_id,
                    defeated_id=constraint.source_id,
                    defeat_type=DefeatType.REBUTTING
                ))

        return relations

    def _identify_observational(self) -> Set[str]:
        """Identify observational beliefs."""
        obs = set()
        for belief_id, belief in self.web.beliefs.items():
            level = getattr(belief, 'level', None)
            if level and hasattr(level, 'value') and level.value == "OBSERVATIONAL":
                obs.add(belief_id)
        return obs

    def get_belief_status(self, belief_id: str) -> Dict[str, Any]:
        """
        Get full epistemic status for a single belief.

        Args:
            belief_id: The belief to check

        Returns:
            Dict with rank, warrant, grounding, and justification info
        """
        state = self.compute_full_state()

        rank = state.ranks.get(belief_id)
        grounding_score = state.grounding_result.scores.get(belief_id)
        warrant_chain = state.warrant_result.chains.get(belief_id)

        return {
            "belief_id": belief_id,
            "rank": rank.to_dict() if rank else None,
            "warranted": belief_id in state.warranted_beliefs,
            "defeated": belief_id in state.defeated_beliefs,
            "grounded": belief_id in state.grounded_beliefs,
            "justification": grounding_score.to_dict() if grounding_score else None,
            "warrant_chain": warrant_chain.to_dict() if warrant_chain else None
        }

    def check_invariants(self) -> List[str]:
        """
        Check all formal invariants (INV-1 through INV-5).

        Returns:
            List of violation messages (empty if all pass)
        """
        state = self.compute_full_state()
        return state.invariant_violations

    def get_causal_edge_confidence(
        self,
        cause: str,
        effect: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get confidence for a causal edge.

        Args:
            cause: Cause variable/belief ID
            effect: Effect variable/belief ID

        Returns:
            Edge confidence info or None if edge not found
        """
        state = self.compute_full_state()
        edge = (cause, effect)

        ec = state.graph_confidence_result.edge_confidences.get(edge)
        if ec:
            return ec.to_dict()
        return None


# ============================================================
# CONVENIENCE FUNCTIONS
# ============================================================

def compute_epistemic_state(web: "WebOfBelief") -> EpistemicState:
    """
    Convenience function to compute epistemic state.

    Args:
        web: WebOfBelief instance

    Returns:
        EpistemicState with all P2-P6 computations
    """
    orchestrator = EpistemicOrchestrator(web)
    return orchestrator.compute_full_state()


def get_orchestrator(web: "WebOfBelief") -> EpistemicOrchestrator:
    """
    Convenience function to create orchestrator.

    Args:
        web: WebOfBelief instance

    Returns:
        EpistemicOrchestrator
    """
    return EpistemicOrchestrator(web)
