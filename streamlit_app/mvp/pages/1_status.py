"""
MVP Status Page
===============

Shows accumulated web statistics and processing history.
"""

import streamlit as st
from pathlib import Path
import sys
import json
from datetime import datetime

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

st.set_page_config(page_title="Status | Article Eater MVP", page_icon="📊", layout="wide")

st.title("📊 Accumulated Web Status")
st.markdown("Real-time statistics from the web of belief accumulator.")

# Refresh button
col1, col2 = st.columns([4, 1])
with col2:
    if st.button("🔄 Refresh"):
        st.rerun()

st.markdown("---")

# Try to load real data
use_mock = False
stats = None
events = []

try:
    from src.services.web_accumulator import get_accumulator
    acc = get_accumulator()
    stats = acc.get_stats()
except Exception as e:
    use_mock = True
    st.warning(f"Using mock data (accumulator unavailable: {e})")

# Mock data for demo
if use_mock:
    st.warning("⚠️ **Demo Mode**: Using sample data. Process papers to see live statistics.", icon="⚠️")

    class MockStats:
        total_papers_processed = 47
        total_beliefs = 312
        total_constraints = 89
        total_bridges = 24
        coherence_score = 0.73
        last_updated = datetime.now().isoformat()
        beliefs_by_level = {
            "EMPIRICAL": 198,
            "THEORETICAL": 67,
            "METHODOLOGICAL": 32,
            "META": 15
        }
        beliefs_by_domain = {
            "attention": 87,
            "stress": 62,
            "productivity": 54,
            "wellbeing": 48,
            "creativity": 33,
            "other": 28
        }
        papers_processed = [f"paper_{i:03d}" for i in range(47)]
    stats = MockStats()

# Main metrics
st.markdown("### Key Metrics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Papers Processed",
        stats.total_papers_processed,
        help="Number of papers integrated into the web"
    )

with col2:
    st.metric(
        "Total Beliefs",
        stats.total_beliefs,
        help="Unique beliefs extracted and accumulated"
    )

with col3:
    st.metric(
        "Total Constraints",
        stats.total_constraints,
        help="Coherence constraints between beliefs"
    )

with col4:
    coherence_delta = None
    if hasattr(stats, 'prev_coherence') and stats.prev_coherence:
        coherence_delta = f"{(stats.coherence_score - stats.prev_coherence):.2f}"
    st.metric(
        "Coherence Score",
        f"{stats.coherence_score:.2f}",
        delta=coherence_delta,
        help="Global coherence of the web (0-1)"
    )

st.markdown("---")

# Breakdown charts
st.markdown("### Belief Distribution")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### By Epistemic Level")
    if hasattr(stats, 'beliefs_by_level') and stats.beliefs_by_level:
        import pandas as pd
        df = pd.DataFrame([
            {"Level": k, "Count": v}
            for k, v in stats.beliefs_by_level.items()
        ])
        st.bar_chart(df.set_index("Level"))
    else:
        st.info("No level breakdown available")

with col2:
    st.markdown("#### By Domain")
    if hasattr(stats, 'beliefs_by_domain') and stats.beliefs_by_domain:
        import pandas as pd
        df = pd.DataFrame([
            {"Domain": k, "Count": v}
            for k, v in stats.beliefs_by_domain.items()
        ])
        st.bar_chart(df.set_index("Domain"))
    else:
        st.info("No domain breakdown available")

st.markdown("---")

# Recent events
st.markdown("### Processing History")

# Try to load events from events.jsonl
events_path = PROJECT_ROOT / "data" / "events.jsonl"

if events_path.exists():
    try:
        with open(events_path) as f:
            events = [json.loads(line) for line in f if line.strip()][-20:]  # Last 20
        events.reverse()  # Most recent first

        if events:
            for event in events[:10]:
                event_type = event.get('event_type', 'unknown')
                paper_id = event.get('paper_id', 'N/A')
                timestamp = event.get('timestamp', '')[:19]  # Truncate microseconds
                details = event.get('details', {})

                if event_type == 'paper_processed':
                    beliefs = details.get('beliefs_added', 0)
                    st.success(f"✓ **{paper_id}** — +{beliefs} beliefs ({timestamp})")
                elif event_type == 'error':
                    error = details.get('error', 'Unknown error')[:50]
                    st.error(f"✗ **{paper_id}** — {error} ({timestamp})")
                else:
                    st.info(f"• {event_type}: {paper_id} ({timestamp})")
        else:
            st.info("No events recorded yet")
    except Exception as e:
        st.warning(f"Could not load events: {e}")
else:
    # Mock events for demo
    st.success("✓ **kaplan_1989** — +12 beliefs (2026-02-11 10:30:00)")
    st.success("✓ **ulrich_1984** — +8 beliefs (2026-02-11 10:25:00)")
    st.success("✓ **kellert_1993** — +15 beliefs (2026-02-11 10:20:00)")
    st.error("✗ **corrupt_pdf_001** — PDF extraction failed (2026-02-11 10:15:00)")
    st.success("✓ **appleton_1975** — +6 beliefs (2026-02-11 10:10:00)")

st.markdown("---")

# Processed papers list (expandable)
with st.expander("📋 View All Processed Papers"):
    if hasattr(stats, 'papers_processed') and stats.papers_processed:
        papers = stats.papers_processed
        col1, col2, col3 = st.columns(3)
        for i, paper_id in enumerate(papers):
            with [col1, col2, col3][i % 3]:
                st.text(f"• {paper_id}")
    else:
        st.info("No papers processed yet")

# Last updated
st.markdown("---")
if hasattr(stats, 'last_updated'):
    st.caption(f"Last updated: {stats.last_updated}")
