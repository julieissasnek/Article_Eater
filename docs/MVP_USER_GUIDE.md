# MVP User Guide

**Article Eater V23.0.0 - Post-Quinean Edition**
**Date**: 2026-02-11

---

## Quick Start

### 1. Start the Web Interface

```bash
cd /Users/davidusa/REPOS/Article_Eater_PostQuinean_v1
streamlit run streamlit_app/mvp/app.py
```

Open http://localhost:8501 in your browser.

### 2. Query the Knowledge Base

Navigate to **Query** page and ask questions like:
- "What affects attention in offices?"
- "Does natural light improve productivity?"
- "What reduces workplace stress?"

### 3. View Status

Navigate to **Status** page to see:
- Papers processed
- Beliefs accumulated
- Coherence score
- Processing history

### 4. Find Knowledge Gaps

Navigate to **Gaps** page to see:
- Domain coverage
- Unexplored areas
- Suggested searches

---

## Command-Line Interface

### Query from Terminal

```bash
# Simple query
python -m src.cli.query "What affects attention?"

# With options
python -m src.cli.query "natural light productivity" --mode detail --gaps
```

### Batch Processing

```bash
# Process papers from job bundles
python scripts/process_papers.py --bundles /path/to/bundles --limit 10

# With configuration file
python scripts/process_papers.py --config scripts/process_config.yaml
```

---

## Key Concepts

### Beliefs and Credence

A **belief** is an evidence-backed statement extracted from papers.

Each belief has:
- **Content**: What the belief says
- **Credence**: Degree of belief (0.0 to 1.0)
- **Uncertainty**: Meta-uncertainty about the credence
- **Level**: Epistemic level (EMPIRICAL, THEORETICAL, etc.)
- **Paper IDs**: Source papers

### Epistemic Levels

| Level | Description | Example |
|-------|-------------|---------|
| EMPIRICAL | Direct observation/measurement | "Natural light increased task performance by 15%" |
| THEORETICAL | Theory-derived statement | "Attention restoration occurs via involuntary attention" |
| METHODOLOGICAL | About methods/measurement | "Self-report stress measures correlate with cortisol" |
| META | About the knowledge itself | "More replication studies needed for biophilia claims" |

### Coherence

The web maintains **coherence** through constraints between beliefs:
- **SUPPORTS**: Beliefs that reinforce each other
- **CONFLICTS**: Beliefs that tension each other
- **REQUIRES**: Logical dependencies

Higher coherence = more internally consistent knowledge base.

### Knowledge Gaps

Gaps are areas where:
- Few beliefs exist for a domain
- Uncertainty is high
- Conflicts are unresolved

The system suggests searches to fill gaps.

---

## Processing Papers

### Job Bundle Format

A job bundle is a directory containing:
```
job_paper_001/
├── paper.pdf       # Required: The PDF
└── paper.json      # Required: Metadata (ae.paper.v1 schema)
```

### Paper Metadata (paper.json)

```json
{
  "schema": "ae.paper.v1",
  "paper_id": "kaplan_1989",
  "doi": "10.1234/example",
  "title": "The Restorative Benefits of Nature",
  "authors": [{"name": "Kaplan, S."}],
  "year": 1989,
  "venue": "Journal of Environmental Psychology"
}
```

### Batch Processing Options

| Option | Description |
|--------|-------------|
| `--bundles` | Directory containing job bundles |
| `--limit` | Maximum papers to process |
| `--profile` | Processing depth: fast, standard, deep |
| `--max-failures` | Circuit breaker threshold |
| `--no-skip-processed` | Re-process already processed papers |

---

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `AE_DATA_DIR` | `data/` | Data directory |
| `AE_WEB_SEEK_EQUILIBRIUM` | `true` | Enable coherence optimization |
| `AE_WEB_CONVERGENCE_THRESHOLD` | `0.001` | Coherence convergence |

### Config File (process_config.yaml)

```yaml
bundles_dir: ~/article_eater_jobs
profile: standard
hitl: auto
max_consecutive_failures: 3
skip_already_processed: true
```

---

## Data Files

| File | Purpose |
|------|---------|
| `data/web_persistence.db` | SQLite database with accumulated web |
| `data/accumulated_web.json` | JSON export for inspection |
| `data/events.jsonl` | Processing event log |
| `data/batch_progress.json` | Batch processing progress |

---

## Troubleshooting

### "Query engine not available"

The web of belief may be empty. Process some papers first:
```bash
python scripts/process_papers.py --bundles /path/to/bundles
```

### "Using mock data"

Backends are unavailable. Check:
1. Database exists: `ls data/web_persistence.db`
2. Dependencies installed: `pip install -r requirements.txt`

### "Circuit breaker triggered"

Too many consecutive failures. Check:
1. PDFs are valid
2. Network connectivity (for LLM calls)
3. Reduce batch size with `--limit`

---

## API Reference

### QueryEngine

```python
from src.services.query_engine import QueryEngine

engine = QueryEngine()

# Simple query
response = engine.query("What affects attention?")

# Full options
response = engine.query(
    "natural light productivity",
    response_mode="detail",    # headline, summary, detail, deep_dive
    include_gaps=True,
    max_results=10,
    min_credence=0.3
)
```

### WebAccumulator

```python
from src.services.web_accumulator import get_accumulator

acc = get_accumulator()

# Get statistics
stats = acc.get_stats()
print(f"Beliefs: {stats.total_beliefs}")

# Export to JSON
acc.export_to_json()
```

---

## Further Reading

- `docs/ARCHITECTURE.md` - System architecture
- `docs/DEMO_SCRIPT.md` - 10-minute demo guide
- `Project_Constitution.md` - Project rules and philosophy
- `CLAUDE.md` - Developer guide
