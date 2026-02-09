# Sprint 3.0 Plan — Unified API, Query Engine, Streamlit Interface, Export

**Date**: 2026-02-08
**Status**: IN PROGRESS
**Panel**: P-S3 (21 experts consulted)
**Interface**: Streamlit (primary) + FastAPI (backend)

---

## Executive Summary

Sprint 3.0 delivers the user-facing layer of Article Eater V23.0.0:
- **Unified API**: Resource-based REST API with 7 core endpoints
- **Query Engine**: Natural language queries with LLM-assisted interpretation
- **Streamlit Interface**: User-type-driven UI with common questions
- **Admin Dashboard**: System inspection for beliefs, constraints, communities
- **Export**: BibTeX, evidence summaries, verification checklists

---

## Design Principles (From Expert Panel)

### From Dr. Herbert Simon (Bounded Rationality)
- **Layered API**: Core 7 endpoints → Extended 25 → Full programmatic
- **Progressive disclosure**: Headline → Summary → Detail → Deep Dive
- **Magical number seven**: Users can't navigate 225 methods

### From Dr. Alan Cooper (Interaction Design)
- **Concrete personas**: Sarah Chen (researcher), Marcus Williams (practitioner), Jordan Taylor (student)
- **Goal-directed design**: Every screen answers "What is the user trying to accomplish?"
- **User type selection**: Let users self-identify to receive appropriate UX

### From Dr. Ben Shneiderman (Information Visualization)
- **Visual Information Seeking Mantra**: Overview first, zoom and filter, then details on demand
- **Force-directed graphs**: For claim networks with pan, zoom, filter by credence
- **Clustered layouts**: For community structure visualization

### From Dr. Judea Pearl (Causal Inference)
- **Query type detection**: Associational vs interventional vs counterfactual
- **Causal endpoints**: `/api/v1/causal/paths/{from}/{to}`, `/api/v1/causal/interventions/{target}`
- **Never conflate correlation with causation**: Explicit in all outputs

### From Dr. Nancy Cartwright (Philosophy of Science)
- **Scope conditions everywhere**: Never return a finding without boundaries
- **Evidence summaries**: What was found, where it applies, what it depends on, what could defeat it
- **Machine-readable scope metadata**: Not just citations

### From Dr. Rachel Kaplan (Environmental Psychology)
- **Practitioner mode**: Translate epistemic output into design guidance
- **Ranked recommendations**: Features + effect sizes + implementation notes
- **Practical implications section**: Every query response ends with actionable guidance

---

## User Types with Common Questions

### 1. Practitioner/Designer
**Persona**: Marcus Williams, Healthcare Architect
**Goal**: Evidence-based design decisions
**Pain**: Can't translate research to practice
**Common Questions**:
1. What reduces stress in hospitals?
2. Evidence for plants in offices?
3. Windows vs skylights for wellbeing?
4. Practical recommendations for waiting rooms
5. What's the dosage for biophilic elements?
6. Nature views — what counts as "nature"?
7. Cost-effective interventions ranked by evidence
8. What should I avoid based on evidence?

### 2. Senior Researcher
**Persona**: Dr. Sarah Chen
**Goal**: Build comprehensive literature reviews
**Pain**: Manual evidence synthesis takes weeks
**Common Questions**:
1. What are the gaps in biophilic design research?
2. Which findings have methodological concerns?
3. What mechanisms explain nature-health links?
4. ART vs SRT — evidence quality comparison?
5. What would change if Ulrich 1984 were retracted?
6. Cross-study heterogeneity for stress outcomes?
7. Which findings are contested between communities?
8. Temporal trends in the evidence base?
9. What populations are understudied?
10. Strongest and weakest evidence by domain?

### 3. Graduate Student
**Persona**: Jordan Taylor
**Goal**: Learn the field, find thesis topic
**Pain**: Overwhelmed by literature volume
**Common Questions**:
1. How does ART theory work?
2. What are the key papers on biophilia?
3. What's contested in this field?
4. Where should I focus my thesis?
5. Explain the evidence hierarchy
6. What's the difference between ART and SRT?
7. Who are the major researchers?
8. What methodologies are commonly used?
9. Recent trends in the field?
10. Entry points for a newcomer?

### 4. Systematic Reviewer
**Goal**: Comprehensive, reproducible evidence synthesis
**Common Questions**:
1. All evidence for outcome X
2. Studies with RCT methodology
3. Export citations for stress reduction
4. Cross-study comparison table
5. Quality assessment for included studies
6. Forest plot data for meta-analysis
7. PRISMA-compatible export

### 5. Quick Lookup
**Goal**: Fast answer to specific question
**Common Questions**:
1. Credence for claim X?
2. What supports Y?
3. Is Z established or contested?
4. Key finding on topic W?
5. How many studies on X?

---

## Component Architecture

### 3.0.1: Unified API

**Core 7 Endpoints** (Layered API — Core Layer):

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/beliefs/` | GET, POST | List/create beliefs |
| `/api/v1/beliefs/{id}` | GET, PUT, DELETE | CRUD single belief |
| `/api/v1/queries/` | POST | Execute natural language query |
| `/api/v1/queries/{id}/results` | GET | Retrieve query results (async) |
| `/api/v1/export/` | POST | Generate export bundle |
| `/api/v1/communities/` | GET | List epistemic communities |
| `/api/v1/admin/stats` | GET | System statistics |

**Extended Layer** (~20 endpoints):
- `/api/v1/constraints/` — Constraint CRUD
- `/api/v1/papers/` — Paper management
- `/api/v1/causal/paths/` — Causal pathway queries
- `/api/v1/causal/interventions/` — Intervention queries
- `/api/v1/batch/` — Batch operations
- `/api/v1/alerts/` — Query monitoring

**Design Principles**:
- URL versioning: `/api/v1/`
- Pagination: `?limit=20&offset=0`
- Async for long queries: Returns job ID, poll for results
- HATEOAS: Responses include links to related resources

### 3.0.2: Query Engine

**Query Type Detection** (Pearl's ladder):
```
User Query → LLM Classification → Type + Entities + Scope
                                       ↓
                              ASSOCIATIONAL → Evidence lookup
                              INTERVENTIONAL → Causal model required
                              COUNTERFACTUAL → Structural equations required
```

**Response Format** (Progressive Disclosure):
```json
{
  "headline": "Plants reduce stress in office settings (credence 0.72)",
  "summary": {
    "finding": "Multiple studies show 15-25% stress reduction",
    "confidence": "moderate",
    "key_evidence": ["Lohr 1996", "Bringslimark 2007"],
    "scope": "Office workers, Western populations, self-report + cortisol"
  },
  "detail": { /* Full evidence trace */ },
  "practical_implications": [
    "Minimum 1 plant per 10m² workspace",
    "Visible greenery more effective than hidden",
    "Real plants preferred over artificial"
  ],
  "caveats": [
    "Limited evidence for hospital settings",
    "No data on long-term effects"
  ]
}
```

**LLM Integration** (Model Tiering):
| Query Type | Model | Cost |
|------------|-------|------|
| Template match | None | $0.00 |
| Simple structure | Haiku | $0.005 |
| Complex synthesis | Sonnet | $0.02 |
| Deep explanation | Opus | $0.10 |

### 3.0.3: Streamlit Interface

**Page Structure**:
```
streamlit_app/
├── main.py                    # Entry point, user type selection
├── config.py                  # API endpoints, styling
├── components/
│   ├── user_type_selector.py  # Persona selection widget
│   ├── common_questions.py    # Pre-populated question buttons
│   ├── query_input.py         # Natural language input
│   ├── result_display.py      # Progressive disclosure results
│   ├── network_graph.py       # D3/vis.js claim network
│   └── export_panel.py        # Export controls
└── pages/
    ├── 1_query.py             # Main query interface
    ├── 2_explore.py           # Visual exploration
    ├── 3_communities.py       # Community browser
    ├── 4_export.py            # Export wizard
    └── 5_admin.py             # Admin dashboard
```

**User Flow**:
1. Landing page: "Who are you?" (user type selection)
2. Query page: Common questions + custom input
3. Results: Progressive disclosure (headline → full)
4. Explore: Visual network navigation
5. Export: Purpose-driven bundles

### 3.0.4: Export

**Export Types**:
| Type | Format | Purpose |
|------|--------|---------|
| Evidence Summary | Markdown/PDF | Practitioner briefing |
| BibTeX | .bib | Citation manager |
| JSONL | .jsonl | Pipeline integration |
| GraphML | .graphml | Network analysis (Gephi) |
| Verification Checklist | Markdown | Quality assurance |

**Evidence Summary Template** (Cartwright):
```markdown
# Evidence Summary: [Topic]
Generated: [Date]

## Key Finding
[One sentence with credence]

## Scope Conditions
- **Population**: [Who this applies to]
- **Setting**: [Where this applies]
- **Methodology**: [How evidence was gathered]
- **Limitations**: [Where this may not generalize]

## Supporting Evidence
[Table of studies with effect sizes]

## Contradicting Evidence
[Any dissenting findings]

## Practical Implications
[Actionable guidance]

## Verification Checklist
- [ ] Scope conditions reviewed
- [ ] Contradicting evidence acknowledged
- [ ] Confidence levels appropriate
- [ ] Citations complete
```

### 3.0.5: Admin Dashboard

**Components**:
1. **System Overview**: Belief count, constraint count, coherence score, last update
2. **Belief Browser**: Searchable table with filters (status, level, credence, theory)
3. **Constraint Network**: Visual graph of epistemic constraints
4. **Community View**: Communities with member beliefs, credences
5. **Paper Browser**: Source papers with extraction status
6. **Health Checks**: API status, test results, recent errors

---

## Implementation Order

### Phase 1: Foundation (Sprint 3.0.1)
**Duration**: Core functionality
**Deliverables**:
- API design document
- 7 core endpoints implemented
- Pagination, async, versioning middleware
- OpenAPI documentation

### Phase 2: Intelligence (Sprint 3.0.2)
**Duration**: Query processing
**Deliverables**:
- Query type detector
- Progressive disclosure formatter
- LLM bridge (Haiku for parsing)
- Scope-aware responses

### Phase 3: Interface (Sprint 3.0.3 + 3.0.5)
**Duration**: User-facing Streamlit
**Deliverables**:
- User type selection
- Common questions per persona
- Query + results pages
- Admin dashboard
- Basic network visualization

### Phase 4: Delivery (Sprint 3.0.4)
**Duration**: Export capabilities
**Deliverables**:
- Evidence summary generator
- BibTeX export
- JSONL/Parquet for pipelines
- Verification checklists

### Phase 5: Enhancement
**Duration**: Polish and extensions
**Deliverables**:
- Extended API (20 endpoints)
- Advanced visualization
- PDF report generation
- Alerting system

---

## Technical Stack

### Backend
- **FastAPI**: REST API framework
- **Pydantic**: Request/response validation
- **SQLite/PostgreSQL**: Persistence
- **Anthropic Claude API**: LLM integration

### Frontend
- **Streamlit**: Primary interface
- **vis.js**: Network visualization
- **Plotly**: Charts and graphs
- **Custom CSS**: Academic aesthetic

### Export
- **bibtexparser**: BibTeX generation
- **pyarrow**: Parquet export
- **networkx**: GraphML export
- **jinja2**: Report templates

---

## Panel Members (P-S3)

### Epistemology & Domain
- Dr. Judea Pearl (Causal inference)
- Dr. Nancy Cartwright (Philosophy of science)
- Dr. Rachel Kaplan (Environmental psychology)

### Information Architecture
- Dr. Herbert Simon (Bounded rationality)
- Dr. Marcia Bates (Information science)
- Dr. Gary Klein (Naturalistic decision making)
- Dr. Atul Gawande (Workflow design)

### System Design
- Dr. Michael Stonebraker (Database systems)
- Dr. Jeff Dean (Large-scale systems)
- Dr. Matei Zaharia (Data pipelines)
- Dr. Roy Fielding (REST architecture)
- Dr. Martin Fowler (Enterprise patterns)

### Visualization & UX
- Dr. Ben Shneiderman (Information visualization)
- Dr. Tamara Munzner (Visualization design)
- Dr. Don Norman (Human-centered design)
- Dr. Alan Cooper (Interaction design)
- Dr. Jakob Nielsen (Usability)

### AI Integration
- Dr. Percy Liang (Foundation models)
- Dr. Christopher Manning (NLP)
- Dr. Dario Amodei (AI safety)
- Dr. Yann LeCun (Deep learning)
- Dr. Emily Bender (Computational linguistics)

---

*Plan approved: 2026-02-08*
*Implementation begins: Phase 1 (API Foundation)*
