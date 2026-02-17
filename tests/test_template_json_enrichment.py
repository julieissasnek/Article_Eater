import json

from scripts.enrich_template_json_fields import (
    enrich_template_data,
    enrich_templates_dir,
)


def test_enrich_template_data_adds_missing_required_fields():
    source = {
        "template_id": "TEST_TEMPLATE_001",
        "display_id": "L9",
        "name": "Test Template",
    }
    updated, added = enrich_template_data(source)

    assert set(added) == {
        "pe_contribution",
        "practical_accessibility",
        "dedup_status",
        "generation",
        "ecological_validation",
    }
    assert updated["pe_contribution"] == "organizational"
    assert updated["practical_accessibility"] == "B"
    assert updated["generation"] == 2
    assert updated["ecological_validation"] is False
    assert updated["dedup_status"] in {"active", "superseded", "residual", "reference", "gap"}


def test_enrich_template_data_does_not_overwrite_existing_values():
    source = {
        "template_id": "TEST_TEMPLATE_002",
        "display_id": "T6",
        "name": "Existing Fields Template",
        "pe_contribution": "predictive",
        "practical_accessibility": "D",
        "dedup_status": "gap",
        "generation": 1,
        "ecological_validation": True,
    }
    updated, added = enrich_template_data(source)

    assert added == []
    assert updated == source


def test_enrich_templates_dir_updates_files_and_validates(tmp_path):
    file_one = tmp_path / "A.json"
    file_two = tmp_path / "B.json"

    file_one.write_text(
        json.dumps(
            {
                "template_id": "TMP_A",
                "display_id": "AX1",
                "name": "Template A",
            }
        ),
        encoding="utf-8",
    )
    file_two.write_text(
        json.dumps(
            {
                "template_id": "TMP_B",
                "display_id": "CREA9",
                "name": "Template B",
                "pe_contribution": "explanatory",
                "practical_accessibility": "A",
                "dedup_status": "active",
                "generation": 2,
                "ecological_validation": False,
            }
        ),
        encoding="utf-8",
    )

    result = enrich_templates_dir(tmp_path)
    assert result["total_files"] == 2
    assert result["changed_files"] == 1
    assert result["validation"]["all_valid"] is True

    data_a = json.loads(file_one.read_text(encoding="utf-8"))
    assert data_a["generation"] == 1
    assert data_a["dedup_status"] in {"active", "superseded", "residual", "reference", "gap"}
    assert data_a["ecological_validation"] is False
