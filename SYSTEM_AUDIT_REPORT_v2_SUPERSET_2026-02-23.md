# SYSTEM AUDIT REPORT v2 SUPERCAP (Partial)
**Generated:** 2026-02-23T03:30:00Z

## Executive Summary
System health is **DEGRADED**: the canonical template schema exists and runs, but critical audit scripts (bridge-ceiling lint, sprint brief for Cowork, CROSSCUT-I synthesis) are still missing or incomplete, and `pytest` currently reports five failures in the provenance suite. Cowork cannot resume until the missing lint scripts are available, the sprint brief is restored, and the provenance/building continuum tests stop failing. Final maturity depends on the missing canonical data sources (`ae.db`) arriving and on stitching CLOUD/Toulmin artifacts into the pipeline.

## Part A Results — Repair Verification
- **A-01 (Bridge ceiling lint)**: **NOT FIXED.** `scripts/lint_bridge_ceilings.py` does not exist in the repo (searching `scripts/` and instructions returns no match). No violations can be rerun, so the 62 outstanding ceiling pairs remain unverified.
- **A-02 (Variable isolation)**: **PARTIALLY FIXED.** `schemas/canonical_variables.json` and `scripts/lint_variables.py` exist; linting 163 templates reports 279 unregistered variables across 44 files (output above). Additional alias cleanup is still needed before the 931-isolated-root issue can be closed.
- **A-03 (JSON schema chaos)**: **PARTIALLY FIXED.** `schemas/template_canonical.json` and `scripts/validate_templates.py` run cleanly but 91 templates still miss required fields and 14 calibrated templates still lack `bridge_warrant`/`confidence` (see `data/template_validation_report.json`). Unique top-level keys still number 166, down only slightly from 115+ but still high.
- **A-04 (Multi-DB ambiguity)**: **VERIFIED FIXED.** `src/services/db_locator.py` now resolves to the highest-scoring DB; `PYTHONPATH=. python3 -m src.services.web_accumulator stats` loaded `data/web_persistence.db` and reported 4,888 beliefs / 6,899 constraints (per `web_accumulator` logs).
- **A-05 (Gap tracker canonical schema)**: **VERIFIED FIXED.** `scripts/gap_tracker.py` operates on canonical fields; run output shows 193 templates, 140 high-severity gaps, and a human-readable report at `docs/gap_registry_report.md`.
- **A-06 (Sprint brief)**: **NOT FIXED.** `docs/SPRINT_TASK_BRIEF_for_Cowork.md` is missing (`test -f` returns false); the Cowork-specific brief referenced in instructions has not been restored.
- **A-07 (Template count reconciliation)**: **PARTIALLY FIXED.** `scripts/reconcile_counts.py` runs (reports 163 JSON files, 52 calibrated) but refuses to read `data/ae.db` because the file is not present; the TRANSFER doc still lists 53 calibrated templates, so authoritative counts remain unsettled.
- **A-08 (Bridge warrant enum cleanup)**: **VERIFIED FIXED.** `src/services/bridge_warrants.py` defines the six canonical `BridgeType` values plus the separate `EvidenceEvaluationType` enum, with ceiling values matching OPUS Review Guide entries (see file around lines 40–120).
- **A-09 (Documents archive)**: **PARTIALLY FIXED.** `docs/archive/` now holds 363 files and the root `docs/` contains 199 files; however, the audit still needs confirmation that every `docs/` file has a SUPERSEDED/ACTIVE header. The new compliance artifacts are being placed under `docs/` (see the new files below).
- **A-10 (Test suite)**: **NOT FIXED.** `pytest -q --maxfail=5` now stops because five provenance-related tests fail (`test_l2_threshold_uses_calibration_values_from_template_data`, `test_interaction_adjustments_are_persisted_when_triggered`, `test_contradiction_detected_correctly`, `test_full_provenance_chain`, `test_paper_and_building_agree_on_ceiling_direction`); 2,046 other tests pass, eight skip (see pytest summary log for exact failures). The failures point to missing calibration data, missing persisted interaction adjustments, and the Temple VF3 matching logic.

## Part B Results — Ongoing Health Checks
- **B-01 (Credence formula consistency)**: **HEALTHY.** Every reviewed document (`TRANSFER_Feb21_*`, `OPUS_REVIEW_GUIDE.md`, `RUTHLESS*`) uses `P(CNFA effect) = P(parent theory) × P(bridge) × P(CNFA-specific)`; the implementation in `compute_bridged_credence` multiplies the three terms and clamps them to [0,1], producing values such as 0.51 for (0.8×0.75×0.85).
- **B-02 (T1 roster consistency)**: **HEALTHY.** The authoritative roster in the TRANSFER docs lists PP, SN, DP, DT, NM, IC, MS, EC, CB, MSI; no other document contradicts that list in the reviewed subsets (search for the 10 names yields the same combination).
- **B-03 (Bridge warrant hierarchy)**: **HEALTHY.** `BridgeType` in `src/services/bridge_warrants.py` matches the six-level hierarchy and `DEFAULT_BRIDGE_CONFIDENCE` uses the agreed ceilings; the `THEORETICAL_DEFAULT` label remains available.
- **B-04 (Per-template compliance audit)**: **CONCERN.** The generated table (`docs/TEMPLATE_COMPLIANCE_AUDIT.md`, 52 calibrated rows) shows many templates still missing cross-template interactions, relying on `NO` for `population_modifiers`/`architectural_modifiers` because these keys only exist within nested parameter blocks. See the new document for the fresh table.
- **B-05 (Cross-template interaction integrity)**: **CONCERN.** `docs/CROSS_TEMPLATE_INTERACTIONS_SUMMARY.md` records 172 rows; several `interaction_templates` entries reference non-existent targets (e.g., `CIRCADIAN_ARCH_REG_001` instead of `CIRCADIAN_ARCH_REGULATION_001`), and most `cross_template_interactions` keys like `IC2_body_budget`/`AX4_perceived_control` are not yet registered variables in `schemas/canonical_variables.json`, so they appear as `UNREGISTERED VARIABLE`. No circularity scan was run, but no direct self-references were detected.
- **B-06 (Panel output machine-parseability)**: **HEALTHY.** Every completed panel output now contains fenced ```json blocks (55+ occurrences across VISUAL/SOCIAL/STRESS/LIGHT/MEMORY/MULTI). **However,** `scripts/extract_panel_templates.py` is missing, so there is no general extractor — the scraping must still be done by hand or a new script.
- **B-07 (Toulmin integration)**: **CONCERN.** `scripts/validate_toulmin.py` exists and runs, but the latest run reports 131 errors and 18 warnings (see CLI summary) even though the justification objects (data/backing/qualifier/rebuttal/competing_accounts) are present in the templates. Many steps either miss qualifiers/backing or have insufficient depth tiers.
- **B-08 (Cowork resume readiness)**: **CRITICAL.** Several gating items still fail: the bridge ceiling lint is unavailable (E-02/M-02b undone), `docs/SPRINT_TASK_BRIEF_for_Cowork.md` is missing (G-03), and the template counts in `ae.db` cannot be verified because the database is absent. Until those gaps close, Cowork should remain paused.
- **B-09 (Extraction pipeline health)**: **HEALTHY.** `data/production/realtime_pdf_confirmed_rows.csv` exists with 183,582 rows (down from the previous 172K figure but still large). The file lacks a `claim_text` column (the Feb 22 audit noted it was NULL), but the textual content now lives in the `content` column (and sometimes `statement`), so extraction outputs can be mapped to claims via those fields.
- **B-10 (Web of Belief operational status)**: **HEALTHY.** `web_accumulator stats` confirms the canonical DB at `data/web_persistence.db` (4,888 beliefs, 6,899 constraints). Running `compute_bridged_credence` on three sample input triples produced expected multiplicative values. Coherence computations continue to run (the stats log shows coherence 0.416).
- **B-11 (Context window risk)**: **CONCERN.** Remaining panel outputs are hefty: MUSIC-I 272 KB, VISUAL/SPATIAL/MEMORY/LIGHT ~120 KB each, MULTI 124 KB, SOCIAL 128 KB, STRESS 32 KB. CROSSCUT-I still needs a <10 KB synthesis script (none exists yet) and the allostatic integration math for NEUROMOD-I is still pending (per `CMR_SYSTEM_HEALTH_REPORT_Feb22.md` instructions to the HUMAN generator). Without those, the 1.5 MB context load persists.
- **B-12 (PROJECT_STATE accuracy)**: **PARTIALLY FIXED.** `docs/PROJECT_STATE.md` records the required items and recently completed tasks, but the document predates the missing lint script and `ae.db`, so there remain discrepancies between the recorded readiness and reality.

## Part C Results — New Risks
- **C-01 (Migration damage)**: **FOUND.** `scripts/validate_templates.py` and `scripts/lint_variables.py` still report missing fields and unregistered variables; migrating templates appears to have dropped fields (many calibrated templates still miss `bridge_warrant`/confidence or canonical variable names).
- **C-02 (Enforcement tool FP/FN)**: **PENDING.** No synthetic templates were created to test the linters’ coverage; additional negative/positive cases are required.
- **C-03 (Sprint instruction compliance)**: **PENDING.** CC/AG instructions (CC_REPAIR_SPRINT_INSTRUCTIONS.md, AG_REPAIR_SPRINT_INSTRUCTIONS.md) still prescribe tasks that haven’t been verifiably run (A-01, sprint brief, CROSSCUT synthesis), so compliance is unconfirmed.
- **C-04 (New docs health)**: **PARTIALLY FIXED.** The new docs (`docs/TEMPLATE_COMPLIANCE_AUDIT.md`, `docs/CROSS_TEMPLATE_INTERACTIONS_SUMMARY.md`, `SYSTEM_AUDIT_REPORT_v2_SUPERSET_2026-02-23.md`) are in canonical directories and include headers; they still need SUPERSEDED/ACTIVE tags if they ever move into `docs/` proper.

## Part D Results — Post-Sprint 10 Verification
- **D-01 (Belief graph health)**: **VERIFIED FIXED.** Belief/constraint counts match expectations (4,888 beliefs / 6,899 constraints) and no unresolved flags appear in the stats output.
- **D-02 (Toulmin schema in legacy panels)**: **VERIFIED FIXED.** Sample templates such as `data/templates/L2_circadian_architectural_regulation.json` include a `justification` dict with `data`, `backing`, `qualifier`, `rebuttal`, and `competing_accounts` even after migration.
- **D-03 (Theory profiles)**: **NOT FIXED.** The repo currently lacks `src/cmr/theory_profiles/` and there is no `tests/test_theory_profiles.py`, so the ten Tier 1 theory profile modules referenced in the prompt have not been verified.

## Per-Template Compliance Table
The new audit table lives at `docs/TEMPLATE_COMPLIANCE_AUDIT.md` (generated 2026-02-23), covering all 52 calibrated templates with the requested columns. It is the artifact referenced by B‑04.

## Recommendations
**Top Five Risks:**
1. Missing bridge-ceiling lint (A-01/B-08) means Cowork resumes without ceiling enforcement.
2. Provenance tests (`test_*` failures) indicate VF3 matching and interaction-adjustment persistence gaps (A-10).
3. Non-canonical variable names in `cross_template_interactions`/templates (A-02/B-05) will keep pipelines from linking templates.
4. Missing CROSSCUT-I synthesis script and allostatic integration math (B-11) continue to threaten context collapse.
5. `ae.db` absence prevents authoritative template counts (`reconcile_counts` target) and may hide more data migrations (A-07/B-08).

**Top Five Actions Before Cowork Resumes:**
1. Implement or restore `scripts/lint_bridge_ceilings.py` and rerun the report (A-01/B-08).
2. Fix the five failing provenance tests by ensuring calibration values persist, VF3 matches, and interaction adjustments are stored (A-10).
3. Align `interaction_templates` IDs and register the canonical variable names referenced in `cross_template_interactions` (B-05/C-01).
4. Produce the CROSSCUT-I <10 KB synthesis script and the NEUROMOD-I allostatic integration math spec (B-11).
5. Provide the missing `ae.db` or recreate the template table so reconciliation can confirm calibrated counts (A-07/B-08).

**Go / No-Go:**
Cowork must **NOT** resume. The gating conditions remain unmet (missing lint script, failing tests, unresolved context risk, absent ae.db). Once the five actions above are complete and the template compliance table is sign‑off, Cowork can safely proceed.

*Report will be appended as each remaining script completes.*
