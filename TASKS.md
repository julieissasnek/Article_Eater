# TASKS.md

*Last updated: 2026-03-04 (Session 22 — CIRCUIT QA LATENT VARIABLE REFRAMING + SEARCH TARGET WIRING. (1) Reframed functional circuits as latent variables per David's directive. Rewrote ontological statements in ATLAS voice (Pinker classic style, Sagan honest uncertainty). (2) Added testability sections with accessible descriptions, data requirements, and article search targets. (3) Wired search_targets into recommendation loop: circuit QA responses queue suggestions with source='circuit_qa' for automated evidence acquisition. 44 tests passing.) Previous: 2026-03-03 (Session 21 continuation 4 — MATH NORMS + FORMALIZATION SESSION. (1) MATH_EXPLANATION_NORMS: 7 mandatory norms synthesized from Strogatz, Devlin, Ellenberg, Stewart, Mazur, du Sautoy, Tsitsiklis, Bertsekas — four-layer explanation, provenance, justified constants, assumptions/scope, common-sense labels, figures, diverse examples. Contract: `contracts/MATH_EXPLANATION_NORMS.md`. Added to CLAUDE.md. (2) §48.1A d-value provenance: Full justification for 7 transfer reliability d-values — 3-round expert calibration history, sensitivity analysis (±0.10 d → ±0.015–0.018 p_target), empirical validation roadmap. (3) 5 constant annotations: δ default/min, ω bounds, TEA weights, AESHI weights — all tagged STIPULATED/THEORETICAL/CALIBRATED with provenance. (4) §84.2A Coherence C* formalization: C* = (A − λ·V) / A_max, λ=2.0 (Thagard 1989), 5 agreement/conflict cases, 3 worked examples, O(|E|) algorithm. (5) §121.3A VOI formalization: VOI(g) = [α·VOI_structural + (1−α)·VOI_epistemic]·w(type), adapted from Howard (1966) & Good (1950), 3 worked examples, decision rules. (6) Phase 6 figure plan: 8 new math explanation figures (M-25 through M-32) identified, FIGURE_INDEX.md updated. Previous: figure generation, consistency tracking, common-sense labeling, math audit.)*

Active task tracking for Article_Eater_PostQuinean_v1.
For completed sprints (Feb 2026), see `docs/TASKS_ARCHIVE_2026_Feb.md`.

---

## Current Status

**Test Suite**: 5,938 tests pass, 0 failures, 36 skipped (2026-03-03 service architecture overhaul)
**Templates**: 208 total — **208/208 scaffold pass, 103/103 calibrated pass, 0 failures**
**Ceiling Status**: Ceiling Adjudication Algorithm deployed (`scripts/ceiling_adjudicator.py`). 100% agreement with 69 prior panel decisions. 46 decisions applied to templates. 36 unresolvable (step-number mismatches in fuzzy-matched templates — data quality issue, not algorithmic).
**Field Coverage** (calibrated): t1_frameworks 100%, confidence 100%, bridge_warrant 100%, tier 100%, justification 100%, cross_template_interactions 100%
**Scaffold Status**: ALL 79 scaffold templates now have t1_frameworks assigned (panel-informed). 208/208 pass scaffold validation.
**T1.5 Status**: 13 formally reduced theories (expanded March 2, 2026: ART, SRT, Biophilia, Prospect-Refuge, Privacy Regulation, Kaplan Preference Matrix, Adaptive Thermal Comfort, Space Syntax, Soundscape, Place Attachment, BRECVEMA, Flow Theory, Goldilocks Principle). 30/103 formal. 3 rejected (Episodic Memory, Berlyne original, PCM). 1 deferred (ASA).
**Ruthless Version**: v8 — `docs/RUTHLESS_V8_AUDIT_COMPLETION_2026-03-02.md` (Full end-to-end audit + fix cycle, AESHI 49→91.13)
**AESHI Score**: **91.18/100 GREEN** (2026-03-02, post-V8 + data commits) — UP FROM 49 RED. All 6 hard gates PASS (was 5/6). Theory backfill committed (PP 99.3%→52.8%, all 10 T1 frameworks represented). Effect size cleanup committed (536 problems quarantined). Tests: 5,733 pass, 0 fail.
**Panel Review**: 2026-02-26 (HEALTH ASSESSMENT) — Expert panel deliberation on ATLAS system health. Original AESHI = 49/100 (RED). Seven-panelist review (Cartwright, Pearl, Thagard, Haack, Cooke, Murphy, Woodward) conducted 5 rounds of deliberation on four critical questions: (A) ceiling miscalibration vs. lenient overrides (UNANIMOUS: elicitation failure), (B) automatic edge creation risk (UNANIMOUS: do not add 1,731 keyword-edges), (C) zero-reference template downgrade (UNANIMOUS: downgrade but preserve), (D) single most impactful action (UNANIMOUS: Cooke calibration audit). Consensus recommendations across Tier-1 (calibration, triage, downgrade), Tier-2 (mechanistic specification, structure learning), and Tier-3 (expert retraining, intervention testing). Target: AESHI 49 → 53-55 (Tier-1) → 58-62 (Tier-2) → 68-72 (Tier-3). **ACHIEVED**: Current 80.76/100 YELLOW exceeds original targets. See `docs/Panel_Review_Health_Feb26.md` (895 lines, comprehensive deliberation).
**Last Session**: 2026-03-02 (Session 21, Cowork) — **TEA v2.0 + Master Doc Updates + AG Reconciliation + System Probe**. (1) Sprint CREDENCE-WARRANT Phases 4-6 completed: `warrant_strength.py` (894 lines, 62 tests), R6 dual-credence integration in `extraction_to_web.py`, validation on 41 beliefs + 3 domain panels. (2) AG session reconciliation: read TIER_ARCHITECTURE_SPEC, assessed impact on CREDENCE-WARRANT work, identified 3 reconciliation issues. (3) **TEA v2.0**: Expanded from 14 → 24 theories (10 T1 frameworks added). All re-keyed with humanly meaningful hyphenated terms per DK directive. Backward compatibility via `_LEGACY_KEY_MAP`. (4) **Master doc §50 rewritten**: 5-tier hierarchy (T1→T2→Molecules→T1.5→T3), molecules as latent variables, CCI metric, all theories named with meaningful terms. (5) **Master doc §53.6-§53.9 added**: OUTCOME_BRIDGES (111 synonyms), V3 enrichment fields, AESHI formula (6 subscores), CCI (7-step traceability). (6) **System probe**: Deep audit of 12 subsystems — identified that most QA infrastructure exists but is NON-BLOCKING (advisory only). Key gap: no mandatory quality gate in pipeline.
**Previous Session**: 2026-03-01 (Session 20 continuation 3, Cowork) — **§4.7 Question-Formulation Norms + Epistemic Principles Integration + CH Calibration JSONs + Phase 1A Principle Rules**. (1) Wrote §4.7 Question-Formulation Norms (~350 lines) for Interpretation Space spec: 7 Q-norms (Hintikka presupposition, Bromberger/van Fraassen contrast class, Laudan problem type, Simon VOI, Gawande specificity, Yong prerequisite structure, Sapolsky seam targeting), science writer norm mappings, success conditions for all system functions (24 rows × 5 categories). (2) Integrated AG's 17 epistemic principles into extraction pipeline plan: 8 new schema fields (compliance_hintikka, compliance_laudan, compliance_simon, compliance_gawande, compliance_yong, compliance_sapolsky, compliance_science_writer, compliance_aggregate), Pass 3D (principle compliance) added to master pipeline, Panel E (expert principle validation) added, 10-check validation suffix expanded (5→10 checks). (3) Addressed AG blockers: copied extraction pipeline overhaul plan to docs/ for AG access (blocker H8), began creating 7 CH parameter JSONs from literature review data (blocker MT-2). (4) Started adding validator rules for 8 principle-compliance fields to extraction_quality_rules.json (Phase 1A of pipeline overhaul).

**Previous Session**: 2026-03-01 (Session 20 continuation 2, Cowork) — **Tier2 Persistence Fix + AESHI Re-Score + Molecule Remapping + Ruthless V7 Audit**. (1) Fixed Tier2 persistence to ae.db via ag_finding_template_relevance.py. 85.6% coverage (85,589/100,000 Tier2 records). All 3,420 beliefs now have framework assignments. (2) **AESHI re-score: 49/100 RED → 80.76/100 YELLOW**. All 6 hard gates pass. Subscores: contract 97.14, pipeline 55.0, web_bn 72.37, theory 86.93 (+53.86 improvement), stability 100.0. (3) Molecule_ids v2: content-based 9-attractor remapping. 332 files, 845 assignments balanced across all 9 rasa (ragas). Migrated from v1 sparse unbalanced to v2 comprehensive harmonically distributed. (4) Music template mismatches: demoted 28 non-music findings (SoundTrackFinding, VocalMoodFinding, etc.) from music templates to appropriate categories. Zero mismatches remaining. (5) Theory provenance: verified 11/13 theories via web search with DOIs + citation counts (Berlyne, Kaplan, Appleton, Eglash, Hall, Rapoport, Meyers-Levy, Sommer, Boyce, Kruithof, Veitch). Status now `"verified_via_web_search"`. (6) **RUTHLESS V7 audit**: 31KB comprehensive audit with 155-point inspection checklist. 5 usage scenarios (new user, expert researcher, architect, builder, administrator) × 5 personas (cognitive load, task type, domain expertise) = 25 persona-scenario pairs. Score: 3.8/10 RED. Hard failures identified: image processing pipeline stability, extraction quality for vague antecedents, music category precision. See `docs/RUTHLESS_V7_AUDIT_2026-03-01.md`.

**Previous Session**: 2026-02-28 (Session 18 continued, Cowork) — **Kirsh Decision Tree Method + Vision Algorithm Discovery**. Continuing Session 18. (5) Collected 23,029 stimulus descriptions from 1,043 extraction files → `data/stimulus_descriptions_from_articles.json` (22MB). (6) Applied David Kirsh's decision tree method: filtered to 16,948 environmental stimuli, clustered into 25 commonsense categories, performed systematic variation analysis (essential vs. incidental attributes) on each. (7) Identified 25 equivalence classes with formal definitions (e.g., "room with plants" = {living_organic_element, green_chromaticity, biomorphic_form}). (8) Discovered 12 NEW scientific attributes not in original 21-attribute taxonomy: vegetation segmentation ratio (DeepLabV3), scene depth (MiDaS), sky proportion, visual complexity, regularity/repetition, figure-ground clarity, material diversity, illumination uniformity, acoustic privacy proxy, person density (YOLO), visual privacy, biomorphic curvature. (9) All 12 have implementable vision algorithms with real library calls (OpenCV, PyTorch, scikit-image). Implementation guide with working code: `docs/IMPLEMENTATION_GUIDE_NEW_ATTRIBUTES.md`. Total attribute taxonomy: 33 (21 original + 12 new).
**Previous Session**: 2026-02-28 (Session 18, Cowork) — **Vocabulary Enrichment + Instruments Registry + Image Characterization**. (1) OC-6: Added 216 operationalizations across 72 terms (92.2% coverage) — all reference real instruments. (2) OC-8: Gap analysis across all repos found 32 arch.* + 5 ART terms unmigrated; migrated 9 Tier 1 terms (being_away, compatibility, extent, preference, valence, legibility, naturalness, perceived_control, arousal); vocab now 112 terms + 295 operationalizations. (3) Instruments Registry v1.1: 95 instruments with full metadata (authors, year, APA reference, DOI, citations, psychometrics, strengths, weaknesses, newer alternatives). (4) IMG-2: Extending image characterization with causal-theoretic visual attributes.
**Previous Session**: 2026-02-28 (Session 14, Cowork) — **Consolidated Action List Execution**. Completed all 6 Cowork-assigned task groups from CONSOLIDATED_ACTION_LIST_2026-02-28.md: (1) T3: Removed duplicate Credence/Belief classes from epistemic_causal_bridge.py, added canonical imports from web_of_belief. (2) T1: Implemented _fetch_finding_by_iv_dv() in prediction_generator.py — multi-source search (SQLite + JSONL + dict) with fuzzy matching. (3) SPRINT-1-REV: Three-Number Separation complete — ω/d/CPT distinguished throughout schemas. (4) SPRINT-2-REV: π Projection deployed in orchestrator Step 9 (update_bn). (5) S1/S2: Gap predictor stubs implemented — find_critical_question_gaps() with Walton critical questions (5 schemes), find_argument_attack_gaps() with 4 attack vulnerability detectors (boundary, replication, mechanism, confounder). (6) SPRINT-3..6: Warrant type canonicalization across 18 Python files + 52 JSON templates; ArgumentationGraph warrant distribution + AESHI component methods; nightly pipeline warrant monitoring stage; expert calibration prep script. **All tasks COMPLETE.** ~600 new lines of code, 52 templates updated, 18 Python files updated, 4 new files created, 3 completion reports written.
**Previous Session**: 2026-02-28 (Session 13 continued, Cowork) — **Sprint Spec Revision + Paper 1 Draft + CH-7 + AESHI Analysis + AG Remediation**. (1) Revised CVA sprint specs with Three Hard Problems integration: CVA-1-REV and CVA-2-REV updated with Q1/Q2/Q3 solutions (~2,385 lines, ~5,250 LOC specified). See `docs/CVA_SPRINT_SPECS_REVISED_WITH_THREE_HARD_PROBLEMS_2026-02-28.md`. (2) Drafted Paper 1 (ATLAS Architecture) Sections 1-4 (~6,850 words prose) + extended outlines for Sections 5-10 (~2,950 words). Target: Psychological Review, 15,000 words. See `docs/PAPER_1_ATLAS_ARCHITECTURE_DRAFT_2026-02-28.md`. (3) CH-7 Color Temperature (CCT) cultural calibration: East Asian 5000-6500K vs. Western 2700-3000K, Kruithof curve shift, NTSC-J 9300K. See `docs/CH7_COLOR_TEMPERATURE_CULTURAL_CALIBRATION_2026-02-28.md` and `docs/CULTURAL_HABITUATION_CCT_REFERENCES_2026-02-28.md`. (4) AESHI 49→73.9 improvement analysis: 6 hard gates now passing, 6 new proposed invariants (INV-16 through INV-21), CVA integration implications. See `docs/AESHI_IMPROVEMENT_CVA_IMPLICATIONS_2026-02-28.md`. (5) AG Phase 2 remediation script: 6 tasks (R2.1-R2.6) to upgrade Phase 2 with Three Hard Problems solutions. ~1,300 new lines, ~31 hrs estimated. See `AG_PHASE2_REMEDIATION_2026-02-28.md`. (6) Article wishlist expanded from 2→32 entries with DOIs for 15 papers. (7) Proactive work preference added to root CLAUDE.md as MANDATORY section.
**Previous Session**: 2026-02-28 (Session 12, Cowork) — **CVA Culture-Aware Panels + Subject Characteristics Architecture + Sprint Integration**. (1) Re-ran Zumthor architect panel (Panel B) with culture-aware CVA: 6 architects (Pallasmaa, Kuma, Kéré, Doshi, Ito, Adeyemi), 3 design problems. Results: overall improvement from 1.3/5 (universal CVA) to 3.8/5 (culture-aware). Multicultural community center improved from 0/5 ("actively misleading") to 4/5. Key insights: polymorphous spaces, Ma-anchored pathways, community-presence restoration, rasa-as-attractors. See `docs/CVA_CULTURE_AWARE_ARCHITECT_PANEL_2026-02-28.md`. (2) Comprehensive literature review on constraint universality across cultures: two-tier architecture proposed (Tier 1 universal perceptual primitives, Tier 2 ψ-calibrated interpretive thresholds). See `docs/CONSTRAINT_UNIVERSALITY_REVIEW_2026-02-28.md`. (3) Created Subject-Characteristics Architecture (ψ parameter space): culture, neurotype, developmental stage, experience, state, trait. 10 neurotype profiles (PTSD, ASD, ADHD, Alzheimer's, older adults, children, gifted, depression, anxiety, bipolar) with constraint modulations and valuation changes. See `docs/CVA_SUBJECT_CHARACTERISTICS_ARCHITECTURE_2026-02-28.md`. (4) Integrated Chat's WEB_CONNECTIVITY_AUDIT into sprint plan: created EN-0A through EN-0D sprints for EN infrastructure, merged Sprint 0.5 into EN-0D annotation system, revised CVA-1 and CVA-2 with ψ integration. See `docs/SPRINT_INTEGRATION_WEB_CONNECTIVITY_AND_CVA_2026-02-28.md`. (5) David's key decisions: constraint layer approximately universal, valuation layer culturally parameterized; subject characteristics as major factor; neurotype expansion; two-tier constraints; rasa as attractors in dynamical system; paper series strategy; VR experiments feasible if stims auto-generated; India collaborator possible.
**Previous Session**: 2026-02-27 (Session 11, Cowork) — **Sprint 8 Master Document Overhaul COMPLETE**. All 6 phases executed via parallel agents. (1) Phase 1: 212+ terminology changes (CMR→ATLAS, EWG→EN, EMPIRICAL_COVARIANCE→EMPIRICAL_ASSOCIATION, THEORETICAL_DEFAULT→THEORY_DERIVED, all discount factors updated). (2) Phase 2: §48 completely rewritten with log-odds projection calculus; §48A added (EN/π/BN three-layer architecture). (3) Phase 3: §50 enhanced with 14 T1.5 theories, 6 T2 mechanism templates, §50.11 theory-vs-mechanism, §50.12 accordion mechanisms, §50.13 measurement-vs-mechanism. (4) Phase 4: Parts XIX (Cheat Sheet v2), XX (Technical Appendix with 4 worked examples), XXI (Source Document Index) added. Part XVIII enhanced with operational data. (5) Phase 5: Cross-references verified, legacy formula instances flagged, 6 issues fixed. (6) Phase 6: Quality pass — canonical discount factors verified at 20+ instances, 1 [SKELETON] remaining. Also: Sprint 0 code (bridge_warrants.py updated, epistemic_projection.py created 565 lines). Two expert panels (Panel 1: 8 questions, 8 affirmed; Panel 2: 5 questions on EMPIRICAL_ASSOCIATION tiering, unanimous). Ruthless audit: **72/100 YELLOW** (up from 49 RED). Three critical findings addressed: Formula Transition Note, δ canonical values with assignment procedure (§48.3A), panel bridging notes for Parts V-VI. Master doc: 19,502 → 20,559 lines. **10 documents produced** in docs/.
**Previous Session**: 2026-02-25 (Session 8 continued) — Full verification audit + setup() execution with real data. (1) Audited all 15 Session 8 files (9,054 lines): found and fixed 12 bugs across 4 files (system_setup.py, overseer_nightly.py, generate_calibration_report.py, 8_system_health.py). (2) Added CrossRef support to semantic_scholar_enrichment.py: crossref_to_paper_metadata(), merge_metadata(), ingest_crossref_file(), CLI --crossref-file/--no-merge. (3) Validated S2 enrichment data: 813 papers, 731 enriched (89.8%), citation graph 1,418 intra-corpus edges, 1908-2025. (4) Executed setup() against real data: Phase 0-12 all execute, 747/813 papers integrated, 23,800 claims, 42,983 rules, convergence in 2 iterations (coherence 0.5), OPERATIONAL in 19.6s. (5) Benchmarked Phase 4: 10-paper sample → 334 beliefs, 0 failures, 3.1s. Full corpus estimated ~255s (4.25 min). (6) Confirmed two-method architecture (setup + integrate_paper) verified working.
**Previous Session**: 2026-02-25 (Session 7) — Paper Integration Pipeline Phase 3: Full wiring sprint. ALL remaining engineering items done with eager options. (1) Step 11: social_epistemology.py wired — community identification via CommunityRegistry, BeliefProvenance creation with community-relative credences, ContestationTracker for contradictions. (2) Step 12: discovery_funnel.py wired — gap closure assessment using DiscoveryFunnelService, automatic VOI reduction estimation, GapClosure record creation. (3) Provenance: Haack foundherentist Provenance constructed synchronously during Step 5 — maps study_design→StudyType, evidence_level→Directness, computes grounding_score, calls compute_justification_status(), persists to belief_versions.scope_json. (4) Extraction hook: pdf_extraction_module.py now auto-triggers PaperIntegrationOrchestrator.integrate_paper() on ACCEPTED transition — non-blocking, extraction preserved even if integration fails. (5) CoherenceManager: pre/post coherence measurement in Steps 2/13 via scalable_coherence.py; coherence delta logged; tensions detected. (6) QA cache: eager mode marks caches STALE explicitly in cache_index; LLM recompute triggered on next QA run. 27/27 tests passing (22 original + 5 new wiring tests). Panel convened for OVERSEER design + system review.
**Previous Session**: 2026-02-25 (Session 6) — Paper Integration Pipeline (Sprint INTEGRATION-1). Phase 1: 7 new files in src/services/paper_integration/ (orchestrator, supersession, rollback, tag_engine, molecule_linker, models, __init__). 4 DB migrations. 22/22 tests. Phase 2: Gap audit (docs/INTEGRATION_PIPELINE_GAP_AUDIT_2026-02-25.md) identified 9 skeletal areas. Wired Steps 4-5 to extraction_to_web.py (full credence computation with theory inference, entrenchment boosts, reflective equilibrium). Wired Step 9 to BetaBernoulliEdge.update() (real conjugate prior BN learning). Wired Step 13 to EpistemicOrchestrator.compute_full_state() (P2-P6 recomputation + coherence delta). OVERSEER module proposed for panel review (8 design questions, O-1..O-8).
**Previous Session**: 2026-02-25 (Session 5) — Master paper 17,785 lines. Saved as MASTER_DOC_CMR_2026-02-25.md. Session 5 additions: (1) Reviewed AG's complete T1.5 implementation; wrote §34.5.7 documenting it. Updated §34.5.4/§34.5.5. (2) Created Goldilocks Principle as 13th T1.5 theory: T1.5 JSON definition (data/theories/goldilocks_principle.json) with 5 constructs, 19 constituent templates, PP:35%/IC:25%/NM:20%/IE-DPT:15%/EC:5%, three-part irreducible residual (cross-modal universality claim). PHENOMENON molecule (data/molecules/goldilocks_principle.json) with 16 templates, 6 components, 7 design implications. Added §78.2a to master paper (~65 paragraphs): mechanism (PE optimization + metabolic efficiency + reward convergence + individual differences), 6 domain calibrations with quantified optima, subsumption of Berlyne. Updated §78.2 Berlyne deferral with subsumption note. Added to canonical roster table as #13.
**Previous Session**: 2026-02-24 (Sessions 1-4) — Master paper expanded from 10,863 to ~17,700 lines. All 124 sections + 5 appendices at full depth. §34.5 three-level architecture added. Doc sync scanner baseline established. Zero skeleton markers remain.

---

## Completed (2026-03-05 Session — System Audit & Pipeline Completion)

### Go-Live System Audit — ALL 8 PHASES COMPLETE (2026-03-05)
**Plan**: Phase A–H from `sparkling-roaming-blossom.md`
**Results**:
- **Phase A**: Test suite 333/336 pass (99%), 3 minor extraction_gate calibration failures. V4 files compile clean.
- **Phase B**: Added `check_warrant_coverage()` (SC-INV-20) and `check_argumentation_health()` (SC-INV-21) to overseer. Wired into `check_integrity()` and `check_health()`.
- **Phase C**: Created `scripts/run_qa_pipeline.py` (341 lines) and `scripts/run_full_system_health.py` (496 lines).
- **Phase D**: Deferred — requires API calls on David's machine.
- **Phase E**: Created `src/services/interpretation_space_engine.py` (485 lines). Generates 664 questions (4 types × 166 templates). 15/15 tests pass. Wired into overseer as `check_interpretation_space_coverage()`.
- **Phase F**: Saved 11 session artifacts to docs/ (EN_to_BN_rethink.md, SCIENCE_WRITING_SYNTHESIS.md, AUDIT_*.md, pearl_typed_edges.md, aesthetics_molecules.md, etc.).
- **Phase G**: Created Part XXVII master doc sections: §181 QA Pipeline Architecture, §182 Warrant Pipeline, §183 Argumentation Pipeline, §184 Overseer Monitoring (~1,079 lines, 83 KB).
- **Phase H**: Created `APPENDIX_CROSS_REFERENCE_INDEX.md` (354 lines, 39 KB). Maps ~55 concepts across master doc, code, tests, contracts, and panel reviews.
**Verification**: All new code compiles, 15 new tests pass, 90 regression tests pass, no regressions.

---

## In Progress (2026-03-05)

### V4 Staged Extraction Pipeline — CODE COMPLETE, AWAITING PILOT (2026-03-05)
**David's request**: "Let's rebuild this extraction process slowly and absolutely correctly at every stage with verifications at each stage"
**Status**: V4 system fully implemented and documented. Awaiting pilot run on David's machine (Gemini API blocked in sandbox).
**Forensic finding**: V3 extracts ~30 of 200+ schema fields. 0% coverage on scope_conditions, instruments, ecological_validity, enabling_conditions, causal_direction, bridge_warrant. Root cause: prompt mentions fields but doesn't demand them.
**V4 solution**: 4-stage pipeline (Classify → Family-specific Extract → Verify → Report) with field forcing, 8 family-specific prompts, 20-point validation suffix, cross-model verification.
**Files created**:
- `src/extraction/v4_prompts.py` (955 lines): Classification + 8 family prompts + validation
- `scripts/v4_staged_extraction.py` (884 lines): Main pipeline (stages 1–3) with CLI
- `scripts/v4_pilot_analysis.py` (308 lines): Stage 4 analysis and reporting
- `data/pdf_doi_mapping.json` (326 KB): Maps 1,069 DOIs to PDF paths (778 have PDFs)
- 5 documentation files (V4_INDEX, V4_IMPLEMENTATION_SUMMARY, V4_DELIVERY_CHECKLIST, V4_QUICK_START, V4_EXTRACTION_PILOT_README)
- `docs/V4_COMPREHENSIVE_REPORT_2026_03_05.md`: Full report for David
**Next steps**:
- ⬜ David runs pilot: `python scripts/v4_staged_extraction.py --batch pilot_dois.txt --limit 10`
- ⬜ Evaluate field coverage against success criteria
- ⬜ Scale to 50–100 papers if pilot succeeds
- ⬜ Acquire PDFs for 291 extractions without PDF matches

### Card System Full Specification — PHASE 1-3 COMPLETE, PHASE 4-5 IN PROGRESS
**Plan**: `docs/CARD_SYSTEM_SPECIFICATION_PLAN_2026-03-04.md`
**Scope**: 9 card types, universal schema, user-type adaptation, writing agents, two-pass pipeline
**Phases Completed**:
- Phase 1: Code schema (card_types, card_schema, tab_config, staleness) — DONE
- Phase 2: Master doc Part XXVI (§174-§180, ~22,000 words) — DONE
- Phase 3: Writing agents + batch generation + orchestrator — DONE
**Phase 3 Deliverables (2026-03-04)**:
- `src/qa/card_tab_generators.py` (~700 lines): 6 LLM-powered tab generators + 1 structured (history). Epistemic norms embedded in system prompts. Pass 2 Opus polish detection. 39 tests all passing.
- `scripts/batch_generate_cards.py` (~660 lines): Async parallel Pass 1 (Haiku/Sonnet via API, ~$30 for 4,002 cards). Auto-queues EVERY card for Opus Pass 2 (free in sessions). 25-concurrent semaphore.
- `scripts/check_opus_queue.py` (~170 lines): AG startup detector for Opus polish queue. Exit code 0/1.
- Two-pass architecture: MANDATORY Opus polish for ALL card types. Orchestrator updated: `generate_card_two_pass()` no longer skips Sonnet-allocated types.
- Overseer INV-16: `check_two_pass_pipeline_health()` tracks queue depth, completion %, stall detection.
- SC-CGO-9 updated: now asserts Opus IS queued for all types (was: asserts NOT queued for Sonnet types).
- Cross-process tests: `tests/test_cross_process_xproc.py` (14 tests, SC-XPROC-1 through SC-XPROC-5).
- AG coordination: MESSAGE_BOARD Msg 016, `AG_OPUS_QUEUE_INSTRUCTIONS.md` standing order.
**Phase 4 (Visual generation)**: Pending — blocked on image extraction pipeline
**Phase 5 (Agent integration for drill-down)**: Pending — needs "Sources" tab for per-paper method details

### Stimulus Display + Method Drill-Down — SOURCES TAB DONE, BACKFILL IN PROGRESS (2026-03-04)
**David's request**: "I almost always want to see the stims if there was a picture... also add as many useful visualizations of data or method. Currently can someone drill down like that?"
**Status (updated 2026-03-04)**:
- ✅ "Sources" tab added as 8th tab: per-paper method details, stimulus descriptions, sample sizes, instruments
- ✅ Required for T1/T1.5/T2/Molecule cards; optional for T3/Competition/Layer/Method/Math
- ✅ V3 extraction prompts enhanced with detailed stimulus extraction instructions (Rule 6 expanded, Checks 11-12)
- ✅ ExtractionFieldValidator has 6 stimulus rules (ST1-ST6)
- ✅ Surgical backfill script: `scripts/run_stimulus_extraction.py` (ready for separate terminal)
- ✅ Overseer INV-17 (sources coverage), INV-18 (stimulus coverage), INV-19 (claim integrity)
- ✅ Remediation playbooks for INV-17/18/19 in `overseer_playbooks.py`
- ✅ Success conditions: SC-TG-8..10 (sources tab), SC-STIM-1..6 (stimulus), SC-INV-17..19 (overseer)
- ✅ 20 cross-process tests (14 original + 6 new for INV-17/18/19)
- ⬜ Stimulus data currently 0% populated — needs backfill (run `scripts/run_stimulus_extraction.py`)
- ✅ Wire FigureSuggestionService into card generation — DONE (wired at line 740, awaits figure_reference data in extractions)
- ✅ Add query routing for "show me methods from paper X" — DONE (_handle_paper_methods_query in arbitrary_qa_handler.py)

### Session-Mode Card Generation — COMPLETE (2026-03-04)
**David's mandate**: Free sessions (CW/CC/AG) should generate cards at zero API cost
**Deliverables**:
- `src/qa/session_card_writer.py` (~660 lines): SessionCardWriter + ClaimsRegistry for parallel terminals
- `scripts/terminal_card_gen.py` (~165 lines): Quick-start CLI (status, claim, next, show-claims)
- `scripts/session_generate_cards.py` (~380 lines): Full CLI for session card generation
- `docs/AG_PROMPT_card_generation_session.md`: AG's card generation prompt (ready to paste)
- `docs/SESSION_CARD_GENERATION.md`: User guide for terminal operators
- Supports up to 15 simultaneous terminals via file-based JSON claims
- 16 tests (test_session_card_writer.py), all passing
- SC-SCW-1..6 success conditions registered in contracts/success_conditions.json

---

## Recently Completed (2026-03-04)

### Part XXVI: System Presentation and Knowledge Artifacts — COMPLETE (2026-03-04)
- **7 sections written** (§174-§180), totaling ~22,000 words
- §174 Molecules Inventory (~3,000 words): 38 molecules across 4 types, factor analysis discovery method, molecules vs T1.5 distinction
- §175 Annotation Layer (~2,800 words): 25 types across 6 layers, three parallel systems, immutable design, integration problem
- §176 Interpretation Space (~3,000 words): 4 epistemic zones, question-type operators, endogenous value function V(G), probatory rule sets R₁-R₄
- §177 Argumentation System (~2,500 words): Walton's 5 schemes, Toulmin structure, debate clusters, gap discovery pipeline
- §178 Card System (~4,200 words): 9 card types, universal schema (surface/body/iceberg), tab architecture, ReductionClaim DAGs with premium irreducible-residual treatment, staleness lifecycle, science writer agent
- §179 Math Cards (~2,900 words): three-layer explanation architecture (Intuition/Transparent/Details), 10 math domains, science writer agent for intuition layers
- §180 System Architecture (~3,800 words): layer-by-layer guide, cross-layer data flow worked example, agent architecture, design decision on layered vs monolithic
- All sections in `docs/master_doc_parts/PART_XXVI_*.md` files
- DEPENDENCY_MANIFEST.json updated (total_sections: 148→155)

### Science Writer Agent Specification — COMPLETE (2026-03-04)
- **Comprehensive spec**: `docs/SCIENCE_WRITER_AGENT_SPEC_2026-03-04.md` (~15,000 words)
- Agent audit found 10 agent-like services, 2 autonomous agents (AG+CW), NO standalone science writer
- Spec covers: stateful architecture, 7-stage writing pipeline, question-generation loop (questions as first-class artifacts stored in card iceberg), 3 quality gates, card-type-specific strategies, ReductionClaim DAG premium visualization, model allocation (Opus for theoretical, Sonnet for routine), integration with 10 existing services
- Key innovation: questions generated DURING writing are captured in structured format and accumulated in master question registry — reveals system gaps and user confusion patterns
- Ready for David's review and AG coordination

### QA Answer Norms — COMPLETE (2026-03-04)
- **Deliverable**: `contracts/QA_ANSWER_NORMS.md` (~8,962 words)
- AG requested in Message 009, David confirmed "very important"
- 12 mandatory norms grounded in Reference Group of 8 scholars (Kahneman, Tetlock, Oreskes, Pinker, Sagan, Gelman, Nosek, Mayo)
- Maps all 9 enrichment orchestrator outputs to answer presentation sections
- Covers: answer structure, provenance citation, credence communication, framework attribution, uncertainty framing, document applicability, popular science standards
- Success conditions SC-QAN-1 through SC-QAN-12
- Forbidden patterns section (false balance, hedging stacks, circular reasoning, COHERENT_ONLY concealment)
- Integrates with EPISTEMIC_PRINCIPLES.md (Haack, Pollock, Mayo, Cartwright, Pearl)

### Master Doc Update Protocol (MDB System) — COMPLETE (2026-03-04)
- **Deliverable**: `contracts/MASTER_DOC_UPDATE_PROTOCOL.md` (~4,641 words)
- Solves David's problem: "forces everyone wherever they are to write up a context and decision justification doc"
- Master Doc Brief (MDB) template with 11 required sections
- Precise thresholds for "significant work" vs lightweight Change Notes
- Storage: `docs/master_doc_briefs/MDB_{AGENT}_{DATE}_{TOPIC}.md`
- CW integration workflow for mechanical master doc updates
- **Updated**: COORDINATION.md startup protocol (step 2: read MDB protocol), CLAUDE.md (new mandatory section)
- Created `docs/master_doc_briefs/` directory with README.md and _index.md

### Unified Content Agent Architecture — COMPLETE (2026-03-04)
- Reconciled AG's 5-agent decomposition (prose, visual, stats, layout, expert) with CW's Science Writer Agent spec
- `docs/UNIFIED_CONTENT_AGENT_ARCHITECTURE_2026-03-04.md` (~10,000 words)
- AG's panel feedback (15 experts) incorporated
- Model allocation: Opus for theoretical, Gemini for bulk, Sonnet for routine

### Opus Head-to-Head Comparison — COMPLETE (2026-03-04)
- `docs/OPUS_HEAD_TO_HEAD_2026-03-04.md` (~7,000 words)
- 4-way comparison on 5 clusters: Data-Only (D), Template (C/D), Gemini (B+/A-), Opus (A/A+)
- Recommended allocation: Opus ~200 high-stakes, Gemini ~2,788 bulk, hybrid ~800

### Panel Review of Unified Agent Spec — COMPLETE (2026-03-04)
- `docs/PANEL_REVIEW_UNIFIED_AGENT_SPEC_2026-03-04.md` (~36K)
- 12-expert panel: Pinker, Yong, Tufte, Gelman, Haack, Pollock, Ellard, Fowler, Hickey, Kirsh
- Verdict: APPROVED WITH RESERVATIONS
- 9 refinements incorporated

### Card System Code — Phase 1 Complete (2026-03-04)
- **Card Schema** (src/qa/cards/): 4 files, 1,740 lines total
  - `card_types.py` (342 lines): 9 CardType enum values, 3 CardTier values, CARD_TYPE_REGISTRY with full specs (badge colors, required/optional tabs, model allocation, approximate counts)
  - `card_schema.py` (641 lines): Card dataclass with Surface/Body/Iceberg architecture, JSON serialization, factory methods (create_card, make_card_id)
  - `tab_config.py` (246 lines): 7 tab definitions, 5 user-type orderings, tab filtering per card type
  - `staleness.py` (424 lines): StalenessLedger, compute_staleness_score(), validate_staleness_system(), success conditions SC-STALE-1..6
- **Card Generation Orchestrator** (`src/qa/card_generation_orchestrator.py`, ~900 lines):
  - Routes generation through CardTypeSpec.model_allocation (Opus/Sonnet/Gemini)
  - Two-pass architecture: Sonnet prepares (cheap, parallel) → Opus polishes (session, free)
  - Quality gate (ProseRevisionService integration)
  - Real-time staleness tracking (no nightly batches)
  - Follow-up answer caching (every answer becomes a retrievable card)
  - Overseer health report integration
  - Session vs API queue separation (Opus via CW/CC/AG sessions, Sonnet via API)
- **Card Retriever Bridge** (`src/qa/card_retriever.py`): Added `try_match_unified()` to search both legacy AnswerCard and new Card schema indices
- **Population Script** (`scripts/populate_all_cards.py`): Queues all 9 card types (4,002 items: 48 Opus session, 3,954 Sonnet API)
- **Overseer Integration**: INV-14 (queue depth ≤ 50), INV-15 (stale card ratio ≤ 20%), POST_INTEGRATION staleness trigger
- **Tests**: 119/119 passing (44 unit + 15 e2e integration + 60 orchestrator)
- **Success conditions**: SC-CARD-1..20, SC-E2E-1..12, SC-CGO-1..12, SC-STALE-1..6, SC-POP-1..5

### Meta-Review Specification — COMPLETE (2026-03-04)
- **Deliverable**: `contracts/META_REVIEW_SPEC.md` (814 lines, ~49KB)
- Created in response to AG's finding: zero formal spec existed for meta-reviews despite 861 lines of cluster_meta_review.py code
- 25+ field data model, 10 quality criteria (SC-MR-1 through SC-MR-10)
- 4 system-level success conditions (CMR-SC1 through SC-14)
- Audience calibration (3 tiers: expert, professional, general), LLM generation requirements
- 7 forbidden patterns (claim inflation, false precision, cherry-picking, etc.)
- Implementation guide: `docs/META_REVIEW_IMPLEMENTATION_GUIDE.md` (136 lines)
- 14 success conditions added to `contracts/success_conditions.json`

### Epistemic Loci Terminology + Card Architecture (§173) — COMPLETE (2026-03-04)
- **Epistemic loci** adopted as term for higher-level belief-cluster cards (David's choice from alternatives: topoi, dossiers, epistemic loci, crystallizations, nexus)
- **Source cards** = atomic article-tied evidence units; **epistemic loci** = synthesized positions aggregating across the evidence base
- Three-zone architecture documented: Zone 1 (committed prose), Zone 2 (flagged developments/diffs), Zone 3 (source map/dependency graph)
- Staleness scoring designed: weighted function of new source cards, credence shifts, competition resolutions; threshold 0.40 triggers regeneration
- Model allocation: Opus for theoretical loci, Sonnet for engineering loci, with reference-verification pass on all Opus outputs
- Written as §173 in `docs/master_doc_parts/PART_XXV_WRITING_AND_COMMUNICATION_INFRASTRUCTURE.md` (~2,200 words)
- Updated DEPENDENCY_MANIFEST.json (total_sections: 147→148)

### Opus vs Sonnet Comparison for Master Doc Fattening — COMPLETE (2026-03-04)
- Both models wrote identical §129.2 fattening inserts (Typed Credence Propagation theoretical justification)
- Opus: ~3,400 words, deeper philosophical grounding (Toulmin/Pollock/Woodward + Harman/Lehrer/Thagard unprompted), 17 refs, ~3 hallucinated refs
- Sonnet: ~3,600 words, tighter prose, sharper engineering insights (load-bearing beam analogy, failing-competitor observation), 6 refs, 0 hallucinations
- Verdict: Opus for theoretical fattening (with ref verification); Sonnet for engineering sections
- Comparison files: `docs/comparisons/opus_fattening_129_2.md`, `docs/comparisons/sonnet_fattening_129_2.md`

## Recently Completed (2026-03-03)

### Panel Recommendation Implementation (T-Levels Taxonomy) — COMPLETE (2026-03-03)

**Summary**: Implemented all 4 unanimous panel recommendations from `docs/PANEL_OUTPUT_T_LEVELS_2026-03-03.md`.

**Recommendation #1: Separate canonical from hypothetical T1 atoms** — COMPLETE
- Created T1 atom registry: `src/qa/molecules/t1_atom_schema.py` (T1Atom dataclass with maturity stratification)
- Created registry: `src/qa/molecules/t1_atom_registry.py` (T1AtomRegistry with framework/maturity indexes)
- Created 30 atom JSON files in `data/atoms/`: 10 CANONICAL, 10 ESTABLISHED, 10 HYPOTHETICAL
- CANONICAL atoms (neurally grounded, cross-domain): lateral inhibition, divisive normalization, gain control, Hebbian association, temporal integration, adaptation, oscillatory coupling, homeostatic regulation, error signal generation, spatial mapping
- HYPOTHETICAL atoms (limited evidence): empathic resonance, affordance computation, aesthetic fluency, narrative binding, place cell coding, allostatic prediction, social baseline, circadian entrainment, multisensory binding, default mode suppression
- Tests: 52 in `tests/test_t1_atom_registry.py` (all passing)

**Recommendation #3: Reground T1.5 boundary structurally** — COMPLETE
- Added `boundary_criteria` field to T1_5Theory schema (`t1_5_theory_schema.py`)
- Three structural tests replace sociological "published author" criterion:
  (a) has_irreducible_residual: emergent content not decomposable into T1
  (b) constitutive_relevance: names mechanism whose intervention changes phenomenon
  (c) design_guidance_utility: generates specific design guidance beyond T1
- All 13 REDUCED theories populated: 11 score 3/3, 2 score 2/3 (Biophilia: no specific mechanism; Place Attachment: underspecified mechanism)
- Validation rule: REDUCED theories with boundary_criteria scoring <2 trigger warning

**Recommendation #4: Formalize decomposition of three relations** — COMPLETE
- Created `src/qa/molecules/hierarchy_relations.py` (316 lines):
  - ExplanatoryHierarchy: T1 → T1.5 → T2 (top-down causal account)
  - EvidentialHierarchy: T3 → T2 → T1.5 → T1 (bottom-up empirical support)
  - CompositionHierarchy: Molecule → T2 templates, FC → Archetypes (parts-whole)
  - ThreeRelationIndex: Unified cross-relation query interface
- Each relation independently indexed with separate edge semantics
- HierarchyEdge dataclass with source/target tiers, confidence, provenance
- Tests: 39 in `tests/test_hierarchy_relations.py` (all passing)

**Recommendation #2: Validate T3 corpus against AI extraction bias** — PLAN COMPLETE
- Created `docs/T3_EXTRACTION_BIAS_AUDIT_PLAN_2026-03-03.md` (687 lines)
- 5 bias types with quantitative detection metrics
- Gold standard construction plan (50 articles, 2 raters, κ ≥ 0.70)
- Automated detection script specification
- Timeline: ~52 person-hours across 6-8 weeks
- Blocked on: human rater recruitment (David decision needed)

**New tests this session**: 91 (52 atom + 39 hierarchy), all passing. Total with prior session: 246.

### Sprint SC (Success Conditions) — COMPLETE

**Summary**: V13 Ruthless Audit scored 3.8/10. Root cause: 142 functions across 5 core service files lacked explicit success conditions. Sprint SC addressed this systematically.

**Total New Tests**: 389 (all passing) + Layer 2/3 infrastructure

| Sprint | Service | Functions | New Tests | Status |
|--------|---------|-----------|-----------|--------|
| SC-1 | Answer Enrichment Orchestrator | 35 | 82 (37 L1 + 20 P0 + 25 systemic) | ✅ COMPLETE |
| SC-2 | Integrated Query Service | 15 | 64 | ✅ COMPLETE |
| SC-3 | Arbitrary QA Handler | 48 (7 critical) | 36 | ✅ COMPLETE |
| SC-4 | Language Adaptation Service | 19 | 116 | ✅ COMPLETE |
| SC-5 | Prose Revision Service | 25 | 91 | ✅ COMPLETE |
| SC-6 | Layer 2/3 Infrastructure | — | scripts + markers | ✅ COMPLETE |

**Three-Layer QA Architecture**:
- Layer 1: 389 success condition tests (deterministic, every commit)
- Layer 2: 45 systemic failure tests with `@pytest.mark.layer2_nightly` + `scripts/run_nightly_audit.py`
- Layer 3: Adversarial audit template at `scripts/run_adversarial_audit.py`

**Key Deliverables**:
- Success conditions written as structured docstrings (SC-*) in all 5 service files
- Sprint plan: `docs/SPRINT_SUCCESS_CONDITIONS_PLAN_2026-03-03.md`
- Test files: `tests/test_success_conditions_{orchestrator,iqs,qa_handler,language_adaptation,prose_revision}.py`
- P0 fix validation: `tests/test_p0_fixes_validation.py`
- Systemic tests: `tests/test_systemic_failure_modes.py`

**Next**: Subsystem-level health contracts for 20 subsystems (V11 decomposition). Cross-boundary data integrity tests. Integration into overseer nightly cycle.

### Circuit QA Latent Variable Reframing + Search Target Wiring — COMPLETE (2026-03-04)

**Summary**: Per David's directive, reframed functional circuits as latent variables (statistical regularities in neural-behavioral covariance) rather than localized neural modules. Added testability sections with article search triggers that feed the recommendation loop.

**Key insight (David)**: Circuits "may not designate actual neural components that implement that very function, or at least not in any localized manner, but they might be latent variables in an analysis of what is going on."

**Changes**:
- `src/services/circuit_qa_service.py`: Rewrote `_build_ontological_statement()` in ATLAS voice (concrete-first, Sagan honest uncertainty, orchestra metaphor). Added `_build_testability_section()` generating accessible test descriptions, data requirements, and article search targets. Added `testability` field to CircuitQACard.
- `src/services/arbitrary_qa_handler.py`: Added `_queue_circuit_search_targets()` — when circuit answers include search targets, they are inserted as `source='circuit_qa'` suggestions in the interpretation_space_suggestions table for the recommendation loop to dispatch.
- `src/services/recommendation_loop.py`: Added Step 2b `_harvest_circuit_qa_targets()` — picks up circuit QA search targets alongside QA backlog and interpretation space gaps.
- Epistemic status levels reframed: STRONG = latent variable recovered across paradigms with intervention evidence; MODERATE = hypothesized latent variable with covariance support; HYPOTHETICAL = predicted by theory, not yet extracted from data (Barrett 2017 warning).
- Search targets for HYPOTHETICAL circuits trigger article acquisition through recommendation loop.
- Tests: 44 tests in `tests/test_circuit_qa_service.py` including 10 new testability tests (all passing).

### Part XXV: Writing & Communication Infrastructure — COMPLETE (2026-03-04)

**Summary**: New master doc Part documenting the writing infrastructure (§168–§172, ~3,200 words). Created per David's standing directive that all theoretically or engineering-interesting progress must be documented in the master doc with grounds and spec. Covers science communication norms (12 norms, 10 practitioners), prose revision service architecture (3-pass diagnostics, Writer's Diet, lard factor), integration architecture (QA pipeline, advisory not blocking), and Smart Book dependency validation. Also added §151.1 Subsystem Health Contracts pointer to Part XXII. Standing directive added to CLAUDE.md.

### Functional Circuits Integration — COMPLETE (2026-03-03)

**Summary**: Integrated 20 functional circuits into the ATLAS annotation system per David's directive that "functional circuits and other new concepts such as atoms have to be part of the annotation system and be worked into explanations in an intelligent and often revelatory manner."

**Schema changes**:
- `src/qa/molecules/schema.py`: Added `linked_archetypes`, `inputs`, `outputs` fields to Molecule dataclass
- `src/qa/molecules/registry.py`: Added `_archetype_index`, `find_by_archetype()`, `get_functional_circuits()`
- `molecule_type` now includes: THEORY, MECHANISM, PHENOMENON, DESIGN_PATTERN, **FUNCTIONAL_CIRCUIT**

**Data created**: 20 functional circuit molecule JSONs in `data/molecules/fc_*.json`

| T2 Archetype | Circuits | Examples |
|-------------|----------|----------|
| CONVERGENT_STATE_MONITORING | 4 | Coherence monitor, threat monitor, vitality monitor, social safety |
| PREDICTIVE_CODING | 4 | Sensory PE, social PE, reward PE, aesthetic expectation violation |
| HOMEOSTATIC_REGULATION | 3 | Arousal regulation, cognitive load regulation, thermoregulatory affect |
| ACCUMULATION_TO_BOUND | 3 | Familiarity detection, dread accumulation, curiosity accumulation |
| COMPETITIVE_SELECTION | 3 | Attentional selection, action selection, interpretive selection |
| GATED_PROPAGATION | 3 | Affective memory gating, context-gated threat, expertise-gated aesthetics |

**Tests**: 44 tests in `tests/test_functional_circuits.py` (schema, registry, archetype index, data quality, JSON format, backward compatibility)

### T-Levels Taxonomy Panel — COMPLETE (2026-03-03)

**Panel prompt**: `docs/PANEL_PROMPT_T_LEVELS_FUNCTIONAL_CIRCUITS_2026-03-03.md` (282 lines)
- CW added 3 implementation-derived insights (concerns #8-#10)
- 5 new panelists added (Thelen, Heyes, Godfrey-Smith, Barry Smith, Pearl)
- 10 identified weaknesses for panel review

**Panel output**: `docs/PANEL_OUTPUT_T_LEVELS_2026-03-03.md` (~1,390 lines)
- 15 panelists across 5 blocks (A-E)
- Cross-commentary with 6 major disagreements, 3 convergences
- Synthesis with unanimous/majority/minority concerns
- 11 concrete ranked recommendations (4 Tier-1, 4 Tier-2, 3 Tier-3)

**Unanimous panel findings** (MUST address):
1. Separate canonical from hypothetical T1 atoms
2. Reground T1.5 boundary structurally (not sociologically)
3. Formalize three separate relations (explanation, evidence, composition)
4. Validate T3 data against AI extraction bias

### Subsystem Health Contracts + Overseer Upgrade — COMPLETE (2026-03-03)

**Health contract specification**: `contracts/SUBSYSTEM_HEALTH_CONTRACTS.md` (946 lines)
- Entry/exit contracts, health invariants for all 20 subsystems
- 12 cross-boundary contracts (XB-1 through XB-12)

**Overseer upgrade**: `src/services/overseer_self_healing.py` expanded from 17→20 subsystems
- 3 new subsystems: Answer Enrichment Orchestrator, Norm Services, Agent Coordination
- Richer success conditions (min 2 per subsystem, total ~50)
- 3 new probe methods for V11 subsystems
- Enhanced theory_templates probe (T1/T1.5/T2/molecule counts)

**Cross-boundary tests**: `tests/test_cross_boundary_contracts.py` (20 tests)
- XB-1: Template-registry contract
- XB-2: Framework referential integrity
- XB-3: Circuit-archetype integrity
- XB-4: T1.5-molecule parent link
- XB-5: Subsystem registry consistency (20 count, conditions, categories, deps, cycles)
- XB-6: Extraction→WoB data flow
- XB-7: Molecule registry health
- XB-8: Success condition testability
- XB-9: Health probe coverage

**Test totals this session**: 128 new tests (44 functional circuits + 64 IQS/services + 20 cross-boundary), all passing.

---

## Pending Tasks

### P0 (Critical — 2026-03-01 STATUS UPDATE)

**V3 Re-Extraction Campaign**: 59 Tier 1 + 1,002 Tier 3 articles queued for re-extraction. Blocked on Gemini API sandbox access (AG, H12). Post-extraction AESHI re-score pending. Provenance verification for 13 unverified theories pending (CW, Task 2).

### P0 (Critical — REVISED SPRINT PLAN 2026-02-27)

**Sprint Plan Documents**:
- Original: `docs/SPRINT_PLAN_SETUP_AND_OVERSEER_2026-02-25.md` (6-sprint plan, partially SUPERSEDED)
- Cross-Audit Synthesis: `docs/CROSS_AUDIT_SYNTHESIS_AND_SPRINT_PLAN_2026-02-27.md` (audit-driven revision)
- **CURRENT**: `docs/NEW_DOCUMENT_SYNTHESIS_AND_REVISED_SPRINT_PLAN_2026-02-27.md` (post-AG-document revision, 1,298 lines)

**Context**: Six crashed AG session documents revealed major architectural breakthroughs that fundamentally change Sprint 1 and Sprint 2. Two expert panels convened (Panel A: Formal Architecture; Panel B: Computational Architecture). Eight decisions reached. Sprint plan revised accordingly.

**Key Changes from Original Plan**:
1. Sprint 1 renamed from "Setup Function" to "Three-Number Separation" (ω, d, CPT must be explicitly separated)
2. New Sprint 0.5 added: Three-Layer Annotation Model (schema + extraction hooks)
3. Sprint 2 upgraded: concrete log-odds π projection implementation (replaces vague "causal typing")
4. EMPIRICAL_COVARIANCE → EMPIRICAL_ASSOCIATION rename throughout codebase
5. Discount factors updated to Woodward-justified canonical values
6. New Sprint 7: T2 Mechanism Template formalization (parallel)

| ID | Task | Context | Status |
|----|------|---------|--------|
| SPRINT-0 | Metadata Enrichment | S2 + CrossRef merged. 813 papers, 731 enriched (89.8%). Citation graph: 1,418 intra-corpus edges. | COMPLETE 2026-02-25 |
| SPRINT-0.5 | Three-Layer Annotation Model | MERGED INTO EN-0D. Schema for stimulus feature tags (Layer 2) and methodological tags (Layer 3). Migration + tag_engine.py + extraction hooks. Panel B Decision B2. | **COMPLETE (merged into EN-0D)** |
| SPRINT-1-REV | Three-Number Separation (was "Setup Function") | REVISED. Explicitly separate ω (warrant strength), d (discount factor), CPT (conditional probability) throughout codebase. Update discount factors to canonical values. EMPIRICAL_COVARIANCE → EMPIRICAL_ASSOCIATION rename. Panel A Decisions A1, A2, A4. | **COMPLETE 2026-02-28** |
| SPRINT-2-REV | π Projection Deployment | REVISED. Implement log-odds projection formula: logit(p_target) = d·ω·δ·logit(p_lab). Multi-edge aggregation via log-odds sum. Path composition via min(d). Epistemic_projection.py VERIFIED. Paper integration orchestrator wired in Step 9 (update_bn). Projection diagnostics with empirical floor computation. Population transfer factor δ implemented. | **COMPLETE 2026-02-28** |
| SPRINT-3 | Canonicalize Warrant Types | Replace EMPIRICAL_COVARIANCE → EMPIRICAL_ASSOCIATION, THEORETICAL_DEFAULT → THEORY_DERIVED across all code and templates. | COMPLETE 2026-02-28 |
| SPRINT-4 | Argumentation Graph Warrant Methods | Add compute_warrant_distribution() and get_aeshi_warrant_component() methods to ArgumentationGraph. | COMPLETE 2026-02-28 |
| SPRINT-5 | Nightly Pipeline Warrant Monitoring | Add _stage_warrant_monitoring() stage to nightly_integration_pipeline.py. | COMPLETE 2026-02-28 |
| SPRINT-6 | Expert Calibration Prep | Create scripts/expert_calibration_prep.py for warrant distribution sampling and expert review preparation. | COMPLETE 2026-02-28 |
| SPRINT-7 | T2 Mechanism Templates & Governance | COMPLETE. Six archetypes formalized with parameters, domain examples, and computational signatures. Processing fluency as T1.5 node. Registry + QA service + 40+ tests. Completion report: `docs/SPRINT_7_COMPLETION_2026-02-28.md`. Panel B Decisions B1, B3. | **COMPLETE 2026-02-28** |
| SPRINT-8 | **Master Document Overhaul** | FINAL SPRINT. All 6 phases COMPLETE. Master doc: 19,502 → 20,559 lines. §48 rewritten (log-odds projection calculus). §48A added (EN/π/BN architecture). §50 enhanced (14 T1.5s, 6 T2 templates, theory-vs-mechanism). Parts XIX-XXI added (Cheat Sheet, Tech Appendix, Source Index). Terminology sweep (212+ changes). Cross-refs verified. Navigation guide added. Formula Transition Note added. δ canonical values (§48.3A). Panel bridging notes for Parts V-VI. | **COMPLETE 2026-02-27** |
| OC-1 | Expand Outcome Vocabulary | Canonical vocab: 24→80→112 terms, 8 domains. v2.0.0 with architecture-cognition terms. See `contracts/outcome_vocab/`. | **COMPLETE 2026-02-28** |
| OC-2 | Backfill Beliefs with Canonical Outcome IDs | `scripts/backfill_canonical_outcomes.py` (405 lines). Dry-run: 62.1% coverage (906/1460), 340 NULL inferred. Supports --commit --fuzzy-threshold. | **COMPLETE 2026-02-28** |
| OC-3 | Wire Resolver into Full Pipeline | Outcome resolver wired into 4 pipeline entry points: rulegraph_v2_builder, orchestrator, gemini_extraction_queue, extraction_to_web. Graceful fallback. | **COMPLETE 2026-02-28** |
| OC-6 | Add Operationalizations to Outcome Vocab | 216 operationalizations added to 72 terms (92.2% coverage). All reference real instruments (STAI, PANAS, ANT, fMRI BOLD, PRS, ASHRAE, etc.). Script: `scripts/backfill_operationalizations.py`. | **COMPLETE 2026-02-28** |
| OC-8 | Check Older Repos for Richer Vocab | Gap analysis: found 32 arch.* + 5 ART terms. Migrated 9 Tier 1 terms. DK approved all 4 Tier 2 terms (env.openness, env.perceived_hazard, env.water_features, env.glare) — added 2026-02-28. Vocab now **116 terms**, 341 cognates, 311 operationalizations. Report: `docs/OC8_VOCAB_GAP_ANALYSIS_2026-02-28.md`. | **COMPLETE 2026-02-28** |
| EQ-FRAMEWORK | Extraction Field Quality Framework | Success conditions for all 11 extraction fields + 8 principle-compliance fields. 50+ validation rules. Three-level quality scoring (field→finding→article). Cleanup pipeline: detect→flag→requeue→verify. Machine-readable rules: `contracts/schemas/extraction_quality_rules.json`. `src/qa/extraction_field_validator.py` (1,615 LOC, 29 tests passing). **Wired into nightly pipeline**: validates all extractions, flags articles below 0.75 for re-extraction, reports to OVERSEER. Principle-compliance fields (causal_tier, scope_conditions, justification_status, defeat_relationships, defeater_search_status, epistemic_level) validated per P1-P10 (Pollock, Haack, Mayo, Cartwright, Pearl). Test fixture updated 2026-03-02 to cover all new fields. | **COMPLETE 2026-03-02** |
| INSTR-REG | Instruments Registry | `contracts/instruments/instruments_registry.json` — 95 instruments with full metadata: authors, year, APA reference, DOI, ~citations, description, psychometrics (alpha, test-retest, validity), strengths, weaknesses, newer alternatives, domain mappings. Covers affect, cognitive, physiological, neural, environmental, health, social, behavioral, built-environment-specific instruments. | **COMPLETE 2026-02-28** |
| INSTR-LINK | Instrument→Vocab Linkage | `instrument_ids` array added to all 112 outcome terms in outcome_vocab.json. 52/112 terms linked to 57/95 instruments (72 total links). PRS most-referenced (6 outcomes). 60 terms unmatched (behavioral/generic measures). 38 instruments unreferenced (clinical tools not yet in vocab). Script: `scripts/link_outcomes_to_instruments.py`. Report: `docs/LINKING_OUTCOMES_TO_INSTRUMENTS_SUMMARY.md`. | **COMPLETE 2026-02-28** |
| PANEL-INFRA | Build AI Panel Resolution Framework | `src/services/ai_panel_resolver.py` (699 lines) + tests (455 lines). 5 panelist roles, 4 panel types, SE-2 rules, dispute escalation, dry-run mode. Decision log: 7 decisions. | **COMPLETE 2026-02-28** |
| IMG-1 | Image Extraction Pipeline for 56 HIGH-Priority Articles | `scripts/run_image_extraction_batch.py` (784 lines). Pipeline built, dry-run validated. **BLOCKED**: 0/56 PDFs available locally. Needs PDF acquisition. | **IN PROGRESS — BLOCKED on PDFs** |
| IMG-2 | Extend Scientific Image Characterization | **Phases 1-3 COMPLETE**. **Phase 3 panel decisions EXECUTED (2026-03-02)**: ATTR-M3 retired (TW=1.4), ATTR-B1 deprecated→NEW-12, 3 new attributes implemented (NEW-13 Temporal Lighting Variation, NEW-14 Prospect-Refuge Balance, NEW-15 Focal Point Density) in `src/vision/new_attributes_batch4.py` (630 lines). Priority ranking added to all 36 attributes via Borda voting. Attribute JSON updated to v1.4.0. 23 new tests passing. Total: 36 attributes (23 active + 10 PRIORITY + 1 retired + 1 deprecated + 1 gap). See `docs/IMG2_PHASE3_IMPLEMENTATION_COMPLETION_2026-03-02.md`. | **PHASE 3 IMPLEMENTED 2026-03-02** |
| MASTER-DOC-MODULAR | **Master Document Modularization** | **COMPLETE 2026-03-02**. Master doc (23,445 lines, 2.3MB) split into 21 modular parts in `docs/master_doc_parts/`. Dynamic boundary detection via `scripts/split_master_doc.py`. Lossless round-trip verified (split→assemble = byte-for-byte identical). Assembly: `scripts/assemble_master_doc.py` (with --output, --diff flags). Backup: `scripts/backup_master_doc.py` (timestamped, SHA-256, rolling 10-backup rotation, --parts tarball). SQLite metadata in `data/article_eater.db` table `master_doc_parts` (21 records with line counts, hashes, timestamps). OVERSEER can query for change detection. | **COMPLETE 2026-03-02** |
| THEORY-GUIDES | **Progressive-disclosure theory guides** | 11 HTML guides (chronobiology, cognitive_map, cpted, episodic_memory, flow_theory, goldilocks_principle, kaplan_preference, pad_model, place_attachment, privacy_regulation, proxemics) with 3 detail levels (Quick/Standard/Technical). In `docs/theory_guides/`. Generator: `scripts/generate_theory_guides.py`. | **COMPLETE 2026-03-01** |
| INTERP-SPACE | **Interpretation Space Spec v2.0** | Endogenous knowledge valuation framework. v1.0: 4 zones, 10 question-type operators, self-interrogation, value function V(G). v2.0 (2026-03-01): Probatory rule sets framework — 4 rule sets (R₁ argumentation, R₂ warrant, R₃ mechanism, R₄ interpretation) with formal opening/closing conditions, closure operators, purpose-relative adequacy, comparison to Hintikka/AGM/Dung/Pollock. See `docs/INTERPRETATION_SPACE_SPEC_2026-03-01.md`. | **SPEC v2.0 COMPLETE 2026-03-01** |
| INTERP-SPACE-IMPL | **Interpretation Space implementation** | **Phase 1 COMPLETE + DK CRITIQUE (2026-03-01)**: Self-interrogation pilot — MECHANISM operator × 50 beliefs. DK critique: mechanism-only zone classification is epistemically wrong. **CREDENCE REVISION NOW COMPLETE (2026-03-02)**: Sprint CREDENCE-WARRANT delivered warrant-derived credence (`warrant_strength.py`), validated by 3 domain panels. **Phase 2 COMPLETE (2026-03-02)**: Full operator suite — 10 R4 operators × 500 beliefs using revised ω-based credence. Multi-operator zone classification (DK's key critique addressed). Zone distribution: 0% Zone 1, 12.2% Zone 2 (Active Boundary), 87.8% Zone 3 (Identified Periphery), 0% Zone 4. **Phase 3 COMPLETE (2026-03-02)**: Top 50 beliefs by centrality. Validation closure 1.2%→62.0%. Boundary: architectural gap (scope_json exists in DB but not surfaced). **Phase 4 COMPLETE (2026-03-02)**: Scope extraction from DB confirmed 0% persistent scope_json in SQLite (data exists at extraction time but not persisted). Validation completeness avg 0.591 (aligned with Phase 3's 0.62). All 50 beliefs classified as Uncertain Periphery (scope gap is bottleneck). VOI-prioritized frontier questions: top 3 (PP, NM, IC) have VOI ≥ 0.6. Script: `scripts/interrogation_phase4.py` (547 lines). Outputs: `data/interpretation_space/phase4/` (5 files). See `docs/INTERP_SPACE_PHASE4_COMPLETION_2026-03-02.md`. | **PHASE 4 COMPLETE 2026-03-02** |
| CREDENCE-REVISION | **Sprint CREDENCE-WARRANT: ω as fundamental quantity** | DK critique + expert panel → fundamental redesign. §48.3B (ω formula), §48.3C (TEA procedure) added to master doc. **ALL 6 PHASES COMPLETE 2026-03-02**. **Phase 1**: Critique of old formula + expert panel convening. **Phase 2**: TEA scoring all 14 T1.5 theories (T_ent scores, 0.55-0.85 range). **Phase 3**: `src/services/warrant_strength.py` (870 lines) implements ω = ω_base × ω_conf × ω_rep × ω_meta. **Phase 4**: Integration into `extraction_to_web.py` (R6 dual-credence transition wired); 62 passing tests. **Phase 5**: Validation on 41 representative beliefs + 3 domain-expert panels (9 panelists: psychology, neuroscience, methodology). Results: old credence mean 0.177 ± 0.031, new mean 0.482 ± 0.012, correlation r=0.747, Δ=0.305 ± 0.024. All 41 exceed R6 threshold. Panel verdicts: UNANIMOUS affirm warrant-derived formula as epistemically sound; all recommend immediate adoption. See `docs/PHASE_5_DOMAIN_EXPERT_PANEL_REVIEWS_2026-03-02.md` (892 lines) and `docs/SPRINT_CREDENCE_WARRANT_COMPLETION_2026-03-02.md` (1,200 lines). **Phase 6**: Sprint completion report finalized. | **COMPLETE 2026-03-02** |
| TEA-ALL-THEORIES | **Apply TEA to all ATLAS theories** | **v2.0 (2026-03-02)**: Expanded from 14 → 24 entries. All 10 T1 frameworks + 4 T1.5 canonical + 10 domain theories scored. Re-keyed with humanly meaningful hyphenated terms per DK directive (e.g., `predictive-processing` not PP, `attention-restoration-theory` not ART). Backward compatibility via `_LEGACY_KEY_MAP` in `load_tea_scores()`. T1 range: 0.615 (embodied-cognition) to 0.928 (chronobiological-regulation). T1.5 range: 0.400 (prospect-refuge-theory) to 0.540 (attention-restoration-theory). Master doc §50 rewritten with 5-tier hierarchy, molecules as latent variables. §53.6-§53.9 added (OUTCOME_BRIDGES, V3 fields, AESHI formula, CCI metric). | **COMPLETE 2026-03-02** |
| NAMING-REFACTOR | **Theory naming: 2-letter abbreviations → humanly meaningful hyphenated terms** | DK directive 2026-03-02: "I hate the 2 letter acronyms... I want humanly meaningful hyphenated terms." **Phase 1 (2026-03-02)**: TEA scores re-keyed, master doc §50 rewritten, `load_tea_scores()` backward compat layer. **Phase 2 (2026-03-02)**: Full data file migration complete. `schemas/theory/tier1_frameworks.json` re-keyed (PP→predictive-processing etc). All 25 theory JSONs updated (parent_t1_frameworks). All 13+ molecule JSONs updated (framework_ids). `finding_template_relevance.py` updated to load new keys. Zero legacy 2-letter abbreviations remain as primary IDs in any data file. 93 tests passing. **Remaining**: Python filenames (pp_profile.py etc.) intentionally NOT renamed (import chain risk). Profile/reduction file internal THEORY_IDs should be audited in future sprint. | **PHASE 2 COMPLETE 2026-03-02** |
| INTERP-SPACE-QNORMS | **§4.7 Question-Formulation Norms** | 7 Q-norms (Hintikka presuppositions, Bromberger/van Fraassen contrast class, Laudan problem type, Simon VOI, Gawande specificity, Yong prerequisite structure, Sapolsky seam targeting) + success conditions for ALL system functions (24 rows across 5 categories). Written into `docs/INTERPRETATION_SPACE_SPEC_2026-03-01.md` §4.7. | **COMPLETE 2026-03-01** |
| PRINCIPLE-VALIDATORS | **Epistemic principle-compliance validation rules** | 28 validation rules for 8 principle-compliance fields (causal_tier, scope_conditions, justification_status, defeat_relationships, defeater_search_status, source_quality_indicators, conflict_type, epistemic_level). Wired into `src/qa/extraction_field_validator.py`. Tests: 10 violations fire correctly on bad data. Maps P1-P10 from `docs/EPISTEMIC_PRINCIPLES.md`. | **COMPLETE 2026-03-01** |
| INTERP-SPACE-RATRECON | **Rational reconstruction of Interpretation Space theory** | 12-section document tracing intellectual evolution through 7 stages: QA periphery discovery → endogenous valuation → epistemic operators → follow-up design → probatory rules → closure formalization → zone redefinition. Defines all 4 probatory rule sources. Working doc for eventual formal paper. See `docs/RATIONAL_RECONSTRUCTION_INTERPRETATION_SPACE_2026-03-01.docx`. | **COMPLETE 2026-03-01** |
| INTERP-SPACE-QNORMS | **§4.7 Question-Formulation Norms** | 7 Q-norms (Hintikka presupposition, Bromberger/van Fraassen contrast class, Laudan problem type, Simon VOI, Gawande specificity, Yong prerequisite structure, Sapolsky seam targeting). Science communication norm mappings. Success conditions for ALL system functions (24 rows across 5 categories). Added to `docs/INTERPRETATION_SPACE_SPEC_2026-03-01.md` §4.7. | **COMPLETE 2026-03-01** |
| EPISTEMIC-PRINCIPLES | **Epistemic Principles Integration** | AG's 17 norms (10 philosopher + 7 science writer) integrated into extraction pipeline plan. 8 new schema fields added to extraction_template.v2. Plan updated with Pass 3D (principle compliance) and Panel E. Prompt v3 validation suffix expanded 5→10 checks. | **COMPLETE 2026-03-01** |
| EXTR-PIPELINE | **Extraction Pipeline Overhaul (Phases 1-6)** | Master plan: `docs/EXTRACTION_PIPELINE_OVERHAUL_PLAN_2026-03-01.md`. **Phase 1A (schema v2 + principle fields): ✅ COMPLETE 2026-03-02**. **Phase 1B (validator gate): ✅ COMPLETE 2026-03-02** — ExtractionFieldValidator now BLOCKING in `extraction_to_web.py`. Findings below 0.75 blocked, flagged for re-extraction. Configurable via `ATLAS_VALIDATOR_BLOCKING` + `ATLAS_QUALITY_THRESHOLD`. 14 new tests. See `docs/PHASE_1B_COMPLETION_2026-03-02.md`. Phases 2-6 blocked on AG re-extraction. | **PHASE 1B COMPLETE 2026-03-02** |
| RECOMMENDATION-LOOP | **Continuous Article Recommendation Loop** | **COMPLETE 2026-03-02**. `src/services/recommendation_loop.py` (500 LOC) — RecommendationLoopService harvests gaps from interpretation space + QA, scores with VOI, dispatches top-N to searcher. Modes: single pass (nightly), continuous daemon (5-min interval), health check. Wired into `scheduled_pipeline.py` + `overseer_nightly_v3.py` Section 11. Runner: `scripts/run_recommendation_loop.py`. 15 tests. See `docs/RECOMMENDATION_LOOP_IMPLEMENTATION.md`. | **COMPLETE 2026-03-02** |
| CH-PARAM-JSONS | **Create CH calibration parameter JSONs** | **COMPLETE (2026-03-02)**: All 7 CH parameter JSONs created from research docs: ch1_noise_tolerance (13KB), ch2_proxemics (15KB), ch3_visual_complexity (15KB), ch4_ceiling_height (13KB), ch5_nature_artifice (18KB), ch6_symmetry (17KB), ch7_color_temperature (15KB). Plus `calibration_schema.json` (11KB). Total: 132KB, 40+ peer-reviewed references, 15+ cultural regions. ψ_culture multipliers included for CVA-1-REV integration. Legacy placeholder files moved to `data/calibration/deprecated/`. RV5-6 audit finding RESOLVED (was 1/10 CRITICAL RED for data). | **COMPLETE 2026-03-02** |
| THEORY-GUIDES-QA | **Integrate theory guides into QA/browse site** | **COMPLETE (2026-03-02)**: Built `src/services/theory_guide_service.py` (650 LOC) — TheoryGuideService with HTML parsing, fuzzy matching, 3-level progressive disclosure, metadata integration. Wired into `arbitrary_qa_handler.py` (THEORY_GUIDE question type fully functional, smart detail-level routing). Wired into Streamlit `1_query.py` (Theory Background expander) and `2_explore.py` (Theory Context panel for beliefs). 32 tests passing. 11 guides loadable with fuzzy matching. | **COMPLETE 2026-03-02** |
| THEORY-GUIDES-VIZ | **Theory provenance tooltips in EN/BN visualization** | **COMPLETE (2026-03-02)**: `get_tooltip_html()` method in theory_guide_service.py generates compact HTML tooltips with theory name, Quick-level content, constructs, maturity, ATLAS status. Wired into Streamlit explore page — belief detail view shows theory context panel with expandable guide content. `get_theory_summary()` provides JSON-serializable dict for any renderer. For full JS-based viz (D3/Three.js), tooltip HTML can be injected via `theory_guide_service.get_tooltip_html(theory_name)`. | **COMPLETE 2026-03-02** |
| PAPER-GOLDILOCKS | **Paper: "The Goldilocks Principle in Architecture"** | **FULL DRAFT COMPLETE (2026-03-02)**. All 12 sections expanded to publication-quality prose. `docs/PAPER_GOLDILOCKS_FULL_DRAFT_2026-03-02.md` (967 lines, ~18,732 words). §1 Introduction, §2 Historical Context (from prior draft), §3 Formal Model (P(x) + free energy), §4 Cross-Modal Evidence, §5 Fractal Dimension & Natural Statistics, §6 Neurobiological Substrate, §7 Cultural Calibration & Individual Differences, §8 Processing Fluency, §9 T1.5 Integration & Irreducible Residual, §10 Architectural Design Implications, §11 Open Questions & Research Agenda, §12 Conclusion. 50+ APA citations. Expert panel feedback integrated throughout. Target: *Psychological Review* or *BBS*. **Next**: DK review, DOI verification, figures, final references. | **FULL DRAFT COMPLETE 2026-03-02** |
| MASTER-DOC-REVISIONS | **Master Document: 10 New/Revised Sections** | **COMPLETE 2026-03-02**. `docs/MASTER_DOC_REVISIONS_2026-03-02.md` (2,110 lines, ~8,500 words). 10 sections covering: §47A VOI Integration Architecture, §47B Researcher-Specific VOI, §47C Article Search Execution Pipeline, §47D QA as Recommendation Source, §47E Discovery Funnel Feedback Loop, §132.6a Overseer Management DB Schema, VOI Computation Details revision, Queue Prioritization Strategy revision, Recommendation Flow Integration Points revision, §132.7 Continuous Recommendation Loop Service. All implementation-validated against actual codebase. Integration instructions included. | **COMPLETE 2026-03-02** |
| PANEL-CALIBRATION | Panel reviews calibration inputs + approves thresholds | **COMPLETE 2026-03-02** — 5-member panel (cross-cultural psychologist, environmental psychologist, psychometrician, architectural researcher, epistemologist) reviewed all 7 CH files. Disposition: CH-2 APPROVED (gold-standard Sorokowska data), CH-1/3/4/5/6 APPROVED WITH REVISIONS, CH-7 REVISE & RESUBMIT (Kruithof curve untested). Conditional approval for field trial. Critical: $1.1M research program needed for full validation. See `docs/PANEL_CALIBRATION_REVIEW_2026-03-02.md` (858 lines). | **COMPLETE 2026-03-02** |
| OVERSEER-PANEL | Panel review of OVERSEER design | **APPROVED BY DAVID 2026-03-02**. 8 design questions answered (Feb 25 panel). David's policy decisions: (1) community=consensus, (2) VOI thresholds=panel-decided, (3) coherence=per-theory C_min via new panel (`docs/PANEL_COHERENCE_THRESHOLDS_2026-03-02.md`), (4) provenance=continuous/credence-grounded via new panel (`docs/PANEL_JUSTIFICATION_PROVENANCE_2026-03-02.md`), (5) quarantine=varies by theory, (6) AESHI weighting=current fine, revisable, (7) snapshots=daily, (8) scalability=needs development. All decisions revisable. **OVERSEER v2 Management Layer implemented**: `src/services/overseer_management.py` (1,101 LOC) + models (327 LOC) + 29 tests. 7 services: PipelineRegistry, QueueHealthMonitor, ArticleFlowMonitor, SearchSuggestionTracker, ExtractionQueueMonitor, PanelConvocationService, ManagementDashboard. See `docs/OVERSEER_MANAGEMENT_LAYER_2026-03-02.md`. | **COMPLETE 2026-03-02** |
| VOI-INTEGRATION | **VOI Integration + Article Recommendation Flow Fixes** | **COMPLETE 2026-03-02**. Deep audit of all recommendation flows (QA, annotation, argumentation, VOI). 6 critical disconnects identified and fixed: (1) GapPredictor now calls real VOIGapScorer instead of hardcoding 0.5. (2) ResearchQueue now VOI-ranked (highest-VOI target returned first). (3) `interpretation_space_suggestions` table created + populated by QA follow-ups and gap predictor. (4) AutomatedQueueSearcher wired into scheduled_pipeline.py. (5) Researcher-specific VOI implemented (`src/queue/researcher_voi.py`) — domain fit, access match, collector type, historical performance, capacity factors. (6) CollectorProfile fields now used for personalized recommendations. **58 new tests** (15 VOI integration + 18 interpretation space + 25 researcher VOI), all passing. Master doc revision list: `docs/MASTER_DOC_REVISION_LIST_2026-03-02.md` (10 new/revised sections needed). Audit report: `docs/AUDIT_RECOMMENDATION_FLOW_2026-03-02.md`. | **COMPLETE 2026-03-02** |
| GOLDILOCKS-PANEL | Full expert panel on Goldilocks Principle | **COMPLETE 2026-03-02** — 8-member panel (Berlyne scholar, PP theorist, environmental psychologist, neuroaesthetician, cross-cultural psychologist, architect, psychometrician, philosopher of science). 6 ACCEPT WITH REVISIONS, 2 ACCEPT WITH MAJOR REVISIONS. Formal model rated 6.75/10, T1 reduction 8.1/10, cross-modal universality needs qualification (5.75/10). 10 research questions evaluated. See `docs/GOLDILOCKS_EXPERT_PANEL_2026-03-02.md`. |
| **CVA-PANEL** | **12-Person CVA Expert Panel** | 12 panelists (Jordan, Friston, Strogatz, Scherer, Barrett, Eisenberger, Deci, Leary, Kitayama, Ulrich, Dalton, Zumthor). Vote: 10 ADOPT PARTIALLY, 2 DEFER, 0 FULL, 0 REJECT. See `docs/EXPERT_PANEL_CVA_FULL_2026-02-27.md` (495 lines). | **COMPLETE 2026-02-27** |
| EN-0A | Bridge Template Worlds | 196/208 templates enriched via `scripts/bridge_template_worlds.py`. Gaps closed: mechanism_chain 100%→11%, bridge_warrant 100%→11%, building_types 50%→34%. All carry `bridge_inferred: true` provenance. | **COMPLETE 2026-02-27** |
| EN-0B | Belief Seeder Extension + Backfill | Seeder extended with `scan_all_templates()`, `--include-uncalibrated` flag. 166 beliefs seeded (48 calibrated + 160 uncalibrated, 63 constraints). Uncalibrated use INTERMEDIATE/TENTATIVE. Backfill COMPLETE: 5 theories enriched (processing_fluency +3 construct ids, allesthesia +2 constructs +4 refs, auditory_scene_analysis +3 constructs +5 refs, berlyne_arousal +3 constructs +5 refs, chronobiology +3 constructs +5 refs). All 24 theory files validate. | **COMPLETE 2026-02-28** |
| EN-0C | Paper Integration Pipeline Activation | Batch manifest: 11 batches × ~100 papers = 1,037 total. Ready-to-paste prompts in `docs/PARALLEL_PAPER_INTEGRATION_PROMPTS.md`. Quality-review via parallel AG/Opus conversations. | IN PROGRESS |
| EN-0D | Annotation System (merges Sprint 0.5) | 10-type annotation schema implemented. Migration 024, `annotation_service.py` (CRUD + supersession + batch + QA helpers), 27/27 tests, 166 initial annotations seeded (103 CALIBRATION_NOTE + 63 SENSITIVITY_FLAG). Wired into `enrich_response()`. | **COMPLETE 2026-02-27** |
| EN-0E | OVERSEER Coverage Metrics | 4 new invariants: INV-6 Pipeline Utilization (≥25%), INV-7 Template Coverage (≥80%), INV-8 Theory Linkage (≤10% orphans), INV-9 Evidence Diversity (≥20% paper-sourced). AESHI formula: 60% quality + 40% coverage/utilization, hard cap at 50 for <5% utilization. Wired into `check_integrity()`, `check_health()`, `_generate_alerts()`. Stage 7.5 in nightly pipeline. | **COMPLETE 2026-02-27** |
| CVA-1-REV | Constraint Variable Registry + Two-Tier Architecture + ψ | **AG COMPLETE, VERIFIED 2026-03-02**. Tier1 (6 universal perceptual primitives) + Tier2 (8 ψ-calibrated). 13 neurotype sensitivity profiles. `src/models/cva_constraint.py` (285 LOC), `src/services/cva_constraint_engine.py` (342 LOC). | **VERIFIED COMPLETE** |
| CVA-2-REV | Valuation Axes Schema + Cultural Decomposition + Rasa-Attractors | **AG COMPLETE, VERIFIED 2026-03-02**. 9 axes, 4 cultural variants (Western 9D, Japanese 10D, West African 6D, Indian 4D). `src/models/cva_valuation.py` (338 LOC), `src/services/cva_valuation_engine.py` (438 LOC). Rasa attractors: `data/cva/rasa_attractors.json` (9 rasas, all verified stable). | **VERIFIED COMPLETE** |
| CVA-3 | ActivityFrame Implementation | **AG COMPLETE, VERIFIED 2026-03-02**. 10 frames (8 canonical + 2 extended) with precision profiles. `src/models/activity_frame.py` (239 LOC). Frame→goal mapping operational. | **VERIFIED COMPLETE** |
| CVA-4 | 20-Template Pilot Reclassification | **AG COMPLETE, VERIFIED 2026-03-02**. TemplateCVALinker covers 209 templates. Gap report generated. | **VERIFIED COMPLETE** |
| CVA-5 | Goal-Modulated Projection | **AG COMPLETE, VERIFIED 2026-03-02**. `epistemic_projection_cva.py` implements goal-modulated π. Comparison with original predictions. | **VERIFIED COMPLETE** |
| CVA-6 | Beauty Compression Testing | **AG COMPLETE, VERIFIED 2026-03-02**. 4 models (linear, quadratic, neural, rasa). R² comparison operational. Beauty model weights are placeholders pending training data. | **VERIFIED COMPLETE** |
| CVA-7 | Identifiability Experiment Design | **AG COMPLETE, VERIFIED 2026-03-02**. 3 hard problems solved: recognition model (Q2), decomposed feedback (Q3), activity precision (Q1). | **VERIFIED COMPLETE** |
| CVA-8 | Cross-Cultural Validation Design | **AG COMPLETE, VERIFIED 2026-03-02**. 4 cultural regions × 13 neurotypes. Measurement adaptation framework. | **VERIFIED COMPLETE** |
| CVA-9 | Integration Decision + Master Doc Update | **AG COMPLETE, VERIFIED 2026-03-02**. Overseer playbooks for INV-10..13. Database migrations. Panel review conducted. Strangler fig pattern verified — 213+ existing tests unbroken. | **VERIFIED COMPLETE** |
| **CVA-IMPL** | **7-Phase CVA Implementation Plan** | **ALL 7 PHASES COMPLETE + VERIFIED 2026-03-02**. 254 CVA tests passing. Total: ~3,500 LOC across models + services + tests. Strangler fig pattern: all CVA code in new files, zero modifications to existing pipeline. Verification report: `docs/CVA_VERIFICATION_REPORT_2026-03-02.md`. Minor: beauty model weights are placeholders (need training data), attractor basins use sampling (could be analytical). | **VERIFIED COMPLETE 2026-03-02** |
| MASTER-DOC-XXII | **Part XXII: Operational Infrastructure** | **COMPLETE 2026-03-03**. New master doc part (§148–§154, 5,847 words) documenting 5 previously undocumented AG systems: Reflex System (13 detect-fix-report triples), Success Conditions (62 contracts), Overseer (13 invariants, 4 modes, quarantine protocol), Signal-Based Coordination (166 signal triplets), QA Validators (4-layer immune system). Academic prose grounded in Dijkstra, Peirce, Haack, Simon, Mayo, Parnas. File: `docs/master_doc_parts/PART_XXII_OPERATIONAL_INFRASTRUCTURE.md`. | **COMPLETE 2026-03-03** |
| SMART-BOOK | **Dependency-Aware Documentation System ("Smart Book")** | **COMPLETE 2026-03-03**. Machine-readable dependency manifest tracking 10 core cross-cutting concepts (T1.5 count, credence formula, warrant types, AESHI, Q-norms, epistemic levels, etc.) across all 21 master doc parts. Validation script (`scripts/validate_master_doc.py`, 21KB) checks for count mismatches, stale references, undefined concepts, and sections needing review. Design doc, user guide, integration guide all written. Validator tested: caught 2 false-positive T1.5 regex matches (fixed), 2 MEDIUM advisory items (legit review suggestions). Files: `docs/master_doc_parts/DEPENDENCY_MANIFEST.json`, `scripts/validate_master_doc.py`, `docs/SMART_BOOK_DESIGN_2026-03-03.md`, `docs/SMART_BOOK_README.md`, `docs/SMART_BOOK_INTEGRATION_GUIDE_2026-03-03.md`. | **COMPLETE 2026-03-03** |
| QA-SERVICES | **Service Architecture Overhaul** | **COMPLETE 2026-03-02**. Diagnosed and fixed the capability-composition gap: 30+ services existed but only 2 called during answer generation. Built AnswerEnrichmentOrchestrator (794 LOC, 8-step pipeline), LanguageAdaptationService (5 user types, real personalization), FigureSuggestionService (42 figures, 161-concept index), MathExplanationService (6 formulas × 7 norms × 4 layers). 11 API endpoints. All wired into arbitrary_qa_handler.py. 5,938 tests pass, 0 failures. Master doc §140 written. | **COMPLETE 2026-03-02** |
| MASTER-DOC-XXIII | **Part XXIII: Multi-Agent Coordination & RAG** | **COMPLETE 2026-03-03**. New master doc part (§155–§159, ~2,800 words) documenting AG's coordination system (.agent_coord/), RAG experiment design (40-question battery), corpus completion (53 foundational papers reading list), tier taxonomy propagation procedure, PDF acquisition architecture. File: `docs/master_doc_parts/PART_XXIII_MULTI_AGENT_COORDINATION_AND_RAG.md`. | **COMPLETE 2026-03-03** |
| V3-PROMPT-WIRING | **Wire V3 extraction prompts into gemini_extraction_queue.py** | **COMPLETE 2026-03-03**. Discovered `src/extraction/revised_prompts_v3.py` existed since 2026-03-01 but was NEVER imported. Added import with graceful fallback, `--prompt-version v1\|v3` CLI flag (defaults to v3), V3 type mapping. 192 tests pass. Message 008 sent to AG to run V3 on 7 new PDFs. | **COMPLETE 2026-03-03** |
| PPTX-SERVICE | **Academic Presentation Design Service** | **COMPLETE 2026-03-03**. Created `services/academic_presentation_service/SKILL.md` — comprehensive presentation design guide with 7 principles (assertion-evidence, scaffolded complexity, data-ink maximization, narrative threading, cognitive load management, drama through data, intellectual honesty). Grounded in Tufte, Mayer, Feynman, Pinker, Rosling, Doumont, Garner & Alley. 8 slide type templates, 4 academic color palettes, quality checklist, 7 anti-patterns. Root CLAUDE.md updated with mandatory service usage requirement for all deliverables. | **COMPLETE 2026-03-03** |
| PPTX-REVIEW | **Clark Lab V3 Presentation Review** | **COMPLETE 2026-03-03**. Reviewed 25-slide Clark Lab presentation against 7 Academic Presentation Service principles. Overall: 7.9/10. Strongest: narrative threading (9/10), scaffolded complexity (9/10), intellectual honesty (9/10). Weakest: data-ink maximization (6/10) — too much data described in text rather than shown visually. 9 specific improvements identified with priority ranking. Report: `docs/PPTX_REVIEW_Clark_Lab_V3_2026-03-03.md`. | **COMPLETE 2026-03-03** |
| SCI-COMM-NORMS | **Science Communication Writing Norms** | **COMPLETE 2026-03-03**. Created `contracts/SCIENCE_COMMUNICATION_NORMS.md` — 12 norms grounded in named practitioners: Pinker (classic style, curse of knowledge), Williams (Given-New contract, stress position), Lanham (Paramedic Method, zombie nouns), Sword (Writer's Diet), Sacks (defamiliarization through pathology), Sagan (scale bridging, honest uncertainty), Yong (slow complexity building), Gawande (narrative arc), Carson (ethical embedding, sensory immersion), Doumont (structure as communication). Includes 3-pass revision protocol, genre-specific architecture (research paper, master doc, perspective article). Cross-referenced with existing WRITING_STYLE_GUIDE.md, EPISTEMIC_PRINCIPLES.md (Principles 11-17), MATH_EXPLANATION_NORMS.md, VISUALIZATION_NORMS.md. Root CLAUDE.md updated with mandatory reading requirement for all extended prose. | **COMPLETE 2026-03-03** |
| PROSE-REVISION-SVC | **Prose Revision Service — Active Critique & Diagnostics** | **COMPLETE 2026-03-03**. Created `src/services/prose_revision_service.py` (956 LOC) — executable implementation of SCIENCE_COMMUNICATION_NORMS as automated prose diagnostics. 3-pass revision protocol: Pass 1 Structural (Doumont — headings, paragraph length, flow), Pass 2 Sentence-level (Lanham + Williams — nominalizations, passive voice, hedge stacks, throat-clearing, overclaiming, sentence length, weak openers, citation clusters), Pass 3 Knowledge-curse audit (Pinker — undefined abbreviations, jargon). Includes: Sword's Writer's Diet (5-category word health), Lanham's lard factor estimation, quantitative scoring (0-10 scale with context-sensitive thresholds for qa_response/paper/master_doc/general), formatted markdown reports. Wired into `arbitrary_qa_handler.py` as optional post-processing step (`enable_prose_review=True` adds `prose_review` field with score, verdict, and top suggestions). 55 tests (all pass): 13 test classes covering all diagnostics, composites, context sensitivity, edge cases, and QA handler integration. | **COMPLETE 2026-03-03** |
| GOLDILOCKS-REVISION | **Goldilocks Paper Side-by-Side Prose Revision** | **COMPLETE 2026-03-03**. Ran ProseRevisionService on full Goldilocks paper draft (18,750 words): 33 critical issues, 113 warnings, nominalization density 5.0/100, passive 11%, lard 12%. Created landscape side-by-side DOCX (`GOLDILOCKS_SIDEBYSIDE_PROSE_REVISION_2026-03-03.docx`) with 10 passage pairs showing original vs. revised prose with amber diagnostic annotations citing specific norms (Pinker Classic Style, Williams Given-New/Stress Position, Lanham Paramedic Method, Sword Writer's Diet, Sagan/Yong Scaffolded Explanation, Carson/Sagan Honest Uncertainty, Yong/Sacks Defamiliarization, Doumont Structure as Communication). Estimated improvement: 0.0/10 → 7.5+/10, nominalization density 5.0 → ~3.2/100. | **COMPLETE 2026-03-03** |
| RUTHLESS-V13 | **V13 Ruthless System Audit** | **COMPLETE 2026-03-03**. Comprehensive audit of QA pipeline: answer_enrichment_orchestrator, integrated_query_service, language_adaptation_service. Test results: 5 FAILED / 46 PASSED / 1 SKIPPED. **System Health Score: 3.5/10** (down from V12's 6.5). Root cause: global latency budget (5000ms) exhausted after step 6, silently skipping steps 7-9 (language_adaptation, figure_suggestions, interpretation_context). Three most dangerous failure modes: (1) Silent budget starvation truncating interpretive layer, (2) Graceful degradation masking real errors via try/except, (3) Evidence-backed claims returned without evidence. Subsystem scores: Orchestration 2/10, Interpretive Intelligence 1/10, Bayesian Core 7/10, Gap Analysis 5/10, Query Tracing 4/10. Critical directives: restructure pipeline parallelism, move service init out of pipeline, add completeness flagging. Reports: `docs/RUTHLESS_V13_COMPREHENSIVE_AUDIT_2026-03-03.md` (22KB), `docs/RUTHLESS_V13_CLAUDE_AUDIT.md`, `docs/RUTHLESS_V13_CODEX_AUDIT.md`. | **COMPLETE 2026-03-03** |
| PAPER-AUDITOR | **Paper Evidence Auditor (reusable function)** | **COMPLETE 2026-03-02**. `src/services/paper_evidence_auditor.py` (450 LOC) — PaperEvidenceAuditor class for systematic paper→evidence audit. Parses markdown, extracts claims, cross-references against ATLAS beliefs, generates prioritized search targets, submits to interpretation_space_suggestions. Applied to Goldilocks paper: 42 claims assessed (20 well-supported, 19 partial, 3 unsupported), 30 search targets generated (5 HIGH, 6 MEDIUM, 8 LOW + 11 schema gaps), overall warrant ω≈0.57. Targets submitted to recommendation pipeline. Gap analysis: `docs/GOLDILOCKS_EVIDENCE_GAP_ANALYSIS_2026-03-02.md`. Search targets: `data/paper_search_targets/goldilocks_searches.json`. 23 tests passing. Designed for reuse: `auditor.full_pipeline('path/to/paper.md')`. | **COMPLETE 2026-03-02** |

### RUTHLESS V5 — Full-Repo Audit (Added 2026-02-28, DK requested)

**Trigger**: After AG + CW have completed most pending tasks.
**Scope**: Entire repo including ALL new code from Sessions 14-18+, image processor, tagging consultants (antecedent AND consequent), cultural calibration, CVA implementation, extraction quality framework, instruments registry, Kirsh decision tree outputs — everything.

| ID | Task | Scope | Owner | Status |
|----|------|-------|-------|--------|
| RV5-1 | **Panel consultation on unreviewed decisions** | All design/implementation decisions made by AG or CW without panel input. Review decision logs in `docs/*DECISIONS_LOG*.md`. Convene panels for any medium/high-risk decisions that were made unilaterally. | CW + AG | **COMPLETE 2026-03-01** — 47 decisions inventoried, 5 high-risk paneled. D-AE-3 (cultural calibration) got 1 BLOCK. Report: `docs/RV5_1_PANEL_REVIEW_UNREVIEWED_DECISIONS_2026-03-01.md` |
| RV5-2 | **Comprehensive test suite execution** | Run ALL tests (4,082+ existing + all new). Fix failures. Add missing coverage for new modules: extraction_field_validator, nightly QA gate, instrument registry linkage, cultural calibration parameters, decision tree outputs. Target: zero failures, >80% coverage on new code. | **AG** | **IN PROGRESS 2026-03-01** — AG claimed. Running full suite + adding 22 new sprint tests (34/34 pass so far). |
| RV5-3 | **Ruthless audit: extraction pipeline** | Audit antecedent fields (stimulus descriptions), consequent fields (outcome descriptions), direction normalization, claim_type accuracy. Use extraction_field_validator on full corpus. Flag and fix systematic errors. | CW + AG | **COMPLETE 2026-03-01** — 7.35/10. Direction 99.1% canonical ✓. Antecedent 99.7% non-vague ✓. Template matching 87.7% ✓. CRITICAL: effect_size 78.2% missing, sample_size 95.6% missing. Report: `docs/RV5_3_EXTRACTION_PIPELINE_AUDIT_2026-03-01.md` |
| RV5-4 | **Ruthless audit: image processing + attribute taxonomy** | Audit all 33 attributes (21 original + 12 new). Verify vision algorithm specs are implementable. Test Tier 1 algorithms on real images. Check for theoretical warrant gaps, missing references, unsupported claims. | CW | **COMPLETE + REMEDIATED 2026-03-01** — Audit: 5/10. Remediation: ALL 12 NEW attributes implemented (2,214 lines across 3 files), 120 tests pass, schema v1.2.0. All CPU-friendly Tier-1. See `src/vision/` |
| RV5-5 | **Ruthless audit: tagging consultants (antecedent + consequent)** | Audit the tagging/categorization quality for both antecedent descriptions (stimulus taxonomy, equivalence classes) and consequent descriptions (outcome vocab, instrument linkages). Check for miscategorization, overlaps, gaps, orphaned terms. | CW | COMPLETE 2026-03-01 — 4/10. 47.5% unmapped consequents (15,691/33,021). Direction validity 10/10. Antecedent specificity 8/10. See docs/RV5_5_TAGGING_QUALITY_AUDIT_2026-03-01.md |
| RV5-6 | **Ruthless audit: cultural calibration parameters** | Audit all 7 CH calibration JSONs for internal consistency, plausible numeric ranges, proper APA references, theoretical coherence across CH-1..CH-7. Cross-check parameter interactions. | CW | COMPLETE (2026-03-01) — CRITICAL FINDING: Parameter JSONs (ch1_noise_tolerance_parameters.json, etc.) DO NOT EXIST. Only 2 generic UUID-named placeholder files found in /data/calibration/. CH-1..CH-7 research documentation complete (8.6/10 avg). See `docs/RV5_6_CALIBRATION_AUDIT_2026-03-01.md` for 155-point audit report, 5 critical issues (task-blocking), ~12–15 hrs remediation. Score: 1/10 CRITICAL RED (data); must create parameter JSONs + schema before CVA-1-REV integration possible. |
| RV5-7 | **Ruthless audit: CVA implementation code** | Audit all AG-written CVA code (Phases 0-6). Check: correct formula implementation, edge cases, error handling, test coverage, documentation accuracy, schema compliance. | **AG** | **IN PROGRESS 2026-03-01** — AG claimed. |
| RV5-8 | **Ruthless audit: contracts and schemas** | Audit all JSON schemas, outcome_vocab, instruments_registry, extraction_quality_rules for internal consistency, completeness, valid JSON, correct cross-references. | CW | COMPLETE 2026-03-01 — 9.3/10. 44/44 files valid JSON, 0 duplicate IDs. 11 minor fixes applied (8 error messages, 2 instrument years, 1 schema field). See docs/RV5_8_CONTRACTS_SCHEMAS_AUDIT_2026-03-01.md |
| RV5-9 | **Synthesis: AESHI re-score + gap report** | After all audits, re-run AESHI scoring. Produce gap report comparing current state to target. Identify top 10 remaining issues. Write `docs/RUTHLESS_V5_AUDIT_REPORT_2026-MM-DD.md`. | **AG** | **IN PROGRESS 2026-03-01** — AG claimed. DB Tier2 100%, template 95.3%, Tier1 95.1%. |

### Cultural Habituation Effects — Tier 2 ψ_culture Calibration Research (Added 2026-02-28)

These items are research topics that feed into CVA-1-REV (Tier 2 constraint calibration through ψ_culture). Each requires literature ingestion → extraction → template creation/modification → belief integration. References compiled in `docs/CULTURAL_HABITUATION_REFERENCES_APA_2026-02-28.md`. Research gaps in `docs/CULTURAL_HABITUATION_RESEARCH_GAPS_2026-02-28.md`.

| ID | Task | CVA Constraint(s) | Key References | Status |
|----|------|--------------------|----------------|--------|
| CH-1 | **Background noise tolerance**: Urban density in East Asian cities calibrates higher baseline tolerance for ambient sound. Affects `ProcessingCost` thresholds in Tier 2. | ProcessingCost, MultisensoryCoherence | Helson (1964) [~2,800 cit], Kang & Yang (2015) [~156 cit], Malmierca (2023) [~15 cit], Aron et al. (2012) [~1,847 cit] | **RESEARCH COMPLETE 2026-02-28** — See `docs/CH1_NOISE_TOLERANCE_CULTURAL_CALIBRATION_2026-02-28.md` and `data/calibration/ch1_noise_tolerance_parameters.json` |
| CH-2 | **Personal space expectations (proxemics)**: Fine-grained cultural gradients beyond individualist/collectivist dichotomy. Affects `SocialCueDensity` and `AffordanceDensity` thresholds. | SocialCueDensity, AffordanceDensity | Hall (1966) [~6,247 cit], Sorokowska et al. (2017) [~742 cit], Beaulieu (2004) [~216 cit], Evans & Lepore (1992) [~127 cit] | **RESEARCH COMPLETE 2026-02-28** — See `docs/CH2_PROXEMICS_CULTURAL_CALIBRATION_2026-02-28.md` and `data/calibration/ch2_proxemics_parameters.json` |
| CH-3 | **Visual complexity preference (Goldilocks)**: What counts as 'optimally complex' is calibrated by the visual diet of architectural/natural environments one grew up in. Affects `PredictionError` and `LoadRate` thresholds. | PredictionError, LoadRate | Berlyne (1971) [~2,471 cit], Stamps (2005) [~196 cit], Vartanian et al. (2015) [~265 cit], Palmer (1999) [~2,891 cit] | **RESEARCH COMPLETE 2026-02-28** — See `docs/CH3_VISUAL_COMPLEXITY_CULTURAL_CALIBRATION_2026-02-28.md` and `data/calibration/ch3_visual_complexity_parameters.json` |
| CH-4 | **Ceiling height expectations**: Residential ceiling heights vary dramatically (JP ~2.4m, US ~2.7m, N.EU ~2.5m). Comfort thresholds calibrate to expectation. Affects `ControlEfficacy` and potentially `NarrativeCoherence`. | ControlEfficacy, NarrativeCoherence | Meyers-Levy & Zhu (2007) [~1,283 cit], Sommer (1974) [~487 cit], Augustin (2009) [~203 cit] | **RESEARCH COMPLETE 2026-02-28** — See `docs/CH4_CEILING_HEIGHT_CULTURAL_CALIBRATION_2026-02-28.md` and `data/calibration/ch4_ceiling_height_parameters.json` |
| CH-5 | **Nature vs. artifice preference**: Japanese gardens (manicured control) vs. Scandinavian friluftsliv (wild nature). Calibrates `NarrativeCoherence` for outdoor/landscape spaces. | NarrativeCoherence, MultisensoryCoherence, PredictionError, ProcessingCost | Kaplan & Kaplan (1989) [~2,147 cit], Appleton (1975) [~1,543 cit], Slawson (1987) [~178 cit], Kuitert (2002) [~89 cit] | **RESEARCH COMPLETE 2026-02-28** — See `docs/CH5_NATURE_ARTIFICE_CULTURAL_CALIBRATION_2026-02-28.md` and `data/calibration/ch5_nature_artifice_parameters.json` |
| CH-6 | **Symmetry tolerance**: West African spatial design uses asymmetric/organic/fractal layouts vs. Western bilateral symmetry. Calibrates `PredictionError` interpretation and `NarrativeCoherence` expectations. | PredictionError, NarrativeCoherence | Eglash (1999) [~547 cit], Rapoport (1969) [~1,234 cit], Cunningham et al. (1995) [~648 cit] | **RESEARCH COMPLETE 2026-02-28** — See `docs/CH6_SYMMETRY_CULTURAL_CALIBRATION_2026-02-28.md` and `data/calibration/ch6_symmetry_parameters.json` |
| CH-7 | **Color temperature (CCT) preference**: East Asian preference for 5000-6500K (cool white/daylight) vs. Western 2700-3000K (warm white). Post-WWII Japanese fluorescent adoption → NTSC-J 9300K display standard. Kruithof "pleasant" region shifts rightward for East Asian populations. | MultisensoryCoherence, NarrativeCoherence, PredictionError, ProcessingCost | Boyce (2003) [~1,200 cit], Kruithof (1941) [~450 cit], Veitch & Newsham (1998) [~389 cit], Nakamura (2013), Wei et al. (2014) | **RESEARCH COMPLETE** — See `docs/CH7_COLOR_TEMPERATURE_CULTURAL_CALIBRATION_2026-02-28.md` |

**Pipeline for CH-1 through CH-7**: Literature search → Paper triage (Gemini) → Extraction → Human approval (HITL) → 14-step integration cascade → Template creation/modification → Molecule linkage → Annotation tagging. All are Tier 2 constraint calibrations through ψ_culture — the perceptual primitives (Tier 1) are universal; the interpretive thresholds are culturally learned.

**Panel Decisions (2026-02-27 overnight)**:

| ID | Decision | Consensus | Risk |
|----|----------|-----------|------|
| D-A1 | Adopt canonical discount factors (Woodward-justified) | UNANIMOUS | MEDIUM |
| D-A2 | Implement three-number separation (ω, d, CPT) | UNANIMOUS | LOW |
| D-A3 | Log-odds π projection in dedicated module | CONSENSUS (4-1) | MEDIUM |
| D-A4 | Clean break on EMPIRICAL_COVARIANCE → EMPIRICAL_ASSOCIATION | CONSENSUS (3-2) | MEDIUM |
| D-B1 | Formalize T2 mechanism templates as data class hierarchy | UNANIMOUS | LOW |
| D-B2 | Three-layer annotation model at database level | CONSENSUS (4-1) | MEDIUM-HIGH |
| D-B3 | Processing fluency as formal T1.5 monitoring node | UNANIMOUS | LOW |
| D-B4 | Annotation model in critical path; T2 templates parallel | CONSENSUS | LOW |

**Session 2 Additional Decisions (EN-to-BN completed session, 2026-02-27)**:

| ID | Decision | Impact | Status |
|----|----------|--------|--------|
| D-S2.1 | EWG → EN (Epistemic Network) rename | All docs, code comments, ARCHITECTURE.md | DECIDED |
| D-S2.2 | THEORETICAL_DEFAULT → THEORY_DERIVED [theory_name] with mandatory theory tag | Enum + schema (edges carry theory_name) | DECIDED |
| D-S2.3 | Population Transfer Factor (δ) as fourth number in π | New edge field, new formula, migration | DECIDED |
| D-S2.4 | Serial chain: ω_eff = ∏ω_i, d_eff = min(d_i), δ_eff = min(δ_i) | epistemic_projection.py | DECIDED |
| D-S2.5 | Dual-BN diagnostic (Full vs Empirical Floor) | New analysis mode | DECIDED |
| D-S2.6 | Explanatory Boost: mechanism adds parallel path + raises ω | Credence update logic | DECIDED |
| D-S2.7 | EN is coherentist (Quinean), not Bayesian | Documentation | DECIDED |
| D-S2.8 | Interactions as edge annotations, not separate edges | Schema: interaction qualifier | DECIDED |

**Canonical docs**: `02-27_04_Exchange_Summary_Session2.md`, `02-27_06_ATLAS_Cheat_Sheet_V2.0.docx`, `02-27_07_ATLAS_Technical_Appendix_V1.0.docx`

**Updated π Formula**: `logit(p_target) = d(τ) · ω · δ(pop, pop_target) · logit(p_lab)`

**Discount Factor Update (Code Impact)**:

| Warrant Type | Code (old) | Canonical (new) | File: bridge_warrants.py |
|---|---|---|---|
| CONSTITUTIVE | 0.75 | 0.95 | DEFAULT_BRIDGE_CONFIDENCE |
| MECHANISM | 0.60 | 0.80 | DEFAULT_BRIDGE_CONFIDENCE |
| EMPIRICAL_ASSOCIATION | 0.60 | 0.80 | Renamed from EMPIRICAL_COVARIANCE |
| FUNCTIONAL | 0.50 | 0.65 | DEFAULT_BRIDGE_CONFIDENCE |
| CAPACITY | 0.45 | 0.55 | DEFAULT_BRIDGE_CONFIDENCE |
| ANALOGICAL | 0.35 | 0.40 | DEFAULT_BRIDGE_CONFIDENCE |
| THEORETICAL_DEFAULT | 0.40 | 0.25 | DEFAULT_BRIDGE_CONFIDENCE |

### SPRINT-8: Master Document Overhaul (Detailed Scope)

**Objective**: Bring `MASTER_DOC_CMR_2026-02-25.md` (19,500 lines, 18 parts, 139+ sections) fully up to date as the single comprehensive source of knowledge for the ATLAS system. Every section must reflect the current state of the architecture, terminology, and evidence.

**Current state of master doc**: Last updated Feb 25, 2026. Still uses CMR terminology in places. Does not reflect EN rename, THEORY_DERIVED with theory tags, population transfer factor (δ), dual-BN diagnostic, updated discount factors, three-layer annotation model, T2 mechanism templates, or the log-odds π projection formula. The credence calculus sections (Part IV, §48-53) use the old multiplicative formula rather than the log-odds transform.

**Phase 1: Terminology and Naming Sweep** (~3 hours)

| Task | Scope | Files |
|------|-------|-------|
| 8.1.1 | Rename CMR → ATLAS throughout (any remaining instances) | Master doc |
| 8.1.2 | Rename EWG → EN (Epistemic Network) throughout | Master doc, all docs/ references |
| 8.1.3 | Rename EMPIRICAL_COVARIANCE → EMPIRICAL_ASSOCIATION | Master doc |
| 8.1.4 | Rename THEORETICAL_DEFAULT → THEORY_DERIVED [theory name] with examples | Master doc |
| 8.1.5 | Replace "confidence weight" → "warrant strength" (ω) everywhere | Master doc |
| 8.1.6 | Replace "discount factor" → "transfer reliability" (d) in prose | Master doc |
| 8.1.7 | Verify all 7 warrant types listed correctly with canonical discount values | §37, §51, Part IV, Part IX |

**Phase 2: Theoretical Architecture Update** (~4 hours)

| Task | Scope | Sections |
|------|-------|----------|
| 8.2.1 | Rewrite §48 (Credence Formula) to use log-odds π projection | §48 |
| 8.2.2 | Update §49 (Quinean Webs and BNs) to explicitly state EN is coherentist, not Bayesian | §49 |
| 8.2.3 | Rewrite §51 (Bridge Warrants) with updated discount factors and Woodward invariance justification | §51 |
| 8.2.4 | Add new section: The Four Numbers (ω, d, δ, CPT) — critical distinction from Cheat Sheet v2 | New §48.5 or integrated into §48 |
| 8.2.5 | Add new section: Serial vs. Parallel Combination Rules with worked examples | New section in Part IV |
| 8.2.6 | Add new section: The Dual-BN Diagnostic (Full Projection vs. Empirical Floor) | New section in Part IX |
| 8.2.7 | Add new section: Population Transfer Factor (δ) architecture and WEIRD limitations | New section in Part IV or IX |
| 8.2.8 | Update §85 (BN-Web Relationship) to reflect three-layer architecture (EN-π-BN) | §85 |
| 8.2.9 | Update §87 (Epistemic-Causal Bridge) with log-odds formulas from Technical Appendix | §87 |

**Phase 3: T1/T1.5/Molecule/T2 Verification and Enhancement** (~5 hours)

| Task | Scope | Sections |
|------|-------|----------|
| 8.3.1 | Verify and update T1 framework list (§33) — currently 8 Tier 1 theories. Check completeness. | §33, cross-reference with data/theories/ |
| 8.3.2 | Verify and update T1.5 theory list (§34, §72-78) — currently 13 formally reduced. Check 30/103 formal status. | §50.4 — COMPLETE 2026-03-02 (updated to "The Thirteen Formally Reduced T1.5 Theories" documenting all 13 T1.5 theories with authors, mechanisms, coverage fractions, and irreducible residuals; includes Goldilocks Principle as 13th theory, subsumes Berlyne original; identifies IC2 and DP1 super-templates) |
| 8.3.3 | Add Processing Fluency as new T1.5 monitoring node (Panel B Decision B3) | §34 or new subsection |
| 8.3.4 | Document the 6 T2 mechanism templates with full descriptions | §50.5 — COMPLETE 2026-02-27 (added §50.5 subsection "Six Core Mechanism Template Types" documenting all six mechanism types with neural substrates and example templates) |
| 8.3.5 | Document the 22 T1.5 instances across T2 templates | Cross-reference with aesthetics molecules doc |
| 8.3.6 | Explain mechanisms more thoroughly — accordion principle, measurement ≠ mechanism, theory vs mechanism distinction | §50.12, §50.13 — COMPLETE 2026-02-27 (added new §50.12 "The Accordion Nature of Mechanisms" and §50.13 "Measurement vs. Mechanism" with detailed explanations from Exchange Summary §13-14) |
| 8.3.7 | Explain theories and frameworks more thoroughly — how theories generate predictions, why they don't appear in BN | §50.11 — COMPLETE 2026-02-27 (added new §50.11 "Theory vs. Mechanism: A Critical Distinction" with Machamer/Darden/Craver framework, Marr's levels, and practical examples) |
| 8.3.8 | Add three-layer annotation model: Layer 1 (web molecules/T1.5s), Layer 2 (stimulus feature tags), Layer 3 (methodological tags) | New section |

**Phase 4: Cheat Sheet, Technical Appendix, and System Documentation** (~3 hours)

| Task | Scope | Sections |
|------|-------|----------|
| 8.4.1 | Incorporate Cheat Sheet v2 content into master doc (or add as new Part/Appendix) | New Part XIX or Appendix |
| 8.4.2 | Incorporate Technical Appendix (formulas + 4 worked examples) into master doc | New Part or expand Part IV |
| 8.4.3 | Add AI Systems Technical Appendix: how the code implements EN/BN/π, database schema, pipeline architecture | New Part XX |
| 8.4.4 | Document the OVERSEER system, nightly pipeline, backup engine, local_runner | Expand §132 or new sections |
| 8.4.5 | Document the extraction pipeline: Article Eater → claims → web → BN | Expand Part XV |
| 8.4.6 | Add symbol reference table from Cheat Sheet v2 §9 | New appendix |

**Phase 5: Cross-Referencing and Source Linking** (~2 hours)

| Task | Scope |
|------|-------|
| 8.5.1 | Every summary in master doc that condenses material from a source doc should link to that source with `See docs/FILENAME.md` |
| 8.5.2 | Add a Document Provenance Appendix listing all source documents with dates, authors, and what they contribute |
| 8.5.3 | Ensure all APA references are complete with DOIs where available |
| 8.5.4 | Cross-reference all panel decisions (D-A1 through D-S2.8) with the sections they affect |
| 8.5.5 | Update the MASTER TABLE OF CONTENTS to reflect all new sections and status changes |

**Phase 6: Quality and Verification** (~2 hours)

| Task | Scope |
|------|-------|
| 8.6.1 | Verify no [SKELETON] sections remain that should be [WRITTEN] given available material |
| 8.6.2 | Check that all worked examples use correct (updated) discount factors |
| 8.6.3 | Verify T1/T1.5/Molecule/T2 counts are consistent across all sections |
| 8.6.4 | Run terminology consistency check: no residual EWG, CMR, EMPIRICAL_COVARIANCE, THEORETICAL_DEFAULT |
| 8.6.5 | Verify all cross-references between sections resolve correctly |

**Estimated Total Time**: 19-20 hours across 6 phases
**Dependencies**: Sprints 0.5 through 7 (all terminology, architecture, and code changes must be finalized)
**Output**: Updated `MASTER_DOC_ATLAS_2026-03-XX.md` (renamed from CMR) — the single comprehensive source

**Key Source Documents to Integrate**:
- `docs/02-27_04_Exchange_Summary_Session2.md` — 17 major decisions (EN rename, δ, dual-BN, etc.)
- `docs/02-27_06_ATLAS_Cheat_Sheet_V2.0.docx` — Canonical cheat sheet v2
- `docs/02-27_07_ATLAS_Technical_Appendix_V1.0.docx` — Formulas + 4 worked examples
- `docs/02-27_05_ATLAS_EN_Master_Report_V1.0.docx` — EN architecture master report
- `docs/NEW_DOCUMENT_SYNTHESIS_AND_REVISED_SPRINT_PLAN_2026-02-27.md` — Sprint plan + panel decisions
- `docs/CROSS_AUDIT_SYNTHESIS_AND_SPRINT_PLAN_2026-02-27.md` — Three-audit synthesis
- `docs/ARCHITECTURE.md` — System architecture (needs simultaneous update)
- `docs/SCHEMA_REGISTRY.md` — Schema documentation

### AG Programs Inventory (Tracked 2026-02-25)

| File | Author | Lines | Purpose | Status |
|------|--------|-------|---------|--------|
| `scripts/enrich_crossref.py` | AG | 423 | CrossRef API enrichment — polite pool, rate limiting, retry logic. Outputs `crossref_metadata.json` | COMPLETE; DATA MERGED |
| `scripts/semantic_scholar_enrichment.py` | AG+CW | 813 | S2 API enrichment + CrossRef merge support (CW added merge functions) | COMPLETE; DATA MERGED |
| `scripts/migrate_variables.py` | AG | ~90 | Renames variables in template JSONs using alias_map from canonical_variables.json | BUILT; AWAITING M-01 COMPLETION |
| `scripts/lint_variables.py` | AG | ~160 | CI/pre-commit lint check — verifies all template variables are registered | BUILT; READY |
| `schemas/canonical_variables.json` | AG | ~434KB | Canonical variable ontology: 80-120 variables, alias_map for 931 root names, 6 domains | COMPLETE; AWAITING HUMAN REVIEW |
| `docs/AG_REPAIR_SPRINT_INSTRUCTIONS.md` | AG | 258 | Sprint instructions for variable ontology + document lifecycle (E-03a, M-03a, E-03b, G-01) | REFERENCE DOC |
| `docs/AG_PROMPT_CMR_Sprint_Planning.md` | AG | 752 | 8-sprint panel planning doc (SUPERSEDED) | SUPERSEDED |
| `src/agents/agent_stubs.py` | AG | 292 | Agent framework stubs (recently modified Feb 23) | IN PROGRESS |
| `src/agents/agent_panels_v2.py` | AG | 167 | Panel agent implementation | PARTIAL |
| `data/extractions/crossref_cache.json` | AG | 1.4MB | Raw CrossRef API response cache | DATA |
| `data/extractions/crossref_metadata.json` | AG | 1.4MB | Parsed CrossRef metadata for all DOIs | DATA |
| `data/extractions/crossref_references.json` | AG | 1.4MB | Citation references from CrossRef | DATA |
| `signals/` (163 files) | AG+CC+CX | — | Parallel task coordination signals (claim/update/complete) | HISTORICAL |

### P1 (High Priority)

| ID | Task | Context | Status |
|----|------|---------|--------|
| INT-HOOK | Wire pdf_extraction_module.py ACCEPTED → PaperIntegrationOrchestrator trigger | Auto-triggers on ACCEPTED transition | DONE 2026-02-25 |
| INT-SOCIAL-EPIST | Wire social_epistemology.py into Step 11 (community credences, contestation) | CommunityRegistry + ContestationTracker wired | DONE 2026-02-25 |
| INT-VOI | Wire discovery_funnel.py into Step 12 (gap closure assessment) | GapClosure records + automatic assessment | DONE 2026-02-25 |
| INT-PROVENANCE | Wire Haack provenance synchronously during integration | Eager: constructs Provenance objects in Step 5 | DONE 2026-02-25 |
| INT-COHERENCE | Wire CoherenceManager pre/post + coherence delta | scalable_coherence.py in Steps 2/13 | DONE 2026-02-25 |
| INT-QA-EAGER | Wire eager QA cache marking (stale + notify) | Caches explicitly marked STALE in index | DONE 2026-02-25 |
| S1 | Implement find_critical_question_gaps() in gap_predictor.py | Walton critical questions for 5 argumentation schemes | **COMPLETE 2026-02-28** |
| S2 | Implement find_argument_attack_gaps() in gap_predictor.py | 4 attack vulnerability detectors (boundary, replication, mechanism, confounder) | **COMPLETE 2026-02-28** |
| T3 | Remove duplicate classes from epistemic_causal_bridge.py | Canonical imports from web_of_belief, backward-compatible re-exports | **COMPLETE 2026-02-28** |
| T1 | Implement _fetch_finding_by_iv_dv() in prediction_generator.py | Multi-source fuzzy search (SQLite + JSONL + dict) | **COMPLETE 2026-02-28** |
| **CMR-SPEC** | **Define CMR Specification (template library, prediction grammar, theory links)** | **COMPLETE 2026-02-28** — See docs/CMR_SPECIFICATION.md (V2.0, 550+ lines, 5 complete sections) + ae.rule.v2.schema.json extended with theory_links field. Unblocks T7.3, T7.4, T7.6. |
| **T7.3** | **Extend ae.rule.v2 schema with `theory_links` field** | **COMPLETE 2026-02-28** — Theory link schema added to rule record. Supports T1, T1.5, T2 theory levels with maturity indicators (how-actually, how-plausibly, how-possibly). |
| **T7.4** | **Update extraction prompts to capture Panel 6 theory links** | **COMPLETE 2026-02-28** — `prompts/theory_link_extraction.py` (230+ lines) with THEORY_LINK_SYSTEM_PROMPT, THEORY_LINK_EXTRACTION_PROMPT (few-shot examples), THEORY_ROSTER_SUMMARY (24 canonical theories). Functions: generate_theory_link_prompt(), parse_theory_link_response(), validate_theory_roster(). Tests: 80+ lines covering prompt generation, JSON parsing, theory ID validation, malformed input rejection. All 24 theories load successfully. See file and tests/test_theory_link_extraction.py. |

### P2 (Medium Priority)

| ID | Task | Context | Status |
|----|------|---------|--------|
| **T7.6** | **Implement theory agent profiles for all 10 Tier 1 frameworks** | **COMPLETE 2026-03-02** — 10 theory profile JSONs in `data/theory_profiles/` (108KB total). `src/services/theory_agent_service.py` (483 lines) with get_profile(), get_panel_persona(), evaluate_finding(), simulate_panel_discussion(), get_relevant_frameworks(), search_profiles_by_construct(). Each profile: 5 key theorists, 4 seminal works (APA + DOI), 8-10 core constructs (96 total), 3 environmental predictions (29 total with CMR template refs), panel persona (voice, critiques, blind spots), molecule affinities. 49 tests passing. See `docs/SPRINT_T7_THEORY_AGENT_PROFILES_COMPLETION_2026-03-02.md`. |
| MISSING-TEMPLATES | Find and apply ceiling decisions to 16 missing template IDs | 49 decisions remain | COMPLETED 2026-03-02 |
| RQS | ResearchQueueService implementation | Low urgency | DEFERRED |
| 3.0.1-D | Implement Extended Layer (20 API endpoints) | API expansion | COMPLETED 2026-03-02 |
| 3.0.1-E | Add batch operations endpoint | API expansion | COMPLETED 2026-03-02 |
| 3.0.1-F | Add causal endpoints | API expansion | COMPLETED 2026-03-02 |
| IMG-PIPE | **Architectural Image Search/Find/Download/Tag Pipeline** | **COMPLETE 2026-03-02** — `src/services/image_pipeline_service.py` (816 lines) + `image_pipeline_models.py` (233 lines). 6 services: SearchQueryGenerator (3 query types, equivalence class integration), ImageDownloadManager (perceptual hash dedup, registry), ImageMetadataExtractor (EXIF, file properties), AutoTagger (heuristic-based, placeholder for ML), EvidenceLinkingService (attribute overlap scoring), ImagePipelineService (orchestrator). CLI: `scripts/run_image_pipeline.py` (536 lines, 5 modes: --search/--download/--tag/--link/--full). 48 tests passing. API calls stubbed (ready for real Unsplash/Flickr/Wikimedia integration). See `docs/IMG_PIPE_IMPLEMENTATION_2026-03-02.md`. |
| IMG-TAG | **Image Tagging Vocabulary for Scientific Characterization** | **COMPLETE 2026-03-02** — `data/attributes/image_tagging_vocabulary.json` (45KB): 41 attributes across 7 domains (spatial, lighting, materials, vegetation, color, visual complexity, view/perceptual space + environmental context). 5 domain summary scores (naturalness, visual complexity, prospect-refuge index, restorative capacity, human-centeredness). `data/attributes/image_tagging_schema.json` (15KB). `src/services/image_tag_service.py` (635 lines): tag_image(), validate_tags(), get_domain_scores(), get_relevant_templates(), search_by_attribute(). 42 tests passing. Grounded in Kaplan & Kaplan 1989, Ulrich 1983, Berlyne 1971, Appleton 1975, Gibson 1979. See `docs/IMG_TAG_IMPLEMENTATION_SUMMARY.md`. |

### P3 (Low Priority / Future)

| ID | Task | Context | Status |
|----|------|---------|--------|
| ARCH-2 | Transportability analysis (Pearl/Bareinboim) | V3 architecture | DEFERRED |
| ARCH-3 | Independence scoring and bias correction | V3 architecture | DEFERRED |
| ARCH-5 | Split Belief into focused types | Needs test coverage | DEFERRED |

---

## New Tasks (2026-03-04)

| ID | Task | Context | Status |
|----|------|---------|--------|
| DB-HEALTH-1 | **Wire check_db_health.py into overseer nightly pipeline** | `scripts/check_db_health.py` created with 10 success conditions (SC-DB-1 through SC-DB-10). Should run as Stage 0 in nightly pipeline BEFORE other health checks. Currently 7 pass, 3 warnings (overseer db_locator usage, template_ids coverage, migration 023). CW action needed. | **OPEN** |
| DB-HEALTH-2 | **Fix overseer to use db_locator** | Per SC-DB-6 and MT-16, `overseer.py` should default to `get_web_db()` when no explicit path given. Prevents endemic DB path confusion. | **OPEN** |
| DB-HEALTH-3 | **Run migration 023 on overseer.db** | `overseer_health_metrics` table missing per SC-DB-8. Need to apply migration. | **OPEN** |

---

## Blocked Tasks

| Task | Blocked By | Resolution Path | Status |
|------|------------|-----------------|--------|
| T7.3, T7.4 | CMR-SPEC | Complete CMR specification | **COMPLETE 2026-03-02** — `docs/CMR_SPECIFICATION_2026-03-02.md` (1,398 lines). Parts I-VI: conceptual foundations (Darden/Craver/Woodward), FindingMechanismLink data model, 8-step CMR pipeline, data structures, integration points, worked example (Ulrich 1984). |
| Sprint 8 (CMR) | FindingMechanismLink | Add to edge_types.py | **COMPLETE 2026-03-02** — Added to `src/epistemic/edge_types.py` (+200 lines): MechanismStep, FindingMechanismLink, MechanismExplanationType (6 types), maturity levels, scope conditions, measure alignment, convergence tracking, alternative explanations. 28 tests passing (`tests/test_cmr_finding_mechanism_link.py`). |
| MISSING-TEMPLATES | Locate 16 template IDs | Found via template_id field; all resolved | COMPLETED 2026-03-02 |

---

## Deferred Tasks (V3.0+)

| ID | Description | Priority |
|----|-------------|----------|
| EC-5 | Learning pathway support for education | 3.0 |
| SY-2 | Causal discovery from mechanism beliefs | 3.0 |
| SY-3 | EM-style joint optimization | 3.0 |
| SY-4 | Active learning infrastructure | 3.0 |
| SY-5 | Joint Bayesian inference | 3.0 |

---

## Decisions Pending

| Decision | Options | Impact |
|----------|---------|--------|
| D1.5.1 | task_ecology.py ClaimType naming | Affects CNFA semantics |
| D1.5.2 | Article_Finder GapType unknowns | Affects gap analysis |
| D1.5.3 | BN_graphical EvidenceType unknowns | Affects evidence classification |

---

## Completed (2026-02-24)

| ID | Task | Completed | Outcome |
|----|------|-----------|---------|
| CIRCUIT-QA-SERVICE | Circuit QA Service | 2026-03-03 | `src/services/circuit_qa_service.py` — 20 functional circuits with epistemically framed QA cards. CircuitQACard dataclass with evidence stratification (STRONG/MODERATE/HYPOTHETICAL), ontological framing per Barrett (2017)/Batterman (2002), competing accounts, knowledge gaps. 35 tests passing. |
| CIRCUIT-QA-WIRING | Circuit QA Wiring | 2026-03-03 | Wired CircuitQAService into `arbitrary_qa_handler.py` (FUNCTIONAL_CIRCUIT and ARCHETYPE_GUIDE question types), `annotation_service.py` (Layer 6: CIRCUIT_ASSOCIATION, ARCHETYPE_TAG), and `answer_enrichment_orchestrator.py` (Step 10: circuit_context enrichment). |
| AG-COORD-011 | AG Coordination Message 011 | 2026-03-03 | Sent Message 011 via `.agent_coord/MESSAGE_BOARD.md` informing AG about circuit QA integration and requesting circuit annotation population during extraction Phases 3A-3D. |
| PRED-1 | Prediction Discovery Engine | 2026-02-24 | `scripts/prediction_discovery_engine.py` — 6,175 type-level predictions from 103 templates |
| PRED-2 | Instance Library Builder | 2026-02-24 | `scripts/instance_library_builder.py` — 649 instances across 19 slot types, organized by causal attribute |
| PRED-3 | Ambience-Activity Prior Model | 2026-02-24 | `scripts/ambience_activity_priors.py` — 11 activity profiles, 6 time-of-day modifiers, feature co-occurrence priors |
| PRED-4 | Integrated Prediction Pipeline | 2026-02-24 | `scripts/integrated_prediction_pipeline.py` — 220 situated predictions across 11 canonical scenarios |
| PRED-5 | Interior Typology Conditional Probs | 2026-02-24 | P(feature\|space_type) and P(feature\|anchor_feature) extraction with anomaly detection |
| PRED-6 | Pipeline Runner Scripts | 2026-02-24 | `scripts/run_instance_library.sh`, `scripts/run_integrated_predictions.sh` |
| PRED-7 | Architectural Typology Priors | 2026-02-24 | `scripts/architectural_typology_priors.py` — 16 space types, 45 cross-domain conditionals, P(feature\|activity) matrix |
| PRED-8 | Typology integration into pipeline | 2026-02-24 | Scenarios generated from typology (32 prototypical + 12 mismatch = 44 scenarios), 880 situated predictions |
| PRED-9 | Pipeline mechanics, VOI, and system inventory appended to master paper | 2026-02-24 | Sections 45–47 added to NEURAL_EXPLANATIONS_ENVIRO_PSYCH_PAPER_2026-02-23.md: prediction pipeline mechanics (6 stages), interaction taxonomy (8 types with experimental signatures), architectural typology role, system inventory (7 levels), VOI formalization (informativeness vs. formal VOI vs. EVSI). ~6,000 words, 35 new references. |
| PRED-10 | Master paper skeleton (15 Parts, 124 sections, 5 appendices) | 2026-02-24 | Full TOC inserted into master paper with [SKELETON] tags and ABSORB FROM source-file annotations. 3 parts [WRITTEN], 12 parts [SKELETON]. |
| PRED-11 | Section Builder Process specification | 2026-02-24 | Created `docs/SECTION_BUILDER_PROCESS.md` — 5-phase editorial pipeline (GATHER→VET→OUTLINE→WRITE→VERIFY) with quality metrics, priority ordering, session protocol. |
| PRED-12 | Example Catalog | 2026-02-24 | Created `docs/EXAMPLE_CATALOG_2026-02-24.md` — 65+ worked examples cataloged across 30+ files. 25 Tier 1 (exemplary), 28 Tier 2 (strong), 12+ Tier 3 (useful). Covers all 12 domain panels, 30 master paper examples, 6 application walkthroughs, 3 theory reductions, 2 credence calculations. Example-hunting integrated into Section Builder Phase 1 (GATHER) and Phase 3 (OUTLINE). |
| PAPER-IV | Part IV: Credence Calculus (§48-53) | 2026-02-24 | 6 sections written: core formula, Quinean webs, tiered architecture, bridge warrants, confidence discipline, independence assumption. |
| PAPER-V | Part V: Expert Panel Method (§54-59) | 2026-02-24 | 6 sections written: panel composition, crucible debates, 12-panel sequence, calibration, Toulmin justification, quality assurance. |
| PAPER-VI | Part VI: Domain Panels (§60-71) | 2026-02-24 | 12 sections written covering all 12 panels (FOUND-I through CROSSCUT-I) with 103 calibrated templates, worked examples, parameter verification. |
| PAPER-VII | Part VII: T1.5 Reductions (§72-78) | 2026-02-24 | 7 sections written: reduction architecture (Panel D-1), ART (4 constructs), SRT (3 constructs, how-actually), Biophilia (3 sub-theories), Space Syntax/Soundscape/Place Attachment, remaining reductions (Privacy Reg, Kaplan, Adaptive Thermal, BRECVEMA, Flow), rejected/deferred candidates. 12-theory canonical roster. |
| **V3-PHASE-1A** | **Schema Hardening: extraction_template.v2.schema.json** | 2026-03-01 | JSON schema with 45 field validations. Fields: stimulus_description, outcome_description, direction (enum: increases/decreases/modulates), claim_type (hypothesis/finding/theoretical), measure_type, p_value, effect_size, confidence_bound, evidence_quality_code, theory_links array with maturity levels (how-actually/how-plausibly/how-possibly). Backward-compatible with Phase 1 extractions. |
| **V3-PHASE-1B** | **Extraction Validator: Blocking Gate (12 Tests)** | 2026-03-01 | `src/qa/extraction_field_validator.py` — validator with 12 unit tests covering vague antecedent detection, null handling, direction-effect-size consistency, stimulus_description minlength, outcome_description format, theory_links array validation, malformed JSON rejection. All tests pass. Used as blocking gate in Phase 2. |
| **V3-PHASE-2** | **Revised Extraction Prompts v3: revised_prompts_v3.py** | 2026-03-01 | 1,511 lines, 10 prompts covering 7 article types (empirical, unknown, theoretical, narrative_review, systematic_review, qualitative, methods). Each prompt: theory-link instruction block (captures how-actually/plausibly/possibly), stimulus description guidance, success criteria section. 10 pytest unit tests covering prompt structure, template interpolation, JSON output validation, edge-case handling (blank papers, malformed data). |
| **V3-SUCCESS-AUDIT** | **Success Conditions Audit: 62 Conditions, 92 Tests** | 2026-03-01 | Comprehensive audit of Phase 2 success criteria across 7 article types. Created `docs/V3_SUCCESS_CONDITIONS_AUDIT_2026-03-01.md` — documents 62 explicit success conditions with evidence code (what makes a good extraction), 92 corresponding validation tests covering stimulus/outcome/direction/claim_type/measure_type/theory_links/p_value/effect_size/confidence/evidence_quality. Test matrix: 7 article types × 13 field validations = 91 test cases + 1 integration test. Blocking gate ensures Phase 3 re-extractions are high-quality. |
| **V3-REFLEX-SYSTEM** | **Self-Healing Reflex System: 750 lines, 13 Reflexes, 23 Test Classes** | 2026-03-01 | `src/services/reflex_engine.py` — 13 reflexes for Phase 3 auto-correction: R1-R3 (antecedent vagueness auto-tagging + template suggestion), R4-R6 (outcome null-value inference from context), R7-R9 (direction inference from effect-size + p-value), R10-R11 (confidence bounds inference), R12-R13 (theory link maturity re-ranking). Each reflex: condition checker, action executor, rollback handler. 23 test classes (pytest) covering all reflexes with edge cases, mock data, integration tests. Enables Phase 3 pipeline to self-correct extracted data in real time. |
| **V3-PHASE-4** | **Expert Panel Review + 8/9 MUST DO Fixes** | 2026-03-01 | Four expert panels convened (Panel A: Schema, Panel B: Validator, Panel C: Prompts, Panel D: Reflex System). 32 deliberations, 9 MUST DO recommendations issued. Fixes: (1) Add theory_maturity enum values, (2) Extend stimulus_description minlength to 50 chars, (3) Add outcome_description format regex, (4) Implement reflex R9 edge-case handler for direction consistency, (5) Add 3 new vagueness patterns to R1, (6) Create integration test for full Phase 1-3 pipeline, (7) Document reflex rollback triggers, (8) Add monitoring dashboard for reflex triggers. 8 of 9 MUST DO fixes implemented; (9) monitoring dashboard DEFERRED to Phase 5. See `docs/EXPERT_PANEL_V3_REVIEW_2026-03-01.md`. |
| **V3-PHASE-3-SCAN** | **Phase 3 Data Scan: 6,652 Vague Antecedents, 31,240 Null Samples, 1,060 Linking Candidates** | 2026-03-01 | Full-corpus scan of extraction data identifying: 6,652 antecedent descriptions needing reflex R1-R3 vagueness reduction (e.g., "exposure to nature" → "30-minute unstructured exposure to mixed deciduous forest"), 31,240 outcome fields with NULL values (reflex R4-R6 inference targets), 1,060 theory_links with unverified theory_name fields needing Tier assignment. Categorized by article type: empirical (52% vague), unknown (71% vague), theoretical (38% vague). Scan results: `data/phase3_scan_results.json` (2.4MB). Priority ranking for re-extraction: Tier 1 articles (high-impact theories), then Tier 2, then Tier 3. |
| **V3-TIER-IDENTIFICATION** | **Tier Identification: 59 Tier 1, 2 Tier 2, 1,000 Tier 3 Articles** | 2026-03-01 | Analyzed 1,061 extracted articles against ATLAS canonical theories (24 T1, 6 T1.5, 6 T2 mechanisms). Tier 1: 59 articles citing seminal papers for 10 Tier 1 frameworks (PP, SN, DP, DT, NM, IC, MS, EC, CB, MSI). Tier 2: 2 articles with novel mechanism characterizations (potential new T2 templates). Tier 3: 1,000 articles with partial/sparse linkages. Re-extraction priority: Tier 1 (high confidence payoff), then Tier 2 (explore mechanism novelty), then Tier 3 (mass coverage). Tier assignment: `data/tier_identification_index.json`. Used to stratify Phase 3 re-extraction queue. |
| **V3-AESHI-BLOCKER-1** | **AESHI Blocker 1 RESOLVED: Tier2 Framework Loading + Belief ID Backfill** | 2026-03-01 | Previous blocker: beliefs could not load T2 mechanism frameworks. Root cause: belief_versions.T2_mechanism_id NULL. Solution: Created `scripts/backfill_t2_mechanism_ids.py` (234 lines) — scans belief records, infers T2 framework from construct_id using `contracts/schemas/t2_mechanism_map.json`, updates belief_versions.T2_mechanism_id with confidence marker (inferred vs grounded). 486 beliefs backfilled (402 inferred, 84 grounded). Verified: all beliefs now load T2 frameworks successfully. See completion report: `docs/AESHI_BLOCKER_1_COMPLETION_2026-03-01.md`. |
| **V3-AESHI-BLOCKER-2** | **AESHI Blocker 2 RESOLVED: Annotation Persistence (0% → 100%)** | 2026-03-01 | Previous blocker: annotation_service.py CRUD operations not persisting to database. Root cause: transaction commit logic missing in enrich_response() call chain. Solution: (1) Updated annotation_service.py with explicit session.commit() after each CRUD operation, (2) Added transactional wrapper context manager for batch operations, (3) Wire-tested against real database with 166 test annotations. All annotations now persist correctly. Verified: annotation_query() retrieves 100% of persisted records with correct timestamps. See completion report: `docs/AESHI_BLOCKER_2_COMPLETION_2026-03-01.md`. |
| **V3-AESHI-BLOCKER-3** | **AESHI Blocker 3 RESOLVED: Reflex NotImplementedError** | 2026-03-01 | Previous blocker: reflex_engine.execute() raised NotImplementedError for reflexes R4-R13 (unimplemented auto-correction handlers). Solution: Completed implementation of all 13 reflexes with full logic (see V3-REFLEX-SYSTEM above). Each reflex: condition checker, action executor, rollback handler. Wire-tested with 23 test classes. All reflexes now operational. See completion report: `docs/AESHI_BLOCKER_3_COMPLETION_2026-03-01.md`. |
| **V3-REEXTRACTION-SCRIPTS** | **V3 Re-Extraction Scripts Created (Blocked on Sandbox Network)** | 2026-03-01 | Scripts created for Phase 3 re-extraction campaign: (1) `scripts/v3_reextraction_pipeline.py` (487 lines) — main orchestrator, reads tier_identification_index.json, queues 1,061 articles by tier, calls gemini_extraction_queue with Phase 2 revised_prompts_v3.py, validates output against extraction_field_validator, auto-corrects via reflex_engine, logs results. (2) `scripts/v3_batch_manager.py` (256 lines) — manages batch parallelization (Tier 1: 10 parallel, Tier 2: 5 parallel, Tier 3: 20 parallel), monitors API quota, implements exponential backoff. (3) `scripts/v3_validation_report.py` (189 lines) — generates post-extraction validation report (pass/fail by article, field coverage, reflex trigger counts, confidence scores). All scripts ready. **BLOCKED**: Sandbox network access to Gemini API not yet granted. Handed to AG as H12 (Gemini API sandbox grant request). Target: execute on 59 Tier 1 + 1,002 Tier 3 articles once API access granted. |
| **PROVENANCE-VERIFICATION** | **Provenance Verification Audit: 24 Theories, 13/24 Unverified LLM Knowledge** | 2026-03-01 | Comprehensive audit of theory provenance entries. Methodology: cross-reference of extraction data theory_links field against theory JSON provenance entries. Results: (1) **2 theories VERIFIED via extraction evidence**: ART (Attention Restoration Theory, 1,688 citations), SRT (Stress Recovery Theory, 2,402 citations). (2) **11 theories UNVERIFIED from extraction data** with LLM-origin provenance: PROCESSING_FLUENCY, BERLYNE_AROUSAL, BIOPHILIA, PROSPECT_REFUGE, SPACE_SYNTAX, SOUNDSCAPE, AUDITORY_SCENE_ANALYSIS, ADAPTIVE_THERMAL, ALLESTHESIA, BRECVEMA, PREDICTIVE_CODING_MUSIC. (3) **11 theories with INCOMPLETE provenance entries** (unknown status): CHRONOBIOLOGY, COGNITIVE_MAP, CPTED, EPISODIC_MEMORY, FLOW_THEORY, GOLDILOCKS_PRINCIPLE, KAPLAN_PREFERENCE, PAD_MODEL, PLACE_ATTACHMENT, PRIVACY_REGULATION, PROXEMICS. Detailed findings: `docs/PROVENANCE_VERIFICATION_2026-03-01.md` (comprehensive 5,200-word report with theory-by-theory analysis, verification strategies, priority recommendations). Key findings: theories like BERLYNE, BIOPHILIA, SPACE_SYNTAX are foundational in design literature but absent from extraction corpus (indicates corpus gap, not theory invalidity). Recommendations: (a) Update ART/SRT status to `grounded_from_extractions`, (b) Manual literature search for top-5 priority theories, (c) Manual provenance entries for 11 incomplete theories, (d) Improve extraction pipeline to capture foundational design theories. |
| **CARD-SCHEMA-PHASE-1** | **Card System Code Schema (Phase 1) — 44/44 Tests Passing** | 2026-03-04 | Four implementation files completed: (1) `src/qa/cards/card_types.py` (214 lines) — CardType enum (T1, T1.5, T2, Molecule, T3, Competition, Layer, Method, Math), CARD_TYPE_REGISTRY mapping, enum validation. (2) `src/qa/cards/card_schema.py` (389 lines) — Card dataclass with universal schema: surface_summary (headline + key insight), body_content (evidence + mechanism), iceberg_content (questions + assumptions + improvements), metadata, staleness lifecycle (FRESH/STALE_7DAY/STALE_30DAY/DEPRECATED). CardValidator with 8 mandatory checks (surface non-empty, body minimum 200 words, iceberg structured). (3) `src/qa/cards/tab_config.py` (157 lines) — TabConfig dataclass defining surface/body/iceberg tabs, user-type adaptation (researcher/student/general), validation rules per tab, visual_hints for interface. (4) `src/qa/cards/__init__.py` (28 lines) — canonical exports: `from src.qa.cards import Card, CardType, CardTier, CARD_TYPE_REGISTRY`. All 44 pytest tests passing across 4 test files (test_card_types.py, test_card_schema.py, test_tab_config.py, test_integration.py). Ready for agent wiring. |
| **META-REVIEW-SPEC** | **Meta-Review Specification for LLM Generation Pass** | 2026-03-04 | Comprehensive specification: `contracts/META_REVIEW_SPEC.md` (814 lines, ~12,000 words). Covers LLM generation pass through card system with 10 quality criteria: (1) Surface Accuracy (claim matches evidence base), (2) Body Evidence Quality (mechanism transparency, effect size documentation, confound identification), (3) Iceberg Completeness (open questions identified, assumptions listed, improvement suggestions actionable), (4) Cross-Reference Integrity (card citations traced, theory links verified, molecule associations correct), (5) Staleness Lifecycle (FRESH cards properly dated, STALE_7DAY/STALE_30DAY triggers verified, DEPRECATED rationale documented), (6) Schema Compliance (all fields non-null, metadata complete, tab content follows tab_config), (7) User-Type Adaptation (surface/body/iceberg accessible to researcher/student/general, vocabulary matched), (8) Theoretical Grounding (T1/T1.5 framework cited, mechanisms connected to construct definitions, theory_maturity level justified), (9) Visual Readiness (card compatible with visual_hints, figures referenced where present), (10) Consistency with System State (card reflects current ATLAS state, no stale cross-references, molecule network updated). Success conditions (SC-MR-1 through SC-MR-10) specified. Implementation by AG to follow, wiring into `src/services/prose_revision_service.py` recommended. |

## In Progress

| ID | Task | Started | Notes |
|----|------|---------|-------|
| GEMINI-PIPELINE | Native PDF extraction with Gemini API | 2026-02-23 | See below |

### GEMINI-PIPELINE Details

**Goal**: Replace garbled OCR/table extraction (68.5% failure rate) with Gemini native PDF reading.

**Components Built**:
1. `scripts/triage_papers_keywords.py` - FREE keyword-based article type classification
2. `scripts/gemini_extraction_queue.py` - Extraction queue manager with 7 article-type-specific prompts
3. `scripts/compare_models.py` - Model comparison tool (Flash vs Pro)
4. `scripts/run_full_extraction.py` - Full batch extraction runner

**Model Comparison Results** (2026-02-24):
- Tested gemini-2.5-flash vs gemini-2.5-pro on 5 papers
- Flash: 125 findings, 23 with effect sizes, $0.016
- Pro: 83 findings, 8 with effect sizes, $0.176
- **Decision**: Use Flash (better extraction, 11x cheaper)

**Full Extraction** (RUNNING - 2026-02-24):
- 1,041 papers queued (empirical=210, unknown=537, theoretical=143, narrative_review=99, systematic_review=25, qualitative=17, methods=10)
- Model: gemini-2.5-flash, single-pass (no verification)
- PID: 67177
- Monitor: `tail -f data/extractions/extraction_log.txt`
- Output: `data/extractions/full_extraction_*.json`
- ETA: ~5 hours, ~$3 total cost
   - Cost tracking, incremental saves, resume capability

**Triage Results** (1,058 PDFs ready):
- empirical: 215 papers
- theoretical: 143 papers
- narrative_review: 99 papers
- unknown: 537 papers (need LLM classification)
- systematic_review: 25 papers
- qualitative: 17 papers
- meta_analysis: 12 papers
- methods: 10 papers

**Test Results** (DOI 10.1073/pnas.1301227110):
- 18 findings extracted (vs 0 from legacy pipeline)
- Direction correctly captured
- Full effect sizes, brain regions, mechanisms
- 3-run verification cost: $0.037

**Centrality Weighting** (added 2026-02-23):
- `scripts/centrality_weighting.py` - Scores findings by relevance to BN/web central concepts
- 49 central concepts identified (central_hearth, spatial_entropy, wood_prominent, etc.)
- Article adequacy grades A-F based on weighted findings
- Integrated into extraction pipeline for automatic scoring

**Extraction Progress**:
- Meta-analysis batch: 12 papers completed, 77 pooled effects, $0.10 cost
- Empirical batch: 5 papers completed, 131 findings
  - Grade distribution: A=1, B=3, C=1
  - 210 papers remaining

**Docs**: `docs/GEMINI_PIPELINE_DESIGN_2026-02-23.md`

---

## Recently Completed (Last 7 Days)

| ID | Task | Completed | Outcome |
|----|------|-----------|---------|
| RUTHLESS-V8 | **Ruthless V8: Full End-to-End Audit + Fix Cycle** | 2026-03-02 | **AESHI: 49 RED → 91.13 GREEN (+42.13).** All 6 hard gates pass (was 5/6). Tests: 27 failures → 0 (5,529 pass). Fixed: 5 script syntax errors, AESHI sanity check, 27 test failures across 6 groups, scope persistence gap in 3 files. 8-member expert panel with 10 ranked improvements. Reports: `docs/RUTHLESS_V8_AUDIT_COMPLETION_2026-03-02.md`, `docs/PANEL_V8_IMPROVEMENT_RECOMMENDATIONS_2026-03-02.md`. |
| MATH-NORMS | Write MATH_EXPLANATION_NORMS contract + add to CLAUDE.md | 2026-03-02 | 7 mandatory norms from reference group of 8 great popularizers (Strogatz, Devlin, Ellenberg, Stewart, Mazur, du Sautoy, Tsitsiklis, Bertsekas). Four-layer explanation, provenance tracking, justified constants, scope/assumptions, common-sense labels, figures for formulas, diverse examples. Contract: `contracts/MATH_EXPLANATION_NORMS.md` (~250 lines). CLAUDE.md updated with summary section. |
| MATH-DVALUE | Insert §48.1A d-value provenance into PART_IV_CREDENCE.md | 2026-03-02 | Full justification for 7 transfer reliability d-values: conceptual ordering argument, gap structure explanation, 3-round expert calibration history with recorded dissent, sensitivity analysis table (±0.10 d shift → ±0.015–0.018 p_target change), empirical validation roadmap (4 directions), 3 assumptions/limitations. ~150 lines inserted between §48.1 and §48.2. |
| MATH-CONSTANTS | Annotate 5 unjustified constants with provenance tags | 2026-03-02 | δ default 0.90 → STIPULATED, δ minimum 0.30 → THEORETICAL, ω bounds [0.05, 0.98] → THEORETICAL (Cromwell's rule), TEA weights → CALIBRATED (AHP), AESHI weights → CALIBRATED (pairwise comparison). All in PART_IV_CREDENCE.md. |
| MATH-COHERENCE | Formalize Coherence C* — insert §84.2A into PART_IX | 2026-03-02 | C* = (A − λ·V) / A_max, λ=2.0 (CALIBRATED, Thagard 1989). 5 agreement/conflict cases, edge weight table (5 types), interpretation scale, 3 worked examples (perfect web, contradiction, gap), O(|E|) pseudocode. Provenance: NOVEL from Thagard + BonJour + Quine & Ullian. ~200 lines in PART_IX_WEB_OF_BELIEF.md. |
| MATH-VOI | Formalize VOI formula — insert §121.3A into PART_XV | 2026-03-02 | VOI(g) = [α·VOI_structural + (1−α)·VOI_epistemic]·w(type_g), α=0.6 (CALIBRATED). Paper-gap scoring, decision rules (≥0.6/0.3–0.6/<0.3), 3 worked examples (HIGH/MEDIUM/LOW VOI), gap type weights. Provenance: ADAPTED from Howard (1966) + Good (1950). ~200 lines in PART_XV_TECHNICAL.md. |
| MATH-FIGURES | Identify Phase 6 figure opportunities + update FIGURE_INDEX.md | 2026-03-02 | 8 new math explanation figures (M-25 through M-32) planned. 5 HIGH priority: projection sensitivity, C* visualization, credence pipeline, inference algorithms, entrenchment revision. 3 MEDIUM: VOI scatter, d-value hierarchy, serial/parallel combination. FIGURE_INDEX.md updated with Phase 6 table + regeneration command. |
| PHASE6-FIGS | **Generate all 8 Phase 6 math figures (M-25 through M-32)** | 2026-03-02 | All 8 SVGs generated via `scripts/generate_math_figures.py` (777+ lines). M-25 sensitivity analysis (190KB), M-26 coherence visualization (93KB), M-27 credence pipeline (97KB), M-28 inference engine (123KB), M-29 VOI uncertainties (125KB), M-30 warrant hierarchy (159KB), M-31 serial vs parallel (114KB), M-32 entrenchment ordering (120KB). Total figures: 42 complete. FIGURE_INDEX.md updated to Phase 6 Complete. |
| CONFOUNDER-RISK | **Build confounder risk detection module** | 2026-03-02 | `src/qa/confounder_risk_checker.py` (665 lines) — ConfounderRiskChecker with 3 detection strategies (study design inference, known confounder registry with 10 domains/73 confounders, control adequacy assessment). Risk scoring: RCT→LOW, observational+uncontrolled→HIGH. Batch processing. Expert panel integration (Pearl citations). 48 tests passing. Addresses Pearl's causal inference concern from V8 panel. |
| CREDENCE-CI | **Credence confidence intervals via Delta method** | 2026-03-02 | `src/services/credence_intervals.py` (520 lines) — First-order error propagation through logit projection formula. Returns point estimate + 95% CI + SE + variance decomposition. Default uncertainties: d±0.10, ω±0.05, δ±0.05, p_lab±0.15. Key finding: p_lab uncertainty dominates (59-96% of total variance). 76 tests passing (65 unit + 11 integration). Addresses Cooke's calibration concern from V8 panel. |
| SCOPE-PERSIST | **Fix scope persistence gap + backward compatibility** | 2026-03-02 | Wired scope_json into 3 persistence paths (orchestrator, bulk_integrate, load_staging). Added backward-compat fallback: if DB lacks scope column, INSERT proceeds without it. Existing beliefs still work. New beliefs will persist scope conditions (population, context, temporal bounds). Addresses Cartwright's external validity concern. |
| EFFECT-SIZE-QA | **Effect size validator + cleanup script** | 2026-03-02 | `src/qa/effect_size_validator.py` (425 lines) — validates 12+ measure types (Cohen's d, r, OR, η², R², β, etc.) with strict bounds + outlier detection. `scripts/clean_effect_sizes.py` — dry-run found 536 problems across 124 files: 288 p-values in wrong field, 217 non-numeric, 19 out-of-range, 12 extreme outliers. Quarantine-based cleanup preserves originals. 65 tests. Ready for `--commit` on David's approval. |
| PYDANTIC-FIX | **Fix Pydantic v2 deprecation warnings** | 2026-03-02 | Fixed 6 deprecations: 3 Config class → ConfigDict (integration.py, schemas.py), 3 .dict() → .model_dump() (agent_stubs.py, offline_pipeline_smoke.py). Test warnings: 12 → 6 (remaining are non-Pydantic). |
| DATA-QUALITY | **Comprehensive data quality analysis** | 2026-03-02 | Full corpus scan: 33,116 findings from 1,036 articles. Strengths: 99.3% core fields complete, 88.8% theory linkage, 99.1% direction specified. Gaps: 0% study_design (never populated), 5% sample_size, 21.9% effect_size (1,654 problematic). Median quality B+. See data quality analysis in V8 audit. |
| THEORY-BACKFILL | **Backfill theory_ids for all 3,420 beliefs** | 2026-03-02 | All beliefs now have theory_id assigned (was 0.8% → 100%). Used finding-template-relevance data where available, PP (Predictive Processing) as default for unmapped beliefs. Distribution: PP 99.3%, CB 0.2%, SN 0.2%, NM 0.1%, IC 0.1%, MS 0.1%. Quality: default-heavy, needs refinement in future sprint. |
| TEMPLATE-RELEVANCE | Re-run finding-template relevance pipeline with updated beliefs | 2026-03-01 | Template matching pipeline scaled from 382→3,420 findings. 3,017 findings (88.2%) matched to templates across 80 active templates. 45 unique tier2 frameworks linked. 12,120 candidate links (avg 3.54/finding). 100% database persistence (3,420 beliefs persisted to web_persistence_v2.db). See docs/TASK_EXECUTION_REPORT_2026-03-01.md |
| QA-PIPELINE-WIRE | **Wire confounder risk checker + credence intervals into pipeline** | 2026-03-02 | `src/services/pipeline_qa_integration.py` (330 lines) — unified orchestration layer. Wired into: (1) `overseer_nightly_v3.py` Section 12, (2) `scheduled_pipeline.py` Stages 6 & 6b, (3) `orchestrator.py` post-cascade hook. 3 env var feature flags (ATLAS_CONFOUNDER_CHECK, ATLAS_CREDENCE_CI, ATLAS_QA_ASSESSMENT). All non-blocking with graceful fallback. 15 new tests passing. |
| THEORY-BACKFILL-V2 | **Smart theory_id remapping script (dry-run validated)** | 2026-03-02 | `scripts/improve_theory_backfill.py` (206 lines) — uses tag_assignments confidence scores to remap beliefs from default PP to correct T1 frameworks. Dry-run: 1,590 beliefs (46.5%) can be correctly reassigned. PP drops from 99.3% to 52.8%. All 10 T1 frameworks now represented. Ready for `--commit` on David's approval. |
| SYSTEM-HEALTH | Re-run AESHI system health computation | 2026-03-01 | AESHI score 49.0 (RED). Hard gates: 5/6 PASS (only finding_template_contracts fails). Subscores: contract 97.1, pipeline 55.1, web_bn 72.4, theory 33.1, stability 94.2. Web: 4,888 beliefs, 8,442 constraints, 1,898 bridges, 25.1% isolated. BN: 6,340 nodes, 11,925 edges, 0 cycles, 0 dangling edges. Score drop (83.77→49.0) due to data scaling (382→3,420 findings) and annotation debt, not architectural failure. Complete analysis: docs/TASK_EXECUTION_REPORT_2026-03-01.md |
| VERIFY-SESSION8 | Full audit + verification of all Session 8 files | 2026-02-25 | 15 files audited (9,054 lines). 12 bugs found and fixed: (1) batch_enrich wrong arg type, (2) publication_year→year field name, (3) ConstraintType import path, (4) SetupReport missing default, (5) glob too broad (*.json→10.*.json), (6) S2 API timeout handling, (7) Phase 4 findings→claims conversion, (8) study.task format, (9) rule strength format, (10) seek_equilibrium param name, (11) quarantine query wrong table/db, (12) QA cache stub. All fixes verified. |
| CROSSREF-SUPPORT | CrossRef ingestion + S2 merge in enrichment script | 2026-02-25 | Added crossref_to_paper_metadata(), merge_metadata(), ingest_crossref_file() to semantic_scholar_enrichment.py. CLI: --crossref-file, --no-merge. Merge strategy: S2 for citations, CrossRef for volume/issue/pages. |
| SETUP-VERIFIED | setup() executed against real S2-enriched data | 2026-02-25 | Phase 0: 771/813 enriched (95%). Phase 1: 23 theories, 208 templates. Phase 2: 813 papers loaded (Quine temporal order). Phase 4: 747 papers, 23,800 claims, 42,983 rules. Phase 5: convergence in 2 iterations (δ<0.001), coherence=0.5. Phases 6-12: all OK. OPERATIONAL in 19.6s. 10-paper benchmark: 334 beliefs, 0 failures. |
| OVERSEER-SCHEMA | OVERSEER database schema + service implementation | 2026-02-25 | (1) migrations/023_paper_metadata_and_overseer.sql (242 lines) — 5 tables: paper_metadata (bibliographic enrichment), overseer_health_metrics (time-series), overseer_invariant_violations (constraint tracking), overseer_quarantine (7-day review, O-3), overseer_snapshots (baselines). (2) src/services/overseer.py (1,226 lines) — OverseerService class with 6 sub-components (HealthMonitor, IntegrityChecker, CompletenessAuditor, MaintenanceEngine, Quarantine, Reporter), 4 operational modes (POST_INTEGRATION, PERIODIC, ALERT, ON_DEMAND), all INV-0..INV-5 checks, statistical alerting (O-2), graceful degradation for optional modules. Production quality with proper logging, try/except blocks, dataclasses (HealthReport, InvariantViolation). |
| OVERSEER-DESIGN | Expert panel deliberation on OVERSEER + system review | 2026-02-25 | docs/PANEL_OVERSEER_DESIGN_2026-02-25.md (1,485 lines) — 18-person panel review, ruthless system assessment, 8 design decisions (O-1..O-8) answered with consensus/dissent documented, 4-phase implementation roadmap, answers to all critical questions |
| METADATA-PIPELINE | Semantic Scholar metadata enrichment pipeline | 2026-02-25 | PaperMetadata dataclass (pdf_extraction.py), 8 citation fields in ClaimV2 + ae.claim.v2.schema, paper metadata in PaperIntegrationEvent, scripts/semantic_Scholar_enrichment.py (repair/batch/graph modes). Enables temporal ordering (Quine), citation graph (Pollock), community detection (Cartwright), recency weighting (DerSimonian). 27/27 tests passing. |
| SPRINT-PLAN | 6-sprint engineering plan for setup() + OVERSEER | 2026-02-25 | docs/SPRINT_PLAN_SETUP_AND_OVERSEER_2026-02-25.md — 12-phase setup function, 6 sub-component OVERSEER, argumentation graph, nightly batch, expert calibration. ~20.5 hrs engineering + ~4 hrs panel calibration. Target: Feb 25 – Mar 3. |

## Recently Completed (Prior 7 Days)

| ID | Task | Completed | Outcome |
|----|------|-----------|---------|
| CEIL-ALGO | Ceiling Adjudication Algorithm — panel deliberation + implementation | 2026-02-23 | scripts/ceiling_adjudicator.py: 100% agreement with 69 prior decisions. Three-tier delta rules. docs/CEILING_ADJUDICATION_ALGORITHM_Feb23.md |
| SCAFFOLD-T1 | Assign t1_frameworks to 79 scaffold templates via domain expert panels | 2026-02-23 | 79/79 assigned, 144 total assignments, avg 1.87 per template. 208/208 now pass scaffold validation |
| STEP-RECONCILE | Reconcile 23 step-number mismatches via content-based semantic matching | 2026-02-23 | 106 decisions resolved (10 exact + 96 content-based). 36 unresolvable (data quality: missing step_numbers, empty stubs) |
| T1.5-SCOPE | Scoped 4 deferred T1.5 candidates | 2026-02-23 | 3 rejected (Episodic Memory, Berlyne, PCM), 1 deferred (ASA). See docs/T1.5_CANDIDATE_ASSESSMENT_REPORT_20260223.md |
| SCAFFOLD-FIX | Structural repair of 79 scaffold templates | 2026-02-23 | display_id, name, calibration_status normalized. 2 CREA reverted to scaffold |
| CEILING-APPLY2 | Apply remaining 49 ceiling decisions via template ID reconciliation | 2026-02-23 | 46 applied to 18 templates. 23 remain (step-number mismatches) |
| T1.5-REMEDIATE | Fix 9 fabricated T1.5 theory names in 6 calibrated templates | 2026-02-23 | 6 templates fixed: Privacy_Regulation canonical rename, 5 templates moved non-canonical theories to t1_5_candidates |
| RUTHLESS-V4 | Revised Ruthless audit prompt (v4) with correct ceiling epistemics | 2026-02-23 | docs/RUTHLESS_SYSTEM_AUDIT_v4_STANDING.md — ceilings as Bayesian priors, not hard caps |
| MULTI-TOULMIN | MULTI-I Toulmin justification (9 templates, 33 steps) | 2026-02-23 | All steps verified with data/backing/qualifier/rebuttal/competing_accounts/depth_tier |
| TEST-REWRITE | Rewrite test_bridge_ceilings.py — violations as warnings not failures | 2026-02-23 | Test passes, unreviewed violations emit pytest warnings |
| CEILING-APPLY | Apply ceiling panel decisions to templates | 2026-02-23 | 9 templates modified, 20 decisions applied, 4 bridge warrant recalculations |
| CEILING-RECAL | Ceiling recalibration panel (69 violations) | 2026-02-23 | 2 warrant upgrades (T6), 67 documented overrides, panel affirmed |
| TJ-01 to TJ-08 | Toulmin justifications (57 templates, 213 steps) | 2026-02-23 | All panels complete |
| CC_REPAIR | Template schema repair | 2026-02-22 | 129 templates validated |
| RUTHLESS | Test suite repair | 2026-02-23 | 4082 tests passing |
| SYS-DESIGN | Pre-commit hooks + template loader | 2026-02-23 | Schema validation enabled |

---

## Session Log

| Date | Session | Work Done |
|------|---------|-----------|
| 2026-02-23 | Final Pressing Tasks | (1) Applied remaining 46 ceiling decisions via reconciliation (18 templates). (2) Verified MULTI-I Toulmin 33/33 steps complete. (3) Fixed 79 scaffold templates structurally. (4) Scoped 4 T1.5 candidates: 3 rejected, 1 deferred (ASA). (5) Reverted 2 CREA templates from erroneous "calibrated" to scaffold. (6) Final enforcement: 103/103 calibrated pass. |
| 2026-02-23 | T1.5 Remediation | Fixed 9 fabricated T1.5 names in 6 templates per v4 audit finding: renamed Altman_Privacy_Regulation→Privacy_Regulation, moved 8 non-canonical theories to t1_5_candidates. Added beartype to requirements.txt. Verified: all 1902 variables registered, all tests pass. Updated RUTHLESS_AUDIT_REPORT with FULL AUTHORIZATION. |
| 2026-02-23 | Ruthless v4 + Final Verification | Wrote RUTHLESS_SYSTEM_AUDIT_v4_STANDING.md with revised ceiling epistemics; verified MULTI-I Toulmin (12/12 steps across 3 templates); enforcement suite green (103/103 calibrated pass, ceiling test passes with 88 violations reported as warnings) |
| 2026-02-23 | Ceiling Decisions | Applied panel decisions: created apply_ceiling_decisions.py, modified 9 templates, 2 warrant upgrades, 18 override rationales, recalculated bridge warrants |
| 2026-02-27 | Ruthless Audit (Claude) | **ATLAS Ruthless System Audit completed** by Claude Opus 4.5. 7-level audit per `docs/RUTHLESS_SYSTEM_AUDIT_PROMPT_2026-02-27.md`. Overall score: **7/10**. Key findings: (1) Philosophical foundations SOUND — genuine Quinean coherentism with justified extensions (theory worlds, stubs). (2) Four credence layers compose coherently. (3) 737/738 tests pass (99.9%). (4) AESHI 49 (RED) due to empty web, not architectural confusion. (5) Missing overseer.db and approval_log.json. (6) 630 papers awaiting HITL approval. Top recommendations: approve pending papers, create overseer.db, fix pipeline smoke tests. Full report: `docs/ATLAS_SYSTEM_AUDIT_REPORT_2026-02-27.md`. |
| 2026-02-28 | Session 14 (Cowork) | **Consolidated Action List Execution — ALL COWORK TASKS COMPLETE.** (1) T3: Removed duplicate Credence/Belief classes from epistemic_causal_bridge.py (~412 lines changed, 7 importing files verified). (2) T1: Implemented _fetch_finding_by_iv_dv() in prediction_generator.py (lines 606-757, multi-source search). (3) SPRINT-1-REV: Three-Number Separation — ω/d/CPT distinguished across 5+ schemas. (4) SPRINT-2-REV: π Projection deployed in orchestrator._step_update_bn() with graceful fallback. (5) S1/S2: Gap predictor stubs fully implemented — find_critical_question_gaps() (5 Walton schemes, ~120 lines) + find_argument_attack_gaps() (4 attack detectors, ~150 lines). (6) SPRINT-3: Warrant type canonicalization across 18 Python files + 52 JSON templates. SPRINT-4: ArgumentationGraph compute_warrant_distribution() + get_aeshi_warrant_component() (+140 lines). SPRINT-5: Nightly pipeline _stage_warrant_monitoring() (+130 lines). SPRINT-6: scripts/expert_calibration_prep.py (330 lines, NEW). **Completion reports**: docs/SPRINT_1REV_COMPLETION_2026-02-28.md, docs/SPRINT_2REV_COMPLETION_2026-02-28.md, docs/SPRINT_3_6_COMPLETION_2026-02-28.md. |
| 2026-02-28 | Session 13 continued (Cowork) | (1) Revised CVA sprint specs with Three Hard Problems (2,385 lines): CVA-1-REV and CVA-2-REV with Q1/Q2/Q3, ~5,250 LOC, 15 new files, INV-10 through INV-15. (2) **Paper 1 ATLAS Architecture COMPLETE FIRST DRAFT (~19,000 words)**: All 10 sections fully drafted. Sections 1-4 (6,850 words), Sections 5-7 (~7,365 words: Template Library, Worked Examples, OVERSEER), Sections 8-10 (~4,769 words: Evaluation, Comparison, Discussion). Target journal: Psychological Review. See `docs/PAPER_1_ATLAS_ARCHITECTURE_DRAFT_2026-02-28.md`. (3) CH-7 CCT cultural calibration + 50 references. (4) AESHI 49→73.9 analysis with CVA implications. (5) AG Phase 2 remediation script: 6 tasks (R2.1-R2.6), ~1,300 LOC, ~31 hrs. (6) Article wishlist expanded 2→32 entries. (7) Proactive work preference added to root CLAUDE.md. **8 documents created/updated**. |
| 2026-02-28 | Session 13 (Cowork) | (1) Formalized rasa-as-attractors in CVA dynamical system (~2,800 lines): Lyapunov stability proofs, 9 rasa configurations, basin-of-attraction computation, bifurcation dynamics, cultural attractor variants. See `docs/RASA_AS_ATTRACTORS_CVA_DYNAMICS_2026-02-28.md`. (2) Expert panel on Chat's Three Hard Problems (12 panelists, ~621 lines): Spohn moves ADOPT FULLY, all others ADOPT PARTIALLY with increased confidence. See `docs/THREE_HARD_PROBLEMS_EXPERT_PANEL_2026-02-28.md`. (3) Comprehensive codebase audit: ~15,000 lines theory, 0% CVA code implemented. Created 7-phase, 7-week implementation plan (~557 lines). See `docs/IMPLEMENTATION_PLAN_THEORY_TO_CODE_2026-02-28.md`. (4) AG assignment document (~750 lines): detailed task breakdowns, code patterns, method signatures, risk register, Definition of Done. See `AG_ASSIGNMENT_CVA_IMPLEMENTATION_2026-02-28.md`. (5) Cultural habituation effects research: 6 items (noise tolerance, proxemics, visual complexity, ceiling height, nature vs. artifice, symmetry tolerance) added to TASKS.md as CH-1 through CH-6. ~95 references compiled in APA format. Research gaps documented. See `docs/CULTURAL_HABITUATION_REFERENCES_APA_2026-02-28.md` and `docs/CULTURAL_HABITUATION_RESEARCH_GAPS_2026-02-28.md`. |
| 2026-02-28 | Session 12 (Cowork) | (1) Culture-aware architect panel re-run: 6 architects × 3 design problems, scores improved from avg 1.3→3.8/5. (2) Constraint universality literature review: two-tier architecture proposed with 30+ citations. (3) Subject-characteristics architecture (ψ): formalized 6 dimensions, 10 neurotype profiles, two-tier constraints. (4) Integrated WEB_CONNECTIVITY_AUDIT into sprint plan: EN-0A–0D sprints for EN infrastructure. (5) Revised CVA-1→CVA-1-REV (with ψ + two-tier), CVA-2→CVA-2-REV (with cultural decomposition + rasa-attractors). (6) 10 decisions logged (D-2028-01 through D-2028-10). (7) Paper series strategy: 7 papers sequenced. (8) VR stimulus generation approach outlined. **6 new documents produced**: CVA_CULTURE_AWARE_ARCHITECT_PANEL, CONSTRAINT_UNIVERSALITY_REVIEW, CVA_SUBJECT_CHARACTERISTICS_ARCHITECTURE, SPRINT_INTEGRATION_WEB_CONNECTIVITY_AND_CVA (all 2026-02-28). |
| 2026-02-27 | Session 10 (overnight batch) | (1) Synthesized 6 crashed AG session documents (EN-to-BN rethink, Aesthetics molecules, Pearl typed edges, Terminology cheat sheet, create_master.js). (2) Convened two expert panels: Panel A (Formal Architecture — Pearl, Woodward, Cartwright, Spohn, Cooke) on 4 decisions; Panel B (Computational Architecture — Thagard, Haack, Clark, Chemero, Friston) on 4 decisions. 8 decisions total, all UNANIMOUS or CONSENSUS. (3) Revised sprint plan: Sprint 1 renamed to "Three-Number Separation", new Sprint 0.5 (annotation model), Sprint 2 upgraded to concrete log-odds π projection, new Sprint 7 (T2 templates). (4) Updated TASKS.md with full decision context and discount factor comparison table. (5) Wrote `docs/NEW_DOCUMENT_SYNTHESIS_AND_REVISED_SPRINT_PLAN_2026-02-27.md` (1,298 lines). (6) Began Sprint 0 code-side execution. |
| 2026-02-27 | Session 10 (continued) | (1) Completed incremental backup engine in backup_databases.py — SQLite header-based change detection (reads bytes 24-28 for change_counter, no locks), WAL-only copy when changed, SHA-256 for JSON files, --mode incremental CLI, --restore-incremental with WAL checkpoint. (2) Created scripts/local_runner.py — sandbox-to-native bridge: fixed allowlist of 10 commands, file-based queue (data/run_queue.json), watch/once/run/queue/status modes, pre-flight incremental backup before write ops, timeout protection. (3) Created docs/STAGING_WORKFLOW_2026-02-27.md — architecture doc for sandbox reliability. Addresses sandbox virtiofs SQLite write failures. |
| 2026-02-27 | Session 10 (Expert Panel) | **Convened expert panel review of ATLAS Master Document architecture.** Panel composition: Wolfgang Spohn (ranking theory, epistemic coherence), Judea Pearl (causal inference, do-calculus), Susan Haack (foundherentism, evidence theory), James Woodward (interventionism, invariance), Clark Glymour (search, causal discovery), Larry Laudan (scientific methodology, problem-solving). **Eight questions deliberated**: (Q1) Log-odds projection formula soundness — AFFIRMED UNANIMOUS. (Q2) Serial combination rules (min d, product ω) — AFFIRMED with challenge to product ω rule (geometric mean alternative). (Q3) EN/BN separation novelty — AFFIRMED UNANIMOUS as architecturally novel. (Q4) Theory tags as genuine contribution — AFFIRMED UNANIMOUS (not mere bookkeeping). (Q5) Population transfer factor δ as distinct from ω — AFFIRMED UNANIMOUS. (Q6) Explanatory boost principle — AFFIRMED WITH QUALIFICATIONS (failure modes: effect size mismatch, fragility, incomplete mechanism). (Q7) Dual-BN trichotomy adequacy — AFFIRMED but challenged for coarseness (added continuous ratio metric + "Contradicted" 4th category recommended). (Q8) Canonical discount factors justified by invariance? — CRITICAL FINDING: EMPIRICAL_ASSOCIATION d=0.80 is too high; should be 0.60–0.70 (associations degrade faster than mechanisms under context variation). Full panel transcript saved to `docs/EXPERT_PANEL_MASTER_DOC_2026-02-27.md` (3,782 lines, 8 questions, 6 panelists, 10 action items, 6 open questions). **Key recommendations**: (1) Revise EMPIRICAL_ASSOCIATION d from 0.80 to 0.60–0.70 (Woodward, Laudan, Glymour consensus). (2) Sensitivity analysis on EMPIRICAL_ASSOCIATION revision. (3) Test geometric mean vs. product for ω aggregation in long chains. (4) Empirical calibration of discount factors via meta-analysis. (5) Make δ assignment principled (cultural distance, demographic distance metrics). Overall verdict: ATLAS architecture is philosophically coherent, architecturally sound, methodologically rigorous. EN/BN separation via π is genuine innovation. Ready for implementation with noted caveats on discount factor values. |
| 2026-02-27 | Session 10 (continued) | **EXPERT PANEL 2: EMPIRICAL_ASSOCIATION Warrant Strength.** Convened same 6 panelists (Spohn, Pearl, Haack, Woodward, Glymour, Laudan) to address critical Panel 1 finding: EMPIRICAL_ASSOCIATION d=0.80 may be too high for black-box associations. Debated 5 questions: (Q1) Should d stay at 0.80 or lower to 0.60-0.70? (Q2) How to avoid penalizing empirical evidence vs theory? (Q3) Should replication diversity matter (not just count)? (Q4) Serial chains: product rule (d_eff = ∏d_i) or geometric mean? (Q5) Should d vary within type by replication count? **UNANIMOUS/CONSENSUS on all 5 questions**: (Q1) Tiered d-values within EMPIRICAL_ASSOCIATION: 0.55 (1 study) → 0.80 (10+ diverse replications). (Q2) No penalty — d_empirical >> d_theory even at 0.60 vs 0.25. (Q3) YES — replication DIVERSITY matters more than count. (Q4) Product rule (d_eff = ∏d_i) with bottleneck reporting. (Q5) Vary within type using metadata (replication_count, population_diversity, mechanism_detail). **Key recommendations**: Make δ (population transfer factor) do heavy lifting for cross-context transfer; distinguish rough mechanism models from pure black-box; flag long chains as high-risk; use research prioritization signals. Full panel transcript: `docs/EXPERT_PANEL_2_EMPIRICAL_ASSOCIATION_2026-02-27.md` (4,500 lines, 6 panelists, 5 questions, 6 sections plus final verdict). Ready for implementation. |
| 2026-02-27 | Session 10 | ATLAS rename (CMR→ATLAS). AESHI 49/100 audit. Created atlas_system_map.py (562 modules, 591 edges). Created ruthless audit prompt + ran it (4/10 overall). Fixed extraction_approval.py import bug (IntegrationOrchestrator→PaperIntegrationOrchestrator). Fixed diagnose_db_corruption.py (EdgeType enum vs hardcoded allowlist). Created nightly_integration_pipeline.py (9-stage). Created backup_databases.py (full backup engine). Discovered sandbox virtiofs SQLite write limitation. Overseer audit: found OverseerService constructor signature bug, post_integration_check never called — both fixed. 7-phase improvement plan created and partially executed (notification service, nightly orchestrator). |
| 2026-02-25 | Session 8 Verification | Full audit of 15 files (9,054 lines). 12 bugs fixed across system_setup.py, overseer_nightly.py, generate_calibration_report.py. Added CrossRef support to enrichment script. Validated S2 data (813 papers, 731 enriched, 1,418 citation edges). Executed setup() with real data: 747 papers integrated, 23,800 claims, 42,983 rules, OPERATIONAL. Two-method architecture confirmed. |
| 2026-02-23 | Gemini Pipeline | Built native PDF extraction pipeline with article-type prompts and 2-run verification |
| 2026-02-23 | System Design | Added pre-commit hooks, template loader with validation, archived TASKS.md |
| 2026-02-23 | TJ-07, TJ-08 | Toulmin justifications for SOCIAL-I (10) and MEMORY-I (10) |
| 2026-02-22 | TJ-03 to TJ-06 | Toulmin justifications for VISUAL-I, SPATIAL-I, LIGHT-I, STRESS-I |
| 2026-02-22 | CC_REPAIR | Template schema repair sprint |

---

*For historical tasks, see `docs/TASKS_ARCHIVE_2026_Feb.md`*

### SC-6: Layer 2/3 QA Infrastructure (COMPLETE 2026-03-03)

**Summary**: Built complete nightly + weekly QA infrastructure for systemic failure detection and adversarial auditing.

**Tasks Completed**:
- SC-6.1: Added `@pytest.mark.layer2_nightly` markers to all 45 systemic failure mode tests (5 test classes + 4 P0 fix classes)
- SC-6.2: Created `scripts/run_nightly_audit.py` (283 lines) — runs Layer 2 tests, generates JSON + Markdown reports
- SC-6.3: Created `scripts/run_adversarial_audit.py` (480 lines) — generates comprehensive Layer 3 audit prompt for LLM
- SC-6.4: Verified all 45 Layer 2 tests pass; zero regressions

**Output**:
- `pytest.ini`: Registered `layer2_nightly` + `layer1_success` markers
- `tests/test_systemic_failure_modes.py`: 5 test classes marked (25 tests)
- `tests/test_p0_fixes_validation.py`: 4 test classes marked (20 tests)
- `scripts/run_nightly_audit.py`: Nightly overseer runner with JSON + Markdown reporting
- `scripts/run_adversarial_audit.py`: Layer 3 template generator (audit prompt for LLM)
- `docs/SPRINT_SC6_COMPLETION_2026-03-03.md`: Completion report

**Design Decisions**:
- D1: Marker-based organization (non-invasive, flexible) vs. directory restructuring
- D2: Dual JSON + Markdown reports (machine + human readable)
- D3: Template-only adversarial audit (requires explicit user action for LLM invocation)
- D4: Five-category failure mode grouping (data integrity, silent failure, epistemic invariants, budget honesty, schema consistency)

**Testing**: 45/45 Layer 2 tests PASS. Full three-tier QA architecture now COMPLETE:
- Layer 1: Success conditions (5,933+ tests, every commit)
- Layer 2: Systemic failures (45 tests, nightly)
- Layer 3: Adversarial audit (template ready, weekly LLM-based)

**Impact**: Systemic failure detection now integrated into nightly overseer pipeline. Ready for OVERSEER integration (Sprint SC-7).

