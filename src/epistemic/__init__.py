"""
Epistemic Module (Tier 2 Implementation).

This module provides epistemic infrastructure for the Article Eater system:
- BN node definitions for epistemic variables
- BN edge definitions for causal relationships
- Reflexive monitoring capabilities (Sprint 3)
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
]
