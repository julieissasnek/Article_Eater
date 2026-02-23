from src.extraction.direction_expectation import direction_expected_for_claim


def test_direction_not_required_for_non_empirical_family():
    claim = {
        "article_type_family": "theoretical",
        "claim_type": "associational",
        "claim_source": "abstract",
        "source_quote": "This paper proposes a conceptual model.",
    }
    expected, reason = direction_expected_for_claim(claim)
    assert expected is False
    assert reason == "non_empirical_family"


def test_direction_not_required_for_abstract_aim_statement():
    claim = {
        "article_type_family": "empirical_v2",
        "claim_type": "associational",
        "claim_source": "abstract",
        "source_quote": "The aim of this study was to investigate the relationship between noise and stress.",
    }
    expected, reason = direction_expected_for_claim(claim)
    assert expected is False
    assert reason == "abstract_aim_statement"


def test_direction_expected_for_empirical_result_claim():
    claim = {
        "article_type_family": "empirical_v2",
        "claim_type": "associational",
        "claim_source": "abstract",
        "source_quote": "Noise significantly increased stress (p < .01).",
    }
    expected, reason = direction_expected_for_claim(claim)
    assert expected is True
    assert reason == "expected_empirical_claim"
