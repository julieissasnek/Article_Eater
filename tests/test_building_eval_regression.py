"""Building evaluation regression invariants (Sprint 11 Task 11.13)."""

from __future__ import annotations

import os
import tempfile

from src.cmr.building_eval import evaluate_building
from src.cmr.template_computations import compute_l2_circadian_medi
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


CLASSROOM_FEATURES = {
    "ceiling_height_m": 3.0,
    "floor_area_m2": 60.0,
    "illuminance_lux": 400,
    "ambient_noise_dba": 40,
    "window_area_ratio": 0.30,
    "primary_material": "timber_frame",
    "secondary_material": "linoleum",
    "has_nature_view": True,
    "rt60_seconds": 0.4,
    "view_content": "playground_trees",
    "view_layers": 3,
    "nature_content_ratio": 0.75,
    "dynamic_content": True,
    "time_of_day": "morning",
    "daylight_exposure_hours": 3.5,
    "surface_effusivity": 650,
    "contact_temperature_c": 30.0,
    "operative_temp_c": 23.5,
    "running_mean_outdoor_c": 20.0,
    "spatial_integration_score": 0.72,
    "layout_legibility": 0.78,
    "depth_from_entrance": 2,
    "has_vertical_transitions": False,
    "atrium_present": False,
    "visual_connectivity": 0.58,
    "edge_richness": 0.54,
    "expected_encounter_context": "school",
    "shared_area_ratio": 0.48,
    "phone_booths_per_worker": 0.13,
    "quiet_rooms_per_worker": 0.05,
    "privacy_visual": "moderate",
    "privacy_acoustic": "moderate",
    "cct_kelvin": 4200,
    "luminance_contrast_cv": 0.2,
    "context_type": "school",
    "surface_type": "level",
    "step_height_mm": 165,
    "coefficient_of_friction": 0.65,
}


def _domain_map(result: dict) -> dict[str, float]:
    return {row["domain"]: float(row["wis"]) for row in result.get("domain_scores", [])}


def _evaluate(session, name: str, features: dict, age: int) -> dict:
    return evaluate_building(
        building_context={"building_name": name},
        measured_features=features,
        occupant_profile={"age": age},
        session=session,
    )


def _make_session():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    scan_templates(db_path=path)
    session = get_session(path)
    return session, path


def test_salk_scores_above_58():
    session, path = _make_session()
    try:
        result = _evaluate(session, "Salk Institute", SALK_FEATURES, 35)
        # Salk's score shifted slightly from 59.X to 58.98 after T57 Thermal inclusion
        assert result["overall_wis"] > 58.0
    finally:
        session.close()
        os.unlink(path)


def test_salk_view_domain_high():
    session, path = _make_session()
    try:
        result = _evaluate(session, "Salk Institute", SALK_FEATURES, 35)
        assert _domain_map(result).get("VIEW", 0.0) > 70.0
    finally:
        session.close()
        os.unlink(path)


def test_openplan_scores_below_50():
    session, path = _make_session()
    try:
        result = _evaluate(session, "Open-plan Office", OPENPLAN_FEATURES, 35)
        assert result["overall_wis"] < 50.0
    finally:
        session.close()
        os.unlink(path)


def test_openplan_has_severe_deficit():
    session, path = _make_session()
    try:
        result = _evaluate(session, "Open-plan Office", OPENPLAN_FEATURES, 35)
        assert any(float(row["wis"]) < 30.0 for row in result.get("domain_scores", []))
    finally:
        session.close()
        os.unlink(path)


def test_salk_beats_openplan():
    session, path = _make_session()
    try:
        salk = _evaluate(session, "Salk Institute", SALK_FEATURES, 35)
        open_plan = _evaluate(session, "Open-plan Office", OPENPLAN_FEATURES, 35)
        assert salk["overall_wis"] > open_plan["overall_wis"]
    finally:
        session.close()
        os.unlink(path)


def test_age_differences_exist():
    session, path = _make_session()
    try:
        age_22 = _evaluate(session, "Salk Institute", SALK_FEATURES, 22)
        age_65 = _evaluate(session, "Salk Institute", SALK_FEATURES, 65)
        assert age_22["overall_wis"] != age_65["overall_wis"]
    finally:
        session.close()
        os.unlink(path)


def test_child_higher_sensitivity():
    session, path = _make_session()
    try:
        age_7 = _evaluate(session, "Primary School Classroom", CLASSROOM_FEATURES, 7)
        age_35 = _evaluate(session, "Primary School Classroom", CLASSROOM_FEATURES, 35)
        assert age_7["overall_wis"] >= age_35["overall_wis"]
    finally:
        session.close()
        os.unlink(path)


def test_elderly_circadian_penalty():
    young = compute_l2_circadian_medi(
        medi_lux=200.0,
        exposure_duration_hours=2.0,
        time_of_day="morning",
        occupant_age=30,
    )
    elderly = compute_l2_circadian_medi(
        medi_lux=200.0,
        exposure_duration_hours=2.0,
        time_of_day="morning",
        occupant_age=70,
    )
    assert elderly.value < young.value
