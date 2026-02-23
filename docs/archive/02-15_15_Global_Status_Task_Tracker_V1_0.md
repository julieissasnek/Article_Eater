# GLOBAL STATUS & TASK TRACKER
## Article Eater — February 15, 2026 — Document 15
## Maintained by Opus. Updated after each agent report.

---

# SPRINT 0: FOUNDATION — STATUS

| Task | Agent | Status | Notes |
|---|---|---|---|
| 0.0 Fix test suite | Antigravity | ✅ DONE | 2578 passing, 1 failure (theory registry seed — expected until Sprint 7) |
| 0.1 Create directory structure | CC | ⏳ ALMOST DONE | `src/queue/`, `src/theory/`, `src/cmr/` with `__init__.py` |
| 0.2 GapType reconciliation | CC | ⏳ ALMOST DONE | Canonical 8-value enum → `src/epistemic/gap_types.py` |
| 0.3 Update framework bootstrap to 10 | CC | ⏳ ALMOST DONE | Add CB, MSI to `theory_bootstrap.py` |
| 0.4 Update stale docs | Antigravity | ✅ DONE | CLAUDE.md + IMPLEMENTATION_TASKS.md verified correct |
| 0.5 Template ID alias map | Antigravity | ✅ DONE | `docs/template_id_aliases.json` — 40 templates. **Needs update for T41–T47.** |
| 0.6 Cross-repo vocab contract | Codex | ✅ DONE | `canonical_enums.json` + `check_enum_drift.py` |
| 0.7 Migration adapter scripts | Codex | ✅ DONE | 5 scripts, dry-run verified, lossless tests pass |

**Sprint 0 gate**: CC finishes 0.1–0.3, then CC reviews Codex's migration patches. After merge, Sprint 1 begins.

---

# THEORY WORK COMPLETED THIS SESSION (Opus)

| Doc | Content | Impact on Codebase |
|---|---|---|
| Doc 14: Panel IV | CC/EF NOT promoted to Tier 1. 7 new templates: T41 (RPE), T42 (Wanting/Liking), T43 (MB/MF Arbitration), T44 (Hierarchical Control), T45 (Proactive/Reactive), T46 (Thalamic Filter), T47 (Gamma/Beta WM) | Template library grows from 40 → 47. Five new `structural_pattern` enum values needed. No change to independence matrix dimensions. |

---

# FULL TASK BACKLOG BY SPRINT

## Sprint 1: Epistemic Core Extensions

| Task | Agent | Status | Dependency |
|---|---|---|---|
| 1.1 Claim node extensions (argument_scheme, critical_questions) | CC | NOT STARTED | Sprint 0 complete |
| 1.2 Edge type consolidation (ConstraintType + EdgeType → one enum) | CC | NOT STARTED | Sprint 0 complete |
| 1.3 Node type consolidation (NodeDomain + NodeTypeFamily → one) | CC | NOT STARTED | Sprint 0 complete |
| 1.4 Cross-repo contract compliance after enum changes | Codex | NOT STARTED | CC finishes 1.2–1.3 |

## Sprint 2: Bayesian Network Extensions

| Task | Agent | Status | Dependency |
|---|---|---|---|
| 2.1 BN: add d-separation, conditional queries | CC | NOT STARTED | Sprint 1 |
| 2.2 Schema migration: new fields to SQLAlchemy models | CC | NOT STARTED | Sprint 1 |

## Sprint 3: Coherence & Bridge

| Task | Agent | Status | Dependency |
|---|---|---|---|
| 3.1 Coherence engine upgrade (scalable_coherence.py) | CC | NOT STARTED | Sprint 2 |
| 3.2 Bridge warrant service extensions | CC | NOT STARTED | Sprint 2 |
| 3.3 Run check_enum_drift.py, report drift | Codex | NOT STARTED | Periodic |

## Sprint 4/4b: Extraction Pipeline

| Task | Agent | Status | Dependency |
|---|---|---|---|
| 4.1 Extraction pipeline extensions | CC | NOT STARTED | Sprint 3 |
| 4.2 Source quality scoring refinement | CC | NOT STARTED | Sprint 3 |
| 4b.1 Method registry implementation | CC | NOT STARTED | Sprint 4 |
| 4b.2 Ecological validity scoring | CC | NOT STARTED | 4b.1 |
| 4b.3 Extract method metadata from 7 finding files | Antigravity | NOT STARTED | Sprint 4 |
| 4b.4 Validate extraction output against canonical schemas | Codex | NOT STARTED | Sprint 4b |

## Sprint 5: Integration

| Task | Agent | Status | Dependency |
|---|---|---|---|
| 5.1 Wire extraction → web of belief → BN pipeline | CC | NOT STARTED | Sprint 4b |
| 5.2 End-to-end pipeline test | CC | NOT STARTED | 5.1 |
| 5.3 Cross-repo contract compliance for full pipeline | Codex | NOT STARTED | 5.2 |

## Sprint 6: Research Queue

| Task | Agent | Status | Dependency |
|---|---|---|---|
| 6.1 ResearchTarget model | CC | NOT STARTED | Sprint 5 |
| 6.2 ResearchQueueService implementation | CC | NOT STARTED | 6.1 |
| 6.3 VOI scoring integration | CC | NOT STARTED | 6.2 |
| 6.4 Queue prioritization panel weights | Antigravity | NOT STARTED | Sprint 6 |

## Sprint 7: Theory Tier ← CRITICAL

| Task | Agent | Status | Dependency |
|---|---|---|---|
| 7.1 Tier1Framework model in DB | CC | NOT STARTED | Sprint 6 |
| 7.2 Independence matrix in DB | CC | NOT STARTED | 7.1 |
| 7.3 MechanisticTemplate + CausalLink models in DB | CC | NOT STARTED | 7.1 |
| 7.4 Encode 12 seed templates | CC | NOT STARTED | 7.3 |
| 7.4b **NEW**: Encode 7 Panel IV templates (T41–T47) | CC | NOT STARTED | 7.3 |
| 7.5 Encode remaining 28 templates (mechanical) | Antigravity | NOT STARTED | 7.4 (needs seed pattern) |
| 7.6 Template ID alias map integration | Antigravity | PARTIAL | alias map exists; needs T41–T47 update |
| 7.7 Cross-framework bridging rules in DB | CC | NOT STARTED | 7.4 |
| 7.7b **NEW**: Register 5 new structural_pattern enum values | CC | NOT STARTED | 7.3 |
| 7.8 Validate all templates load and cross-reference | Codex | NOT STARTED | 7.5 complete |

## Sprint 8: CMR Pipeline ← CRITICAL

| Task | Agent | Status | Dependency |
|---|---|---|---|
| 8.1 CMR data models | CC | NOT STARTED | Sprint 7 |
| 8.2 Step 1: Causal Decomposition | CC | NOT STARTED | 8.1 |
| 8.3 Step 2: Framework Matching | CC | NOT STARTED | 8.1 |
| 8.4 Step 3: Mechanism Tracing (single-template) | CC | NOT STARTED | 8.3 |
| 8.5 Step 4: Three core operations (SUBSTITUTE, VARY_MOD, BLOCK) | CC | NOT STARTED | 8.4 |
| 8.6 Step 4: Remaining 7 operations | Antigravity | NOT STARTED | 8.5 (needs pattern) |
| 8.7 Step 5: Convergence assessment | CC | NOT STARTED | 8.5 |
| 8.8 Step 6: Composition failure detection | CC | NOT STARTED | 8.7 |
| 8.9 Step 7: Prioritization | CC | NOT STARTED | 8.8 |
| 8.10 Pipeline orchestrator + integration | CC | NOT STARTED | 8.9 |
| 8.11 Step 3 upgrade: multi-template composition | CC | NOT STARTED | 8.10 |
| 8.12 Validate CMR output schema against web of belief | Codex | NOT STARTED | 8.10 |
| 8.13 End-to-end test: Ulrich 1984 worked example | CC | NOT STARTED | 8.10 |

## Sprint 9: Pipeline Health

| Task | Agent | Status | Dependency |
|---|---|---|---|
| 9.1 Full test suite, report coverage | CC | NOT STARTED | Sprint 8 |
| 9.2 Cross-repo drift check (final) | Codex | NOT STARTED | Sprint 8 |
| 9.3 Pipeline expectation tests | CC | NOT STARTED | 9.1 |
| 9.4 Performance profiling | CC | NOT STARTED | 9.3 |

## Theory Work (Opus)

| Task | Status | Dependency |
|---|---|---|
| Panel IV: Cognitive Control & Reward | ✅ DONE (doc 14) | — |
| Panel V: Social Brain | READY TO RUN | David's go-ahead |
| Panel T2-A: ART Reduction | NOT STARTED | Post Sprint 7 |
| Panel T2-B: SRT Reduction | NOT STARTED | Post Sprint 7 |
| Panel T2-C: Biophilia/Prospect-Refuge | NOT STARTED | Post Sprint 7 |
| Review Antigravity's 28 template encodings | NOT STARTED | AG completes 7.5 |
| Review CMR output against Ulrich worked example | NOT STARTED | CC completes 8.13 |

---

# IMMEDIATE NEXT TASKS — WHO DOES WHAT NOW

## CC — Next Task (after Sprint 0.1–0.3 merge)

**Task 1 (immediate)**: Review Codex's migration artifacts in `migration_artifacts/`. Apply patches that are clean; flag any that conflict with your Sprint 0 directory changes. This should be fast — the patches are small.

**Task 2 (Sprint 1.1)**: Claim node extensions. Add `argument_scheme` and `critical_questions` fields to claim nodes. Reference: doc 09 Decision 1 (canonical GapType includes CRITICAL_QUESTION and ARGUMENT_ATTACK).

**Task 3 (Sprint 1.2–1.3)**: Edge type and node type consolidation. Two competing enum pairs need to merge:
- ConstraintType (13 values) + EdgeType (19 values) → one canonical enum
- NodeDomain + NodeTypeFamily → one canonical enum

Read doc 08 (Audit Synthesis) for the collision details. Produce a reconciliation proposal before implementing — Opus will review if there are theoretical judgment calls.

---

## Codex — Next Task

**Task (immediate)**: Run the 5 migration scripts in non-dry mode. Stage all generated artifacts (patches, adapters, reports) into `migration_artifacts/` for CC review. Commit as a separate branch so CC can cherry-pick.

**Task (after CC finishes Sprint 1.2–1.3)**: Sprint 1.4 — run `check_enum_drift.py` against the consolidated enums. Report any new cross-repo drift introduced by the merge.

**Also**: After CC registers the 5 new `structural_pattern` values from Panel IV (Sprint 7.7b), validate they are in `canonical_enums.json`. No rush — this is a Sprint 7 task.

---

## Antigravity — Next Task

**Task (immediate)**: Update `docs/template_id_aliases.json` to include the 7 new Panel IV templates. Here is the exact data to add:

```json
{
  "id": "NM_REWARD_PREDICTION_ERROR_001",
  "number": 41,
  "name": "Environmental Reward Prediction Error",
  "aliases": ["NM_RPE_001"],
  "frameworks": ["NM"]
},
{
  "id": "NM_WANTING_LIKING_DISSOCIATION_001",
  "number": 42,
  "name": "Architectural Wanting-Liking Dissociation",
  "aliases": [],
  "frameworks": ["NM"]
},
{
  "id": "CROSS_MB_MF_ARBITRATION_001",
  "number": 43,
  "name": "Model-Based / Model-Free Navigation Arbitration",
  "aliases": [],
  "frameworks": ["SN", "DP", "NM"]
},
{
  "id": "CROSS_HIERARCHICAL_CONTROL_001",
  "number": 44,
  "name": "Hierarchical Control Gradient in Architectural Demands",
  "aliases": [],
  "frameworks": ["PP", "DT", "MS"]
},
{
  "id": "CROSS_PROACTIVE_REACTIVE_CONTROL_001",
  "number": 45,
  "name": "Proactive-Reactive Control Mode and Architectural Predictability",
  "aliases": ["CROSS_PROACTIVE_REACTIVE_001"],
  "frameworks": ["PP", "DT", "NM"]
},
{
  "id": "CROSS_THALAMIC_ENVIRONMENTAL_FILTER_001",
  "number": 46,
  "name": "Thalamic Environmental Filtering (Pulvinar)",
  "aliases": [],
  "frameworks": ["MSI", "PP"]
},
{
  "id": "CROSS_WM_GAMMA_BETA_DYNAMICS_001",
  "number": 47,
  "name": "WM Gamma/Beta Dynamics in Environmental Processing",
  "aliases": [],
  "frameworks": ["MS", "DT"]
}
```

Append these 7 entries to the existing 40 in the JSON array. Verify the file still parses with `python3 -c "import json; json.load(open('docs/template_id_aliases.json'))"`.

**After that**: Antigravity is idle until Sprint 4b.3 (method metadata extraction) or Sprint 7.5 (mechanical template encoding). Sprint 7.5 is the big job but depends on CC building the DB models first.

---

## Opus — What I Am Doing Now

1. **✅ Completed**: Panel IV — 7 new templates specified, verdicts recorded.
2. **Ready**: Panel V (Social Brain) — I have the panelist list and questions from doc 09. Can run on David's signal.
3. **Available**: Theory referee for CC during Sprint 1 enum consolidation — if ConstraintType/EdgeType merger raises theoretical questions, I adjudicate.
4. **Preparing**: Once Antigravity starts Sprint 7.5 (28 template encodings), I will review each batch for theoretical accuracy before CC loads them into the DB.

---

# SUMMARY COUNTS

| Metric | Value |
|---|---|
| Total templates specified | 47 (40 original + 7 Panel IV) |
| Templates encoded in code | 0 (Sprint 7 not started) |
| Tier 1 frameworks | 10 (unchanged) |
| Canonical decisions | 8 (unchanged) |
| Panels completed | I, II, III, IV |
| Panels remaining | V, T2-A, T2-B, T2-C |
| Tests passing | 2,578 (1 expected failure) |
| Sprint 0 tasks | 7/8 complete (CC 0.1–0.3 finishing) |
| Sprint 0 new tasks | 0.5b (AG alias map update for T41–T47) |

---

*Tracker created: February 15, 2026*
*Next document sequence number: 16*
*Reminder: Download all session documents before closing.*
