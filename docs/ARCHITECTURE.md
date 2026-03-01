# ARCHITECTURE.md — ATLAS System Overview

*Last updated: February 26, 2026*

This document is the canonical entry point for any developer or AI working in this codebase. Read this first.

---

## What This System Does

ATLAS (Architecture for Typed, Layered Assessment of Science) extracts causal claims from scientific literature in the cognitive neuroscience of architecture (CNFA) and assembles them into two complementary structures:

1. **Web of Belief** (epistemic layer) — a typed graph of beliefs, warrants, and evidential support relationships. Foundherentist epistemology (Haack, 1993): no foundational claims, everything justified by coherence with everything else. Nodes are beliefs; edges are typed warrants (CONSTITUTIVE, MECHANISM, EMPIRICAL_COVARIANCE, FUNCTIONAL, CAPACITY, ANALOGICAL, THEORETICAL_DEFAULT).

2. **Bayesian Network** (causal layer) — a directed acyclic graph encoding causal relationships between environmental variables and human outcomes. Pearl-compliant (2009). Nodes are measurable variables; edges are causal arrows with conditional probability tables (CPTs).

The two layers are connected by a **projection function π** (epistemic causal bridge): the web of belief is the territory, the BN is the map. The bridge translates epistemic confidence into numerical parameters (Cartwright, 1989).

---

## Five-Layer Architecture

```
Layer 5: Application    │ Streamlit dashboard, API routes, CLI
Layer 4: Extraction     │ PDF → claims → templates → web
Layer 3: Services       │ Web of belief, BN, bridge warrants, overseer
Layer 2: Epistemic      │ Warrants, monitors, entrenchment, coherence
Layer 1: Data/Models    │ ClaimV2, EdgeV2, enums, schemas, contracts
```

---

## Module Map

### Layer 1: Data Models & Contracts

| Module | Path | Purpose |
|--------|------|---------|
| ClaimV2 | `src/epistemic/contracts/claim_v2.py` | Canonical claim schema (provenance tier, causal level, evidence basis) |
| EdgeV2 | `src/epistemic/contracts/edge_v2.py` | Edge schema (typed, weighted, justified) |
| Schemas | `src/contracts/schemas.py` | Pydantic models: Stats, SevenPanelItem, SubjectDemographics |
| Enums | `src/services/web_of_belief_components/enums.py` | EpistemicLevel, BeliefStatus, InferenceType, BeliefKind |
| Graph Models | `src/services/web_of_belief_components/graph_models.py` | Typed graph representation |

### Layer 2: Epistemic Infrastructure

| Module | Path | Purpose |
|--------|------|---------|
| Warrant Scaling | `src/epistemic/warrant_scaling.py` | Dynamic warrant confidence (noisy-OR combination) |
| Coherence Audit | `src/epistemic/monitors/coherence_audit.py` | Runtime coherence health checking |
| Bias Detection | `src/epistemic/monitors/bias_detection.py` | Systematic bias monitoring |
| Asymmetry Monitor | `src/epistemic/monitors/asymmetry_monitor.py` | Evidential asymmetry detection |
| Cross-Type Coherence | `src/epistemic/monitors/cross_type_coherence.py` | Cross-warrant-type coherence |
| Entrenchment | `src/epistemic/entrenchment/` | Quine-style entrenchment (6 sub-modules) |
| Extraction Classifiers | `src/epistemic/extraction/` | Paper, pathway, PE classifiers (8 files) |

### Layer 3: Core Services

| Module | Path | Purpose |
|--------|------|---------|
| **Web of Belief** | `src/services/web_of_belief.py` | Primary epistemic service — the web itself |
| **Bridge Warrants** | `src/services/bridge_warrants.py` | Bridge warrant lifecycle, multiplicative credence formula |
| **Epistemic Causal Bridge** | `src/services/epistemic_causal_bridge.py` | The π function: EWG → BN translation |
| **Overseer** | `src/services/overseer.py` | 6-component governance system (Dijkstra-inspired) |
| **Graph Confidence** | `src/services/graph_confidence_service.py` | BN-side confidence: weighted linear (0.4/0.3/0.3) |
| Scalable Coherence | `src/services/scalable_coherence.py` | Large-scale coherence computation |
| Dual Epistemology | `src/services/dual_epistemology.py` | Web + BN dual-layer management |
| Stability Engine | `src/services/stability_engine.py` | Belief stability assessment |
| WoB Modules | `src/services/web_of_belief_modules/` | 16 sub-modules: coherence, entrenchment, equilibrium, evidence, severity, etc. |
| ECB Modules | `src/services/ecb_modules/` | Causal models, contrast classes, counterfactuals |
| Paper Integration | `src/services/paper_integration/` | 14-step integration cascade (orchestrator.py) |

### Layer 4: Extraction Pipeline

| Module | Path | Purpose |
|--------|------|---------|
| LLM Extraction | `src/extraction/llm_extraction_service.py` | Gemini/GPT-based extraction |
| Paper Triage | `src/extraction/paper_triage.py` | Article type classification |
| Table Classifier | `src/extraction/table_classifier.py` | Table type detection |
| Table Semantics | `src/extraction/table_semantics_codex.py` | Semantic profiling of tables |
| Claim Extractor | `src/extraction/claim_extractor.py` | Claim extraction from text |
| Batch Processing | `src/extraction/batch_extract.py` | Batch extraction orchestration |
| Effect Size Converter | `src/extraction/effect_size_converter.py` | Cohen's d → probability conversion |

### Layer 5: Application

| Module | Path | Purpose |
|--------|------|---------|
| API Main | `app/main.py` | FastAPI application entry point |
| Health Route | `app/routes/health.py` | HTTP health endpoint |
| WoB Route | `app/routes/web_of_belief.py` | Web of belief API |
| Streamlit Dashboard | `streamlit_app/app.py` | Visual dashboard |
| System Health Page | `streamlit_app/pages/8_system_health.py` | Health dashboard |
| Worker | `app/worker.py` | Background job processing |

---

## Key Scripts

### Health & Monitoring

| Script | Scope | Modifies Data? |
|--------|-------|----------------|
| `scripts/overseer_nightly.py` | Full nightly audit (6 invariants) | No (reporting only) |
| `scripts/compute_system_health.py` | Aggregate health score | No |
| `scripts/check_web_bn_health.py` | Web ↔ BN alignment | No |
| `scripts/lint_bridge_ceilings.py` | Ceiling violation detection | No |
| `scripts/validate_all_templates.py` | Template schema validation | No |
| `scripts/corpus_health_report.py` | Corpus-level health report | No |
| `scripts/safe_improve_web_health.py` | Conservative health repair | Yes (reversible) |

### Pipeline

| Script | Scope |
|--------|-------|
| `scripts/gemini_triage_papers.py` | Classify new PDFs by article type |
| `scripts/gemini_extraction_queue.py` | Extract claims from classified PDFs |
| `scripts/two_pass_extraction.py` | Two-pass extraction with verification |
| `scripts/run_realtime_table_rule_intake.py` | Table → provisional rules |
| `scripts/run_full_extraction.py` | Full extraction pipeline |

---

## Credence Formula Architecture (Four Layers)

The system uses different formulas at different levels. This is by design, not a bug.

**Layer 1 — Bridge Warrant Discount** (`bridge_warrants.py`):
```
P(effect | channel_i) = P(parent_theory) × P(bridge) × P(CNFA_specific)
```
Pure multiplicative. Each factor attenuates. Ceilings enforced per warrant type.

**Layer 2 — Multi-Channel Aggregation** (`warrant_scaling.py`):
```
P(composite) = 1 - Π(1 - credence_i)    [noisy-OR]
```
Independent channels combine. Rewards genuine convergence.

**Layer 3 — Warrant Combination** (`warrant_scaling.py`):
Coherence, argumentative, and vigilance warrants combine via noisy-OR with type-specific caps (0.55–0.75).

**Layer 4 — BN Confidence** (`graph_confidence_service.py`):
```
confidence = 0.4 × warrant_score + 0.3 × grounding_score + 0.3 × rank_score
```
Weighted linear for Pearl-compliant causal inference.

---

## Warrant Type Hierarchy (Canonical Ceilings)

| Type | Ceiling | Epistemic Justification |
|------|---------|------------------------|
| CONSTITUTIVE | 0.75 | True by system definition |
| MECHANISM | 0.60 | Known causal pathway |
| EMPIRICAL_COVARIANCE | 0.60 | Direct observational correlation |
| FUNCTIONAL | 0.50 | Functional organization argument |
| CAPACITY | 0.45 | Stable dispositional property |
| THEORETICAL_DEFAULT | 0.40 | Framework starting assumption |
| ANALOGICAL | 0.35 | Cross-domain structural similarity |

Source of truth: `bridge_warrants.py` DEFAULT_BRIDGE_CONFIDENCE dict.

---

## Overseer Invariants

| ID | Check | Source |
|----|-------|--------|
| INV-0 | System is OPERATIONAL | Bootstrap validation |
| INV-1 | Every belief has provenance | Haack (foundherentism) |
| INV-2 | BN edges reflect web credences | Pearl (causal inference) |
| INV-3 | All beliefs conform to ClaimV2 schema | Data integrity |
| INV-4 | Coherence decline ≤ 5% per integration | Dijkstra (invariant maintenance) |
| INV-5 | All credences in [0, 1] | Probability axioms |

---

## Theory Tiers

**Tier 1** — 10 canonical neuroscience frameworks:
PP (Predictive Processing), SN (Spatial Navigation), DP (Dual-Process), DT (DMN/TPN Dynamics), NM (Neuromodulatory Systems), IC (Interoceptive/Constructionist Affect), MS (Memory Systems), EC (Embodied Cognition), CB (Chronobiological Regulation), MSI (Multisensory Integration)

**Tier 1.5** — Domain theories formally reduced to T1 frameworks:
ART (Attention Restoration Theory → reduced to PP+SN), SRT (Stress Recovery Theory → reduced to NM+IC), Biophilia (→ reduced to multiple T1)

**Tier 2** — Empirical claims: extracted findings, bridge warrants, template instances

**Tier 3** — BN nodes: measurable variables with CPTs

---

## Data Flow

```
Scientific papers (PDFs)
    ↓
Paper Triage (classify article type)
    ↓
Gemini Extraction (type-specific prompts → claims, tables, metadata)
    ↓
Table Classification + Semantic Profiling
    ↓
Claim Generation (ae.claim.v1 format)
    ↓
Extraction-to-Web (claims → beliefs, rules → constraints)
    ↓
Paper Integration Orchestrator (14-step cascade)
    ↓
Web of Belief (beliefs, warrants, coherence)
    ↓  π (projection)
Bayesian Network (variables, causal edges, CPTs)
    ↓
Overseer (6 invariants, nightly audit)
    ↓
Streamlit Dashboard + API
```

---

## Database Files

The system uses SQLite databases in `data/`:
- `web.db` — Web of belief state
- `overseer.db` — Overseer health history
- `templates/` — JSON template files per panel/domain

---

## Related Documentation

| Document | Location | Content |
|----------|----------|---------|
| CMR Architecture Explanation | `docs/CMR_ARCHITECTURE_EXPLANATION.md` | Detailed architecture with credence formula derivation |
| WoB + BN Architecture | `docs/WEB_OF_BELIEF_AND_BAYESIAN_NETWORK_ARCHITECTURE (1).md` | Philosophical foundation |
| Schema Registry | `SCHEMA_REGISTRY.md` | Contract and schema index |
| Transfer Context | `docs/TRANSFER_Feb25_Session11_continued.md` | Latest session transfer document |
| Master Specification | `docs/MASTER_DOC_CMR_2026-02-25.md` | 19,000-line canonical specification |

---

## For AI Assistants

If you are an AI asked to work on this codebase:

1. Read this file first.
2. Read `CLAUDE.md` for task tracking, governance rules, and decision logging protocols.
3. Read `SCHEMA_REGISTRY.md` for data contract details.
4. Before modifying any formula or ceiling value, read `src/services/bridge_warrants.py` — it is the source of truth.
5. Before modifying the overseer, read `src/services/overseer.py` — it has 6 invariants that must not be violated.
6. Run `scripts/lint_bridge_ceilings.py` before and after any ceiling change.
7. All decisions must be logged per the protocol in `CLAUDE.md`.
