"""
voi_scoring.py -- Paper-level Value-of-Information scorer.

Provides score_voi(), the single callable imported by abstract_triage_4d.py
for Phase 4D classification.

Relationship to VOICalculator
------------------------------
VOICalculator in services/voi_search.py computes gap-level VOI using a
GapType enum and a structured Belief object (uncertainty + paper_ids).
That interface is designed for the belief-update loop, not for screening
individual incoming papers.

score_voi() is a *paper-level* function: given a candidate paper dict
(as produced by the Phase 4B abstract collection stage), it estimates
the marginal epistemic value of reading that paper in full.  It shares
the same conceptual goal -- quantifying how much new information the
paper would add -- but derives the score from observable paper metadata
rather than from an explicit prior belief.

Score formula
-------------
The final score is the sum of four independent components, clamped to
[0.0, 1.0]:

  1. Domain signal density (primary driver, 0.0 -- 0.60)
     Count of strong domain signals in the abstract.  Each occurrence
     contributes 0.10, capped at 6 signals (0.60 total).
     Strong signals are the same list used by triage_funnel.py.

  2. Study design quality (0.0 -- 0.10)
     Empirical indicators in the abstract: RCT/experiment -> +0.10;
     systematic review / meta-analysis -> +0.06; survey -> +0.03.

  3. Recency (0.0 -- 0.08)
     year >= 2020 -> +0.08; >= 2015 -> +0.04; >= 2010 -> +0.02.

  4. Publication formality (0.0 -- 0.10)
     DOI present -> +0.05; abstract length >= 300 chars -> +0.05.

Thresholds (enforced by abstract_triage_4d.py, not here):
  >= 0.70  ->  ACCEPT
  0.50 - 0.69  ->  EDGE_CASE
  < 0.50   ->  REJECT

This module is intentionally free of lifecycle_db or network dependencies
so it can be imported and tested in isolation.
"""
from __future__ import annotations

import re
from typing import Optional

# ── Domain signals (mirrors triage_funnel._STRONG_SIGNALS) ───────────────────
# Kept here as a local constant so cmr/ has no cross-package dependency on
# track2/triage_funnel.py.  Update both lists in sync.

_STRONG_SIGNALS: frozenset[str] = frozenset({
    "daylight", "daylighting", "natural light", "artificial light",
    "circadian", "melanopsin", "correlated colour", "colour temperature",
    "spatial daylight autonomy", "glare", "luminance", "illuminance",
    "window-to-floor", "visual comfort",
    "cognitive", "cognition", "attention", "working memory",
    "executive function", "alertness", "cognitive fatigue", "mental workload",
    "academic performance", "learning performance", "task performance",
    "n-back", "attentional", "cognitive load",
    "wellbeing", "well-being", "biophilic",
    "thermal comfort", "indoor environment quality", "reverberation",
    "soundscape", "acoustic comfort",
})

# ── Study-design keyword sets ─────────────────────────────────────────────────

_EMPIRICAL_MARKERS: tuple[str, ...] = (
    "randomized", "randomised", "controlled trial", "rct",
    "experiment", "experimental study", "quasi-experiment",
    "field study", "laboratory study", "within-subject", "between-subject",
)

_REVIEW_MARKERS: tuple[str, ...] = (
    "systematic review", "meta-analysis", "meta analysis",
    "scoping review", "literature review",
)

_SURVEY_MARKERS: tuple[str, ...] = (
    "survey", "cross-sectional", "questionnaire", "self-report",
    "observational study",
)


# ── Public API ─────────────────────────────────────────────────────────────────

def score_voi(paper: dict, *, gap_context: str = "") -> float:
    """
    Compute a Value-of-Information score for a candidate paper.

    Parameters
    ----------
    paper : dict
        Must contain at least one of: 'abstract', 'title_raw' / 'title'.
        Optional fields that improve accuracy: 'publication_year', 'doi',
        'cited_by', 'venue'.
    gap_context : str
        Unused in the current implementation; reserved for future gap-
        specific weighting (e.g. boost MECHANISM papers for a mechanism gap).

    Returns
    -------
    float in [0.0, 1.0]
        Higher scores indicate greater expected value from full-text review.
    """
    abstract = (paper.get("abstract") or "").strip()
    title    = (paper.get("title_raw") or paper.get("title") or "").strip()
    year     = paper.get("publication_year") or paper.get("year")
    doi      = (paper.get("doi") or "").strip()

    combined_text = (title + " " + abstract).lower()

    # ── Component 1: domain signal density ───────────────────────────────────
    signal_hits = sum(1 for s in _STRONG_SIGNALS if s in combined_text)
    density_score = min(signal_hits * 0.10, 0.60)

    # ── Component 2: study design quality ────────────────────────────────────
    design_score = 0.0
    abstract_lower = abstract.lower()
    if any(m in abstract_lower for m in _EMPIRICAL_MARKERS):
        design_score = 0.10
    elif any(m in abstract_lower for m in _REVIEW_MARKERS):
        design_score = 0.06
    elif any(m in abstract_lower for m in _SURVEY_MARKERS):
        design_score = 0.03

    # ── Component 3: recency ──────────────────────────────────────────────────
    recency_score = 0.0
    try:
        y = int(year) if year else 0
        if y >= 2020:
            recency_score = 0.08
        elif y >= 2015:
            recency_score = 0.04
        elif y >= 2010:
            recency_score = 0.02
    except (TypeError, ValueError):
        pass

    # ── Component 4: publication formality ───────────────────────────────────
    formality_score = 0.0
    if doi:
        formality_score += 0.05
    if len(abstract) >= 300:
        formality_score += 0.05
    elif len(abstract) >= 150:
        formality_score += 0.02

    raw = density_score + design_score + recency_score + formality_score
    return min(round(raw, 4), 1.0)
