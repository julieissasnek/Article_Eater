# §179: Math Cards — The Three-Layer Explanation Architecture

*Last revised: 2026-03-04*

---

## §179.1: Why Mathematical Transparency Matters (Epistemic Motivation)

ATLAS is a mathematical system. It uses Bayesian belief networks to propagate credences. It calculates coherence metrics from the structure of the web of belief. It computes typed warrant discount factors. It measures the entrenchment of beliefs using Quinean centrality. It applies factor analysis to discover latent theoretical molecules. It scores the staleness of evidence and the value of answering open questions. These operations are rigorous, precise, and—crucially—not self-explanatory.

A practicing architect who encounters an ATLAS prediction ("high-coherence expectation: natural daylight will improve mood for hospital patients, credence 0.74") is entitled to ask: What does credence 0.74 mean? Why not 0.70 or 0.80? How did the system weight the evidence? Where do the numbers come from? If the architect cannot answer these questions, the system is a black box, and no amount of mathematical rigor underneath justifies treating it as trustworthy.

Conversely, a neuroscientist serving on an ATLAS domain panel who reviews a coherence calculation might ask: What is the exact algorithm for computing negative coherence? How are cycles weighted? What is the mathematical proof that this coherence metric satisfies these desiderata? If the system cannot answer with precision, it has lost the right to claim rigor.

These two users—architect and neuroscientist—have fundamentally different relationships to the mathematics. The architect needs intuition without equations. The neuroscientist needs equations without handwaving. The scientist writer explaining the mechanism to a health journalist needs a middle ground: clear mathematics with every symbol defined, but explained one step at a time rather than dumped as formal specification.

**Mathematical transparency serves three epistemic functions:**

First, it *enables legitimate skepticism*. A user who understands how a number was computed can critique the computation. "I see you used a discount factor of 0.80 for mechanism warrants, but I think it should be 0.85" is a substantive disagreement that can be resolved. "This number looks suspicious" is not. Transparency converts vague concern into actionable critique.

Second, it *creates shared understanding across disciplines*. A psychologist, an architect, and a systems engineer do not speak the same technical language. But all three can read an equation with defined variables. The equation becomes the lingua franca. This is why the periodic table works across chemistry, materials science, physics, and geology: everyone agrees on what the symbols mean, so the table can be discussed with equal authority by experts from different fields.

Third, it *binds claims to evidence*. When an ATLAS template asserts "high coherence for the biophilia pathway to stress reduction," the assertion is only as strong as the evidence that supports it. But the evidence lives in the web of belief—in other nodes, other templates, other warrants. If the user cannot see the chain of reasoning from evidence to conclusion, they cannot evaluate whether the chain is sound. Mathematical transparency makes the chain visible.

This section describes how ATLAS addresses these needs through a three-layer explanation architecture for every mathematical operation in the system. The architecture is grounded in principles of science communication (clear prose before equations, equations with defined variables, formal specification for the technically sophisticated) and in epistemology (acknowledging uncertainty, showing provenance, enabling critique).

---

## §179.2: The Three Layers — Intuition, Transparent, Details

Every mathematical operation in ATLAS that a user might encounter—whether directly (as an architect reading a prediction) or indirectly (as a panel member reviewing a template)—is documented at three layers of explanation. The layers are cumulative: the Details layer includes everything in the Transparent layer, which includes the intuition from the Intuition layer. But a user need only read the layer appropriate to their mathematical sophistication.

### Layer 1: Intuition (Science-Writer Quality Explanation, No Equations)

The Intuition layer explains what the math does and why it matters, using analogies, examples, and concrete scenarios. The target audience is anyone with a high school education and general intelligence but no specialized mathematical training: designers, clinicians, patients, policymakers, environmental professionals, students.

The writing follows principles of science communication distilled from Sagan, Gawande, Williams, and Pinker: lead with the question the math answers, use concrete examples before abstractions, acknowledge uncertainty, and explain mechanisms rather than just reporting findings.

Example (Intuition layer for Bayesian credence updates):

> When ATLAS encounters a new finding that contradicts an existing belief, it must decide how much to change its mind. The system uses a principle borrowed from Bayesian reasoning: the strength of the update depends on both how surprising the new evidence is and how firmly the old belief was held. Think of it like a judge weighing new testimony. If the judge was already strongly convinced of guilt (high prior credence), a single eyewitness account (weak evidence) might not shift the conviction much. But if the judge was uncertain, the same evidence might tip the balance. Conversely, if the judge had settled the case based on prior convictions alone, and suddenly multiple forensic experts arrive with contradictory testimony, the judge should shift belief more dramatically. ATLAS uses this same intuition: the impact of new evidence depends on how surprising it is relative to what you already believe, and how firm that prior belief was.

Notice: no equations, one worked-through analogy, clear problem statement. The reader knows what the math is *for* and why it matters in principle.

### Layer 2: Transparent Explanation (Equations with Step-by-Step Walkthrough)

The Transparent layer introduces equations one at a time. Every variable is defined in plain English. Every mathematical step is explained in words. The target audience is researchers, advanced students, domain experts who want to understand the logic but do not require full formal specification.

The writing follows this structure for each equation: (a) plain-English statement of what we are doing; (b) the equation itself; (c) definition of each variable; (d) worked numerical example; (e) intuitive explanation of what the equation says.

Example (Transparent layer for Bayesian credence updates):

> **Plain-English Statement.** When new evidence arrives, we update our belief in a hypothesis using a formula called Bayes' rule. This formula answers the question: given what we already believed, how should new evidence change that belief?
>
> **The Equation:**
>
> c'(H) = c(H) × P(E|H) / P(E)
>
> **Variable Definitions:**
>
> - c(H) = your credence (belief) in hypothesis H *before* seeing the evidence. This is the prior. For example, if you think there is a 60% chance that daylighting improves mood, c(H) = 0.60.
> - c'(H) = your credence in H *after* seeing the evidence. This is the posterior. This is what we are calculating.
> - P(E|H) = the probability you would observe this evidence *if* the hypothesis were true. This is the likelihood. For example, if daylighting really does improve mood, how likely would you be to see a study showing improvement? High probability (0.90) if the hypothesis is true.
> - P(E) = the probability you would observe this evidence *regardless* of whether the hypothesis is true. This is the normalizer. It accounts for the fact that you might see a study showing improvement even if daylighting does not actually improve mood (perhaps due to publication bias or chance). We estimate P(E) by considering all possible ways the evidence could arise.
>
> **Worked Example:**
>
> Suppose you initially believe P(daylighting improves mood) = 0.60. A new well-designed study reports improvement. You estimate:
> - P(study shows improvement | daylighting improves mood) = 0.85 (well-designed studies usually detect true effects, but not always)
> - P(study shows improvement | regardless) = 0.50 (accounting for publication bias and chance, even without a real effect you might see a positive study about half the time)
>
> Then: c'(H) = 0.60 × (0.85 / 0.50) = 0.60 × 1.70 = 1.02
>
> Wait—this exceeds 1, which is impossible for a probability. This means we made an error in our estimate of P(E). [Explanation of how to compute P(E) correctly using the law of total probability.]
>
> **What This Means Intuitively:**
>
> The ratio P(E|H) / P(E) is called the Bayes factor. If this ratio exceeds 1, the evidence supports the hypothesis (makes it more likely). If the ratio is less than 1, the evidence undermines the hypothesis. The larger the ratio, the more the evidence should shift your belief. This aligns with the intuitive principle: surprising evidence (unlikely unless the hypothesis is true) should change your mind more than expected evidence.

Notice: equations are introduced one at a time, every variable is defined in plain English, a worked example shows concrete numbers, and the intuition is explained in the last paragraph. A reader can follow the logic without specialist knowledge, but can also see the precise mathematical operation.

### Layer 3: Details (Full Formal Specification)

The Details layer provides complete mathematical notation, proofs or derivations, implementation notes, connections to the literature (information theory, Bayesian epistemology, statistics), and edge cases.

The target audience is developers, research mathematicians, and readers who want full precision and are comfortable with formal notation. This layer is not for intuitive understanding; it is for verification and formal analysis.

Example (Details layer for Bayesian credence updates):

> **Formal Statement.**
>
> Let H denote a hypothesis in the Epistemic Network represented as a Bayesian random variable. Let h denote a specific value (truth value) of H. Let E denote an observed event (evidence), with possible values e₁, e₂, ..., eₙ. The posterior credence assigned to h given E is computed using Bayes' rule:
>
> P(h | E) = P(E | h) · P(h) / P(E)
>
> where the marginal probability is expanded using the law of total probability:
>
> P(E) = Σᵢ P(E | hᵢ) · P(hᵢ)
>
> This can be rewritten in log-odds space to improve numerical stability:
>
> logit(P(h | E)) = logit(P(h)) + log(P(E | h) / P(E | ¬h))
>
> The second term is the log-likelihood ratio (log-Bayes factor), denoted Λ(E).
>
> **Computational Implementation.**
>
> In ATLAS's implementation, credences are stored and updated in log-odds space throughout to maintain numerical precision when dealing with very small probabilities (e.g., 1e-12). [Implementation pseudocode.] [Discussion of numerical stability, convergence guarantees, edge cases where posterior is 0 or 1.]
>
> **Theoretical Connections.**
>
> Bayes' rule can be derived from first principles in information theory via the principle of maximum entropy (Jaynes, 2003). It is the unique rule satisfying the Cox axioms of rational belief updating. It is the optimal decision rule under expected utility maximization for a wide class of loss functions. See references [list].
>
> **Edge Cases and Assumptions.**
>
> This derivation assumes conditional independence of evidence: P(E₁, E₂ | H) = P(E₁ | H) · P(E₂ | H) given H. This assumption fails when evidence items are correlated, requiring more complex calculations. [Discussion of how ATLAS handles correlated evidence.]

Notice: formal notation, precise definitions, implementation details, and pointers to the theoretical literature. A mathematician or systems engineer can verify the approach against published work.

---

## §179.3: The Math Card Inventory — What ATLAS Formalizes

ATLAS implements substantial mathematical machinery. The following ten mathematics domains require cards in all three layers (Intuition, Transparent, Details):

### 1. **Typed Credence Propagation with Differential Attenuation** (§129)

The system propagates belief credences through a network of causal and evidential links, using message-passing algorithms. Each link attenuates credence depending on the type of warrant (constitutive vs. mechanism vs. empirical, etc.) and the quality of the supporting evidence.

**Math concepts:** message-passing in Bayesian networks, directed acyclic graphs (DAGs), conditional probability tables (CPTs), marginalization, the d-separation criterion, attenuation factors, operator composition, convergence criteria.

**Audience needs:** Architects need to know why a belief's credence is lower than the evidence seems to justify (answer: transmission loss through the network). Panel members need to understand message-passing order and whether the system converges to consistent credences. Developers need full specifications for the update algorithm.

### 2. **Warrant Discount Functions: The α Hierarchy** (§129.1)

Each of the seven warrant types (CONSTITUTIVE, MECHANISM, EMPIRICAL_ASSOCIATION, FUNCTIONAL, CAPACITY, ANALOGICAL, THEORY_DERIVED) carries a transfer reliability discount factor d(τ) that determines how much evidence of that type survives transfer to a new context.

**Math concepts:** discount factors, the warrant type hierarchy, population transfer factors, context distance metrics, hierarchical decomposition, evidence combination rules.

**Audience needs:** Architects need intuition for why some kinds of evidence (mechanism studies) transfer better than others (theoretical claims). Panel members need to understand the epistemic reasoning behind discount values (e.g., why CONSTITUTIVE = 0.95, THEORY_DERIVED = 0.25). Developers need the algorithm for assigning warrants and applying discounts in the message-passing system.

### 3. **Coherence Metrics: Negative, Positive, and Overall** (§131–§132)

ATLAS computes three types of coherence: negative coherence (measuring the degree of mutual support among beliefs), positive coherence (penalizing logical contradictions), and overall coherence (a weighted combination). These metrics guide belief revision and assess system consistency.

**Math concepts:** graph theory (cycles, connectedness), weighting schemes, recursive definitions, normalization factors, stability analysis, comparison with other coherence formalisms (BonJour, Lehrer, Shogenji, etc.).

**Audience needs:** Architects need intuition for what "coherence" means operationally (how does the system decide when a new finding is coherent vs. contradictory?). Panel members and philosophers need to understand how ATLAS's coherence metric relates to classical coherence theories in epistemology. Developers need the algorithm for computing coherence in real time and the proofs that the metric is well-defined.

### 4. **Entrenchment Scoring: Quinean Centrality in the Web** (§133)

ATLAS assigns each belief an entrenchment score reflecting how central it is to the web of belief. Central beliefs are more resistant to revision (they require more evidence to change) because changing them would require revising many downstream beliefs. Peripheral beliefs can be updated easily.

**Math concepts:** graph centrality measures (degree, closeness, betweenness), weighted centrality, recursive dependency, normalization.

**Audience needs:** Architects need to understand that some beliefs in the system are foundational (e.g., "daylight affects human physiology") and thus resistant to change, while others are specific claims (e.g., "optimal daylight intensity is 300–500 lux") and easily updated. Panel members need to engage with the Quinean epistemological framework and see how it is formalized. Developers need the algorithm.

### 5. **Factor Analysis for Molecule Discovery** (§174)

The system applies factor analysis to find latent theoretical molecules—primitive concepts that explain correlations among surface-level findings. When many studies show that daylighting, views of nature, and circadian rhythm improvements all co-occur, factor analysis can reveal whether they share a common mechanism (e.g., "entrainment to the light-dark cycle") or whether they are independent effects.

**Math concepts:** covariance matrices, eigendecomposition, factor loadings, rotation methods (Varimax, Promax), communalities, scree plots, assumptions and diagnostic tests.

**Audience needs:** Architects need intuition for what a "molecule" is and why the system discovers them (simplifying the theory, finding deeper unifying concepts). Panel members need to understand the statistical assumptions and limitations of factor analysis. Developers need the implementation details, including handling of missing data and model selection criteria.

### 6. **Endogenous Value Function V(G): Gap Prioritization** (§176.4)

The system identifies unanswered research questions (gaps) and computes a value score V(G) for each gap, indicating how much answering it would improve the overall system. Gaps with higher V(G) are prioritized for future research.

**Math concepts:** decision theory, expected value of information (EVOI), sensitivity analysis, utility functions, Monte Carlo estimation.

**Audience needs:** Architects need to understand why ATLAS prioritizes certain research questions (those that would resolve high-uncertainty, high-impact questions). Panel members need to see the decision-theoretic reasoning. Developers need the computation algorithm and its assumptions.

### 7. **Staleness Scoring S(card): Card Freshness Computation** (§173.4)

Evidence that was true ten years ago might be outdated. ATLAS scores the staleness of each piece of evidence, applying a discount to credences based on how long the evidence has been in the system without replication or update.

**Math concepts:** exponential decay functions, half-life concepts, recency weighting, time-series analysis.

**Audience needs:** Architects need intuition for why the system depreciates old evidence (science progresses, methods improve). Panel members need to see the decay parameters and justify them. Developers need the algorithm and the parameters.

### 8. **Polarity Scoring in ArgumentationGraph: Debate Structure** (§177.2)

When domain experts disagree, ATLAS represents the disagreement as an argumentation graph where nodes are claims and edges are attack/support relationships. Polarity scores quantify how strongly each node is supported or attacked.

**Math concepts:** directed graphs with polarized edges, propagation algorithms, semantics of argumentation (abstract argumentation, Dung's framework), winning extensions.

**Audience needs:** Architects need intuition for how expert disagreements affect credences (disputed claims are less entrenched, more easily updated). Panel members need to understand the argumentation semantics and how disagreements are represented. Developers need the implementation.

### 9. **Bayesian Belief Network Calibration** (from calibration service)

Posterior distributions from the BBN are only as accurate as the CPT parameters feeding them. ATLAS includes a calibration service that compares predicted probabilities to observed frequencies in empirical data (POE datasets, replication studies, etc.), adjusting parameters to improve fit.

**Math concepts:** maximum likelihood estimation, expectation-maximization (EM) algorithm, Bayesian optimization, calibration curves, Brier score, log loss, conformal prediction intervals.

**Audience needs:** Architects need intuition for what "calibration" means (predictions should be reliable: if the system says 70% likelihood, the event should occur about 70% of the time). Panel members need to understand the statistical methods and their assumptions. Developers need the full implementation.

### 10. **Confidence Interval Computation** (from credence_intervals.py)

When the system makes a prediction (e.g., "credence in mood improvement is 0.74"), it also computes a confidence interval around that credence, reflecting the uncertainty from sparse evidence, measurement error, and population heterogeneity.

**Math concepts:** bootstrap resampling, Bayesian credible intervals, the delta method, Bayesian uncertainty quantification, propagation of uncertainty through dependent calculations.

**Audience needs:** Architects need to know that a credence of 0.74 with a 95% CI of [0.60, 0.88] is very uncertain and should not be treated as a point estimate. Panel members need to see how uncertainty is quantified. Developers need the algorithm.

---

## §179.4: How the Science Writer Agent Produces Intuition Layers

ATLAS includes a specialized service—the **Science Writer Agent**—that generates Intuition-layer explanations (Layer 1) for any mathematical operation in the system. This agent is not a generic language model; it is trained on a corpus of science writing and implements explicit rules for producing accessible mathematics explanations.

### Design Principles for the Science Writer Agent

The agent follows these principles when generating Intuition layers:

**1. Lead with the question.** Begin with what problem the math solves, not the math itself. "When do we believe one piece of evidence over another?" is more compelling than "Bayes' rule updates credences."

**2. Use one concrete analogy.** Abstract mathematics is hard to visualize. A single well-chosen analogy (judge weighing testimony, engineer tuning a system, gardener balancing nutrients) makes the concept graspable. Multiple analogies confuse; no analogy leaves the reader stranded.

**3. Avoid jargon.** Use "belief" instead of "credence" (unless credence is the term that appears in formal contexts, in which case introduce it once and stick with it). Use "certainty" instead of "posterior probability."

**4. Acknowledge uncertainty.** Rather than claiming the math is perfectly accurate, say: "This principle assumes independent evidence; if evidence is correlated, the rule needs adjustment."

**5. Explain why the reader should care.** End the Intuition layer with a sentence connecting the concept to real outcomes: "This principle ensures that the system does not over-commit to early findings; it stays open to new evidence if the evidence is surprising enough."

**6. Prepare for the equation.** The Intuition layer should prime the reader for the Transparent layer by introducing variable names conceptually. "The formula will compare how likely you are to see this evidence *if the hypothesis is true* (we call this the likelihood) versus how likely you are to see this evidence regardless (we call this the normalizer)." Then, in the Transparent layer, the equation P(E|H) / P(E) is not a surprise; it is the formalization of a concept already introduced.

### Implementation

The Science Writer Agent is a specialized Claude instance with:

1. **A detailed system prompt** (3,000+ tokens) encoding the principles above, with examples of good and bad Intuition layers for mathematics concepts from cognitive science, statistics, and information theory.

2. **A corpus of exemplar outputs** covering 20+ core ATLAS math concepts, from which the agent learns patterns and adapts to new concepts.

3. **A critique loop:** Generated explanations are routed to a panel review process (2–3 domain experts plus 1 science communication expert) which flags:
   - Jargon that should be simplified
   - Analogies that might mislead
   - Claims that overstate certainty
   - Missing connections to real outcomes

4. **Automated metrics:**
   - Readability score (Flesch-Kincaid grade level, target ≤ 10)
   - Analogy relevance (does the analogy actually illuminate the concept, or confuse?)
   - Certainty language (percentage of sentences qualified with "typically," "often," "in most cases," flagging overconfident claims)

The Science Writer Agent output is *not* inserted directly into documentation. Instead, it is a draft that undergoes human review before being committed to the Math Card library. This preserves quality while scaling the production of accessible explanations.

---

## §179.5: Design Decision — Progressive Mathematical Disclosure versus Separate Technical Documentation

When designing ATLAS's approach to explaining mathematics, two architectural choices were considered.

### Option A: Progressive Mathematical Disclosure (Chosen)

All mathematical explanations live in a single hierarchical structure: a Math Card with three layers (Intuition → Transparent → Details). A user reads the layer appropriate to their sophistication and can optionally descend to deeper layers if they want more rigor. The card is a single document, not three separate documents.

**Advantages:**
- Single URL, single reference point. When an architect asks "where is the explanation of credence updates?" the answer is one card, not three separate documents.
- Progressive knowledge building. A user starting at Intuition encounters concepts in a carefully scaffolded order, designed to prepare them for the Transparent layer if they descend.
- Consistency of notation and terminology. All three layers use the same variable names, making it easy to map between intuitive and formal understanding.
- Reduced cognitive load. A user does not have to switch between documents; they scroll down a single card.

**Disadvantages:**
- Long documents. A single card with all three layers might be 8–15 pages, requiring significant scrolling or printing.
- Mixed audience. Reading layer 1 with full knowledge that layers 2–3 are below might feel patronizing to some readers ("I don't need this baby-talk explanation"), while lacking those layers entirely is frustrating to others.

### Option B: Separate Technical Documentation (Not Chosen)

Mathematics explanations are split into three separate documents, with different URLs and different maintenance cycles. The Intuition explanation is a separate document from the Transparent explanation, which is separate from the Details specification.

**Advantages:**
- Modularity. Each audience gets exactly what they need without extraneous material. Architects read Intuition docs. Researchers read Transparent docs. Developers read Details docs.
- Focused length. Each document is optimized for its audience; no document is overly long.
- Independent versioning. The Intuition explanation can be updated for clarity without touching the Details specification.

**Disadvantages:**
- Discovery burden. Users must know to look for three separate documents. The architect does not realize that a Transparent layer exists.
- Inconsistency risk. The three documents can diverge in notation, terminology, or even substance if maintenance is not coordinated.
- Broken reference chains. If the Intuition doc says "see the formula for details," but the formula is in a separate document at a different URL, readers encounter friction.
- Overhead of cross-references. Each layer must repeatedly explain why it is relevant and point to other layers.

### Decision: Progressive Disclosure (Option A) for Primary Cards, with Aggregated Separation for Reference

The chosen design uses **progressive disclosure on single Math Cards** (Option A) as the primary mechanism, with one exception: **developers working on implementation can request a separate Technical Reference compilation** (which aggregates all Details layers from relevant cards) without needing to navigate through Intuition and Transparent layers.

**Rationale:**

1. **User discovery matters.** Most users (architects, clinicians, students) benefit from knowing all three layers exist; they do not know in advance whether they will need the Details layer. A single hierarchical card supports exploratory reading. A user starting at Intuition and finding the math clear can skip the rest; a user hitting a barrier in Intuition can descend for clarification. Separate documents force a choice in advance that users cannot make without exploring.

2. **Consistency is epistemic.** If the Intuition layer says "we update credences using Bayes' rule" but the Details layer specifies a modified Bayesian update with discount factors, the inconsistency is not just confusing—it is epistemically problematic. Users have been misled about what the system actually does. Progressive disclosure, with all three layers integrated, prevents this.

3. **Notation integration prevents confusion.** When the Intuition layer introduces a concept ("we compare two probabilities") and the Transparent layer presents the formula (P(E|H) / P(E)), the reader sees immediately that the intuition and the formula are describing the same thing. Separate documents require the reader to remember the intuitive explanation while reading the formula, leading to dissonance.

4. **Developer needs are met separately.** Developers who need to implement a system do not want to read intuitive analogies; they want formal specification and pseudocode. The solution is to provide an optional **Technical Reference compilation** that collects all Details layers relevant to a subsystem (e.g., "Details layers for the message-passing system," "Details layers for credence updates") into a single document, without the Intuition and Transparent scaffolding. This is generated automatically from the Math Card library and can be regenerated whenever the Details layers change.

This design respects both the principle of progressive disclosure for general users and the principle of efficiency for specialized users (developers) who have the domain knowledge to skip scaffolding.

---

## §179.6: Quality Assurance for Math Cards

Every Math Card in the system undergoes a multi-stage review process before publication.

### Stage 1: Coherence Check (Internal)

The card author (and/or the Science Writer Agent) generates all three layers. An automated coherence check verifies:

- Do all three layers use consistent notation and terminology?
- Does the Intuition layer introduce concepts that are formalized in the Transparent layer?
- Does the Transparent layer reference equations that appear in the Details layer?
- Are variable names consistent across layers?

### Stage 2: Clarity Review (Science Communication Expert)

A specialist in science communication (typically with background in one of: physics communication, medical writing, technical writing for non-specialist audiences) reviews the Intuition and Transparent layers. They assess:

- Is the Intuition layer comprehensible to an intelligent non-specialist? (Tested via readability metrics and spot-checking with non-technical readers.)
- Does the analogy illuminate or confuse?
- Are there jargon terms that could be replaced with plain language?
- Does the explanation skip steps that a non-specialist would need to follow the logic?

### Stage 3: Accuracy Review (Domain Expert)

A domain expert in the relevant mathematics (a mathematician, statistician, or theoretical computer scientist) reviews all three layers, particularly the Details layer. They assess:

- Is the mathematics correct? (Proofs verified, standard derivations applied correctly.)
- Are edge cases and assumptions clearly stated?
- Is the connection to the literature accurate and complete?
- Are there alternative approaches that should be acknowledged?

### Stage 4: Practitioner Feedback (Domain Panel)

Domain panel members (architects, environmental designers, health care professionals, etc.) read the Intuition and Transparent layers. They assess:

- Does the explanation answer the questions practitioners actually have?
- Does the explanation align with how practitioners currently understand the concept?
- Are there missing practical details (e.g., how to use this in a design decision)?

### Stage 5: Integration Check

The card is checked against other cards in the system. Do concepts introduced in Card 3 depend on Card 5? Are cross-references correct? Are there redundancies that could be consolidated?

### Publication Criteria

A Math Card is published only when:
- All three layers pass coherence, clarity, and accuracy checks.
- Readability score of Intuition layer ≤ 10 (Flesch-Kincaid).
- At least one domain practitioner has reviewed and approved the Intuition layer.
- The Details layer has been approved by a domain expert mathematician.
- Cross-references to other cards are complete and correct.

---

## §179.7: The Math Card Library

The Math Card library is a navigable collection of all mathematical operations in ATLAS, organized by concept area. As of 2026-03-04, the following cards are either published or in progress:

| Card ID | Topic | Status | Published |
|---------|-------|--------|-----------|
| MC-129 | Typed Credence Propagation | In Progress (Details layer) | 2026-03 (Target) |
| MC-129.1 | Warrant Discount Functions | In Progress (Transparent layer) | 2026-03 (Target) |
| MC-131 | Negative Coherence Metrics | In Progress (Intuition layer) | 2026-04 (Target) |
| MC-132 | Positive & Overall Coherence | Pending (Design phase) | 2026-04 (Target) |
| MC-133 | Entrenchment: Quinean Centrality | In Progress (All layers) | 2026-03 (Target) |
| MC-174 | Factor Analysis: Molecule Discovery | Pending (Design phase) | 2026-05 (Target) |
| MC-176.4 | Endogenous Value Function V(G) | In Progress (Transparent layer) | 2026-04 (Target) |
| MC-173.4 | Staleness Scoring S(card) | Pending (Design phase) | 2026-05 (Target) |
| MC-177.2 | Polarity Scoring in ArgumentationGraph | Pending (Design phase) | 2026-05 (Target) |
| MC-BBN | BBN Calibration | In Progress (All layers) | 2026-03 (Target) |
| MC-CI | Confidence Interval Computation | In Progress (Transparent layer) | 2026-04 (Target) |

Cards are published to a web-accessible Math Card portal (currently hosted at `/Article_Eater_PostQuinean_v1/docs/math_cards/`). Each card has a unique URL, a version number, and an import date in the system documentation. When a card is updated, the previous version is archived (not deleted) and the new version becomes canonical.

---

## §179.8: Integration with QA and Documentation Systems

The Math Card library is not a standalone collection; it integrates with other ATLAS systems that need to explain mathematics to users.

### Integration with QA Answers

When the QA system generates an answer to a question that involves mathematical reasoning—"Why does ATLAS give this belief a credence of 0.74 rather than higher?"—the system checks whether a relevant Math Card exists. If so, the answer includes a link to the card with a brief pointer: "For a detailed explanation of how credences are updated, see Math Card MC-129."

In some cases, the QA system can embed a excerpt from the Intuition layer of a relevant card, providing the answer without requiring the user to click away.

### Integration with Panel Documentation

When domain panel members review a template or make a decision about warrant types, they can consult relevant Math Cards to understand the formal basis for their decisions. For example, a panel member deciding whether a finding should be assigned MECHANISM or EMPIRICAL_ASSOCIATION warrant can read the definitions in MC-129.1 and see how the two warrant types differ in transfer reliability.

### Integration with Technical Documentation

Developers implementing ATLAS subsystems can generate a focused Technical Reference by specifying which concepts they need (e.g., "message-passing system"). The system automatically compiles all Details layers for those cards into a single document, removing Intuition and Transparent layers to avoid clutter.

### Integration with Narrative Answers and Analogies

The Science Writer Agent and narrative generation system have access to the Intuition layers of all cards. When generating a narrative explanation for a user, the system can incorporate relevant analogies and intuitive explanations, drawing from the Math Card library.

---

## References

Fowler, M. (2005). Event sourcing. *martinfowler.com*. Retrieved from https://martinfowler.com/eaaDev/EventSourcing.html

Gawande, A. (2007). *Better: A surgeon's notes on performance*. Metropolitan Books.

Jaynes, E. T. (2003). *Probability theory: The logic of science*. Cambridge University Press.

Kaplan, R., & Kaplan, S. (1989). *The experience of nature: A psychological perspective*. Cambridge University Press.

Lehrer, K., & Wagner, C. (1981). Rational consensus in science and society. *The Journal of Philosophy*, 78(6), 312–326. https://doi.org/10.2307/2025649

Pinker, S. (2014). *The sense of style: The thinking person's guide to writing in the 21st century*. Penguin Press.

Sagan, C. (1995). *The demon-haunted world: Science as a candle in the dark*. Random House.

Shogenji, T. (1999). Is coherence truth-conducive? *Analysis*, 59(4), 338–345. https://doi.org/10.1093/analys/59.4.338

Williams, J. M. (2010). *Style: Toward clarity and grace*. University of Chicago Press.

---

*This section documents the Math Card system architecture as of Sprint XXVI-A (2026-03-04). Card production is ongoing; see `docs/MATH_CARD_PRODUCTION_SCHEDULE.md` for current status. Quality assurance protocols are defined in `docs/MATH_CARD_QA_PROTOCOL.md`. Integration with the Science Writer Agent is documented in `Article_Eater_PostQuinean_v1/services/science_writer_service/SKILL.md`.*
