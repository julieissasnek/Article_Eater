# Article Eater v20.7.30 – Schema Alignment + Zombie Cleanup

Date: 2025-11-27T08:20:17.957410Z

This release resolves the schema mismatch between the worker and DB helper,
and reintroduces the explicit "zombie job" cleanup on worker startup.

Changes:

1. app/db.py
   - `connect()` now:
     - Uses `journal_mode=WAL` and `synchronous=NORMAL` for concurrency + durability.
     - Sets `row_factory=sqlite3.Row` for friendlier access patterns.
   - `ensure_db()` is now the canonical v20.7.x schema bootstrap for:
     - `processing_queue` (id, job_id, job_type, params, status, priority, result, error, timestamps).
     - `articles` (title, abstract, doi, corpus_id, authors, year, venue, full_text, flags, citation_count, URLs, timestamps).
     - `findings` (finding_level, consequent, antecedents, metrics, job_id, paper_id).
     - legacy `seven_panel` summaries.
     - `user_api_keys` and `api_usage_events`.
   - All definitions are aligned with what `app.worker.ResearchWorker`, the
     Streamlit control room, and the sample-data initializer expect.

2. app/worker.py
   - Added `cleanup_zombies()` method on `ResearchWorker`:
     - On startup, marks any `processing_queue` rows with `status='running'`
       as `status='failed'` with a clear error message and `completed_at`
       timestamp.
   - `start()` now calls `self.cleanup_zombies()` before entering the main loop.

No changes were made to the L0/L2 logic or scientific modelling in this
release; the focus is operational integrity and schema consistency.
