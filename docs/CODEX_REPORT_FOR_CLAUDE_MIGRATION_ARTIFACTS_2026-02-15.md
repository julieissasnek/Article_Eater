# Codex Report For Claude: Migration Adapters + Worktree Risks

Date: 2026-02-15  
Branch: `codex/cc-migration-artifacts-sprint-0-7`

## 1) What was completed

Codex ran all 5 migration scripts in non-dry mode and staged artifacts for CC review only:

- `migration_artifacts/migrate_gap_type.patch`
- `migration_artifacts/migrate_gap_type_mapping.json`
- `migration_artifacts/migrate_ci_shape_report.md`
- `migration_artifacts/ci_shape_adapter.py`
- `migration_artifacts/migrate_claim_type_report.md`
- `migration_artifacts/claim_type_adapter.py`
- `migration_artifacts/migrate_evidence_type_report.md`
- `migration_artifacts/evidence_type_adapter.py`
- `migration_artifacts/migrate_article_type_report.md`
- `migration_artifacts/article_type_adapter.py`
- `migration_artifacts/CC_REVIEW_HOLD_NOTE.md`

No source patch was applied to runtime code.

## 2) Hold condition (important)

Do not apply migration patch/adapters until Sprint `0.1` to `0.3` are merged (import paths and layout are expected to change).

## 3) Current worktree risk signal

Repo worktree is heavily dirty outside migration artifacts:

- `22` modified (`M`)
- `1` deleted (`D`)
- `132` untracked (`??`)

Implication: any broad commit/cherry-pick from this branch is risky. Use path-scoped operations only.

## 4) Migration findings CC should review first

1. EvidenceType unmapped values remain in tagging CSV surface:
   - `computed`, `image_2d`, `image_3d`, `metadata`, `sensor`
2. ArticleType crosswalk has lossy collapses:
   - `empirical_v2` collapses `randomized_experiment` + `quasi_experiment`
   - `observational_field` collapses `cross_sectional_survey` + `longitudinal_study` + `observational_field_study`
3. ClaimType mapping was clean on discovered BN values (no unmapped).
4. GapType patch targets two files:
   - `src/services/voi_search.py`
   - `src/services/discovery_funnel.py`

## 5) CI-shape scan caveat

`migrate_ci_shape_report.md` is broad and includes docs/archive/legacy package files, so file-count totals are noisy for active-runtime planning.  
Use it as discovery inventory, then filter to active source paths before applying code changes.

## 6) Next action after Sprint 1.2–1.3

When CC confirms Sprint `1.2` and `1.3` merged, run Sprint `1.4`:

`python3 scripts/check_enum_drift.py`

Then generate a fresh drift report against post-merge paths and update adapters/patches if import paths moved.
