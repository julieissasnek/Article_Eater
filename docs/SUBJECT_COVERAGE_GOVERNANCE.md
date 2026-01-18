# Subject Typing Governance and Coverage

This document explains how subject typing (age bands, culture regions,
clinical populations, traits, and moderators) is governed in Article Eater,
and how reviewers can assess coverage and drift over time.

## 1. Subject Vocab

The canonical subject vocab lives in:

- `config/subject_vocab.json`

It defines allowed values for:

- `demographics.age_band`
- `demographics.education_band`
- `clinical_status.population`
- `culture.region`
- `culture.self_construal_profile`

The Admin UI loads this vocab via:

- `GET /api/admin/rulegraph_v2/subject_vocab`

and uses it to validate subject overrides when an admin edits a rule. If
an override uses a non-canonical value, the UI shows a warning but still
allows the save (so rare / edge populations can be represented).

## 2. Coverage Metrics

The RuleGraph v2 Admin tab now exposes coverage metrics via:

- `GET /api/admin/rulegraph_v2`

which returns:

- `events`: per-paper rule summaries
- `coverage.global`: global counts and percentages of rules with
  age band, culture region, clinical population, traits, and moderators.
- `coverage.by_paper`: the same metrics broken down per paper.

These metrics are rendered in the "Subject typing coverage" panel above
the RuleGraph v2 summary in the Admin GUI.

## 3. Governance Script: subject_coverage_report.py

For governance and Ruthless-style reviews, run:

```bash
python scripts/subject_coverage_report.py
```

This reads the current graph store and subject overrides and writes a
machine-readable snapshot to:

- `reports/subject_coverage_snapshot.json`

The snapshot includes:

- Global counts and percentages, analogous to the Admin UI coverage panel.
- Per-paper coverage entries, suitable for dashboards or further analysis.

## 4. Ruthless Panel Prompts

When running a Ruthless review, the panel should:

1. Inspect the coverage snapshot to see whether most rules have
   subject typing (age, culture, clinical status, traits, moderators).
2. Flag any domains where coverage is systematically thin (e.g. age
   bands present but culture region missing on most rules).
3. Provide concrete recommendations (e.g. "require culture.region for
   all new rules in this batch", or "add subject typing retrofits to
   high-impact legacy rules").

These checks, combined with BN export tests in `tests/test_subject_bn_pipeline.py`,
ensure that subject-aware rules are not only structurally consistent but
also sufficiently annotated to support downstream BN construction.


## 5. Manual QA checklist

For quick manual spot-checks of subject typing, reviewers can:

1. Open the RuleGraph v2 tab in the Admin GUI.
2. Confirm that the age band, education band, clinical population, culture region,
   and self-construal profile controls are populated from the canonical vocab
   in `config/subject_vocab.json`.
3. Verify that new overrides use those canonical values (e.g., age bands such as
   `18-25`, `26-40`, `41-65`; culture regions such as `India`, `North_America`,
   `Western_Europe`; and self-construal profiles such as `independent`,
   `interdependent`, `mixed`).
4. Use the "Subject typing coverage" panel and the "Download coverage JSON" button
   to spot cases where a paper has many rules but low coverage on a particular
   subject dimension.
