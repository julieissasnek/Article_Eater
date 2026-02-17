import json

from src.cmr.building_eval import evaluate_building
from src.cmr.models import CMRTemplateActivation, TemplateRecord, create_tables, get_session


def _write_template(path, display_id: str, required_inputs: list[str]) -> str:
    payload = {
        "display_id": display_id,
        "inputs_required": required_inputs,
    }
    path.write_text(json.dumps(payload), encoding="utf-8")
    return str(path)


def _insert_template(session, display_id: str, json_path: str, series: str = "TEST"):
    session.add(
        TemplateRecord(
            template_id=f"{display_id}_TEMPLATE_001",
            display_id=display_id,
            name=f"{display_id} Template",
            series=series,
            generation=2,
            dedup_status="active",
            superseded_by=None,
            pe_contribution="organizational",
            maturity="supported",
            calibration_status="partial",
            practical_accessibility="B",
            ecological_validation=False,
            json_path=json_path,
            source_docs="68",
        )
    )


def test_building_eval_uses_feature_mapping_for_vf3(tmp_path):
    db_path = str(tmp_path / "feature_map.db")
    create_tables(db_path)
    session = get_session(db_path)

    template_json = _write_template(
        tmp_path / "vf3.json",
        display_id="VF3",
        required_inputs=["ceiling_height_m", "floor_area_m2"],
    )
    _insert_template(session, "VF3", template_json, series="VF")
    session.commit()
    session.close()

    result = evaluate_building(
        building_context={"target_description": "VF3 mapping test"},
        measured_features={"ceiling_height_m": 3.0, "floor_area_m2": 25.0},
        occupant_profile={"age": 12},
        db_path=db_path,
    )
    assert "VF3" in result["activated_templates"]

    session = get_session(db_path)
    try:
        activation = (
            session.query(CMRTemplateActivation)
            .filter(CMRTemplateActivation.template_display_id == "VF3")
            .one()
        )
        mapped_inputs = activation.inputs["mapped_inputs"]
        assert mapped_inputs["ceiling_height_m"] == 3.0
        assert mapped_inputs["floor_area_m2"] == 25.0
        assert mapped_inputs["occupant_age"] == 12
    finally:
        session.close()


def test_building_eval_flags_data_gap_when_mapped_crea2_inputs_missing(tmp_path):
    db_path = str(tmp_path / "feature_gap.db")
    create_tables(db_path)
    session = get_session(db_path)

    template_json = _write_template(
        tmp_path / "crea2.json",
        display_id="CREA2",
        required_inputs=["ambient_noise_dba", "illuminance_lux", "ceiling_height_m", "floor_area_m2"],
    )
    _insert_template(session, "CREA2", template_json, series="CREA")
    session.commit()
    session.close()

    result = evaluate_building(
        building_context={"target_description": "CREA2 mapping gap test"},
        measured_features={
            "ambient_noise_dba": 45,
            "illuminance_lux": 400,
            "ceiling_height_m": 3.0,
            # floor_area_m2 intentionally missing -> ceiling_rh cannot be derived
        },
        occupant_profile={"age": 30},
        db_path=db_path,
    )
    assert "CREA2" not in result["activated_templates"]
    assert "CREA2" in result["data_gaps"]
