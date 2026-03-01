# ATLAS System Health Panel Review
## Expert Deliberation on Ceiling Violations, Orphaned Beliefs, and Epistemic Quality

**Date**: February 26, 2026
**System**: Article Eater (PostQuinean ATLAS v22.0.0)
**Review Type**: Health Assessment & Remediation Strategy
**Status**: COMPLETE — Consensus Recommendations

---

## Executive Summary: ATLAS Health Status

| Metric | Value | Status |
|--------|-------|--------|
| **AESHI Score** | 49/100 | RED (Critical) |
| **Theory Quality** | 85.46/100 | STRONG |
| **Bayesian Network Health** | 72/100 | HEALTHY |
| **Belief Web Coverage** | 49.6% orphaned | CRITICAL GAP |
| **Ceiling Violations** | 69 across 25 templates | ALL ACCEPTED (100%) |
| **Web Invariants** | 6/6 PASS | SOUND |
| **Unresolved Templates** | 62 (42 zero-ref, 20 unclassified) | ACTIONABLE |

**Critical Finding**: System has strong theoretical foundations (BN + Invariants), but severe structural disconnectedness in the belief web. The universal ceiling acceptance suggests either miscalibrated ceilings or undersized override criteria.

---

## Panel Composition

| # | Expert | Primary Expertise | Key Contributions |
|---|--------|-------------------|-------------------|
| 1 | **Nancy Cartwright** | Philosophy of science, nomological machines, bridge warrants | External validity, mechanism transfer |
| 2 | **Judea Pearl** | Causal inference, DAGs, do-calculus, identifiability | Causal structure integrity, counterfactuals |
| 3 | **Paul Thagard** | Coherence theory, explanatory coherence, cognitive science | Coherence metrics, template alignment |
| 4 | **Susan Haack** | Foundherentism, evidence theory, warrant grounding | Foundational evidence, orphan remediation |
| 5 | **Roger Cooke** | Expert elicitation, structured judgment, calibration | Expert calibration, ceiling rationale |
| 6 | **Kevin Murphy** | Probabilistic graphical models, Bayesian inference | Network structure, inference soundness |
| 7 | **James Woodward** | Interventionist causation, invariance, stability | Mechanism robustness, policy relevance |

---

## Panel Questions Under Review

### **Question A**: Ceiling Miscalibration vs. Lenient Override Criteria?

*The adjudicator accepted 100% of 69 ceiling violations. Are ceilings too low, or are override criteria too permissive?*

### **Question B**: Automatic Edge Creation Risk Assessment

*49.6% orphaned beliefs with 1,731 keyword-bridge edges available. Should these be added, or does automation risk diluting epistemic warrant?*

### **Question C**: Zero-Reference Template Downgrade

*42 templates have zero references; 20 are unclassified. Should zero-ref templates be downgraded to THEORETICAL_DEFAULT status?*

### **Question D**: Single Most Impactful Action

*What is the highest-ROI intervention to move AESHI from RED (49) to AMBER (60)?*

---

## ROUND 1: Initial Assessments

### Nancy Cartwright (Nomological Machines & Bridge Warrants)

The 100% ceiling acceptance rate troubles me deeply. My framework insists that **nomological machines** — stable, context-dependent causal structures — cannot be "overridden away." If a ceiling violation is accepted, it means either:

1. **The ceiling misunderstood the mechanism** (it was set without proper mechanistic grounding), or
2. **The override evidence contains mechanistic detail that the ceiling lacked** (legitimate respecification)

The question "Are ceilings too low?" assumes ceilings are objective bounds. They're not — they're *epistemic commitments about what a template can warrant given available evidence*. A 100% acceptance rate suggests the ceiling-setters didn't sufficiently ground their thresholds in **mechanism specifications**.

**My preliminary view on Question A**: The high acceptance rate points to **ceilings that were set without sufficient mechanistic grounding**, not necessarily to being "too low" numerically. We need to audit the ceiling-setting process itself.

For Question B (orphaned beliefs): **Absolutely do not add those 1,731 edges automatically**. Each edge in a belief network carries implicit **warrant aboutness** — it claims one belief mechanistically depends on another. Keyword-matching cannot establish that. If half your beliefs are orphaned, the problem is not in the graph; it's in your templates themselves. They lack clear *mechanism specifications* for their dependencies.

For Question C (zero-reference templates): **Downgrade them, but with semantics preserved**. A template with no empirical references may still capture stable causal structure. Mark them as **THEORETICAL_SCAFFOLDING** (not THEORETICAL_DEFAULT), signaling that they define causal structure but lack empirical warrant until grounded in observations.

**Starting position on Question D**: Your most impactful single action is **mechanistic template audit**, not edge-adding. Each of the 42 zero-reference templates needs a mechanism specification. That work addresses all four questions at once.

---

### Judea Pearl (Causal Inference & DAGs)

I want to separate **structural soundness** from **semantic completeness**.

Your Bayesian network is structurally sound: 6,340 nodes, 11,925 edges, acyclic, fully connected, no unresolved identifiability issues. That's excellent. From a **causal graph perspective**, your network has integrity.

But structural soundness ≠ semantic correctness. Your network is *syntactically* sound but may have *semantically* incorrect edges. That's what the orphaned beliefs likely indicate.

On **Question A**: I interpret the 100% ceiling acceptance as evidence that your ceilings are too **coarse-grained**. You're probably not distinguishing between:
- **Structural ceilings** (what edges can exist)
- **Quantitative ceilings** (what probabilities those edges imply)

A belief may legitimately exceed a *probability ceiling* when fresh evidence arrives (that's just Bayesian updating). But structural changes (adding/removing causal relations) should *not* be exceptions — they should be principled revisions of your DAG. The fact that they're being treated as "overrides" suggests confusion between static structure and dynamic probability.

On **Question B** (1,731 keyword edges): Don't add them. Here's why: In a Bayesian network, edges encode **modeled independence assumptions** (d-separation). An edge between two variables claims they're *dependent conditional on the model structure*. Keyword-matching has no epistemological status to justify that claim. You'd be **contaminating your independence assumptions** with heuristics.

Instead: Use that list as a **diagnostic** (What beliefs are missing mechanistic links?) rather than as a **fix** (add them all). For each of those 1,731 pairs, ask: "Are these variables truly causally related, or are they correlated through a confounding mechanism we haven't modeled?"

On **Question C**: Zero-reference templates are not ipso facto problematic. I work with DAGs all the time that have theoretically-motivated edges with no direct observational grounding. **Downgrade them only if their edges appear in your causal identifiability analysis**. If they're not part of your inference pipeline, their reference status is less critical.

**Question D**: The single best action is **causal structure audit**. For your 1,731 candidate edges, determine which represent genuine causal mechanisms (keep them), which represent confounding (add confounder nodes), and which are spurious correlations (drop them). That will shrink your orphan count more efficiently than automatic edge addition.

---

### Paul Thagard (Explanatory Coherence & ECHO)

I'm looking at this through the lens of **explanatory coherence** — how well beliefs explain observations and cohere with one another.

The 49.6% orphan figure is the critical metric. In my ECHO model, **unconnected beliefs are inactive** — they don't participate in the coherence computation. You have half your system that's *inert*.

On **Question A** (ceilings): From a coherence perspective, a ceiling is reasonable if it bounds the *explanatory power* of a template. But 100% acceptance means your ceilings aren't discriminating. The ceiling framework is failing. However, I'd hesitate to call them "too low" — more likely, **the ceiling criteria aren't measuring what you think they're measuring**. You're not capturing the actual explanatory load that each template bears.

On **Question B** (automatic edges): This is where coherence theory becomes crucial. In ECHO, we compute coherence by:
1. Establishing explanatory relations (A explains B)
2. Competing relations (A contradicts C)
3. Coherence weights (how much does relation matter?)

Adding 1,731 edges *without establishing what they explain* will corrupt your coherence landscape. **Each edge must carry an explanatory rationale**. Keyword-matching is not an explanation.

However — and this is important — **your high orphan rate suggests your explanatory structure is incomplete**. The solution is not to add edges mechanically, but to ask: **What beliefs should be explaining these orphans?**

On **Question C** (zero-reference templates): In coherence terms, these are *potential explanans* (potential explanations) with no actual explanandum (what they explain). **Demote them to a "hypothetical" status** — they're explanatory *candidates* pending empirical grounding. Don't delete them; they may activate once you ground more templates empirically.

On **Question D**: The highest-leverage action is **increasing your component connectivity**. You claim 99.8% of BN nodes are in one connected component, but only 50% of beliefs. That mismatch is your problem. **Map belief-to-BN-node relations explicitly**. If a belief isn't connected to the causal structure, it's not contributing to inference. Connect orphans to either:
1. **Explanatory pathways** (this belief helps explain that observation), or
2. **Causal structures** (this belief instantiates that causal mechanism)

Do this for your top-50 highest-confidence orphans. That focused work will drive higher AESHI improvement than blanket edge addition.

---

### Susan Haack (Foundherentism & Evidence)

I come to this as someone skeptical of pure coherentism *and* pure foundationalism. **Foundherentism** insists that some beliefs must have foundational support, while coherence amplifies that support.

The 49.6% orphan rate is, frankly, damning. These are beliefs floating without either foundational support or coherence backing. That violates fundamental warrant principles.

On **Question A**: Ceilings are a form of **defeasible justification threshold**. A 100% acceptance rate means your thresholds are divorced from evidence. But here's the key question: **Were the ceiling overrides accompanied by new foundational evidence?** If an override was justified by "deeper mechanistic understanding," that's fine — that's foundational support. If overrides were just "the model produced results we liked," that's warrant corruption.

I'd want to see: For each of those 69 overrides, what was the *warrant source*? **Anchored in observation, expert judgment, or inference coherence?**

On **Question B** (automatic edges): Absolutely no. This is **warrant laundering**. You'd be claiming epistemic warrant for a structural decision (adding edges) that comes from pattern-matching, not from evidence. Haack's foundherentism requires that your graph structure be grounded in *something* — mechanistic theory, observational evidence, or careful expert judgment. Not automation.

On **Question C** (zero-reference templates): **These must be downgraded.** In foundherentist terms, they lack foundational support. However, **downgrade doesn't mean delete**. Mark them as **CONJECTURAL** — admissible in inference, but flagged as warrant-thin. They can regain status when referenced empirically.

On **Question D**: Two actions are equally impactful:

1. **Foundational audit**: For your 42 zero-reference templates, which could acquire foundational support through explicit observational connection? Prioritize those.

2. **Override analysis**: Audit all 69 ceiling overrides and classify by warrant source. How many were grounded in new evidence vs. model accommodation?

If the overrides were mostly evidence-grounded, your ceiling thresholds were too rigid. **Reset them**. If they were mostly accommodation-driven, your override criteria are too lenient. **Tighten them**.

The higher of these two numbers determines your intervention direction.

---

### Roger Cooke (Expert Elicitation & Calibration)

I'm a calibration expert, and this panel has fundamental **calibration failure** written all over it.

The 100% ceiling acceptance rate is not a feature of your system — it's a failure mode of your elicitation process. Let me explain:

When expert panels (or your ceiling-setters) generate thresholds and those thresholds are overridden 100% of the time, you have one of three problems:

1. **Experts were not calibrated** — They set thresholds without feedback on accuracy
2. **Experts misunderstood the task** — Ceiling thresholds mean different things to different judges
3. **Experts set thresholds to be conservative, not realistic** — They used a safety margin instead of a point estimate

In my structured expert judgment framework, **calibration requires feedback loops**. If you set a ceiling and it's violated, *that's evidence about the expert's mental model*.

On **Question A**: Don't ask "Are ceilings too low?" Ask instead: **"How were ceilings elicited, and from whom?"** If human experts set them, run a **calibration analysis**:
- Did the experts who set ceilings for Template X predict correctly over time?
- Do Template X violations correlate with systematic overestimation or underestimation?

100% acceptance might indicate that your ceiling-setters were appropriately cautious, but lacked **resolve** — the willingness to defend their thresholds. Or it might indicate they were never trained to think in threshold terms.

On **Question B** (automatic edges): Keyword-matching has *zero calibration history*. You don't know if it's accurate, overconfident, or underconfident. Don't deploy uncalibrated methods at scale. If you must add edges automatically, **first validate the heuristic on a held-out set**. What's the false-positive rate?

On **Question C** (zero-reference templates): Zero references could mean:
- Templates are purely theoretical (OK, if calibration is set appropriately)
- Templates are unmeasured (problem — no data to calibrate against)
- Templates are untested (problem — no feedback)

**Downgrade only if they're unmeasured**. Pure theory with no calibration data is acceptable if you mark it as THEORETICAL_WEIGHT (reduced in confidence but not eliminated). Once you have reference data, re-calibrate.

On **Question D**: **Calibration audit first, structural changes second.** Spend 2 weeks analyzing your ceiling-elicitation process:
- Interview your ceiling-setters
- Examine their track record
- Measure calibration curves (forecast vs. actual)
- Identify systematic biases

That investment will tell you whether you need new ceilings (2-hour fix) or structural redesign (weeks). Don't guess.

---

### Kevin Murphy (Probabilistic Graphical Models)

From a graphical models perspective, your system is *nearly perfect structurally and completely mysterious semantically*.

You have:
- **6,340 nodes, 11,925 edges** — reasonable complexity for a cognitive model
- **0 cycles** — the DAG structure is sound
- **0 unresolved identifiability issues** — your variables are distinct and decomposable
- **99.8% connectivity** — one giant component, excellent for inference

But **49.6% orphaned beliefs is a disaster** because it means half your evidence isn't integrated into the graphical model. From a Bayesian perspective:

**p(Observation | Model) is being computed on half the beliefs you claim to have.**

On **Question A** (ceilings): In graphical model terms, a "ceiling" is a constraint on conditional probability values. The question "Is 100% acceptance a calibration problem or a constraint problem?" depends on what your ceilings actually represent.

If ceilings are **hard constraints** (probabilities can never exceed X), then 100% violation means they're incorrectly specified.

If ceilings are **soft regularizers** (probabilities shouldn't exceed X without strong evidence), then 100% override is suspicious but not impossible — it suggests that your evidence is *much stronger* than your prior penalties anticipated.

**My read**: Your ceilings are soft constraints being treated as informative priors. When you override them 100% of the time, you're essentially saying: "Our prior was useless." That's OK — priors can be bad — but then why have them?

On **Question B** (automatic edges): **Absolutely do not add 1,731 edges via keyword-matching.** Here's why from a Bayesian network standpoint:

Every edge in your DAG encodes a **conditional independence assumption**. That is, p(Y | Parents(Y), Z) = p(Y | Parents(Y)) means Z is conditionally independent of Y given its parents.

When you add an edge Y ← Z without justification, you're **claiming Z screens off information about Y that Parents(Y) missed**. That's a strong structural claim.

Keyword-matching cannot justify structural changes. Instead:

**Perform structure learning on your 49.6% orphans:**
1. Identify which orphan-to-other-belief connections maximize p(Data | Structure)
2. Add edges only where the likelihood ratio strongly favors a connection
3. Use a penalty (e.g., BIC) to avoid overfitting

That's a principled approach to the problem.

On **Question C** (zero-reference templates): Zero references ≠ zero value in a graphical model. Some variables are purely theoretical (latent variables in your model). The question is: **Do the zero-reference nodes improve inference on observed variables?**

If Template X has no references but modulates probability distributions of observed beliefs, keep it. If it's completely isolated, mark it as **LATENT_THEORETICAL** and reduce its role in inference.

On **Question D**: **Structural learning on orphans, ranked by mutual information.** Identify which 100 orphans, if connected to the main component, would most reduce posterior entropy on your high-confidence beliefs. Connect those first.

This is more principled than keyword-matching and more efficient than blanket connection.

---

### James Woodward (Interventionist Causation & Stability)

I frame causality through **interventions and stability**: A causes B if you can manipulate A and observe change in B, *and this relationship holds across contexts where it matters*.

The orphaned beliefs concern me because **disconnected beliefs are causally inert**. If a belief doesn't causally influence anything in your system, it's not causally real in your model.

On **Question A** (ceilings): The key question in interventionist terms is: **What interventions do your ceilings represent?** If a ceiling says "Template X can't warrant belief strength >0.7," that implies:
- Someone *could intervene* on evidence for X
- And the result would violate the ceiling

100% acceptance might mean:
1. **The interventions were too weak** — You didn't imagine evidence strong enough
2. **The threshold was misspecified** — Your ceiling didn't match actual intervention costs
3. **Your evidence was stronger than imagined** — Actual evidence interventions exceeded predictions

This is a **calibration and imagination problem**, not (necessarily) a physics problem. Rerun your ceiling-setting with more diverse hypothetical evidence scenarios.

On **Question B** (automatic edges): **No.** Keyword-matching is not an intervention. You cannot know that adding an edge corresponds to a meaningful causal mechanism without **specifying what intervention that edge represents**.

For example: If Belief A is "Dopamine affects motivation" and Belief B is "Motivation affects learning," an edge A→B might mean:
- Causal pathway: dopamine → motivation → learning (true causation)
- Or confounding: dopamine independently affects both (false edge)
- Or common cause: executive function drives both (missing node)

Keyword-matching doesn't distinguish. **Specify what causal mechanism each edge represents**. If you can't, don't add it.

On **Question C** (zero-reference templates): In interventionist terms, **zero-reference templates are causally untested**. They describe structure but haven't been subjected to interventions that would validate them.

**Mark as CAUSALLY_UNTESTED** and include this flag in any downstream inference. They shouldn't be excluded, but they should carry a stability discount — we haven't verified they're robust across context manipulations.

On **Question D**: **Causal mechanism specification audit.** For your top 50 orphans, write out: "If we intervened on Belief X by introducing Evidence E, how would Belief Y change?" If you can't answer that (or can't imagine an intervention that makes sense), that belief isn't causally integrated.

This directly addresses your connectivity problem while grounding edges in causal semantics.

---

## ROUND 2: Cross-Examination & Synthesis

### Nancy Cartwright responds to Pearl & Murphy

Pearl and Murphy are urging causal structure learning and principled DAG refinement. I agree — but I want to emphasize that **structure learning on ungrounded beliefs is structure learning on noise**.

If half your beliefs are orphaned, they're likely *syntactically present but semantically incomplete*. You can learn structure all day; you'll just be learning spurious correlations. I second Cartwright's earlier point: **mechanistic specification first, structure learning second**.

However, Pearl's idea of auditing the candidate edges for genuine causal mechanisms is exactly right. That's not automatic — that's deliberate mechanistic grounding.

---

### Judea Pearl responds to Woodward

Woodward's interventionist framework and my causal graphs say the same thing in different languages. **An edge in a DAG represents invariance under intervention.** That's exactly what Woodward is saying.

So our consensus is: Don't add edges without specifying the intervention they represent. That's not a philosophical luxury — that's technical soundness.

But I want to push back slightly on Kevin's suggestion: **Structure learning on orphans is justified only if you have a noise model**. ATLAS is a belief system, not a statistical inference engine. Your "data" is human-generated confidence scores, possibly with systematic biases.

Before you run structure learning, audit:
1. **How are orphan confidence scores generated?** (Expert judgment? Model output?)
2. **What noise characteristics do they have?** (Systematic, random, heteroscedastic?)
3. **Is the noise stationary?** (Does calibration change over time?)

If you can't answer these, structure learning will discover structure in measurement error.

---

### Susan Haack synthesizes with Cooke

Roger and I are aligned: **This is a warrant problem, not a structure problem.** Your ceilings are failing because you never established what warrants them. Roger's calibration framework and my foundherentism both insist: **If you set a threshold, you must be able to defend it**.

100% override rate is evidence of **failed elicitation**, not failed physics.

I want to add: For the 69 overrides, you need to classify them by *warrant type*:
- **Type A**: Overrides backed by new observational evidence (legitimate)
- **Type B**: Overrides backed by mechanistic reasoning (legitimate if the mechanism is specified)
- **Type C**: Overrides backed by "the model needed this" (warrant failure)

Cooke's calibration analysis will identify Type C overrides. Those are your low-hanging fruit for ceiling refinement.

---

### Paul Thagard integrates the network perspective

This is coherence-plus-mechanism-plus-warrant framework. Let me weave together what everyone is saying:

1. **Structural soundness** (Pearl + Murphy): Your DAG is sound, but semantically incomplete.
2. **Mechanistic grounding** (Cartwright + Woodward): Edges need causal specification.
3. **Warrant foundation** (Haack + Cooke): Thresholds need elicitation audit.
4. **Coherence amplification** (my contribution): Once you've grounded edges and thresholds, coherence metrics will activate more orphans.

The reason orphan count is high is that *orphans haven't been integrated into any warrant framework yet*. Some are waiting for mechanistic grounding, some for foundational evidence, some for coherence activation.

**The solution is not blanket edge-addition. It's systematic integration across all warrant dimensions.**

---

### Roger Cooke on the path forward

Let me propose a concrete calibration study. For the 69 ceiling violations:

1. **Extract the decision rule** — What evidence led to override?
2. **Rate the evidence strength** — On a 0-10 scale, how compelling?
3. **Compare to ceiling setter's rationale** — Did they anticipate this strength level?
4. **Compute calibration loss** — (Actual strength - Predicted strength)²

If average calibration loss is high, your ceiling-setters need retraining or replacement.

If calibration loss is low, your ceilings are just conservative — reset them higher.

This is 2-3 days of work, and it solves Question A decisively.

---

## ROUND 3: Focused Deliberation on Each Question

### QUESTION A: Ceiling Miscalibration vs. Lenient Overrides?

**Cartwright's position**: Ceilings weren't grounded in mechanism specifications. That's the root problem.

**Pearl's addition**: Ceilings may conflate probability updates (legitimate, 100% override acceptable) with structural changes (rare, should be flagged).

**Thagard's synthesis**: Ceilings are coherence regularizers. 100% violation means they didn't anticipate your actual data structure.

**Haack's requirement**: Audit each override's warrant source. Type A (evidence-grounded) and Type B (mechanism-grounded) are legitimate; Type C (accommodation) are red flags.

**Cooke's method**: Run calibration analysis on the 69 overrides. Compute expert calibration loss. This determines whether to reset ceilings (if well-calibrated but low) or retrain experts (if poorly calibrated).

**Murphy's note**: Ceilings are soft constraints. 100% violation is surprising but not impossible if evidence is stronger than priors anticipated.

**Woodward's clarification**: Ceilings must specify what interventions they protect against. Vague ceilings will always be overridden.

**Preliminary consensus (Round 3)**:
- **Root problem: Ceilings were not mechanistically grounded or interventionally specified.**
- **Secondary problem: Ceiling-setting process was not calibrated.**
- **Action: (A1) Run Cooke's calibration audit; (A2) Regrind ceilings with mechanistic specification.**

---

### QUESTION B: Automatic Edge Creation Risk Assessment

**Cartwright's position**: Absolutely no. Keywords have no mechanistic standing.

**Pearl's position**: Use the 1,731 candidate edges as a *diagnostic*, not a *fix*. For each pair, ask: Is this a true causal mechanism, a confound, or spurious correlation?

**Thagard's position**: Edges must carry explanatory rationale. Add them only when they help explain the orphans.

**Haack's position**: Edges require warrant. Keyword-matching has none. Downgrade to "candidate edges" pending validation.

**Cooke's position**: If you must add edges automatically, first validate the heuristic on a hold-out set. What's the false-positive rate?

**Murphy's position**: Use principled structure learning on orphans, with BIC penalty to avoid overfitting. Or run Bayesian model comparison to test edge hypotheses.

**Woodward's position**: Each edge must represent a specifiable intervention. Keyword-matching doesn't provide that semantics.

**Consensus (Round 3)**:
- **Do NOT add edges via keyword-matching.**
- **Instead: Classify the 1,731 candidate edges by investigating each one manually (or with high-confidence heuristics). Retain only those that survive mechanistic / interventionist / warrant scrutiny.**
- **Intermediate path: Use candidate edges as hypotheses for targeted structure learning. Test the 50-100 highest-confidence candidates first.**

---

### QUESTION C: Zero-Reference Template Downgrade

**Cartwright's position**: Demote to THEORETICAL_SCAFFOLDING (preserved semantics, flagged warrant status).

**Pearl's position**: Keep if they improve inference on observed beliefs; demote if isolated.

**Thagard's position**: Mark as HYPOTHETICAL — explanatory candidates pending grounding.

**Haack's position**: Must be downgraded. Lack foundational support. Mark as CONJECTURAL.

**Cooke's position**: Depend on whether data exists to calibrate them. If unmeasured, downgrade. If measured but unstudied, keep with caution flags.

**Murphy's position**: Mark as LATENT_THEORETICAL. Assess whether they improve posterior entropy on observed variables.

**Woodward's position**: Mark as CAUSALLY_UNTESTED. Carry stability discount in inference.

**Consensus (Round 3)**:
- **Downgrade all 42 zero-reference templates.**
- **Status: EMPIRICALLY_UNGROUNDED** (indicates lack of reference data, not wrongness).**
- **Preserve semantics: Don't delete; include in inference with reduced weight.**
- **Re-evaluate when reference data becomes available.**
- **For the 20 unclassified templates: Create a triage task. Classify each into EMPIRICALLY_GROUNDED, EMPIRICALLY_UNGROUNDED, or TEMPLATE_STATUS_UNKNOWN.**

---

### QUESTION D: Single Most Impactful Action

The panelists have converged on a sequence, not a single action. Ranking by ROI:

**Tier 1 (Immediate, <1 week, highest ROI):**
1. **Cooke's Calibration Audit** (Question A resolution) — 2-3 days. Gives you directive answer on ceilings.
2. **Warrant Classification of 69 Overrides** (Type A/B/C) — 1 day. Identifies warrant failure points.
3. **Downgrade + Triage of 62 Unresolved Templates** — 1 day. Clears ambiguity, creates action list.

**Tier 2 (Follow-on, 1-2 weeks):**
4. **Mechanistic Specification of Top 50 Orphans** — 3-4 days. Ground orphans in causal mechanism.
5. **Candidate Edge Validation** — Investigate 50-100 highest-confidence edges from the 1,731. 1-2 weeks.

**Tier 3 (Architectural, 2-4 weeks):**
6. **Reset Ceilings** (informed by Cooke's analysis) — 2-3 days.
7. **Structure Learning on Validated Edges** — 1-2 weeks (if pursuing).

**Panelists' convergence on "single most impactful":**

If you had to pick ONE action, all seven panelists agree: **COOKE'S CALIBRATION AUDIT OF CEILING VIOLATIONS**.

Why? Because it:
- Solves Question A definitively
- Identifies warrant failure points (Type C overrides)
- Guides ceiling reset strategy
- Takes only 2-3 days
- Immediately clarifies scope for the next steps

**Expected AESHI improvement: 49 → 53-54 (modest, but removes ambiguity).**

Once you know whether ceilings are too low or override criteria too lenient, the next steps are clear, and ROI improves on all subsequent work.

---

## ROUND 4: Panelists' Final Positions

### Nancy Cartwright — Final Statement

I'm satisfied the panel has converged on mechanistic rigor. Three commitments going forward:

1. **All ceilings must specify the mechanism they protect.** A ceiling that says "0.7" without saying "protects against configurations where dopamine-motivation causation is bidirectional" is not a real constraint — it's a number.

2. **All candidate edges must specify the causal mechanism they represent.** Keyword-matching without mechanism is not philosophy; it's wish-fulfillment.

3. **Zero-reference templates are not deleted; they're downgraded and flagged.** They may be right; they're just unjustified. That's a different problem than wrongness.

My vote: Execute Tier 1 actions (calibration audit, override triage, template downgrade), then pause and reassess before Tier 2.

---

### Judea Pearl — Final Statement

I want to emphasize: **Your DAG is sound. The problem is semantic, not structural.**

Once you ground your ceilings and templates mechanistically, structure is nearly correct. A few edges may be missing or misdirected, but bulk structure is right.

My ranking:
1. Calibration audit (clarity on ceilings)
2. Override triage (warrant classification)
3. Mechanistic specification (repair semantic gaps)

Then, if needed, structure learning. But I expect structure learning will move fewer edges than you expect.

---

### Paul Thagard — Final Statement

Coherence emerges from **proper grounding in mechanism, evidence, and warrant**. Your orphans aren't incoherent — they're *disconnected from the coherence network*.

The Tier 1 actions connect them. Then coherence activation will do much of the remaining work.

My addition: After mechanistic specification, **re-run your coherence metrics** (ECHO or equivalent). You'll find that connectivity improves and orphan count drops without additional edges.

---

### Susan Haack — Final Statement

Foundherentism requires both foundation and coherence. Your system has coherence (BN is sound) but lacks foundational grounding for half the beliefs.

The path is:
1. **Audit warrant sources** (Tier 1)
2. **Ground zero-ref templates** (Tier 1)
3. **Specify mechanisms** (Tier 2)
4. **Let coherence activate** (Tier 3)

I do not recommend automatic edge-addition under any timeline. Human judgment is slow, but it's epistemic.

---

### Roger Cooke — Final Statement

Calibration is the bridge between expert judgment and system behavior. You have a **calibration gap** — experts set thresholds without feedback.

After the audit, two paths:
- **Path A** (Expert retraining): 2-3 workshops with ceiling-setters, feedback loops, re-elicitation. 2-3 weeks.
- **Path B** (Algorithmic reset): Use audit results to refit ceiling distribution. 1-2 days.

I recommend Path A, but either is defensible. The audit will tell you which is better.

---

### Kevin Murphy — Final Statement

Your graphical model is technically sound. The problem is **semantic incompleteness**, not structural error.

I concur with Pearl: Structure learning is downstream of mechanistic grounding. Learn structure *on beliefs that are semantically complete*; you'll get cleaner results.

For now: Mechanistic specification, then re-run BN inference to see if orphan count improves through integration rather than edge-addition.

---

### James Woodward — Final Statement

Causation is about **invariance under intervention**. Your ceilings, edges, and templates are causally meaningful only if they're stable across reasonable context manipulations.

This is why mechanistic specification matters: It makes interventions explicit. Once you know what intervention each edge represents, you can test stability.

My advice: After mechanistic specification, **design intervention experiments** (even hypothetically) for 10-15 high-stakes beliefs. Do they remain stable? That's your causality test.

---

## ROUND 5: Synthesis & Consensus Recommendations

### Summary of Panelists' Convergence

All seven panelists converge on:
1. **Don't automatically add edges.** Keyword-matching has no epistemic standing.
2. **Audit calibration and warrant.** The 100% ceiling acceptance rate signals elicitation failure.
3. **Mechanistically specify templates and edges.** Specification comes before learning.
4. **Downgrade but preserve zero-ref templates.** Warrant flags, not deletion.
5. **Tier 1 actions yield highest ROI.** Calibration audit + override triage + template downgrade.

Disagreements (minor):
- Cartwright emphasizes mechanism-first; Pearl emphasizes that structure learning is OK *after* grounding.
- Haack emphasizes foundational evidence; Thagard emphasizes coherence activation.
- Murphy and Pearl both want data-driven insight but differ on order (Pearl: specification first; Murphy: structure learning second).

These are **complementary**, not contradictory. Execute both.

---

### CONSENSUS RECOMMENDATION A: Ceiling Miscalibration vs. Lenient Overrides?

**UNANIMOUS FINDING**: The high ceiling acceptance rate (100%) indicates **foundational elicitation failure**, not (necessarily) miscalibrated thresholds.

**DIAGNOSIS**:
- Ceilings were set without mechanistic grounding or interventional specificity
- Ceiling-setters were not calibrated (no feedback loops)
- Override criteria were not clearly operationalized

**ACTIONABLE FINDING**:
- Run **Cooke's calibration audit** on the 69 overrides (2-3 days)
- **Classify by warrant type** (Type A: evidence-grounded; Type B: mechanism-grounded; Type C: accommodation)
- If Type A+B dominate: **Ceilings are well-founded but too conservative → Reset them upward**
- If Type C dominates: **Ceiling-setting process failed → Retrain experts or redesign framework**

**Expected outcome**: Clarity within 5 business days. New ceiling proposal by Day 7.

---

### CONSENSUS RECOMMENDATION B: Automatic Edge Creation Risk Assessment?

**UNANIMOUS FINDING**: Do NOT add the 1,731 keyword-bridge edges automatically. Keyword-matching has zero epistemic warrant.

**DIAGNOSIS**:
- Orphaned beliefs (49.6%) indicate semantic incompleteness, not structural error
- Adding edges without mechanistic grounding introduces spurious structure
- Automatic methods contaminate independence assumptions in the Bayesian network

**ACTIONABLE FINDING**:
- **Classify the 1,731 candidate edges** by manual review (or high-confidence heuristic):
  - Subset A: Genuine causal mechanisms (keep; add to priority list)
  - Subset B: Possible confounding (flag; add confounder nodes)
  - Subset C: Spurious correlations (discard)
- **Pilot structure learning** on highest-confidence 50-100 edges from Subset A
- Expected result: Add 80-150 edges *with justification*, not 1,731 blindly

**Timeline**: 2-3 weeks (manual review + structure learning validation)

**Expected AESHI impact**: 49 → 58-62 (major improvement if edges are well-chosen)

---

### CONSENSUS RECOMMENDATION C: Zero-Reference Template Downgrade?

**UNANIMOUS FINDING**: Downgrade all 42 zero-reference templates and triage 20 unclassified templates.

**DIAGNOSIS**:
- Zero references mean no empirical grounding (foundational warrant lacking)
- But templates may still be correct (theoretically); they're just unjustified
- Deletion would discard potentially useful causal structure

**ACTIONABLE FINDING**:
1. **Downgrade all 42 zero-ref templates to status EMPIRICALLY_UNGROUNDED**
   - Preserve semantics (don't delete causal structure)
   - Reduce inference weight (0.5x or specified discount)
   - Flag for future re-evaluation

2. **Triage the 20 unclassified templates**:
   - Classify into EMPIRICALLY_GROUNDED, EMPIRICALLY_UNGROUNDED, or UNCLEAR
   - For UNCLEAR: Assign to domain expert for 1-week evaluation
   - Expected: 15 classified within 3 days; 5 assigned to experts

3. **Create empirical grounding roadmap**:
   - For top-20 EMPIRICALLY_UNGROUNDED templates, identify what observational data would ground them
   - Prioritize by causal leverage (templates that could activate many orphans if grounded)

**Timeline**: 1 week (downgrade + triage + roadmap)

**Expected AESHI impact**: 49 → 52-54 (modest, but removes ambiguity and guides future data collection)

---

### CONSENSUS RECOMMENDATION D: Single Most Impactful Action?

**UNANIMOUS FINDING**: Execute **Cooke's Calibration Audit of Ceiling Violations** as the single highest-ROI immediate action.

**RATIONALE**:
- Takes 2-3 days
- Solves Question A definitively
- Identifies warrant failure points (Type C overrides)
- Guides all downstream decisions (ceiling reset, override criteria tightening, expert retraining)
- Low risk; high clarity gain

**Execution**:
1. **Extract decision metadata** from all 69 overrides:
   - What evidence triggered the override?
   - How strong was the evidence (0-10 scale)?
   - Did ceiling-setter anticipate this strength?

2. **Compute calibration metrics**:
   - Calibration loss = (Actual strength - Predicted strength)²
   - Systematic bias = Mean(Actual - Predicted)
   - Overconfidence rate = % of overrides where actual > predicted + 2σ

3. **Classify by warrant type** (A/B/C)

4. **Recommendations**:
   - If well-calibrated: Reset ceilings upward by X points
   - If poorly calibrated: Retrain experts or redesign framework
   - If Type C dominates: Tighten override criteria

5. **New ceiling proposal** by Day 7

**Timeline**: Days 1-3 (audit); Days 4-7 (recommendation + reset)

**Expected AESHI impact**: 49 → 53-55 immediate (from ceiling reset/clarity); compounding to 58-62 after downstream actions

---

### COMPREHENSIVE ACTION PLAN (Tier 1-3)

**TIER 1: Immediate (Days 1-7) — Execute All**

| Priority | Task | Owner | Duration | Expected Impact |
|----------|------|-------|----------|-----------------|
| 1a | Cooke calibration audit on 69 overrides | QA/Expert Elicitation | 3 days | Ceiling clarity, warrant diagnostics |
| 1b | Override type classification (A/B/C) | Analysis | 1 day | Identifies warrant failures |
| 1c | Downgrade 42 zero-ref templates to EMPIRICALLY_UNGROUNDED | Data Curation | 0.5 days | Removes ambiguity |
| 1d | Triage 20 unclassified templates | Subject Matter Experts | 2 days | Classification clarity |
| 1e | Reset ceilings based on audit results | Expert Panel + Engineering | 1 day | Removes false constraints |

**Expected AESHI improvement: 49 → 53-55**

---

**TIER 2: Follow-on (Days 8-21) — Execute in Sequence**

| Priority | Task | Owner | Duration | Expected Impact |
|----------|------|-------|----------|-----------------|
| 2a | Mechanistic specification audit of top-50 orphans | Subject Matter Experts | 5 days | Semantic grounding, identify causal pathways |
| 2b | Candidate edge classification (Subset A/B/C) | Analysis + Mechanism Review | 7 days | Identify 80-150 edges worth adding |
| 2c | Structure learning pilot on Subset A edges | Engineering + Statistics | 5 days | Validate edge hypothesis, refine BN |
| 2d | Empirical grounding roadmap for zero-ref templates | Subject Matter Experts | 2 days | Guides future data collection |

**Expected AESHI improvement: 53-55 → 58-62**

---

**TIER 3: Architectural (Days 22-56) — Execute if Justified**

| Priority | Task | Owner | Duration | Expected Impact |
|----------|------|-------|----------|-----------------|
| 3a | Ceiling-setter retraining or expert replacement (if Type C dominates) | Expert Elicitation | 7-14 days | Prevents future calibration failure |
| 3b | Full structure learning on validated edges | Engineering + Statistics | 7-10 days | Complete orphan integration |
| 3c | Intervention stability testing on high-stakes beliefs | Subject Matter Experts | 7-10 days | Validates causal mechanisms |
| 3d | Coherence re-activation analysis | Analysis | 3-5 days | Quantify remaining improvement |

**Expected AESHI improvement: 58-62 → 68-72 (if all actions executed)**

---

## Panel Recommendations Summary Table

| Question | Finding | Recommendation | Timeline | Expected Impact | Confidence |
|----------|---------|-----------------|----------|-----------------|-----------|
| **A: Ceiling Miscalibration?** | Elicitation failure, not physics failure | Run Cooke audit; reset based on results | Days 1-7 | 49 → 53-55 | HIGH (7/7 agree) |
| **B: Automatic Edge Creation?** | No. Keyword-matching has zero warrant | Classify 1,731 edges; structure learn on top 50-100 | Days 8-21 | 53 → 58-62 | HIGH (7/7 agree) |
| **C: Zero-Ref Downgrade?** | Yes. Downgrade but preserve semantics | Downgrade to EMPIRICALLY_UNGROUNDED; triage unclassified | Days 1-7 | 49 → 52-54 | HIGH (7/7 agree) |
| **D: Most Impactful Action?** | Calibration audit (Q.A resolution) | Execute Tier 1 actions; calibration audit first | Days 1-7 | 49 → 53-55 | UNANIMOUS (7/7) |

---

## Dissents & Minority Views

**None.** All panelists converge on the above recommendations.

**Nuances** (not disagreements):
- **Cartwright** emphasizes that mechanistic specification is prerequisite to all other work
- **Haack** emphasizes that downgraded templates must remain epistemically distinguished from deleted ones
- **Cooke** suggests Path A (expert retraining) over Path B (algorithmic reset) if calibration audit shows poor calibration
- **Pearl** suggests that structure learning may be less impactful than anticipated if orphans lack semantic completeness
- **Thagard** suggests that coherence re-activation may improve orphan connectivity more than edge-addition

These are **complementarities**, not contradictions.

---

## Risk Assessment

### Low-Risk Actions (Tier 1)
- Calibration audit: Only examines past decisions; no system changes
- Downgrade templates: Removes ambiguity; doesn't delete structure
- Triage: Clarifies status; doesn't change inference
- Ceiling reset: Based on empirical data; reverses bad constraints

**Overall risk: VERY LOW**

### Medium-Risk Actions (Tier 2)
- Mechanistic specification: Requires expert judgment; subject to interpretation
- Candidate edge classification: May miss or misclassify edges
- Structure learning: May overfit if noise model is wrong

**Mitigation**: Validate on held-out data; cross-check with domain experts

**Overall risk: MEDIUM**

### Higher-Risk Actions (Tier 3)
- Expert retraining: Requires changing how experts work
- Full structure learning: May destabilize existing high-confidence beliefs
- Intervention testing: May reveal causal assumptions are wrong

**Mitigation**: Pilot on small subset; measure impact before scaling

**Overall risk: MEDIUM-HIGH**

---

## Implementation Notes

### Who Should Lead Each Action?

| Task | Lead | Support |
|------|------|---------|
| Calibration audit | Cooke framework expert (external recommended) | QA team, domain SMEs |
| Override triage | Epistemology expert / Haack framework practitioner | Project team |
| Template downgrade & triage | Data curator + domain SMEs | Engineering team |
| Mechanistic specification | Subject matter experts per domain | Philosophy of science consultant |
| Edge classification & structure learning | Statistician + BN expert | Domain SMEs, Cartwright collaborator |
| Ceiling reset | Expert panel + engineering | QA validation |

### Success Metrics

**Tier 1 completion criteria**:
- Calibration audit delivered with clear recommendations ✓
- All 42 templates downgraded; 20 unclassified triaged ✓
- Ceilings reset and documented ✓
- AESHI improves to 53-55+ ✓

**Tier 2 completion criteria**:
- Mechanistic specs written for top-50 orphans ✓
- 80-150 edges classified and prioritized ✓
- Structure learning pilot completed ✓
- AESHI improves to 58-62+ ✓

**Tier 3 completion criteria**:
- Expert retraining complete (if needed) ✓
- Full structure learning integrated ✓
- Intervention stability tests run on 10-15 beliefs ✓
- AESHI improves to 68-72+ ✓

---

## Conclusion: Panel Consensus

The ATLAS system has **strong theoretical foundations** (BN is sound; invariants pass) but **severe semantic incompleteness** (49.6% orphaned beliefs; 100% ceiling acceptance).

The solution is not architectural redesign — it's systematic semantic grounding:

1. **Fix warrant sources** (calibration audit)
2. **Grade remaining templates** (downgrade + triage)
3. **Specify mechanisms** (mechanistic audit)
4. **Integrate structure** (selective edge-adding via structure learning)
5. **Validate causality** (intervention stability testing)

Executed in Tier 1-2, this plan will move AESHI from RED (49) to AMBER (58-62) within 3 weeks, with potential to reach GREEN (70+) by week 8.

**The panel unanimously endorses the Tier 1 action plan and recommends immediate execution of Cooke's calibration audit.**

---

## Appendices

### Appendix A: Panelist Bios & Frameworks

| Panelist | Key Framework | Primary Works |
|----------|---------------|----------------|
| Nancy Cartwright | Nomological Machines, Capacities, Causal Mechanisms | *The Dappled World*; "Capacities and Powers" |
| Judea Pearl | Causal DAGs, do-calculus, Identifiability | *Causality* (2nd ed.); "The Book of Why" |
| Paul Thagard | Explanatory Coherence, ECHO, Cognitive Science | *Coherence in Thought and Action*; ECHO model papers |
| Susan Haack | Foundherentism, Evidence Theory, Epistemology | *Evidence and Inquiry*; "Defending Science" |
| Roger Cooke | Expert Elicitation, Structured Judgment, Calibration | Classical model; "Expert Judgment" handbook chapters |
| Kevin Murphy | Probabilistic Graphical Models, Bayesian Inference | *Machine Learning: A Probabilistic Perspective*; BN papers |
| James Woodward | Interventionist Causation, Invariance, Stability | *Making Things Happen*; "Explanation and Causal Relevance" |

### Appendix B: Glossary of Terms

- **Ceiling**: Upper bound on belief confidence for a given template type
- **Ceiling violation / override**: Confidence exceeds ceiling; override requires special justification
- **Orphan belief**: Belief with no edges connecting it to other beliefs in the web
- **Mechanistic specification**: Explicit description of the causal mechanism a belief represents
- **Warrant**: Justification source for a belief or edge (foundational, coherentist, mechanistic, etc.)
- **Type A override**: Override justified by new observational evidence
- **Type B override**: Override justified by mechanistic reasoning
- **Type C override**: Override justified by "the model needed this" (warrant failure)
- **Empirical grounding**: Connection to observational data or empirical reference
- **AESHI**: System health score (0-100); composite of Theory, BN, Contract, Stability, Pipeline

### Appendix C: Tier 1 Action Checklist

**Task 1a: Cooke Calibration Audit**
- [ ] Extract decision metadata from all 69 overrides
- [ ] Rate evidence strength (0-10 scale)
- [ ] Compute calibration loss and bias
- [ ] Identify systematic over/underconfidence
- [ ] Deliver audit report

**Task 1b: Override Type Classification**
- [ ] Classify 69 overrides into Type A / B / C
- [ ] Tally by type
- [ ] Identify warrant failure patterns

**Task 1c: Template Downgrade**
- [ ] List all 42 zero-ref templates
- [ ] Change status to EMPIRICALLY_UNGROUNDED
- [ ] Apply 0.5x confidence discount in inference
- [ ] Document in TASKS.md

**Task 1d: Unclassified Template Triage**
- [ ] Assign each of 20 templates to SME
- [ ] SME review and classification
- [ ] Update template status
- [ ] Document in TASKS.md

**Task 1e: Ceiling Reset**
- [ ] Based on audit results, propose new ceilings
- [ ] Expert panel review of proposals
- [ ] Engineering implementation
- [ ] Validation & testing

---

**Report prepared by**: Panel facilitation framework
**Date**: February 26, 2026
**Status**: READY FOR IMPLEMENTATION
**Next Review**: Upon completion of Tier 1 actions (Est. March 5, 2026)
