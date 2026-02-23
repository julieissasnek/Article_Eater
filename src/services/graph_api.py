"""
Graph API Service
=================

Provides graph data for the Evidence Explorer GUI.

Tier 1 implementation per expert panel feedback:
- Graph export in Cytoscape.js compatible format
- Node detail data for side panel
- Search across beliefs, papers, and authors

Date: January 20, 2026
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
import logging
from datetime import datetime, timezone

from src.services.web_of_belief import (
    WebOfBelief,
    Belief,
    BeliefStatus,
    ConstraintType,
    CausalDirection
)

logger = logging.getLogger(__name__)


# =============================================================================
# Graph Export Data Structures
# =============================================================================

@dataclass
class GraphNode:
    """
    A node in the graph export.

    Per expert panel (Pearl): Correlational edges should be visually
    distinct from causal edges.
    """
    id: str
    label: str
    credence: float
    outcome_category: Optional[str]
    status: str
    has_conflict: bool
    contested: bool
    source_depth: str
    node_size: float  # Computed from credence

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'label': self.label,
            'credence': self.credence,
            'outcome_category': self.outcome_category,
            'status': self.status,
            'has_conflict': self.has_conflict,
            'contested': self.contested,
            'source_depth': self.source_depth,
            'node_size': self.node_size
        }


@dataclass
class GraphEdge:
    """
    An edge in the graph export.

    Per expert panel (Pearl): CORRELATIONAL edges should have
    no arrowhead and reduced opacity.
    """
    source: str
    target: str
    constraint_type: str
    strength: float
    causal_direction: str
    is_correlational: bool
    is_bridge: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            'source': self.source,
            'target': self.target,
            'type': self.constraint_type,
            'strength': self.strength,
            'causal_direction': self.causal_direction,
            'is_correlational': self.is_correlational,
            'is_bridge': self.is_bridge
        }


@dataclass
class GraphMetadata:
    """Metadata about the graph."""
    total_beliefs: int
    total_constraints: int
    coherence_score: float
    contested_count: int
    stub_count: int
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            'total_beliefs': self.total_beliefs,
            'total_constraints': self.total_constraints,
            'coherence_score': self.coherence_score,
            'contested_count': self.contested_count,
            'stub_count': self.stub_count,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class GraphExport:
    """
    Complete graph export for Cytoscape.js visualization.

    Schema: ae.graph_export.v1
    """
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    metadata: GraphMetadata

    def to_dict(self) -> Dict[str, Any]:
        return {
            'nodes': [n.to_dict() for n in self.nodes],
            'edges': [e.to_dict() for e in self.edges],
            'metadata': self.metadata.to_dict()
        }


# =============================================================================
# Node Detail Data Structures
# =============================================================================

@dataclass
class SourceInfo:
    """Information about a source paper."""
    paper_id: str
    title: Optional[str]
    strength: float
    year: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'paper_id': self.paper_id,
            'title': self.title,
            'strength': self.strength,
            'year': self.year
        }


@dataclass
class ConstraintInfo:
    """Information about a constraint for detail panel."""
    constraint_id: str
    target_belief_id: str
    target_belief_content: str
    constraint_type: str
    strength: float
    direction: str  # "outgoing" or "incoming"
    causal_direction: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            'constraint_id': self.constraint_id,
            'target_belief_id': self.target_belief_id,
            'target_belief_content': self.target_belief_content,
            'type': self.constraint_type,
            'strength': self.strength,
            'direction': self.direction,
            'causal_direction': self.causal_direction
        }


@dataclass
class ScopeDisplay:
    """
    Scope conditions formatted for display.

    Per expert panel (Kaplan): Show applies/does-not-apply/unknown explicitly.
    """
    applies: List[str]
    does_not_apply: List[str]
    unknown: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            'applies': self.applies,
            'does_not_apply': self.does_not_apply,
            'unknown': self.unknown
        }


@dataclass
class NodeDetail:
    """
    Complete node detail for side panel display.

    Per expert panel (Simon): Progressive disclosure - show simplified
    view by default with expandable sections.
    """
    belief_id: str
    content: str
    credence: float
    credence_uncertainty: float
    status: str
    contested: bool
    credence_range: Optional[Tuple[float, float]]

    # Classification
    outcome_category: Optional[str]
    environment_id: Optional[str]
    level: str  # epistemic level

    # Sources
    sources: List[SourceInfo]
    source_depth: str

    # Constraints
    outgoing_constraints: List[ConstraintInfo]
    incoming_constraints: List[ConstraintInfo]

    # Scope and enabling conditions
    scope: Optional[ScopeDisplay]
    enabling_conditions: Optional[Dict[str, Any]]

    # History
    credence_history_length: int
    is_stable: bool

    def to_dict(self) -> Dict[str, Any]:
        result = {
            'belief_id': self.belief_id,
            'content': self.content,
            'credence': self.credence,
            'credence_uncertainty': self.credence_uncertainty,
            'status': self.status,
            'contested': self.contested,
            'credence_range': list(self.credence_range) if self.credence_range else None,
            'outcome_category': self.outcome_category,
            'environment_id': self.environment_id,
            'level': self.level,
            'sources': [s.to_dict() for s in self.sources],
            'source_depth': self.source_depth,
            'outgoing_constraints': [c.to_dict() for c in self.outgoing_constraints],
            'incoming_constraints': [c.to_dict() for c in self.incoming_constraints],
            'scope': self.scope.to_dict() if self.scope else None,
            'enabling_conditions': self.enabling_conditions,
            'credence_history_length': self.credence_history_length,
            'is_stable': self.is_stable
        }
        return result

    def to_simplified_dict(self) -> Dict[str, Any]:
        """
        Simplified view for novice users.

        Per expert panel (Simon): Show traffic-light confidence,
        basic info, with expand option.
        """
        # Traffic light: green > 0.7, yellow 0.4-0.7, red < 0.4
        if self.credence >= 0.7:
            confidence_level = "HIGH"
        elif self.credence >= 0.4:
            confidence_level = "MEDIUM"
        else:
            confidence_level = "LOW"

        return {
            'belief_id': self.belief_id,
            'content': self.content,
            'confidence_level': confidence_level,
            'source_count': len(self.sources),
            'has_disagreement': self.contested,
            'status': self.status
        }


# =============================================================================
# Search Data Structures
# =============================================================================

class SearchResultType(Enum):
    """Types of search results."""
    BELIEF = "belief"
    PAPER = "paper"
    AUTHOR = "author"


@dataclass
class SearchResult:
    """A single search result."""
    result_type: SearchResultType
    id: str
    title: str
    snippet: str
    relevance: float
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'type': self.result_type.value,
            'id': self.id,
            'title': self.title,
            'snippet': self.snippet,
            'relevance': self.relevance,
            'metadata': self.metadata
        }


@dataclass
class SearchResults:
    """
    Grouped search results.

    Per expert panel (Bates): Show results by category
    (beliefs, papers, authors) with clear separation.
    """
    beliefs: List[SearchResult]
    papers: List[SearchResult]
    authors: List[SearchResult]
    query: str
    total_count: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            'query': self.query,
            'total_count': self.total_count,
            'beliefs': [r.to_dict() for r in self.beliefs],
            'papers': [r.to_dict() for r in self.papers],
            'authors': [r.to_dict() for r in self.authors]
        }


# =============================================================================
# Graph API Service
# =============================================================================

class GraphAPIService:
    """
    Service for graph API endpoints.

    Provides data for Evidence Explorer GUI.
    """

    def __init__(self, web: WebOfBelief, paper_metadata: Optional[Dict[str, Dict]] = None):
        """
        Initialize the service.

        Args:
            web: The web of belief to export
            paper_metadata: Optional dict of paper_id -> metadata (title, authors, year)
        """
        self.web = web
        self.paper_metadata = paper_metadata or {}

    def export_graph(
        self,
        max_nodes: Optional[int] = None,
        min_credence: float = 0.0,
        outcome_filter: Optional[str] = None,
        include_stubs: bool = True
    ) -> GraphExport:
        """
        Export the web as a graph for visualization.

        Args:
            max_nodes: Maximum nodes to return (highest credence first)
            min_credence: Minimum credence threshold
            outcome_filter: Filter by outcome category prefix
            include_stubs: Whether to include stub beliefs

        Returns:
            GraphExport with nodes, edges, and metadata
        """
        # Filter beliefs
        beliefs = list(self.web.beliefs.values())

        if not include_stubs:
            beliefs = [b for b in beliefs if b.status != BeliefStatus.STUB]

        if min_credence > 0:
            beliefs = [b for b in beliefs if b.credence.value >= min_credence]

        if outcome_filter:
            beliefs = [
                b for b in beliefs
                if b.outcome_id and b.outcome_id.startswith(outcome_filter)
            ]

        # Sort by credence and limit
        beliefs.sort(key=lambda b: b.credence.value, reverse=True)
        if max_nodes:
            beliefs = beliefs[:max_nodes]

        belief_ids = {b.belief_id for b in beliefs}

        # Build nodes
        nodes = []
        for belief in beliefs:
            has_conflict = self._belief_has_conflict(belief)
            nodes.append(GraphNode(
                id=belief.belief_id,
                label=self._truncate(belief.content, 80),
                credence=belief.credence.value,
                outcome_category=belief.outcome_id,
                status=belief.status.value,
                has_conflict=has_conflict,
                contested=belief.contested,
                source_depth=belief.source_depth.value,
                node_size=self._compute_node_size(belief.credence.value)
            ))

        # Build edges (only between included nodes)
        edges = []
        for constraint in self.web.constraints.values():
            if constraint.source_id in belief_ids and constraint.target_id in belief_ids:
                is_correlational = constraint.causal_direction == CausalDirection.CORRELATIONAL
                is_bridge = constraint.constraint_type == ConstraintType.BRIDGES
                edges.append(GraphEdge(
                    source=constraint.source_id,
                    target=constraint.target_id,
                    constraint_type=constraint.constraint_type.value,
                    strength=constraint.strength,
                    causal_direction=constraint.causal_direction.value,
                    is_correlational=is_correlational,
                    is_bridge=is_bridge
                ))

        # Build metadata
        contested_count = sum(1 for b in beliefs if b.contested)
        stub_count = sum(1 for b in beliefs if b.status == BeliefStatus.STUB)
        coherence_score = getattr(self.web, 'coherence_score', 0.0)
        if callable(coherence_score):
            coherence_score = 0.0  # Method, not value

        metadata = GraphMetadata(
            total_beliefs=len(nodes),
            total_constraints=len(edges),
            coherence_score=coherence_score,
            contested_count=contested_count,
            stub_count=stub_count
        )

        return GraphExport(nodes=nodes, edges=edges, metadata=metadata)

    def get_node_detail(self, belief_id: str) -> Optional[NodeDetail]:
        """
        Get detailed information about a belief node.

        Args:
            belief_id: The belief ID to look up

        Returns:
            NodeDetail or None if not found
        """
        belief = self.web.beliefs.get(belief_id)
        if not belief:
            return None

        # Build source info
        sources = []
        for paper_id in belief.paper_ids:
            meta = self.paper_metadata.get(paper_id, {})
            sources.append(SourceInfo(
                paper_id=paper_id,
                title=meta.get('title'),
                strength=meta.get('strength', 0.5),
                year=meta.get('year')
            ))

        # Build constraint info
        outgoing = []
        incoming = []
        for constraint in self.web.constraints.values():
            if constraint.source_id == belief_id:
                target = self.web.beliefs.get(constraint.target_id)
                if target:
                    outgoing.append(ConstraintInfo(
                        constraint_id=constraint.constraint_id,
                        target_belief_id=constraint.target_id,
                        target_belief_content=self._truncate(target.content, 50),
                        constraint_type=constraint.constraint_type.value,
                        strength=constraint.strength,
                        direction="outgoing",
                        causal_direction=constraint.causal_direction.value
                    ))
            elif constraint.target_id == belief_id:
                source = self.web.beliefs.get(constraint.source_id)
                if source:
                    incoming.append(ConstraintInfo(
                        constraint_id=constraint.constraint_id,
                        target_belief_id=constraint.source_id,
                        target_belief_content=self._truncate(source.content, 50),
                        constraint_type=constraint.constraint_type.value,
                        strength=constraint.strength,
                        direction="incoming",
                        causal_direction=constraint.causal_direction.value
                    ))

        # Build scope display
        scope_display = None
        if belief.scope:
            applies = []
            does_not_apply = []
            unknown = []

            if belief.scope.setting:
                applies.append(f"Setting: {belief.scope.setting}")
            else:
                unknown.append("Setting")

            if belief.scope.population:
                applies.append(f"Population: {belief.scope.population}")
            else:
                unknown.append("Population")

            if belief.scope.duration:
                applies.append(f"Duration: {belief.scope.duration}")
            else:
                unknown.append("Duration")

            scope_display = ScopeDisplay(
                applies=applies,
                does_not_apply=does_not_apply,
                unknown=unknown
            )

        # Build enabling conditions
        enabling_dict = None
        if belief.enabling_conditions:
            enabling_dict = belief.enabling_conditions.to_dict()

        # Credence range for contested beliefs
        credence_range = None
        if belief.contested:
            credence_range = belief.credence_range()

        return NodeDetail(
            belief_id=belief.belief_id,
            content=belief.content,
            credence=belief.credence.value,
            credence_uncertainty=belief.credence.uncertainty,
            status=belief.status.value,
            contested=belief.contested,
            credence_range=credence_range,
            outcome_category=belief.outcome_id,
            environment_id=belief.environment_id,
            level=belief.level.value,
            sources=sources,
            source_depth=belief.source_depth.value,
            outgoing_constraints=outgoing,
            incoming_constraints=incoming,
            scope=scope_display,
            enabling_conditions=enabling_dict,
            credence_history_length=len(belief.credence_history),
            is_stable=belief.is_stable() if belief.credence_history else True
        )

    def search(
        self,
        query: str,
        include_beliefs: bool = True,
        include_papers: bool = True,
        include_authors: bool = True,
        max_results: int = 20
    ) -> SearchResults:
        """
        Search across beliefs, papers, and authors.

        Per expert panel (Bates): Search should match beliefs,
        papers, and authors with clear category separation.

        Args:
            query: Search query string
            include_beliefs: Include belief results
            include_papers: Include paper results
            include_authors: Include author results
            max_results: Maximum results per category

        Returns:
            SearchResults with grouped results
        """
        query_lower = query.lower()
        belief_results = []
        paper_results = []
        author_results = []

        # Search beliefs
        if include_beliefs:
            for belief in self.web.beliefs.values():
                if query_lower in belief.content.lower():
                    relevance = self._compute_relevance(query_lower, belief.content.lower())
                    belief_results.append(SearchResult(
                        result_type=SearchResultType.BELIEF,
                        id=belief.belief_id,
                        title=self._truncate(belief.content, 60),
                        snippet=belief.content,
                        relevance=relevance,
                        metadata={
                            'credence': belief.credence.value,
                            'status': belief.status.value
                        }
                    ))

        # Search papers
        if include_papers:
            seen_papers = set()
            for belief in self.web.beliefs.values():
                for paper_id in belief.paper_ids:
                    if paper_id in seen_papers:
                        continue
                    seen_papers.add(paper_id)

                    meta = self.paper_metadata.get(paper_id, {})
                    title = meta.get('title', paper_id)
                    if query_lower in title.lower() or query_lower in paper_id.lower():
                        relevance = self._compute_relevance(query_lower, title.lower())
                        paper_results.append(SearchResult(
                            result_type=SearchResultType.PAPER,
                            id=paper_id,
                            title=title,
                            snippet=f"Year: {meta.get('year', 'Unknown')}",
                            relevance=relevance,
                            metadata=meta
                        ))

        # Search authors
        if include_authors:
            author_beliefs = {}  # author -> list of belief ids
            for belief in self.web.beliefs.values():
                for paper_id in belief.paper_ids:
                    meta = self.paper_metadata.get(paper_id, {})
                    authors = meta.get('authors', [])
                    for author in authors:
                        if query_lower in author.lower():
                            if author not in author_beliefs:
                                author_beliefs[author] = []
                            author_beliefs[author].append(belief.belief_id)

            for author, belief_ids in author_beliefs.items():
                relevance = self._compute_relevance(query_lower, author.lower())
                author_results.append(SearchResult(
                    result_type=SearchResultType.AUTHOR,
                    id=author,
                    title=author,
                    snippet=f"{len(belief_ids)} beliefs in web",
                    relevance=relevance,
                    metadata={'belief_count': len(belief_ids)}
                ))

        # Sort by relevance and limit
        belief_results.sort(key=lambda r: r.relevance, reverse=True)
        paper_results.sort(key=lambda r: r.relevance, reverse=True)
        author_results.sort(key=lambda r: r.relevance, reverse=True)

        belief_results = belief_results[:max_results]
        paper_results = paper_results[:max_results]
        author_results = author_results[:max_results]

        total = len(belief_results) + len(paper_results) + len(author_results)

        return SearchResults(
            beliefs=belief_results,
            papers=paper_results,
            authors=author_results,
            query=query,
            total_count=total
        )

    def get_top_beliefs(self, n: int = 30) -> List[Dict[str, Any]]:
        """
        Get top N beliefs by credence for default view.

        Per expert panel (Simon): Default view should show
        top 20-30 beliefs, not all.
        """
        beliefs = list(self.web.beliefs.values())
        beliefs.sort(key=lambda b: b.credence.value, reverse=True)
        beliefs = beliefs[:n]

        return [
            {
                'belief_id': b.belief_id,
                'content': self._truncate(b.content, 80),
                'credence': b.credence.value,
                'outcome_category': b.outcome_id,
                'status': b.status.value,
                'contested': b.contested
            }
            for b in beliefs
        ]

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def _belief_has_conflict(self, belief: Belief) -> bool:
        """Check if a belief has any conflict constraints."""
        for constraint in self.web.constraints.values():
            if constraint.source_id == belief.belief_id or constraint.target_id == belief.belief_id:
                if constraint.constraint_type in (
                    ConstraintType.CONTRADICTS,
                    ConstraintType.STRONG_TENSION
                ):
                    return True
        return False

    def _compute_node_size(self, credence: float) -> float:
        """
        Compute node size from credence.

        Scale: 0.3 (low credence) to 1.0 (high credence)
        """
        return 0.3 + 0.7 * credence

    def _compute_relevance(self, query: str, text: str) -> float:
        """
        Compute search relevance score.

        Simple TF-based scoring.
        """
        if query == text:
            return 1.0
        if text.startswith(query):
            return 0.9
        count = text.count(query)
        return min(0.8, 0.5 + 0.1 * count)

    def _truncate(self, text: str, max_len: int) -> str:
        """Truncate text with ellipsis."""
        if len(text) <= max_len:
            return text
        return text[:max_len - 3] + "..."
