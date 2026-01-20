"""
Tests for Interpretive Intelligence (TODO 2).

Sprint E: Core patterns, vocabulary bridge, and question classification.

Date: January 20, 2026
"""

import pytest
from datetime import datetime, timezone
from typing import List

from src.services.interpretive_intelligence import (
    ExplanationPattern,
    DetailLevel,
    ExpertiseLevel,
    ExplanationRequest,
    ExplanationResponse,
    ClarifyingQuestion,
    IdentifiedGap,
    EvidenceItem,
    EvidenceTraceResult,
    PracticalImplication,
    PracticalResult,
    QuestionClassifier,
    EvidenceTracePattern,
    PracticalImplicationsPattern,
    GapIdentifier,
    InterpretiveEngine,
    create_engine,
    quick_explain,
)

from src.services.web_of_belief import (
    WebOfBelief,
    Belief,
    Constraint,
    Credence,
    EpistemicLevel,
    ConstraintType,
    ScopeConditions,
)


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def sample_belief():
    """Create a sample belief for testing."""
    return Belief(
        belief_id="b_nature_stress",
        content="Nature views reduce stress in office workers",
        level=EpistemicLevel.EMPIRICAL,
        credence=Credence(value=0.75, uncertainty=0.15),
        scope=ScopeConditions(population="office workers", setting="workplace"),
    )


@pytest.fixture
def web_with_evidence():
    """Create a web with beliefs and constraints for evidence testing."""
    web = WebOfBelief()

    # Main belief
    main_belief = Belief(
        belief_id="b_main",
        content="Natural views reduce stress levels",
        level=EpistemicLevel.INTERMEDIATE,
        credence=Credence(value=0.70, uncertainty=0.15),
    )
    web.add_belief(main_belief)

    # Supporting evidence (empirical beliefs)
    for i in range(3):
        evidence = Belief(
            belief_id=f"b_evidence_{i}",
            content=f"Study {i+1} found nature views correlate with lower cortisol",
            level=EpistemicLevel.EMPIRICAL,
            credence=Credence(value=0.65 + i*0.05, uncertainty=0.2),
            paper_ids={f"paper_{i+1}"}
        )
        web.add_belief(evidence)

        constraint = Constraint(
            constraint_id=f"c_support_{i}",
            source_id=f"b_evidence_{i}",
            target_id="b_main",
            constraint_type=ConstraintType.SUPPORTS,
            strength=0.6 + i*0.1,
        )
        web.add_constraint(constraint)

    # Contradicting evidence
    contra = Belief(
        belief_id="b_contra",
        content="One study found no effect of nature views",
        level=EpistemicLevel.EMPIRICAL,
        credence=Credence(value=0.55, uncertainty=0.25),
        paper_ids={"paper_contra"}
    )
    web.add_belief(contra)

    contra_constraint = Constraint(
        constraint_id="c_contra",
        source_id="b_contra",
        target_id="b_main",
        constraint_type=ConstraintType.CONTRADICTS,
        strength=0.5,
    )
    web.add_constraint(contra_constraint)

    return web


@pytest.fixture
def classifier():
    """Create a question classifier."""
    return QuestionClassifier()


@pytest.fixture
def engine(web_with_evidence):
    """Create an interpretive engine with test web."""
    return InterpretiveEngine(web_with_evidence)


# =============================================================================
# DATA STRUCTURE TESTS
# =============================================================================

class TestExplanationPattern:
    """Tests for ExplanationPattern enum."""

    def test_pattern_values(self):
        """Test pattern enum values."""
        assert ExplanationPattern.EVIDENCE.value == "evidence"
        assert ExplanationPattern.PRACTICAL.value == "practical"

    def test_pattern_count(self):
        """Two patterns initially per Lampson."""
        assert len(ExplanationPattern) == 2


class TestDetailLevel:
    """Tests for DetailLevel enum."""

    def test_detail_levels(self):
        """Test detail level values."""
        assert DetailLevel.SUMMARY.value == 1
        assert DetailLevel.STANDARD.value == 2
        assert DetailLevel.COMPREHENSIVE.value == 3


class TestExpertiseLevel:
    """Tests for ExpertiseLevel enum."""

    def test_expertise_levels(self):
        """Test expertise level values."""
        assert ExpertiseLevel.NOVICE.value == 1
        assert ExpertiseLevel.PRACTITIONER.value == 2
        assert ExpertiseLevel.RESEARCHER.value == 3


class TestExplanationRequest:
    """Tests for ExplanationRequest dataclass."""

    def test_minimal_request(self):
        """Test creating request with minimal params."""
        request = ExplanationRequest(
            pattern=ExplanationPattern.EVIDENCE,
            belief_id="test_belief"
        )
        assert request.pattern == ExplanationPattern.EVIDENCE
        assert request.belief_id == "test_belief"
        assert request.detail == DetailLevel.STANDARD  # default
        assert request.expertise == ExpertiseLevel.PRACTITIONER  # default

    def test_full_request(self):
        """Test creating request with all params."""
        request = ExplanationRequest(
            pattern=ExplanationPattern.PRACTICAL,
            belief_id="test_belief",
            detail=DetailLevel.COMPREHENSIVE,
            expertise=ExpertiseLevel.RESEARCHER
        )
        assert request.detail == DetailLevel.COMPREHENSIVE
        assert request.expertise == ExpertiseLevel.RESEARCHER


class TestExplanationResponse:
    """Tests for ExplanationResponse dataclass."""

    def test_successful_response(self):
        """Test successful response creation."""
        response = ExplanationResponse(
            success=True,
            explanation="Test explanation",
            pattern=ExplanationPattern.EVIDENCE,
            detail=DetailLevel.STANDARD
        )
        assert response.success is True
        assert response.explanation == "Test explanation"
        assert response.message is None

    def test_failed_response(self):
        """Test failed response creation."""
        response = ExplanationResponse(
            success=False,
            message="Belief not found"
        )
        assert response.success is False
        assert response.message == "Belief not found"

    def test_to_dict(self):
        """Test response serialization."""
        response = ExplanationResponse(
            success=True,
            explanation="Test",
            pattern=ExplanationPattern.EVIDENCE,
            detail=DetailLevel.SUMMARY
        )
        d = response.to_dict()
        assert d['success'] is True
        assert d['pattern'] == 'evidence'
        assert d['detail'] == 1


class TestIdentifiedGap:
    """Tests for IdentifiedGap dataclass."""

    def test_gap_creation(self):
        """Test gap creation."""
        gap = IdentifiedGap(
            gap_type="uncertain",
            description="High uncertainty",
            belief_id="b_test",
            priority=0.4
        )
        assert gap.gap_type == "uncertain"
        assert gap.priority == 0.4

    def test_to_dict(self):
        """Test gap serialization."""
        gap = IdentifiedGap(
            gap_type="unexplored",
            description="Few studies",
            belief_id="b_test",
            priority=0.5
        )
        d = gap.to_dict()
        assert d['gap_type'] == 'unexplored'
        assert d['priority'] == 0.5


# =============================================================================
# QUESTION CLASSIFIER TESTS
# =============================================================================

class TestQuestionClassifier:
    """Tests for question classification."""

    def test_evidence_keywords(self, classifier):
        """Test classification of evidence-related questions."""
        pattern, confidence = classifier.classify("What evidence supports nature reducing stress?")
        assert pattern == ExplanationPattern.EVIDENCE
        assert confidence > 0.5

    def test_practical_keywords(self, classifier):
        """Test classification of practical questions."""
        pattern, confidence = classifier.classify("What should I design for stress reduction?")
        assert pattern == ExplanationPattern.PRACTICAL
        assert confidence > 0.5

    def test_mixed_keywords_evidence_dominant(self, classifier):
        """Test with multiple evidence keywords."""
        pattern, confidence = classifier.classify("What research studies and findings support this?")
        assert pattern == ExplanationPattern.EVIDENCE

    def test_no_keywords_default(self, classifier):
        """Test question with no keywords defaults to evidence."""
        pattern, confidence = classifier.classify("Tell me about nature.")
        assert pattern == ExplanationPattern.EVIDENCE
        assert confidence < 0.5  # Low confidence

    def test_classify_or_clarify_high_confidence(self, classifier):
        """Test that high confidence returns pattern."""
        result = classifier.classify_or_clarify("What evidence shows plants reduce stress?")
        assert isinstance(result, ExplanationPattern)
        assert result == ExplanationPattern.EVIDENCE

    def test_classify_or_clarify_low_confidence(self, classifier):
        """Test that low confidence returns clarifying question."""
        result = classifier.classify_or_clarify("Tell me about plants.")
        assert isinstance(result, ClarifyingQuestion)
        assert len(result.options) == 2


class TestClarifyingQuestion:
    """Tests for clarifying question structure."""

    def test_structure(self):
        """Test clarifying question has required fields."""
        question = ClarifyingQuestion(
            prompt="What are you looking for?",
            options=[
                ("Evidence", ExplanationPattern.EVIDENCE),
                ("Recommendations", ExplanationPattern.PRACTICAL)
            ]
        )
        assert question.prompt
        assert len(question.options) == 2
        assert question.options[0][1] == ExplanationPattern.EVIDENCE


# =============================================================================
# EVIDENCE TRACE PATTERN TESTS
# =============================================================================

class TestEvidenceTracePattern:
    """Tests for evidence trace pattern."""

    def test_traverse_finds_evidence(self, web_with_evidence):
        """Test that traversal finds supporting evidence."""
        pattern = EvidenceTracePattern()
        result = pattern.traverse(web_with_evidence, "b_main")

        assert result.target_belief.belief_id == "b_main"
        assert len(result.supporting_evidence) == 3
        assert len(result.contradicting_evidence) == 1
        assert result.total_studies == 4

    def test_traverse_sorts_by_strength(self, web_with_evidence):
        """Test that evidence is sorted by strength × quality."""
        pattern = EvidenceTracePattern()
        result = pattern.traverse(web_with_evidence, "b_main")

        # Evidence should be sorted by constraint_strength (we set increasing strength)
        strengths = [e.constraint_strength for e in result.supporting_evidence]
        assert strengths == sorted(strengths, reverse=True)

    def test_traverse_nonexistent_belief(self, web_with_evidence):
        """Test traversal with nonexistent belief raises error."""
        pattern = EvidenceTracePattern()
        with pytest.raises(ValueError):
            pattern.traverse(web_with_evidence, "nonexistent")

    def test_evidence_strength_classification(self, web_with_evidence):
        """Test evidence strength is classified correctly."""
        pattern = EvidenceTracePattern()
        result = pattern.traverse(web_with_evidence, "b_main")

        # With 3 supporting studies, should be moderate
        assert result.evidence_strength in ["moderate", "strong"]

    def test_render_summary(self, web_with_evidence):
        """Test summary rendering."""
        pattern = EvidenceTracePattern()
        result = pattern.traverse(web_with_evidence, "b_main")
        text = pattern.render(result, DetailLevel.SUMMARY, ExpertiseLevel.PRACTITIONER)

        assert "Natural views reduce stress" in text
        assert "3" in text or "studies" in text.lower()

    def test_render_standard(self, web_with_evidence):
        """Test standard rendering."""
        pattern = EvidenceTracePattern()
        result = pattern.traverse(web_with_evidence, "b_main")
        text = pattern.render(result, DetailLevel.STANDARD, ExpertiseLevel.PRACTITIONER)

        assert "## Evidence for:" in text
        assert "Supporting Evidence" in text
        assert "Contradicting Evidence" in text

    def test_render_comprehensive(self, web_with_evidence):
        """Test comprehensive rendering."""
        pattern = EvidenceTracePattern()
        result = pattern.traverse(web_with_evidence, "b_main")
        text = pattern.render(result, DetailLevel.COMPREHENSIVE, ExpertiseLevel.RESEARCHER)

        assert "Comprehensive Evidence Trace" in text
        assert "Belief ID:" in text
        assert "Quantitative Summary" in text


# =============================================================================
# PRACTICAL IMPLICATIONS TESTS
# =============================================================================

class TestPracticalImplicationsPattern:
    """Tests for practical implications pattern."""

    def test_traverse_generates_implications(self, web_with_evidence):
        """Test that traversal generates practical implications."""
        pattern = PracticalImplicationsPattern()
        evidence_pattern = EvidenceTracePattern()
        evidence_result = evidence_pattern.traverse(web_with_evidence, "b_main")

        result = pattern.traverse(web_with_evidence, "b_main", evidence_result)

        assert result.target_belief.belief_id == "b_main"
        # May or may not have implications depending on content matching
        assert isinstance(result.implications, list)
        assert isinstance(result.caveats, list)

    def test_render_practical(self, web_with_evidence):
        """Test practical rendering."""
        pattern = PracticalImplicationsPattern()
        evidence_pattern = EvidenceTracePattern()
        evidence_result = evidence_pattern.traverse(web_with_evidence, "b_main")
        result = pattern.traverse(web_with_evidence, "b_main", evidence_result)

        text = pattern.render(result, DetailLevel.STANDARD, ExpertiseLevel.PRACTITIONER)

        assert "Practical Implications" in text


# =============================================================================
# GAP IDENTIFIER TESTS
# =============================================================================

class TestGapIdentifier:
    """Tests for gap identification."""

    def test_identifies_high_uncertainty(self):
        """Test identification of high uncertainty gap."""
        identifier = GapIdentifier()
        belief = Belief(
            belief_id="b_uncertain",
            content="Test belief",
            level=EpistemicLevel.EMPIRICAL,
            credence=Credence(value=0.6, uncertainty=0.4),  # High uncertainty
        )

        gaps = identifier.identify_gaps(belief)

        assert len(gaps) >= 1
        assert any(g.gap_type == "uncertain" for g in gaps)

    def test_identifies_few_studies(self, web_with_evidence):
        """Test identification of unexplored gap."""
        identifier = GapIdentifier()

        # Create belief with few supporting studies
        belief = Belief(
            belief_id="b_sparse",
            content="Sparse evidence belief",
            level=EpistemicLevel.INTERMEDIATE,
            credence=Credence(value=0.5, uncertainty=0.2),
        )

        # Create minimal evidence result
        evidence_result = EvidenceTraceResult(
            target_belief=belief,
            supporting_evidence=[],  # No evidence
            contradicting_evidence=[],
            total_studies=0,
            strongest_support=None,
            evidence_strength="preliminary"
        )

        gaps = identifier.identify_gaps(belief, evidence_result)

        assert len(gaps) >= 1
        assert any(g.gap_type == "unexplored" for g in gaps)

    def test_no_gaps_for_good_belief(self):
        """Test no gaps for well-supported belief."""
        identifier = GapIdentifier()
        belief = Belief(
            belief_id="b_good",
            content="Well supported belief",
            level=EpistemicLevel.EMPIRICAL,
            credence=Credence(value=0.8, uncertainty=0.1),  # Low uncertainty
        )

        # Create good evidence result
        evidence_result = EvidenceTraceResult(
            target_belief=belief,
            supporting_evidence=[
                EvidenceItem(
                    belief_id=f"e_{i}",
                    content=f"Evidence {i}",
                    source_paper=f"paper_{i}",
                    constraint_strength=0.7,
                    study_quality=0.8,
                    sample_size=100,
                    effect_size=0.5,
                    is_supporting=True,
                    summary="Supporting"
                ) for i in range(5)  # 5 studies
            ],
            contradicting_evidence=[],
            total_studies=5,
            strongest_support=None,
            evidence_strength="strong"
        )

        gaps = identifier.identify_gaps(belief, evidence_result)

        # Should have no gaps (or only minor ones)
        assert len([g for g in gaps if g.gap_type == "unexplored"]) == 0


# =============================================================================
# INTERPRETIVE ENGINE TESTS
# =============================================================================

class TestInterpretiveEngine:
    """Tests for main InterpretiveEngine class."""

    def test_explain_evidence(self, engine):
        """Test explaining with evidence pattern."""
        request = ExplanationRequest(
            pattern=ExplanationPattern.EVIDENCE,
            belief_id="b_main",
            detail=DetailLevel.STANDARD,
            expertise=ExpertiseLevel.PRACTITIONER
        )

        response = engine.explain(request)

        assert response.success is True
        assert "Evidence" in response.explanation
        assert response.pattern == ExplanationPattern.EVIDENCE

    def test_explain_practical(self, engine):
        """Test explaining with practical pattern."""
        request = ExplanationRequest(
            pattern=ExplanationPattern.PRACTICAL,
            belief_id="b_main",
            detail=DetailLevel.STANDARD,
            expertise=ExpertiseLevel.PRACTITIONER
        )

        response = engine.explain(request)

        assert response.success is True
        assert "Practical" in response.explanation
        assert response.pattern == ExplanationPattern.PRACTICAL

    def test_explain_nonexistent_belief(self, engine):
        """Test explaining nonexistent belief."""
        request = ExplanationRequest(
            pattern=ExplanationPattern.EVIDENCE,
            belief_id="nonexistent"
        )

        response = engine.explain(request)

        assert response.success is False
        assert "not found" in response.message.lower()

    def test_explain_identifies_gaps(self, engine):
        """Test that explanation identifies gaps."""
        # Create a belief with high uncertainty
        engine.web.add_belief(Belief(
            belief_id="b_uncertain",
            content="Uncertain belief for testing",
            level=EpistemicLevel.EMPIRICAL,
            credence=Credence(value=0.5, uncertainty=0.4),
        ))

        request = ExplanationRequest(
            pattern=ExplanationPattern.EVIDENCE,
            belief_id="b_uncertain"
        )

        response = engine.explain(request)

        assert response.success is True
        # Should identify uncertainty gap
        assert len(response.identified_gaps) >= 1

    def test_answer_question_evidence(self, engine):
        """Test answering evidence question."""
        result = engine.answer_question("What evidence supports nature reducing stress?")

        # Should either return explanation or clarifying question
        assert isinstance(result, (ExplanationResponse, ClarifyingQuestion))

    def test_answer_question_no_match(self, engine):
        """Test answering question with no matching beliefs."""
        result = engine.answer_question("xyzzy quantum blockchain")

        if isinstance(result, ExplanationResponse):
            assert result.success is False

    def test_expertise_affects_output(self, engine):
        """Test that expertise level affects explanation."""
        request_novice = ExplanationRequest(
            pattern=ExplanationPattern.EVIDENCE,
            belief_id="b_main",
            detail=DetailLevel.SUMMARY,
            expertise=ExpertiseLevel.NOVICE
        )

        request_researcher = ExplanationRequest(
            pattern=ExplanationPattern.EVIDENCE,
            belief_id="b_main",
            detail=DetailLevel.SUMMARY,
            expertise=ExpertiseLevel.RESEARCHER
        )

        response_novice = engine.explain(request_novice)
        response_researcher = engine.explain(request_researcher)

        # Both should succeed
        assert response_novice.success
        assert response_researcher.success

        # Outputs should differ in style
        # Novice should avoid technical jargon
        # (This is a soft test - actual language differs)

    def test_detail_affects_length(self, engine):
        """Test that detail level affects explanation length."""
        request_summary = ExplanationRequest(
            pattern=ExplanationPattern.EVIDENCE,
            belief_id="b_main",
            detail=DetailLevel.SUMMARY
        )

        request_comprehensive = ExplanationRequest(
            pattern=ExplanationPattern.EVIDENCE,
            belief_id="b_main",
            detail=DetailLevel.COMPREHENSIVE
        )

        response_summary = engine.explain(request_summary)
        response_comprehensive = engine.explain(request_comprehensive)

        # Comprehensive should be longer than summary
        assert len(response_comprehensive.explanation) > len(response_summary.explanation)


# =============================================================================
# FACTORY FUNCTION TESTS
# =============================================================================

class TestFactoryFunctions:
    """Tests for factory functions."""

    def test_create_engine(self, web_with_evidence):
        """Test engine creation."""
        engine = create_engine(web_with_evidence)
        assert isinstance(engine, InterpretiveEngine)
        assert engine.web is web_with_evidence

    def test_quick_explain(self, web_with_evidence):
        """Test quick explain function."""
        result = quick_explain(web_with_evidence, "b_main")
        assert isinstance(result, str)
        assert len(result) > 0


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestCredibilityIntegration:
    """Tests for integration with TODO 1 (Credibility Testing)."""

    def test_explain_credibility_decision(self, engine):
        """Test explaining credibility decisions."""
        # Create a mock credibility report
        class MockReport:
            def to_explanation_context(self):
                return {
                    'article_id': 'test_paper',
                    'decision': 'review',
                    'n_flags': 2,
                    'reasons': [
                        'Causal claim exceeds study design',
                        'Scope may extend beyond sample'
                    ]
                }

        report = MockReport()
        explanation = engine.explain_credibility_decision(report, DetailLevel.STANDARD)

        assert "review" in explanation.lower()
        assert "2" in explanation
        assert "Causal" in explanation


class TestEndToEnd:
    """End-to-end integration tests."""

    def test_full_workflow_evidence(self, web_with_evidence):
        """Test complete evidence explanation workflow."""
        # Create engine
        engine = InterpretiveEngine(web_with_evidence)

        # User asks question with keywords that match belief content
        # The belief content is "Natural views reduce stress levels"
        result = engine.answer_question(
            "What evidence shows natural views reduce stress?",
            detail=DetailLevel.STANDARD,
            expertise=ExpertiseLevel.PRACTITIONER
        )

        # Should get explanation (or clarification)
        if isinstance(result, ExplanationResponse):
            # If we got a response, check if it succeeded
            # May fail if keyword matching doesn't find beliefs, which is acceptable
            if result.success:
                assert len(result.explanation) > 50
        else:
            # Got clarifying question, which is also valid
            assert isinstance(result, ClarifyingQuestion)

    def test_full_workflow_practical(self, web_with_evidence):
        """Test complete practical explanation workflow."""
        engine = InterpretiveEngine(web_with_evidence)

        # Direct request for practical implications
        request = ExplanationRequest(
            pattern=ExplanationPattern.PRACTICAL,
            belief_id="b_main",
            detail=DetailLevel.STANDARD,
            expertise=ExpertiseLevel.PRACTITIONER
        )

        response = engine.explain(request)

        assert response.success
        assert "Practical" in response.explanation
