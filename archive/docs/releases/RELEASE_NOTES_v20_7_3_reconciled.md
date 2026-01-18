# Article Eater v20.7.3‑reconciled – Release Notes

## Overview

This release reconciles two parallel 20.7.3 lines:

* **v20.7.3g** – governance‑complete baseline with CI, smoke scripts, and full
  architecture / threat‑model / student docs.
* **v20.7.3i** – agents‑wired branch with graph navigation routes, a guarded
  rules GUI, and a student “rule graph” how‑to.

The **v20.7.3‑reconciled** tree is a **non‑destructive union**:

* Every file present in v20.7.3g is still present here.
* Every file present in v20.7.3i is also present here.
* Where the two versions disagree on file contents:
  * The v20.7.3i version is used as the live file.
  * The v20.7.3g version is preserved under:
    * `archive/v20_7_3g_pre_i/<original_path>`.

No files were silently deleted; superseded versions were archived.

## What’s new vs v20.7.3g

Relative to v20.7.3g, this reconciled build adds the features that were
introduced on the v20.7.3i branch:

* **Graph navigation API (FastAPI)**

  * New router: `app/routes/graph.py`.
  * Read‑only endpoints:
    * `GET /graph/events` – list graph events with optional filters
      (`type`, `paper_id`, `limit`).
    * `GET /graph/topic/{topic}` – retrieve findings and links associated
      with a given topic.

  These are strictly read‑only and intended for student and researcher
  exploration of the JSONL graph store.

* **Rule GUI admin guard**

  * The `apps/user_rules_gui` app now differentiates between:
    * visitors (read‑only browsing of rules), and
    * admins (who can create / edit / delete rules).
  * Admin access is controlled by the environment variable
    `AE_RULES_ADMIN_PASSWORD`.
  * New template:
    * `apps/user_rules_gui/templates/login.html`.

* **Student “rule graph” guide**

  New docs under `docs/`:

  * `docs/STUDENT_HOWTO_RULE_GRAPH.md`
  * `docs/STUDENT_HOWTO_RULE_GRAPH.html`

  These explain how students can:

  * inspect the JSONL graph via the `/graph` endpoints, and
  * browse the curated rules table in the GUI,
  * while respecting the “read‑only for non‑admins” policy.

## What’s restored vs v20.7.3i

v20.7.3i was built on an earlier agents‑wired base that did not include some
of the governance and student handoff artefacts introduced in v20.7.3g.
Those files are restored here:

* **CI & governance wiring**

  * `.github/workflows/ci.yml` – restores the CI gate for governance checks.

* **Smoke / sanity scripts**

  * `scripts/offline_pipeline_smoke.py`
  * `scripts/run_all_checks.py`
  * `scripts/sanity_check.py`

  These provide one‑shot sanity and smoke runs for the pipeline.

* **Config scaffolding**

  * `config/.env.example`
  * `src/config/__init__.py`
  * `src/config/settings.py`

  These give a canonical place to document environment variables and
  configuration defaults, even if some callers now use the newer settings
  helpers.

* **Student / architecture docs**

  * `docs/ARCHITECTURE_OVERVIEW.md`
  * `docs/AUTHORIZATION_MATRIX_v1.md`
  * `docs/CONFIGURATION_GUIDE.md`
  * `docs/RUTHLESS_AUDIT_v20_7_3b_STUDENT_HANDOFF.md`
  * `docs/STUDENT_QUICKSTART_Article_Eater_v20_7_3b.md`
  * `docs/STUDENT_QUICKSTART_Article_Eater_v20_7_3b.html`
  * `docs/THREAT_MODEL_v1.md`

  These documents were never meant to vanish; they are part of the
  governance and teaching surface.

* **Example data**

  * `data/graph.jsonl`
  * `data/calibration/*.json` (sample calibration artefacts)

  These remain as examples and can be replaced or extended by lab‑specific
  runs.

## Governance and contracts

This release is intended to respect the repository‑level contracts:

* **No silent deletions**

  * All files from both v20.7.3g and v20.7.3i are present.
  * When a v20.7.3i file supersedes a v20.7.3g file, the older version is
    copied to:
    * `archive/v20_7_3g_pre_i/<original_path>`.

* **Governance kit and constitution present**

  * `Project_Constitution.md`
  * `release.keep.yml`
  * `deprecations.yml`
  * `MANIFEST.sha256`
  * Governance kit templates and helpers under `governance_kit/`.
  * `scripts/check_governance.py`.

* **Ruthless prompts and audit aides present**

  * `RUTHLESS_v5.x` docs and prompt files.
  * AI‑handoff prompts and audit reports under `docs/` and `docs/audits/`.

* **ZIP + concatenated TXT artefacts**

  For this reconciled version there are two main distribution artefacts:

  * `Article_Eater_v20_7_3_reconciled.zip`
  * `Article_Eater_v20_7_3_reconciled_concatenated.txt`
    (includes a self‑contained deconcatenation script at the top).

## Status relative to Gemini’s critique

Gemini’s earlier “reasonable start” critique is intentionally not papered
over in this release. The reconciled tree is meant as a stable base for the
next phase, not as a claim that all issues are solved.

In particular:

* **Agents “hot‑wired” vs fully engineered**

  * The powered agents (Finder, Aggregator, Linker) are wired and can read /
    write structured graph events, but some of the deeper looping and
    cross‑paper logic is still closer to a proof‑of‑concept than to a
    fully‑engineered control room.

* **Graph backend**

  * A robust JSONL‑backed graph store and service locator are in place.
  * A production‑grade graph database backend (e.g., Neo4j) is not yet wired
    as the default; the abstractions are ready, but deployment integration
    remains future work.

* **Confidence / BBN calibration**

  * The BBN calibrator and Confidence Engine GUI are implemented and usable.
  * The current weights and formulas are hypothesis priors, not yet tuned
    against a labelled corpus of 10–20 papers via expert review.

* **GUI polish**

  * The GUI is functionally complete and documented (including student
    help and rule‑graph HOWTO), but it has not yet undergone a full
    design‑system / visual‑polish pass to reach “commercial SaaS” quality.

## Suggested next steps

The natural next phase on top of v20.7.3‑reconciled is:

1. **Data‑driven calibration**
   * Run a curated set of papers through the agents.
   * Collect expert judgements on findings, links, and confidence.
   * Use the Confidence Engine GUI to tune weights until model output
     matches expert expectations.

2. **Graph backend implementation**
   * Implement and test a Neo4j (or equivalent) adapter behind the existing
     graph service interface.
   * Keep the JSONL backend as a safe fallback for labs without a graph DB.

3. **Agent logic refinement**
   * Expand Aggregator and Linker loops to cover the full set of
     cross‑paper and cross‑mechanism patterns outlined in the design docs.
   * Add practical examples and unit tests for each major pattern.

4. **GUI / UX pass**
   * Apply a dedicated design pass for the main dashboards and modals.
   * Standardise components, error states, and empty‑state messaging so that
     the tool feels cohesive for students and collaborators.

This reconciled release is therefore best understood as a **stable,
governed platform** for continuing development and calibration, rather than
as a final, fully‑calibrated production deployment.
