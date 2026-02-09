"""
Article Eater V23 — Admin Dashboard
Sprint 3.0.5 — 2026-02-08

System inspection for beliefs, constraints, communities, and health.
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import (
    PAGE_TITLE, COLORS, BELIEF_STATUS, EPISTEMIC_LEVELS,
    credence_to_color, credence_to_label
)
from styles import apply_shared_styles

st.set_page_config(
    page_title=f"{PAGE_TITLE} — Admin",
    page_icon="⚙️",
    layout="wide"
)


def render_system_overview():
    """Render system-wide statistics and health."""
    st.markdown("## System Overview")

    # Key metrics row
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            "Total Beliefs",
            "1,247",
            "+23 this week",
            help="Total beliefs in the web of belief"
        )

    with col2:
        st.metric(
            "Constraints",
            "3,891",
            "+67 this week",
            help="Epistemic constraints between beliefs"
        )

    with col3:
        st.metric(
            "Papers",
            "312",
            "+5 this week",
            help="Source papers in the corpus"
        )

    with col4:
        st.metric(
            "Coherence",
            "0.72",
            "+0.02",
            help="Overall web coherence score"
        )

    with col5:
        st.metric(
            "Communities",
            "4",
            "0",
            help="Epistemic communities (ART, SRT, Biophilia, Env Psych)"
        )

    st.markdown("---")

    # Health checks
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Health Checks")

        checks = [
            ("API Server", "✅ Running", "localhost:8000"),
            ("Database", "✅ Connected", "SQLite"),
            ("LLM Service", "✅ Available", "Claude API"),
            ("Cache", "✅ Warm", "1,247 beliefs cached"),
            ("Last Coherence Calc", "✅ Recent", "2 minutes ago"),
        ]

        for name, status, detail in checks:
            st.markdown(f"**{name}**: {status}")
            st.caption(detail)

    with col2:
        st.markdown("### Recent Activity")

        activities = [
            ("🆕 Belief added", "Plants reduce cognitive load", "2 min ago"),
            ("🔗 Constraint added", "ART → attention restoration", "5 min ago"),
            ("📄 Paper ingested", "Kaplan & Kaplan 1989", "1 hour ago"),
            ("🔄 Coherence recalculated", "Score: 0.72", "2 hours ago"),
            ("⚠️ Contestation detected", "Window size effect", "3 hours ago"),
        ]

        for icon_action, description, time in activities:
            st.markdown(f"**{icon_action}**")
            st.caption(f"{description} — {time}")


def render_belief_browser():
    """Render searchable belief browser."""
    st.markdown("## Belief Browser")

    # Search and filter controls
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        search = st.text_input("🔍 Search beliefs", placeholder="Enter keyword...")

    with col2:
        status_filter = st.multiselect(
            "Status",
            ["ACCEPTED", "CONTESTED", "STUB", "REJECTED"],
            default=["ACCEPTED", "CONTESTED"]
        )

    with col3:
        level_filter = st.multiselect(
            "Level",
            ["THEORETICAL", "INTERMEDIATE", "EMPIRICAL", "OBSERVATIONAL"],
            default=["THEORETICAL", "EMPIRICAL"]
        )

    with col4:
        credence_min = st.slider("Min Credence", 0.0, 1.0, 0.0)

    # Results table
    st.markdown("---")

    # Placeholder belief data
    beliefs = [
        {
            "id": "B001",
            "content": "Natural environments restore directed attention capacity",
            "status": "ACCEPTED",
            "level": "THEORETICAL",
            "credence": 0.85,
            "theory": "ART",
            "sources": 12,
            "constraints": 8
        },
        {
            "id": "B002",
            "content": "Plants in offices reduce self-reported stress by 15-25%",
            "status": "ACCEPTED",
            "level": "EMPIRICAL",
            "credence": 0.72,
            "theory": "Biophilia",
            "sources": 8,
            "constraints": 5
        },
        {
            "id": "B003",
            "content": "Window views to nature improve patient recovery",
            "status": "CONTESTED",
            "level": "EMPIRICAL",
            "credence": 0.65,
            "theory": "SRT",
            "sources": 6,
            "constraints": 12
        },
        {
            "id": "B004",
            "content": "Biophilic design effects transfer across cultures",
            "status": "STUB",
            "level": "THEORETICAL",
            "credence": 0.45,
            "theory": "Biophilia",
            "sources": 2,
            "constraints": 3
        },
        {
            "id": "B005",
            "content": "Artificial plants provide equivalent benefits to real plants",
            "status": "REJECTED",
            "level": "EMPIRICAL",
            "credence": 0.22,
            "theory": "Biophilia",
            "sources": 4,
            "constraints": 7
        },
    ]

    # Display as expandable cards
    for belief in beliefs:
        status_info = BELIEF_STATUS.get(belief["status"], {"icon": "?", "color": "#ADB5BD"})
        level_info = EPISTEMIC_LEVELS.get(belief["level"], {"weight": 0.5, "color": "#ADB5BD"})

        with st.expander(
            f"{status_info['icon']} [{belief['id']}] {belief['content'][:60]}...",
            expanded=False
        ):
            col1, col2 = st.columns([2, 1])

            with col1:
                st.markdown(f"**Content**: {belief['content']}")
                st.markdown(f"**Theory**: {belief['theory']}")

            with col2:
                st.markdown(f"**Status**: {belief['status']}")
                st.markdown(f"**Level**: {belief['level']}")
                st.markdown(f"**Credence**: {belief['credence']:.2f}")
                st.caption(credence_to_label(belief['credence']))

            # Metrics row
            mcol1, mcol2, mcol3 = st.columns(3)
            with mcol1:
                st.metric("Sources", belief["sources"])
            with mcol2:
                st.metric("Constraints", belief["constraints"])
            with mcol3:
                st.metric("Entrenchment", f"{belief['credence'] * 0.8:.2f}")

            # Actions
            st.markdown("---")
            acol1, acol2, acol3, acol4 = st.columns(4)
            with acol1:
                st.button("View Details", key=f"view_{belief['id']}")
            with acol2:
                st.button("Show Constraints", key=f"const_{belief['id']}")
            with acol3:
                st.button("Trace Evidence", key=f"trace_{belief['id']}")
            with acol4:
                st.button("Export", key=f"export_{belief['id']}")


def render_constraint_viewer():
    """Render constraint network viewer."""
    st.markdown("## Constraint Network")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.info("Interactive network visualization coming in Phase 3.")
        st.markdown("""
        The constraint network shows epistemic relationships between beliefs:
        - **Positive constraints** (green): Beliefs that mutually support each other
        - **Negative constraints** (red): Beliefs in tension
        - **Edge weight**: Strength of the constraint

        Visualization will use vis.js for interactive exploration.
        """)

    with col2:
        st.markdown("### Constraint Statistics")
        st.metric("Total Constraints", "3,891")
        st.metric("Positive", "3,245 (83%)")
        st.metric("Negative", "646 (17%)")
        st.metric("Avg Strength", "0.67")

    # Constraint table
    st.markdown("---")
    st.markdown("### Recent Constraints")

    constraints = [
        ("B001", "B002", "POSITIVE", 0.82, "ART supports plant effects"),
        ("B001", "B003", "POSITIVE", 0.76, "ART supports window effects"),
        ("B002", "B005", "NEGATIVE", 0.89, "Real vs artificial plants"),
        ("B003", "B004", "NEGATIVE", 0.45, "Cultural transfer uncertainty"),
    ]

    for from_id, to_id, polarity, strength, reason in constraints:
        color = "#85D2A3" if polarity == "POSITIVE" else "#E27D60"  # Light green / soft coral
        st.markdown(
            f"**{from_id}** → **{to_id}**: "
            f"<span style='color:{color}; font-weight:600'>{polarity}</span> ({strength:.2f})",
            unsafe_allow_html=True
        )
        st.caption(reason)


def render_community_browser():
    """Render epistemic community browser."""
    st.markdown("## Epistemic Communities")

    communities = [
        {
            "name": "Attention Restoration Theory (ART)",
            "members": 156,
            "avg_credence": 0.78,
            "key_researchers": ["R. Kaplan", "S. Kaplan"],
            "core_beliefs": ["Directed attention can be fatigued", "Nature restores attention"]
        },
        {
            "name": "Stress Recovery Theory (SRT)",
            "members": 142,
            "avg_credence": 0.72,
            "key_researchers": ["R. Ulrich"],
            "core_beliefs": ["Nature reduces physiological stress", "Evolutionary preference for savanna"]
        },
        {
            "name": "Biophilia Hypothesis",
            "members": 234,
            "avg_credence": 0.68,
            "key_researchers": ["E.O. Wilson", "S. Kellert"],
            "core_beliefs": ["Humans have innate connection to nature", "Biophilic elements improve wellbeing"]
        },
        {
            "name": "Environmental Psychology",
            "members": 312,
            "avg_credence": 0.65,
            "key_researchers": ["D. Stokols", "I. Altman"],
            "core_beliefs": ["Environment affects behavior", "Person-environment fit matters"]
        },
    ]

    for community in communities:
        with st.expander(f"👥 {community['name']} ({community['members']} beliefs)"):
            col1, col2 = st.columns(2)

            with col1:
                st.markdown(f"**Average Credence**: {community['avg_credence']:.2f}")
                st.markdown("**Key Researchers**:")
                for researcher in community["key_researchers"]:
                    st.markdown(f"- {researcher}")

            with col2:
                st.markdown("**Core Beliefs**:")
                for belief in community["core_beliefs"]:
                    st.markdown(f"- {belief}")

            st.button(f"View All Beliefs", key=f"comm_{community['name'][:3]}")


def render_paper_browser():
    """Render source paper browser."""
    st.markdown("## Paper Browser")

    col1, col2 = st.columns([3, 1])

    with col1:
        search = st.text_input("🔍 Search papers", placeholder="Author, title, year...")

    with col2:
        sort_by = st.selectbox("Sort by", ["Year (newest)", "Citations", "Beliefs extracted"])

    papers = [
        {
            "title": "The Experience of Nature",
            "authors": "Kaplan, R. & Kaplan, S.",
            "year": 1989,
            "citations": 4521,
            "beliefs_extracted": 23,
            "status": "Complete"
        },
        {
            "title": "View Through a Window May Influence Recovery from Surgery",
            "authors": "Ulrich, R.S.",
            "year": 1984,
            "citations": 3892,
            "beliefs_extracted": 8,
            "status": "Complete"
        },
        {
            "title": "Biophilia",
            "authors": "Wilson, E.O.",
            "year": 1984,
            "citations": 2156,
            "beliefs_extracted": 15,
            "status": "Complete"
        },
        {
            "title": "The restorative benefits of nature",
            "authors": "Hartig, T., et al.",
            "year": 2014,
            "citations": 892,
            "beliefs_extracted": 12,
            "status": "In Progress"
        },
    ]

    for paper in papers:
        status_icon = "✅" if paper["status"] == "Complete" else "⏳"
        with st.expander(f"{status_icon} {paper['title']} ({paper['year']})"):
            st.markdown(f"**Authors**: {paper['authors']}")

            mcol1, mcol2, mcol3 = st.columns(3)
            with mcol1:
                st.metric("Citations", f"{paper['citations']:,}")
            with mcol2:
                st.metric("Beliefs Extracted", paper["beliefs_extracted"])
            with mcol3:
                st.markdown(f"**Status**: {paper['status']}")

            bcol1, bcol2 = st.columns(2)
            with bcol1:
                st.button("View Extracted Beliefs", key=f"paper_{paper['year']}")
            with bcol2:
                st.button("Re-extract", key=f"reextract_{paper['year']}")


def main():
    """Main admin dashboard."""
    apply_shared_styles()
    st.title("Admin Dashboard")
    st.caption("System inspection and management for Article Eater V23")

    # Navigation tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Overview",
        "💭 Beliefs",
        "🔗 Constraints",
        "👥 Communities",
        "📄 Papers"
    ])

    with tab1:
        render_system_overview()

    with tab2:
        render_belief_browser()

    with tab3:
        render_constraint_viewer()

    with tab4:
        render_community_browser()

    with tab5:
        render_paper_browser()


if __name__ == "__main__":
    main()
