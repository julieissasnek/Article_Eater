from fastapi import APIRouter, Depends, HTTPException, Query

from src.security.admin_guard import admin_required
from ..security.keys import get_key, mask, set_key

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("/keys")
def get_keys(
    user_id: int = Query(..., ge=1),
    ok: bool = Depends(admin_required),
):
    """Legacy profile endpoint backed by encrypted key storage."""
    google_key = get_key(str(user_id), "gemini")
    openai_key = get_key(str(user_id), "openai")
    return {
        "google_api_key": mask(google_key),
        "openai_api_key": mask(openai_key),
    }


@router.post("/keys")
def set_keys(
    google_api_key: str | None = None,
    openai_api_key: str | None = None,
    user_id: int = Query(..., ge=1),
    ok: bool = Depends(admin_required),
):
    """Legacy profile endpoint backed by encrypted key storage."""
    if not google_api_key and not openai_api_key:
        raise HTTPException(status_code=400, detail="Provide at least one key")

    if google_api_key:
        set_key(str(user_id), "gemini", google_api_key)
    if openai_api_key:
        set_key(str(user_id), "openai", openai_api_key)

    return {"ok": True}
