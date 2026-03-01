# OC-8: Outcome Vocabulary Gap Analysis

**Date**: 2026-02-28
**Task**: Check older repos for richer vocab not migrated
**Current vocab**: 103 terms across 8 domains (v2.0.0)

---

## Executive Summary

Three major vocabulary sources exist outside `outcome_vocab.json` that contain terms not yet migrated:

1. **`outcome_taxonomy.py`** (1,608 lines) — Defines 32 `arch.*` terms and 5 `art.*` (Attention Restoration Theory) terms. These represent two complete domain hierarchies developed during Sprint 4 that were never exported to the canonical JSON.

2. **`vocabulary_bridge.yaml`** — Uses an older naming scheme (`psych.*`, `natural.*`, `spatial.*`) with ~20 concepts, some unmapped to current IDs (e.g., `natural.views`, `natural.water`, `natural.plants.indoor`).

3. **`unresolved_outcomes.jsonl`** — 4,080 raw outcome terms extracted from papers, awaiting resolution. This is the PANEL-1 target.

---

## Gap 1: ARCH Domain (32 terms) — SCOPE QUESTION

`outcome_taxonomy.py` defines an `arch` domain hierarchy. However, **this raises a design question**: the current vocab describes *human responses* to built environments (outcomes = dependent variables). Many `arch.*` terms are *environmental input features* (independent variables), not responses:

### Clearly Environmental Inputs (NOT outcomes)
These belong in an environmental feature taxonomy, not outcome vocab:
- `arch.feature.ceiling_height`, `arch.feature.view_distance`, `arch.feature.window_ratio`
- `arch.feature.daylight_factor`, `arch.feature.green_ratio`

### Already Covered (different ID)
These exist under current IDs:
| arch.* term | Current vocab ID |
|------------|-----------------|
| `arch.percept.enclosure` | `env.enclosure` |
| `arch.percept.coherence` | `env.coherence` |
| `arch.percept.complexity` | `env.complexity` |
| `arch.response.place_attachment` | `affect.place_attachment` |
| `arch.response.restoration` | `affect.restorativeness` |
| `arch.config.prospect_refuge_balance` | `env.prospect_refuge` |
| `arch.wayfinding.*` | `behav.wayfinding` |
| `arch.environ.thermal` | `physio.thermal_comfort` |
| `arch.environ.acoustic` | `env.acoustic_quality` |

### Genuinely Missing (should migrate)
| Term | Suggested ID | Definition |
|------|-------------|-----------|
| `arch.percept.openness` | `env.openness` | Perceived spatial openness |
| `arch.percept.naturalness` | `env.naturalness` | Perceived naturalness of environment |
| `arch.percept.legibility` | `env.legibility` | Ease of understanding spatial organization (Lynch, 1960) |
| `arch.percept.aesthetic` | (overlap w/ `affect.aesthetic_pleasure`) | — |
| `arch.config.hazard` | `env.perceived_hazard` | Perceived danger features in environment |
| `arch.response.safety` | (overlap w/ `affect.safety_perception`) | — |
| `arch.response.calming` | (overlap w/ `affect.relaxation`) | — |
| `arch.response.arousing` | `physio.arousal` | Activation response to environment |
| `arch.response.control` | `env.perceived_control` | Sense of control over environmental conditions |
| `arch.environ.biophilic` | (overlap w/ `env.natural_features`) | — |
| `arch.environ.daylight` | (overlap w/ `env.lighting`) | — |

**Recommendation**: Migrate 5 genuinely new terms: `env.openness`, `env.naturalness`, `env.legibility`, `env.perceived_hazard`, `env.perceived_control`. Add `physio.arousal` (fundamental and missing). Skip the rest as duplicates.

---

## Gap 2: ART Domain (5 terms) — SHOULD MIGRATE

Kaplan's (1995) Attention Restoration Theory defines four constructs. Only `fascination` was migrated (as `affect.fascination`). The other three are well-established in environmental psychology:

| ART Construct | Definition | Status |
|--------------|-----------|--------|
| `art.fascination` | Effortless attention capture | ✅ Already in vocab as `affect.fascination` |
| `art.being_away` | Psychological distance from routine demands | ❌ MISSING |
| `art.extent` | Sense of being in a whole other world | ❌ MISSING |
| `art.compatibility` | Fit between environment and one's purposes | ❌ MISSING |

**Recommendation**: Add all three missing ART constructs under `affect.*` domain since they describe subjective environmental experience: `affect.being_away`, `affect.extent`, `affect.compatibility`.

---

## Gap 3: Vocabulary Bridge Unmapped Concepts

`vocabulary_bridge.yaml` has three concepts with no clear vocab mapping:

| Bridge concept | What it means | Recommendation |
|---------------|--------------|----------------|
| `natural.views` | Access to nature views | Subsume under `env.natural_features` (add cognate "nature views") |
| `natural.plants.indoor` | Indoor plant presence | Subsume under `env.natural_features` (add cognate "indoor plants") |
| `natural.water` | Water feature presence | Add `env.water_features` or subsume under `env.natural_features` |

**Recommendation**: Add cognates to `env.natural_features` rather than creating new terms. Water features are specific enough to warrant their own term: `env.water_features`.

---

## Gap 4: Missing Fundamental Constructs

Cross-referencing with standard environmental psychology literature, the following commonly measured constructs are absent:

| Construct | Suggested ID | Rationale |
|-----------|-------------|-----------|
| **Arousal** | `physio.arousal` | Russell's circumplex model; fundamental dimension alongside valence |
| **Preference** | `affect.preference` | Most common DV in environmental aesthetics (Kaplan & Kaplan, 1989) |
| **Valence** | `affect.valence` | Core affect dimension (Russell, 2003) |
| **Thermal sensation** | (extend `physio.thermal_comfort`) | Already covered; add operationalizations |
| **Glare** | `env.glare` | Common lighting DV in building science |

**Recommendation**: Add `physio.arousal`, `affect.preference`, `affect.valence`. These are among the most frequently measured outcomes in the built environment literature.

---

## Migration Plan

### Tier 1: Immediate (no ambiguity)
Add 9 terms to `outcome_vocab.json`:
1. `affect.being_away` — ART construct
2. `affect.extent` — ART construct
3. `affect.compatibility` — ART construct
4. `affect.preference` — Environmental preference
5. `affect.valence` — Core affect valence dimension
6. `env.legibility` — Spatial legibility (Lynch, 1960)
7. `env.naturalness` — Perceived naturalness
8. `env.perceived_control` — Environmental control
9. `physio.arousal` — Physiological/psychological activation

### Tier 2: Needs David's decision
- `env.openness` — Might overlap with `env.spaciousness` and `env.visual_access`
- `env.perceived_hazard` — Might overlap with `affect.safety_perception` (inverse)
- `env.water_features` — Specific enough for separate term?
- `env.glare` — Specific enough for separate term?

### Tier 3: PANEL-1 (4,080 unresolved terms)
Run the AI panel on the full unresolved queue to discover additional constructs.

---

## Files Referenced

| File | Location | Content |
|------|----------|---------|
| outcome_taxonomy.py | `src/services/outcome_taxonomy.py` | 1,608 lines, 67 classes, arch/art domains |
| vocabulary_bridge.yaml | `contracts/vocab/vocabulary_bridge.yaml` | Legacy naming scheme |
| outcome_resolver.py | `lib/outcome_resolver.py` | Resolution engine with fuzzy matching |
| unresolved_outcomes.jsonl | `data/unresolved_outcomes.jsonl` | 4,080 queued terms |
| tag_engine.py | `src/services/paper_integration/tag_engine.py` | Entity/topic tags (different function) |
| BN outcome_taxonomy.py | `../../BN_graphical/src/schemas/outcome_taxonomy.py` | Measurement structure enums |
