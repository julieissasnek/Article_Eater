# MVP Demo Script

**Duration**: 10 minutes
**Audience**: Researchers interested in evidence synthesis
**Date**: 2026-02-11

---

## Setup Checklist (Before Demo)

```bash
# 1. Ensure you're in the Article Eater directory
cd /Users/davidusa/REPOS/Article_Eater_PostQuinean_v1

# 2. Verify tests pass
python3 -m pytest tests/test_web_accumulator.py tests/test_batch_processing.py -v

# 3. Start the Streamlit app
streamlit run streamlit_app/mvp/app.py
```

---

## Demo Flow (10 minutes)

### Part 1: Introduction (2 min)

**Say**: "Article Eater is a research tool that extracts evidence-backed rules from scientific papers and accumulates them into a coherent web of belief."

**Show**: Main page of Streamlit app
- Point to the metrics: Papers, Beliefs, Constraints, Coherence
- Explain: "These are live stats from our accumulated knowledge base"

**Key Points**:
- Post-Quinean foundherentist epistemology (beliefs support each other)
- Persistent accumulation across runs
- Each paper adds to a growing knowledge graph

---

### Part 2: Status Page (2 min)

**Navigate**: Click "Status" in sidebar

**Show**:
1. Key metrics at top (papers processed, beliefs, constraints)
2. Belief distribution charts (by level, by domain)
3. Processing history (recent papers)

**Say**: "The status page shows the health of our accumulated web. Notice how beliefs are distributed across epistemic levels - EMPIRICAL findings at the bottom, THEORETICAL beliefs at the top."

**Highlight**:
- Click "Refresh" to show live updates
- Expand "View All Processed Papers" to show paper list

---

### Part 3: Query Interface (4 min) ⭐ Main Demo

**Navigate**: Click "Query" in sidebar

**Demo Query 1**: "What affects attention in office environments?"

**Steps**:
1. Type the query
2. Click "Search"
3. Walk through results:
   - Headline answer with credence
   - Individual beliefs with confidence bars
   - Paper sources for each belief

**Say**: "The system parses natural language, searches the web, and returns beliefs ranked by relevance and credence. Notice the confidence scores - these come from evidence accumulation."

**Demo Query 2**: "Does natural light improve productivity?"

**Steps**:
1. Type query
2. Show the follow-up questions (expand)
3. Show any gaps identified (expand)

**Say**: "The system also suggests follow-up questions and identifies knowledge gaps - areas where we need more research."

**Example Queries to Have Ready**:
- "What reduces stress in workplaces?"
- "Effects of noise on concentration"
- "Benefits of biophilic design"

---

### Part 4: Gap Analysis (2 min)

**Navigate**: Click "Gaps" in sidebar

**Show**:
1. Domain coverage overview (colored metrics)
2. Individual gap cards with priorities
3. Suggested searches for each gap

**Say**: "The gaps page shows where our knowledge is thin. Red/yellow domains need more research. Each gap includes a suggested search to find relevant papers."

**Highlight**:
- HIGH priority gaps (expand one)
- The suggested search that could be sent to Article Finder
- How this drives the research pipeline

---

### Part 5: The Pipeline (Bonus if time)

**Show**: Terminal (not Streamlit)

```bash
# Show help
python scripts/process_papers.py --help

# Show config
cat scripts/process_config.yaml
```

**Say**: "Behind the scenes, a batch processor can iterate through papers automatically. It has circuit breakers to handle failures and persists everything to SQLite."

---

## Key Messages

1. **Accumulation**: Every paper adds to a growing, coherent knowledge base
2. **Uncertainty**: We track credence and uncertainty, not just yes/no
3. **Gaps**: The system identifies what we DON'T know, not just what we know
4. **Integration**: Article Finder → Article Eater → Web of Belief → Actionable insights

---

## Q&A Preparation

**Q: How does credence differ from confidence?**
A: Credence is degree of belief (0-1). Confidence describes our certainty about that credence (meta-uncertainty).

**Q: What if papers disagree?**
A: The system tracks conflicts as constraints. Disagreement lowers overall coherence and flags tensions.

**Q: How do you handle theory-laden observations?**
A: We track epistemic levels. EMPIRICAL beliefs are closer to observation; THEORETICAL beliefs are more entrenched but can still be revised.

**Q: What theories are built in?**
A: ART (Attention Restoration Theory), SRT (Stress Recovery Theory), Biophilia, Prospect-Refuge, among others.

---

## Fallback Scenarios

**If backends fail**: App shows mock data with clear indicator. Demo still works.

**If query returns no results**: Use this to show gap identification feature.

**If app crashes**: Have backup screenshots in `docs/screenshots/`

---

## Post-Demo

**Leave them with**:
- Link to repository
- This demo script for reference
- Invitation to process their own papers

**Next steps for interested parties**:
1. Try the CLI: `python -m src.cli.query "your question"`
2. Add papers to the batch processor
3. Review the accumulated web in `data/accumulated_web.json`
