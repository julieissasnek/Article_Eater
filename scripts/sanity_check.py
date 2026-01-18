#!/usr/bin/env python3
"""Lightweight repository sanity check for Article Eater v20.7.3.

This script is safe to run on any machine with the dependencies installed.
It performs:
- compileall over the repo
- import checks for key backend/agent modules
- scan for TODO / NotImplementedError / # STUB: in src/
"""
from __future__ import annotations

import compileall
import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]


def main() -> None:
    print(f"[sanity_check] repo root: {ROOT}")
    # 1) Compile all Python files
    ok = compileall.compile_dir(str(ROOT), quiet=1)
    if not ok:
        print("[sanity_check] compileall failed")
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
    patterns = ["TODO", "NotImplementedError", "# STUB:"]
    bad_hits: list[tuple[str, str]] = []
    src_path = ROOT / "src"
    if src_path.exists():
        for path in src_path.rglob("*.py"):
            text = path.read_text(encoding="utf-8", errors="ignore")
            for pat in patterns:
                if pat in text:
                    bad_hits.append((str(path.relative_to(ROOT)), pat))

    if bad_hits:
        msg = "Found disallowed TODO/NotImplemented/STUB markers:\n" + "\n".join(
            f"- {p} contains {pat}" for p, pat in bad_hits
        )
        errors.append(msg)

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
