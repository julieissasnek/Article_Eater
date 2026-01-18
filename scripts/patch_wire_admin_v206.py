#!/usr/bin/env python3
# Governance-safe wiring of admin routes/page into FastAPI app
from pathlib import Path
import time
candidates = [Path('app/main.py'), Path('src/api/main.py'), Path('src/main.py'), Path('main.py')]
ts = time.strftime('%Y%m%d_%H%M%S')
wired = False
for mf in candidates:
    if mf.exists():
        s = mf.read_text(encoding='utf-8', errors='ignore')
        bak = Path(f'archive/_replaced_{ts}/{mf}')
        bak.parent.mkdir(parents=True, exist_ok=True)
        bak.write_text(s, encoding='utf-8')
        add = ""
        if "from src.services.admin_service import router as admin_router" not in s:
            add += "\nfrom src.services.admin_service import router as admin_router\n"
        if "app.include_router(admin_router" not in s:
            add += "\n# Admin API routes (v20.6)\napp.include_router(admin_router, prefix='/api/admin', tags=['admin'])\n"
        if "@app.get('/admin')" not in s and '@app.get("/admin")' not in s:
            add += ("\nfrom fastapi.responses import HTMLResponse\nfrom pathlib import Path as _Path\n"
                    "@app.get('/admin', response_class=HTMLResponse)\n"
                    "def admin_page():\n"
                    "    p = _Path('src/gui/templates/admin.html')\n"
                    "    return p.read_text(encoding='utf-8', errors='ignore') if p.exists() else '<h1>Admin Control Room</h1>'\n")
        mf.write_text(s+add, encoding='utf-8')
        print(f"Wired admin into {mf}")
        wired = True
        break
if not wired:
    print("No main app file found to wire; please integrate manually.")