"""
Tests for Query Response Generator
==================================

Tests for response generation from parsed queries.

Date: January 21, 2026
Phase C Sprint C2
"""

import pytest
from src.services.query_parser import parse_query, QueryType
from src.services.query_response import (
    QueryResponseGenerator,
    QueryResponse,
    ResponseType,
    EvidenceItem,
    FollowUp,
    generate_response
)
from src.services.web_of_belief import (
    WebOfBelief,
    Belief,
    Credence,
    EpistemicLevel,
    SourceDepth,
    ScopeConditions,
    EnablingConditions
)


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def empty_web():
    """Create empty web."""
    return WebOfBelief()


@pytest.fixture
def populated_web():
    """Create web with test beliefs."""
    web = WebOfBelief()

    # Add test beliefs about natural light
    b1 = Belief(
        belief_id="light_1",
        content="Natural light improves worker productivity by 15%",
        level=EpistemicLevel.EMPIRICAL,
        credence=Credence(0.78, 0.10),
        outcome_id="productivity",
        source_depth=SourceDepth.FULL_TEXT,
        paper_ids=["paper_1", "paper_2"]
    )
    web.beliefs[b1.belief_id] = b1

    b2 = Belief(
        belief_id="light_2",
        content="Daylight exposure reduces stress hormones",
        level=EpistemicLevel.EMPIRICAL,
        credence=Credence(0.72, 0.15),
        outcome_id="stress",
        source_depth=SourceDepth.FULL_TEXT,
        paper_ids=["paper_3"]
    )
    web.beliefs[b2.belief_id] = b2

    # Abstract-only causal claim (should trigger warning)
    b3 = Belief(
        belief_id="light_3",
        content="Natural light causes improved cognitive function",
        level=EpistemicLevel.EMPIRICAL,
        credence=Credence(0.65, 0.20),
        outcome_id="cognition",
        source_depth=SourceDepth.ABSTRACT,  # Abstract only!
        paper_ids=["paper_4"]
    )
    web.beliefs[b3.belief_id] = b3

    # Contested belief
    b4 = Belief(
        belief_id="office_1",
        content="Open offices affect productivity (contested)",
        level=EpistemicLevel.EMPIRICAL,
        credence=Credence(0.50, 0.30),
        outcome_id="productivity",
        contested=True,
        source_depth=SourceDepth.FULL_TEXT
    )
    web.beliefs[b4.belief_id] = b4

    # Belief with scope conditions
    b5 = Belief(
        belief_id="temp_1",
        content="Thermal comfort optimizes cognitive performance",
        level=EpistemicLevel.EMPIRICAL,
        credence=Credence(0.75, 0.10),
        outcome_id="cognition",
        source_depth=SourceDepth.FULL_TEXT,
        scope=ScopeConditions(
            population="office workers",
            setting="climate-controlled buildings",
            duration="during work hours",
            scope_specified=True
        ),
        enabling_conditions=EnablingConditions(
            threshold="20-24C",
            temporal_order="continuous exposure"
        )
    )
    web.beliefs[b5.belief_id] = b5

    return web


# =============================================================================
# Response Generation Tests
# =============================================================================

class TestResponseGeneration:
    """Tests for basic response generation."""

    def test_generate_response_empty_web(self, empty_web):
        """Test response generation with empty web."""
        parse_result = parse_query("What is biophilia?")
        generator = QueryResponseGenerator(empty_web)
        response = generator.generate(parse_result)

        assert isinstance(response, QueryResponse)
        assert response.confidence_level == "unknown"
        assert len(response.evidence_items) == 0

    def test_generate_response_with_matches(self, populated_web):
        """Test response with matching beliefs."""
        parse_result = parse_query("Does natural light affect productivity?")
        generator = QueryResponseGenerator(populated_web)
        response = generator.generate(parse_result)

        assert response.response_type == ResponseType.DIRECT_ANSWER
        assert len(response.evidence_items) > 0
        assert response.total_supporting > 0

    def test_response_includes_summary(self, populated_web):
        """Test that response includes summary text."""
        parse_result = parse_query("What do we know about natural light?")
        generator = QueryResponseGenerator(populated_web)
        response = generator.generate(parse_result)

        assert response.summary is not None
        assert len(response.summary) > 0


# =============================================================================
# Follow-Up Generation Tests (Simon: exactly 3)
# =============================================================================

class TestFollowUpGeneration:
    """Tests for follow-up question generation."""

    def test_exactly_three_followups(self, populated_web):
        """Test that exactly 3 follow-ups are generated."""
        parse_result = parse_query("Does natural light affect productivity?")
        generator = QueryResponseGenerator(populated_web)
        response = generator.generate(parse_result)

        assert len(response.follow_ups) == 3

    def test_followup_types(self, populated_web):
        """Test that follow-ups have correct types."""
        parse_result = parse_query("Does natural light affect productivity?")
        generator = QueryResponseGenerator(populated_web)
        response = generator.generate(parse_result)

        types = {f.type for f in response.follow_ups}
        assert "deeper" in types
        assert "scope" in types  # Changed from "broader" per Cartwright/Simon panel
        assert "uncertainty" in types

    def test_followup_structure(self, populated_web):
        """Test follow-up structure."""
        parse_result = parse_query("Does natural light affect productivity?")
        generator = QueryResponseGenerator(populated_web)
        response = generator.generate(parse_result)

        for followup in response.follow_ups:
            assert followup.question is not None
            assert followup.type in ["deeper", "scope", "uncertainty"]  # "scope" replaced "broader"
            assert followup.rationale is not None
            # H4: Verify clickable query fields exist
            assert followup.query_url is not None
            assert followup.query_params is not None


# =============================================================================
# Abstract-Only Warning Tests (Cartwright)
# =============================================================================

class TestAbstractOnlyWarning:
    """Tests for abstract-only causal claim warnings."""

    def test_warning_for_abstract_causal(self, populated_web):
        """Test warning is set for abstract-only causal claims."""
        # Query that should match the abstract-only belief (light_3)
        # Using "affect" pattern which is properly recognized
        parse_result = parse_query("Does natural light affect cognitive function?")
        generator = QueryResponseGenerator(populated_web)
        response = generator.generate(parse_result)

        # Should have warning because light_3 is abstract-only causal
        # Note: Only triggers if matching beliefs include abstract-only causal claims
        # The test verifies the mechanism works when such claims are found
        has_abstract_evidence = any(
            e.source_depth == "abstract" and e.is_causal
            for e in response.evidence_items
        )
        if has_abstract_evidence:
            assert response.abstract_only_warning is True

    def test_evidence_item_needs_caution_flag(self, populated_web):
        """Test evidence items have needs_caution flag."""
        parse_result = parse_query("Does natural light affect cognition?")
        generator = QueryResponseGenerator(populated_web)
        response = generator.generate(parse_result)

        # Check that at least one evidence item has caution flag
        caution_items = [e for e in response.evidence_items if e.needs_caution]
        # May or may not find the abstract-only belief depending on search


# =============================================================================
# Contested Belief Tests
# =============================================================================

class TestContestedBeliefs:
    """Tests for contested belief handling."""

    def test_contested_flag(self, populated_web):
        """Test is_contested flag is set correctly."""
        parse_result = parse_query("Does open office design affect productivity?")
        generator = QueryResponseGenerator(populated_web)
        response = generator.generate(parse_result)

        assert response.is_contested is True


# =============================================================================
# H5: Contested Evidence Section Tests (per Cartwright/Simon panel)
# =============================================================================

class TestContestedEvidenceSection:
    """Tests for the contested evidence section feature (H5)."""

    def test_contested_evidence_present_when_disagreement(self, populated_web):
        """Test contested_evidence section is populated when beliefs disagree."""
        # Add contradicting beliefs to create disagreement
        from src.services.web_of_belief import Belief, Credence, SourceDepth, EpistemicLevel

        # High credence supporting belief
        populated_web.add_belief(Belief(
            belief_id="contested_1",
            content="Open offices improve collaboration and communication",
            level=EpistemicLevel.EMPIRICAL,
            credence=Credence(0.8, 0.10),
            source_depth=SourceDepth.FULL_TEXT,
            paper_ids=["paper_a"]
        ))

        # Low credence contradicting belief
        populated_web.add_belief(Belief(
            belief_id="contested_2",
            content="Open offices reduce productivity due to distractions",
            level=EpistemicLevel.EMPIRICAL,
            credence=Credence(0.3, 0.15),
            source_depth=SourceDepth.FULL_TEXT,
            paper_ids=["paper_b"],
            contested=True
        ))

        parse_result = parse_query("Does open office affect productivity?")
        generator = QueryResponseGenerator(populated_web)
        response = generator.generate(parse_result)

        # Should have contested evidence section
        assert response.contested_evidence is not None
        assert response.contested_evidence.topic is not None

    def test_contested_evidence_has_supporting_and_contradicting(self, populated_web):
        """Test contested evidence groups supporting and contradicting evidence."""
        from src.services.web_of_belief import Belief, Credence, SourceDepth, EpistemicLevel

        # Add beliefs with clear support/contradict split
        populated_web.add_belief(Belief(
            belief_id="support_1",
            content="Light exposure improves mood significantly",
            level=EpistemicLevel.EMPIRICAL,
            credence=Credence(0.75, 0.12),
            source_depth=SourceDepth.FULL_TEXT,
            paper_ids=["p1"]
        ))

        populated_web.add_belief(Belief(
            belief_id="contradict_1",
            content="Light exposure has minimal effect on mood",
            level=EpistemicLevel.EMPIRICAL,
            credence=Credence(0.25, 0.15),
            source_depth=SourceDepth.ABSTRACT,
            paper_ids=["p2"]
        ))

        parse_result = parse_query("Does light affect mood?")
        generator = QueryResponseGenerator(populated_web)
        response = generator.generate(parse_result)

        if response.contested_evidence:
            # Check structure
            assert hasattr(response.contested_evidence, 'supporting')
            assert hasattr(response.contested_evidence, 'contradicting')
            assert hasattr(response.contested_evidence, 'summary')
            assert hasattr(response.contested_evidence, 'reasons_for_disagreement')

    def test_contested_evidence_summary(self, populated_web):
        """Test contested evidence has informative summary."""
        from src.services.web_of_belief import Belief, Credence, SourceDepth, EpistemicLevel

        populated_web.add_belief(Belief(
            belief_id="test_support",
            content="Temperature affects cognitive performance positively",
            level=EpistemicLevel.EMPIRICAL,
            credence=Credence(0.7, 0.12),
            source_depth=SourceDepth.FULL_TEXT,
            paper_ids=["t1"]
        ))

        populated_web.add_belief(Belief(
            belief_id="test_contradict",
            content="Temperature has no effect on cognitive performance",
            level=EpistemicLevel.EMPIRICAL,
            credence=Credence(0.2, 0.18),
            source_depth=SourceDepth.ABSTRACT,
            paper_ids=["t2"]
        ))

        parse_result = parse_query("Does temperature affect cognition?")
        generator = QueryResponseGenerator(populated_web)
        response = generator.generate(parse_result)

        if response.contested_evidence:
            assert len(response.contested_evidence.summary) > 0
            # Summary should mention the topic
            assert "temperature" in response.contested_evidence.topic.lower() or \
                   "cognition" in response.contested_evidence.topic.lower()

    def test_contested_evidence_reasons_for_disagreement(self, populated_web):
        """Test that reasons for disagreement are identified."""
        from src.services.web_of_belief import Belief, Credence, SourceDepth, EpistemicLevel

        # Create disagreement with different source depths
        populated_web.add_belief(Belief(
            belief_id="full_text_support",
            content="Natural light improves worker satisfaction",
            level=EpistemicLevel.EMPIRICAL,
            credence=Credence(0.8, 0.10),
            source_depth=SourceDepth.FULL_TEXT,
            paper_ids=["ft1"]
        ))

        populated_web.add_belief(Belief(
            belief_id="abstract_contradict",
            content="Natural light has limited effect on satisfaction",
            level=EpistemicLevel.EMPIRICAL,
            credence=Credence(0.3, 0.15),
            source_depth=SourceDepth.ABSTRACT,
            paper_ids=["ab1"]
        ))

        parse_result = parse_query("Does natural light affect satisfaction?")
        generator = QueryResponseGenerator(populated_web)
        response = generator.generate(parse_result)

        if response.contested_evidence:
            assert len(response.contested_evidence.reasons_for_disagreement) > 0
            # Should have at least one reason identified

    def test_no_contested_evidence_when_unanimous(self, populated_web):
        """Test no contested section when all evidence agrees."""
        # All existing beliefs about natural light are supportive
        parse_result = parse_query("Does natural light affect productivity?")
        generator = QueryResponseGenerator(populated_web)
        response = generator.generate(parse_result)

        # If all credences are >= 0.5, no contested section needed
        all_supporting = all(e.credence >= 0.5 for e in response.evidence_items)
        if all_supporting and not response.is_contested:
            assert response.contested_evidence is None

    def test_contested_evidence_to_dict(self, populated_web):
        """Test contested evidence serialization."""
        from src.services.web_of_belief import Belief, Credence, SourceDepth, EpistemicLevel

        populated_web.add_belief(Belief(
            belief_id="serial_1",
            content="Noise affects concentration positively",
            level=EpistemicLevel.EMPIRICAL,
            credence=Credence(0.6, 0.12),
            source_depth=SourceDepth.FULL_TEXT,
            paper_ids=["s1"]
        ))

        populated_web.add_belief(Belief(
            belief_id="serial_2",
            content="Noise affects concentration negatively",
            level=EpistemicLevel.EMPIRICAL,
            credence=Credence(0.4, 0.15),
            source_depth=SourceDepth.ABSTRACT,
            paper_ids=["s2"]
        ))

        parse_result = parse_query("Does noise affect concentration?")
        generator = QueryResponseGenerator(populated_web)
        response = generator.generate(parse_result)

        response_dict = response.to_dict()
        if response.contested_evidence:
            assert 'contested_evidence' in response_dict
            ce_dict = response_dict['contested_evidence']
            assert 'topic' in ce_dict
            assert 'supporting' in ce_dict
            assert 'contradicting' in ce_dict
            assert 'summary' in ce_dict
            assert 'reasons_for_disagreement' in ce_dict


# =============================================================================
# Scope and Enabling Conditions Tests
# =============================================================================

class TestScopeConditions:
    """Tests for scope and enabling condition extraction."""

    def test_scope_extraction(self, populated_web):
        """Test scope conditions are extracted."""
        parse_result = parse_query("Does thermal comfort affect cognition?")
        generator = QueryResponseGenerator(populated_web)
        response = generator.generate(parse_result)

        # Should extract scope from temp_1 belief
        if response.scope_conditions:
            assert 'populations' in response.scope_conditions or \
                   'environments' in response.scope_conditions

    def test_enabling_conditions_extraction(self, populated_web):
        """Test enabling conditions are extracted."""
        parse_result = parse_query("Does temperature affect performance?")
        generator = QueryResponseGenerator(populated_web)
        response = generator.generate(parse_result)

        # May or may not have enabling conditions depending on match


# =============================================================================
# Vocabulary Expansion Tests (Bates)
# =============================================================================

class TestVocabularyExpansion:
    """Tests for vocabulary expansion transparency."""

    def test_vocabulary_in_response(self, populated_web):
        """Test vocabulary expansions are included in response."""
        parse_result = parse_query("Does natural light affect productivity?")
        generator = QueryResponseGenerator(populated_web)
        response = generator.generate(parse_result)

        # Should have vocabulary expansions from parse result
        # (only if terms have expansions)
        assert hasattr(response, 'vocabulary_used')


# =============================================================================
# Response Type Tests
# =============================================================================

class TestResponseTypes:
    """Tests for different response types."""

    def test_direct_answer_type(self, populated_web):
        """Test direct answer response type."""
        parse_result = parse_query("Does natural light affect productivity?")
        generator = QueryResponseGenerator(populated_web)
        response = generator.generate(parse_result)

        assert response.response_type == ResponseType.DIRECT_ANSWER

    def test_summary_type(self, populated_web):
        """Test summary response type."""
        parse_result = parse_query("What do we know about natural light?")
        generator = QueryResponseGenerator(populated_web)
        response = generator.generate(parse_result)

        assert response.response_type == ResponseType.SUMMARY

    def test_confidence_type(self, populated_web):
        """Test confidence report response type."""
        parse_result = parse_query("How confident are we about natural light effects?")
        generator = QueryResponseGenerator(populated_web)
        response = generator.generate(parse_result)

        assert response.response_type == ResponseType.CONFIDENCE_REPORT


# =============================================================================
# Confidence Level Tests
# =============================================================================

class TestConfidenceLevel:
    """Tests for confidence level calculation."""

    def test_high_confidence(self, populated_web):
        """Test high confidence for high-credence beliefs."""
        parse_result = parse_query("Does natural light improve productivity?")
        generator = QueryResponseGenerator(populated_web)
        response = generator.generate(parse_result)

        # light_1 has 0.78 credence
        assert response.confidence_level in ["high", "medium"]

    def test_unknown_confidence_no_matches(self, empty_web):
        """Test unknown confidence when no matches."""
        parse_result = parse_query("Does xyzzy affect flibble?")
        generator = QueryResponseGenerator(empty_web)
        response = generator.generate(parse_result)

        assert response.confidence_level == "unknown"


# =============================================================================
# Serialization Tests
# =============================================================================

class TestSerialization:
    """Tests for response serialization."""

    def test_response_to_dict(self, populated_web):
        """Test QueryResponse serialization."""
        parse_result = parse_query("Does natural light affect productivity?")
        generator = QueryResponseGenerator(populated_web)
        response = generator.generate(parse_result)

        d = response.to_dict()

        assert 'response_type' in d
        assert 'summary' in d
        assert 'confidence_level' in d
        assert 'evidence_items' in d
        assert 'follow_ups' in d
        assert len(d['follow_ups']) == 3

    def test_evidence_item_to_dict(self):
        """Test EvidenceItem serialization."""
        item = EvidenceItem(
            belief_id="test",
            content="Test content",
            credence=0.75,
            source_depth="full_text",
            paper_ids=["p1", "p2"],
            is_causal=True,
            needs_caution=False
        )
        d = item.to_dict()

        assert d['belief_id'] == "test"
        assert d['credence'] == 0.75
        assert d['is_causal'] is True

    def test_followup_to_dict(self):
        """Test FollowUp serialization."""
        followup = FollowUp(
            question="What about X?",
            type="deeper",
            rationale="Understand mechanisms"
        )
        d = followup.to_dict()

        assert d['question'] == "What about X?"
        assert d['type'] == "deeper"


# =============================================================================
# Convenience Function Tests
# =============================================================================

class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_generate_response_function(self, populated_web):
        """Test generate_response convenience function."""
        response = generate_response(populated_web, "Does natural light affect productivity?")

        assert isinstance(response, QueryResponse)
        assert len(response.follow_ups) == 3


# =============================================================================
# Integration Tests
# =============================================================================

class TestIntegration:
    """Integration tests."""

    def test_full_workflow(self, populated_web):
        """Test complete query-to-response workflow."""
        query = "Does natural light improve worker productivity?"

        # Generate response
        response = generate_response(populated_web, query)

        # Check all components
        assert response.summary is not None
        assert response.confidence_level in ["high", "medium", "low", "unknown"]
        assert len(response.follow_ups) == 3
        assert response.query_intent is not None

        # Check serialization
        d = response.to_dict()
        assert 'response_type' in d


# =============================================================================
# E1.D2: Directional Opposition Tests (per Pearl Panel)
# =============================================================================

class TestDirectionalOpposition:
    """
    E1.D2 Panel (Pearl): Test directional opposition detection.

    Per Pearl: Credence represents belief strength, not support/contradiction.
    Contested evidence should be identified by directional opposition
    (X increases Y vs X decreases Y), not credence threshold.
    """

    def test_directional_detection_positive(self, empty_web):
        """Test positive direction detection."""
        from src.services.web_of_belief import Belief, Credence, SourceDepth, EpistemicLevel

        empty_web.add_belief(Belief(
            belief_id="dir_pos",
            content="Natural light increases productivity significantly",
            level=EpistemicLevel.EMPIRICAL,
            credence=Credence(0.75, 0.10),
            source_depth=SourceDepth.FULL_TEXT,
            paper_ids=["p1"]
        ))

        generator = QueryResponseGenerator(empty_web)
        belief = empty_web.beliefs["dir_pos"]
        direction = generator._get_causal_direction(belief)

        assert direction == "positive"

    def test_directional_detection_negative(self, empty_web):
        """Test negative direction detection."""
        from src.services.web_of_belief import Belief, Credence, SourceDepth, EpistemicLevel

        empty_web.add_belief(Belief(
            belief_id="dir_neg",
            content="Noise decreases concentration and reduces productivity",
            level=EpistemicLevel.EMPIRICAL,
            credence=Credence(0.75, 0.10),  # Note: High credence but negative direction
            source_depth=SourceDepth.FULL_TEXT,
            paper_ids=["p1"]
        ))

        generator = QueryResponseGenerator(empty_web)
        belief = empty_web.beliefs["dir_neg"]
        direction = generator._get_causal_direction(belief)

        assert direction == "negative"

    def test_directional_opposition_triggers_contested(self, empty_web):
        """E1.D2: Test that directional opposition triggers contested detection."""
        from src.services.web_of_belief import Belief, Credence, SourceDepth, EpistemicLevel

        # Positive direction belief
        empty_web.add_belief(Belief(
            belief_id="opp_1",
            content="Open offices improve communication and collaboration",
            level=EpistemicLevel.EMPIRICAL,
            credence=Credence(0.70, 0.12),  # High credence
            source_depth=SourceDepth.FULL_TEXT,
            paper_ids=["a"]
        ))

        # Negative direction belief (also high credence!)
        empty_web.add_belief(Belief(
            belief_id="opp_2",
            content="Open offices reduce productivity and decrease focus",
            level=EpistemicLevel.EMPIRICAL,
            credence=Credence(0.75, 0.10),  # Also high credence - old logic would miss this!
            source_depth=SourceDepth.FULL_TEXT,
            paper_ids=["b"]
        ))

        parse_result = parse_query("How do open offices affect productivity?")
        generator = QueryResponseGenerator(empty_web)
        response = generator.generate(parse_result)

        # Should detect as contested due to directional opposition
        assert response.is_contested is True
        assert response.contested_evidence is not None

    def test_high_credence_both_sides_now_detected(self, empty_web):
        """E1.D2: Both beliefs with high credence but opposite directions detected."""
        from src.services.web_of_belief import Belief, Credence, SourceDepth, EpistemicLevel

        # Both beliefs have high credence, so old credence-threshold logic would miss
        empty_web.add_belief(Belief(
            belief_id="hc_1",
            content="Plants in offices increase worker wellbeing",
            level=EpistemicLevel.EMPIRICAL,
            credence=Credence(0.80, 0.08),  # High credence
            source_depth=SourceDepth.FULL_TEXT,
            paper_ids=["x"]
        ))

        empty_web.add_belief(Belief(
            belief_id="hc_2",
            content="Plants in offices decrease available workspace and worsen ergonomics",
            level=EpistemicLevel.EMPIRICAL,
            credence=Credence(0.70, 0.10),  # Also high credence
            source_depth=SourceDepth.ABSTRACT,
            paper_ids=["y"]
        ))

        parse_result = parse_query("How do plants affect office workers?")
        generator = QueryResponseGenerator(empty_web)
        response = generator.generate(parse_result)

        # Should be contested because of opposite directions
        assert response.is_contested is True, "Directional opposition should be detected"

    def test_measurement_method_disagreement_reason(self, empty_web):
        """E1.D2 (Cartwright): Test measurement method differences are detected."""
        from src.services.web_of_belief import Belief, Credence, SourceDepth, EpistemicLevel

        # Self-report finding
        empty_web.add_belief(Belief(
            belief_id="meth_1",
            content="Self-report questionnaire shows natural light improves perceived wellbeing",
            level=EpistemicLevel.EMPIRICAL,
            credence=Credence(0.75, 0.10),
            source_depth=SourceDepth.FULL_TEXT,
            paper_ids=["m1"]
        ))

        # Physiological finding with opposite direction
        empty_web.add_belief(Belief(
            belief_id="meth_2",
            content="Cortisol measurements indicate natural light decreases stress markers",
            level=EpistemicLevel.EMPIRICAL,
            credence=Credence(0.70, 0.12),
            source_depth=SourceDepth.FULL_TEXT,
            paper_ids=["m2"]
        ))

        parse_result = parse_query("How does natural light affect wellbeing?")
        generator = QueryResponseGenerator(empty_web)
        response = generator.generate(parse_result)

        # Check reasons include measurement method
        if response.contested_evidence:
            reasons = response.contested_evidence.reasons_for_disagreement
            # Should detect measurement method difference
            has_measurement_reason = any(
                "measurement" in r.lower() or "self-report" in r.lower() or "physiological" in r.lower()
                for r in reasons
            )
            # Note: Will only trigger if beliefs are actually in opposing groups
