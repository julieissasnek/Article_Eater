# Sprint 10 Salk Worked Example (Codex)
Date: 2026-02-17
Runner: Codex

## Input Scenario
- Building: Salk Institute (research institute, climate zone 3C)
- Feature set used:
  - `ceiling_height_m=2.75`
  - `floor_area_m2=18.0`
  - `illuminance_lux=350`
  - `ambient_noise_dba=38`
  - `window_area_ratio=0.40`
  - `primary_material=concrete`
  - `secondary_material=teak`
  - `has_nature_view=true`
  - `rt60_seconds=0.6`
  - `view_content=ocean_horizon`

## Occupant Profiles Evaluated
1. Young researcher (`age=30`)
2. Senior PI (`age=65`)
3. Visiting student (`age=22`)

## Results
- All three profiles produced the same output:
  - `overall_wis=50.0`
  - `overall_confidence=0.6`
  - `n_domains=6`
  - `severe_deficits=[]`
  - `data_gaps=[]`

## Observed Domain Pattern
- Top returned domains were:
  - `CB`
  - `COL`
  - `CREA`
  - `DP`
  - `DT`
- Each domain score observed in this run was `50.0` (placeholder baseline).

## Interpretation
- The orchestration path works end-to-end and returns structured output for all profiles.
- Age/lifespan differentiation is not yet expressed in this scenario because the current building evaluator is still placeholder-dominant for many active templates and does not yet route this feature set into calibrated age-sensitive computations.

## Conclusion
- Operational status: PASS (pipeline executes, persists, and reports for all three profiles).
- Demonstration realism: LIMITED (outputs are currently flat and not yet diagnostic).
