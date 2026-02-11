"""
Tests for Cross-Layer Query Service (INT-5)
2026-02-11
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from src.services.cross_layer_query import (
    CrossLayerQueryService,
    QueryType,
    BeliefSummary,
    ConstraintSummary,
    LayerConnection,
    CrossLayerQueryResult,
    TheorySupportResult,
    get_cross_layer_service
)


class MockCredence:
    """Mock credence with value and uncertainty."""
    def __init__(self, value=0.7, uncertainty=0.2):
        self.value = value
        self.uncertainty = uncertainty


class MockLevel:
    """Mock epistemic level enum."""
    def __init__(self, value):
        self.value = value


class MockConstraintType:
    """Mock constraint type enum."""
    def __init__(self, value):
        self.value = value


class MockBelief:
    """Mock belief for testing."""
    def __init__(
        self,
        belief_id: str,
        content: str = "Test belief content",
        level: str = "empirical",
        credence: float = 0.7,
        uncertainty: float = 0.2,
        environment_id: str = None,
        outcome_id: str = None
    ):
        self.belief_id = belief_id
        self.content = content
        self.level = MockLevel(level)
        self.credence = MockCredence(credence, uncertainty)
        self.environment_id = environment_id
        self.outcome_id = outcome_id
        self.tags = []


class MockConstraint:
    """Mock constraint for testing."""
    def __init__(
        self,
        constraint_id: str,
        source_id: str,
        target_id: str,
        constraint_type: str = "supports",
        strength: float = 0.8
    ):
        self.constraint_id = constraint_id
        self.source_id = source_id
        self.target_id = target_id
        self.constraint_type = MockConstraintType(constraint_type)
        self.strength = strength


class MockWebOfBelief:
    """Mock Web of Belief for testing."""
    def __init__(self):
        # Create some test beliefs across layers
        self.beliefs = {
            "theory_art": MockBelief(
                "theory_art",
                "Attention Restoration Theory",
                "theoretical",
                0.85
            ),
            "theory_srt": MockBelief(
                "theory_srt",
                "Stress Recovery Theory",
                "theoretical",
                0.80
            ),
            "inter_cognitive_load": MockBelief(
                "inter_cognitive_load",
                "High complexity increases cognitive load",
                "intermediate",
                0.75,
                environment_id="complexity",
                outcome_id="cognitive_load"
            ),
            "emp_plants_stress": MockBelief(
                "emp_plants_stress",
                "Plants reduce stress in offices",
                "empirical",
                0.70,
                environment_id="plants",
                outcome_id="stress"
            ),
            "emp_daylight_mood": MockBelief(
                "emp_daylight_mood",
                "Daylight improves mood",
                "empirical",
                0.72,
                environment_id="daylight",
                outcome_id="mood"
            ),
            "obs_window_view": MockBelief(
                "obs_window_view",
                "Window view noted in study X",
                "observational",
                0.65,
                environment_id="window",
                outcome_id="preference"
            ),
        }

        # Create constraints
        self.constraints = {
            "c1": MockConstraint("c1", "theory_art", "inter_cognitive_load", "explains"),
            "c2": MockConstraint("c2", "theory_srt", "emp_plants_stress", "explains"),
            "c3": MockConstraint("c3", "emp_plants_stress", "obs_window_view", "supports"),
            "c4": MockConstraint("c4", "inter_cognitive_load", "emp_daylight_mood", "supports"),
            "c5": MockConstraint("c5", "theory_art", "theory_srt", "contradicts"),  # Cross-layer conflict
        }

        # Build constraint index
        self._constraints_by_belief = {}
        for constraint_id, constraint in self.constraints.items():
            for belief_id in [constraint.source_id, constraint.target_id]:
                if belief_id not in self._constraints_by_belief:
                    self._constraints_by_belief[belief_id] = []
                self._constraints_by_belief[belief_id].append(constraint_id)


@pytest.fixture
def mock_web():
    """Create a mock Web of Belief."""
    return MockWebOfBelief()


@pytest.fixture
def service(mock_web):
    """Create a CrossLayerQueryService with mock web."""
    return CrossLayerQueryService(web=mock_web)


class TestCrossLayerQueryService:
    """Tests for CrossLayerQueryService."""

    def test_find_theory_support(self, service):
        """Test finding empirical support for a theory."""
        result = service.find_theory_support("theory_art")

        assert result is not None
        assert result.theory_belief.belief_id == "theory_art"
        assert result.theory_belief.level == "theoretical"
        assert len(result.supporting_beliefs) > 0
        assert result.support_strength >= 0.0 and result.support_strength <= 1.0

    def test_find_theory_support_not_found(self, service):
        """Test finding support for non-existent theory."""
        result = service.find_theory_support("nonexistent")
        assert result is None

    def test_find_empirical_grounding(self, service):
        """Test finding theoretical grounding for empirical belief."""
        result = service.find_empirical_grounding("emp_plants_stress")

        assert result is not None
        assert result.query_type == QueryType.EMPIRICAL_GROUNDING.value
        assert len(result.beliefs) >= 1  # At least the empirical belief itself

    def test_find_environment_outcome_beliefs(self, service):
        """Test finding beliefs by environment and outcome."""
        result = service.find_environment_outcome_beliefs(
            environment_id="plants",
            outcome_id="stress"
        )

        assert result is not None
        assert result.query_type == QueryType.ENVIRONMENT_OUTCOME.value
        assert len(result.beliefs) >= 1
        # Should find the plants->stress belief
        belief_ids = [b.belief_id for b in result.beliefs]
        assert "emp_plants_stress" in belief_ids

    def test_find_environment_outcome_no_filter(self, service):
        """Test finding all beliefs without filter."""
        result = service.find_environment_outcome_beliefs()

        assert result is not None
        # Should return beliefs (those with env/outcome set)
        assert len(result.beliefs) >= 3

    def test_find_cross_layer_conflicts(self, service):
        """Test finding cross-layer conflicts."""
        result = service.find_cross_layer_conflicts()

        assert result is not None
        assert result.query_type == QueryType.LAYER_CONFLICTS.value
        # Our mock has a contradicts constraint between two theoretical beliefs
        # which are at the same layer, so won't show as cross-layer conflict

    def test_get_belief_chain(self, service):
        """Test getting belief chain."""
        result = service.get_belief_chain("theory_art", max_depth=3)

        assert result is not None
        assert result.query_type == QueryType.BELIEF_CHAIN.value
        assert len(result.beliefs) >= 1
        # Should find connected beliefs
        belief_ids = [b.belief_id for b in result.beliefs]
        assert "theory_art" in belief_ids

    def test_get_belief_chain_not_found(self, service):
        """Test getting chain for non-existent belief."""
        result = service.get_belief_chain("nonexistent")

        assert result is not None
        assert len(result.beliefs) == 0

    def test_get_layer_statistics(self, service):
        """Test getting layer statistics."""
        stats = service.get_layer_statistics()

        assert "total_beliefs" in stats
        assert "total_constraints" in stats
        assert "by_level" in stats
        assert "cross_layer_connections" in stats
        assert "within_layer_connections" in stats
        assert "constraint_types" in stats

        assert stats["total_beliefs"] == 6
        assert stats["total_constraints"] == 5

    def test_level_distance_calculation(self, service):
        """Test level distance calculation."""
        assert service._get_level_distance("theoretical", "theoretical") == 0
        assert service._get_level_distance("theoretical", "empirical") == 2
        assert service._get_level_distance("empirical", "observational") == 1
        assert service._get_level_distance("theoretical", "observational") == 3

    def test_belief_to_summary(self, service, mock_web):
        """Test converting belief to summary."""
        belief = mock_web.beliefs["emp_plants_stress"]
        summary = service._belief_to_summary(belief)

        assert summary.belief_id == "emp_plants_stress"
        assert summary.level == "empirical"
        assert summary.credence == 0.7
        assert summary.environment_id == "plants"
        assert summary.outcome_id == "stress"

    def test_constraint_to_summary(self, service, mock_web):
        """Test converting constraint to summary."""
        constraint = mock_web.constraints["c1"]
        summary = service._constraint_to_summary(constraint)

        assert summary.constraint_id == "c1"
        assert summary.source_id == "theory_art"
        assert summary.target_id == "inter_cognitive_load"
        assert summary.constraint_type == "explains"
        assert summary.strength == 0.8


class TestQueryResults:
    """Tests for query result classes."""

    def test_cross_layer_query_result_to_dict(self):
        """Test CrossLayerQueryResult serialization."""
        result = CrossLayerQueryResult(
            query_type="test",
            query_params={"key": "value"},
            beliefs=[
                BeliefSummary(
                    belief_id="b1",
                    content="Test content",
                    level="empirical",
                    credence=0.7,
                    uncertainty=0.2
                )
            ],
            connections=[],
            layer_summary={"empirical": 1},
            generated_at="2026-02-11T00:00:00"
        )

        d = result.to_dict()
        assert d["query_type"] == "test"
        assert d["n_beliefs"] == 1
        assert d["n_connections"] == 0
        assert d["beliefs"][0]["belief_id"] == "b1"

    def test_theory_support_result_to_dict(self):
        """Test TheorySupportResult serialization."""
        result = TheorySupportResult(
            theory_belief=BeliefSummary(
                belief_id="theory",
                content="Theory content",
                level="theoretical",
                credence=0.8,
                uncertainty=0.1
            ),
            supporting_beliefs=[
                BeliefSummary(
                    belief_id="emp1",
                    content="Empirical content",
                    level="empirical",
                    credence=0.7,
                    uncertainty=0.2
                )
            ],
            support_strength=0.7,
            coverage_score=0.4,
            gaps=["Limited data"]
        )

        d = result.to_dict()
        assert d["theory"]["belief_id"] == "theory"
        assert d["n_supporting"] == 1
        assert d["support_strength"] == 0.7
        assert d["coverage_score"] == 0.4
        assert "Limited data" in d["gaps"]


class TestServiceInitialization:
    """Tests for service initialization."""

    def test_lazy_load_web(self):
        """Test that web is lazy-loaded from accumulator."""
        mock_accumulator = Mock()
        mock_web = MockWebOfBelief()
        mock_accumulator.get_master_web.return_value = (mock_web, None)

        service = CrossLayerQueryService(accumulator=mock_accumulator)

        # Access web property
        web = service.web

        assert web is mock_web
        mock_accumulator.get_master_web.assert_called_once()

    def test_singleton_accessor(self):
        """Test get_cross_layer_service returns same instance."""
        # Reset singleton
        import src.services.cross_layer_query as module
        module._query_service = None

        with patch.object(module.CrossLayerQueryService, '__init__', return_value=None):
            service1 = get_cross_layer_service()
            service2 = get_cross_layer_service()

            assert service1 is service2
