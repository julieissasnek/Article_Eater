# CC REPAIR SPRINT — STRUCTURAL FOUNDATION
## February 22, 2026
## Read PROJECT_STATE.md first. Claim tasks before starting. Update after completing.

---

# CONTEXT

Four independent audits identified structural problems in the template
corpus that must be fixed before the panel pipeline resumes. This sprint
addresses the highest-priority items. The full diagnosis is in
CMR_SYSTEM_HEALTH_REPORT_Feb22_FINAL.md — read it for background.

MULTI-I is complete (9 templates, 9 Toulmin appendices). Cowork is halted.
You have runway to do this work without time pressure from the pipeline.

---

# TASK SEQUENCE

Tasks are grouped into waves. Complete each wave before starting the next
(unless marked PARALLEL-OK). Within a wave, tasks can run in any order.

---

## WAVE 0: QUICK GOVERNANCE FIXES (do first, each takes <10 minutes)

### G-03: Sprint Brief Consolidation

**Problem**: `docs/SPRINT_TASK_BRIEF_for_Cowork.md` is 0 lines (empty file).
Cowork is reading `docs/SPRINT_TASK_BRIEF.md` instead. Two files with nearly
identical names, one empty, creates confusion.

**Action**:
1. Verify: `wc -l docs/SPRINT_TASK_BRIEF_for_Cowork.md`
2. If empty: copy content from SPRINT_TASK_BRIEF.md into it, OR delete it
   and add a note to PROJECT_STATE.md that SPRINT_TASK_BRIEF.md is the sole
   execution authority. Choose whichever is simpler. The goal is ONE brief,
   not two.
3. Fix filename references in the surviving brief:
   - `_GENERALIZED_PANEL_META_PROMPT_Feb21.md` → `*GENERALIZED_PANEL_META_PROMPT_Feb21.md`
     (the actual file has a leading asterisk, not underscore)
   - Check any `V1_0` vs `V1.0` discrepancies in referenced filenames
   - Verify every referenced file actually exists at the stated path

**Acceptance**: One non-empty sprint brief. All filename references resolve.

### R-13: Mark CLAUDE.md SUPERSEDED

**Problem**: `CLAUDE.md` still lists ART/SRT/Biophilia as Tier 1.

**Action**: Add this header to the top of CLAUDE.md:
```
# ⚠️ SUPERSEDED — DO NOT USE FOR ARCHITECTURAL DECISIONS
# See docs/TRANSFER_Feb21_Session8_CORRECTED.md for current architecture.
# This file contains stale T1 roster information (ART/SRT listed as T1).
# Retained for historical reference only.
```

**Acceptance**: Header present. File not deleted (it may be referenced by
other code — just neutralize it).

### M-06: Warrant Type Refactor

**Problem**: `src/services/bridge_warrants.py` enum includes three types
not in the canonical 6-level CMR hierarchy:
- EPISTEMIC_COHERENCE_WARRANT
- ARGUMENTATIVE_WARRANT
- EPISTEMIC_VIGILANCE_WARRANT

**Decision (from HUMAN)**: These are Article Eater claim-evaluation concepts,
not CMR bridge types. They serve different functions. Do NOT delete them.
Refactor them into a separate enum.

**Action**:
1. In `src/services/bridge_warrants.py`, create a new enum:
   ```python
   class EvidenceEvaluationType(str, Enum):
       """Types for evaluating evidence quality in Article Eater.
       These are NOT CMR bridge warrant types and do not have ceiling priors.
       They evaluate how trustworthy/well-structured evidence is,
       not the strength of a theory-to-architecture bridge."""
       EPISTEMIC_COHERENCE = "EPISTEMIC_COHERENCE_WARRANT"
       ARGUMENTATIVE = "ARGUMENTATIVE_WARRANT"
       EPISTEMIC_VIGILANCE = "EPISTEMIC_VIGILANCE_WARRANT"
   ```
2. Remove these three from the `BridgeType` enum (or whatever the CMR
   bridge enum is called).
3. Search the codebase for any code that references these three values.
   Update imports and references to use the new enum.
4. Run tests: `pytest tests/ -q --maxfail=5` — verify no regressions.
5. Add a comment at the top of the BridgeType enum:
   ```python
   # Canonical CMR bridge warrant types (6 levels).
   # Ceiling priors defined in OPUS_REVIEW_GUIDE.md:9-17.
   # For evidence evaluation types, see EvidenceEvaluationType.
   ```

**Acceptance**: Two separate enums. No code references the old combined
enum for these three types. Tests pass.

---

## WAVE 1: DB INVESTIGATION + SCHEMA DEFINITION (parallel tracks)

### M-05a: DB Investigation (for HUMAN decision)

**Problem**: Two web persistence databases exist with vastly different
content. System behavior depends on which code path calls db_locator.py.

**Action**: Run these queries and report results:
```bash
# What's in v1?
sqlite3 data/web_persistence.db "SELECT COUNT(*) FROM beliefs;"
sqlite3 data/web_persistence.db "PRAGMA table_info(beliefs);"
sqlite3 data/web_persistence.db "SELECT * FROM beliefs ORDER BY ROWID LIMIT 5;"
sqlite3 data/web_persistence.db "SELECT DISTINCT substr(source, 1, 50) FROM beliefs LIMIT 20;" 2>/dev/null || echo "no source column"
sqlite3 data/web_persistence.db "SELECT MIN(created_at), MAX(created_at) FROM beliefs;" 2>/dev/null || echo "no created_at column"

# What's in v2?
sqlite3 data/web_persistence_v2.db "SELECT COUNT(*) FROM beliefs;"
sqlite3 data/web_persistence_v2.db "PRAGMA table_info(beliefs);"
sqlite3 data/web_persistence_v2.db "SELECT * FROM beliefs ORDER BY ROWID LIMIT 5;"

# What does db_locator actually do?
cat src/services/db_locator.py

# Who calls it and with what prefer= value?
grep -rn "resolve_web_db\|db_locator\|web_persistence" src/ scripts/ --include="*.py" | head -30
```

**Deliverable**: Paste full output into `docs/DB_INVESTIGATION_REPORT.md`.
The HUMAN decision on M-05b (consolidation strategy) depends on this.

**Decision context (from HUMAN via OPUS/CHAT)**: The likely architecture
is two-tier beliefs in one DB — panel-calibrated beliefs (tier 1, high
quality) and extraction-derived beliefs (tier 2, automated). But we need
to confirm what's actually in v1 before committing.

### E-01: Canonical JSON Schema Definition

**Problem**: 184 template JSON files use 115+ unique top-level keys, two
different field names for every major concept, and no enforced schema.

**Action**:
1. Create `schemas/template_canonical.json` — a JSON Schema (draft-07 or
   later) with TWO validation tiers:

   **Tier: scaffold** (all templates must pass):
   - `template_id` (string, required, unique)
   - `display_id` (string, required — this is what template_scanner needs)
   - `name` (string, required)
   - `t1_frameworks` (array of strings, required, values from: PP, SN, DP,
     DT, NM, IC, MS, EC, CB, MSI)
   - `calibration_status` (string, required, enum: calibrated | scaffold |
     uncalibrated | partial)
   - `panel_source` (string or null)

   **Tier: calibrated** (calibrated templates must additionally have):
   - `mechanism_chain` (array of step objects, each with: step_number,
     description, from, to, and optionally warrant, confidence, source)
   - `bridge_warrant` (string, one of: CONSTITUTIVE, MECHANISM,
     EMPIRICAL_COVARIANCE, FUNCTIONAL, CAPACITY, ANALOGICAL,
     THEORETICAL_DEFAULT)
   - `confidence` (number, 0.0-1.0)
   - `calibrated_parameters` (object)
   - `cross_template_interactions` (array)
   - `residual_gaps` (array)
   - `population_modifiers` (object or null)
   - `architectural_modifiers` (object or null)

   **Canonical field name resolution** (apply during migration):

   | If you find this | Rename to |
   |-----------------|-----------|
   | `status: "calibrated"` | `calibration_status: "calibrated"` |
   | `calibration_status` (any value) | keep as-is |
   | neither field present | add `calibration_status: "uncalibrated"` |
   | `mechanism_steps` | `mechanism_chain` |
   | `bridge_warrant_type` | `bridge_warrant` |
   | `super_template_interactions` | `cross_template_interactions` |
   | `prior_confidence` | `confidence` |
   | `architectural_modifier_coefficients` | `architectural_modifiers` |
   | no `display_id` | generate from template_id (e.g., template_id "NATURE_VIEW_CONVERGENCE_001" → display_id "NVC1" or use existing T#/series ID if one exists in the file) |
   | no `name` | derive from template_id (replace underscores with spaces, title case) |

2. Create `scripts/validate_templates.py`:
   - Reads `schemas/template_canonical.json`
   - Validates every file in `data/templates/*.json`
   - Reports: PASS (scaffold), PASS (calibrated), FAIL (with specific
     missing/wrong fields)
   - Output: both console summary and `data/template_validation_report.json`

3. Run the validator against current corpus. Record how many pass, fail,
   and what the failure patterns are. This output drives M-01.

**Acceptance**: Schema file exists. Validator script exists and runs.
Validation report shows current state of all 184 templates.

**Note on template count**: Codex found 184 files. AG found 174. The
difference may be 10 MEMORY-I templates that were extracted between
the two audits. Verify: `ls data/templates/*.json | wc -l`

---

## WAVE 2: MIGRATION + CEILING ENFORCEMENT

### M-01: Schema Migration

**Depends on**: E-01 complete (schema defined, validator running).

**Action**:
1. Create `scripts/migrate_templates.py`:
   - Reads each template JSON in `data/templates/`
   - Applies the canonical field name resolution table from E-01
   - Adds missing required fields with null/default values
   - Generates `display_id` for files that lack it (see E-01 rules)
   - Generates `name` for files that lack it
   - Writes migrated file back (in-place, or to a staging directory
     first if you prefer — just make sure the final state is in
     data/templates/)
   - Logs every change made per file

2. Run migration.

3. Run validator again. Target: ALL 184 templates pass scaffold tier.
   All calibrated templates pass calibrated tier.

4. Run template_scanner.py — verify it no longer skips files for missing
   display_id.

5. Run `pytest tests/test_template_record.py -v` — this was failing
   because of missing fields. Check if migration fixes it.

**Acceptance**: All templates pass scaffold validation. No scanner skips.
Template record test passes or has identified remaining issues.

### E-02: Bridge Warrant Ceiling Lint

**Depends on**: E-01 complete (schema defines which field names to check).
Can be built in parallel with M-01.

**Action**:
1. Create `scripts/lint_bridge_ceilings.py`:
   - Reads each template JSON
   - For each calibrated template, checks:
     - top-level `bridge_warrant` + `confidence`: confidence ≤ ceiling
     - each step in `mechanism_chain` that has its own warrant + confidence:
       confidence ≤ ceiling for that warrant
   - Ceiling values (from OPUS_REVIEW_GUIDE.md:9-17):
     - CONSTITUTIVE: 0.75
     - MECHANISM: 0.60
     - EMPIRICAL_COVARIANCE: 0.60
     - FUNCTIONAL: 0.50
     - CAPACITY: 0.45
     - ANALOGICAL: 0.35
     - THEORETICAL_DEFAULT: 0.40 (per OPUS_REVIEW_GUIDE convention)
   - Reports: template_id, field_path, warrant_type, confidence_value,
     ceiling, delta (how much it exceeds by)
   - Output: console table + `data/ceiling_violation_report.json`

2. Run against current corpus.

**Acceptance**: Script runs, produces violation report. Codex found 62
violations — your report should find a similar number (may differ slightly
due to migration field name changes).

### M-02a: Ceiling Violation Report for HUMAN

**Depends on**: E-02 complete.

**Action**:
1. Take the output of lint_bridge_ceilings.py
2. Create `docs/CEILING_VIOLATION_REPORT.md` with:
   - Summary: N violations across M templates
   - For each violation, grouped by pattern:
     - Template ID, parameter/step, warrant type, current confidence,
       ceiling, delta
     - Suggested action: REDUCE (clamp to ceiling) or REVIEW (warrant
       type may need upgrading)
   - Use this heuristic for suggested action:
     - Delta ≤ 0.05: suggest REDUCE (likely rounding or minor overshoot)
     - Delta > 0.05 AND template is from a calibrated panel (VISUAL-I etc):
       suggest REVIEW (the panel may have intended a higher warrant)
     - Delta > 0.05 AND template is pre-panel (scaffold): suggest REDUCE
3. The HUMAN will adjudicate each group and tell you what to do.

**Acceptance**: Report exists, is readable, groups violations by pattern.

---

## WAVE 3: MEMORY-I + MULTI-I EXTRACTION + BOOKKEEPING

### R-09: Extract MEMORY-I JSONs

**Depends on**: M-01 complete (so you use canonical field names).

**Action**:
1. Extract 10 calibrated templates from MEMORY_I_Panel_Output.md to
   data/templates/
2. Use canonical field names from E-01 schema
3. Include `display_id`, `name`, `calibration_status: "calibrated"`,
   `panel_source: "MEMORY-I"`
4. Run validator: all 10 must pass calibrated tier
5. Run ceiling lint: all 10 must pass
6. Run gap_tracker

### R-09b: Extract MULTI-I JSONs

**Depends on**: M-01 complete.

**Action**: Same as R-09 but for MULTI_I_Panel_Output.md (9 templates).
Include `panel_source: "MULTI-I"`.

### R-10: Update TRANSFER Doc

**Depends on**: R-09, R-09b complete.

**Action**: Update template counts in TRANSFER_Feb21_Session8_CORRECTED.md.
Add MEMORY-I and MULTI-I rows. Update totals. Also update the count in
OPUS_REVIEW_GUIDE.md (currently says 23/128/151 — stale).

### R-11: Update Sprint Brief S-02

**Action**: Mark S-02 MEMORY-I as COMPLETE. Set post_panel_review_cleared: true.

### R-12: Update Sprint Brief S-03

**Action**: Mark S-03 MULTI-I as COMPLETE (execution done, pending post-review).
Set pre_panel_review_cleared: true.

### A-06: NEUROMOD-I PE Note

**Action**: Add to Sprint Brief S-07 (NEUROMOD-I) section:
```
CALIBRATION CONSTRAINT (from MEMORY-I Flag 4):
PE encoding pathway (VTA → hippocampus) is shared between MEMORY-I
templates (ED_PE_ENCODING_PRINCIPLE_001) and NEUROMOD-I dopaminergic
templates. Apply partial-out rule: NEUROMOD-I owns the dopaminergic
mechanism; MEMORY-I owns the encoding consequence. Do not double-count
the PE signal as both a neuromodulatory input and an encoding driver.
Cross-reference: PRE_PANEL_REVIEW_CLEARANCE_MEMORY_I.md Flag 4.
```

### E-04: Template Count Reconciliation Script

**Depends on**: M-01 complete (so all templates are in canonical form).

**Action**:
1. Create `scripts/reconcile_counts.py`:
   - Count JSON files in data/templates/
   - Count rows in ae.db templates table
   - Parse calibrated count from TRANSFER doc
   - Parse gap_tracker output
   - Report discrepancies
2. Run it. Fix any discrepancies by updating the stale sources.

**Acceptance**: All four sources agree on total and calibrated counts.

---

## WAVE 4: GAP TRACKER + REMAINING CLEANUP

### M-04: Gap Tracker Rewrite

**Depends on**: M-01 complete (canonical schema in place).

**Problem**: gap_tracker.py uses legacy fields (parameter_range,
evidence_base) to classify templates. Modern templates don't have
these fields.

**Action**:
1. Rewrite gap_tracker.py to use canonical fields:
   - Calibrated: `calibration_status == "calibrated"`
   - Has mechanism: `mechanism_chain` exists and is non-empty
   - Has parameters: `calibrated_parameters` exists and is non-empty
   - Gap classification based on what's missing from calibrated tier
2. Run and verify count matches E-04 reconciliation output.

### M-07: Test Suite Triage

**Depends on**: M-01 + M-06 complete.

**Action**:
1. Run `pytest -q --maxfail=20`
2. Codex found 15 failures. After M-01 migration (which adds display_id
   and normalizes fields), many should be fixed.
3. For remaining failures, triage:
   - Template matching failures (VIEW1 not found etc): likely need
     template ID crosswalk or scanner update
   - Theory reference integrity (108 templates with invalid refs):
     likely need theory ID normalization in templates
4. Fix what you can. Document what remains.

---

## WAVE 5: TOULMIN FOUNDATION (after waves 1-3 minimum)

### TJ-01: Toulmin Schema Extension

**Depends on**: E-01 + M-01 complete (canonical base schema exists and
all templates conform to it).

**Action**: Extend the canonical schema with Toulmin justification fields
per OPUS_REVIEW_GUIDE_ADDENDUM_TOULMIN.md. Add to calibrated tier:

```json
"justification": {
  "data": [...],
  "backing": "...",
  "qualifier": "...",
  "rebuttal": "...",
  "competing_accounts": [...]
}
```

Three depth tiers per the addendum: Tier A (full), Tier B (standard),
Tier C (stub). Update validator to check depth tier compliance.

### TJ-02: Toulmin Validation Tooling

**Depends on**: TJ-01.

**Action**: Create scripts/validate_toulmin.py per TOULMIN_SPRINT_TASK_BRIEF.md.

### TJ-07: Forward Integration

**Depends on**: TJ-01.

**Action**: Update *GENERALIZED_PANEL_META_PROMPT_Feb21.md, exemplar_panel_
criteria.md, OPUS_REVIEW_GUIDE.md, and SPRINT_TASK_BRIEF.md so that future
panels produce:
- Fenced JSON blocks (E-05)
- Canonical field names
- Inline Toulmin justification (at appropriate depth tier)
- Ceiling-compliant confidence scores

This is the gate for resuming Cowork.

---

# ACCEPTANCE CRITERIA FOR COWORK RESUME

ALL of the following must be true:
- [x] E-01 schema exists and validates
- [x] M-01 migration complete (all templates pass scaffold)
- [x] E-02 ceiling lint exists and runs
- [x] M-02b ceiling violations adjudicated by HUMAN
- [x] M-04 gap tracker uses current schema
- [x] E-04 template counts reconciled
- [x] TJ-01 Toulmin schema extension in place
- [x] TJ-07 forward integration complete (panel prompt updated)
- [x] G-03 sprint brief consolidated
- [x] Variable ontology at least DRAFTED (E-03a from AG)

When these are met, update PROJECT_STATE.md Phase 4 to ACTIVE.

---

# CLAIMING TASKS

Before starting any task:
1. Open docs/PROJECT_STATE.md
2. Find the task in the task board
3. Write "OPUS/CC" in the Claimed By field
4. Save the file
5. Begin work

After completing:
1. Mark COMPLETED in PROJECT_STATE.md
2. Write output file paths
3. Check if completion unblocks downstream tasks
4. Append to changelog
5. Save

---

*CC_REPAIR_SPRINT_INSTRUCTIONS.md — CMR Project*
*Structural Foundation Sprint, February 22, 2026*
