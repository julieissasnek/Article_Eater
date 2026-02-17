# P8.3 LLM Fallback for Unmapped Variables

**Date**: 2026-02-17  
**Task**: P8.3 (Sprint 8 — Pipeline Reliability Hardening)  
**Author**: Codex

## Summary

Implemented staged fallback resolution for environment/outcome mapping in both realtime ingestion paths.

Updated files:
- `scripts/run_realtime_table_rule_intake.py`
- `scripts/process_realtime_pdf_completion_queue.py`

## New Resolution Order

For both `env` and `out` mapping:

1. Contract lookup exact (`lookup_exact`)
2. Resolver fuzzy/queue path (`resolver_*`)
3. Optional constrained LLM fallback (`llm_lookup_fallback`)
4. Deterministic semantic fallback (`semantic_lookup_fallback`)
5. Generic class fallback (`generic_keyword`)
6. Explicit unresolved (`UNRESOLVED:*`)

## LLM Fallback Design

LLM fallback is **optional and guarded**:

- Requires `AE_ENABLE_LLM_FALLBACK=1` (or `true/yes`)
- Requires `OPENAI_API_KEY`
- Uses model from `AE_LLM_FALLBACK_MODEL` (default: `gpt-4o-mini`)

Safety constraints:
- LLM can only choose from a constrained shortlist of known lookup terms.
- No free-form canonical ID generation is allowed.
- If no confident shortlist exists, it skips API call.

## Deterministic Semantic Fallback

Added lexical+token-overlap scorer using `SequenceMatcher` + token overlap:
- `lookup_candidate_score(...)`
- `rank_lookup_candidates(...)`
- `semantic_lookup_fallback(...)`

This path remains available even when LLM fallback is disabled.

## Queueing Behavior Improvements

- Outcome path now avoids skipping resolver output when queue helpers are present.
- Unresolved outcomes are queued with contextual snippet if still unresolved after all fallbacks.
- Environment unresolved queueing happens only after all fallback stages fail.

## Verification

Command checks:
- `python3 -m py_compile scripts/run_realtime_table_rule_intake.py scripts/process_realtime_pdf_completion_queue.py`
- `./venv/bin/pytest -q tests/test_p8_3_variable_resolution_fallbacks.py` -> `2 passed`
- `./venv/bin/pytest -q tests/test_realtime_pipeline_guardrails.py` -> `3 passed`

## Notes

In current environment, LLM fallback remains disabled by default (no behavior change unless explicitly enabled). This keeps offline/restricted runs deterministic while enabling stronger fallback when credentials are available.

