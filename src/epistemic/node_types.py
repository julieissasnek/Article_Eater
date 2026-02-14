"""
Node Type Taxonomy for Non-Empirical Web Integration (Sprint 6a / Task 6a.1).

Defines 12 node types organized in 5 families for the web of belief.
Extends beyond EMPIRICAL_FINDING to support theoretical papers, reviews,
meta-analyses, conceptual frameworks, and other non-empirical paper types.

Reference: Non_Empirical_Web_Integration_Spec_V1.0.md §2.2
"""

from enum import Enum
from typing import Dict, List, Optional
from dataclasses import dataclass


class NodeTypeFamily(str, Enum):
    """
    Families of node types, each with distinct epistemic properties.

    - EVIDENCE: Nodes that carry empirical data
    - STRUCTURAL: Nodes that organize the web theoretically
    - INTERPRETIVE: Nodes that carry expert judgment
    - GAP: Nodes that mark missing knowledge
    - META: Nodes that organize other nodes
    """
    EVIDENCE = "evidence"          # Family A: carry data
    STRUCTURAL = "structural"      # Family B: organize the web
    INTERPRETIVE = "interpretive"  # Family C: carry expert judgment
    GAP = "gap"                    # Family D: mark what's missing
    META = "meta"                  # Family E: organize other nodes


class NodeType(str, Enum):
    """
    Node types for web of belief (12 types in 5 families).

    Per Non_Empirical_Web_Integration_Spec_V1.0.md §2.2.

    Family A — Evidence Nodes (carry data):
        EMPIRICAL_FINDING: Single-study finding with design metadata
        SYNTHESIS_CONCLUSION: Aggregated finding across multiple studies
        QUALITATIVE_FINDING: Theme/pattern from qualitative research

    Family B — Structural Nodes (organize the web):
        THEORETICAL_PROPOSITION: Proposed causal relationship or mechanism
        DERIVED_HYPOTHESIS: Testable prediction derived from a proposition
        CONCEPTUAL_DEFINITION: Definition of a construct, term, or distinction
        CONCEPTUAL_CONSTRAINT: A "must-not-conflate" rule for two things

    Family C — Interpretive Nodes (carry expert judgment):
        EXPERT_SYNTHESIS: Expert interpretation of evidence (non-systematic)
        METHODOLOGICAL_CRITIQUE: Argument that a method/paradigm is flawed

    Family D — Gap Nodes (mark what's missing):
        KNOWLEDGE_GAP: Identified gap in the evidence

    Family E — Meta-Nodes (organize other nodes):
        FRAMEWORK_STRUCTURE: Organizational schema (taxonomy, typology)
        BRIDGE_WARRANT: Explicit link licensing cross-domain transfer
    """
    # Family A: Evidence Nodes (carry data)
    EMPIRICAL_FINDING = "empirical_finding"
    SYNTHESIS_CONCLUSION = "synthesis_conclusion"
    QUALITATIVE_FINDING = "qualitative_finding"

    # Family B: Structural Nodes (organize the web)
    THEORETICAL_PROPOSITION = "theoretical_proposition"
    DERIVED_HYPOTHESIS = "derived_hypothesis"
    CONCEPTUAL_DEFINITION = "conceptual_definition"
    CONCEPTUAL_CONSTRAINT = "conceptual_constraint"

    # Family C: Interpretive Nodes (carry expert judgment)
    EXPERT_SYNTHESIS = "expert_synthesis"
    METHODOLOGICAL_CRITIQUE = "methodological_critique"

    # Family D: Gap Nodes (mark what's missing)
    KNOWLEDGE_GAP = "knowledge_gap"

    # Family E: Meta-Nodes (organize other nodes)
    FRAMEWORK_STRUCTURE = "framework_structure"
    BRIDGE_WARRANT = "bridge_warrant"


# =============================================================================
# NODE TYPE PROPERTIES
# =============================================================================

@dataclass
class NodeTypeProperties:
    """
    Properties that determine how a node type participates in web computations.

    Per spec §2.3.
    """
    has_effect_size: bool = False
    has_study_design: bool = False
    has_argument_structure: bool = False
    bn_eligible: bool = False
    entrenchment_source: str = "coherence"
    family: NodeTypeFamily = NodeTypeFamily.EVIDENCE


NODE_TYPE_PROPERTIES: Dict[NodeType, NodeTypeProperties] = {
    NodeType.EMPIRICAL_FINDING: NodeTypeProperties(
        has_effect_size=True,
        has_study_design=True,
        has_argument_structure=False,  # Optional
        bn_eligible=True,
        entrenchment_source="direct_evidence_and_coherence",
        family=NodeTypeFamily.EVIDENCE
    ),
    NodeType.SYNTHESIS_CONCLUSION: NodeTypeProperties(
        has_effect_size=True,  # Pooled
        has_study_design=True,  # Aggregate
        has_argument_structure=True,
        bn_eligible=True,  # Higher weight
        entrenchment_source="included_studies_and_coherence",
        family=NodeTypeFamily.EVIDENCE
    ),
    NodeType.QUALITATIVE_FINDING: NodeTypeProperties(
        has_effect_size=False,
        has_study_design=True,  # Qualitative design
        has_argument_structure=True,
        bn_eligible=False,  # Limited (structural only)
        entrenchment_source="triangulation_and_coherence",
        family=NodeTypeFamily.EVIDENCE
    ),
    NodeType.THEORETICAL_PROPOSITION: NodeTypeProperties(
        has_effect_size=False,
        has_study_design=False,
        has_argument_structure=True,  # Derivation chain
        bn_eligible=True,  # Proposes edges
        entrenchment_source="prediction_accuracy_and_coherence",
        family=NodeTypeFamily.STRUCTURAL
    ),
    NodeType.DERIVED_HYPOTHESIS: NodeTypeProperties(
        has_effect_size=True,  # Predicted
        has_study_design=False,
        has_argument_structure=True,
        bn_eligible=True,  # Prior → posterior
        entrenchment_source="confirmation_disconfirmation",
        family=NodeTypeFamily.STRUCTURAL
    ),
    NodeType.CONCEPTUAL_DEFINITION: NodeTypeProperties(
        has_effect_size=False,
        has_study_design=False,
        has_argument_structure=False,
        bn_eligible=False,  # Taxonomy only
        entrenchment_source="adoption_and_usefulness",
        family=NodeTypeFamily.STRUCTURAL
    ),
    NodeType.CONCEPTUAL_CONSTRAINT: NodeTypeProperties(
        has_effect_size=False,
        has_study_design=False,
        has_argument_structure=True,
        bn_eligible=False,  # Validation only
        entrenchment_source="violations_detected",
        family=NodeTypeFamily.STRUCTURAL
    ),
    NodeType.EXPERT_SYNTHESIS: NodeTypeProperties(
        has_effect_size=False,
        has_study_design=False,
        has_argument_structure=True,
        bn_eligible=False,  # Limited
        entrenchment_source="author_expertise_and_coherence",
        family=NodeTypeFamily.INTERPRETIVE
    ),
    NodeType.METHODOLOGICAL_CRITIQUE: NodeTypeProperties(
        has_effect_size=False,
        has_study_design=False,
        has_argument_structure=True,  # Argumentative
        bn_eligible=False,  # Modifies others
        entrenchment_source="argument_quality_and_uptake",
        family=NodeTypeFamily.INTERPRETIVE
    ),
    NodeType.KNOWLEDGE_GAP: NodeTypeProperties(
        has_effect_size=False,
        has_study_design=False,
        has_argument_structure=False,
        bn_eligible=False,  # VOI signal only
        entrenchment_source="persistence",
        family=NodeTypeFamily.GAP
    ),
    NodeType.FRAMEWORK_STRUCTURE: NodeTypeProperties(
        has_effect_size=False,
        has_study_design=False,
        has_argument_structure=False,
        bn_eligible=False,  # Organizational only
        entrenchment_source="adoption",
        family=NodeTypeFamily.META
    ),
    NodeType.BRIDGE_WARRANT: NodeTypeProperties(
        has_effect_size=False,
        has_study_design=False,
        has_argument_structure=True,
        bn_eligible=True,  # Licensing
        entrenchment_source="grounding_quality",
        family=NodeTypeFamily.META
    ),
}


def get_node_type_family(node_type: NodeType) -> NodeTypeFamily:
    """Get the family for a node type."""
    props = NODE_TYPE_PROPERTIES.get(node_type)
    return props.family if props else NodeTypeFamily.EVIDENCE


def get_node_type_properties(node_type: NodeType) -> NodeTypeProperties:
    """Get the properties for a node type."""
    return NODE_TYPE_PROPERTIES.get(node_type, NodeTypeProperties())


def is_bn_eligible(node_type: NodeType) -> bool:
    """Check if a node type is eligible for BN participation."""
    props = NODE_TYPE_PROPERTIES.get(node_type)
    return props.bn_eligible if props else False


def get_evidence_node_types() -> List[NodeType]:
    """Get all evidence node types (Family A)."""
    return [
        NodeType.EMPIRICAL_FINDING,
        NodeType.SYNTHESIS_CONCLUSION,
        NodeType.QUALITATIVE_FINDING,
    ]


def get_structural_node_types() -> List[NodeType]:
    """Get all structural node types (Family B)."""
    return [
        NodeType.THEORETICAL_PROPOSITION,
        NodeType.DERIVED_HYPOTHESIS,
        NodeType.CONCEPTUAL_DEFINITION,
        NodeType.CONCEPTUAL_CONSTRAINT,
    ]


def get_interpretive_node_types() -> List[NodeType]:
    """Get all interpretive node types (Family C)."""
    return [
        NodeType.EXPERT_SYNTHESIS,
        NodeType.METHODOLOGICAL_CRITIQUE,
    ]
