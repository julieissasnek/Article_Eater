from src.cmr.report import format_report_text, generate_report


def test_generate_report_contains_all_required_sections():
    evaluation_result = {
        "overall_wis": 48.0,
        "overall_confidence": 0.62,
        "domain_scores": [
            {"domain": "L", "wis": 75.0, "confidence": 0.8, "n_templates": 2, "template_ids": ["L1", "L2"]},
            {"domain": "MAT", "wis": 28.0, "confidence": 0.4, "n_templates": 2, "template_ids": ["MAT1", "MAT2"]},
        ],
        "data_gaps": ["SOC3", "VIEW1"],
        "template_details": [
            {"template": "L1", "calibration_status": "substantial"},
            {"template": "L2", "calibration_status": "partial"},
            {"template": "MAT1", "calibration_status": "protocol"},
            {"template": "MAT2", "calibration_status": "uncalibrated"},
        ],
    }

    report = generate_report(evaluation_result)
    assert "summary" in report
    assert "strengths" in report
    assert "deficits" in report
    assert "data_gaps" in report
    assert "recommendations" in report
    assert "uncertainty_disclosure" in report
    assert "methodology_note" in report

    assert report["summary"]["overall_wis"] == 48.0
    assert any(item["domain"] == "L" for item in report["strengths"])
    assert any(item["domain"] == "MAT" for item in report["deficits"])
    assert report["data_gaps"] == ["SOC3", "VIEW1"]
    assert report["uncertainty_disclosure"]["empirically_calibrated_templates"] == 2
    assert report["uncertainty_disclosure"]["expert_estimate_templates"] == 2


def test_format_report_text_includes_plain_language_sections():
    report = generate_report(
        {
            "overall_wis": 80.0,
            "overall_confidence": 0.9,
            "domain_scores": [{"domain": "SC", "wis": 82.0, "confidence": 0.9, "n_templates": 1, "template_ids": ["SC1"]}],
            "data_gaps": [],
            "template_details": [{"template": "SC1", "calibration_status": "substantial"}],
        }
    )
    text = format_report_text(report)
    assert "CMR ASSESSMENT REPORT" in text
    assert "Overall WIS: 80.0" in text
    assert "Strengths:" in text
    assert "Deficits:" in text
    assert "Data Gaps:" in text
    assert "Recommendations:" in text
    assert "Uncertainty Disclosure:" in text
    assert "Methodology:" in text
