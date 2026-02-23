#!/usr/bin/env python3
"""Lightweight repository sanity check for Article Eater v20.7.3.

This script is safe to run on any machine with the dependencies installed.
It performs:
- compile of active Python source roots
- import checks for key backend/agent modules
- scan for TODO / NotImplementedError / # STUB: in src/
"""
from __future__ import annotations

import py_compile
import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
ACTIVE_COMPILE_DIRS = ("app", "src", "scripts", "tests", "lib")
TODO_ALLOWLIST_PATH = ROOT / "config" / "sanity_todo_allowlist.txt"
SKIP_PATH_PARTS = {
    "_archive",
    "archive",
    "__MACOSX",
    "__pycache__",
    "node_modules",
    "venv",
    ".venv",
    "quarantine",
    "ruthless_bundle_2026-02-08",
}
TODO_PATTERNS = ("TODO", "NotImplementedError", "# STUB:")


def _iter_compile_files() -> list[pathlib.Path]:
    files: list[pathlib.Path] = []
    for rel_dir in ACTIVE_COMPILE_DIRS:
        base = ROOT / rel_dir
        if not base.exists():
            continue
        for path in base.rglob("*.py"):
            if path.name.startswith("._"):
                continue
            if any(part in SKIP_PATH_PARTS for part in path.parts):
                continue
            files.append(path)
    return sorted(set(files))


def _compile_active_roots() -> tuple[bool, list[str]]:
    errors: list[str] = []
    for path in _iter_compile_files():
        try:
            py_compile.compile(str(path), doraise=True)
        except Exception as exc:
            errors.append(f"{path.relative_to(ROOT)}: {exc}")
    return (len(errors) == 0), errors


def _load_todo_allowlist(path: pathlib.Path) -> set[str]:
    if not path.exists():
        return set()
    allowed: set[str] = set()
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        item = line.strip()
        if not item or item.startswith("#"):
            continue
        allowed.add(item)
    return allowed


def main() -> None:
    print(f"[sanity_check] repo root: {ROOT}")
    # 1) Compile active Python roots only.
    ok, compile_errors = _compile_active_roots()
    if not ok:
        print("[sanity_check] compile step failed")
        for item in compile_errors[:20]:
            print(" -", item)
        if len(compile_errors) > 20:
            print(f" - ... {len(compile_errors) - 20} additional compile errors")
        raise SystemExit(1)

    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

    errors: list[str] = []
    warnings: list[str] = []

    # 2) Import checks (hard failures)
    try:
        from src.agents.agent_stubs import Agent_Finder, Agent_Aggregator, Agent_Linker  # type: ignore
    except Exception as e:  # pragma: no cover - defensive
        errors.append(f"Import error: src.agents.agent_stubs: {e}")

    try:
        from src.services.graph_service_fallback import JSONLGraphStore  # type: ignore
    except Exception as e:
        errors.append(f"Import error: src.services.graph_service_fallback: {e}")

    try:
        from src.services.service_locator import get_graph_service  # type: ignore
    except Exception as e:
        errors.append(f"Import error: src.services.service_locator: {e}")

    try:
        from src.services.bbn_calibrator import compute_confidence_for_finding  # type: ignore
    except Exception as e:
        errors.append(f"Import error: src.services.bbn_calibrator: {e}")

    # Optional: main GUI app (treated as a warning if dependencies are missing)
    try:
        import apps.user_rules_gui.app as user_rules_app  # type: ignore  # noqa: F401
    except Exception as e:
        warnings.append(f"Import warning: apps.user_rules_gui.app: {e}")

    # 3) Scan src/ for TODO / NotImplementedError / # STUB:
    allowed_todo_paths = _load_todo_allowlist(TODO_ALLOWLIST_PATH)
    bad_hits: list[tuple[str, str]] = []
    allowed_hits: list[tuple[str, str]] = []
    src_path = ROOT / "src"
    if src_path.exists():
        for path in src_path.rglob("*.py"):
            text = path.read_text(encoding="utf-8", errors="ignore")
            rel_path = str(path.relative_to(ROOT))
            for pat in TODO_PATTERNS:
                if pat in text:
                    if rel_path in allowed_todo_paths:
                        allowed_hits.append((rel_path, pat))
                    else:
                        bad_hits.append((rel_path, pat))

    if bad_hits:
        msg = "Found disallowed TODO/NotImplemented/STUB markers:\n" + "\n".join(
            f"- {p} contains {pat}" for p, pat in bad_hits
        )
        errors.append(msg)
    if allowed_hits:
        warnings.append(
            "Allowlisted TODO markers detected:\n"
            + "\n".join(f"- {p} contains {pat}" for p, pat in allowed_hits)
        )

    if errors:
        print("[sanity_check] FAIL")
        for e in errors:
            print(" -", e)
        if warnings:
            print("[sanity_check] WARNINGS:")
            for w in warnings:
                print(" -", w)
        raise SystemExit(1)

    print("[sanity_check] OK")
    if warnings:
        print("[sanity_check] WARNINGS (non-fatal):")
        for w in warnings:
            print(" -", w)


if __name__ == "__main__":
    main()
