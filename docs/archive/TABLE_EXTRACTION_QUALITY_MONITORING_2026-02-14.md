# Table Extraction Quality Monitoring (2026-02-14)

## New production artifacts
- `data/production/realtime_extraction_audit.jsonl`
  - One JSON object per processed PDF with quality metrics and warnings.
- `data/review/table_quality_manual_queue.csv`
  - Papers requiring manual review due to quality-gate flags.

## Claim-level provenance now captured
`data/production/realtime_pdf_confirmed_rows.csv` now includes:
- `source_section`
- `source_page_start`
- `source_page_end`
- `source_quote`
- `source_quote_hash`
- `quality_flag`
- `argument_relation_type`
- `citation_text` / `citation_doi` / `target_paper_id` / citation match fields

## New discourse extraction channel
For each PDF, the worker now scans introduction/related work/discussion/conclusion and emits:
- `claim_type=theory_link`
- `claim_type=inter_article_relation`

These are written into `realtime_pdf_confirmed_rows.csv` with page/section anchors.

## Quality gate command
```bash
python3 scripts/check_table_extraction_quality.py
```

Thresholds are configured in:
- `config/table_extraction_quality_thresholds.json`

## Continuous worker integration
Optional per-cycle gate check:
```bash
python3 scripts/run_realtime_production_worker.py --quality-gate
```

## Current baseline status (legacy data)
When the gate is run before a full reprocess, failures are expected due to legacy rows lacking anchors/relations.
