# Panel P-EC: Sprint 1.5 Epistemic-Causal Integration Review

**Date**: February 8, 2026
**Panel**: P-EC (Epistemic-Causal Integration)
**Sprint**: 1.5 — Epistemic-Causal Bridge
**Status**: COMPLETE — Pending Panel Review

---

## Panel Members

| Expert | Expertise | Focus |
|--------|-----------|-------|
| Dr. Judea Pearl | Causal inference, DAGs, do-calculus | Causal layer correctness |
| W.V.O. Quine | Coherentist epistemology, web of belief | Epistemic layer fidelity |
| Bas van Fraassen | Constructive empiricism, contrast classes | Contrastive explanation |
| Nancy Cartwright | Capacities, mechanisms, external validity | Generalization validity |
| Paul Thagard | Explanatory coherence, cognitive architecture | Coherence computation |
| Helen Longino | Social epistemology, objectivity | Community structure needs |

---

## Sprint 1.5 Deliverables Under Review

### 1. Core Integration Architecture
**File**: `src/services/epistemic_causal_bridge.py` (~2000 lines)

| Component | Purpose |
|-----------|---------|
| `EpistemicCausalBridge` | Main orchestration: web → causal models → counterfactuals |
| `ContrastClass` | Van Fraassen contrast specification |
| `PopulationContext` | Baseline-dependent meaning |
| `TheoryRelativeModel` | Per-theory structural equations |
| `MultiTheoryModel` | Weighted theory integration |
| `CounterfactualQuery` | Query with epistemic constraints |

### 2. Five Epistemic-to-Causal Influence Pathways

| Pathway | Mechanism |
|---------|-----------|
| Epistemic Level → Structural Confidence | THEORETICAL constrains structure; EMPIRICAL informs magnitude |
| Entrenchment → Robustness | High entrenchment = decision weight |
| Argument Structure → Contrast | Attacks as contrast shifts |
| Coherence → Admissibility | Filter incoherent counterfactuals |
| Meta-uncertainty → Propagation | Uncertainty compounds through model |

### 3. Integration with Existing WebOfBelief

| Method | Purpose |
|--------|---------|
| `web.create_causal_bridge()` | Factory for bridge instance |
| `web.counterfactual(intervention, outcome)` | Convenience method |
| `web.causal_bridge_available()` | Module availability check |

### 4. Compatibility Fix

**Issue**: Bridge expected `theory_ids: Dict[str, float]`, but existing Belief has `theory_id: Optional[str]`

**Resolution**: `_get_theory_beliefs()` now handles both formats via duck typing:
```python
if hasattr(b, 'theory_ids') and isinstance(b.theory_ids, dict):
    belongs_to_theory = theory_id in b.theory_ids
elif hasattr(b, 'theory_id'):
    belongs_to_theory = b.theory_id == theory_id
```

### 5. Test Coverage

- 34 tests passing
- Categories: Type compatibility, Bridge construction, Model building, Counterfactual inference, Contrast class, Robustness analysis, Epistemic quality, Error handling

---

## Panel Responses

### Dr. Judea Pearl (Causal Inference)

**Assessment**: The architecture correctly positions the epistemic layer as *prior* to the causal layer. This is a principled design choice.

**Concerns**:
1. **Structural equations from beliefs**: The current implementation extracts structural equations by pattern-matching belief tags. This is fragile. Causal structure should come from mechanistic beliefs, not tag inference.

2. **do-calculus implementation**: The `_compute_theory_counterfactual` uses simple forward propagation. For proper counterfactuals, you need:
   - Abduction (infer U from evidence)
   - Action (intervene on X)
   - Prediction (compute Y)

   Current implementation skips abduction.

3. **Theory weighting**: Weighting counterfactuals by theory credence is reasonable, but conflicts between theories aren't just about weight — they may reflect different causal structures.

**Recommendations**:
- **P-EC-R1**: Add explicit causal structure extraction from INTERMEDIATE-level mechanism beliefs
- **P-EC-R2**: Implement proper 3-step counterfactual (abduction→action→prediction)
- **P-EC-R3**: When theories disagree structurally, flag this rather than just averaging

**Verdict**: APPROVED with recommendations for Sprint 2.0

---

### W.V.O. Quine (Coherentist Epistemology)

**Assessment**: The integration respects the core Quinean principle: nothing is foundational. The causal layer is derived from the epistemic web, not imposed upon it.

**Concerns**:
1. **Belief revisability**: When counterfactual results conflict with entrenched beliefs, the system should be able to revise the beliefs, not just the causal model. This feedback loop is implicit but not implemented.

2. **Holism preservation**: The `_get_theory_beliefs` filtering by credence threshold is anti-holistic — it treats beliefs atomistically. In a true web, low-credence beliefs still contribute to coherence.

**Recommendations**:
- **P-EC-R4**: Add a feedback pathway: surprising counterfactual results → belief revision candidates
- **P-EC-R5**: Consider including low-credence beliefs with discounted influence rather than excluding them

**Verdict**: APPROVED — faithful to Quinean principles

---

### Bas van Fraassen (Contrastive Explanation)

**Assessment**: The `ContrastClass` implementation correctly captures the insight that "Why P?" is incomplete — we always ask "Why P rather than Q?"

**Concerns**:
1. **Baseline specification**: `PopulationContext` captures regional/cultural baselines, but the system doesn't yet enforce that contrasts are meaningful within the baseline. A contrast meaningful in Western contexts may be meaningless in others.

2. **Contrast transfer**: The `_assess_contrast_transfer` method attempts to score how well a contrast generalizes, but the scoring function is ad hoc. Need principled metrics.

3. **Cultural meaning**: The `contextual_meaning` field in `ConditionSpec` is a good start, but unused in current implementation.

**Recommendations**:
- **P-EC-R6**: Implement baseline-relative meaning checks before computing counterfactuals
- **P-EC-R7**: Use `contextual_meaning` to adjust counterfactual interpretation
- **P-EC-R8**: Add explicit "contrast not transferable" warnings when baselines differ significantly

**Verdict**: APPROVED — conceptually sound, implementation needs refinement

---

### Nancy Cartwright (Capacities and External Validity)

**Assessment**: The scope assessment (`_assess_scope`) is on the right track but needs strengthening.

**Concerns**:
1. **Capacities vs. regularities**: The structural equations represent regularities, but causal capacities are stable across contexts while regularities are not. The system doesn't distinguish these.

2. **Enabling conditions**: When enabling conditions (from `Belief.enabling_conditions`) aren't met, the capacity cannot manifest. Current implementation doesn't check this.

3. **Scope extrapolation penalty**: The penalty for out-of-scope extrapolation is linear. It should be nonlinear — extrapolating slightly beyond scope is very different from extrapolating far beyond.

**Recommendations**:
- **P-EC-R9**: Check `Belief.enabling_conditions` before including in counterfactual
- **P-EC-R10**: Implement nonlinear scope extrapolation penalty (e.g., exponential decay)
- **P-EC-R11**: Distinguish capacity-based beliefs from mere regularities

**Verdict**: APPROVED with concerns about external validity handling

---

### Paul Thagard (Explanatory Coherence)

**Assessment**: The coherence computation in `_check_coherence` is sound but could benefit from ECHO-style constraint satisfaction.

**Concerns**:
1. **Coherence approximation**: Current O(n²) pairwise coherence is expensive. For large webs, need approximation.

2. **Explanatory vs. analogical coherence**: The system treats all coherence uniformly, but explanatory coherence (theory→data) should be weighted differently from analogical coherence (data↔data).

3. **Coherence caching**: The `CoherenceCache` in panel_concern_resolutions.py is designed but not integrated into the main bridge.

**Recommendations**:
- **P-EC-R12**: Integrate `CoherenceCache` from panel_concern_resolutions.py
- **P-EC-R13**: Weight explanatory coherence higher than analogical (suggest 1.5:1 ratio)
- **P-EC-R14**: Add query-local coherence (only compute coherence for beliefs relevant to query)

**Verdict**: APPROVED — solid foundation

---

### Helen Longino (Social Epistemology)

**Assessment**: The current implementation treats "the field" as monolithic. Real science has communities with different:
- Entrenchment profiles
- Methodological preferences
- Theoretical commitments

**Concerns**:
1. **No community structure**: All beliefs are attributed to "the field" uniformly. When ART and SRT researchers disagree, this should be represented.

2. **No contestation tracking**: When findings are contested, this is epistemically informative — it reveals where knowledge is uncertain.

3. **Power dynamics invisible**: Some labs have more influence than others. High-impact labs can establish findings even with weaker evidence.

**Recommendations**:
- **P-EC-R15**: Sprint 2.5 (Social Epistemology) is essential — prioritize it
- **P-EC-R16**: Add `community_id` to beliefs to track provenance
- **P-EC-R17**: Implement `ContestationRecord` for disputed findings

**Verdict**: APPROVED for individual-level epistemology; social layer needed

---

## Panel Synthesis

### Unanimous Approvals
- Architecture correctly positions epistemic layer as prior to causal
- Van Fraassen contrast classes properly implemented conceptually
- Compatibility fix for `theory_id`/`theory_ids` is appropriate

### Key Concerns

| Priority | Concern | Raised By | Target Sprint |
|:--------:|---------|-----------|---------------|
| HIGH | Enabling conditions not checked | Cartwright | 1.6 or 2.0 |
| HIGH | Social epistemology missing | Longino | 2.5 |
| MEDIUM | Forward propagation vs proper counterfactual | Pearl | 2.0 |
| MEDIUM | Coherence caching not integrated | Thagard | 1.6 |
| LOW | Contextual meaning unused | van Fraassen | 2.5 |

### Recommendations Summary

| ID | Recommendation | Source | Priority | Target |
|----|----------------|--------|----------|--------|
| P-EC-R1 | Explicit causal structure from mechanism beliefs | Pearl | HIGH | 2.0 |
| P-EC-R2 | 3-step counterfactual (abduct→act→predict) | Pearl | MEDIUM | 2.0 |
| P-EC-R3 | Flag structural disagreements between theories | Pearl | MEDIUM | 2.0 |
| P-EC-R4 | Feedback: surprising results → revision candidates | Quine | MEDIUM | 2.0 |
| P-EC-R5 | Include low-credence beliefs with discounted influence | Quine | LOW | 2.5 |
| P-EC-R6 | Baseline-relative meaning checks | van Fraassen | MEDIUM | 2.5 |
| P-EC-R7 | Use contextual_meaning in interpretation | van Fraassen | LOW | 2.5 |
| P-EC-R8 | Explicit "contrast not transferable" warnings | van Fraassen | MEDIUM | 1.6 |
| P-EC-R9 | Check enabling_conditions before counterfactual | Cartwright | HIGH | 1.6 |
| P-EC-R10 | Nonlinear scope extrapolation penalty | Cartwright | MEDIUM | 2.0 |
| P-EC-R11 | Distinguish capacities from regularities | Cartwright | LOW | 2.5 |
| P-EC-R12 | Integrate CoherenceCache | Thagard | HIGH | 1.6 |
| P-EC-R13 | Weight explanatory > analogical coherence (1.5:1) | Thagard | MEDIUM | 2.0 |
| P-EC-R14 | Query-local coherence computation | Thagard | HIGH | 1.6 |
| P-EC-R15 | Prioritize Sprint 2.5 (Social Epistemology) | Longino | HIGH | 2.5 |
| P-EC-R16 | Add community_id to beliefs | Longino | MEDIUM | 2.5 |
| P-EC-R17 | Implement ContestationRecord | Longino | MEDIUM | 2.5 |

---

## Panel Verdict

**SPRINT 1.5: APPROVED**

The epistemic-causal integration is architecturally sound and philosophically principled. The panel approves proceeding to Sprint 1.6 (Quick Wins) with the following high-priority items to address:

### Immediate (Sprint 1.6)
1. **P-EC-R9**: Check `enabling_conditions` before including beliefs in counterfactuals
2. **P-EC-R12**: Integrate `CoherenceCache` for scalability
3. **P-EC-R14**: Implement query-local coherence
4. **P-EC-R8**: Add "contrast not transferable" warnings

### Next Sprint (2.0)
1. **P-EC-R1**: Extract causal structure from mechanism beliefs
2. **P-EC-R2**: Proper 3-step counterfactual
3. **P-EC-R4**: Feedback loop for belief revision

### Planned (2.5)
1. **P-EC-R15-17**: Full social epistemology layer

---

*Panel consultation complete: February 8, 2026*
*Sprint 1.5 APPROVED — Proceed to Sprint 1.6*
