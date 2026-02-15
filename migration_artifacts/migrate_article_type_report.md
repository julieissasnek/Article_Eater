# ArticleType Migration Report

Canonical section: `enums.ArticleTypeCrosswalk`

## Outcome -> AE
- `case_study` -> `case_study`
- `cross_sectional_survey` -> `observational_field`
- `ethnographic_study` -> `ethnographic`
- `grounded_theory_study` -> `grounded_theory`
- `interview_study` -> `interview_study`
- `longitudinal_study` -> `observational_field`
- `meta_analysis` -> `meta_analysis`
- `mixed_methods` -> `mixed_methods`
- `narrative_review` -> `narrative_review`
- `observational_field_study` -> `observational_field`
- `phenomenological_study` -> `phenomenological`
- `quasi_experiment` -> `empirical_v2`
- `randomized_experiment` -> `empirical_v2`
- `systematic_review` -> `systematic_review`
- `theoretical` -> `theoretical`
- `thought_piece` -> `thought_piece`
- `unknown` -> `unknown`

## AE -> Outcome
- `case_study` -> ['case_study']
- `conceptual_framework` -> ['theoretical']
- `empirical_v2` -> ['randomized_experiment', 'quasi_experiment']
- `ethnographic` -> ['ethnographic_study']
- `grounded_theory` -> ['grounded_theory_study']
- `interview_study` -> ['interview_study']
- `meta_analysis` -> ['meta_analysis']
- `mixed_methods` -> ['mixed_methods']
- `narrative_review` -> ['narrative_review']
- `observational_field` -> ['cross_sectional_survey', 'longitudinal_study', 'observational_field_study']
- `phenomenological` -> ['phenomenological_study']
- `systematic_review` -> ['systematic_review']
- `theoretical` -> ['theoretical']
- `thought_piece` -> ['thought_piece']
- `unknown` -> ['unknown']

## Lossy conversions
- `empirical_v2` collapses: ['randomized_experiment', 'quasi_experiment']
- `observational_field` collapses: ['cross_sectional_survey', 'longitudinal_study', 'observational_field_study']

