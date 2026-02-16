# Codex Finished: Migration Adapter Scripts (Sprint 0.7)

Status: Complete (implementation only; no direct source migrations applied).

Implemented scripts:
- `scripts/migrate_gap_type.py`
- `scripts/migrate_ci_shape.py`
- `scripts/migrate_claim_type.py`
- `scripts/migrate_evidence_type.py`
- `scripts/migrate_article_type.py`

Contract source enforced:
- `contracts/vocab/canonical_enums.json`
- Decision reference: `docs/02-15_09_Canonical_Decisions_Record_V1_0.md`

What each script guarantees:
- Supports `--dry-run`.
- Emits review artifacts (patch/report/adapter module), not in-place repo rewrites.
- Includes `test_migration_lossless()` round-trip checks.
- Flags unmapped or lossy conversions where applicable.

Quick validation run:
- `python3 -m py_compile scripts/migrate_gap_type.py scripts/migrate_ci_shape.py scripts/migrate_claim_type.py scripts/migrate_evidence_type.py scripts/migrate_article_type.py` -> pass

Suggested review/apply sequence:
1. Run each script with `--dry-run` and inspect artifacts.
2. Review unmapped/ lossiness sections first (`evidence_type`, `article_type`).
3. Apply approved patch/adapters in downstream PRs.
