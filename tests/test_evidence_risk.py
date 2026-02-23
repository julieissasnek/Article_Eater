from src.extraction.evidence_risk import score_claim_risk


def test_score_claim_risk_flags_placeholder_and_same_raw():
    claim = {
        "claim_id": "c1",
        "paper_id": "p1",
        "iv": "stress",
        "dv": "stress",
        "iv_raw": "col_1: stress score",
        "dv_raw": "col_1: stress score",
        "direction": "increase",
        "source_quote": "col_1: stress score increased with condition A",
        "section": "results",
        "provenance_depth": "table",
    }
    out = score_claim_risk(claim)
    assert out["claim_risk_score"] >= 0.5
    assert "placeholder_raw_variable" in out["claim_risk_reasons"]
    assert "iv_raw_equals_dv_raw" in out["claim_risk_reasons"]


def test_score_claim_risk_marks_unknown_direction_as_risky():
    claim = {
        "claim_id": "c2",
        "paper_id": "p1",
        "article_type_family": "empirical_v2",
        "iv": "noise",
        "dv": "stress",
        "iv_raw": "noise exposure",
        "dv_raw": "cortisol",
        "direction": "unknown",
        "source_quote": "A significant association was observed.",
        "section": "discussion",
        "provenance_depth": "abstract",
    }
    out = score_claim_risk(claim)
    assert out["field_risk_scores"]["direction"] >= 0.5
    assert "unknown_direction" in out["field_risk_reasons"]["direction"]
    assert out["claim_risk_score"] >= 0.30


def test_score_claim_risk_low_for_grounded_directional_claim():
    claim = {
        "claim_id": "c3",
        "paper_id": "p2",
        "iv": "noise",
        "dv": "stress",
        "iv_raw": "noise level",
        "dv_raw": "cortisol concentration",
        "direction": "increase",
        "effect_size": 0.32,
        "effect_size_type": "r",
        "p_value": 0.01,
        "source_quote": "Higher noise levels were associated with increased cortisol (r = +0.32, p = 0.01).",
        "section": "results",
        "provenance_depth": "section",
    }
    out = score_claim_risk(claim)
    assert out["field_risk_scores"]["direction"] < 0.45
    assert out["claim_risk_score"] < 0.55
