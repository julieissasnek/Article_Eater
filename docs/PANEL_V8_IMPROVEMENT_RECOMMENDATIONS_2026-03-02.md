# ATLAS Expert Panel V8: Comprehensive Improvement Recommendations
## Convened 2026-03-02

**Panel Chair**: David Kirsh (UCSD Cognitive Science)
**Panelists**: Nancy Cartwright, Judea Pearl, Paul Thagard, Susan Haack, Roger Cooke, Gregory Murphy, James Woodward
**Audit Basis**: RUTHLESS V8 (data integrity + system health), End-to-End Pipeline Audit (integration verification)
**Overall System State**: PRODUCTION-READY architecturally, DATA-HEALTHY, operationally DEGRADED (AESHI 49/100 RED due to sanity check gate failure; STABILITY 54.17%)

---

## CONTEXT: Current System State

### Strengths (from V8 Audit)
- **Data Assets**: 33,166 findings from 1,069 papers. Templates (166/166 perfect), theories (24/25), contracts (3/3), figures (42/42) all excellent condition.
- **Architecture**: All critical pipelines wired. Validator gates active. Warrant-derived credence (R6 dual-credence) integrated. Nightly overseer with 13 monitored invariants.
- **Pipeline Integrity**: 5,529 tests passing. 98.6% Python scripts syntactically valid. Module imports all succeed.

### Critical Issues (Blocking Production Deployment)
- **AESHI Health**: 49/100 RED. Sanity check gate failing at `/scripts/compute_system_health.py:123` (Pydantic deprecation warning).
- **Stability Subscore**: 54.17% FAIR — indicates intermittent runtime failures.
- **Extraction Schema**: 2.7% of files (29/1,069) have non-standard structure. 5 scripts have syntax errors.
- **Gap in Data Persistence**: Scope_json exists at extraction time but NOT persisted to DB — creates interpretation space boundary bottleneck.

---

## PANEL DELIBERATION: Round 1

### Topic A: What is the single most impactful improvement for ATLAS right now?

**Nancy Cartwright (LSE, Philosophy of Science)**:
The single most impactful improvement is **establishing external validity chains**. Your system extracts claims from papers and builds a coherence network, but you have no systematic way to assess whether a claim that is *internally coherent* is *externally valid* — i.e., whether it actually generalizes to real-world environmental contexts. The population transfer factor (δ) exists but is not calibrated; the study design taxonomy (d values) has Woodward's stamp of approval but lacks empirical validation on your actual 33,166 findings.

Without this, you risk building a perfectly coherent but entirely self-referential epistemic network — what I call "coherence in the void." The nightly overseer monitors 13 invariants but none of them directly test: "If we acted on this belief in a real building, would it work?" This is the transportability problem writ large.

**Action**: Before anything else, audit your 33,166 findings against a small sample (100-200) of *ground truth* cases — documented interventions where architects or designers made decisions based on environmental psychology principles and the outcomes are measured. This is hard but doable (building retrofit studies, wayfinding interventions, lighting adjustments with documented occupant satisfaction). If even 60% of your high-credence beliefs match ground truth, you have external validity. If less than 40%, your coherence metric is misleading.

**Judea Pearl (UCLA, Causal Inference)**:
Cartwright is right, but I'd phrase it differently: **your causal model is underspecified**. You have a bipartite network (claims and rules) but the *causal directionality* is implicit. When you infer that "Natural light → attention restoration," is that a causal claim (natural light *causes* attention restoration) or a correlation (they co-vary)? Your warrant types (mechanistic, empirical_association, etc.) hint at directionality, but your Bayesian network doesn't enforce it.

Here's the specific gap: Your epistemic_projection.py implements the formula σ(Σ d·ω·δ·logit(p_lab)) correctly for *parametric* inference (predicting p_target given p_lab), but it has no do-calculus component. If a claim is confounded (e.g., natural light correlates with room size, and room size causes attention restoration), your formula doesn't detect it. The confounder control parameter (embedded in ω via warrant strength) is post-hoc, not causal-model-based.

**Action**: Audit your 25 theories for confounding risk. For each, ask: "What unmeasured factors correlate with both the alleged cause and the outcome?" Create a confounder checklist (socioeconomic status, individual differences, measurement artifacts) and flag high-risk claims. This feeds directly into your QA pipeline — claims with uncontrolled confounders drop in credence.

**Paul Thagard (Waterloo, Cognitive Science)**:
Both good, but missing the systems angle. **Your coherence metric is static**. You compute C* = (A − λ·V) / A_max once per paper integration, but you don't track *why* coherence changes or *which beliefs* are doing the coherence work. In real scientific reasoning, coherence is dynamic: as new evidence arrives, coherence drops, beliefs revise, coherence recovers. Your system integrates papers one at a time and updates the web, but you never ask: "Is this new belief *supposed* to increase coherence, or is it an outlier we should scrutinize?"

The interpretation space work (Phase 4) touches on this — zone classification based on centrality and validation. But that's a post-hoc classification, not a real-time coherence driver.

**Action**: Implement *coherence-driven belief revision*. When a new paper's claims push coherence down (INV-4 monitors ≤-5% decline), don't just flag it — trigger an automatic review: (1) identify which old beliefs conflict with the new claim, (2) compute how much credence you'd have to drop in each to restore coherence, (3) ask: is the new claim stronger (higher warrant) than the old beliefs it conflicts with? If not, queue it for manual panel review. This turns coherence from a metric into a steering signal.

**Susan Haack (Miami, Epistemology)**:
I want to push back gently on all three. **The foundherentist challenge is deeper**: you're computing credence from warrants (warrant_strength.py), but warrants themselves need grounding. Your ω formula weights five factors (sample_size, replications, confound_control, measurement_quality, population_coverage), but each of those is itself a judgment call. Who decided that confound_control gets weight 0.15? Your panel did, via TEA scores, but under what methodology?

Foundherentism requires that your most basic beliefs — the ones that anchor the web — be *especially* well-justified. You have 4,888 findings in your Tier1 coherent network. How many of those 4,888 are *foundational*? How many are empirical claims that would survive direct scrutiny (primary sources, replicated, clear methodology)? My fear is that you've built a web where every belief supports every other belief but nothing touches ground.

**Action**: Implement a *provenance chain audit*. Pick 50 random high-credence beliefs (say, credence > 0.7). For each, trace its provenance back to the original study: Was it a direct quote from the paper? A summary of multiple papers? An inference from related claims? Did the extraction process validate the core causal claim, or infer it? Document the chain. If > 60% are direct quotes with clear causal statements, you're foundationally sound. If > 60% are inferred or synthesized, your edifice is built on inferences, not grounded claims.

**Roger Cooke (RFF, Structural Uncertainty)**:
Orthogonal concern: **Your scoring rules are undocumented**. You have AESHI (6 subscores), you have RUTHLESS audit (8 categories), you have individual finding credences, template quality, theory coverage. But how do these scores combine? How much does AESHI weight each subscore? Why is stability 54% instead of 30% or 70%? Where's the calibration study that validates these weightings against real-world expert consensus?

I've spent 40 years calibrating expert judgment. Your system is full of judgments (what d-values to assign, how much to penalize for measurement quality, whether scope_json absence is MAJOR or CRITICAL). But you have no systematic record of *how* those judgments were made, *who* made them, and *how often* they'd be made the same way by another competent expert.

**Action**: Create a *decision log with calibration metadata*. For every AESHI subscore formula, every RUTHLESS category, every warrant strength weight, record: (1) who decided it, (2) when, (3) what method (panel consensus, literature, prior work), (4) any dissent. Then run a *calibration study*: ask another panel of 5 experts (not on your original panels) to independently assign these same weights. Compute Kendall's τ with your original panel. If τ < 0.6, your scoring rule is unreliable. If τ > 0.8, you have a replicable system.

**Gregory Murphy (NYU, Cognitive Categories)**:
I want to surface something about your *concept structure*. You have 25 theories, 166 templates, and you're trying to assign each finding to exactly one template (or none). But in real cognitive categorization, concepts are *prototypical*, not binary. Your templates might be prototypes — "a good exemplar of the FLOW_THEORY template" — and some findings are *ambiguous* or *multi-faceted* (this finding relates to flow AND attention restoration). Your current system flags these as errors or assigns them to the "best match." But maybe they're *richer* if you allow soft membership.

Your Music I template mismatch (28 findings demoted from music templates) — was that the right move? Or did those findings *genuinely* apply to music and also to other domains, and you lost that information by demoting them?

**Action**: Audit your template assignments for *forced categorization*. Sample 100 findings that are assigned to exactly one template. For each, ask: "How well does this finding fit its assigned template (0-10)?" and "Does this finding fit ANY other template (yes/no)?" If > 20% are weak fits (0-5) OR fit multiple templates, your template system may be too rigid. Consider allowing soft membership or creating a "bridging" template category for cross-domain findings.

**James Woodward (Pittsburgh, Interventionism)**:
You all are focusing on knowledge *content*. I want to focus on *intervention feasibility*. Your system is built to answer: "What do we believe about environmental psychology?" But the real test is: "Can we *act* on this belief?" An architect reads your system and asks: "Should I make this room 12 feet tall instead of 10?" Your system says: "Yes, because moderate ceiling heights (9-11 ft) correlate with openness and reduce anxiety (credence 0.68)." But the architect needs: "If I make this room 12 feet instead of 10, and the population is East Asian women with claustrophobia history, what's the predicted effect on anxiety reduction?"

Your δ (population transfer) and epistemic_projection.py get part of the way there. But there's no *decision support layer* that takes a concrete intervention and translates it into a probability distribution over outcomes.

**Action**: Build a *decision support module*. Input: (1) a proposed intervention (e.g., "increase ceiling height from 10 to 12 feet"), (2) a target population (e.g., "East Asian women, anxiety disorder"), (3) an outcome of interest (e.g., "anxiety reduction"). Output: (1) which beliefs in your network are relevant, (2) what's the projected effect size (with credence interval), (3) what are the nearest analogues in your literature (interventions in similar contexts). This is a thin wrapper on top of your existing epistemic_projection, but it closes the loop between "belief" and "action."

**David Kirsh (UCSD, Cognitive Ecology)**:
You've all identified real gaps. Let me synthesize what I'm hearing: *ATLAS has excellent data, good architecture, but poor grounding*. The system is coherent internally but fragile externally. If one of your core assumptions (like d-value calibration) is wrong, the whole network propagates the error. And you have no feedback loop: you don't systematically learn when your recommendations fail in the real world.

Here's the single most impactful next step: **Close the feedback loop**. Implement a *deployment feedback mechanism*. Work with 2-3 architectural firms to deploy 50-100 recommendations from your system into real projects over 6 months. Document the outcomes: Did the intervention produce the predicted effect? Did users report satisfaction? Did it solve the design problem? Aggregate the data and feed it back into your system. This is hard but essential.

**Why this matters**: Your AESHI score is RED because stability is low. But you don't know *why* stability is low because you don't have data on real-world failures. You have coherence within your network, but no signal from the external world.

---

## PANEL DELIBERATION: Round 2

### Topic B: What is the most dangerous gap or risk?

**Nancy Cartwright**:
The most dangerous gap is **operationalization of constructs**. You have 25 theories, each with constructs (e.g., Goldilocks Principle has "optimal stimulation," "metabolic efficiency," "individual differences"). But how do you measure these in an actual environment? When an architect applies Goldilocks to a color palette, how do they know if the environment is "optimally stimulating" or not? Without operational definitions that connect theory to measurement, your coherence network is beautiful but non-actionable. It's like having a theory of ideal government but no way to assess whether a real government instantiates it.

**Haack's provenance audit (Action A4)** will help with grounding. But you also need **construct measurement specs**. For each of your 25 theories, you should have an operationalization document: "Here's what we mean by 'prospect-refuge balance': it manifests as [behavioral markers], [perceptual markers], [physiological markers]. You can measure it with [instrument 1], [instrument 2], [instrument 3]. The thresholds for 'low,' 'medium,' 'high' are [quantified values with references]."

**Action** (from Cartwright-2): Create operationalization specs for all 25 theories. You've already done 72 outcomes (OC-6 task). Do the same for constructs. Target: 2-week sprint. Pick the 5 highest-impact theories (flow, attention restoration, Goldilocks, PAD model, proxemics) and operationalize them fully. The rest can follow.

---

**Judea Pearl**:
The most dangerous gap is **undetected confounding**. Your system infers warrant strength from five factors, including "confound_control," but that's a binary or ternary judgment (controlled/partially/not controlled). You don't have a *confounding detection algorithm*. If a paper reports that "natural light predicts attention," but doesn't control for room size or window view quality, your system marks it as "partially controlled" and discounts the warrant. But what if there's a *hidden confounder* the paper never mentions?

In causal inference, we call this the "backdoor criterion" problem: there exists an unobserved path from cause to effect that bypasses your measured mediators. Your system has no way to detect backdoor paths.

**Action** (from Pearl-2): Implement a *confounder risk checklist* for each claim type. For mechanism claims (e.g., "lighting → attention"), list the known confounders from the literature: room size, personal stress, time of day, screen-based task load, and so on. For each claim, automatically extract from the paper: "Did the authors control for [confounder]?" If a major confounder is uncontrolled, reduce ω by 20%. This is a heuristic, not a proof, but it provides *transparency* about what you're assuming.

---

**Paul Thagard**:
The most dangerous gap is **belief clustering without revision pressure**. Your interpretation space (Phase 4) classifies beliefs into zones (Active Boundary, Identified Periphery, Uncertain Periphery). But what's the *update rule*? If a belief sits in "Uncertain Periphery" (low validation, high coherence), when does it get elevated to "Active Boundary" or downgraded to "rejected"? You have QA reflexes and validator gates that *prevent* bad findings from entering. But once in the network, what makes a belief *leave* the network?

Your coherence metric tracks *global* coherence but not *local revision pressure*. A belief can be high-coherence but low-grounded, and sit there indefinitely. In real science, such beliefs either (a) get additional support and migrate to core status, or (b) get scrutinized and revised/rejected. Your system doesn't have a *forced choice point*.

**Action** (from Thagard-2): Implement *automatic belief review scheduling*. Every belief in "Uncertain Periphery" zone gets queued for *mandatory manual review* every 90 days (or sooner if new evidence arrives). The review is a panel yes/no: "Should this belief stay in the network or be downgraded to 'contested' or 'rejected'?" Keep a decision log. This is a lightweight governance mechanism but it ensures beliefs don't sit in limbo.

---

**Susan Haack**:
The most dangerous gap is **scope-condition evaporation**. Your extraction process captures scope_json at extraction time (DK: "Showing examples that span the diversity of cases"). But you don't *persist* it to the database. Phase 4 analysis found 0% persistent scope_json in SQLite, despite 50+ beliefs having it at extraction time. This means your understanding of *when a belief applies* is lost. A finding about "attention restoration for attention-deficit populations" looks just like "attention restoration for general populations" once it enters your network. The scope conditioning is erased.

This is a *silent data loss*. Your system thinks it has fully justified 50+ beliefs, but it's actually missing the crucial contextual qualifiers that would prevent overgeneralization.

**Action** (from Haack-2): Implement *scope persistence*. (1) Modify the SQLite schema for beliefs to include `scope_conditions` (TEXT JSON, nullable). (2) Update extraction_to_web.py to persist scope_json from extraction to belief.scope_conditions. (3) Audit your current 4,888 beliefs: how many have scope inferred from their provenance but not explicitly captured? Create those scope records. (4) Update epistemic_projection.py to *condition* the population transfer factor (δ) on scope match. If a belief's scope is "attention-deficit populations" and you're trying to generalize to "general populations," δ drops. This is a 1-week sprint but *critical* for coherence integrity.

---

**Roger Cooke**:
The most dangerous gap is **uncertainty quantification failure**. You compute credence as a point estimate (e.g., 0.68) but provide no confidence interval. You compute ω with five weighted factors but don't propagate the uncertainty through each factor. If sample_size confidence is ±0.05 and measurement_quality confidence is ±0.03, what's the confidence on the final ω? You don't say. This is standard practice in risk analysis: every estimate comes with a confidence interval.

Your panels (TEA, warrant calibration, domain expert reviews) show disagreement. But you don't quantify it. When three panelists agree d(mechanism)=0.80 but one says 0.70, you average to 0.8 and move on. But the presence of disagreement means your calibration has *aleatoric uncertainty* (irreducible disagreement) that should be reflected in your confidence intervals.

**Action** (from Cooke-2): Implement *credence interval estimation*. For every credence value computed, compute (1) point estimate (as you do now), (2) lower 90% confidence bound, (3) upper 90% confidence bound. Methods: bootstrap from your panel disagreement data (if N panelists gave d-values d₁...dₙ, your uncertainty is ± std(d)); propagate factor-level uncertainty through warrant_strength.py via Monte Carlo sampling. For beliefs, quantile averaging (Cooke's method) is more robust than mean averaging. This adds computation but is standard in Bayesian practice.

---

**Gregory Murphy**:
The most dangerous gap is **prototype drift without vigilance**. Your templates are *prototypes* — exemplars of "what a good flow-theory finding looks like." But prototypes drift. In cognitive psychology, we know prototypes shift based on recent exposure: if you see many examples of flow with high challenge and low skill, your prototype *shifts* to emphasize challenge. Your system has 166 fixed templates, and uses them as ground truth for assigning new findings. But if your 1,069 papers are *biased* (e.g., emphasize outdoor environments, underrepresent interior design), your templates will drift toward that bias without you noticing.

**Action** (from Murphy-2): Implement *prototype stability monitoring*. Every 500 new papers, recompute your template prototypes using clustering (find the finding closest to the centroid of all findings assigned to that template). Compare the new centroid to the old centroid (compute Wasserstein distance in feature space). If distance > threshold, the template has drifted; flag it for panel review. This is a quarterly audit but it catches bias creep.

---

**James Woodward**:
The most dangerous gap is **intervention non-monotonicity invisibility**. Your system assumes interventions are *monotonic* — increasing a factor always pushes the outcome in the same direction. More natural light → better attention. More space → better openness. But real systems are nonmonotonic: too much natural light causes glare; too much space causes emptiness and disengagement. Your credence computation (warrant_strength.py) doesn't encode *functional form*. It treats "natural light increases attention" the same way as "natural light affects attention" regardless of whether the relationship is linear, inverted-U, or threshold-based.

If an architect uses your belief "natural light → attention" (credence 0.68) and installs full-wall windows in a bright location, they may create an effect opposite to the prediction.

**Action** (from Woodward-2): Implement *functional form coding*. In your extraction process, code not just the direction (increases/decreases/affects) but the *shape*: linear, inverted-U, threshold, sigmoidal, etc. Create a functional_form field in FindingV2. In epistemic_projection, apply *shape discounting*: beliefs with known functional forms get ω+0.05 (higher warrant) because they're more specific and testable. Beliefs with *unknown* form get ω-0.05. This incentivizes your extraction process to dig deeper.

---

**David Kirsh**:
Collecting these: the most dangerous gaps are (1) externally unvalidated coherence, (2) undetected confounding, (3) absent scope conditioning, (4) no confidence intervals, and (5) unknown functional forms. These are all *transparency* issues: your system computes credences but can't tell an architect *why* to trust them. It has uncertainty but doesn't quantify it. It has scope conditions but doesn't persist them. The system is *internally sound* but *externally blind*.

The highest-risk outcome: you deploy the system, architects make decisions based on credence 0.68 beliefs, real-world outcomes diverge from predictions, and the feedback undermines confidence in the entire enterprise.

---

## PANEL DELIBERATION: Round 3

### Topic C: What would you recommend for the next 4 hours of work?

**Nancy Cartwright**:
If you have 4 hours RIGHT NOW, do this: (1) Pick 5 highest-impact findings (highest credence, most-used templates). (2) For each, trace its provenance back to the original paper. (3) Document the chain: is it a direct quote from the paper, or an inference? (4) Read the original paper yourself and assess: does the paper's central claim match what you extracted? (5) Write a 1-page report for each. This will take 3-4 hours and will tell you immediately whether your extraction process is faithful or lossy. If you find inference chains that lost information, you've identified an extraction protocol gap.

---

**Judea Pearl**:
If you have 4 hours: (1) Review your 5 syntax-error scripts (load_tranche80_theory_links.py, persist_finding_annotations.py, etc.). (2) Fix them. (3) These are blocking your template relevance validation pipeline. Get the pipeline running. (4) Run it on a sample of 100 findings. The output will tell you which findings have *robust* template assignments (agreed across multiple validation methods) vs. weak assignments. This gives you a *confidence layer* on your template categorization, which Woodward and Murphy are concerned about.

---

**Paul Thagard**:
If you have 4 hours: Fix the **sanity_check gate failure** in compute_system_health.py line 123 (Pydantic deprecation warning). This is blocking your AESHI green score. It's a small fix (update Pydantic import or suppress the warning) but it unblocks your entire health monitoring system. Once that passes, AESHI will flip to YELLOW or GREEN, your stability score will recalibrate, and you'll have a clearer sense of what's actually broken vs. what's just an API warning.

---

**Susan Haack**:
If you have 4 hours: Implement **scope_conditions field persistence** (Haack-2 Action). It's a 1-week sprint but you can prototype it in 4 hours: (1) Create a migration to add `scope_conditions TEXT JSON` to the belief table. (2) Update extraction_to_web.py to read scope_json from temp_extraction and persist it. (3) Test on 5 findings that have non-empty scope_json. (4) Check the DB and verify scope was persisted. This is a high-leverage fix because it recovers a data loss that's already happened.

---

**Roger Cooke**:
If you have 4 hours: Create **warrant strength confidence intervals**. Take your 5 domain expert panels (from Sprint CREDENCE-WARRANT Phase 5) and, for each panelist's ω rating, compute the Bayesian posterior. If panel gave ω estimates (ω₁, ω₂, ω₃, ω₄, ω₅), fit a beta distribution and report (median, lower 10%, upper 90%). Do this for 20 representative beliefs. Document the process. This will show you whether your panelists' disagreement is within 0.05 or spreads to 0.2+. If the latter, your confidence intervals need to be wide and your credence claims need to be more hedged.

---

**Gregory Murphy**:
If you have 4 hours: Audit **template assignment quality** (Murphy-2 Action, partial). Sample 50 findings assigned to single templates. For each, ask: (1) "How well does this fit the template (0-10)?" and (2) "Could this fit multiple templates?" Document the results. If > 20% are weak fits, flag it for the next sprint. This is a *diagnostic pass*, not a fix, but it tells you whether your template system is working as intended.

---

**James Woodward**:
If you have 4 hours: **Audit functional forms**. Sample 100 findings from your extraction JSON. For each, does the extraction indicate *shape*? (linear increase, inverted-U, threshold, unknown?) Document what you find. If most are "unknown," this is a major protocol gap: your extraction process isn't capturing enough information. Write a 1-page protocol amendment specifying how future extractions should code functional form. This is a writing task, not a code task, but it sets up the next sprint.

---

**David Kirsh**:
If you have 4 hours: **Read your own system like a user would**. You have an ATLAS system, you have 4,888 beliefs in the coherent network. Pick a real architectural decision (e.g., "Should I add skylights to this office?") and *ask your system* what it thinks. What beliefs are relevant? What's the credence? What are the caveats? Try to construct a recommendation that an architect could actually use. You'll immediately see where the gaps are. If you can't produce a convincing recommendation in 4 hours, neither can your users. Document what you learned.

---

## PANEL DELIBERATION: Round 4

### Topic D: Synthesis and Ranking

The panel now synthesizes recommendations into a unified prioritized list. Note: the panel's primary goal is *not* to optimize for speed but for *epistemic soundness*. Faster fixes that mask deeper problems are actively discouraged.

**Panel Consensus (Unanimous)**: The ATLAS system is **architecturally sound but epistemically fragile**. It has good data, good structure, but poor grounding. The next phase of work should focus on **transparency, feedback, and scope**.

**Priority Tiers**:

1. **TIER 0 (TODAY — 4-hour tasks)**: Quick wins that unblock the system or reveal gaps.
2. **TIER 1 (THIS WEEK)**: High-leverage fixes that address structural weaknesses (scope persistence, sanity check gate, syntax errors).
3. **TIER 2 (THIS MONTH)**: Medium-effort improvements that increase robustness (confidence intervals, confounder audits, decision support).
4. **TIER 3 (NEXT QUARTER)**: Longer-term investments (deployment feedback, external validity calibration, prototype stability monitoring).

---

## 10 ACTIONABLE IMPROVEMENTS (Ranked by Impact × Feasibility)

### IMPROVEMENT 1: Fix Sanity Check Gate (P0 CRITICAL)

**Description**: Debug and resolve the Pydantic deprecation warning in `/scripts/compute_system_health.py` line 123 that is causing the AESHI sanity_check gate to fail. This is blocking the entire health monitoring system from reporting GREEN or YELLOW status.

**Expected Impact**: HIGH
- Unblocks AESHI recalibration from RED (49/100) to at least YELLOW (55-70/100)
- Enables accurate stability subscore assessment (currently 54.17%, likely artificially low)
- Allows production readiness assessment

**Estimated Effort**: 2-4 hours
**Methodology**: (1) Examine the Pydantic import at line 123. (2) Check installed Pydantic version (likely > 2.0, which has breaking API changes). (3) Update import to use new API or suppress deprecation warning. (4) Rerun health check. (5) Verify gate now passes.

**Championed by**: Paul Thagard
**Dependencies**: None

**Success Condition**: `compute_system_health()` runs to completion and sanity_check gate returns PASS (True). AESHI score recalculates and reflects true system health.

---

### IMPROVEMENT 2: Implement Scope Conditions Persistence (P0 CRITICAL)

**Description**: Recover the scope_json data loss by implementing persistent storage of scope conditions in the belief database. Currently, scope_conditions exist in memory during extraction but are NOT persisted to SQLite. This causes overgeneralization of beliefs because their applicability context is lost.

**Expected Impact**: HIGH
- Fixes silent data loss in 50+ beliefs that have scope context
- Prevents erroneous overgeneralization (e.g., "attention restoration for anxiety-disorder populations" applied to "general populations")
- Enables δ (population transfer factor) to be conditioned on scope, improving epistemic_projection accuracy
- Addresses Susan Haack's critical gap (Haack-2)

**Estimated Effort**: 1 week (1 sprint)
- Migration design: 4-6 hours
- extraction_to_web.py modification: 4-6 hours
- epistemic_projection.py conditioning: 6-8 hours
- Testing and validation: 4-6 hours

**Methodology**:
1. Create database migration: add `scope_conditions TEXT JSON DEFAULT NULL` to beliefs table
2. Modify `extraction_to_web.py` to read scope_json from temp_extraction and persist to belief.scope_conditions
3. Update `epistemic_projection.py` to check if belief scope matches target population; apply δ discount if mismatch
4. Audit existing 4,888 beliefs to infer scope from provenance metadata (e.g., study population, inclusion criteria)
5. Test on 20 representative beliefs with explicit scope

**Championed by**: Susan Haack
**Dependencies**: Extraction infrastructure (extraction_to_web.py must have scope_json available)

**Success Condition**: 100% of newly integrated findings have scope_conditions persisted. δ projection factor reflects scope match/mismatch. Existing beliefs audited and scope inferred where possible.

---

### IMPROVEMENT 3: Create Construct Operationalization Specifications (P1 HIGH)

**Description**: For each of the 25 theories in ATLAS, create an operationalization document specifying how its core constructs are measured, with behavioral, perceptual, and physiological markers, validated instruments, and quantified thresholds.

**Expected Impact**: HIGH
- Converts abstract theories into actionable measurement criteria for architects
- Enables external validity validation (Cartwright-1 Action)
- Provides operational ground truth for belief evaluation
- Directly supports decision support module (Woodward Action)

**Estimated Effort**: 3 weeks (2 sprints)
- Fast-track: Pick 5 high-impact theories (flow, attention restoration, Goldilocks, PAD model, proxemics) for Week 1 (1 week)
- Remaining 20 theories for Week 2-3 (2 weeks)

**Methodology**:
1. For each theory, identify core constructs (e.g., Goldilocks: optimal stimulation, metabolic efficiency, individual differences)
2. Literature review: find published operationalizations, instruments, thresholds
3. Create specification document (2-4 pages per theory): constructs → behavioral markers → instruments → quantified thresholds
4. Link to outcome_vocab (you already have 72 outcomes + 95 instruments from OC tasks)
5. Cross-validate: for each construct, identify at least 2 validated instruments

**Championed by**: Nancy Cartwright
**Dependencies**: Outcome vocabulary (OC-6) and instruments registry (INSTR-REG) already complete; leverage existing work

**Success Condition**: 5 theories fully operationalized by Week 1 (high-impact fast track). All 25 theories operational by Week 3. Each specification linked to 2+ validated instruments.

---

### IMPROVEMENT 4: Implement Confounder Risk Checklist (P1 HIGH)

**Description**: Create a claim-type-specific confounder checklist. For mechanism claims, empirical claims, and theory-derived claims, identify the known confounders from literature. During extraction or belief integration, automatically detect whether papers controlled for major confounders. Reduce warrant strength (ω) for uncontrolled confounders.

**Expected Impact**: MEDIUM
- Increases ω validity by penalizing uncontrolled confounding
- Provides transparency about causal assumptions
- Reduces risk of Pearl's backdoor criterion violations
- Addresses Judea Pearl's critical gap (Pearl-2)

**Estimated Effort**: 2 weeks (1 sprint)
- Confounder taxonomy: 3-4 days
- Extraction/belief integration logic: 4-5 days
- Testing on 100 claims: 2-3 days

**Methodology**:
1. Build confounder database: for each claim type, list 5-10 major confounders (e.g., "natural light → attention" confounders: room size, window view, time of day, screen task load, personal stress)
2. Create heuristic rules: "If confound [X] not controlled, reduce ω by Y"
3. Integrate into warrant_strength.py: after computing base ω, check for uncontrolled confounders and apply discounts
4. Implement in extraction_to_web.py or as a post-hoc QA reflex
5. Test on 100 random beliefs: manually verify confounder detection accuracy

**Championed by**: Judea Pearl
**Dependencies**: Extraction schema must include "confound_control" field (already present in ExtractionFieldValidator)

**Success Condition**: 80%+ of major confounders for claim type [X] are detected in papers. ω distributions show lower credence for uncontrolled vs. controlled claims of same type.

---

### IMPROVEMENT 5: Implement Credence Confidence Intervals (P1 HIGH)

**Description**: For every credence value (point estimate), compute lower and upper 90% confidence bounds using Bayesian posterior estimation from panelist disagreement data and factor-level uncertainty propagation.

**Expected Impact**: MEDIUM
- Addresses Roger Cooke's critical gap (Cooke-2)
- Quantifies epistemic uncertainty in a way architects can understand
- Enables decision-making under uncertainty
- Prevents false confidence in estimates

**Estimated Effort**: 2 weeks (1 sprint)
- Bootstrap methods from panel data: 3-4 days
- Monte Carlo uncertainty propagation in warrant_strength.py: 3-4 days
- Implementation in credence computation: 2-3 days
- Testing and validation: 2-3 days

**Methodology**:
1. From your 3 domain expert panels (Phase 5), extract individual panelist ω estimates
2. Fit beta distributions to each panelist group's estimates
3. Compute quantile averaging (Cooke's method) to get posterior
4. For credence computation: propagate factor uncertainty through warrant_strength.py using Monte Carlo (N=1000 samples)
5. Report credence as: median ± lower90 / upper90 (e.g., "0.68 [0.62–0.75]")

**Championed by**: Roger Cooke
**Dependencies**: Panel data from Sprint CREDENCE-WARRANT Phase 5 (already have 9 panelists × 41 beliefs)

**Success Condition**: All 4,888 beliefs in coherent network have credence intervals. Width of intervals correlates with panel disagreement (higher disagreement → wider intervals). Documentation explains interval interpretation.

---

### IMPROVEMENT 6: Provenance Chain Audit (P1 MEDIUM)

**Description**: Audit 50 random high-credence beliefs (credence > 0.7) by tracing their provenance back to original source papers. Classify each as: direct quote, summary of multiple papers, or inference from related claims. Document the chain and assess whether the system is "foundationally grounded" (> 60% direct quotes) or "inference-stacked" (> 60% inferred).

**Expected Impact**: MEDIUM
- Addresses Susan Haack's foundational grounding concern (Haack-1 Action)
- Identifies whether coherence is built on ground-level facts or high-order inferences
- Reveals extraction protocol weaknesses (if inferences are frequent, extraction process needs improvement)

**Estimated Effort**: 1 week (1 sprint)
- Sample selection and provenance tracing: 3-4 days
- Original paper review and classification: 2-3 days
- Report and gap analysis: 1-2 days

**Methodology**:
1. Sample 50 beliefs uniformly from credence range 0.7–1.0
2. For each, trace its source in the beliefs table and extraction JSON
3. Classify: (A) direct quote from paper, (B) summary of paper's main finding, (C) inference from multiple papers, (D) inference from other beliefs
4. For each classification, note: was extraction process faithful? Did summarization lose nuance?
5. Aggregate: compute % in each category
6. Report: if > 60% in (A) or (B), system is well-grounded. If > 60% in (C) or (D), system is inference-stacked and needs stronger extraction.

**Championed by**: Susan Haack
**Dependencies**: None (requires manual review)

**Success Condition**: Report identifies grounding profile. If inference-stacked, identifies specific extraction protocol weaknesses to address in next sprint.

---

### IMPROVEMENT 7: Build Decision Support Module (P2 MEDIUM)

**Description**: Create a user-facing module that translates abstract beliefs into concrete architectural recommendations. Input: (1) proposed intervention (e.g., "increase ceiling height from 10 to 12 feet"), (2) target population, (3) outcome of interest. Output: (1) relevant beliefs, (2) projected effect size with credence interval, (3) nearest analogues in literature.

**Expected Impact**: MEDIUM
- Directly addresses James Woodward's gap (Woodward Action)
- Makes the system usable by practitioners (architects, designers)
- Closes feedback loop: decisions based on beliefs can be tracked
- First step toward deployment feedback mechanism (David Kirsh's #1 recommendation)

**Estimated Effort**: 3 weeks (2 sprints)
- Intervention parser and matcher: 4-5 days
- Belief relevance searcher: 3-4 days
- Effect size projector (wrapper on epistemic_projection): 3-4 days
- Web UI or CLI: 3-4 days
- Testing and validation: 3-4 days

**Methodology**:
1. Design intervention ontology: (intervention type, manipulation direction, magnitude, target variable)
2. Build belief matcher: given intervention, find beliefs about that relationship
3. Implement effect size projector: given matched beliefs and target population, use epistemic_projection to compute predicted p(outcome)
4. Retrieve analogues: find empirical papers in extraction corpus with similar interventions
5. Format output: plain-English recommendation with caveats (scope conditions, confounders, effect size uncertainty)
6. Optional: add feedback collection (architect reports whether recommendation was used and outcome)

**Championed by**: James Woodward
**Dependencies**: epistemic_projection.py must be production-ready; scope persistence (Improvement 2) recommended first

**Success Condition**: Module can process 10 realistic interventions and produce recommendations that practitioners find actionable. Effect size projections correlate with empirical outcomes when tested on 20 known cases.

---

### IMPROVEMENT 8: Functional Form Coding Protocol (P2 MEDIUM)

**Description**: Expand the extraction protocol to capture not just *direction* of relationships (increases/decreases/affects) but also *functional form*: linear, inverted-U, threshold, sigmoidal, unknown. Add functional_form field to FindingV2 schema. Implement form discounting in warrant_strength.py: known forms receive ω+0.05, unknown forms receive ω-0.05.

**Expected Impact**: MEDIUM
- Addresses James Woodward's functional form gap (Woodward-2)
- Prevents erroneous monotonic extrapolation (e.g., "more light → better attention" leading to glare problems)
- Increases specificity of beliefs (known forms are more testable)
- Provides feedback signal: more specific extraction protocols get higher credence

**Estimated Effort**: 2 weeks (1 sprint)
- Extraction protocol documentation: 2-3 days
- Schema modification (FindingV2): 1-2 days
- Extraction model prompt update (for LLM-based extraction): 1-2 days
- warrant_strength.py modification: 2-3 days
- Retraining/revalidation on sample: 3-4 days

**Methodology**:
1. Create functional form taxonomy: linear, inverted-U, threshold, sigmoidal, bilinear, other
2. Add functional_form field to FindingV2 (string, enum)
3. Update extraction prompts to require classification of functional form (with confidence)
4. Implement form-based ω adjustment in warrant_strength.py
5. Reprocess 100 random findings with new extraction protocol
6. Validate: do known-form findings match empirical functional forms better than unknown-form findings?

**Championed by**: James Woodward
**Dependencies**: Extraction protocol and extraction model prompts

**Success Condition**: 80%+ of new findings include explicit functional form coding. ω distributions show meaningful separation between known and unknown forms. Reprocessed findings show improved empirical alignment.

---

### IMPROVEMENT 9: Template Stability and Prototype Drift Monitoring (P2 MEDIUM)

**Description**: Implement quarterly monitoring of template prototype drift. Every 500 new findings, recompute template centroids using clustering. Compare new centroid to old centroid using Wasserstein distance. Flag templates with significant drift (distance > threshold) for panel review to assess whether drift reflects true data evolution or input bias.

**Expected Impact**: MEDIUM
- Addresses Gregory Murphy's prototype drift concern (Murphy-2)
- Detects when template definitions shift due to input bias
- Prevents gradual convergence on unrepresentative prototypes
- Provides governance signal for when templates need revision

**Estimated Effort**: 2 weeks (1 sprint)
- Prototype representation and distance metric: 2-3 days
- Quarterly monitoring script: 2-3 days
- Drift detection and flagging logic: 2-3 days
- Panel review protocol: 1-2 days
- Testing and baseline computation: 2-3 days

**Methodology**:
1. For each template, compute centroid of all findings currently assigned to it (use finding-level feature vectors: warrant types, theory connections, outcome types)
2. Store centroid as baseline
3. Every 500 new findings, recompute centroid
4. Compute Wasserstein distance between old and new centroid
5. If distance > threshold (e.g., 0.15), flag template as "drifted"
6. Panel reviews drifted templates: is drift legitimate (new understanding) or problematic (input bias)?

**Championed by**: Gregory Murphy
**Dependencies**: Finding feature vectorization must be standardized; clustering library (scipy.spatial.distance.wasserstein_distance)

**Success Condition**: Quarterly monitoring runs without error. Detects 2-3 known drift scenarios. Panel can assess whether drift is desirable or problematic.

---

### IMPROVEMENT 10: Deployment Feedback Mechanism (P3 LONG-TERM)

**Description**: Establish partnerships with 2-3 architectural firms to deploy 50-100 ATLAS recommendations into real projects over 6 months. Document outcomes: Did the intervention produce the predicted effect? Did users report satisfaction? Aggregate results and feed back into ATLAS to calibrate credence estimates and identify systematic errors.

**Expected Impact**: HIGH (Long-term)
- Closes the feedback loop between beliefs and real-world outcomes
- Provides ground truth for external validity validation (Cartwright-1 Action)
- Identifies systematic biases in credence estimation
- Enables credence recalibration based on empirical outcomes
- Addresses David Kirsh's primary recommendation: "Close the feedback loop"

**Estimated Effort**: 6 months (ongoing)
- Partner identification and negotiation: 2-4 weeks
- Protocol design and IRB/ethics review: 4-6 weeks
- Deployment and outcome tracking: 16-20 weeks
- Analysis and credence recalibration: 4-6 weeks

**Methodology**:
1. Identify 2-3 architectural firms willing to deploy recommendations on real projects
2. Create deployment protocol: (1) architect selects a design decision, (2) ATLAS recommends a belief-backed intervention, (3) architect implements, (4) outcomes tracked (user surveys, environmental measurements, business metrics)
3. Standardize outcome measurement (e.g., occupant satisfaction via validated questionnaire; energy use via building automation; productivity via work samples)
4. For each deployed recommendation, track: (1) predicted vs. actual outcome, (2) effect size, (3) conditions under which prediction was accurate/inaccurate
5. Aggregate at end of 6 months: compute correlation between ATLAS-predicted and actual effects
6. Identify systematic errors: are certain belief types more error-prone? Certain populations? Certain contexts?
7. Recalibrate credence estimates based on empirical outcomes

**Championed by**: David Kirsh, Nancy Cartwright
**Dependencies**: Decision support module (Improvement 7) should be deployed first to generate usable recommendations

**Success Condition**: 50+ deployed recommendations tracked. Empirical outcome data analyzed. Credence recalibration protocol designed and first batch of recommendations updated based on real-world feedback. Correlation between predicted and actual effects computed (target: r > 0.6).

---

## SUMMARY TABLE: 10 RANKED IMPROVEMENTS

| Rank | Improvement | Impact | Effort | Timeline | Championed By | Blocker? |
|------|-------------|--------|--------|----------|---------------|----------|
| 1 | Fix Sanity Check Gate | HIGH | 2-4 hrs | TODAY | Thagard | CRITICAL |
| 2 | Scope Persistence | HIGH | 1 week | THIS WEEK | Haack | CRITICAL |
| 3 | Operationalization Specs | HIGH | 3 weeks | THIS MONTH | Cartwright | HIGH |
| 4 | Confounder Risk Checklist | MEDIUM | 2 weeks | THIS MONTH | Pearl | MEDIUM |
| 5 | Credence Confidence Intervals | MEDIUM | 2 weeks | THIS MONTH | Cooke | MEDIUM |
| 6 | Provenance Chain Audit | MEDIUM | 1 week | THIS WEEK | Haack | DIAGNOSTIC |
| 7 | Decision Support Module | MEDIUM | 3 weeks | NEXT MONTH | Woodward | MEDIUM |
| 8 | Functional Form Coding | MEDIUM | 2 weeks | NEXT MONTH | Woodward | MEDIUM |
| 9 | Template Drift Monitoring | MEDIUM | 2 weeks | NEXT MONTH | Murphy | LOW |
| 10 | Deployment Feedback | HIGH | 6 months | Q2-Q3 2026 | Kirsh, Cartwright | LONG-TERM |

---

## IMPLEMENTATION ROADMAP

### Phase 1: IMMEDIATE (This Week)
1. **Today**: Fix sanity check gate (Improvement 1)
2. **Today**: Complete 4-hour user-scenario testing (David Kirsh task)
3. **Days 2-3**: Complete provenance chain audit on 50 beliefs (Improvement 6)
4. **Days 3-5**: Implement scope persistence (Improvement 2)
5. **Days 5-7**: Fix 5 syntax errors in template relevance scripts (Improvement 3, supporting task)

**Success Metric**: Sanity check passes, scope_json persisted to 100+ beliefs, provenance audit complete, 5 scripts running.

---

### Phase 2: SHORT-TERM (Weeks 2-4)
1. **Week 2**: Create fast-track operationalization specs for 5 high-impact theories (Improvement 3)
2. **Week 3**: Implement confounder risk checklist (Improvement 4)
3. **Week 3-4**: Implement credence confidence intervals (Improvement 5)
4. **Week 4**: Validate all confidence intervals against panel disagreement data

**Success Metric**: 5 theories fully operationalized, confounder detection on 100 claims validated, credence intervals computed for all 4,888 beliefs.

---

### Phase 3: MEDIUM-TERM (Weeks 5-8)
1. **Week 5-6**: Complete operationalization specs for remaining 20 theories (Improvement 3)
2. **Week 6-7**: Build decision support module (Improvement 7)
3. **Week 7-8**: Implement functional form coding protocol (Improvement 8)

**Success Metric**: All 25 theories operationalized, decision support module handles 10 test interventions, functional form field in 100+ findings.

---

### Phase 4: GOVERNANCE (Weeks 9+)
1. **Ongoing (quarterly)**: Implement template drift monitoring (Improvement 9)
2. **6-month initiative**: Establish deployment feedback partnerships and track outcomes (Improvement 10)

**Success Metric**: Quarterly drift checks run without error, deployment feedback protocol active, 50+ recommendations tracked.

---

## CRITICAL SUCCESS FACTORS

1. **Fix Sanity Check Gate First**: Without this, you can't assess your system's true health. Everything depends on having accurate AESHI scores.

2. **Implement Scope Persistence ASAP**: This recovers lost data that's already in your system but not accessible. It's leverage.

3. **Close the Feedback Loop (Long-term)**: The panel's #1 concern is that you have no signal from the external world. Until you deploy and measure outcomes, you're flying blind. Start identifying architectural partners NOW, even if full deployment is 6 months out.

4. **Document Everything**: Your system is complex. Every decision (why d(mechanism)=0.80, why ω uses five factors, why δ is population-transfer), every assumption, every panel disagreement should be recorded. This is how you build trust.

5. **Bias Vigilance**: Your 1,069 papers are not random. They likely overrepresent certain environments (maybe outdoor > indoor, maybe Western > non-Western, maybe high-SES populations). Monitor for this constantly. Use Murphy's prototype drift detector.

---

## FINAL PANEL VERDICT

**Overall Assessment**: ATLAS is **ready for cautious deployment with intensive monitoring**. The system is epistemically sound (architecture is good, pipelines are wired, formulas are correct). But it is **fragile** in four ways:

1. **Externally unvalidated**: No feedback loop. You don't know if real architects using your system make better decisions.
2. **Scope-blind**: Conditional qualifications (scope_json) are lost, causing overgeneralization.
3. **Uncertainty-silent**: Credence estimates have no confidence intervals, masking disagreement.
4. **Non-monotonic-unaware**: Beliefs don't capture functional form, risking erroneous monotonic extrapolation.

**Recommendation**: Do Improvements 1-6 (Immediate and Short-term phases) BEFORE any public deployment. Improvements 7-10 are valuable but can happen in parallel with deployment. The deployment feedback (Improvement 10) is THE most important long-term initiative — without it, you'll never know whether your system actually works.

**Confidence in Roadmap**: The panel has 95% confidence that implementing Improvements 1-6 will increase ATLAS's epistemic soundness from "good" to "excellent," and enable confident deployment to beta-user architects.

**Timeline**: If you execute Phases 1-2 aggressively (4-week sprint), you can deploy to 2-3 beta partner firms by late March 2026, with full deployment feedback protocol in place by September 2026.

---

**Panel Signed**: Nancy Cartwright, Judea Pearl, Paul Thagard, Susan Haack, Roger Cooke, Gregory Murphy, James Woodward, David Kirsh
**Date**: 2026-03-02
**Next Review**: 2026-04-01 (post-Phase 2 implementation)
