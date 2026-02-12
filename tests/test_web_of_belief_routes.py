"""
Tests for Web of Belief API Routes
==================================

Tests for Evidence Explorer API endpoints.

Date: January 21, 2026
Phase B Sprint B1
"""

import pytest
from fastapi.testclient import TestClient

# Import app and routes
from app.main import app
from app.routes.web_of_belief import set_web, get_web
from src.services.web_of_belief import (
    WebOfBelief,
    Belief,
    Credence,
    EpistemicLevel,
    SourceDepth,
    EnablingConditions,
    Constraint,
    ConstraintType
)


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def demo_web():
    """Create a demo web for testing."""
    web = WebOfBelief()

    # Add test beliefs - using outcome_id (which maps to outcome_category in API)
    b1 = Belief(
        belief_id="test_1",
        content="Natural light improves productivity",
        level=EpistemicLevel.EMPIRICAL,
        credence=Credence(0.75, 0.10),
        outcome_id="productivity",
        source_depth=SourceDepth.FULL_TEXT
    )
    web.beliefs[b1.belief_id] = b1

    b2 = Belief(
        belief_id="test_2",
        content="Biophilic design reduces stress",
        level=EpistemicLevel.EMPIRICAL,
        credence=Credence(0.68, 0.15),
        outcome_id="stress",
        source_depth=SourceDepth.ABSTRACT
    )
    web.beliefs[b2.belief_id] = b2

    b3 = Belief(
        belief_id="test_3",
        content="Open offices impact focus",
        level=EpistemicLevel.EMPIRICAL,
        credence=Credence(0.52, 0.25),
        outcome_id="productivity",
        contested=True
    )
    web.beliefs[b3.belief_id] = b3

    # Add connections (constraints)
    web.add_constraint(Constraint(
        constraint_id="c:test_1:test_2",
        source_id="test_1",
        target_id="test_2",
        constraint_type=ConstraintType.SUPPORTS,
        strength=0.6
    ))
    web.add_constraint(Constraint(
        constraint_id="c:test_3:test_1",
        source_id="test_3",
        target_id="test_1",
        constraint_type=ConstraintType.CONTRADICTS,
        strength=0.4
    ))

    # Add credence history
    for b in [b1, b2, b3]:
        for i in range(5):
            b.record_credence_change(b.credence.value + 0.01 * i, f"paper_{i}")

    set_web(web)
    return web


@pytest.fixture(autouse=True)
def reset_web():
    """Reset web before each test."""
    set_web(WebOfBelief())
    yield
    set_web(WebOfBelief())


# =============================================================================
# Graph Endpoint Tests
# =============================================================================

class TestGraphEndpoint:
    """Tests for /api/v1/web/graph endpoint."""

    def test_empty_graph(self, client):
        """Test getting empty graph."""
        response = client.get("/api/v1/web/graph")
        assert response.status_code == 200

        data = response.json()
        assert "nodes" in data
        assert "edges" in data
        assert "metadata" in data
        assert len(data["nodes"]) == 0

    def test_graph_with_beliefs(self, client, demo_web):
        """Test getting graph with beliefs."""
        response = client.get("/api/v1/web/graph")
        assert response.status_code == 200

        data = response.json()
        assert len(data["nodes"]) == 3
        assert len(data["edges"]) == 2

    def test_graph_max_nodes(self, client, demo_web):
        """Test max_nodes parameter."""
        response = client.get("/api/v1/web/graph?max_nodes=2")
        assert response.status_code == 200

        data = response.json()
        assert len(data["nodes"]) <= 2

    def test_graph_min_credence(self, client, demo_web):
        """Test min_credence filter."""
        response = client.get("/api/v1/web/graph?min_credence=0.7")
        assert response.status_code == 200

        data = response.json()
        # Only beliefs with credence >= 0.7 should be included
        for node in data["nodes"]:
            assert node["credence"] >= 0.7

    def test_graph_category_filter(self, client, demo_web):
        """Test outcome_category filter."""
        response = client.get("/api/v1/web/graph?outcome_category=productivity")
        assert response.status_code == 200

        data = response.json()
        for node in data["nodes"]:
            assert node["outcome_category"] == "productivity"

    def test_graph_exclude_contested(self, client, demo_web):
        """Test excluding contested beliefs."""
        response = client.get("/api/v1/web/graph?include_contested=false")
        assert response.status_code == 200

        data = response.json()
        for node in data["nodes"]:
            assert node.get("contested", False) is False

    def test_graph_metadata(self, client, demo_web):
        """Test graph metadata."""
        response = client.get("/api/v1/web/graph")
        assert response.status_code == 200

        data = response.json()
        metadata = data["metadata"]
        # Check actual metadata fields from GraphMetadata
        assert "coherence_score" in metadata
        assert "stub_count" in metadata
        assert "contested_count" in metadata
        assert "timestamp" in metadata


# =============================================================================
# Node Detail Endpoint Tests
# =============================================================================

class TestNodeDetailEndpoint:
    """Tests for /api/v1/web/node/{id} endpoint."""

    def test_node_not_found(self, client):
        """Test 404 for non-existent node."""
        response = client.get("/api/v1/web/node/nonexistent")
        assert response.status_code == 404

    def test_node_detail(self, client, demo_web):
        """Test getting node detail."""
        response = client.get("/api/v1/web/node/test_1")
        assert response.status_code == 200

        data = response.json()
        assert data["belief_id"] == "test_1"
        assert "Natural light" in data["content"]
        assert "credence" in data
        assert "value" in data["credence"]
        assert "status" in data

    def test_node_headline(self, client, demo_web):
        """Test headline progressive disclosure level."""
        response = client.get("/api/v1/web/node/test_1")
        data = response.json()

        assert "headline" in data
        # Headline should contain either confidence level or belief content
        assert "confidence" in data["headline"].lower() or "light" in data["headline"].lower()

    def test_node_summary(self, client, demo_web):
        """Test summary progressive disclosure level."""
        response = client.get("/api/v1/web/node/test_1")
        data = response.json()

        assert "summary" in data
        summary = data["summary"]
        assert "traffic_light" in summary
        assert "credence_value" in summary
        assert "source_count" in summary
        assert "disagreement_flag" in summary
        assert "stability_status" in summary

    def test_node_stability_info(self, client, demo_web):
        """Test stability info in node detail."""
        response = client.get("/api/v1/web/node/test_1")
        data = response.json()

        assert "stability_info" in data
        assert "is_stable" in data["stability_info"]

    def test_contested_node_flag(self, client, demo_web):
        """Test contested belief has correct flag."""
        response = client.get("/api/v1/web/node/test_3")
        data = response.json()

        summary = data["summary"]
        assert summary["disagreement_flag"] is True


# =============================================================================
# Search Endpoint Tests
# =============================================================================

class TestSearchEndpoint:
    """Tests for /api/v1/web/search endpoint."""

    def test_search_empty_web(self, client):
        """Test search on empty web."""
        response = client.get("/api/v1/web/search?q=test")
        assert response.status_code == 200

        data = response.json()
        assert data["query"] == "test"
        assert data["total_results"] == 0

    def test_search_finds_beliefs(self, client, demo_web):
        """Test search finds matching beliefs."""
        response = client.get("/api/v1/web/search?q=light")
        assert response.status_code == 200

        data = response.json()
        assert data["total_results"] >= 1
        assert len(data["beliefs"]) >= 1

    def test_search_limit(self, client, demo_web):
        """Test search limit parameter."""
        response = client.get("/api/v1/web/search?q=e&limit=1")
        assert response.status_code == 200

        data = response.json()
        assert len(data["beliefs"]) <= 1

    def test_search_missing_query(self, client):
        """Test search requires query."""
        response = client.get("/api/v1/web/search")
        assert response.status_code == 422  # Validation error


# =============================================================================
# Stability Endpoint Tests
# =============================================================================

class TestStabilityEndpoint:
    """Tests for /api/v1/web/stability endpoint."""

    def test_stability_empty_web(self, client):
        """Test stability on empty web."""
        response = client.get("/api/v1/web/stability")
        assert response.status_code == 200

        data = response.json()
        assert "stability_level" in data
        assert data["total_beliefs"] == 0

    def test_stability_with_beliefs(self, client, demo_web):
        """Test stability with beliefs."""
        response = client.get("/api/v1/web/stability")
        assert response.status_code == 200

        data = response.json()
        assert data["total_beliefs"] == 3
        assert "recommendation" in data
        assert "publication_bias" in data

    def test_stability_counts(self, client, demo_web):
        """Test stability counts."""
        response = client.get("/api/v1/web/stability")
        data = response.json()

        assert "stable_beliefs" in data
        assert "unstable_beliefs" in data
        assert "contested_beliefs" in data
        # Total should add up
        total = data["stable_beliefs"] + data["unstable_beliefs"] + data["contested_beliefs"]
        # Note: Some beliefs may be uncategorized
        assert total <= data["total_beliefs"]


class TestShouldStopEndpoint:
    """Tests for /api/v1/web/stability/should-stop endpoint."""

    def test_should_stop_empty(self, client):
        """Test should-stop on empty web."""
        response = client.get("/api/v1/web/stability/should-stop")
        assert response.status_code == 200

        data = response.json()
        assert "should_stop" in data
        assert "reason" in data
        assert "current_stability" in data

    def test_should_stop_with_beliefs(self, client, demo_web):
        """Test should-stop with beliefs."""
        response = client.get("/api/v1/web/stability/should-stop")
        data = response.json()

        assert isinstance(data["should_stop"], bool)
        assert len(data["reason"]) > 0


# =============================================================================
# Top Beliefs Endpoint Tests
# =============================================================================

class TestTopBeliefsEndpoint:
    """Tests for /api/v1/web/top-beliefs endpoint."""

    def test_top_beliefs_empty(self, client):
        """Test top beliefs on empty web."""
        response = client.get("/api/v1/web/top-beliefs")
        assert response.status_code == 200

        data = response.json()
        assert data["count"] == 0
        assert data["beliefs"] == []

    def test_top_beliefs_sorted(self, client, demo_web):
        """Test top beliefs are sorted by credence."""
        response = client.get("/api/v1/web/top-beliefs")
        data = response.json()

        beliefs = data["beliefs"]
        credences = [b["credence"] for b in beliefs]
        assert credences == sorted(credences, reverse=True)

    def test_top_beliefs_limit(self, client, demo_web):
        """Test top beliefs limit."""
        response = client.get("/api/v1/web/top-beliefs?limit=2")
        data = response.json()

        assert data["count"] <= 2


# =============================================================================
# Categories Endpoint Tests
# =============================================================================

class TestCategoriesEndpoint:
    """Tests for /api/v1/web/categories endpoint."""

    def test_categories_empty(self, client):
        """Test categories on empty web."""
        response = client.get("/api/v1/web/categories")
        assert response.status_code == 200

        data = response.json()
        assert data["categories"] == []

    def test_categories_with_beliefs(self, client, demo_web):
        """Test categories with beliefs."""
        response = client.get("/api/v1/web/categories")
        data = response.json()

        categories = data["categories"]
        assert len(categories) >= 1

        # Check structure
        for cat in categories:
            assert "name" in cat
            assert "count" in cat

    def test_categories_count(self, client, demo_web):
        """Test category counts are correct."""
        response = client.get("/api/v1/web/categories")
        data = response.json()

        # productivity should have 2 beliefs
        productivity = next((c for c in data["categories"] if c["name"] == "productivity"), None)
        assert productivity is not None
        assert productivity["count"] == 2


# =============================================================================
# Admin Endpoint Tests
# =============================================================================

class TestAdminEndpoints:
    """Tests for admin endpoints."""

    def test_load_demo_requires_admin_token(self, client, monkeypatch):
        """Admin demo loader must reject unauthenticated requests."""
        monkeypatch.setenv("AE_ADMIN_TOKEN", "test-token")
        response = client.post("/api/v1/web/admin/load-demo")
        assert response.status_code == 401

    def test_load_demo(self, client, monkeypatch):
        """Test loading demo data."""
        monkeypatch.setenv("AE_ADMIN_TOKEN", "test-token")
        response = client.post(
            "/api/v1/web/admin/load-demo",
            headers={"X-Admin-Token": "test-token"},
        )
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "success"
        assert data["beliefs_loaded"] > 0

        # Verify data loaded
        response = client.get("/api/v1/web/top-beliefs")
        data = response.json()
        assert data["count"] > 0

    def test_clear_web(self, client, demo_web, monkeypatch):
        """Test clearing web."""
        monkeypatch.setenv("AE_ADMIN_TOKEN", "test-token")
        # Verify we have data
        response = client.get("/api/v1/web/top-beliefs")
        assert response.json()["count"] > 0

        # Clear
        response = client.delete(
            "/api/v1/web/admin/clear",
            headers={"X-Admin-Token": "test-token"},
        )
        assert response.status_code == 200

        # Verify cleared
        response = client.get("/api/v1/web/top-beliefs")
        assert response.json()["count"] == 0


# =============================================================================
# Edge Cases & Error Handling
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_invalid_max_nodes(self, client):
        """Test invalid max_nodes parameter."""
        response = client.get("/api/v1/web/graph?max_nodes=0")
        assert response.status_code == 422

    def test_invalid_min_credence(self, client):
        """Test invalid min_credence parameter."""
        response = client.get("/api/v1/web/graph?min_credence=2.0")
        assert response.status_code == 422

    def test_empty_search_query(self, client):
        """Test empty search query."""
        response = client.get("/api/v1/web/search?q=")
        assert response.status_code == 422


# =============================================================================
# Integration Tests
# =============================================================================

class TestIntegration:
    """Integration tests for full workflow."""

    def test_load_explore_detail_workflow(self, client, monkeypatch):
        """Test typical user workflow: load demo → explore → get detail."""
        monkeypatch.setenv("AE_ADMIN_TOKEN", "test-token")
        # Load demo
        response = client.post(
            "/api/v1/web/admin/load-demo",
            headers={"X-Admin-Token": "test-token"},
        )
        assert response.status_code == 200

        # Get graph
        response = client.get("/api/v1/web/graph")
        nodes = response.json()["nodes"]
        assert len(nodes) > 0

        # Get detail for first node
        first_node_id = nodes[0]["id"]
        response = client.get(f"/api/v1/web/node/{first_node_id}")
        assert response.status_code == 200
        assert response.json()["belief_id"] == first_node_id

    def test_search_and_detail_workflow(self, client, monkeypatch):
        """Test search → detail workflow."""
        monkeypatch.setenv("AE_ADMIN_TOKEN", "test-token")
        # Load demo
        client.post(
            "/api/v1/web/admin/load-demo",
            headers={"X-Admin-Token": "test-token"},
        )

        # Search
        response = client.get("/api/v1/web/search?q=daylight")
        beliefs = response.json()["beliefs"]

        if beliefs:
            # Get detail for found belief (SearchResult uses 'id' not 'belief_id')
            belief_id = beliefs[0]["id"]
            response = client.get(f"/api/v1/web/node/{belief_id}")
            assert response.status_code == 200
