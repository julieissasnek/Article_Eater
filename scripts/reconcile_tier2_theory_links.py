#!/usr/bin/env python3
"""Reconcile tier2 theory-link constraints to canonical Sprint 10 shape."""

from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

from src.services.db_locator import get_web_db


def reconcile(db_path: Path) -> dict[str, int]:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT COUNT(*) FROM constraints WHERE constraint_id LIKE 'tier2_theory_link:%'"
        )
        prefix_total = cur.fetchone()[0]

        cur.execute(
            "SELECT COUNT(*) FROM constraints WHERE constraint_type='tier2_theory_link'"
        )
        type_total_before = cur.fetchone()[0]

        cur.execute(
            """
            UPDATE constraints
            SET constraint_type='tier2_theory_link',
                warrant_type='tier2_theory_link'
            WHERE constraint_id LIKE 'tier2_theory_link:%'
            """
        )
        updated_prefix = cur.rowcount if cur.rowcount is not None else 0

        # Normalize legacy discovery-generated rows that previously used
        # tier2_theory_link as a generic constraint type but are not part of
        # tranche80 staged IDs.
        cur.execute(
            """
            UPDATE constraints
            SET constraint_type='coherence_support'
            WHERE constraint_type='tier2_theory_link'
              AND constraint_id NOT LIKE 'tier2_theory_link:%'
            """
        )
        normalized_nonprefix = cur.rowcount if cur.rowcount is not None else 0
        conn.commit()

        cur.execute(
            "SELECT COUNT(*) FROM constraints WHERE constraint_type='tier2_theory_link'"
        )
        type_total_after = cur.fetchone()[0]

        return {
            "prefix_total": int(prefix_total),
            "type_total_before": int(type_total_before),
            "rows_updated_prefix": int(updated_prefix),
            "rows_normalized_nonprefix": int(normalized_nonprefix),
            "type_total_after": int(type_total_after),
        }
    finally:
        conn.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=get_web_db())
    args = parser.parse_args()

    if not args.db.exists():
        print(f"ERROR: DB not found: {args.db}")
        return 1

    result = reconcile(args.db)
    for key, value in result.items():
        print(f"{key}={value}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
