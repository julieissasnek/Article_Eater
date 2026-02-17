from src.cmr.template_computations import (
    compute_t10_sleep_consolidation,
    compute_t14_navigation_stress_loop,
    compute_t15_environmental_control,
    compute_t17_dopaminergic_novelty,
    compute_t18_vestibular_spatial,
    compute_t23_context_memory,
    compute_t28_cognitive_offloading,
    compute_t4_attention_demand,
    compute_t6_cortisol_cascade,
    compute_t7_allostatic_anticipation,
)


def _assert_gap_result(result, expected_risk: str, expected_wis: float):
    assert result.zone == expected_risk
    assert result.value == expected_wis
    assert result.unit == "wis_0_100"
    assert result.details["needs_calibration"] is True
    assert result.details["risk_level"] == expected_risk


def test_t4_attention_high_risk():
    result = compute_t4_attention_demand(
        distraction_rate_per_hour=14,
        attentional_switch_cost=0.9,
        recovery_breaks_per_hour=0.0,
    )
    _assert_gap_result(result, "high", 25.0)


def test_t6_cortisol_high_noise():
    result = compute_t6_cortisol_cascade(
        chronic_noise_exposure_dba=80,
        sleep_quality=0.5,
        control_perception=0.7,
    )
    _assert_gap_result(result, "high", 25.0)


def test_t7_allostatic_moderate():
    result = compute_t7_allostatic_anticipation(
        unpredictability_index=0.5,
        perceived_control=0.6,
        exposure_duration_hours=4,
    )
    _assert_gap_result(result, "moderate", 45.0)


def test_t10_sleep_with_high_light():
    result = compute_t10_sleep_consolidation(
        night_noise_dba=55,
        light_intrusion_lux=30,
        bedtime_regular=False,
    )
    _assert_gap_result(result, "high", 25.0)


def test_t14_navigation_moderate():
    result = compute_t14_navigation_stress_loop(
        wayfinding_error_rate=6,
        crowding_level=0.8,
        time_pressure=0.8,
    )
    assert result.zone in {"moderate", "high"}
    assert result.details["needs_calibration"] is True


def test_t15_control_low_agency():
    result = compute_t15_environmental_control(
        controllability_score=0.25,
        thermal_discomfort_events_per_day=7,
        acoustic_intrusions_per_day=14,
    )
    assert result.zone in {"moderate", "high"}
    assert result.details["needs_calibration"] is True


def test_t17_novelty_low():
    result = compute_t17_dopaminergic_novelty(
        novelty_density=0.2,
        monotony_days=20,
        exploration_access=0.2,
    )
    _assert_gap_result(result, "high", 25.0)


def test_t18_spatial_moderate():
    result = compute_t18_vestibular_spatial(
        vertical_transition_count=18,
        vestibular_cue_quality=0.2,
        motion_disorientation_events=5,
    )
    assert result.zone in {"moderate", "high"}
    assert result.details["needs_calibration"] is True


def test_t23_context_high_cues():
    result = compute_t23_context_memory(
        context_stability=0.9,
        cue_congruence=0.9,
        transition_frequency=1,
    )
    _assert_gap_result(result, "low", 65.0)


def test_t28_cognitive_switching_high():
    result = compute_t28_cognitive_offloading(
        external_memory_support_score=0.2,
        signage_clarity=0.3,
        working_memory_load=0.7,
    )
    _assert_gap_result(result, "high", 25.0)
