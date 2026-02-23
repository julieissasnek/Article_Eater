# RUTHLESS SYSTEM AUDIT PROMPT — POST-SPRINT 10
## Full Reality Check — Theoretical Architecture + Codebase
## February 23, 2026
## Run in: CX (Codex Terminal)

---

# CONTEXT

This system has just undergone a massive stabilization sprint (Sprint 10). 
The following major changes were introduced since the last audit:
1. **Database & Extraction**: A massive extraction dump was successfully loaded into `ae.db` (172k findings).
2. **Template→Belief Seeder**: 34 calibrated templates were successfully seeded into `data/web_persistence.db`.
3. **Web of Belief Pruning**: All "unresolved" and "unknown" junk extraction beliefs (11,000+) were purged, leaving only 4,888 high-signal, domain-classified empirical beliefs and 40 theoretical beliefs.
4. **Canonical Variable Ontology**: `schemas/canonical_variables.json` was created and populated with 77 canonical variables.
5. **Variable Migration**: `scripts/migrate_variables.py` was built and run to normalize the 300+ variables across the templates.
6. **Test Suite**: A `conftest.py` proxy was added to sandbox testing, and the 1,300+ failing tests are now entirely GREEN/PASSING.
7. **Retroactive Toulmin Justification**: Toulmin justifications have been successfully retrofitted to all legacy panels (VISUAL, SPATIAL, LIGHT, STRESS, SOCIAL, MEMORY, MULTI).
8. **Theory Profiles**: 10 Tier 1 Theory Profiles have been created as `.py` modules under `src/cmr/theory_profiles/`.

Your job as the Codex Auditor is to run a ruthless evaluation of the system *now* that these patches are in. Have we truly closed the Reality Gaps identified on Feb 22, or are there lingering structural misalignments?

---

# SECTION 1: THEORETICAL ARCHITECTURE vs RUNTIME REALITY

## 1.1 The Belief Graph Health
Run `cd /Users/davidusa/REPOS/Article_Eater_PostQuinean_v1 && PYTHONPATH=. python3 -m src.services.web_accumulator stats`.
- Does the total belief count exactly match 4,888?
- Does the constraint count exactly match 6,899?
- Are there any 'unresolved' items sneaking back into the pipeline?

## 1.2 The Toulmin Justification Schema
Look at the most recently saved template from VISUAL or SOCIAL (e.g., `data/templates/SOCIAL_I_...json` or `VISUAL...`). 
- Does it contain the literal `toulmin_justification` dictionary structure with `data`, `warrant`, `backing`, `qualifier`, `rebuttal`, and `competing_accounts` as prescribed by the `validate_toulmin.py` script?
- Or did the retroactive assignment miss certain frameworks? Check heavily modified schemas.

## 1.3 Canonical Variables Alignment
Run `python3 scripts/lint_variables.py` (which checks templates against `schemas/canonical_variables.json`).
- Does the linter cleanly pass with 0 unrecognized variables?
- Check if mechanism chains in Gen-2 templates (like VIEW or SC) are actually using these aligned canonical names. 

## 1.4 Test Suite Reality
Run `pytest -v` via the CLI.
- Does the suite actually pass?
- Does `test_cmr_building_eval.py` flag any severe deficits correctly, or does it still hang/timeout?

## 1.5 The Theory Profiles
Check the `src/cmr/theory_profiles/` directory that was just created.
- Are all 10 T1 formal profiles present and returning their expected `get_profile()` dicts? 
- Is `test_theory_profiles.py` passing?

---

# SECTION 2: IDENTIFYING THE NEXT CRITICAL PATH

Based on your audit of the above 5 areas, what broken windows remain? 
Do not be polite. If a patch from Sprint 10 is structurally flawed or didn't actually persist, call it out. 

Write your final response as a `SUMMARY OF LINGERING REGRESSIONS`. If the baseline is truly stable, authorize the initiation of the autonomous Cowork pipeline to calibrate the remaining 117 templates.
