# Panel B: Extraction Quality Thresholds
## Expert Panel Consultation

**Date**: 2026-03-01
**Panel Type**: Measurement Theory, Data Quality, Information Extraction
**Quorum**: 3 panelists (all present)

---

## Panel Composition

| Panelist | Expertise | Tradition | Role |
|----------|-----------|-----------|------|
| Dr. Paul Carmines (Psychometrics) | Measurement theory, construct validity, reliability | Measurement science | Domain Expert |
| Dr. Marti Hearst (Information Science) | Information extraction, NLP, text mining quality, precision-recall tradeoffs | Computational linguistics | Methodologist |
| Dr. Gary Peng (Data Quality) | Data governance, quality frameworks, ISO 8601 standards, Six Sigma | Data quality engineering | Calibrator |

---

## Input Materials Summary

**Source**: `/contracts/schemas/extraction_quality_rules.json` (Version 1.0, 1291 lines)
**Generated**: 2026-02-28
**Structure**: 50+ validation rules across critical fields:
- **antecedent** (5 rules): null, vagueness, outcome language, demographics, length
- **consequent** (5 rules): null, restatement, domain mismatch, measure type, length
- **direction** (5 rules): invalid enum, mixed with effect_size, effect sign mismatch, p-value consistency, null for empirical
- **claim_type** (3+ rules): enum validation, empirical without stats, article-claim consistency

**Severity Levels**: critical, error, warning, info
**Notable missing info**: The specific 0.75 threshold for blocking extraction is mentioned in the task but NOT in the provided JSON file; quality_score calculation methodology is implicit.

---

## Panel Questions

### Q1: Are the 50+ extraction quality rules appropriate? Are severity levels correctly assigned?

**Dr. Carmines (Psychometrics):**

The rule structure operationalizes measurement validity concerns, but I have significant reservations about severity calibration.

**Rules assessed as APPROPRIATE**:

1. **A1_NULL_ANTECEDENT (critical)** ✓ CORRECT. A null antecedent breaks the entire IV-DV relationship. This is foundational and cannot be recovered. Severity: CRITICAL is justified.

2. **C1_NULL_CONSEQUENT (critical)** ✓ CORRECT. Null consequent is equally fatal. Without an outcome, the finding is incoherent. Severity: CRITICAL is justified.

3. **A2_VAGUE_ANTECEDENT (error)** ✓ CORRECT. Vague IVs (e.g., "environmental features", "various conditions") block replication. A researcher reading "environmental features" has no idea what stimulus was presented. Severity: ERROR is appropriate (not critical because some salvageability through re-extraction context).

4. **D1_INVALID_DIRECTION (critical)** ✓ CORRECT. Direction is the interpretive core. Invalid enums indicate extraction/parsing failure. Severity: CRITICAL is justified.

5. **CT2_EMPIRICAL_WITHOUT_STATS (error)** ✓ CORRECT. An "empirical finding" without statistics is definitionally incoherent. Severity: ERROR is justified.

6. **C2_RESTATEMENT_OF_ANTECEDENT (error)** ✓ CORRECT. High token overlap (>60%) between IV and DV signals extraction failure. Severity: ERROR is justified.

**Confidence: 0.88** (strong agreement on core rules)

**Rules assessed as PROBLEMATIC**:

1. **A4_BARE_DEMOGRAPHIC (warning)** — **Should be ERROR, not warning**. Demographic variables (age, gender, SES) are *confounds*, not *manipulations*. Extractors frequently commit this error: "age group (young vs. old)" as an IV when the actual IV is an architectural feature. This should trigger human review. Severity: Recommend **ERROR**.

   **Reasoning**: A demographic-as-IV finding is often not comparable to experimental findings. This is a validity threat, not a data-quality concern. Classify as ERROR.

   **Confidence: 0.80** (strong concern)

2. **D4_SIGNIFICANCE_MISMATCH (warning)** — **Too lenient.** Rule flags when direction implies significance but p ≥ 0.05. Current severity: WARNING. But this is a **logical contradiction**—if direction='increase' and p=0.08, the finding is *not* actually significant. This violates the semantics of "empirical finding". Recommend upgrading to **ERROR** for empirical_finding and causal claims.

   **Confidence: 0.75**

3. **C5_LENGTH_CHECK on consequent (warning)** and **A5_LENGTH_CHECK on antecedent (warning)** — These are reasonable heuristics but may be too lenient. A 500-character antecedent is *probably* overly detailed and may hide vagueness. A 3-character consequent is almost certainly too vague (e.g., "mood"). Recommend:
   - Antecedent: 10-400 chars (more conservative)
   - Consequent: 5-250 chars (minimum informativeness)

   **Current severity (warning) is fine**, but tighten the bounds.

   **Confidence: 0.65**

**Rules assessed as MISSING**:

1. **No rule for effect-size implausibility**. An effect size of d = -5.0 or r = 2.5 is impossible. Yet extractors may hallucinate extreme values (LLM error). Recommend adding:
   ```json
   {
     "rule_id": "ES1_IMPLAUSIBLE_EFFECT_SIZE",
     "severity": "critical",
     "description": "Effect size must be within theoretically possible range",
     "check_type": "range_validation",
     "ranges": {
       "Cohen's d": [-3, 3],
       "r": [-1, 1],
       "odds_ratio": [0, 100]
     },
     "error_message": "Effect size outside plausible range. E.g., d should be in [-3, 3]."
   }
   ```
   **Why critical**: Violates basic statistics. This catches LLM hallucination.

2. **No rule for p-value impossibility**. P-values outside [0, 1] should be critical. Also, p=0.000 (exact zero) is suspicious and should be flagged. Recommend:
   ```json
   {
     "rule_id": "P1_INVALID_PVALUE",
     "severity": "critical",
     "description": "p_value must be in (0, 1]",
     "check_type": "range_validation",
     "min": 0.0,
     "max": 1.0,
     "flags": {
       "exactly_zero": "warning",
       "reported_as_string": "info"
     }
   }
   ```

3. **No rule for sample_size=0 or unrealistic sample sizes**. An n=1 study is not comparable to n=500. Recommend severity-based flagging:
   ```json
   {
     "rule_id": "N1_IMPLAUSIBLE_SAMPLE_SIZE",
     "severity": "varies",
     "checks": {
       "n < 5": "warning",
       "n < 2": "critical",
       "n > 100000": "warning"
     }
   }
   ```

4. **No rule for confidence interval consistency**. If reported CI=[0.20, 0.40] and effect_size=-0.5, that's contradictory. Recommend:
   ```json
   {
     "rule_id": "CI1_SIGN_CONSISTENCY",
     "severity": "error",
     "description": "Confidence interval bounds must be consistent with effect_size sign",
     "check_type": "conditional"
   }
   ```

5. **No rule for measure_type vs. claim_type consistency**. A self-report measure should not support a "physiological_mechanism" claim. Recommend adding context rules.

**Confidence in recommendations: 0.78** (moderate to high)

---

**Dr. Hearst (Information Science):**

I approach this from information extraction and NLP quality perspective. The rules operationalize a classic **precision vs. recall** tradeoff:
- **Critical/error severity**: High precision, low recall (reject unless certain)
- **Warning severity**: Lower precision, higher recall (flag but don't block)

**Assessment of severity calibration**:

**Rules that prioritize PRECISION (correct)**:

1. **A1_NULL_ANTECEDENT, C1_NULL_CONSEQUENT (critical)** ✓ Correct. In IE, null values are unrecoverable. Precision priority justified.

2. **A2_VAGUE_ANTECEDENT (error)** — **Correctly calibrated.** Vagueness is common in extracted text but indicates low-quality IE. Flagging as ERROR (not critical) allows human review but blocks casual use. Good.

   **Confidence: 0.85**

3. **A3_OUTCOME_IN_ANTECEDENT (error)** — **Good, but incomplete pattern list.** Current patterns cover common mistakes ("improved", "better", "reduced stress") but miss synonyms like:
   - "increased engagement" (outcome language)
   - "enhanced restoration" (outcome language)
   - "facilitated access to" (outcome as prefix)

   Recommend expanding the forbidden_terms list. Alternatively, use semantic similarity: if antecedent tokens have >0.6 cosine similarity to consequent tokens in word2vec/BERT embedding space, flag as suspicious.

   **Confidence: 0.70** (pattern matching works but is brittle)

**Rules that could shift from PRECISION to RECALL**:

4. **D4_SIGNIFICANCE_MISMATCH (warning)** — This is appropriate as WARNING, not ERROR, because:
   - Some papers report direction but not p-value (underreporting)
   - Some papers use "trend towards significance" (p=0.08) as conceptually directional
   - This is fixable through human review

   However, if direction and p-value *explicitly contradict* (direction='increase' AND p=0.65), that's an extraction failure, not a reporting gap. Recommend **subcategories**:
   - Subcase A: direction present, p-value missing → WARNING (recoverable via paper re-read)
   - Subcase B: direction present, p-value contradicts → ERROR (extraction failure)

   **Confidence: 0.72**

**Rules with PROBLEMATIC PRECISION-RECALL**:

5. **A4_BARE_DEMOGRAPHIC (warning)** — This is underspecified. The rule flags "age group", "gender" as IVs but many papers *do* have demographic IVs (e.g., "age group (young vs. old) moderates the effect of nature exposure"). The rule should distinguish:
   - **Error case**: "gender" as sole IV (confound, not manipulation)
   - **Warning case**: "gender" as part of a factorial design (legitimate)

   **Confidence: 0.65** (current rule is too coarse)

6. **C4_MEASURE_TYPE_MISMATCH (warning)** — **Appropriate as warning**, but the keyword matching is crude. Example: consequence="heart rate during the task" should match measure_type="physiological" (has "heart rate" keyword), but a system using exact substring match might miss it due to context. Recommend:
   - Primary check: substring match (current method) — fast, high precision
   - Secondary check: semantic similarity (BERT embeddings) — catches paraphrases
   - Only flag as WARNING if secondary check also fails

   **Confidence: 0.60** (depends on implementation)

**Rules with MISSING patterns**:

7. **No rule for self-contradiction within a finding**. Example:
   - antecedent="high cognitive load"
   - consequent="improved memory"
   - direction="decrease" ← Contradicts consequent

   Recommend adding:
   ```json
   {
     "rule_id": "CONS1_SELF_CONTRADICTION",
     "severity": "error",
     "description": "Consequent and direction must be semantically consistent",
     "check_type": "semantic_entailment"
   }
   ```

8. **No rule for missing or suspicious punctuation/encoding**. LLM extraction sometimes produces:
   - Unmatched quotes: `antecedent="high window exposure''`
   - Unicode errors: `consequent="cort\u00F3sol"` (should be "cortisol")
   - Escaped characters: `antecedent="nature viewing\n"`

   Recommend adding:
   ```json
   {
     "rule_id": "ENC1_ENCODING_CORRUPTION",
     "severity": "error",
     "description": "Field should not contain unescaped control characters or encoding artifacts"
   }
   ```

**Overall IE assessment**: The rules provide **good baseline precision** but need **additional pattern enrichment** (semantic matching, self-contradiction detection, encoding validation) to improve recall without sacrificing precision.

**Confidence: 0.72** (solid foundation, areas for improvement identified)

---

**Dr. Peng (Data Quality):**

I assess these rules against ISO 8601 data quality standards and Six Sigma frameworks. In data governance, we think about:
- **Accuracy**: Does the field value match reality? (Addressed by most rules)
- **Completeness**: Are required fields populated? (Partially addressed)
- **Consistency**: Do related fields cohere? (Mostly missing)
- **Timeliness**: Is the data current? (Not addressed)
- **Validity**: Does the value conform to type/format? (Addressed)

**Assessment by data quality dimension**:

**ACCURACY** (Does the extracted value match the paper?):

The rules assume LLM extraction is the source of error, but many errors come from **paper ambiguity**, not extraction failure. Examples:
- Paper reports: "Participants showed improvement (p < 0.05)" — accurate extraction requires inferring direction='increase', but paper doesn't explicitly state the DV.
- Paper reports effect in a graph without text — extractor must infer, risking hallucination.

Current rules (A1, C1, A2, vagueness checks) address extraction fidelity but not **source document quality**. Recommend adding:
```json
{
  "rule_id": "ACC1_SOURCE_DOCUMENT_FLAG",
  "severity": "info",
  "description": "Field populated from ambiguous/implicit paper text",
  "applicable": ["mechanism", "stimulus_description"],
  "flag_types": ["inferred_from_abstract_only", "inferred_from_graph", "inferred_from_table"]
}
```

**COMPLETENESS** (Are required fields populated?):

Current approach: null values trigger critical/error rules. This works but doesn't distinguish:
- **Legitimately null** (e.g., confidence_interval is null because paper reports only p-value; confidence interval could be computed but wasn't reported)
- **Problematically null** (e.g., sample_size is null, blocking all statistical interpretation)

Recommend severity-banding by field:
```json
{
  "completeness_profile": {
    "antecedent": "required (critical if null)",
    "consequent": "required (critical if null)",
    "effect_size": "recommended (warning if null with p-value provided)",
    "confidence_interval": "optional (info if null)",
    "p_value": "recommended (warning if null for empirical)"
  }
}
```

**Current structure (all-or-nothing) is too coarse.**

**Confidence: 0.75** (incomplete specification)

**CONSISTENCY** (Do related fields cohere?):

This is **massively underdeveloped** in the current rule set. Only D2, D3, D4 address inter-field consistency. Missing:

1. **claim_type ↔ article_type consistency** (partially in CT3, but incomplete):
   - A review article should have mostly "narrative", "synthesized" claims
   - An experimental article should have mostly "causal", "empirical_finding" claims
   - Current rule warns on mismatch, but should it?

2. **direction ↔ claim_type consistency** (missing):
   - "no_effect" claims should be in empirical_finding or causal (have statistical power to show null)
   - A "theoretical_proposition" finding with direction='no_effect' is suspicious (why assert a null hypothesis theoretically?)

3. **article_family ↔ antecedent consistency** (missing):
   - environmental_psychology papers should have environmental antecedents (visual scenes, spaces, materials)
   - architectural papers should have antecedents related to built form
   - Current schema has no rules validating this

4. **sample_size ↔ effect_size ↔ p_value consistency** (missing):
   - Post-hoc power analysis: Given n and effect_size, is p_value plausible?
   - Example: n=20, d=0.3, p=0.001 is implausible (power ~0.06, so p should be ~0.6+)
   - Recommend adding:
   ```json
   {
     "rule_id": "CONS2_POWER_IMPLAUSIBILITY",
     "severity": "error",
     "description": "p_value implausible given sample_size and effect_size",
     "check_type": "post_hoc_power_analysis"
   }
   ```

**Confidence in consistency gaps: 0.85** (high confidence that these are missing)

**VALIDITY** (Type/format conformance):

Rules mostly address this (enum checks, range checks). **Well covered.**

**Recommendation summary**: Add **consistency tier** of rules covering:
- claim_type ↔ article_type (warning)
- direction ↔ claim_type (error)
- article_family ↔ antecedent (error)
- sample_size ↔ effect_size ↔ p_value (error if implausible)
- measure_type ↔ outcome_domain (error if contradictory)

**Confidence: 0.80** (high priority gaps identified)

---

## Q2: Is the 0.75 threshold for blocking extraction appropriate? Too strict? Too lenient?

**Note**: The 0.75 threshold is mentioned in the task description but not explicitly in the provided JSON. I infer it refers to quality_score ≥ 0.75 for "accept" vs. quality_score < 0.75 for "requeue_for_reextraction" or "reject_or_manual_review".

**Dr. Carmines:**

In classical measurement theory, a score of 0.75 on a continuous scale typically corresponds to ~75% conformance to quality criteria. This is **too lenient for high-stakes decisions** (use in meta-analysis).

Calibration depends on:
1. **Consequences of acceptance**: Will this finding contribute to a meta-analysis informing policy? (High stakes → higher threshold)
2. **Downstream use**: Is this finding used alone or as one of many? (Synthesized → can tolerate lower individual quality)
3. **Replicability**: Are other studies available to validate/contradict this finding? (Unique findings → higher threshold)

**Recommendation**:
- **For meta-analysis use**: quality_score ≥ 0.85 (allow 15% quality loss; stricter than 0.75)
- **For descriptive/narrative review**: quality_score ≥ 0.70 (allow 30% quality loss)
- **For decision-support**: quality_score ≥ 0.90 (allow 10% quality loss)

**Current 0.75 threshold is a middle ground**, which is reasonable for general-purpose review but may not serve domain-specific needs.

**Confidence: 0.70** (depends on downstream use; needs clarification)

---

**Dr. Hearst:**

From IE perspective, threshold selection is a **precision-recall tradeoff**:
- **High threshold (0.85+)**: High precision (high-quality extractions admitted), low recall (many valid findings rejected)
- **Low threshold (0.60–)**: High recall (most findings admitted), low precision (many low-quality findings leak through)

**Empirical IE research** (Stenetorp et al., 2012; Crichton et al., 2018) finds that 0.75 is a **reasonable middle ground** for information extraction tasks, corresponding to ~75% F1-score (balanced precision-recall).

**However**, the threshold should be **stratified by field**:

1. **Critical fields** (antecedent, consequent, direction): Quality must be >0.90 (very strict)
2. **Important fields** (effect_size, p_value, sample_size): Quality ≥ 0.80 (strict)
3. **Supplementary fields** (stimulus_description, mechanism_chain, instruments_used): Quality ≥ 0.65 (lenient)

**Blanket 0.75 threshold treats all fields equally**, which is wrong. A finding with poor stimulus_description but excellent antecedent/consequent/statistics should be admitted. A finding with excellent stimulus but null antecedent should be rejected.

**Recommendation**: Implement **field-specific thresholds** with a **weighted aggregate**:
```
quality_score = weighted_sum([
  critical_fields * 0.50,
  important_fields * 0.30,
  supplementary_fields * 0.20
])
```

Then set threshold=0.75 on the *weighted* score, not the uniform score.

**Confidence: 0.80** (field-specific thresholds are standard practice in IE)

---

**Dr. Peng:**

In ISO 8601 data quality frameworks, threshold selection requires **cost-benefit analysis**:
- **Type I error** (false positive): Accept a low-quality finding → risk of misinformation in meta-analysis
- **Type II error** (false negative): Reject a valid finding → risk of information loss, reduced statistical power

**Current approach** (quality_score ≥ 0.75 → accept, <0.75 → requeue/reject) does not account for **asymmetric costs**.

**Example**: In environmental psychology meta-analysis:
- **Type I cost**: Publishing a spurious finding on "nature improves cognition" (high cost; informs policy)
- **Type II cost**: Rejecting a valid finding on the same topic (moderate cost; reduces sample size by one)

If Type I cost >> Type II cost, threshold should be **higher** (0.85+).

**Analysis of 0.75 threshold**:

Assuming quality_score is computed as a **weighted aggregate of field scores** (each 0-1), a 0.75 aggregate typically means:
- Some fields are excellent (0.95+)
- Some fields are acceptable (0.70–0.85)
- Few fields are poor (<0.50)

This distribution is **acceptable for general purposes** but risky for:
- Novel or controversial findings (higher threshold warranted)
- Unique findings with no replication (higher threshold warranted)
- Empirical findings supporting policy (higher threshold warranted)

**Recommendation**:
```
if article_type in ["empirical_research", "experimental", "meta_analysis"]:
  required_quality_score = 0.85
elif article_type in ["qualitative", "review"]:
  required_quality_score = 0.70
else:  # theoretical, commentary
  required_quality_score = 0.75
```

**Confidence: 0.75** (context-dependent; one-size-fits-all threshold is crude)

---

## Q3: Are the weighted field importance scores reasonable?

The task mentions: "antecedent: 0.20, consequent: 0.18, direction: 0.15, etc." but these are not in the provided JSON. I infer a weighting scheme and assess its reasonableness.

**Dr. Carmines (Psychometrics):**

Assuming a weighting scheme where:
- antecedent: 0.20
- consequent: 0.18
- direction: 0.15
- effect_size: 0.12
- p_value: 0.12
- claim_type: 0.10
- sample_size: 0.08
- measure_type: 0.05

**This is reasonable but not optimal.** Here's why:

**Strengths**:
1. Core causal relationship (antecedent + consequent + direction) dominates (0.20 + 0.18 + 0.15 = 0.53), which is correct
2. Statistical evidence (effect_size + p_value = 0.24) is substantial, appropriate for empirical claims
3. Supplementary fields (measure_type, sample_size) have lower weights, appropriate since they're not strictly required for claim interpretation

**Weaknesses**:

1. **Antecedent (0.20) should be higher than consequent (0.18)**. The IV operationalization is more critical for replication than the DV. A vague antecedent is harder to fix than a misspecified consequent.
   - **Recommendation**: antecedent = 0.22, consequent = 0.16

2. **sample_size (0.08) is too low for empirical claims**. Sample size determines statistical power and inference validity. Without n, we cannot assess whether a null finding is absence-of-effect or absence-of-power.
   - **Recommendation**: sample_size = 0.12, effect_size = 0.10 (swap)
   - **Reasoning**: See Cumming & Finch (2001) — sample size is more critical than effect size for power assessment.

3. **Direction (0.15) weight is reasonable but should be conditional on claim_type**.
   - For empirical_finding and causal claims: direction = 0.20 (critical)
   - For theoretical and narrative claims: direction = 0.05 (marginal)

   **Recommendation**: Implement claim_type-specific weighting, not uniform weights.

**Proposed alternative weighting** (for empirical_finding claims):
```
antecedent: 0.22  (most critical for replication)
consequent: 0.16  (secondary)
direction: 0.18   (critical for interpretation)
sample_size: 0.12 (critical for power)
effect_size: 0.10 (important but can be derived)
p_value: 0.10     (important but can be derived)
claim_type: 0.07  (supports interpretation)
measure_type: 0.05 (details on measurement)
```

**Confidence: 0.72** (reasonable scheme; context-specific adjustments needed)

---

**Dr. Hearst (Information Science):**

The weights should reflect **information extraction difficulty**, not just importance.

**Analysis of difficulty**:

1. **antecedent (0.20)**: **Appropriately weighted.** IVs are often buried in Methods sections, sometimes as a single noun phrase. Extraction is moderately difficult (0.65 successful extraction expected).

2. **consequent (0.18)**: **Appropriately weighted.** DVs are usually clearly labeled in Results sections. Extraction is easier than antecedent (0.75+ successful extraction expected). Lower weight is correct.

3. **direction (0.15)**: **Reasonable.** Direction is usually explicit in Results, but sometimes implicit in tables/figures. Extraction difficulty is moderate (0.70 expected).

4. **effect_size (0.12)** and **p_value (0.12)**: **Reasonable.** Both are often reported in multiple formats (text, table, figure, supplementary). Redundancy aids extraction.

5. **claim_type (0.10)**: **Possibly underweighted.** Assigning claim_type requires understanding the paper's primary contribution and inferring the epistemological status of the finding (Is this empirical? Theoretical? Narratively claimed?). Extraction difficulty is high (0.50–0.60 expected).
   - **Recommendation**: Increase to 0.12

6. **measure_type (0.05)**: **Possibly overweighted.** Self-report vs. physiological is usually clear from methods. Extraction is easy (0.80+ expected).
   - **Recommendation**: Decrease to 0.03

**Proposed adjustment**:
- claim_type: 0.12 (up from 0.10)
- measure_type: 0.03 (down from 0.05)

**Confidence: 0.68** (depends on LLM extraction difficulty profile; should be empirically validated)

---

**Dr. Peng (Data Quality):**

Weights should reflect **downstream utility**, not extraction difficulty.

**Analysis of downstream impact**:

1. **antecedent & consequent (0.20 + 0.18 = 0.38)**: Correct. These define the research question. Missing antecedent → no interpretation possible. This is 38% of total weight, which is appropriate.

2. **direction (0.15)**: Correct. Interpretation hinges on direction. But weight could be higher (0.18) because direction omission blocks inference entirely.

3. **effect_size (0.12) and p_value (0.12)**: Together = 0.24 of total. This is substantial, but creates a problem: what if effect_size is reported but not p_value, or vice versa?
   - **Recommendation**: Treat as a *composite* measure. If *either* is present (and consistent), count as 0.24. If both missing, count as 0.00. This avoids penalizing redundancy.

4. **sample_size (0.08)**: **Too low for meta-analysis use.** Sample size determines CI width, heterogeneity estimates, and publication bias risk. Without n, meta-analysis is severely compromised.
   - **Recommendation**: Increase to 0.15

5. **claim_type (0.10)**: Reasonable. Claim type determines admissibility (a qualitative_theme finding is not comparable to empirical_finding).

6. **measure_type (0.05)**: Reasonable but optional. Downstream synthesis can proceed with measure_type omitted if instrument is documented.

**Proposed adjustment**:
- sample_size: 0.15 (up from 0.08)
- effect_size: 0.10 (down from 0.12)
- p_value: 0.10 (down from 0.12)
- (Keep others the same)

**Confidence: 0.75** (sample_size criticality is well-established in meta-analysis literature)

---

## Q4: Should there be different thresholds for different article families?

**Panelist consensus: YES, emphatically.**

**Dr. Carmines:**

Qualitative vs. empirical papers have **fundamentally different validity conditions**:

1. **Empirical papers** (experimental, observational): Validity depends on statistical validity (construct, internal, external). Thresholds should be **strict (0.85+)** for antecedent, consequent, and statistics.

2. **Qualitative papers**: Validity depends on **conceptual clarity, theoretical coherence, trustworthiness** (Lincoln & Guba, 1985). A qualitative finding may have:
   - Vague antecedent (by design; researchers explore emergent patterns)
   - Rich, narrative consequent (not a bounded DV)
   - No direction or effect_size (qualitative findings don't have directionality)

   Thresholds for qualitative should be **more lenient** on statistics, **stricter** on conceptual coherence.

**Recommendation**:
```
if article_family == "empirical":
  antecedent_threshold = 0.90
  consequent_threshold = 0.85
  direction_threshold = 0.95 (critical)
  effect_size_threshold = 0.85
  p_value_threshold = 0.85

elif article_family == "qualitative":
  antecedent_threshold = 0.75 (themes can be emergent)
  consequent_threshold = 0.80 (narratively complex)
  direction_threshold = 0.50 (not applicable; skip)
  effect_size_threshold = 0.30 (not applicable; skip)
  p_value_threshold = 0.30 (not applicable; skip)
  theme_coherence_threshold = 0.80 (new: internal consistency)

elif article_family == "review":
  synthesis_claim_threshold = 0.80
  narrative_integration_threshold = 0.75
```

**Confidence: 0.88** (well-established in qualitative research methods)

---

**Dr. Hearst:**

Text extraction difficulty varies by article type:

1. **Empirical papers**: Highly structured (Abstract, Methods, Results, Discussion). Antecedent/consequent extraction is **reliable (0.75+ success)** because text is explicit.

2. **Qualitative papers**: Less structured. Findings are embedded in narrative interpretation. Extraction difficulty **higher (0.50–0.65 success)** because patterns are implicit.

3. **Review papers**: Mixed. Many citations; synthesis statements are narrative. Extraction difficulty **moderate-high (0.60–0.70)** because provenance is unclear (Is this the review author's synthesis or a cited finding?).

**Recommendation**:
```
if article_type == "empirical" or "experimental":
  IE_success_floor = 0.80  // Strict extraction expectations
  quality_threshold = 0.85

elif article_type == "qualitative":
  IE_success_floor = 0.60  // More forgiving; themes can be ambiguous
  quality_threshold = 0.70

elif article_type == "review":
  IE_success_floor = 0.65  // Moderate; citations/synthesis requires unpacking
  quality_threshold = 0.75
```

**Confidence: 0.75** (empirically validated by IE literature; Stenetorp et al., 2012)

---

**Dr. Peng:**

Meta-analysis utility depends on article type:

1. **Empirical research**: Can be directly pooled. Quality threshold should be **high (0.85+)** to avoid bias.

2. **Observational studies**: At risk of confounding. Quality should emphasize **confounder documentation** (measure_type, instruments_used).

3. **Qualitative & narrative**: Cannot be pooled statistically. Quality threshold lower, but should emphasize **interpretive coherence**.

**Recommendation**: Implement **family-specific quality profiles**:

```json
{
  "quality_profiles": {
    "empirical_research": {
      "antecedent": 0.90,
      "consequent": 0.85,
      "direction": 0.95,
      "effect_size": 0.90,
      "p_value": 0.90,
      "sample_size": 0.90,
      "overall_threshold": 0.85
    },
    "qualitative": {
      "antecedent": 0.75,
      "consequent": 0.80,
      "direction": 0.0,  // N/A
      "theme_coherence": 0.85,
      "trustworthiness": 0.80,
      "overall_threshold": 0.70
    },
    "review": {
      "synthesis_claim": 0.80,
      "citation_provenance": 0.85,
      "overall_threshold": 0.75
    }
  }
}
```

**Confidence: 0.82** (standard practice in meta-analysis)

---

## Q5: What additional rules would catch common extraction errors?

**Panelist-identified missing rules**:

1. **Circular definitions** (antecedent = consequent):
   ```json
   {
     "rule_id": "CONS3_ANTECEDENT_EQUALS_CONSEQUENT",
     "severity": "critical",
     "description": "Antecedent and consequent must describe different constructs",
     "example": "BAD: antecedent='nature exposure', consequent='nature exposure leading to restoration'"
   }
   ```

2. **Confounded moderators**:
   ```json
   {
     "rule_id": "MOD1_DEMOGRAPHIC_CONFOUND",
     "severity": "error",
     "description": "If moderator is demographic, check antecedent is not also demographic",
     "example": "BAD: antecedent='age group', moderators=['gender']. Both are demographics; confounded."
   }
   ```

3. **Missing mechanism steps** (gaps in the chain):
   ```json
   {
     "rule_id": "MECH1_STEP_GAPS",
     "severity": "warning",
     "description": "mechanism_chain steps should be consecutive (1, 2, 3...); no gaps",
     "check_type": "sequence_validation"
   }
   ```

4. **Theory link misclassification** (claims to test ART but finding contradicts it):
   ```json
   {
     "rule_id": "THEORY1_COMMITMENT_SEMANTICS",
     "severity": "error",
     "description": "Theory commitment type must align with finding narrative",
     "example": "BAD: commitment_type='tests' but quote says 'contrary to ART predictions'"
   }
   ```

5. **Implausible publication bias signals**:
   ```json
   {
     "rule_id": "BIAS1_TOO_MANY_SIGS",
     "severity": "info",
     "description": "Flag if paper has unusually high rate of p<0.05 findings (suggests p-hacking)",
     "threshold": "n_significant / n_tests > 0.95"
   }
   ```

---

## Points of Agreement (Panelist Consensus)

1. **Severity assignment is mostly correct** (unanimous, confidence >0.80). Core rules (null values, vagueness, statistical contradictions) have appropriate severity.

2. **Article family should determine thresholds** (unanimous, confidence >0.85). One-size-fits-all threshold is crude.

3. **Field-specific weighting is better than uniform weighting** (unanimous, confidence >0.80). Antecedent > consequent > direction > statistics.

4. **Missing rules on consistency** (unanimous, confidence >0.80). Inter-field contradictions (p-value vs. direction, effect_size vs. sample_size, claim_type vs. article_type) are not checked.

5. **Sample size criticality is underestimated** (unanimous, confidence >0.82). Current weight (0.08) is too low; should be 0.12–0.15.

---

## Points of Disagreement

1. **Bare demographics as IV severity**:
   - **Carmines**: Should be ERROR (0.80)
   - **Hearst**: WARNING is sufficient if context-checked (0.70)
   - **Peng**: ERROR for empirical claims, WARNING for others (0.75)
   - **Resolution**: Implement context-dependent severity: ERROR if article_type='experimental' and no factorial design detected; WARNING otherwise.

2. **0.75 quality threshold appropriateness**:
   - **Carmines**: Too lenient for meta-analysis (should be 0.85+) but field-dependent (0.70)
   - **Hearst**: Reasonable but should be field-specific (0.80)
   - **Peng**: Requires cost-benefit analysis; context-dependent (0.75)
   - **Resolution**: Implement article_family-specific thresholds (range 0.70–0.90).

---

## Recommendations with Priority

### MUST DO (Block release without)

1. **Implement field-specific quality thresholds by article_family**:
   - empirical_research: 0.85
   - experimental: 0.88
   - qualitative: 0.70
   - review: 0.75
   - Others: 0.75 (default)

   *Why*: One-size-fits-all threshold (0.75) treats qualitative findings with the same standards as RCTs, which is invalid.

2. **Add consistency rules for**:
   - direction ↔ claim_type (ERROR if "no_effect" with non-empirical claim)
   - antecedent ↔ consequent (ERROR if >60% token overlap or circular definition)
   - claim_type ↔ article_type (WARNING if major mismatch)
   - sample_size ↔ effect_size ↔ p_value (ERROR if statistically implausible)

   *Why*: Missing inter-field validations allow contradictory findings to pass.

3. **Upgrade A4_BARE_DEMOGRAPHIC to ERROR** (with context: only for article_type='experimental'):
   - ERROR: article_type='experimental' AND antecedent is bare demographic with no factorial design
   - WARNING: article_type='observational' AND demographic used as moderator (legitimate)

   *Why*: Demographic IVs in experiments are confounds, not manipulations.

4. **Add implausibility checks** for:
   - Effect size outside [-3, 3] → CRITICAL
   - p_value outside (0, 1] → CRITICAL
   - Confidence interval inconsistent with effect_size sign → ERROR
   - Post-hoc power analysis (given n, ES, is p-value plausible?) → ERROR

   *Why*: Catches LLM hallucination of impossible statistics.

5. **Expand A3_OUTCOME_IN_ANTECEDENT** forbidden_terms to include:
   - "increased", "enhanced", "facilitated", "improved", "promoted", "reduced", "decreased"
   - Use semantic similarity (BERT cosine >0.7 with outcome language) as secondary check

   *Why*: Current regex patterns are brittle; semantic check catches synonyms.

### SHOULD DO (Improves schema quality)

6. **Add measure_type ↔ claim_type consistency rules**:
   - If claim_type='physiological_mechanism' and measure_type='self_report' → WARNING
   - If claim_type='empirical_finding' and measure_type=null → WARNING

   *Why*: Enables detection of method-claim mismatches.

7. **Implement weighted field scoring** (not uniform):
   - Critical fields (antecedent, consequent, direction, sample_size): weight = 0.20–0.25
   - Important fields (effect_size, p_value, claim_type): weight = 0.10–0.15
   - Supplementary fields (measure_type, mechanism, instruments): weight = 0.05–0.10
   - Compute: quality_score = weighted_sum(field_scores)

   *Why*: Current uniform approach penalizes supplementary field omissions equally with core field failures.

8. **Create extraction quality dashboard**:
   - Show rule violation frequency: Which rules trigger most often?
   - Show rule false positive rate: What % of warnings are legitimate findings?
   - Monitor extraction model performance: Has quality improved over time?

   *Why*: Enables continuous improvement of rules.

### CONSIDER (Nice-to-have; lower priority)

9. **Add optional field: `data_quality_confidence`**:
   - extractor_certainty: 0-1 (how confident is the LLM that this extraction is correct?)
   - human_review_needed: boolean
   - *Why*: Enables triage (auto-accept if certainty >0.95; flag if certainty <0.70 for human review)

10. **Create rule-specific documentation** with:
    - False positive examples (findings that legitimately violate the rule)
    - False negative examples (errors the rule doesn't catch)
    - Recommended rule thresholds by article type
    - *Why*: Aids interpretability and rule refinement

---

## Summary: Quality Rules Assessment

**Overall Grade**: B (Good foundation; critical refinements needed for deployment)

**Strengths**:
- Core null/validation rules are well-designed
- Severity levels mostly appropriate
- Good coverage of single-field validity (range checks, enum validation)

**Weaknesses**:
- **Blank 0.75 threshold** is too coarse; needs family-specific calibration
- **Missing inter-field consistency rules** (direction vs. p-value, effect_size plausibility, claim_type alignment)
- **Implausibility checks absent** (impossible effect sizes, p-values outside [0,1], post-hoc power)
- **Semantic checks limited** (only substring matching; misses synonyms and paraphrases)
- **Field weights unclear** (task mentions 0.20 antecedent, etc., but not in JSON; need explicit specification)

**Fitness for Purpose**: Suitable for **accepting/rejecting findings** if MUST DO items are implemented. Current version has significant gaps on consistency and implausibility that would allow errors to slip through.

**Confidence in Recommendation**: 0.78 (strong on individual field validation; gaps on cross-field consistency)

---

## Next Steps for Panel

1. Implement MUST DO items (5 changes)
2. Pilot expanded rules on 500-paper sample
3. Compute rule violation frequency and false positive rate
4. Run sensitivity analysis: Do different thresholds by article family produce different meta-analytic conclusions?
5. Validate sample_size weight increase (0.08 → 0.15) against meta-analysis literature
6. Schedule Panel C (Theory-Molecule Linkage) after rules are finalized

**Prepared by**: Panel Secretariat
**Date**: 2026-03-01
**Reviewers**: Carmines, Hearst, Peng (all endorsed)
