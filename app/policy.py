from __future__ import annotations
import json
from pathlib import Path
from functools import lru_cache

DEFAULT_POLICY = {
    "preferred_providers": ["gemini","openai","anthropic"],
    "eager": {
        "metadata": True,
        "rule_candidacy": True,
        "seven_panel": True,
        "require_llm_for_panels": True,
        "non_admin_fallback_allowed": False
    }
}

@lru_cache(maxsize=1)
def get_policy() -> dict:
    root = Path(__file__).resolve().parents[1]
    p = root / "config" / "app.policy.json"
    if not p.exists():
        return DEFAULT_POLICY
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        merged = DEFAULT_POLICY.copy()
        merged.update(data or {})
        if "eager" in data:
            e = merged["eager"].copy()
            e.update(data["eager"] or {})
            merged["eager"] = e
        return merged
    except Exception:
        return DEFAULT_POLICY