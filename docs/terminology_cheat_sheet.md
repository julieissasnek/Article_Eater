**ATLAS Architecture**

**Terminology & Concept Cheat Sheet**

*Epistemic Warrant Graph · Bayesian Network · Projection Bridge*

February 2026 · v1.0

**1. The Three-Layer Architecture at a Glance**

The ATLAS system has three layers. Each answers a different question,
uses a different formalism, and carries a different kind of number. They
are connected by the projection function π, which translates from the
epistemic layer to the operational layer.

  --------------------------- ------------------------------------------------------------------------------------- ------------------------------------------------------------------------------------------------ -------------------------------------------------------------------
                              **Epistemic Warrant Graph (EWG)**                                                     **Projection Bridge (π)**                                                                        **Bayesian Network (BN)**
  **Core question**           How well-supported is each causal claim, and by what kind of evidence?                How should epistemic assessments translate into operational parameters for a specific context?   Given the operational model, what will happen if we intervene?
  **What it represents**      The full body of scientific evidence bearing on environment--behavior relationships   The transfer logic: how lab evidence maps to a real building                                     The operational causal model for a specific architectural context
  **Graph type**              Labeled directed multigraph (cycles OK, parallel edges OK)                            Function: EWG → BN                                                                               Directed acyclic graph (DAG) --- standard Pearl SCM
  **What the numbers mean**   Warrant strength (ω): degree of belief in the evidential bridge                       Discount factor (d): how much survives transfer, based on warrant type                           Conditional probability (CPT): what actually happens in the world
  **What the edges mean**     \"Evidence of type τ supports the claim that A relates to C\"                         Translates each EWG edge into a CPT contribution                                                 \"A causally influences C in this specific context\"
  **Number range**            ω ∈ (0, 1)                                                                            d ∈ (0, 1), fixed by warrant type                                                                CPT entries ∈ \[0, 1\], columns sum to 1.0
  **Who populates it**        Article Eater + expert review (from published research)                               System architecture (fixed mapping from types to discounts)                                      Computed by π from EWG inputs
  **Can it have cycles?**     Yes --- evidential support can be mutual                                              N/A                                                                                              No --- must be a DAG (Pearl's requirement)
  --------------------------- ------------------------------------------------------------------------------------- ------------------------------------------------------------------------------------------------ -------------------------------------------------------------------

**2. Epistemic Warrant Graph (EWG) --- Key Concepts**

The EWG is the epistemic layer. It represents not the world but our
knowledge about the world. Every element in the EWG answers some version
of: "What do we know, how do we know it, and how confident should we
be?"

  ---------------------- ---------------------------------------------- ---------------------------------------------------------------------------------------------------- -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  **Concept**            **Symbol**                                     **Formal Definition**                                                                                **Plain English / Intuition**
  **Node**               n ∈ N                                          A proposition about an environment--behavior relationship                                            A claim: e.g., "Daylight exposure elevates serotonin." Each node is a statement that can be true or false, well-supported or poorly supported.
  **Edge**               e ∈ E, e = (n₁, n₂)                            A directed connection from source node to target node, carrying type and weight                      A piece of evidence bearing on the target claim. The edge says: "This specific evidence supports (or undermines) that claim."
  **Warrant Type**       τ : E → T                                      A function assigning each edge one of seven types from the set T = {CONSTITUTIVE, MECHANISM, \...}   What kind of evidence is this? Is it an identity? A known causal pathway? A replicated correlation? An analogy? Each type tells you something different about how trustworthy the evidence is and how it will behave in a new context.
  **Warrant Strength**   ω : E → (0,1)                                  The confidence weight: degree of belief that this specific evidential bridge holds                   How good is this particular piece of evidence? High ω (e.g., 0.90) means strong, well-replicated evidence. Low ω (e.g., 0.40) means weak, preliminary, or contested evidence. This is NOT a probability of an outcome --- it is a judgment about evidence quality.
  **Discount Factor**    d : T → (0,1)                                  A ceiling on transfer reliability, determined by warrant type                                        How much of the lab finding survives when you move to a real building? Set by the type of evidence, not by any individual study. CONSTITUTIVE evidence (d = 0.95) almost fully transfers. THEORETICAL\_DEFAULT evidence (d = 0.25) mostly doesn't.
  **Parallel Edges**     Multiple e₁, e₂, \... between same node pair   Multigraph: multiple edges from n₁ to n₂ with different types/weights                                Different lines of evidence for the same claim. E.g., daylight→serotonin might have both a MECHANISM edge (Lambert et al. identified the pathway) and an EMPIRICAL\_COVARIANCE edge (replicated in epidemiological studies). More independent lines = stronger support.
  ---------------------- ---------------------------------------------- ---------------------------------------------------------------------------------------------------- -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

**2.1 The Seven Warrant Types**

Each warrant type captures a distinct epistemic relationship between
evidence and claim. They are ordered by expected transfer reliability
(invariance range).

  --------------------------- ------- ------------------------------------------------------------------------------------------------------------------ ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  **Warrant Type**            **d**   **What It Means**                                                                                                  **Example (Environmental Psychology)**
  **CONSTITUTIVE**            0.95    Identity / definitional relationship. The lab variable IS the architectural variable. Not a causal claim at all.   Ceiling height IS room volume ÷ floor area. Window-to-wall ratio IS glazed area ÷ wall area. These hold in every building by definition.
  **MECHANISM**               0.80    Known causal pathway with identified entities and activities. We know WHY A causes C.                              Daylight → retinal ganglion cells → raphe nuclei → serotonin. The entire chain is identified. Transfers unless a specific link breaks.
  **EMPIRICAL\_COVARIANCE**   0.80    Replicated statistical association without known mechanism. We know THAT A correlates with C but not WHY.          Hospitals with more daylight show faster patient recovery (Beauchemin & Hays, 1996). The correlation replicates, but the causal pathway is unclear. Vulnerable to confounding.
  **FUNCTIONAL**              0.65    Same functional role without known mechanism. The system does the same job, but we don't know how.                 Biophilic elements in offices "serve as stress reducers" (Kaplan, 1995). The functional claim is supported but the mechanism (attention restoration? autonomic regulation?) is debated.
  **CAPACITY**                0.55    The system CAN produce the effect but hasn't been shown to in this context. Possibility, not actuality.            Human auditory cortex can discriminate reverberation times (demonstrated in lab). Therefore, room acoustics COULD affect perceived spaciousness. But no one has shown this in a real building.
  **ANALOGICAL**              0.40    Cross-domain transfer via structural similarity. Evidence from domain X applied to domain Y by analogy.            Fractal patterns reduce stress in natural landscapes (Hägerhäll et al., 2004). By analogy, fractal patterns in building facades should reduce stress. The analogy is plausible but unverified.
  **THEORETICAL\_DEFAULT**    0.25    Theoretical commitment without empirical evidence. A placeholder for where evidence is needed.                     Predictive coding theory predicts that moderately complex facades should minimize prediction error. Theoretically motivated but no direct test.
  --------------------------- ------- ------------------------------------------------------------------------------------------------------------------ ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

**3. Bayesian Network (BN) --- Key Concepts**

The BN is the operational layer. It represents the world ---
specifically, the causal structure that holds (or is projected to hold)
in a particular architectural context. Every element in the BN answers
some version of: "What will happen if we do X?"

  ----------------------------------------- --------------------- ------------------------------------------------------------------------------------------------------------- --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  **Concept**                               **Symbol**            **Formal Definition**                                                                                         **Plain English / Intuition**
  **Node**                                  X ∈ V                 A random variable representing a measurable or manipulable quantity                                           Something the architect can observe, measure, or control. E.g., "daylight level," "occupant mood," "recovery time." Unlike EWG nodes (which are propositions), BN nodes are variables that take values.
  **Edge**                                  X → Y                 A directed edge indicating X is a direct cause of Y in this context                                           A causal claim: changing X will change Y (not just correlation). The edge is UNTYPED --- it says only that causation exists, not what kind of evidence established it. That information lives in the EWG.
  **Conditional Probability Table (CPT)**   P(X \| Pa(X))         For each configuration of parent values, a probability distribution over X's values. Columns sum to 1.        What actually happens in the world. "If daylight is high, there is a 72% chance serotonin is elevated." This is a frequency/propensity claim, not a judgment about evidence quality. It is the object-level content that the EWG's meta-level judgments are about.
  **Prior Distribution**                    P(X) for root nodes   Probability distribution for nodes with no parents                                                            The baseline rate of a variable before any causal influence. E.g., P(mood = positive) = 0.50 in the general population before any daylight intervention.
  **Structural Equation**                   X = f(Pa(X), U)       Each node's value is a function of its parents plus exogenous noise U                                         Pearl's way of encoding the CPT. The function f specifies exactly how parent values combine to determine the child. The noise U captures individual variation.
  **DAG Constraint**                        No directed cycles    The graph must be a directed acyclic graph                                                                    No circular causation allowed. If A causes B, then B cannot cause A (at the same time). This is a hard requirement of Pearl's framework --- unlike the EWG, which permits cycles.
  **do-Calculus**                           P(Y \| do(X = x))     Pearl's formal rules for computing interventional distributions from observational data and graph structure   The computational engine. Given the graph and CPTs, the do-calculus tells you: if you physically set X to value x (not just observe it), what is the probability distribution over Y? This is the whole point of the BN.
  ----------------------------------------- --------------------- ------------------------------------------------------------------------------------------------------------- --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

**4. The Projection Bridge (π) --- Key Concepts**

The projection function π is the interface between the epistemic layer
(EWG) and the operational layer (BN). It translates "how well-supported
is the evidence?" into "what CPT values should the BN use in this
context?"

  ---------------------------------- ------------------------------------------ -------------------------------------------------------------------------------------------------------------------- -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  **Concept**                        **Symbol**                                 **Formal Definition**                                                                                                **Plain English / Intuition**
  **Projection Function**            π : EWG → BN                               A function that takes the EWG (with all its typed, weighted edges) and produces a BN (with DAG structure and CPTs)   The bridge between "what we know" and "what we predict." It decides: given the evidence we have, what operational model should the architect use?
  **Log-Odds Transform**             logit(p) = log(p/(1−p))                    Maps probabilities (0,1) to the real line (−∞, +∞) for linear combination                                            The mathematical trick that makes discounting work. In log-odds space, you can multiply by the discount factor without risking impossible probabilities. The sigmoid function maps back to (0,1).
  **Discount Application**           logit(p\_target) = d · ω · logit(p\_lab)   The lab-derived log-odds are attenuated by the discount factor and warrant strength                                  The core operation. Take the lab finding, convert to log-odds, multiply by d (how much this type of evidence transfers) and ω (how strong this particular evidence is), convert back to probability. The result is the BN's CPT entry for this edge.
  **Ignorance Prior**                p = 0.50                                   The probability assigned when no evidence exists (maximum entropy)                                                   The default: if we know nothing, we assign 50/50. In log-odds, this is 0. The discount factor moves the CPT away from 0.50 toward the lab-derived value, but never all the way (except for CONSTITUTIVE evidence, which nearly reaches it).
  **Multi-Edge Aggregation**         Σ d\_i · ω\_i · logit(p\_i)                When multiple EWG edges project to the same BN edge, their log-odds contributions are summed                         Multiple lines of evidence converge. A MECHANISM edge and an EMPIRICAL\_COVARIANCE edge for the same claim combine additively in log-odds space, producing stronger support than either alone.
  **Structural Collapse**            EWG path → BN edge                         A chain of EWG edges through intermediate/latent nodes collapses into a single BN edge between observable nodes      The BN only has nodes the architect can see or control. So a five-step mechanistic chain in the EWG (daylight → retinal cells → raphe nuclei → serotonin → mood) becomes a single edge (daylight → mood) in the BN. The effective discount is min(d) along the chain.
  **Minimum-Discount Composition**   d\_eff(path) = min(d(e\_i))                The effective discount for a multi-step path is the minimum discount along the path                                  The weakest link dominates. A chain of MECHANISM edges (d = 0.80 each) ending in one ANALOGICAL edge (d = 0.40) has effective discount 0.40. The system cannot claim stronger evidence than its weakest step supports.
  ---------------------------------- ------------------------------------------ -------------------------------------------------------------------------------------------------------------------- -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

**5. The Critical Distinction: Three Different Numbers**

The single most important thing to understand about the ATLAS
architecture is that there are three categorically different kinds of
number, and confusing them produces nonsense.

  -------------------------- ---------------------------------------------------------------------------------------------- ------------------------------------------------------------------------------------------- -------------------------------------------------------------------------------------------------------------------
                             **Warrant Strength (ω)**                                                                       **Discount Factor (d)**                                                                     **Conditional Probability (CPT)**
  **Lives in**               EWG (on each edge)                                                                             Bridge (determined by warrant type)                                                         BN (on each edge)
  **What it measures**       How well-supported is this specific piece of evidence?                                         How much of any evidence of this TYPE survives transfer to a new context?                   What actually happens in the world? Given parent values, what is the probability of each outcome?
  **Kind of uncertainty**    EPISTEMIC: reducible by gathering more/better evidence                                         EPISTEMIC: reflects structural properties of evidence types                                 ALEATORY: irreducible randomness in how people respond
  **Who sets it**            Determined from published evidence (Article Eater + expert review)                             Fixed by system architecture (not adjustable per study)                                     Computed by the projection function π
  **Can it change?**         Yes --- new studies, replications, or retractions change ω                                     No --- unless the theoretical justification for the type hierarchy is revised               Yes --- whenever the EWG is updated, π recomputes the CPTs
  **What does 0.80 mean?**   "We are quite confident this evidence is solid" (strong studies, good replication)             "This type of evidence retains 80% of its information when transferred" (e.g., MECHANISM)   "There is an 80% chance of this outcome given these inputs" (e.g., P(serotonin = high \| daylight = high) = 0.80)
  **Example**                ω = 0.85 on Lambert et al.'s daylight→serotonin finding (well-replicated, clean methodology)   d = 0.80 for MECHANISM (mechanistic knowledge transfers well across contexts)               P(mood = positive \| serotonin = elevated) = 0.72 in the BN for this hospital
  **Prose term**             "Degree of belief in the evidential bridge"                                                    "Transfer reliability"                                                                      "Probability of outcome given inputs"
  -------------------------- ---------------------------------------------------------------------------------------------- ------------------------------------------------------------------------------------------- -------------------------------------------------------------------------------------------------------------------

**6. How Key Phenomena Appear in Each Layer**

**6.1 Confounds**

  ---------------- ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  **Layer**        **How Confounds Appear**                                                                                                                                                                                                                                                                               **What You Can Do About Them**
  **EWG**          A confound is implicit in the warrant type. EMPIRICAL\_COVARIANCE warrants carry the warning: "this correlation might be confounded." MECHANISM warrants partially protect against confounding because the pathway is identified. CONSTITUTIVE warrants are immune (you can't confound an identity).   The warrant type itself is a summary statistic for confounding risk. No need to enumerate every possible confounder as a node. Instead, the type tells you HOW WORRIED to be.
  **Bridge (π)**   The discount factor for EMPIRICAL\_COVARIANCE (d = 0.80) is already attenuated relative to what it would be if the mechanism were known, partly because of confounding risk.                                                                                                                           When projecting EMPIRICAL\_COVARIANCE edges, π applies a discount that implicitly accounts for the possibility that the correlation won't transfer due to confounding differences.
  **BN**           A confound is a common cause: Z → A and Z → C. It must be an explicit node in the graph. If Z is unmeasured, Pearl's framework requires special identification strategies (back-door, front-door, instrumental variables).                                                                             Pearl's do-calculus handles confounds rigorously IF the graph is correctly specified and the confound is either measured or can be circumvented. But you must KNOW the confound exists.
  ---------------- ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

**6.2 Interactions / Effect Modifiers**

  ---------------- --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- ----------------------------------------------------------------------------------------------------------------------------------------------------------------
  **Layer**        **How Interactions Appear**                                                                                                                                                                                                                                                 **What You Can Do About Them**
  **EWG**          An interaction appears as a modifier on an edge's warrant strength. "The evidence for A→C was gathered at a specific level of B. If B differs in the target context, the warrant strength should be reduced." Can also appear as a separate edge from B to the A→C claim.   The EWG can represent the EPISTEMIC STATUS of an interaction: do we know about it? How well-established is the moderation? Is it mechanistic or just observed?
  **Bridge (π)**   If the target context differs from the source on a known moderator, π can further attenuate the projected CPT. The interaction affects how much of the lab finding transfers.                                                                                               Context-specific projection: the same EWG can produce different BNs for different target contexts, depending on known moderating variables.
  **BN**           An interaction is in the CPT: P(C \| A, B) ≠ P(C \| A) · P(C \| B). The functional form of the structural equation C = f(A, B, U) is non-separable in A and B.                                                                                                              Standard probability calculus. The CPT fully encodes the interaction if the moderator B is a node in the BN.
  ---------------- --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- ----------------------------------------------------------------------------------------------------------------------------------------------------------------

**6.3 Theory vs. Mechanism**

  --------------------- -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  **Layer**             **How Each Appears**                                                                                                                                                                                                             **The Difference**
  **EWG (Theory)**      A high-level organizing principle. Lives at the top of the graph. Generates predictions (edges to lower-level claims) but is not itself directly testable. Warrant type: THEORETICAL\_DEFAULT (d = 0.25).                        A THEORY explains WHY a mechanism exists and predicts what form mechanisms should take. Predictive coding predicts that cortical hierarchies minimize prediction error. This is a framework, not a spatiotemporally located process.
  **EWG (Mechanism)**   A specific process with identified entities and activities. Lives in the middle of the graph. Connects observable inputs to observable outputs through intermediate (often latent) states. Warrant type: MECHANISM (d = 0.80).   A MECHANISM is a specific physical/biological process in the world. The retinohypothalamic pathway is a mechanism. It has parts, activities, and spatial-temporal organization. It CAN BE intervened on.
  **BN**                Theories do NOT appear in the BN. They are too abstract to operationalize as variables with probability distributions.                                                                                                           Mechanisms may or may not appear, depending on whether their intermediate states are observable. If collapsed: the mechanism contributes to the CPT of a direct BN edge. If expanded: the intermediate states appear as BN nodes (rare, only when measurable).
  --------------------- -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

**7. Why the BN Has Fewer Edges Than the EWG**

The BN is always a strict subset of the EWG's content. Several classes
of EWG structure are absent from the BN:

  ----------------------------------------------------------------------------------------------------- -------------------------------------------------------------------------------------- -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  **What's in the EWG but not the BN**                                                                  **Why It's Excluded**                                                                  **Where Its Information Goes**
  **Latent/unobservable intermediate states (e.g., raphe nuclei activity, prediction error signals)**   The architect cannot measure or manipulate them. BN nodes must be actionable.          Collapsed into the CPTs of BN edges between observable nodes. Their contribution is encoded in the numerical values, not the graph structure.
  **Theoretical claims (e.g., "predictive coding governs aesthetic response")**                         Too abstract to operationalize as a random variable with a probability distribution.   Contributes to warrant strength (ω) of lower-level claims. A mechanism that is predicted by a theory has slightly higher ω than an orphan mechanism.
  **Parallel edges (multiple evidence types for the same relationship)**                                The BN has exactly one edge (or none) between any pair of nodes. No parallel edges.    Multiple EWG edges between the same pair are aggregated by π (summing log-odds contributions) into a single CPT entry in the BN.
  **Cycles (A supports B which supports A)**                                                            The BN must be a DAG. Cycles violate this requirement.                                 Cycles in the EWG represent mutual epistemic support. They are resolved during projection (e.g., by temporal unrolling or equilibrium computation).
  **Warrant type annotations**                                                                          BN edges are untyped. Pearl's framework does not distinguish kinds of evidence.        Consumed by the projection function. The type determines the discount factor d, which shapes the CPT values. After projection, the type information is "baked in" to the CPT.
  **Warrant strength (ω) annotations**                                                                  BN edges carry CPTs, not evidence quality judgments.                                   Consumed by the projection function. ω modulates how much of the lab finding is retained in the CPT. After projection, ω is "baked in."
  ----------------------------------------------------------------------------------------------------- -------------------------------------------------------------------------------------- -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

The relationship is: the EWG is the comprehensive epistemic record; the
BN is the operational distillation. The EWG knows everything; the BN
knows only what the architect needs. The projection function π is the
responsible compression that transforms one into the other, preserving
the quantitative implications of the evidence while discarding the
metadata about evidence type and quality (which has already done its
work in shaping the CPTs).

**8. Quick Reference: Symbols and Abbreviations**

  ------------ ------------------------------- -------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  **Symbol**   **Name**                        **Definition**
  EWG          Epistemic Warrant Graph         The labeled directed multigraph W = (N, E, τ, ω) representing the body of evidence
  BN           Bayesian Network                The directed acyclic graph with CPTs, used for causal inference (Pearl's framework)
  π            Projection Function             The bridge: EWG → BN. Translates epistemic assessments into operational parameters
  N            Node set (EWG)                  Propositions about environment--behavior relationships
  V            Variable set (BN)               Random variables representing measurable/manipulable quantities
  E            Edge set                        Directed connections carrying evidence (EWG) or causation (BN)
  τ            Warrant Type                    One of seven labels classifying the kind of evidential bridge: {CONSTITUTIVE, MECHANISM, EMPIRICAL\_COVARIANCE, FUNCTIONAL, CAPACITY, ANALOGICAL, THEORETICAL\_DEFAULT}
  ω            Warrant Strength                Confidence weight ∈ (0,1). Degree of belief in the evidential bridge. Prose: "warrant strength"
  d            Discount Factor                 Transfer reliability ∈ (0,1). How much of the evidence survives context transfer. Set by τ, not by individual studies
  CPT          Conditional Probability Table   P(X \| Pa(X)). For each parent configuration, a probability distribution over X's values. Columns sum to 1. The operational, object-level content of the BN
  Pa(X)        Parents of X                    The set of nodes with directed edges into X
  do(X=x)      Intervention                    Pearl's operator: physically set X to value x, cutting all incoming edges to X
  SCM          Structural Causal Model         Pearl's framework: a set of structural equations X = f(Pa(X), U) plus a DAG
  PCH          Pearl Causal Hierarchy          The "ladder of causation": Level 1 (Association), Level 2 (Intervention), Level 3 (Counterfactual)
  CHT          Causal Hierarchy Theorem        Proves the three PCH levels almost always separate: lower-level data cannot answer higher-level questions
  ------------ ------------------------------- -------------------------------------------------------------------------------------------------------------------------------------------------------------------------
