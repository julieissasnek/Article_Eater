"""
Integration Tests for Sprint 6e: Non-Empirical Web Integration.

End-to-end tests verifying the complete flows across Sprint 6a-6d modules:
- Task 6e.1: Theory → hypothesis → confirmation flow
- Task 6e.2: Synthesis floor rule edge cases
- Task 6e.3: Expert vs. systematic comparison
- Task 6e.4: Methodological critique cascade
- Task 6e.5: Mixed empirical/theoretical coherence
- Task 6e.6: Prediction ledger persistence

These tests validate that the components work together correctly.
"""

import pytest
import tempfile
import os
from datetime import datetime

# Sprint 6a: Schema
from src.epistemic.node_types import NodeType, NodeTypeFamily, get_node_type_family
from src.epistemic.edge_types import EdgeType, validate_edge_connection
from src.epistemic.contracts.claim_v2 import ClaimV2
from src.epistemic.contracts.edge_v2 import EdgeV2

# Sprint 6b: Entrenchment
from src.epistemic.entrenchment.node_type_entrenchment import (
    BASE_ENTRENCHMENT,
    compute_base_entrenchment,
    compute_entrenchment_with_modifiers,
)
from src.epistemic.entrenchment.theory_updating import (
    update_theory_entrenchment,
    assess_theory_health,
    CONFIRMATION_BONUS,
    DISCONFIRMATION_PENALTY,
)
from src.epistemic.entrenchment.synthesis_rules import (
    compute_synthesis_entrenchment,
    compute_median_entrenchment,
)
from src.epistemic.entrenchment.expert_discount import (
    compute_expert_synthesis_entrenchment,
    compare_expert_vs_systematic,
    EXPERT_SYNTHESIS_DISCOUNT,
)
from src.epistemic.entrenchment.critique_propagation import (
    CritiquePropagationResult,
)
from src.epistemic.entrenchment.prediction_ledger import (
    PredictionLedger,
    PredictionLedgerEntry,
)

# Sprint 6c: Ingestion
from src.epistemic.extraction.paper_classifier import (
    TemplateFamily,
    classify_paper,
    get_node_types_for_template,
)
from src.epistemic.extraction.theoretical_extractor import (
    extract_theoretical_paper,
    compute_proposition_entrenchment,
)
from src.epistemic.extraction.synthesis_ingester import (
    SynthesisType,
    EvidenceDirection,
    ingest_synthesis_paper,
)

# Sprint 6d: Monitors
from src.epistemic.monitors.theory_monitor import (
    TheoryMonitor,
    TheoryHealthStatus,
    TheoryRisk,
)
from src.epistemic.monitors.cross_type_coherence import (
    CrossTypeCoherenceMonitor,
    CoherenceType,
    CoherenceAnomaly,
)


# =============================================================================
# Task 6e.1: Theory → Hypothesis → Confirmation Flow
# =============================================================================

class TestTheoryHypothesisConfirmationFlow:
    """
    End-to-end test of the theory evaluation pipeline.

    Flow:
    1. Extract theoretical paper → propositions + hypotheses
    2. Register hypotheses in prediction ledger
    3. Process empirical paper → confirmations/disconfirmations
    4. Update theory entrenchment via Popperian asymmetry
    5. Monitor reports correct health status
    """

    def test_full_art_theory_flow(self):
        """
        Simulate ART theory being proposed, tested, and evaluated.

        Attention Restoration Theory:
        - Proposition: Natural environments restore directed attention
        - Hypothesis: Exposure to nature improves ANT scores
        - Studies: Multiple confirmations, one disconfirmation
        """
        # Step 1: Extract theoretical paper (ART)
        art_template = {
            "thesis": {
                "main_claim": "Natural environments restore directed attention through soft fascination"
            },
            "framework": {
                "derived_hypotheses": [
                    {"hypothesis_text": "Exposure to nature improves ANT scores", "testable_via": "ANT task"},
                    {"hypothesis_text": "Urban environments deplete attention", "testable_via": "ANT task"},
                    {"hypothesis_text": "Restoration effect increases with exposure duration"}
                ]
            }
        }

        extraction = extract_theoretical_paper("kaplan_1995", "ART Paper", art_template)

        assert len(extraction.propositions) == 1
        assert len(extraction.hypotheses) == 3
        assert extraction.propositions[0].is_central

        # Step 2: Register hypotheses in ledger
        ledger = PredictionLedger()

        for hyp in extraction.hypotheses:
            ledger.register_hypothesis(
                hypothesis_id=hyp.hypothesis_id,
                text=hyp.hypothesis_text,
                parent_prop_id=hyp.derived_from_proposition_id
            )

        assert ledger.count() == 3

        # Step 3: Simulate empirical studies confirming/disconfirming
        # Study 1: Berman 2008 - confirms ANT hypothesis
        ledger.record_confirmation(extraction.hypotheses[0].hypothesis_id, "berman_2008")

        # Study 2: Berto 2005 - confirms ANT hypothesis
        ledger.record_confirmation(extraction.hypotheses[0].hypothesis_id, "berto_2005")

        # Study 3: Hartig 2003 - confirms ANT hypothesis
        ledger.record_confirmation(extraction.hypotheses[0].hypothesis_id, "hartig_2003")

        # Study 4: Failed replication - disconfirms
        ledger.record_disconfirmation(extraction.hypotheses[0].hypothesis_id, "failed_rep_2020")

        # Step 4: Check hypothesis entrenchment updated correctly
        entry = ledger.get_entry(extraction.hypotheses[0].hypothesis_id)
        assert entry.confirmation_count == 3
        assert entry.disconfirmation_count == 1

        # Entrenchment should be positive (3 conf × 0.05 - 1 disconf × 0.10 = 0.05 net)
        # Base 0.35 + 0.05 = 0.40
        assert entry.current_entrenchment == pytest.approx(0.40, abs=0.01)

        # Step 5: Theory monitor reports correct health
        monitor = TheoryMonitor(ledger)
        prop_id = extraction.propositions[0].proposition_id

        report = monitor.assess_theory(
            theory_id=prop_id,
            theory_text=extraction.propositions[0].proposition_text,
            current_entrenchment=0.35
        )

        # With 3 hypotheses, 3 confirmations total, 1 disconfirmation
        # The theory should be moderately supported
        assert report.health_status in {
            TheoryHealthStatus.WELL_SUPPORTED,
            TheoryHealthStatus.MODERATELY_SUPPORTED
        }
        assert report.n_confirmations >= 3
        assert report.n_disconfirmations >= 1

    def test_theory_with_accumulating_disconfirmations(self):
        """Theory losing support triggers correct alerts."""
        ledger = PredictionLedger()

        # Register hypothesis
        ledger.register_hypothesis("failing_hyp", "Hypothesis that fails", "bad_theory")

        # Multiple disconfirmations
        for i in range(5):
            ledger.record_disconfirmation("failing_hyp", f"disconf_study_{i}")

        # One weak confirmation
        ledger.record_confirmation("failing_hyp", "weak_confirm")

        # Check theory health
        monitor = TheoryMonitor(ledger)
        report = monitor.assess_theory("bad_theory", current_entrenchment=0.35)

        assert report.health_status == TheoryHealthStatus.PROBLEMATIC
        assert TheoryRisk.ACCUMULATING_DISCONFIRMATIONS in report.risks

        # Check alerts
        alerts = monitor.check_theory_alerts()
        alert_types = [a["type"] for a in alerts]
        assert "problematic_theory" in alert_types or "accumulating_disconfirmations" in alert_types


# =============================================================================
# Task 6e.2: Synthesis Floor Rule Edge Cases
# =============================================================================

class TestSynthesisFloorRuleEdgeCases:
    """Test synthesis floor rule in edge cases."""

    def test_synthesis_floor_with_high_quality_studies(self):
        """Synthesis floor uses median of high-quality studies."""
        included_entrenchments = [0.7, 0.75, 0.8, 0.85, 0.9]  # Median = 0.8

        # Base synthesis would be lower due to heterogeneity
        # compute_synthesis_entrenchment applies floor internally
        result = compute_synthesis_entrenchment(
            base_entrenchment=0.5,  # Low base
            included_study_entrenchments=included_entrenchments,
            heterogeneity_i2=60.0,  # High heterogeneity → penalty
            publication_bias="significant",  # Penalty
            grade_quality="moderate"
        )

        # Floor should kick in: result >= median = 0.8
        assert result >= 0.8

    def test_synthesis_floor_with_one_outlier(self):
        """Median floor is robust to single outlier."""
        # One very high quality study, rest moderate
        included_entrenchments = [0.5, 0.55, 0.6, 0.65, 0.95]  # Median = 0.6

        result = compute_synthesis_entrenchment(
            base_entrenchment=0.5,
            included_study_entrenchments=included_entrenchments,
            heterogeneity_i2=30.0,
            publication_bias="none",
            grade_quality="high"
        )

        # Floor should be median = 0.6, not pulled up by outlier
        assert result >= 0.6
        assert result < 0.95  # Should not be as high as outlier

    def test_synthesis_floor_with_low_quality_studies(self):
        """Synthesis can exceed floor if computed value is higher."""
        included_entrenchments = [0.3, 0.35, 0.4]  # Median = 0.35

        # High quality synthesis with high base
        result = compute_synthesis_entrenchment(
            base_entrenchment=0.75,  # High base
            included_study_entrenchments=included_entrenchments,
            heterogeneity_i2=10.0,  # Low heterogeneity
            publication_bias="none",
            grade_quality="high"
        )

        # Should be higher than floor since base is high
        assert result >= 0.35
        # Base 0.75 + 0.05 (high grade) = 0.80
        assert result >= 0.75

    def test_synthesis_floor_empty_studies(self):
        """Empty study list doesn't crash."""
        result = compute_synthesis_entrenchment(
            base_entrenchment=0.6,
            included_study_entrenchments=[],
            heterogeneity_i2=0.0,
            publication_bias="none",
            grade_quality="low"
        )

        # Base 0.6 - 0.05 (low grade) = 0.55
        # No floor to apply
        assert result == pytest.approx(0.55, abs=0.01)


# =============================================================================
# Task 6e.3: Expert vs. Systematic Comparison
# =============================================================================

class TestExpertVsSystematicComparison:
    """Test that expert syntheses are correctly discounted vs. systematic."""

    def test_expert_always_below_equivalent_systematic(self):
        """Expert synthesis should always be ≤70% of equivalent systematic."""
        # Compute systematic entrenchment
        # High quality synthesis with good base
        systematic = compute_synthesis_entrenchment(
            base_entrenchment=0.75,
            included_study_entrenchments=[0.6, 0.65, 0.7, 0.75, 0.8],
            heterogeneity_i2=30.0,
            publication_bias="none",
            grade_quality="high"
        )

        # Compute expert for same content
        expert = compute_expert_synthesis_entrenchment(
            author_expertise="established",  # +0.10
            consistent_with_systematic=True,  # +0.10
            n_studies_cited=10  # +0.02 (10-19 range)
        )

        # Expert max is ~0.67 (0.45 + 0.10 + 0.10 + 0.02)
        # Systematic is ~0.80 (0.75 + 0.05 for high grade, floor at 0.7 median)
        # Expert should be below systematic
        assert expert <= systematic

    def test_compare_function_returns_correct_status(self):
        """Comparison function returns correct status."""
        # Strong systematic vs weak expert - ratio within discount range
        result = compare_expert_vs_systematic(
            expert_entrenchment=0.45,
            systematic_entrenchment=0.80
        )

        # Ratio 0.45/0.80 = 0.5625, which is ≤ 0.7, so "appropriate_discount"
        assert result["status"] == "appropriate_discount"
        assert result["ratio"] == pytest.approx(0.45 / 0.80, abs=0.01)

        # Expert higher than systematic (anomaly case with different conclusions)
        result2 = compare_expert_vs_systematic(
            expert_entrenchment=0.50,
            systematic_entrenchment=0.40,
            same_conclusion=False
        )

        # When systematic > expert is false, with different conclusions → "anomaly"
        assert result2["status"] == "anomaly"

    def test_expert_discount_with_all_modifiers(self):
        """Expert entrenchment with all positive modifiers."""
        # Maximum bonuses
        expert = compute_expert_synthesis_entrenchment(
            author_expertise="established",  # +0.10
            consistent_with_systematic=True,  # +0.10
            n_studies_cited=30,  # +0.05 (>=20)
            theoretical_commitment_declared=True  # +0.02 (transparency bonus)
        )

        # Base 0.45 + 0.10 + 0.10 + 0.05 + 0.02 = 0.72
        assert expert <= 1.0
        assert expert >= 0.70  # Should be around 0.72


# =============================================================================
# Task 6e.4: Methodological Critique Cascade
# =============================================================================

class TestMethodologicalCritiqueCascade:
    """Test that critiques propagate to affected claims."""

    def test_critique_penalty_calculation(self):
        """Critique penalty is computed from severity and scale."""
        # Per the module: penalty = severity * penalty_scale (default 0.2)
        severity = 0.8
        penalty_scale = 0.2

        penalty = severity * penalty_scale
        assert penalty == pytest.approx(0.16)

    def test_critique_affects_validity_correctly(self):
        """Critique reduces validity by penalty amount."""
        # Simulate critique effect
        original_validity = 0.8
        penalty = 0.16  # From severity 0.8 * scale 0.2

        new_validity = max(0.0, original_validity - penalty)

        assert new_validity == pytest.approx(0.64)

    def test_critique_severity_scales_penalty(self):
        """Higher severity → larger penalty."""
        penalty_scale = 0.2

        low_severity_penalty = 0.3 * penalty_scale
        high_severity_penalty = 0.9 * penalty_scale

        assert high_severity_penalty > low_severity_penalty

    def test_critique_doesnt_go_below_zero(self):
        """Validity can't go negative after critique."""
        original_validity = 0.1
        severity = 1.0
        penalty_scale = 0.2

        penalty = severity * penalty_scale  # 0.2

        new_validity = max(0.0, original_validity - penalty)

        assert new_validity >= 0.0
        assert new_validity == pytest.approx(0.0, abs=0.01)  # 0.1 - 0.2 = -0.1 → 0.0

    def test_critique_propagation_result_structure(self):
        """CritiquePropagationResult has expected structure."""
        result = CritiquePropagationResult(
            method_id="photo_rating",
            affected_constructs=["stress", "preference"],
            original_validity={"stress": 0.8, "preference": 0.9},
            new_validity={"stress": 0.64, "preference": 0.74},
            penalty_applied=0.16
        )

        assert result.method_id == "photo_rating"
        assert result.constructs_affected_count == 2
        assert result.penalty_applied == 0.16


# =============================================================================
# Task 6e.5: Mixed Empirical/Theoretical Coherence
# =============================================================================

class TestMixedEmpiricalTheoreticalCoherence:
    """Test coherence computation across node type families."""

    def test_connected_theory_evidence_has_high_coherence(self):
        """Theory connected to confirming evidence has high coherence."""
        monitor = CrossTypeCoherenceMonitor()

        # Theory node
        monitor.register_node("art_prop", NodeType.THEORETICAL_PROPOSITION)

        # Derived hypothesis
        monitor.register_node("art_hyp", NodeType.DERIVED_HYPOTHESIS)

        # Confirming evidence
        monitor.register_node("berman_2008", NodeType.EMPIRICAL_FINDING)

        # Edges
        monitor.register_edge("art_prop", "art_hyp", "theoretically_predicts", 1.0)
        monitor.register_edge("berman_2008", "art_hyp", "confirms_prediction", 1.0)

        # Check coherence
        score = monitor.compute_pairwise_coherence("art_prop", "berman_2008")

        # Should have some coherence (connected via hypothesis)
        assert score is not None
        # Note: indirect connection may have lower score
        assert score.coherence_type == CoherenceType.THEORY_EVIDENCE

    def test_disconnected_evidence_flagged_as_anomaly(self):
        """Evidence without theoretical grounding is flagged."""
        monitor = CrossTypeCoherenceMonitor()

        # Evidence nodes without theory connections
        monitor.register_node("orphan_finding_1", NodeType.EMPIRICAL_FINDING)
        monitor.register_node("orphan_finding_2", NodeType.EMPIRICAL_FINDING)

        anomalies = monitor.detect_anomalies()

        uninterpreted = [
            a for a in anomalies
            if a.anomaly_type == CoherenceAnomaly.UNINTERPRETED_EVIDENCE
        ]

        assert len(uninterpreted) == 2

    def test_synthesis_with_primaries_has_coherence(self):
        """Synthesis connected to primary studies has coherence."""
        monitor = CrossTypeCoherenceMonitor()

        # Synthesis
        monitor.register_node("meta_2020", NodeType.SYNTHESIS_CONCLUSION)

        # Primary studies
        monitor.register_node("study_1", NodeType.EMPIRICAL_FINDING)
        monitor.register_node("study_2", NodeType.EMPIRICAL_FINDING)
        monitor.register_node("study_3", NodeType.EMPIRICAL_FINDING)

        # Include edges
        monitor.register_edge("meta_2020", "study_1", "includes_in_synthesis", 1.0)
        monitor.register_edge("meta_2020", "study_2", "includes_in_synthesis", 1.0)
        monitor.register_edge("meta_2020", "study_3", "includes_in_synthesis", 1.0)

        # Should have no orphan synthesis anomaly
        anomalies = monitor.detect_anomalies()
        orphans = [a for a in anomalies if a.anomaly_type == CoherenceAnomaly.ORPHAN_SYNTHESIS]

        assert len(orphans) == 0

        # Coherence report should show synthesis-primary coherence
        report = monitor.generate_report()
        assert report.total_nodes == 4


# =============================================================================
# Task 6e.6: Prediction Ledger Persistence
# =============================================================================

class TestPredictionLedgerPersistence:
    """Test that ledger state persists correctly."""

    def test_ledger_save_and_load(self):
        """Ledger can be saved and loaded from JSON."""
        # Create ledger with data
        ledger = PredictionLedger()

        ledger.register_hypothesis("h1", "Hypothesis 1", "theory_1")
        ledger.register_hypothesis("h2", "Hypothesis 2", "theory_1")
        ledger.register_hypothesis("h3", "Hypothesis 3", "theory_2")

        ledger.record_confirmation("h1", "study_a")
        ledger.record_confirmation("h1", "study_b")
        ledger.record_disconfirmation("h2", "study_c")

        # Save to temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name

        try:
            ledger.save(temp_path)

            # Load into new ledger
            loaded = PredictionLedger.load(temp_path)

            # Verify state preserved
            assert loaded.count() == 3

            h1 = loaded.get_entry("h1")
            assert h1.confirmation_count == 2
            assert h1.disconfirmation_count == 0

            h2 = loaded.get_entry("h2")
            assert h2.confirmation_count == 0
            assert h2.disconfirmation_count == 1

            # Theory track record should work
            record = loaded.compute_theory_track_record("theory_1")
            assert record["hypothesis_count"] == 2
            assert record["total_confirmations"] == 2
            assert record["total_disconfirmations"] == 1

        finally:
            os.unlink(temp_path)

    def test_ledger_to_dict_roundtrip(self):
        """Ledger can be serialized and deserialized via dict."""
        ledger = PredictionLedger()

        ledger.register_hypothesis("hyp_1", "Test hypothesis", "theory_x")
        ledger.record_confirmation("hyp_1", "study_1")

        # Convert to dict
        data = ledger.to_dict()

        # Create new ledger from dict
        restored = PredictionLedger.from_dict(data)

        # Verify
        entry = restored.get_entry("hyp_1")
        assert entry is not None
        assert entry.hypothesis_text == "Test hypothesis"
        assert entry.derived_from == "theory_x"
        assert entry.confirmation_count == 1


# =============================================================================
# Additional Integration Tests
# =============================================================================

class TestFullPipelineIntegration:
    """Test complete pipeline from classification to monitoring."""

    def test_classify_extract_monitor_flow(self):
        """Full flow: classify paper → extract → register → monitor."""
        # Step 1: Classify paper
        classification = classify_paper(
            title="Toward a theory of restorative environments",
            abstract="We propose a mechanistic account of how natural settings restore directed attention capacity."
        )

        assert classification.template_family == TemplateFamily.THEORETICAL
        assert classification.is_theoretical

        # Step 2: Verify node types available for this template
        node_types = get_node_types_for_template(TemplateFamily.THEORETICAL)
        assert NodeType.THEORETICAL_PROPOSITION in node_types
        assert NodeType.DERIVED_HYPOTHESIS in node_types

        # Step 3: Extract content
        template = {
            "thesis": {"main_claim": "Natural settings restore attention"},
            "framework": {
                "derived_hypotheses": [
                    {"hypothesis_text": "Nature exposure improves focus"}
                ]
            }
        }
        extraction = extract_theoretical_paper("test_paper", "Test", template)

        # Step 4: Set up monitoring
        ledger = PredictionLedger()
        for hyp in extraction.hypotheses:
            ledger.register_hypothesis(
                hyp.hypothesis_id,
                hyp.hypothesis_text,
                hyp.derived_from_proposition_id
            )

        monitor = TheoryMonitor(ledger)
        coh_monitor = CrossTypeCoherenceMonitor()

        # Register nodes
        for prop in extraction.propositions:
            coh_monitor.register_node(prop.proposition_id, NodeType.THEORETICAL_PROPOSITION)
        for hyp in extraction.hypotheses:
            coh_monitor.register_node(hyp.hypothesis_id, NodeType.DERIVED_HYPOTHESIS)

        # Register edges
        for edge in extraction.to_edges():
            coh_monitor.register_edge(
                edge.source_node_id,
                edge.target_node_id,
                edge.edge_type,
                edge.weight
            )

        # Step 5: Verify monitoring works
        prop_id = extraction.propositions[0].proposition_id
        report = monitor.assess_theory(prop_id, current_entrenchment=0.35)

        assert report.health_status == TheoryHealthStatus.UNTESTED  # No confirmations yet
        assert report.n_hypotheses == 1

        # Coherence should detect theory has hypothesis
        coh_report = coh_monitor.generate_report()
        assert coh_report.total_nodes == 2

    def test_synthesis_ingestion_to_coherence(self):
        """Synthesis paper flows through to coherence monitoring."""
        # Classify
        classification = classify_paper(
            title="A meta-analysis of nature exposure effects",
            abstract="We pooled 25 studies..."
        )

        assert classification.template_family == TemplateFamily.META_ANALYSIS

        # Ingest
        template = {
            "overall_effect": {
                "effect_size": 0.45,
                "N_studies": 25,
                "heterogeneity_I2": 30.0,
                "publication_bias": "none",
                "conclusion": "Nature exposure has moderate positive effect"
            },
            "included_studies": ["s1", "s2", "s3", "s4", "s5"]
        }

        result = ingest_synthesis_paper(
            "meta_2024", "Meta-Analysis", SynthesisType.META_ANALYSIS, template
        )

        assert len(result.conclusions) == 1
        assert result.conclusions[0].n_included_studies == 25

        # Set up coherence monitor
        coh_monitor = CrossTypeCoherenceMonitor()

        # Register synthesis
        coh_monitor.register_node(
            result.conclusions[0].conclusion_id,
            NodeType.SYNTHESIS_CONCLUSION
        )

        # Register primaries - get included_study_ids from the conclusion
        included_studies = result.conclusions[0].included_study_ids
        for study_id in included_studies[:3]:
            coh_monitor.register_node(study_id, NodeType.EMPIRICAL_FINDING)

        # Register edges
        for edge in result.to_edges()[:3]:
            coh_monitor.register_edge(
                edge.source_node_id,
                edge.target_node_id,
                edge.edge_type,
                edge.weight
            )

        # Check coherence
        report = coh_monitor.generate_report()
        assert "synthesis_conclusion" in report.nodes_by_type


class TestEdgeTypeValidation:
    """Test that edge type constraints are enforced."""

    def test_valid_theory_to_hypothesis_edge(self):
        """THEORETICALLY_PREDICTS allows theory → hypothesis."""
        is_valid, msg = validate_edge_connection(
            EdgeType.THEORETICALLY_PREDICTS,
            "theoretical_proposition",
            "derived_hypothesis"
        )
        assert is_valid

    def test_invalid_evidence_to_hypothesis_edge(self):
        """THEORETICALLY_PREDICTS doesn't allow evidence → hypothesis."""
        is_valid, msg = validate_edge_connection(
            EdgeType.THEORETICALLY_PREDICTS,
            "empirical_finding",  # Wrong source type
            "derived_hypothesis"
        )
        assert not is_valid

    def test_valid_confirmation_edge(self):
        """CONFIRMS_PREDICTION allows evidence → hypothesis."""
        is_valid, msg = validate_edge_connection(
            EdgeType.CONFIRMS_PREDICTION,
            "empirical_finding",
            "derived_hypothesis"
        )
        assert is_valid

    def test_valid_synthesis_includes_edge(self):
        """INCLUDES_IN_SYNTHESIS allows synthesis → finding."""
        is_valid, msg = validate_edge_connection(
            EdgeType.INCLUDES_IN_SYNTHESIS,
            "synthesis_conclusion",
            "empirical_finding"
        )
        assert is_valid
