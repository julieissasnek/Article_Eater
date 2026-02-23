from __future__ import annotations

from scripts.compute_system_health import (
    compute_chain_completeness,
    linear_high,
    linear_low,
)


def test_linear_high_clamps_and_scales() -> None:
    assert linear_high(5.0, floor=0.0, target=10.0) == 0.5
    assert linear_high(-1.0, floor=0.0, target=10.0) == 0.0
    assert linear_high(12.0, floor=0.0, target=10.0) == 1.0


def test_linear_low_clamps_and_scales() -> None:
    assert linear_low(1.5, best=1.0, worst=2.0) == 0.5
    assert linear_low(0.2, best=1.0, worst=2.0) == 1.0
    assert linear_low(3.0, best=1.0, worst=2.0) == 0.0


def test_chain_completeness_counts_complete_only_when_all_contracts_present() -> None:
    resolutions = [
        {
            "belief_id": "b1",
            "environment_id": "fractal_dimension",
            "outcome_id": "mood",
            "tier1_relevance": {"ART": 0.8},
            "tier2_relevance": {"FRACTAL_FLUENCY": 0.9},
            "top_templates": [{"display_id": "VIEW1"}],
        },
        {
            "belief_id": "b2",
            "environment_id": "ceiling_height",
            "outcome_id": "stress",
            "tier1_relevance": {"SRT": 0.7},
            "tier2_relevance": {},
            "top_templates": [{"display_id": "SRT1"}],
        },
    ]
    belief_ids = {"b1", "b2"}
    annotations = {"b1": {"schema_version": "v1"}, "b2": {"schema_version": "v1"}}
    bn_nodes = {"out.mood", "out.stress"}

    out = compute_chain_completeness(resolutions, belief_ids, annotations, bn_nodes)

    assert out["counts"]["findings_total"] == 2
    assert out["counts"]["complete_chain"] == 1
    assert out["ratios"]["complete_chain_ratio"] == 0.5
    assert out["counts"]["bn_touched"] == 2
