import json

from src.cmr.building_eval import evaluate_building
from src.cmr.models import TemplateRecord, create_tables, get_session


def _write_template(path, display_id: str) -> str:
    payload = {"display_id": display_id, "inputs_required": []}
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


def test_vf3_age_7_differs_from_age_35_in_orchestrator(tmp_path):
    db_path = tmp_path / "cmr_eval_vf3_age.db"
    create_tables(str(db_path))
    session = get_session(str(db_path))

    vf3_path = _write_template(tmp_path / "vf3.json", display_id="VF3")
    _insert_template(session, "VF3", vf3_path, series="VF")
    session.commit()
    session.close()

    measured = {"ceiling_height_m": 3.2, "floor_area_m2": 16.0}
    child = evaluate_building(
        building_context={"target_description": "VF3 child"},
        measured_features=measured,
        occupant_profile={"age": 7},
        db_path=str(db_path),
    )
    adult = evaluate_building(
        building_context={"target_description": "VF3 adult"},
        measured_features=measured,
        occupant_profile={"age": 35},
        db_path=str(db_path),
    )

    assert child["overall_wis"] != adult["overall_wis"]
    assert child["overall_wis"] > adult["overall_wis"]


def test_l2_age_70_scores_lower_than_age_30_at_same_illuminance(tmp_path):
    db_path = tmp_path / "cmr_eval_l2_age.db"
    create_tables(str(db_path))
    session = get_session(str(db_path))

    l2_path = _write_template(tmp_path / "l2.json", display_id="L2")
    _insert_template(session, "L2", l2_path, series="L")
    session.commit()
    session.close()

    measured = {"illuminance_lux": 300.0, "daylight_exposure_hours": 2.0, "time_of_day": "morning"}
    age_30 = evaluate_building(
        building_context={"target_description": "L2 age 30"},
        measured_features=measured,
        occupant_profile={"age": 30},
        db_path=str(db_path),
    )
    age_70 = evaluate_building(
        building_context={"target_description": "L2 age 70"},
        measured_features=measured,
        occupant_profile={"age": 70},
        db_path=str(db_path),
    )

    assert age_70["overall_wis"] < age_30["overall_wis"]
