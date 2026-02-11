"""
MVP Demo: Article Eater Web of Belief
=====================================

Minimal Streamlit interface for demonstrating the accumulated web of belief.

Features:
- Status: View accumulated statistics
- Query: Ask questions of the web
- Gaps: Identify knowledge gaps

Run with:
    streamlit run streamlit_app/mvp/app.py

Author: Claude Code (MVP-GUI)
Created: 2026-02-11
"""

import streamlit as st
from pathlib import Path
import sys

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Page configuration
st.set_page_config(
    page_title="Article Eater MVP",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for clean appearance
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f4e79;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
    }
    .stMetric label {
        font-size: 1rem !important;
    }
</style>
""", unsafe_allow_html=True)

# Main page content
st.markdown('<p class="main-header">Article Eater</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Web of Belief for Cognitive Neuroarchitecture Research</p>', unsafe_allow_html=True)

st.markdown("---")

# Quick overview
col1, col2 = st.columns(2)

with col1:
    st.markdown("### What is this?")
    st.markdown("""
    Article Eater extracts **evidence-backed rules** from scientific papers
    and accumulates them into a coherent **web of belief** using
    Quinean foundherentist epistemology.

    This MVP demonstrates:
    - **Persistent accumulation** across paper processing runs
    - **Query interface** for asking questions of the web
    - **Gap identification** for research planning
    """)

with col2:
    st.markdown("### Quick Start")
    st.markdown("""
    1. **Status** → View accumulated statistics
    2. **Query** → Ask questions about the web
    3. **Gaps** → Find knowledge gaps

    Use the sidebar to navigate between pages.
    """)

st.markdown("---")

# Try to show live stats if available
st.markdown("### Current Status")

try:
    from src.services.web_accumulator import get_accumulator
    acc = get_accumulator()
    stats = acc.get_stats()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Papers Processed", stats.total_papers_processed)
    with col2:
        st.metric("Total Beliefs", stats.total_beliefs)
    with col3:
        st.metric("Total Constraints", stats.total_constraints)
    with col4:
        st.metric("Coherence", f"{stats.coherence_score:.2f}")

except Exception as e:
    st.info("Accumulator not initialized yet. Process some papers first!")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Papers Processed", "—")
    with col2:
        st.metric("Total Beliefs", "—")
    with col3:
        st.metric("Total Constraints", "—")
    with col4:
        st.metric("Coherence", "—")

st.markdown("---")

# Footer
st.markdown("""
<div style="text-align: center; color: #888; padding: 2rem;">
    <small>Article Eater V23.0.0 • Post-Quinean Foundherentist Architecture</small>
</div>
""", unsafe_allow_html=True)
