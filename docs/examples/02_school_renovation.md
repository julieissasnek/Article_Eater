# School Renovation Walkthrough (Age 7 Moderation)

This example compares a classroom before and after renovation. Occupant age is set to `7` to reflect developmental sensitivity in the quick-assess flow.

## Before Renovation

```bash
./venv/bin/python -m src.cmr.cli quick-assess \
  --ceiling 2.5 \
  --area 55 \
  --nature-view urban \
  --colors white,gray \
  --floor-surface level \
  --thermal hvac \
  --material concrete \
  --max-group 20 \
  --age 7
```

Observed output:
- Overall Rating: `Fair`
- Wellness Score: `50.0/100`
- Needs Attention: `SC4 40.0`, `CREA3 35.0`
- Recommendations include wayfinding fixes, natural materials, warmer/nature-inspired colors.

## After Renovation

```bash
./venv/bin/python -m src.cmr.cli quick-assess \
  --ceiling 3.0 \
  --area 55 \
  --nature-view nature \
  --wayfinding \
  --walking-paths \
  --colors green,beige,blue \
  --color-varied \
  --floor-surface level \
  --stairs-standard \
  --thermal operable_windows \
  --material wood \
  --max-group 12 \
  --age 7
```

Observed output:
- Overall Rating: `Good`
- Wellness Score: `68.7/100`
- Strengths: `VF3 77.0`, `VIEW1 75.0`, `SC4 70.0`
- Recommendation: `Space performs well across assessed dimensions`

## Result

Renovation moved this classroom from borderline acceptable to clearly supportive (+`18.7` points). The biggest gains came from daylight/nature access, circulation clarity, and material changes (concrete-heavy to wood/natural palette). The age-7 run confirms these improvements hold under developmental moderation rather than only for adult assumptions.

Next measurement step remains Tier B instrumentation for lighting and acoustics to reduce uncertainty around L-series and sound-related templates.
