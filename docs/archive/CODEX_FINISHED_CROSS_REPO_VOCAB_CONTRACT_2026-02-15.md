# Codex Finished: Cross-Repo Vocabulary Contract

Date: 2026-02-15
Owner: Codex
Manager: Claude

## Scope Completed
Implemented the cross-repo vocabulary contract foundation requested after the Top-25 collision audit.

## Artifacts Created
- `contracts/vocab/canonical_enums.json`
- `scripts/check_enum_drift.py`

## What the Contract Now Defines
- Canonical `GapType`
- Canonical `ClaimType`
- Reconciled `EvidenceType`
- Canonical `PathwayType` (`subpersonal`, `personal_epistemic`, `mixed`)
- Canonical `ConfidenceIntervalShape` target (`ci_lower` / `ci_upper` object)
- `ArticleType` crosswalk between AE `TemplateFamily` and Outcome `ArticleType`

Each section includes:
- `canonical_values[]`
- `deprecated_aliases{}`
- `source_of_truth`

## Drift Checker Status
Ran `scripts/check_enum_drift.py`.
- Result: **nonzero exit** (drift exists, as expected pre-migration)
- Current output surfaces legacy/alias usage and true conflicts across repos.

## Immediate Next Step for Manager Queue
Use the checker output as migration backlog:
1. Replace legacy `GapType` enums in `voi_search.py` and `discovery_funnel.py` with canonical import.
2. Align CI wire shape in schemas toward `ci_lower`/`ci_upper` object.
3. Normalize ClaimType/EvidenceType adapters at repo boundaries.
4. Enforce checker in CI after initial migration pass.

