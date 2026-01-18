#!/usr/bin/env python3
"""Inspect processing_queue job states for Article Eater.

This is a small, read‑only helper for operators / TAs. It prints:

- counts of jobs by status,
- a short list of the most recent failed jobs (with error snippets), and
- any `running` jobs whose `started_at` is older than a threshold.

Usage (from repo root):

    python -m scripts.job_status_inspector
    # or
    python scripts/job_status_inspector.py

By default it connects to `ae.db` in the repository root. You can override
this with the environment variable `AE_DB_PATH`.
"""

from __future__ import annotations

import os
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple


DEFAULT_DB_NAME = "ae.db"
DEFAULT_STALE_MINUTES = 30


def get_db_path() -> Path:
    env = os.getenv("AE_DB_PATH")
    if env:
        return Path(env).expanduser().resolve()
    root = Path(__file__).resolve().parents[1]
    return root / DEFAULT_DB_NAME


def connect(db_path: Path) -> sqlite3.Connection:
    con = sqlite3.connect(str(db_path), timeout=30.0)
    con.row_factory = sqlite3.Row
    # Mirror worker defaults.
    con.execute("PRAGMA journal_mode=WAL;")
    return con


def summarize_status(con: sqlite3.Connection) -> Dict[str, int]:
    cur = con.cursor()
    cur.execute(
        """SELECT status, COUNT(*) AS n
        FROM processing_queue
        GROUP BY status
        ORDER BY status
        """
    )
    return {row[0]: int(row[1]) for row in cur.fetchall()}


def fetch_recent_failures(
    con: sqlite3.Connection,
    limit: int = 10,
) -> List[sqlite3.Row]:
    cur = con.cursor()
    cur.execute(
        """SELECT job_id, job_type, completed_at, error
        FROM processing_queue
        WHERE status = 'failed'
        ORDER BY completed_at DESC
        LIMIT ?
        """,
        (limit,),
    )
    return list(cur.fetchall())


def fetch_stale_running(
    con: sqlite3.Connection,
    stale_minutes: int = DEFAULT_STALE_MINUTES,
) -> List[sqlite3.Row]:
    threshold = datetime.utcnow() - timedelta(minutes=stale_minutes)
    # SQLite datetimes are stored as ISO8601 strings; we compare as text.
    threshold_str = threshold.isoformat()
    cur = con.cursor()
    cur.execute(
        """SELECT job_id, job_type, started_at
        FROM processing_queue
        WHERE status = 'running'
          AND started_at IS NOT NULL
          AND started_at < ?
        ORDER BY started_at ASC
        """,
        (threshold_str,),
    )
    return list(cur.fetchall())


def main() -> None:
    db_path = get_db_path()
    if not db_path.exists():
        print(f"[job_status_inspector] No database found at {db_path}")
        return

    con = connect(db_path)
    try:
        print(f"[job_status_inspector] Inspecting {db_path}")
        print()

        # Summary
        counts = summarize_status(con)
        if not counts:
            print("No jobs found in processing_queue.")
        else:
            print("Job counts by status:")
            for status in sorted(counts.keys()):
                print(f"  {status:8s} : {counts[status]}")
        print()

        # Recent failures
        failures = fetch_recent_failures(con)
        if failures:
            print("Most recent failed jobs:")
            for row in failures:
                job_id = row["job_id"]
                job_type = row["job_type"]
                completed_at = row["completed_at"] or "(unknown)"
                error = (row["error"] or "").strip()
                if len(error) > 120:
                    error = error[:117] + "..."
                print(f"  - {job_id} [{job_type}] @ {completed_at}: {error}")
        else:
            print("No failed jobs recorded.")
        print()

        # Stale running jobs
        stale = fetch_stale_running(con)
        if stale:
            print(
                f"Running jobs older than {DEFAULT_STALE_MINUTES} minutes (potentially stuck):"
            )
            for row in stale:
                job_id = row["job_id"]
                job_type = row["job_type"]
                started_at = row["started_at"] or "(unknown)"
                print(f"  - {job_id} [{job_type}] started_at={started_at}")
        else:
            print(
                "No obviously stale running jobs found (status='running' with old started_at).\n"
            )
    finally:
        con.close()


if __name__ == "__main__":  # pragma: no cover - CLI entry
    main()
