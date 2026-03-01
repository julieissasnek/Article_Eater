# ADR-001: CVA as Extension Layer (Strangler Fig Pattern)

**Date**: 2026-02-28
**Status**: Accepted
**Decision Makers**: Professor David Kirsh, AG (Claude Opus)

---

## Context

The ATLAS codebase manages a Quinean web of belief with 14-step integration
orchestrator, overseer monitoring (INV-0..INV-9), notification service,
annotation service, and extraction pipeline. CVA (Constraint-Valuation
Architecture) adds constraint vectors, valuation vectors, attractor dynamics,
and cultural parameterization. The question: **how should CVA integrate?**

Two approaches:
1. **Replace**: Modify existing data models and services to incorporate CVA fields
2. **Extend**: CVA lives in new files; existing code untouched except for thin hooks

## Decision

**CVA is an extension layer using the strangler fig pattern.**

- All CVA code lives in **new files**: `src/models/cva_*.py`, `src/services/cva_*.py`
- Existing files are modified **only** to add optional hooks (e.g., the orchestrator
  may call CVA annotation after Step 5 if CVA modules are available)
- CVA data structures are **optional metadata** attached to templates and beliefs
- Nothing in the existing system requires CVA to function
- If CVA modules are absent, the system degrades gracefully (no imports fail)

## Consequences

### Positive
- Zero risk to the 4,158 existing tests
- CVA can be developed, tested, and deployed independently
- Existing consumers (QA system, dashboards, nightly reports) unaffected
- Easy rollback: delete CVA files, remove hooks

### Negative
- Some duplication: CVA models may partially mirror existing belief fields
- Cross-cutting concerns (e.g., coherence computation) require bridge code
- Two code paths for belief metadata: standard + CVA-enriched

### Neutral
- CVA test files follow the same `tests/test_cva_*.py` naming convention
- ADR records accumulate in `src/adr/` as the project evolves

## Fitness Function

**Automated test**: All 4,158 existing tests pass with CVA modules imported
but no CVA data present:

```bash
# Import CVA modules in conftest.py (no-op if not populated)
pytest tests/ -v --tb=short
# Expected: 4,158+ tests pass, 0 failures
```

If this fitness function fails at any point during CVA development, **stop and
fix before proceeding**. The extension layer must never break the host system.
