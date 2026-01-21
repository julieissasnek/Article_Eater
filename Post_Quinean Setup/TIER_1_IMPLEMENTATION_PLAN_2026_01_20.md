# Tier 1 Implementation Plan
## Article Eater Post-Quinean v1 — Critical User-Facing Features
**Date**: January 20, 2026
**Status**: DRAFT — Awaiting Expert Panel Review

---

## EXECUTIVE SUMMARY

This plan addresses the four Tier 1 priorities identified by the expert panel:

1. **Evidence Explorer GUI** — Let users SEE the web of belief
2. **Natural Language Query Interface** — Let users ASK questions in plain English
3. **PubMed/Semantic Scholar Ingestion** — Let users ADD papers by DOI/PMID
4. **Belief-Stability Stopping Rules** — Let the system KNOW when to stop searching

Each section includes: rationale, design decisions, implementation approach, and questions for panel review.

---

## TIER 1.1: EVIDENCE EXPLORER GUI

### Rationale

The panel's unanimous verdict: "Until users can SEE the web, everything else is academic." The web of belief is the core intellectual artifact. Without visualization, users cannot:
- Understand what the system knows
- Identify where conflicts exist
- Trust the system's recommendations
- Provide meaningful feedback

### Design Decisions

**Decision 1.1.1: Technology Stack**

| Option | Pros | Cons |
|--------|------|------|
| A. Web-based (React + D3.js) | Cross-platform, shareable URLs, no install | Requires server deployment |
| B. Desktop (Electron + Cytoscape.js) | Offline capable, faster for large graphs | Platform-specific builds |
| C. Jupyter widget (ipycytoscape) | Integrates with research workflow | Limited to notebook users |

**Proposed**: Option A (Web-based) for broadest accessibility. Researchers can share links; architects can access from any device.

**Decision 1.1.2: Graph Layout Algorithm**

| Option | Best For | Limitation |
|--------|----------|------------|
| Force-directed | Organic clustering | Slow for >500 nodes |
| Hierarchical | Theory→evidence structure | Imposes artificial hierarchy |
| Radial | Ego-network exploration | Single focal point |

**Proposed**: Force-directed as default, with hierarchical as option for theory-centric views.

**Decision 1.1.3: Node/Edge Encoding**

| Element | Visual Encoding | Rationale |
|---------|-----------------|-----------|
| Node size | Credence strength (0.3-1.0 scale) | Higher credence = larger node |
| Node color | Outcome category (hue) | Quick category identification |
| Node border | Conflict status (red dashed = conflict) | Alert to problems |
| Edge thickness | Constraint strength | Stronger constraints more visible |
| Edge color | Constraint type (green=support, red=tension, purple=bridge) | Semantic distinction |
| Edge style | Causal direction (solid=forward, dashed=correlational) | Pearl's requirement |

**Decision 1.1.4: Interaction Model**

| Interaction | Action |
|-------------|--------|
| Click node | Select; show detail panel |
| Double-click node | Focus; dim distant nodes |
| Drag node | Reposition (sticky) |
| Scroll | Zoom in/out |
| Right-click node | Context menu (edit, delete, find paths) |
| Shift+click | Multi-select |
| Search box | Highlight matching nodes |

**Decision 1.1.5: Detail Panel Contents**

When a node is selected, show:
```
┌─────────────────────────────────────────┐
│ BELIEF: Natural light improves mood     │
│ ─────────────────────────────────────── │
│ Credence: 0.78 ████████░░ [edit]        │
│ Status: INTEGRATED                       │
│ Outcome: affect.mood.positive            │
│ ─────────────────────────────────────── │
│ SOURCES (3 papers)                       │
│ • Ulrich 1984 (strength: 0.85)          │
│ • Leather 1998 (strength: 0.72)         │
│ • Veitch 2012 (strength: 0.69)          │
│ ─────────────────────────────────────── │
│ CONSTRAINTS (5)                          │
│ → supports: productivity (0.45)         │
│ → supports: stress_reduction (0.62)     │
│ ← supported_by: window_access (0.71)    │
│ ⚡ tension: artificial_light_equiv (0.3)│
│ 🌉 bridge: hospital→office (0.55)       │
│ ─────────────────────────────────────── │
│ SCOPE CONDITIONS                         │
│ • Setting: office, healthcare           │
│ • Population: adults                     │
│ • Duration: >30 min exposure            │
│ ─────────────────────────────────────── │
│ [View History] [Challenge] [Explain]    │
└─────────────────────────────────────────┘
```

### Implementation Approach

**Sprint GUI-1: Backend API (2 days)**
- Add `/api/v1/web/graph` endpoint returning nodes/edges in Cytoscape.js format
- Add `/api/v1/web/node/{id}` endpoint for detail panel data
- Add `/api/v1/web/search?q=` endpoint for node search

**Sprint GUI-2: Basic Visualization (2 days)**
- React app with Cytoscape.js
- Force-directed layout
- Basic node/edge rendering
- Zoom/pan controls

**Sprint GUI-3: Interaction & Detail Panel (2 days)**
- Node selection and detail panel
- Multi-select
- Search highlighting
- Context menu

**Sprint GUI-4: Visual Polish (1 day)**
- Color scheme refinement
- Responsive layout
- Loading states
- Error handling

### Questions for Panel

1. **For UX Expert**: Is the detail panel too dense? Should we split into tabs (Overview / Sources / Constraints / Scope)?

2. **For Dr. Pearl**: Should CORRELATIONAL edges be shown differently (perhaps dotted AND grayed) to emphasize they're not causal?

3. **For Dr. Bates**: Should search match belief content only, or also source paper titles and author names?

4. **For Workflow Designer**: Should the default view show ALL beliefs, or start focused on a user-selected outcome category?

---

## TIER 1.2: NATURAL LANGUAGE QUERY INTERFACE

### Rationale

Users want to ask questions like:
- "What affects creativity in open offices?"
- "Is natural light better than artificial light for mood?"
- "What's the evidence for biophilic design?"

Currently, all queries require structured API calls. This is unusable for non-developers.

### Design Decisions

**Decision 1.2.1: Query Parsing Approach**

| Option | Pros | Cons |
|--------|------|------|
| A. LLM-based (GPT-4/Claude) | Handles ambiguity, natural phrasing | API cost, latency, dependency |
| B. Rule-based NLP (spaCy + patterns) | Fast, no external dependency | Brittle, limited coverage |
| C. Hybrid (rules first, LLM fallback) | Best of both | Complexity |

**Proposed**: Option C (Hybrid). Use rule-based parsing for common patterns; fall back to LLM for complex queries. Log all queries to improve rule coverage over time.

**Decision 1.2.2: Query Types to Support**

| Query Type | Example | Structured Form |
|------------|---------|-----------------|
| Outcome query | "What affects stress?" | `GET /beliefs?outcome=stress.*` |
| Comparison query | "Is A better than B for X?" | `GET /compare?a=A&b=B&outcome=X` |
| Evidence query | "What's the evidence for X?" | `GET /beliefs/{X}/sources` |
| Mechanism query | "Why does X affect Y?" | `GET /paths?from=X&to=Y` |
| Gap query | "What don't we know about X?" | `GET /gaps?topic=X` |
| Contradiction query | "Are there conflicts about X?" | `GET /conflicts?topic=X` |

**Decision 1.2.3: Response Format**

For each query, return:
1. **Direct answer** (1-2 sentences)
2. **Evidence summary** (belief nodes, credences, sources)
3. **Epistemic context** (confidence level, conflicts, gaps)
4. **Follow-up suggestions** ("You might also ask...")

Example response:
```
┌─────────────────────────────────────────────────────────┐
│ Q: What affects creativity in open offices?             │
│ ─────────────────────────────────────────────────────── │
│ ANSWER                                                  │
│ Based on 12 studies, key factors affecting creativity   │
│ in open offices include: noise level (negative),        │
│ visual privacy (positive), and natural light (positive).│
│ ─────────────────────────────────────────────────────── │
│ EVIDENCE (click to explore)                             │
│ • Noise → creativity: -0.45 credence (8 studies)       │
│ • Privacy → creativity: +0.62 credence (5 studies)     │
│ • Light → creativity: +0.38 credence (4 studies)       │
│ ─────────────────────────────────────────────────────── │
│ EPISTEMIC CONTEXT                                       │
│ ⚠️ Moderate confidence — conflicting findings on noise │
│ 🔍 Gap: interaction effects unexplored                  │
│ 🌉 Bridge: lab→field transfer uncertain                 │
│ ─────────────────────────────────────────────────────── │
│ FOLLOW-UP                                               │
│ • "What's the mechanism for noise affecting creativity?"│
│ • "Are there differences between types of noise?"       │
│ • "What about acoustic privacy specifically?"           │
└─────────────────────────────────────────────────────────┘
```

**Decision 1.2.4: Disambiguation Handling**

When query is ambiguous:
```
┌─────────────────────────────────────────────────────────┐
│ Q: What about light?                                    │
│ ─────────────────────────────────────────────────────── │
│ I found several interpretations. Did you mean:          │
│                                                         │
│ ○ Natural light (daylight, sunlight)                   │
│ ○ Artificial light (electric lighting)                 │
│ ○ Light level (illuminance, lux)                       │
│ ○ Light quality (color temperature, spectrum)          │
│                                                         │
│ Or type a more specific question.                       │
└─────────────────────────────────────────────────────────┘
```

### Implementation Approach

**Sprint NLQ-1: Query Parser (2 days)**
- Rule-based patterns for 6 query types
- spaCy NER for outcome/variable extraction
- Vocabulary bridge integration for synonym resolution

**Sprint NLQ-2: LLM Fallback (1 day)**
- Claude API integration for unparseable queries
- Structured output format (JSON)
- Cost tracking and rate limiting

**Sprint NLQ-3: Response Generator (2 days)**
- Template-based response assembly
- Evidence aggregation from web
- Epistemic context extraction
- Follow-up suggestion generation

**Sprint NLQ-4: UI Integration (1 day)**
- Search box in Evidence Explorer header
- Results panel (replaces or augments detail panel)
- Query history

### Questions for Panel

1. **For Dr. Bates**: What's the right balance between precision (narrow interpretation) and recall (broad interpretation) in query parsing?

2. **For Dr. Simon**: How many follow-up suggestions is too many? Should we limit to 3, or show more with progressive disclosure?

3. **For Epistemologist**: The "confidence level" in epistemic context is a simplification. Should we expose the full coherence calculation, or is traffic-light sufficient?

4. **For Dr. Cartwright**: When a query involves bridge warrants (e.g., "Does lab evidence apply to real offices?"), should we default to conservative (bridges uncertain) or optimistic (bridges assumed valid)?

---

## TIER 1.3: PUBMED/SEMANTIC SCHOLAR INGESTION

### Rationale

Currently, paper ingestion requires:
1. Obtain PDF
2. Run CLI command with file path
3. Wait for extraction
4. Review extracted claims

This is too much friction. Researchers want to enter a DOI or PMID and have the system handle the rest.

### Design Decisions

**Decision 1.3.1: Supported Identifiers**

| Identifier | Source | Coverage |
|------------|--------|----------|
| DOI | CrossRef API | ~95% of recent papers |
| PMID | PubMed API | Biomedical literature |
| Semantic Scholar ID | S2 API | Broad coverage + citations |
| arXiv ID | arXiv API | Preprints |

**Proposed**: Support all four. Prioritize DOI (most universal), then PMID (domain-relevant), then S2 ID (for citation data), then arXiv.

**Decision 1.3.2: Metadata vs. Full Text**

| Approach | Pros | Cons |
|----------|------|------|
| A. Metadata only (title, abstract) | Always available, fast | Limited claim extraction |
| B. Full text when available | Richer extraction | Often paywalled |
| C. Metadata + structured data (MeSH, keywords) | Balanced | Requires API integration |

**Proposed**: Option C. Use metadata + structured data for initial ingestion. Offer full-text upload as optional enhancement.

**Decision 1.3.3: Extraction from Abstracts**

Abstract-only extraction will be shallower than full-text. Adjust expectations:
- Mark beliefs extracted from abstracts with `source_depth: "abstract"`
- Lower default credence for abstract-only extractions (0.5 vs 0.7 for full-text)
- Flag for full-text upgrade when available

**Decision 1.3.4: Citation Integration**

Semantic Scholar provides citation data. Use it for:
- "Cited by" links between papers
- Citation count as (weak) quality signal
- Highly-cited papers flagged for priority review

**Decision 1.3.5: Duplicate Detection**

Before ingesting, check if paper already exists:
- Match on DOI (exact)
- Match on title + year (fuzzy, Levenshtein distance < 3)
- If duplicate found, offer to merge or skip

### Implementation Approach

**Sprint ING-1: API Clients (2 days)**
- PubMed E-utilities client (PMID → metadata)
- Semantic Scholar API client (DOI/S2ID → metadata + citations)
- CrossRef API client (DOI → metadata)
- arXiv API client (arXiv ID → metadata)

**Sprint ING-2: Ingestion Pipeline (2 days)**
- Identifier parsing (detect type from format)
- Metadata fetching and normalization
- Abstract extraction pipeline (reuse existing LLM extraction)
- Duplicate detection

**Sprint ING-3: Citation Graph (1 day)**
- Store citation relationships
- "Cited by" and "Cites" queries
- Citation count tracking

**Sprint ING-4: UI Integration (1 day)**
- "Add Paper" dialog in Evidence Explorer
- Identifier input with auto-detection
- Progress indicator during extraction
- Preview extracted claims before integration

### Questions for Panel

1. **For Dr. Bates**: Should we auto-suggest related papers based on citations? ("This paper cites 5 papers already in your web. Add them?")

2. **For Dr. Cartwright**: Abstract-only extraction misses methodology details. Should we require full-text for papers making causal claims, or accept the limitation?

3. **For Systems Architect**: PubMed rate limits are strict (3 requests/second without API key). Should we require users to register for NCBI API keys, or use a shared institutional key?

4. **For Dr. Kaplan**: Are there domain-specific databases beyond PubMed that environmental psychology researchers use (e.g., PsycINFO, Web of Science)?

---

## TIER 1.4: BELIEF-STABILITY STOPPING RULES

### Rationale

Dr. Simon's critique: "Budget-based limits (stop after N papers) are computationally convenient but epistemically arbitrary."

Researchers need to know: "When have I searched enough?" The answer should be based on what the system has learned, not arbitrary paper counts.

### Design Decisions

**Decision 1.4.1: Stability Metric**

| Metric | Definition | Threshold |
|--------|------------|-----------|
| Credence stability | Max |Δcredence| across all beliefs | < 0.01 |
| Coherence stability | |Δcoherence_score| | < 0.005 |
| Topology stability | No new beliefs or constraints added | 0 changes |

**Proposed**: Use credence stability as primary metric. If no belief changes credence by more than 0.01 after K consecutive papers, declare stable.

**Decision 1.4.2: Stability Window**

How many papers must pass without significant change?

| Window | Sensitivity | Risk |
|--------|-------------|------|
| K=3 | High (stops quickly) | May miss slow-building evidence |
| K=5 | Medium | Balanced |
| K=10 | Low (thorough) | May over-search |

**Proposed**: K=5 as default, configurable via `AE_STABILITY_WINDOW` environment variable.

**Decision 1.4.3: Reporting**

When stability is reached, report:
```
┌─────────────────────────────────────────────────────────┐
│ 🎯 BELIEF STABILITY REACHED                             │
│ ─────────────────────────────────────────────────────── │
│ Papers processed: 47                                    │
│ Stable for last: 5 papers                              │
│ Max credence change in window: 0.008                   │
│ ─────────────────────────────────────────────────────── │
│ SUMMARY                                                 │
│ • 23 beliefs reached stable credences                  │
│ • 3 beliefs still have high uncertainty (>0.3 variance)│
│ • 2 gaps remain unexplored                             │
│ ─────────────────────────────────────────────────────── │
│ RECOMMENDATION                                          │
│ The web appears saturated with available evidence.      │
│ Remaining uncertainty is due to genuine disagreement    │
│ in the literature, not lack of evidence.               │
│                                                         │
│ To reduce uncertainty further, consider:               │
│ • Searching grey literature for null results           │
│ • Commissioning new empirical studies                  │
│ ─────────────────────────────────────────────────────── │
│ [Continue Anyway] [Accept & Stop] [View Unstable]      │
└─────────────────────────────────────────────────────────┘
```

**Decision 1.4.4: Hard Cutoff**

Even with stability checking, maintain a hard cutoff to prevent runaway searches:
- Default: 200 papers
- Configurable via `AE_MAX_PAPERS`
- When hit, warn user that stability was not reached

**Decision 1.4.5: Integration with VOI Search**

Stability stopping should interact with VOI:
- If stable AND no high-VOI gaps remain → confident stop
- If stable BUT high-VOI gaps remain → warn user ("Evidence is stable, but these questions remain unanswered")
- If unstable AND high-VOI gaps → continue searching

### Implementation Approach

**Sprint STOP-1: Stability Tracking (1 day)**
- Add credence history to beliefs (last N values)
- Calculate max delta across window
- Detect stability condition

**Sprint STOP-2: Reporting (1 day)**
- Generate stability report
- Identify remaining high-uncertainty beliefs
- Generate recommendations

**Sprint STOP-3: VOI Integration (1 day)**
- Cross-reference stability with VOI gaps
- Generate combined stopping recommendation
- UI for stability status in Evidence Explorer

### Questions for Panel

1. **For Dr. Simon**: Is credence stability the right metric, or should we also consider structural stability (belief graph topology)?

2. **For Epistemologist**: When a belief's credence oscillates (0.6 → 0.7 → 0.6 → 0.7), should we treat this as unstable, or recognize it as an unresolvable tension?

3. **For Dr. Pearl**: If two papers with opposite findings keep alternating which is "more recent," the credence will oscillate. Should we weight by study quality rather than recency to prevent this?

4. **For Dr. Cartwright**: Stability might be an artifact of publication bias—we've seen all the positive results, but null results aren't published. Should stability reporting include a publication bias warning?

---

## SUMMARY: IMPLEMENTATION TIMELINE

| Sprint | Feature | Duration | Dependencies |
|--------|---------|----------|--------------|
| GUI-1 | Backend API | 2 days | None |
| GUI-2 | Basic visualization | 2 days | GUI-1 |
| NLQ-1 | Query parser | 2 days | None |
| ING-1 | API clients | 2 days | None |
| GUI-3 | Interaction & detail | 2 days | GUI-2 |
| NLQ-2 | LLM fallback | 1 day | NLQ-1 |
| ING-2 | Ingestion pipeline | 2 days | ING-1 |
| STOP-1 | Stability tracking | 1 day | None |
| GUI-4 | Visual polish | 1 day | GUI-3 |
| NLQ-3 | Response generator | 2 days | NLQ-2 |
| ING-3 | Citation graph | 1 day | ING-2 |
| STOP-2 | Reporting | 1 day | STOP-1 |
| NLQ-4 | UI integration | 1 day | NLQ-3, GUI-4 |
| ING-4 | UI integration | 1 day | ING-3, GUI-4 |
| STOP-3 | VOI integration | 1 day | STOP-2 |

**Total estimated effort**: 22 sprint-days

**Parallelization opportunity**: GUI, NLQ, ING, and STOP tracks can proceed in parallel with synchronization at UI integration points.

---

## DECISION LOG (For Panel Review)

| ID | Decision | Proposed | Alternatives Considered | Rationale |
|----|----------|----------|------------------------|-----------|
| 1.1.1 | Tech stack | Web (React+D3) | Desktop, Jupyter | Broadest accessibility |
| 1.1.2 | Layout | Force-directed | Hierarchical, Radial | Organic clustering |
| 1.1.3 | Node size | Credence strength | Uniform | Visual salience for confidence |
| 1.1.4 | Interaction | Click-select, double-focus | Hover-select | Deliberate selection |
| 1.2.1 | Query parsing | Hybrid (rules+LLM) | LLM-only, Rules-only | Balance speed and coverage |
| 1.2.2 | Query types | 6 types | More/fewer | Core use cases |
| 1.2.4 | Disambiguation | Ask user | Guess most likely | Avoid silent errors |
| 1.3.1 | Identifiers | DOI, PMID, S2, arXiv | DOI only | Comprehensive coverage |
| 1.3.2 | Depth | Metadata + structured | Full text required | Availability tradeoff |
| 1.3.3 | Abstract credence | 0.5 (lower than full) | Same as full | Acknowledge limitation |
| 1.4.1 | Stability metric | Credence stability | Coherence, Topology | Most interpretable |
| 1.4.2 | Window | K=5 | K=3, K=10 | Balanced sensitivity |
| 1.4.5 | VOI integration | Cross-reference | Separate systems | Unified stopping logic |

---

## QUESTIONS FOR PANEL (CONSOLIDATED)

### GUI Questions
1. Is the detail panel too dense? Should we split into tabs?
2. Should CORRELATIONAL edges be shown differently (dotted AND grayed)?
3. Should search match belief content only, or also papers/authors?
4. Should default view show ALL beliefs or start focused?

### NLQ Questions
5. What's the right precision/recall balance in query parsing?
6. How many follow-up suggestions is too many?
7. Should we expose full coherence calculation or use traffic-light?
8. Should bridge warrants default to conservative or optimistic?

### Ingestion Questions
9. Should we auto-suggest related papers based on citations?
10. Should we require full-text for causal claims?
11. Should users register for API keys, or use shared key?
12. Are there domain-specific databases beyond PubMed?

### Stopping Questions
13. Is credence stability the right metric, or also structural?
14. How should we handle oscillating credences?
15. Should we weight by quality rather than recency?
16. Should stability reporting include publication bias warning?

---

*End of Implementation Plan*

**Awaiting panel review before implementation begins.**
