"""
Tests for Template Computation Functions.

Batch 1: 12 Core Templates (per Doc 68 Task 2.1)
Batch 2: 20 Additional Templates (per Doc 68 Task 3.2)
Batch 3: 10 Gap Template Computations (per Doc 68 Task 3.8)
"""

import math
import pytest

from src.cmr.template_computations import (
    ComputeResult,
    OutputType,
    TEMPLATE_COMPUTE_FUNCTIONS,
    get_compute_function,
    list_implemented_templates,
    get_lifespan_multiplier,
    get_age_band,
    # Batch 1
    compute_vf3_ceiling_height,
    compute_l1_luminance_contrast,
    compute_l2_circadian_medi,
    compute_l3_daylight_composite,
    compute_crea2_processing_style,
    compute_mat1_ct_afferent,
    compute_mat2_thermal_adaptive,
    compute_nmc1_material_convergence,
    compute_soc2_privacy_encounter,
    compute_sc1_spatial_integration,
    compute_sc4_wayfinding_social,
    compute_view1_vqi,
    # Batch 2
    compute_l4_cct_temporal,
    compute_l5_dynamic_light,
    compute_mat3_material_identity,
    compute_mat5_material_cultural,
    compute_tp1_motor_pe,
    compute_tp2_threshold_boundary,
    compute_tp3_temporal_rhythm,
    compute_tp4_temporal_hierarchy,
    compute_soc1_proxemic_pe,
    compute_soc3_territorial,
    compute_crea1_creative_network,
    compute_crea3_incubation,
    compute_crea4_collaborative,
    compute_sc2_isovist,
    compute_sc3_promenade,
    compute_col1_chromatic_pe,
    compute_col2_color_harmony,
    compute_vf1_contour_curvature,
    compute_vf2_visual_rhythm,
    compute_olf1_olfactory_pe,
    # Batch 3
    compute_t4_attention_demand,
    compute_t6_cortisol_cascade,
    compute_t7_allostatic_anticipation,
    compute_t10_sleep_consolidation,
    compute_t14_navigation_stress_loop,
    compute_t15_environmental_control,
    compute_t17_dopaminergic_novelty,
    compute_t18_vestibular_spatial,
    compute_t23_context_memory,
    compute_t28_cognitive_offloading,
)


class TestComputeResult:
    """Tests for ComputeResult dataclass."""

    def test_to_dict_basic(self):
        result = ComputeResult(
            output_type="goldilocks_zone",
            value=0.42,
            unit="ratio",
        )
        d = result.to_dict()
        assert d["output_type"] == "goldilocks_zone"
        assert d["value"] == 0.42
        assert d["unit"] == "ratio"
        assert "zone" not in d
        assert "confidence" not in d

    def test_to_dict_with_zone(self):
        result = ComputeResult(
            output_type="goldilocks_zone",
            value=0.42,
            unit="ratio",
            zone="liberating",
        )
        d = result.to_dict()
        assert d["zone"] == "liberating"

    def test_to_dict_with_confidence(self):
        result = ComputeResult(
            output_type="threshold_check",
            value=1.2,
            unit="ratio_to_threshold",
            confidence=0.85,
        )
        d = result.to_dict()
        assert d["confidence"] == 0.85


class TestLifespanModeration:
    """Tests for lifespan moderation functions."""

    def test_reference_band_multiplier(self):
        # Reference band (25-50) should have multiplier 1.0
        assert get_lifespan_multiplier(30) == 1.0
        assert get_lifespan_multiplier(45) == 1.0

    def test_young_child_multiplier(self):
        # Young children have higher sensitivity
        assert get_lifespan_multiplier(3) == 1.6
        assert get_lifespan_multiplier(8) == 1.35

    def test_elderly_multiplier(self):
        # Elderly have higher sensitivity
        assert get_lifespan_multiplier(70) == 1.45
        assert get_lifespan_multiplier(85) == 1.7

    def test_none_age_defaults(self):
        assert get_lifespan_multiplier(None) == 1.0

    def test_age_band_mapping(self):
        assert get_age_band(2) == "toddler_0_3"
        assert get_age_band(25) == "young_20_40"
        assert get_age_band(50) == "middle_40_65"
        assert get_age_band(75) == "older_65_80"
        assert get_age_band(85) == "frail_80_plus"


class TestVF3CeilingHeight:
    """Tests for VF3 ceiling height computation."""

    def test_confinement_zone(self):
        # Low ceiling in large room = confinement
        result = compute_vf3_ceiling_height(
            ceiling_height_m=2.4,
            floor_area_m2=100.0,
        )
        assert result.value < 0.25
        assert result.zone == "confinement"
        assert result.details["processing_style"] == "concrete"

    def test_liberating_zone(self):
        # High ceiling in standard room = liberating
        result = compute_vf3_ceiling_height(
            ceiling_height_m=3.5,
            floor_area_m2=50.0,
        )
        assert 0.35 <= result.value <= 0.50
        assert result.zone == "liberating"
        assert result.details["processing_style"] == "abstract"
        assert result.details["optimal_for_creativity"] is True

    def test_standard_zone(self):
        # Standard office ceiling
        result = compute_vf3_ceiling_height(
            ceiling_height_m=2.7,
            floor_area_m2=60.0,
        )
        # R_h = 2.7 / sqrt(60) ≈ 0.35
        assert 0.25 <= result.value < 0.50

    def test_invalid_inputs(self):
        with pytest.raises(ValueError):
            compute_vf3_ceiling_height(0.0, 50.0)
        with pytest.raises(ValueError):
            compute_vf3_ceiling_height(3.0, 0.0)


class TestL1LuminanceContrast:
    """Tests for L1 luminance contrast computation."""

    def test_comfort_zone(self):
        result = compute_l1_luminance_contrast(cv_luminance=0.3)
        assert result.zone == "comfort"
        assert result.details["plummer_light_type"] == "wash"

    def test_aesthetic_zone(self):
        result = compute_l1_luminance_contrast(cv_luminance=1.0)
        assert result.zone == "aesthetic"
        assert result.details["optimal_aesthetic"] is True
        assert result.details["plummer_light_type"] == "dapple"

    def test_dramatic_zone(self):
        result = compute_l1_luminance_contrast(cv_luminance=2.0)
        assert result.zone == "dramatic"
        assert result.details["awe_potential"] is True

    def test_glare_zone(self):
        result = compute_l1_luminance_contrast(cv_luminance=4.0)
        assert result.zone == "glare"
        assert result.details["pe_level"] == "excessive"


class TestL2CircadianMEDI:
    """Tests for L2 circadian M-EDI computation."""

    def test_adequate_morning_light(self):
        result = compute_l2_circadian_medi(
            medi_lux=300.0,
            exposure_duration_hours=3.0,
            time_of_day="morning",
            occupant_age=30,
        )
        assert result.zone == "adequate"
        assert result.details["circadian_adequate"] is True
        assert result.details["timing_effect"] == "phase_advance"

    def test_insufficient_light(self):
        result = compute_l2_circadian_medi(
            medi_lux=100.0,
            exposure_duration_hours=2.0,
            time_of_day="morning",
            occupant_age=30,
        )
        assert result.zone == "insufficient"
        assert result.details["medi_adequate"] is False

    def test_age_correction(self):
        # Older adults need more light
        result_young = compute_l2_circadian_medi(
            medi_lux=300.0,
            exposure_duration_hours=3.0,
            time_of_day="morning",
            occupant_age=25,
        )
        result_old = compute_l2_circadian_medi(
            medi_lux=300.0,
            exposure_duration_hours=3.0,
            time_of_day="morning",
            occupant_age=70,
        )
        # Older adult has higher threshold, so ratio is lower
        assert result_old.value < result_young.value
        assert result_old.details["age_correction_factor"] > result_young.details["age_correction_factor"]

    def test_evening_light_problematic(self):
        result = compute_l2_circadian_medi(
            medi_lux=300.0,
            exposure_duration_hours=3.0,
            time_of_day="evening",
        )
        assert result.details["circadian_adequate"] is False
        assert result.details["timing_effect"] == "phase_delay"


class TestL3DaylightComposite:
    """Tests for L3 daylight multi-channel composite."""

    def test_excellent_daylight(self):
        result = compute_l3_daylight_composite(
            circadian_score=0.9,
            view_score=0.85,
            luminance_contrast_score=0.8,
            cct_score=0.7,
            dynamic_variation_score=0.75,
        )
        assert result.value >= 0.8
        assert result.zone == "excellent"
        assert result.details["active_channels"] >= 4

    def test_poor_daylight(self):
        result = compute_l3_daylight_composite(
            circadian_score=0.2,
            view_score=0.1,
            luminance_contrast_score=0.3,
            cct_score=0.2,
            dynamic_variation_score=0.1,
        )
        assert result.value < 0.4
        assert result.zone == "poor"

    def test_super_additivity_bonus(self):
        # Same total inputs, but different channel distribution
        result_concentrated = compute_l3_daylight_composite(
            circadian_score=1.0,
            view_score=0.0,
            luminance_contrast_score=0.0,
            cct_score=0.0,
            dynamic_variation_score=0.0,
        )
        result_distributed = compute_l3_daylight_composite(
            circadian_score=0.6,
            view_score=0.6,
            luminance_contrast_score=0.6,
            cct_score=0.6,
            dynamic_variation_score=0.6,
        )
        # Distributed should have super-additivity bonus
        assert result_distributed.details["super_additivity_bonus"] > 0


class TestCREA2ProcessingStyle:
    """Tests for CREA2 processing style modulation."""

    def test_generative_zone(self):
        # All three pathways active
        result = compute_crea2_processing_style(
            noise_db=70.0,
            ceiling_rh=0.42,
            ambient_lux=150.0,
        )
        assert result.details["matrix_key"] == "A+B+C"
        assert result.value >= 0.5
        assert result.zone == "generative"
        assert result.details["sub_additivity"] < 1.0

    def test_evaluative_zone(self):
        # No pathways active (quiet, low ceiling, bright)
        result = compute_crea2_processing_style(
            noise_db=50.0,
            ceiling_rh=0.25,
            ambient_lux=500.0,
        )
        assert result.details["matrix_key"] == "none"
        assert result.value == 0
        assert result.zone == "evaluative"

    def test_single_pathway(self):
        # Only noise pathway active
        result = compute_crea2_processing_style(
            noise_db=70.0,
            ceiling_rh=0.25,
            ambient_lux=500.0,
        )
        assert result.details["matrix_key"] == "A"
        assert result.details["pathway_a_noise"] is True
        assert result.details["pathway_b_ceiling"] is False

    def test_baseline_creativity_modifier(self):
        result_low = compute_crea2_processing_style(
            noise_db=70.0,
            ceiling_rh=0.42,
            ambient_lux=150.0,
            baseline_creativity="low",
        )
        result_high = compute_crea2_processing_style(
            noise_db=70.0,
            ceiling_rh=0.42,
            ambient_lux=150.0,
            baseline_creativity="high",
        )
        # Low baseline gets bigger boost
        assert result_low.value > result_high.value


class TestMAT1CTAfferent:
    """Tests for MAT1 CT-afferent touch pathway."""

    def test_wood_warm_pleasant(self):
        result = compute_mat1_ct_afferent(
            surface_effusivity=400.0,  # Wood
            contact_temperature_c=32.0,  # Skin temp
        )
        assert result.zone == "warm_pleasant"
        assert result.details["ct_activation"] is True

    def test_metal_cold_aversive(self):
        result = compute_mat1_ct_afferent(
            surface_effusivity=12000.0,  # Metal
            contact_temperature_c=20.0,
        )
        assert result.zone == "cold_aversive"
        assert result.details["ct_activation"] is False

    def test_climate_dependent_valence(self):
        # Stone in hot climate is positive
        result_hot = compute_mat1_ct_afferent(
            surface_effusivity=2000.0,  # Stone
            contact_temperature_c=25.0,
            climate="hot",
        )
        result_cold = compute_mat1_ct_afferent(
            surface_effusivity=2000.0,
            contact_temperature_c=25.0,
            climate="cold",
        )
        assert result_hot.value > result_cold.value


class TestMAT2ThermalAdaptive:
    """Tests for MAT2 thermal adaptive PE."""

    def test_neutral_zone(self):
        # Operative temp very close to adaptive neutral
        result = compute_mat2_thermal_adaptive(
            operative_temperature_c=23.6,
            running_mean_outdoor_c=20.0,  # T_n = 0.31*20 + 17.8 = 24.0
        )
        assert abs(result.value) <= 1
        assert result.zone == "neutral"

    def test_alliesthesia_zone(self):
        result = compute_mat2_thermal_adaptive(
            operative_temperature_c=22.0,
            running_mean_outdoor_c=20.0,  # T_n ≈ 24.0, deviation = 2°C
        )
        assert 1 <= abs(result.value) <= 3
        assert result.zone == "alliesthesia"
        assert result.details["thermal_delight_possible"] is True

    def test_discomfort_zone(self):
        result = compute_mat2_thermal_adaptive(
            operative_temperature_c=18.0,
            running_mean_outdoor_c=20.0,  # T_n ≈ 24.0, deviation = 6°C
        )
        assert abs(result.value) > 5
        assert result.zone == "discomfort"


class TestNMC1MaterialConvergence:
    """Tests for NMC1 natural material convergence."""

    def test_optimal_wood_ratio(self):
        result = compute_nmc1_material_convergence(
            material_type="wood",
            surface_ratio=0.45,  # Optimal
        )
        assert result.zone == "optimal"
        assert result.value >= 0.7

    def test_suboptimal_ratio(self):
        result = compute_nmc1_material_convergence(
            material_type="wood",
            surface_ratio=0.10,
        )
        assert result.zone == "suboptimal"
        assert result.value < 0.7

    def test_different_materials(self):
        result_wood = compute_nmc1_material_convergence("wood", 0.45)
        result_stone = compute_nmc1_material_convergence("stone", 0.45)
        result_concrete = compute_nmc1_material_convergence("concrete", 0.45)
        # All should produce valid scores
        for r in [result_wood, result_stone, result_concrete]:
            assert 0 <= r.value <= 1

    def test_invalid_material(self):
        with pytest.raises(ValueError):
            compute_nmc1_material_convergence("plastic", 0.45)


class TestSOC2PrivacyEncounter:
    """Tests for SOC2 privacy-encounter gradient."""

    def test_optimal_privacy(self):
        result = compute_soc2_privacy_encounter(
            shared_area_ratio=0.50,  # Optimal
            phone_booths_per_worker=0.125,
            quiet_rooms_per_worker=0.04,
            visual_privacy_score=0.7,
            acoustic_privacy_stc=50,
        )
        assert result.zone == "adequate"
        assert result.value >= 0.6

    def test_open_plan_problem(self):
        result = compute_soc2_privacy_encounter(
            shared_area_ratio=0.85,  # Too high
            phone_booths_per_worker=0.05,  # Insufficient
            quiet_rooms_per_worker=0.01,  # Insufficient
            visual_privacy_score=0.2,
            acoustic_privacy_stc=30,
        )
        assert result.zone == "insufficient"
        assert result.details["encounter_paradox_risk"] is True

    def test_acoustic_privacy_scoring(self):
        result_good = compute_soc2_privacy_encounter(
            shared_area_ratio=0.50,
            phone_booths_per_worker=0.125,
            quiet_rooms_per_worker=0.04,
            visual_privacy_score=0.7,
            acoustic_privacy_stc=55,
        )
        result_poor = compute_soc2_privacy_encounter(
            shared_area_ratio=0.50,
            phone_booths_per_worker=0.125,
            quiet_rooms_per_worker=0.04,
            visual_privacy_score=0.7,
            acoustic_privacy_stc=30,
        )
        assert result_good.value > result_poor.value


class TestSC1SpatialIntegration:
    """Tests for SC1 spatial integration/legibility."""

    def test_high_legibility(self):
        result = compute_sc1_spatial_integration(
            integration_normalized=0.9,
            intelligibility=0.95,
            depth_from_entrance=1,
        )
        assert result.zone == "confident"
        assert result.value >= 0.7

    def test_low_legibility(self):
        result = compute_sc1_spatial_integration(
            integration_normalized=0.2,
            intelligibility=0.3,
            depth_from_entrance=8,
        )
        assert result.zone in ["moderate", "disoriented"]
        assert result.value < 0.7

    def test_vertical_transition_penalty(self):
        result_no_vertical = compute_sc1_spatial_integration(
            integration_normalized=0.7,
            intelligibility=0.7,
            depth_from_entrance=3,
            has_vertical_transitions=False,
        )
        result_vertical = compute_sc1_spatial_integration(
            integration_normalized=0.7,
            intelligibility=0.7,
            depth_from_entrance=3,
            has_vertical_transitions=True,
        )
        assert result_no_vertical.value > result_vertical.value

    def test_atrium_mitigation(self):
        result_no_atrium = compute_sc1_spatial_integration(
            integration_normalized=0.7,
            intelligibility=0.7,
            depth_from_entrance=3,
            has_vertical_transitions=True,
            atrium_present=False,
        )
        result_atrium = compute_sc1_spatial_integration(
            integration_normalized=0.7,
            intelligibility=0.7,
            depth_from_entrance=3,
            has_vertical_transitions=True,
            atrium_present=True,
        )
        assert result_atrium.value > result_no_atrium.value


class TestSC4WayfindingSocial:
    """Tests for SC4 wayfinding/social encounter."""

    def test_balanced_social_space(self):
        result = compute_sc4_wayfinding_social(
            integration_normalized=0.6,
            visual_connectivity=0.4,
            edge_richness=0.7,
            expected_encounter_context="social",
        )
        assert result.zone == "balanced"
        assert result.value >= 0.6

    def test_open_plan_risk_detection(self):
        result = compute_sc4_wayfinding_social(
            integration_normalized=0.8,
            visual_connectivity=0.85,  # Very open
            edge_richness=0.15,  # No edges
            expected_encounter_context="work",
        )
        assert result.details["open_plan_risk"] is True
        assert result.details["monitoring_load"] == "excessive"

    def test_context_multiplier(self):
        result_social = compute_sc4_wayfinding_social(
            integration_normalized=0.7,
            visual_connectivity=0.5,
            edge_richness=0.5,
            expected_encounter_context="social",
        )
        result_isolated = compute_sc4_wayfinding_social(
            integration_normalized=0.7,
            visual_connectivity=0.5,
            edge_richness=0.5,
            expected_encounter_context="isolated",
        )
        assert result_social.value > result_isolated.value


class TestVIEW1VQI:
    """Tests for VIEW1 View Quality Index."""

    def test_excellent_nature_view(self):
        result = compute_view1_vqi(
            view_type="nature",
            view_layers=3,
            view_area_ratio=0.5,
            nature_content_ratio=0.9,
            dynamic_content=True,
        )
        assert result.zone == "excellent"
        assert result.value >= 80

    def test_no_view(self):
        result = compute_view1_vqi(
            view_type="none",
            view_layers=0,
            view_area_ratio=0.0,
            nature_content_ratio=0.0,
            dynamic_content=False,
        )
        assert result.zone == "insufficient"
        assert result.value < 20

    def test_urban_view(self):
        result = compute_view1_vqi(
            view_type="urban",
            view_layers=2,
            view_area_ratio=0.4,
            nature_content_ratio=0.2,
            dynamic_content=True,
        )
        assert result.zone in ["adequate", "good"]
        assert 40 <= result.value <= 70

    def test_view_area_modifier(self):
        result_small = compute_view1_vqi(
            view_type="nature",
            view_layers=3,
            view_area_ratio=0.1,
            nature_content_ratio=0.8,
        )
        result_large = compute_view1_vqi(
            view_type="nature",
            view_layers=3,
            view_area_ratio=0.5,
            nature_content_ratio=0.8,
        )
        assert result_large.value > result_small.value


class TestRegistry:
    """Tests for template function registry."""

    def test_all_templates_implemented(self):
        expected = ["VF3", "L1", "L2", "L3", "CREA2", "MAT1", "MAT2", "NMC1",
                    "SOC2", "SC1", "SC4", "VIEW1"]
        implemented = list_implemented_templates()
        for tmpl in expected:
            assert tmpl in implemented, f"Missing template: {tmpl}"

    def test_get_compute_function(self):
        for display_id in list_implemented_templates():
            fn = get_compute_function(display_id)
            assert callable(fn), f"Function for {display_id} not callable"

    def test_get_missing_function(self):
        fn = get_compute_function("NONEXISTENT")
        assert fn is None

    def test_registry_count(self):
        # Registry now includes Batch 1/2/3 plus expanded residual coverage.
        assert len(TEMPLATE_COMPUTE_FUNCTIONS) >= 42

    def test_batch2_templates_implemented(self):
        batch2 = ["L4", "L5", "MAT3", "MAT5", "TP1", "TP2", "TP3", "TP4",
                  "SOC1", "SOC3", "CREA1", "CREA3", "CREA4", "SC2", "SC3",
                  "COL1", "COL2", "VF1", "VF2", "OLF1"]
        implemented = list_implemented_templates()
        for tmpl in batch2:
            assert tmpl in implemented, f"Missing Batch 2 template: {tmpl}"

    def test_batch3_gap_templates_implemented(self):
        batch3 = ["T4", "T6", "T7", "T10", "T14", "T15", "T17", "T18", "T23", "T28"]
        implemented = list_implemented_templates()
        for tmpl in batch3:
            assert tmpl in implemented, f"Missing Batch 3 template: {tmpl}"


# =============================================================================
# BATCH 2 TESTS: L4, L5
# =============================================================================

class TestL4CCTTemporal:
    """Tests for L4 CCT Temporal Ecological."""

    def test_morning_cool_light_congruent(self):
        result = compute_l4_cct_temporal(
            cct_kelvin=5500,
            time_of_day="morning",
            context_type="office",
        )
        assert result.zone == "congruent"
        assert result.value >= 0.8
        assert result.details["processing_style"] == "analytical"

    def test_evening_warm_light_congruent(self):
        result = compute_l4_cct_temporal(
            cct_kelvin=2800,
            time_of_day="evening",
            context_type="residential",
        )
        assert result.zone == "congruent"
        assert result.value >= 0.7
        assert result.details["processing_style"] == "creative"

    def test_evening_cool_light_incongruent(self):
        result = compute_l4_cct_temporal(
            cct_kelvin=6000,
            time_of_day="evening",
            context_type="residential",
        )
        assert result.zone == "incongruent"
        assert result.details["circadian_impact"] is True

    def test_invalid_cct_raises(self):
        with pytest.raises(ValueError):
            compute_l4_cct_temporal(cct_kelvin=500, time_of_day="morning")


class TestL5DynamicLight:
    """Tests for L5 Dynamic Light Temporal PE."""

    def test_natural_daylight_optimal(self):
        result = compute_l5_dynamic_light(
            has_daylight_variation=True,
            has_designed_dynamics=False,
        )
        assert result.zone == "natural_optimal"
        assert result.value >= 0.85

    def test_static_lighting_habituation(self):
        result = compute_l5_dynamic_light(
            has_daylight_variation=False,
            has_designed_dynamics=False,
            static_exposure_hours=5.0,
        )
        assert result.zone == "static_monotony"
        assert result.details["habituation_risk"] is True

    def test_flicker_discomfort(self):
        result = compute_l5_dynamic_light(
            has_daylight_variation=False,
            has_designed_dynamics=True,
            change_rate_hz=5.0,
        )
        assert result.zone == "flicker_discomfort"
        assert result.value <= 0.3


# =============================================================================
# BATCH 2 TESTS: MAT3, MAT5
# =============================================================================

class TestMAT3MaterialIdentity:
    """Tests for MAT3 Material Identity Integration."""

    def test_authentic_wood(self):
        result = compute_mat3_material_identity(
            visual_material="wood",
            haptic_material="wood",
            thermal_material="warm",
            olfactory_match=True,
        )
        assert result.zone == "high_authenticity"
        assert result.value >= 0.8

    def test_fake_material(self):
        result = compute_mat3_material_identity(
            visual_material="wood",
            haptic_material="plastic",
            thermal_material="neutral",
            olfactory_match=False,
        )
        assert result.zone in ["low_authenticity", "fake"]
        assert result.details["pe_level"] in ["high", "very_high"]

    def test_partial_congruence(self):
        result = compute_mat3_material_identity(
            visual_material="stone",
            haptic_material="stone",
            thermal_material="cool",
            olfactory_match=True,
        )
        assert result.value >= 0.7


class TestMAT5MaterialCultural:
    """Tests for MAT5 Material Cultural Conditioning."""

    def test_marble_luxury_positive(self):
        result = compute_mat5_material_cultural(
            material_type="marble",
            context_type="luxury",
        )
        assert result.zone == "positive"
        assert result.value >= 0.8

    def test_raw_concrete_domestic_negative(self):
        result = compute_mat5_material_cultural(
            material_type="raw_concrete",
            context_type="domestic",
        )
        # Raw concrete in domestic context may be negative
        assert result.value < result.details["base_valence"]

    def test_needs_calibration_flag(self):
        result = compute_mat5_material_cultural(
            material_type="brick",
            context_type="commercial",
        )
        assert result.details["needs_calibration"] is True


# =============================================================================
# BATCH 2 TESTS: TP1, TP2
# =============================================================================

class TestTP1MotorPE:
    """Tests for TP1 Motor Prediction Error."""

    def test_level_surface_fluent(self):
        result = compute_tp1_motor_pe(
            surface_type="level",
            coefficient_of_friction=0.6,
        )
        assert result.zone == "fluent"
        assert result.value >= 0.85

    def test_steep_stairs_attention(self):
        result = compute_tp1_motor_pe(
            surface_type="stairs_steep",
            step_height_mm=200,
            coefficient_of_friction=0.5,
        )
        assert result.zone in ["attention_required", "conscious_control"]

    def test_age_increases_cost(self):
        result_young = compute_tp1_motor_pe(
            surface_type="stairs_optimal",
            occupant_age=30,
        )
        result_older = compute_tp1_motor_pe(
            surface_type="stairs_optimal",
            occupant_age=75,
        )
        assert result_young.value > result_older.value
        assert result_older.details["attentional_cost_multiplier"] > 1.5

    def test_slip_hazard_detection(self):
        result = compute_tp1_motor_pe(
            surface_type="level",
            coefficient_of_friction=0.3,
        )
        assert result.details["fall_risk"] is True


class TestTP2ThresholdBoundary:
    """Tests for TP2 Threshold Episodic Boundary."""

    def test_single_channel_weak(self):
        result = compute_tp2_threshold_boundary(
            spatial_change=True,
            light_change=False,
            sound_change=False,
            material_change=False,
        )
        assert result.zone == "weak"
        assert result.value < 0.4

    def test_multi_channel_strong(self):
        result = compute_tp2_threshold_boundary(
            spatial_change=True,
            light_change=True,
            sound_change=True,
            material_change=True,
        )
        assert result.zone == "strong"
        assert result.value >= 0.7

    def test_super_additivity(self):
        result = compute_tp2_threshold_boundary(
            spatial_change=True,
            light_change=True,
            sound_change=True,
            material_change=False,
        )
        assert result.details["super_additivity"] > 0

    def test_passive_traversal_reduced(self):
        result_active = compute_tp2_threshold_boundary(
            spatial_change=True,
            light_change=True,
            sound_change=False,
            material_change=False,
            traversal_active=True,
        )
        result_passive = compute_tp2_threshold_boundary(
            spatial_change=True,
            light_change=True,
            sound_change=False,
            material_change=False,
            traversal_active=False,
        )
        assert result_active.value > result_passive.value


class TestTP3TP4Stubs:
    """Tests for TP3 and TP4 stub implementations."""

    def test_tp3_returns_stub(self):
        result = compute_tp3_temporal_rhythm()
        assert result.details["needs_calibration"] is True
        assert result.details["stub_implementation"] is True
        assert result.confidence <= 0.5

    def test_tp4_returns_stub(self):
        result = compute_tp4_temporal_hierarchy()
        assert result.details["needs_calibration"] is True
        assert result.confidence <= 0.5


# =============================================================================
# BATCH 2 TESTS: SOC1, SOC3
# =============================================================================

class TestSOC1ProxemicPE:
    """Tests for SOC1 Proxemic PE."""

    def test_stranger_appropriate_distance(self):
        result = compute_soc1_proxemic_pe(
            actual_distance_cm=120,
            relationship_type="stranger",
            cultural_cluster="north_american",
        )
        assert result.zone == "appropriate"
        assert result.value >= 0.7

    def test_stranger_too_close(self):
        result = compute_soc1_proxemic_pe(
            actual_distance_cm=50,
            relationship_type="stranger",
        )
        assert result.zone == "too_close"
        assert result.details["behavioral_response"] == "inhibition"

    def test_intimate_close_appropriate(self):
        result = compute_soc1_proxemic_pe(
            actual_distance_cm=30,
            relationship_type="intimate",
        )
        assert result.zone == "appropriate"
        assert result.value >= 0.8

    def test_cultural_variation(self):
        result_na = compute_soc1_proxemic_pe(
            actual_distance_cm=95,
            relationship_type="stranger",
            cultural_cluster="north_american",
        )
        result_la = compute_soc1_proxemic_pe(
            actual_distance_cm=95,
            relationship_type="stranger",
            cultural_cluster="latin_american",
        )
        # Latin American expects closer - 95cm is more "too far" for them
        assert result_na.value != result_la.value


class TestSOC3Territorial:
    """Tests for SOC3 Territorial Affordance."""

    def test_private_low_load(self):
        result = compute_soc3_territorial(
            zone_type="private",
            boundary_clarity=0.9,
            group_size=1,
            has_back_stage=True,
        )
        assert result.value >= 0.8
        assert result.details["goffman_stage"] == "back_stage"

    def test_public_high_load(self):
        result = compute_soc3_territorial(
            zone_type="public",
            boundary_clarity=0.5,
            group_size=200,
        )
        assert result.value < 0.5
        assert result.details["goffman_stage"] == "full_front_stage"

    def test_back_stage_availability(self):
        result_with = compute_soc3_territorial(
            zone_type="semi_public",
            boundary_clarity=0.6,
            group_size=20,
            has_back_stage=True,
        )
        result_without = compute_soc3_territorial(
            zone_type="semi_public",
            boundary_clarity=0.6,
            group_size=20,
            has_back_stage=False,
        )
        assert result_with.value > result_without.value


# =============================================================================
# BATCH 2 TESTS: CREA1, CREA3, CREA4
# =============================================================================

class TestCREA1CreativeNetwork:
    """Tests for CREA1 Creative Network Dynamics."""

    def test_generative_phase_match(self):
        result = compute_crea1_creative_network(
            phase="generative",
            noise_db=68,
            light_lux=150,
            ceiling_rh=0.40,
        )
        assert result.value >= 0.7
        assert result.details["network_state"] == "dmn_dominant"

    def test_evaluative_phase_match(self):
        result = compute_crea1_creative_network(
            phase="evaluative",
            noise_db=40,
            light_lux=450,
            ceiling_rh=0.30,
        )
        assert result.value >= 0.7
        assert result.details["network_state"] == "ecn_dominant"

    def test_phase_mismatch(self):
        result = compute_crea1_creative_network(
            phase="generative",
            noise_db=40,  # Too quiet for generative
            light_lux=450,  # Too bright for generative
            ceiling_rh=0.25,
        )
        assert result.value < 0.5


class TestCREA3Incubation:
    """Tests for CREA3 Incubation Architecture."""

    def test_outdoor_walking_effective(self):
        result = compute_crea3_incubation(
            is_walking=True,
            path_has_nature=True,
            walk_duration_min=15,
            is_indoors=False,
        )
        assert result.zone == "effective"
        assert result.details["total_divergent_d"] >= 0.7

    def test_indoor_walking_moderate(self):
        result = compute_crea3_incubation(
            is_walking=True,
            path_has_nature=False,
            walk_duration_min=10,
            is_indoors=True,
        )
        assert result.value >= 0.5
        assert result.details["base_effect_d"] >= 0.5

    def test_not_walking_minimal(self):
        result = compute_crea3_incubation(
            is_walking=False,
            path_has_nature=True,
            walk_duration_min=15,
        )
        assert result.zone == "minimal" or result.zone == "moderate"
        assert result.details["base_effect_d"] == 0.0


class TestCREA4Stub:
    """Tests for CREA4 stub implementation."""

    def test_crea4_returns_stub(self):
        result = compute_crea4_collaborative()
        assert result.details["needs_calibration"] is True
        assert result.details["stub_implementation"] is True


# =============================================================================
# BATCH 2 TESTS: SC2, SC3
# =============================================================================

class TestSC2Isovist:
    """Tests for SC2 Isovist Visual Prediction."""

    def test_moderate_exposure_optimal(self):
        result = compute_sc2_isovist(
            isovist_area_m2=100,
            isovist_perimeter_m=50,
        )
        assert result.zone == "moderate"
        assert result.value >= 0.6  # Moderate exposure is Goldilocks

    def test_very_high_exposure(self):
        result = compute_sc2_isovist(
            isovist_area_m2=600,
            isovist_perimeter_m=100,
        )
        assert result.zone == "very_high"
        assert result.value < 0.6  # May be overwhelming


class TestSC3Promenade:
    """Tests for SC3 Architectural Promenade."""

    def test_rich_sequence(self):
        result = compute_sc3_promenade(
            sequence_length=5,
            pe_variation=0.5,
        )
        assert result.zone == "rich"
        assert result.value >= 0.7

    def test_short_sequence(self):
        result = compute_sc3_promenade(
            sequence_length=1,  # Very short sequence
            pe_variation=0.5,
        )
        assert result.value < result.details["variation_score"]  # Penalized by short sequence


# =============================================================================
# BATCH 2 TESTS: COL1, COL2, VF1, VF2, OLF1
# =============================================================================

class TestCOL1ChromaticPE:
    """Tests for COL1 Chromatic PE."""

    def test_blue_positive_ecological(self):
        result = compute_col1_chromatic_pe(
            dominant_hue="blue",
            saturation=0.5,
            context_type="office",
        )
        assert result.zone == "positive"
        assert result.details["ecological_valence"] >= 0.7

    def test_habituation_reduces_score(self):
        result_fresh = compute_col1_chromatic_pe(
            dominant_hue="green",
            saturation=0.5,
            exposure_days=0,
        )
        result_habituated = compute_col1_chromatic_pe(
            dominant_hue="green",
            saturation=0.5,
            exposure_days=20,
        )
        assert result_fresh.value > result_habituated.value

    def test_context_adjustment(self):
        result = compute_col1_chromatic_pe(
            dominant_hue="red",
            saturation=0.6,
            context_type="office",  # Red in office is negative
        )
        assert result.details["context_adjustment"] < 0


class TestCOL2Stub:
    """Tests for COL2 stub implementation."""

    def test_col2_returns_stub(self):
        result = compute_col2_color_harmony()
        assert result.details["needs_calibration"] is True


class TestVF1ContourCurvature:
    """Tests for VF1 Contour PE Curvature."""

    def test_curved_preferred(self):
        result = compute_vf1_contour_curvature(
            curvature_ratio=0.7,
            dominant_contour="curved",
        )
        assert result.zone == "curved_preferred"
        assert result.value >= 0.8

    def test_angular_threat_risk(self):
        result = compute_vf1_contour_curvature(
            curvature_ratio=0.1,
            dominant_contour="angular",
        )
        assert result.details["threat_activation_risk"] is True
        assert result.value < 0.6


class TestVF2Stub:
    """Tests for VF2 stub implementation."""

    def test_vf2_returns_stub(self):
        result = compute_vf2_visual_rhythm()
        assert result.details["needs_calibration"] is True


class TestOLF1OlfactoryPE:
    """Tests for OLF1 Olfactory PE Transition."""

    def test_congruent_threshold_enhanced(self):
        result = compute_olf1_olfactory_pe(
            material_scent_match=True,
            functional_scent_match=True,
            is_threshold_crossing=True,
            exposure_minutes=0.5,
        )
        assert result.zone == "congruent"
        assert result.details["episodic_encoding"] == "enhanced"
        assert result.details["proust_effect_potential"] is True

    def test_adaptation_reduces_contribution(self):
        result_fresh = compute_olf1_olfactory_pe(
            material_scent_match=True,
            functional_scent_match=True,
            is_threshold_crossing=False,
            exposure_minutes=1,
        )
        result_adapted = compute_olf1_olfactory_pe(
            material_scent_match=True,
            functional_scent_match=True,
            is_threshold_crossing=False,
            exposure_minutes=15,
        )
        assert result_fresh.value > result_adapted.value

    def test_incongruent_material(self):
        result = compute_olf1_olfactory_pe(
            material_scent_match=False,
            functional_scent_match=False,
            is_threshold_crossing=False,
        )
        assert result.zone == "incongruent"
        assert result.value < 0.7  # Lower score due to mismatches


# =============================================================================
# BATCH 3 TESTS: GAP TEMPLATES T4/T6/T7/T10/T14/T15/T17/T18/T23/T28
# =============================================================================

class TestGapTemplateComputations:
    """Tests for Task 3.8 qualitative gap computations."""

    def _assert_gap_shape(self, result):
        assert result.unit == "wis_0_100"
        assert result.zone in ["low", "moderate", "high"]
        assert result.details["needs_calibration"] is True
        assert result.details["risk_level"] == result.zone
        assert result.value in [25.0, 45.0, 65.0]

    def test_t4_high_risk_attention_demand(self):
        result = compute_t4_attention_demand(15, 0.9, 0.0)
        self._assert_gap_shape(result)
        assert result.zone == "high"

    def test_t6_low_risk_cortisol_cascade(self):
        result = compute_t6_cortisol_cascade(40, 0.9, 0.9)
        self._assert_gap_shape(result)
        assert result.zone == "low"

    def test_t7_moderate_allostatic_anticipation(self):
        result = compute_t7_allostatic_anticipation(0.5, 0.6, 4)
        self._assert_gap_shape(result)
        assert result.zone == "moderate"

    def test_t10_high_sleep_disruption(self):
        result = compute_t10_sleep_consolidation(55, 30, False)
        self._assert_gap_shape(result)
        assert result.zone == "high"

    def test_t14_navigation_stress(self):
        result = compute_t14_navigation_stress_loop(6, 0.8, 0.8)
        self._assert_gap_shape(result)
        assert result.zone in ["moderate", "high"]

    def test_t15_environmental_control(self):
        result = compute_t15_environmental_control(0.3, 7, 14)
        self._assert_gap_shape(result)
        assert result.zone in ["moderate", "high"]

    def test_t17_dopaminergic_novelty(self):
        result = compute_t17_dopaminergic_novelty(0.2, 20, 0.2)
        self._assert_gap_shape(result)
        assert result.zone == "high"

    def test_t18_vestibular_spatial(self):
        result = compute_t18_vestibular_spatial(18, 0.2, 5)
        self._assert_gap_shape(result)
        assert result.zone in ["moderate", "high"]

    def test_t23_context_memory(self):
        result = compute_t23_context_memory(0.9, 0.9, 1)
        self._assert_gap_shape(result)
        assert result.zone == "low"

    def test_t28_cognitive_offloading(self):
        result = compute_t28_cognitive_offloading(0.2, 0.2, 0.9)
        self._assert_gap_shape(result)
        assert result.zone == "high"
