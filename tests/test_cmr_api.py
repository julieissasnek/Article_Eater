"""Integration tests for src.cmr.api (Sprint 12 Task 12.22)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src.cmr.api import create_app
from src.cmr.models import ReductionClaim, TemplateRecord, create_tables, get_session


def _write_template_json(path: Path, display_id: str) -> str:
    payload = {
        "template_id": f"{display_id}_TEMPLATE_001",
        "display_id": display_id,
        "name": f"{display_id} Template",
        "causal_links": [
            {
                "from_level": "environmental",
                "from_variable": "nature_view",
                "to_level": "cognitive",
                "to_variable": "attention_restoration",
            }
        ],
    }
    path.write_text(json.dumps(payload), encoding="utf-8")
    return str(path)


def _seed_db(db_path: Path, tmp_path: Path) -> None:
    create_tables(str(db_path))
    session = get_session(str(db_path))
    try:
        vf3_json = _write_template_json(tmp_path / "vf3_template.json", "VF3")
        view1_json = _write_template_json(tmp_path / "view1_template.json", "VIEW1")

        session.add_all(
            [
                TemplateRecord(
                    template_id="VISUAL_FORM_CEILING_HEIGHT_001",
                    display_id="VF3",
                    name="Visual Form Ceiling Height",
                    series="VF",
                    generation=2,
                    dedup_status="active",
                    superseded_by=None,
                    pe_contribution="predictive",
                    maturity="supported",
                    calibration_status="partial",
                    practical_accessibility="A",
                    ecological_validation=False,
                    json_path=vf3_json,
                    source_docs="67,68",
                ),
                TemplateRecord(
                    template_id="VIEW_QUALITY_INDEX_001",
                    display_id="VIEW1",
                    name="View Quality Index",
                    series="VIEW",
                    generation=2,
                    dedup_status="active",
                    superseded_by=None,
                    pe_contribution="predictive",
                    maturity="supported",
                    calibration_status="partial",
                    practical_accessibility="A",
                    ecological_validation=False,
                    json_path=view1_json,
                    source_docs="67,68",
                ),
                ReductionClaim(
                    tier2_theory="ART",
                    tier2_construct="Being_Away",
                    reduction_type="partial",
                    template_mappings=[
                        {"template_id": "VIEW1", "mechanism": "visual distance", "coverage": 0.4},
                        {"template_id": "VF3", "mechanism": "spatial transition", "coverage": 0.2},
                    ],
                    irreducible_residual="Intentional disengagement component",
                    confidence="moderate",
                    source_panel="T2-A",
                    staging_links_reconciled=1200,
                    staging_links_total=1251,
                ),
            ]
        )
        session.commit()
    finally:
        session.close()


@pytest.fixture
def client(tmp_path: Path) -> TestClient:
    db_path = tmp_path / "cmr_api_test.db"
    _seed_db(db_path, tmp_path)
    app = create_app(default_db_path=str(db_path))
    return TestClient(app)


def test_docs_available(client: TestClient):
    response = client.get("/docs")
    assert response.status_code == 200


def test_evaluate_building_endpoint(client: TestClient):
    response = client.post(
        "/evaluate/building",
        json={
            "building_context": {"building_type": "office"},
            "measured_features": {
                "ceiling_height_m": 3.0,
                "floor_area_m2": 24.0,
                "has_nature_view": True,
                "view_content": "nature",
            },
            "occupant_profile": {"age": 35},
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "complete"
    assert "overall_wis" in data


def test_evaluate_building_validation_error(client: TestClient):
    response = client.post(
        "/evaluate/building",
        json={
            "building_context": {"building_type": "office"},
            "measured_features": {"ceiling_height_m": 3.0},
            "occupant_profile": {"age": 35},
        },
    )
    assert response.status_code == 422
    assert "Missing" in response.json()["detail"]


def test_evaluate_building_quick_endpoint(client: TestClient):
    response = client.post(
        "/evaluate/building/quick",
        json={
            "ceiling_height_m": 3.0,
            "floor_area_m2": 30.0,
            "has_nature_view": True,
            "view_content": "nature",
            "wayfinding_clear": True,
            "walking_paths_available": True,
            "primary_material": "wood",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "overall_rating" in data
    assert data["templates_assessed"] >= 1


def test_evaluate_paper_endpoint(client: TestClient):
    response = client.post(
        "/evaluate/paper",
        json={
            "structured_claims": [
                {
                    "iv": "nature_view",
                    "dv": "attention_restoration",
                    "direction": "increase",
                    "effect_size": 0.6,
                    "sample_n": 42,
                }
            ],
            "citation": "Sample et al. 2026",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "complete"
    assert data["n_claims_extracted"] == 1


def test_compare_endpoint(client: TestClient):
    response = client.post(
        "/compare",
        json={
            "building_a": {
                "measured_features": {"ceiling_height_m": 2.4, "floor_area_m2": 18.0},
                "occupant_profile": {"age": 35},
            },
            "building_b": {
                "measured_features": {"ceiling_height_m": 3.0, "floor_area_m2": 26.0},
                "occupant_profile": {"age": 35},
            },
            "label_a": "Current",
            "label_b": "Proposed",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["label_a"] == "Current"
    assert data["label_b"] == "Proposed"
    assert "overall_delta" in data


def test_sensitivity_endpoint(client: TestClient):
    response = client.post(
        "/sensitivity",
        json={
            "baseline": {
                "measured_features": {"ceiling_height_m": 2.8, "floor_area_m2": 20.0},
                "occupant_profile": {"age": 35},
            },
            "feature_variations": {"ceiling_height_m": [2.4, 3.2]},
            "top_k": 3,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "baseline_overall_wis" in data
    assert len(data["ranked_impacts"]) >= 1
    assert data["best_single_change"] is not None


def test_templates_endpoints(client: TestClient):
    listing = client.get("/templates")
    assert listing.status_code == 200
    list_data = listing.json()
    assert list_data["count"] >= 2
    assert any(row["display_id"] == "VF3" for row in list_data["templates"])

    detail = client.get("/templates/VF3")
    assert detail.status_code == 200
    detail_data = detail.json()
    assert detail_data["display_id"] == "VF3"
    assert isinstance(detail_data["json_data"], dict)


def test_reduction_endpoint(client: TestClient):
    response = client.get("/reductions/art")
    assert response.status_code == 200
    data = response.json()
    assert data["theory"] == "ART"
    assert data["source"] == "database"
    assert len(data["constructs"]) >= 1

