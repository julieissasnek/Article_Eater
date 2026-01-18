
from __future__ import annotations
import json, os
from pathlib import Path
from typing import Any, Dict

_POL = None
def load_policy(path: str|None=None) -> Dict[str, Any]:
    global _POL
    if _POL is not None: return _POL
    path = path or os.environ.get("AE_POLICY_JSON","config/app.policy.json")
    p = Path(path)
    if not p.exists():
        _POL = {
            "llm_defaults": {
                "seven_panel": {"model": "gemini", "temperature": 0.1, "max_tokens": 8000},
                "triage": {"model": "haiku", "temperature": 0.0, "max_tokens": 1024}
            },
            "panels": {
                "eager_generate_on_view": True,
                "allow_fallback_for_admin": True
            },
            "cost": {
                "track_per_user": True,
                "warn_at_usd": 3.00,
                "hard_cap_usd": 5.00
            },
            "engine": {
                "use_mocks": False
            }
        }
        return _POL
    _POL = json.loads(p.read_text(encoding="utf-8"))
    return _POL

def model_for(task: str, is_admin: bool=False) -> Dict[str, Any]:
    pol = load_policy()
    if task == "seven_panel":
        model = pol.get("llm_defaults",{}).get("seven_panel",{})
        if not pol.get("panels",{}).get("allow_fallback_for_admin", False) and not is_admin:
            # force the configured model; disallow override
            return model
        return model
    return pol.get("llm_defaults",{}).get(task, {})