# V4 Extraction Pilot — Quick Start Guide

**For David's immediate use on your machine**
**Updated: 2026-03-05 (v2 — with pipeline robustness)**

---

## In 30 Seconds — Walk Away Mode

The V4 system extracts **all 200+ schema fields** from articles, not just the 30 V3 extracts. It includes pre-flight checks, retry with backoff, checkpoint/resume, budget tracking, dead letter queue, and full telemetry.

### Recommended: Unattended Batch (approve once, walk away)

```bash
# In Claude Code — CC asks permission ONCE for this, then runs unattended
bash scripts/v4_batch_pilot.sh
```

Edit the configuration at the top of `v4_batch_pilot.sh` to change:
- `LIMIT=10` → number of papers (start with 10, scale up)
- `BUDGET=50` → max spend in USD
- `MODEL="gemini-2.5-flash"` → model choice
- `VERIFY_FRACTION=0.2` → how many papers get cross-verified

The batch script handles: dependency check → DOI list generation → extraction → analysis → summary report. All output goes to `data/v4_pilot/` and a timestamped log file.

### Alternative: Direct commands

```bash
# Single PDF
python scripts/v4_staged_extraction.py --pdf ~/Papers/my_paper.pdf

# Batch (one DOI per line in file)
python scripts/v4_staged_extraction.py --batch dois.txt --limit 10

# Analyze results
python scripts/v4_pilot_analysis.py --results data/v4_pilot/*.json
```

---

## Setup (One-Time)

```bash
# 1. Install dependencies
pip install google-genai anthropic

# 2. Set API keys
export GEMINI_API_KEY="your-gemini-key"
export ANTHROPIC_API_KEY="your-anthropic-key"  # Optional, for verification

# 3. Check it works (pre-flight + dry run, no API calls)
python scripts/v4_staged_extraction.py --dry-run --pdf /any/path.pdf
```

---

## Common Commands

| Task | Command |
|------|---------|
| **Single PDF** | `python scripts/v4_staged_extraction.py --pdf /path/to/file.pdf` |
| **Single DOI** | `python scripts/v4_staged_extraction.py --doi 10.1234/example` |
| **Batch (10 papers)** | `python scripts/v4_staged_extraction.py --batch dois.txt --limit 10` |
| **Batch (all, $50 budget)** | `python scripts/v4_staged_extraction.py --batch dois.txt --budget 50` |
| **Resume after crash** | `python scripts/v4_staged_extraction.py --batch dois.txt --resume` |
| **Force start (kill competitors)** | `python scripts/v4_staged_extraction.py --batch dois.txt --force` |
| **Verify 50% instead of 20%** | `python scripts/v4_staged_extraction.py --batch dois.txt --verify-fraction 0.5` |
| **Dry run** | `python scripts/v4_staged_extraction.py --batch dois.txt --dry-run` |
| **Sequential mode** | `python scripts/v4_staged_extraction.py --batch dois.txt --sequential` |
| **Analyze results** | `python scripts/v4_pilot_analysis.py --results data/v4_pilot/v4_extraction_final_*.json` |

---

## What Happens When You Run It

1. **Pre-flight check**: Scans for competing processes, validates API keys, checks disk space
2. **Checkpoint load**: If `--resume`, skips already-completed DOIs
3. **Per paper**:
   - Stage 1: Classify article type (Gemini Flash, ~5s, ~$0.001)
   - Stage 2: Family-specific extraction with field forcing (~30-60s, ~$0.03-0.10)
   - Stage 3: Verification by Claude (20% of papers, ~$0.005-0.01)
   - Checkpoint written after each paper (crash-safe)
4. **Budget check**: Stops if cumulative cost hits limit
5. **Graceful shutdown**: Ctrl-C finishes current paper, saves state, exits
6. **Summary**: Field coverage report, cost breakdown, anomaly list

---

## Output Directory

```
data/v4_pilot/
├── v4_extraction_final_20260305_143022.json     # Results
├── v4_telemetry_20260305_143022.json            # System experience log
├── v4_extraction_log_20260305_143022.txt         # Full console transcript
├── dead_letter_queue.jsonl                       # Failed papers for review
└── checkpoints/
    ├── wal.jsonl                                 # Write-ahead log
    └── checkpoint_state.json                     # Resume state
```

---

## Pipeline Robustness Features

| Feature | What It Does |
|---------|-------------|
| **Pre-flight check** | Kills competing extractors, validates API keys, checks disk |
| **Process lock** | Prevents two V4 instances from running simultaneously |
| **Retry + backoff** | 3 retries with exponential backoff + jitter on transient API failures |
| **Checkpoint/resume** | Write-ahead log; crash → restart picks up where you left off |
| **Dead letter queue** | Permanent failures saved for human review |
| **Budget kill switch** | Stops when cumulative cost hits --budget limit (default: $200) |
| **Graceful shutdown** | Ctrl-C finishes current paper, saves checkpoint, exits cleanly |
| **Telemetry** | Logs decisions, anomalies, field coverage surprises, timing |
| **File logging** | Full transcript saved to disk (not just console) |

---

## Expected Results

### Field Coverage by Type

**Empirical Papers**: sample_size 80%+, direction 95%+, effect_size 70%+, scope_conditions 50%+

**Meta-Analysis**: effect_size 100%, confidence_interval 100%

**Theoretical Papers**: mechanism_chain 70%+, theory_commitments 60%+

**Qualitative Papers**: quote 90%+, provenance_depth 85%+

---

## Costs

- **Per paper (stages 1-2)**: $0.04-$0.11
- **Per paper with verification**: $0.05-$0.13
- **For 10 papers**: ~$0.50-$1.30
- **For 100 papers**: ~$5-$13
- **Full corpus (778 papers)**: ~$31-$86

---

## Troubleshooting

### "Competing processes found"
```bash
python scripts/v4_staged_extraction.py --batch dois.txt --force
# Or kill them manually first
```

### "Lock file held by PID..."
```bash
python scripts/v4_staged_extraction.py --batch dois.txt --force
# Force removes stale lock and kills the holder
```

### "Budget exceeded"
```bash
# Increase budget
python scripts/v4_staged_extraction.py --batch dois.txt --budget 300
```

### "JSON parse error" after retries
```bash
# Check dead letter queue for details
cat data/v4_pilot/dead_letter_queue.jsonl | python -m json.tool
# Re-run with verbose
python scripts/v4_staged_extraction.py --pdf /path.pdf --verbose
```

### Resuming after crash
```bash
# Same command — checkpoint automatically resumes
python scripts/v4_staged_extraction.py --batch dois.txt
# Already-completed DOIs are skipped
```

---

## Full Documentation

- Architecture and design: See `V4_IMPLEMENTATION_SUMMARY.md`
- Prompts and field requirements: See `src/extraction/v4_prompts.py`
- Comprehensive report: See `docs/V4_COMPREHENSIVE_REPORT_2026_03_05.md`
- Implementation details: See script source code (2,100 lines, fully commented)

---

**Questions?** Check the full README or review the code comments.
