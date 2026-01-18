#!/usr/bin/env python3
from __future__ import annotations
import argparse
import subprocess
from pathlib import Path

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("action", choices=["smoke", "release"])
    args = ap.parse_args()

    root = Path(__file__).resolve().parents[1]
    script = root / "bin" / ("prod_smoke.sh" if args.action == "smoke" else "release_and_smoke.sh")
    return subprocess.call([str(script)])

if __name__ == "__main__":
    raise SystemExit(main())
