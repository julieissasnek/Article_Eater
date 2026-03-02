# scripts/ae_streamlit_control_room.py
"""Article Eater Control Room (Streamlit)

A simple, inspectable dashboard for monitoring the research pipeline:

1. Job Queue (processing_queue)
2. Recent Findings (findings JOIN articles)
3. Library Stats (articles, findings, failed jobs)

Run with:

    streamlit run scripts/ae_streamlit_control_room.py
"""

import os
import sys
import time
from datetime import datetime
from pathlib import Path

import pandas as pd
import sqlite3
import streamlit as st

# Ensure repo root is importable when Streamlit runs this script.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.ui_events import log_ui_event

# ---------------------------------------------------------------------
# Page Config
# ---------------------------------------------------------------------
st.set_page_config(
    page_title="Article Eater Control Room",
    page_icon="🦁",
    layout="wide",
)

# ---------------------------------------------------------------------
# DB CONFIG & SETUP
# ---------------------------------------------------------------------
# Prefer explicit env vars, then fallback to local ae.db
DB_PATH = (
    os.environ.get("AE_DB_PATH")
    or os.environ.get("AE_DB")
    or "ae.db"
)

# --- PATCH: Always show render-gate status + DB truth panel -------------------
st.caption("UI Loaded — if you can read this, Streamlit is rendering content.")

def _safe_count(cur: sqlite3.Cursor, table: str) -> int | None:
    try:
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        return int(cur.fetchone()[0])
    except Exception as e:
        import logging; logging.getLogger(__name__).debug(f"Returning None: {e}")
        return None

def _safe_distinct_status(cur: sqlite3.Cursor, table: str):
    try:
        cur.execute(f"SELECT DISTINCT status FROM {table} ORDER BY status")
        return [r[0] for r in cur.fetchall()]
    except Exception as e:
        import logging; logging.getLogger(__name__).debug(f"Returning None: {e}")
        return None

with st.expander("DB Diagnostics (always visible)", expanded=False):
    st.write("DB:", str(Path(DB_PATH).expanduser().resolve()))
    db_path = Path(DB_PATH).expanduser().resolve()
    st.write("Exists:", db_path.exists(), "Size:", db_path.stat().st_size if db_path.exists() else None)
    if db_path.exists():
        con = sqlite3.connect(str(db_path))
        cur = con.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
        tables = [r[0] for r in cur.fetchall()]
        st.write("Tables:", tables)

        for t in ["articles", "findings", "queue", "jobs", "ui_events", "work_queue", "paper_queue", "processing_queue"]:
            n = _safe_count(cur, t)
            if n is not None:
                st.write(f"{t}: {n}")

        for t in ["queue", "jobs", "work_queue", "paper_queue", "processing_queue"]:
            sts = _safe_distinct_status(cur, t)
            if sts is not None:
                st.write(f"{t}.status:", sts)

        con.close()
# --- END PATCH ----------------------------------------------------------------


def get_connection() -> sqlite3.Connection:
    """Create a SQLite connection suitable for dashboard reads.

    - Uses the same DB path convention as the backend.
    - Enables WAL mode (should already be on, but we assert it).
    - Uses a 30s timeout to play nicely with concurrent workers.
    """
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    # WAL should already be enabled, but this is idempotent.
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn


def get_core_counts() -> dict:
    """Fetch lightweight row counts for quick UI feedback."""
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM articles")
        articles = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM findings")
        findings = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM processing_queue")
        queue = cur.fetchone()[0]
    return {"articles": articles, "findings": findings, "queue": queue}


def seed_demo_data() -> dict:
    """Insert small demo dataset for UI previewing."""
    demo_article_id = "demo:article:001"
    demo_job_id = "demo-job-001"
    now = datetime.now().isoformat()
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM articles WHERE article_id = ?", (demo_article_id,))
        has_article = cur.fetchone()[0] > 0
        if not has_article:
            cur.execute(
                """
                INSERT INTO articles(
                    article_id, title, abstract, doi, corpus_id, authors, year,
                    venue, full_text, sections, text_length, is_open_access,
                    citation_count, url_pdf, ingested_at, created_at
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    demo_article_id,
                    "Demo Article: Sleep and Memory Consolidation",
                    "A small synthetic abstract for UI preview purposes.",
                    "10.1234/demo.sleep.2025",
                    "demo-corpus-001",
                    "Doe, J.; Smith, A.",
                    2025,
                    "Journal of Demo Science",
                    "",
                    "",
                    0,
                    1,
                    12,
                    "https://example.com/demo.pdf",
                    now,
                    now,
                ),
            )
        cur.execute("SELECT COUNT(*) FROM findings WHERE paper_id = ?", (demo_article_id,))
        has_findings = cur.fetchone()[0] > 0
        if not has_findings:
            cur.execute(
                """
                INSERT INTO findings(
                    finding_level, consequent, antecedents, operational_measure,
                    measure_type, measure_direction, p_value, effect_size,
                    sample_size, job_id, paper_id, created_at
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    "primary",
                    "memory_recall",
                    "sleep_duration",
                    "recall_score",
                    "behavioral",
                    "positive",
                    0.03,
                    0.42,
                    120,
                    demo_job_id,
                    demo_article_id,
                    now,
                ),
            )
        cur.execute("SELECT COUNT(*) FROM processing_queue WHERE job_id = ?", (demo_job_id,))
        has_job = cur.fetchone()[0] > 0
        if not has_job:
            cur.execute(
                """
                INSERT INTO processing_queue(
                    job_id, job_type, params, status, priority, result, error,
                    created_at, started_at, completed_at, updated_at
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    demo_job_id,
                    "demo_extract",
                    '{"source":"demo","note":"seeded for UI"}',
                    "completed",
                    50,
                    '{"status":"ok"}',
                    None,
                    now,
                    now,
                    now,
                    now,
                ),
            )
        conn.commit()
    return {"seeded_article": not has_article, "seeded_finding": not has_findings, "seeded_job": not has_job}


# ---------------------------------------------------------------------
# SIDEBAR CONTROLS
# ---------------------------------------------------------------------
st.sidebar.title("🦁 Control Room")

auto_refresh = st.sidebar.checkbox("Auto-Refresh (5s)", value=True)
show_debug = st.sidebar.checkbox("Show Debug Snapshot", value=False)

log_ui_event(
    surface="control_room",
    action="view",
    user_id=os.environ.get("USER") or os.environ.get("USERNAME") or "",
    detail={"auto_refresh": bool(auto_refresh)},
)


st.sidebar.markdown(
    """

    **Tips**

    - Turn on *Auto-Refresh* while running workers.
    - Use this page to spot failed or stuck jobs quickly.
    - DB path is taken from `AE_DB_PATH` / `AE_DB` or `ae.db` by default.
    """
)

st.sidebar.markdown("---")
st.sidebar.subheader("Demo Data")
if st.sidebar.button("Insert demo rows"):
    seeded = seed_demo_data()
    st.sidebar.success(
        "Seeded demo data: "
        + ", ".join([k for k, v in seeded.items() if v]) if any(seeded.values()) else "Demo data already present."
    )

if auto_refresh:
    st.sidebar.caption("Auto-refresh is enabled.")

# ---------------------------------------------------------------------
# MAIN DASHBOARD
# ---------------------------------------------------------------------
st.markdown(
    """
    <div style="padding:12px;border:2px solid #ff6b6b;background:#fff5f5;color:#111;border-radius:8px;">
      <strong>UI Loaded</strong> — if you can read this, Streamlit is rendering content.
    </div>
    """,
    unsafe_allow_html=True,
)
st.title("Research Pipeline Status")
st.caption(f"DB: {DB_PATH}")

try:
    counts = get_core_counts()
    st.metric("Articles", counts["articles"])
    st.metric("Findings", counts["findings"])
    st.metric("Queue", counts["queue"])
    if counts["articles"] == 0 and counts["findings"] == 0 and counts["queue"] == 0:
        st.warning("No data yet. Check that workers are running and writing to this DB.")
    elif counts["findings"] == 0:
        st.info("DB is reachable, but no findings yet. Jobs may still be running.")
    else:
        st.success("Data detected. UI should render populated sections below.")
except Exception as exc:
    st.error(f"DB connection error: {exc}")

if show_debug:
    with st.expander("Debug: DB snapshot", expanded=True):
        try:
            with get_connection() as conn:
                df_articles_preview = pd.read_sql_query(
                    "SELECT article_id, title, year, venue, created_at FROM articles ORDER BY created_at DESC LIMIT 5",
                    conn,
                )
                df_findings_preview = pd.read_sql_query(
                    "SELECT id, finding_level, consequent, effect_size, p_value, created_at FROM findings ORDER BY created_at DESC LIMIT 5",
                    conn,
                )
                df_queue_preview = pd.read_sql_query(
                    "SELECT job_id, job_type, status, created_at FROM processing_queue ORDER BY created_at DESC LIMIT 5",
                    conn,
                )
            st.write("Articles (top 5)")
            st.dataframe(df_articles_preview, use_container_width=True, hide_index=True)
            st.write("Findings (top 5)")
            st.dataframe(df_findings_preview, use_container_width=True, hide_index=True)
            st.write("Queue (top 5)")
            st.dataframe(df_queue_preview, use_container_width=True, hide_index=True)
        except Exception as exc:
            st.error(f"Debug preview failed: {exc}")
else:
    st.caption("Debug snapshot hidden. Use the sidebar toggle to show it.")

# ---------------------------------------------------------------------
# 1. QUEUE STATUS (The Heartbeat)
# ---------------------------------------------------------------------
st.subheader("1. Job Queue")

try:
    with get_connection() as conn:
        df_queue = pd.read_sql_query(
            """

            SELECT
                job_id,
                job_type,
                status,
                priority,
                created_at,
                started_at,
                completed_at,
                error,
                result
            FROM processing_queue
            ORDER BY
                CASE status
                    WHEN 'running' THEN 1
                    WHEN 'pending' THEN 2
                    ELSE 3
                END,
                created_at DESC
            LIMIT 50
            """,

            conn,
        )
except Exception as exc:
    st.error(f"Error reading job queue from DB: {exc}")
    df_queue = pd.DataFrame()

if not df_queue.empty:
    def color_status(val: str) -> str:
        """Light background colours by status."""
        if val == "running":
            return "background-color: #fff3cd"  # light amber (accessible)
        if val == "failed":
            return "background-color: #ffe6e6"  # light red
        if val == "complete":
            return "background-color: #e6ffe6"  # light green
        return ""

    st.dataframe(
        df_queue.style.applymap(color_status, subset=["status"]),
        use_container_width=True,
        hide_index=True,
    )
else:
    st.info("Queue is empty or unavailable.")

# ---------------------------------------------------------------------
# 2. FINDINGS STREAM (The Output)
# ---------------------------------------------------------------------
st.subheader("2. Recent Findings")

try:
    with get_connection() as conn:
        df_findings = pd.read_sql_query(
            """

            SELECT
                f.id,
                f.finding_level,
                f.consequent,
                f.effect_size,
                f.p_value,
                a.title AS paper,
                f.created_at
            FROM findings f
            JOIN articles a
                ON f.paper_id = a.article_id
            ORDER BY f.created_at DESC
            LIMIT 10
            """,

            conn,
        )
except Exception as exc:
    st.error(f"Error reading findings from DB: {exc}")
    df_findings = pd.DataFrame()

if not df_findings.empty:
    st.dataframe(
        df_findings,
        use_container_width=True,
        hide_index=True,
    )
else:
    st.write("No findings extracted yet (or unable to query findings).")

# ---------------------------------------------------------------------
# 3. LIBRARY STATS (The Scope)
# ---------------------------------------------------------------------
st.subheader("3. Library Stats")

col1, col2, col3 = st.columns(3)

count_papers = 0
count_findings = 0
count_errors = 0

try:
    with get_connection() as conn:
        row = conn.execute("SELECT COUNT(*) FROM articles").fetchone()
        if row:
            count_papers = row[0]

        row = conn.execute("SELECT COUNT(*) FROM findings").fetchone()
        if row:
            count_findings = row[0]

        row = conn.execute(
            "SELECT COUNT(*) FROM processing_queue WHERE status = 'failed'"
        ).fetchone()
        if row:
            count_errors = row[0]
except Exception as exc:
    st.error(f"Error reading library stats from DB: {exc}")

col1.metric("📚 Papers", count_papers)
col2.metric("🔍 Findings", count_findings)
col3.metric("❌ Job Errors", count_errors)

# ---------------------------------------------------------------------
# 4. TABLE REVIEW (TBL-5: Extracted Tables from PDFs)
# ---------------------------------------------------------------------
st.subheader("4. Extracted Tables")

# Output directory selector
output_base = st.text_input(
    "Output Directory",
    value=str(Path.home() / "ae_outputs"),
    help="Base directory where pipeline outputs are stored"
)

output_path = Path(output_base).expanduser()
if output_path.exists() and output_path.is_dir():
    # Find all tables.jsonl files in subdirectories
    tables_files = list(output_path.rglob("tables.jsonl"))

    if tables_files:
        # Sort by modification time, most recent first
        tables_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)

        # Create dropdown of available table files
        file_options = [str(f.relative_to(output_path)) for f in tables_files[:20]]
        selected_file = st.selectbox(
            "Select tables file",
            options=file_options,
            help="Choose a tables.jsonl file to review"
        )

        if selected_file:
            tables_path = output_path / selected_file
            try:
                import json
                tables_data = []
                with open(tables_path, 'r') as f:
                    for line in f:
                        if line.strip():
                            tables_data.append(json.loads(line))

                if tables_data:
                    st.write(f"Found **{len(tables_data)}** tables in this file")

                    # Table selector
                    table_options = [
                        f"{t.get('table_id', 'unknown')}: {t.get('title', 'Untitled')} (Page {t.get('page_number', '?')})"
                        for t in tables_data
                    ]
                    selected_table_idx = st.selectbox(
                        "Select table to review",
                        options=range(len(table_options)),
                        format_func=lambda i: table_options[i]
                    )

                    if selected_table_idx is not None:
                        table = tables_data[selected_table_idx]

                        # Display table metadata
                        col_meta1, col_meta2 = st.columns(2)
                        with col_meta1:
                            st.write("**Table ID:**", table.get('table_id', 'unknown'))
                            st.write("**Type:**", table.get('table_type', 'unknown'))
                            st.write("**Page:**", table.get('page_number', 'unknown'))
                        with col_meta2:
                            st.write("**Confidence:**", f"{table.get('confidence', 0):.2f}")
                            st.write("**Method:**", table.get('extraction_method', 'unknown'))
                            st.write("**Title:**", table.get('title', 'Untitled'))

                        # Display table content as DataFrame
                        headers = table.get('headers', [])
                        rows = table.get('rows', [])

                        if headers and rows:
                            # Ensure all rows have same number of columns as headers
                            normalized_rows = []
                            for row in rows:
                                if len(row) < len(headers):
                                    row = row + [''] * (len(headers) - len(row))
                                elif len(row) > len(headers):
                                    row = row[:len(headers)]
                                normalized_rows.append(row)

                            df_table = pd.DataFrame(normalized_rows, columns=headers)
                            st.dataframe(df_table, use_container_width=True, hide_index=True)
                        else:
                            st.info("No structured data available for this table")

                        # Show raw JSON in expander
                        with st.expander("Raw table data"):
                            st.json(table)
                else:
                    st.info("No tables found in this file")
            except Exception as e:
                st.error(f"Error reading tables file: {e}")
    else:
        st.info("No tables.jsonl files found in output directory")
else:
    st.warning(f"Output directory not found: {output_path}")

# Also check for table claims if available
st.markdown("---")
st.write("**Table-derived Claims**")

if output_path.exists() and output_path.is_dir() and 'selected_file' in dir() and selected_file:
    # Look for claims from same output directory
    claims_path = tables_path.parent / "claims.jsonl"
    if claims_path.exists():
        try:
            import json
            table_claims = []
            with open(claims_path, 'r') as f:
                for line in f:
                    if line.strip():
                        claim = json.loads(line)
                        # Check if claim is from a table source
                        source = claim.get('source', {})
                        if source.get('type') == 'table':
                            table_claims.append(claim)

            if table_claims:
                st.write(f"Found **{len(table_claims)}** claims derived from tables")

                # Display as DataFrame
                claims_display = []
                for c in table_claims[:20]:  # Limit to 20
                    claims_display.append({
                        "claim_id": c.get('claim_id', 'unknown'),
                        "type": c.get('claim_type', 'unknown'),
                        "content": c.get('claim_text', c.get('content', ''))[:100] + '...' if len(c.get('claim_text', c.get('content', ''))) > 100 else c.get('claim_text', c.get('content', '')),
                        "table_id": c.get('source', {}).get('table_id', 'unknown'),
                        "confidence": c.get('confidence', 0),
                    })

                df_claims = pd.DataFrame(claims_display)
                st.dataframe(df_claims, use_container_width=True, hide_index=True)
            else:
                st.info("No table-derived claims found in claims.jsonl")
        except Exception as e:
            st.error(f"Error reading claims: {e}")
    else:
        st.info("No claims.jsonl found in the same directory")
else:
    st.caption("Select a tables file above to view associated claims")

# ---------------------------------------------------------------------
# 5. PAPER LIFECYCLE (Unified Pipeline Health)
# ---------------------------------------------------------------------
st.subheader("5. Paper Lifecycle")

# Check if lifecycle tables exist
try:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='paper_lifecycle'")
        has_lifecycle_table = cur.fetchone() is not None

        if has_lifecycle_table:
            # Stage Distribution
            st.write("**Stage Distribution**")
            try:
                df_stages = pd.read_sql_query(
                    """
                    SELECT
                        lifecycle_stage as stage,
                        COUNT(*) as count
                    FROM articles
                    WHERE lifecycle_stage IS NOT NULL
                    GROUP BY lifecycle_stage
                    ORDER BY
                        CASE lifecycle_stage
                            WHEN 'discovered' THEN 1
                            WHEN 'searched' THEN 2
                            WHEN 'retrieved' THEN 3
                            WHEN 'stored' THEN 4
                            WHEN 'typed' THEN 5
                            WHEN 'extracting' THEN 6
                            WHEN 'extracted' THEN 7
                            WHEN 'synthesizing' THEN 8
                            WHEN 'synthesized' THEN 9
                            WHEN 'archived' THEN 10
                            WHEN 'failed' THEN 11
                            ELSE 12
                        END
                    """,
                    conn,
                )
                if not df_stages.empty:
                    # Display as horizontal bar chart
                    st.bar_chart(df_stages.set_index('stage')['count'])

                    # Also show as metrics row
                    cols = st.columns(min(len(df_stages), 6))
                    for idx, row in df_stages.iterrows():
                        col_idx = idx % len(cols)
                        with cols[col_idx]:
                            stage_name = row['stage'].capitalize() if row['stage'] else "Unknown"
                            st.metric(stage_name, row['count'])
                else:
                    st.info("No lifecycle data yet. Papers will appear here after processing.")
            except Exception as e:
                st.warning(f"Could not load stage distribution: {e}")

            st.markdown("---")

            # Blocked Papers
            st.write("**Blocked Papers**")
            try:
                df_blocked = pd.read_sql_query(
                    """
                    SELECT
                        article_id as paper_id,
                        title,
                        lifecycle_stage as stage,
                        lifecycle_blocked_reason as reason,
                        lifecycle_updated_at as blocked_since
                    FROM articles
                    WHERE lifecycle_blocked_reason IS NOT NULL
                    ORDER BY lifecycle_updated_at DESC
                    LIMIT 10
                    """,
                    conn,
                )
                if not df_blocked.empty:
                    st.warning(f"**{len(df_blocked)}** papers are currently blocked")

                    def color_blocked(val):
                        return "background-color: #ffe6e6"

                    st.dataframe(
                        df_blocked.style.applymap(color_blocked, subset=['reason']),
                        use_container_width=True,
                        hide_index=True,
                    )
                else:
                    st.success("No blocked papers")
            except Exception as e:
                st.caption(f"Could not load blocked papers: {e}")

            st.markdown("---")

            # Recent Lifecycle Activity
            st.write("**Recent Lifecycle Activity**")
            try:
                df_activity = pd.read_sql_query(
                    """
                    SELECT
                        paper_id,
                        stage,
                        status,
                        started_at,
                        duration_seconds,
                        n_claims,
                        n_rules,
                        error_message
                    FROM paper_lifecycle
                    ORDER BY started_at DESC
                    LIMIT 15
                    """,
                    conn,
                )
                if not df_activity.empty:
                    def color_status(val):
                        if val == 'success':
                            return "background-color: #e6ffe6"
                        if val == 'failed':
                            return "background-color: #ffe6e6"
                        if val == 'in_progress':
                            return "background-color: #fff3cd"  # light amber (accessible)
                        return ""

                    st.dataframe(
                        df_activity.style.applymap(color_status, subset=['status']),
                        use_container_width=True,
                        hide_index=True,
                    )
                else:
                    st.info("No lifecycle activity recorded yet")
            except Exception as e:
                st.caption(f"Could not load lifecycle activity: {e}")

            st.markdown("---")

            # Pipeline Health Summary
            st.write("**Pipeline Health (Last 7 Days)**")
            try:
                # Success rate by stage
                df_health = pd.read_sql_query(
                    """
                    SELECT
                        stage,
                        SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successes,
                        COUNT(*) as total,
                        ROUND(AVG(duration_seconds), 2) as avg_duration_s
                    FROM paper_lifecycle
                    WHERE started_at >= datetime('now', '-7 days')
                    GROUP BY stage
                    ORDER BY stage
                    """,
                    conn,
                )
                if not df_health.empty:
                    # Calculate success rate
                    df_health['success_rate'] = (df_health['successes'] / df_health['total'] * 100).round(1)
                    df_health['success_rate'] = df_health['success_rate'].astype(str) + '%'

                    st.dataframe(
                        df_health[['stage', 'total', 'successes', 'success_rate', 'avg_duration_s']],
                        use_container_width=True,
                        hide_index=True,
                    )
                else:
                    st.info("No processing activity in the last 7 days")
            except Exception as e:
                st.caption(f"Could not load health summary: {e}")

        else:
            st.info(
                "Paper lifecycle tracking is not yet enabled. "
                "Run the 018_paper_lifecycle.sql migration to enable."
            )
except Exception as e:
    st.error(f"Error loading lifecycle data: {e}")

# ---------------------------------------------------------------------
# FOOTER
# ---------------------------------------------------------------------
st.caption(
    f"Connected to: `{DB_PATH}` | Last Updated: {datetime.now().strftime('%H:%M:%S')}"
)

if auto_refresh:
    # Refresh after rendering so the UI isn't blank during reruns.
    st.caption("Refreshing in 5s...")
    time.sleep(5)
    st.rerun()
