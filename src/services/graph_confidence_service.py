"""
Graph Confidence Service (ARCH-4 Phase P5: Pearl Integration).

Computes confidence-weighted causal inference from epistemic state.
This service bridges the epistemic layer (P2-P4) with the causal layer (BN).

Key Concepts (per panel consultation 2026-02-12):

Pearl's requirement: NOT binary "is this edge warranted?" but a DISTRIBUTION

P(Y | do(X=x), confidence) = Σ_G P(Y | do(X=x), G) × P(G | beliefs)

Where:
- G = graph structure (one of many possible)
- P(G | beliefs) = distribution over graphs from epistemic layer

Panel Requirements:
- P5.1: Create GraphConfidenceService class
- P5.2: Edge confidence from warrant + rank
- P5.3: Structure uncertainty quantification
- P5.4: Identifiability check (basic)

Epistemic ↔ Causal Mapping (per Haack-Pearl resolution):
- Epistemic Grounding ↔ Causal Identifiability
- Epistemic Coherence ↔ Causal Graph Consistency
- Epistemic Warrant ↔ Causal Effect Estimate Confidence

References:
- Pearl, J. (2000). Causality: Models, Reasoning, and Inference.
- Pearl, J. (2009). Causal inference in statistics: An overview.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple, Any, TYPE_CHECKING
from enum import Enum
import logging
import math

if TYPE_CHECKING:
    from src.services.web_of_belief import WebOfBelief

from src.services.ranking_service import RankPair
from src.services.grounding_service import FoundherentistScore, JustificationStatus

logger = logging.getLogger(__name__)


class IdentifiabilityStatus(str, Enum):
    """Status of causal effect identifiability."""
    IDENTIFIABLE = "IDENTIFIABLE"           # Effect can be estimated
    UNIDENTIFIABLE = "UNIDENTIFIABLE"       # Effect cannot be estimated (confounding)
    PARTIALLY_IDENTIFIABLE = "PARTIALLY"    # Bounds can be computed
    UNKNOWN = "UNKNOWN"                     # Insufficient information


@dataclass
class EdgeConfidence:
    """
    Confidence assessment for a causal edge.

    Combines epistemic warrant with grounding to produce
    edge-level confidence for causal inference.
    """
    source: str
    target: str
    confidence: float                        # 0-1 overall confidence
    warrant_component: float                 # From warrant status
    grounding_component: float               # From grounding score
    rank_component: float                    # From rank firmness
    supporting_belief_ids: List[str]         # Beliefs supporting this edge
    identifiability: IdentifiabilityStatus

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "target": self.target,
            "confidence": self.confidence,
            "warrant_component": self.warrant_component,
            "grounding_component": self.grounding_component,
            "rank_component": self.rank_component,
            "supporting_belief_ids": self.supporting_belief_ids,
            "identifiability": self.identifiability.value
        }


@dataclass
class StructureUncertainty:
    """
    Quantification of uncertainty in graph structure.

    Per Pearl: We need a distribution over graphs, not a single graph.
    """
    overall_confidence: float               # 0-1 confidence in full structure
    edge_confidences: Dict[Tuple[str, str], float]  # (source, target) -> confidence
    missing_edges: List[Tuple[str, str]]    # Edges that might exist but lack evidence
    uncertain_edges: List[Tuple[str, str]]  # Edges with low confidence
    structure_entropy: float                # Information-theoretic uncertainty

    def to_dict(self) -> Dict[str, Any]:
        return {
            "overall_confidence": self.overall_confidence,
            "edge_confidences": {f"{s}->{t}": c for (s, t), c in self.edge_confidences.items()},
            "missing_edges": [f"{s}->{t}" for s, t in self.missing_edges],
            "uncertain_edges": [f"{s}->{t}" for s, t in self.uncertain_edges],
            "structure_entropy": self.structure_entropy
        }


@dataclass
class CausalEffectBounds:
    """
    Bounds on causal effect given uncertainty.

    Rather than point estimate, provides interval.
    """
    cause: str
    effect: str
    lower_bound: float
    upper_bound: float
    point_estimate: Optional[float]
    confidence: float                        # Confidence in the bounds
    identifiability: IdentifiabilityStatus

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cause": self.cause,
            "effect": self.effect,
            "lower_bound": self.lower_bound,
            "upper_bound": self.upper_bound,
            "point_estimate": self.point_estimate,
            "confidence": self.confidence,
            "identifiability": self.identifiability.value
        }


@dataclass
class GraphConfidenceResult:
    """Result from graph confidence computation."""
    edge_confidences: Dict[Tuple[str, str], EdgeConfidence]
    structure_uncertainty: StructureUncertainty
    violations: List[str]                   # INV-5 violations

    def to_dict(self) -> Dict[str, Any]:
        return {
            "edge_confidences": {
                f"{k[0]}->{k[1]}": v.to_dict()
                for k, v in self.edge_confidences.items()
            },
            "structure_uncertainty": self.structure_uncertainty.to_dict(),
            "violations": self.violations
        }


class GraphConfidenceService:
    """
    Service for computing confidence-weighted causal structure.

    Per panel requirements:
    - Edge confidence from warrant + rank + grounding
    - Structure uncertainty distribution (not point estimate)
    - Enforces INV-5: edge_confident(X,Y) → warranted(belief supporting X→Y)

    Usage:
        >>> service = GraphConfidenceService()
        >>> result = service.compute_confidence(web, ranks, warrant_result, grounding_result)
        >>> for edge, conf in result.edge_confidences.items():
        ...     print(f"{edge}: {conf.confidence:.2f}")
    """

    def __init__(
        self,
        warrant_weight: float = 0.4,
        grounding_weight: float = 0.3,
        rank_weight: float = 0.3,
        confidence_threshold: float = 0.5,   # Min confidence for "confident" edge
        uncertainty_threshold: float = 0.3   # Max entropy for "certain" structure
    ):
        self.warrant_weight = warrant_weight
        self.grounding_weight = grounding_weight
        self.rank_weight = rank_weight
        self.confidence_threshold = confidence_threshold
        self.uncertainty_threshold = uncertainty_threshold

    def compute_confidence(
        self,
        web: "WebOfBelief",
        ranks: Dict[str, RankPair],
        warranted_beliefs: Set[str],
        grounding_scores: Dict[str, FoundherentistScore],
        edge_beliefs: Optional[Dict[Tuple[str, str], List[str]]] = None
    ) -> GraphConfidenceResult:
        """
        Compute confidence for all causal edges.

        Args:
            web: WebOfBelief instance
            ranks: Current rank assignments
            warranted_beliefs: Set of warranted belief IDs
            grounding_scores: Grounding scores per belief
            edge_beliefs: Map of (source, target) -> list of supporting belief IDs

        Returns:
            GraphConfidenceResult with edge confidences and structure uncertainty
        """
        edge_beliefs = edge_beliefs or self._extract_edge_beliefs(web)

        # Compute confidence for each edge
        edge_confidences: Dict[Tuple[str, str], EdgeConfidence] = {}

        for edge, belief_ids in edge_beliefs.items():
            confidence = self._compute_edge_confidence(
                edge,
                belief_ids,
                ranks,
                warranted_beliefs,
                grounding_scores
            )
            edge_confidences[edge] = confidence

        # Compute structure uncertainty
        structure_uncertainty = self._compute_structure_uncertainty(
            edge_confidences,
            web
        )

        # Check INV-5 (BridgeCoherence)
        violations = self._check_bridge_coherence(
            edge_confidences,
            warranted_beliefs
        )

        return GraphConfidenceResult(
            edge_confidences=edge_confidences,
            structure_uncertainty=structure_uncertainty,
            violations=violations
        )

    def _extract_edge_beliefs(
        self,
        web: "WebOfBelief"
    ) -> Dict[Tuple[str, str], List[str]]:
        """
        Extract causal edges and their supporting beliefs from web.

        Looks for constraints that represent causal claims.
        """
        edge_beliefs: Dict[Tuple[str, str], List[str]] = {}

        for belief_id, belief in web.beliefs.items():
            # Check if belief has causal structure (environment_id → outcome_id)
            env_id = getattr(belief, 'environment_id', None)
            outcome_id = getattr(belief, 'outcome_id', None)

            if env_id and outcome_id:
                edge = (env_id, outcome_id)
                if edge not in edge_beliefs:
                    edge_beliefs[edge] = []
                edge_beliefs[edge].append(belief_id)

        # Also look at CAUSES constraints
        for constraint in web.constraints.values():
            ctype = constraint.constraint_type.value if hasattr(constraint.constraint_type, 'value') else str(constraint.constraint_type)
            if ctype in ("CAUSES", "EXPLAINS"):
                edge = (constraint.source_id, constraint.target_id)
                if edge not in edge_beliefs:
                    edge_beliefs[edge] = []
                # The constraint itself acts as evidence

        return edge_beliefs

    def _compute_edge_confidence(
        self,
        edge: Tuple[str, str],
        belief_ids: List[str],
        ranks: Dict[str, RankPair],
        warranted_beliefs: Set[str],
        grounding_scores: Dict[str, FoundherentistScore]
    ) -> EdgeConfidence:
        """
        Compute confidence for a single edge.

        Combines:
        - Warrant status of supporting beliefs
        - Grounding scores of supporting beliefs
        - Rank firmness of supporting beliefs
        """
        if not belief_ids:
            return EdgeConfidence(
                source=edge[0],
                target=edge[1],
                confidence=0.0,
                warrant_component=0.0,
                grounding_component=0.0,
                rank_component=0.0,
                supporting_belief_ids=[],
                identifiability=IdentifiabilityStatus.UNKNOWN
            )

        # Compute warrant component (fraction of supporting beliefs that are warranted)
        warranted_count = sum(1 for b in belief_ids if b in warranted_beliefs)
        warrant_score = warranted_count / len(belief_ids)

        # Compute grounding component (average grounding of supporting beliefs)
        grounding_scores_list = [
            grounding_scores[b].grounding_component
            for b in belief_ids
            if b in grounding_scores
        ]
        grounding_score = (
            sum(grounding_scores_list) / len(grounding_scores_list)
            if grounding_scores_list else 0.0
        )

        # Compute rank component (average firmness of supporting beliefs)
        firmness_scores = [
            ranks[b].firmness / 10  # Normalize to 0-1
            for b in belief_ids
            if b in ranks
        ]
        rank_score = (
            sum(firmness_scores) / len(firmness_scores)
            if firmness_scores else 0.0
        )

        # Combine scores
        confidence = (
            self.warrant_weight * warrant_score +
            self.grounding_weight * grounding_score +
            self.rank_weight * rank_score
        )

        # Determine identifiability
        identifiability = self._assess_identifiability(
            edge, belief_ids, grounding_scores
        )

        return EdgeConfidence(
            source=edge[0],
            target=edge[1],
            confidence=confidence,
            warrant_component=warrant_score,
            grounding_component=grounding_score,
            rank_component=rank_score,
            supporting_belief_ids=belief_ids,
            identifiability=identifiability
        )

    def _assess_identifiability(
        self,
        edge: Tuple[str, str],
        belief_ids: List[str],
        grounding_scores: Dict[str, FoundherentistScore]
    ) -> IdentifiabilityStatus:
        """
        Assess causal effect identifiability.

        Per Haack-Pearl mapping:
        - Well-grounded beliefs → identifiable effects
        - Ungrounded beliefs → unidentifiable effects
        """
        if not belief_ids:
            return IdentifiabilityStatus.UNKNOWN

        # Check grounding status of supporting beliefs
        justification_statuses = [
            grounding_scores[b].justification_status
            for b in belief_ids
            if b in grounding_scores
        ]

        if not justification_statuses:
            return IdentifiabilityStatus.UNKNOWN

        well_justified = sum(
            1 for s in justification_statuses
            if s == JustificationStatus.WELL_JUSTIFIED
        )
        grounded = sum(
            1 for s in justification_statuses
            if s in (JustificationStatus.WELL_JUSTIFIED, JustificationStatus.GROUNDED_ONLY)
        )

        fraction_justified = well_justified / len(justification_statuses)
        fraction_grounded = grounded / len(justification_statuses)

        if fraction_justified > 0.7:
            return IdentifiabilityStatus.IDENTIFIABLE
        elif fraction_grounded > 0.5:
            return IdentifiabilityStatus.PARTIALLY_IDENTIFIABLE
        else:
            return IdentifiabilityStatus.UNIDENTIFIABLE

    def _compute_structure_uncertainty(
        self,
        edge_confidences: Dict[Tuple[str, str], EdgeConfidence],
        web: "WebOfBelief"
    ) -> StructureUncertainty:
        """
        Compute overall structure uncertainty.

        Uses information-theoretic entropy to quantify uncertainty
        in the graph structure.
        """
        if not edge_confidences:
            return StructureUncertainty(
                overall_confidence=0.0,
                edge_confidences={},
                missing_edges=[],
                uncertain_edges=[],
                structure_entropy=1.0
            )

        # Collect edge confidence values
        conf_values = [ec.confidence for ec in edge_confidences.values()]

        # Overall confidence is geometric mean (penalizes weak edges)
        if conf_values:
            log_sum = sum(math.log(max(0.01, c)) for c in conf_values)
            overall_confidence = math.exp(log_sum / len(conf_values))
        else:
            overall_confidence = 0.0

        # Identify uncertain edges
        uncertain_edges = [
            edge for edge, ec in edge_confidences.items()
            if ec.confidence < self.confidence_threshold
        ]

        # Compute entropy from edge confidence distribution
        # H = -Σ p log p where p = confidence / total
        total_conf = sum(conf_values) or 1.0
        entropy = 0.0
        for c in conf_values:
            if c > 0:
                p = c / total_conf
                entropy -= p * math.log2(p)

        # Normalize entropy to 0-1 (max entropy is log2(n))
        max_entropy = math.log2(max(1, len(conf_values)))
        normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0.0

        return StructureUncertainty(
            overall_confidence=overall_confidence,
            edge_confidences={edge: ec.confidence for edge, ec in edge_confidences.items()},
            missing_edges=[],  # Would require domain knowledge to populate
            uncertain_edges=uncertain_edges,
            structure_entropy=normalized_entropy
        )

    def _check_bridge_coherence(
        self,
        edge_confidences: Dict[Tuple[str, str], EdgeConfidence],
        warranted_beliefs: Set[str]
    ) -> List[str]:
        """
        Check INV-5: edge_confident(X,Y) → warranted(belief supporting X→Y)

        Returns list of violation messages.
        """
        violations = []

        for edge, ec in edge_confidences.items():
            if ec.confidence >= self.confidence_threshold:
                # Edge is confident - check that it has warranted support
                has_warranted_support = any(
                    b in warranted_beliefs
                    for b in ec.supporting_belief_ids
                )

                if not has_warranted_support:
                    violations.append(
                        f"INV-5 violation: Edge {edge[0]}→{edge[1]} has "
                        f"confidence {ec.confidence:.2f} but no warranted supporting beliefs"
                    )

        return violations

    def compute_causal_effect_bounds(
        self,
        cause: str,
        effect: str,
        edge_confidences: Dict[Tuple[str, str], EdgeConfidence],
        base_effect_size: float = 0.0,
        max_effect_size: float = 1.0
    ) -> CausalEffectBounds:
        """
        Compute bounds on causal effect given uncertainty.

        Args:
            cause: Cause variable ID
            effect: Effect variable ID
            edge_confidences: Edge confidence data
            base_effect_size: Baseline effect estimate
            max_effect_size: Maximum possible effect

        Returns:
            CausalEffectBounds with interval estimate
        """
        edge = (cause, effect)
        ec = edge_confidences.get(edge)

        if not ec:
            return CausalEffectBounds(
                cause=cause,
                effect=effect,
                lower_bound=0.0,
                upper_bound=max_effect_size,
                point_estimate=None,
                confidence=0.0,
                identifiability=IdentifiabilityStatus.UNKNOWN
            )

        # Bounds contract with confidence
        uncertainty = 1 - ec.confidence
        range_expansion = (max_effect_size - base_effect_size) * uncertainty

        lower = max(0.0, base_effect_size - range_expansion)
        upper = min(max_effect_size, base_effect_size + range_expansion)

        point_estimate = base_effect_size if ec.identifiability == IdentifiabilityStatus.IDENTIFIABLE else None

        return CausalEffectBounds(
            cause=cause,
            effect=effect,
            lower_bound=lower,
            upper_bound=upper,
            point_estimate=point_estimate,
            confidence=ec.confidence,
            identifiability=ec.identifiability
        )


# ============================================================
# CONVENIENCE FUNCTIONS
# ============================================================

def compute_graph_confidence(
    web: "WebOfBelief",
    ranks: Dict[str, RankPair],
    warranted_beliefs: Set[str],
    grounding_scores: Dict[str, FoundherentistScore]
) -> GraphConfidenceResult:
    """
    Convenience function to compute graph confidence.

    Args:
        web: WebOfBelief instance
        ranks: Current rank assignments
        warranted_beliefs: Set of warranted belief IDs
        grounding_scores: Grounding scores per belief

    Returns:
        GraphConfidenceResult
    """
    service = GraphConfidenceService()
    return service.compute_confidence(web, ranks, warranted_beliefs, grounding_scores)
