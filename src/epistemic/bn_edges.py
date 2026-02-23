"""
Epistemic BN Edge Definitions (Sprint T2-2.2).

Defines the causal edge structure for epistemic variables in the Bayesian network.
This module wires the environmental subgraph connecting:
- Environmental legibility to epistemic processing
- Prediction error types to epistemic affect
- Epistemic affect to downstream outcomes

References:
- CNFA: Cognitive Neuroscience of Architecture
- PE: Prediction Error (predictive processing framework)
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum

from src.epistemic.bn_nodes import (
    EpistemicVariable,
    EPISTEMIC_VARIABLES,
    SOURCE_QUALITY_COMPONENTS,
)


# =============================================================================
# PATHWAY TYPE ENUM (imported from web_of_belief for reference)
# =============================================================================

class PathwayType(str, Enum):
    """
    Effect pathways for environmental influences.

    SUBPERSONAL: Direct physiological effects, no interpretation needed
    PERSONAL_EPISTEMIC: Fully interpretation-mediated effects
    MIXED: Both pathways potentially active
    """
    SUBPERSONAL = "subpersonal"
    PERSONAL_EPISTEMIC = "personal_epistemic"
    MIXED = "mixed"


# =============================================================================
# PATHWAY DEFAULTS LOOKUP (Task 2.4)
# =============================================================================

# Maps environmental variable category keywords to default pathway types
PATHWAY_DEFAULTS: Dict[str, PathwayType] = {
    # Subpersonal — direct physiological, no interpretation needed
    "temperature": PathwayType.SUBPERSONAL,
    "thermal": PathwayType.SUBPERSONAL,
    "circadian": PathwayType.SUBPERSONAL,
    "air_quality": PathwayType.SUBPERSONAL,
    "ventilation": PathwayType.SUBPERSONAL,
    "acoustic_db": PathwayType.SUBPERSONAL,
    "cortisol": PathwayType.SUBPERSONAL,
    "hrv": PathwayType.SUBPERSONAL,
    "heart_rate": PathwayType.SUBPERSONAL,

    # Personal epistemic — fully interpretation-mediated
    "spatial_layout": PathwayType.PERSONAL_EPISTEMIC,
    "wayfinding": PathwayType.PERSONAL_EPISTEMIC,
    "legibility": PathwayType.PERSONAL_EPISTEMIC,
    "social_meaning": PathwayType.PERSONAL_EPISTEMIC,
    "aesthetic_judgment": PathwayType.PERSONAL_EPISTEMIC,
    "functional_meaning": PathwayType.PERSONAL_EPISTEMIC,
    "complexity": PathwayType.PERSONAL_EPISTEMIC,
    "preference": PathwayType.PERSONAL_EPISTEMIC,
    "environmental_legibility": PathwayType.PERSONAL_EPISTEMIC,
    "epistemic": PathwayType.PERSONAL_EPISTEMIC,
    "belief": PathwayType.PERSONAL_EPISTEMIC,
    "coherence": PathwayType.PERSONAL_EPISTEMIC,

    # Mixed — both channels
    "lighting": PathwayType.MIXED,
    "color": PathwayType.MIXED,
    "biophilic_elements": PathwayType.MIXED,
    "biophilia": PathwayType.MIXED,
    "nature": PathwayType.MIXED,
    "noise_meaning": PathwayType.MIXED,
    "crowding": PathwayType.MIXED,
    "ceiling_height": PathwayType.MIXED,
    "enclosure": PathwayType.MIXED,
    "prospect_refuge": PathwayType.MIXED,
    "allostatic": PathwayType.MIXED,
    "wellbeing": PathwayType.MIXED,
}


# =============================================================================
# EDGE DATACLASS
# =============================================================================

@dataclass
class EpistemicEdge:
    """
    A directed causal edge in the epistemic BN.

    Represents a causal relationship from source to target variable,
    with an optional pathway type and edge weight.
    """
    source: str  # Variable ID
    target: str  # Variable ID
    edge_type: str = "causal"  # causal | mediated | conditional
    pathway_type: Optional[str] = None  # subpersonal | personal_epistemic | mixed
    weight: float = 1.0  # Edge strength (used in structural equations)
    description: Optional[str] = None

    def to_tuple(self) -> Tuple[str, str]:
        """Return edge as (source, target) tuple for DAG libraries."""
        return (self.source, self.target)

    def to_dict(self) -> Dict:
        return {
            "source": self.source,
            "target": self.target,
            "edge_type": self.edge_type,
            "pathway_type": self.pathway_type,
            "weight": self.weight,
            "description": self.description,
        }


# =============================================================================
# STUB NODES (for connecting to broader BN)
# =============================================================================

# These stub nodes represent connection points to the existing BN structure.
# They will be replaced by actual nodes once the full BN is integrated.

STUB_OVERALL_WELLBEING = EpistemicVariable(
    var_id="overall_wellbeing",
    name="Overall Wellbeing",
    description="Composite wellbeing outcome (stub node for integration)",
    domain=(0.0, 1.0),
    is_observable=True,
    is_latent=False,
    default_value=0.5,
)

STUB_WAYFINDING_SUCCESS = EpistemicVariable(
    var_id="wayfinding_success",
    name="Wayfinding Success",
    description="Success in navigating the built environment (stub node)",
    domain=(0.0, 1.0),
    is_observable=True,
    is_latent=False,
    default_value=0.5,
)

STUB_ALLOSTATIC_REGULATION = EpistemicVariable(
    var_id="allostatic_regulation",
    name="Allostatic Regulation",
    description="Physiological stress regulation capacity (stub node)",
    domain=(0.0, 1.0),
    is_observable=False,
    is_latent=True,
    default_value=0.5,
)

# Registry of stub nodes
STUB_NODES: Dict[str, EpistemicVariable] = {
    "overall_wellbeing": STUB_OVERALL_WELLBEING,
    "wayfinding_success": STUB_WAYFINDING_SUCCESS,
    "allostatic_regulation": STUB_ALLOSTATIC_REGULATION,
}


# =============================================================================
# ENVIRONMENTAL SUBGRAPH EDGES (Task 2.2)
# =============================================================================

# Core epistemic processing chain
ENVIRONMENTAL_EDGES: List[EpistemicEdge] = [
    # Environmental legibility → epistemic fluency
    # High legibility enables faster, easier formation of coherent interpretations
    EpistemicEdge(
        source="environmental_legibility",
        target="epistemic_fluency",
        edge_type="causal",
        pathway_type="personal_epistemic",
        weight=0.8,
        description="Legible environments enable faster coherent interpretation",
    ),

    # Epistemic fluency → epistemic affect
    # Ease of processing generates positive hedonic signal
    EpistemicEdge(
        source="epistemic_fluency",
        target="epistemic_affect",
        edge_type="causal",
        pathway_type="personal_epistemic",
        weight=0.7,
        description="Processing fluency generates positive epistemic affect",
    ),

    # Epistemic affect → overall wellbeing
    # Positive epistemic states contribute to overall wellbeing
    EpistemicEdge(
        source="epistemic_affect",
        target="overall_wellbeing",
        edge_type="causal",
        pathway_type="personal_epistemic",
        weight=0.5,
        description="Epistemic satisfaction contributes to wellbeing",
    ),

    # Prediction error → epistemic affect edges
    # Each PE type negatively affects epistemic affect

    EpistemicEdge(
        source="functional_PE",
        target="epistemic_affect",
        edge_type="causal",
        pathway_type="personal_epistemic",
        weight=-0.6,  # Negative: PE reduces positive affect
        description="Affordance mismatch generates negative epistemic affect",
    ),

    EpistemicEdge(
        source="navigational_PE",
        target="epistemic_affect",
        edge_type="causal",
        pathway_type="personal_epistemic",
        weight=-0.7,  # Navigational PE has strong affective impact
        description="Spatial disorientation generates negative epistemic affect",
    ),

    EpistemicEdge(
        source="social_PE",
        target="epistemic_affect",
        edge_type="causal",
        pathway_type="personal_epistemic",
        weight=-0.5,
        description="Social script mismatch generates negative epistemic affect",
    ),

    # Environmental legibility → wayfinding success
    # Legible environments support successful navigation
    EpistemicEdge(
        source="environmental_legibility",
        target="wayfinding_success",
        edge_type="causal",
        pathway_type="personal_epistemic",
        weight=0.75,
        description="Legible layouts enable successful wayfinding",
    ),

    # Epistemic affect → allostatic regulation
    # Chronic negative epistemic states impair stress regulation
    EpistemicEdge(
        source="epistemic_affect",
        target="allostatic_regulation",
        edge_type="causal",
        pathway_type="mixed",  # Both cognitive and physiological pathways
        weight=0.4,
        description="Epistemic states influence physiological regulation",
    ),
]


# =============================================================================
# SOURCE QUALITY SUBGRAPH EDGES (Task 2.3)
# =============================================================================

SOURCE_QUALITY_EDGES: List[EpistemicEdge] = [
    # methodological_rigor → source_quality
    # Higher rigor increases source quality
    EpistemicEdge(
        source="methodological_rigor",
        target="source_quality",
        edge_type="causal",
        pathway_type="personal_epistemic",  # Quality assessment is interpretive
        weight=0.35,  # ~35% contribution to source quality
        description="Methodological rigor increases source quality",
    ),

    # theoretical_commitment → source_quality (NEGATIVE influence)
    # High a priori commitment reduces source quality (potential bias)
    EpistemicEdge(
        source="theoretical_commitment",
        target="source_quality",
        edge_type="causal",
        pathway_type="personal_epistemic",
        weight=-0.15,  # Negative: bias reduces quality
        description="Strong theoretical commitment reduces source quality (bias risk)",
    ),

    # independence_of_evidence → source_quality
    # Independent replications increase quality
    EpistemicEdge(
        source="independence_of_evidence",
        target="source_quality",
        edge_type="causal",
        pathway_type="personal_epistemic",
        weight=0.25,  # ~25% contribution
        description="Independent evidence increases source quality",
    ),

    # replication_status → source_quality
    # Replicated findings have higher quality
    EpistemicEdge(
        source="replication_status",
        target="source_quality",
        edge_type="causal",
        pathway_type="personal_epistemic",
        weight=0.25,  # ~25% contribution
        description="Successful replication increases source quality",
    ),

    # source_quality → claim_acceptance
    # Higher source quality increases acceptance probability
    EpistemicEdge(
        source="source_quality",
        target="claim_acceptance",
        edge_type="causal",
        pathway_type="personal_epistemic",
        weight=0.6,  # Strong influence
        description="Source quality drives claim acceptance",
    ),

    # claim_coherence → claim_acceptance
    # Coherence with existing web affects acceptance
    EpistemicEdge(
        source="claim_coherence",
        target="claim_acceptance",
        edge_type="causal",
        pathway_type="personal_epistemic",
        weight=0.4,  # Moderate influence
        description="Coherence with existing beliefs affects acceptance",
    ),
]


# =============================================================================
# COMBINED EDGES (all subgraphs)
# =============================================================================

ALL_EPISTEMIC_EDGES: List[EpistemicEdge] = ENVIRONMENTAL_EDGES + SOURCE_QUALITY_EDGES


# =============================================================================
# EDGE REGISTRY AND UTILITIES
# =============================================================================

def get_environmental_edges() -> List[EpistemicEdge]:
    """Get all edges in the environmental epistemic subgraph."""
    return ENVIRONMENTAL_EDGES.copy()


def get_source_quality_edges() -> List[EpistemicEdge]:
    """Get all edges in the source quality subgraph."""
    return SOURCE_QUALITY_EDGES.copy()


def get_all_edges() -> List[EpistemicEdge]:
    """Get all epistemic edges (all subgraphs combined)."""
    return ALL_EPISTEMIC_EDGES.copy()


def get_edges_as_tuples() -> List[Tuple[str, str]]:
    """Get all edges as (source, target) tuples for DAG construction."""
    return [edge.to_tuple() for edge in ALL_EPISTEMIC_EDGES]


def get_edges_for_variable(var_id: str, as_source: bool = True) -> List[EpistemicEdge]:
    """Get all edges where the variable appears as source or target."""
    if as_source:
        return [e for e in ALL_EPISTEMIC_EDGES if e.source == var_id]
    else:
        return [e for e in ALL_EPISTEMIC_EDGES if e.target == var_id]


def get_all_variables() -> Dict[str, EpistemicVariable]:
    """Get all variables (epistemic + source quality components + stub nodes) for BN construction."""
    all_vars = dict(EPISTEMIC_VARIABLES)
    all_vars.update(SOURCE_QUALITY_COMPONENTS)
    all_vars.update(STUB_NODES)
    return all_vars


def validate_edge_connectivity() -> List[str]:
    """
    Validate that all edge endpoints reference defined variables.
    Returns list of missing variable IDs.
    """
    all_vars = get_all_variables()
    missing = []

    for edge in ALL_EPISTEMIC_EDGES:
        if edge.source not in all_vars:
            missing.append(edge.source)
        if edge.target not in all_vars:
            missing.append(edge.target)

    return list(set(missing))


def is_acyclic() -> bool:
    """
    Check if the edge graph is acyclic (valid DAG).
    Uses Kahn's algorithm for topological sort.
    """
    from collections import defaultdict

    # Build adjacency list and in-degree count
    adj = defaultdict(list)
    in_degree = defaultdict(int)
    all_nodes = set()

    for edge in ALL_EPISTEMIC_EDGES:
        adj[edge.source].append(edge.target)
        in_degree[edge.target] += 1
        all_nodes.add(edge.source)
        all_nodes.add(edge.target)

    # Initialize queue with zero in-degree nodes
    queue = [n for n in all_nodes if in_degree[n] == 0]
    visited = 0

    while queue:
        node = queue.pop(0)
        visited += 1
        for neighbor in adj[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    return visited == len(all_nodes)


def get_topological_order() -> List[str]:
    """Return variables in topological order (parents before children)."""
    from collections import defaultdict

    adj = defaultdict(list)
    in_degree = defaultdict(int)
    all_nodes = set()

    for edge in ALL_EPISTEMIC_EDGES:
        adj[edge.source].append(edge.target)
        in_degree[edge.target] += 1
        all_nodes.add(edge.source)
        all_nodes.add(edge.target)

    queue = [n for n in all_nodes if in_degree[n] == 0]
    result = []

    while queue:
        node = queue.pop(0)
        result.append(node)
        for neighbor in adj[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    return result


# =============================================================================
# PATHWAY TYPE ASSIGNMENT (Task 2.4)
# =============================================================================

def assign_pathway_type(
    edge: Any,
    lookup: Dict[str, PathwayType] = None,
    default: PathwayType = PathwayType.MIXED
) -> PathwayType:
    """
    Assign pathway_type to an edge based on its source node.

    Uses PATHWAY_DEFAULTS lookup table to determine pathway type based on
    keywords found in the source variable name. Defaults to MIXED if no match.

    Args:
        edge: An edge object with a 'source' attribute (var_id string)
        lookup: Keyword-to-PathwayType mapping (defaults to PATHWAY_DEFAULTS)
        default: Default pathway type if no match found (defaults to MIXED)

    Returns:
        PathwayType for the edge
    """
    if lookup is None:
        lookup = PATHWAY_DEFAULTS

    # Get source node name (support both string and object with .source attribute)
    if hasattr(edge, 'source'):
        source = edge.source
    elif isinstance(edge, tuple):
        source = edge[0]
    else:
        source = str(edge)

    source_lower = source.lower()

    # Check for keyword matches in lookup
    for keyword, pathway_type in lookup.items():
        if keyword in source_lower:
            return pathway_type

    return default


def tag_edges_with_pathway(
    edges: List[Any],
    lookup: Dict[str, PathwayType] = None
) -> List[Tuple[Any, PathwayType]]:
    """
    Tag a list of edges with their pathway types.

    Args:
        edges: List of edge objects (with source attribute or tuples)
        lookup: Keyword-to-PathwayType mapping

    Returns:
        List of (edge, PathwayType) tuples
    """
    return [(edge, assign_pathway_type(edge, lookup)) for edge in edges]


def get_edges_by_pathway(pathway: PathwayType) -> List[EpistemicEdge]:
    """Get all epistemic edges with a specific pathway type."""
    return [e for e in ALL_EPISTEMIC_EDGES if e.pathway_type == pathway.value]


def validate_all_edges_tagged() -> List[EpistemicEdge]:
    """
    Check that all edges have non-null pathway_type.
    Returns list of untagged edges (should be empty).
    """
    return [e for e in ALL_EPISTEMIC_EDGES if e.pathway_type is None]
