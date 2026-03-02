# QA System Specification — Article Eater Post-Quinean v1
**Date**: 2026-03-01  
**Author**: AG (Antigravity)  
**Status**: Draft for CW review  
**Purpose**: Complete inventory and integration analysis of the QA subsystem, identifying what exists, what's connected, what's missing, and where discovery opportunities lie.

> **For CW**: This document is AG's independent codebase analysis. CW should develop its own view and identify disagreements, additional integration points, or alternative priorities. This is meant to be a shared reference, not a prescriptive plan.

---

## Table of Contents
1. [Executive Summary](#1-executive-summary)
2. [Architecture Overview](#2-architecture-overview)
3. [The 9 QA Subsystems](#3-the-9-qa-subsystems)
4. [Integration Analysis](#4-integration-analysis)
5. [VOI System Status](#5-voi-system-status)
6. [Science-Writer Principles](#6-science-writer-principles)
7. [Nightly Pipeline & Discovery](#7-nightly-pipeline--discovery)
8. [Success Conditions](#8-success-conditions)
9. [Gap Analysis & Recommendations](#9-gap-analysis--recommendations)

---

## 1. Executive Summary

### What we have

The QA system is **9 subsystems spanning ~8,500 lines** across 15+ Python modules. Each subsystem is well-designed and does real work:

| Subsystem | What it does | Working? |
|-----------|-------------|----------|
| **Reflex System** (1525 lines) | 15 detect-fix-report checks for data hygiene (malformed JSON, vague antecedents, missing sample sizes) | ✅ Yes — reports to Overseer |
| **Warrant Service** (486 lines) | Pollock defeasible reasoning — computes WARRANTED/DEFEATED/SUSPENDED/UNGROUNDED for every belief | ✅ Yes — but not run nightly |
| **Gap Predictor** (1497 lines) | Predicts knowledge gaps from web structure + Mayo defeater search | ✅ Yes — but not run nightly |
| **VOI Scoring + Search** (2055 lines) | Scores findings by information value, multi-strategy cross-field search | ⚠️ Infra exists, no closed loop |
| **Source Quality** (319 lines) | Weighted composite: rigor, commitment, independence, replication | ✅ Yes |
| **Template QA** (247 lines) | Validates mechanism chains have warrants and match archetypes | ✅ Yes |
| **Argument QA** (219 lines) | Critique aggregation + evidence hierarchy queries | ✅ Yes |
| **QA Cache Manager** (120 lines) | Detects KB drift in molecule summaries | ✅ Yes |
| **CVA Enricher** (263 lines) | Enriches QA responses with CVA molecule analysis | ✅ Yes |

### What's missing: the connections between them

The individual subsystems are like **well-built organs that aren't wired together**:

1. **No QA component reads provenance** — Haack's JustificationStatus (WELL_JUSTIFIED / COHERENT_ONLY / UNJUSTIFIED) exists in the data model but nothing checks it. COHERENT_ONLY beliefs (coherent but not grounded in observation) are the most dangerous per Haack, and we don't flag them.

2. **No QA component reads annotations** — 10 annotation types exist (OPEN_QUESTION, SENSITIVITY_FLAG, SEARCH_PROMPT, etc.) but QA doesn't consume any of them. User-identified questions and sensitivity flags are invisible to the automated system.

3. **Rollback doesn't trigger QA** — When a paper is rolled back, beliefs can become UNGROUNDED silently. No reflex detects this, no warrant re-computation runs, AESHI isn't updated.

4. **No web UI exposes QA** — Users browsing beliefs see no warrant badges, no health indicators, no search integration. The ArgumentQueryHandler exists in Python but has no web binding.

5. **VOI doesn't affect health** — High-value unanswered gaps don't show up in AESHI. The system can have critical knowledge gaps and still score GREEN.

6. **Source quality doesn't feed credence** — SQ is computed but never fed back to belief strength. A belief based on a single weak study and a belief based on 10 meta-analyses can have the same credence.

### What this document is for

This document (a) inventories everything that exists, (b) traces how the parts do and don't connect, (c) proposes 22 success conditions across 5 tiers, and (d) prioritizes the gaps by effort and impact. The goal is to enable CW and AG to coordinate on which integrations to build next.

### The biggest opportunity

The nightly pipeline already runs 10 stages. Adding a **nightly discovery stage** (gap prediction → defeater search → annotation harvest → VOI re-scoring) would turn it from a maintenance job into a **learning loop** — every night the system identifies what it doesn't know and prioritizes what to read next.

---

## 2. Architecture Overview

The system has three tiers of ambition:

| Tier | Goal | Status |
|------|------|--------|
| **Tier 1 — Hygiene** | Catch malformed data, missing fields, schema drift | ✅ Working |
| **Tier 2 — Epistemic Integrity** | Warrant chain validity, defeat detection, unjustified belief flagging | ⚠️ Partially wired |
| **Tier 3 — Discovery** | Gap prediction, search prioritization, reading guidance | 🔶 Infrastructure exists, not fully integrated |

### System Map

```
┌─────────────────────────────────────────────────────────────────┐
│                     NIGHTLY PIPELINE                            │
│  backup → discovery → triage → extraction → QA gate →          │
│  auto-approve → integrate → web-health → health-check →        │
│  warrant-monitor → overseer-coverage → report                  │
└─────────────────────┬───────────────────────────────────────────┘
                      │ reports to
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    OVERSEER / AESHI                              │
│  INV-1..INV-9 → composite score → PASS/YELLOW/RED              │
└─────────────────────────────────────────────────────────────────┘
                      ▲
          ┌───────────┴────────────┐
          │                        │
┌─────────┴──────────┐  ┌─────────┴──────────┐
│  REFLEX SYSTEM     │  │  TEMPLATE QA       │
│  15 reflexes       │  │  mechanism chain   │
│  detect→fix→report │  │  warrant checks    │
└────────────────────┘  │  archetype match   │
                        └────────────────────┘

┌─────────────────────────┐    ┌────────────────────────┐
│  WARRANT SERVICE        │    │  ARGUMENT QA           │
│  Pollock defeasible     │    │  CritiqueAggregator    │
│  WARRANTED/DEFEATED/    │    │  HierarchyAggregator   │
│  SUSPENDED/UNGROUNDED   │    │  vulnerability profiles│
└─────────────────────────┘    └────────────────────────┘

┌─────────────────────────┐    ┌────────────────────────┐
│  GAP PREDICTOR          │    │  VOI SCORING + SEARCH  │
│  mediation/mechanism/   │    │  finding-level scoring │
│  boundary/direction     │    │  cross-field vocab     │
│  Mayo defeater search   │    │  discovery funnel      │
└─────────────────────────┘    └────────────────────────┘

┌─────────────────────────┐    ┌────────────────────────┐
│  SOURCE QUALITY         │    │  QA CACHE MANAGER      │
│  rigor/commitment/      │    │  KB drift detection    │
│  independence/replication│   │  L1/L2/L3 summaries    │
└─────────────────────────┘    └────────────────────────┘

┌───────────────────────────────────────────────────────┐
│  NOT YET CONNECTED TO QA:                              │
│  • Provenance (Haack foundherentism, JustificationStatus)  │
│  • Annotations (10 types, 3 layers)                    │
│  • Rollback (paper-level undo)                         │
│  • Web UI (no search frontend, no warrant badges)      │
└───────────────────────────────────────────────────────┘
```

---

## 3. The 9 QA Subsystems

### 3.1 Reflex System (Tier 1 — Data Hygiene)

**File**: `src/qa/reflex_system.py` (1525 lines)  
**Architecture**: Each `Reflex` is a (detect, fix, report) triple. `ReflexRegistry` runs all reflexes, logs events as JSONL, and reports to Overseer DB.

**15 concrete reflexes**:

| ID | Reflex | What It Detects | Auto-Fix? |
|----|--------|-----------------|-----------|
| RFX-EXT-DIR | DirectionNormalization | Non-canonical direction values (e.g., "up" instead of "increase") | ✅ Normalizes |
| RFX-EXT-ANT | VagueAntecedentDetector | Vague phrases like "the environment", "the condition" | ❌ Flags for re-extraction |
| RFX-EXT-SS | MissingSampleSize | Empirical findings with null/zero sample_size | ❌ Queues for LLM inference |
| RFX-EXT-JSON | MalformedExtractionJson | JSON parse errors in extraction files | ✅ Quarantines to subdirectory |
| RFX-EXT-EMPTY | ZeroFindingsExtraction | Extractions that produced zero findings | ❌ Queues for re-extraction |
| RFX-SCH-VOCAB | OrphanedVocabTerms | Vocab terms not referenced by any extraction | ❌ Monitors only |
| RFX-SCH-INST | BrokenInstrumentIdReferences | instrument_ids in vocab that don't match instrument registry | ❌ Manual review |
| RFX-SCH-LOOKUP | StaleLookupTable | Outcome lookup table out of sync with vocab | ✅ Regenerates |
| RFX-SCH-RANGE | OutOfRangeCalibrationParameters | Calibrated parameter values outside expected bounds | ❌ Flags |
| RFX-EXT-STALE | StaleExtractionFiles | Extraction files older than templates they reference | ❌ Queues for re-extraction |
| RFX-COV-T2 | Tier2Coverage | Templates without sufficient T2-level coverage | ❌ Reports coverage gaps |
| RFX-COV-ANN | AnnotationPersistence | Annotations that failed to persist to DB | ✅ Re-persists |
| RFX-COV-FW | FrameworkLoading | Framework files that fail to load | ❌ Flags broken frameworks |
| RFX-COV-ENV | EnvOutcomeBackfill | Missing environment→outcome mappings | ✅ Backfills from templates |
| RFX-COV-INLINE | InlineTier2Data | Templates with inline T2 data instead of references | ❌ Flags for migration |

**Severity levels**: INFO, WARNING, ERROR, CRITICAL  
**Reporting**: Each reflex event has a unique ID, timestamp, severity, and goes to:
1. Daily JSONL log in `logs/reflexes/`  
2. Overseer SQLite database  
3. AESHI health scoring

---

### 3.2 Template Quality Assurance (Tier 1/2)

**File**: `src/services/template_quality_assurance.py` (247 lines)

Validates T2 templates against archetype registry. Checks:
1. `mechanism_chain` exists with ≥1 step
2. Each step has justification with **warrant** ← *primary warrant check on templates*
3. Mechanism text matches known archetypes (fuzzy matching)
4. Referenced `template_ids` are valid cross-references

Output: `QAReport` per template with `passed`, `warnings`, `errors`, `matched_archetypes`.

---

### 3.3 Argument QA Handler (Tier 2)

**File**: `src/argument/qa_handlers.py` (219 lines)

Handles natural-language queries routing to argument structure:
- **"What critiques exist for X?"** → `CritiqueAggregator` → method/stimulus/population/assumption/interpretation/statistical critiques → vulnerability profile
- **"How strong is evidence for X?"** → `HierarchyAggregator` → pairwise comparisons, ordered levels, evidence strength, validation verdict

Uses `template_hierarchy_registry` for target resolution and alias normalization.

Output: Structured JSON responses with `ae.query_response.v1` schema.

---

### 3.4 Warrant Service — Pollock Defeasible Logic (Tier 2)

**File**: `src/services/warrant_service.py` (486 lines)

Implements Pollock's defeasible reasoning. Stateless: web state + ranks → warrant status.

**5 warrant statuses**:
| Status | Meaning |
|--------|---------|
| WARRANTED | Has support, no undefeated defeaters |
| DEFEATED | Has a warranted defeater (rebutting or undercutting) |
| SUSPENDED | In a defeat cycle (mutual defeat) |
| UNGROUNDED | No support chain at all |
| UNCHECKED | Not yet analyzed |

**2 defeat types**: REBUTTING (conclusion denied), UNDERCUTTING (inference rule attacked)

**Algorithm**: Recursive reinstatement with cycle detection.
1. Check prima facie warrant (has supporters OR is observational)
2. For each defeater D of B: if D is warranted (recursive), B is defeated
3. For each reinstater R of D: if R is warranted, D is defeated → B reinstated
4. Cycle detection at depth > 3 visits → SUSPENDED

**Consistency invariant**: INV-1: ¬(warranted(B) ∧ warranted(rebutter(B)))

**Key panel references**: Pollock (defeasible logic), panel consultation 2026-02-12.

---

### 3.5 Source Quality (Tier 2)

**File**: `src/epistemic/source_quality.py` (319 lines)

Weighted composite of 4 components:

| Component | Weight | Description |
|-----------|--------|-------------|
| Methodological rigor | 0.40 | Study design quality |
| Theoretical commitment | 0.20 | Potential for confirmatory bias (penalized by study type) |
| Independence of evidence | 0.20 | How independent the evidence sources are |
| Replication status | 0.20 | Whether findings have been replicated |

**Study-type commitment penalty** (per Mayo/Longino):
- Confirmatory: full penalty (1.0×)
- Exploratory: half penalty (0.5×)
- Replication: zero penalty (0.0×)
- Meta-analysis: quarter penalty (0.25×)

Output: `SourceQualityResult` with composite score, component contributions, and categorical quality level (high/moderate/low).

---

### 3.6 Gap Predictor (Tier 3 — Discovery)

**File**: `src/services/gap_predictor.py` (1497 lines)

Predicts knowledge gaps from argument structure in the epistemic web.

**4 gap types** (per Panel P-LAYER):

| Gap Type | Pattern | Example |
|----------|---------|---------|
| Mediation | A→X→Y exists but direct A→Y missing | Light → circadian → mood, but no direct light → mood study |
| Mechanism | Effect established but no mechanism chain | Ceiling height affects creativity, but how? |
| Boundary | Untested settings or populations | Only tested in offices — what about hospitals? |
| Direction | Conflicting results across studies | Some say increase, others decrease |

**Defeater search** (per Mayo, panel 2026-02-12): "For each belief, actively seek disconfirming evidence." Searches for:
- Contradicting beliefs in the web
- Findings with "limitation", "fails to replicate", "boundary condition" language
- Categorizes defeaters by type (methodological, theoretical, empirical, boundary)

**Output**: `PredictedGap` with:
- Gap type & description
- Affected BN edges/beliefs
- VOI score for prioritization
- Suggested search queries
- Resolution approach
- Confidence rating

**Local evidence search**: Before suggesting external search, checks:
1. Extracted findings in `data/extracted_findings/`
2. Existing beliefs that match via keywords
3. Unprocessed papers in extraction queue

---

### 3.7 VOI Scoring (Tier 3)

**File**: `src/cmr/voi_scoring.py` (109 lines)

Scores individual findings by value-of-information:

| Assessment | Calibrated | Uncalibrated | Rationale |
|------------|-----------|--------------|-----------|
| Contradiction | 1.0 | 0.7 | Contradictions of well-calibrated beliefs are highest value |
| Gap (large ES) | 0.8 | 0.8 | Large-effect gaps are high priority |
| Gap (small ES) | 0.4 | 0.4 | Small-effect gaps are lower priority |
| Extension | 0.6 | 0.6 | Extensions add moderate value |
| Confirmation (uncalibrated) | — | 0.5 | Confirms something poorly calibrated — useful |
| Confirmation (calibrated) | 0.2 | — | Confirms something already established — low value |

**Buckets**: high (≥0.8), medium (≥0.5), low (<0.5)

`aggregate_paper_voi()`: Mean VOI across findings → paper-level expected information gain.

---

### 3.8 VOI Search (Tier 3)

**File**: `src/services/voi_search.py` (1946 lines)

Multi-strategy search infrastructure:

- **Gap type classification**: Canonical types (validation, mechanism, direction, boundary) with legacy aliases
- **Cross-field vocabulary**: Translates CNfA concepts to adjacent field terminology (neuroscience, architecture, psychology, etc.) for broader literature search
- **Query expansion**: `expand_query()` finds synonyms across target fields (max 5 terms per expansion)
- **Discovery funnel integration**: Optional integration with `DiscoveryFunnelService` for systematic gap tracking
- **Epsilon-decay strategy selection**: Balances exploitation (known good sources) vs exploration (new sources)
- **Stopping rules**: Infrastructure exists for null-result detection and search termination

---

### 3.9 QA Cache Manager (Infrastructure)

**File**: `src/qa/qa_cache_manager.py` (120 lines)

Tracks KB drift by hashing dependent templates per molecule:
- Computes composite hash of all templates a molecule depends on
- If hash changes after integration → marks molecule summary as STALE
- Progressive disclosure summaries: L1 (headline), L2 (paragraph), L3 (full detail)
- `notify_qa_system()`: Placeholder for event queue / LLM re-computation trigger

---

### 3.10 CVA QA Enricher (Infrastructure)

**File**: `src/services/cva_qa_enricher.py` (263 lines)

Detects CVA-relevant topics in queries (beauty, restoration, cultural, safety) and enriches QA responses with:
- Relevant CVA molecule analysis
- Feature ↔ CVA mapping
- CVA-specific follow-up questions

---

## 4. Integration Analysis

### 4.1 What's Connected

| From | To | How |
|------|----|-----|
| Reflex System | Overseer | Each reflex event → overseer.db → AESHI scoring |
| Template QA | Warrant Service | Checks mechanism chain steps have warrants |
| Argument QA | CritiqueAggregator | Routes critique queries to vulnerability profiling |
| Argument QA | HierarchyAggregator | Routes evidence queries to pairwise comparison |
| Gap Predictor | VOI Scoring | Scores predicted gaps for prioritization |
| Gap Predictor | VOI Search | Feeds gaps → suggested search queries |
| QA Cache Manager | Nightly pipeline | Detects KB drift in molecule summaries |

### 4.2 What's NOT Connected

| Gap | Details | Impact |
|-----|---------|--------|
| **Rollback → QA** | When a paper is rolled back, no QA recheck runs. Beliefs can become UNGROUNDED silently. No reflex detects this. | Beliefs may lose all supporting evidence without any system awareness |
| **Provenance → QA** | Haack JustificationStatus (WELL_JUSTIFIED / COHERENT_ONLY / UNJUSTIFIED) exists but zero QA components read it. ExperientialClaim anchors ignored. | QA can't distinguish evidence quality by grounding depth |
| **Annotations → QA** | 10 annotation types across 3 layers. OPEN_QUESTION could feed gap predictor. SENSITIVITY_FLAG could trigger warrant review. SEARCH_PROMPT could route to VOI search. None of these work. | User-created knowledge signals (annotations) are invisible to automated QA |
| **Web UI → QA** | No TypeScript/React search components. No warrant badges on beliefs. No QA overlays on BN nodes. ArgumentQueryHandler has no web binding. | Users have no visibility into epistemic health of beliefs they're browsing |
| **VOI → AESHI** | High-value gaps don't affect system health score | Gap backlog is invisible to health monitoring |
| **Source Quality → Credence** | SQ computed but not fed back to belief credence | Evidence quality doesn't influence belief strength |
| **CVA → Gap Predictor** | CVA molecules aren't checked for gap coverage | Molecule-level gaps invisible |
| **Warrant Service → Reflex System** | No reflex checks whether warrant computation has run or if beliefs are DEFEATED | Defeated beliefs invisible to automated health system |

### 4.3 Annotation System Detail

The annotation service (`src/services/annotation_service.py`, 634 lines) provides:

**10 annotation types across 3 layers:**

| Layer | Type | Description | QA Uses It? |
|-------|------|-------------|-------------|
| Evidence | CALIBRATION_NOTE | Notes on calibration quality | ❌ |
| Evidence | SENSITIVITY_FLAG | Parameter sensitivity warning | ❌ |
| Evidence | EVIDENCE_OVERRIDE | Manual evidence correction | ❌ |
| Evidence | PROVENANCE_PATCH | Provenance corrections | ❌ |
| Relational | CROSS_REFERENCE | Links between entities | ❌ |
| Relational | MOLECULE_LINK | Links to CVA molecules | ⚠️ CVA enricher |
| Relational | CLINICAL_CAUTION | Clinical safety warnings | ❌ |
| QA/User | OPEN_QUESTION | User-identified questions | ❌ |
| QA/User | SEARCH_PROMPT | Suggested search queries | ❌ |
| QA/User | USER_FEEDBACK | User corrections/comments | ❌ |

**Valid annotation targets**: template, belief, answer, causal_link, parameter, molecule, theory

**Capabilities not exploited**: Full-text search (`search_annotations`), supersession versioning, parameter sensitivity flags (`get_parameter_sensitivity_flags`).

### 4.4 Provenance System Detail

The provenance model (`src/models/provenance.py`, 613 lines) implements Haack's foundherentism:

| Component | Description | QA Uses It? |
|-----------|-------------|-------------|
| JustificationStatus | WELL_JUSTIFIED / GROUNDED_ONLY / COHERENT_ONLY / UNJUSTIFIED | ❌ |
| ExperientialClaim | Anchor claims grounded in observation; `is_anchor()` method | ❌ |
| Directness | DIRECT / ONE_HOP / MULTI_HOP / THEORETICAL | ❌ |
| SourceType | PAPER / OBSERVATION / INFERENCE / THEORY / EXPERT_JUDGMENT / META_ANALYSIS | ❌ |
| Revisability | VERY_LOW / LOW / MODERATE / HIGH | ❌ |
| Observer | Type, expertise, training, reliability rating | ❌ |
| QuantitativeResult | Value, statistic type, CI, p-value, sample size | ❌ |

**Per Haack**: COHERENT_ONLY beliefs (coherent with web but not grounded in observation) are the most dangerous — they can be entirely circular. QA should flag these.

### 4.5 Rollback System Detail

`IntegrationRollback` (`src/services/paper_integration/rollback.py`, 424 lines) provides paper-level undo:

**Cascade steps**:
1. `_remove_beliefs()` — removes or decrements multi-paper beliefs
2. `_remove_constraints()` — removes contributed constraints  
3. `_remove_tags()` — removes tag assignments
4. `_remove_belief_versions()` — marks versions non-current
5. `_rollback_supersessions()` — reverts supersession records
6. `_mark_event_rolled_back()` — audit trail

**What should happen post-rollback but doesn't**:
- Re-run warrant computation for affected beliefs
- Check for newly-UNGROUNDED beliefs
- Update AESHI
- Create SENSITIVITY_FLAG annotations for impacted beliefs
- Alert overseer if high-credence beliefs affected

---

## 5. VOI System Status

| Component | File | Lines | Status |
|-----------|------|-------|--------|
| VOI Scoring | `src/cmr/voi_scoring.py` | 109 | ✅ Working — scores findings, aggregates paper VOI |
| VOI Search | `src/services/voi_search.py` | 1946 | ⚠️ Infrastructure — multi-strategy, cross-field vocab, funnel, stopping rules — but no closed loop |
| Gap Predictor | `src/services/gap_predictor.py` | 1497 | ✅ Working — 4 gap types + Mayo defeater search |
| Tests | 3 test files | — | Exist but not recently verified |

### What VOI can do now:
- Score individual findings by information value (assessment × calibration × effect size)
- Aggregate paper-level VOI summaries
- Predict gaps from web structure (4 types)
- Generate search queries for predicted gaps
- Expand queries across fields via cross-field vocabulary
- Search for defeaters against high-credence beliefs (Mayo principle)
- Check local corpus before suggesting external search

### What VOI can't do yet:
- **Closed-loop search**: Execute searches → integrate results → re-score (manual steps required)
- **Budget-aware prioritization**: No "cost" model for search effort vs expected information gain
- **Stopping rules exercised**: Infrastructure exists in `voi_search.py` but not run end-to-end
- **VOI → AESHI**: High-value unanswered gaps don't affect health score
- **Nightly VOI re-scoring**: After each integration cycle, search priorities should shift but don't

---

## 6. Science-Writer Principles

The following epistemic principles are embedded in the codebase as design constraints:

| Principle | Source | Where Implemented | Formalization |
|-----------|--------|-------------------|---------------|
| Defeasible reasoning | Pollock | `warrant_service.py` — defeat chains, reinstatement, cycle detection | ✅ Algorithmic |
| Foundherentism | Haack | `provenance.py` — JustificationStatus, ExperientialClaim, anchor detection | ✅ Data model (not consumed by QA) |
| Confirmation bias guard | Mayo (severe testing) | `gap_predictor.py` — "actively seek disconfirming evidence" | ⚠️ Method exists, not nightly |
| Independence of evidence | Longino | `source_quality.py` — independence weight (0.20) | ✅ Scored |
| Commitment penalty | Mayo/Longino | `source_quality.py` — study-type-dependent penalty | ✅ Scored |
| Progressive disclosure | — | `qa_cache_manager.py` — L1/L2/L3 summaries | ⚠️ Cache exists, summaries not generated |
| Vulnerability profiling | — | `critique_aggregator.py` — 6 critique categories | ✅ Aggregated |
| Evidence hierarchy | — | `hierarchy_evidence.py` — pairwise comparisons, ordered levels | ✅ Aggregated |

**Important**: These principles live in the code's DNA (docstrings, variable naming, algorithm choices) but are **NOT codified as a separate checkable specification**. There is no `principles.md` that can be audited against.

---

## 7. Nightly Pipeline & Discovery

### 7.1 Current Nightly Pipeline

**File**: `scripts/nightly_integration_pipeline.py` (770 lines)

10 stages running sequentially:

| Stage | Name | What It Does | QA Relevant? |
|-------|------|-------------|-------------|
| 1 | Backup | Back up all critical databases | Infrastructure |
| 2 | Discovery | Check for new articles via acquisition pipeline | Feed-in |
| 3 | Triage | Triage new articles in extraction queue | Feed-in |
| 4 | Extraction | Check extraction queue status | Feed-in |
| 5 | **QA Quality Gate** | Validate extractions against 50+ field rules, flag articles below 0.75 quality | ✅ |
| 6 | Auto-Approve | Auto-approve extractions meeting thresholds (≥5 findings, confidence ≥0.7) | Gatekeeping |
| 7 | Integration | Run SystemSetup.setup() for bulk integration | Core |
| 8 | Web Health | Connect isolated beliefs via safe_improve_web_health | Remediation |
| 9 | **Health Check** | Run full health check gauntlet | ✅ |
| 10 | **Warrant Monitor** | Check warrant type distribution across all extractions | ✅ |
| 11 | **Overseer Coverage** | Run INV-6..INV-9, compute AESHI composite score | ✅ |
| 12 | Report | Generate nightly report | Output |

### 7.2 What the Nightly Pipeline DOESN'T Do (Discovery Opportunities)

| Missing Stage | What It Would Do | Why It Matters |
|---------------|------------------|----------------|
| **Warrant computation** | Run WarrantService on all beliefs post-integration | Detect newly DEFEATED/UNGROUNDED beliefs from tonight's data |
| **Gap predictor** | Run GapPredictor on updated web | Discover what new gaps opened after tonight's integrations |
| **Defeater search** | Search for defeaters against high-credence beliefs | Mayo principle: actively seek disconfirming evidence |
| **Provenance review** | Check JustificationStatus changes | Detect beliefs that became COHERENT_ONLY (dangerous per Haack) |
| **Annotation harvest** | Consume OPEN_QUESTION + SEARCH_PROMPT annotations | Turn user-identified questions into systematic searches |
| **VOI re-scoring** | Re-score all gaps after new data | Update search priorities based on what we learned tonight |
| **Pattern learning** | Analyze reflex firing patterns over time | "3 papers from lab X all have vague antecedents → investigate methods" |

### 7.3 Proposed Nightly Discovery Stage

A new stage (between Health Check and Report) could run:

```
stage_nightly_discovery():
    1. Run gap predictor on updated web → new PredictedGap objects
    2. Run defeater search for beliefs with credence ≥ 0.8
    3. Harvest OPEN_QUESTION annotations as user-guided gaps
    4. Re-score VOI with new data → update search priorities
    5. Compare tonight's reflex patterns to last 7 days → flag anomalies
    6. If any high-VOI gaps emerged → queue for next discovery cycle
    7. Generate discovery digest: "Tonight we learned X, this opens Y"
```

This would turn the nightly pipeline from a **maintenance job** into a **learning loop**.

---

## 8. Success Conditions

### Tier 1 — Hygiene (reflex-level)
- [ ] **SC-QA-01**: All 15 reflexes run without error and report to overseer
- [ ] **SC-QA-02**: Zero malformed JSON files in `data/extractions/`
- [ ] **SC-QA-03**: All template mechanism chains have ≥1 warrant
- [ ] **SC-QA-04**: QA cache staleness detected within 1 extraction cycle

### Tier 2 — Epistemic Integrity
- [ ] **SC-QA-05**: Warrant computation runs on all beliefs; zero UNCHECKED remain
- [ ] **SC-QA-06**: Zero INV-1 violations (warranted belief + warranted rebutter)
- [ ] **SC-QA-07**: Source quality computed for all integrated papers
- [ ] **SC-QA-08**: DEFEATED beliefs flagged in query responses
- [ ] **SC-QA-09**: Provenance COHERENT_ONLY beliefs flagged (Haack warning)

### Tier 3 — Integration
- [ ] **SC-QA-10**: Rollback triggers QA recheck of affected beliefs
- [ ] **SC-QA-11**: OPEN_QUESTION annotations feed into gap predictor
- [ ] **SC-QA-12**: SENSITIVITY_FLAG annotations consumed by template QA
- [ ] **SC-QA-13**: Provenance JustificationStatus used in AESHI health scoring
- [ ] **SC-QA-14**: Web UI shows warrant status badges on beliefs

### Tier 4 — Discovery
- [ ] **SC-QA-15**: Gap predictor runs nightly on updated web
- [ ] **SC-QA-16**: High-VOI gaps (≥0.8) have suggested search queries
- [ ] **SC-QA-17**: Nightly defeater search for beliefs with credence ≥ 0.8
- [ ] **SC-QA-18**: Nightly annotation harvest → gap queue
- [ ] **SC-QA-19**: VOI re-scores after each integration cycle

### Tier 5 — Science Writer Principles
- [ ] **SC-QA-20**: Formal principles document exists and is auditable
- [ ] **SC-QA-21**: Independence scores available for all multi-study calibrations
- [ ] **SC-QA-22**: Commitment penalty applied by study type for all source quality scores

---

## 9. Gap Analysis & Recommendations

### Priority Matrix

| Gap | Impact | Fix Effort | Recommendation |
|-----|--------|------------|----------------|
| Warrant Service → Reflex | DEFEATED beliefs invisible to health | **Low** | Add `WarrantStatusReflex` checking for UNCHECKED/DEFEATED beliefs |
| Rollback → QA recheck | Silent belief degradation | **Medium** | Post-rollback hook calling warrant re-computation for affected IDs |
| Provenance → AESHI | Grounding quality ignored | **Medium** | Add % WELL_JUSTIFIED as AESHI component |
| Annotations → Gap Predictor | User knowledge signals lost | **Low** | Harvest OPEN_QUESTION in nightly discovery stage |
| VOI → AESHI | Gap backlog invisible | **Low** | Add "unanswered high-VOI gaps" as AESHI component |
| Web UI warrant badges | No user visibility | **Medium** | Add warrant status to belief API response |
| Nightly discovery stage | No learning loop | **Medium** | Implement `stage_nightly_discovery()` per Section 7.3 |
| Science-writer principles doc | Can't audit compliance | **Low** | Extract principles from code into `docs/EPISTEMIC_PRINCIPLES.md` |
| Source Quality → Credence | Evidence quality doesn't influence belief strength | **Medium** | Feed SQ composite into credence update formula |
| Closed-loop VOI search | Gaps identified but not pursued | **High** | Requires search execution + integration automation |

### Quick Wins (Low effort, high value)
1. **WarrantStatusReflex** — add one reflex class (~50 lines) to detect UNCHECKED/DEFEATED
2. **Annotation harvest** — `gap_predictor.harvest_annotations()` reading OPEN_QUESTION
3. **VOI → AESHI** — add high-VOI gap count to AESHI formula
4. **Principles document** — extract from docstrings into `docs/EPISTEMIC_PRINCIPLES.md`

### Medium-Term (architectural integration)
5. **Rollback → QA hook** — post-rollback warrant re-computation
6. **Provenance → AESHI** — JustificationStatus as health metric  
7. **Nightly discovery stage** — the learning loop
8. **Source Quality → Credence feedback** — SQ influences belief strength

### Long-Term (system capability)
9. **Closed-loop VOI search** — automated gap → search → integrate → re-score
10. **Web UI QA overlay** — warrant badges, health indicators, search integration

---

*Document prepared for CW review. AG's analysis is based on direct codebase inspection of all referenced files as of 2026-03-01.*
