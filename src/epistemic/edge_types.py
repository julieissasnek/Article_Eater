"""
Edge Type Taxonomy — Canonical Source of Truth (Sprint 1.2).

Per Opus decisions (2026-02-15):
- Merges ConstraintType INTO EdgeType (all values kept distinct)
- EPISTEMIC_DERIVATION vs COHERENCE_SUPPORT: distinct (derivation = inferential, coherence = holistic)
- SUPPORTS/CONTRADICTS vs CONFIRMS/DISCONFIRMS_PREDICTION: distinct (pre-CMR vs post-CMR)
- BN edge types remain separate (different semantic layer)

Categories:
1. Constraint Edges (from ConstraintType) — basic epistemic relations
2. Coherence Edges — Quinean web coherence relations
3. Epistemic Edges — theory tier relations (CMR pipeline)
4. Argumentative Edges — argumentation-based relations
5. Review/Synthesis Edges — meta-analysis relations
6. Theoretical Edges — theory-prediction relations
7. Conceptual Edges — definitional relations
8. Critique Edges — validity challenge relations
9. Attribution Edges — citation relations

Reference: Non_Empirical_Web_Integration_Spec_V1.0.md §3.2
Reference: Canonical Decisions Record (02-15_09)
"""

from enum import Enum
from typing import Dict, List
from dataclasses import dataclass


class EdgeTypeCategory(str, Enum):
    """Categories of edge types."""
    CONSTRAINT = "constraint"        # Basic epistemic relations
    COHERENCE = "coherence"          # Quinean web relations
    EPISTEMIC = "epistemic"          # Theory tier / CMR relations
    ARGUMENTATIVE = "argumentative"  # Argumentation-based
    REVIEW_SYNTHESIS = "review_synthesis"
    THEORETICAL = "theoretical"
    CONCEPTUAL = "conceptual"
    CRITIQUE = "critique"
    ATTRIBUTION = "attribution"


class EdgeType(str, Enum):
    """
    Canonical edge types for web of belief connections.

    Sprint 1.2: Merged ConstraintType + EdgeType per Opus decisions.

    Categories (per Opus 2026-02-15):
    1. CONSTRAINT: Basic epistemic relations (pre-CMR, from papers)
    2. COHERENCE: Quinean web coherence (holistic, bidirectional)
    3. EPISTEMIC: Theory tier relations (CMR pipeline, directional)
    4. ARGUMENTATIVE: Argumentation-based relations
    5. REVIEW_SYNTHESIS: Meta-analysis relations
    6. THEORETICAL: Theory-prediction relations (post-CMR)
    7. CONCEPTUAL: Definitional relations
    8. CRITIQUE: Validity challenge relations
    9. ATTRIBUTION: Citation relations

    Key distinctions (per Opus):
    - SUPPORTS vs CONFIRMS_PREDICTION: pre-CMR vs post-CMR
    - COHERENCE_SUPPORT vs EPISTEMIC_DERIVATION: holistic vs inferential
    """

    # =========================================================================
    # CONSTRAINT EDGES (from ConstraintType) — basic epistemic relations
    # Pre-CMR, extracted from papers, no prediction ID
    # =========================================================================
    SUPPORTS = "supports"              # Positive evidential support
    CONTRADICTS = "contradicts"        # Negative evidential relation
    EXPLAINS = "explains"              # Theoretical → empirical
    INSTANTIATES = "instantiates"      # Empirical → theoretical
    ANALOGOUS = "analogous"            # Similar structure
    INDEPENDENT = "independent"        # No direct constraint

    # =========================================================================
    # COHERENCE EDGES — Quinean web relations
    # Holistic, bidirectional, defeasible (per Opus)
    # =========================================================================
    COHERENCE_SUPPORT = "coherence_support"    # A increases coherence of B
    COHERENCE_TENSION = "coherence_tension"    # A decreases coherence of B

    # =========================================================================
    # EPISTEMIC EDGES — Theory tier / CMR pipeline relations
    # Directional, inferential, with specific provenance chain (per Opus)
    # =========================================================================
    EPISTEMIC_DERIVATION = "epistemic_derivation"          # Tier 1 → Tier 2 template
    EPISTEMIC_CROSS_TEMPLATE = "epistemic_cross_template"  # Between Tier 2 templates
    EPISTEMIC_MEDIATION = "epistemic_mediation"            # Claim mediated by interpretation

    # =========================================================================
    # BRIDGE/WARRANT EDGES — Cross-layer connections
    # =========================================================================
    BRIDGES = "bridges"                              # Bridge warrant connection
    STRONG_TENSION = "strong_tension"                # Strong tension from failed bridge
    SHARED_EVIDENCE = "shared_evidence"              # Same study supports both beliefs
    GENERALIZABILITY_WARRANT = "generalizability_warrant"  # Type A → Type B (Sprint T2-4b)

    # =========================================================================
    # ARGUMENTATIVE EDGES — Argumentation-based relations
    # =========================================================================
    ARGUMENTATIVE_SUPPORT = "argumentative_support"      # Finding supports via argument
    ARGUMENTATIVE_CHALLENGE = "argumentative_challenge"  # Finding challenges via argument

    # =========================================================================
    # REVIEW/SYNTHESIS EDGES — Meta-analysis relations
    # =========================================================================
    INCLUDES_IN_SYNTHESIS = "includes_in_synthesis"
    SYNTHESIZES_AS = "synthesizes_as"
    IDENTIFIES_MODERATOR = "identifies_moderator"
    CONTRADICTS_SYNTHESIS = "contradicts_synthesis"

    # =========================================================================
    # THEORETICAL EDGES — Theory-prediction relations
    # Post-CMR, carries prediction ID and template chain (per Opus)
    # =========================================================================
    THEORETICALLY_PREDICTS = "theoretically_predicts"
    CONFIRMS_PREDICTION = "confirms_prediction"      # Post-CMR: observation confirms prediction
    DISCONFIRMS_PREDICTION = "disconfirms_prediction"  # Post-CMR: observation disconfirms
    PROPOSES_MECHANISM = "proposes_mechanism"
    SUBSUMES_THEORY = "subsumes_theory"
    THEORY_TENSION = "theory_tension"

    # =========================================================================
    # CONCEPTUAL EDGES — Definitional relations
    # =========================================================================
    DEFINES_CONSTRUCT = "defines_construct"
    MUST_DISTINGUISH = "must_distinguish"
    REDEFINES = "redefines"
    ORGANIZES = "organizes"

    # =========================================================================
    # CRITIQUE EDGES — Validity challenge relations
    # =========================================================================
    CHALLENGES_METHOD = "challenges_method"
    CHALLENGES_PARADIGM = "challenges_paradigm"
    PROPOSES_BETTER_METHOD = "proposes_better_method"

    # =========================================================================
    # ATTRIBUTION EDGES — Citation relations
    # =========================================================================
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

    # === MERGED FROM ConstraintType (Sprint 1.2) ===

    # Constraint Edges (basic epistemic relations)
    EdgeType.SUPPORTS: EdgeCompatibility(
        valid_source_types=["empirical_finding", "synthesis_conclusion"],
        valid_target_types=["theoretical_proposition", "derived_hypothesis"],
        category=EdgeTypeCategory.CONSTRAINT
    ),
    EdgeType.CONTRADICTS: EdgeCompatibility(
        valid_source_types=["empirical_finding", "synthesis_conclusion"],
        valid_target_types=["theoretical_proposition", "derived_hypothesis"],
        category=EdgeTypeCategory.CONSTRAINT
    ),
    EdgeType.EXPLAINS: EdgeCompatibility(
        valid_source_types=["theoretical_proposition"],
        valid_target_types=["empirical_finding"],
        category=EdgeTypeCategory.CONSTRAINT
    ),
    EdgeType.INSTANTIATES: EdgeCompatibility(
        valid_source_types=["empirical_finding"],
        valid_target_types=["theoretical_proposition"],
        category=EdgeTypeCategory.CONSTRAINT
    ),
    EdgeType.ANALOGOUS: EdgeCompatibility(
        valid_source_types=[],  # Any node type
        valid_target_types=[],  # Any node type
        category=EdgeTypeCategory.CONSTRAINT
    ),
    EdgeType.INDEPENDENT: EdgeCompatibility(
        valid_source_types=[],
        valid_target_types=[],
        category=EdgeTypeCategory.CONSTRAINT
    ),

    # Coherence Edges (Quinean web relations)
    EdgeType.COHERENCE_SUPPORT: EdgeCompatibility(
        valid_source_types=[],  # Any belief
        valid_target_types=[],  # Any belief
        category=EdgeTypeCategory.COHERENCE
    ),
    EdgeType.COHERENCE_TENSION: EdgeCompatibility(
        valid_source_types=[],
        valid_target_types=[],
        category=EdgeTypeCategory.COHERENCE
    ),

    # Epistemic Edges (CMR pipeline relations)
    EdgeType.EPISTEMIC_DERIVATION: EdgeCompatibility(
        valid_source_types=["theoretical_proposition", "template_chain"],
        valid_target_types=["derived_hypothesis"],
        category=EdgeTypeCategory.EPISTEMIC
    ),
    EdgeType.EPISTEMIC_CROSS_TEMPLATE: EdgeCompatibility(
        valid_source_types=["template_chain"],
        valid_target_types=["template_chain"],
        category=EdgeTypeCategory.EPISTEMIC
    ),
    EdgeType.EPISTEMIC_MEDIATION: EdgeCompatibility(
        valid_source_types=[],
        valid_target_types=[],
        category=EdgeTypeCategory.EPISTEMIC
    ),

    # Bridge/Warrant Edges
    EdgeType.BRIDGES: EdgeCompatibility(
        valid_source_types=["bridge_warrant"],
        valid_target_types=["theoretical_proposition", "empirical_finding"],
        category=EdgeTypeCategory.CONSTRAINT
    ),
    EdgeType.STRONG_TENSION: EdgeCompatibility(
        valid_source_types=["empirical_finding"],
        valid_target_types=["bridge_warrant"],
        category=EdgeTypeCategory.CONSTRAINT
    ),
    EdgeType.SHARED_EVIDENCE: EdgeCompatibility(
        valid_source_types=["empirical_finding"],
        valid_target_types=["empirical_finding"],
        category=EdgeTypeCategory.CONSTRAINT
    ),
    EdgeType.GENERALIZABILITY_WARRANT: EdgeCompatibility(
        valid_source_types=["empirical_finding"],  # Type A claim
        valid_target_types=["empirical_finding"],  # Type B claim
        category=EdgeTypeCategory.CONSTRAINT
    ),

    # Argumentative Edges
    EdgeType.ARGUMENTATIVE_SUPPORT: EdgeCompatibility(
        valid_source_types=["empirical_finding"],
        valid_target_types=["theoretical_proposition", "derived_hypothesis"],
        category=EdgeTypeCategory.ARGUMENTATIVE
    ),
    EdgeType.ARGUMENTATIVE_CHALLENGE: EdgeCompatibility(
        valid_source_types=["empirical_finding", "methodological_critique"],
        valid_target_types=["theoretical_proposition", "derived_hypothesis"],
        category=EdgeTypeCategory.ARGUMENTATIVE
    ),
}


def get_edge_category(edge_type: EdgeType) -> EdgeTypeCategory:
    """Get the category for an edge type."""
    compat = EDGE_COMPATIBILITY.get(edge_type)
    return compat.category if compat else EdgeTypeCategory.CONSTRAINT


# =============================================================================
# LEGACY ALIAS: ConstraintType → EdgeType
# For backward compatibility during migration
# =============================================================================

# Alias for code that still imports ConstraintType
ConstraintType = EdgeType

# Mapping from old ConstraintType names to EdgeType (for string conversion)
LEGACY_CONSTRAINT_TYPE_MAP = {
    "supports": EdgeType.SUPPORTS,
    "contradicts": EdgeType.CONTRADICTS,
    "explains": EdgeType.EXPLAINS,
    "instantiates": EdgeType.INSTANTIATES,
    "analogous": EdgeType.ANALOGOUS,
    "independent": EdgeType.INDEPENDENT,
    "bridges": EdgeType.BRIDGES,
    "strong_tension": EdgeType.STRONG_TENSION,
    "shared_evidence": EdgeType.SHARED_EVIDENCE,
    "epistemic_derivation": EdgeType.EPISTEMIC_DERIVATION,
    "epistemic_cross_template": EdgeType.EPISTEMIC_CROSS_TEMPLATE,
    "epistemic_mediation": EdgeType.EPISTEMIC_MEDIATION,
    "coherence_support": EdgeType.COHERENCE_SUPPORT,
    "coherence_tension": EdgeType.COHERENCE_TENSION,
    "argumentative_support": EdgeType.ARGUMENTATIVE_SUPPORT,
    "argumentative_challenge": EdgeType.ARGUMENTATIVE_CHALLENGE,
    "generalizability_warrant": EdgeType.GENERALIZABILITY_WARRANT,
    "tier2_theory_link": EdgeType.EPISTEMIC_DERIVATION,
}


def convert_legacy_constraint_type(value: str) -> EdgeType:
    """Convert a legacy ConstraintType string to EdgeType."""
    key = value.strip().lower()
    if key in LEGACY_CONSTRAINT_TYPE_MAP:
        return LEGACY_CONSTRAINT_TYPE_MAP[key]
    # Try direct EdgeType conversion
    try:
        return EdgeType(key)
    except ValueError:
        return EdgeType.SUPPORTS  # Default fallback


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


# =============================================================================
# SCHEMA_PENDING_CMR_SPEC: FINDING–MECHANISM LINKS
# =============================================================================
#
# This section is a PLACEHOLDER for Sprint 7: Theory Architecture.
#
# WHAT THIS WILL CONTAIN:
# Links connecting empirical findings to theoretical mechanisms. When a study
# finds that "nature exposure reduces stress" (Tier 3 finding), these links
# specify WHICH Tier 1 mechanism explains HOW:
#   - Predictive Processing: nature statistics match evolved priors → uncertainty reduction
#   - Neuromodulatory: parasympathetic activation via vagal pathway
#   - DMN/TPN: nature allows DMN activation due to low attentional demand
#
# WHY THIS IS PENDING:
# The schema for these links will be determined by the Compositional Mechanistic
# Reasoning (CMR) specification, which is being developed separately. CMR will define:
#   - Template library: canonical compositional reasoning patterns
#   - Prediction grammar: how to compose mechanism claims into testable predictions
#   - Link structure: what fields each finding–mechanism link requires
#
# DEPENDENCIES:
# Sprint 7 requires BOTH:
#   1. Sprint 6 complete (node types, edge types) — provides web infrastructure
#   2. CMR specification ready — provides template library and grammar
#
# DO NOT IMPLEMENT until both dependencies are met.
#
# PLANNED STRUCTURE (TENTATIVE — subject to CMR spec):
#
# @dataclass
# class FindingMechanismLink:
#     """Link between an empirical finding and a theoretical mechanism."""
#     link_id: str
#     finding_id: str  # Tier 3 finding being explained
#     mechanism_id: str  # Tier 1 mechanism doing the explaining
#     framework_id: str  # Which Tier 1 framework this mechanism belongs to
#     composition_template: str  # CMR template ID — PENDING CMR SPEC
#     prediction_grammar: dict  # How this generates predictions — PENDING CMR SPEC
#     confidence: float  # How confident is this mechanistic explanation
#     evidence_type: str  # What kind of evidence supports this link
#
# class MechanismLinkType(str, Enum):
#     """Types of finding–mechanism relationships."""
#     DIRECTLY_EXPLAINS = "directly_explains"  # Mechanism M explains finding F
#     PARTIALLY_EXPLAINS = "partially_explains"  # M explains aspect of F
#     MODULATES = "modulates"  # M modulates magnitude/direction of F
#     MEDIATES = "mediates"  # M is on causal pathway for F
#     CONTRADICTS = "contradicts"  # M predicts opposite of F
#
# FINDING_MECHANISM_LINKS: Dict[str, FindingMechanismLink] = {}
#
# =============================================================================
# END SCHEMA_PENDING_CMR_SPEC
# =============================================================================
