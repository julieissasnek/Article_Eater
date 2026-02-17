"""Sprint 11 Task 11.32: Building evaluation provenance tests."""

from __future__ import annotations

import json
import math
import os
import tempfile
from pathlib import Path

from src.cmr.building_eval import evaluate_building
from src.cmr.models import CMRTemplateActivation, get_session
from src.cmr.template_scanner import scan_templates


BASE_FEATURES = {
    "ceiling_height_m": 3.0,
    "floor_area_m2": 25.0,
    "illuminance_lux": 500.0,
    "daylight_exposure_hours": 4.0,
    "time_of_day": "morning",
    "ambient_noise_dba": 42.0,
    "window_area_ratio": 0.6,
    "view_layers": 4,
    "nature_content_ratio": 0.9,
    "dynamic_content": True,
    "has_nature_view": True,
    "view_content": "trees",
    "primary_material": "wood",
    "natural_material_ratio": 0.9,
    "luminance_contrast_cv": 1.0,
    "surface_effusivity": 350.0,
    "contact_temperature_c": 32.0,
    "operative_temp_c": 22.5,
    "running_mean_outdoor_c": 21.0,
    "shared_area_ratio": 0.25,
    "phone_booths_per_worker": 0.20,
    "quiet_rooms_per_worker": 0.10,
    "privacy_visual": "high",
    "privacy_acoustic": "high",
    "spatial_integration_score": 0.8,
    "layout_legibility": 0.85,
    "depth_from_entrance": 2,
    "has_vertical_transitions": False,
    "atrium_present": True,
    "visual_connectivity": 0.8,
    "edge_richness": 0.7,
    "expected_encounter_context": "research",
    "cct_kelvin": 4200.0,
    "context_type": "office",
    "surface_type": "level",
    "step_height_mm": 160.0,
    "coefficient_of_friction": 0.75,
}


def _make_session() -> tuple[object, str]:
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    scan_templates(db_path=path)
    return get_session(path), path


def _evaluate(session, db_path: str, *, age: int = 35, features: dict | None = None) -> dict:
    return evaluate_building(
        building_context={"building_name": "Provenance Fixture"},
        measured_features={**BASE_FEATURES, **(features or {})},
        occupant_profile={"age": age},
        session=session,
        db_path=db_path,
    )


def _activations(session, evaluation_id: int) -> list[CMRTemplateActivation]:
    return (
        session.query(CMRTemplateActivation)
        .filter_by(evaluation_id=evaluation_id)
        .order_by(CMRTemplateActivation.template_display_id)
        .all()
    )


def test_overall_wis_is_geometric_mean_of_domain_scores() -> None:
    session, path = _make_session()
    try:
        result = _evaluate(session, path)
        wis_values = [float(row["wis"]) for row in result.get("domain_scores", [])]
        assert wis_values, "No domain scores returned"

        manual_geomean = math.exp(sum(math.log(max(v, 1e-6)) for v in wis_values) / len(wis_values))
        assert abs(manual_geomean - float(result["overall_wis"])) < 1e-6
    finally:
        session.close()
        os.unlink(path)


def test_domain_scores_trace_to_template_activations() -> None:
    session, path = _make_session()
    try:
        result = _evaluate(session, path)
        acts = _activations(session, int(result["evaluation_id"]))
        activated_template_ids = {row.template_display_id for row in acts}
        assert activated_template_ids, "No persisted template activations"

        for domain in result.get("domain_scores", []):
            template_ids = list(domain.get("template_ids") or [])
            assert template_ids, f"Domain {domain.get('domain')} has no template IDs"
            for template_id in template_ids:
                assert template_id in activated_template_ids
    finally:
        session.close()
        os.unlink(path)


def test_template_activations_persist_inputs_and_raw_outputs() -> None:
    session, path = _make_session()
    try:
        result = _evaluate(session, path)
        acts = _activations(session, int(result["evaluation_id"]))
        assert acts, "No template activations persisted"

        for act in acts:
            inputs = act.inputs or {}
            outputs = act.outputs or {}

            assert "measured_features" in inputs
            assert "mapped_inputs" in inputs
            assert isinstance(inputs.get("mapped_inputs"), dict)

            if outputs.get("source") == "computed":
                assert "raw_output" in outputs, f"{act.template_display_id} missing raw_output"
                assert "wis_pre_interaction" in outputs
                assert "interaction_multiplier" in outputs
    finally:
        session.close()
        os.unlink(path)


def test_l2_threshold_uses_calibration_values_from_template_data() -> None:
    session, path = _make_session()
    try:
        template_path = Path("data/templates/L2_circadian_architectural_regulation.json")
        payload = json.loads(template_path.read_text(encoding="utf-8"))
        calibration = payload.get("calibration_parameters", {})
        assert calibration.get("standard_dose_response", {}).get("medi_threshold")
        assert calibration.get("age_corrected_dose_response", {}).get("medi_threshold")

        young = _evaluate(session, path, age=25)
        old = _evaluate(session, path, age=65)

        young_l2 = next(
            row for row in _activations(session, int(young["evaluation_id"])) if row.template_display_id == "L2"
        )
        old_l2 = next(
            row for row in _activations(session, int(old["evaluation_id"])) if row.template_display_id == "L2"
        )

        young_threshold = float(
            (
                (young_l2.outputs or {})
                .get("raw_output", {})
                .get("details", {})
                .get("adjusted_threshold_lux", 0.0)
            )
        )
        old_threshold = float(
            (
                (old_l2.outputs or {})
                .get("raw_output", {})
                .get("details", {})
                .get("adjusted_threshold_lux", 0.0)
            )
        )
        assert young_threshold >= 240.0
        assert old_threshold > young_threshold
        assert old_threshold >= 350.0
    finally:
        session.close()
        os.unlink(path)


def test_lifespan_moderation_is_recorded_with_age_context() -> None:
    session, path = _make_session()
    try:
        young = _evaluate(session, path, age=25)
        old = _evaluate(session, path, age=70)

        young_map = {row.template_display_id: row for row in _activations(session, int(young["evaluation_id"]))}
        old_map = {row.template_display_id: row for row in _activations(session, int(old["evaluation_id"]))}

        shared = set(young_map) & set(old_map)
        changed = [tid for tid in shared if float(young_map[tid].wis_score) != float(old_map[tid].wis_score)]
        assert changed, "No age-sensitive template differences found"

        for template_id in changed:
            old_outputs = old_map[template_id].outputs or {}
            assert "age" in old_outputs
            assert "lifespan_multiplier" in old_outputs
    finally:
        session.close()
        os.unlink(path)


def test_interaction_adjustments_are_persisted_when_triggered() -> None:
    session, path = _make_session()
    try:
        result = _evaluate(session, path)
        acts = _activations(session, int(result["evaluation_id"]))

        adjusted = [row for row in acts if row.interaction_adjustments]
        assert adjusted, "No interaction adjustments persisted"

        all_adjustment_types = {
            item.get("type")
            for row in adjusted
            for item in (row.interaction_adjustments or [])
            if isinstance(item, dict)
        }
        assert "convergence_triad" in all_adjustment_types

        for row in adjusted:
            outputs = row.outputs or {}
            assert float(outputs.get("interaction_multiplier", 1.0)) >= 1.0
    finally:
        session.close()
        os.unlink(path)
