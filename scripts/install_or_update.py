#!/usr/bin/env python3
import os, time, shutil
from pathlib import Path
SRC = Path(__file__).resolve().parents[1]
DST = Path(os.environ.get('AE_TARGET_DIR','.') ).resolve()
backup = DST / 'archive' / f"_replaced_{int(time.time())}"
def copy_with_backup(src_file: Path):
    rel = src_file.relative_to(SRC)
    dst_file = DST / rel
    dst_file.parent.mkdir(parents=True, exist_ok=True)
    if dst_file.exists():
        b = backup / rel; b.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(dst_file, b)
    shutil.copy2(src_file, dst_file)
def main():
    backup.mkdir(parents=True, exist_ok=True)
    for p in SRC.rglob('*'):
        if p.is_file() and not str(p).startswith(str(SRC / 'archive')):
            copy_with_backup(p)
    print("Install/Update complete ->", DST)
if __name__ == "__main__":
    main()