# RV5-5 Audit Remediation Checklist

**Generated**: 2026-02-28
**Target Remediation Score**: 7.0/10 (from current 3.5/10)
**Estimated Effort**: 40-60 hours (Tier 1 + Tier 2)

---

## TIER 1: CRITICAL PATH (BLOCKING)

### T1.1: Eliminate "Other" Category (12-16 hours)

**Current State**:
- 8,710 stimuli (37.8%) tagged as "other"
- No distinguishing features
- System is 38% non-functional by definition

**What To Do**:
```
[ ] Run unsupervised clustering on stimulus antecedent text
    - Tool: sklearn.cluster.KMeans or HDBSCAN
    - Input: 23,029 antecedent descriptions (lowercase, stemmed)
    - Output: 8-15 natural clusters

[ ] Qualitatively label discovered clusters
    - Manual review of top 30 stimuli per cluster
    - Assign interpretable cluster names
    - Document defining attributes

[ ] Cross-reference with current category schema
    - Which current categories align with clusters?
    - Which clusters represent new categories?
    - Are "other" stimuli concentrated in specific clusters?

[ ] Create new category schema
    - Merge similar clusters
    - Define cluster boundaries (keywords, examples)
    - Create contracts/stimulus_categories_v2.json

[ ] Re-tag all 8,710 "other" stimuli
    - Use updated schema
    - Record tagging confidence
    - Validate distribution (all categories should be <15% each)
```

**Success Criteria**:
- No category > 20% of total stimuli
- All categories have ≥100 representative stimuli
- "Other" category < 5% (residual only)

**Deliverable**: `data/stimulus_descriptions_from_articles_v2.json`

---

### T1.2: Operationalize "Primary Feature" Essentials (8-12 hours)

**Current State**:
- 8 equivalence classes with "primary_feature" as sole essential attribute
- 7,668 stimuli affected
- Unmeasurable

**Classes to Fix**:
1. other_unclassified (4,601)
2. acoustic_soundscape (1,858)
3. space_ceiling (915)
4. thermal_comfort (283)
5. complexity_clutter_organization (257)
6. [3 others with ~100-300 each]

**What To Do** (per class):
```
[ ] Select 10 representative stimuli (stratified sample)

[ ] Conduct expert card sort
    - 2-3 domain experts
    - Task: "What makes these stimuli equivalent?"
    - Record shared dimensions
    - Record disagreements

[ ] Document discovered attributes
    - Which attributes appear across all 10 stimuli?
    - Which attributes appear in >50% of stimuli?
    - Which attributes vary widely?

[ ] Update decision_tree_equivalence_classes.json
    - Replace "primary_feature" with concrete attributes
    - Document card sort process
    - Update equivalence_class_definition

[ ] Validate against representative_stimuli
    - Do all representative stimuli possess the new essential attributes?
    - If not, either: (a) remove stimulus, or (b) revise essential attributes
```

**Success Criteria**:
- Zero classes with "primary_feature" as essential
- All essential attributes are measurable/verifiable
- Card sort inter-rater agreement ≥ 70%

**Deliverable**: `data/decision_tree_equivalence_classes_v2.json` + `docs/DECISION_TREE_CARD_SORTS.md`

---

### T1.3: Eliminate Circular Operationalizations (6-10 hours)

**Current State**:
- 32 of 116 outcome terms (27.6%) have circular operationalizations
- Operationalizations restate the construct name rather than measuring it

**Example Fixes**:

| Before | After |
|--------|-------|
| `"Attention" -> ["Attention Network Test (ANT)"]` | `"Attention" -> ["Reaction time to target detection under varying congruency conditions; ANT measures cost of incongruence"]` |
| `"Sleep" -> ["Sleep diary"]` | `"Sleep" -> ["Actigraphy or polysomnography; duration and quality from sleep logs"]` |
| `"Frustration" -> ["Frustration Discomfort Scale"]` | `"Frustration" -> ["Self-report of goal-blocking; Frustration Discomfort Scale measures intolerance of negative emotion"]` |

**What To Do**:
```
[ ] Identify all circular operationalizations (script: see below)

[ ] For each term with circular operationalization:
    [ ] Research the canonical measurement approach
        - Academic papers, textbooks, measurement handbooks
        - PubMed, PsycINFO, Google Scholar

    [ ] Write substantive operationalization
        - Include: what is measured, how it is measured, what score means
        - Avoid: restatement of construct name
        - Example: "Visual attention span; time to locate target among distractors"

    [ ] Validate against existing instruments
        - Does operationalization align with instruments listed?
        - If not, update instrument_ids or flag as discrepant

    [ ] Update outcome_vocab.json
```

**Validation Script**:
```python
# Identify circular operationalizations
for term in vocab['terms']:
    term_name = term['name'].lower()
    for op in term.get('operationalizations', []):
        if term_name in op.lower():
            print(f"CIRCULAR: {term_name} in {op}")
```

**Success Criteria**:
- Zero terms with construct name in operationalization text
- All operationalizations describe measurement method, not construct
- Operationalizations ≥ 80 characters (substantive)

**Deliverable**: `contracts/outcome_vocab/outcome_vocab_v2.json`

---

### T1.4: Merge Privacy Duplicates (2-3 hours)

**Current State**:
- `social.privacy` and `env.privacy` are the same construct
- Risk of double-counting in analysis

**What To Do**:
```
[ ] Analyze both Privacy entries
    - Social domain operationalizations (group, interpersonal)
    - Environmental domain operationalizations (spatial, perceptual)

[ ] Decide consolidation strategy
    Option A: Move to single domain (likely "perceptual" or "social")
    Option B: Create multi-level operationalizations

[ ] Update outcome_vocab.json
    - Consolidate entries
    - Create "domain_operationalizations" field (per-domain specificity)
    - Update cognates

[ ] Document decision
    - Why was it split originally?
    - Why consolidate?
    - Implications for existing data?
```

**Example Updated Entry**:
```json
{
  "term_id": "social.privacy",
  "name": "Privacy",
  "definition": "Ability to control access to self and personal information",
  "operationalizations": [
    "Interpersonal privacy: dyadic separation, personal space boundaries",
    "Environmental privacy: visual/acoustic enclosure, spatial opacity",
    "Privacy Satisfaction Scale (Likert rating)",
    "Behavioral: distance from others, door/window closure"
  ],
  "domain_operationalizations": {
    "social": "Interpersonal privacy in dyads/groups",
    "env": "Environmental perception of enclosure"
  }
}
```

**Success Criteria**:
- Single Privacy entry with multi-level operationalizations
- No ambiguity in data aggregation
- Cross-references updated

**Deliverable**: `contracts/outcome_vocab/outcome_vocab_v2.json` (updated)

---

## TIER 2: STRUCTURAL (IMPORTANT)

### T2.1: Create Category Boundary Rules (6-8 hours)

**Deliverable**: `contracts/category_boundaries.json`

**What To Do**:
```
[ ] For each of 13 stimulus categories:

    [ ] Define must-contain keywords
        Example for "plants_greenery":
        must_contain: ["plant", "vegetation", "green", "leaf", "flora"]

    [ ] Define must-NOT-contain keywords
        Example for "plants_greenery":
        must_not_contain: ["color", "artificial", "fabric", "photograph"]

    [ ] Define boundary cases (edge stimuli)
        Example: "green fabric" (color or plants?)
        Decision: if context is clearly color (interior design), -> color_material

    [ ] Provide 3-5 canonical examples per category

    [ ] Document rationale
        Why these boundaries? What are common mistakes?
```

**Structure**:
```json
{
  "categories": {
    "plants_greenery": {
      "description": "Living plants with visible foliage",
      "must_contain_one_of": ["plant", "vegetation", "greenery", "flora"],
      "must_contain_all_of": ["living", "foliage"],
      "must_not_contain": ["artificial", "fabric", "paint", "color_only"],
      "specificity_threshold": "Must mention specific plant/location, not just 'green'",
      "canonical_examples": [
        "Indoor potted plant at workstation",
        "Green wall in office",
        "Biophilic plants in hospital lobby"
      ],
      "boundary_cases": [
        {
          "stimulus": "Green-painted wall",
          "decision": "color_material (no living plants)",
          "rationale": "Color, not vegetation"
        },
        {
          "stimulus": "Photograph of forest",
          "decision": "views or nature (not plants_greenery)",
          "rationale": "Perception of nature, not actual plants"
        }
      ]
    }
  }
}
```

**Success Criteria**:
- All 13 categories have explicit boundaries
- Examples and counter-examples are clear
- Boundaries resolve common tagging confusion

**Deliverable**: `contracts/category_boundaries.json`

---

### T2.2: Limit Multi-Category Tags (4-6 hours)

**Current State**:
- 658 stimuli have 5+ categories
- 4,055 stimuli have 3+ categories (17.6%)

**What To Do**:
```
[ ] Identify all stimuli with ≥3 categories

[ ] For each stimulus:
    [ ] Question: Is this ONE antecedent or MULTIPLE antecedents?

        Example: "Distinctive personal living space (furniture, possessions,
                   rugs, pictures, wall decorations, lighting)"

        This is MULTIPLE antecedents:
        - Furniture (furniture_interior)
        - Pictures/wall decorations (art_decoration)
        - Lighting (lighting)

        Should be DECOMPOSED into 3 stimuli

    [ ] If decomposable: Create sub-stimuli
        S1: "Personal furniture in living space" -> [furniture_interior, building_type]
        S2: "Pictures and wall decorations" -> [art_decoration]
        S3: "Lighting in personal space" -> [lighting]

    [ ] If not decomposable: Keep 2 primary categories, document secondary as "related"

[ ] Update stimulus_descriptions_from_articles.json
    - Mark "decomposed" status
    - Track parent/child relationships
```

**Success Criteria**:
- 95%+ of stimuli have ≤2 categories
- Decomposed stimuli are semantically coherent
- No information loss (child stimuli account for all original antecedents)

**Deliverable**: `data/stimulus_descriptions_from_articles_v2.json` (updated)

---

### T2.3: Add Instrument Coverage Validation (3-4 hours)

**Current State**:
- 52 of 116 terms (44.8%) have instrument_ids
- 64 terms (55.2%) have no instruments

**What To Do**:
```
[ ] For each term without instrument_ids:

    [ ] Research canonical measurement approach
        - Academic sources, standard batteries
        - Outcome measurement literature

    [ ] Decide: Empirical or Theoretical?
        Empirical: "Can be measured; add instrument_ids"
        Theoretical: "Conceptual construct; cannot be directly measured"

    [ ] If empirical:
        [ ] Find ≥1 validated instrument
        [ ] Add to instrument_ids array

    [ ] If theoretical:
        [ ] Mark as "measurement_level": "theoretical"
        [ ] Do not use in empirical analyses

[ ] Update outcome_vocab.json with measurement_level field
```

**Example Updated Entry**:
```json
{
  "term_id": "spatial.wayfinding",
  "name": "Wayfinding",
  "measurement_level": "empirical",
  "operationalizations": [
    "Time to locate target destination",
    "Number of errors/wrong turns",
    "Self-report navigation confidence"
  ],
  "instrument_ids": ["WFES", "WAYFINDING_TIME", "SPATIAL_COGNITION_QUESTIONNAIRE"]
}
```

**Success Criteria**:
- All empirical terms have ≥1 instrument_id
- Theoretical terms are explicitly marked
- No ambiguous terms

**Deliverable**: `contracts/outcome_vocab/outcome_vocab_v2.json` (updated)

---

## TIER 3: REFINEMENT (OPTIONAL)

### T3.1: Add Category Confidence Scores (4-6 hours)

For each stimulus, add:
```json
{
  "antecedent": "...",
  "categories": ["lighting", "color_material"],
  "category_confidence": [0.95, 0.75]  // NEW
}
```

Score interpretation:
- 0.90-1.00: Unambiguous category assignment
- 0.70-0.89: Clear, but some related categories possible
- 0.50-0.69: Borderline; needs human review
- <0.50: Not recommended for analysis

### T3.2: Cognate-Instrument Alignment Audit (3-4 hours)

For each term with cognates:
```python
cognates = ["focus", "concentration"]
instruments = ["ANT", "OSPAN"]

# Validate: Do cognates have compatible instruments?
# Or: Are we calling different constructs by the same name?
```

---

## Quick Validation Checklist (Post-Remediation)

Before declaring audit remediation complete:

- [ ] **Stimuli Distribution**: No category > 20%, < 5% "other"
- [ ] **Operationalizations**: Zero contain construct name (search validation)
- [ ] **Essential Attributes**: All are measurable/concrete; zero "primary_feature"
- [ ] **Duplicates**: No construct appears in 2+ domains without explicit merger
- [ ] **Category Boundaries**: Explicit rules for all 13+ categories
- [ ] **Instruments**: All empirical terms have ≥1 instrument_id
- [ ] **Data Integrity**: All JSON files validate; no missing fields

---

## Effort Breakdown (Revised Estimate)

| Tier | Task | Hours | Priority |
|------|------|-------|----------|
| 1 | Eliminate "Other" | 12-16 | CRITICAL |
| 1 | Operationalize Primary Feature | 8-12 | CRITICAL |
| 1 | Eliminate Circular Ops | 6-10 | CRITICAL |
| 1 | Merge Privacy | 2-3 | CRITICAL |
| 2 | Category Boundaries | 6-8 | IMPORTANT |
| 2 | Limit Multi-tags | 4-6 | IMPORTANT |
| 2 | Instrument Coverage | 3-4 | IMPORTANT |
| 3 | Confidence Scores | 4-6 | OPTIONAL |
| 3 | Cognate Alignment | 3-4 | OPTIONAL |
| | **TOTAL** | **48-69 hours** | |

---

**Report Version**: RV5-5 Remediation
**Generated**: 2026-02-28
**Next Review**: Post-T1 completion (target: 2 weeks)
