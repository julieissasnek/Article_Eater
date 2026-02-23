"""
Corpus Statistics - Article Finder Database Overview.
Shows paper counts, processing status, and extraction results.
"""

import streamlit as st
from pathlib import Path
import sqlite3
from datetime import datetime
import sys

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.services.db_locator import resolve_article_finder_db

# Article Finder database path
try:
    AF_DB_PATH = resolve_article_finder_db()
except Exception:
    AF_DB_PATH = Path.home() / "REPOS" / "Article_Finder_v3_2_3" / "data" / "article_finder.db"


def get_stats():
    """Query Article Finder database for statistics."""
    if not AF_DB_PATH.exists():
        return None

    conn = sqlite3.connect(str(AF_DB_PATH))
    conn.row_factory = sqlite3.Row

    stats = {}

    # Total papers
    stats["total_papers"] = conn.execute("SELECT COUNT(*) FROM papers").fetchone()[0]

    # By status
    rows = conn.execute("SELECT status, COUNT(*) as cnt FROM papers GROUP BY status ORDER BY cnt DESC").fetchall()
    stats["by_status"] = {row["status"] or "null": row["cnt"] for row in rows}

    # PDF status
    stats["with_pdf"] = conn.execute("SELECT COUNT(*) FROM papers WHERE pdf_path IS NOT NULL AND pdf_path != ''").fetchone()[0]
    stats["without_pdf"] = stats["total_papers"] - stats["with_pdf"]

    # Metadata completeness
    stats["with_doi"] = conn.execute("SELECT COUNT(*) FROM papers WHERE doi IS NOT NULL").fetchone()[0]
    stats["with_abstract"] = conn.execute("SELECT COUNT(*) FROM papers WHERE abstract IS NOT NULL AND abstract != ''").fetchone()[0]
    stats["with_year"] = conn.execute("SELECT COUNT(*) FROM papers WHERE year IS NOT NULL").fetchone()[0]

    # Triage decisions
    rows = conn.execute("SELECT triage_decision, COUNT(*) as cnt FROM papers WHERE triage_decision IS NOT NULL GROUP BY triage_decision").fetchall()
    stats["by_triage"] = {row["triage_decision"]: row["cnt"] for row in rows}

    # Article Eater results
    stats["claims"] = conn.execute("SELECT COUNT(*) FROM claims").fetchone()[0]
    stats["rules"] = conn.execute("SELECT COUNT(*) FROM rules").fetchone()[0]
    stats["ae_success"] = conn.execute("SELECT COUNT(*) FROM papers WHERE ae_status = 'SUCCESS'").fetchone()[0]
    stats["ae_partial"] = conn.execute("SELECT COUNT(*) FROM papers WHERE ae_status = 'PARTIAL_SUCCESS'").fetchone()[0]
    stats["ae_fail"] = conn.execute("SELECT COUNT(*) FROM papers WHERE ae_status = 'FAIL'").fetchone()[0]

    # Citations
    stats["citations"] = conn.execute("SELECT COUNT(*) FROM citations").fetchone()[0]

    # Expansion queue
    stats["expansion_pending"] = conn.execute("SELECT COUNT(*) FROM expansion_queue WHERE status = 'pending'").fetchone()[0]

    # Extracted tables
    try:
        stats["total_tables"] = conn.execute("SELECT COUNT(*) FROM extracted_tables").fetchone()[0]
        stats["tables_with_stats"] = conn.execute("SELECT COUNT(*) FROM extracted_tables WHERE has_statistics = 1").fetchone()[0]
        stats["tables_needing_review"] = conn.execute("SELECT COUNT(*) FROM extracted_tables WHERE needs_review = 1 AND reviewed_at IS NULL").fetchone()[0]
    except Exception:
        stats["total_tables"] = 0
        stats["tables_with_stats"] = 0
        stats["tables_needing_review"] = 0

    conn.close()
    return stats


st.title("Corpus Statistics")
st.caption(f"Article Finder Database: {AF_DB_PATH}")

stats = get_stats()

if stats is None:
    st.error(f"Database not found at {AF_DB_PATH}")
else:
    st.markdown("---")

    # Top-level metrics
    st.subheader("Overview")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Papers", f"{stats['total_papers']:,}")
    col2.metric("With PDF", f"{stats['with_pdf']:,}", f"{100*stats['with_pdf']/stats['total_papers']:.1f}%" if stats['total_papers'] else "")
    col3.metric("Claims Extracted", stats["claims"])
    col4.metric("Rules Extracted", stats["rules"])

    st.markdown("---")

    # Processing pipeline
    st.subheader("Processing Pipeline")
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Candidates", stats["by_status"].get("candidate", 0))
    col2.metric("AE Success", stats["ae_success"])
    col3.metric("AE Partial", stats["ae_partial"])
    col4.metric("AE Failed", stats["ae_fail"])
    col5.metric("Rejected", stats["by_status"].get("rejected", 0))

    st.markdown("---")

    # Metadata completeness
    st.subheader("Metadata Completeness")
    col1, col2, col3, col4 = st.columns(4)
    total = stats["total_papers"] or 1
    col1.metric("With DOI", f"{stats['with_doi']:,}", f"{100*stats['with_doi']/total:.0f}%")
    col2.metric("With Abstract", f"{stats['with_abstract']:,}", f"{100*stats['with_abstract']/total:.0f}%")
    col3.metric("With Year", f"{stats['with_year']:,}", f"{100*stats['with_year']/total:.0f}%")
    col4.metric("With PDF", f"{stats['with_pdf']:,}", f"{100*stats['with_pdf']/total:.0f}%")

    st.markdown("---")

    # Status breakdown
    st.subheader("Papers by Status")
    if stats["by_status"]:
        for status, count in sorted(stats["by_status"].items(), key=lambda x: -x[1]):
            pct = 100 * count / stats["total_papers"] if stats["total_papers"] else 0
            st.text(f"  {status}: {count:,} ({pct:.1f}%)")

    # Triage breakdown
    if stats["by_triage"]:
        st.subheader("Triage Decisions")
        for decision, count in sorted(stats["by_triage"].items(), key=lambda x: -x[1]):
            st.text(f"  {decision}: {count:,}")

    st.markdown("---")

    # Extracted Tables
    st.subheader("Extracted Tables")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Tables", stats["total_tables"])
    col2.metric("With Statistics", stats["tables_with_stats"])
    col3.metric("Needs Review", stats["tables_needing_review"])

    st.markdown("---")

    # Citation network
    st.subheader("Citation Network")
    col1, col2 = st.columns(2)
    col1.metric("Total Citations", f"{stats['citations']:,}")
    col2.metric("Expansion Queue", f"{stats['expansion_pending']:,}")

    st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
