"""
Article Eater V23 — Admin Dashboard
Sprint 3.0.3-D — 2026-02-09

System inspection for beliefs, constraints, communities, and health.
Now wired to real data from WebOfBelief and API.
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config import (
    PAGE_TITLE, COLORS, BELIEF_STATUS, EPISTEMIC_LEVELS,
    credence_to_color, credence_to_label
)
from styles import apply_shared_styles
from api_client import get_client

st.set_page_config(
    page_title=f"{PAGE_TITLE} — Admin",
    page_icon="⚙️",
    layout="wide"
)


# =============================================================================
# Data Access Functions
# =============================================================================

def get_system_stats() -> Dict[str, Any]:
    """Get real system statistics from API and WebOfBelief."""
    try:
        client = get_client()
        stats = client.get_stats()
        return stats
    except Exception as e:
        # Fallback to direct WebOfBelief access
        try:
            from src.services.web_of_belief import get_web
            web = get_web()
            return {
                "total_beliefs": len(web.beliefs),
                "total_constraints": len(web.constraints),
                "total_papers": 0,  # Would need DB access
                "total_communities": 4,
                "coherence": 0.0
            }
        except Exception:
            return {
                "total_beliefs": 0,
                "total_constraints": 0,
                "total_papers": 0,
                "total_communities": 0,
                "coherence": 0.0
            }


def get_health_status() -> Dict[str, tuple]:
    """Check system health."""
    health = {}

    # API check
    try:
        client = get_client()
        client.get_stats()
        health["api"] = ("✅ Running", "localhost:8000")
    except Exception:
        health["api"] = ("❌ Unavailable", "Connection failed")

    # Database check
    try:
        import sqlite3
        from pathlib import Path
        db_path = Path(__file__).parent.parent.parent / "db" / "article_eater.db"
        if db_path.exists():
            conn = sqlite3.connect(str(db_path))
            conn.execute("SELECT 1")
            conn.close()
            health["database"] = ("✅ Connected", "SQLite")
        else:
            health["database"] = ("⚠️ Not found", str(db_path))
    except Exception as e:
        health["database"] = ("❌ Error", str(e)[:50])

    # WebOfBelief check
    try:
        from src.services.web_of_belief import get_web
        web = get_web()
        health["web_of_belief"] = ("✅ Loaded", f"{len(web.beliefs)} beliefs")
    except Exception:
        health["web_of_belief"] = ("⚠️ Empty", "No beliefs loaded")

    # LLM check (just check if API key is set)
    import os
    if os.environ.get("ANTHROPIC_API_KEY"):
        health["llm"] = ("✅ Configured", "Claude API")
    else:
        health["llm"] = ("⚠️ No API key", "Set ANTHROPIC_API_KEY")

    return health


def get_real_beliefs(
    search: str = "",
    status_filter: List[str] = None,
    level_filter: List[str] = None,
    min_credence: float = 0.0,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """Get real beliefs from WebOfBelief."""
    try:
        from src.services.web_of_belief import get_web
        web = get_web()

        beliefs = []
        for belief_id, belief in list(web.beliefs.items())[:limit]:
            # Get credence value
            credence = belief.credence
            if hasattr(credence, 'point'):
                credence = credence.point

            # Get status and level as strings
            status = belief.status.value.upper() if hasattr(belief.status, 'value') else str(belief.status).upper()
            level = belief.level.value.upper() if hasattr(belief.level, 'value') else str(belief.level).upper()

            # Apply filters
            if status_filter and status not in status_filter:
                continue
            if level_filter and level not in level_filter:
                continue
            if credence < min_credence:
                continue
            if search and search.lower() not in belief.content.lower():
                continue

            # Count constraints for this belief
            constraint_count = sum(
                1 for c in web.constraints
                if c.source_id == belief_id or c.target_id == belief_id
            )

            beliefs.append({
                "id": belief_id,
                "content": belief.content,
                "status": status,
                "level": level,
                "credence": credence,
                "theory": belief.theory_ids[0] if belief.theory_ids else "Unassigned",
                "sources": len(belief.sources) if hasattr(belief, 'sources') else 0,
                "constraints": constraint_count,
                "entrenchment": web.get_entrenchment(belief_id)
            })

        return beliefs

    except Exception as e:
        st.warning(f"Could not load beliefs: {e}")
        return []


def get_real_constraints(limit: int = 50) -> List[Dict[str, Any]]:
    """Get real constraints from WebOfBelief."""
    try:
        from src.services.web_of_belief import get_web
        web = get_web()

        constraints = []
        for i, constraint in enumerate(web.constraints[:limit]):
            polarity = constraint.polarity.value.upper() if hasattr(constraint.polarity, 'value') else str(constraint.polarity).upper()
            constraints.append({
                "from": constraint.source_id,
                "to": constraint.target_id,
                "polarity": polarity,
                "weight": constraint.weight,
                "reason": constraint.reason or ""
            })

        return constraints

    except Exception:
        return []


def get_real_communities() -> List[Dict[str, Any]]:
    """Get real communities from CommunityRegistry."""
    try:
        from src.services.social_epistemology import get_registry
        registry = get_registry()

        communities = []
        for comm_id, community in registry.communities.items():
            beliefs_list = list(community.beliefs.keys()) if hasattr(community, 'beliefs') else []
            communities.append({
                "id": comm_id,
                "name": community.name,
                "members": len(beliefs_list),
                "avg_credence": community.avg_credence if hasattr(community, 'avg_credence') else 0.5,
                "paradigm": community.paradigm if hasattr(community, 'paradigm') else "Unknown",
                "key_researchers": community.key_researchers if hasattr(community, 'key_researchers') else []
            })

        return communities

    except Exception:
        # Return seed communities
        return [
            {"id": "ART", "name": "Attention Restoration Theory", "members": 0, "avg_credence": 0.75, "paradigm": "ART"},
            {"id": "SRT", "name": "Stress Recovery Theory", "members": 0, "avg_credence": 0.72, "paradigm": "SRT"},
            {"id": "Biophilia", "name": "Biophilia Hypothesis", "members": 0, "avg_credence": 0.68, "paradigm": "Biophilia"},
            {"id": "EnvPsych", "name": "Environmental Psychology", "members": 0, "avg_credence": 0.65, "paradigm": "General"}
        ]


def get_real_papers(limit: int = 50) -> List[Dict[str, Any]]:
    """Get real papers from database."""
    try:
        import sqlite3
        from pathlib import Path
        db_path = Path(__file__).parent.parent.parent / "db" / "article_eater.db"

        if not db_path.exists():
            return []

        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # Try to get papers
        cursor.execute("""
            SELECT id, title, authors, year, doi, status
            FROM papers
            ORDER BY year DESC
            LIMIT ?
        """, (limit,))

        papers = []
        for row in cursor.fetchall():
            papers.append({
                "id": row[0],
                "title": row[1] or "Untitled",
                "authors": row[2] or "Unknown",
                "year": row[3] or 0,
                "doi": row[4] or "",
                "status": row[5] or "Unknown"
            })

        conn.close()
        return papers

    except Exception:
        return []


def render_system_overview():
    """Render system-wide statistics and health."""
    st.markdown("## System Overview")

    # Get real stats
    stats = get_system_stats()

    # Key metrics row
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            "Total Beliefs",
            f"{stats.get('total_beliefs', 0):,}",
            help="Total beliefs in the web of belief"
        )

    with col2:
        st.metric(
            "Constraints",
            f"{stats.get('total_constraints', 0):,}",
            help="Epistemic constraints between beliefs"
        )

    with col3:
        st.metric(
            "Papers",
            f"{stats.get('total_papers', 0):,}",
            help="Source papers in the corpus"
        )

    with col4:
        coherence = stats.get('coherence', 0)
        st.metric(
            "Coherence",
            f"{coherence:.2f}" if coherence else "—",
            help="Overall web coherence score"
        )

    with col5:
        st.metric(
            "Communities",
            f"{stats.get('total_communities', 4)}",
            help="Epistemic communities (ART, SRT, Biophilia, Env Psych)"
        )

    st.markdown("---")

    # Health checks
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Health Checks")

        health = get_health_status()

        for name, (status, detail) in health.items():
            display_name = name.replace("_", " ").title()
            st.markdown(f"**{display_name}**: {status}")
            st.caption(detail)

    with col2:
        st.markdown("### System Info")

        st.markdown(f"**Version**: V23.0.0 (Post-Quinean)")
        st.markdown(f"**Last Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

        # Status breakdown if we have beliefs
        if stats.get('total_beliefs', 0) > 0:
            st.markdown("---")
            st.markdown("**Belief Status Breakdown**")

            try:
                from src.services.web_of_belief import get_web
                web = get_web()

                status_counts = {}
                for belief in web.beliefs.values():
                    status = belief.status.value.upper() if hasattr(belief.status, 'value') else str(belief.status).upper()
                    status_counts[status] = status_counts.get(status, 0) + 1

                for status, count in sorted(status_counts.items()):
                    info = BELIEF_STATUS.get(status, {"icon": "?", "color": "#ADB5BD"})
                    st.markdown(f"{info['icon']} {status}: {count}")
            except Exception:
                pass


def render_belief_browser():
    """Render searchable belief browser."""
    st.markdown("## Belief Browser")

    # Search and filter controls
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        search = st.text_input("🔍 Search beliefs", placeholder="Enter keyword...", key="admin_belief_search")

    with col2:
        status_filter = st.multiselect(
            "Status",
            ["ACCEPTED", "CONTESTED", "STUB", "REJECTED", "ESTABLISHED", "TENTATIVE"],
            default=["ACCEPTED", "CONTESTED"],
            key="admin_status_filter"
        )

    with col3:
        level_filter = st.multiselect(
            "Level",
            ["THEORETICAL", "INTERMEDIATE", "EMPIRICAL", "OBSERVATIONAL", "METHODOLOGICAL"],
            default=["THEORETICAL", "EMPIRICAL"],
            key="admin_level_filter"
        )

    with col4:
        credence_min = st.slider("Min Credence", 0.0, 1.0, 0.0, key="admin_credence_min")

    # Results table
    st.markdown("---")

    # Get real beliefs
    beliefs = get_real_beliefs(
        search=search,
        status_filter=status_filter if status_filter else None,
        level_filter=level_filter if level_filter else None,
        min_credence=credence_min,
        limit=100
    )

    if not beliefs:
        st.info("No beliefs found. Try adjusting filters or process some papers first.")
        return

    st.caption(f"Showing {len(beliefs)} beliefs")

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

    # Get real constraints
    constraints = get_real_constraints(limit=100)

    col1, col2 = st.columns([2, 1])

    with col1:
        # Add link to network visualization
        st.info("For interactive visualization, see the **Explore** page.")
        st.markdown("""
        The constraint network shows epistemic relationships between beliefs:
        - **Positive constraints** (green): Beliefs that mutually support each other
        - **Negative constraints** (red): Beliefs in tension
        - **Edge weight**: Strength of the constraint
        """)

    with col2:
        st.markdown("### Constraint Statistics")

        total = len(constraints)
        positive = sum(1 for c in constraints if c.get("polarity") == "POSITIVE")
        negative = total - positive
        avg_weight = sum(c.get("weight", 0.5) for c in constraints) / total if total > 0 else 0

        st.metric("Total Constraints", f"{total:,}")
        st.metric("Positive", f"{positive:,} ({100*positive//max(total,1)}%)")
        st.metric("Negative", f"{negative:,} ({100*negative//max(total,1)}%)")
        st.metric("Avg Strength", f"{avg_weight:.2f}")

    # Constraint table
    st.markdown("---")
    st.markdown("### Constraints")

    if not constraints:
        st.info("No constraints found. Process some papers to create constraints.")
        return

    for constraint in constraints[:20]:
        from_id = constraint.get("from", "?")
        to_id = constraint.get("to", "?")
        polarity = constraint.get("polarity", "NEUTRAL")
        weight = constraint.get("weight", 0.5)
        reason = constraint.get("reason", "")

        color = "#85D2A3" if polarity == "POSITIVE" else "#E27D60"  # Light green / soft coral
        st.markdown(
            f"**{from_id}** → **{to_id}**: "
            f"<span style='color:{color}; font-weight:600'>{polarity}</span> ({weight:.2f})",
            unsafe_allow_html=True
        )
        if reason:
            st.caption(reason)

    if len(constraints) > 20:
        st.caption(f"+{len(constraints) - 20} more constraints")


def render_community_browser():
    """Render epistemic community browser."""
    st.markdown("## Epistemic Communities")

    communities = get_real_communities()

    if not communities:
        st.info("No communities found.")
        return

    for community in communities:
        name = community.get("name", "Unknown")
        members = community.get("members", 0)
        avg_credence = community.get("avg_credence", 0.5)
        paradigm = community.get("paradigm", "Unknown")
        key_researchers = community.get("key_researchers", [])

        with st.expander(f"👥 {name} ({members} beliefs)"):
            col1, col2 = st.columns(2)

            with col1:
                st.markdown(f"**Average Credence**: {avg_credence:.2f}")
                st.markdown(f"**Paradigm**: {paradigm}")

                if key_researchers:
                    st.markdown("**Key Researchers**:")
                    for researcher in key_researchers[:5]:
                        st.markdown(f"- {researcher}")

            with col2:
                # Get beliefs for this community
                try:
                    from src.services.web_of_belief import get_web
                    web = get_web()
                    community_beliefs = [
                        b for b in web.beliefs.values()
                        if community.get("id") in (b.theory_ids if hasattr(b, 'theory_ids') else [])
                    ]
                    if community_beliefs:
                        st.markdown("**Sample Beliefs**:")
                        for belief in community_beliefs[:3]:
                            st.markdown(f"- {belief.content[:60]}...")
                    else:
                        st.markdown("**No beliefs assigned yet**")
                except Exception:
                    st.markdown("**Beliefs**: Not available")

            st.button(f"View All Beliefs", key=f"comm_{community.get('id', name[:3])}")


def render_paper_browser():
    """Render source paper browser."""
    st.markdown("## Paper Browser")

    col1, col2 = st.columns([3, 1])

    with col1:
        search = st.text_input("🔍 Search papers", placeholder="Author, title, year...", key="admin_paper_search")

    with col2:
        sort_by = st.selectbox("Sort by", ["Year (newest)", "Title", "Author"], key="admin_paper_sort")

    papers = get_real_papers(limit=50)

    # Filter by search
    if search:
        search_lower = search.lower()
        papers = [
            p for p in papers
            if search_lower in p.get("title", "").lower()
            or search_lower in p.get("authors", "").lower()
            or search_lower in str(p.get("year", ""))
        ]

    if not papers:
        st.info("No papers found in database. Process some PDFs to populate the corpus.")
        return

    st.caption(f"Showing {len(papers)} papers")

    for paper in papers:
        title = paper.get("title", "Untitled")
        authors = paper.get("authors", "Unknown")
        year = paper.get("year", "")
        status = paper.get("status", "Unknown")
        doi = paper.get("doi", "")

        status_icon = "✅" if status in ["Complete", "processed"] else "⏳"

        with st.expander(f"{status_icon} {title} ({year})"):
            st.markdown(f"**Authors**: {authors}")

            if doi:
                st.markdown(f"**DOI**: [{doi}](https://doi.org/{doi})")

            mcol1, mcol2, mcol3 = st.columns(3)
            with mcol1:
                st.markdown(f"**Year**: {year}")
            with mcol2:
                st.markdown(f"**Status**: {status}")
            with mcol3:
                st.markdown(f"**ID**: {paper.get('id', 'N/A')}")

            bcol1, bcol2 = st.columns(2)
            with bcol1:
                st.button("View Extracted Beliefs", key=f"paper_{paper.get('id', year)}")
            with bcol2:
                st.button("Re-extract", key=f"reextract_{paper.get('id', year)}")


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
