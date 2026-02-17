"""Cross-pipeline integration tests (Sprint 11 Task 11.17)."""

from __future__ import annotations

import os
import tempfile

from src.cmr.building_eval import evaluate_building
from src.cmr.paper_eval import evaluate_paper
from src.cmr.template_scanner import scan_templates
from src.cmr.models import get_session


SALK_FEATURES = {
    "ceiling_height_m": 2.75,
    "floor_area_m2": 18.0,
    "illuminance_lux": 500,
    "ambient_noise_dba": 28,
    "has_nature_view": True,
    "view_content": "nature_with_water",
    "window_area_ratio": 0.6,
    "view_layers": 4,
    "nature_content_ratio": 0.95,
    "dynamic_content": True,
    "time_of_day": "morning",
    "daylight_exposure_hours": 4.0,
    "primary_material": "wood",
    "natural_material_ratio": 0.9,
    "surface_effusivity": 350,
    "contact_temperature_c": 32.0,
    "operative_temp_c": 22.5,
    "running_mean_outdoor_c": 21.0,
    "spatial_integration_score": 1.0,
    "layout_legibility": 0.9,
    "depth_from_entrance": 1,
    "has_vertical_transitions": False,
    "atrium_present": True,
    "visual_connectivity": 0.85,
    "edge_richness": 0.8,
    "expected_encounter_context": "research",
    "shared_area_ratio": 0.2,
    "phone_booths_per_worker": 0.25,
    "quiet_rooms_per_worker": 0.15,
    "privacy_visual": "high",
    "privacy_acoustic": "high",
    "cct_kelvin": 4200,
    "luminance_contrast_cv": 0.1,
    "context_type": "office",
    "surface_type": "level",
    "step_height_mm": 160,
    "coefficient_of_friction": 0.75,
}


OPENPLAN_FEATURES = {
    "ceiling_height_m": 2.7,
    "floor_area_m2": 500.0,
    "illuminance_lux": 500,
    "ambient_noise_dba": 62,
    "has_nature_view": False,
    "view_content": "adjacent_building_wall",
    "window_area_ratio": 0.08,
    "view_layers": 1,
    "nature_content_ratio": 0.05,
    "dynamic_content": False,
    "time_of_day": "morning",
    "daylight_exposure_hours": 1.0,
    "primary_material": "gypsum",
    "natural_material_ratio": 0.02,
    "surface_effusivity": 1400,
    "contact_temperature_c": 27.0,
    "operative_temp_c": 27.5,
    "running_mean_outdoor_c": 22.0,
    "spatial_integration_score": 0.35,
    "layout_legibility": 0.42,
    "depth_from_entrance": 7,
    "has_vertical_transitions": True,
    "atrium_present": False,
    "visual_connectivity": 0.25,
    "edge_richness": 0.31,
    "expected_encounter_context": "open_plan",
    "shared_area_ratio": 0.92,
    "phone_booths_per_worker": 0.01,
    "quiet_rooms_per_worker": 0.00,
    "privacy_visual": "none",
    "privacy_acoustic": "none",
    "cct_kelvin": 6500,
    "luminance_contrast_cv": 0.42,
    "context_type": "office",
    "surface_type": "stairs_steep",
    "step_height_mm": 190,
    "coefficient_of_friction": 0.42,
}


def _domain(result: dict, domain: str) -> float:
    for row in result.get("domain_scores", []):
        if row.get("domain") == domain:
            return float(row.get("wis", 0.0))
    return 0.0


def test_cross_pipeline_salk_view_consistency():
    fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    try:
        scan_templates(db_path=db_path)
        session = get_session(db_path)
        try:
            building = evaluate_building(
                building_context={"building_name": "Salk Institute"},
                measured_features=SALK_FEATURES,
                occupant_profile={"age": 35},
                session=session,
            )
        finally:
            session.close()

        paper = evaluate_paper(
            structured_claims=[
                {
                    "iv": "nature_view",
                    "dv": "restoration",
                    "direction": "increase",
                    "effect_size": 0.5,
                }
            ],
            db_path=db_path,
        )
    finally:
        os.unlink(db_path)

    assert _domain(building, "VIEW") > 70.0
    assert any(
        update.get("template") == "VIEW1"
        for update in paper.get("template_system_updates", [])
    )
    assert any(
        finding.get("assessment") in {"confirmation", "extension"}
        for finding in paper.get("findings", [])
    )


def test_cross_pipeline_claimed_feature_absent_reflects_in_building_domain():
    fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    try:
        scan_templates(db_path=db_path)
        session = get_session(db_path)
        try:
            building = evaluate_building(
                building_context={"building_name": "Open-plan Office"},
                measured_features=OPENPLAN_FEATURES,
                occupant_profile={"age": 35},
                session=session,
            )
        finally:
            session.close()

        paper = evaluate_paper(
            structured_claims=[
                {
                    "iv": "nature_view",
                    "dv": "restoration",
                    "direction": "increase",
                    "effect_size": 0.5,
                }
            ],
            db_path=db_path,
        )
    finally:
        os.unlink(db_path)

    assert _domain(building, "VIEW") < 30.0
    assert any(
        update.get("template") == "VIEW1"
        for update in paper.get("template_system_updates", [])
    )
