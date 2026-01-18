#!/usr/bin/env python3
"""De-concatenate a single-file bundle created with standard markers into a directory tree.
Usage:
  python deconcat.py --source /path/to/bundle.txt --out ./restored
"""
import argparse
from pathlib import Path

MARK = '----- FILE PATH:'
START = '----- CONTENT START -----'
END = '----- CONTENT END -----'

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--source', required=True)
    ap.add_argument('--out', required=True)
    args = ap.parse_args()

    src = Path(args.source)
    out_root = Path(args.out); out_root.mkdir(parents=True, exist_ok=True)

    cur_rel, buf, in_block = None, [], False
    for line in src.read_text(encoding='utf-8', errors='ignore').splitlines():
        if line.startswith(MARK):
            if cur_rel is not None:
                dest = out_root/cur_rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text('\n'.join(buf), encoding='utf-8')
            cur_rel, buf, in_block = line.split(':',1)[1].strip(), [], False
        elif line.strip() == START:
            in_block = True; buf = []
        elif line.strip() == END:
            in_block = False
        else:
            if cur_rel is not None and in_block:
                buf.append(line)
    if cur_rel is not None:
        dest = out_root/cur_rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text('\n'.join(buf), encoding='utf-8')

if __name__ == '__main__':
    main()