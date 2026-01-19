# Expert Panel Review: Implementation Plan for Validation Concerns

**Date**: Sunday, January 19, 2026
**Document Reviewed**: `IMPLEMENTATION_PLAN_PANEL_CONCERNS_2026_01_19.md`
**Panel**: Pearl, Cartwright, Simon, Bates, Kaplan

---

## Overall Assessment

**Verdict: APPROVED WITH MODIFICATIONS**

The plan addresses our core concerns systematically. The sprint structure is logical, and the prioritization is correct (causal structure before validation infrastructure). We have specific recommendations and answers to the posed questions.

---

## Individual Reviews

### Dr. Judea Pearl

**Assessment**: Satisfied with causal direction approach.

**On 6.1 (Causal Direction)**:

Your `CausalDirection` enum is well-designed. I particularly approve of distinguishing `COMMON_CAUSE` from `CORRELATIONAL`—this is a distinction most systems miss.

**Recommendation**: Add one more category:

```python
class CausalDirection(Enum):
    # ... existing ...
    MEDIATED = "mediated"  # A → M → B (causal but indirect)
```

This matters for CNFA. "Nature reduces stress" may be mediated: Nature → Attention Restoration → Reduced Cognitive Load → Stress Reduction. The direct link is `MEDIATED`, not `FORWARD`.

**Answer to Question 1 (Defaults)**:

> Should `UNKNOWN` be the default, or `CORRELATIONAL`?

**`CORRELATIONAL` should be the default for empirical findings; `UNKNOWN` for theoretical claims.**

Rationale: Most empirical papers in psychology establish correlations and claim causation rhetorically. Defaulting to `CORRELATIONAL` forces the system to find explicit causal evidence before upgrading. This is appropriately conservative.

**On Gold Standard Papers**:

Berman et al. (2008) is experimental and should demonstrate that your system CAN assign `FORWARD` causal direction when warranted. If it doesn't, your extraction logic needs refinement.

**Missing Test Case**: Include a longitudinal study (not just cross-sectional observational vs. experimental). Longitudinal studies warrant stronger causal inference than cross-sectional but weaker than experimental. Your system should produce:

- Cross-sectional observational: `CORRELATIONAL`
- Longitudinal observational: `FORWARD` with elevated uncertainty
- Experimental: `FORWARD` with lower uncertainty

---

### Dr. Nancy Cartwright

**Assessment**: Scope conditions approach is correct. Overlap detection needs specification.

**On 6.2 (Scope Conditions)**:

The `ScopeConditions` dataclass covers the right dimensions. However, `_scopes_overlap()` is underspecified in the plan. Let me be precise:

**Overlap Rules**:

```python
def _scopes_overlap(self, s1: ScopeConditions, s2: ScopeConditions) -> bool:
    """
    Scopes overlap if they share at least one compatible value
    in each non-null dimension.
    """
    # Null = universal scope (applies to all)
    # Check each dimension
    for field in ['population', 'setting', 'duration', 'measurement']:
        v1 = getattr(s1, field)
        v2 = getattr(s2, field)

        # If both specified and different, no overlap
        if v1 and v2 and not self._values_compatible(v1, v2):
            return False

    # If we get here, scopes are compatible (may overlap)
    return True

def _values_compatible(self, v1: str, v2: str) -> bool:
    """Check if scope values are compatible (could apply to same case)."""
    # Exact match
    if v1 == v2:
        return True

    # Hierarchical compatibility
    # e.g., "adults" overlaps with "healthy_adults" but not "children"
    return self._is_hierarchical_match(v1, v2)
```

**Answer to Question 2 (Overlap Threshold)**:

> How much overlap required before declaring genuine conflict?

**Any dimension mismatch should block `GENUINE_CONTRADICTION`.**

If populations differ (adults vs. children), it's a scope boundary—full stop. We shouldn't require "at least 3 of 4 dimensions match." One clear difference is sufficient to explain divergent findings.

**On Conflict Type Refinement**:

Add `PRECISION_BOUNDARY` as a conflict type:

```python
class ConflictType(Enum):
    # ... existing ...
    PRECISION_BOUNDARY = "precision_boundary"  # Same direction, different magnitude
```

Example: Paper A says "moderate effect (d=0.4)", Paper B says "small effect (d=0.15)". These aren't contradictions—they're precision differences. The system should:
1. NOT flag as conflict
2. Merge with appropriate uncertainty
3. Note heterogeneity in meta-analytic sense

---

### Dr. Herbert Simon

**Assessment**: Validation infrastructure is appropriate. Leave-one-out is the key test.

**On 8.2 (Leave-One-Out)**:

This is the most important validation mechanism. Let me sharpen the implementation:

**Prediction Protocol**:

```python
def _predict_belief(self, web: WebOfBelief, held_out_belief: Belief) -> Prediction:
    """
    Can we predict a held-out belief from the web structure?

    Three prediction modes:
    1. DIRECT: Identical belief exists (different paper) → predict its credence
    2. CONSTRAINED: Related beliefs exist via constraints → derive credence
    3. NOVEL: No related beliefs → predict prior (0.5) with high uncertainty
    """
    # Mode 1: Direct match
    for b in web.beliefs.values():
        if self._same_construct(b, held_out_belief):
            return Prediction(
                credence=b.credence.value,
                confidence=0.8,
                mode="DIRECT"
            )

    # Mode 2: Constrained inference
    related = self._find_related_beliefs(web, held_out_belief)
    if related:
        inferred = self._infer_from_constraints(web, related, held_out_belief)
        return Prediction(
            credence=inferred.value,
            confidence=0.5,
            mode="CONSTRAINED"
        )

    # Mode 3: Novel
    return Prediction(
        credence=0.5,
        confidence=0.2,
        mode="NOVEL"
    )
```

**Success Criteria for LOO**:
- DIRECT predictions should have MAE < 0.1 (same finding across papers)
- CONSTRAINED predictions should have MAE < 0.2 (inference from structure)
- NOVEL predictions should be rare (<20% of held-out beliefs)

If most predictions are NOVEL, the web lacks generalizable structure.

**Answer to Question 5 (Pass Threshold)**:

> Is 0.7 F1 appropriate?

**0.7 is appropriate for belief extraction. But differentiate by epistemic level:**

- Empirical findings: Require F1 ≥ 0.75 (these are explicit in papers)
- Intermediate claims: Accept F1 ≥ 0.65 (some interpretation required)
- Theoretical claims: Accept F1 ≥ 0.55 (highly interpretive)

Credence calibration at 70% in-range is appropriate. This acknowledges that expert annotations have their own uncertainty.

**On Sprint Ordering**:

Correct to do Sprint 6-7 before 8-9. You need the ontologies in place before validation can be meaningful. **Do not skip ahead to Gold Standard testing without completing the environment ontology.** Otherwise you'll be validating a system that can't properly identify constructs.

---

### Dr. Marcia Bates

**Assessment**: Environment ontology is essential. Proposed structure is good but needs hierarchy.

**On 7.1 (Environment Taxonomy)**:

Your five top-level domains (spatial, natural, sensory, configurational, aesthetic) are appropriate. But the structure needs explicit hierarchy for inheritance:

```python
ENVIRONMENT_HIERARCHY = {
    "spatial": {
        "_parent": None,
        "_description": "Volumetric and geometric properties",
        "spatial.volume": {
            "_parent": "spatial",
            "_synonyms": ["ceiling height", "room volume", "volumetric capacity"],
            "_related": ["spatial.openness", "spatial.enclosure"]
        },
        "spatial.openness": {
            "_parent": "spatial",
            "_synonyms": ["open plan", "visual openness", "spaciousness", "expansiveness"],
            "_related": ["spatial.volume", "spatial.prospect"],
            "_antonym": "spatial.enclosure"
        },
        # ...
    }
}
```

**Key Addition: `_antonym` field**

If a belief is about "openness increases X" and another is about "enclosure increases X", these are **not** contradictions if openness and enclosure are antonyms. They're the same finding expressed differently.

Your conflict detection should check:
1. Are the environment features antonyms?
2. Are the effect directions opposite?
3. If both yes → same finding, not conflict

**Answer to Question 3 (Diversity Weighting)**:

> Equal weight for environment and outcome domains?

**No. Weight environment domains at 0.6, outcome domains at 0.4.**

Rationale: Environment features are the independent variables in CNFA research. A web that covers many environment features but few outcomes is still valuable (it's about architectural effects). A web that covers many outcomes but few environment features is less coherent (it's not really about architecture).

**On Terminology Tests**:

Your Test Set B (same words, different constructs) is the critical test. I recommend these specific pairs:

| Term | Meaning A | Meaning B | Should Separate? |
|------|-----------|-----------|------------------|
| "complexity" | Visual (facades) | Navigational (paths) | YES |
| "density" | People/area | Building/area | YES |
| "openness" | Visual | Social (to interaction) | YES |
| "restoration" | Attention | Stress | MAYBE (related constructs) |
| "nature" | Real plants | Photos of plants | YES (ecological validity) |

---

### Dr. Rachel Kaplan

**Assessment**: Plan addresses domain-specific concerns well. Paper selection needs refinement.

**On 9.1 (Gold Standard Papers)**:

The nominated papers are canonical, but the set is **too homogeneous**. All are from the nature/restoration cluster. Add diversity:

**Revised Test Corpus**:

| # | Paper | Domain | Why Included |
|---|-------|--------|--------------|
| 1 | Kaplan & Kaplan (1989) | ART | Foundational theory |
| 2 | Ulrich (1984) | SRT/Stress | Classic empirical |
| 3 | Berman et al. (2008) | ART | Experimental test |
| 4 | Appleton (1975) | Prospect-Refuge | Different theory |
| 5 | Kellert & Wilson (1993) | Biophilia | Hypothesis paper |
| **6** | **Evans & McCoy (1998)** | **Built environment** | **Non-nature focus** |
| **7** | **Stamps (2000)** | **Complexity/preference** | **Quantitative modeling** |
| 8 | [Null result - TBD] | Various | Null handling |
| 9 | [Lighting/acoustics paper] | Sensory | Expand beyond nature |
| 10 | [Wayfinding paper] | Configurational | Expand beyond nature |

Papers 6-7 and 9-10 ensure the test set isn't just "nature and stress." If the system only works for ART/SRT, that's a serious limitation we need to discover.

**On 8.3 (Ecological Validity)**:

Your categories are good, but add nuance:

```python
class EcologicalValidity(Enum):
    FIELD_NATURAL = "field_natural"       # Real environment, natural behavior
    FIELD_STRUCTURED = "field_structured" # Real environment, structured task
    LAB_VR = "lab_vr"                     # VR immersion
    LAB_VIDEO = "lab_video"               # Video walkthrough
    LAB_PHOTOS = "lab_photos"             # Static images
    LAB_ABSTRACT = "lab_abstract"         # No environment reference
```

Distinguish VR from video—VR has better validity evidence than video walkthroughs.

**Answer to Question 4 (Paper Selection)**:

> Are the 10 nominated papers appropriate? Substitutions?

**Substitute as marked above.** The original set was nature-heavy. A validation corpus must test whether the system generalizes beyond its strongest subdomain.

**On Expected Outputs for Kaplan (1989)**:

Your annotation example is correct. One addition:

```yaml
expected_constraints:
  - source: "art_directed_attention_fatigue"
    target: "art_nature_restoration"
    type: "supports"
    causal_direction: "forward"  # This is theoretical, so forward is justified
    expected_strength: [0.6, 0.8]

  # ADD THIS:
  - source: "art_nature_restoration"
    target: "SRT_stress_reduction"
    type: "analogical"  # Cross-theory bridge
    causal_direction: "unknown"  # Not established in this paper
    expected_strength: [0.3, 0.5]  # Weaker because analogical
```

The Kaplan paper should generate cross-theory bridges to SRT. If it doesn't, your extraction isn't capturing the intellectual context.

---

## Consensus Modifications

### Required Changes

1. **Add `MEDIATED` to CausalDirection** (Pearl)
2. **Add `PRECISION_BOUNDARY` to ConflictType** (Cartwright)
3. **Add `_antonym` field to environment ontology** (Bates)
4. **Replace 3-4 Gold Standard papers** with non-nature studies (Kaplan)
5. **Differentiate F1 thresholds by epistemic level** (Simon)

### Answers to Posed Questions

| Question | Answer | Rationale |
|----------|--------|-----------|
| Q1: Causal default | `CORRELATIONAL` for empirical, `UNKNOWN` for theoretical | Conservative approach |
| Q2: Overlap threshold | Any dimension mismatch blocks genuine contradiction | Scope differences explain divergence |
| Q3: Diversity weighting | 0.6 environment, 0.4 outcome | Environment features are the IVs |
| Q4: Paper selection | Substitute 4 papers per Kaplan's recommendations | Need domain diversity |
| Q5: Pass threshold | 0.7 overall; 0.75/0.65/0.55 by epistemic level | Match extraction difficulty |

### New Questions from Panel

1. **How will you handle papers that span multiple theories?** (e.g., a paper testing both ART and SRT predictions)
2. **What's the minimum paper count for meaningful LOO validation?** (We suggest N ≥ 30)
3. **Will you version the Gold Standard corpus?** (It should evolve as understanding improves)

---

## Final Recommendation

**Proceed with Sprints 6-9 as planned, incorporating the modifications above.**

The plan is sound. The key risks are:
1. Rushing past Sprint 6-7 to get to validation (don't—ontologies first)
2. Using a nature-heavy test corpus (diversify per Kaplan's suggestions)
3. Treating pass/fail as binary (track where the system succeeds and fails; both are informative)

**Re-review after Sprint 7**: Show us the environment ontology before proceeding to validation. If constructs aren't properly separated at that stage, the Gold Standard testing will be uninterpretable.

---

*Panel review complete. Plan approved with modifications.*
