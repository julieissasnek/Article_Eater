import json

from src.cmr.models import TemplateRecord, create_tables, get_session
from src.cmr.paper_eval import evaluate_paper
from src.cmr.paper_history import (
    create_paper_record,
    get_high_voi_papers,
    get_papers_for_template,
    get_processed_papers,
)


def test_create_and_query_processed_papers(tmp_path):
    db_path = str(tmp_path / "paper_history.db")
    create_tables(db_path)

    create_paper_record(
        citation="Ulrich 1984",
        doi="10.1126/science.6143402",
        n_claims=2,
        n_matched=2,
        n_unmatched=0,
        n_contradictions=0,
        n_confirmations=1,
        n_gaps=0,
        aggregate_voi=0.22,
        proposals_generated=1,
        matched_template_ids=["VIEW1"],
        db_path=db_path,
    )
    create_paper_record(
        citation="Noise and Stress 2000",
        doi="10.1000/noise.2000",
        n_claims=2,
        n_matched=1,
        n_unmatched=1,
        n_contradictions=1,
        n_confirmations=0,
        n_gaps=1,
        aggregate_voi=0.81,
        proposals_generated=2,
        matched_template_ids=["SOC2"],
        db_path=db_path,
    )

    all_records = get_processed_papers(db_path=db_path)
    assert len(all_records) == 2
    assert all_records[0].doi == "10.1000/noise.2000"

    high_voi = get_high_voi_papers(0.7, db_path=db_path)
    assert len(high_voi) == 1
    assert high_voi[0].doi == "10.1000/noise.2000"


def test_get_papers_for_template_filters(tmp_path):
    db_path = str(tmp_path / "paper_history_template.db")
    create_tables(db_path)

    create_paper_record(
        citation="Paper A",
        doi="10.1000/a",
        n_claims=1,
        n_matched=1,
        n_unmatched=0,
        n_contradictions=0,
        n_confirmations=1,
        n_gaps=0,
        aggregate_voi=0.25,
        proposals_generated=0,
        matched_template_ids=["VIEW1", "MAT4"],
        db_path=db_path,
    )
    create_paper_record(
        citation="Paper B",
        doi="10.1000/b",
        n_claims=1,
        n_matched=1,
        n_unmatched=0,
        n_contradictions=0,
        n_confirmations=1,
        n_gaps=0,
        aggregate_voi=0.2,
        proposals_generated=0,
        matched_template_ids=["SOC2"],
        db_path=db_path,
    )

    view_papers = get_papers_for_template("view1", db_path=db_path)
    assert len(view_papers) == 1
    assert view_papers[0].doi == "10.1000/a"


def test_evaluate_paper_writes_history_record(tmp_path):
    db_path = str(tmp_path / "paper_history_eval.db")
    create_tables(db_path)
    session = get_session(db_path)

    view_json = tmp_path / "VIEW1.json"
    view_json.write_text(
        json.dumps(
            {
                "display_id": "VIEW1",
                "causal_links": [
                    {
                        "from_level": "environmental",
                        "from_variable": "nature_view",
                        "to_level": "affective",
                        "to_variable": "stress_reduction",
                        "activity": "increases restoration",
                    }
                ],
                "structural_pattern": "nature_view increases stress_reduction",
            }
        ),
        encoding="utf-8",
    )

    session.add(
        TemplateRecord(
            template_id="VIEW_QUALITY_INDEX_001",
            display_id="VIEW1",
            name="View Quality",
            series="VIEW",
            generation=2,
            dedup_status="active",
            superseded_by=None,
            pe_contribution="predictive",
            maturity="supported",
            calibration_status="partial",
            practical_accessibility="A",
            ecological_validation=True,
            json_path=str(view_json),
            source_docs="68",
        )
    )
    session.commit()
    session.close()

    result = evaluate_paper(
        structured_claims=[
            {
                "iv": "nature_view",
                "dv": "stress_reduction",
                "direction": "increase",
                "effect_size": 0.5,
            }
        ],
        citation="Ulrich 1984",
        doi="10.1126/science.6143402",
        db_path=db_path,
    )
    assert result["status"] == "complete"

    records = get_processed_papers(db_path=db_path)
    assert len(records) == 1
    record = records[0]
    assert record.citation == "Ulrich 1984"
    assert record.doi == "10.1126/science.6143402"
    assert record.n_claims == 1
    assert record.n_matched == 1
    assert "VIEW1" in record.matched_template_ids
