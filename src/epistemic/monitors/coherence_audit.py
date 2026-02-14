"""
Coherence Audit Algorithm (Sprint T3-3.1).

Detects nodes whose entrenchment changed purely from coherence settling
(not from new direct evidence). This is a key reflexive monitoring capability
that helps identify "free-riding" beliefs that gain credence through network
effects rather than independent empirical support.

References:
- Quine, W.V.O. (1951). Two Dogmas of Empiricism
- BonJour, L. (1985). The Structure of Empirical Knowledge
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Any
from enum import Enum


class FlagType(str, Enum):
    """Types of coherence drift flags."""
    COHERENCE_DRIFT_POSITIVE = "coherence_drift_positive"  # Gained entrenchment from coherence
    COHERENCE_DRIFT_NEGATIVE = "coherence_drift_negative"  # Lost entrenchment from coherence


@dataclass
class FlaggedNode:
    """A node flagged for coherence-based entrenchment change."""
    node_id: str
    old_entrenchment: float
    new_entrenchment: float
    coherence_delta: float
    direct_evidence_delta: float
    flag_type: FlagType
    triggering_claims: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "node_id": self.node_id,
            "old_entrenchment": self.old_entrenchment,
            "new_entrenchment": self.new_entrenchment,
            "coherence_delta": self.coherence_delta,
            "direct_evidence_delta": self.direct_evidence_delta,
            "flag_type": self.flag_type.value,
            "triggering_claims": self.triggering_claims,
        }


@dataclass
class CoherenceAuditResult:
    """Result of running a coherence audit."""
    flagged_nodes: List[FlaggedNode]
    total_nodes_checked: int
    total_flagged: int
    threshold_used: float
    new_claims_analyzed: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "flagged_nodes": [n.to_dict() for n in self.flagged_nodes],
            "total_nodes_checked": self.total_nodes_checked,
            "total_flagged": self.total_flagged,
            "threshold_used": self.threshold_used,
            "new_claims_analyzed": self.new_claims_analyzed,
        }

    @property
    def has_flags(self) -> bool:
        return self.total_flagged > 0

    def get_positive_drifts(self) -> List[FlaggedNode]:
        """Get nodes that gained entrenchment from coherence."""
        return [n for n in self.flagged_nodes if n.flag_type == FlagType.COHERENCE_DRIFT_POSITIVE]

    def get_negative_drifts(self) -> List[FlaggedNode]:
        """Get nodes that lost entrenchment from coherence."""
        return [n for n in self.flagged_nodes if n.flag_type == FlagType.COHERENCE_DRIFT_NEGATIVE]


def run_coherence_audit(
    web: Any,
    pre_snapshot: Dict[str, float],
    post_snapshot: Dict[str, float],
    new_claim_ids: List[str],
    threshold: float = 0.1,
    direct_evidence_links: Optional[Dict[str, Set[str]]] = None
) -> CoherenceAuditResult:
    """
    Detect nodes whose entrenchment changed purely from coherence settling.

    This audit identifies beliefs that gained or lost credence through network
    effects (coherence with other beliefs) rather than through direct empirical
    evidence. Such beliefs may be epistemically vulnerable.

    Args:
        web: The web-of-belief graph (used for link traversal if needed).
             Can be None if direct_evidence_links is provided.
        pre_snapshot: {node_id: entrenchment_score} before integration
        post_snapshot: {node_id: entrenchment_score} after integration
        new_claim_ids: IDs of newly integrated claims
        threshold: Minimum delta to flag (default 0.1 = 10% change)
        direct_evidence_links: Optional pre-computed mapping of
            {claim_id: set of node_ids it directly supports}

    Returns:
        CoherenceAuditResult with flagged nodes and summary statistics.

    Example:
        >>> pre = {"A": 0.5, "B": 0.4, "C": 0.6}
        >>> post = {"A": 0.7, "B": 0.55, "C": 0.6}  # A and B changed
        >>> new_claims = ["claim_1"]
        >>> # claim_1 directly supports A
        >>> direct_links = {"claim_1": {"A"}}
        >>> result = run_coherence_audit(None, pre, post, new_claims,
        ...                               direct_evidence_links=direct_links)
        >>> # B should be flagged (changed but no direct evidence)
        >>> # A should NOT be flagged (has direct evidence)
    """
    new_claim_set = set(new_claim_ids)
    flagged_nodes: List[FlaggedNode] = []

    # Build set of nodes that received direct evidence from new claims
    nodes_with_direct_evidence: Set[str] = set()
    if direct_evidence_links:
        for claim_id in new_claim_ids:
            if claim_id in direct_evidence_links:
                nodes_with_direct_evidence.update(direct_evidence_links[claim_id])

    # If we have a web object, try to extract direct evidence links
    if web is not None and not direct_evidence_links:
        nodes_with_direct_evidence = _extract_direct_evidence_nodes(web, new_claim_ids)

    # Check all nodes in the post-snapshot (excluding new claims themselves)
    nodes_to_check = set(post_snapshot.keys()) - new_claim_set

    for node_id in nodes_to_check:
        old_entrenchment = pre_snapshot.get(node_id, 0.0)
        new_entrenchment = post_snapshot.get(node_id, 0.0)
        coherence_delta = new_entrenchment - old_entrenchment

        # Check if this node received direct evidence
        has_direct_evidence = node_id in nodes_with_direct_evidence
        direct_evidence_delta = 1.0 if has_direct_evidence else 0.0

        # Flag if significant change AND no direct evidence
        if abs(coherence_delta) > threshold and not has_direct_evidence:
            flag_type = (
                FlagType.COHERENCE_DRIFT_POSITIVE
                if coherence_delta > 0
                else FlagType.COHERENCE_DRIFT_NEGATIVE
            )

            # Find which new claims triggered this drift
            triggering = _find_triggering_claims(
                web, node_id, new_claim_ids
            ) if web else new_claim_ids

            flagged_nodes.append(FlaggedNode(
                node_id=node_id,
                old_entrenchment=old_entrenchment,
                new_entrenchment=new_entrenchment,
                coherence_delta=coherence_delta,
                direct_evidence_delta=direct_evidence_delta,
                flag_type=flag_type,
                triggering_claims=triggering,
            ))

    return CoherenceAuditResult(
        flagged_nodes=flagged_nodes,
        total_nodes_checked=len(nodes_to_check),
        total_flagged=len(flagged_nodes),
        threshold_used=threshold,
        new_claims_analyzed=new_claim_ids,
    )


def _extract_direct_evidence_nodes(web: Any, new_claim_ids: List[str]) -> Set[str]:
    """
    Extract nodes that receive direct evidence from new claims.

    Attempts to use web object's methods to find direct support links.
    """
    nodes: Set[str] = set()

    # Try different web API patterns
    for claim_id in new_claim_ids:
        # Pattern 1: web has get_supported_nodes method
        if hasattr(web, 'get_supported_nodes'):
            try:
                supported = web.get_supported_nodes(claim_id)
                nodes.update(supported)
            except Exception:
                pass

        # Pattern 2: web has get_outgoing_edges method
        if hasattr(web, 'get_outgoing_edges'):
            try:
                edges = web.get_outgoing_edges(claim_id)
                for edge in edges:
                    if hasattr(edge, 'target'):
                        nodes.add(edge.target)
                    elif isinstance(edge, tuple) and len(edge) >= 2:
                        nodes.add(edge[1])
            except Exception:
                pass

        # Pattern 3: web has constraints attribute (our Constraint model)
        if hasattr(web, 'constraints'):
            try:
                for constraint in web.constraints:
                    if hasattr(constraint, 'source_belief_id'):
                        if constraint.source_belief_id == claim_id:
                            if hasattr(constraint, 'target_belief_id'):
                                nodes.add(constraint.target_belief_id)
            except Exception:
                pass

    return nodes


def _find_triggering_claims(
    web: Any,
    node_id: str,
    new_claim_ids: List[str]
) -> List[str]:
    """
    Find which new claims are connected to the flagged node.

    Returns list of new claims that have a path to this node.
    """
    triggering: List[str] = []

    if web is None:
        return new_claim_ids  # Can't determine, return all

    for claim_id in new_claim_ids:
        # Check if there's any connection between claim and node
        if _has_path(web, claim_id, node_id):
            triggering.append(claim_id)

    return triggering if triggering else new_claim_ids


def _has_path(web: Any, source: str, target: str, max_depth: int = 5) -> bool:
    """
    Check if there's a path from source to target in the web.

    Uses BFS with depth limit to avoid infinite traversal.
    """
    if source == target:
        return True

    visited: Set[str] = set()
    queue: List[tuple] = [(source, 0)]

    while queue:
        current, depth = queue.pop(0)
        if depth >= max_depth:
            continue

        if current in visited:
            continue
        visited.add(current)

        # Get neighbors
        neighbors: List[str] = []
        if hasattr(web, 'get_neighbors'):
            try:
                neighbors = list(web.get_neighbors(current))
            except Exception:
                pass
        elif hasattr(web, 'get_outgoing_edges'):
            try:
                edges = web.get_outgoing_edges(current)
                for edge in edges:
                    if hasattr(edge, 'target'):
                        neighbors.append(edge.target)
                    elif isinstance(edge, tuple):
                        neighbors.append(edge[1])
            except Exception:
                pass

        for neighbor in neighbors:
            if neighbor == target:
                return True
            if neighbor not in visited:
                queue.append((neighbor, depth + 1))

    return False
