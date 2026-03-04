# Sprint Plan: Success Conditions, Tests, and Three-Layer QA Architecture

**Date**: 2026-03-03
**Author**: CW (Claude Code)
**Reviewed by**: David Kirsh
**Status**: PROPOSED

---

## The Problem

The V13 audit scored the system 3.8/10. The root cause is not bad code — the P0 fixes are solid. The root cause is that **142 functions across 5 core service files lack explicit success conditions**, and therefore lack the tests that would catch regressions before they reach production.

### Current Inventory

| File | Functions | Has Docstring | Has Success Conditions | Has Tests |
|------|-----------|---------------|----------------------|-----------|
| `answer_enrichment_orchestrator.py` | 35 | 29/35 (83%) | 3/35 (9%) | ~50 (but mock-heavy) |
| `integrated_query_service.py` | 15 | 14/15 (93%) | 1/15 (7%) | 0 |
| `language_adaptation_service.py` | 19 | 19/19 (100%) | 5/19 (26%) | 6 (in orchestrator tests) |
| `arbitrary_qa_handler.py` | 48 | 42/48 (88%) | 5/48 (10%) | 0 |
| `prose_revision_service.py` | 25 | 21/25 (84%) | 4/25 (16%) | 55 |
| **TOTAL** | **142** | **125 (88%)** | **18 (13%)** | **~111** |

The 88% docstring coverage looks healthy, but only 13% of functions have anything resembling success conditions. And most existing tests use mocks that hide the failure modes the V13 audit found.

---

## Three-Layer QA Architecture

### Layer 1: Success Condition Tests (Deterministic, Every Commit)

**What they are**: Tests derived directly from explicit success conditions written into function docstrings. Each function promises something; the test checks the promise.

**Example**:
```python
def _enrich_credence(self, enriched, beliefs, timeout_ms):
    """Decompose beliefs into credence intervals with confidence.

    SUCCESS CONDITIONS:
    1. Every input belief produces an EnrichedBelief in enriched.enriched_beliefs
    2. paper_ids from input beliefs are preserved in output EnrichedBeliefs
    3. belief_id from input beliefs is preserved in output EnrichedBeliefs
    4. credence_point is a float in [0.0, 1.0] or None if computation fails
    5. credence_ci, if present, has keys: lower, upper, se, width
    6. Service name 'credence_enrichment' appears in services_attempted
    7. On failure, service name appears in services_failed (not silently swallowed)
    """
```

Each success condition generates one test. A function with 7 conditions generates 7 tests. With 142 functions, we expect ~500-800 Layer 1 tests.

**Who runs them**: CI on every commit. Deterministic, fast (<30s for all).

**Who writes them**: Initially, an LLM agent reads each function, writes success conditions, generates tests. David reviews the conditions (the conditions ARE the specification). Tests are mechanical once conditions are approved.

**Reflexive response**: If a Layer 1 test fails, the system first attempts automatic fix (the fix is usually local — a field not being copied, a default not being set). If the fix requires architectural judgment, it escalates to the overseer.

### Layer 2: Systemic Failure Mode Tests (Cross-Boundary, Nightly)

**What they are**: Tests that probe failure modes crossing service boundaries — the kind no single unit test can catch. Already implemented in `test_systemic_failure_modes.py` and `test_p0_fixes_validation.py`.

**Categories**:
- Cross-service data integrity (information survives the full pipeline)
- Silent failure detection (every service failure is visible in output)
- Epistemic invariants (architectural commitments hold across all code paths)
- Budget honesty (latency budget accurately reflected)
- Schema consistency (data structures stable across runs)

**Who runs them**: Nightly overseer. Takes ~90 seconds currently.

**Who writes them**: LLM agent, reviewing the system's architectural commitments and generating tests for each. Panel advisors review whether the invariants are complete.

**Reflexive response**: If a Layer 2 test fails, it means a systemic invariant was broken. This always escalates to the overseer (who may fix it or escalate to David). Layer 2 failures often generate NEW Layer 1 tests that would have caught the underlying issue earlier.

### Layer 3: Adversarial Audit (Weekly/On-Demand)

**What it is**: The V13 Ruthless Audit. An LLM reads the actual source code, reasons about hazardous states, and looks for failure modes that no existing test covers.

**What it does**:
1. Reads all source files
2. Runs all existing tests
3. Asks: "What failure modes are NOT covered by existing tests?"
4. Generates new Layer 1 and Layer 2 tests for any gaps it finds
5. Produces a scored audit report

**Who runs it**: Scheduled weekly by the overseer, or on-demand after major changes.

**Reflexive response**: Layer 3 audits produce test files and audit reports. The tests get added to Layer 1/2 for continuous enforcement. The audit report goes to David for review.

---

## Sprint Plan

### Sprint SC-1: Orchestrator Success Conditions (Priority: HIGHEST)

**Scope**: `answer_enrichment_orchestrator.py` — 35 functions, 3 currently with success conditions
**Estimated effort**: 4-6 hours
**Why first**: This is the composition layer. Every other service flows through here. The V13 P0 bugs were all in this file.

**Tasks**:

| ID | Task | Est. |
|----|------|------|
| SC-1.1 | Write success conditions for all 9 `_enrich_*` methods | 1h |
| SC-1.2 | Write success conditions for `enrich()` main method | 30m |
| SC-1.3 | Write success conditions for `_ServiceRegistry` methods | 30m |
| SC-1.4 | Write success conditions for `EnrichedBelief` and `EnrichedAnswer` | 30m |
| SC-1.5 | Generate Layer 1 tests from SC-1.1-1.4 conditions | 2h |
| SC-1.6 | Run tests, fix any bugs found, re-run | 1h |
| SC-1.7 | Panel review of success conditions (are they complete?) | 30m |

**Expected output**: ~60-80 new Layer 1 tests.

### Sprint SC-2: Integrated Query Service (Priority: HIGH)

**Scope**: `integrated_query_service.py` — 15 functions, 1 with success conditions
**Estimated effort**: 3-4 hours
**Why second**: Framework voices are the most visible part of the system's output. The V13 audit called them "decorative boilerplate." Success conditions will formalize what they SHOULD do.

**Tasks**:

| ID | Task | Est. |
|----|------|------|
| SC-2.1 | Write success conditions for `query()`, `get_theoretical_voices()`, `format_full_response()` | 1h |
| SC-2.2 | Write success conditions for `_generate_panel_comments()`, `_generate_framework_perspective()` | 45m |
| SC-2.3 | Write success conditions for `_semantic_search_templates()`, `_find_article_evidence()` | 45m |
| SC-2.4 | Generate Layer 1 tests | 1h |
| SC-2.5 | Run tests, fix bugs, re-run | 30m |

**Expected output**: ~30-40 new tests.

### Sprint SC-3: QA Handler (Priority: HIGH)

**Scope**: `arbitrary_qa_handler.py` — 48 functions, 5 with partial conditions
**Estimated effort**: 5-7 hours
**Why third**: This is the entry point for all questions. It has 48 functions and ZERO dedicated tests.

**Tasks**:

| ID | Task | Est. |
|----|------|------|
| SC-3.1 | Write success conditions for `classify_question()` (the router) | 30m |
| SC-3.2 | Write success conditions for all `format_*_answer()` handlers (14 handlers) | 2h |
| SC-3.3 | Write success conditions for `ArbitraryQAHandler.answer()` | 30m |
| SC-3.4 | Write success conditions for `build_ai_context()`, `build_ai_prompt()` | 30m |
| SC-3.5 | Generate Layer 1 tests | 2h |
| SC-3.6 | Run tests, fix bugs, re-run | 1h |

**Expected output**: ~80-100 new tests.

### Sprint SC-4: Language Adaptation Service (Priority: MEDIUM)

**Scope**: `language_adaptation_service.py` — 19 functions, 5 with partial conditions
**Estimated effort**: 2-3 hours
**Why fourth**: The V13 audit found `adapt_content()` returns metadata not adapted text. Success conditions will define what "adaptation" actually means.

**Tasks**:

| ID | Task | Est. |
|----|------|------|
| SC-4.1 | Write success conditions for `adapt()`, `adapt_belief_presentation()`, `adapt_content()` | 1h |
| SC-4.2 | Write success conditions for all `_adapt_*` private methods | 30m |
| SC-4.3 | Generate Layer 1 tests | 1h |
| SC-4.4 | Fix `adapt_content()` to actually adapt text (P1 fix) | 30m |

**Expected output**: ~30-40 new tests + P1 fix.

### Sprint SC-5: Prose Revision Service (Priority: LOW)

**Scope**: `prose_revision_service.py` — 25 functions, 4 with partial conditions
**Estimated effort**: 2 hours
**Why last**: Already has 55 tests. Needs success conditions formalized but is the least broken service.

**Tasks**:

| ID | Task | Est. |
|----|------|------|
| SC-5.1 | Write success conditions for `full_critique()`, `suggest_revisions()` | 30m |
| SC-5.2 | Write success conditions for all `find_*` diagnostic methods | 30m |
| SC-5.3 | Generate any missing Layer 1 tests | 1h |

**Expected output**: ~20 new tests.

### Sprint SC-6: Layer 2/3 Infrastructure (Priority: MEDIUM)

**Scope**: Nightly overseer test configuration
**Estimated effort**: 2-3 hours

**Tasks**:

| ID | Task | Est. |
|----|------|------|
| SC-6.1 | Create `tests/layer2_nightly/` directory with systemic test suites | 30m |
| SC-6.2 | Create `scripts/run_nightly_audit.py` — runs Layer 2 tests + generates report | 1h |
| SC-6.3 | Create `scripts/run_adversarial_audit.py` — Layer 3 prompt template + execution | 1h |
| SC-6.4 | Add Layer 2/3 test results to TASKS.md via automated parser | 30m |

---

## Summary

| Sprint | Scope | New Tests | Hours |
|--------|-------|-----------|-------|
| SC-1 | Orchestrator | ~70 | 5 |
| SC-2 | Integrated Query | ~35 | 3.5 |
| SC-3 | QA Handler | ~90 | 6 |
| SC-4 | Language Adaptation | ~35 | 2.5 |
| SC-5 | Prose Revision | ~20 | 2 |
| SC-6 | Layer 2/3 Infra | — | 2.5 |
| **TOTAL** | **5 services** | **~250** | **~21.5** |

From ~111 tests to ~360 tests. From 13% success condition coverage to ~90%.

---

## Panel Consultation Points

Before executing, these decisions benefit from panel input:

1. **What counts as a success condition for a function that generates text?** (e.g., `_generate_framework_perspective()`) — Can we test that the output is semantically relevant to the topic, or only that it has the right structure?

2. **Should `adapt_content()` be fixed to actually adapt text (P1), or should the success condition formalize the current metadata-return behavior?** — If the latter, the function is working as designed; the problem is that the orchestrator expects adaptation it doesn't get.

3. **How should success conditions handle stochastic outputs?** — Functions that involve LLM calls return different text each time. Success conditions can test structure but not content. Is that sufficient?

4. **Should Layer 1 tests use real services or mocks?** — Real services test integration but are slow and flaky. Mocks are fast but miss the bugs the V13 audit found. Recommendation: both — a "fast" mock suite for CI, and a "real" integration suite for nightly.

---

## Execution Order

Given the anti-wait-state rule: start SC-1 immediately (highest priority, most critical). SC-2 and SC-3 can run in parallel after SC-1 completes. SC-4, SC-5, SC-6 can interleave.

**Next action**: Begin SC-1.1 — write success conditions for the 9 `_enrich_*` methods.
