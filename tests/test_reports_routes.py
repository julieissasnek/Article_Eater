"""
Tests for Reports API Routes
============================

Tests for stopping rules and reporting endpoints.

Date: January 21, 2026
Phase D Sprint D1-D2
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI

from app.routes.reports import router, get_web, set_web
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

    for i in range(10):
        belief = Belief(
            belief_id=f"b{i}",
            content=f"Finding {i} about natural light and productivity",
            level=EpistemicLevel.EMPIRICAL if i % 2 == 0 else EpistemicLevel.THEORETICAL,
            credence=Credence(0.6 + (i * 0.03), 0.12),
            outcome_id="productivity" if i < 5 else "cognition",
            source_depth=SourceDepth.FULL_TEXT if i % 3 == 0 else SourceDepth.ABSTRACT,
            contested=i == 5
        )
        web.beliefs[belief.belief_id] = belief

    set_web(web)
    return web


# =============================================================================
# Stopping Endpoint Tests
# =============================================================================

class TestStoppingEndpoints:
    """Tests for stopping evaluation endpoints."""

    def test_evaluate_stopping_empty(self, client, clean_state):
        """Test stopping evaluation with empty web."""
        response = client.post("/api/reports/stopping/evaluate", json={})

        assert response.status_code == 200
        data = response.json()
        assert data["should_stop"] is False

    def test_evaluate_stopping_populated(self, client, populated_web):
        """Test stopping evaluation with data."""
        response = client.post("/api/reports/stopping/evaluate", json={
            "min_beliefs": 5,
            "confidence_threshold": 0.6
        })

        assert response.status_code == 200
        data = response.json()
        assert "should_stop" in data
        assert "recommendation" in data
        assert "criteria_met" in data
        assert "criteria_not_met" in data

    def test_evaluate_stopping_with_topic(self, client, populated_web):
        """Test stopping evaluation for specific topic."""
        response = client.post("/api/reports/stopping/evaluate", json={
            "topic": "light"
        })

        assert response.status_code == 200

    def test_evaluate_stopping_custom_params(self, client, populated_web):
        """Test stopping evaluation with custom parameters."""
        response = client.post("/api/reports/stopping/evaluate", json={
            "min_beliefs": 15,
            "confidence_threshold": 0.9
        })

        data = response.json()
        # With high thresholds, probably won't recommend stopping
        assert data["should_stop"] is False or data["confidence"] < 0.8

    def test_get_stopping_reasons(self, client, clean_state):
        """Test getting stopping reasons."""
        response = client.get("/api/reports/stopping/reasons")

        assert response.status_code == 200
        data = response.json()
        assert "saturation" in data
        assert "confidence" in data
        assert "count" in data


# =============================================================================
# Report Generation Tests
# =============================================================================

class TestReportGeneration:
    """Tests for report generation endpoints."""

    def test_generate_executive_summary(self, client, populated_web):
        """Test generating executive summary."""
        response = client.post("/api/reports/generate", json={
            "report_type": "executive"
        })

        assert response.status_code == 200
        data = response.json()
        assert data["report_type"] == "executive"
        assert "title" in data
        assert "summary" in data
        assert "sections" in data

    def test_generate_evidence_inventory(self, client, populated_web):
        """Test generating evidence inventory."""
        response = client.post("/api/reports/generate", json={
            "report_type": "inventory"
        })

        assert response.status_code == 200
        data = response.json()
        assert data["report_type"] == "inventory"

    def test_generate_confidence_analysis(self, client, populated_web):
        """Test generating confidence analysis."""
        response = client.post("/api/reports/generate", json={
            "report_type": "confidence"
        })

        assert response.status_code == 200
        data = response.json()
        assert data["report_type"] == "confidence"

    def test_generate_gap_analysis(self, client, populated_web):
        """Test generating gap analysis."""
        response = client.post("/api/reports/generate", json={
            "report_type": "gaps"
        })

        assert response.status_code == 200
        data = response.json()
        assert data["report_type"] == "gaps"

    def test_generate_quality_assessment(self, client, populated_web):
        """Test generating quality assessment."""
        response = client.post("/api/reports/generate", json={
            "report_type": "quality"
        })

        assert response.status_code == 200
        data = response.json()
        assert data["report_type"] == "quality"

    def test_generate_topic_deep_dive(self, client, populated_web):
        """Test generating topic deep dive."""
        response = client.post("/api/reports/generate", json={
            "report_type": "topic",
            "topic": "productivity"
        })

        assert response.status_code == 200
        data = response.json()
        assert data["report_type"] == "topic"
        assert "productivity" in data["title"].lower()

    def test_generate_contradiction_report(self, client, populated_web):
        """Test generating contradiction report."""
        response = client.post("/api/reports/generate", json={
            "report_type": "contradictions"
        })

        assert response.status_code == 200
        data = response.json()
        assert data["report_type"] == "contradictions"


# =============================================================================
# Report Types Endpoint Tests
# =============================================================================

class TestReportTypesEndpoint:
    """Tests for report types endpoint."""

    def test_get_report_types(self, client, clean_state):
        """Test getting report types."""
        response = client.get("/api/reports/types")

        assert response.status_code == 200
        data = response.json()

        expected_types = ["executive", "inventory", "confidence", "gaps", "quality", "topic", "contradictions"]
        for report_type in expected_types:
            assert report_type in data


# =============================================================================
# Quick Summary Tests
# =============================================================================

class TestQuickSummary:
    """Tests for quick summary endpoint."""

    def test_summary_empty(self, client, clean_state):
        """Test summary with empty web."""
        response = client.get("/api/reports/summary")

        assert response.status_code == 200
        data = response.json()
        assert data["total_beliefs"] == 0
        assert data["status"] == "empty"

    def test_summary_populated(self, client, populated_web):
        """Test summary with data."""
        response = client.get("/api/reports/summary")

        assert response.status_code == 200
        data = response.json()
        assert data["total_beliefs"] > 0
        assert "average_credence" in data
        assert "status" in data
        assert "message" in data


# =============================================================================
# Dashboard Tests
# =============================================================================

class TestDashboard:
    """Tests for dashboard endpoint."""

    def test_dashboard_empty(self, client, clean_state):
        """Test dashboard with empty web."""
        response = client.get("/api/reports/dashboard")

        assert response.status_code == 200
        data = response.json()
        assert "stopping" in data
        assert "metrics" in data
        assert "distribution" in data
        assert "health" in data

    def test_dashboard_populated(self, client, populated_web):
        """Test dashboard with data."""
        response = client.get("/api/reports/dashboard")

        assert response.status_code == 200
        data = response.json()

        # Check stopping section
        assert "should_stop" in data["stopping"]
        assert "recommendation" in data["stopping"]

        # Check metrics
        assert data["metrics"]["total_beliefs"] > 0
        assert 0 <= data["metrics"]["average_credence"] <= 1

        # Check distribution
        assert "by_source_depth" in data["distribution"]
        assert "by_outcome" in data["distribution"]

        # Check health indicators
        assert isinstance(data["health"]["has_minimum_evidence"], bool)


# =============================================================================
# Integration Tests
# =============================================================================

class TestReportsIntegration:
    """Integration tests for reports endpoints."""

    def test_full_reporting_workflow(self, client, populated_web):
        """Test complete reporting workflow."""
        # 1. Check dashboard
        dashboard = client.get("/api/reports/dashboard").json()
        assert dashboard["metrics"]["total_beliefs"] > 0

        # 2. Evaluate stopping
        stopping = client.post("/api/reports/stopping/evaluate", json={
            "min_beliefs": 5
        }).json()
        assert "recommendation" in stopping

        # 3. Generate executive summary
        exec_report = client.post("/api/reports/generate", json={
            "report_type": "executive"
        }).json()
        assert len(exec_report["sections"]) > 0

        # 4. If not stopping, check what's missing
        if not stopping["should_stop"]:
            gaps = client.post("/api/reports/generate", json={
                "report_type": "gaps"
            }).json()
            assert gaps["report_type"] == "gaps"

        # 5. Get quality assessment
        quality = client.post("/api/reports/generate", json={
            "report_type": "quality"
        }).json()
        assert quality["report_type"] == "quality"

    def test_report_consistency(self, client, populated_web):
        """Test reports are consistent with each other."""
        # Get summary
        summary = client.get("/api/reports/summary").json()

        # Get executive report
        exec_report = client.post("/api/reports/generate", json={
            "report_type": "executive"
        }).json()

        # Both should have same total
        assert summary["total_beliefs"] == exec_report["metadata"]["belief_count"]

    def test_all_report_types_work(self, client, populated_web):
        """Test all report types can be generated."""
        types_response = client.get("/api/reports/types").json()

        for report_type in types_response.keys():
            response = client.post("/api/reports/generate", json={
                "report_type": report_type
            })
            assert response.status_code == 200, f"Failed for {report_type}"
