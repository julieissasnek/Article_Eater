
from __future__ import annotations
import json
import os
from pathlib import Path
from .llm import LLMClient
from app.core.policy import model_for

def _parse_findings_output(out: str) -> list[dict]:
    """Parse LLM output into a list of findings without throwing."""
    out = out.strip()
    if out.startswith("```"):
        out = out.split("```", 2)[1]
    try:
        data = json.loads(out)
    except Exception:
        return []
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        return data.get("findings", [])
    return []


def extract_findings_from_text(text: str, topic: str, is_admin: bool=False) -> list[dict]:
    client = LLMClient()
    cfg = model_for("seven_panel", is_admin=is_admin)
    sys = Path("prompts/SEVEN_PANEL_pass2_findings.md").read_text(encoding="utf-8").replace("{TARGET_TOPIC}", topic)
    user = text[:200000]  # cap
    env_model = os.environ.get("AE_LLM_MODEL")
    if not env_model and os.environ.get("OLLAMA_MODEL"):
        env_model = f"ollama:{os.environ.get('OLLAMA_MODEL')}"
    model = env_model or cfg.get("model", "gemini-1.5-pro")
    if model.startswith("ollama:"):
        out = client.complete_ollama(model=model.split(":", 1)[1], system=sys, user=user, temperature=cfg.get("temperature",0.1), max_tokens=cfg.get("max_tokens",8000))
    elif "gemini" in model:
        out = client.complete_gemini(model=model, system=sys, user=user, temperature=cfg.get("temperature",0.1), max_tokens=cfg.get("max_tokens",8000))
    else:
        out = client.complete_openai(model=model, system=sys, user=user, temperature=cfg.get("temperature",0.1), max_tokens=cfg.get("max_tokens",8000))
    return _parse_findings_output(out)
