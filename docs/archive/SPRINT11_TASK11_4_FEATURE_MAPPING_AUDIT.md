# Sprint 11 Task 11.4: Feature-to-Template Input Mapping Audit
Date: 2026-02-17
Runner: Codex

## Scope
- Added canonical mapping utilities in `src/cmr/feature_mapping.py`.
- Audited mapping coverage for every implemented compute template from `template_computations.py`.
- Verified required-argument coverage against a standard building feature payload.

## Coverage Summary
- Total implemented compute templates: `56`
- Fully mappable from standard building features: `20`
- Not fully mappable (missing required inputs): `36`

### Fully Mappable Templates
`COL2, CREA2, CREA4, L1, L2, L4, L5, MAT1, MAT2, MAT4, SC1, SC4, SOC2, T5, TP1, TP3, TP4, VF2, VF3, VIEW1`

### Templates With Missing Required Inputs
- `COL1`: `dominant_hue`, `saturation`
- `CREA1`: `phase`, `noise_db`, `light_lux`, `ceiling_rh`
- `CREA3`: `is_walking`, `path_has_nature`, `walk_duration_min`
- `L3`: `circadian_score`, `view_score`, `luminance_contrast_score`, `cct_score`, `dynamic_variation_score`
- `MAT3`: `visual_material`, `haptic_material`, `thermal_material`
- `MAT5`: `material_type`
- `OLF1`: `material_scent_match`, `functional_scent_match`, `is_threshold_crossing`
- `SC2`: `isovist_area_m2`, `isovist_perimeter_m`
- `SC3`: `sequence_length`, `pe_variation`
- `SOC1`: `actual_distance_cm`, `relationship_type`
- `SOC3`: `zone_type`, `boundary_clarity`, `group_size`
- `T1`: `spectral_slope`
- `T10`: `night_noise_dba`, `light_intrusion_lux`, `bedtime_regular`
- `T11`: `environmental_novelty_score`
- `T14`: `wayfinding_error_rate`, `crowding_level`, `time_pressure`
- `T15`: `has_thermostat_control`, `has_operable_windows`, `has_movable_furniture`
- `T16`: `exposure_duration_min`
- `T17`: `novelty_density`, `monotony_days`, `exploration_access`
- `T18`: `vertical_transition_count`, `vestibular_cue_quality`, `motion_disorientation_events`
- `T2`: `is_enclosed_niche`, `rear_protection`
- `T20`: `distraction_free_ratio`
- `T22`: `scene_gist_clarity`
- `T23`: `context_stability`, `cue_congruence`, `transition_frequency`
- `T24`: `spatial_sequence_clarity`
- `T27`: `iaq_co2_ppm`
- `T28`: `external_memory_support_score`, `signage_clarity`, `working_memory_load`
- `T32`: `acoustic_snr_db`, `rt60`
- `T33`: `rt60`, `room_volume_m3`
- `T38`: `spatial_nesting_levels`
- `T4`: `distraction_rate_per_hour`, `attentional_switch_cost`, `recovery_breaks_per_hour`
- `T40`: `unisensory_strength_avg`
- `T6`: `chronic_noise_exposure_dba`, `sleep_quality`, `control_perception`
- `T7`: `unpredictability_index`, `perceived_control`, `exposure_duration_hours`
- `T8`: `visual_access_grid`
- `TP2`: `spatial_change`, `light_change`, `sound_change`, `material_change`
- `VF1`: `curvature_ratio`

## Notes
- The mapping now explicitly separates:
  - direct feature aliasing,
  - derived values (e.g., `ceiling_rh`, privacy score/STC),
  - template defaults,
  - unresolved required inputs.
- This gives Step 2 in the orchestrator a deterministic way to:
  - map what can be computed now,
  - and report actionable data gaps where standard feature payload is insufficient.
