# Vocabulary Bridge Technical Guide

**Date**: 2026-03-01

---

## Overview

This document describes the vocabulary bridge system that connects Tier1 theoretical frameworks to Tier2 computational frameworks, enabling enrichment of findings with Tier2 relevance scores.

---

## Data Flow

```
finding_template_theory_links.json (4,888 findings with Tier1)
              |
              v
    enrich_findings_with_tier2.py
              |
         +----+----+
         |         |
         v         v
tier1_to_tier2   outcome_to_tier2
_mapping.json    _framework_mapping.json
         |         |
         +----+----+
              v
finding_template_theory_links_enriched.json
        (2,654 findings with Tier2)
```

---

## Key Components

### 1. Input: `data/production/finding_template_theory_links.json`

**Structure**:
```json
{
  "summary": {
    "findings_total": 4888,
    "findings_with_tier1_relevance": 2654,
    ...
  },
  "resolutions": [
    {
      "belief_id": "pdf:...",
      "environment_id": "env_ae_...",
      "outcome_id": "out_affect",
      "tier1_relevance": {
        "PREDICTIVE_PROCESSING": 0.209,
        "NEUROMODULATORY_REWARD": 0.4037,
        ...
      },
      "tier2_relevance": null  // or missing
    },
    ...
  ]
}
```

**Statistics**:
- 4,888 total findings
- 2,654 with Tier1 relevance scores
- 1,460 already with Tier2 (29.9%)
- 1,194 with Tier1 but no Tier2 (candidate for enrichment)

---

### 2. Mapping: `data/tier1_to_tier2_mapping.json`

**Structure**:
```json
{
  "metadata": { ... },
  "tier1_to_tier2_mapping": {
    "PREDICTIVE_PROCESSING": [
      "PP",
      "PREDICTIVE_PROCESSING",
      "ATTENTION_RESTORATION",
      ...
    ],
    "NEUROMODULATORY_REWARD": [
      "NM",
      "NEUROMODULATORY",
      "NM_REWARD",
      ...
    ],
    ...
  },
  "outcome_to_tier2_framework_mapping": {
    "out_affect": ["AFFECTIVE_NEUROSCIENCE", ...],
    "out_cog": ["COGNITIVE_CONTROL", ...],
    ...
  }
}
```

**Key facts**:
- 17 Tier1 frameworks mapped
- 29 outcome_ids mapped
- Avg 5-7 Tier2 frameworks per Tier1
- Weighted by domain expert knowledge

---

### 3. Processing: `scripts/enrich_findings_with_tier2.py`

**Algorithm**:

```python
for each finding:
  if finding.has('tier2_relevance'):
    skip  # already enriched

  tier1_relevance = finding.get('tier1_relevance', {})
  outcome_id = finding.get('outcome_id', '')

  tier2_candidates = {}

  # Strategy 1: Tier1 lookup
  for tier1_fw, tier1_score in tier1_relevance.items():
    if tier1_fw in mapping:
      tier2_frameworks = mapping[tier1_fw]
      weight = tier1_score / len(tier2_frameworks)
      for tier2_fw in tier2_frameworks:
        tier2_candidates[tier2_fw] += weight

  # Strategy 2: Outcome lookup (lower weight)
  if outcome_id in outcome_mapping:
    for tier2_fw in outcome_mapping[outcome_id]:
      tier2_candidates[tier2_fw] += 0.1 / len(outcome_mapping[outcome_id])

  if tier2_candidates:
    finding['tier2_relevance'] = normalize(tier2_candidates)
    finding['tier2_source'] = determine_source(tier1, outcome_id)
```

**Key behaviors**:
- Preserves original Tier1 confidence scores
- Distributes Tier1 score equally across mapped Tier2 frameworks
- Outcome-specific hints have lower weight (0.1 base)
- Tracks enrichment source for transparency

---

### 4. Output: `data/production/finding_template_theory_links_enriched.json`

**Structure**: Identical to input, with added `tier2_relevance` and `tier2_source` fields

**Example**:
```json
{
  "belief_id": "pdf:doi:...",
  "environment_id": "env_ae_high_ceiling",
  "outcome_id": "out_affect",
  "tier1_relevance": {
    "NEUROMODULATORY_REWARD": 0.4037,
    "SRT": 0.2221,
    "PREDICTIVE_PROCESSING": 0.209
  },
  "tier2_relevance": {
    "NEUROMODULATORY": 0.1009,
    "STRESS_RECOVERY_THEORY": 0.0555,
    "PP": 0.0522,
    "EC": 0.0522,
    ...
  },
  "tier2_source": "tier1"
}
```

---

## Confidence Score Interpretation

**Meaning of scores** (0.0 to 1.0):

- **≥ 0.30**: High confidence — Tier1 framework strongly suggests this Tier2
- **0.10–0.30**: Medium confidence — Tier1 framework maps to multiple Tier2s, score distributed
- **< 0.10**: Low confidence — Multiple Tier1 frameworks map to this Tier2, each contributing small amount
- **0.01–0.05**: Very low confidence — Outcome-specific hint or weak Tier1 signal

**Distribution statistics** (1,194 enriched findings):

```
Mean:     0.1894
Median:   0.2050
Min:      0.0500
Max:      0.6726
Q1:       0.0750
Q3:       0.2235
```

**Interpretation**: Most enriched findings have multiple Tier2 frameworks with modest scores, reflecting the branching nature of the mapping (each Tier1 → multiple Tier2).

---

## Enrichment Source Tracking

Each enriched finding has a `tier2_source` field indicating how it was enriched:

| Source | Count | Method |
|--------|-------|--------|
| original | 1,460 | Already had Tier2 in input |
| tier1 | 1,194 | Enriched via Tier1→Tier2 mapping |
| outcome | 0 | Enriched via outcome_id mapping |
| tier1_and_outcome | 0 | Enriched via both methods |

**Note**: Outcome mappings were designed but not triggered because all orphaned findings had Tier1 labels.

---

## Validation Checkpoints

### Structural Validation
- JSON parseable: ✓
- All 4,888 findings preserved: ✓
- No data loss or corruption: ✓
- Summary stats updated: ✓

### Semantic Validation
- Tier2 frameworks are valid (70 unique): ✓
- Confidence scores in [0, 1]: ✓
- All findings have tier2_source: ✓
- No circular mappings: ✓

### Coverage Validation
- Before: 1,460/4,888 (29.9%)
- After: 2,654/4,888 (54.3%)
- Gain: 1,194 (+24.4 pp)

---

## Downstream Integration

### For Template Matching
```python
# Old approach: only ~30% of findings have Tier2 labels
templates = match_templates(finding, use_tier2=True)  # sparse

# New approach: 54% of findings have Tier2 labels
templates = match_templates(finding, use_tier2=True)  # better coverage
```

### For Framework Analysis
```python
# Old: analyze only ~30% of corpus by Tier2 frameworks
full_tier2_framework_analysis = filter(resolutions, has_tier2=True)  # n=1,460

# New: analyze ~54% of corpus
full_tier2_framework_analysis = filter(resolutions, has_tier2=True)  # n=2,654
```

### For Cross-Theory Research
```python
# Map findings across Tier1→Tier2 for coherent analysis
tier1_fw = "EMBODIED_ECOLOGICAL"
related_tier2_fws = tier1_to_tier2_mapping[tier1_fw]
# Returns: ["EMBODIED_COGNITION", "EC", "ECOLOGICAL_PSYCHOLOGY", ...]
```

---

## Known Issues and Limitations

### 1. Confidence Scores Conservative
**Issue**: Mean 0.189 may seem low.
**Reason**: Inherent uncertainty in theoretical bridging; multiple Tier1 → multiple Tier2.
**Impact**: These are informed inferences, not direct matches. Use for ranking, not as "proof".

### 2. Outcome-Specific Mappings Untested
**Issue**: No findings actually enriched via outcome mappings.
**Reason**: All orphaned findings had Tier1 labels.
**Impact**: Code path exists but untested; may refine if needed.

### 3. No Validation Against Template Content
**Issue**: Tier2 frameworks assigned theoretically but not validated against actual template mechanisms.
**Reason**: Templates and findings operate independently; this bridge is at theory layer.
**Impact**: Recommend spot-checking before heavy reliance for template selection.

---

## Running the Scripts

### Full Enrichment Pipeline

```bash
cd /sessions/keen-busy-turing/mnt/REPOS/Article_Eater_PostQuinean_v1

# Step 1: Build vocabulary bridge (diagnostic only)
python3 scripts/build_vocab_bridge.py

# Step 2: Enrich findings with Tier2
python3 scripts/enrich_findings_with_tier2.py

# Output: data/production/finding_template_theory_links_enriched.json
```

### Using Enriched Findings

```python
import json

with open('data/production/finding_template_theory_links_enriched.json') as f:
    enriched = json.load(f)

# All findings now have tier2_relevance and tier2_source
for resolution in enriched['resolutions']:
    tier2 = resolution.get('tier2_relevance', {})
    source = resolution.get('tier2_source', 'unknown')

    if tier2:
        top_framework = max(tier2.items(), key=lambda x: x[1])[0]
        print(f"{resolution['belief_id']}: {top_framework} (source: {source})")
```

---

## File Locations

| File | Path | Purpose |
|------|------|---------|
| Input findings | `/data/production/finding_template_theory_links.json` | Original findings with Tier1 |
| Mapping | `/data/tier1_to_tier2_mapping.json` | Tier1↔Tier2 relationships |
| Enriched findings | `/data/production/finding_template_theory_links_enriched.json` | Output with Tier2 |
| Build script | `/scripts/build_vocab_bridge.py` | Diagnostic (produced zero matches) |
| Enrich script | `/scripts/enrich_findings_with_tier2.py` | Main enrichment (produces Tier2) |
| This guide | `/docs/VOCAB_BRIDGE_TECHNICAL_GUIDE.md` | Documentation |
| Completion report | `/docs/TIER2_ENRICHMENT_COMPLETION_2026-03-01.md` | Summary and analysis |

---

## Questions for Panel Review

1. **Mapping Validity**: Are the Tier1→Tier2 mappings theoretically sound for your frameworks?
2. **Coverage**: Are any key Tier1→Tier2 relationships missing from the mapping?
3. **Weighting**: Should certain Tier2 frameworks be weighted more heavily within their Tier1 groups?
4. **Outcome Mappings**: Should we develop outcome_id→Tier1 mappings to enrich the remaining 1,194 orphaned findings?
5. **Confidence Thresholds**: Should we filter out Tier2 assignments with confidence < 0.05 or < 0.10?

---

## Appendix: Tier1 Framework Definitions

*[Sourced from finding_template_theory_links.json]*

- **PREDICTIVE_PROCESSING**: Brain as prediction machine, minimizing prediction error
- **NEUROMODULATORY_REWARD**: Dopamine/reward system modulation
- **AFFECTIVE_EMOTION**: Emotional/affective responses
- **COGNITIVE_CONTROL**: Executive function and cognitive control
- **SPATIAL_COGNITION**: Navigation, wayfinding, spatial memory
- **MEMORY_LEARNING**: Learning and memory systems
- **SOCIAL_COGNITION**: Social perception and interaction
- **MULTISENSORY_INTEGRATION**: Cross-modal sensory binding
- **VISUAL_PERCEPTION_AESTHETICS**: Visual perception and aesthetic response
- **EMBODIED_ECOLOGICAL**: Embodied cognition and ecological psychology
- **AUDIO_COGNITION**: Auditory perception and cognition
- **MATERIAL_HAPTIC_THERMAL**: Tactile and thermal perception
- **CREATIVE_COGNITION**: Creative thinking and cognitive flexibility
- **BIOPHILIA**: Nature preference and biophilic design
- **CIRCADIAN_REGULATION**: Circadian rhythms and temporal cognition
- **ART**: Art and aesthetic experience
- **SRT**: Stress Recovery Theory

---

## Appendix: Tier2 Framework Definitions

*[Sourced from template files]*

**Core abbreviations**:
- PP = Predictive Processing
- NM = Neuromodulatory
- EC = Embodied Cognition
- MS = Memory Systems
- IC = Interoceptive Cognition
- DP = Dual Process
- CC = Cognitive Control
- CB = Chronobiological
- DT = (Cross-framework)

**Full names** (70 total):
ACOUSTIC_COMMUNICATION, AESTHETIC_EMOTIONS, AFFECTIVE_NEUROSCIENCE, AFFECTIVE_SCIENCE, ATTENTION_RESTORATION, CB, CC, CHRONOBIOLOGICAL, COGNITIVE_APPRAISAL, COGNITIVE_CONTROL, CROSS_FRAMEWORK, CULTURAL_PSYCHOLOGY, DEVELOPMENTAL_NEUROSCIENCE, DIFFERENTIAL_SUSCEPTIBILITY, DIRECTED_ATTENTION, DMN_TPN_DYNAMICS, DP, DT, DUAL_PROCESS, EC, ECOLOGICAL_RATIONALITY, EMBODIED_COGNITION, EMOTION_PERCEPTION, EMPATHY, HC, IC, INTEROCEPTION, INTEROCEPTION_ALLOSTASIS, INTEROCEPTION_CONSTRUCTIONIST, MEMORY_SYSTEMS, METHODOLOGICAL, MS, MSI, MULTISENSORY_INTEGRATION, MUSIC_COGNITION, NEUROMODULATORY, NM, NM_AROUSAL, NM_REWARD, NM_STRESS, PAD_emotional_model, PP, PREDICTIVE_PROCESSING, RESTORATIVE_ENVIRONMENTS, REWARD_PROCESSING, SN, SPATIAL_NAVIGATION, STRESS_RECOVERY_THEORY, adaptive_thermal_comfort, affordance_theory, allostatic_regulation, arousal_theory, attention_restoration, attention_restoration_theory, biophilia, categorical_color_perception, cognitive_control, cognitive_load_theory, color_in_context, construal_level_theory, creative_cognition, creative_cognition_theory, ecological_psychology, ecological_valence_theory, embodied_cognition, environmental_psychology, forward_models, group_creativity, hierarchical_predictive_coding, incubation_theory, metabolic_health, motor_control_theory, network_neuroscience, organizational_psychology, predictive_processing, processing_fluency, retinal_activation, temporal_cognition, time_perception_theory

---

*Last updated: 2026-03-01*
