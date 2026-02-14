"""
Base Entrenchment Computation by Node Type (Sprint 6b / Task 6b.1).

Implements per-type entrenchment computation per spec §4.2.
Different node types earn entrenchment differently:
- Empirical findings: from source quality and replication
- Theoretical propositions: from prediction accuracy (asymmetric)
- Synthesis conclusions: from included studies (with floor rule)
- Expert synthesis: discounted relative to systematic synthesis

Reference: Non_Empirical_Web_Integration_Spec_V1.0.md §4.2
"""

from dataclasses import dataclass
from typing import Optional, Dict
from enum import Enum

from src.epistemic.node_types import NodeType


# =============================================================================
# BASE ENTRENCHMENT VALUES (Spec §4.2)
# =============================================================================

BASE_ENTRENCHMENT: Dict[NodeType, float] = {
    # Family A: Evidence Nodes
    NodeType.EMPIRICAL_FINDING: 0.50,       # From source_quality score
    NodeType.SYNTHESIS_CONCLUSION: 0.75,     # High base, modifiers apply
    NodeType.QUALITATIVE_FINDING: 0.50,      # Midpoint of 0.40-0.60

    # Family B: Structural Nodes
    NodeType.THEORETICAL_PROPOSITION: 0.35,  # Low base, gains from predictions
    NodeType.DERIVED_HYPOTHESIS: 0.35,       # Inherits from parent
    NodeType.CONCEPTUAL_DEFINITION: 0.80,    # High (definitions are confident)
    NodeType.CONCEPTUAL_CONSTRAINT: 0.70,    # Midpoint of 0.60-0.85

    # Family C: Interpretive Nodes
    NodeType.EXPERT_SYNTHESIS: 0.45,         # Low (non-systematic selection)
    NodeType.METHODOLOGICAL_CRITIQUE: 0.55,  # Midpoint of 0.40-0.70

    # Family D: Gap Nodes
    NodeType.KNOWLEDGE_GAP: None,            # N/A - gaps don't have entrenchment

    # Family E: Meta-Nodes
    NodeType.FRAMEWORK_STRUCTURE: 0.75,      # Midpoint of 0.65-0.85
    NodeType.BRIDGE_WARRANT: 0.45,           # Midpoint of 0.30-0.60
}


# =============================================================================
# ENTRENCHMENT PARAMETERS
# =============================================================================

@dataclass
class EntrenchmentParams:
    """
    Parameters affecting entrenchment computation.

    Different node types use different subsets of these parameters.
    """
    # === SYNTHESIS_CONCLUSION parameters ===
    heterogeneity_i2: Optional[float] = None  # [0, 100] - I² statistic
    publication_bias: Optional[str] = None     # "none" | "marginal" | "significant"
    grade_quality: Optional[str] = None        # "high" | "moderate" | "low"
    n_included_studies: Optional[int] = None

    # === THEORETICAL_PROPOSITION parameters ===
    argument_quality: Optional[str] = None     # "valid_supported" | "valid_questionable" | "gaps"
    evidential_grounding: Optional[str] = None # "strong" | "some" | "weak"
    testability: Optional[str] = None          # "clear" | "difficult"

    # === QUALITATIVE_FINDING parameters ===
    convergence_level: Optional[float] = None  # [0, 1] - participant convergence
    triangulation: Optional[bool] = None
    saturation: Optional[bool] = None

    # === EXPERT_SYNTHESIS parameters ===
    author_expertise: Optional[str] = None     # "established" | "emerging" | "unknown"
    consistent_with_systematic: Optional[bool] = None

    # === METHODOLOGICAL_CRITIQUE parameters ===
    critique_adopted: Optional[bool] = None
    empirical_demonstration: Optional[bool] = None

    # === General parameters ===
    source_quality_score: Optional[float] = None  # [0, 1] from source quality computation
    replication_count: Optional[int] = None
    coherence_score: Optional[float] = None


# =============================================================================
# ENTRENCHMENT COMPUTATION
# =============================================================================

def compute_base_entrenchment(node_type: NodeType) -> Optional[float]:
    """
    Get base entrenchment for a node type.

    Args:
        node_type: The type of node

    Returns:
        Base entrenchment value, or None for KNOWLEDGE_GAP
    """
    return BASE_ENTRENCHMENT.get(node_type)


def compute_entrenchment_with_modifiers(
    node_type: NodeType,
    params: Optional[EntrenchmentParams] = None
) -> Optional[float]:
    """
    Compute entrenchment with type-specific modifiers.

    Args:
        node_type: The type of node
        params: Parameters for computing modifiers

    Returns:
        Modified entrenchment value, or None for KNOWLEDGE_GAP
    """
    if node_type == NodeType.KNOWLEDGE_GAP:
        return None

    base = BASE_ENTRENCHMENT.get(node_type, 0.50)

    if params is None:
        return base

    # Apply type-specific modifiers
    if node_type == NodeType.EMPIRICAL_FINDING:
        base = _compute_empirical_entrenchment(base, params)
    elif node_type == NodeType.SYNTHESIS_CONCLUSION:
        base = _compute_synthesis_base_entrenchment(base, params)
    elif node_type == NodeType.QUALITATIVE_FINDING:
        base = _compute_qualitative_entrenchment(base, params)
    elif node_type == NodeType.THEORETICAL_PROPOSITION:
        base = _compute_theoretical_entrenchment(base, params)
    elif node_type == NodeType.EXPERT_SYNTHESIS:
        base = _compute_expert_synthesis_entrenchment(base, params)
    elif node_type == NodeType.METHODOLOGICAL_CRITIQUE:
        base = _compute_critique_entrenchment(base, params)

    return max(0.0, min(1.0, base))


def _compute_empirical_entrenchment(base: float, params: EntrenchmentParams) -> float:
    """
    Compute entrenchment for EMPIRICAL_FINDING.

    Base: from source_quality score
    Gains: replication (+), coherence with other findings (+)
    Loses: failed replication (-), methodological critique (-)
    """
    if params.source_quality_score is not None:
        base = params.source_quality_score

    if params.replication_count is not None and params.replication_count > 0:
        base += 0.05 * min(params.replication_count, 3)  # Cap at +0.15

    if params.coherence_score is not None:
        base += (params.coherence_score - 0.5) * 0.1  # +/- 0.05

    return base


def _compute_synthesis_base_entrenchment(base: float, params: EntrenchmentParams) -> float:
    """
    Compute base entrenchment for SYNTHESIS_CONCLUSION (before floor rule).

    Base: 0.75 (0.65-0.80 depending on quality)
    Modifiers: heterogeneity, publication bias, GRADE quality
    """
    # Heterogeneity penalty
    if params.heterogeneity_i2 is not None:
        if params.heterogeneity_i2 > 75:
            base -= 0.15
        elif params.heterogeneity_i2 > 50:
            base -= 0.05

    # Publication bias penalty
    if params.publication_bias == "significant":
        base -= 0.10
    elif params.publication_bias == "marginal":
        base -= 0.05

    # GRADE quality bonus/penalty
    if params.grade_quality == "high":
        base += 0.05
    elif params.grade_quality == "low":
        base -= 0.05

    return base


def _compute_qualitative_entrenchment(base: float, params: EntrenchmentParams) -> float:
    """
    Compute entrenchment for QUALITATIVE_FINDING.

    Base: 0.40-0.60 depending on rigor
    Gains: triangulation, participant convergence, saturation
    """
    if params.triangulation:
        base += 0.05

    if params.saturation:
        base += 0.05

    if params.convergence_level is not None:
        base += (params.convergence_level - 0.5) * 0.1

    return base


def _compute_theoretical_entrenchment(base: float, params: EntrenchmentParams) -> float:
    """
    Compute base entrenchment for THEORETICAL_PROPOSITION.

    Base: 0.30-0.55 depending on argument quality
    Note: Confirmation/disconfirmation handled separately in theory_updating.py
    """
    # Argument quality
    if params.argument_quality == "valid_supported":
        base += 0.15
    elif params.argument_quality == "valid_questionable":
        base += 0.05
    elif params.argument_quality == "gaps":
        base -= 0.10

    # Evidential grounding
    if params.evidential_grounding == "strong":
        base += 0.10
    elif params.evidential_grounding == "some":
        base += 0.05

    # Testability
    if params.testability == "clear":
        base += 0.05
    elif params.testability == "difficult":
        base -= 0.05

    return base


def _compute_expert_synthesis_entrenchment(base: float, params: EntrenchmentParams) -> float:
    """
    Compute entrenchment for EXPERT_SYNTHESIS.

    Base: 0.35-0.55 (lower than systematic)
    """
    if params.author_expertise == "established":
        base += 0.10
    elif params.author_expertise == "emerging":
        base += 0.05

    if params.consistent_with_systematic:
        base += 0.10

    return base


def _compute_critique_entrenchment(base: float, params: EntrenchmentParams) -> float:
    """
    Compute entrenchment for METHODOLOGICAL_CRITIQUE.

    Base: 0.40-0.70 depending on argument quality and uptake
    """
    if params.critique_adopted:
        base += 0.10

    if params.empirical_demonstration:
        base += 0.10

    return base


# =============================================================================
# ENTRENCHMENT RANGE VALIDATION
# =============================================================================

ENTRENCHMENT_RANGES: Dict[NodeType, tuple] = {
    NodeType.EMPIRICAL_FINDING: (0.0, 1.0),
    NodeType.SYNTHESIS_CONCLUSION: (0.65, 0.80),
    NodeType.QUALITATIVE_FINDING: (0.40, 0.60),
    NodeType.THEORETICAL_PROPOSITION: (0.30, 0.55),
    NodeType.DERIVED_HYPOTHESIS: (0.30, 0.70),
    NodeType.CONCEPTUAL_DEFINITION: (0.70, 0.90),
    NodeType.CONCEPTUAL_CONSTRAINT: (0.60, 0.85),
    NodeType.EXPERT_SYNTHESIS: (0.35, 0.55),
    NodeType.METHODOLOGICAL_CRITIQUE: (0.40, 0.70),
    NodeType.FRAMEWORK_STRUCTURE: (0.65, 0.85),
    NodeType.BRIDGE_WARRANT: (0.30, 0.60),
}


def get_entrenchment_range(node_type: NodeType) -> Optional[tuple]:
    """Get the valid entrenchment range for a node type."""
    return ENTRENCHMENT_RANGES.get(node_type)
