"""
Tests for Sprint 8: Multi-Theory Handling & Validation Infrastructure.

This module tests:
1. Validation phases and gates
2. Ecological validity classification
3. LOO metrics computation
4. Evidence cluster handling
5. Stratified validation reports

Per expert panel consensus: Progressive validation as corpus grows.
"""

import pytest
from src.services.validation import (
    ValidationPhase,
    ValidationGate,
    VALIDATION_GATES,
    check_validation_eligibility,
    EcologicalValidity,
    ECOLOGICAL_VALIDITY_WEIGHTS,
    get_validity_weight,
    infer_ecological_validity,
    PredictionMode,
    LOOMetrics,
    StratifiedLOOReport,
    compute_loo_metrics,
    ValidationReport,
    PASS_THRESHOLDS,
    check_validation_passed,
    compute_mean_constraint_degree,
    # Panel Fix 2: Coherence contribution
    compute_coherence_contribution,
    assess_theoretical_belief_coherence,
    BeliefCoherenceAssessment,
)

from src.services.web_persistence import WebPersistenceService
from src.services.web_of_belief import (
    Belief,
    Credence,
    EpistemicLevel,
    BeliefStatus,
    ConstraintType,
)
from src.services.bridge_warrants import BridgeType


class TestValidationPhases:
    """Test Case 1: Validation phases and gates."""

    def test_all_phases_defined(self):
        """Verify all validation phases exist."""
        assert ValidationPhase.PHASE_1_ANNOTATION.value == "annotation"
        assert ValidationPhase.PHASE_2_CALIBRATION.value == "calibration"
        assert ValidationPhase.PHASE_3_LOO.value == "loo"
        assert ValidationPhase.PHASE_4_BRIDGES.value == "bridges"

    def test_gates_for_all_phases(self):
        """Verify gates exist for all phases."""
        for phase in ValidationPhase:
            assert phase in VALIDATION_GATES
            gate = VALIDATION_GATES[phase]
            assert gate.min_papers > 0

    def test_gate_requirements_increase(self):
        """Verify later phases have stricter requirements."""
        phases = [
            ValidationPhase.PHASE_1_ANNOTATION,
            ValidationPhase.PHASE_2_CALIBRATION,
            ValidationPhase.PHASE_3_LOO,
            ValidationPhase.PHASE_4_BRIDGES,
        ]

        for i in range(len(phases) - 1):
            current_gate = VALIDATION_GATES[phases[i]]
            next_gate = VALIDATION_GATES[phases[i + 1]]

            # Later phases should require more papers
            assert next_gate.min_papers >= current_gate.min_papers
            # Later phases should require better connectivity
            assert next_gate.min_connectivity >= current_gate.min_connectivity

    def test_gate_check_pass(self):
        """Verify gate check passes when requirements met."""
        gate = VALIDATION_GATES[ValidationPhase.PHASE_1_ANNOTATION]

        # Meet all requirements
        assert gate.check(n_papers=10, connectivity=0.0, lcc_fraction=0.0) is True
        assert gate.check(n_papers=15, connectivity=1.0, lcc_fraction=0.5) is True

    def test_gate_check_fail_papers(self):
        """Verify gate check fails with insufficient papers."""
        gate = VALIDATION_GATES[ValidationPhase.PHASE_1_ANNOTATION]

        # Too few papers
        assert gate.check(n_papers=5, connectivity=0.0, lcc_fraction=0.0) is False

    def test_check_validation_eligibility(self):
        """Verify eligibility check returns correct phases."""
        # Small corpus - only Phase 1
        eligible = check_validation_eligibility(
            n_papers=10,
            mean_constraint_degree=0.0,
            lcc_fraction=0.0
        )
        assert ValidationPhase.PHASE_1_ANNOTATION in eligible
        assert ValidationPhase.PHASE_3_LOO not in eligible

    def test_check_validation_eligibility_large_corpus(self):
        """Verify large corpus is eligible for all phases."""
        eligible = check_validation_eligibility(
            n_papers=100,
            mean_constraint_degree=3.0,
            lcc_fraction=0.9
        )
        assert len(eligible) == 4
        for phase in ValidationPhase:
            assert phase in eligible


class TestEcologicalValidity:
    """Test Case 2: Ecological validity classification."""

    def test_all_validity_levels_defined(self):
        """Verify all ecological validity levels exist."""
        assert EcologicalValidity.FIELD_NATURAL.value == "field_natural"
        assert EcologicalValidity.FIELD_STRUCTURED.value == "field_structured"
        assert EcologicalValidity.LAB_VR.value == "lab_vr"
        assert EcologicalValidity.LAB_VIDEO.value == "lab_video"
        assert EcologicalValidity.LAB_PHOTOS.value == "lab_photos"
        assert EcologicalValidity.LAB_ABSTRACT.value == "lab_abstract"

    def test_validity_weights_descending(self):
        """Verify field studies have higher weights than lab."""
        assert ECOLOGICAL_VALIDITY_WEIGHTS[EcologicalValidity.FIELD_NATURAL] == 1.0
        assert ECOLOGICAL_VALIDITY_WEIGHTS[EcologicalValidity.FIELD_STRUCTURED] < 1.0
        assert ECOLOGICAL_VALIDITY_WEIGHTS[EcologicalValidity.LAB_VR] < ECOLOGICAL_VALIDITY_WEIGHTS[EcologicalValidity.FIELD_STRUCTURED]
        assert ECOLOGICAL_VALIDITY_WEIGHTS[EcologicalValidity.LAB_PHOTOS] < ECOLOGICAL_VALIDITY_WEIGHTS[EcologicalValidity.LAB_VR]
        assert ECOLOGICAL_VALIDITY_WEIGHTS[EcologicalValidity.LAB_ABSTRACT] < ECOLOGICAL_VALIDITY_WEIGHTS[EcologicalValidity.LAB_PHOTOS]

    def test_vr_vs_video_distinction(self):
        """Verify VR is weighted higher than video (Sprint 8.4 distinction)."""
        vr_weight = ECOLOGICAL_VALIDITY_WEIGHTS[EcologicalValidity.LAB_VR]
        video_weight = ECOLOGICAL_VALIDITY_WEIGHTS[EcologicalValidity.LAB_VIDEO]
        assert vr_weight > video_weight

    def test_get_validity_weight(self):
        """Verify weight retrieval works."""
        assert get_validity_weight(EcologicalValidity.FIELD_NATURAL) == 1.0
        assert get_validity_weight(EcologicalValidity.LAB_ABSTRACT) == 0.5

    def test_infer_ecological_validity_field(self):
        """Verify field study inference."""
        text = "A naturalistic field study in a real forest environment"
        validity = infer_ecological_validity(text)
        assert validity == EcologicalValidity.FIELD_NATURAL

    def test_infer_ecological_validity_vr(self):
        """Verify VR study inference."""
        text = "Participants wore VR headsets and explored the virtual environment"
        validity = infer_ecological_validity(text)
        assert validity == EcologicalValidity.LAB_VR

    def test_infer_ecological_validity_video(self):
        """Verify video study inference."""
        text = "Participants watched a video walkthrough of the building"
        validity = infer_ecological_validity(text)
        assert validity == EcologicalValidity.LAB_VIDEO

    def test_infer_ecological_validity_photos(self):
        """Verify photo study inference."""
        text = "Participants rated images of different environments"
        validity = infer_ecological_validity(text)
        assert validity == EcologicalValidity.LAB_PHOTOS

    def test_infer_ecological_validity_abstract(self):
        """Verify abstract study defaults to lab abstract."""
        text = "Participants completed a cognitive task"
        validity = infer_ecological_validity(text)
        assert validity == EcologicalValidity.LAB_ABSTRACT

    def test_get_uncertainty_factor_field_natural(self):
        """
        Panel Fix 5 (Kaplan): Field natural has no uncertainty increase.
        Factor should be 1.0.
        """
        from src.services.validation import get_uncertainty_factor

        factor = get_uncertainty_factor(EcologicalValidity.FIELD_NATURAL)
        assert factor == 1.0

    def test_get_uncertainty_factor_lab_photos(self):
        """
        Panel Fix 5 (Kaplan): LAB_PHOTOS (0.65) → 1/0.65 ≈ 1.54 factor.
        """
        from src.services.validation import get_uncertainty_factor

        factor = get_uncertainty_factor(EcologicalValidity.LAB_PHOTOS)
        assert 1.53 < factor < 1.55  # 1/0.65 ≈ 1.538

    def test_get_uncertainty_factor_lab_abstract(self):
        """
        Panel Fix 5 (Kaplan): LAB_ABSTRACT (0.50) → 1/0.50 = 2.0 factor.
        This is the highest uncertainty increase.
        """
        from src.services.validation import get_uncertainty_factor

        factor = get_uncertainty_factor(EcologicalValidity.LAB_ABSTRACT)
        assert factor == 2.0

    def test_apply_ecological_validity_preserves_credence_value(self):
        """
        Panel Fix 5 (Kaplan): Ecological validity should NOT change credence value.
        Only uncertainty should be affected.
        """
        from src.services.validation import apply_ecological_validity_to_credence

        credence_value = 0.7
        credence_uncertainty = 0.2

        # Apply LAB_PHOTOS validity
        new_value, new_uncertainty = apply_ecological_validity_to_credence(
            credence_value, credence_uncertainty, EcologicalValidity.LAB_PHOTOS
        )

        # Value should be UNCHANGED
        assert new_value == 0.7

        # Uncertainty should be INCREASED by factor 1/0.65 ≈ 1.54
        expected_uncertainty = 0.2 * (1 / 0.65)
        assert abs(new_uncertainty - expected_uncertainty) < 0.01

    def test_apply_ecological_validity_uncertainty_capped_at_one(self):
        """
        Panel Fix 5: Uncertainty should be capped at 1.0 even with high factors.
        """
        from src.services.validation import apply_ecological_validity_to_credence

        credence_value = 0.6
        credence_uncertainty = 0.7  # Already high

        # Apply LAB_ABSTRACT (2x factor)
        new_value, new_uncertainty = apply_ecological_validity_to_credence(
            credence_value, credence_uncertainty, EcologicalValidity.LAB_ABSTRACT
        )

        # Value unchanged
        assert new_value == 0.6

        # Uncertainty would be 1.4, but capped at 1.0
        assert new_uncertainty == 1.0

    def test_apply_ecological_validity_field_natural_no_change(self):
        """
        Panel Fix 5: FIELD_NATURAL has factor 1.0, so no change to uncertainty.
        """
        from src.services.validation import apply_ecological_validity_to_credence

        credence_value = 0.75
        credence_uncertainty = 0.15

        new_value, new_uncertainty = apply_ecological_validity_to_credence(
            credence_value, credence_uncertainty, EcologicalValidity.FIELD_NATURAL
        )

        assert new_value == 0.75
        assert new_uncertainty == 0.15


class TestLOOMetrics:
    """Test Case 3: Leave-one-out metrics computation."""

    def test_compute_loo_metrics_perfect(self):
        """Verify metrics for perfect predictions."""
        predictions = [0.5, 0.6, 0.7]
        actuals = [0.5, 0.6, 0.7]
        uncertainties = [0.1, 0.1, 0.1]
        modes = ["DIRECT", "DIRECT", "CONSTRAINED"]

        metrics = compute_loo_metrics(predictions, actuals, uncertainties, modes)

        assert metrics.mae == 0.0
        assert metrics.rmse == 0.0
        assert metrics.in_range_rate == 1.0
        assert metrics.n_predictions == 3

    def test_compute_loo_metrics_errors(self):
        """Verify metrics with prediction errors."""
        predictions = [0.5, 0.6, 0.7]
        actuals = [0.6, 0.7, 0.8]  # All off by 0.1
        uncertainties = [0.05, 0.05, 0.05]  # Tight uncertainties
        modes = ["DIRECT"] * 3

        metrics = compute_loo_metrics(predictions, actuals, uncertainties, modes)

        assert metrics.mae == pytest.approx(0.1, rel=0.01)
        assert metrics.rmse == pytest.approx(0.1, rel=0.01)
        assert metrics.in_range_rate == 0.0  # All outside uncertainty

    def test_compute_loo_metrics_mode_counts(self):
        """Verify mode distribution is tracked."""
        predictions = [0.5] * 10
        actuals = [0.5] * 10
        uncertainties = [0.1] * 10
        modes = ["DIRECT"] * 5 + ["CONSTRAINED"] * 3 + ["NOVEL"] * 2

        metrics = compute_loo_metrics(predictions, actuals, uncertainties, modes)

        assert metrics.mode_counts["DIRECT"] == 5
        assert metrics.mode_counts["CONSTRAINED"] == 3
        assert metrics.mode_counts["NOVEL"] == 2

    def test_compute_loo_metrics_empty(self):
        """Verify metrics handle empty input."""
        metrics = compute_loo_metrics([], [], [], [])

        assert metrics.mae == 0.0
        assert metrics.n_predictions == 0


class TestStratifiedLOOReport:
    """Test Case 4: Stratified LOO reporting."""

    def test_stratified_loo_report_creation(self):
        """Verify stratified report can be created."""
        overall = LOOMetrics(mae=0.1, rmse=0.15, in_range_rate=0.8, n_predictions=100)

        report = StratifiedLOOReport(
            overall=overall,
            by_theory={"ART": LOOMetrics(mae=0.08, rmse=0.12, in_range_rate=0.85, n_predictions=50)},
            single_theory_papers=LOOMetrics(mae=0.1, rmse=0.15, in_range_rate=0.8, n_predictions=60),
            multi_theory_papers=LOOMetrics(mae=0.12, rmse=0.18, in_range_rate=0.75, n_predictions=40)
        )

        assert report.overall.mae == 0.1
        assert "ART" in report.by_theory
        assert report.single_theory_papers is not None

    def test_stratified_loo_report_to_dict(self):
        """Verify report serializes correctly."""
        overall = LOOMetrics(mae=0.1, rmse=0.15, in_range_rate=0.8, n_predictions=100)
        report = StratifiedLOOReport(overall=overall)

        d = report.to_dict()

        assert 'overall' in d
        assert d['overall']['mae'] == 0.1


class TestEvidenceCluster:
    """Test Case 5: Evidence cluster handling (Sprint 8.1)."""

    def test_shared_evidence_constraint_type_exists(self):
        """Verify SHARED_EVIDENCE constraint type exists."""
        assert ConstraintType.SHARED_EVIDENCE.value == "shared_evidence"

    def test_empirical_covariance_bridge_type_exists(self):
        """Verify EMPIRICAL_ASSOCIATION (formerly EMPIRICAL_COVARIANCE) bridge type exists."""
        # Renamed: EMPIRICAL_COVARIANCE → EMPIRICAL_ASSOCIATION (RV5 BridgeType fix)
        assert BridgeType.EMPIRICAL_ASSOCIATION.value == "empirical_association"

    def test_cluster_aware_merge_same_cluster(self):
        """Verify same-cluster beliefs don't double-count."""
        service = WebPersistenceService(":memory:")

        b1 = Belief(
            belief_id="cluster:001:a",
            content="Nature reduces stress",
            level=EpistemicLevel.EMPIRICAL,
            status=BeliefStatus.TENTATIVE,
            credence=Credence(0.7, 0.2, n_observations=50),
            evidence_cluster_id="cluster:paper_123"
        )

        b2 = Belief(
            belief_id="cluster:001:b",
            content="Nature reduces stress",
            level=EpistemicLevel.EMPIRICAL,
            status=BeliefStatus.TENTATIVE,
            credence=Credence(0.8, 0.15, n_observations=50),
            evidence_cluster_id="cluster:paper_123"  # Same cluster!
        )

        merged = service._merge_credences_cluster_aware(b1, b2)

        # Should NOT sum observations (would be double-counting)
        assert merged.n_observations == 50  # Not 100
        # Uncertainty should NOT decrease
        assert merged.uncertainty >= 0.15  # Max of the two uncertainties

    def test_cluster_aware_merge_different_clusters(self):
        """Verify different-cluster beliefs get normal merge."""
        service = WebPersistenceService(":memory:")

        b1 = Belief(
            belief_id="cluster:001",
            content="Nature reduces stress",
            level=EpistemicLevel.EMPIRICAL,
            status=BeliefStatus.TENTATIVE,
            credence=Credence(0.7, 0.2, n_observations=50),
            evidence_cluster_id="cluster:paper_123"
        )

        b2 = Belief(
            belief_id="cluster:002",
            content="Nature reduces stress",
            level=EpistemicLevel.EMPIRICAL,
            status=BeliefStatus.TENTATIVE,
            credence=Credence(0.8, 0.15, n_observations=50),
            evidence_cluster_id="cluster:paper_456"  # Different cluster
        )

        merged = service._merge_credences_cluster_aware(b1, b2)

        # Should sum observations (different studies)
        assert merged.n_observations == 100
        # Uncertainty should decrease (more evidence)
        assert merged.uncertainty < 0.2


class TestValidationReport:
    """Test Case 6: Validation report and pass checking."""

    def test_validation_report_creation(self):
        """Verify validation report can be created."""
        report = ValidationReport(
            belief_f1=0.75,
            belief_recall=0.8,
            belief_precision=0.71,
            credence_in_range=0.8,
            f1_by_level={"empirical": 0.8, "intermediate": 0.7, "theoretical": 0.6},
            corpus_version="v1.0",
            statistical_power="sufficient"
        )

        assert report.belief_f1 == 0.75
        assert report.f1_by_level["empirical"] == 0.8

    def test_check_validation_passed_success(self):
        """Verify passing report is detected."""
        report = ValidationReport(
            belief_f1=0.75,
            credence_in_range=0.8,
            f1_by_level={"empirical": 0.8, "intermediate": 0.7, "theoretical": 0.6},
            should_not_extract_violations=0
        )

        assert check_validation_passed(report) is True

    def test_check_validation_passed_low_f1(self):
        """Verify low F1 causes failure."""
        report = ValidationReport(
            belief_f1=0.5,  # Below threshold
            credence_in_range=0.8,
            f1_by_level={"empirical": 0.8, "intermediate": 0.7, "theoretical": 0.6},
            should_not_extract_violations=0
        )

        assert check_validation_passed(report) is False

    def test_check_validation_passed_violations(self):
        """Verify should_not_extract violations cause failure."""
        report = ValidationReport(
            belief_f1=0.75,
            credence_in_range=0.8,
            f1_by_level={"empirical": 0.8, "intermediate": 0.7, "theoretical": 0.6},
            should_not_extract_violations=1  # Has violations
        )

        assert check_validation_passed(report) is False

    def test_validation_report_to_dict(self):
        """Verify report serializes correctly."""
        report = ValidationReport(
            belief_f1=0.75,
            phases_passed=[ValidationPhase.PHASE_1_ANNOTATION]
        )

        d = report.to_dict()

        assert d['belief_f1'] == 0.75
        assert 'annotation' in d['phases_passed']


class TestMeanConstraintDegree:
    """Test utility function for constraint degree computation."""

    def test_compute_mean_constraint_degree(self):
        """Verify mean constraint degree calculation."""
        # 10 beliefs, 15 constraints
        # Each constraint connects 2 beliefs, so degree = (2 * 15) / 10 = 3.0
        degree = compute_mean_constraint_degree(n_beliefs=10, n_constraints=15)
        assert degree == 3.0

    def test_compute_mean_constraint_degree_empty(self):
        """Verify empty case returns zero."""
        degree = compute_mean_constraint_degree(n_beliefs=0, n_constraints=0)
        assert degree == 0.0


class TestCoherenceContribution:
    """
    Test Case 7: Coherence contribution assessment (Panel Fix 2).

    Per expert panel (Simon): Theoretical beliefs with low coherence contribution
    should be flagged for review, even if they pass F1 thresholds.
    """

    def test_compute_coherence_high(self):
        """Verify HIGH coherence for well-supported beliefs."""
        contribution = compute_coherence_contribution(
            n_supporting=5,
            n_contradicting=0,
            mean_strength=0.75,
            consistency_with_empirical=0.8
        )
        assert contribution == "high"

    def test_compute_coherence_medium(self):
        """Verify MEDIUM coherence for moderately supported beliefs."""
        contribution = compute_coherence_contribution(
            n_supporting=2,
            n_contradicting=0,
            mean_strength=0.5,
            consistency_with_empirical=0.7
        )
        assert contribution == "medium"

    def test_compute_coherence_low_no_support(self):
        """Verify LOW coherence for isolated beliefs (no support)."""
        contribution = compute_coherence_contribution(
            n_supporting=0,
            n_contradicting=0,
            mean_strength=0.0,
            consistency_with_empirical=None
        )
        assert contribution == "low"

    def test_compute_coherence_low_more_contradicting(self):
        """Verify LOW coherence when contradicting > supporting."""
        contribution = compute_coherence_contribution(
            n_supporting=2,
            n_contradicting=5,
            mean_strength=0.6,
            consistency_with_empirical=0.8
        )
        assert contribution == "low"

    def test_compute_coherence_low_inconsistent_with_empirical(self):
        """Verify LOW coherence when inconsistent with empirical findings."""
        contribution = compute_coherence_contribution(
            n_supporting=3,
            n_contradicting=0,
            mean_strength=0.7,
            consistency_with_empirical=0.3  # Low consistency
        )
        assert contribution == "low"

    def test_assess_theoretical_belief_with_flags(self):
        """Verify assessment generates appropriate flags for low-coherence beliefs."""
        assessment = assess_theoretical_belief_coherence(
            belief_id="theory:001",
            n_supporting=0,
            n_contradicting=2,
            mean_strength=0.0,
            consistency_with_empirical=None
        )

        assert assessment.coherence_contribution == "low"
        assert "LOW_COHERENCE_THEORETICAL" in assessment.flags
        assert "ISOLATED_NO_SUPPORT" in assessment.flags

    def test_assess_theoretical_belief_high_no_flags(self):
        """Verify high-coherence beliefs have no warning flags."""
        assessment = assess_theoretical_belief_coherence(
            belief_id="theory:002",
            n_supporting=5,
            n_contradicting=1,
            mean_strength=0.7,
            consistency_with_empirical=0.85
        )

        assert assessment.coherence_contribution == "high"
        assert len(assessment.flags) == 0

    def test_belief_coherence_assessment_to_dict(self):
        """Verify assessment serializes correctly."""
        assessment = assess_theoretical_belief_coherence(
            belief_id="theory:003",
            n_supporting=2,
            n_contradicting=0,
            mean_strength=0.55,
            consistency_with_empirical=0.65
        )

        d = assessment.to_dict()

        assert d['belief_id'] == "theory:003"
        assert d['coherence_contribution'] in ["high", "medium", "low"]
        assert d['n_supporting_constraints'] == 2
        assert d['mean_constraint_strength'] == 0.55


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
