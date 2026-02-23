#!/usr/bin/env python3
"""
Load extraction CSV to database findings table.

This script loads data from the extraction pipeline CSV (realtime_pdf_confirmed_rows.csv)
into the findings table in ae.db. This addresses the critical gap identified in the
Feb 22, 2026 system audit: beliefs table is empty because extracted claims aren't
being persisted to the database.

Usage:
    python scripts/load_extraction_csv_to_db.py --dry-run  # Preview without writing
    python scripts/load_extraction_csv_to_db.py            # Actually load to DB

Author: Claude Code (Feb 22, 2026)
Audit Reference: SYSTEM_AUDIT_REPORT_Feb22_2026.md, Appendix C.1
"""

import argparse
import pandas as pd
from pathlib import Path
from datetime import datetime, timezone
import sqlite3
import sys


# Paths
PROJECT_ROOT = Path(__file__).parent.parent
CSV_PATH = PROJECT_ROOT / "data" / "production" / "realtime_pdf_confirmed_rows.csv"
DB_PATH = PROJECT_ROOT / "ae.db"


def get_csv_to_findings_mapping():
    """
    Define the column mapping from CSV to findings table schema.

    CSV columns available:
        paper_id, claim_id, claim_type, node_id, statement, ae_confidence,
        node_type, article_type_family, effect_direction, source_section,
        source_page_start, source_page_end, source_quote, confidence, etc.

    Findings table schema:
        id (auto), finding_level, consequent, antecedents, operational_measure,
        measure_type, measure_direction, p_value, effect_size, sample_size,
        job_id, paper_id, created_at, effect_size_type, ci_lower, ci_upper
    """
    return {
        'paper_id': 'paper_id',
        'claim_type': 'finding_level',
        'statement': 'consequent',
        'environment_variable': 'antecedents',
        'outcome_variable': 'operational_measure',
        'node_type': 'measure_type',
        'effect_direction': 'measure_direction',
        'ae_confidence': 'effect_size',  # Using confidence as proxy
        'claim_id': 'job_id',  # Track original claim_id
    }


def load_and_transform_csv(csv_path: Path, verbose: bool = False) -> pd.DataFrame:
    """Load CSV and transform to findings schema."""

    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    df = pd.read_csv(csv_path, low_memory=False)

    if verbose:
        print(f"Loaded {len(df)} rows from {csv_path.name}")
        print(f"Columns: {list(df.columns)[:10]}... ({len(df.columns)} total)")

    # Get mapping
    mapping = get_csv_to_findings_mapping()

    # Create findings dataframe with mapped columns
    findings_df = pd.DataFrame()

    for csv_col, db_col in mapping.items():
        if csv_col in df.columns:
            findings_df[db_col] = df[csv_col]
        else:
            findings_df[db_col] = None
            if verbose:
                print(f"  Warning: CSV column '{csv_col}' not found, setting {db_col} to NULL")

    # Add timestamp
    findings_df['created_at'] = datetime.now(timezone.utc).isoformat()

    # Fill missing columns with defaults
    for col in ['p_value', 'sample_size', 'effect_size_type', 'ci_lower', 'ci_upper']:
        if col not in findings_df.columns:
            findings_df[col] = None

    # Clean up: remove rows with no statement/consequent
    initial_count = len(findings_df)
    findings_df = findings_df.dropna(subset=['consequent'])
    findings_df = findings_df[findings_df['consequent'].str.strip() != '']

    if verbose:
        print(f"  Filtered to {len(findings_df)} rows with valid consequent (from {initial_count})")

    return findings_df


def get_existing_job_ids(db_path: Path) -> set:
    """Get job_ids already in the database to avoid duplicates."""
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.execute("SELECT DISTINCT job_id FROM findings WHERE job_id IS NOT NULL")
        return {row[0] for row in cursor.fetchall()}
    except sqlite3.OperationalError:
        return set()
    finally:
        conn.close()


def load_to_database(findings_df: pd.DataFrame, db_path: Path, dry_run: bool = False) -> int:
    """Load findings dataframe to database."""

    # Check for duplicates
    existing_ids = get_existing_job_ids(db_path)
    if existing_ids and 'job_id' in findings_df.columns:
        before_count = len(findings_df)
        findings_df = findings_df[~findings_df['job_id'].isin(existing_ids)]
        if before_count != len(findings_df):
            print(f"  Skipping {before_count - len(findings_df)} duplicate job_ids")

    if len(findings_df) == 0:
        print("No new rows to load.")
        return 0

    if dry_run:
        print(f"\n[DRY RUN] Would load {len(findings_df)} rows to findings table")
        print(f"\nSample of data to be loaded:")
        print(findings_df[['paper_id', 'finding_level', 'consequent']].head(5).to_string())
        print(f"\nColumns: {list(findings_df.columns)}")
        return len(findings_df)

    # Actually load
    conn = sqlite3.connect(db_path)
    try:
        findings_df.to_sql('findings', conn, if_exists='append', index=False)
        conn.commit()
        print(f"Successfully loaded {len(findings_df)} findings to database")
        return len(findings_df)
    finally:
        conn.close()


def verify_load(db_path: Path):
    """Verify the load by counting findings."""
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.execute("SELECT COUNT(*) FROM findings")
        count = cursor.fetchone()[0]
        print(f"\nDatabase now contains {count} total findings")

        # Show recent additions
        cursor = conn.execute(
            "SELECT paper_id, finding_level, substr(consequent, 1, 60) "
            "FROM findings ORDER BY id DESC LIMIT 5"
        )
        print("\nMost recent findings:")
        for row in cursor.fetchall():
            print(f"  {row[0]}: [{row[1]}] {row[2]}...")
    finally:
        conn.close()


def main():
    parser = argparse.ArgumentParser(
        description="Load extraction CSV to database findings table"
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview what would be loaded without writing to database'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed progress'
    )
    parser.add_argument(
        '--csv',
        type=Path,
        default=CSV_PATH,
        help=f'Path to CSV file (default: {CSV_PATH})'
    )
    parser.add_argument(
        '--db',
        type=Path,
        default=DB_PATH,
        help=f'Path to database (default: {DB_PATH})'
    )

    args = parser.parse_args()

    print(f"CSV→DB Loader")
    print(f"=" * 50)
    print(f"CSV: {args.csv}")
    print(f"DB:  {args.db}")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
    print()

    try:
        # Load and transform
        findings_df = load_and_transform_csv(args.csv, verbose=args.verbose)

        # Load to database
        loaded_count = load_to_database(findings_df, args.db, dry_run=args.dry_run)

        # Verify (only if not dry run)
        if not args.dry_run and loaded_count > 0:
            verify_load(args.db)

        print(f"\nDone. Loaded {loaded_count} rows.")
        return 0

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        raise


if __name__ == "__main__":
    sys.exit(main())
