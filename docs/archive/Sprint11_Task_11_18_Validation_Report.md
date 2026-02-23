# Sprint 11 Task 11.18 Validation Report

Date: 2026-02-17
Agent: Codex

## Scope

Validation sweep for paper evaluation pipeline readiness:
1. Ulrich 1984 evaluation sanity
2. Contradicting study behavior (Task 11.14)
3. Novel gap behavior (Task 11.15)
4. Full repository test suite health
5. Match/assessment coverage across Batch 2 paper corpus

## Results

- Ulrich 1984 (`data/test_papers/ulrich_1984.json`)
  - `status=complete`
  - `n_claims_extracted=2`
  - `n_claims_matched=2`
  - `findings=2`
- Contradiction + gap regressions:
  - `tests/test_paper_eval_contradicting_study.py` passed
  - `tests/test_paper_eval_novel_gap.py` passed
- Targeted paper pipeline run:
  - `tests/test_paper_eval_pipeline.py` passed
  - `tests/test_cmr_paper_eval.py` passed
  - Aggregate: `7 passed`
- Full suite:
  - `./.venv/bin/pytest -q`
  - `3282 passed, 14 skipped, 9 warnings`

## Coverage Snapshot (Batch 2 Test Papers)

- Files evaluated: `10`
- Total claims: `20`
- Claims with at least one template match: `18` (`90.0%`)
- Total template matches generated: `31`
- Claims assessed into findings: `20` (`100%`)

## Readiness Assessment

- Readiness: **Pass**
- Pipeline behavior is coherent for confirmation/contradiction/gap paths.
- Coverage is strong for current template inventory.
- Known nuance: VOI aggregate is exposed at `report.summary.aggregate_voi` rather than top-level `aggregate_voi`.
