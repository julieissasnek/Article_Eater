#!/usr/bin/env python3
"""
deconcat.py — reconstruct files from a concatenated EnvKit pack.

Marker format:
----- FILE PATH: <relpath>
----- CONTENT START -----
<file bytes (utf-8)>
----- CONTENT END -----

Usage:
  python3 deconcat.py EnvKit_Bootstrap_Pack_v0.2.1_concatenated.txt [--out .] [--force]
"""
from __future__ import annotations
import argparse
from pathlib import Path

HEADER = "----- FILE PATH: "
START = "----- CONTENT START -----"
END = "----- CONTENT END -----"

def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("concat_path", type=Path)
    ap.add_argument("--out", type=Path, default=Path("."))
    ap.add_argument("--force", action="store_true")
    return ap.parse_args()

def main():
    args = parse_args()
    lines = args.concat_path.read_text(encoding="utf-8").splitlines()

    i = 0
    files = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith(HEADER):
            rel = line[len(HEADER):].strip()
            if not rel:
                raise SystemExit(f"Bad marker at line {i+1}: empty path")
            i += 1
            while i < len(lines) and lines[i] == "":
                i += 1
            if i >= len(lines) or lines[i] != START:
                raise SystemExit(f"Bad marker near {rel}: missing CONTENT START")
            i += 1
            buf = []
            while i < len(lines) and lines[i] != END:
                buf.append(lines[i])
                i += 1
            if i >= len(lines):
                raise SystemExit(f"Bad marker near {rel}: missing CONTENT END")
            out_path = (args.out / rel).resolve()
            out_path.parent.mkdir(parents=True, exist_ok=True)
            if out_path.exists() and not args.force:
                raise SystemExit(f"Refusing to overwrite existing file: {out_path} (use --force)")
            out_path.write_text("\n".join(buf) + "\n", encoding="utf-8")
            files += 1
        i += 1

    print(f"OK: wrote {files} files into {args.out.resolve()}")

if __name__ == "__main__":
    main()
