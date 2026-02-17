from src.cmr.mechanism_tracing import extract_direction, trace_claim, trace_mechanisms


def test_extract_direction_detects_positive_and_negative():
    assert extract_direction("nature view improves restoration") == "positive"
    assert extract_direction("harsh glare decreases comfort") == "negative"


def test_trace_claim_detects_supported_and_contradicted():
    claim = {
        "description": "Nature view reduces stress.",
        "iv": "nature_view",
        "dv": "stress_reduction",
    }
    template_data_supported = {
        "causal_links": [
            {
                "from_variable": "nature_view",
                "to_variable": "stress_reduction",
                "activity": "reduces stress",
            }
        ]
    }
    template_data_contradicted = {
        "causal_links": [
            {
                "from_variable": "nature_view",
                "to_variable": "stress_reduction",
                "activity": "increases stress",
            }
        ]
    }

    assert trace_claim(claim, template_data_supported)["status"] == "supported"
    assert trace_claim(claim, template_data_contradicted)["status"] == "contradicted"


def test_trace_mechanisms_applies_substitute_vary_mod_and_block():
    matches = [
        {
            "claim": {
                "claim_id": "c1",
                "iv": "nature_view",
                "dv": "stress_reduction",
                "population": "elderly",
                "context": "hospital",
            },
            "matches": [
                {
                    "template_id": "VIEW1",
                    "match_type": "exact",
                    "match_score": 0.91,
                    "template_data": {
                        "lifespan_moderation": {"population": ["elderly", "adult"]},
                        "scope_conditions": {"context": ["hospital"]},
                        "causal_links": [
                            {
                                "from_variable": "nature_view",
                                "to_variable": "stress_reduction",
                            }
                        ],
                    },
                },
                {
                    "template_id": "T6",
                    "match_type": "partial_iv",
                    "match_score": 0.61,
                    "template_data": {
                        "causal_links": [
                            {
                                "from_variable": "nature_view",
                                "to_variable": "cortisol",
                            }
                        ]
                    },
                },
            ],
        }
    ]

    traced = trace_mechanisms(matches)
    assert len(traced) == 2

    view1 = next(item for item in traced if item["template"] == "VIEW1")
    assert "T6" in view1["substitute_alternatives"]
    assert view1["moderator_match"] in {"full", "partial"}
    assert "If" in view1["block_assessment"]


def test_trace_mechanisms_flags_moderator_mismatch():
    matches = [
        {
            "claim": {
                "claim_id": "c2",
                "iv": "daylight",
                "dv": "alertness",
                "context": "classroom",
            },
            "matches": [
                {
                    "template_id": "L1",
                    "match_type": "exact",
                    "match_score": 0.8,
                    "template_data": {
                        "scope_conditions": {"context": ["hospital"]},
                        "causal_links": [
                            {
                                "from_variable": "illuminance",
                                "to_variable": "alertness",
                            }
                        ],
                    },
                }
            ],
        }
    ]

    traced = trace_mechanisms(matches)
    assert traced[0]["moderator_match"] == "mismatch"
    assert traced[0]["overall_confidence"] in {"moderate", "low"}
