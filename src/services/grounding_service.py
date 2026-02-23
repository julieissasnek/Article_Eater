"""
Grounding Service (ARCH-4 Phase P4: Haack Foundherentism).

Implements Haack's foundherentist justification theory, tracking both
coherence AND experiential grounding for beliefs.

Key Concepts (per panel consultation 2026-02-12):

Two Dimensions of Justification:
- COHERENCE: How well belief fits with other beliefs (mutual support)
- GROUNDING: How directly belief connects to experience

Haack's Crossword Puzzle Metaphor:
- CLUES (experience → belief): Direct observation, empirical findings
- ENTRIES (belief ↔ belief): Theoretical coherence, support relations

A well-justified belief satisfies BOTH constraints.

Panel Requirements:
- P4.1: Create stateless GroundingService class
- P4.2: Experiential basis tracking (ExperientialClaim)
- P4.3: Grounding metric computation (distance from experience)
- P4.4: Coherence contribution (existing web logic, extracted)
- P4.5: Foundherentist combination (grounding + coherence)

References:
- Haack, S. (1993). Evidence and Inquiry: Towards Reconstruction in Epistemology.
- Haack, S. (2009). Evidence and Inquiry: A Pragmatist Reconstruction.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Any, TYPE_CHECKING
from enum import Enum
import logging

if TYPE_CHECKING:
    from src.services.web_of_belief import WebOfBelief

logger = logging.getLogger(__name__)


class GroundingStatus(str, Enum):
    """
    Grounding status for a belief (per Haack).

    Indicates how the belief connects to experiential basis.
    """
    GROUNDED_EXPERIENTIAL = "GROUNDED_EXPERIENTIAL"  # Direct observation
    GROUNDED_COHERENT = "GROUNDED_COHERENT"          # Via supports from grounded beliefs
    GROUNDED_MIXED = "GROUNDED_MIXED"                # Both paths
    UNGROUNDED = "UNGROUNDED"                        # Orphaned, no path to experience


class JustificationStatus(str, Enum):
    """
    Foundherentist justification status.

    Combines grounding and coherence per Haack's theory.
    """
    WELL_JUSTIFIED = "WELL_JUSTIFIED"      # Both grounded AND coherent
    GROUNDED_ONLY = "GROUNDED_ONLY"        # Experience but isolated
    COHERENT_ONLY = "COHERENT_ONLY"        # Connected but floating
    UNJUSTIFIED = "UNJUSTIFIED"            # Neither grounded nor coherent


@dataclass
class ExperientialClaim:
    """
    An experiential claim supporting a belief (Haack's "clue").

    Tracks the source and directness of experiential connection.
    """
    claim_id: str
    source: str                      # Paper ID, observation ID, etc.
    source_type: str                 # "observation", "experiment", "survey", etc.
    content: str                     # What was experienced
    directness: float                # 0.0 = inference only, 1.0 = direct observation

    def to_dict(self) -> Dict[str, Any]:
        return {
            "claim_id": self.claim_id,
            "source": self.source,
            "source_type": self.source_type,
            "content": self.content,
            "directness": self.directness
        }


@dataclass
class GroundingChain:
    """
    Chain from belief to experiential basis.

    Tracks the path through which a belief is grounded in experience.
    """
    belief_id: str
    grounding_status: GroundingStatus
    path_length: int                          # Hops to experience
    experiential_bases: List[ExperientialClaim]  # Terminal experiential claims
    support_path: List[str]                   # Belief IDs in grounding path

    def to_dict(self) -> Dict[str, Any]:
        return {
            "belief_id": self.belief_id,
            "grounding_status": self.grounding_status.value,
            "path_length": self.path_length,
            "experiential_bases": [e.to_dict() for e in self.experiential_bases],
            "support_path": self.support_path
        }


@dataclass
class FoundherentistScore:
    """
    Foundherentist justification score for a belief.

    Combines grounding and coherence per Haack-Spohn panel resolution.
    """
    belief_id: str
    grounding_component: float       # 0-1, directness of experiential connection
    coherence_component: float       # 0-1, strength of mutual support
    combined_score: float            # Weighted combination
    justification_status: JustificationStatus
    grounding_chain: Optional[GroundingChain]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "belief_id": self.belief_id,
            "grounding_component": self.grounding_component,
            "coherence_component": self.coherence_component,
            "combined_score": self.combined_score,
            "justification_status": self.justification_status.value,
            "grounding_chain": self.grounding_chain.to_dict() if self.grounding_chain else None
        }


@dataclass
class GroundingResult:
    """Result from grounding computation."""
    scores: Dict[str, FoundherentistScore]
    grounded_beliefs: Set[str]
    ungrounded_beliefs: Set[str]
    violations: List[str]           # INV-2 violations

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scores": {k: v.to_dict() for k, v in self.scores.items()},
            "grounded_beliefs": list(self.grounded_beliefs),
            "ungrounded_beliefs": list(self.ungrounded_beliefs),
            "violations": self.violations
        }


class GroundingService:
    """
    Stateless service for computing foundherentist justification.

    Per panel requirements:
    - Pure function: web state → grounding scores
    - Tracks experiential basis per belief
    - Computes both grounding and coherence components
    - Enforces INV-2 (Groundedness): warranted → grounded ∨ supported_by_warranted

    Usage:
        >>> service = GroundingService()
        >>> result = service.compute_grounding(web, warranted)
        >>> for bid, score in result.scores.items():
        ...     print(f"{bid}: {score.justification_status.value}")
    """

    def __init__(
        self,
        grounding_weight: float = 0.4,      # Weight for grounding in combination
        coherence_weight: float = 0.3,      # Weight for coherence
        level_weight: float = 0.3,          # Weight for epistemic level
        max_path_length: int = 10,          # Max hops to experience
        grounding_threshold: float = 0.3,   # Min grounding to be "grounded"
        coherence_threshold: float = 0.3    # Min coherence to be "coherent"
    ):
        self.grounding_weight = grounding_weight
        self.coherence_weight = coherence_weight
        self.level_weight = level_weight
        self.max_path_length = max_path_length
        self.grounding_threshold = grounding_threshold
        self.coherence_threshold = coherence_threshold

    def compute_grounding(
        self,
        web: "WebOfBelief",
        warranted_beliefs: Set[str],
        experiential_claims: Optional[Dict[str, List[ExperientialClaim]]] = None
    ) -> GroundingResult:
        """
        Compute foundherentist justification for all beliefs.

        Args:
            web: WebOfBelief instance
            warranted_beliefs: Set of warranted belief IDs
            experiential_claims: Map of belief_id -> experiential claims

        Returns:
            GroundingResult with justification scores
        """
        experiential_claims = experiential_claims or {}

        # Build support graph
        support_graph = self._build_support_graph(web)

        # Identify observational beliefs (have direct experiential basis)
        observational = self._identify_observational(web)

        # Compute grounding for each belief
        scores: Dict[str, FoundherentistScore] = {}
        grounded: Set[str] = set()
        ungrounded: Set[str] = set()

        for belief_id in web.beliefs:
            # Compute grounding chain
            chain = self._compute_grounding_chain(
                belief_id,
                support_graph,
                observational,
                experiential_claims,
                visited=set()
            )

            # Compute grounding component
            grounding_score = self._compute_grounding_score(chain, experiential_claims.get(belief_id, []))

            # Compute coherence component
            coherence_score = self._compute_coherence_score(belief_id, web, warranted_beliefs)

            # Compute level-based component
            level_score = self._compute_level_score(belief_id, web)

            # Combine scores (per Haack-Spohn resolution)
            combined = (
                self.grounding_weight * grounding_score +
                self.coherence_weight * coherence_score +
                self.level_weight * level_score
            )

            # Determine justification status
            has_grounding = grounding_score >= self.grounding_threshold
            has_coherence = coherence_score >= self.coherence_threshold

            if has_grounding and has_coherence:
                status = JustificationStatus.WELL_JUSTIFIED
            elif has_grounding:
                status = JustificationStatus.GROUNDED_ONLY
            elif has_coherence:
                status = JustificationStatus.COHERENT_ONLY
            else:
                status = JustificationStatus.UNJUSTIFIED

            scores[belief_id] = FoundherentistScore(
                belief_id=belief_id,
                grounding_component=grounding_score,
                coherence_component=coherence_score,
                combined_score=combined,
                justification_status=status,
                grounding_chain=chain
            )

            if chain.grounding_status != GroundingStatus.UNGROUNDED:
                grounded.add(belief_id)
            else:
                ungrounded.add(belief_id)

        # Check INV-2 (Groundedness)
        violations = self._check_groundedness(warranted_beliefs, grounded, support_graph)

        return GroundingResult(
            scores=scores,
            grounded_beliefs=grounded,
            ungrounded_beliefs=ungrounded,
            violations=violations
        )

    def _build_support_graph(self, web: "WebOfBelief") -> Dict[str, List[str]]:
        """Build support graph (target_id -> list of supporter_ids)."""
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

    def _compute_grounding_chain(
        self,
        belief_id: str,
        support_graph: Dict[str, List[str]],
        observational: Set[str],
        experiential_claims: Dict[str, List[ExperientialClaim]],
        visited: Set[str],
        depth: int = 0
    ) -> GroundingChain:
        """
        Compute the grounding chain for a belief.

        Traces support paths back to observational/experiential basis.
        """
        # Check for cycles
        if belief_id in visited:
            return GroundingChain(
                belief_id=belief_id,
                grounding_status=GroundingStatus.UNGROUNDED,
                path_length=-1,
                experiential_bases=[],
                support_path=list(visited)
            )

        # Check depth limit
        if depth >= self.max_path_length:
            return GroundingChain(
                belief_id=belief_id,
                grounding_status=GroundingStatus.UNGROUNDED,
                path_length=-1,
                experiential_bases=[],
                support_path=[]
            )

        visited = visited | {belief_id}

        # Check if this belief is observational (directly grounded)
        if belief_id in observational:
            claims = experiential_claims.get(belief_id, [])
            return GroundingChain(
                belief_id=belief_id,
                grounding_status=GroundingStatus.GROUNDED_EXPERIENTIAL,
                path_length=0,
                experiential_bases=claims,
                support_path=[belief_id]
            )

        # Check if belief has experiential claims
        claims = experiential_claims.get(belief_id, [])
        has_direct_experience = len(claims) > 0

        # Trace support paths
        supporters = support_graph.get(belief_id, [])
        best_path: Optional[GroundingChain] = None
        all_bases: List[ExperientialClaim] = list(claims)

        for supporter_id in supporters:
            supporter_chain = self._compute_grounding_chain(
                supporter_id,
                support_graph,
                observational,
                experiential_claims,
                visited.copy(),
                depth + 1
            )

            if supporter_chain.grounding_status != GroundingStatus.UNGROUNDED:
                all_bases.extend(supporter_chain.experiential_bases)

                if best_path is None or supporter_chain.path_length < best_path.path_length:
                    best_path = supporter_chain

        # Determine grounding status
        if has_direct_experience and best_path:
            status = GroundingStatus.GROUNDED_MIXED
            path_length = min(0, best_path.path_length + 1)
        elif has_direct_experience:
            status = GroundingStatus.GROUNDED_EXPERIENTIAL
            path_length = 0
        elif best_path:
            status = GroundingStatus.GROUNDED_COHERENT
            path_length = best_path.path_length + 1
        else:
            status = GroundingStatus.UNGROUNDED
            path_length = -1

        support_path = [belief_id]
        if best_path:
            support_path.extend(best_path.support_path)

        return GroundingChain(
            belief_id=belief_id,
            grounding_status=status,
            path_length=path_length,
            experiential_bases=all_bases,
            support_path=support_path
        )

    def _compute_grounding_score(
        self,
        chain: GroundingChain,
        direct_claims: List[ExperientialClaim]
    ) -> float:
        """
        Compute grounding score (0-1) from grounding chain.

        Higher score for:
        - Shorter path to experience
        - More direct experiential claims
        - Higher directness of claims
        """
        if chain.grounding_status == GroundingStatus.UNGROUNDED:
            return 0.0

        if chain.grounding_status == GroundingStatus.GROUNDED_EXPERIENTIAL:
            # Direct experience: base score + directness bonus
            if direct_claims:
                directness = sum(c.directness for c in direct_claims) / len(direct_claims)
                return 0.7 + 0.3 * directness
            return 0.8

        # Coherent grounding: decays with path length
        if chain.path_length <= 0:
            return 0.6

        decay = 0.8 ** chain.path_length
        base_score = 0.5 * decay

        # Bonus for experiential bases
        if chain.experiential_bases:
            avg_directness = sum(c.directness for c in chain.experiential_bases) / len(chain.experiential_bases)
            base_score += 0.2 * avg_directness

        return min(1.0, base_score)

    def _compute_coherence_score(
        self,
        belief_id: str,
        web: "WebOfBelief",
        warranted_beliefs: Set[str]
    ) -> float:
        """
        Compute coherence score (0-1) from web structure.

        Higher score for:
        - More support relationships (both giving and receiving)
        - Support from warranted beliefs
        - Being part of well-connected network
        """
        belief = web.beliefs.get(belief_id)
        if not belief:
            return 0.0

        # Count support relationships
        supporters = []
        supportees = []

        for constraint in web.constraints.values():
            if constraint.constraint_type.value == "SUPPORTS":
                if constraint.target_id == belief_id:
                    supporters.append(constraint.source_id)
                elif constraint.source_id == belief_id:
                    supportees.append(constraint.target_id)

        # Base coherence from connectivity
        n_connections = len(supporters) + len(supportees)
        connectivity_score = min(1.0, n_connections / 10)  # Saturates at 10

        # Bonus for warranted supporters
        warranted_supporters = sum(1 for s in supporters if s in warranted_beliefs)
        warrant_bonus = min(0.3, warranted_supporters * 0.1)

        return min(1.0, connectivity_score * 0.7 + warrant_bonus)

    def _compute_level_score(
        self,
        belief_id: str,
        web: "WebOfBelief"
    ) -> float:
        """
        Compute level-based score (0-1).

        Observational beliefs get highest score, theoretical lowest.
        """
        belief = web.beliefs.get(belief_id)
        if not belief:
            return 0.0

        level = getattr(belief, 'level', None)
        if not level:
            return 0.5

        level_value = level.value if hasattr(level, 'value') else str(level)

        level_scores = {
            "OBSERVATIONAL": 1.0,
            "EMPIRICAL": 0.7,
            "INTERMEDIATE": 0.5,
            "THEORETICAL": 0.3
        }

        return level_scores.get(level_value, 0.5)

    def _check_groundedness(
        self,
        warranted: Set[str],
        grounded: Set[str],
        support_graph: Dict[str, List[str]]
    ) -> List[str]:
        """
        Check INV-2 (Groundedness): warranted → grounded ∨ supported_by_warranted

        Returns list of violation messages.
        """
        violations = []

        for belief_id in warranted:
            if belief_id in grounded:
                continue

            # Check if supported by warranted belief
            supporters = support_graph.get(belief_id, [])
            has_warranted_support = any(s in warranted for s in supporters)

            if not has_warranted_support:
                violations.append(
                    f"INV-2 violation: {belief_id} is warranted but "
                    f"neither grounded nor supported by warranted beliefs"
                )

        return violations


# ============================================================
# CONVENIENCE FUNCTIONS
# ============================================================

def compute_web_grounding(
    web: "WebOfBelief",
    warranted_beliefs: Set[str]
) -> GroundingResult:
    """
    Convenience function to compute grounding for a web.

    Args:
        web: WebOfBelief instance
        warranted_beliefs: Set of warranted belief IDs

    Returns:
        GroundingResult with justification scores
    """
    service = GroundingService()
    return service.compute_grounding(web, warranted_beliefs)


def create_experiential_claim(
    claim_id: str,
    source: str,
    content: str,
    directness: float = 1.0,
    source_type: str = "observation"
) -> ExperientialClaim:
    """
    Convenience function to create an experiential claim.

    Args:
        claim_id: Unique identifier
        source: Source of experience (paper_id, etc.)
        content: What was experienced
        directness: 0.0 = inference, 1.0 = direct observation
        source_type: Type of source

    Returns:
        ExperientialClaim object
    """
    return ExperientialClaim(
        claim_id=claim_id,
        source=source,
        source_type=source_type,
        content=content,
        directness=directness
    )
