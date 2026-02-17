# Sprint 10 Open-Plan Office Worked Example (Antigravity)
Date: 2026-02-17
Runner: Antigravity

## Input Scenario
- Building: TechHub Open Plan Zone A (Office, climate zone 4C)
- Feature set used:
  - `ceiling_height_m=3.2`
  - `floor_area_m2=150.0`
  - `illuminance_lux=500`
  - `ambient_noise_dba=62` (High noise level)
  - `window_area_ratio=0.30`
  - `primary_material=plaster`
  - `secondary_material=glass`
  - `has_nature_view=false`
  - `rt60_seconds=0.8`
  - `view_content=city_street`
  - `desk_density_m2_per_person=8.0`

## Occupant Profiles Evaluated
1. Junior Dev (Introvert, age 24)
2. Sales Lead (Extrovert, age 45)
3. Neurodivergent Engineer (High Sensitivity, age 30)

## Results
- All three profiles produced the same output (consistent with Salk example findings):
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
  - `E`
- Each domain score observed was `50.0` (placeholder baseline).

## Interpretation
- The orchestration path works end-to-end for the open-plan scenario.
- Inputs like `ambient_noise_dba=62` (which should trigger `CREA2` disfluency or distraction) are being processed but likely hitting default baselines or uncalibrated interactions in the current template batch.
- Differential sensitivity (introvert vs. extrovert vs. high sensitivity) is not yet active in the current template logic or is washed out by the baseline overrides.

## Conclusion
- Operational status: PASS (pipeline executes, persists, and reports for all three profiles).
- Demonstration realism: LIMITED (outputs are currently flat, awaiting specific template interaction logic for noise and density).
