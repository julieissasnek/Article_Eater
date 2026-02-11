"""
Tests for Argument Attack Analysis (ATK-1, ATK-3)
=================================================

Tests structured metadata detection, shift classification,
and tension integration.
"""

import pytest
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional

from src.services.argument_attack import (
    AttackType,
    ContrastShiftType,
    ArgumentAttack,
    ShiftClassifier,
    StructuredAttackDetector,
    StructuredAttackEvidence,
    analyze_tension_as_attack,
    enhance_tension_with_attack_analysis,
    classify_from_structured_evidence,
)


# =============================================================================
# MOCK CLASSES FOR TESTING
# =============================================================================

@dataclass
class MockCredence:
    value: float
    uncertainty: float = 0.1


@dataclass
class MockConditionSpec:
    variable: str
    value: Any
    description: str
    contextual_meaning: Dict[str, str] = field(default_factory=dict)


@dataclass
class MockBaselineSpec:
    variable: str
    typical_value: float
    variance: float
    characterization: str
    source_studies: List[str] = field(default_factory=list)


@dataclass
class MockPopulationContext:
    population_id: str
    region: str = "unknown"
    baselines: Dict[str, MockBaselineSpec] = field(default_factory=dict)
    cultural_meanings: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MockContrastClass:
    contrast_id: str
    focal: MockConditionSpec
    contrasts: List[MockConditionSpec]
    population_context: Optional[MockPopulationContext] = None


@dataclass
class MockEnablingConditions:
    threshold: Optional[str] = None
    dosage_satisfies: List[str] = field(default_factory=list)


@dataclass
class MockBelief:
    belief_id: str
    content: str
    credence: MockCredence
    tags: List[str] = field(default_factory=list)
    theory_ids: Dict[str, float] = field(default_factory=dict)
    contrast_class: Optional[MockContrastClass] = None
    enabling_conditions: Optional[MockEnablingConditions] = None
    source_paper_id: str = "paper_001"


# =============================================================================
# TEST ATTACK TYPES AND SHIFT TYPES
# =============================================================================

class TestEnums:
    """Test attack type and shift type enums."""

    def test_attack_types(self):
        """All attack types are valid."""
        assert AttackType.CONFOUNDER.value == "confounder"
        assert AttackType.BOUNDARY_CONDITION.value == "boundary_condition"
        assert AttackType.REPLICATION.value == "replication"
        assert len(AttackType) == 8

    def test_shift_types(self):
        """All shift types are valid."""
        assert ContrastShiftType.PRESERVING.value == "preserving"
        assert ContrastShiftType.POPULATION_SHIFT.value == "population"
        assert ContrastShiftType.MEANING_SHIFT.value == "meaning"
        assert len(ContrastShiftType) == 6


# =============================================================================
# TEST TEXT-BASED SHIFT CLASSIFIER (ATK-3)
# =============================================================================

class TestShiftClassifier:
    """Test text-based heuristic classification."""

    def test_population_keywords(self):
        """Detect population shift from keywords."""
        shift_type, attack_type, dims = ShiftClassifier.classify_from_text(
            attack_claim="No effect in rural populations",
            original_content="Nature reduces stress in urban office workers",
            attack_content="Rural residents show no effect"
        )
        assert shift_type == ContrastShiftType.POPULATION_SHIFT
        assert any("population:" in d for d in dims)

    def test_baseline_keywords(self):
        """Detect baseline shift from keywords."""
        shift_type, attack_type, dims = ShiftClassifier.classify_from_text(
            attack_claim="Effect absent at high baseline",
            original_content="Improves mood from low baseline",
            attack_content="Saturated levels show ceiling effect"
        )
        assert shift_type == ContrastShiftType.BASELINE_SHIFT

    def test_preserving_no_keywords(self):
        """Preserve type when no shift keywords found."""
        shift_type, attack_type, dims = ShiftClassifier.classify_from_text(
            attack_claim="Failed to replicate the finding",
            original_content="X causes Y",
            attack_content="X does not cause Y"
        )
        assert shift_type == ContrastShiftType.PRESERVING
        assert attack_type == AttackType.REPLICATION

    def test_complex_shift_multiple_keywords(self):
        """Detect complex shift with multiple keyword types."""
        shift_type, attack_type, dims = ShiftClassifier.classify_from_text(
            attack_claim="Different population with different baseline and cultural context",
            original_content="Western urban participants",
            attack_content="Eastern rural participants with different cultural meaning"
        )
        assert shift_type == ContrastShiftType.COMPLEX_SHIFT

    def test_attack_type_confounder(self):
        """Classify confounder attack type."""
        _, attack_type, _ = ShiftClassifier.classify_from_text(
            attack_claim="Effect due to confounding variable",
            original_content="X causes Y",
            attack_content="Actually Z confounds this"
        )
        assert attack_type == AttackType.CONFOUNDER

    def test_attack_type_mechanism(self):
        """Classify mechanism attack type."""
        _, attack_type, _ = ShiftClassifier.classify_from_text(
            attack_claim="The proposed mechanism is incorrect",
            original_content="X mediates Y through pathway Z",
            attack_content="Wrong mechanism proposed"
        )
        assert attack_type == AttackType.MECHANISM


# =============================================================================
# TEST STRUCTURED METADATA DETECTION (No NLP)
# =============================================================================

class TestStructuredAttackDetector:
    """Test structured metadata-based detection."""

    def test_population_mismatch(self):
        """Detect population mismatch from PopulationContext."""
        pop_a = MockPopulationContext(
            population_id="urban_workers",
            region="USA"
        )
        pop_b = MockPopulationContext(
            population_id="rural_farmers",
            region="Brazil"
        )

        belief_a = MockBelief(
            belief_id="b1",
            content="Finding A",
            credence=MockCredence(0.7),
            contrast_class=MockContrastClass(
                contrast_id="cc1",
                focal=MockConditionSpec("treatment", "yes", "Treatment"),
                contrasts=[MockConditionSpec("treatment", "no", "Control")],
                population_context=pop_a
            )
        )
        belief_b = MockBelief(
            belief_id="b2",
            content="Finding B",
            credence=MockCredence(0.7),
            contrast_class=MockContrastClass(
                contrast_id="cc2",
                focal=MockConditionSpec("treatment", "yes", "Treatment"),
                contrasts=[MockConditionSpec("treatment", "no", "Control")],
                population_context=pop_b
            )
        )

        evidence = StructuredAttackDetector.detect_population_mismatch(belief_a, belief_b)
        assert evidence is not None
        assert evidence.evidence_type == "population_mismatch"
        assert evidence.confidence >= 0.8

    def test_baseline_shift_detection(self):
        """Detect significant baseline shift."""
        pop_a = MockPopulationContext(
            population_id="low_light",
            baselines={
                "light_exposure": MockBaselineSpec(
                    variable="light_exposure",
                    typical_value=500,
                    variance=100,
                    characterization="very_low"
                )
            }
        )
        pop_b = MockPopulationContext(
            population_id="high_light",
            baselines={
                "light_exposure": MockBaselineSpec(
                    variable="light_exposure",
                    typical_value=5000,
                    variance=500,
                    characterization="high"
                )
            }
        )

        belief_a = MockBelief(
            belief_id="b1",
            content="Light improves mood",
            credence=MockCredence(0.7),
            contrast_class=MockContrastClass(
                contrast_id="cc1",
                focal=MockConditionSpec("light", "bright", "Bright light"),
                contrasts=[MockConditionSpec("light", "dim", "Dim light")],
                population_context=pop_a
            )
        )
        belief_b = MockBelief(
            belief_id="b2",
            content="Light no effect on mood",
            credence=MockCredence(0.7),
            contrast_class=MockContrastClass(
                contrast_id="cc2",
                focal=MockConditionSpec("light", "bright", "Bright light"),
                contrasts=[MockConditionSpec("light", "dim", "Dim light")],
                population_context=pop_b
            )
        )

        evidence = StructuredAttackDetector.detect_baseline_shift(belief_a, belief_b)
        assert evidence is not None
        assert evidence.evidence_type == "baseline_shift"
        assert "light_exposure" in str(evidence.value_a)

    def test_contrast_condition_mismatch(self):
        """Detect different comparison conditions."""
        belief_a = MockBelief(
            belief_id="b1",
            content="Forest vs office",
            credence=MockCredence(0.7),
            contrast_class=MockContrastClass(
                contrast_id="cc1",
                focal=MockConditionSpec("environment", "forest", "Forest"),
                contrasts=[MockConditionSpec("environment", "office", "Office")]
            )
        )
        belief_b = MockBelief(
            belief_id="b2",
            content="Forest vs urban park",
            credence=MockCredence(0.7),
            contrast_class=MockContrastClass(
                contrast_id="cc2",
                focal=MockConditionSpec("environment", "forest", "Forest"),
                contrasts=[MockConditionSpec("environment", "urban_park", "Urban park")]
            )
        )

        evidence = StructuredAttackDetector.detect_contrast_condition_mismatch(belief_a, belief_b)
        assert evidence is not None
        assert evidence.evidence_type == "contrast_condition_mismatch"
        assert evidence.confidence >= 0.9

    def test_dosage_mismatch(self):
        """Detect dosage pattern differences."""
        belief_a = MockBelief(
            belief_id="b1",
            content="Short exposure effective",
            credence=MockCredence(0.7),
            enabling_conditions=MockEnablingConditions(
                dosage_satisfies=["brief", "single_session"]
            )
        )
        belief_b = MockBelief(
            belief_id="b2",
            content="Long exposure needed",
            credence=MockCredence(0.7),
            enabling_conditions=MockEnablingConditions(
                dosage_satisfies=["extended", "repeated"]
            )
        )

        evidence = StructuredAttackDetector.detect_dosage_mismatch(belief_a, belief_b)
        assert evidence is not None
        assert evidence.evidence_type == "dosage_mismatch"

    def test_measurement_mismatch(self):
        """Detect different outcome operationalizations."""
        belief_a = MockBelief(
            belief_id="b1",
            content="Reduces cortisol",
            credence=MockCredence(0.7),
            tags=["outcome:cortisol", "outcome:physiological"]
        )
        belief_b = MockBelief(
            belief_id="b2",
            content="Improves self-reported mood",
            credence=MockCredence(0.7),
            tags=["outcome:mood_self_report", "outcome:psychological"]
        )

        evidence = StructuredAttackDetector.detect_measurement_mismatch(belief_a, belief_b)
        assert evidence is not None
        assert evidence.evidence_type == "outcome_mismatch"

    def test_theory_conflict(self):
        """Detect different theoretical frameworks."""
        belief_a = MockBelief(
            belief_id="b1",
            content="Attention restoration",
            credence=MockCredence(0.7),
            theory_ids={"ART": 1.0}
        )
        belief_b = MockBelief(
            belief_id="b2",
            content="Stress reduction",
            credence=MockCredence(0.7),
            theory_ids={"SRT": 1.0}
        )

        evidence = StructuredAttackDetector.detect_theory_conflict(belief_a, belief_b)
        assert evidence is not None
        assert evidence.evidence_type == "theory_conflict"

    def test_detect_all_combines_evidence(self):
        """detect_all returns all applicable evidence."""
        pop_a = MockPopulationContext(population_id="pop_a", region="A")
        pop_b = MockPopulationContext(population_id="pop_b", region="B")

        belief_a = MockBelief(
            belief_id="b1",
            content="Finding A",
            credence=MockCredence(0.7),
            contrast_class=MockContrastClass(
                contrast_id="cc1",
                focal=MockConditionSpec("x", "yes", "X"),
                contrasts=[MockConditionSpec("x", "no", "Not X")],
                population_context=pop_a
            ),
            theory_ids={"Theory1": 1.0},
            tags=["outcome:mood"]
        )
        belief_b = MockBelief(
            belief_id="b2",
            content="Finding B",
            credence=MockCredence(0.7),
            contrast_class=MockContrastClass(
                contrast_id="cc2",
                focal=MockConditionSpec("x", "yes", "X"),
                contrasts=[MockConditionSpec("x", "no", "Not X")],
                population_context=pop_b
            ),
            theory_ids={"Theory2": 1.0},
            tags=["outcome:stress"]
        )

        evidence = StructuredAttackDetector.detect_all(belief_a, belief_b)
        evidence_types = {e.evidence_type for e in evidence}

        assert "population_mismatch" in evidence_types
        assert "theory_conflict" in evidence_types
        assert "outcome_mismatch" in evidence_types


# =============================================================================
# TEST CLASSIFICATION FROM STRUCTURED EVIDENCE
# =============================================================================

class TestClassifyFromStructuredEvidence:
    """Test shift classification from structured evidence."""

    def test_no_evidence_preserving(self):
        """No evidence means preserving (true contradiction)."""
        shift_type, attack_type, dims = classify_from_structured_evidence([])
        assert shift_type == ContrastShiftType.PRESERVING

    def test_population_evidence(self):
        """Population mismatch leads to population shift."""
        evidence = [StructuredAttackEvidence(
            evidence_type="population_mismatch",
            field_a="population",
            value_a="urban",
            field_b="population",
            value_b="rural",
            confidence=0.9,
            implication="Different populations"
        )]
        shift_type, attack_type, dims = classify_from_structured_evidence(evidence)
        assert shift_type == ContrastShiftType.POPULATION_SHIFT

    def test_multiple_evidence_complex(self):
        """Multiple evidence types lead to complex shift."""
        evidence = [
            StructuredAttackEvidence(
                evidence_type="population_mismatch",
                field_a="pop", value_a="A", field_b="pop", value_b="B",
                confidence=0.9, implication="Pop diff"
            ),
            StructuredAttackEvidence(
                evidence_type="baseline_shift",
                field_a="baseline", value_a="low", field_b="baseline", value_b="high",
                confidence=0.85, implication="Baseline diff"
            )
        ]
        shift_type, attack_type, dims = classify_from_structured_evidence(evidence)
        assert shift_type == ContrastShiftType.COMPLEX_SHIFT


# =============================================================================
# TEST ANALYZE TENSION AS ATTACK (ATK-1)
# =============================================================================

class TestAnalyzeTensionAsAttack:
    """Test the main tension-to-attack analysis function."""

    def test_basic_analysis(self):
        """Basic tension analysis works."""
        anomaly = MockBelief(
            belief_id="anomaly_001",
            content="Nature has no effect on stress",
            credence=MockCredence(0.65)
        )
        target = MockBelief(
            belief_id="target_001",
            content="Nature reduces stress",
            credence=MockCredence(0.8)
        )

        attack, evidence = analyze_tension_as_attack(anomaly, target)

        assert attack.attack_id == "atk_anomaly_001_target_001"
        assert attack.target_belief_id == "target_001"
        assert attack.attack_credence == 0.65
        assert attack.shift_type is not None

    def test_structured_detection_preferred(self):
        """Structured detection is used when metadata available."""
        pop_a = MockPopulationContext(population_id="urban")
        pop_b = MockPopulationContext(population_id="rural")

        anomaly = MockBelief(
            belief_id="anomaly_002",
            content="No effect in rural areas",
            credence=MockCredence(0.7),
            contrast_class=MockContrastClass(
                contrast_id="cc_rural",
                focal=MockConditionSpec("nature", "forest", "Forest"),
                contrasts=[MockConditionSpec("nature", "field", "Field")],
                population_context=pop_b
            )
        )
        target = MockBelief(
            belief_id="target_002",
            content="Effect in urban areas",
            credence=MockCredence(0.8),
            contrast_class=MockContrastClass(
                contrast_id="cc_urban",
                focal=MockConditionSpec("nature", "forest", "Forest"),
                contrasts=[MockConditionSpec("nature", "office", "Office")],
                population_context=pop_a
            )
        )

        attack, evidence = analyze_tension_as_attack(anomaly, target)

        # Should have found structured evidence
        assert len(evidence) > 0
        assert attack.shift_type != ContrastShiftType.PRESERVING

    def test_to_dict_serialization(self):
        """ArgumentAttack serializes to dict correctly."""
        attack = ArgumentAttack(
            attack_id="atk_test",
            source_paper_id="paper_123",
            target_belief_id="belief_456",
            attack_type=AttackType.BOUNDARY_CONDITION,
            attack_claim="Test claim",
            attack_credence=0.75,
            shift_type=ContrastShiftType.POPULATION_SHIFT,
        )

        d = attack.to_dict()
        assert d["attack_id"] == "atk_test"
        assert d["attack_type"] == "boundary_condition"
        assert d["shift_type"] == "population"
        assert d["is_true_refutation"] is False


# =============================================================================
# TEST ENHANCE TENSION WITH ATTACK ANALYSIS
# =============================================================================

class TestEnhanceTensionWithAttackAnalysis:
    """Test tension enhancement for tensions.jsonl output."""

    def test_basic_enhancement(self):
        """Basic tension enhancement works."""
        anomaly = MockBelief(
            belief_id="anomaly_003",
            content="Contradicting finding",
            credence=MockCredence(0.6)
        )
        contradicting = [MockBelief(
            belief_id="target_003",
            content="Original finding",
            credence=MockCredence(0.8)
        )]

        tension = {
            "belief_id": "anomaly_003",
            "content": "Contradicting finding",
            "credence": 0.6,
            "contradicts": ["Original finding"]
        }

        enhanced = enhance_tension_with_attack_analysis(
            tension=tension,
            anomaly_belief=anomaly,
            contradicting_beliefs=contradicting,
            web=None
        )

        assert "attack_analysis" in enhanced
        assert enhanced["attack_analysis"]["n_attacks"] == 1
        assert "attacks" in enhanced["attack_analysis"]

    def test_tension_type_classification(self):
        """Tension type is correctly classified."""
        # Create population mismatch scenario
        pop_a = MockPopulationContext(population_id="group_a")
        pop_b = MockPopulationContext(population_id="group_b")

        anomaly = MockBelief(
            belief_id="a1",
            content="Finding",
            credence=MockCredence(0.7),
            contrast_class=MockContrastClass(
                contrast_id="cc1",
                focal=MockConditionSpec("x", "y", "desc"),
                contrasts=[],
                population_context=pop_a
            )
        )
        contradicting = [MockBelief(
            belief_id="t1",
            content="Opposite",
            credence=MockCredence(0.8),
            contrast_class=MockContrastClass(
                contrast_id="cc2",
                focal=MockConditionSpec("x", "y", "desc"),
                contrasts=[],
                population_context=pop_b
            )
        )]

        tension = {
            "belief_id": "a1",
            "content": "Finding",
            "credence": 0.7,
            "contradicts": ["Opposite"]
        }

        enhanced = enhance_tension_with_attack_analysis(
            tension=tension,
            anomaly_belief=anomaly,
            contradicting_beliefs=contradicting,
            web=None
        )

        # Should be classified as contrast_shift (not true_contradiction)
        assert enhanced["attack_analysis"]["tension_type"] == "contrast_shift"
        assert enhanced["attack_analysis"]["n_contrast_shifts"] == 1
        assert enhanced["attack_analysis"]["n_true_refutations"] == 0

    def test_structured_evidence_included(self):
        """Structured evidence is included in output."""
        pop_a = MockPopulationContext(population_id="pop_x")
        pop_b = MockPopulationContext(population_id="pop_y")

        anomaly = MockBelief(
            belief_id="a2",
            content="Result",
            credence=MockCredence(0.65),
            contrast_class=MockContrastClass(
                contrast_id="cc1",
                focal=MockConditionSpec("v", "1", "d"),
                contrasts=[],
                population_context=pop_a
            )
        )
        contradicting = [MockBelief(
            belief_id="t2",
            content="Opposite result",
            credence=MockCredence(0.8),
            contrast_class=MockContrastClass(
                contrast_id="cc2",
                focal=MockConditionSpec("v", "1", "d"),
                contrasts=[],
                population_context=pop_b
            )
        )]

        tension = {"belief_id": "a2", "content": "Result", "credence": 0.65, "contradicts": []}

        enhanced = enhance_tension_with_attack_analysis(
            tension=tension,
            anomaly_belief=anomaly,
            contradicting_beliefs=contradicting,
            web=None
        )

        # Check that structured evidence is present
        attacks = enhanced["attack_analysis"]["attacks"]
        assert len(attacks) == 1
        assert "structured_evidence" in attacks[0]
        assert attacks[0]["detection_method"] == "structured"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
