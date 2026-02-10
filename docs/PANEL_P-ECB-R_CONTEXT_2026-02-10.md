# Panel P-ECB-R: Epistemic-Causal Bridge Repair

**Date**: 2026-02-10
**Panel ID**: P-ECB-R (Epistemic-Causal Bridge Repair)
**Owner Decision**: Option B confirmed — Counterfactual queries and van Fraassen contrast classes ARE core

---

## Purpose

This document provides the expert panel with complete context to make informed recommendations for repairing the integration between the epistemic layer (Web of Belief) and the causal layer (Bayesian Network/Counterfactuals).

---

## Panelists

| Expert | Domain | Key Contribution Expected |
|--------|--------|--------------------------|
| **Susan Haack** | Foundherentism | How should her framework constrain the integration? |
| **Judea Pearl** | Causal Inference | Proper relationship between belief and causal structure |
| **Bas van Fraassen** | Scientific Explanation | How contrast classes flow through both layers |
| **Herbert Simon** | System Design | Minimal viable integration |
| **Nancy Cartwright** | Philosophy of Science | How capacities and scope affect causal claims |

---

## Part 1: The Foundherentist Architecture (V23.0.0)

### What is Foundherentism?

Per Haack (1993), foundherentism occupies a middle ground:
- **Not pure coherentism**: Some beliefs have a quasi-foundational role
- **Not pure foundationalism**: No belief is absolutely unrevisable
- Experience provides **ampliative warrant**, not bedrock

### V23.0.0 Implementation

On 2026-02-08, we made entrenchment **emergent** rather than settable. This fixed a bug where settable entrenchment created "foundationalism through the back door."

**The Thagard Formula** (implemented in `web_of_belief.py:1212`):

```python
entrenchment = 0.4 * connectivity + 0.3 * level_weight + 0.3 * coherence_contrib
```

Where:
- **connectivity** = min(1.0, constraint_count / 10) — How many other beliefs constrain this one
- **level_weight** = soft hierarchy based on epistemic level:
  - THEORETICAL: 0.8
  - INTERMEDIATE: 0.5
  - EMPIRICAL: 0.3
  - OBSERVATIONAL: 0.2
- **coherence_contrib** = simplified proxy: (credence + status_weight) / 2

**Why This Matters for the Bridge**:
- Theoretical beliefs naturally become more entrenched (level_weight = 0.8)
- But this is *emergent*, not *imposed* — a highly connected observation can outrank an isolated theory
- The causal model should respect this: equations derived from entrenched beliefs should be more robust

### Panel Consultation That Led to V23.0.0

The entrenchment panel (2026-02-08) included:
- Quine: "Settable entrenchment = foundationalism through the back door"
- Haack: "Be explicit about philosophy—either emergent OR explicit foundherentism"
- Thagard: "Compute from connectivity + level + coherence"
- Simon: "Lazy computation with caching for performance"
- Cartwright: "Allow override for special cases"

See: `docs/PANEL_CONSULTATION_ENTRENCHMENT_2026-02-08.md`

---

## Part 2: Current State of the Epistemic-Causal Bridge

### The Problem: Two Distinct Layers That Should Communicate

**Epistemic Layer** (Web of Belief):
- Answers: "What do we believe? With what confidence?"
- Contains: Beliefs, credences, constraints, entrenchment (emergent)
- Implements: Coherence-seeking, reflective equilibrium

**Causal Layer** (BN/Counterfactuals):
- Answers: "What causes what? What would happen if...?"
- Should contain: DAGs, structural equations, do-calculus
- Should implement: Counterfactual reasoning, intervention effects

### The Integration Vision

The bridge should enable:

1. **Epistemic → Causal**: High-credence beliefs become structural equations; constraints become DAG edges
2. **Causal → Epistemic**: Counterfactual results update the web (feedback loop)
3. **Contrast Classes**: Van Fraassen's "compared to what?" made explicit in both layers

### What Currently Exists

**File**: `src/services/epistemic_causal_bridge.py` (~2400 lines)

**Classes Defined**:
- `EpistemicCausalBridge` — Main integration class (line 857)
- `MultiTheoryModel` — Collection of per-theory causal models
- `TheoryRelativeModel` — DAG + equations for one theory
- `StructuralEquation` — Y = f(parents) with credence and entrenchment
- `ContrastClass` — Van Fraassen contrast specification
- `PopulationContext` — Baseline levels and cultural meanings
- `CounterfactualQuery` — Intervention + outcome + contrast class
- `QuineanCounterfactualResult` — Full result with robustness, coherence, scope assessments

**Key Methods**:

```python
class EpistemicCausalBridge:
    def __init__(self, web: 'WebOfBelief'):
        self.web = web

    def build_causal_models(self, credence_threshold=0.5) -> MultiTheoryModel:
        """Extract causal models from the web. Per-theory DAGs."""

    def counterfactual(self, intervention, outcome, contrast_class=None) -> QuineanCounterfactualResult:
        """
        Compute counterfactual with full Quinean analysis:
        1. Theory-relative counterfactuals
        2. Weighted integration
        3. Robustness analysis
        4. Coherence check
        5. Scope assessment
        6. Contrast transfer (van Fraassen)
        """
```

### Critical Issues Found

| Issue | Description | Severity |
|-------|-------------|----------|
| **Two implementations** | Repo file differs from external research file that tests use | HIGH |
| **Duplicate classes** | Bridge defines `Belief`, `Credence`, etc. that duplicate `web_of_belief.py` | MEDIUM |
| **Not used in pipeline** | `app/tasks/pipeline.py` makes zero bridge calls | HIGH |
| **No feedback loop** | Counterfactual results don't update the web | MEDIUM |
| **Tests broken** | Tests import from external path, not repo | HIGH |

---

## Part 3: What the Bridge Does (In Detail)

### 3.1 Model Construction

The bridge extracts causal structure from the web:

```python
def _get_theory_beliefs(self, theory_id, credence_threshold):
    """Get beliefs supporting a theory above threshold."""
    # Filters: theory membership, credence, level (theoretical/intermediate only)
    # P-EC-R9: Also checks enabling conditions (Cartwright)

def _build_theory_model(self, theory_id, beliefs) -> TheoryRelativeModel:
    """Build DAG from theory-specific beliefs."""
    variables = self._extract_variables(beliefs)  # From tags like "outcome:stress"
    edges = self._extract_edges(beliefs)          # From constraints (EXPLAINS, SUPPORTS)
    equations = self._build_equations(beliefs, variables, edges)
    return TheoryRelativeModel(...)
```

**Key design choice**: Variables are extracted from belief tags (e.g., `outcome:stress`, `exposure:nature`). Edges come from web constraints.

### 3.2 Counterfactual Computation

The `counterfactual()` method does 7 things:

1. **Theory-relative computation**: Run counterfactual in each theory's model
2. **Weighted integration**: Combine by theory credence
3. **Robustness analysis**: How much would web need to change to flip the result?
4. **Coherence check**: Does this counterfactual violate any constraints?
5. **Scope assessment**: Is the target population/setting within evidence?
6. **Contrast transfer**: Van Fraassen — is the contrast class appropriate?
7. **Apply adjustments**: Penalties for out-of-scope, contrast mismatch

### 3.3 Van Fraassen Contrast Classes

The bridge implements:

```python
@dataclass
class ContrastClass:
    focal: ConditionSpec            # The intervention (e.g., "nature exposure")
    contrasts: List[ConditionSpec]  # What it's compared to (e.g., "urban exposure", "no exposure")
    contrast_type: ContrastType     # NULL, ALTERNATIVE, GRADIENT, FACTORIAL, POPULATION
    population_context: PopulationContext  # Baseline levels for this population
```

**The insight**: "Nature exposure reduces stress" means different things depending on:
- Compared to what? (No exposure? Urban exposure? Virtual nature?)
- For whom? (Urban office workers? Rural residents with high baseline nature?)
- Where? (Lab study? Field setting?)

The bridge tries to track all of this.

### 3.4 The Missing Feedback Loop

Currently the bridge is **one-directional**:

```
Web of Belief → [Bridge] → Counterfactual Results
```

What's missing:

```
Web of Belief ↔ [Bridge] ↔ Counterfactual Results
                  ↑
                  └── Update credences based on counterfactual coherence
```

Per Quine: If a counterfactual reveals tension, *some* belief in the web should be revised.

---

## Part 4: The Duplicate Class Problem

The bridge file defines classes that duplicate `web_of_belief.py`:

| Class | In `epistemic_causal_bridge.py` | In `web_of_belief.py` | Used? |
|-------|--------------------------------|----------------------|-------|
| `EpistemicLevel` | line 46 | line 87 | NO (bridge uses web's) |
| `BeliefStatus` | line 54 | line 100 | NO |
| `ConstraintType` | line 63 | line 109 | Partially |
| `Credence` | line 110 | line 363 | NO |
| `Belief` | line 150 | line 451 | NO |

**The bridge accesses `self.web.beliefs` which are `web_of_belief.Belief` objects**, not its own `Belief` class.

This is dead code that should be removed.

---

## Part 5: Questions for the Panel

### Q1: For Susan Haack — Foundherentist Integration

The current architecture has:
- Epistemic layer: Emergent entrenchment (foundherentist)
- Causal layer: Theory-relative structural equations weighted by credence

**Question**: How should the "quasi-foundational" role of well-entrenched theoretical beliefs manifest in the causal layer? Should equations derived from THEORETICAL beliefs be treated differently than those from INTERMEDIATE beliefs?

### Q2: For Judea Pearl — Structural Equations from Beliefs

The bridge builds structural equations from beliefs:
```python
equations[var] = StructuralEquation(
    outcome_var=var,
    parent_vars=parents,
    functional_form="linear",  # Default
    parameters={f"beta_{p}": 0.5 for p in parents},  # Default
    credence=avg_credence_of_supporting_beliefs
)
```

**Question**: Is this the right relationship between beliefs and equations? Should equation parameters be estimated differently? How should we handle conflicting beliefs about the same causal relationship?

### Q3: For Bas van Fraassen — Contrast Class Flow

The bridge extracts contrast classes from beliefs and checks transfer to queries.

**Question**: How should contrast classes propagate through counterfactual inference? When a query specifies a contrast class that differs from the evidence base, what's the right adjustment?

### Q4: For Herbert Simon — Simplification

The current bridge is ~2400 lines with elaborate data structures.

**Question**: What's the minimal viable integration? Can we get 80% of the value with 20% of the code?

### Q5: For Nancy Cartwright — Capacities and Enabling Conditions

The bridge checks enabling conditions (per P-EC-R9):
```python
def _check_enabling_conditions(self, belief) -> bool:
    """Beliefs with unmet enabling conditions shouldn't contribute to counterfactuals."""
```

**Question**: How should capacities (your concept) interact with the causal model? When a mechanism belief specifies that "nature reduces stress *if exposure > 30 min*", how should this condition propagate?

### Q6: For All — The Feedback Loop

Currently missing: Counterfactual results don't update the web.

**Question**: How should the causal layer feed back to the epistemic layer? If a counterfactual reveals an incoherence, which belief should be revised?

---

## Part 6: Constraints on the Repair

1. **Foundherentism must be preserved**: The V23.0.0 emergent entrenchment formula should inform causal model confidence
2. **Van Fraassen contrast classes are core**: Not optional, must flow through both layers
3. **The pipeline should actually use it**: The repair must include wiring to `pipeline.py`
4. **Simplicity preferred**: Per Simon, reduce complexity where possible
5. **One source of truth**: Consolidate the two implementations
6. **Feedback loop required**: Causal results should update the web

---

## Part 7: Proposed Architecture (For Panel Critique)

```
                    ┌─────────────────────────────────────────┐
                    │            Web of Belief                │
                    │  (Foundherentist: emergent entrenchment)│
                    │                                         │
                    │  Beliefs, Credences, Constraints        │
                    │  Scope, Enabling Conditions             │
                    │  Contrast Classes (attached to beliefs) │
                    └─────────────────────────────────────────┘
                                      │
                                      ▼ (1) Extract
                    ┌─────────────────────────────────────────┐
                    │        Epistemic-Causal Bridge          │
                    │                                         │
                    │  - Build per-theory causal models       │
                    │  - Equations weighted by entrenchment   │
                    │  - Contrast class checking              │
                    │  - Scope/enabling condition checking    │
                    └─────────────────────────────────────────┘
                                      │
                                      ▼ (2) Compute
                    ┌─────────────────────────────────────────┐
                    │         Causal Layer (BN)               │
                    │                                         │
                    │  - Per-theory structural equations      │
                    │  - Counterfactual computation           │
                    │  - Contrast-relative estimates          │
                    └─────────────────────────────────────────┘
                                      │
                                      ▼ (3) Return
                    ┌─────────────────────────────────────────┐
                    │     QuineanCounterfactualResult         │
                    │                                         │
                    │  - Point estimate + CI                  │
                    │  - Robustness, Coherence, Scope scores  │
                    │  - Warnings about contrast mismatch     │
                    │  - Suggestions for web updates          │
                    └─────────────────────────────────────────┘
                                      │
                                      ▼ (4) Feedback
                    ┌─────────────────────────────────────────┐
                    │        Update Web of Belief             │
                    │                                         │
                    │  - Adjust credences if incoherence      │
                    │  - Add new constraints discovered       │
                    │  - Mark beliefs as anomalous if needed  │
                    └─────────────────────────────────────────┘
```

---

## Requested Output from Panel

1. **Architectural recommendations**: How should the two layers communicate?
2. **Simplification suggestions**: What can be cut from the 2400-line bridge?
3. **Feedback loop design**: How should causal results update the web?
4. **Van Fraassen integration**: How should contrast classes flow through?
5. **Entrenchment-to-equation mapping**: How should emergent entrenchment affect causal confidence?
6. **Specific repair steps**: Ordered list of what to fix

---

*Context document complete. Ready for panel consultation.*
