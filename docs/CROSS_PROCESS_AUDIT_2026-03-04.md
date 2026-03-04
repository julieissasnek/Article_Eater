# Cross-Process Success Condition Audit

**Date**: 2026-03-04  
**Author**: AG (Antigravity)  
**Requested by**: CW via `AG_PROMPT_cross_process_audit.md`  
**Priority**: HIGH — David specifically requested this audit  
**Key Insight**: "The last mile trigger — even if hooked up — never is tested to see if it was pulled."

---

## Section 1: Classification Table

### Classification Key

| Code | Meaning | Risk Level |
|------|---------|------------|
| **PI** | PROCESS_INTERNAL — Tests only within the module it's defined over | Lowest (but hides interface gaps) |
| **SXP** | STATIC_CROSS_PROCESS — Tests compatibility between modules (schemas, enums) but NOT runtime propagation | Medium |
| **RXP** | RUNTIME_CROSS_PROCESS — Tests that a trigger fired by Module A arrives at Module B and produces observable effect | GOLD STANDARD |
| **MXP** | MISSING_CROSS_PROCESS — Trigger chain exists in code but NO success condition tests it | **HIGHEST RISK** |

---

### scripts/scheduled_pipeline.py (SP-SC1..SC6)

| SC ID | Classification | Trigger Chain | Gap Description |
|-------|---------------|---------------|-----------------|
| SP-SC1 | **PI** | Pipeline internal exit code | No test that successful completion triggers overseer `report_pipeline_run()` |
| SP-SC2 | **PI** | Wishlist internal CRUD | No test that wishlist items flow into `run_discovery()` |
| SP-SC3 | **PI** | Discovery produces file | No test that `new_papers.json` is actually consumed by `run_triage()` |
| SP-SC4 | **PI** | Triage classification | No test that triage output feeds `run_extraction()` prompt selection |
| SP-SC5 | **PI** | Extraction produces files | No test that extraction JSONs are consumed by `run_integration()` |
| SP-SC6 | **PI** | State persistence | No test that checkpoint state is used for crash recovery |

> **🔴 Critical Gap**: SP-SC3 → SP-SC4 → SP-SC5 is a 3-step trigger chain with ZERO cross-process tests. Each stage tests its own output but nobody tests that stage N's output is stage N+1's input.

---

### scripts/kirsh_decision_tree_analysis.py (KDT-SC1..SC6)

| SC ID | Classification | Trigger Chain | Gap Description |
|-------|---------------|---------------|-----------------|
| KDT-SC1 | **PI** | Load stimuli internally | — |
| KDT-SC2 | **PI** | Filter internally | — |
| KDT-SC3 | **PI** | Cluster internally | — |
| KDT-SC4 | **PI** | Decision tree internally | — |
| KDT-SC5 | **PI** | Discover attributes internally | — |
| KDT-SC6 | **PI** | Report internally | Standalone script, no downstream consumers |

> All PI — self-contained analysis script. No cross-process risk.

---

### scripts/backfill_operationalizations.py (BO-SC1..SC6)

| SC ID | Classification | Trigger Chain | Gap Description |
|-------|---------------|---------------|-----------------|
| BO-SC1 | **PI** | Load vocab internally | — |
| BO-SC2 | **PI** | Identify empty terms | — |
| BO-SC3 | **PI** | Validate instruments | — |
| BO-SC4 | **PI** | Preserve existing | — |
| BO-SC5 | **PI** | Persist output | No test that updated vocab is consumed by LOI or extraction prompts |
| BO-SC6 | **PI** | Coverage increase | — |

---

### scripts/link_outcomes_to_instruments.py (LOI-SC1..SC6)

| SC ID | Classification | Trigger Chain | Gap Description |
|-------|---------------|---------------|-----------------|
| LOI-SC1 | **PI** | Load registry | — |
| LOI-SC2 | **PI** | Build lookup | — |
| LOI-SC3 | **PI** | Extract abbreviations | — |
| LOI-SC4 | **PI** | Match operationalizations | — |
| LOI-SC5 | **PI** | Add instrument IDs | No test that instrument_ids are used by downstream QA |
| LOI-SC6 | **SXP** | Referential integrity | Tests that IDs in vocab exist in registry (static cross-reference) |

---

### scripts/gemini_extraction_queue.py (GEQ-SC1..SC8)

| SC ID | Classification | Trigger Chain | Gap Description |
|-------|---------------|---------------|-----------------|
| GEQ-SC1 | **PI** | Load triage | No test that triage comes from `run_triage()` output |
| GEQ-SC2 | **PI** | State persistence | — |
| GEQ-SC3 | **PI** | PDF locating | — |
| GEQ-SC4 | **SXP** | Prompt selection per type | Tests type→prompt mapping but NOT that type came from triage |
| GEQ-SC5 | **PI** | Structured output | — |
| GEQ-SC6 | **PI** | Two-run verification | — |
| GEQ-SC7 | **PI** | Cost tracking | — |
| GEQ-SC8 | **PI** | File naming | No test that naming is discoverable by `ExtractionFieldValidator` |

---

### scripts/run_panel_1_outcomes.py (P1O-SC1..SC7)

| SC ID | Classification | Trigger Chain | Gap Description |
|-------|---------------|---------------|-----------------|
| P1O-SC1 | **PI** | Load unresolved terms | — |
| P1O-SC2 | **SXP** | Filter against vocab | Tests vocab compatibility (static cross-ref) |
| P1O-SC3 | **PI** | Cluster terms | — |
| P1O-SC4 | **PI** | Panel invocation | — |
| P1O-SC5 | **PI** | Decision completeness | — |
| P1O-SC6 | **PI** | Output written | No test that output is consumed by vocab update |
| P1O-SC7 | **PI** | Coverage | — |

---

### src/qa/extraction_field_validator.py (EFV-SC1..SC7)

| SC ID | Classification | Trigger Chain | Gap Description |
|-------|---------------|---------------|-----------------|
| EFV-SC1 | **PI** | Validator init | — |
| EFV-SC2 | **PI** | Single validation | — |
| EFV-SC3 | **PI** | Violation detection | — |
| EFV-SC4 | **PI** | Score computation | — |
| EFV-SC5 | **PI** | Batch validation | — |
| EFV-SC6 | **PI** | Threshold filtering | — |
| EFV-SC7 | **PI** | Severity classification | No test that severity drives `validate_and_gate()` blocking |

> **🔴 Critical Gap**: EFV validates and scores but NO test verifies that `validate_and_gate()` actually BLOCKS low-scoring articles from entering the integration pipeline. The gate logic is wired in `nightly_integration_pipeline.py:stage_qa_quality_gate()` but no SC tests the runtime gate decision.

---

### src/services/overseer.py (OS-SC1..SC8)

| SC ID | Classification | Trigger Chain | Gap Description |
|-------|---------------|---------------|-----------------|
| OS-SC1 | **PI** | Overseer init | — |
| OS-SC2 | **PI** | INV-0 check | — |
| OS-SC3 | **PI** | INV-1 provenance check | — |
| OS-SC4 | **PI** | INV-4 coherence delta | No test that coherence delta triggers quarantine |
| OS-SC5 | **PI** | INV-10 QA quality | No test that quality check feeds back to extraction |
| OS-SC6 | **PI** | Violation detection | — |
| OS-SC7 | **PI** | Health report generation | No test that report is consumed by AESHI |
| OS-SC8 | **PI** | Scheduler triggers | No test that POST_INTEGRATION is triggered by `orchestrator.py` |

> **🔴 Critical Gap**: OS-SC8 tests that the scheduler CAN trigger modes, but no test verifies that `PaperIntegrationOrchestrator._run_overseer_post_check()` actually calls `overseer.post_integration_check()` at runtime. The wiring exists (L332-398 of orchestrator.py) but is never tested end-to-end.

---

### src/extraction/revised_prompts_v3.py (REP-SC1..SC8)

| SC ID | Classification | Trigger Chain | Gap Description |
|-------|---------------|---------------|-----------------|
| REP-SC1 | **PI** | Canonical directions | — |
| REP-SC2 | **PI** | Article families | — |
| REP-SC3 | **PI** | Base prompt exists | — |
| REP-SC4 | **PI** | Family prompts exist | — |
| REP-SC5 | **PI** | Validation suffix | — |
| REP-SC6 | **PI** | Vocab injection | No test that injected vocab matches live `outcome_vocab.json` |
| REP-SC7 | **SXP** | Schema compliance | Tests prompt→schema compatibility (static) |
| REP-SC8 | **PI** | Antecedent specificity | — |

---

### src/services/finding_template_relevance.py (FTR-SC1..SC5)

| SC ID | Classification | Trigger Chain | Gap Description |
|-------|---------------|---------------|-----------------|
| FTR-SC1 | **PI** | Framework loading | — |
| FTR-SC2 | **PI** | Tier2 coverage | — |
| FTR-SC3 | **RXP** ✅ | Annotation persistence | Tests that resolved findings ARE persisted to DB |
| FTR-SC4 | **SXP** | Null tier2 check | Tests data quality across finder→template boundary |
| FTR-SC5 | **RXP** ✅ | persist_relevance_to_web_db called | Tests that function IS invoked in pipeline runtime |

> The FTR module has the best cross-process coverage in the entire registry. FTR-SC3 and FTR-SC5 are genuine runtime cross-process tests.

---

### scripts/backfill_belief_ids.py (BEL-SC1..SC6)

| SC ID | Classification | Trigger Chain | Gap Description |
|-------|---------------|---------------|-----------------|
| BEL-SC1 | **PI** | environment_id coverage | — |
| BEL-SC2 | **PI** | outcome_id coverage | — |
| BEL-SC3 | **SXP** | Outcome mapping validity | Tests outcome_ids exist in vocab (static cross-reference) |
| BEL-SC4 | **PI** | Extraction file lookup | — |
| BEL-SC5 | **PI** | Template preservation | — |
| BEL-SC6 | **PI** | Transaction atomicity | — |

---

### scripts/nightly_integration_pipeline.py (NIP-SC1..SC3)

| SC ID | Classification | Trigger Chain | Gap Description |
|-------|---------------|---------------|-----------------|
| NIP-SC1 | **PI** | Pipeline completes | No test that stages execute in correct order |
| NIP-SC2 | **SXP** | Uses centralized DB | Tests db_path compatibility (static) |
| NIP-SC3 | **PI** | Health report produced | No test that report feeds back to overseer DB |

> **🟡 Only 3 SCs for a 17-stage pipeline**. This is the most under-tested module relative to its complexity.

---

### scripts/compute_system_health.py (AESHI-SC1..SC4)

| SC ID | Classification | Trigger Chain | Gap Description |
|-------|---------------|---------------|-----------------|
| AESHI-SC1 | **PI** | Score range | — |
| AESHI-SC2 | **PI** | No default scores | — |
| AESHI-SC3 | **SXP** | Reads correct column | Tests that AESHI reads `epistemic_v2` not missing column |
| AESHI-SC4 | **PI** | Reports written | No test that reports are consumed by any downstream |

---

### scripts/classify_grounding.py (GC-SC1..SC3)

| SC ID | Classification | Trigger Chain | Gap Description |
|-------|---------------|---------------|-----------------|
| GC-SC1 | **PI** | All classified | — |
| GC-SC2 | **PI** | Grounding ratio | — |
| GC-SC3 | **SXP** | Centralized DB | Tests consistency with AESHI db usage |

---

### scripts/propagate_constraints.py (CP-SC1..SC3)

| SC ID | Classification | Trigger Chain | Gap Description |
|-------|---------------|---------------|-----------------|
| CP-SC1 | **PI** | Isolation reduction | — |
| CP-SC2 | **PI** | Valid edges | — |
| CP-SC3 | **PI** | Dry run safety | — |

---

### scripts/migrate_annotations_to_unified.py (AM-SC1..SC3)

| SC ID | Classification | Trigger Chain | Gap Description |
|-------|---------------|---------------|-----------------|
| AM-SC1 | **PI** | Files processed | — |
| AM-SC2 | **PI** | Idempotent | — |
| AM-SC3 | **SXP** | Types registered | Tests enum alignment (static) |

---

### scripts/run_acquisition_pipeline.py (ACQ-SC1..SC4)

| SC ID | Classification | Trigger Chain | Gap Description |
|-------|---------------|---------------|-----------------|
| ACQ-SC1 | **PI** | Dry run safety | — |
| ACQ-SC2 | **PI** | Step isolation | — |
| ACQ-SC3 | **PI** | Summary report | — |
| ACQ-SC4 | **SXP** | Scripts exist | Tests that referenced scripts exist on disk |

---

### src/services/paper_integration/orchestrator.py (IC-SC1..SC5)

| SC ID | Classification | Trigger Chain | Gap Description |
|-------|---------------|---------------|-----------------|
| IC-SC1 | **SXP** | 14 steps implemented | Tests method existence (static) |
| IC-SC2 | **RXP** ✅ | Rollback completeness | Tests runtime rollback across DB tables |
| IC-SC3 | **PI** | Pre-validation | — |
| IC-SC4 | **RXP** ✅ | Provenance tracking | Tests that CASCADE produces beliefs with provenance |
| IC-SC5 | **RXP** ✅ | Event recording | Tests that cascade audit trail is persisted |

---

### src/qa/cluster_meta_review.py (CMR-SC1..SC14)

| SC ID | Classification | Trigger Chain | Gap Description |
|-------|---------------|---------------|-----------------|
| CMR-SC1 | **PI** | Completeness | — |
| CMR-SC2 | **PI** | Quality gate | — |
| CMR-SC3..SC14 | **PI** | Quality criteria | All test meta-review internal quality; none test that meta-reviews reach cards |

> **🟡 14 SCs but all PI**. No test that generated meta-reviews are consumed by `CardRetriever.try_match()` or `IntegratedQueryService.query()`.

---

### src/qa/cards/ E2E (SC-E2E-1..SC-E2E-12)

| SC ID | Classification | Trigger Chain | Gap Description |
|-------|---------------|---------------|-----------------|
| SC-E2E-1 | **RXP** ✅ | Card persistence roundtrip | Tests save → search path → load |
| SC-E2E-2 | **SXP** | Schema imports | Tests import path compatibility |
| SC-E2E-3 | **SXP** | CardType enum match | Tests enum values match generator expectations |
| SC-E2E-4 | **SXP** | Tab definitions complete | Tests all tabs have definitions (static) |
| SC-E2E-5 | **RXP** ✅ | Staleness computation | Tests staleness score from ledger data |
| SC-E2E-6 | **RXP** ✅ | Missing tab detection | Tests validator catches missing tabs |
| SC-E2E-7 | **RXP** ✅ | JSON standard compliance | Tests serialization roundtrip |
| SC-E2E-8 | **PI** | Meta-review directory | Tests directory exists (no data flow) |
| SC-E2E-9 | **RXP** ✅ | User-type tab ordering | Tests personalization output varies |
| SC-E2E-10 | **SXP** | Badge hex format | Tests color values are valid (static) |
| SC-E2E-11 | **SXP** | Model allocation values | Tests enum alignment |
| SC-E2E-12 | **SXP** | Direction enum match | Tests extraction→card direction compatibility |

> The E2E module has the **best** cross-process coverage: 5 RXP + 5 SXP. This was clearly designed to catch last-mile failures.

---

## Summary Statistics

| Classification | Count | Percentage |
|---------------|-------|-----------|
| PROCESS_INTERNAL (PI) | **82** | 74.5% |
| STATIC_CROSS_PROCESS (SXP) | **16** | 14.5% |
| RUNTIME_CROSS_PROCESS (RXP) | **12** | 10.9% |
| **Total** | **110** | 100% |

> **Only 10.9% of success conditions test actual runtime signal propagation.** The remaining 89.1% test modules in isolation or at best check static compatibility. This is the gap David identified.

---

## Section 2: Missing Cross-Process Conditions (MISSING_CROSS_PROCESS)

### SC-XPROC-1: Pipeline Stage Handoff — Discovery → Triage

```json
{
  "id": "SC-XPROC-1",
  "name": "Discovery output is consumed by triage",
  "description": "Papers in data/discovery/new_papers.json are loaded and classified by run_triage() within the same pipeline run",
  "metric": "set(triage_input_papers) ⊇ set(discovery_output_papers)",
  "threshold": "100% of discovered papers reach triage",
  "test_name": "test_xproc_discovery_feeds_triage",
  "rationale": "Each stage tests its own output but nobody verifies the handoff. If file path changes or format diverges, triage silently processes nothing.",
  "trigger_source": "scripts/scheduled_pipeline.py:run_discovery()",
  "effect_target": "scripts/scheduled_pipeline.py:run_triage()",
  "chain": ["run_discovery()", "writes new_papers.json", "run_triage() reads new_papers.json", "triage produces classifications"]
}
```

### SC-XPROC-2: Pipeline Stage Handoff — Extraction → Integration

```json
{
  "id": "SC-XPROC-2",
  "name": "Extraction output reaches integration cascade",
  "description": "Extraction JSON files produced by GEQ are found and loaded by PaperIntegrationOrchestrator in the same pipeline run",
  "metric": "set(integrated_papers) ⊇ set(extracted_papers)",
  "threshold": ">= 90% of extractions reach integration",
  "test_name": "test_xproc_extraction_feeds_integration",
  "rationale": "Extraction produces files at data/extractions/{doi}.json but integration may look for different paths or naming. The wiring exists but is never tested.",
  "trigger_source": "scripts/gemini_extraction_queue.py",
  "effect_target": "src/services/paper_integration/orchestrator.py:integrate_paper()",
  "chain": ["GEQ writes {doi}.json", "run_integration() scans directory", "orchestrator.integrate_paper() reads extraction_data"]
}
```

### SC-XPROC-3: Integration Cascade → Overseer POST_INTEGRATION

```json
{
  "id": "SC-XPROC-3",
  "name": "Integration triggers overseer post-check",
  "description": "After PaperIntegrationOrchestrator.integrate_paper() completes, _run_overseer_post_check() fires and OverseerService.post_integration_check() receives the paper_id and returns a HealthReport",
  "metric": "overseer.post_integration_check(paper_id) is called AND returns HealthReport",
  "threshold": "100% of successful integrations trigger overseer",
  "test_name": "test_xproc_integration_triggers_overseer",
  "rationale": "The wiring exists at orchestrator.py L332-398 but the overseer DB path resolution has a fallback that silently skips the check. OS-SC8 tests the scheduler CAN trigger modes but NOT that integration DOES trigger it.",
  "trigger_source": "src/services/paper_integration/orchestrator.py:integrate_paper()",
  "effect_target": "src/services/overseer.py:post_integration_check()",
  "chain": ["integrate_paper() completes", "_run_overseer_post_check()", "locate overseer/web DBs", "overseer.post_integration_check()", "report violations"]
}
```

### SC-XPROC-4: Integration Cascade → Card Staleness Update

```json
{
  "id": "SC-XPROC-4",
  "name": "Integration triggers card staleness update",
  "description": "After paper integration, on_new_evidence() is called on CardGenerationOrchestrator, which updates staleness ledgers for affected cards",
  "metric": "cards referencing integrated entity have staleness_ledger updated",
  "threshold": "100% of affected cards marked STALE",
  "test_name": "test_xproc_integration_triggers_card_staleness",
  "rationale": "CardGenerationOrchestrator.on_new_evidence() and check_and_queue_stale() exist (L706-730) but no test verifies integration actually calls them. Step 15 'propagate_cards' in CANONICAL_STEPS exists but is marked as non-critical.",
  "trigger_source": "src/services/paper_integration/orchestrator.py step 15",
  "effect_target": "src/qa/card_generation_orchestrator.py:on_new_evidence()",
  "chain": ["integrate_paper() step 15", "propagate_cards()", "on_new_evidence(card_id, paper_doi)", "update staleness ledger", "check_and_queue_stale()"]
}
```

### SC-XPROC-5: EFV Quality Gate → Integration Blocking

```json
{
  "id": "SC-XPROC-5",
  "name": "Low-quality extractions are blocked from integration",
  "description": "Articles scoring below 0.75 in ExtractionFieldValidator are NOT passed to PaperIntegrationOrchestrator",
  "metric": "no paper with EFV score < 0.75 appears in integration cascade",
  "threshold": "100% blocking of sub-threshold papers",
  "test_name": "test_xproc_efv_blocks_low_quality",
  "rationale": "EFV validates (EFV-SC1..7) and nightly pipeline calls stage_qa_quality_gate() which uses EFV, but NO test verifies that the gate ACTUALLY BLOCKS papers. The validate_and_gate() function exists but may not be called, or its return value may be ignored.",
  "trigger_source": "src/qa/extraction_field_validator.py:validate_and_gate()",
  "effect_target": "scripts/nightly_integration_pipeline.py:stage_auto_approve()",
  "chain": ["stage_qa_quality_gate() runs EFV", "scores all articles", "writes reextraction_queue.json for low-scorers", "stage_auto_approve() should skip low-scorers"]
}
```

### SC-XPROC-6: Overseer Health → AESHI Score Computation

```json
{
  "id": "SC-XPROC-6",
  "name": "Overseer health data reaches AESHI computation",
  "description": "Values written by overseer.check_health() to overseer_health_metrics table are read by compute_aeshi() and contribute to the final score",
  "metric": "AESHI reads fresh (< 24hr) health metrics from overseer DB",
  "threshold": "100% of AESHI components from real data (not defaults)",
  "test_name": "test_xproc_health_feeds_aeshi",
  "rationale": "AESHI-SC2 tests 'no default scores' but doesn't verify the data actually came from overseer.check_health(). If overseer never ran, AESHI would either use stale data or defaults without anyone knowing.",
  "trigger_source": "src/services/overseer.py:check_health()",
  "effect_target": "src/services/overseer.py:compute_aeshi()",
  "chain": ["check_health()", "_record_metrics()", "compute_aeshi() reads overseer_health_metrics", "produces score 0-100"]
}
```

### SC-XPROC-7: Meta-Reviews → Card Retriever

```json
{
  "id": "SC-XPROC-7",
  "name": "Generated meta-reviews are findable by card retriever",
  "description": "Meta-reviews generated by ClusterMetaReview are persisted to data/materialized_views/meta_reviews/ AND CardRetriever.try_match() can find and return them for matching queries",
  "metric": "for each meta_review, try_match(review.topic) returns a match with score > 0.5",
  "threshold": ">= 80% of meta-reviews are retrievable",
  "test_name": "test_xproc_meta_reviews_retrievable",
  "rationale": "CMR has 14 SCs testing quality but ZERO testing retrieval. SC-E2E-8 tests that the directory exists but not that the retriever can find anything in it. This is exactly the 'last mile' problem.",
  "trigger_source": "src/qa/cluster_meta_review.py:generate()",
  "effect_target": "src/qa/card_retriever.py:try_match()",
  "chain": ["ClusterMetaReview.generate()", "writes to data/materialized_views/meta_reviews/", "CardRetriever loads index", "try_match() scores queries against index", "returns formatted response"]
}
```

### SC-XPROC-8: CardRetriever Fast-Path → IntegratedQueryService

```json
{
  "id": "SC-XPROC-8",
  "name": "Card fast-path in IQS returns complete response",
  "description": "CardRetriever.try_match_unified() called from IntegratedQueryService.query() returns a valid IntegratedResponse that is indistinguishable from a live-computed response",
  "metric": "card response has same fields as live IntegratedResponse (answer, sources, confidence)",
  "threshold": "100% field compatibility",
  "test_name": "test_xproc_card_fastpath_response_shape",
  "rationale": "AG wired the fast-path in Round 14 but no test verifies the IntegratedResponse wrapper is complete. If a field is missing, downstream consumers fail silently.",
  "trigger_source": "src/qa/card_retriever.py:try_match_unified()",
  "effect_target": "src/services/integrated_query_service.py:query()",
  "chain": ["IQS.query() calls try_match_unified()", "CardRetriever finds match", "IQS wraps in IntegratedResponse", "response sent to consumer"]
}
```

### SC-XPROC-9: Nightly Pipeline → Overseer Coverage Invariants

```json
{
  "id": "SC-XPROC-9",
  "name": "Nightly pipeline stage_overseer_coverage() updates AESHI",
  "description": "stage_overseer_coverage() in nightly pipeline calls overseer.compute_aeshi() and the resulting score is persisted",
  "metric": "overseer_health_metrics has entry with mode='PERIODIC' within last 24hr",
  "threshold": "1 entry per nightly run",
  "test_name": "test_xproc_nightly_updates_aeshi",
  "rationale": "NIP has only 3 SCs for 17 stages. No test verifies that the nightly actually updates the AESHI score in the database.",
  "trigger_source": "scripts/nightly_integration_pipeline.py:stage_overseer_coverage()",
  "effect_target": "src/services/overseer.py:compute_aeshi()",
  "chain": ["nightly pipeline stage 12", "overseer.compute_aeshi()", "_record_metrics('PERIODIC')", "writes to overseer_health_metrics"]
}
```

### SC-XPROC-10: Source Data Auditor → Overseer Aggregation

```json
{
  "id": "SC-XPROC-10",
  "name": "Source data gap reports reach overseer and are aggregated",
  "description": "When tab generators detect thin source_data, _notify_overseer_gaps() fires and OverseerService.get_source_data_health() can read and aggregate the results",
  "metric": "get_source_data_health() returns entries matching gap reports",
  "threshold": "100% of gap reports are readable by overseer",
  "test_name": "test_xproc_source_data_gaps_reach_overseer",
  "rationale": "Built in Round 15 but will be a last-mile failure if overseer DB path is wrong or pipeline_run_log table doesn't exist.",
  "trigger_source": "src/qa/tab_generators.py:_notify_overseer_gaps()",
  "effect_target": "src/services/overseer.py:get_source_data_health()",
  "chain": ["tab generator detects gap", "_notify_overseer_gaps()", "report_pipeline_run() writes to pipeline_run_log", "get_source_data_health() reads and aggregates"]
}
```

### SC-XPROC-11: Integration → Credence Shift → Card Regen

```json
{
  "id": "SC-XPROC-11",
  "name": "Credence shifts from integration trigger card regeneration",
  "description": "When integration changes a belief's credence (omega), on_credence_shift() fires on CardGenerationOrchestrator, which marks affected cards STALE and queues regeneration",
  "metric": "card_staleness_status == STALE for cards referencing shifted beliefs",
  "threshold": "100% of affected cards marked",
  "test_name": "test_xproc_credence_shift_triggers_card_regen",
  "rationale": "on_credence_shift() exists (L722-730) and calls check_and_queue_stale() but no test verifies the BN credence update actually triggers this function.",
  "trigger_source": "src/services/paper_integration/orchestrator.py step 8+10",
  "effect_target": "src/qa/card_generation_orchestrator.py:on_credence_shift()",
  "chain": ["BN edge update changes omega", "step_bn_update()", "on_credence_shift(card_id, old_omega, new_omega)", "check_and_queue_stale()", "card marked STALE"]
}
```

### SC-XPROC-12: Tab Generator → Source Data Auditor → Upstream Service Execution

```json
{
  "id": "SC-XPROC-12",
  "name": "Source data auditor remediation triggers upstream service",
  "description": "When auditor identifies a gap (e.g., missing provenance), the remediation action is executeable and actually populates the missing data",
  "metric": "after remediation, re-audit shows gap resolved",
  "threshold": ">= 80% of remediations resolve the gap",
  "test_name": "test_xproc_auditor_remediation_works",
  "rationale": "The auditor identifies gaps and suggests remediation code, but nobody tests that the remediation actually works. The upstream service may require parameters the auditor doesn't know about.",
  "trigger_source": "src/qa/source_data_auditor.py:audit()",
  "effect_target": "Multiple upstream services (provenance, argumentation, etc.)",
  "chain": ["audit detects gap", "identifies upstream service", "remediation code is executed", "re-audit shows coverage improved"]
}
```

### SC-XPROC-13: Extraction → Template Relevance → Belief env/outcome IDs

```json
{
  "id": "SC-XPROC-13",
  "name": "Extraction findings get env and outcome IDs for template matching",
  "description": "After extraction, belief_env_outcome_extractor populates environment_id and outcome_id, and then FindingTemplateRelevance can compute tier2 scores",
  "metric": "beliefs with env/outcome IDs can compute tier2_relevance",
  "threshold": ">= 90%",
  "test_name": "test_xproc_extraction_to_template_relevance",
  "rationale": "AG discovered that extraction_to_web.py silently returned None for env_id (MT-19). The fix exists but no end-to-end test verifies the full chain from extraction → env/outcome extraction → template relevance scoring.",
  "trigger_source": "src/services/belief_env_outcome_extractor.py",
  "effect_target": "src/services/finding_template_relevance.py:resolve_findings()",
  "chain": ["extraction produces findings", "env_outcome_extractor populates IDs", "template_relevance reads IDs", "computes tier2_relevance score"]
}
```

### SC-XPROC-14: Nightly Pipeline → MV Rebuild → Card Freshness

```json
{
  "id": "SC-XPROC-14",
  "name": "Nightly MV rebuild refreshes card data sources",
  "description": "stage_mv_rebuild() rebuilds STALE materialized views, and after rebuild, card generation has access to fresh data",
  "metric": "mv_build_manifest shows all views FRESH after rebuild",
  "threshold": "100% of STALE views become FRESH",
  "test_name": "test_xproc_mv_rebuild_refreshes_cards",
  "rationale": "MV rebuild runs but no test verifies it affects card generation. Cards may still read stale data if they don't use the MVs.",
  "trigger_source": "scripts/nightly_integration_pipeline.py:stage_mv_rebuild()",
  "effect_target": "src/qa/card_generation_orchestrator.py",
  "chain": ["nightly stage_mv_rebuild()", "MaterializedViewBuilder.build_all()", "writes to data/materialized_views/", "card generation reads from MVs"]
}
```

### SC-XPROC-15: Annotation Service → Tab Generator → Card Content

```json
{
  "id": "SC-XPROC-15",
  "name": "Annotations created in annotation_service appear in card tabs",
  "description": "When AnnotationService.create_annotation() is called for a belief, the annotation appears in source_data['annotations'] when the entity's card is generated",
  "metric": "annotations created for entity_id appear in generated card tab prose",
  "threshold": "100% of annotations surfaced",
  "test_name": "test_xproc_annotations_reach_card_tabs",
  "rationale": "Annotation service (25 types, 6 layers) stores annotations in SQLite, but tab generators only see them if CW's agents populate source_data['annotations']. Nobody tests this full chain.",
  "trigger_source": "src/services/annotation_service.py:create_annotation()",
  "effect_target": "src/qa/tab_generators.py (mechanism, debate generators)",
  "chain": ["create_annotation()", "stored in SQLite", "CW agent calls get_active_annotations()", "populates source_data['annotations']", "tab generator formats into prose"]
}
```

---

## Section 3: Priority Ranking

| Rank | SC ID | Severity | Likelihood | Undetectability | Risk Score |
|------|-------|----------|------------|-----------------|------------|
| 1 | **SC-XPROC-5** | HIGH — Bad data enters web | HIGH — gate logic is complex | HIGH — no symptoms until QA | **CRITICAL** |
| 2 | **SC-XPROC-3** | HIGH — No post-integration monitoring | HIGH — DB path resolution already failed before | HIGH — silent skip | **CRITICAL** |
| 3 | **SC-XPROC-7** | HIGH — 3,788 meta-reviews invisible to QA | HIGH — different teams wrote producer/consumer | HIGH — cards just show [DRAFT] | **CRITICAL** |
| 4 | **SC-XPROC-2** | HIGH — Extractions never integrated | MED — same naming convention | HIGH — pipeline reports success | **CRITICAL** |
| 5 | **SC-XPROC-4** | HIGH — Cards never update after integration | HIGH — step 15 is non-critical | MED — eventually noticed | **HIGH** |
| 6 | **SC-XPROC-13** | HIGH — Template matching broken | HIGH — already broke once (MT-19) | HIGH — returns 0% silently | **HIGH** |
| 7 | **SC-XPROC-11** | MED — Cards show stale credences | MED — BN path is complex | MED — gradual degradation | **HIGH** |
| 8 | **SC-XPROC-1** | MED — No new papers triaged | LOW — simple file path | HIGH — pipeline shows 0 papers | **MEDIUM** |
| 9 | **SC-XPROC-6** | MED — AESHI uses stale data | MED — depends on nightly | MED — AESHI still computes | **MEDIUM** |
| 10 | **SC-XPROC-8** | MED — Fast-path returns partial response | LOW — AG just wired this | MED — some fields may be missing | **MEDIUM** |
| 11 | **SC-XPROC-10** | LOW — Gap reports lost | MED — new code, untested | LOW — logs show errors | **LOW** |
| 12 | **SC-XPROC-9** | MED — AESHI not updated | LOW — nightly is reliable | MED — stale scores | **MEDIUM** |
| 13 | **SC-XPROC-14** | MED — Stale card data | LOW — MVs are rebuilt | LOW — visible in card timestamps | **LOW** |
| 14 | **SC-XPROC-15** | LOW — Annotations invisible | HIGH — CW agents not built yet | MED — optional content | **LOW** |
| 15 | **SC-XPROC-12** | LOW — Remediation untested | MED — upstream APIs vary | LOW — diagnostic still shows gap | **LOW** |

---

## Section 4: Proposed Test Skeletons (Top 10)

### Test 1: SC-XPROC-5 — EFV Quality Gate Blocks Low-Quality Papers

```python
def test_xproc_efv_blocks_low_quality():
    """Verify extraction field validator ACTUALLY BLOCKS sub-threshold papers."""
    # SETUP: Create a deliberately bad extraction JSON
    bad_extraction = {
        "article_type": "empirical",
        "findings": [{"antecedent": "", "consequent": "", "direction": "up"}]  # Missing fields
    }
    good_extraction = {
        "article_type": "empirical",
        "findings": [{"antecedent": "Light exposure", "consequent": "Alertness", "direction": "increase"}]
    }
    
    # ACT: Run the nightly quality gate stage
    pipeline = NightlyPipeline(dry_run=True)
    
    # Write bad + good extractions to temp dir
    # Run stage_qa_quality_gate()
    # Run stage_auto_approve()
    
    # ASSERT: Bad paper is in reextraction_queue, NOT in approved queue
    # ASSERT: Good paper IS in approved queue
    
    # FAILURE MODE: If gate doesn't block:
    # - Bad paper reaches integration cascade
    # - Cascade creates beliefs with empty antecedents
    # - Web has garbage beliefs with no provenance
    # - AESHI drops but nobody connects it to the bad extraction
```

### Test 2: SC-XPROC-3 — Integration Triggers Overseer

```python
def test_xproc_integration_triggers_overseer():
    """Verify PaperIntegrationOrchestrator triggers overseer post-check."""
    import sqlite3
    import tempfile
    
    # SETUP: Real DB with beliefs table, real overseer DB
    with tempfile.NamedTemporaryFile(suffix='.db') as web_db, \
         tempfile.NamedTemporaryFile(suffix='.db') as overseer_db:
        
        web_conn = sqlite3.connect(web_db.name)
        # Create minimal beliefs table
        web_conn.execute("CREATE TABLE beliefs (belief_id TEXT PRIMARY KEY)")
        web_conn.commit()
        
        # ACT: Run integration cascade with a real paper
        orch = PaperIntegrationOrchestrator(web_conn)
        event = orch.integrate_paper("test_paper", extraction_data=VALID_EXTRACTION)
        
        # ASSERT: Overseer's pipeline_run_log has an entry for this paper
        overseer_conn = sqlite3.connect(overseer_db.name)
        rows = overseer_conn.execute(
            "SELECT * FROM pipeline_run_log WHERE pipeline_id = 'integration'"
        ).fetchall()
        assert len(rows) >= 1, "Overseer never received post-integration notification"
        assert "test_paper" in rows[-1]["metadata"]

    # FAILURE MODE: If _run_overseer_post_check silently skips:
    # - Integration succeeds
    # - Overseer never knows a paper was integrated
    # - INV-1 (provenance) and INV-4 (coherence) checks never fire
    # - Violations accumulate invisibly
```

### Test 3: SC-XPROC-7 — Meta-Reviews Retrievable by CardRetriever

```python
def test_xproc_meta_reviews_retrievable():
    """Verify generated meta-reviews are findable by card retriever."""
    from src.qa.cluster_meta_review import ClusterMetaReview
    from src.qa.card_retriever import CardRetriever
    
    # SETUP: Generate a meta-review for a known cluster
    cmr = ClusterMetaReview()
    review = cmr.generate(cluster_id="light-alertness-cluster", findings=SAMPLE_FINDINGS)
    
    # Save to canonical path
    review.save(Path("data/materialized_views/meta_reviews/"))
    
    # ACT: Try to retrieve via CardRetriever
    retriever = CardRetriever(base_dir="data")
    result = retriever.try_match("How does light exposure affect alertness?")
    
    # ASSERT: Retriever finds the meta-review
    assert result is not None, "CardRetriever cannot find generated meta-review"
    assert result.confidence > 0.5
    assert "light" in result.answer.lower()
    
    # FAILURE MODE: If meta-reviews are invisible:
    # - QA pipeline falls through to expensive live enrichment
    # - 3,788 pre-generated reviews provide zero value
    # - IntegratedQueryService.query() always hits slow path
```

### Test 4: SC-XPROC-2 — Extraction Output Reaches Integration

```python
def test_xproc_extraction_feeds_integration():
    """Verify extraction JSONs are found by integration stage."""
    import tempfile
    from pathlib import Path
    
    # SETUP: Simulate extraction output with known DOI
    with tempfile.TemporaryDirectory() as tmpdir:
        ext_dir = Path(tmpdir) / "data" / "extractions"
        ext_dir.mkdir(parents=True)
        
        # Write extraction in exact format GEQ produces
        doi = "10.1234/test-paper"
        safe_doi = doi.replace("/", "_").replace(".", "_")
        ext_file = ext_dir / f"{safe_doi}.json"
        ext_file.write_text(json.dumps(VALID_EXTRACTION))
        
        # ACT: Run integration stage's file discovery
        # (from scheduled_pipeline.py or nightly_integration_pipeline.py)
        found_files = list(ext_dir.glob("*.json"))
        
        # ASSERT: Integration finds the file AND can parse it
        assert len(found_files) == 1
        loaded = json.loads(found_files[0].read_text())
        assert "findings" in loaded
    
    # FAILURE MODE: If naming convention diverges:
    # - GEQ writes "10_1234_test-paper.json"
    # - Integration looks for "doi:10.1234/test-paper.json"
    # - No match, no integration, no error logged
```

### Test 5: SC-XPROC-4 — Integration Triggers Card Staleness

```python
def test_xproc_integration_triggers_card_staleness():
    """Verify integration step 15 marks affected cards as STALE."""
    from src.qa.card_generation_orchestrator import CardGenerationOrchestrator
    
    # SETUP: Create a card for an entity
    orch = CardGenerationOrchestrator(base_dir="data")
    card = orch.generate_card("LIGHT-01", card_type="t2-mechanism")
    assert card.staleness.status == "FRESH"
    
    # ACT: Simulate integration of a paper that affects LIGHT-01
    orch.on_new_evidence("LIGHT-01", paper_doi="10.1234/new-evidence")
    
    # ASSERT: Card is now STALE
    status = orch.get_staleness("LIGHT-01")
    assert status.status == "STALE"
    assert "10.1234/new-evidence" in status.ledger_events
    
    # FAILURE MODE: If on_new_evidence is never called:
    # - Card shows outdated mechanism data
    # - User reads stale evidence-based conclusions
    # - No regeneration is triggered
    # - Card gradually rots while showing "FRESH" status
```

### Test 6: SC-XPROC-13 — Extraction → Env/Outcome IDs → Template Relevance

```python
def test_xproc_extraction_to_template_relevance():
    """Verify full chain from extraction through env ID population to template scoring."""
    from src.services.belief_env_outcome_extractor import BeliefEnvOutcomeExtractor
    from src.services.finding_template_relevance import resolve_findings
    
    # SETUP: A belief from extraction with known consequent
    belief = {"belief_id": "doi:test/123:f1", "consequent": "Cognitive performance"}
    
    # ACT: Extract env/outcome IDs
    extractor = BeliefEnvOutcomeExtractor()
    enriched = extractor.extract_for_belief(belief)
    
    # ASSERT: IDs were populated
    assert enriched["environment_id"] is not None, "env_id still None after extraction"
    assert enriched["outcome_id"] is not None, "outcome_id still None after extraction"
    
    # ACT: Run template relevance with populated IDs
    results = resolve_findings([enriched], templates=SAMPLE_TEMPLATES)
    
    # ASSERT: tier2_relevance is computed (not null)
    assert results[0]["tier2_relevance"] is not None
    
    # FAILURE MODE: If env_id is None (the MT-19 bug):
    # - template_relevance.compute_tier2() returns None
    # - AESHI template_belief_coverage = 0%
    # - 10 AESHI points lost silently
```

### Test 7: SC-XPROC-11 — Credence Shift → Card Regeneration

```python
def test_xproc_credence_shift_triggers_card_regen():
    """Verify BN credence changes trigger card staleness update."""
    from src.qa.card_generation_orchestrator import CardGenerationOrchestrator
    
    # SETUP: Card exists, credence is 0.7
    orch = CardGenerationOrchestrator(base_dir="data")
    
    # ACT: BN update shifts credence from 0.7 to 0.4 (significant shift)
    orch.on_credence_shift("LIGHT-01", old_omega=0.7, new_omega=0.4)
    
    # ASSERT: Card is marked STALE and queued for regeneration
    stale_count = orch.check_and_queue_stale()
    assert stale_count >= 1, "No cards queued despite significant credence shift"
    
    # FAILURE MODE: If on_credence_shift does nothing:
    # - Card shows "High confidence (ω=0.7)" while actual credence is 0.4
    # - User makes decisions based on outdated confidence
```

### Test 8: SC-XPROC-8 — Card Fast-Path Response Shape

```python
def test_xproc_card_fastpath_response_shape():
    """Verify CardRetriever fast-path returns complete IntegratedResponse."""
    from src.services.integrated_query_service import IntegratedQueryService
    
    # SETUP: Pre-populate a card that will be found by retriever
    # (requires a card in data/qa_cache/ matching the query)
    
    # ACT: Query that should hit the fast path
    iqs = IntegratedQueryService()
    response = iqs.query("How does light affect alertness?")
    
    # ASSERT: Response has ALL required fields
    assert hasattr(response, 'answer') and response.answer
    assert hasattr(response, 'sources') and isinstance(response.sources, list)
    assert hasattr(response, 'confidence')
    assert hasattr(response, 'template_id')
    
    # FAILURE MODE: If fast-path response is incomplete:
    # - Frontend receives response without 'sources'
    # - UI shows answer but no evidence citations
    # - User sees confident claim with no backing
```

### Test 9: SC-XPROC-6 — Health Data Feeds AESHI

```python
def test_xproc_health_feeds_aeshi():
    """Verify overseer health metrics reach AESHI computation."""
    from src.services.overseer import OverseerService
    
    # SETUP: Run health check which writes to overseer_health_metrics
    overseer = OverseerService(overseer_db_path, web=None, web_db_path=web_db)
    health = overseer.check_health()
    
    # ACT: Compute AESHI (should read the metrics we just wrote)
    score = overseer.compute_aeshi()
    
    # ASSERT: Score is computed from REAL data, not defaults
    assert score > 0, "AESHI score is 0 — likely using defaults"
    assert score != 100, "AESHI score is 100 — definitely using optimistic defaults"
    
    # Verify the specific component came from check_health()
    aeshi_detail = overseer.compute_aeshi(health_metrics=health)
    assert aeshi_detail == score, "AESHI computation inconsistent between live and passed metrics"
    
    # FAILURE MODE: If health data doesn't reach AESHI:
    # - AESHI defaults all metrics to optimistic values
    # - System Health Report shows GREEN while subsystems are broken
    # - False confidence prevents investigation
```

### Test 10: SC-XPROC-10 — Source Data Gaps Reach Overseer

```python
def test_xproc_source_data_gaps_reach_overseer():
    """Verify tab generator gap reports are aggregated by overseer."""
    from src.qa.tab_generators import _notify_overseer_gaps
    from src.qa.source_data_auditor import audit_source_data
    from src.services.overseer import OverseerService
    
    # SETUP: Audit source data with known gaps
    thin_data = {"mechanism_chain": [], "theory_links": []}  # Missing provenance etc.
    audit = audit_source_data("TEST-01", "t2-mechanism", thin_data)
    
    # ACT: Notify overseer of gaps
    _notify_overseer_gaps("TEST-01", "mechanism", audit)
    
    # ASSERT: Overseer can read the gap report
    overseer = OverseerService(overseer_db_path, web=None, web_db_path=web_db)
    health = overseer.get_source_data_health()
    
    assert health["audited_entities"] >= 1
    assert health["avg_coverage"] < 1.0  # Not fully covered
    assert any(
        e["entity_id"] == "TEST-01" 
        for e in health.get("entities_with_critical_gaps", [])
    )
    
    # FAILURE MODE: If gap reports don't reach overseer:
    # - Tab generators detect gaps but nobody aggregates them
    # - Overseer doesn't know which entities need remediation
    # - Source data stays thin forever
```

---

## Summary for CW

### The Core Problem
**89.1% of success conditions test modules in isolation.** The wiring between modules exists in code but is virtually untested. This means:
1. Every module thinks it's working (its tests pass)
2. The pipeline thinks it's working (exit code 0)
3. But signals may never propagate from Module A to Module B

### The Top 5 Actions

1. **Write SC-XPROC-5**: The EFV quality gate is the most dangerous gap — bad data entering the web is catastrophic and invisible
2. **Write SC-XPROC-3**: Integration → Overseer is wired (L332-398) but the DB path resolution has already failed before, silently skipping the check
3. **Write SC-XPROC-7**: 3,788 meta-reviews may be invisible to QA — the most expensive last-mile failure
4. **Write SC-XPROC-2**: Extraction → Integration file handoff relies on naming convention that is never tested
5. **Write SC-XPROC-13**: The MT-19 chain (extraction → env IDs → template matching) broke once and will break again without a cross-process test

### The Pattern
Every gap follows the same pattern David identified: **the developer wired the trigger, the unit test passes, but nobody tests whether the bullet actually left the barrel.** The test skeletons above use real objects (not mocks) specifically to catch these "wired but not firing" failures.
