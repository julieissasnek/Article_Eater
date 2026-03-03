"""
Database Locator — Sandbox-Safe DB Path Resolution
===================================================

Centralizes all SQLite database path resolution for the Article Eater system.
Detects MacOS sandbox restrictions and automatically falls back to /tmp copies.

Usage:
    from src.utils.db_locator import resolve_db_path

    db_path = resolve_db_path("data/web_persistence.db")
    # Returns original path if writable, otherwise /tmp/web_persistence.db

Created: 2026-03-02
"""

import os
import shutil
import logging
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)

# Cache to avoid re-checking the same paths
_resolved_cache: dict = {}


def _is_writable(path: str) -> bool:
    """Test if a file path is writable by attempting a dummy lockfile."""
    try:
        lock_path = path + ".locktest"
        with open(lock_path, 'w') as f:
            f.write("test")
        os.remove(lock_path)
        return True
    except (OSError, PermissionError):
        return False


def resolve_db_path(original_path: str, copy_if_exists: bool = True) -> str:
    """
    Resolve a database path, falling back to /tmp if sandbox restricted.

    Args:
        original_path: The intended database file path
        copy_if_exists: If True, copy the original DB to /tmp so data is preserved

    Returns:
        A writable path for the database file
    """
    if original_path in _resolved_cache:
        return _resolved_cache[original_path]

    original = Path(original_path).resolve()

    # If the file exists and is writable, use it directly
    if original.exists() and _is_writable(str(original)):
        _resolved_cache[original_path] = str(original)
        return str(original)

    # If the parent directory is writable (file may not exist yet), allow creation
    if original.parent.exists() and _is_writable(str(original.parent / ".write_test_db")):
        _resolved_cache[original_path] = str(original)
        return str(original)

    # Sandbox detected — fall back to /tmp
    tmp_path = Path(tempfile.gettempdir()) / original.name
    logger.warning(
        f"Sandbox detected: '{original}' is not writable. "
        f"Falling back to '{tmp_path}'"
    )

    # Copy the original DB to /tmp if it exists and hasn't been copied yet
    if copy_if_exists and original.exists() and not tmp_path.exists():
        try:
            shutil.copy2(str(original), str(tmp_path))
            logger.info(f"Copied '{original}' → '{tmp_path}' for sandbox fallback")
        except Exception as e:
            logger.warning(f"Could not copy DB to /tmp: {e}")

    _resolved_cache[original_path] = str(tmp_path)
    return str(tmp_path)


def clear_cache():
    """Clear the resolution cache (useful for testing)."""
    _resolved_cache.clear()
