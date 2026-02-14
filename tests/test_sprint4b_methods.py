"""
Tests for Sprint 4b: Method Registry and Task-Ecological Validity.

Verifies implementation of:
- Task 4b.1: Method registry data structure
- Task 4b.2: Seed entries (15+)
- Task 4b.3: Task-ecological validity scoring
- Task 4b.4: Claim type bifurcation
- Task 4b.5: Method identification
- Task 4b.6: Per-claim validity scores
"""

import pytest


class TestTask4b1MethodRegistry:
    """Task 4b.1: Create method_registry data structure."""

    def test_can_import_registry(self):
        """Registry module imports successfully."""
        from src.methods.registry import (
            MethodEntry,
            MethodRegistry,
            MethodType,
            MovementCompatibility,
            ProfileStatus,
        )
        assert MethodEntry is not None
        assert MethodRegistry is not None

    def test_create_method_entry(self):
        """Can create a MethodEntry."""
        from src.methods.registry import (
            MethodEntry,
            MethodType,
            ProfileStatus,
        )

        entry = MethodEntry(
            method_id="test_method",
            method_type=MethodType.PHYSIOLOGICAL_BIOMARKER,
            construct_measured="Test construct",
            profile_status=ProfileStatus.WELL_CHARACTERIZED,
        )

        assert entry.method_id == "test_method"
        assert entry.method_type == MethodType.PHYSIOLOGICAL_BIOMARKER

    def test_registry_add_and_get(self):
        """Can add and retrieve entries from registry."""
        from src.methods.registry import (
            MethodEntry,
            MethodRegistry,
            MethodType,
        )

        registry = MethodRegistry()
        entry = MethodEntry(
            method_id="test_method",
            method_type=MethodType.SELF_REPORT,
            construct_measured="Test",
        )

        registry.add(entry)
        retrieved = registry.get("test_method")

        assert retrieved is not None
        assert retrieved.method_id == "test_method"

    def test_registry_find_by_type(self):
        """Can find entries by method type."""
        from src.methods.registry import (
            MethodEntry,
            MethodRegistry,
            MethodType,
        )

        registry = MethodRegistry()
        registry.add(MethodEntry("m1", MethodType.PHYSIOLOGICAL_BIOMARKER, "C1"))
        registry.add(MethodEntry("m2", MethodType.PHYSIOLOGICAL_BIOMARKER, "C2"))
        registry.add(MethodEntry("m3", MethodType.SELF_REPORT, "C3"))

        physio = registry.find_by_type(MethodType.PHYSIOLOGICAL_BIOMARKER)
        assert len(physio) == 2

    def test_registry_list_uncharacterized(self):
        """Can list uncharacterized methods."""
        from src.methods.registry import (
            MethodEntry,
            MethodRegistry,
            MethodType,
            ProfileStatus,
        )

        registry = MethodRegistry()
        registry.add(MethodEntry("m1", MethodType.SELF_REPORT, "C1",
                                 profile_status=ProfileStatus.WELL_CHARACTERIZED))
        registry.add(MethodEntry("m2", MethodType.SELF_REPORT, "C2",
                                 profile_status=ProfileStatus.UNCHARACTERIZED))

        unchar = registry.list_uncharacterized()
        assert len(unchar) == 1
        assert unchar[0].method_id == "m2"

    def test_construct_validity_lookup(self):
        """Can look up construct validity scores."""
        from src.methods.registry import MethodEntry, MethodType

        entry = MethodEntry(
            method_id="test",
            method_type=MethodType.PHYSIOLOGICAL_BIOMARKER,
            construct_measured="stress",
            construct_validity_map={
                "stress": 0.85,
                "relaxation": 0.60,
            }
        )

        assert entry.get_construct_validity("stress") == 0.85
        assert entry.get_construct_validity("unknown") == 0.3  # D-PANEL.11: conservative uncertainty


class TestTask4b2SeedEntries:
    """Task 4b.2: Seed registry with 15+ entries."""

    def test_seed_entries_exist(self):
        """At least 15 seed entries defined."""
        from src.methods.seed_data import SEED_ENTRIES

        assert len(SEED_ENTRIES) >= 15

    def test_load_seed_entries(self):
        """Can load seed entries into registry."""
        from src.methods.registry import MethodRegistry, MethodType
        from src.methods.seed_data import load_seed_entries

        registry = MethodRegistry()
        count = load_seed_entries(registry)

        assert count >= 15
        assert registry.count() >= 15

    def test_query_physiological_biomarkers(self):
        """Can query for physiological biomarkers."""
        from src.methods.registry import MethodRegistry, MethodType
        from src.methods.seed_data import load_seed_entries

        registry = MethodRegistry()
        load_seed_entries(registry)

        physio = registry.find_by_type(MethodType.PHYSIOLOGICAL_BIOMARKER)
        assert len(physio) >= 5  # cortisol, HRV x2, EDA x2, BP

    def test_cortisol_entry_complete(self):
        """Cortisol entry has all required fields."""
        from src.methods.registry import MethodRegistry
        from src.methods.seed_data import load_seed_entries

        registry = MethodRegistry()
        load_seed_entries(registry)

        cortisol = registry.get("salivary_cortisol")
        assert cortisol is not None
        assert cortisol.temporal_onset == "15-20 min"
        assert cortisol.minimum_sampling_window == "20 min post-stressor"
        assert len(cortisol.confounds) > 0
        assert "hpa_stress_reactivity" in cortisol.construct_validity_map


class TestTask4b3TaskEcology:
    """Task 4b.3: Task-ecological validity enums and scoring."""

    def test_can_import_task_ecology(self):
        """Task ecology module imports successfully."""
        from src.methods.task_ecology import (
            TaskClass,
            EffectPathway,
            ClaimType,
            StateCharacterization,
            compute_task_ecological_validity,
        )
        assert TaskClass.EXPLICIT_EVALUATION.value == "explicit_evaluation"
        assert ClaimType.FUNCTIONAL_EFFECT.value == "functional_effect"

    def test_task_authenticity_scores(self):
        """Task authenticity scores are correctly ordered."""
        from src.methods.task_ecology import TaskClass, TASK_AUTHENTICITY_SCORES

        assert TASK_AUTHENTICITY_SCORES[TaskClass.EXPLICIT_EVALUATION] == 0.2
        assert TASK_AUTHENTICITY_SCORES[TaskClass.NATURAL_BEHAVIOR] == 1.0
        assert TASK_AUTHENTICITY_SCORES[TaskClass.EXPLICIT_EVALUATION] < \
               TASK_AUTHENTICITY_SCORES[TaskClass.NATURAL_BEHAVIOR]

    def test_state_characterization_score(self):
        """State characterization computes average score."""
        from src.methods.task_ecology import StateCharacterization

        state = StateCharacterization(
            affective_state=0.6,
            cognitive_load=0.6,
            goal_urgency=0.6,
            familiarity=0.6,
            physical_state=0.6,
            social_context=0.6,
        )

        assert state.score == pytest.approx(0.6, abs=0.01)

    def test_low_ecological_validity(self):
        """Photo preference rating has low ecological validity."""
        from src.methods.task_ecology import (
            TaskClass, StateCharacterization, compute_task_ecological_validity
        )

        state_none = StateCharacterization()
        score = compute_task_ecological_validity(
            TaskClass.EXPLICIT_EVALUATION,
            state_none,
            attention_directed_to_features=True,
            exposure_representative=False,
            social_context_representative=False
        )

        assert score < 0.3

    def test_high_ecological_validity(self):
        """Real task with state measurement has high ecological validity."""
        from src.methods.task_ecology import (
            TaskClass, StateCharacterization, compute_task_ecological_validity
        )

        state_good = StateCharacterization(0.7, 0.7, 1.0, 1.0, 0.3, 0.7)
        score = compute_task_ecological_validity(
            TaskClass.REAL_TASK_CONTROLLED,
            state_good,
            attention_directed_to_features=False,
            exposure_representative=True,
            social_context_representative=True
        )

        assert score > 0.7

    def test_classify_claim_type(self):
        """Can classify claim as evaluative or functional."""
        from src.methods.task_ecology import classify_claim_type, ClaimType

        evaluative = classify_claim_type("Participants preferred nature views")
        functional = classify_claim_type("Nature views reduce stress")

        assert evaluative == ClaimType.EVALUATIVE_RESPONSE
        assert functional == ClaimType.FUNCTIONAL_EFFECT


class TestTask4b4ClaimTypeBifurcation:
    """Task 4b.4: Claim type bifurcation."""

    def test_generalizability_warrant_exists(self):
        """GENERALIZABILITY_WARRANT link type exists."""
        from src.services.web_of_belief import ConstraintType

        assert hasattr(ConstraintType, "GENERALIZABILITY_WARRANT")
        assert ConstraintType.GENERALIZABILITY_WARRANT.value == "generalizability_warrant"


class TestTask4b5MethodIdentification:
    """Task 4b.5: Method identification in extraction."""

    def test_can_import_method_identifier(self):
        """Method identifier module imports successfully."""
        from src.methods.method_identifier import (
            identify_methods,
            MethodIdentificationResult,
        )
        assert identify_methods is not None

    def test_identify_cortisol(self):
        """Identifies cortisol from methods text."""
        from src.methods.method_identifier import identify_methods

        text = "We measured salivary cortisol using Salivettes at baseline and post-exposure."
        result = identify_methods(text)

        method_ids = [m["method_id"] for m in result.instruments_found]
        assert "salivary_cortisol" in method_ids

    def test_identify_vr_modality(self):
        """Identifies VR presentation modality."""
        from src.methods.method_identifier import identify_methods

        text = "Participants viewed environments using an HMD VR headset (Oculus Rift)."
        result = identify_methods(text)

        assert result.presentation_modality is not None
        assert "vr" in result.presentation_modality["method_id"]

    def test_identify_multiple_methods(self):
        """Can identify multiple methods from text."""
        from src.methods.method_identifier import identify_methods

        text = """
        We measured heart rate variability (HRV) using a Polar chest strap.
        Salivary cortisol was collected using Salivettes.
        Skin conductance was recorded using BioPac electrodes.
        """
        result = identify_methods(text)

        method_ids = [m["method_id"] for m in result.instruments_found]
        assert len(method_ids) >= 2

    def test_classify_task_type(self):
        """Classifies task type from methods text."""
        from src.methods.method_identifier import identify_methods
        from src.methods.task_ecology import TaskClass

        poe_text = "We conducted a post-occupancy evaluation in real office buildings."
        result = identify_methods(poe_text)
        assert result.task_class == TaskClass.NATURAL_BEHAVIOR

        photo_text = "Participants rated photographs of building interiors."
        result2 = identify_methods(photo_text)
        assert result2.task_class == TaskClass.EXPLICIT_EVALUATION

    def test_temporal_alignment_flag(self):
        """Flags temporal alignment issues."""
        from src.methods.method_identifier import identify_methods

        text = """
        We measured salivary cortisol during a 10 minute VR exposure.
        Samples were collected immediately after viewing.
        """
        result = identify_methods(text)

        assert "cortisol_temporal_misalignment" in result.temporal_alignment_flags


class TestTask4b6ValidityScoring:
    """Task 4b.6: Per-claim validity scores."""

    def test_can_import_validity_scorer(self):
        """Validity scorer imports successfully."""
        from src.methods.validity_scorer import (
            compute_claim_validity,
            ClaimValidityResult,
        )
        assert compute_claim_validity is not None

    def test_photo_wayfinding_gets_challenges(self):
        """Wayfinding claim from photos gets construct_presentation_mismatch."""
        from src.methods.method_identifier import identify_methods
        from src.methods.validity_scorer import compute_claim_validity

        methods = identify_methods("We used photographs to assess spatial preferences.")
        validity = compute_claim_validity(
            "Spatial complexity reduces wayfinding efficiency",
            "wayfinding",
            methods
        )

        assert "construct_presentation_mismatch" in validity.auto_challenges

    def test_single_modality_challenge(self):
        """Single measurement modality triggers challenge."""
        from src.methods.method_identifier import identify_methods
        from src.methods.validity_scorer import compute_claim_validity

        methods = identify_methods("We used only self-report preference ratings.")
        validity = compute_claim_validity(
            "Nature views are preferred",
            "preference",
            methods
        )

        assert "single_modality" in validity.auto_challenges

    def test_validity_scores_in_range(self):
        """Validity scores are in [0, 1]."""
        from src.methods.method_identifier import identify_methods
        from src.methods.validity_scorer import compute_claim_validity

        methods = identify_methods("We measured HRV and cortisol in real offices.")
        validity = compute_claim_validity(
            "Office design affects stress",
            "stress",
            methods
        )

        assert 0.0 <= validity.presentation_validity <= 1.0
        assert 0.0 <= validity.measurement_validity <= 1.0
        assert 0.0 <= validity.task_ecological_validity <= 1.0
        assert 0.0 <= validity.composite_validity <= 1.0

    def test_high_validity_for_gold_standard(self):
        """Gold standard study (Fich et al. pattern) gets high validity."""
        from src.methods.method_identifier import identify_methods
        from src.methods.validity_scorer import compute_claim_validity
        from src.methods.registry import MethodRegistry
        from src.methods.seed_data import load_seed_entries

        registry = MethodRegistry()
        load_seed_entries(registry)

        methods = identify_methods("""
        We conducted a CAVE VR study with N=93 participants.
        We measured salivary cortisol at 7 time points following the TSST stress task.
        Heart rate variability was also recorded continuously.
        State anxiety was measured using the STAI.
        """, registry)

        validity = compute_claim_validity(
            "Enclosed rooms increase cortisol response",
            "stress_response",
            methods,
            registry
        )

        # Should have multiple instruments, VR modality, ecological task
        assert len(methods.instruments_found) >= 2
        assert validity.composite_validity > 0.4


class TestMethodsPackageIntegration:
    """Test all methods modules work together."""

    def test_full_workflow(self):
        """Complete workflow from method ID to validity scoring."""
        from src.methods.registry import MethodRegistry
        from src.methods.seed_data import load_seed_entries
        from src.methods.method_identifier import identify_methods
        from src.methods.validity_scorer import compute_claim_validity
        from src.methods.task_ecology import ClaimType, classify_claim_type

        # 1. Load registry
        registry = MethodRegistry()
        load_seed_entries(registry)
        assert registry.count() >= 15

        # 2. Identify methods from paper text
        methods_text = """
        Participants viewed photographs of hospital corridors on a computer monitor.
        They rated each image for perceived restorativeness using the PRS scale.
        """
        methods = identify_methods(methods_text, registry)
        assert methods.presentation_modality is not None

        # 3. Classify claim type
        claim = "Natural elements in hospitals improve perceived restoration"
        claim_type = classify_claim_type(claim)
        assert claim_type == ClaimType.FUNCTIONAL_EFFECT

        # 4. Compute validity
        validity = compute_claim_validity(claim, "restoration", methods, registry)
        assert validity.composite_validity > 0
        assert len(validity.auto_challenges) > 0  # Photos for functional claim

    def test_all_modules_importable_from_package(self):
        """All modules accessible from main package."""
        from src.methods import (
            MethodEntry,
            MethodRegistry,
            MethodType,
            TaskClass,
            ClaimType,
            compute_task_ecological_validity,
            compute_claim_validity,
            identify_methods,
        )

        assert MethodEntry is not None
        assert MethodRegistry is not None
        assert TaskClass is not None
        assert compute_claim_validity is not None
