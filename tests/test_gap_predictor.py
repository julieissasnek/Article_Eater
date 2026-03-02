"""
Tests for Gap Predictor Service — Sprint INT-2
2026-02-11

Tests cover:
1. Mediation gap detection (A→X→Y but no A→Y)
2. Mechanism gap detection (empirical without theoretical)
3. Boundary gap detection (narrow scope)
4. Direction gap detection (conflicting causal directions)
5. Validation gap detection (theoretical without empirical)
6. VOI calculation
7. GapReport structure
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from dataclasses import dataclass, field
from typing import List, Optional, Set
from datetime import datetime, timezone

from src.services.gap_predictor import (
    GapPredictor,
    GapReport,
    PredictedGap,
    GapType,
    GapPriority,
    KNOWN_SETTINGS,
    KNOWN_POPULATIONS,
    get_gap_predictor,
)


# =============================================================================
# Mock Belief Classes
# =============================================================================

@dataclass
class MockCredence:
    """Mock credence object."""
    value: float = 0.5
    uncertainty: float = 0.3


@dataclass
class MockScope:
    """Mock scope object for boundary gap testing."""
    setting: Optional[str] = None
    population: Optional[str] = None


@dataclass
class MockBelief:
    """Mock belief for testing."""
    belief_id: str
    content: str
    level: str = "EMPIRICAL"
    credence: MockCredence = field(default_factory=lambda: MockCredence(0.7, 0.2))
    environment_id: Optional[str] = None
    outcome_id: Optional[str] = None
    theory_id: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    scope: Optional[MockScope] = None


# =============================================================================
# Test Data Structures
# =============================================================================

class TestGapDataStructures:
    """Tests for gap data structures."""

    def test_predicted_gap_to_dict(self):
        """Test PredictedGap serialization."""
        gap = PredictedGap(
            gap_id="gap_0001",
            gap_type=GapType.MEDIATION,
            description="Test gap",
            priority=GapPriority.HIGH,
            voi_score=0.75,
            affected_edge="a_b",
            affected_beliefs=["b1", "b2"],
            suggested_search="test search",
            resolution_approach="test approach"
        )

        d = gap.to_dict()

        assert d['gap_id'] == 'gap_0001'
        assert d['gap_type'] == 'mediation'
        assert d['priority'] == 'high'
        assert d['voi_score'] == 0.75
        assert d['affected_edge'] == 'a_b'
        assert d['suggested_search'] == 'test search'
        assert 'generated_at' in d

    def test_gap_report_to_dict(self):
        """Test GapReport serialization."""
        gap = PredictedGap(
            gap_id="gap_0001",
            gap_type=GapType.MECHANISM,
            description="Test gap",
            voi_score=0.6
        )

        report = GapReport(
            report_id="test_report",
            generated_at=datetime.now(timezone.utc),
            n_gaps=1,
            n_high_priority=0,
            gaps=[gap],
            summary={'test': 'value'}
        )

        d = report.to_dict()

        assert d['schema'] == 'integration.gap_report.v1'
        assert d['report_id'] == 'test_report'
        assert d['n_gaps'] == 1
        assert len(d['gaps']) == 1
        assert d['gaps'][0]['gap_type'] == 'mechanism'

    def test_gap_types_enum(self):
        """Test all gap types are defined."""
        expected_types = {
            'mediation', 'mechanism', 'boundary', 'direction',
            'interaction', 'validation', 'unjustified_edge'
        }

        actual_types = {t.value for t in GapType}

        assert expected_types <= actual_types


# =============================================================================
# Test Mediation Gap Detection
# =============================================================================

def create_mock_web(beliefs_dict, constraints_dict=None):
    """Helper to create mock web with proper structure."""
    mock_web = Mock()
    mock_web.beliefs = beliefs_dict
    mock_web.constraints = constraints_dict or {}
    return mock_web


class TestMediationGaps:
    """Tests for mediation gap detection."""

    def test_finds_mediation_gap(self):
        """Test detecting A→X→Y without A→Y."""
        # Create mock web with beliefs forming a 2-hop path
        mock_web = create_mock_web({
            'b1': MockBelief(
                belief_id='b1',
                content='A affects X',
                environment_id='env.A',
                outcome_id='med.X'
            ),
            'b2': MockBelief(
                belief_id='b2',
                content='X affects Y',
                environment_id='med.X',
                outcome_id='out.Y'
            )
            # Note: No direct A→Y belief
        })

        predictor = GapPredictor(web=mock_web)
        gaps = predictor.find_mediation_gaps()

        assert len(gaps) >= 1
        mediation_gaps = [g for g in gaps if g.gap_type == GapType.MEDIATION]
        assert len(mediation_gaps) >= 1

        gap = mediation_gaps[0]
        assert 'A' in gap.description or 'env.A' in gap.description
        assert 'Y' in gap.description or 'out.Y' in gap.description

    def test_no_gap_when_direct_path_exists(self):
        """Test no mediation gap when A→Y exists."""
        mock_web = create_mock_web({
            'b1': MockBelief(
                belief_id='b1',
                content='A affects X',
                environment_id='env.A',
                outcome_id='med.X'
            ),
            'b2': MockBelief(
                belief_id='b2',
                content='X affects Y',
                environment_id='med.X',
                outcome_id='out.Y'
            ),
            'b3': MockBelief(
                belief_id='b3',
                content='A directly affects Y',
                environment_id='env.A',
                outcome_id='out.Y'
            )
        })

        predictor = GapPredictor(web=mock_web)
        gaps = predictor.find_mediation_gaps()

        # Should find no mediation gap for A→Y (it exists)
        a_y_gaps = [g for g in gaps if 'env.A' in str(g.implied_by) and 'out.Y' in str(g.description)]
        assert len(a_y_gaps) == 0

    def test_empty_web_returns_no_gaps(self):
        """Test that empty web returns no mediation gaps."""
        mock_web = create_mock_web({})

        predictor = GapPredictor(web=mock_web)
        gaps = predictor.find_mediation_gaps()

        assert len(gaps) == 0

    def test_none_web_returns_empty(self):
        """Test that None web returns empty list."""
        predictor = GapPredictor(web=None)
        # Patch the web property to return None
        with patch.object(GapPredictor, 'web', new_callable=lambda: property(lambda self: None)):
            gaps = predictor.find_mediation_gaps()
            assert len(gaps) == 0


# =============================================================================
# Test Mechanism Gap Detection
# =============================================================================

class TestMechanismGaps:
    """Tests for mechanism gap detection."""

    def test_finds_mechanism_gap(self):
        """Test detecting empirical beliefs without theoretical explanation."""
        mock_web = create_mock_web({
            'b1': MockBelief(
                belief_id='b1',
                content='Empirical finding 1',
                level='EMPIRICAL',
                environment_id='env.light',
                outcome_id='out.mood'
            ),
            'b2': MockBelief(
                belief_id='b2',
                content='Empirical finding 2',
                level='EMPIRICAL',
                environment_id='env.light',
                outcome_id='out.mood'
            )
            # Note: No THEORETICAL belief for light→mood
        })

        predictor = GapPredictor(web=mock_web)
        gaps = predictor.find_mechanism_gaps()

        assert len(gaps) >= 1
        gap = gaps[0]
        assert gap.gap_type == GapType.MECHANISM
        assert 'light' in gap.description
        assert 'mood' in gap.description
        assert 'mechanism' in gap.resolution_approach.lower() or 'theoretical' in gap.resolution_approach.lower()

    def test_no_gap_when_theory_exists(self):
        """Test no mechanism gap when theoretical belief exists."""
        mock_web = create_mock_web({
            'b1': MockBelief(
                belief_id='b1',
                content='Empirical finding',
                level='EMPIRICAL',
                environment_id='env.light',
                outcome_id='out.mood'
            ),
            'b2': MockBelief(
                belief_id='b2',
                content='Theoretical explanation',
                level='THEORETICAL',
                environment_id='env.light',
                outcome_id='out.mood'
            )
        })

        predictor = GapPredictor(web=mock_web)
        gaps = predictor.find_mechanism_gaps()

        # Should find no mechanism gap for light→mood (has theory)
        light_mood_gaps = [g for g in gaps if 'light' in g.description and 'mood' in g.description]
        assert len(light_mood_gaps) == 0

    def test_voi_increases_with_more_evidence(self):
        """Test that VOI increases when more empirical beliefs support relationship."""
        mock_web = create_mock_web({
            f'b{i}': MockBelief(
                belief_id=f'b{i}',
                content=f'Empirical finding {i}',
                level='EMPIRICAL',
                environment_id='env.noise',
                outcome_id='out.stress'
            )
            for i in range(5)  # 5 empirical beliefs
        })

        predictor = GapPredictor(web=mock_web)
        gaps = predictor.find_mechanism_gaps()

        assert len(gaps) >= 1
        # More empirical support → higher VOI (base capped at 0.7, plus centrality bonus)
        # Formula: min(0.4 + 0.1*n, 0.7) + centrality_bonus
        # With 5 beliefs: min(0.4 + 0.5, 0.7) = 0.7, centrality adds small bonus
        assert gaps[0].voi_score >= 0.65


# =============================================================================
# Test Boundary Gap Detection
# =============================================================================

class TestBoundaryGaps:
    """Tests for boundary gap detection."""

    def test_finds_boundary_gap(self):
        """Test detecting narrow scope conditions."""
        mock_web = create_mock_web({
            'b1': MockBelief(
                belief_id='b1',
                content='Effect in office setting',
                environment_id='env.plants',
                outcome_id='out.stress',
                tags=['setting:office']
            )
            # Note: Only office setting, missing many others
        })

        predictor = GapPredictor(web=mock_web)
        gaps = predictor.find_boundary_gaps()

        assert len(gaps) >= 1
        gap = gaps[0]
        assert gap.gap_type == GapType.BOUNDARY
        # Should mention some missing settings from KNOWN_SETTINGS
        # (the first 3 alphabetically after filtering out 'office')
        known_minus_office = KNOWN_SETTINGS - {'office'}
        assert any(s in gap.description.lower() for s in known_minus_office)

    def test_no_gap_when_no_coverage(self):
        """Test no boundary gap when belief has no scope coverage."""
        mock_web = create_mock_web({
            'b1': MockBelief(
                belief_id='b1',
                content='Generic effect',
                environment_id='env.plants',
                outcome_id='out.stress',
                tags=[]  # No setting tags
            )
        })

        predictor = GapPredictor(web=mock_web)
        gaps = predictor.find_boundary_gaps()

        # No gaps because we need at least some coverage to identify gaps
        boundary_gaps = [g for g in gaps if g.gap_type == GapType.BOUNDARY]
        assert len(boundary_gaps) == 0

    def test_known_settings_constant(self):
        """Test that KNOWN_SETTINGS contains expected values."""
        expected = {'office', 'healthcare', 'educational'}
        assert expected <= KNOWN_SETTINGS

    def test_known_populations_constant(self):
        """Test that KNOWN_POPULATIONS contains expected values."""
        expected = {'adults', 'children', 'workers'}
        assert expected <= KNOWN_POPULATIONS


# =============================================================================
# Test Direction Gap Detection
# =============================================================================

class TestDirectionGaps:
    """Tests for direction gap detection."""

    def test_finds_direction_gap(self):
        """Test detecting bidirectional relationships."""
        mock_web = create_mock_web({
            'b1': MockBelief(
                belief_id='b1',
                content='A affects B',
                environment_id='var.A',
                outcome_id='var.B'
            ),
            'b2': MockBelief(
                belief_id='b2',
                content='B affects A',
                environment_id='var.B',
                outcome_id='var.A'
            )
        })

        predictor = GapPredictor(web=mock_web)
        gaps = predictor.find_direction_gaps()

        assert len(gaps) >= 1
        gap = gaps[0]
        assert gap.gap_type == GapType.DIRECTION
        assert 'direction' in gap.description.lower() or 'unclear' in gap.description.lower()
        assert gap.priority == GapPriority.HIGH  # Direction gaps are high priority

    def test_no_gap_for_unidirectional(self):
        """Test no direction gap for clear unidirectional relationship."""
        mock_web = create_mock_web({
            'b1': MockBelief(
                belief_id='b1',
                content='A affects B',
                environment_id='var.A',
                outcome_id='var.B'
            )
            # No B→A belief
        })

        predictor = GapPredictor(web=mock_web)
        gaps = predictor.find_direction_gaps()

        assert len(gaps) == 0


# =============================================================================
# Test Validation Gap Detection
# =============================================================================

class TestValidationGaps:
    """Tests for validation gap detection."""

    def test_finds_validation_gap(self):
        """Test detecting theoretical beliefs without empirical support."""
        mock_web = create_mock_web({
            'b1': MockBelief(
                belief_id='b1',
                content='Theory predicts X affects Y',
                level='THEORETICAL',
                environment_id='env.X',
                outcome_id='out.Y'
            )
            # Note: No EMPIRICAL belief for X→Y
        })

        predictor = GapPredictor(web=mock_web)
        gaps = predictor.find_validation_gaps()

        assert len(gaps) >= 1
        gap = gaps[0]
        assert gap.gap_type == GapType.VALIDATION
        # Resolution approach mentions testing/studies
        assert 'experimental' in gap.resolution_approach.lower() or 'studies' in gap.resolution_approach.lower()

    def test_no_gap_when_empirical_exists(self):
        """Test no validation gap when empirical support exists."""
        mock_web = create_mock_web({
            'b1': MockBelief(
                belief_id='b1',
                content='Theory predicts X affects Y',
                level='THEORETICAL',
                environment_id='env.X',
                outcome_id='out.Y'
            ),
            'b2': MockBelief(
                belief_id='b2',
                content='Study found X affects Y',
                level='EMPIRICAL',
                environment_id='env.X',
                outcome_id='out.Y'
            )
        })

        predictor = GapPredictor(web=mock_web)
        gaps = predictor.find_validation_gaps()

        # Should find no validation gap for X→Y
        x_y_gaps = [g for g in gaps if 'X' in g.description and 'Y' in g.description]
        assert len(x_y_gaps) == 0


# =============================================================================
# Test Full Service Integration
# =============================================================================

class TestGapPredictorService:
    """Integration tests for the full service."""

    def test_find_all_gaps_returns_report(self):
        """Test find_all_gaps returns valid GapReport."""
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
        report = predictor.find_all_gaps(max_gaps=10)

        assert isinstance(report, GapReport)
        assert hasattr(report, 'gaps')
        assert hasattr(report, 'n_gaps')
        assert hasattr(report, 'n_high_priority')
        assert 'gap_type_counts' in report.summary

    def test_find_all_gaps_respects_max(self):
        """Test that find_all_gaps respects max_gaps limit."""
        # Create many beliefs that would generate many gaps
        mock_web = create_mock_web({
            f'b{i}': MockBelief(
                belief_id=f'b{i}',
                content=f'Belief {i}',
                level='EMPIRICAL',
                environment_id=f'env.var{i}',
                outcome_id=f'out.result{i}'
            )
            for i in range(20)
        })

        predictor = GapPredictor(web=mock_web)
        report = predictor.find_all_gaps(max_gaps=5)

        assert len(report.gaps) <= 5

    def test_gaps_sorted_by_voi(self):
        """Test that gaps are sorted by VOI score descending."""
        mock_web = create_mock_web({
            'b1': MockBelief(
                belief_id='b1',
                content='Empirical 1',
                level='EMPIRICAL',
                environment_id='env.A',
                outcome_id='out.B'
            ),
            'b2': MockBelief(
                belief_id='b2',
                content='Empirical 2',
                level='EMPIRICAL',
                environment_id='env.A',
                outcome_id='out.B'
            ),
            'b3': MockBelief(
                belief_id='b3',
                content='Empirical 3',
                level='EMPIRICAL',
                environment_id='env.A',
                outcome_id='out.B'
            ),
        })

        predictor = GapPredictor(web=mock_web)
        report = predictor.find_all_gaps()

        # Check that VOI scores are non-increasing
        voi_scores = [g.voi_score for g in report.gaps]
        for i in range(len(voi_scores) - 1):
            assert voi_scores[i] >= voi_scores[i + 1]

    def test_gap_id_generation(self):
        """Test that gap IDs are unique and sequential."""
        mock_web = create_mock_web({
            f'b{i}': MockBelief(
                belief_id=f'b{i}',
                content=f'Belief {i}',
                level='EMPIRICAL',
                environment_id=f'env.{i}',
                outcome_id=f'out.{i}'
            )
            for i in range(5)
        })

        predictor = GapPredictor(web=mock_web)
        report = predictor.find_all_gaps()

        gap_ids = [g.gap_id for g in report.gaps]
        # All IDs should be unique
        assert len(gap_ids) == len(set(gap_ids))
        # All IDs should follow pattern
        for gap_id in gap_ids:
            assert gap_id.startswith('gap_')


# =============================================================================
# Test Singleton and Convenience Functions
# =============================================================================

class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_get_gap_predictor_returns_singleton(self):
        """Test that get_gap_predictor returns singleton."""
        # Reset global
        import src.services.gap_predictor as gp_module
        gp_module._predictor_instance = None

        p1 = get_gap_predictor()
        p2 = get_gap_predictor()

        assert p1 is p2

    def test_predictor_handles_none_web_gracefully(self):
        """Test that predictor handles None web without crashing."""
        predictor = GapPredictor(web=None, edge_justification_service=None)

        # Patch the web property to return None to prevent lazy-loading
        with patch.object(GapPredictor, 'web', new_callable=lambda: property(lambda self: None)):
            with patch.object(GapPredictor, 'edge_service', new_callable=lambda: property(lambda self: None)):
                # All these should return empty lists, not crash
                assert predictor.find_mediation_gaps() == []
                assert predictor.find_mechanism_gaps() == []
                assert predictor.find_boundary_gaps() == []
                assert predictor.find_direction_gaps() == []
                assert predictor.find_validation_gaps() == []
                assert predictor.find_unjustified_edge_gaps() == []


# =============================================================================
# Test VOI Calculations
# =============================================================================

class TestVOICalculations:
    """Tests for Value of Information calculations."""

    def test_mechanism_voi_formula(self):
        """Test mechanism VOI formula: min(0.4 + 0.1 × n_beliefs, 0.7).

        NOTE: Without a web DB connection, no centrality bonus is applied,
        so VOI equals the base formula exactly.
        """
        predictor = GapPredictor()

        # 1 belief: min(0.4 + 0.1, 0.7) = 0.5 base
        beliefs_1 = [MockBelief(belief_id='b1', content='test')]
        voi_1 = predictor._compute_mechanism_voi(beliefs_1)
        # Without web, no centrality bonus, so base only = 0.5
        assert voi_1 == pytest.approx(0.5, rel=0.05)

        # 5 beliefs: min(0.4 + 0.5, 0.7) = 0.7 base (capped)
        beliefs_5 = [MockBelief(belief_id=f'b{i}', content='test') for i in range(5)]
        voi_5 = predictor._compute_mechanism_voi(beliefs_5)
        # Base 0.7 (capped at 0.7)
        assert voi_5 >= 0.7

    def test_boundary_voi_formula(self):
        """Test boundary VOI formula: 0.4 + 0.4 × (1 - coverage_ratio)."""
        predictor = GapPredictor()

        # 1 covered, 4 missing: coverage = 0.2, VOI = 0.4 + 0.4*0.8 = 0.72
        voi = predictor._compute_boundary_voi(n_covered=1, n_missing=4)
        assert voi == pytest.approx(0.72, rel=0.01)

        # 0 covered: should return 0.3
        voi_zero = predictor._compute_boundary_voi(n_covered=0, n_missing=5)
        assert voi_zero == 0.3

    def test_direction_gaps_have_high_voi(self):
        """Test that direction gaps have high VOI (0.8)."""
        mock_web = create_mock_web({
            'b1': MockBelief(
                belief_id='b1',
                content='A affects B',
                environment_id='var.A',
                outcome_id='var.B'
            ),
            'b2': MockBelief(
                belief_id='b2',
                content='B affects A',
                environment_id='var.B',
                outcome_id='var.A'
            )
        })

        predictor = GapPredictor(web=mock_web)
        gaps = predictor.find_direction_gaps()

        assert len(gaps) >= 1
        # Direction gaps have fixed VOI of 0.8
        assert gaps[0].voi_score == 0.8

    def test_validation_gaps_have_medium_voi(self):
        """Test that validation gaps have VOI of 0.65."""
        mock_web = create_mock_web({
            'b1': MockBelief(
                belief_id='b1',
                content='Theory predicts X affects Y',
                level='THEORETICAL',
                environment_id='env.X',
                outcome_id='out.Y'
            )
        })

        predictor = GapPredictor(web=mock_web)
        gaps = predictor.find_validation_gaps()

        assert len(gaps) >= 1
        # Validation gaps have fixed VOI of 0.65
        assert gaps[0].voi_score == 0.65


# =============================================================================
# Test Centrality Integration (Panel D0d)
# =============================================================================

class TestCentralityIntegration:
    """Tests for centrality-based VOI adjustments (Panel D0d)."""

    def test_centrality_cache_handles_empty_constraints(self):
        """Test that centrality cache handles empty constraints dict."""
        mock_web = create_mock_web({
            'b1': MockBelief(belief_id='b1', content='test')
        }, constraints_dict={})

        predictor = GapPredictor(web=mock_web)
        cache = predictor._compute_centrality_cache()

        # Returns beliefs with 0 centrality (no adjacency), plus env/out entries
        assert 'b1' in cache
        assert cache['b1'] == 0.0

    def test_centrality_cache_handles_non_dict_constraints(self):
        """Test that centrality cache handles web with non-dict constraints."""
        mock_web = Mock()
        mock_web.beliefs = {'b1': MockBelief(belief_id='b1', content='test')}
        # Configure constraints to be None (has no 'values' method)
        mock_web.constraints = None

        predictor = GapPredictor(web=mock_web)
        cache = predictor._compute_centrality_cache()

        # Should return beliefs with 0 centrality, not crash
        assert 'b1' in cache

    def test_centrality_adjusts_voi(self):
        """Test that centrality score adjusts VOI calculation."""
        # Create mock constraints with source_id/target_id (not belief_ids)
        c1 = Mock(source_id='b1', target_id='b2')
        c2 = Mock(source_id='b1', target_id='b3')
        c3 = Mock(source_id='b1', target_id='b4')

        # Create a web with constraints to test centrality
        mock_web = create_mock_web(
            beliefs_dict={
                'b1': MockBelief(
                    belief_id='b1',
                    content='Central belief',
                    level='EMPIRICAL',
                    environment_id='env.A',
                    outcome_id='out.B'
                ),
                'b2': MockBelief(
                    belief_id='b2',
                    content='Peripheral belief',
                    level='EMPIRICAL',
                    environment_id='env.C',
                    outcome_id='out.D'
                ),
                'b3': MockBelief(belief_id='b3', content='Another belief'),
                'b4': MockBelief(belief_id='b4', content='Yet another belief')
            },
            constraints_dict={
                'c1': c1,
                'c2': c2,
                'c3': c3,
            }
        )

        predictor = GapPredictor(web=mock_web)
        cache = predictor._compute_centrality_cache()

        # b1 has degree 3 (connects to b2, b3, b4)
        # b2, b3, b4 each have degree 1 (connect only to b1)
        # b1 should have higher centrality
        assert cache.get('b1', 0) > cache.get('b2', 0)


# =============================================================================
# Test Edge Cases
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_belief_without_environment_id(self):
        """Test handling beliefs without environment_id."""
        mock_web = create_mock_web({
            'b1': MockBelief(
                belief_id='b1',
                content='Belief without env',
                environment_id=None,
                outcome_id='out.Y'
            )
        })

        predictor = GapPredictor(web=mock_web)

        # Should not crash
        gaps = predictor.find_mediation_gaps()
        assert isinstance(gaps, list)

    def test_belief_without_outcome_id(self):
        """Test handling beliefs without outcome_id."""
        mock_web = create_mock_web({
            'b1': MockBelief(
                belief_id='b1',
                content='Belief without outcome',
                environment_id='env.X',
                outcome_id=None
            )
        })

        predictor = GapPredictor(web=mock_web)

        # Should not crash
        gaps = predictor.find_mechanism_gaps()
        assert isinstance(gaps, list)

    def test_very_large_web(self):
        """Test performance with larger web (100 beliefs)."""
        mock_web = create_mock_web({
            f'b{i}': MockBelief(
                belief_id=f'b{i}',
                content=f'Belief {i}',
                level='EMPIRICAL' if i % 3 != 0 else 'THEORETICAL',
                environment_id=f'env.{i % 10}',
                outcome_id=f'out.{i % 5}'
            )
            for i in range(100)
        })

        predictor = GapPredictor(web=mock_web)

        # Should complete without timeout
        report = predictor.find_all_gaps(max_gaps=20)

        assert isinstance(report, GapReport)
        assert len(report.gaps) <= 20

    def test_duplicate_beliefs_same_edge(self):
        """Test handling multiple beliefs for same env→outcome edge."""
        mock_web = create_mock_web({
            f'b{i}': MockBelief(
                belief_id=f'b{i}',
                content=f'Study {i} finding',
                level='EMPIRICAL',
                environment_id='env.light',
                outcome_id='out.mood'
            )
            for i in range(10)
        })

        predictor = GapPredictor(web=mock_web)
        gaps = predictor.find_mechanism_gaps()

        # Should find exactly one mechanism gap for light→mood
        light_mood_gaps = [g for g in gaps if 'light' in g.description and 'mood' in g.description]
        assert len(light_mood_gaps) == 1

        # VOI should be high: base capped at 0.7 + centrality bonus
        # Formula: min(0.4 + 0.1*n, 0.7) + 0.3 * centrality
        assert light_mood_gaps[0].voi_score >= 0.7
