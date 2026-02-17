import pytest

from src.cmr.wis import (
    aggregate_domain_wis,
    aggregate_overall_wis,
    cohens_d_to_wis,
    goldilocks_to_wis,
    threshold_to_wis,
)


def test_cohens_d_to_wis_zero_is_50():
    assert cohens_d_to_wis(0.0) == pytest.approx(50.0, abs=1e-9)


def test_cohens_d_to_wis_positive_half_is_about_69_1():
    assert cohens_d_to_wis(0.5) == pytest.approx(69.1, abs=0.2)


def test_cohens_d_to_wis_negative_half_is_about_30_9():
    assert cohens_d_to_wis(-0.5) == pytest.approx(30.9, abs=0.2)


def test_geometric_mean_example_90_15_is_about_36_7():
    result = aggregate_overall_wis(
        [
            {"domain": "light", "domain_wis": 90.0},
            {"domain": "acoustics", "domain_wis": 15.0},
        ]
    )
    assert result["overall_wis"] == pytest.approx(36.7, abs=0.2)


def test_goldilocks_mapping_center_outperforms_outside():
    boundaries = {
        "optimal_min": 40.0,
        "optimal_max": 60.0,
        "extreme_low": 20.0,
        "extreme_high": 80.0,
        "optimal_point": 50.0,
    }
    center = goldilocks_to_wis(50.0, boundaries)
    boundary = goldilocks_to_wis(40.0, boundaries)
    outside = goldilocks_to_wis(30.0, boundaries)
    extreme = goldilocks_to_wis(5.0, boundaries)

    assert center > boundary > outside > extreme
    assert 85.0 <= center <= 90.0
    assert 50.0 <= boundary <= 60.0
    assert 25.0 <= outside <= 40.0
    assert 10.0 <= extreme <= 20.0


def test_threshold_mapping_increases_with_distance_above_threshold():
    below = threshold_to_wis(40.0, 100.0)
    at = threshold_to_wis(100.0, 100.0)
    moderate_above = threshold_to_wis(120.0, 100.0)
    well_above = threshold_to_wis(200.0, 100.0)

    assert below < at < moderate_above < well_above
    assert 15.0 <= below <= 25.0
    assert at == pytest.approx(55.0, abs=1e-9)
    assert 65.0 <= moderate_above <= 75.0
    assert 80.0 <= well_above <= 85.0


def test_domain_aggregation_uses_calibration_weights():
    result = aggregate_domain_wis(
        [
            {"template_id": "A", "wis": 80.0, "calibration_confidence": "established"},
            {"template_id": "B", "wis": 20.0, "calibration_confidence": "speculative"},
        ]
    )
    # (80*1.0 + 20*0.2) / (1.0 + 0.2) = 70
    assert result["domain_wis"] == pytest.approx(70.0, abs=1e-9)
