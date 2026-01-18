#!/usr/bin/env python3
"""EnvKit v0.2 CLI"""
from __future__ import annotations
import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def run(script: str, *args) -> int:
    cmd = [str(ROOT / "bin" / script)] + list(args)
    return subprocess.call(cmd)

def main() -> int:
    ap = argparse.ArgumentParser(description="EnvKit v0.2 CLI")
    sp = ap.add_subparsers(dest="cmd", required=True)
    
    sp.add_parser("smoke", help="Run prod smoke test")
    sp.add_parser("test", help="Run tests")
    sp.add_parser("release", help="Create release")
    sp.add_parser("version", help="Show version")
    sp.add_parser("bump", help="Bump version")
    sp.add_parser("context", help="Generate AI context")
    sp.add_parser("claude-start", help="Bootstrap Claude session")
    
    diag = sp.add_parser("diagnose", help="Diagnose error")
    diag.add_argument("error", nargs="?", default="")
    
    args = ap.parse_args()
    
    cmds = {
        "smoke": lambda: run("prod_smoke.sh"),
        "test": lambda: run("test.sh"),
        "release": lambda: run("release.sh"),
        "version": lambda: run("version.sh", "check"),
        "bump": lambda: run("version.sh", "bump"),
        "context": lambda: run("context.sh"),
        "claude-start": lambda: run("claude_start.sh"),
        "diagnose": lambda: run("claude_diagnose.sh", args.error),
    }
    
    return cmds[args.cmd]()

if __name__ == "__main__":
    sys.exit(main())
