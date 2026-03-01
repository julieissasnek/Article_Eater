# REFEREE SIMULATION PANEL — Adversarial Review of Paper Draft
## "From Philosophical Metaphor to Computational Architecture"
## Convened: February 25, 2026 | Purpose: Stress-test the three weakest points

---

## Panel Composition (5 referees, simulated as hostile-but-fair)

1. **James Woodward** — Interventionist philosophy of causation
2. **Erik Olsson** — Coherence sceptic (*Against Coherence*)
3. **Luc Bovens** — Bayesian coherentism (with Hartmann)
4. **Fred Muller** — Structural realism, philosophy of science methodology
5. **Holly Andersen** — Mechanisms and causation in philosophy of science

---

## ROUND 1: Individual Critiques

---

### Referee 1: James Woodward

**Overall assessment**: The paper makes a genuinely interesting architectural proposal, and the case study gives it concreteness that most philosophy-of-science papers lack. But the central claim about the web-BN boundary has a problem that the paper does not acknowledge.

**Major concern — The web already does causal reasoning.** The paper claims (§4.5) that the web handles "everything except interventional inference and counterfactual reasoning." But the web's mechanism chains — daylight → 5-HT synthesis → mood modulation — ARE causal claims. They specify that one thing *causes* another through an intermediate mechanism. The web's compositional chain propagation multiplies effect sizes along causal pathways. This is causal reasoning.

The paper tries to dodge this by saying the web's causal reasoning "implicitly assumes intervention" (§4.1), meaning it treats each step as an interventional conditional. But if the web already implicitly assumes intervention, then what exactly does the BN add? The paper says: confounding control and counterfactual computation. This is correct but undersells the distinction. The real issue is not that the web can't do causal reasoning — it does — but that the web's causal reasoning is *mechanism-based* while the BN's is *variable-based*. The web traces pathways through mechanisms; the BN computes over probability distributions on variables. These are different *modes* of causal reasoning (Illari & Russo, 2014, make this distinction explicitly), and the paper would be stronger if it named the distinction rather than drawing a sharp line between "web = not causal" and "BN = causal."

**Specific revision**: In §4.1 and §4.5, replace "the web handles everything except interventional and counterfactual reasoning" with something like "the web handles mechanism-based causal reasoning (tracing pathways, specifying intermediate steps, compositional propagation), while the BN handles variable-based causal reasoning (interventional inference via do-calculus, confounding control, counterfactual computation). The distinction is between *how* causes are represented: as mechanistic pathways with epistemic provenance, or as statistical dependencies between variables." This is more accurate and more defensible.

**Minor concern**: The paper cites Rubin (1974) in the references but never engages with the potential outcomes framework. Either use it or drop it.

---

### Referee 2: Erik Olsson

**Overall assessment**: The paper claims to have made coherentism computable. I am sceptical, and the scepticism is specific.

**Major concern — Coherence and truth.** In my book (*Against Coherence*, 2005), I demonstrated that under quite general conditions, coherence among testimonial reports is not truth-conducive — coherent reports are not more likely to be true than incoherent ones, unless the individual reports are already reliable. The paper does not engage with this result. Algorithm 3 computes a coherence metric, but the paper never asks: *does high coherence indicate that the web is correct?* 

The paper acknowledges in §3.4 that "coherence is not truth" (briefly, in the limitations of Algorithm 4) and in §7.1 that the coherence-truth debate continues. But this is too casual. The problem is foundational: if coherence is not truth-conducive, then maximising coherence (which is what the algorithms do) could be *actively misleading* — producing a web that is internally consistent but systematically wrong. The testing protocol (§6) is supposed to guard against this, but Levels 1–2 test internal consistency and retrodiction (which are themselves coherence-based criteria), and Levels 3–5 (prediction and transfer) have not been run.

**Specific revision**: The paper needs a dedicated subsection — perhaps §7.1.1 — that engages with the coherence-truth problem directly. The honest answer, I believe, is this: (a) Olsson's impossibility result applies to *testimonial coherence* among independent witnesses, not to *explanatory coherence* among theoretically connected beliefs (Bovens & Hartmann 2003 make this distinction); (b) the CMR web is not a set of independent testimonies but a structured network with typed edges, Toulmin provenance, and empirical grounding (data priority), which partially vitiates the independence assumptions in Olsson's proof; (c) the testing protocol's Level 3–5 tests provide the empirical check that coherence alone cannot — they test the web's predictions against reality, not against itself. State this argument explicitly. I may not agree with it, but it is the right response.

**Secondary concern**: The paper says Algorithm 3's coherence metric answers Haack's (1993) challenge. Haack's challenge was about *foundherentism* — she wanted a coherence metric that respected the special role of empirical evidence (data priority). Does Algorithm 3 do this? The data priority principle appears nowhere in the algorithm's specification. Bridge warrant types implicitly encode it (CONSTITUTIVE and MECHANISM bridges rest on empirical data), but this should be made explicit.

---

### Referee 3: Luc Bovens

**Overall assessment**: This is a substantial paper and I recognise the ambition. But the reflective equilibrium claim in §7.2 does not survive scrutiny in its current form.

**Major concern — Bayesian model selection and structural innovation.** The paper argues (§7.2) that reflective equilibrium can expand the hypothesis space by generating new theories (citing the Barrett-Craig compromise), while Bayesian model selection operates over a pre-specified hypothesis space. This is the paper's central response to the Bayesian objection. But it's not quite right.

Bayesian model selection can operate over an *open* hypothesis space if new models are generated by some external process and then evaluated by their marginal likelihoods. The Bayesian framework doesn't *generate* new models, but it doesn't prevent them from being generated by other means (abduction, analogy, creative insight) and then evaluated Bayesianly. So the real question is not whether Bayesian methods can handle new hypotheses (they can, once generated) but *how* the new hypotheses are generated and whether the generation process has epistemic content.

The paper's Algorithm 4 (Structural Revision) is the relevant mechanism: it can add new nodes and edges. But Step 4, Option E ("Add new node — new hypothesis or template") is specified as the most expensive option, invoked only when cheaper options fail. The algorithm does not specify *how* the new node is generated — it just says "add new node." This is where the paper's claim breaks down: the algorithm can *evaluate* new hypotheses (by computing their impact on coherence), but it cannot *generate* them. The generation step is delegated to "human or LLM-simulated-panel intelligence" (§129.9 in the supplement).

**Specific revision**: Acknowledge this more precisely in §7.2. The claim should be: "The *web framework* supports reflective equilibrium because it permits structural innovation (new nodes, new edges, new edge types). The *algorithms* support the *evaluation* of structural innovations by computing their coherence impact. But the *generation* of structural innovations remains outside the formal system. Reflective equilibrium, as instantiated in the CMR, is a collaboration between formal evaluation (the algorithms) and creative generation (the panels). Neither alone is sufficient." This is weaker than the current claim but more honest and more defensible.

**Minor concern**: The paper's response to Bovens & Hartmann (2003) in §7.2 ("BN parameters are revised by Bayes' rule in response to evidence, but reflective equilibrium adjusts beliefs in response to coherence with other beliefs — these are different epistemic operations") is correct but needs a citation to distinguish Bayesian updating from Bayesian model selection. Bayesian updating revises parameters within a model; Bayesian model selection chooses among models. The paper conflates these in the current formulation.

---

### Referee 4: Fred Muller

**Overall assessment**: A philosophically ambitious paper with real content. My concerns are methodological.

**Major concern — Discovered vs. stipulated.** The paper identifies this as Crucible 5 of the FOUNDATIONS-I panel (§128.4 in the supplement, referenced in §2.3 of the paper) but does not take a position. Is the bridge warrant hierarchy (CONSTITUTIVE > MECHANISM > ... > THEORETICAL_DEFAULT) an empirical discovery or a methodological stipulation? This matters enormously for the paper's philosophical contribution. If discovered, the hierarchy is a genuine contribution to confirmation theory — a finding about how different kinds of evidence support theoretical claims. If stipulated, it is a useful convention but carries no philosophical weight beyond its instrumental value.

The paper should take a position. My reading of the evidence presented is that the hierarchy is *empirically grounded but not empirically determined* — it reflects genuine epistemological distinctions (a complete mechanism trace IS stronger evidence than an analogy, for reasons anyone would accept) but the specific numerical ceilings (0.75 for CONSTITUTIVE, 0.35 for ANALOGICAL) are calibration parameters, not discovered constants. The hierarchy's *ordering* is discovered; the hierarchy's *numbers* are stipulated. This distinction between ordinal and cardinal properties would clarify much of the paper's discussion.

**Secondary concern — Structural realism.** The paper implicitly adopts a kind of structural realism about scientific knowledge — what matters is the *structure* of the web (typed edges, node tiers, coherence constraints), not the specific content of any particular belief. This is a philosophically loaded position. Is the web a representation of the *structure of reality* (scientific realism) or a representation of the *structure of scientific belief* (epistemological constructivism)? The paper seems to want both. §2.4 says the web tracks epistemic probability ("a fact about us, not about the world"), which is constructivist. But the testing protocol (§6) evaluates the web against real-world observations, which presumes the web is *about* the world, not just about our beliefs. The paper should acknowledge this tension or resolve it.

---

### Referee 5: Holly Andersen

**Overall assessment**: The paper's treatment of mechanisms is its greatest strength and its most underexploited resource. The mechanism chains in the CMR web — with their typed edges, Toulmin provenance, and compositional propagation — are a concrete implementation of what the new mechanist philosophy of science (Machamer, Darden, & Craver, 2000; Bechtel & Abrahamsen, 2005) has argued for theoretically: that scientific explanation is fundamentally about mechanisms, and that mechanisms have internal structure that matters for explanation.

**Major concern — The mechanism-causation relationship.** The paper draws a boundary between the web (mechanisms) and the BN (causation). But in the new mechanist literature, mechanisms ARE causal structures. A mechanism is a set of entities and activities organised to produce a phenomenon — this is a causal claim. The web's mechanism chains are causal chains. The paper's boundary is not between mechanism and causation but between two *kinds* of causal representation:

- The web represents causation as *mechanisms with internal structure* — intermediate steps, each with its own evidence base, warrant type, and uncertainty.
- The BN represents causation as *statistical dependencies between variables* — conditional probabilities without internal mechanistic structure.

This is essentially Woodward's point too, and I agree with his suggested revision. But I want to push further: the paper should connect its architecture to the levels-of-mechanisms literature (Craver, 2007). The CMR's tier structure (T1 → T1.5 → T2) is a levels hierarchy. T1 frameworks are higher-level mechanisms (predictive processing is a mechanism for how the brain handles uncertainty). T2 templates are lower-level mechanisms (the specific pathway from ceiling height through spatial prediction error to creative cognition). The reduction edges between tiers are *constitutive relevance* relations in Craver's sense — lower-level mechanisms are components of higher-level mechanisms.

**Specific revision**: Add a paragraph in §2.1 connecting the typed web to the new mechanist philosophy. The CMR web is not merely a coherentist structure — it is a *mechanist* structure with coherentist properties. The typed edges encode mechanistic organisation (reduction = constitutive relevance, bridge warrant = evidential bridge from mechanism to phenomenon). This connection to the new mechanism literature would strengthen the paper significantly, because it grounds the abstract coherentist framework in a concrete philosophy of scientific explanation that has independent support.

**Minor concern**: The paper mentions Toulmin (1958) in §2.2 but doesn't cite Machamer, Darden, & Craver (2000) or Craver (2007). These are the most relevant references for the mechanism claims and should be added.

---

## ROUND 2: Cross-Referee Discussion

**Woodward**: Holly and I agree on the main point — the web-BN boundary is between mechanism-based and variable-based causal reasoning, not between non-causal and causal reasoning. This is a friendly amendment, not a fatal objection. The paper's architecture is right; the framing is slightly off.

**Olsson**: I want to push back on my own objection somewhat. The paper's architecture — web for epistemology, BN for causal inference, testing protocol for empirical accountability — is actually a *response* to my coherence-truth worry, even if the paper doesn't frame it that way. The web maximises coherence (my concern). The BN generates predictions (my requirement for empirical grounding). The testing protocol checks predictions against reality (my escape route from the coherence trap). If the paper framed the three-component architecture as a response to the coherence-truth problem — coherence PLUS empirical prediction PLUS testing = a system that is both coherent and empirically accountable — that would be a genuine contribution to the coherence-truth debate, not just a dodge.

**Bovens**: Erik makes an excellent point. The paper buries the epistemological significance of the three-component architecture. It's presented as a software engineering decision (we need a web for epistemology and a BN for causal inference), but it's actually a *philosophical* decision about how to combine the virtues of coherentism (explanatory depth, mutual support, reflective equilibrium) with the virtues of empiricism (empirical accountability, predictive testing). This is a reconciliation of coherentism and empiricism that deserves to be stated as such.

**Muller**: Agreed. The paper's deepest philosophical contribution is not the web or the BN taken individually but the *interface* between them — the projection function that translates epistemic provenance into aleatory parameters, and the feedback loop that translates empirical discrepancies into revision signals. The interface is where coherentism meets empiricism. The paper should say this explicitly.

**Andersen**: And the mechanism chains are what makes the interface possible. You can project a mechanism chain into a BN edge because mechanism chains have the right structure — they specify causal pathways with quantitative parameters at each step. You can't project a bare coherence relation into a BN edge because coherence relations don't specify causal pathways. The mechanism-based structure of the web is what enables the projection function. This should be stated.

---

## ROUND 3: Consensus Recommendations

### Mandatory Revisions (all five referees agree)

**R1**: Reframe the web-BN boundary as mechanism-based vs. variable-based causal reasoning (Woodward, Andersen). This is more accurate and more defensible. Revise §4.1, §4.5, and §7.3 accordingly.

**R2**: Engage with the coherence-truth problem directly (Olsson). Add §7.1.1 addressing Olsson (2005), distinguishing testimonial from explanatory coherence, and framing the three-component architecture (web + BN + testing) as a response to the coherence-truth worry.

**R3**: Sharpen the reflective equilibrium claim (Bovens). Acknowledge that the algorithms evaluate but do not generate structural innovations. State that reflective equilibrium in the CMR is a collaboration between formal evaluation and creative generation. Distinguish Bayesian updating from Bayesian model selection.

### Strongly Recommended Revisions (4 of 5 agree)

**R4**: Connect to new mechanism philosophy (Andersen). Add citations to Machamer, Darden, & Craver (2000) and Craver (2007). Identify the tier structure as a levels hierarchy and reduction edges as constitutive relevance relations.

**R5**: State the paper's deepest contribution explicitly (Bovens, Muller, Olsson, Andersen): the three-component architecture reconciles coherentism and empiricism by combining coherence maximisation (web), empirical prediction (BN), and testing (real world). The interface between web and BN is where the reconciliation happens.

**R6**: Take a position on discovered vs. stipulated (Muller): the hierarchy's ordering is discovered (grounded in genuine epistemological distinctions); the numerical ceilings are calibratable parameters. State this.

### Optional Revision

**R7**: Remove Rubin (1974) from references unless it is engaged with substantively (Woodward).

---

## ROUND 4: Priority Assessment for Revision

| Revision | Difficulty | Impact on Paper | Priority |
|----------|-----------|----------------|----------|
| R1 (mechanism vs. variable causation) | MODERATE — reframe, not rewrite | HIGH — fixes the paper's most vulnerable claim | 1 |
| R2 (coherence-truth §7.1.1) | MODERATE — add ~500 words | HIGH — pre-empts the most dangerous review | 2 |
| R5 (state deepest contribution) | LOW — add ~200 words to conclusion | HIGH — elevates the paper | 3 |
| R3 (sharpen reflective equilibrium) | LOW — revise ~300 words in §7.2 | MEDIUM — makes an existing argument more precise | 4 |
| R4 (new mechanism philosophy) | LOW — add ~200 words + 2 citations | MEDIUM — connects to important literature | 5 |
| R6 (discovered vs. stipulated) | LOW — add ~150 words to §2.3 | MEDIUM — resolves an open question | 6 |
| R7 (drop Rubin) | TRIVIAL | LOW | 7 |

---

*REFEREE_SIMULATION_PANEL.md — CMR Project*
*February 25, 2026 (Session 11)*
*For paper revision guidance*
