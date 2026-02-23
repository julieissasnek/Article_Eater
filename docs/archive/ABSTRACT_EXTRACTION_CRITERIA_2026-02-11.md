# Abstract Extraction Criteria for CNfA Rule Generation

**Date**: 2026-02-11
**Status**: PROPOSED - Based on batch 3 analysis
**Purpose**: Improve relevance and topic coverage for abstract → rule pipeline

---

## Problem Statement

Batch 3 processing revealed two systematic problems:
1. **Topic imbalance**: ~32 acoustic rules, 1 restoration rule
2. **Relevance leakage**: ~25-30% of extracted rules are NOT CNfA-relevant

---

## Solution 1: Stratified Topic Sampling

### Required: Equal representation across 9 CNfA domains

```sql
-- Get exactly N papers per topic (e.g., 5 per topic = 45 papers)
WITH ranked AS (
  SELECT *,
    ROW_NUMBER() OVER (PARTITION BY topic_category ORDER BY RANDOM()) as rn
  FROM papers
  WHERE topic_decision = 'on_topic'
    AND abstract IS NOT NULL
    AND LENGTH(abstract) > 200
)
SELECT * FROM ranked WHERE rn <= 5;
```

### Topic Categories (map by title keywords, not source field)

| Category | Required Keywords (title OR abstract) |
|----------|--------------------------------------|
| ACOUSTIC | noise, sound, acoustic, speech, auditory, soundscape |
| AIR | ventilation, air quality, CO2, VOC, IAQ |
| LIGHT | daylight, lighting, illuminance, lux, CCT, circadian, window (light) |
| BIOPHILIC | nature, plant, green, biophilic, garden, vegetation, tree |
| THERMAL | thermal, temperature, heat, humidity, HVAC, comfort (thermal) |
| SPATIAL | layout, density, ceiling height, enclosure, wayfinding, open plan |
| RESTORATION | restoration, restorative, recovery (mental/psychological) |
| COGNITION | attention, cognitive, memory, concentration, mental fatigue, executive function |
| AFFECT | mood, emotion, stress, anxiety, wellbeing, affect |

---

## Solution 2: Pre-Extraction Relevance Filter

### INCLUDE only if abstract contains:

**Environmental variable** (at least one):
- Physical environment term (noise, light, temp, air, space, nature)
- Built environment context (office, classroom, hospital, building, indoor, room)

**AND Human outcome** (at least one):
- Psychological (mood, stress, attention, cognition, performance, comfort)
- Physiological (cortisol, HRV, EEG, heart rate)
- Behavioral (productivity, task performance, learning)

**AND Study type indicator** (at least one):
- Sample/participant terms (n=, participants, subjects, students, workers)
- Method terms (experiment, study, trial, measured, assessed)

### EXCLUDE if abstract contains:

| Exclusion Category | Keywords |
|--------------------|----------|
| Animal studies | mice, rats, rodents, fish, animal model |
| Materials science | polymer, alloy, nanoparticle, synthesis, catalyst |
| Clinical treatment | surgery, chemotherapy, drug trial, dosage, treatment arm |
| Pure methodology | algorithm, neural network accuracy, model performance (without human outcomes) |
| Historical/cultural | dynasty, heritage, artifact, archaeological |
| Digital-only | interface design, website, app (without physical environment) |

---

## Solution 3: Rule Quality Gate

Before writing rule to database, verify it passes:

```
RULE QUALITY CHECKLIST:
[ ] Has environmental IV (physical environment feature)
[ ] Has human DV (psychological, physiological, or behavioral outcome)
[ ] Has effect direction (increases, decreases, improves, impairs)
[ ] Has sample info (n=X) OR study type (experiment, field study)
[ ] NOT a methodology finding (model accuracy, sensing precision)
[ ] NOT a design recommendation without empirical data
```

Rules failing checklist get confidence = 0 or are not inserted.

---

## Implementation Priority

1. **Add topic_category column** to papers table (computed from title keywords)
2. **Create stratified sampling query** for equal topic representation
3. **Add relevance_score column** based on inclusion/exclusion keywords
4. **Filter papers with relevance_score >= threshold** before extraction

---

## Expected Improvement

| Metric | Batch 3 (current) | Target |
|--------|-------------------|--------|
| Topic coverage variance | High (32 acoustic, 1 restoration) | Low (<2x between topics) |
| CNfA relevance rate | ~70% | >90% |
| Mechanism papers | ~20% | <10% (unless explicitly requested) |
| Off-topic leakage | ~25% | <5% |

---

## Revision History

| Date | Change |
|------|--------|
| 2026-02-11 | Initial criteria based on batch 3 analysis |
