"""
Auto-generated article-type crosswalk adapter.
Canonical contract section: enums.ArticleTypeCrosswalk
"""

from __future__ import annotations

from typing import Dict, List

OUTCOME_TO_AE: Dict[str, str] = {
  "case_study": "case_study",
  "cross_sectional_survey": "observational_field",
  "ethnographic_study": "ethnographic",
  "grounded_theory_study": "grounded_theory",
  "interview_study": "interview_study",
  "longitudinal_study": "observational_field",
  "meta_analysis": "meta_analysis",
  "mixed_methods": "mixed_methods",
  "narrative_review": "narrative_review",
  "observational_field_study": "observational_field",
  "phenomenological_study": "phenomenological",
  "quasi_experiment": "empirical_v2",
  "randomized_experiment": "empirical_v2",
  "systematic_review": "systematic_review",
  "theoretical": "theoretical",
  "thought_piece": "thought_piece",
  "unknown": "unknown"
}
AE_TO_OUTCOME: Dict[str, List[str]] = {
  "case_study": [
    "case_study"
  ],
  "conceptual_framework": [
    "theoretical"
  ],
  "empirical_v2": [
    "randomized_experiment",
    "quasi_experiment"
  ],
  "ethnographic": [
    "ethnographic_study"
  ],
  "grounded_theory": [
    "grounded_theory_study"
  ],
  "interview_study": [
    "interview_study"
  ],
  "meta_analysis": [
    "meta_analysis"
  ],
  "mixed_methods": [
    "mixed_methods"
  ],
  "narrative_review": [
    "narrative_review"
  ],
  "observational_field": [
    "cross_sectional_survey",
    "longitudinal_study",
    "observational_field_study"
  ],
  "phenomenological": [
    "phenomenological_study"
  ],
  "systematic_review": [
    "systematic_review"
  ],
  "theoretical": [
    "theoretical"
  ],
  "thought_piece": [
    "thought_piece"
  ],
  "unknown": [
    "unknown"
  ]
}
LOSSY_AE_MAPPINGS: Dict[str, List[str]] = {
  "empirical_v2": [
    "randomized_experiment",
    "quasi_experiment"
  ],
  "observational_field": [
    "cross_sectional_survey",
    "longitudinal_study",
    "observational_field_study"
  ]
}


def outcome_article_to_ae_template(outcome_article_type: str) -> str:
    key = outcome_article_type.strip().lower()
    if key not in OUTCOME_TO_AE:
        raise KeyError(f"Unknown Outcome article type: {outcome_article_type}")
    return OUTCOME_TO_AE[key]


def ae_template_to_outcome_articles(ae_template_family: str) -> List[str]:
    key = ae_template_family.strip().lower()
    if key not in AE_TO_OUTCOME:
        raise KeyError(f"Unknown AE template family: {ae_template_family}")
    return list(AE_TO_OUTCOME[key])


def ae_template_to_primary_outcome_article(ae_template_family: str) -> str:
    return ae_template_to_outcome_articles(ae_template_family)[0]


def is_lossy_ae_template(ae_template_family: str) -> bool:
    key = ae_template_family.strip().lower()
    return key in LOSSY_AE_MAPPINGS and len(LOSSY_AE_MAPPINGS[key]) > 1


def test_migration_lossless() -> None:
    # Round-trip outcome -> ae -> outcomes includes original (set-preserving)
    for outcome, ae in OUTCOME_TO_AE.items():
        outcomes = ae_template_to_outcome_articles(ae)
        assert outcome in outcomes

    # Strict round-trip for non-lossy mappings
    for ae, outcomes in AE_TO_OUTCOME.items():
        if len(outcomes) == 1:
            back = outcome_article_to_ae_template(outcomes[0])
            assert back == ae


if __name__ == "__main__":
    test_migration_lossless()
    print("ArticleType adapter self-test passed.")
