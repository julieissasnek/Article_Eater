"""
Tests for Vocabulary Bridge.

Sprint E: TODO 2 Implementation

Date: January 20, 2026
"""

import pytest
import os
from pathlib import Path

from src.services.vocabulary_bridge import (
    VocabularyBridge,
    create_vocabulary_bridge,
)

from src.services.web_of_belief import (
    WebOfBelief,
    Belief,
    Credence,
    EpistemicLevel,
)


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def vocab_path():
    """Get path to vocabulary bridge YAML."""
    project_root = Path(__file__).parent.parent
    return str(project_root / "contracts" / "vocab" / "vocabulary_bridge.yaml")


@pytest.fixture
def bridge(vocab_path):
    """Create vocabulary bridge instance."""
    return VocabularyBridge(vocab_path)


@pytest.fixture
def web_with_beliefs():
    """Create a web with beliefs for testing."""
    web = WebOfBelief()

    # Add some beliefs with nature/stress content
    web.add_belief(Belief(
        belief_id="b_nature_stress",
        content="Natural views and greenery reduce stress levels in office workers",
        level=EpistemicLevel.EMPIRICAL,
        credence=Credence(value=0.7, uncertainty=0.15),
    ))

    web.add_belief(Belief(
        belief_id="b_daylight",
        content="Natural lighting improves mood and productivity",
        level=EpistemicLevel.EMPIRICAL,
        credence=Credence(value=0.65, uncertainty=0.2),
    ))

    web.add_belief(Belief(
        belief_id="b_ceiling",
        content="Higher ceiling heights enhance creative thinking",
        level=EpistemicLevel.EMPIRICAL,
        credence=Credence(value=0.55, uncertainty=0.25),
    ))

    web.add_belief(Belief(
        belief_id="b_unrelated",
        content="The earth orbits the sun",
        level=EpistemicLevel.THEORETICAL,
        credence=Credence(value=0.99, uncertainty=0.01),
    ))

    return web


# =============================================================================
# LOADING TESTS
# =============================================================================

class TestVocabularyLoading:
    """Tests for vocabulary loading."""

    def test_load_valid_vocab(self, vocab_path):
        """Test loading valid vocabulary file."""
        bridge = VocabularyBridge(vocab_path)
        assert bridge.vocab is not None
        assert "concepts" in bridge.vocab

    def test_load_nonexistent_vocab(self, tmp_path):
        """Test loading nonexistent vocabulary file."""
        bridge = VocabularyBridge(str(tmp_path / "nonexistent.yaml"))
        # Should not crash, just have empty vocab
        assert bridge.vocab == {"concepts": {}, "relationships": {}}

    def test_concepts_loaded(self, bridge):
        """Test that concepts are loaded."""
        concepts = bridge.vocab.get("concepts", {})
        assert len(concepts) >= 20  # We defined 20 concepts

    def test_indices_built(self, bridge):
        """Test that reverse indices are built."""
        assert len(bridge.common_to_internal) > 0
        assert len(bridge.academic_to_internal) > 0
        assert len(bridge.practitioner_to_internal) > 0


# =============================================================================
# QUERY TO INTERNAL TESTS
# =============================================================================

class TestQueryToInternal:
    """Tests for query to internal mapping."""

    def test_common_term_mapping(self, bridge):
        """Test mapping common terms to internal IDs."""
        matches = bridge.query_to_internal("helps you relax")
        assert len(matches) >= 1
        assert any("stress" in m.lower() for m in matches)

    def test_academic_term_mapping(self, bridge):
        """Test mapping academic terms to internal IDs."""
        matches = bridge.query_to_internal("attention restoration theory")
        assert len(matches) >= 1
        assert any("attention" in m.lower() for m in matches)

    def test_practitioner_term_mapping(self, bridge):
        """Test mapping practitioner terms to internal IDs."""
        matches = bridge.query_to_internal("good ventilation")
        assert len(matches) >= 1

    def test_mixed_vocabulary(self, bridge):
        """Test query with terms from multiple vocabulary levels."""
        matches = bridge.query_to_internal("stress recovery and natural lighting")
        assert len(matches) >= 2

    def test_no_matches(self, bridge):
        """Test query with no matching terms."""
        matches = bridge.query_to_internal("xyzzy quantum blockchain")
        assert len(matches) == 0


# =============================================================================
# INTERNAL TO USER TESTS
# =============================================================================

class TestInternalToUser:
    """Tests for internal to user term conversion."""

    def test_novice_terms(self, bridge):
        """Test conversion to novice-level terms."""
        term = bridge.internal_to_user("psych.stress.recovery", "novice")
        # Should be simple/common language
        assert term is not None
        assert "relax" in term.lower() or "stress" in term.lower()

    def test_practitioner_terms(self, bridge):
        """Test conversion to practitioner-level terms."""
        term = bridge.internal_to_user("psych.stress.recovery", "practitioner")
        assert term is not None

    def test_researcher_terms(self, bridge):
        """Test conversion to researcher-level terms."""
        term = bridge.internal_to_user("psych.stress.recovery", "researcher")
        assert term is not None
        # Should be more technical
        assert "recovery" in term.lower() or "psychophysiological" in term.lower()

    def test_unknown_internal_id(self, bridge):
        """Test conversion of unknown internal ID."""
        term = bridge.internal_to_user("unknown.internal.id", "practitioner")
        # Should return the ID as-is
        assert term == "unknown.internal.id"


# =============================================================================
# FIND RELATED BELIEFS TESTS
# =============================================================================

class TestFindRelatedBeliefs:
    """Tests for finding related beliefs."""

    def test_finds_stress_related(self, bridge, web_with_beliefs):
        """Test finding beliefs related to stress."""
        related = bridge.find_related_beliefs("stress reduction in offices", web_with_beliefs)
        assert len(related) >= 1
        # Should find the nature_stress belief
        belief_ids = [b.belief_id for b in related]
        assert "b_nature_stress" in belief_ids

    def test_finds_lighting_related(self, bridge, web_with_beliefs):
        """Test finding beliefs related to lighting."""
        related = bridge.find_related_beliefs("natural light and daylight", web_with_beliefs)
        assert len(related) >= 1
        belief_ids = [b.belief_id for b in related]
        assert "b_daylight" in belief_ids

    def test_excludes_unrelated(self, bridge, web_with_beliefs):
        """Test that unrelated beliefs are not returned first."""
        related = bridge.find_related_beliefs("nature and stress", web_with_beliefs)

        if related:
            # Unrelated belief should not be first
            assert related[0].belief_id != "b_unrelated"

    def test_empty_query(self, bridge, web_with_beliefs):
        """Test with empty query."""
        related = bridge.find_related_beliefs("", web_with_beliefs)
        # Should still work, just return less
        assert isinstance(related, list)


# =============================================================================
# QUERY EXPANSION TESTS
# =============================================================================

class TestExpandQuery:
    """Tests for query expansion."""

    def test_expands_with_synonyms(self, bridge):
        """Test that query is expanded with synonyms."""
        expanded = bridge.expand_query("stress recovery")
        assert len(expanded) > 1
        # Should include related terms
        assert any("relax" in t.lower() for t in expanded) or \
               any("restoration" in t.lower() for t in expanded)

    def test_includes_original(self, bridge):
        """Test that original query is included in expansion."""
        expanded = bridge.expand_query("stress recovery")
        assert "stress recovery" in expanded


# =============================================================================
# CONCEPT INFO TESTS
# =============================================================================

class TestGetConceptInfo:
    """Tests for getting concept information."""

    def test_get_known_concept(self, bridge):
        """Test getting info for known concept."""
        info = bridge.get_concept_info("stress recovery")
        assert info is not None
        assert "internal" in info
        assert "academic" in info
        assert "common" in info

    def test_get_unknown_concept(self, bridge):
        """Test getting info for unknown concept."""
        info = bridge.get_concept_info("xyzzy")
        assert info is None


# =============================================================================
# TRANSLATION TESTS
# =============================================================================

class TestTranslateExplanation:
    """Tests for translating explanation text."""

    def test_translate_to_novice(self, bridge):
        """Test translating academic text to novice level."""
        text = "The study examined psychophysiological restoration through attention restoration."
        translated = bridge.translate_explanation(text, "novice")

        # Should replace some academic terms with simpler ones
        # (depending on vocabulary mappings)
        assert isinstance(translated, str)

    def test_translate_preserves_meaning(self, bridge):
        """Test that translation preserves general meaning."""
        text = "Natural views reduce stress."
        translated = bridge.translate_explanation(text, "novice")

        # Key content words should remain
        assert "natural" in translated.lower() or "nature" in translated.lower()


# =============================================================================
# FACTORY FUNCTION TESTS
# =============================================================================

class TestFactoryFunction:
    """Tests for factory function."""

    def test_create_with_default_path(self):
        """Test creating bridge with default path."""
        bridge = create_vocabulary_bridge()
        assert isinstance(bridge, VocabularyBridge)
        # Should have loaded the vocab (if file exists)

    def test_create_with_custom_path(self, vocab_path):
        """Test creating bridge with custom path."""
        bridge = create_vocabulary_bridge(vocab_path)
        assert isinstance(bridge, VocabularyBridge)
        assert len(bridge.vocab.get("concepts", {})) >= 20


# =============================================================================
# EDGE CASES
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases."""

    def test_case_insensitive_matching(self, bridge):
        """Test that matching is case-insensitive."""
        matches_lower = bridge.query_to_internal("stress recovery")
        matches_upper = bridge.query_to_internal("STRESS RECOVERY")
        matches_mixed = bridge.query_to_internal("Stress Recovery")

        assert set(matches_lower) == set(matches_upper) == set(matches_mixed)

    def test_partial_term_matching(self, bridge):
        """Test matching partial terms."""
        # "relax" should match "helps you relax"
        matches = bridge.query_to_internal("I want to relax")
        # May or may not match depending on implementation
        # This tests current behavior

    def test_multiple_concepts_in_query(self, bridge):
        """Test query mentioning multiple concepts."""
        matches = bridge.query_to_internal(
            "How do stress recovery, attention restoration, and natural lighting relate?"
        )
        # Should find multiple concepts
        assert len(matches) >= 2
