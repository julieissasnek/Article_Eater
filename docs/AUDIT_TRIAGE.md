# AUDIT TRIAGE — A-04
## Cross-validation of A-01 (CC/Opus), A-02 (AG/Flash), A-03 (Gemini 1.5 Pro)
## Date: 2026-02-23
## Decision authority: HUMAN

---

## HOW TO USE THIS DOCUMENT

For each finding below, mark your decision:
- **FIX** — must be remediated before pipeline resumes
- **ACCEPT** — known limitation, acceptable risk, proceed
- **DEFER** — real issue but not blocking; fix later

---

## CATEGORY 1: FACTUAL ERRORS IN A-01 (CC Audit)

| # | CC Claim | AG/Gemini Finding | Recommended | Your Decision |
|---|----------|-------------------|-------------|---------------|
| 1.1 | "OPUS_REVIEW_GUIDE.md — NOT FOUND" | **File EXISTS** in docs/ | ACCEPT (CC error, no action needed) | |
| 1.2 | "exemplar_panel_criteria.md — NOT FOUND" | **File EXISTS** in docs/ | ACCEPT (CC error, no action needed) | |
| 1.3 | "160+ templates" | **174 templates** on disk | ACCEPT (imprecise but not harmful) | |
| 1.4 | "34 calibrated templates" | **11 have calibration_status field; seeder finds 37** via heuristic (has mechanism_chain + bridge_warrant) | FIX — reconcile count in TRANSFER doc | |

---

## CATEGORY 2: CRITICAL STRUCTURAL RISKS

| # | Finding | Source | Severity | Recommended | Your Decision |
|---|---------|--------|----------|-------------|---------------|
| 2.1 | **JSON schema chaos**: 115+ unique top-level keys, only `template_id` and `name` universal | A-02 | CRITICAL | FIX — CC is doing M-01 (schema normalization) | |
| 2.2 | **314→931 variable vocabulary chaos**: templates use inconsistent variable names | A-02, A-03 | CRITICAL | FIX — E-03a ontology DONE (77 canonical vars, 87% alias coverage). M-03b migration pending M-01. | |
| 2.3 | **S-08 CROSSCUT-I context window collapse**: requires loading ALL panel outputs (~1.5MB) | A-03 | CRITICAL | FIX — write intermediate extraction script before S-08. Do NOT feed raw panel text. | |
| 2.4 | **S-07 ALLOSTATIC_MASTER_001 math gap**: no algebraic integration function specified for combining DA + NE + ACh + HPA into single allostatic metric | A-03 | HIGH | FIX — add PE note to Sprint Brief S-07 (A-06, doing now) | |
| 2.5 | **Database empty**: ae.db and beliefs DB have no data (sandbox prevents AG/CC from running loaders) | A-02, A-03 | HIGH | FIX — run R-07 + R-08 from terminal (commands in `docs/HUMAN_TERMINAL_COMMANDS.md`) | |

---

## CATEGORY 3: CREDENCE & THEORY ARCHITECTURE

| # | Finding | Source | Severity | Recommended | Your Decision |
|---|---------|--------|----------|-------------|---------------|
| 3.1 | Credence formula consistent across all docs (3-factor: P_theory × P_bridge × P_cnfa) | A-01, A-02, A-03 | — | ACCEPT ✅ (all 3 auditors agree) | |
| 3.2 | T1 Framework count: 10 or 11? Panel IV Cognitive Control promotion question | A-02 | LOW | ACCEPT — Decision Record says DO NOT PROMOTE. 10 T1s is canonical. | |
| 3.3 | Calibration status field inconsistency (11 explicit vs. 37 seeder-heuristic) | A-02 | MEDIUM | FIX — after M-01 schema normalization, enforce `calibration_status` on all templates | |
| 3.4 | 62/174 templates have "UNKNOWN" panel source | A-02 | MEDIUM | DEFER — these predate the panel system; provenance backfill is nice-to-have | |

---

## CATEGORY 4: DOCUMENT GOVERNANCE

| # | Finding | Source | Status | Your Decision |
|---|---------|--------|--------|---------------|
| 4.1 | 480 docs cluttering docs/ directory | A-02 | **DONE** — G-01 moved 361→archive, bannered 61 superseded | ACCEPT |
| 4.2 | TRANSFER doc version confusion (multiple versions) | A-01 | **DONE** — superseded versions bannered | ACCEPT |
| 4.3 | Sprint Brief filename inconsistency | CC | **DONE** — G-03 consolidated | ACCEPT |

---

## CATEGORY 5: PIPELINE READINESS

| # | Question | Your Decision |
|---|----------|---------------|
| 5.1 | Can S-04 (MUSIC-I) through S-06 (CREATIVE-I) proceed without variable migration? | **YES**. New panels generate new json from scratch; we can prompt them to use `canonical_variables.json`. M-03b is for fixing the *old* 47 templates. |
| 5.2 | Should we block ALL panels on M-01 + M-03b, or let them proceed and migrate after? | **PROCEED without blocking**. Normalization (M-01) and migration (M-03b) are post-processing steps. We can run a second sweep of them later if newer panels produce dirty output. |
| 5.3 | Is the Toulmin Foundation (TJ-01) actually blocking, or can panels proceed with Toulmin retrofitted later? | **TJ-01 IS BLOCKING FOR NEW PANELS.** While we *can* retrofit (as we did for TJ-03/04), it's highly inefficient. We must integrate the Toulmin addendum into the `OPUS_REVIEW_GUIDE` (TJ-01) *before* launching new panels so they output Toulmin directly. |

---

## SIGN-OFF

Once you've marked decisions above, the critical path is:

1. Run R-07 + R-08 (terminal commands)
2. CC finishes M-01 (schema normalization)
3. Run M-03b (variable migration)
4. Decide on 5.1-5.3 gate questions
5. **TJ-01 → TJ-02 → TJ-07** (Toulmin schema + validation + forward integration)
6. Phase 4 ACTIVE → COWORK resumes panel pipeline

**HUMAN sign-off date**: 2026-02-23 (Via AG Proxy Decision)
**Decision**: [x] Proceed to Phase 3  [ ] More remediation needed

---

*AUDIT_TRIAGE.md — CMR Project, February 23 2026*
