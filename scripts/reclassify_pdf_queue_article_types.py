#!/usr/bin/env python3
"""
Reclassify article_type_family for all rows in realtime PDF completion queue.

This backfills queue metadata with the shared paper classifier diagnostics so
legacy labels from the old keyword chain do not continue poisoning downstream
table/rule interpretation.
"""

from __future__ import annotations

import argparse
import csv
import sqlite3
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, List

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.epistemic.extraction.paper_classifier import classify_paper
from src.services.db_locator import resolve_article_finder_db

DEFAULT_AF_DB = None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Reclassify queue article types with diagnostics.")
    parser.add_argument(
        "--queue-csv",
        default="data/production/realtime_pdf_completion_queue.csv",
        help="Path to realtime queue CSV",
    )
    parser.add_argument(
        "--db",
        default=DEFAULT_AF_DB,
        help="Article Finder SQLite DB path (auto-resolved if omitted)",
    )
    parser.add_argument(
        "--review-csv",
        default="data/review/article_type_manual_queue.csv",
        help="Where to write low-confidence / ambiguous type rows",
    )
    parser.add_argument(
        "--min-confidence",
        type=float,
        default=0.60,
        help="Minimum confidence threshold before review flag",
    )
    parser.add_argument(
        "--min-margin",
        type=float,
        default=0.35,
        help="Minimum winner margin threshold before review flag",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Compute and print stats only without writing files",
    )
    return parser.parse_args()


def read_rows(path: Path) -> List[Dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_rows(path: Path, rows: List[Dict[str, str]]) -> None:
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


def write_review_csv(path: Path, rows: List[Dict[str, str]]) -> None:
    fieldnames = [
        "paper_id",
        "doi",
        "title",
        "year",
        "venue",
        "status",
        "article_type_family",
        "article_type_confidence",
        "article_type_runner_up",
        "article_type_margin",
        "article_type_signals",
        "article_type_diagnostics",
        "type_review_flags",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    args = parse_args()
    queue_path = Path(args.queue_csv)
    review_path = Path(args.review_csv)
    db_path = resolve_article_finder_db(args.db)
    print(f"[reclassify_pdf_queue_article_types] using af_db={db_path}")
    if not queue_path.exists():
        print(f"Queue not found: {queue_path}")
        return 1
    if not db_path.exists():
        print(f"DB not found: {db_path}")
        return 1

    rows = read_rows(queue_path)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    mismatch = 0
    review_rows: List[Dict[str, str]] = []
    family_counts = Counter()
    try:
        for row in rows:
            pid = str(row.get("paper_id", "")).strip()
            if not pid:
                continue
            rec = conn.execute(
                "SELECT title, abstract, venue FROM papers WHERE paper_id = ? LIMIT 1",
                (pid,),
            ).fetchone()
            title = str((rec["title"] if rec else row.get("title", "")) or "")
            abstract = str((rec["abstract"] if rec else "") or "")
            venue = str((rec["venue"] if rec else row.get("venue", "")) or "")
            cls = classify_paper(title=title, abstract=abstract, venue=venue)
            confidence = float(cls.confidence)
            margin = float(cls.margin)
            needs_review = bool(cls.needs_manual_review)
            diagnostics = list(cls.diagnostics[:8])

            old_family = str(row.get("article_type_family", "") or "unknown")
            new_family = cls.template_family.value
            if needs_review and confidence < float(args.min_confidence):
                new_family = "unknown"
                diagnostics.append("downgraded_to_unknown_low_confidence")
            if old_family != new_family:
                mismatch += 1

            row["article_type_family"] = new_family
            row["article_type_predicted_family"] = cls.template_family.value
            row["article_type_confidence"] = f"{confidence:.4f}"
            row["article_type_runner_up"] = cls.runner_up_family.value if cls.runner_up_family else ""
            row["article_type_margin"] = f"{margin:.4f}"
            row["article_type_needs_review"] = "true" if needs_review else "false"
            row["article_type_signals"] = "|".join(cls.signals_matched[:8])
            row["article_type_diagnostics"] = "|".join(diagnostics)
            row["article_type_classifier_version"] = "paper_classifier_v2"
            family_counts[new_family] += 1

            low_conf = confidence < float(args.min_confidence)
            low_margin = margin < float(args.min_margin)
            flagged = needs_review
            if low_conf or low_margin or flagged:
                flags = []
                if flagged:
                    flags.append("classifier_flagged")
                if low_conf:
                    flags.append("low_confidence")
                if low_margin:
                    flags.append("low_margin")
                review_rows.append(
                    {
                        "paper_id": row.get("paper_id", ""),
                        "doi": row.get("doi", ""),
                        "title": row.get("title", ""),
                        "year": row.get("year", ""),
                        "venue": row.get("venue", ""),
                        "status": row.get("status", ""),
                        "article_type_family": new_family,
                        "article_type_confidence": f"{confidence:.4f}",
                        "article_type_runner_up": row.get("article_type_runner_up", ""),
                        "article_type_margin": f"{margin:.4f}",
                        "article_type_signals": row.get("article_type_signals", ""),
                        "article_type_diagnostics": row.get("article_type_diagnostics", ""),
                        "type_review_flags": "|".join(flags),
                    }
                )
    finally:
        conn.close()

    print(f"Rows scanned: {len(rows)}")
    print(f"Family changes: {mismatch}")
    print(f"Family distribution: {dict(family_counts.most_common())}")
    print(f"Type review rows: {len(review_rows)}")

    if args.dry_run:
        return 0

    write_rows(queue_path, rows)
    write_review_csv(review_path, review_rows)
    print(f"Queue updated: {queue_path}")
    print(f"Type review CSV: {review_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
