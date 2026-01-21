"""
Tests for Ingestion API Routes
==============================

Tests for paper and belief ingestion endpoints.

Date: January 21, 2026
Phase C Sprint C3
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI

from app.routes.ingestion import (
    router,
    get_web,
    set_web,
    _papers,
    AddPaperResponse,
    AddBeliefResponse,
    OUTCOME_CATEGORIES
)
from src.services.web_of_belief import WebOfBelief, Belief, Credence, EpistemicLevel, SourceDepth


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
    _papers.clear()
    set_web(WebOfBelief())
    yield
    _papers.clear()
    set_web(WebOfBelief())


# =============================================================================
# Paper Ingestion Tests
# =============================================================================

class TestPaperIngestion:
    """Tests for paper ingestion."""

    def test_add_paper_minimal(self, client, clean_state):
        """Test adding a paper with minimal data."""
        response = client.post("/api/ingestion/paper", json={
            "paper": {
                "paper_id": "paper_001",
                "title": "Effects of Natural Light on Productivity"
            },
            "beliefs": []
        })

        assert response.status_code == 200
        data = response.json()
        assert data["paper_id"] == "paper_001"
        assert data["beliefs_added"] == 0

    def test_add_paper_with_full_metadata(self, client, clean_state):
        """Test adding a paper with full metadata."""
        response = client.post("/api/ingestion/paper", json={
            "paper": {
                "paper_id": "paper_002",
                "title": "Biophilic Design in Office Environments",
                "authors": ["Smith, J.", "Jones, A."],
                "year": 2023,
                "doi": "10.1234/example.2023.001",
                "journal": "Journal of Environmental Psychology",
                "source_depth": "full_text",
                "abstract": "This study examines...",
                "keywords": ["biophilia", "office", "productivity"]
            },
            "beliefs": []
        })

        assert response.status_code == 200
        data = response.json()
        assert data["paper_id"] == "paper_002"

    def test_add_paper_with_beliefs(self, client, clean_state):
        """Test adding a paper with beliefs."""
        response = client.post("/api/ingestion/paper", json={
            "paper": {
                "paper_id": "paper_003",
                "title": "Light and Productivity",
                "source_depth": "full_text"
            },
            "beliefs": [
                {
                    "content": "Natural light exposure increases productivity by 15%",
                    "credence": 0.75,
                    "level": "empirical",
                    "outcome_id": "productivity",
                    "source_depth": "full_text"
                },
                {
                    "content": "Daylight reduces afternoon fatigue",
                    "credence": 0.65,
                    "level": "empirical",
                    "outcome_id": "wellbeing"
                }
            ]
        })

        assert response.status_code == 200
        data = response.json()
        assert data["beliefs_added"] == 2
        assert len(data["belief_ids"]) == 2

    def test_add_paper_with_causal_abstract_warning(self, client, clean_state):
        """Test that causal claims from abstracts generate warnings."""
        response = client.post("/api/ingestion/paper", json={
            "paper": {
                "paper_id": "paper_004",
                "title": "Light Effects",
                "source_depth": "abstract"
            },
            "beliefs": [
                {
                    "content": "Natural light causes improved mood",
                    "credence": 0.60,
                    "level": "empirical",
                    "source_depth": "abstract",
                    "is_causal": True
                }
            ]
        })

        assert response.status_code == 200
        data = response.json()
        assert len(data["warnings"]) > 0
        assert "CAUTION" in data["warnings"][0]
        assert "abstract" in data["warnings"][0].lower()


# =============================================================================
# Belief Ingestion Tests
# =============================================================================

class TestBeliefIngestion:
    """Tests for individual belief ingestion."""

    def test_add_belief_minimal(self, client, clean_state):
        """Test adding a belief with minimal data."""
        response = client.post("/api/ingestion/belief", json={
            "content": "Plants in offices reduce perceived stress"
        })

        assert response.status_code == 200
        data = response.json()
        assert "belief_id" in data
        assert data["content"] == "Plants in offices reduce perceived stress"
        assert data["credence"] == 0.5  # default

    def test_add_belief_with_full_data(self, client, clean_state):
        """Test adding a belief with all fields."""
        response = client.post("/api/ingestion/belief", json={
            "content": "Thermal comfort between 20-24C optimizes cognitive performance",
            "credence": 0.80,
            "credence_uncertainty": 0.10,
            "level": "empirical",
            "outcome_id": "cognition",
            "paper_ids": ["paper_001", "paper_002"],
            "source_depth": "full_text",
            "scope": {
                "population": "office workers",
                "setting": "climate-controlled buildings",
                "duration": "during work hours",
                "scope_specified": True
            },
            "enabling_conditions": {
                "threshold": "20-24C",
                "temporal_order": "continuous exposure"
            },
            "is_causal": False,
            "tags": ["thermal", "cognition", "office"]
        })

        assert response.status_code == 200
        data = response.json()
        assert data["credence"] == 0.80

    def test_add_belief_causal_warning(self, client, clean_state):
        """Test warning for causal claim in abstract."""
        response = client.post("/api/ingestion/belief", json={
            "content": "Noise levels affect concentration",
            "source_depth": "abstract"
        })

        assert response.status_code == 200
        data = response.json()
        # Should warn about causal language in abstract
        caution_warnings = [w for w in data["warnings"] if "CAUTION" in w]
        assert len(caution_warnings) > 0

    def test_add_belief_validation_too_short(self, client, clean_state):
        """Test validation rejects too-short content."""
        response = client.post("/api/ingestion/belief", json={
            "content": "Too short"
        })

        assert response.status_code == 422  # Validation error

    def test_add_belief_credence_bounds(self, client, clean_state):
        """Test credence validation."""
        # Too high
        response = client.post("/api/ingestion/belief", json={
            "content": "This belief has invalid credence",
            "credence": 1.5
        })
        assert response.status_code == 422

        # Too low
        response = client.post("/api/ingestion/belief", json={
            "content": "This belief has invalid credence",
            "credence": -0.1
        })
        assert response.status_code == 422


# =============================================================================
# Paper Retrieval Tests
# =============================================================================

class TestPaperRetrieval:
    """Tests for paper retrieval endpoints."""

    def test_list_papers_empty(self, client, clean_state):
        """Test listing papers when none exist."""
        response = client.get("/api/ingestion/papers")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_papers_with_data(self, client, clean_state):
        """Test listing papers after ingestion."""
        # Add a paper
        client.post("/api/ingestion/paper", json={
            "paper": {
                "paper_id": "paper_001",
                "title": "Test Paper 1"
            },
            "beliefs": []
        })
        client.post("/api/ingestion/paper", json={
            "paper": {
                "paper_id": "paper_002",
                "title": "Test Paper 2"
            },
            "beliefs": []
        })

        response = client.get("/api/ingestion/papers")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_get_paper_by_id(self, client, clean_state):
        """Test getting a specific paper."""
        # Add a paper
        client.post("/api/ingestion/paper", json={
            "paper": {
                "paper_id": "paper_001",
                "title": "Test Paper",
                "authors": ["Smith, J."]
            },
            "beliefs": []
        })

        response = client.get("/api/ingestion/paper/paper_001")
        assert response.status_code == 200
        data = response.json()
        assert data["paper_id"] == "paper_001"
        assert data["title"] == "Test Paper"

    def test_get_paper_not_found(self, client, clean_state):
        """Test 404 for non-existent paper."""
        response = client.get("/api/ingestion/paper/nonexistent")
        assert response.status_code == 404

    def test_get_paper_beliefs(self, client, clean_state):
        """Test getting beliefs for a paper."""
        # Add paper with beliefs
        client.post("/api/ingestion/paper", json={
            "paper": {
                "paper_id": "paper_001",
                "title": "Test Paper"
            },
            "beliefs": [
                {"content": "First belief from this paper"},
                {"content": "Second belief from this paper"}
            ]
        })

        response = client.get("/api/ingestion/paper/paper_001/beliefs")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 2
        assert len(data["beliefs"]) == 2


# =============================================================================
# Statistics Tests
# =============================================================================

class TestIngestionStats:
    """Tests for ingestion statistics."""

    def test_stats_empty(self, client, clean_state):
        """Test stats with no data."""
        response = client.get("/api/ingestion/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["total_papers"] == 0
        assert data["total_beliefs"] == 0

    def test_stats_with_data(self, client, clean_state):
        """Test stats after ingestion."""
        # Add papers with beliefs
        client.post("/api/ingestion/paper", json={
            "paper": {"paper_id": "p1", "title": "Paper 1"},
            "beliefs": [
                {
                    "content": "Natural light improves productivity",
                    "level": "empirical",
                    "source_depth": "full_text"
                },
                {
                    "content": "This is a theoretical claim about light",
                    "level": "theoretical",
                    "source_depth": "abstract"
                }
            ]
        })

        response = client.get("/api/ingestion/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["total_papers"] == 1
        assert data["total_beliefs"] == 2
        assert "empirical" in data["beliefs_by_level"]
        assert "theoretical" in data["beliefs_by_level"]
        assert data["causal_claims"] >= 1  # "improves" is causal

    def test_stats_abstract_only_causal(self, client, clean_state):
        """Test tracking of abstract-only causal claims."""
        # Add abstract-only causal claim
        client.post("/api/ingestion/paper", json={
            "paper": {"paper_id": "p1", "title": "Paper 1"},
            "beliefs": [
                {
                    "content": "Treatment X causes improvement in Y",
                    "source_depth": "abstract",
                    "is_causal": True
                }
            ]
        })

        response = client.get("/api/ingestion/stats")
        data = response.json()
        assert data["abstract_only_causal"] >= 1


# =============================================================================
# Outcome Categories Tests
# =============================================================================

class TestOutcomeCategories:
    """Tests for outcome category endpoint."""

    def test_get_outcome_categories(self, client, clean_state):
        """Test getting outcome categories."""
        response = client.get("/api/ingestion/outcome-categories")
        assert response.status_code == 200
        data = response.json()

        # Check expected categories
        assert "productivity" in data
        assert "cognition" in data
        assert "stress" in data
        assert "wellbeing" in data

    def test_outcome_category_descriptions(self, client, clean_state):
        """Test that categories have descriptions."""
        response = client.get("/api/ingestion/outcome-categories")
        data = response.json()

        for category, description in data.items():
            assert len(description) > 0


# =============================================================================
# Delete Tests
# =============================================================================

class TestPaperDeletion:
    """Tests for paper deletion."""

    def test_delete_paper(self, client, clean_state):
        """Test deleting a paper."""
        # Add a paper
        client.post("/api/ingestion/paper", json={
            "paper": {"paper_id": "paper_001", "title": "Test Paper"},
            "beliefs": [{"content": "A belief from this paper"}]
        })

        # Delete it
        response = client.delete("/api/ingestion/paper/paper_001")
        assert response.status_code == 200
        data = response.json()
        assert data["deleted"] == "paper_001"
        assert "Beliefs remain" in data["note"]

        # Verify paper is gone
        response = client.get("/api/ingestion/paper/paper_001")
        assert response.status_code == 404

        # But beliefs should still exist
        web = get_web()
        assert len(web.beliefs) > 0

    def test_delete_nonexistent_paper(self, client, clean_state):
        """Test deleting non-existent paper."""
        response = client.delete("/api/ingestion/paper/nonexistent")
        assert response.status_code == 404


# =============================================================================
# Scope and Enabling Conditions Tests
# =============================================================================

class TestScopeConditions:
    """Tests for scope and enabling conditions."""

    def test_belief_with_scope_conditions(self, client, clean_state):
        """Test adding belief with scope conditions."""
        response = client.post("/api/ingestion/belief", json={
            "content": "This intervention works for office workers in daytime",
            "scope": {
                "population": "office workers",
                "setting": "open plan offices",
                "duration": "8-hour workday",
                "scope_specified": True
            }
        })

        assert response.status_code == 200

        # Verify in web
        web = get_web()
        belief = list(web.beliefs.values())[0]
        assert belief.scope is not None
        assert belief.scope.population == "office workers"
        assert belief.scope.setting == "open plan offices"

    def test_belief_with_enabling_conditions(self, client, clean_state):
        """Test adding belief with enabling conditions."""
        response = client.post("/api/ingestion/belief", json={
            "content": "Effect requires minimum 30 minutes of exposure",
            "enabling_conditions": {
                "minimum_exposure": "30 minutes",
                "threshold": "100 lux minimum",
                "temporal_order": "exposure must precede task"
            }
        })

        assert response.status_code == 200

        # Verify in web
        web = get_web()
        belief = list(web.beliefs.values())[0]
        assert belief.enabling_conditions is not None
        assert belief.enabling_conditions.minimum_exposure == "30 minutes"


# =============================================================================
# Integration Tests
# =============================================================================

class TestIngestionIntegration:
    """Integration tests for ingestion workflow."""

    def test_full_ingestion_workflow(self, client, clean_state):
        """Test complete ingestion workflow."""
        # 1. Check initial state
        stats = client.get("/api/ingestion/stats").json()
        assert stats["total_papers"] == 0

        # 2. Add a paper with beliefs
        response = client.post("/api/ingestion/paper", json={
            "paper": {
                "paper_id": "study_2023_001",
                "title": "Effects of Biophilic Design on Worker Productivity",
                "authors": ["Kaplan, R.", "Ulrich, R."],
                "year": 2023,
                "journal": "Journal of Environmental Psychology",
                "source_depth": "full_text",
                "keywords": ["biophilia", "productivity", "office design"]
            },
            "beliefs": [
                {
                    "content": "Plants in offices increase productivity by 10-15%",
                    "credence": 0.72,
                    "level": "empirical",
                    "outcome_id": "productivity",
                    "source_depth": "full_text",
                    "scope": {
                        "population": "knowledge workers",
                        "setting": "office environments",
                        "scope_specified": True
                    }
                },
                {
                    "content": "Natural elements reduce self-reported stress",
                    "credence": 0.68,
                    "level": "empirical",
                    "outcome_id": "stress",
                    "source_depth": "full_text"
                }
            ]
        })

        assert response.status_code == 200
        paper_result = response.json()
        assert paper_result["beliefs_added"] == 2

        # 3. Add another belief to the same paper
        response = client.post("/api/ingestion/belief", json={
            "content": "Window views of nature improve mood ratings",
            "credence": 0.65,
            "level": "empirical",
            "outcome_id": "mood",
            "paper_ids": ["study_2023_001"],
            "source_depth": "full_text"
        })

        assert response.status_code == 200

        # 4. Check updated stats
        stats = client.get("/api/ingestion/stats").json()
        assert stats["total_papers"] == 1
        assert stats["total_beliefs"] == 3
        assert stats["beliefs_by_level"]["empirical"] == 3

        # 5. Get paper beliefs (includes all beliefs with this paper_id in their paper_ids)
        beliefs_response = client.get("/api/ingestion/paper/study_2023_001/beliefs")
        assert beliefs_response.json()["count"] == 3  # All beliefs associated with this paper

        # 6. Verify web state
        web = get_web()
        assert len(web.beliefs) == 3

    def test_multiple_papers_same_topic(self, client, clean_state):
        """Test ingesting multiple papers on same topic."""
        # Paper 1
        client.post("/api/ingestion/paper", json={
            "paper": {"paper_id": "p1", "title": "Study 1"},
            "beliefs": [
                {"content": "Light affects productivity positively", "credence": 0.70}
            ]
        })

        # Paper 2 with related finding
        client.post("/api/ingestion/paper", json={
            "paper": {"paper_id": "p2", "title": "Study 2"},
            "beliefs": [
                {"content": "Natural light improves worker output", "credence": 0.75}
            ]
        })

        # Paper 3 with contrary finding
        client.post("/api/ingestion/paper", json={
            "paper": {"paper_id": "p3", "title": "Study 3"},
            "beliefs": [
                {"content": "Light type has minimal effect on productivity", "credence": 0.55}
            ]
        })

        stats = client.get("/api/ingestion/stats").json()
        assert stats["total_papers"] == 3
        assert stats["total_beliefs"] == 3

        papers = client.get("/api/ingestion/papers").json()
        assert len(papers) == 3
