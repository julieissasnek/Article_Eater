"""
OVERSEER Health Dashboard — Cartwright's Multi-Metric Coherence Visualization
Article Eater Sprint OVERSEER — 2026-02-25

Displays system health from the OVERSEER service:
  - Health Status Banner (OPERATIONAL/INITIALIZING/ERROR)
  - Coherence Panel (global + per-theory + trend)
  - Integrity Panel (invariant violations)
  - Completeness Panel (template coverage + beliefs per theory)
  - Cache & BN Health
  - Quarantine Queue (7-day review protocol)
  - Recent Activity Log

Data source: overseer.db (SQLite) — migration 023
Accessibility: WCAG 2.1 AA compliant (no dark blue on dark backgrounds)
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional
import sys

import streamlit as st
import pandas as pd

# ============================================================================
# Setup: Paths and imports
# ============================================================================

REPO_ROOT = Path(__file__).resolve().parents[2]
STREAMLIT_ROOT = REPO_ROOT / "streamlit_app"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(STREAMLIT_ROOT) not in sys.path:
    sys.path.insert(0, str(STREAMLIT_ROOT))

from config import PAGE_TITLE, COLORS  # noqa: E402
from styles import apply_shared_styles  # noqa: E402

OVERSEER_DB = REPO_ROOT / "data" / "overseer.db"

st.set_page_config(
    page_title=f"{PAGE_TITLE} - System Health",
    page_icon="🔍",
    layout="wide"
)
apply_shared_styles()

# ============================================================================
# Database Access
# ============================================================================

def get_db() -> sqlite3.Connection:
    """Get database connection."""
    if not OVERSEER_DB.exists():
        return None
    conn = sqlite3.connect(str(OVERSEER_DB))
    conn.row_factory = sqlite3.Row
    return conn


def db_query(query: str, params: tuple = ()) -> list[dict[str, Any]]:
    """Execute query and return rows as dicts."""
    conn = get_db()
    if conn is None:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception:
        return []
    finally:
        conn.close()


def db_scalar(query: str, params: tuple = ()) -> Any:
    """Execute query and return single scalar value."""
    rows = db_query(query, params)
    if rows and rows[0]:
        return list(rows[0].values())[0]
    return None


# ============================================================================
# Data Loading Functions
# ============================================================================

@st.cache_data(ttl=60)
def load_latest_metrics() -> Optional[dict[str, Any]]:
    """Load most recent health metrics."""
    rows = db_query(
        """
        SELECT * FROM overseer_health_metrics
        ORDER BY timestamp DESC
        LIMIT 1
        """
    )
    return rows[0] if rows else None


@st.cache_data(ttl=60)
def load_metrics_history(hours: int = 24) -> list[dict[str, Any]]:
    """Load metrics history."""
    cutoff = datetime.now() - timedelta(hours=hours)
    return db_query(
        """
        SELECT timestamp, global_coherence, coherence_delta,
               conflict_count, total_beliefs, orphan_belief_count,
               templates_with_evidence, total_templates
        FROM overseer_health_metrics
        WHERE timestamp >= datetime(?)
        ORDER BY timestamp ASC
        """,
        (cutoff.isoformat(),)
    )


@st.cache_data(ttl=60)
def load_violations_unresolved() -> list[dict[str, Any]]:
    """Load unresolved invariant violations."""
    return db_query(
        """
        SELECT violation_id, timestamp, invariant_code, severity,
               description, affected_belief_ids_json, trigger_paper_id
        FROM overseer_invariant_violations
        WHERE resolved = 0
        ORDER BY timestamp DESC
        LIMIT 50
        """
    )


@st.cache_data(ttl=60)
def load_violation_counts() -> dict[str, int]:
    """Count violations by severity."""
    rows = db_query(
        """
        SELECT severity, COUNT(*) as count
        FROM overseer_invariant_violations
        WHERE resolved = 0
        GROUP BY severity
        """
    )
    return {row["severity"]: row["count"] for row in rows}


@st.cache_data(ttl=60)
def load_quarantined_beliefs() -> list[dict[str, Any]]:
    """Load beliefs in quarantine with deadline countdown."""
    return db_query(
        """
        SELECT quarantine_id, belief_id, quarantined_at, reason,
               review_deadline, status, original_credence
        FROM overseer_quarantine
        WHERE status IN ('QUARANTINED', 'REVIEWED')
        ORDER BY review_deadline ASC
        LIMIT 100
        """
    )


@st.cache_data(ttl=60)
def load_recent_events(limit: int = 10) -> list[dict[str, Any]]:
    """Load recent integration events."""
    return db_query(
        """
        SELECT timestamp, trigger_paper_id, global_coherence,
               coherence_delta, conflict_count, total_beliefs, mode
        FROM overseer_health_metrics
        WHERE trigger_paper_id IS NOT NULL
        ORDER BY timestamp DESC
        LIMIT ?
        """,
        (limit,)
    )


# ============================================================================
# Helper Functions
# ============================================================================

def get_system_state() -> str:
    """Determine overall system state."""
    metrics = load_latest_metrics()
    if not metrics:
        return "NO_DATA"

    violations = load_violations_unresolved()
    critical_count = sum(
        1 for v in violations if v["severity"] == "CRITICAL"
    )

    if critical_count > 0:
        return "ERROR"
    elif len(violations) > 5:
        return "INITIALIZING"
    else:
        return "OPERATIONAL"


def state_color(state: str) -> str:
    """Map state to display color."""
    return {
        "OPERATIONAL": COLORS["success"],
        "INITIALIZING": COLORS["warning"],
        "ERROR": COLORS["danger"],
        "NO_DATA": "#B8C5D0",
    }.get(state, "#B8C5D0")


def parse_json_safe(json_str: Optional[str], default=None) -> Any:
    """Safely parse JSON with fallback."""
    if not json_str:
        return default
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return default


def format_timestamp(ts: Optional[str]) -> str:
    """Format ISO timestamp to readable string."""
    if not ts:
        return "—"
    try:
        dt = datetime.fromisoformat(ts)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        return ts


def days_until_deadline(deadline: Optional[str]) -> Optional[int]:
    """Calculate days until review deadline."""
    if not deadline:
        return None
    try:
        dt = datetime.fromisoformat(deadline)
        delta = (dt - datetime.now()).days
        return max(0, delta)
    except (ValueError, TypeError):
        return None


# ============================================================================
# Dashboard Sections
# ============================================================================

def render_health_banner() -> None:
    """Section 1: Health Status Banner"""
    st.markdown("## 🏥 System Health Status")

    state = get_system_state()
    metrics = load_latest_metrics()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            f"""
            <div style="
                background-color: {state_color(state)};
                padding: 20px;
                border-radius: 8px;
                text-align: center;
            ">
                <div style="font-size: 24px; font-weight: bold; color: #ffffff;">
                    {state}
                </div>
                <div style="font-size: 12px; color: rgba(255,255,255,0.8); margin-top: 4px;">
                    System State
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        last_audit = format_timestamp(metrics.get("timestamp")) if metrics else "Never"
        st.metric("Last Audit", last_audit)

    with col3:
        uptime_msg = "No data collected yet" if not metrics else "Monitoring active"
        st.metric("Monitoring", uptime_msg)

    if not metrics:
        st.info("No health metrics recorded yet. Run integration or setup to populate data.")
        return True  # Early return flag

    return False


def render_coherence_panel() -> None:
    """Section 2: Coherence Panel (Cartwright multi-metric)"""
    st.markdown("## 🧠 Coherence Analysis")

    metrics = load_latest_metrics()
    if not metrics:
        st.info("No coherence data available.")
        return

    # Global coherence gauge
    global_coh = metrics.get("global_coherence")
    if global_coh is not None:
        col1, col2 = st.columns(2)
        with col1:
            st.metric(
                "Global Coherence",
                f"{global_coh:.3f}",
                f"Δ {metrics.get('coherence_delta', 0):+.4f}"
            )
        with col2:
            st.metric(
                "Status",
                "Stable" if (metrics.get("coherence_delta", 0) or 0) > -0.05 else "Declining"
            )

    # Per-theory coherence (if available)
    per_theory_json = metrics.get("per_theory_coherence_json")
    if per_theory_json:
        per_theory = parse_json_safe(per_theory_json, {})
        if per_theory:
            st.markdown("### Per-Theory Coherence")
            theory_names = {
                "PP": "Process Philosophy",
                "SN": "Social Norms",
                "DP": "Dispositional Properties",
                "DT": "Default Theory",
                "NM": "Non-Monotonic Logic",
                "IC": "Inductive Coherence",
                "MS": "Multiple Systems",
                "EC": "Epistemic Coherence",
                "CB": "Causal Beliefs",
                "MSI": "Meta-System Integration"
            }

            rows = [
                {
                    "Theory": theory_names.get(code, code),
                    "Code": code,
                    "Coherence": f"{score:.3f}"
                }
                for code, score in sorted(per_theory.items())
            ]
            df = pd.DataFrame(rows)
            st.dataframe(df, use_container_width=True, hide_index=True)

    # Coherence trend (24-hour history)
    history = load_metrics_history(hours=24)
    if history:
        st.markdown("### Coherence Trend (24h)")
        df_hist = pd.DataFrame([
            {
                "Timestamp": row["timestamp"],
                "Global Coherence": row["global_coherence"],
            }
            for row in history
        ])
        st.line_chart(df_hist.set_index("Timestamp"))


def render_integrity_panel() -> None:
    """Section 3: Integrity Panel (violations)"""
    st.markdown("## ⚠️ Integrity & Violations")

    violations = load_violations_unresolved()
    counts = load_violation_counts()

    col1, col2, col3 = st.columns(3)
    with col1:
        critical = counts.get("CRITICAL", 0)
        st.metric(
            "Critical Violations",
            critical,
            delta=None if critical == 0 else "🔴"
        )
    with col2:
        major = counts.get("MAJOR", 0)
        st.metric("Major Violations", major)
    with col3:
        minor = counts.get("MINOR", 0)
        st.metric("Minor Violations", minor)

    if not violations:
        st.success("✓ No unresolved violations detected.")
        return

    st.markdown("### Unresolved Violations")

    rows = []
    for v in violations:
        affected = parse_json_safe(v["affected_belief_ids_json"], [])
        rows.append({
            "Code": v["invariant_code"],
            "Severity": v["severity"],
            "Description": v["description"][:80] + "..." if len(v["description"] or "") > 80 else v["description"],
            "Affected": len(affected) if isinstance(affected, list) else 0,
            "Detected": format_timestamp(v["timestamp"])
        })

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Expandable violation details
    with st.expander("View Full Violation Details"):
        for v in violations[:10]:
            st.markdown(f"**{v['invariant_code']}** ({v['severity']})")
            st.write(v["description"])
            st.caption(format_timestamp(v["timestamp"]))
            st.divider()


def render_completeness_panel() -> None:
    """Section 4: Completeness Panel"""
    st.markdown("## 📊 Completeness Metrics")

    metrics = load_latest_metrics()
    if not metrics:
        st.info("No completeness data available.")
        return

    col1, col2, col3 = st.columns(3)

    with col1:
        templates_with = metrics.get("templates_with_evidence", 0)
        total_templates = metrics.get("total_templates", 0)
        coverage = metrics.get("coverage_ratio", 0)

        st.metric(
            "Template Coverage",
            f"{coverage:.1%}",
            f"{templates_with}/{total_templates}"
        )
        st.progress(
            coverage,
            text=f"{int(coverage * 100)}% covered"
        )

    with col2:
        orphans = metrics.get("orphan_belief_count", 0)
        total = metrics.get("total_beliefs", 0)
        st.metric(
            "Orphan Beliefs",
            orphans,
            f"({orphans}/{total} unattached)"
        )

    with col3:
        provenance_with = metrics.get("beliefs_with_provenance", 0)
        provenance_total = metrics.get("total_beliefs", 0)
        prov_cov = metrics.get("provenance_coverage", 0)
        st.metric(
            "Provenance Coverage",
            f"{prov_cov:.1%}",
            f"{provenance_with}/{provenance_total}"
        )

    # Beliefs breakdown (if per-theory data available)
    history = load_metrics_history(hours=168)  # 1 week
    if history:
        st.markdown("### Belief Accumulation (7d)")
        df_hist = pd.DataFrame([
            {
                "Timestamp": row["timestamp"],
                "Total Beliefs": row["total_beliefs"],
            }
            for row in history
        ])
        st.area_chart(df_hist.set_index("Timestamp"))


def render_cache_bn_health() -> None:
    """Section 5: Cache & Bayesian Network Health"""
    st.markdown("## ⚡ Cache & Network Health")

    metrics = load_latest_metrics()
    if not metrics:
        st.info("No cache/network data available.")
        return

    col1, col2, col3 = st.columns(3)

    with col1:
        total_caches = metrics.get("total_qa_caches", 0)
        stale = metrics.get("stale_qa_caches", 0)
        freshness = metrics.get("cache_freshness", 0)
        st.metric(
            "QA Cache Freshness",
            f"{freshness:.1%}",
            f"{total_caches - stale}/{total_caches} fresh"
        )
        if stale > 0:
            st.warning(f"⚠️ {stale} stale caches detected")

    with col2:
        bn_edges = metrics.get("bn_edge_count", 0)
        sync_violations = metrics.get("bn_web_sync_violations", 0)
        st.metric(
            "BN-Web Sync Status",
            "✓ Synced" if sync_violations == 0 else "⚠️ Violations",
            f"{bn_edges} edges, {sync_violations} violations"
        )

    with col3:
        st.metric(
            "BN Complexity",
            f"{bn_edges} edges",
            "See BN_graphical for topology"
        )


def render_quarantine_queue() -> None:
    """Section 6: Quarantine Queue (O-3 protocol)"""
    st.markdown("## 📦 Quarantine Review Queue (O-3)")

    quarantined = load_quarantined_beliefs()

    if not quarantined:
        st.success("✓ No beliefs in quarantine.")
        return

    st.warning(f"{len(quarantined)} belief(s) awaiting 7-day review")

    # Build review table
    rows = []
    now = datetime.now()

    for q in quarantined:
        deadline = q["review_deadline"]
        days_left = days_until_deadline(deadline)

        if days_left is not None:
            if days_left <= 1:
                urgency = "🔴 URGENT"
            elif days_left <= 3:
                urgency = "🟠 Soon"
            else:
                urgency = "🟡 Pending"
        else:
            urgency = "?"
            days_left = "—"

        rows.append({
            "Belief ID": q["belief_id"][:20] + "..." if len(q["belief_id"]) > 20 else q["belief_id"],
            "Reason": q["reason"][:40] + "..." if len(q["reason"] or "") > 40 else q["reason"],
            "Status": q["status"],
            "Days Left": days_left,
            "Urgency": urgency,
        })

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Expandable details
    with st.expander("Quarantine Details & Actions"):
        for q in quarantined[:20]:
            col1, col2 = st.columns([3, 1])

            with col1:
                st.markdown(f"**{q['belief_id']}**")
                st.write(f"Reason: {q['reason']}")
                st.caption(f"Quarantined: {format_timestamp(q['quarantined_at'])}")
                st.caption(f"Review by: {format_timestamp(q['review_deadline'])}")

            with col2:
                # Info-only buttons (no actual OVERSEER calls)
                st.info("Dashboard: read-only view. Use admin panel for review.")

            st.divider()


def render_recent_activity() -> None:
    """Section 7: Recent Activity Log"""
    st.markdown("## 📝 Recent Integration Events")

    events = load_recent_events(limit=20)

    if not events:
        st.info("No recent integration events recorded.")
        return

    rows = []
    for e in events:
        rows.append({
            "Timestamp": format_timestamp(e["timestamp"]),
            "Paper ID": e["trigger_paper_id"][:20] + "..." if len(e["trigger_paper_id"] or "") > 20 else e["trigger_paper_id"],
            "Coherence": f"{e['global_coherence']:.3f}" if e["global_coherence"] else "—",
            "Δ Coherence": f"{e['coherence_delta']:+.4f}" if e["coherence_delta"] is not None else "—",
            "Conflicts": e["conflict_count"] or "—",
            "Mode": e["mode"],
        })

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Expandable timeline details
    with st.expander("Integration Timeline"):
        for e in events[:10]:
            st.markdown(
                f"**{format_timestamp(e['timestamp'])}** | {e['mode']}"
            )
            if e["trigger_paper_id"]:
                st.write(f"Paper: `{e['trigger_paper_id']}`")
            st.write(
                f"Coherence: {e['global_coherence']:.3f} "
                f"(Δ {e['coherence_delta']:+.4f})"
            )
            if e["conflict_count"]:
                st.write(f"Active conflicts: {e['conflict_count']}")
            st.divider()


# ============================================================================
# Main Page
# ============================================================================

def main() -> None:
    """Main dashboard."""
    st.title("🔍 OVERSEER Health Dashboard")
    st.markdown(
        "Cartwright's multi-metric coherence visualization — "
        "System integrity, completeness, and coherence monitoring"
    )
    st.divider()

    # Check database availability
    if not OVERSEER_DB.exists():
        st.error(
            "OVERSEER database not found. "
            "Expected at: `data/overseer.db`"
        )
        st.info(
            "To populate the database:\n"
            "1. Run paper integration via Admin panel\n"
            "2. Trigger OVERSEER health audit\n"
            "3. Refresh this page"
        )
        return

    # Health banner (may return early)
    if render_health_banner():
        return

    st.divider()
    render_coherence_panel()
    st.divider()
    render_integrity_panel()
    st.divider()
    render_completeness_panel()
    st.divider()
    render_cache_bn_health()
    st.divider()
    render_quarantine_queue()
    st.divider()
    render_recent_activity()

    # Footer
    st.divider()
    st.caption(
        "OVERSEER Health Dashboard — Last updated: "
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
        "Read-only monitoring view | "
        "Use Admin panel for interventions"
    )


if __name__ == "__main__":
    main()
