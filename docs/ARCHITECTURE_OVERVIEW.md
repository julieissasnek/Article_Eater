# Architecture Overview – Article Eater (v20.7.3)

This document sketches the high-level architecture of Article Eater as it is
implemented in the v20.7.3 codebase.

---

## 1. Main components

### 1.1 Agents

Location: `src/agents/`

- **Agent_Finder**
  - Takes raw paper text (and optionally an abstract and metadata).
  - Calls an LLM with a Seven-Panel prompt.
  - Parses the response into structured `SevenPanelArtifact` items.
  - Persists findings into the graph service and triggers confidence
    calibration.

- **Agent_Aggregator**
  - Groups findings into higher-level mechanisms or themes.
  - Reads `SevenPanelArtifact` items and emits aggregation events.

- **Agent_Linker**
  - Identifies links between mechanisms, outcomes, and contextual factors.
  - Emits link events into the graph.

All agent LLM calls are routed through a shared `call_llm` helper, which can be
configured to use a fake LLM (for tests) or a real provider.

### 1.2 Services

Location: `src/services/`

- **Graph service (`graph_service_fallback.py` + `service_locator.py`)**
  - In v20.7.3, the default backend is a JSONL file (`data/graph.jsonl`).
  - The `JSONLGraphStore` implements basic operations like:
    - appending events (`finding`, `aggregation`, `links`),
    - reading back all events.

- **Confidence calibrator (`bbn_calibrator.py`)**
  - Computes a confidence value for each finding based on a configuration file
    (e.g., weights on p-values, effect sizes, replication, etc.).
  - Writes per-finding calibration artefacts under `data/calibration/`.

The `service_locator` provides `get_graph_service()` so that the rest of the
code does not depend on a specific backend implementation.

### 1.3 GUIs

Location: `src/gui/` and `apps/`

- **Web frontends**
  - Provide views for librarians, synthesizers, and admins (e.g., paper
    ingestion, rule management, confidence inspection).
  - Some of these are still evolving; the current repo focuses on ensuring the
    engine is stable and testable.

- **User Rules GUI (`apps/user_rules_gui/`)**
  - A small Flask app backed by SQLite.
  - Allows users to add/edit/delete rules through a simple web interface.

---

## 2. Data flow (happy path)

1. **Paper ingestion**
   - A paper (PDF or text) is ingested and normalised to raw text.

2. **Finder phase**
   - `Agent_Finder` receives the text, calls the LLM, and parses Seven-Panel
     findings.
   - Findings are stored as `finding` events via the graph service.
   - Confidence scores are computed and written to `data/calibration/`.

3. **Aggregator phase**
   - `Agent_Aggregator` groups related findings into mechanisms.
   - `aggregation` events are written to the graph.

4. **Linker phase**
   - `Agent_Linker` identifies links between mechanisms, outcomes, and other
     entities.
   - `links` events are appended to the graph.

5. **Downstream use**
   - GUIs and analysis tools read from the graph and calibration artefacts to
     present summaries, visualisations, and rule candidates.

---

## 3. Testing and health checks

- **`scripts/sanity_check.py`**
  - Compiles all Python modules.
  - Checks imports for key agents and services.
  - Scans `src/` for `TODO` / `NotImplementedError` / `# STUB:` markers.

- **`scripts/offline_pipeline_smoke.py`**
  - Monkey-patches the LLM call to a fake implementation.
  - Runs the Finder → Aggregator → Linker pipeline on a dummy paper.
  - Verifies the presence of `finding`, `aggregation`, and `links` events in
    `data/graph.jsonl` and at least one calibration artefact.

- **`scripts/run_all_checks.py`**
  - Runs the two scripts above in sequence and prints a summary.
  - Intended as the first entrypoint for “is my checkout healthy?”.

---

## 4. Configuration and deployment

- **Configuration**
  - Centralised in `src/config/settings.py`.
  - Reads from environment variables and an optional `config/.env` file.

- **Backends**
  - JSONL graph backend is the default and requires no external services.
  - Neo4j or other backends can be plugged in by extending the graph service
    and updating `Settings`.

- **LLM providers**
  - The engine can run with a fake LLM for tests or a real provider in
    research/production setups, controlled via configuration.

This overview is deliberately compact. For deeper details, see the module-level
docstrings in the `src/` tree and the additional documentation in `docs/`.
