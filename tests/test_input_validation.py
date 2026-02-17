from src.cmr.validation import validate_building_inputs


def test_validation_flags_missing_inputs():
    result = validate_building_inputs({"ceiling_height_m": 2.8})
    assert not result.valid
    assert "missing features" in result.missing_features or result.missing_features
    assert result.templates_status
    assert not result.templates_status["L1"]["can_activate"]


def test_validation_warns_out_of_band():
    inputs = {"ambient_noise_dba": 130.0, "ceiling_height_m": 3.0, "floor_area_m2": 20.0}
    result = validate_building_inputs(inputs)
    assert any("ambient_noise_dba" in warning for warning in result.warnings)
