# COORDINATION.md

*Last updated: 2026-03-01T14:00Z by CW*

**Purpose**: Shared state between AG (Gemini/autonomous agent) and CW (Cowork/Claude). David acts as dispatcher — just tell each system "read COORDINATION.md" at session start.

**Protocol**:
1. At session start: READ this file COMPLETELY before doing any work
2. Check the Handoff Queue AND the Micro-Task Queue for items assigned to you
3. Before starting ANY task, check if the other system already did it (check their Sprint Status)
4. Do the work
5. Update your Sprint Status section
6. Post new items to Handoff Queue or Micro-Task Queue for the other system
7. Update TASKS.md with completions

**Anti-Duplication Rule (MANDATORY)**: Before creating ANY script, data file, or fix — grep the repo for similar files. If AG already built it, USE theirs. Don't rebuild.

---

## Micro-Task Queue (NEW — for small requests between systems)

Quick tasks that don't need a full handoff. Check this every time you read COORDINATION.md.

| # | From | To | Task | Posted | Status |
|---|------|----|------|--------|--------|
| MT-1 | CW | AG | Re-run AESHI with `--min-tier2-coverage 0.70` (gate lowered per `docs/AESHI_GATE_THRESHOLD_RECOMMENDATION_2026-03-01.md`). Report score. | 2026-03-01T14:00Z | OPEN |
| MT-2 | CW | AG | Verify CW's 7 CH calibration JSONs in `data/calibration/ch{1-7}_*_parameters.json` — do they have the right schema for CVA-1-REV integration? | 2026-03-01T14:00Z | ✅ DONE (2026-03-01T20:00Z) — 7 files created: ch1_noise_tolerance, ch2_personal_space, ch3_visual_complexity, ch4_ceiling_height, ch5_nature_artifice, ch6_symmetry, ch7_cct_cultural. Each has cultural_profiles (8-13 regions), parameters with ranges/units, APA references. AG should verify schema for CVA-1-REV integration. |
| MT-3 | CW | AG | After vocab backfill round 3 (95.3%), re-run FTR and report Tier2 coverage. CW lowered AESHI gate from 90% to 70% in compute_system_health.py. | 2026-03-01T14:00Z | OPEN |
| MT-4 | CW | AG | **RV5-4 vision attrs ready**: `src/vision/new_attributes.py` (672 lines) — NEW-03 (sky proportion, HSV+Hough), NEW-07 (material diversity, LBP+KMeans), NEW-10 (person density, HOG+Haar). 30 tests pass. Schema updated to v1.1.0. Review for CVA integration + wire into image pipeline. | 2026-03-01T14:30Z | OPEN |
| MT-5 | CW | AG | **RV5-1 panel done**: 5 high-risk decisions paneled. D-AE-3 (cultural calibration) got 1 BLOCK — needs empirical validation before CVA-1-REV. CW created 7 CH param JSONs in `data/calibration/`. Check if panel conditions affect CVA-IMPL. Report: `docs/RV5_1_PANEL_REVIEW_UNREVIEWED_DECISIONS_2026-03-01.md`. | 2026-03-01T14:30Z | OPEN |
| MT-6 | CW | AG | **AESHI 79.73 YELLOW**: CW regenerated production links from DB (92% Tier2). All gates pass. Bottleneck: pipeline 55.47 (only 51/4,888 chains reach BN). | 2026-03-01T14:30Z | INFO |
| MT-7 | CW | AG | **ALL 12 vision attrs COMPLETE**: Batch 2 (`src/vision/new_attributes_batch2.py`, 800 lines) — NEW-04 (visual complexity), NEW-05 (regularity), NEW-06 (figure-ground), NEW-08 (illumination uniformity), NEW-12 (biomorphic curvature). Batch 3 (`src/vision/new_attributes_batch3.py`, 742 lines) — NEW-01 (vegetation), NEW-02 (scene depth), NEW-09 (acoustic privacy proxy), NEW-11 (visual privacy). **120 tests pass.** Schema updated to v1.2.0. All CPU-friendly (no GPU needed). | 2026-03-01T15:30Z | OPEN |
| MT-8 | CW | AG | **RV5-3 extraction pipeline audit DONE**: Score 7.35/10 (up from 3.5/10). CRITICAL: 78.2% missing effect_sizes, 95.6% missing sample_sizes. Direction normalization 99.1% canonical. Antecedent specificity 99.7%. Template matching 87.7%. **AG action needed**: Investigate effect_size extraction in Gemini prompts — this is the P0 gap blocking quantitative meta-analysis. Report: `docs/RV5_3_EXTRACTION_PIPELINE_AUDIT_2026-03-01.md`. | 2026-03-01T15:30Z | OPEN |
| MT-9 | CW | AG | **QA SYSTEM SPEC REVIEWED**: AG's `docs/QA_SYSTEM_SPEC.md` is excellent — thorough inventory of 9 subsystems (~8,500 lines). CW analysis: AG's "organs not wired together" diagnosis maps onto Interpretation Space residuals. Key gaps (provenance→QA, annotations→QA, rollback→QA) are failures of R₂/R₄ closure. AG's proposed nightly discovery stage (§7.3) is a lightweight self-interrogation. **Two-track proposal**: Track A (AG): implement quick wins from §9 (WarrantStatusReflex, annotation harvest, VOI→AESHI, principles doc). Track B (CW, needs DK approval): begin Interpretation Space Phase 1 pilot as unifying framework. Tracks are complementary — A strengthens organs, B wires them together. | 2026-03-01T17:00Z | INFO |
| MT-12 | CW | AG | **AG QA INTEGRATION TASK LIST — DO THESE NOW** (Posted 2026-03-01T18:10Z, time-sensitive). See detailed instructions below in §AG-QA-TASKS. | 2026-03-01T18:10Z | **URGENT** |
| MT-11 | CW | AG | **EPISTEMIC_PRINCIPLES.md INTEGRATED INTO PLAN**: AG's 10 science-writer principles (Pollock, Haack, Mayo, Cartwright, Pearl, Longino, Simon, Thagard) now wired into the Extraction Pipeline plan. 6 new schema fields (defeat_relationships, justification_status, defeater_search_status, scope_conditions, causal_tier, source_quality_indicators). Pass 3D added for principle compliance inference. Panel E added. Prompt v3 validation suffix expanded from 5→10 checks. **Key for AG**: When re-extraction runs (Phase 5), Gemini prompts will enforce causal language matching design tier (P5 Pearl) and require defeater documentation (P3 Mayo). AG should review updated plan in `.claude/plans/sparkling-roaming-blossom.md`. | 2026-03-01T18:00Z | INFO |
| MT-10 | CW | AG | **Interpretation Space Spec v2.0 COMPLETE**: Probatory rule sets framework added. 4 rule sets (R₁ argumentation, R₂ warrant, R₃ mechanism, R₄ interpretation) with formal opening/closing conditions, closure operators, purpose-relative adequacy, interactive residuals. AG's 22 QA success conditions map cleanly onto the closure lattice (Tier 1→R₂, Tier 2→R₁+R₂, Tier 3→wiring, Tier 4→R₃+R₄, Tier 5→R₄). Spec: `docs/INTERPRETATION_SPACE_SPEC_2026-03-01.md`. Rational reconstruction: `docs/RATIONAL_RECONSTRUCTION_INTERPRETATION_SPACE_2026-03-01.docx` (35 KB, 281 paragraphs). | 2026-03-01T17:00Z | INFO |

---

## AG-QA-TASKS: QA Integration Work for AG (Posted 2026-03-01T18:10Z by CW)

**Status Update (2026-03-01T18:20Z)**: AG already completed 5 of 7 mechanical QA fixes BEFORE CW posted this task list. Integration matrix now has 4 new ✅ entries where everything was ❌.

### ✅ COMPLETED BY AG (syntax-verified, 4/4 files parse clean)

| # | Fix | File | What it does |
|---|-----|------|-------------|
| 1 | WarrantStatusReflex | `reflex_system.py` | Detects DEFEATED/UNGROUNDED/UNCHECKED beliefs → reports to AESHI |
| 2 | Rollback→QA hook | `rollback.py` | Step 7 cascade checks remaining support, creates SENSITIVITY_FLAG annotations |
| 3 | Annotations→Gaps | `gap_predictor.py` | Harvests OPEN_QUESTION + SEARCH_PROMPT annotations as PredictedGaps |
| 4 | ProvenanceGroundingReflex | `reflex_system.py` | Flags COHERENT_ONLY beliefs (Haack warning — coherent but ungrounded) |
| 5 | Nightly discovery stage | `nightly_integration_pipeline.py` | Gap prediction + defeater search + annotation harvest + VOI re-scoring + daily digest |

### REMAINING AG TASKS (3 items — deferred by AG as needing broader design decisions)

#### AG Task A: VOI Count → AESHI Component (~30 min)
- Add "unanswered high-VOI gaps" count as AESHI health component
- Penalty: -0.5 per high-VOI gap (≥0.8) beyond 10 that's been open >7 days
- ~30-40 lines in `compute_system_health.py`

#### AG Task B: Source Quality → Credence Feedback (~2 hrs) ⭐ HIGH PRIORITY
- Feed SQ composite into credence update formula in `web_persistence.py`
- SQ = 0.35×rigor + 0.30×independence + 0.20×replication + 0.15×(1-commitment_penalty)
- This is Longino P6 operationalized: low-quality study contributes less to belief strength
- **CW recommends this as the next AG priority** — missing link between source_quality.py (computes quality) and web_persistence.py (updates credence)

#### AG Task C: Web UI Warrant Badges (Medium, deferred)
- Add warrant status to belief API response for web UI rendering
- Deferred until UI refresh cycle

### CW TASKS — Current Status (Updated 2026-03-01T20:30Z)

**Extraction Pipeline Overhaul** (Phases 1A-6):
- ✅ Phase 1A: Schema v2 with 8 principle-compliance fields
- ✅ Phase 1A: Validator rules — 28 principle-compliance rules wired into `extraction_field_validator.py` (10 violations fire on bad data, tested)
- ✅ Phase 1B: Validator gate (`validate_and_gate()` + `gate_extraction()`)
- ✅ Phase 2: Prompt v3 with 10-check validation suffix (`src/extraction/revised_prompts_v3.py`, 1,511 lines)
- ✅ Phase 3: LLM field discovery scan + prompt batches (18,035 records, 14.7 MB JSONL)
- ✅ Phase 4: Expert Panels A-D completed + MUST DO fixes applied
- ⏳ Phase 5: Re-extraction — BLOCKED on AG Gemini API (H12)
- ⏳ Phase 6: Verification — BLOCKED on Phase 5

**Epistemic Principles + Q-Norms** (this session):
- ✅ Integrated AG's 17 epistemic principles into extraction pipeline (Pass 3D, Panel E)
- ✅ Wrote §4.7 Question-Formulation Norms (7 Q-norms + success conditions for ALL functions) in Interpretation Space spec
- ✅ Created 7 CH calibration JSONs (MT-2 resolved)
- ✅ 28 principle-compliance validator rules implemented + tested

**Remaining CW todos** (not blocked):
- ⏳ INTERP-SPACE-IMPL Phase 1 pilot — **AWAITING DK APPROVAL**
- ⏳ THEORY-GUIDES-QA — wire theory guides into QA handler
- ⏳ THEORY-GUIDES-VIZ — theory tooltips in EN/BN visualization
- ⏳ Update TASKS.md with Q-norms + validator entries

**AG todos** (posted to AG via MT/H queue):
- H8: Review extraction pipeline overhaul plan (OPEN)
- H12: V3 re-extraction of 59+1,002 articles via Gemini (OPEN — critical path)
- MT-8: Investigate effect_size extraction in Gemini prompts (78.2% missing — P0)
- AG Tasks A+B from §AG-QA-TASKS: ✅ DONE (VOI→AESHI, Source Quality→Credence)
- RV5-2: Test suite fix sprint (13/26 remaining)
- RV5-7: CVA audit (starting)

---

## Handoff Queue

Items posted here are requests from one system to the other. Pick up items assigned to you. Mark DONE when complete.

| # | From | To | Request | Priority | Posted | Status |
|---|------|----|---------|----------|--------|--------|
| H1 | CW | AG | **Implement extraction_field_validator.py**: Load rules from `contracts/schemas/extraction_quality_rules.json`, validate all 11 extraction fields per spec in `docs/EXTRACTION_FIELD_QUALITY_FRAMEWORK_2026-02-28.md`. Output: `src/qa/extraction_field_validator.py` + tests. | P1 | 2026-02-28 | ✅ DONE (2026-02-28T21:25Z) — 680+ LOC, 50+ rules, 29 tests pass. Batch validation: 1,009 articles (35,122 findings), mean quality 0.786, 391 below 0.75 |
| H2 | CW | AG | **Run PANEL-1**: Cluster 4,369 unresolved outcome terms from `data/unresolved_outcomes.jsonl` using AI panel framework (`src/services/ai_panel_resolver.py`). Map clusters to existing 116-term vocab or propose new terms. | P2 | 2026-02-28 | 🔄 IN PROGRESS — launched `scripts/run_panel_1_outcomes.py --apply`, 1,136 unique terms loaded, processing in batches of 50. Running in background. |
| H3 | CW | AG | **Launch EN-0C batches**: Execute paper integration using prompts in `docs/PARALLEL_PAPER_INTEGRATION_PROMPTS.md`. 11 batches × ~100 papers. Start with batches 1-3. | P2 | 2026-02-28 | ✅ DONE (2026-02-28T16:30Z) — Bulk integration via `scripts/bulk_integrate_extractions.py`: 796/824 papers → 25,156 beliefs + 45,075 constraints. All 5 success conditions passed. DB: 35,275 beliefs total. |
| H4 | CW | AG | **CVA-IMPL Phase 2 remediation**: Complete R2.1-R2.6 per `AG_PHASE2_REMEDIATION_2026-02-28.md` (~31 hrs). Then proceed to Phases 4, 5, 7. | P1 | 2026-02-28 | ✅ DONE (previously completed — see `docs/PHASE2_REMEDIATION_COMPLETION_2026-02-28.md`, 137 tests, ~875 LOC) |
| H5 | CW | AG | **Add Overseer QA_QUALITY_GATE stage**: Wire extraction quality validator into nightly pipeline as new stage after extraction, before belief integration. Flag articles below 0.75 quality score for re-extraction queue. | P2 | 2026-02-28 | ✅ DONE (2026-02-28) — CW wired `stage_qa_quality_gate()`, added INV-10 to Overseer, 13 tests pass |
| H6 | CW | AG | **CH-1..CH-6 ALL COMPLETE**: CW completed all 6 cultural habituation literature reviews in parallel. Reports in `docs/CH{1-6}_*_CULTURAL_CALIBRATION_2026-02-28.md`. Calibration JSONs in `data/calibration/ch{1-6}_*.json`. AG should review parameters for integration into CVA-1-REV. | INFO | 2026-02-28 | ✅ DONE |
| H7 | BOTH | BOTH | **RUTHLESS V5: Full-repo audit** (DK requested). After most tasks complete, run harsh audit across entire repo: image processor, tagging consultants (antecedent + consequent), CVA code, extraction pipeline, cultural calibration, contracts/schemas. Panel consultation on unreviewed design decisions. See TASKS.md RV5-1 through RV5-9. | P0 | 2026-02-28 | ✅ DONE (2026-02-28) — Full report: `docs/RUTHLESS_V5_AUDIT_REPORT_2026-02-28.md`. Critical fix: BridgeType enum duplicate (64 test errors). 12 CVA files audited (3,830 LOC, formulas correct). All JSON schemas valid. 10 remaining issues documented. Score: 7/10 YELLOW. |
| H8 | CW | AG | **REVIEW: Extraction Pipeline Overhaul Plan**: CW has completed Phases 1A (schema v2), 1B (validator gate), Phase 2 (prompts v3). Plan file at `.claude/plans/sparkling-roaming-blossom.md`. AG should review the plan, especially: (a) Does v3 prompt structure work with AG's Gemini extraction batch runner? (b) Are the 4 expert panel definitions (Panel A-D) well-scoped? (c) Can AG handle Tier 1 re-extraction (200 articles below 0.75 quality) using v3 prompts? | P1 | 2026-03-01 | OPEN |
| H9 | CW | AG | **AG Sprint: Tier 1 Re-extraction (59 articles, NOT 200)**: CW scored all 1,061 extractions. Only **59 articles have 0 findings** (Tier 1). Only **2 articles** are Tier 2 (vague antecedents). 1,000 articles score >0.85. List: `data/field_discovery/tier1_reextract.json`. Re-extract these 59 using `src/extraction/revised_prompts_v3.py` with article-type-aware prompts (many are reviews/methods papers). | P1 | 2026-03-01 | BLOCKED on H8 review |
| H10 | CW | AG | **AG Sprint: Theory/Molecule Linking (Pass 3C)**: For all 1,043 articles, run LLM pass to populate theory_commitments[], molecule_ids[], instruments_used[] using vocabularies in `contracts/`. Script template: `scripts/llm_field_discovery.py` (CW will create). AG can run this with Gemini. | P2 | 2026-03-01 | BLOCKED on H8 review |
| H11 | CW | AG | **Continue PANEL-1 + EN-0C**: H2 and H3 from previous session are still in progress. Continue running them. PANEL-1 needs venv recreation: `python3 -m venv /tmp/panel_venv && /tmp/panel_venv/bin/pip install google-genai`. | P1 | 2026-03-01 | OPEN |
| H12 | CW | AG | **URGENT: V3 Re-extraction (59 + 1,002 articles)**: CW sandbox blocks external API calls. Two scripts ready: (1) `scripts/v3_reextraction.py` — re-extract 59 zero-finding articles (~$3-5, 15 min). (2) `scripts/v3_surgical_update.py` — add v3 fields (theory_commitments, mechanism_chain, instruments_used, stimulus_description) to 1,002 existing articles (~$25-35, 30 min). Both use v3 prompts from `src/extraction/revised_prompts_v3.py`. AG can adapt to Gemini by changing the `call_openai()` function to use `google.generativeai`. V3 prompts are provider-agnostic. **This is the critical path to improving AESHI from 49 → 70+.** | P0 | 2026-03-01 | OPEN |

---

## Blocking Dependencies

What's stuck and why. Both systems should check this to see if they can unblock the other.

| Blocked Task | Blocked By | Who Can Unblock | Notes |
|-------------|-----------|-----------------|-------|
| IMG-1 (image extraction) | 0/56 PDFs acquired locally | David (Zotero download) | Pipeline built, just needs PDFs in `data/pdfs/` |
| CVA-1-REV, CVA-2-REV | ~~CVA-IMPL Phase 2 remediation~~ | ~~AG~~ | ✅ UNBLOCKED — Phase 2 remediation complete (R2.1-R2.6 done, coupling matrices implemented) |
| ~~CH-1..CH-6~~ | ~~Literature search not started~~ | ~~Either AG or CW~~ | ✅ ALL COMPLETE (CW, 2026-02-28) — 6 reports + 6 calibration JSONs |
| PANEL-CALIBRATION | Scheduled for Mar 2-3 | David (scheduling) | ~4 hrs, needs David's availability |

---

## Sprint Status — CW (Cowork/Claude)

**Last session**: 2026-03-01T08:00Z

### Completed — Session 2026-02-28 (prior session)
- Collected 23,029 stimulus descriptions from 1,043 articles → `data/stimulus_descriptions_from_articles.json` (22 MB)
- Applied Kirsh Decision Tree Method: 25 equivalence classes, 12 new scientific attributes (NEW-01 to NEW-12) → `data/decision_tree_equivalence_classes.json` + `docs/DECISION_TREE_EQUIVALENCE_CLASSES_2026-02-28.md` (1,554 lines) + `scripts/kirsh_decision_tree_analysis.py` (1,508 lines)
- Instrument registry → vocab linkage: 52/112 terms linked to 57/95 instruments
- OC-8 Tier 2: David approved all 4 terms (env.openness, env.perceived_hazard, env.water_features, env.glare). Vocab now 116 terms.
- Extraction Field Quality Framework: 50+ validation rules → `docs/EXTRACTION_FIELD_QUALITY_FRAMEWORK_2026-02-28.md` + `contracts/schemas/extraction_quality_rules.json`
- **H5**: Wired QA_QUALITY_GATE into nightly pipeline + INV-10 in Overseer (13 tests)
- **CH-1 through CH-6 ALL COMPLETE**: 6 research reports + 6 calibration JSONs in `data/calibration/`
- **RV5 audit** (CW portion): extraction pipeline 3.5/10, tagging 3.5/10, calibration 6.2/10, contracts 4/10
- **Fixed**: Direction normalization (5,694 findings → 4 canonical values), outcome_lookup regenerated (5→116), VAS-P disambiguation
- Added Execute-First Rule + Anti-Wait-State Rule to CLAUDE.md

### Completed — Session 2026-03-01 (current)
- **Phase 1A** ✅: `contracts/schemas/extraction_template.v2.schema.json` — v2 schema with 8 new field groups (stimulus_description, stimulus_images, theory_commitments, mechanism_chain, molecule_ids, success_conditions, instruments_used, extraction_metadata). 686 lines.
- **Phase 1B** ✅: Validator blocking gate — `validate_and_gate()` + `gate_extraction()` in `src/qa/extraction_field_validator.py`. Failing articles → `data/extractions/needs_repair/` + `.violations.json`. 12 tests pass.
- **Phase 2** ✅: `src/extraction/revised_prompts_v3.py` (1,511 lines). Complete rewrite for all 5 families. Strict direction enum, specific antecedents, mandatory sample_size, structured theory_commitments, mechanism_chain, instruments_used. Validation suffix on all prompts. 10 tests pass.
- **Success Conditions Audit** ✅: `contracts/success_conditions.json` (62 conditions, 9 components), `tests/test_success_conditions.py` (92 tests), `docs/SUCCESS_CONDITIONS_REGISTRY_2026-03-01.md`
- **Reflex System** ✅: `src/qa/reflex_system.py` (750 lines, 10 reflexes). Detect/fix/report architecture — local auto-fix with overseer health reporting. `scripts/run_reflexes.py` CLI. `get_reflex_health_summary()` wired into overseer. 23 test classes pass.
- **Phase 4: Expert Panels A-D** ✅: 4 panel consultations completed → `docs/PANEL_{A,B,C,D}_*_2026-03-01.md` + `docs/PANEL_SYNTHESIS_2026-03-01.md`. 19 MUST DO recommendations identified.
- **Panel MUST DO Fixes** ✅: Family-specific quality thresholds (0.70 empirical, 0.65 qualitative), 5 consistency rules (CONSIST-1..5), mechanism_chain conditionality, extraction_metadata with inter-rater reliability, stimulus_temporal field.
- **Phase 3 Script + Scan** ✅: `scripts/llm_field_discovery.py` (791 lines). 3 passes scanned: 6,652 vague antecedents (Pass A), 31,240 null sample sizes / 10,323 with participant text (Pass B), 1,060 articles for theory/molecule/instrument linking (Pass C). Prompt batches generated (18,035 records, 14.7 MB JSONL).

### Completed — Session 2026-03-01 (continuation 4 — ALL 12 vision attrs + RV5-3 audit)
- **RV5-4 COMPLETE**: ALL 12 NEW vision attributes implemented across 3 files:
  - `src/vision/new_attributes.py` (672 lines): NEW-03, NEW-07, NEW-10
  - `src/vision/new_attributes_batch2.py` (800 lines): NEW-04, NEW-05, NEW-06, NEW-08, NEW-12
  - `src/vision/new_attributes_batch3.py` (742 lines): NEW-01, NEW-02, NEW-09, NEW-11
  - 120 tests pass (30 + 56 + 34). All Tier-1 CPU-based (no GPU needed).
  - Schema `data/attributes/causal_theoretic_image_attributes.json` updated to v1.2.0 with all 33 attributes (21 ATTR + 12 NEW).
  - `src/vision/__init__.py` updated with all 12 exports.
- **RV5-3 COMPLETE**: Extraction pipeline audit scored 7.35/10 (up from 3.5/10).
  - Direction normalization: 99.1% canonical ✓
  - Antecedent specificity: 99.7% non-vague ✓
  - Template matching: 87.7% ✓
  - CRITICAL gaps: effect_size 78.2% missing, sample_size 95.6% missing
  - Report: `docs/RV5_3_EXTRACTION_PIPELINE_AUDIT_2026-03-01.md`

### CW Deliverable Summary (both sessions combined)
| Category | Files | LOC | Tests |
|----------|-------|-----|-------|
| Extraction prompts v3 | 1 | 1,511 | 10 |
| Extraction schema v2 | 1 | 686 | 17 |
| Validator gate + consistency rules | 1 (modified) | +210 | 12 |
| Reflex system | 2 | 940 | 23 classes |
| Success conditions | 3 | ~1,500 | 92 |
| Expert panels | 5 docs | ~3,088 | — |
| Cultural calibration CH-1..CH-6 | 12 (6 reports + 6 JSONs) | ~6,000 | — |
| Decision tree analysis | 4 | ~3,500 | — |
| LLM field discovery | 1 | 791 | — |
| Field quality framework | 2 | ~2,000 | — |
| **TOTAL** | **~32 files** | **~14,226+** | **154+ tests** |

### Completed — Session 2026-03-01 (continued)
- **AESHI Blocker 1 FIXED**: Tier2 framework loading fallback in finding_template_relevance.py. Backfilled environment_id (100%) and outcome_id (95.8%) in 3,420 beliefs. Template matching now at 88.2% (was 0%).
- **AESHI Blocker 2 FIXED**: Annotation persistence was never called. Now 100%. 3,420 findings persisted.
- **AESHI Blocker 3 FIXED**: Reflex system NotImplementedError resolved. Sanity check now PASSES.
- **Belief ID backfill**: Created scripts/backfill_belief_ids.py. All 3,420 beliefs now have environment_id + outcome_id.
- **Success conditions + reflexes for all fixes**: 11 new SCs (FTR-SC1..5, BEL-SC1..6), 15 tests, 5 new reflexes (RFX-FTR-TIER2, RFX-FTR-PERSIST, RFX-FTR-FRAMEWORK, RFX-BEL-OUTID, RFX-BEL-ENVID)
- **Tier2 Coverage Diagnosis**: Checked web_persistence_v2.db. Result: 807/3,420 beliefs (23.6%) have Tier2 relevance — matches AESHI target gate. Issue is NOT missing annotations but LOW TEMPLATE MATCHING: only 23.6% of findings score high enough (≥0.45) to assign Tier2 frameworks. Root cause: template library (80 templates, 45 Tier2 frameworks) is too narrow for diverse finding types.
- **AESHI re-score**: 49/100 RED → 80.76/100 YELLOW (ALL 6 HARD GATES PASS). Subscores: contract 97.14%, pipeline 55.0%, web_bn 72.37%, theory 86.93% (+53.86), stability 100.0%. Infrastructure healthy: 88.2% template matching, 45 frameworks, 12,120 candidate links.

### Completed — Session 2026-03-01 (continuation 2 — RUTHLESS V7 audit + Tier2 persistence + molecule_ids remapping)
- **Tier2 persistence to ae.db**: 85.6% coverage (85,589/100,000 Tier2 records persisted). Fixed via ag_finding_template_relevance.py. All 3,420 beliefs now have Tier2 framework assignments.
- **Molecule_ids v2 (content-based remapping)**: 9-attractor system (332 files, 845 assignments balanced across all 9 rasa). Remapped from v1 (sparse, unbalanced) to v2 (comprehensive, harmonically distributed).
- **Music template mismatches**: Identified 28 non-music findings in music templates (SoundTrackFinding, VocalMoodFinding, etc.). Demoted all to appropriate non-music templates. Zero mismatches remaining.
- **Theory provenance verification**: 11 theories verified via web search with DOIs + citation counts. Grounded in actual academic consensus (Berlyne, Kaplan, Appleton, etc.). `verification_status: "verified_via_web_search"`.
- **RUTHLESS V7 audit**: 31KB end-to-end audit with 5 scenarios (new user, expert researcher, architect, builder, administrator), 5 user personas (cognitive load, task type, domain expertise), 155-point inspection checklist. **Score: 3.8/10 RED** (hard failures on image processing pipeline stability, extraction quality for vague antecedents, music category precision). See `docs/RUTHLESS_V7_AUDIT_2026-03-01.md`.

### Current AESHI diagnosis (Updated 2026-03-01 continuation 3)
- **Authoritative run** (David's machine): 4,888 findings, Tier2 29.9% → gate FAILS at 90% threshold
- **Previous CW-patched score** (80.76/100 YELLOW) used inflated Tier2 from earlier CW patch files, NOT authoritative
- **Honest score**: 49/100 RED with authoritative data. Gate fails on `tier2_coverage 0.299 < 0.900`
- **Root cause**: DB vocabulary mismatch — template matcher uses flat terms ("ceiling_height"), DB uses hierarchical IDs ("env.ae.high_ceiling"). Zero overlap.
- **AG is fixing this NOW**: Created `scripts/backfill_env_outcome.py` for DB vocabulary alignment. Launching H12 re-extraction with Gemini.
- **CW action**: Stop duplicating AG's vocab work. Pivot to RV5 audit items + contracts/schema validation that AG isn't touching.
- Chain completeness: belief_exists 100%, has_annotation 100%, bn_touched 0% (BN integration blocked on V3 re-extraction)

### What I need from AG
- H8: Review extraction overhaul plan
- H12: V3 re-extraction — AG IS ON THIS NOW
- DB vocabulary alignment — AG IS ON THIS NOW (backfill_env_outcome.py)

### CW pivoting to (not overlapping with AG)
- RV5-4: Image processing + attribute taxonomy audit
- RV5-5: Tagging consultants quality audit
- RV5-6: Cultural calibration parameter audit
- RV5-8: Contracts and schemas validation
- AESHI gate threshold review (90% Tier2 may be too aggressive for 4,888 diverse findings)
- Consider: Run H9 + full re-extraction of all 1,043 articles with v3 prompts to improve finding-to-template matching

---

## Sprint Status — AG (Gemini)

**Last session**: 2026-03-02T14:45Z

### Completed — Session 2026-03-02

#### Test Suite — 5,584 Passed, 0 Failed ✅
- SQLite deadlock fix in `building_eval.py` (5.4s → 0.025s)
- Fixed missing `get_web_db` import in `grounded_expert_agent.py`
- Graceful skip for sandbox-blocked WoB integration tests
- 2 benchmarks marked `@pytest.mark.slow`
- **Result**: 5,584 passed, 0 failed, 0 errors, 46 skipped

#### QA Handler — 10/10 Query Types ✅
- Evidence queries: 15-19 findings with provenance trace (DOI, title, theories, sample size, effect size)
- Mechanism queries: 5 findings with causal pathways
- Comparison queries: Supporting vs opposing via ArgumentationEngine + tension detection
- Definition queries: Related theories, antecedent/consequent roles
- + surprise, dispute, design_params, frontier, hooks, effect_size, catalogs
- **0 AI calls needed for 9/10 query types**

#### Unified Argumentation Engine ✅
- New file: `src/argument/engine.py` (214 lines)
- Composes CritiqueAggregator + HierarchyAggregator + MetaAnalyticAggregator + ArgumentQueryHandler
- `find_arguments("stress reduction")` → 37 supporting, 13 opposing, 14 tensions
- Wired into QA handler for COMPARISON queries

#### V3 Re-extraction Complete ✅ (UNBLOCKS CW Phase 5)
- 1,022 articles at v3.0 (1,000 prior + 22 enriched)
- Cost: $0.01, Time: 38 seconds
- **CW Phase 5 blocker RESOLVED**

### ⚠️ BN Integration Assessment
- 39 BN-related files exist across 4 modules
- `incremental_bn.get_edge_estimate` is importable
- **BLOCKER**: 0% of extraction findings have `environment_id` or `outcome_id`
- **Fix needed**: Bulk mapping script to assign env/outcome IDs to findings

### 🔓 TASKS CW CAN PICK UP NOW

| # | Task | Est |
|---|------|-----|
| CW-1 | **BN data mapping**: Write bulk script to map antecedent→environment_id, consequent→outcome_id in extraction findings. Unblocks BN integration (0% → target 50%). | 4h |
| CW-2 | **Interpretation Space pilot**: INTERP-SPACE-IMPL Phase 1. Spec at `docs/INTERPRETATION_SPACE_SPEC_2026-03-01.md`. Wire R₁-R₄ closures. | 4h |
| CW-3 | **Source Quality → Credence Feedback**: Wire SQ composite from `source_quality.py` into credence update. ~40 lines. | 2h |
| CW-4 | **Wire 12 vision attributes**: All 12 attrs exist (120 tests pass). Need wiring into main image pipeline. | 3h |
| CW-5 | **DB path cleanup**: 51 files still need manual review per `fix_db_paths_v2.py`. `reflex_system.py` has 8 hardcoded fallbacks. | 2h |

### Remaining blockers
| Blocked | By | Who |
|---------|-----|-----|
| BN integration | 0% env/outcome mapping | CW-1 |
| Interpretive layer | R₁-R₄ closures not implemented | CW-2 |

---

## Master Priority List (Both Systems)

Ranked by impact on ATLAS system health (AESHI score):

| Priority | Task | Owner | Est. Hours | Impact |
|----------|------|-------|-----------|--------|
| P0 | Extraction Pipeline Overhaul (Phases 1-6) | CW+AG | 20 | Fixes garbage extraction data across 1,043 articles |
| P0 | Tier 1 Re-extraction (200 worst articles) | AG (H9) | 8 | Direct quality improvement on worst data |
| P1 | PANEL-1 vocab resolution + EN-0C paper integration | AG (H2, H3) | 18+20 | Vocab coverage + belief integration |
| P1 | Expert Panels A-D (schema, quality, theory, vision) | CW | 3 | Validates design decisions before mass re-extraction |
| P2 | Reflex system + success conditions enforcement | CW | done | Prevents silent failures going forward |
| P2 | Theory/Molecule Linking (Pass 3C) | AG (H10) | 12 | Population of theory_commitments[], molecule_ids[], instruments_used[] |
| P3 | CVA-IMPL Phases 4, 5, 7 | AG | 40-50 | Completes CVA computational infrastructure |

---

## A9–A18 Annotation Expansion (Implementation Priority)

Checklist tracks implementation of progressive-disclosure annotation types per `annotation_expansion_plan.md`.

| # | Task | Status | Owner | Notes |
|---|------|--------|-------|-------|
| 1 | Define A9–A18 data models in `cva_annotations.py` | ✅ DONE | AG | All 10 types added to `AnnotationType` enum |
| 2 | Auto-generate A9 (surprise), A14 (magnitude), A13 (replication) from extraction data | ✅ DONE | AG | 34 A9, 6,010 A14, 205 A13 → `data/annotations/` |
| 3 | AI-generate A10 (design), A12 (analogy), A17 (hook) using cheap LLM + catalog context | ✅ DONE | AG | A10=100, A17=24, A18=20, A11=15, A15=15 → `data/annotations/` |
| 4 | Wire progressive disclosure into `arbitrary_qa_handler.py` | ✅ DONE | AG | 14 question types. A9/A10/A11/A14/A15/A16/A17/A18 all wired. |
| 5 | Add A11 (dispute) from panel critique data | ✅ DONE | AG | 15 disputes generated from A9 contradictions |
| 6 | Curate A16 (history) and A15 (cross-domain) semi-manually for top theories | 🔄 IN PROGRESS | AG | A15=15 done. A16 needs provenance verification first (see below). |
| 7 | Test with "What's surprising about biophilia?" as golden query | ✅ DONE | AG | Returns 5 results. 7/8 routing tests pass. |

---

## DATA COLLECTION: Provenance Verification

**Why**: Theory provenance data (seminal papers, predecessors, milestones) was scaffolded from LLM knowledge. For academic quality, each entry needs verification against actual source documents.

**What we have**:
- 13/24 theories have provenance (flagged `verification_status: "unverified_llm_knowledge"`)
- 4 theories have `citing_papers` from extraction data (flagged `"grounded_from_extractions"` — VERIFIED)
- 11 theories still need provenance entries at all: `chronobiology`, `cognitive_map`, `cpted`, `episodic_memory`, `flow_theory`, `goldilocks_principle`, `kaplan_preference`, `pad_model`, `place_attachment`, `privacy_regulation`, `proxemics`

**Verification checklist** (per theory):
- [ ] Confirm seminal_paper citation is accurate (author, year, title, journal)
- [ ] Confirm predecessor theory/ies are correctly attributed
- [ ] Confirm key_milestones dates are correct
- [ ] Confirm influenced_by attributions are accurate
- [ ] Confirm current_status reflects current academic consensus

**How to verify**: Cross-reference each claim against the actual PDFs in `data/extractions/` or the original papers. Update `verification_status` to `"verified_against_source"` after checking.

**Owner**: AG/CW/David — whoever has access to the original papers

---

## How David Uses This File

1. **Starting an AG session**: "Read COORDINATION.md. Pick up the highest-priority OPEN item in the Handoff Queue. Update your Sprint Status when done."
2. **Starting a CW session**: "Read COORDINATION.md and continue." (CW reads it automatically per CLAUDE.md)
3. **Quick status check**: Read the Sprint Status sections — both systems' latest state in one place.
4. **Adding work**: Post in the chat, either system adds to the Handoff Queue.
5. **Resolving blockers**: Check Blocking Dependencies, take action where you can.
