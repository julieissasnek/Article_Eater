"""Admin dashboard (3.0.5-A/B/C): overview, belief inspector, constraint viewer."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
import sys
from typing import Any

import streamlit as st


REPO_ROOT = Path(__file__).resolve().parents[2]
STREAMLIT_ROOT = REPO_ROOT / "streamlit_app"

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(STREAMLIT_ROOT) not in sys.path:
    sys.path.insert(0, str(STREAMLIT_ROOT))

from config import PAGE_TITLE  # noqa: E402
from styles import apply_shared_styles  # noqa: E402
from src.services.web_accumulator import WebAccumulator  # noqa: E402
from src.services.web_of_belief import Belief, WebOfBelief, create_neuroarchitecture_web  # noqa: E402


st.set_page_config(page_title=f"{PAGE_TITLE} - Admin", page_icon="A", layout="wide")
apply_shared_styles()


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def _candidate_db_paths() -> list[Path]:
    data_dir = REPO_ROOT / "data"
    return [
        data_dir / "web_persistence_v2.db",
        data_dir / "web_persistence.db",
    ]


@st.cache_resource(show_spinner=False)
def load_web() -> tuple[WebOfBelief, str]:
    """Load master web from persistence, fallback to demo seed web."""
    for db_path in _candidate_db_paths():
        if not db_path.exists():
            continue
        try:
            accumulator = WebAccumulator(db_path=db_path)
            web, _ = accumulator.get_master_web()
            if web is not None and web.beliefs:
                return web, str(db_path)
        except Exception:
            continue

    return create_neuroarchitecture_web(), "demo_seed_web"


def belief_rows(web: WebOfBelief) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for belief_id, belief in web.beliefs.items():
        credence = _safe_float(getattr(getattr(belief, "credence", None), "value", 0.5), 0.5)
        uncertainty = _safe_float(getattr(getattr(belief, "credence", None), "uncertainty", 0.5), 0.5)
        rows.append(
            {
                "belief_id": belief_id,
                "content": belief.content,
                "status": getattr(belief.status, "value", str(belief.status)),
                "level": getattr(belief.level, "value", str(belief.level)),
                "credence": credence,
                "uncertainty": uncertainty,
                "entrenchment": _safe_float(web.get_entrenchment(belief_id), 0.0),
                "severity": _safe_float(belief.compute_severity() if hasattr(belief, "compute_severity") else 0.0),
                "source_lab": getattr(belief, "source_lab", None),
                "source_institution": getattr(belief, "source_institution", None),
                "study_method": getattr(belief, "study_method", None),
                "scope_population": getattr(belief, "scope_population", None),
                "scope_context": getattr(belief, "scope_context", None),
                "scope_temporal": getattr(belief, "scope_temporal", None),
            }
        )
    rows.sort(key=lambda r: (r["credence"], r["entrenchment"]), reverse=True)
    return rows


def constraint_rows(web: WebOfBelief) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for constraint in web.constraints.values():
        rows.append(
            {
                "constraint_id": constraint.constraint_id,
                "source_id": constraint.source_id,
                "target_id": constraint.target_id,
                "type": getattr(constraint.constraint_type, "value", str(constraint.constraint_type)),
                "strength": _safe_float(getattr(constraint, "strength", 0.5), 0.5),
                "bidirectional": bool(getattr(constraint, "bidirectional", False)),
            }
        )
    rows.sort(key=lambda r: r["strength"], reverse=True)
    return rows


def _edge_color(edge_type: str) -> str:
    lowered = edge_type.lower()
    if any(token in lowered for token in ("contradict", "tension", "disconfirm", "challenge")):
        return "#c0392b"
    return "#1e8449"


def _label_for_belief(web: WebOfBelief, belief_id: str) -> str:
    belief: Belief | None = web.beliefs.get(belief_id)
    if not belief:
        return belief_id
    text = belief.content.strip().replace('"', "'")
    if len(text) > 48:
        text = f"{text[:45]}..."
    return f"{belief_id}: {text}"


def render_overview(web: WebOfBelief, source: str) -> None:
    rows = belief_rows(web)
    edges = constraint_rows(web)
    statuses = Counter(row["status"] for row in rows)
    levels = Counter(row["level"] for row in rows)

    st.subheader("System Overview")
    st.caption(f"Loaded from: {source}")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Beliefs", len(rows))
    c2.metric("Constraints", len(edges))
    c3.metric("Coherence", f"{_safe_float(web.coherence_score(), 0.0):.3f}")
    c4.metric("Stubs", statuses.get("stub", 0))

    st.write("Belief status counts")
    st.dataframe(
        [{"status": key, "count": value} for key, value in sorted(statuses.items())],
        use_container_width=True,
        hide_index=True,
    )

    st.write("Belief level counts")
    st.dataframe(
        [{"level": key, "count": value} for key, value in sorted(levels.items())],
        use_container_width=True,
        hide_index=True,
    )

    if hasattr(web, "compute_independence_score"):
        independence = web.compute_independence_score()
        st.write("Evidence independence")
        st.json(independence)


def render_belief_inspector(web: WebOfBelief) -> None:
    st.subheader("Belief Inspector")
    rows = belief_rows(web)
    if not rows:
        st.info("No beliefs available.")
        return

    all_statuses = sorted({row["status"] for row in rows})
    all_levels = sorted({row["level"] for row in rows})

    c1, c2, c3, c4 = st.columns(4)
    search = c1.text_input("Search content", "")
    status_filter = c2.multiselect("Status", all_statuses, default=all_statuses)
    level_filter = c3.multiselect("Level", all_levels, default=all_levels)
    min_credence = c4.slider("Min credence", 0.0, 1.0, 0.0, 0.01)

    filtered = [
        row for row in rows
        if row["status"] in status_filter
        and row["level"] in level_filter
        and row["credence"] >= min_credence
        and (not search or search.lower() in row["content"].lower())
    ]

    st.caption(f"Showing {len(filtered)} beliefs")
    st.dataframe(filtered, use_container_width=True, hide_index=True)

    if not filtered:
        return

    selected_id = st.selectbox("Inspect belief", options=[row["belief_id"] for row in filtered])
    belief = web.beliefs.get(selected_id)
    if belief is None:
        return

    st.write("Belief detail")
    st.json(belief.to_dict(computed_entrenchment=web.get_entrenchment(selected_id)))
    st.write("Entrenchment components")
    st.json(web.get_entrenchment_components(selected_id))


def render_constraint_viewer(web: WebOfBelief) -> None:
    st.subheader("Constraint Viewer")
    rows = constraint_rows(web)
    if not rows:
        st.info("No constraints available.")
        return

    all_types = sorted({row["type"] for row in rows})
    c1, c2, c3 = st.columns(3)
    min_strength = c1.slider("Min strength", 0.0, 1.0, 0.2, 0.01)
    max_edges = c2.slider("Max edges in graph", 10, 250, 75, 5)
    type_filter = c3.multiselect("Constraint type", all_types, default=all_types)

    filtered = [
        row for row in rows
        if row["strength"] >= min_strength and row["type"] in type_filter
    ]

    st.caption(f"Showing {len(filtered)} constraints")

    graph_edges = filtered[:max_edges]
    dot_lines = [
        "digraph BeliefNet {",
        "rankdir=LR;",
        'node [shape=box, style="rounded,filled", fillcolor="#f8f9f9", color="#7f8c8d"];',
    ]
    for edge in graph_edges:
        src_label = _label_for_belief(web, edge["source_id"])
        tgt_label = _label_for_belief(web, edge["target_id"])
        color = _edge_color(edge["type"])
        label = f"{edge['type']} ({edge['strength']:.2f})"
        dot_lines.append(
            f'"{src_label}" -> "{tgt_label}" [color="{color}", penwidth=1.7, label="{label}"];'
        )
    dot_lines.append("}")

    st.graphviz_chart("\n".join(dot_lines), use_container_width=True)
    st.dataframe(filtered[:500], use_container_width=True, hide_index=True)


def main() -> None:
    st.title("Admin Dashboard")
    web, source = load_web()
    overview_tab, beliefs_tab, constraints_tab = st.tabs(
        ["Overview", "Belief Inspector", "Constraint Viewer"]
    )
    with overview_tab:
        render_overview(web, source)
    with beliefs_tab:
        render_belief_inspector(web)
    with constraints_tab:
        render_constraint_viewer(web)


main()
