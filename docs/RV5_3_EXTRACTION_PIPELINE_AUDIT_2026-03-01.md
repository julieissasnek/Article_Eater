# RV5-3 Extraction Pipeline Audit

**Date**: 2026-03-01
**Version**: RV5-3
**Overall Quality Score**: 7.35/10 (Rubric Level: 7-8)

---

## Executive Summary

This audit examines **1065 extraction articles** containing **33115 findings** extracted from the Article_Eater corpus. The pipeline shows **7-8 quality** with specific strengths and critical gaps.

### Quality Score Interpretation
- **9-10**: >95% proper fields, <5% vague antecedents, canonical directions everywhere
- **7-8**: >85% proper, <15% vague, minimal non-canonical
- **5-6**: >70% proper, issues exist but manageable
- **3-4**: Significant gaps, many fields missing
- **1-2**: Systemic quality issues

**Current Score 7.35 falls in Rubric 7-8.**

---

## 1. Antecedent Quality Analysis

### Overview
- **Total Antecedents Analyzed**: 33115
- **Vague Antecedents**: 115 (0.3%)
- **Specific/Measurable Antecedents**: 2280 (6.9%)
- **Neutral/Contextual**: 30720

### Vagueness Breakdown
Examples of vague patterns found:

- **vague_environment**: 53 occurrences
- **vague_high_level**: 48 occurrences
- **vague_increased_exposure**: 7 occurrences
- **vague_stimulus**: 3 occurrences
- **vague_study**: 3 occurrences
- **vague_positive_condition**: 1 occurrences

### Specificity Breakdown
Examples of specific/measurable patterns found:

- **specific_light_type**: 838 occurrences
- **specific_measurement**: 602 occurrences
- **specific_decibel**: 319 occurrences
- **specific_wavelength**: 226 occurrences
- **specific_condition**: 175 occurrences
- **specific_temperature**: 120 occurrences

### Sample Vague Antecedents (Random Sample)

1. **DOI**: 10.1002/ad.2031
   **Antecedent**: "Ambiguity and uncertainty in the environment/structure"
   **Category**: vague_environment

2. **DOI**: 10.1016/j.apergo.2006.04.009
   **Antecedent**: "dynamic lighting scenario (stimulating cool-white high-level light in morning, gradually warmer/lowe"
   **Category**: vague_high_level

3. **DOI**: 10.1037/e614362011-012
   **Antecedent**: "Very high listening level (above 85 phons)"
   **Category**: vague_high_level

4. **DOI**: 10.1073/pnas.1121254109
   **Antecedent**: "Territoriality expressed in the environment (hierarchy of recognized spaces, symbolic markers)"
   **Category**: vague_environment

5. **DOI**: 10.1371/journal.pone.0123783
   **Antecedent**: "Higher educational level (EEG cluster 2 participants)"
   **Category**: vague_high_level

6. **DOI**: 10.3390/biology13040220
   **Antecedent**: "sudden or unprecedented modifications to the environment"
   **Category**: vague_environment

7. **DOI**: ANature/IN/THE/SPACE/DESIGN/GUIDE/FOR/STRESS/RELIE
   **Antecedent**: "Lack of sensory stimulation and variety in the environment"
   **Category**: vague_environment

8. **DOI**: Beyond/the/Visual/The/Impacts/of/Urban/Soundscapes
   **Antecedent**: "High level of park activity (human activity and events)"
   **Category**: vague_high_level

9. **DOI**: Light/Dark/and/all/Thats/in/Between/Revisiting/the
   **Antecedent**: "visible electro-magnetic radiation reflected off the environment"
   **Category**: vague_environment

10. **DOI**: The/city/soundscape/and/the/brain
   **Antecedent**: "distance between the stimulus object and the person"
   **Category**: vague_stimulus


---

## 2. Direction Field Normalization

### Canonical Direction Coverage
- **Total Findings with Direction**: 32819
- **Canonical Values** (increase, decrease, no_effect, mixed): 32819 (99.1%)
- **Non-Canonical Values**: 0 (0.9%)
- **Null/Missing Direction**: 296 (0.9%)

### Non-Canonical Direction Values Found


### Assessment
**Status**: PASS
- Expected: ≥95% of directions should be canonical
- Current: 99.1%
- Non-canonical directions indicate extraction model drift or inconsistent labeling

---

## 3. Sample Size Coverage

### Statistics
- **Findings with sample_size populated**: 1460 (4.4%)
- **Findings with sample_size NULL**: 31655 (95.6%)

### Sample Size Distribution (Populated Fields Only)
- **Count**: 1460 findings
- **Mean**: 996.7
- **Stdev**: 5323.6
- **Min**: 1
- **Max**: 43021

### Assessment
**Status**: POOR
- Current coverage: 4.4%
- Empirical findings should have sample_size ~90%+ of the time
- Many null values suggest extraction skips this field for non-empirical findings (acceptable) or fails to extract from methods sections (problematic)

---

## 4. Claim Type Distribution

### Distribution

- **associational**: 8559 findings (25.8%)
- **causal**: 6082 findings (18.4%)
- **theoretical_proposition**: 5621 findings (17.0%)
- **narrative**: 4499 findings (13.6%)
- **synthesized**: 2606 findings (7.9%)
- **null**: 1717 findings (5.2%)
- **moderated**: 933 findings (2.8%)
- **qualitative_theme**: 677 findings (2.0%)
- **empirical_finding**: 546 findings (1.6%)
- **methodological**: 330 findings (1.0%)
- **empirical**: 169 findings (0.5%)
- **cited**: 131 findings (0.4%)
- **pooled_effect**: 99 findings (0.3%)
- **statistical**: 86 findings (0.3%)
- **claimed**: 70 findings (0.2%)
- **empirical_result**: 50 findings (0.2%)
- **proposed_indicator**: 50 findings (0.2%)
- **mediated**: 45 findings (0.1%)
- **empirical_generalization**: 34 findings (0.1%)
- **validation**: 30 findings (0.1%)
- **vote_count**: 29 findings (0.1%)
- **proposal**: 24 findings (0.1%)
- **empirical_observation**: 20 findings (0.1%)
- **synthesized_empirical_finding**: 20 findings (0.1%)
- **empirical_finding_confirms_proposition**: 19 findings (0.1%)
- **partial_mediated**: 17 findings (0.1%)
- **derived_guideline**: 15 findings (0.0%)
- **comparative**: 12 findings (0.0%)
- **design_implication**: 10 findings (0.0%)
- **literature_review_synthesis**: 10 findings (0.0%)
- **subgroup_effect**: 8 findings (0.0%)
- **descriptive**: 7 findings (0.0%)
- **simulated**: 7 findings (0.0%)
- **complete_mediated**: 6 findings (0.0%)
- **project_description**: 5 findings (0.0%)
- **prescriptive**: 4 findings (0.0%)
- **no_effect**: 4 findings (0.0%)
- **definition**: 4 findings (0.0%)
- **observational**: 3 findings (0.0%)
- **experimental_observation**: 3 findings (0.0%)
- **review_conclusion**: 3 findings (0.0%)
- **theoretical_critique**: 2 findings (0.0%)
- **review_summary_of_findings**: 2 findings (0.0%)
- **moderated_mediated**: 2 findings (0.0%)
- **historical**: 2 findings (0.0%)
- **qualitative**: 2 findings (0.0%)
- **limitation**: 1 findings (0.0%)
- **interpretive**: 1 findings (0.0%)
- **historical_context**: 1 findings (0.0%)
- **mixed**: 1 findings (0.0%)
- **NULL claim_type**: 537 (1.6%)

### Assessment
**Distribution Health**: BALANCED
- Top claim type represents 25.8% of corpus
- Expected: Multiple types represented, no single type >50%
- Current diversity: 50 distinct types

---

## 5. Effect Size and P-value Coverage

### Coverage Statistics
- **Findings with effect_size populated**: 7222 (21.8%)
- **Findings with p_value populated**: 10467 (31.6%)
- **Both populated**: 5497 (16.6%)
- **Neither populated**: 20923 (63.2%)

### Assessment
**Status**: POOR
- Effect size is critical for quantitative meta-analysis
- Current coverage: 21.8%
- P-value coverage: 31.6%
- **Gap**: 63.2% of findings have neither metric

---

## 6. Template Matching Coverage

### Statistics
- **Articles with template matches**: 980 / 1065 (92.0%)
- **Findings with template matches**: 29034 / 33115 (87.7%)
- **Average templates per matched finding**: 4.14

### Assessment
**Status**: EXCELLENT
- Template matching enables theory linking
- Current coverage: 87.7%
- Expected: >80% for theory-based extraction

---

## 7. Extraction Completeness by Article Type

### Summary by Article Type
| Article Type | Count | Findings | Vague % | Canonical Dir % | Sample Size % | Effect Size % |
|---|---|---|---|---|---|---|
| unknown | 277 | 9596 | 0.0% | 0.0% | 0.0% | 0.0% |
| empirical_v2 | 277 | 8729 | 0.0% | 100.0% | 11.1% | 0.0% |
| narrative_review | 115 | 4829 | 0.0% | 100.0% | 0.0% | 0.0% |
| conceptual_framework | 107 | 2482 | 0.0% | 100.0% | 0.0% | 0.0% |
| systematic_review | 50 | 1772 | 0.0% | 100.0% | 0.0% | 0.0% |
| theoretical | 44 | 831 | 0.0% | 100.0% | 0.0% | 0.0% |
| observational_field | 42 | 1351 | 0.0% | 100.0% | 0.0% | 0.0% |
| mixed_methods | 33 | 1389 | 0.0% | 100.0% | 100.0% | 100.0% |
| empirical_study | 17 | 338 | 0.0% | 100.0% | 0.0% | 0.0% |
| case_study | 17 | 362 | 0.0% | 100.0% | 0.0% | 22.2% |
| methods | 13 | 288 | 0.0% | 100.0% | 0.0% | 0.0% |
| thought_piece | 10 | 153 | 0.0% | 100.0% | 0.0% | 0.0% |
| other | 10 | 244 | 2.6% | 100.0% | 0.0% | 55.3% |
| interview_study | 8 | 97 | 0.0% | 100.0% | 0.0% | 0.0% |
| empirical | 7 | 39 | 14.3% | 0.0% | 0.0% | 100.0% |
| phenomenological | 7 | 51 | 0.0% | 100.0% | 0.0% | 0.0% |
| meta_analysis | 5 | 85 | 0.0% | 100.0% | 0.0% | 93.3% |
| original_research | 4 | 161 | 0.0% | 100.0% | 0.0% | 22.5% |
| grounded_theory | 3 | 23 | 0.0% | 100.0% | 0.0% | 0.0% |
| review | 3 | 22 | 0.0% | 0.0% | 0.0% | 100.0% |
| None | 3 | 31 | 0.0% | 100.0% | 0.0% | 0.0% |
| quasi_experiment | 2 | 21 | 0.0% | 100.0% | 0.0% | 28.6% |
| empirical_research | 2 | 94 | 0.0% | 100.0% | 0.0% | 0.0% |
| experimental_study | 2 | 23 | 0.0% | 100.0% | 0.0% | 27.3% |
| original_research_article | 1 | 20 | 0.0% | 100.0% | 0.0% | 40.0% |
| primary_research | 1 | 13 | 0.0% | 100.0% | 0.0% | 0.0% |
| research_article | 1 | 15 | 0.0% | 100.0% | 0.0% | 66.7% |
| scoping_review | 1 | 4 | 0.0% | 100.0% | 0.0% | 0.0% |
| research_report | 1 | 31 | 0.0% | 100.0% | 0.0% | 74.2% |
| essay | 1 | 9 | 0.0% | 100.0% | 0.0% | 0.0% |
| ethnographic | 1 | 12 | 0.0% | 100.0% | 0.0% | 0.0% |


### Quality Profiles by Type
**Empirical Studies** (should have: high sample_size %, high effect_size %)
**Synthesis/Review** (should have: moderate sample_size %, lower effect_size %)
**Theoretical** (should have: low sample_size %, minimal effect_size %)
**Qualitative** (should have: null sample_size expected, varied effect_size %)

---

## 8. Critical Problems Identified

### Problem Categories

#### A. Vague Antecedents (115 findings, 0.3%)
**Impact**: MEDIUM - Reduces specificity and reproducibility
- Example: "the environment" instead of "open-plan office with 45 dB noise"
- These make findings difficult to operationalize in new studies

#### B. Non-Canonical Directions (0 findings)
**Impact**: HIGH - Breaks downstream processing
- Non-canonical values prevent automated analysis
- Indicates extraction model drift or QA failure

#### C. Missing Sample Sizes (31655 findings, 95.6%)
**Impact**: MEDIUM - Blocks meta-analysis
- For empirical studies, sample_size should be near 100%
- Current gap suggests methods section parsing failures

#### D. Missing Effect Sizes (25893 findings, 78.2%)
**Impact**: HIGH - Blocks quantitative synthesis
- Effect size is critical for systematic review
- 63.2% have neither effect_size nor p_value

#### E. Low Template Matching (12.3% unmatched)
**Impact**: MEDIUM - Breaks theory linking
- Theory links require template matches
- Current coverage: 87.7%

---

## 9. Recommendations (Ranked by Impact)

### P1 (Critical) — Fix Direction Normalization
- **Action**: Audit all 0 non-canonical directions
- **Rationale**: Breaks automated pipeline
- **Effort**: 2-4 hours
- **Expected Impact**: +0.9% conformance

### P1 (Critical) — Recover Missing Effect Sizes
- **Action**: Retrace 25893 findings where extraction skipped effect_size
- **Rationale**: Required for meta-analysis
- **Effort**: 8-16 hours
- **Expected Impact**: +78.2% coverage

### P2 (High) — Improve Template Matching
- **Action**: Enhance template matching algorithm to reach >85% coverage
- **Rationale**: Currently 87.7%, expected >85%
- **Effort**: 4-8 hours
- **Expected Impact**: Enables theory linking for -886 additional findings

### P2 (High) — Reduce Vague Antecedents
- **Action**: Retrace 115 vague antecedents; add specific contextual details
- **Rationale**: 0.3% vagueness exceeds acceptable threshold
- **Effort**: 6-12 hours
- **Expected Impact**: +0.3% specificity

### P3 (Medium) — Improve Sample Size Coverage for Empirical Studies
- **Action**: Audit empirical articles; ensure methods/results sections parsed for N
- **Rationale**: 4.4% coverage is low for empirical work
- **Effort**: 4-6 hours
- **Expected Impact**: +85.6% for empirical subset

---

## 10. Detailed Findings Tables

### Non-Canonical Directions (Top 20)
| Direction | Count | % of Total |
|---|---|---|


### Claim Type Distribution (All Types)
| Claim Type | Count | % of Total |
|---|---|---|
| associational | 8559 | 25.85% |
| causal | 6082 | 18.37% |
| theoretical_proposition | 5621 | 16.97% |
| narrative | 4499 | 13.59% |
| synthesized | 2606 | 7.87% |
| null | 1717 | 5.18% |
| moderated | 933 | 2.82% |
| qualitative_theme | 677 | 2.04% |
| empirical_finding | 546 | 1.65% |
| methodological | 330 | 1.00% |
| empirical | 169 | 0.51% |
| cited | 131 | 0.40% |
| pooled_effect | 99 | 0.30% |
| statistical | 86 | 0.26% |
| claimed | 70 | 0.21% |
| empirical_result | 50 | 0.15% |
| proposed_indicator | 50 | 0.15% |
| mediated | 45 | 0.14% |
| empirical_generalization | 34 | 0.10% |
| validation | 30 | 0.09% |
| vote_count | 29 | 0.09% |
| proposal | 24 | 0.07% |
| empirical_observation | 20 | 0.06% |
| synthesized_empirical_finding | 20 | 0.06% |
| empirical_finding_confirms_proposition | 19 | 0.06% |
| partial_mediated | 17 | 0.05% |
| derived_guideline | 15 | 0.05% |
| comparative | 12 | 0.04% |
| design_implication | 10 | 0.03% |
| literature_review_synthesis | 10 | 0.03% |
| subgroup_effect | 8 | 0.02% |
| descriptive | 7 | 0.02% |
| simulated | 7 | 0.02% |
| complete_mediated | 6 | 0.02% |
| project_description | 5 | 0.02% |
| prescriptive | 4 | 0.01% |
| no_effect | 4 | 0.01% |
| definition | 4 | 0.01% |
| observational | 3 | 0.01% |
| experimental_observation | 3 | 0.01% |
| review_conclusion | 3 | 0.01% |
| theoretical_critique | 2 | 0.01% |
| review_summary_of_findings | 2 | 0.01% |
| moderated_mediated | 2 | 0.01% |
| historical | 2 | 0.01% |
| qualitative | 2 | 0.01% |
| limitation | 1 | 0.00% |
| interpretive | 1 | 0.00% |
| historical_context | 1 | 0.00% |
| mixed | 1 | 0.00% |


---

## 11. Comparison to Previous RV5 Audit

Historical trends (if previous audit data available):
- Previous RV5 quality score: [data needed]
- Improvement in vagueness: [data needed]
- Improvement in direction normalization: [data needed]
- Improvement in template coverage: [data needed]

**Note**: This is the first RV5-3 audit. Update this section in subsequent runs.

---

## 12. Recommendations for Next Steps

### Immediate (This Week)
1. Fix all 0 non-canonical directions
2. Identify bottleneck for effect_size extraction (25893 missing)
3. Sample 20 vague antecedents; identify extraction model issue

### Short-term (This Sprint)
1. Retrace 115 vague antecedents with human review
2. Enhance template matching from 87.7% to >85%
3. Audit sample_size extraction for empirical studies

### Medium-term (Next Sprint)
1. Implement automated vagueness detection in QA pipeline
2. Create extraction debugging logs to trace effect_size/p_value misses
3. Establish baseline metrics for continuous monitoring

---

## Conclusion

**Overall Assessment**: Rubric 7-8 (7.35/10)

The extraction pipeline has produced 33115 findings from 1065 articles with **mixed quality**:

✓ **Strengths**:
- 99.1% of directions are canonical (adequate)
- 87.7% of findings have template matches
- 1460 findings with quantifiable sample sizes

✗ **Critical Gaps**:
- 0 non-canonical direction values
- 25893 findings missing effect_size (78.2%)
- 115 vague antecedents (0.3%)

**Next Action**: Focus on P1 items (direction normalization, effect size recovery) before scaling extraction further.

---

**Generated**: 2026-03-01
**Auditor**: Claude Code (RV5-3)
**Data Source**: 1069 extraction JSON files from `data/extractions/`
