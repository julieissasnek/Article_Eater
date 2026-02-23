"""
Ranking Service (ARCH-4 Phase P2: Spohn Conditionalization).

Implements Spohn's ranking theory for epistemic state representation.
This is a stateless service that computes ranks from web state.

Key Concepts (per panel consultation 2026-02-12):
- κ(B) = rank of B = degree of DISBELIEF (not belief!)
- B is believed iff κ(¬B) > 0 (negation is disbelieved)
- B is disbelieved iff κ(B) > 0
- B is suspended iff κ(B) = κ(¬B) = 0

Conditionalization (Spohn 1988):
- κ_new(B) = κ_old(B|E) when E is learned with firmness n
- This allows non-monotonic belief revision

Panel Requirements:
- P2.1: Create stateless RankingService class
- P2.2: Base rank computation from evidence
- P2.3: Spohn conditionalization κ_new(B) = κ_old(B) + κ(¬E)
- P2.4: Defeat-adjusted ranks (integration with Pollock)
- P2.5: Property tests for rank coherence

References:
- Spohn, W. (1988). Ordinal Conditional Functions: A Dynamic Theory of Epistemic States.
- Spohn, W. (2012). The Laws of Belief: Ranking Theory and its Philosophical Applications.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple, Any, TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from src.services.web_of_belief import WebOfBelief

logger = logging.getLogger(__name__)


# Maximum rank value (κ = ∞ reserved for contradictions)
MAX_RANK = 100
DEFAULT_FIRMNESS = 1


@dataclass
class RankPair:
    """
    Spohn ranking pair for a belief.

    Semantics (per Spohn panel consultation):
    - rank (κ(B)): degree of DISBELIEF in B
    - neg_rank (κ(¬B)): degree of disbelief in negation

    A belief B is:
    - BELIEVED if neg_rank > rank (κ(¬B) > κ(B))
    - DISBELIEVED if rank > neg_rank (κ(B) > κ(¬B))
    - SUSPENDED if rank == neg_rank

    The FIRMNESS is |rank - neg_rank|, indicating strength of doxastic commitment.
    """
    rank: int = 0        # κ(B) - degree of disbelief in B
    neg_rank: int = 0    # κ(¬B) - degree of disbelief in ¬B

    def __post_init__(self):
        # Clamp to valid range
        self.rank = max(0, min(MAX_RANK, self.rank))
        self.neg_rank = max(0, min(MAX_RANK, self.neg_rank))

    @property
    def believed(self) -> bool:
        """B is believed iff κ(¬B) > κ(B)."""
        return self.neg_rank > self.rank

    @property
    def disbelieved(self) -> bool:
        """B is disbelieved iff κ(B) > κ(¬B)."""
        return self.rank > self.neg_rank

    @property
    def suspended(self) -> bool:
        """B is suspended iff κ(B) = κ(¬B)."""
        return self.rank == self.neg_rank

    @property
    def firmness(self) -> int:
        """Firmness = |κ(B) - κ(¬B)|, strength of doxastic commitment."""
        return abs(self.rank - self.neg_rank)

    @property
    def belief_direction(self) -> str:
        """Human-readable belief direction."""
        if self.believed:
            return "believed"
        elif self.disbelieved:
            return "disbelieved"
        else:
            return "suspended"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rank": self.rank,
            "neg_rank": self.neg_rank,
            "believed": self.believed,
            "disbelieved": self.disbelieved,
            "suspended": self.suspended,
            "firmness": self.firmness
        }


@dataclass
class RankingResult:
    """Result from ranking computation."""
    ranks: Dict[str, RankPair]
    base_ranks: Dict[str, RankPair]  # Before defeat adjustment
    defeat_adjustments: Dict[str, int]  # belief_id -> adjustment
    violations: List[str]  # INV-3 violations

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ranks": {k: v.to_dict() for k, v in self.ranks.items()},
            "defeat_adjustments": self.defeat_adjustments,
            "violations": self.violations
        }


class RankingService:
    """
    Stateless service for computing Spohn ranks.

    Per panel requirements:
    - Pure function: web state → ranks
    - Integrates evidence, defeat adjustments
    - Enforces INV-3 (RankCoherence): supports(A,B) ∧ warranted(A) → rank(B) ≤ rank(A) + δ
    - Enforces INV-4 (DefeatAsymmetry): defeats(D,B) → rank(D) < rank(B)

    Usage:
        >>> service = RankingService()
        >>> result = service.compute_ranks(web)
        >>> for belief_id, rank_pair in result.ranks.items():
        ...     print(f"{belief_id}: {rank_pair.belief_direction}")
    """

    def __init__(
        self,
        max_rank: int = MAX_RANK,
        default_firmness: int = DEFAULT_FIRMNESS,
        support_penalty: int = 1,  # δ in INV-3
        defeat_boost: int = 2      # How much defeat raises rank
    ):
        self.max_rank = max_rank
        self.default_firmness = default_firmness
        self.support_penalty = support_penalty
        self.defeat_boost = defeat_boost

    def compute_ranks(
        self,
        web: "WebOfBelief",
        warranted_beliefs: Optional[Set[str]] = None,
        defeat_relations: Optional[List[Tuple[str, str]]] = None
    ) -> RankingResult:
        """
        Compute ranks for all beliefs in the web.

        Args:
            web: WebOfBelief instance
            warranted_beliefs: Set of belief IDs that are currently warranted
            defeat_relations: List of (defeater_id, defeated_id) tuples

        Returns:
            RankingResult with computed ranks
        """
        # Phase 1: Base ranks from evidence/credence
        base_ranks = self._compute_base_ranks(web)

        # Phase 2: Defeat adjustments (Pollock integration)
        defeat_adjustments: Dict[str, int] = {}
        if defeat_relations:
            defeat_adjustments = self._compute_defeat_adjustments(
                base_ranks, defeat_relations
            )

        # Phase 3: Apply adjustments
        adjusted_ranks = self._apply_defeat_adjustments(base_ranks, defeat_adjustments)

        # Phase 4: Check and enforce INV-3 (RankCoherence)
        violations = self._check_rank_coherence(
            adjusted_ranks, web, warranted_beliefs or set()
        )

        return RankingResult(
            ranks=adjusted_ranks,
            base_ranks=base_ranks,
            defeat_adjustments=defeat_adjustments,
            violations=violations
        )

    def _compute_base_ranks(self, web: "WebOfBelief") -> Dict[str, RankPair]:
        """
        Compute base ranks from belief credence/evidence.

        Conversion from credence (0-1) to ranks:
        - credence > 0.5: believed, κ(B) = 0, κ(¬B) = firmness
        - credence < 0.5: disbelieved, κ(B) = firmness, κ(¬B) = 0
        - credence = 0.5: suspended, κ(B) = κ(¬B) = 0

        Firmness scales with distance from 0.5 and uncertainty.
        """
        ranks = {}

        for belief_id, belief in web.beliefs.items():
            # Get credence (probability-like value)
            credence = getattr(belief.credence, 'value', 0.5) if hasattr(belief, 'credence') else 0.5
            uncertainty = getattr(belief.credence, 'uncertainty', 0.2) if hasattr(belief, 'credence') else 0.2

            # Convert to ranks
            rank_pair = self.credence_to_ranks(credence, uncertainty)
            ranks[belief_id] = rank_pair

        return ranks

    def credence_to_ranks(
        self,
        credence: float,
        uncertainty: float = 0.2
    ) -> RankPair:
        """
        Convert credence (probability-like) to Spohn ranks.

        Args:
            credence: Value in [0, 1], where 0.5 = neutral
            uncertainty: Value in [0, 1], affects firmness

        Returns:
            RankPair with appropriate κ(B) and κ(¬B)

        Per Spohn panel consultation:
        - Higher credence → lower κ(B), higher κ(¬B)
        - Lower credence → higher κ(B), lower κ(¬B)
        - Credence 0.5 → both ranks 0 (suspended)
        """
        # Clamp inputs
        credence = max(0.0, min(1.0, credence))
        uncertainty = max(0.0, min(1.0, uncertainty))

        # Compute firmness from credence strength and certainty
        strength = abs(credence - 0.5) * 2  # 0 at 0.5, 1 at 0 or 1
        certainty = 1 - uncertainty
        firmness = int(round(strength * certainty * 10))  # Scale to 0-10
        firmness = max(0, min(self.max_rank, firmness))

        if credence > 0.5:
            # Believed: κ(B) = 0, κ(¬B) = firmness
            return RankPair(rank=0, neg_rank=firmness)
        elif credence < 0.5:
            # Disbelieved: κ(B) = firmness, κ(¬B) = 0
            return RankPair(rank=firmness, neg_rank=0)
        else:
            # Suspended: both 0
            return RankPair(rank=0, neg_rank=0)

    def ranks_to_credence(self, ranks: RankPair) -> Tuple[float, float]:
        """
        Convert Spohn ranks back to credence/uncertainty.

        Returns:
            Tuple of (credence, uncertainty)
        """
        firmness = ranks.firmness
        max_firmness = 10

        # Compute certainty from firmness
        certainty = min(1.0, firmness / max_firmness)
        uncertainty = 1 - certainty

        # Compute credence from direction and firmness
        if ranks.believed:
            credence = 0.5 + (certainty * 0.5)
        elif ranks.disbelieved:
            credence = 0.5 - (certainty * 0.5)
        else:
            credence = 0.5

        return credence, uncertainty

    def _compute_defeat_adjustments(
        self,
        base_ranks: Dict[str, RankPair],
        defeat_relations: List[Tuple[str, str]]
    ) -> Dict[str, int]:
        """
        Compute rank adjustments from defeat relations.

        Per Pollock integration:
        - If D defeats B, and D is believed (κ(D) = 0), raise κ(B)
        - The adjustment depends on defeat strength

        Enforces INV-4 (DefeatAsymmetry): defeats(D,B) → rank(D) < rank(B)
        """
        adjustments: Dict[str, int] = {}

        for defeater_id, defeated_id in defeat_relations:
            if defeater_id not in base_ranks or defeated_id not in base_ranks:
                continue

            defeater_ranks = base_ranks[defeater_id]
            defeated_ranks = base_ranks[defeated_id]

            # Only apply defeat if defeater is believed
            if defeater_ranks.believed:
                # INV-4: defeater rank must be lower than defeated rank (after adjustment)
                # So we boost defeated rank to ensure asymmetry
                current_adjustment = adjustments.get(defeated_id, 0)
                needed_adjustment = max(0, defeater_ranks.rank - defeated_ranks.rank + 1)
                adjustments[defeated_id] = max(current_adjustment, needed_adjustment + self.defeat_boost)

        return adjustments

    def _apply_defeat_adjustments(
        self,
        base_ranks: Dict[str, RankPair],
        adjustments: Dict[str, int]
    ) -> Dict[str, RankPair]:
        """Apply defeat adjustments to base ranks."""
        result = {}

        for belief_id, rank_pair in base_ranks.items():
            adjustment = adjustments.get(belief_id, 0)
            if adjustment > 0:
                # Raise κ(B) by adjustment amount
                new_rank = min(self.max_rank, rank_pair.rank + adjustment)
                result[belief_id] = RankPair(rank=new_rank, neg_rank=rank_pair.neg_rank)
            else:
                result[belief_id] = RankPair(rank=rank_pair.rank, neg_rank=rank_pair.neg_rank)

        return result

    def _check_rank_coherence(
        self,
        ranks: Dict[str, RankPair],
        web: "WebOfBelief",
        warranted_beliefs: Set[str]
    ) -> List[str]:
        """
        Check INV-3 (RankCoherence): supports(A,B) ∧ warranted(A) → rank(B) ≤ rank(A) + δ

        Returns list of violation messages.
        """
        violations = []

        for constraint in web.constraints.values():
            if constraint.constraint_type.value == "SUPPORTS":
                source_id = constraint.source_id
                target_id = constraint.target_id

                if source_id not in ranks or target_id not in ranks:
                    continue

                # Only check if source is warranted
                if source_id not in warranted_beliefs:
                    continue

                source_rank = ranks[source_id].rank
                target_rank = ranks[target_id].rank

                # INV-3: rank(target) ≤ rank(source) + δ
                max_allowed = source_rank + self.support_penalty
                if target_rank > max_allowed:
                    violations.append(
                        f"INV-3 violation: {source_id} supports {target_id}, "
                        f"but rank({target_id})={target_rank} > rank({source_id})+δ={max_allowed}"
                    )

        return violations

    def conditionalize(
        self,
        current_ranks: Dict[str, RankPair],
        evidence_id: str,
        evidence_supports: List[str],
        evidence_contradicts: List[str],
        firmness: int = DEFAULT_FIRMNESS
    ) -> Dict[str, RankPair]:
        """
        Spohn conditionalization on new evidence.

        When evidence E is learned with firmness n:
        - For beliefs B that E supports: decrease κ(B)
        - For beliefs B that E contradicts: increase κ(B)

        This is simplified from full conditionalization which requires
        the entire ranking function over all propositions.

        Args:
            current_ranks: Current rank assignments
            evidence_id: ID of the evidence belief
            evidence_supports: Belief IDs that evidence supports
            evidence_contradicts: Belief IDs that evidence contradicts
            firmness: Strength of the evidence (default 1)

        Returns:
            New rank assignments after conditionalization
        """
        new_ranks = {}

        for belief_id, rank_pair in current_ranks.items():
            if belief_id in evidence_supports:
                # Evidence supports this belief: decrease κ(B), increase κ(¬B)
                new_rank = max(0, rank_pair.rank - firmness)
                new_neg_rank = min(self.max_rank, rank_pair.neg_rank + firmness)
                new_ranks[belief_id] = RankPair(rank=new_rank, neg_rank=new_neg_rank)

            elif belief_id in evidence_contradicts:
                # Evidence contradicts this belief: increase κ(B), decrease κ(¬B)
                new_rank = min(self.max_rank, rank_pair.rank + firmness)
                new_neg_rank = max(0, rank_pair.neg_rank - firmness)
                new_ranks[belief_id] = RankPair(rank=new_rank, neg_rank=new_neg_rank)

            else:
                # Unaffected by evidence
                new_ranks[belief_id] = RankPair(rank=rank_pair.rank, neg_rank=rank_pair.neg_rank)

        return new_ranks


# ============================================================
# CONVENIENCE FUNCTIONS
# ============================================================

def compute_web_ranks(
    web: "WebOfBelief",
    warranted_beliefs: Optional[Set[str]] = None,
    defeat_relations: Optional[List[Tuple[str, str]]] = None
) -> RankingResult:
    """
    Convenience function to compute ranks for a web.

    Args:
        web: WebOfBelief instance
        warranted_beliefs: Set of warranted belief IDs
        defeat_relations: List of (defeater, defeated) tuples

    Returns:
        RankingResult with all computed ranks
    """
    service = RankingService()
    return service.compute_ranks(web, warranted_beliefs, defeat_relations)


def credence_to_ranks(credence: float, uncertainty: float = 0.2) -> RankPair:
    """
    Convenience function to convert credence to ranks.

    Args:
        credence: Value in [0, 1]
        uncertainty: Value in [0, 1]

    Returns:
        RankPair
    """
    service = RankingService()
    return service.credence_to_ranks(credence, uncertainty)
