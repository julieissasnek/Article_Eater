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
            pe_contribution="predictive",
            maturity="supported",
            calibration_status="substantial",
            practical_accessibility="B",
            ecological_validation=True,
            json_path=json_path,
            source_docs="68",
        )
    )


def test_paper_eval_flags_contradicting_high_ceiling_study(tmp_path):
    db_path = str(tmp_path / "paper_eval_contradiction.db")
    create_tables(db_path)
    session = get_session(db_path)

    vf3_json = tmp_path / "VF3.json"
    vf3_json.write_text(
        json.dumps(
            {
                "display_id": "VF3",
                "causal_links": [
                    {
                        "from_level": "environmental",
                        "from_variable": "ceiling_height_3.5m",
                        "to_level": "cognitive",
                        "to_variable": "divergent_thinking",
                        "activity": "increases divergent thinking",
                    }
                ],
                "structural_pattern": "higher ceilings increase divergent thinking",
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
                        "from_variable": "ceiling_height_3.5m",
                        "to_level": "cognitive",
                        "to_variable": "divergent_thinking",
                        "activity": "increases divergent thinking",
                    },
                    {
                        "from_level": "environmental",
                        "from_variable": "ceiling_height_3.5m",
                        "to_level": "cognitive",
                        "to_variable": "convergent_thinking",
                        "activity": "increases convergent thinking modestly",
                    },
                ],
                "structural_pattern": "ceiling-height effects are generally facilitative for creativity",
            }
        ),
        encoding="utf-8",
    )

    _seed_template(session, "VF3", "Ceiling Height and Creativity", "VF", json_path=str(vf3_json))
    _seed_template(session, "CREA2", "Creative Processing Calibration", "CREA", json_path=str(crea2_json))
    session.commit()
    session.close()

    result = evaluate_paper(
        structured_claims=[
            {
                "claim_id": "c1",
                "description": "High ceilings impair creative performance in divergent thinking tasks.",
                "iv": "ceiling_height_3.5m",
                "dv": "divergent_thinking",
                "direction": "decrease",
                "effect_size": -0.3,
            },
            {
                "claim_id": "c2",
                "description": "High ceilings improve convergent task performance.",
                "iv": "ceiling_height_3.5m",
                "dv": "convergent_thinking",
                "direction": "increase",
                "effect_size": 0.4,
            },
        ],
        db_path=db_path,
    )

    assert result["status"] == "complete"
    matched_templates = {
        match["template_id"]
        for row in result["template_matches"]
        for match in row.get("matches", [])
    }
    assert "VF3" in matched_templates
    assert "CREA2" in matched_templates

    findings_by_claim = {
        item["claim"].get("dv"): item for item in result["findings"] if isinstance(item.get("claim"), dict)
    }
    assert findings_by_claim["divergent_thinking"]["assessment"] == "contradiction"
    assert findings_by_claim["divergent_thinking"]["voi"] == "high"
    assert findings_by_claim["convergent_thinking"]["assessment"] in {"confirmation", "gap"}

    assert result["prioritized_findings"][0]["category"] == "contradiction"
    assert any(
        "VF3 Goldilocks boundaries" in recommendation
        for recommendation in result["report"].get("recommendations", [])
    )
