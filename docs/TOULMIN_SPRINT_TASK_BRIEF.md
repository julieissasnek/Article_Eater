# TOULMIN JUSTIFICATION LAYER — CC SPRINT TASK BRIEF
## Execute AFTER ruthless audit remediation is complete
## Depends on: SYSTEM_AUDIT_REPORT findings resolved
## February 22, 2026

---

# PREREQUISITES

Do NOT begin these sprints until:
1. The Ruthless System Audit (RUTHLESS_SYSTEM_AUDIT_PROMPT_Feb22.md) has been
   run across CC, AG/Gemini, and AG/Codex
2. The audit findings have been triaged and critical issues resolved
3. The calibrated JSON schema is confirmed stable (audit §4.3 may reveal
   format inconsistencies across panels that need resolving first)

If the audit reveals that the calibrated JSON format differs across panels
(likely: STRESS-I and LIGHT-I predate OPUS_REVIEW_GUIDE), resolve that
BEFORE starting TJ-01. The Toulmin layer must be added to a stable schema,
not a moving target.

---

# SPRINT OVERVIEW

| Sprint | Name | Input | Output | Depends On |
|--------|------|-------|--------|-----------|
| TJ-01 | Schema extension | OPUS_REVIEW_GUIDE_ADDENDUM_TOULMIN.md | Updated JSON schema with justification fields | Audit remediation complete |
| TJ-02 | Validation tooling | TJ-01 schema | Validator script + depth tier classifier | TJ-01 |
| TJ-03 | Retroactive extraction — VISUAL-I | VISUAL_I_Panel_Output_Feb21.md | 8 templates with justification layer | TJ-01, TJ-02 |
| TJ-04 | Retroactive extraction — SPATIAL-I | SPATIAL_I_Panel_Output_Feb21.md | 4 templates with justification layer | TJ-01, TJ-02 |
| TJ-05 | Retroactive extraction — LIGHT-I | LIGHT_I_Panel_Output_Feb21.md | 8 templates with justification layer | TJ-01, TJ-02 |
| TJ-06 | Retroactive extraction — STRESS-I | STRESS_I_Panel_Output_Feb21.md | 3 templates with justification layer | TJ-01, TJ-02 |
| TJ-07 | Forward integration | Sprint Task Brief, panel meta-prompt | Updated panel production workflow | TJ-01, TJ-02 |
| TJ-08 | Article Eater integration | Codebase, TJ-01 schema | Code that can ingest/display/update justification fields | TJ-01 |

---

# SPRINT TJ-01: SCHEMA EXTENSION

**Goal**: Extend the calibrated template JSON schema to include the Toulmin
justification layer as specified in OPUS_REVIEW_GUIDE_ADDENDUM_TOULMIN.md.

## Input files — read ALL before writing anything

1. `OPUS_REVIEW_GUIDE_ADDENDUM_TOULMIN.md` — the specification (§2 defines all fields)
2. `VISUAL_I_Panel_Output_Feb21.md` — Output Block 1 contains the current JSON
   schema. The Toulmin layer must be additive — all existing fields preserved.
3. The current data model files in the codebase (if any exist — the audit will
   tell you where they are or whether they exist at all)

## Tasks

1. **Define the JSON schema extension.** Write a formal JSON Schema (draft-07
   or later) that validates a calibrated template WITH the justification layer.
   The schema must:
   - Accept templates WITHOUT the justification layer (backward compatible —
     older templates pass validation with a warning, not an error)
   - Require the justification layer for any template with `"status": "calibrated"`
     and a calibration date after February 22, 2026
   - Enforce the field requirements from the addendum §2 (data array min length,
     non-empty backing/qualifier/rebuttal strings)
   - Enforce the depth tier rules from §4 (Tier A for confidence > 0.55 or
     MECHANISM warrant; Tier B for all other calibrated steps; Tier C for
     RESIDUAL GAPS only)

2. **Write the schema file.** Save as `schemas/template_with_justification.json`

3. **Write a migration guide.** A short document explaining how to add the
   justification layer to an existing template JSON block. Include before/after
   examples. Save as `docs/TOULMIN_MIGRATION_GUIDE.md`

## Output files

- `schemas/template_with_justification.json`
- `docs/TOULMIN_MIGRATION_GUIDE.md`

## Completion criteria

- [ ] Schema validates the example in ADDENDUM §6 (T1 step 3)
- [ ] Schema accepts current VISUAL-I JSON without justification (backward compat)
- [ ] Schema rejects a template with confidence > 0.55 and missing justification
- [ ] Migration guide includes before/after example

---

# SPRINT TJ-02: VALIDATION TOOLING

**Goal**: Build a validator script that checks Toulmin justification compliance
across all calibrated templates.

## Tasks

1. **Build `scripts/validate_toulmin.py`**. The script should:
   - Accept a panel output file (markdown with embedded JSON) or a standalone
     JSON file
   - Extract all calibrated template JSON blocks
   - For each template, for each mechanism step:
     - Check whether justification layer is present
     - Classify the step's required depth tier (A, B, or C) based on the rules
       in ADDENDUM §4
     - Validate that the justification meets the required tier's minimum fields
     - Check the consistency rules from ADDENDUM §3:
       - Data < 2 independent paradigms AND confidence > 0.50 → FLAG
       - Non-empty competing_accounts AND confidence > 0.55 → FLAG
       - Rebuttal describes active condition AND confidence > 0.60 → FLAG
       - Qualifier identifies timescale mismatch → CHECK confidence reduction
     - Report: template ID, step number, required tier, actual tier, compliance
       status, flags

2. **Build `scripts/classify_depth_tier.py`** (or integrate into the above).
   Given a mechanism step's warrant type, confidence score, and
   competing_accounts array, return the required depth tier (A, B, or C).

3. **Write tests.** At minimum:
   - Test that the T1 step 3 example from ADDENDUM §6 passes as Tier A
   - Test that a step with confidence 0.40, no justification, in RESIDUAL GAPS
     passes as Tier C
   - Test that a step with confidence 0.60 and no justification fails
   - Test each consistency flag fires correctly

## Output files

- `scripts/validate_toulmin.py`
- `scripts/classify_depth_tier.py` (or integrated)
- `tests/test_toulmin_validation.py`

## Completion criteria

- [ ] Validator runs on VISUAL-I panel output and reports all steps as "missing
      justification" (expected — justification hasn't been added yet)
- [ ] Validator runs on the ADDENDUM §6 example and reports it as compliant
- [ ] All tests pass
- [ ] Validator produces a summary report: N steps total, N compliant, N
      missing, N flagged, breakdown by depth tier

---

# SPRINT TJ-03: RETROACTIVE EXTRACTION — VISUAL-I

**Goal**: Extract Toulmin justification content from VISUAL-I panel output and
add it to all 8 calibrated template JSON blocks.

## Why VISUAL-I first

VISUAL-I has the most detailed Crucible debate content of any completed panel.
The opening statements, disputes, and consensus notes contain most of the
Toulmin components — they just need to be extracted and structured. This
sprint establishes the extraction method that TJ-04 through TJ-06 will follow.

## Input files

1. `VISUAL_I_Panel_Output_Feb21.md` — the FULL panel output, including:
   - Opening statements (→ `data` and `backing`)
   - Crucible debates (→ `rebuttal` and `competing_accounts`)
   - Consensus notes (→ `qualifier`)
   - Calibrated JSON (→ the templates to be extended)
   - Residual gaps (→ Tier C stubs for uncalibratable steps)
2. `OPUS_REVIEW_GUIDE_ADDENDUM_TOULMIN.md` — field definitions
3. `schemas/template_with_justification.json` — for validation

## Method

For each of the 8 templates (T1, T2, T22, L1, VIEW1, VF1, VF2, VF3):
1. Read the opening statements from the experts assigned to this template
2. Read the Crucible debate(s) relevant to this template
3. Read the residual gaps section for this template
4. For each mechanism step in the template:
   a. Identify which opening statements and debate passages provide evidence
      for this step
   b. Extract data entries (finding, source, paradigm, effect, n, design)
   c. Write the backing paragraph from the convergence argument made in the
      debate
   d. Write the qualifier from the consensus and residual gaps
   e. Write the rebuttal from the disputes and the residual gaps
   f. Extract competing accounts from expert disagreements
   g. Classify the required depth tier
   h. Populate the justification object

5. After populating all steps for all 8 templates, run validate_toulmin.py
6. Fix any flagged inconsistencies (confidence score vs. justification content)

## Critical rule

Do NOT invent justification content that is not present in or derivable from
the panel output. If the panel output does not contain sufficient debate
content for a mechanism step, write a Tier C stub and mark it:
`"justification_status": "stub — insufficient panel debate content for this step"`

The panel debates contain a LOT of material — most steps should reach Tier B
or Tier A. But some intermediate steps (especially metabolic cost estimates
and population modifier derivations) may not have been debated. Those get stubs.

## Output files

- `VISUAL_I_Panel_Output_TOULMIN.md` — the full panel output with justification
  layer added to all 8 template JSON blocks
- `reports/VISUAL_I_toulmin_validation_report.md` — output of validate_toulmin.py

## Completion criteria

- [ ] All 8 templates have justification layer
- [ ] All Tier A steps (confidence > 0.55 or MECHANISM warrant) have full
      justification (data ≥ 2, backing, qualifier, rebuttal, competing if any)
- [ ] Validator reports zero errors for required tier compliance
- [ ] No invented content — every data entry traceable to panel output
- [ ] Summary: N total steps across 8 templates, N at Tier A, N at Tier B,
      N at Tier C stub

---

# SPRINT TJ-04: RETROACTIVE EXTRACTION — SPATIAL-I

**Goal**: Same as TJ-03 but for SPATIAL-I (4 templates: SC1, SC2, SC3, SC4).

## Input files

1. `SPATIAL_I_Panel_Output_Feb21.md` (Doc 63)
2. ADDENDUM and schema from TJ-01

## Notes

SPATIAL-I may have less detailed debate content than VISUAL-I (it was an earlier
panel). Expect more Tier C stubs. This is acceptable — flag the stubs for future
panel revisit rather than inventing content.

## Output files

- `SPATIAL_I_Panel_Output_TOULMIN.md`
- `reports/SPATIAL_I_toulmin_validation_report.md`

## Completion criteria

Same as TJ-03 adapted for 4 templates.

---

# SPRINT TJ-05: RETROACTIVE EXTRACTION — LIGHT-I

**Goal**: Same as TJ-03 but for LIGHT-I (8 templates).

## Input files

1. `LIGHT_I_Panel_Output_Feb21.md`
2. ADDENDUM and schema from TJ-01

## Notes

LIGHT-I predates the OPUS_REVIEW_GUIDE. Its JSON format may differ from VISUAL-I.
If the audit (or audit remediation) has already standardized the format, proceed
normally. If not, standardize the JSON format FIRST (match VISUAL-I schema), THEN
add the justification layer.

LIGHT-I may have the strongest CONSTITUTIVE warrant examples in the system
(daylight exposure). These steps should have particularly clear justifications
because the bridge is definitional — the data section can cite the constitutive
relationship directly.

## Output files

- `LIGHT_I_Panel_Output_TOULMIN.md`
- `reports/LIGHT_I_toulmin_validation_report.md`

---

# SPRINT TJ-06: RETROACTIVE EXTRACTION — STRESS-I

**Goal**: Same as TJ-03 but for STRESS-I (3 templates: T6, T7, T14).

## Input files

1. `STRESS_I_Panel_Output_Feb21.md`
2. ADDENDUM and schema from TJ-01

## Notes

STRESS-I was the first panel calibrated and predates all current formatting
standards. Expect the most format remediation work here. The panel debate
content may be sparser than later panels. T7 (allostatic anticipation) is
referenced by multiple downstream panels — its justification layer is
high-priority because other panels inherit from it.

## Output files

- `STRESS_I_Panel_Output_TOULMIN.md`
- `reports/STRESS_I_toulmin_validation_report.md`

---

# SPRINT TJ-07: FORWARD INTEGRATION

**Goal**: Modify the panel production workflow so that all future panels
(SOCIAL-I onward) produce the Toulmin justification layer as part of normal
calibration output.

## Tasks

1. **Update `_GENERALIZED_PANEL_META_PROMPT_Feb21.md`**. Add instructions to
   the panel prompt template specifying that:
   - Opening statements must include structured data entries (finding, source,
     paradigm, effect, n, design) for each mechanism step they anchor
   - Crucible debates must produce explicit rebuttal and competing_accounts
     content that is retained in the output (not summarized away)
   - Consensus calibration must produce qualifier text for each step
   - The calibrated JSON output must include the justification field per step

2. **Update `exemplar_panel_criteria.md`**. Add the Toulmin justification layer
   to the list of mandatory panel output components. Include the VISUAL-I T1
   step 3 example (from ADDENDUM §6) as the exemplar.

3. **Update `OPUS_REVIEW_GUIDE.md`**. Incorporate the addendum into the main
   guide (or add a reference directing readers to the addendum). Add to the
   red flag scan: "Missing justification on any step with confidence > 0.50"
   and "Rebuttal describes active condition but confidence > 0.60."

4. **Update the Sprint Task Brief completion checklists**. Add to every sprint's
   checklist:
   - [ ] All mechanism steps have justification layer at required depth tier
   - [ ] validate_toulmin.py reports zero errors

## Output files

- Updated `_GENERALIZED_PANEL_META_PROMPT_Feb21.md`
- Updated `exemplar_panel_criteria.md`
- Updated `OPUS_REVIEW_GUIDE.md`
- Updated `SPRINT_TASK_BRIEF_for_Cowork.md` (all sprint checklists)

## Completion criteria

- [ ] A test run of the updated panel meta-prompt on a single template produces
      output with the justification layer
- [ ] The exemplar criteria document includes a Toulmin example
- [ ] The OPUS_REVIEW_GUIDE includes the new red flags
- [ ] All 8 sprint checklists in the Sprint Task Brief include the new items

---

# SPRINT TJ-08: ARTICLE EATER INTEGRATION

**Goal**: Ensure the Article Eater codebase can ingest, store, display, and
update the Toulmin justification layer.

## Depends on

- The audit (RUTHLESS_SYSTEM_AUDIT_PROMPT_Feb22.md §8) will report whether
  ANY code currently consumes calibrated template JSON. If the answer is "no
  code exists," this sprint scopes the initial implementation. If code exists
  but doesn't handle justification fields, this sprint extends it.

## Tasks (scope depends on audit findings)

### If no template ingestion code exists:

1. Design the data model for storing calibrated templates with justification.
   Minimum viable: a document store (JSON files or SQLite with JSON columns)
   that can:
   - Store a template with all fields including justification
   - Query templates by ID, panel, T1 framework, bridge warrant type
   - Query justification data entries by source (which papers support which steps)
   - Query competing accounts across templates (which debates are unresolved)

2. Write an ingestion script that reads a panel output file (markdown with
   embedded JSON) and extracts all calibrated template blocks into the store.

3. Write a display function that, given a template ID and a step number,
   returns either the summary (description + warrant + confidence) or the
   full justification (all Toulmin fields). This is the QA drill-down.

4. Write an update function that adds a new data entry to an existing step's
   justification (for when the Article Eater ingests a new paper that supports
   or challenges an existing mechanism step).

### If template ingestion code exists but lacks justification:

1. Extend the data model to include the justification fields.
2. Write a migration script that adds empty justification stubs to all existing
   stored templates.
3. Write an ingestion update that populates justification from the TOULMIN
   panel output files produced in TJ-03 through TJ-06.
4. Write the display and update functions as above.

## Output files

- Data model extension (schema or code)
- Ingestion script or extension
- Display function
- Update function
- Tests for all of the above

## Completion criteria

- [ ] All 23 calibrated templates (with justification from TJ-03 through TJ-06)
      are stored in the system
- [ ] Query by template ID returns full justification
- [ ] Query by source returns all steps that cite a given paper
- [ ] Adding a new data entry to an existing step works and persists
- [ ] Display function returns summary or full justification on request

---

# SPRINT SEQUENCING SUMMARY

```
AUDIT REMEDIATION (prerequisite — not part of TJ sprints)
    |
    v
TJ-01: Schema extension
    |
    v
TJ-02: Validation tooling
    |
    +---> TJ-03: Retroactive — VISUAL-I (do first, establishes method)
    |         |
    |         +---> TJ-04: Retroactive — SPATIAL-I (parallel OK)
    |         +---> TJ-05: Retroactive — LIGHT-I (parallel OK)
    |         +---> TJ-06: Retroactive — STRESS-I (parallel OK)
    |
    +---> TJ-07: Forward integration (can run parallel with TJ-03)
    |
    v
TJ-08: Article Eater integration (after TJ-03 through TJ-06 complete)
```

TJ-03 must precede TJ-04/05/06 because it establishes the extraction method.
TJ-04, TJ-05, TJ-06 can run in parallel after TJ-03 is complete.
TJ-07 can run in parallel with TJ-03 (it modifies workflow docs, not templates).
TJ-08 runs last because it needs all 23 templates with justification as input.

---

# RELATIONSHIP TO COWORK PANEL PIPELINE

The Cowork pipeline (SOCIAL-I through CROSSCUT-I) and the Toulmin sprints
can run in parallel IF TJ-07 is completed before SOCIAL-I begins production.
Once TJ-07 updates the panel meta-prompt and exemplar criteria, all Cowork
panels will produce the justification layer natively.

If SOCIAL-I begins BEFORE TJ-07 is complete, SOCIAL-I's output will need
retroactive Toulmin extraction (same as TJ-03 method). This is not ideal
but not catastrophic — it just adds one more retroactive sprint.

**Recommended sequencing**:
1. Run audit
2. Remediate critical audit findings
3. Complete TJ-01 and TJ-02 (schema and tooling)
4. Complete TJ-07 (forward integration — update panel prompt and exemplar)
5. Clear SOCIAL-I for Cowork execution (panel now produces Toulmin natively)
6. Run TJ-03 through TJ-06 (retroactive for completed panels) in parallel
   with Cowork producing SOCIAL-I
7. TJ-08 after all retroactive sprints complete

---

*TOULMIN_SPRINT_TASK_BRIEF.md — CMR Project*
*Generated: February 22, 2026*
*Execute after: Ruthless Audit remediation*
*Hand to: Claude Code*
