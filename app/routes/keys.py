from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from ..db import connect
from ..security.keys import set_key, get_key, mask
from src.security.admin_guard import admin_required

router = APIRouter(prefix="/profile/api-keys", tags=["api-keys"])

class KeyIn(BaseModel):
    user_id: str
    provider: str
    key: str


def _normalize_provider(provider: str) -> str:
    p = (provider or "").strip().lower()
    if not p:
        raise HTTPException(status_code=400, detail="provider is required")
    if not all(c.isalnum() or c in {"_", "-"} for c in p):
        raise HTTPException(status_code=400, detail="invalid provider")
    return p


def _list_user_keys(user_id: str):
    with connect() as con:
        cur = con.cursor()
        cur.execute(
            "SELECT provider, created_at FROM user_api_keys WHERE user_id=? ORDER BY provider",
            (user_id,),
        )
        rows = cur.fetchall()
    items = []
    for row in rows:
        provider = row["provider"] if hasattr(row, "__getitem__") else row[0]
        created_at = row["created_at"] if hasattr(row, "__getitem__") else row[1]
        raw = get_key(user_id, provider)
        items.append(
            {
                "provider": provider,
                "key_masked": mask(raw) if raw else "",
                "created_at": created_at,
            }
        )
    return items

@router.post("")
def set_api_key(body: KeyIn, ok: bool = Depends(admin_required)):
    provider = _normalize_provider(body.provider)
    set_key(body.user_id, provider, body.key)
    return {"status": "ok", "user_id": body.user_id, "provider": provider}

@router.get("")
def get_api_key(
    user_id: str = Query(..., min_length=1),
    provider: str | None = Query(None),
    ok: bool = Depends(admin_required),
):
    # `provider` optional: preserve old single-key mode and add list mode.
    if provider is not None:
        norm_provider = _normalize_provider(provider)
        raw = get_key(user_id, norm_provider)
        return {
            "user_id": user_id,
            "provider": norm_provider,
            "key_masked": mask(raw) if raw else "",
        }
    return {"user_id": user_id, "keys": _list_user_keys(user_id)}


@router.delete("/{provider}")
def delete_api_key(
    provider: str,
    user_id: str = Query(..., min_length=1),
    ok: bool = Depends(admin_required),
):
    norm_provider = _normalize_provider(provider)
    with connect() as con:
        cur = con.cursor()
        cur.execute(
            "DELETE FROM user_api_keys WHERE user_id=? AND provider=?",
            (user_id, norm_provider),
        )
        deleted = cur.rowcount
        con.commit()
    return {"status": "ok", "deleted": bool(deleted), "user_id": user_id, "provider": norm_provider}
