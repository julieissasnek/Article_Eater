from src.cmr.voi_scoring import aggregate_paper_voi, score_voi


def test_score_voi_applies_contract_rules():
    findings = [
        {"assessment": "contradiction", "template_maturity": "supported"},
        {"assessment": "contradiction", "template_maturity": "preliminary"},
        {"assessment": "gap", "effect_size": 0.9},
        {"assessment": "gap", "effect_size": 0.2},
        {"assessment": "extension"},
        {"assessment": "confirmation", "template_maturity": "supported"},
        {"assessment": "confirmation", "template_maturity": "preliminary"},
    ]

    scored = score_voi(findings)
    by_assessment = {
        (item["assessment"], item.get("template_maturity"), item.get("effect_size")): item["voi_score"]
        for item in scored
    }

    assert by_assessment[("contradiction", "supported", None)] == 1.0
    assert by_assessment[("contradiction", "preliminary", None)] == 0.7
    assert by_assessment[("gap", None, 0.9)] == 0.8
    assert by_assessment[("gap", None, 0.2)] == 0.4
    assert by_assessment[("extension", None, None)] == 0.6
    assert by_assessment[("confirmation", "supported", None)] == 0.2
    assert by_assessment[("confirmation", "preliminary", None)] == 0.5


def test_aggregate_paper_voi_returns_expected_summary():
    findings = [
        {"assessment": "contradiction", "template_maturity": "supported"},
        {"assessment": "gap", "effect_size": 0.8},
        {"assessment": "confirmation", "template_maturity": "supported"},
    ]
    aggregate = aggregate_paper_voi(findings)

    assert aggregate["n_findings"] == 3
    assert aggregate["high_value_findings"] == 2
    assert aggregate["expected_information_gain"] == "medium"
    assert 0.0 <= aggregate["aggregate_voi"] <= 1.0
