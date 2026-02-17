import json

from src.cmr.models import TemplateRecord, create_tables, get_session
from src.cmr.paper_eval import evaluate_paper


def _seed_template(
    session,
    display_id: str,
    name: str,
    series: str,
    *,
    json_path: str,
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
            json_path=json_path,
            source_docs="68",
        )
    )


def test_paper_eval_flags_novel_air_quality_claims_as_gap(tmp_path):
    db_path = str(tmp_path / "paper_eval_novel_gap.db")
    create_tables(db_path)
    session = get_session(db_path)

    t27_json = tmp_path / "T27.json"
    t27_json.write_text(
        json.dumps(
            {
                "display_id": "T27",
                "causal_links": [
                    {
                        "from_level": "physiological",
                        "from_variable": "interoceptive_signal",
                        "to_level": "cognitive",
                        "to_variable": "cognitive_function",
                        "activity": "associated coupling",
                    }
                ],
                "structural_pattern": "interoceptive residual pathway with CO2-linked sensing",
            }
        ),
        encoding="utf-8",
    )

    _seed_template(
        session,
        "T27",
        "Interoceptive Inference Residual",
        "T",
        json_path=str(t27_json),
    )
    session.commit()
    session.close()

    result = evaluate_paper(
        structured_claims=[
            {
                "claim_id": "aq1",
                "description": "Indoor air quality at CO2 1000ppm decreases decision making.",
                "iv": "co2_1000ppm",
                "dv": "decision_making",
                "direction": "decrease",
                "effect_size": -0.7,
            },
            {
                "claim_id": "aq2",
                "description": "CO2 at 2500ppm decreases cognitive function.",
                "iv": "co2_2500ppm",
                "dv": "cognitive_function",
                "direction": "decrease",
                "effect_size": -1.4,
            },
        ],
        db_path=db_path,
    )

    assert result["status"] == "complete"

    all_matches = [match for row in result["template_matches"] for match in row.get("matches", [])]
    assert any(match["template_id"] == "T27" for match in all_matches)
    assert not any(match["match_type"] == "exact" for match in all_matches)

    assert all(finding["assessment"] == "gap" for finding in result["findings"])
    assert all(finding["voi"] == "high" for finding in result["findings"])

    assert any(
        update["type"] == "gap" and "AIR-I panel" in update["detail"]
        for update in result["template_system_updates"]
    )
    assert any(
        "AIR-I panel development" in recommendation
        for recommendation in result["report"].get("recommendations", [])
    )
