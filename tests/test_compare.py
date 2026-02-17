"""Tests for building comparison mode (Sprint 12 Task 12.19)."""

from __future__ import annotations

from src.cmr.compare import compare_buildings
from src.cmr.template_scanner import scan_templates


def test_compare_buildings_reports_overall_and_domain_deltas(tmp_path):
    db_path = str(tmp_path / "compare.db")
    scan_templates(db_path=db_path)

    features_a = {
        "ceiling_height_m": 2.5,
        "floor_area_m2": 25.0,
        "has_nature_view": False,
        "view_content": "urban_wall",
        "ambient_noise_dba": 60,
        "illuminance_lux": 250,
        "window_area_ratio": 0.1,
        "primary_material": "concrete",
    }
    features_b = {
        "ceiling_height_m": 3.2,
        "floor_area_m2": 25.0,
        "has_nature_view": True,
        "view_content": "nature",
        "ambient_noise_dba": 42,
        "illuminance_lux": 450,
        "window_area_ratio": 0.35,
        "primary_material": "wood",
    }

    result = compare_buildings(
        features_a=features_a,
        features_b=features_b,
        label_a="Current",
        label_b="Proposed",
        occupant_age=35,
        db_path=db_path,
    )

    assert "overall" in result
    assert "per_domain_deltas" in result
    assert "summary" in result
    assert isinstance(result["per_domain_deltas"], list)
    assert result["labels"]["a"] == "Current"
    assert result["labels"]["b"] == "Proposed"
    assert result["overall"]["delta"] != 0.0


def test_compare_buildings_template_activity_changes_present(tmp_path):
    db_path = str(tmp_path / "compare_templates.db")
    scan_templates(db_path=db_path)

    base = {
        "ceiling_height_m": 2.7,
        "floor_area_m2": 20.0,
        "illuminance_lux": 300,
    }
    enriched = {
        **base,
        "has_nature_view": True,
        "view_content": "nature",
        "ambient_noise_dba": 40,
        "window_area_ratio": 0.3,
        "primary_material": "wood",
    }

    result = compare_buildings(
        features_a=base,
        features_b=enriched,
        db_path=db_path,
    )
    changes = result["template_activity_changes"]
    assert "added_in_b" in changes
    assert "removed_in_b" in changes
    assert "shared_count" in changes
