#!/usr/bin/env python3
"""Detect stale task claims and suggest steal commands."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

UTC = timezone.utc


def parse_ts(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)
    except ValueError:
        return None


def read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def discover_tasks(signals_dir: Path) -> set[str]:
    tasks: set[str] = set()
    for p in signals_dir.glob("*_CLAIMED.json"):
        tasks.add(p.name[: -len("_CLAIMED.json")].upper())
    return tasks


def main() -> int:
    parser = argparse.ArgumentParser(description="Stale claim watchdog")
    parser.add_argument("--signals-dir", type=Path, default=Path("signals"))
    parser.add_argument("--grace-seconds", type=int, default=300)
    parser.add_argument("--suggest-by", default="codex")
    parser.add_argument("--fail-on-stale", action="store_true")
    args = parser.parse_args()

    signals_dir = args.signals_dir.resolve()
    now = datetime.now(tz=UTC)
    grace = timedelta(seconds=args.grace_seconds)

    stale: list[dict[str, Any]] = []

    for task in sorted(discover_tasks(signals_dir)):
        claim_path = signals_dir / f"{task}_CLAIMED.json"
        complete_path = signals_dir / f"{task}_COMPLETE.json"

        claim = read_json(claim_path)
        complete = read_json(complete_path)
        if not claim or complete:
            continue

        status = str(claim.get("status", "")).lower()
        if status in {"completed", "abandoned"}:
            continue

        expires = parse_ts(str(claim.get("lease_expires_at", "")))
        if not expires:
            continue

        if expires + grace < now:
            owner = str(claim.get("claimed_by", "unknown"))
            stale.append(
                {
                    "task_id": task,
                    "claimed_by": owner,
                    "expired_at": expires.isoformat().replace("+00:00", "Z"),
                    "age_seconds": int((now - expires).total_seconds()),
                    "steal_command": (
                        f"python3 scripts/task_signal.py claim --task {task} --by {args.suggest_by} "
                        f"--allow-steal --steal-reason 'lease expired watchdog'"
                    ),
                }
            )

    print(
        json.dumps(
            {
                "checked_at": now.isoformat().replace("+00:00", "Z"),
                "grace_seconds": args.grace_seconds,
                "stale_count": len(stale),
                "stale": stale,
            },
            indent=2,
            ensure_ascii=True,
        )
    )

    if args.fail_on_stale and stale:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
