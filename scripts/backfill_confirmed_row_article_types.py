#!/usr/bin/env python3
"""
Backfill article-type metadata in realtime_pdf_confirmed_rows.csv from queue CSV.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Dict, List


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Backfill confirmed-row article-type metadata.")
    parser.add_argument(
        "--queue-csv",
        default="data/production/realtime_pdf_completion_queue.csv",
        help="Queue CSV with canonical article_type metadata",
    )
    parser.add_argument(
        "--confirmed-csv",
        default="data/production/realtime_pdf_confirmed_rows.csv",
        help="Confirmed rows CSV to backfill",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Compute stats only without writing file",
    )
    return parser.parse_args()


def read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: List[Dict[str, str]]) -> None:
    fieldnames: List[str] = []
    seen = set()
    for row in rows:
        for key in row.keys():
            if key not in seen:
                seen.add(key)
                fieldnames.append(key)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    args = parse_args()
    queue_path = Path(args.queue_csv)
    confirmed_path = Path(args.confirmed_csv)
    if not queue_path.exists():
        print(f"Queue CSV not found: {queue_path}")
        return 1
    if not confirmed_path.exists():
        print(f"Confirmed CSV not found: {confirmed_path}")
        return 1

    queue_rows = read_csv(queue_path)
    confirmed_rows = read_csv(confirmed_path)

    queue_index: Dict[str, Dict[str, str]] = {}
    for row in queue_rows:
        pid = str(row.get("paper_id", "")).strip()
        if pid:
            queue_index[pid] = row

    target_fields = [
        "article_type_family",
        "article_type_predicted_family",
        "article_type_confidence",
        "article_type_runner_up",
        "article_type_margin",
        "article_type_needs_review",
        "article_type_signals",
        "article_type_diagnostics",
        "article_type_classifier_version",
    ]

    updated_rows = 0
    missing_paper = 0
    for row in confirmed_rows:
        pid = str(row.get("paper_id", "")).strip()
        if not pid:
            continue
        src = queue_index.get(pid)
        if not src:
            missing_paper += 1
            continue
        changed = False
        for field in target_fields:
            src_val = str(src.get(field, "") or "")
            if not src_val:
                continue
            if str(row.get(field, "") or "") != src_val:
                row[field] = src_val
                changed = True
        if changed:
            updated_rows += 1

    print(f"Confirmed rows scanned: {len(confirmed_rows)}")
    print(f"Rows updated: {updated_rows}")
    print(f"Rows with paper_id not found in queue: {missing_paper}")

    if args.dry_run:
        return 0

    write_csv(confirmed_path, confirmed_rows)
    print(f"Confirmed CSV updated: {confirmed_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
