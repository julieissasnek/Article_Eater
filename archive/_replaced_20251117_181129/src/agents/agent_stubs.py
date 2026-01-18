"""
Powered agents (v20.6.3).
Replaces the previous print(...) placeholders with real LLM-backed implementations.
- Agent_Finder: extracts Seven-Panel items via LLM with JSON-schema validation.
- Agent_Aggregator: clusters findings into rule candidates via LLM (prompt_aggregator.md).
- Agent_Linker: proposes links across candidates via LLM (prompt_linker.md).
- BBN_Calibrator: delegates to src/agents/bbn_calibrator.py to produce a separate advisory artifact.
All prompts are loaded from /prompts; the Admin Control Room can edit them live.
"""
from __future__ import annotations
from pathlib import Path
from typing import Any, List, Dict, Optional

from src.agents.agent_core import call_llm, LLMConfig
from src.agents.json_utils import parse_and_validate
from src.contracts.schemas import SevenPanelArtifact, SevenPanelItem
from src.agents.bbn_calibrator import calibrate as _bbn_calibrate

PROMPTS_DIR = Path("prompts")

def _read_prompt(candidates: List[str]) -> str:
    for name in candidates:
        p = PROMPTS_DIR / name
        if p.exists():
            return p.read_text(encoding="utf-8", errors="ignore")
    return ""

def Agent_Finder(
    paper_text: str,
    abstract: Optional[str] = None,
    paper_type: str = "generic"
) -> SevenPanelArtifact:
    """
    Extract Seven-Panel findings from a paper using provider-agnostic LLM.
    - Selects prompt by paper_type if available, otherwise falls back to 7panel_pass2_findings.md.
    - Validates JSON against prompts/seven_panel_schema.json.
    - Returns a SevenPanelArtifact (with provider/model recorded).
    """
    cfg = LLMConfig()
    prompt = _read_prompt([f"prompt_{paper_type}.md", "7panel_pass2_findings.md"])
    assembled = f"""You are extracting a Seven-Panel findings array from an academic paper.

Abstract:
{abstract or ''}

Paper (may be truncated for cost):
{(paper_text or '')[:20000]}

Instructions:
{prompt}
"""
    raw = call_llm(assembled, cfg)       # <— REAL LLM CALL
    items = parse_and_validate(raw)      # <— JSON-SCHEMA VALIDATION
    # Ensure raw_abstract is present for each item if missing
    for i in items:
        i.setdefault("raw_abstract", abstract or None)
    sp_items = [SevenPanelItem(**i) for i in items]
    return SevenPanelArtifact(items=sp_items, provider=cfg.provider, model=cfg.model)

def Agent_Aggregator(seven_panel_items: List[Dict[str,Any]]) -> Dict[str,Any]:
    """
    Cluster seven-panel items into rule candidates and surface contradictions via LLM.
    Returns JSON (dict) as produced by the LLM (no hard-coded structure in code).
    """
    cfg = LLMConfig()
    prompt = _read_prompt(["prompt_aggregator.md"])
    payload = f"""You are the Aggregator. Here are validated Seven-Panel items (JSON):

{seven_panel_items}

Instructions:
{prompt}
"""
    raw = call_llm(payload, cfg)         # <— REAL LLM CALL
    # The admin may evolve the aggregator schema; we accept any valid JSON dict here.
    import json
    try:
        data = json.loads(raw)
    except Exception as e:
        raise ValueError(f"Aggregator returned non-JSON: {e}")
    if not isinstance(data, dict):
        raise ValueError("Aggregator output must be a JSON object.")
    return data

def Agent_Linker(rule_candidates: Dict[str,Any], seven_panel_items: List[Dict[str,Any]]) -> Dict[str,Any]:
    """
    Propose links (chaining, synergy, antagonism) across rule candidates using LLM.
    """
    cfg = LLMConfig()
    prompt = _read_prompt(["prompt_linker.md"])
    payload = f"""You are the Linker. Use rule candidates and seven-panel items.

Rule candidates (JSON):
{rule_candidates}

Seven-panel items (JSON):
{seven_panel_items}

Instructions:
{prompt}
"""
    raw = call_llm(payload, cfg)         # <— REAL LLM CALL
    import json
    try:
        data = json.loads(raw)
    except Exception as e:
        raise ValueError(f"Linker returned non-JSON: {e}")
    if not isinstance(data, dict):
        raise ValueError("Linker output must be a JSON object.")
    return data

def BBN_Calibrator(seven_panel_items: List[Dict[str,Any]]) -> Dict[str,Any]:
    """
    Delegates to the calibrator to compute an advisory calibration artifact.
    Does NOT mutate the primary BN inputs.
    """
    return _bbn_calibrate(seven_panel_items)