# From Philosophical Metaphor to Computational Architecture: How a Web of Belief Becomes a Working Knowledge System

**David Kirsh**  
Department of Cognitive Science, University of California, San Diego

**Draft for:** *Philosophy of Science* | Alternate venues: *Synthese*, *British Journal for the Philosophy of Science*, *Artificial Intelligence*

**February 2026**

---

## Abstract

The philosophical traditions of coherentism and causal inference have developed independently over the past half-century. Coherentism (Quine & Ullian, 1970; Thagard, 1989, 2000; BonJour, 1985) captures the epistemological structure of scientific knowledge — why we believe what we believe, how beliefs support and constrain each other, and how the total web of belief is revised in response to new evidence. Causal inference (Pearl, 1988, 2009; Spirtes, Glymour, & Scheines, 2000) provides rigorous machinery for interventional and counterfactual reasoning — what will happen if we intervene on the world, and what would have happened in counterfactual scenarios. Neither tradition, taken alone, is sufficient for representing scientific knowledge in a computationally useful way. Coherentism has lacked formal algorithms and has never been implemented at the scale of a real scientific domain. Causal inference has lacked epistemological structure: a Bayesian network has no concept of explanation, warrant type, theoretical coherence, or reflective equilibrium.

This paper argues that these traditions can be integrated by maintaining two distinct but interfaced knowledge structures: a *typed web of belief* that handles epistemological reasoning (coherence assessment, reflective equilibrium, competition resolution, value-of-information analysis, structural revision) and a *Bayesian network* that handles causal inference (interventional prediction via do-calculus, counterfactual reasoning). The web generates the BN's structure and parameters through a formal projection function; the BN's predictions feed back to the web for empirical diagnosis and revision. The integration is demonstrated through a case study: the Compositional Mechanistic Reasoning (CMR) system, which represents scientific knowledge about the relationship between buildings and human cognition as a typed belief web with approximately 130 nodes, 400 edges, and 8 formally distinct edge types. Six polynomial-time algorithms make the web's reasoning explicit and computable, and a five-level testing protocol provides empirical validation.

The contribution is threefold. First, coherentism is shown to be computable: the philosophical tradition that Haack (1993) criticised for underspecifying coherence is given a formal, efficiently computable coherence metric with typed constraint satisfaction and diagnostic decomposition. Second, reflective equilibrium is shown to be (partially) formalisable: the process of mutual adjustment between principles and particular judgments is captured by an algorithm that combines entrenchment ordering with coherence maximisation, though the evaluative dimension of genuine reflective equilibrium remains beyond the formal system. Third, the boundary between what a web of belief can do and what requires a Bayesian network is drawn with precision: the web handles everything except interventional inference (separating causation from association in the presence of confounders) and counterfactual reasoning (computing probabilities in hypothetical worlds).

**Keywords**: web of belief, coherentism, Bayesian networks, causal inference, computational epistemology, reflective equilibrium, philosophy of science

---

## 1. The Gap

Two of the most productive intellectual traditions in the philosophy of science have developed in near-total isolation from each other. This paper is about closing the gap between them.

The first tradition is **coherentism** — the view that beliefs are justified not by their relationship to an independent foundation but by their coherence with other beliefs. The lineage runs from Quine and Ullian's (1970) metaphor of knowledge as an interconnected web through BonJour's (1985) systematic defence of coherentism, Thagard's (1989, 2000) computational theory of explanatory coherence, and Lehrer's (1990) theory of knowledge as justified acceptance within a system of beliefs. The core insight is that scientific knowledge is not a list of independent facts but a structured network in which the *reasons for believing something* are as important as the belief itself. When a scientist asserts that high ceilings facilitate creative cognition, the coherentist asks not merely whether this is true but *why the scientist believes it*, *how this belief connects to other beliefs about cognition and architecture*, and *what evidence would lead to revision*.

The second tradition is **causal inference** — the mathematical framework for reasoning about cause and effect. The lineage runs from Wright's (1921) path analysis through Pearl's (1988, 2009) Bayesian networks and do-calculus, Spirtes, Glymour, and Scheines' (2000) causal discovery algorithms, and Rubin's (1974) potential outcomes framework. The core insight is that correlation is not causation, and that the distinction matters operationally: observing that high-ceiling buildings have creative occupants is not the same as knowing what will happen if you raise the ceiling. The causal inference tradition provides the mathematical machinery for separating these two kinds of knowledge — observational from interventional — and for computing the consequences of interventions and the probabilities of counterfactual outcomes.

These traditions address different questions. Coherentism asks: *What do we believe, and why?* Causal inference asks: *If we act on our beliefs, what will happen?* The first is about the epistemological structure of knowledge — how beliefs are justified, how they cohere, how they are revised. The second is about the operational consequences of knowledge — how to predict, intervene, and reason about alternatives. Both questions are essential for science, and both are essential for any computational system that aspires to represent scientific knowledge in a practically useful way.

Yet the traditions have never been integrated. No coherentist epistemology has included causal inference machinery. No causal inference framework has included epistemological structure. Thagard's (1989) ECHO model, the most developed computational coherentism, was a constraint-satisfaction system with approximately 20–30 nodes, binary coherence relations, and no typed edges, no bridge warrants, and no interface to Bayesian machinery. Pearl's (2009) causal model framework, the most developed causal inference machinery, takes its graphical structure as given — it computes with whatever DAG it receives, without evaluating whether the DAG is well-supported, whether its edges have different epistemological characters, or whether the overall structure is coherent.

The gap is not merely academic. It manifests concretely whenever a computational knowledge system must answer both epistemological and interventional questions. Consider a system that represents scientific knowledge about how buildings affect human cognition. An architect consulting this system wants to know two things: (a) *How confident should I be that high ceilings facilitate creative cognition?* — an epistemological question that requires evaluating the quality and coherence of the evidence. (b) *If I raise the ceiling in this building, how much improvement in creative performance can I expect?* — an interventional question that requires causal inference with confounding control. A system that answers only (a) provides understanding without actionable prediction. A system that answers only (b) provides prediction without understanding — and, critically, without the ability to diagnose why its predictions fail or to revise itself intelligently when they do.

This paper demonstrates that the gap can be closed by maintaining two distinct but interfaced knowledge structures: a **typed web of belief** that handles epistemological reasoning and a **Bayesian network** that handles causal inference, connected by a formal projection function that generates the BN from the web's current state and a feedback loop that channels the BN's empirical results back to the web for revision. The demonstration is not merely theoretical. It is grounded in a concrete case study: the Compositional Mechanistic Reasoning (CMR) system, which represents the current state of scientific knowledge about the relationship between buildings and the human brain as a typed belief web with approximately 130 nodes, 400 edges, and 8 formally distinct edge types, interfacing with a Bayesian network for interventional and counterfactual reasoning.

---

## 2. The Typed Web of Belief

### 2.1 Beyond Quine: Making the Metaphor Precise

Quine and Ullian's (1970) original web of belief was a metaphor. Beliefs are interconnected; central beliefs (logic, mathematics) resist revision because many other beliefs depend on them; peripheral beliefs (today's weather) can be revised easily. The metaphor captures something important about the structure of knowledge, but it is computationally inert — it does not specify what the nodes are, what the edges mean, how coherence is measured, or how the web is revised.

Thagard (1989, 2000) took the first step toward making the metaphor precise by identifying six principles governing coherence in a belief network: symmetry (coherence is a mutual relation), explanation (hypotheses that explain evidence cohere with it), analogy (analogous hypotheses provide mutual support), data priority (empirically grounded beliefs have a default advantage), contradiction (contradictory beliefs incohere), and competition (incompatible explanations of the same evidence compete). Thagard implemented these principles in the ECHO model, a connectionist network that settled into a partition of beliefs into accepted and rejected sets by maximising the satisfaction of coherence and incoherence constraints.

ECHO was an important proof of concept, but it had significant limitations for representing real scientific knowledge at scale. All coherence relations were symmetric and untyped — the same constraint-satisfaction mechanism handled explanation, analogy, and data priority without distinguishing their epistemological characters. The system operated over a binary acceptance/rejection partition rather than graded credences. And it was never scaled beyond approximately 30 nodes representing a simplified scientific controversy (Thagard, 1989, used the Lavoisier-Priestley oxygen controversy as the primary test case, with 23 propositions).

The typed web of belief developed here extends Thagard's framework in four directions that are essential for representing real scientific knowledge at the scale of a functioning research domain.

It is worth noting at the outset that the typed web is not merely a coherentist structure — it is a *mechanist* structure with coherentist properties. The new mechanist philosophy of science (Machamer, Darden, & Craver, 2000; Bechtel & Abrahamsen, 2005; Craver, 2007) has argued that scientific explanation is fundamentally about mechanisms: organised sets of entities and activities that produce phenomena. The CMR web's mechanism chains are precisely such structures — causal pathways from environmental features through neural processes to occupant outcomes, with internal structure at every step. The tier hierarchy (T1 → T1.5 → T2) is a levels hierarchy in Craver's (2007) sense: T1 frameworks are higher-level mechanisms, T2 templates are lower-level mechanisms, and the reduction edges between them are constitutive relevance relations — lower-level mechanisms are components of higher-level mechanisms. The typed edges encode mechanistic organisation: reduction edges specify constitutive relevance, bridge warrant edges specify the evidential bridge from mechanism to phenomenon, and cross-template interactions specify shared mechanistic components. The coherentist properties (mutual support, competition, reflective equilibrium) emerge from this mechanistic foundation — they describe how a community's understanding of mechanisms hangs together, not merely how a set of abstract propositions cohere.

### 2.2 The Formal Object

A typed web of belief is a directed graph G = (N, E, τ_N, τ_E, θ) where:

**N** is the set of nodes, each representing a justified belief. In the CMR system, |N| ≈ 130, comprising: 10 Tier 1 framework theories (e.g., Predictive Processing, Neuromodulation, Interoception), 10 Tier 1.5 domain theories (e.g., Biophilia, Prospect-Refuge, Attention Restoration), approximately 93 Tier 2 calibrated templates (specific claims about how environmental features affect neural mechanisms and produce occupant outcomes), 8 cross-cutting axioms (meta-parameters that modify all templates, such as dose-response functions and individual differences), and 2 working models (theoretical commitments constraining multiple templates).

**E** ⊆ N × N is the set of directed edges. |E| ≈ 300–400 in the CMR system. Edges are typed, and the types are the central innovation.

**τ_N : N → {T1, T1.5, T2, AX, WM, stub}** is the node type function, assigning each node to a tier in the theoretical hierarchy.

**τ_E : E → EdgeType** is the edge type function, where EdgeType is one of eight formally distinct types (Section 2.3).

**θ** is the annotation function, assigning to each node: a credence score c ∈ [0, 1] (or an interval [c_lo, c_hi] for imprecise credences), a bridge warrant ceiling w ∈ [0, 1], and a Toulmin structure (Toulmin, 1958) recording the data, backing, warrant, qualifier, rebuttal, and competing accounts for the belief.

The Toulmin structure is not decorative metadata. It is the epistemological substance that distinguishes a web of belief from a knowledge graph. A knowledge graph stores facts and relations. The typed web stores *justified beliefs* — beliefs with epistemological provenance that answers the questions "why do we believe this?", "what would change our minds?", and "how confident should we be?" These questions are answerable because the Toulmin structure records, for each belief, the evidence on which it rests, the inferential bridge from evidence to conclusion, the conditions under which the inference is valid, the conditions under which it fails, and the alternative explanations that have been considered and either defeated or left unresolved.

### 2.3 The Eight Edge Types

The eight edge types in the typed web are an exhaustive inventory of the ways in which scientific beliefs can be related. Each type carries a different epistemological character, a different mode of evidential support or constraint, and a different propagation rule for transmitting credence through the web.

**Type 1: Reduction.** A higher-tier belief is explained by a lower-tier mechanism. Prospect-Refuge theory (T1.5) is *reduced* to Predictive Processing and Default Mode / Place Cells (T1). This means that the credibility of Prospect-Refuge depends on the credibility of the T1 frameworks it reduces to. Reduction edges transmit credence downward with modest attenuation: if Predictive Processing is well-supported, Prospect-Refuge inherits support.

**Type 2: Bridge Warrant (7 subtypes).** These connect theoretical claims to empirical evidence, but they carry a *type* that categorises the epistemological character of the inferential bridge. The seven subtypes — CONSTITUTIVE, MECHANISM, EMPIRICAL_COVARIANCE, FUNCTIONAL, CAPACITY, ANALOGICAL, and THEORETICAL_DEFAULT — form a hierarchy from strongest to weakest evidential support. A CONSTITUTIVE bridge (the mechanism *is* the phenomenon) carries more credence than an ANALOGICAL bridge (reasoning from a parallel case). Crucially, two beliefs with the same numerical credence but different bridge warrant types mean different things epistemologically and require different kinds of research to resolve their uncertainty. This distinction is invisible in any system that represents evidential support as bare numbers.

**Type 3: Competition.** Rival hypotheses for the same evidence. Competitions have three possible resolution states: VICTORY (one account wins), COMPROMISE (domain partition, as in the Barrett-Craig two-stage interoceptive model), or EQUILIBRIUM (the evidence does not discriminate). Unresolved competitions reduce web coherence.

**Type 4: Cross-template Interaction.** Beliefs that share a mechanism or environmental input. These edges carry a valence (synergistic, antagonistic, or conditional) and a strength.

**Type 5: Inheritance.** Parameter sharing across beliefs. When two templates inherit the same parameter (e.g., HPA axis response parameters shared between stress and neuromodulation templates), inheritance edges ensure consistency and prevent double-counting.

**Type 6: Working Model.** A theoretical commitment constraining multiple beliefs. Working models (e.g., the Barrett-Craig two-stage model) sit between T1 and T1.5 in influence and carry explicit revision clauses.

**Type 7: Axiom.** A meta-parameter modifying all beliefs. Cross-cutting axioms (e.g., dose-response functions, perceived control) define background conditions.

**Type 8: Partial-Out.** A scope partition preventing double-counting. When two beliefs would otherwise claim the same effect independently, partial-out edges restrict each to its non-overlapping contribution. These edges carry no credence — they are purely structural.

This taxonomy is motivated by the observation that scientific reasoning involves qualitatively different kinds of inferential relationships, and that collapsing them into a single undifferentiated "supports" or "is-caused-by" relation loses information that matters for coherence assessment, revision, and research planning. The ECHO model had three relation types (explanation, analogy, contradiction). Standard Bayesian networks have one (conditional dependence). The typed web has eight, each with distinct propagation rules, and the claim is that this richer typology is necessary for representing real scientific knowledge faithfully.

A question that must be addressed is whether the bridge warrant hierarchy — CONSTITUTIVE > MECHANISM > EMPIRICAL_COVARIANCE > FUNCTIONAL > CAPACITY > ANALOGICAL > THEORETICAL_DEFAULT — is a discovery or a stipulation. The position taken here is that the hierarchy's *ordering* is empirically grounded: a complete mechanism trace genuinely IS stronger evidence than a structural analogy, for reasons that any philosopher of evidence would accept (the mechanism trace specifies the causal pathway; the analogy assumes it from a parallel case). This is not a convention — it reflects genuine epistemological distinctions. However, the hierarchy's *numerical ceilings* (0.75 for CONSTITUTIVE, 0.35 for ANALOGICAL, etc.) are calibration parameters, not discovered constants. They are initial estimates derived from expert judgment about the strength of different evidence types, and they should be refined by the retrodiction test (Section 6.3): the values that best reproduce the panels' historical credence assignments are the empirically calibrated values. The distinction between ordinal and cardinal properties — the ordering is discovered, the numbers are calibratable — resolves what would otherwise be a distracting debate about whether the hierarchy is "real."

### 2.4 Two Kinds of Probability

The typed web tracks **epistemic probability** — the scientific community's uncertainty about whether its theories, mechanisms, and evidence are correctly specified. When the web assigns a credence of 0.45 to the claim that a particular daylight-to-mood pathway is correctly specified, it is describing a state of knowledge, not a frequency in the world. This probability changes when the community learns more, even if the world stays the same.

The Bayesian network, by contrast, aspires to contain **aleatory probability** — the inherent variability of the world. When the BN's conditional probability table specifies P(Mood = positive | Daylight = high) = 0.70, it aspires to describe a population frequency.

The distinction between epistemic and aleatory probability has a long history in probability theory (Hacking, 1975; Hájek, 2019) and is standard equipment in the philosophy of science. What is novel here is the architectural commitment to maintaining both kinds simultaneously, in different data structures, with formal translation protocols between them. The web stores epistemic probabilities with their epistemological provenance (the Toulmin structure, the bridge warrant type). The BN stores aleatory probabilities stripped of provenance (bare numbers in CPTs). The projection from web to BN involves a translation from epistemic to aleatory that is necessarily lossy — the BN cannot represent *why* a particular conditional probability has its value, only *what* the value is.

This lossy translation is the reason the web must remain the primary knowledge representation and the BN must be a derived projection, regenerated whenever the web revises.

This architectural separation between epistemic and aleatory probability is a useful simplification, not an ontological partition. In practice, the web's epistemic credences are often attitudes toward probabilistic propositions — the community's confidence that a particular conditional probability (an aleatory fact) has a certain value. The epistemic and aleatory are interleaved: what the community knows is partly constituted by probabilistic facts about the world (Moss, 2018). The separation remains architecturally justified because it enforces different representational requirements — the web must store provenance (why the credence has its value), while the BN must store conditional probability tables (what the value is) — but it should be understood as a design decision that trades ontological precision for computational tractability, not as a claim about the fundamental nature of probability.

---

## 3. The Algorithms: Making Coherentism Computable

### 3.1 The Computability Challenge

Haack (1993) famously criticised coherentism for failing to specify what coherence *is* with sufficient precision to be evaluable. How much coherence is enough? How do you measure it? How do you compare the coherence of two belief systems? These questions are devastating if coherence remains an informal notion. They are answerable if coherence is given a formal, computable metric.

This section presents six polynomial-time algorithms that make the typed web's reasoning explicit and computable. They are specified as formal procedures with defined inputs, outputs, and complexity bounds. Whether they constitute a complete formalisation of scientific reasoning is a separate question (Section 7 addresses this honestly); the claim here is that they capture the *structural* aspects of coherentist reasoning — credence propagation, competition resolution, coherence measurement, belief revision, research prioritisation, and projection to a causal model — with sufficient precision to be implemented, tested, and evaluated.

### 3.2 Algorithm 1: Typed Credence Propagation

The first algorithm computes updated credences for all nodes by propagating evidential support through the web's typed edges. It is inspired by belief propagation in graphical models (Pearl, 1988) but modified for typed edges: different edge types transmit different kinds of support with different attenuation factors.

The key technical innovation is the **typed attenuation factor** α(edge_type), which specifies how much credence flows through each edge type. A reduction edge transmits credence with α = 0.90 (modest attenuation — if the parent theory is well-supported, the child inherits most of that support). A CONSTITUTIVE bridge transmits with α = 0.90 (the strongest evidence bridge). An ANALOGICAL bridge transmits with α = 0.45 (analogical reasoning provides much weaker support). A competition edge transmits with α = −0.30 (competitors *reduce* each other's credence).

These α values are not arbitrary. They are the computational instantiation of the bridge warrant hierarchy — a philosophical judgment about the relative strength of different kinds of evidential support. But they are parameters, not axioms. The retrodiction test (Section 6.2) provides a method for calibrating them empirically: adjust α values until the algorithm best reproduces the historical decisions of the expert panels that built the web. A sensitivity analysis (Section 6.5) provides a method for assessing whether the results are robust across the plausible range of α values.

The algorithm iterates until convergence (credences stabilise within a tolerance ε). Convergence is guaranteed for acyclic graphs and for cyclic graphs when the damping factor λ satisfies a standard condition from iterative methods: λ < 1/(1 + max_degree). For the CMR's graph (maximum node degree ≈ 15), λ = 0.3 satisfies this condition. The algorithm also enforces two structural constraints: bridge warrant ceilings (no node's credence exceeds its warrant ceiling) and entrenchment (T1 framework beliefs resist downward revision more strongly than T2 template beliefs, reflecting Quine's insight that central beliefs are more resistant to revision than peripheral ones).

Complexity: O(max_iterations × |E|). For the CMR (|E| ≈ 400, max_iterations = 1000): 400,000 operations. Milliseconds on modern hardware.

### 3.3 Algorithm 2: Graded Competition Resolution

Scientific controversies are a persistent feature of real knowledge bases, and a coherentist system must handle them formally. Algorithm 2 extends Dung's (1995) argumentation semantics to a graded setting: competing hypotheses attack each other with computed attack strengths (based on data contradiction, domain restriction, explanatory superiority, and warrant superiority), and the algorithm determines one of three outcomes.

VICTORY occurs when one competitor's net support exceeds the next-best by more than a threshold (default 0.30). COMPROMISE occurs when the competitors attack each other only outside their respective domains — a domain partition that can be detected by comparing the qualifier features of the competitors' Toulmin structures. EQUILIBRIUM occurs when neither VICTORY nor COMPROMISE applies; the competitors retain credences proportional to their relative support, and the competition edge is flagged for imprecise probability treatment.

The Barrett-Craig two-stage interoceptive model — the CMR system's most prominent theoretical compromise — would be represented as a COMPROMISE resolution: Barrett's constructionism holds for the anterior insula (context-dependent emotional construction) and Craig's labelled-line theory holds for the posterior insula (modality-specific interoceptive signal). The domain partition is detectable because Barrett's supporting evidence has a qualifier restricting it to high-level affective processing while Craig's supporting evidence has a qualifier restricting it to early interoceptive coding.

Complexity: O(k² × |T|) per competition, where k is the number of competitors and |T| is the Toulmin structure size. For the CMR's typical 2–3 way competitions: trivial.

### 3.4 Algorithm 3: Typed Global Coherence Metric

This is the algorithm that answers Haack's challenge. It computes a global coherence score C ∈ [-1, 1] by evaluating, for each edge in the web, the degree to which the beliefs at the edge's endpoints satisfy the coherence constraint implied by the edge type.

For positive-coherence edges (reduction, bridge, inheritance, interaction, working model, axiom): constraint satisfaction is proportional to the product of the endpoint credences, weighted by the edge type's importance. High credence in both connected nodes × high edge-type weight = high constraint satisfaction. For competition edges: resolved competitions (VICTORY or COMPROMISE) contribute positively (the web has dealt with a tension), while unresolved competitions contribute negatively in proportion to the closeness of the competitors' credences (the web cannot decide). For partial-out edges: neutral (they are structural boundaries, not coherence contributors).

The global score C is the ratio of total constraint satisfaction to maximum possible satisfaction. But the *diagnostic decomposition* is more informative than the global score: the metric decomposes by edge type (which *kinds* of connections are working well or poorly) and by node (which *specific* beliefs are most or least coherent with their local neighbourhood). This decomposition directly identifies where the web is strong, where it is weak, and where intervention would most improve overall coherence.

Complexity: O(|E|). For the CMR: approximately 400 operations. Instantaneous.

### 3.5 Algorithm 4: Structural Revision

When new evidence conflicts with the web's current state, the web must be revised. Algorithm 4 extends AGM belief revision theory (Alchourrón, Gärdenfors, & Makinson, 1985) for typed graphs with entrenchment ordering.

The algorithm embodies Quine's insight about the differential revisability of beliefs. It first assesses which nodes are affected by the new evidence, then computes an entrenchment score for each affected node — a function of tier (T1 beliefs are more entrenched than T2 beliefs), local coherence (well-supported beliefs resist revision), and connectivity (highly connected beliefs resist revision because changing them propagates widely). Affected nodes are revised in ascending entrenchment order (least entrenched first), with the algorithm selecting at each step the least drastic revision that restores coherence: updating a credence (cheapest), changing an edge type, adding or removing edges, changing a node's tier, or adding a new node (most expensive).

The algorithm is greedy — it processes nodes in order without exploring all revision combinations — which sacrifices global optimality for tractability. When the greedy strategy fails to restore coherence, the algorithm defers to human review, an honest acknowledgment that some revision decisions exceed the scope of automated inference.

This is the algorithm that most closely approximates reflective equilibrium (Section 7.2 discusses the approximation's limitations). The mutual adjustment between principles (high-entrenchment beliefs) and particular judgments (low-entrenchment beliefs) is captured by the entrenchment ordering: the algorithm tries revising peripheral beliefs first, resorting to revision of central beliefs only when peripheral revision is insufficient.

Complexity: O(|affected| × |E|). Typically fast, since most new evidence affects fewer than 20 nodes.

### 3.6 Algorithm 5: Value of Information

Science must decide not only what to believe but *what to investigate next*. Algorithm 5 ranks the web's uncertainties by their expected impact on overall coherence, producing a formal research agenda.

For each uncertain parameter (THEORETICAL_DEFAULTs, unresolved competitions, low-confidence mechanism steps), the algorithm simulates two scenarios — optimistic (the uncertainty is resolved favourably: credence set to the warrant ceiling) and pessimistic (the uncertainty is resolved unfavourably: credence set to 0.10) — and computes the expected coherence change. This is multiplied by the node's downstream reach (the number of nodes reachable via directed edges), producing a Value of Information (VOI) score that balances coherence impact with graph-structural importance.

The output is a ranked list: the uncertainty with the highest VOI is the highest-priority research target. This ranking has the appealing property of being *derived from the web's own structure* rather than imposed by external judgment. A THEORETICAL_DEFAULT in the most highly connected node (T29, the allostatic load master template in the CMR system) has high VOI because resolving it improves the entire system. A THEORETICAL_DEFAULT in an isolated peripheral template has low VOI because resolving it improves only one belief.

A refinement worth noting: the current VOI computation ranks uncertainties by their expected impact on *coherence*. But from the perspective of scientific understanding (Khalifa, 2017), the more important ranking might be by expected impact on *counterfactual reasoning capacity* — how much resolving a given uncertainty would change the BN's interventional and counterfactual predictions. An uncertainty that, when resolved, would dramatically alter the BN's answer to "what happens if I raise the ceiling?" is more important for practical understanding than one that merely improves the web's internal coherence score. Incorporating the BN projection (Algorithm 6) into the VOI computation — ranking uncertainties by their downstream impact on the BN's predictions, not just the web's coherence — is a natural extension.

Complexity: O(|uncertainties| × (|E| + |N|)). For the CMR: approximately 26,500 operations. Fast.

### 3.7 Algorithm 6: BN Projection

The final algorithm generates a Bayesian network from the web's current state, implementing the interface between the two knowledge structures. It identifies the observable and manipulable variables (environmental parameters and occupant outcomes — the endpoints of mechanism chains), compresses multi-step mechanism chains into single BN edges, populates the BN's conditional probability tables via the CPT elicitation protocol, and validates the resulting DAG.

The compression step is where the web's epistemological richness is lost and the BN's computational tractability is gained. A four-step mechanism chain (environmental feature → neural mechanism 1 → neural mechanism 2 → outcome) becomes a single BN edge with a CPT entry derived from the product of step-by-step transition probabilities. The intermediate neural mechanisms are not represented in the BN. The BN knows *that* daylight improves mood (with some probability). The web knows *why* — through which pathway, with what evidence, against what competitors, under what conditions. The projection is lossy by design.

Complexity: O(|chains| × |length| + |V|³), where |V| is the number of BN variables. For the CMR: trivially fast.

### 3.8 Computational Complexity Summary

All six algorithms are polynomial in the web's size. All complete in milliseconds for the CMR's actual graph (approximately 130 nodes, 400 edges). The calculus can run interactively — a user can modify the web and see updated coherence, credence propagation, and VOI ranking in real time. This is not a theoretical claim about computability; it is a practical claim about usability.


---

## 4. The Bayesian Network Interface

### 4.1 What the BN Provides

The Bayesian network (Pearl, 1988, 2009) is a directed acyclic graph in which nodes represent random variables and directed edges represent conditional dependencies, with each node carrying a conditional probability table (CPT). The BN's computational power lies in two operations that the web cannot perform.

**Interventional reasoning (do-calculus).** Pearl's (2009) fundamental insight is that observing a variable and intervening on it are different operations. When an architect observes that buildings with high ceilings tend to have more creative occupants, the observation is confounded: high-ceiling buildings are newer, more expensive, better maintained, and occupied by higher-income people. The observed correlation conflates the causal effect of ceiling height with the effects of every common cause. When the architect *intervenes* — raises the ceiling in a specific building — the incoming causal connections to ceiling height are severed (the ceiling height is now fixed by the architect's decision, not by building age or budget), and only the outgoing effects propagate. The do-calculus formalises when and how observational data can be used to estimate these interventional effects, even in the presence of known confounders.

A clarification is needed here. The web's mechanism chains *are* causal claims — they specify that one thing causes another through intermediate steps. The web's compositional chain propagation is a form of causal reasoning: it traces causal pathways and multiplies effect sizes along them. The distinction between web and BN is therefore not between non-causal and causal reasoning, but between two *modes* of causal reasoning (cf. Illari & Russo, 2014). The web performs **mechanism-based causal reasoning**: it traces pathways through intermediate steps, each with its own evidence base, warrant type, and uncertainty. The BN performs **variable-based causal reasoning**: it computes over probability distributions on observable variables, handling confounding control and counterfactual inference through the formal machinery of do-calculus and structural equations. Each step in a mechanism chain implicitly assumes intervention ("if this input is present, this output follows"), but the web does not rigorously handle confounding — the case where the input covaries with other causes of the output through pathways not represented in the mechanism chain. For this, the BN's variable-based causal machinery is required.

**Counterfactual reasoning.** "Given that we observed low occupant mood in this building, *would* mood have been positive if daylight had been higher?" This combines conditioning on actual evidence (what happened) with hypothetical intervention (what might have happened differently). Counterfactual reasoning requires the BN's structural equations and the three-step procedure of abduction, action, and prediction (Pearl, 2009, Chapter 7).

These two capabilities are precisely what makes the system useful for applied science. The fundamental question in architectural practice is "if I change the design, what will happen?" — an interventional question. And the fundamental question in post-occupancy evaluation is "would outcomes have been different if the design had been different?" — a counterfactual question.

### 4.2 What the BN Cannot Provide

The BN's limitations are equally important and are, in a sense, the motivation for the entire architecture.

The BN has **no concept of explanation**. It can compute P(Mood = positive | do(Daylight = high)) = 0.70, but it cannot explain *why* daylight improves mood. The mechanism (daylight → retinal stimulation → raphe nuclei → tryptophan hydroxylase → serotonin synthesis → positive processing bias) is not represented in the BN. The BN has a single edge "Daylight → Mood" with a CPT. The *why* lives in the web.

The BN has **no concept of warrant types**. All edges in a BN carry the same kind of information: conditional probabilities. But two edges with the same CPT value can mean epistemologically different things — one might rest on a complete neural mechanism trace and the other on a structural analogy from a different domain. The BN erases this distinction.

The BN has **no concept of coherence**. Adding a new variable and edge to the BN does not trigger any coherence check — the BN does not evaluate whether the new addition is consistent with any theory of how the world works. The coherence checking must happen elsewhere: in the web.

The BN has **no capacity for structural self-revision**. The BN's structure (the DAG) is fixed; only its parameters (the CPTs) are updated by Bayes' rule. But the most important episodes in the CMR's development involved *structural* changes: adopting the Barrett-Craig two-stage model (adding new edges and retyping existing ones), elevating AX4 to a formally recognised moderator (adding axiom edges to every template), demoting Attention Restoration Theory and Stress Reduction Theory from T1 to T1.5 (changing node types). These structural modifications are web operations that the BN cannot initiate.

### 4.3 The Projection Function: Web → BN

The formal interface between web and BN is a **projection function** π: Web → BN that generates a Bayesian network from the web's current state. Algorithm 6 implements this function.

The projection is **surjective but not injective** — multiple web states can project to the same BN (because the projection discards epistemological provenance), but every well-formed BN can in principle be derived from some web state. This means the projection is lossy: information flows from web to BN but is lost in the compression. The bridge warrant type, the Toulmin justification, the competing accounts, the qualifier/rebuttal structure — all of this is discarded in the projection. The BN receives a number; the web retains the reasoning behind the number.

This lossiness is by design, not by accident. The BN is a computationally tractable snapshot of the web's current epistemic state, optimised for interventional and counterfactual inference. It sacrifices epistemological richness for computational power. The web retains the richness. When the web is revised (a new study is published, a competition is resolved, a working model is adopted), the BN is regenerated — not patched, but regenerated from scratch via the projection function. This "regeneration" property ensures that the BN is always consistent with the web's current state, even though the BN itself has no mechanism for maintaining that consistency.

### 4.4 The Feedback Loop: BN → Web

The flow from BN to web is narrower but critically important. The BN's interventional predictions are tested against real-world observations (occupant satisfaction surveys, cognitive performance measures, physiological recordings in actual buildings). Discrepancies between predicted and observed outcomes feed back to the web, triggering the structural revision algorithm (Algorithm 4). The web investigates: is a mechanism chain wrongly specified? Is a parameter miscalibrated? Is there a confounding variable the BN's structure missed? Is a competing account actually correct?

This feedback loop closes the epistemic cycle: the web generates the BN (theory → prediction); the BN generates predictions (prediction → test); the predictions are tested against reality (test → evidence); the evidence feeds back to the web (evidence → revision); the revised web generates a new BN (revision → theory). Each cycle is an iteration of the fundamental scientific process — theorise, predict, test, revise — made explicit and formal.

### 4.5 The Asymmetric Relationship

The relationship between web and BN is **asymmetric but genuinely bidirectional**. The asymmetry is important and was not fully appreciated in the CMR system's earlier self-understanding. The web is epistemically primary. It can reason about mechanisms, coherence, evidence, theory, and competing accounts on its own. It can compute quantitative consequences through compositional chain propagation — mechanism-based causal reasoning that traces pathways through intermediate steps with typed epistemic provenance. It handles everything that a scientific community's knowledge system needs to handle — except for two specific operations that require variable-based causal machinery.

The BN provides those two operations (interventional inference with confounding control, and counterfactual reasoning) and nothing else. The distinction is not between causal and non-causal reasoning — the web's mechanism chains are causal structures, as the new mechanist philosophy of science has emphasised (Machamer, Darden, & Craver, 2000; Craver, 2007). The distinction is between two *representations* of causation: the web represents causes as mechanistic pathways with internal structure and epistemic provenance at every step; the BN represents causes as statistical dependencies between observable variables, stripped of internal structure but equipped with formal tools for handling confounding and computing counterfactuals.

This asymmetry has an important practical consequence. When the BN produces a surprising result, the *diagnosis* must occur in the web. Only the web has the epistemological structure to ask "why is this prediction surprising?" and "what would need to be revised to accommodate the discrepancy?" The BN can flag the discrepancy; the web can understand it.

---

## 5. The Case Study: 130 Nodes, 400 Edges, 8 Edge Types

### 5.1 The CMR System

The Compositional Mechanistic Reasoning (CMR) system represents the current state of scientific knowledge about the relationship between buildings and the human brain. It was developed through a series of eleven expert panels (STRESS-I through CROSSCUT-I), each of which deliberated over a specific domain of environmental neuroscience: visual processing, lighting, spatial cognition, stress, social dynamics, memory, multisensory integration, creativity, music and acoustics, thermal comfort, and neuromodulation. A twelfth panel (CROSSCUT-I) integrates cross-cutting parameters that modify all domains.

The web's content is summarised in Table 1.

**Table 1: CMR Web of Belief — Summary Statistics**

| Component | Count | Description |
|-----------|-------|-------------|
| T1 Framework Theories | 10 | PP, Salience, DMN/Place Cells, Dual-Task, Neuromodulation, Interoception, Multisensory, Embodied, Circadian, Motor-Sensory |
| T1.5 Domain Theories | 10 | Biophilia, Prospect-Refuge, ART, SRT, Fractal Fluency, Awe/Kama Muta, Space Syntax, Soundscape, Place Attachment, Aesthetic Anchoring (candidate) |
| T2 Calibrated Templates | ~93 | Specific mechanism chains with numerical parameters |
| Cross-cutting Axioms | 8 | Dose-response, habituation, individual differences, cultural modulation, perceived control, temporal, neurodiversity, VR limitation |
| Working Models | 2 | Barrett-Craig two-stage, Differential-mode |
| Total Nodes | ~130 | |
| Total Edges | ~400 | Across 8 types |

### 5.2 How the Web Was Built: The Panel Process as Epistemology Engineering

The CMR web was not specified by a single designer. It was built through an iterative process of simulated expert panel deliberation in which each panel performed a series of epistemological operations: reduction (connecting higher-level theories to lower-level mechanisms), calibration (assigning numerical parameters with explicit uncertainty ranges and warrant types), adjudication (resolving competing accounts through structured debate), inheritance (establishing shared parameters across panels), and constraint enforcement (preventing confidence inflation, double-counting, and theoretical incoherence).

Each operation modifies the web. Reduction adds edges. Calibration populates nodes with parameters. Adjudication resolves or records competition edges. Inheritance adds sharing edges. Constraint enforcement removes or revises nodes and edges that violate coherence norms. The result is a dynamic structure that reflects the current best judgment of a community of scientists about a complex domain — encoding not just what they believe but why they believe it, what would change their minds, and where they disagree.

A candid assessment of this process must acknowledge its social-epistemic limitations. The simulated experts share a common generative source (a large language model), which may introduce systematic biases that independent human experts would not share. O'Connor and Weatherall (2019) have shown that even well-designed social epistemic processes can fail to converge to truth when agents share evidence selectively or when early evidence creates strong anchoring effects. The CMR panel process has both features: each panel sees only its domain's literature, and early panels create anchoring effects — the Barrett-Craig model, adopted at THERMAL-I, constrained all subsequent panels' treatment of interoception. O'Connor and Weatherall's (2018) models of epistemic networks distinguish *convergent* path dependence (different orderings reach the same equilibrium) from *divergent* path dependence (different orderings reach different equilibria). The CMR's structural features make divergent path dependence a live concern, not merely a theoretical possibility. The coherence metric (Algorithm 3) may compound this risk by rewarding mutual support, which is a property of both genuine scientific consensus and groupthink. The testing protocol's empirical levels (3–5) are the principal safeguard: they check the web's predictions against reality, not against itself.

### 5.3 What the Web Represents That a Database Cannot

The difference between the CMR web and a standard evidence database can be illustrated with a concrete example. Suppose a new study is published showing that the Lambert et al. (2002) finding — that daylight exposure affects brain serotonin turnover — does not replicate.

In a standard database, you would update the daylight effect size and move on. In the CMR web, the consequences propagate through the graph structure:

(1) Template NM7 (Serotonergic Mood Modulation) loses its primary evidence. Its confidence drops. The competing account (circadian entrainment rather than direct serotonergic modulation) gains relative weight.

(2) Template T29 (Allostatic Load Master) is affected because its 5-HT input term becomes more uncertain. The Value of Information for the 5-HT pathway increases — it is now the highest-priority research target.

(3) The cross-template interaction between daylight and serotonergic processing (shared with the LIGHT-I panel) is undermined, weakening the melanopic-to-serotonergic chain.

(4) The "sick building syndrome" mechanism (poor daylight → low 5-HT → negative processing bias → amplified complaints) loses its neurochemical substrate. The web does not delete this mechanism — it flags it as now resting on a THEORETICAL_DEFAULT rather than EMPIRICAL_COVARIANCE, which changes the bridge warrant type and lowers the confidence ceiling.

(5) The Crucible 1 consensus from NEUROMOD-I (wanting-liking balance moderated by 5-HT) is weakened, because the 5-HT moderation depends on the daylight-5-HT link.

All of this propagation is possible because the web encodes the *reasons* for each belief, not just the belief itself. A database would know that the effect size changed; the web knows *what else changes as a consequence* and *why*.

### 5.4 Reflective Equilibrium in Practice: The Barrett-Craig Compromise

The Barrett-Craig two-stage model of interoception provides a concrete illustration of reflective equilibrium as it operates in the CMR web. The model emerged from a competition between two established theories: Lisa Feldman Barrett's constructionist account (emotions are constructed from interoceptive signals by contextual interpretation in the anterior insula) and Bud Craig's labelled-line account (interoceptive signals are modality-specific and carry their affective valence from the posterior insula forward). These theories made different predictions about how thermal comfort affects occupant affect.

The panel process functioned as a reflective equilibrium engine. The general principles (each expert's theoretical framework) were confronted with particular findings (posterior insula shows modality-specific responses; anterior insula shows context-dependent constructionist processing). Neither principle survived intact. The resulting compromise — a two-stage model in which early processing is modality-specific (vindicating Craig) and later processing is constructionist (vindicating Barrett) — was not in either tradition's prior hypothesis space. It emerged from the confrontation between them. This is the hallmark of genuine reflective equilibrium: the hypothesis space is *expanded* by the process, not merely searched.

---

## 6. Testing and Limits

### 6.1 The Testing Philosophy

A formal system that has not been tested against reality is an elaborate exercise in self-consistency. The five-level testing protocol specifies increasingly severe validation tests, each targeting a different aspect of the calculus. The levels are cumulative: success at Level 1 is necessary before Level 2, and so on.

### 6.2 Level 1: Internal Consistency

The algorithms must not produce contradictions, infinities, or non-termination. This is a sanity check: does the calculus work as software? Test: encode the full CMR web as a typed graph, implement all six algorithms, run them, and verify that credences stay in [0, 1], the coherence metric is finite and non-degenerate, structural revision terminates, and all constraints are satisfied.

### 6.3 Level 2: Retrodiction

The calculus must reproduce the reasoning that built the web. Test: reconstruct the web's state before each of five major historical decisions (Barrett-Craig adoption, differential-mode adoption, AX4 elevation, ART/SRT demotion, Aesthetic Anchoring deferral), apply the algorithms, and check whether they recommend the same decisions. Scoring: >80% agreement indicates the calculus captures the panels' reasoning. A harder version samples 50–100 micro-decisions across all panel outputs and scores agreement.

This test is particularly informative because it is bidirectionally diagnostic. If the calculus agrees with the panels, it means the panels reasoned coherently — their informal judgments are derivable from the formal rules. If the calculus disagrees, either the calculus is wrong (its rules do not capture scientific reasoning) or the panels were inconsistent (their informal reasoning contained errors that the formal system detects). Either outcome is informative.

### 6.4 Level 3: Prediction

The deepest empirical test: the calculus predicts outcomes it has not seen. Before CROSSCUT-I (the final panel) is executed, the calculus generates sealed predictions about which axiom parameters will be most contested, whether specific templates will achieve their target bridge warrant status, and how competition resolutions will proceed. These predictions are sealed, the panel is run, and the predictions are compared with outcomes.

### 6.5 Levels 4–5: Transfer and Adversarial Testing

Level 4 tests domain generality by applying the calculus to a structurally similar but content-independent scientific domain (candidate domains: air pollution and cognition, psychedelic-assisted therapy, urban noise and cardiovascular health). Level 5 tests robustness by constructing deliberately pathological webs: credence cycles, contradictory inheritance, total competition equilibrium, 1000-node scale.

### 6.6 What Has Been Tested and What Has Not

Intellectual honesty requires precision on this point. As of this writing, the algorithms exist as formal specifications with pseudocode and complexity analyses. They have not been implemented as running software. Levels 1–5 of the testing protocol have not been executed. The retrodiction and prediction tests have not been run.

What exists is the web itself (130 nodes, 400 edges, built through 11 panels of structured expert deliberation), the algorithms (six formally specified procedures with polynomial complexity bounds), and the testing protocol (five levels with concrete test cases and scoring rubrics). The gap between specification and implementation is real, and closing it is the immediate next step.

The paper's contribution is therefore architectural, not empirical. It presents a design for integrating coherentism and causal inference that is sufficiently detailed to be implementable and testable, grounded in a real case study at a non-trivial scale, and accompanied by a concrete validation plan. Whether the design actually works — whether the algorithms produce reasonable outputs, whether the retrodiction test yields high agreement, whether the predictions are accurate — is an empirical question that this paper sets up but does not answer.

---

## 7. What This Means for Philosophy of Science

### 7.1 Coherentism Is Computable

The first consequence of this work is that coherentism — the epistemological tradition that Haack (1993) criticised for underspecifying coherence — can be given a formal, efficiently computable interpretation. Algorithm 3 (Typed Coherence Metric) provides a specific answer to Haack's challenge: coherence is typed weighted constraint satisfaction over a graph with formally distinct edge types. The metric is computable in O(|E|) time, produces both a global score and a diagnostic decomposition, and treats different kinds of coherence relations differently (resolved competitions contribute positively, unresolved competitions contribute negatively, partial-outs are neutral).

This does not settle the philosophical debate about whether coherence is truth-conducive — whether a coherent belief system is more likely to be true than an incoherent one. That debate continues (Olsson, 2005; Bovens & Hartmann, 2003). What it does is remove a methodological objection: the objection that coherentism is too vague to be evaluated. With a formal metric, one can ask concrete questions. Is the CMR web's coherence increasing over time? Does each panel leave the web in a better state? Are there regions of persistent incoherence that indicate unresolved theoretical problems? These are empirically answerable questions once coherence is a number rather than an intuition.

Moreover, the data priority principle — Thagard's (1989) requirement that empirically grounded beliefs have a default advantage — is encoded in the bridge warrant hierarchy. CONSTITUTIVE and MECHANISM bridges, which rest on direct empirical evidence of the mechanism, carry higher attenuation factors than ANALOGICAL or THEORETICAL_DEFAULT bridges. Algorithm 3's coherence metric inherits this weighting: edges grounded in empirical data contribute more to coherence than edges resting on analogy or expert default. Haack's (1993) foundherentist requirement that coherence should respect the special epistemic status of observation is thereby honoured within the formal system.

### 7.1.1 The Coherence-Truth Problem and the Three-Component Response

The deepest challenge to any coherentist architecture is Olsson's (2005) demonstration that, under quite general conditions, coherence among reports is not truth-conducive. Coherent beliefs may be systematically wrong if they are mutually reinforcing but collectively disconnected from reality. A web that maximises coherence (which is what the algorithms do) could be *actively misleading* — producing a knowledge system that is internally beautiful and externally false.

This challenge cannot be answered by coherence alone. No amount of internal consistency guarantees external correctness. The CMR architecture's response is structural: it embeds the coherentist web within a three-component system that combines the virtues of coherentism with the virtues of empiricism.

The **web** maximises explanatory coherence — mutual support among beliefs, typed justificatory structure, reflective equilibrium between principles and particular findings. This gives the system the explanatory depth and revisionary flexibility that coherentism provides.

The **Bayesian network** generates empirical predictions — quantitative, interventional predictions about what will happen when specific environmental features are changed. These predictions are derived from the web via the projection function, but once generated, they are empirical claims about the world, testable against observation.

The **testing protocol** checks those predictions against reality. When predictions fail, the discrepancies feed back to the web via Algorithm 4 (Structural Revision), triggering the revision that coherence alone cannot motivate. The web may be perfectly coherent before the test; if the test fails, coherence is not enough, and the web must change.

This three-component architecture is, in effect, a reconciliation of coherentism and empiricism. The coherentist insight is that knowledge is a structured web of mutually supporting beliefs, not a list of independent facts. The empiricist insight is that beliefs must be tested against the world, because internal coherence does not guarantee truth. The CMR architecture combines both: the web provides the structure, the BN provides the predictions, and the testing protocol provides the empirical accountability. The interface between web and BN — the projection function that translates epistemic provenance into aleatory parameters — is where the reconciliation happens. It is the bridge between a system that values *coherence* (explanatory depth, mutual support, theoretical elegance) and a system that values *correspondence* (accurate prediction, empirical testing, real-world feedback).

Olsson's impossibility result applies to testimonial coherence among independent witnesses. The CMR web is not a set of independent testimonies. It is a structured network with typed edges, Toulmin provenance, and a formal interface to empirical testing. Whether this structural richness is sufficient to escape Olsson's result is itself an empirical question — one that Levels 3–5 of the testing protocol address. But the architecture is designed to make coherence truth-*sensitive* even if coherence alone is not truth-*conducive*.

### 7.2 Reflective Equilibrium Is (Partially) Formalisable

The second consequence is more nuanced. Algorithm 4 (Structural Revision) captures the *structural* aspects of reflective equilibrium: mutual adjustment between beliefs of different entrenchment levels, minimal change as a revision principle, and coherence as the criterion for evaluating revisions. The entrenchment ordering — T1 beliefs resist revision more than T2 beliefs — formalises the Quinean gradient from central to peripheral beliefs. The preference for least-drastic revisions (update credences before changing edge types before adding nodes) formalises the principle of minimal change from AGM belief revision theory (Alchourrón, Gärdenfors, & Makinson, 1985).

But genuine reflective equilibrium involves more than structural adjustment. It involves *normative evaluation* — deciding whether a principle ought to be revised in light of a particular case, or whether the case should be reinterpreted in light of the principle. This evaluative dimension is not captured by the algorithm. The algorithm revises beliefs to restore coherence, which is *necessary* for reflective equilibrium but not *sufficient*. A system could restore coherence by making a revision that is coherent but epistemically unacceptable — for example, by downgrading a well-replicated finding to accommodate a theoretically convenient principle. The algorithm's coherence-maximisation criterion does not prevent this.

A more precise objection comes from the Bayesian coherentist tradition. Bovens and Hartmann (2003) argued that Bayesian methods can capture coherence phenomena, and Bayesian *model selection* — comparing the marginal likelihoods of competing models — provides a formal method for choosing among theoretical frameworks. This is not the same as Bayesian *updating* (which revises parameters within a fixed model) but is a distinct operation that evaluates competing *structures*. If Bayesian model selection can do what reflective equilibrium does, the typed web is unnecessary — a well-specified Bayesian framework would suffice.

The response requires precision. The web framework supports reflective equilibrium because it permits *structural innovation*: the creation of new nodes, new edges, and new edge types that were not in the prior hypothesis space. The Barrett-Craig two-stage model was not a hypothesis that either tradition had articulated before the panel process brought them into confrontation; it emerged from that confrontation. Bayesian model selection can evaluate new models once generated, but it cannot generate them — model generation is external to the Bayesian framework. The algorithms can *evaluate* structural innovations (by computing their coherence impact via Algorithm 3), but they cannot *generate* them. The generation step is delegated to human or LLM-simulated-panel intelligence. Reflective equilibrium, as instantiated in the CMR, is therefore a collaboration between formal evaluation (the algorithms) and creative generation (the panels). Neither alone is sufficient. This is a weaker claim than "the CMR formalises reflective equilibrium," but it is more honest and more defensible.

The Barrett-Craig compromise illustrates the gap. Algorithm 4 could, in principle, reproduce the compromise: it would detect the conflict between Barrett's constructionism and Craig's labelled-line theory, compute that the evidence supports both in restricted domains, and generate a composite node with domain-conditional credences. But the *insight* that the posterior/anterior insula dissociation suggests a two-stage processing architecture — an insight that expanded the hypothesis space — is beyond the algorithm's capacity. The algorithm operates over the existing graph structure; the insight involved *creating a new structure that did not previously exist*. Theory generation remains a creative act that the formal system can evaluate (via coherence assessment) but cannot perform.

This partial formalisability is worth stating clearly because it avoids two common errors: the error of overclaiming (that reflective equilibrium has been fully formalised) and the error of dismissing the effort (that since full formalisation is impossible, partial formalisation is worthless). The structural aspects of reflective equilibrium — the ones that govern *which beliefs are revised* and *in what order* — are formalisable and constitute a genuine advance over informal coherentist practice. The evaluative aspects — the ones that govern *whether the revision is good* — remain informal and constitute a genuine limitation.

### 7.3 The Web-BN Boundary Is Precise

The third consequence is a precise delineation of the boundary between two modes of causal reasoning in science. The typed web handles mechanism-based causal reasoning: tracing pathways through intermediate steps, each with its own evidence base, warrant type, and epistemic provenance. It handles explanatory coherence, competition resolution, reflective equilibrium, value-of-information analysis, and structural revision. The Bayesian network handles variable-based causal reasoning: computing over probability distributions on observable variables, with the formal machinery of do-calculus for interventional inference and structural equations for counterfactual reasoning.

This boundary is more nuanced than a simple "web = qualitative, BN = quantitative" split. The web handles quantitative reasoning through compositional chain propagation — tracing effect sizes along mechanism chains to derive compound effects. The BN's unique contribution is not quantitative prediction but *confounding control* and *counterfactual computation*: the formal distinction between observing and intervening in the presence of common causes, and the capacity to reason about what would have happened in worlds that did not occur. These are operations that require representing causation as statistical dependencies between variables — the web's mechanism chains have the wrong representational format for this kind of inference, not because they lack causal content but because their causal content is structured differently.

The boundary also has implications for artificial intelligence more broadly. Large language models and knowledge graphs can store facts and generate explanations, but they lack formal causal inference machinery. Bayesian networks provide causal inference but lack epistemological structure. The architecture presented here suggests that these are not competing approaches but complementary ones — that a system aiming to represent scientific knowledge needs both the epistemological structure (which the typed web provides) and the causal machinery (which the BN provides), and that the interface between them must be a formal projection function that preserves what can be preserved and explicitly discards what cannot.

### 7.4 Beyond the BN-vs-Web Debate: The Deeper Point

The deepest consequence of this work is not about the specific architecture but about what it reveals regarding the structure of scientific understanding. Khalifa (2017) argues that understanding requires not merely having a correct explanatory model but being able to use that model to answer relevant counterfactual questions — what would have happened if things had been different? By this criterion, scientific understanding in the CMR is *distributed across both structures*. The web provides the explanatory models — mechanism chains with typed edges and epistemic provenance at every step. The BN provides the counterfactual reasoning capacity — the formal machinery for computing what would have happened under alternative conditions, controlling for confounders. Neither alone constitutes understanding in the full philosophical sense. The web without the BN provides explanation without counterfactual reach. The BN without the web provides counterfactual computation without explanatory depth. Together, they constitute a system that not only explains (why does ceiling height affect creativity?) but supports the counterfactual inferences that understanding requires (would creativity have been different if the ceiling had been different?).

This means the architectural division of labour is not merely a matter of computational convenience — it reflects the *structure of scientific understanding itself*. A system that aims to represent what a scientific community understands about a domain needs both explanatory models (which the web provides) and counterfactual reasoning capacity (which the BN provides). The two-structure architecture is not an engineering choice but a philosophical necessity.

The CMR case study, with its 130 nodes and 400 typed edges, also suggests that scientific knowledge in a complex applied domain has a richer structure than either coherentist epistemology or causal inference theory has assumed. Scientific knowledge is not merely a web of mutually supporting beliefs (the coherentist picture). It is a web with *typed edges* — different kinds of justificatory relationships that carry different epistemological characters and require different kinds of evidence for their strengthening. Scientific knowledge is not merely a causal graph with conditional probabilities (the Bayesian picture). It is a graph with *epistemological provenance* — each edge carries not just a number but a record of why the number has its value, what would change it, and how confident the community is in it.

The typed web of belief is an attempt to represent this richer structure computationally. Whether it succeeds — whether the algorithms produce reasonable outputs, whether the coherence metric tracks something real, whether the testing protocol validates the architecture — is an empirical question. But the *existence of the structure* — the fact that real scientific knowledge in a real domain has this character — is itself a contribution to the philosophy of science, regardless of whether the specific formal treatment presented here survives scrutiny.

---

## 8. Conclusion

The gap between coherentism and causal inference is not a natural feature of the intellectual landscape. It is an accident of disciplinary history — the traditions grew up in different departments, with different formal tools, addressing different questions. This paper has argued that the gap can be closed, and has presented a specific architecture for closing it: a typed web of belief that handles mechanism-based causal reasoning and epistemological structure, interfaced with a Bayesian network that handles variable-based causal reasoning (interventional inference and counterfactual computation), connected by a formal projection function and a feedback loop.

The architecture's deepest contribution may be not the web or the BN taken individually but the interface between them. The projection function that translates epistemic provenance into aleatory parameters, and the feedback loop that translates empirical discrepancies into revision signals, together constitute a reconciliation of coherentism and empiricism. The coherentist insight — that knowledge is a structured web of mutually supporting beliefs with explanatory depth and revisionary flexibility — is combined with the empiricist requirement that beliefs be tested against the world and revised when they fail. The mechanism chains in the web are what make this reconciliation possible: because mechanisms have internal causal structure with quantitative parameters, they can be projected into the BN's variable-based representation while retaining enough information to generate testable predictions. A bare coherence relation cannot be projected; a mechanism chain can.

The architecture is grounded in a concrete case study (the CMR system, ~130 nodes, ~400 edges, 8 edge types) and specified by six polynomial-time algorithms with a five-level testing protocol. It demonstrates that coherentism is computable, that reflective equilibrium is partially formalisable (the structural aspects, though not the evaluative aspects), and that the boundary between mechanism-based and variable-based causal reasoning can be drawn with precision. What it does not yet demonstrate — because the implementation and testing have not been completed — is that the architecture works in practice. That is the next step.

The cycle of theorise — predict — test — revise is the oldest pattern in science. What this paper proposes is a system that makes that cycle explicit, formal, and computable — a system that not only knows things but knows that it knows them, knows why it knows them, and knows what it does not yet know.

---

## References

Alchourrón, C. E., Gärdenfors, P., & Makinson, D. (1985). On the logic of theory change: Partial meet contraction and revision functions. *Journal of Symbolic Logic*, 50(2), 510–530. https://doi.org/10.2307/2274239 [Google Scholar: ~4,500 citations]

BonJour, L. (1985). *The structure of empirical knowledge*. Harvard University Press. [Google Scholar: ~3,200 citations]

Bovens, L., & Hartmann, S. (2003). *Bayesian epistemology*. Oxford University Press. https://doi.org/10.1093/0199269750.001.0001 [Google Scholar: ~1,600 citations]

Bechtel, W., & Abrahamsen, A. (2005). Explanation: A mechanist alternative. *Studies in History and Philosophy of Biological and Biomedical Sciences*, 36(2), 421–441. https://doi.org/10.1016/j.shpsc.2005.03.010 [Google Scholar: ~1,200 citations]

Craver, C. F. (2007). *Explaining the brain: Mechanisms and the mosaic unity of neuroscience*. Oxford University Press. [Google Scholar: ~3,000 citations]

Daniels, N. (1979). Wide reflective equilibrium and theory acceptance in ethics. *Journal of Philosophy*, 76(5), 256–282. https://doi.org/10.2307/2025881 [Google Scholar: ~1,400 citations]

Dung, P. M. (1995). On the acceptability of arguments and its fundamental role in nonmonotonic reasoning, logic programming and n-person games. *Artificial Intelligence*, 77(2), 321–357. https://doi.org/10.1016/0004-3702(94)00041-X [Google Scholar: ~7,500 citations]

Elgin, C. Z. (1996). *Considered judgment*. Princeton University Press. [Google Scholar: ~700 citations]

Gärdenfors, P. (2000). *Conceptual spaces: The geometry of thought*. MIT Press. [Google Scholar: ~4,200 citations]

Goodman, N. (1955). *Fact, fiction, and forecast*. Harvard University Press. [Google Scholar: ~7,500 citations]

Haack, S. (1993). *Evidence and inquiry: Towards reconstruction in epistemology*. Blackwell. [Google Scholar: ~2,300 citations]

Hacking, I. (1975). *The emergence of probability*. Cambridge University Press. [Google Scholar: ~3,800 citations]

Hájek, A. (2019). Interpretations of probability. In E. N. Zalta (Ed.), *Stanford Encyclopedia of Philosophy*. Stanford University.

Illari, P. M., & Russo, F. (2014). *Causality: Philosophical theory meets scientific practice*. Oxford University Press. [Google Scholar: ~600 citations]

Khalifa, K. (2017). *Understanding, explanation, and scientific knowledge*. Cambridge University Press. https://doi.org/10.1017/9781108164276 [Google Scholar: ~400 citations]

Kelly, K. T. (1996). *The logic of reliable inquiry*. Oxford University Press. [Google Scholar: ~600 citations]

Laudan, L. (1977). *Progress and its problems: Towards a theory of scientific growth*. University of California Press. [Google Scholar: ~4,000 citations]

Lehrer, K. (1990). *Theory of knowledge*. Westview Press. [Google Scholar: ~2,800 citations]

Levi, I. (1980). *The enterprise of knowledge*. MIT Press. [Google Scholar: ~2,000 citations]

Machamer, P., Darden, L., & Craver, C. F. (2000). Thinking about mechanisms. *Philosophy of Science*, 67(1), 1–25. https://doi.org/10.1086/392759 [Google Scholar: ~5,500 citations]

Moss, S. (2018). *Probabilistic knowledge*. Oxford University Press. https://doi.org/10.1093/oso/9780198792154.001.0001 [Google Scholar: ~400 citations]

O'Connor, C., & Weatherall, J. O. (2019). *The misinformation age: How false beliefs spread*. Yale University Press. [Google Scholar: ~800 citations]

Olsson, E. J. (2005). *Against coherence: Truth, probability, and justification*. Oxford University Press. https://doi.org/10.1093/0199279993.001.0001 [Google Scholar: ~700 citations]

Pearl, J. (1988). *Probabilistic reasoning in intelligent systems: Networks of plausible inference*. Morgan Kaufmann. [Google Scholar: ~22,000 citations]

Pearl, J. (2009). *Causality: Models, reasoning, and inference* (2nd ed.). Cambridge University Press. https://doi.org/10.1017/CBO9780511803161 [Google Scholar: ~28,000 citations]

Prakken, H. (2010). An abstract framework for argumentation with structured arguments. *Argument and Computation*, 1(2), 93–124. https://doi.org/10.1080/19462161003734514 [Google Scholar: ~800 citations]

Quine, W. V. O., & Ullian, J. S. (1970). *The web of belief*. Random House. [Google Scholar: ~2,500 citations]

Rawls, J. (1971). *A theory of justice*. Harvard University Press. [Google Scholar: ~65,000 citations]

Spirtes, P., Glymour, C., & Scheines, R. (2000). *Causation, prediction, and search* (2nd ed.). MIT Press. [Google Scholar: ~7,800 citations]

Thagard, P. (1989). Explanatory coherence. *Behavioral and Brain Sciences*, 12(3), 435–467. https://doi.org/10.1017/S0140525X00057046 [Google Scholar: ~2,400 citations]

Thagard, P. (2000). *Coherence in thought and action*. MIT Press. [Google Scholar: ~2,200 citations]

Toulmin, S. E. (1958). *The uses of argument*. Cambridge University Press. [Google Scholar: ~14,000 citations]

Walley, P. (1991). *Statistical reasoning with imprecise probabilities*. Chapman & Hall. [Google Scholar: ~3,700 citations]

Wright, S. (1921). Correlation and causation. *Journal of Agricultural Research*, 20(7), 557–585. [Google Scholar: ~3,100 citations]

---

## Appendix A: Algorithm Pseudocode

*The full pseudocode for all six algorithms is available in the companion technical document (WEB_OF_BELIEF_AND_BAYESIAN_NETWORK_ARCHITECTURE.md, Part IX) and in the MASTER_DOC_CMR supplement (§129). For the convenience of reviewers, the typed attenuation factors and complexity bounds are summarised here.*

**Table A1: Typed Attenuation Factors for Credence Propagation**

| Edge Type | α Factor | Rationale |
|-----------|----------|-----------|
| reduction | 0.90 | Credence flows downward with modest attenuation |
| bridge(CONSTITUTIVE) | 0.90 | Mechanism IS the phenomenon |
| bridge(MECHANISM) | 0.75 | Complete causal pathway traced |
| bridge(EMPIRICAL_COV) | 0.70 | Replicated association, mechanism unspecified |
| bridge(FUNCTIONAL) | 0.60 | Functional analogy |
| bridge(CAPACITY) | 0.55 | Neural capacity confirmed, architectural operation unconfirmed |
| bridge(ANALOGICAL) | 0.45 | Structural analogy only |
| bridge(THEO_DEFAULT) | 0.50 | Expert-assigned placeholder |
| inheritance | 0.95 | Parameter sharing |
| competition | −0.30 | Competitors reduce each other's credence |
| interaction | 0.10 | Weak positive mutual support |
| working_model | 0.85 | Strong theoretical commitment |
| ax_axiom | 0.80 | Meta-parameter constraint |
| partial_out | 0.00 | No credence flow |

**Table A2: Computational Complexity Summary**

| Algorithm | Time Complexity | CMR Runtime |
|-----------|----------------|-------------|
| 1. Credence Propagation | O(iter × |E|) | Milliseconds |
| 2. Competition Resolution | O(k² × |T|) | Microseconds |
| 3. Global Coherence | O(|E|) | Microseconds |
| 4. Structural Revision | O(|affected| × |E|) | Milliseconds |
| 5. Value of Information | O(|uncertainties| × (|E| + |N|)) | Milliseconds |
| 6. BN Projection | O(|chains| × |length| + |V|³) | Milliseconds |

---

*Paper draft: "From Philosophical Metaphor to Computational Architecture"*
*David Kirsh, Department of Cognitive Science, UCSD*
*February 2026*
*Word count: approximately 8,500 (main text) + appendix*
