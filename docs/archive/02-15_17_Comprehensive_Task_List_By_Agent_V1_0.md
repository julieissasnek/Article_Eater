# COMPREHENSIVE TASK LIST BY AGENT
## Article Eater — February 15, 2026 — Document 17
## All tasks, all agents, full granularity. Includes Opus theory work.

---

# OPUS — THEORY ARCHITECT & MANAGER

Opus tasks are the intellectual spine of the project. They produce specs that the other three agents implement. Estimated effort is in "panel-equivalents" where Panel IV ≈ 1.0.

## Immediate (This Session / Next Session)

| ID | Task | Effort | Dependency | Output |
|---|---|---|---|---|
| **O-1** | **Panel D-1: ReductionClaim Architecture** | 0.3 | None | Python dataclass spec for `ReductionClaim`; integration rules with web of belief constraint types; versioning policy; relationship to 1,361 staging theory-links |
| | Convene: Glymour, Pearl, Gärdenfors, Bechtel, + 1-2 others | | | |
| | Key questions: single chain vs DAG? Irreducible residual representation? How does it map to `MechanismTrace`? How do the 1,361 staging rows get persisted via this structure? | | | |
| **O-2** | **Panel V: Social Brain** | 1.0 | None (parallel to O-1) | Verdict on Tier 1 promotion; new templates if warranted; disposition of T19 (social affordance) |
| | Convene: Lieberman, Saxe, Dunbar, Bavelier, S. Cacioppo | | | |
| | Key questions: promote to Tier 1? TPJ dual role? Dunbar's number as architectural constraint? Social isolation as allostatic factor? | | | |
| **O-3** | **Break Tier 2 panels into granular tasks** | 0.2 | O-1 complete | Task specs for T2-A, T2-B, T2-C with inputs, outputs, dependencies, and effort estimates |
| | Uses ReductionClaim spec from O-1 + Antigravity's construct map + Codex's staging data counts | | | |
| **O-4** | **Update Sprint Plan & Global Tracker** | 0.1 | O-1, O-2, O-3 | Revised docs 12 and 15 incorporating all new tasks |
| | Insert: ReductionClaim model → Sprint 7.9; `reduce_tier2_theory()` → Sprint 8.14; staging theory-link persistence → Sprint 5 or 7; any new templates from Panel V | | | |

## Tier 2 Reduction Panels (After O-1 and O-3)

| ID | Task | Effort | Dependency | Output |
|---|---|---|---|---|
| **O-5** | **Panel T2-A: ART Reduction** | 0.8 | O-1, O-3 | ReductionClaim instances for 4 ART constructs (Soft Fascination, Being Away, Extent, Compatibility); irreducible residual assessment; reconciliation against 1,251 staging ART links |
| | Convene: Berman, R. Kaplan, Hunter, Kahn, Joye, White | | | |
| | Method: experts produce top-down decomposition → compare against bottom-up empirical links → flag discrepancies | | | |
| **O-6** | **Panel T2-B: SRT Reduction** | 0.5 | O-1, O-3 | ReductionClaim instances for 3 SRT constructs (Immediate Affective Response, Parasympathetic Activation, Cortisol Reduction); irreducible residual; reconciliation against 3 staging SRT links (sparse — mostly top-down) |
| | Convene: Ulrich, Berto, Grinde, Ellard | | | |
| **O-7** | **Panel T2-C: Biophilia / Prospect-Refuge / Pattern Language** | 0.7 | O-1, O-3 | ReductionClaim instances for 4+ constructs (Prospect, Refuge, Complexity, Fractal Fluency); reconciliation against 102 staging biophilia links |
| | Convene: Beatley (for Kellert), Hildebrand, Salingaros, Altomonte | | | |
| | Extra question: Altomonte's finding that IEQ factors interact multiplicatively — does this challenge T29's summation assumption? | | | |

## Ongoing / Reactive

| ID | Task | Effort | Dependency | Output |
|---|---|---|---|---|
| **O-8** | **Theory referee for CC: Sprint 1 enum consolidation** | 0.1 per call | CC hits a judgment call during 1.2-1.3 | Binding decision on how merged enums map to theoretical categories |
| **O-9** | **Review Antigravity's 28 template encodings** | 0.5 | AG completes Sprint 7.5 | Approved/corrected template batches ready for CC to load |
| **O-10** | **Review CMR output vs Ulrich worked example** | 0.3 | CC completes Sprint 8.13 | Validation report: does pipeline reproduce expected predictions from doc 11 Part 4? |
| **O-11** | **Theory questions from CC during Sprint 7-8** | 0.1 per call | CC encounters theoretical ambiguity | Binding answers on template semantics, bridging quality assignments, scope conditions |

### Opus Total Estimated Effort: ~4.5 panel-equivalents remaining

---

# CLAUDE CODE (CC) — PRIMARY CODEBASE ENGINEER

CC does ~70% of all implementation work. Tasks listed in sprint order with current status.

## Sprint 0 (Foundation) — ✅ EFFECTIVELY DONE

| ID | Task | Status | Notes |
|---|---|---|---|
| CC-0.1 | Create `src/queue/`, `src/theory/`, `src/cmr/` | ✅ DONE | Files in place, not git-committed |
| CC-0.2 | GapType reconciliation → `src/epistemic/gap_types.py` | ✅ DONE | Canonical 8-value enum, imports updated |
| CC-0.3 | Update `theory_bootstrap.py` to 10 frameworks | ✅ DONE | 15 theories registered, tests pass |
| CC-0.R | **Review Codex migration patches** | **NEXT** | Review `migration_artifacts/`, apply clean patches, flag conflicts |

## Sprint 1 (Epistemic Core Extensions)

| ID | Task | Status | Dependency | Notes |
|---|---|---|---|---|
| CC-1.1 | Claim node extensions (`argument_scheme`, `critical_questions`) | NOT STARTED | Sprint 0 merge | Ref: doc 09 Decision 1 |
| CC-1.2 | Edge type consolidation (ConstraintType 13 vals + EdgeType 19 vals → one enum) | NOT STARTED | Sprint 0 merge | Ref: doc 08 collision #18. **May need Opus referee (O-8)** |
| CC-1.3 | Node type consolidation (NodeDomain + NodeTypeFamily → one) | NOT STARTED | Sprint 0 merge | Ref: doc 08 collision #19. **May need Opus referee (O-8)** |

## Sprint 2 (Bayesian Network Extensions)

| ID | Task | Status | Dependency |
|---|---|---|---|
| CC-2.1 | BN: add d-separation, conditional queries | NOT STARTED | Sprint 1 |
| CC-2.2 | Schema migration: add new fields to SQLAlchemy models | NOT STARTED | Sprint 1 |

## Sprint 3 (Coherence & Bridge)

| ID | Task | Status | Dependency |
|---|---|---|---|
| CC-3.1 | Coherence engine upgrade (`scalable_coherence.py`) | NOT STARTED | Sprint 2 |
| CC-3.2 | Bridge warrant service extensions | NOT STARTED | Sprint 2 |

## Sprint 4/4b (Extraction Pipeline)

| ID | Task | Status | Dependency |
|---|---|---|---|
| CC-4.1 | Extraction pipeline extensions (argument_scheme, CQ fields) | NOT STARTED | Sprint 3 |
| CC-4.2 | Source quality scoring refinement | NOT STARTED | Sprint 3 |
| CC-4b.1 | Method registry implementation | NOT STARTED | Sprint 4 |
| CC-4b.2 | Ecological validity scoring | NOT STARTED | CC-4b.1 |

## Sprint 5 (Integration)

| ID | Task | Status | Dependency |
|---|---|---|---|
| CC-5.1 | Wire extraction → web of belief → BN pipeline | NOT STARTED | Sprint 4b |
| CC-5.2 | End-to-end pipeline test (paper in → beliefs out) | NOT STARTED | CC-5.1 |
| CC-5.3★ | **NEW: Persist 1,361 staging theory-links** | NOT STARTED | CC-5.1 | 
| | *The staging rows in `data/review/tranche80_confirmed_rows.csv` (1,251 ART, 102 biophilia, 3 SRT) need to be loaded into the web of belief with proper theory_id and constraint types. May move to Sprint 7 depending on ReductionClaim model availability.* | | |

## Sprint 6 (Research Queue)

| ID | Task | Status | Dependency |
|---|---|---|---|
| CC-6.1 | ResearchTarget model (with canonical GapType) | NOT STARTED | Sprint 5 |
| CC-6.2 | ResearchQueueService implementation | NOT STARTED | CC-6.1 |
| CC-6.3 | VOI scoring integration | NOT STARTED | CC-6.2 |

## Sprint 7 (Theory Tier) — CRITICAL

| ID | Task | Status | Dependency | Source |
|---|---|---|---|---|
| CC-7.1 | Tier1Framework model in DB | NOT STARTED | Sprint 6 | doc 07 §1 |
| CC-7.2 | Independence matrix in DB | NOT STARTED | CC-7.1 | doc 07 §2 |
| CC-7.3 | MechanisticTemplate + CausalLink models in DB | NOT STARTED | CC-7.1 | doc 07 §3 |
| CC-7.4 | Encode 12 seed templates | NOT STARTED | CC-7.3 | docs 07 + 10 |
| CC-7.4b | Encode 7 Panel IV templates (T41–T47) | NOT STARTED | CC-7.3 | doc 14 |
| CC-7.4c★ | **NEW: Encode Panel V templates (if any)** | BLOCKED | O-2 (Panel V) | TBD |
| CC-7.7 | Cross-framework bridging rules in DB | NOT STARTED | CC-7.4 | doc 06 Part 3 |
| CC-7.7b | Register 5 new `structural_pattern` enum values (COMPETITION, STRATIFICATION, BIFURCATION, GATING, OSCILLATORY_GATING) | NOT STARTED | CC-7.3 | doc 14 Part 7 |
| CC-7.9★ | **NEW: Implement ReductionClaim model in DB** | BLOCKED | O-1 (Panel D-1) | Opus spec |
| | *Dataclass + SQLAlchemy model + migration. Depends on D-1 panel output for structure.* | | | |

## Sprint 8 (CMR Pipeline) — CRITICAL

| ID | Task | Status | Dependency |
|---|---|---|---|
| CC-8.1 | CMR data models (`models.py`) | NOT STARTED | Sprint 7 |
| CC-8.2 | Step 1: Causal Decomposition | NOT STARTED | CC-8.1 |
| CC-8.3 | Step 2: Framework Matching | NOT STARTED | CC-8.1 |
| CC-8.4 | Step 3: Mechanism Tracing (single-template) | NOT STARTED | CC-8.3 |
| CC-8.5 | Step 4: Three core operations (SUBSTITUTE, VARY_MOD, BLOCK) | NOT STARTED | CC-8.4 |
| CC-8.7 | Step 5: Convergence assessment | NOT STARTED | CC-8.5 |
| CC-8.8 | Step 6: Composition failure detection (Barrett's R10) | NOT STARTED | CC-8.7 |
| CC-8.9 | Step 7: Prioritization | NOT STARTED | CC-8.8 |
| CC-8.10 | Pipeline orchestrator + integration | NOT STARTED | CC-8.9 |
| CC-8.11 | Step 3 upgrade: multi-template composition | NOT STARTED | CC-8.10 |
| CC-8.13 | End-to-end test: Ulrich 1984 worked example | NOT STARTED | CC-8.10 |
| CC-8.14★ | **NEW: `reduce_tier2_theory()` entry point** | BLOCKED | O-1 + CC-8.10 |
| | *Alternative CMR entry point that takes a Tier 2 theory claim as input and produces a ReductionClaim via mechanical template matching. Enables validation of panel-produced reductions.* | | |

## Sprint 9 (Pipeline Health)

| ID | Task | Status | Dependency |
|---|---|---|---|
| CC-9.1 | Full test suite + coverage report | NOT STARTED | Sprint 8 |
| CC-9.3 | Pipeline expectation tests | NOT STARTED | CC-9.1 |
| CC-9.4 | Performance profiling | NOT STARTED | CC-9.3 |

### CC Total: ~45 tasks, ~70% of implementation work

---

# CODEX — CROSS-REPO VALIDATION & MIGRATION

Codex operates across all 5 repos. ~15% of total work. Periodic rather than continuous.

## Completed

| ID | Task | Status |
|---|---|---|
| CX-0.6 | Cross-repo vocab contract (`canonical_enums.json` + `check_enum_drift.py`) | ✅ DONE |
| CX-0.7 | 5 migration adapter scripts (dry-run verified, lossless tests pass) | ✅ DONE |

## Immediate

| ID | Task | Status | Dependency | Notes |
|---|---|---|---|---|
| CX-0.7b | Stage migration artifacts for CC review | **NEXT** | None | Run 5 scripts in non-dry mode, stage to `migration_artifacts/`, commit on separate branch |

## Sprint-Gated

| ID | Task | Status | Dependency | Notes |
|---|---|---|---|---|
| CX-1.4 | Cross-repo contract compliance after CC's enum consolidation | NOT STARTED | CC finishes 1.2–1.3 | Run `check_enum_drift.py` against consolidated enums |
| CX-3.3 | Periodic drift check | NOT STARTED | Sprint 3 boundary | Standard periodic check |
| CX-4b.4 | Validate extraction output against canonical schemas | NOT STARTED | Sprint 4b | Cross-repo schema check |
| CX-5.3 | Cross-repo contract compliance for full pipeline | NOT STARTED | CC-5.2 | Final pre-theory-tier validation |
| CX-7.7c★ | **NEW: Validate 5 new `structural_pattern` values in `canonical_enums.json`** | NOT STARTED | CC-7.7b | After CC registers COMPETITION, STRATIFICATION, BIFURCATION, GATING, OSCILLATORY_GATING |
| CX-7.8 | Validate all templates load and cross-reference correctly | NOT STARTED | AG-7.5 complete | Schema validation, FK integrity across all 47+ templates |
| CX-7.9b★ | **NEW: Add `TheoryLevel` enum to cross-repo contract** | NOT STARTED | O-1 (Panel D-1) | Currently AE-local only. After D-1 defines ReductionClaim, Codex adds theory-tier enum to `canonical_enums.json` |
| CX-8.12 | Validate CMR output schema against web of belief | NOT STARTED | CC-8.10 | DERIVED_HYPOTHESIS nodes must conform |
| CX-9.2 | Final cross-repo drift check | NOT STARTED | Sprint 8 complete | Full system validation |

### Codex Total: ~10 tasks, ~15% of implementation work

---

# ANTIGRAVITY — MECHANICAL ENCODING & BOUNDED TASKS

Antigravity handles precise, well-specified mechanical work. ~15% of total. Needs very clear instructions.

## Completed

| ID | Task | Status |
|---|---|---|
| AG-0.0 | Fix test suite | ✅ DONE (2578 passing, 1 expected failure) |
| AG-0.4 | Update stale docs (CLAUDE.md, IMPLEMENTATION_TASKS.md) | ✅ DONE |
| AG-0.5 | Template ID alias map (T1–T40) | ✅ DONE |
| AG-T2map | Extract preliminary Tier 2 construct map | ✅ DONE (`docs/tier2_construct_map_preliminary.md`) |

## Immediate

| ID | Task | Status | Dependency | Notes |
|---|---|---|---|---|
| AG-0.5b | Update alias map with T41–T47 | **NEXT** | None | Data provided in doc 15. Append 7 entries, verify JSON parses. |
| AG-0.5c★ | **NEW: Update alias map with Panel V templates (if any)** | BLOCKED | O-2 | Depends on Panel V output |

## Sprint-Gated

| ID | Task | Status | Dependency | Notes |
|---|---|---|---|---|
| AG-4b.3 | Extract method metadata from 7 finding files | NOT STARTED | Sprint 4 | Mechanical: read each JSONL, add `study_design` field |
| AG-6.4 | Queue prioritization panel weights | NOT STARTED | Sprint 6 | Mechanical: encode weights from docs into config |
| AG-7.5 | **Encode remaining 28 templates (T1–T40 minus 12 seeds)** | NOT STARTED | CC-7.4 (seed pattern needed) | **BIG JOB**: 4 batches of 7 templates each, following seed patterns from docs 07+10. Source: Panel I–III documents. Opus reviews each batch (O-9). |
| AG-7.6 | Template ID alias map integration into DB | NOT STARTED | AG-0.5b + CC-7.3 | Wire alias map JSON into the DB template model |
| AG-8.6 | CMR Step 4: Remaining 7 prediction operations | NOT STARTED | CC-8.5 (needs pattern from first 3) | Mechanical: follow pattern CC establishes for SUBSTITUTE, VARY_MOD, BLOCK |
| AG-T2extract★ | **NEW: Extract Tier 2 → template references from Panel I–III docs during Sprint 7.5** | NOT STARTED | AG-7.5 | Two birds: while encoding templates, also flag any Tier 2 theory references in the narrative. Produces enriched construct map for Opus panels O-5/O-6/O-7. |

### Antigravity Total: ~8 tasks, ~15% of implementation work

---

# CROSS-AGENT DEPENDENCIES (Critical Path)

```
O-1 (ReductionClaim spec) ──→ CC-7.9 (implement model)
                           ──→ CX-7.9b (cross-repo enum)
                           ──→ O-3 (Tier 2 task breakdown)
                               ──→ O-5, O-6, O-7 (Tier 2 panels)
                                   ──→ CC-8.14 (reduce_tier2_theory validation)

O-2 (Panel V) ──→ CC-7.4c (encode new templates, if any)
              ──→ AG-0.5c (alias map update)
              ──→ O-4 (sprint plan update)

CC-0.R (review Codex patches) ──→ CC-1.1, 1.2, 1.3 (Sprint 1)
                                  ──→ CX-1.4 (drift check)

CC-7.4 (seed templates) ──→ AG-7.5 (28 templates) ──→ O-9 (review) ──→ CX-7.8 (validate)

CC-8.5 (3 core ops) ──→ AG-8.6 (7 remaining ops) ──→ CC-8.10 (orchestrator)
```

---

# SUMMARY COUNTS

| Agent | Done | Immediate | Sprint-Gated | Blocked on Opus | Total Remaining |
|---|---|---|---|---|---|
| **Opus** | 5 panels + 9 docs | 2 (D-1, V) | 3 Tier 2 panels | — | ~11 |
| **CC** | Sprint 0 | 1 (review patches) | ~40 across Sprints 1–9 | 3 (7.4c, 7.9, 8.14) | ~44 |
| **Codex** | Sprint 0.6–0.7 | 1 (stage artifacts) | ~8 across Sprints 1–9 | 1 (7.9b) | ~10 |
| **Antigravity** | Sprint 0.0, 0.4, 0.5 | 1 (alias update) | ~6 across Sprints 4b–8 | 1 (0.5c) | ~8 |

**Critical path to CMR**: CC Sprints 1→2→3→4→5→6→7→8. Opus theory work (O-1, O-2) should run in parallel now so it's ready when CC reaches Sprint 7.

---

*Task list created: February 15, 2026*
*Next document sequence number: 18*
