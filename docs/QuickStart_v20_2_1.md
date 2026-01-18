# QuickStart — Article Eater v20.2.1

This quickstart proves an end‑to‑end run from job submission → L0/L1/L2 processing → seven‑panel → rules → interactions.

## 0) Pre‑requisites
- Python 3.10+
- SQLite3
- Valid Gemini API key (set via your secrets mechanism or env var `GEMINI_API_KEY`)
- (Optional) OpenAI/Anthropic keys as fallback for admins only

## 1) Initialize database (idempotent)
```bash
python scripts/migrate_v20.py ./ae.db
```

## 2) Start services (two terminals)
```bash
scripts/run_api.sh --reload
python app/worker.py
```

## 3) Submit a job (browser)
- Open `frontend/dashboard.html`
- Create a search for your CNfA topic (e.g., "natural light AND stress")
- Confirm in **Queue** that your job appears and advances L0 → L1 → L2

## 4) Verify outputs
- **Library**: Open the new article card; verify **Seven‑Panel** renders (with CI fields if present or null).
- **Rules**: Confirm new/updated rules with provenance.
- **Interactions**: See contradictions/CI conflicts and try **Find Disambiguating Articles** (enqueues targeted L0).

## 5) Optional: smoke test
```bash
python scripts/smoke_test.py --base http://127.0.0.1:8000 --topic "natural light AND stress"
```
This script creates a test job and polls until seven‑panel appears (or times out), printing PASS/FAIL.