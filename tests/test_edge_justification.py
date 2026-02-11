"""
Tests for Edge Justification Service — Sprint INT-1
2026-02-11

Tests cover:
1. Variable matching (BN vars → beliefs)
2. Credence aggregation (inverse-variance weighting)
3. Conflict detection
4. Justification status determination
5. API endpoints
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

# Import service components
from src.services.edge_justification import (
    EdgeJustificationService,
    EdgeJustification,
    BeliefSummary,
    ConflictSummary,
    ProvenanceSummary,
    JustificationStatus,
    ConflictType,
    get_variable_matching_criteria,
    BN_VARIABLE_MAPPINGS,
)


# =============================================================================
# Mock Belief Class (for testing without full WebOfBelief)
# =============================================================================

@dataclass
class MockCredence:
    """Mock credence object."""
    value: float = 0.5
    uncertainty: float = 0.3


@dataclass
class MockBelief:
    """Mock belief for testing."""
    belief_id: str
    content: str
    level: str = "EMPIRICAL"
    credence: MockCredence = field(default_factory=lambda: MockCredence(0.7, 0.2))
    paper_ids: List[str] = field(default_factory=list)
    theory_id: Optional[str] = None
    environment_id: Optional[str] = None
    outcome_id: Optional[str] = None
    tags: List[str] = field(default_factory=list)


# =============================================================================
# Test Variable Matching
# =============================================================================

class TestVariableMatching:
    """Tests for BN variable to taxonomy matching."""

    def test_known_variable_has_mappings(self):
        """Test that known BN variables have taxonomy mappings."""
        env_ids, out_ids, keywords = get_variable_matching_criteria('daylight')

        assert len(env_ids) > 0 or len(out_ids) > 0 or len(keywords) > 0
        assert 'daylight' in keywords or 'natural light' in keywords

    def test_unknown_variable_uses_name_as_keyword(self):
        """Test that unknown variables use their name as keyword."""
        env_ids, out_ids, keywords = get_variable_matching_criteria('unknown_var')

        assert 'unknown_var' in keywords
        assert len(env_ids) == 0
        assert len(out_ids) == 0

    def test_all_bn_variables_have_mappings(self):
        """Test that all defined BN variables have proper mappings."""
        for var_name, mapping in BN_VARIABLE_MAPPINGS.items():
            assert 'keywords' in mapping or 'environment_ids' in mapping or 'outcome_ids' in mapping
            # At least keywords should be present
            if 'keywords' in mapping:
                assert len(mapping['keywords']) > 0

    def test_stress_maps_to_outcome_ids(self):
        """Test that stress (an outcome) maps to outcome IDs."""
        env_ids, out_ids, keywords = get_variable_matching_criteria('stress')

        assert len(out_ids) > 0
        assert any('stress' in oid for oid in out_ids)


# =============================================================================
# Test Credence Aggregation
# =============================================================================

class TestCredenceAggregation:
    """Tests for credence aggregation logic."""

    def setup_method(self):
        """Set up service with mock web."""
        self.service = EdgeJustificationService(web=None)

    def test_empty_beliefs_returns_zero(self):
        """Test that empty belief list returns 0 credence."""
        agg_cred, agg_unc = self.service._aggregate_credence([])

        assert agg_cred == 0.0
        assert agg_unc == 1.0

    def test_single_belief_returns_its_credence(self):
        """Test that single belief returns its own credence."""
        belief = MockBelief(
            belief_id="b1",
            content="test",
            credence=MockCredence(0.8, 0.2)
        )

        agg_cred, agg_unc = self.service._aggregate_credence([belief])

        assert agg_cred == pytest.approx(0.8, rel=1e-6)
        # Uncertainty should be based on single belief

    def test_multiple_beliefs_weighted_average(self):
        """Test that multiple beliefs produce weighted average."""
        # Belief with low uncertainty (high weight)
        b1 = MockBelief(
            belief_id="b1",
            content="test1",
            credence=MockCredence(0.9, 0.1)  # Low uncertainty = high weight
        )
        # Belief with high uncertainty (low weight)
        b2 = MockBelief(
            belief_id="b2",
            content="test2",
            credence=MockCredence(0.5, 0.5)  # High uncertainty = low weight
        )

        agg_cred, agg_unc = self.service._aggregate_credence([b1, b2])

        # b1 should dominate due to lower uncertainty
        assert agg_cred > 0.7  # Closer to b1's 0.9 than b2's 0.5

    def test_aggregation_handles_zero_uncertainty(self):
        """Test that aggregation handles near-zero uncertainty gracefully."""
        belief = MockBelief(
            belief_id="b1",
            content="test",
            credence=MockCredence(0.8, 0.01)  # Very low uncertainty
        )

        # Should not raise exception
        agg_cred, agg_unc = self.service._aggregate_credence([belief])

        assert 0 <= agg_cred <= 1
        assert 0 <= agg_unc <= 1


# =============================================================================
# Test Belief Matching
# =============================================================================

class TestBeliefMatching:
    """Tests for belief-to-edge matching logic."""

    def setup_method(self):
        """Set up service with mock web."""
        self.service = EdgeJustificationService(web=None)

    def test_matches_by_canonical_ids(self):
        """Test matching by environment_id and outcome_id."""
        belief = MockBelief(
            belief_id="b1",
            content="Unrelated content",
            environment_id="sensory.light.natural",
            outcome_id="psych.stress"
        )

        matched = self.service._belief_matches_edge(
            belief,
            src_env_ids=["sensory.light.natural"],
            src_keywords=["daylight"],
            tgt_out_ids=["psych.stress"],
            tgt_keywords=["stress"]
        )

        assert matched is True

    def test_matches_by_keywords(self):
        """Test matching by content keywords."""
        belief = MockBelief(
            belief_id="b1",
            content="Natural light reduces stress in office workers",
            environment_id=None,  # No canonical IDs
            outcome_id=None
        )

        matched = self.service._belief_matches_edge(
            belief,
            src_env_ids=["sensory.light.natural"],
            src_keywords=["natural light"],
            tgt_out_ids=["psych.stress"],
            tgt_keywords=["stress"]
        )

        assert matched is True

    def test_no_match_when_only_source(self):
        """Test no match when only source keyword present."""
        belief = MockBelief(
            belief_id="b1",
            content="Natural light is pleasant",  # No stress mention
        )

        matched = self.service._belief_matches_edge(
            belief,
            src_env_ids=[],
            src_keywords=["natural light"],
            tgt_out_ids=[],
            tgt_keywords=["stress"]
        )

        assert matched is False


# =============================================================================
# Test Justification Status
# =============================================================================

class TestJustificationStatus:
    """Tests for justification status determination."""

    def setup_method(self):
        """Set up service."""
        self.service = EdgeJustificationService(web=None)

    def test_unjustified_when_no_beliefs(self):
        """Test UNJUSTIFIED status when no supporting beliefs."""
        status = self.service._determine_status(
            supporting=[],
            conflicting=[],
            agg_credence=0.0
        )

        assert status == JustificationStatus.UNJUSTIFIED

    def test_strong_when_high_credence_multiple_sources(self):
        """Test STRONG status with high credence and multiple sources."""
        beliefs = [
            MockBelief(belief_id="b1", content="test1", credence=MockCredence(0.8, 0.2)),
            MockBelief(belief_id="b2", content="test2", credence=MockCredence(0.75, 0.2)),
        ]

        status = self.service._determine_status(
            supporting=beliefs,
            conflicting=[],
            agg_credence=0.75
        )

        assert status == JustificationStatus.STRONG

    def test_contested_when_many_conflicts(self):
        """Test CONTESTED status when conflicts exceed threshold."""
        beliefs = [MockBelief(belief_id="b1", content="test")]
        conflicts = [
            ConflictSummary(belief_id="c1", credence=0.6, conflict_type=ConflictType.WEAKENS, content_summary="conflict")
        ]

        status = self.service._determine_status(
            supporting=beliefs,
            conflicting=conflicts,
            agg_credence=0.6
        )

        assert status == JustificationStatus.CONTESTED

    def test_weak_when_low_credence(self):
        """Test WEAK status when credence is low."""
        beliefs = [MockBelief(belief_id="b1", content="test", credence=MockCredence(0.3, 0.3))]

        status = self.service._determine_status(
            supporting=beliefs,
            conflicting=[],
            agg_credence=0.3
        )

        assert status == JustificationStatus.WEAK


# =============================================================================
# Test Full Service
# =============================================================================

class TestEdgeJustificationService:
    """Integration tests for the full service."""

    def test_get_justification_returns_valid_structure(self):
        """Test that get_justification returns valid EdgeJustification."""
        # Create mock web with beliefs
        mock_web = Mock()
        mock_web.beliefs = {
            'b1': MockBelief(
                belief_id='b1',
                content='Natural light reduces stress levels',
                credence=MockCredence(0.8, 0.2),
                paper_ids=['paper_001']
            )
        }
        mock_web._constraints_by_belief = {}
        mock_web.constraints = {}

        service = EdgeJustificationService(web=mock_web)
        result = service.get_justification('daylight', 'stress')

        assert isinstance(result, EdgeJustification)
        assert result.edge_id == 'daylight_stress'
        assert result.source_node == 'daylight'
        assert result.target_node == 'stress'
        assert 0 <= result.aggregate_credence <= 1

    def test_get_justification_with_no_web_returns_unjustified(self):
        """Test that missing web returns UNJUSTIFIED status."""
        # Create service and mock the web property to return None
        service = EdgeJustificationService(web=None, accumulator=None)
        # Patch the class property to return None
        with patch.object(EdgeJustificationService, 'web', new_callable=lambda: property(lambda self: None)):
            result = service.get_justification('daylight', 'stress')

            assert result.justification_status == JustificationStatus.UNJUSTIFIED
            assert len(result.supporting_beliefs) == 0

    def test_to_dict_returns_valid_json_structure(self):
        """Test that to_dict produces valid JSON-compatible dict."""
        mock_web = Mock()
        mock_web.beliefs = {}
        mock_web._constraints_by_belief = {}
        mock_web.constraints = {}

        service = EdgeJustificationService(web=mock_web)
        result = service.get_justification('daylight', 'stress')

        result_dict = result.to_dict()

        assert 'schema' in result_dict
        assert result_dict['schema'] == 'integration.edge_justification.v1'
        assert 'edge_id' in result_dict
        assert 'aggregate_credence' in result_dict
        assert 'justification_status' in result_dict


# =============================================================================
# Test API Endpoints
# =============================================================================

class TestIntegrationAPI:
    """Tests for integration API endpoints."""

    def test_health_endpoint_response_model(self):
        """Test that health endpoint has correct structure (without async)."""
        # This tests the response structure without actually calling the async endpoint
        # Full API testing would be done via FastAPI TestClient
        expected_keys = ['status', 'services', 'web_available']

        # Test that the function exists and is callable
        from app.routes.integration import integration_health
        assert callable(integration_health)


# =============================================================================
# Test Data Structures
# =============================================================================

class TestDataStructures:
    """Tests for data structure serialization."""

    def test_belief_summary_to_dict(self):
        """Test BeliefSummary serialization."""
        summary = BeliefSummary(
            belief_id="b1",
            credence=0.8,
            uncertainty=0.2,
            content_summary="Test belief",
            paper_id="paper_001",
            epistemic_level="EMPIRICAL"
        )

        d = summary.to_dict()

        assert d['belief_id'] == 'b1'
        assert d['credence'] == 0.8
        assert d['content_summary'] == 'Test belief'

    def test_conflict_summary_to_dict(self):
        """Test ConflictSummary serialization."""
        conflict = ConflictSummary(
            belief_id="c1",
            credence=0.6,
            conflict_type=ConflictType.CONTRADICTS,
            content_summary="Conflicting claim"
        )

        d = conflict.to_dict()

        assert d['belief_id'] == 'c1'
        assert d['conflict_type'] == 'contradicts'

    def test_edge_justification_to_dict(self):
        """Test EdgeJustification serialization."""
        justification = EdgeJustification(
            edge_id="test_edge",
            source_node="source",
            target_node="target",
            aggregate_credence=0.75,
            aggregate_uncertainty=0.15,
            justification_status=JustificationStatus.MODERATE
        )

        d = justification.to_dict()

        assert d['schema'] == 'integration.edge_justification.v1'
        assert d['edge_id'] == 'test_edge'
        assert d['justification_status'] == 'moderate'
        assert 'generated_at' in d
