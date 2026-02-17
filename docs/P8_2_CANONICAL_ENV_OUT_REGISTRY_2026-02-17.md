# P8.2 Canonical Env/Out Registry

**Date**: 2026-02-17  
**Task**: P8.2 (Sprint 8 — Pipeline Reliability Hardening)  
**Author**: Codex

## What Was Implemented

Created a canonical registry build pipeline and artifact:

- Script: `scripts/build_canonical_env_out_registry.py`
- Output: `contracts/vocab/canonical_env_out_registry.json`

The registry merges:
1. Contract lookup vocabularies
   - `contracts/vocab/environment_lookup.json`
   - `contracts/outcome_vocab/outcome_lookup.json`
2. Production-observed node IDs
   - `data/production/realtime_tables.jsonl`
3. Rule-layer alignment diagnostics
   - `data/production/realtime_rules.jsonl`

## Registry Guarantees

- Canonical IDs are normalized to runtime node-ID form (`env.*`, `out.*`) using safe component normalization.
- Allowed IDs include canonical and generic forms.
- Unresolved IDs are explicitly tracked by prefix (`env.unresolved.*`, `out.unresolved.*`).
- Table vs rule layer alignment is reported in the same artifact.

## Current Snapshot (from generated registry)

- Environment canonical IDs: `424`
- Outcome canonical IDs: `24`
- Environment unresolved rows: `3,473`
- Outcome unresolved rows: `1,972`
- Table/rule row alignment:
  - `env_exact_row_alignment: true`
  - `out_exact_row_alignment: true`
- Observed unknown IDs not covered by canonical+generic sets:
  - Environment: `0`
  - Outcome: `0`

Interpretation:
- Registry coverage for observed non-unresolved node IDs is now complete.
- Remaining gap is unresolved-term resolution quality (P8.3), not allowed-ID registry coverage.

## Rebuild Command

```bash
python3 scripts/build_canonical_env_out_registry.py
```

