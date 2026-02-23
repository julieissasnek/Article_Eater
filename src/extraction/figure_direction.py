"""Figure-level direction inference from PDF vector graphics.

Purpose:
- Provide a precision-first fallback when textual direction is unknown.
- Infer trend direction from plotted line segments in figure pages.

Notes:
- PDF coordinates have Y increasing downward, so visual slope direction is
  the inverse of dy/dx sign.
- This module intentionally returns only increase/decrease/unknown (no no_effect).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import fitz  # type: ignore
except Exception:  # pragma: no cover - optional dependency at runtime
    fitz = None  # type: ignore


_TOKEN_RE = re.compile(r"[a-z0-9]+")
_FIG_LABEL_RE = re.compile(r"\b(fig(?:ure)?\.?)\s*\d+", re.IGNORECASE)
_COVARIATE_IV_TOKENS = {"age", "gender", "sex", "income", "education", "race", "ethnicity"}


@dataclass
class FigureDirectionSignal:
    direction: str
    confidence: float
    source_page: int | None
    evidence_quote: str
    diagnostics: dict[str, Any]


def _norm(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _tokens(text: str) -> set[str]:
    return {tok for tok in _TOKEN_RE.findall(text.lower()) if len(tok) >= 3}


def _claim_token_buckets(claim: dict[str, Any]) -> tuple[set[str], set[str], set[str]]:
    iv_blob = " ".join([_norm(claim.get("iv")), _norm(claim.get("iv_raw"))])
    dv_blob = " ".join([_norm(claim.get("dv")), _norm(claim.get("dv_raw"))])
    iv_tokens = _tokens(iv_blob)
    dv_tokens = _tokens(dv_blob)
    return iv_tokens, dv_tokens, iv_tokens.union(dv_tokens)


def _page_relevance(page_text: str, iv_toks: set[str], dv_toks: set[str]) -> tuple[float, int, int]:
    ptoks = _tokens(page_text)
    iv_overlap = len(ptoks.intersection(iv_toks))
    dv_overlap = len(ptoks.intersection(dv_toks))
    has_fig = 1.0 if _FIG_LABEL_RE.search(page_text) else 0.0
    score = has_fig + (iv_overlap * 0.5) + (dv_overlap * 0.5)
    return score, iv_overlap, dv_overlap


def _line_slope_vote(drawings: list[dict[str, Any]]) -> tuple[int, int, int, int]:
    """Return (diag_inc, diag_dec, horiz, vert) from line segments."""
    diag_inc = 0
    diag_dec = 0
    horiz = 0
    vert = 0

    for d in drawings:
        width = d.get("width")
        # Ignore fill-only / glyph-outline style paths.
        if width is None:
            continue

        for item in d.get("items", []):
            cmd = item[0] if item else None
            if cmd != "l":
                continue
            if len(item) < 3:
                continue
            p1, p2 = item[1], item[2]
            dx = float(p2.x - p1.x)
            dy = float(p2.y - p1.y)
            seg_len = (dx * dx + dy * dy) ** 0.5
            if seg_len < 6.0:
                continue

            if abs(dx) < 0.8:
                vert += 1
                continue

            slope = dy / dx
            if abs(slope) <= 0.12:
                horiz += 1
                continue

            # PDF Y-axis is downward: dy/dx > 0 means visually decreasing.
            if slope < 0:
                diag_inc += 1
            else:
                diag_dec += 1

    return diag_inc, diag_dec, horiz, vert


def infer_direction_from_pdf_figures(
    pdf_path: str | Path,
    claim: dict[str, Any],
    *,
    max_pages: int = 30,
    min_diag_segments: int = 3,
) -> FigureDirectionSignal:
    """Infer direction from figure-like line trends in a PDF.

    Returns unknown if evidence is weak or ambiguous.
    """
    if fitz is None:
        return FigureDirectionSignal(
            direction="unknown",
            confidence=0.0,
            source_page=None,
            evidence_quote="figure_direction_unavailable:fitz_not_installed",
            diagnostics={},
        )

    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        return FigureDirectionSignal(
            direction="unknown",
            confidence=0.0,
            source_page=None,
            evidence_quote=f"figure_direction_unavailable:pdf_missing:{pdf_path}",
            diagnostics={},
        )

    iv_toks, dv_toks, all_toks = _claim_token_buckets(claim)
    if not all_toks:
        return FigureDirectionSignal(
            direction="unknown",
            confidence=0.0,
            source_page=None,
            evidence_quote="figure_direction_unavailable:no_claim_tokens",
            diagnostics={},
        )
    if iv_toks.intersection(_COVARIATE_IV_TOKENS):
        return FigureDirectionSignal(
            direction="unknown",
            confidence=0.0,
            source_page=None,
            evidence_quote="figure_direction_skipped:covariate_iv",
            diagnostics={"iv_tokens": sorted(iv_toks)},
        )

    best: FigureDirectionSignal | None = None

    doc = fitz.open(str(pdf_path))
    try:
        for idx in range(min(max_pages, len(doc))):
            page = doc[idx]
            page_text = _norm(page.get_text("text"))
            relevance, iv_overlap, dv_overlap = _page_relevance(page_text, iv_toks, dv_toks)
            # Precision-first: require lexical support for both IV and DV on-page.
            if iv_overlap < 1 or dv_overlap < 1:
                continue

            drawings = page.get_drawings()
            diag_inc, diag_dec, horiz, vert = _line_slope_vote(drawings)
            diag_total = diag_inc + diag_dec
            if diag_total < min_diag_segments:
                continue

            balance = (diag_inc - diag_dec) / float(max(1, diag_total))
            if abs(balance) < 0.34:
                direction = "unknown"
            else:
                direction = "increase" if balance > 0 else "decrease"

            confidence = min(
                0.82,
                0.42 + (0.28 * abs(balance)) + (0.04 * min(diag_total, 10)) + (0.05 * min(relevance, 4.0)),
            )
            if direction == "unknown":
                confidence = min(confidence, 0.45)

            evidence = (
                f"Figure page {idx + 1}: line-slope vote inc={diag_inc}, dec={diag_dec}, "
                f"horiz={horiz}, vert={vert}, balance={balance:.2f}"
            )
            cand = FigureDirectionSignal(
                direction=direction,
                confidence=round(confidence, 3),
                source_page=idx + 1,
                evidence_quote=evidence,
                diagnostics={
                    "diag_inc": diag_inc,
                    "diag_dec": diag_dec,
                    "diag_total": diag_total,
                    "horiz": horiz,
                    "vert": vert,
                    "balance": round(balance, 3),
                    "relevance": round(relevance, 3),
                    "iv_overlap": iv_overlap,
                    "dv_overlap": dv_overlap,
                },
            )
            if best is None or cand.confidence > best.confidence:
                best = cand
    finally:
        doc.close()

    if best is None:
        return FigureDirectionSignal(
            direction="unknown",
            confidence=0.0,
            source_page=None,
            evidence_quote="figure_direction_unavailable:no_usable_figure_signal",
            diagnostics={},
        )
    return best
