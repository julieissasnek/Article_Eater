# External-Evidence Direction Pilot (2-of-3 Consensus)

Date: 2026-02-19

## Scope
Pilot adjudication on theory-direction tension claims using external evidence and a conservative `2-of-3` vote rule:
- Vote 1: current extractor direction
- Vote 2: primary source direction/relevance
- Vote 3: secondary source direction/relevance

If at least 2 votes did not support a precise signed direction for the mapped IV->DV, direction was set to `unknown`.

## Artifacts
- Overrides: `data/review/direction_overrides.external_evidence_pilot.json`
- Baseline extraction: `data/production/structured_claims.external_pilot_baseline.json`
- Pilot extraction: `data/production/structured_claims.external_pilot_with_overrides.json`
- Baseline web report: `docs/web_health_external_pilot_baseline.md`
- Pilot web report: `docs/web_health_external_pilot_with_overrides.md`

## Commands Used
```bash
python3 -m src.extraction.batch_extract --method enhanced --no-direction-overrides --no-adjudication-packets --output-path data/production/structured_claims.external_pilot_baseline.json
python3 -m src.extraction.batch_extract --method enhanced --direction-overrides-path data/review/direction_overrides.external_evidence_pilot.json --no-adjudication-packets --output-path data/production/structured_claims.external_pilot_with_overrides.json

python3 scripts/rebuild_web_db.py --db-path data/production/web_external_pilot_baseline.db --input data/production/structured_claims.external_pilot_baseline.json --report-path docs/web_health_external_pilot_baseline.md
python3 scripts/rebuild_web_db.py --db-path data/production/web_external_pilot_with_overrides.db --input data/production/structured_claims.external_pilot_with_overrides.json --report-path docs/web_health_external_pilot_with_overrides.md
```

## Results
- Overrides reviewed: 21
- Overrides applied: 20
- Theory-direction tension claims: `37 -> 18` (resolved 20)
- Theory-null tension claims: `1 -> 0`
- Direction distribution:
  - `increase`: `151 -> 143`
  - `decrease`: `56 -> 46`
  - `no_effect`: `4 -> 3`
  - `unknown`: `171 -> 190`

## Web Impact
- Contradictions: `8 -> 8` (unchanged)
- Contradictions suppressed (low direction trust): `41 -> 29`

Interpretation: the pilot substantially reduced theory-tension flags by removing direction assignments unsupported by external evidence for mapped IV->DV pairs. Direct contradiction edges did not change in this sample, but low-trust suppression shifted.

## Notable Corrective Signal
One high-value direction correction changed sign:
- `abs:doi:10.1177/0013916518824631:C005`
  - `decrease -> increase`
  - external evidence indicates higher bedroom ceiling height is associated with reduced negative crowding effects.

## Prompt Policy Adjustment
To avoid over-constraining adjudicators, direction packet generation was updated to request open-ended evidence retrieval across full-paper and credible external sources rather than abstract-only guidance.
