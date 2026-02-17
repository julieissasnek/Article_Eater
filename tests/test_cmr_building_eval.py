import json

from src.cmr.building_eval import evaluate_building
from src.cmr.models import TemplateRecord, create_tables, get_session


def _write_template(path, display_id: str, required_inputs: list[str], domain: str) -> str:
    payload = {
        "display_id": display_id,
        "inputs_required": required_inputs,
        "domain": domain,
    }
    path.write_text(json.dumps(payload), encoding="utf-8")
    return str(path)


def _insert_template_record(session, display_id: str, json_path: str, series: str = "A1"):
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


def test_building_eval_pipeline_runs_end_to_end(tmp_path):
    db_path = tmp_path / "cmr_eval.db"
    create_tables(str(db_path))
    session = get_session(str(db_path))

    t1 = _write_template(
        tmp_path / "ok1.json",
        display_id="OK1",
        required_inputs=["ceiling_height_m"],
        domain="A1",
    )
    t2 = _write_template(
        tmp_path / "miss1.json",
        display_id="MISS1",
        required_inputs=["ambient_noise_dba"],
        domain="A2",
    )

    _insert_template_record(session, "OK1", t1, series="A1")
    _insert_template_record(session, "MISS1", t2, series="A2")
    session.commit()
    session.close()

    report = evaluate_building(
        building_context={
            "target_description": "Dummy facility",
            "data_gaps": ["MISS1"],
        },
        measured_features={"ceiling_height_m": 3.0},
        occupant_profile={"age": 35},
        db_path=str(db_path),
    )

    assert report["status"] == "complete"
    assert isinstance(report["domain_scores"], list)
    assert isinstance(report["overall_wis"], float)
    assert "OK1" in report["activated_templates"]
    assert report["data_gaps"] == ["MISS1"]


def test_building_eval_flags_severe_deficit_domain(tmp_path):
    db_path = tmp_path / "cmr_eval_severe.db"
    create_tables(str(db_path))
    session = get_session(str(db_path))

    t1 = _write_template(
        tmp_path / "low1.json",
        display_id="LOW1",
        required_inputs=["ceiling_height_m"],
        domain="A_LOW",
    )
    _insert_template_record(session, "LOW1", t1, series="A_LOW")
    session.commit()
    session.close()

    report = evaluate_building(
        building_context={
            "target_description": "Low score test",
            "template_wis_overrides": {"LOW1": 20.0},
        },
        measured_features={"ceiling_height_m": 2.8},
        occupant_profile={"age": 40},
        db_path=str(db_path),
    )

    assert "A_LOW" in report["severe_deficits"]
    low_domain = next(item for item in report["domain_scores"] if item["domain"] == "A_LOW")
    assert low_domain["wis"] == 20.0
