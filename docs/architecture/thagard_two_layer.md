# Thagard Two-Layer Architecture

## EC-1: Explanatory Coherence in Article Eater

*Created: 2026-02-22 | Task: EC-1 (Panel Recommendation)*

---

## Overview

Article Eater's epistemic engine implements a **two-layer coherence architecture** that separates the *explanatory* question ("how well do beliefs explain each other?") from the *positional* question ("how important is this belief in the web?"). This follows Thagard's insight that explanation and entrenchment are related but distinct epistemic virtues.

```
                    ┌─────────────────────────────┐
                    │      WebOfBelief            │
                    │      (Master State)         │
                    └──────────┬──────────────────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                                 ▼
    ┌──────────────────┐              ┌──────────────────┐
    │    LAYER 1:      │              │    LAYER 2:      │
    │    Explanatory   │              │    Positional    │
    │    Coherence     │              │    Value         │
    │                  │              │                  │
    │  scalable_       │              │  analysis_ops.   │
    │  coherence.py    │              │  belief_value()  │
    │  refined_        │              │  belief_         │
    │  epistemic.py    │              │  centrality()    │
    └──────────────────┘              └──────────────────┘
```

---

## Layer 1: Explanatory Coherence

### Source: `src/services/scalable_coherence.py` (~1100 lines)

This layer answers: *"How well do beliefs in the web explain each other?"*

The implementation uses **hierarchical clustering** (per Thagard + Simon satisficing):

1. **Clustering** (`ClusterManager`): Beliefs are grouped by:
   - **Primary**: `theory_id` (strongest predictor of constraint patterns)
   - **Secondary**: `EpistemicLevel` (theoretical/empirical/observational)
   - **Tertiary**: `domain` (cross-theory beliefs)

2. **Constraint Network** (`ConstraintNetwork`): O(1) lookup graph tracking which beliefs constrain each other (SUPPORTS, CONTRADICTS, EXPLAINS, MEDIATED, etc.)

3. **Two-Level Coherence Computation** (`CoherenceManager`):
   - **Intra-cluster coherence**: Dense computation (all pairs within cluster)
   - **Inter-cluster coherence**: Sparse computation (boundary nodes only)
   - **Combined**: `0.7 × intra + 0.3 × inter`

4. **Caching** (`CoherenceCache`): LRU cache with dependency-based invalidation. When a belief changes, only its cluster's cache is invalidated — not the entire web.

**Complexity**: O(n log n) vs. the naive O(n²) approach.

### Thagard's Explanatory Coherence (via Bovens-Hartmann)

Source: `src/services/refined_epistemic.py`, method `explanatory_coherence()`

```python
def explanatory_coherence(hypothesis, explained, explanation_strengths, competing_explanations):
    """
    Base coherence = average explanation strength across explained beliefs
    Penalty = number of competing explanations × 0.1
    Coherence = base - min(0.5, penalty)
    """
```

This implements the core Thagard principle: beliefs cohere when one **explains** others, and coherence decreases with **competing explanations**. The implementation bounds the penalty at 0.5 to prevent pathological cases where many weak competitors overwhelm a strong explanation.

---

## Layer 2: Positional Value (Belief Value)

### Source: `src/services/web_of_belief_modules/analysis_ops.py`

This layer answers: *"How important is this belief to the web's overall structure?"*

```python
belief_value(belief_id, centrality_weight=0.5):
    centrality = belief_centrality(belief_id)   # How connected?
    sensitivity = belief_sensitivity(belief_id)  # How much would web change if removed?
    return weighted_combination(centrality, sensitivity, centrality_weight)
```

- **Centrality**: Number and strength of constraints connecting this belief to others
- **Sensitivity**: How much the web's coherence would change if this belief were removed or revised
- **Combination**: Configurable weight (default: 50/50)

This is what the system uses for:
- **VOI prioritization**: Higher-value beliefs get investigated first
- **Gap prediction**: Missing connections to high-value beliefs generate research targets
- **Defeater search**: Potential defeaters for high-value beliefs are prioritized

---

## The Two Layers Working Together

### Entrenchment Formula

The legacy entrenchment (V23.0.0 made this emergent, not settable) combines both layers:

```
entrenchment = 0.40 × connectivity   (Layer 2: positional)
             + 0.30 × level_weight   (structural position in tier hierarchy)
             + 0.30 × coherence_contrib (Layer 1: explanatory)
```

This is computed dynamically by `WebOfBelief.get_entrenchment(belief_id)`.

### Why Two Layers?

Following Thagard's (1989) *Explanatory Coherence* and Bovens & Hartmann's (2003) *Bayesian Epistemology*:

1. **Explanation ≠ Importance**: A belief can explain many things (high coherence) but be peripheral to the web (low centrality). Conversely, a hub belief with many connections might not explain anything — it might just be well-connected to many independent findings.

2. **Revision resistance**: When the web encounters contradictions, the system must decide what to revise. The two-layer architecture prevents "revision of highly explanatory beliefs because a weakly-connected empirical finding contradicts them" (Quine's maxim of minimum mutilation).

3. **Scalability**: Separating coherence computation into clusters (Layer 1) from web-wide centrality (Layer 2) enables O(n log n) computation.

---

## Key Files

| File | Role | Lines |
|------|------|-------|
| `src/services/scalable_coherence.py` | Layer 1: Hierarchical coherence | ~1100 |
| `src/services/refined_epistemic.py` | Thagard/Bovens explanatory coherence | ~500 |
| `src/services/web_of_belief_modules/analysis_ops.py` | Layer 2: belief_value, centrality, sensitivity | ~350 |
| `src/services/web_of_belief.py` | Master state + `get_entrenchment()` | ~2100 |

## References

- Thagard, P. (1989). Explanatory Coherence. *Behavioral and Brain Sciences*, 12(3), 435-467.
- Bovens, L., & Hartmann, S. (2003). *Bayesian Epistemology*. Oxford University Press.
- Quine, W.V.O. (1951). Two Dogmas of Empiricism. *The Philosophical Review*, 60(1), 20-43.
