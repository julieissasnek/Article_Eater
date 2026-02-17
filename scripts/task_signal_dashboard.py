#!/usr/bin/env python3
"""Render a live dashboard of task signal states."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
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
    for path in signals_dir.glob("*.json"):
        name = path.name
        for suffix in ("_CLAIMED.json", "_UPDATE.json", "_COMPLETE.json"):
            if name.endswith(suffix):
                tasks.add(name[: -len(suffix)].upper())
                break
    return tasks


def short_ts(value: str | None) -> str:
    ts = parse_ts(value)
    if not ts:
        return "-"
    return ts.strftime("%m-%d %H:%MZ")


def state_for(claim: dict[str, Any] | None, complete: dict[str, Any] | None, now: datetime) -> str:
    if complete:
        return "complete"
    if not claim:
        return "unclaimed"

    status = str(claim.get("status", "")).lower()
    expires = parse_ts(str(claim.get("lease_expires_at", "")))
    if status in {"completed", "abandoned"}:
        return status
    if expires and expires > now:
        if status == "blocked":
            return "blocked_active"
        return "claimed_active"
    if status == "blocked":
        return "blocked_expired"
    return "claimed_expired"


def render_table(rows: list[dict[str, str]]) -> None:
    cols = [
        ("TASK", 12),
        ("STATE", 16),
        ("OWNER", 14),
        ("PROG", 6),
        ("LEASE_EXPIRES", 14),
        ("UPDATED", 14),
        ("COMPLETED", 14),
    ]

    def fmt_cell(text: str, width: int) -> str:
        t = text if text is not None else "-"
        return (t[: width - 1] + "…") if len(t) > width else t.ljust(width)

    header = "  ".join(fmt_cell(name, width) for name, width in cols)
    sep = "  ".join("-" * width for _, width in cols)
    print(header)
    print(sep)

    for row in rows:
        print(
            "  ".join(
                fmt_cell(row.get(name, "-"), width)
                for name, width in cols
            )
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="Task signal dashboard")
    parser.add_argument("--signals-dir", type=Path, default=Path("signals"))
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of table")
    args = parser.parse_args()

    signals_dir = args.signals_dir.resolve()
    now = datetime.now(tz=UTC)

    tasks = sorted(discover_tasks(signals_dir))
    rows: list[dict[str, str]] = []

    for task in tasks:
        claim = read_json(signals_dir / f"{task}_CLAIMED.json")
        update = read_json(signals_dir / f"{task}_UPDATE.json")
        complete = read_json(signals_dir / f"{task}_COMPLETE.json")

        owner = "-"
        if claim and claim.get("claimed_by"):
            owner = str(claim["claimed_by"])
        elif complete and complete.get("completed_by"):
            owner = str(complete["completed_by"])

        progress = "-"
        if update and update.get("progress_pct") is not None:
            progress = str(update.get("progress_pct"))
        elif complete:
            progress = "100"

        row = {
            "TASK": task,
            "STATE": state_for(claim, complete, now),
            "OWNER": owner,
            "PROG": progress,
            "LEASE_EXPIRES": short_ts(claim.get("lease_expires_at") if claim else None),
            "UPDATED": short_ts(update.get("timestamp") if update else None),
            "COMPLETED": short_ts(complete.get("timestamp") if complete else None),
        }
        rows.append(row)

    if args.json:
        print(json.dumps({"checked_at": now.isoformat().replace("+00:00", "Z"), "rows": rows}, indent=2))
    else:
        render_table(rows)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
