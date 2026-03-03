#!/usr/bin/env python3
"""
Improve theory_id backfill in web_persistence_v2.db

PROBLEM:
- 3,420 beliefs in web_persistence_v2.db have theory_id backfilled
- 99.3% (3,395) were assigned "PP" as a default because mapping wasn't done properly
- Only 25 beliefs have correct non-PP theory_ids

SOLUTION:
1. Use tag_assignments table (theoretical tags) to infer theory_id
2. Each belief may have multiple tags with confidence scores
3. Pick highest-confidence tag as the primary theory_id
4. Fall back to finding_template_theory_links.json if no tags
5. Only use PP as absolute last resort

APPROACH:
- For each belief in beliefs table:
  a. Check tag_assignments table for theoretical tags with highest confidence
  b. If found, use that as theory_id
  c. If not found, use existing theory_id (which might be PP)
  d. Report before/after distribution

MODES:
- --dry-run (default): Show what would change without modifying DB
- --commit: Actually update the database

AUTHOR: Claude Code
DATE: 2026-03-02
"""

import sqlite3
import json
import argparse
from collections import defaultdict
from pathlib import Path


def load_tier1_frameworks():
    """Load T1 framework abbreviations."""
    with open('schemas/theory/tier1_frameworks.json', 'r') as f:
        data = json.load(f)

    frameworks = {}
    for key, framework in data.get('frameworks', {}).items():
        abbr = framework.get('abbreviation')
        if abbr:
            frameworks[abbr] = {
                'name': framework.get('name'),
                'aliases': framework.get('aliases', [])
            }

    return frameworks


def load_finding_template_links():
    """Load finding_template_theory_links.json for fallback mapping."""
    with open('data/production/finding_template_theory_links.json', 'r') as f:
        data = json.load(f)

    # Build a map of belief_id -> best tier1 theory
    belief_theory_map = {}
    for resolution in data.get('resolutions', []):
        belief_id = resolution.get('belief_id')
        tier1_relevance = resolution.get('tier1_relevance', {})

        if belief_id and tier1_relevance:
            # Get highest-scoring theory
            best_theory = max(tier1_relevance.items(), key=lambda x: x[1])
            belief_theory_map[belief_id] = best_theory[0]

    return belief_theory_map


def get_best_theory_from_tags(cursor, belief_id, tier1_abbrs):
    """
    Get the highest-confidence theoretical tag for a belief.

    Args:
        cursor: SQLite cursor
        belief_id: The belief ID
        tier1_abbrs: Set of valid T1 framework abbreviations

    Returns:
        (theory_id, confidence) or (None, 0.0)
    """
    cursor.execute("""
        SELECT tag_value, confidence
        FROM tag_assignments
        WHERE belief_id = ? AND tag_dimension = 'theoretical'
        ORDER BY confidence DESC
        LIMIT 100
    """, (belief_id,))

    tags = cursor.fetchall()

    # Find the first tag that's a valid T1 framework
    for tag_value, confidence in tags:
        if tag_value in tier1_abbrs:
            return tag_value, confidence

    # No valid T1 framework tag found
    return None, 0.0


def improve_backfill(database_path, dry_run=True):
    """
    Improve theory_id backfill for all beliefs.

    Args:
        database_path: Path to web_persistence_v2.db
        dry_run: If True, only show what would change

    Returns:
        dict with statistics
    """
    # Load frameworks
    tier1_frameworks = load_tier1_frameworks()
    tier1_abbrs = set(tier1_frameworks.keys())

    print(f"Loaded {len(tier1_abbrs)} T1 frameworks: {sorted(tier1_abbrs)}")

    # Load fallback mapping
    belief_theory_map = load_finding_template_links()
    print(f"Loaded finding_template_theory_links with {len(belief_theory_map)} belief mappings")

    # Connect to database
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # Get all beliefs
    cursor.execute("""
        SELECT belief_id, theory_id
        FROM beliefs
        ORDER BY belief_id
    """)

    beliefs = cursor.fetchall()
    print(f"\nProcessing {len(beliefs)} beliefs...")

    # Statistics
    stats = {
        'total': len(beliefs),
        'unchanged': 0,
        'updated_from_tags': 0,
        'updated_from_links': 0,
        'kept_as_pp': 0,
        'before_distribution': defaultdict(int),
        'after_distribution': defaultdict(int),
        'changes': []
    }

    # Collect changes
    updates = []

    for belief_id, old_theory_id in beliefs:
        # Record before
        stats['before_distribution'][old_theory_id] += 1

        # Try to find best theory
        new_theory_id = old_theory_id  # Default to current
        source = 'unchanged'
        confidence = 0.0

        # Strategy 1: Check tags (highest confidence)
        tag_theory, tag_conf = get_best_theory_from_tags(cursor, belief_id, tier1_abbrs)
        if tag_theory:
            new_theory_id = tag_theory
            source = 'from_tags'
            confidence = tag_conf

        # Strategy 2: Fall back to finding_template_theory_links
        elif belief_id in belief_theory_map:
            new_theory_id = belief_theory_map[belief_id]
            source = 'from_links'

        # Strategy 3: Keep existing (might be PP)
        else:
            if old_theory_id == 'PP':
                source = 'kept_as_pp'
            # else: already set to old_theory_id

        # Record after
        stats['after_distribution'][new_theory_id] += 1

        # Track change
        if new_theory_id != old_theory_id:
            stats['updated_' + source] += 1
            updates.append({
                'belief_id': belief_id,
                'old_theory_id': old_theory_id,
                'new_theory_id': new_theory_id,
                'source': source,
                'confidence': confidence
            })
        else:
            stats['unchanged'] += 1

    # Print before/after distribution
    print("\n=== BEFORE (Current State) ===")
    for theory_id in sorted(stats['before_distribution'].keys()):
        count = stats['before_distribution'][theory_id]
        pct = 100.0 * count / stats['total']
        print(f"  {theory_id:15} {count:5d} ({pct:6.2f}%)")

    print("\n=== AFTER (Improved State) ===")
    for theory_id in sorted(stats['after_distribution'].keys()):
        count = stats['after_distribution'][theory_id]
        pct = 100.0 * count / stats['total']
        print(f"  {theory_id:15} {count:5d} ({pct:6.2f}%)")

    print("\n=== CHANGES SUMMARY ===")
    print(f"  Total beliefs: {stats['total']}")
    print(f"  Unchanged: {stats['unchanged']}")
    print(f"  Updated from tags: {stats['updated_from_tags']}")
    print(f"  Updated from links: {stats['updated_from_links']}")
    print(f"  Kept as PP (no mapping found): {stats['kept_as_pp']}")

    print("\n=== TOP 10 CHANGES (by theory transition) ===")
    # Group changes by old->new transition
    transitions = defaultdict(int)
    for change in updates:
        transition = f"{change['old_theory_id']} → {change['new_theory_id']}"
        transitions[transition] += 1

    for transition, count in sorted(transitions.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {transition:25} {count:5d} beliefs")

    # Apply updates if not dry-run
    if not dry_run and updates:
        print(f"\n=== COMMITTING {len(updates)} UPDATES ===")
        for change in updates:
            cursor.execute("""
                UPDATE beliefs
                SET theory_id = ?, updated_at = datetime('now')
                WHERE belief_id = ?
            """, (change['new_theory_id'], change['belief_id']))

        conn.commit()
        print(f"Updated {len(updates)} beliefs")
    elif dry_run and updates:
        print(f"\n[DRY-RUN MODE] Would update {len(updates)} beliefs")
        print("Run with --commit to apply changes")

    # Sample some changes
    if updates:
        print(f"\n=== SAMPLE CHANGES ===")
        for change in updates[:5]:
            print(f"  {change['belief_id']:50}")
            print(f"    {change['old_theory_id']} → {change['new_theory_id']:12} (source: {change['source']}, conf: {change['confidence']:.2f})")

    conn.close()
    return stats


def main():
    parser = argparse.ArgumentParser(
        description='Improve theory_id backfill in beliefs database'
    )
    parser.add_argument(
        '--database',
        default='data/web_persistence_v2.db',
        help='Path to database (default: data/web_persistence_v2.db)'
    )
    parser.add_argument(
        '--commit',
        action='store_true',
        help='Actually update the database (default is dry-run)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        default=True,
        help='Show what would change without modifying DB (default)'
    )

    args = parser.parse_args()

    # Handle conflicting flags
    if args.commit and args.dry_run:
        args.dry_run = False  # --commit takes precedence

    print(f"Database: {args.database}")
    print(f"Mode: {'DRY-RUN' if args.dry_run else 'COMMIT'}")
    print()

    stats = improve_backfill(args.database, dry_run=args.dry_run)

    if args.dry_run:
        print("\n[DRY-RUN COMPLETE] No changes made to database")


if __name__ == '__main__':
    main()
