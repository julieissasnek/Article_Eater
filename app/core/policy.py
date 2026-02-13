"""
Policy configuration for Article Eater.

Updated 2026-02-11: Renamed seven_panel to article_essence_extraction
"""

from __future__ import annotations
import json
import os
from pathlib import Path
from typing import Any, Dict

_POL = None


def load_policy(path: str | None = None) -> Dict[str, Any]:
    global _POL
    if _POL is not None:
        return _POL
    path = path or os.environ.get("AE_POLICY_JSON", "config/app.policy.json")
    p = Path(path)
    if not p.exists():
        _POL = {
            "llm_defaults": {
                "article_essence_extraction": {
                    "model": "gemini",
                    "temperature": 0.1,
                    "max_tokens": 8000
                },
                # Legacy alias for backward compatibility
                "seven_panel": {
                    "model": "gemini",
                    "temperature": 0.1,
                    "max_tokens": 8000
                },
                "triage": {
                    "model": "haiku",
                    "temperature": 0.0,
                    "max_tokens": 1024
                }
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


def model_for(task: str, is_admin: bool = False) -> Dict[str, Any]:
    """Get model configuration for a task.

    Args:
        task: Task name (e.g., "article_essence_extraction", "triage")
        is_admin: Whether to allow admin-level model access

    Returns:
        Model configuration dict with model, temperature, max_tokens
    """
    pol = load_policy()

    # Handle both new and legacy task names
    if task in ("article_essence_extraction", "seven_panel"):
        # Try new name first, fall back to legacy
        model = pol.get("llm_defaults", {}).get("article_essence_extraction", {})
        if not model:
            model = pol.get("llm_defaults", {}).get("seven_panel", {})
        if not pol.get("panels", {}).get("allow_fallback_for_admin", False) and not is_admin:
            return model
        return model

    return pol.get("llm_defaults", {}).get(task, {})
