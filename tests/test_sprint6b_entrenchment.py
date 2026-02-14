"""
Tests for Sprint 6b: Entrenchment Dynamics.

Tests the six entrenchment modules:
- Task 6b.1: node_type_entrenchment.py
- Task 6b.2: theory_updating.py
- Task 6b.3: critique_propagation.py
- Task 6b.4: prediction_ledger.py
- Task 6b.5: synthesis_rules.py
- Task 6b.6: expert_discount.py
"""

import pytest
from unittest.mock import MagicMock

# Task 6b.1: Node Type Entrenchment
from src.epistemic.entrenchment.node_type_entrenchment import (
    BASE_ENTRENCHMENT,
    EntrenchmentParams,
    compute_base_entrenchment,
    compute_entrenchment_with_modifiers,
)
from src.epistemic.node_types import NodeType

# Task 6b.2: Theory Updating
from src.epistemic.entrenchment.theory_updating import (
    CONFIRMATION_BONUS,
    DISCONFIRMATION_PENALTY,
    update_theory_entrenchment,
    propagate_to_parent_theory,
    compute_theory_trajectory,
    assess_theory_health,
)

# Task 6b.3: Critique Propagation
from src.epistemic.entrenchment.critique_propagation import (
    CritiquePropagationResult,
    propagate_critique_to_registry,
    record_critique_in_registry,
)

# Task 6b.4: Prediction Ledger
from src.epistemic.entrenchment.prediction_ledger import (
    PredictionLedgerEntry,
    PredictionLedger,
)

# Task 6b.5: Synthesis Rules
from src.epistemic.entrenchment.synthesis_rules import (
    compute_median_entrenchment,
    compute_synthesis_entrenchment,
    assess_synthesis_quality,
    should_trust_synthesis_over_primary,
)

# Task 6b.6: Expert Discount
from src.epistemic.entrenchment.expert_discount import (
    EXPERT_SYNTHESIS_DISCOUNT,
    apply_expert_synthesis_discount,
    compute_expert_synthesis_entrenchment,
    compare_expert_vs_systematic,
    get_recommended_discount,
)


# =============================================================================
# Task 6b.1: Node Type Entrenchment Tests
# =============================================================================

class TestNodeTypeEntrenchment:
    """Test base entrenchment values per node type."""

    def test_base_entrenchment_values_present(self):
        """All 12 node types have base entrenchment values (except KNOWLEDGE_GAP)."""
        for node_type in NodeType:
            assert node_type in BASE_ENTRENCHMENT
            if node_type != NodeType.KNOWLEDGE_GAP:
                assert 0.0 <= BASE_ENTRENCHMENT[node_type] <= 1.0
            else:
                # KNOWLEDGE_GAP doesn't have entrenchment (N/A)
                assert BASE_ENTRENCHMENT[node_type] is None

    def test_empirical_finding_base(self):
        """EMPIRICAL_FINDING has base 0.50 (from source_quality score)."""
        assert BASE_ENTRENCHMENT[NodeType.EMPIRICAL_FINDING] == pytest.approx(0.50)

    def test_synthesis_conclusion_base(self):
        """SYNTHESIS_CONCLUSION has base 0.75."""
        assert BASE_ENTRENCHMENT[NodeType.SYNTHESIS_CONCLUSION] == pytest.approx(0.75)

    def test_theoretical_proposition_base(self):
        """THEORETICAL_PROPOSITION has base 0.35."""
        assert BASE_ENTRENCHMENT[NodeType.THEORETICAL_PROPOSITION] == pytest.approx(0.35)

    def test_compute_base_entrenchment(self):
        """compute_base_entrenchment returns correct values."""
        assert compute_base_entrenchment(NodeType.EMPIRICAL_FINDING) == pytest.approx(0.50)
        assert compute_base_entrenchment(NodeType.EXPERT_SYNTHESIS) == pytest.approx(0.45)
        assert compute_base_entrenchment(NodeType.KNOWLEDGE_GAP) is None

    def test_entrenchment_with_modifiers(self):
        """Modifiers adjust entrenchment correctly."""
        # Test with empirical finding and source_quality + replication
        params = EntrenchmentParams(
            source_quality_score=0.60,
            replication_count=2,
        )
        result = compute_entrenchment_with_modifiers(NodeType.EMPIRICAL_FINDING, params)
        # 0.60 (source) + 0.05*2 (replications) = 0.70
        assert result == pytest.approx(0.70)

    def test_entrenchment_clamped_to_valid_range(self):
        """Entrenchment is clamped to [0, 1]."""
        # High source quality + many replications
        params = EntrenchmentParams(
            source_quality_score=0.95,
            replication_count=5,  # Capped at 3 for +0.15
        )
        result = compute_entrenchment_with_modifiers(NodeType.EMPIRICAL_FINDING, params)
        assert result == 1.0  # Clamped at max

    def test_knowledge_gap_returns_none(self):
        """KNOWLEDGE_GAP returns None for entrenchment."""
        result = compute_entrenchment_with_modifiers(NodeType.KNOWLEDGE_GAP, None)
        assert result is None


# =============================================================================
# Task 6b.2: Theory Updating Tests
# =============================================================================

class TestTheoryUpdating:
    """Test asymmetric Popperian updating."""

    def test_confirmation_bonus_constant(self):
        """CONFIRMATION_BONUS is 0.05."""
        assert CONFIRMATION_BONUS == 0.05

    def test_disconfirmation_penalty_constant(self):
        """DISCONFIRMATION_PENALTY is 0.10 (2x asymmetric)."""
        assert DISCONFIRMATION_PENALTY == 0.10

    def test_update_with_confirmation(self):
        """Confirmation increases entrenchment by 0.05."""
        result = update_theory_entrenchment(0.35, confirmations=1, disconfirmations=0)
        assert result == pytest.approx(0.40)

    def test_update_with_disconfirmation(self):
        """Disconfirmation decreases entrenchment by 0.10."""
        result = update_theory_entrenchment(0.35, confirmations=0, disconfirmations=1)
        assert result == pytest.approx(0.25)

    def test_asymmetric_net_loss(self):
        """Equal confirmations and disconfirmations result in net loss."""
        result = update_theory_entrenchment(0.35, confirmations=1, disconfirmations=1)
        # Net: +0.05 - 0.10 = -0.05
        assert result == pytest.approx(0.30)

    def test_update_clamped_to_valid_range(self):
        """Results are clamped to [0, 1]."""
        # Many disconfirmations
        result = update_theory_entrenchment(0.15, confirmations=0, disconfirmations=5)
        assert result == 0.0

        # Many confirmations
        result = update_theory_entrenchment(0.90, confirmations=5, disconfirmations=0)
        assert result == 1.0

    def test_propagate_to_parent_confirmed(self):
        """Parent theory gains from child confirmation."""
        result = propagate_to_parent_theory(0.35, child_confirmed=True)
        assert result == pytest.approx(0.40)

    def test_propagate_to_parent_disconfirmed(self):
        """Parent theory loses (damped) from child disconfirmation."""
        result = propagate_to_parent_theory(0.35, child_confirmed=False)
        # Damped penalty: 0.10 * 0.5 = 0.05
        assert result == pytest.approx(0.30)

    def test_compute_theory_trajectory(self):
        """Trajectory shows entrenchment evolution."""
        history = [True, True, False, True]  # 3 confirm, 1 disconfirm
        trajectory = compute_theory_trajectory(0.35, history)
        assert len(trajectory) == 5  # Initial + 4 events
        assert trajectory[0] == 0.35
        assert trajectory[-1] == pytest.approx(0.35 + 3*0.05 - 1*0.10)

    def test_assess_theory_health_well_supported(self):
        """High success rate with high entrenchment is well_supported."""
        status, _ = assess_theory_health(0.60, confirmations=8, disconfirmations=2)
        assert status == "well_supported"

    def test_assess_theory_health_untested(self):
        """No tests means untested status."""
        status, _ = assess_theory_health(0.35, confirmations=0, disconfirmations=0)
        assert status == "untested"


# =============================================================================
# Task 6b.3: Critique Propagation Tests
# =============================================================================

class TestCritiquePropagation:
    """Test methodological critique propagation."""

    def test_propagate_critique_updates_validity(self):
        """Critique propagates to method registry and reduces validity."""
        # Mock registry and method
        mock_method = MagicMock()
        mock_method.get_construct_validity = MagicMock(return_value=0.8)
        mock_method.construct_validity_map = {"stress": 0.8, "attention": 0.7}

        mock_registry = MagicMock()
        mock_registry.get = MagicMock(return_value=mock_method)

        result = propagate_critique_to_registry(
            critique_target_method_id="hrv_measurement",
            critique_severity=0.6,
            affected_constructs=["stress"],
            registry=mock_registry,
            penalty_scale=0.2
        )

        assert result is not None
        assert result.method_id == "hrv_measurement"
        assert result.penalty_applied == pytest.approx(0.12)  # 0.6 * 0.2
        assert "stress" in result.affected_constructs

    def test_propagate_critique_method_not_found(self):
        """Returns None if method not in registry."""
        mock_registry = MagicMock()
        mock_registry.get = MagicMock(return_value=None)

        result = propagate_critique_to_registry(
            critique_target_method_id="nonexistent",
            critique_severity=0.5,
            affected_constructs=["stress"],
            registry=mock_registry
        )

        assert result is None

    def test_record_critique_in_registry(self):
        """Critique is recorded in method's confounds list."""
        mock_method = MagicMock()
        mock_method.confounds = []

        mock_registry = MagicMock()
        mock_registry.get = MagicMock(return_value=mock_method)

        success = record_critique_in_registry(
            critique_target_method_id="photo_preference",
            critique_description="Cannot assess physiological response",
            registry=mock_registry,
            severity=0.7
        )

        assert success
        assert len(mock_method.confounds) == 1
        assert "CRITIQUE:" in mock_method.confounds[0]


# =============================================================================
# Task 6b.4: Prediction Ledger Tests
# =============================================================================

class TestPredictionLedger:
    """Test prediction tracking ledger."""

    def test_ledger_entry_creation(self):
        """PredictionLedgerEntry initializes correctly."""
        entry = PredictionLedgerEntry(
            hypothesis_id="kaplan_1995_h3",
            hypothesis_text="Exposure to natural settings restores directed attention",
            derived_from="kaplan_1995_prop2"
        )
        assert entry.hypothesis_id == "kaplan_1995_h3"
        assert entry.current_entrenchment == pytest.approx(0.35)
        assert entry.confirmation_count == 0
        assert entry.disconfirmation_count == 0

    def test_add_confirmation(self):
        """Adding confirmation updates entrenchment."""
        entry = PredictionLedgerEntry(
            hypothesis_id="h1",
            hypothesis_text="Test hypothesis",
            derived_from="theory1"
        )
        initial = entry.current_entrenchment
        entry.add_confirmation("study_1")
        assert entry.confirmation_count == 1
        assert entry.current_entrenchment > initial

    def test_add_disconfirmation(self):
        """Adding disconfirmation updates entrenchment."""
        entry = PredictionLedgerEntry(
            hypothesis_id="h1",
            hypothesis_text="Test hypothesis",
            derived_from="theory1"
        )
        initial = entry.current_entrenchment
        entry.add_disconfirmation("study_1")
        assert entry.disconfirmation_count == 1
        assert entry.current_entrenchment < initial

    def test_ledger_register_and_retrieve(self):
        """Ledger can register and retrieve hypotheses."""
        ledger = PredictionLedger()
        entry = ledger.register_hypothesis(
            hypothesis_id="h1",
            text="Test hypothesis",
            parent_prop_id="theory1"
        )
        assert ledger.count() == 1
        assert ledger.get_entry("h1") == entry

    def test_ledger_record_confirmation(self):
        """Ledger records confirmations for hypotheses."""
        ledger = PredictionLedger()
        ledger.register_hypothesis("h1", "Test", "theory1")
        success = ledger.record_confirmation("h1", "study_1")
        assert success
        assert ledger.get_entry("h1").confirmation_count == 1

    def test_ledger_theory_track_record(self):
        """Ledger computes theory track record."""
        ledger = PredictionLedger()
        ledger.register_hypothesis("h1", "Hyp 1", "theory1")
        ledger.register_hypothesis("h2", "Hyp 2", "theory1")
        ledger.record_confirmation("h1", "study_1")
        ledger.record_confirmation("h1", "study_2")
        ledger.record_disconfirmation("h2", "study_3")

        record = ledger.compute_theory_track_record("theory1")
        assert record["hypothesis_count"] == 2
        assert record["total_confirmations"] == 2
        assert record["total_disconfirmations"] == 1
        assert record["success_rate"] == pytest.approx(2/3)

    def test_ledger_serialization(self):
        """Ledger can serialize and deserialize."""
        ledger = PredictionLedger()
        ledger.register_hypothesis("h1", "Test", "theory1")
        ledger.record_confirmation("h1", "study_1")

        data = ledger.to_dict()
        restored = PredictionLedger.from_dict(data)

        assert restored.count() == 1
        assert restored.get_entry("h1").confirmation_count == 1


# =============================================================================
# Task 6b.5: Synthesis Rules Tests
# =============================================================================

class TestSynthesisRules:
    """Test SYNTHESIS_CONCLUSION floor rule."""

    def test_compute_median_odd_count(self):
        """Median of odd-count list is middle element."""
        values = [0.3, 0.4, 0.5, 0.6, 0.7]
        assert compute_median_entrenchment(values) == pytest.approx(0.5)

    def test_compute_median_even_count(self):
        """Median of even-count list is average of middle two."""
        values = [0.3, 0.4, 0.6, 0.7]
        assert compute_median_entrenchment(values) == pytest.approx(0.5)

    def test_compute_median_empty(self):
        """Median of empty list is None."""
        assert compute_median_entrenchment([]) is None

    def test_floor_rule_applied(self):
        """Synthesis entrenchment >= median of included studies."""
        included = [0.3, 0.4, 0.5, 0.6, 0.7]  # median = 0.5
        result = compute_synthesis_entrenchment(
            base_entrenchment=0.40,
            included_study_entrenchments=included
        )
        # Floor kicks in: 0.40 < 0.5 (median), so result = 0.5
        assert result == pytest.approx(0.5)

    def test_no_floor_when_base_higher(self):
        """Floor doesn't apply when base > median."""
        included = [0.3, 0.4, 0.5, 0.6, 0.7]  # median = 0.5
        result = compute_synthesis_entrenchment(
            base_entrenchment=0.75,
            included_study_entrenchments=included
        )
        # Base is higher than median, use base (with any modifiers)
        assert result >= 0.5

    def test_heterogeneity_penalty(self):
        """High heterogeneity reduces entrenchment."""
        result_low = compute_synthesis_entrenchment(
            base_entrenchment=0.75,
            included_study_entrenchments=[],
            heterogeneity_i2=25.0
        )
        result_high = compute_synthesis_entrenchment(
            base_entrenchment=0.75,
            included_study_entrenchments=[],
            heterogeneity_i2=80.0
        )
        assert result_high < result_low

    def test_publication_bias_penalty(self):
        """Significant publication bias reduces entrenchment."""
        result_none = compute_synthesis_entrenchment(
            base_entrenchment=0.75,
            included_study_entrenchments=[],
            publication_bias="none"
        )
        result_sig = compute_synthesis_entrenchment(
            base_entrenchment=0.75,
            included_study_entrenchments=[],
            publication_bias="significant"
        )
        assert result_sig < result_none

    def test_assess_synthesis_quality(self):
        """Quality assessment detects issues."""
        assessment = assess_synthesis_quality(
            heterogeneity_i2=85.0,
            publication_bias="significant",
            n_studies=3
        )
        assert assessment["rating"] in ["low", "very_low"]
        assert len(assessment["issues"]) > 0

    def test_should_trust_synthesis_over_primary(self):
        """Synthesis with many studies preferred over single study."""
        assert should_trust_synthesis_over_primary(
            synthesis_entrenchment=0.60,
            primary_study_entrenchment=0.55,
            synthesis_n_studies=10
        ) is True


# =============================================================================
# Task 6b.6: Expert Discount Tests
# =============================================================================

class TestExpertDiscount:
    """Test EXPERT_SYNTHESIS discount factor."""

    def test_discount_constant(self):
        """EXPERT_SYNTHESIS_DISCOUNT is 0.7."""
        assert EXPERT_SYNTHESIS_DISCOUNT == 0.7

    def test_apply_discount(self):
        """Discount reduces entrenchment by factor."""
        result = apply_expert_synthesis_discount(0.70)
        assert result == pytest.approx(0.49)  # 0.70 * 0.7

    def test_apply_custom_discount(self):
        """Custom discount factor can be applied."""
        result = apply_expert_synthesis_discount(0.80, discount_factor=0.5)
        assert result == pytest.approx(0.40)

    def test_compute_expert_entrenchment_established(self):
        """Established author gets higher entrenchment."""
        est = compute_expert_synthesis_entrenchment(author_expertise="established")
        unk = compute_expert_synthesis_entrenchment(author_expertise="unknown")
        assert est > unk

    def test_compute_expert_entrenchment_consistent(self):
        """Consistency with systematic reviews increases entrenchment."""
        con = compute_expert_synthesis_entrenchment(consistent_with_systematic=True)
        not_con = compute_expert_synthesis_entrenchment(consistent_with_systematic=False)
        assert con > not_con

    def test_compare_expert_vs_systematic_same_conclusion(self):
        """Comparison when reaching same conclusion."""
        # Use values that clearly result in ratio < 0.7
        result = compare_expert_vs_systematic(
            expert_entrenchment=0.48,  # 0.48 / 0.70 = 0.6857... < 0.7
            systematic_entrenchment=0.70,
            same_conclusion=True
        )
        # The ratio is below 0.7, which satisfies ratio <= 0.7
        assert result["status"] == "appropriate_discount"
        assert result["ratio"] == pytest.approx(0.48 / 0.70, abs=0.01)

    def test_compare_expert_vs_systematic_overweighted(self):
        """Detects when expert is overweighted."""
        result = compare_expert_vs_systematic(
            expert_entrenchment=0.60,
            systematic_entrenchment=0.70,
            same_conclusion=True
        )
        assert result["status"] == "expert_overweighted"

    def test_get_recommended_discount_field_consensus(self):
        """Field consensus affects recommended discount."""
        weak = get_recommended_discount("unknown", field_consensus="weak")
        strong = get_recommended_discount("unknown", field_consensus="strong")
        assert weak > strong  # Less discount when consensus is weak
