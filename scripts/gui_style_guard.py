#!/usr/bin/env python3
import sys, re
from pathlib import Path
root = Path(__file__).resolve().parents[1]
pages = list((root/'frontend'/'pages').glob('*.html'))
required = [
    (re.compile(r'<link[^>]+href="\.{2}/css/main\.css"'), 'Missing main.css link'),
    (re.compile(r'class="app-header"'), 'Missing .app-header header'),
    (re.compile(r'class="container"'), 'Missing .container wrapper'),
    (re.compile(r'class="btn\b'), 'Missing a .btn button'),
    (re.compile(r'class="card"'), 'Missing .card component'),
]
errors = []
for p in pages:
    try: s = p.read_text(encoding='utf-8', errors='ignore')
    except: continue
    for pat,msg in required:
        if not pat.search(s): errors.append(f"{p.relative_to(root)}: {msg}")
if errors:
    print("GUI Style Guard FAIL:\n" + "\n".join(errors)); sys.exit(2)
print("GUI Style Guard PASS")