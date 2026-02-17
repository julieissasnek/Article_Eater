"""Tests for CMR feature-to-template input mapping (Sprint 11 Task 11.4)."""

from src.cmr.feature_mapping import (
    STANDARD_BUILDING_FEATURE_EXAMPLE,
    audit_feature_mapping_coverage,
    get_required_template_args,
    map_features_to_template_inputs,
)


def test_vf3_mapping_has_all_required_inputs():
    mapped, missing = map_features_to_template_inputs(
        "VF3",
        dict(STANDARD_BUILDING_FEATURE_EXAMPLE),
        {"age": 35},
    )
    assert missing == []
    assert mapped["ceiling_height_m"] == STANDARD_BUILDING_FEATURE_EXAMPLE["ceiling_height_m"]
    assert mapped["floor_area_m2"] == STANDARD_BUILDING_FEATURE_EXAMPLE["floor_area_m2"]
    assert mapped["occupant_age"] == 35


def test_crea2_mapping_derives_ceiling_rh():
    mapped, missing = map_features_to_template_inputs(
        "CREA2",
        dict(STANDARD_BUILDING_FEATURE_EXAMPLE),
        {"age": 35},
    )
    assert missing == []
    assert "ceiling_rh" in mapped
    assert mapped["ceiling_rh"] > 0
    assert mapped["noise_db"] == STANDARD_BUILDING_FEATURE_EXAMPLE["ambient_noise_dba"]
    assert mapped["ambient_lux"] == STANDARD_BUILDING_FEATURE_EXAMPLE["illuminance_lux"]


def test_view1_mapping_derives_view_type_from_content():
    measured = dict(STANDARD_BUILDING_FEATURE_EXAMPLE)
    measured["has_nature_view"] = True
    measured["view_content"] = "playground_trees"
    mapped, missing = map_features_to_template_inputs("VIEW1", measured, {"age": 7})
    assert missing == []
    assert mapped["view_type"] == "nature"
    assert mapped["occupant_age"] == 7


def test_required_args_introspection_for_vf3():
    required = get_required_template_args("VF3")
    assert required == ["ceiling_height_m", "floor_area_m2"]


def test_coverage_audit_flags_templates_without_standard_inputs():
    audit = audit_feature_mapping_coverage(template_ids=["VF3", "L3", "TP2"])
    assert "VF3" in audit["supported_templates"]
    assert "L3" not in audit["supported_templates"]
    assert "TP2" not in audit["supported_templates"]
    assert "L3" in audit["missing_by_template"]
    assert "TP2" in audit["missing_by_template"]

