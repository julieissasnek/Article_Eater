
from fastapi import APIRouter
import sqlite3, os
router = APIRouter(prefix="/interactions", tags=["interactions"])
DB = os.environ.get("AE_DB","ae.db")
def _conn(): return sqlite3.connect(DB)

@router.get("/review")
def review():
    with _conn() as con:
        rows = [dict(id=r[0], a=r[1], b=r[2], t=r[3], s=r[4], notes=r[5]) for r in con.execute(
            "SELECT interaction_id, rule_a_id, rule_b_id, interaction_type, status, notes FROM rule_interactions ORDER BY interaction_id DESC").fetchall()]
    return {"pending": rows}