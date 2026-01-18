# Article Eater v20.7.43 – Technical Validation Log

- **Environment**: macOS 14.5 (arm64), Python 3.11.12 in `venv` (3.14.0 also present but unused). Repeated Homebrew hook prints `/bin/ps: Operation not permitted`; also see noisy `anaconda-cloud-auth` import warning before Python invocations.
- **Dependency install**: `pip install -r requirements.txt` succeeded after elevated run for network access.
- **Database**: `python -c "import app.db as db; db.ensure_db()"` created `ae.db`; WAL files present from worker runs.
- **Sanity/Smoke**:
  - `scripts/sanity_check.py` → OK (non-fatal warning: missing Flask for optional `apps.user_rules_gui`).
  - `scripts/offline_pipeline_smoke.py` → OK (events=4, calibration files=1).
- **Core services**:
  - Worker (`python -m app.worker`) initially broken by malformed logging setup and idle-timeout print strings; fixed in `app/worker.py`. Requires elevated permissions to bind port 4004 in this environment. Starts cleanly; idle timeout honored.
  - Control Room (`streamlit run scripts/ae_streamlit_control_room.py`) starts headlessly with elevated permissions; UI event logging verified via `app.services.ui_events.log_ui_event` (recorded `control_room|view` row in `ui_events`). Direct browser interaction not exercised due to headless CLI constraints.
- **Real L0+L2 job**:
  - Enqueued L0 harvest (`query="biophilic design"`, limit 1) → complete, inserted 1 article (`articles` table populated).
  - Enqueued L2 extract for that article → completed with 0 findings; error in logs: `Missing GOOGLE_API_KEY for Gemini`. No findings present (`findings` count = 0). External LLM key required for a true L2 pass.
- **Antigravity installer**:
  - Builder script present (`scripts/build_antigravity_installer.py`) but required input `Article_Eater_v20_7_43_usability_antigravity_full_concatenated.txt` is missing in the bundle, so installer could not be built or tested.

Open issues/blockers:
- Need valid `GOOGLE_API_KEY` (or equivalent OpenAI key/model override) to run a real L2 extraction and populate findings.
- Need the v20.7.43 concatenated TXT asset to exercise `build_antigravity_installer.py` and verify the installer path.
- Minor noise: repeated `anaconda-cloud-auth` import warning on Python startup; does not block runs.
