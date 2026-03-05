# Forensic Analysis: Supporting Data Tables

**Date**: March 5, 2026
**Analysis Date**: 2026-03-05
**Data Source**: 1,064 extractions, 33,116 findings

---

## TABLE 1: SAMPLE SIZE EXTRACTION (20 Empirical Papers)

| # | DOI (first 35 chars) | Type | Findings | Finding_SS | % | Paper_SS |
|---|---|---|---|---|---|---|
| 1 | 10.1016/j.ergon.2011.09.004 | empirical_v2 | 37 | 1 | 3% | Yes |
| 2 | 10.1007/s00226-021-01320-7 | empirical_v2 | 36 | 0 | 0% | Yes |
| 3 | 10.1103/physrevlett.110.195901 | empirical | 4 | 0 | 0% | No |
| 4 | 10.1080/10630732.2023.2289144 | empirical_v2 | 37 | 2 | 5% | Yes |
| 5 | 10.1073/pnas.1418490112 | empirical_v2 | 11 | 2 | 18% | Yes |
| 6 | 10.1016/j.jobe.2023.106776 | empirical_v2 | 27 | 0 | 0% | No |
| 7 | 10.1016/j.cub.2013.07.004 | empirical_study | 4 | 4 | 100% | Yes |
| 8 | [Integration paper] | empirical_v2 | 18 | 13 | 72% | No |
| 9 | 10.1016/j.buildenv.2024.111293 | empirical_v2 | 21 | 0 | 0% | No |
| 10 | [Requirements paper] | empirical_v2 | 9 | 1 | 11% | No |
| 11 | 10.3389/fnhum.2015.00514 | empirical_v2 | 14 | 4 | 29% | Yes |
| 12 | 10.1007/s11406-017-9817-0 | empirical_v2 | 33 | 0 | 0% | Yes |
| 13 | 10.1007/s11229-021-03156-x | empirical_v2 | 47 | 1 | 2% | Yes |
| 14 | 10.1016/j.buildenv.2025.113254 | empirical_v2 | 36 | 0 | 0% | No |
| 15 | 10.1068/p5262 | empirical_v2 | 30 | 0 | 0% | Yes |
| 16 | 10.1080/00140130903154579 | empirical_v2 | 56 | 2 | 4% | Yes |
| 17 | 10.1006/jevp.2001.0221 | empirical_study | 35 | 1 | 3% | Yes |
| 18 | 10.1007/s00226-022-01419-5 | empirical_v2 | 26 | 2 | 8% | Yes |
| 19 | [Physiological benefits] | empirical_v2 | 14 | 0 | 0% | No |
| 20 | 10.1037/xap0000024 | empirical_v2 | 39 | 0 | 0% | No |

**Summary**:
- Average finding-level coverage: 12.7%
- Papers with paper-level sample_size: 12/20 (60%)
- Range: 0% to 100%
- Median: 0% (most papers have 0% finding-level SS)

**Global Empirical Statistics**:
- Total empirical findings: 9,200
- With sample_size: 1,226 (13.3%)

---

## TABLE 2: EFFECT SIZE COVERAGE BY CLAIM TYPE

**Note**: Sample from 20 papers with 3+ findings each

| Claim Type | Count | With_ES | With_P | With_Any_Stat | With_No_Stat |
|---|---|---|---|---|---|
| empirical_finding | 0 | 0 | 0 | 0 | 0 |
| associational | n | n | n | n | n |
| other types | n | n | n | n | n |

*Sample shows no findings classified as "empirical_finding" in sampled papers*

**Global Coverage (all 33,116 findings)**:
- With effect_size: ~8,093 (24.4%)
- With p_value: ~10,234 (30.9%)
- With ANY statistics: ~11,050 (33.4%)
- With NO statistics: ~22,066 (66.6%)

---

## TABLE 3: ARTICLE TYPE DISTRIBUTION (n=1,064)

| Article Type | Count | % | Family |
|---|---|---|---|
| empirical_v2 | 277 | 26.0 | empirical |
| narrative_review | 115 | 10.8 | synthesis |
| conceptual_framework | 107 | 10.1 | theoretical |
| unknown | 279 | 26.2 | unknown |
| systematic_review | 50 | 4.7 | synthesis |
| theoretical | 44 | 4.1 | theoretical |
| observational_field | 42 | 3.9 | empirical |
| mixed_methods | 33 | 3.1 | empirical |
| empirical_study | 17 | 1.6 | empirical |
| case_study | 17 | 1.6 | qualitative |
| methods | 13 | 1.2 | methods |
| thought_piece | 10 | 0.9 | theoretical |
| other | 10 | 0.9 | other |
| interview_study | 8 | 0.8 | qualitative |
| empirical | 7 | 0.7 | empirical |
| phenomenological | 7 | 0.7 | qualitative |
| meta_analysis | 5 | 0.5 | synthesis |
| original_research | 4 | 0.4 | empirical |
| grounded_theory | 3 | 0.3 | qualitative |
| review | 3 | 0.3 | synthesis |
| [20 other types] | 20 | 1.9 | mixed |

**Family Summary**:
- empirical: 396 (37.2%)
- unknown: 176 (16.5%)
- synthesis: 173 (16.3%)
- theoretical: 163 (15.3%)
- qualitative: 21 (2.0%)
- methods: 13 (1.2%)
- [other]: 6 (0.6%)

---

## TABLE 4: FINDING QUALITY TIER DISTRIBUTION

### Overall (n=33,116)

| Tier | Count | % | Requirement |
|---|---|---|---|
| A | 1,200 | 3.6% | antecedent + consequent + direction + effect_size + sample_size + p_value |
| B | 10,850 | 32.8% | antecedent + consequent + direction + (effect_size OR p_value) |
| C | 20,770 | 62.7% | antecedent + consequent + direction only |
| D | 296 | 0.9% | Missing antecedent/consequent/direction |

### By Article Type

| Type | A | B | C | D | Total | A% |
|---|---|---|---|---|---|---|
| empirical_v2 | 891 | 6,493 | 1,345 | 0 | 8,729 | 10.2% |
| unknown | 40 | 1,922 | 7,389 | 245 | 9,596 | 0.4% |
| narrative_review | 3 | 237 | 4,589 | 0 | 4,829 | 0.06% |
| conceptual_framework | 0 | 9 | 2,473 | 0 | 2,482 | 0.0% |
| systematic_review | 6 | 269 | 1,497 | 0 | 1,772 | 0.3% |
| mixed_methods | 84 | 715 | 590 | 0 | 1,389 | 6.0% |
| observational_field | 129 | 746 | 476 | 0 | 1,351 | 9.5% |
| mixed_methods (2) | 84 | 715 | 590 | 0 | 1,389 | 6.0% |
| theoretical | 0 | 0 | 822 | 9 | 831 | 0.0% |
| case_study | 23 | 65 | 275 | 0 | 363 | 6.3% |
| empirical_study | 6 | 149 | 183 | 0 | 338 | 1.8% |

**Key Insight**: Tier A very low across all types; empirical_v2 shows best performance at 10.2%

---

## TABLE 5: ANTECEDENT QUALITY RATINGS (n=30 sample)

| # | Antecedent (first 65 chars) | Length | Has_Numbers | Has_Units | Rating |
|---|---|---|---|---|---|
| 1 | direct experience of the outdoors | 8 | No | No | VAGUE |
| 2 | Sharp vs. curved contours in healthcare settings (objects... | 10+ | No | No | MODERATE |
| 3 | Visual - Grey ratio | 3 | No | No | VAGUE |
| 4 | Open plan environments with sufficient daylighting | 8 | No | No | VAGUE |
| 5 | Distance to goal (far) | 4 | Yes | No | VAGUE |
| 6 | Visual stimulation with wooden-wall images (all three ty... | 8 | No | No | MODERATE |
| 7 | Slowdown of global economy (during COVID-19) | 6 | No | No | MODERATE |
| 8 | Narrow (1/3 octave wide) 10-dB dip in TL curve | 8 | Yes | Yes | MODERATE |
| 9 | Male gender | 2 | No | No | VAGUE |
| 10 | Virtual Environment type (Immersive vs. Desktop) | 5 | No | No | MODERATE |
| [11-30] | [similar distribution] | — | — | — | — |

**Summary**:
- SPECIFIC: 0/30 (0%)
- MODERATE: 11/30 (36.7%)
- VAGUE: 19/30 (63.3%)

**Characteristics of MODERATE (better quality)**:
- Length: 8+ words
- Contains: contrasts, condition types, or measurement parameters
- Example: "Virtual Environment type (Immersive vs. Desktop VR)"

**Characteristics of VAGUE (poor quality)**:
- Length: <8 words
- No numbers, units, or specifics
- Example: "Male gender" or "Noise"

---

## TABLE 6: THEORY LINK VALUES (top 40)

| Theory Link | Count | % of Links | Type | Full Name (if known) |
|---|---|---|---|---|
| PP | 13,882 | 47.2 | CODE | Predictive Processing? |
| NM | 6,710 | 22.8 | CODE | Neurological Mismatch? |
| IC | 5,710 | 19.4 | CODE | Information Coherence? |
| DT | 4,510 | 15.3 | CODE | Data Type? |
| MSI | 3,349 | 11.4 | CODE | Multisensory Integration |
| DP | 3,058 | 10.4 | CODE | Data Pattern? |
| CB | 2,324 | 7.9 | CODE | Cognitive Behavior? |
| SN | 2,158 | 7.3 | CODE | Sensory Noise? |
| Biophilia | 2,147 | 7.3 | THEORY | Biophilia Hypothesis |
| SRT | 2,021 | 6.9 | CODE | Stress Recovery Theory? |
| MS | 1,874 | 6.4 | CODE | ? |
| EC | 1,768 | 6.0 | CODE | Environmental Control? |
| ART | 1,311 | 4.5 | CODE | Attention Restoration Theory |
| Privacy Regulation | 687 | 2.3 | THEORY | Privacy Regulation Theory |
| AX8 | 564 | 1.9 | CODE | ? |
| A8_Social | 557 | 1.9 | CODE | Architectural Type 8 Social |
| T20 | 525 | 1.8 | CODE | Template 20? |
| AX9 | 385 | 1.3 | CODE | ? |
| A9_Task_Cognition | 330 | 1.1 | CODE | Architectural Type 9 |
| Privacy | 326 | 1.1 | THEORY | Privacy |
| Prospect-Refuge | 267 | 0.9 | THEORY | Prospect-Refuge Theory |
| ACOUSTIC_EMOTION_MAPPING | 233 | 0.8 | THEORY | Acoustic Emotion Mapping |
| L1 | 218 | 0.7 | CODE | Layer 1? |
| COL1 | 215 | 0.7 | CODE | Color Type 1? |
| COL2 | 183 | 0.6 | CODE | Color Type 2? |
| A3_Spatial_Config | 173 | 0.6 | CODE | Architectural Type 3 |
| A6_Visual_Form | 161 | 0.5 | CODE | Architectural Type 6 |
| A10_Temporal | 142 | 0.5 | CODE | Architectural Type 10 |
| T74 | 99 | 0.3 | CODE | ? |
| ENCLOSURE_SAFETY | 97 | 0.3 | THEORY | Enclosure Safety |
| [10 more] | [<1% each] | — | — | — |

**Summary**:
- Total findings with theory_links: 29,397/33,116 (88.8%)
- Broad codes (2-3 chars): ~70% of findings use these
- Specific theories: ~30% use named theories like "Biophilia", "Privacy Regulation"
- Abbreviations dominate: "PP", "NM", "IC" = 89.4% of all links combined

---

## TABLE 7: EXTRACTION VERSION ANALYSIS

| Version | Count | % | Quality_Score_Avg |
|---|---|---|---|
| v3.0 | 1,010 | 94.9% | 0.732 |
| null | 51 | 4.8% | (N/A) |
| v3.0_gemini | 2 | 0.2% | (N/A) |
| v3.0_converted | 1 | 0.1% | (N/A) |

**Quality Improvement**:
- V3.0 average: 0.732
- Non-V3 average: 0.337
- Improvement: +0.395 (+117%)

**Surgical Update Coverage**:
- With surgical_update_at: 1,010/1,064 (94.9%)
- Interpretation: 95% of corpus updated by surgical quality pass

**Implication**: V3 extraction is significantly better than prior versions, but still has room for improvement (0.732 out of 1.0)

---

## TABLE 8: PROMPT VS TEMPLATE FIELD COVERAGE

| Field | Requested in V3 Prompt | Template Requires? | Status |
|---|---|---|---|
| **antecedent** | Yes (37 mentions) | Yes | ✓ COVERED |
| **consequent** | Yes (28 mentions) | Yes | ✓ COVERED |
| **direction** | Yes (44 mentions) | Yes | ✓ COVERED |
| **effect_size** | Yes (15 mentions) | Yes | ✓ COVERED |
| **sample_size** | Yes (13 mentions) | Yes | ⚠ WRONG LEVEL (article not finding) |
| **p_value** | Yes (11 mentions) | Yes | ✓ COVERED |
| **confidence_interval** | Yes (5 mentions) | Yes | ✓ COVERED |
| **test_statistic** | Yes (2 mentions) | Yes | ⚠ RARE |
| **theory_links** | Yes (11 mentions) | Yes | ✓ COVERED (but low specificity) |
| **mechanism** | Yes (40 mentions) | Yes | ✓ COVERED |
| **claim_type** | Yes (18 mentions) | Yes | ✓ COVERED |
| **bridge_warrant** | Yes (2 mentions) | Yes | ⚠ RARE |
| **ecological_validity** | NO (0 mentions) | Yes | ❌ MISSING |
| **causal_direction** | NO (0 mentions) | Yes | ❌ MISSING |
| **scope_conditions** | NO (0 mentions) | Yes | ❌ MISSING |
| **enabling_conditions** | NO (0 mentions) | Yes | ❌ MISSING |
| **measurement_method** | NO (0 mentions) | Yes | ❌ MISSING |
| **access_level** | NO (0 mentions) | Yes | ❌ MISSING |

**Critical Gaps**: 6 fields required by template, zero mentions in V3 prompt

---

## TABLE 9: STATISTICAL SUMMARY

| Metric | Value | Interpretation |
|---|---|---|
| **Total extractions** | 1,064 | — |
| **Total findings** | 33,116 | — |
| **Empirical articles** | 303 | 28.5% of corpus |
| **Empirical findings** | 9,200 | 27.8% of all findings |
| **Tier A findings** | 1,200 | 3.6% (target: 20-30%) |
| **Tier B findings** | 10,850 | 32.8% (acceptable) |
| **Tier C findings** | 20,770 | 62.7% (too high) |
| **Sample size coverage** | 13.3% (empirical) | Need 80%+ |
| **Effect size coverage** | 24.3% (global) | Need 50%+ |
| **Theory link coverage** | 88.8% (global) | Excellent |
| **Antecedent specificity** | 36.7% (moderate+) | Need 70%+ |
| **V3 quality score** | 0.732 (avg) | Improvement evident |
| **Surgical update rate** | 94.9% | Excellent coverage |

---

## TABLE 10: PRIORITY MATRIX FOR FIXES

| Fix | Effort (hours) | Expected Impact (Tier A improvement) | ROI | Priority |
|---|---|---|---|---|
| Add scope conditions to prompt | 2-4 | +2-3% | HIGH | CRITICAL |
| Move sample_size to finding level | 2-3 | +1-2% | HIGH | CRITICAL |
| Add enabling conditions to prompt | 4-6 | +1-2% | MEDIUM | HIGH |
| Add ecological validity extraction | 1-2 | +0.5-1% | MEDIUM | HIGH |
| Improve antecedent operationalization | 3-5 | +2-3% | HIGH | HIGH |
| Add measurement method extraction | 3-4 | +1% | MEDIUM | MEDIUM |
| Improve theory link specificity | 4-6 | +0-1% (quality not tier) | LOW | MEDIUM |
| Create family-specific prompts | 8-12 | +5-10% | VERY HIGH | MEDIUM |
| Implement tiered extraction pipeline | 12+ | +10-15% | VERY HIGH | LOW (long-term) |

---

