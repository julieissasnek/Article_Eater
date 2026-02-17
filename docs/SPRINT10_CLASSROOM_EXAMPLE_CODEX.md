# Sprint 10 Task 3.11: Primary School Classroom Worked Example
Date: 2026-02-17
Runner: Codex

## Scenario Inputs
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

## Profiles Evaluated
- Child profile: age 7
- Adult profile: age 35

## Building Evaluation Output (evaluate_building)
- Age 7 overall WIS: `50.0`
- Age 35 overall WIS: `50.0`
- Overall delta (age7 - age35): `0.0`
- Domain deltas (age7 - age35): all `0.0` (`CB`, `COL`, `CREA`, `DP`, `DT`, `E`)

## Developmental Moderation Check
Template-level probes show age sensitivity is present in compute-layer logic:
- Lifespan multiplier age 7: `1.35`
- Lifespan multiplier age 35: `1.0`
- L2 circadian ratio age 7: `1.6`
- L2 circadian ratio age 35: `1.391`

## Interpretation
- Pipeline execution status: PASS (both profiles run end-to-end and persist correctly).
- Differential age effect in orchestrator output: not yet visible for this classroom run (flat scores).
- Differential age effect in template-level computations: visible (higher child sensitivity multiplier and L2 age correction difference).

## Artifact
- Structured output: `data/review/sprint10_classroom_worked_example.json`
- Repro script: `scripts/run_primary_school_classroom_example.py`
