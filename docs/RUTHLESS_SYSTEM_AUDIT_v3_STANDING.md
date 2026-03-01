# RUTHLESS SYSTEM AUDIT v3 — STANDING HEALTH CHECK
## Post-Repair Verification & Ongoing CI/CD Validation
## February 2026

---

# CONTEXT

This system has just successfully cleared the "Ruthless Repair" mini-sprint. The major structural violations—specifically A-01 (Bridge Warrant Ceilings), A-02 (Canonical Variables), and A-10 (Test Pipeline Failures)—have been permanently resolved and wrapped into self-healing CI/CD test gates. 

The current system state is:
- **Calibrated Templates**: Operating with 100% adherence to schema maximum confidence ceilings.
- **Canonical Variables**: All template mechanism chains now draw exclusively from the unified `schemas/canonical_variables.json` ontology.
- **Test Suite**: Fully green. `pytest` now wraps both the variable linting and the ceiling linting to prevent structural drift.
- **Web of Belief**: Pruned and consolidated to pure, high-signal claims and theories.

Your job as the Auditor (Codex/Claude/Gemini) is to perform a **standing review** of the codebase *now* that these patches are secured. The manual verification phase is over; we are now relying on the machine validations. Do the integrations hold water?

---

# SECTION 1: EXECUTE THE AUTOMATED GATES

Do not trust self-reports. Run the following commands sequentially and report the literal output. If any gate fails, immediately halt the audit and report the exact trace.

## 1.1 The Bridge Ceiling Test (A-01 CI/CD)
Run the automated cap verification:
`pytest tests/test_bridge_ceilings.py -v`
- Does the test pass? 
- Are there truly zero violations remaining across the entire template corpus?

## 1.2 The Canonical Variable Enforcer (A-02 CI/CD)
Run the ontology enforcer:
`pytest tests/test_canonical_variables.py -v`
- Does the ontology check pass cleanly?
- Run `python3 scripts/lint_variables.py` directly. Does it confirm that all legacy variables sit safely within the `UNMAPPED_LEGACY` bucket inside `canonical_variables.json`?

## 1.3 Baseline System Tests (A-10 CI/CD)
Run the core test suite:
`pytest tests/ -v -k "not test_bridge_ceilings and not test_canonical_variables"`
- Does the entire suite pass green?
- Pay special attention to `test_cross_pipeline_salk_view_consistency`. Did the heuristic terminology fix ("promotes" vs unknown directionality) hold?

---

# SECTION 2: THEORETICAL ARCHITECTURE vs RUNTIME REALITY

## 2.1 The Belief Graph Integrity
Execute: `PYTHONPATH=. python3 -m src.services.web_accumulator stats`
- Verify the total belief count exactly matches the pruned ~4,888 empirical beliefs.
- Are there any `unresolved` junk items sneaking back into the pipeline?

## 2.2 The Toulmin Justification Schema
Inspect the most recently updated template from the `SOCIAL-I` or `VISUAL-I` panels in `data/templates/`.
- Look directly at the JSON. Does the `toulmin_justification` dictionary structure exist comprehensively with `data`, `warrant`, `backing`, `qualifier`, `rebuttal`, and `competing_accounts`?
- Identify if any nested mechanism logic appears to bypass this schema.

## 2.3 Theory Profiles & Routing
Review the internal profiles situated at `src/cmr/theory_profiles/`.
- Are all 10 Tier-1 formal profiles properly exporting their runtime dicts without Python syntax errors? 
- Can the extraction pipeline successfully load these targets?

---

# SECTION 3: THE FINAL DETERMINATION

Based on your execution of the automated gates and your structural inspection: 
1. Are the CI/CD wrappers written in `test_bridge_ceilings.py` and `test_canonical_variables.py` sufficiently ruthless to block future drift? 
2. Are there any lurking architectural deficits bridging the conceptual theory to the runtime database?

Do not hallucinate praise. Write your final response as a **RUTHLESS AUDITOR'S REPORT**. Detail exact logs, point out any lingering misalignments, and if the baseline is bulletproof, issue the authorization to activate Cowork Phase 4.
