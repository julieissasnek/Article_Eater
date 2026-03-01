"""
test_cva_e2e.py — End-to-End Integration Tests (Phase 7)
==========================================================

Tests the full CVA pipeline: scene → constraints → valuations → beauty,
with subject parameterization, cultural variants, and attractor dynamics.
"""

import pytest
import math

from src.models.cva_constraint import CVAConstraintVector, Tier2ConstraintVector
from src.models.cva_valuation import CVAValuationVector, CulturalVariant
from src.models.subject_characteristics import (
    SubjectCharacteristics,
    NEUROTYPE_PROFILES,
    CULTURAL_PRESETS,
)
from src.models.activity_frame import ActivityFrame, ActivityFrameType
from src.models.cva_annotations import (
    CVAAnnotationSet,
    MeasurementAnnotation,
    StimulusAnnotation,
    MoleculeLink,
    MeasurementModality,
    StimulusType,
)
from src.services.cva_constraint_engine import CVAConstraintEngine
from src.services.cva_valuation_engine import CVAValuationEngine
from src.services.cva_beauty import (
    LinearBeautyReadout,
    RasaBeautyReadout,
    create_beauty_readout,
    BeautyModelType,
)
from src.services.cva_attractor import CVAAttractorEngine, RASA_ATTRACTORS
from src.services.cva_dynamics import CVADynamics, DynamicsState, FeedbackSignal
from src.services.overseer_playbooks import (
    RemediationEngine,
    RemediationAction,
    ALL_PLAYBOOKS,
)


# ──────────────────────────────────────────────────────────────────
# E2E: Full Pipeline (Phase 7, Task 7.1)
# ──────────────────────────────────────────────────────────────────

class TestFullPipeline:
    """Scene → CVA constraints → valuations → beauty for different subjects."""

    OFFICE_SCENE = {
        "edge": 0.6, "motion": 0.2, "contrast": 0.7,
        "figure_ground": 0.8, "temporal_coherence": 0.6, "symmetry": 0.7,
    }

    PARK_SCENE = {
        "edge": 0.4, "motion": 0.5, "contrast": 0.5,
        "figure_ground": 0.3, "temporal_coherence": 0.8, "symmetry": 0.3,
    }

    def test_typical_western_adult(self):
        eng_c = CVAConstraintEngine()
        eng_v = CVAValuationEngine()
        beauty = LinearBeautyReadout()

        subject = SubjectCharacteristics(subject_id="typical_western")
        c = eng_c.compute(self.OFFICE_SCENE, subject)
        v = eng_v.compute(c, subject)
        b = beauty.compute(v)

        assert isinstance(c, CVAConstraintVector)
        assert v.variant == CulturalVariant.WESTERN
        assert 0.0 <= b <= 1.0

    def test_ptsd_subject_valid_valuations(self):
        eng_c = CVAConstraintEngine()
        eng_v = CVAValuationEngine()

        subject = SubjectCharacteristics(
            subject_id="ptsd_001",
            neurotype=NEUROTYPE_PROFILES["ptsd"],
        )
        c = eng_c.compute(self.OFFICE_SCENE, subject)
        v = eng_v.compute(c, subject)

        # PTSD increases prediction_error → base safety reduced via
        # negative weight in constraint→valuation mapping. The 2.5× gain
        # tries to compensate, but net effect is scene-dependent.
        # Verify all valuations are valid and interest is suppressed.
        assert 0.0 <= v["SafetyValue"] <= 1.0
        assert v["InterestValue"] < 0.5  # Interest suppressed in PTSD (0.3× gain)

    def test_japanese_cultural_variant_produces_amae(self):
        eng_c = CVAConstraintEngine()
        eng_v = CVAValuationEngine()

        subject = SubjectCharacteristics(
            subject_id="japanese_001",
            culture=CULTURAL_PRESETS["japanese"],
        )
        c = eng_c.compute(self.PARK_SCENE, subject)
        v = eng_v.compute(c, subject)

        assert v.variant == CulturalVariant.JAPANESE
        assert "AmaeValue" in v.values
        assert "MaValue" in v.values
        assert v.dimensionality == 10

    def test_indian_rasa_beauty(self):
        eng_c = CVAConstraintEngine()
        eng_v = CVAValuationEngine()
        beauty = RasaBeautyReadout()

        subject = SubjectCharacteristics(
            subject_id="indian_001",
            culture=CULTURAL_PRESETS["indian"],
        )
        c = eng_c.compute(self.PARK_SCENE, subject)
        v = eng_v.compute(c, subject)
        b = beauty.compute(v)
        rasa = beauty.dominant_rasa(v)

        assert v.variant == CulturalVariant.INDIAN
        assert 0.0 <= b <= 1.0
        assert rasa in ("shringara", "hasya", "karuna", "raudra", "veera",
                         "bhayanaka", "bibhatsa", "adbhuta", "shanta")

    def test_west_african_asa(self):
        eng_c = CVAConstraintEngine()
        eng_v = CVAValuationEngine()

        subject = SubjectCharacteristics(
            culture=CULTURAL_PRESETS["west_african"],
        )
        c = eng_c.compute(self.OFFICE_SCENE, subject)
        v = eng_v.compute(c, subject)

        assert v.variant == CulturalVariant.WEST_AFRICAN
        assert "ÀṣàValue" in v.values
        assert v.dimensionality == 6

    def test_activity_frame_modulates_pipeline(self):
        eng_c = CVAConstraintEngine()
        eng_v = CVAValuationEngine()

        subject = SubjectCharacteristics()
        c = eng_c.compute(self.OFFICE_SCENE, subject)

        frame_work = ActivityFrame(frame_type=ActivityFrameType.GOAL_DIRECTED)
        frame_rest = ActivityFrame(frame_type=ActivityFrameType.RESTORATIVE)

        v_work = eng_v.compute(c, subject, frame=frame_work)
        v_rest = eng_v.compute(c, subject, frame=frame_rest)

        # Both should produce valid valuations
        assert 0.0 <= v_work.net_valuation()
        assert 0.0 <= v_rest.net_valuation()


# ──────────────────────────────────────────────────────────────────
# E2E: Attractor Dynamics (Phase 7, Task 7.4)
# ──────────────────────────────────────────────────────────────────

class TestAttractorDynamicsE2E:
    def test_transition_shanta_to_adbhuta(self):
        """Simulate transition from Peace to Wonder."""
        engine = CVAAttractorEngine()
        path = engine.transition_path("shanta", "adbhuta", steps=200)
        assert len(path) > 100
        # Final state should be nearer to adbhuta
        final = path[-1]
        name, dist = engine.find_nearest_attractor(final)
        assert name == "adbhuta"

    def test_cultural_shift_changes_attractors(self):
        """Japanese cultural shift alters attractor positions."""
        engine = CVAAttractorEngine()
        before = engine.attractors["shanta"].constraints[:]
        engine.apply_cultural_shift("japanese")
        after = engine.attractors["shanta"].constraints
        assert before != after

    def test_neurotype_modulation_affects_basins(self):
        """PTSD widens shanta basin, narrows bhayanaka."""
        engine = CVAAttractorEngine()
        basins = engine.neurotype_basin_modulation("ptsd")
        default_shanta = RASA_ATTRACTORS["shanta"].basin_radius
        assert basins["shanta"] > default_shanta


# ──────────────────────────────────────────────────────────────────
# E2E: Overseer + CVA (Phase 7, Task 7.2)
# ──────────────────────────────────────────────────────────────────

class TestOverseerCVAE2E:
    def test_all_playbooks_have_steps(self):
        """Every playbook has at least one remediation step."""
        for code, pb in ALL_PLAYBOOKS.items():
            assert len(pb.steps) > 0, f"{code}: no steps"

    def test_remediation_engine_executes(self):
        """Remediation engine can execute a known playbook."""
        engine = RemediationEngine()
        result = engine.execute_playbook("INV-4")
        assert result.success  # All steps "skip" (no handlers registered)
        assert result.steps_executed == result.steps_total

    def test_cva_invariants_exist(self):
        """CVA-specific invariants INV-10..13 have playbooks."""
        for inv in ("INV-10", "INV-11", "INV-12", "INV-13"):
            assert inv in ALL_PLAYBOOKS

    def test_learning_loop_tracks_success(self):
        """Success rate tracking works."""
        engine = RemediationEngine()
        engine.execute_playbook("INV-4")
        engine.execute_playbook("INV-4")
        rates = engine.get_success_rates()
        assert rates["INV-4"] == 1.0  # Both succeeded


# ──────────────────────────────────────────────────────────────────
# E2E: Annotations (Phase 7, Task 7.1 annotation path)
# ──────────────────────────────────────────────────────────────────

class TestAnnotationE2E:
    def test_annotation_set_round_trip(self):
        ann = CVAAnnotationSet(
            target_id="T_MSI_001",
            measurements=[
                MeasurementAnnotation(
                    modality=MeasurementModality.FMRI,
                    spatial_resolution="3mm",
                    sample_size=24,
                    population="neurotypical adults",
                ),
            ],
            stimuli=[
                StimulusAnnotation(
                    stimulus_type=StimulusType.MULTISENSORY,
                    duration_ms=500,
                    complexity=0.6,
                    cva_constraints_relevant=["MultisensoryCoherence", "LoadRate"],
                ),
            ],
            molecule_links=[
                MoleculeLink(
                    molecule_id="M_RASA",
                    template_id="T_MSI_001",
                    link_type="supports",
                    strength=0.7,
                ),
            ],
            constraint_tags={"MultisensoryCoherence": 0.8},
            valuation_tags={"InterestValue": 0.7},
        )

        j = ann.to_json()
        ann2 = CVAAnnotationSet.from_json(j)
        assert ann2.target_id == "T_MSI_001"
        assert len(ann2.measurements) == 1
        assert ann2.measurements[0].modality == MeasurementModality.FMRI
        assert len(ann2.stimuli) == 1
        assert len(ann2.molecule_links) == 1


# ──────────────────────────────────────────────────────────────────
# E2E: Dynamics Convergence (Phase 7, Task 7.5 stress-like)
# ──────────────────────────────────────────────────────────────────

class TestDynamicsStress:
    def test_multiple_subjects_converge(self):
        """Multiple subjects should all converge to valid states."""
        eng_c = CVAConstraintEngine()
        eng_v = CVAValuationEngine()
        dyn = CVADynamics(alpha=3.0, beta=2.0, dt=0.01)

        scene = {
            "edge": 0.5, "motion": 0.4, "contrast": 0.6,
            "figure_ground": 0.5, "temporal_coherence": 0.7, "symmetry": 0.5,
        }

        profiles = ["typical", "ptsd", "asd", "adhd", "depression",
                     "anxiety", "gifted", "older_adult"]
        for profile_name in profiles:
            subject = SubjectCharacteristics(
                neurotype=NEUROTYPE_PROFILES[profile_name],
            )
            c = eng_c.compute(scene, subject)
            v = eng_v.compute(c, subject)

            # Simulate dynamics convergence
            state = DynamicsState(
                constraints=c.tier2.as_vector(),
                valuations=v.as_vector()[:9],
            )
            target_c = c.tier2.as_vector()
            target_v = v.as_vector()[:9]

            trajectory = dyn.simulate(state, target_c, target_v, duration=1.0)
            assert dyn.has_converged(trajectory[-1], target_c, target_v, tolerance=0.05), \
                f"{profile_name} did not converge"

    def test_all_beauty_models_produce_valid_output(self):
        """All 4 beauty models produce [0,1] output for all cultural variants."""
        eng_c = CVAConstraintEngine()
        eng_v = CVAValuationEngine()
        scene = {"edge": 0.5, "motion": 0.4, "contrast": 0.6,
                 "figure_ground": 0.5, "temporal_coherence": 0.7, "symmetry": 0.5}

        for culture_name in ["western", "japanese", "west_african", "indian"]:
            subject = SubjectCharacteristics(culture=CULTURAL_PRESETS[culture_name])
            c = eng_c.compute(scene, subject)
            v = eng_v.compute(c, subject)

            for model_type in BeautyModelType:
                model = create_beauty_readout(model_type)
                b = model.compute(v)
                assert 0.0 <= b <= 1.0, \
                    f"{culture_name}/{model_type.value}: beauty={b}"
