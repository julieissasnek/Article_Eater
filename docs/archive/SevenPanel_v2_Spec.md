# Seven-Panel v2 Specification

Seven-Panel v2 is a per-paper staging format. For each `paper_id`, it consists of up to seven panels:

- S: `panel_subjects` — subjects & sample.
- C: `panel_context` — setting, tasks, and activity.
- M: `panel_measures` — indicators and construct mappings.
- F: `panel_findings` — key findings and effect sizes.
- H: `panel_heterogeneity` — moderators and heterogeneity patterns.
- X: `panel_mechanisms` — mechanisms and theory.
- L: `panel_limits` — limits and generalization notes.

Each panel is a JSON object with a `type` field indicating its panel.

## S — Subjects & Sample (`panel_subjects`)

Fields:

- `paper_id: string`.
- `sample`:
  - `n_total: number | null`.
  - `demographics`: age statistics, age band, sex/gender distribution, education band.
  - `culture`: countries, region, self_construal_profile.
  - `clinical_status`: population, key inclusions, key exclusions.
- `traits_measured`: list of trait measures (name, scale, used_as_moderator).
- `notes`.

## C — Context & Task (`panel_context`)

Fields:

- `paper_id: string`.
- `tasks`: list of tasks, each with:
  - `task_id`, `name`,
  - `activity_type` (passive_viewing / active_navigation / cognitive_task / social_interaction / other),
  - `duration_min`,
  - `setting` (lab / VR / field / online / other),
  - `environment_type` (office / hospital / home / school / urban_outdoor / natural_outdoor / other),
  - `relevance_tags`, `notes`.
- `global_notes`.

## M — Measures & Indicators (`panel_measures`)

Fields:

- `paper_id: string`.
- `indicators`: list with:
  - `indicator_id`, `name`, `modality` (self_report / physiology / behavior / performance / neural / other),
  - `instrument`, `timescale` (phasic / tonic / retrospective / mixed / unknown),
  - `interpretation`, `notes`.
- `construct_mappings`: list with:
  - `construct`,
  - `indicator_ids`,
  - `notes`.

## F — Findings & Effect Sizes (`panel_findings`)

Fields:

- `paper_id: string`.
- `items`: list with:
  - `finding_id`,
  - `finding_text`,
  - `statistics` (p_value, effect_size, effect_size_type, sample_size, ci_lower, ci_upper),
  - `quote`, `page_span`,
  - optional `task_id`, `indicator_ids`,
  - optional `raw_abstract`.

## H — Heterogeneity & Moderators (`panel_heterogeneity`)

Fields:

- `paper_id: string`.
- `moderation_patterns`: list with:
  - `finding_id`,
  - `moderator`,
  - `dimension` (demographics / culture / traits / clinical / sensory / context / other),
  - `levels_compared`,
  - `pattern`,
  - `stats_summary`,
  - `evidence_snippet`,
  - `section`.

## X — Mechanisms & Theory (`panel_mechanisms`)

Fields:

- `paper_id: string`.
- `mechanism_claims`: list with:
  - `claim_id`,
  - `claim_text`,
  - `theory` (predictive_coding / biophilia / attention_restoration / stress_recovery / other / unknown),
  - `phenomenon`,
  - `role` (explains / is_consistent_with / challenges),
  - `strength` (speculative / consistent / strongly_supported),
  - `evidence_snippet`, `page_span`.

## L — Limits & Generalization (`panel_limits`)

Fields:

- `paper_id: string`.
- `generalization_notes`: generalization statements.
- `threats_to_validity`: list of named threats.
- `future_work_notes`: suggested next steps.
