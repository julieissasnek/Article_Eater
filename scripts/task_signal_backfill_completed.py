#!/usr/bin/env python3
"""Backfill CLAIMED/UPDATE files for existing COMPLETE tasks."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

UTC = timezone.utc


def parse_ts(value: str | None) -> datetime:
    if not value:
        return datetime.now(tz=UTC)
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)
    except ValueError:
        return datetime.now(tz=UTC)


def iso_z(ts: datetime) -> str:
    return ts.astimezone(UTC).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, payload: dict[str, Any], dry_run: bool) -> None:
    if dry_run:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=True)
        f.write("\n")


def infer_owner(task_id: str, complete: dict[str, Any]) -> str:
    owner = complete.get("completed_by")
    if isinstance(owner, str) and owner.strip():
        return owner.strip()

    task = task_id.upper()
    if task.startswith("CX"):
        return "codex"
    if task.startswith("CC"):
        return "claude_code"
    if task.startswith("AG"):
        return "antigravity"
    return "unknown"


def task_ids(signals_dir: Path) -> list[str]:
    ids: set[str] = set()
    for p in signals_dir.glob("*_COMPLETE.json"):
        ids.add(p.name[: -len("_COMPLETE.json")].upper())
    return sorted(ids)


def main() -> int:
    parser = argparse.ArgumentParser(description="Backfill CLAIMED/UPDATE from COMPLETE files")
    parser.add_argument("--signals-dir", type=Path, default=Path("signals"))
    parser.add_argument("--owner", default=None, help="Only backfill tasks inferred/owned by this owner")
    parser.add_argument("--task-prefix", default=None, help="Only backfill tasks with this prefix (e.g., CC, AG, CX)")
    parser.add_argument("--lease-seconds", type=int, default=1800)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    signals_dir = args.signals_dir.resolve()

    created_claim = 0
    created_update = 0
    skipped = 0

    for task_id in task_ids(signals_dir):
        complete_path = signals_dir / f"{task_id}_COMPLETE.json"
        claim_path = signals_dir / f"{task_id}_CLAIMED.json"
        update_path = signals_dir / f"{task_id}_UPDATE.json"

        complete = read_json(complete_path)
        if not complete:
            continue

        owner = infer_owner(task_id, complete)
        if args.owner and owner != args.owner:
            skipped += 1
            continue
        if args.task_prefix and not task_id.startswith(args.task_prefix.upper()):
            skipped += 1
            continue

        completed_ts = parse_ts(str(complete.get("timestamp")))
        claim_ts = completed_ts - timedelta(minutes=15)
        update_ts = completed_ts - timedelta(minutes=5)

        if not claim_path.exists():
            claim_payload = {
                "task_id": task_id,
                "claimed_by": owner,
                "timestamp": iso_z(claim_ts),
                "lease_seconds": int(args.lease_seconds),
                "lease_expires_at": iso_z(claim_ts + timedelta(seconds=int(args.lease_seconds))),
                "status": "completed",
                "claim_action": "backfill",
                "intent": "backfilled from existing completion signal",
                "expected_output_files": complete.get("output_files", []),
                "last_heartbeat_at": iso_z(update_ts),
                "completed_at": iso_z(completed_ts),
            }
            write_json(claim_path, claim_payload, args.dry_run)
            created_claim += 1

        if not update_path.exists():
            update_payload = {
                "task_id": task_id,
                "claimed_by": owner,
                "timestamp": iso_z(update_ts),
                "status": "completed",
                "progress_pct": 100,
                "note": "backfilled from completion signal",
                "files_touched": complete.get("output_files", []),
                "eta_minutes": 0,
                "blocked_on": [],
            }
            write_json(update_path, update_payload, args.dry_run)
            created_update += 1

    print(
        json.dumps(
            {
                "signals_dir": str(signals_dir),
                "owner_filter": args.owner,
                "task_prefix_filter": args.task_prefix,
                "dry_run": args.dry_run,
                "created_claim_files": created_claim,
                "created_update_files": created_update,
                "skipped_by_filter": skipped,
            },
            indent=2,
            ensure_ascii=True,
        )
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
