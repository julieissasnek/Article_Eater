# Interpretation Space Phase 1 - Pilot Beliefs Dataset

**Created**: 2026-03-01
**Version**: v1.0
**Status**: Ready for Phase 1 Self-Interrogation Pilot

---

## Overview

This directory contains the curated 50-belief pilot sample for the Interpretation Space Phase 1 self-interrogation protocol. Beliefs are stratified across four epistemic zones designed to test different aspects of the interrogation framework.

---

## Files

### 1. `pilot_beliefs_50.json` (76 KB)
**The main dataset.** Array of 50 belief objects, each containing:

- `belief_id`: Unique identifier (format: `doi__f{finding_num}` or `template:...`)
- `content`: Full belief statement with antecedent→consequent structure
- `credence_value`: Confidence level (0.158–0.736 range)
- `credence_uncertainty`: Uncertainty metric (null in current version)
- `scope`: Scope conditions (null for most; Zone 4 gap-finding candidate)
- `domain`: Domain/subject tag (sparse; 26% coverage)
- `entrenchment`: Coherence-based stability score
- `epistemic_v2`: Template linkage structure with environment, outcome, and top-scoring causal templates
- `paper_ids`: Source DOI citations (74% coverage)
- `stratification_zone`: Classification (1, 2, 3, or 4)
- `stratification_rationale`: Selection justification

**Usage**: Load as JSON array; iterate over beliefs for interrogation testing.

### 2. `pilot_beliefs_50_SUMMARY.json` (3.1 KB)
**Quantitative summary.** High-level statistics covering:

- Stratification targets vs. actual counts
- Credence distribution by zone
- Data coverage percentages
- Unique source DOI list
- Entrenchment and template coverage

**Usage**: Quick validation, summary reporting, statistical comparison.

### 3. `SELECTION_REPORT_2026-03-01.md` (9.7 KB)
**Detailed selection methodology and rationale.** Covers:

- Population statistics from source database (3,420 total beliefs)
- Zone-by-zone selection criteria and justification
- Data coverage analysis
- Source composition (empirical vs. template-based)
- Credence distribution visualization
- Self-interrogation protocol application points
- Recommendations for Phase 1 execution

**Usage**: Reference documentation for understanding sample design; input to expert panel review.

### 4. `README.md` (this file)
Navigation and quick-start guide.

---

## Dataset Composition

### Zone Distribution

| Zone | Type | Count | Credence Range | Purpose |
|---|---|---|---|---|
| **1** | High-credence | 12 | 0.704–0.736 | Baseline stable beliefs; test protocol on well-entrenched claims |
| **2** | Moderate-credence | 15 | 0.400–0.683 | Primary interrogation target; test warrant adequacy |
| **3** | Low-credence | 13 | 0.158–0.370 | Frontier beliefs; test credence calibration and evidence requirements |
| **4** | Poorly-covered | 10 | 0.400–0.600 | Gap-finding; test interrogation's ability to identify missing scope/mechanism |

### Credence Statistics

```
Mean credence:    0.478
Median credence:  0.482
Std deviation:    0.196
Min credence:     0.158 (Zone 3)
Max credence:     0.736 (Zone 1)
```

### Source Diversity

- **Unique sources**: 39 (empirical papers + synthetic templates)
- **Empirical papers**: 25 peer-reviewed DOI-based articles
- **Template-derived**: 14 beliefs from causal mechanism templates
- **Geographic/domain spread**: Color science, perception, architecture, neuroscience, sleep, social cognition, material science

### Metadata Coverage

| Field | Count | Percentage |
|---|---|---|
| epistemic_v2 (template linkages) | 50 | **100%** |
| paper_ids (source DOIs) | 37 | **74%** |
| entrenchment | 50 | **100%** |
| domain | 13 | 26% |
| scope conditions | 0 | **0%** ← Zone 4 gap-finding opportunity |

---

## How to Use

### For Protocol Testing

```python
import json

# Load beliefs
with open('pilot_beliefs_50.json') as f:
    beliefs = json.load(f)

# Filter by zone
zone_1_beliefs = [b for b in beliefs if b['stratification_zone'] == '1']

# Access interrogation targets
for belief in zone_1_beliefs:
    belief_id = belief['belief_id']
    content = belief['content']
    templates = belief['epistemic_v2']['template_relevance_v1']['top_templates']
    # Apply interrogation protocol...
```

### For Summary Reporting

```python
# Load summary
with open('pilot_beliefs_50_SUMMARY.json') as f:
    summary = json.load(f)

# Reference statistics
print(f"Zone 1 credence range: {summary['credence_statistics']['by_zone']['zone_1']}")
print(f"Template coverage: {summary['data_coverage']['coverage_percentage']['epistemic_v2']}%")
```

### For Methodology Review

```bash
# Read detailed methodology
cat SELECTION_REPORT_2026-03-01.md
```

---

## Phase 1 Interrogation Targets

The self-interrogation protocol should test:

### Protocol Questions (by zone)

**Zone 1 (Stability Testing)**
- Q1: Are your template linkages accurate?
- Q2: Is your high credence justified solely by coherence?

**Zone 2 (Primary Testing)**
- Q3: What scope conditions apply to you?
- Q4: Do your paper sources fully support your credence?
- Q5: What mechanism chains rationalize you?

**Zone 3 (Frontier Testing)**
- Q6: What evidence would upgrade your credence?
- Q7: Are you a frontier belief or fundamentally false?

**Zone 4 (Gap Recovery)**
- Q8: What scope conditions should apply?
- Q9: What mechanism chains are missing?
- Q10: What warrant citations are absent?

### Expected Outcomes

- Self-repair of epistemic structure
- Warrant diagnosis by type
- Scope condition recovery for under-specified beliefs
- Credence calibration validation
- Template relevance accuracy assessment

---

## Technical Specifications

### Field Specifications

#### belief_id
- Format: `doi__f{num}` or `template:{template_id}`
- Example: `10.1006/jevp.2000.0198__f8`
- Uniqueness: All 50 IDs are unique

#### credence_value
- Type: float
- Range: [0.0, 1.0]
- Actual range in sample: [0.158, 0.736]
- Distribution: Non-uniform (clustered by zone)

#### epistemic_v2
- Type: JSON object
- Structure:
  ```json
  {
    "template_relevance_v1": {
      "environment_id": "env_XXXX",
      "outcome_id": "outcome_XXXX",
      "tier1_relevance": {...},
      "tier2_relevance": {...},
      "top_templates": [
        {
          "template_id": "...",
          "display_id": "...",
          "score": 0.0–1.0,
          "reasons": [...]
        }
      ]
    }
  }
  ```
- Completeness: 100% (all 50 beliefs have this field)

#### paper_ids
- Type: JSON array of strings
- Example: `["doi:10.1006/jevp.2000.0198"]`
- Coverage: 37/50 beliefs (74%)
- Note: Zone 3 low-credence beliefs often lack paper sources

---

## Data Validation

All 50 beliefs pass the following checks:

- ✓ Valid JSON structure
- ✓ Required fields present (belief_id, content, credence_value, stratification_zone)
- ✓ No null belief IDs or content
- ✓ Unique belief_id values (no duplicates)
- ✓ Credence values within expected zone ranges
- ✓ Zone counts match targets (12/15/13/10)
- ✓ 100% template linkage coverage

**Validation Status**: PASS (2026-03-01)

---

## Integration with ATLAS EN

### Relationships

- **Source**: Extracted from `web_persistence_v2.db` (beliefs table)
- **Entrenchment context**: Coherence-based scores from same database
- **Template context**: Links via `epistemic_v2` to schema templates
- **Paper context**: DOI references traceable to `data/extractions/` JSON files

### Upstream Dependencies

These 50 beliefs depend on:
1. `web_persistence_v2.db` (source database)
2. `data/extractions/{doi}.json` (paper metadata, if needed for deep interrogation)
3. ATLAS template schema (for template relevance interpretation)

### Downstream Integrations

The self-interrogation results will feed into:
1. Warrant diagnosis and classification
2. Scope condition enrichment
3. Mechanism chain specification
4. Credence recalibration models
5. System-level epistemic coherence updates

---

## Recommended Next Steps

### Phase 1a: Protocol Validation (this pilot)
1. Run interrogation protocol on all 50 beliefs
2. Collect responses and classify by success/failure
3. Refine question set based on response quality
4. Test specific protocol questions on Zone subsamples

### Phase 1b: Detailed Analysis
1. Deep interrogation of Zone 4 beliefs for scope recovery
2. Statistical comparison of interrogation accuracy vs. entrenchment score
3. Template relevance validation against interrogation results
4. Paper source verification for top-credence Zone 1 beliefs

### Phase 2: Scaling
1. Extend interrogation to full 3,420-belief set
2. Automate warrant diagnosis for large-scale assessment
3. Update database with recovered scope/mechanism data
4. Generate system-level coherence reports

---

## Contact & Metadata

**Sample Version**: v1.0 (frozen)
**Database Snapshot**: 2026-03-01 21:28 UTC
**Selection Algorithm**: Stratified random sampling with zone-based credence thresholds
**Reproducibility**: Random seed = 42 (Python; deterministic)

**Questions about this dataset?**
- See `SELECTION_REPORT_2026-03-01.md` for methodology
- See `pilot_beliefs_50_SUMMARY.json` for statistics
- Check belief IDs against source DOIs in `data/extractions/`

---

**Sample Status**: Ready for Phase 1 Interrogation ✓
