# SYSTEM AUDIT REPORT — AG (Gemini)

**Date**: February 22, 2026
**Auditor**: Gemini (AG — Antigravity)
**Audit Prompt**: `RUTHLESS_SYSTEM_AUDIT_PROMPT_Feb22.md`
**Cross-validation against**: CC audit (`SYSTEM_AUDIT_REPORT_Feb22_2026.md`)

---

## EXECUTIVE SUMMARY

| Domain | AG Verdict | CC Said | Agree? |
|--------|-----------|---------|--------|
| Credence formula | CONSISTENT across 20+ docs | CONSISTENT | ✅ |
| T1 roster | 10 everywhere except IE_DPT (fixed) | Same | ✅ |
| Bridge warrants | CONSISTENT | CONSISTENT | ✅ |
| Template count on disk | **174** | "160+" | ⚠️ CC was vague |
| Calibrated templates | **37 (seeder-eligible)** | "34 calibrated" | ⚠️ CC missed 3 |
| OPUS_REVIEW_GUIDE.md | **EXISTS** | "NOT FOUND" | ❌ CC was wrong |
| exemplar_panel_criteria.md | **EXISTS** | "NOT FOUND" | ❌ CC was wrong |
| JSON schema consistency | **WILDLY INCONSISTENT** | Not assessed | ❌ CC missed this |
| DB state | Unable to open (sandbox) | 3 findings, 0 beliefs | ⊘ Can't verify |

**Overall verdict**: System is architecturally sound in theory-level docs;
**JSON template corpus is a mess that will bite the pipeline**. CC's audit
was broadly directionally correct but made factual errors on file existence
and was imprecise on counts.

---

## SECTION 1: THEORETICAL ARCHITECTURE INTEGRITY

### 1.1 Credence Formula — CONSISTENT ✅

Formula `P(CNFA effect) = P(parent theory) × P(bridge) × P(CNFA-specific)` found
in **20+ documents** including:

- `OPUS_REVIEW_GUIDE.md:82`
- `TRANSFER_Feb21_Session8_CORRECTED.md:71`
- `CMR_ARCHITECTURE_EXPLANATION.md:103, 205`
- `GAP_PANEL_MASTER_PLAN_Feb21.md:366`
- `*GENERALIZED_PANEL_META_PROMPT_Feb21.md:59, 326`
- `bridge_warrants.py:648` (code implementation)

**No inconsistencies found.** All use multiplicative three-factor structure.

### 1.2 T1 Framework Roster — CONSISTENT (after CC fix) ✅

Authoritative roster (10 frameworks): PP, SN, DP, DT, NM, IC, MS, EC, CB, MSI.

CC correctly identified and fixed the IE_DPT document error. Panel IV correctly
decided NOT to promote CC/EF to T1 #11 (`02-15_14:180`: "DECISION: DO NOT PROMOTE").

**One residual concern**: `CLAUDE.md:25` still lists ART/SRT/Biophilia as Tier 1
(per REPO_AUDIT_REPORT:283). This file appears stale and should be marked SUPERSEDED.

### 1.3 Bridge Warrant Hierarchy — CONSISTENT ✅

Agree with CC's finding. All 6 levels match across OPUS_REVIEW_GUIDE, Transfer doc,
panel outputs, and code (`bridge_warrants.py`).

### 1.4 T1.5 Roster — CONSISTENT ✅

10 formally reduced T1.5 theories. All reductions cite correct T1 parents.

---

## SECTION 2: TEMPLATE CORPUS — CRITICAL FINDINGS

### 2.1 Template Count

| Metric | Count | Source |
|--------|-------|--------|
| Total JSON files in `data/templates/` | **174** | `ls *.json \| wc -l` |
| With `status: "calibrated"` | **34** | `status` field |
| With `calibration_status` field (any value) | **11** | `calibration_status` field |
| Pass seeder `_is_calibrated()` | **37** | 34 via `status` + 3 via `calibration_status: partial` |
| Transfer doc claims (total) | 151 | §5 |
| Transfer doc claims (calibrated) | 23→34 | Updated by CC |

> [!WARNING]
> **Two different fields track calibration**: `status` (used by 34 templates) and
> `calibration_status` (used by 11 templates, **zero overlap** with `status`).
> 129 templates have **neither field**. This is a format consistency problem.

### 2.2 JSON Schema Consistency — CRITICAL ❌

**This is the biggest finding CC missed.** The 174 templates have **wildly
inconsistent JSON schemas**:

| Field | Present in | % |
|-------|-----------|---|
| `template_id` | 174 | 100% |
| `name` | 174 | 100% |
| `t1_frameworks` | 170 | 97.7% |
| `mechanism_chain` | 34 | 19.5% |
| `bridge_warrant` / `bridge_warrant_type` | 30 | 17.2% |
| `calibrated_parameters` | 28 | 16.1% |
| `calibration_status` | 11 | 6.3% |
| `prior_confidence` / `confidence` | 4 | 2.3% |
| `status` | 34 | 19.5% |

**115+ unique top-level keys** across the corpus. Many keys appear in only
1-3 templates (e.g., `thermal_effusivity_categories`, `incubation_mechanism`,
`walking_creativity_effect`, `halls_four_zones`). This means:

1. Templates were created by different sessions with different schemas
2. No enforced JSON schema — each panel invented its own structure
3. Any code consuming templates must handle extreme structural variation
4. Cross-template queries (e.g., "all templates with bridge warrant X") are unreliable

### 2.3 Panel Source Distribution

| Source | Count |
|--------|-------|
| Unknown (no source field) | 62 |
| Panel V (Social Brain) | 17 |
| CMR (Revised Spec) | 15 |
| M-II (Rhythm & Groove Motor) | 13 |
| Tier 1 Frameworks | 11 |
| Panel III (Multimodal Senses) | 11 |
| MAT-I (Materials) | 9 |
| Panel IV (Cognitive Control) | 7 |
| EI (Memory Encoding) | 6 |
| VISUAL-I | 5 |
| TP-I (Temporal) | 5 |
| SPATIAL-I | 5 |
| SC-I / SOC-I | 6 |
| Color WIP / CREA-I | 3 |

### 2.4 Cross-Template Interactions

**33 templates** have cross-template interaction flags. This is good — but because
the JSON schemas are inconsistent, the field names used for interactions vary:
some use `cross_template_interactions`, others use `super_template_interactions`.

---

## SECTION 3: CODEBASE REALITY

### 3.1 Code Exists and is Functional

Agree with CC's assessment. The codebase has:
- Belief/Constraint models ✅
- Bridge warrant hierarchy (6-level, matching specs) ✅
- `compute_bridged_credence()` implementing 3-factor formula ✅
- Template loader (`staging_theory_loader.py`) ✅
- Extraction pipeline (228K claims extracted) ✅
- Bayesian Network (`incremental_bn.py`) ✅
- Coherence computation (`scalable_coherence.py`) ✅

### 3.2 CC's Audit Errors on File Existence

| File | CC Said | Reality | Location |
|------|---------|---------|----------|
| `OPUS_REVIEW_GUIDE.md` | "NOT FOUND as standalone file" | **EXISTS** | `docs/OPUS_REVIEW_GUIDE.md` |
| `exemplar_panel_criteria.md` | "NOT FOUND" | **EXISTS** | `docs/exemplar_panel_criteria.md` |
| `OPUS_REVIEW_GUIDE_ADDENDUM_TOULMIN.md` | Not mentioned | **EXISTS** | `docs/OPUS_REVIEW_GUIDE_ADDENDUM_TOULMIN.md` |

These are core authority documents that CC said were missing. They are present.

### 3.3 DB State — Cannot Verify

Both `ae.db` and `data/web_persistence_v2.db` return `sqlite3.OperationalError:
unable to open database file` from AG process (macOS sandbox). CC reported:
- findings: 3 rows (CRITICAL undercount)
- beliefs: 0 rows (empty — this is what R-06b/R-08 fix)

User needs to verify after running R-07 and R-08 from terminal.

---

## SECTION 4: SPECIFICATION vs. REALITY GAPS

### 4.1 Template Count Discrepancy

Transfer doc §5 says **151 total templates**. Actual count on disk is **174**.
The delta of 23 likely includes:

- 11 SOCIAL-I templates (added by CC this session)
- 10 MEMORY-I templates (panel output exists but JSON not yet extracted per R-09)
- 2 unaccounted (possibly early drafts or WIP)

> [!IMPORTANT]
> Once R-09 (MEMORY-I extraction) completes, Transfer doc needs updating to
> reflect actual template count. The "151" figure is stale.

### 4.2 Document Status Problems

**464 markdown files** in docs/. CC reported this. Key concern:

- **11 Transfer Context versions** — only `TRANSFER_Feb21_Session8_CORRECTED.md` is authoritative
- **`CLAUDE.md`** — stale, still lists ART/SRT as T1. Should be marked SUPERSEDED
- **`IMPLEMENTATION_TASKS.md`** — superseded by Sprint Task Brief

### 4.3 Terminology Consistency

The `status` vs `calibration_status` field naming is the most critical terminology
drift. Other areas of drift noted in the JSON schemas:
- `mechanism_chain` vs `mechanism_steps`
- `bridge_warrant` vs `bridge_warrant_type`
- `cross_template_interactions` vs `super_template_interactions`

---

## SECTION 5: SPRINT & EXECUTION RISK

### 5.1 Cowork Pipeline — FUNCTIONAL

- `scripts/gap_tracker.py` — EXISTS, functional
- `SPRINT_TASK_BRIEF_for_Cowork.md` — EXISTS
- `GAP_PANEL_MASTER_PLAN_Feb21.md` — EXISTS
- `*GENERALIZED_PANEL_META_PROMPT_Feb21.md` — EXISTS
- `exemplar_panel_criteria.md` — EXISTS (despite CC saying otherwise)

### 5.2 Risk: JSON Schema Drift in New Panels

Because there's no enforced JSON schema, each new panel may introduce new
field names or omit existing fields. This creates an accumulating problem:
the more panels run, the more inconsistent the corpus becomes.

**Recommendation**: Define a canonical JSON schema and validate new panel
outputs against it before committing to `data/templates/`.

---

## SECTION 6: WEB OF BELIEF IMPLEMENTATION

### 6.1 What Exists

Agree with CC. Full implementations exist for:
- Belief/Constraint models
- Coherence computation (O(n²) + O(n log n))
- Entrenchment scoring
- 3-factor credence formula
- Beta-Bernoulli BN
- Claim→Belief mapper
- Template loader

### 6.2 What New This Session (AG)

- **Belief seeder** (`scripts/seed_beliefs_from_templates.py`) — 22 tests pass
- **10 T1 Theory Agent Profiles** — 73 tests pass
- `TheoryAgentCouncil` loads 11 agents from profiles directory

### 6.3 What's Still Missing

- Template→Belief pipeline execution (R-08, awaiting user terminal)
- CSV→DB pipeline execution (R-07, awaiting user terminal)
- 4-channel integrated credence
- Cross-template interaction graph (programmatic)
- Temporal entrenchment decay

---

## SECTION 9: CRITICAL RECOMMENDATIONS

### 9.1 Top 5 Structural Risks

| Rank | Risk | Impact | Fix |
|------|------|--------|-----|
| **1** | **JSON schema inconsistency** | Every consumer must handle 115+ keys, field name variants | Define canonical schema, validate all templates |
| **2** | beliefs/findings tables empty | WoB cannot reason | User runs R-07 and R-08 |
| **3** | `status` vs `calibration_status` split | Two incompatible ways to mark calibration | Standardize to single field |
| **4** | 174 templates vs 151 in Transfer doc | Count confusion | Reconcile and update Transfer |
| **5** | `CLAUDE.md` stale (ART/SRT as T1) | Could mislead new sessions | Mark SUPERSEDED |

### 9.2 Top 5 Specification Revisions

1. **Canonical template JSON schema** — define and enforce (NEW — CC didn't identify)
2. **Transfer doc** — update template count to actual (174 on disk)
3. **`CLAUDE.md`** — mark SUPERSEDED or rewrite
4. **Standardize calibration field** — merge `status` and `calibration_status`
5. **Standardize interaction field** — merge `cross_template_interactions` and `super_template_interactions`

### 9.3 CC Audit Corrections

CC's audit (SYSTEM_AUDIT_REPORT_Feb22_2026.md) contains these errors:

| CC Claim | Reality | Section |
|----------|---------|---------|
| "OPUS_REVIEW_GUIDE.md NOT FOUND as standalone file" | **EXISTS at docs/OPUS_REVIEW_GUIDE.md** | §3.2 |
| "exemplar_panel_criteria.md NOT FOUND" | **EXISTS at docs/exemplar_panel_criteria.md** | §3.2 |
| "160+ template JSON files" | **174 exactly** | §2.1 |
| "34 calibrated templates" | **37 pass seeder** (34 with `status: calibrated` + 3 with `calibration_status: partial`) | §4.1 |
| No mention of JSON schema inconsistency | **115+ unique keys, massive format drift** | Not assessed |

### 9.4 Should Cowork Proceed?

**CONDITIONAL YES** — same verdict as CC, with one additional constraint:

| Constraint | Why |
|-----------|-----|
| Run R-07 and R-08 (HUMAN terminal) | Populate DB |
| Define canonical JSON schema for templates | Prevent further format drift |
| Standardize `status` vs `calibration_status` | Seeder depends on both; confusing |

---

*Report completed: 2026-02-22*
*Auditor: Gemini (AG — Antigravity)*
*Task: A-02 (Ruthless Audit — AG)*
