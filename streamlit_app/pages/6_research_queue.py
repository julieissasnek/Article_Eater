"""Article Eater V23 — Research Queue Dashboard.

Sprint 9 I9.6: visualize queue state, assign targets, and track progress.
"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

# Add parent directories for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config import PAGE_TITLE
from styles import apply_shared_styles
from src.queue import CollectorProfile, CollectorType, OpportunityStatus, ResearchQueueService, TargetStatus

st.set_page_config(
    page_title=f"{PAGE_TITLE} — Research Queue",
    page_icon="🧭",
    layout="wide",
)


def _get_service() -> ResearchQueueService:
    return ResearchQueueService()


def _render_metrics(snapshot: dict):
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    by_status = snapshot["by_status"]
    with c1:
        st.metric("Open", by_status.get("open", 0))
    with c2:
        st.metric("Searching", by_status.get("searching", 0))
    with c3:
        st.metric("Found", by_status.get("found", 0))
    with c4:
        st.metric("Closed", by_status.get("closed", 0))
    with c5:
        st.metric("Collectors", snapshot.get("n_collectors", 0))
    with c6:
        st.metric("Opportunities", snapshot.get("n_opportunities", 0))


def _targets_rows(service: ResearchQueueService) -> list[dict]:
    rows = []
    for t in service.list_targets():
        rows.append(
            {
                "target_id": t.target_id,
                "priority": t.priority.value,
                "status": t.status.value,
                "assigned_to": t.assigned_to or "",
                "voi": round(t.voi_score, 3),
                "gap_type": t.gap_type.value,
                "description": t.gap_description,
                "updated_at": t.updated_at.isoformat(),
            }
        )
    return rows


def _render_targets_tab(service: ResearchQueueService):
    st.subheader("Targets")
    rows = _targets_rows(service)
    if not rows:
        st.info("No queue targets yet. Click 'Refresh Queue' to generate targets.")
        return

    col1, col2 = st.columns(2)
    with col1:
        status_filter = st.multiselect(
            "Filter by status",
            options=sorted({r["status"] for r in rows}),
            default=sorted({r["status"] for r in rows}),
        )
    with col2:
        priority_filter = st.multiselect(
            "Filter by priority",
            options=["high", "medium", "low"],
            default=["high", "medium", "low"],
        )

    filtered = [r for r in rows if r["status"] in status_filter and r["priority"] in priority_filter]
    st.dataframe(filtered, use_container_width=True, hide_index=True)

    st.markdown("#### Manual Actions")
    collectors = [c.collector_id for c in service.list_collectors()]
    if not collectors:
        st.caption("Register a collector first in the Collectors tab.")

    col_claim, col_status = st.columns(2)

    with col_claim:
        with st.form("claim_target_form", clear_on_submit=False):
            st.markdown("**Claim Target**")
            selected_collector = st.selectbox(
                "Collector",
                options=collectors or [""],
                index=0,
                disabled=not collectors,
            )
            selected_target = st.selectbox(
                "Target (optional, blank = next best)",
                options=[""] + [r["target_id"] for r in filtered],
                index=0,
            )
            submitted = st.form_submit_button("Claim")
            if submitted and selected_collector:
                res = service.claim_target(selected_collector, selected_target or None)
                if res.success:
                    st.success(f"Claimed {res.target.target_id}")
                else:
                    st.warning(res.message)

    with col_status:
        with st.form("set_status_form", clear_on_submit=False):
            st.markdown("**Set Status**")
            tgt = st.selectbox("Target", options=[r["target_id"] for r in filtered])
            new_status = st.selectbox(
                "New status",
                options=[s.value for s in TargetStatus],
                index=0,
            )
            submitted = st.form_submit_button("Update Status")
            if submitted:
                updated = service.set_target_status(tgt, TargetStatus(new_status))
                if updated:
                    st.success(f"Updated {tgt} -> {new_status}")
                else:
                    st.error("Target not found")


def _render_collectors_tab(service: ResearchQueueService):
    st.subheader("Collectors")

    collectors = service.list_collectors()
    if collectors:
        rows = []
        for c in collectors:
            rows.append(
                {
                    "collector_id": c.collector_id,
                    "type": c.collector_type.value,
                    "name": c.name,
                    "databases": ", ".join(c.can_access_databases),
                    "max_concurrent": c.max_concurrent_targets,
                    "turnaround_h": c.typical_turnaround_hours,
                }
            )
        st.dataframe(rows, use_container_width=True, hide_index=True)
    else:
        st.caption("No collectors registered yet.")

    st.markdown("#### Register Collector")
    with st.form("register_collector_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            collector_id = st.text_input("Collector ID", value="")
            name = st.text_input("Name", value="")
            ctype = st.selectbox("Type", options=[t.value for t in CollectorType])
        with col2:
            dbs = st.text_input("Databases (comma-separated)", value="semantic_scholar,pubmed,zotero")
            max_conc = st.number_input("Max concurrent targets", min_value=1, max_value=20, value=1)
            turnaround = st.number_input("Turnaround hours", min_value=1.0, max_value=168.0, value=24.0)

        submitted = st.form_submit_button("Register")
        if submitted:
            if not collector_id.strip():
                st.warning("Collector ID is required.")
            else:
                profile = CollectorProfile(
                    collector_id=collector_id.strip(),
                    collector_type=CollectorType(ctype),
                    name=name.strip() or collector_id.strip(),
                    can_access_databases=[d.strip() for d in dbs.split(",") if d.strip()],
                    max_concurrent_targets=int(max_conc),
                    typical_turnaround_hours=float(turnaround),
                )
                service.register_collector(profile)
                st.success(f"Registered collector: {profile.collector_id}")


def _render_opportunities_tab(service: ResearchQueueService):
    st.subheader("Research Opportunities")
    opportunities = service.list_research_opportunities()
    if not opportunities:
        st.caption("No research opportunities recorded yet.")
        return

    rows = []
    for o in opportunities:
        rows.append(
            {
                "opportunity_id": o.opportunity_id,
                "source_target_id": o.source_target_id,
                "status": o.status.value,
                "voi": round(o.voi_score, 3),
                "suggested_design": o.suggested_design,
                "suggested_setting": o.suggested_setting,
                "created_by": o.created_by,
            }
        )
    st.dataframe(rows, use_container_width=True, hide_index=True)

    with st.form("update_opportunity_form", clear_on_submit=False):
        oid = st.selectbox("Opportunity", options=[o.opportunity_id for o in opportunities])
        status = st.selectbox("Status", options=[s.value for s in OpportunityStatus])
        contact = st.text_input("Researcher contact (optional)", value="")
        doi = st.text_input("Publication DOI (optional)", value="")
        submitted = st.form_submit_button("Update Opportunity")
        if submitted:
            updated = service.update_research_opportunity(
                oid,
                status=OpportunityStatus(status),
                researcher_contact=(contact or None),
                publication_doi=(doi or None),
            )
            if updated:
                st.success(f"Updated opportunity {oid}")
            else:
                st.error("Opportunity not found")


def _render_automation_tab(service: ResearchQueueService):
    st.subheader("Automation")

    with st.expander("Run Automated Searcher", expanded=True):
        c1, c2, c3, c4 = st.columns(4)
        max_targets = c1.number_input("Max targets/run", min_value=1, max_value=20, value=3)
        max_queries = c2.number_input("Queries/target", min_value=1, max_value=10, value=3)
        max_results = c3.number_input("Results/query", min_value=1, max_value=50, value=10)
        min_rel = c4.slider("Min relevance", min_value=0.0, max_value=1.0, value=0.25, step=0.05)

        if st.button("Run Automated Searcher", type="primary"):
            runs = service.run_automated_searcher(
                max_targets_per_run=int(max_targets),
                max_queries_per_target=int(max_queries),
                max_results_per_query=int(max_results),
                min_relevance=float(min_rel),
            )
            if runs:
                st.success(f"Processed {len(runs)} target(s)")
                st.dataframe(runs, use_container_width=True, hide_index=True)
            else:
                st.info("No targets processed.")

    with st.expander("Run Zotero Sync", expanded=False):
        bib_path = st.text_input(
            "BibTeX path",
            value=str(Path.home() / "Downloads" / "zotero_export.bib"),
        )
        min_score = st.slider("Min match score", min_value=0.0, max_value=1.0, value=0.18, step=0.01)
        if st.button("Run Zotero Sync"):
            matches = service.sync_zotero_to_queue(bibtex_path=bib_path, min_score=float(min_score))
            st.success(f"Matched {len(matches)} article(s)")


def main():
    apply_shared_styles()
    st.title("Research Queue")
    st.caption("Gap-driven target queue, collector assignment, and automated discovery")

    service = _get_service()

    col_a, col_b = st.columns([1, 4])
    with col_a:
        if st.button("Refresh Queue", type="primary"):
            service.refresh_queue()
            st.success("Queue refreshed")
    with col_b:
        snapshot = service.get_dashboard_snapshot()
        st.caption(f"Queue: {snapshot['queue_id']} | Updated: {snapshot['updated_at']}")

    _render_metrics(snapshot)

    tab_targets, tab_collectors, tab_opps, tab_auto = st.tabs(
        ["Targets", "Collectors", "Opportunities", "Automation"]
    )
    with tab_targets:
        _render_targets_tab(service)
    with tab_collectors:
        _render_collectors_tab(service)
    with tab_opps:
        _render_opportunities_tab(service)
    with tab_auto:
        _render_automation_tab(service)


if __name__ == "__main__":
    main()
