"""
Article Eater V23 — Streamlit Interface
Sprint 3.0 — 2026-02-08

Main entry point with user type selection and navigation.
"""

import streamlit as st
from config import (
    PAGE_TITLE, PAGE_ICON, LAYOUT, COLORS,
    USER_TYPES, UserType
)

# Page configuration
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout=LAYOUT,
    initial_sidebar_state="expanded"
)

# Custom CSS for light cheerful aesthetic
st.markdown("""
<style>
    /* Main container - warm cream background */
    .main {
        background-color: #FFF9F0;
    }

    .stApp {
        background-color: #FFF9F0;
    }

    /* Headers - soft blue instead of dark */
    h1, h2, h3 {
        color: #5B8FB9 !important;
        font-family: 'Georgia', serif;
    }

    h1 {
        color: #4A90A4 !important;
    }

    /* Paragraphs and text - soft gray, not black */
    p, span, label, .stMarkdown {
        color: #4A5568 !important;
    }

    /* User type cards */
    .user-type-card {
        background: #FFFFFF;
        border: 2px solid #E8F4F8;
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        cursor: pointer;
        transition: all 0.2s;
    }

    .user-type-card:hover {
        border-color: #7FC8A9;
        box-shadow: 0 4px 12px rgba(127, 200, 169, 0.2);
    }

    .user-type-card.selected {
        border-color: #7FC8A9;
        background: #F0FFF4;
    }

    /* Question buttons */
    .question-btn {
        background: #FFFFFF;
        border: 1px solid #E8F4F8;
        border-radius: 8px;
        padding: 10px 15px;
        margin: 5px;
        cursor: pointer;
        text-align: left;
        transition: all 0.2s;
    }

    .question-btn:hover {
        background: #F0FFF4;
        border-color: #7FC8A9;
    }

    /* Credence badges - softer colors */
    .credence-high {
        background: #85D2A3;
        color: #1A4D2E;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.85em;
    }

    .credence-moderate {
        background: #7FC8A9;
        color: #1A4D2E;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.85em;
    }

    .credence-low {
        background: #F5D491;
        color: #6B4423;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.85em;
    }

    /* Sidebar - light and airy */
    section[data-testid="stSidebar"] {
        background-color: #F0F7FA !important;
    }

    section[data-testid="stSidebar"] .stMarkdown {
        color: #4A5568 !important;
    }

    /* Status indicators - cheerful colors */
    .status-accepted { color: #85D2A3; }
    .status-rejected { color: #E27D60; }
    .status-contested { color: #E8A87C; }
    .status-stub { color: #B8C5D0; }

    /* Buttons - mint green accent */
    .stButton > button {
        background-color: #7FC8A9 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
    }

    .stButton > button:hover {
        background-color: #5BB389 !important;
    }

    /* Primary buttons */
    .stButton > button[kind="primary"] {
        background-color: #5B8FB9 !important;
    }

    .stButton > button[kind="primary"]:hover {
        background-color: #4A7A9E !important;
    }

    /* Metrics - softer styling */
    [data-testid="stMetricValue"] {
        color: #5B8FB9 !important;
    }

    /* Expanders */
    .streamlit-expanderHeader {
        background-color: #F8FCFF !important;
        border-radius: 8px !important;
    }

    /* Info boxes */
    .stAlert {
        background-color: #E8F4F8 !important;
        border: 1px solid #B8D4E3 !important;
        border-radius: 8px !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #F0F7FA;
        border-radius: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        color: #5B8FB9 !important;
    }

    /* Input fields */
    .stTextInput > div > div > input {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 8px !important;
    }

    /* Select boxes */
    .stSelectbox > div > div {
        background-color: #FFFFFF !important;
        border-radius: 8px !important;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables."""
    if "user_type" not in st.session_state:
        st.session_state.user_type = None
    if "current_query" not in st.session_state:
        st.session_state.current_query = ""
    if "query_results" not in st.session_state:
        st.session_state.query_results = None
    if "selected_belief" not in st.session_state:
        st.session_state.selected_belief = None


def render_user_type_selection():
    """Render user type selection cards."""
    st.title("Article Eater V23")
    st.markdown("### Evidence-backed knowledge for CNFA neuroarchitecture research")
    st.markdown("---")

    st.markdown("## Who are you?")
    st.markdown("Select your role to get tailored questions and interface.")

    # Create columns for user type cards
    cols = st.columns(len(USER_TYPES))

    for idx, (type_id, user_type) in enumerate(USER_TYPES.items()):
        with cols[idx]:
            # Card container
            is_selected = st.session_state.user_type == type_id
            card_class = "selected" if is_selected else ""

            with st.container():
                st.markdown(f"### {user_type.name}")
                if user_type.persona:
                    st.caption(f"*{user_type.persona}*")
                st.markdown(user_type.description)

                if st.button(
                    "Select" if not is_selected else "✓ Selected",
                    key=f"select_{type_id}",
                    type="primary" if is_selected else "secondary"
                ):
                    st.session_state.user_type = type_id
                    st.rerun()


def render_sidebar():
    """Render sidebar with navigation and user info."""
    with st.sidebar:
        st.markdown(f"## {PAGE_TITLE}")

        # User type indicator
        if st.session_state.user_type:
            user_type = USER_TYPES[st.session_state.user_type]
            st.markdown(f"### {user_type.name}")
            if st.button("Change Role", key="change_role"):
                st.session_state.user_type = None
                st.rerun()

        st.markdown("---")

        # Navigation
        st.markdown("### Navigation")

        # These will be actual page links in the final version
        pages = [
            ("Query", "Query the evidence base"),
            ("Explore", "Visual network exploration"),
            ("Communities", "Epistemic community browser"),
            ("Export", "Export evidence bundles"),
            ("Admin", "System dashboard"),
        ]

        for name, description in pages:
            st.markdown(f"**{name}**")
            st.caption(description)

        st.markdown("---")

        # Quick stats (placeholder)
        st.markdown("### System Status")
        st.metric("Beliefs", "1,247")
        st.metric("Constraints", "3,891")
        st.metric("Coherence", "0.72")


def render_common_questions(user_type: UserType):
    """Render common questions as clickable buttons."""
    st.markdown("### Common Questions")
    st.markdown(f"*Questions tailored for {user_type.name}*")

    # Create rows of question buttons
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
                        st.rerun()


def render_query_interface(user_type: UserType):
    """Render the main query interface."""
    st.markdown("## Query the Evidence Base")

    # Query input
    query = st.text_input(
        "Ask a question about the evidence",
        value=st.session_state.current_query,
        placeholder="e.g., What reduces stress in hospitals?",
        key="query_input"
    )

    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        if st.button("Search", type="primary", use_container_width=True):
            if query:
                st.session_state.current_query = query
                # Placeholder for actual query execution
                st.session_state.query_results = {
                    "headline": f"Results for: {query}",
                    "status": "pending"
                }

    with col2:
        response_mode = st.selectbox(
            "Response depth",
            ["Quick", "Standard", "Deep"],
            index=1
        )

    with col3:
        include_scope = st.checkbox("Show scope conditions", value=True)

    st.markdown("---")

    # Common questions section
    render_common_questions(user_type)

    # Results section (placeholder)
    if st.session_state.query_results:
        st.markdown("---")
        st.markdown("### Results")

        with st.container():
            st.info(f"**Query**: {st.session_state.current_query}")

            # Placeholder result
            st.markdown("""
            #### Headline
            Plants are associated with stress reduction in office settings
            (credence: 0.72 ± 0.12)

            #### Summary
            Multiple studies show 15-25% reduction in self-reported stress
            when plants are present in office environments. Evidence is
            strongest for:
            - Real plants (vs. artificial)
            - Visible greenery in direct line of sight
            - Minimum density of 1 plant per 10m²

            #### Scope Conditions
            - **Population**: Office workers, primarily Western countries
            - **Setting**: Indoor office environments
            - **Methodology**: Self-report surveys, some cortisol measurements
            - **Limitations**: Limited hospital data, no long-term studies

            #### Key Sources
            - Lohr et al. (1996) — n=96, cortisol + self-report
            - Bringslimark et al. (2007) — Meta-analysis, k=21
            - Fjeld (2000) — n=51, sick leave reduction
            """)

            # Export options
            col1, col2, col3 = st.columns(3)
            with col1:
                st.button("Copy Summary")
            with col2:
                st.button("Export BibTeX")
            with col3:
                st.button("View in Graph")


def render_main_interface():
    """Render the main interface after user type selection."""
    user_type = USER_TYPES[st.session_state.user_type]

    # Sidebar
    render_sidebar()

    # Main content
    st.title(f"{user_type.name} Mode")
    if user_type.persona:
        st.caption(f"Personalized for researchers like *{user_type.persona}*")

    # Tabs for different sections
    tab1, tab2, tab3 = st.tabs(["Query", "Explore", "Stats"])

    with tab1:
        render_query_interface(user_type)

    with tab2:
        st.markdown("## Network Exploration")
        st.info("Visual exploration of the belief network coming in next phase.")

        # Placeholder for network visualization
        st.markdown("""
        ### Available Visualizations
        - **Claim Network**: Force-directed graph of beliefs and constraints
        - **Community Structure**: Clustered view by epistemic community
        - **Evidence Flow**: Sankey diagram of supporting evidence
        - **Entrenchment Heatmap**: Color-coded by entrenchment scores
        """)

    with tab3:
        st.markdown("## Quick Statistics")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Beliefs", "1,247", "+23")
        with col2:
            st.metric("Constraints", "3,891", "+67")
        with col3:
            st.metric("Coherence", "0.72", "+0.02")
        with col4:
            st.metric("Papers", "312", "+5")

        st.markdown("---")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Belief Status Distribution")
            st.markdown("""
            - ✓ **Accepted**: 847 (68%)
            - ⚡ **Contested**: 231 (19%)
            - ? **Stub**: 142 (11%)
            - ✗ **Rejected**: 27 (2%)
            """)

        with col2:
            st.markdown("### Epistemic Level Distribution")
            st.markdown("""
            - **Theoretical**: 89 (7%)
            - **Intermediate**: 234 (19%)
            - **Empirical**: 756 (61%)
            - **Observational**: 168 (13%)
            """)


def main():
    """Main application entry point."""
    init_session_state()

    if st.session_state.user_type is None:
        render_user_type_selection()
    else:
        render_main_interface()


if __name__ == "__main__":
    main()
