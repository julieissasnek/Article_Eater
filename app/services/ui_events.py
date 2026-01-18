"""Lightweight UI event logging helpers.

This module provides a tiny, low-risk API for recording interaction
events from GUIs (Streamlit dashboard, browser front-ends, admin tools).

Usage from Python (e.g. Streamlit):

    from app.services.ui_events import log_ui_event

    log_ui_event(
        surface="control_room",
        action="view",
        user_id=os.environ.get("USER") or os.environ.get("USERNAME"),
        detail={"auto_refresh": bool(auto_refresh)},
    )

The implementation is deliberately simple:

- Uses the canonical app.db.connect() helper.
- Swallows all exceptions so that logging can *never* break the UI.
- Stores details as a JSON blob for easy post-hoc analysis.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from ..db import connect


def log_ui_event(
    surface: str,
    action: str,
    user_id: Optional[str] = None,
    detail: Optional[Dict[str, Any]] = None,
) -> None:
    """Record a single UI event into the ui_events table.

    Parameters
    ----------
    surface:
        Logical name of the GUI surface (e.g. "control_room",
        "search", "admin_rulegraph").
    action:
        Short verb for what happened (e.g. "view", "click_go",
        "preset_selected", "error_dialog_shown").
    user_id:
        Optional user identifier (e.g. UCSD account name). This is
        hashed or truncated at analysis time; here we just store the
        raw string or None.
    detail:
        Optional dict of additional details (current mode, preset
        name, parameters, error type, etc.). Will be JSON-encoded.
    """
    try:
        payload = json.dumps(detail or {}, ensure_ascii=False)
        ts = datetime.now(timezone.utc).isoformat(timespec="seconds")

        con = connect()
        cur = con.cursor()
        cur.execute(
            """INSERT INTO ui_events(timestamp, user_hash, surface, action, detail_json)
            VALUES (?, ?, ?, ?, ?)
            """,
            (ts, user_id or "", surface, action, payload),
        )
        con.commit()
        con.close()
    except Exception:
        # UI logging must never break the interface. If something goes
        # wrong (e.g. DB not initialised yet), we silently ignore it.
        return
