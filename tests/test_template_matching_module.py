import json

from src.cmr.models import TemplateRecord
from src.cmr.template_matching import build_template_index, match_claims_to_templates


def _make_template(tmp_path, display_id: str, causal_links: list[dict], structural_pattern: str = "") -> TemplateRecord:
    path = tmp_path / f"{display_id}.json"
    payload = {
        "display_id": display_id,
        "causal_links": causal_links,
        "structural_pattern": structural_pattern,
    }
    path.write_text(json.dumps(payload), encoding="utf-8")
    return TemplateRecord(
        template_id=f"{display_id}_TEMPLATE_001",
        display_id=display_id,
        name=f"{display_id} Template",
        series="TEST",
        generation=2,
        dedup_status="active",
        superseded_by=None,
        pe_contribution="organizational",
        maturity="supported",
        calibration_status="partial",
        practical_accessibility="B",
        ecological_validation=False,
        json_path=str(path),
        source_docs="68",
    )


def _matches_for_claim(results: list[dict], claim_id: str) -> list[dict]:
    for entry in results:
        if entry["claim"].get("claim_id") == claim_id:
            return entry["matches"]
    raise AssertionError(f"Missing claim result for {claim_id}")


def test_build_template_index_extracts_inputs_outputs(tmp_path):
    template = _make_template(
        tmp_path,
        "VIEW1",
        [
            {
                "from_level": "environmental",
                "from_variable": "nature_view",
                "to_level": "affective",
                "to_variable": "stress_reduction",
            }
        ],
        structural_pattern="nature view reduces stress",
    )

    index = build_template_index([template])

    assert "VIEW1" in index
    assert "nature_view" in index["VIEW1"]["inputs"]
    assert "stress_reduction" in index["VIEW1"]["outputs"]


def test_match_claims_to_templates_supports_plan_examples(tmp_path):
    vf3 = _make_template(
        tmp_path,
        "VF3",
        [
            {
                "from_level": "environmental",
                "from_variable": "ceiling_height",
                "to_level": "cognitive",
                "to_variable": "creative_thinking",
            }
        ],
        structural_pattern="ceiling height affects creative thinking",
    )
    crea2 = _make_template(
        tmp_path,
        "CREA2",
        [
            {
                "from_level": "environmental",
                "from_variable": "ambient_noise_dba",
                "to_level": "cognitive",
                "to_variable": "creative_thinking",
            }
        ],
        structural_pattern="ceiling height and acoustic envelope modulate creativity",
    )
    view1 = _make_template(
        tmp_path,
        "VIEW1",
        [
            {
                "from_level": "environmental",
                "from_variable": "nature_view",
                "to_level": "affective",
                "to_variable": "stress_reduction",
            }
        ],
        structural_pattern="nature view supports stress recovery",
    )
    t6 = _make_template(
        tmp_path,
        "T6",
        [
            {
                "from_level": "environmental",
                "from_variable": "nature_view",
                "to_level": "cognitive",
                "to_variable": "attention_restoration",
            }
        ],
        structural_pattern="nature view restores directed attention",
    )

    index = build_template_index([vf3, crea2, view1, t6])
    claims = [
        {"claim_id": "c1", "iv": "ceiling_height", "dv": "creative_thinking"},
        {"claim_id": "c2", "iv": "nature_view", "dv": "stress_reduction"},
        {"claim_id": "c3", "iv": "carpet_color", "dv": "productivity"},
    ]

    results = match_claims_to_templates(claims, index)

    c1_matches = _matches_for_claim(results, "c1")
    c1_by_template = {m["template_id"]: m for m in c1_matches}
    assert c1_by_template["VF3"]["match_type"] == "exact"
    assert c1_by_template["CREA2"]["match_type"] in {"partial_dv", "mechanistic"}

    c2_matches = _matches_for_claim(results, "c2")
    c2_by_template = {m["template_id"]: m for m in c2_matches}
    assert c2_by_template["VIEW1"]["match_type"] == "exact"
    assert c2_by_template["T6"]["match_type"] in {"partial_iv", "mechanistic"}

    c3_matches = _matches_for_claim(results, "c3")
    assert c3_matches == []


def test_match_claims_to_templates_uses_synonym_matching(tmp_path):
    l1 = _make_template(
        tmp_path,
        "L1",
        [
            {
                "from_level": "environmental",
                "from_variable": "illuminance",
                "to_level": "cognitive",
                "to_variable": "alertness",
            }
        ],
        structural_pattern="daylight improves alertness",
    )
    index = build_template_index([l1])

    results = match_claims_to_templates(
        claims=[{"claim_id": "syn1", "iv": "daylight", "dv": "alertness"}],
        template_index=index,
    )

    matches = _matches_for_claim(results, "syn1")
    assert matches
    assert matches[0]["template_id"] == "L1"
    assert matches[0]["match_type"] == "exact"
