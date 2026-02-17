# Sprint 10 Validation Sweep (Codex)
Date: 2026-02-17
Runner: Codex (branch `codex/cc-migration-artifacts-sprint-0-7`)

## 3.1a Template DB Validation
- Source: `ae.db`, table `templates`
- Total records: `150` (expected: 150) -> PASS
- Dedup status counts:
  - `active=52`, `superseded=9`, `residual=43`, `reference=7`, `gap=39`
  - Expected reference profile in plan: `~14 superseded, ~18 residual, ~10 gap, ~8 reference`
  - Result: MISMATCH (distribution drift)
- Generation counts: `gen1=118`, `gen2=32` (mix present) -> PASS (mixed generations present)
- Series coverage observed:
  - `AX, CB, COL, CREA, DP, DT, E, EC, IC, L, M, MAT, MS, MSI, NM, OLF, PP, SC, SN, SOC, SRT, T, TP, VF, VIEW`
- Missing critical fields (`dedup_status/generation/series/calibration_status`): none

## 3.1b Staging Links Validation
- Source: `data/web_persistence.db`, table `constraints`
- `constraint_type='tier2_theory_link'` count: `994` (expected: 1361) -> FAIL
- By target theory:
  - `theory:art=929`
  - `theory:biophilia=58`
  - `theory:embodied_cognition=4`
  - `theory:srt=2`
  - `theory:predictive_processing=1`
- Total constraints: `28,314` (expected reference in plan: ~27,320)
- Conclusion: staging link load is present but not matching plan counts/distribution.

## 3.1c WIS Module Spot-Check
- `cohens_d_to_wis` for `[-1.0, -0.5, -0.2, 0, 0.2, 0.5, 0.8, 1.0]`:
  - `[15.87, 30.85, 42.07, 50.00, 57.93, 69.15, 78.81, 84.13]`
- Monotonic increasing: `True`
- `d=0 -> 50.0` (PASS)
- `d=0.5 -> 69.15` (~69.1 PASS)
- `d=0.8 -> 78.81` (~78.8 PASS)
- `aggregate_overall_wis([90,15]) -> 36.74` (~36.7 PASS)
- Goldilocks sample:
  - center (`50`) -> `90.0`
  - outside (`30`) -> `30.0`

## 3.1d Interaction Matrix Spot-Check
- `get_interaction('A','C') -> {'sub_additivity': 0.76, ...}` PASS
- Triad 3-channel adjustment via `apply_all_interactions([L3, MAT4, VIEW1])`:
  - outputs: `L3=61.0`, `MAT4=73.2`, `VIEW1=85.4` (multiplier 1.22) PASS
- `get_interaction('VF3','CREA2B') -> single_chain=True` PASS
- `get_interaction('L1','SC4') -> None` PASS
- Note: pairwise `get_interaction('L3','MAT4')` returns `None`; triad behavior is applied in `apply_all_interactions`.

## 3.1e Building Evaluation End-to-End
- Executed `evaluate_building(...)` with Salk-like test context:
  - context: `{building_type: research_institute, climate_zone: 3C}`
  - features: `{ceiling_height_m: 3.0, floor_area_m2: 25.0, illuminance_lux: 400, ambient_noise_dba: 45}`
  - profile: `{age: 35, cultural_context: Western}`
- Result:
  - `status=complete`
  - `overall_wis=50.0`
  - `domain_scores=6`
  - `severe_deficits=[]`
  - `data_gaps=[]`
- Interpretation: pipeline runs end-to-end; current score behavior remains placeholder-dominant (uniform ~50 outputs).

## 3.1f Full Test Suite
- Command: `./venv/bin/pytest -q`
- Result: `3103 passed, 9 skipped, 9 warnings`
- Status: GREEN

## Summary
- Core Sprint 10 infrastructure is operational and test-green.
- Two material drifts remain for sprint acceptance:
  1. Tier2 staging-link count/distribution mismatch (`994` vs expected `1361`).
  2. Template dedup-status distribution differs substantially from plan reference profile.
