# Sprint 10 Primary School Classroom Worked Example (Codex)
Date: 2026-02-17
Runner: Codex

## Input Scenario
- Building: Primary school classroom (Task 3.11)
- Feature set used:
  - `ceiling_height_m=3.0`
  - `floor_area_m2=60.0`
  - `illuminance_lux=400`
  - `ambient_noise_dba=40`
  - `window_area_ratio=0.30`
  - `primary_material=timber_frame`
  - `secondary_material=linoleum`
  - `has_nature_view=true`
  - `rt60_seconds=0.4`
  - `view_content=playground_trees`

## Method
- Used `src/cmr/worked_examples.py::run_primary_school_classroom_example`.
- Evaluated age 7 and age 35 against the same classroom.
- Computed template-specific WIS overrides from core template computations (`VF3`, `L1`, `L2`, `L3`, `MAT2`, `SC1`, `SOC2`, `VIEW1`, `TP1`).
- Applied developmental/lifespan moderation around neutral WIS=50 using template-emitted multipliers (`restoration_multiplier`, `lifespan_multiplier`).
- Ran `evaluate_building(...)` for both profiles with the same template set and measured features.

## Results
### Age 7 (child)
- `overall_wis=85.21`
- Domain scores:
  - `VF=93.20`
  - `L=73.25`
  - `MAT=78.00`
  - `SC=63.00`
  - `SOC=100.00`
  - `VIEW=100.00`
  - `TP=97.25`

### Age 35 (teacher)
- `overall_wis=79.56`
- Domain scores:
  - `VF=82.00`
  - `L=67.64`
  - `MAT=78.00`
  - `SC=59.63`
  - `SOC=94.38`
  - `VIEW=97.50`
  - `TP=85.00`

### Delta (child minus teacher)
- `overall_wis=+5.65`
- Domain deltas:
  - `VF=+11.20`
  - `TP=+12.25`
  - `L=+5.61`
  - `SOC=+5.62`
  - `SC=+3.37`
  - `VIEW=+2.50`
  - `MAT=+0.00`

## Interpretation
- Developmental moderation is active in the expected direction: the same supportive classroom yields a stronger response for age 7 than age 35.
- Magnitude is plausible for a sensitivity-amplification model (overall delta `+5.65` WIS).
- Strongest shifts appear in movement/affordance and spatial-experience channels (`TP`, `VF`), with moderate shifts in light/social domains.

## Conclusion
- Operational status: PASS (Task 3.11 completed with measurable child-vs-teacher differentiation).
- Remaining limitation: this worked example uses calibrated template computations plus override bridging; full direct template execution in `evaluate_building` remains a future integration step.
