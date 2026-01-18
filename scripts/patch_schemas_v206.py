#!/usr/bin/env python3
# Governance-safe: archives original, idempotently adds raw_abstract field to SevenPanelArtifact (if present)
from pathlib import Path
import re, time, shutil
root = Path('.'); ts = time.strftime('%Y%m%d_%H%M%S')
target = root/'src/contracts/schemas.py'
if not target.exists():
    print("schemas.py not found; nothing to patch.")
    raise SystemExit(0)
txt = target.read_text(encoding='utf-8', errors='ignore')
arch = root/f'archive/_replaced_{ts}/src/contracts/schemas.py'
arch.parent.mkdir(parents=True, exist_ok=True)
arch.write_text(txt, encoding='utf-8')
if 'class SevenPanelArtifact' in txt and 'raw_abstract' not in txt:
    patched = re.sub(r'(class\s+SevenPanelArtifact\s*\(.*?\):\s*)(.*?)\n\n',
                     lambda m: m.group(1)+m.group(2)+
                               "\n    raw_abstract: str | None = Field(None, description='The raw abstract text.')\n\n",
                     txt, flags=re.S)
    target.write_text(patched, encoding='utf-8')
    print("Patched SevenPanelArtifact: added raw_abstract.")
else:
    print("No change needed (already present or class missing).")