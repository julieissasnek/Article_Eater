# Table Generation Execution (2026-02-13)

## Inputs and Gates Used
- Production gate doc: `/Users/davidusa/REPOS/Article_Finder_v3_2_3/docs/PRODUCTION_RUN.md`
- Gate script: `/Users/davidusa/REPOS/Article_Finder_v3_2_3/scripts/production_run.py`
- DB: `/Users/davidusa/REPOS/Article_Finder_v3_2_3/data/article_finder.db`
- Reject candidates export: `/Users/davidusa/REPOS/Article_Finder_v3_2_3/data/review/reject_candidates.csv`

## Production Gate Run
Command:

```bash
python3 scripts/production_run.py \
  --db data/article_finder.db \
  --high-cite-threshold 150 \
  --export data/review/reject_candidates.csv
```

Result:
- Total papers: 16073
- Reject candidates: 3582
- Protected rejects: 729
- High-citation rejects: 0
- Gate status: failed on `pdf_coverage` threshold (non-destructive; export still generated)

## New Artifacts Added (Article Eater)

### Queue + Pruning-Aware Selection
- `scripts/build_table_extraction_queue.py`
- `config/table_must_include_seeds.txt`
- `data/table_queue/table_extraction_queue.csv` (109 rows)
- `data/table_queue/protected_rejects_review.csv` (11 rows)
- `data/table_queue/table_extraction_queue_summary.md`

### Abstract Reduced Tables + Download Priorities
- `scripts/build_abstract_reduced_tables.py`
- `data/table_queue/abstract_reduced_tables.csv` (9740 rows)
- `data/table_queue/download_priority_for_pdf.csv` (150 rows)
- `data/table_queue/abstract_reduced_tables_summary.md`

### Codex Gold Pack for Model Benchmarking
- `scripts/build_table_gold_pack.py`
- `data/table_gold/codex_gold_v1/manifest.csv`
- `data/table_gold/codex_gold_v1/raw_tables.jsonl`
- `data/table_gold/codex_gold_v1/codex_gold_rows.csv`
- `data/table_gold/codex_gold_v1/manual_adjudication_queue.csv`
- `data/table_gold/codex_gold_v1/summary.md`

### Gold-vs-Model Comparison Harness
- `scripts/compare_gold_vs_model_tables.py`
- `docs/HAIKU_TABLE_PROMPT_CANDIDATE_2026-02-13.md`

## Gold Pack Run Summary
From `data/table_gold/codex_gold_v1/summary.md`:
- Queue input rows: 98
- Processed PDFs: 87
- Missing PDFs: 11
- Failed extractions: 0
- Gold rows written: 149

## Notes and Constraints
1. No Anthropic API key was present in environment, so Haiku extraction was not executed in this run.
2. Citation mode in current DB is local graph citation counts (global cited_by_count column not present), so citation ranking is conservative.
3. Abstract reduced tables are explicitly labeled provisional (`abstract_only_reduced_table`) and should not be used as final causal evidence.
4. Provenance markers now distinguish abstract vs PDF artifacts:
   - abstract: `provenance_tier=abstract_provisional`, `requires_pdf_confirmation=true`
   - PDF table extraction: `provenance_tier=pdf_confirmed`, `requires_pdf_confirmation=no`

## Realtime Production Line
- Script: `scripts/run_realtime_table_rule_intake.py`
- Behavior per run:
  1. Creates provisional abstract table record for each newly found paper.
  2. Creates provisional abstract rule record for each newly found paper.
  3. Integrates provisional abstract beliefs into Web of Belief + incremental BN (lower evidence weight).
  4. Queues papers with `pdf_path` into `data/production/realtime_pdf_completion_queue.csv` for completion extraction.
- Completion script: `scripts/process_realtime_pdf_completion_queue.py`
  - drains queued PDFs in batch and writes `data/production/realtime_pdf_confirmed_rows.csv`
  - integrates PDF-confirmed beliefs into Web + BN at higher evidence weight
- Continuous orchestration: `scripts/run_realtime_production_worker.py`

## Next Step Commands

### Run codex gold pack again (if queue updates)
```bash
cd /Users/davidusa/REPOS/Article_Eater_PostQuinean_v1
python3 scripts/build_table_gold_pack.py \
  --queue-csv data/table_queue/table_extraction_queue.csv \
  --max-papers 98 \
  --output-dir data/table_gold/codex_gold_v1
```

### Compare Haiku output against codex gold
```bash
cd /Users/davidusa/REPOS/Article_Eater_PostQuinean_v1
python3 scripts/compare_gold_vs_model_tables.py \
  --gold-csv data/table_gold/codex_gold_v1/codex_gold_rows.csv \
  --model-csv <path/to/haiku_rows.csv> \
  --output-md data/table_gold/haiku_vs_gold_report.md
```
