import json

import pytest

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


def test_building_eval_applies_convergence_triad_adjustment(tmp_path):
    db_path = tmp_path / "cmr_eval_triad.db"
    create_tables(str(db_path))
    session = get_session(str(db_path))

    l3_path = _write_template(tmp_path / "l3.json", display_id="L3", required_inputs=[], domain="L")
    nmc1_path = _write_template(tmp_path / "nmc1.json", display_id="NMC1", required_inputs=[], domain="NMC")
    view1_path = _write_template(tmp_path / "view1.json", display_id="VIEW1", required_inputs=[], domain="VIEW")

    _insert_template_record(session, "L3", l3_path, series="L")
    _insert_template_record(session, "NMC1", nmc1_path, series="NMC")
    _insert_template_record(session, "VIEW1", view1_path, series="VIEW")
    session.commit()
    session.close()

    report = evaluate_building(
        building_context={
            "target_description": "Convergence triad check",
            "template_wis_overrides": {
                "L3": 50.0,
                "NMC1": 40.0,
                "VIEW1": 60.0,
            },
        },
        measured_features={
            "l2_score": 0.7,
            "view_score": 0.6,
            "l1_score": 0.65,
            "l4_score": 0.55,
            "l5_score": 0.6,
            "primary_material": "wood",
            "natural_material_ratio": 0.5,
            "window_area_ratio": 0.3,
            "view_layers": 3,
            "nature_content_ratio": 0.6,
            "dynamic_content": True,
        },
        occupant_profile={"age": 35},
        db_path=str(db_path),
    )

    domains = {row["domain"]: row for row in report["domain_scores"]}
    assert domains["L"]["wis"] == pytest.approx(50.0 * 1.22, abs=0.01)
    assert domains["NMC"]["wis"] == pytest.approx(40.0 * 1.22, abs=0.01)
    assert domains["VIEW"]["wis"] == pytest.approx(60.0 * 1.22, abs=0.01)
