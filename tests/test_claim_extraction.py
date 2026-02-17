from src.cmr.claim_extraction import extract_claims_from_text, extract_claims_structured


def test_extract_claims_structured_normalizes_and_validates():
    claims = [
        {
            "independent_var": "Nature View",
            "dependent_var": "Recovery Time",
            "direction": "decrease",
            "effect_size": "0.42",
            "sample_n": "121",
            "context": "hospital",
        },
        {"iv": "Bad Row Only IV"},
    ]

    result = extract_claims_structured(claims)
    assert len(result) == 1
    claim = result[0]
    assert claim["iv"] == "Nature View"
    assert claim["dv"] == "Recovery Time"
    assert claim["direction"] == "negative"
    assert claim["effect_size"] == 0.42
    assert claim["sample_n"] == 121
    assert claim["source"] == "structured_input"
    assert claim["validation_warnings"] == []
    assert claim["duplicate_count"] == 1


def test_extract_claims_structured_warns_on_bad_inputs():
    claims = [
        {
            "iv": "Nature View",
            "dv": "Recovery Time",
            "direction": "sideways",
            "effect_size": 3.2,
            "sample_n": 8,
        }
    ]

    result = extract_claims_structured(claims)
    assert len(result) == 1
    warnings = set(result[0]["validation_warnings"])
    assert "invalid_direction" in warnings
    assert "effect_size_outlier" in warnings
    assert "small_sample_n" in warnings


def test_extract_claims_structured_dedupes_duplicates():
    claims = [
        {"iv": "Nature View", "dv": "Recovery Time", "direction": "decrease"},
        {"iv": "nature view", "dv": "recovery time", "direction": "decreases"},
    ]

    result = extract_claims_structured(claims)
    assert len(result) == 1
    assert result[0]["duplicate_count"] == 2
    assert "duplicate_claim" in result[0]["validation_warnings"]


def test_extract_claims_from_text_supports_base_verbs_and_inflections():
    text = "Nature views reduce stress. High ceilings enhances creativity. Daylight increase alertness."
    claims = extract_claims_from_text(text)

    assert len(claims) >= 3
    assert any(c["direction"] == "negative" and "stress" in c["dv"].lower() for c in claims)
    assert any(c["direction"] == "positive" and "creativity" in c["dv"].lower() for c in claims)
    assert any(c["direction"] == "positive" and "alertness" in c["dv"].lower() for c in claims)


def test_extract_claims_from_text_ulrich_like_sentence_maps_view_and_recovery():
    text = (
        "Patients with nature views had shorter recovery times and required less pain medication."
    )
    claims = extract_claims_from_text(text)
    assert len(claims) >= 2

    recovery_claim = next((c for c in claims if "recovery" in c["dv"].lower()), None)
    assert recovery_claim is not None
    assert recovery_claim["direction"] == "negative"
    assert recovery_claim["iv_mapping_status"] in {"mapped", "novel_variable"}
    assert recovery_claim["dv_mapping_status"] in {"mapped", "novel_variable"}
    assert 0.3 <= recovery_claim["confidence"] <= 0.95


def test_extract_claims_from_text_flags_novel_variables():
    text = "Telepathy index increases quantum feng-shui coherence."
    claims = extract_claims_from_text(text)
    assert len(claims) >= 1
    claim = claims[0]
    assert claim["iv_mapping_status"] == "novel_variable"
    assert claim["dv_mapping_status"] == "novel_variable"
