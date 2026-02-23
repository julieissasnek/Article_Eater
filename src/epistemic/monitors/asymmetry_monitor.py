"""
Entrenchment Asymmetry Monitor (Sprint T3-3.2).

Identifies nodes that are highly entrenched (many coherence connections)
but have weak direct empirical support. Such nodes may be "coherence free-riders"
that appear well-supported due to network position rather than evidence quality.

This is a key vulnerability indicator: beliefs can become entrenched through
mutual coherence without sufficient empirical grounding.

References:
- Haack, S. (1993). Evidence and Inquiry: Foundherentist epistemology
- BonJour, L. (1985). The Structure of Empirical Knowledge (isolation objection)
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from enum import Enum


class AsymmetryRisk(str, Enum):
    """Risk levels for asymmetry."""
    HIGH = "high"        # ratio > 5.0
    MEDIUM = "medium"    # ratio > 3.0
    LOW = "low"          # ratio > threshold but < 3.0


@dataclass
class AsymmetryFlag:
    """A node flagged for entrenchment asymmetry."""
    node_id: str
    entrenchment_score: float
    direct_evidence_score: float
    asymmetry_ratio: float
    risk_level: AsymmetryRisk
    coherence_link_count: int
    direct_study_count: int
    recommendation: str

    def to_dict(self) -> Dict:
        return {
            "node_id": self.node_id,
            "entrenchment_score": self.entrenchment_score,
            "direct_evidence_score": self.direct_evidence_score,
            "asymmetry_ratio": self.asymmetry_ratio,
            "risk_level": self.risk_level.value,
            "coherence_link_count": self.coherence_link_count,
            "direct_study_count": self.direct_study_count,
            "recommendation": self.recommendation,
        }


@dataclass
class AsymmetryResult:
    """Result of running the asymmetry monitor."""
    flagged_nodes: List[AsymmetryFlag]
    total_checked: int
    total_flagged: int
    threshold_used: float
    high_risk_count: int = 0
    medium_risk_count: int = 0
    low_risk_count: int = 0

    def __post_init__(self):
        """Compute risk counts."""
        self.high_risk_count = sum(1 for n in self.flagged_nodes if n.risk_level == AsymmetryRisk.HIGH)
        self.medium_risk_count = sum(1 for n in self.flagged_nodes if n.risk_level == AsymmetryRisk.MEDIUM)
        self.low_risk_count = sum(1 for n in self.flagged_nodes if n.risk_level == AsymmetryRisk.LOW)

    def to_dict(self) -> Dict:
        return {
            "flagged_nodes": [n.to_dict() for n in self.flagged_nodes],
            "total_checked": self.total_checked,
            "total_flagged": self.total_flagged,
            "threshold_used": self.threshold_used,
            "risk_summary": {
                "high": self.high_risk_count,
                "medium": self.medium_risk_count,
                "low": self.low_risk_count,
            },
        }

    @property
    def has_flags(self) -> bool:
        return self.total_flagged > 0

    def get_high_risk(self) -> List[AsymmetryFlag]:
        """Get high-risk flagged nodes."""
        return [n for n in self.flagged_nodes if n.risk_level == AsymmetryRisk.HIGH]


def run_asymmetry_monitor(
    web: Any,
    threshold: float = 3.0,
    epsilon: float = 0.01,
    entrenchment_scores: Optional[Dict[str, float]] = None,
    direct_evidence_counts: Optional[Dict[str, int]] = None,
    source_quality_scores: Optional[Dict[str, float]] = None,
    coherence_link_counts: Optional[Dict[str, int]] = None,
) -> AsymmetryResult:
    """
    Identify nodes with high entrenchment but weak direct evidence.

    A high asymmetry ratio indicates that a belief's credence comes primarily
    from network coherence rather than direct empirical support. Such beliefs
    are epistemically vulnerable to network restructuring.

    Args:
        web: The web-of-belief graph. Can be None if all data provided.
        threshold: Minimum entrenchment/evidence ratio to flag (default 3.0)
        epsilon: Small value to avoid division by zero (default 0.01)
        entrenchment_scores: Optional pre-computed {node_id: entrenchment}
        direct_evidence_counts: Optional {node_id: number of direct studies}
        source_quality_scores: Optional {node_id: quality-weighted evidence score}
        coherence_link_counts: Optional {node_id: number of coherence links}

    Returns:
        AsymmetryResult with flagged nodes and risk distribution.

    Example:
        >>> entrenchment = {"A": 0.9, "B": 0.3, "C": 0.8}
        >>> evidence = {"A": 10, "B": 2, "C": 1}  # C has high entrenchment, low evidence
        >>> result = run_asymmetry_monitor(None, entrenchment_scores=entrenchment,
        ...                                 direct_evidence_counts=evidence)
        >>> # C should be flagged (0.8 entrenchment / 1 study = 0.8 ratio > threshold)
    """
    flagged_nodes: List[AsymmetryFlag] = []

    # Get data from web if not provided
    if entrenchment_scores is None:
        entrenchment_scores = _extract_entrenchment(web)
    if direct_evidence_counts is None:
        direct_evidence_counts = _extract_evidence_counts(web)
    if coherence_link_counts is None:
        coherence_link_counts = _extract_coherence_counts(web)

    # Get all nodes to check
    all_nodes = set(entrenchment_scores.keys())

    for node_id in all_nodes:
        entrenchment = entrenchment_scores.get(node_id, 0.0)
        direct_count = direct_evidence_counts.get(node_id, 0)
        coherence_count = coherence_link_counts.get(node_id, 0)

        # Compute direct evidence score
        # Use source quality if available, otherwise just count
        if source_quality_scores and node_id in source_quality_scores:
            direct_evidence_score = source_quality_scores[node_id]
        else:
            # Normalize count to [0, 1] scale (assuming 10+ studies = 1.0)
            direct_evidence_score = min(1.0, direct_count / 10.0)

        # Compute asymmetry ratio
        asymmetry_ratio = entrenchment / max(direct_evidence_score, epsilon)

        # Flag if above threshold
        if asymmetry_ratio > threshold:
            risk_level = _classify_risk(asymmetry_ratio)
            recommendation = _generate_recommendation(
                asymmetry_ratio, direct_count, coherence_count
            )

            flagged_nodes.append(AsymmetryFlag(
                node_id=node_id,
                entrenchment_score=entrenchment,
                direct_evidence_score=direct_evidence_score,
                asymmetry_ratio=asymmetry_ratio,
                risk_level=risk_level,
                coherence_link_count=coherence_count,
                direct_study_count=direct_count,
                recommendation=recommendation,
            ))

    # Sort by asymmetry ratio (highest first)
    flagged_nodes.sort(key=lambda x: x.asymmetry_ratio, reverse=True)

    return AsymmetryResult(
        flagged_nodes=flagged_nodes,
        total_checked=len(all_nodes),
        total_flagged=len(flagged_nodes),
        threshold_used=threshold,
    )


def _classify_risk(ratio: float) -> AsymmetryRisk:
    """Classify risk level based on asymmetry ratio."""
    if ratio > 5.0:
        return AsymmetryRisk.HIGH
    elif ratio > 3.0:
        return AsymmetryRisk.MEDIUM
    else:
        return AsymmetryRisk.LOW


def _generate_recommendation(
    ratio: float,
    direct_count: int,
    coherence_count: int
) -> str:
    """Generate actionable recommendation based on asymmetry pattern."""
    if direct_count == 0:
        return "CRITICAL: No direct empirical support. Needs primary evidence."
    elif direct_count == 1:
        return "Needs independent replication from different lab/paradigm."
    elif ratio > 5.0:
        return "High coherence reliance. Seek diverse methodological approaches."
    else:
        return "Moderate asymmetry. Consider additional direct evidence."


def _extract_entrenchment(web: Any) -> Dict[str, float]:
    """Extract entrenchment scores from web object."""
    scores: Dict[str, float] = {}

    if web is None:
        return scores

    # Try different API patterns
    if hasattr(web, 'get_entrenchment_scores'):
        try:
            return web.get_entrenchment_scores()
        except Exception:
            pass

    if hasattr(web, 'beliefs'):
        try:
            for belief in web.beliefs:
                if hasattr(belief, 'belief_id') and hasattr(belief, 'entrenchment'):
                    scores[belief.belief_id] = belief.entrenchment
                elif hasattr(belief, 'id') and hasattr(belief, 'entrenchment'):
                    scores[belief.id] = belief.entrenchment
        except Exception:
            pass

    if hasattr(web, 'nodes'):
        try:
            for node_id, node in web.nodes.items():
                if hasattr(node, 'entrenchment'):
                    scores[node_id] = node.entrenchment
        except Exception:
            pass

    return scores


def _extract_evidence_counts(web: Any) -> Dict[str, int]:
    """Extract direct evidence counts from web object."""
    counts: Dict[str, int] = {}

    if web is None:
        return counts

    # Try to count supporting studies per belief
    if hasattr(web, 'beliefs'):
        try:
            for belief in web.beliefs:
                belief_id = getattr(belief, 'belief_id', getattr(belief, 'id', None))
                if belief_id:
                    # Count sources if available
                    sources = getattr(belief, 'source_ids', [])
                    if not sources:
                        sources = getattr(belief, 'sources', [])
                    counts[belief_id] = len(sources) if sources else 0
        except Exception:
            pass

    return counts


def _extract_coherence_counts(web: Any) -> Dict[str, int]:
    """Extract coherence link counts from web object."""
    counts: Dict[str, int] = {}

    if web is None:
        return counts

    # Try different API patterns
    if hasattr(web, 'constraints'):
        try:
            for constraint in web.constraints:
                source = getattr(constraint, 'source_belief_id', None)
                target = getattr(constraint, 'target_belief_id', None)
                if source:
                    counts[source] = counts.get(source, 0) + 1
                if target:
                    counts[target] = counts.get(target, 0) + 1
        except Exception:
            pass

    if hasattr(web, 'edges'):
        try:
            for edge in web.edges:
                if isinstance(edge, tuple):
                    source, target = edge[0], edge[1]
                else:
                    source = getattr(edge, 'source', None)
                    target = getattr(edge, 'target', None)
                if source:
                    counts[source] = counts.get(source, 0) + 1
                if target:
                    counts[target] = counts.get(target, 0) + 1
        except Exception:
            pass

    return counts
