# Article Eater v20.7.5 — Subject-Aware Panels + RuleGraph v2 Builder

## Overview

This sprint wires the subject-aware Seven-Panel v2 scaffolding into
the engine as an **optional**, additive path:

- A new Agent_Finder_v2 entry point that runs the classic Seven-Panel
  finder PLUS a subject-aware Seven-Panel v2 extraction.
- A RuleGraph v2 builder that maps Seven-Panel v2 panels into structured
  rule objects with explicit subject_scope and subject_moderators.
- A JSONL graph store extension to persist RuleGraph v2 events.

Existing flows, tests, and public surfaces remain unchanged.

## Changes

1. **SevenPanelV2Bundle model**

   - Added `SevenPanelV2Bundle` to `src/contracts/schemas.py` as a
     container for:
       - PanelSubjects, PanelContext, PanelMeasures,
         PanelFindingsV2, PanelHeterogeneity, PanelMechanisms,
         PanelLimits
       - plus provider/model metadata and optional cost_usd.

2. **Seven-Panel v2 extraction agent**

   - New module: `src/agents/agent_panels_v2.py`
   - Function: `extract_seven_panel_v2(pdf_text, abstract, paper_id)`
   - Behaviour:
       - Reads `prompts/seven_panel_v2_master.md`.
       - Calls the configured LLM provider via `LLMConfig`/`call_llm`.
       - Expects a single JSON object with keys:
         `panel_subjects`, `panel_context`, `panel_measures`,
         `panel_findings`, `panel_heterogeneity`, `panel_mechanisms`,
         `panel_limits`.
       - Validates each non-null panel against its JSON schema in
         `schemas/panel_*.schema.json`.
       - Returns a populated `SevenPanelV2Bundle`.

3. **RuleGraph v2 builder**

   - New module: `src/services/rulegraph_v2_builder.py`
   - Function: `build_rulegraph_v2_rules(paper_id, bundle)`
   - Behaviour:
       - For each `FindingV2` item, constructs a RuleGraph v2 dict
         (see `schemas/rule_graph.schema.json`) with:
           - `rule_id` = `<paper_id>:<finding_id>`
           - `status` = `prima_facie`
           - `rule_text` = `finding_text`
           - `factors` / `outcomes` = empty lists (for now)
           - `provenance` = paper_id + provider/model
           - `evidence` = per-finding stats/quote/page_span/task_id/indicators
           - `subject_scope` = derived from PanelSubjects.sample
           - `subject_moderators` = derived from PanelHeterogeneity patterns
           - `graph_version` = "2.0"
           - `created_at` = current UTC ISO timestamp.

4. **Graph store extension**

   - Updated `src/services/graph_service_fallback.py`:
       - New method `apply_rulegraph_v2(paper_id, rules)` which appends
         a `"type": "rulegraph_v2"` event to `data/graph.jsonl` with:
           - `paper_id`
           - `rules` (the full list of v2 rule dicts).

5. **High-level agent wrapper**

   - Updated `src/agents/agent_stubs.py`:
       - New function `Agent_Finder_v2(paper_text, abstract, paper_type, paper_id)`.
       - Behaviour:
           1. Generate a synthetic paper_id if none is provided.
           2. Call `Agent_Finder(...)` to run the classic Seven-Panel
              extraction and persistence.
           3. Call `extract_seven_panel_v2(...)` to build a
              `SevenPanelV2Bundle`.
           4. Call `build_rulegraph_v2_rules(...)` and persist the
              resulting rules via `apply_rulegraph_v2`.
           5. Return a dict bundling:
              `paper_id`, `seven_panel`, `panels_v2`, `rules_v2`.

6. **Prompt for Seven-Panel v2**

   - New prompt file: `prompts/seven_panel_v2_master.md`.
   - Documents the intended JSON shapes for each v2 panel and emphasises:
       - subject-aware sampling and traits,
       - context and task structure,
       - measurement indicators and construct mappings,
       - heterogeneity patterns (moderators),
       - mechanisms and limits.

## Compatibility

- No existing public APIs or CLIs have changed.
- `Agent_Finder` continues to use the legacy Seven-Panel schema and
  JSONL events.
- `Agent_Finder_v2` is an opt-in richer path that downstream tools can
  gradually adopt.

