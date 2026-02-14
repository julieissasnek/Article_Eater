"""
Epistemic Module (Tier 2 Implementation).

This module provides epistemic infrastructure for the Article Eater system:
- BN node definitions for epistemic variables
- BN edge definitions for causal relationships
- Reflexive monitoring capabilities (Sprint 3)
- Node/edge type taxonomy for non-empirical papers (Sprint 6)
"""

from src.epistemic.bn_nodes import (
    EpistemicVariable,
    VariableType,
    EPISTEMIC_VARIABLES,
    SOURCE_QUALITY_COMPONENTS,
    get_epistemic_variable,
    list_epistemic_variables,
    get_pe_variables,
    get_environmental_variables,
    get_source_quality_variables,
    get_source_quality_component_variables,
)

from src.epistemic.bn_edges import (
    EpistemicEdge,
    PathwayType,
    ENVIRONMENTAL_EDGES,
    SOURCE_QUALITY_EDGES,
    ALL_EPISTEMIC_EDGES,
    PATHWAY_DEFAULTS,
    STUB_NODES,
    get_environmental_edges,
    get_source_quality_edges,
    get_all_edges,
    get_edges_as_tuples,
    get_edges_for_variable,
    get_all_variables,
    validate_edge_connectivity,
    is_acyclic,
    get_topological_order,
    assign_pathway_type,
    tag_edges_with_pathway,
    get_edges_by_pathway,
    validate_all_edges_tagged,
)

from src.epistemic.source_quality import (
    compute_source_quality,
    compute_source_quality_context,
    compute_source_quality_detailed,
    SourceQualityResult,
    StudyType,
    DEFAULT_SOURCE_QUALITY_WEIGHTS,
    COMMITMENT_PENALTY_MULTIPLIER,
    classify_quality,
    high_quality_threshold,
    moderate_quality_threshold,
)

from src.epistemic.warrant_scaling import (
    compute_coherence_warrant,
    get_coherence_warrant_for_belief,
    compute_argumentative_warrant,
    compute_vigilance_warrant,
    compute_total_warrant,
    BASE_COHERENCE_WARRANT,
    BASE_ARGUMENTATIVE_WARRANT,
    BASE_VIGILANCE_WARRANT,
)

# Sprint 6: Non-Empirical Web Integration
from src.epistemic.node_types import (
    NodeType,
    NodeTypeFamily,
    NodeTypeProperties,
    get_node_type_family,
    get_node_type_properties,
    is_bn_eligible,
    get_evidence_node_types,
    get_structural_node_types,
    get_interpretive_node_types,
)

from src.epistemic.edge_types import (
    EdgeType,
    EdgeTypeCategory,
    EdgeCompatibility,
    get_edge_category,
    get_valid_source_types,
    get_valid_target_types,
    validate_edge_connection,
    get_theoretical_edges,
    get_review_synthesis_edges,
)

from src.epistemic.contracts import ClaimV2, EdgeV2

from src.epistemic.validation import (
    NODE_TYPE_TEMPLATE_MAP,
    validate_node_for_template,
    get_valid_node_types_for_template,
)

__all__ = [
    # Node definitions
    "EpistemicVariable",
    "VariableType",
    "EPISTEMIC_VARIABLES",
    "SOURCE_QUALITY_COMPONENTS",
    "get_epistemic_variable",
    "list_epistemic_variables",
    "get_pe_variables",
    "get_environmental_variables",
    "get_source_quality_variables",
    "get_source_quality_component_variables",
    # Edge definitions
    "EpistemicEdge",
    "PathwayType",
    "ENVIRONMENTAL_EDGES",
    "SOURCE_QUALITY_EDGES",
    "ALL_EPISTEMIC_EDGES",
    "PATHWAY_DEFAULTS",
    "STUB_NODES",
    "get_environmental_edges",
    "get_source_quality_edges",
    "get_all_edges",
    "get_edges_as_tuples",
    "get_edges_for_variable",
    "get_all_variables",
    "validate_edge_connectivity",
    "is_acyclic",
    "get_topological_order",
    # Pathway assignment
    "assign_pathway_type",
    "tag_edges_with_pathway",
    "get_edges_by_pathway",
    "validate_all_edges_tagged",
    # Source quality computation
    "compute_source_quality",
    "compute_source_quality_context",
    "compute_source_quality_detailed",
    "SourceQualityResult",
    "StudyType",
    "DEFAULT_SOURCE_QUALITY_WEIGHTS",
    "COMMITMENT_PENALTY_MULTIPLIER",
    "classify_quality",
    "high_quality_threshold",
    "moderate_quality_threshold",
    # Warrant scaling (panel-approved)
    "compute_coherence_warrant",
    "get_coherence_warrant_for_belief",
    "compute_argumentative_warrant",
    "compute_vigilance_warrant",
    "compute_total_warrant",
    "BASE_COHERENCE_WARRANT",
    "BASE_ARGUMENTATIVE_WARRANT",
    "BASE_VIGILANCE_WARRANT",
    # Sprint 6: Node type taxonomy
    "NodeType",
    "NodeTypeFamily",
    "NodeTypeProperties",
    "get_node_type_family",
    "get_node_type_properties",
    "is_bn_eligible",
    "get_evidence_node_types",
    "get_structural_node_types",
    "get_interpretive_node_types",
    # Sprint 6: Edge type taxonomy
    "EdgeType",
    "EdgeTypeCategory",
    "EdgeCompatibility",
    "get_edge_category",
    "get_valid_source_types",
    "get_valid_target_types",
    "validate_edge_connection",
    "get_theoretical_edges",
    "get_review_synthesis_edges",
    # Sprint 6: Contracts
    "ClaimV2",
    "EdgeV2",
    # Sprint 6: Validation
    "NODE_TYPE_TEMPLATE_MAP",
    "validate_node_for_template",
    "get_valid_node_types_for_template",
]
