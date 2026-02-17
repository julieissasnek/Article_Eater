#!/usr/bin/env python3
"""Task signal helper for claim/update/complete workflow.

Writes and reads JSON files in signals/:
- {TASK}_CLAIMED.json
- {TASK}_UPDATE.json
- {TASK}_COMPLETE.json
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

UTC = timezone.utc


def now_utc() -> datetime:
    return datetime.now(tz=UTC)


def iso_z(ts: datetime) -> str:
    return ts.astimezone(UTC).isoformat().replace("+00:00", "Z")


def parse_iso_z(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)


def read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=True)
        f.write("\n")


@dataclass
class TaskPaths:
    claim: Path
    update: Path
    complete: Path



def build_paths(signals_dir: Path, task_id: str) -> TaskPaths:
    task = task_id.upper()
    return TaskPaths(
        claim=signals_dir / f"{task}_CLAIMED.json",
        update=signals_dir / f"{task}_UPDATE.json",
        complete=signals_dir / f"{task}_COMPLETE.json",
    )


def claim_is_active(claim: dict[str, Any] | None, at: datetime | None = None) -> bool:
    if not claim:
        return False
    status = str(claim.get("status", "")).lower()
    if status in {"completed", "abandoned"}:
        return False
    expires = claim.get("lease_expires_at")
    if not expires:
        return False
    check_time = at or now_utc()
    try:
        return parse_iso_z(str(expires)) > check_time
    except ValueError:
        return False


def cmd_claim(args: argparse.Namespace) -> int:
    now = now_utc()
    paths = build_paths(args.signals_dir, args.task)

    if paths.complete.exists():
        print(f"ERROR: task already complete ({paths.complete})", file=sys.stderr)
        return 2

    existing = read_json(paths.claim)
    active = claim_is_active(existing, now)
    existing_owner = (existing or {}).get("claimed_by")

    if active and existing_owner and existing_owner != args.by:
        print(
            f"ERROR: active claim exists for {args.task} by {existing_owner} until {existing.get('lease_expires_at')}",
            file=sys.stderr,
        )
        return 2

    if existing and existing_owner and existing_owner != args.by and not args.allow_steal:
        print(
            "ERROR: prior claim exists from another owner; pass --allow-steal if lease is expired and takeover is intentional",
            file=sys.stderr,
        )
        return 2

    lease_seconds = int(args.lease_seconds)
    expires = now + timedelta(seconds=lease_seconds)

    if not existing:
        claim_action = "new"
    elif existing_owner == args.by:
        claim_action = "renewed"
    else:
        claim_action = "stolen"

    payload: dict[str, Any] = {
        "task_id": args.task.upper(),
        "claimed_by": args.by,
        "timestamp": iso_z(now),
        "lease_seconds": lease_seconds,
        "lease_expires_at": iso_z(expires),
        "status": "claimed",
        "claim_action": claim_action,
        "intent": args.intent or "",
        "expected_output_files": args.output_file or [],
    }

    if claim_action == "stolen":
        payload["stolen_from"] = existing_owner
        payload["stolen_reason"] = args.steal_reason or "expired lease"

    write_json(paths.claim, payload)
    print(f"WROTE {paths.claim}")
    return 0


def cmd_update(args: argparse.Namespace) -> int:
    now = now_utc()
    paths = build_paths(args.signals_dir, args.task)

    if paths.complete.exists():
        print(f"ERROR: task already complete ({paths.complete})", file=sys.stderr)
        return 2

    claim = read_json(paths.claim)
    if not claim:
        print(f"ERROR: no claim file exists ({paths.claim})", file=sys.stderr)
        return 2

    owner = claim.get("claimed_by")
    if owner != args.by:
        print(f"ERROR: task claimed by {owner}; update denied for {args.by}", file=sys.stderr)
        return 2

    if args.progress is not None and not (0 <= args.progress <= 100):
        print("ERROR: --progress must be between 0 and 100", file=sys.stderr)
        return 2

    update_payload: dict[str, Any] = {
        "task_id": args.task.upper(),
        "claimed_by": args.by,
        "timestamp": iso_z(now),
        "status": args.status,
        "progress_pct": args.progress,
        "note": args.note or "",
        "files_touched": args.file or [],
        "eta_minutes": args.eta_minutes,
        "blocked_on": args.blocked_on or [],
    }
    write_json(paths.update, update_payload)

    renew_seconds = args.renew_seconds
    if renew_seconds is None:
        renew_seconds = int(claim.get("lease_seconds", 1800))

    claim["last_heartbeat_at"] = iso_z(now)
    claim["lease_expires_at"] = iso_z(now + timedelta(seconds=int(renew_seconds)))
    claim["status"] = "blocked" if args.status == "blocked" else "claimed"
    write_json(paths.claim, claim)

    print(f"WROTE {paths.update}")
    print(f"UPDATED LEASE {paths.claim}")
    return 0


def cmd_complete(args: argparse.Namespace) -> int:
    now = now_utc()
    paths = build_paths(args.signals_dir, args.task)

    claim = read_json(paths.claim)
    if claim:
        owner = claim.get("claimed_by")
        if owner != args.by and not args.force:
            print(
                f"ERROR: task claimed by {owner}; pass --force to complete anyway",
                file=sys.stderr,
            )
            return 2

    payload: dict[str, Any] = {
        "task_id": args.task.upper(),
        "completed_by": args.by,
        "timestamp": iso_z(now),
        "output_files": args.output_file or [],
        "notes": args.notes or "",
        "issues_found": args.issue or [],
        "changes_to_plan": args.change or [],
    }

    write_json(paths.complete, payload)

    if claim:
        claim["status"] = "completed"
        claim["completed_at"] = iso_z(now)
        write_json(paths.claim, claim)

    update_payload = {
        "task_id": args.task.upper(),
        "claimed_by": args.by,
        "timestamp": iso_z(now),
        "status": "completed",
        "progress_pct": 100,
        "note": args.notes or "",
        "files_touched": args.output_file or [],
        "eta_minutes": 0,
        "blocked_on": [],
    }
    write_json(paths.update, update_payload)

    print(f"WROTE {paths.complete}")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    now = now_utc()
    paths = build_paths(args.signals_dir, args.task)

    claim = read_json(paths.claim)
    update = read_json(paths.update)
    complete = read_json(paths.complete)

    if complete:
        state = "complete"
    elif claim_is_active(claim, now):
        state = "claimed_active"
    elif claim:
        state = "claimed_expired"
    else:
        state = "unclaimed"

    summary = {
        "task_id": args.task.upper(),
        "state": state,
        "claim_file": str(paths.claim),
        "update_file": str(paths.update),
        "complete_file": str(paths.complete),
        "claim": claim,
        "update": update,
        "complete": complete,
        "checked_at": iso_z(now),
    }

    print(json.dumps(summary, indent=2, ensure_ascii=True))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Task signal helper")
    parser.add_argument(
        "--signals-dir",
        type=Path,
        default=Path("signals"),
        help="Signals directory (default: signals)",
    )

    sub = parser.add_subparsers(dest="cmd", required=True)

    p_claim = sub.add_parser("claim", help="Create or renew claim")
    p_claim.add_argument("--task", required=True)
    p_claim.add_argument("--by", required=True)
    p_claim.add_argument("--lease-seconds", type=int, default=1800)
    p_claim.add_argument("--intent", default="")
    p_claim.add_argument("--output-file", action="append")
    p_claim.add_argument("--allow-steal", action="store_true")
    p_claim.add_argument("--steal-reason", default="")
    p_claim.set_defaults(func=cmd_claim)

    p_update = sub.add_parser("update", help="Write progress update and renew lease")
    p_update.add_argument("--task", required=True)
    p_update.add_argument("--by", required=True)
    p_update.add_argument("--status", choices=["in_progress", "blocked"], default="in_progress")
    p_update.add_argument("--progress", type=int)
    p_update.add_argument("--note", default="")
    p_update.add_argument("--file", action="append")
    p_update.add_argument("--eta-minutes", type=int)
    p_update.add_argument("--blocked-on", action="append")
    p_update.add_argument("--renew-seconds", type=int)
    p_update.set_defaults(func=cmd_update)

    p_complete = sub.add_parser("complete", help="Write completion signal and close claim")
    p_complete.add_argument("--task", required=True)
    p_complete.add_argument("--by", required=True)
    p_complete.add_argument("--notes", default="")
    p_complete.add_argument("--output-file", action="append")
    p_complete.add_argument("--issue", action="append")
    p_complete.add_argument("--change", action="append")
    p_complete.add_argument("--force", action="store_true")
    p_complete.set_defaults(func=cmd_complete)

    p_status = sub.add_parser("status", help="Show task signal status")
    p_status.add_argument("--task", required=True)
    p_status.set_defaults(func=cmd_status)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    args.signals_dir = args.signals_dir.resolve()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
