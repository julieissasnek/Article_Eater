# Web/BN Stabilization Report (2026-02-14)

## Completed
- Historical relation/bridge reprocess:
  - `scripts/reprocess_web_relations_and_bridges.py`
- Contradiction-focused quality pass:
  - `scripts/backfill_outcome_polarity_conflicts.py`
- Health gates + reporting:
  - `config/web_bn_health_thresholds.json`
  - `scripts/check_web_bn_health.py`
  - Integrated into `bin/scheduled_health_check.sh`

## Reprocess Outcome
- Added cross-paper constraints: `8680`
  - `explains`: `8663`
  - `supports`: `13`
  - `contradicts`: `4`
- Added bridges: `969`
- Legacy reclassification remained conservative:
  - `supports -> contradicts`: `1`

## Contradiction Boost Outcome
- Added polarity-conflict contradictions: `55` total in two passes (`51 + 4`)
- Contradiction count:
  - before: `10`
  - after: `65`

## Current Health Snapshot
- Web:
  - beliefs: `5880`
  - constraints: `17453`
  - bridges: `976`
  - relation mix:
    - supports: `8682` (`49.75%`)
    - explains: `8706` (`49.88%`)
    - contradicts: `65` (`0.37%`)
  - isolated beliefs: `1238` (`21.05%`)
- BN:
  - nodes: `3059`
  - edges: `2252`
  - unresolved nodes: `2855` (`93.33%`)
  - largest component: `845` (`27.62%`)
  - dangling edges: `0`
  - cycle check: `pass` (acyclic)

## Health Gates
- `minimum_viable`: **PASS** (`12/12`)
- `target`: **FAIL** (`0/7`)
  - misses: web isolation, contradiction depth, bridge count, BN density, BN unresolved rate, BN connectivity

## Idempotency
- `scripts/reprocess_web_relations_and_bridges.py --dry-run` returns zero pending changes.
- `scripts/backfill_outcome_polarity_conflicts.py --dry-run` returns zero pending changes.
