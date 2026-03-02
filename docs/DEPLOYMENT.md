# ATLAS Deployment Procedure

**System:** Article_Eater_PostQuinean_v1 — ATLAS  
**Date:** 2026-03-01  

---

## Prerequisites

- Python 3.10+ (tested on 3.14)
- macOS or Linux
- ~2GB disk for databases and extractions
- Gemini API key (for extraction pipeline)

## Fresh Install

```bash
# 1. Clone
git clone <repo-url> Article_Eater_PostQuinean_v1
cd Article_Eater_PostQuinean_v1

# 2. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Optional dependencies (for vision/CV features)
pip install opencv-python-headless  # cv2
pip install streamlit               # dashboard
pip install structlog               # structured logging

# 5. Set API keys
export GEMINI_API_KEY="your-key-here"
# Or create .env file:
echo 'GEMINI_API_KEY=your-key-here' > .env

# 6. Verify installation
python3 -c "from src.services.db_locator import get_web_db; print(f'DB: {get_web_db()}')"
python3 scripts/sprint_c_verification.py
```

## Database Setup

The system uses SQLite databases in `data/`:

| Database | Purpose | Created By |
|----------|---------|------------|
| `web_persistence_v2.db` | Primary epistemic web (beliefs, constraints, annotations) | Integration pipeline |
| `overseer.db` | Governance, pipeline state | Overseer service |

Database resolution is centralized via `src/services/db_locator.py`:
```python
from src.services.db_locator import get_web_db
db_path = get_web_db()  # Returns Path to the best available DB
```

## Running the System

### Health Check
```bash
python3 scripts/compute_system_health.py --skip-gates
# Produces: data/production/system_health_report.json
#           docs/system_health_report.md
```

### Nightly Pipeline
```bash
python3 scripts/nightly_integration_pipeline.py
```

### Individual Pipelines
```bash
# Grounding classification
python3 scripts/classify_grounding.py

# Constraint propagation (dry-run first)
python3 scripts/propagate_constraints.py --dry-run
python3 scripts/propagate_constraints.py

# Annotation migration
python3 scripts/migrate_annotations_to_unified.py

# Sprint verification
python3 scripts/sprint_c_verification.py
```

### Test Suite
```bash
pytest tests/ -x --tb=short -q
```

### Streamlit Dashboard
```bash
streamlit run src/qa/app.py
```

## Configuration

Key configuration files:
- `contracts/success_conditions.json` — 89 measurable success conditions
- `schemas/theory/` — 6 taxonomy files
- `data/templates/` — 208 research templates
- `data/cva_annotations/` — CVA annotation JSONs

## Monitoring

- **AESHI score**: `data/production/system_health_report.json`
- **Reflex system**: 22 auto-repair reflexes in `src/qa/reflex_system.py`
- **Overseer**: `src/services/overseer.py` — 6 epistemic invariants

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| "No module named 'cv2'" | Optional dependency | `pip install opencv-python-headless` |
| "No module named 'streamlit'" | Optional dependency | `pip install streamlit` |
| AESHI score = 0 | Stale report | `python3 scripts/compute_system_health.py --skip-gates` |
| DB not found | Path resolution | Check `python3 -c "from src.services.db_locator import get_web_db; print(get_web_db())"` |
| Grounding all UNSET | Needs classification | `python3 scripts/classify_grounding.py` |
