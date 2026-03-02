"""
Article Eater V23 — Explore Page
Sprint 3.0.3-C — 2026-02-09

Visual exploration of the belief network.
Implements Shneiderman's Visual Information Seeking Mantra:
"Overview first, zoom and filter, then details on demand"

Uses NetworkService for full vis.js integration with:
- Force-directed / hierarchical layouts
- Clustering by theory / level / status / community
- Interactive filtering and node selection
Integrated with TheoryGuideService for belief theory context.
"""

import streamlit as st
import json
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import theory guide service
try:
    from src.services.theory_guide_service import TheoryGuideService
    THEORY_SERVICE = TheoryGuideService()
    HAS_THEORY_SERVICE = True
except Exception as e:
    print(f"Warning: Could not load TheoryGuideService: {e}")
    HAS_THEORY_SERVICE = False

from config import (
    PAGE_TITLE, COLORS, BELIEF_STATUS, EPISTEMIC_LEVELS,
    credence_to_color, credence_to_label
)
from api_client import get_client, BeliefSummary
from styles import apply_shared_styles

# Import network components
from components.network import (
    render_claim_network,
    render_network_controls,
    render_network_metrics,
    render_node_focus_view,
    get_beliefs_from_web
)

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


def convert_beliefs_to_dicts(beliefs: List[BeliefSummary]) -> List[Dict[str, Any]]:
    """Convert BeliefSummary objects to dictionaries for NetworkService."""
    return [
        {
            "id": belief.id,
            "content": belief.content,
            "credence": belief.credence,
            "status": belief.status,
            "level": belief.level,
            "theory": belief.theory
        }
        for belief in beliefs
    ]


def get_constraints_from_api(belief_ids: List[str]) -> List[Dict[str, Any]]:
    """Get constraints from API for the given belief IDs."""
    client = get_client()
    all_constraints = []

    # Get constraints for each belief
    # Note: In production, we'd have a bulk endpoint for this
    belief_id_set = set(belief_ids)

    for belief_id in belief_ids[:20]:  # Limit API calls
        try:
            constraints = client.get_belief_constraints(belief_id)
            for c in constraints:
                # Only include constraints where both endpoints are visible
                target = c.get("target_id", "")
                if target in belief_id_set:
                    all_constraints.append({
                        "source_id": belief_id,
                        "target_id": target,
                        "polarity": c.get("polarity", "NEUTRAL"),
                        "weight": c.get("weight", 0.5),
                        "reason": c.get("reason", "")
                    })
        except Exception:
            pass  # Skip on error

    return all_constraints


def render_network_visualization(beliefs: List[BeliefSummary], options: Dict):
    """Render the network visualization using NetworkService component."""
    st.markdown("## Network Visualization")

    if not beliefs:
        st.warning("No beliefs match the current filters.")
        return

    # Convert to dictionaries for NetworkService
    belief_dicts = convert_beliefs_to_dicts(beliefs)
    belief_ids = [b.id for b in beliefs]

    # Get constraints from API or WebOfBelief
    constraints = get_constraints_from_api(belief_ids)

    # Also try to get from WebOfBelief directly if available
    if not constraints:
        try:
            _, web_constraints = get_beliefs_from_web()
            # Filter to relevant constraints
            belief_id_set = set(belief_ids)
            constraints = [
                c for c in web_constraints
                if c.get("source_id") in belief_id_set and c.get("target_id") in belief_id_set
            ]
        except Exception:
            pass

    # Map cluster_by option
    cluster_map = {
        "None": None,
        "Theory": "theory",
        "Level": "level",
        "Community": "community"
    }
    cluster_by = cluster_map.get(options.get("cluster_by", "None"))

    # Render using component
    metrics = render_claim_network(
        beliefs=belief_dicts,
        constraints=constraints,
        height=550,
        layout="force",
        cluster_by=cluster_by,
        show_legend=True,
        key="main_network"
    )

    # Show metrics in expander
    if metrics:
        with st.expander("Graph Metrics", expanded=False):
            render_network_metrics(metrics)


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
    """Render details panel for selected node with theory context."""
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

    # Theory context from metadata
    if HAS_THEORY_SERVICE and belief.get("theory"):
        with st.expander("📚 Theory Context", expanded=False):
            try:
                theory_name = belief.get("theory")
                guide = THEORY_SERVICE.get_guide(theory_name, detail_level="quick")
                if guide:
                    st.markdown(f"**Theory**: {guide.display_name}")
                    st.markdown(guide.content[:250] + "...")

                    if guide.constructs:
                        st.markdown(f"**Key Constructs**: {', '.join(guide.constructs[:3])}")

                    if guide.atlas_status:
                        st.markdown(f"**ATLAS Status**: `{guide.atlas_status}`")
            except Exception:
                pass

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
