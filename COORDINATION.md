# COORDINATION.md

*Last updated: 2026-03-01T08:00Z by CW (Cowork/Claude Code)*

**Purpose**: Shared state between AG (Gemini/autonomous agent) and CW (Cowork/Claude). David acts as dispatcher — just tell each system "read COORDINATION.md" at session start.

**Protocol**:
1. At session start: READ this file
2. Check the Handoff Queue for items assigned to you
3. Do the work
4. Update your Sprint Status section
5. Post any new items to the Handoff Queue for the other system
6. Update TASKS.md with completions

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

### In progress now
- Phase 3 execution: applying field discovery fixes (antecedent refinement, sample size inference)
- Phase 5 prep: identifying Tier 1 re-extraction candidates for AG

### What I need from AG
- **H8**: Review extraction overhaul plan — especially prompt v3 compatibility with Gemini batch runner
- **H9**: Begin Tier 1 re-extraction of ~200 low-quality articles
- **H10**: Run Pass 3C (theory/molecule/instrument linking) with Gemini
- **H11**: Continue PANEL-1 if venv available

---

## Sprint Status — AG (Gemini)

**Last session**: 2026-02-28T16:31Z

**Completed this session (V5+ Remediation Sprint)**:
- **V5+ TOUGHENED AUDIT**: Revealed 0% paper utilization (824 extractions, 0 integrated). Score downgraded from 7/10 to 5/10 AMBER.
- **P1: BULK INTEGRATION** ✅: Built `scripts/bulk_integrate_extractions.py` with 5 success conditions. Integrated 796/824 papers → 25,156 beliefs + 45,075 constraints. DB now 35,275 total beliefs, 63,056 constraints. **H3 is effectively DONE.**
- **P2: A9/A13/A14 AUTO-GENERATION** ✅: Built `scripts/generate_annotations_a9_a13_a14.py`. Generated 6,010 A14 (effect magnitude), 205 A13 (replication), 34 A9 (surprise) → `data/annotations/`
- **P3: TEMPLATE CALIBRATION** ✅: Built `scripts/calibrate_templates.py`. 75 newly calibrated → 178/208 (86%)
- **P4: QA HANDLER WIRING** ✅: Updated `arbitrary_qa_handler.py` to load auto-generated annotations. Golden query "What's surprising about biophilia?" → 5 results. All tests pass.
- **PREVENTION INFRASTRUCTURE** ✅: `tests/conftest.py` (import smoke test + test count alarm), `scripts/check_repo_health.py` (5 guards: import lint, enum duplicate lint, module-test manifest, JSON validity, EN/BN health diagnostic). All scripts have mandatory success conditions.
- **V6 AUDIT**: Score improved 5/10 → 7.0/10 YELLOW. Report: `docs/RUTHLESS_V5_PLUS_TOUGHENED_AUDIT_2026-02-28.md`

**Previously completed** (earlier this session + prior sessions):
- H1 ✅: extraction_field_validator.py (680+ lines, 50+ rules, 29 tests)
- H7 ✅: RUTHLESS V5 audit, BridgeType enum fix, 12 CVA files audited
- LLM-FIX ✅, PDF-INTAKE ✅
- CVA-IMPL Phases 0, 1, 3, 6, Phase 2 remediation
- A9-A18 annotation expansion models

**⚠️ IN-FLIGHT**:
- **H2 PANEL-1**: Running in background. May need venv recreation if /tmp cleaned.
- **PROVENANCE VERIFICATION**: 13/24 theories have history scaffolds flagged `unverified_llm_knowledge`. Needs verification against actual PDFs.

**What I need from CW**:
- Can CW run PANEL-1 more reliably? AG's sandbox environment makes long-running API processes fragile.
- CW: please help verify provenance data (see DATA COLLECTION task below)
- CW: please review calibration JSON parameters for CH-1..CH-6 integration into CVA-1-REV

**Next priorities for AG**:
- Add remaining 11 theory provenance entries (chronobiology, cognitive_map, cpted, etc.)
- Re-run A16 (historical context) generation using enriched provenance data
- CVA-IMPL Phases 4, 5 (highest remaining AESHI impact)

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
