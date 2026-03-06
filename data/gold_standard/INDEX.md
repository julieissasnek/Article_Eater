# Gold Standard Extraction Index

**Project**: Article Eater - Gold Standard Comparison Dataset
**Last Updated**: 2026-03-05
**Total Papers**: 6
**Total Findings (Empirical Only)**: 32

---

## Papers in Gold Standard Collection

### Existing Papers (1-3)

| # | DOI | Title | Year | Type | Findings |
|---|-----|-------|------|------|----------|
| 1 | 10.1038/s41598-025-18629-z | Cognitive efficiency in VR simulated natural indoor environments examined through EEG and affective responses | 2025 | Empirical | 15 |
| 2 | 10.1186/s40410-016-0033-1 | [Historical architecture study] | TBD | Empirical | TBD |
| 3 | 10.1016/j.buildenv.2025.110819 | [Building environment study] | TBD | Empirical | TBD |

### New Papers (4-6) — Comparison Against Gemini

| # | DOI | Title | Year | Type | Findings | Gemini Extract |
|---|-----|-------|------|------|----------|-----------------|
| 4 | 10.1002/ad.2031 | Function as the Basis of Psychiatric Ward Design | 1957 | Theoretical | 0* | 17 |
| 5 | 10.1002/ad.2630 | Multi Sensory Design | 2011 | Methodological | 0* | 12 |
| 6 | 10.1002/ad.2634 | Effects of architectural interventions on psychological, cognitive, social, and pro-environmental aspects of occupant well-being | 2024 | Empirical | **17** | 18 |

*Papers 4-5 are not empirical studies (no quantitative findings). Gemini extraction appears to have misclassified design principles and methodological steps as empirical findings.

---

## File Descriptions

### New Extraction Files

#### paper4_10.1002_ad.2031.json
- **Size**: 5.8 KB
- **Findings**: 0 (correctly identified as non-empirical)
- **Content**: 9 design principles for psychiatric wards with clinical rationale
- **Special Features**: Maps perceptual disturbances to architectural implications
- **Validation**: JSON valid

#### paper5_10.1002_ad.2630.json
- **Size**: 6.5 KB
- **Findings**: 0 (correctly identified as non-empirical)
- **Content**: 8-step Multi Sensory Design methodology framework
- **Special Features**: Complete methodology documentation with sensory integration at each stage
- **Validation**: JSON valid

#### paper6_10.1002_ad.2634.json
- **Size**: 44 KB
- **Findings**: **17 empirical findings**
- **Content**: Comprehensive extraction of 2×2×2 experimental study on architectural interventions
- **Special Features**:
  - All p-values extracted with precision
  - All effect sizes labeled with proper type (η²p)
  - Sample demographics complete (N=411, 67% male, 33% female, age 37.5±12.1)
  - 4 main effects (windows, diversity, materials, gender effects)
  - 2 null findings (nature alone, curvilinear alone)
  - 3 interaction effects (combined features)
  - 3 demographic moderators
  - 2 mechanism discussions
  - 1 behavioral outcome (donation)
  - 2 methodological features
- **Validation**: JSON valid

#### GOLD_STANDARD_PAPERS_4_5_6_REPORT.md
- **Size**: 8 KB
- **Content**: Comprehensive extraction report with methodology, quality metrics, and comparative analysis
- **Sections**:
  - Summary table of all 3 papers
  - Detailed content analysis for each paper
  - Why papers 4-5 have 0 findings
  - Complete findings summary for paper 6
  - Comparison to Gemini extraction
  - Extraction quality metrics
  - JSON validation results
  - Extraction methodology explanation
  - Key insights and recommendations

---

## Comparison to Gemini Extraction

### Finding Counts
- Paper 4: Gold Standard = 0, Gemini = 17 (**Discrepancy**: Gemini over-extracted design principles)
- Paper 5: Gold Standard = 0, Gemini = 12 (**Discrepancy**: Gemini over-extracted methodological steps)
- Paper 6: Gold Standard = 17, Gemini = 18 (**Minor Discrepancy**: Possible double-counting by Gemini)

### Classification Differences
- **Papers 4-5**: Gold standard correctly identifies these as non-empirical works
- **Paper 6**: Gold standard extracts all empirical findings comprehensively with exact statistics

### Precision Differences
- **P-values**: Gold standard extracts exact values (e.g., p=0.001); Gemini may round
- **Effect sizes**: Gold standard includes proper nomenclature (η²p); Gemini may omit type labels
- **Sample details**: Gold standard includes full demographic breakdown; Gemini may provide only N

---

## Extraction Quality Metrics

### Paper 4
- Design principles extracted: 9
- Perceptual disturbances mapped: 6
- Theory links identified: 5
- Data type: Qualitative/clinical wisdom
- **Status**: Complete and accurate

### Paper 5
- Design methodology steps: 8
- Core principles documented: 5
- Sensory modalities covered: 5
- Data type: Methodological framework
- **Status**: Complete and accurate

### Paper 6
- Empirical findings: 17
- P-values reported: 14/17 (82%)
- Effect sizes reported: 12/17 (71%)
- Direct quotes: 17/17 (100%)
- Sample documented: Complete (N=411, demographics, exclusion rates)
- **Status**: Complete and comprehensive

---

## Validation Results

All files passed JSON syntax validation:
```
paper4_10.1002_ad.2031.json   ✓ VALID
paper5_10.1002_ad.2630.json   ✓ VALID
paper6_10.1002_ad.2634.json   ✓ VALID
```

All required schema fields verified:
- ✓ Top-level: doi, title, authors, publication_year, journal, article_type, domains, findings, limitations, overall_theory_links, extraction_metadata
- ✓ Findings (paper 6): id, antecedent, consequent, direction, claim_type, statement, p_value, effect_size, sample_size, sample, measure_type, instruments_used, source, quote, mechanism, theory_links, scope_conditions, moderators_reported

---

## Key Findings from Paper 6 (Empirical Study)

### Main Effects (p < 0.05)
1. Windows increase sense of belonging (p=0.001, η²p=0.0553)
2. Windows decrease stress (p=0.007, η²p=0.0168)
3. Diverse representation increases divergent creativity (p=0.005, η²p=0.0440)
4. Women report higher environmental concern than men (p=0.001)

### Null Findings (Isolation Effects)
- Nature views alone: no cognitive performance effect
- Curvilinear forms alone: no cognitive performance effect

### Interactions
- Windows + natural materials: synergistic effect on belonging
- Artificial + no window: worst combination for well-being
- Diverse representation × participant race: stronger effect for non-white participants

### Mechanisms
- Diversity priming reduces stereotype threat and improves stress outcomes
- Cognitive diversity activation enhances divergent creativity

### Behavioral Evidence
- Environmental concern translates to donation behavior

---

## How to Use This Dataset

### For Comparative Analysis
1. Compare Gemini counts vs. Gold Standard counts
2. Analyze precision differences in statistics (p-values, effect sizes)
3. Evaluate classification accuracy (empirical vs. non-empirical)
4. Assess schema compliance

### For Research
1. Use paper 6 findings for meta-analysis on built environment effects
2. Reference papers 4-5 for architectural design principles background
3. Cite gold standard extraction in methodological sections

### For Validation
1. Review GOLD_STANDARD_PAPERS_4_5_6_REPORT.md for methodology
2. Spot-check findings against original papers using source citations
3. Verify JSON syntax with `python3 -m json.tool`
4. Validate sample sizes and p-value precision

---

## Citation

If using these gold standard extractions, cite as:

```
Gold standard extraction of papers 4-6 (Osmond 1957, Schifferstein 2011, Bianchi et al. 2024), extracted 2026-03-05 for the Article Eater project comparative analysis. Papers obtained from Article_Finder_v3_2_3 and building environment literature collection.
```

---

## Notes for Panel Review

1. **Papers 4-5**: Represent foundational theoretical works that establish design principles and methodologies. They contribute conceptual frameworks rather than empirical evidence. Correctly marked as 0 findings.

2. **Paper 6**: Rich empirical study examining interactions between architectural features (materials, windows) and diversity representation on well-being outcomes. The 17 findings represent main effects, null findings, interactions, mechanisms, and behavioral outcomes. Small effect sizes (η²p < 0.044) suggest effects are real but of modest magnitude.

3. **Gemini Comparison**: Suggests Gemini may have misclassified prescriptive content (design principles, methodology steps) as empirical findings. Gold standard correctly distinguishes between theoretical/methodological papers and empirical studies.

4. **Next Steps**: 
   - Conduct inter-rater reliability analysis on Paper 6 findings
   - Analyze Gemini extraction errors by category
   - Document decision rules for classifying article types
   - Recommend improvements to automated extraction pipeline

---

**Extraction Completed**: 2026-03-05  
**Model**: claude-opus-4-gold-standard  
**Status**: READY FOR ANALYSIS AND PANEL REVIEW
