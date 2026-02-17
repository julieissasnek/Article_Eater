#!/usr/bin/env python3
"""Drain a PDF queue with timeout-aware skip for blocking rows."""

from __future__ import annotations

import argparse
import csv
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

UTC = timezone.utc


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--queue-csv", required=True)
    p.add_argument("--confirmed-csv", required=True)
    p.add_argument("--no-claims-csv", required=True)
    p.add_argument("--audit-jsonl", required=True)
    p.add_argument("--manual-review-csv", required=True)
    p.add_argument("--article-type-review-csv", required=True)
    p.add_argument("--batch-size", type=int, default=1)
    p.add_argument("--max-workers", type=int, default=1)
    p.add_argument("--timeout-seconds", type=float, default=120.0)
    p.add_argument("--sleep-seconds", type=float, default=0.2)
    p.add_argument("--max-iterations", type=int, default=0, help="0 = unlimited")
    p.add_argument("--max-skips", type=int, default=100)
    return p.parse_args()


def load_rows(path: Path) -> tuple[List[str], List[Dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        return list(r.fieldnames or []), list(r)


def write_rows(path: Path, fields: List[str], rows: List[Dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def queue_counts(rows: List[Dict[str, str]]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for row in rows:
        s = str(row.get("status", "")).strip()
        counts[s] = counts.get(s, 0) + 1
    return counts


def mark_first_queued_failed(queue_csv: Path, reason: str) -> str:
    fields, rows = load_rows(queue_csv)
    failed_pid = ""
    now = datetime.now(tz=UTC).isoformat()
    for row in rows:
        if str(row.get("status", "")).startswith("queued_"):
            failed_pid = str(row.get("paper_id", ""))
            row["status"] = "failed"
            row["error"] = reason
            row["processed_at"] = now
            if "retry_status" in fields:
                row["retry_status"] = "timeout_skipped_by_script"
            if "retry_error" in fields:
                row["retry_error"] = reason
            break
    if failed_pid:
        write_rows(queue_csv, fields, rows)
    return failed_pid


def main() -> int:
    args = parse_args()
    queue_csv = Path(args.queue_csv)
    proc_script = Path("scripts/process_realtime_pdf_completion_queue.py")
    if not queue_csv.exists():
        raise SystemExit(f"Missing queue CSV: {queue_csv}")
    if not proc_script.exists():
        raise SystemExit(f"Missing process script: {proc_script}")

    skips = 0
    iteration = 0
    while True:
        iteration += 1
        if args.max_iterations and iteration > args.max_iterations:
            print(f"Reached max_iterations={args.max_iterations}")
            break

        _, rows = load_rows(queue_csv)
        pending = sum(1 for r in rows if str(r.get("status", "")).startswith("queued_"))
        if pending <= 0:
            print("Queue drained.")
            break

        print(f"[iter {iteration}] pending={pending}, skips={skips}")
        cmd = [
            sys.executable,
            str(proc_script),
            "--queue-csv",
            args.queue_csv,
            "--confirmed-csv",
            args.confirmed_csv,
            "--no-claims-csv",
            args.no_claims_csv,
            "--audit-jsonl",
            args.audit_jsonl,
            "--manual-review-csv",
            args.manual_review_csv,
            "--article-type-review-csv",
            args.article_type_review_csv,
            "--batch-size",
            str(args.batch_size),
            "--max-workers",
            str(args.max_workers),
        ]
        try:
            run = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=args.timeout_seconds if args.timeout_seconds > 0 else None,
            )
        except subprocess.TimeoutExpired:
            pid = mark_first_queued_failed(queue_csv, reason=f"timeout_{int(args.timeout_seconds)}s")
            skips += 1
            print(f"[iter {iteration}] timeout; skipped paper_id={pid or '<none>'}")
            if skips >= args.max_skips:
                print(f"Reached max_skips={args.max_skips}; aborting.")
                return 2
            time.sleep(max(0.0, args.sleep_seconds))
            continue

        if run.stdout.strip():
            print(run.stdout.strip())
        if run.stderr.strip():
            print(run.stderr.strip(), file=sys.stderr)
        if run.returncode != 0:
            print(f"[iter {iteration}] process script failed rc={run.returncode}", file=sys.stderr)
            return run.returncode

        time.sleep(max(0.0, args.sleep_seconds))

    _, rows = load_rows(queue_csv)
    print(f"Final status counts: {queue_counts(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
