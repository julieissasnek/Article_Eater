from src.cmr.architect_report import format_architect_report_text, generate_architect_report


def _sample_evaluation() -> dict:
    return {
        "overall_wis": 62.4,
        "domain_scores": [
            {"domain": "VIEW", "wis": 78.0},
            {"domain": "L", "wis": 71.5},
            {"domain": "SC", "wis": 63.0},
            {"domain": "SOC", "wis": 44.0},
            {"domain": "MAT", "wis": 41.0},
        ],
        "data_gaps": ["ambient_noise_dba", "rt60_seconds"],
    }


def test_generate_architect_report_has_required_sections():
    report = generate_architect_report(_sample_evaluation())
    assert "building_wellness_score" in report
    assert "whats_working" in report
    assert "what_needs_attention" in report
    assert "quick_wins_under_1000" in report
    assert "design_changes" in report
    assert "what_we_couldnt_assess" in report
    assert "methodology_note" in report
    assert report["building_wellness_score"]["score"] == 62.4
    assert report["building_wellness_score"]["color"] in {"green", "yellow", "orange", "red"}


def test_generate_architect_report_uses_plain_language_not_template_ids():
    report = generate_architect_report(_sample_evaluation())
    text = " ".join(
        report["whats_working"]
        + report["what_needs_attention"]
        + report["quick_wins_under_1000"]
        + report["design_changes"]
    ).upper()
    # Ensure no internal template identifiers leak.
    assert "VF3" not in text
    assert "VIEW1" not in text
    assert "SOC2" not in text
    assert "TEMPLATE ID" not in text


def test_format_architect_report_text_sections():
    report = generate_architect_report(_sample_evaluation())
    rendered = format_architect_report_text(report)
    assert "ARCHITECT REPORT" in rendered
    assert "What's Working:" in rendered
    assert "Quick Wins (under $1000):" in rendered
    assert "Methodology Note:" in rendered
