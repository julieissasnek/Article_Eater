from pathlib import Path

from scripts.run_realtime_table_rule_intake import evaluate_abstract_rule_gate
import scripts.process_realtime_pdf_completion_queue as rtq


class _FakeTable:
    def __init__(self, table_id: str = "t1", page_number: int = 2):
        self.table_id = table_id
        self.page_number = page_number


class _FakeClaim:
    def __init__(self):
        self.claim_id = "c1"
        self.claim_type = "effect"
        self.content = "Daylight improved attention."
        self.confidence = 0.81
        self.metadata = {}
        self.source_table_id = "t1"
        self.source_row = 1


class _FakeResult:
    def __init__(self):
        self.tables = [_FakeTable()]
        self.claims = [_FakeClaim()]
        self.errors = []


class _FakeIntegrator:
    def __init__(self, *args, **kwargs):
        pass

    def extract_and_convert(self, pdf_path, paper_id):
        return _FakeResult()


def test_evaluate_abstract_rule_gate_accepts_confident_empirical():
    gate = evaluate_abstract_rule_gate(
        "empirical_v2",
        {"confidence": 0.82, "margin": 0.45, "needs_review": False},
    )
    assert gate["eligible"] is True
    assert gate["policy"] == "emit_empirical_abstract_causal_rule"


def test_evaluate_abstract_rule_gate_defers_non_empirical_and_uncertain():
    non_emp = evaluate_abstract_rule_gate(
        "theoretical",
        {"confidence": 0.93, "margin": 0.80, "needs_review": False},
    )
    assert non_emp["eligible"] is False
    assert "family_not_empirical" in non_emp["reason"]

    uncertain = evaluate_abstract_rule_gate(
        "empirical_v2",
        {"confidence": 0.55, "margin": 0.20, "needs_review": True},
    )
    assert uncertain["eligible"] is False
    assert uncertain["policy"] == "defer_uncertain_type_abstract_causal_rule"


def test_process_single_row_propagates_article_type_uncertainty(monkeypatch, tmp_path):
    pdf = tmp_path / "paper.pdf"
    pdf.write_bytes(b"%PDF-1.4\n% fake\n")

    monkeypatch.setattr(rtq, "PipelineTableIntegrator", _FakeIntegrator)
    monkeypatch.setattr(rtq, "extract_discourse_rows", lambda **kwargs: ([], {"section_counts": {}}))
    monkeypatch.setattr(
        rtq,
        "resolve_env_outcome_from_claim",
        lambda content, meta, paper_id: {
            "environment_raw_term": "daylight",
            "outcome_raw_term": "attention",
            "environment_candidates": "daylight",
            "outcome_candidates": "attention",
            "environment_canonical_id": "env.daylight",
            "outcome_canonical_id": "out.attention",
            "environment_resolution_confidence": 0.9,
            "outcome_resolution_confidence": 0.9,
            "environment_resolution_match_type": "lookup",
            "outcome_resolution_match_type": "lookup",
            "environment_node_id": "env.daylight",
            "outcome_node_id": "out.attention",
        },
    )

    row = {"paper_id": "p1", "pdf_path": str(pdf)}
    res = rtq.process_single_row(
        row_index=0,
        row=row,
        queue_csv_path=tmp_path / "queue.csv",
        article_type_family="empirical_v2",
        article_type_needs_review=True,
    )

    assert res.status == "completed_pdf_extracted"
    assert len(res.confirmed_rows) == 1
    out = res.confirmed_rows[0]
    assert out["needs_verification"] == "true"
    assert out["article_type_needs_review"] == "true"
    assert "needs_article_type_verification" in out["quality_flag"]
