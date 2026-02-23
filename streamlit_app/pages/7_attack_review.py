"""ATK-4: Review UI for detected argument-attack patterns in extracted claims."""

from __future__ import annotations

import json
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
from src.extraction.claim_extractor import detect_attack_patterns_from_text  # noqa: E402


st.set_page_config(page_title=f"{PAGE_TITLE} - Attack Review", page_icon="R", layout="wide")
apply_shared_styles()


def _claim_files() -> list[Path]:
    production = REPO_ROOT / "data" / "production"
    return [
        production / "structured_claims_codex_semantic.json",
        production / "structured_claims_codex_semantic.limit50.postpatch.json",
        production / "structured_claims.json",
        production / "structured_claims_codex.json",
        production / "batch_15_extraction_results.jsonl",
    ]


def _load_claims_from_json(path: Path) -> list[dict[str, Any]]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(obj, list):
        return [x for x in obj if isinstance(x, dict)]
    if isinstance(obj, dict):
        for key in ("claims", "structured_claims", "items", "results"):
            value = obj.get(key)
            if isinstance(value, list):
                return [x for x in value if isinstance(x, dict)]
    return []


def _load_claims_from_jsonl(path: Path) -> list[dict[str, Any]]:
    claims: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if not stripped:
                continue
            row = json.loads(stripped)
            if isinstance(row, dict):
                claims.append(row)
    return claims


@st.cache_data(show_spinner=False)
def load_claims() -> tuple[list[dict[str, Any]], str]:
    for candidate in _claim_files():
        if not candidate.exists():
            continue
        try:
            if candidate.suffix == ".jsonl":
                claims = _load_claims_from_jsonl(candidate)
            else:
                claims = _load_claims_from_json(candidate)
            if claims:
                return claims, str(candidate)
        except Exception:
            continue
    return [], "none"


def _attack_matches(claim: dict[str, Any]) -> list[dict[str, Any]]:
    existing = claim.get("attack_patterns")
    if isinstance(existing, list):
        filtered = [x for x in existing if isinstance(x, dict) and x.get("attack_type")]
        if filtered:
            return filtered

    text = " ".join(
        str(claim.get(key) or "")
        for key in ("source_quote", "context", "iv_raw", "dv_raw", "iv", "dv")
    ).strip()
    return detect_attack_patterns_from_text(text)


def build_rows(claims: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for claim in claims:
        matches = _attack_matches(claim)
        if not matches:
            continue
        for match in matches:
            rows.append(
                {
                    "claim_id": claim.get("claim_id"),
                    "paper_id": claim.get("paper_id"),
                    "attack_type": match.get("attack_type"),
                    "confidence": float(match.get("confidence", 0.0)),
                    "matched_terms": ", ".join(match.get("matched_terms", [])),
                    "source_quote": str(claim.get("source_quote") or "")[:400],
                }
            )
    rows.sort(key=lambda r: r["confidence"], reverse=True)
    return rows


def main() -> None:
    st.title("Argument Attack Review")
    claims, source = load_claims()
    st.caption(f"Claims source: {source}")

    if not claims:
        st.warning("No claim file found in data/production with extractable claims.")
        return

    rows = build_rows(claims)
    total_claims = len(claims)
    attacked_claims = len({r["claim_id"] for r in rows})

    c1, c2, c3 = st.columns(3)
    c1.metric("Claims scanned", total_claims)
    c2.metric("Claims with attacks", attacked_claims)
    c3.metric("Total attack cues", len(rows))

    if not rows:
        st.info("No attack patterns detected in current claims.")
        return

    attack_types = sorted({r["attack_type"] for r in rows})
    f1, f2, f3 = st.columns(3)
    selected_types = f1.multiselect("Attack type", attack_types, default=attack_types)
    min_conf = f2.slider("Min confidence", 0.0, 1.0, 0.4, 0.01)
    text_query = f3.text_input("Text search", "")

    filtered = [
        r for r in rows
        if r["attack_type"] in selected_types
        and r["confidence"] >= min_conf
        and (
            not text_query
            or text_query.lower() in r["source_quote"].lower()
            or text_query.lower() in str(r["paper_id"]).lower()
        )
    ]

    st.caption(f"Showing {len(filtered)} attack records")
    if not filtered:
        st.info("No attack records match the current filters.")
        return

    counts: dict[str, int] = {}
    for row in filtered:
        counts[row["attack_type"]] = counts.get(row["attack_type"], 0) + 1
    st.dataframe(
        [{"attack_type": key, "count": value} for key, value in sorted(counts.items())],
        use_container_width=True,
        hide_index=True,
    )

    st.dataframe(filtered, use_container_width=True, hide_index=True)

    selected_claim_ids = sorted({r["claim_id"] for r in filtered})
    selected_claim = st.selectbox("Inspect claim", options=selected_claim_ids)
    selected_rows = [r for r in filtered if r["claim_id"] == selected_claim]
    for row in selected_rows:
        st.write(f"Attack: {row['attack_type']} (confidence={row['confidence']:.2f})")
        st.write(f"Matched terms: {row['matched_terms']}")
        st.code(row["source_quote"] or "", language="text")


main()
