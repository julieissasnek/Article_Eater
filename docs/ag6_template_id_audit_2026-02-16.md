# AG6 Template ID Canonicalization Audit (2026-02-16)

## Scope
Audited `data/templates/*.json` for canonical ID shape drift.

Canonical checks used:
- `template_id`: `^[A-Z0-9]+(?:_[A-Z0-9]+)*_[0-9]{3}$`
- `display_id`: `^(T|M|AX|L|MAT|SC)[0-9]+$`

## Findings
- Files scanned: 81
- Missing `template_id`: 0
- Duplicate `template_id`: 0
- Non-canonical `template_id`: 4
- Non-canonical `display_id`: 13

### Non-canonical `template_id`
- `AX1.json`: `AX1`
- `AX3.json`: `AX3`
- `AX5.json`: `AX5`
- `AX6.json`: `AX6`

### Non-canonical `display_id` (legacy namespace drift)
- `CB2`, `DP2`, `DT1`, `EC2`, `IC2`, `MS2`, `MSI2`, `NM2`, `NM3`, `PP4`, `SN1`, `SN2`, `SRT1`

## Impact
- Runtime integrity is currently unaffected by these names (registry/drift checks can pass).
- Full canonicalization is a **cross-registry migration** task, because template IDs are referenced in:
  - `data/reductions/*.json`
  - `data/attributes/*.json`
  - `interactions[*].template_id` inside template files
  - likely docs/tests relying on known IDs.

## Recommendation
Execute a dedicated ID migration with an explicit old->new mapping table and global reference rewrite, then rerun:
- `npx tsc --noEmit`
- `npx ts-node scripts/check_theory_drift.ts`
- `node scripts/check_template_contract_compatibility.js`
