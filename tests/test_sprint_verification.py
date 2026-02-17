"""Sprint 10/11 integrated verification suite (Sprint 11 Task 11.31)."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest

from src.cmr.building_eval import evaluate_building
from src.cmr.lifespan_moderation import compute_template_with_lifespan
from src.cmr.models import TemplateRecord, get_session
from src.cmr.paper_eval import evaluate_paper
from src.cmr.template_computations import TEMPLATE_COMPUTE_FUNCTIONS
from src.cmr.template_scanner import scan_templates
from src.cmr.wis import cohens_d_to_wis
from src.services.web_persistence import WebPersistenceService


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


@pytest.fixture(scope="module")
def seeded_db_path() -> str:
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    scan_templates(db_path=path)
    try:
        yield path
    finally:
        os.unlink(path)


def _evaluate(db_path: str, name: str, features: dict, age: int = 35) -> dict:
    session = get_session(db_path)
    try:
        return evaluate_building(
            building_context={"building_name": name},
            measured_features=features,
            occupant_profile={"age": age},
            session=session,
            db_path=db_path,
        )
    finally:
        session.close()


def _tier2_links_from_master_web() -> list:
    ae_db = Path("ae.db")
    if not ae_db.exists():
        pytest.skip("No local ae.db present for staging-link verification")

    service = WebPersistenceService(str(ae_db))
    master_web_id = service.get_master_web_id()
    if not master_web_id:
        pytest.skip("Master web not initialized in local ae.db")

    constraints = service.get_constraints_for_web(master_web_id)
    links = []
    for item in constraints:
        haystack = " ".join(
            [
                str(getattr(item, "constraint_type", "")),
                str(getattr(item, "constraint_id", "")),
                str(getattr(item, "source_id", "")),
                str(getattr(item, "target_id", "")),
                str(getattr(item, "provenance", "")),
            ]
        ).lower()
        if "tier2" in haystack and "theory" in haystack:
            links.append(item)

    if not links:
        pytest.skip("No tier2 theory links found in local master web")
    return links


def test_s10_template_db_exists_and_populated(seeded_db_path: str) -> None:
    session = get_session(seeded_db_path)
    try:
        count = session.query(TemplateRecord).count()
    finally:
        session.close()
    assert count >= 150, f"Expected >=150 templates, found {count}"


def test_s10_template_db_has_classifications(seeded_db_path: str) -> None:
    allowed_status = {"active", "superseded", "residual", "reference", "gap"}
    allowed_pe = {"predictive", "explanatory", "organizational"}
    allowed_access = {"A", "B", "C", "D"}

    session = get_session(seeded_db_path)
    try:
        templates = session.query(TemplateRecord).all()
    finally:
        session.close()

    assert templates
    for template in templates:
        assert template.dedup_status in allowed_status
        assert template.pe_contribution in allowed_pe
        assert template.practical_accessibility in allowed_access


def test_s10_no_orphan_json_files(seeded_db_path: str) -> None:
    session = get_session(seeded_db_path)
    try:
        db_json_names = {Path(row.json_path).name for row in session.query(TemplateRecord).all()}
    finally:
        session.close()

    file_names = {path.name for path in Path("data/templates").glob("*.json")}
    assert file_names - db_json_names == set()


def test_s10_staging_links_loaded() -> None:
    links = _tier2_links_from_master_web()
    assert len(links) >= 1361, f"Expected >=1361 tier2 theory links, found {len(links)}"


def test_s10_staging_links_have_theory_ids() -> None:
    links = _tier2_links_from_master_web()
    text = " ".join(
        [
            " ".join(
                [
                    str(getattr(item, "constraint_id", "")),
                    str(getattr(item, "source_id", "")),
                    str(getattr(item, "target_id", "")),
                    str(getattr(item, "provenance", "")),
                ]
            ).lower()
            for item in links
        ]
    )
    assert "art" in text
    assert "biophilia" in text


def test_s10_wis_not_always_50() -> None:
    for d_value in [0.1, 0.2, 0.3, 0.5, 0.8, -0.3, -0.5]:
        assert cohens_d_to_wis(d_value) != 50.0


def test_s10_wis_monotonic() -> None:
    d_values = [-1.0, -0.5, 0.0, 0.2, 0.5, 0.8, 1.0]
    wis_values = [cohens_d_to_wis(value) for value in d_values]
    for i in range(len(wis_values) - 1):
        assert wis_values[i] < wis_values[i + 1]


def test_s10_compute_functions_exist() -> None:
    expected = {"VF3", "L1", "L2", "L3", "MAT1", "MAT2", "MAT4", "SOC2", "SC1", "SC4", "VIEW1", "CREA2"}
    assert expected.issubset(set(TEMPLATE_COMPUTE_FUNCTIONS.keys()))


def test_s10_compute_functions_return_real_values() -> None:
    result = compute_template_with_lifespan(
        template_id="VF3",
        measured_features={"ceiling_height_m": 2.75, "floor_area_m2": 18.0},
        occupant_profile={"age": 35},
    )
    assert result["needs_computation"] is False
    assert result["wis"] != 50.0


def test_s10_orchestrator_calls_real_functions(seeded_db_path: str) -> None:
    salk = _evaluate(seeded_db_path, "Salk Institute", SALK_FEATURES, age=35)
    openplan = _evaluate(seeded_db_path, "Open-plan Office", OPENPLAN_FEATURES, age=35)

    assert salk["overall_wis"] != openplan["overall_wis"]
    assert salk["overall_wis"] != 50.0
    assert openplan["overall_wis"] != 50.0


def test_s10_orchestrator_lifespan_works(seeded_db_path: str) -> None:
    young = _evaluate(seeded_db_path, "Salk Institute", SALK_FEATURES, age=25)
    older = _evaluate(seeded_db_path, "Salk Institute", SALK_FEATURES, age=70)
    assert young["overall_wis"] != older["overall_wis"]


def test_s11_salk_scores_well(seeded_db_path: str) -> None:
    result = _evaluate(seeded_db_path, "Salk Institute", SALK_FEATURES, age=35)
    assert result["overall_wis"] > 55.0


def test_s11_openplan_scores_badly(seeded_db_path: str) -> None:
    result = _evaluate(seeded_db_path, "Open-plan Office", OPENPLAN_FEATURES, age=35)
    assert result["overall_wis"] < 50.0


def test_s11_salk_beats_openplan(seeded_db_path: str) -> None:
    salk = _evaluate(seeded_db_path, "Salk Institute", SALK_FEATURES, age=35)
    openplan = _evaluate(seeded_db_path, "Open-plan Office", OPENPLAN_FEATURES, age=35)
    assert salk["overall_wis"] > openplan["overall_wis"]


def test_s11_paper_eval_runs(seeded_db_path: str) -> None:
    result = evaluate_paper(
        structured_claims=[{"iv": "nature_view", "dv": "restoration", "direction": "increase", "effect_size": 0.5}],
        db_path=seeded_db_path,
    )
    assert result["status"] == "complete"
    assert result.get("findings")


def test_s11_paper_eval_finds_view1(seeded_db_path: str) -> None:
    result = evaluate_paper(
        structured_claims=[{"iv": "nature_view", "dv": "restoration", "direction": "increase", "effect_size": 0.5}],
        db_path=seeded_db_path,
    )
    matched_templates = {
        match["template_id"]
        for row in result.get("template_matches", [])
        for match in row.get("matches", [])
    }
    assert "VIEW1" in matched_templates


def test_s11_paper_eval_sensitive_to_direction(seeded_db_path: str) -> None:
    confirm = evaluate_paper(
        structured_claims=[
            {
                "iv": "ambient_noise_70dba",
                "dv": "divergent_creativity",
                "direction": "increase",
                "effect_size": 0.5,
            }
        ],
        db_path=seeded_db_path,
    )
    contradict = evaluate_paper(
        structured_claims=[
            {
                "iv": "ambient_noise_70dba",
                "dv": "divergent_creativity",
                "direction": "decrease",
                "effect_size": -0.5,
            }
        ],
        db_path=seeded_db_path,
    )
    assert confirm["findings"][0]["assessment"] != contradict["findings"][0]["assessment"]
