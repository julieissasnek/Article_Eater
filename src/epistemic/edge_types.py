"""
Edge Type Taxonomy for Non-Empirical Web Integration (Sprint 6a / Task 6a.2).

Defines 19 new edge types for connecting non-empirical node types.
Extends the existing ConstraintType enum with specialized edge types for:
- Review/synthesis connections
- Theoretical relationships
- Conceptual links
- Critique propagation
- Attribution tracking

Reference: Non_Empirical_Web_Integration_Spec_V1.0.md §3.2
"""

from enum import Enum
from typing import Dict, List, Set
from dataclasses import dataclass


class EdgeTypeCategory(str, Enum):
    """Categories of edge types."""
    REVIEW_SYNTHESIS = "review_synthesis"
    THEORETICAL = "theoretical"
    CONCEPTUAL = "conceptual"
    CRITIQUE = "critique"
    ATTRIBUTION = "attribution"
    LEGACY = "legacy"  # Existing ConstraintType values


class EdgeType(str, Enum):
    """
    Edge types for web of belief connections.

    Per Non_Empirical_Web_Integration_Spec_V1.0.md §3.2.

    Review/Synthesis Edges:
        INCLUDES_IN_SYNTHESIS: Meta-analysis includes a study
        SYNTHESIZES_AS: Evidence direction across N studies
        IDENTIFIES_MODERATOR: Effect is moderated by X
        CONTRADICTS_SYNTHESIS: New study contradicts meta-analytic conclusion

    Theoretical Edges:
        THEORETICALLY_PREDICTS: Theory T predicts finding H
        CONFIRMS_PREDICTION: Study confirms hypothesis
        DISCONFIRMS_PREDICTION: Study disconfirms hypothesis
        PROPOSES_MECHANISM: Theory proposes mechanism M
        SUBSUMES_THEORY: Theory A subsumes Theory B
        THEORY_TENSION: Theories make incompatible predictions

    Conceptual Edges:
        DEFINES_CONSTRUCT: Definition of a construct
        MUST_DISTINGUISH: Two things must not be conflated
        REDEFINES: Newer definition supersedes older
        ORGANIZES: Taxonomy organizes constructs

    Critique Edges:
        CHALLENGES_METHOD: Method has validity problem
        CHALLENGES_PARADIGM: All studies using paradigm P are vulnerable
        PROPOSES_BETTER_METHOD: Method B addresses problems of Method A

    Attribution Edges:
        ATTRIBUTES_FINDING: Review cites Study S as showing X
        INTERPRETS_AS: Reviewer interprets evidence as meaning X
    """
    # === Review/Synthesis Edges ===
    INCLUDES_IN_SYNTHESIS = "includes_in_synthesis"
    SYNTHESIZES_AS = "synthesizes_as"
    IDENTIFIES_MODERATOR = "identifies_moderator"
    CONTRADICTS_SYNTHESIS = "contradicts_synthesis"

    # === Theoretical Edges ===
    THEORETICALLY_PREDICTS = "theoretically_predicts"
    CONFIRMS_PREDICTION = "confirms_prediction"
    DISCONFIRMS_PREDICTION = "disconfirms_prediction"
    PROPOSES_MECHANISM = "proposes_mechanism"
    SUBSUMES_THEORY = "subsumes_theory"
    THEORY_TENSION = "theory_tension"

    # === Conceptual Edges ===
    DEFINES_CONSTRUCT = "defines_construct"
    MUST_DISTINGUISH = "must_distinguish"
    REDEFINES = "redefines"
    ORGANIZES = "organizes"

    # === Critique Edges ===
    CHALLENGES_METHOD = "challenges_method"
    CHALLENGES_PARADIGM = "challenges_paradigm"
    PROPOSES_BETTER_METHOD = "proposes_better_method"

    # === Attribution Edges ===
    ATTRIBUTES_FINDING = "attributes_finding"
    INTERPRETS_AS = "interprets_as"


# =============================================================================
# EDGE TYPE COMPATIBILITY MATRIX
# =============================================================================

@dataclass
class EdgeCompatibility:
    """
    Compatibility rules for edge types.

    Per spec §3.3: Not all edge types connect to all node types.
    """
    valid_source_types: List[str]
    valid_target_types: List[str]
    category: EdgeTypeCategory


EDGE_COMPATIBILITY: Dict[EdgeType, EdgeCompatibility] = {
    # Review/Synthesis Edges
    EdgeType.INCLUDES_IN_SYNTHESIS: EdgeCompatibility(
        valid_source_types=["synthesis_conclusion"],
        valid_target_types=["empirical_finding"],
        category=EdgeTypeCategory.REVIEW_SYNTHESIS
    ),
    EdgeType.SYNTHESIZES_AS: EdgeCompatibility(
        valid_source_types=["synthesis_conclusion"],
        valid_target_types=[],  # Targets direction value, not a node
        category=EdgeTypeCategory.REVIEW_SYNTHESIS
    ),
    EdgeType.IDENTIFIES_MODERATOR: EdgeCompatibility(
        valid_source_types=["synthesis_conclusion"],
        valid_target_types=[],  # Targets variable, not a node
        category=EdgeTypeCategory.REVIEW_SYNTHESIS
    ),
    EdgeType.CONTRADICTS_SYNTHESIS: EdgeCompatibility(
        valid_source_types=["empirical_finding"],
        valid_target_types=["synthesis_conclusion"],
        category=EdgeTypeCategory.REVIEW_SYNTHESIS
    ),

    # Theoretical Edges
    EdgeType.THEORETICALLY_PREDICTS: EdgeCompatibility(
        valid_source_types=["theoretical_proposition"],
        valid_target_types=["derived_hypothesis"],
        category=EdgeTypeCategory.THEORETICAL
    ),
    EdgeType.CONFIRMS_PREDICTION: EdgeCompatibility(
        valid_source_types=["empirical_finding", "synthesis_conclusion"],
        valid_target_types=["derived_hypothesis"],
        category=EdgeTypeCategory.THEORETICAL
    ),
    EdgeType.DISCONFIRMS_PREDICTION: EdgeCompatibility(
        valid_source_types=["empirical_finding", "synthesis_conclusion"],
        valid_target_types=["derived_hypothesis"],
        category=EdgeTypeCategory.THEORETICAL
    ),
    EdgeType.PROPOSES_MECHANISM: EdgeCompatibility(
        valid_source_types=["theoretical_proposition"],
        valid_target_types=[],  # Targets causal pathway
        category=EdgeTypeCategory.THEORETICAL
    ),
    EdgeType.SUBSUMES_THEORY: EdgeCompatibility(
        valid_source_types=["theoretical_proposition"],
        valid_target_types=["theoretical_proposition"],
        category=EdgeTypeCategory.THEORETICAL
    ),
    EdgeType.THEORY_TENSION: EdgeCompatibility(
        valid_source_types=["theoretical_proposition"],
        valid_target_types=["theoretical_proposition"],
        category=EdgeTypeCategory.THEORETICAL
    ),

    # Conceptual Edges
    EdgeType.DEFINES_CONSTRUCT: EdgeCompatibility(
        valid_source_types=["conceptual_definition"],
        valid_target_types=[],  # Targets construct in taxonomy
        category=EdgeTypeCategory.CONCEPTUAL
    ),
    EdgeType.MUST_DISTINGUISH: EdgeCompatibility(
        valid_source_types=["conceptual_constraint"],
        valid_target_types=[],  # Targets construct pair
        category=EdgeTypeCategory.CONCEPTUAL
    ),
    EdgeType.REDEFINES: EdgeCompatibility(
        valid_source_types=["conceptual_definition"],
        valid_target_types=["conceptual_definition"],
        category=EdgeTypeCategory.CONCEPTUAL
    ),
    EdgeType.ORGANIZES: EdgeCompatibility(
        valid_source_types=["framework_structure"],
        valid_target_types=[],  # Targets multiple nodes
        category=EdgeTypeCategory.CONCEPTUAL
    ),

    # Critique Edges
    EdgeType.CHALLENGES_METHOD: EdgeCompatibility(
        valid_source_types=["methodological_critique"],
        valid_target_types=[],  # Targets method_registry entry
        category=EdgeTypeCategory.CRITIQUE
    ),
    EdgeType.CHALLENGES_PARADIGM: EdgeCompatibility(
        valid_source_types=["methodological_critique"],
        valid_target_types=["empirical_finding"],  # Multiple
        category=EdgeTypeCategory.CRITIQUE
    ),
    EdgeType.PROPOSES_BETTER_METHOD: EdgeCompatibility(
        valid_source_types=["methodological_critique"],
        valid_target_types=[],  # Targets method_registry entry
        category=EdgeTypeCategory.CRITIQUE
    ),

    # Attribution Edges
    EdgeType.ATTRIBUTES_FINDING: EdgeCompatibility(
        valid_source_types=["expert_synthesis"],
        valid_target_types=["empirical_finding"],
        category=EdgeTypeCategory.ATTRIBUTION
    ),
    EdgeType.INTERPRETS_AS: EdgeCompatibility(
        valid_source_types=["expert_synthesis"],
        valid_target_types=[],  # Targets interpretation
        category=EdgeTypeCategory.ATTRIBUTION
    ),
}


def get_edge_category(edge_type: EdgeType) -> EdgeTypeCategory:
    """Get the category for an edge type."""
    compat = EDGE_COMPATIBILITY.get(edge_type)
    return compat.category if compat else EdgeTypeCategory.LEGACY


def get_valid_source_types(edge_type: EdgeType) -> List[str]:
    """Get valid source node types for an edge type."""
    compat = EDGE_COMPATIBILITY.get(edge_type)
    return compat.valid_source_types if compat else []


def get_valid_target_types(edge_type: EdgeType) -> List[str]:
    """Get valid target node types for an edge type."""
    compat = EDGE_COMPATIBILITY.get(edge_type)
    return compat.valid_target_types if compat else []


def validate_edge_connection(
    edge_type: EdgeType,
    source_node_type: str,
    target_node_type: str
) -> tuple[bool, str]:
    """
    Validate that an edge connection is compatible.

    Args:
        edge_type: The type of edge
        source_node_type: The node type of the source
        target_node_type: The node type of the target

    Returns:
        Tuple of (is_valid, message)
    """
    compat = EDGE_COMPATIBILITY.get(edge_type)
    if compat is None:
        return True, "unknown_edge_type"  # Allow unknown with warning

    # Check source validity
    if compat.valid_source_types and source_node_type not in compat.valid_source_types:
        return False, f"Invalid source type '{source_node_type}' for edge '{edge_type.value}'"

    # Check target validity (empty list means any target is valid)
    if compat.valid_target_types and target_node_type not in compat.valid_target_types:
        return False, f"Invalid target type '{target_node_type}' for edge '{edge_type.value}'"

    return True, "valid"


def get_theoretical_edges() -> List[EdgeType]:
    """Get all theoretical edge types."""
    return [
        EdgeType.THEORETICALLY_PREDICTS,
        EdgeType.CONFIRMS_PREDICTION,
        EdgeType.DISCONFIRMS_PREDICTION,
        EdgeType.PROPOSES_MECHANISM,
        EdgeType.SUBSUMES_THEORY,
        EdgeType.THEORY_TENSION,
    ]


def get_review_synthesis_edges() -> List[EdgeType]:
    """Get all review/synthesis edge types."""
    return [
        EdgeType.INCLUDES_IN_SYNTHESIS,
        EdgeType.SYNTHESIZES_AS,
        EdgeType.IDENTIFIES_MODERATOR,
        EdgeType.CONTRADICTS_SYNTHESIS,
    ]
