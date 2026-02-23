# RUTHLESS REPO AUDIT REPORT
## Article Eater — Sections 1, 5, 6
## February 15, 2026

**Requested Focus**: Sections 1 (Codebase Reality Map), 5 (Dependency Risk Assessment), 6 (Extraction Pipeline Health)

---

# SECTION 1: CODEBASE REALITY MAP

## 1.1 What Actually Exists

### Data Models / Schemas

| Item | Status | Path | Details |
|------|--------|------|---------|
| Node model (claims, beliefs) | **EXISTS** | `src/services/web_of_belief.py` | `Belief` dataclass with: `belief_id`, `content`, `level` (EpistemicLevel enum), `status` (BeliefStatus), `credence` (Credence dataclass), `theory_id`, `paper_ids`, `domain`, `tags`, `environment_id`, `outcome_id`, `scope` |
| Edge/Link model | **EXISTS** | `src/services/web_of_belief.py` | `Constraint` dataclass with: `constraint_id`, `source_id`, `target_id`, `constraint_type` (ConstraintType), `weight` |
| Enum: node_domain | **PARTIAL** | `src/epistemic/node_types.py:16-31` | `NodeTypeFamily` enum with 5 values (EVIDENCE, STRUCTURAL, INTERPRETIVE, GAP, META). `NodeType` enum with 12 values. Note: "node_domain" terminology from IMPLEMENTATION_TASKS.md maps to `NodeTypeFamily`. |
| Enum: node_subtype | **EXISTS** | `src/epistemic/node_types.py:33-81` | `NodeType` enum with 12 values across 5 families |
| Enum: link_type | **EXISTS** | Multiple locations | `ConstraintType` in `web_of_belief.py:109-129` (13 values), `EdgeType` in `edge_types.py:30-92` (19 values). **TERMINOLOGY CONFLICT**: Two separate enums serve overlapping purposes. |
| Bridge warrant model | **EXISTS** | `src/services/bridge_warrants.py`, `src/epistemic/node_types.py:81` (BRIDGE_WARRANT NodeType) | Fully implemented bridge warrant service |
| Theory/framework model | **EXISTS** | `src/models/theory_models.py`, `src/data/theory_bootstrap.py` | `TheoryFramework` dataclass, `TheoryLevel` enum (TIER_1_FRAMEWORK, TIER_2_DOMAIN), 8 Tier 1 frameworks bootstrapped |
| Template/mechanism model | **PARTIAL** | `edge_types.py:290-344` | PLACEHOLDER ONLY. Comments state "SCHEMA_PENDING_CMR_SPEC" — `FindingMechanismLink` is commented out, awaiting CMR specification |
| ResearchTarget / queue model | **DOES NOT EXIST** in code | Contract only: `contracts/research_queue.contract.md` | Contract specifies `ResearchTarget` and `ResearchQueueService` but NO implementation exists in `src/` |

### Inference / Reasoning Engines

| Item | Status | Path | Details |
|------|--------|------|---------|
| Bayesian Network assembly | **PARTIAL** | `src/services/incremental_bn.py` | Beta-Bernoulli conjugate prior updating. **NO external BN library** (no pgmpy, pomegranate, or bnlearn). Edge strengths computed as Beta distributions but no graphical model inference (no d-separation, no conditional probability queries). |
| Coherence / constraint satisfaction | **EXISTS** | `src/services/scalable_coherence.py`, `src/services/web_of_belief.py` | Coherence score computation exists. Quadratic coherence computation in `web_of_belief.py`. Scalable version in `scalable_coherence.py`. |
| Entrenchment scoring | **EXISTS** | `src/epistemic/entrenchment/` directory | Multiple modules: `critique_propagation.py`, `node_type_entrenchment.py`. Entrenchment emerges from connection structure. |
| CMR / prediction generation | **DOES NOT EXIST** | — | No implementation. Template library mentioned in specs but not coded. |
| Gap detection / gap predictor | **EXISTS** | `src/services/gap_predictor.py` | Fully implemented `GapPredictor` class with 8 gap types: MEDIATION, MECHANISM, BOUNDARY, DIRECTION, INTERACTION, VALIDATION, UNJUSTIFIED_EDGE, CRITICAL_QUESTION, ARGUMENT_ATTACK. **Note**: Last two (Sprint 10) call methods that don't exist yet — `find_critical_question_gaps()` and `find_argument_attack_gaps()` are called but not implemented. |

### Extraction Pipeline

| Item | Status | Path | Details |
|------|--------|------|---------|
| PDF extraction tool | **EXISTS** | `src/services/pdf_extraction.py` | Uses `pdfplumber` library. Extracts: title, authors, year, journal, DOI, theories referenced, sample size, study design, exposure type, findings, effect sizes, temporal parameters |
| Claim extraction | **EXISTS** | `src/services/extraction_to_web.py`, `src/epistemic/extraction/` | Multiple extractors: `synthesis_ingester.py`, `theoretical_extractor.py`, `pathway_classifier.py`, `paper_classifier.py`, `rule_to_claim_mapper.py` |
| Metadata extraction | **EXISTS** | `src/services/pdf_extraction.py:71-100` | `ExtractedPaper` dataclass captures: title, authors, year, journal, DOI, paper_type, sample_size, study_design |
| Method identification | **EXISTS** | `src/epistemic/extraction/` directory | `pathway_classifier.py` for pathway types |
| Source quality scoring | **EXISTS** | `src/services/` | Various services contribute to quality assessment |

### Data / Artifacts

| Item | Status | Path | Details |
|------|--------|------|---------|
| Papers processed | **1170 papers** | `data/accumulated_web.json` | JSON shows `n_papers_processed: 1170` |
| Beliefs count | **10,653 beliefs** | `data/accumulated_web.json` | `n_beliefs: 10653` |
| Constraints count | **25,943 constraints** | `data/accumulated_web.json` | `n_constraints: 25943` |
| Format | **JSON/JSONL** | `data/` directory | `accumulated_web.json` (16.8 MB), `rules.jsonl` (31 rules), `events.jsonl` |
| Extracted findings | **7 papers with findings** | `data/extracted_findings/` | 7 JSONL files with structured findings |
| PDFs | **37 total** | Various locations | `find` found 37 PDF files in repo |
| Test fixtures | **EXISTS** | `tests/` | 96 test files |
| Database | **SQLAlchemy configured** | `requirements.txt` | SQLAlchemy 2.0.36 in requirements. No database file found (may use SQLite or external DB) |

### Tests

| Item | Status | Details |
|------|--------|---------|
| Test framework | **pytest** | Configured in project |
| Test file count | **96 test files** | In `tests/` directory |
| Current state | **BROKEN** | 12 collection errors, 20 warnings. Tests cannot run. Errors in: `test_api_key_routes.py`, `test_api_smoke.py`, `test_full_integration.py`, `test_gold_standard.py`, `test_subject_bn_csv_pack.py`, `test_subject_bn_export.py`, `test_subject_bn_pipeline.py`, `test_ui_admin_surfaces.py`, `test_usage_admin_auth.py`, `test_vocabulary_bridge.py`, `test_voi_search.py`, `test_web_of_belief_routes.py` |
| Warnings | **Naming conflicts** | Pytest warns about `TestResult`, `TestStrength`, `TestType`, `Testability` enums in `src/models/theory_models.py` that look like test classes |

### Configuration / Infrastructure

| Item | Status | Details |
|------|--------|---------|
| Project structure | **Monorepo** | Single `Article_Eater_PostQuinean_v1` repo |
| Python version | **3.14.2** | Via `python3 --version` |
| Key dependencies | **FastAPI 0.115.2**, **pydantic 2.9.2**, **SQLAlchemy 2.0.36**, **pdfplumber** (unlisted) | In `requirements.txt` |
| Docker | **UNKNOWN** | No Dockerfile found in search |
| Deployment config | **UNKNOWN** | No deployment files found |

## 1.2 Architecture Diagram (ACTUAL)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           ARTICLE EATER v22                               │
└─────────────────────────────────────────────────────────────────────────┘

ACQUISITION PATH (WORKING):
┌──────────┐    ┌──────────────┐    ┌────────────────┐    ┌─────────────────┐
│ Zotero   │───>│ BibTeX/PDF   │───>│ pdf_extraction │───>│ ExtractedPaper  │
│ Library  │    │ Import       │    │ (pdfplumber)   │    │ dataclass       │
└──────────┘    └──────────────┘    └────────────────┘    └────────┬────────┘
                                                                    │
                                                    ┌───────────────┘
                                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                         EXTRACTION PIPELINE                             │
│  ┌────────────────┐   ┌────────────────┐   ┌───────────────────────┐   │
│  │ synthesis_     │   │ theoretical_   │   │ rule_to_claim_mapper  │   │
│  │ ingester.py    │   │ extractor.py   │   │ (rules.jsonl→beliefs) │   │
│  └────────┬───────┘   └───────┬────────┘   └───────────┬───────────┘   │
└───────────┼───────────────────┼────────────────────────┼───────────────┘
            │                   │                        │
            └───────────────────┼────────────────────────┘
                                ▼
┌────────────────────────────────────────────────────────────────────────┐
│                     WEB OF BELIEF (Quinean Coherentism)                 │
│  src/services/web_of_belief.py                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ 10,653 Beliefs ──(25,943 Constraints)──▶ Coherence Score: 0.42  │   │
│  │ Dict[belief_id, Belief]                                          │   │
│  │ Levels: THEORETICAL, INTERMEDIATE, EMPIRICAL, OBSERVATIONAL     │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                │                                        │
│                                ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ COHERENCE ENGINE (scalable_coherence.py)                         │   │
│  │ - Quadratic constraint evaluation                                │   │
│  │ - Entrenchment from connection structure                         │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────────────┘
                                │
            ┌───────────────────┼───────────────────┐
            ▼                   ▼                   ▼
┌───────────────────┐ ┌───────────────────┐ ┌───────────────────┐
│ gap_predictor.py  │ │ incremental_bn.py │ │ bridge_warrants   │
│ 8 gap types       │ │ Beta-Bernoulli    │ │ Theory-finding    │
│ VOI scoring       │ │ edge updates      │ │ connections       │
│ NO CQ/Attack impl │ │ NO d-separation   │ │                   │
└───────────────────┘ └───────────────────┘ └───────────────────┘

STORAGE:
┌──────────────────────────────────────────────────────────────────────────┐
│ data/accumulated_web.json  (16.8 MB) — master web state                  │
│ data/rules.jsonl           (31 rules)                                    │
│ data/extracted_findings/   (7 papers)                                    │
│ data/events.jsonl          (event log)                                   │
└──────────────────────────────────────────────────────────────────────────┘

NOT IMPLEMENTED (CONTRACT/SPEC ONLY):
┌──────────────────────────────────────────────────────────────────────────┐
│ ✗ ResearchQueueService (contracts/research_queue.contract.md)            │
│ ✗ VOI Collector (contracts/voi_collector.contract.md)                    │
│ ✗ CMR Pipeline (docs/*CMR*.md — templates in docs, not code)             │
│ ✗ FindingMechanismLink (edge_types.py:290-344 — commented out)           │
│ ✗ find_critical_question_gaps() — called but not implemented             │
│ ✗ find_argument_attack_gaps() — called but not implemented               │
└──────────────────────────────────────────────────────────────────────────┘
```

---

# SECTION 5: DEPENDENCY RISK ASSESSMENT

## 5.1 Blocked Tasks

| Task | Blocked Because | Required First |
|------|-----------------|----------------|
| **Sprint 8: CMR Pipeline** | `FindingMechanismLink` is commented-out placeholder in `edge_types.py:290-344`. Cannot implement CMR pipeline without this data structure. | Must implement `FindingMechanismLink` and `MechanismLinkType` first |
| **Task 6.1: ResearchTarget model** | GapType enum already exists in `gap_predictor.py` with 8 values. Sprint 6 task 6.1 spec shows different GapType. **ENUM COLLISION**. | Reconcile GapType definitions between `gap_predictor.py` and Sprint 6 spec |
| **Sprint 10: Argument Gap Detection** | `find_critical_question_gaps()` and `find_argument_attack_gaps()` are called in `find_all_gaps()` but methods don't exist. Will cause runtime error. | Implement stub methods or remove calls |
| **Tests** | 12 test files have collection errors. Tests cannot run. | Fix import errors in test files |

## 5.2 Underspecified Tasks

| Task | Judgment Needed | Why CC Can't Decide |
|------|-----------------|---------------------|
| **Template library (CMR)** | Which 30+ templates to implement? | Templates 1-30 exist in `docs/*.md` but are **narrative only**. Need structured encoding (from_variable, to_variable, maturity, etc.) which requires domain expert judgment |
| **Theory-driven VOI** | How to compute `theory_voi = min(n_frameworks / 3, 1.0)`? | Which frameworks "predict" which gaps? This is domain knowledge not present in code |
| **Causal level assignment** | CausalLevel (COUNTERFACTUAL, INTERVENTIONAL, ASSOCIATIONAL) per Pearl | Requires reading paper methodology to determine. Not extractable automatically |
| **Marr level assignment** | MarrLevel (COMPUTATIONAL, ALGORITHMIC, IMPLEMENTATION) | Theoretical judgment about what level of explanation a gap addresses |

## 5.3 Duration Risks

| Task | Estimated | Risk Factor | Likely Reality |
|------|-----------|-------------|----------------|
| **Sprint 7: Theory Tier Data Structures** | "2 weeks" implied | 8 Tier 1 frameworks already exist in `theory_bootstrap.py` BUT templates are docs-only, not code | Templates need manual encoding. 30+ templates × 15 min each = 7.5 hours minimum IF specs are clear |
| **Sprint 8: CMR Pipeline** | "2 weeks" implied | CMR spec is 89 KB of markdown. 6-step pipeline. No code exists. | Complex new system. 4+ weeks realistic |
| **Test fixes** | Not scoped | 12 files with collection errors | May require significant refactoring if imports are circular or modules missing |

## 5.4 Ordering Risks (Hidden Sequential Dependencies)

| Claimed Parallel | Actually Sequential Because |
|------------------|----------------------------|
| Sprint 6 + Sprint 7 | Sprint 6 creates `GapType` enum, Sprint 7 uses it. But `GapType` ALREADY EXISTS in `gap_predictor.py` with different values. Cannot run in parallel without breaking things |
| Sprint 4b (Method Registry) + Sprint 7 | Method registry needs to tag claims with ecological validity. Theory frameworks need method registry to assess empirical support. Circular dependency |
| Sprint 9 (Pipeline Health) after Sprint 5 | Sprint 9 needs working tests. Tests currently broken. Sprint 9 blocked until test collection errors fixed |

---

# SECTION 6: EXTRACTION PIPELINE HEALTH

## 6.1 Extraction Quality Spot Check

**Sample**: `data/extracted_findings/doi_10.1186_s41235-020-00243-4_findings.jsonl` (5 findings)

| Finding | Correctly Parsed? | Metadata Populated? | Errors? |
|---------|-------------------|---------------------|---------|
| "Architectural practice...dominated by visual/sight" | ✓ Yes | ⚠ Missing: p_value, effect_size, sample_size (all null) | Review paper - stats expected to be null |
| "Crossmodal interactions...lighting colour and thermal comfort" | ✓ Yes | ⚠ Missing: all stats null | Same |
| "Sound influences perceived safety" | ⚠ `measure_direction: "unknown"` | ⚠ All stats null | Direction should be inferrable |
| "Synaesthetic design...crossmodal correspondences" | ✓ Yes | ⚠ All stats null | Conceptual finding |
| "Multisensory approach...social, cognitive, emotional development" | ✓ Yes | ⚠ All stats null | Prediction, not measurement |

**Quality Assessment**:
- **Content extraction**: GOOD. Finding text accurately captures paper claims.
- **Metadata extraction**: POOR. All 5 findings have null statistics (p_value, effect_size, sample_size, CI).
- **Reason**: This is a **review paper** (`article_type: "review"`). Review papers don't have primary statistics. BUT the system doesn't distinguish — it creates empty fields rather than marking as "N/A for paper type."
- **Extracted by**: `"claude_manual"` — These were manually extracted, not by automated pipeline.

**Overall Error Rate Estimate**: For review papers, ~20% have ambiguous direction. For empirical papers with statistics, need separate sample.

## 6.2 Coverage Assessment

| Metric | Value | Assessment |
|--------|-------|------------|
| Papers processed | **1,170** | Strong corpus |
| Unique beliefs | **10,653** | ~9 beliefs per paper average |
| Constraints | **25,943** | ~22 constraints per paper |
| Coherence score | **0.416** | Moderate coherence |
| Extracted findings files | **7 papers** | Only 0.6% of papers have structured findings in `extracted_findings/` |
| Rules generated | **31 rules** | Only ~0.03 rules per paper — very low |

**Gap Analysis**:
- 1,170 papers processed, but only 31 rules in `rules.jsonl`
- Only 7 papers have detailed extracted findings in `extracted_findings/`
- 10,653 beliefs but only 31 mapped to rules — **extraction pipeline generates beliefs but not rules**

## 6.3 Data Format Assessment

| Question | Answer |
|----------|--------|
| Can Sprints 1-5 consume this data? | **PARTIAL**. Beliefs exist. But Sprint 4 (extraction pipeline extensions) assumes `argument_scheme`, `critical_questions` fields that aren't populated. |
| Transformations needed? | 1. Rules need claim→belief backlinks. 2. Statistics need filling for empirical papers. 3. `extracted_by: "claude_manual"` findings need automation. |
| Data migration required? | NO — data is already in JSON/JSONL. Schema compatible with existing code. |

**Critical Format Issues**:
1. `accumulated_web.json` beliefs have `theory_id: null` for 100% of sampled beliefs. Theory links not being captured.
2. `domain` field shows `realtime_pdf: 8258`, `realtime_abstract: 965`, `unknown: 1430` — 13% have unknown domain
3. Many beliefs are table cell extractions (e.g., `"content": ": Location C; Microphone 1: 52.4 dB(A)"`) — low semantic value

---

# CRITICAL FINDINGS SUMMARY

## Top 5 Issues (Blocking Severity)

1. **Tests Broken**: 12 test files have collection errors. Cannot verify any changes. **MUST FIX FIRST**.

2. **GapType Enum Collision**: `GapPredictor.GapType` (8 values) vs Sprint 6 spec `GapType` (7 values, different names). Sprint 6 cannot proceed without reconciliation.

3. **Sprint 10 Runtime Error**: `find_all_gaps()` calls `find_critical_question_gaps()` and `find_argument_attack_gaps()` which don't exist. Code will crash if called.

4. **No ResearchQueue Implementation**: Contracts exist (`contracts/research_queue.contract.md`), GapPredictor exists, but no `ResearchQueueService` bridges them.

5. **CMR Pipeline Missing**: Core spec feature (Templates 1-30, 6-step pipeline) has no code. `FindingMechanismLink` is commented out.

## Sprint Reordering Recommendation

**Current order**: 0→1→2→4→4b→3→5→6→7→8→9

**Recommended order**:
1. **FIRST**: Fix test collection errors (unlisted but blocking)
2. **THEN Sprint 0-1**: Discovery + Schema (as specified)
3. **Sprint 6 PARTIAL**: Just `ResearchTarget` model (reconcile GapType)
4. **Sprint 7**: Theory tier (already partially done in `theory_bootstrap.py`)
5. **Sprint 2-3-4-4b-5**: BN/monitors/extraction (as specified)
6. **Sprint 8**: CMR (requires Sprint 7 complete)
7. **Sprint 9**: Pipeline health (requires tests working)
8. **Sprint 10**: Argument gaps (implement stub methods)

---

*Report generated: 2026-02-15*
*Auditor: Claude Code (ruthless mode)*

---

# SECTION 2: SPECIFICATION vs REALITY GAPS (Requested Focus)

## 2.1 Per-Document Implementation Status

| Document | Implementation Status | Evidence | Stale Assumptions / Drift |
|---|---:|---|---|
| `CLAUDE.md` | 50% | Core Tier-2 concepts exist (`src/epistemic/node_types.py`, `src/epistemic/edge_types.py`, `src/methods/task_ecology.py`). | Tiering is stale (`CLAUDE.md:25` keeps ART/SRT/Biophilia in Tier 1). File map is stale (`CLAUDE.md:99-113` references missing files like `src/epistemic/schema.py`, `src/epistemic/templates.py`, `src/epistemic/extraction/tier2_extractor.py`). |
| `docs/IMPLEMENTATION_TASKS.md` | 65% | Many enums/services exist; pathway classifier implemented (`src/epistemic/extraction/pathway_classifier.py`). | Intra-doc pathway taxonomy conflict: `SUBPERSONAL/PERSONAL_EPISTEMIC/MIXED` (`docs/IMPLEMENTATION_TASKS.md:161-165`) vs `EXPLICIT/IMPLICIT_*` (`docs/IMPLEMENTATION_TASKS.md:1128-1132`). |
| `docs/THEORY_TIER_ARCHITECTURE_V1.0_2026-02-14.md` | 45% | Tier correction partially reflected in code (`src/data/theory_bootstrap.py`, `src/models/theory_models.py`). | Architecture links promised in doc (`docs/THEORY_TIER_ARCHITECTURE_V1.0_2026-02-14.md:264-299`) are not implemented; finding-mechanism schema is placeholder (`src/epistemic/edge_types.py:291-343`). |
| `docs/02-14_08_Compositional_Mechanistic_Reasoning_Spec_V1.0.md` | 10% | CMR ideas referenced in comments only (`src/epistemic/edge_types.py:305-309`). | Spec states six-step CMR pipeline, but no `src/cmr/*` modules exist. |
| `docs/02-14_09_CMR_Revised_Spec_Panel_Templates_V2.0.md` | 20% | Templates 1-20 are documented. | Not encoded as machine models (`src/theory/templates.py` missing). Internal ID renaming conflict (template headers vs summary table; see Section 2.3). |
| `docs/02-15_01_Neuroscience_Panel_Tier1_Frameworks_V1.0.md` | 10% | Recommendations are documented. | Recommends Chronobiological Tier 1 #9 (`docs/02-15_01_Neuroscience_Panel_Tier1_Frameworks_V1.0.md:253`), not reflected in active code model set. |
| `docs/02-15_02_Neuroscience_Panel_Templates_and_Taxonomy_V1.0.md` | 15% | Templates 21-30 are documented and structurally detailed. | Assumes 9 Tier-1 framework baseline (`docs/02-15_02_Neuroscience_Panel_Templates_and_Taxonomy_V1.0.md:607`) and dynamic promotion layer; code still lacks framework-layer implementation modules (`src/theory/*` missing). |
| `docs/02-15_03_Panel_III_Multimodal_Senses_HigherCognition_V1.0.md` | 5% | Templates 31-40 narrative + parameters documented. | Templates 31-40 are not structurally encoded (no link-level bridging/evidence/scope fields; see Section 4). Promotes Tier-1 #10 (`docs/02-15_03_Panel_III_Multimodal_Senses_HigherCognition_V1.0.md:426`) with no code support. |
| `docs/PANEL_QUEUE_PRIORITIZATION_2026-02-15.md` | 35% | Gap/VOI pieces exist: `src/services/gap_predictor.py`, `src/services/voi_search.py`, `src/services/discovery_funnel.py`. | Claims gap priorities are “already implemented” (`docs/PANEL_QUEUE_PRIORITIZATION_2026-02-15.md:113`), but taxonomies differ across those three services (see Section 2.3). |
| `docs/PIPELINE_EXPECTATION_TESTS_2026-02-15.md` | 85% | Referenced test/script files exist: `tests/test_realtime_pipeline_guardrails.py`, `scripts/verify_pipeline_expectations.py`, `scripts/check_table_extraction_quality.py`. | “Current result: PASS” lines (`docs/PIPELINE_EXPECTATION_TESTS_2026-02-15.md:33-47`) are point-in-time assertions, not enforced state. |
| `Ecological_Validity_Background_V1_0.md` (listed in prompt) | 40% | Method ecology code exists (`src/methods/task_ecology.py`). | The expected markdown file path is missing; available file is `.docx` (`docs/Ecological_Validity_CNFA_Background_Notes_V1.0.docx`). |
| `docs/02-15_04_Claude_Code_Master_Sprint_Plan_V1_0.md` | 20% | Some dependencies/contracts exist. | Uses non-existent paths and modules: `docs/Ecological_Validity_Background_V1_0.md` (`:102`), `docs/Queue_Prioritization_Panel.md` (`:110`), `src/queue/*` (`:116, :191, :350, :396`), `src/theory/*` (`:529, :612, :686, :752, :782`), `src/cmr/*` (`:841, :899, :955, :997`). |

## 2.2 Stale Spec Assumptions That Do Not Match Code

| Spec Assumption | Spec Source | Reality in Code |
|---|---|---|
| Tier 1 includes ART/SRT/Biophilia | `CLAUDE.md:25` | Corrected architecture demotes them to Tier 2 (`docs/THEORY_TIER_ARCHITECTURE_V1.0_2026-02-14.md:10-14`). |
| Effect pathway is `EXPLICIT/IMPLICIT_COGNITIVE/IMPLICIT_PHYSIOLOGICAL/MIXED` | `CLAUDE.md:53-56` | Operational pathway enum is `SUBPERSONAL/PERSONAL_EPISTEMIC/MIXED` (`src/services/web_of_belief.py:257-271`, `src/epistemic/extraction/pathway_classifier.py:5-7`). |
| Sprint file map under `src/epistemic/` exists as documented | `CLAUDE.md:99-113` | Missing files: `src/epistemic/schema.py`, `src/epistemic/templates.py`, `src/epistemic/extraction/tier2_extractor.py`, `src/epistemic/extraction/method_identifier.py`. |
| CMR mechanics available for finding-mechanism links | `docs/THEORY_TIER_ARCHITECTURE_V1.0_2026-02-14.md:281-299` | Explicitly pending; placeholder only (`src/epistemic/edge_types.py:291-343`). |
| Queue implementation should be in `src/queue/*` | `docs/02-15_04_Claude_Code_Master_Sprint_Plan_V1_0.md:116,191,350,396` | `src/queue/` does not exist. Queue is contract-only (`contracts/research_queue.contract.md`). |
| Theory/template implementation should be in `src/theory/*` | `docs/02-15_04_Claude_Code_Master_Sprint_Plan_V1_0.md:529,612,686,752,782` | Repository has `src/theories/` and `src/data/theory_bootstrap.py`, but no `src/theory/*` modules listed by spec. |
| CMR pipeline modules available in `src/cmr/*` | `docs/02-15_04_Claude_Code_Master_Sprint_Plan_V1_0.md:841,899,955,997` | `src/cmr/` does not exist. |
| Ecological validity spec path is markdown | `docs/02-15_04_Claude_Code_Master_Sprint_Plan_V1_0.md:102` | Available file is docx: `docs/Ecological_Validity_CNFA_Background_Notes_V1.0.docx`. |
| Queue panel gap weights map directly to existing code | `docs/PANEL_QUEUE_PRIORITIZATION_2026-02-15.md:113-121` | Gap type enums diverge across `gap_predictor`, `voi_search`, `discovery_funnel` (see next section). |

## 2.3 Cross-Document Contradictions and Terminology Conflicts

| Concept | Doc A | Doc B | Conflict | Impact |
|---|---|---|---|---|
| Tier-1 membership | `CLAUDE.md:25` | `docs/THEORY_TIER_ARCHITECTURE_V1.0_2026-02-14.md:10-14` | ART/SRT/Biophilia in Tier 1 vs explicitly “wrong; demote to Tier 2”. | Breaks framework seeding and inference assumptions. |
| Number of Tier-1 frameworks | `docs/02-15_04_Claude_Code_Master_Sprint_Plan_V1_0.md:784-793` (8) | `docs/02-15_02_Neuroscience_Panel_Templates_and_Taxonomy_V1.0.md:607` (9), `docs/02-15_03_Panel_III_Multimodal_Senses_HigherCognition_V1.0.md:426` (10) | 8 vs 9 vs 10 baseline frameworks. | Invalidates fixed-size assumptions in code/tests. |
| Template 31 identity | `docs/02-15_02_Neuroscience_Panel_Templates_and_Taxonomy_V1.0.md:601,612` | `docs/02-15_03_Panel_III_Multimodal_Senses_HigherCognition_V1.0.md:98,443` | Template 31 is proposed olfactory in Panel II, but finalized as auditory in Panel III. | Template-ID collision; downstream mappings become ambiguous. |
| Template IDs in same doc | `docs/02-14_09_CMR_Revised_Spec_Panel_Templates_V2.0.md:766,823,905,934,960,987` | `docs/02-14_09_CMR_Revised_Spec_Panel_Templates_V2.0.md:1029-1037` | Header IDs vs summary IDs are renamed/shortened (e.g., `IC_INTEROCEPTIVE_AFFECT_CONSTRUCTION_001` vs `IC_INTEROCEPTIVE_AFFECT_001`). | Deterministic template lookup fails unless alias map added. |
| Gap taxonomy | `docs/PANEL_QUEUE_PRIORITIZATION_2026-02-15.md:113-121`, `docs/02-15_04_Claude_Code_Master_Sprint_Plan_V1_0.md:123-131` | `src/services/gap_predictor.py:36-47`, `src/services/voi_search.py:244-257`, `src/services/discovery_funnel.py:41-47` | Four competing GapType sets across docs/services. | Queue priority, VOI, and closure tracking cannot align reliably. |
| Pathway taxonomy | `CLAUDE.md:53-56`, `docs/IMPLEMENTATION_TASKS.md:1128-1132` | `docs/IMPLEMENTATION_TASKS.md:161-165`, `src/epistemic/extraction/pathway_classifier.py:5-7` | EXPLICIT/IMPLICIT vs SUBPERSONAL/PERSONAL_EPISTEMIC. | Mis-tagged evidence and inconsistent validity scoring. |
| Research queue naming | `contracts/research_queue.contract.md:124` (`ResearchQueueService`) | `docs/02-15_04_Claude_Code_Master_Sprint_Plan_V1_0.md:399` (`ResearchQueue`) | Service contract vs local class naming + location mismatch. | Integration ambiguity for API wiring and tests. |

## 2.4 Terminology Reconciliation Needed (Priority)

| Priority | Decision Needed | Current Variants |
|---|---|---|
| P0 | Gap taxonomy single source of truth | `mediation/mechanism/...` vs `uncertain/unexplored/...` vs `missing_evidence/weak_support/...` |
| P0 | Template ID canonicalization | Full IDs vs shortened IDs; Panel II vs Panel III collision on Template 31 |
| P0 | Tier count and promotion policy | 8 fixed vs 9 (+Chrono) vs 10 (+MSI) |
| P1 | Pathway taxonomy | `subpersonal/personal_epistemic/mixed` vs `explicit/implicit_*` |
| P1 | Repo path conventions for implementation docs | `src/theory/*` vs actual `src/theories/*` + `src/data/theory_bootstrap.py` |
| P1 | Bridge epistemic fields | credence/entrenchment vs rank/warrant/grounding in cross-repo bridge contracts |

---

# SECTION 3: VARIABLE VOCABULARY AUDIT (Cross-Repo Unified)

## 3.1 Scan Scope and Artifact

Per request, vocabulary scan was executed across:

- `Article_Eater_PostQuinean_v1`
- `Article_Finder_v3_2_3` (current)
- `BN_graphical`
- `Tagging_Contractor`
- `Outcome_Contractor`

Unified table artifact (cross-repo):

- `docs/UNIFIED_VARIABLE_VOCAB_TABLE_CROSS_REPOS_2026-02-15.md`
- `docs/UNIFIED_VARIABLE_VOCAB_TABLE_CROSS_REPOS_2026-02-15.csv`

Scan summary:

- Semantic variable tokens: 4,320
- Cross-repo drift candidates (`repo_count >= 2`): 232

## 3.2 High-Risk Drift Clusters (Cross-Repo)

| Cluster | Variables Seen Across Repos | Repos | Risk |
|---|---|---|---|
| Effect statistics | `effect_size`, `p_value`, `ci_lower`, `ci_upper`, `confidence_interval` | AE + AF + BN_graphical + Outcome_Contractor | Same semantics, uneven field naming (`ci_*` vs `confidence_interval`). |
| Claim identity/classification | `claim_id`, `claim_type`, `evidence_type`, `effect_direction` | AE + AF + BN_graphical + Outcome_Contractor | Cross-system joins brittle when one side keys by `claim_type` and another by argument role/evidence kind. |
| Environmental and outcome payload | `environment_factors`, `boundary_conditions`, `enabling_conditions` | AE + AF + BN_graphical + Outcome_Contractor | Similar concepts appear with different granularity; conversion losses likely. |
| Epistemic confidence layer | `ae_confidence`, `credence*`, `rank*`, `warrant_status` | AE + BN_graphical (+ Outcome for some fields) | Mixed epistemic calculus vocab still coexists; bridge schemas can mis-map certainty semantics. |
| Pathway semantics | `personal_epistemic`, `implicit_cognitive`, `implicit_physiological` | Mostly AE now | Internal inconsistency; likely to leak into cross-repo exports. |

## 3.3 Canonical Variable List (Operational Recommendation)

### Environmental Features

- Canonical: `environment_factors`
- Supporting specific keys should live in controlled vocab lookups:
  - `contracts/vocab/environment_lookup.json` (AE)
  - Contractor-side mappings in Tagging/Outcome repos
- Drift to retire: free-text environment labels without lookup-backed IDs.

### Neural / Physiological

- Canonical: `effect_size`, `effect_size_type`, `p_value`, `ci_lower`, `ci_upper`
- Canonical stress axis terms for bridge layer: `cortisol`, `hpa_axis_activation` (if used), `stress_level`
- Drift to retire: mixed CI representations (`confidence_interval` object vs scalar bounds only).

### Psychological / Cognitive

- Canonical: `claim_type`, `effect_direction`, `boundary_conditions`, `enabling_conditions`
- Canonical pathway set (pick one and enforce):
  - Option A: `subpersonal`, `personal_epistemic`, `mixed`
  - Option B: `explicit`, `implicit_cognitive`, `implicit_physiological`, `mixed`
- Current state is mixed across docs and code.

### Behavioral / Outcome

- Canonical outcome field root: `outcome`
- Canonical outcome lookup location:
  - `contracts/outcome_vocab/outcome_lookup.json` (AE)
- Drift to retire: ad-hoc outcome labels not mapped to canonical lookup IDs.

## 3.4 Critical Recommendation for §3

Adopt one generated-source vocabulary contract and make all five repos consume it as build artifact. Until that is done, drift will continue every sprint.

---

# SECTION 4: TEMPLATE COMPLETENESS AUDIT (Templates 1-40)

## 4.1 Summary

Completeness criteria used (per prompt):

- Fully specified requires: structured causal chain, per-link bridging quality, per-link maturity, evidence, and scope conditions.

Results:

- Templates 1-20: 16/20 fully specified.
- Templates 21-30: 10/10 fully specified.
- Templates 31-40: 0/10 fully specified (narrative + params present, but missing bridging/evidence/scope schema fields).

## 4.2 Full Table

| Template ID | Name | Fully Specified? | Causal Chain Complete? | Params Given? | Scope Conditions? | Missing What? |
|---|---|---|---|---|---|---|
| 1 | PP_SPECTRAL_MATCH_001 | Yes | Yes | Yes | Yes | None |
| 2 | PP_COMPLEXITY_GOLDILOCKS_002 | Yes | Yes | No | Yes | None |
| 3 | SN_LAYOUT_COGNITIVE_MAP_001 | Yes | Yes | Yes | Yes | None |
| 4 | DT_ATTENTIONAL_DEMAND_001 | Yes | Yes | Yes | Yes | None |
| 5 | NM_THREAT_HPA_001 | Yes | Yes | Yes | Yes | None |
| 6 | NM_CORTISOL_HIPPOCAMPAL_005 | Yes | Yes | Yes | Yes | None |
| 7 | IC_ALLOSTATIC_ANTICIPATION_001 | Yes | Yes | Yes | Yes | None |
| 8 | EC_AFFORDANCE_POSTURAL_001 | Yes | Yes | Yes | Yes | None |
| 9 | DP_IMPLICIT_EVALUATION_001 | Yes | Yes | Yes | Yes | None |
| 10 | MS_CONSOLIDATION_RESTORATION_001 | Yes | Yes | Yes | Yes | None |
| 11 | NM_NORADRENERGIC_EXPLORE_006 | Yes | Yes | Yes | Yes | None |
| 12 | IC_INTEROCEPTIVE_AFFECT_CONSTRUCTION_001 | Yes | Yes | No | Yes | None |
| 13 | XF_NATURE_VIEW_MULTIPATH_001 | No | No | No | No | structured causal links, bridging quality per link, link-level evidence, scope conditions |
| 14 | XF_NAVIGATION_STRESS_VICIOUS_CYCLE_002 | No | No | No | No | structured causal links, bridging quality per link, link-level evidence, scope conditions |
| 15 | PP_CULTURAL_PRIOR_CALIBRATION_001 | Yes | Yes | Yes | Yes | None |
| 16 | DT_RESTORATION_TIMECOURSE_001 | No | No | Yes | No | bridging quality per link, link-level evidence, scope conditions |
| 17 | NM_DOPAMINERGIC_NOVELTY_REWARD_001 | Yes | Yes | No | Yes | None |
| 18 | EC_VESTIBULAR_SPATIAL_COGNITION_001 | Yes | Yes | No | Yes | None |
| 19 | XF_SOCIAL_AFFORDANCE_DENSITY_001 | Yes | Yes | Yes | Yes | None |
| 20 | XF_ENVIRONMENT_COGNITIVE_PERFORMANCE_001 | No | No | No | No | structured causal links, bridging quality per link, link-level evidence, scope conditions |
| 21 | PP_ACTIVE_INFERENCE_003 | Yes | Yes | Yes | Yes | None |
| 22 | PP_RAPID_GIST_004 | Yes | Yes | Yes | Yes | None |
| 23 | SN_CONTEXT_MEMORY_002 | Yes | Yes | Yes | Yes | None |
| 24 | SN_THETA_SEQUENCE_003 | Yes | Yes | Yes | Yes | None |
| 25 | MS_RIPPLE_REPLAY_002 | Yes | Yes | Yes | Yes | None |
| 26 | NM_CHOLINERGIC_GATING_007 | Yes | Yes | Yes | Yes | None |
| 27 | DT_DMN_MAINTENANCE_002 | Yes | Yes | No | Yes | None |
| 28 | EC_COGNITIVE_OFFLOADING_002 | Yes | Yes | No | Yes | None |
| 29 | ALLOSTATIC_MASTER_001 | Yes | Yes | Yes | Yes | None |
| 30 | CHRONO_LIGHT_ENTRAINMENT_001 | Yes | Yes | Yes | Yes | None |
| 31 | AUD_SCENE_ANALYSIS_001 | No | No | Yes | No | bridging quality per link, link-level evidence, scope conditions |
| 32 | AUD_SUBCORTICAL_ENCODING_002 | No | No | Yes | No | bridging quality per link, link-level evidence, scope conditions |
| 33 | AUD_REVERBERATION_SPACE_003 | No | No | Yes | No | bridging quality per link, link-level evidence, scope conditions |
| 34 | HAP_SURFACE_MATERIAL_001 | No | No | Yes | No | bridging quality per link, link-level evidence, scope conditions |
| 35 | OLF_CONTEXT_AFFECT_001 | No | No | Yes | No | bridging quality per link, link-level evidence, scope conditions |
| 36 | HC_WORKING_MEMORY_LOAD_001 | No | No | Yes | No | bridging quality per link, link-level evidence, scope conditions |
| 37 | ER_ECOLOGICAL_RATIONALITY_001 | No | No | Yes | No | bridging quality per link, link-level evidence, scope conditions |
| 38 | HC_HIERARCHICAL_CONTROL_002 | No | No | Yes | No | bridging quality per link, link-level evidence, scope conditions |
| 39 | MSI_CONGRUENCY_PRINCIPLE_001 | No | No | Yes | No | bridging quality per link, link-level evidence, scope conditions |
| 40 | MSI_INVERSE_EFFECTIVENESS_002 | No | No | Yes | No | bridging quality per link, link-level evidence, scope conditions |

## 4.3 Practical Consequence

Templates 31-40 are useful scientific notes but not production-ready mechanistic templates. They cannot be consumed safely by automated CMR tracing until encoded in a strict schema.

---

# SECTION 7: MULTI-REPO AUDIT (All 5 Repositories)

## 7.1 Repository Overview

| Repo | Purpose | Files | Tests | Status |
|------|---------|-------|-------|--------|
| **Article_Eater_PostQuinean_v1** | Epistemic extraction + web of belief | ~200 .py | 96 files | Tests BROKEN (12 collection errors) |
| **Article_Finder_v3_2_3** | PDF discovery + retrieval + Zotero | 13,496 files | 2,828 test files | Tests not run (large) |
| **BN_graphical** | Bayesian network + causal inference | 28,629 files | 8,811 tests | Tests FAIL (5 errors, venv needed) |
| **Tagging_Contractor** | Image feature extraction (environment side) | 520 .py | 6 tests | Minimal test coverage |
| **Outcome_Contractor** | Outcome vocabulary (human side) | 2,057 files | 35 tests | Tests FAIL (4 errors, missing yaml) |

## 7.2 Integration Contracts Status

| Contract | Location | Producers | Consumers | Status |
|----------|----------|-----------|-----------|--------|
| `ae.paper.v1` | AF `schemas/` | Article_Finder | Article_Eater | ✓ IMPLEMENTED in `eater_interface/job_bundle_v2.py` |
| `ae_bn_bridge.v1` | BN `contracts/` | Article_Eater | BN_graphical | ✓ IMPLEMENTED in `src/coherence/epistemic_adapter.py` |
| `localized_image_tags.v0.1` | TC `contracts/` | Tagging_Contractor | BN_graphical | ✓ SCHEMA EXISTS |
| `core.v1` | OC `contracts/` | Outcome_Contractor | All | ✓ FROZEN CONTRACT |
| `research_queue.v1` | AE `contracts/` | GapPredictor | VOI Collectors | ⚠ CONTRACT ONLY — no implementation |

## 7.3 Cross-Repo Data Flow (Actual)

```
                          ARTICLE DISCOVERY
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    Article_Finder_v3_2_3                                │
│  ┌────────────┐    ┌────────────┐    ┌──────────────────┐              │
│  │ Semantic   │    │ PubMed     │    │ Zotero           │              │
│  │ Scholar    │───>│ OpenAlex   │───>│ Integration      │              │
│  │ Search     │    │ CrossRef   │    │ (uni library)    │              │
│  └────────────┘    └────────────┘    └────────┬─────────┘              │
│                                               │                         │
│  Produces: ae.paper.v1 bundles (paper.json + PDF)                       │
└───────────────────────────────────────────────┼─────────────────────────┘
                                                │
                          ┌─────────────────────┼─────────────────────┐
                          │                     │                     │
                          ▼                     ▼                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    Article_Eater_PostQuinean_v1                         │
│  ┌────────────┐    ┌────────────┐    ┌──────────────────┐              │
│  │ PDF        │    │ Claim      │    │ Web of Belief    │              │
│  │ Extraction │───>│ Extraction │───>│ (Coherence)      │              │
│  └────────────┘    └────────────┘    └────────┬─────────┘              │
│                                               │                         │
│  Produces: Beliefs, Constraints, Rules, Gap Predictions                 │
└───────────────────────────────────────────────┼─────────────────────────┘
                                                │
                          ┌─────────────────────┼─────────────────────┐
                          │                     │                     │
                          ▼                     ▼                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        BN_graphical                                      │
│  ┌────────────┐    ┌────────────┐    ┌──────────────────┐              │
│  │ Epistemic  │    │ Statistical│    │ Intervention     │              │
│  │ Adapter    │◄──>│ Engine     │───>│ Prediction       │              │
│  │ (v1/v2)    │    │ (PyMC)     │    │ (do-calculus)    │              │
│  └────────────┘    └────────────┘    └──────────────────┘              │
│                                                                         │
│  Consumes: ae_bn_bridge.v1 from AE                                      │
│  Consumes: localized_image_tags from TC                                 │
│  Consumes: outcome terms from OC                                        │
└─────────────────────────────────────────────────────────────────────────┘
                          ▲                     ▲
                          │                     │
        ┌─────────────────┘                     └─────────────────┐
        │                                                         │
┌───────┴───────────────┐                       ┌─────────────────┴─────┐
│  Tagging_Contractor   │                       │  Outcome_Contractor   │
│  (Environment side)   │                       │  (Human side)         │
│                       │                       │                       │
│  Image → Features     │                       │  Outcome vocabulary   │
│  - Semantic regions   │                       │  - 7 domains          │
│  - Dense maps         │                       │  - Hierarchical       │
│  - Global attributes  │                       │  - Frozen contract    │
└───────────────────────┘                       └───────────────────────┘
```

## 7.4 Cross-Repo Integration Issues

| Issue | Repos Affected | Severity | Details |
|-------|---------------|----------|---------|
| **Epistemic format mismatch** | AE ↔ BN | MEDIUM | AE uses credence/entrenchment (v1), BN has dual-format adapter but v2 (rank/warrant) not populated in AE |
| **GapType taxonomy divergence** | AE only | HIGH | 4 different GapType enums in AE codebase (gap_predictor, voi_search, discovery_funnel, Sprint 6 spec) |
| **Test suite failures** | AE, BN, OC | HIGH | 3 of 5 repos have broken test suites |
| **Missing queue implementation** | AE → AF | HIGH | `ResearchQueueService` contract exists but no code bridges GapPredictor to AF search |
| **Pathway taxonomy conflict** | AE docs | MEDIUM | `EXPLICIT/IMPLICIT_*` vs `SUBPERSONAL/PERSONAL_EPISTEMIC` |

## 7.5 Per-Repo Test Status

### Article_Eater_PostQuinean_v1
```
Tests: 96 files, BROKEN
Errors: 12 collection errors (import failures)
Blocking: test_api_*, test_full_integration, test_voi_search, etc.
```

### BN_graphical
```
Tests: 879 collected, 5 errors
Errors: ModuleNotFoundError for pymc (requires bn_venv activation)
Fix: source bn_venv/bin/activate && pytest
```

### Outcome_Contractor
```
Tests: 35 files, 4 collection errors
Errors: ModuleNotFoundError: No module named 'yaml'
Fix: pip install pyyaml
```

### Tagging_Contractor
```
Tests: 6 test files only
Status: Minimal coverage
```

### Article_Finder_v3_2_3
```
Tests: 2,828 test files
Status: Not run (large codebase)
```

## 7.6 Cross-Repo Recommendations

### Priority 0 (Immediate)

1. **Fix test suites** in AE, BN, OC before any feature work
2. **Reconcile GapType** taxonomy — pick one and enforce across all services
3. **Document activation requirements** — BN requires `bn_venv`, OC needs `pyyaml`

### Priority 1 (Short-term)

4. **Implement ResearchQueueService** — bridge GapPredictor to Article_Finder
5. **Populate v2 epistemic fields** in AE for full BN bridge compatibility
6. **Add test coverage** to Tagging_Contractor (only 6 tests for 520 files)

### Priority 2 (Medium-term)

7. **Unify pathway taxonomy** — decide EXPLICIT/IMPLICIT vs SUBPERSONAL/PERSONAL
8. **Implement CMR pipeline** — currently docs-only, no code
9. **Create cross-repo integration tests** — verify AE→AF and AE→BN data flows

---

*Multi-repo audit completed: 2026-02-15*
*Scope: Article_Eater, Article_Finder, BN_graphical, Tagging_Contractor, Outcome_Contractor*

