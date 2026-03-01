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
            "iv": "spatial_enclosure_ratio",
            "dv": "creative_network_dynamics",
            "direction": "decrease",
            "effect_size": 0.3,
            "description": "high ceilings reduce divergent thinking in tests",
        },
    ]


def test_evaluate_paper_pipeline_produces_report(tmp_path) -> None:
    db_path = str(tmp_path / "test_paper_eval.db")
    from src.cmr.template_scanner import scan_templates
    scan_templates(db_path=db_path)
    
    report = evaluate_paper(structured_claims=_sample_claims(), db_path=db_path)
    assert report["status"] == "complete"
    assert report["report"]["summary"]["status"] == "paper_pipeline_complete"
    assert report["n_claims_extracted"] == 2
    assert report["n_claims_matched"] >= 1
    assert report["findings"]
    assert report["template_system_updates"]


def test_prioritized_findings_have_voi_scores(tmp_path) -> None:
    db_path = str(tmp_path / "test_paper_eval.db")
    from src.cmr.template_scanner import scan_templates
    scan_templates(db_path=db_path)
    
    report = evaluate_paper(structured_claims=_sample_claims(), db_path=db_path)
    assert report["prioritized_findings"]
    for finding in report["prioritized_findings"]:
        score = float(finding["voi_score"])
        assert -1.0e-6 <= score <= 100.0
        assert finding["voi_bucket"] in {"high", "medium", "low"}
