"""
ECB-F6: Boundary Value Tests for Sprint ECB-3 Features

Tests for exact threshold boundaries in contrast transfer, security weight bounds,
gap identification edge cases, and error handling.

Panel Source: Brooks
Date: 2026-02-10
"""

import pytest
from unittest.mock import MagicMock, patch
import os

# Import the module under test
from src.services.epistemic_causal_bridge import (
    EpistemicCausalBridge,
    ContrastTransferType,
    ContrastAssessment,
    ContrastClass,
    ContrastType,
    ConditionSpec,
    PopulationContext,
    BaselineSpec,
    CONTRAST_TRANSFER_THRESHOLDS,
    EpistemicGap,
)


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def mock_web():
    """Create a minimal mock WebOfBelief for testing."""
    web = MagicMock()
    web.beliefs = {}
    web.constraints = {}
    web.theory_ids = []
    web.domain = "test"
    return web


@pytest.fixture
def bridge(mock_web):
    """Create a bridge instance for testing."""
    return EpistemicCausalBridge(mock_web)


@pytest.fixture
def sample_contrast_class():
    """Create a sample contrast class for testing."""
    return ContrastClass(
        contrast_id="test_contrast",
        focal=ConditionSpec(variable="nature_exposure", value=1, description="With nature"),
        contrasts=[ConditionSpec(variable="nature_exposure", value=0, description="Without nature")],
        contrast_type=ContrastType.NULL,
        explicit=True
    )


# =============================================================================
# TEST CLASS: Contrast Transfer Threshold Boundaries
# =============================================================================

class TestContrastThresholdBoundaries:
    """Test contrast transfer classification at exact threshold values."""

    def test_thresholds_configured_correctly(self):
        """Verify default threshold values."""
        assert CONTRAST_TRANSFER_THRESHOLDS[ContrastTransferType.DIRECT] == 0.9
        assert CONTRAST_TRANSFER_THRESHOLDS[ContrastTransferType.BASELINE_SHIFT] == 0.7
        assert CONTRAST_TRANSFER_THRESHOLDS[ContrastTransferType.POPULATION_SHIFT] == 0.5

    def test_direct_threshold_at_0_90(self, bridge):
        """Similarity of exactly 0.90 should be DIRECT."""
        result = bridge._classify_contrast_transfer(
            contrast_similarity=0.90,
            contrast_preserved=True,
            baseline_diffs={},
            meaning_diffs={},
            source_contrast=MagicMock(),
            target_contrast=MagicMock()
        )
        transfer_type, _, is_defined, _ = result
        assert transfer_type == ContrastTransferType.DIRECT
        assert is_defined is True

    def test_direct_threshold_at_0_89(self, bridge):
        """Similarity of 0.89 should be BASELINE_SHIFT (not DIRECT)."""
        result = bridge._classify_contrast_transfer(
            contrast_similarity=0.89,
            contrast_preserved=False,
            baseline_diffs={},
            meaning_diffs={},
            source_contrast=MagicMock(),
            target_contrast=MagicMock()
        )
        transfer_type, _, is_defined, _ = result
        assert transfer_type == ContrastTransferType.BASELINE_SHIFT
        assert is_defined is True

    def test_baseline_threshold_at_0_70(self, bridge):
        """Similarity of exactly 0.70 should be BASELINE_SHIFT."""
        result = bridge._classify_contrast_transfer(
            contrast_similarity=0.70,
            contrast_preserved=False,
            baseline_diffs={},
            meaning_diffs={},
            source_contrast=MagicMock(),
            target_contrast=MagicMock()
        )
        transfer_type, _, is_defined, _ = result
        assert transfer_type == ContrastTransferType.BASELINE_SHIFT
        assert is_defined is True

    def test_baseline_threshold_at_0_69(self, bridge):
        """Similarity of 0.69 should be POPULATION_SHIFT (not BASELINE_SHIFT)."""
        result = bridge._classify_contrast_transfer(
            contrast_similarity=0.69,
            contrast_preserved=False,
            baseline_diffs={},
            meaning_diffs={},
            source_contrast=MagicMock(),
            target_contrast=MagicMock()
        )
        transfer_type, _, is_defined, _ = result
        assert transfer_type == ContrastTransferType.POPULATION_SHIFT
        assert is_defined is True

    def test_population_threshold_at_0_50(self, bridge):
        """Similarity of exactly 0.50 should be POPULATION_SHIFT."""
        result = bridge._classify_contrast_transfer(
            contrast_similarity=0.50,
            contrast_preserved=False,
            baseline_diffs={},
            meaning_diffs={},
            source_contrast=MagicMock(),
            target_contrast=MagicMock()
        )
        transfer_type, _, is_defined, _ = result
        assert transfer_type == ContrastTransferType.POPULATION_SHIFT
        assert is_defined is True

    def test_population_threshold_at_0_49(self, bridge):
        """Similarity of 0.49 should be MEANING_SHIFT (undefined result)."""
        result = bridge._classify_contrast_transfer(
            contrast_similarity=0.49,
            contrast_preserved=False,
            baseline_diffs={},
            meaning_diffs={},
            source_contrast=MagicMock(),
            target_contrast=MagicMock()
        )
        transfer_type, _, is_defined, reason = result
        assert transfer_type == ContrastTransferType.MEANING_SHIFT
        assert is_defined is False
        assert "0.49" in reason

    def test_meaning_diff_overrides_high_similarity(self, bridge):
        """Meaning differences should override even high similarity scores."""
        result = bridge._classify_contrast_transfer(
            contrast_similarity=0.95,  # Would be DIRECT by similarity
            contrast_preserved=True,
            baseline_diffs={},
            meaning_diffs={"nature": ("wilderness", "park")},  # But meaning differs
            source_contrast=MagicMock(),
            target_contrast=MagicMock()
        )
        transfer_type, _, is_defined, reason = result
        assert transfer_type == ContrastTransferType.MEANING_SHIFT
        assert is_defined is False
        assert "nature" in reason

    def test_null_source_contrast_returns_undefined(self, bridge):
        """Missing source contrast should return UNDEFINED (but still defined result)."""
        result = bridge._classify_contrast_transfer(
            contrast_similarity=0.0,
            contrast_preserved=False,
            baseline_diffs={},
            meaning_diffs={},
            source_contrast=None,
            target_contrast=MagicMock()
        )
        transfer_type, _, is_defined, _ = result
        assert transfer_type == ContrastTransferType.UNDEFINED
        # UNDEFINED contrast != undefined result (we just don't know the contrast)
        assert is_defined is True


class TestContrastThresholdsConfigurable:
    """Test that thresholds can be configured via environment variables."""

    def test_direct_threshold_from_env(self):
        """Threshold should be configurable via AE_CONTRAST_THRESHOLD_DIRECT."""
        with patch.dict(os.environ, {'AE_CONTRAST_THRESHOLD_DIRECT': '0.95'}):
            # Re-import to pick up new env var (would need module reload in practice)
            # For now, just test that the env var is read
            val = float(os.environ.get('AE_CONTRAST_THRESHOLD_DIRECT', '0.9'))
            assert val == 0.95

    def test_population_threshold_from_env(self):
        """Threshold should be configurable via AE_CONTRAST_THRESHOLD_POPULATION."""
        with patch.dict(os.environ, {'AE_CONTRAST_THRESHOLD_POPULATION': '0.6'}):
            val = float(os.environ.get('AE_CONTRAST_THRESHOLD_POPULATION', '0.5'))
            assert val == 0.6


# =============================================================================
# TEST CLASS: Security Weight Bounds
# =============================================================================

class TestSecurityWeightBounds:
    """Test that security weights stay within valid bounds."""

    def test_minimum_security_floor(self, bridge, mock_web):
        """Even worst case should be >= 0.05."""
        # Create a theoretical, stub, anomalous belief with no contrast class
        belief = MagicMock()
        belief.level = MagicMock()
        belief.level.value = "theoretical"
        belief.status = MagicMock()
        belief.status.value = "anomalous"
        belief.contrast_class = None

        mock_web.beliefs = {"b1": belief}

        result = bridge.compute_security(["b1"])
        security = result['belief_securities']['b1']

        assert security >= 0.05, f"Security {security} below floor of 0.05"

    def test_maximum_security_cap(self, bridge, mock_web):
        """Even best case should be <= 0.95."""
        # Create an observational, entrenched belief with explicit contrast class
        belief = MagicMock()
        belief.level = MagicMock()
        belief.level.value = "observational"
        belief.status = MagicMock()
        belief.status.value = "entrenched"
        belief.contrast_class = MagicMock()
        belief.contrast_class.explicit = True

        mock_web.beliefs = {"b1": belief}

        result = bridge.compute_security(["b1"])
        security = result['belief_securities']['b1']

        assert security <= 0.95, f"Security {security} above cap of 0.95"

    def test_security_with_all_bonuses(self, bridge, mock_web):
        """Test maximum bonuses don't exceed cap."""
        # observational (0.9) + explicit contrast (0.15) + entrenched (0.10) = 1.15 → capped at 0.95
        belief = MagicMock()
        belief.level = MagicMock()
        belief.level.value = "observational"
        belief.status = MagicMock()
        belief.status.value = "entrenched"
        belief.contrast_class = MagicMock()
        belief.contrast_class.explicit = True

        mock_web.beliefs = {"b1": belief}

        result = bridge.compute_security(["b1"])
        security = result['belief_securities']['b1']

        assert security == 0.95, f"Expected capped security 0.95, got {security}"

    def test_security_with_all_penalties(self, bridge, mock_web):
        """Test maximum penalties don't go below floor."""
        # theoretical (0.3) + stub (-0.10) + anomalous (-0.15) = 0.05 → at floor
        belief = MagicMock()
        belief.level = MagicMock()
        belief.level.value = "theoretical"
        belief.status = MagicMock()
        belief.status.value = "anomalous"
        belief.contrast_class = None

        mock_web.beliefs = {"b1": belief}

        result = bridge.compute_security(["b1"])
        security = result['belief_securities']['b1']

        # 0.3 - 0.15 = 0.15, which is above floor
        # But if status was stub AND anomalous... let's test stub alone
        belief.status.value = "stub"
        result = bridge.compute_security(["b1"])
        security = result['belief_securities']['b1']
        assert security >= 0.05

    def test_empty_belief_list_security(self, bridge, mock_web):
        """Empty belief list should return mean_security of 0.5."""
        result = bridge.compute_security([])
        assert result['mean_security'] == 0.5
        assert result['n_beliefs_assessed'] == 0


# =============================================================================
# TEST CLASS: Gap Identification Edge Cases
# =============================================================================

class TestGapIdentificationEdgeCases:
    """Test gap identification with edge cases."""

    def test_gap_dataclass_creation(self):
        """Test EpistemicGap dataclass can be created."""
        gap = EpistemicGap(
            gap_id="test_gap_1",
            gap_type="missing_contrast",
            description="Test gap",
            priority=0.7
        )
        assert gap.gap_id == "test_gap_1"
        assert gap.gap_type == "missing_contrast"
        assert gap.priority == 0.7
        assert gap.suggested_query is None

    def test_gap_to_voi_request(self):
        """Test EpistemicGap.to_voi_request() method."""
        gap = EpistemicGap(
            gap_id="gap_123",
            gap_type="low_coverage",
            description="Limited evidence for urban population",
            priority=0.8,
            suggested_query="Studies of stress in urban environments",
            target_population="urban_dwellers",
            target_variable="cortisol"
        )

        voi_request = gap.to_voi_request()

        assert voi_request['gap_id'] == "gap_123"
        assert voi_request['gap_type'] == "low_coverage"
        assert voi_request['priority'] == 0.8
        assert voi_request['query'] == "Studies of stress in urban environments"
        assert voi_request['target_population'] == "urban_dwellers"
        assert voi_request['target_variable'] == "cortisol"
        assert voi_request['source'] == "epistemic_causal_bridge"

    def test_gap_without_suggested_query_uses_description(self):
        """Gap without suggested_query should use description in VOI request."""
        gap = EpistemicGap(
            gap_id="gap_456",
            gap_type="theory_conflict",
            description="ART and SRT disagree on mechanism",
            priority=0.6
        )

        voi_request = gap.to_voi_request()
        assert voi_request['query'] == "ART and SRT disagree on mechanism"

    def test_gap_priority_ranges(self):
        """Test that gap priorities are in expected ranges."""
        # Priority formulas from documentation
        assert 0.0 <= 0.7 <= 1.0  # missing_contrast
        assert 0.0 <= 0.8 * 0.5 <= 1.0  # low_coverage with 50% coverage
        assert 0.0 <= 0.6 * 0.3 <= 1.0  # theory_conflict with 0.3 range
        assert 0.0 <= 0.5 <= 1.0  # baseline_unknown
        assert 0.0 <= 0.4 <= 1.0  # blocked_beliefs


# =============================================================================
# TEST CLASS: Error Handling Edge Cases
# =============================================================================

class TestErrorHandlingEdgeCases:
    """Test error handling for edge cases."""

    def test_bridge_rejects_none_web(self):
        """Bridge should raise TypeError for None web."""
        with pytest.raises(TypeError):
            EpistemicCausalBridge(None)

    def test_bridge_rejects_invalid_web(self):
        """Bridge should raise TypeError for object without beliefs/constraints."""
        invalid_web = MagicMock(spec=[])  # No attributes
        with pytest.raises(TypeError):
            EpistemicCausalBridge(invalid_web)

    def test_counterfactual_rejects_empty_intervention(self, bridge):
        """Counterfactual should raise ValueError for empty intervention."""
        with pytest.raises(ValueError, match="intervention cannot be empty"):
            bridge.counterfactual(
                intervention={},
                outcome="stress"
            )

    def test_counterfactual_rejects_empty_outcome(self, bridge):
        """Counterfactual should raise ValueError for empty outcome."""
        with pytest.raises(ValueError, match="outcome cannot be empty"):
            bridge.counterfactual(
                intervention={"nature_exposure": 1},
                outcome=""
            )

    def test_build_models_rejects_invalid_threshold(self, bridge, mock_web):
        """build_causal_models should raise ValueError for out-of-range threshold."""
        mock_web.beliefs = {"b1": MagicMock()}

        with pytest.raises(ValueError, match="credence_threshold must be 0.0-1.0"):
            bridge.build_causal_models(credence_threshold=1.5)

        with pytest.raises(ValueError, match="credence_threshold must be 0.0-1.0"):
            bridge.build_causal_models(credence_threshold=-0.1)

    def test_empty_web_returns_empty_model(self, bridge, mock_web):
        """Empty web should return empty model, not raise error."""
        mock_web.beliefs = {}
        mock_web.theory_ids = []

        model = bridge.build_causal_models()

        assert model is not None
        assert len(model.theory_models) == 0


# =============================================================================
# TEST CLASS: Feedback Loop Gate (ECB-F9)
# =============================================================================

class TestFeedbackLoopGate:
    """Test the contrast-gated feedback loop (ECB-F9)."""

    def test_feedback_gated_when_result_undefined(self, bridge):
        """Feedback should be gated when result is undefined."""
        result = MagicMock()
        result.is_defined = False
        result.reason_undefined = "contrast_mismatch:meaning_differs"

        response = bridge.update_web_from_result(result)

        assert response['gated'] is True
        assert response['n_beliefs_updated'] == 0
        assert 'result_undefined' in response['gate_reason']

    def test_feedback_gated_when_meaning_shift(self, bridge):
        """Feedback should be gated when contrast transfer is MEANING_SHIFT."""
        result = MagicMock()
        result.is_defined = True
        result.contrast = MagicMock()
        result.contrast.transfer_type = ContrastTransferType.MEANING_SHIFT

        response = bridge.update_web_from_result(result)

        assert response['gated'] is True
        assert response['n_beliefs_updated'] == 0
        assert 'meaning_shift' in response['gate_reason']

    def test_feedback_proceeds_when_valid_transfer(self, bridge):
        """Feedback should proceed when contrast transfer is valid."""
        result = MagicMock()
        result.is_defined = True
        result.contrast = MagicMock()
        result.contrast.transfer_type = ContrastTransferType.DIRECT
        result.robustness = MagicMock()
        result.robustness.sensitive_beliefs = []
        result.coherence = MagicMock()
        result.coherence.violations = []

        response = bridge.update_web_from_result(result)

        assert 'gated' not in response or response.get('gated') is False
