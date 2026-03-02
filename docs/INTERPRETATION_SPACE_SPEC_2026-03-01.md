# The Interpretation Space: A Specification for Endogenous Knowledge Valuation in ATLAS

**Date**: 2026-03-01
**Authors**: David Kirsh & Claude (CW)
**Status**: Conceptual specification — ready for panel review
**Version**: 2.0 (expanded with probatory rule sets and epistemic closure framework)

---

## 1. Motivation

The ATLAS system currently maintains three computational layers: an Epistemic Network (EN) of beliefs with credences, warrants, and argumentation structure; a Bayesian Network (BN) for causal inference over environmental variables; and a QA system that translates this knowledge into answers for human users. A fourth layer — what we call the Interpretation Space — is implicit in the existing architecture but has never been formalized. This document specifies what it is, why it matters, and how it should be built.

The core observation is this. The QA system, when applied reflexively to the EN, reveals a *periphery of knowledge* — a boundary surface between what the system knows well, what it knows weakly, and what it does not know at all. This periphery is not a static object; it has intrinsic structure determined by the beliefs themselves, their warrant chains, their argumentation vulnerabilities, and the question-type operators that can be applied to them. The Interpretation Space is the formal representation of this periphery, together with the value landscape it implies for future investigation.

The key intellectual move is to recognize that the value of acquiring new knowledge is not primarily determined by external demand (what users happen to ask about) but by the *internal coherence structure* of the web of belief. A Quinean epistemology holds that beliefs face the tribunal of experience as a corporate body; revisions are evaluated by their impact on the whole web. The same logic applies to acquisitions: the value of new evidence is determined by how it would reshape the web — resolving tensions, completing mechanisms, establishing boundaries, validating contested claims. This value can be computed endogenously, without waiting for external queries, by systematically applying the QA system's own question-type operators to the EN and evaluating the quality of its own answers.

---

## 2. The Four Zones

The Interpretation Space partitions the epistemic territory into four zones, ordered by distance from the center of well-established knowledge:

### Zone 1: The Known Interior

Beliefs with high credence (≥ 0.7), strong warrants (CONSTITUTIVE or MECHANISM with d ≥ 0.80), and successful argumentation defense (no unresolved attacks of severity > 0.3). These beliefs are stable in the Quinean sense: revising them would require substantial reorganization of the web. The QA system gives confident, well-sourced answers about claims in this zone.

**Example**: "Natural daylight exposure in offices improves self-reported alertness." Supported by multiple RCTs, mechanistic account through circadian entrainment (SCN → melanopsin → cortisol rhythm), no serious unresolved critiques. Credence 0.85, warrant type MECHANISM, discount factor 0.80.

**Characteristic**: The system can explain *why* this is true (mechanism), *how much* (effect sizes), *for whom* (boundary conditions), and *what would change its mind* (what evidence would lower credence).

### Zone 2: The Active Boundary

Beliefs with moderate credence (0.4–0.7), or with warrant chains that have gaps, or with active argumentation disputes. The system can answer questions about these beliefs but with meaningful caveats. This is where scientific activity is most productive — the claims are well-formed enough to test but uncertain enough that new evidence would make a real difference.

**Example**: "Fractal dimension D ≈ 1.3–1.5 in architectural facades is preferred cross-culturally." Supported by several studies (Hagerhall et al. 2004, Taylor et al. 2005, Spehar et al. 2003) but the cross-cultural claim is under-tested — most studies use Western populations. Credence 0.62, warrant type EMPIRICAL_ASSOCIATION, discount factor 0.65. An unresolved boundary critique exists: "Does this hold for populations raised in highly rectilinear environments (e.g., modernist housing projects)?"

**Characteristic**: The system can state the claim and cite evidence, but the follow-up questions it generates are substantive rather than merely expansive — they point to genuine uncertainties.

### Zone 3: The Identified Periphery

Gaps that are explicitly represented in the VOI system — questions the system knows it cannot answer, classified by gap type (MECHANISM, VALIDATION, BOUNDARY, DIRECTION, INTERACTION, MEDIATION) and linked to the beliefs they would affect if resolved. These are well-formed questions without answers.

**Example**: "What is the dose-response curve for biophilic elements in windowless workspaces? Is there a minimum vegetation coverage ratio below which the effect disappears?" This gap is identified by the gap predictor because the belief "visible vegetation reduces stress" has no boundary specification for coverage thresholds, and multiple templates reference vegetation without quantifying amount.

**Characteristic**: The system can articulate the question precisely, explain why it matters (which beliefs would change, by how much, affecting which downstream inferences), and estimate the tractability of resolution (literature-resolvable, analysis-resolvable, experiment-resolvable).

### Zone 4: The Uncharted Exterior

Regions signaled by QA failures — queries that cannot be classified, questions that fall through all handlers to the ARBITRARY fallback, follow-up chains that terminate in "I don't know" without being able to articulate what *kind* of knowledge is missing. The system doesn't know what it doesn't know. These are not well-formed gaps; they are absences.

**Example**: A user asks "How does the smell of a building affect trust in its occupants?" The system has no beliefs about olfaction-trust interactions, no templates covering it, no theories that predict it. It cannot even formulate the gap precisely because it lacks the vocabulary — "olfactory-social trust mediation" is not a concept in its current ontology.

**Characteristic**: The system can recognize that it has encountered something outside its scope, but cannot articulate the structure of what's missing. Moving from Zone 4 to Zone 3 (charting the uncharted) requires conceptual expansion — adding new terms, new question types, or new theoretical frameworks.

---

## 3. The Endogenous Value Landscape

The critical innovation of the Interpretation Space is that it computes the value of potential knowledge acquisitions *from the inside* — from the structure of the EN itself, not from external demand.

### 3.1 The question-type operators

The QA system's 20+ question types are not just classification categories — they are *epistemic operators* that, when applied to a belief, generate specific kinds of follow-up questions. For any belief B in the EN, we can systematically apply:

| Operator | Question generated | What it probes |
|----------|-------------------|----------------|
| MECHANISM | "How does B work?" | Warrant completeness — is the causal chain from antecedent to consequent fully specified? |
| VALIDATION | "How strong is the evidence for B?" | Credence grounding — is the credence justified by the evidence base, or is it inherited/inferred? |
| BOUNDARY | "When does B fail?" | Scope specification — are the boundary conditions of B characterized? |
| DIRECTION | "Is the effect positive or negative?" | Sign certainty — for claims with EMPIRICAL_ASSOCIATION warrants, is the direction well-established? |
| COMPARISON | "How does B relate to B'?" | Coherence — do related beliefs form a consistent picture, or are there tensions? |
| SURPRISE | "What's counterintuitive about B?" | Informativeness — does B violate expectations, and if so, is the violation explained? |
| CROSS_DOMAIN | "Does B connect to other fields?" | Scope expansion — are there lateral connections that would enrich the web? |
| EFFECT_SIZE | "How big is the effect?" | Quantification — is B merely directional or properly quantified? |
| DESIGN_GUIDANCE | "What should a designer do with B?" | Actionability — can B be translated into design recommendations? |
| FRONTIER | "What don't we know about B?" | Self-awareness — can the system articulate its own ignorance about B? |

### 3.2 Self-interrogation as exploration

The key procedure is this: for each belief B in the EN (or a prioritized subset), the system applies each question-type operator, generates the corresponding question, routes it through the QA system, and evaluates the quality of its own answer. Quality is measured by:

- **Completeness**: Did the answer address the question, or did it fall back to a partial or empty response?
- **Groundedness**: Is the answer supported by specific beliefs with traceable warrants, or is it generated from pattern-matching and templates?
- **Coherence**: Is the answer consistent with related beliefs, or does it expose tensions?
- **Quantification**: Does the answer include specific numbers (effect sizes, thresholds, confidence intervals), or only qualitative claims?
- **Follow-up richness**: Does the answer generate rich, substantive follow-ups, or only mechanical template-based ones?

A belief B for which all operators produce high-quality answers is in Zone 1 (known interior). A belief for which some operators produce weak answers is in Zone 2 (active boundary). A belief for which most operators produce weak answers, but the weaknesses can be articulated as specific gaps, is in Zone 3 (identified periphery). If the operators don't even produce coherent questions, B is at the edge of Zone 4.

### 3.3 The value function

The endogenous value of resolving a gap G at the periphery is:

**V(G) = Structural_Impact(G) × Tractability(G) × Coherence_Tension(G)**

where:

**Structural_Impact(G)** measures how much the web of belief would change if G were resolved. This is the existing VOI computation — counterfactual coherence analysis. If resolving G would change the credence of many downstream beliefs, the structural impact is high. Computed by the existing `voi_search.py` using the gap predictor's counterfactual analysis.

**Tractability(G)** estimates how easy G is to resolve, inferred from the warrant structure of surrounding beliefs and the gap type:

| Gap Type | Tractability Signal | Typical Resolution Path |
|----------|-------------------|------------------------|
| MECHANISM gap between two MECHANISM-warranted beliefs | HIGH — surrounding structure constrains the answer | Literature search for intermediate mechanism |
| BOUNDARY gap for an EMPIRICAL_ASSOCIATION-warranted belief | MODERATE — empirical question, studies may exist | Targeted literature search for boundary studies |
| VALIDATION gap for a THEORY_DERIVED belief | MODERATE — need empirical test of theoretical prediction | Search for experimental studies |
| DIRECTION gap for a belief with conflicting evidence | MODERATE-HIGH — evidence exists but disagrees | Meta-analytic resolution or moderator analysis |
| MECHANISM gap in a region of ANALOGICAL warrants | LOW — little structural constraint on the answer | May require novel theorizing or experiments |
| Any gap in Zone 4 (uncharted) | VERY LOW — question not yet well-formed | Requires conceptual expansion before evidence search |

**Coherence_Tension(G)** measures whether G sits at a point of active tension in the web — where existing beliefs push in different directions, or where an unresolved argumentation attack creates instability. High tension means resolving G would settle a dispute and stabilize the web; low tension means G is merely an absence, not a contradiction. This is computed from the argumentation graph: unresolved attacks of severity > 0.3 within two hops of G's location indicate high tension.

The product V(G) gives a single scalar that ranks gaps by their expected *epistemic return on investment* — not by how interesting they are to some arbitrary set of users, but by how much they would improve the coherence, completeness, and reliability of the web of belief itself.

### 3.4 Why this is different from demand-driven VOI

The standard approach to information valuation in deployed systems is demand-driven: observe what users ask about, notice where the system gives weak answers, and prioritize acquisition accordingly. This is useful but has a fundamental limitation: it samples the periphery according to the *distribution of user interests*, which is arbitrary with respect to the epistemic structure. If no user happens to ask about olfactory-trust mediation, the demand-driven system never notices that gap — even if resolving it would reshape multiple belief clusters.

The endogenous approach samples the periphery according to the *distribution of epistemic weakness*, which is a property of the web itself. The question-type operators are applied uniformly across the belief space, so every belief gets probed, every gap gets identified, and the value landscape reflects the structure of knowledge rather than the structure of demand.

This distinction matters most for what we might call *silent gaps* — regions where the system's incompleteness is invisible to users because they don't think to ask. A user asking about biophilia will get a reasonable answer and never learn that the system has no account of olfactory-biophilic interactions. But the self-interrogation procedure, applying the CROSS_DOMAIN operator to biophilia beliefs, would immediately surface the question "Does biophilia extend to olfactory channels?" and rate the answer quality as low — mapping a boundary point that no user has probed.

---

## 4. Probatory Rule Sets and Epistemic Closure

### 4.1 The Interpretation Space as an extension of the web of belief

The Interpretation Space is not merely a monitoring overlay on the web of belief — it is an *extension* of the web itself. The standard web of belief (Quine & Ullian, 1970, 1978) assumes that beliefs are related by entailment, though Quine was deliberately vague about what "entailment" means in practice. In formal epistemic logic, one might use Hintikka's (1962) belief logic, where the operator **B**φ ("the agent believes φ") is governed by axioms like closure under known implication (if Bφ and B(φ→ψ), then Bψ). But ATLAS does not use belief logic and should not. The relationships between beliefs in ATLAS are not deductive entailments; they are *probatory connections* — relations that bear on the evidential status, warrant strength, mechanistic grounding, or argumentative vulnerability of claims.

This observation leads to a fundamental reframing: instead of talking about beliefs and their logical entailments, we should talk about beliefs and the *probatory rules* that connect them. These are the rules under which beliefs support, challenge, extend, or demand elaboration of other beliefs. They are inference rules of a sort, but they operate in a different space from deductive or even probabilistic inference. They are closer to what Toulmin (1958) called "warrants" — the backing that makes an inference legitimate — but generalized to a full set of heterogeneous rule types with well-defined opening and closing conditions.

The crucial consequence: we can talk about *closure* under different probatory rule sets. A set of beliefs is closed under a rule set R when applying any rule in R to any belief in the set either produces a result already in the set (the rule is satisfied) or generates an explicitly tracked gap (the rule has been applied but its demands are not yet met). Different rule sets produce different closures, and different users/purposes require different closures. This gives us a principled vocabulary for adequacy: a knowledge base is adequate *for purpose P* when it is closed under the rule sets that P demands.

### 4.2 The four probatory rule sets

ATLAS currently embeds four distinct rule sets, though until now they have been implicit rather than formalized.

#### Rule Set R₁: Argumentation Rules

**Source**: Walton's (1996) argumentation schemes, as implemented in `argumentation_graph.py`. Five schemes currently operational: argument from expert opinion, argument from sign, argument from cause to effect, argument from analogy, argument from correlation to cause.

**Nature**: Each scheme is a defeasible inference pattern with associated *critical questions*. The scheme licenses the inference; the critical questions probe whether the license holds in this case.

**Opening condition**: A belief B is supported by an argument matching one of the five schemes. The scheme is *opened* when the argument is constructed — i.e., when an extraction or integration step creates an argument linking premises to conclusion via one of the recognized schemes.

**Closing conditions** (per scheme):

| Scheme | Critical Questions | Closure Requires |
|--------|-------------------|------------------|
| Expert opinion | (1) Is the source credible? (2) Is claim in domain? (3) Do peers agree? (4) Is evidence consistent? | All 4 CQs answered with evidence or explicitly deferred with justification |
| Sign | (1) How strong is the correlation? (2) Are there counter-signs? | Effect size quantified + no unresolved contradictory findings |
| Cause to effect | (1) Is there a credible mechanism? (2) Was cause present? (3) Were other causes excluded? | Mechanism at how-plausibly level + intervention or quasi-experimental evidence |
| Analogy | (1) Are the cases truly similar? (2) Are there relevant differences? | Similarity dimensions explicitly listed + disanalogies checked |
| Correlation to cause | (1) Is there a third factor? (2) Is the direction correct? (3) Is there a plausible mechanism? | Confound analysis + temporal precedence + mechanism sketch |

**Success condition for R₁-closure**: For every argument in the EN instantiating a recognized scheme, all critical questions are either (a) answered with traceable evidence (warrant type + source), or (b) explicitly deferred with a recorded gap in the VOI system.

**Metric**: Percentage of arguments with all CQs addressed. Target: ≥ 80% for Zone 1 beliefs, ≥ 50% for Zone 2, ≥ 0% for Zone 3 (gaps are expected here).

#### Rule Set R₂: Warrant Rules

**Source**: The ATLAS warrant taxonomy (EMPIRICAL_ASSOCIATION, THEORY_DERIVED, EXPERT_CONSENSUS, MECHANISM, CONSTITUTIVE, ANALOGICAL, LOGICAL_ENTAILMENT).

**Nature**: Each warrant type has *type-specific adequacy conditions* — what it takes for a belief warranted by that type to be considered well-supported. These are not logical inference rules but evidential sufficiency standards.

**Opening condition**: A belief B has a warrant of a recognized type. The warrant is *opened* when evidence is linked to the belief during extraction or integration.

**Closing conditions** (per warrant type):

| Warrant Type | Closing Conditions |
|-------------|-------------------|
| EMPIRICAL_ASSOCIATION | (1) At least one replication OR meta-analysis; (2) effect size quantified with CI; (3) mechanism at least how-possibly specified; (4) at least one boundary condition tested; (5) sample size ≥ 100 cumulative or 3+ independent samples |
| THEORY_DERIVED | (1) Derivation made explicit (which theory, which premises, which auxiliary assumptions); (2) at least one direct empirical test; (3) competing theoretical derivations noted if they exist |
| EXPERT_CONSENSUS | (1) Source identified (which panel, which experts, when); (2) degree of consensus quantified; (3) checked against empirical evidence where available |
| MECHANISM | (1) Mechanism specified at how-plausibly level (Craver 2007) with at least 2 steps in the chain; (2) each step supported by evidence (neural, cognitive, perceptual, or behavioral); (3) boundary conditions of the mechanism identified |
| CONSTITUTIVE | (1) Definitional relationship made explicit; (2) no hidden empirical assumptions buried in the definition |
| ANALOGICAL | (1) Source and target of analogy explicit; (2) relevant similarities enumerated; (3) disanalogies acknowledged and assessed for threat; (4) independent evidence for the target domain exists |
| LOGICAL_ENTAILMENT | (1) Premises stated; (2) inference valid; (3) premises have their own warrant chains |

**Success condition for R₂-closure**: For every warranted belief in the EN, the warrant's type-specific closing conditions are met or the unmet conditions are tracked as explicit gaps.

**Metric**: For each warrant type, percentage of instances meeting all closing conditions. Weighted aggregate across all beliefs gives the "warrant maturity score."

#### Rule Set R₃: Mechanism Rules

**Source**: The T1.5/T2 theory reduction framework, building on Craver (2007), Bechtel & Abrahamsen (2005), and the ATLAS maturity ladder (how-possibly → how-plausibly → how-actually).

**Nature**: Rules governing when a proposed causal mechanism adequately explains a phenomenon. These overlap with R₂'s MECHANISM warrant conditions but apply more broadly — any causal claim, regardless of warrant type, is subject to mechanism rules.

**Opening condition**: A belief B asserts a causal relationship (direction ∈ {increase, decrease}) between an environmental antecedent and a human outcome.

**Closing conditions**:

| Maturity Level | Requirements | Evidence Standard |
|---------------|--------------|-------------------|
| how-possibly | (1) At least one plausible mechanism sketched; (2) mechanism consistent with known neuroscience/psychology; (3) no known fatal objections | Literature-consistent; no direct evidence required |
| how-plausibly | (1) Mechanism specified with ≥ 2 steps; (2) each step has independent evidence; (3) the chain as a whole is consistent with the observed effect size and direction; (4) competing mechanisms acknowledged | Direct evidence for most steps; quantitative consistency |
| how-actually | (1) Mechanism tested via intervention or dissociation; (2) mediator(s) measured; (3) alternative mechanisms ruled out by evidence; (4) mechanism accounts for known boundary conditions | Experimental or quasi-experimental evidence for the mechanism itself |

**Additional rules within R₃**:
- **Theory linkage**: Every mechanism must be linked to at least one T1 framework (PP, EC, NM, DP, DT, IC, IE-DPT, SN, ER, AX) or the linkage gap must be explicit.
- **Molecule linkage**: Every mechanism should map to at least one rasa attractor molecule or the mapping gap must be noted.
- **Reductive coherence**: If a T1.5 theory claims to reduce to T1 frameworks, the reduction must be explicit — which constructs map to which framework components, with what percentage allocation.

**Success condition for R₃-closure**: For every causal belief in the EN, the mechanism is specified at the how-plausibly level or higher, with theory and molecule linkages, or all missing elements are tracked as gaps.

**Metric**: Distribution of mechanism maturity across causal beliefs. Target: ≥ 60% at how-plausibly, ≤ 10% with no mechanism at all.

#### Rule Set R₄: Interpretation Rules

**Source**: The 10 question-type operators defined in §3.1 of this spec, derived from the QA system's question taxonomy.

**Nature**: These are the most distinctive of the four rule sets. They are not traditional inference rules (they don't derive new beliefs from old ones) and not just evidential standards (they don't just check sufficiency). They are *epistemic probes* — operators that, when applied to a belief, either confirm that a particular dimension of understanding is adequate or generate a specific demand for further knowledge. They are the rules that govern *interpretive completeness* — whether the system can not merely state a fact but explain it, contextualize it, quantify it, and act on it.

**Opening condition**: Any belief in the EN. All 10 operators apply to all beliefs (though some operators are more informative for certain belief types — EFFECT_SIZE is most relevant for empirical beliefs, MECHANISM for causal claims, CROSS_DOMAIN for theoretical propositions).

**Closing conditions** (per operator):

| Operator | Closed When |
|----------|------------|
| MECHANISM | QA produces answer with groundedness ≥ 0.7 and the mechanism chain has ≥ 2 steps with evidence |
| VALIDATION | QA identifies ≥ 2 independent evidence sources with traceable warrants |
| BOUNDARY | QA identifies ≥ 1 tested boundary condition and ≥ 1 untested boundary (honesty about limits) |
| DIRECTION | Direction is one of {increase, decrease, no_effect, mixed} with consistent evidence |
| COMPARISON | QA can articulate how this belief relates to ≥ 2 other beliefs with explicit coherence assessment |
| SURPRISE | If the finding is counterintuitive (A9 annotation), the surprise is explained mechanistically |
| CROSS_DOMAIN | QA can identify ≥ 1 connection to a different T1 framework or discipline |
| EFFECT_SIZE | A quantitative effect size is reported with units and confidence interval or range |
| DESIGN_GUIDANCE | QA can produce ≥ 1 specific, actionable design recommendation with conditions |
| FRONTIER | QA can articulate ≥ 1 open question about this belief that is not already tracked in VOI |

**Success condition for R₄-closure**: For a given belief, all 10 operators have been applied and either meet their closing condition or have their unmet condition recorded as a gap.

**Metric**: Mean operator closure rate across beliefs. Full R₄-closure across the EN would mean the system can comprehensively interpret every belief it holds — explain it, validate it, contextualize it, quantify it, apply it, and identify what remains unknown about it.

### 4.3 Closure, partial closure, and purpose-relative adequacy

Full closure under all four rule sets simultaneously — Cl(W, R₁ ∩ R₂ ∩ R₃ ∩ R₄) — is an ideal that no finite knowledge system will achieve. It corresponds to a complete interpretation of the domain: every argument defended, every warrant satisfied, every mechanism specified, every belief fully probed. This is the asymptotic target, not a realistic goal.

What matters in practice is *partial closure relative to purpose*. Different users and different contexts require different closures:

| Purpose | Required Rule Sets | Adequate Closure Level |
|---------|-------------------|----------------------|
| Architect selecting materials | R₂ (warrant: is there evidence?) + R₄-EFFECT_SIZE + R₄-DESIGN_GUIDANCE | ≥ 70% on required operators |
| Researcher writing grant | R₃ (mechanism: where are the gaps?) + R₄-FRONTIER + R₄-MECHANISM | ≥ 50% (gaps are the point) |
| Student learning about biophilia | R₄-MECHANISM + R₄-COMPARISON + R₄-SURPRISE | ≥ 60% for engaging explanation |
| System health assessment (AESHI) | R₁ (argumentation integrity) + R₂ (warrant maturity) | ≥ 80% for GREEN status |
| Paper reviewer evaluating claims | R₁ + R₂ + R₃ at high thresholds | ≥ 90% for critical claims |
| Discovery/VOI computation | R₃ (mechanism gaps) + R₄-FRONTIER | Explicitly seeking *failures* of closure |

This gives us a formal definition of *adequacy relative to purpose*: the system is adequate for purpose P when it achieves the required closure level on the rule sets that P demands. The QA system, when receiving a query, can now check: "What purpose does this query serve? Which rule sets define adequacy for that purpose? Is the relevant belief closed under those rules? If not, the gaps become either caveats in the answer or suggested follow-ups."

### 4.4 Formalization: closure operators and the interpretation lattice

Let **W** denote the web of belief — the set of all beliefs with their credences, warrants, argumentation structure, and mechanism specifications.

For each rule set Rᵢ (i = 1, 2, 3, 4), define the *closure operator*:

**Cl(W, Rᵢ)** = W ∪ { all gaps generated by applying rules in Rᵢ to beliefs in W }

A gap G ∈ Cl(W, Rᵢ) \ W represents a demand that Rᵢ makes on W that W does not currently satisfy. The set of such gaps is the *residual* of W under Rᵢ:

**Res(W, Rᵢ)** = Cl(W, Rᵢ) \ W

The *interpretation space* at any moment is then characterized by the four residuals:

- **Res(W, R₁)**: Unanswered critical questions (argumentation gaps)
- **Res(W, R₂)**: Unmet warrant adequacy conditions (evidential gaps)
- **Res(W, R₃)**: Missing or immature mechanisms (explanatory gaps)
- **Res(W, R₄)**: Failed interpretation probes (understanding gaps)

The four zones map onto these residuals as follows:

- **Zone 1 (Known Interior)**: Beliefs where Res(W, Rᵢ) is empty for all relevant Rᵢ — fully closed under all applicable rules.
- **Zone 2 (Active Boundary)**: Beliefs where Res(W, Rᵢ) is non-empty for some Rᵢ but the residual elements are small and well-characterized.
- **Zone 3 (Identified Periphery)**: The gaps themselves — elements of Res(W, Rᵢ) that are well-formed demands for further knowledge.
- **Zone 4 (Uncharted Exterior)**: Regions where the rules cannot even be applied because the system lacks the conceptual vocabulary — the operators fail to produce coherent questions.

The endogenous value function V(G) now has a sharper definition: for a gap G that appears in multiple residuals, its value is higher because it represents a *convergent demand* from multiple epistemic dimensions. Formally:

**V(G) = Σᵢ wᵢ · Impact(G, Rᵢ) × Tractability(G) × |{j : G ∈ Res(W, Rⱼ)}|**

where wᵢ weights the rule sets (possibly purpose-dependent) and the final factor counts how many rule sets independently demand G's resolution. A gap that appears in the argumentation residual AND the mechanism residual AND the interpretation residual has triple the structural demand of one appearing in only a single residual.

### 4.5 Comparison to alternative logics of belief

It is worth situating this framework relative to established approaches in epistemic logic and belief revision, to make clear what we are and are not doing.

**Hintikka's epistemic logic** (Hintikka, 1962, *Knowledge and Belief*): Hintikka formalized knowledge and belief using modal operators K and B with possible-worlds semantics. The agent knows φ (Kφ) iff φ is true in all epistemically accessible worlds. This is elegant but unsuitable for ATLAS for three reasons: (1) it assumes logical omniscience (the agent believes all logical consequences of its beliefs), which is computationally unrealistic; (2) it treats knowledge as a binary predicate, whereas ATLAS works with graded credences; (3) it provides no account of *warrants* — why a belief is held — only that it is held. Our probatory rules are explicitly about the *reasons* for beliefs, not just their truth conditions.

**AGM belief revision** (Alchourrón, Gärdenfels & Makinson, 1985): AGM provides axioms for how a belief set should change when new information arrives (expansion, contraction, revision). It is closer to our framework but still operates with a binary notion of belief (in the set or not) and its revision operators are purely logical. Our rule sets are *heterogeneous* — argumentation rules work differently from mechanism rules, which work differently from interpretation probes — and our closure conditions are domain-sensitive, not purely formal.

**Dung's argumentation frameworks** (Dung, 1995): Dung's abstract argumentation framework defines notions like "acceptable" and "grounded" extensions based on attack relations between arguments. Our R₁ (argumentation rules) is closest to Dung, but we extend it with the other three rule sets that address warrant adequacy, mechanism specification, and interpretive completeness — dimensions that Dung's framework does not address.

**Pollock's defeasible reasoning** (Pollock, 1995): Pollock's system of *prima facie* and *conclusive* reasons, with *rebutting* and *undercutting* defeaters, provides a richer framework for defeasible inference than Dung's abstract attacks. Our warrant closing conditions can be read as Pollock-style conditions for when prima facie reasons become sufficiently strong to resist defeaters. But we add mechanism rules and interpretation probes that go beyond Pollock's purely logical account.

What distinguishes our approach from all of these is the *heterogeneity* of the rule sets and their *opening and closing conditions*. We are not trying to capture belief dynamics in a single formal system. We are recognizing that scientific epistemology involves multiple, qualitatively different kinds of evidential connections, each with its own standards of adequacy. The probatory rules formalize these different kinds of connections, and closure under different subsets of rules captures different notions of epistemic adequacy. This is a pragmatist move in the spirit of both Quine and Dewey: the criteria for adequate knowledge depend on the purpose for which the knowledge is being used.

### 4.6 Connections to closure in mathematics and logic

The term "closure" is used deliberately. In mathematics, a set is closed under an operation when applying the operation to elements of the set always yields elements still in the set. In deductive logic, a theory is closed under consequence when all logical consequences of the theory are in the theory. Our usage generalizes this: a web of belief is closed under a probatory rule set when applying any rule to any belief either yields a condition that is already satisfied or generates an explicitly tracked gap. The gaps are the "residuals" — the elements that would need to be added to achieve closure.

This gives us a hierarchy of closure conditions, forming a lattice:

- Cl(W, ∅) = W (trivial closure — no rules applied)
- Cl(W, R₁) = W ∪ Res(W, R₁) (argumentation closure)
- Cl(W, R₂) = W ∪ Res(W, R₂) (warrant closure)
- Cl(W, R₃) = W ∪ Res(W, R₃) (mechanism closure)
- Cl(W, R₄) = W ∪ Res(W, R₄) (interpretation closure)
- Cl(W, Rᵢ ∪ Rⱼ) = closure under both rule sets simultaneously
- ...
- Cl(W, R₁ ∪ R₂ ∪ R₃ ∪ R₄) = full epistemic closure (the ideal)

The residual Res(W, Rᵢ ∪ Rⱼ) may be larger than Res(W, Rᵢ) ∪ Res(W, Rⱼ) because the interaction of two rule sets can generate demands that neither generates alone. For instance, a belief might satisfy R₂ (warrant adequate) and R₃ (mechanism adequate) individually, but the combination reveals a tension: the mechanism predicts a larger effect than the warrant evidence supports. The R₂+R₃ residual includes this coherence gap even though neither residual alone does.

This interactive property is epistemically significant: it means that achieving closure under multiple rule sets simultaneously is *harder* than achieving closure under each separately, and the *additional* gaps revealed by combining rule sets are often the most interesting — they represent deep structural tensions in the web of belief.

### 4.7 Question-Formulation Norms and Success Conditions

The probatory rule sets (§4.2) specify *when* to open a question and *when* to close it. The science writer principles (§7) specify *how* to compose answers. But neither addresses the intermediate problem: *how to formulate a good question* — one whose answer would actually advance epistemic closure. This section codifies question-formulation norms (Q-norms) that govern the behavior of the 10 R₄ operators, drawing on the epistemology of questions (erotetic logic), the science communication norms from Sagan, Sacks, Sapolsky, Yong, Pinker, Roach, and Gawande, and the operational success conditions that every norm must satisfy.

**Why this matters**: A poorly formulated question wastes computational resources, generates vacuous answers, and creates the illusion of interrogation without actual epistemic progress. The system can generate fluent questions as easily as fluent answers — and fluent questions are just as dangerous as fluent answers if they lack epistemic grip. The Q-norms ensure that every question the system generates is (a) well-presupposed, (b) contrast-specified, (c) level-appropriate, (d) answerable in principle, and (e) valuable if answered.

#### 4.7.1 The seven question-formulation norms

**Q1: Warrant Your Presuppositions (Hintikka)**

Every question presupposes that certain things are true. "Why does daylight reduce stress?" presupposes that daylight *does* reduce stress. The Hintikka norm requires that every presupposition of a question be checked against the web of belief before the question is posed. If the presupposition has credence below 0.5 or warrant status DEFEATED or UNGROUNDED, the question must be reformulated — typically by replacing the why-question with a whether-question.

This is drawn from Hintikka's interrogative model of inquiry (Hintikka, 1999, *Inquiry as Inquiry*, Cambridge University Press; ~2,800 citations), which models inquiry as a game between the inquirer and an oracle, where questions are moves whose legitimacy depends on the current state of the inquirer's information.

| Presupposition Check | Action |
|---------------------|--------|
| Presupposition warranted (credence ≥ 0.5, WARRANTED) | Proceed with question as formulated |
| Presupposition weakly warranted (0.3–0.5, TENTATIVE) | Reformulate: "Is it the case that X?" rather than "Why does X?" |
| Presupposition unwarranted (< 0.3, DEFEATED) | Do not pose the question; instead open a gap on the presupposition itself |
| Presupposition untested | Pose a whether-question first; queue the original question conditionally |

**Success condition for Q1**: SC-Q1: ≥ 95% of questions generated by R₄ operators have all presuppositions verified against the web of belief (warrant_status ≠ DEFEATED). Test: sample 100 generated questions, check presupposition warrant status. Failure mode: system asks "Why does X improve Y?" when X→Y is DEFEATED.

**Q2: Specify the Contrast Class (Bromberger / van Fraassen)**

Every why-question and how-question has an implicit contrast class — a set of alternatives that the answer must distinguish among. "Why does daylight reduce stress?" is ambiguous until the contrast class is specified: "Why daylight rather than full-spectrum artificial light of equal intensity?" vs. "Why daylight rather than dim artificial light?" These are different questions with different answers, because the first isolates the spectral-composition factor while the second confounds intensity with spectrum.

This is drawn from Bromberger (1966, "Why-questions," in *Mind and Cosmos*, University of Pittsburgh Press; ~650 citations) and van Fraassen (1980, *The Scientific Image*, Oxford University Press; ~11,000 citations), who argued that the pragmatics of explanation are determined by the contrast class, not the explanandum alone.

The Q2 norm requires every MECHANISM, COMPARISON, BOUNDARY, and DIRECTION question to include an explicit contrast. The system must generate the contrast from the web of belief — for instance, by identifying beliefs with the same consequent but different antecedents, or the same antecedent but different scope conditions.

| Operator | Default Contrast Strategy |
|----------|-------------------------|
| MECHANISM | "Through what process X rather than alternative process Y?" (Y = next-most-cited mechanism for this IV→DV) |
| COMPARISON | "Why does X produce a larger effect than Y?" (Y = closest comparator in the web) |
| BOUNDARY | "Under what conditions does the effect fail?" (contrast: scope where effect holds vs. untested scope) |
| DIRECTION | "Why does the evidence point toward increase rather than decrease?" (contrast: contradicting studies) |
| SURPRISE | "Why is the actual finding Z rather than the expected finding W?" (contrast: common assumption vs. data) |

**Success condition for Q2**: SC-Q2: ≥ 80% of MECHANISM/COMPARISON/BOUNDARY/DIRECTION questions include an explicit contrast class drawn from the web of belief. Test: sample 50 questions per operator, check for contrast specification. Failure mode: "Why does noise affect cognition?" (no contrast) rather than "Why does unpredictable noise impair focused attention while continuous moderate noise does not?" (contrastive).

**Q3: Classify the Problem Type (Laudan)**

Not all gaps are the same kind of gap. Laudan (1977, *Progress and Its Problems*, University of California Press; ~4,200 citations) distinguished empirical problems (what happens under what conditions?) from conceptual problems (does this theory cohere internally and with neighboring theories?). A question targeting an empirical gap requires a different answer — and different evidence — than a question targeting a conceptual gap.

The Q3 norm requires every generated question to be classified as one of:

| Problem Type | Example | What Counts as a Good Answer | Closure Rule Set |
|-------------|---------|------------------------------|-----------------|
| EMPIRICAL_GAP | "Does daylight reduce stress in healthcare settings?" | New data, or reanalysis of existing data with scope extension | R₂ (warrant) + R₃ (mechanism) |
| CONCEPTUAL_GAP | "Is ART compatible with predictive processing accounts of restoration?" | Theoretical argument showing compatibility or incompatibility | R₁ (argumentation) + R₃ (mechanism) |
| METHODOLOGICAL_GAP | "How should we measure 'restoration' — self-report, cortisol, or EEG?" | Instrument comparison, validity evidence | R₂ (warrant) |
| BRIDGING_GAP | "How does the lighting-circadian finding connect to the biophilia-stress finding?" | Cross-domain mechanism or shared theoretical grounding | R₃ (mechanism) + R₄ (interpretation) |

**Success condition for Q3**: SC-Q3: 100% of generated questions carry a problem_type label. ≥ 85% agreement between automatic classification and expert judgment on a 50-question sample. Failure mode: treating a conceptual gap as if new data would close it (e.g., running more experiments on ART vs. PP compatibility when what's needed is theoretical analysis).

**Q4: Estimate the Value Before Asking (Simon)**

Not all questions are worth asking. The Simon norm requires that every generated question carry a VOI estimate *before* the system attempts to answer it, and that questions below a minimum VOI threshold be deferred rather than pursued.

This is the computational operationalization of Simon's (1956, "Rational choice and the structure of the environment," *Psychological Review*; ~5,000 citations) bounded rationality: cognitive resources are finite, so inquiry must be prioritized. The value estimate combines three factors already defined in §3.3:

V_prior(Q) = structural_impact(Q) × tractability(Q) × |{rule sets generating Q}|

If V_prior(Q) < θ_VOI (default: 0.15), the question is logged but not pursued. If V_prior(Q) ≥ θ_VOI, the question enters the interrogation queue ordered by V_prior.

The key insight from the science communication literature: Gawande's norm ("name the gap") applies here too — every deferred question should still be *recorded* as a named gap, because naming a gap you chose not to pursue is epistemically valuable even if pursuing it isn't cost-effective right now. The gap registry (Zone 3) contains both pursued and deferred questions, distinguished by their VOI scores.

**Success condition for Q4**: SC-Q4: All generated questions carry a V_prior estimate. ≥ 70% of questions with V_prior ≥ 0.5 produce answers that change at least one zone classification when pursued. ≤ 20% of questions with V_prior < 0.15 would have changed a zone classification if pursued (checked on a deferred sample of 30 questions). Failure mode: the system asks many low-value questions while high-value questions languish in the queue.

**Q5: Name What You Don't Know with Precision (Gawande Applied to Questions)**

Vague questions generate vague answers. "We don't understand the mechanism" is a gap statement but not a question. "We lack physiological stress measures for the daylight effect — all 4 studies use self-report" is a gap statement that immediately suggests a specific question ("Does daylight reduce cortisol, not just self-reported stress?") with a specific answer shape (a physiological measurement study in a daylight vs. control condition).

The Gawande norm for questions requires that every question generated by an R₄ operator specify:
- What *specifically* is unknown (not "the mechanism" but "the step between circadian entrainment and cortisol reduction")
- What *kind* of answer would close the gap (a study design, a theoretical argument, a reanalysis)
- What the *current best guess* is (so the question has a falsifiable anchor)

This maps to the A18 (UnansweredQuestion) annotation type in the extended annotations, which already has fields for `question`, `why_important`, `what_would_it_take`, and `estimated_difficulty`.

**Success condition for Q5**: SC-Q5: ≥ 90% of generated questions have all three Gawande specifics: (a) a non-vague target, (b) a specified answer shape, (c) a falsifiable current best guess. Test: expert rates 50 questions on a 3-point specificity scale per dimension. Mean ≥ 2.5/3. Failure mode: "What is the mechanism of biophilia?" (vague target, no answer shape, no best guess).

**Q6: Earn the Complexity of the Question (Yong Applied to Questions)**

Don't ask a cross-domain question until the within-domain picture is clear. Don't ask about moderators until the main effect is established. Don't ask about cultural variation until the baseline population is characterized. The Yong norm for questions imposes a *prerequisite structure* on the R₄ operators:

| Question Complexity Level | Prerequisite | Operators |
|--------------------------|-------------|-----------|
| L1: Main effect | None | VALIDATION, EFFECT_SIZE |
| L2: Mechanism | L1 established (main effect in Zone 1) | MECHANISM |
| L3: Boundaries | L1 established | BOUNDARY, COMPARISON |
| L4: Cross-domain | L2 established (mechanism in Zone 1 or 2) | CROSS_DOMAIN, SURPRISE |
| L5: Frontier | L3 established | FRONTIER, DESIGN_GUIDANCE, DIRECTION |

This prevents the system from generating intellectually exciting but premature questions. If the main effect of daylight on stress is still in Zone 2 (answer quality mediocre), the system should not be asking cross-domain questions about whether the same mechanism applies to thermal comfort. It should be asking L1/L2 questions to solidify the base.

**Success condition for Q6**: SC-Q6: ≥ 90% of generated questions satisfy their prerequisite: the belief/finding they interrogate has the required prerequisite in Zone 1 or Zone 2. Test: for each question, check that the prerequisite level is satisfied. Failure mode: asking "How does the daylight-circadian mechanism compare to the thermal-comfort mechanism?" when the daylight-circadian mechanism itself is still in Zone 3 (no good answer).

**Q7: Show the Seam in the Question Itself (Sapolsky Applied to Questions)**

The best questions are not "Does X work?" but "Under what conditions does X fail?" The Sapolsky norm for questions requires that when the system has evidence of a seam — conflicting results, precision differences, boundary violations, or undercutting defeaters — the question should be formulated to *target the seam* rather than the central tendency.

This connects directly to the A11 (Dispute) annotation type and to Cartwright's conflict typology (P10 in the epistemic principles). When the system detects a CONTRADICTS or BOUNDARY_VIOLATION conflict, the generated question should ask about the *boundary*, not the effect:

- Instead of: "Does noise affect cognitive performance?" (which has a mixed answer because it depends on noise type)
- Generate: "What distinguishes the noise types that impair cognition from those that don't? Is it predictability, spectral content, or semantic content?"

The seam-targeting norm is the most generative of the Q-norms: it turns areas of uncertainty from liabilities into research questions, which is exactly what good science communication does — making the mess interesting, as Sapolsky advocates.

**Success condition for Q7**: SC-Q7: When the web of belief contains a conflict (CONTRADICTS, WEAKENS, or BOUNDARY_VIOLATION) for a given IV→DV pair, ≥ 80% of generated questions about that pair target the conflict rather than asking about the main effect. Test: identify 30 IV→DV pairs with conflicts, check generated questions. Failure mode: asking "Does X affect Y?" when three studies say yes and two say no, rather than "What distinguishes the conditions where X affects Y from those where it doesn't?"

#### 4.7.2 The science communication norms applied to question generation

The 7 popular science writer norms from Part II of EPISTEMIC_PRINCIPLES.md (Principles 11–17) were designed for answer composition, but each has a question-generation counterpart:

| Writer Norm (Answer) | Question-Generation Counterpart | Implementation |
|---------------------|-------------------------------|----------------|
| P11 Sacks: Lead with the human | Generate questions anchored in human experience, not abstractions | DESIGN_GUIDANCE operator should always reference a user scenario: "When an architect designs X, what would happen if...?" |
| P12 Sagan: Give scale | Include magnitude expectations in the question | "Is the effect large enough to matter for a 30-person office?" not just "Is there an effect?" |
| P13 Sapolsky: Show the seam | → Q7 above | Target conflicts and boundaries |
| P14 Yong: Earn the complexity | → Q6 above | Prerequisite structure on question depth |
| P15 Gawande: Name the gap | → Q5 above | Specify what's unknown with precision |
| P16 Pinker: Make it falsifiable | Every question must have a falsifiable answer shape | "If ART is correct, then X should show Y. Does it?" — the question contains its own test |
| P17 Roach: Hook and door | Questions should themselves be hooks — create curiosity | A17 (NarrativeHook) should be generated alongside the question: "Here's something odd: plants reduce stress in 6 studies, but not in 3. What's different about those 3?" |

This mapping means the Q-norms and the science writer norms are not separate systems — they are the same principles applied at different phases of the epistemic cycle: question-formulation vs. answer-composition. The system should be as epistemically disciplined in asking as it is in answering.

#### 4.7.3 Success conditions for every system function

David's mandate: every function must have explicit, operational success conditions so we can test whether it meets its goal and to what degree. The following table extends the IS-SC conditions from §11 to cover all functions introduced in §4:

**Probatory Rule Set Functions**

| Function | Success Condition | Target | Test Method |
|----------|------------------|--------|-------------|
| R₁.open(belief) — generate argumentation gaps | SC-R1-OPEN: Generated gaps correspond to genuine Walton critical questions | ≥ 85% precision on 50-belief sample | Expert reviews whether each gap is a legitimate critical question |
| R₁.close(gap) — check if argumentation gap is resolved | SC-R1-CLOSE: Closed gaps do not reopen after new evidence | ≤ 5% reopening rate over 3 nightly cycles | Track gap status over time |
| R₂.open(belief) — generate warrant gaps | SC-R2-OPEN: Gaps correctly identify warrant deficiencies | ≥ 90% agreement with warrant_service.py output | Compare gap list to warrant audit |
| R₂.close(gap) — check warrant adequacy | SC-R2-CLOSE: Closed warrant gaps have warrant_status ≠ UNGROUNDED | 100% (hard gate) | Automated check |
| R₃.open(belief) — generate mechanism gaps | SC-R3-OPEN: Mechanism gaps correctly identify missing explanatory steps | ≥ 80% agreement with mechanism_chain completeness | Compare to template mechanism chains |
| R₃.close(gap) — check mechanism completeness | SC-R3-CLOSE: Closed mechanism gaps have mechanism_chain with ≥ 2 steps, all with evidence_strength ≠ "assumed" | ≥ 90% compliance | Automated check on mechanism_chain field |
| R₄.open(belief) — generate interpretation questions | SC-R4-OPEN: Questions pass all 7 Q-norms (Q1–Q7) | ≥ 80% composite Q-norm compliance | Automated Q-norm checker + expert sample |
| R₄.close(gap) — check answer quality | SC-R4-CLOSE: Answer quality rubric (5 dimensions) ≥ 0.6 on all dimensions | ≥ 70% of answers meet threshold | Automated rubric scoring |

**Closure Functions**

| Function | Success Condition | Target | Test Method |
|----------|------------------|--------|-------------|
| Cl(W, Rᵢ) — compute closure under rule set i | SC-CL-COMPLETE: All beliefs in W are probed by Rᵢ | 100% coverage | Count probed vs. total beliefs |
| Cl(W, Rᵢ) — residual computation | SC-CL-RESIDUAL: Residual set contains no false positives (gaps that are actually resolved) | ≤ 5% false positive rate | Expert reviews 30 residual items |
| Res(W, Rᵢ ∪ Rⱼ) — interactive residuals | SC-CL-INTERACT: Interactive residuals (gaps from combining rule sets) are detected | ≥ 50% of known tensions captured | Compare to expert-identified tensions |

**Value Function**

| Function | Success Condition | Target | Test Method |
|----------|------------------|--------|-------------|
| V(G) — gap value computation | SC-V-CORR: Correlation with expert ranking | Spearman ρ ≥ 0.6 | David ranks 30 gaps; compare to V(G) |
| V_prior(Q) — question value estimation | SC-V-PRED: High-V questions produce zone changes | ≥ 70% of V_prior ≥ 0.5 questions change ≥ 1 zone | Track zone changes post-interrogation |
| θ_VOI — value threshold | SC-V-THRESH: Threshold correctly separates productive from unproductive questions | AUC ≥ 0.75 for predicting zone change | ROC analysis on pursued vs. deferred questions |

**Question Generation Functions (Q-Norm Compliance)**

| Function | Success Condition | Target | Test Method |
|----------|------------------|--------|-------------|
| Q-norm composite | SC-Q-ALL: Generated questions satisfy all applicable Q-norms | ≥ 80% composite compliance | Automated checker + 50-question expert sample |
| Presupposition check (Q1) | SC-Q1: see above | ≥ 95% | Automated warrant check |
| Contrast class (Q2) | SC-Q2: see above | ≥ 80% | Automated + expert |
| Problem type (Q3) | SC-Q3: see above | 100% labeled, 85% correct | Automated label + expert validation |
| VOI pre-estimate (Q4) | SC-Q4: see above | 100% estimated, 70% predictive | Automated + longitudinal tracking |
| Gawande specificity (Q5) | SC-Q5: see above | ≥ 90% | Expert rating |
| Prerequisite check (Q6) | SC-Q6: see above | ≥ 90% | Automated prerequisite graph |
| Seam targeting (Q7) | SC-Q7: see above | ≥ 80% | Automated conflict detection + question analysis |

**Zone Classification Functions**

| Function | Success Condition | Target | Test Method |
|----------|------------------|--------|-------------|
| classify_zone(belief, operator_results) | SC-ZONE-ACC: Agreement with expert classification | ≥ 80% on 50-belief sample | David classifies; compare |
| reclassify_after_interrogation() | SC-ZONE-STABLE: Convergence within 5 rounds | < 5% reclassification by round 5 | Track reclassification rate |
| detect_zone_boundary() | SC-ZONE-BOUND: Boundary beliefs correctly identified | ≥ 75% recall of expert-identified boundary beliefs | Expert labels 30 boundary beliefs |

---

## 5. The Expanding Sphere

### 4.1 Recursive self-interrogation

The procedure is iterative. In each round:

1. **Select** a set of beliefs (initially the full EN, subsequently prioritized by previous rounds' boundary detections).
2. **Apply** question-type operators to generate questions.
3. **Route** questions through the QA system.
4. **Evaluate** answer quality (completeness, groundedness, coherence, quantification, follow-up richness).
5. **Classify** each belief into Zones 1–4 based on the answer quality profile.
6. **Compute** V(G) for all identified gaps (Zone 3 points).
7. **Generate follow-ups** for the weakest answers.
8. **Repeat** from step 3 with the follow-up questions.

Each round expands the interpretation sphere: beliefs that were in Zone 2 may move to Zone 1 (if the self-interrogation revealed that the system actually has strong answers) or to Zone 3 (if it revealed specific, articulable gaps). Zone 4 regions may move to Zone 3 as the system's vocabulary and question types become enriched by the process. The sphere grows outward from the known interior.

### 4.2 Convergence and the steady-state periphery

The process converges when the self-interrogation no longer changes zone classifications — every belief has been probed by every operator, the boundaries are stable, and the value landscape is characterized. At this point, the Interpretation Space is a complete map of what the system knows, what it doesn't know, and what it would be most valuable to find out next.

In practice, convergence is asymptotic: each round reduces the number of reclassifications, but the periphery is always expanding as follow-ups generate new questions that point to regions the system hasn't considered. The system never fully converges because the question-type operators, applied to newly identified gaps, generate second-order questions that themselves have peripheries.

This is not a bug; it is the correct epistemic behavior. A system that "converged" — that ran out of questions to ask itself — would be claiming completeness, which is incoherent for a Quinean web of belief. The expanding sphere is the computational expression of fallibilism: there is always more to learn, and the system can always articulate what it would be.

### 4.3 The value landscape as scientific strategy

The converged (or near-converged) value landscape V(G) over the identified periphery constitutes a *research agenda* — a prioritized list of questions, ranked by their expected return on investigative effort, derived entirely from the structure of existing knowledge. This is a formalization of what good scientists do intuitively: they look at what's known, identify where the tensions and gaps are, estimate which gaps are tractable, and focus their effort where the expected epistemic payoff is highest.

The crucial feature is that this research agenda is *endogenous* to the knowledge base. It does not depend on funding priorities, disciplinary fashions, or the idiosyncratic interests of individual researchers. It falls out of the epistemology. Different people might reasonably weight the three factors (structural impact, tractability, coherence tension) differently — a theorist might weight coherence tension highly, an experimentalist might weight tractability, an architect might weight downstream design implications — but the underlying value landscape is objective in the sense that it is computed from the beliefs and their structure, not from preferences about what to study.

---

## 6. Architecture

### 6.1 Components

The Interpretation Space requires three new components integrated with the existing ATLAS architecture:

**Component 1: The Self-Interrogator** (`src/interpretation/self_interrogator.py`)

Implements the recursive self-interrogation procedure. For a given belief or set of beliefs:

- Generates questions by applying question-type operators
- Routes questions through the existing QA system (reuses `arbitrary_qa_handler.py`, `qa_handlers.py`, `router.py`)
- Evaluates answer quality using a rubric (completeness, groundedness, coherence, quantification, follow-up richness)
- Classifies beliefs into Zones 1–4
- Generates follow-up questions for weak answers
- Records the full interrogation trace for audit and analysis

**Component 2: The Value Computer** (`src/interpretation/value_computer.py`)

Computes V(G) = Structural_Impact × Tractability × Coherence_Tension for all identified gaps:

- Structural_Impact: delegates to existing `voi_search.py` counterfactual analysis
- Tractability: inferred from warrant types of surrounding beliefs, gap type, and Zone classification
- Coherence_Tension: computed from argumentation graph (unresolved attacks within 2 hops)
- Maintains a ranked gap registry with V(G) scores, updated after each interrogation round

**Component 3: The Periphery Map** (`src/interpretation/periphery_map.py`)

Maintains the four-zone classification and its evolution over time:

- Zone assignment for every belief (updated per interrogation round)
- Boundary surface representation (which beliefs are adjacent to which zones)
- Historical trajectory (how beliefs have moved between zones as evidence accumulates)
- Visualization support (zone maps, value heatmaps, boundary evolution animations)
- Integration with QA follow-up generation (the three-slot triad draws from the periphery map)

### 6.2 Integration points

| Existing Component | Integration |
|-------------------|-------------|
| EN (web_of_belief.py) | Source of beliefs, credences, warrant chains for zone classification |
| Argumentation Graph | Source of attack/defense structure for coherence tension computation |
| VOI system (voi_search.py) | Source of structural impact scores; receives tractability-adjusted V(G) |
| Discovery Funnel (discovery_funnel.py) | Receives prioritized gap list from value computer; reports closure results back |
| QA system (arbitrary_qa_handler.py) | Used by self-interrogator as the evaluation engine; receives periphery data for follow-up generation |
| Reflex system (reflex_system.py) | Monitors interpretation space health (are zone classifications stable? is value computation converging?) |

### 6.3 Data model

```
InterpretationRecord:
  belief_id: str
  zone: Zone (1|2|3|4)
  zone_confidence: float (0-1)
  operator_results: Dict[QuestionType, AnswerQuality]
  gaps_identified: List[GapRecord]
  follow_ups_generated: List[str]
  interrogation_round: int
  timestamp: datetime

GapRecord:
  gap_id: str
  gap_type: GapType
  source_belief_id: str
  generated_by_operator: QuestionType
  question_text: str
  answer_quality: AnswerQuality
  structural_impact: float
  tractability: float
  coherence_tension: float
  value_score: float  # V(G)
  resolution_status: OPEN|SEARCHING|CLOSED|STALE

AnswerQuality:
  completeness: float (0-1)
  groundedness: float (0-1)
  coherence: float (0-1)
  quantification: float (0-1)
  followup_richness: float (0-1)
  overall: float (0-1, weighted combination)

PeripherySnapshot:
  round: int
  timestamp: datetime
  zone_distribution: Dict[Zone, int]  # how many beliefs in each zone
  boundary_beliefs: List[str]  # beliefs at zone transitions
  top_gaps: List[GapRecord]  # highest V(G) gaps
  convergence_metric: float  # fraction of beliefs whose zone changed this round

ClosureProfile:
  belief_id: str
  r1_argumentation: {status: CLOSED|OPEN|N_A, open_cqs: List[str], closure_pct: float}
  r2_warrant: {status: CLOSED|OPEN|N_A, unmet_conditions: List[str], closure_pct: float}
  r3_mechanism: {status: CLOSED|OPEN|N_A, maturity: how-possibly|how-plausibly|how-actually|none, gaps: List[str]}
  r4_interpretation: {operator_results: Dict[Operator, CLOSED|OPEN], closure_pct: float}
  overall_closure: float  # weighted combination across applicable rule sets
  purpose_adequacy: Dict[Purpose, bool]  # is this belief adequate for each purpose?

ResidualRecord:
  rule_set: R1|R2|R3|R4
  gap_id: str
  source_belief_id: str
  condition_unmet: str  # specific closing condition that failed
  cross_residual: bool  # true if this gap appears in multiple rule sets' residuals
  convergent_demand_count: int  # how many rule sets independently demand this gap's resolution
```

---

## 7. The Science Writer Principles

The Interpretation Space changes what the QA system's science writer principles should be. In the earlier formulation, the principles governed how to compose answers for human readers. With the Interpretation Space, they also govern how the system *interrogates itself* — because the quality of self-interrogation depends on the quality of the questions asked and the standards by which answers are evaluated.

### 7.1 Principles for answer composition (human-facing)

1. **Lead with the phenomenon, not the theory.** Start with what the person would experience in the built environment, then explain the mechanism.
2. **Quantify whenever possible.** Effect sizes, thresholds, confidence intervals. "~15% improvement (Cohen's d ≈ 0.4)" over "helps."
3. **State the boundary conditions.** Every finding has scope. Where does it apply? Where does it fail? What moderators have been tested?
4. **Distinguish mechanism from correlation.** Make the warrant type explicit: is this a constitutive relationship, a well-characterized mechanism, an empirical association, or an analogy?
5. **Use surprise strategically.** When A9 annotations indicate a counterintuitive finding, lead with the surprise — it drives engagement and learning.
6. **Acknowledge what you don't know.** Every answer should include the frontier — what would change the answer if discovered. This is Zone 3 material surfaced in Zone 1/2 answers.
7. **Follow-ups should teach, not just branch.** The three follow-up questions (depth, breadth, actionability) should create a *trajectory* — a sequence that, if followed, builds structured understanding.

### 7.2 Principles for self-interrogation (system-facing)

1. **Apply all operators uniformly.** Don't skip operators because the answer seems obvious. Obvious answers that are actually ungrounded (high credence, low warrant strength) are the most dangerous.
2. **Grade answers honestly.** The self-evaluation rubric must not be lenient. A template-matched response with no specific evidence is not "grounded" even if it sounds confident.
3. **Follow the weakest signal.** When self-interrogation reveals a weak answer, pursue it with follow-ups before moving to the next belief. Depth before breadth in self-interrogation.
4. **Record everything.** Every question generated, every answer evaluated, every zone classification — the interrogation trace is itself a dataset about the system's epistemic state.
5. **Don't confuse fluency with knowledge.** The system can generate fluent answers about topics where it has no grounded beliefs. The quality rubric must penalize ungrounded fluency heavily.

---

## 8. Connection to QA Follow-Up Design

The Interpretation Space resolves the follow-up question design problem raised in earlier discussion. The three-slot triad (depth, breadth, actionability) was proposed as a heuristic. The Interpretation Space provides a principled basis:

**Depth slot**: Choose the question whose gap G has the highest coherence_tension among the claims in the current answer. This points the learner toward the most actively disputed or weakly warranted part of what they just read — where going deeper would be most intellectually productive.

**Breadth slot**: Choose the question that would move the learner from Zone 1 toward Zone 2 or Zone 3 — from well-known territory toward the boundary. This is the A15/CROSS_DOMAIN move: connecting what they know to something adjacent that they might not have considered. The Interpretation Space tells us which adjacent beliefs are in Zone 2 (interesting, partially known) vs. Zone 1 (well-known, less interesting to explore) vs. Zone 3 (gap, can't answer well — avoid for breadth suggestions).

**Actionability slot**: Choose the question that maximizes movement along the design-implication axis — from theoretical understanding toward specific, implementable recommendations. The value computer's tractability score helps here: suggest the actionable follow-up for which the system has the strongest evidence, so the learner gets a satisfying, concrete answer.

This means follow-up generation isn't heuristic — it's *informed by the periphery map*. The system knows the topology of its own knowledge and chooses follow-ups that guide the learner along the most productive path through that topology.

---

## 9. Philosophical Foundations

### 9.1 Quinean coherentism as computational epistemology

The Interpretation Space is the computational realization of a Quinean epistemology. Quine's "web of belief" metaphor (Quine & Ullian, 1970) holds that beliefs are not justified individually but as members of a web; revisions are evaluated by their impact on the whole structure. The EN already implements this at the level of individual beliefs. The Interpretation Space extends it to the meta-level: *knowledge about knowledge* — what we know, what we don't know, and what it would be worth knowing — is itself derived from the web's structure rather than imposed from outside.

The endogenous value function V(G) is the formalization of what Quine called "conservatism" and "simplicity" as revision criteria, enriched with tractability (which Quine didn't consider computationally, but which is essential for any system that must allocate finite resources to knowledge acquisition). The expanding sphere of interpretation is the dynamic process by which the web discovers its own boundaries — an ongoing reflective equilibrium, in Rawls' (1971) sense but applied to empirical knowledge rather than normative principles.

### 9.2 The relationship to Value of Information theory

Classical VOI theory (Howard, 1966; Raiffa & Schlaifer, 1961) computes the expected value of resolving uncertainty before making a decision. The ATLAS system has no single decision to make — it's a knowledge system, not a decision system. The Interpretation Space adapts VOI to the purely epistemic case: the "decision" is which question to ask next (or which evidence to acquire), and the "value" is measured in coherence improvement rather than utility.

This is what the system's panel review (Howard & Pearl) called "Expected Epistemic Gain" (EEG) — a reformulation of VOI for epistemological rather than decision-theoretic contexts. The Interpretation Space extends EEG by incorporating tractability and demand, yielding a more complete picture of expected return on investigative effort.

### 9.3 Active inference and the free energy principle

There is a suggestive parallel with Friston's (2010) free energy principle. The self-interrogation procedure can be understood as the knowledge system minimizing its *epistemic free energy* — the discrepancy between its model of the domain and the actual structure of that domain, as revealed by its own question-answering failures. Each round of self-interrogation reduces free energy by either: (a) revealing that the system knows more than it thought (Zone 2 → Zone 1), (b) converting vague ignorance into specific gaps (Zone 4 → Zone 3), or (c) informing acquisition priorities that will reduce uncertainty (Zone 3 → search → Zone 1). The expanding sphere is epistemic active inference: the system acts on its own knowledge base to reduce prediction error about what it knows and doesn't know.

This is not merely an analogy. The predictive processing (PP) framework, which is one of the ten T1 frameworks in ATLAS, applies to the system's own epistemic processing as much as to the environmental perception it models. The system generates predictions about its own answer quality (based on zone classifications), compares those predictions to actual answer quality (via self-interrogation), and updates its model (zone reclassification) to minimize the prediction error. The Interpretation Space is the system's model of its own epistemic state, and the self-interrogation procedure is the inference process that keeps that model calibrated.

---

## 10. Implementation Roadmap

### Phase 1: Self-Interrogation Pilot (1 week)

- Implement self-interrogator for a single question type (MECHANISM) across 50 beliefs
- Develop answer quality rubric (5 dimensions, 0-1 scale each)
- Classify pilot beliefs into Zones 1-4
- Validate zone classifications against human judgment (David reviews 20 classifications)
- Output: calibrated rubric, initial zone map for 50 beliefs

### Phase 2: Full Operator Suite (2 weeks)

- Extend self-interrogation to all 10 question-type operators
- Run full interrogation across the 4,888 belief corpus (or a stratified sample of 500)
- Compute V(G) for all identified gaps
- Compare endogenous V(G) rankings to existing VOI rankings from `voi_search.py`
- Output: complete zone map, value landscape, comparison analysis

### Phase 3: Recursive Follow-Up (1 week)

- Implement follow-up generation from weak answers
- Run 3 rounds of recursive self-interrogation
- Measure convergence (fraction of beliefs changing zone per round)
- Document the expanding sphere — how many new gaps were identified in each round?
- Output: convergence analysis, gap discovery curve

### Phase 4: Integration (2 weeks)

- Wire periphery map into QA follow-up generation (three-slot triad)
- Wire value landscape into VOI search (cost-adjusted gap prioritization)
- Wire zone classifications into browse interface (visual zone indicators)
- Add theory guide tooltips (from `docs/theory_guides/`) to Zone 2/3 boundary beliefs
- Output: integrated system with self-aware knowledge delivery

### Phase 5: Evaluation (1 week)

- Re-run QA panel evaluation (6 personas) with interpretation-space-informed follow-ups
- Compare to baseline 2.0/5 mean score
- Measure: Are follow-ups more substantive? Do they create better learning trajectories?
- Measure: Does the value landscape match expert intuition about what's worth studying?
- Output: evaluation report, delta from baseline

---

## 11. Success Conditions

| ID | Condition | Target | Rationale |
|----|-----------|--------|-----------|
| IS-SC-1 | Zone classification agreement with human judgment | ≥ 80% on 50-belief sample | Zone boundaries should match expert assessment |
| IS-SC-2 | Self-interrogation coverage | All 10 operators × 500+ beliefs | Sufficient to characterize the periphery |
| IS-SC-3 | Convergence within 5 rounds | < 5% zone reclassification per round by round 5 | System should stabilize |
| IS-SC-4 | Gap discovery (new Zone 3 entries per round) | ≥ 50 new gaps in rounds 2-3 | Self-interrogation should discover gaps that structural analysis alone misses |
| IS-SC-5 | Value landscape correlation with expert intuition | Spearman ρ ≥ 0.6 between V(G) ranking and David's ranking of "most worth investigating" | Endogenous value should track expert judgment |
| IS-SC-6 | QA follow-up quality improvement | ≥ 0.5 point improvement in panel persona scores (from 2.0/5 baseline) | The practical payoff |
| IS-SC-7 | VOI search improvement | ≥ 20% better gap closure rate when using V(G) vs. structural VOI alone | Tractability adjustment should improve resource allocation |

---

## 12. Open Questions for Panel Review

1. **Operator completeness**: Are 10 question-type operators sufficient to characterize the periphery, or do we need additional operators (e.g., TEMPORAL — "Has this changed over time?", CULTURAL — "Does this vary across cultures?", METHODOLOGICAL — "How was this measured?")?

2. **Rubric calibration**: How should the five dimensions of answer quality be weighted? Is completeness more important than groundedness? Does the weighting depend on the zone?

3. **Tractability estimation**: The warrant-based tractability heuristic (Table in §3.3) is a first approximation. Should tractability be learned from the discovery funnel's actual closure rates — i.e., empirically calibrated based on how hard it actually turned out to be to close different types of gaps?

4. **Zone 4 handling**: How should the system deal with Zone 4 regions — areas where it can't even formulate the gap? One option: use the QA system's ARBITRARY fallback rate as a Zone 4 detector, and use LLM-generated conceptual expansion to move Zone 4 → Zone 3. But this risks generating spurious gaps.

5. **Computational cost**: Full self-interrogation (10 operators × 4,888 beliefs × 4 quality dimensions) generates ~195,000 evaluations per round. Can this be done efficiently with local heuristics, or does it require LLM calls? If the latter, what's the API budget?

6. **Recursion depth**: How many rounds of follow-up should the self-interrogator pursue before stopping? Diminishing returns suggest 3-5 rounds, but the optimal depth may depend on the zone distribution.

7. **Rule set completeness**: Are four rule sets sufficient? One candidate for a fifth is *temporal rules* — conditions governing how beliefs should be updated when the evidence base changes over time (new studies, retractions, paradigm shifts). Another candidate is *social-epistemic rules* — conditions governing how disagreement among experts should affect credence (cf. Goldman, 1999, *Knowledge in a Social World*).

8. **Closure interactions**: §4.6 notes that Res(W, Rᵢ ∪ Rⱼ) may exceed Res(W, Rᵢ) ∪ Res(W, Rⱼ). How should the system detect and prioritize these *interactive residuals* — gaps that only emerge when multiple rule sets are applied simultaneously? Are these the most valuable gaps, or just the hardest to resolve?

9. **Purpose classification**: §4.3 proposes purpose-relative adequacy. How should the system infer purpose from a user query? Should it ask explicitly, or should it maintain a purpose model that refines over the course of an interaction?

10. **Rule set evolution**: Should the rule sets themselves be treated as beliefs in the web — subject to revision, expansion, and criticism? If so, what are the meta-rules governing the revision of rules? This risks infinite regress, but the pragmatist response is that the regress terminates when the rules are "good enough" for current purposes.

11. **Q-norm completeness**: Are 7 question-formulation norms sufficient? Candidates for additional norms include: a *temporal* norm (when should a question be re-asked because circumstances have changed?), a *social-epistemic* norm (when should the system pose a question to external experts rather than attempting to answer internally?), and a *resource-aware* norm (how should API cost constrain question depth?).

12. **Q-norm weighting**: Should all 7 Q-norms be weighted equally when computing composite compliance, or should some (e.g., Q1 presupposition checking, which prevents the system from asking incoherent questions) be treated as hard gates while others (e.g., Q7 seam targeting, which is generative but not strictly necessary) are treated as soft targets?

13. **Success condition calibration**: The success condition targets in §4.7.3 are initial estimates. After the Phase 1 pilot (§10), these should be empirically calibrated: are the thresholds achievable? Are they too lenient? Do they correctly distinguish good interrogation from bad? The calibration results should feed back into the Q-norm definitions.

---

## References

Friston, K. (2010). The free-energy principle: A unified brain theory? *Nature Reviews Neuroscience*, 11(2), 127–138. https://doi.org/10.1038/nrn2787

Howard, R. A. (1966). Information value theory. *IEEE Transactions on Systems Science and Cybernetics*, 2(1), 22–26.

Quine, W. V. O., & Ullian, J. S. (1970). *The web of belief*. Random House.

Raiffa, H., & Schlaifer, R. (1961). *Applied statistical decision theory*. Harvard Business School.

Rawls, J. (1971). *A theory of justice*. Harvard University Press.

Bromberger, S. (1966). Why-questions. In R. G. Colodny (Ed.), *Mind and cosmos: Essays in contemporary science and philosophy* (pp. 86–111). University of Pittsburgh Press. (~650 citations)

Hintikka, J. (1999). *Inquiry as inquiry: A logic of scientific discovery*. Cambridge University Press. (~2,800 citations)

Laudan, L. (1977). *Progress and its problems: Toward a theory of scientific growth*. University of California Press. (~4,200 citations)

Simon, H. A. (1956). Rational choice and the structure of the environment. *Psychological Review*, 63(2), 129–138. https://doi.org/10.1037/h0042769 (~5,000 citations)

van Fraassen, B. C. (1980). *The scientific image*. Oxford University Press. (~11,000 citations)

Achinstein, P. (2001). *The book of evidence*. Oxford University Press.

Alchourrón, C. E., Gärdenfels, P., & Makinson, D. (1985). On the logic of theory change: Partial meet contraction and revision functions. *Journal of Symbolic Logic*, 50(2), 510–530. https://doi.org/10.2307/2274239

Bechtel, W., & Abrahamsen, A. (2005). Explanation: A mechanist alternative. *Studies in History and Philosophy of Biological and Biomedical Sciences*, 36(2), 421–441.

Craver, C. F. (2007). *Explaining the brain: Mechanisms and the mosaic unity of neuroscience*. Oxford University Press.

Dung, P. M. (1995). On the acceptability of arguments and its fundamental role in nonmonotonic reasoning, logic programming and n-person games. *Artificial Intelligence*, 77(2), 321–357. https://doi.org/10.1016/0004-3702(94)00041-X

Goldman, A. I. (1999). *Knowledge in a social world*. Oxford University Press.

Hintikka, J. (1962). *Knowledge and belief: An introduction to the logic of the two notions*. Cornell University Press.

Hintikka, J. (1999). *Inquiry as inquiry: A logic of scientific discovery*. Springer.

Pollock, J. L. (1995). *Cognitive carpentry: A blueprint for how to build a person*. MIT Press.

Quine, W. V. O., & Ullian, J. S. (1978). *The web of belief* (2nd ed.). Random House.

Schum, D. A. (1994). *The evidential foundations of probabilistic reasoning*. Northwestern University Press.

Toulmin, S. E. (1958). *The uses of argument*. Cambridge University Press.

Walton, D. N. (1996). *Argumentation schemes for presumptive reasoning*. Lawrence Erlbaum Associates.

---

*Document generated 2026-03-01. Part of the ATLAS/Article_Eater_PostQuinean evidence synthesis system, UCSD Cognitive Science.*
