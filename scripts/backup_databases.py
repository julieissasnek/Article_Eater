#!/usr/bin/env python3
"""
ATLAS Database Backup Service — Full + Incremental
====================================================

Created: 2026-02-27  |  Updated: 2026-02-27 (incremental mode)
Sprint: MAINTENANCE-1

Two backup modes:

1. FULL BACKUP (--mode full, default for nightly)
   - SQLite online backup API → consistent full snapshot
   - 90MB database → ~6 seconds
   - Used: nightly, pre-migration, tagged checkpoints

2. INCREMENTAL BACKUP (--mode incremental, near-instant)
   - Compares SQLite page-level change_counter to last known value
   - If unchanged → skip entirely (0 bytes, <50ms)
   - If changed → copies ONLY the WAL file + records page count delta
   - For JSON files → computes SHA-256 hash; skip if unchanged
   - Typical incremental: <1 second, <1MB (just the WAL)
   - Restore: apply WAL on top of last full backup

Architecture:
    data/backups/
      ├── backup_log.json              # Audit trail
      ├── incremental_state.json       # Change counters per DB
      ├── web_persistence_2026-02-27_daily.db      # Full
      ├── web_persistence_2026-02-27T14:30_incr.wal # Incremental (WAL only)
      └── extraction_queue_2026-02-27_daily.json    # Full (JSON)

Usage:
    # Full nightly backup
    python scripts/backup_databases.py

    # Near-instant incremental (run before any pipeline stage)
    python scripts/backup_databases.py --mode incremental

    # Pre-operation tagged full backup
    python scripts/backup_databases.py --tag before_bulk_integration

    # Dry run
    python scripts/backup_databases.py --dry-run

    # List existing backups
    python scripts/backup_databases.py --list

    # Restore from backup
    python scripts/backup_databases.py --restore data/backups/web_persistence_2026-02-27_daily.db

    # Restore incremental (applies WAL to full backup)
    python scripts/backup_databases.py --restore-incremental data/backups/web_persistence_2026-02-27T14:30_incr.wal
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import logging
import os
import shutil
import sqlite3
import struct
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

BACKUP_DIR = PROJECT_ROOT / "data" / "backups"
BACKUP_LOG = BACKUP_DIR / "backup_log.json"
INCREMENTAL_STATE = BACKUP_DIR / "incremental_state.json"

# Critical databases to back up (relative to PROJECT_ROOT)
CRITICAL_DATABASES = [
    "data/web_persistence.db",
    "data/web_of_belief.db",
    # Overseer DB (may not exist yet)
    "data/overseer.db",
    # Extraction queue (JSON, not SQLite, but critical state)
    "data/extraction_pipeline/extraction_queue.json",
    # Notification queue
    "data/notifications/queue.json",
]

# Retention policy
DAILY_RETENTION = 7       # Keep 7 daily backups
WEEKLY_RETENTION = 4      # Keep 4 weekly backups
TAGGED_RETENTION = 30     # Keep tagged backups for 30 days

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [BACKUP] %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)


# =============================================================================
# INCREMENTAL BACKUP ENGINE
# =============================================================================

def _read_sqlite_header(db_path: Path) -> Dict[str, Any]:
    """
    Read SQLite database header (first 100 bytes) without opening a connection.
    This is a pure file read — no locks acquired, no journal created.

    SQLite header format (https://www.sqlite.org/fileformat.html):
      Offset  Size  Description
      24      4     File change counter (incremented on each transaction commit)
      28      4     Database size in pages
      40      4     Schema cookie (incremented on schema changes)
      92      4     Version-valid-for number (change counter at last vacuum)

    Returns dict with change_counter, page_count, schema_cookie, file_size.
    """
    try:
        with open(db_path, "rb") as f:
            header = f.read(100)
            if len(header) < 100 or header[:16] != b"SQLite format 3\x00":
                return {"error": "not a valid SQLite file"}

            page_size = struct.unpack(">H", header[16:18])[0]
            # Page size 1 means 65536 (special encoding)
            if page_size == 1:
                page_size = 65536

            change_counter = struct.unpack(">I", header[24:28])[0]
            page_count = struct.unpack(">I", header[28:32])[0]
            schema_cookie = struct.unpack(">I", header[40:44])[0]
            version_valid_for = struct.unpack(">I", header[92:96])[0]

            return {
                "change_counter": change_counter,
                "page_count": page_count,
                "page_size": page_size,
                "schema_cookie": schema_cookie,
                "version_valid_for": version_valid_for,
                "file_size": db_path.stat().st_size,
            }
    except Exception as e:
        return {"error": str(e)}


def _hash_file(path: Path, algorithm: str = "sha256") -> str:
    """Compute SHA-256 hash of a file, reading in 64KB chunks."""
    h = hashlib.new(algorithm)
    with open(path, "rb") as f:
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def _load_incremental_state() -> Dict[str, Any]:
    """Load the incremental state file tracking last-known change counters."""
    if INCREMENTAL_STATE.exists():
        try:
            return json.loads(INCREMENTAL_STATE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, IOError):
            pass
    return {"databases": {}, "last_full_backup": {}}


def _save_incremental_state(state: Dict[str, Any]) -> None:
    """Save incremental state."""
    INCREMENTAL_STATE.parent.mkdir(parents=True, exist_ok=True)
    state["updated_at"] = datetime.now(timezone.utc).isoformat()
    INCREMENTAL_STATE.write_text(
        json.dumps(state, indent=2, default=str), encoding="utf-8"
    )


def incremental_backup_sqlite(
    db_path: Path, backup_dir: Path
) -> Dict[str, Any]:
    """
    Near-instant incremental backup for a SQLite database.

    Strategy:
      1. Read the 100-byte header to get change_counter (no locks, no journal)
      2. Compare to last known change_counter from incremental_state.json
      3. If unchanged → skip entirely (return in <1ms)
      4. If changed → copy the WAL file if it exists, else do a minimal
         page-level backup using the backup API with page stepping

    Returns:
        {status: "unchanged"|"backed_up"|"failed",
         duration_ms: float,
         bytes_written: int,
         backup_path: str|None}
    """
    start = time.monotonic()
    state = _load_incremental_state()
    db_key = str(db_path.relative_to(PROJECT_ROOT))

    # Step 1: Read header without opening database
    header = _read_sqlite_header(db_path)
    if "error" in header:
        return {
            "status": "failed",
            "error": header["error"],
            "duration_ms": round((time.monotonic() - start) * 1000, 1),
        }

    current_counter = header["change_counter"]
    current_size = header["file_size"]
    last_known = state.get("databases", {}).get(db_key, {})
    last_counter = last_known.get("change_counter", -1)

    # Step 2: Compare change counter
    if current_counter == last_counter and current_size == last_known.get("file_size", -1):
        duration = round((time.monotonic() - start) * 1000, 1)
        logger.info(
            f"  {db_path.name}: unchanged (counter={current_counter}) [{duration}ms]"
        )
        return {
            "status": "unchanged",
            "change_counter": current_counter,
            "duration_ms": duration,
            "bytes_written": 0,
            "backup_path": None,
        }

    # Step 3: Database has changed — perform incremental backup
    now_str = datetime.now().strftime("%Y-%m-%dT%H-%M")
    backup_dir.mkdir(parents=True, exist_ok=True)

    # Strategy A: If WAL file exists, copy just the WAL
    wal_path = db_path.with_suffix(db_path.suffix + "-wal")
    bytes_written = 0
    backup_path = None

    if wal_path.exists() and wal_path.stat().st_size > 0:
        wal_backup = backup_dir / f"{db_path.stem}_{now_str}_incr.wal"
        shutil.copy2(str(wal_path), str(wal_backup))
        bytes_written = wal_backup.stat().st_size
        backup_path = str(wal_backup)
        logger.info(
            f"  {db_path.name}: WAL backup ({bytes_written / 1024:.1f} KB)"
        )
    else:
        # Strategy B: No WAL → use backup API with page stepping for speed
        # backup() with pages=-1 copies all pages, but we can step through
        # N pages at a time to allow concurrent reads
        incr_db_path = backup_dir / f"{db_path.stem}_{now_str}_incr.db"
        try:
            src_conn = sqlite3.connect(str(db_path))
            dst_conn = sqlite3.connect(str(incr_db_path))
            # Step through 100 pages at a time (non-blocking for readers)
            with dst_conn:
                src_conn.backup(dst_conn, pages=100, sleep=0.01)
            dst_conn.close()
            src_conn.close()
            bytes_written = incr_db_path.stat().st_size
            backup_path = str(incr_db_path)
            logger.info(
                f"  {db_path.name}: stepped backup "
                f"({bytes_written / 1_000_000:.1f} MB, "
                f"Δcounter {last_counter}→{current_counter})"
            )
        except Exception as e:
            # Last resort: full file copy
            try:
                shutil.copy2(str(db_path), str(incr_db_path))
                bytes_written = incr_db_path.stat().st_size
                backup_path = str(incr_db_path)
                logger.info(
                    f"  {db_path.name}: file-copy fallback "
                    f"({bytes_written / 1_000_000:.1f} MB)"
                )
            except Exception as e2:
                return {
                    "status": "failed",
                    "error": str(e2),
                    "duration_ms": round((time.monotonic() - start) * 1000, 1),
                }

    # Step 4: Update state
    state.setdefault("databases", {})[db_key] = {
        "change_counter": current_counter,
        "page_count": header["page_count"],
        "file_size": current_size,
        "last_incremental_at": datetime.now(timezone.utc).isoformat(),
        "last_backup_path": backup_path,
    }
    _save_incremental_state(state)

    duration = round((time.monotonic() - start) * 1000, 1)
    return {
        "status": "backed_up",
        "change_counter": current_counter,
        "delta_counter": current_counter - last_counter if last_counter >= 0 else "first",
        "duration_ms": duration,
        "bytes_written": bytes_written,
        "backup_path": backup_path,
    }


def incremental_backup_json(
    json_path: Path, backup_dir: Path
) -> Dict[str, Any]:
    """
    Near-instant incremental backup for JSON files using SHA-256 hash comparison.
    """
    start = time.monotonic()
    state = _load_incremental_state()
    file_key = str(json_path.relative_to(PROJECT_ROOT))

    current_hash = _hash_file(json_path)
    last_known = state.get("databases", {}).get(file_key, {})
    last_hash = last_known.get("hash", "")

    if current_hash == last_hash:
        duration = round((time.monotonic() - start) * 1000, 1)
        logger.info(f"  {json_path.name}: unchanged [{duration}ms]")
        return {
            "status": "unchanged",
            "duration_ms": duration,
            "bytes_written": 0,
        }

    # Changed — copy the file
    now_str = datetime.now().strftime("%Y-%m-%dT%H-%M")
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup_name = f"{json_path.stem}_{now_str}_incr{json_path.suffix}"
    backup_path = backup_dir / backup_name
    shutil.copy2(str(json_path), str(backup_path))
    bytes_written = backup_path.stat().st_size

    state.setdefault("databases", {})[file_key] = {
        "hash": current_hash,
        "file_size": json_path.stat().st_size,
        "last_incremental_at": datetime.now(timezone.utc).isoformat(),
    }
    _save_incremental_state(state)

    duration = round((time.monotonic() - start) * 1000, 1)
    logger.info(
        f"  {json_path.name}: backed up ({bytes_written / 1024:.1f} KB) [{duration}ms]"
    )
    return {
        "status": "backed_up",
        "duration_ms": duration,
        "bytes_written": bytes_written,
        "backup_path": str(backup_path),
    }


def run_incremental_backup(
    databases: Optional[List[str]] = None,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """
    Run near-instant incremental backup of all critical databases.

    Only copies data that has changed since last backup.
    Typical runtime: <100ms when nothing changed, <2s when WAL exists.
    """
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    start = time.monotonic()

    db_list = databases or CRITICAL_DATABASES
    results = {
        "mode": "incremental",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "databases": [],
        "total_bytes_written": 0,
        "n_unchanged": 0,
        "n_backed_up": 0,
    }

    for db_rel in db_list:
        db_path = PROJECT_ROOT / db_rel
        if not db_path.exists():
            results["databases"].append({
                "source": db_rel,
                "status": "skipped",
            })
            continue

        if dry_run:
            if db_path.suffix == ".db":
                header = _read_sqlite_header(db_path)
                state = _load_incremental_state()
                db_key = str(db_path.relative_to(PROJECT_ROOT))
                last = state.get("databases", {}).get(db_key, {})
                changed = (
                    header.get("change_counter", -1) != last.get("change_counter", -1)
                    or header.get("file_size", -1) != last.get("file_size", -1)
                )
                results["databases"].append({
                    "source": db_rel,
                    "status": "would_backup" if changed else "unchanged",
                    "change_counter": header.get("change_counter"),
                    "last_counter": last.get("change_counter"),
                })
            else:
                results["databases"].append({
                    "source": db_rel,
                    "status": "would_check_hash",
                })
            continue

        if db_path.suffix == ".db":
            result = incremental_backup_sqlite(db_path, BACKUP_DIR)
        elif db_path.suffix == ".json":
            result = incremental_backup_json(db_path, BACKUP_DIR)
        else:
            result = {"status": "unsupported_format"}

        result["source"] = db_rel
        results["databases"].append(result)
        results["total_bytes_written"] += result.get("bytes_written", 0)

        if result.get("status") == "unchanged":
            results["n_unchanged"] += 1
        elif result.get("status") == "backed_up":
            results["n_backed_up"] += 1

    total_ms = round((time.monotonic() - start) * 1000, 1)
    results["total_duration_ms"] = total_ms

    # Log
    if not dry_run:
        log_backup({
            "timestamp": results["timestamp"],
            "mode": "incremental",
            "n_backed_up": results["n_backed_up"],
            "n_unchanged": results["n_unchanged"],
            "total_bytes_written": results["total_bytes_written"],
            "total_duration_ms": total_ms,
        })

    return results


# =============================================================================
# FULL BACKUP ENGINE
# =============================================================================

def sqlite_online_backup(src_path: Path, dst_path: Path) -> bool:
    """
    Use SQLite's built-in online backup API for consistent snapshots.
    Falls back to file copy if the backup API fails (e.g., disk I/O on
    virtiofs mounts).
    """
    # Try online backup API first (safest for concurrent access)
    try:
        src_conn = sqlite3.connect(str(src_path))
        dst_conn = sqlite3.connect(str(dst_path))
        src_conn.backup(dst_conn)
        dst_conn.close()
        src_conn.close()
        return True
    except Exception as e:
        logger.warning(f"SQLite backup API failed ({e}), falling back to file copy")

    # Fallback: simple file copy (safe if no concurrent writers)
    try:
        shutil.copy2(str(src_path), str(dst_path))
        # Verify the copy is readable
        conn = sqlite3.connect(str(dst_path))
        integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
        conn.close()
        if integrity == "ok":
            logger.info(f"File-copy backup succeeded for {src_path.name}")
            return True
        else:
            logger.error(f"File-copy backup integrity failed: {integrity}")
            return False
    except Exception as e2:
        logger.error(f"File-copy fallback also failed for {src_path}: {e2}")
        return False


def verify_backup(backup_path: Path, original_path: Path) -> Dict[str, Any]:
    """Verify backup integrity by checking structure and row counts."""
    result = {"verified": False, "checks": []}

    try:
        conn = sqlite3.connect(str(backup_path))
        # Integrity check
        integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
        result["checks"].append({"integrity_check": integrity})

        if integrity != "ok":
            conn.close()
            return result

        # Compare table counts with original
        orig_conn = sqlite3.connect(str(original_path))
        orig_tables = {
            r[0] for r in orig_conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
        backup_tables = {
            r[0] for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }

        result["checks"].append({
            "tables_match": orig_tables == backup_tables,
            "original_tables": len(orig_tables),
            "backup_tables": len(backup_tables),
        })

        # Spot-check row counts on key tables
        for table in sorted(orig_tables & backup_tables):
            if table.startswith("sqlite_"):
                continue
            try:
                orig_count = orig_conn.execute(
                    f'SELECT COUNT(*) FROM "{table}"'
                ).fetchone()[0]
                backup_count = conn.execute(
                    f'SELECT COUNT(*) FROM "{table}"'
                ).fetchone()[0]
                if orig_count != backup_count:
                    result["checks"].append({
                        "table": table,
                        "original_rows": orig_count,
                        "backup_rows": backup_count,
                        "match": False,
                    })
            except Exception:
                pass

        orig_conn.close()
        conn.close()
        result["verified"] = True

    except Exception as e:
        result["error"] = str(e)

    return result


def backup_json_file(src_path: Path, dst_path: Path) -> bool:
    """Back up a JSON file with simple copy."""
    try:
        shutil.copy2(str(src_path), str(dst_path))
        # Verify it's valid JSON
        json.loads(dst_path.read_text(encoding="utf-8"))
        return True
    except Exception as e:
        logger.error(f"JSON backup failed for {src_path}: {e}")
        return False


def compress_backup(backup_path: Path) -> Optional[Path]:
    """Compress a backup file with gzip."""
    gz_path = backup_path.with_suffix(backup_path.suffix + ".gz")
    try:
        with open(backup_path, "rb") as f_in:
            with gzip.open(gz_path, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
        backup_path.unlink()
        return gz_path
    except Exception as e:
        logger.error(f"Compression failed for {backup_path}: {e}")
        return None


def log_backup(entry: Dict[str, Any]) -> None:
    """Append to the backup audit log."""
    log_entries = []
    if BACKUP_LOG.exists():
        try:
            log_entries = json.loads(BACKUP_LOG.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, IOError):
            pass

    log_entries.append(entry)

    # Keep last 500 entries
    if len(log_entries) > 500:
        log_entries = log_entries[-500:]

    BACKUP_LOG.write_text(
        json.dumps(log_entries, indent=2, default=str),
        encoding="utf-8",
    )


def rotate_backups() -> int:
    """Remove old backups per retention policy."""
    removed = 0
    now = datetime.now(timezone.utc)

    for backup_file in BACKUP_DIR.glob("*"):
        if backup_file.name == "backup_log.json":
            continue
        if not backup_file.is_file():
            continue

        age = now - datetime.fromtimestamp(
            backup_file.stat().st_mtime, tz=timezone.utc
        )

        # Tagged backups get longer retention
        if "_tag_" in backup_file.name:
            max_age = timedelta(days=TAGGED_RETENTION)
        elif "_weekly_" in backup_file.name:
            max_age = timedelta(days=WEEKLY_RETENTION * 7)
        else:
            max_age = timedelta(days=DAILY_RETENTION)

        if age > max_age:
            try:
                backup_file.unlink()
                removed += 1
                logger.info(f"Rotated old backup: {backup_file.name} (age: {age.days}d)")
            except OSError:
                pass

    return removed


def list_backups() -> List[Dict[str, Any]]:
    """List all existing backups with metadata."""
    backups = []
    for f in sorted(BACKUP_DIR.glob("*")):
        if f.name == "backup_log.json" or not f.is_file():
            continue
        stat = f.stat()
        backups.append({
            "file": f.name,
            "size_mb": round(stat.st_size / 1_000_000, 1),
            "modified": datetime.fromtimestamp(
                stat.st_mtime, tz=timezone.utc
            ).strftime("%Y-%m-%d %H:%M"),
            "path": str(f),
        })
    return backups


def run_backup(
    databases: Optional[List[str]] = None,
    tag: Optional[str] = None,
    dry_run: bool = False,
    compress: bool = False,
) -> Dict[str, Any]:
    """
    Execute backup of all critical databases.

    Returns summary with backup paths and verification results.
    """
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y-%m-%d")
    is_weekly = now.weekday() == 0  # Monday = weekly backup

    db_list = databases or CRITICAL_DATABASES
    results = {
        "timestamp": now.isoformat(),
        "tag": tag,
        "databases": [],
        "total_size_bytes": 0,
    }

    for db_rel in db_list:
        db_path = PROJECT_ROOT / db_rel
        if not db_path.exists():
            logger.info(f"Skipping (not found): {db_rel}")
            results["databases"].append({
                "source": db_rel,
                "status": "skipped",
                "reason": "file not found",
            })
            continue

        # Build backup filename
        stem = db_path.stem
        suffix = db_path.suffix
        if tag:
            backup_name = f"{stem}_{date_str}_tag_{tag}{suffix}"
        elif is_weekly:
            backup_name = f"{stem}_{date_str}_weekly{suffix}"
        else:
            backup_name = f"{stem}_{date_str}_daily{suffix}"

        backup_path = BACKUP_DIR / backup_name

        if dry_run:
            size = db_path.stat().st_size
            logger.info(
                f"[DRY-RUN] Would backup: {db_rel} → {backup_name} "
                f"({size / 1_000_000:.1f} MB)"
            )
            results["databases"].append({
                "source": db_rel,
                "status": "dry_run",
                "backup_name": backup_name,
                "size_bytes": size,
            })
            results["total_size_bytes"] += size
            continue

        # Perform backup
        logger.info(f"Backing up: {db_rel} → {backup_name}")

        if suffix == ".db":
            success = sqlite_online_backup(db_path, backup_path)
        else:
            success = backup_json_file(db_path, backup_path)

        if not success:
            results["databases"].append({
                "source": db_rel,
                "status": "failed",
            })
            continue

        size = backup_path.stat().st_size
        results["total_size_bytes"] += size

        # Verify SQLite backups
        verification = {}
        if suffix == ".db":
            verification = verify_backup(backup_path, db_path)
            if not verification.get("verified"):
                logger.warning(f"Backup verification FAILED for {db_rel}")

        # Compress if requested
        final_path = backup_path
        if compress and size > 1_000_000:  # Only compress > 1MB
            compressed = compress_backup(backup_path)
            if compressed:
                final_path = compressed
                size = compressed.stat().st_size

        results["databases"].append({
            "source": db_rel,
            "status": "ok",
            "backup_path": str(final_path),
            "size_bytes": size,
            "verified": verification.get("verified", None),
        })

        logger.info(
            f"  ✓ {backup_name} ({size / 1_000_000:.1f} MB)"
            f"{' [verified]' if verification.get('verified') else ''}"
        )

    # Rotate old backups
    if not dry_run:
        rotated = rotate_backups()
        results["rotated"] = rotated
        if rotated:
            logger.info(f"Rotated {rotated} old backups")

    # Log the operation
    if not dry_run:
        log_backup({
            "timestamp": now.isoformat(),
            "tag": tag,
            "n_backed_up": sum(
                1 for d in results["databases"] if d["status"] == "ok"
            ),
            "total_size_bytes": results["total_size_bytes"],
        })

    return results


def restore_backup(backup_path: str, target: Optional[str] = None) -> bool:
    """
    Restore a database from a backup file.

    If target is not specified, restores to the original location
    (inferred from the backup filename).
    """
    src = Path(backup_path)
    if not src.exists():
        logger.error(f"Backup file not found: {backup_path}")
        return False

    # Decompress if needed
    if src.suffix == ".gz":
        logger.info("Decompressing backup...")
        decompressed = src.with_suffix("")
        with gzip.open(src, "rb") as f_in:
            with open(decompressed, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
        src = decompressed

    if target:
        dst = Path(target)
    else:
        # Infer original location from filename
        # e.g., web_persistence_2026-02-27_daily.db → data/web_persistence.db
        stem = src.stem
        # Remove date and tag suffixes
        for pattern in ["_daily", "_weekly"]:
            if pattern in stem:
                stem = stem[:stem.index(pattern)]
                break
        if "_tag_" in stem:
            stem = stem[:stem.index("_tag_")]
        # Remove date
        import re
        stem = re.sub(r"_\d{4}-\d{2}-\d{2}$", "", stem)

        dst = PROJECT_ROOT / "data" / f"{stem}{src.suffix}"

    logger.info(f"Restoring {src.name} → {dst}")

    # Backup current file before overwriting
    if dst.exists():
        pre_restore = dst.with_suffix(dst.suffix + ".pre_restore")
        shutil.copy2(str(dst), str(pre_restore))
        logger.info(f"Saved pre-restore copy: {pre_restore.name}")

    # Restore
    shutil.copy2(str(src), str(dst))

    # Verify
    if dst.suffix == ".db":
        try:
            conn = sqlite3.connect(str(dst))
            integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
            conn.close()
            if integrity == "ok":
                logger.info("Restored database integrity: OK")
                return True
            else:
                logger.error(f"Restored database integrity: {integrity}")
                return False
        except Exception as e:
            logger.error(f"Restoration verification failed: {e}")
            return False

    return True


def _restore_incremental(wal_backup: str, target: Optional[str] = None) -> int:
    """
    Restore by applying an incremental WAL backup on top of the most recent
    full backup of the same database.

    Strategy:
      1. Find the most recent full backup matching the WAL's database name
      2. Copy that full backup to the restore target
      3. Copy the WAL file alongside it (same directory, standard naming)
      4. Open with SQLite → WAL checkpoint applies automatically
      5. Verify integrity
    """
    wal_path = Path(wal_backup)
    if not wal_path.exists():
        logger.error(f"WAL backup not found: {wal_backup}")
        return 1

    # Extract database stem from WAL filename
    # e.g., web_persistence_2026-02-27T14-30_incr.wal → web_persistence
    stem = wal_path.stem  # web_persistence_2026-02-27T14-30_incr
    import re
    db_stem = re.sub(r"_\d{4}-\d{2}-\d{2}T\d{2}-\d{2}_incr$", "", stem)

    # Find most recent full backup
    full_candidates = sorted(
        BACKUP_DIR.glob(f"{db_stem}_*_daily.db"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    # Also check weekly and tagged
    full_candidates += sorted(
        BACKUP_DIR.glob(f"{db_stem}_*_weekly.db"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    full_candidates += sorted(
        BACKUP_DIR.glob(f"{db_stem}_*_tag_*.db"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )

    if not full_candidates:
        logger.error(
            f"No full backup found for '{db_stem}'. "
            f"Cannot apply incremental WAL without a base."
        )
        return 1

    base_backup = full_candidates[0]
    logger.info(f"Using base backup: {base_backup.name}")

    # Determine restore target
    if target:
        dst = Path(target)
    else:
        dst = PROJECT_ROOT / "data" / f"{db_stem}.db"

    # Safety: backup current file before overwriting
    if dst.exists():
        pre_restore = dst.with_suffix(".db.pre_restore")
        shutil.copy2(str(dst), str(pre_restore))
        logger.info(f"Saved pre-restore copy: {pre_restore.name}")

    # Step 1: Copy full backup to target
    shutil.copy2(str(base_backup), str(dst))

    # Step 2: Copy WAL alongside target (SQLite will checkpoint on open)
    wal_dst = Path(str(dst) + "-wal")
    shutil.copy2(str(wal_path), str(wal_dst))

    # Step 3: Open database → triggers WAL checkpoint
    try:
        conn = sqlite3.connect(str(dst))
        # Force WAL checkpoint
        conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
        conn.close()

        # Clean up WAL after checkpoint
        if wal_dst.exists():
            wal_dst.unlink()

        if integrity == "ok":
            logger.info(f"Incremental restore complete. Integrity: OK")
            logger.info(f"Restored to: {dst}")
            return 0
        else:
            logger.error(f"Restored database integrity: {integrity}")
            return 1
    except Exception as e:
        logger.error(f"Incremental restore failed: {e}")
        return 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description="ATLAS Database Backup Service — Full + Incremental"
    )
    parser.add_argument(
        "--mode", choices=["full", "incremental"], default="full",
        help="Backup mode: 'full' (default, complete snapshot) or "
             "'incremental' (near-instant, only changed data)"
    )
    parser.add_argument(
        "--db", type=str, nargs="*",
        help="Specific database(s) to back up (relative to project root)"
    )
    parser.add_argument(
        "--tag", type=str,
        help="Tag for this backup (e.g., 'before_migration', 'pre_bulk_load')"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show what would be backed up without doing it"
    )
    parser.add_argument(
        "--compress", action="store_true",
        help="Compress backups with gzip (full mode only)"
    )
    parser.add_argument(
        "--list", action="store_true", dest="list_backups",
        help="List existing backups"
    )
    parser.add_argument(
        "--restore", type=str,
        help="Restore from a full backup file"
    )
    parser.add_argument(
        "--restore-incremental", type=str,
        help="Restore by applying an incremental WAL backup on top of "
             "the most recent full backup"
    )
    parser.add_argument(
        "--restore-target", type=str,
        help="Target path for restore (optional, infers from filename)"
    )
    args = parser.parse_args()

    # --list: show existing backups
    if args.list_backups:
        backups = list_backups()
        if not backups:
            print("No backups found.")
            return 0
        print(f"\n{'File':<55} {'Size':>8} {'Modified':<18}")
        print("-" * 85)
        for b in backups:
            print(f"{b['file']:<55} {b['size_mb']:>6.1f}MB {b['modified']:<18}")
        total = sum(b["size_mb"] for b in backups)
        print(f"\nTotal: {len(backups)} backups, {total:.1f} MB")
        return 0

    # --restore: restore from full backup
    if args.restore:
        success = restore_backup(args.restore, args.restore_target)
        return 0 if success else 1

    # --restore-incremental: apply WAL on top of last full backup
    if args.restore_incremental:
        return _restore_incremental(args.restore_incremental, args.restore_target)

    # Dispatch by mode
    if args.mode == "incremental":
        results = run_incremental_backup(
            databases=args.db,
            dry_run=args.dry_run,
        )

        # Summary
        print(f"\nIncremental backup summary:")
        print(f"  Backed up: {results['n_backed_up']}")
        print(f"  Unchanged: {results['n_unchanged']}")
        print(f"  Total bytes written: {results['total_bytes_written']:,}")
        print(f"  Duration: {results['total_duration_ms']:.0f}ms")
        return 0

    else:
        # Full backup (default)
        results = run_backup(
            databases=args.db,
            tag=args.tag,
            dry_run=args.dry_run,
            compress=args.compress,
        )

        # Summary
        ok = sum(1 for d in results["databases"] if d["status"] == "ok")
        skipped = sum(1 for d in results["databases"] if d["status"] == "skipped")
        failed = sum(1 for d in results["databases"] if d["status"] == "failed")
        total_mb = results["total_size_bytes"] / 1_000_000

        print(f"\nFull backup summary: {ok} OK, {skipped} skipped, {failed} failed ({total_mb:.1f} MB)")
        if results.get("rotated"):
            print(f"Rotated {results['rotated']} old backups")

        return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
