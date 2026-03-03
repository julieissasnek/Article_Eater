# AG Task: Interactive EN/BN Visualization Explorer

*Date: 2026-03-02*
*Priority: P0 — David wants to use the system today*
*Estimated effort: 4-6 hours*

---

## Context

David wants to be able to explore the Epistemic Network (EN) and Bayesian Network (BN) interactively through the Streamlit interface. The current Communities page (Page 3) has basic vis.js network rendering but lacks:

1. **Topic-scoped subgraph extraction** — user enters a topic, sees only the relevant subgraph
2. **Warrant-type filtering** — filter edges by warrant type (7 types), show/hide by strength
3. **Credence trace** — click a belief and see *why* it has its credence (which warrants contribute)
4. **Theory comparison view** — compare how two T1 frameworks view the same domain
5. **Gap visualization** — highlight beliefs with low credence + high centrality (productive gaps)

## What Already Exists

- `src/services/network_service.py` — vis.js graph rendering service (force-directed, hierarchical, Barnes-Hut layouts; clustering by theory/community/epistemic level; node coloring by credence; edge properties for warrant type)
- `streamlit_app/pages/3_communities.py` — Community network visualization page
- `streamlit_app/pages/9_knowledge_base.py` — Search + browse interface
- `src/services/query_engine.py` — Core query execution
- `src/services/arbitrary_qa_handler.py` — Question classification (25+ question types)
- `data/web_persistence_v2.db` — SQLite with 3,420 beliefs, constraints, warrants
- `src/qa/confounder_risk_checker.py` — Risk assessment per belief
- `src/services/credence_intervals.py` — Confidence intervals for credences

## Deliverables

### 1. New Streamlit Page: `streamlit_app/pages/10_en_explorer.py`

**Layout**: Three-panel design
- **Left sidebar**: Topic search box + warrant type checkboxes + credence range slider + theory filter dropdown
- **Center**: vis.js graph (the subgraph matching filters)
- **Right panel**: Detail view for selected node (belief content, credence ± CI, scope conditions, contributing warrants, connected theories, source papers)

**Interactions**:
- Type a topic → extract relevant subgraph (use template_query_service or query_engine to find matching beliefs, then expand 1-2 hops)
- Click a node → populate right panel with belief details
- Double-click a node → expand its neighborhood (add connected beliefs to view)
- Toggle warrant type checkboxes → show/hide edge types
- Drag credence slider → filter nodes by credence range
- Color mode selector: by credence (green→red) / by theory (categorical) / by entrenchment (size)

### 2. Subgraph Extraction Service: `src/services/en_subgraph.py`

Functions needed:
- `extract_topic_subgraph(topic: str, max_nodes: int = 50, max_hops: int = 2) -> SubgraphData`
  - Find beliefs matching topic (fuzzy search on content)
  - Expand N hops along warrant edges
  - Return nodes + edges + metadata
- `extract_ego_subgraph(belief_id: str, radius: int = 2) -> SubgraphData`
  - All beliefs within N warrant-hops of a focal belief
- `extract_theory_comparison(theory_a: str, theory_b: str, domain: str = None) -> ComparisonData`
  - Beliefs assigned to each theory, shared domain overlap, conflicting predictions
- `get_credence_trace(belief_id: str) -> CredenceTrace`
  - Decompose credence into contributing warrants, each with d, ω, δ, source
- `find_productive_gaps(min_centrality: float = 0.3, max_credence: float = 0.5) -> List[GapNode]`
  - High-centrality, low-credence beliefs = productive research targets

### 3. Tests: `tests/test_en_explorer.py`

Cover:
- Subgraph extraction returns valid nodes/edges
- Topic search finds relevant beliefs
- Credence trace decomposes correctly
- Gap finder returns high-centrality low-credence nodes
- Edge filtering by warrant type works
- Theory comparison shows non-empty overlap

## Technical Notes

- vis.js is already loaded in the Streamlit app via streamlit-agraph or raw HTML components
- The database schema has: beliefs (id, content, credence_value, theory_id, scope, ...), constraints (source_id, target_id, type, ...), and warrant data
- Use `streamlit_components_v1` HTML component for vis.js if streamlit-agraph is too limited
- Keep the subgraph under 100 nodes for usability — use semantic zoom (show cluster summaries first, expand on click)
- The right panel should use `st.expander()` for progressive disclosure of belief details

## Priority Order

If you can only do some of these, prioritize:
1. Topic search → subgraph display (this is the core "ask a question, see the network" flow)
2. Click-to-select → belief detail panel
3. Warrant type filtering
4. Credence trace visualization
5. Theory comparison view
6. Gap visualization

## Example Interaction

User types: "ceiling height creativity"
→ System finds 8 beliefs mentioning ceiling height and creativity
→ Expands 1 hop → 23 connected beliefs (some about spatial volume, some about cognitive style)
→ Displays subgraph: 23 nodes, 47 edges
→ Nodes colored by credence (green = high, red = low)
→ User clicks "Higher ceilings promote abstract thinking (Meyers-Levy & Zhu, 2007)"
→ Right panel shows: credence 0.68 ± 0.09, theory: Predictive Processing, scope: Western adults in lab settings, 3 supporting warrants (MECHANISM d=0.80, EMPIRICAL_ASSOCIATION d=0.80, FUNCTIONAL d=0.65), 1 contradicting warrant
→ User double-clicks → expands to show connected thermal comfort and spatial volume beliefs

---

*This task should be done in a new Streamlit page so it doesn't break existing pages. All data access through existing services where possible.*
