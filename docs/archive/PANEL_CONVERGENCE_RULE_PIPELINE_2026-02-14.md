# Panel Convergence: Rule/Claim Pipeline Reliability (2026-02-14)

## Context Provided to Experts
System objective:
- Keep broad article coverage from abstract-first ingestion.
- Prevent low-confidence/mis-typed articles from injecting brittle causal edges into Web/BN.
- Preserve extracted evidence from PDF stage while explicitly marking uncertainty.

Observed failure pattern:
- Article-type misclassification can produce wrong abstract causal edges.
- Those edges can be ingested into Web/BN before PDF confirmation.
- PDF extraction rows from uncertain article families were not consistently surfaced as verification-required.

Current pipeline anchors:
- Abstract intake: `scripts/run_realtime_table_rule_intake.py`
- PDF completion: `scripts/process_realtime_pdf_completion_queue.py`
- Safe tranche reprocess: `scripts/reprocess_article_type_tranche_safe.py`

## Expert Query Pack
1. Information Extraction Engineer
Question:
- Should abstract-stage causal edge creation be gated by article family confidence/review state, while still preserving table/provenance records?

2. Causal/Bayesian Reliability Engineer
Question:
- For PDF-confirmed rows, should uncertain article family act as a hard block or a soft-trust downgrade (`needs_verification`) so evidence is preserved but trust-weighted downstream?

3. Workflow/Operations Engineer
Question:
- What minimal changes guarantee uncertainty propagation in both main queue and timeout-safe reprocessing paths?

## Converged Recommendation
1. Gate abstract causal edge emission:
- Emit abstract causal edge rules only for empirical-capable families and confident, non-flagged type predictions.
- For non-empirical/uncertain families, emit deferred rule metadata (not active causal edge), preserve table record, and require PDF/manual confirmation.

2. Propagate article-type uncertainty into PDF rows:
- Keep extracted claims, but set `needs_verification=true` when article type is uncertain.
- Add explicit quality flag marker `needs_article_type_verification` to avoid silent promotion.

3. Apply same uncertainty behavior in timeout-safe reprocessing:
- `reprocess_article_type_tranche_safe.py` must pass uncertainty state through to `process_single_row`.

## Revision Plan
1. Add abstract rule gate helper and family allowlist in intake script.
2. Attach gate metadata to abstract table rows (`abstract_rule_eligible`, policy, deferred reason).
3. Emit `edge` rule only when gate passes; otherwise emit `deferred_edge` metadata rule.
4. Prevent in-memory abstract Web/BN integration for gate-failed rows.
5. Extend `process_single_row` signature to accept `article_type_needs_review`.
6. Force `needs_verification` and quality-flag downgrade when uncertain type.
7. Update main queue executor and safe-tranche worker to pass uncertainty flag.
8. Validate by compile + ingestion test suite + quality health script.

## Implementation Status
Completed in this pass:
- `scripts/run_realtime_table_rule_intake.py`
  - Added `EMPIRICAL_ABSTRACT_RULE_FAMILIES`.
  - Added `evaluate_abstract_rule_gate(...)`.
  - Added gate metadata to table records.
  - Added deferred-rule emission path (`rule_type=deferred_edge`) for uncertain/non-empirical abstracts.
  - Skips abstract Web/BN integration when rule gate is not eligible.
- `scripts/process_realtime_pdf_completion_queue.py`
  - `process_single_row(...)` now accepts `article_type_needs_review`.
  - Uncertain type now forces `needs_verification=true` on table/discourse rows.
  - Adds `quality_flag=needs_article_type_verification` (or appends to existing flag).
  - Main queue executor now passes family + uncertainty from classifier diagnostics.
- `scripts/reprocess_article_type_tranche_safe.py`
  - Worker now passes `article_type_needs_review` through to queue processor.

Validation run:
- `python3 -m py_compile scripts/run_realtime_table_rule_intake.py scripts/process_realtime_pdf_completion_queue.py scripts/reprocess_article_type_tranche_safe.py` (pass)
- `pytest -q tests/test_sprint6c_ingestion.py` -> 28 passed
- `python3 scripts/check_table_extraction_quality.py` -> `quality_gate: PASS`

## Practical Effect
- Reduces false-positive abstract causal edges entering Web/BN.
- Preserves extraction recall while marking trust uncertainty explicitly.
- Keeps main and timeout-safe processing behavior consistent.
