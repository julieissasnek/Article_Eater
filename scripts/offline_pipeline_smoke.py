#!/usr/bin/env python3
"""Offline pipeline smoke test for Article Eater v20.7.3.

This script DOES NOT call any real LLM provider. Instead, it monkey-patches
the agent-level `call_llm` function to return small, schema-valid JSON
payloads and then exercises:

- Agent_Finder  -> Seven-Panel extraction + persistence + confidence
- Agent_Aggregator -> aggregation event
- Agent_Linker -> links event

It asserts that:
- data/graph.jsonl contains at least one finding, aggregation, and links event
- data/calibration/ contains at least one per-finding JSON artefact

If anything fails, the script exits with a non-zero status.
"""
from __future__ import annotations

import json
import sys
import pathlib
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[1]


def _install_root() -> None:
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))


def fake_call_llm(prompt: str, cfg: Any) -> str:
    """Return canned JSON based on the prompt content.

    We prioritise Aggregator/Linker branches because their templates may
    mention "Seven-Panel findings" in the instructions.
    """
    if "You are the Aggregator" in prompt:
        return json.dumps(
            {
                "groups": [
                    {
                        "summary": "Smoke test group: all findings about biophilic ceilings.",
                        "finding_ids": ["FINDING_SMOKE_1"],
                    }
                ]
            }
        )
    if "You are the Linker" in prompt:
        return json.dumps(
            {
                "links": [
                    {
                        "from": "Biophilic ceilings",
                        "to": "Reduced stress",
                        "relation": "supports",
                        "evidence_ids": ["FINDING_SMOKE_1"],
                    }
                ]
            }
        )
    if "Seven-Panel findings array" in prompt or "Seven-Panel findings" in prompt:
        data = [
            {
                "finding_text": "Dummy finding: biophilic ceiling reduces reported stress.",
                "statistics": {
                    "p_value": 0.03,
                    "effect_size": 0.5,
                    "effect_size_type": "d",
                    "sample_size": 120,
                    "ci_lower": 0.2,
                    "ci_upper": 0.8,
                },
                "quote": "Participants under biophilic ceilings reported lower stress.",
                "page_span": "p.3-4",
                "raw_abstract": "Dummy abstract for offline smoke test.",
            }
        ]
        return json.dumps(data)
    # Fallback: return an empty object
    return json.dumps({})


def main() -> None:
    _install_root()

    from src.services.service_locator import get_graph_service  # type: ignore
    from src.agents import agent_stubs as stubs  # type: ignore

    Agent_Finder = stubs.Agent_Finder
    Agent_Aggregator = stubs.Agent_Aggregator
    Agent_Linker = stubs.Agent_Linker

    original_call_llm = stubs.call_llm
    stubs.call_llm = fake_call_llm

    # Clean any previous smoke-test artefacts
    data_dir = ROOT / "data"
    graph_path = data_dir / "graph.jsonl"
    calib_dir = data_dir / "calibration"
    data_dir.mkdir(parents=True, exist_ok=True)
    calib_dir.mkdir(parents=True, exist_ok=True)

    if graph_path.exists():
        graph_path.unlink()
    for p in calib_dir.glob("*.json"):
        try:
            p.unlink()
        except Exception as e:
            import logging; logging.getLogger(__name__).debug(f"Non-critical: {e}")

    paper_text = "This is a dummy paper used only for the offline smoke test."
    abstract = "Dummy abstract for offline smoke test."

    artifact = Agent_Finder(
        paper_text=paper_text,
        abstract=abstract,
        paper_type="generic",
        paper_id="SMOKE_TEST_PAPER",
    )

    seven_items = [item.model_dump() for item in artifact.items]
    agg = Agent_Aggregator(seven_items)
    links = Agent_Linker(agg, seven_items)

    store = get_graph_service()
    events = store.get_all_events()
    event_types = {e.get("type") for e in events}

    missing = {"finding", "aggregation", "links"} - event_types
    if missing:
        print("[offline_pipeline_smoke] FAIL: missing event types:", missing)
        stubs.call_llm = original_call_llm
        raise SystemExit(1)

    calib_files = list(calib_dir.glob("*.json"))
    if not calib_files:
        print("[offline_pipeline_smoke] FAIL: no calibration artefacts found in data/calibration")
        stubs.call_llm = original_call_llm
        raise SystemExit(1)

    print("[offline_pipeline_smoke] OK")
    print(f" - events in graph.jsonl: {len(events)}")
    print(f" - calibration files: {len(calib_files)}")

    stubs.call_llm = original_call_llm


if __name__ == "__main__":
    main()
