from src.cmr.convergence import assess_convergence, check_composition_failures


def test_assess_convergence_handles_nested_trace_entries():
    traced_claims = [
        {
            "claim": {"claim_id": "c_strong"},
            "traced_templates": [
                {"template_id": "VIEW1", "status": "supported"},
                {"template_id": "T6", "status": "supported"},
                {"template_id": "SOC1", "status": "supported"},
            ],
        },
        {
            "claim": {"claim_id": "c_contradicted"},
            "traced_templates": [
                {"template_id": "CREA2", "status": "contradicted"},
                {"template_id": "VIEW1", "status": "supported"},
            ],
        },
        {
            "claim": {"claim_id": "c_unsupported"},
            "traced_templates": [],
        },
    ]

    results = assess_convergence(traced_claims)
    by_id = {row["claim"]["claim_id"]: row["convergence"]["status"] for row in results}

    assert by_id["c_strong"] == "strong"
    assert by_id["c_contradicted"] == "contradicted"
    assert by_id["c_unsupported"] == "unsupported"


def test_assess_convergence_accepts_flat_mechanism_trace_output():
    flat = [
        {"claim": {"claim_id": "flat1"}, "template": "VIEW1", "status": "supported"},
        {"claim": {"claim_id": "flat1"}, "template": "T6", "status": "supported"},
        {"claim": {"claim_id": "flat2"}, "template": "CREA2", "status": "contradicted"},
    ]

    results = assess_convergence(flat)
    by_id = {row["claim"]["claim_id"]: row["convergence"]["status"] for row in results}

    assert by_id["flat1"] == "moderate"
    assert by_id["flat2"] == "contradicted"


def test_check_composition_failures_warns_for_known_interactions():
    traced_claims = [
        {
            "claim": {"claim_id": "comp1"},
            "traced_templates": [
                {"template_id": "A", "status": "supported"},
                {"template_id": "C", "status": "supported"},
            ],
        }
    ]

    converged = assess_convergence(traced_claims)
    checked = check_composition_failures(converged)

    analysis = checked[0]["composition_analysis"]
    assert analysis["status"] == "warning"
    warning_types = {item["type"] for item in analysis["warnings"]}
    assert "sub_additivity" in warning_types
    assert "interference" in warning_types


def test_check_composition_failures_auto_runs_convergence_for_flat_input():
    flat = [
        {"claim": {"claim_id": "flat3"}, "template": "VIEW1", "status": "supported"},
        {"claim": {"claim_id": "flat3"}, "template": "T6", "status": "supported"},
    ]

    checked = check_composition_failures(flat)
    assert checked[0]["convergence"]["status"] == "moderate"
    assert checked[0]["composition_analysis"]["status"] in {"clean", "warning"}
