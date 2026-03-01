# Taxonomy Cross-Reference & Gap Analysis
**Generated**: 2026-02-28T15:03:31.541938+00:00

## System Inventory

| System | Coverage |
|--------|----------|
| Outcome Vocab | 103 terms across 8 domains |
| Tag Engine | 42 tags across 3 dimensions |
| Image Features | 14 features |

## Cross-Reference Summary

| Mapping | Count |
|---------|-------|
| Tag → Outcome links | 46 |
| Tag → Image links | 16 |
| Outcome → Image links | 19 |

## Gap Analysis

### Outcomes Without Tag Coverage (60)
These outcome constructs have no corresponding tag_engine tag:

- `affect.anxiety`
- `affect.frustration`
- `affect.joy`
- `affect.mood.negative`
- `affect.mood.positive`
- `affect.mystery`
- `affect.place_attachment`
- `affect.relaxation`
- `affect.resilience`
- `affect.serenity`
- `behav.activity`
- `behav.comfort_seeking`
- `behav.dwell_time`
- `behav.exploration`
- `behav.learning`
- ... and 45 more

### Outcomes Without Image Representation (86)
These outcomes cannot be visually searched or matched to images:

- `affect.anxiety`
- `affect.awe`
- `affect.fascination`
- `affect.frustration`
- `affect.joy`
- `affect.mood`
- `affect.mood.negative`
- `affect.mood.positive`
- `affect.mystery`
- `affect.place_attachment`
- `affect.relaxation`
- `affect.resilience`
- `affect.satisfaction`
- `affect.serenity`
- `affect.stress`
- ... and 71 more

### Tags Without Outcome Mapping (25)

- `EEG`
- `VR`
- `affective`
- `allostatic`
- `behavioral_observation`
- `cognitive`
- `cultural`
- `developmental`
- `evolutionary`
- `experiment`
- `eye_tracking`
- `fMRI`
- `field_study`
- `interview`
- `meta_analysis`
- `mixed_methods`
- `neurological`
- `perceptual`
- `physiological`
- `physiological_measures`
- `quasi_experiment`
- `simulation`
- `social`
- `survey`
- `systematic_review`

### Opaque Zones (59)
Outcomes with **neither** tag nor image coverage — blind spots:

- ⚠️ `affect.anxiety`
- ⚠️ `affect.frustration`
- ⚠️ `affect.joy`
- ⚠️ `affect.mood.negative`
- ⚠️ `affect.mood.positive`
- ⚠️ `affect.mystery`
- ⚠️ `affect.place_attachment`
- ⚠️ `affect.relaxation`
- ⚠️ `affect.resilience`
- ⚠️ `affect.serenity`
- ⚠️ `behav.activity`
- ⚠️ `behav.comfort_seeking`
- ⚠️ `behav.dwell_time`
- ⚠️ `behav.exploration`
- ⚠️ `behav.learning`
- ⚠️ `behav.productivity`
- ⚠️ `behav.risk_taking`
- ⚠️ `behav.social_behavior`
- ⚠️ `cog.attention.broad`
- ⚠️ `cog.attention.divided`
- ⚠️ `cog.attention.selective`
- ⚠️ `cog.attention.sustained`
- ⚠️ `cog.executive`
- ⚠️ `cog.executive.inhibition`
- ⚠️ `cog.executive.planning`
- ⚠️ `cog.language`
- ⚠️ `cog.memory`
- ⚠️ `cog.memory.episodic`
- ⚠️ `cog.memory.working`
- ⚠️ `cog.place_recognition`
- ⚠️ `cog.processing_speed`
- ⚠️ `cog.reasoning`
- ⚠️ `env.air_quality`
- ⚠️ `env.color`
- ⚠️ `env.privacy`
- ⚠️ `env.spaciousness`
- ⚠️ `env.visual_access`
- ⚠️ `health.immunity`
- ⚠️ `health.resilience`
- ⚠️ `health.sick_building`
- ⚠️ `neural.activation`
- ⚠️ `neural.connectivity`
- ⚠️ `neural.default_mode`
- ⚠️ `neural.eeg`
- ⚠️ `neural.synchrony`
- ⚠️ `physio.blood_pressure`
- ⚠️ `physio.eye_movement`
- ⚠️ `physio.fatigue`
- ⚠️ `physio.heart_rate`
- ⚠️ `physio.heart_rate.hrv`
- ⚠️ `physio.pain`
- ⚠️ `physio.respiration`
- ⚠️ `physio.skin_conductance`
- ⚠️ `physio.stress_hormones.cortisol`
- ⚠️ `social.affiliation`
- ⚠️ `social.belonging`
- ⚠️ `social.cohesion`
- ⚠️ `social.collaboration`
- ⚠️ `social.trust`

## Recommendations

1. **Priority mappings**: Wire opaque zone outcomes to tags and image features
2. **Tag expansion**: Add tags for outcomes like `social.belonging`, `affect.place_attachment`
3. **Image feature gaps**: Add CNfA features for neural and health outcomes
4. **Unified search**: Build query layer that searches all three systems