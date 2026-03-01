"""Sprint 11 Task 11.26: End-to-end argument structure tracing."""

from __future__ import annotations

import os
import tempfile

import pytest

from src.cmr.building_eval import evaluate_building
from src.cmr.claim_extraction import extract_claims_structured
from src.cmr.convergence import assess_convergence, check_composition_failures
from src.cmr.mechanism_tracing import trace_mechanisms
from src.cmr.models import TemplateRecord, get_session
from src.cmr.paper_eval import evaluate_paper
from src.cmr.template_matching import build_template_index, match_claims_to_templates
from src.cmr.template_scanner import scan_templates
from src.cmr.voi_scoring import score_voi


@pytest.fixture(scope="module")
def seeded_db_path() -> str:
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    scan_templates(db_path=path, clear_existing=True)
    try:
        yield path
    finally:
        os.unlink(path)


def _evaluate_building(db_path: str, features: dict, age: int = 50) -> dict:
    session = get_session(db_path)
    try:
        return evaluate_building(
            building_context={"building_name": "argument-tracing-fixture"},
            measured_features=features,
            occupant_profile={"age": age},
            session=session,
            db_path=db_path,
        )
    finally:
        session.close()


def _view_domain_wis(result: dict) -> float:
    for row in result.get("domain_scores", []):
        if row.get("domain") == "VIEW":
            return float(row.get("wis", 0.0))
    return 0.0


def test_full_trace_nature_view_claim(seeded_db_path: str) -> None:
    claim = {
        "iv": "nature_view",
        "dv": "stress_reduction",
        "direction": "decrease",
        "effect_size": 0.5,
        "sample_n": 46,
        "context": "hospital",
    }

    # Step 1: claim extraction
    extracted = extract_claims_structured([claim])
    assert len(extracted) == 1
    assert extracted[0]["iv"] == "nature_view"
    assert extracted[0]["effect_size"] == 0.5
    assert extracted[0]["sample_n"] == 46

    # Step 2: template matching
    session = get_session(seeded_db_path)
    try:
        templates = (
            session.query(TemplateRecord)
            .filter(TemplateRecord.dedup_status == "active")
            .all()
        )
    finally:
        session.close()

    template_index = build_template_index(templates)
    matches = match_claims_to_templates(extracted, template_index)
    assert matches
    matched_ids = {
        match.get("template_id")
        for row in matches
        for match in row.get("matches", [])
    }
    assert "VIEW1" in matched_ids

    view1_match = next(
        match
        for row in matches
        for match in row.get("matches", [])
        if match.get("template_id") == "VIEW1"
    )
    assert view1_match["match_type"] in {"exact", "partial_iv", "partial_dv", "mechanistic"}
    assert float(view1_match.get("match_score", 0.0)) >= 0.5

    # Step 3: mechanism tracing
    enriched_matches = []
    for row in matches:
        enriched_row = {"claim": row.get("claim"), "matches": []}
        for match in row.get("matches", []):
            template_id = match.get("template_id")
            enriched_row["matches"].append(
                {
                    **match,
                    "template_data": template_index.get(template_id, {}).get("json_data", {}),
                }
            )
        enriched_matches.append(enriched_row)

    traced = trace_mechanisms(enriched_matches)
    assert traced
    view1_trace = next(item for item in traced if item.get("template") == "VIEW1")
    assert "substitute_alternatives" in view1_trace
    assert view1_trace.get("moderator_match") in {"full", "partial", "mismatch"}

    # Step 4: convergence
    converged = assess_convergence(traced)
    assert converged
    status = converged[0].get("convergence", {}).get("status")
    assert status in {"strong", "moderate", "single_mechanism", "unsupported", "contradicted"}

    # Step 5: composition
    composed = check_composition_failures(converged)
    assert composed
    assert "composition_analysis" in composed[0]

    # Step 6: VOI scoring
    raw_for_voi = [
        {
            "assessment": "contradiction"
            if item.get("convergence", {}).get("status") == "contradicted"
            else "extension"
            if item.get("matches")
            else "gap",
            "template_maturity": "supported",
            "effect_size": float(claim["effect_size"]),
        }
        for item in composed
    ]
    scored = score_voi(raw_for_voi)
    assert scored
    assert 0.0 <= float(scored[0]["voi_score"]) <= 1.0

    # Step 7: report assembly
    report = evaluate_paper(structured_claims=[claim], db_path=seeded_db_path)
    assert report["n_claims_matched"] >= 1
    assert any(
        match.get("template_id") == "VIEW1"
        for row in report.get("template_matches", [])
        for match in row.get("matches", [])
    )


def test_cross_check_building_pipeline_for_same_argument(seeded_db_path: str) -> None:
    claim = {
        "iv": "nature_view",
        "dv": "stress_reduction",
        "direction": "decrease",
        "effect_size": 0.5,
        "context": "hospital",
    }
    paper = evaluate_paper(structured_claims=[claim], db_path=seeded_db_path)
    assert paper["status"] == "complete"
    assert paper["n_claims_matched"] >= 1

    base_features = {
        "ceiling_height_m": 2.7,
        "floor_area_m2": 20.0,
        "illuminance_lux": 350.0,
        "ambient_noise_dba": 40.0,
        "daylight_exposure_hours": 3.0,
        "time_of_day": "morning",
        "window_area_ratio": 0.2,
        "view_layers": 1,
        "nature_content_ratio": 0.0,
        "dynamic_content": False,
        "has_nature_view": False,
        "view_content": "parking_lot",
        "primary_material": "gypsum",
        "natural_material_ratio": 0.2,
        "luminance_contrast_cv": 0.8,
        "surface_effusivity": 800.0,
        "contact_temperature_c": 30.0,
        "operative_temp_c": 23.0,
        "running_mean_outdoor_c": 20.0,
        "shared_area_ratio": 0.4,
        "phone_booths_per_worker": 0.05,
        "quiet_rooms_per_worker": 0.02,
        "privacy_visual": "moderate",
        "privacy_acoustic": "moderate",
        "spatial_integration_score": 0.6,
        "layout_legibility": 0.7,
        "depth_from_entrance": 3,
        "has_vertical_transitions": False,
        "atrium_present": False,
        "visual_connectivity": 0.5,
        "edge_richness": 0.5,
        "expected_encounter_context": "hospital",
        "cct_kelvin": 4200.0,
        "context_type": "hospital",
        "surface_type": "level",
        "step_height_mm": 165.0,
        "coefficient_of_friction": 0.65,
    }

    with_view = _evaluate_building(
        seeded_db_path,
        {
            **base_features,
            "has_nature_view": True,
            "view_content": "trees_garden",
            "window_area_ratio": 0.6,
            "view_layers": 4,
            "nature_content_ratio": 0.9,
            "dynamic_content": True,
        },
    )
    without_view = _evaluate_building(seeded_db_path, base_features)

    assert with_view["overall_wis"] > without_view["overall_wis"]
    assert _view_domain_wis(with_view) > _view_domain_wis(without_view)
