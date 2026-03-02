#!/usr/bin/env python3
"""
ATLAS Local Runner — Sandbox-to-Native Bridge
===============================================

Created: 2026-02-27
Sprint: MAINTENANCE-1

Problem:
    AI sandboxes (Cowork, AG, etc.) can read your codebase but cannot reliably
    write to SQLite databases due to virtiofs/overlay filesystem restrictions.
    This means pipeline stages that modify web_persistence.db, overseer.db, etc.
    fail silently or with disk I/O errors.

Solution:
    This script runs NATIVELY on your Mac. It watches for command requests
    written by sandboxed AI sessions and executes them with full filesystem
    access. Think of it as a thin "executor" that bridges the sandbox gap.

Architecture:
    Sandbox AI (Cowork/AG)              Your Mac (native)
    ┌──────────────────┐                ┌──────────────────┐
    │ Writes command    │  ──(file)──>  │ local_runner.py   │
    │ to run_queue.json │                │ watches queue     │
    │                   │  <──(file)──  │ executes commands  │
    │ Reads results     │                │ writes results     │
    └──────────────────┘                └──────────────────┘

    The shared medium is the repo directory, which both sandbox and native
    can read/write (the sandbox mounts it).

Modes:
    1. WATCH MODE (daemon):
       python scripts/local_runner.py watch
       Polls run_queue.json every 5s, executes pending commands.

    2. ONCE MODE (manual):
       python scripts/local_runner.py once
       Processes all pending commands, then exits.

    3. RUN MODE (direct):
       python scripts/local_runner.py run backup --mode incremental
       python scripts/local_runner.py run integrate
       python scripts/local_runner.py run health
       python scripts/local_runner.py run nightly
       Runs a named pipeline stage directly.

    4. STATUS MODE:
       python scripts/local_runner.py status
       Shows current queue state and recent results.

Command Queue Format (data/run_queue.json):
    {
        "commands": [
            {
                "id": "cmd_20260227_143022",
                "requested_by": "cowork_session",
                "requested_at": "2026-02-27T14:30:22Z",
                "command": "integrate",
                "args": {},
                "status": "pending",
                "priority": 1
            }
        ],
        "results": [
            {
                "id": "cmd_20260227_143022",
                "started_at": "...",
                "completed_at": "...",
                "status": "ok",
                "output": {...},
                "duration_s": 245.3
            }
        ]
    }

Cron setup (recommended):
    # Run pending commands every 5 minutes
    */5 * * * * cd /Users/davidusa/REPOS/Article_Eater_PostQuinean_v1 && python scripts/local_runner.py once >> logs/local_runner.log 2>&1

Safety:
    - Only executes commands from a FIXED allowlist (no arbitrary code exec)
    - Pre-flight backup before any write operation
    - Results logged with full stdout/stderr capture
    - Dry-run support for all commands
"""

from __future__ import annotations

import argparse
import json
import logging
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

QUEUE_PATH = PROJECT_ROOT / "data" / "run_queue.json"
LOGS_DIR = PROJECT_ROOT / "logs"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [LOCAL_RUNNER] %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)


# =============================================================================
# COMMAND ALLOWLIST — Only these commands can be executed
# =============================================================================

ALLOWED_COMMANDS: Dict[str, Dict[str, Any]] = {
    "backup_full": {
        "description": "Full backup of all databases",
        "script": "scripts/backup_databases.py",
        "args": ["--mode", "full"],
        "needs_backup": False,  # It IS the backup
        "timeout": 120,
    },
    "backup_incremental": {
        "description": "Near-instant incremental backup",
        "script": "scripts/backup_databases.py",
        "args": ["--mode", "incremental"],
        "needs_backup": False,
        "timeout": 30,
    },
    "integrate": {
        "description": "Run SystemSetup.setup() — bulk integration of all extractions",
        "script": "scripts/nightly_integration_pipeline.py",
        "args": ["--stages", "integrate"],
        "needs_backup": True,
        "timeout": 600,
    },
    "health": {
        "description": "Run health check gauntlet",
        "script": "scripts/nightly_integration_pipeline.py",
        "args": ["--stages", "health_check"],
        "needs_backup": False,
        "timeout": 120,
    },
    "web_health": {
        "description": "Run safe_improve_web_health to connect isolated beliefs",
        "script": "scripts/safe_improve_web_health.py",
        "args": [],
        "needs_backup": True,
        "timeout": 300,
    },
    "nightly": {
        "description": "Full nightly pipeline (all stages)",
        "script": "scripts/nightly_integration_pipeline.py",
        "args": [],
        "needs_backup": True,
        "timeout": 900,
    },
    "diagnose": {
        "description": "Run database diagnostic",
        "script": "scripts/diagnose_db_corruption.py",
        "args": [],
        "needs_backup": False,
        "timeout": 60,
    },
    "reconcile_tier2": {
        "description": "Reconcile tier2 theory-link constraints",
        "script": "scripts/reconcile_tier2_theory_links.py",
        "args": [],
        "needs_backup": True,
        "timeout": 60,
    },
    "system_health": {
        "description": "Compute AESHI system health score",
        "script": "scripts/compute_system_health.py",
        "args": [],
        "needs_backup": False,
        "timeout": 120,
    },
    "system_map": {
        "description": "Generate system architecture map",
        "script": "scripts/atlas_system_map.py",
        "args": [],
        "needs_backup": False,
        "timeout": 120,
    },
}


# =============================================================================
# QUEUE MANAGEMENT
# =============================================================================

def _load_queue() -> Dict[str, Any]:
    """Load the command queue from disk."""
    if QUEUE_PATH.exists():
        try:
            return json.loads(QUEUE_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, IOError):
            pass
    return {"commands": [], "results": []}


def _save_queue(queue: Dict[str, Any]) -> None:
    """Save the command queue to disk."""
    QUEUE_PATH.parent.mkdir(parents=True, exist_ok=True)
    queue["updated_at"] = datetime.now(timezone.utc).isoformat()
    QUEUE_PATH.write_text(
        json.dumps(queue, indent=2, default=str),
        encoding="utf-8",
    )


def enqueue_command(
    command: str,
    args: Optional[Dict[str, Any]] = None,
    requested_by: str = "manual",
    priority: int = 1,
) -> str:
    """
    Add a command to the execution queue.

    Called by sandbox AI sessions to request native execution.
    Returns the command ID.
    """
    if command not in ALLOWED_COMMANDS:
        raise ValueError(
            f"Unknown command '{command}'. "
            f"Allowed: {', '.join(sorted(ALLOWED_COMMANDS.keys()))}"
        )

    queue = _load_queue()
    cmd_id = f"cmd_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    queue["commands"].append({
        "id": cmd_id,
        "command": command,
        "args": args or {},
        "requested_by": requested_by,
        "requested_at": datetime.now(timezone.utc).isoformat(),
        "status": "pending",
        "priority": priority,
    })

    _save_queue(queue)
    logger.info(f"Enqueued: {cmd_id} → {command} (by {requested_by})")
    return cmd_id


def get_command_result(cmd_id: str) -> Optional[Dict[str, Any]]:
    """Check if a command has completed and return its result."""
    queue = _load_queue()
    for result in queue.get("results", []):
        if result.get("id") == cmd_id:
            return result
    return None


# =============================================================================
# PRE-FLIGHT BACKUP (HARD GATE)
# =============================================================================

def _preflight_backup() -> tuple:
    """
    Run incremental backup as a hard gate before any database-writing command.

    Returns:
        (success: bool, diagnosis: dict|None)

    If backup fails, runs a diagnostic to determine WHY — checking:
      1. Do the database files exist?
      2. Are they readable (valid SQLite headers)?
      3. Is the backup directory writable?
      4. Are there stale journal/WAL lock files?
      5. Is disk space sufficient?
      6. Can SQLite open the databases at all?

    The diagnosis dict is stored in the command result so it's visible
    in run_queue.json for debugging.
    """
    logger.info("Pre-flight incremental backup (HARD GATE)...")

    try:
        backup_result = subprocess.run(
            [sys.executable, "scripts/backup_databases.py",
             "--mode", "incremental"],
            capture_output=True, text=True, cwd=str(PROJECT_ROOT),
            timeout=30,
        )
        if backup_result.returncode == 0:
            logger.info("Pre-flight backup: OK")
            return (True, None)

        # Backup failed — run diagnosis
        logger.error(
            f"Pre-flight backup FAILED (rc={backup_result.returncode}). "
            f"Running diagnosis..."
        )
        diag = _diagnose_backup_failure(
            backup_result.stdout, backup_result.stderr
        )
        return (False, diag)

    except subprocess.TimeoutExpired:
        logger.error("Pre-flight backup TIMED OUT (30s). Running diagnosis...")
        diag = _diagnose_backup_failure("", "Timeout after 30 seconds")
        diag["timeout"] = True
        return (False, diag)

    except Exception as e:
        logger.error(f"Pre-flight backup EXCEPTION: {e}. Running diagnosis...")
        diag = _diagnose_backup_failure("", str(e))
        diag["exception"] = str(e)
        return (False, diag)


def _diagnose_backup_failure(stdout: str, stderr: str) -> Dict[str, Any]:
    """
    Diagnose why the incremental backup failed.

    Checks filesystem, database health, locks, and disk space.
    Returns a structured diagnosis dict for logging and debugging.
    """
    import sqlite3
    import struct

    diag: Dict[str, Any] = {
        "diagnosed_at": datetime.now(timezone.utc).isoformat(),
        "backup_stdout": stdout[-500:] if stdout else "",
        "backup_stderr": stderr[-500:] if stderr else "",
        "checks": [],
    }

    data_dir = PROJECT_ROOT / "data"
    backup_dir = PROJECT_ROOT / "data" / "backups"

    # Check 1: Do critical database files exist?
    critical_dbs = [
        data_dir / "web_persistence.db",
        data_dir / "web_of_belief.db",
        data_dir / "overseer.db",
    ]
    for db in critical_dbs:
        exists = db.exists()
        size = db.stat().st_size if exists else 0
        diag["checks"].append({
            "check": f"exists:{db.name}",
            "ok": exists,
            "size_bytes": size,
        })

    # Check 2: Are there stale journal or WAL lock files?
    stale_locks = []
    for db in critical_dbs:
        if not db.exists():
            continue
        journal = db.with_suffix(db.suffix + "-journal")
        wal = db.with_suffix(db.suffix + "-wal")
        shm = db.with_suffix(db.suffix + "-shm")
        for lock_file in [journal, wal, shm]:
            if lock_file.exists():
                age_s = time.time() - lock_file.stat().st_mtime
                stale_locks.append({
                    "file": lock_file.name,
                    "size_bytes": lock_file.stat().st_size,
                    "age_seconds": round(age_s, 1),
                    "likely_stale": age_s > 300,  # >5 min = likely stale
                })
    diag["checks"].append({
        "check": "stale_locks",
        "ok": len(stale_locks) == 0,
        "locks_found": stale_locks,
    })

    # Check 3: Can we read SQLite headers? (no connection, no locks)
    for db in critical_dbs:
        if not db.exists():
            continue
        try:
            with open(db, "rb") as f:
                header = f.read(100)
            if len(header) >= 100 and header[:16] == b"SQLite format 3\x00":
                counter = struct.unpack(">I", header[24:28])[0]
                pages = struct.unpack(">I", header[28:32])[0]
                diag["checks"].append({
                    "check": f"header_read:{db.name}",
                    "ok": True,
                    "change_counter": counter,
                    "page_count": pages,
                })
            else:
                diag["checks"].append({
                    "check": f"header_read:{db.name}",
                    "ok": False,
                    "error": "invalid SQLite header",
                })
        except Exception as e:
            diag["checks"].append({
                "check": f"header_read:{db.name}",
                "ok": False,
                "error": str(e),
            })

    # Check 4: Is the backup directory writable?
    try:
        backup_dir.mkdir(parents=True, exist_ok=True)
        test_file = backup_dir / ".write_test"
        test_file.write_text("test")
        test_file.unlink()
        diag["checks"].append({
            "check": "backup_dir_writable",
            "ok": True,
            "path": str(backup_dir),
        })
    except Exception as e:
        diag["checks"].append({
            "check": "backup_dir_writable",
            "ok": False,
            "error": str(e),
            "path": str(backup_dir),
        })

    # Check 5: Disk space
    try:
        stat = os.statvfs(str(data_dir))
        free_bytes = stat.f_bavail * stat.f_frsize
        free_mb = free_bytes / 1_000_000
        diag["checks"].append({
            "check": "disk_space",
            "ok": free_mb > 100,  # Need at least 100MB free
            "free_mb": round(free_mb, 1),
        })
    except Exception as e:
        diag["checks"].append({
            "check": "disk_space",
            "ok": False,
            "error": str(e),
        })

    # Check 6: Can SQLite open databases at all?
    for db in critical_dbs:
        if not db.exists():
            continue
        try:
            conn = sqlite3.connect(str(db), timeout=5)
            integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
            conn.close()
            diag["checks"].append({
                "check": f"sqlite_open:{db.name}",
                "ok": integrity == "ok",
                "integrity": integrity,
            })
        except Exception as e:
            diag["checks"].append({
                "check": f"sqlite_open:{db.name}",
                "ok": False,
                "error": str(e),
            })

    # Synthesize root cause
    failed_checks = [c for c in diag["checks"] if not c.get("ok")]
    if not failed_checks:
        diag["root_cause"] = (
            "All individual checks passed but backup still failed. "
            "Likely a transient issue — retry may succeed."
        )
        diag["recommendation"] = "retry"
    elif any("stale_locks" in c.get("check", "") for c in failed_checks):
        locks = [c for c in failed_checks if "stale_locks" in c.get("check", "")]
        diag["root_cause"] = (
            f"Stale lock files detected. A previous process may have "
            f"crashed mid-write, leaving journal/WAL/SHM files behind."
        )
        diag["recommendation"] = (
            "Remove stale lock files manually: "
            + ", ".join(
                l["file"] for lock_check in locks
                for l in lock_check.get("locks_found", [])
                if l.get("likely_stale")
            )
        )
    elif any("writable" in c.get("check", "") for c in failed_checks):
        diag["root_cause"] = "Backup directory is not writable."
        diag["recommendation"] = (
            f"Check permissions on {backup_dir}. "
            f"If running in a sandbox, this operation must run natively."
        )
    elif any("disk_space" in c.get("check", "") for c in failed_checks):
        diag["root_cause"] = "Insufficient disk space."
        diag["recommendation"] = "Free up disk space before retrying."
    elif any("sqlite_open" in c.get("check", "") for c in failed_checks):
        diag["root_cause"] = (
            "One or more databases cannot be opened by SQLite. "
            "Possible corruption or filesystem restriction."
        )
        diag["recommendation"] = (
            "Run: python scripts/diagnose_db_corruption.py for full analysis. "
            "If in sandbox, run natively."
        )
    elif any("header_read" in c.get("check", "") for c in failed_checks):
        diag["root_cause"] = "Database files have invalid SQLite headers."
        diag["recommendation"] = "Restore from last known good backup."
    else:
        diag["root_cause"] = "Unknown — see individual check results."
        diag["recommendation"] = "Review checks and stderr output."

    # Log diagnosis to file for persistent record
    diag_log = LOGS_DIR / "backup_failure_diagnosis.json"
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    try:
        existing = []
        if diag_log.exists():
            try:
                existing = json.loads(diag_log.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, IOError):
                pass
        existing.append(diag)
        # Keep last 50 diagnoses
        if len(existing) > 50:
            existing = existing[-50:]
        diag_log.write_text(
            json.dumps(existing, indent=2, default=str), encoding="utf-8"
        )
    except Exception as e:
        logger.debug(f"Non-critical: {e}")  # Don't let logging failure block the diagnosis return

    logger.error(f"Diagnosis root cause: {diag['root_cause']}")
    logger.error(f"Recommendation: {diag['recommendation']}")

    return diag


# =============================================================================
# COMMAND EXECUTION
# =============================================================================

def execute_command(
    command: str,
    extra_args: Optional[Dict[str, Any]] = None,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """
    Execute an allowed command natively.

    Returns result dict with status, output, duration.
    """
    if command not in ALLOWED_COMMANDS:
        return {"status": "error", "error": f"Unknown command: {command}"}

    spec = ALLOWED_COMMANDS[command]
    script = PROJECT_ROOT / spec["script"]

    if not script.exists():
        return {"status": "error", "error": f"Script not found: {spec['script']}"}

    # Build command line
    cmd = [sys.executable, str(script)] + spec["args"]

    # Add any extra args from the queue
    if extra_args:
        for k, v in extra_args.items():
            if isinstance(v, bool) and v:
                cmd.append(f"--{k}")
            elif not isinstance(v, bool):
                cmd.extend([f"--{k}", str(v)])

    if dry_run:
        cmd.append("--dry-run")

    logger.info(f"Executing: {' '.join(cmd)}")

    # Pre-flight backup — HARD GATE
    # If backup fails, command is NOT executed. Diagnosis is forced.
    if spec["needs_backup"] and not dry_run:
        backup_ok, backup_diag = _preflight_backup()
        if not backup_ok:
            return {
                "status": "backup_failed",
                "command": command,
                "error": "Pre-flight incremental backup failed. "
                         "Command blocked to protect live database.",
                "diagnosis": backup_diag,
                "duration_s": 0,
                "requeue": True,
            }

    # Execute the command
    start = time.time()
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=spec["timeout"],
        )
        elapsed = time.time() - start

        return {
            "status": "ok" if result.returncode == 0 else "failed",
            "returncode": result.returncode,
            "stdout": result.stdout[-2000:] if result.stdout else "",
            "stderr": result.stderr[-1000:] if result.stderr else "",
            "duration_s": round(elapsed, 1),
            "command": command,
            "script": spec["script"],
        }

    except subprocess.TimeoutExpired:
        elapsed = time.time() - start
        return {
            "status": "timeout",
            "duration_s": round(elapsed, 1),
            "timeout_limit": spec["timeout"],
            "command": command,
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "duration_s": round(time.time() - start, 1),
            "command": command,
        }


# =============================================================================
# QUEUE PROCESSING
# =============================================================================

def process_queue(dry_run: bool = False) -> List[Dict[str, Any]]:
    """Process all pending commands in the queue."""
    queue = _load_queue()
    pending = [
        c for c in queue.get("commands", [])
        if c.get("status") == "pending"
    ]

    if not pending:
        logger.info("No pending commands in queue.")
        return []

    # Sort by priority (lower = higher priority)
    pending.sort(key=lambda c: c.get("priority", 99))

    results = []
    for cmd in pending:
        cmd_id = cmd["id"]
        command = cmd["command"]
        extra_args = cmd.get("args", {})

        logger.info(f"Processing: {cmd_id} → {command}")
        cmd["status"] = "running"
        cmd["started_at"] = datetime.now(timezone.utc).isoformat()
        _save_queue(queue)

        result = execute_command(command, extra_args, dry_run=dry_run)
        result["id"] = cmd_id
        result["started_at"] = cmd.get("started_at")
        result["completed_at"] = datetime.now(timezone.utc).isoformat()

        # Handle backup_failed: re-queue instead of marking complete
        if result.get("status") == "backup_failed":
            retry_count = cmd.get("retry_count", 0) + 1
            max_retries = 3

            if retry_count >= max_retries:
                # Exhausted retries — mark as blocked, don't keep retrying
                cmd["status"] = "blocked_backup_failed"
                logger.error(
                    f"  {cmd_id}: backup failed {retry_count} times. "
                    f"BLOCKED — requires manual intervention. "
                    f"See logs/backup_failure_diagnosis.json"
                )
            else:
                # Re-queue: set back to pending with incremented retry count
                cmd["status"] = "pending"
                cmd["retry_count"] = retry_count
                cmd["last_backup_failure"] = result.get("diagnosis", {}).get(
                    "root_cause", "unknown"
                )
                logger.warning(
                    f"  {cmd_id}: backup failed (attempt {retry_count}/{max_retries}). "
                    f"Re-queued. Root cause: {cmd.get('last_backup_failure')}"
                )

            # Still log the result for the audit trail
            queue.setdefault("results", []).append(result)
            results.append(result)
        else:
            # Normal completion — update status
            cmd["status"] = result["status"]

            # Add to results
            queue.setdefault("results", []).append(result)
            results.append(result)

        # Keep only last 100 results
        if len(queue["results"]) > 100:
            queue["results"] = queue["results"][-100:]

        _save_queue(queue)

        logger.info(
            f"  → {result['status']} ({result.get('duration_s', 0)}s)"
        )

    # Clean completed commands from the queue
    # Keep: pending (re-queued after backup failure) and blocked
    queue["commands"] = [
        c for c in queue["commands"]
        if c.get("status") in ("pending", "blocked_backup_failed")
    ]
    _save_queue(queue)

    return results


# =============================================================================
# WATCH MODE
# =============================================================================

def watch(interval: int = 5, dry_run: bool = False) -> None:
    """
    Watch mode: poll the queue every N seconds and execute pending commands.
    Ctrl+C to stop.
    """
    logger.info(f"Watching queue every {interval}s. Ctrl+C to stop.")
    logger.info(f"Queue file: {QUEUE_PATH}")

    try:
        while True:
            process_queue(dry_run=dry_run)
            time.sleep(interval)
    except KeyboardInterrupt:
        logger.info("Watch mode stopped.")


# =============================================================================
# STATUS
# =============================================================================

def show_status() -> None:
    """Show current queue state and recent results."""
    queue = _load_queue()

    pending = [c for c in queue.get("commands", []) if c.get("status") == "pending"]
    running = [c for c in queue.get("commands", []) if c.get("status") == "running"]
    blocked = [c for c in queue.get("commands", []) if c.get("status") == "blocked_backup_failed"]
    results = queue.get("results", [])[-10:]  # Last 10 results

    print(f"\n{'=' * 60}")
    print("ATLAS Local Runner — Status")
    print(f"{'=' * 60}")
    print(f"Queue file: {QUEUE_PATH}")
    print(f"Pending: {len(pending)}  |  Running: {len(running)}  |  Blocked: {len(blocked)}")

    if blocked:
        print(f"\n*** BLOCKED COMMANDS (backup failed {3}x — manual intervention needed) ***")
        for cmd in blocked:
            desc = ALLOWED_COMMANDS.get(cmd['command'], {}).get('description', '?')
            print(f"  [{cmd['id']}] {cmd['command']} — {desc}")
            print(f"    Last failure: {cmd.get('last_backup_failure', '?')}")
            print(f"    Retries: {cmd.get('retry_count', '?')}")
            print(f"    Action: fix root cause, then set status back to 'pending' in run_queue.json")

    if pending:
        print(f"\nPending Commands:")
        for cmd in pending:
            desc = ALLOWED_COMMANDS.get(cmd['command'], {}).get('description', '?')
            retry_info = f" (retry #{cmd['retry_count']})" if cmd.get('retry_count') else ""
            print(f"  [{cmd['id']}] {cmd['command']} — {desc}{retry_info}")
            print(f"    Requested by: {cmd.get('requested_by', '?')} "
                  f"at {cmd.get('requested_at', '?')}")

    if running:
        print(f"\nRunning Commands:")
        for cmd in running:
            print(f"  [{cmd['id']}] {cmd['command']} — started {cmd.get('started_at', '?')}")

    if results:
        print(f"\nRecent Results (last {len(results)}):")
        for r in reversed(results):
            status_icon = {"ok": "✓", "failed": "✗", "timeout": "⏱", "error": "!", "backup_failed": "⛔"}.get(
                r.get("status", "?"), "?"
            )
            print(
                f"  {status_icon} [{r.get('id', '?')}] {r.get('command', '?')} "
                f"— {r.get('status', '?')} ({r.get('duration_s', 0)}s)"
            )

    print(f"\nAvailable Commands:")
    for name, spec in sorted(ALLOWED_COMMANDS.items()):
        needs = " [pre-backup]" if spec["needs_backup"] else ""
        print(f"  {name:25s} {spec['description']}{needs}")

    print(f"{'=' * 60}")


# =============================================================================
# MAIN
# =============================================================================

def main() -> int:
    parser = argparse.ArgumentParser(
        description="ATLAS Local Runner — execute pipeline commands natively",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start watch mode (runs pending commands every 5s)
  python scripts/local_runner.py watch

  # Process pending commands once then exit
  python scripts/local_runner.py once

  # Run a specific command directly
  python scripts/local_runner.py run integrate
  python scripts/local_runner.py run backup_incremental
  python scripts/local_runner.py run nightly --dry-run

  # Queue a command (for sandbox AI sessions to call)
  python scripts/local_runner.py queue integrate --by cowork

  # Show queue status
  python scripts/local_runner.py status
        """,
    )

    subparsers = parser.add_subparsers(dest="action", help="Action to perform")

    # watch
    watch_p = subparsers.add_parser("watch", help="Watch queue and execute (daemon)")
    watch_p.add_argument("--interval", type=int, default=5, help="Poll interval in seconds")
    watch_p.add_argument("--dry-run", action="store_true")

    # once
    once_p = subparsers.add_parser("once", help="Process queue once then exit")
    once_p.add_argument("--dry-run", action="store_true")

    # run
    run_p = subparsers.add_parser("run", help="Run a command directly")
    run_p.add_argument("command", choices=sorted(ALLOWED_COMMANDS.keys()))
    run_p.add_argument("--dry-run", action="store_true")

    # queue
    queue_p = subparsers.add_parser("queue", help="Enqueue a command for later execution")
    queue_p.add_argument("command", choices=sorted(ALLOWED_COMMANDS.keys()))
    queue_p.add_argument("--by", default="manual", help="Who is requesting")
    queue_p.add_argument("--priority", type=int, default=1)

    # status
    subparsers.add_parser("status", help="Show queue status")

    args = parser.parse_args()

    if not args.action:
        parser.print_help()
        return 0

    if args.action == "watch":
        watch(interval=args.interval, dry_run=args.dry_run)
        return 0

    elif args.action == "once":
        results = process_queue(dry_run=args.dry_run)
        failed = sum(1 for r in results if r.get("status") != "ok")
        return 1 if failed > 0 else 0

    elif args.action == "run":
        result = execute_command(args.command, dry_run=args.dry_run)
        print(json.dumps(result, indent=2, default=str))
        return 0 if result.get("status") == "ok" else 1

    elif args.action == "queue":
        cmd_id = enqueue_command(
            args.command,
            requested_by=args.by,
            priority=args.priority,
        )
        print(f"Enqueued: {cmd_id}")
        return 0

    elif args.action == "status":
        show_status()
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
