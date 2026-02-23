# CX V14 Lifespan U-Curve Validation Report

- Generated: 2026-02-17T07:58:28.278Z
- Template files scanned: 215
- Target templates: L1, L2, L3, L4, L5, MAT1, MAT2, MAT3, MAT4, MAT5, TP1, TP2, TP3, TP4, SOC1, SOC2, SOC3, CREA1, CREA2, CREA3, VIEW1
- Duplicate display IDs in scope: 5
- Invalid age_band_modifiers: 0
- Invalid lifespan_sensitivity_multiplier blocks: 0
- Boundary-ready templates (16/20/25): 21
- Boundary trend failures: 0

## Per-Template Results

| Display | Age Bands | Lifespan Block | Boundary Probe (16/20/25) |
|---|---|---|---|
| L1 | ok | ok | ready [1.0932, 1.0298, 1.0000] |
| L2 | ok | ok | ready [1.0932, 1.0298, 1.0000] |
| L3 | ok | ok | ready [1.0932, 1.0298, 1.0000] |
| L4 | ok | ok | ready [1.0932, 1.0298, 1.0000] |
| L5 | ok | ok | ready [1.0932, 1.0298, 1.0000] |
| MAT1 | ok | ok | ready [1.0932, 1.0298, 1.0000] |
| MAT2 | ok | ok | ready [1.0932, 1.0298, 1.0000] |
| MAT3 | ok | ok | ready [1.0932, 1.0298, 1.0000] |
| MAT4 | ok | ok | ready [1.0932, 1.0298, 1.0000] |
| MAT5 | ok | ok | ready [1.0932, 1.0298, 1.0000] |
| TP1 | ok | ok | ready [1.0932, 1.0298, 1.0000] |
| TP2 | ok | ok | ready [1.0932, 1.0298, 1.0000] |
| TP3 | ok | ok | ready [1.0932, 1.0298, 1.0000] |
| TP4 | ok | ok | ready [1.0932, 1.0298, 1.0000] |
| SOC1 | ok | ok | ready [1.0932, 1.0298, 1.0000] |
| SOC2 | ok | ok | ready [1.0932, 1.0298, 1.0000] |
| SOC3 | ok | ok | ready [1.0932, 1.0298, 1.0000] |
| CREA1 | ok | ok | ready [1.0932, 1.0298, 1.0000] |
| CREA2 | ok | ok | ready [1.0932, 1.0298, 1.0000] |
| CREA3 | ok | ok | ready [1.0932, 1.0298, 1.0000] |
| VIEW1 | ok | ok | ready [1.0932, 1.0298, 1.0000] |

## Findings

- Lifespan U-curve configuration is structurally valid for the V14 target template set.
- Boundary-age handoff (16→20→25) is monotonic toward adult baseline in all boundary-ready templates.

## Artifacts

- JSON: `data/review/cx_v14_lifespan_ucurve_validation_2026-02-17.json`
- Markdown: `docs/cx_v14_lifespan_ucurve_validation_report_2026-02-17.md`

