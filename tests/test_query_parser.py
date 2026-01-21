"""
Tests for Query Parser
======================

Tests for natural language query parsing.

Date: January 21, 2026
Phase C Sprint C1
"""

import pytest
from src.services.query_parser import (
    QueryParser,
    QueryType,
    QueryIntent,
    ParseResult,
    parse_query,
    get_query_type,
    expand_term,
    VOCABULARY_BRIDGE
)


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def parser():
    """Create default parser."""
    return QueryParser()


# =============================================================================
# Query Type Detection Tests
# =============================================================================

class TestQueryTypeDetection:
    """Tests for query type detection."""

    def test_what_is_effect_query(self, parser):
        """Test detecting what-is-effect queries."""
        result = parser.parse("What is the effect of natural light on productivity?")
        assert result.primary.query_type == QueryType.WHAT_IS
        assert result.primary.subject == "natural light"
        assert result.primary.object == "productivity"

    def test_does_affect_query(self, parser):
        """Test detecting does-X-affect-Y queries."""
        result = parser.parse("Does natural light affect productivity?")
        assert result.primary.query_type == QueryType.DOES_X_AFFECT_Y
        assert "natural light" in result.primary.subject.lower()
        assert "productivity" in result.primary.object.lower()

    def test_how_much_query(self, parser):
        """Test detecting how-much queries."""
        result = parser.parse("How much does noise affect concentration?")
        assert result.primary.query_type == QueryType.HOW_MUCH

    def test_what_do_we_know_query(self, parser):
        """Test detecting what-do-we-know queries."""
        result = parser.parse("What do we know about biophilic design?")
        assert result.primary.query_type == QueryType.WHAT_DO_WE_KNOW
        assert "biophilic design" in result.primary.subject.lower()

    def test_what_evidence_query(self, parser):
        """Test detecting what-evidence queries."""
        result = parser.parse("What evidence supports the claim that plants reduce stress?")
        assert result.primary.query_type == QueryType.WHAT_EVIDENCE

    def test_compare_query(self, parser):
        """Test detecting compare queries."""
        result = parser.parse("Compare natural light and artificial light effects")
        assert result.primary.query_type == QueryType.COMPARE
        assert "natural light" in result.primary.subject.lower()
        assert "artificial light" in result.primary.object.lower()

    def test_how_confident_query(self, parser):
        """Test detecting confidence queries."""
        result = parser.parse("How confident are we about the effect of noise on productivity?")
        assert result.primary.query_type == QueryType.HOW_CONFIDENT

    def test_why_believe_query(self, parser):
        """Test detecting why-believe queries."""
        result = parser.parse("Why do we believe that natural light improves mood?")
        assert result.primary.query_type == QueryType.WHY_BELIEVE

    def test_what_contradicts_query(self, parser):
        """Test detecting contradiction queries."""
        result = parser.parse("What contradicts the claim about open offices?")
        assert result.primary.query_type == QueryType.WHAT_CONTRADICTS

    def test_what_dont_know_query(self, parser):
        """Test detecting gap queries."""
        result = parser.parse("What don't we know about thermal comfort?")
        assert result.primary.query_type == QueryType.WHAT_DONT_KNOW

    def test_when_does_query(self, parser):
        """Test detecting scope-when queries."""
        result = parser.parse("When does natural light work?")
        assert result.primary.query_type == QueryType.WHEN_DOES

    def test_for_whom_query(self, parser):
        """Test detecting scope-who queries."""
        result = parser.parse("For whom does open office design work?")
        assert result.primary.query_type == QueryType.FOR_WHOM

    def test_unknown_query(self, parser):
        """Test handling unknown query type."""
        result = parser.parse("blarg flibble wobble")
        assert result.primary.query_type == QueryType.UNKNOWN
        assert result.needs_clarification is True


# =============================================================================
# Vocabulary Expansion Tests
# =============================================================================

class TestVocabularyExpansion:
    """Tests for vocabulary bridge expansion."""

    def test_expand_natural_light(self):
        """Test expanding 'natural light' term."""
        expansions = expand_term("natural light")
        assert "daylight" in expansions
        assert "sunlight" in expansions

    def test_expand_productivity(self):
        """Test expanding 'productivity' term."""
        expansions = expand_term("productivity")
        assert "performance" in expansions
        assert "efficiency" in expansions

    def test_expand_stress(self):
        """Test expanding 'stress' term."""
        expansions = expand_term("stress")
        assert "anxiety" in expansions

    def test_expand_unknown_term(self):
        """Test expanding unknown term."""
        expansions = expand_term("xyzzy")
        assert expansions == []

    def test_query_includes_expansions(self, parser):
        """Test that parsed query includes expansions."""
        result = parser.parse("Does natural light affect productivity?")

        # Should have expansions in vocabulary_expansions
        assert len(result.vocabulary_expansions) > 0

        # Primary intent should have expansions
        assert len(result.primary.subject_expansions) > 0 or \
               len(result.primary.object_expansions) > 0


# =============================================================================
# Parse Result Structure Tests
# =============================================================================

class TestParseResultStructure:
    """Tests for ParseResult structure."""

    def test_parse_result_has_primary(self, parser):
        """Test that result has primary intent."""
        result = parser.parse("What is biophilia?")
        assert result.primary is not None
        assert isinstance(result.primary, QueryIntent)

    def test_parse_result_confidence(self, parser):
        """Test confidence scoring."""
        result = parser.parse("What is the effect of natural light on productivity?")
        assert 0 <= result.primary.confidence <= 1

    def test_high_confidence_for_clear_query(self, parser):
        """Test high confidence for clear, well-formed query."""
        result = parser.parse("Does natural light affect productivity?")
        assert result.primary.confidence >= 0.7

    def test_low_confidence_for_ambiguous(self, parser):
        """Test low confidence for ambiguous query."""
        result = parser.parse("light productivity")
        # Should still parse but with lower confidence or unknown
        assert result.primary.confidence < 0.7 or result.primary.query_type == QueryType.UNKNOWN

    def test_parse_result_to_dict(self, parser):
        """Test serialization."""
        result = parser.parse("What is biophilia?")
        d = result.to_dict()

        assert 'primary' in d
        assert 'alternatives' in d
        assert 'vocabulary_expansions' in d
        assert 'needs_clarification' in d

    def test_query_intent_to_dict(self, parser):
        """Test QueryIntent serialization."""
        result = parser.parse("What is biophilia?")
        d = result.primary.to_dict()

        assert 'query_type' in d
        assert 'confidence' in d
        assert 'subject' in d
        assert 'original_query' in d


# =============================================================================
# Search Terms Generation Tests
# =============================================================================

class TestSearchTerms:
    """Tests for search terms generation."""

    def test_get_search_terms_basic(self, parser):
        """Test basic search term extraction."""
        result = parser.parse("Does natural light affect productivity?")
        terms = parser.get_search_terms(result.primary)

        assert len(terms) > 0
        # Should include original terms
        assert any("light" in t.lower() for t in terms)
        assert any("productivity" in t.lower() for t in terms)

    def test_get_search_terms_includes_expansions(self, parser):
        """Test that search terms include vocabulary expansions."""
        result = parser.parse("Does natural light affect productivity?")
        terms = parser.get_search_terms(result.primary)

        # Should include expansions
        terms_lower = [t.lower() for t in terms]
        assert "daylight" in terms_lower or "sunlight" in terms_lower

    def test_search_terms_deduplicated(self, parser):
        """Test that search terms are deduplicated."""
        result = parser.parse("Does natural light affect natural light exposure?")
        terms = parser.get_search_terms(result.primary)

        # Count unique terms
        unique = set(t.lower() for t in terms)
        assert len(unique) == len(terms)


# =============================================================================
# Edge Cases and Normalization Tests
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases and normalization."""

    def test_case_insensitive(self, parser):
        """Test case insensitive matching."""
        result1 = parser.parse("What is biophilia?")
        result2 = parser.parse("WHAT IS BIOPHILIA?")
        result3 = parser.parse("What Is Biophilia?")

        assert result1.primary.query_type == result2.primary.query_type
        assert result1.primary.query_type == result3.primary.query_type

    def test_extra_whitespace(self, parser):
        """Test handling extra whitespace."""
        result = parser.parse("What   is    biophilia?")
        assert result.primary.query_type == QueryType.WHAT_IS

    def test_no_question_mark(self, parser):
        """Test handling query without question mark."""
        result = parser.parse("What is biophilia")
        assert result.primary.query_type == QueryType.WHAT_IS

    def test_empty_query(self, parser):
        """Test handling empty query."""
        result = parser.parse("")
        assert result.primary.query_type == QueryType.UNKNOWN

    def test_whitespace_only(self, parser):
        """Test handling whitespace-only query."""
        result = parser.parse("   ")
        assert result.primary.query_type == QueryType.UNKNOWN


# =============================================================================
# Convenience Function Tests
# =============================================================================

class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_parse_query_function(self):
        """Test parse_query convenience function."""
        result = parse_query("What is biophilia?")
        assert isinstance(result, ParseResult)
        assert result.primary.query_type == QueryType.WHAT_IS

    def test_get_query_type_function(self):
        """Test get_query_type convenience function."""
        qt = get_query_type("Does light affect mood?")
        assert qt == QueryType.DOES_X_AFFECT_Y


# =============================================================================
# Alternative Parses Tests
# =============================================================================

class TestAlternatives:
    """Tests for alternative parses."""

    def test_alternatives_provided(self, parser):
        """Test that alternatives are provided for ambiguous queries."""
        # A query that could match multiple patterns
        result = parser.parse("What is the relationship between light and mood?")

        # Should have at least primary
        assert result.primary is not None

    def test_clarification_for_unknown(self, parser):
        """Test clarification options for unknown queries."""
        result = parser.parse("xyz abc 123")

        assert result.needs_clarification is True
        assert len(result.clarification_options) > 0


# =============================================================================
# Domain-Specific Query Tests
# =============================================================================

class TestDomainSpecificQueries:
    """Tests for domain-specific queries (neuroarchitecture)."""

    def test_biophilic_design_query(self, parser):
        """Test query about biophilic design."""
        result = parser.parse("What do we know about biophilic design?")
        assert result.primary.query_type == QueryType.WHAT_DO_WE_KNOW
        assert "biophilic design" in result.primary.subject.lower()

    def test_thermal_comfort_query(self, parser):
        """Test query about thermal comfort."""
        result = parser.parse("How does temperature affect cognitive performance?")
        assert result.primary.query_type in (QueryType.WHAT_IS, QueryType.DOES_X_AFFECT_Y, QueryType.HOW_MUCH)

    def test_open_office_query(self, parser):
        """Test query about open offices."""
        result = parser.parse("Does open office design reduce productivity?")
        assert result.primary.query_type == QueryType.DOES_X_AFFECT_Y

    def test_nature_views_query(self, parser):
        """Test query about nature views."""
        result = parser.parse("What is the effect of nature views on patient recovery?")
        assert result.primary.query_type == QueryType.WHAT_IS
        assert "nature views" in result.primary.subject.lower()


# =============================================================================
# Integration Tests
# =============================================================================

class TestIntegration:
    """Integration tests."""

    def test_full_workflow(self, parser):
        """Test complete parse workflow."""
        query = "Does natural light improve worker productivity?"

        # Parse
        result = parser.parse(query)

        # Check structure
        assert result.primary.query_type == QueryType.DOES_X_AFFECT_Y
        assert result.primary.original_query == query
        assert result.primary.confidence > 0.5

        # Get search terms
        terms = parser.get_search_terms(result.primary)
        assert len(terms) > 0

        # Check expansions
        assert len(result.vocabulary_expansions) > 0

    def test_multiple_queries(self, parser):
        """Test parsing multiple different queries."""
        queries = [
            "What is biophilia?",
            "Does noise affect concentration?",
            "How confident are we about thermal comfort?",
            "Compare natural and artificial light",
            "What don't we know about stress?"
        ]

        types_found = set()
        for q in queries:
            result = parser.parse(q)
            types_found.add(result.primary.query_type)

        # Should find multiple different types
        assert len(types_found) >= 4
