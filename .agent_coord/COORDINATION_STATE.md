# Agent Coordination State
# =========================
# SINGLE SOURCE OF TRUTH for system state.
# Both AG (Antigravity) and Claude MUST read this at session start.
# Both MUST update it at session end.
# Last updated: 2026-03-02T20:45:00-08:00

## System Metrics

| Metric | Value | Last Verified |
|--------|-------|--------------|
| Test Count | 5,789 passing, 0 failed | 2026-03-02 AG |
| T1 Frameworks | 10 | 2026-03-02 AG |
| T1.5 Domain Theories | 13 | 2026-03-02 AG |
| T2 Templates | ~166 (~103 calibrated) | 2026-03-01 |
| Molecules | 18 | 2026-03-01 |
| T3 Beliefs | Dynamic (grows with EN/BN) | — |
| AESHI Score | 86.11 GREEN | 2026-03-01 |
| API Routes | 203 | 2026-03-02 Claude |
| Enrichment Services | 8 wired into orchestrator | 2026-03-02 Claude |

## Canonical Sources of Truth

| What | Authoritative File | DO NOT HARDCODE |
|------|-------------------|-----------------|
| T1 Frameworks | `schemas/theory/tier1_frameworks.json` | 10 (always load from JSON) |
| T1.5 Domain Theories | `schemas/theory/tier1_5_domain_theories.json` | 13 (always load from JSON) |
| T2 Templates | `schemas/theory/tier2_mechanisms.json` | ~166 |
| Molecules | `schemas/theory/molecule_taxonomy.json` | 18 |
| Propagation Procedure | `docs/TIER_TAXONOMY_PROPAGATION_PROCEDURE.md` | When counts change |
| Epistemic Norms | `docs/EPISTEMIC_PRINCIPLES.md` | 17 norms |
| QA Handler | `src/services/arbitrary_qa_handler.py` | Dynamic loading |
| Enrichment Orchestrator | `src/services/answer_enrichment_orchestrator.py` | 8 services |

## Active Work / File Locks

| Agent | Currently Working On | Files Locked | Since |
|-------|---------------------|--------------|-------|
| AG | Service architecture + coordination system | `.agent_coord/*`, `.agents/workflows/*` | 2026-03-02 20:45 |
| Claude | (idle) | — | — |

## Last Session Summary

### AG (Antigravity) — 2026-03-02
- Expanded T1.5 from 4 → 13 in canonical schema
- Updated QA handler to dynamically load T1.5 from JSON
- Updated TIER_ARCHITECTURE_SPEC with full 13-theory table
- Created `TIER_TAXONOMY_PROPAGATION_PROCEDURE.md`
- Created `test_tier_taxonomy_consistency.py` (13 tests, all pass)
- Fixed T1 naming: abbreviations → full names in tag_engine, QA handler

### Claude — 2026-03-02
- Built answer enrichment orchestrator (794 lines)
- Created language_adaptation_service.py (~400 lines)
- Created figure_suggestion_service.py (~300 lines)
- Created math_explanation_service.py (~400 lines)
- Created app/routes/services.py (636 lines, 11 API endpoints)
- Wired orchestrator into QA handler via `_apply_enrichment()`
- 192 new tests across 4 test files

## Known Issues / Ambiguities

| Issue | Status | Owner |
|-------|--------|-------|
| Master doc T1.5 counts (4/10/12/13 in different sections) | Passed to Claude for fix | Claude |
| Molecule count may need updating (13 T1.5 are also molecules) | Open | Either |
| `TASKS.md` is stale (says 4,082 tests) | Being fixed by AG now | AG |
