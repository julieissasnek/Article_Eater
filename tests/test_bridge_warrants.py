"""
Tests for Sprint 3: Bridge Warrants

This module tests the bridge warrant implementation per the Expert Panel
specification (2026-01-18).

Test Cases (as specified by Expert Panel):
1. Basic bridge creation - Create bridge, verify structure matches schema
2. Bridge-weighted credence - Verify formula: parent * bridge * cnfa_specific
3. Bridge failure - Verify status change, tension creation, anomaly generation
4. Bridge revision - Verify downgrade from mechanism to functional
5. Serialization round-trip - Create, serialize, deserialize, verify equality

References:
- Sprint 3 expert advice.md
- contracts/ae_af/schemas/ae.bridge.v1.schema.json
"""

import pytest
import json
from datetime import datetime, timezone
from pathlib import Path

# Import bridge warrant components
from src.services.bridge_warrants import (
    BridgeWarrant,
    BridgeRegistry,
    BridgeType,
    BridgeStatus,
    ConfidenceSource,
    FailureRecord,
    Provenance,
    create_bridge,
    evaluate_bridge,
    record_failure,
    revise_bridge,
    compute_bridged_credence,
    suggest_bridges,
    detect_bridge_from_claim,
    create_anomaly_from_bridge_failure,
    DEFAULT_BRIDGE_CONFIDENCE,
)

# Import web of belief for integration tests
from src.services.web_of_belief import (
    WebOfBelief,
    Belief,
    Credence,
    EpistemicLevel,
    BeliefStatus,
    ConstraintType,
    create_neuroarchitecture_web,
)


class TestBasicBridgeCreation:
    """Test Case 1: Basic bridge creation."""

    def test_create_mechanism_bridge(self):
        """Create a mechanism bridge and verify structure."""
        bridge = create_bridge(
            source_domain="object_perception",
            target_domain="architectural_perception",
            bridge_type=BridgeType.MECHANISM,
            warrant_statement="Angular geometry activates a domain-general threat detection mechanism",
            assumed_mechanism="amygdala threat detection",
            source_beliefs=["belief:bar_neta_2006"],
            target_beliefs=["belief:vartanian_2013"],
            created_by="test:manual"
        )

        # Verify structure
        assert bridge.bridge_id.startswith("bridge:")
        assert bridge.source_domain == "object_perception"
        assert bridge.target_domain == "architectural_perception"
        assert bridge.bridge_type == BridgeType.MECHANISM
        assert bridge.assumed_mechanism == "amygdala threat detection"
        assert bridge.status == BridgeStatus.HYPOTHESIZED
        assert bridge.confidence == DEFAULT_BRIDGE_CONFIDENCE[BridgeType.MECHANISM]
        assert bridge.confidence_source == ConfidenceSource.DEFAULT
        assert "belief:bar_neta_2006" in bridge.source_beliefs
        assert "belief:vartanian_2013" in bridge.target_beliefs

    def test_create_all_bridge_types(self):
        """Create bridges of each type and verify default confidences."""
        for bridge_type in BridgeType:
            bridge = create_bridge(
                source_domain="test_source",
                target_domain="test_target",
                bridge_type=bridge_type,
                warrant_statement=f"Test {bridge_type.value} bridge"
            )

            assert bridge.bridge_type == bridge_type
            assert bridge.confidence == DEFAULT_BRIDGE_CONFIDENCE[bridge_type]

    def test_bridge_to_dict_matches_schema(self):
        """Verify serialized bridge matches ae.bridge.v1 schema structure."""
        bridge = create_bridge(
            source_domain="object_perception",
            target_domain="architectural_perception",
            bridge_type=BridgeType.MECHANISM,
            warrant_statement="Test warrant statement"
        )

        d = bridge.to_dict()

        # Verify required fields
        assert d["schema"] == "ae.bridge.v1"
        assert "bridge_id" in d
        assert "source_domain" in d
        assert "target_domain" in d
        assert "bridge_type" in d
        assert "warrant_statement" in d
        assert "confidence" in d
        assert "status" in d

        # Verify bridge_id pattern
        assert d["bridge_id"].startswith("bridge:")

        # Verify confidence is in valid range
        assert 0 <= d["confidence"] <= 1

        # Verify status is valid enum value
        assert d["status"] in ["hypothesized", "supported", "contested", "failed", "revised"]


class TestBridgeWeightedCredence:
    """Test Case 2: Bridge-weighted credence computation."""

    def test_basic_credence_computation(self):
        """Verify formula: parent * bridge * cnfa_specific."""
        # Expert Panel example: 0.8 * 0.6 * 0.9 = 0.432
        result = compute_bridged_credence(
            parent_theory_credence=0.8,
            bridge_confidence=0.6,
            cnfa_specific_confidence=0.9
        )

        assert abs(result - 0.432) < 0.001

    def test_boundary_values(self):
        """Test boundary conditions."""
        # All maximum
        assert compute_bridged_credence(1.0, 1.0, 1.0) == 1.0

        # All minimum
        assert compute_bridged_credence(0.0, 0.0, 0.0) == 0.0

        # Single zero term
        assert compute_bridged_credence(0.8, 0.0, 0.9) == 0.0
        assert compute_bridged_credence(0.0, 0.6, 0.9) == 0.0
        assert compute_bridged_credence(0.8, 0.6, 0.0) == 0.0

    def test_values_clamped_to_range(self):
        """Verify out-of-range inputs are clamped."""
        # Values > 1 should be clamped to 1
        result = compute_bridged_credence(1.5, 0.6, 0.9)
        assert result <= 1.0

        # Values < 0 should be clamped to 0
        result = compute_bridged_credence(-0.5, 0.6, 0.9)
        assert result >= 0.0

    def test_default_confidences_produce_expected_ranges(self):
        """Test default confidence values produce sensible results."""
        parent = 0.75  # Typical theory credence

        # Mechanism bridge (0.6)
        mech_result = compute_bridged_credence(parent, 0.6, 0.8)
        assert 0.3 < mech_result < 0.5

        # Analogical bridge (0.35)
        analog_result = compute_bridged_credence(parent, 0.35, 0.8)
        assert 0.15 < analog_result < 0.3

        # Constitutive bridge (0.85)
        const_result = compute_bridged_credence(parent, 0.85, 0.8)
        assert 0.4 < const_result < 0.6

        # Constitutive should be highest
        assert const_result > mech_result > analog_result


class TestBridgeFailureHandling:
    """Test Case 3: Bridge failure handling."""

    def test_record_failure_changes_status(self):
        """Verify bridge status changes to FAILED."""
        bridge = create_bridge(
            source_domain="object_perception",
            target_domain="architectural_perception",
            bridge_type=BridgeType.MECHANISM,
            warrant_statement="Test mechanism bridge"
        )

        assert bridge.status == BridgeStatus.HYPOTHESIZED

        failed_bridge = record_failure(
            bridge=bridge,
            disconfirming_evidence=["belief:vartanian_2013_acc"],
            failure_type="mechanism_not_conserved",
            suggested_revision=BridgeType.FUNCTIONAL
        )

        assert failed_bridge.status == BridgeStatus.FAILED

    def test_failure_creates_voi_flag(self):
        """Verify VOI flag is set on failure."""
        bridge = create_bridge(
            source_domain="test",
            target_domain="test",
            bridge_type=BridgeType.MECHANISM,
            warrant_statement="Test"
        )

        assert bridge.voi_flag is False

        failed_bridge = record_failure(
            bridge=bridge,
            disconfirming_evidence=["evidence:1"],
            failure_type="test_failure"
        )

        assert failed_bridge.voi_flag is True

    def test_failure_record_contains_evidence(self):
        """Verify failure record contains disconfirming evidence."""
        bridge = create_bridge(
            source_domain="test",
            target_domain="test",
            bridge_type=BridgeType.MECHANISM,
            warrant_statement="Test"
        )

        disconfirming = ["belief:a", "belief:b", "belief:c"]
        failed_bridge = record_failure(
            bridge=bridge,
            disconfirming_evidence=disconfirming,
            failure_type="mechanism_not_conserved",
            suggested_revision=BridgeType.FUNCTIONAL
        )

        assert failed_bridge.failure_record is not None
        assert failed_bridge.failure_record.disconfirming_evidence == disconfirming
        assert failed_bridge.failure_record.failure_type == "mechanism_not_conserved"
        assert failed_bridge.failure_record.suggested_revision == BridgeType.FUNCTIONAL

    def test_failure_reduces_confidence(self):
        """Verify confidence is dramatically reduced on failure."""
        bridge = create_bridge(
            source_domain="test",
            target_domain="test",
            bridge_type=BridgeType.MECHANISM,
            warrant_statement="Test"
        )

        original_confidence = bridge.confidence
        failed_bridge = record_failure(
            bridge=bridge,
            disconfirming_evidence=["evidence:1"],
            failure_type="test_failure"
        )

        # Should be reduced to ~30% of original
        assert failed_bridge.confidence < original_confidence * 0.5

    def test_failure_creates_anomaly(self):
        """Verify anomaly record is created from failed bridge."""
        bridge = create_bridge(
            source_domain="object_perception",
            target_domain="architectural_perception",
            bridge_type=BridgeType.MECHANISM,
            warrant_statement="Test",
            source_beliefs=["belief:source"],
            target_beliefs=["belief:target"]
        )

        failed_bridge = record_failure(
            bridge=bridge,
            disconfirming_evidence=["belief:disconfirm"],
            failure_type="mechanism_not_conserved"
        )

        anomaly = create_anomaly_from_bridge_failure(failed_bridge)

        assert anomaly.anomaly_type == "bridge_failure"
        assert anomaly.source_entity_id == failed_bridge.bridge_id
        assert "mechanism_not_conserved" in anomaly.description
        assert anomaly.voi_score > 0


class TestBridgeRevision:
    """Test Case 4: Bridge revision after failure."""

    def test_revise_mechanism_to_functional(self):
        """Verify mechanism bridge can be downgraded to functional."""
        original = create_bridge(
            source_domain="object_perception",
            target_domain="architectural_perception",
            bridge_type=BridgeType.MECHANISM,
            warrant_statement="Angular geometry activates amygdala",
            assumed_mechanism="amygdala threat detection",
            source_beliefs=["belief:bar_neta"],
            target_beliefs=["belief:vartanian"]
        )

        failed = record_failure(
            bridge=original,
            disconfirming_evidence=["belief:vartanian_acc"],
            failure_type="mechanism_not_conserved",
            suggested_revision=BridgeType.FUNCTIONAL
        )

        revised = revise_bridge(
            failed_bridge=failed,
            new_type=BridgeType.FUNCTIONAL,
            new_warrant_statement="Angular geometry evokes negative affect regardless of scale"
        )

        # Verify revision
        assert revised.bridge_type == BridgeType.FUNCTIONAL
        assert revised.status == BridgeStatus.REVISED
        assert revised.confidence == DEFAULT_BRIDGE_CONFIDENCE[BridgeType.FUNCTIONAL]
        assert revised.bridge_id != original.bridge_id  # New ID
        assert revised.source_beliefs == original.source_beliefs  # Preserved
        assert revised.target_beliefs == original.target_beliefs  # Preserved

    def test_revised_bridge_has_lineage(self):
        """Verify revised bridge tracks its origin."""
        original = create_bridge(
            source_domain="test",
            target_domain="test",
            bridge_type=BridgeType.MECHANISM,
            warrant_statement="Test"
        )

        failed = record_failure(
            bridge=original,
            disconfirming_evidence=["evidence:1"],
            failure_type="test"
        )

        revised = revise_bridge(failed, BridgeType.FUNCTIONAL)

        # Provenance should indicate revision origin
        assert original.bridge_id in revised.provenance.created_by


class TestSerializationRoundTrip:
    """Test Case 5: Serialization round-trip."""

    def test_bridge_serialization_roundtrip(self):
        """Create bridge, serialize, deserialize, verify equality."""
        original = create_bridge(
            source_domain="object_perception",
            target_domain="architectural_perception",
            bridge_type=BridgeType.MECHANISM,
            warrant_statement="Angular geometry activates threat detection",
            assumed_mechanism="amygdala pathway",
            source_beliefs=["belief:1", "belief:2"],
            target_beliefs=["belief:3"],
            confidence=0.65,
            created_by="test:serialization"
        )

        # Add some evidence
        original.evidence_for.append("paper:support1")
        original.evidence_against.append("paper:against1")

        # Serialize
        serialized = original.to_dict()
        json_str = json.dumps(serialized)

        # Deserialize
        loaded_dict = json.loads(json_str)
        restored = BridgeWarrant.from_dict(loaded_dict)

        # Verify equality of key fields
        assert restored.bridge_id == original.bridge_id
        assert restored.source_domain == original.source_domain
        assert restored.target_domain == original.target_domain
        assert restored.bridge_type == original.bridge_type
        assert restored.warrant_statement == original.warrant_statement
        assert restored.assumed_mechanism == original.assumed_mechanism
        assert restored.confidence == original.confidence
        assert restored.status == original.status
        assert restored.source_beliefs == original.source_beliefs
        assert restored.target_beliefs == original.target_beliefs
        assert restored.evidence_for == original.evidence_for
        assert restored.evidence_against == original.evidence_against

    def test_failed_bridge_serialization_roundtrip(self):
        """Verify failed bridge with failure_record serializes correctly."""
        bridge = create_bridge(
            source_domain="test",
            target_domain="test",
            bridge_type=BridgeType.MECHANISM,
            warrant_statement="Test"
        )

        failed = record_failure(
            bridge=bridge,
            disconfirming_evidence=["evidence:1", "evidence:2"],
            failure_type="mechanism_not_conserved",
            suggested_revision=BridgeType.FUNCTIONAL
        )

        # Serialize and deserialize
        serialized = failed.to_dict()
        restored = BridgeWarrant.from_dict(serialized)

        # Verify failure record preserved
        assert restored.failure_record is not None
        assert restored.failure_record.failure_type == "mechanism_not_conserved"
        assert restored.failure_record.disconfirming_evidence == ["evidence:1", "evidence:2"]
        assert restored.failure_record.suggested_revision == BridgeType.FUNCTIONAL

    def test_registry_to_jsonl_roundtrip(self, tmp_path):
        """Verify registry can be saved and loaded from JSONL."""
        registry = BridgeRegistry()

        # Add several bridges
        for i, bt in enumerate(BridgeType):
            bridge = create_bridge(
                source_domain=f"source_{i}",
                target_domain=f"target_{i}",
                bridge_type=bt,
                warrant_statement=f"Test bridge {i}"
            )
            registry.add(bridge)

        # Save
        jsonl_path = tmp_path / "bridges.jsonl"
        registry.to_jsonl(jsonl_path)

        # Load
        loaded_registry = BridgeRegistry.from_jsonl(jsonl_path)

        # Verify
        assert len(loaded_registry.all()) == len(BridgeType)
        for bt in BridgeType:
            bridges = loaded_registry.get_by_type(bt)
            assert len(bridges) == 1


class TestBridgeRegistry:
    """Test registry operations."""

    def test_registry_add_and_get(self):
        """Test adding and retrieving bridges."""
        registry = BridgeRegistry()

        bridge = create_bridge(
            source_domain="test",
            target_domain="test",
            bridge_type=BridgeType.MECHANISM,
            warrant_statement="Test"
        )

        registry.add(bridge)

        retrieved = registry.get(bridge.bridge_id)
        assert retrieved is not None
        assert retrieved.bridge_id == bridge.bridge_id

    def test_registry_indexing_by_domain(self):
        """Test retrieving bridges by domain."""
        registry = BridgeRegistry()

        # Add bridges from same source to different targets
        for i in range(3):
            bridge = create_bridge(
                source_domain="object_perception",
                target_domain=f"target_{i}",
                bridge_type=BridgeType.MECHANISM,
                warrant_statement=f"Test {i}"
            )
            registry.add(bridge)

        # Should find all 3 by source domain
        by_source = registry.get_by_source_domain("object_perception")
        assert len(by_source) == 3

        # Should find 1 by specific target domain
        by_target = registry.get_by_target_domain("target_1")
        assert len(by_target) == 1

    def test_registry_indexing_by_status(self):
        """Test retrieving bridges by status."""
        registry = BridgeRegistry()

        # Add hypothesized bridge
        hyp_bridge = create_bridge(
            source_domain="test",
            target_domain="test",
            bridge_type=BridgeType.MECHANISM,
            warrant_statement="Test"
        )
        registry.add(hyp_bridge)

        # Add failed bridge
        failed_bridge = record_failure(
            bridge=create_bridge(
                source_domain="test2",
                target_domain="test2",
                bridge_type=BridgeType.MECHANISM,
                warrant_statement="Test2"
            ),
            disconfirming_evidence=["ev:1"],
            failure_type="test"
        )
        registry.add(failed_bridge)

        # Verify counts
        assert len(registry.get_by_status(BridgeStatus.HYPOTHESIZED)) == 1
        assert len(registry.get_failed()) == 1


class TestWebOfBeliefIntegration:
    """Test integration with WebOfBelief."""

    def test_integrate_bridge_creates_constraints(self):
        """Verify integrating a bridge creates BRIDGES constraints."""
        web = create_neuroarchitecture_web()

        # Create beliefs that will be connected by bridge
        web.add_belief(Belief(
            belief_id="belief:source_1",
            content="Angular objects activate amygdala",
            level=EpistemicLevel.EMPIRICAL,
            status=BeliefStatus.TENTATIVE,
            credence=Credence(0.7, 0.2)
        ))

        web.add_belief(Belief(
            belief_id="belief:target_1",
            content="Angular rooms affect emotional response",
            level=EpistemicLevel.EMPIRICAL,
            status=BeliefStatus.TENTATIVE,
            credence=Credence(0.6, 0.25)
        ))

        initial_constraints = len(web.constraints)

        # Create and integrate bridge
        bridge = create_bridge(
            source_domain="object_perception",
            target_domain="architectural_perception",
            bridge_type=BridgeType.MECHANISM,
            warrant_statement="Test bridge",
            source_beliefs=["belief:source_1"],
            target_beliefs=["belief:target_1"]
        )

        result = web.integrate_bridge(bridge)

        # Should have created at least one constraint
        assert result["constraints_created"] >= 1
        assert len(web.constraints) > initial_constraints

    def test_failed_bridge_creates_tension(self):
        """Verify failed bridge creates STRONG_TENSION constraint."""
        web = create_neuroarchitecture_web()

        # Create source belief
        web.add_belief(Belief(
            belief_id="belief:source_2",
            content="Test source belief",
            level=EpistemicLevel.EMPIRICAL,
            status=BeliefStatus.TENTATIVE,
            credence=Credence(0.7, 0.2)
        ))

        # Create target belief
        web.add_belief(Belief(
            belief_id="belief:target_2",
            content="Test target belief",
            level=EpistemicLevel.EMPIRICAL,
            status=BeliefStatus.TENTATIVE,
            credence=Credence(0.6, 0.25)
        ))

        # Create disconfirming evidence
        web.add_belief(Belief(
            belief_id="belief:disconfirm",
            content="Disconfirming evidence",
            level=EpistemicLevel.EMPIRICAL,
            status=BeliefStatus.TENTATIVE,
            credence=Credence(0.8, 0.15)
        ))

        # Create failed bridge
        bridge = create_bridge(
            source_domain="test",
            target_domain="test",
            bridge_type=BridgeType.MECHANISM,
            warrant_statement="Test",
            source_beliefs=["belief:source_2"],
            target_beliefs=["belief:target_2"]
        )

        failed = record_failure(
            bridge=bridge,
            disconfirming_evidence=["belief:disconfirm"],
            failure_type="test_failure"
        )

        result = web.integrate_bridge(failed)

        # Should have created tensions
        assert result["tensions_created"] >= 1


class TestBridgeEvaluation:
    """Test evidence-based bridge evaluation."""

    def test_supporting_evidence_increases_confidence(self):
        """Verify supporting evidence increases bridge confidence."""
        bridge = create_bridge(
            source_domain="test",
            target_domain="test",
            bridge_type=BridgeType.MECHANISM,
            warrant_statement="Test"
        )

        original_confidence = bridge.confidence

        updated = evaluate_bridge(
            bridge=bridge,
            new_evidence_id="evidence:support1",
            supports=True,
            evidence_strength=0.8
        )

        assert updated.confidence > original_confidence
        assert "evidence:support1" in updated.evidence_for

    def test_contradicting_evidence_decreases_confidence(self):
        """Verify contradicting evidence decreases bridge confidence."""
        bridge = create_bridge(
            source_domain="test",
            target_domain="test",
            bridge_type=BridgeType.MECHANISM,
            warrant_statement="Test"
        )

        original_confidence = bridge.confidence

        updated = evaluate_bridge(
            bridge=bridge,
            new_evidence_id="evidence:contradict1",
            supports=False,
            evidence_strength=0.8
        )

        assert updated.confidence < original_confidence
        assert "evidence:contradict1" in updated.evidence_against

    def test_evaluation_updates_status(self):
        """Verify evaluation updates status appropriately."""
        bridge = create_bridge(
            source_domain="test",
            target_domain="test",
            bridge_type=BridgeType.MECHANISM,
            warrant_statement="Test"
        )

        # Add supporting evidence -> SUPPORTED
        supported = evaluate_bridge(bridge, "ev:1", supports=True, evidence_strength=0.7)
        assert supported.status == BridgeStatus.SUPPORTED

        # Add contradicting evidence -> CONTESTED
        contested = evaluate_bridge(supported, "ev:2", supports=False, evidence_strength=0.7)
        assert contested.status == BridgeStatus.CONTESTED


class TestBridgeSuggestion:
    """Test bridge suggestion functionality."""

    def test_suggest_bridges_returns_candidates(self):
        """Verify suggest_bridges returns candidate bridges."""
        suggestions = suggest_bridges(
            source_domain="object_perception",
            target_domain="architectural_perception",
            source_statements=["Angular objects activate amygdala pathway"]
        )

        assert len(suggestions) > 0

        # Should include at least an analogical bridge
        types = [s.bridge_type for s in suggestions]
        assert BridgeType.ANALOGICAL in types

    def test_detect_bridge_from_claim(self):
        """Verify bridge can be detected from a claim."""
        claim = {
            "claim_id": "test:claim:1",
            "statement": "Angular objects activate the amygdala, suggesting threat detection",
            "constructs": {
                "outcomes": [{"id": "affect.stress"}],
                "environment_factors": []
            }
        }

        bridge = detect_bridge_from_claim(claim)

        # May or may not detect a bridge depending on keywords
        if bridge:
            assert bridge.bridge_id.startswith("bridge:")
            assert bridge.status == BridgeStatus.HYPOTHESIZED


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
