# System Inventory: CNfA Evidence Pipeline

**Date**: 2026-02-11
**Purpose**: Document all components before MVP integration
**Status**: Pre-MVP Review (COMPLETE)

---

## Executive Summary

The CNfA (Cognitive Neuroarchitecture for Affect) research platform consists of **6 interconnected repositories** serving two parallel tracks:

1. **Text Track**: Papers → Rules → Beliefs → Epistemic Web → Queries
2. **Image Track**: Photos → Features → Bayesian Network → Predictions

Both tracks share vocabulary through **Outcome_Contractor** (effect side) and **Tagging_Contractor** (cause side).

---

## Repository Map (Complete)

```
/Users/davidusa/REPOS/
├── Article_Finder_v3_2_3/           # Paper collection & storage (16K papers)
├── Article_Eater_PostQuinean_v1/    # Extraction & epistemic web (Quinean engine)
├── Outcome_Contractor/               # Human-side vocabulary (outcomes/effects)
├── Tagging_Contractor/               # Environment-side vocabulary (424 tags)
├── BN_graphical/                     # Image→psychology Bayesian network
└── _Collecting Articles/             # Zotero exports

/Users/davidusa/Documents/___NEW AI PROJECTS/IMAGE TAGGER/
└── _Image-tagger-main_Taggert/       # Image feature extraction (v3.4.74)
```

---

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           TEXT TRACK (Literature)                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐      │
│  │ Article_Finder   │───>│ Article_Eater    │───>│ Epistemic Web    │      │
│  │ (16K papers)     │    │ (extraction)     │    │ (beliefs)        │      │
│  └──────────────────┘    └──────────────────┘    └────────┬─────────┘      │
│                                                            │                 │
│                                                            ▼                 │
│                                                  ┌──────────────────┐       │
│                                                  │ Query Engine     │       │
│                                                  │ (inference)      │       │
│                                                  └──────────────────┘       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                     ┌────────────────┴────────────────┐
                     │     SHARED VOCABULARY LAYER     │
                     ├─────────────────────────────────┤
                     │  ┌───────────────────────────┐  │
                     │  │ Outcome_Contractor        │  │
                     │  │ (effect side: 7 domains)  │  │
                     │  └───────────────────────────┘  │
                     │  ┌───────────────────────────┐  │
                     │  │ Tagging_Contractor        │  │
                     │  │ (cause side: 424 tags)    │  │
                     │  └───────────────────────────┘  │
                     └─────────────────────────────────┘
                                      │
┌─────────────────────────────────────────────────────────────────────────────┐
│                           IMAGE TRACK (Visual)                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐      │
│  │ Image_Tagger     │───>│ Feature Vectors  │───>│ BN_graphical     │      │
│  │ (CV + VLM)       │    │ (424 attributes) │    │ (causal model)   │      │
│  └──────────────────┘    └──────────────────┘    └──────────────────┘      │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 1. Article Finder (Paper Database)

**Path**: `/Users/davidusa/REPOS/Article_Finder_v3_2_3/`
**Purpose**: Collect, store, and manage scientific papers for CNfA research
**Status**: ACTIVE, MATURE

### Database
- **Location**: `data/article_finder.db` (SQLite)
- **Papers**: 16,073 total
- **With PDFs**: 1,111
- **On-topic**: 4,927
- **HBE foundational**: 123

### Key Tables
```sql
papers (
  paper_id, doi, title, authors, year, venue, publisher, abstract,
  pdf_path, source, status, topic_decision, topic_category,
  ae_status, ae_n_claims, ae_n_rules, extended_notes, ...
)
```

### Existing Integration Code
```
eater_interface/
├── invoker.py          # EaterInvoker class - calls AE CLI
├── job_bundle.py       # Creates input bundles for AE
├── job_bundle_v2.py    # Updated bundle format
├── output_parser.py    # Parses AE output
├── output_parser_v2.py # Updated parser
└── pipeline.py         # AF→AE pipeline orchestration
```

### Key Classes
- `EaterInvoker` - Invokes `article_eater eat` command
- `JobBundle` / `JobBundleV2` - Creates paper packages for AE
- `OutputParser` / `OutputImporter` - Parses AE results back to AF

---

## 2. Article Eater (Extraction & Epistemic Engine)

**Path**: `/Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/`
**Purpose**: Extract evidence from papers, build Quinean web of belief
**Version**: V23.0.0 (Emergent Entrenchment)
**Status**: ACTIVE, MATURE

### Database
- **Location**: `ae.db` (SQLite)
- **Rules**: 115
- **Theories**: ART, SRT, PAD, etc. (populated via theory_bootstrap.py)

### Core Services (`src/services/`)

| File | Lines | Purpose | Sprint |
|------|-------|---------|--------|
| `web_of_belief.py` | ~2000 | Core Quinean engine - Belief, Constraint, WebOfBelief | Core |
| `extraction_to_web.py` | ~500 | Claims → Beliefs mapper | Sprint 1 |
| `epistemic_causal_bridge.py` | ~2000 | Quinean→Pearlian bridge | Sprint 1.5 |
| `social_epistemology.py` | ~1300 | Community-relative credence | Sprint 2.5 |
| `bridge_warrants.py` | ~400 | Knowledge transfer bridges | Sprint 3 |
| `outcome_taxonomy.py` | ~300 | Outcome classification | Sprint 4 |
| `web_persistence.py` | ~400 | Save/load web state | Sprint 5 |
| `environment_taxonomy.py` | ~300 | Environment classification | Sprint 7 |
| `validation.py` | ~400 | Validation phases | Sprint 8 |
| `gold_standard.py` | ~300 | Gold standard corpus | Sprint 9 |
| `voi_search.py` | ~400 | VOI-driven search | Future |

### Pipeline (`app/tasks/pipeline.py`)
- Main extraction pipeline
- Calls `integrate_extraction()` from extraction_to_web
- Outputs: claims.jsonl, rules.jsonl, web_state.json, stubs.jsonl, tensions.jsonl

### Contracts/Schemas

| Schema | Purpose |
|--------|---------|
| `ae.claim.v1.schema.json` | Extracted claims |
| `ae.rule.v1.schema.json` | Rules for BN |
| `ae.web_state.v1.schema.json` | **Web of belief state (key for MVP!)** |
| `ae.bridge.v1.schema.json` | Bridge warrants |
| `social_epistemology.v1.schema.json` | Community credence |

---

## 3. Outcome_Contractor (Human-Side Vocabulary)

**Path**: `/Users/davidusa/REPOS/Outcome_Contractor/`
**Purpose**: Canonical authority for outcome/effect vocabulary (the "Y" in X→Y)
**Version**: 1.0.0
**Status**: ACTIVE, MATURE

### Core Function
Manages the controlled vocabulary for human outcomes that architectural features can influence. Serves as shared vocabulary backbone for Article Eater, Article Finder, and BN_graphical.

### Database
- **Location**: `data/outcome_contractor.db` (SQLite)
- **Tables**: terms, cognates, operationalizations, candidates, changes
- **Size**: ~1.1 MB

### 7 Outcome Domains

| Domain | Code | Examples |
|--------|------|----------|
| Cognitive | `cog` | attention, memory, executive function |
| Affective | `affect` | mood, emotion, stress, anxiety |
| Behavioral | `behav` | productivity, sleep, energy |
| Social | `social` | collaboration, isolation, interaction |
| Physiological | `physio` | heart rate, cortisol, HPA axis |
| Neural | `neural` | connectivity, oscillations, EEG |
| Health | `health` | life satisfaction, quality of life |

### Key Exports (`contracts/oc_export/`)

| File | Consumer | Size |
|------|----------|------|
| `outcome_vocab.json` | Canonical full vocabulary | ~321 KB |
| `ae_outcome_lookup.json` | Article Eater (flat lookup) | ~247 KB |
| `af_outcomes_taxonomy.yaml` | Article Finder (hierarchical) | ~209 KB |
| `bn_outcome_nodes.json` | BN_graphical (node definitions) | ~504 KB |
| `constitutive_bridges.json` | Definitional relationships | ~758 KB |

### Contract Philosophy
- **Frozen Core** (`core.v1.schema.json`): Minimum fields that never change
- **Consumer Needs Files**: Each consumer declares what they need
- **Extensions Field**: Reserved for forward-compatible additions

### Integration Points
- **Article Eater**: Resolves extracted outcome text → canonical term_id
- **Article Finder**: Populates outcomes facet in search UI
- **BN_graphical**: Outcomes become effect nodes in causal graph

---

## 4. Tagging_Contractor (Environment-Side Vocabulary)

**Path**: `/Users/davidusa/REPOS/Tagging_Contractor/`
**Purpose**: Semantic contracts for built-environment features (the "X" in X→Y)
**Version**: v0.2.8
**Status**: ACTIVE, MATURE

### Core Function
Defines what each architectural tag means, how it should be extracted, and what evidence is required. The "semantic contract layer" for perception research.

### Registry
- **Location**: `core/trs-core/v0.2.8/registry/registry_v0.2.8.json`
- **Total Tags**: 424
- **Categories**: 419 environmental, 5 preference/affect
- **By Extractability**: 56% from 2D, 41% partial, 3% no

### Tag Structure
```yaml
tag_id: "affect.cozy"
canonical_name: "Cozy"
domain: "Affect"
definition: "Perceived affective response..."
value_type: "binary" | "continuous" | "categorical"
extractability:
  from_2d: "yes" | "partial" | "no"
  from_3d_vr: "yes" | "partial" | "no"
semantics:
  aliases: ["cozy feeling", ...]
  disambiguation: {context_hints, exclusions, ...}
  factor_associations: ["comfort_affect"]
bn:
  evidence_role: "stimulus_antecedent" | "latent" | "outcome"
literature:
  search_terms: [...]
  key_refs: [...]
```

### Consumer Contracts (`contracts/`)

| Contract | Consumer | Tags |
|----------|----------|------|
| `image_tagger_contract_v0.2.8.json` | Image Tagger | ~400 |
| `article_eater_contract_v0.2.8.json` | Article Eater | ~200 |
| `bn_contract_v0.2.8.json` | BN_graphical | ~420 |
| `preference_testing_contract_v0.2.8.json` | Preference testing | ~96 |

### Localized Attribute Schema
- **File**: `contracts/localized_image_tags.schema.json`
- **Purpose**: Spatially-structured feature extraction (per-region, dense maps)
- **Key insight**: 71.5% of tags require or benefit from localization

---

## 5. Image_Tagger (Visual Feature Extraction)

**Path**: `/Users/davidusa/Documents/___NEW AI PROJECTS/IMAGE TAGGER/_Image-tagger-main_Taggert/`
**Purpose**: Extract visual features from architectural photographs
**Version**: v3.4.74
**Status**: ACTIVE

### Core Function
Enterprise-grade web application combining:
- Human-in-the-loop (HITL) collaborative tagging
- Deterministic computer vision (CV) analysis
- Visual Language Model (VLM) integration for semantic attributes

### Tech Stack
- **Backend**: FastAPI + SQLAlchemy 2.0 + PostgreSQL 15
- **Frontend**: 4 React micro-apps (Workbench, Monitor, Admin, Explorer)
- **Deployment**: Docker Compose, single port 8080 via Nginx
- **VLM Providers**: Gemini, OpenAI, Anthropic (pluggable)

### Science Pipeline (`backend/science/`)

**L0 (Physics/Vision)**:
| Module | Features |
|--------|----------|
| `color.py` | luminance, saturation, warmth |
| `complexity.py` | edge_density, organization_ratio |
| `glcm.py` | texture contrast, homogeneity, energy |
| `fractals.py` | fractal_dimension (box-counting) |
| `symmetry.py` | mirror correlation |
| `naturalness.py` | green/blue hue presence |

**L1 (Spatial)**:
| Module | Features |
|--------|----------|
| `spatial/depth.py` | prospect, enclosure, depth_bins |
| `spatial/isovist.py` | isovist_area, compactness |
| `fluency.py` | perceptual fluency composites |

**L2 (Cognitive/Semantic - VLM)**:
| Module | Features |
|--------|----------|
| `context/cognitive.py` | coherence, complexity, legibility, mystery, restoration |
| `semantics/semantic_tags_vlm.py` | style.*, room_function.* |
| `context/social.py` | cozy, welcoming, tranquil, scary, jarring |

### Frontend Apps

| App | Purpose |
|-----|---------|
| **Workbench** | HITL annotation interface |
| **Monitor** | Velocity, IRR, quality checks |
| **Admin** | VLM config, user management |
| **Explorer** | Search, filter, export |

### BN Export
- **Endpoint**: `/v1/export/bn-snapshot`
- **Output**: BNRow[] with indices + bins
- **Consumer**: BN_graphical

---

## 6. BN_graphical (Bayesian Causal Network)

**Path**: `/Users/davidusa/REPOS/BN_graphical/`
**Purpose**: Predict psychological outcomes from space images via causal inference
**Status**: ACTIVE, SEPARATE SYSTEM

### Architecture
```
Images → Attributes → Mediators → Outcomes
         (visual)    (percepts)   (psych)
```

### Tech Stack
- **Inference**: PyMC for Bayesian inference
- **Database**: PostgreSQL
- **API**: FastAPI + nginx
- **Deployment**: Docker

### Three-Layer Causal Model
1. **Layer 1 (Input)**: Attributes from Image Tagger (424 tags)
2. **Layer 2 (Mediators)**: Psychological perceptions (warmth, cognitive load)
3. **Layer 3 (Outcomes)**: Psychological states (stress, focus, satisfaction)

### Relevance to MVP
- **MEDIUM** - Separate image-based prediction system
- Currently does NOT use text-extracted beliefs from Article Eater
- Could potentially consume Article Eater rules as priors in future
- Shares vocabulary with Outcome_Contractor and Tagging_Contractor

### Contracts
- `bn.api.v2.schema.json` - API schema
- `bn.epistemology.v1.schema.json` - Epistemology schema
- `bn.prediction.v1.schema.json` - Prediction format

---

## 7. Integration Status Matrix

### Text Track Integration

| From | To | Status | Interface |
|------|----|--------|-----------|
| Article_Finder | Article_Eater | ✅ EXISTS | `eater_interface/invoker.py` |
| Article_Eater | Web of Belief | ✅ EXISTS | `extraction_to_web.py` |
| Web of Belief | Persistence | ⚠️ PARTIAL | `web_persistence.py` (per-run only) |
| Web of Belief | Query Engine | ❌ MISSING | Need to build |
| Outcome_Contractor | Article_Eater | ✅ EXISTS | `ae_outcome_lookup.json` |

### Image Track Integration

| From | To | Status | Interface |
|------|----|--------|-----------|
| Image_Tagger | BN_graphical | ✅ EXISTS | `/v1/export/bn-snapshot` |
| Tagging_Contractor | Image_Tagger | ✅ EXISTS | `image_tagger_contract_v0.2.8.json` |
| Tagging_Contractor | BN_graphical | ✅ EXISTS | `bn_contract_v0.2.8.json` |
| Outcome_Contractor | BN_graphical | ✅ EXISTS | `bn_outcome_nodes.json` |

### Cross-Track Integration (FUTURE)

| From | To | Status | Notes |
|------|----|--------|-------|
| Article_Eater rules | BN_graphical priors | ❌ NOT STARTED | Could inform effect sizes |
| Image features | Article_Eater constraints | ❌ NOT STARTED | Visual evidence for beliefs |

---

## 8. What Exists vs. What's Missing for MVP

### ✅ EXISTS (can reuse)

| Component | Location | Notes |
|-----------|----------|-------|
| Paper database | AF: `data/article_finder.db` | 16K papers, structured |
| AF→AE invoker | AF: `eater_interface/invoker.py` | EaterInvoker class |
| Job bundle creation | AF: `eater_interface/job_bundle_v2.py` | Creates AE inputs |
| Output parser | AF: `eater_interface/output_parser_v2.py` | Parses AE results |
| Extraction pipeline | AE: `app/tasks/pipeline.py` | Full extraction logic |
| Web of belief engine | AE: `src/services/web_of_belief.py` | Mature, tested |
| Claims→beliefs mapper | AE: `src/services/extraction_to_web.py` | Sprint 1 |
| Web persistence | AE: `src/services/web_persistence.py` | Sprint 5 |
| Web state schema | AE: `contracts/.../ae.web_state.v1.schema.json` | Well-defined |
| Outcome vocabulary | OC: `contracts/oc_export/` | 7 domains, 1000+ terms |
| Environment vocabulary | TC: `registry_v0.2.8.json` | 424 tags |
| Theory registry | AE: `src/services/theory_registry.py` | ART, SRT, etc. |

### ❌ MISSING (must build for MVP)

| Component | What's Needed | Priority |
|-----------|---------------|----------|
| **Persistent accumulated web** | File that grows across runs | P0 |
| **Batch processor script** | Simple: "process these 100 papers" | P0 |
| **Query CLI** | `query "What affects X?"` → beliefs | P0 |
| **Gap identification** | "Low coverage in thermal×creativity" | P1 |
| **Status GUI** | Pipeline progress, belief counts | P1 |
| **Query GUI** | Ask questions, see results | P1 |

### ⚠️ EXISTS BUT NOT WIRED

| Component | Issue |
|-----------|-------|
| `integrate_extraction()` | Called but output not accumulated |
| `web_state.json` | Created per-run but not merged |
| VOI search | Code exists but not connected to query loop |
| Outcome resolver | OC has resolver but AE not using it directly |

---

## 9. Data Flow (Current vs. Needed)

### Current Flow (Disconnected)
```
AF SQLite ──[invoker]──> AE CLI ──[pipeline]──> JSON files (per run)
                                                    │
                                                    └──> (discarded)
```

### Needed Flow (Connected)
```
AF SQLite ──[invoker]──> AE CLI ──[pipeline]──> web_state.json (per run)
     │                                                │
     │                                                ▼
     │                                      ┌─────────────────┐
     │                                      │ ACCUMULATED WEB │
     │                                      │ (persistent)    │
     │                                      └────────┬────────┘
     │                                               │
     │                   ┌───────────────────────────┼───────────────────────────┐
     │                   │                           │                           │
     │                   ▼                           ▼                           ▼
     │            Query Engine              Gap Identifier                 GUI Dashboard
     │            (answer Q's)              (what's missing?)             (visualize)
     │                   │                           │
     │                   │                           ▼
     └───────────────────┼────────────────── Search Generator
                         │                    (Scholar AI queries)
                         │                           │
                         └───────────────────────────┘
                                 (closed loop)
```

---

## 10. Key Files to Examine for MVP

Before implementation, should read:

1. **AF→AE interface**: `Article_Finder_v3_2_3/eater_interface/pipeline.py`
2. **AE extraction**: `Article_Eater_PostQuinean_v1/app/tasks/pipeline.py`
3. **Web persistence**: `Article_Eater_PostQuinean_v1/src/services/web_persistence.py`
4. **Integration function**: `Article_Eater_PostQuinean_v1/src/services/extraction_to_web.py`
5. **Outcome resolver**: `Outcome_Contractor/core/resolver.py`

---

## 11. Estimated Existing Code to Reuse

| Component | Est. Reusable | Notes |
|-----------|---------------|-------|
| Paper storage/retrieval | 95% | AF works well |
| Extraction logic | 90% | AE pipeline mature |
| Web of belief | 95% | Well-tested |
| Outcome vocabulary | 100% | OC ready to use |
| Environment vocabulary | 100% | TC ready to use |
| Persistence format | 90% | Schema defined |
| Gap identification | 60% | VOI code exists, needs wiring |
| Query engine | 20% | Need to build query interface |
| GUI | 0% | Need to build |

**Summary**: ~70% of backend exists. Main work is:
- Wiring components together
- Building query interface
- Building GUI
- Creating accumulation loop

---

## 12. Vocabulary Alignment

Both tracks share vocabulary through the contractors:

### Cause Side (Tagging_Contractor)
```
424 tags in 12 domains:
A. Luminous Environment (41)
D. Spatial Configuration (39)
E. Visual Complexity (22)
F. Material & Surface (14)
G. Color & Palette (14)
H. Biophilic Elements (20)
I. Architectural Patterns (20)
K. Social-Spatial (18)
L. Computed Features (48)
...
```

### Effect Side (Outcome_Contractor)
```
7 domains with ~1000+ terms:
cog: Cognitive (attention, memory, executive)
affect: Affective (mood, emotion, stress)
behav: Behavioral (productivity, sleep)
social: Social (collaboration, isolation)
physio: Physiological (HPA axis, cortisol)
neural: Neural (connectivity, EEG)
health: Health (life satisfaction)
```

### Causal Arrow
```
Tagging_Contractor (X) ────────> Outcome_Contractor (Y)
   "warm lighting"                  "positive affect"
   "high enclosure"                 "stress reduction"
   "visual complexity"              "cognitive load"
```

---

## 13. Questions Resolved by Panel

See `docs/PANEL_P-INT_MVP_INTEGRATION_2026-02-11.md` for full panel consultation.

**Key decisions**:
1. **Should we modify existing code or wrap it?** → Create new orchestrator (Option B)
2. **Where should accumulated web live?** → In Article Eater: `data/accumulated_web.json`
3. **How to handle partial failures?** → Save after each paper, circuit breaker after 3 failures
4. **Streamlit app location?** → In Article Eater repo
5. **Authentication for demo?** → Single-user sufficient

---

## 14. MVP Phases (from Panel)

### Phase 0: Contracts (Day 1)
- [ ] Verify `af_paper.v1.json` contract
- [ ] Verify `ae_rule.v1.json` contract
- [ ] Define `query_request.v1.json`
- [ ] Define `query_response.v1.json`
- [ ] Define `gap_report.v1.json`

### Phase 1: Persistence (Day 2)
- [ ] Create `data/web_state.json` - persistent belief store
- [ ] Add `events.jsonl` - event log for debugging
- [ ] Implement BeliefStore save/load
- [ ] Test: Can save web, restart, load, query

### Phase 2: Pipeline Connection (Day 3-4)
- [ ] Create `scripts/process_papers.py` - batch processor
- [ ] Wire: AF papers → AE extraction → Web accumulation
- [ ] Add progress tracking
- [ ] Process 100 test papers end-to-end

### Phase 3: Query Interface (Day 5)
- [ ] Create `src/services/query_engine.py`
- [ ] Implement `query(question) -> beliefs with confidence`
- [ ] Implement `identify_gaps() -> gap report`
- [ ] CLI: `python -m src.cli.query "What affects attention?"`

### Phase 4: Minimal GUI (Day 6)
- [ ] Streamlit app with 3 pages (status, query, gaps)
- [ ] Basic visualizations (confidence bars, source links)

### Phase 5: Polish (Day 7)
- [ ] Error handling, timeouts, logging
- [ ] Documentation for demo
- [ ] 10-minute demo script

---

*Inventory complete. Ready for MVP implementation.*
