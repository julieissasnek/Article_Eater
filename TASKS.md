# TASKS.md

*Last updated: Wednesday, February 19, 2026 (Backlog tasks 1.1, 1.3, 1.4, D.11 completed)*

This file tracks all tasks for the Article_Eater_PostQuinean_v1 project.

---

## 🔧 SPRINT D: DATA REMEDIATION — 2026-02-18

| Task | Agent | Priority | Status | Notes |
|------|-------|----------|--------|-------|
| D.1 | CC | HIGH | ✅ COMPLETE | Vocabulary sheet consolidated from 3 sources |
| D.2 | CC/AG | HIGH | ✅ COMPLETE | Paper triage classifier |
| D.3 | Codex | HIGH | ✅ COMPLETE | Table reconstruction and classification |
| D.4 | AG | HIGH | ✅ COMPLETE | Full CSV garbage audit |
| D.5 | CC | HIGH | ✅ COMPLETE | Gold standard 15 papers |
| D.6 | CC | HIGH | ✅ COMPLETE | Claim extraction engine (48 tests passing) |
| D.7 | AG | HIGH | ✅ COMPLETE | Gold standard validation framework |
| D.8 | Codex | HIGH | ✅ COMPLETE | Effect size converter |
| D.9 | AG | HIGH | ✅ COMPLETE | Web of belief health report |
| D.10 | Codex | HIGH | ✅ COMPLETE | Batch extraction pipeline (72 claims from 116 papers) |
| D.11 | Codex | HIGH | ✅ COMPLETE | Rebuilt `web_persistence_v2.db` + post-rebuild health report |
| D.12 | CC | HIGH | ✅ COMPLETE | CMR pipeline integration (22 papers, 67 claims, 50 matched) |
| D.13 | Codex | HIGH | ✅ COMPLETE | Validation report generated (`docs/sprint_d_validation_report.md`, verdict: NEEDS WORK) |

**Sprint D Artifacts**:
- `data/vocabulary/variable_vocabulary.json` — Consolidated variable vocabulary (D.1)
- `src/extraction/vocabulary.py` — Vocabulary lookup functions (D.1)
- `data/production/paper_triage.json` — Paper classification (D.2)
- `src/extraction/paper_triage.py` — Paper triage classifier (D.2)
- `data/production/table_classifications.json` — Table classifications (D.3)
- `src/extraction/table_classifier.py` — Table reconstruction and classification (D.3)
- `src/extraction/effect_size_converter.py` — Effect size conversion utilities (D.8)
- `src/extraction/claim_extractor.py` — Claim extraction engine (D.6)
- `tests/test_claim_extractor.py` — 48 tests for claim extraction (D.6)
- `data/gold_standard/gold_standard_papers.json` — Gold standard papers (D.5)

**See**: `docs/SprintD_Data_Remediation.md` for full sprint details.

---

## 🚀 SPRINT 10: CMR PIPELINE FOUNDATION — 2026-02-17

| Task | Agent | Priority | Status | Notes |
|------|-------|----------|--------|-------|
| 1.2 | Claude Code | HIGH | ✅ COMPLETE | Template DB Index: TemplateRecord model, migration, scanner, 22 tests passing |
| 2.1 | Claude Code | HIGH | ✅ COMPLETE | Template Computation Functions Batch 1: 12 core templates (VF3, L1-3, CREA2, MAT1-2-4, SOC2, SC1-4, VIEW1), 55 tests passing |
| 3.2 | Claude Code | HIGH | ✅ COMPLETE | Template Computation Functions Batch 2: 20 additional templates (L4-5, MAT3-5, TP1-4, SOC1-3, CREA1-4, SC2-3, COL1-2, VF1-2, OLF1), 52 tests passing |
| 1.1 | Codex | HIGH | ✅ COMPLETE | `python3 scripts/check_enum_drift.py` reports 0 drift issues |
| 1.3 | Codex | HIGH | ✅ COMPLETE | Added `CMRStagingTheoryLink` + loader; loaded 1045 rows from template causal links |
| 1.4 | Codex | HIGH | ✅ COMPLETE | Added `to_wis()` conversion utility and test coverage |

**Sprint 10 Artifacts**:
- `src/cmr/models.py` — SQLAlchemy models (TemplateRecord, CMREvaluation, etc.)
- `src/cmr/template_scanner.py` — JSON template scanner and DB population
- `src/cmr/template_computations.py` — 32 template compute functions (Batch 1 + Batch 2)
- `migrations/007_create_templates_table.sql` — SQL migration
- `tests/test_template_record.py` — 22 tests for template loading
- `tests/test_template_computations.py` — 107 tests for compute functions
- `docs/DECISIONS.md` — Implementation decisions log

**Validation**:
- `python -m pytest tests/test_template_record.py -v` (22 passed)
- `python -m pytest tests/test_template_computations.py -v` (107 passed)
- `python -m pytest tests/ --tb=no -q` (3101 passed, 9 skipped)

---

## 🤖 GROUNDED EXPERT AGENT INTEGRATION — 2026-02-17

| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| GEA-1 | Retrieval and recursive explanation hardening | HIGH | ✅ COMPLETE | Alias-safe template resolution + `overall_maturity` confidence mapping in `src/services/grounded_expert_agent.py` |
| GEA-2 | WebOfBelief empirical evidence layer | HIGH | ✅ COMPLETE | SQLite empirical claim retrieval and grounded evidence synthesis added |
| GEA-3 | BN confidence calibration layer | HIGH | ✅ COMPLETE | BN posterior summaries added to expert responses (`bn_calibration`, confidence statement, formatted output) |

**Validation**: `./venv/bin/pytest -q tests/test_grounded_expert_agent.py` (4 passed)

---

## 🎯 SPRINT V15 CODEX VALIDATION — 2026-02-17

| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| V15-CX-1 | Update task board with Docs 64 and 65 | HIGH | ✅ COMPLETE | Task board now explicitly tracks Doc 64 (VF-II) and Doc 65 (CREA-III) integration and validation outcomes. |
| V15-CX-2 | Validate VF3 → CREA2B single-chain computation | HIGH | ✅ COMPLETE | Verified `data/templates/VF3.json` keeps single chain `VF3 -> Affect -> CREA2B -> Divergent Thinking` and no direct VF3→CREA2 interaction path that would double-count effects. |
| V15-CX-3 | Verify interaction matrix lookup/sub-additivity | HIGH | ✅ COMPLETE | Verified all 7 CREA2 matrix combinations and expected sub-additivity values (`A+B=0.84`, `A+C=0.76`, `B+C=0.80`, `A+B+C=0.70`; singletons `=1.0`). |
| V15-CX-STAB | Restore V14 gate compatibility after CREA-III additions | HIGH | ✅ COMPLETE | Backfilled missing V14 lifespan root fields for `CREA4`; `./bin/prod_smoke.sh` now exits cleanly. |

**Sprint Artifacts**:
- `docs/Sprint_Prompt_V15_Post_VF_II_CREA_III.md`
- `docs/64_Panel_VF_II_Visual_Form_Calibration_V1_0.md`
- `docs/65_Panel_CREA_III_Creative_Deepening_V1_0.md`

**Validation**:
- `node scripts/validate_v14_lifespan_fields.js`
- `node scripts/validate_v14_runtime_checks.js`
- `./bin/prod_smoke.sh`

---

## 🚨 HIGH PRIORITY AUDIT RUN — 2026-02-15

| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| RRA-S2 | Spec vs Reality gaps (Section 2 ruthless audit) | CRITICAL | ✅ COMPLETE | Reported in `docs/REPO_AUDIT_REPORT_2026-02-15.md` (Section 2 addendum) |
| RRA-S3 | Variable vocabulary audit (Section 3) | CRITICAL | ✅ COMPLETE | Cross-repo unified table: `docs/UNIFIED_VARIABLE_VOCAB_TABLE_CROSS_REPOS_2026-02-15.md` + `.csv` |
| RRA-S4 | Template completeness audit (Section 4) | CRITICAL | ✅ COMPLETE | Template 1-40 completeness matrix in `docs/REPO_AUDIT_REPORT_2026-02-15.md` |

---

## 📋 TEMPLATE ENCODING TASKS — 2026-02-16

### CC-11: Missing Music Templates (M8-M17)

| Status | Priority | Notes |
|--------|----------|-------|
| ✅ COMPLETE | MEDIUM | 9 templates from Panels 29 and 30 |

**Panel 29 (MII - Rhythm, Groove, Motor)**: M8, M9, M10, M11 (4 templates) ✅
**Panel 30 (MIII - Musical Emotion)**: M13, M14, M15, M16, M17 (5 templates) ✅
**Commit**: `f3faf4a` — [CC-11/CC-12] Add 25 templates

### CC-12: Missing Neuroscience Templates (Panels IV, V, EI)

| Status | Priority | Notes |
|--------|----------|-------|
| ✅ COMPLETE | MEDIUM | 11 templates from 02-15_ panels (Panel IV already existed) |

**Panel IV (Cognitive Control/Reward)**: Already existed ✅
**Panel V (Social Brain)**: T48, T49, T50, T51, T52 (5 templates) ✅
**Panel EI (Memory Encoding)**: ED1, ED2, ED3, ED4, ED5, ED6 (6 templates) ✅
**Commit**: `f3faf4a` — [CC-11/CC-12] Add 25 templates

### CC-14: New Panel Templates (Docs 44-47)

| Status | Priority | Notes |
|--------|----------|-------|
| ✅ COMPLETE | MEDIUM | All 4 panels encoded |

**Doc 44 (SOC-I Social Config)**: SOC1, SOC2, SOC3 (3 templates) ✅
**Doc 45 (COL-I Color)**: COL1, COL2 (2 templates) ✅
**Doc 46 (OLF-I Olfaction)**: OLF1 (1 template) ✅
**Doc 47 (VIEW-I Nature View)**: VIEW1 (1 template) ✅
**Commits**: `f3faf4a` (SOC, COL), `d624bba` (OLF1), `b2e2b0d` (VIEW1)

**Total templates: 129** (139 including framework + interaction reference fixes)

### CC-17: Template Query Service (Functional Integration)

| Status | Priority | Notes |
|--------|----------|-------|
| ✅ COMPLETE | HIGH | Prototype query service that answers design questions |

**Problem Identified**: Templates encode rich mechanistic knowledge but were disconnected from query system. Query engine worked with WebOfBelief (article extractions) but not templates.

**Solution**: Created `src/services/template_query_service.py` that:
- Searches templates by keyword relevance
- Extracts HOW (causal pathway), WHY (higher-order principle), WHEN (scope conditions), FOR WHOM (moderators)
- Synthesizes human-readable answers with confidence ratings
- Identifies research gaps from maturity ratings

**Example Query**: "When do high ceilings increase creativity and for whom?"
- Finds VF3 (Spatial Proportions and Cognitive Processing Mode)
- Returns mechanism: ceiling_height → enclosure_affect → cognitive_processing_style
- Returns scope: tasks with variable processing requirements, offices/schools/libraries
- Returns moderators: task type, cultural expectations, duration

**Architecture Note**: This is Layer 1 of a three-layer integration:
1. **Templates** (this service) — MECHANISTIC VOCABULARY, WHY it works
2. **Article Network** — EMPIRICAL EVIDENCE, specific effect sizes
3. **Bayesian Network** — CONFIDENCE CALIBRATION, posterior beliefs

Full integration would query all three layers and synthesize.

**Files Created**:
- `src/services/template_query_service.py`

### CC-16: Panel MAT-II Materials Calibration (Doc 51)

| Status | Priority | Notes |
|--------|----------|-------|
| ✅ COMPLETE | HIGH | Calibration parameters added to MAT1-MAT5 templates |

**Panel MAT-II is a "deepening" panel** — adds calibration parameters to existing MAT1-MAT5 templates, not new templates.

**Calibration Updates**:
- **MAT1** (CT-Affective Touch): CT-afferent dose-response boundaries (pleasurable 28-36°C, optimal velocity 1-10 cm/s), thermal effusivity classification, preattentive processing evidence
- **MAT2** (Thermal Adaptive PE): Goldilocks boundaries (neutral ±1°C, positive PE ±1-3°C, tolerance ±3-5°C, discomfort >±5°C), adaptive neutral formula T_n = 0.31×T_outdoor + 17.8°C, alliesthesia principle
- **MAT3** (Cross-Modal Congruence): 2×2×2 factorial experiment protocol, predicted effect sizes (d ≈ 0.4-1.2), prior-precision model (haptic > visual)
- **MAT4** (Natural Material Convergence): Channel weights (0.30/0.20/0.10/0.15/0.25 ±0.08-0.12), super-additivity 20-30%, time structure, preliminary stone/concrete/metal profiles
- **MAT5** (Cultural Conditioning): Multiplicative moderator model, cross-cultural prediction framework, olfactory cultural variation

**Files Modified**:
- `data/templates/MAT1_affective_touch_pathway.json`
- `data/templates/MAT2_thermal_adaptive_pe.json`
- `data/templates/MAT3_material_identity_integration.json`
- `data/templates/MAT4_natural_material_convergence.json`
- `data/templates/MAT5_material_cultural_conditioning.json`

### CC-15: Panel L-II Light Calibration (Doc 49)

| Status | Priority | Notes |
|--------|----------|-------|
| ✅ COMPLETE | HIGH | Calibration parameters added to L1-L5 templates |

**Panel L-II is a "deepening" panel** — adds calibration parameters to existing L1-L5 templates, not new templates.

**Calibration Updates**:
- **L1** (Luminance Contrast PE): CV-of-luminance Goldilocks boundaries (Rockcastle), photosensitivity correction (Wilkins ±30-50%)
- **L2** (Circadian Regulation): Age-correction function M-EDI(age) ≈ M-EDI(25) × (1 + 0.015 × (age − 25)), dose-response thresholds
- **L3** (Daylight Multi-Channel): Expert-estimated channel weights (~0.35/0.25/0.15/0.10/0.15), super-additivity 15-25%
- **L4** (CCT Temporal Ecological): Dual interpretation (ecological vs arousal) — Steidle-Veitch debate, maturity → "supported_with_acknowledged_dissent"
- **L5** (Dynamic Light): Maturity upgraded "preliminary" → "supported_preliminary", Chamilothori moving/static evidence

**Files Modified**:
- `data/templates/L1_luminance_contrast_pe.json`
- `data/templates/L2_circadian_architectural_regulation.json`
- `data/templates/L3_daylight_multichannel_convergence.json`
- `data/templates/L4_cct_temporal_ecological.json`
- `data/templates/L5_dynamic_light_temporal_pe.json`

### CC-13: Master Reference Inventory (Doc 43)

| Status | Priority | Notes |
|--------|----------|-------|
| ✅ COMPLETE | HIGH | 228 unique references extracted and deduplicated |

**Purpose**: Consolidated, deduplicated master list of all APA references from panel documents
**Output**: `docs/43_Master_Reference_Inventory.json`
**Script**: `scripts/extract_panel_references.py`
**Statistics**:
- 473 raw references extracted from 18 panel documents
- 228 unique references after deduplication (by first_author + year + title_keyword)
- 50 near-duplicates flagged for manual review
- 18 references cited across multiple panels
**Source Panels**: Docs 14, 18-23, 25, 27-30, 33, 34, 37-39, 42

---

## 🚨 CRITICAL: THEORY TIER ARCHITECTURE CORRECTION — 2026-02-14

**Document**: `docs/THEORY_TIER_ARCHITECTURE_V1.0_2026-02-14.md`
**Source**: Claude Desktop session 2026-02-13/14 — Framework Architecture & Affect Tiers Revision

### The Correction

ART, SRT, Biophilia were incorrectly placed at Tier 1. They are **phenomenological descriptions** of *what happens*, not mechanistic accounts of *why*. They belong at **Tier 2**.

### Correct Tier Structure

| Tier | Category | Theories |
|------|----------|----------|
| **1** | Framework Theories (neurally grounded) | Predictive Processing, Spatial Navigation/Cognitive Mapping, Dual-Process, DMN/TPN Dynamics, Neuromodulatory Systems, Interoception, Memory Systems, Embodied Cognition |
| **2** | Domain-Specific (demoted) | ART, SRT, Biophilia, Prospect-Refuge, Environmental Preference/Berlyne, Wayfinding/Lynch |
| **2b** | Methodological | Measurement theory, experimental design, statistics |
| **3** | Extracted Claims | Individual empirical findings |

### Sprint 7 — Theory Architecture

**⚠️ DEPENDENCIES**: Sprint 7 requires BOTH:
1. **Sprint 6 (node types, edge types)** — provides web infrastructure — ✅ COMPLETE
2. **CMR Specification (template library, prediction grammar)** — defines theory link structure — ⏳ PENDING

**DO NOT START T7.3/T7.4 until CMR spec is implementation-ready.**

| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| T7.1: Restructure theory_bootstrap.py with correct Tier 1/2 hierarchy | HIGH | ✅ COMPLETE | 8 Tier 1 frameworks added |
| T7.2: Create missing Tier 1 framework profiles (7 of 8 missing) | HIGH | ✅ COMPLETE | All 8 in `get_tier1_frameworks()` |
| T7.3: Extend ae.rule.v2 schema with `theory_links` field | HIGH | ⏳ BLOCKED | Awaiting CMR spec |
| T7.4: Update extraction prompts to capture Panel 6 theory links | HIGH | ⏳ BLOCKED | Awaiting CMR spec |
| T7.5: Create TheoryLevel enum: FRAMEWORK_THEORY, DOMAIN_THEORY, METHODOLOGICAL | MEDIUM | ✅ COMPLETE | In theory_models.py |
| T7.6: Implement theory agent profiles for all 8 Tier 1 frameworks | MEDIUM | PENDING | After T7.3/T7.4 |

### Completed Work (2026-02-14)

**Files Modified**:
- `src/models/theory_models.py`: Added `TheoryLevel.FRAMEWORK_THEORY`, `DOMAIN_THEORY`, `METHODOLOGICAL`
- `src/data/theory_bootstrap.py`:
  - Added 8 Tier 1 framework functions: `create_predictive_processing_framework()`, etc.
  - Updated ART/SRT/Biophilia/Fractal Fluency/Allostatic Load to `level=DOMAIN_THEORY` with `parent_theories` links
  - Added `get_tier1_frameworks()` and `get_tier2_domain_theories()` helper functions
  - Deprecated old `create_predictive_processing_theory()` (superseded by framework version)
- `src/epistemic/edge_types.py`: Added `SCHEMA_PENDING_CMR_SPEC` placeholder for finding–mechanism links

### What Remains (CMR-Dependent)

The `finding_mechanism_links` schema will specify how Tier 3 findings connect to Tier 1 mechanisms:
- **Template library**: Canonical compositional reasoning patterns
- **Prediction grammar**: How to compose mechanism claims into testable predictions
- **Link structure**: What fields each finding–mechanism link requires

**Placeholder location**: `src/epistemic/edge_types.py` (end of file, marked `SCHEMA_PENDING_CMR_SPEC`)

---

## 🔧 PIPELINE RELIABILITY AUDIT — 2026-02-15

### What EXISTS and WORKS

| Stage | Component | Status | Location |
|-------|-----------|--------|----------|
| 1. Article Finding | Zotero integration | ✅ WORKING | User manages via Zotero + university library |
| 2. BibTeX Import | Streamlit wizard | ✅ WORKING | `streamlit_app/pages/1_bibtex_import.py` |
| 3. PDF Discovery | Auto-scan ~/Zotero/storage | ✅ WORKING | `discover_pdfs()` in bibtex_import.py |
| 4. PDF Text Extraction | pdfminer.six | ✅ WORKING | `app/pdf_ingest.py` |
| 5. Table Extraction | AI + pdfplumber hybrid | ✅ WORKING | `src/services/table_extractor.py` |
| 6. Rule Extraction | ae.rule.v2 generation | ✅ WORKING | 133 cached, rules flowing |
| 7. Web of Belief | ClaimV2, 12 NodeTypes | ✅ WORKING | `src/services/web_of_belief.py` |
| 8. Query/Reasoning | Natural language queries | ✅ WORKING | `src/services/query_engine.py` |

**Production Data**:
- 133 PDFs preprocessed (`data/production/pdf_preprocess_cache/`)
- 49 Zotero-sourced papers
- Rules generated in `data/production/realtime_rules.jsonl`

### GUIs Available

| App | Purpose | Launch |
|-----|---------|--------|
| Streamlit | BibTeX import, query, explore, export | `streamlit run streamlit_app/app.py` |
| Flask | API routes, annotator | `python -m app.main` |
| Frontend | Article annotator | `frontend/article-annotator.html` |

### Quality/Reliability Concerns

| Issue | Severity | Notes |
|-------|----------|-------|
| Many `env.unresolved.*` variables | MEDIUM | LLM extraction producing unmapped variables |
| `provenance_tier: abstract_provisional` | LOW | Expected — requires PDF confirmation |
| Mock API clients in paper_fetcher.py | LOW | Only for direct API fetch; Zotero handles acquisition |
| BN inference missing pgmpy | MEDIUM | Variables defined but no actual causal queries |

### Sprint 8 — Pipeline Reliability Hardening

| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| P8.1: Audit variable mapping coverage | HIGH | ✅ COMPLETE | Report: `docs/P8_1_VARIABLE_MAPPING_AUDIT_2026-02-17.md` (12,596-row audit; unresolved env 27.6%, unresolved out 15.7%; table→rule alignment 100%) |
| P8.2: Create canonical env/out variable registry | HIGH | ✅ COMPLETE | Added `scripts/build_canonical_env_out_registry.py` + `contracts/vocab/canonical_env_out_registry.json`; report: `docs/P8_2_CANONICAL_ENV_OUT_REGISTRY_2026-02-17.md` |
| P8.3: Add LLM fallback for unmapped variables | MEDIUM | ✅ COMPLETE | Implemented in `scripts/run_realtime_table_rule_intake.py` and `scripts/process_realtime_pdf_completion_queue.py` with constrained shortlist policy; report: `docs/P8_3_LLM_FALLBACK_RESOLUTION_2026-02-17.md` |
| P8.4: Wire pgmpy for BN inference | MEDIUM | ✅ COMPLETE | Added optional pgmpy inference wiring in `src/services/incremental_bn.py` (posterior query, d-separation, Markov blanket) with graceful fallback; report: `docs/P8_4_PGMPY_BN_INFERENCE_WIRING_2026-02-17.md` |
| P8.5: Test Zotero→BibTeX→extraction E2E flow | HIGH | ✅ COMPLETE | Added integration test `tests/test_bibtex_e2e_flow.py` and verified full BibTeX ingest stack (`57 passed` across BibTeX test suite); report: `docs/P8_5_ZOTERO_BIBTEX_EXTRACTION_E2E_2026-02-17.md` |
| P8.6: Add extraction quality metrics | MEDIUM | ✅ COMPLETE | Added fallback/match-type metrics + JSON report output in `scripts/check_table_extraction_quality.py`; per-paper audit enrichment in `scripts/process_realtime_pdf_completion_queue.py`; follow-up fix `docs/P8_6_QUALITY_GATE_FIX_2026-02-17.md`; quality gate now PASS |

### Sprint 9 — Unified Research Queue & Tight Integration

**Contracts Created**: 2026-02-15
- `contracts/research_queue.contract.md` — Research Queue Service specification
- `contracts/voi_collector.contract.md` — VOI Collector interface for humans/bots

**Goal**: Unify gap prediction, VOI scoring, theory-driven priorities, and discovery funnel
into a single actionable "What should I be looking for?" queue.

**Existing Infrastructure to Integrate**:
- `src/services/gap_predictor.py` — 7 gap types from argument structure
- `src/services/voi_search.py` — cross-field vocabulary, search strategies
- `src/services/discovery_funnel.py` — gap → search → PDF → closure tracking
- `src/services/epistemic_orchestrator.py` — P2-P6 service coordination

| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| I9.1: Implement ResearchQueueService | HIGH | ✅ COMPLETE | Implemented in `src/queue/service.py` + `src/queue/models.py`; queue persistence + assignment/reporting flow |
| I9.2: Add theory-driven gap detection | HIGH | ✅ COMPLETE | Tier 1 prediction gap generation + framework coverage metric in queue state |
| I9.3: Connect queue to Zotero watcher | MEDIUM | ✅ COMPLETE | BibTeX delta watcher in `src/queue/zotero_watcher.py`; passive match+auto-report via `sync_zotero_to_queue()` |
| I9.4: Create VOI collector registration | MEDIUM | ✅ COMPLETE | Collector profile registration + `claim_target` + search guidance implemented in `src/queue/service.py` / `src/queue/models.py` |
| I9.5: Add research opportunity registry | MEDIUM | ✅ COMPLETE | Added `ResearchOpportunity` model + registry lifecycle methods and persistence in `src/queue/service.py` |
| I9.6: Build Streamlit queue dashboard | LOW | ✅ COMPLETE | Added `streamlit_app/pages/6_research_queue.py` with queue metrics, assignment/actions, opportunity updates, and automation controls |
| I9.7: Implement automated searcher bot | LOW | ✅ COMPLETE | Added `src/queue/automated_searcher.py` + `run_automated_searcher()` for Semantic Scholar-backed bulk screening and queue reporting |

**Theory-Driven Gap Detection** (I9.2):
```
For each Tier 1 framework:
  For each prediction (explicit + derived):
    Check if empirical support exists in web
    If not: Generate ResearchTarget with:
      - mechanism_predictions from framework
      - suggested_queries from cross-field vocabulary
      - is_research_opportunity = false (initially)
    After search: If no articles → mark as research opportunity
```

**Expert Panel Guidance** (already embedded in existing services):
- Simon: Satisficing, bounded rationality
- Pearl: Causal attribution of search success/failure
- Haack: Foundherentism, where grounding is weak
- Thagard: Coherence-based prioritization
- Bates: Berrypicking search behavior

**NEW Panel Consultation**: `docs/PANEL_QUEUE_PRIORITIZATION_2026-02-15.md`
- Added: Marr (computational/algorithmic/implementation levels)
- Added: Friston (prediction error as priority signal)
- Unified priority formula combining 6 components
- Satisficing rules for when to stop searching
- Theory-driven queue refresh algorithm

---

## 🤖 CC Tasks — Autonomous AI Worker (Claude Code)

**Created**: 2026-02-16
**Source**: Doc 35/36 parallel AI coordination system

### CC-1: Template Data Structure Encoding

| Target | Current | Status | Notes |
|--------|---------|--------|-------|
| 63 templates | 77 templates | ✅ 100% COMPLETE | `data/templates/*.json` + L1-L5 + MAT1-MAT5 + SC1-SC4 |

**Completed**: 2026-02-16
- Registry functional at `src/theory/templateRegistry.ts`
- Templates cover all 10 Tier 1 frameworks + auxiliary mechanisms
- Templates indexed: T1-T30, M1-M12, AX1-AX12, SN1-2, PP4, IC2, NM2-3, DT1, CB2, EC2, MS2, DP2, MSI2, SRT1

### CX-5: Light & Luminance Templates (from Panel 34)

| Status | Notes |
|--------|-------|
| ✅ COMPLETE | 5 new templates encoded from `docs/panels/34_Panel_LI_Light_Luminance.md` |

**Completed**: 2026-02-16
**Panel Document**: Doc 34 — Panel L-I: Light & Luminance in Architectural Experience
**Templates Created**:
| ID | Display | Name | Maturity |
|----|---------|------|----------|
| `LUM_CONTRAST_PE_001` | L1 | Luminance Contrast PE | supported |
| `CIRCADIAN_ARCH_REG_001` | L2 | Circadian Architectural Regulation | established |
| `DAYLIGHT_MULTICHANNEL_001` | L3 | Daylight Multi-Channel Convergence | supported |
| `CCT_TEMPORAL_ECOLOGICAL_001` | L4 | CCT as Temporal-Ecological Signal | supported (with dissent) |
| `DYNAMIC_LIGHT_TEMPORAL_001` | L5 | Dynamic Light Temporal PE | preliminary |

**Coverage Impact**: A4 (Light & Luminance) upgraded from ★ Minimal → ★★★ Moderate

### CC-7: Materials Templates (from Panel 37)

| Status | Notes |
|--------|-------|
| ✅ COMPLETE | 5 new templates encoded from `docs/panels/37_Panel_MAT_I_Materials.md` |

**Completed**: 2026-02-16
**Panel Document**: Doc 37 — Panel MAT-I: Materials, Surfaces, & Haptic Properties
**Templates Created**:
| ID | Display | Name | Maturity |
|----|---------|------|----------|
| `CT_AFFECTIVE_TOUCH_001` | MAT1 | C-Tactile Affective Touch Pathway | supported |
| `THERMAL_ADAPTIVE_PE_001` | MAT2 | Thermal Comfort as Adaptive PE | supported |
| `MATERIAL_IDENTITY_INTEGRATION_001` | MAT3 | Multi-Modal Material Identity Integration | supported |
| `NATURAL_MATERIAL_CONVERGENCE_001` | MAT4 | Natural Material Convergence (Wood Template) | supported |
| `MATERIAL_CULTURAL_CONDITIONING_001` | MAT5 | Material-Cultural Conditioning | preliminary |

**Coverage Impact**: A1 (Materials & Surfaces) significantly strengthened

### CC-8: Spatial Configuration Templates (from Panel 38)

| Status | Notes |
|--------|-------|
| ✅ COMPLETE | 4 new templates encoded from `docs/38_Panel_SC_I_Spatial_Config.md` |

**Completed**: 2026-02-16
**Panel Document**: Doc 38 — Panel SC-I: Spatial Configuration
**Templates Created**:
| ID | Display | Name | Maturity |
|----|---------|------|----------|
| `SPATIAL_INTEGRATION_NAV_PE_001` | SC1 | Spatial Integration & Navigational PE | supported |
| `ISOVIST_VISUAL_PREDICTION_001` | SC2 | Isovist Dynamics & Visual Prediction | supported |
| `ARCH_PROMENADE_PE_ORCHESTRATION_001` | SC3 | Architectural Promenade | supported |
| `SPATIAL_SOCIAL_ENCOUNTER_001` | SC4 | Spatial Configuration & Social Encounter | supported |

**Coverage Impact**: A3 (Spatial Configuration) upgraded from ★★ Partial → ★★★★ Strong
**Template Count**: 73 → 77 total templates

### CC-9: Visual Form Templates (from Panel 39 — PREVIOUSLY OVERLOOKED)

| Status | Notes |
|--------|-------|
| ✅ COMPLETE | 3 new templates encoded from `docs/39_Panel_VF_I_Visual_Form.md` |

**Completed**: 2026-02-16
**Panel Document**: Doc 39 — Panel VF-I: Visual Form, Contour, and Architectural Pattern
**NOTE**: This panel was OVERLOOKED in previous encoding passes despite being ready.
**Templates Created**:
| ID | Display | Name | Maturity |
|----|---------|------|----------|
| `CONTOUR_PE_CURVATURE_001` | VF1 | Contour PE — Curvature and Angularity | supported |
| `VISUAL_RHYTHM_SCALING_001` | VF2 | Visual Rhythm and Scaling Hierarchy | preliminary |
| `SPATIAL_PROPORTIONS_PROCESSING_001` | VF3 | Spatial Proportions and Cognitive Processing Mode | supported |

**Coverage Impact**: A6 (Visual Pattern & Form) upgraded from ★★★ Moderate → ★★★★ Strong
**Template Count**: 77 → 80 total templates

### CC-10: Temporal Dynamics Templates (from Panel 42)

| Status | Notes |
|--------|-------|
| ✅ COMPLETE | 4 new templates encoded from `docs/42_Panel_TP_I_Temporal.md` |

**Completed**: 2026-02-16
**Panel Document**: Doc 42 — Panel TP-I: Temporal Dynamics, Movement, and Architectural Time
**Templates Created**:
| ID | Display | Name | Maturity |
|----|---------|------|----------|
| `MOTOR_PREDICTION_ARCH_001` | TP1 | Motor Prediction and Proprioceptive PE | supported |
| `THRESHOLD_EPISODIC_BOUNDARY_001` | TP2 | Threshold as Episodic Boundary (Doorway Effect) | supported |
| `MATERIAL_AGING_TEMPORAL_DEPTH_001` | TP3 | Material Aging and Temporal Depth | preliminary |
| `TEMPORAL_HIERARCHY_ARCH_PE_001` | TP4 | Temporal Hierarchy of Architectural PE | preliminary |

**Coverage Impact**: A10 (Temporal Experience & Movement) upgraded from ★★ Partial → ★★★★ Strong
**Template Count**: 80 → 84 total templates

### CC-2: ReductionClaim Encoding

| Target | Current | Status |
|--------|---------|--------|
| 10 reduction claims | 12 claims | ✅ COMPLETE (Codex) |

**Completed**: Codex encoded 4 ART, 4 SRT, 4 Biophilia reduction claims.

### CC-3: Cross-Reference Index Encoding

| Status | Notes |
|--------|-------|
| ✅ COMPLETE (Codex) | 5 attribute domains encoded: Spatial, Visual, Sensory, Content, Affordance |

### CC-4: Epistemic Core Bridge

| Status | Notes |
|--------|-------|
| ✅ COMPLETE (Codex) | `createClaimFromTemplate`, `createEdgesFromReduction` implemented |

### CC-5: PDF & Abstract Table Audit

| Status | Notes |
|--------|-------|
| ✅ COMPLETE | Findings in `signals/CC5_COMPLETE.json` |
| | Critical gap: `architectural_variable` field missing from extraction |
| | Resolution: CX-4 interface uses optional fields |

### Sprint 1.5 Phase C: External Repo Drift

**Status**: DOCUMENTED — Requires fixes in external repos

| Repo | File | Enum | Issue |
|------|------|------|-------|
| Article_Finder | `search/gap_analyzer.py` | GapType | Unknown values: `coverage`, `neural`, `theory` |
| BN_graphical | `src/article_processing/article_decomposer.py` | ClaimType | Deprecated aliases: boundary→moderated, effect→causal, etc. |
| BN_graphical | `src/literature_integration/literature_linker.py` | EvidenceType | Unknown values: `direct`, `indirect`, `meta`, `review` |
| BN_graphical | `src/schemas/enhanced_edge.py` | EvidenceType | Deprecated alias: empirical→observational |
| BN_graphical | `contracts/bn.api.v2.schema.json` | CI Shape | Deprecated alias: array→object shape |
| Outcome_Contractor | `contracts/article_extraction_contracts.py` | ArticleType | Deprecated aliases for study types |
| Outcome_Contractor | `article_finder/article_type_classifier.py` | ArticleType | Deprecated aliases for study types |

**Fix Pattern**: Update enums to use canonical values from `contracts/vocab/canonical_enums.json`

**Phase A+B**: ✅ COMPLETE — AE-internal drift fixed (2026-02-16)

---

### Streamlit Pages (6 total)

1. `0_corpus_stats.py` — Corpus statistics
2. `1_bibtex_import.py` — BibTeX import wizard (Zotero integration)
3. `1_query.py` — Natural language query interface
4. `2_explore.py` — Web of belief exploration
5. `3_communities.py` — Community detection
6. `4_export.py` — Export functionality
7. `5_admin.py` — Admin panel

---

## ⭐ SPRINT 6 PIPELINE STATUS — Verified 2026-02-14

**Critical Bridge Created**: `src/epistemic/extraction/rule_to_claim_mapper.py`

Maps ae.rule.v2 (PDF extractions) → Sprint 6 ClaimV2/NodeType:
- "edge", "association" → EMPIRICAL_FINDING
- "presumption" → THEORETICAL_PROPOSITION
- "constraint" → CONCEPTUAL_CONSTRAINT
- "rebuttal" → METHODOLOGICAL_CRITIQUE

**Real Data Verification**:
| Metric | Count |
|--------|-------|
| Source rules (ae.rule.v2) | 31 |
| ClaimV2 nodes created | 31 |
| EdgeV2 edges created | 22 |
| Papers represented | 9 |

**⚠️ Tier Structure NEEDS UPDATE** (see correction above):
- Tier 1: **6 theories in bootstrap, but 7 of 8 Tier 1 frameworks MISSING**
- Tier 2: 12 NodeTypes, 19 EdgeTypes, monitoring infrastructure
- Tier 3: 31 extracted claims flowing through Sprint 6
- **MISSING**: Theory-to-finding links not captured in extraction!

**Test**: `pytest tests/test_rule_to_claim_mapper.py` (23/23 pass)

--- Completed tasks are kept as project history. **Panels are first-class objects** integrated into the sprint cycle.

---

## ⭐ CODEX TASK LIST (TOP PRIORITY) — Added 2026-02-12

**Task List ID**: `CODEX-TASKS-2026-02-12`
**Location**: `docs/CODEX_TASK_LIST_2026-02-12.md`
**Restart Handoff**: `docs/CODEX_CONTINUATION_HANDOFF_2026-02-12.md` (read first when resuming after context compaction/restart)

| Task | Description | Status |
|------|-------------|--------|
| TASK-0 | Ruthless System Evaluation | COMPLETE (2026-02-12) |
| TASK-1 | Fix Critical Issues | COMPLETE (2026-02-12, code-level) |
| TASK-2 | Fix Major Issues | COMPLETE (2026-02-17, closure pass + compatibility hardening; full pytest: 2935 passed, 9 skipped) |
| TASK-3 | Integration Test Suite | COMPLETE (2026-02-12) |
| TASK-4 | Documentation Audit | COMPLETE (2026-02-12) |
| TASK-5 | Performance Profiling | COMPLETE (2026-02-12) |
| TASK-6 | Security Hardening | COMPLETE (2026-02-12) |

**Start Command**: Point Codex to `docs/CODEX_TASK_LIST_2026-02-12.md` and tell it to begin.

---

## ⭐ CHATGPT TASK LIST — Added 2026-02-12

**Task List ID**: `CHAT-TASKS-2026-02-12`
**Location**: `docs/CHAT_TASK_LIST_2026-02-12.md`

Long-running evidence processing tasks for ChatGPT:
- T1: Abstract Processing (42h)
- T2: Table Extraction (17h)
- T3: Citation Pruning (33h)
- T4: Canonical ID Mapping (17h)
- T5: Belief Generation (25h)
- T6: Scope Extraction (17h)
- T7: Theory Linkage (15h)
- T8: Conflict Detection (7h)

**Execution Order**: T3 → T1 → T4 → T5 → T6 → T2 → T7 → T8

---

## Task Coordination (MANDATORY)

**Before starting ANY task, check `ACTIVE_TASKS.md`** to see what's claimed.

```
1. Read ACTIVE_TASKS.md
2. Claim your task (add row to Active Claims)
3. Start work
4. Update ACTIVE_TASKS.md when done
5. Update this file (TASKS.md) with completion status
```

This prevents duplicate work across parallel terminals.

---

## Current Priority Order

### ✓ MVP INTEGRATION — COMPLETE (2026-02-11)

**Goal**: Working demo that answers "What affects attention in offices?" with confidence and sources.

| Lane | Description | Status | Panel |
|------|-------------|--------|-------|
| MVP-0 | Contracts & Schemas | ✓ COMPLETE | PANEL_MVP0_CONTRACTS |
| MVP-1 | Persistent Web State | ✓ COMPLETE | PANEL_MVP1_DECISIONS |
| MVP-2 | Batch Processing Script | ✓ COMPLETE | PANEL_MVP2_DECISIONS |
| MVP-3 | Query Engine + CLI | ✓ COMPLETE | PANEL_MVP3_QUERY_ENGINE |
| MVP-GUI | Streamlit UI | ✓ COMPLETE | PANEL_MVP_GUI_DECISIONS |
| MVP-5 | Demo & Docs | ✓ COMPLETE | (documentation only) |

---

### ⭐ INTEGRATION SPRINTS (TOP PRIORITY) — Added 2026-02-11

**Goal**: Full 12-layer integration between Epistemic Web and Bayesian Network.

**Architecture Doc**: `docs/INTEGRATION_ARCHITECTURE_WEB_BN_2026-02-11.md`
**Implementation Plan**: `docs/IMPLEMENTATION_PLAN_INTEGRATION_2026-02-11.md`
**Decisions Log**: `docs/DECISIONS_INTEGRATION_SPRINTS_2026-02-11.md`

**Sprint Schedule:**

| Sprint | Description | Depends On | Status |
|--------|-------------|------------|--------|
| INT-1 | Edge Justification Foundation | - | ✓ COMPLETE |
| INT-2 | Gap Prediction Engine | INT-1 | ✓ COMPLETE |
| INT-3 | BN Frontend — Evidence Panel | INT-1 | ✓ COMPLETE |
| INT-4 | Epistemic Web Component | INT-1 | ✓ COMPLETE |
| INT-5 | Cross-Layer Query API | INT-1 | ✓ COMPLETE |
| INT-6 | User Modes & Testing | INT-2,3,4,5 | ✓ COMPLETE |

**Sprint Details:**

#### INT-1: Edge Justification Foundation ✓ COMPLETE (2026-02-11)
- [x] Create `integration.edge_justification.v1.schema.json`
- [x] Implement `EdgeJustificationService` (`src/services/edge_justification.py`)
- [x] Add `/api/v1/integration/edge/{id}/justification` endpoint
- [x] Write tests (`tests/test_edge_justification.py`)

#### INT-2: Gap Prediction Engine ✓ COMPLETE (2026-02-11)
- [x] Implement `GapPredictor` class (`src/services/gap_predictor.py`)
- [x] Mediation, mechanism, boundary, direction gap detection
- [x] VOI calculation for prioritization
- [x] Write tests (`tests/test_gap_predictor.py`)

#### INT-3: BN Frontend — Evidence Panel ✓ COMPLETE (2026-02-11, BN_graphical repo)
- [x] Modify `CausalGraphView.tsx` — edge opacity from credence
- [x] Create `EvidencePanel.tsx` with justification details
- [x] Add edge click interaction
- [x] Color edges by justification status (strong/moderate/weak/unjustified/contested)

#### INT-4: Epistemic Web Component ✓ COMPLETE (2026-02-11, BN_graphical repo)
- [x] Create `WebView.tsx` with React Flow
- [x] Node colors by epistemic level (theoretical/intermediate/empirical/observational)
- [x] Edge colors by constraint type (supports/explains/contradicts/instantiates)
- [x] Filter controls by level
- [x] Add `/api/v1/integration/web/state` endpoint

#### INT-5: Cross-Layer Query API ✓ COMPLETE (2026-02-11)
- [x] Implement `CrossLayerQueryService` (`src/services/cross_layer_query.py`)
- [x] Theory support queries, empirical grounding, environment-outcome lookup
- [x] Cross-layer conflict detection, belief chains
- [x] Layer statistics endpoint
- [x] Write tests (`tests/test_cross_layer_query.py` — 16 tests passing)

#### INT-6: User Modes & Integration Testing ✓ COMPLETE (2026-02-11)
- [x] Mode switcher UI (Knowledge/Prediction/Expert)
  - Created `ModeContext.tsx` with feature matrix per mode
  - Created `ModeSwitcher.tsx` component with full and compact variants
  - Updated `ExplorerPage.tsx` for mode-aware rendering
- [x] Panel review for all INT sprints (see `docs/DECISIONS_INT_3_6_PANEL_REVIEW_2026-02-11.md`)
  - 14 decisions reviewed by Pearl, Simon, Shneiderman, Cartwright, Haack
  - 8 approved, 4 approved with enhancements, 2 require revision
- [ ] End-to-end integration tests (deferred to follow-up sprint)
- [ ] Documentation updates (deferred to follow-up sprint)

**Parallelization Note**: After INT-1 completes, INT-2/3/4/5 can run in parallel.

**See**: `docs/PARALLEL_WORK.md` for file ownership.
**See**: `docs/SYSTEM_INVENTORY_2026-02-11.md` for full repo documentation.

---

### ⭐ Panel Review Fixes (2026-02-12) — Claude Code Session

**Context**: Ruthless panel review (`docs/PANEL_RUTHLESS_REVIEW_2026-02-12.md`) identified critical issues.
**Overall Score**: 4/10 - "Ambitious but confused"

| Fix | Description | Status | Panel Reference |
|-----|-------------|--------|-----------------|
| FIX-1 | Widen credence intervals (floor 0.05→0.25) | ✓ COMPLETE | Kahneman: overconfidence |
| FIX-2 | Remove crypto-foundationalist level weights | ✓ COMPLETE | Haack: 1.5/0.8 smuggles foundationalism |
| FIX-3 | Add defeater search to gap predictor | ✓ COMPLETE | Mayo: confirmation bias is structural |

**Changes Made (2026-02-12)**:
1. `src/services/web_of_belief.py`:
   - Raised uncertainty floor from 0.05 to 0.25 (lines 430-431)
   - Changed `is_well_established()` threshold from 0.2 to 0.35
   - Changed default uncertainty from 0.4 to 0.5 in Belief class
2. `src/services/gap_predictor.py`:
   - Changed LEVEL_WEIGHTS to all 1.0 (lines 346-351) - removes crypto-foundationalism
   - Added `find_defeaters_for_belief()` method (~150 lines)
   - Added `find_all_defeaters()` method for batch defeater search
   - Added DEFEATER_INDICATORS dictionary for defeater language detection
3. `app/routes/integration.py`:
   - Added `/api/v1/integration/defeaters/belief/{belief_id}` endpoint
   - Added `/api/v1/integration/defeaters/top` endpoint

**Tests**: All 2518 tests passing after changes.

---

### ⭐ Panel Review — Larger Architectural Changes (2026-02-12)

These require significant design decisions and implementation effort.

#### ARCH-1: Causal Inference — Do-Calculus Decision ⚠️ NEEDS DECISION

**Panel Critique (Pearl)**: "No do-operator implementation. Your 'epistemic_causal_bridge.py' claims to bridge Quinean to Pearlian, but I see no actual do-calculus. Where is do(X=x)? Where are the truncated factorizations? You have causal VOCABULARY without causal SEMANTICS... This is 'causal inference theater.'"

**The Question**: Should we implement real do-calculus?

| Option | Description | Effort | Trade-off |
|--------|-------------|--------|-----------|
| A. Implement do-calculus | Full Pearl machinery: do-operator, truncated factorizations, identification algorithms | HIGH (~2-3 sprints) | Rigorous but complex; requires structural equations for every relationship |
| B. Remove causal claims | Rename to "evidence aggregation"; remove causal language from code/docs | LOW (1 sprint) | Honest but less ambitious; still useful for evidence tracking |
| C. Clarify scope | Keep current code but document it as "causal hypothesis tracking" not "causal inference" | LOW (days) | Middle ground; acknowledges limitation without major refactor |
| D. Partial implementation | Implement do-operator for simple cases (no confounders) | MEDIUM (1 sprint) | Some rigor without full complexity |

**Recommendation**: Option C or D. Full do-calculus (Option A) requires:
- Structural equations for every BN edge
- Identification algorithms (backdoor, frontdoor criteria)
- Confounding adjustment
- This is a research project in itself

**Status**: NEEDS DECISION
**Assigned**: Professor Kirsh

---

#### ARCH-2: Transportability / Scope Extrapolation

**Panel Critique (Cartwright)**: "Scope is tracked but not USED. You record that a belief applies to 'office workers in open-plan offices' but then treat it as evidence for general claims about daylight→productivity. Where is the extrapolation logic? What licenses generalizing from offices to hospitals?"

| Task | Description | Status |
|------|-------------|--------|
| ARCH-2a | Implement transportability analysis (Pearl/Bareinboim) | PENDING |
| ARCH-2b | Add similarity metrics between settings | PENDING |
| ARCH-2c | Flag extrapolations with confidence penalties | PENDING |
| ARCH-2d | Require explicit transport assumptions | PENDING |

**Effort**: MEDIUM (1-2 sprints)
**Depends On**: ARCH-1 decision (if we go full Pearl, transportability follows naturally)

---

#### ARCH-3: Replication & Publication Bias (Meehl)

**Panel Critique (Meehl)**: "No replication tracking. Same finding from same lab twice isn't independent replication. You need to track: independent labs, different methods, different populations. Your accumulation treats all studies as independent."

| Task | Description | Status |
|------|-------------|--------|
| ARCH-3a | Add lab/institution tracking to beliefs | PENDING |
| ARCH-3b | Implement independence scoring (lab × method × population) | PENDING |
| ARCH-3c | Add crud factor adjustment for soft psychology | PENDING |
| ARCH-3d | Implement publication bias correction (funnel plot analysis) | PENDING |
| ARCH-3e | Model effect size decay (decline effect) | PENDING |
| ARCH-3f | Weight early findings LESS (regression to mean expectation) | PENDING |

**Effort**: MEDIUM (1-2 sprints)
**Dependencies**: Requires metadata extraction from papers (lab, methods)

---

#### ARCH-4: Formal Epistemic Calculus (Panel-Developed Plan)

**Panel Consultation**: `docs/PANEL_ARCH4_EPISTEMIC_CALCULUS_2026-02-12.md` ⭐ START HERE

**Panel**: Spohn (ranking), Pollock (defeat), Haack (foundherentism), Pearl (causal bridge), Lamport (TLA+), Liskov (architecture)

**Key Insight**: Do-calculus is for causal inference. The epistemic layer needs its own calculus:
- **Ranking Theory** (Spohn) — Ordinal ranks for entrenchment, formal revision rules
- **Defeasible Logic** (Pollock) — Non-monotonic inference with defeaters, reinstatement
- **Foundherentist Structure** (Haack) — Grounding + coherence, not just one metric

**Agreed Architecture** (from panel synthesis):
```
RANKING SERVICE (Spohn) + WARRANT SERVICE (Pollock) + GROUNDING SERVICE (Haack)
                              │
                              ▼
                EPISTEMIC-CAUSAL BRIDGE (Pearl)
                              │
                              ▼
                    CAUSAL LAYER (BN)
```

**Agreed Invariants** (5 formal properties to verify):
- INV-1: Consistency — ¬(warranted(B) ∧ warranted(rebutter(B)))
- INV-2: Groundedness — warranted → grounded ∨ supported_by_warranted
- INV-3: RankCoherence — supports(A,B) ∧ warranted(A) → rank(B) ≤ rank(A) + δ
- INV-4: DefeatAsymmetry — defeats(D,B) → rank(D) < rank(B)
- INV-5: BridgeCoherence — edge_confident(X,Y) → warranted(belief supporting X→Y)

**Implementation Phases** (panel-approved):

| Phase | Description | Sprint | Panel Reviewer |
|-------|-------------|--------|----------------|
| P1 | Data Model Refactoring (Belief → Content+Status+Provenance) | 1 | Liskov |
| P2 | Ranking Service (Spohn conditionalization, defeat-adjusted ranks) | 1 | Spohn |
| P3 | Warrant Service (defeat, reinstatement, warrant status) | 1 | Pollock |
| P4 | Grounding Service (experiential basis, foundherentist justification) | 1 | Haack |
| P5 | Epistemic-Causal Bridge (edge confidence, structure uncertainty) | 1 | Pearl |
| P6 | Formal Verification (TLA+ spec, model checking) | 1 | Lamport |

**Phase 1: Data Model Refactoring**

**Sprint 1.1: Design & Contracts** — ✓ COMPLETE (2026-02-13)
- Schemas: `contracts/schemas/propositional_content.v1.schema.json`
- Schemas: `contracts/schemas/epistemic_status.v1.schema.json`
- Schemas: `contracts/schemas/provenance.v1.schema.json`
- Schemas: `contracts/schemas/experiential_claim.v1.schema.json`
- Migration doc: `docs/ARCH4_MIGRATION_STRATEGY.md`
- Panel review: `docs/PANEL_REVIEW_SPRINT_1_1_SCHEMAS_2026-02-13.md`

**Sprint 1.2: Implementation & Migration** — ✓ COMPLETE (2026-02-13)
- Implementation: `src/models/propositional_content.py`
- Implementation: `src/models/epistemic_status.py`
- Implementation: `src/models/provenance.py`
- Belief refactored with v2 composition fields
- Migration script: `scripts/migrate_beliefs_to_v24.py`
- Persistence updated: `epistemic_v2` column

**Sprint 1.3: BN_graphical Coherence Integration** — ✓ COMPLETE (2026-02-13)
- BN Sprints 4-8: `epistemic_adapter`, `belief_conflict_handler`, `rank_calibrator`, `epistemic_workflow`
- AE Client: `src/services/bn_coherence_client.py` (integration layer)
- Tests: `tests/test_bn_coherence_client.py` (23 tests passing)
- Pre-integration hooks: `pre_integration_check()`, `should_integrate_belief()`
- BN_graphical total: 140 tests (adapter 49, conflict 17, calibrator 26, workflow 26, integration 22)
- Wired into `extraction_to_web.py` via `BN_COHERENCE_ENABLED` env var

**Sprint 1.4: P2-P6 Service Implementation** — ✓ COMPLETE (2026-02-14)
- P2: `src/services/ranking_service.py` — Spohn conditionalization, rank computation (~350 lines)
- P3: `src/services/warrant_service.py` — Pollock defeasible reasoning, reinstatement (~350 lines)
- P4: `src/services/grounding_service.py` — Haack foundherentism, experiential basis (~350 lines)
- P5: `src/services/graph_confidence_service.py` — Pearl integration, edge confidence (~350 lines)
- P6: `specs/EpistemicWeb.tla` — TLA+ formal specification with INV-1 through INV-5 (~300 lines)
- Orchestrator: `src/services/epistemic_orchestrator.py` — Integrates P2-P6 with WebOfBelief (~300 lines)
- Tests: `tests/test_epistemic_services.py` — 28 tests covering P2-P6 services and invariants
- Total AE new tests: 51 (28 P2-P6 + 23 BN coherence client)

| Task | Description | Status |
|------|-------------|--------|
| P1.1 | Split Belief into Content + Status + Provenance | ✓ COMPLETE |
| P1.2 | Create RankPair dataclass (rank, neg_rank) | ✓ COMPLETE |
| P1.3 | Create GroundingStatus enum and ExperientialClaim | ✓ COMPLETE |
| P1.4 | Update WebOfBelief to use new model | ✓ COMPLETE |
| P1.5 | Migration script for existing data | ✓ COMPLETE |

**Phase 2: Ranking Service (Spohn)** — ✓ COMPLETE (2026-02-14)

| Task | Description | Status |
|------|-------------|--------|
| P2.1 | Create RankingService class | ✓ COMPLETE |
| P2.2 | Implement base rank computation from evidence | ✓ COMPLETE |
| P2.3 | Implement Spohn conditionalization | ✓ COMPLETE |
| P2.4 | Implement defeat-adjusted ranks | ✓ COMPLETE |
| P2.5 | Property-based tests for rank coherence | ✓ COMPLETE |
| P2.6 | Panel review: Spohn | ✓ APPROVED |

**Phase 3: Warrant Service (Pollock)** — ✓ COMPLETE (2026-02-14)

| Task | Description | Status |
|------|-------------|--------|
| P3.1 | Create WarrantService class | ✓ COMPLETE |
| P3.2 | Implement prima facie warrant | ✓ COMPLETE |
| P3.3 | Implement rebutting defeat | ✓ COMPLETE |
| P3.4 | Implement undercutting defeat | ✓ COMPLETE |
| P3.5 | Implement reinstatement (recursive) | ✓ COMPLETE |
| P3.6 | Property-based tests for consistency invariant | ✓ COMPLETE |
| P3.7 | Panel review: Pollock | ✓ APPROVED |

**Phase 4: Grounding Service (Haack)** — ✓ COMPLETE (2026-02-14)

| Task | Description | Status |
|------|-------------|--------|
| P4.1 | Create GroundingService class | ✓ COMPLETE |
| P4.2 | Implement experiential basis tracking | ✓ COMPLETE |
| P4.3 | Implement grounding metric computation | ✓ COMPLETE |
| P4.4 | Refactor coherence contribution | ✓ COMPLETE |
| P4.5 | Combine into foundherentist justification status | ✓ COMPLETE |
| P4.6 | Panel review: Haack | ✓ APPROVED |

**Phase 5: Epistemic-Causal Bridge (Pearl)** — ✓ COMPLETE (2026-02-14)

| Task | Description | Status |
|------|-------------|--------|
| P5.1 | Create GraphConfidenceService | ✓ COMPLETE |
| P5.2 | Implement edge confidence from warrant + rank | ✓ COMPLETE |
| P5.3 | Implement structure uncertainty quantification | ✓ COMPLETE |
| P5.4 | Add identifiability check (basic) | ✓ COMPLETE |
| P5.5 | Panel review: Pearl | ✓ APPROVED |

**Phase 6: Formal Verification (Lamport)** — ✓ COMPLETE (2026-02-14)

| Task | Description | Status |
|------|-------------|--------|
| P6.1 | Write TLA+ specification | ✓ COMPLETE |
| P6.2 | Model check safety properties | PENDING (Requires TLC) |
| P6.3 | Model check liveness properties | PENDING (Requires TLC) |
| P6.4 | Document refinement relation to code | ✓ COMPLETE (in spec) |
| P6.5 | Final panel review: All | ✓ APPROVED (see docs/PANEL_REVIEW_ARCH4_P2_P6_2026-02-14.md) |

**Key Documents**:
- Sprint plan: `docs/ARCH4_SPRINT_PLAN_2026-02-12.md` ⭐ EXECUTION PLAN
- Panel consultation: `docs/PANEL_ARCH4_EPISTEMIC_CALCULUS_2026-02-12.md`
- Draft spec: `docs/EPISTEMIC_CALCULUS_SPEC_2026-02-12.md`

**Key References**:
- Spohn, W. (2012). *The Laws of Belief: Ranking Theory and Its Philosophical Applications*
- Pollock, J. (1995). *Cognitive Carpentry: A Blueprint for How to Build a Person*
- Pollock, J. (1987). "Defeasible Reasoning" — Cognitive Science 11(4)

**Effort**: 6 sprints (panel-approved phasing)
**Dependencies**: None — can run in parallel with other ARCH tasks
**Panel Sign-Off**: Spohn ✓, Pollock ✓, Haack ✓, Pearl ✓, Lamport ✓, Liskov ✓

---

#### ARCH-5: God Object Decomposition (Liskov)

**Panel Critique (Liskov)**: "Belief class is a god object. It has 20+ fields, optional everything, no clear invariants. What makes a Belief a Belief? Module boundaries are unclear. `web_of_belief.py` is 1900 lines. `epistemic_causal_bridge.py` is 2000 lines. These aren't modules - they're monoliths."

| Task | Description | Status |
|------|-------------|--------|
| ARCH-5a | Split Belief into focused types (TheoreticalBelief, EmpiricalBelief, etc.) | DEFERRED (needs comprehensive test coverage first) |
| ARCH-5b | Extract coherence computation to separate module | ✅ DONE (coherence.py in web_of_belief_modules) |
| ARCH-5c | Extract entrenchment computation to separate module | ✅ DONE (entrenchment.py in web_of_belief_modules) |
| ARCH-5d | Break web_of_belief.py into <500 line modules | ✅ DONE (modular extraction + compatibility layer) |
| ARCH-5e | Break epistemic_causal_bridge.py into focused modules | ✅ DONE (ecb_modules/: contrast_classes, causal_models, counterfactuals) |
| ARCH-5f | Define clear module interfaces | ✅ DONE (docs/architecture/module_interfaces.md) |

**Effort**: MEDIUM-HIGH (1-2 sprints, careful refactoring)
**Risk**: Breaking changes; needs comprehensive test coverage first

---

#### ARCH-6: Severe Testing (Mayo)

**Panel Critique (Mayo)**: "No severe tests. Your beliefs gain credence by accumulation, not by passing severe tests. A belief that's 'consistent with 10 studies' might not have been severely tested by ANY of them."

| Task | Description | Status |
|------|-------------|--------|
| ARCH-6a | Track study design quality (RCT vs observational) | ✅ DONE (StudyDesign enum, 8 levels, STUDY_DESIGN_SEVERITY_WEIGHT) |
| ARCH-6b | Compute "severity" of each supporting study | ✅ DONE (compute_severity now incorporates study design) |
| ARCH-6c | Require at least one severe test for high credence | ✅ DONE (severity_gate_check(): credence >0.70 requires MODERATELY_TESTED+) |
| ARCH-6d | Distinguish "consistent with" from "severely tested by" | ✅ DONE (EvidenceQuality enum + classify_evidence_quality()) |

**Effort**: MEDIUM (1 sprint)
**Requires**: Study design metadata extraction

---

### Priority Recommendation

1. **ARCH-4** (Formal Epistemic Calculus) — ⭐ PANEL-APPROVED PLAN READY
2. **ARCH-1** (Do-Calculus Decision) — Must decide before other causal work
3. **ARCH-3** (Replication/Bias) — High impact on credence accuracy
4. **ARCH-6** (Severe Testing) — Addresses confirmation bias structurally
5. **ARCH-5** (Decomposition) — Technical debt, enables other work
6. **ARCH-2** (Transportability) — Depends on ARCH-1

**Recommendation**: Start ARCH-4 Phase 1 immediately. It has:
- Full panel consultation complete
- 6-phase implementation plan
- Panel reviewers assigned to each phase
- Clear invariants and success criteria

**Parallel Tracks**:
- **Causal Track**: ARCH-1 → ARCH-2 (Pearl/Cartwright concerns)
- **Epistemic Track**: ARCH-4 → ARCH-6 → ARCH-3 (Spohn/Pollock/Meehl concerns)
- **Engineering Track**: ARCH-5 (Liskov concerns) — can run anytime

**The Big Picture**:
```
EPISTEMIC LAYER                    CAUSAL LAYER
(Spohn + Pollock)                  (Pearl)
     │                                  │
     ▼                                  ▼
┌─────────────────┐              ┌─────────────────┐
│ Ranking Theory  │              │  Do-Calculus    │
│ (entrenchment)  │              │  (intervention) │
├─────────────────┤              ├─────────────────┤
│ Defeasible Logic│──────────────│  BN Structure   │
│ (defeat/warrant)│   bridges    │  (DAG edges)    │
└─────────────────┘              └─────────────────┘
         │                                  │
         └──────────┬───────────────────────┘
                    ▼
         ┌─────────────────────┐
         │ Epistemic-Causal    │
         │ Bridge (confidence  │
         │ in causal claims)   │
         └─────────────────────┘
```

---

### Previous Sprints (Completed)

1. ~~**Sprint 2.5 Social Epistemology**~~ ✓ COMPLETE
2. ~~**Panel Convening**~~ ✓ COMPLETE — P-TC (7 decisions), P-QW (6 decisions)
3. ~~**Strategic TODOs 1-3**~~ ✓ COMPLETE — Credibility, Interpretive, VOI
4. ~~**Sprint 2.6 Panel Implementation**~~ ✓ COMPLETE — P-TC Track A, P-QW Track B
5. ~~**Technical Debt**~~ ✓ ALL COMPLETE [TD-A, TD-B, TD-C, TD-D, TD-E]
6. ~~**Sprint 2.0.4-2.0.5**~~ ✓ COMPLETE — Pipeline testing and error handling
7. ~~**AF-AE Integration: BibTeX Metadata**~~ ✓ COMPLETE (BIB-1 through BIB-7)
8. ~~**Entrenchment Historical Replay + Monitor**~~ ✓ COMPLETE (ENT-1 through ENT-5)
9. ~~**Sprint 3.0 Phase 1-2**~~ ✓ COMPLETE — API, Query Engine, Export, Visualization
10. ~~**Panel Consultations Sprint 3.0**~~ ✓ COMPLETE (2026-02-09)

### Paused/Deferred

11. **Sprint ECB: Epistemic-Causal Bridge Repair** — PAUSED (post-MVP)
12. **Article Discovery + PDF Retrieval Monitoring** — PAUSED (DISC-1, DISC-2 complete)
13. **VOI Discovery & PDF Retrieval Infrastructure** — PAUSED (INFRA-1 through INFRA-15)

---

## Implementation Decisions - Panel Review P-ECB-R2 ✓ COMPLETE

*Added: 2026-02-11, Resolved: 2026-02-11*

Panel P-ECB-R2 (Cartwright, Simon, Pearl) reviewed 6 implementation decisions. All recommendations implemented.

| ID | Decision | Panel Verdict | Resolution |
|----|----------|---------------|------------|
| PA-1 | Threshold parsing defaults to `>=` | **Approved with Enhancement** | Added `operator_inferred` flag; logs warning when operator assumed |
| PA-2 | Dosage hierarchy | **Revised** | Removed implicit hierarchy; added `dosage_satisfies` field to EnablingConditions |
| PA-3 | Temporal normalization to minutes | **Revised** | Changed to seconds internally; added TemporalSpec.display() helper |
| PA-4 | "Near threshold" = 0.1 gap | **Approved with Modification** | Changed default to 0.15; made configurable via parameter |
| PA-5 | Tracking non-theory beliefs | **Revised** | Two-tier tracking: _excluded (actionable) vs _skipped (noise) |
| PA-6 | Positive temporal_lag = precedes | **Revised** | Added TemporalSpec dataclass with explicit {magnitude, unit, direction} |

### Key Changes Made

**PA-1**: `_check_threshold_condition()` now returns 3-tuple with `operator_inferred` flag; logs warning when assuming `>=`.

**PA-2**: Added `dosage_satisfies: List[str]` field to `EnablingConditions` in `web_of_belief.py`. Removed implicit hierarchy from `_dosage_satisfies()`.

**PA-3 & PA-6**: Added `TemporalSpec` dataclass with `{magnitude, unit, direction}`. Internal normalization to seconds. Display helpers preserve readability.

**PA-4**: `get_exclusion_summary(near_threshold_gap=0.15)` now configurable, default changed from 0.1 to 0.15.

**PA-5**: Added `_skipped_beliefs` registry for "not_in_theory" exclusions. New method `get_skipped_beliefs()`. Summary includes `total_skipped` count.

---

## Sprint ECB: Epistemic-Causal Bridge Repair

**Added**: 2026-02-10
**Priority**: P0 (System Coherence Critical)
**Panel**: P-ECB-R (Haack, Pearl, van Fraassen, Simon, Cartwright, Parnas, Brooks)
**Target Version**: V23.1.0
**Context**: System coherence concerns identified. Epistemic-causal bridge has two implementations, duplicate classes, and is not wired into pipeline. Panel approved comprehensive repair.

### Problem Statement

1. **Two implementations exist**: Repo file ≠ external research file (tests use wrong one)
2. **Duplicate class definitions**: Bridge defines `Belief`, `Credence`, etc. that duplicate `web_of_belief.py`
3. **Not used in pipeline**: `app/tasks/pipeline.py` makes zero bridge calls
4. **No feedback loop**: Counterfactual results don't update the web
5. **Van Fraassen contrast classes disconnected**: Elaborate but not integrated

### Panel Recommendations (P-ECB-R)

| Expert | Key Recommendation |
|--------|-------------------|
| **Haack** | Equations need TWO weights: supportiveness (entrenchment) + security (experiential grounding) |
| **Pearl** | Separate DAG structure from parameters; track associational/interventional/counterfactual |
| **van Fraassen** | If contrast doesn't transfer, return undefined; route gaps to VOI |
| **Simon** | Target ~500 lines (down from 2400); ruthless simplification |
| **Cartwright** | Enabling conditions GATE computation; capacities don't manifest without conditions |
| **Parnas** | Delete duplicates; single source of truth; add error handling |
| **Brooks** | Checkpoint each sprint; don't add features while simplifying |

### Archived Features (For Future Reintegration)

| Feature | Archive Location | Future TODO |
|---------|-----------------|-------------|
| Individual Differences | `quarantine/2026-02-10/individual_differences.py` | IND-1 through IND-4 |
| Cultural Meanings | `quarantine/2026-02-10/cultural_meaning.py` | CULT-1 through CULT-5 |
| Argument Attack Analysis | **REINTEGRATED** → `src/services/argument_attack.py` | ~~ATK-1~~ ✓ ~~ATK-2~~ ✓ ~~ATK-3~~ ✓ ~~ATK-4~~ ✓ |
| Elaborate Generalization | `quarantine/2026-02-10/generalization_elaborate.py` | GEN-1 through GEN-4 |

See: `docs/ARCHIVED_FEATURES_EPISTEMIC_CAUSAL_BRIDGE_2026-02-10.md`

---

### Sprint ATK: Argument Attack Reintegration ✓ PARTIAL COMPLETE

**Added**: 2026-02-11
**Completed**: ATK-1, ATK-3
**Remaining**: none

| ID | Task | Description | Status |
|----|------|-------------|--------|
| ATK-1 | Wire into tensions.jsonl | Enhance `get_tensions()` with attack analysis, output to `tensions.jsonl` | ✓ DONE |
| ATK-2 | Claim extraction detection | Add attack patterns to claim extraction (NLP) | DONE |
| ATK-3 | Shift classification | Rule-based heuristics for classifying contrast shifts | ✓ DONE |
| ATK-4 | Review UI | Streamlit page for attack review | DONE |

**Implementation Summary (2026-02-11)**:

1. **New module**: `src/services/argument_attack.py` (~600 lines)
   - `AttackType` enum (8 types: CONFOUNDER, BOUNDARY_CONDITION, etc.)
   - `ContrastShiftType` enum (6 types: PRESERVING, POPULATION_SHIFT, etc.)
   - `ArgumentAttack` dataclass with full contrast class analysis
   - `ShiftClassifier` for text-based heuristics (fallback)
   - `StructuredAttackDetector` for metadata-based detection (no NLP needed)

2. **Structured detection** (per user insight: "many attacks fall into categories easy to identify without NLP"):
   - `detect_population_mismatch()` — PopulationContext comparison
   - `detect_baseline_shift()` — Baseline characterization differences
   - `detect_contrast_condition_mismatch()` — Different comparison conditions
   - `detect_dosage_mismatch()` — EnablingConditions.dosage_satisfies
   - `detect_measurement_mismatch()` — Outcome tag differences
   - `detect_theory_conflict()` — Different theoretical frameworks

3. **Tension integration**: `extraction_to_web.get_tensions()` now calls `enhance_tension_with_attack_analysis()` when available

4. **Tests**: 24 tests in `tests/test_argument_attack.py` — all passing

**Key insight**: Many apparent contradictions are contrast shifts, not true refutations. This system distinguishes them.

---

### Sprint ECB-1: Cleanup and Consolidation ✓ COMPLETE

**Goal**: Single source of truth, remove dead code
**Completed**: 2026-02-10
**Outcome**: 68+89 tests pass, duplicates marked DEPRECATED, features archived

| ID | Task | Description | Status |
|----|------|-------------|--------|
| ECB-1.0 | Diff implementations | Compare repo vs external file, document differences | ✓ DONE — Only 43 lines differ (all V23.0.0 entrenchment) |
| ECB-1.1 | Archive features | Move IndividualDiff, CulturalMeaning, ArgumentAttack to quarantine with headers | ✓ DONE — 4 files + README |
| ECB-1.2 | Mark duplicates DEPRECATED | EpistemicLevel, BeliefStatus, Credence, Belief with clear warnings | ✓ DONE — Kept for stub/demo, marked for ECB-2 removal |
| ECB-1.3 | Update test imports | Fix `test_epistemic_causal_integration.py` to use repo module | ✓ DONE — Removed external path, 68 tests pass |
| ECB-1.4 | Verify tests pass | Run bridge, persistence, warrants tests | ✓ DONE — 68+89 tests pass |

**Checkpoint**: All tests pass ✓, file compiles ✓, pipeline unchanged ✓

**Notes**:
- Duplicate classes MARKED as DEPRECATED rather than deleted (per Brooks: "Don't break while simplifying")
- Stub WebOfBelief kept for demo functions (marked for removal in ECB-2)
- V23.0.0 entrenchment code preserved intact (web_of_belief.py untouched)

---

### Sprint ECB-2: Core Integration ✓ COMPLETE

**Goal**: Working bridge wired into pipeline
**Completed**: 2026-02-10
**Outcome**: Bridge wired into pipeline.py, CLI flags added, feedback loop implemented

| ID | Task | Description | Status |
|----|------|-------------|--------|
| ECB-2.1 | Simplify class | Reduced 2462→2020 lines (~500 target deferred to incremental cleanup) | ✓ DONE |
| ECB-2.2 | Add enabling conditions | `StructuralEquation.enabling_conditions` + `is_applicable(context)` → (bool, reason) | ✓ DONE |
| ECB-2.3 | Wire into pipeline | Stage 2.8 in pipeline.py, `--no-causal` and `--causal-credence-threshold` CLI flags | ✓ DONE |
| ECB-2.4 | Add feedback loop | `update_web_from_result()` with proportional delta (Simon), conditional tracking | ✓ DONE |

**Checkpoint**: Pipeline runs with bridge ✓, 68 tests pass ✓

**Notes**:
- Bridge builds causal models from high-credence beliefs
- CLI: `--no-causal` disables, `--causal-credence-threshold` configures belief threshold
- Feedback loop updates uncertainty proportionally to sensitivity
- Demo functions archived to quarantine/2026-02-10/demo_and_stub_web.py

---

### Sprint ECB-3: Van Fraassen and Polish ✓ COMPLETE

**Goal**: Full contrast class rigor, feedback loop working
**Completed**: 2026-02-10
**Dependencies**: ECB-2 complete

| ID | Task | Description | Status |
|----|------|-------------|--------|
| ECB-3.1 | Contrast transfer rules | `ContrastTransferType` enum, configurable thresholds via `AE_CONTRAST_THRESHOLD_*` | ✓ DONE |
| ECB-3.2 | Return undefined | `is_defined=False` + `reason_undefined` when contrast transfer fails | ✓ DONE |
| ECB-3.3 | Gap identification | 5 gap types: missing_contrast, low_coverage, theory_conflict, baseline_unknown, blocked_beliefs | ✓ DONE |
| ECB-3.4 | Security weight | `compute_security()` and `compute_model_security()` with Haack weights | ✓ DONE |
| ECB-3.5 | Update ARCHITECTURE.md | Causal layer diagram, transfer rules, gap types, security weights documented | ✓ DONE |
| ECB-3.6 | Error handling pass | `BridgeError` hierarchy, graceful empty web handling, validation | ✓ DONE |

**Checkpoint**: 68 integration tests pass ✓, 153 related tests pass ✓, docs updated ✓

**Panel Consultation**: P-ECB-R reviewed all decisions
- D1-D6 approved with minor notes
- Future work: meaning equivalence flag, enabling_unclear gap type, theory conflict decomposition
- See: `docs/PANEL_CONSULTATION_ECB-3_2026-02-10.md`

---

### Pending: Panel-Recommended ECB Enhancements

**Added**: 2026-02-10
**Source**: Full panel review of Sprints ECB-1, ECB-2, and ECB-3
**Panel**: Pearl, van Fraassen, Haack, Simon, Cartwright, Parnas, Brooks
**Documentation**: `docs/PANEL_CONSULTATION_ECB_FULL_REVIEW_2026-02-10.md`

These enhancements address limitations identified during comprehensive panel review of all ECB repair work. Each improves the epistemic-causal bridge's ability to handle real-world complexity.

| ID | Task | Priority | Panel Source | Status |
|----|------|----------|--------------|--------|
| ECB-F1 | Meaning equivalence flag | P2 | van Fraassen | ☐ TODO |
| ECB-F2 | Add `enabling_unclear` gap type | P2 | Cartwright | ☐ TODO |
| ECB-F3 | Decompose theory conflict | P2 | Pearl | ☐ TODO |
| ECB-F4 | Track contrast class source | P3 | Haack | ☐ TODO |
| ECB-F5 | Deprecate `transfer_type_str` | P3 | Parnas | ☐ TODO |
| ECB-F6 | ECB-3 boundary value tests | P1 | Brooks | ✓ DONE |
| ECB-F7 | Prominent causal failure warning | P1 | Pearl | ✓ DONE |
| ECB-F8 | Flag causal-empirical beliefs | P2 | Pearl | ☐ TODO |
| ECB-F9 | Contrast-gated feedback | P1 | van Fraassen | ✓ DONE |
| ECB-F10 | Observational grounding | P2 | Haack | ☐ TODO |
| ECB-F11 | Configurable feedback rate | P2 | Simon | ☐ TODO |
| ECB-F12 | Complete enabling condition checks | P2 | Cartwright | ✓ DONE |
| ECB-F13 | Excluded belief registry | P2 | Cartwright | ✓ DONE |
| ECB-F14 | Lazy bridge import | P1 | Parnas | ✓ DONE |
| ECB-F15 | CLI shorthand flags | P3 | Parnas | ✓ DONE |
| ECB-F16 | User documentation sprint | P1 | Brooks | ✓ DONE |
| ECB-F17 | Stub contrast warning | P3 | van Fraassen | ✓ DONE |
| ECB-F18 | DEPRECATED removal deadline | P2 | Parnas | ✓ DONE |

**P1 Features Complete** (2026-02-10):
- ECB-F6: 29 boundary value tests in `tests/test_ecb3_boundaries.py`
- ECB-F7: Prominent warning in `web_state.json` when causal layer fails
- ECB-F9: Feedback loop gated on `is_defined` and contrast transfer type
- ECB-F14: Lazy import in `pipeline.py` isolates module failures
- ECB-F16: User guide at `docs/USER_GUIDE_CAUSAL_BRIDGE.md`

**Panel Action Items Complete** (2026-02-10):
- ECB-F12: Complete enabling condition checks (threshold parsing, dosage, temporal windows)
- ECB-F13: `ExcludedBelief` dataclass, `get_excluded_beliefs()`, `get_exclusion_summary()`
- ECB-F15: `--cct` shorthand for `--causal-credence-threshold`
- ECB-F17: Van Fraassen contrast class warning in archived stub
- ECB-F18: `REMOVE_BY: V24.0` comments on all DEPRECATED classes

#### ECB-F1: Meaning Equivalence Flag (van Fraassen)

**What**: Add `meaning_equivalent: bool` to `ContrastAssessment` that can override MEANING_SHIFT classification.

**Why**: Currently, if two populations use different words for the same construct (e.g., "nature" vs "green space"), we classify this as MEANING_SHIFT and refuse to transfer. But sometimes meanings differ lexically yet are *functionally equivalent*—the construct produces the same behavioral/psychological effects. This flag allows domain experts to mark such cases as transferable despite surface meaning differences.

**Implementation**:
```python
@dataclass
class ContrastAssessment:
    ...
    meaning_equivalent: bool = False  # If True, override MEANING_SHIFT → POPULATION_SHIFT
```

**Location**: `src/services/epistemic_causal_bridge.py:ContrastAssessment`

---

#### ECB-F2: Add `enabling_unclear` Gap Type (Cartwright)

**What**: Add sixth gap type `enabling_unclear` distinct from `blocked_beliefs`.

**Why**: There's a crucial difference between:
- `blocked_beliefs`: We KNOW the enabling conditions but they're UNMET
- `enabling_unclear`: We DON'T KNOW what the enabling conditions ARE

The second is a deeper epistemic gap—we can't even evaluate whether the mechanism will manifest. This matters for research prioritization: understanding enabling conditions should precede testing them.

**Implementation**:
```python
# In _identify_gaps():
if has_causal_claim_without_conditions(belief):
    gaps.append(EpistemicGap(
        gap_id=make_gap_id(),
        gap_type="enabling_unclear",
        description=f"Enabling conditions unknown for: {belief.belief_id}",
        priority=0.6,  # Higher than blocked_beliefs (0.4)
        suggested_query=f"What conditions enable {mechanism}?"
    ))
```

**Location**: `src/services/epistemic_causal_bridge.py:_identify_gaps()`

---

#### ECB-F3: Decompose Theory Conflict (Pearl)

**What**: Split `theory_conflict` gap into `structural_conflict` and `parametric_conflict`.

**Why**: Pearl noted that theory disagreements come in two flavors:
- **Structural**: Theories propose different DAGs (different causal relationships)
- **Parametric**: Theories agree on DAG but disagree on coefficients

These require different resolutions:
- Structural conflicts need experiments that distinguish causal pathways
- Parametric conflicts need more precise measurement of effect sizes

**Implementation**:
```python
class TheoryConflictType(Enum):
    STRUCTURAL = "structural"    # Different DAGs
    PARAMETRIC = "parametric"    # Same DAG, different coefficients
    MIXED = "mixed"              # Both

# Detect by comparing edges across theory models
if theory_models have different edges:
    conflict_type = STRUCTURAL
elif theory_models have same edges but different parameters:
    conflict_type = PARAMETRIC
```

**Location**: `src/services/epistemic_causal_bridge.py:_identify_gaps()`

---

#### ECB-F4: Track Contrast Class Source (Haack)

**What**: Track whether contrast class was explicitly stated in paper methods vs inferred from results.

**Why**: Haack's foundherentism weights experiential grounding. A contrast class stated in the Methods section ("we compared forest exposure to urban control") has higher epistemic security than one inferred from Results ("effect size suggests the contrast was..."). This should affect the security weight bonus.

**Implementation**:
```python
@dataclass
class ContrastClass:
    ...
    source: str = "inferred"  # Already exists
    source_location: Optional[str] = None  # NEW: "methods", "results", "discussion"

# In compute_security():
if contrast_class.source_location == "methods":
    contrast_bonus = 0.20  # Higher
else:
    contrast_bonus = 0.10  # Lower
```

**Location**: `src/services/epistemic_causal_bridge.py:ContrastClass`, `compute_security()`

---

#### ECB-F5: Deprecate `transfer_type_str` (Parnas)

**What**: Remove backward-compatibility `transfer_type_str: str` field, use only `transfer_type: ContrastTransferType` enum.

**Why**: Parnas correctly identified this as technical debt. Dual representations complicate the interface and invite bugs where code checks one but not the other. The enum should be the single source of truth.

**Implementation**:
1. Deprecation warning in V23.1
2. Remove in V24.0
3. Update all callers to use `.transfer_type.value` if string needed

**Location**: `src/services/epistemic_causal_bridge.py:ContrastAssessment`

---

#### ECB-F6: ECB-3 Boundary Value Tests (Brooks)

**What**: Add explicit tests for ECB-3 features at boundary values.

**Why**: Brooks noted the new code is tested only implicitly. We need explicit tests for:
- Contrast similarity at exact thresholds (0.49 vs 0.50 vs 0.51)
- Gap identification with edge cases (empty gaps, all gaps)
- Security weight bounds (min 0.05, max 0.95)
- Error handling (None inputs, empty dicts)

**Implementation**:
```python
# tests/test_ecb3_boundaries.py
class TestContrastThresholdBoundaries:
    def test_similarity_at_direct_threshold(self):
        # 0.90 should be DIRECT, 0.89 should be BASELINE_SHIFT

    def test_similarity_at_population_threshold(self):
        # 0.50 should be POPULATION_SHIFT, 0.49 should be MEANING_SHIFT

class TestSecurityWeightBounds:
    def test_minimum_security_floor(self):
        # Even worst case should be >= 0.05

    def test_maximum_security_cap(self):
        # Even best case should be <= 0.95
```

**Location**: `tests/test_ecb3_boundaries.py` (new file)

---

#### ECB-F7: Prominent Causal Failure Warning (Pearl)

**What**: Add prominent warning to output when causal layer fails to build.

**Why**: Currently, if `build_causal_models()` fails, the pipeline continues with `enabled: False` in the output. Users might not notice this flag and draw conclusions without understanding that causal annotations are missing. Pearl: *"They might not notice the `enabled: False` flag and draw conclusions without understanding limitations."*

**Implementation**:
```python
# In pipeline.py _build_causal_layer():
except Exception as e:
    logger.warning(f"Causal bridge failed: {e}")
    result['causal_layer'] = {
        'enabled': False,
        'error': str(e),
        'WARNING': 'CAUSAL LAYER UNAVAILABLE - Results lack causal annotations'
    }
    # Also add to top-level warnings list
    result.setdefault('warnings', []).append(
        'CAUSAL LAYER FAILED: Results do not include causal inference annotations'
    )
```

**Location**: `app/tasks/pipeline.py:_build_causal_layer()`

---

#### ECB-F8: Flag Causal-Empirical Beliefs (Pearl)

**What**: Automatically flag empirical beliefs that contain causal language ("causes", "leads to", "results in").

**Why**: Beliefs classified as EMPIRICAL should describe observations, not causal structure. When an empirical belief says "X causes Y," it's making a structural claim despite being classified as observational. These hybrid beliefs deserve epistemological review—they may be misclassified or may reveal implicit causal assumptions. Pearl: *"Empirical beliefs with CAUSAL language should be flagged for review."*

**Implementation**:
```python
CAUSAL_PATTERNS = ['causes', 'leads to', 'results in', 'produces', 'triggers']

def flag_causal_empirical(belief: Belief) -> Optional[str]:
    if belief.level in (EpistemicLevel.EMPIRICAL, EpistemicLevel.OBSERVATIONAL):
        content = belief.content.lower()
        for pattern in CAUSAL_PATTERNS:
            if pattern in content:
                return f"REVIEW: Empirical belief contains causal language '{pattern}'"
    return None
```

**Location**: `src/services/epistemic_causal_bridge.py` (new function), called during `build_causal_models()`

---

#### ECB-F9: Contrast-Gated Feedback (van Fraassen)

**What**: Gate the feedback loop so it only updates belief credences when contrast transfer is valid.

**Why**: Currently, if a counterfactual has HIGH robustness but LOW contrast similarity, we still update credences. But low contrast similarity means the finding may not apply at all—we're reinforcing beliefs based on potentially non-transferable results. van Fraassen: *"Don't reinforce beliefs based on results that may not transfer."*

**Implementation**:
```python
def update_web_from_result(self, result: QuineanCounterfactualResult):
    # Gate: Only update if contrast transfer is valid
    if not result.is_defined:
        logger.info(f"Skipping feedback: result undefined ({result.reason_undefined})")
        return {'updates': [], 'reason': 'result_undefined'}

    if result.contrast.transfer_type == ContrastTransferType.MEANING_SHIFT:
        logger.info("Skipping feedback: contrast transfer is MEANING_SHIFT")
        return {'updates': [], 'reason': 'meaning_shift'}

    # Proceed with feedback only for valid transfers
    ...
```

**Location**: `src/services/epistemic_causal_bridge.py:update_web_from_result()`

---

#### ECB-F10: Observational Grounding (Haack)

**What**: Include observational beliefs in `compute_security()` even when excluded from structure building.

**Why**: Haack's foundherentism says observational beliefs have the HIGHEST security—they're directly experiential. Currently, `_get_theory_beliefs()` filters them out for structure building (correct), but `compute_security()` should still count them because they GROUND the model even if they don't shape it. Haack: *"You're ignoring your most grounded evidence."*

**Implementation**:
```python
def compute_security(self, belief_ids: Optional[List[str]] = None) -> Dict[str, Any]:
    # Include ALL beliefs in security computation, not just structural ones
    if belief_ids is None:
        # Use all beliefs, including observational
        belief_ids = list(self.web.beliefs.keys())

    # Observational beliefs get highest base security
    level_weights = {
        'observational': 0.9,   # Highest - direct experience
        'empirical': 0.7,       # Systematic observation
        'intermediate': 0.5,    # Mixed
        'theoretical': 0.3,     # Abstract
    }
```

**Location**: `src/services/epistemic_causal_bridge.py:compute_security()`

---

#### ECB-F11: Configurable Feedback Rate (Simon)

**What**: Make the feedback loop learning rate configurable via environment variable.

**Why**: The current 0.2 cap prevents overreaction to single queries, but different domains warrant different learning rates. High-stakes domains (medical) should update slowly; exploratory domains could update faster. Simon: *"Should the cap be configurable? Different domains may warrant different learning rates."*

**Implementation**:
```python
import os

# Configurable feedback rate (default 0.2 = 20% max change per query)
FEEDBACK_MAX_DELTA = float(os.environ.get('AE_FEEDBACK_MAX_DELTA', '0.2'))

def update_web_from_result(self, result: QuineanCounterfactualResult):
    ...
    # Use configurable rate instead of hardcoded 0.2
    delta = sensitivity * FEEDBACK_MAX_DELTA * (1 - old_uncertainty)
```

**Location**: `src/services/epistemic_causal_bridge.py` (module-level constant + update_web_from_result)

---

#### ECB-F12: Complete Enabling Condition Checks (Cartwright)

**What**: Implement threshold, dosage, and temporal condition checking in `is_applicable()`.

**Why**: The current implementation only checks `blocking_factors` and `concurrent_factors`. But real mechanisms have more nuanced enabling conditions: thresholds ("only above 30 minutes exposure"), dosage ("only at high intensity"), temporal windows ("only during recovery period"). Cartwright: *"What about threshold conditions, dosage conditions, temporal conditions?"*

**Implementation**:
```python
@dataclass
class EnablingConditions:
    blocking_factors: List[str] = field(default_factory=list)
    concurrent_factors: List[str] = field(default_factory=list)
    # NEW: Threshold conditions
    thresholds: Dict[str, Tuple[float, str]] = field(default_factory=dict)  # var -> (min_value, unit)
    # NEW: Dosage conditions
    dosage_requirements: Dict[str, str] = field(default_factory=dict)  # var -> level ("low"|"medium"|"high")
    # NEW: Temporal windows
    temporal_windows: Dict[str, Tuple[str, str]] = field(default_factory=dict)  # phase -> (start, end)

def is_applicable(self, context: Dict[str, Any]) -> Tuple[bool, str]:
    # Check thresholds
    for var, (min_val, unit) in self.thresholds.items():
        if var in context and context[var] < min_val:
            return (False, f"threshold_unmet:{var}<{min_val}{unit}")

    # Check dosage
    for var, required_level in self.dosage_requirements.items():
        if var in context and not meets_dosage(context[var], required_level):
            return (False, f"dosage_insufficient:{var}!={required_level}")

    # Check temporal window
    for phase, (start, end) in self.temporal_windows.items():
        if 'current_phase' in context and not in_window(context['current_phase'], start, end):
            return (False, f"temporal_mismatch:{phase}")
    ...
```

**Location**: `src/services/epistemic_causal_bridge.py:EnablingConditions`, `StructuralEquation.is_applicable()`

---

#### ECB-F13: Excluded Belief Registry (Cartwright)

**What**: Track beliefs excluded from causal models with reasons.

**Why**: When building causal models, we filter out empirical/observational beliefs and low-credence beliefs. This is correct, but we lose track of what was excluded and why. Cartwright: *"The filtering should TRACK which empirical beliefs were excluded and why. This is data, not noise."*

**Implementation**:
```python
@dataclass
class ExcludedBelief:
    belief_id: str
    reason: str  # "low_credence", "empirical_level", "enabling_blocked", etc.
    details: Dict[str, Any] = field(default_factory=dict)

class EpistemicCausalBridge:
    def __init__(self, web):
        ...
        self._excluded_beliefs: List[ExcludedBelief] = []

    def _get_theory_beliefs(self, theory_id, credence_threshold):
        for belief in candidates:
            if belief.credence.value < credence_threshold:
                self._excluded_beliefs.append(ExcludedBelief(
                    belief.belief_id, "low_credence",
                    {'credence': belief.credence.value, 'threshold': credence_threshold}
                ))
            elif belief.level in (EpistemicLevel.EMPIRICAL, EpistemicLevel.OBSERVATIONAL):
                self._excluded_beliefs.append(ExcludedBelief(
                    belief.belief_id, "empirical_level",
                    {'level': belief.level.value}
                ))
            ...

    def get_excluded_beliefs(self) -> List[ExcludedBelief]:
        return self._excluded_beliefs
```

**Location**: `src/services/epistemic_causal_bridge.py` (new class + tracking in _get_theory_beliefs)

---

#### ECB-F14: Lazy Bridge Import (Parnas)

**What**: Import the bridge module only when needed to isolate import failures.

**Why**: Currently, the pipeline imports from epistemic_causal_bridge at the top of the file. If that module fails to load (syntax error, missing dependency), the entire pipeline fails. Lazy import isolates the failure. Parnas: *"If that module fails to load, the entire pipeline fails."*

**Implementation**:
```python
# In pipeline.py - BEFORE:
from src.services.epistemic_causal_bridge import EpistemicCausalBridge

# AFTER:
def _build_causal_layer(web, options):
    try:
        from src.services.epistemic_causal_bridge import EpistemicCausalBridge
    except ImportError as e:
        logger.error(f"Failed to import epistemic_causal_bridge: {e}")
        return {'enabled': False, 'error': f'import_failed: {e}'}

    bridge = EpistemicCausalBridge(web)
    ...
```

**Location**: `app/tasks/pipeline.py` (change top-level import to lazy import)

---

#### ECB-F15: CLI Shorthand Flags (Parnas)

**What**: Add shorthand flags for frequently-used long options.

**Why**: `--causal-credence-threshold` is verbose for power users. Parnas: *"Consider also accepting `--cct` as shorthand."*

**Implementation**:
```python
# In article_eater_contract_cli.py
parser.add_argument(
    '--causal-credence-threshold', '--cct',
    type=float,
    default=0.5,
    help='Minimum credence for causal model beliefs (default 0.5)'
)
```

**Location**: `app/cli/article_eater_contract_cli.py`

---

#### ECB-F16: User Documentation Sprint (Brooks)

**What**: Create user-facing documentation for causal features.

**Why**: The bridge repair focused on the MODULE, not the USER EXPERIENCE. Brooks: *"I don't see user documentation, example notebooks, or integration tests with real data."*

**Deliverables**:
1. `docs/USER_GUIDE_CAUSAL_BRIDGE.md` — How to use causal features
2. `notebooks/causal_counterfactual_examples.ipynb` — Example queries
3. `tests/integration/test_causal_real_data.py` — Real-world validation
4. CLI examples in README

**Location**: `docs/`, `notebooks/`, `tests/integration/`

---

#### ECB-F17: Stub Contrast Warning (van Fraassen)

**What**: Add warning to stub WebOfBelief documentation about contrast class limitations.

**Why**: The demo stub doesn't model contrast classes properly. Tests using the stub may give false confidence about contrast handling. van Fraassen: *"Any tests using the stub may give false confidence."*

**Implementation**:
```python
# In quarantine/2026-02-10/epistemic_causal_bridge_features/demo_and_stub_web.py
class WebOfBelief:
    """
    MINIMAL STUB for demonstration/testing only.

    WARNING: This stub does NOT properly model contrast classes.
    - Beliefs created here lack contrast_class field
    - Tests using this stub do NOT validate contrast handling
    - Use the real WebOfBelief from web_of_belief.py for production
    """
```

**Location**: `quarantine/2026-02-10/epistemic_causal_bridge_features/demo_and_stub_web.py`

---

#### ECB-F18: DEPRECATED Removal Deadline (Parnas)

**What**: Add `# REMOVE_BY: V24.0` comments to DEPRECATED code.

**Why**: DEPRECATED code should have a removal deadline. Without it, developers don't know if it's safe to remove or still in transition. Parnas: *"DEPRECATED code should be removed in V24.0. Add a `# REMOVE_BY: V24.0` comment."*

**Implementation**:
```python
class EpistemicLevel(Enum):
    """
    DEPRECATED: Use web_of_belief.EpistemicLevel instead.
    REMOVE_BY: V24.0
    ...
    """
```

**Location**: `src/services/epistemic_causal_bridge.py` (all DEPRECATED classes)

---

### Future Archived Feature Reintegration TODOs

**Individual Differences** (after core bridge stable):
| ID | Task | Priority |
|----|------|----------|
| IND-1 | Literature review: individual difference moderators in CNfA | P2 |
| IND-2 | Populate IndividualDifferenceFactor with literature data | P2 |
| IND-3 | Add CNS questionnaire to Streamlit UI | P3 |
| IND-4 | Validate personalized predictions | P3 |

**Cultural Meanings** (after contrast transfer working):
| ID | Task | Priority |
|----|------|----------|
| CULT-1 | Literature review: cultural variation in nature concepts | P2 |
| CULT-2 | Design cultural meaning schema with anthropology input | P2 |
| CULT-3 | Populate for major cultural contexts | P3 |
| CULT-4 | Implement meaning similarity metric | P3 |
| CULT-5 | Add cultural context to PopulationContext | P3 |

**Argument Attack Analysis** (after contrast extraction working):
| ID | Task | Priority |
|----|------|----------|
| ATK-1 | Integrate attack analysis with coherence violation detection | P2 |
| ATK-2 | Add attack detection to claim extraction pipeline | P3 (DONE) |
| ATK-3 | Train classifier for shift type identification | P3 |
| ATK-4 | UI for reviewing detected attacks | P3 (DONE) |

---

### Sprint ECB Documentation

| Document | Purpose |
|----------|---------|
| `docs/PANEL_P-ECB-R_CONTEXT_2026-02-10.md` | Full panel context |
| `docs/PANEL_P-ECB-R_RESPONSES_2026-02-10.md` | Expert responses |
| `docs/PANEL_P-ECB-R_PLAN_REVIEW_2026-02-10.md` | Plan review with updates |
| `docs/IMPLEMENTATION_PLAN_BRIDGE_REPAIR_2026-02-10.md` | Detailed implementation plan |
| `docs/ARCHIVED_FEATURES_EPISTEMIC_CAUSAL_BRIDGE_2026-02-10.md` | Archived features documentation |

---

## Completed: Panel Consultations (2026-02-09)

**Panel P-VOI**: Value of Information - Theoretical Grounding
- Panelists: Howard, Pearl, Simon, Thagard, Haack, Bates
- Key outcomes:
  - Clarified VOI semantics (Expected Epistemic Gain, not classical VOI)
  - Separated structural VOI from epistemic VOI (Pearl)
  - Added gap type priority weights (Thagard)
  - Made epsilon-greedy ADAPTIVE based on search success (Simon)

**Panels P-S3-A through P-S3-E**: Sprint 3.0 Decisions
- 27 decisions reviewed across 10 modules
- Panelists: Amodei, Liang, Kleinberg, Higgins, Cartwright, Mayo, Munzner, van Fraassen
- Key implementations:
  - Level-dependent credence thresholds (Cartwright)
  - Effective credence accounting for uncertainty (Mayo)
  - Closure type quantification (Pearl)

See: `docs/PANEL_CONSULTATION_P-VOI_2026-02-09.md`
See: `docs/PANEL_CONSULTATION_SPRINT_3.0_CONSOLIDATED_2026-02-09.md`

---

## Pending: Article Discovery + PDF Retrieval Monitoring

**Added**: 2026-02-09
**Priority**: P1
**Context**: VOI gaps are predictions about where articles *should* exist. We need to track the full discovery funnel: gap identification → article search → PDF retrieval → successful ingestion. This closes the loop between what the system predicts it needs and what it actually acquires.

### Problem Statement

1. VOI search identifies high-value gaps in the web of belief
2. These gaps predict topics/questions where articles *should* exist
3. Article Finder searches for articles matching these gaps
4. PDF retrieval may succeed or fail (paywalls, missing files, format issues)
5. Ingestion may succeed or fail (corrupt PDFs, extraction errors)
6. **Currently no tracking of this funnel** — we don't know our success rate

### Design Goals

1. **Gap-to-Article Mapping**: Track which gaps led to which article searches
2. **Search Effectiveness**: Did searches find relevant articles?
3. **PDF Acquisition Rate**: What % of identified articles yield usable PDFs?
4. **Ingestion Success Rate**: What % of PDFs successfully enter the pipeline?
5. **Gap Closure Rate**: Did the acquired articles actually address the gaps?

### Proposed Architecture

```
VOI Gap Identification
    │
    ├── gap_id, topic, predicted_value, search_terms
    │
    ▼
Article Search Execution
    │
    ├── search_id, gap_id, query, source (Scholar, Semantic Scholar, etc.)
    ├── n_results, relevance_scores
    │
    ▼
PDF Retrieval Attempts
    │
    ├── article_id, retrieval_method (direct, Sci-Hub, library, request)
    ├── status (success, paywall, not_found, timeout, format_error)
    │
    ▼
Pipeline Ingestion
    │
    ├── paper_id, extraction_status, n_claims, n_rules
    ├── gap_addressed (did this paper reduce the gap VOI?)
    │
    ▼
Funnel Metrics Dashboard
    │
    └── Success rates at each stage, bottleneck identification
```

### Tasks

| ID | Task | Estimate | Status | Dependencies |
|----|------|----------|--------|--------------|
| DISC-1 | Design discovery_funnel schema (SQLite tables) | 2h | ✓ DONE | — |
| DISC-2 | Add gap tracking to VOI search output | 2h | ✓ DONE | DISC-1 ✓ |
| DISC-3 | Add search execution logging | 3h | ☐ TODO | Article Finder |
| DISC-4 | Add PDF retrieval tracking with failure categorization | 3h | ☐ TODO | — |
| DISC-5 | Add ingestion success/failure tracking | 2h | ☐ TODO | pipeline.py |
| DISC-6 | Compute gap closure rate (VOI before/after) | 3h | ☐ TODO | DISC-2 ✓, DISC-5 |
| DISC-7 | Build funnel metrics API endpoints | 3h | ☐ TODO | DISC-1 through DISC-6 |
| DISC-8 | Build funnel dashboard (Streamlit) | 4h | ☐ TODO | DISC-7 |
| DISC-9 | Add alerts for low success rates | 2h | ☐ TODO | DISC-7 |
| DISC-10 | Generate 30-40 CNFA benchmark questions | 4h | ☐ DEFERRED | Populated corpus |
| DISC-11 | Batch PDF ingestion wrapper | 3h | ☐ TODO | — |
| DISC-12 | Abstract-based web bootstrapping (sketch → refine) | 4h | ☐ TODO | DISC-11 |

### DISC-11: Batch PDF Ingestion Wrapper

**Added**: 2026-02-11
**Status**: TODO
**Priority**: P1 (enables corpus building)

**Purpose**: Enable "point at a PDF folder and go" ingestion. Currently the pipeline expects a structured input directory with `paper.json` metadata. This wrapper automates the setup.

**Proposed Implementation**:
```python
# scripts/batch_ingest.py

def batch_ingest(
    pdf_dir: Path,
    output_dir: Path,
    bibtex_file: Optional[Path] = None,
    use_semantic_scholar: bool = True,
    parallel: int = 4
):
    """
    Batch ingest all PDFs in a directory.

    1. For each PDF:
       a. Try to match with BibTeX entry (by filename, DOI, title)
       b. If no BibTeX, query Semantic Scholar by title (from PDF first page)
       c. If no metadata found, extract from PDF header
       d. Create paper.json
       e. Call run_pipeline()
       f. Track success/failure (DISC-5 integration)

    2. Generate ingestion report:
       - Success/failure counts
       - Papers needing manual metadata
       - Duplicate detection
    """
```

**Components to Wire**:
- `app/pdf_ingest.py:extract_pdf_text()` — Already exists
- `src/services/bibtex_ingestion.py` — Already exists (BIB-1-7)
- `app/tasks/pipeline.py:run_pipeline()` — Already exists
- Semantic Scholar API — Free, 100 RPS with key

**CLI Interface**:
```bash
./bin/batch_ingest --pdf-dir ./corpus/pdfs --bibtex ./corpus/references.bib --out ./output
```

---

### DISC-12: Abstract-Based Web Bootstrapping (Sketch → Refine)

**Added**: 2026-02-11
**Status**: TODO
**Priority**: P1 (enables rapid prototyping)
**Philosophy**: Foundherentist — beliefs are revisable as better evidence arrives

**Purpose**: Bootstrap the Web of Belief quickly using abstracts and metadata, then incrementally refine with gold-standard full-text extraction. This creates a "sketch" of the knowledge graph that improves over time.

**Strategy**:
```
Phase 1: SKETCH (fast, imperfect)
├── Input: Abstracts + BibTeX metadata
├── Method: LLM extraction with relaxed confidence
├── Output: Candidate beliefs with source_depth=ABSTRACT
├── Credence: Lower (0.4-0.6), higher uncertainty (0.3)
└── Goal: Coverage over precision

Phase 2: REFINE (incremental, gold-standard)
├── Input: Full PDF text
├── Method: Full extraction pipeline
├── Output: Gold-standard beliefs with source_depth=FULL_TEXT
├── Action: Replace/merge with sketch beliefs
└── Goal: Precision over coverage
```

**Key Design Decisions**:

| Decision | Choice | Rationale |
|----------|--------|-----------|
| D1: Mark sketch beliefs | `source_depth=ABSTRACT`, `is_sketch=True` | Cartwright: track provenance |
| D2: Sketch credence | 0.5 ± 0.3 (high uncertainty) | Simon: satisfice early, refine later |
| D3: Replacement strategy | Merge if consistent, replace if contradictory | Quine: revise at periphery |
| D4: Preserve sketch history | Keep original as constraint source | Haack: track epistemic journey |

**Implementation**:
```python
# src/services/sketch_extractor.py

class SketchExtractor:
    """Extract candidate beliefs from abstracts using LLM."""

    def extract_from_abstract(
        self,
        abstract: str,
        metadata: PaperMetadata
    ) -> List[SketchBelief]:
        """
        Use LLM to extract candidate beliefs from abstract.

        Prompt focuses on:
        - Main finding (effect direction, rough magnitude)
        - Population/setting
        - Theory referenced (ART, SRT, etc.)
        - Methodology type

        Returns beliefs marked as sketch with high uncertainty.
        """

    def refine_with_full_text(
        self,
        sketch_beliefs: List[SketchBelief],
        full_extraction: ExtractionResult
    ) -> List[Belief]:
        """
        Replace/merge sketch beliefs with gold-standard extraction.

        - If gold confirms sketch: increase credence, reduce uncertainty
        - If gold contradicts sketch: replace with gold
        - If gold adds new: add alongside sketch
        - Keep sketch as historical constraint
        """
```

**Benefits**:
1. **Faster time-to-value**: Get a working web in hours, not weeks
2. **VOI search enabled early**: Identify gaps before full corpus processing
3. **DISC-10 unblocked**: Can generate benchmark questions against sketch
4. **Gradual quality improvement**: Each PDF processed improves the web
5. **Explicit uncertainty**: Users see which beliefs are sketches vs gold

**Metrics**:
| Metric | Formula | Target |
|--------|---------|--------|
| Sketch Coverage | sketched_papers / total_papers | 100% |
| Refinement Rate | refined_beliefs / sketch_beliefs | Increasing over time |
| Sketch→Gold Agreement | gold_confirms_sketch / refined_beliefs | > 70% |

---

### DISC-10: CNFA Benchmark Questions

**Added**: 2026-02-11
**Status**: DEFERRED — Waiting for populated PDF corpus
**Dependency**: Web of Belief must have sufficient ingested papers (target: 50+ papers)

**Purpose**: Generate 30-40 research questions grounded in actual CNfA literature to:
1. Benchmark query engine accuracy against known answers
2. Seed Streamlit UI with realistic user questions
3. Drive VOI-based gap identification with validated queries
4. Test reasoning system on our own corpus (not external RAG tools)

**Question Categories** (proposed):
| Category | Count | Example |
|----------|-------|---------|
| Mechanism | 8 | "What physiological mechanisms explain stress reduction from nature views?" |
| Effect size | 8 | "How large is the effect of indoor plants on workplace productivity?" |
| Boundary/scope | 6 | "Does biophilic design work differently for children vs adults?" |
| Controversy/gap | 6 | "What methodological concerns exist in ART research?" |
| Design implication | 6 | "What evidence supports specific plant densities for offices?" |
| Theory comparison | 4 | "How do ART and SRT predictions differ for urban parks?" |

**Output Format**: `data/cnfa_benchmark_questions.yaml` with:
- Question text, category, related theories, difficulty level
- Expected answer type (quantitative, qualitative, list)
- Search terms for VOI integration

**API Note**: External tools (Elicit, Consensus, Scite, Semantic Scholar) have APIs available but we intentionally defer to build internal reasoning capability first.

### Key Metrics to Track

| Metric | Formula | Target |
|--------|---------|--------|
| Search Hit Rate | articles_found / gaps_searched | > 80% |
| PDF Acquisition Rate | pdfs_obtained / articles_identified | > 60% |
| Ingestion Success Rate | papers_ingested / pdfs_obtained | > 90% |
| Gap Closure Rate | gaps_with_reduced_voi / gaps_addressed | > 50% |
| End-to-End Rate | gaps_closed / gaps_searched | > 25% |

### Failure Categories (DISC-4)

| Category | Description | Mitigation |
|----------|-------------|------------|
| PAYWALL | Article behind paywall | Try Sci-Hub, library access, author request |
| NOT_FOUND | PDF doesn't exist at URL | Try alternate sources |
| FORMAT_ERROR | PDF corrupted or non-standard | Manual download, OCR |
| TIMEOUT | Retrieval timed out | Retry with backoff |
| RATE_LIMITED | Source rate limiting | Queue with delays |
| ACCESS_DENIED | IP blocked or auth required | Rotate sources |

### Panel Consultation Recommended

For DISC-1 schema design, consult:
- **Bates** (information seeking behavior)
- **Kleinberg** (network flow, funnel analysis)
- **Simon** (satisficing in search)
- **Pearl** (causal attribution of success/failure)

---

## Pending: VOI Discovery & PDF Retrieval Infrastructure

**Added**: 2026-02-11
**Priority**: P0 (Blocking DISC-3 through DISC-9)
**Context**: Assessment of 2026-02-11 revealed that while VOI gap detection is 95% complete, the infrastructure to actually find and retrieve papers is critically incomplete. The system can identify what it needs but cannot acquire it.

### Problem Statement

1. **VOI search generates queries but doesn't execute them** — `voi_search.py` (1880 lines) identifies gaps and generates search terms, but no orchestrator calls external APIs
2. **Only Semantic Scholar stub exists** — 31 lines of code, no relevance scoring, deduplication, or multi-source coordination
3. **Zero PDF retrieval methods implemented** — Discovery funnel defines 6 methods (DIRECT_LINK, UNPAYWALL, SCIHUB, LIBRARY, AUTHOR_REQUEST, MANUAL) but none are coded
4. **Zotero is filesystem-only** — Can list PDFs in `~/Zotero/storage` but cannot query `zotero.sqlite` for metadata (titles, DOIs, tags)
5. **PDF sectioning is fragile** — Regex-based heuristics fail on non-standard paper formats

### Current State Summary

| Component | Lines of Code | Completeness | Notes |
|-----------|---------------|--------------|-------|
| Gap Detection (`voi_search.py`) | 1880 | 95% | Works well |
| Query Generation | ~200 | 85% | Cross-field vocab expansion done |
| Search Execution | 0 | 0% | **MISSING** |
| Semantic Scholar API | 31 | 10% | Stub only |
| PubMed/ERIC/CrossRef APIs | 0 | 0% | **NOT STARTED** |
| Unpaywall Integration | 0 | 0% | **NOT STARTED** |
| Sci-Hub Integration | 0 | 0% | **NOT STARTED** |
| Library Proxy Support | 0 | 0% | **NOT STARTED** |
| Zotero Metadata Access | 0 | 0% | **NOT STARTED** |
| PDF Sectioning | ~100 | 40% | Fragile regex |

### Tasks

| ID | Task | Description | Priority | Dependencies |
|----|------|-------------|----------|--------------|
| INFRA-1 | Implement VOI search executor | Orchestrator that takes gap → queries → calls APIs → returns ranked results | P0 | — |
| INFRA-2 | Extend Semantic Scholar integration | Add relevance scoring, deduplication, pagination, rate limiting | P1 | INFRA-1 |
| INFRA-3 | Add Unpaywall API integration | DOI → open access PDF URL resolution | P1 | — |
| INFRA-4 | Add CrossRef API integration | DOI validation, metadata enrichment, reference extraction | P2 | — |
| INFRA-5 | Add PubMed API integration | Biomedical literature search via E-utilities | P2 | INFRA-1 |
| INFRA-6 | Add ERIC API integration | Education literature search | P3 | INFRA-1 |
| INFRA-7 | Implement PDF direct download | Fetch PDFs from publisher URLs, handle redirects | P1 | — |
| INFRA-8 | Implement Unpaywall PDF retrieval | Use INFRA-3 to get OA links, download PDFs | P1 | INFRA-3 |
| INFRA-9 | Implement library proxy support | Route requests through institutional proxy (CalTech, etc.) | P2 | — |
| INFRA-10 | Add Zotero database access | Query `zotero.sqlite` for metadata (DOIs, titles, tags, collections) | P1 | — |
| INFRA-11 | Add Zotero sync capability | Bi-directional: import Zotero metadata, export AE findings | P3 | INFRA-10 |
| INFRA-12 | Improve PDF sectioning | Replace regex with SciSpacy or BERT-based section classification | P2 | — |
| INFRA-13 | Add OCR support | Handle scanned/image-based PDFs via Tesseract or similar | P3 | — |
| INFRA-14 | Multi-source search coordinator | Parallel queries across sources, deduplication, relevance fusion | P1 | INFRA-1, INFRA-2, INFRA-5 |
| INFRA-15 | Citation network traversal | Given paper, find citing/cited papers for gap closure | P2 | INFRA-2, INFRA-4 |

### Implementation Order (Recommended)

**Phase 1: Core Search (Unblocks DISC-3)**
1. INFRA-1 (VOI search executor)
2. INFRA-2 (Semantic Scholar extension)
3. INFRA-14 (Multi-source coordinator - basic version)

**Phase 2: PDF Acquisition (Unblocks DISC-4)**
4. INFRA-3 (Unpaywall API)
5. INFRA-7 (Direct download)
6. INFRA-8 (Unpaywall retrieval)
7. INFRA-10 (Zotero database access)

**Phase 3: Extended Sources**
8. INFRA-4 (CrossRef)
9. INFRA-5 (PubMed)
10. INFRA-9 (Library proxy)

**Phase 4: Quality Improvements**
11. INFRA-12 (Better PDF sectioning)
12. INFRA-15 (Citation traversal)
13. INFRA-6 (ERIC)
14. INFRA-11 (Zotero sync)
15. INFRA-13 (OCR)

### API Keys & Configuration Required

| Service | Env Variable | Status |
|---------|--------------|--------|
| Semantic Scholar | `SEMANTIC_SCHOLAR_API_KEY` | ✓ Configured |
| Unpaywall | `UNPAYWALL_EMAIL` | ☐ Need to add |
| CrossRef | `CROSSREF_MAILTO` | ☐ Need to add (polite pool) |
| PubMed | `NCBI_API_KEY` | ☐ Optional (higher rate limits) |
| ERIC | — | ☐ Free, no key needed |

### Panel Consultation Recommended

For INFRA-1 and INFRA-14 (search orchestration), consult:
- **Bates** (berrypicking, information foraging)
- **Simon** (satisficing, bounded rationality in search)
- **Pearl** (relevance as causal contribution to gap closure)
- **Cartwright** (source reliability, evidence quality)

---

## Completed: Entrenchment Historical Replay + Monitor

**Added**: 2026-02-09
**Completed**: 2026-02-09
**Context**: Distinguish entrenchment history inside the system (ingestion-time) vs scholarly history (publication-time). Admins can replay the web in true historical order and see how entrenchment evolves.

### Completed Tasks

| ID | Task | Completed | Outcome |
|----|------|-----------|---------|
| RULES-1 | Convert 31 findings to ae.rule.v2 format | 2026-02-11 | Created `scripts/convert_findings_to_rules.py`, output to `data/rules.jsonl` (31 rules) |
| ENT-1 | Add publication_year/date to paper model | 2026-02-09 | Already in schema + DB (`paper_publication` table) |
| ENT-2 | Build scholarly-time replay pipeline | 2026-02-09 | `src/services/entrenchment_replay.py` - Fixed attribute naming conflict |
| ENT-3 | Store entrenchment snapshots for both timelines | 2026-02-09 | Added query methods to `web_persistence.py`: `get_entrenchment_history()`, `get_entrenchment_events()`, `get_latest_entrenchment()`, `compare_timeline_entrenchment()`, `get_entrenchment_trajectory()` |
| ENT-4 | Admin monitor UI: dual timeline | 2026-02-09 | Created `frontend/entrenchment-monitor.html` + `app/routes/entrenchment.py` API endpoints |
| ENT-5 | Health metrics: volatility, stagnation | 2026-02-09 | Health metrics in entrenchment API: volatility, stagnation count, timeline divergence, conflict load |

### Follow-up Tasks (Phase 2)

**Context**: Replay should not mutate the live master web. Provide a safe runner that copies the DB and runs scholarly replay against the copy by default.

| ID | Task | Status |
|----|------|--------|
| ENT-6 | Decide replay DB strategy + add runner that copies live DB (no mutation) | ✓ COMPLETE (2026-02-17) |

### Tests
- `tests/test_entrenchment_tracker.py`: 16 tests covering paper publication, replay pipeline, snapshots, health metrics
- `tests/test_entrenchment_replay_safe.py`: 3 tests covering safe DB copy strategy, master-filtered loader, and runner execution against copied DB

---

## Pending: AF-AE BibTeX Integration

**Added**: 2026-02-08
**Context**: Article Finder accepts user-uploaded PDFs that lack BibTeX metadata. Without metadata (title, authors, abstract, DOI, year), Article Eater cannot properly extract rules or track provenance.

### Problem Statement

1. AF hunts articles (has metadata) but also accepts direct PDF uploads (no metadata)
2. User has Zotero library with BibTeX export capability
3. Need to link uploaded PDFs to their BibTeX records
4. Need this metadata for AE rule extraction and provenance tracking

### Design Options

| Option | Where | Approach | Pros | Cons |
|--------|-------|----------|------|------|
| **A. AF Upload Enhancement** | Article Finder | Add BibTeX upload alongside PDF, match by filename or user selection | Clean separation, metadata lives with source | Requires AF changes |
| **B. AE Metadata Augmentation** | Article Eater | Accept BibTeX bundle in input_bundle, enrich paper.json | AE already handles bundles | Metadata should live upstream |
| **C. Zotero Connector** | New service | Watch Zotero export folder, auto-match PDFs by hash/filename | Automated, works with existing workflow | New service to maintain |
| **D. Manual Linking UI** | AF or Streamlit | Upload BibTeX, show unlinked PDFs, user manually matches | Handles edge cases | Manual work |

### Recommended Approach: Hybrid A + D

1. **AF Enhancement**: Add optional BibTeX upload with PDF
   - Parse BibTeX, extract fields for `paper.json`
   - Fields needed: `title`, `authors`, `abstract`, `year`, `doi`, `journal`, `volume`, `pages`

2. **Bulk Zotero Import** (for existing library):
   - User exports Zotero collection as BibTeX
   - AF/Streamlit UI shows unlinked PDFs and BibTeX entries
   - User matches them (or auto-match by title similarity)
   - Matched entries create proper `paper.json` metadata

3. **AE Contract Update**:
   - `paper.json` already has fields for this
   - Ensure `abstract` is used for extraction when fulltext unavailable
   - Add `bibtex_source` field to provenance

### Tasks

| ID | Task | Estimate | Status |
|----|------|----------|--------|
| BIB-1 | Design paper.json schema extensions for BibTeX fields | 1h | ✓ DONE (included in BIB-2) |
| BIB-2 | Add BibTeX parser utility | 2h | ✓ DONE |
| BIB-3 | AF: Add BibTeX upload option alongside PDF | 3h | ✓ DONE |
| BIB-4 | AF: Create bulk Zotero import UI | 4h | ✓ DONE (Streamlit page) |
| BIB-5 | Auto-match algorithm (title similarity, DOI, filename) | 3h | ✓ DONE |
| BIB-6 | AE: Ensure abstract extraction works when fulltext missing | 2h | ✓ DONE |
| BIB-7 | Ingest matched PDFs into AE pipeline | 3h | ✓ DONE |

---

## Pending: Extraction Tables (16 Types)

**Added**: 2026-02-08 (from WHERE_WE_STAND.md #12)
**Source**: `/Users/davidusa/REPOS/Outcome_Contractor/article_finder/exemplary_extraction_tables.md`
**Context**: Each article type needs complete field specs, rule mappings, validation rules, and AI prompts.

### Status: 16/16 Complete ✅

| # | Article Type | Status | Notes |
|---|--------------|--------|-------|
| 1 | Randomized Experiment | ✅ Complete | Full spec 2026-02-03 |
| 2 | Quasi-Experiment | ✅ Complete | Full spec 2026-02-03 |
| 3 | Cross-Sectional Survey | ✅ Complete | Full spec 2026-02-03 |
| 4 | Longitudinal Study | ✅ Complete | Full spec 2026-02-08 (panel additions) |
| 5 | Observational Field Study | ✅ Complete | Full spec 2026-02-09 |
| 6 | Phenomenological Study | ✅ Complete | Full spec 2026-02-09 (qualitative) |
| 7 | Ethnographic Study | ✅ Complete | Full spec 2026-02-09 (qualitative) |
| 8 | Grounded Theory Study | ✅ Complete | Full spec 2026-02-09 (qualitative) |
| 9 | Case Study | ✅ Complete | Full spec 2026-02-09 |
| 10 | Interview Study | ✅ Complete | Full spec 2026-02-09 (qualitative) |
| 11 | Mixed Methods | ✅ Complete | Full spec 2026-02-09 |
| 12 | Meta-Analysis | ✅ Complete | Full spec 2026-02-08 (panel additions) |
| 13 | Systematic Review | ✅ Complete | v1.1 2026-02-09 (panel additions) |
| 14 | Narrative Review | ✅ Complete | Full spec 2026-02-09 |
| 15 | Theoretical | ✅ Complete | Full spec 2026-02-09 |
| 16 | Thought Piece | ✅ Complete | Full spec 2026-02-09 |

### Next Priority
1. Complete Systematic Review (similar structure to Meta-Analysis)
2. Complete remaining synthesis types (Narrative Review)
3. Complete qualitative types (starting with Case Study)

### Each Type Needs
1. Complete field list (required/optional)
2. Mapping to rule types (which fields → which rules)
3. Validation rules (what makes extraction adequate)
4. AI prompt specifications
5. Edge cases (missing data, ambiguous findings)

### Panel Consultation Completed: 2026-02-08

**Panelists**: Walton (argumentation), Pearl (causation), Cartwright (philosophy of science), Lipton (explanation), Hearst (NLP extraction), Teufel (scientific discourse), R. Kaplan (domain)

**Document**: `/Users/davidusa/REPOS/Outcome_Contractor/docs/PANEL_CONSULTATION_EXTRACTION_TABLES_2026_02_08.md`

**Key Additions from Panel**:

| Addition | Source | Priority |
|----------|--------|----------|
| New rule types: REBUTTAL, PRESUMPTION, ASSOCIATION, CONTRAST | Walton, Pearl, Lipton | High |
| `causal_level` (association/intervention/counterfactual) | Pearl | High |
| `argument_scheme` + `critical_questions[]` | Walton | High |
| `contrast_class` + `difference_maker` | Lipton | High |
| `enabling_conditions[]` + `bridge_type` | Cartwright | Medium |
| `extraction_difficulty` + `source_zone` per field | Hearst, Teufel | Medium |
| Domain features (ART, Appleton, etc.) | Kaplan | High for CNfA |
| Stimulus documentation template | All | High |

**Immediate Action Items**:
- [x] Add new rule types to schema — DONE 2026-02-09 (ae.rule.v2.schema.json, ae.claim.v2.schema.json)
- [x] Add argument_schemes vocabulary — DONE 2026-02-09 (contracts/vocab/argument_schemes.json)
- [x] Update RCT/Quasi-Exp/Cross-Sectional with panel additions — DONE 2026-02-09 (EXTRACTION_TEMPLATE_PANEL_ADDITIONS_2026_02_09.md)
- [x] Create stimulus documentation template with domain features — DONE 2026-02-09 (STIMULUS_DOCUMENTATION_TEMPLATE_2026_02_09.md)
- [x] Complete Longitudinal Study spec (high causal value per Pearl) — DONE 2026-02-08
- [x] Complete Meta-Analysis spec (high synthesis value) — DONE 2026-02-08

---

## Pending: Extracted Tables Database (PDF Tables)

**Added**: 2026-02-08
**Context**: Track tables extracted from PDFs (results tables, demographics, etc.)

| ID | Task | Status |
|----|------|--------|
| TBL-1 | Add `extracted_tables` schema to AF database | ✓ DONE |
| TBL-2 | Add CRUD methods to Database class | ✓ DONE |
| TBL-3 | Add table extraction code (AI/API primary, pdfplumber fallback) | ✓ DONE |
| TBL-4 | Integrate with AE claim extraction | ✓ DONE |
| TBL-5 | Add table review UI | ✓ DONE |
| TBL-6 | Tiered model extraction (Haiku→Sonnet for complex fields) | ☐ TODO |
| TBL-7 | Model comparison benchmark (multi-provider + Codex) | ☐ TODO |

### TBL-6: Tiered Model Table Extraction

**Added**: 2026-02-11
**Status**: TODO
**Priority**: P2 (quality improvement)
**Pattern**: Mirrors 3.0.2-E (Haiku for parsing, Sonnet for synthesis)

**Purpose**: Use cheaper/faster models for simple fields, smarter models for complex interpretation. Optimizes cost while improving quality on nuanced extractions.

**Two-Pass Architecture**:
```
Pass 1: STRUCTURE (Haiku - $0.005/table)
├── Detect table boundaries and headers
├── Extract simple fields: citation, N, year, country, study type
├── Flag complex cells needing interpretation
└── Output: Partially filled table + complexity flags

Pass 2: INTERPRET (Sonnet - only flagged cells)
├── Effect size interpretation: magnitude + clinical significance
├── Confidence interval: precision assessment
├── Quality assessment: structured RoB domains
├── Methodology notes: standardized categories
└── Output: Complete table with nuanced interpretations
```

**Field Classification**:
| Complexity | Fields | Model | Cost |
|------------|--------|-------|------|
| Simple | Citation, N, Year, Country | Haiku | $0.001 |
| Semi-structured | Study design, Setting, Population | Haiku | $0.002 |
| Complex | Effect size meaning, CI interpretation, Quality judgment | Sonnet | $0.01 |
| Ambiguous | Conflicting results, Non-standard stats | Opus | $0.05 |

**Implementation**:
```python
# src/services/table_extractor.py - extend with:

class TieredTableExtractor(TableExtractorBase):
    """Two-pass extraction: Haiku for structure, Sonnet for interpretation."""

    def __init__(
        self,
        api_client,
        structure_model: str = "claude-3-haiku-20240307",
        interpret_model: str = "claude-sonnet-4-20250514"
    ):
        self.structure_extractor = AITableExtractor(api_client, structure_model)
        self.interpret_extractor = AITableExtractor(api_client, interpret_model)
```

**When to Use**:
- ✅ Results tables (effect sizes, CIs, p-values)
- ✅ Quality assessment tables (RoB judgments)
- ✅ Complex methodology tables
- ❌ Demographics tables (mostly numbers)
- ❌ Simple characteristics tables

**Cost Projection**:
| Table Type | Haiku Only | Tiered | Quality Gain |
|------------|-----------|--------|--------------|
| Demographics | $0.005 | $0.005 | None |
| Study characteristics | $0.005 | $0.006 | Low |
| Results | $0.005 | $0.015 | High |
| Quality assessment | $0.005 | $0.020 | High |

### TBL-7: Model Comparison Benchmark (Multi-Provider + Codex)

**Added**: 2026-02-11
**Status**: TODO
**Priority**: P1 (must complete before TBL-6 implementation)
**Dependency**: TBL-6 should wait for TBL-7 validation results

**Purpose**: Establish gold standard benchmark for table extraction quality across AI providers. Determine whether cheaper models produce equivalent results, identify divergence patterns, and develop optimized prompts.

**Core Question**: Do Haiku/GPT-4-mini/Gemini Flash produce extraction quality comparable to Sonnet/Opus, or do we need the tiered approach from TBL-6?

**AI Providers to Test**:
| Provider | Models | Cost Tier | Notes |
|----------|--------|-----------|-------|
| **Anthropic** | claude-3-haiku, claude-sonnet-4, claude-opus-4 | Low/Med/High | Primary |
| **OpenAI** | gpt-4o-mini, gpt-4o, gpt-4-turbo | Low/Med/High | Comparison |
| **Google** | gemini-1.5-flash, gemini-1.5-pro | Low/High | Comparison |
| **Codex** | codex-mini, codex-standard | Med | When user running via Codex |

**Codex Support**: The benchmark must detect when running inside Codex and allow the current Codex model to be tested alongside API-based models. This enables real-time comparison without API costs.

**Gold Standard Test Set**:
1. **Curate 20 representative tables** from diverse papers:
   - 5 demographics tables (simple)
   - 5 study characteristics tables (semi-structured)
   - 5 results tables with effect sizes (complex)
   - 5 quality assessment tables (complex)

2. **Create human-verified ground truth** for each table:
   - Correct field values
   - Edge case annotations
   - Ambiguity notes

3. **Store in**: `gold_standard/table_extraction/v1.0/`

**Evaluation Metrics**:
| Metric | Weight | Description |
|--------|--------|-------------|
| **Field-level accuracy** | 40% | Exact match for simple fields |
| **Semantic accuracy** | 30% | Meaning-equivalent for interpreted fields |
| **Structural accuracy** | 20% | Row/column alignment |
| **Edge case handling** | 10% | Missing data, unusual formats |

**Benchmark Script**:
```python
# scripts/table_extraction_benchmark.py

class TableExtractionBenchmark:
    """Multi-provider table extraction benchmark."""

    def __init__(self, gold_standard_dir: str):
        self.gold_standard = self._load_gold_standard(gold_standard_dir)
        self.results = {}

    def detect_codex_environment(self) -> bool:
        """Detect if running inside Codex."""
        return os.environ.get("CODEX_MODEL") is not None

    def register_providers(self):
        """Register available AI providers."""
        providers = {
            "anthropic": ["haiku", "sonnet", "opus"],
            "openai": ["gpt-4o-mini", "gpt-4o"],
            "google": ["gemini-1.5-flash", "gemini-1.5-pro"],
        }
        if self.detect_codex_environment():
            providers["codex"] = ["current"]
        return providers

    def run_benchmark(self, provider: str, model: str, table: Table) -> ExtractionResult:
        """Extract table with specified provider/model."""
        pass

    def score_extraction(self, result: ExtractionResult, ground_truth: Table) -> Score:
        """Score extraction against ground truth."""
        pass

    def generate_report(self) -> BenchmarkReport:
        """Generate comparison report across all providers."""
        pass
```

**Expected Outputs**:
1. **Accuracy matrix** — Provider × Table Type × Model Tier
2. **Divergence report** — Where models disagree and why
3. **Cost-quality tradeoff** — Pareto frontier visualization
4. **Prompt optimization notes** — What works better for which model
5. **Recommendation** — Whether TBL-6 tiered approach is justified

**Implementation Steps**:
1. Create gold standard table corpus (20 tables)
2. Build benchmark harness with provider abstraction
3. Add Codex detection and passthrough
4. Run initial benchmark across all providers
5. Analyze divergence patterns
6. Document prompt engineering findings
7. Generate cost-quality recommendation for TBL-6

**Success Criteria**:
- [ ] 20 gold standard tables with ground truth
- [ ] Benchmark runs on all listed providers
- [ ] Codex passthrough works when in Codex environment
- [ ] Report identifies model tiers with statistically significant quality differences
- [ ] Clear recommendation for TBL-6 implementation

---

**TBL-3 Completion (2026-02-08)**:
- Created `src/services/table_extractor.py` (~750 lines)
- `AITableExtractor`: LLM-based extraction with structured prompts for 4 table types
  - STUDY_CHARACTERISTICS, RESULTS, QUALITY_ASSESSMENT, DEMOGRAPHICS
- `PdfPlumberTableExtractor`: Geometric extraction fallback
- `HybridTableExtractor`: Combines AI + pdfplumber
- `ExtractedTable` dataclass with to_dict(), to_markdown() methods
- Conversion functions: `extracted_table_to_article_metadata()`, `extracted_table_to_rct_facts()`
- Factory function: `get_table_extractor(method, api_client, model)`
- 46 tests in `tests/test_table_extractor.py`

**TBL-4 Completion (2026-02-09)**:
- Created `src/services/table_to_claims.py` (~480 lines)
  - `TableClaim`: Claim dataclass for table-derived claims
  - `TableClaimGenerator`: Converts tables to claims by type
  - `PipelineTableIntegrator`: Integrates with pipeline
  - `extract_tables_for_pipeline()`: Convenience function
  - Export functions for tables.jsonl
- Integrated into `app/tasks/pipeline.py`:
  - Table extraction after BN export, before web integration
  - Claim merging with deduplication
  - Added to result dict: `n_tables`, `n_table_claims`
  - Added artifact: `tables_jsonl`

**TBL-5 Completion (2026-02-09)**:
- Added table review section to `scripts/ae_streamlit_control_room.py`
  - Output directory browser for tables.jsonl files
  - Table selector with metadata display
  - DataFrame visualization of table content
  - Raw JSON view in expander
  - Table-derived claims display from claims.jsonl

**BIB-2 Completion (2026-02-08)**:
- Created `src/services/bibtex_utils.py` (~700 lines, no external deps)
- `BibTeXParser`: Full BibTeX parsing with nested braces, LaTeX cleanup
- `BibTeXEntry`: Data class with `to_paper_json()` conversion
- `PDFBibTeXMatcher`: Multi-strategy matching (DOI, arXiv, title, author-year)
- `normalize_text()`, `title_similarity()`: Fuzzy matching utilities
- Created `streamlit_app/pages/1_bibtex_import.py` (~450 lines)
  - Upload BibTeX and PDFs
  - Auto-match with confidence scores
  - Manual linking for unmatched items
  - Export as paper.json bundles, match reports, or CSV
- 41 tests in `tests/test_bibtex_utils.py`

**BIB-6 Completion (2026-02-09)**:
- Added abstract fallback to `app/tasks/pipeline.py` (lines 1223-1242)
  - When PDF extraction fails or yields < 100 chars, tries paper.json abstract
  - Logs fallback usage with audit event
- Updated `contracts/ae_af/schemas/ae.paper.v1.schema.json`
  - Added optional `abstract` field with description

**BIB-3 Completion (2026-02-09)**:
- Updated `app/routes/annotator.py` with BibTeX upload endpoints
  - `POST /upload-with-bibtex`: Upload PDF + optional BibTeX file or text
  - `POST /upload-bibtex-batch`: Upload BibTeX file to register multiple papers
- BibTeX metadata creates proper paper.json for AE pipeline
- Integrates with existing BibTeX parser from bibtex_utils.py
- PDF + metadata stored together, ready for ingestion

**BIB-7 Completion (2026-02-09)**:
- Created `src/services/bibtex_ingestion.py` (~350 lines)
  - `BibTeXIngestionService`: Ingests matched PDFs into AE pipeline
  - `_create_input_bundle()`: Creates paper.json + PDF bundles
  - Also writes abstract.txt as additional fallback
  - Batch processing with progress tracking
- Convenience functions: `ingest_matched_papers()`, `ingest_single_paper()`
- Updated `streamlit_app/pages/1_bibtex_import.py`
  - Added "Run Pipeline" section with output dir and profile selection
  - Direct ingestion from UI without export step
- 14 tests in `tests/test_bibtex_ingestion.py`

---

## Parallel Work Lanes

**Coordination files**: `ACTIVE_TASKS.md` (task claims) + `PARALLEL_WORK.md` (file ownership)

| Lane | Scope | Key Files | Status |
|------|-------|-----------|--------|
| **A** | Sprint 2.5 Schema Design | `social_epistemology.py` (new) | ✓ COMPLETE |
| **B** | Sprint 2.5 Implementation | `web_of_belief.py` extensions | ✓ COMPLETE |
| **C** | TODO 1: Credibility Testing | `credibility_testing.py`, `credibility_feedback.py` | ✓ COMPLETE |
| **D** | TODO 2: Interpretive Intelligence | `interpretive_intelligence.py` | ✓ COMPLETE |
| **E** | TODO 3: VOI Search | `voi_search.py` | ✓ COMPLETE |
| **F** | Panel Convening (P-TC, P-QW) | `docs/PANEL_*.md` | ✓ COMPLETE |
| **G** | Fix Failing Tests | `test_theory_system.py`, `rulegraph_v2_builder.py` | ✓ COMPLETE |
| **H** | Commit TD Work | TD-C, TD-D, TD-E files | AVAILABLE |
| **I** | Sprint 2.0 Pipeline Integration | `app/tasks/pipeline.py` | AVAILABLE |

**Recommended parallel pairs** (minimal conflicts):
- Lane A + Lane E (Schema + VOI)
- Lane C + Lane F (Credibility + Panels)
- Lane D + Lane E (Interpretive + VOI)

**Claim a lane**: Edit `PARALLEL_WORK.md` → Active Claims table

---

## Active Panels

Panels evaluate work during sprints. After evaluation: replan → patch code → continue.

### Panel Registry

| Panel ID | Name | Scope | Members | Status |
|----------|------|-------|---------|--------|
| P-EC | Epistemic-Causal Integration | `epistemic_causal_integration.py`, `epistemic_to_causal_bridges.py`, `web_of_belief.py` | Pearl, Quine, van Fraassen, Cartwright, Thagard, Longino | COMPLETE (Sprint 1.5) |
| P-QW | Quality-Weighted Entrenchment | `web_persistence.py`, `extraction_to_web.py` | Pearl, Cartwright, Simon, Bates, Kaplan, Mayo | ✓ CONSULTED (6 decisions) |
| P-SE | Social Epistemology | `social_epistemology.py` | Longino, Kitcher, Knorr Cetina, Collins, Kuhn | ✓ CONSULTED (5 questions) |
| P-TC | Task Context | `task_taxonomy.json`, claim schema | Klein, Ericsson, Kahneman, R. Kaplan, Simon, Suchman | ✓ CONSULTED (7 decisions) |
| P-TD | Technical Debt | `web_of_belief.py`, `extraction_to_web.py` | Thagard, Simon, Cartwright, Mayo, Bates, Pustejovsky, Manning, Kleinberg, Hearst | ✓ CONSULTED (4 items) |

### Panel Invocation Protocol

```
Sprint Work → Decision Accumulates → Threshold Met (≥5) OR Sprint Boundary
                                            ↓
                              Panel Consultation Triggered
                                            ↓
                    Panel Evaluates → Recommendations Generated
                                            ↓
                         Replan → Patch Code → Mark Resolved
                                            ↓
                                   Continue Sprint
```

---

## Sprint 1.5: Epistemic-Causal Integration

**Status**: IN PROGRESS (90% complete)
**Panel**: P-EC (Epistemic-Causal Integration)
**Source**: `/Users/davidusa/REPOS/research/claude_epist_layer adds K to causal BN/`

### Completed

| ID | Task | Completed | Outcome |
|----|------|-----------|---------|
| 1.5.1 | Core integration architecture | 2026-02-08 | `epistemic_causal_integration.py` (~800 lines) |
| 1.5.2 | Five epistemic-to-causal bridges | 2026-02-08 | `epistemic_to_causal_bridges.py` (~600 lines) |
| 1.5.3 | Panel concern resolutions | 2026-02-08 | `panel_concern_resolutions.py` (~500 lines) |
| 1.5.4 | Van Fraassen contrast class design | 2026-02-08 | `van_fraassen_contrast_class.md` |
| 1.5.5 | Expert panel: Quinean vs Pearl | 2026-02-08 | `expert_panel_quinean_vs_pearl.md` |
| 1.5.6 | Expert panel: Integration review | 2026-02-08 | `expert_panel_epistemic_causal_integration.md` |
| 1.5.7 | Expert panel: Synergies | 2026-02-08 | `expert_panel_synergies.md` |
| 1.5.8 | Sprint plan | 2026-02-08 | `__sprint_plan_v1.md` |

### In Progress

| ID | Task | Started | Notes |
|----|------|---------|-------|
| 1.6.1 | Inference type tagging | 2026-02-08 | Ready to start |

### Panel P-EC Complete (2026-02-08)

**Verdict**: SPRINT 1.5 APPROVED

**High-Priority Recommendations for Sprint 1.6**:
| ID | Recommendation | Source |
|----|----------------|--------|
| P-EC-R9 | Check `enabling_conditions` before counterfactuals | Cartwright |
| P-EC-R12 | Integrate `CoherenceCache` for scalability | Thagard |
| P-EC-R14 | Query-local coherence computation | Thagard |
| P-EC-R8 | "Contrast not transferable" warnings | van Fraassen |

**Full review**: `docs/PANEL_P-EC_SPRINT_1.5_REVIEW_2026_02_08.md`

### Recently Completed (Sprint 1.5 — ALL DONE)

| ID | Task | Completed | Outcome |
|----|------|-----------|---------|
| 1.5.11 | Documentation update | 2026-02-08 | Updated CLAUDE.md with Sprint 1.5 capabilities, architecture diagram, essential files |
| 1.5.10 | Wire into `web_of_belief.py` | 2026-02-08 | Added `create_causal_bridge()`, `counterfactual()`, `causal_bridge_available()` methods. 34 tests. |
| 1.5.9 | Integration tests for bridge | 2026-02-08 | 29 tests. Fixed `_get_theory_beliefs()` for `theory_id`/`theory_ids` compatibility |

### Panel Evaluation Required

After 1.5.9-1.5.11 complete → P-EC panel evaluates integration with existing `src/services/web_of_belief.py`

---

## Sprint 1.6: Quick Wins

**Status**: COMPLETE
**Panel**: P-EC (same panel evaluates)
**Completed**: February 8, 2026

### Completed

| ID | Task | Completed | Outcome |
|----|------|-----------|---------|
| 1.6.1 | Inference type tagging | 2026-02-08 | `InferenceType` enum (INDUCTIVE, DEDUCTIVE, ABDUCTIVE, MIXED, UNKNOWN) added to Belief |
| 1.6.2 | Belief type tagging | 2026-02-08 | `BeliefKind` enum (MECHANISTIC, EVIDENTIAL, THEORETICAL, METHODOLOGICAL, BRIDGE) added to Belief |
| 1.6.3 | Value computation | 2026-02-08 | `belief_centrality()`, `belief_sensitivity()`, `belief_value()`, `beliefs_by_value()`, `high_value_beliefs()` methods in WebOfBelief |
| 1.6.4 | Tension-resolving experiments | 2026-02-08 | `suggest_experiments()`, `get_research_priorities()` methods in WebOfBelief. 13 new tests. |

### P-EC Panel Recommendations Implemented

| ID | Recommendation | Status | Outcome |
|----|----------------|--------|---------|
| P-EC-R9 | Check `enabling_conditions` before counterfactuals | COMPLETE | `_check_enabling_conditions()`, `_track_blocked_belief()`, `get_blocked_beliefs()` added to EpistemicCausalBridge |

### Total Tests: 68 passing

### Panel Checkpoint

Sprint 1.6 complete → Ready for P-EC panel evaluation of tagging accuracy and value computation validity

---

## Sprint 2.5: Social Epistemology

**Status**: COMPLETE
**Panel**: P-SE (Social Epistemology) — CONSULTED (2026-02-08)
**Design Document**: `docs/SPRINT_2.5_DESIGN.md`
**Schema**: `contracts/schemas/social_epistemology.schema.json`
**Module**: `src/services/social_epistemology.py` (~1300 lines)
**Tests**: 54 passing

### Completed

| ID | Task | Completed | Outcome |
|----|------|-----------|---------|
| 2.5.1 | Design community schema | 2026-02-08 | Multi-criteria identification: theory (0.35), exemplars (0.25), methods (0.25), citations (0.15) |
| 2.5.2 | Design `EpistemicCommunity` class | 2026-02-08 | Full class design with metrics, hierarchy, history events |
| 2.5.3 | Design `BeliefProvenance` class | 2026-02-08 | Tracks origins, community credences, contestation |
| 2.5.4 | Implement `EpistemicCommunity` | 2026-02-08 | Vocabulary overlap, track record weighting, history events |
| 2.5.5 | Implement `BeliefProvenance` | 2026-02-08 | Community credences, contestation detection, aggregation (per SE-2) |
| 2.5.6 | Implement `ContestationTracker` | 2026-02-08 | Track disputes, experimenter's regress detection (Collins) |
| 2.5.7 | Implement `MethodologicalDiversityAssessor` | 2026-02-08 | Diversity index, vulnerability detection, diversification suggestions |
| 2.5.8 | Integrate with Belief class | 2026-02-08 | Added `provenance`, `community_associations`, `get_community_credence()`, `is_community_contested()` |
| 2.5.9 | Tests | 2026-02-08 | 54 tests covering all classes and integration |
| 2.5.10 | CommunityRegistry | 2026-02-08 | CRUD operations, vocabulary-based lookup, serialization |
| 2.5.11 | CNFA Seed Data | 2026-02-08 | ART, SRT, Biophilia, Environmental Psychology communities

### Panel Questions P-SE — RESOLVED (2026-02-08)

| Q# | Question | Decision | Rationale |
|----|----------|----------|-----------|
| SE-1 | How identify communities? | Multi-criteria: theory (0.35), exemplars (0.25), methods (0.25), citations (0.15) | Per Longino, Kuhn, Knorr Cetina |
| SE-2 | How aggregate disagreeing communities? | Report separately by default; average only for empirical, within-paradigm | Per Longino, Kuhn |
| SE-3 | How represent power asymmetries? | Track separately from credence; use domain-specific track record | Per Longino, Kitcher |
| SE-4 | Track historical changes? | Snapshot-based with event annotations | Per Kitcher, Collins |
| SE-5 | What granularity? | Three-tier hierarchy: Field > Paradigm > Lab | Per Longino, Knorr Cetina |

---

## Sprint 2.6: Panel Decision Implementation

**Status**: COMPLETE (2026-02-08)
**Panels**: P-TC (Task Context), P-QW (Quality-Weighted Entrenchment)
**Dependencies**: Sprint 2.5 complete ✓

### Track A: Task Context (P-TC Decisions) — ✓ COMPLETE

**Target Files**: `src/services/extraction_to_web.py`

| ID | Task | Source | Description | Status |
|----|------|--------|-------------|--------|
| 2.6.1 | Add `inference_basis` field | P-TC D1 | Track whether task context is stated/inferred/unknown | ✓ DONE |
| 2.6.2 | Add `review_recommended` flag | P-TC D3 | Flag claims with keyword inference confidence <0.7 | ✓ DONE |
| 2.6.3 | Add `presumed_lab` flag | P-TC D4 | Default `lab_task` with `presumed: true` when not stated | ✓ DONE |
| 2.6.4 | Add `effective_demand` calculation | P-TC D6 | Compute effective_demand = skill × cognitive_demand | ✓ DONE |
| 2.6.5 | Add `mechanism_only` tag | P-TC D7 | Tag pure psych/neuro papers without design implications | ✓ DONE |
| 2.6.6 | Helper functions | — | `extract_task_context()`, `compute_effective_demand()`, `is_mechanism_only()` | ✓ DONE |
| 2.6.7 | Integration with claim_to_belief | — | Sprint 2.6 fields set in mapping pipeline | ✓ DONE |

**New Classes/Functions**:
- `TaskContextResult` dataclass
- `extract_task_context(claim)` - instrument/keyword matching
- `compute_effective_demand(cognitive_demand, skill_level)` - Ericsson matrix
- `is_mechanism_only(claim)` - D7 detection

### Track B: Quality-Weighted Entrenchment (P-QW Decisions) — ✓ COMPLETE

**Target Files**: `src/services/web_persistence.py`, `contracts/vocab/institution_tiers.json`

| ID | Task | Source | Description | Status |
|----|------|--------|-------------|--------|
| 2.6.8 | Reduce institution weight | P-QW Q2 | Changed to 0.12 in QUALITY_WEIGHTS | ✓ DONE |
| 2.6.9 | Add institutions to tier list | P-QW Q2 | Wageningen, Uppsala, JCU added as Tier 1 | ✓ DONE |
| 2.6.10 | Update component weights | P-QW Q4 | QUALITY_WEIGHTS dict with new weights | ✓ DONE |
| 2.6.11 | Add citation velocity | P-QW Q5 | `citation_velocity(count, year)` function | ✓ DONE |
| 2.6.12 | Implement piecewise mapping | P-QW Q6 | `quality_to_entrenchment()` with floor at 0.3 | ✓ DONE |
| 2.6.13 | Publish institution tier list | P-QW Q2 | Created `contracts/vocab/institution_tiers.json` | ✓ DONE |
| 2.6.14 | Update save_paper_quality | — | Extended with institution, h_index, pub_year, eco_validity | ✓ DONE |

**New Functions**:
- `citation_velocity(citation_count, publication_year)` - Q5
- `quality_to_entrenchment(overall_quality)` - Q6 piecewise
- `get_institution_tier(institution)` - Q2 tier lookup
- `institution_tier_to_score(tier)` - tier to quality score

**New Files**:
- `contracts/vocab/institution_tiers.json` - published tier list

**Tests**: 62 web_persistence tests passing

### Approved (No Code Changes Needed)

| Source | Decision | Note |
|--------|----------|------|
| P-TC D2 | Instrument mapping confidence 0.95 | Keep as-is, add `transfer_uncertainty` to docs |
| P-TC D5 | Rate limit 0.1s with API key | Keep as-is |
| P-QW Q1 | Citation thresholds 8-tier | Keep as-is |
| P-QW Q3 | h-index tier boundaries | Keep as-is |

---

## Pending Panel Decisions

### P-TC: Task Context Decisions — CONSULTED (2026-02-08)

**Status**: PANEL COMPLETE
**Review**: `docs/PANEL_P-TC_TASK_CONTEXT_REVIEW_2026_02_08.md`

| D# | Decision | Panel Verdict | Action |
|----|----------|---------------|--------|
| D1 | Default task when unknown | MODIFY | Add `inference_basis` field (stated/inferred/unknown) |
| D2 | Instrument mapping confidence | APPROVE | Keep 0.95, add `transfer_uncertainty` caveat |
| D3 | Keyword inference confidence | MODIFY | Keep 0.5-0.7, add `review_recommended` flag for <0.7 |
| D4 | Default ecological validity | MODIFY | Default `lab_task` with `presumed: true` flag |
| D5 | Rate limit with API key | APPROVE | Keep 0.1s |
| D6 | Cognitive demand levels | MODIFY | Keep 3 levels, add `effective_demand` from skill×demand |
| D7 | Include pure psych/neuro papers | APPROVE | Include with `mechanism_only` tag |

**Implementation**: → **Sprint 2.6 Track A** (tasks 2.6.1–2.6.7)

### P-QW: Quality-Weighted Entrenchment Decisions — CONSULTED (2026-02-08)

**Status**: PANEL COMPLETE
**Review**: `docs/PANEL_P-QW_QUALITY_WEIGHTED_ENTRENCHMENT_REVIEW_2026_02_08.md`

| Q# | Decision | Panel Verdict | Action |
|----|----------|---------------|--------|
| Q1 | Citation thresholds | APPROVE | Keep 8-tier system |
| Q2 | Institution tier assignments | MODIFY | Reduce weight to 0.12, add Wageningen/Uppsala/JCU, publish list |
| Q3 | h-index tier boundaries | APPROVE | Keep current boundaries |
| Q4 | Weighting of quality components | MODIFY | Meth 0.28, Cite 0.18, Inst 0.12, Auth 0.18, Prereg 0.10, Sample 0.10, EcoVal 0.04 |
| Q5 | Career stage adjustment | MODIFY | Replace with citation velocity (citations/year) |
| Q6 | Quality → entrenchment mapping | MODIFY | Piecewise: Quality < 0.3 → 0.10; else linear 0.15-0.70 |

**Implementation**: → **Sprint 2.6 Track B** (tasks 2.6.8–2.6.14)

---

## Panel Recommendations Tracking

### From P-EC (Epistemic-Causal) — Awaiting Implementation

| Rec# | Source Panel | Recommendation | Target Sprint | Status |
|------|--------------|----------------|---------------|--------|
| EC-1 | Thagard | Two-layer architecture documentation | 1.5 | DONE |
| EC-2 | Longino | Dialectical structure tracking | 2.5 | PLANNED |
| EC-3 | Cartwright | Scope metadata with boundary conditions | 1.6 | DONE |
| EC-4 | Chang | Iteration tracking for epistemic development | 2.0 | PLANNED |
| EC-5 | Case | Learning pathway support for education | 3.0 | DEFERRED |
| EC-6 | Mitchell | Community-relative entrenchment | 2.5 | PLANNED |
| EC-7 | Gopnik | Empirical validation against expert judgment | 2.0 | PLANNED |
| EC-8 | Thagard | Efficient coherence approximations | Tech Debt | LOGGED |
| EC-9 | van Fraassen | Cultural meaning beyond baselines | 2.5 | PLANNED |

### From P-EC Synergies Panel — Awaiting Implementation

| Rec# | Source | Recommendation | Target Sprint | Status |
|------|--------|----------------|---------------|--------|
| SY-1 | Pearl | Causal diagnosis of credence differences | 2.0 | PLANNED |
| SY-2 | Spirtes/Glymour | Causal discovery from mechanism beliefs | 3.0 | DEFERRED |
| SY-3 | Griffiths | EM-style joint optimization | 3.0 | DEFERRED |
| SY-4 | Eberhardt | Active learning infrastructure | 3.0 | DEFERRED |
| SY-5 | Murphy | Joint Bayesian inference | 3.0 | DEFERRED |
| SY-6 | van Fraassen | Contrast-relative causal discovery | 2.0 | PLANNED |
| SY-7 | Cartwright | Capacity inference | 2.5 | PLANNED |
| SY-8 | Longino | Paradigm-relative models | 2.5 | PLANNED |
| SY-9 | Chang | Belief value analysis | 1.6 | DONE |

---

## Technical Debt

**Panel**: P-TD (Technical Debt) — CONSULTED (2026-02-08)
**Review**: `docs/PANEL_P-TD_TECHNICAL_DEBT_REVIEW_2026_02_08.md`

| ID | Item | Priority | Panel Recommendation | Sprint |
|----|------|----------|---------------------|--------|
| TD-1 | Coherence O(n²) → O(n log n) | 3 | Hierarchical + constraint network + caching | TD-C |
| TD-2 | Theory inference accuracy | 1 | Embedding similarity + keyword disambiguation (target 85%) | TD-A |
| TD-3 | Scope metadata missing | 2 | Section-aware hybrid extraction + generalization_risk | TD-B |
| TD-4 | Temporal parsing | 4 | spaCy patterns + LLM fallback | TD-D |

### Technical Debt Sprints (Panel-Recommended Order)

**Sprint TD-A: Theory Inference** (TD-2) — ✓ COMPLETE (2026-02-08)
| Task | Description | Status |
|------|-------------|--------|
| TD-A.1 | Add sentence-transformers dependency | ✓ |
| TD-A.2 | Create theory description embeddings | ✓ |
| TD-A.3 | Implement EmbeddingTheoryMatcher class | ✓ |
| TD-A.4 | Add disambiguation rules for false positives | ✓ |
| TD-A.5 | Add confidence scores to theory assignments | ✓ |
| TD-A.6 | Write tests (43 passing) | ✓ |
| TD-A.7 | Integrate with extraction_to_web.py | ✓ |

**Files created**: `src/services/theory_matcher.py` (~400 lines), `tests/test_theory_matcher.py` (43 tests)

**Sprint TD-B: Scope Extraction** (TD-3) — ✓ COMPLETE (2026-02-08)
| Task | Description | Status |
|------|-------------|--------|
| TD-B.1 | Add spaCy NER patterns for scope entities | ✓ |
| TD-B.2 | Implement section-aware extraction | ✓ |
| TD-B.3 | Add explicit vs. inferred tracking | ✓ |
| TD-B.4 | Calculate generalization_risk | ✓ |
| TD-B.5 | Create ScopeExtractor class | ✓ |
| TD-B.6 | Integrate with extraction_to_web.py | ✓ |
| TD-B.7 | Write tests (51 passing) | ✓ |

**Files created**: `src/services/scope_extractor.py` (~500 lines), `tests/test_scope_extractor.py` (51 tests)

**Sprint TD-C: Scalability** (TD-1) — ✓ COMPLETE (2026-02-08)
| Task | Description | Status |
|------|-------------|--------|
| TD-C.1 | Implement theory-based belief clustering | ✓ |
| TD-C.2 | Add hierarchical coherence computation | ✓ |
| TD-C.3 | Add coherence caching with invalidation | ✓ |
| TD-C.4 | Benchmark at 5000 beliefs (<100ms target) | ✓ |
| TD-C.5 | Add constraint network for explicit relations | ✓ |
| TD-C.6 | Write tests (64 passing) | ✓ |

**Files created**: `src/services/scalable_coherence.py` (~1000 lines), `tests/test_scalable_coherence.py` (64 tests)

**Sprint TD-D: Temporal** (TD-4) — ✓ COMPLETE (2026-02-08)
| Task | Description | Status |
|------|-------------|--------|
| TD-D.1 | Add temporal patterns (duration, frequency, relations) | ✓ |
| TD-D.2 | Implement duration normalization (to minutes) | ✓ |
| TD-D.3 | Add temporal relation extraction (before/after/during) | ✓ |
| TD-D.4 | Integrate with scope extraction | ✓ |
| TD-D.5 | Write tests (67 passing) | ✓ |

**Files created**: `src/services/temporal_parser.py` (~900 lines), `tests/test_temporal_parser.py` (67 tests)

**Sprint TD-E: Incremental BN Learning** — ✓ COMPLETE (2026-02-08)
| Task | Description | Status |
|------|-------------|--------|
| TD-E.1 | Implement BetaBernoulliEdge with conjugate updates | ✓ |
| TD-E.2 | Create IncrementalBNBuilder class | ✓ |
| TD-E.3 | Add uncertainty tracking (credible intervals per edge) | ✓ |
| TD-E.4 | Connect VOI search to edge uncertainty | ✓ |
| TD-E.5 | Implement streaming parameter updates | ✓ |
| TD-E.6 | Add active learning prioritization | ✓ |
| TD-E.7 | Write tests (41 passing) | ✓ |

**Files created**: `src/services/incremental_bn.py` (~600 lines), `tests/test_incremental_bn.py` (41 tests)

**Extended Panel for TD-E** (Online Learning): M. Jordan, Gelman, Griffiths, Blei, Ghahramani, de Freitas

---

## Future Work (Post-Sprint 2.5)

### Sprint 2.0: Pipeline Integration

**Status**: ✓ COMPLETE (2026-02-08)

| ID | Task | Estimate | Dependencies | Status |
|----|------|----------|--------------|--------|
| 2.0.1 | Wire `extraction_to_web.py` into `pipeline.py` | 2h | Sprint 1.5 | ✓ DONE |
| 2.0.2 | Implement output serialization | 3h | — | ✓ DONE |
| 2.0.3 | Add CLI flags for web outputs | 2h | — | ✓ DONE |
| 2.0.4 | Test with sample papers | 4h | All above | ✓ DONE |
| 2.0.5 | Error handling and logging | 2h | All above | ✓ DONE |

**Sprint 2.0.5 Completion (2026-02-08)**:
- Created `src/services/pipeline_logging.py` (~400 lines)
- Custom exception hierarchy: PipelineError, ExtractionError, LLMError, ConfigurationError, WebIntegrationError, SerializationError, DatabaseError, ValidationError, RetryableError
- ErrorCollector class for structured error tracking with severity levels (FATAL, BLOCKING, DEGRADED, WARNING, INFO)
- ErrorRecord dataclass for serializable error records
- `with_retry` decorator for transient failure recovery with exponential backoff
- `pipeline_stage` context manager for stage-level error handling
- Structured JSON logging with configurable format (structured/simple)
- Environment variable configuration: AE_LOG_LEVEL, AE_LOG_FORMAT, AE_LOG_FILE
- Enhanced pipeline.py with try/except blocks for validation, extraction, and serialization stages
- New output file: `errors.jsonl` written when errors are collected
- 32 new tests (`test_pipeline_logging.py`)
- All 1346 tests passing

**Sprint 2.0.1 Completion (2026-02-08)**:
- Wired TD-C (Scalable Coherence) into pipeline.py
- Wired TD-E (Incremental BN Learning) into pipeline.py
- Added CoherenceManager for O(n log n) coherence computation
- Added IncrementalBNBuilder for Bayesian parameter updates
- Added `bn_incremental_state.json` output file
- Added TD statistics to coherence_summary.json
- 13 new integration tests (`test_pipeline_td_wiring.py`)

**Sprint 2.0.2 Completion (2026-02-08)**:
- Created `src/services/output_serializer.py` (~500 lines)
- Manifest generation with SHA256 checksums for all outputs
- Theory inference export (TD-A audit trail)
- Scope condition export (TD-B)
- Temporal expression export (TD-D)
- Cluster statistics export (TD-C)
- BN edge export with 95% credible intervals (TD-E)
- Enhanced belief serialization with all TD module data
- Schema versions for all output types
- 20 new tests (`test_output_serializer.py`)
- New pipeline outputs: `manifest.json`, `cluster_stats.json`, `bn_edges.json`

**Sprint 2.0.3 Completion (2026-02-08)**:
- Added Web of Belief CLI flags: `--web/--no-web`, `--web-equilibrium/--no-web-equilibrium`, `--web-max-iterations`, `--web-convergence-threshold`
- Added Export control CLI flags: `--export-manifest/--no-export-manifest`, `--export-bn/--no-export-bn`, `--export-cluster-stats/--no-export-cluster-stats`, `--export-bn-edges/--no-export-bn-edges`
- Updated `run_from_contract_bundle()` and `_integrate_into_web_of_belief()` to accept `web_options` and `export_options`
- Web integration can now be completely disabled via `--no-web`
- Environment variables overridden by CLI flags
- 9 new tests (`test_cli_web_flags.py`)

**Sprint 2.0.4 Completion (2026-02-08)**:
- Tested pipeline with `contracts/ae_af/examples/input_bundle_minimal`
- Fixed V23 entrenchment compatibility issues:
  - Added `entrenchment` property to Belief class (returns `_legacy_entrenchment`)
  - Updated all Belief constructors to use `_legacy_entrenchment=` parameter
  - Fixed 3 test files: test_epistemic_causal_integration.py, test_web_persistence.py, test_phase1_refined_epistemic.py
- All outputs verified:
  - `web_state.json`: 8 beliefs, 3 constraints, coherence=0.5
  - `manifest.json`: SHA256 checksums for all 8 output files
  - `cluster_stats.json`: 6 clusters (3 theory, 2 level, 1 orphan)
  - `bn_edges.json`: 2 edges with 95% credible intervals
  - `coherence_summary.json`: TD-C scalable coherence used, TD-E incremental BN used
- All 1442 tests passing

### Sprint 3.0: Full Integration

**Status**: IN PROGRESS
**Panel**: P-S3 (21 experts consulted — see `docs/SPRINT_3.0_PLAN.md`)
**Interface**: Streamlit (primary) + FastAPI (backend)
**Philosophy**: User-type-driven design with pre-populated common questions

---

#### Sprint 3.0.1: Unified API (Foundation)

| ID | Task | Priority | Deliverable | Status |
|----|------|----------|-------------|--------|
| 3.0.1-A | Design resource-based API (~25 endpoints) | P1 | `docs/API_DESIGN_SPRINT_3.0.1.md` | ✅ DONE 2026-02-09 |
| 3.0.1-B | Implement Core Layer (7 high-use endpoints) | P1 | `app/routes/api_unified.py` | ✅ DONE 2026-02-09 |
| 3.0.1-C | Add versioning, pagination, async support | P1 | `app/routes/api_unified.py` | ✅ DONE 2026-02-09 |
| 3.0.1-D | Implement Extended Layer (20 endpoints) | P2 | `app/api/v1/extended/` | Pending |
| 3.0.1-E | Add batch operations endpoint | P2 | `app/api/v1/batch/` | Pending |
| 3.0.1-F | Add causal endpoints | P2 | `app/api/v1/causal/` | Pending |

**Core 7 Endpoints** (per Simon's layered API):
1. `/api/v1/beliefs/` — Belief CRUD + search
2. `/api/v1/queries/` — Natural language query execution
3. `/api/v1/export/` — Evidence summaries, BibTeX, bundles
4. `/api/v1/communities/` — Community-relative operations
5. `/api/v1/constraints/` — Epistemic constraints
6. `/api/v1/papers/` — Paper/source management
7. `/api/v1/admin/` — System state, health, statistics

---

#### Sprint 3.0.2: Query Engine (Intelligence)

| ID | Task | Priority | Deliverable | Status |
|----|------|----------|-------------|--------|
| 3.0.2-A | Query type detection (Pearl: associational/interventional/counterfactual) | P1 | `src/services/query_parser.py` | ✅ DONE 2026-02-09 |
| 3.0.2-B | Progressive disclosure response format (Simon: headline→summary→detail) | P1 | `src/services/query_response.py` | ✅ DONE 2026-02-09 |
| 3.0.2-C | Scope-aware output generation (Cartwright) | P1 | `src/services/scope_renderer.py` | ✅ DONE 2026-02-09 |
| 3.0.2-D | Practitioner mode with design implications (Kaplan) | P1 | Integrated in 3.0.2-B | ✅ DONE 2026-02-09 |
| 3.0.2-E | LLM integration (Haiku for parsing, Sonnet for synthesis) | P1 | `src/services/llm_query_bridge.py` | ✅ DONE 2026-02-09 |
| 3.0.2-F | Add RELATED, TRENDING, CANONICAL patterns (Bates) | P2 | `src/services/llm_query_bridge.py` | ✅ DONE 2026-02-09 |
| 3.0.2-G | Alerting/monitoring capability | P3 | `src/services/query_alerts.py` | ✅ DONE 2026-02-09 (panel review) |

**Query Types** (10 patterns):
- WHAT, WHY, COMPARE, GAPS, CONTRADICT, CONTINGENT, HOW_CONFIDENT
- NEW: RELATED, TRENDING, CANONICAL (Bates recommendation)

---

#### Sprint 3.0.3: Streamlit Interface (Understanding)

| ID | Task | Priority | Deliverable | Status |
|----|------|----------|-------------|--------|
| 3.0.3-A | Core Streamlit app with user type selection | P1 | `streamlit_app/main.py` | ✅ DONE 2026-02-09 |
| 3.0.3-B | Query interface with common questions per user type | P1 | `streamlit_app/pages/query.py` | ✅ DONE 2026-02-09 |
| 3.0.3-C | Claim network graph (D3.js/vis.js via components) | P1 | `streamlit_app/components/network.py` | ✅ DONE 2026-02-09 |
| 3.0.3-D | Admin dashboard (beliefs, constraints, system state) | P1 | `streamlit_app/pages/5_admin.py` | ✅ DONE 2026-02-09 |
| 3.0.3-E | Overview-zoom-filter-details interaction (Shneiderman) | P1 | JS interaction layer | ✅ DONE 2026-02-09 |
| 3.0.3-F | GraphML export for Gephi/Cytoscape | P2 | `src/services/graph_export.py` | ✅ DONE 2026-02-09 |
| 3.0.3-G | Community structure visualization | P2 | `streamlit_app/pages/3_communities.py` | ✅ DONE 2026-02-09 |
| 3.0.3-H | Interactive HTML export (standalone) | P2 | `src/services/graph_export.py` | ✅ DONE 2026-02-09 |

**3.0.3-A/B Implementation Notes (2026-02-09)**:
- Created `streamlit_app/query_service.py` (~500 lines) — Direct query service layer
- Updated `streamlit_app/api_client.py` — Added direct mode fallback
- Existing `main.py` already had user type selection (Cooper personas)
- Existing `pages/1_query.py` already had common questions interface
- Direct service uses `query_parser.py` for rule-based intent detection
- Supports quick/standard/deep response modes
- Scope-aware output with Cartwright-style conditions
- 35 tests passing (`tests/test_streamlit_query_service.py`)

**User Types with Common Questions** (Cooper personas):

| User Type | Persona | Example Questions (5-10) |
|-----------|---------|-------------------------|
| **Practitioner/Designer** | Marcus Williams | "What reduces stress in hospitals?", "Evidence for plants in offices?", "Windows vs skylights for wellbeing?", "Practical recommendations for waiting rooms", "Dosage for biophilic elements?" |
| **Senior Researcher** | Dr. Sarah Chen | "Gaps in biophilic design research?", "Methodological concerns in findings?", "Mechanisms explaining nature-health links?", "ART vs SRT evidence quality?", "Impact if Ulrich 1984 retracted?" |
| **Graduate Student** | Jordan Taylor | "How does ART theory work?", "Key papers on biophilia?", "What's contested in this field?", "Where should I focus my thesis?", "Explain the evidence hierarchy" |
| **Systematic Reviewer** | — | "All evidence for outcome X", "Studies with RCT methodology", "Export citations for stress reduction", "Cross-study comparison table" |
| **Quick Lookup** | — | "Credence for claim X?", "What supports Y?", "Is Z established or contested?" |

**3.0.3-C/E Implementation Notes (2026-02-09)**:
- Created `streamlit_app/components/network.py` (~300 lines) — Reusable network component
- Wraps `src/services/network_service.py` (~1050 lines) with comprehensive vis.js integration
- `render_claim_network()` — Main visualization function with layout/clustering options
- `render_network_controls()` — Sidebar widgets for layout algorithm, clustering, max nodes
- `render_network_metrics()` — Graph metrics display (nodes, edges, density, degree)
- `render_node_focus_view()` — Focus on node neighborhood (2-hop by default)
- `get_beliefs_from_web()` — Direct WebOfBelief data retrieval
- Updated `pages/2_explore.py` to use component with real constraint data
- Shneiderman's mantra implemented: Overview (full graph) → Zoom (pan/zoom controls) → Filter (sidebar filters) → Details (node click shows constraints/evidence)
- Layout algorithms: force-directed (default), Barnes-Hut, repulsion, hierarchical
- Clustering modes: theory, level, status, community
- Node color by status, size by credence, edge color by polarity

**3.0.3-D Implementation Notes (2026-02-09)**:
- Updated `streamlit_app/pages/5_admin.py` to use real data from WebOfBelief and API
- Added data access functions: `get_system_stats()`, `get_health_status()`, `get_real_beliefs()`, `get_real_constraints()`, `get_real_communities()`, `get_real_papers()`
- System Overview now shows real counts from WebOfBelief
- Health checks verify: API server, SQLite database, WebOfBelief status, LLM configuration
- Belief Browser with live filtering by status, level, credence, and search
- Constraint Viewer with real constraints and statistics (positive/negative counts)
- Community Browser with CommunityRegistry data and sample beliefs
- Paper Browser with SQLite database queries

**3.0.3-F/G/H Implementation Notes (2026-02-09)**:
- Created `src/services/graph_export.py` (~1100 lines) — Multi-format graph export
- **GraphML export**: Full support for Gephi, Cytoscape, yEd, NetworkX, igraph
- **GEXF export**: Gephi native format with visual attributes (color by status, size by credence)
- **JSON export**: D3.js/vis.js compatible with metrics
- **DOT export**: Graphviz format with color coding
- **Interactive HTML export**: Self-contained vis.js visualization with:
  - Sidebar filters (search, credence slider, status checkboxes)
  - Layout algorithm selector (force-directed, Barnes-Hut, repulsion)
  - Node click info panel
  - Legend and navigation controls
- Updated `streamlit_app/pages/3_communities.py` with network visualization tab
- Community network shows: theory nodes, contestation edges (dashed red), shared belief edges (green)
- Real data from CommunityRegistry with fallback to defaults

---

#### Sprint 3.0.4: Export (Delivery)

| ID | Task | Priority | Deliverable | Status |
|----|------|----------|-------------|--------|
| 3.0.4-A | Evidence summary generator with scope metadata (Cartwright) | P1 | `src/services/evidence_summarizer.py` | ✅ DONE 2026-02-09 |
| 3.0.4-B | Pipeline-friendly formats (JSONL, Parquet) (Zaharia) | P1 | `src/services/export_formats.py` | ✅ DONE 2026-02-09 |
| 3.0.4-C | Verification checklists (Gawande) | P1 | `src/services/export_checklists.py` | ✅ DONE 2026-02-09 |
| 3.0.4-D | BibTeX generator with full metadata | P2 | `src/services/bibtex_generator.py` | Pending |
| 3.0.4-E | Purpose-driven export bundles (Munzner) | P2 | `src/services/export_bundles.py` | Pending |
| 3.0.4-F | Report generation (PDF/Markdown) | P3 | `src/services/report_generator.py` | ✅ DONE (Sprint 3.0.5-G) |

---

#### Sprint 3.0.5: Admin & System Inspection

| ID | Task | Priority | Deliverable | Status |
|----|------|----------|-------------|--------|
| 3.0.5-A | Admin dashboard in Streamlit | P1 | `streamlit_app/pages/admin.py` | DONE |
| 3.0.5-B | Belief inspector (browse, search, filter) | P1 | Admin component | DONE |
| 3.0.5-C | Constraint viewer (network visualization) | P1 | Admin component | DONE |
| 3.0.5-D | Community browser (members, credences) | P1 | Admin component | Pending |
| 3.0.5-E | System statistics (counts, coherence, health) | P1 | Admin component | Pending |
| 3.0.5-F | Paper/source browser | P2 | Admin component | Pending |
| 3.0.5-G | Export audit trail | P2 | Admin component | Pending |

---

#### Implementation Order (Recommended)

```
Phase 1: Foundation (3.0.1-A, 3.0.1-B, 3.0.1-C)
         Core API with 7 endpoints, versioning, async
         ↓
Phase 2: Intelligence (3.0.2-A through 3.0.2-E)
         Query engine with LLM integration
         ↓
Phase 3: Interface (3.0.3-A through 3.0.3-E, 3.0.5-A through 3.0.5-E)
         Streamlit app + Admin dashboard + User types
         ↓
Phase 4: Delivery (3.0.4-A through 3.0.4-C)
         Core export capabilities
         ↓
Phase 5: Enhancement (remaining P2/P3 tasks)
         Extended API, advanced viz, reports
```

---

#### AI Integration Architecture

**Model Tiering** (per Amodei cost optimization):
- **Template match**: $0 (no LLM) — "What is the credence for X?"
- **Haiku**: $0.005 — Query parsing, intent classification
- **Sonnet**: $0.02 — Complex synthesis, comparisons
- **Opus**: $0.10 — Deep explanations, reports

**Target**: 80% of queries at $0-0.01, 15% at $0.02, 5% at $0.10

---

### Strategic TODOs (from STRATEGIC_TODOS_2026_01_20.md)

| TODO | Description | Blocked By |
|------|-------------|------------|
| 1 | Credibility Testing Method | Sprint 2.0 |
| 2 | Interpretive Intelligence Module | Sprint 2.5 |
| 3 | VOI-Driven Article Search | Sprint 2.0 |

---

## Files Reference

### Sprint 1.5 Files (in claude_epist_layer)

| File | Lines | Status |
|------|-------|--------|
| `epistemic_causal_integration.py` | ~800 | ✓ Complete |
| `epistemic_to_causal_bridges.py` | ~600 | ✓ Complete |
| `panel_concern_resolutions.py` | ~500 | ✓ Complete |
| `quinean_counterfactual_implementation.py` | ~500 | ✓ Complete |
| `van_fraassen_contrast_class.md` | ~700 | ✓ Complete |
| `expert_panel_quinean_vs_pearl.md` | ~800 | ✓ Complete |
| `expert_panel_epistemic_causal_integration.md` | ~600 | ✓ Complete |
| `expert_panel_synergies.md` | ~400 | ✓ Complete |
| `expert_panel_formal_foundations.md` | ~600 | ✓ Complete |

### Target Integration Points (Article Eater repo)

| File | Purpose | Sprint |
|------|---------|--------|
| `src/services/web_of_belief.py` | Main Quinean engine | 1.5 |
| `src/services/extraction_to_web.py` | Claim → belief mapper | 1.5, 1.6 |
| `src/services/web_persistence.py` | Quality weighting | P-QW decisions |
| `app/tasks/pipeline.py` | Extraction pipeline | 2.0 |

---

## Ruthless Review & Scheduled Testing

**Status**: COMPLETE (2026-02-08)

### Files Created

| File | Purpose |
|------|---------|
| `bin/ruthless_review.sh` | Bundle creator for external LLM review |
| `bin/scheduled_health_check.sh` | Automated test runner with regression detection |
| `docs/RUTHLESS_REVIEW_PROMPT_V5_2026_02_08.md` | 60+ expert panel critique prompt |
| `docs/HEALTH_CHECK_SETUP.md` | Cron/launchd setup instructions |

### Usage

```bash
# Create review bundle for ChatGPT/Gemini
./bin/ruthless_review.sh

# Run health check with notification
./bin/scheduled_health_check.sh --notify

# Full health check with bundle on failure
./bin/scheduled_health_check.sh --notify --bundle
```

### Cron Setup (Daily at 9am)

```bash
crontab -e
# Add: 0 9 * * * /Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/bin/scheduled_health_check.sh --notify
```

---

## Session Log

| Date | Session Notes |
|------|---------------|
| 2026-02-10 | **Sprint ECB: Epistemic-Causal Bridge Repair PLANNED**. David raised system coherence concerns. Investigation revealed: (1) Two implementations exist (repo vs external research file), (2) Tests use wrong file, (3) Pipeline doesn't use bridge, (4) Duplicate class definitions, (5) No feedback loop. Convened Panel P-ECB-R (Haack, Pearl, van Fraassen, Simon, Cartwright, Parnas, Brooks). Created 5 docs: context, responses, plan review, implementation plan, archived features. Defined 3 sprints: ECB-1 (cleanup), ECB-2 (core integration), ECB-3 (van Fraassen + polish). Archived features documented for future reintegration: Individual Differences (IND-1 to IND-4), Cultural Meanings (CULT-1 to CULT-5), Argument Attack (ATK-1 to ATK-4). Target: ~500 lines (down from 2400). Version target: V23.1.0. |
| 2026-02-09 | **Entrenchment Tracker Updates**: Added entrenchment tracker schema + migrations, publication metadata capture, replay scaffold, BibTeX publication_date parsing + test, and pipeline metadata upsert. Added `publication_date` to AE paper schema + example. New tables in `web_persistence.py`, new `entrenchment_replay.py`, and `migrations/005_add_entrenchment_tracker.sql`. Version bumped to 23.0.5. Tests: `pytest tests/test_bibtex_utils.py`. |
| 2026-02-09 | **Sprint 3.0.3-A/B COMPLETE**: Streamlit Interface. (1) Created `streamlit_app/query_service.py` (~500 lines) - DirectQueryService for local query execution without API server. Uses query_parser.py for rule-based intent detection. Supports quick/standard/deep response modes. Scope-aware output. (2) Updated `streamlit_app/api_client.py` with direct mode fallback - automatically uses local services when API unavailable. Added `prefer_direct` option. (3) Verified existing `main.py` has user type selection (5 Cooper personas), existing `pages/1_query.py` has common questions interface. 35 tests passing (`tests/test_streamlit_query_service.py`). |
| 2026-02-09 | **Sprint 3.0.4-A/B/C COMPLETE**: (1) Evidence Summarizer: Created `src/services/evidence_summarizer.py` (~600 lines) - Cartwright-style scope metadata, transferability assessment, caveats, synthesis. 35 tests. (2) Export Formats: Created `src/services/export_formats.py` (~650 lines) - JSONL, CSV, TSV, JSON, Parquet (with pyarrow fallback), streaming exporter. 38 tests. (3) Verification Checklists: Created `src/services/export_checklists.py` (~650 lines) - Gawande-style checklists for evidence verification, extraction quality, methodology review, scope assessment, paper intake, pre-export. 37 tests. Total: 110 new tests. |
| 2026-02-09 | **3.0.3-E through 3.0.5-G + ENT-1 through ENT-5 COMPLETE**: (1) Network Visualization: Created `src/services/network_service.py` (~600 lines) - vis.js integration, force-directed layouts, clustering modes, graph metrics. 44 tests. (2) Report Generation: Created `src/services/report_generator.py` (~700 lines) - Markdown/HTML/PDF/JSON exports. 46 tests. (3) Export Audit: Created `src/services/export_audit.py` (~650 lines) - SQLite audit trail, content hashing, provenance tracking. 34 tests. (4) Entrenchment: Paper publication already in DB; Fixed `entrenchment_replay.py` (attribute naming); Added 5 entrenchment query methods to `web_persistence.py`; Created `frontend/entrenchment-monitor.html` + `app/routes/entrenchment.py` API; Health metrics (volatility, stagnation, divergence). 16 tests. |
| 2026-02-09 | **3.0.2-C + 3.0.2-F COMPLETE**: Scope-aware output + Bates patterns. (1) Created `src/services/scope_renderer.py` (~550 lines): ScopeRenderer with extract_scope_from_belief(), assess_transferability(), render_scoped_evidence(), render_scoped_response(). ScopeCondition, TransferabilityAssessment, ScopedEvidence, ScopedResponse dataclasses. Population conflict detection, lab→field warnings. 31 tests passing. (2) Enhanced `src/services/llm_query_bridge.py` with Bates berrypicking patterns: _retrieve_related() (serendipitous discovery via constraints/shared theories), _retrieve_trending() (recent papers/credence changes), _retrieve_canonical() (entrenched/foundational beliefs). Specialized synthesis methods: _synthesize_related(), _synthesize_trending(), _synthesize_canonical() with custom prompts. 48 tests passing (14 new Bates tests). |
| 2026-02-09 | **3.0.2-E COMPLETE**: LLM Integration with WebOfBelief. Enhanced `src/services/llm_query_bridge.py` (~850 lines total): (1) `retrieve_evidence()` — WebOfBelief integration with entity matching, scope filtering, credence sorting, entrenched belief boosting (~100 lines). (2) `GoogleProvider` — Gemini model support (~50 lines). (3) `_deep_synthesis()` — Full BEST tier model usage for complex reasoning with detailed JSON output structure (~100 lines). Created `tests/test_llm_query_bridge.py` (34 tests) covering: model configuration, providers, orchestration, intent detection, evidence retrieval with mock WebOfBelief, response synthesis, full pipeline, edge cases. All 34 tests passing. |
| 2026-02-09 | **ALL 16 EXTRACTION TEMPLATES COMPLETE**: Finished final 3 templates: (1) `EXTRACTION_TEMPLATE_NARRATIVE_REVIEW_2026_02_09.md` — interpretive/attributed/gap rules, argument_from_expert_opinion scheme, causal_level=association max (reviews don't generate evidence). (2) `EXTRACTION_TEMPLATE_THEORETICAL_2026_02_09.md` — theoretical/definitional/hypothesis/mechanism rules, deductive_argument scheme, causal_level=theoretical (proposed, not tested). (3) `EXTRACTION_TEMPLATE_THOUGHT_PIECE_2026_02_09.md` — opinion/recommendation/priority/asserted/framing rules, causal_level=null (opinions) or asserted (undemonstrated claims), lowest confidence range. **Extraction Table Status**: 16/16 COMPLETE. |
| 2026-02-09 | **ALL QUALITATIVE TEMPLATES COMPLETE**: Created 4 qualitative extraction templates with v2 panel additions: (1) `EXTRACTION_TEMPLATE_PHENOMENOLOGICAL_2026_02_09.md` — Husserl/Heidegger/IPA/embodied approaches, causal_level explicitly null (brackets causation), experiential rule type. (2) `EXTRACTION_TEMPLATE_ETHNOGRAPHIC_2026_02_09.md` — classical/focused/critical/autoethnographic types, cultural/norm/contextual rules, emic vs etic perspectives. (3) `EXTRACTION_TEMPLATE_GROUNDED_THEORY_2026_02_09.md` — Glaserian/Straussian/Constructivist traditions, theoretical/process/conditional rules, abductive_argument scheme. (4) `EXTRACTION_TEMPLATE_INTERVIEW_STUDY_2026_02_09.md` — descriptive/exploratory/explanatory types, perspective/reported_association/preference rules, self-report limitations documented. |
| 2026-02-09 | **EXTRACTION TEMPLATES COMPLETE**: Created 4 new extraction templates with v2 panel additions: (1) `EXTRACTION_TEMPLATE_OBSERVATIONAL_FIELD_2026_02_09.md` — naturalistic observation, association-only causal level, argument_from_sign scheme. (2) `EXTRACTION_TEMPLATE_CASE_STUDY_2026_02_09.md` — intrinsic/instrumental/critical/exemplary types, presumption rules, argument_from_example scheme. (3) `EXTRACTION_TEMPLATE_MIXED_METHODS_2026_02_09.md` — convergent/sequential designs, integration assessment, convergence-adjusted confidence. (4) Updated `EXTRACTION_TEMPLATE_SYSTEMATIC_REVIEW` to v1.1 with panel additions. Also fixed health check script integer comparison bug. |
| 2026-02-09 | **SCHEMA-1/2/3 COMPLETE**: (1) Schema extensions: Created `ae.rule.v2.schema.json` with new rule_types (rebuttal, presumption, association, contrast) and fields (causal_level, argument_scheme, critical_questions, contrast_class, difference_maker, enabling_conditions, bridge_type). Created `ae.claim.v2.schema.json` with causal_level, extraction_difficulty, source_zone. Created `contracts/vocab/argument_schemes.json` with 10 Walton schemes. (2) Panel additions doc: Created `EXTRACTION_TEMPLATE_PANEL_ADDITIONS_2026_02_09.md` specifying how to integrate Pearl causal levels, Walton argument schemes, Lipton contrast classes, Hearst/Teufel extraction metadata into existing templates. (3) Stimulus template: Created `STIMULUS_DOCUMENTATION_TEMPLATE_2026_02_09.md` with full CNfA domain features (ART, Prospect-Refuge, Biophilia, SRT markers) and ae.stimulus.v1 schema. |
| 2026-02-08 | **TBL-3 COMPLETE**: PDF Table Extraction. Created `src/services/table_extractor.py` (~750 lines). `AITableExtractor`: LLM-based extraction with structured prompts for STUDY_CHARACTERISTICS, RESULTS, QUALITY_ASSESSMENT, DEMOGRAPHICS table types. `PdfPlumberTableExtractor`: Geometric fallback. `HybridTableExtractor`: Combines both. Conversion functions to `ArticleMetadata` and `RCTStudyFact` types. 46 tests (`test_table_extractor.py`). Export engine already has table generators (ArticleMetadataTableGenerator, RCTTableGenerator) — now connected to extraction. |
| 2026-02-08 | **V23.0.0 BREAKING CHANGE: Emergent Entrenchment**: Removed `entrenchment` as settable field from `Belief` class. Added `WebOfBelief.get_entrenchment(belief_id)` method computing entrenchment via Thagard formula (40% connectivity + 30% level_weight + 30% coherence_contrib). Lazy caching with invalidation on constraint changes. Updated 8 files to use new method. Panel consultation: Quine, Haack, Thagard, Cartwright, Parnas, Simon. Philosophy clarified as foundherentism (Haack 1993), not pure Quinean coherentism. Fixed P1 bugs from ChatGPT ruthless review: constraint index purge, boundary status staleness, decision semantics (ACCEPT default). Created `tests/test_scalable_coherence_benchmark.py` (8 tests). Panel doc: `docs/PANEL_CONSULTATION_ENTRENCHMENT_2026-02-08.md`. |
| 2026-02-08 | **SPRINT 2.0.3 COMPLETE**: CLI flags for web outputs. Added `--web/--no-web`, `--web-equilibrium/--no-web-equilibrium`, `--web-max-iterations`, `--web-convergence-threshold` for Web of Belief control. Added `--export-manifest`, `--export-bn`, `--export-cluster-stats`, `--export-bn-edges` (all with `--no-*` variants) for export control. Updated pipeline functions to accept `web_options` and `export_options` dicts. 9 tests (`test_cli_web_flags.py`). |
| 2026-02-08 | **SPRINT 2.0.2 COMPLETE**: Output Serialization. Created `src/services/output_serializer.py` (~500 lines) with manifest generation, SHA256 checksums, TD module exports (theory inference audit, scope conditions, temporal expressions, cluster stats, BN edges with credible intervals). Schema versions for all outputs. Pipeline now generates `manifest.json`, `cluster_stats.json`, `bn_edges.json`. 20 tests (`test_output_serializer.py`). |
| 2026-02-08 | **SPRINT 2.0.1 COMPLETE**: Pipeline Integration wiring. Wired TD-C (Scalable Coherence) and TD-E (Incremental BN) into `app/tasks/pipeline.py`. Added CoherenceManager for O(n log n) coherence computation. Added IncrementalBNBuilder for Bayesian edge parameter updates. New output: `bn_incremental_state.json`. Enhanced `coherence_summary.json` with TD statistics (`scalable_coherence_used`, `incremental_bn_used`, `n_bn_updates`, `n_bn_edges`). Created `tests/test_pipeline_td_wiring.py` (13 tests). |
| 2026-02-08 | **SPRINT TD-D COMPLETE**: Temporal Parsing. Created `src/services/temporal_parser.py` (~900 lines) with Duration/Frequency/TemporalExpression dataclasses, pattern-based extraction for durations (simple, range, compound), frequencies (daily/weekly/etc), and temporal relations (before/after/during). Integrated with scope_extractor.py for enhanced duration extraction. ExposureType classification (acute/subacute/chronic/residential). 67 tests passing. **ALL TECHNICAL DEBT COMPLETE.** |
| 2026-02-08 | **RUTHLESS REVIEW INFRASTRUCTURE**: Created `bin/ruthless_review.sh` bundle creator, `bin/scheduled_health_check.sh` for cron/launchd scheduling, 60+ expert panel prompt (Torvalds, Carmack, Knuth, Pearl, Quine, Feynman, etc.). Health check tracks regression history in `logs/test_history.csv`. |
| 2026-02-08 | **SPRINT TD-C COMPLETE**: Scalable Coherence. Created `src/services/scalable_coherence.py` (~1000 lines) with ClusterManager (theory-based clustering), ConstraintNetwork (O(1) lookups), CoherenceCache (LRU with invalidation), CoherenceManager (hierarchical computation). Intra-cluster dense, inter-cluster sparse. Benchmark: 5000 beliefs, 25000 constraints in <500ms (target met). 64 tests passing. Drop-in replacement for O(n²) coherence computation. |
| 2026-02-08 | **SPRINT 2.6 COMPLETE**: Panel Decision Implementation. Track A (P-TC): Added `inference_basis`, `review_recommended`, `presumed_lab`, `effective_demand`, `mechanism_only` to MappingResult. New functions: `extract_task_context()`, `compute_effective_demand()`, `is_mechanism_only()`. Track B (P-QW): Updated QUALITY_WEIGHTS (Meth 0.28, Cite 0.18, Inst 0.12, etc.), added `citation_velocity()`, `quality_to_entrenchment()` piecewise mapping, `get_institution_tier()`. Created `contracts/vocab/institution_tiers.json`. 62 web_persistence tests passing. |
| 2026-02-08 | **SPRINT TD-E COMPLETE**: Incremental BN Learning. Created `src/services/incremental_bn.py` (~600 lines) with BetaBernoulliEdge (conjugate prior updates), IncrementalBNBuilder (streaming parameter updates), ActiveLearningScheduler (uncertainty × relevance prioritization). O(1) updates per observation via Beta-Bernoulli conjugacy. 95% credible intervals for edge strength. Connected to VOI search for gap identification. 41 tests passing. |
| 2026-02-08 | **SPRINT TD-B COMPLETE**: Scope Extraction enhancement. Created `src/services/scope_extractor.py` (~500 lines) with pattern-based extraction for population, setting, duration, nature type, methodology. Section-aware extraction, explicit/inferred tracking, generalization_risk calculation. Integrated with `extraction_to_web.py`. 51 tests passing. Falls back to pattern matching when spaCy unavailable. |
| 2026-02-08 | **SPRINT TD-A COMPLETE**: Theory Inference enhancement. Created `src/services/theory_matcher.py` (~400 lines) with EmbeddingTheoryMatcher, disambiguation rules for false positives (mechanical stress, attention to detail), and confidence scores. Integrated with `extraction_to_web.py`. 43 tests passing. Falls back to keyword matching when sentence-transformers unavailable. |
| 2026-02-08 | **P-TD PANEL CONSULTED**: Technical debt review complete. 9 experts consulted (Thagard, Simon, Cartwright, Mayo, Bates, Pustejovsky, Manning, Kleinberg, Hearst). Added incremental learning experts (Jordan, Gelman, Griffiths, Blei, Ghahramani). Defined 5 TD sprints: TD-A (theory inference), TD-B (scope), TD-C (scalability), TD-D (temporal), TD-E (incremental BN). See `docs/PANEL_P-TD_TECHNICAL_DEBT_REVIEW_2026_02_08.md`. |
| 2026-02-08 | **PARALLEL SESSION (Lane E) COMPLETE**: TODO 3 VOI-Driven Search enhanced. Created `cross_field_vocabulary.yaml` (~480 lines) with CNfA→psychology/neuroscience/architecture/medicine term mappings. Added `CrossFieldVocabulary` class to `voi_search.py`. Extended `QueryGenerator` with `generate_cross_field_queries()` and `expand_query_terms()`. Now 92 tests passing. |
| 2026-02-08 | **PARALLEL SESSION (Lane D) COMPLETE**: TODO 2 Interpretive Intelligence enhanced. Added MECHANISM and DISAGREEMENT patterns (expanded from 2 to 4 patterns). MechanismExplanationPattern (~150 lines), DisagreementSummaryPattern (~150 lines). Now 69 tests passing. Updated QuestionClassifier with new keywords. |
| 2026-02-08 | **PARALLEL SESSION (Lane A) COMPLETE**: Sprint 2.5 Schema Design done. Convened P-SE panel (Longino, Kitcher, Knorr Cetina, Collins, Kuhn). Resolved SE-1 through SE-5. Created `docs/SPRINT_2.5_DESIGN.md` (~600 lines) and `contracts/schemas/social_epistemology.v1.schema.json`. Lane B now unblocked for implementation. |
| 2026-02-08 | **PARALLEL SESSION (Lane C) COMPLETE**: TODO 1 Credibility Testing fully implemented. Created `credibility_feedback.py` (500 lines, 27 tests). Added Severity 3 checks (semantic coherence, stub detection) - now 68 tests. Enhanced pipeline with review queue and feedback tracking imports. Updated root `CLAUDE.md` with parallel work coordination. |
| 2026-02-08 | **PARALLEL SESSION (Lane F)**: Convened P-TC panel (7 decisions) and P-QW panel (6 decisions). Both panels complete with recommendations. See `docs/PANEL_P-TC_*.md` and `docs/PANEL_P-QW_*.md`. |
| 2026-02-08 | **Sprint 1.6 COMPLETE**: 68 tests passing. Added InferenceType, BeliefKind enums. Value computation (centrality, sensitivity). Tension-resolving experiments. P-EC-R9 enabling conditions check. |
| 2026-02-08 | **P-EC Panel APPROVED Sprint 1.5**. 17 recommendations generated. 4 high-priority for 1.6: enabling_conditions, CoherenceCache, query-local coherence, contrast warnings. |
| 2026-02-08 | **Sprint 1.5 COMPLETE**: All 3 remaining tasks done. 1.5.9: Integration tests (29→34). 1.5.10: Wire to web_of_belief.py. 1.5.11: CLAUDE.md updated. |
| 2026-02-08 | **Sprint 1.5.9 COMPLETE**: 29 integration tests passing. Fixed bridge to handle both `theory_id` (existing) and `theory_ids` (new). Key compatibility issue resolved. |
| 2026-02-08 | Integrated claude_epist_layer work; restructured panels as first-class; prioritized 1.5 → 1.6 → 2.5 |
| 2026-02-04 | Quality-Weighted Entrenchment spec drafted |
| 2026-02-03 | Task Context Integration panel convened |

---

*Tasks are project state, not ephemeral notes. Completed tasks document what we've done.*

---

## Abstract → Rule Extraction Pipeline (2026-02-11)

*Added: 2026-02-11*

### Completed: Batch 3 Processing

| Metric | Value |
|--------|-------|
| Papers queried | 64 |
| Rules extracted | 39 (batch 3) |
| Total rules from abstracts | 87 (batches 1-3) |
| High-confidence rules | ~23 |
| Marginal/problematic rules | ~11 |

### Problems Identified

1. **Topic imbalance**: Acoustic 32 rules, Restoration 1 rule (sampling bias)
2. **Relevance leakage**: ~25-30% of extracted rules are NOT CNfA-relevant
   - Methodology papers (no human outcomes)
   - Clinical/medical (not environmental)
   - Digital interfaces (not built environment)
   - Materials science, animal studies

### Root Causes

| Problem | Cause | Solution |
|---------|-------|----------|
| Topic imbalance | Used \`source\` field instead of stratified sampling | Add \`topic_category\` column, use ROW_NUMBER() PARTITION BY |
| Relevance leakage | Keywords alone don't catch false positives | Multi-tier confidence scoring (E+O keywords in abstract) |
| False positives | "mood" matches linguistics, "attention" matches CV | Require BOTH environment AND outcome keywords |

### Implemented Fixes

1. Added \`topic_category\` column to AF papers table
2. Created multi-tier confidence scoring query
3. Documented criteria in \`Article_Eater_PostQuinean_v1/docs/ABSTRACT_EXTRACTION_CRITERIA_2026-02-11.md\`

### Pending Tasks

| ID | Task | Priority |
|----|------|----------|
| DISC-13 | Implement \`extraction_priority\` column in AF database | P1 |
| DISC-14 | Create stratified sampling function for balanced topic coverage | P1 |
| DISC-15 | Add pre-extraction relevance filter (Tier 1 = high confidence pool) | P2 |
| DISC-16 | Process Tier 1 papers (300 high-confidence CNfA papers) | P2 |


---

## Zotero Import Fix (2026-02-11) ✓ COMPLETE

### Problem
- 1,672 PDFs in Zotero library
- Only 2 papers marked as zotero_import in AF database
- Matching bug: fuzzy title matching too loose (80% of shorter title)

### Fixes Applied
1. **Tightened `_titles_similar()`** in `ingest/zotero_bridge.py`:
   - Raised threshold to 85%
   - Require bidirectional match (both titles must match)
   - Minimum 5 words required for fuzzy matching
2. **Added `create_new` mode**:
   - Automatically creates new AF papers for unmatched Zotero items
   - Default: True

### Results

| Metric | Before | After |
|--------|--------|-------|
| Papers in AF | 15,036 | 15,933 (+897) |
| Papers with PDFs | 81 | 1,093 |
| PDFs in storage | ~10 | 1,017 |

### Key Papers Now in Database
- Heschong 1999 - Daylighting in Schools
- Vartanian 2014 - Ceiling height effects
- Taylor 2017 - Fractal Fluency for Biophilic
- Multiple wood/materials papers
- Baron 1992 - Indoor lighting on cognition


---

## Citation/Refinement Tracking in Epistemic Web (Future Sprint)

*Added: 2026-02-11*
*Priority: P2 (after core extraction pipeline stabilizes)*

### Problem Statement

The epistemic web currently lacks mechanisms to track when later papers refine, replicate, or extend findings from earlier papers. This matters for:

1. **Credence weighting**: Replications shouldn't double-count as independent evidence
2. **Theoretical refinement**: Track Lakatos-style progressive research programs
3. **Recency weighting**: Later refinements may be more precise
4. **Avoiding double-counting**: Same finding from multiple papers should consolidate

### Current State

- `Belief.paper_ids`: Lists papers supporting a belief (but doesn't distinguish relationship type)
- `ConstraintType`: SUPPORTS, CONTRADICTS, EXPLAINS, INSTANTIATES, BRIDGES, SHARED_EVIDENCE
- No paper-to-paper citation links
- No refinement/replication/extension tracking

### Proposed New ConstraintTypes

| Type | Meaning | Credence Effect |
|------|---------|-----------------|
| REFINES | Later narrows/qualifies earlier (same direction, more precise) | Update SE, don't double-count |
| REPLICATES | Same finding reproduced | Strengthen credence, weighted merge |
| EXTENDS | Adds moderators, new population, boundary conditions | Preserve both, link |
| SUPERSEDES | Replaces/obsoletes earlier (methodology improvement) | Shift weight to later |
| CITES | Paper B cites Paper A (neutral link for tracking) | No direct credence effect |

### Implementation Requirements

1. **Schema changes**:
   - Add new ConstraintTypes to `web_of_belief.py`
   - Add `citation_links` table: (citing_paper_id, cited_paper_id, link_type, confidence)
   
2. **Extraction logic**:
   - Detect when Paper B references Paper A's findings
   - Classify relationship type (refine vs. replicate vs. contradict)
   - May require citation parsing from PDFs
   
3. **Credence computation**:
   - Modify inverse-variance weighting to handle replications
   - Implement refinement chain tracking
   - Add recency bonus for superseding findings

4. **UI/Reporting**:
   - Show refinement chains in belief inspection
   - Flag when findings have been superseded

### Dependencies

- Requires robust paper_id matching across extractions
- May need citation extraction from PDFs (GROBID or similar)
- Would benefit from DOI-based citation graph (OpenAlex, Semantic Scholar)

### Estimated Effort

Medium-large sprint (comparable to Sprint 5 persistence work)

### Related

- Sprint 8 SHARED_EVIDENCE already handles same-study beliefs
- Social epistemology module tracks community-level credence
- Could integrate with external citation databases


### Detailed Context and Rationale

#### Why This Matters for CNfA

Consider this scenario:
1. **Ulrich (1984)**: "View of nature → faster recovery from surgery"
2. **Ulrich et al. (1991)**: "Exposure to natural environments → stress recovery (physiological markers)"
3. **Hartig et al. (2003)**: "Walking in nature → attention restoration + blood pressure reduction"
4. **Berman et al. (2008)**: "Even photos of nature → cognitive improvement (but smaller effect than real nature)"

These are NOT independent findings - they form a **refinement chain** within SRT/ART. Currently we'd treat them as separate beliefs, potentially over-counting the evidence. We should instead recognize:
- Ulrich 1984 → Ulrich 1991 (EXTENDS: adds physiological markers)
- Ulrich 1991 → Hartig 2003 (REPLICATES + EXTENDS: adds attention, active vs. passive exposure)
- All → Berman 2008 (REFINES: photos work but effect is attenuated)

#### Example from HBE/Mehrabian-Russell

1. **Mehrabian & Russell (1974)**: PAD model - environments → pleasure/arousal/dominance → approach/avoidance
2. **Donovan & Rossiter (1982)**: Applied M-R to retail - confirmed in stores
3. **Russell & Pratt (1980)**: Refined to focus on P-A (dropped Dominance for most applications)
4. **Bakker et al. (2014)**: Meta-review showing Dominance still matters but is under-studied

Without refinement tracking, we might:
- Double-count M-R 1974 and Donovan 1982 (same finding, different context)
- Miss that Russell 1980 REFINES the original (P-A more predictive than full PAD)
- Not know that Bakker 2014 SUPERSEDES the "dominance is unimportant" belief

#### Connection to Foundherentist Epistemology

In V23.0.0's foundherentist framework, entrenchment is emergent from:
- 40% connectivity (constraint count)
- 30% epistemic level weight
- 30% coherence contribution

**Citation/refinement tracking affects all three**:
1. **Connectivity**: Refinement links add constraints
2. **Level**: Original theoretical claims vs. later empirical refinements
3. **Coherence**: Replication increases coherence; contradiction decreases it

Without this, the web can't properly represent how scientific knowledge accumulates through progressive refinement rather than just accumulation of independent findings.

#### Quine/Haack Perspective

From a Quinean view, when observation conflicts with theory, ANY node in the web can be revised. But we should prefer revising:
- Peripheral beliefs over central ones (entrenchment)
- Recent findings over well-replicated ones (unless methodology improved)
- Specific findings over general theories (unless theory is falsified)

**Citation tracking enables this**: If Paper B says "contrary to Paper A, we found X", we can:
1. Check if B is a methodological improvement over A
2. See if other papers support A or B
3. Revise the belief most consistent with web coherence

#### Connection to Sprint 8 (SHARED_EVIDENCE)

Sprint 8 added `SHARED_EVIDENCE` constraint type to prevent double-counting when the same study supports multiple beliefs. Citation tracking is the **inter-paper** version of this - preventing double-counting when the same finding appears in multiple papers through replication or citation.

The current system handles:
- ✓ Same study, multiple claims (SHARED_EVIDENCE)
- ✗ Same finding, multiple papers (needs REPLICATES)
- ✗ Refined finding, multiple papers (needs REFINES)
- ✗ Obsoleted finding (needs SUPERSEDES)

#### Data Sources for Implementation

| Source | What It Provides | API Available |
|--------|------------------|---------------|
| OpenAlex | Citation links, reference lists | Yes (free) |
| Semantic Scholar | Citation context, influence scores | Yes (free) |
| Crossref | DOI-based citations | Yes (free) |
| GROBID | Extract citations from PDFs | Local service |

Recommended approach: Use OpenAlex/Semantic Scholar APIs to get citation links between papers we have, then classify relationship types based on citation context.

#### Interaction with Extraction Pipeline

When extracting rules from Paper B:
1. Check if Paper B cites any papers in our database
2. If yes, classify the citation relationship
3. When creating beliefs, check for existing beliefs from cited papers
4. If related belief exists, create REFINES/REPLICATES/EXTENDS constraint instead of new independent belief

This requires the extraction prompt to identify:
- "Consistent with [Author Year], we found..."  → REPLICATES
- "Extending [Author Year], we also found..." → EXTENDS
- "Contrary to [Author Year], our results show..." → CONTRADICTS
- "[Author Year] found X in [context]; we found X holds in [new context]" → EXTENDS
- "While [Author Year] reported [effect], our more controlled study found [refined effect]" → REFINES or SUPERSEDES

---

## Sprint 6: Non-Empirical Web Integration — Started 2026-02-14

**Specification**: `docs/Non_Empirical_Web_Integration_Spec_V1.0.md`
**Implementation Plan**: `docs/IMPLEMENTATION_TASKS_ADDENDUM_SPRINT6.md`

Extends the web of belief to handle theoretical papers, reviews, meta-analyses, expert syntheses, methodological critiques, and other non-empirical paper types.

### Sprint 6a: Schema Extensions — COMPLETE (2026-02-14)

| Task | Description | Status | Commit |
|------|-------------|--------|--------|
| 6a.1 | 12 NodeType enum in node_types.py | ✓ COMPLETE | 8d4cfa8 |
| 6a.2 | 19 EdgeType enum in edge_types.py | ✓ COMPLETE | 8d4cfa8 |
| 6a.3 | ClaimV2 dataclass (ae.claim.v2) | ✓ COMPLETE | 8d4cfa8 |
| 6a.4 | EdgeV2 dataclass (ae.edge.v2) | ✓ COMPLETE | 8d4cfa8 |
| 6a.5 | Node type → template mapping | ✓ COMPLETE | 8d4cfa8 |

### Sprint 6b: Entrenchment Dynamics — COMPLETE (2026-02-14)

| Task | Description | Status | Commit |
|------|-------------|--------|--------|
| 6b.1 | node_type_entrenchment.py (base values, modifiers) | ✓ COMPLETE | f5df233 |
| 6b.2 | theory_updating.py (asymmetric Popperian) | ✓ COMPLETE | f5df233 |
| 6b.3 | critique_propagation.py (method registry impact) | ✓ COMPLETE | f5df233 |
| 6b.4 | prediction_ledger.py (hypothesis tracking) | ✓ COMPLETE | f5df233 |
| 6b.5 | synthesis_rules.py (floor rule) | ✓ COMPLETE | f5df233 |
| 6b.6 | expert_discount.py (0.7× discount factor) | ✓ COMPLETE | f5df233 |

**Tests**: 46 tests in test_sprint6b_entrenchment.py (all passing)

### Sprint 6c: Ingestion Pipeline — COMPLETE (2026-02-14)

| Task | Description | Status | Commit |
|------|-------------|--------|--------|
| 6c.1 | paper_classifier.py (15 TemplateFamily, pattern matching) | ✓ COMPLETE | d286f27 |
| 6c.2 | theoretical_extractor.py (extract propositions/hypotheses) | ✓ COMPLETE | d286f27 |
| 6c.3 | synthesis_ingester.py (meta-analysis/review ingestion) | ✓ COMPLETE | d286f27 |

**Tests**: 25 tests in test_sprint6c_ingestion.py (all passing)
**Panel Review**: docs/PANEL_REVIEW_SPRINT6_EPISTEMIC_2026-02-14.md (8 decisions approved)

### Sprint 6d: Monitor Updates — COMPLETE (2026-02-14)

| Task | Description | Status | Files |
|------|-------------|--------|-------|
| 6d.1 | theory_monitor.py (TheoryHealthStatus, TheoryRisk) | ✓ COMPLETE | src/epistemic/monitors/theory_monitor.py |
| 6d.2 | cross_type_coherence.py (CoherenceType, anomaly detection) | ✓ COMPLETE | src/epistemic/monitors/cross_type_coherence.py |
| 6d.3 | api_extensions.py (theory/coherence/prediction endpoints) | ✓ COMPLETE | src/epistemic/api_extensions.py |
| 6d.4 | dashboard_components.py (theory visualization) | ✓ COMPLETE | streamlit_app/components/dashboard_components.py |

**Tests**: 36 tests in test_sprint6d_monitors.py (all passing)

### Sprint 6e: Integration Tests — COMPLETE (2026-02-14)

| Task | Description | Status |
|------|-------------|--------|
| 6e.1 | Test theory → hypothesis → confirmation flow | ✓ COMPLETE |
| 6e.2 | Test synthesis floor rule edge cases | ✓ COMPLETE |
| 6e.3 | Test expert vs. systematic comparison | ✓ COMPLETE |
| 6e.4 | Test methodological critique cascade | ✓ COMPLETE |
| 6e.5 | Test mixed empirical/theoretical coherence | ✓ COMPLETE |
| 6e.6 | Test prediction ledger persistence | ✓ COMPLETE |
| 6e.7 | Panel review for Sprint 6 | ✓ COMPLETE |

**Tests**: 25 tests in test_sprint6e_integration.py (all passing)
**Total Sprint 6 Tests**: 135 tests (6a: 3, 6b: 46, 6c: 25, 6d: 36, 6e: 25)

### Sprint 6 Panel Review Summary (Task 6e.7)

**Compliance Assessment**: Full compliance with Non_Empirical_Web_Integration_Spec_V1.0.md

| Spec Section | Implementation | Status |
|--------------|----------------|--------|
| §2.2 Node Types (12 types) | node_types.py | ✓ All 12 types in 5 families |
| §2.3 Node Properties | node_types.py | ✓ Properties per type |
| §3.2 Edge Types (19 types) | edge_types.py | ✓ All 19 types |
| §3.3 Compatibility Matrix | edge_types.py | ✓ Validation implemented |
| §4.2 Entrenchment Dynamics | entrenchment/*.py | ✓ Per-type rules |
| §4.2 Popperian Asymmetry | theory_updating.py | ✓ CONFIRMATION_BONUS=0.05, DISCONFIRMATION_PENALTY=0.10 |
| §4.2 Synthesis Floor Rule | synthesis_rules.py | ✓ Floor = median of included studies |
| §4.2 Expert Discount (0.7×) | expert_discount.py | ✓ Configurable discount |
| §5.5 Prediction Ledger | prediction_ledger.py | ✓ Track confirmations/disconfirmations |
| §6.2 ae.claim.v2 Contract | contracts/claim_v2.py | ✓ Universal ingestion contract |
| §6.3 ae.edge.v2 Contract | contracts/edge_v2.py | ✓ Edge ingestion contract |
| §7.1 Theory Monitor | theory_monitor.py | ✓ Health status, risk flags |
| §7.1 Coherence Monitor | cross_type_coherence.py | ✓ Anomaly detection |

**Key Epistemic Decisions Validated**:
1. Asymmetric Popperian updating prevents runaway confirmation
2. Synthesis floor ensures meta-analyses don't drop below their evidence
3. Expert discount (0.7×) implements epistemic humility for narrative reviews
4. Theory health monitoring catches unfalsifiable/overentrenched theories
5. Cross-type coherence detects orphaned nodes and structural anomalies

**Sprint 6 COMPLETE** — All 5 sub-sprints implemented and tested.

---

## RUTHLESS REPO AUDIT — 2026-02-15

**Audit Report**: `docs/REPO_AUDIT_REPORT_2026-02-15.md`
**Focus**: Sections 1, 5, 6 (Codebase Reality, Dependencies, Extraction Health)

### Critical Findings

| Issue | Severity | Status |
|-------|----------|--------|
| Tests broken (12 collection errors) | **BLOCKING** | Pending |
| Sprint 10 runtime error (missing methods) | HIGH | `find_critical_question_gaps()` and `find_argument_attack_gaps()` called but not implemented |
| GapType enum collision | MEDIUM | Sprint 6 spec vs `gap_predictor.py` have different values |
| No ResearchQueueService implementation | MEDIUM | Contract exists, no code |
| CMR pipeline not implemented | LOW | Templates in docs only |

### Blocked Tasks (Identified)

1. **Sprint 8 (CMR)** blocked by missing `FindingMechanismLink` (commented out in edge_types.py)
2. **Sprint 9 (Health Tests)** blocked by broken test suite
3. **Sprint 10 (Argument Gaps)** blocked by missing method implementations

### Audit Findings Summary

| Metric | Value |
|--------|-------|
| Papers processed | 1,170 |
| Beliefs | 10,653 |
| Constraints | 25,943 |
| Coherence score | 0.416 |
| Test files | 96 |
| Tests runnable | NO (12 collection errors) |
| Rules generated | 31 (only 0.03 per paper) |

### Recommended Next Steps

1. **FIX**: Test collection errors (12 files)
2. **FIX**: Add stub methods for `find_critical_question_gaps()` and `find_argument_attack_gaps()`
3. **RECONCILE**: GapType enum between `gap_predictor.py` and Sprint 6 spec
4. **IMPLEMENT**: ResearchQueueService (bridge contracts to GapPredictor)

---

## SPRINT 0 KICKOFF — 2026-02-15

**Authority Document**: `docs/02-15_09_Canonical_Decisions_Record_V1_0.md`

### Task 0.1: Create Directory Structure — COMPLETE

| Directory | Purpose | Status |
|-----------|---------|--------|
| `src/queue/` | Sprint 6 Research Queue | ✓ Created with `__init__.py` |
| `src/theory/` | Sprint 7 Theory Tier | ✓ Created with `__init__.py` |
| `src/cmr/` | Sprint 8 CMR Pipeline | ✓ Created with `__init__.py` |

### Task 0.2: GapType Reconciliation — COMPLETE

**Canonical Source**: `src/epistemic/gap_types.py` (new file)

| GapType Value | Weight | Description |
|---------------|--------|-------------|
| MEDIATION | 0.5 | A→X→Y exists but direct A→Y missing |
| MECHANISM | 0.7 | Empirical but no theoretical explanation |
| BOUNDARY | 0.4 | Narrow scope conditions |
| DIRECTION | 0.9 | Conflicting causal directions |
| INTERACTION | 0.5 | Independent effects, no interaction |
| VALIDATION | 0.6 | Theoretical but no empirical support |
| UNJUSTIFIED_EDGE | 0.85 | BN edge without belief support |
| CRITICAL_QUESTION | 0.6 | Walton CQ unaddressed (Sprint 10) |
| ARGUMENT_ATTACK | 0.7 | Known attack type applies (Sprint 10) |

**Updated Files**:
- `src/epistemic/gap_types.py` — NEW canonical source with GapType, GapPriority, GAP_TYPE_WEIGHTS, LEGACY_GAP_TYPE_MAP
- `src/services/gap_predictor.py` — Now imports from canonical source
- `src/services/voi_search.py` — Added canonical import, legacy adapter with `to_canonical()` method
- `src/services/discovery_funnel.py` — Added canonical import, legacy adapter with `to_canonical()` method

### Task 0.3: Update Framework Bootstrap to 10 — COMPLETE

**Added Frameworks** (per Canonical Decision 3):
- CB — Chronobiological Regulation (Tier 1.9)
- MSI — Multisensory Integration (Tier 1.10)

**Updated Function**: `get_tier1_frameworks()` now returns 10 frameworks:
1. PP — Predictive Processing
2. SN — Spatial Navigation / Cognitive Mapping
3. DP — Dual-Process Evaluation
4. DT — DMN/TPN Dynamics
5. NM — Neuromodulatory Systems
6. IC — Interoceptive / Constructionist Affect
7. MS — Memory Systems
8. EC — Embodied Cognition
9. CB — Chronobiological Regulation (new)
10. MSI — Multisensory Integration (new)

### Task 0.4: Update Stale Docs — COMPLETE

**Per Canonical Decision 4** (`SUBPERSONAL / PERSONAL_EPISTEMIC / MIXED`):

| Document | Changes Made |
|----------|--------------|
| `CLAUDE.md` | Updated Effect Pathways to use canonical taxonomy; Updated Three Tiers to list 10 Tier 1 frameworks; Demoted ART/SRT/Biophilia to Tier 2 Domain Theories |
| `docs/IMPLEMENTATION_TASKS.md` | Updated EffectPathway enum in Task 4b.3 to use canonical taxonomy |

**Retired Terminology**:
- ~~EXPLICIT~~ → PERSONAL_EPISTEMIC (conscious evaluation)
- ~~IMPLICIT_COGNITIVE~~ → SUBPERSONAL (automatic processing below awareness)
- ~~IMPLICIT_PHYSIOLOGICAL~~ → SUBPERSONAL (direct physiological effects)
- MIXED → MIXED (unchanged)

---

### Sprint 0 Summary

| Task | Status | Files Created/Modified |
|------|--------|------------------------|
| 0.1 | ✓ COMPLETE | `src/queue/__init__.py`, `src/theory/__init__.py`, `src/cmr/__init__.py` |
| 0.2 | ✓ COMPLETE | `src/epistemic/gap_types.py` (new), `gap_predictor.py`, `voi_search.py`, `discovery_funnel.py` |
| 0.3 | ✓ COMPLETE | `src/data/theory_bootstrap.py` (CB + MSI frameworks) |
| 0.4 | ✓ COMPLETE | `CLAUDE.md`, `docs/IMPLEMENTATION_TASKS.md` |

**Next**: Run test suite to verify `test_theory_system.py::test_list_theories` passes (expects ≥6 theories, should now get 10).

---

### Schema Fix (discovered during Sprint 0 verification)

**Issue**: Database CHECK constraint in `db/sql/017_theories.sql` only allowed old theory levels (`meta_principle`, `theory`, `principle`, `mechanism`) but new Tier Architecture uses `framework_theory`, `domain_theory`, `methodological`.

**Fix Applied**: Updated CHECK constraint to include all TheoryLevel values:
```sql
level TEXT NOT NULL CHECK(level IN (
    'framework_theory', 'domain_theory', 'methodological', 'mechanism',
    'meta_principle', 'theory', 'principle'  -- Legacy values for backwards compatibility
)),
```

**Result**: 
- `test_list_theories` now PASSES (expects >= 6 theories, gets 15)
- `test_list_theories_with_filter` FAILS - test uses deprecated level values, needs update

### Follow-up Task

| ID | Task | Priority | Notes |
|----|------|----------|-------|
| T-POST-0.1 | Update `test_list_theories_with_filter` to use `FRAMEWORK_THEORY` and `DOMAIN_THEORY` | LOW | Test uses deprecated TheoryLevel values |

---

## Sprint 1.1–1.3 Complete — 2026-02-15

### Sprint 1.1: Claim Node Extensions — COMPLETE

| File | Change |
|------|--------|
| `db/sql/019_argumentation_fields.sql` | Added `argument_scheme`, `critical_questions` columns to `theory_claims` and `findings` |
| `src/models/theory_models.py` | Added fields to `TheoryClaim` dataclass |
| `tests/test_theory_system.py` | 2 new tests for argumentation fields + backward compatibility |

### Sprint 1.2: ConstraintType + EdgeType Merge — COMPLETE

**Per Opus decisions (2026-02-15):**

| Decision | Verdict |
|----------|---------|
| EPISTEMIC_DERIVATION vs COHERENCE_SUPPORT | **KEEP DISTINCT** (derivation = inferential, coherence = holistic) |
| SUPPORTS/CONTRADICTS vs CONFIRMS/DISCONFIRMS_PREDICTION | **KEEP DISTINCT** (pre-CMR vs post-CMR) |
| BN EdgeType separate | **CONFIRMED** (different semantic layer) |

**Implementation:**

| File | Change |
|------|--------|
| `src/epistemic/edge_types.py` | Expanded to 36 values in 9 categories; added `ConstraintType` alias |
| `src/services/web_of_belief.py` | Replaced local `ConstraintType` with import from `edge_types` |
| `src/services/epistemic_causal_bridge.py` | Replaced deprecated `ConstraintType` with import |

**EdgeType categories (36 total):**
1. CONSTRAINT (6): SUPPORTS, CONTRADICTS, EXPLAINS, INSTANTIATES, ANALOGOUS, INDEPENDENT
2. COHERENCE (2): COHERENCE_SUPPORT, COHERENCE_TENSION
3. EPISTEMIC (3): EPISTEMIC_DERIVATION, EPISTEMIC_CROSS_TEMPLATE, EPISTEMIC_MEDIATION
4. BRIDGE/WARRANT (4): BRIDGES, STRONG_TENSION, SHARED_EVIDENCE, GENERALIZABILITY_WARRANT
5. ARGUMENTATIVE (2): ARGUMENTATIVE_SUPPORT, ARGUMENTATIVE_CHALLENGE
6. REVIEW_SYNTHESIS (4): INCLUDES_IN_SYNTHESIS, SYNTHESIZES_AS, IDENTIFIES_MODERATOR, CONTRADICTS_SYNTHESIS
7. THEORETICAL (6): THEORETICALLY_PREDICTS, CONFIRMS_PREDICTION, DISCONFIRMS_PREDICTION, PROPOSES_MECHANISM, SUBSUMES_THEORY, THEORY_TENSION
8. CONCEPTUAL (4): DEFINES_CONSTRUCT, MUST_DISTINGUISH, REDEFINES, ORGANIZES
9. CRITIQUE (3): CHALLENGES_METHOD, CHALLENGES_PARADIGM, PROPOSES_BETTER_METHOD
10. ATTRIBUTION (2): ATTRIBUTES_FINDING, INTERPRETS_AS

### Sprint 1.3: NodeDomain + NodeTypeFamily — NO MERGE NEEDED

**Decision**: These are orthogonal concepts and should remain separate.
- `NodeTypeFamily` = epistemic classification (EVIDENCE, STRUCTURAL, INTERPRETIVE, GAP, META)
- `NodeDomain` = subject area (BASIC_SCIENCE, ENVIRONMENTAL_PSYCHOLOGY, METHODOLOGY, CNFA, EPISTEMIC)

### Test Results

```
26 passed, 8 skipped, 1 warning
```

All modifications verified working.

---

## Sprint 1.5: Cross-Repo Enum Drift Resolution — 2026-02-16

**Objective**: Resolve 13 drift issues detected by `scripts/check_enum_drift.py` to unblock Codex Sprint 1.4 work.

**Canonical Source**: `contracts/vocab/canonical_enums.json`

### Summary of Drift Issues

| # | Repo | File | Category | Issue Type | Values |
|---|------|------|----------|------------|--------|
| 1 | AE | `ruthless_bundle.../voi_search.py` | GapType | deprecated aliases | `uncertain`, `unexplored` |
| 2 | Article_Finder | `search/gap_analyzer.py` | GapType | unknown values | `coverage`, `neural`, `theory` |
| 3 | AE | `src/methods/task_ecology.py` | ClaimType | unknown values | `evaluative_response`, `functional_effect` |
| 4 | BN_graphical | `article_decomposer.py` | ClaimType | deprecated aliases | `boundary`, `effect`, `mechanism`, `null_result`, `replication` |
| 5 | AE | `src/services/incremental_bn.py` | EvidenceType | deprecated alias | `unknown` |
| 6 | AE | `ruthless_bundle.../incremental_bn.py` | EvidenceType | deprecated alias | `unknown` |
| 7 | BN_graphical | `literature_linker.py` | EvidenceType | unknown values | `direct`, `indirect`, `meta`, `review` |
| 8 | BN_graphical | `enhanced_edge.py` | EvidenceType | deprecated alias | `empirical` |
| 9 | AE | `src/methods/task_ecology.py` | PathwayType | deprecated aliases | `explicit`, `implicit_cognitive`, `implicit_physiological` |
| 10 | BN_graphical | `bn.api.v2.schema.json` | ConfidenceIntervalShape | deprecated format | `confidence_interval_array` |
| 11 | AE | `ae.claim.v2.schema.json` | ConfidenceIntervalShape | deprecated format | `ci95_array` |
| 12 | Outcome_Contractor | `article_extraction_contracts.py` | ArticleTypeCrosswalk | deprecated aliases | 8 values |
| 13 | Outcome_Contractor | `article_type_classifier.py` | ArticleTypeCrosswalk | deprecated aliases | 8 values |

---

### Phase A: AE Internal Fixes — ✓ COMPLETE (2026-02-16)

| Task ID | Description | File | Action | Status |
|---------|-------------|------|--------|--------|
| 1.5.A1 | Fix EvidenceType deprecated alias | `src/services/incremental_bn.py` | Replace `unknown` → `observational` | ✓ DONE |
| 1.5.A2 | Fix PathwayType deprecated aliases | `src/methods/task_ecology.py` | Canonical values: `subpersonal`, `personal_epistemic`, `mixed` | ✓ DONE |
| 1.5.A3 | Rename ClaimType to ClaimBifurcationType | `src/methods/task_ecology.py` | Renamed to avoid collision; backward compat alias in `__init__.py` | ✓ DONE |
| 1.5.A4 | Exclude ruthless_bundle from drift check | `scripts/check_enum_drift.py` | Added to exclusion paths | ✓ DONE |

---

### Phase B: Schema Fixes — ✓ COMPLETE (2026-02-16)

| Task ID | Description | File | Action | Status |
|---------|-------------|------|--------|--------|
| 1.5.B1 | Migrate CI shape in AE schema | `contracts/ae_af/schemas/ae.claim.v2.schema.json` | Changed to `{ci_lower, ci_upper}` object | ✓ DONE |
| 1.5.B2 | Verify table_extractor CI format | `src/services/table_extractor.py` | Already uses `ci_lower`/`ci_upper` | ✓ VERIFIED |

**Signal**: `signals/SPRINT_1_5_PHASE_AB_COMPLETE.json`
**Result**: Drift reduced from 13 → 7 issues. All AE-internal drift resolved.

---

### Phase C: External Repo Fixes — PARTIAL COMPLETE (C2/C3 done; C1/C2c remain decision-tracked)

**Assignee**: Codex or CC with cross-repo coordination
**Blocking**: Codex Sprint 1.4 drift check (must reach 0 issues)

#### C1: Article_Finder_v3_2_3

| Task ID | Description | File | Action | Status |
|---------|-------------|------|--------|--------|
| 1.5.C1a | **DECISION**: GapType unknown values | `search/gap_analyzer.py` | `coverage`, `neural`, `theory` not in canonical. Options: (a) add to canonical, (b) map to existing, (c) remove | DECISION NEEDED |

**Mapping proposal if (b)**:
- `coverage` → `mechanism` (coverage gap = unexplored mechanism)
- `neural` → `mechanism` (neural pathway = mechanism type)
- `theory` → `unjustified_edge` or new canonical value?

#### C2: BN_graphical

| Task ID | Description | File | Action | Status |
|---------|-------------|------|--------|--------|
| 1.5.C2a | Fix ClaimType deprecated aliases | `article_decomposer.py` | `boundary`→`moderated`, `effect`→`causal`, `mechanism`→`mechanistic`, `null_result`→`null`, `replication`→`descriptive` | DONE (verified) |
| 1.5.C2b | Fix EvidenceType deprecated alias | `enhanced_edge.py` | `empirical` → `observational` | DONE (verified) |
| 1.5.C2c | **DECISION**: EvidenceType unknown values | `literature_linker.py` | `direct`, `indirect`, `meta`, `review` not canonical. Options: (a) add to canonical, (b) map | DECISION NEEDED |
| 1.5.C2d | Fix ConfidenceIntervalShape schema | `contracts/bn.api.v2.schema.json` | Migrate to `{ci_lower, ci_upper}` object format | DONE (verified) |

**Mapping proposal for C2c**:
- `direct` → `experimental` (direct evidence = experimental?)
- `indirect` → `observational` (indirect = observational?)
- `meta` → `meta_analysis`
- `review` → needs decision (not same as meta_analysis)

#### C3: Outcome_Contractor

| Task ID | Description | File | Action | Status |
|---------|-------------|------|--------|--------|
| 1.5.C3a | Fix ArticleTypeCrosswalk aliases | `article_extraction_contracts.py` | Replace 8 deprecated values with canonical equivalents | DONE (verified) |
| 1.5.C3b | Fix ArticleTypeCrosswalk aliases | `article_type_classifier.py` | Replace 8 deprecated values with canonical equivalents | DONE (verified) |

**Deprecated → Canonical mapping** (from canonical_enums.json):
- `cross_sectional_survey` → `observational_field`
- `ethnographic_study` → `ethnographic`
- `grounded_theory_study` → `grounded_theory`
- `longitudinal_study` → `observational_field`
- `observational_field_study` → `observational_field`
- `phenomenological_study` → `phenomenological`
- `quasi_experiment` → `empirical_v2`
- `randomized_experiment` → `empirical_v2`

---

### Decisions Required Before Proceeding

| Decision | Options | Impact | Recommended |
|----------|---------|--------|-------------|
| **D1.5.1**: task_ecology.py ClaimType | (a) Rename to ResponseType, (b) Add to canonical, (c) Separate enum | Affects CNFA claim bifurcation semantics | (a) Rename — these are Type A/B response categories, not claim types |
| **D1.5.2**: Article_Finder GapType unknowns | (a) Add to canonical, (b) Map to existing | Affects gap analysis vocabulary | (b) Map — `coverage`→`mechanism`, `neural`→`mechanism`, `theory`→`validation` |
| **D1.5.3**: BN_graphical EvidenceType unknowns | (a) Add to canonical, (b) Map to existing | Affects evidence classification | (b) Map — `direct`→`experimental`, `indirect`→`observational`, `meta`→`meta_analysis`, `review`→`theoretical` |

---

### Execution Order

```
Phase A (AE internal) ─────────────────────────┐
  1.5.A4 (exclude ruthless_bundle)             │
  1.5.A1 (incremental_bn EvidenceType)         ├─► Can run in parallel
  1.5.A2 (task_ecology PathwayType)            │
                                               │
Phase B (Schemas) ─────────────────────────────┤
  1.5.B1 (ae.claim.v2 CI shape)                │
  1.5.B2 (table_extractor verify)              │
                                               │
[GATE: Decisions D1.5.1, D1.5.2, D1.5.3] ──────┘
                                               │
                                               ▼
Phase C (External repos) ──────────────────────┐
  1.5.C2a-d (BN_graphical)                     ├─► COMPLETE
  1.5.C3a-b (Outcome_Contractor)               │   COMPLETE
  1.5.C1a (Article_Finder)                     │   Decision-tracked mapping default
                                               │
                                               ▼
1.5.A3 (task_ecology ClaimType) ───────────────┘ After D1.5.1 decision

Final: Re-run scripts/check_enum_drift.py → 0 issues
```

---

### Success Criteria

- [ ] `python3 scripts/check_enum_drift.py` exits with code 0
- [ ] All 13 drift issues resolved
- [ ] Decisions D1.5.1–D1.5.3 documented in `docs/DECISIONS_LOG.md`
- [ ] Codex can proceed with Sprint 1.4 downstream work
