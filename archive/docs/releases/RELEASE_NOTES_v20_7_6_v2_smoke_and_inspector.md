# Article Eater v20.7.6 — v2 smoke test + RuleGraph inspector

## Overview

This sprint focuses on **robustness and inspectability** of the v2,
subject-aware path:

- An offline smoke test that exercises `Agent_Finder_v2` without calling
  any real LLM provider and asserts that `rulegraph_v2` events are
  correctly written to `data/graph.jsonl`.
- A small CLI inspector to list v2 rules and summarise their subject
  annotations.

Existing flows remain unchanged.

## Changes

1. **Offline v2 pipeline smoke test**

   - New script: `scripts/offline_pipeline_v2_smoke.py`
   - Behaviour:
       - Monkey-patches `src.agents.agent_stubs.call_llm` with a canned
         `fake_call_llm` that returns a schema-valid Seven-Panel v2 JSON
         object (including:
           - panel_subjects with demographics, culture, clinical status,
             traits (e.g., HSPS),
           - panel_context with a single dummy task,
           - panel_measures with one indicator and construct mapping,
           - panel_findings with one finding,
           - panel_heterogeneity with a trait-based moderator,
           - panel_mechanisms and panel_limits).
       - Calls `Agent_Finder_v2(...)` to trigger:
           - classic Seven-Panel extraction,
           - Seven-Panel v2 extraction,
           - RuleGraph v2 construction,
           - persistence of a `"type": "rulegraph_v2"` event.
       - Asserts:
           - `data/graph.jsonl` exists and contains at least one
             `rulegraph_v2` event.
       - Prints a small OK summary and the number of events and v2 rules.

2. **RuleGraph v2 inspector CLI**

   - New script: `scripts/inspect_rulegraph_v2.py`
   - Behaviour:
       - Reads `data/graph.jsonl`.
       - Filters events with `"type": "rulegraph_v2"`.
       - For each event, prints:
           - `paper_id`
           - number of rules
           - up to three sample rules, showing:
               - `rule_id`
               - truncated `rule_text`
               - a one-line summary of `subject_scope`:
                   - age_band / education_band / n
                   - culture region and countries
                   - clinical population
                   - key traits measured
               - a one-line summary of `subject_moderators` grouped by
                 dimension (demographics / culture / traits / clinical / etc.).
       - Handles missing or malformed lines robustly (continues past
         JSON decode errors).

## Usage

- To run the offline v2 smoke test (no real LLM calls):

  ```bash
  python scripts/offline_pipeline_v2_smoke.py
  ```

- To inspect stored v2 rules:

  ```bash
  python scripts/inspect_rulegraph_v2.py
  ```

These utilities give fast feedback that the subject-aware path is wired
correctly and that the resulting RuleGraph v2 events are human-
interpretable.
