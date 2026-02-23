# Subject-Aware Seven-Panel v2 + RuleGraph v2 Workflow

This document explains how to exercise the subject-aware Seven-Panel v2
and RuleGraph v2 pipeline in Article Eater.

## 1. Run a standard L0/L1/L2 pipeline

Use the normal ingestion pipeline (CLI or worker) to:
- fetch papers from Semantic Scholar (L0),
- cluster and select key papers (L1),
- extract classic Seven-Panel findings (L2).

This populates the `articles`, `findings`, and JSONL graph store.

## 2. Run the v2 subject-aware pipeline

The v2 path augments classic Seven-Panel with:
- PanelSubjects (detailed subject profile),
- PanelContext,
- PanelMeasures,
- PanelFindingsV2,
- PanelHeterogeneity,
- PanelMechanisms,
- PanelLimits,
and then builds subject-aware RuleGraph v2 rules from those panels.

There are two main ways to exercise this path:

### 2.1 Command-line smoke test

From the repo root:

```bash
python scripts/offline_pipeline_v2_smoke.py
```

This:
- monkey-patches the v2 agent to return canned but schema-valid Seven-Panel v2 JSON,
- writes `rulegraph_v2` events into `data/graph.jsonl`,
- validates that at least one `rulegraph_v2` event is present.

### 2.2 Admin UI "Run v2 subject pipeline smoke test"

In the Admin Control Room (`/admin`):

- Go to the **Subject Rules (RuleGraph v2)** tab.
- Click **“Run v2 subject pipeline smoke test”**.
- The backend calls `scripts/offline_pipeline_v2_smoke.py` in a subprocess.
- A popup shows whether the test passed and the underlying return code.

## 3. Inspect subject-aware rules

Still in the RuleGraph v2 tab:

- Use the paper filter, text search, age band filter, and trait filter
  to explore subject_scope and subject_moderators across rules.
- Use **Download coverage JSON** to snapshot global and per-paper
  subject typing coverage.

## 4. BN export and downstream analysis

Once subject-aware rules look reasonable:

- Use **Export BN (JSON)** in the RuleGraph v2 tab to build a BN skeleton
  from the v2 rules.
- Load this into the BN Playground or external tools for further analysis.

This gives you a full subject-aware loop: from Seven-Panel v2 panels,
through RuleGraph v2 rules, into BN- and RAG-friendly representations
that explicitly encode subject_scope and subject_moderators.
