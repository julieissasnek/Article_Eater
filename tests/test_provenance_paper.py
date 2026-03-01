"""Sprint 11 Task 11.33: Paper evaluation provenance tests."""

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


BASE_BUILDING_FEATURES = {
    "floor_area_m2": 30.0,
    "illuminance_lux": 400.0,
    "daylight_exposure_hours": 3.0,
    "time_of_day": "morning",
    "ambient_noise_dba": 40.0,
    "window_area_ratio": 0.3,
    "view_layers": 2,
    "nature_content_ratio": 0.2,
    "dynamic_content": False,
    "has_nature_view": False,
    "view_content": "urban",
    "primary_material": "gypsum",
    "natural_material_ratio": 0.2,
    "luminance_contrast_cv": 0.8,
    "surface_effusivity": 800.0,
    "contact_temperature_c": 30.0,
    "operative_temp_c": 23.0,
    "running_mean_outdoor_c": 20.0,
    "shared_area_ratio": 0.5,
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
    "expected_encounter_context": "work",
    "cct_kelvin": 4200.0,
    "context_type": "office",
    "surface_type": "level",
    "step_height_mm": 165.0,
    "coefficient_of_friction": 0.65,
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


def _domain_score(result: dict, domain: str) -> float:
    for row in result.get("domain_scores", []):
        if row.get("domain") == domain:
            return float(row.get("wis", 0.0))
    return 0.0


def _evaluate_building_with_ceiling(db_path: str, height_m: float) -> dict:
    session = get_session(db_path)
    try:
        return evaluate_building(
            building_context={"building_name": f"ceiling-{height_m}"},
            measured_features={**BASE_BUILDING_FEATURES, "ceiling_height_m": height_m},
            occupant_profile={"age": 35},
            session=session,
            db_path=db_path,
        )
    finally:
        session.close()


def test_claim_match_records_rationale(seeded_db_path: str) -> None:
    result = evaluate_paper(
        structured_claims=[
            {
                "iv": "nature_view",
                "dv": "stress_reduction",
                "direction": "decrease",
                "effect_size": 0.5,
                "context": "hospital",
            }
        ],
        db_path=seeded_db_path,
    )

    assert result.get("template_matches")
    for row in result["template_matches"]:
        for match in row.get("matches", []):
            assert match.get("rationale")
            assert match.get("match_type")


def test_claim_direction_matters(seeded_db_path: str) -> None:
    confirming = evaluate_paper(
        structured_claims=[
            {
                "iv": "ambient_noise_level",
                "dv": "processing_fluency",
                "direction": "increase",
                "effect_size": 0.6,
            }
        ],
        db_path=seeded_db_path,
    )
    contradicting = evaluate_paper(
        structured_claims=[
            {
                "iv": "ambient_noise_level",
                "dv": "processing_fluency",
                "direction": "decrease",
                "effect_size": -0.6,
            }
        ],
        db_path=seeded_db_path,
    )
    
    assert confirming["findings"][0]["assessment"] != contradicting["findings"][0]["assessment"]
    assert any(update.get("type") == "confirms" for update in confirming["template_system_updates"])
    assert any(update.get("type") == "contradicts" for update in contradicting["template_system_updates"])


def test_effect_size_changes_gap_voi(seeded_db_path: str) -> None:
    weak = evaluate_paper(
        structured_claims=[
            {
                "iv": "electromagnetic_field",
                "dv": "sleep_quality",
                "direction": "decrease",
                "effect_size": -0.2,
            }
        ],
        db_path=seeded_db_path,
    )
    strong = evaluate_paper(
        structured_claims=[
            {
                "iv": "electromagnetic_field",
                "dv": "sleep_quality",
                "direction": "decrease",
                "effect_size": -0.9,
            }
        ],
        db_path=seeded_db_path,
    )

    weak_voi = float(weak["prioritized_findings"][0]["voi_score"])
    strong_voi = float(strong["prioritized_findings"][0]["voi_score"])
    assert weak["findings"][0]["assessment"] == "gap"
    assert strong["findings"][0]["assessment"] == "gap"
    assert strong_voi > weak_voi


def test_contradiction_detected_correctly(seeded_db_path: str) -> None:
    result = evaluate_paper(
        structured_claims=[
            {
                "iv": "spatial_enclosure_ratio",
                "dv": "creative_network_dynamics",
                "direction": "decrease",
                "effect_size": -0.5,
            }
        ],
        db_path=seeded_db_path,
    )

    assert result["findings"][0]["assessment"] == "contradiction"
    assert any(
        update.get("type") == "contradicts" and update.get("template") == "VF3"
        for update in result["template_system_updates"]
    )


def test_gap_identified_for_unmapped_variables(seeded_db_path: str) -> None:
    result = evaluate_paper(
        structured_claims=[
            {
                "iv": "electromagnetic_field",
                "dv": "sleep_quality",
                "direction": "decrease",
                "effect_size": -0.4,
            }
        ],
        db_path=seeded_db_path,
    )

    assert result["n_claims_unmatched"] >= 1
    assert result["findings"][0]["assessment"] == "gap"
    assert any(update.get("type") == "gap" for update in result["template_system_updates"])


def test_full_provenance_chain(seeded_db_path: str) -> None:
    claim = {
        "iv": "spatial_enclosure_ratio",
        "dv": "creative_network_dynamics",
        "direction": "increase",
        "effect_size": 0.6,
        "sample_n": 80,
        "context": "office",
    }

    extracted = extract_claims_structured([claim])
    assert extracted[0]["effect_size"] == 0.6
    assert extracted[0]["sample_n"] == 80

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
    matched_ids = {
        match.get("template_id")
        for row in matches
        for match in row.get("matches", [])
    }
    assert "VF3" in matched_ids

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
    assert any(row.get("template") == "VF3" for row in traced)

    converged = assess_convergence(traced)
    composed = check_composition_failures(converged)
    assert composed
    assert "convergence" in composed[0]
    assert "composition_analysis" in composed[0]

    result = evaluate_paper(structured_claims=[claim], db_path=seeded_db_path)
    step_names = [step.get("name") for step in result.get("steps", [])]
    assert result["status"] == "complete"
    assert result["prioritized_findings"]
    assert result["prioritized_findings"][0].get("voi_score") is not None
    assert "claim_extraction" in step_names
    assert "template_matching" in step_names
    assert "mechanism_tracing" in step_names
    assert "convergence_assessment" in step_names
    assert "composition_check" in step_names
    assert "prioritization" in step_names
    assert "report_assembly" in step_names


def test_paper_and_building_agree_on_ceiling_direction(seeded_db_path: str) -> None:
    paper = evaluate_paper(
        structured_claims=[
            {
                "iv": "spatial_enclosure_ratio",
                "dv": "creative_network_dynamics",
                "direction": "increase",
                "effect_size": 0.5,
            }
        ],
        db_path=seeded_db_path,
    )
    high = _evaluate_building_with_ceiling(seeded_db_path, 3.5)
    low = _evaluate_building_with_ceiling(seeded_db_path, 2.3)

    assert _domain_score(high, "VF") > _domain_score(low, "VF")
    assert high["overall_wis"] >= low["overall_wis"]
    assert any(
        update.get("type") == "confirms" and update.get("template") == "VF3"
        for update in paper["template_system_updates"]
    )


def test_paper_contradiction_aligns_with_system_prediction(seeded_db_path: str) -> None:
    paper = evaluate_paper(
        structured_claims=[
            {
                "iv": "spatial_enclosure_ratio",
                "dv": "creative_network_dynamics",
                "direction": "decrease",
                "effect_size": -0.5,
            }
        ],
        db_path=seeded_db_path,
    )
    high = _evaluate_building_with_ceiling(seeded_db_path, 3.5)
    low = _evaluate_building_with_ceiling(seeded_db_path, 2.3)

    assert _domain_score(high, "VF") > _domain_score(low, "VF")
    assert any(
        update.get("type") == "contradicts" and update.get("template") == "VF3"
        for update in paper["template_system_updates"]
    )
