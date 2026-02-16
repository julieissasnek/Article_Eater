"""
Tests for Sprint 6d: Monitor Updates.

Tests the four monitor modules:
- Task 6d.1: theory_monitor.py
- Task 6d.2: cross_type_coherence.py
- Task 6d.3: api_extensions.py
- Task 6d.4: dashboard_components.py (integration tests)
"""

import pytest
from datetime import datetime

# Task 6d.1: Theory Monitor
from src.epistemic.monitors.theory_monitor import (
    TheoryMonitor,
    TheoryHealthStatus,
    TheoryRisk,
    TheoryHealthReport,
    TheoryMonitorSummary,
    create_theory_monitor,
    assess_all_theories,
)

# Task 6d.2: Cross-Type Coherence
from src.epistemic.monitors.cross_type_coherence import (
    CrossTypeCoherenceMonitor,
    CoherenceType,
    CoherenceAnomaly,
    CrossTypeCoherenceScore,
    CoherenceAnomalyReport,
    WebCoherenceReport,
    create_coherence_monitor,
    compute_family_coherence,
    get_coherence_weight,
)

from src.epistemic.node_types import NodeType
from src.epistemic.entrenchment.prediction_ledger import PredictionLedger


# =============================================================================
# Task 6d.1: Theory Monitor Tests
# =============================================================================

class TestTheoryMonitor:
    """Test theory health monitoring."""

    def test_create_theory_monitor(self):
        """Theory monitor can be created."""
        monitor = create_theory_monitor()
        assert monitor is not None
        assert isinstance(monitor, TheoryMonitor)

    def test_assess_theory_untested(self):
        """Untested theory is flagged correctly."""
        monitor = TheoryMonitor()
        report = monitor.assess_theory(
            theory_id="test_theory_001",
            theory_text="Test theoretical proposition",
            current_entrenchment=0.35
        )

        assert report.theory_id == "test_theory_001"
        assert report.health_status == TheoryHealthStatus.UNTESTED
        assert report.n_confirmations == 0
        assert report.n_disconfirmations == 0

    def test_assess_theory_with_ledger(self):
        """Theory assessment uses ledger data."""
        ledger = PredictionLedger()

        # Register hypothesis derived from theory
        ledger.register_hypothesis(
            hypothesis_id="hyp_001",
            text="Test hypothesis",
            parent_prop_id="theory_001"
        )

        # Record confirmations
        ledger.record_confirmation("hyp_001", "study_1")
        ledger.record_confirmation("hyp_001", "study_2")

        monitor = TheoryMonitor(ledger)
        report = monitor.assess_theory(
            theory_id="theory_001",
            theory_text="Theory with confirmations",
            current_entrenchment=0.35
        )

        assert report.n_confirmations == 2
        assert report.n_disconfirmations == 0
        assert report.health_status in {
            TheoryHealthStatus.WELL_SUPPORTED,
            TheoryHealthStatus.MODERATELY_SUPPORTED
        }

    def test_assess_theory_with_disconfirmations(self):
        """Disconfirmations affect theory health."""
        ledger = PredictionLedger()

        ledger.register_hypothesis(
            hypothesis_id="hyp_001",
            text="Test hypothesis",
            parent_prop_id="theory_002"
        )

        # More disconfirmations than confirmations
        ledger.record_confirmation("hyp_001", "study_1")
        ledger.record_disconfirmation("hyp_001", "study_2")
        ledger.record_disconfirmation("hyp_001", "study_3")
        ledger.record_disconfirmation("hyp_001", "study_4")

        monitor = TheoryMonitor(ledger)
        report = monitor.assess_theory(
            theory_id="theory_002",
            current_entrenchment=0.35
        )

        assert report.n_disconfirmations >= 2
        assert report.health_status in {
            TheoryHealthStatus.NEEDS_REVISION,
            TheoryHealthStatus.PROBLEMATIC
        }

    def test_identify_unfalsifiable_risk(self):
        """Unfalsifiable theory is flagged."""
        monitor = TheoryMonitor()
        report = monitor.assess_theory(
            theory_id="unfalsifiable_theory",
            current_entrenchment=0.6  # High entrenchment
        )

        # No hypotheses = no testable predictions = unfalsifiable
        assert TheoryRisk.UNFALSIFIABLE in report.risks

    def test_identify_overentrenched_risk(self):
        """Overentrenched theory without evidence is flagged."""
        monitor = TheoryMonitor()
        report = monitor.assess_theory(
            theory_id="overentrenched_theory",
            current_entrenchment=0.7  # High entrenchment, no confirmations
        )

        assert TheoryRisk.OVERENTRENCHED in report.risks

    def test_get_summary(self):
        """Monitor generates summary correctly."""
        monitor = TheoryMonitor()

        # Assess multiple theories
        monitor.assess_theory("theory_1", current_entrenchment=0.35)
        monitor.assess_theory("theory_2", current_entrenchment=0.50)
        monitor.assess_theory("theory_3", current_entrenchment=0.70)

        summary = monitor.get_summary()

        assert summary.total_theories == 3
        assert summary.untested >= 0

    def test_check_theory_alerts(self):
        """Alerts are generated for problematic theories."""
        ledger = PredictionLedger()

        # Create a theory with many disconfirmations
        ledger.register_hypothesis("hyp_bad", "Bad hypothesis", "bad_theory")
        for i in range(5):
            ledger.record_disconfirmation("hyp_bad", f"study_{i}")

        monitor = TheoryMonitor(ledger)
        monitor.assess_theory("bad_theory", current_entrenchment=0.35)

        alerts = monitor.check_theory_alerts()

        assert len(alerts) > 0
        alert_types = [a["type"] for a in alerts]
        assert "problematic_theory" in alert_types or "accumulating_disconfirmations" in alert_types

    def test_assess_all_theories(self):
        """Batch assessment of theories."""
        ledger = PredictionLedger()

        theory_data = [
            {"theory_id": "t1", "theory_text": "Theory 1", "entrenchment": 0.35},
            {"theory_id": "t2", "theory_text": "Theory 2", "entrenchment": 0.50},
        ]

        reports = assess_all_theories(theory_data, ledger)

        assert len(reports) == 2
        assert all(isinstance(r, TheoryHealthReport) for r in reports)

    def test_theory_health_report_to_dict(self):
        """TheoryHealthReport serializes correctly."""
        report = TheoryHealthReport(
            theory_id="test",
            theory_text="Test theory",
            current_entrenchment=0.5,
            health_status=TheoryHealthStatus.UNTESTED,
            n_hypotheses=0,
            n_confirmations=0,
            n_disconfirmations=0,
            confirmation_rate=None,
            risks=[TheoryRisk.UNFALSIFIABLE],
            recommendation="Derive testable predictions"
        )

        d = report.to_dict()

        assert d["theory_id"] == "test"
        assert d["health_status"] == "untested"
        assert "unfalsifiable" in d["risks"]


# =============================================================================
# Task 6d.2: Cross-Type Coherence Tests
# =============================================================================

class TestCrossTypeCoherence:
    """Test cross-type coherence monitoring."""

    def test_create_coherence_monitor(self):
        """Coherence monitor can be created."""
        monitor = create_coherence_monitor()
        assert monitor is not None
        assert isinstance(monitor, CrossTypeCoherenceMonitor)

    def test_register_nodes(self):
        """Nodes can be registered."""
        monitor = CrossTypeCoherenceMonitor()
        monitor.register_node("node_1", NodeType.THEORETICAL_PROPOSITION)
        monitor.register_node("node_2", NodeType.EMPIRICAL_FINDING)

        assert "node_1" in monitor._nodes
        assert "node_2" in monitor._nodes

    def test_register_edges(self):
        """Edges can be registered."""
        monitor = CrossTypeCoherenceMonitor()
        monitor.register_node("node_1", NodeType.THEORETICAL_PROPOSITION)
        monitor.register_node("node_2", NodeType.DERIVED_HYPOTHESIS)
        monitor.register_edge("node_1", "node_2", "theoretically_predicts", 1.0)

        assert len(monitor._edges) == 1

    def test_compute_pairwise_coherence(self):
        """Pairwise coherence can be computed."""
        monitor = CrossTypeCoherenceMonitor()
        monitor.register_node("theory_1", NodeType.THEORETICAL_PROPOSITION)
        monitor.register_node("finding_1", NodeType.EMPIRICAL_FINDING)
        monitor.register_edge("theory_1", "finding_1", "theoretically_predicts", 1.0)

        score = monitor.compute_pairwise_coherence("theory_1", "finding_1")

        assert score is not None
        assert isinstance(score, CrossTypeCoherenceScore)
        assert 0.0 <= score.score <= 1.0

    def test_coherence_type_theory_evidence(self):
        """Theory-evidence coherence type is assigned correctly."""
        monitor = CrossTypeCoherenceMonitor()
        monitor.register_node("theory_1", NodeType.THEORETICAL_PROPOSITION)
        monitor.register_node("finding_1", NodeType.EMPIRICAL_FINDING)

        score = monitor.compute_pairwise_coherence("theory_1", "finding_1")

        assert score.coherence_type == CoherenceType.THEORY_EVIDENCE

    def test_coherence_type_synthesis_primary(self):
        """Synthesis-primary coherence type is assigned correctly."""
        monitor = CrossTypeCoherenceMonitor()
        monitor.register_node("synth_1", NodeType.SYNTHESIS_CONCLUSION)
        monitor.register_node("study_1", NodeType.EMPIRICAL_FINDING)

        score = monitor.compute_pairwise_coherence("synth_1", "study_1")

        assert score.coherence_type == CoherenceType.SYNTHESIS_PRIMARY

    def test_detect_ungrounded_theory(self):
        """Ungrounded theories are detected."""
        monitor = CrossTypeCoherenceMonitor()
        monitor.register_node("lonely_theory", NodeType.THEORETICAL_PROPOSITION)
        # No edges connecting it to evidence

        anomalies = monitor.detect_anomalies()
        ungrounded = [a for a in anomalies if a.anomaly_type == CoherenceAnomaly.UNGROUNDED_THEORY]

        assert len(ungrounded) == 1
        assert ungrounded[0].node_id == "lonely_theory"

    def test_detect_uninterpreted_evidence(self):
        """Uninterpreted evidence is detected."""
        monitor = CrossTypeCoherenceMonitor()
        monitor.register_node("orphan_finding", NodeType.EMPIRICAL_FINDING)
        # No edges connecting it to theory

        anomalies = monitor.detect_anomalies()
        uninterpreted = [a for a in anomalies if a.anomaly_type == CoherenceAnomaly.UNINTERPRETED_EVIDENCE]

        assert len(uninterpreted) == 1
        assert uninterpreted[0].node_id == "orphan_finding"

    def test_detect_orphan_synthesis(self):
        """Orphan syntheses are detected."""
        monitor = CrossTypeCoherenceMonitor()
        monitor.register_node("orphan_synth", NodeType.SYNTHESIS_CONCLUSION)
        # No INCLUDES_IN_SYNTHESIS edges

        anomalies = monitor.detect_anomalies()
        orphans = [a for a in anomalies if a.anomaly_type == CoherenceAnomaly.ORPHAN_SYNTHESIS]

        assert len(orphans) == 1
        assert orphans[0].node_id == "orphan_synth"

    def test_detect_untested_hypothesis(self):
        """Untested hypotheses are detected."""
        monitor = CrossTypeCoherenceMonitor()
        monitor.register_node("untested_hyp", NodeType.DERIVED_HYPOTHESIS)
        # No confirms_prediction or disconfirms_prediction edges

        anomalies = monitor.detect_anomalies()
        untested = [a for a in anomalies if a.anomaly_type == CoherenceAnomaly.UNTESTED_HYPOTHESIS]

        assert len(untested) == 1
        assert untested[0].node_id == "untested_hyp"

    def test_detect_isolated_definition(self):
        """Isolated definitions are detected."""
        monitor = CrossTypeCoherenceMonitor()
        monitor.register_node("lonely_def", NodeType.CONCEPTUAL_DEFINITION)
        # No connections

        anomalies = monitor.detect_anomalies()
        isolated = [a for a in anomalies if a.anomaly_type == CoherenceAnomaly.ISOLATED_DEFINITION]

        assert len(isolated) == 1
        assert isolated[0].node_id == "lonely_def"

    def test_generate_report(self):
        """Coherence report is generated correctly."""
        monitor = CrossTypeCoherenceMonitor()
        monitor.register_node("theory_1", NodeType.THEORETICAL_PROPOSITION)
        monitor.register_node("finding_1", NodeType.EMPIRICAL_FINDING)
        monitor.register_edge("theory_1", "finding_1", "theoretically_predicts", 1.0)

        report = monitor.generate_report()

        assert isinstance(report, WebCoherenceReport)
        assert report.total_nodes == 2
        assert "theoretical_proposition" in report.nodes_by_type
        assert "empirical_finding" in report.nodes_by_type

    def test_compute_family_coherence(self):
        """Family-level coherence can be computed."""
        nodes = [
            ("t1", NodeType.THEORETICAL_PROPOSITION),
            ("t2", NodeType.THEORETICAL_PROPOSITION),
            ("e1", NodeType.EMPIRICAL_FINDING),
            ("e2", NodeType.EMPIRICAL_FINDING),
        ]
        edges = [
            ("t1", "e1", "theoretically_predicts"),
            ("t2", "e2", "theoretically_predicts"),
        ]

        family_coherence = compute_family_coherence(nodes, edges)

        # Should have structural-evidence coherence
        assert any("structural" in k[0] or "evidence" in k[0] for k in family_coherence.keys())

    def test_get_coherence_weight(self):
        """Coherence weights are returned correctly."""
        weight = get_coherence_weight(
            NodeType.THEORETICAL_PROPOSITION,
            NodeType.EMPIRICAL_FINDING
        )

        # Structural-Evidence coherence should have high weight
        assert weight > 0.5

    def test_coherence_score_to_dict(self):
        """CrossTypeCoherenceScore serializes correctly."""
        score = CrossTypeCoherenceScore(
            source_node_id="node_1",
            source_node_type=NodeType.THEORETICAL_PROPOSITION,
            target_node_id="node_2",
            target_node_type=NodeType.EMPIRICAL_FINDING,
            coherence_type=CoherenceType.THEORY_EVIDENCE,
            score=0.75,
            edge_count=1,
            explanation="High coherence via theoretically_predicts"
        )

        d = score.to_dict()

        assert d["source_node_id"] == "node_1"
        assert d["coherence_type"] == "theory_evidence"
        assert d["score"] == 0.75

    def test_anomaly_report_to_dict(self):
        """CoherenceAnomalyReport serializes correctly."""
        report = CoherenceAnomalyReport(
            node_id="test_node",
            node_type=NodeType.THEORETICAL_PROPOSITION,
            anomaly_type=CoherenceAnomaly.UNGROUNDED_THEORY,
            severity=0.7,
            description="Theory has no empirical connections",
            suggested_action="Link to evidence"
        )

        d = report.to_dict()

        assert d["node_id"] == "test_node"
        assert d["anomaly_type"] == "ungrounded_theory"
        assert d["severity"] == 0.7

    def test_web_coherence_report_to_dict(self):
        """WebCoherenceReport serializes correctly."""
        report = WebCoherenceReport(
            total_nodes=10,
            nodes_by_type={"theoretical_proposition": 3, "empirical_finding": 7},
            cross_type_scores=[],
            anomalies=[],
            mean_theory_evidence_coherence=0.6,
            mean_synthesis_primary_coherence=0.5,
            ungrounded_theory_count=1,
            uninterpreted_evidence_count=2
        )

        d = report.to_dict()

        assert d["total_nodes"] == 10
        assert d["mean_theory_evidence_coherence"] == 0.6


# =============================================================================
# Task 6d.3: API Extensions Tests (Unit Tests)
# =============================================================================

class TestAPIExtensionsUnit:
    """Unit tests for API extension components."""

    def test_imports(self):
        """API extensions module imports correctly."""
        from src.epistemic.api_extensions import (
            theory_health_router,
            coherence_router,
            predictions_router,
            nodes_router,
            get_sprint6_router,
        )

        router = get_sprint6_router()
        assert router is not None

    def test_node_types_endpoint_logic(self):
        """Node types listing logic works."""
        from src.epistemic.node_types import NodeType, NODE_TYPE_PROPERTIES

        types = []
        for node_type in NodeType:
            props = NODE_TYPE_PROPERTIES.get(node_type)
            types.append({
                "type": node_type.value,
                "family": props.family.value if props else "unknown",
                "bn_eligible": props.bn_eligible if props else False,
            })

        assert len(types) == 12  # 12 node types
        assert any(t["type"] == "theoretical_proposition" for t in types)
        assert any(t["type"] == "empirical_finding" for t in types)


# =============================================================================
# Integration Tests
# =============================================================================

class TestSprintIntegration:
    """Integration tests across Sprint 6d modules."""

    def test_monitor_to_api_flow(self):
        """Monitor data flows to API layer correctly."""
        # Create monitor
        ledger = PredictionLedger()
        monitor = TheoryMonitor(ledger)

        # Assess theory
        report = monitor.assess_theory(
            theory_id="integration_test_theory",
            theory_text="Test for integration",
            current_entrenchment=0.5
        )

        # Report should be serializable (for API)
        report_dict = report.to_dict()
        assert "theory_id" in report_dict
        assert "health_status" in report_dict

    def test_coherence_to_api_flow(self):
        """Coherence data flows to API layer correctly."""
        # Create monitor
        monitor = CrossTypeCoherenceMonitor()

        # Register nodes
        monitor.register_node("api_theory", NodeType.THEORETICAL_PROPOSITION)
        monitor.register_node("api_evidence", NodeType.EMPIRICAL_FINDING)
        monitor.register_edge("api_theory", "api_evidence", "theoretically_predicts", 1.0)

        # Generate report
        report = monitor.generate_report()

        # Report should be serializable (for API)
        report_dict = report.to_dict()
        assert "total_nodes" in report_dict
        assert report_dict["total_nodes"] == 2

    def test_theory_and_coherence_integration(self):
        """Theory monitor and coherence monitor work together."""
        # Set up ledger with hypothesis
        ledger = PredictionLedger()
        ledger.register_hypothesis("int_hyp_1", "Integration hypothesis", "int_theory_1")
        ledger.record_confirmation("int_hyp_1", "study_1")

        # Theory monitor
        theory_monitor = TheoryMonitor(ledger)
        theory_report = theory_monitor.assess_theory(
            theory_id="int_theory_1",
            current_entrenchment=0.35
        )

        # Coherence monitor
        coh_monitor = CrossTypeCoherenceMonitor()
        coh_monitor.register_node("int_theory_1", NodeType.THEORETICAL_PROPOSITION)
        coh_monitor.register_node("int_hyp_1", NodeType.DERIVED_HYPOTHESIS)
        coh_monitor.register_node("study_1", NodeType.EMPIRICAL_FINDING)
        coh_monitor.register_edge("int_theory_1", "int_hyp_1", "theoretically_predicts", 1.0)
        coh_monitor.register_edge("study_1", "int_hyp_1", "confirms_prediction", 1.0)

        coh_report = coh_monitor.generate_report()

        # Both should work
        assert theory_report.n_confirmations == 1
        assert coh_report.total_nodes == 3

        # No anomalies for connected nodes
        anomalies = coh_monitor.detect_anomalies()
        # hypothesis has test, theory has hypothesis, evidence has connection
        ungrounded = [a for a in anomalies if a.anomaly_type == CoherenceAnomaly.UNGROUNDED_THEORY and a.node_id == "int_theory_1"]
        assert len(ungrounded) == 0


class TestTheoryMonitorEdgeCases:
    """Edge case tests for theory monitor."""

    def test_empty_ledger(self):
        """Monitor handles empty ledger."""
        monitor = TheoryMonitor()
        report = monitor.assess_theory("empty_theory", current_entrenchment=0.35)

        assert report.health_status == TheoryHealthStatus.UNTESTED
        assert report.confirmation_rate is None

    def test_multiple_hypotheses_per_theory(self):
        """Multiple hypotheses contribute to theory track record."""
        ledger = PredictionLedger()

        # 3 hypotheses for one theory
        ledger.register_hypothesis("h1", "Hyp 1", "multi_theory")
        ledger.register_hypothesis("h2", "Hyp 2", "multi_theory")
        ledger.register_hypothesis("h3", "Hyp 3", "multi_theory")

        ledger.record_confirmation("h1", "s1")
        ledger.record_confirmation("h2", "s2")
        ledger.record_disconfirmation("h3", "s3")

        monitor = TheoryMonitor(ledger)
        report = monitor.assess_theory("multi_theory", current_entrenchment=0.35)

        assert report.n_hypotheses == 3
        assert report.n_confirmations == 2
        assert report.n_disconfirmations == 1


class TestCrossTypeCoherenceEdgeCases:
    """Edge case tests for coherence monitor."""

    def test_empty_web(self):
        """Monitor handles empty web."""
        monitor = CrossTypeCoherenceMonitor()
        report = monitor.generate_report()

        assert report.total_nodes == 0
        assert len(report.anomalies) == 0

    def test_fully_connected_web(self):
        """Fully connected web has no anomalies."""
        monitor = CrossTypeCoherenceMonitor()

        # Theory with hypothesis and confirming evidence
        monitor.register_node("t1", NodeType.THEORETICAL_PROPOSITION)
        monitor.register_node("h1", NodeType.DERIVED_HYPOTHESIS)
        monitor.register_node("e1", NodeType.EMPIRICAL_FINDING)

        monitor.register_edge("t1", "h1", "theoretically_predicts", 1.0)
        monitor.register_edge("e1", "h1", "confirms_prediction", 1.0)

        anomalies = monitor.detect_anomalies()

        # Theory connected to hypothesis (not ungrounded)
        # Evidence connected to hypothesis (not uninterpreted)
        # Hypothesis has confirming study (not untested)
        ungrounded = [a for a in anomalies if a.anomaly_type == CoherenceAnomaly.UNGROUNDED_THEORY]
        uninterpreted = [a for a in anomalies if a.anomaly_type == CoherenceAnomaly.UNINTERPRETED_EVIDENCE]
        untested = [a for a in anomalies if a.anomaly_type == CoherenceAnomaly.UNTESTED_HYPOTHESIS]

        assert len(ungrounded) == 0
        assert len(uninterpreted) == 0
        assert len(untested) == 0
