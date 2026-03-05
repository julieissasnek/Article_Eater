# ATLAS Subsystem Improvement Proposals & Sprint Plans

**Date**: 2026-03-05
**Author**: AG (Antigravity)
**Version**: 1.0

---

## Executive Summary

System average design quality: **6.9/10**. System robustness: **6.1/10**. Test pass rate: **99.87%**.

The system's *logic and architecture* are strong (S5/S7/S8 scored ≥8), but the *critical path bottleneck* is S3 (Antecedent/Consequent Tagging) which delivers 0% usable BN node mappings, cascading into a completely empty BN (S6). Two subsystems (S1, S4) have incomplete implementations.

### Priority Matrix

| Priority | Subsystem | Issue | Impact |
|:---------|:----------|:------|:-------|
| **P0** | S3 Tagging → S6 BN | 0% BN mapping | Entire BN integration blocked |
| **P1** | S2 Extraction Gate | Threshold drift | New extractions auto-quarantined |
| **P1** | S4 Image Pipeline | Stubs throughout | No real CV capability |
| **P1** | S1 Paper Acquisition | Missing API keys | No new paper intake |
| **P2** | S7 QA Search | Keyword-only | Misses nuanced queries |
| **P2** | S9 Card Generation | No circuit breaker | LLM failure cascades |
| **P3** | S5 WoB Coherence | O(n²) scaling | Future problem at 10K+ beliefs |
| **P3** | S8 Overseer | No chaos testing | Unverified resilience |

---

## Sprint 1: Critical Path — S3→S6 Data Mapping (P0)

**Goal**: Get ≥80% of beliefs mapped to BN nodes.
**Effort**: ~2 days
**Impact**: Unblocks entire BN integration subsystem (currently 1/10 score)

### 1.1 Fix Entity/Outcome Mapping Pipeline

**Root Cause**: Beliefs use DOI-based IDs (`10.1234/...`). BN nodes expect `(env_id, outcome_id)` pairs. The bridge (S3) does not consistently produce these canonical IDs.

#### Changes

- **[MODIFY] `src/services/belief_env_outcome_extractor.py`**: Add semantic similarity matching (not just keyword) using the extraction's `antecedent`/`consequent` fields to find closest taxonomy nodes. Fallback to LLM-based classification for unmatched terms.
- **[MODIFY] `src/services/iv_dv_classifier.py`**: Add confidence scoring for classifications; reject below 0.5 confidence.
- **[NEW] `scripts/backfill_bn_mapping.py`**: Batch script to re-process all 33K findings and populate `bn_node_id` on each belief.
- **[MODIFY] `src/services/incremental_bn.py`**: Add `populate_from_beliefs()` method that reads WoB beliefs with env/outcome IDs and creates BN edges.

#### Verification
- After backfill: `SELECT COUNT(*) FROM beliefs WHERE bn_node_id IS NOT NULL` ≥ 80% of total
- BN should have ≥50 edges after population
- XB-4 contract (BN-Web sync) should pass

### 1.2 Fix Extraction Gate Thresholds

**Root Cause**: Extraction field validator added v3 fields (theory_links, mechanism_chain) that the gate tests don't include in their test fixtures. "Passing" extraction gets score 0.7 instead of expected 0.8+.

#### Changes
- **[MODIFY] `tests/test_extraction_gate.py`**: Update test fixtures to include v3 required fields
- **[MODIFY] `src/qa/extraction_field_validator.py`**: Add v3 field weight calibration

#### Verification
- Gate tests pass: `python3 -m pytest tests/test_extraction_gate.py -v` → 14/14 pass

---

## Sprint 2: Infrastructure — S1 & S4 Implementation (P1)

**Goal**: Wire S1 API keys, replace S4 stubs with real implementations.
**Effort**: ~3 days
**Impact**: Enables paper acquisition and image classification

### 2.1 Paper Acquisition Configuration

#### Changes
- **[NEW] `.env.example`**: Document all required API keys
- **[MODIFY] `src/services/paper_fetcher.py`**: Add graceful degradation when individual APIs are unavailable (try CrossRef → PubMed → S2 in order)
- **[NEW] `scripts/acquisition_health_check.py`**: Script to test API connectivity
- **[MODIFY] `contracts/SUBSYSTEM_HEALTH_CONTRACTS.md`**: Update S1 status from RED → conditional on API config

#### Verification
- `python3 scripts/acquisition_health_check.py` reports ≥1 API available
- Acquire 10 papers via available API → verify staging output schema

### 2.2 Image Pipeline De-stubbing

#### Changes
- **[MODIFY] `src/services/image_pipeline_service.py`**: 
  - Replace `download_image()` stub with HTTP download (Unsplash/Flickr API)
  - Replace `_compute_perceptual_hash_stub()` with actual phash (imagehash library)
  - Replace `extract()` stub with PIL-based metadata extraction
- **[MODIFY] `src/services/image_pipeline_service.py`**: Add transfer learning classifier (CLIP or MobileNet)
- **[NEW] `tests/test_image_pipeline_live.py`**: Integration tests with real image downloads

#### Verification
- Download 5 test images → classify → verify 41-attribute tags
- Confidence calibration: histogram of confidence scores should be well-distributed

---

## Sprint 3: Quality & Search — S7 & S9 Hardening (P2)

**Goal**: Add semantic search to QA, add circuit breakers to card generation.
**Effort**: ~2 days

### 3.1 Hybrid Search for QA

#### Changes
- **[NEW] `src/services/vector_search.py`**: Sentence-transformer embedding + FAISS index over 33K findings
- **[MODIFY] `src/services/arbitrary_qa_handler.py`**: Add vector search as secondary retrieval path; merge results with keyword search
- **[NEW] `scripts/build_search_index.py`**: Build FAISS index from extraction corpus

#### Verification
- Query "What environmental factors affect stress recovery?" → verify semantic matches not findable by keyword
- Measure recall@10 improvement on 20 test queries

### 3.2 Card Generation Circuit Breaker

#### Changes
- **[MODIFY] `scripts/cc_restart_safe.py`**: Add circuit breaker pattern — after 3 consecutive LLM failures, pause batch for 60s before retry
- **[MODIFY] `src/qa/card_generation_orchestrator.py`**: Add timeout enforcement (5s per enrichment step, 30s total)
- **[MODIFY] `src/services/answer_enrichment_orchestrator.py`**: Enforce 5s total enrichment budget (currently can reach 18s)

#### Verification
- Simulate LLM failures → verify circuit breaker pauses correctly
- Measure enrichment latency → P95 ≤ 5s

---

## Sprint 4: Unified End-to-End Success Condition (P2-P3)

**Goal**: Create a single unified validation that proves the entire system works end-to-end.
**Effort**: ~1 day

### 4.1 E2E Success Condition Component

The system currently has 140+ per-subsystem invariants but no single "the whole thing works" test. This sprint creates one.

#### The Unified E2E Success Condition

```
ATLAS_E2E_SUCCESS := 
  ∃ paper P such that:
    1. P was acquired via S1 (paper_fetcher)
    2. P was extracted via S2 (claim_extractor) → ≥1 finding
    3. Each finding was tagged via S3 (env_id ≠ NULL ∧ outcome_id ≠ NULL)
    4. ≥1 finding was integrated into S5 (web_of_belief) as a belief
    5. ≥1 belief was mapped to S6 (BN edge exists)
    6. A query about P's topic returns ≥1 grounded answer via S7
    7. S8 (overseer) reports no RED invariant violations
    AND
    |timestamp(step 7) - timestamp(step 1)| ≤ 15 minutes
```

#### Changes
- **[NEW] `tests/test_e2e_atlas_pipeline.py`**: Full round-trip test
- **[NEW] `scripts/e2e_validation.py`**: On-demand E2E validation script
- **[MODIFY] `scripts/compute_system_health.py`**: Add E2E score as top-level AESHI component

#### Verification
- Run E2E with a known-good paper → all 7 steps pass
- Run with known-bad paper (empty PDF) → fails at step 2 with clear error

---

## Sprint Summary

| Sprint | Focus | Effort | Impact | Subsystems |
|:-------|:------|:-------|:-------|:-----------|
| **Sprint 1** | Critical path: BN mapping + gate fix | 2 days | P0 — Unblocks BN | S3, S6, S2 |
| **Sprint 2** | Infrastructure: APIs + CV | 3 days | P1 — Enables S1, S4 | S1, S4 |
| **Sprint 3** | Search + resilience | 2 days | P2 — Semantic QA, reliability | S7, S9 |
| **Sprint 4** | Unified E2E | 1 day | P2 — Proves system works | All |
| **Total** | | **8 days** | | |

---

## Post-Sprint Targets

After all 4 sprints:

| Metric | Current | Target |
|:-------|:--------|:-------|
| Design Quality Avg | 6.9/10 | 8.0/10 |
| Robustness Avg | 6.1/10 | 7.5/10 |
| BN Mapping | 0% | ≥80% |
| Image Pipeline | Stubs | Live CV |
| QA Search | Keyword | Hybrid (keyword + semantic) |
| E2E Test | None | Round-trip validated |
| RED Subsystems | 2 (S1, S6) | 0 |
| YELLOW Subsystems | 2 (S3, S4) | 1 (S4 transitioning) |
