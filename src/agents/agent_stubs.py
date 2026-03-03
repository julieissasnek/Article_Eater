
"""High-level agent entry points for Article Eater.

These agents are the thin, provider-agnostic layer that:
- Build prompts from file-backed templates.
- Call the generic LLM core.
- Validate and map JSON into strongly typed schemas.
- (Now) persist key artefacts to the JSONL graph store and emit
  per-finding confidence artefacts, without changing the BN itself.

This module is the canonical place for "how humans talk to the engine".
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional
import json
import logging
import uuid

from src.agents.agent_core import LLMConfig, call_llm
from src.agents.json_utils import parse_and_validate
from src.contracts.schemas import SevenPanelArtifact, SevenPanelItem

# New: persistence + per-finding confidence
from src.services.service_locator import get_graph_service
from src.services.bbn_calibrator import compute_confidence_for_finding

from src.agents.agent_panels_v2 import extract_seven_panel_v2
from src.services.rulegraph_v2_builder import build_rulegraph_v2_rules

LOGGER = logging.getLogger(__name__)

PROMPTS_DIR = Path("prompts")


def _read_prompt(candidates: List[str]) -> str:
    """Return the first existing prompt file from candidates.

    This keeps prompt selection entirely file-backed so the Admin UI
    can switch behaviour without touching code.
    """
    for name in candidates:
        candidate_path = PROMPTS_DIR / name
        if candidate_path.exists():
            return candidate_path.read_text(encoding="utf-8")
    # Fallback: empty instructions – the LLM will still see system-level guardrails.
    return ""


def _persist_seven_panel_and_findings(
    artifact: SevenPanelArtifact,
    abstract: Optional[str],
    paper_id: Optional[str],
) -> None:
    """Persist Seven-Panel artefact and individual findings to the graph store.

    - If paper_id is None, a synthetic ID is generated.
    - Each SevenPanelItem is stored as a 'finding' event.
    - For each stored finding we attempt to compute a confidence score
      using src.services.bbn_calibrator; failures are logged but do not
      break the main Agent flow.
    """
    try:
        store = get_graph_service()
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.warning("Graph service unavailable in Agent_Finder: %s", exc)
        return

    pid = paper_id or f"paper_{uuid.uuid4().hex}"

    try:
        store.attach_seven_panel(pid, artifact.model_dump(), raw_abstract=abstract or None)
    except Exception as exc:
        LOGGER.warning("Failed to attach SevenPanel for %s: %s", pid, exc)

    for item in artifact.items:
        try:
            finding_dict = item.model_dump()
            finding_id = store.create_finding(pid, finding_dict)
        except Exception as exc:
            LOGGER.warning("Failed to store finding for %s: %s", pid, exc)
            continue

        # Derive simple stats for confidence; fall back gracefully if absent.
        stats = {}
        # Stats is nested under item.statistics in the schema.
        stats_obj = getattr(item, "statistics", None)
        if stats_obj is not None:
            try:
                stats = {
                    "sample_size": getattr(stats_obj, "sample_size", None),
                    "p_value": getattr(stats_obj, "p_value", None),
                    "effect_size": getattr(stats_obj, "effect_size", None),
                }
            except Exception:
                stats = {}

        try:
            compute_confidence_for_finding(finding_id, stats)
        except Exception as exc:
            LOGGER.warning(
                "Confidence computation failed for finding %s: %s", finding_id, exc
            )


def Agent_Finder(
    paper_text: str,
    abstract: Optional[str] = None,
    paper_type: str = "generic",
    paper_id: Optional[str] = None,
) -> SevenPanelArtifact:
    """Extract Seven-Panel findings from a paper using provider-agnostic LLM.

    Behaviour:
    - Select prompt by paper_type if available, otherwise fall back to
      7panel_pass2_findings.md.
    - Validate JSON against prompts/seven_panel_schema.json.
    - Return a SevenPanelArtifact (provider/model recorded).
    - Persist the Seven-Panel artefact and each finding to the JSONL graph
      store, and emit a per-finding confidence artefact.

    NOTE:
    - The paper_id parameter is optional and purely for persistence.
      If omitted, a synthetic ID is generated. Existing callers that
      pass (paper_text, abstract) continue to work unchanged.
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
    raw = call_llm(assembled, cfg)       # REAL LLM CALL
    items = parse_and_validate(raw)      # JSON-SCHEMA VALIDATION

    # Ensure raw_abstract is present for each item if missing
    for i in items:
        i.setdefault("raw_abstract", abstract or None)

    sp_items = [SevenPanelItem(**i) for i in items]
    artifact = SevenPanelArtifact(items=sp_items, provider=cfg.provider, model=cfg.model)

    # Persistence + per-finding confidence (best-effort, non-fatal)
    _persist_seven_panel_and_findings(artifact, abstract, paper_id)

    return artifact


def Agent_Aggregator(seven_panel_items: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Cluster Seven-Panel items into rule candidates and surface contradictions via LLM.

    Aggregator is intentionally schema-light. The exact JSON shape is
    governed by prompt_aggregator.md so the Admin UI can evolve it over time.

    In addition to returning the LLM JSON as a Python dict, we also record
    an 'aggregation' event in the JSONL graph store under a generic topic.
    """
    cfg = LLMConfig()
    prompt = _read_prompt(["prompt_aggregator.md"])
    payload = f"""You are the Aggregator. Here are validated Seven-Panel items (JSON):

{seven_panel_items}

Instructions:
{prompt}
"""
    raw = call_llm(payload, cfg)         # REAL LLM CALL

    try:
        data = json.loads(raw)
    except Exception as exc:
        raise ValueError(f"Aggregator returned non-JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("Aggregator output must be a JSON object.")

    # Best-effort persistence of aggregation payload
    try:
        store = get_graph_service()
        store.apply_aggregation(topic="AGGREGATION", payload=data)
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.warning("Failed to persist aggregation event: %s", exc)

    return data


def Agent_Linker(
    rule_candidates: Dict[str, Any],
    seven_panel_items: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Propose links (chaining, synergy, antagonism) across rule candidates using LLM.

    The Linker operates on rule_candidates (typically produced by the
    Aggregator) and Seven-Panel items. The prompt controls the exact JSON
    schema for links.

    We also record a 'links' event in the JSONL graph store under a
    generic topic, so later tooling can inspect or replay the linking
    decisions without relying on the LLM again.
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
    raw = call_llm(payload, cfg)         # REAL LLM CALL

    try:
        data = json.loads(raw)
    except Exception as exc:
        raise ValueError(f"Linker returned non-JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("Linker output must be a JSON object.")

    # Best-effort persistence of link payload
    try:
        store = get_graph_service()
        store.apply_links(topic="LINKS", payload=data)
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.warning("Failed to persist links event: %s", exc)

    return data

def Agent_Finder_v2(
    paper_text: str,
    abstract: Optional[str] = None,
    paper_type: str = "generic",
    paper_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Subject-aware Seven-Panel v2 finder + RuleGraph v2 builder.

    This is a thin convenience wrapper that:
    - delegates to Agent_Finder for the classic SevenPanelArtifact flow
      (including persistence + confidence),
    - runs Seven-Panel v2 extraction on the same paper,
    - builds RuleGraph v2 rules with explicit subject_scope and
      subject_moderators,
    - persists the v2 rules as a single 'rulegraph_v2' event in the
      JSONL graph store.

    It returns a dict that bundles the classic and v2 artefacts.
    """
    # Ensure we have a stable paper_id for persistence.
    if paper_id is None:
        paper_id = f"AUTO_{uuid.uuid4()}"

    # 1) Classic Seven-Panel flow (side effects included)
    seven_panel = Agent_Finder(
        paper_text=paper_text,
        abstract=abstract,
        paper_type=paper_type,
        paper_id=paper_id,
    )

    # 2) Seven-Panel v2 extraction
    bundle = extract_seven_panel_v2(
        pdf_text=paper_text,
        abstract=abstract,
        paper_id=paper_id,
    )

    # 3) RuleGraph v2 rules + persistence
    rules = build_rulegraph_v2_rules(paper_id=paper_id, bundle=bundle)
    if rules:
        try:
            store = get_graph_service()
            store.apply_rulegraph_v2(paper_id=paper_id, rules=[r for r in rules])
        except Exception as exc:  # pragma: no cover - defensive
            LOGGER.warning("Failed to persist RuleGraph v2 rules: %s", exc)

    return {
        "paper_id": paper_id,
        "seven_panel": seven_panel,
        "panels_v2": bundle,
        "rules_v2": rules,
    }

