from src.extraction.table_semantics_codex import build_table_content_profile


def test_profile_detects_regression_table():
    table = {
        "table_id": "T1",
        "paper_id": "p1",
        "rows": [
            {"text": "Predictor beta SE p-value"},
            {"text": "Daylight beta = 0.34 SE = 0.10 p = 0.01"},
        ],
    }
    profile = build_table_content_profile(table)
    assert profile["semantic_type"] == "regression_coefficients"
    assert profile["extractable"] is True


def test_profile_rejects_reference_table():
    table = {
        "table_id": "T2",
        "paper_id": "p2",
        "rows": [
            {"text": "Kaplan et al. (1995). Journal of Environmental Psychology."},
            {"text": "Ulrich (1984). Science, Vol. 224, pp. 420-421."},
        ],
    }
    profile = build_table_content_profile(table)
    assert profile["semantic_type"] == "references"
    assert profile["extractable"] is False


def test_profile_rejects_model_fit_table():
    table = {
        "table_id": "T3",
        "paper_id": "p3",
        "rows": [
            {"text": "Model fit indices: RMSEA = 0.05 CFI = 0.96 χ²/df = 1.9"},
            {"text": "AIC = 123.4 BIC = 131.2"},
        ],
    }
    profile = build_table_content_profile(table)
    assert profile["semantic_type"] == "model_fit"
    assert profile["extractable"] is False
