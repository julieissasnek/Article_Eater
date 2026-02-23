# Realtime Table/Rule Production Line (2026-02-13)

## Requirement
Every newly discovered article must immediately get:
1. A table artifact.
2. A rule artifact.
3. A PDF-completion queue entry if a PDF path exists.

## Implemented Script
- `scripts/run_realtime_table_rule_intake.py`
- `scripts/process_realtime_pdf_completion_queue.py`
- `scripts/run_realtime_production_worker.py`
- `scripts/preprocess_pdf_queue.py`

## What It Does
On each run (incremental via watermark state):
1. Reads new papers from AF DB (`created_at/retrieved_at/updated_at` watermark).
2. Creates provisional abstract-based table records in:
   - `data/production/realtime_tables.jsonl`
3. Creates provisional abstract-based rule records in:
   - `data/production/realtime_rules.jsonl`
4. Integrates provisional abstract beliefs into:
   - Web of Belief (via `WebAccumulator`)
   - Incremental BN (lower weight for abstract evidence)
5. If `pdf_path` exists, enqueues paper in:
   - `data/production/realtime_pdf_completion_queue.csv`
6. Updates watermark in:
   - `data/production/realtime_intake_state.json`

PDF completion worker:
0. (Optional but recommended) Preprocess queued PDFs in parallel:
   - parse diagnostics + text-density signals
   - page-level text cache for audit/discourse extraction support
   - queue marking: `preprocess_status=ready|quarantine|missing_pdf|error`
1. Reads queued PDF rows in batches.
2. Extracts PDF tables/claims.
3. Writes PDF-confirmed rows:
   - `data/production/realtime_pdf_confirmed_rows.csv`
4. Extracts discourse claims from introduction/related work/discussion/conclusion:
   - Theory links (`claim_type=theory_link`)
   - Inter-article relations (`claim_type=inter_article_relation`)
5. Emits per-paper extraction audit:
   - `data/production/realtime_extraction_audit.jsonl`
6. Emits manual quality review queue:
   - `data/review/table_quality_manual_queue.csv`
7. Integrates PDF-confirmed beliefs into Web + BN (higher weight).
8. Marks queue row status (`completed_*`, `missing_pdf`, `error_*`).

## Provenance Marking Policy
### Abstract-derived artifacts
- `evidence_level`: `abstract_only_reduced_table` (tables) or `abstract_finding_rule` (rules)
- `provenance_tier`: `abstract_provisional`
- `requires_pdf_confirmation`: `true`
- `status`: `provisional` (rules)

### PDF-derived table artifacts
- `evidence_level`: `pdf_table_extracted`
- `provenance_tier`: `pdf_confirmed`
- `requires_pdf_confirmation`: `no`
- Emitted by: `scripts/build_table_gold_pack.py`

## Web/BN Behavior
- Abstract-derived provisional rules are now integrated immediately into the Web of Belief and BN updates (with reduced weight).
- PDF-derived confirmations are integrated as stronger evidence and can refine BN edge estimates.

## Operational Commands
Dry run:
```bash
python3 scripts/run_realtime_table_rule_intake.py --dry-run --limit 50
```

Production run:
```bash
python3 scripts/run_realtime_table_rule_intake.py --limit 250
```

PDF queue batch run:
```bash
python3 scripts/process_realtime_pdf_completion_queue.py \
  --batch-size 80 \
  --max-workers 6 \
  --prioritize-preprocessed \
  --integrate-web \
  --update-bn
```

PDF preprocess batch run:
```bash
python3 scripts/preprocess_pdf_queue.py \
  --queued-only \
  --batch-size 200 \
  --max-workers 8
```

Quality gate run:
```bash
python3 scripts/check_table_extraction_quality.py
```

Continuous worker (fast cadence):
```bash
python3 scripts/run_realtime_production_worker.py \
  --poll-seconds 20 \
  --intake-limit 40 \
  --preprocess-pdfs \
  --preprocess-batch-size 200 \
  --preprocess-workers 8 \
  --pdf-batch-size 80 \
  --pdf-workers 6 \
  --skip-preprocess-quarantine \
  --quality-gate
```

## Recommended Scheduling
Run continuously via worker; equivalent cron cadence would be every 20-60 seconds depending on load.

## Guarantee
This gives immediate table+rule coverage for every new paper, while preserving a strict marker boundary between provisional abstract evidence and confirmed PDF-based extraction.
