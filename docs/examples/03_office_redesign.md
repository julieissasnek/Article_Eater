# Open-Plan Office Redesign Walkthrough

This walkthrough compares a problematic open-plan office with a redesigned layout that introduces clearer zoning and lower crowding pressure.

## Baseline (Open Plan, Poor Privacy Conditions)

```bash
./venv/bin/python -m src.cmr.cli quick-assess \
  --ceiling 2.6 \
  --area 140 \
  --nature-view urban \
  --colors white,gray \
  --floor-surface level \
  --thermal hvac \
  --material concrete \
  --max-group 40 \
  --age 35
```

Observed output:
- Overall Rating: `Needs Attention`
- Wellness Score: `47.5/100`
- Needs Attention: `SC4 40.0`, `CREA3 35.0`, `VF3 25.0`
- Recommendations:
  - Improve spatial proportions/ceiling experience
  - Improve wayfinding and landmarks
  - Add natural materials and warmer colors

## Redesigned (Zoned + Material + View Improvements)

```bash
./venv/bin/python -m src.cmr.cli quick-assess \
  --ceiling 3.2 \
  --area 140 \
  --nature-view nature \
  --wayfinding \
  --walking-paths \
  --colors green,beige,wood \
  --color-varied \
  --floor-surface level \
  --stairs-standard \
  --thermal operable_windows \
  --material wood \
  --max-group 8 \
  --age 35
```

Observed output:
- Overall Rating: `Good`
- Wellness Score: `66.0/100`
- Strengths: `VIEW1 75.0`, `SC4 70.0`, `TP1 70.0`

## Result

The redesign improves score by +`18.5` points and eliminates all severe quick-assess deficits. Mechanistically, the change is consistent with moving from high-crowding, low-legibility open-plan conditions to a layout with better visual recovery opportunities and navigational clarity.

For implementation planning, this suggests a phased path:
1. First wave: zoning/wayfinding and capacity control (`max-group` reduction).
2. Second wave: material and daylight/view upgrades.
3. Third wave: Tier B measurements for lighting and acoustics to lock in calibration-quality confidence.
