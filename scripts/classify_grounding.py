#!/usr/bin/env python3
"""
classify_grounding.py — Classify belief justification status
==============================================================

Per Haack's foundherentism (ATLAS §48.1):
- GROUNDED: Belief has experiential/empirical backing (linked to paper findings)
- COHERENT_ONLY: Justified only by coherence with other beliefs (has edges, no papers)  
- UNJUSTIFIED: No justification (isolated, no papers)

Classification logic:
1. If belief has paper_ids → GROUNDED (empirical evidence from published research)
2. If belief has ≥1 constraint edge but no papers → COHERENT_ONLY (web coherence only)
3. If belief is isolated (no edges, no papers) → UNJUSTIFIED

Updates the `epistemic_v2` JSON column with the computed justification_status.

Usage:
    python3 scripts/classify_grounding.py --dry-run     # see what would change
    python3 scripts/classify_grounding.py               # apply classifications
"""

import argparse
import json
import logging
import sqlite3
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)

DEFAULT_DB = PROJECT_ROOT / "data" / "web_persistence_v2.db"


def _resolve_db(explicit: str | None = None) -> str:
    """Resolve DB path using the same logic as compute_system_health.py."""
    if explicit:
        return explicit
    try:
        from src.services.db_locator import resolve_web_db
        resolved = resolve_web_db(prefer="integrated")
        logger.info("Resolved DB via db_locator: %s", resolved)
        return str(resolved)
    except Exception:
        logger.info("db_locator failed, using default: %s", DEFAULT_DB)
        return str(DEFAULT_DB)


def classify_beliefs(db_path: str, dry_run: bool = False) -> dict:
    """Classify all non-retired beliefs and update epistemic_v2."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    # Get schema
    cols = {row[1] for row in conn.execute("PRAGMA table_info(beliefs)").fetchall()}
    logger.info("Beliefs table columns: %s", sorted(cols))

    # Get all non-retired beliefs
    beliefs = conn.execute(
        "SELECT belief_id, paper_ids, evidence_cluster_id, epistemic_v2, status "
        "FROM beliefs WHERE status != 'RETIRED'"
    ).fetchall()
    total = len(beliefs)
    logger.info("Total non-retired beliefs: %d", total)

    # Build set of beliefs that have edges
    beliefs_with_edges = set()
    for row in conn.execute(
        "SELECT DISTINCT source_id FROM constraints"
    ).fetchall():
        beliefs_with_edges.add(row[0])
    for row in conn.execute(
        "SELECT DISTINCT target_id FROM constraints"
    ).fetchall():
        beliefs_with_edges.add(row[0])
    logger.info("Beliefs with ≥1 edge: %d", len(beliefs_with_edges))

    # Classify
    stats = {
        "GROUNDED": 0,
        "COHERENT_ONLY": 0,
        "UNJUSTIFIED": 0,
        "total": total,
        "already_set": 0,
        "updated": 0,
    }
    updates = []

    for b in beliefs:
        belief_id = b["belief_id"]

        # Check paper_ids
        has_papers = False
        paper_ids_raw = b["paper_ids"]
        if paper_ids_raw:
            try:
                papers = json.loads(paper_ids_raw)
                if isinstance(papers, list) and len(papers) > 0:
                    has_papers = True
            except (json.JSONDecodeError, TypeError):
                if paper_ids_raw.strip() not in ("", "[]", "null"):
                    has_papers = True

        # Check evidence_cluster_id
        has_cluster = bool(b["evidence_cluster_id"] and b["evidence_cluster_id"].strip())

        # Check edges
        has_edges = belief_id in beliefs_with_edges

        # Classify per Haack's foundherentism
        if has_papers or has_cluster:
            status = "GROUNDED"
        elif has_edges:
            status = "COHERENT_ONLY"
        else:
            status = "UNJUSTIFIED"

        stats[status] += 1

        # Parse existing epistemic_v2
        ev2 = {}
        if b["epistemic_v2"]:
            try:
                ev2 = json.loads(b["epistemic_v2"])
            except (json.JSONDecodeError, TypeError):
                ev2 = {}

        # Check if already set correctly
        existing_prov = ev2.get("provenance_v2", {})
        if existing_prov.get("justification_status") == status:
            stats["already_set"] += 1
            continue

        # Update provenance_v2
        if "provenance_v2" not in ev2:
            ev2["provenance_v2"] = {}
        ev2["provenance_v2"]["justification_status"] = status
        ev2["provenance_v2"]["grounding_basis"] = (
            "paper_evidence" if has_papers else
            "evidence_cluster" if has_cluster else
            "web_coherence" if has_edges else
            "none"
        )

        updates.append((json.dumps(ev2), belief_id))
        stats["updated"] += 1

    # Apply updates
    if not dry_run and updates:
        conn.executemany(
            "UPDATE beliefs SET epistemic_v2 = ? WHERE belief_id = ?",
            updates,
        )
        conn.commit()
        logger.info("Applied %d updates to epistemic_v2", len(updates))
    elif dry_run:
        logger.info("DRY RUN — would update %d beliefs", len(updates))

    conn.close()

    # Compute ratios
    stats["grounding_ratio"] = round(stats["GROUNDED"] / total, 4) if total > 0 else 0
    stats["coherent_ratio"] = round(stats["COHERENT_ONLY"] / total, 4) if total > 0 else 0
    stats["unjustified_ratio"] = round(stats["UNJUSTIFIED"] / total, 4) if total > 0 else 0

    return stats


def main():
    parser = argparse.ArgumentParser(
        description="Classify belief justification status (GROUNDED / COHERENT_ONLY / UNJUSTIFIED)"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show classifications without updating DB",
    )
    parser.add_argument(
        "--db", type=str, default=str(DEFAULT_DB),
        help="Path to SQLite database",
    )
    args = parser.parse_args()

    db_path = _resolve_db(args.db if args.db != str(DEFAULT_DB) else None)
    logger.info("Using DB: %s", db_path)

    logger.info("=== Grounding Classification ===")
    stats = classify_beliefs(db_path, dry_run=args.dry_run)

    print("\n" + "=" * 60)
    print("GROUNDING CLASSIFICATION RESULTS")
    print("=" * 60)
    print(f"  Total beliefs:    {stats['total']:,}")
    print(f"  GROUNDED:         {stats['GROUNDED']:,}  ({100*stats['grounding_ratio']:.1f}%)")
    print(f"  COHERENT_ONLY:    {stats['COHERENT_ONLY']:,}  ({100*stats['coherent_ratio']:.1f}%)")
    print(f"  UNJUSTIFIED:      {stats['UNJUSTIFIED']:,}  ({100*stats['unjustified_ratio']:.1f}%)")
    print(f"  Already set:      {stats['already_set']:,}")
    print(f"  {'Would update' if args.dry_run else 'Updated'}:  {stats['updated']:,}")

    # AESHI impact prediction
    print(f"\n  AESHI grounding score: {'GREEN' if stats['grounding_ratio'] >= 0.60 else 'YELLOW' if stats['grounding_ratio'] >= 0.40 else 'RED'}")
    if stats["grounding_ratio"] < 0.60:
        needed = int(0.60 * stats["total"] - stats["GROUNDED"])
        print(f"  Need {needed:,} more GROUNDED beliefs for GREEN threshold")

    print()
    if args.dry_run:
        print("  Run without --dry-run to apply classifications.")


if __name__ == "__main__":
    main()
