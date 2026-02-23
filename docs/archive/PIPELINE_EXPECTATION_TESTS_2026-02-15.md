# Pipeline Expectation Tests (2026-02-15)

Purpose:
- Verify we are getting the behavior we intend, not just passing extraction runs.

## 1) Policy Guardrail Unit Tests
File:
- `tests/test_realtime_pipeline_guardrails.py`

Checks:
- Abstract rule gate allows confident empirical families.
- Abstract rule gate defers non-empirical/uncertain families.
- PDF claim rows from uncertain article types are always marked:
  - `needs_verification=true`
  - `quality_flag` includes `needs_article_type_verification`.

Run:
- `pytest -q tests/test_realtime_pipeline_guardrails.py`

## 2) Data-Level Expectation Gate (Real Outputs)
File:
- `scripts/verify_pipeline_expectations.py`

Checks on current CSV artifacts:
- No queue row regresses from prior successful extraction (`prior_status=completed_pdf_extracted`) to timeout/error/no-claims.
- In recent confirmed tranche rows, uncertainty propagation is present at required rates:
  - `needs_verification=true` rate >= threshold (default 0.95)
  - `quality_flag` marker rate >= threshold (default 0.95)

Run:
- `python3 scripts/verify_pipeline_expectations.py`

Current result:
- `expectation_gate: PASS`

## 3) Corpus Health Gate
File:
- `scripts/check_table_extraction_quality.py`

Use:
- Global extraction health and coverage tracking.

Run:
- `python3 scripts/check_table_extraction_quality.py`

Current result:
- `quality_gate: PASS`
