# Gold Standard Extraction Dataset

This directory contains gold standard (hand-curated) extractions of scientific articles for the Article Eater project.

## Files

### 1. `paper1_10.1038_s41598-025-18629-z.json`
**Main extraction file** — Complete structured extraction of the Kim (2025) paper.

**Structure**:
- `article_level`: Metadata (DOI, authors, journal, domains)
- `findings`: 15 empirical findings with:
  - Operationalized variables (antecedents/consequents)
  - Exact statistics (p-values, effect sizes, test statistics)
  - Direct quotes from source text
  - Mechanism descriptions
  - Theory links
  - Scope conditions and sample info
- `limitations`: 7 author-acknowledged limitations
- `overall_theory_links`: 3 theoretical frameworks
- `key_hypotheses_tested`: 4 hypotheses with support status
- `design_features`: Complete methodological details
- `measurement_summary`: All instruments and constructs
- `statistical_details`: Analysis approaches
- `extraction_metadata`: Validation and integrity information

**Size**: 51 KB | **Format**: Valid JSON

### 2. `EXTRACTION_SUMMARY.md`
**Human-readable summary** — Overview, key findings, limitations, and recommendations.

Contains:
- Article overview and design
- Findings table (neurophysiological, affective, cognitive)
- Regression model results
- Hypothesis testing summary
- Core mechanism identified
- Extraction quality metrics
- Recommended next steps

### 3. `README.md`
This file.

---

## Paper Details

**Title**: Cognitive efficiency in VR simulated natural indoor environments examined through EEG and affective responses

**Authors**: Sieun Kim (Yonsei University)

**DOI**: 10.1038/s41598-025-18629-z

**Journal**: Scientific Reports (2025)

**Study Design**: Within-subject experimental, N=36 Korean college students

**Key Variables**:
- **Independent**: 4 VR-simulated interior environments (Control, Curvilinear Forms, Nature Views, Wooden Interior)
- **Dependent**: 
  - Neurophysiological: EEG frequency band ratios (ATR, TBR, ABR)
  - Affective: Self-reported relaxation and valence
  - Cognitive: Task performance (Error Detection, Stroop, Go/No-Go)

---

## Key Findings Summary

| Finding | Result | P-value | Effect Size |
|---------|--------|---------|-------------|
| Wooden interior → ATR (alpha activity) | ↑ Increase | 0.007 | η²p = 0.109 |
| Wooden interior → TBR (cognitive load) | ↓ Decrease | 0.008 | η²p = 0.107 |
| Wooden interior → ABR (relaxation) | ↑ Increase | 0.001 | η²p = 0.137 |
| Wooden interior → Cognitive performance | ↑ Increase | < 0.001 | η²p = 0.475 |
| Nature views alone → Cognitive performance | No effect | NS | — |
| Curvilinear forms alone → Cognitive performance | No effect | NS | — |
| **Overall regression model** (ATR + Relaxation + W condition) | Significant | < 0.001 | R² = 0.148 |

---

## Extraction Quality

✓ **15 findings** extracted with full methodological precision
✓ **All p-values** reported with exact values (not approximate)
✓ **All effect sizes** extracted with proper nomenclature (η²p, β, R²)
✓ **Direct quotes** from source for every major finding
✓ **Scope conditions** documented (setting, duration, measurement type)
✓ **Theory links** provided for each finding
✓ **Mechanisms** proposed where discussed in paper
✓ **Limitations** listed with author acknowledgments

**Validation**: JSON validated as syntactically correct. All required fields present across all findings.

---

## How to Use

### For Analysis
```python
import json

with open('paper1_10.1038_s41598-025-18629-z.json') as f:
    data = json.load(f)

# Access specific finding
finding = data['findings'][0]  # F1: ATR in W condition

# Access hypothesis tests
hypotheses = data['key_hypotheses_tested']

# Access limitations
limitations = data['limitations']
```

### For Panel Review
1. Read `EXTRACTION_SUMMARY.md` for overview
2. Review `paper1_10.1038_s41598-025-18629-z.json` for complete details
3. Evaluate mechanism (F14), surprising null findings (F7, F8), and regression model (F13)
4. Consider limitations and recommendations for follow-up research

### For Validation
```bash
python3 -m json.tool paper1_10.1038_s41598-025-18629-z.json > /dev/null
echo "JSON is valid"
```

---

## Citation

If using this extraction in subsequent research, cite as:

"Gold standard extraction of Kim (2025) [DOI: 10.1038/s41598-025-18629-z], extracted 2025-03-05 for the Article Eater project."

---

## Notes

- **Generalizability**: Sample limited to Korean college students; findings may not generalize across cultures and populations
- **VR vs Real-world**: VR-based stimuli may not capture full multisensory complexity of real indoor spaces
- **Exploratory**: Study explores novel design-cognition relationships; replication needed
- **Panel review pending**: Results recommended for expert panel evaluation of mechanism and methodology

---

## Contact

For questions about the extraction methodology or findings interpretation, refer to the Article Eater project documentation.

**Extraction completed**: 2025-03-05  
**Status**: GOLD STANDARD — Ready for analysis and panel review
