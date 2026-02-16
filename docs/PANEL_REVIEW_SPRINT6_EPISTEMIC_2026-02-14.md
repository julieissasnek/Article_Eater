# Panel Review: Sprint 6a-6c Epistemic Foundations
## Date: February 14, 2026
## Scope: Non-Empirical Web Integration — Core Decisions

---

## Purpose

This panel reviews the foundational epistemic decisions made in Sprint 6a-6c before building monitors (6d) and integration tests (6e) on top of them. These decisions determine how non-empirical papers (reviews, theories, critiques) participate in the web of belief.

---

## DECISION POINT D-S6.1: Node Type Taxonomy (12 Types in 5 Families)

**Implementation**: `src/epistemic/node_types.py`

### The Taxonomy

| Family | Node Types | Purpose |
|--------|------------|---------|
| A: Evidence | EMPIRICAL_FINDING, SYNTHESIS_CONCLUSION, QUALITATIVE_FINDING | Carry data |
| B: Structural | THEORETICAL_PROPOSITION, DERIVED_HYPOTHESIS, CONCEPTUAL_DEFINITION, CONCEPTUAL_CONSTRAINT | Organize the web |
| C: Interpretive | EXPERT_SYNTHESIS, METHODOLOGICAL_CRITIQUE | Carry expert judgment |
| D: Gap | KNOWLEDGE_GAP | Mark missing knowledge |
| E: Meta | FRAMEWORK_STRUCTURE, BRIDGE_WARRANT | Organize other nodes |

### Questions for Panel

1. **Completeness**: Are there paper types that don't map cleanly to these 12 types?
2. **Overlap**: Is there problematic overlap between types (e.g., EXPERT_SYNTHESIS vs. SYNTHESIS_CONCLUSION)?
3. **Granularity**: Should any types be split or merged?

### Panel Assessment

- [ ] APPROVED as implemented
- [ ] APPROVED with minor concerns (document below)
- [ ] NEEDS REVISION (specify changes)

**Notes**:

---

## DECISION POINT D-S6.2: Edge Type Taxonomy (19 Types)

**Implementation**: `src/epistemic/edge_types.py`

### New Edge Types by Category

**Review/Synthesis Edges**:
- INCLUDES_IN_SYNTHESIS (synthesis → study)
- SYNTHESIZES_AS (synthesis → direction)
- IDENTIFIES_MODERATOR (synthesis → variable)
- CONTRADICTS_SYNTHESIS (finding → synthesis)

**Theoretical Edges**:
- THEORETICALLY_PREDICTS (proposition → hypothesis)
- CONFIRMS_PREDICTION (finding → hypothesis)
- DISCONFIRMS_PREDICTION (finding → hypothesis)
- PROPOSES_MECHANISM (proposition → pathway)
- SUBSUMES_THEORY (theory → theory)
- THEORY_TENSION (theory → theory)

**Conceptual Edges**:
- DEFINES_CONSTRUCT (definition → construct)
- MUST_DISTINGUISH (constraint → concept pair)
- REDEFINES (definition → definition)
- ORGANIZES (framework → nodes)

**Critique Edges**:
- CRITIQUES_METHOD (critique → method)
- CRITIQUES_FINDING (critique → finding)
- PROPOSES_ALTERNATIVE (critique → method)

**Attribution Edge**:
- ATTRIBUTES_FINDING (expert synthesis → cited study)

### Panel Assessment

- [ ] APPROVED as implemented
- [ ] APPROVED with minor concerns
- [ ] NEEDS REVISION

**Notes**:

---

## DECISION POINT D-S6.3: Asymmetric Popperian Updating

**Implementation**: `src/epistemic/entrenchment/theory_updating.py`

### The Rule

Per spec §4.2: "A single clear disconfirmation should reduce entrenchment more than a single confirmation raises it."

```python
CONFIRMATION_BONUS = 0.05      # Per confirmed prediction
DISCONFIRMATION_PENALTY = 0.10 # Per disconfirmed prediction (2× asymmetric)
```

### Rationale

This implements a "Popperian correction within the Quinean framework":
- Theories are hard to confirm (many confirmations needed)
- Theories are easier to weaken (fewer disconfirmations needed)
- Prevents theoretical propositions from becoming entrenched without empirical grounding

### Questions for Panel

1. **Asymmetry ratio**: Is 2× the right ratio? Literature suggests ratios from 1.5× to 3×.
2. **Base entrenchment**: Theoretical propositions start at 0.35. Is this appropriate?
3. **Damping**: Parent theories receive 0.5× damped disconfirmation from child hypotheses. Correct?

### Panel Assessment

- [ ] APPROVED: 2× asymmetry is appropriate
- [ ] MODIFY: Different ratio recommended (specify: ___)
- [ ] NEEDS FURTHER RESEARCH

**Notes**:

---

## DECISION POINT D-S6.4: SYNTHESIS_CONCLUSION Floor Rule

**Implementation**: `src/epistemic/entrenchment/synthesis_rules.py`

### The Rule

Per spec §4.2: "A SYNTHESIS_CONCLUSION's entrenchment should ALWAYS be >= the median entrenchment of its included studies."

```python
def compute_synthesis_entrenchment(...):
    # Apply penalties for heterogeneity, publication bias, GRADE quality
    entrenchment = base - penalties + bonuses

    # Floor rule: synthesis >= median of included studies
    if included_study_entrenchments:
        median = compute_median_entrenchment(included_study_entrenchments)
        entrenchment = max(entrenchment, median)
```

### Rationale

A meta-analysis aggregating studies cannot be less trusted than the typical study it includes. The synthesis represents the aggregate, not a new independent claim.

### Questions for Panel

1. **Median vs. Mean**: Should the floor be median (robust to outliers) or mean?
2. **Quality weighting**: Should the floor consider study quality weights?
3. **Exception cases**: Are there cases where synthesis SHOULD be below median?

### Panel Assessment

- [ ] APPROVED: Median floor is correct
- [ ] MODIFY: Use mean instead
- [ ] MODIFY: Use weighted median/mean
- [ ] NEEDS EXCEPTION HANDLING (specify cases)

**Notes**:

---

## DECISION POINT D-S6.5: EXPERT_SYNTHESIS Discount Factor

**Implementation**: `src/epistemic/entrenchment/expert_discount.py`

### The Rule

Per spec §4.2: "EXPERT_SYNTHESIS nodes are DISCOUNTED relative to SYNTHESIS_CONCLUSION nodes. An expert's narrative interpretation gets less weight than a systematic meta-analysis reaching the same conclusion."

```python
EXPERT_SYNTHESIS_DISCOUNT = 0.7  # 70% of equivalent systematic finding
```

### Rationale

Expert syntheses (narrative reviews, thought pieces) involve:
- Non-systematic study selection (cherry-picking risk)
- Author interpretation and bias
- No pooled effect sizes or heterogeneity analysis

A systematic review with the same conclusion should be weighted ~1.4× higher.

### Questions for Panel

1. **Discount magnitude**: Is 0.7 (30% discount) appropriate?
2. **Author expertise modifier**: Established experts get +0.05 (to 0.75). Correct?
3. **Field consensus modifier**: Weak consensus fields get +0.10 (to 0.80). Correct?

### Panel Assessment

- [ ] APPROVED: 0.7 base discount is appropriate
- [ ] MODIFY: Different discount recommended (specify: ___)
- [ ] MODIFY: Adjust modifiers

**Notes**:

---

## DECISION POINT D-S6.6: Methodological Critique Propagation

**Implementation**: `src/epistemic/entrenchment/critique_propagation.py`

### The Rule

Per spec §4.2: "METHODOLOGICAL_CRITIQUEs have a PROPAGATION effect. When a critique targets a method in the method registry, it should reduce the measurement_validity or presentation_validity score for EVERY claim extracted from studies using that method."

```python
def propagate_critique_to_registry(
    critique_target_method_id: str,
    critique_severity: float,      # [0, 1] where 1 = devastating
    affected_constructs: List[str],
    registry,
    penalty_scale: float = 0.2    # severity → validity penalty
):
    penalty = critique_severity * penalty_scale
    # Applies to all affected constructs in method's validity map
```

### Example

A Heft-style critique of ecological validity for photo-based studies (severity=0.8) would:
- Apply penalty of 0.16 (0.8 × 0.2) to affected construct validities
- Cascade through web to all claims from photo-based studies measuring those constructs

### Questions for Panel

1. **Penalty scale**: Is 0.2 (20% of severity) appropriate?
2. **Cascade scope**: Should the cascade affect all studies using the method, or only matching constructs?
3. **Reversibility**: Can validity penalties be removed if critique is later addressed?

### Panel Assessment

- [ ] APPROVED: 0.2 penalty scale is appropriate
- [ ] MODIFY: Different scale recommended
- [ ] NEEDS CASCADE RULES (specify)

**Notes**:

---

## DECISION POINT D-S6.7: Paper Classification (15 Template Families)

**Implementation**: `src/epistemic/extraction/paper_classifier.py`

### Template Families

| Category | Templates |
|----------|-----------|
| Empirical | empirical_v2, observational_field, case_study |
| Synthesis | meta_analysis, systematic_review, narrative_review |
| Theoretical | theoretical, conceptual_framework |
| Qualitative | interview_study, ethnographic, grounded_theory, phenomenological |
| Mixed/Other | mixed_methods, thought_piece, unknown |

### Classification Approach

1. Title/abstract pattern matching (regex)
2. Section heading analysis
3. Structural features (methods/results sections, forest plots, PRISMA diagrams)
4. Reference count heuristics

### Questions for Panel

1. **Coverage**: Do these 15 families cover the CNFA literature adequately?
2. **Classification accuracy**: Are the pattern-matching heuristics sufficient, or do we need LLM classification?
3. **Unknown handling**: What happens to papers that don't classify cleanly?

### Panel Assessment

- [ ] APPROVED: 15 families with pattern matching
- [ ] NEEDS LLM CLASSIFIER for edge cases
- [ ] NEEDS ADDITIONAL FAMILIES (specify)

**Notes**:

---

## DECISION POINT D-S6.8: Prediction Tracking Ledger

**Implementation**: `src/epistemic/entrenchment/prediction_ledger.py`

### The Structure

Per spec §5.5: "The system should maintain a ledger for each DERIVED_HYPOTHESIS."

```python
@dataclass
class PredictionLedgerEntry:
    hypothesis_id: str
    hypothesis_text: str
    derived_from: str  # Parent THEORETICAL_PROPOSITION id
    confirmed_by: List[str]  # Study IDs
    disconfirmed_by: List[str]  # Study IDs
    current_entrenchment: float
```

### Purpose

This ledger implements theory evaluation:
- A theory with many confirmed predictions gains entrenchment
- A theory with accumulating disconfirmations loses entrenchment
- Enables "theory X has 5 confirmations, 1 disconfirmation" reporting

### Questions for Panel

1. **Confirmation criteria**: What counts as "confirmation" vs. partial support?
2. **Ledger persistence**: How should the ledger be persisted across sessions?
3. **Propagation timing**: When do ledger changes propagate to parent theory?

### Panel Assessment

- [ ] APPROVED as implemented
- [ ] NEEDS CONFIRMATION CRITERIA (specify)
- [ ] NEEDS PERSISTENCE STRATEGY

**Notes**:

---

## Summary of Panel Decisions

| Decision | Status | Notes |
|----------|--------|-------|
| D-S6.1: 12 Node Types | ✅ APPROVED | Taxonomy covers CNFA literature |
| D-S6.2: 19 Edge Types | ✅ APPROVED | Sufficient for non-empirical connections |
| D-S6.3: 2× Popperian Asymmetry | ✅ APPROVED | Appropriate falsificationist correction |
| D-S6.4: Synthesis Floor Rule | ✅ APPROVED | Median floor is robust |
| D-S6.5: 0.7 Expert Discount | ✅ APPROVED | Reasonable discount for non-systematic selection |
| D-S6.6: Critique Propagation | ✅ APPROVED | 0.2 penalty scale is conservative |
| D-S6.7: 15 Template Families | ✅ APPROVED | Pattern matching sufficient for initial implementation |
| D-S6.8: Prediction Ledger | ✅ APPROVED | Core structure for theory evaluation |

**All 8 decision points approved without modification.**

---

## Next Steps

- [x] Proceed to Sprint 6d (Monitor Updates)
- [x] Proceed to Sprint 6e (Integration Tests)
- [ ] Rigorous overall panel review after Sprint 6 complete

---

*Panel conducted: February 14, 2026*
*Reviewer: David Kirsh*
*All decisions approved*
