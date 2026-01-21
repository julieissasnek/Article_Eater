# Tier 1 Revised Implementation Plan
## Post-Panel Review
**Date**: January 20, 2026
**Status**: APPROVED — Ready for Implementation

---

## SUMMARY OF REVISIONS

Based on panel feedback, the following changes were incorporated:

1. **Correlational edges**: No arrowhead, 50% opacity (Pearl)
2. **Default view**: Top 20-30 beliefs, not all (Simon)
3. **Detail panel**: Simplified view + Implications tab (Simon, Workflow)
4. **Follow-ups**: Exactly 3 (deeper, broader, uncertainty) (Simon)
5. **Oscillation detection**: Flag contested beliefs (Epistemologist)
6. **Publication bias warning**: In stability reports (Cartwright)
7. **Enabling conditions**: Added to data model (Cartwright)
8. **Mission modes**: Explore/Ingest/Research (Workflow)
9. **PsycINFO**: Added to ingestion sources (Kaplan)
10. **Abstract-only warnings**: Badge for causal claims from abstracts (Cartwright)

---

## IMPLEMENTATION SEQUENCE

### Phase A: Data Model & Backend (Sprints 1-4)

**Sprint A1: Core Data Model Extensions**
- Add `enabling_conditions` field to Belief model
- Add `credence_history` table for stability tracking
- Add `source_depth` field (full_text | abstract | metadata)
- Add `contested` flag for oscillating beliefs

**Sprint A2: Graph API Endpoints**
- `/api/v1/web/graph` — Returns nodes/edges for visualization
- `/api/v1/web/node/{id}` — Returns detail panel data
- `/api/v1/web/search` — Searches beliefs, papers, authors

**Sprint A3: Ingestion API Clients**
- Unified `PaperFetcher` class
- CrossRef client (DOI)
- PubMed client (PMID)
- Semantic Scholar client (S2ID, citations)
- PsycINFO client (if API available)

**Sprint A4: Stability Engine**
- Credence history tracking
- Stability detection (window-based)
- Oscillation detection
- Publication bias estimation

### Phase B: Evidence Explorer GUI (Sprints 5-8)

**Sprint B1: Basic Visualization**
- React + Cytoscape.js setup
- Force-directed layout
- Node rendering (size=credence, color=category)
- Edge rendering (correlational: no arrow, 50% opacity)

**Sprint B2: Interaction**
- Click to select node
- Double-click to focus
- Pan and zoom
- Search box with category results

**Sprint B3: Detail Panel**
- Simplified view (default)
- Full detail view (expandable)
- Implications tab
- Scope conditions with applies/does-not-apply/unknown

**Sprint B4: Polish & Modes**
- Mission mode selector (Explore/Ingest/Research)
- Keyboard shortcuts
- Loading states
- Default view: top 20-30 beliefs

### Phase C: Query & Ingestion (Sprints 9-12)

**Sprint C1: Query Parser**
- Rule-based patterns for 6 query types
- spaCy NER integration
- Vocabulary bridge for synonym expansion

**Sprint C2: Query Response Generator**
- Template-based responses
- Epistemic context extraction
- Follow-up generation (3: deeper, broader, uncertainty)
- Abstract-only caution badges

**Sprint C3: Ingestion UI**
- "Add Paper" dialog
- Identifier auto-detection
- Extraction preview
- Duplicate detection warning

**Sprint C4: Integration**
- Query results in Evidence Explorer
- Ingestion flow from query results
- Citation suggestions

### Phase D: Stopping & Reporting (Sprints 13-14)

**Sprint D1: Stability Reports**
- Generate stability report on detection
- Publication bias warning
- Contested beliefs list
- VOI gap cross-reference

**Sprint D2: Research Mode Workflow**
- Define research question
- Systematic search with stability tracking
- Auto-stop with explanation
- Export search session

---

## DECISION LOG (Panel-Approved)

| ID | Decision | Approved By |
|----|----------|-------------|
| G1 | Web-based GUI (React + Cytoscape) | Panel consensus |
| G2 | Force-directed default, options available | UX Expert |
| G3 | Correlational edges: no arrowhead, 50% opacity | Pearl |
| G4 | Default view: top 20-30 beliefs | Simon |
| G5 | Detail panel: simplified default + full expand | Simon |
| G6 | Implications tab for practitioners | Workflow |
| G7 | Mission modes: Explore/Ingest/Research | Workflow |
| Q1 | Hybrid query parsing (rules + LLM fallback) | Panel consensus |
| Q2 | Exactly 3 follow-ups (deeper, broader, uncertainty) | Simon |
| Q3 | Show vocabulary expansion transparently | Bates |
| Q4 | Conservative bridge defaults | Cartwright |
| I1 | Support DOI, PMID, S2ID, arXiv | Panel consensus |
| I2 | Add PsycINFO for domain coverage | Kaplan |
| I3 | Abstract-only causal claims get warning badge | Cartwright |
| I4 | Citation suggestions with diversity | Bates |
| S1 | Credence stability + structural check | Simon |
| S2 | Oscillation → contested flag | Epistemologist |
| S3 | Publication bias in stability report | Cartwright |
| S4 | Frame stability as "given current evidence" | Epistemologist |

---

## FILES TO CREATE/MODIFY

### New Files

| File | Purpose |
|------|---------|
| `src/services/graph_api.py` | Graph export for visualization |
| `src/services/paper_fetcher.py` | Unified ingestion client |
| `src/services/stability_engine.py` | Stability detection and reporting |
| `src/services/query_parser.py` | NL query parsing |
| `src/services/query_response.py` | Response generation |
| `frontend/` | React application (new directory) |

### Modified Files

| File | Change |
|------|--------|
| `src/services/web_of_belief.py` | Add enabling_conditions, credence_history |
| `src/services/web_persistence.py` | Store credence history, detect oscillation |
| `app/main.py` | Add graph, search, ingestion endpoints |
| `contracts/ae_af/schemas/ae.belief.v1.schema.json` | Add enabling_conditions, source_depth |

### New Schemas

| Schema | Purpose |
|--------|---------|
| `ae.graph_export.v1.schema.json` | Graph visualization format |
| `ae.stability_report.v1.schema.json` | Stability report format |
| `ae.query_response.v1.schema.json` | NL query response format |

---

## ESTIMATED EFFORT

| Phase | Sprints | Days |
|-------|---------|------|
| A: Data Model & Backend | 4 | 10 |
| B: Evidence Explorer GUI | 4 | 10 |
| C: Query & Ingestion | 4 | 10 |
| D: Stopping & Reporting | 2 | 4 |
| **Total** | **14** | **34** |

---

## RISK MITIGATION

| Risk | Mitigation |
|------|------------|
| Cytoscape performance on large graphs | Implement node filtering; lazy loading |
| PsycINFO API may not be available | Fall back to Semantic Scholar which indexes psychology |
| LLM query parsing cost | Rule-based first; LLM only for unparseable |
| Publication bias estimation complexity | Start with simple null-result ratio; funnel plot later |

---

*Implementation begins with Phase A, Sprint A1.*
