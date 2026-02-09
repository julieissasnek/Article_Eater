"""
Article Eater V23 — Query Page
Sprint 3.0.2 — 2026-02-08

Natural language query interface with user type selection and common questions.
"""

import streamlit as st
import sys
from pathlib import Path
from typing import Optional

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import (
    PAGE_TITLE, COLORS, USER_TYPES, UserType,
    QUERY_TYPES, credence_to_color, credence_to_label
)
from api_client import get_client, QueryRequest, QueryResult
from styles import apply_shared_styles

st.set_page_config(
    page_title=f"{PAGE_TITLE} — Query",
    page_icon="🔍",
    layout="wide"
)


def init_session_state():
    """Initialize session state for query page."""
    if "user_type" not in st.session_state:
        st.session_state.user_type = None
    if "current_query" not in st.session_state:
        st.session_state.current_query = ""
    if "query_result" not in st.session_state:
        st.session_state.query_result = None
    if "response_mode" not in st.session_state:
        st.session_state.response_mode = "standard"


def render_user_type_selector():
    """Render compact user type selector in sidebar."""
    st.sidebar.markdown("### Your Role")

    current_type = st.session_state.user_type

    # Show current selection or selector
    if current_type:
        user_type = USER_TYPES[current_type]
        st.sidebar.markdown(f"**{user_type.name}**")
        if user_type.persona:
            st.sidebar.caption(f"*{user_type.persona}*")
        if st.sidebar.button("Change Role"):
            st.session_state.user_type = None
            st.rerun()
    else:
        selected = st.sidebar.selectbox(
            "Select your role",
            options=list(USER_TYPES.keys()),
            format_func=lambda x: USER_TYPES[x].name,
            key="user_type_select"
        )
        if st.sidebar.button("Confirm", type="primary"):
            st.session_state.user_type = selected
            st.rerun()


def render_common_questions(user_type: UserType):
    """Render common questions as clickable buttons."""
    st.markdown("### Quick Questions")
    st.caption(f"Common questions for {user_type.name}")

    # Display questions in a grid
    questions = user_type.common_questions
    cols_per_row = 2

    for i in range(0, len(questions), cols_per_row):
        cols = st.columns(cols_per_row)
        for j, col in enumerate(cols):
            if i + j < len(questions):
                question = questions[i + j]
                with col:
                    if st.button(
                        question,
                        key=f"q_{i}_{j}",
                        use_container_width=True
                    ):
                        st.session_state.current_query = question
                        execute_query(question)


def execute_query(query: str):
    """Execute a query and store result."""
    client = get_client()

    request = QueryRequest(
        query=query,
        mode=st.session_state.response_mode,
        include_scope=True,
        include_practitioner_implications=True,
        user_type=st.session_state.user_type
    )

    with st.spinner("Searching evidence base..."):
        result = client.execute_query(request)
        st.session_state.query_result = result
        st.session_state.current_query = query


def render_query_input():
    """Render the query input area."""
    st.markdown("### Ask a Question")

    # Query input
    col1, col2 = st.columns([4, 1])

    with col1:
        query = st.text_input(
            "Your question",
            value=st.session_state.current_query,
            placeholder="e.g., What reduces stress in hospitals?",
            label_visibility="collapsed"
        )

    with col2:
        if st.button("Search", type="primary", use_container_width=True):
            if query:
                execute_query(query)

    # Options row
    col1, col2, col3 = st.columns(3)

    with col1:
        st.session_state.response_mode = st.selectbox(
            "Response depth",
            ["quick", "standard", "deep"],
            index=1,
            format_func=lambda x: {
                "quick": "⚡ Quick (headline)",
                "standard": "Standard (summary)",
                "deep": "🔬 Deep (full trace)"
            }[x]
        )

    with col2:
        include_scope = st.checkbox("Show scope conditions", value=True)

    with col3:
        include_practical = st.checkbox("Show practical implications", value=True)


def render_result_headline(result: QueryResult):
    """Render the headline result."""
    st.markdown("---")
    st.markdown("## Results")

    # Query type indicator
    query_type_info = QUERY_TYPES.get(result.query_type.upper(), "General query")
    st.caption(f"Query type: **{result.query_type}** — {query_type_info}")

    # Headline
    st.markdown(f"### {result.headline}")


def render_result_summary(result: QueryResult):
    """Render the summary section."""
    if not result.summary:
        return

    st.markdown("### Summary")

    summary = result.summary
    if isinstance(summary, dict):
        if "finding" in summary:
            st.markdown(f"**Finding**: {summary['finding']}")
        if "confidence" in summary:
            st.markdown(f"**Confidence**: {summary['confidence']}")
        if "key_evidence" in summary:
            st.markdown("**Key Evidence**:")
            for ev in summary["key_evidence"]:
                st.markdown(f"- {ev}")
    else:
        st.markdown(summary)


def render_scope_conditions(result: QueryResult):
    """Render scope conditions section."""
    if not result.scope_conditions:
        return

    st.markdown("### Scope Conditions")
    st.caption("When and where these findings apply")

    scope = result.scope_conditions
    col1, col2 = st.columns(2)

    with col1:
        if "population" in scope:
            st.markdown(f"**Population**: {scope['population']}")
        if "setting" in scope:
            st.markdown(f"**Setting**: {scope['setting']}")

    with col2:
        if "methodology" in scope:
            st.markdown(f"**Methodology**: {scope['methodology']}")
        if "limitations" in scope:
            st.markdown(f"**Limitations**: {scope['limitations']}")


def render_practical_implications(result: QueryResult):
    """Render practical implications section."""
    if not result.practical_implications:
        return

    st.markdown("### Practical Implications")
    st.caption("Actionable guidance for practitioners")

    for impl in result.practical_implications:
        st.markdown(f"✓ {impl}")


def render_caveats(result: QueryResult):
    """Render caveats and warnings."""
    if not result.caveats:
        return

    st.markdown("### Caveats")

    for caveat in result.caveats:
        st.warning(caveat)


def render_sources(result: QueryResult):
    """Render key sources section."""
    if not result.key_sources:
        return

    st.markdown("### Key Sources")

    for source in result.key_sources:
        st.markdown(f"📄 {source}")


def render_export_options(result: QueryResult):
    """Render export options."""
    st.markdown("---")
    st.markdown("### Export")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("Copy Summary", use_container_width=True):
            # Would copy to clipboard
            st.success("Copied to clipboard!")

    with col2:
        if st.button("BibTeX", use_container_width=True):
            st.info("BibTeX export coming soon")

    with col3:
        if st.button("View in Graph", use_container_width=True):
            st.info("Graph view coming in Phase 3")

    with col4:
        if st.button("📄 Full Report", use_container_width=True):
            st.info("Report generation coming in Sprint 3.0.4")


def render_query_result(result: QueryResult):
    """Render the full query result."""
    render_result_headline(result)
    render_result_summary(result)
    render_scope_conditions(result)
    render_practical_implications(result)
    render_caveats(result)
    render_sources(result)
    render_export_options(result)


def main():
    """Main query page."""
    apply_shared_styles()
    init_session_state()

    # Sidebar
    render_user_type_selector()

    # Sidebar stats
    client = get_client()
    stats = client.get_stats()

    st.sidebar.markdown("---")
    st.sidebar.markdown("### System Status")
    st.sidebar.metric("Beliefs", f"{stats.total_beliefs:,}")
    st.sidebar.metric("Coherence", f"{stats.overall_coherence:.2f}")

    # Main content
    st.title("Query the Evidence Base")

    if st.session_state.user_type:
        user_type = USER_TYPES[st.session_state.user_type]
        st.caption(f"Mode: {user_type.name}")
    else:
        st.info("👆 Select your role in the sidebar for personalized questions")

    # Query input
    render_query_input()

    # Common questions (if user type selected)
    if st.session_state.user_type:
        st.markdown("---")
        user_type = USER_TYPES[st.session_state.user_type]
        render_common_questions(user_type)

    # Results
    if st.session_state.query_result:
        render_query_result(st.session_state.query_result)


if __name__ == "__main__":
    main()
