# STIMULUS DOCUMENTATION TEMPLATE v1.0

**Version**: 1.0.0
**Date**: February 9, 2026
**Status**: APPROVED by Panel (2026-02-08)
**Domain**: CNfA (Cognition, Neuroscience, and Architecture) / Environmental Psychology

---

## PURPOSE

This template standardizes documentation of environmental stimuli used in CNfA research. Proper stimulus documentation enables:

1. **Replication** — Others can recreate the study
2. **Scope assessment** — Transfer to real-world settings
3. **Taxonomy mapping** — Link to environment ontology
4. **Bridge warrant evaluation** — Cross-domain generalization
5. **Dosage analysis** — Nature "dose" for design guidelines

---

## WHEN TO USE

Apply this template when extracting from studies that use:
- Nature images (photos, videos)
- Virtual reality environments
- Physical installations (plants, water features)
- Acoustic stimuli (nature sounds)
- Architectural spaces
- Multi-sensory environmental stimuli

---

## STIMULUS DOCUMENTATION SCHEMA

### Header Information

```yaml
stimulus_doc:
  schema: "ae.stimulus.v1"
  paper_id: "[paper_id from extraction]"
  stimulus_set_id: "[unique ID for this stimulus set]"
  created_at: "[ISO timestamp]"
```

### 1. STIMULUS CLASSIFICATION

```yaml
classification:
  # Primary modality
  modality: "visual|auditory|olfactory|haptic|multi_sensory"

  # Presentation format
  format: "photograph|video|vr|ar|physical|acoustic|illustration|text_description"

  # Environment type (from environment_taxonomy)
  environment_type:
    primary: "[env_id from taxonomy]"
    secondary: ["[additional env_ids]"]

  # Nature elements present (from Kellert's biophilic design patterns)
  biophilic_elements:
    direct_nature:
      - "vegetation"
      - "water"
      - "animals"
      - "natural_light"
      - "air_flow"
      - "weather"
    indirect_nature:
      - "natural_materials"
      - "natural_colors"
      - "nature_imagery"
      - "natural_patterns"
      - "nature_sounds"
    space_and_place:
      - "prospect"
      - "refuge"
      - "mystery"
      - "risk_peril"
      - "transitional_spaces"

  # Kaplan's ART features
  art_features:
    being_away: "high|moderate|low|not_assessed"
    fascination: "high|moderate|low|not_assessed"
    extent: "high|moderate|low|not_assessed"
    compatibility: "high|moderate|low|not_assessed"

  # Ulrich's SRT features
  srt_features:
    positive_affect: "high|moderate|low|not_assessed"
    physiological_calming: "expected|not_expected"
    attention_holding: "soft|hard"
```

### 2. PHYSICAL SPECIFICATIONS

```yaml
physical_specs:
  # For visual stimuli
  visual:
    dimensions:
      width: "[cm or degrees]"
      height: "[cm or degrees]"
      aspect_ratio: "[e.g., 16:9]"
    display:
      medium: "monitor|projector|print|vr_headset"
      resolution: "[e.g., 1920x1080]"
      viewing_distance: "[cm]"
      viewing_angle: "[degrees]"
    color:
      color_space: "RGB|LAB|calibrated"
      luminance_cd_m2: "[value or range]"
      color_temperature_K: "[value]"
    image_properties:
      green_coverage_percent: "[0-100]"
      sky_visibility_percent: "[0-100]"
      water_visibility_percent: "[0-100]"
      human_presence: "none|distant|present"
      animal_presence: "none|distant|present"
      built_elements_percent: "[0-100]"

  # For auditory stimuli
  auditory:
    duration_seconds: "[value]"
    sound_type: "field_recording|synthesized|curated_library"
    acoustic_features:
      dominant_frequency_hz: "[range]"
      loudness_db: "[value]"
      variation: "constant|rhythmic|variable"
    sound_elements:
      birdsong: true|false
      water_sounds: true|false
      wind: true|false
      human_sounds: true|false
      traffic_noise: true|false

  # For VR/AR environments
  virtual:
    platform: "[e.g., Unity, Unreal]"
    headset: "[e.g., Oculus Quest 2]"
    fov_degrees: "[value]"
    movement: "stationary|walking|teleport"
    interaction: "passive|active"
    photorealism: "high|moderate|low|stylized"

  # For physical installations
  physical:
    location: "indoor|outdoor"
    dimensions_meters: "[L x W x H]"
    materials: ["[list]"]
    maintenance: "live|preserved|artificial"
```

### 3. TEMPORAL PARAMETERS

```yaml
temporal:
  # Exposure timing
  exposure:
    duration_seconds: "[total exposure time]"
    presentation_type: "single|repeated|continuous"
    if_repeated:
      n_presentations: "[count]"
      isi_seconds: "[inter-stimulus interval]"
      block_structure: "[description]"

  # Timing in protocol
  protocol_position:
    after: "[what preceded - baseline, stressor, etc.]"
    before: "[what followed - task, measurement, etc.]"
    delay_to_measurement_seconds: "[time to DV measure]"

  # Dynamic stimuli
  if_dynamic:
    video_duration_seconds: "[value]"
    frame_rate_fps: "[value]"
    motion_type: "static|slow_motion|real_time|time_lapse"
```

### 4. SELECTION METHODOLOGY

```yaml
selection:
  # Source
  source:
    origin: "researcher_created|stock_library|prior_study|validated_set"
    if_library: "[e.g., IAPS, Nature Pics Database]"
    if_prior_study: "[citation]"

  # Selection criteria
  criteria:
    prescaling_study: true|false
    if_prescaling:
      n_raters: "[value]"
      rating_dimensions: ["[list]"]
      selection_threshold: "[e.g., top 20%]"
    matching_criteria:
      - "[e.g., luminance matched]"
      - "[e.g., complexity matched]"
      - "[e.g., color temperature matched]"

  # Variation
  variation:
    n_unique_stimuli: "[count]"
    counterbalancing: "yes|no|partial"
    randomization: "yes|no|pseudo"
```

### 5. CONTROL CONDITION

```yaml
control:
  # Control type
  type: "built_environment|geometric|blank|unrelated|no_control"

  # Control specifications (same structure as experimental)
  description: "[brief description]"
  matching:
    - "[matched on dimension 1]"
    - "[matched on dimension 2]"
  differences:
    - "[key difference 1 - defines manipulation]"
    - "[key difference 2]"

  # Minimal pair analysis
  minimal_pair:
    what_varies: "[the manipulated variable]"
    what_constant: "[controlled variables]"
    interpretation: "[what contrast allows us to infer]"
```

### 6. ECOLOGICAL VALIDITY ASSESSMENT

```yaml
ecological_validity:
  # Classification (from validation.py)
  level: "FIELD_NATURAL|FIELD_BUILT|LAB_VR|LAB_PHOTOS|LAB_ABSTRACT"

  # Representativeness
  representativeness:
    real_world_match: "high|moderate|low"
    target_context: "[what real-world setting is this meant to represent]"
    transfer_concerns:
      - "[concern 1]"
      - "[concern 2]"

  # Generalization boundaries
  generalization:
    generalizes_to:
      - "[context 1]"
      - "[context 2]"
    does_not_generalize_to:
      - "[context 1 with reason]"
      - "[context 2 with reason]"
```

### 7. DOMAIN FEATURES (CNfA-Specific)

```yaml
domain_features:
  # Kaplan ART theory markers
  art_theory:
    restorative_potential: "high|moderate|low"
    justification: "[why this rating]"

  # Appleton prospect-refuge markers
  prospect_refuge:
    prospect_level: "high|moderate|low|absent"
    refuge_level: "high|moderate|low|absent"
    balance: "prospect_dominant|refuge_dominant|balanced"

  # Biophilia hypothesis markers
  biophilia:
    nature_connection_strength: "high|moderate|low"
    evolutionary_relevance: "[savanna, forest, water body, etc.]"

  # Stress recovery markers (Ulrich SRT)
  stress_recovery:
    expected_valence: "positive|neutral|negative"
    arousal_level: "calming|neutral|activating"
    physiological_target: "[cortisol, HR, BP, etc.]"

  # Design implications
  design:
    applicable_building_types:
      - "[healthcare, office, residential, etc.]"
    dosage_implications:
      minimum_exposure: "[time or amount]"
      recommended_exposure: "[time or amount]"
```

---

## EXAMPLE: COMPLETE STIMULUS DOCUMENTATION

```yaml
stimulus_doc:
  schema: "ae.stimulus.v1"
  paper_id: "ulrich_1991_stress_recovery"
  stimulus_set_id: "ulrich_1991_nature_videos"
  created_at: "2026-02-09T10:00:00Z"

classification:
  modality: "visual"
  format: "video"
  environment_type:
    primary: "ENV_NATURAL_VEGETATION"
    secondary: ["ENV_NATURAL_WATER"]
  biophilic_elements:
    direct_nature:
      - "vegetation"
      - "water"
    indirect_nature:
      - "natural_colors"
    space_and_place:
      - "prospect"
  art_features:
    being_away: "high"
    fascination: "moderate"
    extent: "high"
    compatibility: "high"
  srt_features:
    positive_affect: "high"
    physiological_calming: "expected"
    attention_holding: "soft"

physical_specs:
  visual:
    dimensions:
      aspect_ratio: "4:3"
    display:
      medium: "monitor"
      resolution: "720x480"
      viewing_distance: "60cm"
    color:
      color_space: "RGB"
    image_properties:
      green_coverage_percent: 60
      sky_visibility_percent: 30
      water_visibility_percent: 15
      human_presence: "none"
      animal_presence: "none"
      built_elements_percent: 5

temporal:
  exposure:
    duration_seconds: 600
    presentation_type: "continuous"
  protocol_position:
    after: "stressor_industrial_accident_video"
    before: "physiological_measurements"
    delay_to_measurement_seconds: 0

selection:
  source:
    origin: "researcher_created"
  criteria:
    prescaling_study: true
    if_prescaling:
      n_raters: 30
      rating_dimensions: ["pleasantness", "naturalness"]
      selection_threshold: "top quartile"
  variation:
    n_unique_stimuli: 1
    counterbalancing: "no"
    randomization: "no"

control:
  type: "built_environment"
  description: "Video of traffic in urban setting"
  matching:
    - "duration matched"
    - "motion present"
  differences:
    - "no vegetation"
    - "presence of vehicles and traffic noise"
  minimal_pair:
    what_varies: "nature vs urban content"
    what_constant: "video format, duration, color calibration"
    interpretation: "differences attributable to nature content"

ecological_validity:
  level: "LAB_PHOTOS"
  representativeness:
    real_world_match: "moderate"
    target_context: "viewing nature from window or during walk"
    transfer_concerns:
      - "2D video lacks depth cues"
      - "no olfactory or haptic components"
      - "controlled viewing vs. natural exploration"
  generalization:
    generalizes_to:
      - "other video-based nature interventions"
      - "window views of nature (with caveats)"
    does_not_generalize_to:
      - "immersive VR (different presence level)"
      - "physical outdoor exposure (multi-sensory)"

domain_features:
  art_theory:
    restorative_potential: "high"
    justification: "high being_away and fascination ratings"
  prospect_refuge:
    prospect_level: "high"
    refuge_level: "low"
    balance: "prospect_dominant"
  biophilia:
    nature_connection_strength: "moderate"
    evolutionary_relevance: "mixed vegetation and water"
  stress_recovery:
    expected_valence: "positive"
    arousal_level: "calming"
    physiological_target: "heart_rate, blood_pressure, muscle_tension"
  design:
    applicable_building_types:
      - "healthcare_waiting_rooms"
      - "office_break_areas"
    dosage_implications:
      minimum_exposure: "5 minutes"
      recommended_exposure: "10+ minutes"
```

---

## VALIDATION CHECKLIST

Before finalizing stimulus documentation:

- [ ] **Classification complete** — Modality, format, environment type assigned
- [ ] **Physical specs documented** — Dimensions, display, timing specified
- [ ] **Selection methodology recorded** — Source, criteria, validation
- [ ] **Control condition described** — What was compared, what matched
- [ ] **Ecological validity assessed** — Level classified, transfer concerns noted
- [ ] **Domain features tagged** — ART, Prospect-Refuge, Biophilia, SRT markers
- [ ] **Design implications extracted** — Building types, dosage recommendations

---

## MAPPING TO TAXONOMY

| Stimulus Feature | Maps To |
|------------------|---------|
| Environment type | `contracts/vocab/environment_lookup.json` |
| Biophilic elements | Kellert's 14 patterns |
| ART features | `src/services/environment_taxonomy.py` |
| Ecological validity | `src/services/validation.py` EcologicalValidity enum |
| Outcomes targeted | `contracts/vocab/outcome_lookup.json` |

---

## REFERENCES

- Kellert, S. R., & Calabrese, E. F. (2015). The Practice of Biophilic Design.
- Kaplan, R., & Kaplan, S. (1989). The Experience of Nature. Cambridge University Press.
- Ulrich, R. S. (1991). Stress recovery during exposure to natural and urban environments. Journal of Environmental Psychology.
- Appleton, J. (1975). The Experience of Landscape. Wiley.

---

*This template integrates with ae.claim.v2 and ae.rule.v2 schemas via the stimulus_set_id field.*
