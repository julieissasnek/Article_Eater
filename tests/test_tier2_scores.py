"""Tests for Tier 2 construct scoring integration (Sprint 12 Task 12.15)."""

from __future__ import annotations

from src.cmr.building_eval import evaluate_building
from src.cmr.template_scanner import scan_templates
from src.cmr.tier2_scores import compute_tier2_scores


def test_compute_tier2_scores_uses_coverage_weighted_average(monkeypatch):
    def fake_reduce_theory(theory: str):
        if theory == "ART":
            return [
                {
                    "construct": "Being_Away",
                    "template_mappings": [
                        {"template_id": "VIEW1", "coverage": 0.40},
                        {"template_id": "SC2", "coverage": 0.25},
                        {"template_id": "VF3", "coverage": 0.20},
                    ],
                }
            ]
        return []

    monkeypatch.setattr("src.cmr.tier2_scores.reduce_theory", fake_reduce_theory)

    scores = compute_tier2_scores({"VIEW1": 85.0, "SC2": 70.0, "VF3": 65.0})
    expected = (85.0 * 0.40 + 70.0 * 0.25 + 65.0 * 0.20) / (0.40 + 0.25 + 0.20)
    assert scores["ART"]["Being_Away"] == round(expected, 1)


def test_evaluate_building_returns_tier2_scores_field(tmp_path):
    db_path = str(tmp_path / "tier2_eval.db")
    scan_templates(db_path=db_path)

    result = evaluate_building(
        building_context={"building_name": "Tier2 Integration Test"},
        measured_features={
            "ceiling_height_m": 3.0,
            "floor_area_m2": 25.0,
            "has_nature_view": True,
            "view_content": "nature",
            "illuminance_lux": 450,
            "ambient_noise_dba": 42,
            "window_area_ratio": 0.3,
            "primary_material": "wood",
        },
        occupant_profile={"age": 35},
        db_path=db_path,
    )

    assert "tier2_scores" in result
    assert isinstance(result["tier2_scores"], dict)
