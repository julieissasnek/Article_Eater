from fastapi import APIRouter, Depends, Request
from ..db import connect
from ..middleware.costs import record_cost_event
from src.security.admin_guard import admin_required

router = APIRouter(prefix="/usage", tags=["usage"])

@router.get("/me")
async def usage_me(request: Request, user_id: str = "anon"):
    await record_cost_event(request, user_id=user_id)
    con = connect(); cur = con.cursor()
    cur.execute("SELECT datetime(created_at), provider, model, tokens_in, tokens_out, cost_usd FROM api_usage_events WHERE user_id=? ORDER BY id DESC LIMIT 200", (user_id,))
    rows = cur.fetchall(); con.close()
    return {"user": user_id, "events": [{"ts": r[0], "provider": r[1], "model": r[2], "in": r[3], "out": r[4], "cost": r[5]} for r in rows]}

@router.get("/admin/summary")
async def usage_admin_summary(ok: bool = Depends(admin_required)):
    con = connect(); cur = con.cursor()
    cur.execute("SELECT provider, model, COUNT(*), SUM(tokens_in), SUM(tokens_out), SUM(cost_usd) FROM api_usage_events GROUP BY provider, model ORDER BY 1,2" )
    rows = cur.fetchall(); con.close()
    return [{"provider":r[0], "model":r[1], "events":r[2], "tokens_in":r[3] or 0, "tokens_out":r[4] or 0, "cost_usd":round(r[5] or 0.0, 4)} for r in rows]
