from src.cmr.paper_report import format_paper_report_text, generate_paper_report


def _sample_evaluation() -> dict:
    claim_a = {"description": "Nature views reduce stress.", "iv": "nature views", "dv": "stress"}
    claim_b = {"description": "High ceilings impair divergent thinking.", "iv": "high ceilings", "dv": "divergent thinking"}
    claim_c = {"description": "CO2 reduces decision making.", "iv": "co2_1000ppm", "dv": "decision_making"}
    return {
        "paper_summary": "Processed 3 claims from paper; 2 matched templates and 1 unmatched.",
        "n_claims_extracted": 3,
        "n_claims_matched": 2,
        "n_claims_unmatched": 1,
        "findings": [
            {
                "claim": claim_a,
                "assessment": "confirmation",
                "convergence": "moderate",
                "confidence": "high",
                "voi": "low",
            },
            {
                "claim": claim_b,
                "assessment": "contradiction",
                "convergence": "contradicted",
                "confidence": "high",
                "voi": "high",
            },
            {
                "claim": claim_c,
                "assessment": "gap",
                "convergence": "unsupported",
                "confidence": "medium",
                "voi": "medium",
            },
        ],
        "template_matches": [
            {"claim": claim_a, "matches": [{"template_id": "VIEW1"}]},
            {"claim": claim_b, "matches": [{"template_id": "VF3"}, {"template_id": "CREA2"}]},
            {"claim": claim_c, "matches": []},
        ],
        "template_system_updates": [
            {"type": "confirms", "template": "VIEW1", "detail": "Nature view claim confirms VIEW1."},
            {"type": "contradicts", "template": "VF3", "detail": "Ceiling claim contradicts VF3."},
            {"type": "gap", "template": "none", "detail": "No template matched CO2 claim."},
        ],
    }


def test_generate_paper_report_sections():
    report = generate_paper_report(_sample_evaluation())

    assert "summary" in report
    assert "claim_assessments" in report
    assert "high_voi_findings" in report
    assert "template_system_update_recommendations" in report
    assert "methodology_note" in report
    assert report["summary"]["claims_extracted"] == 3
    assert report["summary"]["claims_matched"] == 2
    assert report["summary"]["coverage_ratio"] == 0.667
    assert len(report["high_voi_findings"]) == 2


def test_format_paper_report_text_contains_key_sections():
    report = generate_paper_report(_sample_evaluation())
    text = format_paper_report_text(report)

    assert "PAPER EVALUATION REPORT" in text
    assert "Per-Claim Assessment:" in text
    assert "High-VOI Findings:" in text
    assert "Template Update Recommendations:" in text
    assert "Methodology:" in text
