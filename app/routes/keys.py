from fastapi import APIRouter
from pydantic import BaseModel
from ..security.keys import set_key, get_key, mask

router = APIRouter(prefix="/profile/api-keys", tags=["api-keys"])

class KeyIn(BaseModel):
    user_id: str
    provider: str
    key: str

@router.post("")
def set_api_key(body: KeyIn):
    set_key(body.user_id, body.provider, body.key)
    return {"status":"ok"}

@router.get("")
def get_api_key(user_id: str, provider: str):
    raw = get_key(user_id, provider)
    return {"user_id":user_id, "provider":provider, "key_masked": mask(raw) if raw else ""}