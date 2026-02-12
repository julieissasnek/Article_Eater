# Run Instructions: Article Eater V22.0.0 (Post-Quinean)

**Date**: January 22, 2026
**Purpose**: Document how to run the system

---

## 1. Prerequisites

- Python 3.11+
- Virtual environment (recommended)
- SQLite (bundled with Python)

## 2. Installation

```bash
# Clone the repository
cd /path/to/Article_Eater_PostQuinean_v1

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template (if exists)
cp .env.template .env  # Edit as needed
```

## 3. Running the CLI

The main entrypoint is `bin/article_eater`:

```bash
# Basic extraction (smoke test)
./bin/article_eater eat \
    --in contracts/ae_af/examples/input_bundle_minimal \
    --out /tmp/ae_out_example \
    --profile standard \
    --hitl auto

# With specific PDF corpus
./bin/article_eater eat \
    --in /path/to/pdf/folder \
    --out /path/to/output \
    --profile standard
```

### CLI Options

| Option | Description |
|--------|-------------|
| `--in` | Input folder containing PDFs or claim bundles |
| `--out` | Output folder for results |
| `--profile` | Processing profile: `standard`, `minimal`, `thorough` |
| `--hitl` | Human-in-the-loop mode: `auto`, `review`, `approve` |

## 4. Running the API Server

```bash
# Start FastAPI server
uvicorn app.main:app --reload --port 8000

# Or with production settings
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/query` | GET/POST | Query the web of belief |
| `/api/v1/reports/{type}` | GET | Generate reports |
| `/api/v1/ingestion/paper` | POST | Ingest new papers + beliefs |
| `/healthz` | GET | Health check |

## 5. Running Tests

```bash
# All tests
pytest -q  # discovery is constrained to tests/ via pytest.ini

# Core service tests only (no external dependencies)
pytest tests/test_causal_classifier.py tests/test_reporting.py \
       tests/test_bridge_warrants.py tests/test_query_response.py -v

# With coverage
pytest --cov=src --cov-report=html
```

Admin/profile key routes require `X-Admin-Token` (`AE_ADMIN_TOKEN`) in request headers.

Also guarded:
- `/admin`
- `/admin/stats`
- `/usage/admin/summary`
- `/api/v1/web/admin/*`

## 6. Production Verification

```bash
# Run production smoke test
./bin/prod_smoke.sh

# Check governance compliance
python scripts/check_governance.py
```

## 6.1 BN Frontend Verification (cross-repo)

```bash
cd /Users/davidusa/REPOS/BN_graphical/frontend-v2
npm ci
npm run build
```

If Vite/Rollup reports missing native optional dependencies (for example
`@rollup/rollup-darwin-arm64`), run `npm ci` again in `frontend-v2` to
rebuild `node_modules` for the current platform and architecture.

## 7. Output Files

After extraction, the output folder contains:

| File | Description |
|------|-------------|
| `claims.jsonl` | Extracted claims from papers |
| `rules.jsonl` | Generated rules |
| `web_state.json` | Web of belief state |
| `bridges.jsonl` | Bridge warrants |
| `stubs.jsonl` | Findings that don't fit ontology |
| `tensions.jsonl` | Detected tensions |
| `coherence_summary.json` | Coherence metrics |

## 8. Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_MODEL` | `mistral` | LLM model for extraction |
| `DB_URL` | `sqlite:///ae.db` | Database URL |
| `AE_WEB_SEEK_EQUILIBRIUM` | `true` | Enable equilibrium-seeking |
| `AE_WEB_EQUILIBRIUM_MAX_ITERATIONS` | `100` | Max iterations |
| `AE_WEB_CONVERGENCE_THRESHOLD` | `0.001` | Convergence threshold |

## 9. Docker (Optional)

If Docker is configured:

```bash
# Build and run
docker compose up -d --build

# Check status
docker compose ps

# View logs
docker compose logs -f
```

---

## Known Gaps (Audit Note)

1. **No CI/CD Workflows**: `.github/workflows/` does not exist. The Project_Constitution references CI gates, but they are not implemented.

2. **No README.md**: Root-level README is missing. Use this document and CLAUDE.md for guidance.

3. **pyproject.toml is minimal**: Only contains ruff configuration. Full dependencies are in `requirements.txt`.
