#!/usr/bin/env python3
"""
backfill_belief_ids.py — Populate environment_id and outcome_id for beliefs
===============================================================================

CRITICAL FIX: All 3,420 beliefs in web_persistence_v2.db have null environment_id
and outcome_id. The template matcher needs these to compute relevance scores.

This script:
1. Loads outcome_lookup.json (consequent string → outcome_id mapping)
2. Connects to beliefs table and iterates through each belief
3. For each belief:
   - Extracts consequent/outcome from content field
   - Maps to outcome_id using outcome_lookup fuzzy matching
   - Hashes antecedent to create environment_id (or use raw antecedent)
   - Updates belief row with both IDs
4. Reports: beliefs updated, coverage metrics, sample mappings

Usage:
    python3 scripts/backfill_belief_ids.py \
        --web-db data/web_persistence_v2.db \
        --outcome-lookup contracts/outcome_vocab/outcome_lookup.json \
        [--dry-run] [--limit N]

Version: 1.0 (2026-03-01)
"""

import argparse
import hashlib
import json
import logging
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

from src.services.db_locator import get_web_db
from typing import Optional, Dict, Tuple

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s'
)
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def load_outcome_lookup(lookup_path: Path) -> Dict[str, str]:
    """Load outcome_lookup.json: maps consequent strings to outcome_ids."""
    try:
        with open(lookup_path) as f:
            data = json.load(f)
        lookup = data.get("lookup", {})
        logger.info(f"Loaded outcome_lookup.json: {len(lookup)} mappings")
        return lookup
    except Exception as e:
        logger.error(f"Failed to load outcome_lookup: {e}")
        return {}


def find_best_outcome_id(
    text: str,
    outcome_lookup: Dict[str, str],
    fallback_prefix: str = "unknown"
) -> Optional[str]:
    """
    Find the best outcome_id for a given text by keyword matching.

    Strategies (in order):
    1. Exact match in outcome_lookup
    2. Case-insensitive substring match (longest match wins)
    3. Split text into keywords, find best match per keyword
    4. Return fallback if no match
    """
    if not text:
        return None

    text_lower = text.lower().strip()

    # Strategy 1: Exact match
    if text_lower in outcome_lookup:
        return outcome_lookup[text_lower]

    # Strategy 2: Case-insensitive substring match (longest match wins)
    best_match = None
    best_match_len = 0
    for key, val in outcome_lookup.items():
        if key in text_lower and len(key) > best_match_len:
            best_match = val
            best_match_len = len(key)

    if best_match:
        return best_match

    # Strategy 3: Keyword matching - extract key terms from text
    # Remove common stop words and split
    stop_words = {'the', 'a', 'an', 'and', 'or', 'is', 'of', 'to', 'in', 'by', 'from', 'for', 'that', 'this', 'it', 'on', 'at', 'with'}
    words = [w.strip('()[]{}.,;:!?"\'') for w in text_lower.split()]
    keywords = [w for w in words if w and w not in stop_words and len(w) > 2]

    # Try to match each keyword
    best_matches_by_keyword = {}
    for keyword in keywords:
        for key, val in outcome_lookup.items():
            if keyword in key or key in keyword:
                best_matches_by_keyword[keyword] = val
                break

    # Return most specific match (one with longest key)
    if best_matches_by_keyword:
        return max(best_matches_by_keyword.values(),
                  key=lambda v: len(v))

    # Strategy 4: Fallback to unknown
    return None


def hash_environment(text: str) -> str:
    """Create deterministic hash of environment text."""
    if not text:
        return "env:unknown"

    # Use first 100 chars to keep it manageable
    text_norm = text.strip()[:100].lower()
    hash_val = hashlib.md5(text_norm.encode()).hexdigest()[:8]
    return f"env:{hash_val}"


def extract_consequent_from_belief_content(
    belief_id: str,
    content: str,
    extractions_dir: Optional[Path] = None
) -> Optional[str]:
    """
    Extract consequent/outcome text from belief content or original extraction.

    Strategies:
    1. If content contains JSON with "consequent" field, use that
    2. If belief_id starts with "template:", use content as consequent
    3. If belief_id is extraction-based (doi:...), look up original extraction file
    4. Otherwise return None
    """
    if not content or not content.strip():
        content = None
    else:
        # Try to parse content as JSON
        try:
            obj = json.loads(content)
            if isinstance(obj, dict):
                for key in ['consequent', 'outcome', 'conclusion', 'effect']:
                    if key in obj:
                        return obj[key]
        except (json.JSONDecodeError, ValueError):
            pass

    # If belief_id starts with "template:", content is the consequent
    if belief_id.startswith("template:"):
        return content

    # For extraction-based beliefs (doi:...), look up the original extraction
    if belief_id.startswith("doi:") and extractions_dir:
        try:
            # Parse belief_id: doi:10.1234/doi:TBL-...:C001
            parts = belief_id.split(":")
            if len(parts) >= 2:
                doi = parts[1]  # e.g., "10.1234/doi"
                # Build extraction file path
                fname = doi.replace("/", "_")
                ext_path = extractions_dir / f"{fname}.json"

                if ext_path.exists():
                    with open(ext_path) as f:
                        ext_data = json.load(f)
                    findings = ext_data.get("findings", [])
                    if findings and len(findings) > 0:
                        # Return the first finding's consequent
                        # (in practice, we'd need to match the table/cell reference)
                        return findings[0].get("consequent")
        except Exception as e:
            logger.debug(f"Non-critical: {e}")

    return content if content else None


def backfill_belief_ids(
    web_db_path: Path,
    outcome_lookup: Dict[str, str],
    dry_run: bool = False,
    limit: Optional[int] = None,
    extractions_dir: Optional[Path] = None,
) -> Dict:
    """
    Main backfill process.

    Returns:
        Dict with statistics: beliefs_updated, coverage_before, coverage_after, sample_mappings
    """
    conn = sqlite3.connect(web_db_path)
    conn.row_factory = sqlite3.Row

    # Count baseline
    total_beliefs = conn.execute("SELECT COUNT(*) FROM beliefs").fetchone()[0]
    with_outcome_before = conn.execute(
        "SELECT COUNT(*) FROM beliefs WHERE outcome_id IS NOT NULL"
    ).fetchone()[0]
    with_env_before = conn.execute(
        "SELECT COUNT(*) FROM beliefs WHERE environment_id IS NOT NULL"
    ).fetchone()[0]

    logger.info(f"Baseline: {total_beliefs} total beliefs")
    logger.info(f"  - {with_outcome_before} ({100*with_outcome_before/max(1,total_beliefs):.1f}%) with outcome_id")
    logger.info(f"  - {with_env_before} ({100*with_env_before/max(1,total_beliefs):.1f}%) with environment_id")

    # Fetch beliefs (with limit for testing)
    query = "SELECT belief_id, content FROM beliefs WHERE outcome_id IS NULL OR environment_id IS NULL"
    if limit:
        query += f" LIMIT {limit}"

    cursor = conn.execute(query)
    beliefs_to_update = cursor.fetchall()
    logger.info(f"Found {len(beliefs_to_update)} beliefs to backfill")

    updated_count = 0
    outcome_id_assigned = 0
    env_id_assigned = 0
    sample_mappings = []

    for i, belief in enumerate(beliefs_to_update):
        belief_id = belief['belief_id']
        content = belief['content']

        # Extract consequent from content or original extraction
        consequent = extract_consequent_from_belief_content(belief_id, content, extractions_dir)

        # For beliefs from extractions without consequent in content,
        # we try to extract from belief_id or use content as proxy
        if not consequent and content:
            consequent = content.strip()[:200]  # Use first 200 chars as consequent

        # Map consequent to outcome_id
        outcome_id = None
        if consequent:
            outcome_id = find_best_outcome_id(consequent, outcome_lookup)

        # Create environment_id from belief_id pattern
        # For extraction-based beliefs: belief_id contains DOI and table/cell info
        env_id = hash_environment(belief_id)

        # Update database
        if not dry_run:
            try:
                conn.execute(
                    """UPDATE beliefs
                       SET outcome_id = ?, environment_id = ?, updated_at = ?
                       WHERE belief_id = ?""",
                    (outcome_id, env_id, datetime.now(timezone.utc).isoformat(), belief_id)
                )
                updated_count += 1
                if outcome_id:
                    outcome_id_assigned += 1
                if env_id:
                    env_id_assigned += 1
            except Exception as e:
                logger.warning(f"Failed to update {belief_id}: {e}")
                continue
        else:
            # Dry run: just count
            updated_count += 1
            if outcome_id:
                outcome_id_assigned += 1
            if env_id:
                env_id_assigned += 1

        # Collect sample for reporting
        if len(sample_mappings) < 10:
            sample_mappings.append({
                "belief_id": belief_id[:80],
                "consequent": (consequent[:60] + "...") if consequent and len(consequent) > 60 else consequent,
                "outcome_id": outcome_id,
                "env_id": env_id[:20]
            })

        if (i + 1) % 500 == 0:
            logger.info(f"Progress: {i+1}/{len(beliefs_to_update)} beliefs processed")

    if not dry_run:
        conn.commit()

    # Final counts
    if not dry_run:
        with_outcome_after = conn.execute(
            "SELECT COUNT(*) FROM beliefs WHERE outcome_id IS NOT NULL"
        ).fetchone()[0]
        with_env_after = conn.execute(
            "SELECT COUNT(*) FROM beliefs WHERE environment_id IS NOT NULL"
        ).fetchone()[0]
    else:
        with_outcome_after = with_outcome_before + outcome_id_assigned
        with_env_after = with_env_before + env_id_assigned

    conn.close()

    return {
        "total_beliefs": total_beliefs,
        "beliefs_updated": updated_count,
        "outcome_ids_assigned": outcome_id_assigned,
        "environment_ids_assigned": env_id_assigned,
        "coverage_outcome_before": with_outcome_before / max(1, total_beliefs),
        "coverage_outcome_after": with_outcome_after / max(1, total_beliefs),
        "coverage_env_before": with_env_before / max(1, total_beliefs),
        "coverage_env_after": with_env_after / max(1, total_beliefs),
        "sample_mappings": sample_mappings,
        "dry_run": dry_run,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--web-db",
        type=Path,
        default=get_web_db(),
        help="Path to WebOfBelief SQLite DB"
    )
    parser.add_argument(
        "--outcome-lookup",
        type=Path,
        default=Path("contracts/outcome_vocab/outcome_lookup.json"),
        help="Path to outcome_lookup.json"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Don't write to DB, just report"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit beliefs to process (for testing)"
    )

    args = parser.parse_args()

    # Validate inputs
    if not args.web_db.exists():
        logger.error(f"Database not found: {args.web_db}")
        return 1
    if not args.outcome_lookup.exists():
        logger.error(f"Outcome lookup not found: {args.outcome_lookup}")
        return 1

    logger.info(f"Starting backfill: web_db={args.web_db}, dry_run={args.dry_run}")

    # Load outcome vocabulary
    outcome_lookup = load_outcome_lookup(args.outcome_lookup)
    if not outcome_lookup:
        logger.warning("No outcome_lookup mappings loaded; outcome_id assignment may be limited")

    # Run backfill
    extractions_dir = PROJECT_ROOT / "data" / "extractions"
    results = backfill_belief_ids(
        args.web_db,
        outcome_lookup,
        dry_run=args.dry_run,
        limit=args.limit,
        extractions_dir=extractions_dir,
    )

    # Report results
    print("\n" + "=" * 70)
    print("  BELIEF ID BACKFILL RESULTS")
    print("=" * 70)
    print(f"  Total beliefs:              {results['total_beliefs']}")
    print(f"  Beliefs updated:            {results['beliefs_updated']}")
    print(f"  outcome_ids assigned:       {results['outcome_ids_assigned']}")
    print(f"  environment_ids assigned:   {results['environment_ids_assigned']}")
    print()
    print(f"  OUTCOME_ID Coverage:")
    print(f"    Before: {100*results['coverage_outcome_before']:.1f}% ({int(results['total_beliefs']*results['coverage_outcome_before'])} beliefs)")
    print(f"    After:  {100*results['coverage_outcome_after']:.1f}% ({int(results['total_beliefs']*results['coverage_outcome_after'])} beliefs)")
    print()
    print(f"  ENVIRONMENT_ID Coverage:")
    print(f"    Before: {100*results['coverage_env_before']:.1f}% ({int(results['total_beliefs']*results['coverage_env_before'])} beliefs)")
    print(f"    After:  {100*results['coverage_env_after']:.1f}% ({int(results['total_beliefs']*results['coverage_env_after'])} beliefs)")
    print()
    if results['sample_mappings']:
        print(f"  Sample Mappings (first 10):")
        for sample in results['sample_mappings']:
            print(f"    {sample['belief_id']}")
            print(f"      consequent: {sample['consequent']}")
            print(f"      outcome_id: {sample['outcome_id']}")
            print(f"      env_id: {sample['env_id']}")

    print()
    if results['dry_run']:
        print("  ⚠️  DRY RUN — No changes written to database")
    else:
        print("  ✓ Changes committed to database")
    print("=" * 70 + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
