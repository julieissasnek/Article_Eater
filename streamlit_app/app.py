"""
Article Eater Streamlit Application.

Main entry point for the Streamlit UI. Run with:
    streamlit run streamlit_app/app.py

Created: 2026-02-08
"""

import streamlit as st
from pathlib import Path
import sys

# Add project root to path for imports
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Page config
st.set_page_config(
    page_title="Article Eater",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

# Main page content
st.title("Article Eater")
st.caption("Post-Quinean Evidence Extraction System")

st.markdown("---")

st.markdown("""
Article Eater extracts evidence-backed rules from scientific articles using
foundherentist epistemology. This interface provides tools for:

- **BibTeX Import** — Link metadata to uploaded PDFs
- **Query** — Natural language queries over the knowledge base
- **Explore** — Browse beliefs, communities, and tensions
- **Export** — Generate BibTeX, summaries, and reports

Use the sidebar to navigate.
""")

# Sidebar info
st.sidebar.caption("V23.0.0")

# Show quick stats if available
try:
    from src.services.web_persistence import PersistenceService
    service = PersistenceService()
    stats = service.get_statistics("master")
    if stats:
        st.sidebar.metric("Beliefs", stats.get("n_beliefs", 0))
        st.sidebar.metric("Papers", stats.get("n_papers", 0))
except Exception:
    pass
