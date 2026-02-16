"""
Warrant Service (ARCH-4 Phase P3: Pollock Defeasible Reasoning).

Implements Pollock's defeasible logic for epistemic warrant.
This is a stateless service that computes warrant status from web state.

Key Concepts (per panel consultation 2026-02-12):
- Warrant = Prima facie justification - Undefeated defeaters
- Rebutting defeat: Defeater directly contradicts conclusion
- Undercutting defeat: Defeater attacks inference/method, not conclusion
- Reinstatement: If defeater is itself defeated, original belief reinstated

Three-Level Defeat Structure (Pollock):
    A rebuts B
    C rebuts A
    → Therefore B is REINSTATED

This is non-monotonic reasoning: adding information can restore previous beliefs.

Panel Requirements:
- P3.1: Create stateless WarrantService class
- P3.2: Prima facie warrant (has supporters OR is observational)
- P3.3: Rebutting defeat
- P3.4: Undercutting defeat
- P3.5: Reinstatement (recursive)
- P3.6: INV-1 (Consistency): ¬(warranted(B) ∧ warranted(rebutter(B)))

References:
- Pollock, J.L. (1987). Defeasible Reasoning. Cognitive Science.
- Pollock, J.L. (1995). Cognitive Carpentry. MIT Press.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple, Any, TYPE_CHECKING
from enum import Enum
import logging

if TYPE_CHECKING:
    from src.services.web_of_belief import WebOfBelief

from src.services.ranking_service import RankPair

logger = logging.getLogger(__name__)


class WarrantStatus(str, Enum):
    """Status of epistemic warrant for a belief."""
    WARRANTED = "WARRANTED"           # Justified, undefeated
    DEFEATED = "DEFEATED"             # Has undefeated defeater
    SUSPENDED = "SUSPENDED"           # In defeat cycle (neither warranted nor defeated)
    UNGROUNDED = "UNGROUNDED"         # No chain to experience (Haack)
    UNCHECKED = "UNCHECKED"           # Not yet evaluated


class DefeatType(str, Enum):
    """Type of defeat relation."""
    REBUTTING = "REBUTTING"           # Attacks conclusion directly
    UNDERCUTTING = "UNDERCUTTING"     # Attacks inference/method
    BOTH = "BOTH"                     # Both types apply


@dataclass
class DefeatRelation:
    """A defeat relation between beliefs."""
    defeater_id: str
    defeated_id: str
    defeat_type: DefeatType
    attack_point: Optional[str] = None  # For undercutting: what inference attacked
    strength: float = 1.0               # Strength of defeat

    def to_dict(self) -> Dict[str, Any]:
        return {
            "defeater_id": self.defeater_id,
            "defeated_id": self.defeated_id,
            "defeat_type": self.defeat_type.value,
            "attack_point": self.attack_point,
            "strength": self.strength
        }


@dataclass
class DefeatChain:
    """Explanation of why a belief is/isn't warranted."""
    belief_id: str
    status: WarrantStatus
    defeaters: List[str]                # IDs of undefeated defeaters
    reinstaters: List[str]              # IDs of beliefs that reinstate this one
    cycle_members: List[str]            # If SUSPENDED: members of defeat cycle
    depth: int = 0                      # Depth of analysis

    def to_dict(self) -> Dict[str, Any]:
        return {
            "belief_id": self.belief_id,
            "status": self.status.value,
            "defeaters": self.defeaters,
            "reinstaters": self.reinstaters,
            "cycle_members": self.cycle_members,
            "depth": self.depth
        }


@dataclass
class WarrantResult:
    """Result from warrant computation."""
    warranted: Set[str]                 # IDs of warranted beliefs
    defeated: Set[str]                  # IDs of defeated beliefs
    suspended: Set[str]                 # IDs of beliefs in defeat cycles
    ungrounded: Set[str]                # IDs of ungrounded beliefs
    chains: Dict[str, DefeatChain]      # Explanation chains
    violations: List[str]               # INV-1 violations

    def to_dict(self) -> Dict[str, Any]:
        return {
            "warranted": list(self.warranted),
            "defeated": list(self.defeated),
            "suspended": list(self.suspended),
            "ungrounded": list(self.ungrounded),
            "chains": {k: v.to_dict() for k, v in self.chains.items()},
            "violations": self.violations
        }


class WarrantService:
    """
    Stateless service for computing warrant status.

    Per panel requirements:
    - Pure function: web state + ranks → warrant status
    - Recursive reinstatement logic
    - Enforces INV-1 (Consistency): ¬(warranted(B) ∧ warranted(rebutter(B)))

    Usage:
        >>> service = WarrantService()
        >>> result = service.compute_warrant(web, ranks)
        >>> for belief_id in result.warranted:
        ...     print(f"{belief_id} is warranted")
    """

    def __init__(
        self,
        max_depth: int = 10,          # Max recursion depth for reinstatement
        cycle_threshold: int = 3       # Consecutive visits to detect cycle
    ):
        self.max_depth = max_depth
        self.cycle_threshold = cycle_threshold

    def compute_warrant(
        self,
        web: "WebOfBelief",
        ranks: Dict[str, RankPair],
        defeat_relations: Optional[List[DefeatRelation]] = None,
        observational_beliefs: Optional[Set[str]] = None
    ) -> WarrantResult:
        """
        Compute warrant status for all beliefs in the web.

        Args:
            web: WebOfBelief instance
            ranks: Current rank assignments
            defeat_relations: List of DefeatRelation objects
            observational_beliefs: Set of belief IDs at observational level

        Returns:
            WarrantResult with warrant status for all beliefs
        """
        # Build defeat graph
        defeat_graph = self._build_defeat_graph(defeat_relations or [])

        # Build support graph
        support_graph = self._build_support_graph(web)

        # Identify observational beliefs (self-warranted)
        obs_beliefs = observational_beliefs or self._identify_observational(web)

        # Compute warrant status recursively
        warranted: Set[str] = set()
        defeated: Set[str] = set()
        suspended: Set[str] = set()
        ungrounded: Set[str] = set()
        chains: Dict[str, DefeatChain] = {}

        for belief_id in web.beliefs:
            status, chain = self._compute_belief_warrant(
                belief_id,
                defeat_graph,
                support_graph,
                ranks,
                obs_beliefs,
                visited=set(),
                depth=0
            )

            chains[belief_id] = chain

            if status == WarrantStatus.WARRANTED:
                warranted.add(belief_id)
            elif status == WarrantStatus.DEFEATED:
                defeated.add(belief_id)
            elif status == WarrantStatus.SUSPENDED:
                suspended.add(belief_id)
            else:
                ungrounded.add(belief_id)

        # Check INV-1 (Consistency)
        violations = self._check_consistency(warranted, defeat_graph)

        return WarrantResult(
            warranted=warranted,
            defeated=defeated,
            suspended=suspended,
            ungrounded=ungrounded,
            chains=chains,
            violations=violations
        )

    def _build_defeat_graph(
        self,
        defeat_relations: List[DefeatRelation]
    ) -> Dict[str, List[DefeatRelation]]:
        """Build graph of defeat relations (defeated_id -> list of defeaters)."""
        graph: Dict[str, List[DefeatRelation]] = {}
        for rel in defeat_relations:
            if rel.defeated_id not in graph:
                graph[rel.defeated_id] = []
            graph[rel.defeated_id].append(rel)
        return graph

    def _build_support_graph(
        self,
        web: "WebOfBelief"
    ) -> Dict[str, List[str]]:
        """Build graph of support relations (target_id -> list of supporter_ids)."""
        graph: Dict[str, List[str]] = {}
        for constraint in web.constraints.values():
            if constraint.constraint_type.value == "SUPPORTS":
                target = constraint.target_id
                source = constraint.source_id
                if target not in graph:
                    graph[target] = []
                graph[target].append(source)
        return graph

    def _identify_observational(self, web: "WebOfBelief") -> Set[str]:
        """Identify beliefs at observational level."""
        obs = set()
        for belief_id, belief in web.beliefs.items():
            level = getattr(belief, 'level', None)
            if level and hasattr(level, 'value') and level.value == "OBSERVATIONAL":
                obs.add(belief_id)
        return obs

    def _compute_belief_warrant(
        self,
        belief_id: str,
        defeat_graph: Dict[str, List[DefeatRelation]],
        support_graph: Dict[str, List[str]],
        ranks: Dict[str, RankPair],
        observational: Set[str],
        visited: Set[str],
        depth: int
    ) -> Tuple[WarrantStatus, DefeatChain]:
        """
        Recursively compute warrant status for a belief.

        Pollock's algorithm:
        1. Check prima facie warrant (has supporters OR is observational)
        2. For each defeater D of B:
           a. If D is warranted (recursive), B is defeated
           b. But check if D is itself defeated (reinstatement)
        3. Handle cycles (SUSPENDED status)
        """
        # Check for cycles
        if belief_id in visited:
            if len(visited) >= self.cycle_threshold:
                return WarrantStatus.SUSPENDED, DefeatChain(
                    belief_id=belief_id,
                    status=WarrantStatus.SUSPENDED,
                    defeaters=[],
                    reinstaters=[],
                    cycle_members=list(visited),
                    depth=depth
                )

        # Check depth limit
        if depth >= self.max_depth:
            return WarrantStatus.SUSPENDED, DefeatChain(
                belief_id=belief_id,
                status=WarrantStatus.SUSPENDED,
                defeaters=[],
                reinstaters=[],
                cycle_members=[],
                depth=depth
            )

        visited = visited | {belief_id}

        # Step 1: Check prima facie warrant
        supporters = support_graph.get(belief_id, [])
        is_observational = belief_id in observational

        if not supporters and not is_observational:
            # No prima facie warrant - ungrounded
            return WarrantStatus.UNGROUNDED, DefeatChain(
                belief_id=belief_id,
                status=WarrantStatus.UNGROUNDED,
                defeaters=[],
                reinstaters=[],
                cycle_members=[],
                depth=depth
            )

        # Step 2: Check defeaters
        defeat_relations = defeat_graph.get(belief_id, [])
        undefeated_defeaters: List[str] = []
        reinstaters: List[str] = []

        for defeat_rel in defeat_relations:
            defeater_id = defeat_rel.defeater_id

            # Check if defeater is warranted
            defeater_status, _ = self._compute_belief_warrant(
                defeater_id,
                defeat_graph,
                support_graph,
                ranks,
                observational,
                visited.copy(),
                depth + 1
            )

            if defeater_status == WarrantStatus.WARRANTED:
                # Defeater is warranted - this belief might be defeated
                # But check for reinstatement (is defeater defeated by something else?)
                defeater_defeaters = defeat_graph.get(defeater_id, [])
                reinstated = False

                for dd_rel in defeater_defeaters:
                    dd_status, _ = self._compute_belief_warrant(
                        dd_rel.defeater_id,
                        defeat_graph,
                        support_graph,
                        ranks,
                        observational,
                        visited.copy(),
                        depth + 2
                    )
                    if dd_status == WarrantStatus.WARRANTED:
                        # Defeater's defeater is warranted - reinstatement!
                        reinstated = True
                        reinstaters.append(dd_rel.defeater_id)
                        break

                if not reinstated:
                    undefeated_defeaters.append(defeater_id)

        # Step 3: Determine final status
        if undefeated_defeaters:
            return WarrantStatus.DEFEATED, DefeatChain(
                belief_id=belief_id,
                status=WarrantStatus.DEFEATED,
                defeaters=undefeated_defeaters,
                reinstaters=reinstaters,
                cycle_members=[],
                depth=depth
            )

        return WarrantStatus.WARRANTED, DefeatChain(
            belief_id=belief_id,
            status=WarrantStatus.WARRANTED,
            defeaters=[],
            reinstaters=reinstaters,
            cycle_members=[],
            depth=depth
        )

    def _check_consistency(
        self,
        warranted: Set[str],
        defeat_graph: Dict[str, List[DefeatRelation]]
    ) -> List[str]:
        """
        Check INV-1 (Consistency): ¬(warranted(B) ∧ warranted(rebutter(B)))

        Returns list of violation messages.
        """
        violations = []

        for defeated_id, relations in defeat_graph.items():
            for rel in relations:
                if rel.defeat_type in (DefeatType.REBUTTING, DefeatType.BOTH):
                    defeater_id = rel.defeater_id

                    # INV-1: Both can't be warranted
                    if defeater_id in warranted and defeated_id in warranted:
                        violations.append(
                            f"INV-1 violation: Both {defeater_id} (rebutter) and "
                            f"{defeated_id} (rebuttee) are warranted"
                        )

        return violations

    def get_defeat_chain(
        self,
        belief_id: str,
        web: "WebOfBelief",
        ranks: Dict[str, RankPair],
        defeat_relations: Optional[List[DefeatRelation]] = None
    ) -> DefeatChain:
        """
        Get the defeat chain explanation for a single belief.

        Args:
            belief_id: The belief to analyze
            web: WebOfBelief instance
            ranks: Current rank assignments
            defeat_relations: List of DefeatRelation objects

        Returns:
            DefeatChain explaining the belief's warrant status
        """
        defeat_graph = self._build_defeat_graph(defeat_relations or [])
        support_graph = self._build_support_graph(web)
        obs_beliefs = self._identify_observational(web)

        _, chain = self._compute_belief_warrant(
            belief_id,
            defeat_graph,
            support_graph,
            ranks,
            obs_beliefs,
            visited=set(),
            depth=0
        )

        return chain


# ============================================================
# CONVENIENCE FUNCTIONS
# ============================================================

def compute_web_warrant(
    web: "WebOfBelief",
    ranks: Dict[str, RankPair],
    defeat_relations: Optional[List[DefeatRelation]] = None
) -> WarrantResult:
    """
    Convenience function to compute warrant for a web.

    Args:
        web: WebOfBelief instance
        ranks: Current rank assignments
        defeat_relations: List of DefeatRelation objects

    Returns:
        WarrantResult with warrant status for all beliefs
    """
    service = WarrantService()
    return service.compute_warrant(web, ranks, defeat_relations)


def create_defeat_relation(
    defeater_id: str,
    defeated_id: str,
    defeat_type: str = "REBUTTING",
    strength: float = 1.0
) -> DefeatRelation:
    """
    Convenience function to create a defeat relation.

    Args:
        defeater_id: ID of the defeating belief
        defeated_id: ID of the defeated belief
        defeat_type: "REBUTTING", "UNDERCUTTING", or "BOTH"
        strength: Strength of defeat (0-1)

    Returns:
        DefeatRelation object
    """
    return DefeatRelation(
        defeater_id=defeater_id,
        defeated_id=defeated_id,
        defeat_type=DefeatType(defeat_type),
        strength=strength
    )
