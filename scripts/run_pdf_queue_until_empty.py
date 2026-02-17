#!/usr/bin/env python3
"""
Loop PDF queue processing until no queued rows remain.

Useful for long-running shard processing from a dedicated terminal.
"""

from __future__ import annotations

import argparse
import fcntl
import os
import subprocess
import sys
import time
from pathlib import Path


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run PDF completion queue repeatedly until empty.")
    p.add_argument("--queue-csv", required=True, help="Queue CSV to drain")
    p.add_argument("--confirmed-csv", required=True, help="Per-run confirmed output CSV")
    p.add_argument("--no-claims-csv", required=True, help="Per-run no-claims output CSV")
    p.add_argument("--audit-jsonl", required=True, help="Per-run audit JSONL")
    p.add_argument("--manual-review-csv", required=True, help="Per-run manual-review CSV")
    p.add_argument("--article-type-review-csv", required=True, help="Per-run article-type review CSV")
    p.add_argument("--batch-size", type=int, default=4)
    p.add_argument("--max-workers", type=int, default=2)
    p.add_argument("--sleep-seconds", type=float, default=0.5)
    p.add_argument("--max-iterations", type=int, default=0, help="0 means unlimited")
    p.add_argument(
        "--subprocess-timeout-seconds",
        type=float,
        default=0.0,
        help="Timeout for each queue-processing subprocess (0 = no timeout)",
    )
    p.add_argument(
        "--lock-file",
        default=None,
        help="Optional lock file path; default is <queue-csv>.lock to prevent concurrent runners.",
    )
    p.add_argument("--prioritize-preprocessed", action="store_true")
    p.add_argument("--skip-preprocess-quarantine", action="store_true")
    p.add_argument("--integrate-web", action="store_true")
    p.add_argument("--update-bn", action="store_true")
    return p.parse_args()


def acquire_queue_lock(lock_path: Path):
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    lock_fh = lock_path.open("w", encoding="utf-8")
    try:
        fcntl.flock(lock_fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        lock_fh.close()
        raise
    lock_fh.seek(0)
    lock_fh.truncate(0)
    lock_fh.write(f"{os.getpid()}\n")
    lock_fh.flush()
    return lock_fh


def main() -> int:
    args = parse_args()
    script = Path("scripts/process_realtime_pdf_completion_queue.py")
    if not script.exists():
        print(f"Missing script: {script}", file=sys.stderr)
        return 2
    queue_csv_path = Path(args.queue_csv)
    lock_path = Path(args.lock_file) if args.lock_file else Path(f"{queue_csv_path}.lock")
    try:
        lock_fh = acquire_queue_lock(lock_path)
    except BlockingIOError:
        print(
            f"Another queue runner already holds lock: {lock_path}. "
            "Use a different queue or wait for the current runner to finish.",
            file=sys.stderr,
        )
        return 3

    try:
        i = 0
        while True:
            i += 1
            cmd = [
                sys.executable,
                str(script),
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
            if args.prioritize_preprocessed:
                cmd.append("--prioritize-preprocessed")
            if args.skip_preprocess_quarantine:
                cmd.append("--skip-preprocess-quarantine")
            if args.integrate_web:
                cmd.append("--integrate-web")
            if args.update_bn:
                cmd.append("--update-bn")

            print(f"[iter {i}] running: {' '.join(cmd)}")
            try:
                run = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=args.subprocess_timeout_seconds if args.subprocess_timeout_seconds > 0 else None,
                )
            except subprocess.TimeoutExpired:
                print(
                    f"[iter {i}] timed out after {args.subprocess_timeout_seconds:.1f}s; "
                    "exit for manual inspection.",
                    file=sys.stderr,
                )
                return 124
            stdout = run.stdout.strip()
            stderr = run.stderr.strip()
            if stdout:
                print(stdout)
            if stderr:
                print(stderr, file=sys.stderr)
            if run.returncode != 0:
                print(f"[iter {i}] non-zero exit: {run.returncode}", file=sys.stderr)
                return run.returncode

            if "No queued PDF rows to process." in stdout:
                print(f"[iter {i}] queue drained.")
                break

            if args.max_iterations > 0 and i >= args.max_iterations:
                print(f"[iter {i}] reached max_iterations={args.max_iterations}.")
                break

            time.sleep(max(0.0, args.sleep_seconds))
    finally:
        try:
            fcntl.flock(lock_fh.fileno(), fcntl.LOCK_UN)
        except Exception:
            pass
        lock_fh.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
