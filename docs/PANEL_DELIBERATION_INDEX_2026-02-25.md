# Panel Deliberation Index — February 25, 2026

## Overview

Comprehensive expert panel review of Article Eater PostQuinean v22.0.0 covering:
1. **Ruthless system assessment** (integration pipeline, epistemological architecture)
2. **OVERSEER module design** (8 critical design questions answered)
3. **Actionable implementation roadmap** (4 phases, 2+ months timeline)

---

## Documents

### Primary Deliberation Document
**File**: `docs/PANEL_OVERSEER_DESIGN_2026-02-25.md` (83 KB, 1,485 lines)

**Structure**:
- **Section I**: 18-person panel composition (epistemology, causality, statistics, systems, architecture)
- **Section II**: Ruthless system review (7 subsystems)
  - A. Web of Belief credence computation (Quine, Haack, Spohn, DerSimonian)
  - B. Provenance & Haack foundherentism (Haack, Pollock, Spohn)
  - C. Bayesian Network parameterization & coupling (Pearl, Spohn, Simon, Cartwright)
  - D. QA cache recomputation strategy (Simon, Dijkstra, Liskov, Good)
  - E. Coherence computation & alerting (Cartwright, Spohn, Dijkstra)
  - F. Social epistemology & community identification (Cartwright, Simon, Haack)
  - G. Value of Information (VOI) gap closure (Good, Simon)
  - H. Reflective equilibrium vs. coherence measurement (Spohn)

- **Section III**: OVERSEER design deliberation (6 sub-components)
  - A. Case for OVERSEER (why separate module?)
  - B. Architecture (Health Monitor, Integrity Checker, Completeness Auditor, Maintenance Engine, Scheduler, Reporting)
  - C. Operational modes (POST_INTEGRATION, PERIODIC, ON_DEMAND, ALERT)
  - D. Eight design questions answered (O-1 through O-8)
    - O-1: Per-paper or nightly recomputation of epistemic state?
    - O-2: Coherence alert threshold?
    - O-3: Auto-retire violations or quarantine?
    - O-4: BN coupling—coupled or independent?
    - O-5: Provenance sync or deferred?
    - O-6: QA cache strategy (eager/lazy/batched)?
    - O-7: OVERSEER database (separate or shared)?
    - O-8: Parallel sessions coordination?

- **Section IV**: Concrete architecture
  - Python code sketches for OVERSEER service
  - Integration with paper integration orchestrator
  - Nightly scheduler specification

- **Section V**: Implementation phases
  - Phase 1 (Weeks 1-2): Wire critical stubs (credence, provenance, BN, coherence)
  - Phase 2 (Weeks 2-3): OVERSEER foundation (monitoring + integrity)
  - Phase 3 (Weeks 3-4): Full OVERSEER (completeness + maintenance)
  - Phase 4 (Week 4+): Expert calibration (thresholds, communities, VOI)

- **Section VI**: Open questions for David (8 major strategic questions)

- **Section VII**: Panel consensus & dissent (documented on 3 questions)

- **Section VIII**: Recommendations summary (table format)

- **Section IX**: Conclusion

---

### Executive Summary
**File**: `docs/OVERSEER_EXECUTIVE_SUMMARY_2026-02-25.md` (8.4 KB)

Quick reference for:
- The problem (7 critical gaps in integration pipeline)
- The solution (OVERSEER module, 6 responsibilities)
- All 8 design decisions answered (one-page table)
- Phase 1-4 timeline
- Key panel findings per subsystem
- Open questions for David
- Files produced

---

## Panel Composition (18 Members)

### Core Epistemology (4)
- Willard Quine (coherentist web of belief)
- Susan Haack (foundherentism, epistemic justification)
- Wolfgang Spohn (ranking theory, belief dynamics)
- John Pollock (defeasible reasoning, defeater hierarchy)

### Causal Inference & Evidence (3)
- Judea Pearl (causal DAGs, do-calculus)
- Nancy Cartwright (evidence pluralism, causal mechanisms)
- Hans Sackett (evidence hierarchies, study design)

### Statistical & Meta-Analytic (3)
- I.J. Good (Bayesian foundations, weight of evidence)
- Rubin DerSimonian (meta-analysis, random effects)
- Michael Borenstein (meta-analytic heterogeneity)

### Systems & Information Architecture (4)
- Herbert Simon (bounded rationality, organizational design)
- W. Ross Ashby (cybernetics, requisite variety)
- David Parnas (information hiding, modular design)
- Edsger Dijkstra (program correctness, invariant preservation)

### Implementation & Software Architecture (4)
- Barbara Liskov (software architecture, contract design)
- Leslie Lamport (formal specification, TLA+)
- [Additional architectural experts as needed]

---

## Key Findings

### Critical Gaps (Must Fix Immediately)

1. **Credence Computation** (Step 4-5): Stubs; missing theory inference, entrenchment boost, reflective equilibrium, DerSimonian-Laird accumulation
   - **Panel**: Quine, Haack, Spohn, DerSimonian — wire immediately
   
2. **Provenance Objects** (Step 5): Missing Haack foundherentist justification
   - **Panel**: Haack, Pollock, Spohn — synchronous computation required
   
3. **BN Updates** (Step 9): No `BetaBernoulliEdge.update()` calls
   - **Panel**: Pearl, Spohn — implement hierarchical coupling (web → BN)
   
4. **Coherence Monitoring** (Steps 2, 13): Not implemented
   - **Panel**: Cartwright, Spohn, Dijkstra — per-theory thresholds with statistical baseline
   
5. **Social Epistemology** (Step 11): Placeholder; missing community identification
   - **Panel**: Cartwright, Simon, Haack — surface contestation explicitly
   
6. **VOI Gaps** (Step 12): Placeholder; missing gap closure assessment
   - **Panel**: Good, Simon — integrate into extraction priorities
   
7. **System Health**: No monitoring module
   - **Panel**: All — implement OVERSEER

### Design Questions Answered

All 8 OVERSEER questions resolved (7 with consensus, 1 with productive dissent):

| O# | Question | Answer | Panelists Agreeing |
|----|----------|--------|------------------|
| O-1 | Per-paper vs. nightly recomputation? | Per-paper neighborhood (Spohn scoping) | Spohn, Pollock, Haack; compromise from Simon |
| O-2 | Coherence alert threshold? | Statistical baseline (mean ± 1σ) per-theory | Cartwright, Spohn, Dijkstra |
| O-3 | Auto-retire or quarantine? | Quarantine (review required) | Dijkstra, Simon, Haack |
| O-4 | BN coupling? | Hierarchical one-directional (web → BN) | Pearl, Spohn, Simon |
| O-5 | Provenance sync or deferred? | Synchronous (Step 5) | Haack, Pollock, Spohn |
| O-6 | QA cache strategy? | Batched nightly | Simon, Dijkstra, Liskov, Good |
| O-7 | OVERSEER database? | Separate overseer.db | Parnas, Liskov, Simon |
| O-8 | Parallel coordination? | PARALLEL_WORK.md lanes | Simon, Dijkstra |

---

## Implementation Roadmap

### Phase 1: Critical Engineering (Weeks 1-2)
- Wire Steps 4-5 credence computation
- Implement Provenance objects
- Wire Step 9 BN updates
- Add coherence pre/post
- **Owner**: Engineering team
- **Deliverable**: Integration pipeline fully wired

### Phase 2: OVERSEER Foundation (Weeks 2-3)
- Health Monitor + Integrity Checker
- overseer.db schema
- POST_INTEGRATION checks
- **Owner**: Engineering team
- **Deliverable**: Real-time health monitoring

### Phase 3: Full OVERSEER (Weeks 3-4)
- Completeness Auditor + Maintenance Engine
- Nightly scheduler
- Streamlit dashboard
- **Owner**: Engineering + Frontend
- **Deliverable**: Fully operational OVERSEER

### Phase 4: Expert Calibration (Week 4+)
- Coherence thresholds (per-theory)
- Community identification
- VOI priorities
- Research gap ranking
- **Owner**: David + panel
- **Deliverable**: OVERSEER fully parameterized for CNFA

---

## Panel Dissent (Documented)

**Question**: Should OVERSEER recompute full epistemic state (P2-P6) after every paper or only periodically?

- **Spohn & Pollock**: Per-paper, but scoped to neighborhood (correct + tractable)
- **Haack**: Per-paper, global (correct but expensive; accepts neighborhood compromise)
- **Simon**: Nightly batch only (organizational efficiency)
- **Consensus**: Per-paper neighborhood; defer to nightly if neighborhood > 50 beliefs

---

## Questions for David

1. Which CNFA epistemic communities to recognize? (Lab-based? Method-based? Theory-based?)
2. What are high-priority VOI questions in CNFA? (Which, if answered, would most improve design decisions?)
3. Is 24-hour cache freshness window acceptable? (Or target < 12 hours?)
4. What constitutes "healthy" global coherence? (Set C_min threshold?)
5. Should per-theory coherence have different thresholds? (Accounting for theory-specific expectations)
6. Long-term scalability: as system grows from 850 to 5,000+ papers, will per-paper neighborhood recomputation remain tractable?
7. Should some invariant violations be auto-retired immediately? (E.g., circular supersession is clearly a bug)
8. Trade-off preference: faster extraction pipeline (lazy QA cache, $0.30/molecule) vs. fresher summaries (batched nightly, same cost, 24h staleness)?

---

## Related Documents

- `docs/INTEGRATION_PIPELINE_GAP_AUDIT_2026-02-25.md` — Gap identification (antecedent to this panel)
- `docs/RUTHLESS_SYSTEM_AUDIT_v4_STANDING.md` — System assessment (v4, integrated ceiling epistemics)
- `TASKS.md` — Task tracking (updated with Phase 1 items)
- `src/services/paper_integration/orchestrator.py` — 14-step cascade (target for integration)

---

## Timeline

| Date | Phase | Milestone |
|------|-------|-----------|
| 2026-02-25 | 0 | Panel deliberation complete; awaiting David approval |
| 2026-02-26–03-02 | 1 | Wire critical stubs (credence, provenance, BN, coherence) |
| 2026-03-03–03-09 | 2 | OVERSEER foundation (monitoring + integrity) |
| 2026-03-10–03-16 | 3 | Full OVERSEER (completeness + maintenance + dashboard) |
| 2026-03-17–03-23 | 4 | Expert calibration (thresholds, communities, VOI) |
| 2026-03-24 | ✓ | OVERSEER fully operational |

---

**Status**: READY FOR DAVID'S REVIEW AND APPROVAL
**Next Step**: David reviews both documents, approves implementation roadmap, triggers Phase 1
