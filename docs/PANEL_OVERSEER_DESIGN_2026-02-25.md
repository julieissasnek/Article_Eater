# Expert Panel Deliberation: System Oversight & Integration Integrity

**Panel Date**: 2026-02-25
**Convener**: Claude Code for Professor David Kirsh
**Purpose**: Ruthless review of Article Eater v22.0.0 integration architecture + OVERSEER module design
**Status**: FOR APPROVAL — Actionable recommendations with documented dissent

---

## I. Panel Composition & Expertise

### Core Epistemology

| Panelist | Specialty | Why Critical |
|----------|-----------|-------------|
| **Willard Quine** | Coherentist web of belief, revision holism | Our foundation—claims revision propagates through the web |
| **Susan Haack** | Foundherentism, epistemic justification | Provenance & grounding—how do beliefs earn justification? |
| **Wolfgang Spohn** | Ranking theory, belief dynamics | Our formal framework for entrenchment; how ranks interact with new evidence |
| **John Pollock** | Defeasible reasoning, defeater hierarchy | Architecture of our warrant computation; when do new papers undermine old ones? |

### Causal Inference & Evidence

| Panelist | Specialty | Why Critical |
|----------|-----------|-------------|
| **Judea Pearl** | Causal DAGs, do-calculus, confounding | BN parameterization—how does web epistemology constrain causal graphs? |
| **Nancy Cartwright** | Evidence pluralism, causal mechanisms | Are we respecting methodological diversity? Single-method vulnerability detection |
| **Hans Sackett** | Evidence hierarchies, study design | Task-ecological validity—does our paper evaluation respect design realities? |

### Statistical & Meta-Analytic

| Panelist | Specialty | Why Critical |
|----------|-----------|-------------|
| **I.J. Good** | Bayesian foundations, weight of evidence | Are our BetaBernoulliEdge conjugate priors well-calibrated? |
| **Rubin DerSimonian** | Meta-analysis, random effects | Our credence accumulation uses inverse-variance weighting—is this right for heterogeneous evidence? |
| **Michael Borenstein** | Meta-analytic heterogeneity | Coherence computation—is cross-theory heterogeneity handled correctly? |

### Systems & Information Architecture

| Panelist | Specialty | Why Critical |
|----------|-----------|-------------|
| **Herbert Simon** | Bounded rationality, organizational design | OVERSEER governance—who decides what the system does? |
| **W. Ross Ashby** | Cybernetics, requisite variety | System complexity: are our monitoring mechanisms sufficiently sophisticated? |
| **David Parnas** | Information hiding, modular design | Separation of concerns: does OVERSEER belong as a separate subsystem? |
| **Edsger Dijkstra** | Program correctness, invariant preservation | Invariants INV-1 through INV-5—are they sufficient? |

### Implementation & Expertise

| Panelist | Specialty | Why Critical |
|----------|-----------|-------------|
| **Barbara Liskov** | Software architecture, contract design | Paper integration contract—is ClaimV2 sufficient? |
| **Leslie Lamport** | Formal specification, TLA+ | Can we formally specify OVERSEER's state machine? |

---

## II. Ruthless System Review

### A. Web of Belief: Credence Computation

**Finding**: The integration pipeline (Step 4-5) currently bypasses sophisticated credence logic.

**Current implementation** (`orchestrator.py` Step 4):
```python
# STUB: Direct credential extraction
credence_mean = extraction.ae_confidence  # [0, 1]
# Missing: extraction_to_web.integrate_extraction() full pipeline
```

**What should happen** (per `extraction_to_web.py`):
- **Theory inference**: Apply diminishing returns formula for multi-theory attachment:
  ```
  combined = 1 - (1 - current) * (1 - new * 0.5)
  ```
  This implements Quine's idea that coherence with multiple theories produces non-linear credence gains.

- **Mechanistic entrenchment boost**: +0.15 for claims mechanistically grounded in T1 frameworks
  - Spohn would ask: Does this map to ranking theory? Is it a principled adjustment or ad hoc?
  - Good would ask: Is the +0.15 calibrated against empirical warrant accumulation?

- **Reflective equilibrium**: Iterate 5x (configurable) to allow bidirectional belief adjustment
  - Haack requires this—foundherentism demands mutual adjustment between foundational and coherentist support

- **Meta-analytic accumulation**: Use `web_persistence.accumulate_belief()`:
  ```
  1. Inverse-variance weighted credence merge (DerSimonian-Laird)
  2. Paper quality weighting (methodology 0.28, citations 0.18, institution 0.12, ...)
  3. Conflict detection (4 types: direct contradiction, undermining, supporting, neutral)
  4. Coherence dashboard update
  ```

**Panel Assessment** (Quine, Haack, Spohn, DerSimonian):

**Quine's Take**: "You're capturing the right intuition—that new evidence revises the entire web, not just one node. But your current stub violates holism. By directly inserting `ae_confidence`, you're treating it as atomic rather than relational. The formula for theory inference shows you understand this, but it's not being executed. FIX URGENTLY."

**Haack's Take**: "I require that every belief in the web be epistemically justified in two ways: (1) a foundation (something not purely coherent), and (2) coherence with the network. Your reflective equilibrium loop is the right mechanism for (2), but you're missing (1)—provenance chains. Each belief must trace back to experiential grounding. The provenance computation (Step 5) should happen *synchronously*, not as deferred OVERSEER work. Without it, you have coherence but no foundherentism."

**Spohn's Take**: "Your entrenchment values should fall out of ranking theory, not be set by formula. The diminishing returns function has the right shape (sub-additive), but it's heuristic. I want to see: κ(¬B) after new evidence = κ(¬B) prior - update_strength(design, sample_size, coherence). The +0.15 boost needs grounding. Is it because mechanistic claims are more entrenched in T1 frameworks? If so, say so explicitly. Also: you need to handle *conditional ranks*—when theory T1 is true, what's the rank of B? This is crucial for Bayesian network work (Pearl's do-calculus requires conditional independence structures that map to rank conditioning)."

**DerSimonian's Take**: "Inverse-variance weighting is sound for meta-analysis when heterogeneity is low. But CNFA is heterogeneous: papers use VR vs. real buildings, photos vs. in-situ, correlational vs. RCT designs. Your credence weights need to account for this. I'd recommend: (1) heterogeneity test (I-squared) before weighting, (2) random-effects model if I-squared > 50%, (3) subgroup analysis by study design. Your current approach treats all credences equally if they come from the same template. That's wrong."

**RECOMMENDATION**:
- **CRITICAL**: Wire Step 4-5 to `extraction_to_web.integrate_extraction()` + `web_persistence.accumulate_belief()` immediately (engineering task, no panel needed)
- **CRITICAL**: Compute provenance synchronously during Step 5 (see Section B)
- **CRITICAL**: Add coherence pre/post measurement (Step 2 → Step 13) to detect integration problems
- **MAJOR**: Refactor credence weighting to use random-effects model with heterogeneity test
- **MAJOR**: Make the +0.15 boost derived from Spohn ranking theory, not arbitrary

---

### B. Provenance & Justification (Haack Foundherentism)

**Finding**: System records `BeliefVersionEntry` (which paper contributed) but does NOT construct `Provenance` objects with justification status.

**Current state**:
- `BeliefVersionEntry` tracks `paper_id`, `credence_contribution`, `integration_event_id`
- Missing: `Provenance` dataclass with:
  - `source_type` (Experimental, Observational, Theoretical, Consensus)
  - `study_type` (RCT, Quasi-Experimental, Correlational, Phenomenological, Meta-Analysis)
  - `directness` (Direct: effect measured in situ; Indirect: proxy measure; Inferential: mechanism inferred)
  - `grounding_chain` (path to experiential basis)
  - `justification_status` (FOUNDATIONAL, COHERENT_ONLY, DEFEATER_UNDERMINED, AMBIGUOUS)

**Missing computation** (should happen in Step 5, currently deferred):
1. Map `extraction.study_design` → `StudyType` via schema
2. Extract `directness` from measurement method (cortisol ← direct; self-report ← proxy)
3. Construct experiential grounding chain:
   ```
   Belief: "Natural views reduce stress"
   ├─ Experimental evidence: RCT N=60, direct cortisol measurement (FOUNDATIONAL)
   │  └─ Paper 1: Fich et al. (2014), TSST stressor
   ├─ Observational: POE survey N=200, self-report (COHERENT_ONLY)
   │  └─ Paper 2: Author et al. (2020), correlational
   └─ Theoretical inference: mechanism coherent with neuromodulation theory (COHERENT_ONLY)
   ```
4. Determine `justification_status`:
   - FOUNDATIONAL: At least one direct experimental evidence + no undefeated defeaters
   - COHERENT_ONLY: Only coherence + proxies, no direct evidence
   - DEFEATER_UNDERMINED: Coherence broken by newer, higher-quality evidence
   - AMBIGUOUS: Mixed quality or conflicting evidence profiles

**Panel Assessment** (Haack, Pollock, Spohn):

**Haack's Take**: "This is the heart of foundherentism. A belief cannot be justified *purely* by coherence—it needs something to lean against. That something is a grounding chain back to experience. Your current system is purely coherentist; it lacks the foundational support. The provenance computation I describe is not optional—it's constitutive. Every belief must answer: 'Why should I believe this? Because of mutual support (coherence) AND because it traces back to reliable experience (grounding).' Without provenance, you've violated foundherentism."

**Pollock's Take**: "The justification status gives me the warrant structure I need. But you must distinguish: a belief can be justified by experimental evidence while also being undercut by a defeater (e.g., later meta-analysis showing effect is due to confound). Your status categories need to accommodate this. I'd add: JUSTIFIED_BUT_DEFEATED (evidence good, but undercutting defeater present). Also: who decides what counts as a 'defeater'? This requires panel expertise. You can't automate it. A methodology question masquerading as an epistemology question is still a methodology question."

**Spohn's Take**: "Provenance maps to rank-theoretic justification. A foundational belief has κ(¬B) = ∞ (rock-bottom, cannot be defeated). A coherent-only belief has κ(¬B) = finite (can be revised). A defeated belief has κ(B) > 0 (actively disbelieved). Your `justification_status` should code for ranks. FOUNDATIONAL → κ(¬B) = ∞; COHERENT_ONLY → κ(¬B) = f(coherence_score); DEFEATED → κ(B) > 0."

**RECOMMENDATION**:
- **CRITICAL**: Construct `Provenance` objects synchronously during Step 5; persist to `belief_provenance` table
- **CRITICAL**: Map `study_design` → `StudyType` with explicit schema (RCT=EXPERIMENTAL, POE=OBSERVATIONAL, etc.)
- **MAJOR**: Implement grounding chain traversal—show the path from belief to experiential basis
- **MAJOR**: Map `justification_status` to Spohn ranks for formal consistency
- **PANEL DECISION NEEDED**: What counts as FOUNDATIONAL? (Only RCTs? Or quasi-experimental with matching? Observational with instrumental variable?)

---

### C. Bayesian Network: Parameter Updates & Coupling

**Finding**: Step 9 records edge keys but does NOT actually update `BetaBernoulliEdge` objects or persist Beta parameters.

**Current state**:
```python
# Step 9: _step_update_bn
# STUB: Just log the edge keys
event.actions.append(IntegrationAction(
    type="bn_edge_update",
    description=f"Mapped {len(edges)} constraints to BN edges"
))
# Missing: Create/lookup BetaBernoulliEdge, call update(), persist
```

**What should happen**:
1. For each extracted constraint (rule), determine its mapping to BN edge:
   ```
   Belief: "X reduces stress"
   Constraint: "Natural views → Stress Recovery"
   ├─ IV: natural_views (binary feature)
   ├─ DV: stress_recovery (latent construct, measured via cortisol, HRV, self-report)
   └─ BN edge: natural_views → stress_recovery
   ```

2. Look up or create `BetaBernoulliEdge(source='natural_views', target='stress_recovery')`

3. Update conjugate priors:
   ```python
   edge.update(
       supports=True,  # Direction of constraint
       weight=quality_score,  # Inverse-variance + paper quality
       paper_id=integration_event.paper_id,
       evidence_type=EvidenceType.EXPERIMENTAL  # from study_design
   )
   ```

4. Persist updated Beta parameters: `α' = α + weight`, `β' = β + (1 - weight)`

5. Invalidate `EpistemicCausalBridge` cache (BN posterior changed)

**Critical coupling question**: Should BN edge parameters be **coupled** to web credences or **independent**?

**Option 1: Coupled** (my recommendation)
- BN edge posterior = function of web credence + paper quality
- Relationship: `edge.p_support = 0.3 + 0.7 * web_credence * quality_weight`
- Advantage: Epistemic state constrains causal graph
- Disadvantage: Circular dependency (web→BN→web)
- Pearl's question: Can we maintain d-separation properties with circular feedback?

**Option 2: Independent** (parallel tracks)
- BN edge parameters updated only from extracted constraints' polarity
- Relationship: orthogonal (no feedback)
- Advantage: Clean separation, no circularity
- Disadvantage: Web and BN may disagree on beliefs

**Option 3: Hierarchical** (Spohn's approach)
- Web (Quinean coherence + ranks) is epistemologically primary
- BN (Pearl causal inference) is epistemologically downstream
- BN edge parameters reflect web credences, *but* modulated by causal specificity
- If web says P(X→Y) = 0.7 but BN says P(Y|X) = 0.9, investigate the discrepancy

**Panel Assessment** (Pearl, Spohn, Simon, Cartwright):

**Pearl's Take**: "Your Bayesian network must satisfy the Markov condition: every variable is independent of non-descendants given its parents. If you couple BN edges to web credences bidirectionally, you create feedback loops that break Markov. However, *causal graphs are asymmetric*. I allow you to *constrain* edge parameters using non-causal information (like epistemic coherence), provided you clearly distinguish your epistemological layer (coherence, warrant) from your causal layer (confounding, d-separation). My recommendation: Make web → BN one-directional. Web credences inform edge priors, but don't feed back. Causal structure (DAG) is fixed; only edge weights change."

**Spohn's Take**: "I prefer hierarchical coupling. The ranking function applies to epistemology; causal graphs apply to the world. Your web ranks propositions (beliefs); your BN parameterizes causal mechanisms. They're asking different questions. But ranks should inform your causal confidence. If κ(natural_views → stress) is high (low disbelief), then your BN edge weight should reflect that. Not one-directional feedback—more like: ranks *constrain* the BN, but don't fully determine it. The BN adds causal specificity (does the effect run through physiology or cognition?) that the web doesn't capture."

**Simon's Take**: "From an organizational perspective, coupling is dangerous. You have two separate subsystems (Quinean web, Pearl network) with different logics, different update rules, different epistemic criteria. If you couple them tightly, a bug in one cascades to both. A failure in BN parameter computation could corrupt web credences. My advice: clean interfaces between subsystems. Define exactly what information crosses the boundary. Use Option 2 (independent) or Option 3 (hierarchical with clear hierarchy) but NOT bidirectional coupling."

**Cartwright's Take**: "You're treating BN edges as if they represent *universal causal regularities*. They don't. They represent *specific mechanisms in this population, in this context*. The web captures methodological diversity (RCT vs. observational vs. phenomenological). The BN erases that diversity by averaging. You should parameterize BN edges with *method-conditional* probability: P(Y|X, method=RCT) vs. P(Y|X, method=observational). Don't hide heterogeneity under a single Beta distribution. Make it visible in the BN structure itself."

**RECOMMENDATION**:
- **CRITICAL**: Implement Option 3 (Hierarchical coupling):
  - Web credences → BN edge priors (epistemology constrains causality)
  - No feedback from BN to web (unidirectional)
  - Clear documentation of the mapping formula
- **CRITICAL**: Wire Step 9 to `BetaBernoulliEdge.update()` with constraint polarity + quality weight
- **MAJOR**: Add method-conditional edges to BN (edge parameterization depends on study design)
- **PANEL DECISION NEEDED**: Is the mapping from credence to edge weight `0.3 + 0.7 * credence` the right formula? (Elicit expert calibration)

---

### D. QA Cache: Eager vs. Lazy Recomputation

**Finding**: Step 10 calls `QACacheManager.notify_qa_system()`, which is a placeholder. Current design marks caches STALE but doesn't recompute.

**Three strategies on the table**:

**Option A: Eager** (Synchronous recomputation during integration)
- When paper integrated, recompute L1/L2/L3 summaries for affected molecules immediately
- Advantages: Cache always fresh; user queries return latest summaries
- Disadvantages: LLM calls for every integration (expensive); slows pipeline; integration can fail if LLM fails
- Cost: $0.50-2.00 per molecule recomputation; hundreds of LLM calls per extraction batch

**Option B: Lazy** (Deferred recomputation on query)
- Mark cache STALE; recompute only when user queries the molecule
- Advantages: No synchronous cost; fast extraction pipeline
- Disadvantages: User sees stale summaries until they navigate away and back; unpredictable latency
- Risk: Cache staleness could exceed a week if molecule isn't queried

**Option C: Batched** (Nightly bulk recomputation)
- Mark caches STALE during integration; batch-recompute all stale caches during off-hours
- Advantages: Pipeline fast; cache mostly fresh; predictable cost and timing
- Disadvantages: Users see stale summaries for up to 24 hours; requires batch job infrastructure
- Cost: $0.10-0.30 per molecule (volume discount); 1-2 hours per nightly batch

**Current implementation** (in Session 6 wiring):
```python
# Step 10: Mark cache stale explicitly
cache_manager.mark_stale(molecule_id, dependency_hash_before)
# Recompute triggered on next query (lazy)
```

**Panel Assessment** (Simon, Dijkstra, Liskov, Good):

**Simon's Take**: "Organizations have 'slack' for important resources. QA caches are important—they communicate system confidence to users. You should maintain enough slack that caches stay fresh. That argues for batched (Option C). You have the resources: nightly batch window, bulk LLM discounts. Option B (lazy) is organizationally fragile—users get frustrated with unpredictable latency. Option A (eager) over-invests in freshness. Option C finds the right balance."

**Dijkstra's Take**: "Correctness first. Your system must guarantee that displayed summaries match the underlying web state *within a bounded time window*. Lazy (Option B) violates this—staleness is unbounded. Eager (Option A) meets the guarantee but at high cost. Batched (Option C) is the compromise: freshness guaranteed within 24 hours. Define this formally: 'Every molecule's QA cache is recomputed within 24 hours of relevant paper integration.' Then instrument it: log staleness duration, alert if violated."

**Liskov's Take**: "Interface perspective: your system should *hide* the caching mechanism. Users shouldn't see stale summaries and wonder if they're outdated. From a module design view, the QA cache is *internal implementation*—not part of the public contract. You should expose: get_qa_summary(molecule_id) → summary (fresh, from cache or recomputed as needed). Don't expose STALE status to users. Either keep cache fresh (Option C) or recompute transparently (Option B with timeout). Hide the machinery."

**Good's Take**: "Probabilistic confidence: your caches decay in credibility over time. Instead of binary FRESH/STALE, assign time-decay credence. A cache from 1 hour ago is 99% credible; from 24 hours ago, 85% credible; from 7 days ago, 60% credible. When displaying summaries, show credibility alongside: 'Summary confidence: 85% (last updated 18h ago; recomputing...)'  This is honest about uncertainty."

**RECOMMENDATION**:
- **ADOPT**: Option C (Batched nightly recomputation)
  - Balances freshness, cost, and pipeline performance
  - Provides Simon's organizational slack
  - Meets Dijkstra's formal guarantee (staleness ≤ 24h)
- **ADOPT**: Liskov's interface design—hide STALE status; surface credence decay
- **IMPLEMENT**: Good's time-decay credence formula for QA summaries
- **PANEL DECISION NEEDED**: Is 24-hour freshness window acceptable? (Elicit domain knowledge)

---

### E. Coherence Computation: Threshold & Metric

**Finding**: Integration pipeline (Step 2 → Step 13) measures pre/post coherence delta, but no alert threshold or metric defined.

**Current skeleton** (Step 2 & Step 13):
```python
# Step 2: _step_snapshot
coherence_before = web.compute_coherence()  # Not yet called

# Step 13: _step_post_validate
coherence_after = web.compute_coherence()
delta = coherence_after - coherence_before  # Computed but not acted upon
event.coherence_delta = delta
# Missing: Threshold check, alert generation
```

**Coherence computation** (per `scalable_coherence.py`):
- Network-wide coherence: `mean(pairwise_support(B_i, B_j)) for all adjacent belief pairs`
- Per-theory coherence: `coherence(beliefs in T1 framework)`
- Temporal coherence: `mean(credence_stability) for recently-integrated beliefs`

**What should trigger an alert?**
- Absolute delta: Coherence drops > 5%? 10%? 15%?
- Relative delta: Drop exceeds typical noise from paper-to-paper variation?
- Asymmetric effect: Drop in one theory (e.g., Stress Recovery Theory) but not others?
- Direction: Should *increasing* coherence also alert? (Could indicate over-fitting)

**Three alerting strategies**:

**Option A: Threshold-based** ("Hard caps")
- Rule: If coherence_delta < -0.10, alert CRITICAL
- Advantages: Simple, interpretable, auditable
- Disadvantages: Arbitrary threshold; no context (delta of -0.10 bad in small web, okay in large web)

**Option B: Statistical baseline** ("Anomaly detection")
- Compute historical coherence_delta distribution from past 50 integrations
- Rule: If coherence_delta < 2σ below mean, alert MAJOR
- Advantages: Context-sensitive, adapts to system growth
- Disadvantages: Requires history; slow to respond to new patterns

**Option C: Cartwright dashboard** (multi-metric)
- Track: global coherence (Option A), per-theory coherence, conflict rate, orphan belief count
- Rule: Alert if *any* metric exceeds alarm threshold; escalate if multiple metrics red
- Advantages: Rich signal; captures different failure modes
- Disadvantages: More complex; harder to debug (which metric caused the alert?)

**Panel Assessment** (Cartwright, Spohn, Dijkstra):

**Cartwright's Take**: "Coherence is not a single number. A 'coherent' belief system can still have dangerous blind spots. Your Integration II (Spatial Navigation Theory) might be perfectly coherent while your Integration VI (Embodied Cognition) is unraveling. Use my dashboard approach (Option C). Track per-theory coherence, methodological diversity (are all beliefs from RCTs?), and conflict accumulation. Coherence is a necessary but not sufficient condition for a healthy epistemic system."

**Spohn's Take**: "Coherence maps to rank consistency. If coherence drops, your ranking function is becoming inconsistent (ranks don't satisfy the axioms). This is *dangerous*—it means you're violating your own epistemic logic. I'd use Option B (statistical baseline) but with a low threshold: alert if delta < 1σ below mean. Don't wait for crisis. Also: track *why* coherence dropped. Is it because the new belief contradicts existing ones? Or because it attaches to a weak theory? The delta is a symptom; the cause matters."

**Dijkstra's Take**: "Define an invariant: 'Global coherence shall not decline more than 5% per integration.' Instrument it: measure before and after; log the delta; fail loudly if violated. In your code, use an assertion: `assert coherence_after >= 0.95 * coherence_before, f'Coherence dropped {(1-coherence_after/coherence_before)*100:.1f}%'`. Make violations visible immediately. Don't hide them in logs."

**RECOMMENDATION**:
- **ADOPT**: Cartwright's dashboard approach (Option C)
  - Track 5 metrics: global coherence, per-theory coherence, conflict rate, orphan count, methodological diversity
  - Define alarm thresholds for each (calibrated by expert panel)
  - Alert when any metric exceeds threshold
- **ADOPT**: Spohn's statistical baseline for coherence specifically
  - Compute historical mean + σ from past 50 integrations
  - Alert if coherence_delta < mean - 1σ
- **ADOPT**: Dijkstra's formalization
  - Write invariant: "Coherence decline per integration ≤ 5%"
  - Code as assertion; fail loudly on violation
- **PANEL DECISION NEEDED**: Calibrate alarm thresholds for each metric
  - What % conflict rate is acceptable? 5%? 10%?
  - What % orphan beliefs is acceptable? <1%?
  - What minimum methodological diversity (study design) is required per theory?

---

### F. Social Epistemology & Community Identification

**Finding**: Step 11 is a placeholder. Current code doesn't identify epistemic communities or track contestation.

**What should happen** (per social_epistemology.py skeleton):
1. Identify which `EpistemicCommunity` the paper's authors belong to:
   - Lab/institution (e.g., "Ulrich lab" for Stress Recovery research)
   - Methodological tradition (e.g., "VR researchers" vs. "field POE researchers")
   - Theoretical affiliation (e.g., "Predictive Processing adherents")

2. Compute `CommunityRelativeCredence`:
   - Within-community consensus (do others in the lab agree?)
   - Between-community agreement (do competing labs reach similar conclusions?)
   - Community dissent ratio (if 3 of 5 lab papers contradict this one, flag it)

3. Update `ContestationTracker` if the new paper contradicts existing community consensus:
   - Type 1: Direct contradiction (same finding, opposite direction)
   - Type 2: Undermining (different mechanism, same effect, questions causal pathway)
   - Type 3: Scope disagreement (both agree on mechanism, disagree on population/context)
   - Type 4: Methodological challenge (similar question, very different methods, conflicting results)

4. Detect methodological monoculture:
   - If all papers supporting Belief X use same method (all VR, all photos), flag as vulnerable
   - Cartwright calls this "evidence pluralism"—single method ≠ robust evidence

**Why this matters**: Communities have perspectives, biases, research traditions. A finding supported by "Stress Recovery Theory community" but contradicted by "Embodied Cognition community" signals a genuine dispute, not just evidentiary weakness. The system should track these disputes *explicitly*, not dissolve them into a single credence number.

**Example**:
```
Belief: "Enclosed rooms reduce stress recovery"

Paper A (Ulrich lab, 2010): RCT, enclosed room, cortisol +73%, FOUNDATIONAL
Community: SRT (Stress Recovery Theory) ← consensus across 12 papers

Paper B (Kaplan & Kaplan lab, 1989): Enclosed room, attention restoration, FOUNDATIONAL
Community: ART (Attention Restoration Theory) ← consensus across 8 papers

Paper C (Affordances school, 2022): "Enclosure doesn't matter; wayfinding complexity does"
Community: EC (Embodied Cognition) ← dissent; only 2 papers, newer position

Status: CONTESTED
  - Consensus: SRT + ART agree (enclosed is bad for stress)
  - Dissent: EC challenges mechanism (claims enclosure is proxy for complexity)
  - Action: Panel review to disambiguate (stress ≠ complexity? or related constructs?)
```

**Panel Assessment** (Cartwright, Simon, Haack):

**Cartwright's Take**: "This is *crucial*. Evidence pluralism requires recognizing that different communities use different methods, ask different questions, have different reliability profiles. Your system should NOT average away these differences. A finding supported by RCT evidence (high method reliability) and contradicted by observational evidence (low method reliability) is different from the reverse. Track communities explicitly. Make the contestation visible. Let users decide whether to trust SRT researchers or EC researchers based on *their* methodological track record."

**Simon's Take**: "Organizations are communities. The Stress Recovery community is an organization with shared values (coherence matters), shared methods (cortisol, HRV), shared theories (Ulrich 1983). When a new paper contradicts community consensus, it's an *organizational event*, not just an evidentiary event. The system should treat it seriously: convene panel review, update community trust scores, trace how the dissent propagates. Don't automate this. Surface it for human decision-making."

**Haack's Take**: "Foundherentism requires diverse perspectives. A belief justified only by self-consistent community (echo chamber) is not well-justified. You need *cross-community* support. If SRT researchers and EC researchers both support a conclusion (from different angles), it's more justified than if only SRT does. Use contestation tracking to measure cross-community consensus. Low consensus = higher risk of hidden bias."

**RECOMMENDATION**:
- **MAJOR**: Implement Step 11 with:
  - `CommunityRegistry` mapping papers to communities (institution, methodology, theory)
  - `ContestationTracker` recording 4 types of disagreement
  - `MethodologicalDiversityAssessor` checking if evidence is monoculture
- **MAJOR**: Track community-relative credence separately from global credence
  - Global credence: what does the entire system believe?
  - Community credence: what does each community believe?
  - Consensus: % of communities agreeing
- **MAJOR**: Surface contestation in UI—show debates explicitly
  - "This finding is SUPPORTED by SRT (consensus 8/8 papers) but OPPOSED by EC (consensus 1/3 papers)"
- **PANEL DECISION NEEDED**:
  - Which communities should the system recognize? (Elicit expert knowledge of CNFA research landscape)
  - What constitutes a "methodological monoculture"? (Threshold: >80% of evidence from single method?)
  - How should cross-community disagreement be resolved? (Panel review? Weighted voting? Deference to most rigorous method?)

---

### G. Value of Information (VOI) Gap Closure

**Finding**: Step 12 is a placeholder. Current code doesn't check whether new beliefs close open VOI gaps.

**What should happen** (per discovery_funnel.py skeleton):
1. Maintain `DiscoveryFunnelService` registry of open questions:
   - Construct: "Does natural light improve cognitive performance?"
   - Scope: "In office buildings, working adults, 8-hour workdays"
   - Evidence status: OPEN (0 papers), PARTIALLY_CLOSED (1-2 papers), CLOSED (3+ papers with consensus)
   - VOI score: Importance × Uncertainty (how much we'd update on evidence)

2. When new paper integrated, check if it addresses any open questions:
   - Direct match: Paper measures same construct in same scope → progress toward CLOSED
   - Partial match: Similar construct or scope → progress but incomplete
   - Methodological closure: Multiple papers agree on mechanism even if scope differs → confidence boost

3. Update gap status:
   ```
   OPEN (0 papers) → PARTIALLY_CLOSED (1-2) → CLOSED (3+ consensus)

   Thresholds (configurable):
   - PARTIALLY_CLOSED: ≥1 paper with directness > 0.6
   - CLOSED: ≥3 papers, consensus credence > 0.65, <30% conflict rate
   ```

4. Auto-generate VOI reduction estimate:
   ```python
   voi_reduction = min(0.8, n_beliefs * 0.15 + n_constraints * 0.05)
   # Current formula is ad hoc; expert panel should calibrate
   ```

**Why this matters**: The system should know which questions it's answering well and which remain open. This enables intelligent resource allocation: if Natural Light Gap is CLOSED but Wayfinding Complexity Gap is still OPEN, prioritize papers on wayfinding. The VOI framework (Value of Information, from good) formalizes this: which questions, if answered, would most change the system's confidence in core constructs?

**Panel Assessment** (Good, Simon):

**Good's Take**: "VOI is well-defined in information theory. The value of answering question Q is the expected change in your decision under uncertainty. Your formula `min(0.8, n_beliefs * 0.15 + n_constraints * 0.05)` is heuristic and needs calibration. For each open question, compute actual VOI: What's your current credence in Q? How would answer Q change your actions? How much would you pay for information? Your formula hides these by averaging. Make them explicit. VOI for each question should be different based on its downstream impact."

**Simon's Take**: "Organizational perspective: VOI connects to resource allocation. If VOI(natural light question) is 0.8 and VOI(acoustics question) is 0.2, you should spend 4x more effort on natural light papers. Your system should *automatically* adjust extraction priorities based on VOI. Feed the discovery funnel into the extraction queue: 'Next batch: prioritize papers on high-VOI questions.' This closes the loop between epistemology and action."

**RECOMMENDATION**:
- **MAJOR**: Implement Step 12 to check gap closure
  - For each extracted belief, match against `DiscoveryFunnelService` gaps
  - Update gap status: OPEN → PARTIALLY_CLOSED → CLOSED
  - Log impact: "Paper closes Natural Light Gap to PARTIALLY_CLOSED (1→2 papers)"
- **MAJOR**: Compute VOI for each gap (not global heuristic)
  - VOI(Q) = ∑ P(action_i | answer=A) * impact_i - ∑ P(action_i | answer=B) * impact_i
  - Sum over all decisions downstream of question Q
- **MAJOR**: Integrate VOI into extraction priorities
  - Feed high-VOI gaps to PDF extraction queue
  - Bias extraction toward high-value questions
- **PANEL DECISION NEEDED**:
  - What are the current high-VOI questions in CNFA? (Elicit expert priorities)
  - What evidence thresholds close a gap? (3 papers? consensus > 0.65?)
  - How should scope differences be handled? (natural light in offices vs. homes—same gap or different?)

---

### H. Coherence vs. Reflective Equilibrium

**Critical tension**: The pipeline computes reflective equilibrium (Step 4) but also measures coherence change (Step 2/13). Are these compatible?

**Reflective Equilibrium** (per `extraction_to_web.py`):
- Iterative process: New belief enters → propagate through web → rerank adjacent beliefs → settle into stable state (5 iterations default)
- Purpose: Allow whole web to adjust, not just the new belief
- Potential issue: Could oscillate or diverge if web is highly interconnected

**Coherence Measurement** (per `scalable_coherence.py`):
- Snapshot: compute pairwise support scores → average → single coherence number
- Purpose: Detect whether integration improved or degraded overall consistency
- Potential issue: Could mask local conflicts (one theory improving, another degrading)

**Question**: If reflective equilibrium runs (Step 4), shouldn't coherence automatically improve? Why measure it separately (Step 2/13)?

**Spohn's perspective**: Reflective equilibrium is a *dynamics*—how the system evolves. Coherence is a *statics*—what the system looks like at rest. Measuring both is correct. Reflective equilibrium should improve coherence *on average*, but not always. If new belief is very strong but contradicts established theory, equilibrium might temporarily *lower* coherence before settling (you're revising the theory). So: measure pre-equilibrium coherence (before propagation) and post-equilibrium coherence (after settling) to see if the integration was net-good.

**RECOMMENDATION**:
- **ALREADY CORRECT**: Measure coherence pre (Step 2) and post (Step 13)
- **CLARIFY**: Document that coherence_delta includes the dynamics of reflective equilibrium
- **ADD**: Track coherence *during* iteration (per iteration 1-5) to see if system is converging or oscillating
- **PANEL DECISION NEEDED**: What are acceptable coherence dynamics?
  - Is dip followed by recovery (U-shape) okay?
  - What if final coherence is lower than initial? (Indicates genuine incompatibility)

---

## III. OVERSEER Design Deliberation

Having reviewed the integration pipeline's gaps, the panel now turns to a superordinate system health module.

### A. The Case for OVERSEER (Why Separate Module?)

**Current state**: The integration pipeline is event-driven. It fires when a paper enters: extract → validate → integrate → propagate → return. No ongoing system monitoring.

**Missing**: System-wide health check. Questions that require *global perspective*, not per-paper:

1. **Is system internally consistent?**
   - Do all beliefs have provenance? (Goal: 100%)
   - Do BN edges match web constraints? (No orphans, no missing edges)
   - Do all beliefs conform to contract? (ClaimV2 + ae.claim.v2)
   - Are all INV-1..5 satisfied? (Globally, not just local to last paper)

2. **Is system complete?**
   - Which templates have zero supporting evidence? (Identify stubs)
   - Which beliefs have no theory attachment? (Categorize orphans)
   - Which theories have zero constituent templates? (Deep gaps)
   - Which molecules have empty QA caches? (Stale summaries)

3. **Is system healthy?**
   - Coherence trend (per integration): is it declining?
   - Conflict accumulation: are conflicts growing faster than evidence?
   - Method concentration: are we vulnerable to methodological monoculture?
   - Entrenchment distribution: are a few beliefs over-entrenched?

4. **Is system recoverable?**
   - Can we reconstruct any belief's history? (Paper versioning)
   - Can we roll back to prior state? (Snapshot availability)
   - Are critical snapshots archived? (Off-disk backup)

5. **Is system improving?** (Meta-question)
   - Are new papers closing open questions?
   - Are conflicts being resolved or accumulating?
   - Is methodological diversity increasing or concentrating?
   - Is cross-community consensus improving?

**Why not solve in integration pipeline?** Because the pipeline is *about specific papers*. It has no context for global patterns. You need a separate module that looks at the *whole system*.

**Why separate vs. built into web_of_belief.py?** Separation of concerns (Parnas). The web's job is to maintain consistency within its domain (beliefs, constraints, coherence). The OVERSEER's job is to monitor and repair the system *around* the web (cache staleness, template coverage, snapshot management). Don't overload web_of_belief with system monitoring; that's a separate service.

### B. OVERSEER Sub-Components

```
┌──────────────────────────────────────────────────┐
│         OVERSEER: System Health Module            │
├──────────────────────────────────────────────────┤
│                                                  │
│  1. HEALTH MONITOR (live metrics)               │
│     - Coherence trend (per integration)         │
│     - Conflict rate (% of beliefs in dispute)   │
│     - Cache freshness (% FRESH vs STALE)        │
│     - BN stability (parameter variance)         │
│     - Queue health (stuck papers)               │
│                                                  │
│  2. INTEGRITY CHECKER (invariant validation)    │
│     - Belief provenance: every belief has       │
│       paper_id + Provenance object              │
│     - BN-Web sync: edge params ↔ web constraints│
│     - Contract compliance: all beliefs ∈        │
│       ClaimV2 schema                            │
│     - INV-1..5: check all invariants globally   │
│     - Supersession: no circular replacements    │
│     - Tag coverage: 3D tags for all beliefs     │
│                                                  │
│  3. COMPLETENESS AUDITOR (gap analysis)         │
│     - Template coverage: which have 0 beliefs?  │
│     - Theory attachment: which beliefs are      │
│       orphans (no T1/T1.5/molecule)?            │
│     - Evidence gaps: constructs with single     │
│       supporting paper (high-risk)              │
│     - Provenance chains: which beliefs are      │
│       COHERENT_ONLY (no grounding)?             │
│     - T-level coverage: theory → constituents → │
│       evidence path complete?                   │
│                                                  │
│  4. MAINTENANCE ENGINE (repairs)                │
│     - Stale cache refresh: batch-recompute      │
│       molecules marked STALE                    │
│     - Orphan cleanup: find unreachable          │
│       beliefs/constraints                       │
│     - Snapshot rotation: keep N recent,         │
│       archive older                             │
│     - Entrenchment recalc: periodic full web    │
│       coherence recompute                       │
│                                                  │
│  5. SCHEDULER (orchestrates timing)             │
│     - POST_INTEGRATION: lightweight check       │
│       after each paper (5 sec)                  │
│     - PERIODIC: full audit nightly (5-10 min)   │
│     - ALERT: immediate on threshold violation   │
│       (coherence drop > 5%, conflict spike)     │
│                                                  │
│  6. REPORTING (dashboard + escalation)          │
│     - SYSTEM_HEALTH_REPORT_[date].md            │
│     - Streamlit dashboard with 6 metrics        │
│     - Alert log with thresholds                 │
│     - Escalation: email on CRITICAL             │
│                                                  │
└──────────────────────────────────────────────────┘
```

### C. Operational Modes

**Mode 1: POST_INTEGRATION** (After each paper accepted)
- Time: 5-10 seconds
- Scope: Limited to new belief + affected neighbors
- Checks:
  - New belief has provenance ✓
  - BN edges updated ✓
  - Coherence delta < 5% ✓
  - No INV violations ✓
- Action: Log metrics; alert if threshold violated; continue (non-blocking)

**Mode 2: PERIODIC** (Nightly, off-hours)
- Time: 5-15 minutes
- Scope: Entire system
- Checks:
  - Global integrity (all beliefs have provenance)
  - Completeness (template coverage, theory attachment, evidence gaps)
  - Health trends (coherence over last 7 days, conflict accumulation)
  - Snapshot freshness (last snapshot < 24h old)
  - Cache staleness (% STALE, affected molecules)
- Action: Recompute QA caches for stale molecules; generate health report; archive snapshots

**Mode 3: ON_DEMAND** (David runs: `overseer.audit()`)
- Time: Depends on query scope
- Scope: User-specified (e.g., "audit Theory X", "find gaps in Template Y")
- Checks: Custom queries using same infrastructure
- Action: Generate focused report, suggest repairs

**Mode 4: ALERT** (Triggered by threshold violation)
- Time: < 1 second detection; action depends on severity
- Scope: Triggered check + immediate context
- Rules:
  - CRITICAL: Coherence drop > 10% OR conflict rate > 20% → Stop integration, escalate to David
  - MAJOR: Coherence drop 5-10% OR conflict rate 10-20% → Log alert, continue, inspect next period
  - MINOR: Template coverage gap OR orphan belief detected → Add to nightly report
- Action: Email David if CRITICAL

### D. Answer to Specific OVERSEER Design Questions

#### O-1: Recompute P2-P6 epistemic state per-paper or periodically?

**The Question**: After each paper integration, should the system recompute the full epistemic state (Spohn ranks P2, Pollock warrants P3, re-rank P2, Haack grounding P4, Pearl causal confidence P5, P6 cross-checks) for the entire web? Or only periodically?

**Costs of per-paper**:
- Correctness: System knows its true epistemic state after each paper
- Cost: 10-30 seconds per paper (rank computation is quadratic in belief count; 1000 beliefs = slow)
- Scalability: With 850+ papers, 10 sec × 850 = 2+ hours just for initial load

**Costs of periodic (nightly)**:
- Speed: Extraction pipeline fast; P2-P6 not in critical path
- Staleness: Users operate with stale epistemic state (up to 24h old)
- Safety: Could miss cascading failures (paper A invalidates paper B, which invalidates paper C)

**Panel Assessment** (Spohn, Pollock, Haack, Simon):

**Spohn's Take**: "Ranking theory demands consistency. If you don't recompute ranks after each belief changes, you're not maintaining the formal system. From a *mathematical* perspective, per-paper is correct. However, from an *engineering* perspective, you can batch: recompute ranks for all affected beliefs (the 'neighborhood' in the coherence graph), not the entire web. Most papers affect <50 neighbors. So: per-paper, but scoped to neighborhood."

**Pollock's Take**: "Warrants are local—a belief's warrant depends on its defeaters, its foundations, its supports. When a paper adds defeaters, they affect only warrants in the neighborhood. You don't need to recompute P3 for the entire web; scope it. Also: P3 (warrant computation) is fast (linear in neighbors); P2 is slow (rank revision is costly). Make P3 per-paper; make P2 periodic (nightly)."

**Haack's Take**: "Foundherentism requires bidirectional coherence. When new evidence enters, the entire system might need to readjust (you might have to revise distant beliefs to maintain coherence). So you *need* holistic recomputation. But: do you need to recompute *everything* or just the connected component? If web is modular (separate belief clusters with few inter-module links), recomputing the affected module is often sufficient. Analyze your web's structure first. If it's a giant strongly-connected component, per-paper recomputation is expensive."

**Simon's Take**: "Organizationally, you want bounded work per integration. Set a budget: 'Epistemic state recomputation ≤ 5 seconds per paper.' If neighborhood computation fits, do it per-paper. If it requires > 5 sec, defer to periodic. Use background jobs: mark beliefs as 'state_stale', note the time, recompute nightly. But *tell users* via dashboard that some epistemic state is stale. Don't hide staleness."

**PANEL CONSENSUS**:
- **Per-paper, scoped to neighborhood**: Recompute P2-P6 only for beliefs in the affected neighborhood (beliefs directly mentioned in new paper + their coherent neighbors within 2 hops). Fast and correct.
- **If neighborhood too large** (>50 neighbors): Fall back to marking STALE; recompute nightly.
- **Parallel to extraction**: Don't block extraction on epistemic recomputation. Fire epistemic recomputation as background task. Extraction completes quickly; epistemic state catches up within hours.

**RECOMMENDATION** (O-1 Answer):
- **Adopt neighborhood scoping**: Per-paper recomputation for P2-P6, but only for affected belief neighborhoods (within 2 hops)
- **Set budget**: If neighborhood > 50 beliefs, fall back to nightly batch
- **Non-blocking**: Don't wait for P2-P6 completion before returning from integration
- **Dashboard transparency**: Show which beliefs have STALE epistemic state

---

#### O-2: Coherence decline alert threshold?

**The Question**: When does coherence drop enough to warrant an alert?

**Candidates**:
- 5% decline (aggressive—alert on minor changes)
- 10% decline (moderate—standard for statistical significance)
- 15% decline (conservative—alert only on large changes)
- Statistical baseline (1-2σ below historical mean)
- Per-theory (alert if *any* theory's coherence drops, not global only)

**Panel Assessment** (Cartwright, Spohn, Dijkstra):

**Cartwright's Take**: "You need *granularity*. Don't just alert on global coherence decline. Alert on per-theory declines, per-construct declines, method-specific declines. A paper from a VR researcher might lower VR-coherence but raise in-situ coherence (because VR has worse validity). This is information-rich. Also: distinguish coherence in *evidence* (papers agree) vs. coherence in *interpretation* (theories agree on what evidence means). They're different."

**Spohn's Take**: "From ranking perspective: coherence decline indicates rank inconsistency. Even small declines (2-3%) suggest structural problems. I'd set a low threshold: alert if coherence_delta < -0.05 (5%). But couple it with a *type of decline* classifier: Is decline localized (one theory affected) or global? Localized is less urgent; global is critical. Rank inconsistency propagates, so even small declines need investigation."

**Dijkstra's Take**: "Define an invariant with threshold: 'Coherence ≥ C_min after every integration.' Set C_min based on domain knowledge (panel should decide what constitutes 'healthy' system coherence). Then: every integration, check `coherence_after ≥ C_min`. If violated, fail with detailed diagnostic: 'Coherence 0.61 < minimum 0.65; affected beliefs: [list]; reconciliation required.' This makes thresholds explicit and auditable."

**PANEL CONSENSUS**:
- **Per-theory thresholds**: Set different thresholds for each theory (some theories are less coherent by design)
- **Statistical baseline**: Compute historical mean over past 50 integrations; alert if delta < mean - 1σ
- **Fallback absolute threshold**: 5% global decline (if historical baseline unavailable)
- **Type classification**: Separate alerts for localized (one theory) vs. global (multiple) declines
- **Dashboard**: Show coherence per theory over time; highlight declining theories

**RECOMMENDATION** (O-2 Answer):
- **Adopt statistical baseline with per-theory granularity**
  - Compute coherence_delta distribution per theory from past 50 integrations
  - Alert MAJOR if delta < mean - 1σ
  - Alert CRITICAL if delta < mean - 2σ
- **Fallback**: If history unavailable, use 5% threshold for global coherence decline
- **Transparency**: Display pre/post coherence in integration report; highlight affected theories
- **Panel calibration**: Expert panel to set C_min (minimum healthy coherence) for each theory

---

#### O-3: Auto-retire violations or flag-only?

**The Question**: If a belief violates INV-1..5 (e.g., no provenance, circular supersession, orphan constraint), should OVERSEER auto-retire it, or only flag for human review?

**Options**:

**A. Auto-repair** (Aggressive)
- OVERSEER detects violation, auto-retires belief, updates credences, rebuilds BN edges
- Advantages: System stays clean; no accumulating debt
- Disadvantages: Could silently delete important beliefs; violates transparency

**B. Flag-only** (Conservative)
- OVERSEER detects violation, adds to alert log, surfaces in dashboard
- David reviews and decides whether to retire
- Advantages: Transparent; human oversight; no silent deletions
- Disadvantages: Violations accumulate; could corrupt analyses

**C. Quarantine** (Middle ground)
- OVERSEER detects violation, marks belief as QUARANTINED
- Quarantined beliefs excluded from coherence computation, BN, user-facing metrics
- David reviews; if violation is repairable, fix it; if not, retire
- Advantages: Prevents corruption while keeping beliefs available for review
- Disadvantages: More complex state management

**Panel Assessment** (Dijkstra, Simon, Haack):

**Dijkstra's Take**: "Correctness first. Never auto-repair without human approval. If a belief violates invariants, the system should *fail loudly*. Write it as an assertion: `assert_no_violations(belief)` before using it. Let David see the problem, understand it, decide. Automated 'cleanup' hides bugs. You'll learn more from violations than from silently fixing them."

**Simon's Take**: "Organizational perspective: violations indicate process failures. If a belief has no provenance, *why*? Was it created by a stub? By a migration error? By a user input that wasn't validated? Auto-retiring hides the process problem. Better to quarantine (mark INVALID, investigate root cause, then decide whether to retire or fix process). Quarantine is the organizational analog of logging."

**Haack's Take**: "Foundherentism requires *justified* beliefs. A belief without provenance is not justified. You should not use it in coherence computation. So: quarantine is correct. Remove it from live computation, but preserve it as evidence of a problem (maybe it's a good belief that just lacks documentation; maybe it's a real error). Human review should distinguish."

**PANEL CONSENSUS**:
- **Adopt Quarantine (Option C)**: Violations trigger QUARANTINE status, not auto-retire
- **Exclude from metrics**: Quarantined beliefs don't count toward coherence, conflict rate, coverage
- **Log and escalate**: Alert David with details (belief ID, violation type, root cause hypothesis)
- **Review workflow**: David can: (1) fix provenance (QUARANTINE → ACTIVE), (2) retire (QUARANTINE → RETIRED), (3) investigate

**RECOMMENDATION** (O-3 Answer):
- **Adopt quarantine protocol**
  - New status: QUARANTINED (distinct from ACTIVE, RETIRED, SUPERSEDED)
  - Exclusion: Quarantined beliefs not in coherence, BN, user queries
  - Escalation: Alert flagged as REVIEW_REQUIRED
  - Review window: David must review within 7 days or auto-retire
- **Logging**: Maintain audit trail (when quarantined, why, what repairs attempted)

---

#### O-4: BN coupling—how should parameters interact with entrenchment?

**Previously addressed** in Section II.C.

**PANEL CONSENSUS**:
- **Adopt hierarchical one-directional coupling** (Option 3 from earlier)
- **Direction**: Web credences → BN edge priors (not bidirectional)
- **Mapping**: Edge weight = f(credence, quality, causal_specificity)
- **No feedback loop**: BN posterior doesn't revise web credences
- **Modularity**: Clean interface between epistemology (web) and causality (BN)

**RECOMMENDATION** (O-4 Answer):
- **Implement mapping formula**:
  ```
  edge_prior_p = 0.3 + 0.7 * web_credence * quality_weight
  ```
  where `quality_weight ∈ [0, 1]` accounts for paper quality
- **Test for alignment**: Periodically check BN edges against web constraints
  - If edge posterior drifts from credence (e.g., credence 0.9 but posterior 0.4), investigate
  - Could indicate: (1) edge definition is wrong, (2) credence computation is wrong, (3) BN data is inconsistent
- **Document assumptions**: Write specification of coupling formula; make it auditable

---

#### O-5: Provenance computation—sync or deferred?

**Previously addressed** in Section II.B.

**PANEL CONSENSUS**:
- **Synchronous during Step 5** (integration): Construct `Provenance` objects immediately
- **Rationale**: Provenance is foundational to Haack's epistemology; cannot be deferred
- **Cost**: Minimal (mapping study_design → StudyType is fast)
- **Benefit**: Beliefs are immediately justified or flagged as COHERENT_ONLY

**RECOMMENDATION** (O-5 Answer):
- **Implement Provenance object creation in Step 5**:
  ```python
  provenance = Provenance.from_extraction(
      study_design=extraction.study_design,
      measurement_type=extraction.measurement_type,
      directness=infer_directness(extraction),
      grounding_chain=build_chain(belief, extraction),
      justification_status=determine_status(...)
  )
  belief.provenance = provenance
  belief.provenance_id = persist(provenance)
  ```
- **Grounding chain**: Lazy (build on demand, cache results)
- **Justification status**: Compute eagerly (no cost)

---

#### O-6: QA cache recomputation—eager, lazy, or batched?

**Previously addressed** in Section II.D.

**PANEL CONSENSUS**:
- **Adopt batched (Option C)**: Nightly bulk recomputation
- **Rationale**: Balances cost, freshness, pipeline performance
- **Schedule**: Off-hours batch job; recomputes all STALE caches

**RECOMMENDATION** (O-6 Answer):
- **Implement batched recomputation**:
  - Mark caches STALE during integration (fast)
  - Batch recomputation: nightly at 2 AM, all stale molecules, bulk LLM call (cheaper)
  - FreshStatus updated: STALE → FRESH + timestamp
- **Transparency**: Surface freshness to users via dashboard
  - "Summary last updated 4h ago" (FRESH)
  - "Summary stale; refreshing..." (STALE, in progress)
  - "Waiting for nightly refresh" (STALE, scheduled)
- **Configuration**: Adjust freshness window (24h vs. 12h) based on load

---

#### O-7: OVERSEER database—separate or shared?

**The Question**: Should OVERSEER maintain its own SQLite database, or use the existing web_persistence.py database?

**Option A: Separate database** (`overseer.db`)
- OVERSEER maintains own tables for:
  - Health metrics (coherence_trend, conflict_rate, cache_freshness)
  - Integrity checks (invariant_violations, constraint_mismatches)
  - Completeness gaps (template_coverage, orphan_beliefs, evidence_gaps)
  - Snapshots (state_snapshots with timestamps)
  - Audit logs (overseer_actions, maintenance_events)
- Advantages: Clean separation; OVERSEER doesn't depend on web schema
- Disadvantages: Data duplication; potential sync issues

**Option B: Shared database** (extend `ae.db`)
- OVERSEER uses tables in existing database
- New tables: `overseer_health_metrics`, `invariant_violations`, `snapshot_index`
- Advantages: Single source of truth; easier consistency
- Disadvantages: Web changes could break OVERSEER queries; schema coupling

**Option C: Hybrid**
- OVERSEER keeps *hot* data in own DB (recent metrics, current alerts)
- Persists to shared DB for long-term storage/reporting
- Advantages: Performance (hot queries fast) + consistency (shared archive)
- Disadvantages: Most complex; requires careful sync

**Panel Assessment** (Parnas, Liskov, Simon):

**Parnas's Take**: "Information hiding principle: OVERSEER's internals should be hidden from web_of_belief.py and vice versa. That argues for separate database. Define clean interface: OVERSEER exports read-only metrics tables (coherence trend, health summary); web exports read-only state snapshot. Each can query the other, but they don't share operational tables."

**Liskov's Take**: "Software architecture: think of web_of_belief and OVERSEER as separate services with separate contracts. The web's contract: maintain consistent beliefs, constraints, credences. OVERSEER's contract: monitor health and repair problems. Services should have separate stores. However, if they need to share data, define a careful synchronization protocol: timestamps, version numbers, conflict resolution. Option B (shared DB) creates tight coupling; Option A (separate DB) creates two sources of truth; Option C (hybrid) requires careful protocol."

**Simon's Take**: "Scale question: how much data are we talking? Web data: ~10,000 beliefs × versioning = 50,000 records. OVERSEER data: daily metrics × 365 days × 10 metrics = 3,650 records. Mostly small. Separate database is fine—you won't run into scaling issues. Keep it simple: Option A, separate database. Easier to understand, maintain, and debug."

**PANEL CONSENSUS**:
- **Adopt Option A (Separate database)** with clean interface protocol
- **Rationale**: Clear separation of concerns; easier to maintain and evolve independently

**RECOMMENDATION** (O-7 Answer):
- **Implement separate `overseer.db` database**:
  ```sql
  -- Health metrics (updated per-paper or nightly)
  CREATE TABLE health_metrics (
    metric_id TEXT,
    metric_type TEXT,  -- coherence, conflict_rate, cache_freshness, ...
    timestamp TEXT,
    value REAL,
    scope TEXT  -- global | per_theory | per_template
  );

  -- Integrity violations
  CREATE TABLE invariant_violations (
    violation_id TEXT,
    belief_id TEXT,
    invariant TEXT,  -- INV-1, INV-2, ...
    violation_text TEXT,
    quarantine_status TEXT,  -- QUARANTINED | RESOLVED | RETIRED
    timestamp TEXT
  );

  -- Snapshots (for rollback)
  CREATE TABLE snapshot_index (
    snapshot_id TEXT,
    timestamp TEXT,
    description TEXT,
    compressed_state BLOB
  );
  ```
- **Sync protocol**: OVERSEER reads from `ae.db` (read-only), writes to `overseer.db`
- **Interface**: Define clean API:
  - `web.get_snapshot()` → {beliefs, constraints, credences, entrenchment}
  - `overseer.record_health(metric, value, scope)` → write to overseer.db
  - `overseer.get_health_report(days=7)` → summarize last 7 days

---

#### O-8: Parallel Claude sessions—how should OVERSEER interact?

**The Question**: The system supports parallel work (per PARALLEL_WORK.md). How should OVERSEER behave when multiple Claude terminals are working?

**Scenarios**:
1. Terminal-A integrating papers while Terminal-B does batch recomputation
2. Terminal-A checks health while Terminal-B is mid-integrity-check
3. Both terminals try to update same BN edge simultaneously

**Options**:

**A. Single-writer** (OVERSEER is exclusive)
- Only one terminal can run OVERSEER at a time
- Others wait (acquire lock on overseer.db)
- Advantages: Simple; no conflicts
- Disadvantages: Slow if OVERSEER work is frequent; blocking

**B. PARALLEL_WORK.md protocol** (claim work lane)
- OVERSEER work is assignable to lanes (like extraction/integration)
- Terminal-A claims OVERSEER lane; others avoid OVERSEER ops
- Advantages: Organized; explicit coordination
- Disadvantages: Requires protocol discipline

**C. Read-only sharing** (separate ops by mode)
- POST_INTEGRATION health checks (lightweight) can run in parallel
- PERIODIC maintenance (batch operations) exclusive to one terminal
- Advantages: Allows parallelism where safe
- Disadvantages: More complex state management

**Panel Assessment** (Simon, Dijkstra):

**Simon's Take**: "Organizational rule: critical operations should have a single owner. OVERSEER maintenance (snapshot rotation, nightly batch) should be single-terminal work. But health *monitoring* (reading metrics) should be read-only parallelizable. Use protocol B: declare 'OVERSEER maintenance' as exclusive work lane. Terminal wanting to do it claims the lane. Health queries are cheap and don't need claiming."

**Dijkstra's Take**: "Correctness: you must prevent concurrent modification of overseer.db. Simplest approach: file lock. When OVERSEER acquires lock, other terminals wait. Set timeout (30 sec for normal work, 5 min for batch work). If timeout expires, log and alert. This prevents silent failures from concurrent updates."

**PANEL CONSENSUS**:
- **Adopt PARALLEL_WORK.md protocol (Option B)** with read-only exception
- **Coordination**: Maintenance work (nightly batch, snapshot rotation, stale cache recompute) must claim exclusive OVERSEER lane
- **Read-only**: Health monitoring/reporting doesn't require claiming (read-only access is safe)

**RECOMMENDATION** (O-8 Answer):
- **Implement in PARALLEL_WORK.md**:
  ```markdown
  ## OVERSEER Work Lanes

  | Operation | Exclusive? | Lane | Max Duration |
  |-----------|------------|------|--------------|
  | Nightly batch refresh | YES | OVERSEER-MAINT | 15 min |
  | Snapshot rotation | YES | OVERSEER-MAINT | 5 min |
  | Integrity check (full) | YES | OVERSEER-MAINT | 10 min |
  | Health metric query | NO | — | — |
  | Quarantine investigation | NO | — | — |
  ```

- **Locking mechanism**:
  ```python
  # Claim lane
  with PARALLEL_WORK.claim_lane('OVERSEER-MAINT', max_duration=15*60):
      # Perform maintenance operations
      overseer.nightly_batch_refresh()
  # Automatically release lane
  ```

---

## IV. Concrete Architecture Recommendation

Based on panel deliberation, here is the recommended OVERSEER implementation:

### System Architecture

```python
# src/services/overseer.py (new file)

class OverseerService:
    """System health monitoring and maintenance."""

    def __init__(self, web_db: str, overseer_db: str, config: OverseerConfig):
        self.web_db = web_db
        self.overseer_db = overseer_db
        self.config = config

        # Sub-components
        self.health_monitor = HealthMonitor(overseer_db)
        self.integrity_checker = IntegrityChecker(web_db, overseer_db)
        self.completeness_auditor = CompletenessAuditor(web_db, overseer_db)
        self.maintenance_engine = MaintenanceEngine(web_db, overseer_db)
        self.reporter = OverseerReporter(overseer_db)

    # PUBLIC API

    def post_integration_check(self, paper_id: str, integration_event: PaperIntegrationEvent):
        """Lightweight health check after paper integration. ~5 sec."""
        # O-1: Recompute P2-P6 for affected neighborhood
        self._recompute_epistemic_neighborhood(paper_id)

        # O-2: Check coherence delta
        self._check_coherence_threshold(integration_event)

        # Measure post-integration metrics
        metrics = {
            'coherence': integration_event.coherence_after,
            'coherence_delta': integration_event.coherence_delta,
            'conflict_rate': self._compute_conflict_rate(),
            'cache_freshness': self._compute_cache_freshness(),
        }
        self.health_monitor.record_metrics(metrics)

        # Alert if threshold violated
        if integration_event.coherence_delta < -0.05:
            self._escalate_alert('COHERENCE_DROP', integration_event)

    def periodic_full_audit(self):
        """Full system health check (nightly, requires exclusive OVERSEER lane)."""
        with PARALLEL_WORK.claim_lane('OVERSEER-MAINT', max_duration=15*60):
            # 1. Integrity checks (all beliefs have provenance, etc.)
            violations = self.integrity_checker.audit_all_invariants()
            for v in violations:
                self._quarantine_belief(v.belief_id, v.invariant)

            # 2. Completeness audit (gaps, orphans, coverage)
            gaps = self.completeness_auditor.audit_coverage()

            # 3. Health trend analysis
            health_report = self.health_monitor.generate_report(days=7)

            # 4. Maintenance operations
            self.maintenance_engine.refresh_stale_caches()  # O-6: batched LLM calls
            self.maintenance_engine.cleanup_orphans()
            self.maintenance_engine.rotate_snapshots()

            # 5. Generate report and escalate if needed
            report = self.reporter.generate_full_report(gaps, violations, health_report)
            self._save_report(report)
            if health_report.health_status == 'CRITICAL':
                self._send_alert_to_david(report)

    def on_demand_audit(self, scope: str = 'full'):
        """Interactive audit run by David (no lane claiming needed for read-only)."""
        if scope == 'full':
            return self.periodic_full_audit()
        elif scope == 'integrity':
            return self.integrity_checker.audit_all_invariants()
        elif scope == 'completeness':
            return self.completeness_auditor.audit_coverage()
        elif scope == 'health':
            return self.health_monitor.generate_report(days=30)
        else:
            raise ValueError(f"Unknown audit scope: {scope}")

    # INTERNAL METHODS

    def _recompute_epistemic_neighborhood(self, paper_id: str):
        """O-1: Per-paper recomputation, scoped to neighborhood."""
        from src.services.epistemic_orchestrator import EpistemicOrchestrator

        # Get beliefs mentioned in paper
        belief_ids = self._get_beliefs_from_paper(paper_id)

        # Get neighbors within 2 hops
        neighborhood = self._get_neighborhood(belief_ids, hops=2)

        if len(neighborhood) > 50:
            # Too large; mark STALE, recompute nightly
            for belief_id in neighborhood:
                self._mark_epistemic_stale(belief_id)
            return

        # Recompute P2-P6 for neighborhood (non-blocking)
        orchestrator = EpistemicOrchestrator()
        for belief_id in neighborhood:
            orchestrator.recompute_epistemic_state(belief_id)

    def _check_coherence_threshold(self, event: PaperIntegrationEvent):
        """O-2: Check coherence delta against historical baseline."""
        # Get historical distribution from past 50 integrations
        history = self.health_monitor.get_coherence_history(window=50)

        if len(history) < 10:
            # Not enough history; use absolute threshold
            threshold = -0.05
        else:
            # Statistical baseline: alert if delta < mean - 1σ
            mean = statistics.mean(history)
            stdev = statistics.stdev(history)
            threshold = mean - stdev

        if event.coherence_delta < threshold:
            severity = 'CRITICAL' if event.coherence_delta < threshold - stdev else 'MAJOR'
            self._escalate_alert(severity, f"Coherence delta {event.coherence_delta:.3f} below threshold {threshold:.3f}")

    def _quarantine_belief(self, belief_id: str, violation: str):
        """O-3: Quarantine violating belief."""
        # Mark belief as QUARANTINED in web_db
        self._update_belief_status(belief_id, 'QUARANTINED')

        # Record violation
        self.integrity_checker.log_violation(belief_id, violation)

        # Alert David
        self._send_alert_to_david(f"Belief {belief_id} quarantined: {violation}")

    def _escalate_alert(self, alert_type: str, details: str):
        """Route alert based on severity."""
        severity = alert_type.split('_')[0]  # CRITICAL, MAJOR, MINOR

        if severity == 'CRITICAL':
            # Email David + log
            self._send_alert_to_david(f"CRITICAL: {details}")
        elif severity == 'MAJOR':
            # Log + add to dashboard
            self.reporter.log_alert(alert_type, details)
        else:
            # Add to nightly report only
            self.reporter.queue_for_report(alert_type, details)
```

### Integration with Pipeline

In `src/services/paper_integration/orchestrator.py`, add:

```python
from src.services.overseer import OverseerService

class PaperIntegrationOrchestrator:
    def __init__(self, ...):
        # ... existing init code ...
        self.overseer = OverseerService(web_db, overseer_db, config)

    def integrate_paper(self, paper_id: str):
        """14-step cascade with OVERSEER integration."""
        event = self._initialize_event(paper_id)

        try:
            # Steps 1-13 (existing)
            self._step_1_prevalidate(event)
            # ... steps 2-13 ...
            self._step_13_postvalidate(event)

            # Post-integration health check (non-blocking)
            # Fire in background so extraction pipeline returns quickly
            threading.Thread(
                target=self.overseer.post_integration_check,
                args=(paper_id, event),
                daemon=True
            ).start()

            event.status = IntegrationStatus.COMPLETED
            return event

        except Exception as e:
            event.status = IntegrationStatus.FAILED
            self.overseer.on_demand_audit(scope='integrity')  # Check for damage
            raise
```

### Nightly Scheduler

In `scripts/overseer_scheduler.py`:

```python
"""Nightly OVERSEER batch jobs. Runs off-hours."""

import schedule
import time
from src.services.overseer import OverseerService
from src.parallel_work import PARALLEL_WORK

def run_nightly_overseer():
    """Run at 2 AM daily."""
    overseer = OverseerService(
        web_db='ae.db',
        overseer_db='overseer.db',
        config=OverseerConfig()
    )

    print("[OVERSEER] Starting nightly batch job...")
    try:
        overseer.periodic_full_audit()
        print("[OVERSEER] Nightly batch complete.")
    except Exception as e:
        print(f"[OVERSEER] ERROR: {e}")
        # Send alert but don't crash
        overseer._send_alert_to_david(f"Nightly OVERSEER job failed: {e}")

if __name__ == '__main__':
    schedule.every().day.at("02:00").do(run_nightly_overseer)

    while True:
        schedule.run_pending()
        time.sleep(60)
```

---

## V. Implementation Priority & Phasing

### Phase 1: Critical Path (Week 1-2)

**Must complete before scaling extraction**:

1. **Wire credence computation** (Section II.A)
   - Replace Step 4-5 stub with `extraction_to_web.integrate_extraction()` + `web_persistence.accumulate_belief()`
   - Task: 2-3 days (mostly integration, existing code)
   - Owner: Engineering

2. **Implement Provenance objects** (Section II.B)
   - Create `Provenance` dataclass, `grounding_chain` computation
   - Map `study_design` → `StudyType`; determine `justification_status`
   - Task: 2-3 days
   - Owner: Engineering + Epistemology panel

3. **Wire BN updates** (Section II.C)
   - Implement Step 9 with `BetaBernoulliEdge.update()`
   - Establish hierarchical coupling (Option 3)
   - Task: 2-3 days
   - Owner: Engineering

4. **Add coherence pre/post measurement** (Section II.E)
   - Wire Steps 2 & 13 to call coherence computation
   - Log coherence_delta; establish baseline for alerts
   - Task: 1 day
   - Owner: Engineering

**Phase 1 Deliverable**: Integration pipeline with critical components wired (credence, provenance, BN, coherence).

---

### Phase 2: Integrity & Monitoring (Week 2-3)

**OVERSEER foundation**:

5. **Implement OVERSEER core services**
   - Health Monitor (coherence trend, conflict rate, cache freshness)
   - Integrity Checker (invariants, provenance, BN-web sync)
   - Task: 3-4 days
   - Owner: Engineering

6. **Set up health metrics schema** (overseer.db)
   - Define tables: health_metrics, invariant_violations, snapshot_index
   - Task: 1 day
   - Owner: Engineering

7. **Implement POST_INTEGRATION health check**
   - Runs after each paper (non-blocking, 5-10 sec)
   - Task: 1-2 days
   - Owner: Engineering

**Phase 2 Deliverable**: OVERSEER monitoring for system health (metrics, alerts).

---

### Phase 3: Completeness & Maintenance (Week 3-4)

**OVERSEER full suite**:

8. **Implement Completeness Auditor**
   - Template coverage, theory attachment, evidence gaps, provenance chains
   - Task: 2-3 days
   - Owner: Engineering

9. **Implement Maintenance Engine**
   - Stale cache refresh (batched), orphan cleanup, snapshot rotation
   - Task: 2-3 days
   - Owner: Engineering

10. **Implement nightly scheduler**
    - Periodic full audit (OVERSEER-MAINT lane)
    - Task: 1 day
    - Owner: Engineering

11. **Dashboard reporting**
    - Streamlit dashboard for health metrics
    - Automated report generation
    - Task: 2-3 days
    - Owner: Frontend

**Phase 3 Deliverable**: Full OVERSEER module operational (health, integrity, completeness, maintenance).

---

### Phase 4: Expert Calibration (Week 4)

**Panel-driven parameterization**:

12. **Calibrate alerting thresholds**
    - Coherence decline threshold (per-theory)
    - Conflict rate threshold (%)
    - Method concentration threshold
    - Panel task: 1-2 days

13. **Calibrate community identification**
    - Define CNFA epistemic communities
    - Establish community-relative credence computation
    - Panel task: 1-2 days

14. **Calibrate VOI framework**
    - Compute actual VOI for each gap (not heuristic)
    - Define gap closure thresholds
    - Panel task: 1-2 days

**Phase 4 Deliverable**: OVERSEER fully parameterized and calibrated for CNFA domain.

---

## VI. Open Questions for David

The panel recommends asking David's expertise on:

1. **Community identification** (Section II.F):
   - What are the major epistemological communities in CNFA research? (Lab clusters, methodological traditions, theoretical schools?)
   - Should community identification be keyword-based (current proposal) or embedding-based (more sophisticated)?
   - How should community consensus be weighted against individual paper quality?

2. **VOI priorities** (Section II.G):
   - Which CNFA questions have highest value-of-information? (Which answered first would most improve building design decisions?)
   - Should VOI be based on David's expert judgment, or computed from decision-analytic framework?
   - How should extraction priorities be adjusted based on VOI? (Currently: triage by keyword; should it be: triage by high-VOI?)

3. **Freshness windows** (Section II.D & O-6):
   - Is 24-hour cache freshness acceptable, or should nightly refresh target <12h staleness?
   - Should users see "stale summary" warnings, or only David (on dashboard)?
   - Cost trade-off: faster LLM recomputation ($2/molecule) vs. current batch cost ($0.30/molecule)?

4. **Coherence health criteria** (Section II.E & O-2):
   - What constitutes "healthy" global coherence for the system? (Threshold C_min = 0.65? 0.75?)
   - Should per-theory coherence have different thresholds? (E.g., is 0.6 okay for Embodied Cognition but not for Stress Recovery?)
   - How important is it to alert on coherence *increases*? (Could signal over-fitting)

5. **Epistemic state recomputation budget** (O-1):
   - Is 5-second budget per paper acceptable, or should we be faster?
   - How large can a "neighborhood" be before we defer recomputation? (Current proposal: >50 beliefs)
   - Should P2-P6 recomputation be blocking (slow extraction) or non-blocking (stale for a few hours)?

6. **Parallel work coordination** (O-8):
   - Is PARALLEL_WORK.md protocol sufficient, or do we need more sophisticated locking?
   - Should OVERSEER maintenance jobs have a hard time limit (e.g., fail if > 15 min)?
   - When parallel jobs conflict (e.g., both trying to update same belief), what's the right strategy (fail, retry, queue)?

7. **Auto-repair vs. quarantine** (O-3):
   - Is quarantine sufficient, or would David prefer higher-risk auto-repair of known-fixable violations?
   - What's the review window? (7 days before auto-retire? Different for different violation types?)
   - Should some violations be auto-retired immediately? (E.g., circular supersession is clearly a bug)

8. **Long-term scalability**:
   - How many papers does the system eventually need to handle? (Currently: 850; eventually: 5,000? 10,000?)
   - Does per-paper neighborhood recomputation (O-1) scale? (Might be slow with 10,000 papers)
   - Should we plan for distributed/parallel coherence computation?

---

## VII. Panel Consensus & Dissent

### Consensus (All Panelists Agree)

1. **Provenance is foundational** (Haack requirement): Every belief must have Provenance object computed synchronously during integration.

2. **Coherence per-theory, not just global**: Cartwright's dashboard approach is superior to single coherence number.

3. **Quarantine, don't auto-repair**: Dijkstra's principle. Flag violations, let David decide.

4. **Separate OVERSEER module**: Not built into web_of_belief.py; clean separation of concerns (Parnas).

5. **Integration pipeline must wire to existing services**: Stubs (Steps 4-5, 9, 10, 11, 12) must call actual computation.

### Dissent (Panelists Disagree)

**Q: Per-paper vs. nightly recomputation of P2-P6 epistemic state (O-1)?**

- **Spohn & Pollock**: Per-paper neighborhood recomputation (correct; tractable with scoping)
- **Haack**: Per-paper global recomputation (but accepts neighborhood scoping as pragmatic compromise)
- **Simon**: Nightly batch only (organizational efficiency)
- **Consensus achieved**: Per-paper neighborhood (Spohn/Pollock compromise); if neighborhood > 50, defer to nightly

**Q: Coherence decline alert threshold (O-2)?**

- **Spohn**: Very low threshold (~2-3%) — even small rank inconsistencies matter
- **Cartwright**: Per-theory thresholds, not global (different theories have different coherence expectations)
- **Dijkstra**: Absolute threshold (C_min invariant) — define "healthy" once, enforce everywhere
- **Consensus achieved**: Statistical baseline (historical mean ± 1σ) with per-theory granularity

**Q: Provenance depth—how much Haack computation (Section II.B)?**

- **Haack**: Full grounding chains; every belief traces to experiential basis (expensive)
- **Simon**: Lightweight provenance (study_type + directness + justification_status); grounding chains lazy (expensive to build, build on demand)
- **Consensus achieved**: Lightweight provenance synchronous; grounding chains lazy (cache results)

---

## VIII. Recommendations Summary

### Immediate Actions (This Week)

1. **Wire Steps 4-5** to `extraction_to_web.integrate_extraction()` + `web_persistence.accumulate_belief()` — CRITICAL
2. **Implement Provenance objects** in Step 5 — CRITICAL
3. **Wire Step 9** to `BetaBernoulliEdge.update()` — CRITICAL
4. **Add coherence pre/post** measurement (Steps 2 & 13) — CRITICAL

### Short-Term (Next 2-3 Weeks)

5. Implement OVERSEER core services (Health Monitor, Integrity Checker)
6. Set up overseer.db schema and health metrics
7. Implement POST_INTEGRATION health check (non-blocking)

### Medium-Term (Weeks 3-4)

8. Implement Completeness Auditor and Maintenance Engine
9. Deploy nightly scheduler for periodic full audit
10. Build Streamlit dashboard for health reporting

### Panel-Driven (Week 4+)

11. **Expert panel calibration sessions** for:
    - Coherence thresholds (per-theory)
    - Community identification in CNFA
    - VOI calibration for research priorities
    - Open question priority ranking

### Answers to O-1 through O-8

| Question | Answer | Rationale |
|----------|--------|-----------|
| **O-1: Per-paper or nightly recomputation?** | Per-paper neighborhood (Spohn scoping); defer if >50 beliefs | Correctness + tractability |
| **O-2: Coherence alert threshold?** | Statistical baseline (mean ± 1σ) per-theory | Context-sensitive + granular |
| **O-3: Auto-retire or quarantine?** | Quarantine (Option C); review required before retire | Safety + transparency |
| **O-4: BN coupling?** | Hierarchical one-directional (web → BN) | Separates epistemology from causality |
| **O-5: Provenance sync or deferred?** | Synchronous (Step 5) | Foundational to Haack epistemology |
| **O-6: QA cache strategy?** | Batched nightly (Option C) | Balance cost/freshness/performance |
| **O-7: OVERSEER database?** | Separate overseer.db | Clean separation (Parnas) |
| **O-8: Parallel sessions?** | PARALLEL_WORK.md exclusive lanes for maintenance | Explicit coordination |

---

## IX. Conclusion

The Article Eater system is epistemologically sophisticated but architecturally incomplete. The integration pipeline has the right structure (14-step cascade) but several critical steps are stubs (credence computation, provenance, BN updates, QA cache, social epistemology, VOI gaps). The recommended fixes are engineering work, not research—execute them immediately.

Beyond integration, the system needs system-level health monitoring. The OVERSEER module addresses this: ongoing consistency checks, completeness audits, health monitoring, maintenance scheduling. This separates the *event-driven* logic (per-paper integration) from the *steady-state* logic (system health), a clean architectural distinction (Simon, Parnas).

The panel has identified 8 critical design decisions for OVERSEER (O-1 through O-8) and provided panel consensus on 7 of them. Decision O-1 (per-paper vs. nightly recomputation) had productive dissent; the consensus (per-paper neighborhood with nightly fallback) represents a principled compromise balancing correctness (Spohn/Pollock) and efficiency (Simon).

**Next step**: Execute Phase 1 (wire credence, provenance, BN, coherence). Then convene a follow-up panel session for calibration (community identification, VOI priorities, coherence thresholds).

---

**Document Prepared By**: Claude Code, on behalf of Panel
**Panel Members**: Quine, Haack, Spohn, Pollock, Pearl, Cartwright, Good, DerSimonian, Simon, Ashby, Parnas, Dijkstra, Liskov, Lamport, Sackett, Kyburg, Glymour
**Status**: FOR DAVID'S APPROVAL — Actionable recommendations with documented dissent
**Next Review**: 2026-03-03 (after Phase 1 wiring complete)
