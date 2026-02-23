#!/usr/bin/env python3
"""
Backfill realtime PDF completion queue with AF papers that have PDFs but are missing from queue.

This addresses corpus coverage drift where only incrementally ingested papers were queued
for PDF completion and historical papers with valid PDF paths were never enqueued.
"""

from __future__ import annotations

import argparse
import csv
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.services.db_locator import resolve_article_finder_db

DEFAULT_QUEUE_CSV = Path("data/production/realtime_pdf_completion_queue.csv")


def now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Backfill missing PDF papers into completion queue.")
    p.add_argument("--af-db", type=Path, default=None, help="Path to article_finder.db (auto-resolved if omitted)")
    p.add_argument(
        "--queue-csv",
        type=Path,
        default=DEFAULT_QUEUE_CSV,
        help="Path to realtime_pdf_completion_queue.csv",
    )
    p.add_argument(
        "--status",
        default="queued_pdf_backfill",
        help="Queue status value for newly enqueued rows",
    )
    p.add_argument(
        "--reason",
        default="ag9_corpus_quality_backfill",
        help="Reason value for newly enqueued rows",
    )
    p.add_argument(
        "--source",
        default="backfill_pdf_completion_queue",
        help="Source value for newly enqueued rows",
    )
    p.add_argument(
        "--require-existing-pdf-file",
        action="store_true",
        help="Only enqueue rows whose pdf_path exists on disk now",
    )
    p.add_argument(
        "--min-abstract-len",
        type=int,
        default=0,
        help="Optional abstract length floor (0 disables)",
    )
    p.add_argument("--max-add", type=int, default=0, help="Optional cap on number of rows to enqueue (0 = no cap)")
    p.add_argument("--dry-run", action="store_true", help="Report changes only")
    return p.parse_args()


def read_queue(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_queue(path: Path, rows: List[Dict[str, Any]]) -> None:
    fieldnames = set()
    for row in rows:
        fieldnames.update(row.keys())

    ordered = [
        "paper_id",
        "doi",
        "title",
        "year",
        "venue",
        "pdf_path",
        "status",
        "queued_at",
        "processed_at",
        "reason",
        "source",
        "resolved_pdf_path",
        "n_tables",
        "n_claims",
        "error",
    ]
    for key in sorted(fieldnames):
        if key not in ordered:
            ordered.append(key)

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=ordered)
        w.writeheader()
        w.writerows(rows)


def fetch_pdf_papers(db_path: Path, min_abstract_len: int) -> List[Dict[str, Any]]:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.cursor()
        where_parts = ["pdf_path IS NOT NULL", "TRIM(pdf_path) != ''"]
        params: List[Any] = []
        if min_abstract_len > 0:
            where_parts.append("abstract IS NOT NULL")
            where_parts.append("LENGTH(TRIM(abstract)) >= ?")
            params.append(min_abstract_len)
        where_sql = " AND ".join(where_parts)
        query = f"""
            SELECT
                paper_id,
                COALESCE(doi, '') AS doi,
                COALESCE(title, '') AS title,
                COALESCE(year, '') AS year,
                COALESCE(venue, '') AS venue,
                COALESCE(pdf_path, '') AS pdf_path
            FROM papers
            WHERE {where_sql}
            ORDER BY paper_id ASC
        """
        cur.execute(query, params)
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()


def main() -> int:
    args = parse_args()
    args.af_db = resolve_article_finder_db(args.af_db)
    print(f"[backfill_pdf_completion_queue] using af_db={args.af_db}")
    queue_rows = read_queue(args.queue_csv)
    existing_ids = {str(r.get("paper_id", "")).strip() for r in queue_rows if str(r.get("paper_id", "")).strip()}

    af_rows = fetch_pdf_papers(args.af_db, args.min_abstract_len)

    added: List[Dict[str, Any]] = []
    skipped_missing_file = 0
    for row in af_rows:
        paper_id = str(row.get("paper_id", "")).strip()
        if not paper_id or paper_id in existing_ids:
            continue

        pdf_path = str(row.get("pdf_path", "")).strip()
        if args.require_existing_pdf_file and (not pdf_path or not Path(pdf_path).exists()):
            skipped_missing_file += 1
            continue

        new_row = {
            "paper_id": paper_id,
            "doi": str(row.get("doi", "")).strip(),
            "title": str(row.get("title", "")).strip(),
            "year": str(row.get("year", "")).strip(),
            "venue": str(row.get("venue", "")).strip(),
            "pdf_path": pdf_path,
            "status": args.status,
            "queued_at": now_iso(),
            "processed_at": "",
            "reason": args.reason,
            "source": args.source,
            "resolved_pdf_path": "",
            "n_tables": "",
            "n_claims": "",
            "error": "",
        }
        added.append(new_row)
        if args.max_add > 0 and len(added) >= args.max_add:
            break

    print(f"AF PDF papers scanned: {len(af_rows)}")
    print(f"Queue rows existing: {len(queue_rows)}")
    print(f"Papers already queued: {len(existing_ids)}")
    print(f"Rows to add: {len(added)}")
    if args.require_existing_pdf_file:
        print(f"Skipped missing pdf files: {skipped_missing_file}")

    if args.dry_run:
        return 0

    if not added:
        print("No rows added.")
        return 0

    queue_rows.extend(added)
    write_queue(args.queue_csv, queue_rows)
    print(f"Wrote queue: {args.queue_csv} (total rows now {len(queue_rows)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
