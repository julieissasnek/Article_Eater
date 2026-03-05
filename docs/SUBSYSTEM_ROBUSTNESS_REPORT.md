# ATLAS Subsystem Robustness Report

**Date**: 2026-03-05
**Author**: AG (Antigravity)
**Version**: 1.0

---

## Test Baseline

| Metric | Value |
|:-------|:------|
| **Suite run** | 2026-03-05, Python 3.14.2, pytest 9.0.2 |
| **Total tests** | 6,748 passed / 9 failed / 52 skipped |
| **Duration** | 214.42s |
| **Collection errors** | 1 (`test_figure_suggestion_service.py` — ImportError `FigureMetadata`) |

---

## Per-Subsystem Test Results

### S1. Article Finder / Paper Acquisition

| Test Area | Result | Notes |
|:----------|:-------|:------|
| Acquisition tests | ✅ Pass | `test_acquisition_integration.py` |
| Triage tests | ✅ Pass | `test_paper_triage.py` (within S2 tests) |
| **E2E: VOI gap → search → acquire** | ❌ Not testable | API keys not configured (RED) |

**Robustness Score**: 3/10 — Cannot verify end-to-end in current environment. Triage logic works but full pipeline blocked by missing API credentials.

**Critical Failure Modes**:
1. Zero API keys configured → no paper acquisition possible
2. No fallback acquisition path when APIs are down
3. No rate-limit backoff testing

---

### S2. Extraction Pipeline

| Test Area | Tests | Pass | Fail | Notes |
|:----------|:------|:-----|:-----|:------|
| Claim extraction | 51 | 51 | 0 | Full coverage |
| Extraction field validator | 89 | 88 | 1 | `test_quality_score_perfect` — threshold drift |
| Extraction gate | 14 | 11 | 3 | Gate scoring threshold mismatch |
| Two-pass verification | 6 | 6 | 0 | Second-pass delta detection |
| V3 prompts | 12 | 12 | 0 | All 5 article families |

**Robustness Score**: 8/10 — Strong test coverage. The 4 failures are threshold calibration issues (gate expects 0.8+ but validator scores 0.7 for "passing" extractions), not logic bugs.

**Critical Failure Modes**:
1. Gate threshold drift: validator tightened scoring (v3 additions) but gate tests not updated
2. No adversarial prompt injection testing
3. LLM non-determinism not accounted for in tests (no retry/variance tracking)

---

### S3. Antecedent/Consequent Tagging

| Test Area | Tests | Pass | Fail | Notes |
|:----------|:------|:-----|:-----|:------|
| Belief-env-outcome extractor | 28 | 28 | 0 | Mapping extraction |
| Canonical variables | 15 | 15 | 0 | Variable normalization |
| IV/DV classifier | 19 | 19 | 0 | Classification logic |

**Robustness Score**: 5/10 — Unit tests pass but the critical BN mapping chain is broken (0% beliefs map to BN nodes). Tests validate mapping *logic* but not *coverage* against real corpus.

**Critical Failure Modes**:
1. **0% BN node mapping** — belief IDs (DOI-based) don't match BN node IDs (env+outcome canonical pairs)
2. Keyword matching has unknown recall against real extraction output vocabulary
3. No cross-subsystem integration test verifying S3→S6 data flow

---

### S4. Image Analyzer

| Test Area | Tests | Pass | Fail | Notes |
|:----------|:------|:-----|:-----|:------|
| Image pipeline | Minimal | Pass | 0 | Basic pipeline init tests |
| Image tag service | 12 | 12 | 0 | 41-attribute vocabulary |

**Robustness Score**: 2/10 — Stub implementations throughout. `download_image()` returns mock data. No real image classification. Tests verify stub behavior, not actual CV capability.

**Critical Failure Modes**:
1. `ImageDownloadManager.download_image()` is STUBBED (returns mock)
2. `ImageMetadataExtractor.extract()` is STUBBED
3. `_compute_perceptual_hash_stub()` is a placeholder
4. No real vision API integration

---

### S5. Web of Belief

| Test Area | Tests | Pass | Fail | Notes |
|:----------|:------|:-----|:-----|:------|
| Web of Belief core | 78 | 78 | 0 | Belief CRUD, coherence, constraints |
| Bridge warrants | 35 | 35 | 0 | Noisy-OR, credence formula |
| Entrenchment | 22 | 22 | 0 | Quine-style replay |
| Coherence monitoring | 18 | 18 | 0 | Threshold detection |
| Stability engine | 14 | 14 | 0 | Belief delta tracking |

**Robustness Score**: 9/10 — Comprehensive test coverage across all sub-modules. Coherence, constraints, provenance all verified.

**Critical Failure Modes**:
1. Coherence computation is O(n²) for large belief sets — potential scaling issue beyond 10K beliefs
2. No stress test with adversarial beliefs (contradictory evidence flooding)

---

### S6. Bayesian Network

| Test Area | Tests | Pass | Fail | Notes |
|:----------|:------|:-----|:-----|:------|
| BN health | 19 | 19 | 0 | DAG checks, edge integrity |
| BN coherence client | 12 | 12 | 0 | BN-Web sync |
| Incremental BN | 27 | 27 | 0 | Beta-Bernoulli updates |

**Robustness Score**: 4/10 — Math and structure tests pass, but the BN is empty in practice (0 beliefs mapped). Tests verify the engine works correctly on synthetic data, but the data pipeline to populate it is broken.

**Critical Failure Modes**:
1. **0 real data mapped** — BN engine works but has no input
2. pgmpy dependency optional fallback untested in CI
3. No sensitivity analysis (how much does belief X change when evidence Y is updated?)

---

### S7. QA & Answer System

| Test Area | Tests | Pass | Fail | Notes |
|:----------|:------|:-----|:-----|:------|
| E2E QA pipeline | 18 | 18 | 0 | Query→search→answer |
| Answer enrichment | 42 | 42 | 0 | 9-step orchestrator |
| Card generation | 31 | 31 | 0 | 9-type card taxonomy |
| Card tab generators | 38 | 38 | 0 | All prose tabs |
| Pipeline QA integration | 6 | 4 | 2 | Sandbox permission (not QA logic) |

**Robustness Score**: 8/10 — Strong test coverage. The 2 failures are sandbox permission issues (can't write logs), not QA logic. File-based search architecture prevents LLM hallucination excellently.

**Critical Failure Modes**:
1. No semantic search — keyword only, so nuanced queries may miss relevant findings
2. No answer quality evaluation (no recall/precision metrics)
3. Enrichment budget can reach 18s worst-case (should be capped at 5s)

---

### S8. Overseer & Health

| Test Area | Tests | Pass | Fail | Notes |
|:----------|:------|:-----|:-----|:------|
| Overseer core | 24 | 24 | 0 | 6-component init |
| Overseer self-healing | 15 | 15 | 0 | Playbook execution |
| Overseer diagnostician | 11 | 11 | 0 | Diagnostic analysis |
| System health | 18 | 18 | 0 | AESHI computation |

**Robustness Score**: 9/10 — 140+ invariants comprehensive. Self-healing and diagnostics well-tested.

**Critical Failure Modes**:
1. Nightly audit depends on SQLite — sandbox permission can block execution
2. No chaos engineering (what happens when overseer itself fails?)

---

### S9. Content Creation / ATLAS Cards

| Test Area | Tests | Pass | Fail | Notes |
|:----------|:------|:-----|:-----|:------|
| Card integration E2E | 14 | 14 | 0 | End-to-end card generation |
| Card quality validation | 8 | 8 | 0 | SC-PH, SC-SD, SC-PR, SC-CQ |
| Card retrieval | 12 | 12 | 0 | Card lookup and rendering |

**Robustness Score**: 7/10 — Good coverage. Crash-safe orchestration well-tested but no load/stress testing.

**Critical Failure Modes**:
1. Two-pass generation requires LLM API availability (single point of failure)
2. No circuit breaker for LLM API failures during batch generation

---

## Robustness Summary

| Subsystem | Score | Tests Pass | Tests Fail | Status |
|:----------|:------|:-----------|:-----------|:-------|
| S1. Article Finder | 3/10 | ✅ | 0 | ❌ Can't test E2E (no API keys) |
| S2. Extraction | 8/10 | 168 | 4 | ⚠️ Gate threshold drift |
| S3. Tagging | 5/10 | 62 | 0 | ⚠️ 0% BN mapping |
| S4. Image | 2/10 | 12 | 0 | ❌ Stubs only |
| S5. Web of Belief | 9/10 | 167 | 0 | ✅ Excellent |
| S6. Bayesian Network | 4/10 | 58 | 0 | ❌ 0% data populated |
| S7. QA | 8/10 | 133 | 2 | ✅ Good (sandbox issues only) |
| S8. Overseer | 9/10 | 68 | 0 | ✅ Excellent |
| S9. Content Creation | 7/10 | 34 | 0 | ✅ Good |

**System Robustness Average**: 6.1/10

**Key Finding**: The system's *logic* is sound (6,748/6,757 tests pass, 99.87% pass rate), but its *data connectivity* is the critical weakness. S3→S6 data mapping is broken, and S1/S4 are incomplete implementations.

---

## Cross-Boundary Contract Status

| Contract | Description | Status |
|:---------|:-----------|:-------|
| XB-1 | QA→Export response consistency | ✅ PASS |
| XB-2 | Export→Web referential integrity | ✅ PASS |
| XB-3 | QA→Theory framework references | ⚠️ Not tested (requires live QA) |
| XB-4 | BN-Web sync (±0.01) | ❌ FAIL (0% data) |
| XB-5 | Extraction→Integration provenance | ✅ PASS |
| XB-6 | Enrichment→Template coherence | ✅ PASS |
| XB-7 | Warrant-Belief referential integrity | ✅ PASS |
| XB-8 | QA-Cache coherence | ✅ PASS |
| XB-9 | Service availability (13 services) | ⚠️ 11/13 available |
| XB-10 | Export completeness | ✅ PASS |
| XB-11 | Overseer coverage | ✅ PASS |
| XB-12 | QA-Export consistency | ✅ PASS |
