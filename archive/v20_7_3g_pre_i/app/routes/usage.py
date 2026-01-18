from fastapi import APIRouter, Request, Depends

from ..db import connect
from app.auth import get_current_user_dep, require_admin
from ..middleware.costs import record_cost_event

router = APIRouter(prefix="/usage", tags=["usage"])


@router.get("/me")
async def usage_me(request: Request, current_user = Depends(get_current_user_dep)):
    """
    Return recent API usage for the calling user.

    - If authenticated, binds to the JWT user's `user_id`.
    - If anonymous, falls back to a synthetic "anon" user_id.
    """
    user_id = current_user.user_id if current_user else "anon"

    # Record this cost event (if cost headers are present).
    await record_cost_event(request, user_id=user_id)

    con = connect()
    cur = con.cursor()
    cur.execute(
        """
        SELECT datetime(created_at),
               provider,
               model,
               tokens_in,
               tokens_out,
               cost_usd
        FROM api_usage_events
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT 200
        """,
        (user_id,),
    )
    rows = cur.fetchall()
    con.close()

    events = [
        {
            "ts": r[0],
            "provider": r[1],
            "model": r[2],
            "in": r[3],
            "out": r[4],
            "cost": r[5],
        }
        for r in rows
    ]
    return {"user": user_id, "events": events}


@router.get("/admin/summary")
async def usage_admin_summary(admin_user = Depends(require_admin)):
    """
    Return an aggregated cost summary across all users and providers.

    Requires an authenticated user with role `admin`.
    """
    con = connect()
    cur = con.cursor()
    cur.execute(
        """
        SELECT provider,
               model,
               COUNT(*),
               SUM(tokens_in),
               SUM(tokens_out),
               SUM(cost_usd)
        FROM api_usage_events
        GROUP BY provider, model
        ORDER BY provider, model
        """
    )
    rows = cur.fetchall()
    con.close()

    summary = [
        {
            "provider": r[0],
            "model": r[1],
            "events": r[2],
            "tokens_in": r[3] or 0,
            "tokens_out": r[4] or 0,
            "cost_usd": round(r[5] or 0.0, 4),
        }
        for r in rows
    ]
    return summary
