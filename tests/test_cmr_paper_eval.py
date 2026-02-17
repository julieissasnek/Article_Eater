from src.cmr.models import TemplateRecord, create_tables, get_session
from src.cmr.paper_eval import evaluate_paper


def _seed_template(session, display_id: str, name: str, series: str):
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
            json_path=f"data/templates/{display_id}.json",
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
