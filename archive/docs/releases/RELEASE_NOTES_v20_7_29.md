# Article Eater v20.7.29 – Streamlit Control Room Integration

Date: 2025-11-27T07:43:06.481943Z

This release makes the Streamlit Control Room the canonical dashboard for
monitoring the Article Eater research pipeline.

Changes in this version:

- Replaced `scripts/ae_streamlit_control_room.py` with a true Streamlit UI:
  - Uses `st.dataframe`, `st.metric`, and `st.caption` instead of console `print`.
  - Displays:
    - Job queue (processing_queue) with status-based row highlighting.
    - Recent findings (findings JOIN articles).
    - Library stats (papers, findings, failed jobs).
  - Supports optional auto-refresh (5s) via sidebar toggle.

- DB access in the control room mirrors backend policy:
  - Uses `AE_DB_PATH` / `AE_DB` env vars or falls back to `ae.db`.
  - Opens SQLite connections with `timeout=30.0` and `PRAGMA journal_mode=WAL;`.

No backend or schema changes were made in this release. All worker, governance,
and job-status semantics are as in v20.7.28.
