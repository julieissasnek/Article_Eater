# PDF Extraction Pipeline Instructions

**Location**: `src/extraction/pdf_extraction_module.py`

**Purpose**: Extract structured findings from scientific PDFs with quality control, image extraction, and queue management.

---

## Quick Start

```bash
cd /path/to/Article_Eater_PostQuinean_v1  # or use PROJECT_ROOT
source venv/bin/activate

# Check current status
python -m src.extraction.pdf_extraction_module --status

# Process 50 papers
python -m src.extraction.pdf_extraction_module --resume --batch 50
```

---

## Full Workflow

### 1. Initialize Queue (first time only)

```bash
# Add papers from existing extraction file
python -m src.extraction.pdf_extraction_module \
    --scan data/extractions/full_extraction_20260224_010144.json
```

This adds papers marked as "unknown" or "failed" to the processing queue.

### 2. Check Status

```bash
python -m src.extraction.pdf_extraction_module --status
```

Output shows:
- `pending`: Papers waiting to be processed
- `accepted`: Papers successfully extracted (ready for BN/Web)
- `requeued`: Papers that failed quality check but will retry
- `failed`: Papers that need manual review
- `lock`: Whether another process is running

### 3. Process Papers

```bash
# Process 50 papers (default)
python -m src.extraction.pdf_extraction_module --resume

# Process specific batch size
python -m src.extraction.pdf_extraction_module --resume --batch 100

# Skip image extraction (faster)
python -m src.extraction.pdf_extraction_module --resume --no-images
```

### 4. Continue Until Done

Keep running `--resume` until all papers are processed:

```bash
while true; do
    python -m src.extraction.pdf_extraction_module --resume --batch 50
    if [ $? -ne 0 ]; then break; fi
    sleep 5
done
```

---

## Parallel Execution (Multiple Agents)

The pipeline supports **multiple agents running simultaneously**. Each agent:
1. Claims papers atomically (no conflicts)
2. Processes its claimed papers
3. Releases papers when done
4. Has a 10-minute timeout (stale claims get reclaimed)

### Running Multiple Agents

```bash
# Terminal 1 (Agent A)
python -m src.extraction.pdf_extraction_module --resume --batch 50

# Terminal 2 (Agent B) - runs simultaneously, claims DIFFERENT papers
python -m src.extraction.pdf_extraction_module --resume --batch 50

# Terminal 3 (Agent C) - etc.
python -m src.extraction.pdf_extraction_module --resume --batch 50
```

Each agent gets different papers - no conflicts.

### Check Active Agents

```bash
python -m src.extraction.pdf_extraction_module --status
```

Shows:
```json
{
  "agents": {
    "this_agent": "hostname_pid_timestamp",
    "active": {
      "agent_1": {"count": 50, "host": "machine1"},
      "agent_2": {"count": 50, "host": "machine2"}
    },
    "papers_claimed": 100,
    "stale_claims": 0
  }
}
```

### If an Agent Crashes

Stale claims (no heartbeat for 10 minutes) are automatically reclaimed:

```bash
# Manually reclaim stale papers
python -m src.extraction.pdf_extraction_module --reclaim
```

### Running from Multiple Machines

Works automatically - just point to the same `--output-dir` (must be accessible to all machines, e.g., shared drive or NFS)

---

## Output Locations

| Path | Contents |
|------|----------|
| `data/extraction_pipeline/extraction_queue.json` | Queue state and progress |
| `data/extraction_pipeline/results/*.json` | Individual paper extractions |
| `data/extraction_pipeline/images/*.{png,jpg}` | Extracted images from PDFs |
| `data/extraction_pipeline/pipeline.lock` | Process lock file |

---

## What Gets Extracted

For each paper:

1. **Article Type**: empirical, meta_analysis, systematic_review, narrative_review, theoretical, qualitative, methods

2. **Findings** (array):
   - `antecedent`: Environmental feature (IV)
   - `consequent`: Human response (DV)
   - `direction`: increase | decrease | no_effect | mixed
   - `claim_type`: causal | associational | moderated | null
   - `p_value`: Statistical significance
   - `effect_size`: Cohen's d, r, eta², beta, OR
   - `sample_size`: N
   - `theory_links`: PP, SN, DP, DT, NM, IC, MS, EC, CB, MSI, ART, SRT, Biophilia
   - `mechanism`: Theoretical explanation
   - `quote`: Supporting text

3. **Stimuli** (array):
   - `type`: photograph | rendering | VR | video | physical_space
   - `description`: What stimuli showed
   - `n_stimuli`: Number of stimuli
   - `source`: Figure reference

4. **Tables** (array):
   - `table_id`: Table 1, etc.
   - `description`: What table shows
   - `key_stats`: Important statistics

5. **Images**: Extracted figures/stimuli saved to images directory

---

## Quality Thresholds

Papers are evaluated and routed based on quality:

| Article Type | Min Findings | Require Stats | Require Direction | Min Score |
|-------------|--------------|---------------|-------------------|-----------|
| empirical | 1 | 50% | 90% | 0.6 |
| meta_analysis | 1 | 80% | 90% | 0.7 |
| systematic_review | 1 | 0% | 70% | 0.5 |
| narrative_review | 1 | 0% | 50% | 0.4 |
| theoretical | 0 | 0% | 30% | 0.3 |

Papers that fail quality are requeued (up to 2 retries) then marked failed.

---

## Getting Results for BN/Web Integration

```python
from src.extraction import ExtractionPipeline

pipeline = ExtractionPipeline(
    pdf_dir="data/pdfs",  # or set ARTICLE_EATER_PDF_DIR env var
    output_dir="data/extraction_pipeline"
)

# Get accepted results
ready = pipeline.get_ready_for_integration()
print(f"{len(ready)} papers ready for BN/Web")

# After integration, mark as integrated
pipeline.mark_integrated([doi1, doi2, ...])
```

---

## Troubleshooting

### "Could not acquire lock"
Another process is running. Either wait for it to finish or use `--unlock` if it crashed.

### Papers stuck in "requeued"
They failed quality check. After max retries (2), they move to "failed".

### Low quality scores
Check the extraction results in `results/*.json` for issues. Common problems:
- PDF is OCR-garbled
- Paper is not actually the expected article type
- Statistics are in unusual format

---

## For AI Assistants

When asked to run extraction:

1. **Check status first**: `--status`
2. **Process in batches**: `--resume --batch 50`
3. **Report progress**: Number processed, accepted, remaining
4. **Handle errors**: Use `--unlock` if stuck

The pipeline is designed to be interrupted and resumed safely.
