"""
Tests for Language Adaptation Service.

Created: 2026-03-02
Author: Claude Code
"""

import pytest
from src.services.language_adaptation_service import (
    LanguageAdaptationService,
    UserType,
    ArchitectProfile,
    ResearcherProfile,
    StudentProfile,
    ReviewerProfile,
    QuickLookupProfile,
)


class TestLanguageAdaptationServiceInitialization:
    """Test service initialization."""

    def test_service_initializes(self):
        """Service should initialize without error."""
        service = LanguageAdaptationService()
        assert service is not None

    def test_all_user_types_have_profiles(self):
        """All UserType enums should have corresponding profiles."""
        service = LanguageAdaptationService()
        for user_type in UserType:
            profile = service.USER_PROFILES.get(user_type)
            assert profile is not None, f"No profile for {user_type}"

    def test_architect_profile_exists(self):
        """Architect profile should be complete."""
        service = LanguageAdaptationService()
        profile = service.get_profile(UserType.ARCHITECT)
        assert profile['user_type'] == 'architect'
        assert 'presupposition' in profile
        assert 'answer_structure' in profile
        assert profile['actionability'] == 0.70


class TestGetProfile:
    """Test profile retrieval."""

    def test_get_architect_profile(self):
        """Should return architect profile."""
        service = LanguageAdaptationService()
        profile = service.get_profile(UserType.ARCHITECT)
        assert profile['user_type'] == 'architect'
        assert 'design_parameter' in profile['answer_structure']

    def test_get_researcher_profile(self):
        """Should return researcher profile."""
        service = LanguageAdaptationService()
        profile = service.get_profile(UserType.RESEARCHER)
        assert profile['user_type'] == 'researcher'
        assert 'mechanism' in profile['answer_structure']
        assert 'effect_sizes_with_ci' in profile['answer_structure']

    def test_get_student_profile(self):
        """Should return student profile."""
        service = LanguageAdaptationService()
        profile = service.get_profile(UserType.STUDENT)
        assert profile['user_type'] == 'student'
        assert 'theoretical_framework' in profile['answer_structure']

    def test_get_reviewer_profile(self):
        """Should return reviewer profile."""
        service = LanguageAdaptationService()
        profile = service.get_profile(UserType.REVIEWER)
        assert profile['user_type'] == 'reviewer'
        assert 'study_level_data' in profile['answer_structure']
        assert profile['actionability'] == 1.0

    def test_get_quick_lookup_profile(self):
        """Should return quick lookup profile."""
        service = LanguageAdaptationService()
        profile = service.get_profile(UserType.QUICK_LOOKUP)
        assert profile['user_type'] == 'quick_lookup'
        assert 'headline' in profile['answer_structure']
        assert profile['actionability'] == 0.90


class TestAdaptUncertainty:
    """Test uncertainty formatting for different user types."""

    def test_architect_uncertainty_format(self):
        """Architect should get percentage with qualifier."""
        service = LanguageAdaptationService()
        result = service.adapt_uncertainty(0.72, (None, None), UserType.ARCHITECT)
        assert '%' in result
        assert 'High' in result or 'high' in result
        assert '72' in result

    def test_researcher_uncertainty_format(self):
        """Researcher should get credence interval."""
        service = LanguageAdaptationService()
        result = service.adapt_uncertainty(0.72, (0.64, 0.80), UserType.RESEARCHER)
        assert 'credence' in result
        assert '0.64' in result
        assert '0.80' in result
        assert 'CI' in result or '95%' in result

    def test_student_uncertainty_format(self):
        """Student should get verbal qualitative format."""
        service = LanguageAdaptationService()
        result = service.adapt_uncertainty(0.70, (None, None), UserType.STUDENT)
        assert 'out of 10' in result or '7 out' in result
        assert 'agree' in result

    def test_reviewer_uncertainty_format(self):
        """Reviewer should get GRADE format."""
        service = LanguageAdaptationService()
        result = service.adapt_uncertainty(0.72, (None, None), UserType.REVIEWER)
        assert 'GRADE' in result or 'Moderate' in result

    def test_quick_lookup_uncertainty_format(self):
        """Quick lookup should get simple label."""
        service = LanguageAdaptationService()
        result = service.adapt_uncertainty(0.72, (None, None), UserType.QUICK_LOOKUP)
        assert 'confidence' in result
        assert len(result) < 50  # Very short


class TestAdaptCitation:
    """Test citation formatting for different user types."""

    def test_architect_citation_format(self):
        """Architect should get author-year with brief title."""
        service = LanguageAdaptationService()
        paper = {
            'authors': 'Ulrich, R.S.',
            'year': 1984,
            'title': 'View through a window may influence recovery',
            'short_title': 'window views in hospitals',
        }
        result = service.adapt_citation(paper, UserType.ARCHITECT)
        assert 'Ulrich' in result
        assert '1984' in result
        assert len(result) < 100  # Concise

    def test_researcher_citation_format(self):
        """Researcher should get full APA with DOI."""
        service = LanguageAdaptationService()
        paper = {
            'authors': 'Ulrich, R.S.',
            'year': 1984,
            'title': 'View through a window may influence recovery',
            'journal': 'Science',
            'volume': 224,
            'pages': '420-421',
            'doi': '10.1126/science.224.4647.420',
        }
        result = service.adapt_citation(paper, UserType.RESEARCHER)
        assert 'Ulrich' in result
        assert '1984' in result
        assert 'Science' in result
        assert 'doi.org' in result

    def test_student_citation_format(self):
        """Student should get narrative format."""
        service = LanguageAdaptationService()
        paper = {
            'authors': 'Ulrich, R.S.',
            'year': 1984,
            'title': 'View through a window may influence recovery',
            'key_finding': 'that hospital patients near windows recovered faster',
        }
        result = service.adapt_citation(paper, UserType.STUDENT)
        assert 'Ulrich' in result
        assert 'study' in result
        assert '1984' in result

    def test_reviewer_citation_format(self):
        """Reviewer should get complete bibliographic info."""
        service = LanguageAdaptationService()
        paper = {
            'authors': 'Ulrich, R.S.',
            'year': 1984,
            'title': 'View through a window may influence recovery',
            'journal': 'Science',
            'volume': 224,
            'pages': '420-421',
            'doi': '10.1126/science.224.4647.420',
        }
        result = service.adapt_citation(paper, UserType.REVIEWER)
        assert 'Ulrich' in result
        assert '1984' in result
        assert 'Science' in result
        assert 'pp.' in result or 'pages' in result

    def test_quick_lookup_citation_format(self):
        """Quick lookup should get minimal citation."""
        service = LanguageAdaptationService()
        paper = {
            'authors': 'Ulrich, R.S.',
            'year': 1984,
            'title': 'View through a window may influence recovery',
        }
        result = service.adapt_citation(paper, UserType.QUICK_LOOKUP)
        assert 'Ulrich' in result
        assert '1984' in result
        assert len(result) < 50  # Very brief


class TestGetAnswerStructure:
    """Test answer structure differences by user type."""

    def test_architect_structure(self):
        """Architect structure should be parameter-first."""
        service = LanguageAdaptationService()
        structure = service.get_answer_structure(UserType.ARCHITECT)
        assert 'design_parameter' in structure
        assert structure.index('design_parameter') < structure.index('evidence_summary')

    def test_researcher_structure(self):
        """Researcher structure should be mechanism-first."""
        service = LanguageAdaptationService()
        structure = service.get_answer_structure(UserType.RESEARCHER)
        assert 'mechanism' in structure
        assert 'effect_sizes_with_ci' in structure

    def test_student_structure(self):
        """Student structure should be theory-first."""
        service = LanguageAdaptationService()
        structure = service.get_answer_structure(UserType.STUDENT)
        assert 'theoretical_framework' in structure
        assert 'key_papers' in structure

    def test_reviewer_structure(self):
        """Reviewer structure should be study-level-data-first."""
        service = LanguageAdaptationService()
        structure = service.get_answer_structure(UserType.REVIEWER)
        assert 'study_level_data' in structure
        assert structure.index('study_level_data') < structure.index('heterogeneity_metrics')

    def test_quick_lookup_structure(self):
        """Quick lookup structure should be headline-first."""
        service = LanguageAdaptationService()
        structure = service.get_answer_structure(UserType.QUICK_LOOKUP)
        assert structure[0] == 'headline'
        assert len(structure) <= 5  # Very minimal


class TestGetCompletenessRequirements:
    """Test what makes a complete answer for each user type."""

    def test_architect_completeness(self):
        """Architect answer must include parameters and measurement."""
        service = LanguageAdaptationService()
        criteria = service.get_completeness_criteria(UserType.ARCHITECT)
        assert any('Design parameter' in c for c in criteria)
        assert any('Measurement' in c for c in criteria)
        assert len(criteria) >= 5

    def test_researcher_completeness(self):
        """Researcher answer must include effect sizes and heterogeneity."""
        service = LanguageAdaptationService()
        criteria = service.get_completeness_criteria(UserType.RESEARCHER)
        assert any('Effect size' in c for c in criteria)
        assert any('Heterogeneity' in c for c in criteria)
        assert len(criteria) >= 8

    def test_student_completeness(self):
        """Student answer must include theoretical framework and key papers."""
        service = LanguageAdaptationService()
        criteria = service.get_completeness_criteria(UserType.STUDENT)
        assert any('Theoretical' in c for c in criteria)
        assert any('Key papers' in c for c in criteria)
        assert len(criteria) >= 8

    def test_reviewer_completeness(self):
        """Reviewer answer must include study-level data and GRADE."""
        service = LanguageAdaptationService()
        criteria = service.get_completeness_criteria(UserType.REVIEWER)
        assert any('Study-level' in c for c in criteria)
        assert any('GRADE' in c for c in criteria)
        assert len(criteria) >= 8

    def test_quick_lookup_completeness(self):
        """Quick lookup answer is minimal."""
        service = LanguageAdaptationService()
        criteria = service.get_completeness_criteria(UserType.QUICK_LOOKUP)
        assert len(criteria) == 5  # Exactly 5 minimal criteria


class TestAdaptFullAnswer:
    """Test adapting a full answer for a user type."""

    def test_adapt_architect_answer(self):
        """Should adapt answer for architect context."""
        service = LanguageAdaptationService()
        answer = {
            'headline': 'Plants reduce stress in offices',
            'mechanism': 'Natural elements trigger restoration via ART mechanism',
            'evidence': {'study_count': 17, 'effect_size': 0.35},
            'scope': 'Office knowledge workers, living plants visible',
            'caveats': ['Requires maintenance', 'Weak in outdoor settings'],
            'credence': 0.65,
        }
        adapted = service.adapt(answer, UserType.ARCHITECT)
        assert adapted['user_type'] == 'architect'
        assert 'structure' in adapted
        assert 'Design' in adapted['headline']

    def test_adapt_researcher_answer(self):
        """Should adapt answer for researcher context."""
        service = LanguageAdaptationService()
        answer = {
            'headline': 'Plants reduce stress in offices',
            'mechanism': 'Natural elements trigger restoration via ART mechanism',
            'evidence': {'study_count': 17, 'effect_size': 0.35},
            'scope': 'Office knowledge workers, living plants visible',
            'credence': 0.65,
            'credence_range': (0.55, 0.75),
        }
        adapted = service.adapt(answer, UserType.RESEARCHER)
        assert adapted['user_type'] == 'researcher'
        assert 'mechanism' in adapted
        assert 'credence' in adapted

    def test_adapt_quick_lookup_answer(self):
        """Should adapt answer for quick lookup context."""
        service = LanguageAdaptationService()
        answer = {
            'headline': 'Plants reduce stress in offices because natural elements help you relax',
            'mechanism': 'Natural elements trigger restoration via ART mechanism',
            'evidence': {'study_count': 17},
            'scope': 'Office knowledge workers, living plants visible',
            'caveats': ['Requires maintenance', 'Weak in outdoor settings', 'Studies are small'],
            'credence': 0.65,
        }
        adapted = service.adapt(answer, UserType.QUICK_LOOKUP)
        assert adapted['user_type'] == 'quick_lookup'
        # Quick lookup version should be shorter
        assert len(adapted['headline']) <= 100


class TestCredenceToLabel:
    """Test credence-to-verbal-label conversion."""

    def test_very_high_credence(self):
        """0.90 should map to very high."""
        service = LanguageAdaptationService()
        label = service._credence_to_label(0.90)
        assert 'high' in label.lower()

    def test_high_credence(self):
        """0.75 should map to high."""
        service = LanguageAdaptationService()
        label = service._credence_to_label(0.75)
        assert 'high' in label.lower()

    def test_moderate_credence(self):
        """0.60 should map to moderate."""
        service = LanguageAdaptationService()
        label = service._credence_to_label(0.60)
        assert 'moderate' in label.lower()

    def test_low_credence(self):
        """0.45 should map to low."""
        service = LanguageAdaptationService()
        label = service._credence_to_label(0.45)
        assert 'low' in label.lower()

    def test_very_low_credence(self):
        """0.20 should map to very low."""
        service = LanguageAdaptationService()
        label = service._credence_to_label(0.20)
        assert 'very' in label.lower() and 'low' in label.lower()


class TestCredenceToGrade:
    """Test credence-to-GRADE conversion."""

    def test_high_grade(self):
        """0.85 should map to high GRADE."""
        service = LanguageAdaptationService()
        grade = service._credence_to_grade(0.85)
        assert 'High' in grade

    def test_moderate_grade(self):
        """0.65 should map to moderate GRADE."""
        service = LanguageAdaptationService()
        grade = service._credence_to_grade(0.65)
        assert 'Moderate' in grade

    def test_low_grade(self):
        """0.45 should map to low GRADE."""
        service = LanguageAdaptationService()
        grade = service._credence_to_grade(0.45)
        assert 'Low' in grade

    def test_very_low_grade(self):
        """0.30 should map to very low GRADE."""
        service = LanguageAdaptationService()
        grade = service._credence_to_grade(0.30)
        assert 'Very' in grade or 'very' in grade.lower()


class TestTranslateVocabulary:
    """Test vocabulary translation for different user types."""

    def test_architect_vocabulary_translation(self):
        """Should translate technical terms for architects."""
        service = LanguageAdaptationService()
        text = "Attention Restoration Theory suggests predictive error minimization"
        translated = service._translate_vocabulary(text, UserType.ARCHITECT)
        assert 'recovery' in translated or 'Attention' not in translated
        # At least one translation should happen

    def test_student_vocabulary_translation(self):
        """Should keep technical terms but define them."""
        service = LanguageAdaptationService()
        text = "ART and SRT are competing theories"
        translated = service._translate_vocabulary(text, UserType.STUDENT)
        # Student version should expand abbreviations
        assert 'Attention' in translated or 'Stress' in translated


class TestAdaptBeliefPresentation:
    """Test adapting individual belief presentation."""

    def test_adapt_belief_for_architect(self):
        """Should include design parameters for architects."""
        service = LanguageAdaptationService()
        belief = {
            'content': 'High ceilings increase creative thinking',
            'credence': 0.72,
            'design_parameter': 'Ceiling height ≥ 10 feet',
        }
        adapted = service.adapt_belief_presentation(belief, UserType.ARCHITECT)
        assert 'design_parameter' in adapted
        assert adapted['design_parameter'] == 'Ceiling height ≥ 10 feet'

    def test_adapt_belief_for_researcher(self):
        """Should include effect sizes for researchers."""
        service = LanguageAdaptationService()
        belief = {
            'content': 'High ceilings increase creative thinking',
            'credence': 0.72,
            'effect_size': 0.45,
            'confidence_interval': (0.32, 0.58),
        }
        adapted = service.adapt_belief_presentation(belief, UserType.RESEARCHER)
        assert 'effect_size' in adapted
        assert adapted['effect_size'] == 0.45

    def test_adapt_belief_for_student(self):
        """Should include learning resources for students."""
        service = LanguageAdaptationService()
        belief = {
            'content': 'High ceilings increase creative thinking',
            'key_papers': ['Kaplan 1989', 'Yuan et al. 2021'],
        }
        adapted = service.adapt_belief_presentation(belief, UserType.STUDENT)
        assert 'key_papers' in adapted


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
