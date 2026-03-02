#!/usr/bin/env python3
"""
ATLAS Database Diagnostic — Physical + Application-Level Integrity
==================================================================

Updated: 2026-02-27 (per AG's Emergency DB Health Report)

Fixes:
  A: Added repo-root sys.path bootstrap (was missing, caused ModuleNotFoundError)
  B: Validates constraint types against centralized EdgeType enum instead of
     hardcoded legacy allowlist. The old allowlist ('supports', 'contradicts',
     'explains', 'constitutes', 'predicts') missed ~30% of valid edge types
     including epistemic_derivation, coherence_support, epistemic_mediation.
  C: Reports non-canonical types as INFO (not ERROR) since they may be valid
     extensions not yet registered in the enum.

Usage:
    python scripts/diagnose_db_corruption.py
    python scripts/diagnose_db_corruption.py --db data/web_persistence.db
    python scripts/diagnose_db_corruption.py --verbose
"""

import sqlite3
import sys
import argparse
from pathlib import Path

# Fix A: repo-root sys.path bootstrap
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.services.db_locator import resolve_web_db


def get_canonical_constraint_types() -> set:
    """
    Fix B: Load canonical edge types from the centralized EdgeType enum
    instead of a hardcoded allowlist.
    """
    try:
        from src.epistemic.edge_types import EdgeType
        return {e.value for e in EdgeType}
    except ImportError:
        # Fallback: comprehensive list if import fails
        return {
            "supports", "contradicts", "explains", "instantiates",
            "analogous", "independent",
            "coherence_support", "coherence_tension",
            "epistemic_derivation", "epistemic_cross_template",
            "epistemic_mediation",
            "bridges", "strong_tension", "shared_evidence",
            "generalizability_warrant",
            "argumentative_support", "argumentative_challenge",
            "includes_in_synthesis", "synthesizes_as",
            "identifies_moderator", "contradicts_synthesis",
            "theoretically_predicts", "confirms_prediction",
            "disconfirms_prediction", "proposes_mechanism",
            "subsumes_theory", "theory_tension",
            "defines_construct", "refines_construct",
            "challenges_validity", "questions_method",
            "questions_generalizability",
            "cites_evidence", "extends_finding",
        }


def diagnose(db_path_override: str = None, verbose: bool = False) -> int:
    try:
        if db_path_override:
            db_path = Path(db_path_override)
            if not db_path.exists():
                print(f"ERROR: Database not found: {db_path}")
                return 1
        else:
            db_path = resolve_web_db(None, prefer="integrated")
    except Exception as e:
        print(f"Error locating DB: {e}")
        return 1

    print(f"Diagnosing DB at: {db_path}")

    # 1. Check if file exists and has size
    if not Path(db_path).exists():
        print("ERROR: Database file does not exist!")
        return 1

    size_mb = Path(db_path).stat().st_size / (1024 * 1024)
    print(f"File size: {size_mb:.2f} MB")
    if size_mb == 0:
        print("ERROR: Database file is empty (0 bytes)!")
        return 1

    # Check for stale journal/WAL files
    journal = Path(str(db_path) + "-journal")
    wal = Path(str(db_path) + "-wal")
    if journal.exists():
        print(f"WARNING: Stale journal file exists ({journal.name}, "
              f"{journal.stat().st_size / 1024:.0f} KB)")
        print("  This may indicate an interrupted write operation.")
    if wal.exists():
        print(f"INFO: WAL file exists ({wal.name}, "
              f"{wal.stat().st_size / 1024:.0f} KB)")

    # 2. Try to connect and run integrity checks
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        print("\nRunning PRAGMA integrity_check...")
        cursor.execute("PRAGMA integrity_check;")
        results = cursor.fetchall()

        for row in results:
            print(f"  {row[0]}")

        physical_ok = len(results) == 1 and results[0][0] == "ok"
        if physical_ok:
            print("Physical integrity: PASS (SQLite structure is sound)")
        else:
            print("Physical integrity: FAIL (structural corruption detected)")
            conn.close()
            return 1

        # Quick check
        cursor.execute("PRAGMA quick_check;")
        quick = cursor.fetchone()[0]
        print(f"Quick check: {quick}")

        # Journal mode
        cursor.execute("PRAGMA journal_mode;")
        journal_mode = cursor.fetchone()[0]
        print(f"Journal mode: {journal_mode}")

        # 3. Application-level integrity
        print("\n--- Application-Level Integrity ---")

        # Tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [r[0] for r in cursor.fetchall()]
        print(f"Tables ({len(tables)}): {', '.join(tables)}")

        # Beliefs
        count_beliefs = cursor.execute("SELECT COUNT(*) FROM beliefs").fetchone()[0]
        print(f"Total beliefs: {count_beliefs}")

        # Beliefs by level
        try:
            cursor.execute("SELECT level, COUNT(*) FROM beliefs GROUP BY level ORDER BY COUNT(*) DESC")
            for row in cursor.fetchall():
                print(f"  {row[0]}: {row[1]}")
        except Exception as e:
            import logging; logging.getLogger(__name__).debug(f"Non-critical: {e}")

        # Constraints
        count_constraints = cursor.execute("SELECT COUNT(*) FROM constraints").fetchone()[0]
        print(f"Total constraints: {count_constraints}")

        # Fix B: Validate constraint types against centralized EdgeType enum
        canonical_types = get_canonical_constraint_types()
        cursor.execute(
            "SELECT DISTINCT constraint_type, COUNT(*) FROM constraints "
            "GROUP BY constraint_type ORDER BY COUNT(*) DESC"
        )
        type_rows = cursor.fetchall()

        non_canonical = []
        print(f"\nConstraint types ({len(type_rows)} distinct):")
        for ctype, count in type_rows:
            is_canonical = ctype in canonical_types
            status = "✓" if is_canonical else "?"
            print(f"  {status} {ctype}: {count}")
            if not is_canonical:
                non_canonical.append((ctype, count))

        # Fix C: Non-canonical types are INFO, not ERROR
        if non_canonical:
            total_nc = sum(c for _, c in non_canonical)
            pct = total_nc / count_constraints * 100 if count_constraints else 0
            print(f"\nINFO: {len(non_canonical)} non-canonical constraint types "
                  f"({total_nc} rows, {pct:.1f}% of total)")
            print("  These may be valid extensions not yet registered in EdgeType enum.")
            print("  This is NOT corruption — it's a contract mismatch between")
            print("  the edge type registry and the data.")
        else:
            print("\nAll constraint types are canonical. ✓")

        # Bridges
        if "bridges" in tables:
            count_bridges = cursor.execute("SELECT COUNT(*) FROM bridges").fetchone()[0]
            print(f"\nBridges: {count_bridges}")

        # Paper integrations
        if "paper_integrations" in tables:
            count_papers = cursor.execute(
                "SELECT COUNT(DISTINCT paper_id) FROM paper_integrations"
            ).fetchone()[0]
            print(f"Distinct papers integrated: {count_papers}")

        # Isolated beliefs
        try:
            cursor.execute("""
                SELECT COUNT(*) FROM beliefs b
                WHERE b.belief_id NOT IN (
                    SELECT source_id FROM constraints
                    UNION
                    SELECT target_id FROM constraints
                )
            """)
            isolated = cursor.fetchone()[0]
            pct = isolated / count_beliefs * 100 if count_beliefs else 0
            print(f"Isolated beliefs: {isolated} ({pct:.1f}%)")
        except Exception as e:
            import logging; logging.getLogger(__name__).debug(f"Non-critical: {e}")

        # Write test
        print("\n--- Write Capability ---")
        try:
            cursor.execute("CREATE TABLE IF NOT EXISTS _diagnostic_test (x INTEGER)")
            cursor.execute("INSERT INTO _diagnostic_test VALUES (1)")
            conn.commit()
            cursor.execute("DROP TABLE _diagnostic_test")
            conn.commit()
            print("Write test: PASS")
        except Exception as e:
            print(f"Write test: FAIL ({e})")
            print("  Database is readable but not writable.")

        conn.close()

        # 4. Final verdict
        print("\n=== DIAGNOSTIC VERDICT ===")
        print(f"Physical integrity:     {'PASS' if physical_ok else 'FAIL'}")
        print(f"Application integrity:  {'PASS' if not non_canonical else 'INFO (non-canonical types present)'}")
        print(f"Beliefs:                {count_beliefs}")
        print(f"Constraints:            {count_constraints}")

        return 0

    except sqlite3.DatabaseError as e:
        print(f"\nFATAL SQLITE ERROR: {e}")
        return 1
    except Exception as e:
        print(f"\nUNEXPECTED ERROR: {e}")
        return 1


def main():
    parser = argparse.ArgumentParser(
        description="ATLAS Database Diagnostic"
    )
    parser.add_argument("--db", type=str, help="Path to specific database")
    parser.add_argument("--verbose", action="store_true", help="Show detailed output")
    args = parser.parse_args()
    return diagnose(db_path_override=args.db, verbose=args.verbose)


if __name__ == "__main__":
    sys.exit(main())
