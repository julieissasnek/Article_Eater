# Success Conditions — Full System Inventory

**Date**: 2026-03-03  
**Author**: AG (Antigravity)  
**Purpose**: Testable success conditions for every critical pipeline in the system.

---

## 1. Answer Enrichment Pipeline

| Condition | How to Verify | Status |
|:----------|:-------------|:-------|
| `EnrichedBelief.paper_ids` populated | Unit test | ✅ Done |
| Grounding gate crash → abstention | Unit test | ✅ Done |
| `get_master_web()` returns WebOfBelief not tuple | Unit test | ✅ Done |
| `EnrichedAnswer.status` reflects failures | Unit test | ✅ Done |
| Shell beliefs created when credence disabled | Unit test | ✅ Done |
| ImportError vs RuntimeError distinguished | Unit test | ✅ Done |

**Test file**: `tests/test_answer_enrichment_orchestrator.py` (50 pass, 1 skip)

---

## 2. Precomputed Answer Cards

| Condition | How to Verify | Status |
|:----------|:-------------|:-------|
| Card hit for known topic (noise→stress) | `test_card_hit_noise_stress` | ✅ Pass |
| Card miss for irrelevant query | `test_card_miss_irrelevant_query` | ✅ Pass |
| Retrieval < 100ms | `test_card_retrieval_speed` (actual: 39ms) | ✅ Pass |
| User type respected | `test_card_respects_user_type` | ✅ Pass |
| QA handler checks cards before routing | `test_qa_handler_serves_card` | ✅ Pass |
| Card response has required fields | `test_card_response_structure` | ✅ Pass |

**Test file**: `tests/test_card_retrieval.py` (9 pass, 2 skip)

---

## 3. PDF Ingestion Pipeline (`auto_ingest_pdfs.py`)

| Condition | How to Verify | Status |
|:----------|:-------------|:-------|
| New PDF detected in `pdfs_incoming/` | `detect_new_pdfs()` returns list | ⚠️ No test |
| Extraction produces JSON | `extract_pdf()` returns path | ⚠️ No test |
| QA gate rejects score < 0.5 | `qa_check()` returns float, threshold applied | ⚠️ No test |
| Integration adds beliefs to web | `integrate_to_web()` returns count > 0 | ⚠️ No test |
| Overseer notified after integration | `notify_overseer()` returns True | ⚠️ No test |
| IncrementalUpdater marks clusters STALE | `on_new_extraction()` called | ✅ Wired |
| Failed extraction → HITL DB record | `record_hitl_needed()` called | ⚠️ No test |
| Ingest log written to `acquisition/ingest_log.json` | Check file exists | ⚠️ No test |

---

## 4. Belief Clustering Pipeline (`src/qa/belief_clustering.py`)

| Condition | How to Verify | Status |
|:----------|:-------------|:-------|
| Findings loaded from `data/extractions/` | Cluster input count matches corpus | ❌ No test |
| Clusters produced with theme labels | `belief_clusters.json` has antecedent/consequent per cluster | ❌ No test |
| Minimum cluster size enforced (≥2 findings) | Check `size_distribution` in summary | ❌ No test |
| Cluster summary stats correct | `cluster_summary.json` n_clusters matches actual | ❌ No test |

---

## 5. Card Generator Pipeline (`src/qa/card_generator.py`)

| Condition | How to Verify | Status |
|:----------|:-------------|:-------|
| Cards generated per cluster × user_type | 6 user-type files in `answer_cards/` | ❌ No test |
| Card has required fields (prose, confidence, theories) | Schema validation | ❌ No test |
| `card_index.json` matches card files | Index keys ⊆ card cluster_ids | ❌ No test |
| Quality score computed per card | `quality_score` > 0 | ❌ No test |

---

## 6. Materialized View Builder (`src/qa/mv_builder.py`)

| Condition | How to Verify | Status |
|:----------|:-------------|:-------|
| STALE views rebuilt on incremental run | `build_all(incremental=True)` only rebuilds affected | ✅ Has test |
| Output written to `data/materialized_views/` | Files exist after build | ✅ Has test |

**Test file**: `tests/test_mv_builder.py`

---

## 7. Evidence Integration (`src/services/evidence_integration.py`)

| Condition | How to Verify | Status |
|:----------|:-------------|:-------|
| Findings merged into web beliefs | Count beliefs before/after | ❌ No test |
| Duplicate findings deduplicated | Same DOI+finding → no duplicate belief | ❌ No test |
| Source provenance preserved (DOI, title) | Integrated belief has source field | ❌ No test |

---

## 8. Extraction to Web (`src/services/extraction_to_web.py`)

| Condition | How to Verify | Status |
|:----------|:-------------|:-------|
| Extraction JSON → beliefs in web | `integrate_extraction()` adds beliefs | ❌ No test |
| Theory links preserved | Integrated belief has theory_links | ❌ No test |
| Mechanism chain preserved | Integrated belief has mechanism | ❌ No test |

---

## 9. Grounding Gate (`src/qa/grounding_gate.py`)

| Condition | How to Verify | Status |
|:----------|:-------------|:-------|
| Query with evidence → pass | `check()` returns `should_abstain=False` | ✅ Has test |
| Query without evidence → abstain | `check()` returns `should_abstain=True` | ✅ Has test |
| Coherence status computed | Result has `coherence_status` field | ✅ Has test |

**Test file**: `tests/test_grounding_gate.py`

---

## 10. Overseer (`src/services/overseer.py`)

| Condition | How to Verify | Status |
|:----------|:-------------|:-------|
| `check_invariants()` runs all 9 invariants | Returns report with 9 entries | ✅ Has test |
| `health_check()` reports actual service status | Not always 9/9 when services fail | ⚠️ Audit flagged |
| `post_integration_check()` detects violations | Returns violations list | ✅ Has test |

**Test file**: `tests/test_overseer_inv4.py` + others

---

## 11. BBN Calibrator (`src/services/bbn_calibrator.py`)

| Condition | How to Verify | Status |
|:----------|:-------------|:-------|
| Bayesian network calibrated from evidence | Posterior probabilities computed | ❌ No test |
| Calibration respects evidence weight | Stronger evidence → higher posterior | ❌ No test |

---

## 12. Epistemic Orchestrator (`src/services/epistemic_orchestrator.py`)

| Condition | How to Verify | Status |
|:----------|:-------------|:-------|
| Orchestrates multi-step epistemic queries | End-to-end query returns structured response | ❌ No test |

---

## 13. Argumentation Graph (`src/services/argumentation_graph.py`)

| Condition | How to Verify | Status |
|:----------|:-------------|:-------|
| Argument attacks detected | `compute_attacks()` returns attack list | ❌ No test |
| Argument hierarchy built | Graph has nodes and edges | ❌ No test |

---

## 14. Integrated Query Service (`src/services/integrated_query_service.py`)

| Condition | How to Verify | Status |
|:----------|:-------------|:-------|
| Web of belief loaded (unpacked from tuple) | `self.web` is WebOfBelief | ✅ Fixed (P0 #3) |
| Template embeddings computed for semantic search | Embedding cache populated | ❌ No test |
| Query routes to appropriate handler | Classification → correct handler | ❌ No test |

---

## 15. Incremental Updater (`src/qa/incremental_updater.py`)

| Condition | How to Verify | Status |
|:----------|:-------------|:-------|
| New extraction → affected clusters identified | `on_new_extraction()` returns cluster list | ❌ No test |
| Affected clusters marked in `_pending_updates.json` | File contains stale cluster IDs | ❌ No test |
| `clear_pending()` removes pending file | File deleted after clear | ❌ No test |

---

## 16. Gap Predictor (`src/services/gap_predictor.py`)

| Condition | How to Verify | Status |
|:----------|:-------------|:-------|
| Gaps predicted from corpus | `predict_gaps()` returns gap list | ✅ Has test |
| Findings directory correctly referenced | Searches `data/extractions/` not wrong path | ⚠️ Audit flagged path mismatch |
| VOI scores computed (not hardcoded 0.5) | Scores vary by gap importance | ⚠️ Audit flagged |

**Test file**: `tests/test_gap_predictor.py`

---

## 17. Knowledge Catalog (`src/services/knowledge_catalog.py`)

| Condition | How to Verify | Status |
|:----------|:-------------|:-------|
| Theories loaded from canonical JSON | `get_theories()` returns non-empty list | ❌ No test |
| Molecules loaded | `get_molecules()` returns 18 molecules | ❌ No test |
| Cultural differences loaded | `get_cultural_differences()` returns list | ❌ No test |

---

## 18. Precompute Pipeline (`src/qa/precompute_pipeline.py`)

| Condition | How to Verify | Status |
|:----------|:-------------|:-------|
| Molecules loaded from `data/molecules/` | `_load_molecules()` returns non-empty dict | ❌ No test |
| STALE molecules re-computed | `compute_all()` only processes stale | ❌ No test |
| L1/L2/L3 summaries saved to cache | Cache entries created with FRESH status | ❌ No test |

---
---

# Part II: Subsystem-Level Success Conditions

## Source: V9 Audit (17 System-Level Subsystems)

These are the 17 major subsystems identified by the 18-expert V9 panel.

> [!NOTE]
> These subsystems should also appear in the Master Document. **TODO if they aren't there yet**: ensure the master doc has a section defining each subsystem's boundary, constituent modules, and acceptance criteria.

| # | Subsystem | V9 Score | Success Condition | Status |
|:--|:----------|:---------|:------------------|:-------|
| 1 | **QA & Query** (9 files, 10K LOC) | ⚠️ | 14+ question types classified and answered; precomputed cards served <100ms; evidence queries include DOI provenance | ✅ Mostly met (cards wired today) |
| 2 | **Export & Reporting** (7 files, 7K LOC) | ✅ | Export produces valid JSON/BibTeX/checklist; report_generator renders without crash | ⚠️ No integration test |
| 3 | **Web of Belief** (5 files, 7K LOC) | ✅ | 4,888+ beliefs stored; coherence methods callable; `get_master_web()` returns WebOfBelief not tuple | ✅ Tuple fixed (P0 #3) |
| 4 | **Paper Acquisition** (5 files, 6K LOC) | ❌ | DOI→PDF download succeeds; HITL queue tracks failures; acquisition report generated | ❌ API keys missing |
| 5 | **Theory & Templates** (6 files, 5.5K LOC) | ✅ | Template registry loads all templates; theory agents produce profiles | ⚠️ Agents not consuming T3 data |
| 6 | **DB & Infrastructure** (6 files, 6K LOC) | ⚠️ | `db_locator` resolves all paths; no dual-DB conflicts; migrations run cleanly | ⚠️ Dual-DB persists |
| 7 | **Bayesian Network** (4 files, 5K LOC) | ⚠️ | `bn_touched` > 50%; BN calibrated from evidence; posteriors change on new beliefs | ❌ **0% mapped** |
| 8 | **Extraction & Integration** (5 files, 5K LOC) | ⚠️ | New PDFs extracted → beliefs in DB; paper_ids preserved; IncrementalUpdater marks STALE | ✅ Updater wired today |
| 9 | **Overseer & Self-Monitoring** (5 files, 5K LOC) | ✅ | 18 reflexes active; `check_invariants()` runs all 9 INVs; `health_check()` reflects actual service state | ⚠️ health_check always 9/9 |
| 10 | **Interpretation Space** (4 files, 5K LOC) | ✅ | Phase 3 complete; R₁-R₄ closure operators produce output | ❌ R₁-R₄ unimplemented |
| 11 | **Warrant & Credence** (4 files, 3K LOC) | ✅ | Credence CI computed; warrant trace decomposition covers 8+ study types; 62/62 tests pass | ✅ Tests pass |
| 12 | **T3 Belief Engine** (6 files, 3K LOC) | ✅ | 519+ established beliefs; classification rate ≥70%; field reviewer terminal rate ≤10% | ✅ 138 tests pass |
| 13 | **Image Pipeline** (6 files, 3K LOC) | ⚠️ | Image attributes synced; environment_image_db populated; image tags generated | ⚠️ Partial impl |
| 14 | **Taxonomy & Vocabulary** (4 files, 3K LOC) | ✅ | 133 taxonomy nodes; luminous/acoustic/thermal/natural domains correct per standards | ✅ Tests pass |
| 15 | **CVA** (8 files, 3K LOC) | ✅ | CVA constraint engine runs; beauty evaluation produces scores; attractor dynamics computed | ✅ Functional |
| 16 | **Argumentation** (2 files, 2K LOC) | ✅ | ArgumentationEngine facade imports; vulnerability report generated; tensions detected | ⚠️ No integration test |
| 17 | **Annotation** (2 files, 1K LOC) | ✅ | 441+ annotations; annotation service creates/queries annotations | ✅ Tests pass |

**Verdict**: 10/17 ✅, 5/17 ⚠️, 2/17 ❌

---

## Source: V13 Full Audit (10 Enrichment Subsystems)

These are the enrichment pipeline subsystems scored in the V13 full audit. They live inside the answer enrichment orchestrator.

| # | Subsystem | V13 Score | Success Condition | Status |
|:--|:----------|:---------|:------------------|:-------|
| E1 | **Orchestration & Budget** | 7/10 | 9-step pipeline completes; per-step timeout enforced; degradation alert on budget exhaustion | ⚠️ No per-step timeout |
| E2 | **Grounding Gate** | 8/10 | Gate crash → abstention not proceed; corpus search validates evidence exists | ✅ Fixed (P0 #2) |
| E3 | **Credence Enrichment** | 3/10 | CI computation runs; `warrant_strength` module available; paper_ids preserved | ✅ paper_ids fixed; ⚠️ CI still fragile |
| E4 | **Warrant Trace** | 2/10 | DesignType enum matches module schema; warrant decomposition succeeds | ❌ Schema mismatch reported |
| E5 | **Framework Voices** | 2/10 | Voices are topic-aware (reference query content); not hardcoded templates | ❌ **BROKEN** |
| E6 | **Language Adaptation** | 1/10 | `adapt_content()` returns rewritten prose, not metadata dict | ❌ **BROKEN** |
| E7 | **Gap Analysis** | 4/10 | `GapPredictor` reads correct directory (`data/extractions/`); VOI scores vary | ⚠️ Path mismatch flagged |
| E8 | **Follow-Ups** | 3/10 | Recommendations generated without cascading failures; fallback doesn't crash | ⚠️ Fragile |
| E9 | **Figure Suggestions** | 2/10 | Non-empty suggestion list returned; or explicitly disabled | ❌ Returns empty lists |
| E10 | **Data Integrity** | 5/10 | paper_ids preserved through pipeline; `EnrichedAnswer.status` reflects failures | ✅ Fixed (P0 #1, #4) |

---

## Source: Panel Feb 25 (7 Epistemological Subsystems)

These address the philosophical architecture of belief management:

| # | Subsystem | Panel Verdict | Status |
|:--|:----------|:-------------|:-------|
| A | **Credence Computation** | Wire immediately (critical gap) | ⚠️ Partial (CI works, Source Quality not fed in) |
| B | **Provenance & Foundherentism** | Synchronous computation in Step 5 | ⚠️ Partial (tracer exists, CrosswordPosition untested) |
| C | **BN Coupling** | Hierarchical one-directional (web → BN) | ❌ 0% mapped |
| D | **QA Cache Recomputation** | Batched nightly | ✅ `qa_cache_manager` wired |
| E | **Coherence Computation & Alerting** | Per-theory tracking with baselines | ⚠️ Computed but not alerted |
| F | **Social Epistemology & Community** | Surface contestation explicitly | ❌ Placeholder |
| G | **VOI Gap Closure** | Expert panel to define high-VOI questions | ⚠️ Infra exists, not closed loop |

---

## Source: QA_SYSTEM_SPEC.md (22 Formal Success Conditions)

See [QA_SYSTEM_SPEC.md](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/docs/QA_SYSTEM_SPEC.md) §8 for full definitions. Status summary:

| Tier | SC Range | Description | Done | Not Done |
|:-----|:---------|:-----------|:-----|:---------|
| 1 — Hygiene | SC-QA-01 to 04 | Reflexes run, report to overseer | ✅ 4/4 | — |
| 2 — Epistemic | SC-QA-05 to 09 | Warrant, INV-1, Source Quality, DEFEATED, COHERENT | 2/5 | SC-05,06,07 |
| 3 — Integration | SC-QA-10 to 14 | Rollback→QA, annotations→gaps, SENSITIVITY, provenance→AESHI, UI | 2/5 | SC-12,13,14 |
| 4 — Discovery | SC-QA-15 to 19 | Nightly gap pred, VOI, defeater search, annotation harvest | 4/5 | SC-16 partial |
| 5 — Principles | SC-QA-20 to 22 | Principles doc, independence, commitment | 2/3 | SC-20 |
| **Total** | | | **14/22** | **8 remaining** |

---

## Source: Annotation Plan (12 Formal Success Conditions)

See [AG_QA_ANNOTATION_IMPLEMENTATION_PLAN_2026-03-01.md](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/docs/AG_QA_ANNOTATION_IMPLEMENTATION_PLAN_2026-03-01.md) for full definitions:

| ID | Condition | Status |
|:---|:----------|:-------|
| AN-SC-01 | Single query API returns all annotation types | ❌ |
| AN-SC-02 | All 3 layers persist to same backing store | ❌ |
| AN-SC-03 | A9-A18 data models have persistence service | ❌ |
| AN-SC-04 | Annotation count > 0 for >50% of beliefs | ❌ |
| AN-SC-05 | SENSITIVITY_FLAG consumed by template QA | ❌ |
| AN-SC-06 | OPEN_QUESTION consumed by gap predictor | ✅ |
| AN-SC-07 | SEARCH_PROMPT consumed by VOI search | ❌ |
| AN-SC-08 | Annotations influence belief entrenchment | ❌ |
| AN-SC-09 | Annotation health → AESHI component | ❌ |
| AN-SC-10 | Auto-annotation runs on all extractions | ⚠️ CVA only |
| AN-SC-11 | Annotation supersession works end-to-end | ✅ L1 only |
| AN-SC-12 | Full-text search across annotations | ✅ L1 only |
| **Total** | | **3/12 done** |

---
---

# Part III: Summary

## Full Inventory

| Source | Subsystems | Success Conditions | Met |
|:-------|:----------|:------------------|:----|
| V9 Audit (17 system) | 17 | ~17 | 10/17 |
| V13 Audit (10 enrichment) | 10 | ~10 | 3/10 |
| Panel Feb 25 (7 epistemological) | 7 | ~7 | 1/7 |
| QA_SYSTEM_SPEC.md (formal) | 9 subsystems | 22 SCs | 14/22 |
| Annotation Plan (formal) | 3 layers | 12 SCs | 3/12 |
| **Pipeline-level (Part I)** | 18 pipelines | ~60 conditions | 13 tested |
| **Grand Total** | **~45 subsystems** | **~128 conditions** | **~44 met** |

> [!IMPORTANT]
> The Master Document currently has **NO engineering subsystem inventory section**. See `docs/SUBSYSTEM_INVENTORY_FOR_MASTER_DOC_2026-03-03.md` for the canonical inventory that CW should add.

### Running All Existing Tests

```bash
# P0 audit fix tests
python3 -m pytest tests/test_answer_enrichment_orchestrator.py -v

# Card retrieval tests
python3 -m pytest tests/test_card_retrieval.py -v

# All tests
python3 -m pytest tests/ -v --tb=short
```

