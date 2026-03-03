# AG Contributions — Draft for Master Doc

**Date**: 2026-03-02 (AG session, for Claude review before merging)  
**Context**: AG's recent engineering contributions that should be reflected in the master book.

---

## §NEW: PDF Acquisition Infrastructure

ATLAS now has a 5-step automated PDF acquisition cascade:

```
DOI → OpenAlex Content API → Unpaywall → CORE → PMC/NCBI → OA URL Fallback
```

**API Stack**: OpenAlex (paid content, $0.01/PDF), Unpaywall (free OA locations), CORE (37M repository full texts), PMC/NCBI (NIH-funded open access), Semantic Scholar (metadata + citations), CrossRef (DOI resolution).

**Results**: Of 30 journal papers from the foundational reading list, 7 (23%) were downloaded automatically at zero cost. The remaining 23 are recorded in the HITL database for human acquisition via Elicit, Academia.edu, or UCSD Library.

**Key insight**: Most academic papers behind paywalls (Elsevier, Nature, Annual Reviews, APA) cannot be acquired programmatically regardless of API sophistication. The institutional access advantage (UCSD Library) is the most powerful acquisition tool for a researcher like David.

## §NEW: Auto-Ingestion Pipeline

Script: `scripts/auto_ingest_pdfs.py`

When new PDFs appear in `data/pdfs_incoming/`, the pipeline runs:

1. **DETECT** — Scan for PDFs not yet extracted
2. **EXTRACT** — Run Gemini extraction → extraction JSON
3. **QA GATE** — Validate quality (≥0.5 = pass, ≥0.75 = high confidence)
4. **INTEGRATE** — Add beliefs to Web of Belief via `ExtractionToWebIntegrator`
5. **OVERSEER** — Call `post_integration_check()`, flag violations

Supports `--watch` (continuous polling), `--dry-run`, `--hitl-status`.

Failed acquisitions are automatically recorded to the HITL database (`data/acquisition/hitl_needed.json`) with DOI, failure reason, priority, and recommended manual sources.

## §NEW: HITL (Human-In-The-Loop) Database

The HITL database bridges automated and manual acquisition:

```json
{
  "doi": "10.1038/nrn2787",
  "reason": "Automated cascade failed — paywalled by Nature",
  "priority": "high",
  "status": "pending",
  "attempt_count": 1,
  "recommended_sources": ["Elicit", "Academia.edu", "UCSD Library", "scholar.archive.org"]
}
```

The Overseer can read this database. The human dashboard will display it as actionable cards: "5 high-priority papers need your attention. Fastest path: paste these DOIs into Elicit (~10 min)."

## §UPDATE: Answer Enrichment Orchestrator — V11 Panel Fixes

Five engineering improvements based on the V11 Ruthless Audit panel:

1. **Service contracts** (Protocol classes) — `CredenceService`, `WarrantService`, `RiskAssessor`, `GapDetector`, `QuestionClassifierService`. These enforce type-safe service interfaces without requiring inheritance.

2. **Health check endpoint** — `orchestrator.health_check()` probes all 9 services and returns a structured availability report including healthy/total counts, import errors, and step dependency graph.

3. **Global latency budget** — 5-second total timeout (configurable via `EnrichmentConfig.global_timeout_ms`). If the budget is exceeded mid-pipeline, remaining steps are cancelled and logged. This prevents the worst-case 18s (9 steps × 2s) from blocking interactive QA.

4. **Step dependency graph** — `STEP_DEPENDENCIES` declares that `warrant_trace` depends on `credence_ci` (needs enriched beliefs), and `follow_ups` depends on `gap_analysis`. Steps run in declared order; if a dependency is skipped, dependents operate on partial data (graceful degradation).

5. **Dead registry cleanup** — Removed `argumentation_graph`, `bridge_warrants`, and `prediction_generator` from `_ServiceRegistry`. These were loaded but never called by any enrichment step, per Panel Member B: "Dead code in a service registry implies capabilities that don't exist."

## §PROPOSED: Interpretation Layer Acronym

The Interpretation Layer (formally `interpretive_intelligence.py`) deserves an acronym. Candidates:
- **IIS** — Interpretive Intelligence Service (matches class name)
- **IRIS** — Interpretive Research Intelligence System
- **IL** — Interpretation Layer (simple)

Recommendation: **IIS** — short, matches code, and "intelligence" captures that this is more than routing (it classifies explanation patterns, matches pedagogical modes, and selects epistemic operations).

## §PROPOSED: Human Dashboard

Panel deliberation completed (see `docs/DASHBOARD_PANEL_DELIBERATION_2026-03-02.md`). 

Recommended implementation: three-view Streamlit dashboard:
1. **Mission Control** — AESHI, HITL queue, violations, belief trends (30s daily glance)
2. **Operations** — pipeline stages, service health, API quotas, latency budget (investigation)
3. **Research Command** — theory coverage, gap predictions, VOI-ranked papers, tension alerts

Design principles from the panel: 60-second rule, action > information, progressive disclosure, traffic-light colors, "since last visit" framing.
