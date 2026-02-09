"""
Shared styles for Article Eater Streamlit Interface
Sprint 3.0 — 2026-02-08

Light cheerful color scheme applied consistently across all pages.
"""

from config import COLORS

# Shared CSS for all pages
SHARED_CSS = f"""
<style>
    /* Main container - warm cream background */
    .main {{
        background-color: {COLORS['background']};
    }}

    .stApp {{
        background-color: {COLORS['background']};
    }}

    /* Headers - soft blue */
    h1, h2, h3 {{
        color: {COLORS['primary']} !important;
        font-family: 'Georgia', serif;
    }}

    h1 {{
        color: #4A90A4 !important;
    }}

    /* Text - soft gray, not black */
    p, span, label, .stMarkdown {{
        color: {COLORS['text']} !important;
    }}

    /* Sidebar - light and airy */
    section[data-testid="stSidebar"] {{
        background-color: #F0F7FA !important;
    }}

    section[data-testid="stSidebar"] .stMarkdown {{
        color: {COLORS['text']} !important;
    }}

    /* Buttons - mint green accent */
    .stButton > button {{
        background-color: {COLORS['secondary']} !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
    }}

    .stButton > button:hover {{
        background-color: #5BB389 !important;
    }}

    .stButton > button[kind="primary"] {{
        background-color: {COLORS['primary']} !important;
    }}

    .stButton > button[kind="primary"]:hover {{
        background-color: #4A7A9E !important;
    }}

    /* Metrics - softer styling */
    [data-testid="stMetricValue"] {{
        color: {COLORS['primary']} !important;
    }}

    /* Expanders */
    .streamlit-expanderHeader {{
        background-color: #F8FCFF !important;
        border-radius: 8px !important;
    }}

    /* Info boxes */
    .stAlert {{
        background-color: #E8F4F8 !important;
        border: 1px solid #B8D4E3 !important;
        border-radius: 8px !important;
    }}

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        background-color: #F0F7FA;
        border-radius: 8px;
    }}

    .stTabs [data-baseweb="tab"] {{
        color: {COLORS['primary']} !important;
    }}

    /* Input fields */
    .stTextInput > div > div > input {{
        background-color: {COLORS['card_bg']} !important;
        border: 1px solid {COLORS['border']} !important;
        border-radius: 8px !important;
    }}

    /* Select boxes */
    .stSelectbox > div > div {{
        background-color: {COLORS['card_bg']} !important;
        border-radius: 8px !important;
    }}

    /* Cards and containers */
    .element-container {{
        color: {COLORS['text']};
    }}

    /* Credence badges */
    .credence-high {{
        background: {COLORS['success']};
        color: #1A4D2E;
        padding: 2px 8px;
        border-radius: 4px;
    }}

    .credence-moderate {{
        background: {COLORS['secondary']};
        color: #1A4D2E;
        padding: 2px 8px;
        border-radius: 4px;
    }}

    .credence-low {{
        background: {COLORS['accent']};
        color: #6B4423;
        padding: 2px 8px;
        border-radius: 4px;
    }}

    /* Status indicators */
    .status-accepted {{ color: {COLORS['success']}; }}
    .status-rejected {{ color: {COLORS['danger']}; }}
    .status-contested {{ color: {COLORS['warning']}; }}
    .status-stub {{ color: #B8C5D0; }}
</style>
"""


def apply_shared_styles():
    """Apply shared styles to the current page. Call this at the start of each page."""
    import streamlit as st
    st.markdown(SHARED_CSS, unsafe_allow_html=True)
