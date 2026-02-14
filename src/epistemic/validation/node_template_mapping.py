"""
Node Type → Template Family Mapping Validation (Sprint 6a / Task 6a.5).

Implements the compatibility matrix from spec Appendix A.
Validates that extracted node types are valid for the source template family.

Reference: Non_Empirical_Web_Integration_Spec_V1.0.md Appendix A
"""

from typing import Dict, List, Set


# =============================================================================
# NODE TYPE → TEMPLATE FAMILY MAPPING (Spec Appendix A)
# =============================================================================

NODE_TYPE_TEMPLATE_MAP: Dict[str, List[str]] = {
    # Template family → list of valid node types that can be produced

    # Primary study templates
    "empirical_v2": [
        "empirical_finding"
    ],
    "observational_field": [
        "empirical_finding"
    ],
    "case_study": [
        "empirical_finding",
        "derived_hypothesis",
        "bridge_warrant"
    ],

    # Quantitative synthesis templates
    "meta_analysis": [
        "synthesis_conclusion",
        "knowledge_gap"
    ],
    "systematic_review": [
        "synthesis_conclusion",
        "methodological_critique",
        "knowledge_gap"
    ],

    # Qualitative templates
    "interview_study": [
        "qualitative_finding"
    ],
    "ethnographic": [
        "qualitative_finding",
        "conceptual_definition"
    ],
    "grounded_theory": [
        "qualitative_finding",
        "derived_hypothesis"
    ],
    "phenomenological": [
        "qualitative_finding"
    ],

    # Mixed methods
    "mixed_methods": [
        "empirical_finding",
        "qualitative_finding",
        "bridge_warrant"
    ],

    # Theoretical/conceptual templates
    "theoretical": [
        "theoretical_proposition",
        "derived_hypothesis",
        "conceptual_definition",
        "bridge_warrant"
    ],
    "conceptual_framework": [
        "conceptual_definition",
        "conceptual_constraint",
        "framework_structure"
    ],

    # Expert opinion templates
    "narrative_review": [
        "expert_synthesis",
        "knowledge_gap",
        "bridge_warrant"
    ],
    "thought_piece": [
        "expert_synthesis",
        "methodological_critique",
        "knowledge_gap"
    ],
}


# Build reverse mapping: node_type → list of valid templates
TEMPLATE_FOR_NODE_TYPE: Dict[str, List[str]] = {}
for template, node_types in NODE_TYPE_TEMPLATE_MAP.items():
    for node_type in node_types:
        if node_type not in TEMPLATE_FOR_NODE_TYPE:
            TEMPLATE_FOR_NODE_TYPE[node_type] = []
        TEMPLATE_FOR_NODE_TYPE[node_type].append(template)


def validate_node_for_template(node_type: str, template_family: str) -> bool:
    """
    Check if node_type is valid for the given template_family.

    Args:
        node_type: The node type to validate
        template_family: The source template family

    Returns:
        True if valid, False otherwise
    """
    valid_types = NODE_TYPE_TEMPLATE_MAP.get(template_family, [])
    return node_type in valid_types


def get_valid_node_types_for_template(template_family: str) -> List[str]:
    """
    Get all valid node types for a template family.

    Args:
        template_family: The template family name

    Returns:
        List of valid node type strings
    """
    return NODE_TYPE_TEMPLATE_MAP.get(template_family, [])


def get_valid_templates_for_node_type(node_type: str) -> List[str]:
    """
    Get all template families that can produce a node type.

    Args:
        node_type: The node type

    Returns:
        List of template family names
    """
    return TEMPLATE_FOR_NODE_TYPE.get(node_type, [])


def validate_extraction(
    nodes: List[dict],
    template_family: str
) -> tuple[bool, List[str]]:
    """
    Validate all nodes from an extraction against template compatibility.

    Args:
        nodes: List of node dictionaries with 'node_type' field
        template_family: The source template family

    Returns:
        Tuple of (all_valid, list_of_invalid_node_types)
    """
    valid_types = set(NODE_TYPE_TEMPLATE_MAP.get(template_family, []))
    invalid = []

    for node in nodes:
        node_type = node.get("node_type", "")
        if node_type and node_type not in valid_types:
            invalid.append(node_type)

    return len(invalid) == 0, invalid


# =============================================================================
# TEMPLATE FAMILY METADATA
# =============================================================================

TEMPLATE_FAMILY_DESCRIPTIONS: Dict[str, str] = {
    "empirical_v2": "Primary empirical study (experiments, RCTs)",
    "observational_field": "Field observation study (POE, ESM)",
    "case_study": "Single or multiple case study",
    "meta_analysis": "Quantitative meta-analysis",
    "systematic_review": "Systematic literature review",
    "interview_study": "Qualitative interview study",
    "ethnographic": "Ethnographic research",
    "grounded_theory": "Grounded theory study",
    "phenomenological": "Phenomenological study",
    "mixed_methods": "Mixed methods study",
    "theoretical": "Theoretical paper",
    "conceptual_framework": "Conceptual framework paper",
    "narrative_review": "Narrative/scoping review",
    "thought_piece": "Commentary, editorial, expert opinion",
}


def get_all_template_families() -> List[str]:
    """Get all defined template families."""
    return list(NODE_TYPE_TEMPLATE_MAP.keys())


def get_empirical_templates() -> List[str]:
    """Get templates that produce empirical findings."""
    return [
        t for t, types in NODE_TYPE_TEMPLATE_MAP.items()
        if "empirical_finding" in types
    ]


def get_theoretical_templates() -> List[str]:
    """Get templates that produce theoretical propositions."""
    return [
        t for t, types in NODE_TYPE_TEMPLATE_MAP.items()
        if "theoretical_proposition" in types
    ]
