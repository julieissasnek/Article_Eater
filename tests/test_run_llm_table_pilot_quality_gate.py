"""Tests for quality-gating helpers in run_llm_table_pilot."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_mod():
    root = Path(__file__).resolve().parents[1]
    script = root / "scripts" / "run_llm_table_pilot.py"
    spec = importlib.util.spec_from_file_location("run_llm_table_pilot", script)
    assert spec is not None
    assert spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def test_claim_rejection_flags_placeholder_and_duplicate_raw():
    mod = _load_mod()
    claim = {
        "iv": "has_nature_view",
        "dv": "recovery_time",
        "iv_raw": "col_1: 0.31",
        "dv_raw": "col_1: 0.31",
        "source_quote": "col_1: 0.31 col_2: 0.39",
    }
    reasons = set(mod._claim_rejection_reasons(claim))
    assert "drop_placeholder_column_label" in reasons
    assert "drop_same_raw_iv_dv" in reasons


def test_claim_rejection_flags_unmapped_and_same_mapped():
    mod = _load_mod()
    claim1 = {
        "iv": None,
        "dv": "stress",
        "iv_raw": "window area",
        "dv_raw": "stress",
        "source_quote": "window area predicted stress",
    }
    reasons1 = set(mod._claim_rejection_reasons(claim1))
    assert "drop_unmapped_iv_or_dv" in reasons1

    claim2 = {
        "iv": "stress",
        "dv": "stress",
        "iv_raw": "stress index",
        "dv_raw": "stress score",
        "source_quote": "stress was linked to stress",
    }
    reasons2 = set(mod._claim_rejection_reasons(claim2))
    assert "drop_same_mapped_iv_dv" in reasons2


def test_run_profile_variant_records_error_message_and_traceback(monkeypatch):
    mod = _load_mod()

    class DummyAdapter:
        def __init__(self, provider: str, codex_timeout_sec: int = 90):
            self.provider = provider
            self.codex_timeout_sec = codex_timeout_sec

    class FailingExtractor:
        def __init__(self, api_client=None, model: str = ""):
            self.api_client = api_client
            self.model = model

        def extract_tables(self, pdf_path, pages=None):
            raise AttributeError("boom")

    monkeypatch.setattr(mod, "_ChatAdapter", DummyAdapter)
    monkeypatch.setattr(mod, "AITableExtractor", FailingExtractor)

    profile = mod.ModelProfile(name="t", provider="codex_exec", model="gpt-5.2-codex")
    out = mod._run_profile_variant(
        profile=profile,
        variant="no_gate",
        selected_pdfs=[{"paper_id": "p1", "pdf_path": __file__}],
        vocab={},
        max_pages=1,
        codex_timeout_sec=30,
    )

    assert out["counters"]["pdf_errors"] == 1
    assert len(out["table_records"]) == 1
    rec = out["table_records"][0]
    assert rec["error"] == "extract_tables_error:AttributeError"
    assert rec["error_message"] == "boom"
    assert "AttributeError: boom" in rec["traceback"]
