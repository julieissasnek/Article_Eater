import json

from src.cmr.models import TemplateRecord, create_tables, get_session
from src.cmr.paper_eval import evaluate_paper


def _seed_template(
    session,
    display_id: str,
    name: str,
    series: str,
    *,
    json_path: str | None = None,
):
    session.add(
        TemplateRecord(
            template_id=f"{display_id}_TEMPLATE_001",
            display_id=display_id,
            name=name,
            series=series,
            generation=2,
            dedup_status="active",
            superseded_by=None,
            pe_contribution="organizational",
            maturity="supported",
            calibration_status="partial",
            practical_accessibility="B",
            ecological_validation=False,
            json_path=json_path or f"data/templates/{display_id}.json",
            source_docs="68",
        )
    )


def test_evaluate_paper_runs_with_provided_claims(tmp_path):
    db_path = str(tmp_path / "paper_eval.db")
    create_tables(db_path)
    session = get_session(db_path)
    _seed_template(session, "MAT1", "Affective Touch Thermal Pathway", "MAT")
    _seed_template(session, "VIEW1", "View Quality Index", "VIEW")
    session.commit()
    session.close()

    result = evaluate_paper(
        paper_text="Dummy paper text about affective touch and stress outcomes.",
        structured_claims=[
            {
                "claim_id": "c1",
                "text": "Affective touch improves stress recovery.",
                "iv": "touch",
                "dv": "stress",
            }
        ],
        db_path=db_path,
    )

    assert result["status"] == "complete"
    assert isinstance(result["report"], dict)
    assert "summary" in result["report"]
    assert len(result["steps"]) == 7
    assert result["steps"][0]["name"] == "claim_extraction"
    assert result["steps"][-1]["name"] == "report_assembly"


def test_evaluate_paper_runs_with_placeholder_claim_extraction(tmp_path):
    db_path = str(tmp_path / "paper_eval_placeholder.db")
    create_tables(db_path)

    result = evaluate_paper(
        paper_text="This is a placeholder paper with no structured claims provided.",
        structured_claims=None,
        db_path=db_path,
    )

    assert result["status"] == "complete"
    assert result["steps"][0]["details"]["mode"] == "placeholder"
    assert len(result["claims"]) == 1


def test_evaluate_paper_contract_shape_with_matched_contradicted_and_gap_claims(tmp_path):
    db_path = str(tmp_path / "paper_eval_contract.db")
    create_tables(db_path)
    session = get_session(db_path)

    view1_json = tmp_path / "VIEW1.json"
    view1_json.write_text(
        json.dumps(
            {
                "display_id": "VIEW1",
                "causal_links": [
                    {
                        "from_level": "environmental",
                        "from_variable": "has_nature_view",
                        "to_level": "affective",
                        "to_variable": "stress",
                        "activity": "reduces stress",
                    }
                ],
                "structural_pattern": "nature view reduces stress",
            }
        ),
        encoding="utf-8",
    )

    crea2_json = tmp_path / "CREA2.json"
    crea2_json.write_text(
        json.dumps(
            {
                "display_id": "CREA2",
                "causal_links": [
                    {
                        "from_level": "environmental",
                        "from_variable": "ambient_noise_dba",
                        "to_level": "cognitive",
                        "to_variable": "creative_output",
                        "activity": "increases creative output",
                    }
                ],
                "structural_pattern": "moderate noise enhances creativity",
            }
        ),
        encoding="utf-8",
    )

    _seed_template(
        session,
        "VIEW1",
        "View Quality Index",
        "VIEW",
        json_path=str(view1_json),
    )
    _seed_template(
        session,
        "CREA2",
        "Processing Style Calibration",
        "CREA",
        json_path=str(crea2_json),
    )
    session.commit()
    session.close()

    result = evaluate_paper(
        structured_claims=[
            {
                "claim_id": "c_match",
                "description": "Nature views reduce stress.",
                "iv": "nature views",
                "dv": "stress",
                "direction": "negative",
            },
            {
                "claim_id": "c_contradict",
                "description": "Ambient noise reduces creative output.",
                "iv": "ambient noise",
                "dv": "creative output",
                "direction": "negative",
            },
            {
                "claim_id": "c_gap",
                "description": "Corridor artwork improves heart rate variability.",
                "iv": "corridor artwork",
                "dv": "heart rate variability",
                "direction": "positive",
            },
        ],
        db_path=db_path,
    )

    assert result["status"] == "complete"
    assert result["paper_summary"]
    assert result["n_claims_extracted"] == 3
    assert result["n_claims_matched"] == 2
    assert result["n_claims_unmatched"] == 1

    assessments = {item["assessment"] for item in result["findings"]}
    assert "contradiction" in assessments
    assert "confirmation" in assessments or "gap" in assessments
    assert any(update["type"] == "gap" for update in result["template_system_updates"])
