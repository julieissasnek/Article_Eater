# P8.6 Extraction Quality Metrics

**Date**: 2026-02-17  
**Task**: P8.6 (Sprint 8 — Pipeline Reliability Hardening)  
**Author**: Codex

## Summary

Extended extraction quality instrumentation so fallback behavior is measurable and reviewed continuously.

Updated files:
- `scripts/check_table_extraction_quality.py`
- `scripts/process_realtime_pdf_completion_queue.py`

## What Was Added

### 1) Quality Gate metrics for resolution pathways

`check_table_extraction_quality.py` now reports:
- `environment_resolution_match_type_counts`
- `outcome_resolution_match_type_counts`
- `environment_llm_fallback_rate`
- `outcome_llm_fallback_rate`
- `environment_semantic_fallback_rate`
- `outcome_semantic_fallback_rate`
- `environment_missing_match_type_rate`
- `outcome_missing_match_type_rate`

These are computed on `resolution_rows` (rows with env/out canonical fields), avoiding contamination from non-resolution rows.

### 2) Structured report artifact for periodic review

Added output:
- `--report-json` (default: `data/production/table_extraction_quality_report.json`)

The report includes all core metrics + failures + final gate status, enabling periodic/automated review.

### 3) Per-paper extraction audit enrichment

`process_realtime_pdf_completion_queue.py` audit payload now includes:
- resolution match-type counts
- per-paper LLM fallback rates
- per-paper semantic fallback rates
- warning for missing resolution match-type metadata

This allows paper-level diagnosis in addition to global quality checks.

## Verification

- `python3 -m py_compile scripts/check_table_extraction_quality.py scripts/process_realtime_pdf_completion_queue.py scripts/run_realtime_table_rule_intake.py`
- `python3 scripts/check_table_extraction_quality.py --soft`
- `./venv/bin/pytest -q tests/test_p8_3_variable_resolution_fallbacks.py tests/test_realtime_pipeline_guardrails.py`

## Current Gate Snapshot (from --soft run)

- Unresolved environment rate: `0.0000`
- Unresolved outcome rate: `0.0027`
- LLM fallback rates: `0.0000` (disabled by default)
- Semantic fallback rates: `0.0000` (historical data predates new match types)
- Remaining FAIL source: article type metadata coverage threshold (`0.5334 < 0.9500`), unrelated to P8.6 changes.

