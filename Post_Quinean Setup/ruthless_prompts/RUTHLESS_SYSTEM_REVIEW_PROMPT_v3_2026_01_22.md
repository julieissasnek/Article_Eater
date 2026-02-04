# Ruthless System Review v3: Article Eater Post-Quinean V21

**Date**: January 22, 2026 (Post Phase 1 Fixes)
**Review Type**: Architecture, ML/AI Scalability, GUI/UX & User Workflow Audit
**Status**: Post-ChatGPT and local panel review
**Version**: 3.0 (Added GUI/UX and User Workflow section)

---

## Recent Fixes Applied (Phase 1)

1. **CORS Security**: Removed wildcard `"*"` from allow_origins (C3 fix)
2. **Router Wiring Test**: Added test_main_wiring.py to prevent "green tests with broken deployment"
3. **Auth Model Documentation**: Documented local-only research tool security model in CLAUDE.md
4. **Version Alignment**: Updated requirements.txt header to V21.0.0

---

## Expert Panel (16 Experts + UX Specialists)

### Core Methodological Panel
1. **Dr. Judea Pearl** — Causality, Bayesian networks, do-calculus
2. **Dr. Nancy Cartwright** — Philosophy of science, evidence portability
3. **Dr. Herbert Simon** — Bounded rationality, satisficing, system design
4. **Dr. Marcia Bates** — Information science, search behavior
5. **Dr. Rachel Kaplan** — Environmental psychology (domain expert)

### Technical & Governance Experts
6. **Dr. Leslie Lamport** — Distributed systems, formal methods
7. **Dr. Barbara Liskov** — Software design, abstraction, type systems
8. **Dr. Fred Brooks** — System architecture, software engineering
9. **Dr. David Parnas** — Module design, information hiding
10. **Dr. Peter Naur** — Programming as theory building

### AI/CS Leaders
11. **Dr. Andrew Ng** — ML systems, MLOps, data-centric AI
12. **Dr. Andrej Karpathy** — Deep learning, LLM applications
13. **Dr. Ilya Sutskever** — Neural scaling, AI safety
14. **Dr. Yann LeCun** — Self-supervised learning, world models
15. **Dr. Peter Norvig** — AI at scale, probabilistic programming
16. **Dr. Jeff Dean** — Large-scale systems, ML infrastructure

---

## NEW: GUI/UX and User Workflow Review

### Current UI Components

1. **Evidence Explorer** (`frontend/evidence-explorer.html`)
   - ~921 lines single-file SPA
   - Cytoscape.js graph visualization
   - 7 filter facets (source, tier, credence, year, study type, framework, contested)
   - Traffic-light credence indicators
   - Three-level progressive disclosure (headline → summary → detail)

2. **Ingestion Interface** (`frontend/ingestion.html`)
   - Article submission form
   - Processing status display

3. **Admin Dashboard** (`src/gui/templates/admin.html`)
   - System statistics
   - Job queue monitoring

### User Workflow Questions

For each expert, consider:

1. **Current Workflow Adequacy**:
   - Who are the target users? (Researchers, students, practitioners?)
   - What is the typical workflow? (Search → Filter → Explore → Export?)
   - Where are the friction points in the current UI?

2. **Output Delivery**:
   - How should evidence summaries be delivered? (Dashboard, reports, exports?)
   - What export formats matter? (PDF, CSV, BibTeX, JSON?)
   - Should there be email/notification of new evidence?

3. **AI-Enhanced UX Opportunities**:
   - Where would conversational AI (chat interface) add value?
   - Could AI pre-filter or recommend evidence?
   - How might AI explain causal classifications to non-experts?
   - Should AI generate narrative summaries of contested evidence?

4. **Accessibility & Cognitive Load**:
   - Are 7 filter facets too many? (Simon's 7±2 rule)
   - Is the graph visualization accessible to colorblind users?
   - How do we support users with different expertise levels?

---

## Questions by Expert

### For Pearl (Causality)
1. How should causal graphs be visualized to non-experts?
2. Should the UI distinguish do(X) interventions from P(Y|X) observations?
3. How can we make causal tier classifications interpretable?

### For Cartwright (Evidence)
1. How should bridge warrant strength be communicated visually?
2. Should the UI show "why this evidence transfers" explanations?
3. How do we communicate measurement modality differences?

### For Simon (Bounded Rationality)
1. Is 7 filter facets within cognitive limits? Should we group into Basic/Advanced?
2. Are the credence presets (High/Medium/Low) effective satisficing aids?
3. How do we prevent information overload in the detail panel?

### For Bates (Information Science)
1. Does the current search support berrypicking behavior?
2. How should facets be organized for exploratory search?
3. Is the vocabulary expansion transparent enough?

### For Kaplan (Domain Expert)
1. What visualizations do neuroarchitecture researchers actually need?
2. How should conflicting evidence about biophilic design be presented?
3. What export formats matter for design practitioners?

### For Lamport (Formal Methods)
1. How should consistency be communicated during concurrent updates?
2. Should users see "snapshot as of" timestamps?
3. How do we visualize credence propagation (INV-W8)?

### For Liskov (Software Design)
1. Is the API response structure conducive to good UI components?
2. Should the UI use optimistic updates or wait for server confirmation?
3. How do we handle partial data states gracefully?

### For Brooks (Architecture)
1. Is the frontend-backend separation clean enough?
2. What's the MVP vs full-feature scope for the UI?
3. How do we avoid second-system syndrome in the GUI?

### For Parnas (Module Design)
1. Should UI components mirror the service decomposition?
2. How do we prevent UI logic duplication?
3. What's the information hiding boundary for API clients?

### For Naur (Theory Building)
1. Can a new user understand the system's theory from the UI alone?
2. Are the worked examples in docs reflected in the UI?
3. How do we communicate "what this system doesn't do"?

---

## NEW: AI/UX Integration Questions

### For Andrew Ng (ML/UX)
1. **Data Collection for UX**: How should we collect user feedback on classifications?
2. **Active Learning UI**: Can users flag incorrect classifications to improve the system?
3. **Personalization**: Should the UI adapt to individual researcher interests?

### For Andrej Karpathy (LLM/UX)
1. **Chat Interface**: Would a "Ask about this evidence" chat be valuable?
2. **Prompt Patterns**: How should users phrase natural language queries?
3. **Explanation Generation**: Can LLMs explain why evidence is contested?

### For Ilya Sutskever (Safety/UX)
1. **Overconfidence Warning**: How do we prevent users from over-trusting CAUSAL tier?
2. **Uncertainty Communication**: How should epistemic uncertainty be visualized?
3. **Corpus Bias Display**: Should the UI show what topics are under-represented?

### For Yann LeCun (World Models/UX)
1. **Mental Model Alignment**: Does the UI help users build an accurate mental model?
2. **Coherence Visualization**: How should the web-of-belief coherence be shown?
3. **Predictive UI**: Can the system suggest what user wants to explore next?

### For Peter Norvig (AI Systems/UX)
1. **Query Understanding**: How should natural language queries be disambiguated in UI?
2. **Ranking Display**: How do we show why certain evidence ranks higher?
3. **Search Refinement**: How do we support iterative query refinement?

### For Jeff Dean (Infrastructure/UX)
1. **Performance Perception**: How do we make slow operations feel responsive?
2. **Caching Strategy**: What should be cached client-side for speed?
3. **Offline Mode**: Should the UI support offline evidence exploration?

---

## Deliverables Requested

For each expert, provide:
1. **Assessment** (APPROVE / MODIFY / REJECT)
2. **Priority** (CRITICAL / HIGH / MEDIUM / LOW)
3. **GUI/UX specific recommendations**
4. **AI-enhanced UX opportunities**
5. **User workflow improvements**

---

## Files for Review

### Frontend
- `frontend/evidence-explorer.html` (921 lines - main UI)
- `frontend/ingestion.html` (submission UI)
- `src/gui/templates/admin.html` (admin dashboard)

### API (affects UX)
- `app/routes/query.py` (natural language query endpoints)
- `app/routes/reports.py` (report generation)
- `app/routes/web_of_belief.py` (graph and search endpoints)

### Services (determine what UI can show)
- `src/services/query_response.py` (response structure)
- `src/services/reporting.py` (report content)
- `src/services/graph_api.py` (graph export for Cytoscape)
