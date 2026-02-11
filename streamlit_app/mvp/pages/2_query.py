"""
MVP Query Page
==============

Interface for querying the web of belief.
"""

import streamlit as st
from pathlib import Path
import sys
from dataclasses import dataclass
from typing import List, Optional, Dict

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

st.set_page_config(page_title="Query | Article Eater MVP", page_icon="🔍", layout="wide")

st.title("🔍 Query the Web of Belief")
st.markdown("Ask questions about what the accumulated research says.")

st.markdown("---")

# Query input
query = st.text_input(
    "Enter your question:",
    placeholder="e.g., What affects attention in office environments?",
    help="Ask a natural language question about the research"
)

col1, col2 = st.columns([3, 1])
with col1:
    search_type = st.radio(
        "Search type:",
        ["Natural language", "Keyword", "Domain"],
        horizontal=True
    )
with col2:
    max_results = st.slider("Max results", 5, 50, 10)

search_button = st.button("🔍 Search", type="primary", use_container_width=True)

st.markdown("---")

# Mock query results for demo
@dataclass
class MockBelief:
    belief_id: str
    content: str
    credence: float
    level: str
    domain: str
    paper_ids: List[str]
    n_supporting: int

def get_mock_results(query: str) -> List[MockBelief]:
    """Generate mock results based on query keywords."""
    all_beliefs = [
        MockBelief(
            belief_id="belief_001",
            content="Natural light exposure improves cognitive performance in office workers",
            credence=0.82,
            level="EMPIRICAL",
            domain="attention",
            paper_ids=["kaplan_1989", "ulrich_1991"],
            n_supporting=7
        ),
        MockBelief(
            belief_id="belief_002",
            content="Views of nature reduce mental fatigue and restore directed attention",
            credence=0.78,
            level="THEORETICAL",
            domain="attention",
            paper_ids=["kaplan_1995", "berman_2008"],
            n_supporting=5
        ),
        MockBelief(
            belief_id="belief_003",
            content="Open-plan offices increase distractions and reduce focus",
            credence=0.71,
            level="EMPIRICAL",
            domain="attention",
            paper_ids=["kim_2013", "bernstein_2018"],
            n_supporting=4
        ),
        MockBelief(
            belief_id="belief_004",
            content="Biophilic design elements reduce stress markers in occupants",
            credence=0.76,
            level="EMPIRICAL",
            domain="stress",
            paper_ids=["kellert_2008", "browning_2014"],
            n_supporting=6
        ),
        MockBelief(
            belief_id="belief_005",
            content="Indoor plants improve air quality perception and wellbeing",
            credence=0.68,
            level="EMPIRICAL",
            domain="wellbeing",
            paper_ids=["lohr_1996", "bringslimark_2009"],
            n_supporting=3
        ),
        MockBelief(
            belief_id="belief_006",
            content="Noise levels above 55dB impair concentration on complex tasks",
            credence=0.85,
            level="EMPIRICAL",
            domain="attention",
            paper_ids=["banbury_2005", "hongisto_2016"],
            n_supporting=8
        ),
        MockBelief(
            belief_id="belief_007",
            content="Temperature between 21-23°C optimizes cognitive performance",
            credence=0.79,
            level="EMPIRICAL",
            domain="productivity",
            paper_ids=["seppanen_2006", "lan_2011"],
            n_supporting=5
        ),
        MockBelief(
            belief_id="belief_008",
            content="Prospect-refuge theory explains preference for semi-enclosed spaces",
            credence=0.72,
            level="THEORETICAL",
            domain="wellbeing",
            paper_ids=["appleton_1975", "dosen_2016"],
            n_supporting=4
        ),
    ]

    if not query:
        return []

    # Simple keyword matching for demo
    query_lower = query.lower()
    keywords = query_lower.split()

    results = []
    for belief in all_beliefs:
        content_lower = belief.content.lower()
        domain_lower = belief.domain.lower()

        # Check for matches
        score = 0
        for kw in keywords:
            if kw in content_lower:
                score += 2
            if kw in domain_lower:
                score += 1

        if score > 0:
            results.append((score, belief))

    # Sort by score and return
    results.sort(key=lambda x: (-x[0], -x[1].credence))
    return [r[1] for r in results[:max_results]]

# Try to use real query engine if available
def try_real_query(query: str, mode: str = "summary", include_gaps: bool = False) -> Optional[Dict]:
    """Try to use the real query engine."""
    try:
        from src.services.query_engine import QueryEngine
        engine = QueryEngine()
        return engine.query(query, response_mode=mode, include_gaps=include_gaps)
    except ImportError as e:
        st.warning(f"QueryEngine not available: {e}")
        return None
    except Exception as e:
        st.error(f"Query error: {e}")
        return None


def format_real_results(response: Dict) -> List[MockBelief]:
    """Convert real query response to display format."""
    results = []

    # Get evidence from summary or detail
    evidence = []
    if "summary" in response and response["summary"]:
        evidence = response["summary"].get("key_evidence", [])
    if "detail" in response and response["detail"]:
        evidence = response["detail"].get("all_evidence", evidence)

    for ev in evidence:
        results.append(MockBelief(
            belief_id=ev.get("belief_id", "unknown"),
            content=ev.get("content", ""),
            credence=ev.get("credence", 0.5),
            level=ev.get("source_depth", "UNKNOWN").upper(),
            domain=ev.get("domain", "general"),
            paper_ids=ev.get("paper_ids", []),
            n_supporting=len(ev.get("paper_ids", []))
        ))

    return results

# Results display
if search_button and query:
    st.markdown("### Results")

    # Try real query first
    real_response = try_real_query(query, mode="detail", include_gaps=True)

    if real_response is not None and real_response.get("status") == "success":
        results = format_real_results(real_response)
        st.success(f"Live query engine: {real_response.get('headline', '')[:100]}")

        # Show follow-ups if available
        if "follow_ups" in real_response:
            with st.expander("Suggested follow-up questions"):
                for fu in real_response.get("follow_ups", []):
                    st.markdown(f"- **{fu.get('type', '')}**: {fu.get('question', '')}")

        # Show gaps if available
        if "gaps" in real_response and real_response["gaps"].get("n_gaps", 0) > 0:
            with st.expander(f"Knowledge gaps ({real_response['gaps']['n_gaps']})"):
                for gap in real_response["gaps"].get("top_gaps", []):
                    st.warning(f"**{gap.get('gap_type', '')}**: {gap.get('description', '')}")
    elif real_response is not None:
        results = []
        st.warning(f"Query returned: {real_response.get('status', 'unknown')} - {real_response.get('headline', '')}")
    else:
        results = get_mock_results(query)
        st.info("Using mock data (query engine not available)")

    if not results:
        st.warning("No matching beliefs found. Try different keywords.")
    else:
        st.markdown(f"Found **{len(results)}** relevant beliefs:")
        st.markdown("")

        for i, belief in enumerate(results, 1):
            with st.container():
                # Credence as progress bar
                credence_pct = int(belief.credence * 100)
                credence_color = (
                    "🟢" if credence_pct >= 75 else
                    "🟡" if credence_pct >= 50 else
                    "🟠"
                )

                col1, col2 = st.columns([4, 1])

                with col1:
                    st.markdown(f"**{i}. {belief.content}**")
                    st.caption(
                        f"Level: {belief.level} • Domain: {belief.domain} • "
                        f"Sources: {', '.join(belief.paper_ids[:3])}"
                        f"{'...' if len(belief.paper_ids) > 3 else ''}"
                    )

                with col2:
                    st.markdown(f"{credence_color} **{credence_pct}%**")
                    st.progress(belief.credence)
                    st.caption(f"n={belief.n_supporting}")

                st.markdown("---")

elif search_button:
    st.warning("Please enter a query")

# Example queries
st.markdown("### Example Queries")
example_queries = [
    "What affects attention in offices?",
    "How does natural light impact productivity?",
    "What reduces stress in work environments?",
    "Effects of noise on concentration",
    "Benefits of biophilic design"
]

cols = st.columns(len(example_queries))
for i, eq in enumerate(example_queries):
    with cols[i]:
        if st.button(eq, key=f"example_{i}", use_container_width=True):
            st.session_state['query'] = eq
            st.rerun()
