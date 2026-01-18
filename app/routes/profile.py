
from fastapi import APIRouter, Depends
import os, sqlite3, base64
router = APIRouter(prefix="/profile", tags=["profile"])
DB = os.environ.get("AE_DB","ae.db")
def _conn(): return sqlite3.connect(DB)
def _mask(s): 
    if not s: return None
    return s[:4] + "..." + s[-4:] if len(s)>8 else "***"

@router.get("/keys")
def get_keys(user_id: int=1):
    # naive per-user storage in kv table
    with _conn() as con:
        con.execute("CREATE TABLE IF NOT EXISTS kv (user_id INT, k TEXT, v TEXT, PRIMARY KEY(user_id,k))")
        row = con.execute("SELECT v FROM kv WHERE user_id=? AND k='gemini_key'", (user_id,)).fetchone()
        g = row[0] if row else None
        row = con.execute("SELECT v FROM kv WHERE user_id=? AND k='openai_key'", (user_id,)).fetchone()
        o = row[0] if row else None
    return {"google_api_key": _mask(g), "openai_api_key": _mask(o)}

@router.post("/keys")
def set_keys(google_api_key: str|None=None, openai_api_key: str|None=None, user_id: int=1):
    with _conn() as con:
        con.execute("CREATE TABLE IF NOT EXISTS kv (user_id INT, k TEXT, v TEXT, PRIMARY KEY(user_id,k))")
        if google_api_key:
            con.execute("INSERT OR REPLACE INTO kv(user_id,k,v) VALUES(?,?,?)", (user_id,'gemini_key',google_api_key))
        if openai_api_key:
            con.execute("INSERT OR REPLACE INTO kv(user_id,k,v) VALUES(?,?,?)", (user_id,'openai_key',openai_api_key))
    return {"ok": True}