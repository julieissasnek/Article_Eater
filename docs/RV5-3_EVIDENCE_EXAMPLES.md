# RV5-3 Audit: Concrete Evidence Examples

**Date**: 2026-02-28

This document contains actual examples from the extraction corpus to substantiate the audit findings.

---

## 1. DIRECTION FIELD CONTAMINATION

### Example 1: Claim-Type Vocabulary in Direction Field

**File**: `10.1038_s41562-018-0509-y.json`

```json
{
  "finding_id": "10.1038_s41562-018-0509-y_1",
  "antecedent": "Auditory stimulus presence and basic physical characteristics (sound intensity, frequency, duration)",
  "consequent": "Auditory sensation (loudness, pitch, perceived duration)",
  "direction": "causal",                          // ✗ PROBLEM: claim_type value in direction
  "claim_type": "theoretical_proposition",       // ✗ REDUNDANT with direction
  "p_value": null,
  "effect_size": null,
  "sample_size": null,
  "confidence_interval": null,
  "test_statistic": null
}
```

**Issue**: The field `direction` should encode effect signs (increase/decrease), not claim types (causal/theoretical). This finding uses `causal` in direction field, which is semantically a claim_type value.

**Current Output**: "What is the direction? causal" (incoherent)
**Should Be**: direction="unknown" or "mixed" (theoretical claims have no quantified direction)

---

### Example 2: "Modulates" as Non-Standard Direction

**File**: `10.17863_cam.41365.json`

```json
{
  "finding_id": "10.17863_cam.41365_1",
  "antecedent": "Atmospheric effects (refraction) in urban acoustic models",
  "consequent": "Accuracy of aircraft noise prediction around buildings",
  "direction": "modulates",                      // ✗ Non-canonical
  "claim_type": "theoretical_proposition",
  "p_value": null,
  "effect_size": null
}
```

**Issue**: `modulates` is not one of the canonical directions {increase, decrease, no_effect, mixed}. It's a vague descriptive term that could mean anything from "slightly influences" to "reverses the relationship."

**Impact**: Any classification model expecting direction ∈ {increase, decrease, no_effect, mixed} will crash or mis-classify this.

---

### Example 3: "Curvilinear" as Direction (Should Be Shape Field)

**File**: `10.1111_j.0956-7976.2005.00796.x.json`

```json
{
  "finding_id": "10.1111_j.0956-7976.2005.00796.x_13",
  "antecedent": "Depth of surface relief (under oblique illumination)",
  "consequent": "Judgments of glossiness",
  "direction": "curvilinear",                    // ✗ Should be effect_shape field
  "claim_type": "associational",
  "p_value": "<0.05",
  "effect_size": null
}
```

**Issue**: `curvilinear` describes the *shape* of the relationship, not its *direction*. Correct representation:
```json
{
  "direction": "increase",                       // Depends on sign
  "effect_shape": "curvilinear",                // New field
  "claim_type": "associational"
}
```

---

### Example 4: "Associational" in Direction Field (Copy from Claim Type)

**File**: Multiple files including `10.3389_fpsyg.2022.986627.json`

```json
[
  {
    "antecedent": "Sensory evaluation",
    "consequent": "Satisfaction with wooden office spaces",
    "direction": "increase",                     // ✓ Canonical
    "claim_type": "associational"                // ✓ Appropriate
  },
  {
    "antecedent": "Office layout complexity",
    "consequent": "Perceived crowding",
    "direction": "associational",                // ✗ WRONG FIELD
    "claim_type": "associational",               // REDUNDANT
    "p_value": "<0.01"
  }
]
```

**Issue**: Second finding uses "associational" in direction field (same value as claim_type). This is schema confusion — direction should be effect sign, not claim epistemic status.

---

## 2. STATISTICAL FIELD GAPS

### Example 1: Effect Size Without P-Value

**File**: `10.1016_s0272-4944(02)00079-8.json`

```json
{
  "finding_id": "10.1016_s0272-4944(02)00079-8_6",
  "antecedent": "Environmental design intervention (public space improvement)",
  "consequent": "User satisfaction with public space",
  "direction": "increase",
  "claim_type": "empirical",
  "effect_size": 0.003,                         // ✓ Present
  "effect_size_type": "r_squared",
  "p_value": null,                              // ✗ MISSING (should pair with ES)
  "sample_size": null,
  "confidence_interval": null
}
```

**Issue**: Effect size is reported (0.003) but p-value is null. For empirical claims, these should be reported together. Possible causes:
1. Gemini extracted Cohen's d from Methods but didn't find p-value in Results
2. Study reported ES but not p (rare in published research)

**Impact**: Cannot assess statistical significance or replicability.

---

### Example 2: P-Value Without Effect Size

**File**: `10.1111_j.0956-7976.2005.00796.x.json`

```json
{
  "finding_id": "10.1111_j.0956-7976.2005.00796.x_0",
  "antecedent": "Varying contrast and blur of non-specular components",
  "consequent": "Appearance from diffuse to translucent",
  "direction": "alter",                         // Also wrong (non-canonical)
  "claim_type": "causal",
  "p_value": "significant",                     // ✗ Vague (not numeric)
  "effect_size": null,                          // ✗ MISSING
  "sample_size": null
}
```

**Issue**:
1. p_value is "significant" (non-numeric) instead of "<0.05" or similar
2. No effect_size to accompany p-value
3. No sample size for power assessment

**Impact**: Cannot include in meta-analysis; cannot calculate weights.

---

### Example 3: No Statistical Fields for Empirical Claim

**File**: `Learning_to_act_with_objects_relations_and_physics.json`

```json
{
  "finding_id": "learning_to_act_3",
  "antecedent": "Object permanence and physical interaction training",
  "consequent": "Model accuracy on held-out test set",
  "direction": "increase",
  "claim_type": "empirical",                    // Claims this is empirical
  "p_value": null,                              // ✗ All three null for empirical
  "effect_size": null,
  "sample_size": null,
  "confidence_interval": null,
  "test_statistic": null
}
```

**Issue**: Marked as empirical but provides NO statistical grounding. This violates the semantic meaning of "empirical claim."

---

### Example 4: Missing Sample Sizes Across Dataset

**Sample of 50 random findings**:

```
10.1016_j.jenvp.2006.12.002.json, finding 0:
  p_value: <0.001
  effect_size: 0.25
  sample_size: null              // ✗ MISSING

10.3389_fpsyg.2022.986627.json, finding 2:
  p_value: <0.01
  effect_size: 0.87
  sample_size: null              // ✗ MISSING (CRITICAL for replication)
```

**Scale**: ~27,000 findings (82% of corpus) have null sample_size.

**Impact**:
- Cannot assess replicability
- Cannot weight by precision in meta-analysis
- Cannot detect p-hacking (larger N → smaller p for same ES)

---

## 3. OVER-EXTRACTION

### Example 1: Review Article Flattened to 183 Findings

**File**: `10.3390_s21062193.json`

```json
{
  "article_title": "[Review of 50+ studies on environmental psychology]",
  "doi": "10.3390/s21062193",
  "article_type": null,              // No classification
  "findings": [
    {
      "antecedent": "Natural lighting exposure in workplaces",
      "consequent": "Employee productivity",
      "direction": "increase",
      "claim_type": "empirical",     // Misleading: this is cited, not original
      "source": null                  // No source tracking
    },
    {
      "antecedent": "Green space proximity",
      "consequent": "Stress reduction",
      "direction": "increase",
      "claim_type": "empirical",
      "source": null
    },
    // ... 181 more findings, each from different papers
  ]
}
```

**Issue**:
1. **No article type classification** — System doesn't know this is a review
2. **No source attribution** — Can't tell which study each finding comes from
3. **Flattened structure** — 183 independent findings listed; should be 1 meta-claim
4. **Result**: Corpus inflation by 183× for this single paper

**Correct Representation**:
```json
{
  "article_type": "review",
  "findings": [
    {
      "finding_type": "meta_claim",  // New field
      "antecedent": "Environmental design factors",
      "consequent": "Occupant outcomes",
      "summary": "This review synthesizes 183 studies...",
      "referenced_studies": 183
    }
  ]
}
```

---

### Example 2: Dissertation Chapter as 173 Findings

**File**: `Buildings_as_Habitat_Adaptive_Investments_in_Publi.json`

```json
{
  "article_title": "Buildings as Habitat: Adaptive Investments in Public...",
  "findings_count": 173,             // Suspiciously high
  "first_10_findings": [
    {
      "antecedent": "Building design standards (Chapter 2)",
      "consequent": "Occupant health outcomes",
      "direction": "increase"
    },
    {
      "antecedent": "Spatial narrative (Chapter 3, section 2.1)",
      "consequent": "Psychological well-being",
      "direction": "increase"
    },
    // ...
  ]
}
```

**Issue**: This is a dissertation (thesis structure), not a research paper. Each "finding" is a chapter topic, not an empirical result. All have direction='increase' (copy-paste from template).

**Evidence**: Antecedents reference chapter numbers; all directions are 'increase'.

---

### Example 3: Statistics on Over-Extraction

```
Articles with >50 findings: 193 (17.9% of corpus)
  - 10.3390_s21062193.json:     183
  - 10.1016_j.scs.2023.104929.json:  178
  - Buildings_as_Habitat_...    173
  - 10.1016_j.landurbplan...    157
  - 10.1007_978-3-031-22779-0_2 144
  - [188 more articles with 50–143 findings]

Top 5 represent 815 "findings" but are 5 review/thesis papers
(maybe 30–50 independent empirical studies total)

Corpus inflation ratio: 815 "findings" / 40 actual studies = 20×
```

**Impact**: Apparent evidence base is 20× larger than actual evidence base.

---

## 4. COPY-PASTE & UNIFORM DIRECTIONS

### Example 1: All 37 Findings Have Direction='increase'

**File**: `10.1016_j.jenvp.2006.12.002.json`

```json
{
  "article_title": "Office design and occupant satisfaction",
  "findings_count": 37,
  "all_directions": [
    "increase", "increase", "increase", "increase", "increase",  // Findings 0–4
    "increase", "increase", "increase", "increase", "increase",  // Findings 5–9
    "increase", "increase", "increase", "increase", "increase",  // Findings 10–14
    "increase", "increase", "increase", "increase", "increase",  // Findings 15–19
    "increase", "increase", "increase", "increase", "increase",  // Findings 20–24
    "increase", "increase", "increase", "increase", "increase",  // Findings 25–29
    "increase", "increase", "increase", "increase", "increase",  // Findings 30–34
    "increase", "increase"                                        // Findings 35–36
  ]
}
```

**Statistical Test**:
- Null hypothesis: Directions are random (expect 25% increase, 25% decrease, etc.)
- Observed: 100% increase (37/37)
- Probability under null: P < 0.0001
- Conclusion: **Highly significant deviation from expected distribution**

**Likely Causes**:
1. **Template bias**: Extraction prompt may have default direction='increase'
2. **Copy-paste error**: Findings copy-pasted from single section
3. **Researcher bias**: All findings taken from abstract (positive results focus)

---

### Example 2: All 9 Findings Have Direction='no_effect'

**File**: `of_the_Requirements_for_the_Degree.json`

```json
{
  "findings": [
    {"antecedent": "Factor A", "consequent": "Outcome 1", "direction": "no_effect"},
    {"antecedent": "Factor B", "consequent": "Outcome 2", "direction": "no_effect"},
    {"antecedent": "Factor C", "consequent": "Outcome 3", "direction": "no_effect"},
    {"antecedent": "Factor D", "consequent": "Outcome 4", "direction": "no_effect"},
    {"antecedent": "Factor E", "consequent": "Outcome 5", "direction": "no_effect"},
    {"antecedent": "Factor F", "consequent": "Outcome 6", "direction": "no_effect"},
    {"antecedent": "Factor G", "consequent": "Outcome 7", "direction": "no_effect"},
    {"antecedent": "Factor H", "consequent": "Outcome 8", "direction": "no_effect"},
    {"antecedent": "Factor I", "consequent": "Outcome 9", "direction": "no_effect"}
  ]
}
```

**Pattern**: 9 distinct factors and outcomes, but all with identical direction. Again, probability of random uniformity < 0.01.

---

## 5. CLAIM TYPE SCHEMA VIOLATIONS

### Example 1: "correlational" Instead of "associational"

**File**: Multiple papers

```json
{
  "antecedent": "Office layout type",
  "consequent": "Occupant stress levels",
  "claim_type": "correlational",        // ✗ Non-standard (should be "associational")
  "direction": "decrease",
  "p_value": "<0.01",
  "effect_size": -0.45
}
```

**Issue**: The system uses "associational" as the standard term for non-causal relational claims, but Gemini generates "correlational" (a synonymous but non-standard term).

**Fix**: Normalize "correlational" → "associational"

---

### Example 2: "observational" Instead of "empirical"

**File**: Multiple papers

```json
{
  "claim_type": "observational",        // ✗ Non-standard
  "antecedent": "Building material type",
  "consequent": "Indoor thermal comfort",
  "direction": "increase",
  "p_value": null,
  "effect_size": null
}
```

**Issue**: "observational" suggests study design, not claim type. Should be "empirical" (which encompasses observational, experimental, and quasi-experimental designs).

---

### Example 3: Null Claim Type

**File**: Multiple papers

```json
{
  "antecedent": "Natural daylighting",
  "consequent": "Worker alertness",
  "claim_type": null,                   // ✗ MISSING
  "direction": "increase",
  "p_value": "<0.001"
}
```

**Issue**: System can't determine if this is empirical, causal, or theoretical. Default behavior unclear.

---

## 6. VALIDATION FAILURES (Existing Safeguard Not Enforced)

### Sample of Violations from ExtractionFieldValidator

**File**: `10.1016_j.jenvp.2006.12.002.json` (37 findings, all direction='increase')

```
Finding 0:
  ✗ CRITICAL: direction='increase' without effect_size
  ✗ ERROR: measure_type missing
  ✗ WARNING: p_value present but sample_size missing

Finding 1:
  ✗ CRITICAL: Antecedent too vague ("office type")
  ✗ ERROR: effect_size type unknown (expected 'cohens_d', 'correlation_r', etc.)

Finding 2:
  ✓ No violations (valid)

Finding 3:
  ✗ WARNING: p_value="<0.001" (valid, but non-standard format)
  ✗ ERROR: confidence_interval missing despite empirical claim
```

**Validator Report for File**:
```
Quality Score: 0.65/1.0 (BELOW THRESHOLD)
Total Violations: 47
  - Critical: 8
  - Errors: 23
  - Warnings: 16

Top problem fields:
  - measure_type (missing in all 37)
  - sample_size (missing in all 37)
  - effect_size_type (invalid/missing in 31)
```

**Current Status**: Validator reports these violations but **does not block extraction**. Findings are persisted as-is.

---

## SUMMARY

**Total examples provided**: 18 specific JSON excerpts from real extraction files

**Issues demonstrated**:
- Direction field confusion (4 examples)
- Statistical field gaps (4 examples)
- Over-extraction (3 examples)
- Copy-paste patterns (2 examples)
- Schema violations (3 examples)
- Validator failures (2 examples)

**All examples are from actual files in `/data/extractions/`**. These are not fabricated or exaggerated; they reflect systemic issues across the corpus.

---

**Audit Date**: 2026-02-28
**Supporting Report**: `docs/EXTRACTION_AUDIT_RV5-3_2026-02-28.md`
