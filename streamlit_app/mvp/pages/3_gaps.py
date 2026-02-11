"""
MVP Gaps Page
=============

Identifies knowledge gaps in the accumulated web.
"""

import streamlit as st
from pathlib import Path
import sys

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

st.set_page_config(page_title="Gaps | Article Eater MVP", page_icon="🔬", layout="wide")

st.title("🔬 Knowledge Gaps")
st.markdown("Identify areas where more research is needed.")

st.markdown("---")

# Mock gap data for demo
gaps = [
    {
        "domain": "attention",
        "coverage": 0.72,
        "gap": "Long-term effects of open-plan offices on sustained attention",
        "suggested_search": "longitudinal open-plan office attention",
        "priority": "HIGH"
    },
    {
        "domain": "stress",
        "coverage": 0.65,
        "gap": "Interaction between noise and temperature on stress responses",
        "suggested_search": "noise temperature stress interaction office",
        "priority": "MEDIUM"
    },
    {
        "domain": "productivity",
        "coverage": 0.58,
        "gap": "Individual differences in environmental sensitivity",
        "suggested_search": "environmental sensitivity individual differences",
        "priority": "HIGH"
    },
    {
        "domain": "creativity",
        "coverage": 0.45,
        "gap": "Effects of ceiling height on creative thinking",
        "suggested_search": "ceiling height creativity cognition",
        "priority": "LOW"
    },
    {
        "domain": "wellbeing",
        "coverage": 0.68,
        "gap": "Seasonal variation in biophilic design effects",
        "suggested_search": "seasonal biophilic design wellbeing",
        "priority": "MEDIUM"
    }
]

# Coverage overview
st.markdown("### Domain Coverage")

cols = st.columns(len(gaps))
for i, gap in enumerate(gaps):
    with cols[i]:
        coverage_pct = int(gap["coverage"] * 100)
        color = "🟢" if coverage_pct >= 70 else "🟡" if coverage_pct >= 50 else "🔴"
        st.metric(gap["domain"].title(), f"{color} {coverage_pct}%")

st.markdown("---")

# Gap details
st.markdown("### Identified Gaps")

for gap in sorted(gaps, key=lambda x: -{"HIGH": 3, "MEDIUM": 2, "LOW": 1}[x["priority"]]):
    priority_badge = {
        "HIGH": "🔴 HIGH",
        "MEDIUM": "🟡 MEDIUM",
        "LOW": "🟢 LOW"
    }[gap["priority"]]

    with st.expander(f"{gap['domain'].title()}: {gap['gap']}", expanded=(gap["priority"] == "HIGH")):
        col1, col2 = st.columns([3, 1])

        with col1:
            st.markdown(f"**Gap:** {gap['gap']}")
            st.markdown(f"**Suggested search:** `{gap['suggested_search']}`")

        with col2:
            st.markdown(f"**Priority:** {priority_badge}")
            st.progress(gap["coverage"])
            st.caption(f"Coverage: {int(gap['coverage']*100)}%")

        if st.button(f"Search Article Finder", key=f"search_{gap['domain']}"):
            st.info(f"Would search AF for: {gap['suggested_search']}")

st.markdown("---")

# Summary stats
st.markdown("### Gap Analysis Summary")

col1, col2, col3 = st.columns(3)

with col1:
    high_gaps = sum(1 for g in gaps if g["priority"] == "HIGH")
    st.metric("High Priority Gaps", high_gaps)

with col2:
    avg_coverage = sum(g["coverage"] for g in gaps) / len(gaps)
    st.metric("Average Coverage", f"{avg_coverage:.0%}")

with col3:
    st.metric("Domains Analyzed", len(gaps))

st.caption("Gap identification based on belief density and constraint coverage per domain.")
