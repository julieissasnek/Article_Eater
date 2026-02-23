#!/usr/bin/env python3
"""Offline v2 pipeline smoke test for Article Eater v20.7.6.

This script does NOT call any real LLM provider. Instead, it monkey-patches
the agent-level `call_llm` function to return small, schema-valid JSON
payloads and then exercises the **v2** path:

- Agent_Finder_v2 -> classic Seven-Panel extraction
                    + Seven-Panel v2 panels
                    + RuleGraph v2 rules

It asserts that:
- data/graph.jsonl contains at least one `rulegraph_v2` event.

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

    We only need enough structure to satisfy the Seven-Panel v2 schemas.
    """
    # Agent_Finder_v2 still runs classic Agent_Finder first, so return a
    # schema-valid classic findings array for that path.
    if "Seven-Panel findings array" in prompt or "Seven-Panel findings" in prompt:
        return json.dumps(
            [
                {
                    "finding_text": "Dummy finding: biophilic ceiling reduces reported stress.",
                    "statistics": {
                        "p_value": 0.03,
                        "effect_size": 0.5,
                        "effect_size_type": "d",
                        "sample_size": 60,
                        "ci_lower": 0.2,
                        "ci_upper": 0.8,
                    },
                    "quote": "Participants under biophilic ceilings reported lower stress.",
                    "page_span": "p.3-4",
                    "raw_abstract": "Dummy abstract for v2 smoke test.",
                }
            ]
        )

    # The v2 agent identifies itself by expecting a single JSON object with
    # keys panel_subjects / panel_context / ... / panel_limits.
    if "Seven-Panel v2 representation" in prompt or "Seven-Panel v2" in prompt:
        return json.dumps(
            {
                "panel_subjects": {
                    "type": "panel_subjects",
                    "paper_id": "SMOKE_TEST_PAPER_V2",
                    "sample": {
                        "demographics": {
                            "age_mean": 30.0,
                            "age_sd": 5.0,
                            "age_range": "18-40",
                            "age_band": "young_adult",
                            "sex_gender_distribution": {"female": 40, "male": 20},
                            "education_band": "university_undergrads",
                            "sample_size": 60,
                        },
                        "culture": {
                            "countries": ["United States"],
                            "region": "WEIRD",
                            "self_construal_profile": "more_independent",
                        },
                        "clinical_status": {
                            "population": "healthy",
                            "key_inclusions": [],
                            "key_exclusions": [],
                        },
                    },
                    "traits_measured": [
                        {
                            "name": "Sensory Processing Sensitivity",
                            "scale": "HSPS",
                            "used_as_moderator": True,
                        }
                    ],
                    "notes": "Same as sample.traits_measured.",
                },
                "panel_context": {
                    "type": "panel_context",
                    "paper_id": "SMOKE_TEST_PAPER_V2",
                    "tasks": [
                        {
                            "task_id": "TASK1",
                            "name": "View biophilic vs. non-biophilic ceiling images",
                            "activity_type": "passive_viewing",
                            "duration_min": 10,
                            "setting": "lab",
                            "environment_type": "office",
                            "relevance_tags": ["biophilia", "architecture"],
                            "notes": "Dummy context task.",
                        }
                    ],
                    "global_notes": "Dummy context for smoke test.",
                },
                "panel_measures": {
                    "type": "panel_measures",
                    "paper_id": "SMOKE_TEST_PAPER_V2",
                    "indicators": [
                        {
                            "indicator_id": "IND_STRESS",
                            "name": "Perceived stress VAS",
                            "modality": "self_report",
                            "instrument": "10cm visual analog scale",
                            "timescale": "phasic",
                            "interpretation": ["higher = more stressed"],
                            "notes": None,
                        }
                    ],
                    "construct_mappings": [
                        {
                            "construct": "stress",
                            "indicator_ids": ["IND_STRESS"],
                            "notes": "Basic mapping for smoke test.",
                        }
                    ],
                    "notes": None,
                },
                "panel_findings": {
                    "type": "panel_findings",
                    "paper_id": "SMOKE_TEST_PAPER_V2",
                    "items": [
                        {
                            "finding_id": "FINDING_V2_1",
                            "finding_text": "Biophilic ceilings reduce perceived stress compared to non-biophilic ceilings.",
                            "statistics": {
                                "p_value": 0.01,
                                "effect_size": 0.6,
                                "effect_size_type": "d",
                                "sample_size": 60,
                                "ci_lower": 0.2,
                                "ci_upper": 1.0,
                            },
                            "quote": "Participants reported lower stress under biophilic ceilings.",
                            "page_span": "p. 10-11",
                            "task_id": "TASK1",
                            "indicator_ids": ["IND_STRESS"],
                            "raw_abstract": None,
                        }
                    ],
                },
                "panel_heterogeneity": {
                    "type": "panel_heterogeneity",
                    "paper_id": "SMOKE_TEST_PAPER_V2",
                    "moderation_patterns": [
                        {
                            "finding_id": "FINDING_V2_1",
                            "moderator": "Sensory Processing Sensitivity",
                            "dimension": "traits",
                            "levels_compared": ["high_SPS", "low_SPS"],
                            "pattern": "Effect is stronger for high-SPS individuals.",
                            "stats_summary": "interaction p < .05",
                            "evidence_snippet": "High-SPS participants showed larger stress reductions.",
                            "section": "Results",
                        }
                    ],
                },
                "panel_mechanisms": {
                    "type": "panel_mechanisms",
                    "paper_id": "SMOKE_TEST_PAPER_V2",
                    "mechanism_claims": [
                        {
                            "claim_id": "MECH1",
                            "claim_text": "Biophilic ceilings support predictive coding by providing scale-invariant structure.",
                            "theory": "predictive_coding",
                            "phenomenon": "reduced stress response",
                            "role": "explains",
                            "strength": "speculative",
                            "evidence_snippet": "We speculate that fractal-like patterns support predictive models.",
                            "page_span": "p. 12",
                        }
                    ],
                },
                "panel_limits": {
                    "type": "panel_limits",
                    "paper_id": "SMOKE_TEST_PAPER_V2",
                    "generalization_notes": [
                        "Findings likely generalise to similar WEIRD undergraduate samples."
                    ],
                    "threats_to_validity": [
                        "Limited demographic diversity",
                        "Artificial lab environment",
                    ],
                    "future_work_notes": [
                        "Replicate in non-WEIRD samples",
                        "Extend to real architectural spaces",
                    ],
                },
            }
        )

    # Fallback: return an empty object for non-finding/non-v2 prompt paths.
    return json.dumps({})

def main() -> None:
    _install_root()
    from scripts import offline_pipeline_smoke  # type: ignore
    from src.agents import agent_stubs as stubs
    from src.agents import agent_panels_v2
    from src.services.service_locator import get_graph_service

    original_call_llm = stubs.call_llm
    original_v2_call_llm = agent_panels_v2.call_llm
    stubs.call_llm = fake_call_llm
    agent_panels_v2.call_llm = fake_call_llm

    data_dir = ROOT / "data"
    graph_path = data_dir / "graph.jsonl"
    data_dir.mkdir(parents=True, exist_ok=True)

    if graph_path.exists():
        graph_path.unlink()

    paper_text = "Dummy v2 paper text for offline v2 smoke test."
    abstract = "Dummy abstract for v2 smoke test."

    # Use the v2 agent; it will internally invoke the classic flow as well.
    result = stubs.Agent_Finder_v2(
        paper_text=paper_text,
        abstract=abstract,
        paper_type="generic",
        paper_id="SMOKE_TEST_PAPER_V2",
    )

    store = get_graph_service()
    events = store.get_all_events()
    event_types = {e.get("type") for e in events}

    if "rulegraph_v2" not in event_types:
        print("[offline_pipeline_v2_smoke] FAIL: missing rulegraph_v2 event in graph.jsonl")
        stubs.call_llm = original_call_llm
        agent_panels_v2.call_llm = original_v2_call_llm
        raise SystemExit(1)

    print("[offline_pipeline_v2_smoke] OK")
    print(f" - events in graph.jsonl: {len(events)}")
    print(f" - v2 rules emitted: {len(result.get('rules_v2', []))}")

    stubs.call_llm = original_call_llm
    agent_panels_v2.call_llm = original_v2_call_llm


if __name__ == "__main__":
    main()
