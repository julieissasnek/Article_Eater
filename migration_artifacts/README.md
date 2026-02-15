# Sprint 0.7 Migration Artifacts (Codex -> CC)

This directory contains non-destructive migration outputs generated from:

- `contracts/vocab/canonical_enums.json`
- `docs/02-15_09_Canonical_Decisions_Record_V1_0.md`

## Current hold state

- Do **not** apply these artifacts until CC finishes Sprint `0.1`-`0.3` merges.
- See `migration_artifacts/CC_REVIEW_HOLD_NOTE.md`.

## Artifact inventory

| File | Purpose | CC action |
|---|---|---|
| `migrate_gap_type.patch` | Patch to remove local `GapType` definitions and import canonical `src.epistemic.gap_types.GapType` in target AE services. | Review patch hunks, apply after path stabilization, run tests. |
| `migrate_gap_type_mapping.json` | Legacy -> canonical mapping used by GapType migration (`deprecated_aliases`). | Validate semantic mapping against canonical contract before patch apply. |
| `migrate_ci_shape_report.md` | Cross-repo scan report of scalar CI fields vs object CI fields with line numbers. | Use as rollout checklist for CI wire-shape normalization. |
| `ci_shape_adapter.py` | Lossless adapter functions: `ci_object_to_scalars()` and `scalars_to_ci_object()`. | Cherry-pick or port into consolidated location and wire into bridge code. |
| `migrate_claim_type_report.md` | BN ClaimType discovery + mapping to AE canonical ClaimType; unmapped flags. | Review mappings and unresolved values before integration. |
| `claim_type_adapter.py` | Adapter module with `bn_claim_to_canonical()` and `canonical_to_bn_claim()`. | Integrate at BN->AE boundary, then run affected tests. |
| `migrate_evidence_type_report.md` | BN/Tagging/Article Finder evidence-type discovery and canonical mapping status. | Resolve any remaining unmapped values before enforcement. |
| `evidence_type_adapter.py` | Cross-source EvidenceType adapter with source-aware reverse mappings. | Integrate into ingestion/bridge conversion points. |
| `migrate_article_type_report.md` | `TemplateFamily <-> ArticleType` crosswalk report with lossy mapping flags. | Confirm lossy cases are expected, then apply adapter. |
| `article_type_adapter.py` | Bidirectional article-type crosswalk adapter (`outcome_article_to_ae_template`, reverse funcs). | Integrate at AE/Outcome conversion boundaries. |
| `test_migration_lossless_output.txt` | Final one-pass output from all 5 `test_migration_lossless()` checks. | Keep as evidence for Sprint `0.7` gate review. |

## Generation commands (non-dry)

Executed from AE repo root:

```bash
python3 scripts/migrate_gap_type.py --output-dir migration_artifacts
python3 scripts/migrate_ci_shape.py --output-dir migration_artifacts
python3 scripts/migrate_claim_type.py --output-dir migration_artifacts
python3 scripts/migrate_evidence_type.py --output-dir migration_artifacts
python3 scripts/migrate_article_type.py --output-dir migration_artifacts
```

## Final lossless test run output

```text
scripts/migrate_gap_type.py: PASS
scripts/migrate_ci_shape.py: PASS
scripts/migrate_claim_type.py: PASS
scripts/migrate_evidence_type.py: PASS
scripts/migrate_article_type.py: PASS
```
