from fastapi import Request
from ..db import connect

async def record_cost_event(request: Request, user_id: str = "anon"):
    h = request.headers
    model = h.get("x-model")
    tokens_in = int(h.get("x-tokens-in","0") or 0)
    tokens_out = int(h.get("x-tokens-out","0") or 0)
    cost = float(h.get("x-cost","0") or 0.0)
    provider = h.get("x-provider") or "unknown"
    if not (model or tokens_in or tokens_out or cost):
        return
    con = connect(); cur = con.cursor()
    cur.execute("""INSERT INTO api_usage_events(user_id,provider,model,tokens_in,tokens_out,cost_usd,created_at)
                 VALUES(?,?,?,?,?,?,datetime('now'))""",
                 (user_id, provider, model, tokens_in, tokens_out, cost))
    con.commit(); con.close()