#!/usr/bin/env python3
"""Run the core Article Eater health checks in sequence.

This is the recommended entrypoint for students and new contributors.
It runs:

1. scripts/sanity_check.py
2. scripts/offline_pipeline_smoke.py

and prints a short human-readable summary.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _run(label: str, script: str) -> bool:
    print(f"[run_all_checks] Running {label} ...")
    proc = subprocess.run(
        [sys.executable, str(ROOT / script)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    print(proc.stdout)
    if proc.returncode != 0:
        print(f"[run_all_checks] {label} FAILED (exit code {proc.returncode})")
        return False
    print(f"[run_all_checks] {label} OK")
    return True


def main() -> None:
    ok_sanity = _run("sanity_check", "scripts/sanity_check.py")
    ok_smoke = False
    if ok_sanity:
        ok_smoke = _run("offline_pipeline_smoke", "scripts/offline_pipeline_smoke.py")
    else:
        print("[run_all_checks] Skipping offline_pipeline_smoke because sanity_check failed.")

    print("\n[run_all_checks] SUMMARY")
    print(f" - sanity_check: {'OK' if ok_sanity else 'FAILED'}")
    print(f" - offline_pipeline_smoke: {'OK' if ok_smoke else 'SKIPPED/FAILED'}")

    if not (ok_sanity and ok_smoke):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
