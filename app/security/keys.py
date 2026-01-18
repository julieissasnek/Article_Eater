import base64, os
from typing import Optional
from cryptography.fernet import Fernet, InvalidToken
from ..db import connect

def _fernet() -> Fernet:
    master = os.environ.get("AE_MASTER_KEY", "").strip()
    if not master:
        master = base64.urlsafe_b64encode(os.urandom(32)).decode()
        os.environ["AE_MASTER_KEY"] = master
    return Fernet(master.encode() if not isinstance(master, bytes) else master)

def set_key(user_id: str, provider: str, raw_key: str) -> None:
    token = _fernet().encrypt(raw_key.encode())
    con = connect(); cur = con.cursor()
    cur.execute("INSERT OR REPLACE INTO user_api_keys(user_id,provider,enc_key,created_at) VALUES(?,?,?,datetime('now'))",
                (user_id, provider, token))
    con.commit(); con.close()

def get_key(user_id: str, provider: str) -> Optional[str]:
    con = connect(); cur = con.cursor()
    cur.execute("SELECT enc_key FROM user_api_keys WHERE user_id=? AND provider=?", (user_id, provider))
    row = cur.fetchone(); con.close()
    if not row: return None
    try: return _fernet().decrypt(row[0]).decode()
    except InvalidToken: return None

def mask(key: Optional[str]) -> str:
    if not key: return ""
    return key[:4] + "*" * max(0, len(key)-8) + key[-4:] if len(key)>8 else "*"*len(key)