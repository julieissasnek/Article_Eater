# Epistemic Calculus Specification

**Date**: 2026-02-12
**Status**: DRAFT — Theoretical Foundation
**Task**: ARCH-4 (Formal Epistemic Calculus)

---

## Motivation

Pearl's do-calculus provides a formal system for causal inference:
- **Language**: do-operator, P(Y | do(X=x))
- **Rules**: Three inference rules based on graph structure
- **Completeness**: If an effect is identifiable, do-calculus derives it

The Article Eater epistemic layer currently has algorithms but no calculus:
- Entrenchment is computed (0.4 × connectivity + 0.3 × level + 0.3 × coherence)
- But there are no inference rules with provable properties
- No formal semantics for "justification" or "coherence"

**Goal**: Define a formal epistemic calculus using Spohn's Ranking Theory and Pollock's Defeasible Logic.

---

## Part 1: Ranking Theory (Spohn)

### Core Concepts

| Concept | Symbol | Meaning |
|---------|--------|---------|
| Ranking function | κ | Maps propositions to ordinal ranks (0, 1, 2, ..., ∞) |
| Rank of belief | κ(B) | How firmly B is believed; lower = more entrenched |
| Disbelief | κ(B) > 0 | B is disbelieved to degree κ(B) |
| Belief | κ(¬B) > 0 | B is believed (its negation is disbelieved) |
| Suspension | κ(B) = κ(¬B) = 0 | Neither B nor ¬B is believed |

### Key Insight

Current system uses **cardinal** entrenchment (0.0 to 1.0).
Spohn uses **ordinal** ranks (0, 1, 2, ...).

Ordinal is better because:
- No false precision (what does 0.73 vs 0.74 really mean?)
- Natural for "more/less entrenched" comparisons
- Formal revision rules are cleaner

### Spohn's Conditionalization Rule

When evidence E is learned with firmness n:

```
κ_new(B) = min(κ_old(B | E), κ_old(B | ¬E) + n)
```

Where conditional rank is:
```
κ(B | E) = κ(B ∧ E) - κ(E)
```

### Mapping to Article Eater

| Current System | Spohn Equivalent |
|----------------|------------------|
| `belief.credence.value` | Could derive from rank: credence = 1 / (1 + κ(¬B)) |
| `entrenchment` (0-1) | Replace with ordinal rank κ(B) |
| `Credence.update()` | Replace with Spohn conditionalization |
| `uncertainty` | Becomes spread: \|κ(B) - κ(¬B)\| |

---

## Part 2: Defeasible Logic (Pollock)

### Core Concepts

| Concept | Meaning |
|---------|---------|
| Prima facie reason | Evidence that supports conclusion unless defeated |
| Rebutting defeater | Contradicts the conclusion directly |
| Undercutting defeater | Attacks the inference link, not the conclusion |
| Warrant | A prima facie reason that survives all defeaters |

### Defeater Types in Article Eater

| Type | Example | Pollock Category |
|------|---------|------------------|
| Contradictory belief | "Daylight has no effect on mood" vs "Daylight improves mood" | Rebutting |
| Methodological critique | "That study was underpowered" | Undercutting |
| Scope limitation | "Only applies to office workers" | Undercutting |
| Replication failure | "Failed to replicate in 3 independent labs" | Rebutting |

### Inference Rules

**Rule 1: Prima Facie Support**
```
If belief A supports belief B (constraint type = SUPPORTS),
and A has rank κ(A) = r,
then B has prima facie rank κ(B) ≤ r + δ
where δ is the inference penalty (e.g., 1 for strong support, 2 for weak)
```

**Rule 2: Rebutting Defeat**
```
If belief D rebuts belief B (same domain, opposite conclusion),
and κ(D) < κ(B),
then B's effective rank increases: κ_eff(B) = κ(B) + (κ(B) - κ(D))
```

**Rule 3: Undercutting Defeat**
```
If belief U undercuts the inference from A to B,
and κ(U) < κ(A→B),
then the inference A→B is blocked,
and B loses support from A
```

**Rule 4: Warrant Propagation**
```
Belief B is warranted iff:
1. B has prima facie support from warranted beliefs, AND
2. No undefeated rebutters exist, AND
3. No undefeated undercutters block the supporting inferences
```

---

## Part 3: Formal Properties

### Invariants (for TLA+ specification)

**INV-1: Groundedness**
```
Every warranted belief is either:
- Observational (grounded in experience), OR
- Supported by warranted beliefs via undefeated inferences
```

**INV-2: Consistency**
```
For any belief B: NOT (warranted(B) AND warranted(¬B))
```

**INV-3: Rank Coherence**
```
If A supports B with penalty δ, and A is warranted:
κ(B) ≤ κ(A) + δ (unless defeated)
```

**INV-4: Defeat Asymmetry**
```
If D defeats B, then κ(D) < κ(B) (defeater is more entrenched)
```

### Correctness Criteria

The epistemic web is **correct** iff:
1. All invariants hold
2. Warranted beliefs form a coherent set (no cycles of mutual support without grounding)
3. Ranks respect the evidence (higher evidence = lower rank)

---

## Part 4: Implementation Roadmap

### Phase 1: Theoretical (ARCH-4a through ARCH-4d)

1. Read Spohn (2012) chapters 1-5 (ranking basics)
2. Read Pollock (1987) on defeasible reasoning
3. Write formal mapping document: current concepts → formal equivalents
4. Define the calculus precisely (language, rules, semantics)

### Phase 2: Ranking Implementation (ARCH-4e through ARCH-4h)

1. Add `rank: int` field to Belief (or compute from credence)
2. Implement Spohn conditionalization in `Credence.update()`
3. Modify `get_entrenchment()` to return ordinal rank
4. Write property-based tests for rank coherence

### Phase 3: Defeat Implementation (ARCH-4i through ARCH-4l)

1. Extend `ConstraintType` enum: REBUTS, UNDERCUTS
2. Modify `find_defeaters_for_belief()` to classify defeater type
3. Implement warrant computation (prima facie + defeat check)
4. Add `is_warranted()` method to WebOfBelief

### Phase 4: Verification (ARCH-4m through ARCH-4p)

1. Write TLA+ spec for core invariants
2. Use model checker to verify properties
3. Connect to causal layer: warranted beliefs license BN edges

---

## Part 5: Connection to Causal Layer

The epistemic calculus answers: **"What should we believe?"**
The causal calculus (do-calculus) answers: **"What happens if we intervene?"**

Bridge:
```
P(Y | do(X=x)) is trustworthy iff
  the BN edge X→Y is supported by warranted beliefs
  with rank κ(X→Y) ≤ threshold
```

This makes the epistemic-causal bridge formal:
- Epistemic layer provides confidence in structure
- Causal layer computes effects given structure
- Combined: confidence-weighted causal predictions

---

## References

1. Spohn, W. (2012). *The Laws of Belief: Ranking Theory and Its Philosophical Applications*. Oxford University Press.

2. Pollock, J. (1987). "Defeasible Reasoning." *Cognitive Science*, 11(4), 481-518.

3. Pollock, J. (1995). *Cognitive Carpentry: A Blueprint for How to Build a Person*. MIT Press.

4. Pearl, J. (2009). *Causality: Models, Reasoning, and Inference*. 2nd ed. Cambridge University Press.

5. Artemov, S. (2008). "The Logic of Justification." *Review of Symbolic Logic*, 1(4), 477-513.

---

## Next Steps

1. [ ] Professor Kirsh to review and approve theoretical direction
2. [ ] Obtain Spohn (2012) and Pollock (1987/1995) for detailed study
3. [ ] Begin ARCH-4a: Extract core formalism from Spohn
4. [ ] Schedule panel consultation with constructed Spohn/Pollock voices

---

*Draft specification. Subject to revision after theoretical study.*
