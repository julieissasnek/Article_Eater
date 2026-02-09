"""
Article Eater V23 — Communities Page
Sprint 3.0.3 — 2026-02-08

Browse and explore epistemic communities.
Based on Sprint 2.5 Social Epistemology design.
"""

import streamlit as st
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import PAGE_TITLE, COLORS, credence_to_color
from styles import apply_shared_styles

st.set_page_config(
    page_title=f"{PAGE_TITLE} — Communities",
    page_icon="👥",
    layout="wide"
)


# Community data (would come from API in production)
COMMUNITIES = [
    {
        "id": "art",
        "name": "Attention Restoration Theory (ART)",
        "icon": "🧠",
        "description": "Theory that natural environments restore directed attention capacity through 'soft fascination'",
        "beliefs_count": 156,
        "average_credence": 0.78,
        "key_researchers": ["Rachel Kaplan", "Stephen Kaplan", "Marc Berman"],
        "core_beliefs": [
            "Directed attention can be fatigued through sustained focus",
            "Natural environments provide 'soft fascination' that allows attention to rest",
            "Exposure to nature restores directed attention capacity",
            "ART effects are mediated by involuntary attention engagement"
        ],
        "methodologies": ["Attention testing (ANT, DSB)", "EEG", "Self-report"],
        "key_papers": ["Kaplan & Kaplan 1989", "Berman et al. 2008", "Hartig et al. 2014"],
        "contested_with": ["SRT (mechanism debate)"],
        "year_founded": 1989
    },
    {
        "id": "srt",
        "name": "Stress Recovery Theory (SRT)",
        "icon": "💚",
        "description": "Theory that natural environments trigger rapid physiological stress recovery through evolutionary mechanisms",
        "beliefs_count": 142,
        "average_credence": 0.72,
        "key_researchers": ["Roger Ulrich"],
        "core_beliefs": [
            "Humans have evolved to prefer natural environments",
            "Natural settings trigger parasympathetic activation",
            "Stress recovery in nature is faster than in urban settings",
            "Visual access to nature reduces physiological stress markers"
        ],
        "methodologies": ["Cortisol measurement", "Heart rate variability", "Skin conductance"],
        "key_papers": ["Ulrich 1984", "Ulrich et al. 1991"],
        "contested_with": ["ART (mechanism debate)"],
        "year_founded": 1984
    },
    {
        "id": "biophilia",
        "name": "Biophilia Hypothesis",
        "icon": "🌿",
        "description": "Theory that humans have an innate, genetically-based tendency to affiliate with living systems",
        "beliefs_count": 234,
        "average_credence": 0.68,
        "key_researchers": ["E.O. Wilson", "Stephen Kellert"],
        "core_beliefs": [
            "Humans have evolved biophilic tendencies",
            "Connection to nature is essential for human wellbeing",
            "Biophilic elements in design improve health outcomes",
            "Nature deficit disorder affects modern populations"
        ],
        "methodologies": ["Survey instruments", "Preference studies", "Health outcomes"],
        "key_papers": ["Wilson 1984", "Kellert & Wilson 1993"],
        "contested_with": [],
        "year_founded": 1984
    },
    {
        "id": "env_psych",
        "name": "Environmental Psychology",
        "icon": "🏗️",
        "description": "Study of transactions between individuals and their physical settings",
        "beliefs_count": 312,
        "average_credence": 0.65,
        "key_researchers": ["Daniel Stokols", "Irwin Altman", "Robert Gifford"],
        "core_beliefs": [
            "Physical environments affect human behavior and wellbeing",
            "Person-environment fit influences outcomes",
            "Environmental stress has measurable health effects",
            "Design interventions can improve psychological outcomes"
        ],
        "methodologies": ["Field studies", "Survey instruments", "Behavioral observation"],
        "key_papers": ["Stokols 1978", "Gifford 2007"],
        "contested_with": [],
        "year_founded": 1960
    }
]


def render_community_overview():
    """Render overview of all communities."""
    st.markdown("## Community Overview")

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)

    total_beliefs = sum(c["beliefs_count"] for c in COMMUNITIES)
    avg_credence = sum(c["average_credence"] * c["beliefs_count"] for c in COMMUNITIES) / total_beliefs

    with col1:
        st.metric("Communities", len(COMMUNITIES))
    with col2:
        st.metric("Total Beliefs", f"{total_beliefs:,}")
    with col3:
        st.metric("Avg Credence", f"{avg_credence:.2f}")
    with col4:
        contested = sum(1 for c in COMMUNITIES if c["contested_with"])
        st.metric("Contested", contested)


def render_community_cards():
    """Render community selection cards."""
    st.markdown("## Communities")

    cols = st.columns(2)

    for idx, community in enumerate(COMMUNITIES):
        with cols[idx % 2]:
            with st.container():
                # Header
                st.markdown(f"### {community['icon']} {community['name']}")
                st.caption(f"Est. {community['year_founded']}")

                # Description
                st.markdown(community['description'])

                # Metrics
                mcol1, mcol2 = st.columns(2)
                with mcol1:
                    st.metric("Beliefs", community['beliefs_count'])
                with mcol2:
                    credence_color = credence_to_color(community['average_credence'])
                    st.metric("Avg Credence", f"{community['average_credence']:.2f}")

                # Key researchers
                st.markdown(f"**Key Researchers**: {', '.join(community['key_researchers'])}")

                # Contestation warning
                if community['contested_with']:
                    st.warning(f"⚡ Contested with: {', '.join(community['contested_with'])}")

                # View details button
                if st.button(f"View Details", key=f"view_{community['id']}"):
                    st.session_state.selected_community = community['id']
                    st.rerun()

                st.markdown("---")


def render_community_detail(community_id: str):
    """Render detailed view of a community."""
    community = next((c for c in COMMUNITIES if c['id'] == community_id), None)

    if not community:
        st.error(f"Community not found: {community_id}")
        return

    # Back button
    if st.button("← Back to all communities"):
        st.session_state.selected_community = None
        st.rerun()

    # Header
    st.markdown(f"# {community['icon']} {community['name']}")
    st.caption(f"Established {community['year_founded']}")
    st.markdown(community['description'])

    st.markdown("---")

    # Tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "💭 Core Beliefs", "📄 Key Papers", "🔬 Methodology"])

    with tab1:
        # Metrics
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Beliefs", community['beliefs_count'])
        with col2:
            st.metric("Average Credence", f"{community['average_credence']:.2f}")
        with col3:
            st.metric("Key Papers", len(community['key_papers']))

        # Researchers
        st.markdown("### Key Researchers")
        for researcher in community['key_researchers']:
            st.markdown(f"- 👤 **{researcher}**")

        # Contestation
        if community['contested_with']:
            st.markdown("### Contested Areas")
            for contested in community['contested_with']:
                st.warning(f"⚡ {contested}")

    with tab2:
        st.markdown("### Core Beliefs")

        for i, belief in enumerate(community['core_beliefs'], 1):
            with st.expander(f"Belief {i}: {belief[:50]}..."):
                st.markdown(f"**{belief}**")
                st.caption("Status: ACCEPTED | Level: THEORETICAL")
                st.progress(community['average_credence'])
                st.caption(f"Credence: {community['average_credence']:.2f}")

    with tab3:
        st.markdown("### Key Papers")

        for paper in community['key_papers']:
            st.markdown(f"📄 **{paper}**")

        st.markdown("---")
        st.button("📚 Export BibTeX for this community")

    with tab4:
        st.markdown("### Methodologies Used")

        for method in community['methodologies']:
            st.markdown(f"- 🔬 {method}")

        st.markdown("---")
        st.markdown("### Methodological Diversity")
        st.info(f"This community uses {len(community['methodologies'])} distinct methodological approaches.")


def render_community_comparison():
    """Render comparison view between communities."""
    st.markdown("## Compare Communities")

    col1, col2 = st.columns(2)

    with col1:
        comm1 = st.selectbox(
            "First Community",
            [c['name'] for c in COMMUNITIES],
            index=0
        )

    with col2:
        comm2 = st.selectbox(
            "Second Community",
            [c['name'] for c in COMMUNITIES],
            index=1
        )

    # Get community data
    c1 = next((c for c in COMMUNITIES if c['name'] == comm1), None)
    c2 = next((c for c in COMMUNITIES if c['name'] == comm2), None)

    if c1 and c2:
        st.markdown("---")

        # Comparison table
        col1, col2, col3 = st.columns([2, 1, 2])

        with col1:
            st.markdown(f"### {c1['icon']} {c1['name']}")
            st.metric("Beliefs", c1['beliefs_count'])
            st.metric("Credence", f"{c1['average_credence']:.2f}")
            st.markdown(f"**Founded**: {c1['year_founded']}")

        with col2:
            st.markdown("### vs")

        with col3:
            st.markdown(f"### {c2['icon']} {c2['name']}")
            st.metric("Beliefs", c2['beliefs_count'])
            st.metric("Credence", f"{c2['average_credence']:.2f}")
            st.markdown(f"**Founded**: {c2['year_founded']}")

        # Overlap analysis
        st.markdown("---")
        st.markdown("### Overlap Analysis")

        # Check if contested
        if c2['name'].split('(')[0].strip() in str(c1['contested_with']):
            st.warning(f"⚡ These communities have contested views")
        else:
            st.success("✓ No direct contestation between these communities")


def init_session_state():
    """Initialize session state."""
    if "selected_community" not in st.session_state:
        st.session_state.selected_community = None


def main():
    """Main communities page."""
    apply_shared_styles()
    init_session_state()

    st.title("Epistemic Communities")
    st.caption("Browse and explore research communities in environmental psychology")

    # Navigation tabs
    if st.session_state.selected_community:
        render_community_detail(st.session_state.selected_community)
    else:
        tab1, tab2 = st.tabs(["📋 Browse", "⚖️ Compare"])

        with tab1:
            render_community_overview()
            st.markdown("---")
            render_community_cards()

        with tab2:
            render_community_comparison()


if __name__ == "__main__":
    main()
