#!/usr/bin/env python3
"""Build a paper-level remake queue from table_remake_queue.csv."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

UTC = timezone.utc


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--table-remake-csv", type=Path, default=Path("data/review/table_remake_queue.csv"))
    p.add_argument("--base-queue-csv", type=Path, default=Path("data/production/realtime_pdf_completion_queue.csv"))
    p.add_argument("--output-queue-csv", type=Path, default=Path("data/review/table_remake_paper_queue.csv"))
    p.add_argument("--report-json", type=Path, default=Path("data/review/table_remake_paper_queue_report.json"))
    return p.parse_args()


def load_csv(path: Path) -> List[Dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def main() -> int:
    args = parse_args()
    if not args.table_remake_csv.exists():
        raise SystemExit(f"Missing table remake CSV: {args.table_remake_csv}")
    if not args.base_queue_csv.exists():
        raise SystemExit(f"Missing base queue CSV: {args.base_queue_csv}")

    remake_rows = load_csv(args.table_remake_csv)
    base_rows = load_csv(args.base_queue_csv)

    bad_papers = {r.get("paper_id", "").strip() for r in remake_rows if r.get("paper_id", "").strip()}

    by_paper: Dict[str, Dict[str, str]] = {}
    for row in base_rows:
        pid = row.get("paper_id", "").strip()
        if not pid:
            continue
        by_paper[pid] = row

    out_rows: List[Dict[str, str]] = []
    now = datetime.now(tz=UTC).isoformat()
    missing = []
    for pid in sorted(bad_papers):
        base = by_paper.get(pid)
        if not base:
            missing.append(pid)
            continue
        row = dict(base)
        row["status"] = "queued_table_remake"
        row["reason"] = "table_remake_required"
        row["queued_at"] = now
        row["processed_at"] = ""
        row["error"] = ""
        out_rows.append(row)

    args.output_queue_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.output_queue_csv.open("w", encoding="utf-8", newline="") as f:
        if out_rows:
            fieldnames = list(out_rows[0].keys())
        else:
            fieldnames = list(base_rows[0].keys()) if base_rows else []
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        if out_rows:
            w.writerows(out_rows)

    report = {
        "generated_at": now,
        "table_remake_rows": len(remake_rows),
        "target_papers": len(bad_papers),
        "paper_queue_rows": len(out_rows),
        "missing_papers_from_base_queue": len(missing),
        "missing_paper_ids_sample": missing[:25],
        "status_counts": dict(Counter(r.get("status", "") for r in out_rows)),
        "output_queue_csv": str(args.output_queue_csv),
    }

    args.report_json.parent.mkdir(parents=True, exist_ok=True)
    args.report_json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
