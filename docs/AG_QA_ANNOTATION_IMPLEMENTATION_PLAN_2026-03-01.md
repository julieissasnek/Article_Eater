# QA & Annotation System: Spec, Plan, and Implementation

## Status of Existing Specs

| System | Spec exists? | What it covers | What's missing |
|--------|-------------|----------------|----------------|
| **QA** | ✅ [QA_SYSTEM_SPEC.md](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/docs/QA_SYSTEM_SPEC.md) (602 lines) | 9 subsystems, 22 SCs, gap analysis, integration matrix | Implementation status tracking; post-fix verification |
| **Annotation** | ❌ No spec document | — | Everything: no single doc explains the annotation architecture |

---

## Part 1: QA System — Current State Audit

### 9 Subsystems (~8,500 LOC)

| # | Subsystem | LOC | Wired to Pipeline? | Wired to AESHI? | Tests? |
|---|-----------|-----|--------------------|--------------------|--------|
| 1 | [Reflex System](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/qa/reflex_system.py) | 1725 | ✅ Nightly stage | ✅ Via overseer | ✅ 23 classes |
| 2 | [Template QA](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/services/template_quality_assurance.py) | 247 | ❌ Manual only | ❌ | ⚠️ Partial |
| 3 | [Argument QA](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/argument/qa_handlers.py) | 219 | ❌ Manual only | ❌ | ⚠️ Partial |
| 4 | [Warrant Service](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/services/warrant_service.py) | 486 | ❌ Not nightly | ❌ | ⚠️ Partial |
| 5 | [Source Quality](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/epistemic/source_quality.py) | 319 | ❌ Computed but unused | ❌ | ✅ |
| 6 | [Gap Predictor](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/services/gap_predictor.py) | 1497 | ⚠️ Added to nightly discovery | ❌ | ⚠️ Partial |
| 7 | [VOI Scoring](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/cmr/voi_scoring.py) | 109 | ❌ | ❌ | ⚠️ |
| 8 | [VOI Search](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/services/voi_search.py) | 1946 | ❌ | ❌ | ⚠️ |
| 9 | [QA Cache](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/qa/qa_cache_manager.py) | 120 | ✅ Nightly | ❌ | ✅ |

### 22 Success Conditions — Status

Already defined in QA_SYSTEM_SPEC.md §8. Here's what's been done:

| Tier | SC | Status | Notes |
|------|-----|--------|-------|
| 1 — Hygiene | SC-QA-01 to 04 | ✅ Done | All 15 reflexes run, report to overseer |
| 2 — Epistemic | SC-QA-05 (warrant runs) | ❌ **NOT DONE** | Warrant not run nightly |
| 2 | SC-QA-06 (zero INV-1) | ❌ **NOT DONE** | No check |
| 2 | SC-QA-07 (SQ computed) | ⚠️ Partial | Computed but not fed to credence |
| 2 | SC-QA-08 (DEFEATED flagged) | ✅ Done | WarrantStatusReflex added |
| 2 | SC-QA-09 (COHERENT_ONLY flagged) | ✅ Done | ProvenanceGroundingReflex added |
| 3 — Integration | SC-QA-10 (rollback→QA) | ✅ Done | Post-rollback hook added |
| 3 | SC-QA-11 (annotations→gaps) | ✅ Done | OPEN_QUESTION harvest added |
| 3 | SC-QA-12 (SENSITIVITY→template QA) | ❌ **NOT DONE** | |
| 3 | SC-QA-13 (provenance→AESHI) | ❌ **NOT DONE** | |
| 3 | SC-QA-14 (web UI warrant badges) | ❌ **NOT DONE** | Deferred (UI cycle) |
| 4 — Discovery | SC-QA-15 (nightly gap pred) | ✅ Done | Nightly discovery stage added |
| 4 | SC-QA-16 (high-VOI queries) | ⚠️ Partial | Infra exists, not closed loop |
| 4 | SC-QA-17 (nightly defeater search) | ✅ Done | Added to nightly discovery |
| 4 | SC-QA-18 (annotation harvest) | ✅ Done | Added to nightly discovery |
| 4 | SC-QA-19 (VOI re-score) | ✅ Done | Added to nightly discovery |
| 5 — Principles | SC-QA-20 (principles doc) | ❌ **NOT DONE** | No `EPISTEMIC_PRINCIPLES.md` |
| 5 | SC-QA-21/22 | ✅ Done | Independence/commitment in source_quality |

### QA Remaining Work

| Priority | What | Where | Effort |
|----------|------|-------|--------|
| **P1** | Nightly warrant computation on all beliefs | `nightly_integration_pipeline.py` | ~2 hrs |
| **P1** | Source Quality → Credence feedback | `web_persistence.py` | ~2 hrs |
| **P2** | SENSITIVITY_FLAG → template QA | `template_quality_assurance.py` | ~1 hr |
| **P2** | Provenance JustificationStatus → AESHI | `compute_system_health.py` | ~1 hr |
| **P2** | `EPISTEMIC_PRINCIPLES.md` | `docs/` | ~1 hr |
| **P3** | VOI count → AESHI component | `compute_system_health.py` | ~30 min |
| **P3** | Web UI warrant badges | TypeScript/React | ~4 hrs (deferred) |

---

## Part 2: Annotation System — Full Spec

### What Exists (Three Parallel Systems)

```
┌─────────────────────────────────────────────┐
│  ANNOTATION LAYER 1: General-Purpose        │
│  annotation_service.py (634L)               │
│  SQLite-backed, 10 types, 3 layers          │
│  CRUD + search + supersession versioning    │
│  Targets: belief, template, answer, theory  │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│  ANNOTATION LAYER 2: CVA-Specific           │
│  cva_annotation_service.py (283L)           │
│  JSON file-backed, auto-detect patterns     │
│  Types: modality, stimulus, molecule links  │
│  cva_annotations.py (238L) = data models    │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│  ANNOTATION LAYER 3: Extended A9-A18        │
│  extended_annotations.py (434L)             │
│  Data models only (no service class)        │
│  Types: surprise, design implication,       │
│  dispute, analogy, replication, effect,     │
│  cross-domain, history, hook, unanswered    │
└─────────────────────────────────────────────┘
```

### The Problem

These three layers are **not unified**:
- Layer 1 uses SQLite (`web_persistence_v2.db`)
- Layer 2 uses JSON files (`data/annotations/`)  
- Layer 3 has data models but **no persistence service at all**
- No single API to ask "what annotations exist for belief X?"
- No annotation feeds back into QA, AESHI, or entrenchment

### Annotation Types Inventory

| ID | Type | Layer | Persistence | QA consumes? | AESHI? |
|----|------|-------|-------------|-------------|--------|
| A1 | CALIBRATION_NOTE | L1 | ✅ SQLite | ❌ | ❌ |
| A2 | SENSITIVITY_FLAG | L1 | ✅ SQLite | ❌ | ❌ |
| A3 | EVIDENCE_OVERRIDE | L1 | ✅ SQLite | ❌ | ❌ |
| A4 | PROVENANCE_PATCH | L1 | ✅ SQLite | ❌ | ❌ |
| A5 | CROSS_REFERENCE | L1 | ✅ SQLite | ❌ | ❌ |
| A6 | MOLECULE_LINK | L1 | ✅ SQLite | ⚠️ CVA only | ❌ |
| A7 | CLINICAL_CAUTION | L1 | ✅ SQLite | ❌ | ❌ |
| A8 | OPEN_QUESTION | L1 | ✅ SQLite | ✅ Gap pred | ❌ |
| CVA | measurement_modality | L2 | JSON files | ❌ | ❌ |
| CVA | stimulus_description | L2 | JSON files | ❌ | ❌ |
| CVA | molecule_t15_link | L2 | JSON files | ❌ | ❌ |
| A9 | surprise_flag | L3 | **None** | ❌ | ❌ |
| A10 | design_implication | L3 | **None** | ❌ | ❌ |
| A11 | dispute | L3 | **None** | ❌ | ❌ |
| A12 | analogical_bridge | L3 | **None** | ❌ | ❌ |
| A13 | replication_status | L3 | **None** | ❌ | ❌ |
| A14 | effect_magnitude | L3 | **None** | ❌ | ❌ |
| A15 | cross_domain | L3 | **None** | ❌ | ❌ |
| A16 | historical_context | L3 | **None** | ❌ | ❌ |
| A17 | narrative_hook | L3 | **None** | ❌ | ❌ |
| A18 | unanswered_question | L3 | **None** | ❌ | ❌ |

### Annotation System Success Conditions

| ID | Condition | Threshold | Current |
|----|-----------|-----------|---------|
| **AN-SC-01** | Single query API returns all annotation types for any target | 100% types accessible | ❌ |
| **AN-SC-02** | All 3 layers persist to same backing store | 100% in SQLite | ❌ (only L1) |
| **AN-SC-03** | A9-A18 data models have persistence service | 100% | ❌ |
| **AN-SC-04** | Annotation count per belief > 0 for >50% of beliefs | >50% | ❌ (unknown) |
| **AN-SC-05** | SENSITIVITY_FLAG consumed by template QA | 100% | ❌ |
| **AN-SC-06** | OPEN_QUESTION consumed by gap predictor | 100% | ✅ Done |
| **AN-SC-07** | SEARCH_PROMPT consumed by VOI search | 100% | ❌ |
| **AN-SC-08** | Annotations influence belief entrenchment | Formula defined | ❌ |
| **AN-SC-09** | Annotation health → AESHI component | Score defined | ❌ |
| **AN-SC-10** | Auto-annotation runs on all extractions | >90% coverage | ⚠️ (CVA only, 116/166) |
| **AN-SC-11** | Annotation supersession works end-to-end | Test passes | ✅ (L1 only) |
| **AN-SC-12** | Full-text search across annotations | Returns results | ✅ (L1 only) |

### Annotation System Remaining Work

| Priority | What | Effort |
|----------|------|--------|
| **P1** | Unify L2+L3 into L1's SQLite backing | ~3 hrs |
| **P1** | Single `get_all_annotations(target_id)` API | ~1 hr |
| **P1** | Persist A9-A18 to SQLite via AnnotationService | ~2 hrs |
| **P2** | Wire annotations → AESHI component | ~1 hr |
| **P2** | Wire SENSITIVITY_FLAG → template QA | ~1 hr |
| **P2** | Wire SEARCH_PROMPT → VOI search | ~1 hr |
| **P3** | Auto-annotate pipeline for A9-A14 on all beliefs | ~2 hrs |
| **P3** | Annotation → entrenchment formula | ~2 hrs |

---

## Part 3: Joint Sprint Design

### Sprint A: QA Wiring (est. 4 hrs)
1. Nightly warrant computation on all beliefs
2. Source Quality → Credence feedback (P0 per CW)
3. VOI count → AESHI component
4. EPISTEMIC_PRINCIPLES.md

### Sprint B: Annotation Unification (est. 4 hrs)
1. Migrate L2+L3 persistence to SQLite (same DB as L1)
2. Single `get_all_annotations(target_id)` API
3. Persist generated A9-A18 data to SQLite
4. Wire SENSITIVITY_FLAG → template QA
5. Wire SEARCH_PROMPT → VOI search

### Sprint C: Integration + Verification (est. 2 hrs)
1. Annotation health → AESHI component
2. Run 5 real beliefs through full pipeline trace
3. Verify annotation queries return results
4. Run example QA queries

### Sprint D: Ruthless V8 (after Sprints A-C)

See Part 4.

---

## Part 4: Ruthless V8 — Amped-Up Audit

### Panel Composition

| Panelist | Focus |
|----------|-------|
| **Graph Theorist** | Belief graph: diameter, clustering coefficient, degree distribution, betweenness centrality, community structure, connected components |
| **Distributed Systems Engineer** | Data flow linearity, idempotency, error propagation, eventually-consistent state, API contracts |
| **Database/IR Specialist** | Index coverage, query plan efficiency, N+1 problems, schema normalization |
| **Bayesian Network Expert** | CPD correctness, d-separation, interventional reasoning, BN↔EN consistency |
| **Phil of Science** | Quinean holism correctness, constraint semantics, entrenchment computation vs BonJour, foundherentism vs coherentism |

### New Graph Theory Metrics

| Metric | Healthy Range | What bad values mean |
|--------|--------------|---------------------|
| Graph diameter | <10 | Isolated clusters, no global coherence |
| Clustering coefficient | >0.1 | Beliefs don't form local clusters |
| Degree distribution | Power-law (γ ≈ 2-3) | Random graph = no structure |
| Betweenness centrality top-10 | Named entities | Critical bridge beliefs to protect |
| Connected components | 1 giant + isolates <5% | Fragmented web |
| Average path length | <6 | Small-world property |

### Audit Scenarios

1. **New user**: Search for "how does ceiling height affect creativity?" → full pipeline trace
2. **Theory conflict**: Two theories predict opposite effects → how does the system handle it?
3. **Paper retraction**: Rollback a high-influence paper → cascading effects
4. **Gap discovery**: What does the system think it doesn't know yet?
5. **Design brief**: "Design a school that maximizes attention restoration" → can the system generate evidence-based recommendations?

### Pre-Ruthless Checklist

- [ ] Sprints A-C complete
- [ ] All 22 QA SCs passing (or documented exceptions)
- [ ] All 12 Annotation SCs passing (or documented exceptions)
- [ ] 5 example queries tested and returning sensible results
- [ ] Graph metrics computed and within healthy ranges

---

## Verification Plan

### Automated Tests
```bash
pytest tests/test_success_conditions.py -v
python3 scripts/compute_system_health.py --skip-gates
python3 scripts/run_reflexes.py --all
```

### Manual Verification
1. Query: "What's surprising about biophilia in dense vegetation?"
2. Query: "How strong is the evidence for daylight → cortisol reduction?"
3. Trace belief `pdf:doi:10.xxx:TBL-C025` through all systems
4. Verify annotation count > 0 for >50% of beliefs
5. Run graph metrics on belief graph
