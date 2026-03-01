# Paper Integration Pipeline — Gap Audit & OVERSEER Proposal

**Date**: 2026-02-25
**Author**: Claude (Session 6)
**Status**: FOR PANEL REVIEW
**Context**: Sprint INTEGRATION-1 delivered 7 modules (orchestrator, supersession, rollback, tag engine, molecule linker, models, migrations) with 22/22 tests passing. This document audits what those modules *actually compute* vs. what the system requires for a fully functioning web and BN, and proposes a superordinate OVERSEER module.

---

## Part I: Honest Assessment — What the Pipeline Does and Doesn't Do

### What Works (Genuinely Computed)

| Component | Status | What It Actually Does |
|-----------|--------|----------------------|
| **14-step cascade** | REAL | Steps execute in sequence with critical/non-critical distinction, abort-on-failure logic, audit trail |
| **Supersession detection** | REAL | Construct overlap (Jaccard asymmetric), quality comparison (design strength, sample size, meta-analysis), partial supersession |
| **Rollback** | REAL | Paper-level undo: removes beliefs, constraints, tags, belief versions; marks supersession records as rolled back |
| **Tag assignment (3D)** | REAL | Entity/topic extraction (10 domains, keyword-based), theoretical tags (T1 keywords + known theories), effect size categorization (Cohen's d) |
| **Molecule linkage** | REAL | Construct_id match (0.95), DV/IV match (0.85/0.65), keyword fallback (0.50+); correctly propagates to molecules and T1.5 via inverted indices |
| **DB persistence** | REAL | 4 new tables with indices; belief versions track per-paper contributions; integration events provide full audit trail |
| **Idempotency** | REAL | Checks `paper_integration_events` for existing COMPLETED event before running |

### What's Skeletal (Structure Present, Computation Missing)

These are the critical gaps David identified:

#### 1. Credence Computation — NOT DONE

**Current state**: Step 4 (`_step_map_extraction`) just copies `ae_confidence` from the extraction output into `credence_mean`. It does NOT:

- Run `extraction_to_web.py`'s full `integrate_extraction()` function, which computes:
  - Theory inference (diminishing returns formula: `combined = 1 - (1 - current) * (1 - new * 0.5)`)
  - Mechanistic entrenchment boost (+0.15)
  - Multi-theory attachment (secondary threshold 0.3)
  - Null finding polarity (CONTRADICTS at 0.6 strength)
  - BN coherence cross-check (if enabled)
  - Reflective equilibrium iterations (configurable, default 5)

- Run `web_persistence.py`'s `accumulate_belief()`, which computes:
  - Inverse-variance weighted credence merging (DerSimonian-Laird meta-analytic)
  - Paper quality weighting (methodology 0.28, citations 0.18, institution 0.12, etc.)
  - Conflict detection and categorization (4 ConflictTypes)
  - Coherence dashboard metrics

**What should happen**: Step 5 should call `extraction_to_web.integrate_extraction()` directly, then pipe the resulting `WebOfBelief` into `web_persistence.accumulate_belief()`. The current direct-SQL approach bypasses all the sophisticated credence computation.

#### 2. Epistemic State (P2-P6) — NOT TRIGGERED

**Current state**: Step 13 (`_step_post_validate`) checks 3 basic invariants. It does NOT:

- Call `EpistemicOrchestrator.compute_full_state()`, which runs:
  - P2: Spohn rank computation from credences + defeat relations
  - P3: Pollock warrant status with defeat and observational beliefs
  - P2 again: Re-rank with warrant info (tiered)
  - P4: Haack grounding (experiential basis + coherence conjunction)
  - P5: Pearl graph confidence for causal bridge

This is the full formal epistemic calculus. After every paper integration, the system should recompute epistemic state for at least the affected beliefs and their neighborhood.

#### 3. BN Parameter Update — STUB

**Current state**: Step 9 (`_step_update_bn`) records edge keys in the event log but does NOT:

- Create or look up `BetaBernoulliEdge` objects
- Call `edge.update(supports=True/False, weight=quality, paper_id=pid)`
- Persist updated Beta parameters
- Invalidate the `EpistemicCausalBridge` cache

**What should happen**: For each constraint (rule), determine the BN edge it maps to, look up or create the `BetaBernoulliEdge`, call `update()` with the constraint's polarity and quality-weighted evidence strength.

#### 4. Provenance (Haack) — NOT WIRED

**Current state**: We record `BeliefVersionEntry` (which paper contributed which credence). But we do NOT:

- Create `Provenance` objects with `SourceType`, `StudyType`, `Directness`, `JustificationStatus`
- Compute grounding chains (path to experiential basis)
- Track `ExperientialClaim` objects (observation type, directness)
- Update `BeliefProvenance` in social epistemology with lab/method/community attribution

**What should happen**: Each new belief should get a `Provenance` object constructed from the extraction metadata (study design → StudyType, measurement type → ObservationType). The grounding chain should trace from the belief through the extraction to the experimental observation.

#### 5. QA Cache Recomputation — NOTIFIES BUT DOESN'T RECOMPUTE

**Current state**: Step 10 calls `QACacheManager.notify_qa_system()`, which is itself a print-statement placeholder. It does NOT:

- Actually recompute L1/L2/L3 progressive disclosure summaries
- Call the LLM re-computation pipeline for affected molecules
- Update the MD5 dependency hash

**What should happen**: Full QA cache recomputation would require LLM calls for each affected molecule (to regenerate summaries). This is expensive and should probably be deferred/batched rather than synchronous.

#### 6. Social Epistemology — PLACEHOLDER

**Current state**: Step 11 returns a placeholder note. It does NOT:

- Identify which `EpistemicCommunity` the paper's authors belong to
- Compute `CommunityRelativeCredence` for the new beliefs
- Update `ContestationTracker` if the paper contradicts existing community consensus
- Track methodological diversity (single-method vulnerability detection)

#### 7. VOI Gap Refresh — PLACEHOLDER

**Current state**: Step 12 returns a placeholder note. It does NOT:

- Check if any VOI gaps in the `DiscoveryFunnelService` are closed by the new beliefs
- Update gap status from OPEN → PARTIALLY_CLOSED → CLOSED
- Reassess search priorities based on the new evidence

#### 8. Entrenchment Recalculation — NOT DONE

After new beliefs and constraints enter the web, entrenchment scores should be recalculated using `scalable_coherence.py`'s hierarchical coherence computation. The current pipeline does not trigger this.

#### 9. Coherence Dashboard Update — NOT DONE

`web_persistence.py` has a full `CoherenceDashboard` with `is_healthy()` and `health_summary()`. The pipeline doesn't compute or log coherence before/after integration.

---

## Part II: Invocation — When Does This Pipeline Fire?

**Current state**: The orchestrator must be called explicitly. There is no hook in `pdf_extraction_module.py` or the extraction queue that automatically triggers integration when a paper is ACCEPTED.

**What's needed**: A callback or event hook in the extraction pipeline's state machine:

```
EVALUATING → ACCEPTED → [trigger PaperIntegrationOrchestrator.integrate_paper()]
```

The `pdf_extraction_module.py` has a `WorkClaimer` with state transitions (PENDING → CLASSIFYING → EXTRACTING → EVALUATING → ACCEPTED/REQUEUED/FAILED). The ACCEPTED transition is where integration should fire.

**Decision needed**: Should this be synchronous (blocks until all 14 steps complete) or asynchronous (fires integration as a background task)? The QA recomputation step involves LLM calls and could take minutes per molecule.

---

## Part III: The Case for an OVERSEER Module

David's intuition is right. The Paper Integration Pipeline handles the *event-driven* case: a specific paper enters the system. But there is no module responsible for the *steady-state* questions:

1. **Is the system internally consistent?** Do all beliefs have proper provenance? Do BN edge parameters match web constraints? Are all molecule caches fresh?

2. **Is the system complete?** Are there beliefs without theory attachments? Templates without any supporting evidence? Molecules with empty constituent templates?

3. **Is the system healthy?** Is coherence trending down? Are conflicts accumulating faster than resolution? Are there communities with single-method vulnerability?

4. **Is the system current?** Are there papers in the queue that should have been integrated? Stale caches? Superseded beliefs that haven't been retired?

5. **Is the system recoverable?** Can we reconstruct any belief's full history? Can we roll back to any prior state? Are snapshots being taken regularly?

These questions cannot be answered by the integration pipeline because they require a *system-wide* perspective, not a per-paper perspective. This is the OVERSEER's domain.

### Proposed OVERSEER Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        OVERSEER MODULE                          │
│                                                                 │
│  Responsibilities:                                              │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────────┐ │
│  │ HEALTH      │  │ INTEGRITY    │  │ COMPLETENESS           │ │
│  │ MONITOR     │  │ CHECKER      │  │ AUDITOR                │ │
│  │             │  │              │  │                        │ │
│  │ - Coherence │  │ - Belief     │  │ - Template coverage    │ │
│  │   trends    │  │   provenance │  │ - Theory attachment    │ │
│  │ - Conflict  │  │ - BN-web     │  │ - Molecule staleness   │ │
│  │   rates     │  │   sync       │  │ - Evidence gaps        │ │
│  │ - Cache     │  │ - Contract   │  │ - Provenance chains    │ │
│  │   freshness │  │   compliance │  │ - T-level coverage     │ │
│  │ - Queue     │  │ - Invariant  │  │                        │ │
│  │   health    │  │   INV-1..5   │  │                        │ │
│  └─────────────┘  └──────────────┘  └────────────────────────┘ │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────────┐│
│  │ MAINTENANCE  │  │ SCHEDULER    │  │ REPORTING              ││
│  │ ENGINE       │  │              │  │                        ││
│  │              │  │ - Periodic   │  │ - Health dashboard     ││
│  │ - Stale      │  │   health     │  │ - Integrity report     ││
│  │   cache      │  │   checks     │  │ - Completeness gaps    ││
│  │   refresh    │  │ - Triggered  │  │ - Maintenance log      ││
│  │ - Orphan     │  │   repairs    │  │ - Trend analysis       ││
│  │   cleanup    │  │ - Batch      │  │ - Alert escalation     ││
│  │ - Snapshot   │  │   recompute  │  │                        ││
│  │   rotation   │  │   windows    │  │                        ││
│  └──────────────┘  └──────────────┘  └────────────────────────┘│
│                                                                 │
│  Modes:                                                         │
│  - ON_DEMAND: David runs overseer.audit()                       │
│  - POST_INTEGRATION: Fires after each paper integration         │
│  - PERIODIC: Nightly/weekly full system health check            │
│  - ALERT: Triggered by threshold violations                     │
└─────────────────────────────────────────────────────────────────┘
```

### OVERSEER Sub-Components

**1. Health Monitor**
- Tracks coherence trend (per-theory and global) across integrations
- Conflict accumulation rate (should stay below 10% of beliefs)
- Cache freshness (% of molecules with FRESH vs STALE status)
- Queue health (papers stuck in EXTRACTING for >24h, REQUEUED count)
- BN convergence (are Beta posteriors stabilizing or oscillating?)

**2. Integrity Checker**
- Every belief has: paper_id, provenance, at least one constraint, a theory attachment
- BN edges match web constraints (no orphan edges, no missing edges)
- All beliefs conform to ae.claim.v2 contract
- INV-1 through INV-5 hold globally (not just for the most recent paper)
- Supersession records are consistent (no circular supersession)
- Tag assignments cover all three dimensions for all beliefs

**3. Completeness Auditor**
- Template coverage: which templates have zero supporting beliefs?
- Theory attachment: which beliefs have no T1, T1.5, or molecule connection?
- Evidence gaps: which constructs have only one supporting paper?
- Provenance chains: which beliefs lack grounding (COHERENT_ONLY status)?
- T-level coverage: which T1.5 theories have constituent templates with no evidence?

**4. Maintenance Engine**
- Stale cache refresh: batch-recompute QA caches for molecules marked STALE
- Orphan cleanup: find beliefs/constraints with no integration event
- Snapshot rotation: keep N most recent snapshots, archive older ones
- Entrenchment recalculation: periodic full-web entrenchment recompute
- Coherence recalculation: periodic hierarchical coherence update

**5. Scheduler**
- POST_INTEGRATION: lightweight health check after each paper (seconds)
- PERIODIC: full integrity + completeness audit (minutes, batched)
- ALERT: immediate when thresholds violated (coherence drop >5%, conflict spike)

**6. Reporting**
- Generates `SYSTEM_HEALTH_REPORT_[date].md` in docs/
- Dashboard metrics for Streamlit display
- Alert escalation (email/log when critical thresholds breached)

### Panel Questions for OVERSEER Design

These require domain expertise to resolve:

| Q# | Question | Domain | Options |
|----|----------|--------|---------|
| O-1 | Should the OVERSEER recompute full epistemic state (P2-P6) after every paper, or only periodically? | Performance/Epistemology | Per-paper (correct but expensive) vs. batched (fast but stale) vs. incremental (only affected neighborhood) |
| O-2 | What coherence decline threshold triggers an alert? | Epistemology | 5%? 10%? Per-theory vs. global? Per Cartwright's dashboard metrics? |
| O-3 | Should the OVERSEER have authority to auto-retire beliefs that violate INV-1..5, or only flag them? | Governance | Auto-repair (dangerous) vs. flag-only (safe) vs. quarantine (middle ground) |
| O-4 | How should BN parameter updates interact with entrenchment? Should they be coupled or independent? | Architecture | Coupled (BN informs entrenchment) vs. independent (parallel tracks) vs. Pearl's do-calculus bridge |
| O-5 | Should provenance computation be synchronous (during integration) or deferred (OVERSEER maintenance)? | Performance | Synchronous (correct) vs. deferred (fast) vs. hybrid (basic sync, full deferred) |
| O-6 | What's the right QA cache recomputation strategy? | Performance | Eager (recompute immediately, expensive LLM calls) vs. lazy (mark stale, recompute on query) vs. batched (nightly) |
| O-7 | Should the OVERSEER maintain its own database or use the existing web_persistence.py SQLite? | Architecture | Separate DB (clean separation) vs. shared DB (simpler) vs. new tables in existing DB |
| O-8 | How does the OVERSEER interact with parallel Claude sessions? Should it claim a work lane? | Coordination | PARALLEL_WORK.md protocol vs. file locks vs. single-writer constraint |

---

## Part IV: Immediate Action Items (No Panel Needed)

These are straightforward engineering tasks that don't require epistemological judgment:

### A. Wire Integration Pipeline to Existing Services

Replace the current direct-SQL approach in Steps 4-5 with calls to `extraction_to_web.integrate_extraction()` + `web_persistence.accumulate_belief()`. This immediately gains:
- Full credence computation (inverse-variance weighting, paper quality, theory inference)
- Conflict detection and categorization
- Reflective equilibrium
- Coherence tracking

### B. Wire BN Update (Step 9)

Replace the stub with actual `BetaBernoulliEdge.update()` calls using constraint polarity + quality weight. This requires mapping each constraint to its BN edge (source → target).

### C. Add Post-Integration Epistemic State Recomputation

After Step 5, call `EpistemicOrchestrator.invalidate_cache()` and optionally `compute_full_state()` for the affected belief neighborhood.

### D. Add Extraction Pipeline Hook

Add a callback in `pdf_extraction_module.py`'s state machine so that ACCEPTED → triggers `PaperIntegrationOrchestrator.integrate_paper()`.

### E. Wire Coherence Dashboard

Call `web_persistence.py`'s coherence computation before and after integration; log the delta in the integration event.

---

## Part V: Summary of Recommendations

1. **Immediate**: Wire Steps 4-5 to use `extraction_to_web.py` + `web_persistence.py` (no panel needed, pure engineering)
2. **Immediate**: Wire Step 9 to actual BN updates (no panel needed)
3. **Immediate**: Add extraction pipeline hook for automatic triggering
4. **Panel Required**: OVERSEER design decisions (O-1 through O-8)
5. **Panel Required**: Provenance depth (how much Haack computation per integration?)
6. **Panel Required**: QA recomputation strategy (eager vs. lazy vs. batched)
7. **Post-Panel**: Implement OVERSEER module with panel-approved architecture
