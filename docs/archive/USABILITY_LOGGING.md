# Usability & Interaction Logging (ui_events)

This document describes a **very lightweight** telemetry layer used to
understand how people actually use Article Eater: which surfaces they
visit, which buttons they press, and where they run into errors.

The goal is to give the teaching / research team visibility into real
user behaviour without turning this into a heavy analytics system.

---

## 1. Schema: `ui_events` table

The `ui_events` table is created by `app.db.ensure_db()` alongside the
queue, findings and usage tables.

```sql
CREATE TABLE IF NOT EXISTS ui_events(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    user_hash TEXT,
    surface TEXT,
    action TEXT,
    detail_json TEXT
);
```

Field semantics:

- `timestamp` — UTC ISO8601 string, when the event was recorded.
- `user_hash` — an identifier for the user. In most cases this is
  populated from environment variables (e.g. UCSD username) on
  internal deployments, or left empty for anonymous usage.
- `surface` — logical name of the UI surface, e.g.
  - `control_room`
  - `search`
  - `admin_rulegraph`
  - `admin_confidence`
- `action` — short verb describing what happened, e.g.
  - `view`
  - `click_go`
  - `preset_selected`
  - `error_dialog_shown`
- `detail_json` — small JSON blob with extra context (which preset,
  which switches, what error message, etc.).

The table is intentionally compact and append-only. A periodic clean-up
or export job can archive old events if needed.

---

## 2. Python helper: `app.services.ui_events.log_ui_event`

The module `app/services/ui_events.py` contains a single helper:

```python
from app.services.ui_events import log_ui_event

log_ui_event(
    surface="control_room",
    action="view",
    user_id=os.environ.get("USER") or os.environ.get("USERNAME"),
    detail={"auto_refresh": bool(auto_refresh)},
)
```

Key properties:

- Uses the canonical `app.db.connect()` helper.
- Swallows all exceptions so logging can *never* break a UI.
- Serialises `detail` as JSON and inserts one row into `ui_events`.

### 2.1 Streamlit Control Room

The Streamlit dashboard (`scripts/ae_streamlit_control_room.py`) now
calls `log_ui_event` automatically whenever the page renders:

- `surface` is set to `"control_room"`.
- `action` is `"view"`.
- `detail` includes whether auto-refresh was enabled.

This gives you a basic “heartbeat” of how often the dashboard is used.

You can add more calls for particular actions, e.g. when you add a
“Run small demo job” button:

```python
if st.button("Run small demo job"):
    # ... enqueue a demo job ...
    log_ui_event(
        surface="control_room",
        action="click_demo_job",
        user_id=current_user,
        detail={"topic": "demo-topic"},
    )
```

---

## 3. Instrumenting browser GUIs (JavaScript)

For browser-based UIs (e.g. the search / results pages), the pattern is:

1. Add a backend endpoint that accepts UI events.
2. Call that endpoint from JavaScript when the user does something
   important (click GO, select a preset, see an error).

### 3.1 Suggested FastAPI route (for future work)

> **Note:** This is a suggested sketch for the Technical Lead. It is
> not yet wired into `app.main`. When you are ready, you can add a
> small router like this under `app/routes/ui_events.py` and include
> it from `app.main`.

```python
# app/routes/ui_events.py (sketch)
from fastapi import APIRouter
from pydantic import BaseModel
from app.services.ui_events import log_ui_event

router = APIRouter(prefix="/ui", tags=["ui"])

class UIEventIn(BaseModel):
    surface: str
    action: str
    user_id: str | None = None
    detail: dict | None = None

@router.post("/event")
async def record_ui_event(event: UIEventIn):
    log_ui_event(
        surface=event.surface,
        action=event.action,
        user_id=event.user_id,
        detail=event.detail,
    )
    return {"status": "ok"}
```

Then, in `app.main`, you would register the router:

```python
from .routes import ui_events as ui_events_routes

app.include_router(ui_events_routes.router)
```

(Do this only when you are ready and have a few minutes to run smoke
tests; it is intentionally small and self-contained.)

### 3.2 JavaScript snippet for front-ends

Once such a route exists, you can log events from browser UIs with a
single `fetch` call:

```javascript
async function logUiEvent(surface, action, detail = {}) {
  try {
    await fetch("/ui/event", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        surface,
        action,
        user_id: window.currentUser || null,
        detail,
      }),
    });
  } catch (e) {
    // Never break the UI if logging fails
    console.warn("ui_events logging failed", e);
  }
}
```

Example usage on a search form:

```javascript
document
  .getElementById("search-form")
  .addEventListener("submit", function (ev) {
    const topic = document.getElementById("topic-input").value || "";
    logUiEvent("search", "click_go", { topic });
  });
```

Example usage for a “Typical Task” preset dropdown:

```javascript
document
  .getElementById("preset-select")
  .addEventListener("change", function (ev) {
    const presetId = ev.target.value;
    logUiEvent("search", "preset_selected", { preset_id: presetId });
  });
```

---

## 4. Analysing usability data

You can explore the `ui_events` table directly in SQLite, or via a
small notebook. Typical questions:

- Which surfaces are used the most?
- How often is the GO / Execute button pressed on each surface?
- Are there particular presets that are popular or associated with
  errors?
- Do users frequently see `error_dialog_shown` events on any page?

Example simple query:

```sql
SELECT surface, action, COUNT(*) AS n
FROM ui_events
GROUP BY surface, action
ORDER BY n DESC;
```

For more detailed analysis, export `ui_events` to CSV and load it into
a Jupyter notebook or R.

---

## 5. Privacy considerations

This logging layer is designed for **internal teaching / research**
deployments, not for public SaaS analytics.

- `user_hash` can be:
  - A hashed identifier, computed offline when analysing the data.
  - A short username string (e.g. campus account) if appropriate.
- Events should be used to improve UI and teaching materials, not to
  grade or evaluate individuals without explicit consent.
- If you deploy outside a classroom or lab context, review your
  institution’s policies on telemetry and user tracking.

If at any point you decide to disable this layer entirely, you can:

- Stop calling `log_ui_event` in GUIs, and/or
- Drop or truncate the `ui_events` table from the DB.

The rest of Article Eater will continue to function normally.
