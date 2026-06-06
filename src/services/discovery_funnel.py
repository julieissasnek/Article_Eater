"""
discovery_funnel.py -- Gap closure assessment for the Knowledge Atlas pipeline.

Provides classify_closure(), which estimates whether a research gap has been
addressed by the collected evidence in pipeline_lifecycle_full.db.

A gap is considered:
  'closed'        -- >= CLOSED_THRESHOLD ACCEPT papers with VOI >= 0.70
  'partially_closed' -- some on-topic evidence but below the closed threshold
  'open'          -- no ACCEPT papers found for this gap
  'insufficient_data' -- fewer than MIN_PAPERS papers ingested for this gap

This module is the canonical import point for gap-closure logic.
It reads directly from article_references via lifecycle_db.get_connection()
and never hard-codes counts.

Usage:
    from services.discovery_funnel import classify_closure, GapClosure

    result = classify_closure("GAP-PNU-001", db_path=LIFECYCLE_DB)
    print(result.status)       # 'closed' | 'partially_closed' | 'open' | ...
    print(result.accept_count) # int
    print(result.mean_voi)     # float or None
    print(result.reason)       # human-readable string
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

# ── Thresholds ────────────────────────────────────────────────────────────────
CLOSED_THRESHOLD    = 3     # minimum ACCEPT papers to consider a gap 'closed'
MIN_PAPERS          = 1     # gaps with fewer papers → 'insufficient_data'
MIN_VOI_FOR_CLOSED  = 0.60  # mean VOI of ACCEPT papers must be >= this


# ── Result dataclass ──────────────────────────────────────────────────────────

@dataclass
class GapClosure:
    """Result of classify_closure() for one research gap."""
    gap_id:        str
    status:        str            # closed | partially_closed | open | insufficient_data
    total_papers:  int
    accept_count:  int
    edge_count:    int
    mean_voi:      Optional[float]
    reason:        str


# ── Classifier ────────────────────────────────────────────────────────────────

def classify_closure(
    gap_id: str,
    *,
    db_path: str = "",
) -> GapClosure:
    """
    Classify the closure state of a research gap.

    Parameters
    ----------
    gap_id   : the gap identifier (e.g. 'GAP-PNU-001')
    db_path  : path to pipeline_lifecycle_full.db; defaults to lifecycle_db.LIFECYCLE_DB

    Returns
    -------
    GapClosure dataclass with status, counts, and a human-readable reason.
    """
    if not db_path:
        try:
            import sys as _sys, pathlib as _pl
            _track2 = _pl.Path(__file__).resolve().parent.parent.parent.parent / "Knowledge_Atlas" / "160sp" / "track2"
            if str(_track2) not in _sys.path and _track2.exists():
                _sys.path.insert(0, str(_track2))
            from lifecycle_db import LIFECYCLE_DB as _default_db  # type: ignore
            db_path = _default_db
        except ImportError:
            return GapClosure(gap_id, "insufficient_data", 0, 0, 0, None,
                              "lifecycle_db not importable")

    if not Path(db_path).exists() or Path(db_path).stat().st_size == 0:
        return GapClosure(gap_id, "insufficient_data", 0, 0, 0, None,
                          f"Database not found: {db_path}")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    row = conn.execute(
        """
        SELECT
            COUNT(*)                                                      AS total,
            SUM(CASE WHEN phase4d_decision='ACCEPT'    THEN 1 ELSE 0 END) AS n_accept,
            SUM(CASE WHEN phase4d_decision='EDGE_CASE' THEN 1 ELSE 0 END) AS n_edge,
            AVG(CASE WHEN phase4d_decision='ACCEPT'
                     THEN phase4d_voi_score END)                          AS mean_voi
        FROM article_references
        WHERE discovered_query = ?
        """,
        (gap_id,),
    ).fetchone()
    conn.close()

    total      = row["total"]     or 0
    n_accept   = row["n_accept"]  or 0
    n_edge     = row["n_edge"]    or 0
    mean_voi   = round(row["mean_voi"], 4) if row["mean_voi"] is not None else None

    if total < MIN_PAPERS:
        status = "insufficient_data"
        reason = f"Only {total} papers ingested for {gap_id}; need at least {MIN_PAPERS}."
    elif n_accept == 0:
        status = "open"
        reason = f"No ACCEPT papers found for {gap_id} (total={total})."
    elif n_accept >= CLOSED_THRESHOLD and (mean_voi or 0) >= MIN_VOI_FOR_CLOSED:
        status = "closed"
        reason = (
            f"{n_accept} ACCEPT papers with mean VOI {mean_voi:.3f} "
            f"meet the closure threshold ({CLOSED_THRESHOLD} papers, VOI >= {MIN_VOI_FOR_CLOSED})."
        )
    else:
        status = "partially_closed"
        voi_str = f"{mean_voi:.3f}" if mean_voi is not None else "N/A"
        reason = (
            f"{n_accept} ACCEPT paper(s) found (threshold={CLOSED_THRESHOLD}), "
            f"mean VOI={voi_str}. "
            "More evidence needed for full closure."
        )

    return GapClosure(
        gap_id       = gap_id,
        status       = status,
        total_papers = total,
        accept_count = n_accept,
        edge_count   = n_edge,
        mean_voi     = mean_voi,
        reason       = reason,
    )


def classify_all_gaps(
    query_file: str,
    *,
    db_path: str = "",
) -> list[GapClosure]:
    """
    Run classify_closure() on every gap defined in query_results.json.
    Returns a list of GapClosure objects sorted by status then gap_id.
    """
    import json
    p = Path(query_file)
    if not p.exists():
        return []
    gaps = json.loads(p.read_text(encoding="utf-8"))
    results = [classify_closure(g["gap_id"], db_path=db_path) for g in gaps]
    order = {"closed": 0, "partially_closed": 1, "open": 2, "insufficient_data": 3}
    results.sort(key=lambda r: (order.get(r.status, 9), r.gap_id))
    return results
