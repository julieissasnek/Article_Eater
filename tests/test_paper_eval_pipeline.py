from __future__ import annotations

from src.cmr.paper_eval import evaluate_paper


def _sample_claims() -> list[dict]:
    return [
        {
            "iv": "nature_view",
            "dv": "recovery_time",
            "direction": "decrease",
            "effect_size": 0.5,
            "description": "patients with nature views recover faster",
        },
        {
            "iv": "ceiling_height",
            "dv": "divergent_thinking",
            "direction": "decrease",
            "effect_size": 0.3,
            "description": "high ceilings reduce divergent thinking in tests",
        },
    ]


def test_evaluate_paper_pipeline_produces_report() -> None:
    report = evaluate_paper(structured_claims=_sample_claims(), db_path="ae.db")
    assert report["status"] == "complete"
    assert report["report"]["summary"]["status"] == "paper_pipeline_complete"
    assert report["n_claims_extracted"] == 2
    assert report["n_claims_matched"] >= 1
    assert report["findings"]
    assert report["template_system_updates"]


def test_prioritized_findings_have_voi_scores() -> None:
    report = evaluate_paper(structured_claims=_sample_claims(), db_path="ae.db")
    assert report["prioritized_findings"]
    for finding in report["prioritized_findings"]:
        score = float(finding["voi_score"])
        assert -1.0e-6 <= score <= 100.0
        assert finding["voi_bucket"] in {"high", "medium", "low"}
