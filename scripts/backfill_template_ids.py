#!/usr/bin/env python3
"""
Backfill template_ids column in beliefs table for AESHI template coverage.

This script:
1. Loads all templates from data/templates/*.json
2. Loads all beliefs from web_persistence.db
3. Runs template resolution scoring for each belief
4. Updates beliefs.template_ids with JSON array of display_ids

The template_ids column is what AESHI's _check_template_belief_coverage() checks.
This column should contain a JSON array of template display_ids (e.g., ["CREA4", "AX1"]).

Usage:
    python scripts/backfill_template_ids.py [--dry-run] [--min-score 0.35] [--top-k 5]
"""

import argparse
import json
import logging
import sqlite3
import sys
from pathlib import Path
from datetime import datetime, timezone

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.finding_template_relevance import (
    load_findings_from_web_db,
    load_template_profiles,
    resolve_finding,
    ResolverConfig,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def backfill_template_ids(
    db_path: Path,
    templates_dir: Path,
    min_score: float = 0.35,
    top_k: int = 5,
    dry_run: bool = False,
) -> dict:
    """
    Backfill template_ids column in beliefs table.

    Returns dict with statistics about the backfill operation.
    """
    logger.info(f"Loading templates from {templates_dir}")
    templates = load_template_profiles(templates_dir)
    logger.info(f"  Loaded {len(templates)} templates")

    logger.info(f"Loading beliefs from {db_path}")
    findings = load_findings_from_web_db(db_path)
    logger.info(f"  Loaded {len(findings)} beliefs")

    # Configure resolver
    config = ResolverConfig(
        min_template_score=min_score,
        top_k_templates=top_k,
        min_tier_support_score=0.45,
    )

    # Process all beliefs
    stats = {
        "total_beliefs": len(findings),
        "beliefs_with_templates": 0,
        "beliefs_without_templates": 0,
        "total_template_links": 0,
        "updated": 0,
        "errors": 0,
    }

    # Collect updates
    updates = []  # list of (belief_id, template_ids_json)

    logger.info(f"Resolving templates for {len(findings)} beliefs (min_score={min_score}, top_k={top_k})...")

    for i, finding in enumerate(findings):
        if (i + 1) % 500 == 0:
            logger.info(f"  Progress: {i + 1}/{len(findings)} beliefs processed")

        try:
            resolution = resolve_finding(finding, templates, config)

            if resolution.top_templates:
                # Get display_ids for top templates
                display_ids = [t["display_id"] for t in resolution.top_templates]
                template_ids_json = json.dumps(display_ids, sort_keys=True)

                updates.append((finding.belief_id, template_ids_json))
                stats["beliefs_with_templates"] += 1
                stats["total_template_links"] += len(display_ids)
            else:
                updates.append((finding.belief_id, None))  # Clear any existing value
                stats["beliefs_without_templates"] += 1

        except Exception as e:
            logger.warning(f"  Error resolving belief {finding.belief_id}: {e}")
            stats["errors"] += 1

    logger.info(f"Resolution complete. {stats['beliefs_with_templates']}/{stats['total_beliefs']} beliefs have template matches")

    if dry_run:
        logger.info("DRY RUN - no database changes made")
        # Show sample updates
        sample_with = [u for u in updates if u[1] is not None][:5]
        if sample_with:
            logger.info("Sample updates (with templates):")
            for belief_id, template_ids in sample_with:
                logger.info(f"  {belief_id}: {template_ids}")
        return stats

    # Apply updates to database
    logger.info(f"Updating {len(updates)} beliefs in database...")

    conn = sqlite3.connect(str(db_path))
    try:
        cur = conn.cursor()

        # Check if template_ids column exists
        cur.execute("PRAGMA table_info(beliefs)")
        cols = {row[1] for row in cur.fetchall()}

        if "template_ids" not in cols:
            logger.info("Adding template_ids column to beliefs table")
            cur.execute("ALTER TABLE beliefs ADD COLUMN template_ids TEXT")

        # Batch update
        now_iso = datetime.now(timezone.utc).isoformat()
        has_updated_at = "updated_at" in cols

        for belief_id, template_ids_json in updates:
            try:
                if has_updated_at:
                    cur.execute(
                        "UPDATE beliefs SET template_ids = ?, updated_at = ? WHERE belief_id = ?",
                        (template_ids_json, now_iso, belief_id),
                    )
                else:
                    cur.execute(
                        "UPDATE beliefs SET template_ids = ? WHERE belief_id = ?",
                        (template_ids_json, belief_id),
                    )
                stats["updated"] += 1
            except Exception as e:
                logger.warning(f"  Error updating belief {belief_id}: {e}")
                stats["errors"] += 1

        conn.commit()
        logger.info(f"Successfully updated {stats['updated']} beliefs")

    finally:
        conn.close()

    return stats


def verify_coverage(db_path: Path) -> dict:
    """Verify template coverage after backfill."""
    conn = sqlite3.connect(str(db_path))
    try:
        cur = conn.cursor()

        # Total beliefs
        cur.execute("SELECT COUNT(*) FROM beliefs")
        total = cur.fetchone()[0]

        # Beliefs with template_ids
        cur.execute(
            "SELECT COUNT(*) FROM beliefs WHERE template_ids IS NOT NULL AND template_ids != ''"
        )
        with_templates = cur.fetchone()[0]

        # Sample of template_ids values
        cur.execute(
            "SELECT belief_id, template_ids FROM beliefs WHERE template_ids IS NOT NULL AND template_ids != '' LIMIT 5"
        )
        samples = cur.fetchall()

        return {
            "total_beliefs": total,
            "beliefs_with_template_ids": with_templates,
            "coverage_pct": round(100 * with_templates / total, 2) if total > 0 else 0,
            "samples": samples,
        }
    finally:
        conn.close()


def main():
    parser = argparse.ArgumentParser(description="Backfill template_ids in beliefs table")
    parser.add_argument(
        "--db-path",
        type=Path,
        default=Path("data/web_persistence.db"),
        help="Path to web_persistence.db",
    )
    parser.add_argument(
        "--templates-dir",
        type=Path,
        default=Path("data/templates"),
        help="Path to templates directory",
    )
    parser.add_argument(
        "--min-score",
        type=float,
        default=0.35,
        help="Minimum template relevance score (default: 0.35)",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=5,
        help="Maximum templates per belief (default: 5)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without making database changes",
    )

    args = parser.parse_args()

    # Validate paths
    if not args.db_path.exists():
        logger.error(f"Database not found: {args.db_path}")
        sys.exit(1)

    if not args.templates_dir.exists():
        logger.error(f"Templates directory not found: {args.templates_dir}")
        sys.exit(1)

    # Run backfill
    logger.info("=" * 60)
    logger.info("TEMPLATE_IDS BACKFILL FOR AESHI COVERAGE")
    logger.info("=" * 60)

    stats = backfill_template_ids(
        db_path=args.db_path,
        templates_dir=args.templates_dir,
        min_score=args.min_score,
        top_k=args.top_k,
        dry_run=args.dry_run,
    )

    logger.info("-" * 60)
    logger.info("BACKFILL STATISTICS:")
    for key, value in stats.items():
        logger.info(f"  {key}: {value}")

    if not args.dry_run:
        # Verify coverage
        logger.info("-" * 60)
        logger.info("VERIFICATION:")
        coverage = verify_coverage(args.db_path)
        logger.info(f"  Total beliefs: {coverage['total_beliefs']}")
        logger.info(f"  With template_ids: {coverage['beliefs_with_template_ids']}")
        logger.info(f"  Coverage: {coverage['coverage_pct']}%")

        if coverage['samples']:
            logger.info("  Sample entries:")
            for belief_id, template_ids in coverage['samples']:
                logger.info(f"    {belief_id}: {template_ids}")

    logger.info("=" * 60)
    logger.info("DONE")

    # Return coverage percentage for AESHI improvement tracking
    if not args.dry_run:
        return coverage['coverage_pct']
    return 0


if __name__ == "__main__":
    main()
