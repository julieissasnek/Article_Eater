# TASKS.md

*Last updated: 2026-02-23*

Active task tracking for Article_Eater_PostQuinean_v1.
For completed sprints (Feb 2026), see `docs/TASKS_ARCHIVE_2026_Feb.md`.

---

## Current Status

**Test Suite**: 4,082 tests collect (0 collection errors)
**Templates**: 129 templates, 57 calibrated with Toulmin justifications
**Last Commit**: TJ-07, TJ-08 Toulmin justifications for SOCIAL-I and MEMORY-I

---

## Pending Tasks

### P1 (High Priority)

| ID | Task | Context | Status |
|----|------|---------|--------|
| CMR-SPEC | Define CMR Specification (template library, prediction grammar) | Blocks T7.3, T7.4, T7.6 | PENDING |
| T7.3 | Extend ae.rule.v2 schema with `theory_links` field | Needs CMR spec | BLOCKED |
| T7.4 | Update extraction prompts to capture Panel 6 theory links | Needs CMR spec | BLOCKED |

### P2 (Medium Priority)

| ID | Task | Context | Status |
|----|------|---------|--------|
| T7.6 | Implement theory agent profiles for all 8 Tier 1 frameworks | After T7.3/T7.4 | PENDING |
| RQS | ResearchQueueService implementation | Low urgency | DEFERRED |
| 3.0.1-D | Implement Extended Layer (20 API endpoints) | API expansion | PENDING |
| 3.0.1-E | Add batch operations endpoint | API expansion | PENDING |
| 3.0.1-F | Add causal endpoints | API expansion | PENDING |

### P3 (Low Priority / Future)

| ID | Task | Context | Status |
|----|------|---------|--------|
| ARCH-2 | Transportability analysis (Pearl/Bareinboim) | V3 architecture | DEFERRED |
| ARCH-3 | Independence scoring and bias correction | V3 architecture | DEFERRED |
| ARCH-5 | Split Belief into focused types | Needs test coverage | DEFERRED |

---

## Blocked Tasks

| Task | Blocked By | Resolution Path |
|------|------------|-----------------|
| T7.3, T7.4 | CMR-SPEC | Complete CMR specification |
| Sprint 8 (CMR) | FindingMechanismLink | Add to edge_types.py |
| Sprint 9 (Health Tests) | Test suite stability | Resolved (4082 tests pass) |

---

## Deferred Tasks (V3.0+)

| ID | Description | Priority |
|----|-------------|----------|
| EC-5 | Learning pathway support for education | 3.0 |
| SY-2 | Causal discovery from mechanism beliefs | 3.0 |
| SY-3 | EM-style joint optimization | 3.0 |
| SY-4 | Active learning infrastructure | 3.0 |
| SY-5 | Joint Bayesian inference | 3.0 |

---

## Decisions Pending

| Decision | Options | Impact |
|----------|---------|--------|
| D1.5.1 | task_ecology.py ClaimType naming | Affects CNFA semantics |
| D1.5.2 | Article_Finder GapType unknowns | Affects gap analysis |
| D1.5.3 | BN_graphical EvidenceType unknowns | Affects evidence classification |

---

## In Progress

| ID | Task | Started | Notes |
|----|------|---------|-------|
| (none) | | | |

---

## Recently Completed (Last 7 Days)

| ID | Task | Completed | Outcome |
|----|------|-----------|---------|
| TJ-01 to TJ-08 | Toulmin justifications (57 templates, 213 steps) | 2026-02-23 | All panels complete |
| CC_REPAIR | Template schema repair | 2026-02-22 | 129 templates validated |
| RUTHLESS | Test suite repair | 2026-02-23 | 4082 tests passing |
| SYS-DESIGN | Pre-commit hooks + template loader | 2026-02-23 | Schema validation enabled |

---

## Session Log

| Date | Session | Work Done |
|------|---------|-----------|
| 2026-02-23 | System Design | Added pre-commit hooks, template loader with validation, archived TASKS.md |
| 2026-02-23 | TJ-07, TJ-08 | Toulmin justifications for SOCIAL-I (10) and MEMORY-I (10) |
| 2026-02-22 | TJ-03 to TJ-06 | Toulmin justifications for VISUAL-I, SPATIAL-I, LIGHT-I, STRESS-I |
| 2026-02-22 | CC_REPAIR | Template schema repair sprint |

---

*For historical tasks, see `docs/TASKS_ARCHIVE_2026_Feb.md`*
