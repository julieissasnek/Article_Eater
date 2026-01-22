# Architecture Diagram

**Date**: January 22, 2026
**Version**: V21.0.0 (Post-Quinean)
**Purpose**: Visual documentation of system architecture (per Parnas, ruthless review 2026-01-22)

---

## 1. High-Level Data Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ARTICLE EATER V21.0.0                             │
│                              (Post-Quinean)                                 │
└─────────────────────────────────────────────────────────────────────────────┘

                                   INPUT
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            PDF CORPUS                                       │
│  Scientific articles from neuroarchitecture research                        │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      EXTRACTION LAYER (Track A)                             │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐         │
│  │   PDF Parser    │───▶│  Claim Extractor │───▶│  Rule Generator │         │
│  │   (PyMuPDF)     │    │   (LLM-based)    │    │   (Heuristics)  │         │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘         │
│                                                                             │
│  Output: claims.jsonl, rules.jsonl                                          │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      EPISTEMIC LAYER (Track B)                              │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                    extraction_to_web.py                               │  │
│  │              Claims → Beliefs mapper (Sprint 1)                       │  │
│  │   - Maps claim constructs to belief content                           │  │
│  │   - Determines source_depth from claim metadata                       │  │
│  │   - Sets initial credence based on evidence quality                   │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                     │                                       │
│                                     ▼                                       │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                     web_of_belief.py                                  │  │
│  │           THE KEY FILE - Quinean Coherentist Engine                   │  │
│  │                                                                       │  │
│  │   ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐          │  │
│  │   │   Belief    │  │  Credence   │  │ CoherenceConstraint │          │  │
│  │   │  (Entity)   │  │  (Value)    │  │    (Relation)       │          │  │
│  │   └─────────────┘  └─────────────┘  └─────────────────────┘          │  │
│  │                                                                       │  │
│  │   Features:                                                           │  │
│  │   - Belief storage and retrieval                                      │  │
│  │   - Coherence constraint management                                   │  │
│  │   - Equilibrium-seeking (optional)                                    │  │
│  │   - Credence propagation                                              │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                     │                                       │
│            ┌────────────────────────┼────────────────────────┐             │
│            │                        │                        │             │
│            ▼                        ▼                        ▼             │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐        │
│  │causal_classifier│    │bridge_warrants  │    │outcome_taxonomy │        │
│  │     .py         │    │     .py         │    │     .py         │        │
│  │                 │    │                 │    │                 │        │
│  │ Three-tier      │    │ Knowledge       │    │ CNFA outcome    │        │
│  │ classification  │    │ transfer        │    │ taxonomy        │        │
│  │                 │    │ warrants        │    │                 │        │
│  │ CAUSAL/         │    │                 │    │ behav./cog./    │        │
│  │ SUGGESTIVE/     │    │ MECHANISM/      │    │ affect./        │        │
│  │ ASSOCIATIONAL   │    │ FUNCTIONAL/     │    │ physio./health  │        │
│  │                 │    │ CAPACITY/etc    │    │                 │        │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘        │
│                                                                             │
│  Output: web_state.json, bridges.jsonl, stubs.jsonl, tensions.jsonl        │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         QUERY LAYER (Track D)                               │
│                                                                             │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐         │
│  │  query_parser   │───▶│query_response   │───▶│   reporting     │         │
│  │      .py        │    │      .py        │    │      .py        │         │
│  │                 │    │                 │    │                 │         │
│  │ NL → Intent     │    │ Intent →        │    │ Gap analysis    │         │
│  │ vocabulary      │    │ Response with   │    │ Quality reports │         │
│  │ expansion       │    │ evidence items  │    │ Summaries       │         │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘         │
│                                                                             │
│  Output: QueryResponse with follow-ups, contested evidence, scope          │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           API LAYER                                         │
│                                                                             │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐         │
│  │ app/routes/     │    │ app/routes/     │    │ app/routes/     │         │
│  │   query.py      │    │  reports.py     │    │  ingestion.py   │         │
│  │                 │    │                 │    │                 │         │
│  │ GET /query      │    │ GET /report     │    │ POST /ingest    │         │
│  │ POST /query     │    │ GET /gap        │    │ POST /paper     │         │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘         │
│                                                                             │
│  Framework: FastAPI                                                         │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
                                  OUTPUT
```

---

## 2. Service Dependencies

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        SERVICE DEPENDENCY GRAPH                             │
└─────────────────────────────────────────────────────────────────────────────┘

                        ┌──────────────────┐
                        │  query_parser    │
                        │                  │
                        │ Depends on:      │
                        │ - vocabulary_    │
                        │   bridge.py      │
                        └────────┬─────────┘
                                 │
                                 ▼
                        ┌──────────────────┐
                        │ query_response   │
                        │                  │◄──────────────────┐
                        │ Depends on:      │                   │
                        │ - web_of_belief  │                   │
                        │ - causal_        │                   │
                        │   classifier     │                   │
                        │ - query_parser   │                   │
                        └────────┬─────────┘                   │
                                 │                             │
                    ┌────────────┴────────────┐               │
                    │                         │               │
                    ▼                         ▼               │
          ┌──────────────────┐     ┌──────────────────┐      │
          │  web_of_belief   │     │causal_classifier │      │
          │                  │     │                  │      │
          │ Core data store  │     │ Pattern-based    │      │
          │ No dependencies  │     │ classification   │      │
          │ on other services│     │                  │      │
          └────────┬─────────┘     │ No dependencies  │      │
                   │               │ on other services│      │
                   │               └──────────────────┘      │
                   │                                          │
                   ▼                                          │
          ┌──────────────────┐                               │
          │   reporting      │───────────────────────────────┘
          │                  │
          │ Depends on:      │
          │ - web_of_belief  │
          │ - causal_        │
          │   classifier     │
          │ - outcome_       │
          │   taxonomy       │
          └──────────────────┘


          ┌──────────────────┐     ┌──────────────────┐
          │ bridge_warrants  │     │ outcome_taxonomy │
          │                  │     │                  │
          │ Independent      │     │ Independent      │
          │ module           │     │ module           │
          │                  │     │                  │
          │ Used by:         │     │ Used by:         │
          │ - pipeline       │     │ - reporting      │
          │ - reporting      │     │ - extraction     │
          └──────────────────┘     └──────────────────┘
```

---

## 3. Data Flow: Query Processing

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      QUERY PROCESSING PIPELINE                              │
└─────────────────────────────────────────────────────────────────────────────┘

User Query: "Does natural light improve cognitive performance?"
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 1: PARSE QUERY (query_parser.py)                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Input: "Does natural light improve cognitive performance?"                 │
│                                                                             │
│  Processing:                                                                │
│  1. Detect query type → CAUSATION                                           │
│  2. Extract terms → ["natural light", "cognitive performance"]              │
│  3. Expand vocabulary → ["daylight", "daylighting", "sunlight",            │
│                          "attention", "memory", "focus", "cognition"]       │
│  4. Detect constraints → None                                               │
│                                                                             │
│  Output: QueryIntent(                                                       │
│    query_type=CAUSATION,                                                    │
│    terms=["natural light", "cognitive performance"],                        │
│    expanded_terms=["daylight", "daylighting", ...],                         │
│    constraints={}                                                           │
│  )                                                                          │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 2: FIND RELEVANT BELIEFS (query_response.py)                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  For each belief in web.beliefs:                                            │
│    1. Check term match (original + expanded)                                │
│    2. Calculate relevance score                                             │
│    3. Apply threshold filter                                                │
│                                                                             │
│  Output: List[Belief] sorted by credence                                    │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 3: CLASSIFY CAUSAL TIER (causal_classifier.py)                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  For each relevant belief:                                                  │
│    1. Check experimental design → design-first approach                     │
│    2. Match causal patterns                                                 │
│    3. Match suggestive patterns                                             │
│    4. Match associational patterns                                          │
│    5. Check confounder mention                                              │
│    6. Check mechanism mention                                               │
│    7. Detect theoretical frameworks                                         │
│                                                                             │
│  Output: CausalClassification(tier, confidence, evidence_type, ...)         │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 4: DETECT CONTESTED EVIDENCE (query_response.py)                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. Group beliefs by causal direction (positive vs negative)                │
│  2. Check for directional opposition:                                       │
│     - High-credence evidence saying X increases Y                           │
│     - High-credence evidence saying X decreases Y                           │
│  3. If opposition found:                                                    │
│     - Identify reasons for disagreement                                     │
│       (measurement method, population, methodology)                         │
│     - Create ContestedEvidence section                                      │
│                                                                             │
│  Output: ContestedEvidence(supporting, contradicting, reasons)              │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 5: GENERATE RESPONSE (query_response.py)                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. Determine confidence level (HIGH/MEDIUM/LOW/UNKNOWN)                    │
│  2. Create evidence items (top 10)                                          │
│  3. Generate summary                                                        │
│  4. Create exactly 3 follow-ups:                                            │
│     - Deeper: "What mechanisms explain this effect?"                        │
│     - Scope: "Under what conditions does this hold?"                        │
│     - Uncertainty: "What are the key unknowns?"                             │
│  5. Include vocabulary used, warnings, scope conditions                     │
│                                                                             │
│  Output: QueryResponse(                                                     │
│    summary="...",                                                           │
│    evidence_items=[...],                                                    │
│    follow_ups=[...],                                                        │
│    contested_evidence=...,                                                  │
│    confidence_level="medium",                                               │
│    vocabulary_used=[...]                                                    │
│  )                                                                          │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Key Files Summary

| File | Lines | Purpose | Dependencies |
|------|-------|---------|--------------|
| `src/services/web_of_belief.py` | ~1300 | Core coherentist engine | None |
| `src/services/causal_classifier.py` | ~680 | Three-tier classification | None |
| `src/services/query_response.py` | ~750 | Response generation | web_of_belief, causal_classifier, query_parser |
| `src/services/query_parser.py` | ~400 | NL parsing, vocab expansion | vocabulary_bridge |
| `src/services/reporting.py` | ~850 | Gap analysis, reports | web_of_belief, causal_classifier, outcome_taxonomy |
| `src/services/bridge_warrants.py` | ~1000 | Knowledge transfer | None |
| `src/services/outcome_taxonomy.py` | ~500 | CNFA outcome hierarchy | None |
| `src/services/web_persistence.py` | ~600 | Web state persistence | web_of_belief |
| `src/services/extraction_to_web.py` | ~400 | Claims → Beliefs mapper | web_of_belief |

---

## 5. Schema Relationships

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          SCHEMA RELATIONSHIPS                               │
└─────────────────────────────────────────────────────────────────────────────┘

  ae.claim.v1.schema.json                    ae.web_state.v1.schema.json
  ┌───────────────────┐                      ┌───────────────────┐
  │ claim_id          │                      │ web_id            │
  │ statement         │──── extracts ───────▶│ beliefs[]         │
  │ constructs        │        to            │   belief_id       │
  │   outcomes[]      │                      │   content         │
  │   environments[]  │                      │   credence        │
  │ evidence_quality  │                      │   source_depth    │
  │ paper_id          │                      │   level           │
  └───────────────────┘                      │   scope           │
                                             │ constraints[]     │
                                             │ metadata          │
                                             └───────────────────┘
                                                      │
                                                      │ references
                                                      ▼
  ae.bridge.v1.schema.json                   ae.coherence_summary.v1.schema.json
  ┌───────────────────┐                      ┌───────────────────┐
  │ bridge_id         │                      │ timestamp         │
  │ source_domain     │                      │ coherence_score   │
  │ target_domain     │                      │ belief_count      │
  │ bridge_type       │──── connected ──────▶│ constraint_count  │
  │ confidence        │        via           │ stubs[]           │
  │ source_beliefs[]  │                      │ tensions[]        │
  │ target_beliefs[]  │                      └───────────────────┘
  │ evidence_for[]    │
  │ evidence_against[]│
  └───────────────────┘
```
