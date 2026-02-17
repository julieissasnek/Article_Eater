import pytest

from src.cmr.template_computations import (
    compute_t10_sleep_consolidation,
    compute_t14_navigation_stress,
    compute_t15_environmental_control,
    compute_t17_dopaminergic_novelty,
    compute_t18_vestibular_spatial,
    compute_t23_context_memory,
    compute_t28_cognitive_offloading,
    compute_t4_attention_demand,
    compute_t6_cortisol_cascade,
    compute_t7_allostatic_load,
)


def _assert_gap_result(result: dict, expected_risk: str, expected_wis: float):
    assert result["risk_level"] == expected_risk
    assert result["wis"] == pytest.approx(expected_wis)
    assert result["needs_calibration"], "Gap templates must flag calibration need"


def test_t4_attention_high_risk():
    result = compute_t4_attention_demand(task_intensity=0.9, noise_dba=72)
    _assert_gap_result(result, "high", 25.0)


def test_t6_cortisol_high_noise():
    result = compute_t6_cortisol_cascade(noise_dba=80, sleep_quality=0.5, control_perception=0.7)
    _assert_gap_result(result, "high", 25.0)


def test_t7_allostatic_moderate():
    result = compute_t7_allostatic_load(stress_events=3, social_support=0.5, recovery_time=6)
    _assert_gap_result(result, "moderate", 45.0)


def test_t10_sleep_with_high_light():
    result = compute_t10_sleep_consolidation(light_exposure=700, screen_time=2, bedtime_consistency=0.8)
    _assert_gap_result(result, "high", 25.0)


def test_t14_navigation_moderate():
    result = compute_t14_navigation_stress(navigation_complexity=0.7, signage_quality=0.65)
    _assert_gap_result(result, "moderate", 45.0)


def test_t15_control_low_autonomy():
    result = compute_t15_environmental_control(control_autonomy=0.25, mechanical_noise=60)
    _assert_gap_result(result, "high", 25.0)


def test_t17_novelty_low():
    result = compute_t17_dopaminergic_novelty(novelty_density=0.1, prediction_error=0.05)
    _assert_gap_result(result, "high", 25.0)


def test_t18_spatial_moderate():
    result = compute_t18_vestibular_spatial(acceleration_changes=0.6, walkway_smoothness=0.5)
    _assert_gap_result(result, "moderate", 45.0)


def test_t23_context_high_cues():
    result = compute_t23_context_memory(cue_density=0.9, support_structures=0.2)
    _assert_gap_result(result, "high", 25.0)


def test_t28_cognitive_switching_high():
    result = compute_t28_cognitive_offloading(assistive_tools=0.2, task_switching=0.7)
    _assert_gap_result(result, "high", 25.0)
