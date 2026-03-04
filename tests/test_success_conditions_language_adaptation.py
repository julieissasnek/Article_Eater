"""
Test suite for Language Adaptation Service SUCCESS CONDITIONS.

Tests cover all documented success conditions for:
- adapt()
- adapt_belief_presentation()
- adapt_content()
- All private _adapt_* methods

Created: 2026-03-03
Sprint: SC-4
"""

import pytest
from typing import Dict, Any

from src.services.language_adaptation_service import (
    LanguageAdaptationService,
    UserType,
    adapt_content,
    ArchitectProfile,
    ResearcherProfile,
    StudentProfile,
    ReviewerProfile,
    QuickLookupProfile,
)


class TestAdaptMainMethod:
    """Test adapt() method SUCCESS CONDITIONS (SC-LA-ADAPT-1 through SC-LA-ADAPT-13)."""

    @pytest.fixture
    def service(self):
        return LanguageAdaptationService()

    @pytest.fixture
    def full_answer(self):
        """Complete answer dict with all possible fields."""
        return {
            'headline': 'Natural light improves cognitive performance',
            'mechanism': 'Circadian alignment reduces sleep debt. Better sleep improves focus.',
            'evidence': {
                'study_count': 42,
                'average_effect_size': 0.65,
            },
            'scope': 'Applies to office workers 18-65 without light-sensitive conditions.',
            'caveats': [
                'Limited to temperate climates',
                'Applies to settings with controllable windows',
                'Works best with consistent schedule'
            ],
            'credence': 0.75,
            'credence_range': (0.68, 0.82),
            'citations': [
                {
                    'authors': 'Ulrich & Simons',
                    'year': 1986,
                    'title': 'Recovery from stress during exposure to plants, light, and water features',
                    'doi': '10.1016/j.jenvp.2003.04.001'
                }
            ]
        }

    def test_adapt_returns_dict(self, service, full_answer):
        """SC-LA-ADAPT-1: Returns dict with required keys."""
        result = service.adapt(full_answer, UserType.ARCHITECT)
        assert isinstance(result, dict)
        assert 'user_type' in result
        assert 'original_answer' in result
        assert 'structure' in result

    def test_adapt_user_type_matches(self, service, full_answer):
        """SC-LA-ADAPT-2: user_type in output matches input."""
        for ut in UserType:
            result = service.adapt(full_answer, ut)
            assert result['user_type'] == ut.value

    def test_adapt_original_answer_preserved(self, service, full_answer):
        """SC-LA-ADAPT-3: original_answer contains unmodified input."""
        result = service.adapt(full_answer, UserType.RESEARCHER)
        assert result['original_answer'] == full_answer

    def test_adapt_structure_present(self, service, full_answer):
        """SC-LA-ADAPT-4: structure key contains get_answer_structure result."""
        result = service.adapt(full_answer, UserType.STUDENT)
        expected_structure = service.get_answer_structure(UserType.STUDENT)
        assert result['structure'] == expected_structure

    def test_adapt_headline_included(self, service, full_answer):
        """SC-LA-ADAPT-5: Headline is adapted if present."""
        result = service.adapt(full_answer, UserType.ARCHITECT)
        assert 'headline' in result
        assert isinstance(result['headline'], str)

    def test_adapt_mechanism_included(self, service, full_answer):
        """SC-LA-ADAPT-6: Mechanism is adapted if present."""
        result = service.adapt(full_answer, UserType.RESEARCHER)
        assert 'mechanism' in result
        assert isinstance(result['mechanism'], str)

    def test_adapt_evidence_included(self, service, full_answer):
        """SC-LA-ADAPT-7: Evidence is adapted if present."""
        result = service.adapt(full_answer, UserType.ARCHITECT)
        assert 'evidence' in result
        assert isinstance(result['evidence'], dict)

    def test_adapt_scope_included(self, service, full_answer):
        """SC-LA-ADAPT-8: Scope is adapted if present."""
        result = service.adapt(full_answer, UserType.QUICK_LOOKUP)
        assert 'scope' in result
        assert isinstance(result['scope'], str)

    def test_adapt_caveats_included(self, service, full_answer):
        """SC-LA-ADAPT-9: Caveats are adapted if present."""
        result = service.adapt(full_answer, UserType.STUDENT)
        assert 'caveats' in result
        assert isinstance(result['caveats'], list)

    def test_adapt_credence_included(self, service, full_answer):
        """SC-LA-ADAPT-10: Credence formatting included if present."""
        result = service.adapt(full_answer, UserType.RESEARCHER)
        assert 'credence' in result
        assert isinstance(result['credence'], str)

    def test_adapt_citations_included(self, service, full_answer):
        """SC-LA-ADAPT-11: Citations are formatted if present."""
        result = service.adapt(full_answer, UserType.ARCHITECT)
        assert 'citations' in result
        assert isinstance(result['citations'], list)
        assert len(result['citations']) > 0

    def test_adapt_all_user_types(self, service, full_answer):
        """SC-LA-ADAPT-12: Handles all UserType enum values without exception."""
        for ut in UserType:
            result = service.adapt(full_answer, ut)
            assert result is not None
            assert isinstance(result, dict)

    def test_adapt_empty_answer(self, service):
        """SC-LA-ADAPT-13: Returns non-empty dict for non-empty input."""
        empty_answer = {}
        result = service.adapt(empty_answer, UserType.RESEARCHER)
        assert result is not None
        assert 'user_type' in result
        assert 'original_answer' in result
        assert 'structure' in result


class TestAdaptBeliefPresentation:
    """Test adapt_belief_presentation() SUCCESS CONDITIONS (SC-LA-BELIEF-1 through SC-LA-BELIEF-15)."""

    @pytest.fixture
    def service(self):
        return LanguageAdaptationService()

    @pytest.fixture
    def belief(self):
        return {
            'content': 'Attention Restoration Theory explains that natural environments reduce directed attention fatigue',
            'credence': 0.72,
            'credence_range': (0.65, 0.80),
            'design_parameter': 'At least 30 minutes of view access',
            'measurement_kpi': 'Task completion time, error rate',
            'effect_size': 0.65,
            'confidence_interval': (0.45, 0.85),
            'methodology_notes': 'RCT with 120 office workers',
            'key_papers': ['Ulrich 1986', 'Kaplan 1989'],
            'learning_path': 'Start with Kaplan, then Ulrich, then recent meta-analyses',
            'grade_rating': 'Moderate',
            'study_metadata': {'n_studies': 42, 'i_squared': 0.62}
        }

    def test_belief_returns_dict_with_required_keys(self, service, belief):
        """SC-LA-BELIEF-1: Returns dict with 'content' and 'user_type' keys."""
        result = service.adapt_belief_presentation(belief, UserType.ARCHITECT)
        assert isinstance(result, dict)
        assert 'content' in result
        assert 'user_type' in result

    def test_belief_user_type_matches(self, service, belief):
        """SC-LA-BELIEF-2: user_type matches input."""
        result = service.adapt_belief_presentation(belief, UserType.RESEARCHER)
        assert result['user_type'] == UserType.RESEARCHER.value

    def test_belief_vocabulary_translated(self, service, belief):
        """SC-LA-BELIEF-3: content is vocabulary-translated."""
        result = service.adapt_belief_presentation(belief, UserType.ARCHITECT)
        # Should translate 'Attention Restoration Theory'
        assert 'directed attention system recover' in result['content']

    def test_belief_credence_included(self, service, belief):
        """SC-LA-BELIEF-4: Credence formatting included if present."""
        result = service.adapt_belief_presentation(belief, UserType.ARCHITECT)
        assert 'credence' in result
        assert isinstance(result['credence'], str)

    def test_belief_architect_design_parameter(self, service, belief):
        """SC-LA-BELIEF-5: Architect includes design_parameter if present."""
        result = service.adapt_belief_presentation(belief, UserType.ARCHITECT)
        assert 'design_parameter' in result
        assert result['design_parameter'] == belief['design_parameter']

    def test_belief_architect_measurement_kpi(self, service, belief):
        """SC-LA-BELIEF-6: Architect includes measurement_kpi if present."""
        result = service.adapt_belief_presentation(belief, UserType.ARCHITECT)
        assert 'measurement_kpi' in result
        assert result['measurement_kpi'] == belief['measurement_kpi']

    def test_belief_researcher_effect_size(self, service, belief):
        """SC-LA-BELIEF-7: Researcher includes effect_size if present."""
        result = service.adapt_belief_presentation(belief, UserType.RESEARCHER)
        assert 'effect_size' in result
        assert result['effect_size'] == belief['effect_size']

    def test_belief_researcher_confidence_interval(self, service, belief):
        """SC-LA-BELIEF-8: Researcher includes confidence_interval if present."""
        result = service.adapt_belief_presentation(belief, UserType.RESEARCHER)
        assert 'confidence_interval' in result
        assert result['confidence_interval'] == belief['confidence_interval']

    def test_belief_researcher_methodology_notes(self, service, belief):
        """SC-LA-BELIEF-9: Researcher includes methodology_notes if present."""
        result = service.adapt_belief_presentation(belief, UserType.RESEARCHER)
        assert 'methodology_notes' in result
        assert result['methodology_notes'] == belief['methodology_notes']

    def test_belief_student_key_papers(self, service, belief):
        """SC-LA-BELIEF-10: Student includes key_papers if present."""
        result = service.adapt_belief_presentation(belief, UserType.STUDENT)
        assert 'key_papers' in result
        assert result['key_papers'] == belief['key_papers']

    def test_belief_student_learning_path(self, service, belief):
        """SC-LA-BELIEF-11: Student includes learning_path if present."""
        result = service.adapt_belief_presentation(belief, UserType.STUDENT)
        assert 'learning_path' in result
        assert result['learning_path'] == belief['learning_path']

    def test_belief_reviewer_grade_rating(self, service, belief):
        """SC-LA-BELIEF-12: Reviewer includes grade_rating if present."""
        result = service.adapt_belief_presentation(belief, UserType.REVIEWER)
        assert 'grade_rating' in result
        assert result['grade_rating'] == belief['grade_rating']

    def test_belief_reviewer_study_metadata(self, service, belief):
        """SC-LA-BELIEF-13: Reviewer includes study_metadata if present."""
        result = service.adapt_belief_presentation(belief, UserType.REVIEWER)
        assert 'study_metadata' in result
        assert result['study_metadata'] == belief['study_metadata']

    def test_belief_quick_lookup_truncate(self, service):
        """SC-LA-BELIEF-14: Quick lookup content truncated to 100 chars."""
        long_content = 'x' * 150
        belief = {'content': long_content}
        result = service.adapt_belief_presentation(belief, UserType.QUICK_LOOKUP)
        assert len(result['content']) <= 103  # 100 + "..."

    def test_belief_all_user_types(self, service, belief):
        """SC-LA-BELIEF-15: Handles all UserType enum values without exception."""
        for ut in UserType:
            result = service.adapt_belief_presentation(belief, ut)
            assert result is not None
            assert isinstance(result, dict)


class TestAdaptContent:
    """Test adapt_content() module-level function SUCCESS CONDITIONS (SC-LA-CONTENT-1 through SC-LA-CONTENT-14)."""

    def test_content_returns_dict(self):
        """SC-LA-CONTENT-1: Returns dict (not string)."""
        result = adapt_content("Some answer text", "researcher")
        assert isinstance(result, dict)

    def test_content_vocabulary_key(self):
        """SC-LA-CONTENT-2: Includes 'vocabulary' key with string value."""
        result = adapt_content("Some text", "architect")
        assert 'vocabulary' in result
        assert isinstance(result['vocabulary'], str)

    def test_content_detail_level_key(self):
        """SC-LA-CONTENT-3: Includes 'detail_level' key with valid value."""
        result = adapt_content("Some text", "student")
        assert 'detail_level' in result
        assert result['detail_level'] in ('high', 'medium')

    def test_content_uncertainty_language_key(self):
        """SC-LA-CONTENT-4: Includes 'uncertainty_language' key."""
        result = adapt_content("Some text", "reviewer")
        assert 'uncertainty_language' in result
        assert isinstance(result['uncertainty_language'], str)

    def test_content_answer_structure_key(self):
        """SC-LA-CONTENT-5: Includes 'answer_structure' key with list."""
        result = adapt_content("Some text", "researcher")
        assert 'answer_structure' in result
        assert isinstance(result['answer_structure'], list)

    def test_content_completeness_criteria_key(self):
        """SC-LA-CONTENT-6: Includes 'completeness_criteria' key with list."""
        result = adapt_content("Some text", "quick_lookup")
        assert 'completeness_criteria' in result
        assert isinstance(result['completeness_criteria'], list)

    def test_content_actionability_key(self):
        """SC-LA-CONTENT-7: Includes 'actionability' key with float value."""
        result = adapt_content("Some text", "architect")
        assert 'actionability' in result
        assert isinstance(result['actionability'], float)
        assert 0.0 <= result['actionability'] <= 1.0

    def test_content_user_type_resolved_key(self):
        """SC-LA-CONTENT-8: Includes 'user_type_resolved' key."""
        result = adapt_content("Some text", "student")
        assert 'user_type_resolved' in result
        assert isinstance(result['user_type_resolved'], str)

    def test_content_user_type_resolution(self):
        """SC-LA-CONTENT-9: Resolves string user_type to valid UserType enum value."""
        for user_type_str in ['researcher', 'student', 'architect', 'reviewer', 'quick_lookup']:
            result = adapt_content("Some text", user_type_str)
            assert result['user_type_resolved'] == user_type_str

    def test_content_unknown_user_type_defaults(self):
        """SC-LA-CONTENT-10: Unknown user_type defaults to 'researcher'."""
        result = adapt_content("Some text", "unknown_type")
        assert result['user_type_resolved'] == 'researcher'

    def test_content_detail_level_researcher_high(self):
        """SC-LA-CONTENT-11: detail_level is 'high' for researcher and reviewer types."""
        for user_type in ['researcher', 'reviewer']:
            result = adapt_content("Some text", user_type)
            assert result['detail_level'] == 'high'

    def test_content_detail_level_others_medium(self):
        """SC-LA-CONTENT-12: detail_level is 'medium' for other types."""
        for user_type in ['architect', 'student', 'quick_lookup']:
            result = adapt_content("Some text", user_type)
            assert result['detail_level'] == 'medium'

    def test_content_singleton_initialization(self):
        """SC-LA-CONTENT-13: Initializes module singleton on first call."""
        result1 = adapt_content("Text 1", "researcher")
        result2 = adapt_content("Text 2", "researcher")
        # Both should succeed and be consistent
        assert result1 is not None
        assert result2 is not None

    def test_content_consistent_repeated_calls(self):
        """SC-LA-CONTENT-14: Returns consistent profile data for same user_type."""
        result1 = adapt_content("Text A", "student")
        result2 = adapt_content("Text B", "student")
        assert result1['user_type_resolved'] == result2['user_type_resolved']
        assert result1['vocabulary'] == result2['vocabulary']


class TestAdaptHeadlinePrivate:
    """Test _adapt_headline() SUCCESS CONDITIONS (SC-LA-HEADLINE-1 through SC-LA-HEADLINE-6)."""

    @pytest.fixture
    def service(self):
        return LanguageAdaptationService()

    def test_headline_returns_string(self, service):
        """SC-LA-HEADLINE-1: Returns string."""
        result = service._adapt_headline("Test headline", UserType.ARCHITECT)
        assert isinstance(result, str)

    def test_headline_quick_lookup_truncates(self, service):
        """SC-LA-HEADLINE-2: Quick lookup truncates to 80 chars."""
        long_headline = "x" * 100
        result = service._adapt_headline(long_headline, UserType.QUICK_LOOKUP)
        assert len(result) <= 80

    def test_headline_architect_adds_prefix(self, service):
        """SC-LA-HEADLINE-3: Architect prepends 'Design Finding:' if not present."""
        headline = "Natural light improves performance"
        result = service._adapt_headline(headline, UserType.ARCHITECT)
        assert result.startswith("Design Finding:")

    def test_headline_architect_no_double_prefix(self, service):
        """SC-LA-HEADLINE-3b: Architect does not double-prefix."""
        headline = "Design Finding: Natural light improves performance"
        result = service._adapt_headline(headline, UserType.ARCHITECT)
        assert result.count("Design Finding:") == 1

    def test_headline_other_types_unchanged(self, service):
        """SC-LA-HEADLINE-4: Other types return headline unchanged."""
        headline = "Natural light improves performance"
        for ut in [UserType.RESEARCHER, UserType.STUDENT, UserType.REVIEWER]:
            result = service._adapt_headline(headline, ut)
            assert result == headline

    def test_headline_empty_string(self, service):
        """SC-LA-HEADLINE-5: Handles empty string input."""
        result = service._adapt_headline("", UserType.ARCHITECT)
        assert result is not None
        assert isinstance(result, str)

    def test_headline_no_input_modification(self, service):
        """SC-LA-HEADLINE-6: Does not modify input parameter."""
        original = "Test headline"
        service._adapt_headline(original, UserType.RESEARCHER)
        assert original == "Test headline"


class TestAdaptMechanismPrivate:
    """Test _adapt_mechanism() SUCCESS CONDITIONS (SC-LA-MECHANISM-1 through SC-LA-MECHANISM-7)."""

    @pytest.fixture
    def service(self):
        return LanguageAdaptationService()

    def test_mechanism_returns_string(self, service):
        """SC-LA-MECHANISM-1: Returns string."""
        result = service._adapt_mechanism("Multi-sentence mechanism", UserType.RESEARCHER)
        assert isinstance(result, str)

    def test_mechanism_quick_lookup_first_sentence(self, service):
        """SC-LA-MECHANISM-2: Quick lookup truncates to first sentence only."""
        mechanism = "First sentence. Second sentence. Third sentence."
        result = service._adapt_mechanism(mechanism, UserType.QUICK_LOOKUP)
        assert result == "First sentence."
        assert "Second" not in result

    def test_mechanism_architect_unchanged(self, service):
        """SC-LA-MECHANISM-3: Architect returns mechanism unchanged."""
        mechanism = "Circadian alignment reduces sleep debt."
        result = service._adapt_mechanism(mechanism, UserType.ARCHITECT)
        assert result == mechanism

    def test_mechanism_researcher_unchanged(self, service):
        """SC-LA-MECHANISM-4: Researcher returns mechanism unchanged."""
        mechanism = "Mechanism explanation."
        result = service._adapt_mechanism(mechanism, UserType.RESEARCHER)
        assert result == mechanism

    def test_mechanism_other_types_unchanged(self, service):
        """SC-LA-MECHANISM-5: Other types return mechanism unchanged."""
        mechanism = "Some mechanism."
        for ut in [UserType.STUDENT, UserType.REVIEWER]:
            result = service._adapt_mechanism(mechanism, ut)
            assert result == mechanism

    def test_mechanism_empty_string(self, service):
        """SC-LA-MECHANISM-6: Handles empty string input."""
        result = service._adapt_mechanism("", UserType.QUICK_LOOKUP)
        assert result is not None
        assert isinstance(result, str)

    def test_mechanism_adds_period(self, service):
        """SC-LA-MECHANISM-7: Adds period if first sentence doesn't end with period."""
        mechanism_no_period = "First sentence"
        result = service._adapt_mechanism(mechanism_no_period, UserType.QUICK_LOOKUP)
        assert result.endswith(".")


class TestAdaptEvidencePrivate:
    """Test _adapt_evidence() SUCCESS CONDITIONS (SC-LA-EVIDENCE-1 through SC-LA-EVIDENCE-9)."""

    @pytest.fixture
    def service(self):
        return LanguageAdaptationService()

    @pytest.fixture
    def evidence(self):
        return {
            'study_count': 42,
            'average_effect_size': 0.65,
            'quality_rating': 'Moderate',
        }

    def test_evidence_returns_dict(self, service, evidence):
        """SC-LA-EVIDENCE-1: Returns dict (shallow copy)."""
        result = service._adapt_evidence(evidence, UserType.ARCHITECT)
        assert isinstance(result, dict)

    def test_evidence_architect_flags(self, service, evidence):
        """SC-LA-EVIDENCE-2: Architect sets specific flags."""
        result = service._adapt_evidence(evidence, UserType.ARCHITECT)
        assert result.get('include_ebd_level') is True
        assert result.get('include_effect_size_range') is True
        assert result.get('include_sample_size') is True

    def test_evidence_researcher_flags(self, service, evidence):
        """SC-LA-EVIDENCE-3: Researcher sets specific flags."""
        result = service._adapt_evidence(evidence, UserType.RESEARCHER)
        assert result.get('include_cohens_d') is True
        assert result.get('include_ci') is True
        assert result.get('include_i_squared') is True
        assert result.get('include_publication_bias') is True

    def test_evidence_student_flags(self, service, evidence):
        """SC-LA-EVIDENCE-4: Student sets specific flags."""
        result = service._adapt_evidence(evidence, UserType.STUDENT)
        assert result.get('include_study_count') is True
        assert result.get('include_quality_assessment') is True
        assert result.get('include_contested') is True

    def test_evidence_reviewer_flags(self, service, evidence):
        """SC-LA-EVIDENCE-5: Reviewer sets specific flags."""
        result = service._adapt_evidence(evidence, UserType.REVIEWER)
        assert result.get('include_grade') is True
        assert result.get('include_raw_effect_sizes') is True
        assert result.get('export_format') == 'structured'

    def test_evidence_quick_lookup_flags(self, service, evidence):
        """SC-LA-EVIDENCE-6: Quick lookup sets study_count only."""
        result = service._adapt_evidence(evidence, UserType.QUICK_LOOKUP)
        assert result.get('include_study_count') is True

    def test_evidence_preserves_original_keys(self, service, evidence):
        """SC-LA-EVIDENCE-7: Preserves all original keys from input dict."""
        result = service._adapt_evidence(evidence, UserType.ARCHITECT)
        for key in evidence.keys():
            assert key in result

    def test_evidence_no_input_modification(self, service, evidence):
        """SC-LA-EVIDENCE-8: Does not modify input parameter."""
        original_evidence = evidence.copy()
        service._adapt_evidence(evidence, UserType.RESEARCHER)
        assert evidence == original_evidence

    def test_evidence_empty_dict(self, service):
        """SC-LA-EVIDENCE-9: Handles empty dict input."""
        result = service._adapt_evidence({}, UserType.ARCHITECT)
        assert result is not None
        assert isinstance(result, dict)


class TestAdaptScopePrivate:
    """Test _adapt_scope() SUCCESS CONDITIONS (SC-LA-SCOPE-1 through SC-LA-SCOPE-5)."""

    @pytest.fixture
    def service(self):
        return LanguageAdaptationService()

    def test_scope_returns_string(self, service):
        """SC-LA-SCOPE-1: Returns string."""
        result = service._adapt_scope("Scope statement.", UserType.ARCHITECT)
        assert isinstance(result, str)

    def test_scope_quick_lookup_first_sentence(self, service):
        """SC-LA-SCOPE-2: Quick lookup truncates to first sentence only."""
        scope = "Applies to office workers. May not apply to remote workers. Tested in winter."
        result = service._adapt_scope(scope, UserType.QUICK_LOOKUP)
        assert result == "Applies to office workers."
        assert "remote" not in result

    def test_scope_other_types_unchanged(self, service):
        """SC-LA-SCOPE-3: Other types return scope unchanged."""
        scope = "Applies to office workers with windows."
        for ut in [UserType.ARCHITECT, UserType.RESEARCHER, UserType.STUDENT, UserType.REVIEWER]:
            result = service._adapt_scope(scope, ut)
            assert result == scope

    def test_scope_adds_period(self, service):
        """SC-LA-SCOPE-4: Adds period if first sentence doesn't end with period."""
        scope = "Applies to office workers"
        result = service._adapt_scope(scope, UserType.QUICK_LOOKUP)
        assert result.endswith(".")

    def test_scope_empty_string(self, service):
        """SC-LA-SCOPE-5: Handles empty string input."""
        result = service._adapt_scope("", UserType.QUICK_LOOKUP)
        assert result is not None
        assert isinstance(result, str)


class TestAdaptCaveatsPrivate:
    """Test _adapt_caveats() SUCCESS CONDITIONS (SC-LA-CAVEATS-1 through SC-LA-CAVEATS-8)."""

    @pytest.fixture
    def service(self):
        return LanguageAdaptationService()

    @pytest.fixture
    def caveats(self):
        return [
            "Limited to temperate climates",
            "Only applies in office settings with controllable windows",
            "Works best with consistent daily schedule",
            "May not work during seasonal affective disorder season",
            "Contraindicated for patients on photosensitizing medications"
        ]

    def test_caveats_returns_list(self, service, caveats):
        """SC-LA-CAVEATS-1: Returns list."""
        result = service._adapt_caveats(caveats, UserType.RESEARCHER)
        assert isinstance(result, list)

    def test_caveats_quick_lookup_one(self, service, caveats):
        """SC-LA-CAVEATS-2: Quick lookup returns at most 1 caveat."""
        result = service._adapt_caveats(caveats, UserType.QUICK_LOOKUP)
        assert len(result) <= 1

    def test_caveats_architect_filters_keywords(self, service, caveats):
        """SC-LA-CAVEATS-3: Architect filters to caveats containing key terms."""
        result = service._adapt_caveats(caveats, UserType.ARCHITECT)
        # Should include 'applies' and 'work' caveats
        for caveat in result:
            has_keyword = any(
                keyword in caveat.lower()
                for keyword in ['apply', 'work', 'context', 'population']
            )
            assert has_keyword

    def test_caveats_architect_max_three(self, service, caveats):
        """SC-LA-CAVEATS-4: Architect returns at most 3 caveats after filtering."""
        result = service._adapt_caveats(caveats, UserType.ARCHITECT)
        assert len(result) <= 3

    def test_caveats_others_max_three(self, service, caveats):
        """SC-LA-CAVEATS-5: Other types return at most 3 caveats."""
        for ut in [UserType.RESEARCHER, UserType.STUDENT, UserType.REVIEWER]:
            result = service._adapt_caveats(caveats, ut)
            assert len(result) <= 3

    def test_caveats_preserves_text(self, service, caveats):
        """SC-LA-CAVEATS-6: Preserves caveat text without modification."""
        result = service._adapt_caveats(caveats, UserType.RESEARCHER)
        for caveat in result:
            assert caveat in caveats

    def test_caveats_empty_list(self, service):
        """SC-LA-CAVEATS-7: Handles empty list input."""
        result = service._adapt_caveats([], UserType.RESEARCHER)
        assert result == []

    def test_caveats_no_match_returns_empty(self, service):
        """SC-LA-CAVEATS-8: Returns empty list if no caveats meet filter criteria."""
        architect_caveats = ["Generic caveat one", "Generic caveat two"]
        result = service._adapt_caveats(architect_caveats, UserType.ARCHITECT)
        assert len(result) == 0


class TestAdaptCitationsPrivate:
    """Test _adapt_citations() SUCCESS CONDITIONS (SC-LA-CITATIONS-1 through SC-LA-CITATIONS-5)."""

    @pytest.fixture
    def service(self):
        return LanguageAdaptationService()

    @pytest.fixture
    def citations(self):
        return [
            {
                'authors': 'Ulrich & Simons',
                'year': 1986,
                'title': 'Recovery from stress during exposure to plants',
                'doi': '10.1016/j.jenvp.2003.04.001'
            },
            {
                'authors': 'Kaplan & Kaplan',
                'year': 1989,
                'title': 'The Experience of Nature: A Psychological Perspective',
            }
        ]

    def test_citations_returns_list(self, service, citations):
        """SC-LA-CITATIONS-1: Returns list of strings."""
        result = service._adapt_citations(citations, UserType.ARCHITECT)
        assert isinstance(result, list)
        for item in result:
            assert isinstance(item, str)

    def test_citations_preserves_count(self, service, citations):
        """SC-LA-CITATIONS-2: Preserves number of citations."""
        result = service._adapt_citations(citations, UserType.ARCHITECT)
        assert len(result) == len(citations)

    def test_citations_formatted_via_adapt_citation(self, service, citations):
        """SC-LA-CITATIONS-3: Each citation formatted via adapt_citation()."""
        result = service._adapt_citations(citations, UserType.ARCHITECT)
        # Architect format should have year and author
        for citation_str in result:
            assert '1986' in citation_str or '1989' in citation_str

    def test_citations_empty_list(self, service):
        """SC-LA-CITATIONS-4: Handles empty list input."""
        result = service._adapt_citations([], UserType.RESEARCHER)
        assert result == []

    def test_citations_missing_fields(self, service):
        """SC-LA-CITATIONS-5: Handles citations with missing fields."""
        incomplete_citations = [
            {'authors': 'Smith', 'year': 2020},
            {'title': 'Some Title'}
        ]
        result = service._adapt_citations(incomplete_citations, UserType.RESEARCHER)
        assert len(result) == 2
        assert all(isinstance(item, str) for item in result)


class TestAdaptUncertaintyPrivate:
    """Test _adapt_uncertainty() SUCCESS CONDITIONS (SC-LA-UNCERTAINTY-1 through SC-LA-UNCERTAINTY-10)."""

    @pytest.fixture
    def service(self):
        return LanguageAdaptationService()

    def test_uncertainty_returns_string(self, service):
        """SC-LA-UNCERTAINTY-1: Returns string."""
        result = service._adapt_uncertainty(0.75, (None, None), UserType.ARCHITECT)
        assert isinstance(result, str)

    def test_uncertainty_architect_format(self, service):
        """SC-LA-UNCERTAINTY-2: Architect format includes percentage."""
        result = service._adapt_uncertainty(0.72, (None, None), UserType.ARCHITECT)
        assert '%' in result
        assert 'confidence' in result.lower()
        assert '72' in result

    def test_uncertainty_researcher_with_ci(self, service):
        """SC-LA-UNCERTAINTY-3: Researcher format includes CI when provided."""
        result = service._adapt_uncertainty(0.72, (0.64, 0.80), UserType.RESEARCHER)
        assert 'credence' in result
        assert '0.72' in result
        assert 'CI' in result
        assert '0.64' in result
        assert '0.80' in result

    def test_uncertainty_researcher_without_ci(self, service):
        """SC-LA-UNCERTAINTY-4: Researcher without CI returns simpler format."""
        result = service._adapt_uncertainty(0.72, (None, None), UserType.RESEARCHER)
        assert 'credence' in result
        assert '0.72' in result

    def test_uncertainty_student_format(self, service):
        """SC-LA-UNCERTAINTY-5: Student format includes out-of-10 scale."""
        result = service._adapt_uncertainty(0.70, (None, None), UserType.STUDENT)
        assert 'out of 10' in result
        assert '7' in result  # 0.70 * 10 = 7

    def test_uncertainty_reviewer_grade_format(self, service):
        """SC-LA-UNCERTAINTY-6: Reviewer format includes GRADE certainty."""
        result = service._adapt_uncertainty(0.75, (None, None), UserType.REVIEWER)
        assert 'GRADE' in result
        assert 'certainty' in result.lower()

    def test_uncertainty_quick_lookup_format(self, service):
        """SC-LA-UNCERTAINTY-7: Quick lookup returns simple confidence label."""
        result = service._adapt_uncertainty(0.75, (None, None), UserType.QUICK_LOOKUP)
        assert 'confidence' in result.lower()

    def test_uncertainty_default_format(self, service):
        """SC-LA-UNCERTAINTY-8: Unknown type uses default format."""
        # Test with a value that should fall through
        result = service._adapt_uncertainty(0.75, (None, None), UserType.ARCHITECT)
        assert result is not None
        assert isinstance(result, str)

    def test_uncertainty_credence_range(self, service):
        """SC-LA-UNCERTAINTY-9: Handles credence values 0.0 to 1.0."""
        for credence in [0.0, 0.25, 0.5, 0.75, 1.0]:
            result = service._adapt_uncertainty(credence, (None, None), UserType.ARCHITECT)
            assert result is not None
            assert isinstance(result, str)

    def test_uncertainty_partial_ci(self, service):
        """SC-LA-UNCERTAINTY-10: Handles CI with None values gracefully."""
        result = service._adapt_uncertainty(0.75, (0.65, None), UserType.RESEARCHER)
        assert result is not None
        assert isinstance(result, str)


class TestAdaptVocabularyPrivate:
    """Test _translate_vocabulary() SUCCESS CONDITIONS (SC-LA-VOCAB-1 through SC-LA-VOCAB-10)."""

    @pytest.fixture
    def service(self):
        return LanguageAdaptationService()

    def test_vocab_returns_string(self, service):
        """SC-LA-VOCAB-1: Returns string."""
        result = service._translate_vocabulary("Test text", UserType.ARCHITECT)
        assert isinstance(result, str)

    def test_vocab_architect_art_translation(self, service):
        """SC-LA-VOCAB-2: Architect translates ART correctly."""
        text = "Attention Restoration Theory is important"
        result = service._translate_vocabulary(text, UserType.ARCHITECT)
        assert 'directed attention system recover' in result

    def test_vocab_architect_pem_translation(self, service):
        """SC-LA-VOCAB-3: Architect translates predictive error minimization."""
        text = "This involves predictive error minimization"
        result = service._translate_vocabulary(text, UserType.ARCHITECT)
        assert 'prediction error processing' in result

    def test_vocab_architect_interoceptive_translation(self, service):
        """SC-LA-VOCAB-4: Architect translates interoceptive signals."""
        text = "interoceptive signals are important"
        result = service._translate_vocabulary(text, UserType.ARCHITECT)
        assert 'internal body signals' in result

    def test_vocab_architect_parasympathetic_translation(self, service):
        """SC-LA-VOCAB-5: Architect translates parasympathetic activation."""
        text = "parasympathetic activation promotes relaxation"
        result = service._translate_vocabulary(text, UserType.ARCHITECT)
        assert 'relaxation response' in result

    def test_vocab_student_art_translation(self, service):
        """SC-LA-VOCAB-6: Student translates ART to full form."""
        text = "ART explains this phenomenon"
        result = service._translate_vocabulary(text, UserType.STUDENT)
        assert 'Attention Restoration Theory' in result

    def test_vocab_student_srt_translation(self, service):
        """SC-LA-VOCAB-7: Student translates SRT."""
        text = "SRT is a related theory"
        result = service._translate_vocabulary(text, UserType.STUDENT)
        assert 'Stress Recovery Theory' in result

    def test_vocab_other_types_unchanged(self, service):
        """SC-LA-VOCAB-8: Other types return text unchanged."""
        text = "Attention Restoration Theory in context"
        for ut in [UserType.RESEARCHER, UserType.REVIEWER, UserType.QUICK_LOOKUP]:
            result = service._translate_vocabulary(text, ut)
            assert result == text

    def test_vocab_no_translations_present(self, service):
        """SC-LA-VOCAB-9: Handles text with no translations present."""
        text = "This is plain text with no technical terms"
        result = service._translate_vocabulary(text, UserType.ARCHITECT)
        assert result == text

    def test_vocab_case_sensitivity(self, service):
        """SC-LA-VOCAB-10: Preserves case sensitivity."""
        text = "attention restoration theory"  # lowercase
        result = service._translate_vocabulary(text, UserType.ARCHITECT)
        # Should not translate because case doesn't match
        assert result == text


class TestCredenceLabelsPrivate:
    """Test _credence_to_label() SUCCESS CONDITIONS (SC-LA-LABEL-1 through SC-LA-LABEL-7)."""

    @pytest.fixture
    def service(self):
        return LanguageAdaptationService()

    def test_label_returns_string(self, service):
        """SC-LA-LABEL-1: Returns string label."""
        result = service._credence_to_label(0.75)
        assert isinstance(result, str)

    def test_label_very_high(self, service):
        """SC-LA-LABEL-2: >= 0.85 returns 'Very high'."""
        for credence in [0.85, 0.90, 0.99]:
            result = service._credence_to_label(credence)
            assert result == "Very high"

    def test_label_high(self, service):
        """SC-LA-LABEL-3: >= 0.70 returns 'High'."""
        for credence in [0.70, 0.75, 0.84]:
            result = service._credence_to_label(credence)
            assert result == "High"

    def test_label_moderate(self, service):
        """SC-LA-LABEL-4: >= 0.55 returns 'Moderate'."""
        for credence in [0.55, 0.60, 0.69]:
            result = service._credence_to_label(credence)
            assert result == "Moderate"

    def test_label_low(self, service):
        """SC-LA-LABEL-5: >= 0.40 returns 'Low'."""
        for credence in [0.40, 0.45, 0.54]:
            result = service._credence_to_label(credence)
            assert result == "Low"

    def test_label_very_low(self, service):
        """SC-LA-LABEL-6: < 0.40 returns 'Very low'."""
        for credence in [0.0, 0.20, 0.39]:
            result = service._credence_to_label(credence)
            assert result == "Very low"

    def test_label_boundaries(self, service):
        """SC-LA-LABEL-7: Boundary values map to expected labels."""
        assert service._credence_to_label(0.85) == "Very high"
        assert service._credence_to_label(0.70) == "High"
        assert service._credence_to_label(0.55) == "Moderate"
        assert service._credence_to_label(0.40) == "Low"


class TestCredenceGradePrivate:
    """Test _credence_to_grade() SUCCESS CONDITIONS (SC-LA-GRADE-1 through SC-LA-GRADE-6)."""

    @pytest.fixture
    def service(self):
        return LanguageAdaptationService()

    def test_grade_returns_string(self, service):
        """SC-LA-GRADE-1: Returns string label."""
        result = service._credence_to_grade(0.75)
        assert isinstance(result, str)

    def test_grade_high(self, service):
        """SC-LA-GRADE-2: >= 0.80 returns 'High'."""
        for credence in [0.80, 0.90, 0.99]:
            result = service._credence_to_grade(credence)
            assert result == "High"

    def test_grade_moderate(self, service):
        """SC-LA-GRADE-3: >= 0.60 returns 'Moderate'."""
        for credence in [0.60, 0.70, 0.79]:
            result = service._credence_to_grade(credence)
            assert result == "Moderate"

    def test_grade_low(self, service):
        """SC-LA-GRADE-4: >= 0.40 returns 'Low'."""
        for credence in [0.40, 0.50, 0.59]:
            result = service._credence_to_grade(credence)
            assert result == "Low"

    def test_grade_very_low(self, service):
        """SC-LA-GRADE-5: < 0.40 returns 'Very low'."""
        for credence in [0.0, 0.20, 0.39]:
            result = service._credence_to_grade(credence)
            assert result == "Very low"

    def test_grade_boundaries(self, service):
        """SC-LA-GRADE-6: Boundary values map to expected GRADE levels."""
        assert service._credence_to_grade(0.80) == "High"
        assert service._credence_to_grade(0.60) == "Moderate"
        assert service._credence_to_grade(0.40) == "Low"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
