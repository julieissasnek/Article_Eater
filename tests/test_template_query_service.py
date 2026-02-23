import json
from pathlib import Path

from src.services.template_query_service import TemplateQueryService


def _write_template(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def test_extract_causal_pathway_supports_variable_schema(tmp_path: Path) -> None:
    _write_template(
        tmp_path / "t41.json",
        {
            "template_id": "NM_REWARD_PREDICTION_ERROR_001",
            "display_id": "T41",
            "name": "Environmental Reward Prediction Error",
            "structural_pattern": "MEDIATION",
            "causal_links": [
                {
                    "from_variable": "environmental_outcome",
                    "to_variable": "reward_prediction_error",
                    "activity": "compute_temporal_difference",
                    "from_level": "environmental",
                    "to_level": "subcortical",
                    "bridging_quality": "HIGH",
                    "maturity": "how-actually",
                    "key_evidence": "Schultz et al. 1997",
                }
            ],
        },
    )

    service = TemplateQueryService(str(tmp_path))
    response = service.query(
        "reward prediction error mechanism",
        min_relevance=0.0,
        max_templates=5,
    )

    assert response.relevant_templates
    top = response.relevant_templates[0]
    assert top.display_id == "T41"
    assert top.how
    link = top.how[0]
    assert link.from_entity == "environmental_outcome"
    assert link.to_entity == "reward_prediction_error"
    assert link.level == "environmental"
    assert link.bridging_to == "subcortical"
    assert link.bridging_quality == "HIGH"
    assert "environmental_outcome --[compute_temporal_difference]--> reward_prediction_error" in response.causal_chain


def test_query_deduplicates_template_and_display_id_indexes(tmp_path: Path) -> None:
    _write_template(
        tmp_path / "l2.json",
        {
            "template_id": "CIRCADIAN_ARCH_REG_001",
            "display_id": "L2",
            "name": "Circadian Architectural Regulation",
            "short_description": "ipRGC and SCN pathway for light timing",
            "causal_links": [],
        },
    )

    service = TemplateQueryService(str(tmp_path))
    response = service.query("circadian SCN ipRGC", min_relevance=0.0, max_templates=5)

    assert len(response.relevant_templates) == 1
    assert response.relevant_templates[0].display_id == "L2"


def test_related_templates_resolve_by_template_id(tmp_path: Path) -> None:
    _write_template(
        tmp_path / "a.json",
        {
            "template_id": "A_TEMP_001",
            "display_id": "A1",
            "name": "Primary Template",
            "structural_pattern": "primary relationship",
            "causal_links": [],
            "interactions": [
                {
                    "template_id": "B_TEMP_001",
                    "nature": "Depends on related mechanism",
                }
            ],
        },
    )
    _write_template(
        tmp_path / "b.json",
        {
            "template_id": "B_TEMP_001",
            "display_id": "B1",
            "name": "Related Template",
            "structural_pattern": "supporting mechanism",
            "causal_links": [],
        },
    )

    service = TemplateQueryService(str(tmp_path))
    response = service.query("primary template mechanism", min_relevance=0.0, max_templates=3)

    related_ids = {item.display_id for item in response.related_templates}
    assert "B1" in related_ids
