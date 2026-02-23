"""
Network Visualization Service — Sprint 3.0.3-E
2026-02-10

Deep vis.js integration for belief network visualization.
Provides graph data, layout algorithms, clustering, and metrics.

Expert Panel Guidance:
- Shneiderman: Overview first, zoom and filter, details on demand
- Pearl: Causal direction visualization
- Tufte: Maximize data-ink ratio
"""

import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import logging

logger = logging.getLogger(__name__)


# =============================================================================
# Data Structures
# =============================================================================

class LayoutAlgorithm(Enum):
    """Available layout algorithms for vis.js."""
    FORCE_DIRECTED = "forceAtlas2Based"
    HIERARCHICAL = "hierarchicalRepulsion"
    BARNESHET = "barnesHut"
    REPULSION = "repulsion"


class ClusterMode(Enum):
    """Clustering modes for graph organization."""
    NONE = "none"
    THEORY = "theory"
    LEVEL = "level"
    COMMUNITY = "community"
    STATUS = "status"


class EdgeType(Enum):
    """Types of constraint edges."""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    CAUSAL = "causal"


@dataclass
class GraphNode:
    """A node in the belief network graph."""
    id: str
    label: str
    title: str  # Tooltip
    color: str
    size: float
    shape: str = "dot"
    level: Optional[str] = None
    status: Optional[str] = None
    credence: float = 0.5
    theory: Optional[str] = None
    community: Optional[str] = None
    entrenchment: float = 0.0
    # Computed metrics
    degree: int = 0
    betweenness: float = 0.0
    clustering_coefficient: float = 0.0
    # Grouping
    group: Optional[str] = None
    hidden: bool = False

    def to_vis_dict(self) -> Dict[str, Any]:
        """Convert to vis.js node format."""
        return {
            "id": self.id,
            "label": self.label,
            "title": self.title,
            "color": self.color,
            "size": self.size,
            "shape": self.shape,
            "group": self.group,
            "hidden": self.hidden,
            # Custom data for interaction
            "level": self.level,
            "status": self.status,
            "credence": self.credence,
            "theory": self.theory,
            "entrenchment": self.entrenchment,
            "degree": self.degree,
        }


@dataclass
class GraphEdge:
    """An edge (constraint) in the belief network graph."""
    id: str
    source: str  # from node
    target: str  # to node
    weight: float
    edge_type: EdgeType
    color: str
    width: float = 1.0
    title: str = ""  # Tooltip
    arrows: str = "to"
    dashes: bool = False
    smooth: bool = True
    hidden: bool = False

    def to_vis_dict(self) -> Dict[str, Any]:
        """Convert to vis.js edge format."""
        return {
            "id": self.id,
            "from": self.source,
            "to": self.target,
            "color": {"color": self.color, "highlight": self.color},
            "width": self.width,
            "title": self.title,
            "arrows": {"to": {"enabled": self.arrows == "to", "scaleFactor": 0.5}},
            "dashes": self.dashes,
            "smooth": {"enabled": self.smooth, "type": "curvedCW", "roundness": 0.2},
            "hidden": self.hidden,
        }


@dataclass
class GraphMetrics:
    """Computed metrics for the graph."""
    node_count: int = 0
    edge_count: int = 0
    density: float = 0.0
    average_degree: float = 0.0
    clustering_coefficient: float = 0.0
    components: int = 1
    diameter: int = 0
    # Status breakdown
    accepted_count: int = 0
    contested_count: int = 0
    stub_count: int = 0
    rejected_count: int = 0
    # Level breakdown
    theoretical_count: int = 0
    empirical_count: int = 0
    methodological_count: int = 0


@dataclass
class GraphData:
    """Complete graph data for vis.js visualization."""
    nodes: List[GraphNode] = field(default_factory=list)
    edges: List[GraphEdge] = field(default_factory=list)
    metrics: GraphMetrics = field(default_factory=GraphMetrics)
    clusters: Dict[str, List[str]] = field(default_factory=dict)

    def to_vis_dict(self) -> Dict[str, Any]:
        """Convert to vis.js format."""
        return {
            "nodes": [n.to_vis_dict() for n in self.nodes if not n.hidden],
            "edges": [e.to_vis_dict() for e in self.edges if not e.hidden],
        }

    def to_json(self) -> str:
        """Serialize to JSON for frontend."""
        return json.dumps(self.to_vis_dict())


# =============================================================================
# Color Schemes
# =============================================================================

STATUS_COLORS = {
    "ACCEPTED": "#2E7D32",      # Green
    "ESTABLISHED": "#2E7D32",   # Green
    "ENTRENCHED": "#1B5E20",    # Dark Green
    "CONTESTED": "#F57C00",     # Orange
    "STUB": "#9E9E9E",          # Gray
    "TENTATIVE": "#64B5F6",     # Light Blue
    "REJECTED": "#C62828",      # Red
}

LEVEL_COLORS = {
    "THEORETICAL": "#7B1FA2",   # Purple
    "EMPIRICAL": "#1976D2",     # Blue
    "METHODOLOGICAL": "#00838F", # Teal
    "INTERMEDIATE": "#5E35B1",  # Deep Purple
}

EDGE_COLORS = {
    "positive": "#4CAF50",      # Green
    "negative": "#F44336",      # Red
    "neutral": "#9E9E9E",       # Gray
    "causal": "#2196F3",        # Blue
}

THEORY_COLORS = {
    "ART": "#E91E63",           # Pink
    "SRT": "#9C27B0",           # Purple
    "Biophilia": "#4CAF50",     # Green
    "Environmental Psychology": "#2196F3",  # Blue
    "Prospect-Refuge": "#FF9800", # Orange
    "Default": "#607D8B",       # Blue Gray
}


# =============================================================================
# Network Service
# =============================================================================

class NetworkService:
    """
    Service for building and analyzing belief network visualizations.

    Provides:
    - Graph construction from WebOfBelief data
    - Multiple layout algorithms
    - Clustering by theory/level/community/status
    - Graph metrics computation
    - Search and highlight
    - Filtering and visibility control
    """

    def __init__(self):
        self.graph_data: Optional[GraphData] = None
        self._adjacency: Dict[str, Set[str]] = {}

    # =========================================================================
    # Graph Construction
    # =========================================================================

    def build_graph_from_beliefs(
        self,
        beliefs: List[Dict[str, Any]],
        constraints: Optional[List[Dict[str, Any]]] = None,
        max_nodes: int = 200,
        min_credence: float = 0.0
    ) -> GraphData:
        """
        Build graph data from belief and constraint data.

        Args:
            beliefs: List of belief dictionaries
            constraints: List of constraint dictionaries
            max_nodes: Maximum nodes to include (highest credence first)
            min_credence: Minimum credence threshold
        """
        # Filter and sort beliefs
        def get_credence_value(b):
            cred = b.get("credence", 0)
            if isinstance(cred, dict):
                return cred.get("point", 0)
            return cred

        filtered_beliefs = [
            b for b in beliefs
            if get_credence_value(b) >= min_credence
        ]
        sorted_beliefs = sorted(
            filtered_beliefs,
            key=get_credence_value,
            reverse=True
        )[:max_nodes]

        # Build node set for constraint filtering
        belief_ids = {b.get("id", b.get("belief_id", "")) for b in sorted_beliefs}

        # Create nodes
        nodes = []
        for belief in sorted_beliefs:
            node = self._create_node(belief)
            nodes.append(node)

        # Create edges from constraints
        edges = []
        if constraints:
            for i, constraint in enumerate(constraints):
                edge = self._create_edge(constraint, i, belief_ids)
                if edge:
                    edges.append(edge)

        # Build adjacency for metrics
        self._build_adjacency(nodes, edges)

        # Compute node metrics
        for node in nodes:
            node.degree = len(self._adjacency.get(node.id, set()))

        # Compute graph metrics
        metrics = self._compute_metrics(nodes, edges)

        self.graph_data = GraphData(
            nodes=nodes,
            edges=edges,
            metrics=metrics
        )

        return self.graph_data

    def _create_node(self, belief: Dict[str, Any]) -> GraphNode:
        """Create a graph node from belief data."""
        belief_id = belief.get("id", belief.get("belief_id", "unknown"))
        content = belief.get("content", "")
        credence = belief.get("credence", 0.5)
        if isinstance(credence, dict):
            credence = credence.get("point", 0.5)

        status = belief.get("status", "STUB")
        if hasattr(status, "value"):
            status = status.value.upper()
        elif isinstance(status, str):
            status = status.upper()

        level = belief.get("level", "EMPIRICAL")
        if hasattr(level, "value"):
            level = level.value.upper()
        elif isinstance(level, str):
            level = level.upper()

        theory = belief.get("theory", belief.get("theory_ids", []))
        if isinstance(theory, list) and theory:
            theory = theory[0]
        elif isinstance(theory, list):
            theory = None

        # Determine color based on status
        color = STATUS_COLORS.get(status, "#9E9E9E")

        # Size based on credence (10-40)
        size = 10 + (credence * 30)

        # Truncate label
        label = content[:35] + "..." if len(content) > 35 else content

        # Build tooltip
        title = f"""<b>{content}</b><br>
Credence: {credence:.2f}<br>
Status: {status}<br>
Level: {level}"""
        if theory:
            title += f"<br>Theory: {theory}"

        return GraphNode(
            id=belief_id,
            label=label,
            title=title,
            color=color,
            size=size,
            level=level,
            status=status,
            credence=credence,
            theory=theory,
            entrenchment=belief.get("entrenchment", 0.0)
        )

    def _create_edge(
        self,
        constraint: Dict[str, Any],
        index: int,
        valid_ids: Set[str]
    ) -> Optional[GraphEdge]:
        """Create a graph edge from constraint data."""
        source = constraint.get("source_id", constraint.get("from", ""))
        target = constraint.get("target_id", constraint.get("to", ""))

        # Skip edges with missing nodes
        if source not in valid_ids or target not in valid_ids:
            return None

        # Determine edge type and color
        polarity = constraint.get("polarity", "NEUTRAL")
        weight = constraint.get("weight", constraint.get("strength", 0.5))

        if polarity == "POSITIVE" or weight > 0.5:
            edge_type = EdgeType.POSITIVE
            color = EDGE_COLORS["positive"]
        elif polarity == "NEGATIVE" or weight < -0.5:
            edge_type = EdgeType.NEGATIVE
            color = EDGE_COLORS["negative"]
            weight = abs(weight)
        else:
            edge_type = EdgeType.NEUTRAL
            color = EDGE_COLORS["neutral"]

        # Check for causal edge
        if constraint.get("causal_direction") or constraint.get("is_causal"):
            edge_type = EdgeType.CAUSAL
            color = EDGE_COLORS["causal"]

        # Width based on weight (1-4)
        width = 1 + (abs(weight) * 3)

        # Tooltip
        title = f"{edge_type.value.capitalize()} constraint (weight: {weight:.2f})"
        if constraint.get("reason"):
            title += f"<br>{constraint['reason']}"

        return GraphEdge(
            id=f"e{index}",
            source=source,
            target=target,
            weight=weight,
            edge_type=edge_type,
            color=color,
            width=width,
            title=title,
            dashes=(edge_type == EdgeType.NEGATIVE)
        )

    def _build_adjacency(
        self,
        nodes: List[GraphNode],
        edges: List[GraphEdge]
    ) -> None:
        """Build adjacency list for metric computation."""
        self._adjacency = {n.id: set() for n in nodes}

        for edge in edges:
            if edge.source in self._adjacency:
                self._adjacency[edge.source].add(edge.target)
            if edge.target in self._adjacency:
                self._adjacency[edge.target].add(edge.source)

    def _compute_metrics(
        self,
        nodes: List[GraphNode],
        edges: List[GraphEdge]
    ) -> GraphMetrics:
        """Compute graph-level metrics."""
        n = len(nodes)
        m = len(edges)

        # Density
        density = (2 * m) / (n * (n - 1)) if n > 1 else 0

        # Average degree
        degrees = [len(self._adjacency.get(node.id, set())) for node in nodes]
        avg_degree = sum(degrees) / n if n > 0 else 0

        # Status breakdown
        status_counts = {}
        for node in nodes:
            status = node.status or "STUB"
            status_counts[status] = status_counts.get(status, 0) + 1

        # Level breakdown
        level_counts = {}
        for node in nodes:
            level = node.level or "EMPIRICAL"
            level_counts[level] = level_counts.get(level, 0) + 1

        return GraphMetrics(
            node_count=n,
            edge_count=m,
            density=density,
            average_degree=avg_degree,
            accepted_count=status_counts.get("ACCEPTED", 0) + status_counts.get("ESTABLISHED", 0),
            contested_count=status_counts.get("CONTESTED", 0),
            stub_count=status_counts.get("STUB", 0) + status_counts.get("TENTATIVE", 0),
            rejected_count=status_counts.get("REJECTED", 0),
            theoretical_count=level_counts.get("THEORETICAL", 0),
            empirical_count=level_counts.get("EMPIRICAL", 0),
            methodological_count=level_counts.get("METHODOLOGICAL", 0),
        )

    # =========================================================================
    # Clustering
    # =========================================================================

    def apply_clustering(
        self,
        mode: ClusterMode,
        graph_data: Optional[GraphData] = None
    ) -> Dict[str, List[str]]:
        """
        Apply clustering to organize nodes into groups.

        Returns dict mapping cluster name to list of node IDs.
        """
        data = graph_data or self.graph_data
        if not data:
            return {}

        clusters: Dict[str, List[str]] = {}

        for node in data.nodes:
            if mode == ClusterMode.THEORY:
                cluster_key = node.theory or "Unassigned"
            elif mode == ClusterMode.LEVEL:
                cluster_key = node.level or "Unknown"
            elif mode == ClusterMode.STATUS:
                cluster_key = node.status or "Unknown"
            elif mode == ClusterMode.COMMUNITY:
                cluster_key = node.community or "Default"
            else:
                cluster_key = "All"

            if cluster_key not in clusters:
                clusters[cluster_key] = []
            clusters[cluster_key].append(node.id)

            # Assign group for vis.js clustering
            node.group = cluster_key

        data.clusters = clusters
        return clusters

    # =========================================================================
    # Filtering and Visibility
    # =========================================================================

    def filter_nodes(
        self,
        status: Optional[List[str]] = None,
        level: Optional[List[str]] = None,
        min_credence: float = 0.0,
        theories: Optional[List[str]] = None,
        search: Optional[str] = None,
        graph_data: Optional[GraphData] = None
    ) -> int:
        """
        Filter nodes by criteria. Returns count of visible nodes.

        Modifies node.hidden in place.
        """
        data = graph_data or self.graph_data
        if not data:
            return 0

        visible_count = 0
        visible_ids = set()

        for node in data.nodes:
            hidden = False

            # Status filter
            if status and node.status not in status:
                hidden = True

            # Level filter
            if level and node.level not in level:
                hidden = True

            # Credence filter
            if node.credence < min_credence:
                hidden = True

            # Theory filter
            if theories and node.theory not in theories:
                hidden = True

            # Search filter
            if search:
                search_lower = search.lower()
                if (search_lower not in node.label.lower() and
                    search_lower not in (node.title or "").lower()):
                    hidden = True

            node.hidden = hidden
            if not hidden:
                visible_count += 1
                visible_ids.add(node.id)

        # Hide edges where either endpoint is hidden
        for edge in data.edges:
            edge.hidden = (edge.source not in visible_ids or
                          edge.target not in visible_ids)

        return visible_count

    def highlight_nodes(
        self,
        node_ids: List[str],
        highlight_color: str = "#FFD700",
        graph_data: Optional[GraphData] = None
    ) -> None:
        """Highlight specific nodes."""
        data = graph_data or self.graph_data
        if not data:
            return

        highlight_set = set(node_ids)

        for node in data.nodes:
            if node.id in highlight_set:
                node.color = highlight_color
                node.size *= 1.5

    def reset_highlight(
        self,
        graph_data: Optional[GraphData] = None
    ) -> None:
        """Reset all node highlighting."""
        data = graph_data or self.graph_data
        if not data:
            return

        for node in data.nodes:
            node.color = STATUS_COLORS.get(node.status or "STUB", "#9E9E9E")
            node.size = 10 + (node.credence * 30)

    # =========================================================================
    # Neighborhood Exploration
    # =========================================================================

    def get_neighborhood(
        self,
        node_id: str,
        depth: int = 1,
        graph_data: Optional[GraphData] = None
    ) -> List[str]:
        """Get node IDs within N hops of given node."""
        data = graph_data or self.graph_data
        if not data or not self._adjacency:
            return [node_id]

        visited = {node_id}
        frontier = {node_id}

        for _ in range(depth):
            new_frontier = set()
            for nid in frontier:
                neighbors = self._adjacency.get(nid, set())
                for neighbor in neighbors:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        new_frontier.add(neighbor)
            frontier = new_frontier

        return list(visited)

    def focus_on_node(
        self,
        node_id: str,
        depth: int = 2,
        graph_data: Optional[GraphData] = None
    ) -> None:
        """Focus view on a node and its neighborhood."""
        neighborhood = self.get_neighborhood(node_id, depth, graph_data)
        neighborhood_set = set(neighborhood)

        data = graph_data or self.graph_data
        if not data:
            return

        # Hide non-neighborhood nodes
        for node in data.nodes:
            node.hidden = node.id not in neighborhood_set

        # Hide edges not in neighborhood
        for edge in data.edges:
            edge.hidden = (edge.source not in neighborhood_set or
                          edge.target not in neighborhood_set)

        # Highlight the focal node
        self.highlight_nodes([node_id], graph_data=data)

    # =========================================================================
    # Layout Configuration
    # =========================================================================

    def get_layout_options(
        self,
        algorithm: LayoutAlgorithm = LayoutAlgorithm.FORCE_DIRECTED,
        hierarchical: bool = False,
        direction: str = "UD"  # UD, DU, LR, RL
    ) -> Dict[str, Any]:
        """Get vis.js physics/layout options for given algorithm."""

        base_options = {
            "stabilization": {
                "enabled": True,
                "iterations": 100,
                "updateInterval": 25
            },
            "maxVelocity": 50,
            "minVelocity": 0.1,
        }

        if hierarchical:
            return {
                "enabled": True,
                "levelSeparation": 150,
                "nodeSpacing": 100,
                "treeSpacing": 200,
                "direction": direction,
                "sortMethod": "directed",
                **base_options
            }

        if algorithm == LayoutAlgorithm.FORCE_DIRECTED:
            return {
                "enabled": True,
                "solver": "forceAtlas2Based",
                "forceAtlas2Based": {
                    "gravitationalConstant": -50,
                    "centralGravity": 0.01,
                    "springLength": 100,
                    "springConstant": 0.08,
                    "damping": 0.4,
                    "avoidOverlap": 0.5
                },
                **base_options
            }
        elif algorithm == LayoutAlgorithm.BARNESHET:
            return {
                "enabled": True,
                "solver": "barnesHut",
                "barnesHut": {
                    "gravitationalConstant": -2000,
                    "centralGravity": 0.3,
                    "springLength": 95,
                    "springConstant": 0.04,
                    "damping": 0.09
                },
                **base_options
            }
        elif algorithm == LayoutAlgorithm.REPULSION:
            return {
                "enabled": True,
                "solver": "repulsion",
                "repulsion": {
                    "nodeDistance": 100,
                    "centralGravity": 0.2,
                    "springLength": 200,
                    "springConstant": 0.05,
                    "damping": 0.09
                },
                **base_options
            }
        else:
            return {
                "enabled": True,
                "solver": "hierarchicalRepulsion",
                "hierarchicalRepulsion": {
                    "nodeDistance": 120,
                    "centralGravity": 0.0,
                    "springLength": 100,
                    "springConstant": 0.01,
                    "damping": 0.09
                },
                **base_options
            }

    # =========================================================================
    # HTML Generation for Streamlit
    # =========================================================================

    def generate_vis_html(
        self,
        graph_data: Optional[GraphData] = None,
        height: int = 600,
        layout: LayoutAlgorithm = LayoutAlgorithm.FORCE_DIRECTED,
        show_legend: bool = True,
        enable_clustering: bool = False,
        cluster_mode: Optional[ClusterMode] = None
    ) -> str:
        """
        Generate complete HTML for vis.js visualization.

        This can be embedded in Streamlit via st.components.v1.html()
        """
        data = graph_data or self.graph_data
        if not data:
            return "<p>No graph data available</p>"

        # Apply clustering if requested
        if enable_clustering and cluster_mode and cluster_mode != ClusterMode.NONE:
            self.apply_clustering(cluster_mode, data)

        # Get layout options
        physics_options = self.get_layout_options(layout)

        # Serialize graph data
        nodes_json = json.dumps([n.to_vis_dict() for n in data.nodes if not n.hidden])
        edges_json = json.dumps([e.to_vis_dict() for e in data.edges if not e.hidden])
        physics_json = json.dumps(physics_options)

        legend_html = ""
        if show_legend:
            legend_html = """
            <div class="legend">
                <div class="legend-title">Status</div>
                <div class="legend-item">
                    <div class="legend-color" style="background: #2E7D32"></div>
                    <span>Accepted</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: #F57C00"></div>
                    <span>Contested</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: #9E9E9E"></div>
                    <span>Stub</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: #C62828"></div>
                    <span>Rejected</span>
                </div>
                <div class="legend-title" style="margin-top: 10px;">Edges</div>
                <div class="legend-item">
                    <div class="legend-line" style="background: #4CAF50"></div>
                    <span>Positive</span>
                </div>
                <div class="legend-item">
                    <div class="legend-line" style="background: #F44336; border-style: dashed;"></div>
                    <span>Negative</span>
                </div>
            </div>
            """

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
            <style>
                body {{
                    margin: 0;
                    padding: 0;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                }}
                #network {{
                    width: 100%;
                    height: {height}px;
                    border: 1px solid #E0E0E0;
                    border-radius: 8px;
                    background: #FAFAFA;
                }}
                .legend {{
                    position: absolute;
                    top: 10px;
                    right: 10px;
                    background: rgba(255,255,255,0.95);
                    padding: 12px;
                    border-radius: 8px;
                    border: 1px solid #E0E0E0;
                    font-size: 11px;
                    color: #333;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    z-index: 1000;
                }}
                .legend-title {{
                    font-weight: 600;
                    margin-bottom: 6px;
                    color: #666;
                    text-transform: uppercase;
                    font-size: 10px;
                    letter-spacing: 0.5px;
                }}
                .legend-item {{
                    display: flex;
                    align-items: center;
                    margin: 4px 0;
                }}
                .legend-color {{
                    width: 10px;
                    height: 10px;
                    border-radius: 50%;
                    margin-right: 8px;
                }}
                .legend-line {{
                    width: 20px;
                    height: 2px;
                    margin-right: 8px;
                }}
                .controls {{
                    position: absolute;
                    bottom: 10px;
                    left: 10px;
                    display: flex;
                    gap: 8px;
                }}
                .control-btn {{
                    padding: 6px 12px;
                    border: 1px solid #E0E0E0;
                    border-radius: 4px;
                    background: white;
                    cursor: pointer;
                    font-size: 12px;
                }}
                .control-btn:hover {{
                    background: #F5F5F5;
                }}
                .info-panel {{
                    position: absolute;
                    bottom: 10px;
                    right: 10px;
                    background: rgba(255,255,255,0.95);
                    padding: 8px 12px;
                    border-radius: 4px;
                    border: 1px solid #E0E0E0;
                    font-size: 11px;
                    color: #666;
                }}
            </style>
        </head>
        <body>
            <div style="position: relative;">
                <div id="network"></div>
                {legend_html}
                <div class="controls">
                    <button class="control-btn" onclick="network.fit()">Fit</button>
                    <button class="control-btn" onclick="togglePhysics()">Toggle Physics</button>
                    <button class="control-btn" onclick="resetView()">Reset</button>
                </div>
                <div class="info-panel" id="info">
                    Nodes: {data.metrics.node_count} | Edges: {data.metrics.edge_count}
                </div>
            </div>
            <script>
                var nodes = new vis.DataSet({nodes_json});
                var edges = new vis.DataSet({edges_json});

                var container = document.getElementById('network');
                var data = {{ nodes: nodes, edges: edges }};

                var options = {{
                    nodes: {{
                        shape: 'dot',
                        font: {{
                            size: 12,
                            face: 'Georgia',
                            color: '#333'
                        }},
                        borderWidth: 2,
                        borderWidthSelected: 3
                    }},
                    edges: {{
                        font: {{ size: 10 }},
                        scaling: {{
                            min: 1,
                            max: 4
                        }}
                    }},
                    physics: {physics_json},
                    interaction: {{
                        hover: true,
                        tooltipDelay: 100,
                        navigationButtons: true,
                        keyboard: {{
                            enabled: true,
                            bindToWindow: false
                        }},
                        multiselect: true,
                        selectConnectedEdges: true
                    }},
                    groups: {{
                        'ART': {{ color: '#E91E63' }},
                        'SRT': {{ color: '#9C27B0' }},
                        'Biophilia': {{ color: '#4CAF50' }},
                        'Prospect-Refuge': {{ color: '#FF9800' }},
                        'THEORETICAL': {{ color: '#7B1FA2' }},
                        'EMPIRICAL': {{ color: '#1976D2' }},
                        'METHODOLOGICAL': {{ color: '#00838F' }}
                    }}
                }};

                var network = new vis.Network(container, data, options);
                var physicsEnabled = true;

                function togglePhysics() {{
                    physicsEnabled = !physicsEnabled;
                    network.setOptions({{ physics: {{ enabled: physicsEnabled }} }});
                }}

                function resetView() {{
                    network.fit();
                    network.setOptions({{ physics: {{ enabled: true }} }});
                    physicsEnabled = true;
                }}

                network.on('click', function(params) {{
                    if (params.nodes.length > 0) {{
                        var nodeId = params.nodes[0];
                        var node = nodes.get(nodeId);
                        console.log('Selected:', node);
                        // Communicate to Streamlit via query params
                        window.parent.postMessage({{
                            type: 'streamlit:setComponentValue',
                            value: {{ selectedNode: nodeId }}
                        }}, '*');
                    }}
                }});

                network.on('hoverNode', function(params) {{
                    document.body.style.cursor = 'pointer';
                }});

                network.on('blurNode', function(params) {{
                    document.body.style.cursor = 'default';
                }});

                network.on('stabilizationProgress', function(params) {{
                    var progress = Math.round(params.iterations / params.total * 100);
                    document.getElementById('info').innerHTML =
                        'Stabilizing: ' + progress + '%';
                }});

                network.on('stabilizationIterationsDone', function() {{
                    document.getElementById('info').innerHTML =
                        'Nodes: {data.metrics.node_count} | Edges: {data.metrics.edge_count}';
                }});
            </script>
        </body>
        </html>
        """

        return html


# =============================================================================
# Singleton and Convenience Functions
# =============================================================================

_network_service: Optional[NetworkService] = None


def get_network_service() -> NetworkService:
    """Get or create singleton network service."""
    global _network_service
    if _network_service is None:
        _network_service = NetworkService()
    return _network_service


def build_network_visualization(
    beliefs: List[Dict[str, Any]],
    constraints: Optional[List[Dict[str, Any]]] = None,
    layout: LayoutAlgorithm = LayoutAlgorithm.FORCE_DIRECTED,
    cluster_by: Optional[ClusterMode] = None,
    height: int = 600
) -> str:
    """
    Convenience function to build network visualization HTML.

    Args:
        beliefs: List of belief dictionaries
        constraints: List of constraint dictionaries
        layout: Layout algorithm to use
        cluster_by: Optional clustering mode
        height: Height of visualization in pixels

    Returns:
        HTML string for embedding in Streamlit
    """
    service = get_network_service()
    graph_data = service.build_graph_from_beliefs(beliefs, constraints)

    return service.generate_vis_html(
        graph_data=graph_data,
        height=height,
        layout=layout,
        enable_clustering=(cluster_by is not None),
        cluster_mode=cluster_by
    )
