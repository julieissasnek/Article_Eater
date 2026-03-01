# PANEL CONSULTATION — Philosophical Paper Sharpening
## Convened: February 25, 2026 | Duration: Focused consultation (not a full panel)
## Purpose: Sharpen the novelty claim, identify strongest objections, confirm venue framing

---

## Panel Composition (5 experts)

1. **Susan Haack** (Philosophy of evidence, foundherentism) — Selected because her work explicitly bridges coherentism and foundationalism, and because her critique of coherentism (underspecification of coherence) is one the paper must address.

2. **Paul Thagard** (Explanatory coherence, ECHO) — Selected because the paper's typed web extends his constraint-satisfaction approach, and he would know whether the extension is genuine or cosmetic.

3. **Judea Pearl** (Causal inference, do-calculus) — Selected because the paper's central architectural claim is about the web-BN boundary, and Pearl would know whether the boundary is drawn correctly.

4. **Stephan Hartmann** (Bayesian coherentism) — Selected because he has argued that Bayesian methods can capture coherence phenomena, which is the strongest potential counter-argument to the paper's claim that the web and BN do fundamentally different things.

5. **Kevin Kelly** (Formal learning theory, topology of inquiry) — Selected because the paper's algorithms make convergence claims, and Kelly's framework provides the most rigorous tools for evaluating those claims.

---

## Round Table: What Is the Genuine Novelty Here?

**Haack**: The novelty is not in coherentism itself — Quine, BonJour, Lehrer, and I have all articulated versions of coherentist epistemology. The novelty is in the *implementation*. Nobody has built a working computational system that maintains a coherentist knowledge base with typed justificatory links, and that interfaces it with a causal inference engine. The ECHO model comes closest, but it was a toy system — 20-30 nodes, binary coherence constraints, no typed edges, no bridge warrants, no interface to Bayesian machinery. If the paper can demonstrate that a 130-node web with 8 edge types and 400 edges actually *computes* — that the algorithms terminate, converge, and produce reasonable outputs — that is a genuine contribution. But it must be honest about the gap between philosophical ambition and computational reality: has this actually been tested, or is it a specification?

**Thagard**: Susan is right that ECHO was limited, and I'd go further: the typed edge structure is a real advance over my constraint-satisfaction approach. In ECHO, all coherence relations were symmetric and untyped — explanation, analogy, and contradiction were the only relation types, and they all contributed to the same constraint satisfaction problem. The CMR's eight edge types, with different attenuation factors and different propagation rules, capture distinctions that ECHO could not. The CONSTITUTIVE/MECHANISM/ANALOGICAL hierarchy, in particular, formalises something that I knew was important but never specified: that different kinds of evidential support have different epistemological characters. The key question for the paper is whether the typed propagation rules are *principled* or *ad hoc* — are the alpha values derived from something, or are they just numbers someone chose?

**Pearl**: The architectural claim — that the web does everything except interventional and counterfactual reasoning, and the BN provides exactly those two things — is correctly stated but potentially controversial. Many people in my community believe that causal Bayesian networks are the right representation for scientific knowledge full stop, not a secondary projection from some other structure. The paper needs to make a clear argument for why the BN is insufficient as a primary knowledge representation. The best argument is the one you've already made: the BN has no concept of explanation, no concept of warrant types, no concept of reflective equilibrium, and no mechanism for self-revision. It computes with whatever structure it is given. But you should be precise about the do-calculus claim: the web's compositional chain propagation *implicitly assumes intervention* (each step is "if this input is present, this output follows"), but it doesn't handle confounding. The BN's unique contribution is handling the *difference between seeing and doing in the presence of confounders*. State it that precisely.

**Hartmann**: I will be the devil's advocate. In my work with Bovens, we showed that Bayesian methods can capture coherence phenomena — that the degree to which evidence *coheres* (mutual support, multiple independent confirmation) can be measured using standard probability theory. Your paper claims that the web does something the BN cannot: reflective equilibrium. I'm not entirely convinced. Bayesian model selection — comparing the marginal likelihoods of competing models — is a formal method for choosing between theoretical frameworks, which is what reflective equilibrium does informally. The paper should engage with this objection directly: what *specifically* can reflective equilibrium do that Bayesian model selection cannot? My suggestion: the answer is *structural innovation*. Bayesian model selection operates over a pre-specified hypothesis space. Reflective equilibrium can generate new hypotheses — the Barrett-Craig two-stage model was not in anyone's prior hypothesis space; it emerged from the confrontation between two existing theories. Bayesian methods cannot generate new hypotheses; they can only evaluate existing ones.

**Kelly**: Two things. First, convergence. Your Algorithm 1 claims convergence with damping factor λ < 1/(1+max_degree). This is a standard result for linear iterative methods, but your algorithm has a sigmoid nonlinearity and bridge warrant ceiling clipping, both of which complicate the convergence analysis. You should be careful about the convergence claim — state it as empirically observed convergence for the CMR's specific graph, not as a proven theorem. Second, the testing protocol. Your Level 2 (retrodiction) is the most important test, and it's also the most philosophically interesting. If the calculus reproduces the panels' historical decisions, it means the panels were reasoning coherently — their informal judgments follow from the formal rules. If it doesn't, either the calculus is wrong or the panels were inconsistent. Either way, it's informative. But note: retrodiction is not prediction. Reproducing known decisions is necessary but not sufficient. Level 3 (sealed CROSSCUT-I predictions) is the real test. The paper should be clear about what has been tested and what hasn't.

---

## Crucible: Strongest Objections a Referee Would Raise

### Objection 1: "This is just a knowledge graph with extra steps."

**Response** (Thagard + Haack consensus): A knowledge graph stores facts and relations. A web of belief stores *justified beliefs* — beliefs with epistemological provenance (Toulmin structures, bridge warrant types, competing accounts, revision clauses). The difference is not decorative. A knowledge graph cannot answer "why do we believe this?" or "what would change our minds?" or "how confident should we be?" The CMR web can, because the epistemological provenance is first-class data, not metadata.

### Objection 2: "The alpha values are ad hoc — you could get any result by tuning them."

**Response** (Kelly + Thagard consensus): The alpha values are parameters, and parameters require justification. The paper should: (a) motivate the alpha values from the bridge warrant hierarchy (which has independent philosophical justification), (b) propose the retrodiction test as the calibration method, and (c) report the sensitivity analysis (Frontier 3) showing how much the outputs vary across the plausible range of alpha values. If outputs are stable, the ad-hoc-ness doesn't matter. If outputs are sensitive, the specific sensitive parameters become empirical targets.

### Objection 3: "Reflective equilibrium is a philosophical concept, not a computational one. You can't 'formalise' it without losing what makes it interesting."

**Response** (Haack, dissenting from the majority): There is real tension here. Reflective equilibrium in philosophy involves *normative judgment* — deciding whether a principle ought to be revised in light of a particular case, or whether the case should be reinterpreted in light of the principle. The CMR's Algorithm 4 (Structural Revision) approximates this with entrenchment ordering and coherence maximisation, but these are *proxy* criteria. The algorithm revises beliefs to restore coherence, which is *necessary* for reflective equilibrium but not *sufficient* — genuine reflective equilibrium also involves normative evaluation of whether the coherent result is epistemically acceptable. The paper should acknowledge this limitation honestly.

**Hartmann concurs**: The formalisation captures the *structural* aspects of reflective equilibrium (mutual adjustment, minimal change, entrenchment) but not the *evaluative* aspects (whether the resulting equilibrium is good). This is a genuine limitation, and the paper is stronger if it says so rather than overclaiming.

### Objection 4: "You haven't actually built and tested this system."

**Response** (Pearl): This is the most damaging objection if it's true. The paper must be precise about what exists (the web structure, the calibrated templates, the algorithms as specifications) and what doesn't yet exist (running code, empirical test results). A paper that presents specifications as results will be rejected at any good journal. But a paper that presents the *architecture* — with honest acknowledgment that implementation and testing are next steps — can be published if the architecture itself is sufficiently novel and well-motivated. Frame it as a theoretical contribution with a concrete implementation plan, not as an empirical report.

---

## Consensus Recommendations for Paper Framing

1. **Venue**: *Philosophy of Science* or *Synthese* for the philosophical argument; *Artificial Intelligence* if emphasising the computational architecture. The paper straddles philosophy and AI; the framing should tilt toward one audience. **Recommendation**: Write for *Philosophy of Science* but include enough technical detail (in appendices) that the AI community can evaluate the algorithms. This positions the paper as "philosophy of science with computational teeth" rather than "AI system with philosophical aspirations."

2. **Title suggestion**: "From Philosophical Metaphor to Computational Architecture: How a Web of Belief Becomes a Working Knowledge System" — signals the transformation from philosophy to computation.

3. **Central argument**: The philosophical traditions of coherentism (Quine, Thagard) and causal inference (Pearl, Spirtes) have developed independently. Neither is sufficient for representing scientific knowledge in a computationally useful way. Coherentism captures the epistemological structure of science (why we believe what we believe) but lacks causal inference machinery. Causal inference provides rigorous interventional and counterfactual reasoning but lacks epistemological structure (it has no concept of explanation, warrant, or coherence). The CMR system demonstrates that these traditions can be *integrated* by maintaining a typed web of belief (for epistemological reasoning) that interfaces with a Bayesian network (for causal inference) through a formal projection function. The integration is not merely juxtaposition: the web generates the BN's structure and parameters, and the BN's predictions feed back to the web for diagnosis and revision.

4. **What to include**: The case study (CMR, 130 nodes, 400 edges) as a proof of concept. The algorithms as formal specifications. The testing protocol as a validation plan. Honest limitations (algorithms not yet implemented, retrodiction not yet run, alpha values not yet calibrated).

5. **What to omit**: The full details of the 12 domain panels (too much domain content for a philosophy paper). The complete pseudocode (put in appendices). The Cowork specification (not relevant to the philosophical argument).

---

*Panel consultation complete. Duration: focused. Outcome: five actionable recommendations, four objection-response pairs, confirmed venue and framing strategy.*
