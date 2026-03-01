import pytest

from src.cmr.interactions import apply_all_interactions, get_interaction


def test_get_interaction_crea2_combo():
    record = get_interaction("A", "C")
    assert record is not None
    assert record["sub_additivity"] == 0.76
    assert record["type"] == "crea2"


def test_convergence_triad_multiplier():
    scores = [
        {"template": "L3", "wis": 50.0},
        {"template": "MAT4", "wis": 40.0},
        {"template": "VIEW1", "wis": 60.0},
    ]
    adjusted = apply_all_interactions(scores)
    # Only L3 and VIEW1 are actually in the convergence triad, so MAT4 remains unadjusted.
    assert adjusted[0]["wis"] == pytest.approx(50.0 * 1.15, abs=0.01)
    assert adjusted[1]["wis"] == pytest.approx(40.0, abs=0.01)
    assert adjusted[2]["wis"] == pytest.approx(60.0 * 1.15, abs=0.01)
    assert any(adj["type"] == "convergence_triad" for adj in adjusted[0]["interaction_adjustments"])


def test_vf3_crea2b_single_chain_flag():
    scores = [
        {"template": "VF3", "wis": 50.0},
        {"template": "CREA2B", "wis": 75.0},
    ]
    adjusted = apply_all_interactions(scores)
    vf3 = next(item for item in adjusted if item["template"] == "VF3")
    crea2b = next(item for item in adjusted if item["template"] == "CREA2B")
    assert vf3.get("single_chain_with") == "CREA2B"
    assert crea2b.get("single_chain_with") == "VF3"


def test_vf1_vf3_additive_checked_no_adjustment():
    record = get_interaction("VF1", "VF3")
    assert record is not None
    assert record["type"] == "vf_additive"
    assert record["multiplier"] == pytest.approx(1.0)


def test_unrelated_pair_no_interaction():
    scores = [
        {"template": "A", "wis": 50.0},
        {"template": "XYZ", "wis": 80.0},
    ]
    adjusted = apply_all_interactions(scores)
    assert all(not item["interaction_adjustments"] for item in adjusted)
    assert get_interaction("L2", "SOC1") is None
