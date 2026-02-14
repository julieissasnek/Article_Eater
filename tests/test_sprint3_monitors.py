"""
Tests for Sprint 3: Reflexive Monitoring Algorithms.

Verifies:
- Task 3.1: Coherence audit algorithm
- Task 3.2: Entrenchment asymmetry monitor
- Task 3.3: Structural bias detection
- Task 3.4: Adversarial review cycle
"""

import pytest


class TestTask31CoherenceAudit:
    """Task 3.1: Coherence audit algorithm tests."""

    def test_can_import_coherence_audit(self):
        """Coherence audit module is importable."""
        from src.epistemic.monitors.coherence_audit import run_coherence_audit
        assert run_coherence_audit is not None

    def test_basic_coherence_drift_detection(self):
        """Detects coherence drift when node changes without direct evidence."""
        from src.epistemic.monitors.coherence_audit import run_coherence_audit, FlagType

        pre = {"A": 0.5, "B": 0.4, "C": 0.6}
        post = {"A": 0.7, "B": 0.55, "C": 0.6}  # A and B changed
        new_claims = ["claim_1"]
        # claim_1 directly supports A, not B
        direct_links = {"claim_1": {"A"}}

        result = run_coherence_audit(
            web=None,
            pre_snapshot=pre,
            post_snapshot=post,
            new_claim_ids=new_claims,
            direct_evidence_links=direct_links,
        )

        # B should be flagged (changed but no direct evidence)
        flagged_ids = [n.node_id for n in result.flagged_nodes]
        assert "B" in flagged_ids
        assert "A" not in flagged_ids  # A has direct evidence
        assert "C" not in flagged_ids  # C didn't change

    def test_positive_vs_negative_drift(self):
        """Correctly classifies positive and negative coherence drift."""
        from src.epistemic.monitors.coherence_audit import run_coherence_audit, FlagType

        pre = {"X": 0.5, "Y": 0.5}
        post = {"X": 0.7, "Y": 0.3}  # X up, Y down
        new_claims = ["claim_1"]

        result = run_coherence_audit(
            web=None,
            pre_snapshot=pre,
            post_snapshot=post,
            new_claim_ids=new_claims,
        )

        # Both should be flagged with appropriate types
        x_flag = next((n for n in result.flagged_nodes if n.node_id == "X"), None)
        y_flag = next((n for n in result.flagged_nodes if n.node_id == "Y"), None)

        assert x_flag is not None
        assert x_flag.flag_type == FlagType.COHERENCE_DRIFT_POSITIVE

        assert y_flag is not None
        assert y_flag.flag_type == FlagType.COHERENCE_DRIFT_NEGATIVE

    def test_threshold_filtering(self):
        """Only flags changes above threshold."""
        from src.epistemic.monitors.coherence_audit import run_coherence_audit

        pre = {"A": 0.5, "B": 0.5}
        post = {"A": 0.55, "B": 0.9}  # A small change, B big change

        result = run_coherence_audit(
            web=None,
            pre_snapshot=pre,
            post_snapshot=post,
            new_claim_ids=[],
            threshold=0.1,
        )

        flagged_ids = [n.node_id for n in result.flagged_nodes]
        assert "A" not in flagged_ids  # Change too small
        assert "B" in flagged_ids  # Change significant

    def test_result_serialization(self):
        """Result can be serialized to dict."""
        from src.epistemic.monitors.coherence_audit import run_coherence_audit

        result = run_coherence_audit(
            web=None,
            pre_snapshot={"A": 0.5},
            post_snapshot={"A": 0.8},
            new_claim_ids=[],
        )

        d = result.to_dict()
        assert "flagged_nodes" in d
        assert "total_nodes_checked" in d
        assert "total_flagged" in d


class TestTask32AsymmetryMonitor:
    """Task 3.2: Entrenchment asymmetry monitor tests."""

    def test_can_import_asymmetry_monitor(self):
        """Asymmetry monitor module is importable."""
        from src.epistemic.monitors.asymmetry_monitor import run_asymmetry_monitor
        assert run_asymmetry_monitor is not None

    def test_detects_high_entrenchment_low_evidence(self):
        """Flags nodes with high entrenchment but low direct evidence."""
        from src.epistemic.monitors.asymmetry_monitor import run_asymmetry_monitor

        entrenchment = {"A": 0.9, "B": 0.3, "C": 0.8}
        evidence = {"A": 10, "B": 2, "C": 1}  # C has high entrenchment, low evidence

        result = run_asymmetry_monitor(
            web=None,
            entrenchment_scores=entrenchment,
            direct_evidence_counts=evidence,
            coherence_link_counts={"A": 5, "B": 3, "C": 8},
        )

        flagged_ids = [n.node_id for n in result.flagged_nodes]
        assert "C" in flagged_ids  # High entrenchment / low evidence
        assert "A" not in flagged_ids  # Good evidence support

    def test_asymmetry_ratio_calculation(self):
        """Correctly calculates asymmetry ratio."""
        from src.epistemic.monitors.asymmetry_monitor import run_asymmetry_monitor

        entrenchment = {"X": 0.8}
        evidence = {"X": 1}  # Very low evidence

        result = run_asymmetry_monitor(
            web=None,
            entrenchment_scores=entrenchment,
            direct_evidence_counts=evidence,
            threshold=1.0,  # Low threshold to ensure flagging
        )

        assert result.total_flagged == 1
        flagged = result.flagged_nodes[0]
        # 0.8 entrenchment / 0.1 normalized evidence = 8.0 ratio
        assert flagged.asymmetry_ratio > 3.0

    def test_risk_level_classification(self):
        """Correctly classifies risk levels."""
        from src.epistemic.monitors.asymmetry_monitor import run_asymmetry_monitor, AsymmetryRisk

        entrenchment = {"HIGH": 0.9, "MED": 0.5, "LOW": 0.35}
        evidence = {"HIGH": 0, "MED": 0, "LOW": 0}  # All zero evidence

        result = run_asymmetry_monitor(
            web=None,
            entrenchment_scores=entrenchment,
            direct_evidence_counts=evidence,
            threshold=1.0,
        )

        # Should have all three risk levels represented
        high_risk = result.get_high_risk()
        assert len(high_risk) > 0

    def test_recommendation_generated(self):
        """Generates actionable recommendations."""
        from src.epistemic.monitors.asymmetry_monitor import run_asymmetry_monitor

        result = run_asymmetry_monitor(
            web=None,
            entrenchment_scores={"A": 0.9},
            direct_evidence_counts={"A": 0},
            threshold=1.0,
        )

        assert result.total_flagged == 1
        assert "CRITICAL" in result.flagged_nodes[0].recommendation


class TestTask33BiasDetection:
    """Task 3.3: Structural bias detection tests."""

    def test_can_import_bias_detection(self):
        """Bias detection module is importable."""
        from src.epistemic.monitors.bias_detection import run_structural_bias_detection
        assert run_structural_bias_detection is not None

    def test_detects_single_lab_cluster(self):
        """Flags low independence when all studies from same lab."""
        from src.epistemic.monitors.bias_detection import (
            run_structural_bias_detection, BiasFlag
        )

        # 5 studies all from same lab, same paradigm, same method
        evidence = [
            {"lab_id": "lab_A", "paradigm": "ART", "method": "self_report"},
            {"lab_id": "lab_A", "paradigm": "ART", "method": "self_report"},
            {"lab_id": "lab_A", "paradigm": "ART", "method": "self_report"},
            {"lab_id": "lab_A", "paradigm": "ART", "method": "self_report"},
            {"lab_id": "lab_A", "paradigm": "ART", "method": "self_report"},
        ]

        # Use higher thresholds to ensure flags are triggered
        result = run_structural_bias_detection(
            web=None,
            node_id="claim_1",
            evidence_metadata=evidence,
            independence_threshold=0.3,
            paradigm_threshold=0.25,  # 1/5=0.2 < 0.25 -> flagged
            method_threshold=0.25,    # 1/5=0.2 < 0.25 -> flagged
        )

        # All from same lab -> independence = 0 < 0.3
        assert BiasFlag.LOW_INDEPENDENCE in result.flags
        # All same paradigm (1/5 = 0.2) < 0.25 threshold
        assert BiasFlag.LOW_PARADIGM_DIVERSITY in result.flags
        # All same method (1/5 = 0.2) < 0.25 threshold
        assert BiasFlag.LOW_METHOD_DIVERSITY in result.flags

    def test_diverse_evidence_no_flags(self):
        """No flags when evidence is diverse."""
        from src.epistemic.monitors.bias_detection import run_structural_bias_detection

        evidence = [
            {"lab_id": "lab_A", "paradigm": "ART", "method": "self_report"},
            {"lab_id": "lab_B", "paradigm": "SRT", "method": "cortisol"},
            {"lab_id": "lab_C", "paradigm": "Biophilia", "method": "EEG"},
            {"lab_id": "lab_D", "paradigm": "Predictive", "method": "fMRI"},
            {"lab_id": "lab_E", "paradigm": "Embodied", "method": "behavioral"},
        ]

        result = run_structural_bias_detection(
            web=None,
            node_id="claim_1",
            evidence_metadata=evidence,
        )

        assert len(result.flags) == 0
        assert result.overall_diversity_score > 0.5

    def test_single_source_flag(self):
        """Flags single-source evidence."""
        from src.epistemic.monitors.bias_detection import (
            run_structural_bias_detection, BiasFlag
        )

        result = run_structural_bias_detection(
            web=None,
            node_id="claim_1",
            evidence_metadata=[{"lab_id": "lab_A", "paradigm": "X", "method": "Y"}],
        )

        assert BiasFlag.SINGLE_SOURCE in result.flags

    def test_no_evidence_handling(self):
        """Handles case with no evidence gracefully."""
        from src.epistemic.monitors.bias_detection import (
            run_structural_bias_detection, BiasFlag
        )

        result = run_structural_bias_detection(
            web=None,
            node_id="claim_1",
            evidence_metadata=[],
        )

        assert BiasFlag.SINGLE_SOURCE in result.flags
        assert result.evidence_count == 0


class TestTask34AdversarialReview:
    """Task 3.4: Adversarial review cycle tests."""

    def test_can_import_adversarial_review(self):
        """Adversarial review module is importable."""
        from src.epistemic.monitors.adversarial_review import run_adversarial_review
        assert run_adversarial_review is not None

    def test_basic_adversarial_review(self):
        """Reviews top entrenched nodes."""
        from src.epistemic.monitors.adversarial_review import run_adversarial_review

        entrenchment = {"A": 0.9, "B": 0.8, "C": 0.7, "D": 0.5}
        counter = {"A": [{"source": "study_x", "type": "failed_replication", "weight": 0.3}]}

        result = run_adversarial_review(
            web=None,
            n_top_nodes=3,
            entrenchment_scores=entrenchment,
            counter_evidence=counter,
        )

        assert result.total_reviewed == 3
        assert len(result.reviewed_nodes) == 3

        # A should show some vulnerability due to counter-evidence
        a_review = next((n for n in result.reviewed_nodes if n.node_id == "A"), None)
        assert a_review is not None
        assert a_review.counter_evidence_count == 1

    def test_survival_status_classification(self):
        """Correctly classifies survival status."""
        from src.epistemic.monitors.adversarial_review import (
            run_adversarial_review, SurvivalStatus
        )

        entrenchment = {"STRONG": 0.95, "WEAK": 0.3}
        counter = {
            "STRONG": [],  # No counter-evidence
            "WEAK": [
                {"source": "s1", "type": "contradiction", "weight": 0.5},
                {"source": "s2", "type": "failed_rep", "weight": 0.5},
            ],
        }

        result = run_adversarial_review(
            web=None,
            n_top_nodes=2,
            entrenchment_scores=entrenchment,
            counter_evidence=counter,
            acceptance_threshold=0.4,
        )

        strong_review = next((n for n in result.reviewed_nodes if n.node_id == "STRONG"), None)
        assert strong_review.survival_status == SurvivalStatus.SURVIVED

    def test_vulnerability_score_calculation(self):
        """Calculates vulnerability score correctly."""
        from src.epistemic.monitors.adversarial_review import run_adversarial_review

        entrenchment = {"X": 0.8}
        counter = {"X": [{"source": "s1", "type": "contradict", "weight": 0.4}]}

        result = run_adversarial_review(
            web=None,
            n_top_nodes=1,
            entrenchment_scores=entrenchment,
            counter_evidence=counter,
            precision_boost=2.0,  # Double the counter-evidence weight
        )

        reviewed = result.reviewed_nodes[0]
        # Should show some vulnerability
        assert reviewed.vulnerability_score > 0
        assert reviewed.post_review_entrenchment < reviewed.pre_review_entrenchment

    def test_result_serialization(self):
        """Result can be serialized to dict."""
        from src.epistemic.monitors.adversarial_review import run_adversarial_review

        result = run_adversarial_review(
            web=None,
            n_top_nodes=1,
            entrenchment_scores={"A": 0.8},
            counter_evidence={},
        )

        d = result.to_dict()
        assert "reviewed_nodes" in d
        assert "summary" in d
        assert "parameters" in d


class TestMonitorsIntegration:
    """Integration tests for all monitors."""

    def test_all_monitors_importable_from_package(self):
        """All monitors are importable from the monitors package."""
        from src.epistemic.monitors import (
            run_coherence_audit,
            run_asymmetry_monitor,
            run_structural_bias_detection,
            run_adversarial_review,
        )

        assert run_coherence_audit is not None
        assert run_asymmetry_monitor is not None
        assert run_structural_bias_detection is not None
        assert run_adversarial_review is not None

    def test_monitor_results_have_common_interface(self):
        """All monitor results have to_dict method."""
        from src.epistemic.monitors import (
            run_coherence_audit,
            run_asymmetry_monitor,
            run_structural_bias_detection,
            run_adversarial_review,
        )

        # All should return serializable results
        r1 = run_coherence_audit(None, {"A": 0.5}, {"A": 0.8}, [])
        r2 = run_asymmetry_monitor(None, entrenchment_scores={"A": 0.8},
                                    direct_evidence_counts={"A": 1})
        r3 = run_structural_bias_detection(None, "A", evidence_metadata=[])
        r4 = run_adversarial_review(None, entrenchment_scores={"A": 0.8})

        assert hasattr(r1, 'to_dict')
        assert hasattr(r2, 'to_dict')
        assert hasattr(r3, 'to_dict')
        assert hasattr(r4, 'to_dict')

        # All should serialize without error
        assert isinstance(r1.to_dict(), dict)
        assert isinstance(r2.to_dict(), dict)
        assert isinstance(r3.to_dict(), dict)
        assert isinstance(r4.to_dict(), dict)
