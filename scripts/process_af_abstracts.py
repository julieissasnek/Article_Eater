#!/usr/bin/env python3
"""
Process Abstracts from Article Finder Database
==============================================

Reads papers from the Article Finder database and extracts rules
using the Article Essence Extraction pipeline.

Usage:
    python scripts/process_af_abstracts.py --limit 10 --topic neuroarchitecture
    python scripts/process_af_abstracts.py --category BIOPHILIC --limit 20
    python scripts/process_af_abstracts.py --dry-run  # Show what would be processed

Author: Claude Code
Created: 2026-02-11
"""

import argparse
import json
import logging
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.services.db_locator import resolve_article_finder_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Article Finder database path (resolved at runtime)
def get_af_connection(af_db_path: Path | None = None) -> sqlite3.Connection:
    """Connect to Article Finder database."""
    resolved_db = resolve_article_finder_db(af_db_path)
    if not resolved_db.exists():
        raise FileNotFoundError(f"Article Finder database not found: {resolved_db}")
    conn = sqlite3.connect(resolved_db)
    conn.row_factory = sqlite3.Row
    return conn


def get_papers_for_extraction(
    conn: sqlite3.Connection,
    limit: int = 10,
    category: Optional[str] = None,
    min_triage_score: float = 0.5,
    exclude_processed: bool = True,
) -> List[Dict[str, Any]]:
    """
    Get papers ready for extraction.

    Selection criteria (per contract):
    - triage_decision = 'send_to_eater'
    - Has abstract > 200 chars
    - Optionally filtered by topic_category
    - Optionally exclude already processed (ae_status = 'SUCCESS')
    """
    query = """
    SELECT
        paper_id,
        doi,
        title,
        authors,
        year,
        venue,
        abstract,
        pdf_path,
        triage_score,
        topic_category,
        ae_status
    FROM papers
    WHERE triage_decision = 'send_to_eater'
      AND abstract IS NOT NULL
      AND LENGTH(abstract) > 200
      AND triage_score >= ?
      AND (off_topic_flag IS NULL OR off_topic_flag = 0)
    """
    params = [min_triage_score]

    if category:
        query += " AND topic_category = ?"
        params.append(category)

    if exclude_processed:
        query += " AND (ae_status IS NULL OR ae_status != 'SUCCESS')"

    query += " ORDER BY triage_score DESC LIMIT ?"
    params.append(limit)

    cursor = conn.execute(query, params)
    return [dict(row) for row in cursor.fetchall()]


def extract_rules_from_abstract(
    abstract: str,
    paper_id: str,
    topic: str = "neuroarchitecture",
) -> List[Dict[str, Any]]:
    """
    Extract findings/rules from an abstract using Article Essence Extraction.

    Returns list of finding dictionaries.
    """
    try:
        from app.services.extract_article_essence import extract_findings_from_text
        findings = extract_findings_from_text(abstract, topic=topic)
        return findings
    except Exception as e:
        logger.error(f"Extraction failed for {paper_id}: {e}")
        return []


def update_paper_status(
    conn: sqlite3.Connection,
    paper_id: str,
    status: str,
    n_claims: int = 0,
    n_rules: int = 0,
) -> None:
    """Update paper's AE status in AF database."""
    conn.execute("""
        UPDATE papers
        SET ae_status = ?,
            ae_n_claims = ?,
            ae_n_rules = ?,
            updated_at = ?
        WHERE paper_id = ?
    """, (status, n_claims, n_rules, datetime.now().isoformat(), paper_id))
    conn.commit()


def save_findings_to_jsonl(
    findings: List[Dict[str, Any]],
    paper_id: str,
    output_dir: Path,
) -> Path:
    """Save findings to JSONL file."""
    output_dir.mkdir(parents=True, exist_ok=True)
    safe_id = paper_id.replace("/", "_").replace(":", "_")[:50]
    output_path = output_dir / f"{safe_id}_findings.jsonl"

    with open(output_path, "w") as f:
        for finding in findings:
            finding["paper_id"] = paper_id
            finding["extracted_at"] = datetime.now().isoformat()
            f.write(json.dumps(finding) + "\n")

    return output_path


def process_papers(
    limit: int = 10,
    topic: str = "neuroarchitecture",
    category: Optional[str] = None,
    output_dir: Optional[Path] = None,
    af_db_path: Optional[Path] = None,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """
    Main processing function.

    Returns summary of processing results.
    """
    output_dir = output_dir or PROJECT_ROOT / "data" / "extracted_findings"

    conn = get_af_connection(af_db_path)
    papers = get_papers_for_extraction(conn, limit=limit, category=category)

    logger.info(f"Found {len(papers)} papers ready for extraction")

    if dry_run:
        logger.info("DRY RUN - would process:")
        for p in papers:
            logger.info(f"  - {p['paper_id']}: {p['title'][:60]}...")
        return {"dry_run": True, "papers_found": len(papers)}

    results = {
        "processed": 0,
        "succeeded": 0,
        "failed": 0,
        "total_findings": 0,
        "papers": [],
    }

    for i, paper in enumerate(papers):
        paper_id = paper["paper_id"]
        title = paper["title"][:60]
        logger.info(f"[{i+1}/{len(papers)}] Processing: {paper_id}")
        logger.info(f"  Title: {title}...")

        try:
            findings = extract_rules_from_abstract(
                abstract=paper["abstract"],
                paper_id=paper_id,
                topic=topic,
            )

            n_findings = len(findings)
            logger.info(f"  Extracted {n_findings} findings")

            if findings:
                output_path = save_findings_to_jsonl(findings, paper_id, output_dir)
                logger.info(f"  Saved to: {output_path}")

                update_paper_status(conn, paper_id, "SUCCESS", n_claims=n_findings)
                results["succeeded"] += 1
                results["total_findings"] += n_findings
            else:
                update_paper_status(conn, paper_id, "NO_FINDINGS")
                results["succeeded"] += 1  # Not a failure, just no findings

            results["papers"].append({
                "paper_id": paper_id,
                "status": "SUCCESS",
                "findings": n_findings,
            })

        except Exception as e:
            logger.error(f"  FAILED: {e}")
            update_paper_status(conn, paper_id, "FAIL")
            results["failed"] += 1
            results["papers"].append({
                "paper_id": paper_id,
                "status": "FAIL",
                "error": str(e),
            })

        results["processed"] += 1

    conn.close()

    # Log summary
    logger.info("=" * 60)
    logger.info("PROCESSING COMPLETE")
    logger.info(f"  Processed: {results['processed']}")
    logger.info(f"  Succeeded: {results['succeeded']}")
    logger.info(f"  Failed: {results['failed']}")
    logger.info(f"  Total findings: {results['total_findings']}")
    logger.info("=" * 60)

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Process abstracts from Article Finder database"
    )
    parser.add_argument(
        "--af-db",
        type=Path,
        default=None,
        help="Path to article_finder.db (auto-resolved if omitted)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Maximum papers to process (default: 10)",
    )
    parser.add_argument(
        "--topic",
        type=str,
        default="neuroarchitecture",
        help="Target topic for extraction (default: neuroarchitecture)",
    )
    parser.add_argument(
        "--category",
        type=str,
        help="Filter by topic_category (e.g., BIOPHILIC, ACOUSTIC, LIGHT)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output directory for findings",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be processed without doing extraction",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose logging",
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    results = process_papers(
        limit=args.limit,
        topic=args.topic,
        category=args.category,
        output_dir=args.output,
        af_db_path=args.af_db,
        dry_run=args.dry_run,
    )

    # Exit with error code if any failures
    if results.get("failed", 0) > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
