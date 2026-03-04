"""
Language Adaptation Service — adapts answer content for different user types.

Not cosmetic reformatting — structural adaptation of:
- Presupposition frame (what background knowledge is assumed)
- Answer structure (mechanism-first vs recommendation-first vs theory-first)
- Vocabulary register (technical vs translated vs scaffolded)
- Uncertainty communication (credence intervals vs verbal qualifiers vs risk language)
- Citation style (APA with DOIs vs "studies show" vs key-papers-to-read)
- Actionability level (design parameters vs theoretical implications vs learning paths)

Created: 2026-03-02
Author: Claude Code
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
import logging

logger = logging.getLogger(__name__)


class UserType(Enum):
    """User persona types per QA_PERSONALIZATION_SPEC_2026-03-02."""
    ARCHITECT = "architect"
    RESEARCHER = "researcher"
    STUDENT = "student"
    REVIEWER = "reviewer"
    QUICK_LOOKUP = "quick_lookup"


@dataclass
class ArchitectProfile:
    """Architect / Practitioner-Designer profile."""
    user_type: str = "architect"
    presupposition: str = (
        "Understands basic design language and evidence-based design concepts. "
        "May lack deep psychological theory or research methods background. "
        "Knows what 'evidence-based design' means. Familiar with constraints: "
        "budget, buildability, codes, timelines."
    )
    primary_question_mode: List[str] = field(default_factory=lambda: [
        "What should I do? (prescriptive, not descriptive)",
        "What's the evidence for X in my context? (contextual, bounded)",
        "What's the minimum effective dose? (practical thresholds)",
        "What can I measure to know if it's working? (KPIs, proxy metrics)"
    ])
    answer_structure: List[str] = field(default_factory=lambda: [
        "design_parameter",
        "scope_of_applicability",
        "evidence_summary",
        "practical_implications",
        "measurement_approach",
        "contraindications",
        "cost_effectiveness"
    ])
    vocabulary: str = "plain_english_plus_design_terms"
    uncertainty_style: str = "percentage_with_qualifier"
    citation_style: str = "minimal_author_year"
    actionability: float = 0.70  # 70% of answer should enable decisions
    completeness_criteria: List[str] = field(default_factory=lambda: [
        "Design parameter(s): specific, measurable values or ranges",
        "Scope of applicability: population, setting, boundary conditions",
        "Evidence summary: strength (EBD level), number of studies, effect size range",
        "Practical implications: what to do, what to avoid, trade-offs",
        "Measurement approach: how to know if the design worked",
        "Contraindications: when guidance doesn't apply or backfires",
        "Cost-effectiveness: ROI or priority ranking vs other interventions"
    ])


@dataclass
class ResearcherProfile:
    """Senior Researcher profile."""
    user_type: str = "researcher"
    presupposition: str = (
        "PhD-level training in their discipline. Understands research design, "
        "statistics, and limitations. Expects nuance: contested findings, "
        "effect size variability, scope conditions. Wants to know what the "
        "literature really says, not a simplified summary."
    )
    primary_question_mode: List[str] = field(default_factory=lambda: [
        "What's the state of the art? (comprehensive, with disputes)",
        "What's the evidence quality? (methodology, limitations, confounds)",
        "Where are the gaps? (what's unknown, what needs studying)",
        "What would change if X finding were retracted? (sensitivity analysis)",
        "How strong is this really? (effect sizes, heterogeneity, publication bias)"
    ])
    answer_structure: List[str] = field(default_factory=lambda: [
        "mechanism",
        "effect_sizes_with_ci",
        "scope_conditions",
        "methodology_summary",
        "quality_issues",
        "heterogeneity",
        "competing_explanations",
        "research_gaps",
        "uncertainty_quantified",
        "conflicts"
    ])
    vocabulary: str = "technical_precise"
    uncertainty_style: str = "credence_interval_with_explanation"
    citation_style: str = "full_apa_with_dois"
    actionability: float = 0.20  # 20% should enable decisions, 80% satisfy curiosity
    completeness_criteria: List[str] = field(default_factory=lambda: [
        "Effect sizes with confidence intervals or full distribution",
        "Mechanism(s) with supporting evidence at each step",
        "Scope conditions with evidence for each",
        "Methodology summary: common designs, sample sizes, outcome measures",
        "Quality issues: publication bias, replication rate, contested interpretations",
        "Heterogeneity: effect size varies by what? (moderators identified)",
        "Competing explanations: alternative theories that fit some data",
        "Research gaps: what's missing, what would move the field forward",
        "Uncertainty quantified: credence intervals, not point estimates",
        "Conflicts: where does this community debate each other?"
    ])


@dataclass
class StudentProfile:
    """Graduate Student profile."""
    user_type: str = "student"
    presupposition: str = (
        "Developing expert knowledge; basic research literacy. Wants to "
        "understand 'why' things work, not just 'what works'. Uncertain about "
        "theory landscape and field politics. Needs to understand the "
        "foundations and doesn't know what they don't know yet."
    )
    primary_question_mode: List[str] = field(default_factory=lambda: [
        "How does theory X work? (foundational understanding)",
        "What are the key papers? (seminal works, must-read articles)",
        "What's contested? (debates that matter for research direction)",
        "Where should I focus my work? (thesis opportunities, open questions)",
        "What methodologies dominate this area? (what training do I need)"
    ])
    answer_structure: List[str] = field(default_factory=lambda: [
        "theoretical_framework",
        "key_papers",
        "evidence_hierarchy",
        "theory_map",
        "historical_context",
        "practitioner_applications",
        "methods_commonly_used",
        "open_questions",
        "field_politics",
        "learning_path"
    ])
    vocabulary: str = "accessible_plus_technical"
    uncertainty_style: str = "credence_with_brief_explanation"
    citation_style: str = "author_year_with_context"
    actionability: float = 0.30  # 30% enables research planning, 70% satisfies learning
    completeness_criteria: List[str] = field(default_factory=lambda: [
        "Theoretical framework explained from first principles",
        "Key papers with brief context about why they matter",
        "Evidence hierarchy: established vs contested vs speculative",
        "Theory map: how this theory connects to others",
        "Historical context: how did we get here? What changed?",
        "Practitioner applications if any: does this matter outside academia?",
        "Methods commonly used and their strengths/limitations",
        "Open questions: interesting research directions",
        "Field politics: gently, who disagrees and about what?",
        "Learning path: 'if you want to master this, here's the sequence'"
    ])


@dataclass
class ReviewerProfile:
    """Systematic Reviewer profile."""
    user_type: str = "reviewer"
    presupposition: str = (
        "Expertise in systematic review methodology (PRISMA, Cochrane). "
        "Needs machine-readable, reproducible output. Often filtering evidence "
        "for specific inclusion criteria. Wants structured data that can be "
        "exported and analyzed independently."
    )
    primary_question_mode: List[str] = field(default_factory=lambda: [
        "All evidence for outcome X (complete enumeration, not synthesis)",
        "Studies matching criteria Y (filtered by methodology, population, etc.)",
        "Export data for meta-analysis (structured, computable format)",
        "GRADE ratings (standardized quality assessment)",
        "Effect heterogeneity breakdown (effects split by study characteristics)"
    ])
    answer_structure: List[str] = field(default_factory=lambda: [
        "study_level_data",
        "grade_assessment",
        "inclusion_exclusion_criteria",
        "heterogeneity_metrics",
        "publication_bias_assessment",
        "sensitivity_analyses",
        "subgroup_analyses",
        "forest_plot_data",
        "search_strategy_documented",
        "excluded_studies"
    ])
    vocabulary: str = "standardized_prisma"
    uncertainty_style: str = "grade_level_plus_metrics"
    citation_style: str = "complete_bibliographic"
    actionability: float = 1.0  # 100% of output should be actionable for synthesis
    completeness_criteria: List[str] = field(default_factory=lambda: [
        "Study-level data (exportable table format)",
        "GRADE assessment for each outcome",
        "Inclusion/exclusion criteria applied (transparency)",
        "Heterogeneity metrics (I², Q test, explanation of variance)",
        "Publication bias assessment (funnel plot or Egger test)",
        "Sensitivity analyses: remove low-quality studies, show effect change",
        "Subgroup analyses: effects by population, setting, intervention type",
        "Forest plot data: ready for meta-analysis software import",
        "Search strategy documented: how studies were found (reproducibility)",
        "Excluded studies (optionally): high-quality studies that didn't meet criteria"
    ])


@dataclass
class QuickLookupProfile:
    """Quick Lookup profile."""
    user_type: str = "quick_lookup"
    presupposition: str = (
        "Busy professional or student with limited time. Wants the answer in "
        "<2 minutes. May lack domain expertise; needs credence translated. "
        "Just wants: Is this true and how confident are you?"
    )
    primary_question_mode: List[str] = field(default_factory=lambda: [
        "Yes/no questions: Is X supported by evidence?",
        "Quick credence: How confident should I be about Y?",
        "Simple facts: How many studies on Z?",
        "Directional: Does this help or hurt?"
    ])
    answer_structure: List[str] = field(default_factory=lambda: [
        "headline",
        "credence_level",
        "why_mechanism",
        "scope",
        "caveat"
    ])
    vocabulary: str = "plain_english_no_jargon"
    uncertainty_style: str = "simple_label"
    citation_style: str = "none_or_study_count"
    actionability: float = 0.90  # 90% should help decide quickly
    completeness_criteria: List[str] = field(default_factory=lambda: [
        "Headline (one sentence)",
        "Credence level (high/moderate/low)",
        "Why (one-sentence mechanism)",
        "Scope (one sentence: for whom/when)",
        "Caveat (one sentence: main limitation)"
    ])


class LanguageAdaptationService:
    """Adapts answer content for different user types."""

    USER_PROFILES = {
        UserType.ARCHITECT: ArchitectProfile(),
        UserType.RESEARCHER: ResearcherProfile(),
        UserType.STUDENT: StudentProfile(),
        UserType.REVIEWER: ReviewerProfile(),
        UserType.QUICK_LOOKUP: QuickLookupProfile(),
    }

    def __init__(self):
        """Initialize the service."""
        logger.info("Language Adaptation Service initialized")

    def get_profile(self, user_type: UserType) -> Dict[str, Any]:
        """Get the profile for a user type as a dictionary."""
        profile = self.USER_PROFILES.get(user_type)
        if not profile:
            logger.warning(f"Unknown user type: {user_type}. Defaulting to researcher.")
            profile = self.USER_PROFILES[UserType.RESEARCHER]

        return {
            'user_type': profile.user_type,
            'presupposition': profile.presupposition,
            'primary_question_mode': profile.primary_question_mode,
            'answer_structure': profile.answer_structure,
            'vocabulary': profile.vocabulary,
            'uncertainty_style': profile.uncertainty_style,
            'citation_style': profile.citation_style,
            'actionability': profile.actionability,
            'completeness_criteria': profile.completeness_criteria,
        }

    def adapt(self, answer: Dict[str, Any], user_type: UserType) -> Dict[str, Any]:
        """
        Adapt a full answer for the given user type.

        Args:
            answer: Dictionary with 'headline', 'mechanism', 'evidence', 'scope', 'caveats'
            user_type: UserType enum

        Returns:
            Adapted answer dictionary for the user type

        SUCCESS CONDITIONS (SC-LA-ADAPT):
        - SC-LA-ADAPT-1: Returns dict with 'user_type', 'original_answer', 'structure' keys
        - SC-LA-ADAPT-2: user_type in output matches input user_type.value
        - SC-LA-ADAPT-3: 'original_answer' key contains unmodified input answer dict
        - SC-LA-ADAPT-4: 'structure' key contains result of get_answer_structure(user_type)
        - SC-LA-ADAPT-5: If 'headline' in input, adapted output includes adapted headline
        - SC-LA-ADAPT-6: If 'mechanism' in input, adapted output includes adapted mechanism
        - SC-LA-ADAPT-7: If 'evidence' in input, adapted output includes adapted evidence dict
        - SC-LA-ADAPT-8: If 'scope' in input, adapted output includes adapted scope
        - SC-LA-ADAPT-9: If 'caveats' in input, adapted output includes adapted caveats list
        - SC-LA-ADAPT-10: If 'credence' in input, adapted output includes uncertainty formatting
        - SC-LA-ADAPT-11: If 'citations' in input, adapted output includes formatted citations list
        - SC-LA-ADAPT-12: Handles all UserType enum values without exception
        - SC-LA-ADAPT-13: Returns non-empty dict for non-empty input answer
        """
        profile = self.USER_PROFILES.get(user_type, self.USER_PROFILES[UserType.RESEARCHER])

        adapted = {
            'user_type': user_type.value,
            'original_answer': answer,
            'structure': self.get_answer_structure(user_type),
        }

        # Adapt each component
        if 'headline' in answer:
            adapted['headline'] = self._adapt_headline(answer['headline'], user_type)

        if 'mechanism' in answer:
            adapted['mechanism'] = self._adapt_mechanism(answer['mechanism'], user_type)

        if 'evidence' in answer:
            adapted['evidence'] = self._adapt_evidence(answer['evidence'], user_type)

        if 'scope' in answer:
            adapted['scope'] = self._adapt_scope(answer['scope'], user_type)

        if 'caveats' in answer:
            adapted['caveats'] = self._adapt_caveats(answer['caveats'], user_type)

        if 'credence' in answer:
            adapted['credence'] = self._adapt_uncertainty(
                answer.get('credence', 0.5),
                answer.get('credence_range', (None, None)),
                user_type
            )

        if 'citations' in answer:
            adapted['citations'] = self._adapt_citations(answer['citations'], user_type)

        return adapted

    def adapt_belief_presentation(self, belief: Dict[str, Any], user_type: UserType) -> Dict[str, Any]:
        """
        Adapt how a single belief is presented.

        Args:
            belief: Dictionary with 'content', 'credence', 'evidence_type', etc.
            user_type: UserType enum

        Returns:
            Adapted belief for the user type

        SUCCESS CONDITIONS (SC-LA-BELIEF):
        - SC-LA-BELIEF-1: Returns dict with 'content' and 'user_type' keys
        - SC-LA-BELIEF-2: user_type in output matches input user_type.value
        - SC-LA-BELIEF-3: 'content' is vocabulary-translated for the user type
        - SC-LA-BELIEF-4: If 'credence' in input, adapted output includes uncertainty formatting
        - SC-LA-BELIEF-5: Architect type includes 'design_parameter' if present in input
        - SC-LA-BELIEF-6: Architect type includes 'measurement_kpi' if present in input
        - SC-LA-BELIEF-7: Researcher type includes 'effect_size' if present in input
        - SC-LA-BELIEF-8: Researcher type includes 'confidence_interval' if present in input
        - SC-LA-BELIEF-9: Researcher type includes 'methodology_notes' if present in input
        - SC-LA-BELIEF-10: Student type includes 'key_papers' if present in input
        - SC-LA-BELIEF-11: Student type includes 'learning_path' if present in input
        - SC-LA-BELIEF-12: Reviewer type includes 'grade_rating' if present in input
        - SC-LA-BELIEF-13: Reviewer type includes 'study_metadata' if present in input
        - SC-LA-BELIEF-14: Quick lookup content is truncated to 100 chars with ellipsis
        - SC-LA-BELIEF-15: Handles all UserType enum values without exception
        """
        profile = self.USER_PROFILES.get(user_type, self.USER_PROFILES[UserType.RESEARCHER])

        adapted = {
            'content': belief.get('content', ''),
            'user_type': user_type.value,
        }

        # Vocabulary adaptation
        adapted['content'] = self._translate_vocabulary(
            adapted['content'],
            user_type
        )

        # Credence presentation
        if 'credence' in belief:
            adapted['credence'] = self._adapt_uncertainty(
                belief['credence'],
                belief.get('credence_range', (None, None)),
                user_type
            )

        # Add structure-specific fields
        if user_type == UserType.ARCHITECT:
            if 'design_parameter' in belief:
                adapted['design_parameter'] = belief['design_parameter']
            if 'measurement_kpi' in belief:
                adapted['measurement_kpi'] = belief['measurement_kpi']

        elif user_type == UserType.RESEARCHER:
            if 'effect_size' in belief:
                adapted['effect_size'] = belief['effect_size']
            if 'confidence_interval' in belief:
                adapted['confidence_interval'] = belief['confidence_interval']
            if 'methodology_notes' in belief:
                adapted['methodology_notes'] = belief['methodology_notes']

        elif user_type == UserType.STUDENT:
            if 'key_papers' in belief:
                adapted['key_papers'] = belief['key_papers']
            if 'learning_path' in belief:
                adapted['learning_path'] = belief['learning_path']

        elif user_type == UserType.REVIEWER:
            if 'grade_rating' in belief:
                adapted['grade_rating'] = belief['grade_rating']
            if 'study_metadata' in belief:
                adapted['study_metadata'] = belief['study_metadata']

        elif user_type == UserType.QUICK_LOOKUP:
            # Keep it very brief
            adapted['content'] = adapted['content'][:100] + "..." if len(adapted['content']) > 100 else adapted['content']

        return adapted

    def adapt_uncertainty(self, credence: float, ci: Tuple[Optional[float], Optional[float]], user_type: UserType) -> str:
        """
        Format uncertainty for user type.

        Args:
            credence: Point estimate (0.0–1.0)
            ci: Confidence interval as (lower, upper)
            user_type: UserType enum

        Returns:
            Formatted uncertainty string
        """
        return self._adapt_uncertainty(credence, ci, user_type)

    def _adapt_uncertainty(self, credence: float, ci: Tuple[Optional[float], Optional[float]], user_type: UserType) -> str:
        """
        Internal uncertainty adaptation.

        SUCCESS CONDITIONS (SC-LA-UNCERTAINTY):
        - SC-LA-UNCERTAINTY-1: Returns string
        - SC-LA-UNCERTAINTY-2: Architect: returns '{label} confidence ({percentage}%)' format
        - SC-LA-UNCERTAINTY-3: Researcher: returns 'credence {:.2f}, 95% CI [lower, upper]' format when CI provided
        - SC-LA-UNCERTAINTY-4: Researcher: returns 'credence {:.2f}' when CI not provided
        - SC-LA-UNCERTAINTY-5: Student: returns '{label} — about N out of 10 studies agree' format
        - SC-LA-UNCERTAINTY-6: Reviewer: returns '{grade_level} certainty (GRADE)' format
        - SC-LA-UNCERTAINTY-7: Quick lookup: returns '{label} confidence' format
        - SC-LA-UNCERTAINTY-8: Default: returns 'Credence: {percentage}%' format
        - SC-LA-UNCERTAINTY-9: Handles credence values 0.0 to 1.0
        - SC-LA-UNCERTAINTY-10: Handles CI with None values gracefully
        """
        if user_type == UserType.ARCHITECT:
            # "moderate-high confidence (72%)"
            confidence_label = self._credence_to_label(credence)
            return f"{confidence_label} confidence ({credence*100:.0f}%)"

        elif user_type == UserType.RESEARCHER:
            # "credence 0.72, 95% CI [0.64, 0.80]"
            if ci[0] is not None and ci[1] is not None:
                return f"credence {credence:.2f}, 95% CI [{ci[0]:.2f}, {ci[1]:.2f}]"
            else:
                return f"credence {credence:.2f}"

        elif user_type == UserType.STUDENT:
            # "fairly well supported — about 7 out of 10 studies agree"
            confidence_label = self._credence_to_label(credence)
            out_of_10 = int(credence * 10)
            return f"{confidence_label} — about {out_of_10} out of 10 studies agree"

        elif user_type == UserType.REVIEWER:
            # "Moderate certainty (GRADE). I² = 62%"
            grade = self._credence_to_grade(credence)
            return f"{grade} certainty (GRADE)"

        elif user_type == UserType.QUICK_LOOKUP:
            # "Moderate confidence"
            return self._credence_to_label(credence) + " confidence"

        return f"Credence: {credence:.0%}"

    def adapt_citation(self, paper: Dict[str, Any], user_type: UserType) -> str:
        """
        Format citation for user type.

        Args:
            paper: Dictionary with 'authors', 'year', 'title', 'doi', etc.
            user_type: UserType enum

        Returns:
            Formatted citation
        """
        authors = paper.get('authors', 'Unknown')
        year = paper.get('year', 'n.d.')
        title = paper.get('title', 'Unknown Title')
        journal = paper.get('journal', 'Unknown Journal')
        doi = paper.get('doi', None)
        volume = paper.get('volume', '')
        pages = paper.get('pages', '')

        if user_type == UserType.ARCHITECT:
            # "Ulrich 1984 — hospital window views"
            first_author = authors.split(' and ')[0] if ' and ' in authors else authors
            short_title = paper.get('short_title', title[:40])
            return f"{first_author} {year} — {short_title}"

        elif user_type == UserType.RESEARCHER:
            # Full APA with DOI
            citation = f"{authors} ({year}). {title}. {journal}"
            if volume:
                citation += f", {volume}"
            if pages:
                citation += f", {pages}"
            if doi:
                citation += f". https://doi.org/{doi}"
            return citation

        elif user_type == UserType.STUDENT:
            # "A landmark 1984 study by Roger Ulrich showed that..."
            first_author = authors.split(' and ')[0] if ' and ' in authors else authors
            return f"A {year} study by {first_author} showed that {paper.get('key_finding', '')}."

        elif user_type == UserType.REVIEWER:
            # Complete bibliographic info
            citation = f"{authors} ({year}). {title}. {journal}"
            if volume:
                citation += f", {volume}"
            if pages:
                citation += f", pp. {pages}"
            if doi:
                citation += f". https://doi.org/{doi}"
            return citation

        elif user_type == UserType.QUICK_LOOKUP:
            # Minimal
            first_author = authors.split(' and ')[0] if ' and ' in authors else authors
            return f"{first_author} {year}"

        return f"{authors} ({year})"

    def get_answer_structure(self, user_type: UserType) -> List[str]:
        """
        Return the ordered sections for this user type's answer.

        Architect: [recommendation, evidence_summary, parameters, scope, contraindications]
        Researcher: [mechanism, evidence_with_effect_sizes, scope, gaps, competing_explanations]
        Student: [theory_context, key_finding, mechanism, key_papers, open_questions]
        """
        profile = self.USER_PROFILES.get(user_type, self.USER_PROFILES[UserType.RESEARCHER])
        return profile.answer_structure

    def get_completeness_criteria(self, user_type: UserType) -> List[str]:
        """Return what constitutes a 'complete' answer for this user type."""
        profile = self.USER_PROFILES.get(user_type, self.USER_PROFILES[UserType.RESEARCHER])
        return profile.completeness_criteria

    # =========================================================================
    # Private Helper Methods
    # =========================================================================

    def _adapt_headline(self, headline: str, user_type: UserType) -> str:
        """
        Adapt the headline for the user type.

        SUCCESS CONDITIONS (SC-LA-HEADLINE):
        - SC-LA-HEADLINE-1: Returns string
        - SC-LA-HEADLINE-2: Quick lookup: truncates to 80 chars with no ellipsis
        - SC-LA-HEADLINE-3: Architect: prepends 'Design Finding: ' if not already present
        - SC-LA-HEADLINE-4: Other types: returns headline unchanged
        - SC-LA-HEADLINE-5: Handles empty string input
        - SC-LA-HEADLINE-6: Does not modify input parameter
        """
        if user_type == UserType.QUICK_LOOKUP:
            # Make it even shorter
            return headline[:80] if len(headline) > 80 else headline
        elif user_type == UserType.ARCHITECT:
            # Make it prescriptive
            if not headline.startswith("Design"):
                return f"Design Finding: {headline}"
        return headline

    def _adapt_mechanism(self, mechanism: str, user_type: UserType) -> str:
        """
        Adapt mechanism explanation.

        SUCCESS CONDITIONS (SC-LA-MECHANISM):
        - SC-LA-MECHANISM-1: Returns string
        - SC-LA-MECHANISM-2: Quick lookup: truncates to first sentence only
        - SC-LA-MECHANISM-3: Architect: returns mechanism unchanged
        - SC-LA-MECHANISM-4: Researcher: returns mechanism unchanged
        - SC-LA-MECHANISM-5: Other types: returns mechanism unchanged
        - SC-LA-MECHANISM-6: Handles empty string input
        - SC-LA-MECHANISM-7: Adds period if first sentence doesn't end with period
        """
        if user_type == UserType.QUICK_LOOKUP:
            # One sentence
            sentences = mechanism.split('.')
            return sentences[0] + "." if sentences else mechanism
        elif user_type == UserType.ARCHITECT:
            # Focus on practical implications
            return mechanism
        elif user_type == UserType.RESEARCHER:
            # Technical detail
            return mechanism
        return mechanism

    def _adapt_evidence(self, evidence: Dict[str, Any], user_type: UserType) -> Dict[str, Any]:
        """
        Adapt evidence presentation.

        SUCCESS CONDITIONS (SC-LA-EVIDENCE):
        - SC-LA-EVIDENCE-1: Returns dict (shallow copy of input)
        - SC-LA-EVIDENCE-2: Architect: sets include_ebd_level=True, include_effect_size_range=True, include_sample_size=True
        - SC-LA-EVIDENCE-3: Researcher: sets include_cohens_d=True, include_ci=True, include_i_squared=True, include_publication_bias=True
        - SC-LA-EVIDENCE-4: Student: sets include_study_count=True, include_quality_assessment=True, include_contested=True
        - SC-LA-EVIDENCE-5: Reviewer: sets include_grade=True, include_raw_effect_sizes=True, export_format='structured'
        - SC-LA-EVIDENCE-6: Quick lookup: sets include_study_count=True only
        - SC-LA-EVIDENCE-7: Preserves all original keys from input dict
        - SC-LA-EVIDENCE-8: Does not modify input parameter
        - SC-LA-EVIDENCE-9: Handles empty dict input
        """
        adapted = evidence.copy()

        if user_type == UserType.ARCHITECT:
            # Include: EBD level, effect size range, sample size
            adapted['include_ebd_level'] = True
            adapted['include_effect_size_range'] = True
            adapted['include_sample_size'] = True

        elif user_type == UserType.RESEARCHER:
            # Include: effect size (Cohen's d), 95% CI, I², publication bias
            adapted['include_cohens_d'] = True
            adapted['include_ci'] = True
            adapted['include_i_squared'] = True
            adapted['include_publication_bias'] = True

        elif user_type == UserType.STUDENT:
            # Include: study count, quality, what's contested
            adapted['include_study_count'] = True
            adapted['include_quality_assessment'] = True
            adapted['include_contested'] = True

        elif user_type == UserType.REVIEWER:
            # Include: all GRADE elements, raw effect sizes
            adapted['include_grade'] = True
            adapted['include_raw_effect_sizes'] = True
            adapted['export_format'] = 'structured'

        elif user_type == UserType.QUICK_LOOKUP:
            # Include: study count only
            adapted['include_study_count'] = True

        return adapted

    def _adapt_scope(self, scope: str, user_type: UserType) -> str:
        """
        Adapt scope statement.

        SUCCESS CONDITIONS (SC-LA-SCOPE):
        - SC-LA-SCOPE-1: Returns string
        - SC-LA-SCOPE-2: Quick lookup: truncates to first sentence only
        - SC-LA-SCOPE-3: Other types: returns scope unchanged
        - SC-LA-SCOPE-4: Adds period if first sentence doesn't end with period
        - SC-LA-SCOPE-5: Handles empty string input
        """
        if user_type == UserType.QUICK_LOOKUP:
            # One sentence
            return scope.split('.')[0] + "." if scope else ""
        return scope

    def _adapt_caveats(self, caveats: List[str], user_type: UserType) -> List[str]:
        """
        Adapt caveats.

        SUCCESS CONDITIONS (SC-LA-CAVEATS):
        - SC-LA-CAVEATS-1: Returns list
        - SC-LA-CAVEATS-2: Quick lookup: returns at most 1 caveat
        - SC-LA-CAVEATS-3: Architect: filters to caveats containing 'apply', 'work', 'context', or 'population'
        - SC-LA-CAVEATS-4: Architect: returns at most 3 caveats after filtering
        - SC-LA-CAVEATS-5: Other types: returns at most 3 caveats
        - SC-LA-CAVEATS-6: Preserves caveat text without modification
        - SC-LA-CAVEATS-7: Handles empty list input
        - SC-LA-CAVEATS-8: Returns empty list if no caveats meet filter criteria
        """
        if user_type == UserType.QUICK_LOOKUP:
            # One caveat
            return caveats[:1] if caveats else []
        elif user_type == UserType.ARCHITECT:
            # Focus on practical limitations
            return [c for c in caveats if any(x in c.lower() for x in ['apply', 'work', 'context', 'population'])][:3]
        return caveats[:3]

    def _adapt_citations(self, citations: List[Dict[str, Any]], user_type: UserType) -> List[str]:
        """
        Adapt citations for the user type.

        SUCCESS CONDITIONS (SC-LA-CITATIONS):
        - SC-LA-CITATIONS-1: Returns list of strings
        - SC-LA-CITATIONS-2: Preserves number of citations (no filtering)
        - SC-LA-CITATIONS-3: Each citation is formatted via adapt_citation()
        - SC-LA-CITATIONS-4: Handles empty list input
        - SC-LA-CITATIONS-5: Handles citations with missing fields
        """
        formatted = []
        for paper in citations:
            formatted.append(self.adapt_citation(paper, user_type))
        return formatted

    def _translate_vocabulary(self, text: str, user_type: UserType) -> str:
        """
        Translate technical vocabulary for the user type.

        SUCCESS CONDITIONS (SC-LA-VOCAB):
        - SC-LA-VOCAB-1: Returns string
        - SC-LA-VOCAB-2: Architect: translates 'Attention Restoration Theory' to 'the design lets your directed attention system recover'
        - SC-LA-VOCAB-3: Architect: translates 'predictive error minimization' to 'prediction error processing'
        - SC-LA-VOCAB-4: Architect: translates 'interoceptive signals' to 'internal body signals'
        - SC-LA-VOCAB-5: Architect: translates 'parasympathetic activation' to 'relaxation response'
        - SC-LA-VOCAB-6: Student: translates 'ART' to 'Attention Restoration Theory'
        - SC-LA-VOCAB-7: Student: translates 'SRT' to 'Stress Recovery Theory'
        - SC-LA-VOCAB-8: Other types: returns text unchanged
        - SC-LA-VOCAB-9: Handles text with no translations present
        - SC-LA-VOCAB-10: Preserves case sensitivity
        """
        translations = {
            UserType.ARCHITECT: {
                'Attention Restoration Theory': 'the design lets your directed attention system recover',
                'predictive error minimization': 'prediction error processing',
                'interoceptive signals': 'internal body signals',
                'parasympathetic activation': 'relaxation response',
            },
            UserType.STUDENT: {
                'ART': 'Attention Restoration Theory',
                'SRT': 'Stress Recovery Theory',
            },
        }

        translation_map = translations.get(user_type, {})
        for technical, plain in translation_map.items():
            text = text.replace(technical, plain)

        return text

    def _credence_to_label(self, credence: float) -> str:
        """
        Convert credence to verbal label.

        SUCCESS CONDITIONS (SC-LA-LABEL):
        - SC-LA-LABEL-1: Returns string label
        - SC-LA-LABEL-2: >= 0.85 returns 'Very high'
        - SC-LA-LABEL-3: >= 0.70 returns 'High'
        - SC-LA-LABEL-4: >= 0.55 returns 'Moderate'
        - SC-LA-LABEL-5: >= 0.40 returns 'Low'
        - SC-LA-LABEL-6: < 0.40 returns 'Very low'
        - SC-LA-LABEL-7: Boundary values (0.85, 0.70, 0.55, 0.40) map to expected labels
        """
        if credence >= 0.85:
            return "Very high"
        elif credence >= 0.70:
            return "High"
        elif credence >= 0.55:
            return "Moderate"
        elif credence >= 0.40:
            return "Low"
        else:
            return "Very low"

    def _credence_to_grade(self, credence: float) -> str:
        """
        Convert credence to GRADE certainty level.

        SUCCESS CONDITIONS (SC-LA-GRADE):
        - SC-LA-GRADE-1: Returns string label
        - SC-LA-GRADE-2: >= 0.80 returns 'High'
        - SC-LA-GRADE-3: >= 0.60 returns 'Moderate'
        - SC-LA-GRADE-4: >= 0.40 returns 'Low'
        - SC-LA-GRADE-5: < 0.40 returns 'Very low'
        - SC-LA-GRADE-6: Boundary values (0.80, 0.60, 0.40) map to expected GRADE levels
        """
        if credence >= 0.80:
            return "High"
        elif credence >= 0.60:
            return "Moderate"
        elif credence >= 0.40:
            return "Low"
        else:
            return "Very low"


# =============================================================================
# MODULE-LEVEL CONVENIENCE FUNCTION
# Bridge for AnswerEnrichmentOrchestrator Step 7
# =============================================================================

# Map common string user types to our UserType enum
_USER_TYPE_MAP = {
    "researcher": UserType.RESEARCHER,
    "student": UserType.STUDENT,
    "architect": UserType.ARCHITECT,
    "clinician": UserType.RESEARCHER,      # Clinician → Researcher (closest match)
    "policy_maker": UserType.ARCHITECT,     # Policy maker → Architect (decision-oriented)
    "general_public": UserType.QUICK_LOOKUP,
    "reviewer": UserType.REVIEWER,
    "quick_lookup": UserType.QUICK_LOOKUP,
}

_service_instance = None


def adapt_content(content: str, user_type: str, topic: str = "") -> Dict[str, Any]:
    """
    Module-level convenience function for the AnswerEnrichmentOrchestrator.

    Adapts content for a given user type and returns a metadata dict
    with vocabulary level, detail density, and uncertainty framing.

    Args:
        content: The answer text to adapt
        user_type: String user type (e.g. 'researcher', 'student', 'clinician')
        topic: The topic context

    Returns:
        Dict with keys: vocabulary, detail_level, uncertainty_language,
                        answer_structure, completeness_criteria

    NOTE: P1 ISSUE — This function returns a metadata dict describing how content
    should be adapted, NOT the adapted text itself. The actual content transformation
    is deferred to the AnswerEnrichmentOrchestrator or other services. This is the
    current behavior and is documented here for testing purposes. The full text
    adaptation will be implemented in a separate P1 task.

    SUCCESS CONDITIONS (SC-LA-CONTENT):
    - SC-LA-CONTENT-1: Returns dict (not string)
    - SC-LA-CONTENT-2: Dict includes 'vocabulary' key with string value
    - SC-LA-CONTENT-3: Dict includes 'detail_level' key with 'high' or 'medium' value
    - SC-LA-CONTENT-4: Dict includes 'uncertainty_language' key with string value
    - SC-LA-CONTENT-5: Dict includes 'answer_structure' key with list value
    - SC-LA-CONTENT-6: Dict includes 'completeness_criteria' key with list value
    - SC-LA-CONTENT-7: Dict includes 'actionability' key with float value (0.0-1.0)
    - SC-LA-CONTENT-8: Dict includes 'user_type_resolved' key with string value
    - SC-LA-CONTENT-9: Resolves string user_type to valid UserType enum value
    - SC-LA-CONTENT-10: Unknown user_type defaults to 'researcher'
    - SC-LA-CONTENT-11: detail_level is 'high' for researcher and reviewer types
    - SC-LA-CONTENT-12: detail_level is 'medium' for other types
    - SC-LA-CONTENT-13: Initializes module singleton on first call
    - SC-LA-CONTENT-14: Returns consistent profile data for same user_type on repeated calls
    """
    global _service_instance
    if _service_instance is None:
        _service_instance = LanguageAdaptationService()

    # Resolve user type string to enum
    ut = _USER_TYPE_MAP.get(user_type.lower(), UserType.RESEARCHER)

    profile = _service_instance.get_profile(ut)

    return {
        "vocabulary": profile.get("vocabulary", "technical_precise"),
        "detail_level": "high" if ut in (UserType.RESEARCHER, UserType.REVIEWER) else "medium",
        "uncertainty_language": profile.get("uncertainty_style", "credence_interval_with_explanation"),
        "answer_structure": profile.get("answer_structure", []),
        "completeness_criteria": profile.get("completeness_criteria", []),
        "actionability": profile.get("actionability", 0.5),
        "user_type_resolved": ut.value,
    }

