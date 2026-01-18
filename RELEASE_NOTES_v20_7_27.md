# Article Eater v20.7.27 – Ruthless Frontend / Packaging Fixes

This release addresses the remaining concerns from the Gemini "ruthless" review
on top of the v20.7.26 read–think–write worker and WAL-mode SQLite changes.

## Changes

1. **Deconcatenator hardened**
   - Replaced the naive `deconcat.py` that split on the string `----- FILE PATH:` and
     used `errors="ignore"` with a robust, line-oriented parser.
   - New format supports per-file `ENCODING` headers (`plain` or `base64`) and treats
     markers only when they appear at the start of a line in marker position.
   - Binary files in concatenated dumps are expected to be base64-encoded; the
     deconcatenator decodes and writes them as binary. Text files are written as
     UTF-8 without silently dropping bytes.

2. **Read/Think/Write + WAL (already in v20.7.26)**
   - `app/db.py` and the worker's `_conn()` helper now enable `PRAGMA journal_mode=WAL`
     and use `timeout=30.0` for better coexistence of Streamlit UI and background worker.
   - `ResearchWorker.run_l2_extract` uses a strict three-phase read–think–write pattern:
     it reads all article text into memory, closes the DB, calls the LLM on that
     in-memory data only, then reopens the DB for a single batched write.

3. **SQL injection audit**
   - Searched for `cursor.execute(f"...")` and similar patterns across the repo.
   - Remaining f-string SQL is confined to internal migration/quarantine scripts that
     operate only on hard-coded table/column names (no user input). UI and worker paths
     use parameterized queries.

4. **Streamlit control room sanity check**
   - Confirmed that the live Streamlit dashboard is implemented in
     `scripts/ae_streamlit_control_room.py` using `st.write`, `st.dataframe`, etc.,
     and does not rely on `print()` for UI output.
   - Older ASCII-art / print-based control room implementations are no longer used.

This puts the repository closer to a genuine "GO" for classroom and lab use: the
research worker is concurrency-safe for typical loads, the Streamlit UI is real,
and the packaging/deconcat story is robust enough for distribution.
