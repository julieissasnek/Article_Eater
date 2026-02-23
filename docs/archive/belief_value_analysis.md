# Belief Value Analysis

## SY-9: Chang Belief Value Method

*Created: 2026-02-22 | Task: SY-9 (Panel Recommendation)*

---

## What It Does

`WebOfBelief.belief_value(belief_id)` computes the **epistemic value** of any belief in the web — a [0, 1] score indicating how "worth investigating" a belief is. High-value beliefs are both structurally important *and* fragile.

Per P-EC panel (Chang, SY-9): *"This metric identifies beliefs that are most worth investigating — they're structurally important AND their revision would significantly affect the web."*

---

## The Formula

```
belief_value = w × centrality + (1 - w) × sensitivity
```

Where `w = centrality_weight` (default 0.5).

### Component 1: Centrality

**Question**: *How connected is this belief?*

```python
centrality = f(constraint_count, total_beliefs)
```

- Counts all constraints (SUPPORTS, CONTRADICTS, EXPLAINS, MEDIATED, etc.) touching this belief
- Normalizes by total web size
- **High centrality** = belief is a hub, connected to many other beliefs

### Component 2: Sensitivity

**Question**: *How much would the web change if this belief shifted?*

```python
sensitivity = |coherence_after_perturbation - coherence_before| / delta
```

Implementation:
1. Record current web coherence
2. Perturb the belief's credence by ±δ (default 0.1)
3. Recompute web coherence
4. Measure the change, then restore original state
5. Sensitivity = |Δcoherence| / δ, clamped to [0, 1]

- **High sensitivity** = the web is fragile with respect to this belief — changing it would cascade through many constraints

---

## Usage Examples

### 1. Finding the most valuable beliefs for research

```python
from src.services.web_accumulator import WebAccumulator

acc = WebAccumulator()
web, _ = acc.get_master_web()

# Get value for a specific belief
v = web.belief_value("attention_restoration_theory")
print(f"ART value: {v:.3f}")

# Rank all beliefs by value
ranked = sorted(
    web.beliefs.keys(),
    key=lambda bid: web.belief_value(bid),
    reverse=True
)
for bid in ranked[:10]:
    print(f"  {bid}: {web.belief_value(bid):.3f}")
```

### 2. Adjusting the centrality/sensitivity balance

```python
# Favor structurally important beliefs (good for gap prediction)
v_structural = web.belief_value("wood_stress_reduction", centrality_weight=0.8)

# Favor fragile beliefs (good for defeater search)
v_fragile = web.belief_value("wood_stress_reduction", centrality_weight=0.2)
```

### 3. VOI-driven research prioritization

The gap predictor uses `belief_value` to rank research targets:

```python
from src.services.gap_predictor import GapPredictor

gp = GapPredictor(web)
gaps = gp.predict_gaps()

# Each gap's priority incorporates belief_value of its parent beliefs
for gap in sorted(gaps, key=lambda g: g.voi_score, reverse=True)[:5]:
    print(f"  {gap.description}: VOI={gap.voi_score:.3f}")
```

---

## When to Use What Weight

| Use Case | `centrality_weight` | Rationale |
|----------|-------------------|-----------|
| Research prioritization | 0.5 (default) | Balance hub importance with fragility |
| Gap prediction | 0.6–0.8 | Favor well-connected beliefs (missing connections to hubs matter most) |
| Defeater search | 0.2–0.4 | Favor sensitive beliefs (fragile beliefs need testing most) |
| Theory revision | 0.3 | Highly sensitive theoretical beliefs are revision candidates |

---

## Key Files

| File | Function | Role |
|------|----------|------|
| `src/services/web_of_belief.py` | `WebOfBelief.belief_value()` | Public API |
| `src/services/web_of_belief_modules/analysis_ops.py` | `WebAnalysisOperations.belief_value()` | Core computation |
| `src/services/web_of_belief_modules/analysis_ops.py` | `belief_centrality()` | Constraint connectivity |
| `src/services/web_of_belief_modules/analysis_ops.py` | `belief_sensitivity()` | Perturbation-based fragility |

## Theoretical Background

Based on Chang's (2004) *Inventing Temperature* — the idea that some measurements/beliefs are more epistemically valuable because they simultaneously constrain and are constrained by many other parts of the knowledge system. When such a belief is revised, the ripple effects are large — making it a high-priority target for both investigation and protection.
