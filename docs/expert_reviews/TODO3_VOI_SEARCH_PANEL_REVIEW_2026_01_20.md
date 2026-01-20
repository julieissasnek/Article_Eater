# Expert Panel Review: TODO 3 — VOI-Driven Article Search

**Date:** January 20, 2026
**Sprint:** TODO 3, Phase A (Expert Consultation)
**Status:** Panel Deliberation

---

## Panel Composition

- **Dr. Judea Pearl** — Bayesian networks, causal inference, information value
- **Dr. Nancy Cartwright** — Philosophy of science, evidence, capacities
- **Dr. Herbert Simon** — Bounded rationality, search, satisficing
- **Dr. Marcia Bates** — Information science, search strategies, berrypicking
- **Dr. Rachel Kaplan** — Environmental psychology (domain expert)
- **Dr. C. Lee Giles** — Information retrieval, citation networks (invited for this TODO)

---

## Part I: Independent Reflection on the Problem

*Each panelist reflects on the VOI-driven search problem from their own perspective, before reviewing the proposed approach.*

---

### Dr. Judea Pearl

**On the Nature of the VOI-Driven Search Problem:**

Value of Information is a decision-theoretic concept. The value of obtaining information X is the expected improvement in decision quality from knowing X versus not knowing X.

In this context, we're asking: Given the current state of the web, which new articles would most improve the web's quality? Quality here means: accuracy of credences, completeness of coverage, resolution of tensions.

From my causal perspective, I see several distinct kinds of valuable information:

**1. Causal identification information:** Papers that let us distinguish causal from correlational relationships. These are especially valuable because causal knowledge supports intervention reasoning, while correlational knowledge only supports prediction.

**2. Confounder resolution information:** Papers that address potential confounds in existing evidence. If we believe "X → Y" but suspect confounder Z, papers that control for Z are highly valuable.

**3. Mechanism specification information:** Papers that fill in the "how" between cause and effect. If we know "nature → stress reduction" but not the mechanism, papers proposing and testing mechanisms are valuable.

**4. External validity information:** Papers from different populations, settings, or methodologies that test whether findings generalize.

Standard search doesn't distinguish these types. A VOI-driven search should prioritize based on what kind of information would most improve the web.

**Key insight:** VOI isn't just about filling gaps—it's about filling the *right* gaps. A gap in causal identification is more valuable to fill than a gap in replication of already-strong effects.

---

### Dr. Nancy Cartwright

**On the Nature of the VOI-Driven Search Problem:**

I want to frame this problem in terms of **evidential needs**. The web makes claims. Each claim has evidential needs—what would strengthen or weaken it?

Types of evidential needs:

**1. Existence evidence:** Does the effect exist at all? (Basic replication)

**2. Scope evidence:** Where does the effect hold? (Population, setting, context)

**3. Mechanism evidence:** How does the effect work? (Mediators, pathways)

**4. Robustness evidence:** Is the effect confounded? (Alternative explanations)

**5. Magnitude evidence:** How big is the effect? (Precision of effect size)

Different beliefs have different evidential needs. A newly proposed effect needs existence evidence. A well-established effect needs scope evidence. A contested effect needs robustness evidence.

The search system should diagnose what each belief needs and search for papers that provide it.

**Key insight:** Don't search generically for "papers about X." Search specifically for "papers that test whether X holds in population Y" or "papers that control for confounder Z."

Another crucial point: **Absence of evidence is evidence of absence** (to some degree). If we search thoroughly for papers on topic X and find nothing, that's informative—it suggests X is under-studied or that findings on X might not replicate. The search system should track what it looked for and didn't find, not just what it found.

---

### Dr. Herbert Simon

**On the Nature of the VOI-Driven Search Problem:**

From a search theory perspective, this is a **sequential decision problem**. At each step, we choose a search action (a query to execute). We observe results. We update our beliefs about where valuable papers are. We repeat.

The challenge is **exploration vs. exploitation**:
- **Exploitation:** Search in areas where we've found valuable papers before
- **Exploration:** Search in new areas that might have valuable papers

Pure exploitation misses novel relevant areas. Pure exploration wastes effort on irrelevant areas. Optimal search balances both.

I would model this as a **multi-armed bandit** problem. Each search strategy is an "arm." We maintain estimates of each strategy's yield (relevant papers per query). We allocate search effort to maximize expected total yield.

Practical implication: Don't just design queries—design **search strategies** and track which strategies work for which gap types. Over time, the system learns which strategies are productive.

**Key insight:** The goal isn't to find the single best query. It's to develop a repertoire of search strategies and allocate effort across them efficiently.

Also: **Satisficing applies.** We don't need to find *every* relevant paper. We need to find *enough* papers to adequately constrain beliefs. Define "adequate" and stop when you reach it.

---

### Dr. Marcia Bates

**On the Nature of the VOI-Driven Search Problem:**

From information retrieval research, I see this as a **complex search task** requiring multiple strategies. My "berrypicking" model is relevant: real information seeking isn't a single query but an evolving process where each result informs the next query.

**Search strategies for scientific literature:**

1. **Subject searching:** Standard keyword search on topic
2. **Citation searching:** Follow citations forward and backward from known relevant papers
3. **Author searching:** Find other work by authors of relevant papers
4. **Journal browsing:** Explore journals that publish relevant content
5. **Related records:** Use database "similar to" features
6. **Footnote chasing:** Mine bibliographies of known papers

For CNfA, I'd add:

7. **Cross-disciplinary searching:** Search in neuroscience, psychology, architecture databases with translated terminology
8. **Grey literature:** Conference proceedings, dissertations, reports
9. **Preprint searching:** arXiv, PsyArXiv, OSF Preprints for recent work

A VOI-driven system should employ all these strategies, not just keyword search. Different strategies have different strengths:
- Subject search: High recall, lower precision
- Citation search: High relevance for related work
- Author search: Good for research programs
- Cross-disciplinary: Essential for bridging evidence

**Key insight:** The search system needs a **portfolio of strategies**, not a single approach. Different gaps call for different strategies.

Another critical point: **Query formulation is hard.** Researchers spend years learning how to search effectively. The system can't assume users will write good queries. It should generate queries automatically from gap specifications, using domain knowledge.

---

### Dr. Rachel Kaplan

**On the Nature of the VOI-Driven Search Problem:**

Let me reflect on why current search fails for CNfA and what would actually help.

**Why current search fails:**

1. **Vocabulary fragmentation:** The same phenomenon has different names across fields:
   - "Stress recovery" (CNfA) = "Autonomic restoration" (physiology) = "Relaxation response" (psychology)
   - We miss papers using unfamiliar vocabulary

2. **Discipline silos:** Relevant work appears in architecture, psychology, neuroscience, healthcare design, human factors, forestry, and more. No single database covers all.

3. **Theory vs. application:** Theoretical neuroscience papers might inform CNfA but wouldn't mention "architecture" or "design." We miss fundamental science.

4. **Null results invisible:** Publication bias means null results are hard to find—but they're exactly what we need for calibration.

5. **Historical literature:** Foundational papers from before digital indexing may be missed.

**What papers do we actually need?**

For **strengthening existing knowledge:**
- Replications in new populations
- Replications with different measures
- Longitudinal studies (most evidence is cross-sectional)

For **challenging existing knowledge:**
- Studies with null results
- Studies in non-WEIRD populations
- Studies with rigorous confound control

For **extending knowledge:**
- Studies of mechanisms (not just effects)
- Studies of moderators (what conditions matter)
- Studies in real-world settings (not just labs)

For **bridging theories:**
- Studies that test multiple theories simultaneously
- Studies that measure constructs from different frameworks
- Theoretical papers that relate frameworks

**Key insight:** We need to search strategically for *what's missing*, not just for *more of the same*. The system should diagnose gaps and search to fill them specifically.

---

### Dr. C. Lee Giles

**On the Nature of the VOI-Driven Search Problem:**

From information retrieval and bibliometric perspectives, let me reflect on the technical challenges.

**Search challenges for scientific literature:**

1. **Semantic gap:** The query (an epistemic gap description) is in a different language than the documents (scientific papers). Bridging this gap requires sophisticated translation.

2. **Quality variation:** Not all papers are equal. Search should prioritize high-quality, high-impact sources. But impact metrics (citations) bias toward old papers and popular topics.

3. **Recency vs. relevance:** Recent papers may be more relevant but have fewer citations. Old papers are well-cited but may be superseded.

4. **Full-text vs. metadata:** Metadata search (titles, abstracts) is fast but incomplete. Full-text search is comprehensive but noisy. Optimal search uses both.

5. **Multi-source integration:** Different databases (PubMed, Web of Science, Semantic Scholar, Google Scholar) have different coverage and APIs. Comprehensive search requires multi-source integration.

**Technical approaches:**

1. **Query expansion:** Automatically broaden queries with synonyms, related terms, and broader/narrower concepts
2. **Dense retrieval:** Use neural embeddings to find semantically similar papers even without keyword overlap
3. **Citation graph:** Propagate relevance through citation networks (papers cited by relevant papers are more likely relevant)
4. **Learning to rank:** Train a model to rank papers by relevance to the gap type

**Key insight:** This isn't a single search problem—it's an **information integration** problem. The system needs to:
1. Translate gaps into queries
2. Execute queries across multiple sources
3. Aggregate and deduplicate results
4. Rank by expected information value
5. Track what was searched and what was found

Also: **Feedback is essential.** When papers are acquired and processed, the system learns whether they were actually useful. This feedback should improve future search.

---

## Part II: Panel Review of Proposed Approach

*The panel has now read the implementation team's proposed approach from `STRATEGIC_TODOS_PROBLEM_ANALYSIS_2026_01_20.md`.*

---

### Panel Discussion

**Dr. Pearl:** The proposal's gap typing (scope, mechanism, bridge, replication, null, theory challenge) is good but incomplete. I'd add:
- **Causal identification gap:** We have correlational evidence but need experimental evidence
- **Confounder gap:** We suspect confounder C but have no studies controlling for it
- **Mediator gap:** We hypothesize mediator M but have no studies testing it

These are specifically about the causal structure, which is distinct from the types listed.

**Dr. Cartwright:** The proposal correctly identifies that different gap types need different search strategies. I'd push further: the search strategy should be *generated from* the gap specification, not just selected from a menu. If the gap is "SRT-ART bridge needs empirical covariance," the system should generate queries like "stress recovery AND attention restoration AND (nature OR environment)" automatically.

**Dr. Simon:** The proposal mentions VOI scores but doesn't specify how to compute them. I'd recommend starting simple:
- VOI = Uncertainty_reduction × Credibility_importance
- Uncertainty_reduction: How much would a typical paper reduce uncertainty?
- Credibility_importance: How central is this belief to the web?

Refine as you learn what predicts actual value.

**Dr. Bates:** The proposal mentions cross-field vocabulary mapping, which is essential. But the example vocabulary file is incomplete. I'd recommend:
1. Start with the 20 most important CNfA concepts
2. Manually identify equivalents in psychology, neuroscience, architecture
3. Use embeddings to automatically expand
4. Continuously refine based on search performance

Also: the proposal mentions multiple data sources but doesn't specify an integration strategy. Semantic Scholar should be primary (free API, good coverage). PubMed for health-related queries. Google Scholar as fallback for hard-to-find items.

**Dr. Kaplan:** The proposal focuses on finding papers but doesn't discuss what happens next. Acquisition is expensive (reading, extracting, integrating). The system should estimate not just "is this paper relevant?" but "is this paper worth the acquisition cost?" A paper that's slightly relevant but easy to process may be more valuable than a highly relevant paper that's impenetrable.

**Dr. Giles:** The proposal's query generation approach is reasonable. I'd add **dense retrieval** as a complement to keyword search. Use Semantic Scholar's semantic search API or embed the gap description and find papers with similar embeddings. This catches papers that use different vocabulary but address the same concept.

---

## Part III: Responses to Specific Questions

---

### Q1: How do we estimate VOI without knowing what we'll find?

**Dr. Pearl:** Use expected value. Estimate:
- P(finding relevant paper | search effort)
- Utility of relevant paper (uncertainty reduction × belief importance)
- Cost of search effort

VOI = P(relevant) × Utility - Cost

For novel searches, use priors from similar gap types. Update as you accumulate experience.

**Dr. Simon:** Start with coarse estimates and refine. Track:
- Which gap types yield relevant papers most often?
- Which search strategies have best precision/recall?
- Which sources have best coverage for which topics?

Use this historical data to estimate VOI for new gaps.

**Dr. Bates:** Estimate from **search yield curves**. For each strategy, track: How many relevant papers in top 10? Top 50? Top 100? This tells you the expected value of additional search effort.

---

### Q2: How do we balance exploration vs. exploitation?

**Dr. Simon:** Classic explore/exploit tradeoff. I recommend **epsilon-greedy**:
- With probability 0.8: Use best-performing strategy for this gap type
- With probability 0.2: Try a random strategy (exploration)

Adjust epsilon based on how much you're learning. If strategies are well-characterized, increase exploitation. If still discovering what works, increase exploration.

**Dr. Giles:** Also consider **diminishing returns**. The first search for a topic yields many relevant papers. The tenth search yields fewer. Track cumulative yield per gap type and shift effort to under-explored gaps.

---

### Q3: What's the right granularity for cross-field vocabulary?

**Dr. Bates:** Aim for **conceptual equivalence**, not synonym lists. Two terms are equivalent if papers using either term would be relevant to the same gap.

Levels of granularity:
- **Coarse:** "stress" maps to "stress" across all fields
- **Medium:** "stress recovery" maps to "autonomic restoration," "relaxation response," "stress resilience"
- **Fine:** "salivary cortisol decrease" maps to "HPA axis down-regulation"

Medium granularity is probably right for initial implementation. Fine granularity for high-priority concepts.

**Dr. Kaplan:** From domain knowledge, priority concepts for vocabulary mapping:
1. Stress / stress recovery / restoration
2. Attention / attention restoration / cognitive fatigue
3. Nature / natural environment / biophilic elements
4. Built environment / architecture / space
5. Wellbeing / wellness / health outcomes

Start with these five concept families.

---

### Q4: How do we distinguish "no papers exist" from "our search was bad"?

**Dr. Bates:** This is the **recall problem**. You can never be certain you've found everything. But you can increase confidence:

1. **Multiple strategies:** If keyword, citation, and semantic search all return nothing, the gap is likely genuinely unfilled
2. **Expert validation:** Ask domain experts: "We found nothing on X. Does that match your knowledge?"
3. **Hedged reporting:** Say "No papers found using strategies A, B, C" not "No papers exist"

**Dr. Cartwright:** Importantly: "No papers found" is itself information. If a simple, obvious gap has no literature, that tells us:
- The question might be uninteresting to researchers
- Or the phenomenon might be difficult to study
- Or the finding might be null and unpublished

Record "no papers found" as a fact in the system. It's evidence about the state of the literature.

**Dr. Giles:** Technical approach: Compare your recall to **expected recall**. If Semantic Scholar has 200M papers and you're searching a reasonable scientific topic, you expect to find *something*. If you find nothing, either the topic is extremely niche or your queries are wrong.

One diagnostic: Try searching for a known relevant paper. If your queries don't retrieve papers you know exist, the queries are bad.

---

## Part IV: Additional Thoughts and Requirements

---

### Dr. Pearl — On Causal Gap Prioritization

I want to emphasize: **causal knowledge is more valuable than correlational knowledge**.

When prioritizing gaps, weight causal identification gaps highly. A correlational study tells us "X and Y co-occur." A causal study tells us "intervening on X changes Y." The latter supports design decisions; the former doesn't.

The search system should specifically seek:
- Randomized experiments
- Natural experiments
- Instrumental variable studies
- Regression discontinuity designs

These designs support causal inference. The system should recognize these terms and prioritize papers that use them.

---

### Dr. Cartwright — On Negative Evidence Search

The proposal doesn't adequately address searching for **negative evidence**. But calibrating credences requires knowing about null results, failed replications, and contradictory findings.

Search strategies for negative evidence:
- "No effect" OR "no significant" OR "failed to replicate" + topic terms
- Journals that publish null results (PLOS ONE, Frontiers)
- Pre-registered studies (more likely to report null results)
- Replication databases (Psychological Science Accelerator, ManyLabs)

This is uncomfortable because it challenges existing beliefs. But it's essential for calibration.

---

### Dr. Simon — On Search Resource Management

The search system needs a **budget**. Search takes time, API calls cost money, human review is expensive.

I recommend:
1. **Set weekly search budget** (number of queries, number of papers to review)
2. **Allocate budget to gaps by VOI** (highest VOI gaps get most effort)
3. **Track yield per effort** (papers acquired per hour invested)
4. **Stop when marginal yield drops below threshold**

Without resource management, the system could search forever. Satisficing criteria are essential.

---

### Dr. Bates — On Search as Ongoing Process

Search shouldn't be a one-time activity. Literature is constantly published. Gaps change as the web evolves.

I recommend:
1. **Periodic gap assessment:** Monthly, reassess what gaps exist
2. **Continuous monitoring:** Set up alerts for new papers matching gap queries
3. **Triggered search:** When a gap's VOI exceeds threshold, launch focused search
4. **Acquisition pipeline:** Systematic process from search → review → acquire → process

The system should eventually run largely autonomously, with human oversight for quality control.

---

### Dr. Kaplan — On Domain-Specific Search Sources

For CNfA specifically, these sources are essential:

**Academic databases:**
- PubMed (health outcomes)
- PsycINFO (psychology)
- Web of Science (general science)
- Scopus (engineering, architecture)
- Avery Index to Architectural Periodicals

**Grey literature:**
- Conference proceedings (ANFA, EDRA, IAPS)
- Center for Health Design repository
- Dissertations (ProQuest)

**Specific journals to monitor:**
- Environment and Behavior
- Journal of Environmental Psychology
- HERD: Health Environments Research & Design
- Building and Environment
- Architectural Science Review

The search system should know which sources to query for which types of gaps.

---

### Dr. Giles — On Relevance Feedback

The system learns which papers were actually valuable when they're processed. This feedback should improve future search.

Implement:
1. **Explicit feedback:** Human marks each acquired paper as "useful" or "not useful"
2. **Implicit feedback:** Papers that update beliefs significantly were useful; papers that change nothing were not
3. **Query refinement:** Use feedback to adjust query weights and term mappings
4. **Strategy selection:** Track which strategies yield useful papers

Over time, the system should get better at predicting what will be valuable.

---

## Part V: Synthesis and Recommendations

---

### Recommended Gap Types (Expanded)

1. **Scope boundary gap:** Effect known in population A, need evidence for population B
2. **Mechanism gap:** Effect known, mechanism hypothesized but untested
3. **Bridge evidence gap:** Two theories both predict effect, need covariance evidence
4. **Replication gap:** Effect reported once, needs independent replication
5. **Null result gap:** Effect assumed, need calibration from null findings
6. **Theory challenge gap:** Theory established, need evidence testing alternatives
7. **Causal identification gap:** Correlational evidence exists, need experimental evidence
8. **Confounder gap:** Effect might be confounded, need studies with controls
9. **Magnitude precision gap:** Effect established, need tighter effect size estimates

### Recommended Search Strategies

| Gap Type | Primary Strategies | Secondary Strategies |
|----------|-------------------|---------------------|
| Scope boundary | Subject search with scope terms | Citation search from known papers |
| Mechanism | Subject search + "mechanism" terms | Author search (mechanism researchers) |
| Bridge evidence | Multi-concept search (both theories) | Journal browsing (cross-disciplinary) |
| Replication | Citation search (papers citing original) | Pre-registration databases |
| Null result | Special null-result queries | Replication databases |
| Causal identification | Method terms (RCT, experiment) | Journal filtering (experimental journals) |

### Recommended VOI Computation

```
VOI(gap) = P(finding paper) × E[uncertainty reduction] × belief_importance - search_cost

Where:
- P(finding paper): Estimated from historical yield for this gap type and strategy
- E[uncertainty reduction]: How much a typical paper would reduce uncertainty
- belief_importance: How central is the affected belief? (connectivity, credence, n_supporting)
- search_cost: Estimated effort in queries, review time, processing time
```

### Recommended Implementation Approach

1. **Phase 1: Gap Identification**
   - Implement gap typing based on web structure
   - Compute VOI for each identified gap
   - Prioritize top-10 gaps for search

2. **Phase 2: Query Generation**
   - Build cross-field vocabulary for top-20 concepts
   - Implement query templates for each gap type
   - Generate queries from gap specifications

3. **Phase 3: Multi-Source Search**
   - Integrate Semantic Scholar (primary)
   - Integrate PubMed (health-related)
   - Implement query expansion
   - Aggregate and deduplicate results

4. **Phase 4: Ranking and Recommendation**
   - Rank results by expected information value
   - Estimate acquisition cost
   - Generate prioritized acquisition list

5. **Phase 5: Feedback Loop**
   - Track which acquired papers were useful
   - Update strategy effectiveness estimates
   - Refine vocabulary mappings

### Recommended Metrics

- **Precision@10:** Fraction of top-10 results that are relevant
- **Gap coverage:** Fraction of high-VOI gaps with at least one relevant paper found
- **Acquisition value:** Average credence change per acquired paper
- **Search efficiency:** Relevant papers found per query executed
- **Strategy performance:** Yield by strategy type

---

## Next Steps

1. **Build vocabulary mapping** for top-20 CNfA concepts (Sprint B)
2. **Implement gap identification** from web structure (Sprint B)
3. **Generate queries** for test set of 10 gaps (Sprint C)
4. **Execute searches** and evaluate results (Sprint C)
5. **Implement ranking** and acquisition recommendations (Sprint D)
6. **Build feedback loop** from acquired papers (Sprint E)
7. **Panel reconvenes** to review search performance (after Sprint D)

---

*Panel session concluded: January 20, 2026*
*Document prepared for implementation team*
