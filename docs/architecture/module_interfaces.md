# Module Interface Documentation

## ARCH-5f: Clear Module Interfaces for Article Eater

*Created: 2026-02-22 | Task: ARCH-5f*

---

## Module Architecture Overview

```
src/services/
├── web_of_belief.py              # Master Belief class + WebOfBelief
├── web_of_belief_components/     # ARCH-5d: Extracted enums & data structures
│   ├── __init__.py               # Compatibility re-exports
│   ├── enums.py                  # EpistemicLevel, StudyDesign, EvidenceQuality, etc.
│   ├── graph_models.py           # Constraint, TheoryWorld, UncertainQuantity
│   └── scope_models.py           # ScopeConditions, EnablingConditions, CredenceHistoryEntry
│
├── web_of_belief_modules/        # ARCH-5d: Extracted computation modules
│   ├── __init__.py               # Compatibility re-exports
│   ├── analysis_ops.py           # belief_value, centrality, sensitivity
│   ├── coherence.py              # Coherence computation
│   ├── entrenchment.py           # Thagard entrenchment formula
│   ├── independence.py           # ARCH-3b: Lab×method×population diversity
│   ├── severity.py               # ARCH-6b: Mayo severity scoring
│   ├── mutations.py              # Belief/constraint mutation operations
│   ├── engines.py                # Computation engines
│   ├── evidence_updates.py       # Evidence processing
│   ├── experiments.py            # Experimental design
│   ├── reporting.py              # Web reporting
│   ├── snapshots.py              # Web state snapshots
│   ├── theory_worlds.py          # Theory world management
│   ├── value_metrics.py          # Epistemic value computation
│   └── web_state.py              # Mutable web state
│
├── epistemic_causal_bridge.py    # Main EpistemicCausalBridge class (Part 10)
├── ecb_modules/                  # ARCH-5e: Extracted ECB data structures
│   ├── __init__.py               # Compatibility re-exports (all 30 types)
│   ├── contrast_classes.py       # Van Fraassen: ContrastClass, PopulationContext, etc.
│   ├── causal_models.py          # Pearlian: Variable, StructuralEquation, etc.
│   └── counterfactuals.py        # Results: CounterfactualQuery, EpistemicGap, etc.
│
├── scalable_coherence.py         # O(n log n) hierarchical coherence
├── refined_epistemic.py          # Bovens-Hartmann coherence methods
└── epistemic_causal_bridge.py    # EpistemicCausalBridge + deprecated stubs
```

---

## Module Interfaces

### 1. `web_of_belief_components` — Enums & Data Structures

**Purpose**: Type definitions used across the epistemic layer.

| Export | Type | Description |
|--------|------|-------------|
| `EpistemicLevel` | Enum | THEORETICAL → OBSERVATIONAL |
| `BeliefStatus` | Enum | STUB → ENTRENCHED |
| `StudyDesign` | Enum | RCT → UNKNOWN (ARCH-6a) |
| `EvidenceQuality` | Enum | SEVERELY_TESTED → UNTESTED (ARCH-6d) |
| `Constraint` | Dataclass | Edge between beliefs |
| `ScopeConditions` | Dataclass | Cartwright scope |
| `EnablingConditions` | Dataclass | Activation requirements |

**Import pattern**: `from src.services.web_of_belief_components import StudyDesign`

### 2. `web_of_belief_modules` — Computation Modules

**Purpose**: Extracted computations that operate on WebOfBelief state.

| Module | Key Function | Input → Output |
|--------|-------------|----------------|
| `analysis_ops.py` | `belief_value()` | (web, belief_id) → float |
| `coherence.py` | `compute_coherence()` | (beliefs, constraints) → float |
| `entrenchment.py` | `compute_entrenchment()` | (belief, web) → float |
| `independence.py` | `compute_independence_score()` | records → dict |
| `severity.py` | `compute_severity_score()` | (credence, metrics) → float |

**Import pattern**: `from src.services.web_of_belief_modules import compute_severity_score`

### 3. `ecb_modules` — Bridge Data Structures

**Purpose**: Data types for the epistemic-causal bridge layer.

#### `contrast_classes.py` — Van Fraassen Layer
| Type | Description |
|------|-------------|
| `ContrastClass` | What question does a finding answer? |
| `PopulationContext` | Population + baselines + cultural meanings |
| `TemporalSpec` | Structured temporal conditions (PA-6) |
| `TransportabilityAssessment` | Pearl/Bareinboim transfer assessment |

#### `causal_models.py` — Pearlian Layer
| Type | Description |
|------|-------------|
| `Variable` | Variable in causal model |
| `StructuralEquation` | Y = f(parents, U) with enabling conditions |
| `TheoryRelativeModel` | Causal model relative to one theory |
| `MultiTheoryModel` | Collection of theory-relative models |

#### `counterfactuals.py` — Results Layer
| Type | Description |
|------|-------------|
| `CounterfactualQuery` | "What if we set X?" query |
| `QuineanCounterfactualResult` | Full result with Quinean annotations |
| `EpistemicGap` | Identified gap for VOI routing |
| `ExcludedBelief` | Why a belief was excluded from model |

**Import pattern**: `from src.services.ecb_modules import ContrastClass, StructuralEquation`

---

## Dependency Direction

```
web_of_belief_components  ←  web_of_belief_modules  ←  web_of_belief.py
                                                              ↓
ecb_modules (data types)  ←──────────────  epistemic_causal_bridge.py
                                                              ↓
                                           scalable_coherence.py
```

**Rule**: Data types flow left/up. Computation flows right/down. No circular dependencies.
