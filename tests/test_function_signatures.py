"""Function signature and wiring drift audit (Sprint 11 Task 11.22)."""

from __future__ import annotations

import inspect
import json

from src.cmr.building_eval import evaluate_building
from src.cmr.feature_mapping import (
    FEATURE_TO_TEMPLATE_INPUT,
    STANDARD_BUILDING_FEATURE_EXAMPLE,
    map_features_to_template_inputs,
)
from src.cmr.models import CMRTemplateActivation, TemplateRecord, create_tables, get_session
from src.cmr.template_computations import TEMPLATE_COMPUTE_FUNCTIONS


CORE_TEMPLATES = [
    "COL2",
    "CREA2",
    "CREA4",
    "L1",
    "L2",
    "L4",
    "L5",
    "MAT1",
    "MAT2",
    "MAT4",
    "SC1",
    "SC4",
    "SOC2",
    "T5",
    "TP1",
    "TP3",
    "TP4",
    "VF2",
    "VF3",
    "VIEW1",
]


def _write_template(path, display_id: str, required_inputs: list[str]) -> str:
    payload = {"display_id": display_id, "inputs_required": required_inputs}
    path.write_text(json.dumps(payload), encoding="utf-8")
    return str(path)


def _insert_template(session, display_id: str, json_path: str, series: str):
    session.add(
        TemplateRecord(
            template_id=f"{display_id}_TEMPLATE_001",
            display_id=display_id,
            name=f"{display_id} Template",
            series=series,
            generation=2,
            dedup_status="active",
            superseded_by=None,
            pe_contribution="predictive",
            maturity="supported",
            calibration_status="partial",
            practical_accessibility="B",
            ecological_validation=False,
            json_path=json_path,
            source_docs="68",
        )
    )


def test_dispatch_map_signatures_accept_occupant_age():
    """Compute dispatch functions should accept occupant_age or **kwargs."""
    for template_id, func in TEMPLATE_COMPUTE_FUNCTIONS.items():
        sig = inspect.signature(func)
        params = sig.parameters
        has_var_kw = any(
            param.kind == inspect.Parameter.VAR_KEYWORD for param in params.values()
        )
        assert "occupant_age" in params or has_var_kw, (
            f"{template_id}:{func.__name__} must accept occupant_age (or **kwargs)"
        )


def test_feature_mapping_arg_match_function_signatures():
    """Mapped target argument names must exist in compute function signatures."""
    for template_id, arg_map in FEATURE_TO_TEMPLATE_INPUT.items():
        func = TEMPLATE_COMPUTE_FUNCTIONS.get(template_id)
        if func is None:
            continue
        params = set(inspect.signature(func).parameters.keys())
        for mapped_arg in arg_map.keys():
            assert mapped_arg in params, (
                f"{template_id} mapping references unknown arg '{mapped_arg}' "
                f"for function {func.__name__}"
            )


def test_core_templates_have_resolvable_required_inputs_with_standard_features():
    """Core templates should resolve required args from standard building payload."""
    features = dict(STANDARD_BUILDING_FEATURE_EXAMPLE)
    profile = {"age": 35}
    missing_by_template: dict[str, list[str]] = {}
    for template_id in CORE_TEMPLATES:
        mapped, missing = map_features_to_template_inputs(template_id, features, profile)
        if missing:
            missing_by_template[template_id] = missing
        else:
            required_params = {
                name
                for name, param in inspect.signature(TEMPLATE_COMPUTE_FUNCTIONS[template_id]).parameters.items()
                if param.default is inspect.Parameter.empty
                and param.kind
                not in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)
            }
            assert required_params.issubset(set(mapped.keys())), (
                f"{template_id} missing mapped required args: "
                f"{sorted(required_params - set(mapped.keys()))}"
            )

    assert not missing_by_template, f"Core templates unresolved required inputs: {missing_by_template}"


def test_wis_conversion_and_interactions_are_not_bypassed(tmp_path):
    """
    Valid inputs for wired templates should produce non-placeholder outputs and
    record interaction adjustments where expected.
    """
    db_path = str(tmp_path / "function_signature_eval.db")
    create_tables(db_path)
    session = get_session(db_path)

    vf3_path = _write_template(tmp_path / "vf3.json", "VF3", ["ceiling_height_m", "floor_area_m2"])
    l2_path = _write_template(tmp_path / "l2.json", "L2", ["illuminance_lux"])
    l3_path = _write_template(tmp_path / "l3.json", "L3", [])
    mat4_path = _write_template(tmp_path / "mat4.json", "MAT4", [])
    view1_path = _write_template(tmp_path / "view1.json", "VIEW1", [])

    _insert_template(session, "VF3", vf3_path, "VF")
    _insert_template(session, "L2", l2_path, "L")
    _insert_template(session, "L3", l3_path, "L")
    _insert_template(session, "MAT4", mat4_path, "MAT")
    _insert_template(session, "VIEW1", view1_path, "VIEW")
    session.commit()
    session.close()

    result = evaluate_building(
        building_context={
            "target_description": "Function signature audit",
            # Force triad activity while still exercising mapped compute paths.
            "template_wis_overrides": {"L3": 50.0, "MAT4": 40.0, "VIEW1": 60.0},
        },
        measured_features={
            "ceiling_height_m": 3.0,
            "floor_area_m2": 25.0,
            "illuminance_lux": 500.0,
            "daylight_exposure_hours": 2.0,
            "time_of_day": "morning",
            "l2_score": 0.7,
            "view_score": 0.65,
            "l1_score": 0.6,
            "l4_score": 0.55,
            "l5_score": 0.6,
            "primary_material": "wood",
            "natural_material_ratio": 0.5,
            "window_area_ratio": 0.4,
            "view_layers": 3,
            "nature_content_ratio": 0.8,
            "dynamic_content": True,
        },
        occupant_profile={"age": 35},
        db_path=db_path,
    )

    assert result["overall_wis"] != 50.0
    assert result["data_gaps"] == []
    assert {"VF3", "L2", "L3", "MAT4", "VIEW1"}.issubset(set(result["activated_templates"]))

    # Verify interaction adjustments persisted to activation rows.
    session = get_session(db_path)
    try:
        triad_activations = (
            session.query(CMRTemplateActivation)
            .filter(CMRTemplateActivation.template_display_id.in_(["L3", "MAT4", "VIEW1"]))
            .all()
        )
        assert len(triad_activations) == 3
        assert all(
            any(adj.get("type") == "convergence_triad" for adj in (row.interaction_adjustments or []))
            for row in triad_activations
        ), "Triad templates should record convergence_triad interaction adjustments"
    finally:
        session.close()
