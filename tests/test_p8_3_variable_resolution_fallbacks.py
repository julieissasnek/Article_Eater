import importlib.util
import sys
from pathlib import Path


def _load_intake_module():
    path = Path("scripts/run_realtime_table_rule_intake.py")
    spec = importlib.util.spec_from_file_location("run_realtime_table_rule_intake", str(path))
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_semantic_lookup_fallback_maps_close_term():
    mod = _load_intake_module()
    lookup = {
        "daylight exposure": "env.natural.daylight",
        "sustained attention": "cog.attention.sustained",
    }
    result = mod.semantic_lookup_fallback(
        raw_term="daylight expo",
        context_text="daylight exposure in classrooms improved outcomes",
        lookup_map=lookup,
        min_score=0.6,
    )
    assert result["canonical_id"] == "env.natural.daylight"
    assert result["confidence"] > 0.0


def test_resolve_outcome_factor_uses_semantic_fallback(monkeypatch):
    mod = _load_intake_module()

    monkeypatch.setattr(mod, "OUTCOME_LOOKUP_MAP", {"sustained attention": "cog.attention.sustained"})
    monkeypatch.setattr(mod, "resolve_outcome", None)
    monkeypatch.setattr(mod, "resolve_or_queue", None)
    monkeypatch.setattr(mod, "queue_unknown_outcome", None)

    result = mod.resolve_outcome_factor(
        raw_term="sustained attentn",
        paper_id="paper:test:1",
        context_text="students showed sustained attention benefits",
    )
    assert result["resolved"] is True
    assert result["match_type"] == "semantic_lookup_fallback"
    assert result["canonical_id"] == "cog.attention.sustained"
