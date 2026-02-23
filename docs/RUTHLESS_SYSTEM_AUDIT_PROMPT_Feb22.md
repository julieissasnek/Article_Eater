# RUTHLESS SYSTEM AUDIT PROMPT — CMR / ARTICLE EATER
## Full Reality Check — Theoretical Architecture + Codebase
## February 22, 2026
## Run in: CC, then AG/Gemini, then AG/Codex. Cross-validate findings.

---

# CONTEXT

This project has two interlocking components:

1. **The CMR theoretical architecture**: a compositional mechanistic reasoning
   framework with 10 T1 frameworks, 10+ T1.5 domain theories, 151 templates
   across 12 panels, a bridge warrant hierarchy, a credence formula, and a
   calibration method using virtual expert panels. 23 templates have been
   calibrated across 4 completed panels (STRESS-I, LIGHT-I, SPATIAL-I,
   VISUAL-I). 8 panels remain. An autonomous Cowork pipeline is about to
   execute the remaining panels.

2. **The Article Eater codebase**: a computational system that is supposed to
   ingest research papers, extract mechanism claims, assign them to templates,
   and compute calibrated credence scores. This codebase existed before the
   theoretical architecture was fully developed and may or may not match it.

Both surfaces must be audited. Misalignment between them — where the specs
describe structures the code can't consume, or the code implements structures
the specs have superseded — is the primary risk.

**Do not be polite. Do not soften findings. Cite file paths and line numbers.
Quote conflicting passages verbatim. This audit is the last chance to catch
structural problems before 128 more templates are calibrated.**

---

# SECTION 1: THEORETICAL ARCHITECTURE INTEGRITY

## 1.1 Core Credence Formula Consistency

The formula is: `P(CNFA effect) = P(parent theory) × P(bridge) × P(CNFA-specific)`

Search every document in `docs/` for references to this formula or its components.
Report:

- Is the formula stated consistently everywhere it appears?
- Are there any documents that use a DIFFERENT credence computation?
- Are there any documents that add terms, use additive combination, or modify
  the three-factor structure?
- Are there any templates in the calibrated panel outputs that compute credence
  in a way that doesn't match this formula?

## 1.2 T1 Roster Consistency

The AUTHORITATIVE T1 roster is in `TRANSFER_Feb21_Session8_CORRECTED.md` §2.1.
It contains exactly 10 frameworks. Search EVERY document in the repo for any
reference to T1 theories, Tier 1 frameworks, or foundational theories.

Report as a table:

| Document | T1 count stated | Includes ART/SRT as T1? | Includes IE-DPT as T1 #11? | Other discrepancies |
|----------|----------------|------------------------|---------------------------|-------------------|

Known errors to check for:
- ART and SRT listed as T1 (they are T1.5)
- IE-DPT listed as T1 #11 (it is an elevation of T1 #3; count remains 10)
- 02-20_10 panel briefing has incorrect T1 roster
- IE_DPT_Full_T1_Specification.md Part V uses pre-Feb 14 roster

Flag every document that disagrees with the authoritative roster.

## 1.3 T1.5 Roster Consistency

The AUTHORITATIVE T1.5 roster is in `TRANSFER_Feb21_Session8_CORRECTED.md` §2.2.
10 formally reduced + 1 pending candidate (Aesthetic Anchoring) + 8 unidentified
candidates.

- Do all formal reductions cite the same T1 parent frameworks consistently?
- Does the T1_5_Three_New_Reductions document's reductions match the Transfer doc?
- Are there any T1.5 theories referenced in panel outputs that aren't in the roster?
- Does any document count more or fewer than 10 formally reduced T1.5 theories?

## 1.4 Bridge Warrant Hierarchy Consistency

The AUTHORITATIVE hierarchy is in both `OPUS_REVIEW_GUIDE.md` §1 and
`TRANSFER_Feb21_Session8_CORRECTED.md` §2.3.

Search every document and every calibrated panel output for bridge warrant
assignments. Report:

| Warrant Type | Prior P (OPUS Guide) | Prior P (Transfer) | Prior P (used in panel outputs) | Consistent? |
|-------------|---------------------|-------------------|-------------------------------|-------------|
| CONSTITUTIVE | | | | |
| MECHANISM | | | | |
| EMPIRICAL_COVARIANCE | | | | |
| FUNCTIONAL | | | | |
| CAPACITY | | | | |
| ANALOGICAL | | | | |

Then check: in every calibrated template JSON across all panel outputs, does the
confidence score respect the bridge warrant ceiling? Flag every violation.

## 1.5 Template Count Reconciliation

The Transfer doc §5 says 151 total, 23 calibrated, 128 remaining.

- Count every unique template ID across all panel outputs and all specification
  documents. Is the actual count 151?
- Are there template IDs in the gap registry that don't appear in any spec?
- Are there template IDs in the specs that aren't in the gap registry?
- Are there duplicate template IDs (same ID, different content)?
- Does 23 calibrated actually check out? Count every template with `"status": "calibrated"` across all panel output files.

## 1.6 Panel Output Structural Compliance

For each completed panel output (STRESS-I, LIGHT-I, SPATIAL-I, VISUAL-I),
check against `OPUS_REVIEW_GUIDE.md` §4 mandatory outputs:

| Requirement | STRESS-I | LIGHT-I | SPATIAL-I | VISUAL-I |
|-------------|---------|---------|----------|---------|
| Calibrated JSON with all fields | | | | |
| Confidence score for every scalar | | | | |
| Bridge warrant for every scalar | | | | |
| Population modifiers where relevant | | | | |
| Architectural modifier coefficients | | | | |
| IC2 interaction statement per template | | | | |
| AX4 interaction statement per template | | | | |
| RESIDUAL GAPS section | | | | |
| THEORETICAL_DEFAULT flags on scores < 0.50 | | | | |
| CROSS_TEMPLATE_INTERACTION flags | | | | |
| CMR integration note | | | | |
| APA references with DOIs | | | | |

Mark each cell: PRESENT / PARTIAL (what's missing) / ABSENT.

Flag any panel output that was produced before the OPUS_REVIEW_GUIDE existed
and therefore may not comply with rules that were defined after it was written.
STRESS-I and LIGHT-I are the most likely to have this problem.

## 1.7 Cross-Template Interaction Accounting

VISUAL-I generated 12 cross-template flags. Each was assigned to a target panel.

- List every cross-template flag from every completed panel output.
- For each flag, confirm: is the target panel aware of it? Does the target
  panel's sprint entry in the Sprint Task Brief reference it?
- Are there any orphaned flags — assigned to a panel but not mentioned in
  that panel's input files or sprint entry?
- Are there any circular dependencies — panel A flags something for panel B,
  which flags something back for panel A?

---

# SECTION 2: CODEBASE REALITY MAP

## 2.1 What Actually Exists

For EACH of the following, report: **EXISTS (path)** or **DOES NOT EXIST** or
**PARTIAL (path, what's missing)**.

**Data Models / Schemas:**
- [ ] Node model (claims, beliefs) — fields, path
- [ ] Edge/Link model — fields, path
- [ ] Bridge warrant model or enum — does it match the 6-level hierarchy?
- [ ] Theory/framework model — does it represent T1/T1.5/T2 tiers?
- [ ] Template/mechanism model — can it represent the calibrated JSON format?
- [ ] Confidence score model — does it support the scoring discipline?
- [ ] Population modifier model
- [ ] ResearchTarget or gap/queue model
- [ ] Any existing credence computation code

**Extraction Pipeline:**
- [ ] PDF extraction — tool, status
- [ ] Claim extraction — method, prompt/template
- [ ] Metadata extraction
- [ ] Method identification
- [ ] Source quality scoring

**Inference / Reasoning:**
- [ ] Bayesian Network assembly — library, graph structure
- [ ] Coherence / constraint satisfaction
- [ ] Entrenchment scoring
- [ ] CMR or prediction generation code
- [ ] Gap detection / gap predictor

**Data / Artifacts:**
- [ ] Papers processed — count, location, format
- [ ] Extracted claims — count, format
- [ ] Database(s) — type, schema
- [ ] Test fixtures / corpora

**Infrastructure:**
- [ ] Project structure (monorepo? multiple repos?)
- [ ] Language versions, key dependencies
- [ ] Test framework, test count, pass/fail
- [ ] CI/CD, Docker, deployment config

## 2.2 Architecture Diagram

Draw the ACTUAL data flow as it exists today:
```
Paper PDF → [what] → [what] → [what] → stored where?
```
Then draw the data flow the specs describe. Show the gap.

## 2.3 Can the Code Consume the Panel Outputs?

This is the critical new question. The panel calibration process produces
calibrated JSON (see VISUAL-I Output Block 1 for the format). The Article
Eater is supposed to ingest this.

- Can the current codebase parse the calibrated JSON format from VISUAL-I?
- Does the data model have fields for: mechanism_chain, bridge_warrant,
  confidence, population_modifiers, architectural_modifiers, IC2_interaction,
  AX4_interaction, cross_template_flags?
- If not, what would need to be added/changed?
- Are there ANY integration points between the calibrated panel outputs and
  the codebase, or are they currently disconnected artifacts?

---

# SECTION 3: SPECIFICATION vs. REALITY GAPS

## 3.1 Document Inventory

List every document in `docs/` with: filename, date, stated purpose, and
whether it is CURRENT or SUPERSEDED. Flag documents that have been superseded
but not marked as such.

The following documents are known to exist or should exist. For each, report
whether it is present, current, and internally consistent:

| Document | Purpose | Expected Status |
|----------|---------|----------------|
| `TRANSFER_Feb21_Session8_CORRECTED.md` | Authoritative project state | CURRENT — primary authority |
| `GAP_PANEL_MASTER_PLAN_Feb21.md` | Panel sequence and template targets | CURRENT — primary authority |
| `OPUS_REVIEW_GUIDE.md` | Calibration discipline rules | CURRENT — primary authority |
| `SPRINT_TASK_BRIEF_for_Cowork.md` | Autonomous execution orders | CURRENT — primary authority |
| `exemplar_panel_criteria.md` | Style authority for panel outputs | CURRENT |
| `_GENERALIZED_PANEL_META_PROMPT_Feb21.md` | Panel prompt template | CURRENT |
| `02-14_07_Theory_Tier_Architecture_V1_0.md` | Tier structure rationale | Check if superseded by Transfer doc |
| `02-14_08_Compositional_Mechanistic_Reasoning_Spec_V1_0.md` | Original CMR spec | Check if superseded |
| `02-14_09_CMR_Revised_Spec_Panel_Templates_V2_0.md` | Templates 1-18 | Check if superseded by panel outputs |
| `02-15_02_Neuroscience_Panel_Templates_and_Taxonomy_V1_0.md` | Templates 21-30 | Check if superseded |
| `IE_DPT_Full_T1_Specification.md` | IE-DPT specification | CONTAINS ERRORS 1-3 |
| `T1_5_Three_New_Reductions_SpaceSyntax_Soundscape_PlaceAttachment.md` | T1.5 reductions | CURRENT |
| `STRESS_I_Panel_Output_Feb21.md` | STRESS-I calibrated output | Check format compliance |
| `LIGHT_I_Panel_Output_Feb21.md` | LIGHT-I calibrated output | Check format compliance |
| `SPATIAL_I_Panel_Output_Feb21.md` | SPATIAL-I calibrated output | Check format compliance |
| `VISUAL_I_Panel_Output_Feb21.md` | VISUAL-I calibrated output | Check format compliance |
| `CLAUDE.md` | Overall architecture (old) | Likely SUPERSEDED |
| `IMPLEMENTATION_TASKS.md` | Sprint plan (old) | Likely SUPERSEDED by Sprint Task Brief |
| `cross_repo_contract_v2.md` | Software protocol | Check status |
| Any other documents found | | Report |

Flag any document that is referenced by another document but does not exist
in the repo. Flag any document that exists but is referenced by nothing.

## 3.2 Specification-Code Alignment

For each specification document, report:

| Document | Implementation % | Stale Assumptions | Contradictions |
|----------|-----------------|-------------------|----------------|

## 3.3 Cross-Document Terminology Audit

This remains critical. The project has been developed across many Claude
sessions with terminology drift. Find every case where:

- Same concept, different names in different documents
- Same name, different meanings in different documents
- Concept defined in one doc, referenced differently in another

Particular areas of known drift:
- Tier numbering
- Template ID formats (T1, T2, T6, T7, T14, T22, etc. vs. PP_SPECTRAL_MATCH_001)
- Bridge warrant names (has the vocabulary been consistent across sessions?)
- Effect pathway terminology
- Maturity level labels
- Gap severity taxonomy
- Variable names in mechanism chains

## 3.4 The IE-DPT Document Problem

`IE_DPT_Full_T1_Specification.md` contains known Errors 1-3 (see Transfer doc §4).
Has any code or any other document consumed the incorrect content from this file?
Has any panel output cited it as authority? If the errors have propagated, trace
the propagation path.

## 3.5 Variable Vocabulary Audit

This is critical. 23 calibrated templates now produce JSON with hundreds of
variable names in mechanism chains, parameter fields, and modifier coefficients.
These variables must be consistent across templates and consumable by code.

Search across ALL specification documents, ALL calibrated panel outputs, and
ALL code for every variable name used in:
- Mechanistic template causal chains (the `from` and `to` fields in mechanism steps)
- Calibrated parameter names and units
- Population modifier variable names
- Architectural modifier variable names
- BN node definitions (if any exist in code)
- Extraction pipeline outputs (if any exist)

Produce a **canonical variable inventory** organized by domain:

```
ENVIRONMENTAL / ARCHITECTURAL FEATURES:
- [every variable name found, with source file and template ID]
- Flag synonyms (same feature, different names across templates)
- Flag conflicts (same name, different features)

NEURAL / PHYSIOLOGICAL INTERMEDIARIES:
- [every variable name]
- Flag synonyms and conflicts

PSYCHOLOGICAL / COGNITIVE STATES:
- [every variable name]

BEHAVIORAL / OUTCOME MEASURES:
- [every variable name]

POPULATION MODIFIERS:
- [every variable name — age, clinical status, expertise, etc.]

ARCHITECTURAL MODIFIERS:
- [every variable name — building type, occupancy, etc.]
```

For each cluster of synonyms, recommend a canonical name.

Pay particular attention to variables that appear in CROSS_TEMPLATE_INTERACTION
flags — these variables MUST be named identically across the templates that
share them, or the Article Eater cannot compute joint effects.

---

# SECTION 4: TEMPLATE COMPLETENESS AUDIT

## 4.1 Calibrated Templates (23)

For each of the 23 calibrated templates, verify:

| Template ID | Panel | Mechanism chain complete? | All params have confidence? | Bridge warrant assigned? | THEORETICAL_DEFAULT flags present where needed? | Residual gaps specified? |
|-------------|-------|--------------------------|---------------------------|------------------------|-----------------------------------------------|------------------------|

## 4.2 Uncalibrated Templates (128)

How many of the 128 remaining templates have:
- A structural scaffold (template ID, name, T1 frameworks, empty param fields)?
- A mechanism chain (even if uncalibrated)?
- Nothing — just a name in a list?

Report the breakdown: how many are scaffold-ready for panel calibration vs.
how many need structural work before a panel can calibrate them?

## 4.3 Template Format Consistency

Do all calibrated templates use the same JSON schema? Compare the JSON
structures across STRESS-I, LIGHT-I, SPATIAL-I, and VISUAL-I. Flag any
structural differences (different field names, different nesting, missing
fields in earlier panels).

If earlier panels (STRESS-I, LIGHT-I) used a different format than VISUAL-I,
do they need to be retroactively reformatted?

---

# SECTION 5: SPRINT AND EXECUTION RISK

## 5.1 Cowork Pipeline Risks

The Sprint Task Brief (`SPRINT_TASK_BRIEF_for_Cowork.md`) is about to drive
autonomous execution of 8 panels producing 128 templates.

- Are all input files referenced in every sprint entry actually present in
  the project folder? Check every filename against the actual filesystem.
- Does `scripts/gap_tracker.py` exist and function? Test it.
- Are there any sprint entries with placeholder content (`[AG: Fill...]`)?
- Does the crash-resilience protocol work? (Can you simulate a partial write
  and recovery?)

## 5.2 Dependency Chain Validation

Map the actual dependency chain implied by the sprint input files:

```
SOCIAL-I requires: STRESS-I output, VISUAL-I output
MEMORY-I requires: SOCIAL-I output, SPATIAL-I output, 02-15_02 spec
MULTI-I requires: VISUAL-I output
...
```

Is this chain consistent with the sprint ordering? Are there any cases where
a sprint requires input from a panel that hasn't been executed yet at that
point in the sequence?

## 5.3 Context Window Risk

Estimate the context window load for each panel:
- Sprint Task Brief: ~800 lines
- Transfer doc: ~450 lines
- Panel meta-prompt: ? lines
- Exemplar criteria: ? lines
- Prior panel outputs (varies): ? lines
- The panel output being produced: grows to ~1,000-1,500 lines

Which panels risk exceeding context limits? MUSIC-I (13 templates, multiple
prior panel inputs) and CROSSCUT-I (15 templates, ALL prior panels as input)
are the most likely candidates. Estimate whether they fit.

## 5.4 Underspecified Judgment Calls

For each sprint in the Sprint Task Brief, identify calibration constructs
where the brief says "calibrate" but the logic requires theoretical judgment
that an autonomous agent may not be able to make without human input. Examples:

- Choosing between competing mechanistic accounts (which one anchors the template?)
- Setting boundary values where no empirical data exist and the brief gives no range
- Resolving cross-template interactions that require structural decisions about
  the web (merge templates? split? add interaction term?)
- Assigning bridge warrants in ambiguous cases (MECHANISM vs. EMPIRICAL_COVARIANCE
  boundary calls)

For each, report: sprint, template, construct, what judgment is needed, and
whether the brief provides enough constraint for autonomous execution.

## 5.5 Post-Panel Review Bottleneck

The review protocol requires human clearance between every panel. With 8
panels remaining, that's 8 pre-panel reviews + 8 post-panel reviews = 16
human review checkpoints. Estimate: at current pace, how long does the
full pipeline take? Is this sustainable?

## 5.6 Format Drift Risk Across Panels

STRESS-I and LIGHT-I were calibrated before the OPUS_REVIEW_GUIDE existed.
VISUAL-I was calibrated after. If earlier panels used a different JSON
structure, different mandatory fields, or different confidence score
conventions, every panel output produced by Cowork will follow the VISUAL-I
format while the earlier panels don't match. This creates inconsistency
in the 151-template corpus. Report: what format differences exist between
early and late panels, and should earlier panels be retroactively reformatted
BEFORE Cowork produces 128 more templates in the late format?

---

# SECTION 6: GAP TRACKER AND REGISTRY HEALTH

## 6.1 Gap Tracker Script

- Does `scripts/gap_tracker.py` exist?
- Does it run without errors?
- Does it produce the expected report format?
- Does its template registry match the 151 templates in the Transfer doc?
- Does it correctly show 23 calibrated and 128 remaining?

## 6.2 Gap Registry Reconciliation

Cross-reference the gap tracker's template list against:
- The Transfer doc §5
- The GAP_PANEL_MASTER_PLAN
- Every sprint entry in the Sprint Task Brief
- Every completed panel output

Are there templates in one source but not another? Are counts consistent?

---

# SECTION 7: EXTRACTION PIPELINE HEALTH

If the extraction pipeline has produced artifacts:

## 7.1 Spot Check
Pick 5 random extracted records. For each: correct parse? Populated fields? Errors?

## 7.2 Coverage
Papers processed, claims extracted, claims per paper, failure rate.

## 7.3 Format Compatibility
Can the extraction output feed into the CMR template calibration process?
Or are they currently disconnected systems?

---

# SECTION 8: WEB OF BELIEF / BN IMPLEMENTATION STATUS

The CMR is described as a "Web of Belief with Bayesian causal network properties."

- Is there ANY code implementing the web-of-belief structure?
- Is there ANY code implementing Bayesian network inference?
- Is there ANY code that takes calibrated template JSON and computes the
  three-factor credence product?
- Is there ANY code that tracks cross-template interactions?
- Is there ANY code that tracks entrenchment (T1 harder to revise than templates)?

If the answer to all of these is "no," then the entire theoretical architecture
exists only as specification documents and calibrated panel outputs, with no
computational implementation. This is not necessarily a crisis — the specs and
panels are valuable independently — but it needs to be stated clearly.

---

# SECTION 9: CRITICAL RECOMMENDATIONS

## 9.1 Top 5 Structural Risks

Ordered by "if you don't fix this, everything downstream breaks."

## 9.2 Top 5 Specification Revisions Needed

Which documents need revision before the remaining 8 panels are calibrated?

## 9.3 Code-Theory Integration Plan

Given the actual state of the codebase and the actual state of the theoretical
architecture, what is the shortest path to a system where:
- Calibrated panel outputs can be computationally consumed
- The three-factor credence formula can be computed
- Cross-template interactions can be tracked programmatically
- The gap registry is a live system, not a document

## 9.4 Retroactive Compliance

Do the earlier panel outputs (STRESS-I, LIGHT-I, SPATIAL-I) need to be
retroactively brought into compliance with the OPUS_REVIEW_GUIDE? If so,
estimate the effort.

## 9.5 Should Cowork Proceed?

Based on everything found in this audit: should the Cowork autonomous pipeline
proceed with SOCIAL-I and subsequent panels NOW, or should specific issues be
resolved first? If proceed, list the constraints. If wait, list what must be
fixed and estimate the time.

---

# OUTPUT FORMAT

Produce a single markdown document: `SYSTEM_AUDIT_REPORT_Feb22_2026.md`

Be exhaustive. Cite file paths and line numbers. Quote conflicting text
verbatim. This audit will be used to:

1. Decide whether to proceed with the Cowork pipeline or pause
2. Prioritize code-theory integration work
3. Retroactively fix earlier panel outputs if needed
4. Reconcile terminology across all documents
5. Determine what the Article Eater can and cannot currently do

**Err on the side of reporting too much rather than too little.**

---

*RUTHLESS_SYSTEM_AUDIT_PROMPT_Feb22.md*
*Run in: CC → AG/Gemini → AG/Codex*
*Cross-validate findings across all three*
