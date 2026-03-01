# CONSOLIDATED ACTION LIST — What Has to Be Done

**Date**: February 28, 2026
**Audit by**: Cowork Session 13 continued
**Scope**: Full repo audit + AG assignment cross-reference + code gap analysis

---

## EXECUTIVE SUMMARY

The codebase is in **good health** (audit grade: A). AG has completed Phases 0–3 and Phase 6 of the 7-phase CVA implementation, plus partial Phase 4. The remaining work falls into three categories:

1. **AG's Remaining CVA Phases** (Phases 4–5, 7 + Phase 2 remediation) — ~90 hrs
2. **Pre-existing Stubs/TODOs** (from original ATLAS codebase) — ~25 hrs
3. **Infrastructure & Integration Tasks** (not assigned to anyone yet) — ~15 hrs

---

## A. AG STATUS: WHAT AG HAS BUILT

| Phase | Status | Files Created | Tests | Notes |
|-------|--------|--------------|-------|-------|
| **Phase 0** | ✅ COMPLETE | logging_config.py, overseer INV-6..9 | Part of test suite | Foundation solid |
| **Phase 1** | ✅ COMPLETE | cva_constraint.py (285 lines), cva_valuation.py (338), subject_characteristics.py (362), activity_frame.py (239), cva_annotations.py | 37 tests | Data models all present |
| **Phase 2** | ⚠️ 70% COMPLETE | cva_constraint_engine.py (342), cva_valuation_engine.py (248), cva_dynamics.py (565), cva_beauty.py (244) | 24 tests | **MISSING**: cva_feedback.py, sparse auxiliary, probabilistic recognition partial |
| **Phase 3** | ⚠️ 60% COMPLETE | cva_attractor.py (321), rasa_attractors.json | 13 tests | **MISSING**: cultural_attractors/ directory, full basin computation |
| **Phase 4** | ⚠️ 30% COMPLETE | overseer_playbooks.py (299) | — | **MISSING**: overseer_predictive.py, overseer_nightly_v3.py, learning loop, CVA invariants INV-10..13 |
| **Phase 5** | ❌ NOT STARTED | — | — | Annotation types, batch scripts |
| **Phase 6** | ✅ COMPLETE | 5 molecule JSONs in data/molecules/ | 16 E2E tests | All molecules created and linked |
| **Phase 7** | ❌ NOT STARTED | — | — | Integration + stress tests, system report |

**Total AG Tests**: 90 (37 models + 24 engines + 13 attractor + 16 E2E)
**Total AG Code**: ~3,243 lines across 10 files

---

## B. WHAT REMAINS — ORGANIZED BY OWNER

### B1. ASSIGN TO AG: Phase 2 Remediation + Remaining Phases (~90 hrs)

These tasks require AG because they extend AG's own code and involve the mathematical/computational heart of CVA.

#### Phase 2 Remediation (Three Hard Problems) — ~31 hrs
*See `AG_PHASE2_REMEDIATION_2026-02-28.md` for full specification*

| ID | Task | Priority | Est. Hours |
|----|------|----------|-----------|
| R2.4 | **Coupling Matrices**: Replace scalar α/β with full K_cc [8×8], K_cv [8×9], K_vc [9×8], K_vv [9×9] | P0 (CRITICAL) | 8 |
| R2.1 | **Probabilistic Recognition**: ConstraintDistribution with Gaussian posterior, precision from ActivityFrame | P0 (CRITICAL) | 6 |
| R2.2 | **Decomposed Feedback**: Create `cva_feedback.py` — ε_attn (0.3-0.5s), ε_prec (0.5-2.0s), ε_prior (1-5s) | P0 (CRITICAL) | 6 |
| R2.5 | **Lyapunov Analysis**: Full 17×17 Jacobian (not diagonal), proper basin-of-attraction | P1 | 5 |
| R2.3 | **Sparse Auxiliary**: v_core always active, v_aux frame-dependent with sparsity control | P1 | 3 |
| R2.6 | **Test Suite**: ~20 new tests for all remediated code | P1 | 3 |

#### Phase 3 Completion — ~14 hrs

| Task | Description | Est. Hours |
|------|-------------|-----------|
| 3.5 | Cultural attractor variants (4 JSON files in data/cva/cultural_attractors/) | 4 |
| 3.6 | Attractor transition dynamics (hysteresis, frame-switch bifurcation) | 6 |
| 3.7 | Neurotype basin modulation (PTSD→enlarged Bhayānaka, etc.) | 4 |

#### Phase 4 Completion — ~22 hrs

| Task | Description | Est. Hours |
|------|-------------|-----------|
| 4.2 | Auto-remediation engine (`_process_violations()` in overseer.py) | 8 |
| 4.3 | Learning loop (track remediation success rates in overseer.db) | 4 |
| 4.4 | Predictive health (`overseer_predictive.py` — NEW, ~300 lines) | 6 |
| 4.5 | CVA-aware invariants INV-10 through INV-13 | 4 |
| 4.6 | Unified nightly report v3 (`overseer_nightly_v3.py` — NEW, ~400 lines) | Included |

#### Phase 5: QA Annotations — ~20 hrs

| Task | Description | Est. Hours |
|------|-------------|-----------|
| 5.1-5.3 | Add MEASUREMENT_MODALITY, STIMULUS_DESCRIPTION, MOLECULE_T15_LINK annotation types | 8 |
| 5.4-5.5 | Batch-annotate templates (batch_annotate_measurements.py, batch_annotate_stimuli.py) | 8 |
| 5.6 | Wire annotations into QA preprocessing | 4 |

#### Phase 7: Integration Testing — ~26 hrs

| Task | Description | Est. Hours |
|------|-------------|-----------|
| 7.1 | Paper → extraction → CVA annotation → integration E2E test | 6 |
| 7.2 | Overseer detects CVA violation → auto-remediates E2E test | 4 |
| 7.3 | Cultural variant switching (Western → Japanese) E2E | 3 |
| 7.4 | Attractor computation for 3 design scenarios | 4 |
| 7.5 | 100 papers through pipeline stress test | 4 |
| 7.6 | Overseer nightly v3 dry run | 2 |
| 7.7 | System health report generation script | 3 |

---

### B2. ASSIGN TO COWORK (THIS TERMINAL): Pre-existing Stubs + Infrastructure (~40 hrs)

These are ATLAS-core tasks independent of AG's CVA work. I can do them now or in parallel.

#### Pre-existing Stubs (from audit)

| ID | Task | File | Blocker | Est. Hours | Can Do Now? |
|----|------|------|---------|-----------|-------------|
| S1 | Implement `find_critical_question_gaps()` | gap_predictor.py:1210 | ClaimV2 argument fields | 4 | ⚠️ Partial — can implement skeleton with fallback |
| S2 | Implement `find_argument_attack_gaps()` | gap_predictor.py:1232 | Contrast class analysis | 4 | ⚠️ Partial — can wire to existing argument_attack.py |
| T1 | Implement `_fetch_finding_by_iv_dv()` | prediction_generator.py:614 | findings_db schema | 2 | YES — can implement against extraction data |
| T2 | Wire BN posterior/prior/likelihood into QueryResult | integrated_query_service.py:700 | BN service API | 3 | ⚠️ Depends on BN calibration state |
| T3 | Remove duplicate classes from epistemic_causal_bridge.py | epistemic_causal_bridge.py:75,165 | Demo function updates | 3 | YES — straightforward cleanup |
| T4 | VOI-driven search integration | interpretive_intelligence.py:2631 | VOI algorithm | 6 | ❌ Blocked — needs panel decision |

#### Sprint Tasks Still Pending (from TASKS.md)

| ID | Task | Est. Hours | Can Do Now? |
|----|------|-----------|-------------|
| SPRINT-1-REV | Three-Number Separation (ω, d, CPT) throughout codebase | 8 | YES |
| SPRINT-2-REV | π Projection Deployment (log-odds formula in epistemic_projection.py) | 6 | YES |
| SPRINT-3 update | Coherence Dashboard update for new warrant types | 3 | YES |
| SPRINT-4 update | Argumentation Graph + AESHI recalibration | 3 | YES |
| SPRINT-5 update | Nightly Batch Infrastructure warrant monitoring | 2 | YES |
| SPRINT-6 update | Expert Calibration Prep update | 2 | YES |

---

### B3. BLOCKED / DEFERRED — Neither Terminal Should Do Yet

| Task | Blocked By | When |
|------|------------|------|
| T7.3 (Extend ae.rule.v2 with theory_links) | CMR-SPEC | After CMR spec complete |
| T7.4 (Update extraction prompts) | CMR-SPEC | After CMR spec complete |
| T7.6 (Theory agent profiles) | T7.3/T7.4 | After theory links |
| PANEL-CALIBRATION | Scheduling with David | Mar 2-3 target |
| GOLDILOCKS-PANEL | Low priority | Deferred |
| EN-0C completion (1,037 papers) | AG in progress | Ongoing |

---

## C. RECOMMENDED EXECUTION ORDER

### For AG (next session):

```
1. Phase 2 Remediation (R2.4 → R2.1 → R2.2 → R2.5 → R2.3 → R2.6)  ~31 hrs
2. Phase 3 Completion (3.5 → 3.6 → 3.7)                               ~14 hrs
3. Phase 4 Completion (4.2 → 4.3 → 4.4 → 4.5 → 4.6)                  ~22 hrs
4. Phase 5 (5.1-5.6)                                                    ~20 hrs
5. Phase 7 (7.1-7.7)                                                    ~26 hrs
                                                              TOTAL: ~113 hrs
```

### For This Terminal (NOW):

```
1. T3: Remove duplicate classes from epistemic_causal_bridge.py          ~3 hrs
2. T1: Implement _fetch_finding_by_iv_dv()                               ~2 hrs
3. SPRINT-1-REV: Three-Number Separation                                 ~8 hrs
4. SPRINT-2-REV: π Projection Deployment                                 ~6 hrs
5. S1/S2: Partial stub implementation (gap predictor)                    ~6 hrs
6. SPRINT-3..6 updates                                                   ~10 hrs
                                                              TOTAL: ~35 hrs
```

---

## D. SUMMARY TABLE

| Category | Tasks | Hours | Owner |
|----------|-------|-------|-------|
| AG Phase 2 Remediation | 6 tasks | 31 | AG |
| AG Phases 3-5, 7 completion | ~20 tasks | 82 | AG |
| Pre-existing stubs (doable now) | 3 tasks | 9 | Cowork |
| Sprint 1-REV + 2-REV (codebase-wide) | 2 sprints | 14 | Cowork |
| Sprint 3-6 updates | 4 sprints | 10 | Cowork |
| Blocked/Deferred | 6 items | — | Later |
| **TOTAL** | ~41 tasks | ~146 hrs | — |

---

*Generated by Cowork Session 13 continued · February 28, 2026*
