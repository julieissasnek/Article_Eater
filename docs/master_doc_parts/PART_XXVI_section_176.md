# §176. The Interpretation Space: Four Epistemic Zones, Question Taxonomy, and Gap Discovery

**Date**: 2026-03-04
**Part**: PART XXVI (The System's Self-Model)
**Status**: Foundational specification for epistemic adequacy

---

## §176.1: The System's Self-Model of Knowledge

A knowledge system, if it is to improve its own epistemic standing, must first answer a prior question: what does it actually know, and how does it know it? This is not a rhetorical gesture toward self-awareness but a practical requirement. The ATLAS system maintains thousands of beliefs about the built environment, human perception, and design principles. These beliefs have different epistemic credentials. Some rest on multiple randomized trials with consistent findings. Others stand on single studies, or on theoretical derivation with sparse empirical grounding. Still others are explicit gaps — questions the system recognizes it cannot answer. And beyond these, there lie the unknowns that the system does not yet even recognize as questions.

The Interpretation Space is ATLAS's formal representation of this epistemic landscape. It is not a static classification scheme where beliefs are sorted into bins labeled "certain," "probable," and "uncertain." Rather, it is a dynamic model of what the system knows and doesn't know, organized into zones of epistemic proximity and probed by systematic question-type operators that reveal weaknesses in understanding, warrant grounding, mechanistic explanation, and actionable guidance.

The epistemological motivation is Quinean: the web of belief does not face the tribunal of experience one proposition at a time. Instead, it meets experience as a corporate body. A belief's epistemic standing is partly local—determined by its own warrant chain and argumentation defense—but partly holistic, determined by how it integrates with the rest of the web. When the system holds that "daylight exposure reduces cortisol" and separately holds that "cortisol elevates during stress," and further holds that "reduced cortisol correlates with lower stress-related illness," the coherence of these three claims reinforces each of them. Conversely, if the system holds one belief that directly contradicts another, or if it holds a belief with unresolved gaps in the mechanistic chain connecting cause to effect, the coherence of the web is compromised. The Interpretation Space extends Quine's intuition to an operational level: it identifies precisely where the web is coherent and robust, where tensions exist that demand resolution, where knowledge is well-formed but incomplete, and where the system confronts genuine unknowns it cannot yet articulate.

This self-model serves a critical function. The standard approach to knowledge management in deployed systems is demand-driven: observe what users ask about, notice where the system gives weak answers, and prioritize acquisition accordingly. This works when the users happen to ask about the system's weaknesses. But it samples the periphery of knowledge according to the arbitrary distribution of human interests, not according to the intrinsic structure of the knowledge base itself. A user might never ask about olfactory cues in the built environment, but the Interpretation Space can recognize—through its own systematic self-interrogation—that the system has a blind spot in multi-sensory biophilia, a gap whose resolution would reshape multiple belief clusters and improve the coherence of the whole web.

---

## §176.2: The Four Epistemic Zones

The Interpretation Space partitions ATLAS's epistemic territory into four zones, ordered by epistemic security and distance from the core of well-established knowledge.

**Zone 1: The Known Interior.** This is the region of credences ≥ 0.7, supported by strong warrants (CONSTITUTIVE or MECHANISM warrants with discount factors d ≥ 0.80), and defended against argumentation attacks of severity > 0.3. These are beliefs that have achieved epistemic stability in the Quinean sense: revising them would require substantial reorganization of the surrounding web. When the QA system draws on beliefs from Zone 1, it provides confident, well-sourced answers that can explain not merely what is true but why, how much, for whom, and what evidence would change the conclusion.

Consider the belief: "Natural daylight exposure in office environments improves self-reported alertness." This claim is supported by multiple randomized trials (RCTs) with consistent findings across different populations and measurement contexts. There exists a mechanistic account linking environmental light to circadian rhythm entrainment, specifically via melanopsin-expressing retinal ganglion cells projecting to the suprachiasmatic nucleus, which entrains the endogenous cortisol rhythm and thereby influences perceived alertness. The evidence spans neural, physiological, and behavioral levels. Critical questions about the strength of the effect have been addressed with quantitative effect sizes. Known boundary conditions—the effect is strongest for people with dysregulated circadian rhythms, weakest for those working entirely indoors under artificial lighting—are documented. No serious unresolved critiques have been raised that remain undisputed. This belief earns a credence of 0.85, warrant type MECHANISM, and occupies the known interior.

**Zone 2: The Active Boundary.** Here lie beliefs with moderate credence (0.4–0.7), or claims whose warrant chains contain gaps, or propositions subject to active argumentation disputes. The system can answer questions about these beliefs with meaningful caveats. This is the frontier where scientific activity is most productive. The claims are well-formed enough to test, but uncertain enough that new evidence would make a genuine difference to what the system believes.

Consider the claim: "A fractal dimension of approximately 1.3–1.5 in architectural façades is preferred across human cultures." This is supported by several studies (Hagerhall et al. 2004, Taylor et al. 2005, Spehar et al. 2003) demonstrating fractal-preference relationships in visual art and architecture. But the cross-cultural scope of this claim is underexplored: most studies have drawn from Western, industrialized populations. An unresolved boundary critique exists: "Does this preference hold for populations raised in highly rectilinear, modernist environments where fractal patterns have not been salient in childhood exposure?" The belief earns a credence of 0.62, warrant type EMPIRICAL_ASSOCIATION with a discount factor of 0.65 due to the limited boundary testing. Follow-up questions the system generates about this belief are substantive, not merely mechanical: they point to genuine uncertainties about scope and generalizability.

**Zone 3: The Identified Periphery.** Beyond the boundary lies a region of explicit, well-formed gaps. These are questions the system recognizes it cannot answer, classified by gap type (MECHANISM, VALIDATION, BOUNDARY, DIRECTION, INTERACTION, MEDIATION) and linked to the beliefs they would affect if resolved. Zone 3 gaps are not absences; they are demands that the system can articulate precisely.

An example: "What is the dose-response curve for biophilic elements in windowless workspaces? Is there a minimum vegetation coverage ratio below which the effect disappears?" The system knows that visible vegetation reduces stress-related outcomes (a Zone 1 or 2 belief, depending on evidence strength). But it lacks quantitative boundary specifications for vegetation coverage. This gap is identified by the gap-prediction system because multiple template-based rules reference vegetation exposure without specifying dosage. The gap is tractable because related environmental-dose studies exist in the literature; an answer might be found through targeted literature search. And the gap is consequential: resolving it would allow the system to translate general principles into specific design guidance (e.g., "a 40% vegetation coverage is sufficient; beyond 60%, diminishing returns emerge").

**Zone 4: The Uncharted Exterior.** Beyond the periphery lies genuinely uncharted territory—regions signaled by QA failures and conceptual blind spots. These are queries that cannot be classified, questions that fall through all handlers to the arbitrary fallback, follow-up chains that terminate in "I do not know" without the system being able to articulate what kind of knowledge is missing. The system does not know what it does not know.

Consider a user's query: "How does the olfactory character of a building affect occupants' trust in its proprietors?" The system has no beliefs about olfaction, no templates for olfactory-social-trust mediation, no theories that predict such interactions. It cannot even formulate the gap precisely because it lacks vocabulary: "olfactory-trust-mediation-in-commercial-buildings" is not a concept in its current ontology. Moving from Zone 4 to Zone 3 requires conceptual expansion—adding new question-type operators, new theory frameworks, or new vocabulary—before evidence search can begin.

The four-zone model matters because it tells the system where attention should be invested. Zone 1 beliefs require maintenance: defending their warrant chains, documenting boundary conditions as new evidence emerges. Zone 2 beliefs demand investigation: targeted research to resolve warrant gaps or boundary uncertainties. Zone 3 gaps are the system's research agenda—questions formulated but not yet answered. Zone 4 signals need for conceptual work: expanding the vocabulary and theoretical frameworks that allow the system to recognize and formulate questions it cannot yet pose.

---

## §176.3: The Question-Type Taxonomy as Epistemic Operators

The QA system's question taxonomy is typically understood as a classification scheme: given a user query, identify its type (MECHANISM, VALIDATION, BOUNDARY, etc.) and route it to the appropriate handler. But in the context of the Interpretation Space, the question types function differently. They are not merely categories; they are epistemic operators—functions that, when applied to a belief, generate specific kinds of follow-up questions and reveal specific kinds of incompleteness.

Consider a belief B in the Epistemic Network: "High ceilings promote feelings of freedom and open-mindedness." The system holds this belief, perhaps with credence 0.58, supported by a handful of studies in environmental psychology. Now apply the question-type operators:

The MECHANISM operator generates: "How does high ceiling height causally produce feelings of freedom? What is the causal chain? Are there neurological correlates? Attentional mechanisms? Aesthetic processing?" Applying the operator reveals that the system cannot articulate the mechanism beyond vague appeals to "openness" as a metaphor. The mechanism is immature.

The VALIDATION operator generates: "How strong is the evidence base for this effect? How many independent studies? With what effect sizes? What are the confidence intervals? Are there replications or meta-analyses?" Applying the operator reveals that the system has perhaps three independent studies with modest effect sizes (d ≈ 0.40) and no meta-analytic synthesis. The validation gap is moderate.

The BOUNDARY operator generates: "When does high ceiling promote freedom? In all contexts or only some? Does the effect hold in religious spaces (where high ceilings may evoke awe rather than freedom)? In industrial buildings? In small rooms where high ceilings create disproportionality?" Applying the operator reveals that the system has tested the effect in office and classroom settings but not in the extremes.

The EFFECT_SIZE operator generates: "By how much does ceiling height increase feelings of freedom, measured on what scale, with what precision?" Applying the operator reveals quantitative specificity: a typical study might show a 0.4 standard deviation increase in self-reported feelings of freedom for every 1-meter increase in ceiling height (up to some threshold), but the system lacks studies that map the full dose-response curve.

The DESIGN_GUIDANCE operator generates: "Given this belief, what should a designer do? If I am designing a workspace where open-mindedness is important, what ceiling height should I target?" Applying the operator reveals that the system can sketch a preliminary answer—"aim for ceilings above 3 meters"—but the guidance is qualitative, lacks confidence intervals, and does not account for interactions with other variables (room size, task type, occupant personality).

The FRONTIER operator generates: "What do we not understand about this belief? What questions would a researcher ask next?" Applying the operator reveals several open questions: the mechanism, the boundary conditions, the interaction with room size, the cultural variation (do non-Western populations show the same preference?), the durational effects (is the feeling sustained or does adaptation occur?).

All ten such operators—MECHANISM, VALIDATION, BOUNDARY, DIRECTION, COMPARISON, SURPRISE, CROSS_DOMAIN, EFFECT_SIZE, DESIGN_GUIDANCE, FRONTIER—can be systematically applied to any belief. A belief for which all operators produce high-quality answers occupies Zone 1. One for which some operators produce weak answers sits on the boundary between Zones 1 and 2. One for which most operators produce weak but articulate answers lies in Zone 2. One for which the operators reveal well-formed gaps occupies the threshold to Zone 3. And if the operators themselves fail to produce coherent questions, the belief approaches Zone 4.

This operationalization has a crucial property: it is uniform and exhaustive. Rather than waiting for users to probe the system's knowledge in arbitrary ways, the interpretation space probes every belief along every epistemic dimension. The result is a complete map of the system's strengths and weaknesses, not a sample biased by the distribution of user queries.

---

## §176.4: Endogenous Value and the Coherence-Driven Landscape

The Interpretation Space computes the epistemic value of resolving a gap not from external user demand but from the internal structure of the web of belief itself. This is a fundamental shift in how knowledge acquisition is prioritized.

The standard, demand-driven approach works as follows: observe user queries, identify questions the system struggles with, collect evidence to answer those questions, and reintegrate the evidence. This is useful. It ensures the system responds to human information needs. But it has a deep limitation: it samples the frontier of knowledge according to the distribution of user interests, which is orthogonal to the structure of the knowledge base.

The endogenous approach, by contrast, values knowledge by asking: "If this gap were resolved, how would the web of belief change? Would it become more coherent? Would tensions be resolved? Would mechanisms be completed? Would boundary conditions be established?" The value of a gap is computed from the degree to which resolving it would improve the epistemic integrity of the system as a whole.

Formally, the endogenous value of resolving a gap G is:

**V(G) = Structural_Impact(G) × Tractability(G) × Coherence_Tension(G)**

**Structural Impact(G)** measures how many beliefs would change credence if G were resolved, and by how much. This is computed via counterfactual coherence analysis: the system hypothetically resolves the gap (e.g., assumes the answer is true), recomputes the credences of downstream beliefs via Bayesian update, and measures the magnitude of shift. A gap with high structural impact would, if resolved, reshape multiple belief clusters. For instance, resolving the gap "What is the complete mechanism by which natural light influences circadian rhythm?" would strengthen credences in a dozen related beliefs about light, physiology, alertness, and sleep quality.

**Tractability(G)** estimates the difficulty of resolving the gap, inferred from the warrant structure of surrounding beliefs and the type of gap:

- A MECHANISM gap between two mechanistically warranted beliefs has *high* tractability: the surrounding structure constrains the answer, and literature searches can find the missing link.
- A BOUNDARY gap for an empirically warranted belief has *moderate* tractability: boundary questions are empirical, but studies may not exist specifically targeting the boundary.
- A MECHANISM gap in a region dominated by analogical warrants has *low* tractability: the surrounding structure provides little constraint, and the answer may require novel theorizing or experimental work.
- Any gap in Zone 4 (uncharted, not yet well-formed) has *very low* tractability: the question cannot be answered until the conceptual vocabulary is expanded.

**Coherence_Tension(G)** measures whether the gap sits at a point of active stress in the web. If the gap is located near unresolved argumentation attacks, or near beliefs that push in different directions, or near contradictions in the empirical evidence, then resolving the gap would settle a dispute and stabilize the web. High tension means the gap is consequential not just structurally but emotionally—its resolution would bring harmony to a discordant region. Low tension means the gap is an absence rather than a contradiction; filling it would add knowledge but would not resolve ongoing disputes.

Together, these three factors identify gaps of genuine epistemic value. A gap with high structural impact, high tractability, and high coherence tension would, if resolved, improve multiple belief clusters via a resolution path that research could realistically follow. Such gaps move to the front of the research queue.

This value function reveals something that demand-driven systems routinely miss: what we might call *silent gaps*. A silent gap is a region of incompleteness that is invisible to users because they don't think to ask about it. Suppose the system has rich knowledge about how daylight affects alertness, mood, and sleep quality. But it has no account of how olfactory cues interact with these effects—how the smell of an office (fresh air, plants, or conversely, stale air) modulates the benefits of daylight exposure. No user has asked about this interaction. The demand-driven system never probes it. But the endogenous approach, applying the CROSS_DOMAIN operator to daylight-related beliefs, asks: "Do these effects connect to other sensory modalities?" And if the answer reveals that olfactory-visual interactions are not characterized, the gap predictor can compute the value of resolving that gap. It may be high: understanding multi-sensory biophilia could reshape the system's entire model of environmental perception.

---

## §176.5: Probatory Rule Sets and Epistemic Closure

The Interpretation Space is not merely an overlay on the web of belief; it is an extension of the web itself. To formalize this extension, we require a notion of *probatory rules*—rules that govern the relationships between beliefs, not in the sense of logical entailment (which is Hintikka's or AGM's concern) but in the sense of warrant adequacy, mechanism specification, argumentation integrity, and interpretive completeness.

Four rule sets define these probatory relationships:

**Rule Set R₁: Argumentation Rules.** Based on Walton's schemes for defeasible inference (expert opinion, sign, cause-to-effect, analogy, correlation-to-cause), these rules govern whether arguments supporting beliefs are closed against critical questions. An argument from expert opinion is *open* when constructed; it closes only when all critical questions—Is the source credible? Is the claim in the expert's domain? Do peers agree? Is the evidence consistent?—are answered with traceable evidence. An argument from cause-to-effect opens with a causal claim and closes only when a credible mechanism, evidence for the causal antecedent, and evidence for exclusion of alternative causes are all documented.

**Rule Set R₂: Warrant Rules.** These establish sufficiency conditions for each warrant type. An EMPIRICAL_ASSOCIATION warrant requires at least one replication or meta-analysis, quantified effect sizes with confidence intervals, a mechanism at the how-possibly level, at least one tested boundary condition, and cumulative sample size ≥ 100 or ≥ 3 independent studies. A MECHANISM warrant requires a mechanistic chain with ≥ 2 steps, each step with independent evidence, quantitative consistency with observed effect sizes, and acknowledgment of competing mechanisms. A THEORY_DERIVED warrant requires explicit statement of which theory, which premises, which auxiliary assumptions, plus at least one direct empirical test.

**Rule Set R₃: Mechanism Rules.** These govern the specification of causal mechanisms according to a maturity ladder: how-possibly (plausible mechanism, consistent with known science, no fatal objections), how-plausibly (mechanism with ≥ 2 steps, each with independent evidence, quantitatively consistent), and how-actually (mechanism tested via intervention, mediators measured, alternatives ruled out). Additionally, R₃ requires that causal mechanisms be linked to T1 theoretical frameworks and, where applicable, to rasa attractor molecules.

**Rule Set R₄: Interpretation Rules.** These are the most distinctive. Based on the ten question-type operators, R₄ rules specify when a belief has been adequately *interpreted*—not merely believed but explained, quantified, contextualized, and situated within a landscape of known unknowns. A belief closes under the MECHANISM operator when the QA system can produce an answer with groundedness ≥ 0.7 and the mechanism chain contains ≥ 2 evidence-backed steps. A belief closes under the EFFECT_SIZE operator when quantitative effect sizes are reported with units and confidence intervals. A belief closes under the FRONTIER operator when the system can articulate ≥ 1 open question that is not already tracked in the VOI system.

Now the key definition: the system is *closed under rule set Rᵢ* when, for every belief in the epistemic network to which Rᵢ applies, either the rule is satisfied or the unmet condition is explicitly tracked as a gap. A gap is thus not a deficiency but a *formalized demand*—a statement of what further knowledge would be needed to satisfy the rule.

Different purposes require different closures. An architect selecting materials for a retrofit needs closure under R₂ (is there evidence?) and R₄-EFFECT_SIZE and R₄-DESIGN_GUIDANCE (what should I do?). A researcher writing a grant proposal needs closure under R₃ (where are the mechanistic gaps?) and R₄-FRONTIER (what are the open questions?). A critical literature reviewer needs high closure under R₁, R₂, and R₃. The system, when receiving a query, can check: "What purpose does this query serve? Which rule sets define adequacy for that purpose? Are the relevant beliefs closed under those rules? If not, the gaps become either caveats in the answer or suggestions for further investigation."

This gives us a formal definition of epistemic adequacy: the system is adequate for purpose P when it achieves closure (≥80% of relevant rule conditions satisfied) under the rule sets that P demands. Full closure under all four rule sets simultaneously is an ideal limit, not a realistic goal. What matters is purposeful, partial closure—knowing which rules matter for which questions, and being transparent about which rules remain unsatisfied.

---

## §176.6: Design Decision: A Separate Epistemic Layer

A natural question arises: why formalize the Interpretation Space as a separate computational layer rather than embed gap detection and value computation directly within the QA pipeline?

The answer lies in a distinction between two different epistemic tasks that are often conflated. The QA pipeline's task is to *answer questions*: given a query from a user or a downstream system, retrieve relevant beliefs, compute their coherence, and generate an answer. The Interpretation Space's task is to *ask questions*: given the current state of the epistemic network, identify gaps, classify them, compute their value, and prioritize them for resolution.

These are different problems with different optimization criteria. The QA pipeline is optimized for *responsiveness*: when asked, answer quickly and accurately. The Interpretation Space is optimized for *comprehensiveness*: systematically probe all beliefs along all epistemic dimensions to generate a complete map of strengths and weaknesses.

If gap detection were embedded in the QA pipeline, the system would only probe gaps when users happened to ask questions that triggered gap-generating operators. The coverage would be incomplete and biased toward user interests. A separate layer allows the system to apply all operators to all beliefs, exhaustively and uniformly, independent of what users happen to ask.

Furthermore, separating the two layers creates clarity about epistemic standards. The QA system's criterion for success is: "Did I answer the user's question truthfully and well?" The Interpretation Space's criterion is different: "Did I identify all significant gaps, classify them correctly, and rank them by epistemic value?" These are complementary but distinct standards. By formalizing them separately, we avoid the confusion of mixing demand-driven (QA) with supply-driven (endogenous) value.

A third virtue of separation is modularity. The Interpretation Space can be updated, refined, and evolved independently of the QA system. New question-type operators can be added; rule sets can be revised; the value function can be recalibrated. The QA system continues to function; the Interpretation Space's role is to feed high-value gaps into the research queue, which in turn feeds the evidence-integration pipeline, which updates the Epistemic Network, which improves the QA system's answers.

The Interpretation Space thus represents a recognition of an elementary truth about knowledge systems: not all knowledge work is reactive (answering questions). Some of the most important knowledge work is proactive: asking questions that should be answered, prioritizing investigation by the intrinsic structure of the knowledge base, and systematically seeking out gaps before users stumble upon them. This proactive dimension requires its own formal machinery. The Interpretation Space is that machinery.

---

## References

Alchourrón, C. E., Gärdenfels, P., & Makinson, D. (1985). On the logic of theory change: Partial meet contraction and revision functions. *The Journal of Symbolic Logic*, 50(2), 510–530.

Bechtel, W., & Abrahamsen, A. (2005). Explanation: A mechanistic alternative. *Studies in History and Philosophy of Science Part C: Studies in History and Philosophy of Biological and Biomedical Sciences*, 36(2), 421–441.

Craver, C. F. (2007). *Explaining the brain: Mechanisms and the mosaic unity of neuroscience*. Oxford University Press.

Dung, P. M. (1995). On the acceptability of arguments and its fundamental role in nonmonotonic reasoning, logic programming and n-person games. *Artificial Intelligence*, 77(2), 321–357.

Hintikka, J. (1962). *Knowledge and belief: An introduction to the logic of the two notions*. Cornell University Press.

Howard, R. A. (1966). Information value theory. *IEEE Transactions on Systems Science and Cybernetics*, SSC-2(1), 22–26.

Pollock, J. L. (1995). *Cognitive carpentry: A blueprint for how to build a person*. MIT Press.

Quine, W. V., & Ullian, J. S. (1970, 1978). *The web of belief*. Random House (1970); 2nd edition (1978).

Toulmin, S. (1958). *The uses of argument*. Cambridge University Press.

van Fraassen, B. C. (1980). *The scientific image*. Oxford University Press.

Walton, D. N. (1996). *Argumentation schemes for presumptive reasoning*. Lawrence Erlbaum Associates.
