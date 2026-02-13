"""
Article Essence Extraction Service
==================================

Extracts structured essential information from scientific articles.
Replaces the legacy "seven_panel" naming (2026-02-11).

Supports multiple extraction templates based on article type:
- Empirical studies
- Meta-analyses
- Systematic reviews
- Theoretical papers
- Case studies
- And 10+ more types (see docs/EXTRACTION_TEMPLATE_*.md)
"""

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


def extract_findings_from_text(text: str, topic: str, is_admin: bool = False) -> list[dict]:
    """
    Extract structured findings from article text.

    Args:
        text: Full text or abstract of the article
        topic: Target topic for extraction (e.g., "neuroarchitecture")
        is_admin: Whether to use admin-level model access

    Returns:
        List of finding dictionaries with:
        - finding_text
        - antecedents
        - consequent
        - measure_direction
        - statistics
        - quote
        - page_span
    """
    client = LLMClient()
    cfg = model_for("article_essence_extraction", is_admin=is_admin)

    # Load extraction prompt
    prompt_path = Path("prompts/ARTICLE_ESSENCE_findings.md")
    if not prompt_path.exists():
        # Fallback to legacy prompt during transition
        prompt_path = Path("prompts/SEVEN_PANEL_pass2_findings.md")

    sys = prompt_path.read_text(encoding="utf-8").replace("{TARGET_TOPIC}", topic)
    user = text[:200000]  # cap to avoid token limits

    # Model selection
    env_model = os.environ.get("AE_LLM_MODEL")
    if not env_model and os.environ.get("OLLAMA_MODEL"):
        env_model = f"ollama:{os.environ.get('OLLAMA_MODEL')}"
    model = env_model or cfg.get("model", "gemini-1.5-pro")

    # Execute extraction
    if model.startswith("ollama:"):
        out = client.complete_ollama(
            model=model.split(":", 1)[1],
            system=sys,
            user=user,
            temperature=cfg.get("temperature", 0.1),
            max_tokens=cfg.get("max_tokens", 8000)
        )
    elif "gemini" in model:
        out = client.complete_gemini(
            model=model,
            system=sys,
            user=user,
            temperature=cfg.get("temperature", 0.1),
            max_tokens=cfg.get("max_tokens", 8000)
        )
    else:
        out = client.complete_openai(
            model=model,
            system=sys,
            user=user,
            temperature=cfg.get("temperature", 0.1),
            max_tokens=cfg.get("max_tokens", 8000)
        )

    return _parse_findings_output(out)


# Legacy alias for backward compatibility during transition
# TODO: Remove after all callers updated (REMOVE_BY: 2026-03-11)
extract_seven_panel = extract_findings_from_text
