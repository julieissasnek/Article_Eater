# RUTHLESS SYSTEM AUDIT v2 — CMR / ARTICLE EATER
## Post-Repair Verification + Ongoing Health Check
## February 2026 (run after structural repair sprint completes)
## Run in: CC, then AG or Gemini, then Codex. Cross-validate findings.

---

# CONTEXT

This is the second ruthless audit. The first (Feb 22, 2026) was run across
four independent auditors (Codex, AG/Opus, Gemini 1.5 Pro, Codex CSVs)
and identified 10 structural problems. A repair sprint was then executed
by CC and AG (see CC_REPAIR_SPRINT_INSTRUCTIONS.md and
AG_REPAIR_SPRINT_INSTRUCTIONS.md for what was assigned).

This audit has two jobs:

1. **VERIFY THE REPAIRS.** Did the repair sprint actually fix what it
   claimed to fix? Don't trust self-reports — check independently.

2. **CATCH WHAT'S STILL BROKEN.** The first audit found problems. The
   repairs may have introduced new ones. And some problems from the first
   audit may have been missed or insufficiently fixed.

**Current state (update these numbers before running):**

- T1 frameworks: 10
- T1.5 theories: 10 formally reduced + candidates
- Total template JSON files: ~184 (verify: `ls data/templates/*.json | wc -l`)
- Calibrated templates: ~53 (verify against canonical schema validator)
- Completed panels: 7 (VISUAL-I, SPATIAL-I, LIGHT-I, STRESS-I, SOCIAL-I,
  MEMORY-I, MULTI-I)
- Remaining panels: 5 (MUSIC-I, THERMAL-I, CREATIVE-I, NEUROMOD-I, CROSSCUT-I)
- Cowork status: HALTED (waiting for Phase 4 ACTIVE in PROJECT_STATE.md)
- Extraction findings in ae.db: ~172,091
- Web persistence: status depends on M-05b consolidation decision

**The same rules apply as before: Do not be polite. Do not soften findings.
Cite file paths and line numbers. Quote conflicting passages verbatim.**

---

# PART A: REPAIR VERIFICATION

The Feb 22 audit identified 10 problems. For each one below, independently
verify whether the repair was actually completed and whether it actually
fixed the problem. Do NOT rely on changelog entries, commit messages, or
claims in PROJECT_STATE.md. Check the artifacts directly.

## A-01: Bridge Warrant Ceiling Violations (was: 62 of 145 pairs)

The Feb 22 Codex audit found 62 bridge_warrant + confidence pairs exceeding
their warrant ceiling (OPUS_REVIEW_GUIDE.md:9-17). The repair sprint was
supposed to:
- Build `scripts/lint_bridge_ceilings.py` (E-02)
- Produce a violation report (M-02a)
- Have HUMAN adjudicate each violation (M-02b)
- Apply fixes

**Verify:**
1. Does `scripts/lint_bridge_ceilings.py` exist?
2. Run it. How many violations does it find NOW?
3. If violations remain: are they documented as HUMAN-approved exceptions,
   or are they simply unfixed?
4. Does the lint use the correct ceiling values?
   - CONSTITUTIVE: 0.75
   - MECHANISM: 0.60
   - EMPIRICAL_COVARIANCE: 0.60
   - FUNCTIONAL: 0.50
   - CAPACITY: 0.45
   - ANALOGICAL: 0.35
5. Does the lint check BOTH top-level confidence AND per-step confidence
   within mechanism_chain entries?
6. Is THEORETICAL_DEFAULT handled? (It should have a ceiling — check what
   value was chosen and whether it matches OPUS Review Guide conventions.)

**Report**: violation count before repair, violation count now, delta,
any remaining violations with template_id and details.

## A-02: Variable Isolation (was: 931 unique roots, 1500 in only 1 template)

The repair sprint was supposed to:
- Build canonical variable ontology (E-03a): ~80-120 variables
- Build migration script (M-03a)
- Execute migration (M-03b)

**Verify:**
1. Does `schemas/canonical_variables.json` exist?
2. How many canonical variables are defined? How many domains?
3. Does the alias_map cover all variable names currently in templates?
   Run: extract every variable name from every template's mechanism_chain,
   calibrated_parameters, population_modifiers, architectural_modifiers.
   Check each against the alias_map. Report any UNREGISTERED variables.
4. Does `scripts/lint_variables.py` exist? Run it. How many templates pass?
5. After migration: how many variables appear in 2+ templates? (This was
   33 before. It should be dramatically higher if synonyms were merged.)
6. Pick 5 known cross-template interaction pairs from panel outputs. For
   each pair, verify that the output variable of template A uses the SAME
   canonical name as the input variable of template B. If not, the
   migration missed something.

**Report**: canonical variable count, alias coverage %, cross-template
variable sharing before and after, any unregistered variables.

## A-03: JSON Schema Chaos (was: 115+ unique top-level keys, 184 files)

The repair sprint was supposed to:
- Define canonical schema (E-01): `schemas/template_canonical.json`
- Build validator (E-01): `scripts/validate_templates.py`
- Migrate all templates (M-01)

**Verify:**
1. Does `schemas/template_canonical.json` exist? Is it valid JSON Schema?
2. Does `scripts/validate_templates.py` exist?
3. Run the validator against ALL template files. Report:
   - Total templates
   - Pass scaffold tier
   - Pass calibrated tier
   - FAIL (with failure reasons)
4. Are there still templates missing `display_id`? (This was causing
   template_scanner.py to skip files.) Run the scanner and check for
   skip warnings.
5. Count unique top-level keys across all templates now. (Was 115+.
   Should be dramatically reduced after migration.)
6. Check field name consistency specifically:
   - Is `calibration_status` the ONLY calibration field? (Was split
     between `status` and `calibration_status`)
   - Is `mechanism_chain` the ONLY mechanism field? (Was split with
     `mechanism_steps`)
   - Is `bridge_warrant` the ONLY warrant field? (Was split with
     `bridge_warrant_type`)
   - Is `cross_template_interactions` the ONLY interaction field? (Was
     split with `super_template_interactions`)
   - Is `architectural_modifiers` the ONLY modifier field? (Was split
     with `architectural_modifier_coefficients`)

**Report**: validation pass rates, unique key count before and after,
specific field name unification status.

## A-04: Multi-DB Ambiguity (was: two DBs with different content)

The repair sprint was supposed to:
- Investigate DB contents (M-05a)
- HUMAN decides consolidation strategy (M-05b)
- Execute consolidation

**Verify:**
1. How many web persistence databases exist now?
   `ls data/web_persistence*.db`
2. Does `src/services/db_locator.py` still have the `prefer=` ambiguity?
   Or does it now resolve to a single canonical DB?
3. What is in the canonical DB?
   - Beliefs count, constraints count, bridges count
   - Are beliefs tagged with provenance/tier (panel_calibrated vs
     extraction_derived)?
4. Run the belief seeder. Does it target the correct DB?
5. Run any code that queries beliefs (e.g., web_of_belief.py). Does it
   read from the correct DB?

**Report**: DB count, resolution strategy, belief/constraint/bridge counts,
provenance tagging status.

## A-05: Gap Tracker Legacy Schema (was: uses parameter_range/evidence_base)

The repair sprint was supposed to:
- Rewrite gap_tracker.py to use canonical fields (M-04)

**Verify:**
1. Open `scripts/gap_tracker.py`. Does it still reference `parameter_range`
   or `evidence_base`? (grep for these strings)
2. Does it use `calibration_status` from the canonical schema?
3. Run it. Does its template count match:
   - `ls data/templates/*.json | wc -l`
   - The TRANSFER doc's stated total
   - `scripts/reconcile_counts.py` output (if E-04 was built)
4. Does its calibrated count match the number of templates with
   `calibration_status: "calibrated"` in the canonical schema?

**Report**: field references found, count consistency across sources.

## A-06: Sprint Brief Empty File (was: SPRINT_TASK_BRIEF_for_Cowork.md = 0 lines)

**Verify:**
1. Does `docs/SPRINT_TASK_BRIEF_for_Cowork.md` still exist?
2. If yes: `wc -l` — is it still empty?
3. Is there now ONE clear sprint brief (not two)?
4. Do all filename references in the surviving brief resolve to actual
   files? Check every referenced path.

**Report**: brief status, reference resolution.

## A-07: Template Count Ambiguity (was: 151 vs 153 vs 174 vs 184)

**Verify:**
1. Does `scripts/reconcile_counts.py` exist? (E-04)
2. Run it. Do all sources agree?
   - JSON files on disk
   - ae.db templates table
   - TRANSFER doc stated total
   - gap_tracker output
3. What is the ACTUAL authoritative template count now?

**Report**: counts from each source, discrepancies.

## A-08: Extra Warrant Types in Code (was: 3 AE types mixed with CMR types)

The repair sprint was supposed to:
- Refactor into separate enum (M-06)

**Verify:**
1. Open `src/services/bridge_warrants.py`. Is there a separate
   `EvidenceEvaluationType` enum (or similar)?
2. Does the `BridgeType` enum contain ONLY the 6 canonical CMR types
   (+ THEORETICAL_DEFAULT if applicable)?
3. grep the codebase for references to EPISTEMIC_COHERENCE_WARRANT,
   ARGUMENTATIVE_WARRANT, EPISTEMIC_VIGILANCE_WARRANT. Do they all
   reference the new enum, not BridgeType?
4. Run tests: `pytest tests/ -q --maxfail=5`

**Report**: enum separation status, orphan references, test results.

## A-09: Document Sprawl (was: 479 files, 8 CURRENT, 246 UNKNOWN)

The repair sprint was supposed to:
- Classify all files (G-01)
- Move ARCHIVE to docs/archive/
- Add SUPERSEDED headers

**Verify:**
1. Does `docs/archive/` exist? How many files in it?
2. How many files remain in `docs/` (not counting archive)?
3. Does `docs/CLAUDE.md` have a SUPERSEDED header? (R-13)
4. Does `docs/02-20_10_Panel_Launch_Briefing_ImplicitExplicit.md` have
   a SUPERSEDED or DO-NOT-USE header?
5. Count files in docs/ with no status classification. (Should be 0.)
6. Pick 10 random files from docs/ (not archive). For each, verify it
   is actually CURRENT — referenced by PROJECT_STATE.md or actively used
   by the pipeline.

**Report**: file counts (docs/, docs/archive/), unclassified count,
spot-check results.

## A-10: Test Suite (was: 15 failed, 4049 passed, 18 skipped)

**Verify:**
1. Run `pytest -q --maxfail=30`
2. Report: passed, failed, skipped
3. For each failure: is it the same failure from the Feb 22 run, or new?
4. Specifically check:
   - `test_full_trace_nature_view_claim` — was failing because VIEW1
     not matched (template scanner skip). Still failing?
   - `test_all_150_files_load` — template count hardcoded to 150. Was
     this updated?
   - `test_active_templates_map_to_existing_theories` — 108 templates
     had invalid theory refs. Still failing?

**Report**: pass/fail/skip counts, comparison to Feb 22 baseline, new
failures.

---

# PART B: ONGOING HEALTH CHECK

Everything in Part A checked the repairs. Part B checks the system's
current health regardless of what was repaired. This is the standing
audit that should be rerun periodically.

## B-01: Credence Formula Consistency

Same as original audit §1.1. Search every document in docs/ for the
three-factor formula. Report any inconsistencies.

`P(CNFA effect) = P(parent theory) × P(bridge) × P(CNFA-specific)`

Is it stated identically everywhere? Does code implement it correctly?
Does `compute_bridged_credence()` in bridge_warrants.py match the spec?

## B-02: T1 Roster Consistency

Same as original §1.2. Authoritative roster: 10 frameworks (PP, SN, DP,
DT, NM, IC, MS, EC, CB, MSI) in TRANSFER doc.

Search every document. Report any that disagree. Pay particular attention
to any NEW documents created during the repair sprint that might have
introduced errors.

## B-03: Bridge Warrant Hierarchy Consistency

Same as original §1.4, but now also check:
- Does the BridgeType enum in code match the 6-level hierarchy in docs?
- Is EvidenceEvaluationType properly separated?
- Do all calibrated templates (including newly extracted MEMORY-I and
  MULTI-I) have valid warrant types?
- Stale docstring at bridge_warrants.py:30 (Constitutive 0.85) — was it
  fixed?

## B-04: Per-Template Compliance Audit

**THIS WAS NOT DONE IN THE FIRST AUDIT.** The original prompt (§4.1)
asked for a per-template compliance table, but no auditor completed it.
Do it now.

For EVERY calibrated template (all ~53), verify against
OPUS_REVIEW_GUIDE.md §4 mandatory outputs:

| Template ID | Panel | mechanism_chain complete? | All params have confidence? | bridge_warrant assigned? | confidence ≤ ceiling? | THEORETICAL_DEFAULT flags where needed? | residual_gaps specified? | population_modifiers present? | architectural_modifiers present? | cross_template_interactions present? |
|-------------|-------|--------------------------|---------------------------|------------------------|----------------------|----------------------------------------|------------------------|------------------------------|--------------------------------|-------------------------------------|

Mark each cell: YES / NO / PARTIAL (what's missing) / N/A.

This table becomes a standing artifact. Save it as
`docs/TEMPLATE_COMPLIANCE_AUDIT.md`.

**Automated approach**: If the canonical schema validator (E-01) exists,
this table can be generated programmatically. Write a script if possible:
`scripts/audit_template_compliance.py` that reads every calibrated
template and checks each column.

## B-05: Cross-Template Interaction Integrity

For every cross-template interaction flag in every completed panel output:

1. Does the source template exist in data/templates/?
2. Does the target template exist in data/templates/?
3. Do the shared variables use canonical names (from E-03a)?
4. Are there still orphan routing targets (SC-III, VF-III, SPATIAL-II,
   etc.) that don't map to any current sprint panel?
5. Are there still circular dependencies (LIGHT-I ↔ VISUAL-I)?
   If so, are they documented with anti-double-counting rules?

Report the interaction graph as a table:

| Source Template | Target Template | Shared Variable | Status |
|----------------|----------------|-----------------|--------|

## B-06: Panel Output Machine-Parseability

The Feb 22 Codex audit found 0 machine-parseable fenced JSON blocks in
panel output markdown files.

1. Check ALL completed panel outputs (7 panels). Do any now contain
   fenced ```json blocks that can be extracted programmatically?
2. Does `scripts/extract_panel_templates.py` (E-05) exist as a
   general-purpose extractor? Or is it still hardcoded to one file?
3. For MEMORY-I and MULTI-I (extracted during the repair sprint): were
   the JSONs extracted using canonical field names?

## B-07: Toulmin Integration Status

The Toulmin foundation (TJ-01, TJ-02, TJ-07) was supposed to be built
during the repair sprint.

1. Does the canonical schema include Toulmin justification fields?
2. Does `scripts/validate_toulmin.py` exist?
3. Has the panel meta-prompt been updated to require Toulmin output?
4. Do the MULTI-I Toulmin appendices (9 produced) conform to whatever
   schema was defined?
5. Is there a plan for retroactive Toulmin on VISUAL-I through STRESS-I?

## B-08: Cowork Resume Readiness

The Cowork pipeline is halted. PROJECT_STATE.md defines a resume gate
with ~10 conditions. For each condition:

| Condition | Met? | Evidence |
|-----------|------|----------|
| E-01 schema exists and validates | | |
| M-01 migration complete | | |
| E-02 ceiling lint exists | | |
| M-02b ceiling violations adjudicated | | |
| E-03a variable ontology drafted | | |
| M-04 gap tracker uses current schema | | |
| E-04 counts reconciled | | |
| TJ-01 Toulmin schema in place | | |
| TJ-07 forward integration complete | | |
| G-03 sprint brief consolidated | | |

If ANY condition is not met: Cowork should NOT resume. Report which
conditions are blocking and what remains to be done.

## B-09: Extraction Pipeline Health

Same as original §7, updated:

1. Does `data/production/realtime_pdf_confirmed_rows.csv` exist?
   Row count? (Was 172,091)
2. The Feb 22 audit found claim_text is NULL in all 172K rows. Is this
   still the case? If so, what field contains the actual claim content?
3. Can extraction outputs be mapped to calibrated templates? What's
   the join path?
4. Queue status: how many papers queued, completed, error?

## B-10: Web of Belief Operational Status

1. Which database is canonical? (Should be resolved by M-05b.)
2. Run `compute_bridged_credence()` on 3 randomly chosen calibrated
   templates. Does it produce a valid number? Does the number match
   manual computation of P(T1) × P(bridge) × P(CNFA-specific)?
3. Can the coherence computation (scalable_coherence.py) run on the
   current belief set?
4. Do the 10 theory agent profiles load correctly?
5. Is there an end-to-end path from: paper → extraction → claim →
   belief → credence score? If not, where does it break?

## B-11: Context Window Risk for Remaining Panels

The Feb 22 Gemini audit identified CROSSCUT-I as a context collapse risk
(requires all prior panel outputs, estimated 1.5-2MB).

1. Estimate context load for each remaining panel:
   - MUSIC-I (13 templates)
   - THERMAL-I (templates TBD)
   - CREATIVE-I (templates TBD)
   - NEUROMOD-I (highest input load per Codex: 6,288 lines)
   - CROSSCUT-I (ALL prior panel outputs)
2. Does a synthesis script exist that compresses prior panel outputs
   into a <10KB summary for CROSSCUT-I?
3. For NEUROMOD-I: has the allostatic integration math been specified?
   (HUMAN was supposed to provide this.)

## B-12: PROJECT_STATE.md Accuracy

PROJECT_STATE.md is the coordination protocol. It must be accurate.

1. For every task marked COMPLETED in PROJECT_STATE.md: verify the
   stated output file exists at the stated path.
2. For every task marked BLOCKED: verify the stated dependency is
   actually incomplete.
3. For every task marked AVAILABLE: verify it has no uncompleted
   dependencies.
4. Is the changelog consistent with the actual file modification dates?
5. Are there completed tasks NOT recorded in PROJECT_STATE.md?

---

# PART C: NEW RISKS

The first audit couldn't catch problems that didn't exist yet. The repair
sprint may have introduced new ones. Look for:

## C-01: Migration Damage

Did M-01 (schema migration) or M-03b (variable migration) corrupt any
template data?

1. Pick 10 calibrated templates. For each, compare the current JSON to
   the original panel output markdown. Do the VALUES match? (Field names
   should have changed; values should not.)
2. Are there any templates where migration created invalid JSON?
3. Are there any templates where migration lost data (fields present in
   the original that are now missing)?

## C-02: Enforcement Tool False Positives/Negatives

1. Create a deliberately non-compliant template JSON (wrong field names,
   ceiling violation, unregistered variable). Run ALL lints against it.
   Do they ALL catch the problems?
2. Create a deliberately compliant template. Run all lints. Do they
   ALL pass it?
3. Are there edge cases the lints miss? (e.g., nested confidence values
   inside mechanism_chain steps, population modifier variables, etc.)

## C-03: Sprint Instruction Compliance

Did CC and AG actually follow their instructions?

1. Read CC_REPAIR_SPRINT_INSTRUCTIONS.md. For each task assigned to CC,
   verify the stated acceptance criteria are met.
2. Read AG_REPAIR_SPRINT_INSTRUCTIONS.md. For each task assigned to AG,
   verify the stated acceptance criteria are met.
3. Were any tasks done out of order (violating wave dependencies)?
4. Were any tasks skipped without documentation?

## C-04: New Documents Health

The repair sprint created several new files (schemas, scripts, reports).
For each new file:

1. Is it referenced in PROJECT_STATE.md?
2. Is it in the correct directory (schemas/, scripts/, docs/)?
3. Does it have a header explaining its purpose?
4. Is it internally consistent (no placeholder text, no TODO markers,
   no contradictions with existing authority docs)?

---

# OUTPUT FORMAT

Produce a single markdown document: `SYSTEM_AUDIT_REPORT_v2_[DATE].md`

Structure:
1. **Executive Summary**: One paragraph. System health: HEALTHY / DEGRADED /
   CRITICAL. One-sentence verdict on Cowork resume readiness.
2. **Part A Results**: Repair verification. For each of A-01 through A-10:
   VERIFIED FIXED / PARTIALLY FIXED (details) / NOT FIXED / MADE WORSE.
3. **Part B Results**: Ongoing health. For each of B-01 through B-12:
   HEALTHY / CONCERN (details) / CRITICAL.
4. **Part C Results**: New risks. For each of C-01 through C-04:
   NONE FOUND / FOUND (details).
5. **Per-Template Compliance Table** (B-04): the full table, saved also
   as a standalone artifact.
6. **Recommendations**: Top 5 remaining risks. Top 5 actions before
   Cowork resumes. Explicit go/no-go recommendation.

**Cite file paths and line numbers. Quote conflicting text verbatim.
Err on the side of reporting too much.**

---

# SCHEDULING

This audit should be run:
- **Once** immediately after the repair sprint completes (primary purpose)
- **Once** after each batch of 2-3 panels completes (health check)
- **Once** before CROSSCUT-I (final pre-capstone verification)

The per-template compliance table (B-04) should be regenerated after
every panel extraction.

---

*RUTHLESS_SYSTEM_AUDIT_v2.md*
*Post-repair verification + ongoing health check*
*Run in: CC → AG/Gemini → Codex. Cross-validate findings.*
