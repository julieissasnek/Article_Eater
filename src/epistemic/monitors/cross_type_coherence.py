"""
Cross-Type Coherence Monitor (Sprint 6d / Task 6d.2).

Computes coherence relationships between different node types in the web.
Different node type pairs have different coherence semantics:
- THEORETICAL_PROPOSITION ↔ EMPIRICAL_FINDING: prediction/confirmation
- SYNTHESIS_CONCLUSION ↔ EMPIRICAL_FINDING: aggregation coherence
- EXPERT_SYNTHESIS ↔ SYNTHESIS_CONCLUSION: interpretation alignment

Per spec §5.2:
"The system should track how well theoretical structures cohere with
empirical evidence, and flag theories that lack empirical grounding
or evidence that lacks theoretical interpretation."

Reference: Non_Empirical_Web_Integration_Spec_V1.0.md §5.2
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any
from enum import Enum
from datetime import datetime

from src.epistemic.node_types import NodeType, NodeTypeFamily, get_node_type_family


class CoherenceType(str, Enum):
    """Types of cross-type coherence relationships."""
    THEORY_EVIDENCE = "theory_evidence"           # Theory ↔ empirical support
    SYNTHESIS_PRIMARY = "synthesis_primary"       # Synthesis ↔ included studies
    INTERPRETATION_DATA = "interpretation_data"  # Expert synthesis ↔ evidence
    HYPOTHESIS_TEST = "hypothesis_test"          # Hypothesis ↔ confirming studies
    CRITIQUE_TARGET = "critique_target"          # Critique ↔ affected claims
    DEFINITION_USAGE = "definition_usage"        # Definition ↔ nodes using it


class CoherenceAnomaly(str, Enum):
    """Types of coherence anomalies."""
    UNGROUNDED_THEORY = "ungrounded_theory"               # Theory with no evidence
    UNINTERPRETED_EVIDENCE = "uninterpreted_evidence"     # Evidence without theory
    ORPHAN_SYNTHESIS = "orphan_synthesis"                 # Synthesis with no primaries
    CONTRADICTED_SYNTHESIS = "contradicted_synthesis"     # Synthesis contradicted by new data
    UNTESTED_HYPOTHESIS = "untested_hypothesis"           # Hypothesis with no tests
    ISOLATED_DEFINITION = "isolated_definition"           # Definition not used
    DISCONNECTED_CRITIQUE = "disconnected_critique"       # Critique not linked to targets


@dataclass
class CrossTypeCoherenceScore:
    """Coherence score between two node types."""
    source_node_id: str
    source_node_type: NodeType
    target_node_id: str
    target_node_type: NodeType
    coherence_type: CoherenceType
    score: float  # 0.0 (incoherent) to 1.0 (highly coherent)
    edge_types_present: List[str] = field(default_factory=list)
    edge_count: int = 0
    explanation: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "source_node_id": self.source_node_id,
            "source_node_type": self.source_node_type.value,
            "target_node_id": self.target_node_id,
            "target_node_type": self.target_node_type.value,
            "coherence_type": self.coherence_type.value,
            "score": self.score,
            "edge_types_present": self.edge_types_present,
            "edge_count": self.edge_count,
            "explanation": self.explanation,
        }


@dataclass
class CoherenceAnomalyReport:
    """Report of a coherence anomaly."""
    node_id: str
    node_type: NodeType
    anomaly_type: CoherenceAnomaly
    severity: float  # 0.0 (minor) to 1.0 (critical)
    description: str
    suggested_action: str
    related_nodes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "node_id": self.node_id,
            "node_type": self.node_type.value,
            "anomaly_type": self.anomaly_type.value,
            "severity": self.severity,
            "description": self.description,
            "suggested_action": self.suggested_action,
            "related_nodes": self.related_nodes,
        }


@dataclass
class WebCoherenceReport:
    """Overall coherence report for the web."""
    total_nodes: int
    nodes_by_type: Dict[str, int]
    cross_type_scores: List[CrossTypeCoherenceScore]
    anomalies: List[CoherenceAnomalyReport]
    mean_theory_evidence_coherence: float
    mean_synthesis_primary_coherence: float
    ungrounded_theory_count: int
    uninterpreted_evidence_count: int
    generated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "total_nodes": self.total_nodes,
            "nodes_by_type": self.nodes_by_type,
            "cross_type_scores": [s.to_dict() for s in self.cross_type_scores],
            "anomalies": [a.to_dict() for a in self.anomalies],
            "mean_theory_evidence_coherence": self.mean_theory_evidence_coherence,
            "mean_synthesis_primary_coherence": self.mean_synthesis_primary_coherence,
            "ungrounded_theory_count": self.ungrounded_theory_count,
            "uninterpreted_evidence_count": self.uninterpreted_evidence_count,
            "generated_at": self.generated_at.isoformat(),
        }


# =============================================================================
# COHERENCE WEIGHTS FOR NODE TYPE PAIRS
# =============================================================================

# Weights for different coherence relationships
# Higher weight = more important for overall web coherence
COHERENCE_WEIGHTS: Dict[Tuple[NodeTypeFamily, NodeTypeFamily], float] = {
    # Structural-Evidence coherence is most important
    (NodeTypeFamily.STRUCTURAL, NodeTypeFamily.EVIDENCE): 1.0,
    (NodeTypeFamily.EVIDENCE, NodeTypeFamily.STRUCTURAL): 1.0,

    # Interpretive-Evidence coherence matters for expert synthesis
    (NodeTypeFamily.INTERPRETIVE, NodeTypeFamily.EVIDENCE): 0.7,
    (NodeTypeFamily.EVIDENCE, NodeTypeFamily.INTERPRETIVE): 0.7,

    # Meta-Structural coherence for framework organization
    (NodeTypeFamily.META, NodeTypeFamily.STRUCTURAL): 0.6,
    (NodeTypeFamily.STRUCTURAL, NodeTypeFamily.META): 0.6,

    # Gap-Evidence (gaps should point to evidence boundaries)
    (NodeTypeFamily.GAP, NodeTypeFamily.EVIDENCE): 0.5,
    (NodeTypeFamily.EVIDENCE, NodeTypeFamily.GAP): 0.5,

    # Within-family coherence (theories with theories, etc.)
    (NodeTypeFamily.STRUCTURAL, NodeTypeFamily.STRUCTURAL): 0.8,
    (NodeTypeFamily.EVIDENCE, NodeTypeFamily.EVIDENCE): 0.6,
    (NodeTypeFamily.INTERPRETIVE, NodeTypeFamily.INTERPRETIVE): 0.4,
}


class CrossTypeCoherenceMonitor:
    """
    Monitors coherence relationships between different node types.

    Tracks how well theoretical structures cohere with empirical evidence,
    how syntheses cohere with primary studies, and identifies structural
    anomalies in the web.
    """

    def __init__(self):
        self._nodes: Dict[str, Tuple[NodeType, Any]] = {}
        self._edges: List[Dict[str, Any]] = []
        self._coherence_cache: Dict[Tuple[str, str], CrossTypeCoherenceScore] = {}

    def register_node(
        self,
        node_id: str,
        node_type: NodeType,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Register a node for coherence monitoring."""
        self._nodes[node_id] = (node_type, metadata or {})

    def register_edge(
        self,
        source_id: str,
        target_id: str,
        edge_type: str,
        weight: float = 1.0
    ) -> None:
        """Register an edge between nodes."""
        self._edges.append({
            "source": source_id,
            "target": target_id,
            "edge_type": edge_type,
            "weight": weight,
        })

    def compute_pairwise_coherence(
        self,
        node_a_id: str,
        node_b_id: str
    ) -> Optional[CrossTypeCoherenceScore]:
        """
        Compute coherence score between two specific nodes.

        Args:
            node_a_id: First node ID
            node_b_id: Second node ID

        Returns:
            CrossTypeCoherenceScore or None if nodes not found
        """
        if node_a_id not in self._nodes or node_b_id not in self._nodes:
            return None

        cache_key = (node_a_id, node_b_id)
        if cache_key in self._coherence_cache:
            return self._coherence_cache[cache_key]

        node_a_type, _ = self._nodes[node_a_id]
        node_b_type, _ = self._nodes[node_b_id]

        # Determine coherence type
        coherence_type = self._determine_coherence_type(node_a_type, node_b_type)

        # Find edges between these nodes
        connecting_edges = self._find_connecting_edges(node_a_id, node_b_id)
        edge_types = [e["edge_type"] for e in connecting_edges]

        # Compute score based on edge presence and types
        score = self._compute_coherence_score(
            node_a_type, node_b_type, connecting_edges
        )

        explanation = self._generate_coherence_explanation(
            node_a_type, node_b_type, score, edge_types
        )

        result = CrossTypeCoherenceScore(
            source_node_id=node_a_id,
            source_node_type=node_a_type,
            target_node_id=node_b_id,
            target_node_type=node_b_type,
            coherence_type=coherence_type,
            score=score,
            edge_types_present=edge_types,
            edge_count=len(connecting_edges),
            explanation=explanation,
        )

        self._coherence_cache[cache_key] = result
        return result

    def _determine_coherence_type(
        self,
        type_a: NodeType,
        type_b: NodeType
    ) -> CoherenceType:
        """Determine the coherence type for a node type pair."""
        # Theory-Evidence coherence
        if type_a == NodeType.THEORETICAL_PROPOSITION:
            if type_b in {NodeType.EMPIRICAL_FINDING, NodeType.SYNTHESIS_CONCLUSION}:
                return CoherenceType.THEORY_EVIDENCE
            if type_b == NodeType.DERIVED_HYPOTHESIS:
                return CoherenceType.HYPOTHESIS_TEST

        if type_b == NodeType.THEORETICAL_PROPOSITION:
            if type_a in {NodeType.EMPIRICAL_FINDING, NodeType.SYNTHESIS_CONCLUSION}:
                return CoherenceType.THEORY_EVIDENCE

        # Synthesis-Primary coherence
        if type_a == NodeType.SYNTHESIS_CONCLUSION:
            if type_b == NodeType.EMPIRICAL_FINDING:
                return CoherenceType.SYNTHESIS_PRIMARY

        if type_b == NodeType.SYNTHESIS_CONCLUSION:
            if type_a == NodeType.EMPIRICAL_FINDING:
                return CoherenceType.SYNTHESIS_PRIMARY

        # Expert interpretation coherence
        if type_a == NodeType.EXPERT_SYNTHESIS or type_b == NodeType.EXPERT_SYNTHESIS:
            return CoherenceType.INTERPRETATION_DATA

        # Hypothesis testing coherence
        if type_a == NodeType.DERIVED_HYPOTHESIS or type_b == NodeType.DERIVED_HYPOTHESIS:
            return CoherenceType.HYPOTHESIS_TEST

        # Critique coherence
        if type_a == NodeType.METHODOLOGICAL_CRITIQUE or type_b == NodeType.METHODOLOGICAL_CRITIQUE:
            return CoherenceType.CRITIQUE_TARGET

        # Definition usage coherence
        if type_a == NodeType.CONCEPTUAL_DEFINITION or type_b == NodeType.CONCEPTUAL_DEFINITION:
            return CoherenceType.DEFINITION_USAGE

        # Default: theory-evidence
        return CoherenceType.THEORY_EVIDENCE

    def _find_connecting_edges(
        self,
        node_a_id: str,
        node_b_id: str
    ) -> List[Dict[str, Any]]:
        """Find all edges connecting two nodes (in either direction)."""
        return [
            e for e in self._edges
            if (e["source"] == node_a_id and e["target"] == node_b_id)
            or (e["source"] == node_b_id and e["target"] == node_a_id)
        ]

    def _compute_coherence_score(
        self,
        type_a: NodeType,
        type_b: NodeType,
        edges: List[Dict[str, Any]]
    ) -> float:
        """
        Compute coherence score based on node types and connecting edges.

        The score considers:
        - Presence of edges (no edges = lower coherence)
        - Types of edges (more appropriate edge types = higher coherence)
        - Edge weights (stronger edges = higher coherence)
        """
        if not edges:
            # No direct connection: low but non-zero (might have indirect)
            return 0.1

        # Base score from number of connections
        base_score = min(0.3 + 0.1 * len(edges), 0.6)

        # Bonus for appropriate edge types
        edge_type_bonus = 0.0
        for edge in edges:
            edge_type = edge["edge_type"]

            # Theory-evidence appropriate edges
            if type_a == NodeType.THEORETICAL_PROPOSITION or type_b == NodeType.THEORETICAL_PROPOSITION:
                if edge_type in {"theoretically_predicts", "confirms_prediction", "disconfirms_prediction"}:
                    edge_type_bonus += 0.15

            # Synthesis-primary appropriate edges
            if type_a == NodeType.SYNTHESIS_CONCLUSION or type_b == NodeType.SYNTHESIS_CONCLUSION:
                if edge_type == "includes_in_synthesis":
                    edge_type_bonus += 0.15
                if edge_type == "contradicts_synthesis":
                    edge_type_bonus += 0.10  # Still coherent (tracked contradiction)

            # Hypothesis testing edges
            if type_a == NodeType.DERIVED_HYPOTHESIS or type_b == NodeType.DERIVED_HYPOTHESIS:
                if edge_type in {"confirms_prediction", "disconfirms_prediction"}:
                    edge_type_bonus += 0.15

        # Weight contribution
        total_weight = sum(e.get("weight", 1.0) for e in edges)
        weight_factor = min(total_weight / len(edges), 1.0) if edges else 0.5

        score = base_score + edge_type_bonus
        score *= weight_factor

        return min(max(score, 0.0), 1.0)

    def _generate_coherence_explanation(
        self,
        type_a: NodeType,
        type_b: NodeType,
        score: float,
        edge_types: List[str]
    ) -> str:
        """Generate human-readable explanation of coherence score."""
        if score < 0.3:
            level = "low"
        elif score < 0.6:
            level = "moderate"
        else:
            level = "high"

        if not edge_types:
            return f"{level.capitalize()} coherence between {type_a.value} and {type_b.value}: no direct edges"

        edge_desc = ", ".join(set(edge_types))
        return f"{level.capitalize()} coherence between {type_a.value} and {type_b.value} via {edge_desc}"

    def detect_anomalies(self) -> List[CoherenceAnomalyReport]:
        """
        Detect structural anomalies in the web coherence.

        Returns list of anomaly reports.
        """
        anomalies: List[CoherenceAnomalyReport] = []

        # Check for ungrounded theories
        anomalies.extend(self._detect_ungrounded_theories())

        # Check for uninterpreted evidence
        anomalies.extend(self._detect_uninterpreted_evidence())

        # Check for orphan syntheses
        anomalies.extend(self._detect_orphan_syntheses())

        # Check for untested hypotheses
        anomalies.extend(self._detect_untested_hypotheses())

        # Check for isolated definitions
        anomalies.extend(self._detect_isolated_definitions())

        return anomalies

    def _detect_ungrounded_theories(self) -> List[CoherenceAnomalyReport]:
        """Detect theories without empirical support."""
        anomalies = []

        for node_id, (node_type, _) in self._nodes.items():
            if node_type != NodeType.THEORETICAL_PROPOSITION:
                continue

            # Check for evidence connections
            has_evidence = False
            for edge in self._edges:
                if edge["source"] == node_id or edge["target"] == node_id:
                    # Check if connected to evidence
                    other_id = edge["target"] if edge["source"] == node_id else edge["source"]
                    if other_id in self._nodes:
                        other_type, _ = self._nodes[other_id]
                        if other_type in {NodeType.EMPIRICAL_FINDING, NodeType.SYNTHESIS_CONCLUSION, NodeType.DERIVED_HYPOTHESIS}:
                            has_evidence = True
                            break

            if not has_evidence:
                anomalies.append(CoherenceAnomalyReport(
                    node_id=node_id,
                    node_type=node_type,
                    anomaly_type=CoherenceAnomaly.UNGROUNDED_THEORY,
                    severity=0.7,
                    description=f"Theory '{node_id}' has no empirical connections",
                    suggested_action="Derive testable hypotheses or link to supporting evidence",
                ))

        return anomalies

    def _detect_uninterpreted_evidence(self) -> List[CoherenceAnomalyReport]:
        """Detect evidence without theoretical interpretation."""
        anomalies = []

        for node_id, (node_type, _) in self._nodes.items():
            if node_type not in {NodeType.EMPIRICAL_FINDING}:
                continue

            # Check for theory connections
            has_theory = False
            for edge in self._edges:
                if edge["source"] == node_id or edge["target"] == node_id:
                    other_id = edge["target"] if edge["source"] == node_id else edge["source"]
                    if other_id in self._nodes:
                        other_type, _ = self._nodes[other_id]
                        if other_type in {NodeType.THEORETICAL_PROPOSITION, NodeType.DERIVED_HYPOTHESIS, NodeType.SYNTHESIS_CONCLUSION}:
                            has_theory = True
                            break

            if not has_theory:
                anomalies.append(CoherenceAnomalyReport(
                    node_id=node_id,
                    node_type=node_type,
                    anomaly_type=CoherenceAnomaly.UNINTERPRETED_EVIDENCE,
                    severity=0.5,
                    description=f"Evidence '{node_id}' lacks theoretical interpretation",
                    suggested_action="Link to relevant theory or synthesis",
                ))

        return anomalies

    def _detect_orphan_syntheses(self) -> List[CoherenceAnomalyReport]:
        """Detect syntheses without linked primary studies."""
        anomalies = []

        for node_id, (node_type, _) in self._nodes.items():
            if node_type != NodeType.SYNTHESIS_CONCLUSION:
                continue

            # Check for INCLUDES_IN_SYNTHESIS edges
            has_primaries = False
            for edge in self._edges:
                if edge["source"] == node_id:
                    if edge["edge_type"] == "includes_in_synthesis":
                        has_primaries = True
                        break

            if not has_primaries:
                anomalies.append(CoherenceAnomalyReport(
                    node_id=node_id,
                    node_type=node_type,
                    anomaly_type=CoherenceAnomaly.ORPHAN_SYNTHESIS,
                    severity=0.6,
                    description=f"Synthesis '{node_id}' has no linked primary studies",
                    suggested_action="Link to included studies via INCLUDES_IN_SYNTHESIS edges",
                ))

        return anomalies

    def _detect_untested_hypotheses(self) -> List[CoherenceAnomalyReport]:
        """Detect hypotheses without confirming/disconfirming studies."""
        anomalies = []

        for node_id, (node_type, _) in self._nodes.items():
            if node_type != NodeType.DERIVED_HYPOTHESIS:
                continue

            # Check for test edges
            has_tests = False
            for edge in self._edges:
                if edge["target"] == node_id:
                    if edge["edge_type"] in {"confirms_prediction", "disconfirms_prediction"}:
                        has_tests = True
                        break

            if not has_tests:
                anomalies.append(CoherenceAnomalyReport(
                    node_id=node_id,
                    node_type=node_type,
                    anomaly_type=CoherenceAnomaly.UNTESTED_HYPOTHESIS,
                    severity=0.4,
                    description=f"Hypothesis '{node_id}' has no empirical tests",
                    suggested_action="Seek studies that test this prediction",
                ))

        return anomalies

    def _detect_isolated_definitions(self) -> List[CoherenceAnomalyReport]:
        """Detect definitions not used by other nodes."""
        anomalies = []

        for node_id, (node_type, _) in self._nodes.items():
            if node_type != NodeType.CONCEPTUAL_DEFINITION:
                continue

            # Check for any connections
            has_connections = any(
                edge["source"] == node_id or edge["target"] == node_id
                for edge in self._edges
            )

            if not has_connections:
                anomalies.append(CoherenceAnomalyReport(
                    node_id=node_id,
                    node_type=node_type,
                    anomaly_type=CoherenceAnomaly.ISOLATED_DEFINITION,
                    severity=0.3,
                    description=f"Definition '{node_id}' is not connected to other nodes",
                    suggested_action="Link to nodes that use this construct",
                ))

        return anomalies

    def generate_report(self) -> WebCoherenceReport:
        """
        Generate comprehensive coherence report for the web.

        Returns:
            WebCoherenceReport with statistics and anomalies
        """
        # Count nodes by type
        nodes_by_type: Dict[str, int] = {}
        for _, (node_type, _) in self._nodes.items():
            type_key = node_type.value
            nodes_by_type[type_key] = nodes_by_type.get(type_key, 0) + 1

        # Compute cross-type coherence scores
        cross_type_scores: List[CrossTypeCoherenceScore] = []

        # Sample important pairs for report
        theories = [nid for nid, (nt, _) in self._nodes.items()
                    if nt == NodeType.THEORETICAL_PROPOSITION]
        evidence = [nid for nid, (nt, _) in self._nodes.items()
                    if nt in {NodeType.EMPIRICAL_FINDING, NodeType.SYNTHESIS_CONCLUSION}]
        syntheses = [nid for nid, (nt, _) in self._nodes.items()
                     if nt == NodeType.SYNTHESIS_CONCLUSION]

        # Theory-evidence coherence
        theory_evidence_scores = []
        for t_id in theories:
            for e_id in evidence:
                score = self.compute_pairwise_coherence(t_id, e_id)
                if score:
                    cross_type_scores.append(score)
                    theory_evidence_scores.append(score.score)

        # Synthesis-primary coherence
        synthesis_primary_scores = []
        primaries = [nid for nid, (nt, _) in self._nodes.items()
                     if nt == NodeType.EMPIRICAL_FINDING]
        for s_id in syntheses:
            for p_id in primaries:
                score = self.compute_pairwise_coherence(s_id, p_id)
                if score:
                    if score not in cross_type_scores:
                        cross_type_scores.append(score)
                    synthesis_primary_scores.append(score.score)

        # Detect anomalies
        anomalies = self.detect_anomalies()

        # Compute means
        mean_theory_evidence = (
            sum(theory_evidence_scores) / len(theory_evidence_scores)
            if theory_evidence_scores else 0.0
        )
        mean_synthesis_primary = (
            sum(synthesis_primary_scores) / len(synthesis_primary_scores)
            if synthesis_primary_scores else 0.0
        )

        # Count specific anomaly types
        ungrounded_count = sum(
            1 for a in anomalies
            if a.anomaly_type == CoherenceAnomaly.UNGROUNDED_THEORY
        )
        uninterpreted_count = sum(
            1 for a in anomalies
            if a.anomaly_type == CoherenceAnomaly.UNINTERPRETED_EVIDENCE
        )

        return WebCoherenceReport(
            total_nodes=len(self._nodes),
            nodes_by_type=nodes_by_type,
            cross_type_scores=cross_type_scores,
            anomalies=anomalies,
            mean_theory_evidence_coherence=mean_theory_evidence,
            mean_synthesis_primary_coherence=mean_synthesis_primary,
            ungrounded_theory_count=ungrounded_count,
            uninterpreted_evidence_count=uninterpreted_count,
        )


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def create_coherence_monitor() -> CrossTypeCoherenceMonitor:
    """Create a cross-type coherence monitor instance."""
    return CrossTypeCoherenceMonitor()


def compute_family_coherence(
    nodes: List[Tuple[str, NodeType]],
    edges: List[Tuple[str, str, str]],
) -> Dict[Tuple[str, str], float]:
    """
    Compute coherence scores aggregated by node type family pairs.

    Args:
        nodes: List of (node_id, node_type) tuples
        edges: List of (source_id, target_id, edge_type) tuples

    Returns:
        Dict mapping (family_a, family_b) to mean coherence score
    """
    monitor = CrossTypeCoherenceMonitor()

    for node_id, node_type in nodes:
        monitor.register_node(node_id, node_type)

    for source, target, edge_type in edges:
        monitor.register_edge(source, target, edge_type)

    # Group nodes by family
    family_nodes: Dict[NodeTypeFamily, List[str]] = {}
    for node_id, node_type in nodes:
        family = get_node_type_family(node_type)
        if family not in family_nodes:
            family_nodes[family] = []
        family_nodes[family].append(node_id)

    # Compute pairwise family coherence
    family_coherence: Dict[Tuple[str, str], List[float]] = {}

    for family_a, nodes_a in family_nodes.items():
        for family_b, nodes_b in family_nodes.items():
            if family_a == family_b:
                continue

            key = (family_a.value, family_b.value)
            scores = []

            for node_a in nodes_a:
                for node_b in nodes_b:
                    score = monitor.compute_pairwise_coherence(node_a, node_b)
                    if score:
                        scores.append(score.score)

            if scores:
                if key not in family_coherence:
                    family_coherence[key] = []
                family_coherence[key].extend(scores)

    # Compute means
    return {
        key: sum(scores) / len(scores)
        for key, scores in family_coherence.items()
        if scores
    }


def get_coherence_weight(
    type_a: NodeType,
    type_b: NodeType
) -> float:
    """
    Get the coherence weight for a node type pair.

    Higher weight means this coherence relationship is more important
    for overall web health.
    """
    family_a = get_node_type_family(type_a)
    family_b = get_node_type_family(type_b)

    return COHERENCE_WEIGHTS.get(
        (family_a, family_b),
        0.5  # Default weight
    )
