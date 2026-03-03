"""
Integration Pipeline Tests — INT-1 through INT-6
2026-02-11

End-to-end tests verifying the complete pipeline between
Article_Eater (Epistemic Web) and BN_graphical (Bayesian Network).

Test Coverage:
- INT-1: Edge Justification Service
- INT-2: Gap Predictor Service
- INT-3: Edge Sync API endpoints
- INT-5: Cross-Layer Query Service
- Integration: Full pipeline with all services

Note: INT-4 (WebView) and INT-6 (User Modes) are frontend components
tested separately in BN_graphical.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone


# =============================================================================
# Mock Classes for Testing
# =============================================================================

@dataclass
class MockCredence:
    """Mock credence for testing."""
    value: float = 0.7
    uncertainty: float = 0.2


@dataclass
class MockBelief:
    """Mock belief for integration testing."""
    belief_id: str
    content: str
    level: str = "EMPIRICAL"
    credence: MockCredence = field(default_factory=lambda: MockCredence(0.7, 0.2))
    environment_id: Optional[str] = None
    outcome_id: Optional[str] = None
    theory_id: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    paper_ids: List[str] = field(default_factory=list)


@dataclass
class MockConstraint:
    """Mock constraint for testing."""
    constraint_id: str
    source_id: str
    target_id: str
    constraint_type: str = "SUPPORT"
    weight: float = 0.8


def create_mock_web(beliefs_dict: Dict[str, Any], constraints_dict: Optional[Dict] = None):
    """Create a mock WebOfBelief with given beliefs and constraints."""
    mock_web = Mock()
    mock_web.beliefs = beliefs_dict
    mock_web.constraints = constraints_dict or {}
    # Cross-layer query uses _constraints_by_belief index
    mock_web._constraints_by_belief = {}
    return mock_web


# =============================================================================
# Test INT-1 + INT-2 Integration
# =============================================================================

class TestEdgeJustificationGapIntegration:
    """Test EdgeJustification and GapPredictor work together."""

    def test_unjustified_edge_generates_gap(self):
        """
        When an edge has no justification, GapPredictor should identify it.
        INT-1 (EdgeJustification) + INT-2 (GapPredictor) integration.
        """
        from src.services.edge_justification import (
            EdgeJustificationService,
            JustificationStatus
        )
        from src.services.gap_predictor import GapPredictor, GapType

        # Create a web with beliefs that don't justify edge A→B
        mock_web = create_mock_web({
            'b1': MockBelief(
                belief_id='b1',
                content='C affects D',
                environment_id='env.C',
                outcome_id='out.D'
            )
        })

        # Edge service should report unjustified
        edge_service = EdgeJustificationService(web=mock_web)

        # Mock get_justification to return unjustified for test edge
        with patch.object(edge_service, 'get_justification') as mock_get:
            mock_justification = Mock()
            mock_justification.justification_status = JustificationStatus.UNJUSTIFIED
            mock_justification.edge_id = 'edge_A_B'
            mock_justification.source_node = 'A'
            mock_justification.target_node = 'B'
            mock_get.return_value = mock_justification

            with patch.object(edge_service, 'get_all_justifications') as mock_all:
                mock_all.return_value = [mock_justification]

                # Gap predictor should find the unjustified edge gap
                predictor = GapPredictor(web=mock_web, edge_justification_service=edge_service)
                gaps = predictor.find_unjustified_edge_gaps()

                assert len(gaps) == 1
                assert gaps[0].gap_type == GapType.UNJUSTIFIED_EDGE
                assert 'A' in gaps[0].description
                assert 'B' in gaps[0].description

    def test_justified_edge_no_gap(self):
        """
        When an edge has strong justification, no gap should be reported.
        """
        from src.services.edge_justification import (
            EdgeJustificationService,
            JustificationStatus
        )
        from src.services.gap_predictor import GapPredictor, GapType

        # Create web with beliefs that justify light→mood
        mock_web = create_mock_web({
            'b1': MockBelief(
                belief_id='b1',
                content='Light exposure affects mood',
                level='EMPIRICAL',
                environment_id='env.light',
                outcome_id='out.mood'
            ),
            'b2': MockBelief(
                belief_id='b2',
                content='Circadian rhythm theory explains light-mood relationship',
                level='THEORETICAL',
                environment_id='env.light',
                outcome_id='out.mood'
            )
        })

        # All edges are justified
        edge_service = EdgeJustificationService(web=mock_web)

        with patch.object(edge_service, 'get_all_justifications') as mock_all:
            # Return empty list (no unjustified edges)
            mock_all.return_value = []

            predictor = GapPredictor(web=mock_web, edge_justification_service=edge_service)
            gaps = predictor.find_unjustified_edge_gaps()

            assert len(gaps) == 0


# =============================================================================
# Test INT-5 Cross-Layer Query Integration
# =============================================================================

class TestCrossLayerQueryIntegration:
    """Test Cross-Layer Query service with full web structure."""

    def test_theory_support_returns_result_or_none(self):
        """
        Test find_theory_support returns appropriate result.
        INT-5: Cross-layer query handles beliefs without constraint index.
        """
        from src.services.cross_layer_query import CrossLayerQueryService

        # Create a web with multi-level beliefs
        mock_web = create_mock_web({
            'theory_1': MockBelief(
                belief_id='theory_1',
                content='ART theory: attention is fascinated by nature',
                level='THEORETICAL',
                environment_id='env.nature',
                outcome_id='out.attention'
            )
        })

        service = CrossLayerQueryService(web=mock_web)
        result = service.find_theory_support('theory_1')

        # Result should be a TheorySupportResult object (not None because belief exists)
        assert result is not None
        # With no constraint index, support will be empty but result is valid
        assert hasattr(result, 'theory_belief')
        assert hasattr(result, 'supporting_beliefs')
        assert hasattr(result, 'support_strength')

    def test_environment_outcome_query(self):
        """
        Test querying all beliefs for a specific env→outcome relationship.
        INT-5: Environment-outcome focused query.
        """
        from src.services.cross_layer_query import CrossLayerQueryService

        mock_web = create_mock_web({
            'b1': MockBelief(
                belief_id='b1',
                content='Plants reduce stress',
                level='EMPIRICAL',
                environment_id='env.plants',
                outcome_id='out.stress'
            ),
            'b2': MockBelief(
                belief_id='b2',
                content='Biophilia theory predicts plants reduce stress',
                level='THEORETICAL',
                environment_id='env.plants',
                outcome_id='out.stress'
            ),
            'b3': MockBelief(
                belief_id='b3',
                content='Light affects mood',
                level='EMPIRICAL',
                environment_id='env.light',
                outcome_id='out.mood'
            )
        })

        service = CrossLayerQueryService(web=mock_web)
        result = service.find_environment_outcome_beliefs(
            environment_id='env.plants',
            outcome_id='out.stress'
        )

        # Result is a CrossLayerQueryResult object with beliefs list
        assert result is not None
        assert hasattr(result, 'beliefs')
        assert len(result.beliefs) == 2
        belief_ids = [b.belief_id for b in result.beliefs]
        assert 'b1' in belief_ids
        assert 'b2' in belief_ids
        assert 'b3' not in belief_ids

    def test_layer_statistics(self):
        """
        Test layer statistics calculation.
        INT-5: Get distribution of beliefs across epistemic levels.
        """
        from src.services.cross_layer_query import CrossLayerQueryService

        mock_web = create_mock_web({
            't1': MockBelief(belief_id='t1', content='Theory', level='THEORETICAL'),
            'e1': MockBelief(belief_id='e1', content='Empirical 1', level='EMPIRICAL'),
            'e2': MockBelief(belief_id='e2', content='Empirical 2', level='EMPIRICAL'),
            'o1': MockBelief(belief_id='o1', content='Observation', level='OBSERVATIONAL'),
        })

        service = CrossLayerQueryService(web=mock_web)
        stats = service.get_layer_statistics()

        # Stats is a dict with by_level counts
        assert stats is not None
        assert 'by_level' in stats
        assert 'total_beliefs' in stats
        assert stats['total_beliefs'] == 4


# =============================================================================
# Test Evidence Clustering (Panel D0a)
# =============================================================================

class TestEvidenceClusteringIntegration:
    """Test evidence clustering by source paper (Panel D0a)."""

    def test_same_paper_beliefs_clustered(self):
        """
        Beliefs from the same paper should be clustered together
        to prevent double-counting evidence.
        """
        from src.services.edge_justification import EdgeJustificationService

        mock_web = create_mock_web({
            'b1': MockBelief(
                belief_id='b1',
                content='Finding 1 from Ulrich 1984',
                level='EMPIRICAL',
                environment_id='env.nature',
                outcome_id='out.stress',
                paper_ids=['ulrich_1984']
            ),
            'b2': MockBelief(
                belief_id='b2',
                content='Finding 2 from Ulrich 1984',
                level='EMPIRICAL',
                environment_id='env.nature',
                outcome_id='out.stress',
                paper_ids=['ulrich_1984']
            ),
            'b3': MockBelief(
                belief_id='b3',
                content='Finding from Kaplan 1989',
                level='EMPIRICAL',
                environment_id='env.nature',
                outcome_id='out.stress',
                paper_ids=['kaplan_1989']
            )
        })

        service = EdgeJustificationService(web=mock_web)
        clusters = service._cluster_beliefs_by_paper(list(mock_web.beliefs.values()))

        # Should have 2 clusters (one per paper)
        assert 'ulrich_1984' in clusters
        assert 'kaplan_1989' in clusters
        assert len(clusters['ulrich_1984']) == 2
        assert len(clusters['kaplan_1989']) == 1


# =============================================================================
# Test VOI with Centrality (Panel D0d)
# =============================================================================

class TestVOICentralityIntegration:
    """Test VOI calculation incorporates graph centrality (Panel D0d)."""

    def test_central_beliefs_higher_voi(self):
        """
        Gaps affecting more central beliefs should have higher VOI.
        Panel D0d: Graph centrality influences VOI calculation.
        """
        from src.services.gap_predictor import GapPredictor

        # Create constraints that make b1 more central than b3
        c1 = Mock(source_id='b1', target_id='b2')
        c2 = Mock(source_id='b1', target_id='b3')
        c3 = Mock(source_id='b1', target_id='b4')

        mock_web = create_mock_web(
            beliefs_dict={
                'b1': MockBelief(
                    belief_id='b1',
                    content='Central belief about light',
                    level='EMPIRICAL',
                    environment_id='env.light',
                    outcome_id='out.mood'
                ),
                'b2': MockBelief(
                    belief_id='b2',
                    content='Supporting belief 1',
                    level='EMPIRICAL',
                    environment_id='env.light',
                    outcome_id='out.mood'
                ),
                'b3': MockBelief(
                    belief_id='b3',
                    content='Peripheral belief about noise',
                    level='EMPIRICAL',
                    environment_id='env.noise',
                    outcome_id='out.focus'
                ),
                'b4': MockBelief(
                    belief_id='b4',
                    content='Another supporting belief',
                    level='EMPIRICAL',
                    environment_id='env.light',
                    outcome_id='out.mood'
                )
            },
            constraints_dict={
                'c1': c1, 'c2': c2, 'c3': c3
            }
        )

        predictor = GapPredictor(web=mock_web)
        centrality = predictor._compute_centrality_cache()

        # b1 should have higher centrality (connected to 3 others)
        assert centrality.get('b1', 0) > centrality.get('b3', 0)


# =============================================================================
# Test Full Pipeline Integration
# =============================================================================

class TestFullPipelineIntegration:
    """Test the complete pipeline with all services working together."""

    def test_pipeline_flow_web_to_gaps(self):
        """
        Test complete flow: Web → EdgeJustification → GapPredictor → Report
        """
        from src.services.edge_justification import EdgeJustificationService
        from src.services.gap_predictor import GapPredictor, GapReport
        from src.services.cross_layer_query import CrossLayerQueryService

        # Create a realistic web structure
        mock_web = create_mock_web({
            # Theoretical belief without empirical support (validation gap)
            't1': MockBelief(
                belief_id='t1',
                content='Theory predicts plants reduce cortisol',
                level='THEORETICAL',
                environment_id='env.plants',
                outcome_id='out.cortisol'
            ),
            # Empirical beliefs without theoretical explanation (mechanism gap)
            'e1': MockBelief(
                belief_id='e1',
                content='Study 1: Nature reduces stress',
                level='EMPIRICAL',
                environment_id='env.nature',
                outcome_id='out.stress',
                paper_ids=['study_1']
            ),
            'e2': MockBelief(
                belief_id='e2',
                content='Study 2: Nature reduces stress',
                level='EMPIRICAL',
                environment_id='env.nature',
                outcome_id='out.stress',
                paper_ids=['study_2']
            ),
            # Mediation path without direct link
            'm1': MockBelief(
                belief_id='m1',
                content='Light affects circadian rhythm',
                level='EMPIRICAL',
                environment_id='env.light',
                outcome_id='med.circadian'
            ),
            'm2': MockBelief(
                belief_id='m2',
                content='Circadian rhythm affects sleep',
                level='EMPIRICAL',
                environment_id='med.circadian',
                outcome_id='out.sleep'
            )
            # Note: No direct light→sleep belief (mediation gap)
        })

        # Initialize all services
        edge_service = EdgeJustificationService(web=mock_web)
        cross_layer_service = CrossLayerQueryService(web=mock_web)
        # Disable VOI scorer to test with heuristic formula
        gap_predictor = GapPredictor(web=mock_web, edge_justification_service=edge_service, voi_scorer=None)

        # Generate gap report
        report = gap_predictor.find_all_gaps(max_gaps=20)

        # Verify report structure
        assert isinstance(report, GapReport)
        assert report.n_gaps > 0
        assert 'gap_type_counts' in report.summary

        # Should find at least these gap types:
        gap_types = {g.gap_type.value for g in report.gaps}

        # Validation gap (t1 has no empirical support for plants→cortisol)
        assert 'validation' in gap_types

        # Mediation gap (light→circadian→sleep, but no light→sleep)
        assert 'mediation' in gap_types

        # Note: Mechanism gaps require specific level detection which may not
        # trigger with mock beliefs depending on how level matching works

        # Verify cross-layer query returns layer statistics
        stats = cross_layer_service.get_layer_statistics()
        assert stats is not None
        assert 'by_level' in stats

    def test_pipeline_serialization(self):
        """Test that all service outputs can be serialized to JSON-compatible dicts."""
        import json
        from src.services.gap_predictor import GapPredictor

        mock_web = create_mock_web({
            'b1': MockBelief(
                belief_id='b1',
                content='Test belief',
                level='EMPIRICAL',
                environment_id='env.test',
                outcome_id='out.test'
            )
        })

        predictor = GapPredictor(web=mock_web)
        report = predictor.find_all_gaps(max_gaps=5)

        # Should be JSON serializable
        report_dict = report.to_dict()
        json_str = json.dumps(report_dict)

        assert json_str is not None
        assert 'gaps' in report_dict
        assert 'schema' in report_dict

    def test_pipeline_handles_empty_web(self):
        """Test pipeline gracefully handles empty web."""
        from src.services.gap_predictor import GapPredictor
        from src.services.cross_layer_query import CrossLayerQueryService

        mock_web = create_mock_web({})

        # Don't use edge service (it lazy-loads BN edges)
        cross_layer_service = CrossLayerQueryService(web=mock_web)
        gap_predictor = GapPredictor(web=mock_web, edge_justification_service=None)

        # Gap predictor should return empty report from direct gap detection
        # (mediation, mechanism, boundary, direction, validation)
        mediation = gap_predictor.find_mediation_gaps()
        mechanism = gap_predictor.find_mechanism_gaps()
        boundary = gap_predictor.find_boundary_gaps()
        direction = gap_predictor.find_direction_gaps()
        validation = gap_predictor.find_validation_gaps()

        assert len(mediation) == 0
        assert len(mechanism) == 0
        assert len(boundary) == 0
        assert len(direction) == 0
        assert len(validation) == 0

        stats = cross_layer_service.get_layer_statistics()
        assert stats is not None


# =============================================================================
# Test API Response Formats (INT-3)
# =============================================================================

class TestAPIResponseFormats:
    """Test that API responses match expected schemas."""

    def test_edge_justification_response_format(self):
        """Test EdgeJustification response matches API schema."""
        from src.services.edge_justification import (
            EdgeJustificationService,
            EdgeJustification,
            JustificationStatus
        )

        mock_web = create_mock_web({
            'b1': MockBelief(
                belief_id='b1',
                content='Test belief',
                level='EMPIRICAL',
                environment_id='env.A',
                outcome_id='out.B'
            )
        })

        service = EdgeJustificationService(web=mock_web)
        justification = service.get_justification('env.A', 'out.B')

        # Convert to dict
        j_dict = justification.to_dict()

        # Required fields per API schema
        assert 'edge_id' in j_dict
        assert 'source_node' in j_dict
        assert 'target_node' in j_dict
        assert 'justification_status' in j_dict
        assert 'supporting_beliefs' in j_dict
        assert 'aggregate_credence' in j_dict
        assert 'aggregate_uncertainty' in j_dict

    def test_gap_report_response_format(self):
        """Test GapReport response matches API schema."""
        from src.services.gap_predictor import GapPredictor

        mock_web = create_mock_web({
            'b1': MockBelief(
                belief_id='b1',
                content='Test belief',
                level='EMPIRICAL',
                environment_id='env.A',
                outcome_id='out.B'
            )
        })

        predictor = GapPredictor(web=mock_web)
        report = predictor.find_all_gaps()

        r_dict = report.to_dict()

        # Required fields per API schema
        assert r_dict['schema'] == 'integration.gap_report.v1'
        assert 'report_id' in r_dict
        assert 'generated_at' in r_dict
        assert 'n_gaps' in r_dict
        assert 'n_high_priority' in r_dict
        assert 'gaps' in r_dict
        assert 'summary' in r_dict

    def test_cross_layer_query_response_format(self):
        """Test CrossLayerQuery response matches API schema."""
        from src.services.cross_layer_query import CrossLayerQueryService

        mock_web = create_mock_web({
            't1': MockBelief(
                belief_id='t1',
                content='Theoretical belief',
                level='THEORETICAL',
                environment_id='env.A',
                outcome_id='out.B'
            )
        })

        service = CrossLayerQueryService(web=mock_web)
        result = service.find_theory_support('t1')

        # Result should be a TheorySupportResult object with required attributes
        assert result is not None
        assert hasattr(result, 'theory_belief')
        assert hasattr(result, 'supporting_beliefs')
        assert hasattr(result, 'support_strength')
        assert hasattr(result, 'coverage_score')
        assert hasattr(result, 'gaps')

    def test_environment_outcome_query_response_format(self):
        """Test environment-outcome query response format."""
        from src.services.cross_layer_query import CrossLayerQueryService

        mock_web = create_mock_web({
            'b1': MockBelief(
                belief_id='b1',
                content='Test belief',
                level='EMPIRICAL',
                environment_id='env.A',
                outcome_id='out.B'
            )
        })

        service = CrossLayerQueryService(web=mock_web)
        result = service.find_environment_outcome_beliefs(
            environment_id='env.A',
            outcome_id='out.B'
        )

        # Result is a CrossLayerQueryResult with required attributes
        assert result is not None
        assert hasattr(result, 'query_type')
        assert hasattr(result, 'beliefs')
        assert hasattr(result, 'generated_at')
        assert len(result.beliefs) == 1
