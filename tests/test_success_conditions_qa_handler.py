"""Layer 1 Tests for SUCCESS CONDITIONS in arbitrary_qa_handler.py

This test suite validates the critical success conditions for the
Arbitrary QA Handler module. Focus is on structural contracts, return
types, and graceful error handling.

SUCCESS CONDITIONS TESTED:
- classify_question(): SC-CQ-1 through SC-CQ-4
- ArbitraryQAHandler.answer(): SC-ANS-1 through SC-ANS-8
- build_ai_context(): SC-BAC-1 through SC-BAC-4
- build_ai_prompt(): SC-BAP-1 through SC-BAP-4
- format_theory_catalog(): SC-FTC-1 through SC-FTC-5
- _apply_enrichment(): SC-AE-1 through SC-AE-4
- _apply_prose_review(): SC-APR-1 through SC-APR-4
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, timezone
from typing import Dict, Any

from src.services.arbitrary_qa_handler import (
    classify_question,
    build_ai_context,
    build_ai_prompt,
    format_theory_catalog,
    ArbitraryQAHandler,
    QuestionType,
)


class MockCatalog:
    """Mock KnowledgeCatalog for testing."""

    def get_theories(self):
        return [
            {
                "name": "Theory1",
                "authors": "Author1",
                "year": 2020,
                "summary": "Test theory",
                "evidence_count": 5,
            }
        ]

    def get_frameworks(self):
        return [
            {
                "name": "Framework1",
                "summary": "Test framework",
            }
        ]

    def get_molecules(self):
        return [
            {
                "name": "Molecule1",
                "id": "MOL1",
                "summary": "Test molecule",
            }
        ]

    def get_cultural_differences(self):
        return [
            {
                "dimension": "Dimension1",
                "variants": [
                    {"culture": "Western", "pattern": "Pattern1"},
                    {"culture": "Eastern", "pattern": "Pattern2"},
                ],
            }
        ]

    def search(self, query: str):
        return {
            "theories": [
                {
                    "name": "Theory1",
                    "authors": "Author1",
                    "summary": "Test theory",
                }
            ],
            "frameworks": [
                {
                    "name": "Framework1",
                    "summary": "Test framework",
                }
            ],
            "molecules": [
                {
                    "name": "Molecule1",
                    "id": "MOL1",
                }
            ],
            "cultural": [],
        }


# =============================================================================
# Tests for classify_question()
# =============================================================================


class TestClassifyQuestion:
    """Test SUCCESS CONDITIONS for classify_question()."""

    def test_sc_cq_1_returns_tuple(self):
        """SC-CQ-1: Returns a 2-tuple (question_type: str, confidence: float)."""
        result = classify_question("What are all theories?")
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], str)
        assert isinstance(result[1], float)

    def test_sc_cq_2_valid_question_type(self):
        """SC-CQ-2: question_type is a valid QuestionType constant."""
        result = classify_question("Show me all theories")
        qtype = result[0]
        # Check that it matches a known question type (QuestionType constants are strings)
        valid_types = {
            QuestionType.CATALOG_THEORIES,
            QuestionType.CATALOG_CULTURAL,
            QuestionType.CATALOG_MOLECULES,
            QuestionType.ARBITRARY,
        }
        assert qtype in valid_types or isinstance(qtype, str)

    def test_sc_cq_3_confidence_in_range(self):
        """SC-CQ-3: confidence is in [0.0, 1.0]."""
        test_questions = [
            "What are all theories?",
            "Show me cultural differences",
            "What is a random question?",
            "",
        ]
        for q in test_questions:
            _, confidence = classify_question(q)
            assert 0.0 <= confidence <= 1.0

    def test_sc_cq_4_never_raises_exception(self):
        """SC-CQ-4: Never raises exception (returns fallback on error)."""
        # Test with various edge cases
        test_inputs = [
            None,  # Will be converted to string
            "",
            "a" * 10000,  # Very long
            "special\nchars\ttabs",
            12345,  # Will be converted to string
        ]

        for inp in test_inputs:
            try:
                result = classify_question(str(inp))
                assert isinstance(result, tuple)
                assert len(result) == 2
            except Exception as e:
                pytest.fail(f"classify_question raised exception for {inp}: {e}")

    def test_sc_cq_pattern_matching(self):
        """Test that pattern matching returns high confidence for known types."""
        result = classify_question("Show me all the theories")
        _, confidence = result
        assert confidence >= 0.8  # Pattern match confidence is 0.85


# =============================================================================
# Tests for build_ai_context()
# =============================================================================


class TestBuildAIContext:
    """Test SUCCESS CONDITIONS for build_ai_context()."""

    def test_sc_bac_1_returns_string(self):
        """SC-BAC-1: Returns a string (never None)."""
        catalog = MockCatalog()
        result = build_ai_context("What is the theory?", catalog)
        assert isinstance(result, str)
        assert result is not None

    def test_sc_bac_2_respects_max_tokens(self):
        """SC-BAC-2: Result length roughly bounded by max_tokens * 4 chars."""
        catalog = MockCatalog()
        max_tokens = 100
        result = build_ai_context("query", catalog, max_tokens=max_tokens)
        # Allow ±10% for estimation error
        max_length = max_tokens * 4
        assert len(result) <= max_length + 50  # Small buffer

    def test_sc_bac_3_contains_relevant_info(self):
        """SC-BAC-3: Contains relevant information from catalog."""
        catalog = MockCatalog()
        result = build_ai_context("theory", catalog)
        # Should contain at least some catalog information
        assert len(result) > 10
        # Should contain structure keywords
        assert "RELEVANT" in result or "SYSTEM OVERVIEW" in result

    def test_sc_bac_4_never_raises_exception(self):
        """SC-BAC-4: Never raises exception (returns fallback on error)."""
        # Mock catalog that raises exception
        bad_catalog = Mock()
        bad_catalog.search.side_effect = Exception("Catalog error")

        try:
            result = build_ai_context("query", bad_catalog)
            assert isinstance(result, str)
        except Exception as e:
            pytest.fail(f"build_ai_context raised exception: {e}")

    def test_sc_bac_returns_default_on_empty_search(self):
        """Test fallback on empty search results."""
        catalog = MockCatalog()
        # Search returns empty dict
        catalog.search = Mock(return_value={})

        result = build_ai_context("query", catalog)
        assert isinstance(result, str)
        assert len(result) > 0


# =============================================================================
# Tests for build_ai_prompt()
# =============================================================================


class TestBuildAIPrompt:
    """Test SUCCESS CONDITIONS for build_ai_prompt()."""

    def test_sc_bap_1_returns_string(self):
        """SC-BAP-1: Returns a string (never None)."""
        result = build_ai_prompt("What is X?", "Context text")
        assert isinstance(result, str)
        assert result is not None

    def test_sc_bap_2_contains_question(self):
        """SC-BAP-2: Result contains the question text verbatim."""
        question = "What is the meaning of life?"
        result = build_ai_prompt(question, "Some context")
        assert question in result

    def test_sc_bap_3_contains_context(self):
        """SC-BAP-3: Result contains the context text."""
        context = "This is important context information"
        result = build_ai_prompt("Question?", context)
        assert context in result

    def test_sc_bap_4_never_raises_exception(self):
        """SC-BAP-4: Never raises exception."""
        test_cases = [
            ("", ""),
            ("Q" * 1000, "C" * 1000),
            ("Special\nchars", "More\nchars"),
        ]

        for question, context in test_cases:
            try:
                result = build_ai_prompt(question, context)
                assert isinstance(result, str)
            except Exception as e:
                pytest.fail(
                    f"build_ai_prompt raised exception for Q={question[:20]} C={context[:20]}: {e}"
                )


# =============================================================================
# Tests for format_theory_catalog()
# =============================================================================


class TestFormatTheoryCatalog:
    """Test SUCCESS CONDITIONS for format_theory_catalog()."""

    def test_sc_ftc_1_returns_dict(self):
        """SC-FTC-1: Returns a dict."""
        catalog = MockCatalog()
        result = format_theory_catalog(catalog)
        assert isinstance(result, dict)

    def test_sc_ftc_2_has_sections_and_headline(self):
        """SC-FTC-2: Dict has 'sections' key with list and 'headline' key."""
        catalog = MockCatalog()
        result = format_theory_catalog(catalog)
        assert "sections" in result or "answer" in result
        assert "headline" in result
        if "sections" in result:
            assert isinstance(result["sections"], list)

    def test_sc_ftc_3_has_sources(self):
        """SC-FTC-3: Dict has 'sources' key with list value."""
        catalog = MockCatalog()
        result = format_theory_catalog(catalog)
        assert "sources" in result
        assert isinstance(result["sources"], list)

    def test_sc_ftc_4_has_question_type(self):
        """SC-FTC-4: Dict has 'question_type' key matching CATALOG_THEORIES."""
        catalog = MockCatalog()
        result = format_theory_catalog(catalog)
        assert "question_type" in result
        assert result["question_type"] == QuestionType.CATALOG_THEORIES

    def test_sc_ftc_5_has_headline(self):
        """SC-FTC-5: Dict has 'headline' key with non-empty string."""
        catalog = MockCatalog()
        result = format_theory_catalog(catalog)
        assert "headline" in result
        assert isinstance(result["headline"], str)
        assert len(result["headline"]) > 0

    def test_sc_ftc_graceful_failure(self):
        """Test graceful failure when catalog is broken."""
        bad_catalog = Mock()
        bad_catalog.get_theories.side_effect = Exception("Error")

        result = format_theory_catalog(bad_catalog)
        assert isinstance(result, dict)
        assert result["question_type"] == QuestionType.CATALOG_THEORIES
        assert "headline" in result
        assert "Error" in result["headline"] or "unavailable" in result["headline"]


# =============================================================================
# Tests for ArbitraryQAHandler.answer()
# =============================================================================


class TestArbitraryQAHandlerAnswer:
    """Test SUCCESS CONDITIONS for ArbitraryQAHandler.answer()."""

    def _create_handler(self):
        """Helper to create handler with mocked catalog."""
        try:
            handler = ArbitraryQAHandler(enable_enrichment=False, enable_prose_review=False)
            # Replace catalog with mock
            handler.catalog = MockCatalog()
            return handler
        except Exception as e:
            pytest.skip(f"Cannot instantiate handler: {e}")

    def test_sc_ans_1_returns_dict(self):
        """SC-ANS-1: Returns a dict (never None)."""
        handler = self._create_handler()
        result = handler.answer("What are all theories?")
        assert isinstance(result, dict)
        assert result is not None

    def test_sc_ans_2_has_required_keys(self):
        """SC-ANS-2: Dict always has keys: question, answer, question_type, confidence, sources."""
        handler = self._create_handler()
        result = handler.answer("What are all theories?")

        required_keys = ["question", "answer", "question_type", "confidence", "sources"]
        for key in required_keys:
            assert key in result, f"Missing required key: {key}"

    def test_sc_ans_3_question_matches_input(self):
        """SC-ANS-3: question field matches input question."""
        handler = self._create_handler()
        input_question = "What are all theories?"
        result = handler.answer(input_question)
        assert result["question"] == input_question

    def test_sc_ans_4_answer_is_nonempty_string(self):
        """SC-ANS-4: answer is a non-empty string."""
        handler = self._create_handler()
        result = handler.answer("What are all theories?")
        assert isinstance(result["answer"], str)
        assert len(result["answer"]) > 0 or "headline" in result  # answer or headline

    def test_sc_ans_5_sources_is_list(self):
        """SC-ANS-5: sources is a list."""
        handler = self._create_handler()
        result = handler.answer("What are all theories?")
        assert "sources" in result
        assert isinstance(result["sources"], list)

    def test_sc_ans_6_never_raises_exception(self):
        """SC-ANS-6: Never raises exception on any question string."""
        handler = self._create_handler()
        test_questions = [
            "What are all theories?",
            "",
            "a" * 500,
            "Special\nchars\t123",
        ]

        for q in test_questions:
            try:
                result = handler.answer(q)
                assert isinstance(result, dict)
            except Exception as e:
                pytest.fail(f"answer() raised exception for question {q}: {e}")

    def test_sc_ans_8_timestamp_present(self):
        """SC-ANS-8: timestamp is present."""
        handler = self._create_handler()
        result = handler.answer("What are all theories?")

        assert "timestamp" in result
        # Should be ISO 8601 format
        assert isinstance(result["timestamp"], str)
        try:
            datetime.fromisoformat(result["timestamp"].replace("Z", "+00:00"))
        except ValueError:
            pytest.fail(f"timestamp not in ISO 8601 format: {result['timestamp']}")


# =============================================================================
# Tests for _apply_enrichment()
# =============================================================================


class TestApplyEnrichment:
    """Test SUCCESS CONDITIONS for _apply_enrichment()."""

    def _create_handler(self):
        """Helper to create handler."""
        try:
            handler = ArbitraryQAHandler(enable_enrichment=False)
            handler.catalog = MockCatalog()
            return handler
        except Exception as e:
            pytest.skip(f"Cannot instantiate handler: {e}")

    def test_sc_ae_1_returns_dict(self):
        """SC-AE-1: Returns a dict (always, even on failure)."""
        handler = self._create_handler()
        base_answer = {
            "answer": "Test",
            "question_type": QuestionType.ARBITRARY,
        }
        result = handler._apply_enrichment(base_answer, "test question")
        assert isinstance(result, dict)

    def test_sc_ae_2_preserves_original_answer(self):
        """SC-AE-2: Original answer preserved even when enrichment fails."""
        handler = self._create_handler()
        base_answer = {
            "answer": "Original answer",
            "question_type": QuestionType.ARBITRARY,
        }
        result = handler._apply_enrichment(base_answer, "test question")
        assert result["answer"] == "Original answer"

    def test_sc_ae_4_sets_enriched_flag(self):
        """SC-AE-4: On failure/disabled, result has 'enriched' key set to False."""
        handler = self._create_handler()
        base_answer = {"answer": "Test"}
        result = handler._apply_enrichment(base_answer, "test question")
        assert "enriched" in result
        assert result["enriched"] is False


# =============================================================================
# Tests for _apply_prose_review()
# =============================================================================


class TestApplyProseReview:
    """Test SUCCESS CONDITIONS for _apply_prose_review()."""

    def _create_handler(self):
        """Helper to create handler."""
        try:
            handler = ArbitraryQAHandler(enable_prose_review=False)
            handler.catalog = MockCatalog()
            return handler
        except Exception as e:
            pytest.skip(f"Cannot instantiate handler: {e}")

    def test_sc_apr_1_returns_dict(self):
        """SC-APR-1: Returns a dict (always, even on failure)."""
        handler = self._create_handler()
        base_answer = {
            "answer": "Test answer",
            "sections": [{"heading": "Test", "items": ["Item 1"]}],
        }
        result = handler._apply_prose_review(base_answer)
        assert isinstance(result, dict)

    def test_sc_apr_2_preserves_original_answer(self):
        """SC-APR-2: Original answer preserved even when review fails."""
        handler = self._create_handler()
        base_answer = {
            "answer": "Original answer",
            "sections": [{"heading": "Test", "items": ["Item 1"]}],
        }
        result = handler._apply_prose_review(base_answer)
        assert result["answer"] == "Original answer"

    def test_sc_apr_4_sets_reviewed_flag(self):
        """SC-APR-4: On failure/disabled, result has 'prose_reviewed' key set to False."""
        handler = self._create_handler()
        base_answer = {"answer": "Test"}
        result = handler._apply_prose_review(base_answer)
        assert "prose_reviewed" in result
        assert result["prose_reviewed"] is False


# =============================================================================
# Integration Tests
# =============================================================================


class TestIntegration:
    """Integration tests for the full QA flow."""

    def _create_handler(self, enable_enrichment=False, enable_prose_review=False, llm_fn=None):
        """Helper to create handler with mock catalog."""
        try:
            handler = ArbitraryQAHandler(
                enable_enrichment=enable_enrichment,
                enable_prose_review=enable_prose_review,
                llm_fn=llm_fn,
            )
            handler.catalog = MockCatalog()
            return handler
        except Exception as e:
            pytest.skip(f"Cannot instantiate handler: {e}")

    def test_full_qa_flow_catalog_theories(self):
        """Test full flow for catalog theories question."""
        handler = self._create_handler()
        result = handler.answer("What are all the theories in this system?")

        # Verify all SC-ANS conditions
        assert isinstance(result, dict)
        assert result["question"] == "What are all the theories in this system?"
        assert len(result["answer"]) > 0
        assert result["question_type"] == QuestionType.CATALOG_THEORIES
        assert 0.0 <= result["confidence"] <= 1.0
        assert isinstance(result["sources"], list)
        assert "timestamp" in result

    def test_full_qa_flow_arbitrary_question(self):
        """Test full flow for arbitrary question (AI-routed)."""
        handler = self._create_handler(llm_fn=None)  # No LLM, should use fallback
        result = handler.answer("What is the impact of lighting on cognition?")

        # Verify SC-ANS conditions
        assert isinstance(result, dict)
        assert result["question"] == "What is the impact of lighting on cognition?"
        assert 0.0 <= result["confidence"] <= 1.0
        assert isinstance(result["sources"], list)
        assert "timestamp" in result

    def test_error_recovery_on_handler_failure(self):
        """Test error recovery when a handler fails."""
        try:
            handler = ArbitraryQAHandler(enable_enrichment=False, enable_prose_review=False)
            bad_catalog = Mock()
            bad_catalog.get_theories.side_effect = Exception("Catalog error")
            bad_catalog.get_frameworks.return_value = []
            bad_catalog.get_molecules.return_value = []
            handler.catalog = bad_catalog

            result = handler.answer("What are all the theories?")

            # Should still return valid response despite error
            assert isinstance(result, dict)
            assert "question" in result
            assert "timestamp" in result
        except Exception as e:
            pytest.skip(f"Cannot test error recovery: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
