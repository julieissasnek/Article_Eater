import pytest

from src.extraction.effect_size_converter import to_cohens_d, to_wis


def test_t_to_d_textbook_value():
    out = to_cohens_d(2.10, "t_value", df2=38)
    assert out["d"] == pytest.approx(0.68, abs=0.01)


def test_f_to_d_textbook_value():
    out = to_cohens_d(4.0, "f_value", df1=1, df2=60)
    assert out["d"] == pytest.approx(0.52, abs=0.01)


def test_r_to_d_textbook_value():
    out = to_cohens_d(0.30, "r")
    assert out["d"] == pytest.approx(0.63, abs=0.01)


def test_eta_squared_to_d_textbook_value():
    out = to_cohens_d(0.06, "eta_squared")
    assert out["d"] == pytest.approx(0.51, abs=0.01)


def test_small_sample_hedges_g_is_smaller_magnitude():
    out = to_cohens_d(2.10, "t_value", n1=10, n2=10)
    assert out["hedges_g"] is not None
    assert abs(out["hedges_g"]) < abs(out["d"])


def test_to_wis_from_r_value_is_high_for_positive_association():
    out = to_wis(0.30, "r")
    assert out["d"] == pytest.approx(0.63, abs=0.01)
    assert out["wis"] > 70.0


def test_to_wis_carries_low_confidence_assumption_for_p_only():
    out = to_wis(0.04, "p_value_only", n=120)
    assert out["wis"] > 50.0
    assert any("low confidence" in assumption for assumption in out["assumptions"])
