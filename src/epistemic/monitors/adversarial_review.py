"""
Adversarial Review Cycle (Sprint T3-3.4).

Stress-tests the most entrenched claims by temporarily boosting counter-evidence.
This simulates what would happen if counter-evidence were given more weight,
helping identify claims that are robust vs. vulnerable to challenge.

The adversarial review is a key reflexive capability: it allows the system
to anticipate how beliefs would fare under more skeptical conditions.

References:
- Pollock, J.L. (1987). Defeasible Reasoning
- Mill, J.S. (1859). On Liberty (marketplace of ideas)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Any, Callable
from enum import Enum


class SurvivalStatus(str, Enum):
    """Outcome of adversarial review."""
    SURVIVED = "survived"              # Still above acceptance threshold
    VULNERABLE = "vulnerable"          # Dropped below threshold
    COLLAPSED = "collapsed"            # Dropped to near-zero


@dataclass
class ReviewedNode:
    """Result of adversarial review for a single node."""
    node_id: str
    pre_review_entrenchment: float
    post_review_entrenchment: float
    vulnerability_score: float  # Magnitude of drop (0 = no change, 1 = total collapse)
    survival_status: SurvivalStatus
    counter_evidence_count: int
    counter_evidence_summary: List[str]
    recommendation: str

    def to_dict(self) -> Dict:
        return {
            "node_id": self.node_id,
            "pre_review_entrenchment": self.pre_review_entrenchment,
            "post_review_entrenchment": self.post_review_entrenchment,
            "vulnerability_score": self.vulnerability_score,
            "survival_status": self.survival_status.value,
            "counter_evidence_count": self.counter_evidence_count,
            "counter_evidence_summary": self.counter_evidence_summary,
            "recommendation": self.recommendation,
        }

    @property
    def survived(self) -> bool:
        return self.survival_status == SurvivalStatus.SURVIVED


@dataclass
class AdversarialReviewResult:
    """Result of running adversarial review on multiple nodes."""
    reviewed_nodes: List[ReviewedNode]
    total_reviewed: int
    survived_count: int
    vulnerable_count: int
    collapsed_count: int
    precision_boost_used: float
    acceptance_threshold: float

    def to_dict(self) -> Dict:
        return {
            "reviewed_nodes": [n.to_dict() for n in self.reviewed_nodes],
            "total_reviewed": self.total_reviewed,
            "summary": {
                "survived": self.survived_count,
                "vulnerable": self.vulnerable_count,
                "collapsed": self.collapsed_count,
            },
            "parameters": {
                "precision_boost": self.precision_boost_used,
                "acceptance_threshold": self.acceptance_threshold,
            },
        }

    @property
    def vulnerability_rate(self) -> float:
        """Fraction of nodes that became vulnerable or collapsed."""
        if self.total_reviewed == 0:
            return 0.0
        return (self.vulnerable_count + self.collapsed_count) / self.total_reviewed

    def get_vulnerable_nodes(self) -> List[ReviewedNode]:
        """Get nodes that became vulnerable under adversarial conditions."""
        return [n for n in self.reviewed_nodes
                if n.survival_status in (SurvivalStatus.VULNERABLE, SurvivalStatus.COLLAPSED)]


def run_adversarial_review(
    web: Any,
    n_top_nodes: int = 10,
    precision_boost: float = 1.5,
    acceptance_threshold: float = 0.5,
    entrenchment_scores: Optional[Dict[str, float]] = None,
    counter_evidence: Optional[Dict[str, List[Dict]]] = None,
    recompute_entrenchment: Optional[Callable] = None,
) -> AdversarialReviewResult:
    """
    Stress-test the most entrenched claims by boosting counter-evidence.

    Simulates a more skeptical reviewer by temporarily increasing the weight
    of counter-evidence (contradicting studies, failed replications) and
    observing which beliefs remain stable.

    Args:
        web: The web-of-belief graph.
        n_top_nodes: Number of top entrenched nodes to review (default 10).
        precision_boost: How much to multiply counter-evidence weight (default 1.5).
        acceptance_threshold: Entrenchment below which belief is "vulnerable" (0.5).
        entrenchment_scores: Optional pre-computed {node_id: entrenchment}.
        counter_evidence: Optional {node_id: list of counter-evidence dicts}.
            Each dict should have: {"source": str, "type": str, "weight": float}
        recompute_entrenchment: Optional function(web, boosted_weights) -> Dict[str, float]
            If not provided, uses simple simulation.

    Returns:
        AdversarialReviewResult with reviewed nodes and survival statistics.

    Example:
        >>> entrenchment = {"A": 0.9, "B": 0.8, "C": 0.7}
        >>> counter = {"A": [{"source": "study_x", "type": "failed_replication", "weight": 0.3}]}
        >>> result = run_adversarial_review(None, n_top_nodes=3,
        ...                                  entrenchment_scores=entrenchment,
        ...                                  counter_evidence=counter)
        >>> # A has counter-evidence, so should show vulnerability after boost
    """
    # Get entrenchment scores
    if entrenchment_scores is None:
        entrenchment_scores = _extract_entrenchment(web)

    if not entrenchment_scores:
        return AdversarialReviewResult(
            reviewed_nodes=[],
            total_reviewed=0,
            survived_count=0,
            vulnerable_count=0,
            collapsed_count=0,
            precision_boost_used=precision_boost,
            acceptance_threshold=acceptance_threshold,
        )

    # Get counter-evidence
    if counter_evidence is None:
        counter_evidence = _extract_counter_evidence(web)

    # Select top N most entrenched nodes
    sorted_nodes = sorted(
        entrenchment_scores.items(),
        key=lambda x: x[1],
        reverse=True
    )[:n_top_nodes]

    reviewed_nodes: List[ReviewedNode] = []
    survived_count = 0
    vulnerable_count = 0
    collapsed_count = 0

    for node_id, pre_entrenchment in sorted_nodes:
        # Get counter-evidence for this node
        node_counter = counter_evidence.get(node_id, [])

        # Simulate boosted counter-evidence effect
        post_entrenchment = _simulate_adversarial_entrenchment(
            pre_entrenchment,
            node_counter,
            precision_boost,
            recompute_entrenchment,
            web,
            node_id,
        )

        # Compute vulnerability score
        if pre_entrenchment > 0:
            vulnerability_score = (pre_entrenchment - post_entrenchment) / pre_entrenchment
        else:
            vulnerability_score = 0.0
        vulnerability_score = max(0.0, min(1.0, vulnerability_score))

        # Determine survival status
        if post_entrenchment >= acceptance_threshold:
            status = SurvivalStatus.SURVIVED
            survived_count += 1
        elif post_entrenchment < 0.1:
            status = SurvivalStatus.COLLAPSED
            collapsed_count += 1
        else:
            status = SurvivalStatus.VULNERABLE
            vulnerable_count += 1

        # Generate counter-evidence summary
        summary = [f"{ce.get('type', 'evidence')}: {ce.get('source', 'unknown')}"
                  for ce in node_counter[:5]]  # Limit to 5

        # Generate recommendation
        recommendation = _generate_recommendation(
            status, vulnerability_score, len(node_counter)
        )

        reviewed_nodes.append(ReviewedNode(
            node_id=node_id,
            pre_review_entrenchment=pre_entrenchment,
            post_review_entrenchment=post_entrenchment,
            vulnerability_score=vulnerability_score,
            survival_status=status,
            counter_evidence_count=len(node_counter),
            counter_evidence_summary=summary,
            recommendation=recommendation,
        ))

    return AdversarialReviewResult(
        reviewed_nodes=reviewed_nodes,
        total_reviewed=len(reviewed_nodes),
        survived_count=survived_count,
        vulnerable_count=vulnerable_count,
        collapsed_count=collapsed_count,
        precision_boost_used=precision_boost,
        acceptance_threshold=acceptance_threshold,
    )


def _simulate_adversarial_entrenchment(
    pre_entrenchment: float,
    counter_evidence: List[Dict],
    precision_boost: float,
    recompute_fn: Optional[Callable],
    web: Any,
    node_id: str,
) -> float:
    """
    Simulate entrenchment after boosting counter-evidence.

    If a recompute function is provided, uses it.
    Otherwise, uses a simple heuristic model.
    """
    if recompute_fn is not None:
        try:
            # Build boosted weights
            boosted = {}
            for ce in counter_evidence:
                source = ce.get('source', 'unknown')
                original_weight = ce.get('weight', 0.1)
                boosted[source] = original_weight * precision_boost
            return recompute_fn(web, node_id, boosted)
        except Exception:
            pass

    # Simple heuristic model:
    # Each counter-evidence item reduces entrenchment proportionally
    # Effect is amplified by precision_boost
    if not counter_evidence:
        return pre_entrenchment

    total_counter_weight = sum(
        ce.get('weight', 0.1) * precision_boost
        for ce in counter_evidence
    )

    # Entrenchment reduction is sigmoid-like
    # More counter-evidence = larger reduction, but diminishing returns
    reduction_factor = total_counter_weight / (1.0 + total_counter_weight)

    post_entrenchment = pre_entrenchment * (1.0 - reduction_factor)

    return max(0.0, min(1.0, post_entrenchment))


def _generate_recommendation(
    status: SurvivalStatus,
    vulnerability: float,
    counter_count: int
) -> str:
    """Generate recommendation based on adversarial review outcome."""
    if status == SurvivalStatus.COLLAPSED:
        return "CRITICAL: Belief collapses under scrutiny. Requires major evidential support."
    elif status == SurvivalStatus.VULNERABLE:
        if counter_count > 3:
            return "Multiple counter-evidence sources. Needs direct replication or reconciliation."
        else:
            return "Vulnerable to counter-evidence. Investigate and address specific challenges."
    else:  # SURVIVED
        if vulnerability > 0.3:
            return "Survived but showed significant vulnerability. Monitor for new counter-evidence."
        elif counter_count > 0:
            return "Robust under adversarial conditions despite counter-evidence."
        else:
            return "No significant counter-evidence found. Stable belief."


def _extract_entrenchment(web: Any) -> Dict[str, float]:
    """Extract entrenchment scores from web object."""
    scores: Dict[str, float] = {}

    if web is None:
        return scores

    if hasattr(web, 'get_entrenchment_scores'):
        try:
            return web.get_entrenchment_scores()
        except Exception:
            pass

    if hasattr(web, 'beliefs'):
        try:
            for belief in web.beliefs:
                belief_id = getattr(belief, 'belief_id', getattr(belief, 'id', None))
                entrenchment = getattr(belief, 'entrenchment', None)
                if belief_id and entrenchment is not None:
                    scores[belief_id] = entrenchment
        except Exception:
            pass

    return scores


def _extract_counter_evidence(web: Any) -> Dict[str, List[Dict]]:
    """Extract counter-evidence for each node from web object."""
    counter: Dict[str, List[Dict]] = {}

    if web is None:
        return counter

    # Try to get from constraints
    if hasattr(web, 'constraints'):
        try:
            for constraint in web.constraints:
                constraint_type = getattr(constraint, 'constraint_type', None)
                if constraint_type:
                    type_str = str(constraint_type).lower()
                    # Look for contradicting/challenging constraints
                    if any(kw in type_str for kw in ['contradict', 'tension', 'challenge', 'fail']):
                        target = getattr(constraint, 'target_belief_id', None)
                        source = getattr(constraint, 'source_belief_id', None)
                        if target and source:
                            if target not in counter:
                                counter[target] = []
                            counter[target].append({
                                'source': source,
                                'type': type_str,
                                'weight': getattr(constraint, 'strength', 0.1),
                            })
        except Exception:
            pass

    # Try to get from failed replications
    if hasattr(web, 'beliefs'):
        try:
            for belief in web.beliefs:
                belief_id = getattr(belief, 'belief_id', getattr(belief, 'id', None))
                replication_status = getattr(belief, 'replication_status', None)
                if belief_id and replication_status:
                    status_str = str(replication_status).lower()
                    if 'fail' in status_str:
                        # This belief itself is a failed replication
                        # Add as counter-evidence to what it tried to replicate
                        original = getattr(belief, 'replicates', None)
                        if original:
                            if original not in counter:
                                counter[original] = []
                            counter[original].append({
                                'source': belief_id,
                                'type': 'failed_replication',
                                'weight': 0.3,
                            })
        except Exception:
            pass

    return counter
