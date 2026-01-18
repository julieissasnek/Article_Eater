"""Seven-Panel v2 extraction agent.

This module introduces a richer Seven-Panel staging format that is
explicitly subject-aware and BN-friendly. It does **not** change the
behaviour of the classic SevenPanelArtifact / Agent_Finder pipeline;
instead, it provides a parallel path that callers can opt into.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional, Dict, Any

import json
from jsonschema import validate, ValidationError

from src.agents.agent_core import LLMConfig, call_llm
from src.contracts.schemas import (
    SevenPanelV2Bundle,
    PanelSubjects,
    PanelContext,
    PanelMeasures,
    PanelFindingsV2,
    PanelHeterogeneity,
    PanelMechanisms,
    PanelLimits,
)

PROMPTS_DIR = Path("prompts")
SCHEMAS_DIR = Path("schemas")


_PANEL_SCHEMA_FILES: Dict[str, str] = {
    "panel_subjects": "panel_subjects.schema.json",
    "panel_context": "panel_context.schema.json",
    "panel_measures": "panel_measures.schema.json",
    "panel_findings": "panel_findings_v2.schema.json",
    "panel_heterogeneity": "panel_heterogeneity.schema.json",
    "panel_mechanisms": "panel_mechanisms.schema.json",
    "panel_limits": "panel_limits.schema.json",
}


def _load_prompt(name: str = "seven_panel_v2_master.md") -> str:
    p = PROMPTS_DIR / name
    if not p.exists():
        return ""
    return p.read_text(encoding="utf-8", errors="ignore")


def _load_schema(name: str) -> Dict[str, Any]:
    path = SCHEMAS_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"Missing JSON schema {name} in {SCHEMAS_DIR}")
    return json.loads(path.read_text(encoding="utf-8"))


def _validate_panel(kind: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    schema_name = _PANEL_SCHEMA_FILES.get(kind)
    if not schema_name:
        return payload
    schema = _load_schema(schema_name)
    try:
        validate(payload, schema)
    except ValidationError as exc:
        raise ValueError(f"{kind} validation failed: {exc.message}") from exc
    return payload


def extract_seven_panel_v2(
    pdf_text: str,
    abstract: Optional[str],
    paper_id: Optional[str] = None,
) -> SevenPanelV2Bundle:
    """Run a single LLM pass to extract Seven-Panel v2 panels.

    The LLM is instructed (via seven_panel_v2_master.md) to return a single
    JSON object of the form:

    {
      "panel_subjects": {...} | null,
      "panel_context": {...} | null,
      "panel_measures": {...} | null,
      "panel_findings": {...} | null,
      "panel_heterogeneity": {...} | null,
      "panel_mechanisms": {...} | null,
      "panel_limits": {...} | null
    }

    Each non-null panel is validated against its dedicated JSON schema in
    schemas/panel_*.schema.json and then mapped into a Pydantic model.
    """
    cfg = LLMConfig()
    inst = _load_prompt("seven_panel_v2_master.md")
    assembled = f"""You are extracting the Seven-Panel v2 representation of an academic paper.

Paper ID (may be synthetic):
{paper_id or ""}

Abstract:
{abstract or ""}

PDF (may be truncated for cost):
{(pdf_text or "")[:20000]}

Instructions:
{inst}
"""
    raw = call_llm(assembled, cfg)  # REAL LLM CALL

    try:
        data = json.loads(raw)
    except Exception as exc:
        raise ValueError(f"Seven-Panel v2 LLM returned non-JSON: {exc}") from exc

    if not isinstance(data, dict):
        raise ValueError("Seven-Panel v2 output must be a JSON object.")

    # Validate and map each panel, but tolerate missing keys gracefully.
    subjects = None
    context = None
    measures = None
    findings = None
    heterogeneity = None
    mechanisms = None
    limits = None

    if data.get("panel_subjects") is not None:
        payload = _validate_panel("panel_subjects", data["panel_subjects"])
        subjects = PanelSubjects(**payload)

    if data.get("panel_context") is not None:
        payload = _validate_panel("panel_context", data["panel_context"])
        context = PanelContext(**payload)

    if data.get("panel_measures") is not None:
        payload = _validate_panel("panel_measures", data["panel_measures"])
        measures = PanelMeasures(**payload)

    if data.get("panel_findings") is not None:
        payload = _validate_panel("panel_findings", data["panel_findings"])
        findings = PanelFindingsV2(**payload)

    if data.get("panel_heterogeneity") is not None:
        payload = _validate_panel("panel_heterogeneity", data["panel_heterogeneity"])
        heterogeneity = PanelHeterogeneity(**payload)

    if data.get("panel_mechanisms") is not None:
        payload = _validate_panel("panel_mechanisms", data["panel_mechanisms"])
        mechanisms = PanelMechanisms(**payload)

    if data.get("panel_limits") is not None:
        payload = _validate_panel("panel_limits", data["panel_limits"])
        limits = PanelLimits(**payload)

    bundle = SevenPanelV2Bundle(
        subjects=subjects,
        context=context,
        measures=measures,
        findings=findings,
        heterogeneity=heterogeneity,
        mechanisms=mechanisms,
        limits=limits,
        provider=cfg.provider,
        model=cfg.model,
        cost_usd=None,  # cost accounting is handled at a higher level
    )
    return bundle
