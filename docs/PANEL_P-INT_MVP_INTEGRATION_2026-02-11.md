# Panel Consultation: MVP Integration Strategy

**Date**: 2026-02-11
**Panel ID**: P-INT (Integration)
**Purpose**: Plan robust integration of Article Finder → Article Eater → Epistemic Web → Inference pipeline for proof-of-concept demo

---

## Panel Composition

| Expert | Expertise | Perspective |
|--------|-----------|-------------|
| **Fred Brooks** | Software engineering, systems architecture | "No silver bullet", conceptual integrity, MVP discipline |
| **Martin Fowler** | Enterprise integration patterns, refactoring | Contract-first design, continuous integration |
| **Kent Beck** | XP, TDD, simple design | "Make it work, make it right, make it fast" |
| **Barbara Liskov** | Abstraction, modularity, interfaces | Data abstraction, substitutability |
| **David Parnas** | Information hiding, modular design | Secrets, interfaces, change anticipation |
| **Michael Nygard** | Production systems, stability patterns | Release it, circuit breakers, bulkheads |

---

## Problem Statement

We have functioning components that aren't connected:

```
CURRENT STATE:
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│ Article Finder  │     │ Article Eater   │     │ Web of Belief   │
│ (16K papers)    │ ──? │ (115 rules)     │ ──? │ (0 persistent)  │
│ SQLite DB       │     │ SQLite + JSON   │     │ In-memory only  │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                         │
                                                         ▼
                                               ┌─────────────────┐
                                               │ Query/Inference │
                                               │ (Not connected) │
                                               └─────────────────┘
```

**Goal**: Working demo that shows:
1. Papers → Rules → Beliefs → Web (accumulating)
2. Query the web, get answers with confidence and sources
3. Identify gaps → suggest searches
4. Basic GUI to visualize

---

## Questions for Panel

### Q1: What's the minimum viable integration architecture?

### Q2: How should we handle persistence across runs?

### Q3: What contracts/interfaces need to be specified first?

### Q4: What's the right testing strategy for integration?

### Q5: What should the MVP GUI show?

### Q6: How do we avoid over-engineering while building for extensibility?

---

## Panel Responses

### Fred Brooks (Systems Architecture)

**On MVP scope:**
"The hardest single part of building a software system is deciding precisely what to build. No other part of the conceptual work is as difficult as establishing the detailed technical requirements. No other part of the work so cripples the resulting system if done wrong."

**Recommendation for Q1:**
Build the **surgical team** model - one main pipeline with supporting utilities. Don't try to build a general-purpose platform. Build the ONE use case that demonstrates value:

> **Use Case 0**: "Given 100 CNfA papers, build a queryable belief network that can answer 'What affects attention in offices?' with confidence levels and citations."

Everything in MVP must serve Use Case 0. Everything else is post-demo.

**On Q6 (avoiding over-engineering):**
"Plan to throw one away; you will anyhow." Build the simplest thing that works, then iterate. The first system exists to learn what you actually need.

---

### Martin Fowler (Integration Patterns)

**On Q2 (persistence):**
Use the **Event Sourcing** pattern light:
- Don't just save state; save the events that produced the state
- `belief_added`, `constraint_created`, `credence_updated`, `paper_processed`
- Can replay to any point; can debug why web looks the way it does

```python
# events.jsonl (append-only)
{"event": "paper_processed", "paper_id": "doi:10.xxx", "rules_extracted": 3, "ts": "..."}
{"event": "belief_added", "belief_id": "b_001", "content": "...", "from_rule": "r_001", "ts": "..."}
{"event": "constraint_added", "a": "b_001", "b": "b_002", "type": "SUPPORTS", "ts": "..."}
```

**On Q3 (contracts):**
Define these interfaces FIRST:

1. **AF→AE Contract**: What does Article Finder provide to Article Eater?
   ```json
   {
     "paper_id": "string",
     "title": "string",
     "abstract": "string",
     "pdf_path": "string|null",
     "metadata": {...}
   }
   ```

2. **AE→Web Contract**: What does extraction produce?
   ```json
   {
     "rule_id": "string",
     "paper_id": "string",
     "belief_content": "string",
     "epistemic_level": "EMPIRICAL|THEORETICAL",
     "confidence": 0.0-1.0,
     "evidence": {...}
   }
   ```

3. **Query→Web Contract**: What can you ask?
   ```json
   {
     "query_type": "what_affects|evidence_for|confidence_in|gaps_in",
     "target": "string",
     "filters": {...}
   }
   ```

---

### Kent Beck (Simple Design)

**On Q1 (minimum viable):**
Four rules of simple design:
1. **Passes the tests** - Define acceptance tests for Use Case 0 first
2. **Reveals intention** - Clear names, obvious flow
3. **No duplication** - One place for each concept
4. **Fewest elements** - Remove anything not serving Use Case 0

**Concrete MVP:**
```
Day 1: Make it work (ugly, hardcoded, one script)
Day 2: Make it right (extract functions, add tests)
Day 3: Make it observable (add logging, basic GUI)
```

**On Q4 (testing):**
One acceptance test drives MVP:
```python
def test_use_case_0():
    # Given: 100 CNfA papers
    papers = load_test_corpus("tests/fixtures/100_cnfa_papers.json")

    # When: Process through full pipeline
    web = process_papers_to_web(papers)

    # Then: Can answer the canonical question
    result = web.query("What affects attention in offices?")

    assert len(result.beliefs) > 0
    assert all(b.confidence > 0 for b in result.beliefs)
    assert all(len(b.sources) > 0 for b in result.beliefs)

    # And: Can identify gaps
    gaps = web.identify_gaps()
    assert 'suggested_searches' in gaps
```

Write this test FIRST. Make it pass. That's MVP.

---

### Barbara Liskov (Abstraction)

**On Q3 (interfaces):**
Define abstract interfaces that hide implementation:

```python
class PaperRepository(ABC):
    """Abstraction over paper storage."""
    @abstractmethod
    def get_paper(self, paper_id: str) -> Paper: ...
    @abstractmethod
    def get_papers_for_processing(self, limit: int) -> List[Paper]: ...
    @abstractmethod
    def mark_processed(self, paper_id: str, result: ProcessingResult): ...

class BeliefStore(ABC):
    """Abstraction over belief persistence."""
    @abstractmethod
    def add_belief(self, belief: Belief) -> str: ...
    @abstractmethod
    def get_beliefs_about(self, topic: str) -> List[Belief]: ...
    @abstractmethod
    def save_state(self) -> None: ...
    @abstractmethod
    def load_state(self) -> None: ...

class QueryEngine(ABC):
    """Abstraction over inference."""
    @abstractmethod
    def query(self, question: str) -> QueryResult: ...
    @abstractmethod
    def identify_gaps(self) -> GapReport: ...
```

MVP can use simple implementations (JSON files, in-memory). Later swap in sophisticated ones without changing callers.

---

### David Parnas (Information Hiding)

**On module boundaries:**
Each module should hide a "secret":

| Module | Secret Hidden | Interface |
|--------|---------------|-----------|
| `paper_store` | How papers are stored (SQLite vs. files) | `get_paper(id)`, `list_papers(filter)` |
| `extractor` | How rules are extracted (LLM prompt, model) | `extract_rules(paper) -> List[Rule]` |
| `web_builder` | How beliefs accumulate (Quinean details) | `add_rule(rule)`, `get_web_state()` |
| `query_engine` | How queries are resolved (coherence calc) | `query(question) -> Answer` |
| `gap_finder` | How gaps are identified (VOI calc) | `find_gaps() -> List[Gap]` |

**On Q6 (change anticipation):**
Things likely to change:
- LLM model used for extraction (hide behind `Extractor` interface)
- Storage backend (hide behind `Repository` interfaces)
- Query language (start simple, interface allows extension)

Things unlikely to change:
- Core epistemic concepts (Belief, Constraint, Coherence)
- Basic flow (papers → rules → beliefs → queries)

Invest in interfaces around the volatile parts.

---

### Michael Nygard (Production Readiness)

**On Q5 (MVP GUI):**
Don't build a full GUI. Build **three views**:

1. **Pipeline Status** (Streamlit page):
   - Papers: 16K total, 115 processed, 4800 on-topic
   - Rules: 115 extracted, 85 integrated into web
   - Beliefs: 120 in web, 15 theoretical, 105 empirical
   - Last run: 2026-02-11 14:30

2. **Query Interface** (Streamlit page):
   - Text box: "What affects attention?"
   - Results: List of beliefs with confidence bars, expandable sources
   - "Confidence is based on N supporting studies..."

3. **Gap Report** (Streamlit page):
   - "Low coverage areas: Thermal × Creativity (2 beliefs, 0.3 avg confidence)"
   - "Suggested searches: 'thermal comfort creative performance office'"
   - Button: "Add to search queue"

**On stability for demo:**
- Use **timeouts** on LLM calls (extraction can hang)
- Use **circuit breakers** (if extraction fails 3x, skip paper)
- Save state **frequently** (after each paper, not just at end)
- Log **everything** (you will need to debug during demo)

---

## Synthesis: MVP Plan

### Phase 0: Contracts (Day 1)
Define JSON schemas for:
- [ ] `af_paper.v1.json` - Paper from Article Finder
- [ ] `ae_rule.v1.json` - Already exists, verify
- [ ] `web_belief.v1.json` - Belief ready for web
- [ ] `query_request.v1.json` - Query input
- [ ] `query_response.v1.json` - Query output
- [ ] `gap_report.v1.json` - Gap identification output

### Phase 1: Persistence (Day 2)
- [ ] Create `data/web_state.json` - persistent belief store
- [ ] Add `events.jsonl` - event log for debugging
- [ ] Implement `BeliefStore` with save/load
- [ ] Test: Can save web, restart, load, query

### Phase 2: Pipeline Connection (Day 3-4)
- [ ] Create `scripts/process_papers.py` - batch processor
- [ ] Wire: AF papers → AE extraction → Web accumulation
- [ ] Add progress tracking (papers processed, rules extracted, beliefs added)
- [ ] Process 100 test papers end-to-end

### Phase 3: Query Interface (Day 5)
- [ ] Create `src/services/query_engine.py`
- [ ] Implement `query(question) -> beliefs with confidence`
- [ ] Implement `identify_gaps() -> gap report`
- [ ] CLI: `python -m src.cli.query "What affects attention?"`

### Phase 4: Minimal GUI (Day 6)
- [ ] Streamlit app with 3 pages (status, query, gaps)
- [ ] Basic visualizations (confidence bars, source links)
- [ ] Demo-ready presentation

### Phase 5: Polish (Day 7)
- [ ] Error handling, timeouts, logging
- [ ] Documentation for demo
- [ ] 10-minute demo script

---

## Post-Demo Improvements (Parking Lot)

| ID | Improvement | Rationale |
|----|-------------|-----------|
| POST-1 | Full PDF extraction (not just abstracts) | More content, but slower |
| POST-2 | Citation tracking / refinement chains | Epistemic accuracy |
| POST-3 | Multi-theory comparison views | Research utility |
| POST-4 | Scholar AI integration for gap-filling | Closed loop |
| POST-5 | User authentication / multi-user | Production use |
| POST-6 | Advanced visualizations (web graph, timeline) | Understanding |
| POST-7 | API endpoints (not just GUI) | Integration |
| POST-8 | Foundational book extraction (full secondary material) | Coverage |
| POST-9 | All pending ECB-F* enhancements | Epistemic sophistication |
| POST-10 | Individual differences / cultural meaning reintegration | Personalization |

---

## Panel Verdict

**Unanimous recommendation**: Focus ruthlessly on Use Case 0. Build the simplest end-to-end pipeline that answers one question with confidence and sources. Everything else is post-demo.

**Critical path**:
1. Persistent web state (without this, nothing accumulates)
2. Batch processing script (without this, can't populate)
3. Query interface (without this, can't demo value)

**Time estimate**: 5-7 focused days for working MVP.

---

## Appendix: Acceptance Criteria for Demo

### Must Have (MVP)
- [ ] Process 100 papers → rules → beliefs
- [ ] Query: "What affects attention in offices?" returns beliefs
- [ ] Each belief shows confidence and paper sources
- [ ] Gap report shows under-covered areas
- [ ] Basic Streamlit GUI shows all three

### Should Have (if time)
- [ ] Process 500 papers
- [ ] 3+ different query types working
- [ ] Suggested search terms from gaps

### Won't Have (post-demo)
- Full PDF extraction
- Citation tracking
- Multi-user support
- Production deployment

---

*Panel consultation complete. Proceed with Phase 0: Contracts.*
