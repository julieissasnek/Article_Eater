"""
Dashboard Components for Non-Empirical Web Integration (Sprint 6d / Task 6d.4).

Streamlit components for visualizing theory health, cross-type coherence,
prediction tracking, and node type distributions.

Usage:
    from components.dashboard_components import (
        render_theory_health_dashboard,
        render_coherence_dashboard,
        render_prediction_tracker
    )

Reference: Non_Empirical_Web_Integration_Spec_V1.0.md §6.4
"""

import streamlit as st
import streamlit.components.v1 as components
from typing import List, Dict, Any, Optional
import sys
from pathlib import Path
import json

# Add parent paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from src.epistemic.monitors.theory_monitor import (
        TheoryMonitor,
        TheoryHealthStatus,
        TheoryRisk,
        TheoryHealthReport,
        TheoryMonitorSummary,
    )
    from src.epistemic.monitors.cross_type_coherence import (
        CrossTypeCoherenceMonitor,
        CoherenceType,
        CoherenceAnomaly,
        WebCoherenceReport,
    )
    from src.epistemic.entrenchment.prediction_ledger import (
        PredictionLedger,
        ConfirmationType,
    )
    from src.epistemic.node_types import NodeType, NodeTypeFamily
    _imports_available = True
except ImportError as e:
    _imports_available = False
    _import_error = str(e)


# =============================================================================
# COLOR SCHEMES
# =============================================================================

HEALTH_STATUS_COLORS = {
    "well_supported": "#28a745",      # Green
    "moderately_supported": "#17a2b8", # Cyan
    "needs_revision": "#ffc107",       # Yellow
    "problematic": "#dc3545",          # Red
    "untested": "#6c757d",             # Gray
    "suspect": "#fd7e14",              # Orange
}

RISK_COLORS = {
    "unfalsifiable": "#dc3545",
    "overentrenched": "#fd7e14",
    "accumulating_disconfirmations": "#ffc107",
    "single_lab_support": "#17a2b8",
    "stale": "#6c757d",
}

NODE_FAMILY_COLORS = {
    "evidence": "#28a745",      # Green
    "structural": "#007bff",    # Blue
    "interpretive": "#6f42c1",  # Purple
    "gap": "#ffc107",           # Yellow
    "meta": "#17a2b8",          # Cyan
}


# =============================================================================
# THEORY HEALTH COMPONENTS
# =============================================================================

def render_theory_health_dashboard(
    reports: List[TheoryHealthReport],
    summary: Optional[TheoryMonitorSummary] = None
):
    """
    Render theory health dashboard with status overview and details.

    Args:
        reports: List of TheoryHealthReport objects
        summary: Optional TheoryMonitorSummary
    """
    if not _imports_available:
        st.error(f"Import error: {_import_error}")
        return

    st.markdown("## Theory Health Dashboard")
    st.markdown("*Track confirmation/disconfirmation ratios and identify theories needing attention.*")

    if summary:
        _render_health_summary(summary)

    if reports:
        _render_theory_health_table(reports)
        _render_theory_health_details(reports)
    else:
        st.info("No theories assessed yet. Process theoretical papers to populate this dashboard.")


def _render_health_summary(summary: TheoryMonitorSummary):
    """Render health summary metrics."""
    st.markdown("### Overview")

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        st.metric(
            "Total Theories",
            summary.total_theories,
            help="Number of theoretical propositions tracked"
        )

    with col2:
        st.metric(
            "Well Supported",
            summary.well_supported,
            delta=None,
            help="Theories with high confirmation rate"
        )

    with col3:
        st.metric(
            "Moderately Supported",
            summary.moderately_supported,
            help="Theories with mixed evidence"
        )

    with col4:
        st.metric(
            "Needs Revision",
            summary.needs_revision,
            delta=None,
            help="Theories requiring refinement"
        )

    with col5:
        st.metric(
            "Problematic",
            summary.problematic,
            delta=None,
            help="Theories with poor track record"
        )

    with col6:
        st.metric(
            "Untested",
            summary.untested,
            help="Theories without empirical tests"
        )

    # Risk summary
    if summary.theories_with_risks > 0:
        st.warning(f"⚠️ {summary.theories_with_risks} theories have risk flags")


def _render_theory_health_table(reports: List[TheoryHealthReport]):
    """Render sortable table of theory health."""
    st.markdown("### Theory Status Table")

    # Convert to display data
    table_data = []
    for r in reports:
        table_data.append({
            "Theory": r.theory_id[:30] + "..." if len(r.theory_id) > 30 else r.theory_id,
            "Status": r.health_status.value.replace("_", " ").title(),
            "Entrenchment": f"{r.current_entrenchment:.2f}",
            "Confirmations": r.n_confirmations,
            "Disconfirmations": r.n_disconfirmations,
            "Rate": f"{r.confirmation_rate:.0%}" if r.confirmation_rate else "N/A",
            "Risks": len(r.risks),
        })

    # Render as dataframe
    import pandas as pd
    df = pd.DataFrame(table_data)
    st.dataframe(df, use_container_width=True)


def _render_theory_health_details(reports: List[TheoryHealthReport]):
    """Render expandable details for each theory."""
    st.markdown("### Theory Details")

    # Sort by status (problematic first)
    status_order = {
        TheoryHealthStatus.PROBLEMATIC: 0,
        TheoryHealthStatus.NEEDS_REVISION: 1,
        TheoryHealthStatus.SUSPECT: 2,
        TheoryHealthStatus.UNTESTED: 3,
        TheoryHealthStatus.MODERATELY_SUPPORTED: 4,
        TheoryHealthStatus.WELL_SUPPORTED: 5,
    }
    sorted_reports = sorted(reports, key=lambda r: status_order.get(r.health_status, 6))

    for report in sorted_reports:
        color = HEALTH_STATUS_COLORS.get(report.health_status.value, "#6c757d")
        status_badge = f"<span style='color: {color}; font-weight: bold;'>●</span> {report.health_status.value.replace('_', ' ').title()}"

        with st.expander(f"{report.theory_id} — {report.health_status.value.replace('_', ' ').title()}"):
            st.markdown(f"**Status:** {status_badge}", unsafe_allow_html=True)

            if report.theory_text:
                st.markdown(f"**Text:** {report.theory_text}")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Entrenchment", f"{report.current_entrenchment:.3f}")
            with col2:
                st.metric("Confirmations", report.n_confirmations)
            with col3:
                st.metric("Disconfirmations", report.n_disconfirmations)

            if report.risks:
                st.markdown("**Risks:**")
                for risk in report.risks:
                    risk_color = RISK_COLORS.get(risk.value, "#6c757d")
                    st.markdown(f"- <span style='color: {risk_color};'>⚠️ {risk.value.replace('_', ' ').title()}</span>", unsafe_allow_html=True)

            if report.recommendation:
                st.info(f"**Recommendation:** {report.recommendation}")


def render_theory_health_chart(reports: List[TheoryHealthReport]):
    """Render visual chart of theory health distribution."""
    if not reports:
        return

    st.markdown("### Health Distribution")

    # Count by status
    status_counts = {}
    for r in reports:
        status = r.health_status.value.replace("_", " ").title()
        status_counts[status] = status_counts.get(status, 0) + 1

    # Create simple bar using markdown/HTML
    total = sum(status_counts.values())

    html = "<div style='display: flex; width: 100%; height: 30px; border-radius: 5px; overflow: hidden;'>"
    for status, count in status_counts.items():
        pct = (count / total) * 100
        color = HEALTH_STATUS_COLORS.get(status.lower().replace(" ", "_"), "#6c757d")
        html += f"<div style='background: {color}; width: {pct}%; display: flex; align-items: center; justify-content: center;' title='{status}: {count}'>"
        if pct > 10:
            html += f"<span style='color: white; font-size: 12px;'>{count}</span>"
        html += "</div>"
    html += "</div>"

    st.markdown(html, unsafe_allow_html=True)

    # Legend
    legend_html = "<div style='display: flex; gap: 15px; margin-top: 10px;'>"
    for status, count in status_counts.items():
        color = HEALTH_STATUS_COLORS.get(status.lower().replace(" ", "_"), "#6c757d")
        legend_html += f"<span><span style='color: {color};'>●</span> {status} ({count})</span>"
    legend_html += "</div>"
    st.markdown(legend_html, unsafe_allow_html=True)


# =============================================================================
# COHERENCE COMPONENTS
# =============================================================================

def render_coherence_dashboard(report: WebCoherenceReport):
    """
    Render cross-type coherence dashboard.

    Args:
        report: WebCoherenceReport from coherence monitor
    """
    if not _imports_available:
        st.error(f"Import error: {_import_error}")
        return

    st.markdown("## Cross-Type Coherence Dashboard")
    st.markdown("*Track how well theoretical structures cohere with empirical evidence.*")

    _render_coherence_metrics(report)
    _render_node_type_distribution(report)
    _render_coherence_anomalies(report)


def _render_coherence_metrics(report: WebCoherenceReport):
    """Render coherence metrics."""
    st.markdown("### Coherence Metrics")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Nodes",
            report.total_nodes,
            help="Total nodes in the web"
        )

    with col2:
        te_coherence = report.mean_theory_evidence_coherence
        color = "normal" if te_coherence > 0.5 else "inverse"
        st.metric(
            "Theory-Evidence Coherence",
            f"{te_coherence:.2f}",
            delta=None,
            help="Mean coherence between theories and evidence"
        )

    with col3:
        sp_coherence = report.mean_synthesis_primary_coherence
        st.metric(
            "Synthesis-Primary Coherence",
            f"{sp_coherence:.2f}",
            help="Mean coherence between syntheses and primary studies"
        )

    with col4:
        st.metric(
            "Anomalies",
            len(report.anomalies),
            delta=None,
            help="Number of structural anomalies detected"
        )

    # Warning cards
    col1, col2 = st.columns(2)

    with col1:
        if report.ungrounded_theory_count > 0:
            st.warning(f"⚠️ {report.ungrounded_theory_count} ungrounded theories (no empirical connections)")

    with col2:
        if report.uninterpreted_evidence_count > 0:
            st.info(f"ℹ️ {report.uninterpreted_evidence_count} uninterpreted evidence nodes (no theoretical links)")


def _render_node_type_distribution(report: WebCoherenceReport):
    """Render node type distribution chart."""
    st.markdown("### Node Type Distribution")

    if not report.nodes_by_type:
        st.info("No nodes in the web")
        return

    # Create horizontal bar chart using HTML
    total = sum(report.nodes_by_type.values())
    max_count = max(report.nodes_by_type.values())

    html = "<div style='margin: 10px 0;'>"
    for node_type, count in sorted(report.nodes_by_type.items(), key=lambda x: -x[1]):
        # Determine family color
        try:
            nt = NodeType(node_type)
            from src.epistemic.node_types import get_node_type_family
            family = get_node_type_family(nt).value
            color = NODE_FAMILY_COLORS.get(family, "#6c757d")
        except (ValueError, ImportError):
            color = "#6c757d"

        pct = (count / max_count) * 100
        label = node_type.replace("_", " ").title()

        html += f"""
        <div style='display: flex; align-items: center; margin: 5px 0;'>
            <div style='width: 150px; font-size: 12px;'>{label}</div>
            <div style='flex: 1; background: #e9ecef; border-radius: 3px; height: 20px;'>
                <div style='background: {color}; width: {pct}%; height: 100%; border-radius: 3px; display: flex; align-items: center; justify-content: flex-end; padding-right: 5px;'>
                    <span style='color: white; font-size: 11px;'>{count}</span>
                </div>
            </div>
        </div>
        """
    html += "</div>"

    st.markdown(html, unsafe_allow_html=True)


def _render_coherence_anomalies(report: WebCoherenceReport):
    """Render anomaly cards."""
    if not report.anomalies:
        st.success("✓ No structural anomalies detected")
        return

    st.markdown("### Structural Anomalies")

    # Group by type
    by_type: Dict[str, List] = {}
    for a in report.anomalies:
        t = a.anomaly_type.value
        if t not in by_type:
            by_type[t] = []
        by_type[t].append(a)

    for anomaly_type, anomalies in by_type.items():
        with st.expander(f"{anomaly_type.replace('_', ' ').title()} ({len(anomalies)})"):
            for a in anomalies[:10]:  # Limit display
                severity_color = "#dc3545" if a.severity > 0.6 else "#ffc107" if a.severity > 0.3 else "#17a2b8"
                st.markdown(f"""
                <div style='border-left: 3px solid {severity_color}; padding: 5px 10px; margin: 5px 0; background: #f8f9fa;'>
                    <strong>{a.node_id}</strong> ({a.node_type.value})<br/>
                    <small>{a.description}</small><br/>
                    <em style='color: #6c757d;'>→ {a.suggested_action}</em>
                </div>
                """, unsafe_allow_html=True)

            if len(anomalies) > 10:
                st.caption(f"... and {len(anomalies) - 10} more")


# =============================================================================
# PREDICTION TRACKER COMPONENTS
# =============================================================================

def render_prediction_tracker(
    ledger: PredictionLedger,
    show_controls: bool = True
):
    """
    Render prediction tracking dashboard.

    Args:
        ledger: PredictionLedger instance
        show_controls: Whether to show add/confirm controls
    """
    if not _imports_available:
        st.error(f"Import error: {_import_error}")
        return

    st.markdown("## Prediction Tracker")
    st.markdown("*Track hypothesis confirmations and disconfirmations.*")

    entries = ledger.get_all_entries()

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)

    total = len(entries)
    confirmed = sum(1 for e in entries if e.get_status() == "confirmed")
    disconfirmed = sum(1 for e in entries if e.get_status() == "disconfirmed")
    untested = sum(1 for e in entries if e.get_status() == "untested")

    with col1:
        st.metric("Total Hypotheses", total)
    with col2:
        st.metric("Confirmed", confirmed, help="Hypotheses with confirmations only")
    with col3:
        st.metric("Disconfirmed", disconfirmed, help="Hypotheses with more disconfirmations")
    with col4:
        st.metric("Untested", untested, help="Hypotheses awaiting empirical test")

    # Filter controls
    status_filter = st.selectbox(
        "Filter by status",
        ["all", "untested", "confirmed", "disconfirmed", "mixed"],
        format_func=lambda x: x.title()
    )

    # Filter entries
    if status_filter != "all":
        entries = [e for e in entries if e.get_status() == status_filter]

    # Render entries
    st.markdown(f"### Predictions ({len(entries)})")

    for entry in entries:
        status = entry.get_status()
        status_colors = {
            "confirmed": "#28a745",
            "disconfirmed": "#dc3545",
            "mixed": "#ffc107",
            "untested": "#6c757d"
        }
        color = status_colors.get(status, "#6c757d")

        with st.expander(f"{entry.hypothesis_id} — {status.title()}"):
            st.markdown(f"**Text:** {entry.hypothesis_text}")
            st.markdown(f"**Derived from:** {entry.derived_from}")
            st.markdown(f"**Status:** <span style='color: {color}; font-weight: bold;'>{status.title()}</span>", unsafe_allow_html=True)

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Entrenchment", f"{entry.current_entrenchment:.3f}")
            with col2:
                st.metric("Confirmations", len(entry.confirmed_by))
            with col3:
                st.metric("Disconfirmations", len(entry.disconfirmed_by))

            if entry.confirmed_by:
                st.markdown("**Confirmed by:**")
                for study_id, conf_type in entry.confirmed_by:
                    st.markdown(f"- {study_id} ({conf_type})")

            if entry.disconfirmed_by:
                st.markdown("**Disconfirmed by:**")
                for study_id in entry.disconfirmed_by:
                    st.markdown(f"- {study_id}")


def render_theory_track_record(
    ledger: PredictionLedger,
    theory_id: str
):
    """
    Render track record for a specific theory.

    Args:
        ledger: PredictionLedger instance
        theory_id: ID of the theory to display
    """
    record = ledger.compute_theory_track_record(theory_id)

    st.markdown(f"### Track Record: {theory_id}")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Hypotheses", record["hypothesis_count"])
    with col2:
        st.metric("Confirmations", record["total_confirmations"])
    with col3:
        st.metric("Disconfirmations", record["total_disconfirmations"])
    with col4:
        rate = record["success_rate"]
        st.metric("Success Rate", f"{rate:.0%}" if rate else "N/A")

    # Visual success bar
    total_tests = record["total_confirmations"] + record["total_disconfirmations"]
    if total_tests > 0:
        confirm_pct = (record["total_confirmations"] / total_tests) * 100
        disconfirm_pct = 100 - confirm_pct

        html = f"""
        <div style='display: flex; height: 20px; border-radius: 3px; overflow: hidden; margin: 10px 0;'>
            <div style='background: #28a745; width: {confirm_pct}%;' title='Confirmed'></div>
            <div style='background: #dc3545; width: {disconfirm_pct}%;' title='Disconfirmed'></div>
        </div>
        <div style='display: flex; justify-content: space-between; font-size: 12px;'>
            <span style='color: #28a745;'>Confirmed: {record["total_confirmations"]}</span>
            <span style='color: #dc3545;'>Disconfirmed: {record["total_disconfirmations"]}</span>
        </div>
        """
        st.markdown(html, unsafe_allow_html=True)


# =============================================================================
# CONTROLS / SIDEBAR COMPONENTS
# =============================================================================

def render_theory_health_controls() -> Dict[str, Any]:
    """
    Render theory health control widgets in sidebar.

    Returns:
        Dictionary of control values.
    """
    st.sidebar.markdown("### Theory Health Controls")

    min_entrenchment = st.sidebar.slider(
        "Min Entrenchment",
        min_value=0.0,
        max_value=1.0,
        value=0.0,
        step=0.05,
        help="Filter theories by minimum entrenchment"
    )

    show_untested = st.sidebar.checkbox(
        "Include Untested",
        value=True,
        help="Show theories without empirical tests"
    )

    sort_by = st.sidebar.selectbox(
        "Sort By",
        ["status", "entrenchment", "confirmation_rate", "risks"],
        format_func=lambda x: x.replace("_", " ").title()
    )

    return {
        "min_entrenchment": min_entrenchment,
        "show_untested": show_untested,
        "sort_by": sort_by
    }


def render_coherence_controls() -> Dict[str, Any]:
    """
    Render coherence control widgets in sidebar.

    Returns:
        Dictionary of control values.
    """
    st.sidebar.markdown("### Coherence Controls")

    family_filter = st.sidebar.multiselect(
        "Node Families",
        ["evidence", "structural", "interpretive", "gap", "meta"],
        default=["evidence", "structural"],
        help="Filter by node type family"
    )

    show_anomalies = st.sidebar.checkbox(
        "Show Anomalies Only",
        value=False,
        help="Only show nodes with structural anomalies"
    )

    min_coherence = st.sidebar.slider(
        "Min Coherence Score",
        min_value=0.0,
        max_value=1.0,
        value=0.0,
        step=0.1,
        help="Filter by minimum coherence score"
    )

    return {
        "family_filter": family_filter,
        "show_anomalies": show_anomalies,
        "min_coherence": min_coherence
    }


# =============================================================================
# QUICK ACCESS FUNCTIONS
# =============================================================================

def quick_theory_dashboard():
    """
    Quick theory health dashboard using default data.

    Useful for embedding in main app.
    """
    try:
        from src.epistemic.monitors.theory_monitor import TheoryMonitor
        from src.epistemic.entrenchment.prediction_ledger import PredictionLedger

        ledger = PredictionLedger()
        monitor = TheoryMonitor(ledger)

        # Would normally load from web
        reports = list(monitor._theory_cache.values())
        summary = monitor.get_summary() if reports else None

        render_theory_health_dashboard(reports, summary)

    except Exception as e:
        st.error(f"Error loading theory dashboard: {e}")


def quick_coherence_dashboard():
    """
    Quick coherence dashboard using default data.

    Useful for embedding in main app.
    """
    try:
        from src.epistemic.monitors.cross_type_coherence import CrossTypeCoherenceMonitor

        monitor = CrossTypeCoherenceMonitor()
        report = monitor.generate_report()

        render_coherence_dashboard(report)

    except Exception as e:
        st.error(f"Error loading coherence dashboard: {e}")
