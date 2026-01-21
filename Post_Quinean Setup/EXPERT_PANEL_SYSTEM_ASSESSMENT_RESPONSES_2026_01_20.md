# Expert Panel System Assessment — Responses
## Article Eater Post-Quinean v1 — Critical Review
**Date**: January 20, 2026
**Panel Session**: Comprehensive System Assessment

---

# PANEL RESPONSES

---

## DR. JUDEA PEARL — Causal Inference & Bayesian Networks

### Overall Assessment

The system demonstrates sophisticated awareness of causal reasoning distinctions, but I have serious concerns about the BN integration strategy.

### Specific Responses

**Q1: How should we calculate BN priors from Quinean web coherence?**

This question reveals a fundamental tension. In standard Bayesian networks, priors represent degrees of belief *before* observing evidence. The Quinean web, by contrast, treats all beliefs as already conditioned on the totality of evidence—there is no "prior" state.

**My recommendation**: Do not attempt to extract priors from the web. Instead:
1. The BN should be a *projection* of the web onto a causal graph structure
2. Use the web's credences directly as marginal probabilities in a *causal Bayesian network* (CBN)
3. For CPTs, derive conditional relationships from the constraint structure: if the web contains a constraint "A supports B with strength 0.7", this informs P(B|A) but requires additional assumptions about P(B|¬A)

**Critical gap**: The system lacks a principled method for inferring P(B|¬A) from coherentist constraints. You need a "closed-world assumption" or similar default.

**Q2: CausalDirection mapping to BN edge semantics**

Your CausalDirection enum is well-designed. The mapping should be:
- FORWARD → directed edge A → B
- REVERSE → directed edge B → A
- BIDIRECTIONAL → either feedback loop (two directed edges) or common effect (collider)
- COMMON_CAUSE → introduce latent variable L with L → A, L → B
- MEDIATED → introduce mediator M with A → M → B
- CORRELATIONAL → no directed edge; encode as soft constraint or omit from causal BN

**Warning**: CORRELATIONAL findings should NOT become BN edges. They belong in an associational layer, not the causal graph. Mixing these will produce incorrect interventional predictions.

**Q3: Should BN auto-update or regenerate?**

Regenerate. The BN is a derived artifact. When the web changes, regenerate the BN from scratch rather than trying to propagate updates incrementally. Incremental updates risk accumulating numerical errors and losing structural coherence.

### Gap Analysis (BN-Related Use Cases)

| UC | Feasibility | Issue |
|----|-------------|-------|
| UC1 (Image→Evidence) | LOW | No BN query interface exists; CPT generation undefined |
| UC7 (Effect→Cause) | MEDIUM | BN can support this *if* edges are correctly directed |
| UC3 (VOI Experiments) | HIGH | VOI calculator exists; BN not required |

### Critical Recommendation

**Do not ship BN export until you have**:
1. A specification for CPT generation from constraints
2. Clear separation of causal vs. correlational findings
3. Handling of COMMON_CAUSE and MEDIATED with latent variables

**Priority**: HIGH. UC1 depends entirely on a functional BN.

---

## DR. NANCY CARTWRIGHT — Philosophy of Science & Bridge Warrants

### Overall Assessment

The bridge warrant implementation is philosophically sophisticated—more so than most computational systems I've seen. However, I have concerns about how failures are handled and about the treatment of scope conditions.

### Specific Responses

**Q1: Should bridge failures revise the source theory or just the bridge?**

This is the right question, and the Quinean answer is clear: *both are candidates for revision*. The system should not privilege either.

**Current implementation concern**: I suspect the system defaults to flagging the bridge as unreliable without propagating doubt to the source theory. This is a subtle form of foundationalism—treating the theory as more central than it should be.

**My recommendation**: When a bridge fails, create an "anomaly node" in the web that constrains BOTH:
1. The bridge warrant confidence (direct impact)
2. The source theory confidence (indirect impact, weighted by the bridge's original confidence)

The web should then seek equilibrium. Sometimes the theory survives; sometimes it doesn't. That's proper Quinean behavior.

**Q2: Scope boundary conflicts—split beliefs or add conditions?**

Both are valid strategies, and the choice depends on whether the scope difference is *principled* or *accidental*.

- **Principled scope difference**: The mechanism genuinely operates differently in different contexts. Create context-specific beliefs. Example: "Natural light improves mood in offices" vs. "Natural light improves mood in hospitals" may involve different mechanisms (work stress vs. healing).

- **Accidental scope difference**: The mechanism is the same, but studies were conducted in different contexts. Keep one belief with scope conditions. Example: Different effect sizes in different countries may reflect measurement differences, not mechanism differences.

**Implementation suggestion**: Add a "scope_differentiation_type" field to scope conditions: PRINCIPLED vs. ACCIDENTAL. Let the system default to ACCIDENTAL (conservative), but allow human reviewers to upgrade to PRINCIPLED when warranted.

**Q3: Capacity claims with enabling conditions**

This is where most evidence-based systems fail. A capacity claim like "Natural light CAN improve mood" requires enabling conditions (adequate dosage, baseline mood state, absence of interfering factors).

**Current gap**: The system tracks scope conditions but not enabling conditions. These are different:
- Scope: "This finding applies to office settings" (domain restriction)
- Enabling: "This effect requires at least 30 minutes of exposure" (activation requirement)

**Recommendation**: Add an "enabling_conditions" field to beliefs, separate from scope_conditions. Without this, UC4 (Theory-Mechanism Understanding) cannot explain WHY findings sometimes fail to replicate.

### Gap Analysis (Bridge-Related Use Cases)

| UC | Feasibility | Issue |
|----|-------------|-------|
| UC9 (Bridge Audit) | HIGH | bridge_warrants.py supports queries; needs GUI |
| UC12 (Cross-Domain Transfer) | MEDIUM | Bridge types exist; domain-distance metric missing |
| UC8 (Contradiction Resolution) | MEDIUM | Conflict types exist; explanation generation partial |

### Critical Recommendation

**Add enabling conditions**. Without them, the system cannot distinguish "failed because mechanism absent" from "failed because mechanism blocked."

---

## DR. HERBERT SIMON — Bounded Rationality & System Design

### Overall Assessment

The system shows admirable attention to satisficing principles in VOI search. However, the overall user experience appears to demand too much cognitive effort for the decisions users must make.

### Specific Responses

**Q1: Epsilon-greedy vs. Thompson sampling**

Epsilon-greedy with decay is appropriate for this domain. Thompson sampling requires maintaining posterior distributions for each search strategy, which adds complexity without clear benefit here.

However, your decay schedule matters enormously. The current implementation (I assume linear or exponential decay) should be validated against actual user search sessions.

**Recommendation**: Log epsilon values and search outcomes. After 50+ real sessions, analyze whether users find good papers faster with current decay vs. alternatives. Don't over-optimize prematurely.

**Q2: Designing for bounded rationality without patronizing experts**

This is the central challenge. Experts resent systems that hide information; novices are overwhelmed by systems that show everything.

**Design principle**: Progressive disclosure with expert escape hatches.

- **Default view**: Show decisions (BLOCK/REVIEW, recommended papers) with one-sentence justifications
- **Expand view**: Show the factors behind each decision (credibility score, scope distance, design strength)
- **Expert view**: Show full constraint network, credence values, equilibrium trajectory

Never *force* users through the simple views. Let experts jump directly to the complex view if they want.

**Critical observation**: The current system has no views at all—it's all API/CLI. This is fine for research, but unusable for practitioners.

**Q3: Stopping rules**

Budget-based limits (stop after N papers) are computationally convenient but epistemically arbitrary.

**Better stopping rules** (in order of preference):
1. **Diminishing VOI**: Stop when expected value of next search < threshold
2. **Belief stability**: Stop when credences haven't changed > ε in last K papers
3. **Coverage**: Stop when all high-priority gaps have at least one study
4. **Budget**: Stop after N papers (current implementation)

**Recommendation**: Implement rule 2 (belief stability) as default, with rule 4 as hard cutoff. This respects user time while allowing the system to say "I've learned all I can from available sources."

### Gap Analysis (Workflow-Related Use Cases)

| UC | Feasibility | Issue |
|----|-------------|-------|
| UC3 (VOI Experiments) | HIGH | Core implemented; needs workflow integration |
| UC6 (Field Overview) | LOW | Requires aggregation logic not yet built |
| UC14 (Hypothesis Refinement) | MEDIUM | Needs NL parsing + gap identification |

### Critical Recommendation

**Implement belief-stability stopping**. Budget limits will frustrate researchers who want to know "when is enough enough?"

---

## DR. MARCIA BATES — Information Science & Search Behavior

### Overall Assessment

The vocabulary bridge and search components show good understanding of terminology challenges. However, the search experience is not designed around how researchers actually search.

### Specific Responses

**Q1: Expertise levels—are these right?**

Your three levels (academic, practitioner, common) are reasonable but incomplete. I suggest:

1. **Domain expert**: Uses precise technical terms (your "academic")
2. **Adjacent-field researcher**: Uses general scientific vocabulary but may not know domain-specific terms
3. **Practitioner**: Uses applied/professional vocabulary (your "practitioner")
4. **Student/novice**: Uses textbook/pedagogical vocabulary
5. **Layperson**: Uses everyday vocabulary (your "common")

**The missing level is critical**: Adjacent-field researchers are a key user group for interdisciplinary tools. A cognitive scientist searching for architectural findings won't use architect vocabulary OR psychology vocabulary—they'll use generic scientific terms.

**Q2: Terminological drift**

This is a real problem. Terms change meaning over time; new terms emerge; old terms become deprecated.

**Recommendations**:
1. **Version your vocabulary files** with date stamps
2. **Track first-seen and last-seen dates** for each term in the corpus
3. **Flag deprecated terms** (common in old papers but absent from recent ones)
4. **Link historical terms to current equivalents** (e.g., "personal space" → "proxemics")

Without this, the system will become progressively confused as the corpus spans more decades.

**Q3: Search interaction patterns for exploratory seeking**

Researchers don't search in a straight line. They:
1. Start with a vague question
2. Find something relevant
3. Follow citations and related papers
4. Refine the question based on what they learned
5. Search again with better terms
6. Repeat

**Your system lacks**:
- Citation following (paper A cites paper B; let me see B)
- "More like this" recommendations
- Query refinement suggestions ("Did you mean X? Papers also discuss Y")
- Search history with ability to return to earlier queries

These are table stakes for exploratory search. UC2 and UC6 will fail without them.

### Gap Analysis (Search-Related Use Cases)

| UC | Feasibility | Issue |
|----|-------------|-------|
| UC2 (Network Probing) | LOW | No query interface; no "more like this" |
| UC5 (Measurement Methods) | MEDIUM | Taxonomy exists; no search entry point |
| UC15 (Systematic Review) | LOW | No citation following; no PRISMA export |

### Critical Recommendation

**Add exploratory search features**: citation following, query refinement, "more like this." Without these, researchers will not use the system.

---

## DR. RACHEL KAPLAN — Environmental Psychology (Domain Expert)

### Overall Assessment

The outcome taxonomy reflects current CNFA constructs well, but I'm concerned about ecological validity and the treatment of interaction effects.

### Specific Responses

**Q1: Missing constructs**

The taxonomy covers individual-level outcomes well but is weaker on:

1. **Social outcomes**: Collaboration, privacy, territoriality, social support
2. **Temporal dynamics**: Adaptation, habituation, sensitization
3. **Preference vs. performance**: People often prefer environments where they perform worse (comfort vs. challenge)
4. **Restorative environments** (yes, my work): Fascination, being away, extent, compatibility

**Recommendation**: Add a "social_outcomes" category and a "temporal_dynamics" category. These are essential for understanding real built environments.

**Q2: Handling stubs**

Stubs—findings that don't fit the ontology—should be:
1. Logged with full context (don't lose information)
2. Periodically reviewed for patterns (multiple stubs about "soundscapes" suggests missing category)
3. Either integrated (extend ontology) or explained (why they don't fit)

**Current concern**: I suspect stubs are being quietly dropped or ignored. If so, you're systematically losing the most interesting findings—the ones that challenge current understanding.

**Q3: Domain-specific validation**

I recommend validation against:
1. **Kaplan & Kaplan (1989)** — The Experience of Nature (foundational taxonomy)
2. **Ulrich (1991)** — Stress recovery theory
3. **Appleton (1975)** — Prospect-refuge theory (I see you have this—good)
4. **Gifford (2014)** — Environmental Psychology textbook (comprehensive taxonomy)

Run your outcome taxonomy against the constructs in these sources. Any major discrepancies should be investigated.

### Gap Analysis (Domain-Related Use Cases)

| UC | Feasibility | Issue |
|----|-------------|-------|
| UC4 (Theory-Mechanism) | LOW | Theory system not integrated |
| UC7 (Effect→Cause) | MEDIUM | Interactions poorly modeled |
| UC11 (Publication Bias) | HIGH | NullResultDetector implemented |

### Critical Recommendation

**Add social outcomes and temporal dynamics**. Built environments are social and change over time. A taxonomy that ignores these will miss half the research.

---

## WORKFLOW DESIGNER — Task Analysis & User Journeys

### Overall Assessment

The system has powerful backend capabilities but no coherent user workflows. Each use case requires assembling API calls manually—this is not viable for any user except developers.

### Primary Task Analysis

| UC | Primary Task | Key Decisions | Missing Support |
|----|--------------|---------------|-----------------|
| UC1 | Evaluate design options | Which features matter? What are tradeoffs? | Image ingestion, BN queries, comparison view |
| UC2 | Understand evidence landscape | How strong is evidence? Where are conflicts? | Query interface, epistemic summaries |
| UC3 | Prioritize research directions | Where is effort best spent? | VOI dashboard, recommendation explanation |
| UC4 | Learn domain theories | What explains these findings? | Theory browsing, mechanism diagrams |
| UC6 | Get oriented in field | What do I need to know? | Overview generation, curriculum structure |

### Cognitive Load Analysis

The system exposes too many dimensions simultaneously:
- Credence (0-1 float)
- Coherence (aggregate score)
- Bridge type (4 categories)
- Bridge confidence (0-1 float)
- Scope conditions (structured list)
- Conflict type (3 categories)
- Study design strength (scored)
- Causal direction (7 categories)

**No user can hold all of this in working memory.**

**Recommendations**:
1. **Layer 1 (always visible)**: Traffic-light credence (green/yellow/red), conflict flag (yes/no)
2. **Layer 2 (on hover/click)**: Confidence value, conflict type, key scope conditions
3. **Layer 3 (deep dive)**: Full constraint network, all metadata

### Error Recovery

**Current state**: No mechanism for users to notice or correct errors.

**Required**:
1. Extraction review interface (show claim, ask "is this right?")
2. Bridge challenge interface (show bridge, ask "does this transfer apply?")
3. Credence override with justification logging
4. Rollback capability (undo last N ingestions)

### Critical Recommendation

**Design three distinct user journeys**:
1. **Architect journey**: Image → Evidence → Decision (UC1)
2. **Researcher journey**: Question → Literature → Gaps → Experiment (UC2, UC3)
3. **Student journey**: Topic → Overview → Deep dive → Understanding (UC4, UC6)

Each journey should be a guided flow, not a grab-bag of API calls.

---

## GUI/UX EXPERT — Interface Design

### Overall Assessment

The system needs a GUI. Without one, adoption will be limited to technically sophisticated researchers willing to write Python.

### Visual Vocabulary Recommendations

| Concept | Representation |
|---------|----------------|
| Credence | Color gradient (red→yellow→green) + numeric |
| Coherence | Circular gauge (0-100%) |
| Bridge type | Icons (mechanism=gear, functional=arrow, analogical=≈, constitutive=∈) |
| Conflict | Warning triangle with conflict type on hover |
| Scope conditions | Tag chips (clickable to filter) |
| Causal direction | Arrow style (solid=forward, dashed=correlational, double=bidirectional) |

### Essential Screens (MVP)

**Screen 1: Dashboard**
- Current web statistics (beliefs, constraints, coherence)
- Recent papers ingested
- Top gaps (VOI-ranked)
- Alerts (new conflicts, low-confidence beliefs)

**Screen 2: Evidence Explorer**
- Graph visualization of belief network (force-directed layout)
- Click node → side panel with belief details
- Filter by outcome, credence, source paper
- "Find path" between two nodes

**Screen 3: Paper Ingestion**
- Upload PDF or enter DOI
- Show extracted claims before integration
- Allow user to edit/reject claims
- Show predicted web impact before confirming

**Screen 4: Query Interface**
- Natural language input (LLM-parsed)
- Faceted filters (outcome, date range, study type)
- Results with epistemic context cards
- "More like this" and "Related papers" buttons

**Screen 5: Gap Analysis**
- VOI-ranked list of epistemic gaps
- For each gap: type, relevant beliefs, recommended searches
- Export search queries for PubMed/Google Scholar

### Network Visualization

Use a force-directed graph with:
- Node size = credence strength
- Node color = outcome category
- Edge thickness = constraint strength
- Edge color = constraint type (support=green, tension=red, bridge=purple)
- Click-to-focus: clicking a node dims distant nodes
- Semantic zoom: zoomed out shows clusters; zoomed in shows individual beliefs

**Tool recommendation**: D3.js or Cytoscape.js for web; Gephi export for publications.

### Critical Recommendation

**Build Screen 2 (Evidence Explorer) first**. It's the core value proposition—letting users SEE the web of belief. Everything else is secondary.

---

## SYSTEMS ARCHITECT — Integration & Scalability

### Overall Assessment

The architecture is clean and well-tested for a research prototype. Production deployment will require database migration and API hardening.

### Scalability Analysis

| Scale | SQLite Adequate? | Issue |
|-------|------------------|-------|
| 1-100 papers | YES | Current state |
| 100-1,000 papers | MAYBE | Write contention during parallel ingestion |
| 1,000-10,000 papers | NO | Query performance on large graphs |
| 10,000+ papers | NO | Need distributed graph database |

**Migration path**:
1. **Phase 1** (now): SQLite with WAL mode for better concurrency
2. **Phase 2** (1K papers): PostgreSQL with graph extension (Apache AGE) or dedicated graph DB (Neo4j)
3. **Phase 3** (10K+ papers): Distributed graph (JanusGraph, Neptune)

### Integration Points

| System | Integration Method | Priority |
|--------|-------------------|----------|
| Zotero/Mendeley | Import via BibTeX/RIS | HIGH |
| GeNIe/Netica | Export BIFXML | HIGH (for BN use cases) |
| Revit/SketchUp | Not feasible without plugin development | LOW |
| Canvas/Moodle | LTI integration for teaching modules | MEDIUM |
| PubMed/Semantic Scholar | API for search/ingestion | HIGH |

### API Design Recommendation

Use **GraphQL** for the evidence explorer (flexible queries on graph data) and **REST** for CRUD operations (paper ingestion, feedback submission).

WebSocket for real-time: equilibrium-seeking progress, collaborative editing.

### Deployment Recommendation

**Phase 1**: Single-tenant, on-premises (academic institution server)
- Simpler compliance (no data leaves institution)
- Professor controls access

**Phase 2**: Multi-tenant cloud (AWS/GCP)
- Shared infrastructure across research groups
- Requires authentication/authorization overhaul

### Data Portability

Export formats needed:
1. **Full web export**: JSON (custom schema) for backup/transfer
2. **BN export**: BIFXML, XDSL (GeNIe), Hugin .net
3. **Citation export**: BibTeX, RIS for reference managers
4. **Analysis export**: CSV/Parquet for statistical analysis

### Critical Recommendation

**Add PubMed/Semantic Scholar integration**. Paper ingestion from DOI/PMID will dramatically reduce friction for researchers.

---

## EPISTEMOLOGIST — Quinean Fidelity Critique

### Overall Assessment

The system makes a genuine attempt to implement coherentist epistemology, but several implementation choices reveal latent foundationalist assumptions.

### Fidelity Analysis

**Claim 1: No foundational beliefs**

*Partially honored*. The system allows any belief to be revised, which is correct. However:
- Constraint strengths appear to be fixed at extraction time. A truly Quinean system would allow constraints themselves to be revised based on global coherence.
- The "stub" mechanism treats some findings as second-class. While this is pragmatically necessary, it introduces a distinction between "integrated" (first-class) and "stubbed" (liminal) beliefs that Quine would not endorse.

**Recommendation**: Allow constraint revision. When equilibrium-seeking repeatedly fails, consider weakening constraints, not just adjusting credences.

**Claim 2: Coherence as criterion**

*Largely honored*. The coherence score and equilibrium-seeking mechanism implement something like coherence-based justification.

**Concern**: The coherence score appears to be a sum/product of local constraint satisfactions. This captures *consistency* but not *explanatory coherence*. True coherence includes explanatory relations—beliefs that explain each other should have higher joint credence than beliefs that merely don't contradict.

**Recommendation**: Add explanatory coherence to the scoring function. Beliefs linked by EXPLANATORY constraints (from Glymour's taxonomy) should contribute more to coherence than those linked only by EVIDENTIAL constraints.

**Claim 3: Mutual constraint**

*Honored*. Constraints are bidirectional where appropriate.

**Claim 4: Stubs as liminal**

*Questionable*. The stub mechanism is pragmatically useful but philosophically suspicious.

In pure Quinean terms, there should be no "outside" the web—every finding either integrates or forces revision. Stubs create a waiting room that Quine wouldn't recognize.

**Pragmatic defense**: Given finite computational resources, stubs are a reasonable approximation. But the system should periodically attempt re-integration of stubs, rather than leaving them permanently liminal.

**Recommendation**: Add a "stub re-integration pass" to equilibrium-seeking. After N iterations, attempt to integrate each stub; if still incompatible, leave as stub with incremented "failed_integration_count."

**Claim 5: Bridge warrants explicit**

*Honored and exceeded*. The bridge warrant implementation is philosophically sophisticated.

### Core Philosophical Concern

The equilibrium-seeking algorithm optimizes a coherence score. This is fine as far as it goes, but it treats coherence as a *maximization target* rather than a *constraint on inference*.

Quine's view is not "maximize coherence" but "revise minimally to restore coherence." These are different:
- Maximization: Always make the web more coherent, even if current coherence is acceptable
- Minimal revision: Only revise when coherence falls below threshold; minimize change when revising

The current implementation appears to do maximization. This can lead to over-revision—changing beliefs that are adequately justified just because a slightly different configuration scores 0.01 higher.

**Recommendation**: Implement *satisficing* coherence—seek equilibrium only when coherence drops below threshold; stop when threshold is restored. This honors Quine's conservatism.

### Critical Recommendation

**Implement satisficing coherence with constraint revision**. Without these, the system is "Quine-inspired" rather than "Quinean."

---

# SYNTHESIS: PRIORITY ROADMAP

Based on all panel inputs, here is a prioritized roadmap:

## Tier 1: CRITICAL (Required for any user adoption)

| Item | Owner | Dependencies |
|------|-------|--------------|
| Evidence Explorer GUI (Screen 2) | UX | None |
| Natural language query interface | Dev | LLM integration |
| PubMed/Semantic Scholar ingestion | Dev | API keys |
| Belief-stability stopping rules | Dev | None |

## Tier 2: HIGH (Required for primary use cases)

| Item | Owner | Dependencies |
|------|-------|--------------|
| BN export with CPT specification | Pearl review | CPT generation spec |
| Theory system pipeline integration | Dev | Sprint 8 |
| Exploratory search features | Bates review | Query interface |
| Enabling conditions field | Dev | Schema update |
| Social outcomes taxonomy | Kaplan review | Vocabulary update |

## Tier 3: MEDIUM (Enhances usability)

| Item | Owner | Dependencies |
|------|-------|--------------|
| Paper ingestion GUI (Screen 3) | UX | Evidence Explorer |
| Three user journey designs | Workflow | GUI foundation |
| Adjacent-field vocabulary level | Dev | Vocabulary bridge |
| PostgreSQL migration | Dev | Evidence of scale need |
| Satisficing coherence algorithm | Dev | Current algorithm analysis |

## Tier 4: LOW (Future enhancement)

| Item | Owner | Dependencies |
|------|-------|--------------|
| Multi-user support | Dev | Cloud deployment |
| Image integration | Dev | Tag vocabulary |
| LMS integration | Dev | Teaching module export |
| Real-time feedback loop | Dev | Feedback store integration |

---

# RISK ASSESSMENT

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| BN semantics undefined → UC1 fails | HIGH | HIGH | Resolve before GUI |
| No GUI → zero adoption | HIGH | HIGH | Prioritize Evidence Explorer |
| Stubs accumulate → lost insights | MEDIUM | HIGH | Implement re-integration pass |
| SQLite doesn't scale | MEDIUM | MEDIUM | Monitor; plan PostgreSQL |
| Vocabulary drift → confusion | MEDIUM | MEDIUM | Version vocabularies |
| Foundationalist creep | LOW | HIGH | Regular philosophical review |

---

# FINAL VERDICT

**What works**: The epistemic engine is solid. Sprints 1-7 deliver a coherent, tested implementation of Quinean coherentism with bridge warrants, credibility testing, and VOI search.

**What's missing**: Everything the user would actually touch. No GUI, no query interface, no exploratory search, no intuitive workflows.

**What's fooling you**: The test count (470+) suggests completeness, but tests cover the engine, not the user experience. You have a powerful motor with no car around it.

**Next step**: Build the Evidence Explorer GUI. Until users can SEE the web, everything else is academic.

---

*End of Panel Responses*
