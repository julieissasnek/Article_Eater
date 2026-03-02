"""
conftest.py — Test Configuration + Import Smoke Test
=====================================================

GUARD 1 (added 2026-02-28, RV5-2 prevention):
    pytest_configure imports every src/ module at startup.
    If ANY module fails to import (duplicate enum, circular import,
    syntax error), ALL tests abort with a clear message.

    ROOT CAUSE: BridgeType enum had duplicate EMPIRICAL_ASSOCIATION members
    after a global rename. 64/67 test files silently failed to collect.
    This guard makes that class of failure impossible to miss.
"""

import importlib
import os
import pkgutil
import sys
import tempfile
import warnings
from pathlib import Path

import pytest


# ═══════════════════════════════════════════════════════════════════
# GUARD 1: Import smoke test — catches broken enums, circular imports
# ═══════════════════════════════════════════════════════════════════

def _discover_modules(package_path: str, prefix: str = "") -> list:
    """Recursively discover all Python modules under a package path."""
    modules = []
    try:
        for importer, modname, ispkg in pkgutil.walk_packages(
            [package_path], prefix=prefix
        ):
            modules.append(modname)
    except Exception:
        pass
    return modules


def pytest_configure(config):
    """
    Run at pytest startup BEFORE collection.
    Imports every module in src/ to catch broken enums, syntax errors,
    circular imports, and missing dependencies immediately.
    """
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    src_path = os.path.join(project_root, "src")

    if not os.path.isdir(src_path):
        return

    # Ensure project root is on sys.path
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    failures = []
    modules = _discover_modules(src_path, prefix="src.")

    # Known optional dependencies — skip modules that fail only because of these
    OPTIONAL_DEPS = {'structlog', 'streamlit', 'google', 'google.genai', 
                     'scipy', 'numpy', 'sklearn', 'flask', 'fastapi', 'uvicorn',
                     'cv2', 'PIL', 'torch', 'torchvision', 'skimage',
                     'tensorflow', 'keras', 'midas'}

    for mod_name in modules:
        try:
            importlib.import_module(mod_name)
        except Exception as e:
            # Check if this is just a missing optional dependency
            emsg = str(e)
            is_optional = (
                isinstance(e, (ImportError, ModuleNotFoundError)) and
                any(dep in emsg for dep in OPTIONAL_DEPS)
            )
            if not is_optional:
                failures.append((mod_name, type(e).__name__, emsg[:200]))

    if failures:
        msg_lines = [
            "",
            "=" * 70,
            "IMPORT SMOKE TEST FAILED — ABORTING ALL TESTS",
            "=" * 70,
            "",
            f"{len(failures)} module(s) failed to import:",
            "",
        ]
        for mod, etype, emsg in failures:
            msg_lines.append(f"  ✗ {mod}")
            msg_lines.append(f"    {etype}: {emsg}")
            msg_lines.append("")

        msg_lines.extend([
            "Root cause: One or more source modules have import-time errors.",
            "Common causes: duplicate enum members, circular imports, syntax errors.",
            "",
            "Fix the error(s) above before running tests.",
            "=" * 70,
        ])
        pytest.exit("\n".join(msg_lines), returncode=4)


# ═══════════════════════════════════════════════════════════════════
# GUARD 2: Test count alarm — catches silent collection failures
# ═══════════════════════════════════════════════════════════════════

def pytest_collection_modifyitems(config, items):
    """Warn if test count drops dramatically (silent collection failures)."""
    MINIMUM_EXPECTED = 100  # Conservative floor; actual is ~4000+
    if len(items) < MINIMUM_EXPECTED:
        warnings.warn(
            f"\n⚠️  TEST COUNT ALARM: Only {len(items)} tests collected "
            f"(expected ≥{MINIMUM_EXPECTED}). Possible silent collection failures.",
            UserWarning,
            stacklevel=1,
        )


# ═══════════════════════════════════════════════════════════════════
# Existing: Test DB setup
# ═══════════════════════════════════════════════════════════════════

@pytest.fixture(scope="session", autouse=True)
def setup_test_db(tmp_path_factory):
    # Create a temporary sqlite database file for tests
    temp_dir = tmp_path_factory.mktemp("db")
    test_db_path = temp_dir / "test_ae.db"

    # Set the environment variable so app.db.connect uses it
    os.environ["AE_DB_PATH"] = str(test_db_path)

    # Actually create the schema in the temporary database
    try:
        from app.db import ensure_db
        ensure_db()
    except ImportError:
        pass  # app.db may not be available in all test configurations

    yield
