# OVERSEER Design — Executive Summary

**Date**: 2026-02-25
**Document**: Full deliberation in `docs/PANEL_OVERSEER_DESIGN_2026-02-25.md` (1,485 lines)
**Status**: Panel consensus achieved; awaiting David's approval for Phase 1 implementation

---

## The Problem

The Article Eater integration pipeline (14-step cascade) is architecturally sound but has **critical gaps**:

1. **Credence computation** (Step 4-5): Stubs—doesn't call `extraction_to_web.integrate_extraction()` or `web_persistence.accumulate_belief()`
2. **Provenance** (Step 5): No Haack foundherentist justification objects created
3. **BN updates** (Step 9): No actual `BetaBernoulliEdge.update()` calls
4. **Coherence monitoring** (Steps 2, 13): Pre/post measurement not implemented
5. **Social epistemology** (Step 11): Community identification placeholder
6. **VOI gaps** (Step 12): Gap closure assessment not triggered
7. **System health**: No module monitors coherence trends, conflict rates, cache freshness

**Result**: Papers integrate, but the system doesn't truly accumulate evidence or check its own health.

---

## The Solution: OVERSEER Module

A superordinate system health service with six responsibilities:

```
OVERSEER
├─ Health Monitor (coherence trends, conflict rates, cache freshness)
├─ Integrity Checker (every belief has provenance, BN-web sync, INV-1..5)
├─ Completeness Auditor (template coverage, theory attachment, evidence gaps)
├─ Maintenance Engine (stale cache refresh, orphan cleanup, snapshots)
├─ Scheduler (post-integration / nightly / alert / on-demand modes)
└─ Reporting (health dashboard, alert escalation)
```

Operates in 4 modes:
- **POST_INTEGRATION** (5-10 sec per paper): Quick health check
- **PERIODIC** (nightly, 5-15 min): Full system audit + batch maintenance
- **ALERT** (< 1 sec detection): Triggered by threshold violations (e.g., coherence drop > 5%)
- **ON_DEMAND** (interactive): David runs `overseer.audit(scope='...')`

---

## Critical Design Decisions (O-1 through O-8)

All answered by expert panel with consensus or documented dissent:

| O# | Question | Answer | Rationale |
|----|----------|--------|-----------|
| **O-1** | Recompute P2-P6 per-paper or nightly? | Per-paper *neighborhood* (Spohn scoping) | Correct + tractable |
| **O-2** | Coherence alert threshold? | Statistical baseline (mean ± 1σ) per-theory | Context-sensitive |
| **O-3** | Auto-retire violations or flag-only? | Quarantine (review required before retire) | Safety + transparency |
| **O-4** | BN coupling—coupled or independent? | Hierarchical one-directional (web → BN) | Separates epistemology/causality |
| **O-5** | Provenance computation—sync or deferred? | Synchronous (Step 5) | Foundational to Haack epistemology |
| **O-6** | QA cache recomputation strategy? | Batched nightly (Option C) | Balance cost/freshness/performance |
| **O-7** | OVERSEER database—separate or shared? | Separate `overseer.db` | Clean separation (Parnas) |
| **O-8** | Parallel sessions coordination? | PARALLEL_WORK.md exclusive lanes | Explicit coordination |

---

## Phase 1: Critical Engineering (Week 1-2)

**Must complete before scaling extraction**:

1. Wire Steps 4-5 to actual credence computation (2-3 days)
2. Implement Provenance objects in Step 5 (2-3 days)
3. Wire Step 9 to BN updates (2-3 days)
4. Add coherence pre/post measurement (1 day)

**Owner**: Engineering team

---

## Phase 2: OVERSEER Foundation (Weeks 2-3)

1. Implement Health Monitor + Integrity Checker
2. Set up overseer.db schema
3. POST_INTEGRATION health check (non-blocking)

**Owner**: Engineering team

---

## Phase 3: Full OVERSEER (Weeks 3-4)

1. Completeness Auditor + Maintenance Engine
2. Nightly scheduler + reporting
3. Streamlit dashboard

**Owner**: Engineering + Frontend

---

## Phase 4: Expert Calibration (Week 4)

Panel-driven parameterization:
- Coherence thresholds (per-theory)
- Community identification in CNFA
- VOI priorities
- High-priority research gaps

**Owner**: David + panel experts

---

## Key Panel Findings (Ruthless Review)

### Web of Belief: Credence Computation
- **Current**: Direct assignment of `ae_confidence` (0.1 - 0.9)
- **Should be**: Full Quinean integration with theory inference, entrenchment boost, reflective equilibrium, DerSimonian-Laird meta-analytic accumulation
- **Issue**: Coherence is illusory if credences aren't properly computed
- **Panel consensus**: Wire immediately

### Provenance & Justification
- **Current**: `BeliefVersionEntry` tracks which paper contributed
- **Should be**: Full `Provenance` objects with `StudyType`, `Directness`, `JustificationStatus`, grounding chains
- **Issue**: Without provenance, system is purely coherentist (violates Haack foundherentism)
- **Panel consensus**: Synchronous computation in Step 5

### Bayesian Network Parameterization
- **Current**: Step 9 is a stub; edges not updated
- **Should be**: `BetaBernoulliEdge.update()` with constraint polarity + quality weight
- **Coupling**: Web credences → BN priors (one-directional, not bidirectional)
- **Panel consensus**: Hierarchical coupling; web is epistemologically primary

### Coherence Monitoring
- **Current**: Computed but not logged or alerted
- **Should be**: Per-theory tracking with statistical baseline alerts
- **Threshold**: Alert if coherence_delta < (historical_mean - 1σ)
- **Panel consensus**: Cartwright's multi-metric dashboard (global + per-theory + conflict rate + cache freshness)

### Social Epistemology
- **Current**: Step 11 placeholder; no community identification
- **Should be**: Explicit community tracking, consensus measurement, methodological monoculture detection
- **Why**: Single-method evidence is vulnerable; cross-community agreement is robust
- **Panel consensus**: Surface contestation explicitly; don't hide disagreements in averaging

### Value of Information
- **Current**: Step 12 placeholder; heuristic `min(0.8, n_beliefs * 0.15 + n_constraints * 0.05)`
- **Should be**: Compute actual VOI for each question; integrate into extraction priorities
- **Why**: Resource allocation should follow value (which questions, if answered, would most change decisions?)
- **Panel consensus**: Expert panel to define high-VOI questions in CNFA

---

## Panel Voices (Constructed but Evidence-Based)

**Epistemology**: Quine (coherentism), Haack (foundherentism), Spohn (ranking theory), Pollock (defeasible reasoning)

**Causality**: Pearl (DAGs, do-calculus), Cartwright (evidence pluralism)

**Statistics**: Good (Bayesian foundations), DerSimonian (meta-analysis), Borenstein (heterogeneity)

**Systems**: Simon (bounded rationality, organizations), Ashby (cybernetics, requisite variety)

**Architecture**: Parnas (information hiding), Dijkstra (correctness), Liskov (software design), Lamport (formal specification)

---

## Open Questions for David

1. **Which CNFA epistemic communities should be recognized?** (Lab clusters? Methodological traditions? Theoretical schools?)
2. **What's high-priority VOI in CNFA?** (Which questions, if answered, would most improve building design decisions?)
3. **Is 24-hour cache freshness acceptable?** (Or target < 12h?)
4. **What constitutes 'healthy' coherence?** (Threshold C_min for global coherence?)
5. **Should per-theory coherence have different thresholds?** (Is 0.6 okay for EC but not SRT?)
6. **Parallelization strategy**: As system grows (850 → 5000+ papers), will per-paper neighborhood recomputation still work?

---

## Next Steps

1. **David reviews** `docs/PANEL_OVERSEER_DESIGN_2026-02-25.md`
2. **David approves** implementation roadmap (Phases 1-4)
3. **Engineering executes** Phase 1 (wire critical stubs)
4. **David + panel** calibration session (Phase 4) once Phase 1 complete

---

## Files Produced

- **Full panel document**: `docs/PANEL_OVERSEER_DESIGN_2026-02-25.md` (1,485 lines)
  - Part I: Ruthless review (web, provenance, BN, cache, coherence, social epistemology, VOI, entrenchment)
  - Part II: OVERSEER design (architecture, sub-components, operational modes, 8 design questions answered)
  - Part III: Concrete implementation (Python code sketches, Phase 1-4 roadmap)
  - Part IV: Panel dissent (documented disagreements on 3 questions with consensus resolutions)

- **This document**: Executive summary for quick reference

---

**Ready for**: David's review and approval
**Timeline**: Phase 1 (2 weeks) → Phase 2-3 (4 weeks) → Phase 4 (1-2 weeks) → Full operational OVERSEER by mid-March 2026
