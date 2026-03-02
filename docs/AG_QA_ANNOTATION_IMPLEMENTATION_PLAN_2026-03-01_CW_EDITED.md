# QA & Annotation System: Spec, Plan, and Implementation

**CW Edit Pass: 2026-03-02**

> [CW NOTE] I've made substantive edits throughout, marked with `[CW]`. The big changes:
> 1. **Sprint order flipped**: Annotation unification (now Sprint A) before QA wiring (now Sprint B). Rationale below.
> 2. **SQ → ω, not SQ → Credence**: Source Quality should feed into `warrant_strength.py`'s ω computation, NOT the old credence system. Sprint CREDENCE-WARRANT established warrant-derived credence as canonical.
> 3. **Nightly warrant must use `warrant_strength.py`** (894 LOC, 62 tests, §48.3B), NOT `warrant_service.py` (486 LOC, old code).
> 4. **Three-phase annotation migration**, not big-bang.
> 5. **Naming**: All new code must use humanly meaningful hyphenated terms (e.g., `predictive-processing`, NOT `PP`). David hates 2-letter abbreviations. The 6 theory taxonomy JSON files AG created in `schemas/theory/` need this fix too.
> 6. **Ruthless V8 panel composition changes**.

---

## Status of Existing Specs

| System | Spec exists? | What it covers | What's missing |
|--------|-------------|----------------|----------------|
| **QA** | ✅ [QA_SYSTEM_SPEC.md](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/docs/QA_SYSTEM_SPEC.md) (602 lines) | 9 subsystems, 22 SCs, gap analysis, integration matrix | Implementation status tracking; post-fix verification |
| **Annotation** | ❌ No spec document | — | Everything: no single doc explains the annotation architecture |

---

## Part 1: QA System — Current State Audit

### 9 Subsystems (~8,500 LOC)

| # | Subsystem | LOC | Wired to Pipeline? | Wired to AESHI? | Tests? |
|---|-----------|-----|--------------------|--------------------|--------|
| 1 | [Reflex System](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/qa/reflex_system.py) | 1725 | ✅ Nightly stage | ✅ Via overseer | ✅ 23 classes |
| 2 | [Template QA](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/services/template_quality_assurance.py) | 247 | ❌ Manual only | ❌ | ⚠️ Partial |
| 3 | [Argument QA](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/argument/qa_handlers.py) | 219 | ❌ Manual only | ❌ | ⚠️ Partial |
| 4 | [Warrant Strength](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/services/warrant_strength.py) | 894 | ❌ Not nightly | ❌ | ✅ 62 tests |
| 5 | [Source Quality](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/epistemic/source_quality.py) | 319 | ❌ Computed but unused | ❌ | ✅ |
| 6 | [Gap Predictor](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/services/gap_predictor.py) | 1497 | ⚠️ Added to nightly discovery | ❌ | ⚠️ Partial |
| 7 | [VOI Scoring](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/cmr/voi_scoring.py) | 109 | ❌ | ❌ | ⚠️ |
| 8 | [VOI Search](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/services/voi_search.py) | 1946 | ❌ | ❌ | ⚠️ |
| 9 | [QA Cache](file:///Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/qa/qa_cache_manager.py) | 120 | ✅ Nightly | ❌ | ✅ |

> [CW] Row 4 corrected: The canonical warrant module is `warrant_strength.py` (894 LOC, 62 passing tests, implements §48.3B formula ω = ω_base × ω_conf × ω_rep × ω_meta). The older `warrant_service.py` (486 LOC) is legacy and should NOT be the target of new wiring. All nightly warrant computation must go through `warrant_strength.py`.

### 22 Success Conditions — Status

Already defined in QA_SYSTEM_SPEC.md §8. Here's what's been done:

| Tier | SC | Status | Notes |
|------|-----|--------|-------|
| 1 — Hygiene | SC-QA-01 to 04 | ✅ Done | All 15 reflexes run, report to overseer |
| 2 — Epistemic | SC-QA-05 (warrant runs) | ❌ **NOT DONE** | Warrant not run nightly |
| 2 | SC-QA-06 (zero INV-1) | ❌ **NOT DONE** | No check |
| 2 | SC-QA-07 (SQ computed) | ⚠️ Partial | Computed but not fed to ω [CW: not "credence" — feeds ω] |
| 2 | SC-QA-08 (DEFEATED flagged) | ✅ Done | WarrantStatusReflex added |
| 2 | SC-QA-09 (COHERENT_ONLY flagged) | ✅ Done | ProvenanceGroundingReflex added |
| 3 — Integration | SC-QA-10 (rollback→QA) | ✅ Done | Post-rollback hook added |
| 3 | SC-QA-11 (annotations→gaps) | ✅ Done | OPEN_QUESTION harvest added |
| 3 | SC-QA-12 (SENSITIVITY→template QA) | ❌ **NOT DONE** | |
| 3 | SC-QA-13 (provenance→AESHI) | ❌ **NOT DONE** | |
| 3 | SC-QA-14 (web UI warrant badges) | ❌ **NOT DONE** | Deferred (UI cycle) |
| 4 — Discovery | SC-QA-15 (nightly gap pred) | ✅ Done | Nightly discovery stage added |
| 4 | SC-QA-16 (high-VOI queries) | ⚠️ Partial | Infra exists, not closed loop |
| 4 | SC-QA-17 (nightly defeater search) | ✅ Done | Added to nightly discovery |
| 4 | SC-QA-18 (annotation harvest) | ✅ Done | Added to nightly discovery |
| 4 | SC-QA-19 (VOI re-score) | ✅ Done | Added to nightly discovery |
| 5 — Principles | SC-QA-20 (principles doc) | ❌ **NOT DONE** | No `EPISTEMIC_PRINCIPLES.md` |
| 5 | SC-QA-21/22 | ✅ Done | Independence/commitment in source_quality |

### QA Remaining Work

| Priority | What | Where | Effort |
|----------|------|-------|--------|
| **P1** | Nightly ω computation on all beliefs | `warrant_strength.py` → `nightly_integration_pipeline.py` | ~2 hrs |
| **P1** | Source Quality → ω_source component | `warrant_strength.py` | ~2 hrs |
| **P2** | SENSITIVITY_FLAG → template QA | `template_quality_assurance.py` | ~1 hr |
| **P2** | Provenance JustificationStatus → AESHI | `compute_system_health.py` | ~1 hr |
| **P2** | `EPISTEMIC_PRINCIPLES.md` | `docs/` | ~1 hr |
| **P3** | VOI count → AESHI component | `compute_system_health.py` | ~30 min |
| **P3** | Web UI warrant badges | TypeScript/React | ~4 hrs (deferred) |

> [CW] Critical correction in P1 rows:
> - "Nightly warrant computation" → "Nightly ω computation" — must use `warrant_strength.py`, not `warrant_service.py`
> - "Source Quality → Credence feedback" → "Source Quality → ω_source component" — SQ feeds into the ω formula as one of its inputs (specifically into `ω_base` via severity assessment, and potentially as a standalone `ω_source` multiplier). It does NOT feed into old-style credence directly. Sprint CREDENCE-WARRANT established that credence is now DERIVED from warrant strength: `credence(belief) = σ(Σ d_i · ω_i · δ_i · logit(p_lab_i))`. Wiring SQ into old credence would bypass this architecture entirely.
>
> Implementation sketch for SQ → ω integration:
> 1. In `warrant_strength.py`, add `compute_source_quality_modifier(article_metadata) → float` that calls `source_quality.py`'s existing scoring
> 2. This returns a multiplier in [0.7, 1.1] based on pre-registration, blinding, independence, sample adequacy
> 3. Apply as `ω_final = ω_base × ω_conf × ω_rep × ω_meta × ω_source`
> 4. The existing `SourceQualityIndicators` dataclass in `source_quality.py` already computes the right components — just need a bridge function
> 5. ~3 hours total including tests

---

## Part 2: Annotation System — Full Spec

### What Exists (Three Parallel Systems)

```
┌─────────────────────────────────────────────┐
│  ANNOTATION LAYER 1: General-Purpose        │
│  annotation_service.py (634L)               │
│  SQLite-backed, 10 types, 3 layers          │
│  CRUD + search + supersession versioning    │
│  Targets: belief, template, answer, theory  │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│  ANNOTATION LAYER 2: CVA-Specific           │
│  cva_annotation_service.py (283L)           │
│  JSON file-backed, auto-detect patterns     │
│  Types: modality, stimulus, molecule links  │
│  cva_annotations.py (238L) = data models    │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│  ANNOTATION LAYER 3: Extended A9-A18        │
│  extended_annotations.py (434L)             │
│  Data models only (no service class)        │
│  Types: surprise, design implication,       │
│  dispute, analogy, replication, effect,     │
│  cross-domain, history, hook, unanswered    │
└─────────────────────────────────────────────┘
```

### The Problem

These three layers are **not unified**:
- Layer 1 uses SQLite (`web_persistence_v2.db`)
- Layer 2 uses JSON files (`data/annotations/`)
- Layer 3 has data models but **no persistence service at all**
- No single API to ask "what annotations exist for belief X?"
- No annotation feeds back into QA, AESHI, or entrenchment

### Annotation Types Inventory

| ID | Type | Layer | Persistence | QA consumes? | AESHI? |
|----|------|-------|-------------|-------------|--------|
| A1 | CALIBRATION_NOTE | L1 | ✅ SQLite | ❌ | ❌ |
| A2 | SENSITIVITY_FLAG | L1 | ✅ SQLite | ❌ | ❌ |
| A3 | EVIDENCE_OVERRIDE | L1 | ✅ SQLite | ❌ | ❌ |
| A4 | PROVENANCE_PATCH | L1 | ✅ SQLite | ❌ | ❌ |
| A5 | CROSS_REFERENCE | L1 | ✅ SQLite | ❌ | ❌ |
| A6 | MOLECULE_LINK | L1 | ✅ SQLite | ⚠️ CVA only | ❌ |
| A7 | CLINICAL_CAUTION | L1 | ✅ SQLite | ❌ | ❌ |
| A8 | OPEN_QUESTION | L1 | ✅ SQLite | ✅ Gap pred | ❌ |
| CVA | measurement_modality | L2 | JSON files | ❌ | ❌ |
| CVA | stimulus_description | L2 | JSON files | ❌ | ❌ |
| CVA | molecule_t15_link | L2 | JSON files | ❌ | ❌ |
| A9 | surprise_flag | L3 | **None** | ❌ | ❌ |
| A10 | design_implication | L3 | **None** | ❌ | ❌ |
| A11 | dispute | L3 | **None** | ❌ | ❌ |
| A12 | analogical_bridge | L3 | **None** | ❌ | ❌ |
| A13 | replication_status | L3 | **None** | ❌ | ❌ |
| A14 | effect_magnitude | L3 | **None** | ❌ | ❌ |
| A15 | cross_domain | L3 | **None** | ❌ | ❌ |
| A16 | historical_context | L3 | **None** | ❌ | ❌ |
| A17 | narrative_hook | L3 | **None** | ❌ | ❌ |
| A18 | unanswered_question | L3 | **None** | ❌ | ❌ |

### Annotation System Success Conditions

| ID | Condition | Threshold | Current |
|----|-----------|-----------|---------|
| **AN-SC-01** | Single query API returns all annotation types for any target | 100% types accessible | ❌ |
| **AN-SC-02** | All 3 layers persist to same backing store | 100% in SQLite | ❌ (only L1) |
| **AN-SC-03** | A9-A18 data models have persistence service | 100% | ❌ |
| **AN-SC-04** | Annotation count per belief > 0 for >50% of beliefs | >50% | ❌ (unknown) |
| **AN-SC-05** | SENSITIVITY_FLAG consumed by template QA | 100% | ❌ |
| **AN-SC-06** | OPEN_QUESTION consumed by gap predictor | 100% | ✅ Done |
| **AN-SC-07** | SEARCH_PROMPT consumed by VOI search | 100% | ❌ |
| **AN-SC-08** | Annotations influence belief entrenchment | Formula defined | ❌ |
| **AN-SC-09** | Annotation health → AESHI component | Score defined | ❌ |
| **AN-SC-10** | Auto-annotation runs on all extractions | >90% coverage | ⚠️ (CVA only, 116/166) |
| **AN-SC-11** | Annotation supersession works end-to-end | Test passes | ✅ (L1 only) |
| **AN-SC-12** | Full-text search across annotations | Returns results | ✅ (L1 only) |

### Annotation System Remaining Work

| Priority | What | Effort |
|----------|------|--------|
| **P1** | Unify L2+L3 into L1's SQLite backing (THREE-PHASE — see below) | ~4 hrs |
| **P1** | Single `get_all_annotations(target_id)` API | ~1 hr |
| **P1** | Persist A9-A18 to SQLite via AnnotationService | ~2 hrs |
| **P2** | Wire annotations → AESHI component | ~1 hr |
| **P2** | Wire SENSITIVITY_FLAG → template QA | ~1 hr |
| **P2** | Wire SEARCH_PROMPT → VOI search | ~1 hr |
| **P3** | Auto-annotate pipeline for A9-A14 on all beliefs | ~2 hrs |
| **P3** | Annotation → entrenchment formula | ~2 hrs |

> [CW] THREE-PHASE ANNOTATION MIGRATION (not big-bang):
>
> **Phase α (Additive)**: Add L2 and L3 annotation types to L1's SQLite schema. Write new persistence methods in `annotation_service.py` for all 18+ types. Do NOT touch L2's JSON files or L2/L3 code yet. At the end of this phase, L1 can store everything but L2/L3 still work as before. ~2 hrs.
>
> **Phase β (Switch Loader)**: Change all code that READS annotations to use L1's unified `get_all_annotations()` API. Backfill: run a one-time migration script that reads all existing L2 JSON files and L3 in-memory annotations and writes them to SQLite. Verify parity. ~1.5 hrs.
>
> **Phase γ (Deprecate)**: Once L1 is the single source of truth and all consumers read from it, deprecate L2's JSON file writing (keep read-only for rollback safety). Mark L3 data model files as "persistence via L1". Remove dead code paths. ~0.5 hrs.
>
> Why three phases: If you do a big-bang migration and something goes wrong with 4,888 beliefs × multiple annotation types, you can't easily revert. The additive-first approach means L2 JSON files remain the source of truth until Phase β explicitly switches over, giving you a rollback path at every stage.

---

## Part 3: Joint Sprint Design

> [CW] **SPRINT ORDER FLIPPED.** AG had QA wiring first (Sprint A) then annotation unification (Sprint B). I'm reversing this. Rationale:
>
> The system probe (Session 21) revealed that most QA components exist but are **advisory, not blocking**. The deeper problem is that QA operates on **fragmented data** — three annotation layers, inconsistent backing stores, no unified query API. Wiring QA subsystems to the nightly pipeline while annotations are still split across SQLite/JSON/nothing means the QA checks will be shallow: they'll check what they can see, miss what's in the other stores, and produce a false sense of coverage.
>
> Unify the data layer first, THEN wire QA to the unified layer. This also means the QA wiring work (Sprint B) gets to target a single, clean annotation API rather than dealing with three different access patterns.

### Sprint A: Annotation Unification (est. 5 hrs) [CW: was Sprint B]

> [CW] This is the foundation. Everything else builds on having a unified annotation layer.

**Phase α — Additive (2 hrs)**:
1. Add L2 annotation types (measurement_modality, stimulus_description, molecule_t15_link) to L1's SQLite schema
2. Add L3 annotation types (A9-A18) to L1's SQLite schema
3. Write persistence methods in `annotation_service.py` for all new types
4. Tests: each new type round-trips through SQLite

**Phase β — Switch Loader (2 hrs)**:
1. Implement `get_all_annotations(target_id)` unified API
2. Write migration script: read all L2 JSON files → write to SQLite
3. Backfill any L3 annotations that were generated but not persisted
4. Switch all annotation consumers to use unified API
5. Verify: annotation count per belief matches across old and new paths

**Phase γ — Deprecate (1 hr)**:
1. Mark L2 JSON writing as deprecated (keep read-only)
2. Wire SENSITIVITY_FLAG → template QA (now possible via unified API)
3. Wire SEARCH_PROMPT → VOI search (now possible via unified API)
4. Annotation health → AESHI component

### Sprint B: QA Wiring (est. 4 hrs) [CW: was Sprint A]

> [CW] Now that annotation layer is unified, QA components can query a single API. This makes the wiring cleaner and the checks more comprehensive.

1. **Nightly ω computation on all beliefs** — Wire `warrant_strength.py`'s `compute_warrant_strength()` into `nightly_integration_pipeline.py`. For each belief, compute ω using the finding's extracted metadata (design type, sample size, p_lab, confounds). Store result in `beliefs` table alongside existing credence. ~2 hrs.
   > [CW] CRITICAL: Use `warrant_strength.py` (implements §48.3B formula: ω = ω_base × ω_conf × ω_rep × ω_meta, 62 passing tests), NOT `warrant_service.py` (legacy, different formula). The R6 dual-credence transition in `extraction_to_web.py` already uses `warrant_strength.py` — nightly should match.
2. **Source Quality → ω_source component** — Add `ω_source` multiplier to `warrant_strength.py` that calls `source_quality.py`. SQ indicators (pre-registration, blinding, independence, sample adequacy) map to a [0.7, 1.1] range multiplier. Apply as 5th factor in ω formula. ~2 hrs.
   > [CW] This is the correct integration point for SQ. NOT "SQ → Credence" (which would bypass the warrant architecture). The ω formula already has the right structure — SQ is just another epistemic dimension that modulates evidence strength.
3. **VOI count → AESHI component** — ~30 min
4. **`EPISTEMIC_PRINCIPLES.md`** — Document already exists conceptually in `docs/EPISTEMIC_PRINCIPLES.md` (10 principles from Pollock, Haack, Mayo, Cartwright, Pearl, Simon, Thagard, Longino). Write the formal version referencing how each principle maps to extraction fields and QA checks. ~1 hr.

### Sprint C: Integration + Verification (est. 2 hrs)

1. Provenance JustificationStatus → AESHI component
2. Run 5 real beliefs through full pipeline trace
3. Verify annotation queries return all types for test beliefs
4. Run example QA queries
5. **Compute ω for 100 sample beliefs, compare to legacy credence** — verify the R6 dual-credence transition shows reasonable correlation (r > 0.5) and meaningful divergences where expected

### Sprint D: Ruthless V8 (after Sprints A-C)

See Part 4.

---

## Part 4: Ruthless V8 — Amped-Up Audit

### Panel Composition

> [CW] Modified panel. Changes:
> - **Kept**: Graph Theorist, Bayesian Network Expert, Phil of Science (these are essential)
> - **Replaced "Distributed Systems Engineer"** with **Measurement & Psychometrics Specialist** — the system's core challenge is measurement validity (are we extracting the right constructs? are TEA scores calibrated? are ω components weighted correctly?), not distributed systems engineering. The system runs on one machine.
> - **Replaced "Database/IR Specialist"** with **User Experience / Design Practitioner** — the ultimate consumer of ATLAS is an architect or designer asking "should I use natural light in this space?" The system needs a voice asking "can a practitioner actually USE this output?" This also tests the query engine and answer generation quality.
> - **Added to Phil of Science brief**: Must engage with the warrant strength formula (§48.3B), the credence projection formula, and the epistemic principles document — not just Quinean holism in the abstract.

| Panelist | Focus |
|----------|-------|
| **Graph Theorist** | Belief graph: diameter, clustering coefficient, degree distribution, betweenness centrality, community structure, connected components |
| **Measurement & Psychometrics Specialist** | TEA score calibration, ω component weights, extraction field validity, inter-rater reliability of automated coding, construct validity of molecules [CW: replaces Distributed Systems Engineer] |
| **User Experience / Design Practitioner** | Can a designer get useful answers? Query engine UX, answer quality, evidence trace readability, practical actionability of recommendations [CW: replaces Database/IR Specialist] |
| **Bayesian Network Expert** | CPD correctness, d-separation, interventional reasoning, BN↔EN consistency |
| **Phil of Science** | Quinean holism, warrant strength formula (§48.3B), credence projection (§48), entrenchment computation, foundherentism vs coherentism, epistemic principles compliance |

### New Graph Theory Metrics

| Metric | Healthy Range | What bad values mean |
|--------|--------------|---------------------|
| Graph diameter | <10 | Isolated clusters, no global coherence |
| Clustering coefficient | >0.1 | Beliefs don't form local clusters |
| Degree distribution | Power-law (γ ≈ 2-3) | Random graph = no structure |
| Betweenness centrality top-10 | Named entities | Critical bridge beliefs to protect |
| Connected components | 1 giant + isolates <5% | Fragmented web |
| Average path length | <6 | Small-world property |

### Audit Scenarios

1. **New user**: Search for "how does ceiling height affect creativity?" → full pipeline trace
2. **Theory conflict**: Two theories predict opposite effects → how does the system handle it?
3. **Paper retraction**: Rollback a high-influence paper → cascading effects
4. **Gap discovery**: What does the system think it doesn't know yet?
5. **Design brief**: "Design a school that maximizes attention restoration" → can the system generate evidence-based recommendations?

> [CW] Add scenario 6:
> 6. **Warrant stress test**: Pick 3 beliefs where ω-derived credence diverges most from legacy credence (R6 dual-credence). Trace why. Is the warrant formula revealing real epistemic problems, or is it miscalibrated?

### Pre-Ruthless Checklist

- [ ] Sprints A-C complete
- [ ] All 22 QA SCs passing (or documented exceptions)
- [ ] All 12 Annotation SCs passing (or documented exceptions)
- [ ] 5 example queries tested and returning sensible results
- [ ] Graph metrics computed and within healthy ranges
- [ ] Theory taxonomy JSON files updated to use humanly meaningful hyphenated names (NOT 2-letter abbreviations)

---

## Part 5: Naming Convention Requirement [CW: NEW SECTION]

> [CW] Adding this because AG's existing `schemas/theory/` files still use 2-letter abbreviations (PP, SN, DP, etc.) which David has explicitly rejected. This needs to be fixed in the same sprint window.

**Rule**: All theory identifiers in code, data files, and documentation must use humanly meaningful hyphenated terms:

| OLD (forbidden) | NEW (required) |
|-----------------|----------------|
| PP | predictive-processing |
| SN | spatial-navigation |
| DP | dual-process-evaluation |
| DT | default-mode-dynamics |
| NM | neuromodulatory-systems |
| IC | interoceptive-constructionist-affect |
| MS | memory-systems |
| EC | embodied-cognition |
| CB | chronobiological-regulation |
| MSI | multisensory-integration |
| ART | attention-restoration-theory |
| SRT | stress-recovery-theory |

**Where this applies immediately**:
- `schemas/theory/tier1_frameworks.json` — primary IDs must be hyphenated names
- `schemas/theory/tier1_5_domain_theories.json` — same
- `schemas/theory/molecule_taxonomy.json` — any theory references
- `finding_template_relevance.py` — `T1_FRAMEWORK_IDS` must use new names
- Any new code written in Sprints A-D

**Backward compatibility**: Keep abbreviations as `aliases[]` in the JSON files and in `warrant_strength.py`'s `_LEGACY_KEY_MAP`. Never use abbreviations as primary identifiers.

The canonical mapping lives in `data/theories/tea_scores.json` (v2.0.0, 24 entries). All other files should reference this as the source of truth for theory naming.

---

## Verification Plan

### Automated Tests
```bash
pytest tests/test_success_conditions.py -v
pytest tests/test_warrant_strength.py -v   # [CW: added — 62 tests for ω]
python3 scripts/compute_system_health.py --skip-gates
python3 scripts/run_reflexes.py --all
```

### Manual Verification
1. Query: "What's surprising about biophilia in dense vegetation?"
2. Query: "How strong is the evidence for daylight → cortisol reduction?"
3. Trace belief `pdf:doi:10.xxx:TBL-C025` through all systems
4. Verify annotation count > 0 for >50% of beliefs
5. Run graph metrics on belief graph
6. **Compute ω for 10 beliefs, verify each component (ω_base, ω_conf, ω_rep, ω_meta, ω_source) is reasonable** [CW: added]
7. **Verify no 2-letter abbreviations appear as primary IDs in any data file** [CW: added]
