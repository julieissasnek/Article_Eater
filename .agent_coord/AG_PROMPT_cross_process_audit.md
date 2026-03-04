# AG Prompt: Cross-Process Success Condition Audit

**Date**: 2026-03-04
**From**: CW
**Priority**: HIGH — David specifically requested this audit

## Task

Audit ALL success conditions in `contracts/success_conditions.json` to classify each as:

1. **PROCESS_INTERNAL**: Tests only within the function/module it's defined over. The test instantiates the module, calls its methods, and checks its return values. No other module is instantiated or invoked.

2. **STATIC_CROSS_PROCESS**: Tests compatibility between two modules (e.g., enum values match, schema fields align) but does NOT test runtime signal propagation. These catch interface mismatches but NOT trigger failures.

3. **RUNTIME_CROSS_PROCESS**: Tests that a trigger fired by Module A actually arrives at Module B and produces an observable effect in Module B's state. These are the gold standard — they catch "last mile" failures where everything is wired but the signal never propagates.

4. **MISSING_CROSS_PROCESS**: Identify trigger-to-effect chains that EXIST IN THE CODE but have NO corresponding success condition. These are the most dangerous gaps — the wiring exists, it might work, but nobody will know if it breaks.

## Method

For each success condition (there are ~110):

1. Read the condition's `description` and `metric`
2. Read the corresponding test (if it exists) in the test suite
3. Classify as PROCESS_INTERNAL, STATIC_CROSS_PROCESS, or RUNTIME_CROSS_PROCESS
4. For PROCESS_INTERNAL conditions, note what cross-process trigger chain they SHOULD be part of

Then, independently:

5. Read the following integration points in the codebase and identify trigger chains that lack success conditions:
   - `src/services/overseer.py` — POST_INTEGRATION hook, _update_card_staleness(), scheduler triggers
   - `src/services/paper_integration/orchestrator.py` — 14-step cascade, what it triggers after completion
   - `scripts/scheduled_pipeline.py` — stage-to-stage handoffs
   - `scripts/nightly_integration_pipeline.py` — what it triggers in overseer, AESHI, constraint propagation
   - `src/qa/card_generation_orchestrator.py` — on_new_evidence(), on_credence_shift(), check_and_queue_stale()
   - `src/qa/card_retriever.py` — try_match_unified() bridge between old and new schemas
   - `src/qa/extraction_field_validator.py` — validate_and_gate() blocking logic
   - `src/services/finding_template_relevance.py` — persist_relevance_to_web_db() integration

## Output Format

Create `docs/CROSS_PROCESS_AUDIT_2026-03-04.md` with:

### Section 1: Classification Table

| SC ID | Module | Classification | Trigger Chain (if applicable) | Gap Description |
|-------|--------|---------------|------------------------------|-----------------|
| SP-SC1 | scheduled_pipeline | PROCESS_INTERNAL | Pipeline → extraction → integration → overseer | No test verifies extraction output reaches integration |
| ... | ... | ... | ... | ... |

### Section 2: Missing Cross-Process Conditions

For each identified gap, write a proposed success condition in the same format as existing ones:

```json
{
  "id": "SC-XPROC-N",
  "name": "...",
  "description": "...",
  "metric": "...",
  "threshold": "...",
  "test_name": "...",
  "rationale": "...",
  "trigger_source": "module that fires the trigger",
  "effect_target": "module that should receive the effect",
  "chain": ["step1", "step2", "step3"]
}
```

### Section 3: Priority Ranking

Rank the missing cross-process conditions by:
- **Severity**: How bad is it if this chain breaks silently? (HIGH/MED/LOW)
- **Likelihood**: How likely is it to break? (HIGH if components were developed independently, LOW if tightly coupled)
- **Detectability**: How quickly would we notice? (HIGH if invisible, LOW if other symptoms appear)

The top priority conditions should be the ones that are HIGH severity, HIGH likelihood, and HIGH undetectability — these are the silent killers.

### Section 4: Proposed Test Skeletons

For the top 10 missing cross-process conditions, write a test skeleton showing:
- What gets instantiated (real objects, not mocks)
- What trigger gets fired
- What effect gets asserted
- What the failure mode looks like if the chain is broken

## Key Insight from David

David's exact observation: "the last mile trigger - even if hooked up - never is tested to see if it was pulled (or still needs another pull)."

The audit should focus especially on triggers that ARE wired in the code but are NOT verified by any test. These represent the highest-risk gaps because:
1. The developer thinks they're done (the wiring exists)
2. The success condition thinks it's covered (the module-level test passes)
3. But the actual runtime signal may never propagate (and nobody knows)

## Files to Read

- `contracts/success_conditions.json` — the full registry (~1,248 lines, ~110 conditions)
- `tests/test_card_schema.py` — 44 tests
- `tests/test_card_integration_e2e.py` — 15 tests
- `tests/test_card_generation_orchestrator.py` — 60 tests
- All test files in `tests/` directory
- All source files listed in the integration points above
