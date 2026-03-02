#!/usr/bin/env python3
"""
Backfill beliefs with canonical outcome IDs.

Task: OC-2

Resolves raw outcome_id strings to canonical vocabulary terms from:
  contracts/outcome_vocab/outcome_vocab.json (80 canonical terms)
  contracts/outcome_vocab/outcome_lookup.json (283 lookup entries)

For each belief:
  1. Check if outcome_id is already canonical (in outcome_vocab terms)
  2. If not canonical, resolve via outcome_resolver.resolve_outcome()
  3. Update belief with canonical outcome_id
  4. Handle NULL outcome_ids by inferring from content text

Success criterion: >= 80% of beliefs use canonical outcome_id terms.
"""

from __future__ import annotations

import argparse
import copy
import json
import shutil
import sqlite3
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Set, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from lib.outcome_resolver import resolve_outcome, suggest_domain
from src.services.db_locator import resolve_web_db

MASTER_WEB_ID = "master:web:accumulated"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Backfill beliefs with canonical outcome IDs from OC vocabulary."
    )
    p.add_argument(
        "--web-db",
        default=None,
        help="Path to web DB (auto-resolved if omitted)",
    )
    p.add_argument(
        "--web-db-prefer",
        choices=("integrated", "latest"),
        default="integrated",
        help="Auto-resolution policy when --web-db is omitted",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Compute without writing (default: True)",
    )
    p.add_argument(
        "--commit",
        action="store_true",
        help="Actually write changes to database",
    )
    p.add_argument(
        "--fuzzy-threshold",
        type=float,
        default=0.85,
        help="Minimum similarity score for fuzzy matching (0-1)",
    )
    p.add_argument(
        "--batch-size",
        type=int,
        default=100,
        help="Number of updates before commit",
    )
    return p.parse_args()


def load_canonical_terms() -> Set[str]:
    """Load canonical term IDs from outcome_vocab.json."""
    vocab_path = PROJECT_ROOT / "contracts" / "outcome_vocab" / "outcome_vocab.json"
    if not vocab_path.exists():
        print(f"[WARN] Outcome vocab not found: {vocab_path}")
        return set()

    try:
        with open(vocab_path) as f:
            data = json.load(f)
        # Extract term_ids from the terms list
        canonical = set()
        for term in data.get("terms", []):
            term_id = term.get("term_id")
            if term_id:
                canonical.add(term_id)
        print(f"[info] Loaded {len(canonical)} canonical outcome terms")
        return canonical
    except Exception as e:
        print(f"[ERROR] Failed to load canonical terms: {e}")
        return set()


def is_canonical(outcome_id: str, canonical_terms: Set[str]) -> bool:
    """Check if outcome_id is in the canonical vocabulary."""
    return outcome_id in canonical_terms


def extract_outcome_keywords(content: str, domain: Optional[str] = None) -> list[str]:
    """Extract potential outcome keywords from belief content."""
    if not content:
        return []

    # Very simple extraction: split on common delimiters and filter short tokens
    tokens = []
    for token in content.replace(",", " ").replace(".", " ").split():
        token = token.strip().lower()
        if len(token) > 2 and not token.isdigit():
            tokens.append(token)

    # If we have domain info, filter for domain-relevant terms
    if domain:
        domain_keywords = {
            "cog": ["attention", "memory", "cognit", "think", "learn", "focus"],
            "affect": ["mood", "emotion", "stress", "anxiety", "depress"],
            "behav": ["behavior", "action", "activity", "sleep", "perform"],
            "social": ["social", "interact", "communicat"],
            "physio": ["heart", "blood", "cortisol", "fatigue", "pain"],
            "neural": ["brain", "neural", "cortex", "eeg", "fmri"],
            "health": ["health", "wellbeing", "illness", "disease"],
        }
        relevant = domain_keywords.get(domain, [])
        tokens = [t for t in tokens if any(k in t for k in relevant)]

    return tokens[:5]  # Return top 5 keywords


def try_resolve_from_content(
    content: str,
    domain: Optional[str],
    fuzzy_threshold: float,
) -> Optional[str]:
    """Try to infer outcome_id from belief content."""
    if not content:
        return None

    keywords = extract_outcome_keywords(content, domain)
    for keyword in keywords:
        resolved = resolve_outcome(keyword, fuzzy_threshold)
        if resolved and resolved["confidence"] >= fuzzy_threshold:
            return resolved["canonical_id"]

    return None


def main() -> int:
    args = parse_args()
    db_path = resolve_web_db(args.web_db, prefer=args.web_db_prefer)
    print(f"[backfill_canonical_outcomes] using web_db={db_path}")

    # Load canonical terms
    canonical_terms = load_canonical_terms()
    if not canonical_terms:
        print("[ERROR] Could not load canonical terms. Aborting.")
        return 1

    # Backup database if we're about to commit
    if args.commit and not args.dry_run:
        backup_path = db_path.with_suffix(f".bak.{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
        print(f"[info] Backing up database to {backup_path}")
        try:
            shutil.copy2(str(db_path), str(backup_path))
            print(f"[info] Backup created: {backup_path}")
        except Exception as e:
            print(f"[ERROR] Failed to create backup: {e}")
            return 1

    # Open database with recovery attempt
    try:
        conn = sqlite3.connect(str(db_path), timeout=60.0)
        conn.row_factory = sqlite3.Row
        # Try to execute a simple query to check if DB is healthy
        conn.execute("SELECT COUNT(*) FROM beliefs LIMIT 1")
    except sqlite3.OperationalError as e:
        if "disk I/O error" in str(e) or "database disk image is malformed" in str(e):
            print(f"[ERROR] Database appears corrupted or locked: {e}")
            print(f"[info] Attempting recovery with PRAGMA integrity_check...")
            try:
                conn = sqlite3.connect(str(db_path))
                result = conn.execute("PRAGMA integrity_check").fetchone()
                if result[0] != "ok":
                    print(f"[ERROR] Integrity check failed: {result[0]}")
                    print("[ERROR] Cannot proceed with corrupted database")
                    return 1
            except Exception as recovery_err:
                print(f"[ERROR] Recovery failed: {recovery_err}")
                return 1
        else:
            raise

    conn.row_factory = sqlite3.Row

    # Enable WAL mode for better concurrency on subsequent operations
    try:
        conn.execute("PRAGMA journal_mode=WAL")
    except Exception as e:
        import logging; logging.getLogger(__name__).debug(f"Non-critical: {e}")  # If WAL fails, fall back to default

    try:
        # Fetch all beliefs with outcome_id
        print("[info] Querying beliefs with non-NULL outcome_id...")
        beliefs_with_outcome = conn.execute(
            """
            SELECT belief_id, content, outcome_id, domain
            FROM beliefs
            WHERE outcome_id IS NOT NULL AND outcome_id != ''
            """,
        ).fetchall()

        print(f"[info] Found {len(beliefs_with_outcome)} beliefs with non-NULL outcome_id")

        # Fetch beliefs with NULL outcome_id
        print("[info] Querying beliefs with NULL outcome_id...")
        beliefs_without_outcome = conn.execute(
            """
            SELECT belief_id, content, domain
            FROM beliefs
            WHERE outcome_id IS NULL OR outcome_id = ''
            """,
        ).fetchall()

        print(f"[info] Found {len(beliefs_without_outcome)} beliefs with NULL outcome_id")

        # Process beliefs with outcome_id
        stats: Dict[str, int] = {
            "total_with_outcome": len(beliefs_with_outcome),
            "already_canonical": 0,
            "resolved_via_outcome": 0,
            "resolved_via_content": 0,
            "unresolved": 0,
            "total_without_outcome": len(beliefs_without_outcome),
            "inferred_from_content": 0,
        }

        updates: list[Tuple[Any, ...]] = []
        unresolved_terms: Dict[str, int] = defaultdict(int)
        by_domain: Dict[str, int] = defaultdict(int)

        print("[info] Processing beliefs with outcome_id...")
        for row in beliefs_with_outcome:
            belief_id = row["belief_id"]
            content = row["content"]
            outcome_id = row["outcome_id"]
            domain = row["domain"]

            # Check if already canonical
            if is_canonical(outcome_id, canonical_terms):
                stats["already_canonical"] += 1
                by_domain[domain or "unknown"] += 1
                continue

            # Try resolving the raw outcome_id
            resolved = resolve_outcome(outcome_id, args.fuzzy_threshold)
            if resolved and resolved["confidence"] >= args.fuzzy_threshold:
                canonical_id = resolved["canonical_id"]
                stats["resolved_via_outcome"] += 1
                updates.append((canonical_id, belief_id))
                by_domain[domain or "unknown"] += 1
                continue

            # Try inferring from content
            inferred_id = try_resolve_from_content(content, domain, args.fuzzy_threshold)
            if inferred_id:
                stats["resolved_via_content"] += 1
                updates.append((inferred_id, belief_id))
                by_domain[domain or "unknown"] += 1
                continue

            # Could not resolve
            stats["unresolved"] += 1
            unresolved_terms[outcome_id] += 1
            by_domain[domain or "unknown"] += 1

        # Process beliefs without outcome_id
        print("[info] Processing beliefs with NULL outcome_id...")
        for row in beliefs_without_outcome:
            belief_id = row["belief_id"]
            content = row["content"]
            domain = row["domain"]

            # Try inferring from content
            inferred_id = try_resolve_from_content(content, domain, args.fuzzy_threshold)
            if inferred_id:
                stats["inferred_from_content"] += 1
                updates.append((inferred_id, belief_id))
                by_domain[domain or "unknown"] += 1

        # Report
        print("\n" + "=" * 70)
        print("BACKFILL SUMMARY")
        print("=" * 70)
        print(f"\nBelief Coverage (with outcome_id):")
        print(f"  Total:                    {stats['total_with_outcome']}")
        print(f"  Already canonical:        {stats['already_canonical']}")
        print(f"  Resolved via outcome:     {stats['resolved_via_outcome']}")
        print(f"  Resolved via content:     {stats['resolved_via_content']}")
        print(f"  Unresolved:               {stats['unresolved']}")

        with_outcome_resolved = (
            stats["already_canonical"]
            + stats["resolved_via_outcome"]
            + stats["resolved_via_content"]
        )
        pct = 100.0 * with_outcome_resolved / stats["total_with_outcome"] if stats["total_with_outcome"] > 0 else 0.0
        print(f"  Coverage:                 {with_outcome_resolved}/{stats['total_with_outcome']} ({pct:.1f}%)")

        print(f"\nBelief Coverage (without outcome_id):")
        print(f"  Total:                    {stats['total_without_outcome']}")
        print(f"  Inferred from content:    {stats['inferred_from_content']}")

        print(f"\nBreakdown by domain:")
        for domain_key in sorted(by_domain.keys()):
            print(f"  {domain_key:20s}: {by_domain[domain_key]:6d}")

        print(f"\nTop 20 unresolved terms:")
        sorted_unresolved = sorted(
            unresolved_terms.items(),
            key=lambda x: -x[1],
        )[:20]
        for term, count in sorted_unresolved:
            print(f"  {term:40s}: {count:4d}")

        # Dry run check
        if args.dry_run and not args.commit:
            print(f"\n[info] DRY RUN: Would update {len(updates)} beliefs")
            print("[info] Use --commit to write changes")
            return 0

        # Commit updates
        if updates:
            print(f"\n[info] Committing {len(updates)} updates...")
            batch = []
            committed_count = 0
            for canonical_id, belief_id in updates:
                batch.append((canonical_id, belief_id))
                if len(batch) >= args.batch_size:
                    try:
                        conn.executemany(
                            """
                            UPDATE beliefs
                            SET outcome_id = ?
                            WHERE belief_id = ?
                            """,
                            batch,
                        )
                        conn.commit()
                        committed_count += len(batch)
                        print(f"[info]   Committed {len(batch)} beliefs (total: {committed_count})")
                    except sqlite3.OperationalError as e:
                        print(f"[ERROR] Failed to commit batch: {e}")
                        conn.rollback()
                        raise
                    batch = []

            # Commit remaining
            if batch:
                try:
                    conn.executemany(
                        """
                        UPDATE beliefs
                        SET outcome_id = ?
                        WHERE belief_id = ?
                        """,
                        batch,
                    )
                    conn.commit()
                    committed_count += len(batch)
                    print(f"[info]   Committed {len(batch)} beliefs (total: {committed_count})")
                except sqlite3.OperationalError as e:
                    print(f"[ERROR] Failed to commit final batch: {e}")
                    conn.rollback()
                    raise

            print(f"[info] All {committed_count} beliefs updated successfully")
        else:
            print("[info] No updates needed")

        return 0

    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 1

    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
