"""Article-type-specific extraction field contract.

Keeps D10/D15 from assuming an empirical-only schema for every paper.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FamilyFieldContract:
    family: str
    required_fields: tuple[str, ...]
    optional_fields: tuple[str, ...]


FAMILY_CONTRACTS: dict[str, FamilyFieldContract] = {
    "empirical_v2": FamilyFieldContract(
        family="empirical_v2",
        required_fields=(
            "research_question",
            "design_type",
            "participants",
            "stimuli_or_exposures",
            "measures",
            "findings",
            "limitations",
        ),
        optional_fields=("mechanisms", "moderators", "implementation_implications"),
    ),
    "observational_field": FamilyFieldContract(
        family="observational_field",
        required_fields=(
            "research_question",
            "design_type",
            "participants",
            "stimuli_or_exposures",
            "measures",
            "findings",
            "limitations",
        ),
        optional_fields=("mechanisms", "moderators", "implementation_implications"),
    ),
    "case_study": FamilyFieldContract(
        family="case_study",
        required_fields=(
            "research_question",
            "design_type",
            "participants",
            "stimuli_or_exposures",
            "measures",
            "findings",
            "limitations",
        ),
        optional_fields=("mechanisms", "moderators", "implementation_implications"),
    ),
    "mixed_methods": FamilyFieldContract(
        family="mixed_methods",
        required_fields=(
            "research_question",
            "design_type",
            "participants",
            "stimuli_or_exposures",
            "measures",
            "findings",
            "limitations",
        ),
        optional_fields=("mechanisms", "moderators", "implementation_implications"),
    ),
    "meta_analysis": FamilyFieldContract(
        family="meta_analysis",
        required_fields=(
            "review_question",
            "inclusion_exclusion_criteria",
            "evidence_base_summary",
            "synthesis_conclusions",
            "evidence_gaps",
        ),
        optional_fields=("pooled_effects", "risk_of_bias_assessment", "heterogeneity_sources"),
    ),
    "systematic_review": FamilyFieldContract(
        family="systematic_review",
        required_fields=(
            "review_question",
            "inclusion_exclusion_criteria",
            "evidence_base_summary",
            "synthesis_conclusions",
            "evidence_gaps",
        ),
        optional_fields=("pooled_effects", "risk_of_bias_assessment", "heterogeneity_sources"),
    ),
    "narrative_review": FamilyFieldContract(
        family="narrative_review",
        required_fields=(
            "review_question",
            "inclusion_exclusion_criteria",
            "evidence_base_summary",
            "synthesis_conclusions",
            "evidence_gaps",
        ),
        optional_fields=("pooled_effects", "risk_of_bias_assessment", "heterogeneity_sources"),
    ),
    "theoretical": FamilyFieldContract(
        family="theoretical",
        required_fields=(
            "central_proposition",
            "concept_definitions",
            "argument_structure",
            "mechanism_or_causal_logic",
            "testable_hypotheses_or_predictions",
        ),
        optional_fields=("bridge_warrants", "methodological_critiques"),
    ),
    "conceptual_framework": FamilyFieldContract(
        family="conceptual_framework",
        required_fields=(
            "central_proposition",
            "concept_definitions",
            "argument_structure",
            "mechanism_or_causal_logic",
            "testable_hypotheses_or_predictions",
        ),
        optional_fields=("bridge_warrants", "methodological_critiques"),
    ),
    "thought_piece": FamilyFieldContract(
        family="thought_piece",
        required_fields=(
            "central_proposition",
            "concept_definitions",
            "argument_structure",
            "mechanism_or_causal_logic",
            "testable_hypotheses_or_predictions",
        ),
        optional_fields=("bridge_warrants", "methodological_critiques"),
    ),
    "interview_study": FamilyFieldContract(
        family="interview_study",
        required_fields=(
            "research_focus",
            "sample_context",
            "data_collection_method",
            "coding_or_analysis_approach",
            "themes_or_constructs",
            "supporting_quotes_or_evidence_snippets",
            "transferability_limits",
        ),
        optional_fields=("derived_hypotheses", "mechanism_candidates"),
    ),
    "ethnographic": FamilyFieldContract(
        family="ethnographic",
        required_fields=(
            "research_focus",
            "sample_context",
            "data_collection_method",
            "coding_or_analysis_approach",
            "themes_or_constructs",
            "supporting_quotes_or_evidence_snippets",
            "transferability_limits",
        ),
        optional_fields=("derived_hypotheses", "mechanism_candidates"),
    ),
    "grounded_theory": FamilyFieldContract(
        family="grounded_theory",
        required_fields=(
            "research_focus",
            "sample_context",
            "data_collection_method",
            "coding_or_analysis_approach",
            "themes_or_constructs",
            "supporting_quotes_or_evidence_snippets",
            "transferability_limits",
        ),
        optional_fields=("derived_hypotheses", "mechanism_candidates"),
    ),
    "phenomenological": FamilyFieldContract(
        family="phenomenological",
        required_fields=(
            "research_focus",
            "sample_context",
            "data_collection_method",
            "coding_or_analysis_approach",
            "themes_or_constructs",
            "supporting_quotes_or_evidence_snippets",
            "transferability_limits",
        ),
        optional_fields=("derived_hypotheses", "mechanism_candidates"),
    ),
    "unknown": FamilyFieldContract(
        family="unknown",
        required_fields=("classification_diagnostics", "minimum_safe_summary"),
        optional_fields=(),
    ),
}


def get_family_contract(article_type_family: str | None) -> FamilyFieldContract:
    """Return the extraction contract for a template family."""
    key = str(article_type_family or "unknown").strip().lower()
    return FAMILY_CONTRACTS.get(key, FAMILY_CONTRACTS["unknown"])


def field_is_allowed(article_type_family: str | None, field_name: str) -> bool:
    """Check if a field is required/optional for this family."""
    contract = get_family_contract(article_type_family)
    return field_name in contract.required_fields or field_name in contract.optional_fields
