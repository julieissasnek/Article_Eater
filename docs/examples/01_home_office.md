# Home Office Walkthrough

This walkthrough uses Tier A quick assessment to evaluate a small home office with limited daylight and mostly neutral finishes.

## Command

```bash
./venv/bin/python -m src.cmr.cli quick-assess \
  --ceiling 2.6 \
  --area 12 \
  --nature-view none \
  --colors white,gray \
  --floor-surface level \
  --thermal hvac \
  --material laminate \
  --max-group 2 \
  --age 34
```

## Observed Output (excerpt)

- Overall Rating: `Fair`
- Wellness Score: `51.5/100`
- Strengths: `VF3 80.0`, `VIEW1 60.0`, `TP1 60.0`
- Needs Attention: `SC4 40.0`, `CREA3 35.0`
- Top recommendations:
  - Improve wayfinding with clearer signage or spatial landmarks
  - Introduce warmer or nature-inspired colors

## Interpretation

The space is functional but not yet restorative. Spatial proportions are acceptable (`VF3`), but circulation and navigational clarity are weak (`CREA3`, `SC4`) and likely increase low-level cognitive load during task switching.

Because there is no meaningful nature view, this office relies on interior design choices for restoration support. The fastest interventions are:

1. Establish explicit zones (focus desk, reading corner, standing/stretch spot).
2. Add warm/natural palette elements instead of all-cool neutral surfaces.
3. Add 1-2 visual nature proxies (plants or high-quality nature imagery) to improve visual recovery cues.

The command output also points to Tier B upgrades (light and sound measurements). Those should be the next step once low-cost layout/color changes are in place.
