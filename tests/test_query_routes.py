"""
Tests for Query API Routes
==========================

Tests for natural language query endpoints.

Date: January 21, 2026
Phase C Sprint C4
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI

from app.routes.query import (
    router, get_web, set_web
)
from src.services.web_of_belief import (
    WebOfBelief, Belief, Credence, EpistemicLevel, SourceDepth
)


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def app():
    """Create test FastAPI app."""
    app = FastAPI()
    app.include_router(router)
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def clean_state():
    """Reset state before each test."""
    set_web(WebOfBelief())
    yield
    set_web(WebOfBelief())


@pytest.fixture
def populated_web():
    """Create web with test beliefs."""
    web = WebOfBelief()

    # Add test beliefs
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

    # Abstract-only causal claim
    b3 = Belief(
        belief_id="light_3",
        content="Natural light causes improved cognitive function",
        level=EpistemicLevel.EMPIRICAL,
        credence=Credence(0.65, 0.20),
        outcome_id="cognition",
        source_depth=SourceDepth.ABSTRACT,
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

    set_web(web)
    return web


# =============================================================================
# Parse Endpoint Tests
# =============================================================================

class TestParseEndpoint:
    """Tests for the /parse endpoint."""

    def test_parse_simple_query(self, client, clean_state):
        """Test parsing a simple query."""
        response = client.post("/api/query/parse", json={
            "query": "Does natural light affect productivity?"
        })

        assert response.status_code == 200
        data = response.json()
        assert data["query_type"] == "does_affect"
        assert "light" in data["subject"].lower()
        assert "productivity" in data["object"].lower()

    def test_parse_with_expansions(self, client, clean_state):
        """Test that parsing includes vocabulary expansions."""
        response = client.post("/api/query/parse", json={
            "query": "Does natural light affect productivity?"
        })

        data = response.json()
        # Should have expansions for known terms
        assert "subject_expansions" in data
        assert "object_expansions" in data

    def test_parse_what_do_we_know(self, client, clean_state):
        """Test parsing 'what do we know' query."""
        response = client.post("/api/query/parse", json={
            "query": "What do we know about biophilic design?"
        })

        data = response.json()
        assert data["query_type"] == "what_know"  # Matches QueryType.WHAT_DO_WE_KNOW.value

    def test_parse_unknown_query(self, client, clean_state):
        """Test parsing an unrecognized query."""
        response = client.post("/api/query/parse", json={
            "query": "blarg flibble wobble"
        })

        data = response.json()
        assert data["query_type"] == "unknown"
        assert data["needs_clarification"] is True

    def test_parse_validation_too_short(self, client, clean_state):
        """Test validation rejects too-short queries."""
        response = client.post("/api/query/parse", json={
            "query": "hi"
        })

        assert response.status_code == 422


# =============================================================================
# Search Endpoint Tests
# =============================================================================

class TestSearchEndpoint:
    """Tests for the /search endpoint."""

    def test_search_empty_web(self, client, clean_state):
        """Test search with no beliefs."""
        response = client.post("/api/query/search", json={
            "query": "Does natural light affect productivity?"
        })

        assert response.status_code == 200
        data = response.json()
        assert data["confidence_level"] == "unknown"
        assert len(data["evidence_items"]) == 0

    def test_search_with_results(self, client, populated_web):
        """Test search returns matching beliefs."""
        response = client.post("/api/query/search", json={
            "query": "Does natural light affect productivity?"
        })

        assert response.status_code == 200
        data = response.json()
        assert len(data["evidence_items"]) > 0
        assert data["total_supporting"] > 0

    def test_search_exactly_three_followups(self, client, populated_web):
        """Test that search returns exactly 3 follow-ups (per Simon)."""
        response = client.post("/api/query/search", json={
            "query": "Does natural light affect productivity?"
        })

        data = response.json()
        assert len(data["follow_ups"]) == 3

        # Check follow-up types (H4: "broader" changed to "scope" per Cartwright/Simon)
        types = {f["type"] for f in data["follow_ups"]}
        assert "deeper" in types
        assert "scope" in types
        assert "uncertainty" in types

    def test_search_abstract_only_warning(self, client, populated_web):
        """Test warning for abstract-only causal claims (Cartwright)."""
        response = client.post("/api/query/search", json={
            "query": "Does natural light cause improved cognition?"
        })

        data = response.json()
        # Should have abstract warning because light_3 is abstract-only causal
        if data["abstract_only_warning"]:
            assert len(data["warnings"]) > 0
            assert any("abstract" in w.lower() for w in data["warnings"])

    def test_search_contested_warning(self, client, populated_web):
        """Test warning for contested beliefs."""
        response = client.post("/api/query/search", json={
            "query": "Does open office design affect productivity?"
        })

        data = response.json()
        if data["is_contested"]:
            assert any("contested" in w.lower() for w in data["warnings"])

    def test_search_includes_vocabulary(self, client, populated_web):
        """Test that search includes vocabulary expansions (per Bates)."""
        response = client.post("/api/query/search", json={
            "query": "Does natural light affect productivity?",
            "include_expansions": True
        })

        data = response.json()
        assert "vocabulary_used" in data

    def test_search_without_vocabulary(self, client, populated_web):
        """Test search without vocabulary expansions."""
        response = client.post("/api/query/search", json={
            "query": "Does natural light affect productivity?",
            "include_expansions": False
        })

        data = response.json()
        assert data["vocabulary_used"] == {}

    def test_search_max_evidence(self, client, populated_web):
        """Test max_evidence parameter."""
        response = client.post("/api/query/search", json={
            "query": "Does natural light affect productivity?",
            "max_evidence": 2
        })

        data = response.json()
        assert len(data["evidence_items"]) <= 2


# =============================================================================
# Query Types Endpoint Tests
# =============================================================================

class TestQueryTypesEndpoint:
    """Tests for the /types endpoint."""

    def test_get_query_types(self, client, clean_state):
        """Test getting query types."""
        response = client.get("/api/query/types")

        assert response.status_code == 200
        data = response.json()

        # Check expected types
        assert "what_is" in data
        assert "does_affect" in data
        assert "how_much" in data
        assert "compare" in data

    def test_query_types_have_descriptions(self, client, clean_state):
        """Test that types have descriptions."""
        response = client.get("/api/query/types")
        data = response.json()

        for query_type, description in data.items():
            assert len(description) > 0


# =============================================================================
# Suggestions Endpoint Tests
# =============================================================================

class TestSuggestionsEndpoint:
    """Tests for the /suggestions endpoint."""

    def test_get_suggestions(self, client, clean_state):
        """Test getting query suggestions."""
        response = client.get("/api/query/suggestions")

        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0

    def test_suggestions_structure(self, client, clean_state):
        """Test suggestion structure."""
        response = client.get("/api/query/suggestions")
        data = response.json()

        for suggestion in data:
            assert "query" in suggestion
            assert "description" in suggestion
            assert "category" in suggestion

    def test_suggestions_have_categories(self, client, clean_state):
        """Test suggestions have varied categories."""
        response = client.get("/api/query/suggestions")
        data = response.json()

        categories = {s["category"] for s in data}
        assert len(categories) >= 3  # Multiple categories


# =============================================================================
# Vocabulary Endpoint Tests
# =============================================================================

class TestVocabularyEndpoint:
    """Tests for the /vocabulary endpoint."""

    def test_expand_known_term(self, client, clean_state):
        """Test expanding a known term."""
        response = client.get("/api/query/vocabulary/natural%20light")

        assert response.status_code == 200
        data = response.json()
        assert data["term"] == "natural light"
        assert len(data["expansions"]) > 0
        assert "daylight" in data["expansions"] or "sunlight" in data["expansions"]

    def test_expand_unknown_term(self, client, clean_state):
        """Test expanding an unknown term."""
        response = client.get("/api/query/vocabulary/xyzzy")

        assert response.status_code == 200
        data = response.json()
        assert data["term"] == "xyzzy"
        assert data["expansions"] == []


# =============================================================================
# Stats Endpoint Tests
# =============================================================================

class TestStatsEndpoint:
    """Tests for the /stats endpoint."""

    def test_get_stats_empty(self, client, clean_state):
        """Test stats with empty web."""
        response = client.get("/api/query/stats")

        assert response.status_code == 200
        data = response.json()
        assert data["beliefs_available"] == 0
        assert data["follow_ups_per_query"] == 3  # Per Simon

    def test_get_stats_populated(self, client, populated_web):
        """Test stats with populated web."""
        response = client.get("/api/query/stats")

        data = response.json()
        assert data["beliefs_available"] > 0


# =============================================================================
# Integration Tests
# =============================================================================

class TestQueryIntegration:
    """Integration tests for query workflow."""

    def test_full_query_workflow(self, client, populated_web):
        """Test complete query workflow."""
        # 1. Get suggestions
        suggestions = client.get("/api/query/suggestions").json()
        assert len(suggestions) > 0

        # 2. Parse a query
        parse_result = client.post("/api/query/parse", json={
            "query": "Does natural light affect productivity?"
        }).json()

        assert parse_result["query_type"] == "does_affect"
        assert parse_result["confidence"] > 0.5

        # 3. Search for evidence
        search_result = client.post("/api/query/search", json={
            "query": "Does natural light affect productivity?"
        }).json()

        assert len(search_result["evidence_items"]) > 0
        assert len(search_result["follow_ups"]) == 3

        # 4. Follow a follow-up
        deeper = search_result["follow_ups"][0]
        assert deeper["type"] == "deeper"

        # 5. Search the follow-up
        followup_result = client.post("/api/query/search", json={
            "query": deeper["question"]
        }).json()

        # Should get a valid response
        assert "summary" in followup_result

    def test_multiple_query_types(self, client, populated_web):
        """Test different query types."""
        queries = [
            ("Does natural light affect productivity?", "does_affect"),
            ("What do we know about daylight?", "what_know"),  # QueryType.WHAT_DO_WE_KNOW.value
            ("How confident are we about light effects?", "confidence"),  # QueryType.HOW_CONFIDENT.value
            ("Compare natural and artificial light", "compare"),
        ]

        for query, expected_type in queries:
            result = client.post("/api/query/parse", json={"query": query}).json()
            assert result["query_type"] == expected_type, f"Failed for: {query}"

    def test_evidence_item_structure(self, client, populated_web):
        """Test evidence item has all required fields."""
        result = client.post("/api/query/search", json={
            "query": "Does natural light affect productivity?"
        }).json()

        if len(result["evidence_items"]) > 0:
            item = result["evidence_items"][0]
            assert "belief_id" in item
            assert "content" in item
            assert "credence" in item
            assert "source_depth" in item
            assert "paper_ids" in item
            assert "is_causal" in item
            assert "needs_caution" in item
