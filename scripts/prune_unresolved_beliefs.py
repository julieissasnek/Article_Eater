#!/usr/bin/env python3
"""
Prune unresolved/unknown domain beliefs from the Web of Belief.

This script deletes beliefs from `ae.db` and `data/web_persistence.db` that were
blindly extracted by the pipeline (e.g. domain = 'unresolved' or 'unknown') and
were not seeded by calibrated frameworks. It also deletes any constraints that
reference these deleted beliefs.
"""

import argparse
import sqlite3
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DB_PATH = PROJECT_ROOT / "data" / "web_persistence.db"

def prune_web_persistence(db_path: Path, dry_run: bool = False):
    print(f"\nTarget Database: {db_path}")
    if not db_path.exists():
        print(f"Error: Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='beliefs'")
        if not cursor.fetchone():
            print("Table 'beliefs' not found in database.")
            return

        # 1. Identify beliefs to prune
        # Only prune if domain is unresolved or unknown.
        cursor.execute(
            "SELECT belief_id FROM beliefs WHERE domain IN ('unresolved', 'unknown')"
        )
        beliefs_to_prune = [row[0] for row in cursor.fetchall()]
        
        print(f"Found {len(beliefs_to_prune)} beliefs with 'unresolved' or 'unknown' domains.")

        if not beliefs_to_prune:
            print("Nothing to prune.")
            return

        if dry_run:
            print(f"[DRY RUN] Would delete {len(beliefs_to_prune)} beliefs.")
        else:
            # 2. Delete the beliefs
            placeholders = ','.join('?' * len(beliefs_to_prune))
            cursor.execute(
                f"DELETE FROM beliefs WHERE domain IN ('unresolved', 'unknown')"
            )
            deleted_beliefs = cursor.rowcount
            print(f"Deleted {deleted_beliefs} beliefs.")

            # 3. Clean up orphaned constraints
            # Any constraint where source_id or target_id is no longer in beliefs
            cursor.execute('''
                DELETE FROM constraints 
                WHERE source_id NOT IN (SELECT belief_id FROM beliefs)
                   OR target_id NOT IN (SELECT belief_id FROM beliefs)
            ''')
            deleted_constraints = cursor.rowcount
            print(f"Deleted {deleted_constraints} orphaned constraints.")

            conn.commit()
            print("Pruning complete. Run 'python3 -m src.services.web_accumulator stats' to verify.")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()

def main():
    parser = argparse.ArgumentParser(description="Prune pointless extraction chunks from Web of Belief.")
    parser.add_argument('--dry-run', action='store_true', help="Preview what would be deleted.")
    args = parser.parse_args()

    print("=== Web of Belief Pruning Utility ===")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
    
    prune_web_persistence(DB_PATH, dry_run=args.dry_run)

if __name__ == "__main__":
    main()
