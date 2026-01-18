
#!/usr/bin/env python3
"""Safe update script: merges this release into an existing checkout without deleting files.
- Copies new/changed files, backs up overwritten files to archive/_replaced_<timestamp>/
- Leaves unmatched files untouched.
"""
import os, shutil, time, pathlib

SRC = pathlib.Path(__file__).resolve().parents[1]
DST = pathlib.Path(os.environ.get("AE_TARGET_DIR",".")).resolve()
backup = DST/"archive"/f"_replaced_{int(time.time())}"
backup.mkdir(parents=True, exist_ok=True)

def copy_with_backup(rel):
    src = SRC/rel
    dst = DST/rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        # backup old
        b = backup/rel
        b.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(dst, b)
    shutil.copy2(src, dst)

for p in SRC.rglob("*"):
    if p.is_file():
        rel = p.relative_to(SRC)
        if "archive/" in str(rel): 
            continue
        copy_with_backup(rel)
print("Safe update complete →", DST)