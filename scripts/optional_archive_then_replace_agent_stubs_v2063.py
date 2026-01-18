#!/usr/bin/env python3
from pathlib import Path
import time, shutil
root = Path('.')
tgt = root/'src/agents/agent_stubs.py'
if not tgt.exists():
    print('No agent_stubs.py to archive; skipping.')
else:
    ts = time.strftime('%Y%m%d_%H%M%S')
    arch = root/f'archive/_replaced_{ts}/src/agents'
    arch.mkdir(parents=True, exist_ok=True)
    shutil.copy2(tgt, arch/'agent_stubs.py')
    print(f'Archived old agent_stubs.py to {arch}')
print('Done.')