from fastapi import Header, HTTPException, status
import os, json, pathlib
from datetime import datetime, timezone

AUDIT = pathlib.Path("logs/admin_audit.log")
AUDIT.parent.mkdir(parents=True, exist_ok=True)

def _audit(action: str):
    try:
        rec = {"ts": datetime.now(timezone.utc).isoformat(), "action": action}
        AUDIT.write_text((AUDIT.read_text() if AUDIT.exists() else "") + json.dumps(rec)+"\n", encoding="utf-8")
    except Exception:
        pass

def admin_required(x_admin_token: str | None = Header(default=None, alias="X-Admin-Token")):
    token = os.getenv("AE_ADMIN_TOKEN", "")
    if not token or not x_admin_token or x_admin_token != token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="admin token required")
    _audit("admin_access")
    return True
