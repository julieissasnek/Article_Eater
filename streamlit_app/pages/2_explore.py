"""
Article Eater V23 — Explore Page
Sprint 3.0.3 — 2026-02-08

Visual exploration of the belief network.
Implements Shneiderman's Visual Information Seeking Mantra:
"Overview first, zoom and filter, then details on demand"
"""

import streamlit as st
import json
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import (
    PAGE_TITLE, COLORS, BELIEF_STATUS, EPISTEMIC_LEVELS,
    credence_to_color, credence_to_label
)
from api_client import get_client, BeliefSummary
from styles import apply_shared_styles

st.set_page_config(
    page_title=f"{PAGE_TITLE} — Explore",
    page_icon="🗺️",
    layout="wide"
)


def init_session_state():
    """Initialize session state for explore page."""
    if "selected_node" not in st.session_state:
        st.session_state.selected_node = None
    if "filter_status" not in st.session_state:
        st.session_state.filter_status = ["ACCEPTED", "CONTESTED"]
    if "filter_level" not in st.session_state:
        st.session_state.filter_level = list(EPISTEMIC_LEVELS.keys())
    if "min_credence" not in st.session_state:
        st.session_state.min_credence = 0.0
    if "selected_theory" not in st.session_state:
        st.session_state.selected_theory = "All"


def render_sidebar_filters():
    """Render filter controls in sidebar."""
    st.sidebar.markdown("### Filters")

    # Status filter
    st.session_state.filter_status = st.sidebar.multiselect(
        "Belief Status",
        ["ACCEPTED", "CONTESTED", "STUB", "REJECTED"],
        default=st.session_state.filter_status
    )

    # Level filter
    st.session_state.filter_level = st.sidebar.multiselect(
        "Epistemic Level",
        list(EPISTEMIC_LEVELS.keys()),
        default=st.session_state.filter_level
    )

    # Credence filter
    st.session_state.min_credence = st.sidebar.slider(
        "Minimum Credence",
        0.0, 1.0, st.session_state.min_credence, 0.05
    )

    # Theory filter
    st.session_state.selected_theory = st.sidebar.selectbox(
        "Theory",
        ["All", "ART", "SRT", "Biophilia", "Environmental Psychology"]
    )

    st.sidebar.markdown("---")

    # View options
    st.sidebar.markdown("### View Options")
    show_constraints = st.sidebar.checkbox("Show constraints", value=True)
    show_labels = st.sidebar.checkbox("Show labels", value=True)
    cluster_by = st.sidebar.selectbox(
        "Cluster by",
        ["None", "Theory", "Level", "Community"]
    )

    return {
        "show_constraints": show_constraints,
        "show_labels": show_labels,
        "cluster_by": cluster_by
    }


def generate_graph_data(beliefs: List[BeliefSummary]) -> Dict[str, Any]:
    """Generate vis.js compatible graph data."""
    nodes = []
    edges = []

    for belief in beliefs:
        # Determine node color based on status
        status_info = BELIEF_STATUS.get(belief.status, {"color": "#ADB5BD"})

        # Determine node size based on credence
        size = 10 + (belief.credence * 30)

        nodes.append({
            "id": belief.id,
            "label": belief.content[:40] + "..." if len(belief.content) > 40 else belief.content,
            "title": f"{belief.content}\n\nCredence: {belief.credence:.2f}\nStatus: {belief.status}\nLevel: {belief.level}",
            "color": status_info["color"],
            "size": size,
            "level": belief.level,
            "credence": belief.credence,
            "status": belief.status,
            "theory": belief.theory
        })

    # Generate sample edges (would come from actual constraint data)
    # For demo, create some connections between beliefs
    if len(nodes) >= 2:
        edges.append({
            "from": nodes[0]["id"],
            "to": nodes[1]["id"],
            "color": COLORS["success"],
            "width": 2,
            "title": "Positive constraint (0.82)"
        })
    if len(nodes) >= 3:
        edges.append({
            "from": nodes[0]["id"],
            "to": nodes[2]["id"],
            "color": COLORS["success"],
            "width": 1.5,
            "title": "Positive constraint (0.65)"
        })
    if len(nodes) >= 4:
        edges.append({
            "from": nodes[2]["id"],
            "to": nodes[3]["id"],
            "color": COLORS["danger"],
            "width": 2,
            "title": "Negative constraint (0.78)"
        })

    return {"nodes": nodes, "edges": edges}


def render_network_visualization(beliefs: List[BeliefSummary], options: Dict):
    """Render the network visualization using vis.js via HTML component."""
    st.markdown("## Network Visualization")

    if not beliefs:
        st.warning("No beliefs match the current filters.")
        return

    graph_data = generate_graph_data(beliefs)

    # Create vis.js visualization as HTML
    vis_html = f"""
    <html>
    <head>
        <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
        <style>
            #network {{
                width: 100%;
                height: 500px;
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                background: {COLORS['background']};
            }}
            .legend {{
                position: absolute;
                top: 10px;
                right: 10px;
                background: {COLORS['card_bg']};
                padding: 10px;
                border-radius: 8px;
                border: 1px solid {COLORS['border']};
                font-size: 12px;
                color: {COLORS['text']};
            }}
            .legend-item {{
                display: flex;
                align-items: center;
                margin: 5px 0;
            }}
            .legend-color {{
                width: 12px;
                height: 12px;
                border-radius: 50%;
                margin-right: 8px;
            }}
        </style>
    </head>
    <body>
        <div id="network"></div>
        <div class="legend">
            <div class="legend-item">
                <div class="legend-color" style="background: {BELIEF_STATUS['ACCEPTED']['color']}"></div>
                <span>Accepted</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: {BELIEF_STATUS['CONTESTED']['color']}"></div>
                <span>Contested</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: {BELIEF_STATUS['STUB']['color']}"></div>
                <span>Stub</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: {BELIEF_STATUS['REJECTED']['color']}"></div>
                <span>Rejected</span>
            </div>
        </div>
        <script>
            var nodes = new vis.DataSet({json.dumps(graph_data['nodes'])});
            var edges = new vis.DataSet({json.dumps(graph_data['edges'])});

            var container = document.getElementById('network');
            var data = {{ nodes: nodes, edges: edges }};
            var options = {{
                nodes: {{
                    shape: 'dot',
                    font: {{
                        size: {'14' if options['show_labels'] else '0'},
                        face: 'Georgia'
                    }},
                    borderWidth: 2
                }},
                edges: {{
                    arrows: {{ to: {{ enabled: true, scaleFactor: 0.5 }} }},
                    smooth: {{ type: 'curvedCW', roundness: 0.2 }}
                }},
                physics: {{
                    enabled: true,
                    solver: 'forceAtlas2Based',
                    forceAtlas2Based: {{
                        gravitationalConstant: -50,
                        centralGravity: 0.01,
                        springLength: 100,
                        springConstant: 0.08
                    }},
                    stabilization: {{
                        iterations: 100
                    }}
                }},
                interaction: {{
                    hover: true,
                    tooltipDelay: 100,
                    navigationButtons: true,
                    keyboard: true
                }}
            }};

            var network = new vis.Network(container, data, options);

            network.on('click', function(params) {{
                if (params.nodes.length > 0) {{
                    var nodeId = params.nodes[0];
                    // Would communicate back to Streamlit
                    console.log('Selected node:', nodeId);
                }}
            }});
        </script>
    </body>
    </html>
    """

    st.components.v1.html(vis_html, height=550)

    # Node count info
    st.caption(f"Showing {len(graph_data['nodes'])} beliefs, {len(graph_data['edges'])} constraints")


def render_overview_stats(beliefs: List[BeliefSummary]):
    """Render overview statistics panel."""
    st.markdown("### Overview")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Visible Beliefs", len(beliefs))

    with col2:
        if beliefs:
            avg_credence = sum(b.credence for b in beliefs) / len(beliefs)
            st.metric("Avg Credence", f"{avg_credence:.2f}")
        else:
            st.metric("Avg Credence", "—")

    with col3:
        accepted = sum(1 for b in beliefs if b.status == "ACCEPTED")
        st.metric("Accepted", accepted)

    with col4:
        contested = sum(1 for b in beliefs if b.status == "CONTESTED")
        st.metric("Contested", contested)


def render_belief_list(beliefs: List[BeliefSummary]):
    """Render filterable belief list."""
    st.markdown("### Beliefs")

    # Search within results
    search = st.text_input("🔍 Filter beliefs", placeholder="Type to filter...")

    filtered = beliefs
    if search:
        filtered = [b for b in beliefs if search.lower() in b.content.lower()]

    # Display as table
    for belief in filtered[:20]:  # Limit display
        status_info = BELIEF_STATUS.get(belief.status, {"icon": "?", "color": "#ADB5BD"})

        col1, col2, col3 = st.columns([3, 1, 1])

        with col1:
            st.markdown(f"**{status_info['icon']}** {belief.content[:80]}...")

        with col2:
            st.markdown(f"Credence: **{belief.credence:.2f}**")

        with col3:
            if st.button("Details", key=f"detail_{belief.id}"):
                st.session_state.selected_node = belief.id

    if len(filtered) > 20:
        st.caption(f"Showing 20 of {len(filtered)} beliefs")


def render_node_details(belief_id: str):
    """Render details panel for selected node."""
    st.markdown("### Selected Belief")

    client = get_client()
    belief = client.get_belief(belief_id)

    if not belief:
        st.warning("Could not load belief details")
        return

    # Belief content
    st.markdown(f"**{belief.get('content', 'Unknown')}**")

    # Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Credence", f"{belief.get('credence', 0):.2f}")
    with col2:
        st.metric("Status", belief.get("status", "Unknown"))
    with col3:
        st.metric("Level", belief.get("level", "Unknown"))

    # Constraints
    st.markdown("#### Constraints")
    constraints = client.get_belief_constraints(belief_id)
    if constraints:
        for c in constraints[:5]:
            polarity = "🟢" if c.get("polarity") == "POSITIVE" else "🔴"
            st.markdown(f"{polarity} {c.get('target_id', '?')}: {c.get('reason', '')}")
    else:
        st.caption("No constraints found")

    # Evidence
    st.markdown("#### Evidence")
    evidence = client.get_belief_evidence(belief_id)
    if evidence:
        for ev in evidence[:5]:
            st.markdown(f"📄 {ev.get('source', 'Unknown source')}")
    else:
        st.caption("No evidence linked")

    # Actions
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Clear Selection"):
            st.session_state.selected_node = None
            st.rerun()
    with col2:
        st.button("Export This Belief")


def render_community_view(beliefs: List[BeliefSummary]):
    """Render community-clustered view."""
    st.markdown("### By Community")

    # Group beliefs by theory
    by_theory = {}
    for belief in beliefs:
        theory = belief.theory or "Unassigned"
        if theory not in by_theory:
            by_theory[theory] = []
        by_theory[theory].append(belief)

    # Display communities
    for theory, theory_beliefs in sorted(by_theory.items()):
        with st.expander(f"👥 {theory} ({len(theory_beliefs)} beliefs)"):
            for belief in theory_beliefs[:10]:
                status_info = BELIEF_STATUS.get(belief.status, {"icon": "?"})
                st.markdown(f"{status_info['icon']} {belief.content[:60]}... ({belief.credence:.2f})")

            if len(theory_beliefs) > 10:
                st.caption(f"+{len(theory_beliefs) - 10} more")


def main():
    """Main explore page."""
    apply_shared_styles()
    init_session_state()

    st.title("Explore the Evidence Network")
    st.caption("Visual exploration following Shneiderman's mantra: Overview first, zoom and filter, then details on demand")

    # Sidebar filters
    options = render_sidebar_filters()

    # Get filtered beliefs
    client = get_client()
    beliefs = client.get_beliefs(
        limit=100,
        status=st.session_state.filter_status,
        level=st.session_state.filter_level,
        min_credence=st.session_state.min_credence
    )

    # Apply theory filter
    if st.session_state.selected_theory != "All":
        beliefs = [b for b in beliefs if b.theory == st.session_state.selected_theory]

    # Main content tabs
    tab1, tab2, tab3 = st.tabs(["🕸️ Network", "📋 List", "👥 Communities"])

    with tab1:
        render_overview_stats(beliefs)
        st.markdown("---")
        render_network_visualization(beliefs, options)

        # Details panel if node selected
        if st.session_state.selected_node:
            st.markdown("---")
            render_node_details(st.session_state.selected_node)

    with tab2:
        render_overview_stats(beliefs)
        st.markdown("---")
        render_belief_list(beliefs)

    with tab3:
        render_overview_stats(beliefs)
        st.markdown("---")
        render_community_view(beliefs)


if __name__ == "__main__":
    main()
