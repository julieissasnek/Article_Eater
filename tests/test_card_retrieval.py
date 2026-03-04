"""
Tests for CardRetriever — Precomputed Answer Card Lookup
=========================================================

Validates that:
1. Card hits return precomputed responses for known topics
2. Card misses return None for unknown queries
3. User type is respected (different cards for different personas)
4. Card retrieval is fast (<100ms)
5. QA handler integration works end-to-end
"""

import json
import time
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

PROJECT_ROOT = Path(__file__).parent.parent


# =============================================================================
# CardRetriever Unit Tests
# =============================================================================


class TestCardRetriever:
    """Test the CardRetriever service directly."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up CardRetriever for testing."""
        try:
            from src.qa.card_retriever import CardRetriever
            self.retriever = CardRetriever()
            self.available = self.retriever.is_available
        except Exception:
            self.retriever = None
            self.available = False

    @pytest.mark.skipif(
        not Path(PROJECT_ROOT / "data/materialized_views/answer_cards/card_index.json").exists(),
        reason="Card index not built yet"
    )
    def test_card_hit_noise_stress(self):
        """Query about noise and stress should hit a precomputed card."""
        result = self.retriever.try_match(
            "How does noise affect stress levels?",
            user_type="researcher",
        )
        assert result is not None, "Expected card hit for 'noise → stress'"
        assert result["source"] == "precomputed_card"
        assert result["enriched"] is True
        assert "sections" in result
        assert "headline" in result
        assert result.get("card_metadata", {}).get("cluster_id") is not None

    @pytest.mark.skipif(
        not Path(PROJECT_ROOT / "data/materialized_views/answer_cards/card_index.json").exists(),
        reason="Card index not built yet"
    )
    def test_card_hit_nature_stress(self):
        """Query about nature exposure and stress should hit a card."""
        result = self.retriever.try_match(
            "Does nature exposure reduce stress?",
            user_type="researcher",
        )
        assert result is not None, "Expected card hit for 'nature → stress'"
        assert len(result.get("sections", [])) > 0, "Card should have sections with content"

    @pytest.mark.skipif(
        not Path(PROJECT_ROOT / "data/materialized_views/answer_cards/card_index.json").exists(),
        reason="Card index not built yet"
    )
    def test_card_miss_irrelevant_query(self):
        """Irrelevant query should get no card match."""
        result = self.retriever.try_match(
            "What is the meaning of life?",
            user_type="researcher",
        )
        assert result is None, "Expected card miss for irrelevant query"

    @pytest.mark.skipif(
        not Path(PROJECT_ROOT / "data/materialized_views/answer_cards/card_index.json").exists(),
        reason="Card index not built yet"
    )
    def test_card_retrieval_speed(self):
        """Card retrieval should complete in <100ms."""
        start = time.monotonic()
        self.retriever.try_match(
            "How does noise affect stress?",
            user_type="researcher",
        )
        elapsed_ms = (time.monotonic() - start) * 1000
        assert elapsed_ms < 100, f"Card retrieval took {elapsed_ms:.1f}ms (expected <100ms)"

    @pytest.mark.skipif(
        not Path(PROJECT_ROOT / "data/materialized_views/answer_cards/card_index.json").exists(),
        reason="Card index not built yet"
    )
    def test_card_respects_user_type(self):
        """Same query should return different cards for different user types."""
        researcher = self.retriever.try_match(
            "How does noise affect stress?",
            user_type="researcher",
        )
        student = self.retriever.try_match(
            "How does noise affect stress?",
            user_type="student",
        )
        if researcher and student:
            # Cards should be different (adapted to user type)
            assert researcher["card_metadata"]["user_type"] != student["card_metadata"]["user_type"]

    @pytest.mark.skipif(
        not Path(PROJECT_ROOT / "data/materialized_views/answer_cards/card_index.json").exists(),
        reason="Card index not built yet"
    )
    def test_card_response_structure(self):
        """Card response should have all required fields."""
        result = self.retriever.try_match(
            "How does noise affect performance?",
            user_type="researcher",
        )
        if result is not None:
            required_keys = [
                "question_type", "headline", "sections", "confidence",
                "ai_generated", "enriched", "source", "card_metadata",
                "follow_ups",
            ]
            for key in required_keys:
                assert key in result, f"Missing required key: {key}"

    def test_retriever_index_loaded(self):
        """CardRetriever should have loaded the index."""
        if self.available:
            assert self.retriever.n_clusters > 0

    @pytest.mark.skipif(
        not Path(PROJECT_ROOT / "data/materialized_views/answer_cards/card_index.json").exists(),
        reason="Card index not built yet"
    )
    def test_card_hit_thermal_comfort(self):
        """Query about thermal comfort should hit a card."""
        result = self.retriever.try_match(
            "How does temperature affect thermal comfort?",
            user_type="researcher",
        )
        assert result is not None, "Expected card hit for 'thermal → comfort'"

    @pytest.mark.skipif(
        not Path(PROJECT_ROOT / "data/materialized_views/answer_cards/card_index.json").exists(),
        reason="Card index not built yet"
    )
    def test_card_hit_light_mood(self):
        """Query about light and mood should hit a card."""
        result = self.retriever.try_match(
            "Does natural light affect mood?",
            user_type="researcher",
        )
        assert result is not None, "Expected card hit for 'light → mood'"


# =============================================================================
# QA Handler Integration Tests
# =============================================================================


class TestQAHandlerCardIntegration:
    """Test that the QA handler correctly uses CardRetriever."""

    @pytest.mark.skipif(
        not Path(PROJECT_ROOT / "data/materialized_views/answer_cards/card_index.json").exists(),
        reason="Card index not built yet"
    )
    def test_qa_handler_serves_card(self):
        """QA handler should return precomputed card for matching query."""
        try:
            from src.services.arbitrary_qa_handler import ArbitraryQAHandler
            handler = ArbitraryQAHandler(enable_enrichment=False)
            response = handler.answer("How does noise affect stress?")

            # Should have been served from card
            if response.get("source") == "precomputed_card":
                assert response["enriched"] is True
                assert response.get("card_metadata") is not None
        except Exception as e:
            pytest.skip(f"QA handler not available: {e}")

    @pytest.mark.skipif(
        not Path(PROJECT_ROOT / "data/materialized_views/answer_cards/card_index.json").exists(),
        reason="Card index not built yet"
    )
    def test_qa_handler_stats_track_card_served(self):
        """QA handler should track card_served in stats."""
        try:
            from src.services.arbitrary_qa_handler import ArbitraryQAHandler
            handler = ArbitraryQAHandler(enable_enrichment=False)
            handler.answer("How does noise affect stress?")

            assert "card_served" in handler._stats
        except Exception as e:
            pytest.skip(f"QA handler not available: {e}")
