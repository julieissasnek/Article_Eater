# P8.6 Quality Gate Fix

**Date**: 2026-02-17

## Fix

Adjusted `article_type_metadata_coverage` in `scripts/check_table_extraction_quality.py` to use typed rows as denominator:

- Before: `typed_metadata / queue_rows` (false failure)
- After: `typed_metadata / typed_rows` (correct completeness metric)

Also gated failure check on `typed_rows` existence.

## Verification

Command:
```bash
python3 scripts/check_table_extraction_quality.py --soft
```

Result:
- `quality_gate: PASS`
- `article_type_metadata_coverage: 1.0000`

