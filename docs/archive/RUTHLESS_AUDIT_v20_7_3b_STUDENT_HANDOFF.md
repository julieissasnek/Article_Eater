# Ruthless Audit – v20.7.3b Student Handoff

**Perspective:** Senior undergraduate or early graduate student joining an Article Eater project.

**Question:** “Can I, following the docs, get a working environment and run a meaningful test without getting stuck?”

This audit focuses only on **student usability**, not on long-term research completeness.

---

## 1. Engine and pipeline

### Status: GO for student-level testing

Evidence:

- `scripts/sanity_check.py`:
  - Compiles all Python files under the repo.
  - Imports:
    - `src.agents.agent_stubs` (Finder, Aggregator, Linker).
    - `src.services.graph_service_fallback.JSONLGraphStore`.
    - `src.services.service_locator.get_graph_service`.
    - `src.services.bbn_calibrator.compute_confidence_for_finding`.
  - Scans `src/` for `TODO`, `NotImplementedError`, `# STUB:`.
  - On a healthy checkout, it should report **OK**.

- `scripts/offline_pipeline_smoke.py`:
  - Monkey-patches `call_llm` to avoid real API usage.
  - Runs:
    - `Agent_Finder` on a dummy paper.
    - `Agent_Aggregator` on the resulting Seven-Panel items.
    - `Agent_Linker` on the aggregated output.
  - Asserts that:
    - `data/graph.jsonl` contains at least one `finding`, `aggregation`, and `links` event.
    - `data/calibration/` contains at least one JSON confidence artefact.

Conclusion:

- A student with a working Python environment can:
  - Install dependencies.
  - Run both scripts successfully.
  - Inspect the engine’s outputs (graph + calibration) without editing any code.

---

## 2. Installation and environment

### Status: GO with clear instructions

- `requirements.txt` at the repo root captures the backend and agent dependencies.
- The Student Quickstart includes:
  - Virtualenv setup instructions.
  - Clear `pip install -r requirements.txt` step.
  - A note that the User Rules GUI requires an extra `pip install -r apps/user_rules_gui/requirements.txt`.

Risks:

- Students who skip the virtualenv may collide with system Python packages.
- Missing `Flask` / `SQLAlchemy` is handled as a **warning** in `sanity_check.py`, not a hard failure.

Conclusion:

- For students who follow the instructions literally, environment setup is **feasible and bounded**.

---

## 3. GUIs and user experience

### Status: PARTIAL GO (limited surfaces)

Currently “student-usable” surfaces:

1. **Offline pipeline scripts (CLI)**
   - Good for:
     - Seeing the engine move data end-to-end.
     - Inspecting real artefacts in `data/graph.jsonl` and `data/calibration/`.
   - Not a visual UI, but cognitively straightforward.

2. **User Rules GUI (Flask)**
   - Good for:
     - Exploring a simple rule-editing interface.
     - Understanding how rules are stored and manipulated via a web UI.
   - Self-contained, with its own `requirements.txt`.

Not yet fully audited:

- The full Article Eater frontends that are supposed to expose:
  - The Librarian’s views (paper ingestion, seven-panel reviews).
  - The Synthesizer’s views (rule clusters).
  - The Admin’s “confidence engine” GUI.

These exist in the repo but have **not** been fully audited here for:

- Error handling.
- Consistent navigation.
- Alignment with the current Agent + graph + calibration implementation.

Conclusion:

- Students can **safely use** the CLI tests and User Rules GUI.
- They should be warned that the more ambitious GUIs may still be evolving.

---

## 4. Scope clarity for students

Without guidance, a student might assume:

- The system is “production-ready.”
- All GUIs are equally supported.
- Neo4j, BN integration, and real LLM calls are expected to work out-of-the-box.

We explicitly **counter** that by:

- Limiting the Quickstart to:
  - Core engine tests.
  - One optional GUI (User Rules).
- Marking advanced topics as out-of-scope for first contact:
  - External graph databases.
  - Full BN integration.
  - Real LLM providers.

Conclusion:

- With the new docs, expectations are clearly bounded.
- Students should know what is stable and what is aspirational.

---

## 5. Final student-focused GO / NO-GO

From a **student onboarding** perspective:

- **GO** for:
  - Setting up a Python environment.
  - Running `scripts/sanity_check.py`.
  - Running `scripts/offline_pipeline_smoke.py`.
  - Inspecting `data/graph.jsonl` and `data/calibration/`.
  - Running the User Rules GUI as a small, self-contained UI.

- **NO-GO (for now)** for:
  - Treating the full Article Eater GUI stack as a polished, end-to-end product.
  - Expecting automatic Neo4j / BN / real-LLM integration without additional configuration and supervision.

This is a **workable student handoff** for engine-level experimentation and small UI demos, but not yet a turnkey “click once and get a full research system” experience.
