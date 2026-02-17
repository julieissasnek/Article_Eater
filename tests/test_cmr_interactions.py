import pytest

from src.cmr.interactions import CREA2_INTERACTIONS, apply_all_interactions, get_interaction


def test_crea2_noise_dim_sub_additivity_is_0_76():
    # Doc 65 matrix: noise + dim = A+C
    assert CREA2_INTERACTIONS["A+C"]["sub_additivity"] == 0.76


def test_convergence_triad_all_three_uses_1_22_multiplier():
    scores = [
        {"template": "L3", "wis": 50.0},
        {"template": "MAT4", "wis": 60.0},
        {"template": "VIEW1", "wis": 70.0},
    ]
    adjusted = {row["template"]: row for row in apply_all_interactions(scores)}

    assert adjusted["L3"]["wis"] == pytest.approx(61.0, abs=1e-9)
    assert adjusted["MAT4"]["wis"] == pytest.approx(73.2, abs=1e-9)
    assert adjusted["VIEW1"]["wis"] == pytest.approx(85.4, abs=1e-9)
    assert any(
        item.get("type") == "convergence_triad"
        and item.get("multiplier") == 1.22
        and item.get("channels_active") == 3
        for item in adjusted["L3"]["interaction_adjustments"]
    )


def test_vf3_crea2b_sets_single_chain_flag():
    interaction = get_interaction("VF3", "CREA2B")
    assert interaction is not None
    assert interaction["interaction_type"] == "single_chain"
    assert interaction["compute_independently"] is False

    adjusted = {row["template"]: row for row in apply_all_interactions(
        [{"template": "VF3", "wis": 63.0}, {"template": "CREA2B", "wis": 55.0}]
    )}
    assert any(
        item.get("type") == "single_chain"
        and item.get("from_template") == "VF3"
        and item.get("to_template") == "CREA2B"
        for item in adjusted["CREA2B"]["interaction_adjustments"]
    )


def test_unrelated_templates_have_no_interaction():
    assert get_interaction("L1", "SC4") is None
