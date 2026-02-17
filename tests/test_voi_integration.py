import importlib
import json

from src.cmr.models import TemplateRecord, create_tables, get_session
from src.cmr.paper_eval import evaluate_paper


def _seed_template(
    session,
    *,
    display_id: str,
    maturity: str,
    iv: str,
    dv: str,
    direction_activity: str,
    json_path: str,
):
    session.add(
        TemplateRecord(
            template_id=f"{display_id}_TEMPLATE_001",
            display_id=display_id,
            name=f"{display_id} Template",
            series="T",
            generation=2,
            dedup_status="active",
            superseded_by=None,
            pe_contribution="predictive",
            maturity=maturity,
            calibration_status="partial",
            practical_accessibility="B",
            ecological_validation=False,
            json_path=json_path,
            source_docs="68",
        )
    )


def _write_template(path, display_id: str, iv: str, dv: str, direction_activity: str) -> str:
    payload = {
        "display_id": display_id,
        "causal_links": [
            {
                "from_level": "environmental",
                "from_variable": iv,
                "to_level": "cognitive",
                "to_variable": dv,
                "activity": direction_activity,
            }
        ],
        "structural_pattern": f"{iv} {direction_activity} {dv}",
    }
    path.write_text(json.dumps(payload), encoding="utf-8")
    return str(path)


def _aggregate_voi(result: dict) -> float:
    return float(result.get("report", {}).get("summary", {}).get("aggregate_voi", 0.0))


def test_voi_varies_with_contradiction(tmp_path):
    db_path = str(tmp_path / "voi_contradiction.db")
    create_tables(db_path)
    session = get_session(db_path)

    view1_path = _write_template(
        tmp_path / "VIEW1.json",
        display_id="VIEW1",
        iv="nature_view",
        dv="restoration",
        direction_activity="increases",
    )
    _seed_template(
        session,
        display_id="VIEW1",
        maturity="supported",
        iv="nature_view",
        dv="restoration",
        direction_activity="increases",
        json_path=view1_path,
    )
    session.commit()
    session.close()

    confirming = evaluate_paper(
        structured_claims=[
            {
                "claim_id": "confirm",
                "description": "Nature view increases restoration.",
                "iv": "nature_view",
                "dv": "restoration",
                "direction": "increase",
                "effect_size": 0.5,
            }
        ],
        db_path=db_path,
    )
    contradicting = evaluate_paper(
        structured_claims=[
            {
                "claim_id": "contradict",
                "description": "Nature view decreases restoration.",
                "iv": "nature_view",
                "dv": "restoration",
                "direction": "decrease",
                "effect_size": 0.5,
            }
        ],
        db_path=db_path,
    )

    assert _aggregate_voi(contradicting) > _aggregate_voi(confirming)


def test_voi_varies_with_effect_size(tmp_path):
    db_path = str(tmp_path / "voi_effect_size.db")
    create_tables(db_path)

    weak = evaluate_paper(
        structured_claims=[
            {
                "claim_id": "weak_gap",
                "description": "Air quality decreases cognition.",
                "iv": "air_quality",
                "dv": "cognition",
                "direction": "decrease",
                "effect_size": 0.1,
            }
        ],
        db_path=db_path,
    )
    strong = evaluate_paper(
        structured_claims=[
            {
                "claim_id": "strong_gap",
                "description": "Air quality strongly decreases cognition.",
                "iv": "air_quality",
                "dv": "cognition",
                "direction": "decrease",
                "effect_size": 1.4,
            }
        ],
        db_path=db_path,
    )

    assert _aggregate_voi(strong) > _aggregate_voi(weak)


def test_voi_sensitive_to_template_maturity(tmp_path):
    def _run_single_case(
        db_path: str,
        template_display_id: str,
        template_maturity: str,
        iv: str,
        dv: str,
        description: str,
    ) -> dict:
        create_tables(db_path)
        session = get_session(db_path)
        path = _write_template(
            tmp_path / f"{template_display_id}.json",
            display_id=template_display_id,
            iv=iv,
            dv=dv,
            direction_activity="increases",
        )
        _seed_template(
            session,
            display_id=template_display_id,
            maturity=template_maturity,
            iv=iv,
            dv=dv,
            direction_activity="increases",
            json_path=path,
        )
        session.commit()
        session.close()

        return evaluate_paper(
            structured_claims=[
                {
                    "claim_id": f"{template_display_id}_contra",
                    "description": description,
                    "iv": iv,
                    "dv": dv,
                    "direction": "decrease",
                    "effect_size": 0.6,
                }
            ],
            db_path=db_path,
        )

    contradict_supported = _run_single_case(
        db_path=str(tmp_path / "voi_maturity_supported.db"),
        template_display_id="SUP1",
        template_maturity="supported",
        iv="daylight",
        dv="alertness",
        description="Daylight decreases alertness.",
    )
    contradict_speculative = _run_single_case(
        db_path=str(tmp_path / "voi_maturity_speculative.db"),
        template_display_id="SPEC1",
        template_maturity="speculative",
        iv="color_saturation",
        dv="calmness",
        description="Color saturation decreases calmness.",
    )

    assert _aggregate_voi(contradict_supported) > _aggregate_voi(contradict_speculative)


def test_existing_voi_service_consistency():
    old_voi = importlib.import_module("src.services.voi_search")
    new_voi = importlib.import_module("src.cmr.voi_scoring")

    old_path = getattr(old_voi, "__file__", "")
    new_path = getattr(new_voi, "__file__", "")

    assert old_path
    assert new_path
    assert old_path != new_path, "VOI modules should be explicitly separate implementations"
    assert hasattr(new_voi, "score_voi")
