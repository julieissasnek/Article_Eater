"""
Network Visualization Component — Sprint 3.0.3-C
2026-02-09

Streamlit component wrapping NetworkService for claim network visualization.
Implements Shneiderman's Visual Information Seeking Mantra:
"Overview first, zoom and filter, then details on demand"

Usage:
    from components.network import render_claim_network

    render_claim_network(
        beliefs=beliefs_list,
        constraints=constraints_list,
        height=600,
        cluster_by="theory"
    )
"""

import streamlit as st
import streamlit.components.v1 as components
from typing import List, Dict, Any, Optional
import sys
from pathlib import Path

# Add parent paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.services.network_service import (
    NetworkService,
    get_network_service,
    build_network_visualization,
    LayoutAlgorithm,
    ClusterMode,
    GraphData,
    GraphMetrics
)


def render_claim_network(
    beliefs: List[Dict[str, Any]],
    constraints: Optional[List[Dict[str, Any]]] = None,
    height: int = 600,
    layout: str = "force",
    cluster_by: Optional[str] = None,
    min_credence: float = 0.0,
    max_nodes: int = 150,
    show_legend: bool = True,
    key: str = "network"
) -> Optional[str]:
    """
    Render an interactive claim network visualization.

    Args:
        beliefs: List of belief dictionaries with id, content, credence, status, level
        constraints: Optional list of constraint dictionaries with source_id, target_id, polarity
        height: Height of the visualization in pixels
        layout: Layout algorithm ("force", "hierarchical", "barnes", "repulsion")
        cluster_by: Optional clustering ("theory", "level", "status", "community")
        min_credence: Minimum credence threshold for display
        max_nodes: Maximum nodes to display
        show_legend: Whether to show the legend
        key: Unique key for Streamlit component

    Returns:
        Selected node ID if a node was clicked, None otherwise
    """
    if not beliefs:
        st.info("No beliefs to visualize. Add beliefs or adjust filters.")
        return None

    # Map layout string to enum
    layout_map = {
        "force": LayoutAlgorithm.FORCE_DIRECTED,
        "hierarchical": LayoutAlgorithm.HIERARCHICAL,
        "barnes": LayoutAlgorithm.BARNESHET,
        "repulsion": LayoutAlgorithm.REPULSION
    }
    layout_algo = layout_map.get(layout, LayoutAlgorithm.FORCE_DIRECTED)

    # Map cluster string to enum
    cluster_map = {
        "theory": ClusterMode.THEORY,
        "level": ClusterMode.LEVEL,
        "status": ClusterMode.STATUS,
        "community": ClusterMode.COMMUNITY,
        None: ClusterMode.NONE,
        "none": ClusterMode.NONE
    }
    cluster_mode = cluster_map.get(cluster_by, ClusterMode.NONE)

    # Get network service
    service = get_network_service()

    # Build graph data
    graph_data = service.build_graph_from_beliefs(
        beliefs=beliefs,
        constraints=constraints,
        max_nodes=max_nodes,
        min_credence=min_credence
    )

    # Apply clustering if requested
    if cluster_mode != ClusterMode.NONE:
        service.apply_clustering(cluster_mode, graph_data)

    # Generate HTML
    html = service.generate_vis_html(
        graph_data=graph_data,
        height=height,
        layout=layout_algo,
        show_legend=show_legend,
        enable_clustering=(cluster_mode != ClusterMode.NONE),
        cluster_mode=cluster_mode
    )

    # Render via Streamlit component
    components.html(html, height=height + 50, key=key)

    # Return metrics for display
    return graph_data.metrics


def render_network_controls() -> Dict[str, Any]:
    """
    Render network control widgets in sidebar.

    Returns:
        Dictionary of control values.
    """
    st.sidebar.markdown("### Network Controls")

    layout = st.sidebar.selectbox(
        "Layout Algorithm",
        ["force", "barnes", "repulsion", "hierarchical"],
        format_func=lambda x: {
            "force": "Force-Directed (default)",
            "barnes": "Barnes-Hut",
            "repulsion": "Repulsion",
            "hierarchical": "Hierarchical"
        }.get(x, x)
    )

    cluster_by = st.sidebar.selectbox(
        "Cluster By",
        [None, "theory", "level", "status", "community"],
        format_func=lambda x: {
            None: "No Clustering",
            "theory": "Theory",
            "level": "Epistemic Level",
            "status": "Belief Status",
            "community": "Community"
        }.get(x, x)
    )

    max_nodes = st.sidebar.slider(
        "Max Nodes",
        min_value=20,
        max_value=300,
        value=150,
        step=10,
        help="Maximum number of nodes to display (highest credence first)"
    )

    show_legend = st.sidebar.checkbox("Show Legend", value=True)

    return {
        "layout": layout,
        "cluster_by": cluster_by,
        "max_nodes": max_nodes,
        "show_legend": show_legend
    }


def render_network_metrics(metrics: GraphMetrics):
    """
    Render graph metrics as Streamlit metrics.

    Args:
        metrics: GraphMetrics from NetworkService
    """
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Nodes", metrics.node_count)

    with col2:
        st.metric("Edges", metrics.edge_count)

    with col3:
        st.metric("Density", f"{metrics.density:.3f}")

    with col4:
        st.metric("Avg Degree", f"{metrics.average_degree:.1f}")

    # Status breakdown
    st.markdown("**Status Distribution**")
    status_col1, status_col2, status_col3, status_col4 = st.columns(4)

    with status_col1:
        st.metric("Accepted", metrics.accepted_count, help="Green nodes")

    with status_col2:
        st.metric("Contested", metrics.contested_count, help="Orange nodes")

    with status_col3:
        st.metric("Stub", metrics.stub_count, help="Gray nodes")

    with status_col4:
        st.metric("Rejected", metrics.rejected_count, help="Red nodes")


def render_node_focus_view(
    node_id: str,
    beliefs: List[Dict[str, Any]],
    constraints: Optional[List[Dict[str, Any]]] = None,
    depth: int = 2,
    height: int = 400
):
    """
    Render a focused view centered on a specific node and its neighborhood.

    Args:
        node_id: The belief ID to focus on
        beliefs: Full list of beliefs
        constraints: Full list of constraints
        depth: Neighborhood depth (hops from focal node)
        height: Visualization height
    """
    service = get_network_service()

    # Build full graph
    graph_data = service.build_graph_from_beliefs(
        beliefs=beliefs,
        constraints=constraints
    )

    # Focus on the node
    service.focus_on_node(node_id, depth=depth, graph_data=graph_data)

    # Generate HTML
    html = service.generate_vis_html(
        graph_data=graph_data,
        height=height,
        layout=LayoutAlgorithm.FORCE_DIRECTED,
        show_legend=False
    )

    st.markdown(f"### Neighborhood of `{node_id}`")
    st.caption(f"Showing nodes within {depth} hops")

    components.html(html, height=height + 20, key=f"focus_{node_id}")


def render_network_search(
    beliefs: List[Dict[str, Any]],
    constraints: Optional[List[Dict[str, Any]]] = None,
    height: int = 500
):
    """
    Render network with search/highlight functionality.

    Args:
        beliefs: List of beliefs
        constraints: List of constraints
        height: Visualization height
    """
    search_term = st.text_input(
        "Search beliefs",
        placeholder="Enter term to highlight matching nodes...",
        key="network_search"
    )

    service = get_network_service()

    # Build graph
    graph_data = service.build_graph_from_beliefs(
        beliefs=beliefs,
        constraints=constraints
    )

    # Apply search filter if term provided
    if search_term:
        visible_count = service.filter_nodes(
            search=search_term,
            graph_data=graph_data
        )
        st.caption(f"Found {visible_count} matching nodes")

    # Generate HTML
    html = service.generate_vis_html(
        graph_data=graph_data,
        height=height,
        layout=LayoutAlgorithm.FORCE_DIRECTED
    )

    components.html(html, height=height + 20, key="search_network")


def get_beliefs_from_web() -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Get beliefs and constraints from WebOfBelief.

    Returns:
        Tuple of (beliefs list, constraints list)
    """
    try:
        from src.services.web_of_belief import get_web
        web = get_web()

        beliefs = []
        for belief_id, belief in web.beliefs.items():
            beliefs.append({
                "id": belief_id,
                "content": belief.content,
                "credence": belief.credence.point if hasattr(belief.credence, 'point') else belief.credence,
                "status": belief.status.value if hasattr(belief.status, 'value') else str(belief.status),
                "level": belief.level.value if hasattr(belief.level, 'value') else str(belief.level),
                "theory": belief.theory_ids[0] if belief.theory_ids else None,
                "entrenchment": web.get_entrenchment(belief_id)
            })

        constraints = []
        for i, constraint in enumerate(web.constraints):
            constraints.append({
                "id": f"c{i}",
                "source_id": constraint.source_id,
                "target_id": constraint.target_id,
                "polarity": constraint.polarity.value if hasattr(constraint.polarity, 'value') else str(constraint.polarity),
                "weight": constraint.weight,
                "reason": constraint.reason
            })

        return beliefs, constraints

    except Exception as e:
        st.warning(f"Could not load from WebOfBelief: {e}")
        return [], []


# Convenience function for quick embedding
def quick_network(height: int = 600, key: str = "quick_net"):
    """
    Quick network visualization using current WebOfBelief state.

    Args:
        height: Visualization height
        key: Component key
    """
    beliefs, constraints = get_beliefs_from_web()

    if beliefs:
        metrics = render_claim_network(
            beliefs=beliefs,
            constraints=constraints,
            height=height,
            key=key
        )
        if metrics:
            with st.expander("Network Metrics"):
                render_network_metrics(metrics)
    else:
        st.info("No beliefs in the web. Process some papers first!")
