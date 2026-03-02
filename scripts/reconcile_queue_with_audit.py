#!/usr/bin/env python3
"""Reconcile queue statuses using audit JSONL as source of truth for completed rows."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Dict, List


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--queue-csv", type=Path, required=True)
    p.add_argument("--audit-jsonl", type=Path, required=True)
    p.add_argument(
        "--completed-statuses",
        default="completed_pdf_extracted,completed_pdf_no_claims",
        help="Comma-separated statuses treated as terminal complete in audit",
    )
    p.add_argument("--dry-run", action="store_true")
    return p.parse_args()


def read_latest_audit_by_paper(path: Path) -> Dict[str, Dict[str, str]]:
    latest: Dict[str, Dict[str, str]] = {}
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception as e:
                import logging; logging.getLogger(__name__).debug(f"Skipped: {e}")
                continue
            if not isinstance(obj, dict):
                continue
            paper_id = str(obj.get("paper_id", "")).strip()
            if not paper_id:
                continue
            prev = latest.get(paper_id)
            cur_ts = str(obj.get("generated_at", ""))
            prev_ts = str(prev.get("generated_at", "")) if prev else ""
            if prev is None or cur_ts >= prev_ts:
                latest[paper_id] = obj
    return latest


def write_rows_atomic(path: Path, fieldnames: List[str], rows: List[Dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = NamedTemporaryFile("w", encoding="utf-8", newline="", delete=False, dir=str(path.parent))
    try:
        writer = csv.DictWriter(tmp, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    finally:
        tmp.close()
    Path(tmp.name).replace(path)


def main() -> int:
    args = parse_args()
    if not args.queue_csv.exists():
        raise SystemExit(f"Missing queue CSV: {args.queue_csv}")
    if not args.audit_jsonl.exists():
        raise SystemExit(f"Missing audit JSONL: {args.audit_jsonl}")

    terminal = {s.strip() for s in args.completed_statuses.split(",") if s.strip()}
    latest = read_latest_audit_by_paper(args.audit_jsonl)

    with args.queue_csv.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)

    before = Counter(r.get("status", "") for r in rows)
    changed = 0
    changed_by_status: Counter[str] = Counter()

    for row in rows:
        paper_id = str(row.get("paper_id", "")).strip()
        if not paper_id:
            continue
        audit_row = latest.get(paper_id)
        if not audit_row:
            continue
        new_status = str(audit_row.get("status", "")).strip()
        if new_status not in terminal:
            continue

        old_status = str(row.get("status", "")).strip()
        if old_status == new_status:
            continue

        row["status"] = new_status
        if "processed_at" in row and audit_row.get("generated_at"):
            row["processed_at"] = str(audit_row.get("generated_at", ""))
        if "n_tables" in row and audit_row.get("n_tables") is not None:
            row["n_tables"] = str(audit_row.get("n_tables", ""))
        if "n_claims" in row and audit_row.get("n_claims_total") is not None:
            row["n_claims"] = str(audit_row.get("n_claims_total", ""))
        if "error" in row and new_status.startswith("completed_"):
            row["error"] = ""

        changed += 1
        changed_by_status[f"{old_status}->{new_status}"] += 1

    after = Counter(r.get("status", "") for r in rows)

    summary = {
        "queue_csv": str(args.queue_csv),
        "audit_jsonl": str(args.audit_jsonl),
        "terminal_statuses": sorted(terminal),
        "rows_total": len(rows),
        "rows_changed": changed,
        "changed_by_status": dict(changed_by_status),
        "status_counts_before": dict(before),
        "status_counts_after": dict(after),
    }

    if args.dry_run:
        print(json.dumps(summary, indent=2))
        return 0

    write_rows_atomic(args.queue_csv, fieldnames, rows)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
