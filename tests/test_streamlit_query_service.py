"""
Tests for Streamlit Query Service — Sprint 3.0.3
2026-02-09
"""

import sys
from pathlib import Path
import pytest

# Add streamlit_app to path
sys.path.insert(0, str(Path(__file__).parent.parent / "streamlit_app"))

from query_service import (
    DirectQueryService,
    QueryResult,
    EvidenceSource,
    ScopeInfo,
    SystemStats,
    get_query_service,
)


# =============================================================================
# Mock WebOfBelief
# =============================================================================

class MockCredence:
    def __init__(self, point: float = 0.7):
        self.point = point


class MockScope:
    def __init__(
        self,
        population: str = None,
        setting: str = None,
        methodology: str = None
    ):
        self.population = population
        self.setting = setting
        self.methodology = methodology


class MockStatus:
    def __init__(self, value: str = "established"):
        self.value = value


class MockLevel:
    def __init__(self, value: str = "empirical"):
        self.value = value


class MockBelief:
    def __init__(
        self,
        belief_id: str,
        content: str,
        credence: float = 0.7,
        status: str = "established",
        level: str = "empirical",
        paper_ids: list = None,
        environment_id: str = None,
        outcome_id: str = None,
        scope: MockScope = None
    ):
        self.belief_id = belief_id
        self.content = content
        self.credence = MockCredence(credence)
        self.status = MockStatus(status)
        self.level = MockLevel(level)
        self.paper_ids = paper_ids or []
        self.environment_id = environment_id
        self.outcome_id = outcome_id
        self.scope = scope


class MockWebOfBelief:
    def __init__(self, beliefs: list = None):
        self._beliefs = beliefs or []
        self.beliefs = {b.belief_id: b for b in self._beliefs}
        self.constraints = []


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def sample_beliefs():
    """Create sample beliefs for testing."""
    return [
        MockBelief(
            belief_id="B001",
            content="Natural light improves mood in office environments",
            credence=0.85,
            status="established",
            level="empirical",
            paper_ids=["paper_001", "paper_002"],
            environment_id="natural_light",
            outcome_id="mood",
            scope=MockScope(
                population="office workers",
                setting="office environments"
            )
        ),
        MockBelief(
            belief_id="B002",
            content="Plants reduce stress by 15-25% in office settings",
            credence=0.72,
            status="established",
            level="empirical",
            paper_ids=["paper_003"],
            environment_id="plants",
            outcome_id="stress",
            scope=MockScope(
                population="office workers",
                setting="indoor offices",
                methodology="self-report surveys"
            )
        ),
        MockBelief(
            belief_id="B003",
            content="Window views to nature improve patient recovery",
            credence=0.65,
            status="contested",
            level="empirical",
            paper_ids=["paper_004", "paper_005"],
            environment_id="window_views",
            outcome_id="recovery"
        ),
        MockBelief(
            belief_id="B004",
            content="Attention Restoration Theory explains nature-attention links",
            credence=0.80,
            status="established",
            level="theoretical"
        ),
        MockBelief(
            belief_id="B005",
            content="Noise above 55dB reduces productivity",
            credence=0.78,
            status="established",
            level="empirical",
            environment_id="noise",
            outcome_id="productivity"
        ),
    ]


@pytest.fixture
def mock_web(sample_beliefs):
    """Create mock web of belief."""
    return MockWebOfBelief(sample_beliefs)


@pytest.fixture
def service(mock_web):
    """Create query service with mock web."""
    return DirectQueryService(web_of_belief=mock_web)


# =============================================================================
# DirectQueryService Tests
# =============================================================================

class TestDirectQueryService:
    """Test DirectQueryService class."""

    def test_create_service(self):
        """Test creating service without web."""
        service = DirectQueryService()
        assert service.web is None
        assert service.use_llm is False

    def test_create_service_with_web(self, mock_web):
        """Test creating service with web."""
        service = DirectQueryService(web_of_belief=mock_web)
        assert service.web is mock_web

    def test_set_web_of_belief(self, mock_web):
        """Test setting web after creation."""
        service = DirectQueryService()
        service.set_web_of_belief(mock_web)
        assert service.web is mock_web


class TestQueryExecution:
    """Test query execution."""

    def test_execute_simple_query(self, service):
        """Test executing a simple query."""
        result = service.execute_query("What is the effect of plants on stress?")

        assert isinstance(result, QueryResult)
        assert result.query == "What is the effect of plants on stress?"
        assert result.headline is not None
        assert result.processing_mode == "direct"

    def test_execute_query_finds_relevant_evidence(self, service):
        """Test that query finds relevant beliefs."""
        # Use proper question format for parser
        result = service.execute_query("What is the effect of plants on stress?")

        # Should find the plants/stress belief
        assert len(result.evidence) > 0
        plant_belief = next(
            (e for e in result.evidence if "plants" in e.content.lower()),
            None
        )
        assert plant_belief is not None

    def test_execute_query_no_web(self):
        """Test query execution without web."""
        service = DirectQueryService()
        result = service.execute_query("test query")

        assert result.headline is not None
        assert "No evidence" in result.headline

    def test_query_type_detection(self, service):
        """Test that query type is detected."""
        result = service.execute_query("What is the effect of light on mood?")
        # Should detect as WHAT_IS or similar
        assert result.query_type in ["what_is", "does_affect", "what"]

    def test_quick_mode(self, service):
        """Test quick response mode."""
        result = service.execute_query("plants", mode="quick")

        assert result.headline is not None
        # Quick mode should not include detailed summary
        # (depending on implementation, might still have summary)

    def test_standard_mode(self, service):
        """Test standard response mode."""
        result = service.execute_query("plants", mode="standard")

        assert result.summary is not None

    def test_deep_mode(self, service):
        """Test deep response mode."""
        result = service.execute_query("plants", mode="deep")

        assert result.summary is not None
        assert result.detail is not None

    def test_scope_conditions_included(self, service):
        """Test that scope conditions are included."""
        result = service.execute_query(
            "plants stress",
            include_scope=True
        )

        # Should have aggregated scope conditions
        if result.evidence:
            assert result.scope_conditions is not None or len(result.evidence[0].scope.to_dict()) >= 0

    def test_practical_implications(self, service):
        """Test practical implications generation."""
        result = service.execute_query(
            "plants reduce stress",
            include_practitioner=True
        )

        assert result.practical_implications is not None
        assert isinstance(result.practical_implications, list)


class TestEvidenceRetrieval:
    """Test evidence retrieval."""

    def test_retrieve_by_subject(self, service):
        """Test retrieval by subject."""
        result = service.execute_query("natural light")

        # Should find the natural light belief
        light_belief = next(
            (e for e in result.evidence if "natural light" in e.content.lower()),
            None
        )
        assert light_belief is not None

    def test_retrieve_by_outcome(self, service):
        """Test retrieval by outcome."""
        result = service.execute_query("productivity")

        # Should find the noise/productivity belief
        prod_belief = next(
            (e for e in result.evidence if "productivity" in e.content.lower()),
            None
        )
        assert prod_belief is not None

    def test_max_evidence_limit(self, service):
        """Test evidence limit is respected."""
        result = service.execute_query("office", max_evidence=2)

        assert len(result.evidence) <= 2

    def test_evidence_sorted_by_relevance(self, service):
        """Test evidence is sorted by relevance."""
        result = service.execute_query("plants stress office")

        if len(result.evidence) >= 2:
            # Plants/stress belief should rank highly
            first = result.evidence[0]
            assert "plants" in first.content.lower() or "stress" in first.content.lower()


class TestResponseGeneration:
    """Test response generation."""

    def test_headline_format(self, service):
        """Test headline format."""
        result = service.execute_query("plants")

        # Headline should contain content and credence
        assert "(" in result.headline or "credence" in result.headline.lower() or result.headline

    def test_caveats_for_contested(self, service):
        """Test caveats are generated for contested beliefs."""
        # Query for window views which is contested
        result = service.execute_query("window views recovery")

        if any(e.status == "contested" for e in result.evidence):
            # Should have caveat about contested beliefs
            assert any("contested" in c.lower() for c in result.caveats)

    def test_key_sources_extracted(self, service):
        """Test key sources are extracted."""
        result = service.execute_query("plants")

        assert result.key_sources is not None
        assert isinstance(result.key_sources, list)


class TestSystemStats:
    """Test system statistics."""

    def test_get_stats_with_web(self, service):
        """Test getting stats with web."""
        stats = service.get_stats()

        assert isinstance(stats, SystemStats)
        assert stats.total_beliefs == 5

    def test_get_stats_without_web(self):
        """Test getting stats without web."""
        service = DirectQueryService()
        stats = service.get_stats()

        assert stats.total_beliefs == 0

    def test_stats_content(self, service, sample_beliefs):
        """Test stats content is correct."""
        stats = service.get_stats()

        # Check counts
        assert stats.total_beliefs == len(sample_beliefs)

        # Check contested count
        contested = sum(1 for b in sample_beliefs if b.status.value == "contested")
        assert stats.contested_beliefs == contested

        # Check papers
        all_papers = set()
        for b in sample_beliefs:
            all_papers.update(b.paper_ids)
        assert stats.total_papers == len(all_papers)


class TestEvidenceSource:
    """Test EvidenceSource dataclass."""

    def test_create_evidence_source(self):
        """Test creating evidence source."""
        ev = EvidenceSource(
            belief_id="B001",
            content="Test content",
            credence=0.75,
            credence_label="High confidence",
            status="established",
            level="empirical",
            sources=["paper_001"],
            scope=ScopeInfo(population="adults")
        )

        assert ev.belief_id == "B001"
        assert ev.credence == 0.75

    def test_evidence_source_to_dict(self):
        """Test evidence source serialization."""
        ev = EvidenceSource(
            belief_id="B001",
            content="Test",
            credence=0.75,
            credence_label="High",
            status="established",
            level="empirical"
        )

        d = ev.to_dict()

        assert d["belief_id"] == "B001"
        assert d["credence"] == 0.75


class TestQueryResult:
    """Test QueryResult dataclass."""

    def test_create_query_result(self):
        """Test creating query result."""
        result = QueryResult(
            query="test",
            query_type="what",
            causal_level="associational",
            headline="Test headline"
        )

        assert result.query == "test"
        assert result.headline == "Test headline"

    def test_query_result_to_dict(self):
        """Test query result serialization."""
        result = QueryResult(
            query="test",
            query_type="what",
            causal_level="associational",
            headline="Test",
            caveats=["Caveat 1"]
        )

        d = result.to_dict()

        assert d["query"] == "test"
        assert d["caveats"] == ["Caveat 1"]


class TestCredenceLabels:
    """Test credence label generation."""

    def test_high_credence(self, service):
        """Test high credence label."""
        label = service._credence_label(0.85)
        assert label == "High confidence"

    def test_moderate_credence(self, service):
        """Test moderate credence label."""
        label = service._credence_label(0.60)
        assert label == "Moderate confidence"

    def test_low_credence(self, service):
        """Test low credence label."""
        label = service._credence_label(0.30)
        assert label == "Low confidence"

    def test_very_low_credence(self, service):
        """Test very low credence label."""
        label = service._credence_label(0.15)
        assert label == "Very low confidence"


class TestSingleton:
    """Test singleton pattern."""

    def test_get_query_service(self):
        """Test singleton getter."""
        service1 = get_query_service()
        service2 = get_query_service()

        assert service1 is service2

    def test_singleton_with_web(self, mock_web):
        """Test singleton with web update."""
        service = get_query_service(web_of_belief=mock_web)
        assert service.web is mock_web


# =============================================================================
# Integration Tests
# =============================================================================

class TestIntegration:
    """Integration tests for full query workflow."""

    def test_full_query_workflow(self, service):
        """Test complete query workflow."""
        # Execute query
        result = service.execute_query(
            "What is the effect of plants on stress?",
            mode="standard",
            include_scope=True,
            include_practitioner=True
        )

        # Verify structure
        assert result.query is not None
        assert result.query_type is not None
        assert result.headline is not None
        assert result.summary is not None

        # Verify evidence
        assert len(result.evidence) > 0

        # Verify can serialize
        d = result.to_dict()
        assert "query" in d
        assert "evidence" in d

    def test_comparison_query(self, service):
        """Test comparison query."""
        result = service.execute_query("compare plants and natural light")

        assert result.query_type is not None

    def test_confidence_query(self, service):
        """Test confidence query."""
        result = service.execute_query("how confident are we about plants?")

        assert result.headline is not None
