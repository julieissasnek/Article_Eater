# Expert Panel Consultation: Research Queue Prioritization

**Date**: 2026-02-15
**Panel ID**: P-QUEUE-1
**Topic**: How should the Research Queue prioritize targets?

---

## Panel Composition

### Decision Theory
- **Herbert Simon** (satisficing, bounded rationality)
- **Ronald Howard** (value of information)

### Coherence & Structure
- **Paul Thagard** (explanatory coherence)
- **Susan Haack** (foundherentism)

### Causation
- **Judea Pearl** (causal hierarchy, structural vs. epistemic)
- **Nancy Cartwright** (capacities, scope conditions)

### Theory Integration (NEW)
- **David Marr** (computational/algorithmic/implementation levels)
- **Karl Friston** (free energy, prediction error as priority signal)

---

## The Question

> Given the Research Queue contains targets from multiple sources (GapPredictor,
> theory-driven predictions, VOI analysis), how should we compute a unified
> priority score that respects:
>
> 1. Epistemic urgency (what hurts coherence most)
> 2. Theory alignment (what Tier 1 frameworks predict should exist)
> 3. Practical findability (what's likely to exist vs. research opportunity)
> 4. Satisficing constraints (when to stop searching)

---

## Panel Responses

### Simon: Bounded Rationality and Satisficing

**Core Principle**: Don't compute optimal priorities — compute "good enough" priorities quickly.

**Recommendations**:

1. **Three-bucket priority** (not continuous scores):
   - HIGH: Act now — coherence actively damaged
   - MEDIUM: Should address — structural gap or theory prediction
   - LOW: Nice to have — boundary clarification

2. **Satisficing stopping rules**:
   ```
   STOP searching for a target when:
   - Found ≥3 relevant articles, OR
   - Searched ≥5 databases with ≥50 results screened, OR
   - Time spent > 2 hours (escalate to human_researcher)
   ```

3. **Don't re-optimize continuously**:
   - Refresh queue daily, not per-target
   - Batch similar targets together

---

### Howard: Value of Information Framework

**Core Principle**: VOI = (Value of best action after info) - (Value of best action before info)

**Recommendations**:

1. **Frame the decision correctly**:
   > The decision being informed is: "Which paper to read/ingest next?"
   > NOT: "What is the true state of the world?"

2. **VOI decomposition** (per P-VOI Panel):
   ```python
   total_voi = w1 * structural_voi + w2 * epistemic_voi + w3 * theory_voi

   where:
     structural_voi = coherence_gain_if_gap_filled
     epistemic_voi = uncertainty_reduction_expected
     theory_voi = n_frameworks_that_predict_this / 8  # NEW
   ```

3. **Suggest weights**:
   ```python
   w1 = 0.4  # Structural (coherence)
   w2 = 0.3  # Epistemic (uncertainty)
   w3 = 0.3  # Theory alignment (NEW)
   ```

---

### Thagard: Explanatory Coherence

**Core Principle**: Prioritize gaps that most damage explanatory coherence when unfilled.

**Recommendations**:

1. **Coherence impact scoring**:
   ```python
   coherence_impact = (
       n_beliefs_affected * 0.3 +
       avg_credence_of_affected * 0.3 +
       is_on_critical_path * 0.4  # path from theory to observation
   )
   ```

2. **Gap type priorities** (already implemented, confirm):
   | Gap Type | Priority Weight | Rationale |
   |----------|-----------------|-----------|
   | CONTRADICTION | 1.0 | Actively damages coherence |
   | DIRECTION | 0.9 | Causal confusion propagates |
   | MECHANISM | 0.7 | Explanatory gap |
   | VALIDATION | 0.6 | Theory needs grounding |
   | BOUNDARY | 0.4 | Scope clarification |
   | MEDIATION | 0.5 | Structural completeness |

3. **Theory-driven boost**:
   ```python
   if gap.theory_drivers:
       priority *= 1.0 + 0.1 * len(gap.theory_drivers)
   # Gap predicted by 3 frameworks gets 1.3x boost
   ```

---

### Haack: Foundherentist Grounding

**Core Principle**: Beliefs need both coherence AND experiential grounding. Prioritize gaps in grounding chains.

**Recommendations**:

1. **Track grounding depth**:
   ```python
   grounding_depth = min_path_length_to_empirical_finding
   # Beliefs far from empirical grounding are more vulnerable
   ```

2. **Prioritize ungrounded theory predictions**:
   ```python
   if belief.level == THEORETICAL and grounding_depth > 3:
       # Theory claim with no empirical support within 3 hops
       priority = HIGH
   ```

3. **Foundational gaps first**:
   ```
   Fill gaps closer to empirical base before theoretical superstructure
   ```

---

### Pearl: Causal Hierarchy and Structural VOI

**Core Principle**: Distinguish structural gaps (missing edges) from parametric gaps (uncertain weights).

**Recommendations**:

1. **Structural vs. Epistemic separation**:
   ```python
   structural_gap = edge_missing or direction_unknown
   epistemic_gap = edge_exists_but_uncertain

   # Structural gaps affect d-separation, more fundamental
   if structural_gap:
       priority *= 1.5
   ```

2. **Causal level priorities**:
   | Causal Level | Priority Boost | Rationale |
   |--------------|----------------|-----------|
   | Counterfactual | 1.3x | Hardest to establish, most valuable |
   | Interventional | 1.2x | Enables causal claims |
   | Associational | 1.0x | Baseline |

3. **Identifiability check**:
   ```python
   if not is_causally_identifiable(target_edge):
       # Can't resolve even with data — may be research design question
       mark_as_research_opportunity(
           reason="Requires experimental design, not literature search"
       )
   ```

---

### Cartwright: Capacities and Scope

**Core Principle**: Effects are local. Prioritize gaps that clarify scope conditions.

**Recommendations**:

1. **Scope-conditional VOI**:
   ```python
   # A finding proven in offices but not hospitals has limited scope
   scope_coverage = n_settings_tested / n_relevant_settings
   if scope_coverage < 0.5:
       priority_for_boundary_gaps *= 1.3
   ```

2. **Population generalization tracking**:
   ```python
   pop_coverage = n_populations_tested / n_target_populations
   # Findings only on students get boundary gap boost
   ```

3. **Enabling condition gaps**:
   ```
   If X→Y is established but enabling conditions unclear:
   - HIGH priority if X is architectural (can't be retrofitted)
   - MEDIUM priority if X is easily modifiable
   ```

---

### Marr: Levels of Analysis (NEW — Theory Integration)

**Core Principle**: Gaps exist at different levels. Prioritize based on which level is weakest.

**Recommendations**:

1. **Three-level gap classification**:
   | Level | Example Gap | Priority |
   |-------|-------------|----------|
   | Computational | WHY does nature reduce stress? (missing framework link) | HIGH |
   | Algorithmic | HOW does the brain compute this? (missing mechanism) | MEDIUM |
   | Implementation | WHERE in the brain? (missing neural evidence) | LOW |

2. **Level-appropriate targets**:
   ```python
   if gap.level == COMPUTATIONAL:
       suggested_search = "theory framework model"
   elif gap.level == ALGORITHMIC:
       suggested_search = "mechanism pathway process"
   elif gap.level == IMPLEMENTATION:
       suggested_search = "fMRI EEG neural imaging"
   ```

3. **Cross-level coherence**:
   ```
   If computational-level theory exists but algorithmic mechanism missing:
   - This is a MECHANISM gap, HIGH priority
   - Tier 1 framework predicts it, no Tier 3 finding supports it
   ```

---

### Friston: Free Energy and Prediction Error (NEW — Theory Integration)

**Core Principle**: The system should minimize its own prediction error about the literature.

**Recommendations**:

1. **Prediction error as priority**:
   ```python
   # If Tier 1 framework PREDICTS finding X should exist
   # But we haven't found X
   # That's high prediction error → high priority

   prediction_error = framework_confidence * (1 - evidence_found)
   priority ∝ prediction_error
   ```

2. **Active inference framing**:
   ```
   The Research Queue is the system's "action policy" for reducing
   uncertainty. Targets with highest expected uncertainty reduction
   should be searched first.
   ```

3. **Precision weighting**:
   ```python
   # Weight by how precisely the framework predicts the finding
   if prediction.quantitative:
       precision = 1 / prediction.ci_width
   else:
       precision = 0.5  # qualitative predictions are less precise

   weighted_priority = prediction_error * precision
   ```

---

## Panel Consensus: Priority Formula

```python
def compute_priority(target: ResearchTarget) -> float:
    """
    Unified priority score per P-QUEUE-1 panel consensus.

    Returns value in [0, 1] where higher = more urgent.
    """

    # === Component 1: Gap Type Base Priority (Thagard) ===
    gap_base = GAP_TYPE_WEIGHTS[target.gap_type]

    # === Component 2: VOI Decomposition (Howard) ===
    structural_voi = target.structural_voi  # From GapPredictor
    epistemic_voi = target.epistemic_voi    # From uncertainty analysis

    # === Component 3: Theory Alignment (Friston, NEW) ===
    n_frameworks = len(target.theory_drivers)
    theory_voi = min(n_frameworks / 3, 1.0)  # Cap at 3 frameworks predicting

    # If framework makes precise prediction, boost further
    if target.mechanism_predictions:
        theory_voi *= 1.2

    # === Component 4: Coherence Impact (Thagard) ===
    coherence_impact = (
        len(target.affected_beliefs) * 0.1 +
        target.is_on_critical_path * 0.3
    )
    coherence_impact = min(coherence_impact, 1.0)

    # === Component 5: Grounding Depth (Haack) ===
    grounding_penalty = 0
    if target.grounding_depth > 3:
        grounding_penalty = 0.2  # Far from empirical base

    # === Component 6: Structural Gap Boost (Pearl) ===
    structural_boost = 0
    if target.gap_type in [GapType.DIRECTION, GapType.UNJUSTIFIED_EDGE]:
        structural_boost = 0.2

    # === Weighted Combination ===
    priority = (
        gap_base * 0.25 +
        structural_voi * 0.15 +
        epistemic_voi * 0.15 +
        theory_voi * 0.20 +           # NEW: Theory alignment
        coherence_impact * 0.15 +
        structural_boost +
        grounding_penalty
    )

    return min(priority, 1.0)


# === Priority Buckets (Simon) ===
def bucket_priority(score: float) -> Priority:
    if score >= 0.7:
        return Priority.HIGH
    elif score >= 0.4:
        return Priority.MEDIUM
    else:
        return Priority.LOW
```

---

## Panel Consensus: Satisficing Rules (Simon)

```python
SATISFICING_RULES = {
    "max_search_time_hours": 2,
    "min_articles_to_stop": 3,
    "max_databases": 5,
    "max_results_screened": 50,
    "stale_after_days": 30,
}

def should_stop_searching(target: ResearchTarget, search_log: SearchLog) -> bool:
    """Per Simon: Don't optimize, satisfice."""

    # Found enough
    if len(search_log.articles_found) >= SATISFICING_RULES["min_articles_to_stop"]:
        return True

    # Searched enough
    if search_log.n_databases >= SATISFICING_RULES["max_databases"]:
        if search_log.n_screened >= SATISFICING_RULES["max_results_screened"]:
            return True

    # Time limit
    if search_log.time_spent_hours >= SATISFICING_RULES["max_search_time_hours"]:
        return True  # Escalate to human

    return False
```

---

## Panel Consensus: Theory-Driven Queue Refresh

```python
def refresh_theory_driven_targets(frameworks: List[Theory]) -> List[ResearchTarget]:
    """
    Generate targets from Tier 1 framework predictions.

    Per Friston: Minimize prediction error between what frameworks
    predict SHOULD exist and what we've found.
    """
    targets = []

    for framework in frameworks:
        for prediction in framework.all_predictions:
            # Check if prediction has empirical support
            support = find_supporting_beliefs(prediction)

            if not support or support.credence < 0.5:
                # High prediction error — framework predicts, no evidence
                target = ResearchTarget(
                    gap_type=GapType.VALIDATION,
                    gap_description=f"{framework.name} predicts: {prediction.statement}",
                    theory_drivers=[framework.theory_id],
                    mechanism_predictions=[prediction.statement],
                    voi_score=framework.overall_confidence * (1 - support.credence if support else 1.0),
                    is_research_opportunity=False,
                )
                targets.append(target)

    return targets
```

---

## Implementation Recommendations

1. **Add theory_voi field to ResearchTarget** (per Friston)
2. **Track grounding_depth in GapPredictor** (per Haack)
3. **Add causal_level to targets** (per Pearl)
4. **Implement satisficing rules** (per Simon)
5. **Add Marr levels to gap classification** (per Marr)

---

## Appendix: Expert Citations

- Simon, H. A. (1956). Rational choice and the structure of the environment.
- Howard, R. A. (1966). Information value theory.
- Thagard, P. (1989). Explanatory coherence.
- Haack, S. (1993). Evidence and Inquiry.
- Pearl, J. (2009). Causality.
- Cartwright, N. (1989). Nature's Capacities and their Measurement.
- Marr, D. (1982). Vision.
- Friston, K. (2010). The free-energy principle.
