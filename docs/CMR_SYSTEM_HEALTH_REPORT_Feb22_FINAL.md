# CMR SYSTEM HEALTH REPORT — FOUR-AUDITOR FINAL SYNTHESIS
## All reports read in full: CC/Codex (20 checkpoints), AG/Opus, Gemini 1.5 Pro, Codex CSVs
## Synthesized by: OPUS/CHAT, February 22, 2026

---

# PART I: DIAGNOSIS

## The System in One Paragraph

The CMR theoretical architecture is sound and internally consistent. The
credence formula, T1/T1.5 rosters, bridge warrant hierarchy, and panel
calibration method all agree across 20+ documents and the codebase. Seven
panels are now complete (VISUAL-I through MULTI-I), producing 53 calibrated
templates with disciplined confidence scoring. The Crucible debate method
works well and is now capturing Toulmin raw material. The codebase is
substantial: BN, coherence computation, credence formula, extraction
pipeline (172K findings), belief seeder (34 beliefs + 50 constraints),
and 10 theory agent profiles all exist and pass their tests.

The problems are all in the intermediate layer — the 184 template JSON
files that bridge theory to code. They use inconsistent schemas, inconsistent
variable names, confidence scores that violate their own ceiling rules, and
three different ID regimes. The gap tracker uses a legacy schema and produces
unreliable counts. The template scanner requires fields that many templates
lack, making them invisible to the code. Two different web persistence
databases create ambiguity about the system's actual belief state. And
there are 479 markdown files in docs/ with only 8 marked as current.

The theory is right. The code works. The data layer is broken. And the
governance layer (which documents are authoritative, which templates count,
which DB is canonical) is ambiguous.

---

## Auditor Corrections and Credit

My earlier triage (based on AG's characterization of the CC report) was
unfair to Codex. AG claimed CC "hallucinated absence of OPUS_REVIEW_GUIDE.md"
and "missed JSON schema inconsistency." But the actual Codex report:

- DID identify schema heterogeneity (Checkpoints 4, 6, 14, 17)
- DID identify field naming drift (Checkpoint 1 finding 6, Checkpoint 17)
- Found 62 bridge-warrant ceiling violations that NO other auditor caught
- Found SPRINT_TASK_BRIEF_for_Cowork.md is EMPTY (0 lines)
- Found gap tracker uses legacy schema and misclassifies modern templates
- Found template scanner skips files missing display_id
- Found three extra bridge warrant types in code not in docs
- Found multi-DB ambiguity (web_persistence.db vs v2)
- Found 184 template files (not 174 as AG reported)
- Ran full pytest: 15 failed, 4049 passed, 18 skipped
- Found panel outputs contain 0 machine-parseable fenced JSON blocks
- Found null claim_text in all 172K extraction rows
- Found circular cross-template flags (LIGHT-I ↔ VISUAL-I)
- Found orphan routing targets (SC-III, VF-III, etc.) not in sprint brief

AG's finding about "OPUS_REVIEW_GUIDE.md NOT FOUND" appears to be
AG misreading the Codex report, not the other way around. The Codex report
never claims the file doesn't exist — it cites it repeatedly with line
numbers (OPUS_REVIEW_GUIDE.md:82, :106, :18, :55, etc.).

**Revised auditor rankings by contribution:**

1. **Codex (A-01)**: Most thorough. 20 checkpoints, line-cited evidence,
   test suite run, bridge ceiling scan, DB inspection, extraction pipeline
   quality, gap tracker root-cause analysis, variable/doc inventories.
2. **Gemini 1.5 Pro (A-03)**: Best execution risk findings (CROSSCUT-I
   context collapse, NEUROMOD-I math, variable vocabulary).
3. **AG/Opus (A-02)**: Useful JSON field frequency table (115+ keys).
   But cross-validation of Codex was inaccurate.
4. **Codex CSVs**: Essential empirical data (1,533 variables, 480 docs).

---

## The Ten Real Problems (revised, ordered by severity)

### 1. BRIDGE WARRANT CEILING VIOLATIONS — CRITICAL (integrity)

**Source**: Codex Checkpoint 3, finding 3.
**Finding**: 62 of 145 bridge_warrant + confidence pairs exceed the
declared ceiling. Examples: MECHANISM warrant with confidence 0.68 (ceiling
0.60), CONSTITUTIVE warrant with confidence 0.88 (ceiling 0.75).
**Why critical**: The bridge warrant ceiling is a HARD RULE in
OPUS_REVIEW_GUIDE.md:18. If calibrated templates routinely violate it,
the entire confidence scoring discipline is undermined. The credence
formula multiplies these values — inflated bridge confidence propagates
through every downstream computation.
**Impact**: This is not just a formatting problem. It's a theoretical
integrity problem. Every template with a ceiling violation has an
incorrectly inflated credence score.

### 2. VARIABLE ISOLATION — CRITICAL (compositionality)

**Source**: Codex CSV, Gemini A-03.
**Finding**: 1,533 variable entries, 931 unique roots, 1,500 appearing
in only one template. Only 33 shared across 2+ templates.
**Why critical**: Cross-template composition requires shared variable
names at interface points. Without them, the CMR cannot compute joint
effects — its core value proposition.

### 3. JSON SCHEMA CHAOS — CRITICAL (infrastructure)

**Source**: All four auditors.
**Finding**: 184 template files (Codex count — differs from AG's 174).
115+ unique top-level keys. Two field names for every major concept.
129 templates with no calibration status. Template scanner requires
display_id which many templates lack, making them invisible to code.
**Why critical**: Every consumer of templates must handle arbitrary
structural variation.

### 4. MULTI-DB AMBIGUITY — HIGH (governance)

**Source**: Codex Checkpoint 18.
**Finding**: Two web persistence databases exist. web_persistence.db has
12,668 beliefs and 37,657 constraints. web_persistence_v2.db has 106
beliefs and 527 constraints. db_locator.py selects between them based
on a `prefer=` argument. AG's belief seeder just created 34 beliefs
in v2. Tools using `prefer='integrated'` see one graph; tools using
`prefer='latest'` see a completely different, much smaller graph.
**Why critical**: The system literally has two different belief states
depending on which code path calls it. This must be resolved to a single
canonical database.

### 5. GAP TRACKER LEGACY SCHEMA — HIGH (governance)

**Source**: Codex Checkpoint 6.
**Finding**: gap_tracker.py uses parameter_range and evidence_base
fields (legacy schema) to classify templates. Modern calibrated
templates use different fields. Result: tracker misclassifies modern
templates, producing unreliable counts (151 vs 153 vs 184).
**Why critical**: The gap tracker is supposed to be the authoritative
count of what's been calibrated and what remains. If it can't
accurately count, project planning is based on wrong numbers.

### 6. SPRINT TASK BRIEF FOR COWORK IS EMPTY — HIGH (governance)

**Source**: Codex Checkpoint 2, finding 1.
**Finding**: SPRINT_TASK_BRIEF_for_Cowork.md is 0 lines.
**Implication**: Cowork must be reading SPRINT_TASK_BRIEF.md instead.
But these are supposed to be different files (one is the master brief,
one is the Cowork execution authority). This needs clarification — is
there one brief or two? If one, delete the empty file to prevent
confusion. If two, populate the Cowork version.

### 7. TEMPLATE COUNT AMBIGUITY — HIGH (governance)

**Source**: All auditors.
**Finding**: Transfer doc says 151. OPUS Guide says 23/128/151 (stale).
Gap tracker says 153. AG counted 174 JSON files. Codex counted 184.
ae.db templates table has 150. Nobody agrees.
**Root cause**: No single reconciliation command. Templates added by
different sessions without updating all counters. Some files are
drafts, WIP, or duplicates.

### 8. PANEL OUTPUTS NOT MACHINE-PARSEABLE — MODERATE (pipeline)

**Source**: Codex Checkpoint 4.
**Finding**: Automated extraction of fenced JSON blocks from panel
output docs returned 0 parseable blocks. Panel outputs are narrative
markdown with inline JSON-like structures that aren't consistently
fenced. The extraction script (extract_panel_json.py) is hardcoded
to one file.
**Implication**: Template JSON extraction from panels requires manual
or semi-manual effort each time. This doesn't block calibration but
slows the template → code pipeline.

### 9. EXTRA BRIDGE WARRANT TYPES IN CODE — MODERATE (spec-code drift)

**Source**: Codex Checkpoint 17.
**Finding**: bridge_warrants.py enum includes EPISTEMIC_COHERENCE_WARRANT,
ARGUMENTATIVE_WARRANT, EPISTEMIC_VIGILANCE_WARRANT. None of these
appear in the canonical 6-level hierarchy in OPUS_REVIEW_GUIDE or
Transfer doc.
**Implication**: Code can assign warrant types that the theoretical
architecture doesn't recognize. Either ratify these in the docs or
remove them from code.

### 10. DOCUMENT SPRAWL — MODERATE (governance)

**Source**: Codex Checkpoint 5, doc inventory CSV.
**Finding**: 479 markdown files. 8 CURRENT. 246 UNKNOWN. 11 versions
of Transfer Context. CLAUDE.md still lists ART/SRT as T1.
02-20_10_Panel_Launch_Briefing lists IE-DPT as T1 #11.
**Implication**: Any new AI session reading docs/ without
PROJECT_STATE.md will encounter contradictory information.

---

# PART II: STRATEGIC PLAN

The short-term fix approach — patch each problem individually, in sequence —
is what we've been doing. It's necessary but insufficient. Each panel session
creates new templates with whatever schema that session invents. Each sprint
fixes some things and introduces new inconsistencies. The fundamental issue
is that there is no enforcement layer: no schema validation, no ceiling
check, no variable normalization, no registry reconciliation — just human
review catching what it can.

The strategic plan has three layers: ENFORCEMENT (prevent new problems),
REMEDIATION (fix existing problems), and GOVERNANCE (make the system
self-describing).

## Layer 1: ENFORCEMENT (prevent future drift)

These run in CI or as pre-commit hooks. Once built, every new template
must pass them before being committed to data/templates/.

### E-01: Canonical JSON Schema + Validator

**What**: JSON Schema (draft-07+) defining required and optional fields
for all templates. Two tiers: scaffold (minimal) and calibrated (full).
**Enforces**: Field naming consistency, required field presence, type
correctness.
**Deliverable**: schemas/template_canonical.json + scripts/validate_templates.py
**Assign**: CC
**Blocks**: Everything else (this is the foundation).

### E-02: Bridge Warrant Ceiling Lint

**What**: Script that reads every template JSON, checks whether
confidence > prior(bridge_warrant), and fails with specific violations.
**Enforces**: The OPUS hard rule at OPUS_REVIEW_GUIDE.md:18.
**Deliverable**: scripts/lint_bridge_ceilings.py
**Assign**: CC
**Run**: After every panel extraction, before committing templates.

### E-03: Variable Registry + Normalization Check

**What**: Canonical variable ontology (schemas/canonical_variables.json)
plus a lint script that checks every variable in every template against
the registry. Unknown variables fail the check.
**Enforces**: Cross-template compositionality — templates can only use
registered variable names.
**Deliverable**: schemas/canonical_variables.json + scripts/lint_variables.py
**Assign**: AG (ontology), CC (lint script)
**Constraint**: New panels may introduce new variables, but they must be
added to the registry explicitly — no silent invention.

### E-04: Template Registry Reconciliation Command

**What**: Single script that counts templates in data/templates/,
ae.db templates table, gap_tracker output, and Transfer doc, and
reports any discrepancies.
**Enforces**: Count consistency.
**Deliverable**: scripts/reconcile_template_counts.py
**Assign**: CC

### E-05: Panel Output Extraction Standard

**What**: Require panel outputs to include fenced JSON blocks for each
calibrated template (```json ... ```). Build a general-purpose extractor
that replaces the hardcoded one-file script.
**Enforces**: Machine-parseable panel outputs.
**Deliverable**: scripts/extract_panel_templates.py (general, not per-panel)
**Assign**: CC, as part of TJ-07 (forward integration).

## Layer 2: REMEDIATION (fix existing corpus)

These run once to bring the existing 184 templates into compliance with
the enforcement layer.

### M-01: Schema Migration

**What**: Rename variant fields to canonical names. Add missing required
fields with null/default values. Resolve display_id gaps so template
scanner stops skipping files.
**Input**: Output of E-01 validator (which templates fail, why).
**Assign**: CC
**Scope**: All 184 template files.

### M-02: Bridge Ceiling Fix

**What**: For each of the 62 ceiling violations, either (a) reduce
confidence to the ceiling value, or (b) upgrade the bridge warrant type
if the evidence justifies a stronger warrant. Each decision requires
theoretical judgment.
**Constraint**: This is NOT a blind clamp-to-ceiling operation. Some
violations may be legitimate cases where the panel determined a higher
warrant level but used the wrong label. Others are genuinely inflated
confidence that should be reduced.
**Assign**: HUMAN review required for each violation. CC builds the
report; HUMAN adjudicates.

### M-03: Variable Migration

**What**: Using canonical_variables.json, rename all variables inside
all 184 template JSONs. Must handle mechanism_chain steps, parameters,
modifiers, cross-template interaction references.
**Assign**: AG (script), CC (execution after P1 migration).
**Runs after**: E-01 (schema) and E-03 (variable registry) both complete.

### M-04: Gap Tracker Rewrite

**What**: Rebase gap_tracker.py on current calibrated template fields
(calibrated_parameters, mechanism-level confidence/warrant, residual
gap structures) instead of legacy parameter_range/evidence_base.
**Assign**: CC
**Runs after**: M-01 (so all templates have consistent schema).

### M-05: DB Consolidation

**What**: Decide canonical web persistence DB. Migrate beliefs/constraints
from the non-canonical DB into the canonical one. Remove db_locator.py
ambiguity — one DB, one path.
**Assign**: CC or AG
**Decision required**: Is web_persistence.db (12,668 beliefs) or
web_persistence_v2.db (106 beliefs + AG's 34 new ones) the canonical
store? The v1 DB has vastly more content but may contain stale/legacy
beliefs. The v2 DB is clean but nearly empty. HUMAN decides.

### M-06: Extra Warrant Types

**What**: Either (a) add EPISTEMIC_COHERENCE_WARRANT, ARGUMENTATIVE_WARRANT,
EPISTEMIC_VIGILANCE_WARRANT to the canonical hierarchy in OPUS_REVIEW_GUIDE
and Transfer doc, with defined ceiling priors, or (b) remove them from
bridge_warrants.py. HUMAN decides which.

### M-07: Test Suite Fix

**What**: Address the 15 failing tests (out of 4,082). Root causes are
mostly template scanner skips (missing display_id) and theory-reference
integrity failures (108 templates with invalid theory refs). M-01
(schema migration) will fix most of these.
**Assign**: CC, after M-01.

## Layer 3: GOVERNANCE (make system self-describing)

### G-01: Document Lifecycle

**What**: Classify all 479 markdown files as CURRENT / SUPERSEDED /
ARCHIVE. Move ARCHIVE to docs/archive/. Add SUPERSEDED headers.
**Assign**: AG using Codex doc inventory CSV.
**Goal**: Reduce active docs/ to ~30-50 current documents.

### G-02: PROJECT_STATE.md as Living Authority

**What**: PROJECT_STATE.md becomes the single entry point. Every system
reads it first. It contains the task board, phase gates, document
registry, and changelog.
**Status**: Already created. Needs to be kept up to date.

### G-03: SPRINT_TASK_BRIEF Consolidation

**What**: Decide: one brief or two? If one, delete the empty
SPRINT_TASK_BRIEF_for_Cowork.md. If two, populate the Cowork version.
Fix filename references (_GENERALIZED vs *GENERALIZED, V1_0 vs V1.0).
**Assign**: CC

### G-04: Orphan Cross-Template Target Resolution

**What**: Map orphan routing targets (SC-III, VF-III, SPATIAL-II,
THEORY-REVIEW, AX-I, etc.) to current sprint panel nomenclature.
Decide which are subsumed by existing panels and which need new panels.
**Assign**: HUMAN decision, CC updates.

### G-05: Template ID Crosswalk

**What**: Build deterministic mapping between all three ID regimes
(legacy T#, series short e.g. VF3, long-form canonical e.g.
NATURE_VIEW_CONVERGENCE_001). Enforce: one canonical ID per template,
with aliases tracked.
**Assign**: CC, as part of M-01.

---

# PART III: EXECUTION ORDER

```
IMMEDIATE (parallel tracks):

  CC TRACK:
    E-01 (canonical schema) → M-01 (migration) → E-02 (ceiling lint)
    → M-02 prep (ceiling violation report for HUMAN)
    → M-04 (gap tracker rewrite)
    → TJ-01 (Toulmin schema extension on canonical base)
    → TJ-02 (Toulmin validator) → TJ-07 (forward integration)
    G-03 (brief consolidation — quick, do alongside E-01)

  AG TRACK:
    E-03a (canonical variable ontology) → M-03 script (variable migration)
    G-01 (document lifecycle — parallel)
    E-03b (variable lint script — after E-03a)

  HUMAN TRACK:
    M-02 adjudication (ceiling violations — when CC produces report)
    M-05 decision (which DB is canonical)
    M-06 decision (extra warrant types: ratify or remove)
    G-04 (orphan target resolution)
    Allostatic integration spec (before S-07)

  COWORK:
    HALTED (MULTI-I complete with Toulmin appendices ✓)
    Resumes when: E-01 + E-02 + E-03 + TJ-07 all complete
    First panel after resume: MUSIC-I

BEFORE S-07 (NEUROMOD-I):
    HUMAN allostatic integration spec
    A-06 (PE partial-out note) in Sprint Brief

BEFORE S-08 (CROSSCUT-I):
    Synthesis script (extract THEORETICAL_DEFAULT flags, residual gaps,
    interaction flags from all panels into <10KB summary)
    G-04 (orphan targets resolved — CROSSCUT-I needs to know what's real)

AFTER COWORK RESUMES:
    TJ-03-06 (retroactive Toulmin on VISUAL/SPATIAL/LIGHT/STRESS)
    in parallel with panel pipeline

AFTER ALL PANELS COMPLETE:
    TJ-08 (AE integration)
    M-07 (test suite cleanup — most will be fixed by M-01)
```

---

# PART IV: WHAT "DONE" LOOKS LIKE

When this plan is complete, the system will have:

1. **One canonical JSON schema** that every template conforms to.
   New templates are validated against it before commitment.

2. **One canonical variable ontology** (~80-120 variables) that every
   template uses. Cross-template composition is mechanically possible.

3. **Bridge warrant ceiling enforcement** — no template can have a
   confidence score above its warrant's ceiling. Violations are caught
   automatically.

4. **One database** for web persistence, with all beliefs, constraints,
   and bridges in one place.

5. **One template count** that agrees across Transfer doc, gap tracker,
   data/templates/, and ae.db.

6. **One set of current documents** (~30-50) with everything else
   archived or marked superseded.

7. **Toulmin justification** either inline (for panels after TJ-07)
   or in raw material appendices (for MULTI-I and retroactively for
   VISUAL-I through STRESS-I).

8. **Automated enforcement** — schema validator, ceiling lint, variable
   lint, count reconciler — that prevents future drift.

9. **Machine-parseable panel outputs** with fenced JSON blocks and a
   general-purpose extractor.

10. **A passing test suite** (or nearly so — the 15 failures resolved
    or explained).

This is the difference between a research prototype and a system that
can scale to 151+ templates without accumulating entropy faster than
panels can reduce it.

---

# PART V: REALISTIC TIMELINE

| Track | Tasks | Estimated effort | Calendar |
|-------|-------|-----------------|----------|
| CC: Schema + migration | E-01, M-01, G-03, G-05 | 2-3 focused sessions | Days 1-3 |
| CC: Ceiling + gap tracker | E-02, M-04, E-04 | 1-2 sessions | Days 2-4 |
| AG: Variable ontology | E-03, M-03 script | 1-2 sessions | Days 1-3 |
| AG: Document lifecycle | G-01 | 1 session | Day 1-2 |
| HUMAN: Adjudication | M-02, M-05, M-06, G-04 | Review sessions | Days 3-5 |
| CC: Toulmin foundation | TJ-01, TJ-02, TJ-07 | 2-3 sessions | Days 4-7 |
| CC + AG: Variable migration | M-03 execution | 1 session | Day 5 (after E-01 + E-03) |
| COWORK: Resume | MUSIC-I onward | Per existing schedule | Day 8+ |

**Total estimated time to "done"**: 7-10 working days for the structural
repair, then panel pipeline resumes with enforcement in place.

This is not fast. But the alternative — continuing to produce panels on
top of structural chaos — means every future panel adds to the remediation
debt, and CROSSCUT-I (the capstone) inherits all of it at once.

---

*CMR_SYSTEM_HEALTH_REPORT_Feb22_FINAL.md*
*Four-auditor synthesis with full CC/Codex report read*
*OPUS/CHAT, February 22, 2026*
