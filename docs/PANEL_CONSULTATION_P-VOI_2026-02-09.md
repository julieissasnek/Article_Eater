# Panel Consultation P-VOI: Value of Information - Theoretical Grounding
**Date**: 2026-02-09
**Panel ID**: P-VOI
**Priority**: CRITICAL (Foundational)

---

## The Core Question

**How does our gap-based VOI relate to classical VOI calculations, and is treating argument structure gaps as "expected information locations" theoretically defensible?**

---

## Background

### Classical VOI (Howard 1966, Raiffa & Schlaifer 1961)

The classical formulation computes:

```
VOI = E[U(d*, X)] - E[U(d₀)]
```

Where:
- `U(d, X)` = utility of decision d given state X
- `d*` = optimal decision after learning information
- `d₀` = optimal decision before learning information

**Key assumptions**:
1. Well-defined decision alternatives
2. Known prior probability distribution over states
3. Quantified utility function
4. Information reduces uncertainty about states

### Our Gap-Based Approach

In Article Eater, "gaps" are identified through argument structure analysis:

```python
class EpistemicGap:
    gap_type: GapType  # MISSING_EVIDENCE, WEAK_SUPPORT, CONTRADICTION, BOUNDARY_UNCLEAR
    target_belief: str
    predicted_voi: float  # 0-1 score
    uncertainty_reduction: float
    coherence_impact: float
```

**Key differences from classical VOI**:
1. **No explicit decision alternatives** - The "decision" is which belief to update
2. **Discrete network structure** - Gaps exist in argument topology, not continuous probability space
3. **Coherence as utility** - We maximize coherence, not expected monetary value
4. **Structural prediction** - Gaps predict WHERE information should exist

---

## Questions for the Panel

### Q1: Theoretical Status of Gap-Based VOI

Is it legitimate to call what we compute "Value of Information" or should we use different terminology?

### Q2: Relationship Between Gap VOI and Belief Credence

Currently gaps are prioritized by:
```python
UNCERTAINTY_WEIGHT = 0.4  # High uncertainty beliefs
CENTRALITY_WEIGHT = 0.3   # Well-connected beliefs
SPARSITY_WEIGHT = 0.3     # Under-supported beliefs
```

Is this weighting defensible? What should the relationship be?

### Q3: Entrenchment and Information Value

Highly entrenched beliefs are more resistant to revision. Should:
- High entrenchment INCREASE gap VOI (more valuable to find disconfirming evidence)?
- High entrenchment DECREASE gap VOI (evidence unlikely to change anything)?
- Entrenchment be orthogonal to VOI?

### Q4: Exploration-Exploitation Tradeoff

We use epsilon-greedy search with decay:
```python
initial_epsilon = 0.3  # 30% random exploration
min_epsilon = 0.05     # 5% floor
decay = 0.99           # 1% decay per search
```

Is this appropriate for epistemic search, or should coherence guide exploration differently?

### Q5: Gap Closure Measurement

Should gap closure be measured by:
- VOI reduction (the gap is "worth less" now)?
- Coherence improvement (the web is more coherent)?
- Uncertainty reduction (we're more certain)?
- Some combination?

---

## Panel Responses

### Dr. Ronald Howard (Decision Analysis, Original VOI)

*Constructed from: "Decision Analysis: Applied Decision Theory" (1966), "Information Value Theory" (1966)*

The question of whether "gap-based VOI" constitutes genuine VOI depends on whether you can articulate what DECISION is being made. In classical theory, information has value only because it changes what we DO.

**Critical observation**: Your system appears to conflate two distinct things:
1. **Value of information FOR belief revision** (which belief to update)
2. **Value of information FOR action** (what to do in the world)

If Article Eater is purely an epistemic system (updating beliefs, not taking actions), then "VOI" is a **misnomer**. What you're computing is closer to **Expected Coherence Gain** or **Expected Uncertainty Reduction**.

However, if you frame the "decision" as "which paper to read next" or "where to search," then you DO have a decision-theoretic structure:
- Alternatives: {search source A, search source B, search topic C, ...}
- States: {paper exists and is relevant, paper exists but irrelevant, no paper exists, ...}
- Utility: coherence gain from finding/not-finding information

**Recommendation**: Rename to "Expected Epistemic Gain" (EEG) unless you're modeling search decisions explicitly. If you ARE modeling search decisions, then the classical VOI framework applies, but your utility function is coherence, not monetary value.

**VERDICT**: MODIFY terminology and clarify which decision is being informed.

---

### Dr. Judea Pearl (Causal Networks, Information Value in DAGs)

*Constructed from: "Causality" (2000), "Probabilistic Reasoning in Intelligent Systems" (1988)*

The interesting innovation in your approach is treating argument structure gaps as **structural counterfactuals**. In causal graph terms, a gap says: "If node X existed and connected to nodes Y and Z, what would happen to the network's posterior?"

This is analogous to computing **do-calculus interventions** on belief networks:
```
VOI(gap) ≈ E[P(web | do(add_belief(gap.target)))] - P(web | ∅)
```

The key insight: **gaps are not random variables; they are hypothetical structural modifications**. This is fundamentally different from classical VOI, where we learn the VALUE of an existing random variable.

**Critical observation**: Your weighting formula (0.4/0.3/0.3) mixes:
- **Uncertainty** (property of existing beliefs)
- **Centrality** (structural position)
- **Sparsity** (structural deficiency)

These are incommensurable. Uncertainty is epistemic; centrality and sparsity are structural. You need a **principled way to combine** these.

**Recommendation**:
1. Separate **epistemic VOI** (reducing uncertainty about existing beliefs) from **structural VOI** (filling network gaps)
2. For structural gaps, use **counterfactual coherence**: "What coherence WOULD we have if this gap were filled?"
3. Weight centrality by **expected propagation**: high-centrality gaps propagate updates further

**Proposed formula**:
```
structural_voi = E[coherence_after_fill] - coherence_now
                 × propagation_factor(centrality)
epistemic_voi = uncertainty_reduction × belief_importance
gap_voi = α × structural_voi + (1-α) × epistemic_voi
```

Where α depends on whether the gap is structural (missing node) vs. epistemic (uncertain existing node).

**VERDICT**: MODIFY - Separate structural from epistemic VOI; use counterfactual coherence for structural gaps.

---

### Dr. Herbert Simon (Bounded Rationality, Satisficing)

*Constructed from: "Administrative Behavior" (1947), "The Sciences of the Artificial" (1969)*

The classical VOI calculation assumes unbounded computation—you can evaluate all alternatives, all states, all utilities. In practice, **satisficing** is what agents actually do.

Your epsilon-greedy approach is a reasonable satisficing heuristic for search, but the parameters (0.3 → 0.05, decay 0.99) are arbitrary. More importantly, **the decay rate should depend on search success**, not just search count.

**Key insight**: Exploration should INCREASE when:
- Recent searches failed to close gaps
- Search space appears larger than expected
- New high-VOI gaps are discovered

Exploration should DECREASE when:
- Recent searches successfully closed gaps
- Search space is being exhausted
- Gap closure rate is satisfactory

**Recommendation**:
1. Make epsilon decay **adaptive**:
   ```python
   if last_5_searches_success_rate < 0.2:
       epsilon = min(epsilon * 1.2, 0.5)  # Explore more
   elif last_5_searches_success_rate > 0.6:
       epsilon = epsilon * 0.95  # Exploit more
   ```
2. Add a **satisficing threshold**: Stop searching when coherence exceeds some acceptable level
3. Use **aspiration adaptation**: Start with high aspirations, lower them if not achievable

**On terminology**: "Value of Information" is fine as long as you acknowledge it's **bounded VOI**—the value computable within practical constraints, not theoretical maximum.

**VERDICT**: MODIFY - Make exploration adaptive based on search success, not just decay.

---

### Dr. Paul Thagard (Coherence Maximization)

*Constructed from: "Coherence in Thought and Action" (2000), "Explanatory Coherence" (1989)*

From a coherentist perspective, "Value of Information" should be understood as **Expected Coherence Contribution**. The value of filling a gap depends entirely on how it would integrate with existing beliefs.

**Critical observation**: Your gap types (MISSING_EVIDENCE, WEAK_SUPPORT, CONTRADICTION, BOUNDARY_UNCLEAR) are excellent from a coherentist standpoint. Each represents a different kind of coherence deficit:

| Gap Type | Coherence Deficit | Expected Resolution |
|----------|-------------------|---------------------|
| MISSING_EVIDENCE | Explanatory gap | New belief supports existing claim |
| WEAK_SUPPORT | Low constraint weight | Stronger evidence for existing path |
| CONTRADICTION | Negative coherence | New belief resolves tension |
| BOUNDARY_UNCLEAR | Scope ambiguity | Scope condition specification |

**Recommendation**:
1. **Weight gap types differently**: Contradictions have highest VOI (they actively HURT coherence until resolved)
2. **Use coherence gradient**: VOI = ∂coherence/∂gap_filled
3. **Don't decay exploration uniformly**: Different gap types need different exploration strategies

**Proposed gap type weights**:
```python
GAP_TYPE_WEIGHTS = {
    GapType.CONTRADICTION: 1.0,      # Highest priority - active harm
    GapType.WEAK_SUPPORT: 0.7,       # Structural weakness
    GapType.MISSING_EVIDENCE: 0.5,   # Potential improvement
    GapType.BOUNDARY_UNCLEAR: 0.4,   # Important but less urgent
}
```

**On the core question**: Yes, treating gaps as "expected information locations" is coherentist-legitimate. Gaps ARE places where coherence can be improved. Classical VOI asks "what's the value of knowing X?" Coherentist VOI asks "what's the value of HAVING a belief about X?" The latter is what you're computing.

**VERDICT**: APPROVE with modifications - Add gap type weighting; use coherence gradient for VOI.

---

### Dr. Susan Haack (Foundherentism, Epistemic Justification)

*Constructed from: "Evidence and Inquiry" (1993), "Defending Science—Within Reason" (2003)*

The tension you're grappling with is fundamental to foundherentism. Classical VOI assumes a **foundationalist** structure: some beliefs are basic, others derived, information flows upward. Your gap-based approach is more **coherentist**: beliefs mutually support each other, gaps represent missing connections.

**Critical observation**: The question "where should information exist?" presupposes a kind of structural expectation—that the argument network SHOULD have certain connections. This is **normative epistemology**, not just descriptive.

**Key distinctions**:
1. **Descriptive gaps**: Places where beliefs ARE unsupported (empirical)
2. **Normative gaps**: Places where beliefs SHOULD BE supported (theoretical expectation)
3. **Your system conflates these** when it uses argument schemes to predict gaps

**Recommendation**:
1. Be explicit about the **source of gap expectations**:
   - Argument scheme gaps (Walton) = theoretical expectations
   - Low-credence beliefs = empirical observations
   - Network sparsity = structural inference
2. Weight expectations by **track record**: Do argument-scheme-predicted gaps actually get filled by evidence in practice?
3. Allow for **stub beliefs**: Some gaps might be unfillable given current knowledge; don't keep searching forever

**On VOI terminology**: I would call what you're computing "Expected Justificatory Contribution" (EJC). It captures the foundherentist insight that justification is degree-theoretic and depends on mutual support.

**VERDICT**: MODIFY - Distinguish normative from descriptive gaps; add stub recognition.

---

### Dr. Marcia Bates (Information Science, Berrypicking)

*Constructed from: "The Design of Browsing and Berrypicking Techniques" (1989), "Information Search Process" (1979)*

The classical VOI model assumes **targeted retrieval**: you know what information you want; you just don't have it. Real information seeking is **berrypicking**: you find some information, it changes what you're looking for, you search again with modified understanding.

**Critical observation**: Your gap-based approach is perfect for berrypicking IF you update gap priorities after each search. The gap that was most valuable before a search might not be most valuable after.

**Recommendation**:
1. **Re-score all gaps after each search**: New information changes the value landscape
2. **Track gap discovery rate**: Good searches often REVEAL new gaps (this is valuable!)
3. **Use evolving search strategies**: Start broad (high epsilon), narrow as understanding develops
4. **Measure serendipity**: Track when searches find unexpected connections (not just targeted closure)

**Proposed berrypicking metrics**:
```python
@dataclass
class SearchOutcome:
    targeted_gap_closure: float  # Did we close what we aimed at?
    new_gaps_discovered: int     # Did we find new questions?
    serendipitous_connections: int  # Unexpected but valuable?
    search_refinement: str       # How did query evolve?
```

**On VOI**: In information science, we'd call this "Information Foraging Value" (IFV)—the expected payoff of following an information scent. Your gaps are scent trails.

**VERDICT**: APPROVE with modifications - Add gap re-scoring after search; track serendipity.

---

## Panel Synthesis

### Consensus Points

1. **Terminology**: "Value of Information" is acceptable but should be qualified:
   - "Expected Epistemic Gain" (EEG) or "Expected Coherence Contribution" (ECC) more precise
   - Acknowledge this is bounded/satisficing VOI, not classical unbounded

2. **Structural vs. Epistemic**: The panel unanimously recommends **separating**:
   - Structural gaps (missing nodes in argument network)
   - Epistemic gaps (high uncertainty about existing nodes)
   - These require different search strategies

3. **Gap Type Weighting**: Contradictions should be highest priority (Thagard)

4. **Adaptive Exploration**: Epsilon-greedy decay should be success-adaptive, not fixed (Simon)

5. **Post-Search Updating**: Gap priorities should be recalculated after each search (Bates)

### Key Disagreements

| Issue | Howard/Haack | Pearl/Thagard | Resolution |
|-------|--------------|---------------|------------|
| Is this "real" VOI? | Misnomer; rename | Yes, coherence-based VOI | Keep name with qualifier |
| Entrenchment role | Orthogonal | Higher = more propagation | Include in propagation factor |
| Gap closure metric | Uncertainty reduction | Coherence gain | Both; weighted by gap type |

---

## Approved Changes

### Change V1: Rename and Clarify VOI Semantics

```python
# OLD
class EpistemicGap:
    predicted_voi: float  # Unclear what this means

# NEW
class EpistemicGap:
    """
    A gap represents a location in the web of belief where information
    acquisition would improve epistemic standing.

    VOI Semantics (per P-VOI Panel 2026-02-09):
    - 'voi' here means Expected Epistemic Gain (EEG), not classical VOI
    - Computed as weighted combination of structural and epistemic factors
    - Bounded/satisficing computation, not theoretical maximum
    """
    expected_epistemic_gain: float  # Replaces predicted_voi
    structural_voi: float  # Value from filling structural gap
    epistemic_voi: float   # Value from reducing uncertainty
```

### Change V2: Separate Structural from Epistemic VOI

```python
def compute_gap_voi(gap: EpistemicGap, web: WebOfBelief) -> float:
    """
    Compute Expected Epistemic Gain for a gap.

    Per P-VOI Panel:
    - Structural VOI = counterfactual coherence improvement
    - Epistemic VOI = uncertainty reduction × belief importance
    - Combined with α weighting based on gap type
    """
    if gap.gap_type in [GapType.MISSING_EVIDENCE, GapType.WEAK_SUPPORT]:
        alpha = 0.7  # More structural
    elif gap.gap_type == GapType.CONTRADICTION:
        alpha = 0.5  # Equal weight
    else:  # BOUNDARY_UNCLEAR
        alpha = 0.3  # More epistemic

    structural_voi = compute_counterfactual_coherence(gap, web)
    epistemic_voi = gap.uncertainty_reduction * get_belief_importance(gap.target_belief)

    return alpha * structural_voi + (1 - alpha) * epistemic_voi
```

### Change V3: Gap Type Priority Weighting

```python
GAP_TYPE_WEIGHTS = {
    GapType.CONTRADICTION: 1.0,      # Active harm to coherence
    GapType.WEAK_SUPPORT: 0.7,       # Structural weakness
    GapType.MISSING_EVIDENCE: 0.5,   # Potential improvement
    GapType.BOUNDARY_UNCLEAR: 0.4,   # Scope clarification
}
```

### Change V4: Adaptive Epsilon-Greedy

```python
def update_epsilon(
    current_epsilon: float,
    recent_success_rate: float,
    min_epsilon: float = 0.05,
    max_epsilon: float = 0.5
) -> float:
    """
    Adaptive exploration based on search success (Simon).
    """
    if recent_success_rate < 0.2:
        # Searches failing - explore more
        return min(current_epsilon * 1.2, max_epsilon)
    elif recent_success_rate > 0.6:
        # Searches succeeding - exploit more
        return max(current_epsilon * 0.95, min_epsilon)
    else:
        # Maintain current balance
        return current_epsilon
```

### Change V5: Post-Search Gap Re-Scoring

```python
def rescore_gaps_after_search(
    gaps: List[EpistemicGap],
    search_result: SearchResult,
    web: WebOfBelief
) -> List[EpistemicGap]:
    """
    Recalculate all gap priorities after a search (Bates).

    New information may:
    - Close some gaps (remove from list)
    - Reveal new gaps (add to list)
    - Change value of existing gaps (re-score)
    """
    updated_gaps = []
    for gap in gaps:
        if gap_is_closed(gap, search_result):
            continue  # Remove closed gaps
        gap.expected_epistemic_gain = compute_gap_voi(gap, web)  # Re-score
        updated_gaps.append(gap)

    # Add newly discovered gaps
    new_gaps = discover_gaps_from_search(search_result, web)
    updated_gaps.extend(new_gaps)

    return sorted(updated_gaps, key=lambda g: g.expected_epistemic_gain, reverse=True)
```

### Change V6: Track Serendipity (Bates)

```python
@dataclass
class SearchMetrics:
    """Extended search outcome tracking per Bates berrypicking."""
    targeted_closure: float      # Did we close the targeted gap?
    new_gaps_discovered: int     # How many new questions emerged?
    serendipitous_links: int     # Unexpected valuable connections?
    coherence_delta: float       # Net coherence change
    query_evolution: str         # How did understanding change?
```

---

## Implementation Priority

1. **CRITICAL**: Change V2 (separate structural/epistemic VOI) - affects core algorithm
2. **HIGH**: Change V4 (adaptive epsilon) - affects search quality
3. **HIGH**: Change V3 (gap type weights) - affects prioritization
4. **MEDIUM**: Change V5 (post-search re-scoring) - affects iteration
5. **MEDIUM**: Change V1 (terminology) - documentation and clarity
6. **LOW**: Change V6 (serendipity tracking) - nice-to-have metrics

---

## Unresolved Questions (For Future Panels)

1. **How to compute counterfactual coherence efficiently?** (Pearl suggests approximation)
2. **What is the satisficing threshold for "good enough" coherence?** (Simon)
3. **How to detect when gaps are truly unfillable?** (Haack's stub recognition)
4. **How to weight track record of gap-type predictions?** (Haack)

---

*Panel consultation completed: 2026-02-09*
*Approved by: Howard, Pearl, Simon, Thagard, Haack, Bates*
