# ARCH-4 Sprint Plan: Formal Epistemic Calculus

**Date**: 2026-02-12
**Panel**: P-ARCH4-EPISTEMIC-CALCULUS
**Total Duration**: 12 sprints (~12 weeks)

---

## Overview

```
Phase 1: Data Model ──────► Phase 2: Ranking ──────► Phase 3: Warrant
(2 sprints)                 (2 sprints)              (3 sprints)
                                                           │
                                                           ▼
Phase 6: Verification ◄──── Phase 5: Bridge ◄────── Phase 4: Grounding
(2 sprints)                 (1 sprint)               (2 sprints)
```

---

## Phase 1: Data Model Refactoring (2 sprints)

### Sprint 1.1: Design & Contracts

**Goal**: Define new data model with panel-approved structure

| ID | Task | Deliverable | Acceptance Criteria |
|----|------|-------------|---------------------|
| 1.1.1 | Design PropositionalContent class | `contracts/schemas/propositional_content.schema.json` | Schema validated by Liskov voice |
| 1.1.2 | Design EpistemicStatus class | `contracts/schemas/epistemic_status.schema.json` | Includes rank, neg_rank, warrant_status |
| 1.1.3 | Design Provenance class | `contracts/schemas/provenance.schema.json` | Includes sources, grounding basis |
| 1.1.4 | Design ExperientialClaim class | `contracts/schemas/experiential_claim.schema.json` | Per Haack's grounding requirements |
| 1.1.5 | Write migration strategy doc | `docs/ARCH4_MIGRATION_STRATEGY.md` | Backward compatibility plan |

**Exit Criteria**: All schemas pass JSON Schema validation; Liskov panel review approves

---

### Sprint 1.2: Implementation & Migration

**Goal**: Implement new model and migrate existing data

| ID | Task | Deliverable | Acceptance Criteria |
|----|------|-------------|---------------------|
| 1.2.1 | Implement PropositionalContent | `src/models/propositional_content.py` | Unit tests pass |
| 1.2.2 | Implement EpistemicStatus | `src/models/epistemic_status.py` | Includes RankPair dataclass |
| 1.2.3 | Implement Provenance | `src/models/provenance.py` | Includes ExperientialClaim |
| 1.2.4 | Refactor Belief to use composition | `src/services/web_of_belief.py` | Belief uses new components |
| 1.2.5 | Write migration script | `scripts/migrate_beliefs_to_v24.py` | Existing 128 beliefs migrated |
| 1.2.6 | Update persistence layer | `src/services/web_persistence.py` | New schema in SQLite |

**Exit Criteria**: All existing tests pass; migration completes without data loss

**Panel Review**: Liskov — architecture cleanliness

---

## Phase 2: Ranking Service (2 sprints)

### Sprint 2.1: Core Ranking

**Goal**: Implement Spohn's ranking theory basics

| ID | Task | Deliverable | Acceptance Criteria |
|----|------|-------------|---------------------|
| 2.1.1 | Create RankingService class | `src/services/ranking_service.py` | Clean interface per Liskov |
| 2.1.2 | Implement rank computation from evidence | Method: `compute_base_ranks()` | Observational beliefs get rank 0 |
| 2.1.3 | Implement belief/disbelief semantics | Methods: `is_believed()`, `is_disbelieved()` | Correct per Spohn's inversion |
| 2.1.4 | Implement rank combination | Method: `combine_ranks()` | For beliefs with multiple sources |
| 2.1.5 | Write property-based tests | `tests/test_ranking_service.py` | Hypothesis tests for rank properties |

**Exit Criteria**: Rank computation is pure (no side effects); semantics match Spohn

---

### Sprint 2.2: Conditionalization & Defeat Adjustment

**Goal**: Implement belief revision via conditionalization

| ID | Task | Deliverable | Acceptance Criteria |
|----|------|-------------|---------------------|
| 2.2.1 | Implement Spohn conditionalization | Method: `conditionalize(evidence, firmness)` | Formula: κ_new(B) = min(κ(B\|E), κ(B\|¬E) + n) |
| 2.2.2 | Implement conditional ranks | Method: `conditional_rank(B, E)` | Formula: κ(B\|E) = κ(B∧E) - κ(E) |
| 2.2.3 | Implement defeat adjustment | Method: `adjust_for_defeat(ranks, defeats)` | Ranks increase when defeated |
| 2.2.4 | Implement rank history tracking | Class: `RankHistory` | For debugging and explanation |
| 2.2.5 | Integration tests | `tests/test_ranking_integration.py` | End-to-end rank computation |

**Exit Criteria**: Conditionalization passes formal properties

**Panel Review**: Spohn — correctness of ranking semantics

---

## Phase 3: Warrant Service (3 sprints)

### Sprint 3.1: Prima Facie Warrant

**Goal**: Implement basic warrant without defeat

| ID | Task | Deliverable | Acceptance Criteria |
|----|------|-------------|---------------------|
| 3.1.1 | Create WarrantService class | `src/services/warrant_service.py` | Clean interface |
| 3.1.2 | Define WarrantStatus enum | `WARRANTED`, `DEFEATED`, `SUSPENDED`, `UNGROUNDED` | Clear semantics |
| 3.1.3 | Implement prima facie warrant | Method: `compute_prima_facie(belief_id)` | Based on support constraints |
| 3.1.4 | Implement warrant propagation | Method: `propagate_warrant()` | Warrant flows through support |
| 3.1.5 | Handle observational grounding | Special case: observational beliefs prima facie warranted | Per Haack |

**Exit Criteria**: Prima facie warrant computed correctly for acyclic support

---

### Sprint 3.2: Defeat Detection

**Goal**: Implement rebutting and undercutting defeat

| ID | Task | Deliverable | Acceptance Criteria |
|----|------|-------------|---------------------|
| 3.2.1 | Extend ConstraintType enum | Add: `REBUTS`, `UNDERCUTS` | Clear defeat types |
| 3.2.2 | Refactor defeater search | Update `find_defeaters_for_belief()` | Classify by defeat type |
| 3.2.3 | Implement rebutting defeat | Method: `check_rebutting_defeat(belief_id)` | Contradictory conclusions |
| 3.2.4 | Implement undercutting defeat | Method: `check_undercutting_defeat(belief_id)` | Attacks inference link |
| 3.2.5 | Implement defeat strength | Use ranks for defeat strength | Per Spohn-Pollock integration |
| 3.2.6 | Add attack_point field | Track what undercutter attacks | For explanation |

**Exit Criteria**: Both defeat types correctly identified; INV-4 (DefeatAsymmetry) holds

---

### Sprint 3.3: Reinstatement

**Goal**: Implement recursive defeat and reinstatement

| ID | Task | Deliverable | Acceptance Criteria |
|----|------|-------------|---------------------|
| 3.3.1 | Implement recursive warrant check | Method: `is_warranted(belief_id, seen=set())` | Handles cycles |
| 3.3.2 | Implement reinstatement logic | If defeater is defeated, target reinstated | Per Pollock |
| 3.3.3 | Implement defeat chain tracking | Class: `DefeatChain` | For explanation |
| 3.3.4 | Add cycle detection | Prevent infinite loops | Return SUSPENDED if cyclic |
| 3.3.5 | Comprehensive warrant tests | Test cases from Pollock literature | Match expected behavior |
| 3.3.6 | Property tests for consistency | INV-1: ¬(warranted(B) ∧ warranted(rebutter(B))) | Must always hold |

**Exit Criteria**: Reinstatement works; INV-1 (Consistency) verified

**Panel Review**: Pollock — defeat and reinstatement correctness

---

## Phase 4: Grounding Service (2 sprints)

### Sprint 4.1: Experiential Basis

**Goal**: Track how beliefs connect to experience

| ID | Task | Deliverable | Acceptance Criteria |
|----|------|-------------|---------------------|
| 4.1.1 | Create GroundingService class | `src/services/grounding_service.py` | Clean interface |
| 4.1.2 | Implement experiential claim extraction | From paper metadata | Source, directness, content |
| 4.1.3 | Implement grounding metric | Method: `compute_grounding(belief_id)` | 0-1 scale, higher = better grounded |
| 4.1.4 | Track grounding chains | How observational → empirical → theoretical | Per Haack's crossword |
| 4.1.5 | Add directness metric | How directly observed vs. inferred | Affects grounding score |

**Exit Criteria**: Every belief has a grounding score; observational beliefs score highest

---

### Sprint 4.2: Foundherentist Justification

**Goal**: Combine grounding and coherence per Haack

| ID | Task | Deliverable | Acceptance Criteria |
|----|------|-------------|---------------------|
| 4.2.1 | Refactor coherence computation | Extract to method in GroundingService | Clean separation |
| 4.2.2 | Implement justification status | Enum: `WELL_JUSTIFIED`, `GROUNDED_ONLY`, `COHERENT_ONLY`, `UNJUSTIFIED` | Per Haack's categories |
| 4.2.3 | Combine grounding + coherence | Method: `compute_justification_status()` | Both required for WELL_JUSTIFIED |
| 4.2.4 | Implement crossword constraint | High coherence can't compensate for zero grounding | Per Haack |
| 4.2.5 | Add justification explanation | Method: `explain_justification(belief_id)` | Human-readable |
| 4.2.6 | Verify INV-2 (Groundedness) | warranted → grounded ∨ supported_by_warranted | Must hold |

**Exit Criteria**: Foundherentist justification computed correctly

**Panel Review**: Haack — foundherentist structure preserved

---

## Phase 5: Epistemic-Causal Bridge (1 sprint)

### Sprint 5.1: Graph Confidence

**Goal**: Connect epistemic layer to causal layer

| ID | Task | Deliverable | Acceptance Criteria |
|----|------|-------------|---------------------|
| 5.1.1 | Create GraphConfidenceService | `src/services/graph_confidence_service.py` | Clean interface |
| 5.1.2 | Implement edge confidence | Method: `edge_confidence(source, target)` | From warrant + rank of supporting beliefs |
| 5.1.3 | Implement structure confidence | Method: `structure_confidence()` | Overall graph confidence |
| 5.1.4 | Add uncertainty quantification | Return intervals, not just points | Per Pearl |
| 5.1.5 | Basic identifiability check | Method: `is_identifiable(X, Y)` | Check for confounders |
| 5.1.6 | Verify INV-5 (BridgeCoherence) | edge_confident → warranted support | Must hold |
| 5.1.7 | Update API endpoints | `/api/v1/integration/edge/{id}/confidence` | Expose confidence |

**Exit Criteria**: BN edges have epistemic confidence scores

**Panel Review**: Pearl — bridge quantification correct

---

## Phase 6: Formal Verification (2 sprints)

### Sprint 6.1: TLA+ Specification

**Goal**: Write formal specification

| ID | Task | Deliverable | Acceptance Criteria |
|----|------|-------------|---------------------|
| 6.1.1 | Define state space in TLA+ | `specs/EpistemicWeb.tla` | Beliefs, constraints, ranks, warrant |
| 6.1.2 | Define initial state | Empty web with no beliefs | Formally specified |
| 6.1.3 | Define transitions | AddBelief, AddConstraint, Revise, etc. | All state changes |
| 6.1.4 | Specify INV-1 (Consistency) | TLA+ predicate | Model checkable |
| 6.1.5 | Specify INV-2 (Groundedness) | TLA+ predicate | Model checkable |
| 6.1.6 | Specify INV-3 (RankCoherence) | TLA+ predicate | Model checkable |
| 6.1.7 | Specify INV-4 (DefeatAsymmetry) | TLA+ predicate | Model checkable |
| 6.1.8 | Specify INV-5 (BridgeCoherence) | TLA+ predicate | Model checkable |

**Exit Criteria**: Complete TLA+ specification compiles

---

### Sprint 6.2: Model Checking & Documentation

**Goal**: Verify properties and document refinement

| ID | Task | Deliverable | Acceptance Criteria |
|----|------|-------------|---------------------|
| 6.2.1 | Configure TLC model checker | `specs/EpistemicWeb.cfg` | Parameters set |
| 6.2.2 | Model check safety (INV-1,2,3,4,5) | TLC output | No violations found |
| 6.2.3 | Define liveness properties | Eventually warranted, eventually revised | Formally specified |
| 6.2.4 | Model check liveness | TLC output | Properties satisfied |
| 6.2.5 | Document refinement mapping | `docs/TLA_REFINEMENT.md` | Spec ↔ Code correspondence |
| 6.2.6 | Final integration test | All services working together | End-to-end pass |

**Exit Criteria**: All invariants verified; refinement documented

**Panel Review**: Lamport — specification rigor; All — final sign-off

---

## Sprint Summary

| Sprint | Phase | Focus | Duration |
|--------|-------|-------|----------|
| 1.1 | Data Model | Design & Contracts | 1 week |
| 1.2 | Data Model | Implementation & Migration | 1 week |
| 2.1 | Ranking | Core Ranking | 1 week |
| 2.2 | Ranking | Conditionalization | 1 week |
| 3.1 | Warrant | Prima Facie | 1 week |
| 3.2 | Warrant | Defeat Detection | 1 week |
| 3.3 | Warrant | Reinstatement | 1 week |
| 4.1 | Grounding | Experiential Basis | 1 week |
| 4.2 | Grounding | Foundherentist Justification | 1 week |
| 5.1 | Bridge | Graph Confidence | 1 week |
| 6.1 | Verification | TLA+ Specification | 1 week |
| 6.2 | Verification | Model Checking | 1 week |

**Total**: 12 sprints / 12 weeks

---

## Dependencies

```
1.1 ──► 1.2 ──► 2.1 ──► 2.2 ──┐
                              │
                              ▼
                        3.1 ──► 3.2 ──► 3.3 ──┐
                                              │
                              ┌───────────────┘
                              ▼
                        4.1 ──► 4.2 ──► 5.1 ──► 6.1 ──► 6.2
```

**Critical Path**: 1.1 → 1.2 → 2.1 → 2.2 → 3.1 → 3.2 → 3.3 → 4.1 → 4.2 → 5.1 → 6.1 → 6.2

**Parallelization Opportunity**: After Sprint 2.2, Sprints 3.x and 4.x could run in parallel if resources allow.

---

## Panel Review Checkpoints

| After Sprint | Reviewer | Focus |
|--------------|----------|-------|
| 1.2 | Liskov | Architecture cleanliness |
| 2.2 | Spohn | Ranking semantics |
| 3.3 | Pollock | Defeat and reinstatement |
| 4.2 | Haack | Foundherentist structure |
| 5.1 | Pearl | Bridge quantification |
| 6.2 | Lamport + All | Formal verification + final |

---

## Risk Register

| Risk | Mitigation |
|------|------------|
| Spohn semantics wrong | Panel review at Sprint 2.2; study original text |
| Reinstatement cycles | Cycle detection in Sprint 3.3; tested thoroughly |
| Migration breaks existing data | Backward compatibility in Sprint 1.2; rollback plan |
| TLA+ model checking blows up | Limit state space; use abstractions |
| Phase creep | Strict sprint boundaries; defer to future work |

---

## Success Metrics

| Metric | Target |
|--------|--------|
| All 5 invariants verified by TLC | 100% |
| Test coverage for new services | >90% |
| Existing tests still pass | 100% |
| Panel reviews pass | 6/6 |
| Refinement documented | Complete |

---

*Sprint plan ready for execution.*
*ARCH-4 | P-ARCH4-EPISTEMIC-CALCULUS | 2026-02-12*
