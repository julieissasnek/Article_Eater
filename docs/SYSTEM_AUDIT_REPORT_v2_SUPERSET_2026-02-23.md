# SYSTEM AUDIT REPORT v2 SUPERSET (2026-02-23)
**Auditor:** Antigravity (AG)  
**Date:** Feb 23, 2026  

## 1. Executive Summary
**System Health:** **DEGRADED (with significant recent structural improvements)**  
**Cowork Resume Readiness:** **NO-GO**

The system has made massive strides in schema standardization and Toulmin justification integration. All 103 calibrated templates successfully pass the new `template_canonical.json` structural validation. However, the system is not ready to resume Phase 4 Cowork. There are 272 unregistered mechanism variables across 48 templates, ~60 lingering bridge warrant ceiling violations, a broken test suite (`test_cross_pipeline_salk_view_consistency`), and hardcoded database paths causing scripts like `web_accumulator` and `reconcile_counts.py` to crash.

---

## 2. Part A Results: Repair Verification

*   **A-01: Bridge Warrant Ceiling Violations** — **PARTIALLY FIXED**
    *   `scripts/lint_bridge_ceilings.py` exists and functions correctly. However, a run reveals dozens of remaining violations (e.g., `MS_RIPPLE_REPLAY_002` mechanism confidences hitting 0.80 against a 0.60 ceiling).
*   **A-02: Variable Isolation** — **PARTIALLY FIXED**
    *   `schemas/canonical_variables.json` exists, but `scripts/lint_variables.py` reveals 48 templates with 272 unregistered variables.
*   **A-03: JSON Schema Chaos** — **VERIFIED FIXED (for Calibrated Tier)**
    *   `scripts/validate_templates.py` confirms 103/103 calibrated templates pass. Scaffold templates still have 72 failures due to missing mandatory fields. Unification is a vast success.
*   **A-04: Multi-DB Ambiguity** — **NOT FIXED**
    *   `web_persistence_v2.db` is the correct DB, but internal codebase references are severely fragmented. Core components still attempt to open `data/web_persistence.db` leading to `sqlite3.OperationalError` crashes.
*   **A-05: Gap Tracker Legacy Schema** — **VERIFIED FIXED**
    *   `parameter_range` and `evidence_base` have been purged.
*   **A-06: Sprint Brief Empty File** — **VERIFIED FIXED**
    *   The empty legacy brief no longer exists.
*   **A-07: Template Count Ambiguity** — **NOT FIXED**
    *   `scripts/reconcile_counts.py` exists but crashes entirely because it attempts to query the non-existent `web_persistence.db`.
*   **A-08: Extra Warrant Types in Code** — **VERIFIED FIXED**
    *   `src/services/bridge_warrants.py` successfully isolates 6 canonical `BridgeType`s from the `EvidenceEvaluationType`s.
*   **A-09: Document Sprawl** — **HEALTHY**
    *   Archives are cleanly separated.
*   **A-10: Test Suite** — **PARTIALLY FIXED**
    *   The test suite still fails structurally on `tests/test_cross_pipeline.py::test_cross_pipeline_salk_view_consistency`.

---

## 3. Part B Results: Ongoing Health

*   **B-01: Credence Formula Consistency** — **HEALTHY**
*   **B-02: T1 Roster Consistency** — **HEALTHY** (Confirmed 10 frameworks)
*   **B-03: Bridge Warrant Hierarchy** — **HEALTHY**
*   **B-04: Per-Template Compliance Table** — **COMPLETED**
    *   An automated generation script (`scripts/audit_template_compliance.py`) was written to handle string-or-dict provenance variability. It generated the full matrix table and saved it to `docs/TEMPLATE_COMPLIANCE_AUDIT.md`.
*   **B-05: Cross-Template Interaction Integrity** — **CONCERN**
    *   Variables are still bleeding out of the canonical schema list.
*   **B-06: Panel Output Machine-Parseability** — **HEALTHY**
*   **B-07: Toulmin Integration Status** — **HEALTHY**
    *   Retroactive injection succeeded. Legacy templates (e.g. `SOCIAL-I`) now have robust `justification` objects with `data`, `backing`, `qualifier`, etc.
*   **B-08: Cowork Resume Readiness** — **CRITICAL (NO-GO)**
    *   Failing Conditions: M-02b ceiling violations unresolved, M-03b variable migrations incomplete, E-04 count reconciler crashes.
*   **B-09: Extraction Pipeline Health** — **HEALTHY**
    *   Gemini implementation is running correctly for extraction logic.
*   **B-10: Web of Belief Operational Status** — **CONCERN**
    *   `web_accumulator` fails to run directly due to DB pathing.
*   **B-11: Context Window Risk** — **CONCERN**
*   **B-12: PROJECT_STATE.md Accuracy** — **CONCERN**

---

## 4. Part C Results: New Risks

*   **C-01: Hardcoded Legacy Database Paths**
    *   A major new risk discovered is that `src.services.web_accumulator` ignores the `AE_DB_PATH` environment variable entirely, hardcoding its target to `data/web_persistence.db`. This causes a cascading failure in `reconcile_counts.py`.
*   **C-02: String vs Dict Schemas**
    *   The `provenance` field in templates fluctuates between being a string (legacy) and a dictionary (new), which crashed the B-04 audit script before it was patched.

---

## 5. Part D Results: Post-Sprint 10 Completion Verification

*   **D-01: The Belief Graph Health** — **NOT VERIFIED (CRASHED)**
    *   As noted above, `web_accumulator stats` threw an `OperationalError` trying to open the old database.
*   **D-02: Toulmin Justification Schema in Legacy Panels** — **HEALTHY**
    *   Verified against `NM_SOCIAL_ISOLATION_ALLOSTATIC_001.json`. Total compliance to the complex Toulmin substructure was observed.
*   **D-03: The Theory Profiles** — **HEALTHY**
    *   All 10 Tier 1 Formal profiles are correctly located in `src/cmr/theory_profiles/` and operating successfully under their Agentic testing paradigm.

---

## 6. Recommendations & Next Steps

**Top 5 Remaining Risks:**
1. Hardcoded deprecated db paths in core `web_` services.
2. 272 unregistered variables slipping past the canonical variable ontology.
3. ~60 unadjudicated bridge warrant ceiling violations.
4. Test suite `test_cross_pipeline` failure.
5. Inconsistent dictionary shapes in template metadata (e.g. `provenance`).

**Explicit Go/No-Go Formulation:**  
**NO-GO** for resuming Cowork Phase 4.

**First 3 Actions needed:**
1. Run a global find-and-replace to change hardcoded `web_persistence.db` paths to safely fallback to `web_persistence_v2.db` or correctly ingest `AE_DB_PATH`.
2. Map the 272 unregistered variables to the canonical ontology to fix the 48 broken templates.
3. Fix the `test_cross_pipeline_salk_view_consistency` test.
