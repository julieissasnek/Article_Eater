# Expert Panel Discussion: "Why Warrant Types Matter" by David Kirsh

## Panel Members

1. **Nancy Cartwright** — Philosophy of Science, Durham University / UC San Diego
2. **Judea Pearl** — Computer Science / Causal Inference, UCLA
3. **Armen Der Kiureghian** — Structural Engineering / Uncertainty Quantification, UC Berkeley
4. **Sarah Moss** — Epistemology / Formal Epistemology, University of Michigan
5. **Paul Thagard** — Cognitive Science / Philosophy of Science, University of Waterloo
6. **Andrea Saltelli** — Statistics / Global Sensitivity Analysis, Open University of Catalonia
7. **James Woodward** — Philosophy / Causal Semantics, University of Pittsburgh
8. **Craig Fox** — Psychology / Decision Science, UCLA

---

## ROUND 1: OPENING REACTIONS

### Nancy Cartwright

Kirsh has done something important here, though I'm not sure he fully realizes the philosophical depth of what he's proposing. The warrant-typing framework maps naturally onto the distinction I've spent two decades defending: the difference between universal capacities and their local manifestations. When Kirsh distinguishes MECHANISM warrants (universally applicable biological pathways) from EMPIRICAL_COVARIANCE warrants (context-dependent correlations), he's essentially capturing my argument about causal capacities. A system possesses a capacity universally, but whether that capacity manifests depends entirely on local circumstances.

What strikes me most is that Kirsh recognizes something that still troubles much of science: we collapse distinctly different epistemic situations into a single number. A 0.60 confidence from a fully mapped mechanistic pathway really IS different from a 0.60 confidence from a correlation that might be confounded by a dozen unmeasured variables. I've always insisted that good science requires tracking what evidence supports a claim, not just how confident we should be in the claim. Warrant-typing operationalizes this insight.

However, I have reservations about the seven-type hierarchy. The distinction between CAPACITY and MECHANISM seems to me less fundamental than it appears in this paper. In my framework, CAPACITY warrants are simply MECHANISM warrants where we understand the capacity but doubt its manifestation under field conditions. This isn't a distinct epistemic category; it's a partially characterized mechanism. Similarly, CONSTITUTIVE warrants occupy an odd position — they're not really evidence for causal claims at all, just definitional clarity about what we're measuring. I would have preferred five types, with CONSTITUTIVE excluded as a category error and CAPACITY collapsed into a uncertainty-of-manifestation parameter attached to MECHANISM warrants.

The connection to interventionism is solid, and I appreciate that Kirsh engages seriously with Woodward's framework. But I want to push back on one point: does warrant-typing really capture the difference between a causal capacity and its manifestation? It seems to encode information about what we know about the mechanism, not about the local conditions that might activate or suppress it. A MECHANISM warrant tells me the capacity exists and how it works, but knowing the mechanism does not automatically tell me whether the capacity will manifest in a particular context. That still requires field investigation.

Finally, the ATLAS implementation is impressive — 1,000 articles, 130 nodes, 400 edges is real work. But how stable are the warrant-type assignments? Are different experts assigning the same warrant type to the same paper? This matters enormously for the reliability of the framework.

---

### Judea Pearl

I find warrant-typing conceptually appealing, but I'm troubled by its lack of formal rigor. In my work on structural causal models (SCMs) and causal hierarchies, I've learned that informal taxonomies of evidence collapse under scrutiny. The do-calculus provides a formal framework for distinguishing different kinds of causal knowledge: observational equivalence classes, identifiability conditions, and the identification of causal effects. Warrant types feel like a pre-formal attempt to capture distinctions that should ultimately reduce to these mathematical structures.

Here's my central concern: what does a MECHANISM warrant actually correspond to in the SCM formalism? If Kirsh means that we have identified the functional form of the causal mechanism (the edge weights in the DAG and the exogenous noise terms), then a MECHANISM warrant is equivalent to having identified a causal effect from X to Y through intermediate nodes — which is precisely what the SCM framework formalizes through the do-operator and path-specific effects. An EMPIRICAL_COVARIANCE warrant would correspond to observational knowledge without identified causal effects. An ANALOGICAL warrant would be a guess about edge weights based on structural similarity to another model.

If this interpretation is correct, warrant-typing is valuable as a conceptual framework but should be axiomatized formally. Without formalization, how do we know the seven types are exhaustive? How do we know they're truly distinct and not overlapping categories? The distinction between FUNCTIONAL and MECHANISM warrants troubles me especially: both claim that a variable plays a certain role, but one knows the mechanism and one doesn't. But "knowing the mechanism" is vague. Do we need to know only the first-order causal links, or all the way down to physics? The SCM framework forces you to specify exactly what you mean by "mechanism" and what level of abstraction you're working at.

Moreover, Kirsh's treatment of confounding is informal. He says EMPIRICAL_COVARIANCE warrants are "confound-vulnerable" while MECHANISM warrants are "confound-resistant." But confounding in the SCM framework is a precise concept: it's the existence of unobserved common causes (backdoor paths). The confound-resistance of a MECHANISM warrant, as I understand it, means that we've blocked all backdoor paths by understanding the mechanism. But this isn't automatic — mechanisms can have unobserved components too. For instance, the mechanism "light → retinal cells → serotonin" could be confounded by an unobserved factor that affects both light exposure and serotonin through a different pathway (e.g., circadian effects on serotonin independent of light). So confound-resistance is not a property of the warrant type alone; it depends on whether the mechanism has been exhaustively characterized.

That said, Kirsh is pointing at something real. In my experience, mechanistically-grounded causal inferences are more robust to confounding precisely because scientists who know the mechanism tend to measure more comprehensive mediator variables and are alert to potential backdoor paths. So there's a practical wisdom in the observation that MECHANISM warrants are more robust. But this is a statistical property of how scientists conduct research, not a logical property of mechanisms themselves.

If Kirsh developed a formal theory that mapped warrant types onto SCM identifiability conditions, this would be much stronger. What probability distributions can be recovered from observational data given a claim that rests on a MECHANISM warrant? What causal effects can be identified? These are the right questions, and the answers would give warrant-typing genuine theoretical grounding.

The value-of-information analysis (Section 4.1) is promising, though. Different warrant types do prescribe different research strategies, and this is exactly what VOI analysis should capture. But again, this would be stronger if formalized using decision theory and SCM identifiability conditions.

---

### Armen Der Kiureghian

As someone who has spent decades working on uncertainty quantification in structural engineering, I can tell you that the distinction between aleatory (irreducible) and epistemic (reducible) uncertainty is fundamental to my field. Kirsh's framework builds nicely on this distinction, but it doesn't replace our existing toolkit — it complements it. I see warrant-typing as a step beyond the aleatory-epistemic dichotomy, offering a finer-grained classification of epistemic uncertainty.

However, I have practical concerns about implementation. In structural engineering, we use Monte Carlo simulation, polynomial chaos methods, and other advanced uncertainty quantification techniques. These methods are designed to propagate uncertainty through computational models. How do warrant types integrate with this existing infrastructure? Does a MECHANISM warrant change how we specify probability distributions? Does an EMPIRICAL_COVARIANCE warrant require different sampling strategies than a MECHANISM warrant?

Kirsh hints at this in Section 4.4 on calibration and trust, mentioning "discount factors" that vary by warrant type (0.8-0.95 for MECHANISM, 0.4-0.7 for EMPIRICAL_COVARIANCE, 0.2-0.5 for ANALOGICAL). These sound reasonable, but on what basis are they chosen? Are these empirically validated? If I'm using a MECHANISM warrant claim from architectural neuroscience to inform my building design decisions, should I really apply only a 0.2 discount factor when translating from laboratory to field conditions? My experience in structural engineering suggests that field validation is essential regardless of warrant type. The laboratory environment differs from real-world conditions in ways that no warrant-type taxonomy can fully capture — temperature fluctuations, material degradation, soil variability, aging effects.

The real value of warrant-typing in engineering would be in research allocation. If I have two competing claims at equal probability but with different warrant types, warrant-typing would tell me which one deserves more investment in field validation. A MECHANISM warrant suggests that field validation should focus on whether the mechanism activates under real conditions and whether there are field-specific factors that suppress the mechanism. An EMPIRICAL_COVARIANCE warrant suggests that field validation should focus on whether the correlation actually exists in the field and what confounders might be at play. This is useful guidance for experimental design.

But I worry about one thing: the paper treats confounding as if warrant type is sufficient to characterize confounding vulnerability. In structural engineering, confounding is often not the main threat to validity — variability and parameter uncertainty are. A MECHANISM warrant claim like "steel with higher carbon content is stronger" is mechanistically sound, but field strength is confounded by dozens of variables (temperature, workmanship, environmental exposure, time since fabrication). The mechanism is understood, but prediction remains difficult because of unobserved variability in the causal system. Warrant types don't directly address this problem.

That said, the ATLAS system sounds promising. If it's generating real insights about which kinds of evidence are more stable across time and research groups, that's exactly the kind of empirical validation we need. The claim that "mechanistic claims are more stable than correlational claims" is testable and important. Have you tested this systematically? Can you control for other factors like publication bias, research group diversity, and sample size? This would be a significant contribution.

One final point: the paper would benefit from explicit treatment of uncertainty in the mechanism itself. Not all mechanistic knowledge is equally detailed. Some mechanisms are traced to the molecular level; others to the physiological system level; others to the behavioral level. A MECHANISM warrant at different levels of mechanistic detail should perhaps carry different priors and different confidence in field transfer. This is implicitly in the paper but should be made explicit.

---

### Sarah Moss

Warrant-typing offers a fresh perspective on a problem I've been working on extensively: how do we represent and update knowledge in conditions of both aleatoric and epistemic uncertainty? My recent work on interleaving — the way agents can hold different attitudes toward different aspects of a single claim — suggests that Kirsh's framework captures something important that existing probabilistic epistemology misses.

Here's what I find compelling: in my formal epistemology framework, I've argued that beliefs can be rationally inconsistent across different dimensions without violating the norms of epistemic rationality. For instance, an agent might assign high credence (0.8) to "daylight affects serotonin" while assigning low credence (0.3) to "this specific window in my office affects my serotonin." The same underlying causal claim receives different credence levels because the contexts differ. Warrant-typing explains why: the high-credence version likely rests on MECHANISM warrants (which transfer across contexts), while the low-credence version would require EMPIRICAL_COVARIANCE warrants (which don't transfer predictably).

But I have a fundamental worry about the framework as currently presented. Warrant types seem to function as a shorthand for a much richer body of information about evidence structure. When Kirsh says a MECHANISM warrant is "confound-resistant," he's not just saying something about the logical form of mechanistic evidence — he's assuming a particular model of how mechanisms work, what kinds of confounding are possible, and what background knowledge is available. This model needs to be made explicit.

Specifically, I'm concerned about the relationship between warrant types and what I call "epistemic status" — the agent's judgment about how well-articulated the evidence for a claim is. Consider two MECHANISM warrants: one for "neurotransmitter X increases in response to stimulus Y" (extensively validated across species and experimental conditions), and one for "architectural feature Z improves occupant wellness through mechanism M" (newly proposed, mechanism partially characterized). Both have the same warrant type, but the epistemic status is radically different. The first mechanism is well-established; the second is speculative. Yet Kirsh assigns both the same prior (0.60).

This suggests that warrant type alone is insufficient. We need to combine warrant type with something like a "mechanism maturity score" — a judgment about how thoroughly the mechanism has been validated across different conditions and populations. A MECHANISM warrant for a 50-year-old biological pathway should carry a higher prior than a MECHANISM warrant for a novel architectural hypothesis.

The framework also underspecifies how warrant types interact with agent learning. I've argued that rational belief updating is not simply Bayesian in conditions of deep uncertainty — agents must also update their models of how evidence relates to claims. Warrant-typing provides a structure for such model updating: as new evidence accumulates, we might change our judgment not about the probability of a claim but about its warrant type. A claim might move from ANALOGICAL to CAPACITY to MECHANISM status as evidence accumulates. How does this process work formally? The paper doesn't address this.

One more thing: the paper claims that warrant types provide a "middle path" between coherentism and foundationalism (Section 5.3), but I'm not convinced this is right. The warrant-type hierarchy (CONSTITUTIVE > MECHANISM > EMPIRICAL_COVARIANCE > FUNCTIONAL > CAPACITY > ANALOGICAL > THEORETICAL_DEFAULT) looks like a foundationalist ordering, not a coherentist alternative. In my view, what would make warrant-typing truly coherentist is if it explicitly modeled how warrant-type assignments shift when we update our entire belief system in response to anomalies. Does a single counterexample to a mechanistic claim demote it to EMPIRICAL_COVARIANCE status, or do we revise the mechanism and keep the claim at MECHANISM status? The paper doesn't specify.

Still, I think Kirsh is onto something important about how knowledge operates under uncertainty. The framework deserves development and formalization.

---

### Paul Thagard

Kirsh's paper is a natural extension of my own work on computational philosophy of science, and I want to support it enthusiastically. The ATLAS system represents exactly the kind of computational knowledge representation that I've been advocating for since the 1980s. Making scientific claims and their evidential warrants explicit in a knowledge graph allows us to ask empirical questions about how evidence works in science — questions we couldn't ask when everything was collapsed into probabilities.

However, I have a concern about where warrant-typing fits into the broader picture of how scientific reasoning actually works. My theory of explanatory coherence (ECHO) argues that scientists evaluate theories not just based on how well individual claims fit the evidence, but based on how well the entire theoretical system hangs together — how well all the pieces cohere. A claim that is poorly supported by direct evidence can still have high credibility if it coheres beautifully with the rest of the system. Conversely, a claim with strong direct evidence can be rejected if it creates incoherence with the broader theory.

How does warrant-typing interact with coherence? The paper mentions coherentism briefly (Section 5.3) but doesn't develop the connection. Here's what concerns me: a MECHANISM warrant tells us something about direct evidential support, but it doesn't tell us anything about how well the claim coheres with other claims in the system. Consider two mechanistic claims: one that fits beautifully with established theory and one that requires radical revision of background beliefs. Both are mechanistic; both should carry the same weight in warrant-typing. But in actual scientific reasoning, the second claim requires much more evidence than the first because of coherence considerations.

I would argue that warrant-typing needs to be supplemented with a coherence analysis. When we annotate a claim with a MECHANISM warrant, we should also annotate it with a coherence score: how well does this claim fit with the rest of what we believe? A mechanistic claim that creates massive incoherence in the system deserves to be treated differently than a mechanistic claim that fits smoothly into the theoretical architecture.

That said, Kirsh's framework points in the right direction. The value-of-information analysis (Section 4.1) is especially promising. In ECHO and related work, I've argued that research allocation should be guided by the information value of different experiments — not just their cost, but how much they would reduce uncertainty about central theoretical claims. Warrant-typing provides a systematic way to think about this. Different warrant types prescribe different research directions, and this is exactly what a rational research strategy should do.

I'm also impressed by the ATLAS implementation. The empirical observation that "mechanistic claims are more stable across time and research groups than claims supported by correlation" is exactly the kind of insight that emerges from systematic computational analysis of scientific literature. This could be used to test theories of scientific change. If coherence is as important as I think, then we might expect that highly coherent claims (which would need to be mechanistic to maintain coherence) are more stable than incoherent claims, even if they're both mechanistic. This is a testable prediction.

One final point: warrant-typing could be profitably combined with my work on conceptual change. When scientists discover that a mechanism they thought was constitutive is actually contingent, or that a functional analogy is mechanistically grounded, they're not just updating probabilities — they're changing the structure of their conceptual systems. Warrant-typing provides a framework for representing such changes explicitly. A shift from ANALOGICAL to MECHANISM warrant represents a fundamental conceptual reorganization. Making this explicit would enrich our understanding of scientific progress.

---

### Andrea Saltelli

I approach this paper from the perspective of global sensitivity analysis and uncertainty quantification in complex computational models, and I have two serious concerns about the warrant-typing framework.

First, the paper lacks empirical grounding. Kirsh assigns priors to each warrant type (CONSTITUTIVE: 0.75, MECHANISM: 0.60, EMPIRICAL_COVARIANCE: 0.60, FUNCTIONAL: 0.50, CAPACITY: 0.45, ANALOGICAL: 0.35, THEORETICAL_DEFAULT: <0.50) without any justification. Where do these numbers come from? Are they empirically derived from analysis of the ATLAS system? Are they intuitive judgments? If ATLAS contains 130 nodes and 400 edges, have you actually computed the frequency distribution of outcomes for claims at each warrant type? What fraction of MECHANISM warrants hold up over time? What fraction collapse to EMPIRICAL_COVARIANCE status?

In my field, we're very careful about assigning prior probabilities to uncertain parameters. We use expert elicitation, historical data, and sensitivity analysis to understand the impact of prior assumptions. The priors in warrant-typing strike me as guesses. And because these priors are used in Section 4.4 to derive "discount factors" for field application, they matter enormously. A 0.8 discount factor for MECHANISM warrants versus a 0.4 discount factor for EMPIRICAL_COVARIANCE warrants is a massive difference in how a model will perform. This needs empirical justification.

Second, and related: the paper doesn't engage with the problem of model structural uncertainty. In my work with Tarantola and others, we've documented that the biggest source of uncertainty in complex environmental and engineering models isn't parameter uncertainty — it's model structure uncertainty. Warrant-typing helps with epistemic uncertainty about parameter values, but it doesn't address uncertainty about the functional form of relationships between variables, the completeness of the causal model, or the relevance of included variables.

Consider the example: "daylight exposure increases serotonin production." A MECHANISM warrant says we understand the pathway (light → retinal cells → raphe nuclei → serotonin synthesis). But does the mechanism we've identified exhaust the relevant causal pathways? What if serotonin is also affected by circadian rhythm, which is affected by light but through a different pathway? What if thermal effects of windows affect occupant behavior in ways that confound the light effect? Warrant-typing tells us we have a mechanism, but it doesn't tell us whether we have the complete mechanism or just one mechanism among many.

In sensitivity analysis, we call this the "input uncertainty" versus "factor uncertainty" distinction. We might know the probability distribution for a parameter (input uncertainty), but we might be uncertain whether we've included all the relevant parameters (factor uncertainty). The second is almost always more important and harder to quantify. Warrant-typing addresses the first problem (making input uncertainty explicit) but not the second.

That said, I can see value in the framework for organizing existing knowledge. The observation that mechanistic claims are more stable in literature than correlational claims is important if true. But the paper should back this up with systematic analysis of the ATLAS corpus. Present the frequency distributions, the survival curves, the stability metrics. Otherwise, this is an unsubstantiated claim, however plausible it sounds.

And here's a question for future work: could warrant-typing be combined with global sensitivity analysis? Imagine that different warrant types correspond to different uncertainty structures that we could explore using variance-based sensitivity analysis. A MECHANISM warrant might produce a different sensitivity signature than an EMPIRICAL_COVARIANCE warrant — mechanistic parameters might be less influential on model output (because the mechanism is well-understood) while correlational parameters might be more influential (because their effects are context-dependent). This could provide an empirical way to validate the warrant-type framework.

---

### James Woodward

Kirsh engages seriously with my interventionist framework and I appreciate the attempt to ground warrant-typing in formal causal semantics. However, I have concerns about whether the mapping from warrant types to interventionist evidence is as tight as the paper suggests.

In my work, I've argued that a causal claim "X causes Y" is true if and only if there exists an intervention on X that would change Y, where an intervention is a manipulation that breaks the normal causal pathways to X and replaces them with the experimental manipulation (Pearl's back-door criterion captures this idea, though Pearl and I would disagree on some details). The strength of evidence for a causal claim depends on how much information we have about what would happen under intervention.

Kirsh's framework maps warrant types to intervention-supporting evidence: CONSTITUTIVE warrants tell you what variable to intervene on; MECHANISM warrants tell you what the effect would be; EMPIRICAL_COVARIANCE warrants suggest the effect might exist; ANALOGICAL warrants are speculations; THEORETICAL_DEFAULT warrants are untested hypotheses. This mapping is largely correct, but there are ambiguities that need clarification.

Consider a MECHANISM warrant. Kirsh says it "provides strong support for interventionist causal claims because understanding the mechanism tells you precisely what would change if you altered the cause." But understanding the mechanism in the laboratory does not automatically tell you what would happen if you intervened in the field. The mechanism might be suppressed, modified, or blocked by field-specific factors. So a MECHANISM warrant provides strong support for a causal claim in the laboratory context but requires field validation for a causal claim in a new context.

This suggests that warrant types should be indexed to contexts, not treated as context-independent properties. A claim might be MECHANISM-warranted in the laboratory but only EMPIRICAL_COVARIANCE-warranted in the field (if the field correlation is replicated but the mechanism hasn't been validated in field conditions). The paper's treatment of context-generalization is useful but underspecified. We need a more explicit account of how warrant types change as we move from one context to another.

Also, I want to emphasize something that Kirsh mentions but doesn't fully develop: the intervention-supporting property of a warrant type depends on what we already know about causal systems. MECHANISM warrants support intervention claims partly because biological mechanisms are conserved across contexts (as Cartwright emphasizes), but this is an empirical fact about the world, not a logical fact about mechanisms. In other domains — say, social science or climate modeling — mechanisms might not be well-conserved across contexts, and a MECHANISM warrant would provide weaker intervention support.

Here's a concrete example: suppose we have a mechanistic account of how a leadership intervention affects team productivity (mechanism involves increases in team trust, which increases coordination, which improves productivity). This mechanism is well-characterized in the laboratory. But if we deploy this intervention in a company where trust is already high due to strong organizational culture, the mechanism might not activate (ceiling effect). A MECHANISM warrant here is weaker than it would be in a domain where mechanisms are robustly transferable.

I also want to flag an issue about the difference between mechanisms and interventionist causal claims. Knowing the mechanism is useful for causal claims, but a mechanism per se is not identical to a causal claim. The mechanism tells you how the cause operates; the causal claim says that intervening on the cause would change the effect. These are related but not identical. A system might have a beautiful mechanism (light → serotonin synthesis) that doesn't produce measurable effects on behavior because of competing influences downstream. So MECHANISM warrants support causal claims, but the support is probabilistic, not certain.

Finally, I want to raise a question about the temporal structure of mechanisms. Some causal mechanisms operate on short timescales (retinal response to light, which happens in milliseconds), while others operate on long timescales (serotonin effects on mood, which might take weeks). Should warrant types be indexed to timescale? A MECHANISM warrant for an immediate effect might be much stronger than a MECHANISM warrant for a long-delayed effect where confounding factors might accumulate.

Despite these reservations, I think Kirsh is making a genuine contribution. Warrant-typing offers a way to make mechanistic evidence explicit and to ground causal reasoning in the structure of what we know about mechanisms. This is valuable work.

---

### Craig Fox

I come to this paper from the perspective of behavioral decision science and judgment under uncertainty, and I have both appreciative and critical things to say.

First, the appreciative part: Kirsh correctly identifies a real problem in how decision-makers (including scientists) use probabilistic information. My research with Ülkümen and others has shown that people do naturally distinguish different sources of uncertainty when prompted to do so, and they make systematically different decisions based on what kind of uncertainty they face. When people know that uncertainty is epistemic (reducible through research), they search for information differently than when uncertainty is aleatory (irreducible). Warrant-typing extends this insight into a more sophisticated taxonomy of epistemic uncertainty, and that's genuinely useful for understanding how people ought to reason.

The idea that warrant types should prescribe different research strategies is exactly right. If I'm facing a MECHANISM warrant at 0.60 confidence, my research strategy should focus on validating whether the mechanism activates under field conditions. If I'm facing an EMPIRICAL_COVARIANCE warrant at 0.60 confidence, my research strategy should focus on controlling for confounders. Warrant-typing provides a conceptual framework for the kind of rational information search that my work says people aspire to, even if they often fall short.

However, I have a major concern: the paper is not grounded in psychological reality, yet it makes claims about human reasoning as if it is. Section 6.4 addresses this directly. Kirsh argues that warrant-typing is prescriptive, not descriptive — a normative standard that humans violate but should aspire to. I agree with this claim in principle. But the paper would be much stronger if it included cognitive science evidence about how people actually distinguish among warrant types.

Here's what we know from my research: people distinguish risk from uncertainty reasonably well, especially when explicitly prompted. People do NOT reliably distinguish different sources of epistemic uncertainty in naturalistic settings. When presented with two equally-probable claims, one supported by a mechanism they understand and one supported by a correlation they don't understand, most people cannot articulate the difference in what should happen next. They might sense that one feels more reliable than the other, but they cannot specify why or what research strategy would be appropriate.

This has important implications for the practical use of warrant-typing. If the framework is meant to inform computational systems (like ATLAS) that support human decision-making, then we need to know how to communicate warrant types to users effectively. Displaying "MECHANISM warrant: 0.60" will not by itself change how people reason. We need to communicate not just the warrant type but what it means — what would change the probability, what research strategy is appropriate, how the claim will likely generalize.

Moreover, I'm concerned about overconfidence biases related to warrant types. There's a danger that a MECHANISM warrant could trigger a "mere knowledge" effect, where people treat mechanistic evidence as more reliable than it actually is, especially when the mechanism is complex and they don't fully understand it. "Well, it's based on a mechanism, so it must be reliable." This is exactly backwards from the paper's main claim — mechanistic evidence IS more reliable in some ways, but this needs to be communicated carefully to avoid overconfidence.

I'd also like to flag an issue about warrant-type instability. People's judgments about whether a claim rests on a mechanism are influenced by cognitive and motivational factors. If someone is motivated to believe a claim, they're more likely to interpret available evidence as mechanistic. If they're motivated to disbelieve a claim, they'll emphasize correlational or analogical aspects. The framework might inadvertently crystallize such motivated reasoning. We need research on how to elicit reliable warrant-type judgments from experts, how to resolve disagreements among experts about warrant types, and how to train people to assign warrant types without motivated bias.

Finally, I want to note that the prior probabilities assigned to each warrant type (Section 3) seem arbitrary from a behavioral perspective. Where does 0.60 for MECHANISM come from? From my research on probability estimation, these base rates should be calibrated to the actual outcomes of claims at each warrant type. If mechanistic claims in a given domain actually succeed 60% of the time, then 0.60 is reasonable. But if they succeed 80% of the time (because scientists who know the mechanism tend to be more careful), then the prior should be higher. Again, this is an empirical question that needs data.

That said, I see genuine value in the framework. The question of how to represent and communicate uncertainty is crucial for applied decision-making, and warrant-typing offers a structure that's more nuanced than raw probabilities. With proper attention to the psychology of reasoning and risk communication, this could be a useful tool.

---

## ROUND 2: FOCUSED CRITIQUES

### Nancy Cartwright — Focused Critique

My core concern is that warrant-typing doesn't fully capture the problem it claims to solve. Kirsh argues that bare probabilities are "informationally impoverished" because they don't tell you what kind of evidence supports a claim. This is true. But warrant-typing, as presented, doesn't fully solve this problem because it doesn't specify what contextual conditions are required for the warrant to operate.

Consider the MECHANISM warrant for "daylight exposure increases serotonin production." The paper says this warrant is "relatively invulnerable to confounding" and "generalizable wherever biology does." But this is only true if certain contextual conditions obtain. The mechanism will operate if: (1) the retinal cells are functional, (2) the raphe nuclei are functional, (3) the person isn't taking an SSRI that artificially elevates serotonin, (4) the person is in a circadian state where serotonin production is possible, and dozens of other conditions. The mechanism is universal, but its manifestation is context-dependent.

This is the heart of my capacities-based framework: causal claims should be unpacked into capacity claims ("the system HAS the capacity to respond") plus manifestation conditions ("but the capacity will be manifested only if..."). Kirsh's warrant types encode information about capacity claims but not about manifestation conditions. A MECHANISM warrant says "the capacity exists and we understand how," but it doesn't specify when the capacity will be manifested.

The practical consequence is that the "discount factors" Kirsh mentions in Section 4.4 are insufficient for field application. He suggests that a MECHANISM warrant warrants a 0.8-0.95 discount factor when moving from laboratory to field conditions. But the actual discount needed depends entirely on the manifestation conditions. If the field context lacks one critical manifestation condition, the discount should be near zero (the mechanism won't activate at all). If the field context supplies all manifestation conditions, no discount is needed.

This suggests that warrant-typing should be extended to include a "manifestation-condition analysis" for each claim. A fully specified claim would be: "Warrant type: MECHANISM, Prior: 0.60, Manifestation conditions: [list of conditions required for capacity to activate], Likelihood that field context satisfies manifestation conditions: [estimate]." Without this additional structure, warrant-typing provides limited guidance for field application.

I want to emphasize that this is a refinement, not a fundamental objection. Kirsh's framework is on the right track. But the execution needs to be more rigorous about the distinction between capacity and manifestation.

---

### Judea Pearl — Focused Critique

The lack of formal axiomatization is the deepest problem with this work. Let me be concrete about what I mean.

In the structural causal model framework, causal effects can be formalized precisely. Given a DAG representing causal structure, the causal effect of X on Y is defined as: E[Y | do(X=x)] - E[Y | do(X=x')], where do() represents an intervention. Identifiability conditions determine whether this effect can be recovered from observational data. The frontdoor criterion, backdoor criterion, and other tools allow us to determine what causal effects are identifiable given what knowledge.

Now, how should warrant types map onto identifiability conditions? My hypothesis:

- **CONSTITUTIVE warrant**: tells you that a variable is measurable without confounding (X = the exact quantity you care about). This corresponds to being able to identify P(X) without bias.

- **MECHANISM warrant**: tells you that the full causal effect X → Y and all mediating pathways are characterized. This corresponds to identifying all path-specific effects and having all confounders measured. Formally, all backdoor paths are blocked, and all mediating paths are identified.

- **EMPIRICAL_COVARIANCE warrant**: tells you that X and Y are observed to be correlated, but causal direction and confounding are unresolved. This corresponds to having only observational data without causal model structure — P(X,Y) is known but P(Y|do(X)) is not identifiable.

- **CAPACITY warrant**: tells you the mechanism exists in principle but hasn't been validated in the field. This corresponds to having the correct SCM structure in theory but not having validated parameters through field data.

- **ANALOGICAL warrant**: tells you that the SCM structure is suspected based on analogy to another domain. This corresponds to hypothesizing an SCM structure based on similarity to a known causal system.

If these mappings are correct, warrant-typing could be formalized as a classification of SCM identifiability status. The value would be enormous: you could prove theorems about which warrant types can be promoted to which other types under what additional assumptions.

For instance: "A claim with EMPIRICAL_COVARIANCE warrant can be promoted to MECHANISM warrant if and only if (a) an additional variable is measured that blocks all backdoor paths, or (b) an experimental intervention is performed." This would be a formal theorem with precise conditions. The paper hints at this but doesn't develop it.

Here's what the paper should include: a formal appendix with definitions of each warrant type in terms of SCM identifiability conditions, theorems about when warrant-type promotion is possible, proofs about the vulnerability of each warrant type to confounding (formalizing the intuition that MECHANISM warrants are confound-resistant), and analysis of how warrant types relate to causal effect identification. Without this, the framework remains conceptually useful but scientifically shallow.

I also want to flag a specific technical problem. The paper treats confounding as if it's a property of warrant types, but confounding is actually a property of the causal system AND the variable set. Two claims might have identical MECHANISM warrants but different confounding vulnerabilities if one has unmeasured confounders in the field and the other doesn't. Warrant types don't resolve confounding; they characterize what we know about the mechanism. The actual confounding vulnerability depends on what variables have been measured in a particular context.

---

### Armen Der Kiureghian — Focused Critique

My critique concerns the practical integration of warrant-typing with existing uncertainty quantification (UQ) infrastructure and the lack of empirical validation of the framework's utility.

First, on integration: Kirsh proposes that warrant types should prescribe different discount factors (0.8-0.95 for MECHANISM, 0.4-0.7 for EMPIRICAL_COVARIANCE, etc.) when translating laboratory findings to field application. But how do these discount factors integrate with existing UQ methods? In structural engineering, we use:

- **Probability boxes (p-boxes)** to represent uncertain probability distributions
- **Evidence theory** to represent uncertain probability mass assignments
- **Imprecise probability** to represent ambiguity about distribution families
- **Dempster-Shafer theory** to combine evidence from multiple sources

If a MECHANISM warrant claim has 0.8-0.95 discount factor, does that mean we should use a p-box with an 80-95% confidence bound around the laboratory estimate? Does it mean we should apply a multiplicative uncertainty factor to the sensitivity parameter? The paper doesn't specify.

Second, the priors assigned to warrant types (0.75 for CONSTITUTIVE, 0.60 for MECHANISM, etc.) are suspiciously round numbers. In my field, we derive such priors from historical data and expert calibration. Have you actually analyzed the ATLAS corpus to derive these empirically? What fraction of claims initially assigned a MECHANISM warrant actually survive field validation? This is a crucial number for setting the prior, and the paper provides no evidence.

Third, I'm skeptical of the stability claims. Section 5.4 mentions that "mechanistic claims are more stable across time and research groups than claims supported by correlation." This is presented as a fact emerging from ATLAS analysis, but no evidence is provided. How did you define "stability"? Is it survival in the literature (papers continue to cite the claim)? Success in replication studies? In structural engineering, we've learned that paper survivability doesn't equal empirical validity — claims can become "established" through self-citation loops and institutional inertia. What metric of success did you actually use?

Furthermore, if you're claiming that mechanistic claims are more stable, you need to control for confounding factors: Do mechanistic claims get more funding and therefore more replication attempts? Are mechanistic papers published in higher-prestige journals? Do they get cited more, creating visibility bias? The causal claim about mechanism-stability requires a more careful analysis.

Finally, on practical utility: the paper claims warrant-typing enables better research allocation (Section 4.1). This would be genuinely valuable. But it's not demonstrated. Take a concrete example: you have $1 million to spend improving certainty about building occupant wellness claims. Warrant-typing predicts that you should allocate more resources to validating MECHANISM warrants in the field and more resources to confound-control for EMPIRICAL_COVARIANCE warrants. Does this prediction match empirical success? Would a team that allocates research according to warrant-typing actually achieve better results than a team using intuitive strategies?

What I would want to see: a prospective study where research allocation decisions are made using warrant-typing, compared to a control group using standard approaches. Measure which team produces more stable, field-validated knowledge. This would provide real validation of the framework's utility.

---

### Sarah Moss — Focused Critique

My concern is that warrant-typing doesn't adequately capture what I call "epistemic status differentiation" — the distinction between claims that are epistemically well-positioned (extensively validated, part of established theory) and claims that are epistemically fragile (newly proposed, speculative, creating theoretical tension).

Two claims might have the same warrant type but radically different epistemic status. Compare:
- Claim A: "Light stimulates retinal ganglion cells (MECHANISM warrant)" — validated thousands of times across species and contexts, completely integrated into neurobiology
- Claim B: "Fractal patterns in facades improve visual satisfaction through visual system sensitivity to fractals (MECHANISM warrant)" — newly proposed mechanism, validated in one laboratory study, creates tension with existing theories about visual aesthetics

Both are MECHANISM warrants, but Claim A deserves much higher credence than Claim B. Yet the framework assigns them the same prior (0.60).

The problem is that warrant type captures information about the KIND of evidence, but not the AMOUNT or STRENGTH of that evidence. A mechanism supported by 100 studies is epistemically different from a mechanism supported by one study, even though both are MECHANISM warrants.

I would propose that warrant-typing needs to be supplemented with an "evidence strength" dimension. For each warrant type, specify: how many independent studies support it? What's the magnitude of the effect? How consistent is the effect across different populations and conditions? How long has the mechanism been validated? Do experts converge on it or disagree?

This information could be encoded as a confidence interval around the warrant-type prior. Instead of saying "MECHANISM warrant: 0.60," say "MECHANISM warrant: 0.60 (95% CI: 0.55-0.72, based on 47 studies with consistent effect sizes)." This would ground the framework in actual empirical data and make the priors transparent.

There's also a problem with how warrant types interact with theoretical integration. In my formal epistemology, I've argued that rational belief updating requires agents to balance three considerations: (1) fit with evidence (which warrant types capture), (2) coherence with existing beliefs (which warrant types don't capture), and (3) simplicity and informativeness of the theoretical system as a whole (which warrant types don't capture).

Warrant-typing handles the first consideration well. But a claim might have strong warrant but poor fit with the rest of what we believe, or a claim might have weak warrant but excellent fit with theory. A complete framework would balance these.

For instance: "Biophilic design reduces cortisol" might have a THEORETICAL_DEFAULT warrant (based on Wilson's theory) but excellent coherence with evolutionary psychology and neurobiology. This combination (weak warrant, strong coherence) justifies a moderate credence level — higher than the warrant type alone would suggest. Conversely, "Negative ions improve mood" might have a MECHANISM warrant at the cellular level but creates friction with existing neurobiology and is often cited with skepticism by experts. This combination (moderate warrant, poor coherence) justifies a more cautious credence than the warrant type alone would suggest.

A fully developed framework would make these coherence considerations explicit.

---

### Paul Thagard — Focused Critique

My main criticism is that warrant-typing neglects the role of explanatory coherence in how scientists actually evaluate evidence. In my work on ECHO and conceptual change, I've argued that scientists don't evaluate theories by assigning probabilities to individual claims; they evaluate them by judging how well the entire theoretical system hangs together.

Here's a concrete concern: a claim might have a strong MECHANISM warrant in the laboratory but be rejected by scientists if it creates incoherence with the broader theory. Conversely, a claim with weaker evidence might be accepted if it beautifully fills a gap in the theoretical structure.

Example: suppose we have a MECHANISM warrant claim that contradicts a foundational principle of cognitive psychology. Scientists might invest substantial effort in looking for artifacts or alternative explanations before accepting the claim. But if a claim with an ANALOGICAL warrant fits perfectly with existing theory and fills theoretical gaps, scientists might accept it more readily, even though the warrant type is weaker.

Warrant-typing alone doesn't capture this. It treats each claim as epistemically independent, when in fact scientists judge claims relative to the coherence of the entire system.

I propose supplementing warrant-typing with coherence analysis. When a claim is annotated with a warrant type, also specify: How well does this claim cohere with existing accepted theory? What would accepting this claim require us to revise in the broader theoretical system? Is the claim a natural extension of existing theory, or does it require significant modifications?

This could be formalized using constraint satisfaction, as in ECHO. Each warrant type specifies how strongly a claim is supported by direct evidence. Each coherence relation specifies how the claim relates to others: a MECHANISM warrant for X plus strong positive coherence with Y means that accepting X makes the system more coherent overall, which should increase the credence in X. A MECHANISM warrant for X plus strong negative coherence with foundational belief Z means that accepting X creates tension in the system, which should decrease the credence despite the warrant.

Here's what would make warrant-typing much stronger: embed it in a formal theory of explanatory coherence. This would show how warrant types interact with theoretical considerations to produce rational belief updates. Without this, the framework is incomplete.

---

### Andrea Saltelli — Focused Critique

I'll be blunt: the paper makes empirical claims about the ATLAS system without providing empirical support. Section 5.4 asserts that "mechanistic claims are more stable across time and research groups than claims supported by correlation," and Section 2 claims that warrant-typing answers questions about "what kind of evidence would reduce it [uncertainty]." These are factual claims about how science works. They need data.

If ATLAS contains 130 nodes and 400 edges over 1,000 articles, this is a valuable resource. But the paper doesn't report any systematic analysis of what actually happens to claims at different warrant types. Provide:

1. **Survival statistics**: For each warrant type, what percentage of claims initially classified as MECHANISM warrant remain accepted in the literature 5, 10, 20 years later? Provide survival curves with confidence intervals. Control for confounding factors like publication bias, sample size, and field.

2. **Prior calibration**: For each warrant type, what is the empirical frequency of claim success? If claims with MECHANISM warrants succeed 70% of the time and claims with ANALOGICAL warrants succeed 20% of the time, then these are your calibrated priors. Don't use 0.60 and 0.35 unless you can defend them with data.

3. **Uncertainty reduction analysis**: Track claims that move from one warrant type to another. When does a MECHANISM warrant get "promoted" to CONSTITUTIVE status? When does an EMPIRICAL_COVARIANCE warrant get "demoted" to CAPACITY status? What information flow causes these transitions? This is essential for validating the framework's claim about "what kind of evidence reduces uncertainty."

4. **Discount factor validation**: Test the discount factors proposed in Section 4.4. Compare laboratory effect sizes for claims across different warrant types with field effect sizes. Do MECHANISM claims really maintain 80-95% of their laboratory effect in the field, while EMPIRICAL_COVARIANCE claims maintain only 40-70%? These are testable hypotheses.

5. **Inter-rater reliability**: How consistent are different experts at assigning warrant types? If two experts disagree about whether a claim has a MECHANISM or EMPIRICAL_COVARIANCE warrant, what causes the disagreement? This is crucial for any practical implementation.

6. **Sensitivity analysis**: How robust are your stability findings to different operationalizations of "stability"? What if you measure stability as effect size consistency instead of paper survival? What if you weight papers by citation count? Do the conclusions change?

Without this empirical grounding, the framework is sophisticated speculation. With it, it becomes actionable science. The paper should either provide this analysis or explicitly identify it as future work.

---

### James Woodward — Focused Critique

I want to develop my interventionist critique more precisely. The paper claims that warrant types map onto interventionist evidence (Section 5.1), but the mapping is more complicated than presented.

My fundamental definition is: X causes Y if there exists an intervention I(X) such that if we perform I, the value of Y changes. The strength of evidence for "X causes Y" depends on how much we know about I and its effects.

Now, how do warrant types support interventionist claims?

**CONSTITUTIVE warrants** don't directly support causal claims at all. Knowing that "lux at the retina" is measured doesn't establish that intervening on lux would change any downstream outcome. It establishes that we're measuring the right thing, but not that the thing causes anything. I agree with Cartwright's criticism here.

**MECHANISM warrants** support interventionist claims, but only for the specific mechanism that's been characterized. If we understand the pathway "light → retinal cell activation → serotonin synthesis," this supports the causal claim "light affects serotonin synthesis." It tells us what would happen if we intervened: we'd increase serotonin. But it doesn't tell us what would happen downstream. Increasing serotonin might not increase mood if downstream mechanisms are missing or suppressed. So MECHANISM warrants support causal claims about the mechanism itself, but not necessarily about broader effects.

This suggests that we need warrant types indexed to specific causal claims, not to general evidence. Instead of saying "this paper provides MECHANISM warrant evidence," we might say: "This paper provides MECHANISM warrant evidence for the claim 'light affects serotonin,' but only EMPIRICAL_COVARIANCE warrant evidence for the claim 'daylight improves occupant mood,' because the link between serotonin and mood is unmeasured and correlational."

**EMPIRICAL_COVARIANCE warrants** provide evidence that X and Y are associated, but not which causes which, and not in the absence of confounding. So they provide minimal interventionist support. Seeing a correlation between window area and reported mood is consistent with three different causal structures: window → mood, mood/wealth → window, wealth → both. EMPIRICAL_COVARIANCE warrants can't distinguish these.

**CAPACITY warrants** indicate that a causal pathway might exist but hasn't been demonstrated. These provide the weakest interventionist support.

**ANALOGICAL warrants** are speculations about causal structure based on similarities to known systems. They provide defeasible interventionist support.

The implication: we need to be much more careful about the specificity of causal claims that warrant types support. A claim like "X causes Y in system S under conditions C, through mechanism M, affecting outcome Z" is more precise than "daylight affects serotonin." The warrant type should specify what claims it supports.

Furthermore, interventionist support for a mechanism is not the same as interventionist support for the mechanism having a downstream effect. If we know the mechanism light → serotonin, we can intervene with confidence on light to produce serotonin changes. But we cannot intervene with confidence on light to produce mood changes unless we also know that serotonin affects mood.

I would recommend that warrant types be specified relative to particular causal claims with particular scope conditions. This would make the intervention-supporting properties of warrant types much clearer.

---

### Craig Fox — Focused Critique

Two focused concerns about the behavioral aspects of warrant-typing.

First, **warrant-type communication**: The paper doesn't address how warrant types should be communicated to users who will make decisions based on them. This is important because my research shows that how uncertainty is framed dramatically affects decisions. Suppose I tell a user: "This claim has a MECHANISM warrant." Most users will interpret this as "This claim is reliable." But if I say, "This claim has strong evidence for the mechanism but hasn't been validated in the field," the user might be more appropriately cautious.

The problem is that warrant types are a technical distinction that doesn't map directly onto user understanding. To make the framework useful for decision-making, you need to communicate warrant types in ways that accurately convey their epistemic status without creating false confidence.

This is related to a phenomenon I call **expertise-belief asymmetry**: experts understand nuances in evidence (e.g., that a mechanism is well-characterized but its field manifestation is untested), but when they communicate findings to stakeholders, these nuances get lost. The stakeholder hears "mechanistic evidence" and interprets it as "high confidence." Warrant-typing could help address this if it's paired with explicit communication guidelines.

Second, **motivated reasoning and warrant-type judgment**: People's assignments of warrant types are influenced by motivations. If someone is motivated to believe a claim, they're more likely to interpret available evidence as mechanistic ("There's definitely a mechanism; we just haven't characterized all the details"). If someone is motivated to disbelieve a claim, they'll emphasize limitations ("It's really just a correlation; the mechanism is speculative").

This is well-documented in research on motivated cognition and belief polarization. The framework needs to acknowledge this and provide guidance on how to elicit reliable warrant-type judgments despite motivated bias.

One approach: use structured expert elicitation protocols that require experts to justify their warrant-type assignments explicitly. Instead of asking "Is this a MECHANISM warrant?" ask "List all the independent causal pathways that have been experimentally validated for this claim. For each pathway, state which studies validated it." This forces specificity and makes motivated reasoning more transparent.

Without attention to these psychological factors, warrant-typing will become another technical tool that experts understand but non-experts misuse, or that experts use to confirm preexisting beliefs.

---

## ROUND 3: CROSS-PANEL DEBATE

**Moderator**: Thank you all for your focused critiques. I'd like to draw out some of the key disagreements and see if we can make progress on them. Let me start with a fundamental disagreement about formalization.

**Judea Pearl (responding to the panel)**: I want to press on the formalization issue because I think it's fundamental. Nancy, you emphasize the distinction between capacity and manifestation, which is brilliant, but how do we formalize it? If I don't have a formal representation of what "capacity" means versus "manifestation," I can't build a computational system that reliably makes distinctions between warrant types. Don't you agree that we need mathematics?

**Nancy Cartwright**: I do think formalization is valuable, Judea, but I'm wary of formalizing too early. Causal capacities have a complicated ontology — they're not properties of individual systems but properties of types of systems, relative to contexts. If we formalize prematurely, we might force causal concepts into mathematical structures that distort them. My suggestion is that we first develop a rich conceptual analysis of how warrant types relate to capacities, manifestation conditions, and context dependence. Once that's clear, formalization becomes tractable.

**Judea Pearl**: But without formalization, how do you know you've got the conceptual analysis right? The SCM framework has shown that many commonsense notions about causation are either incoherent or need significant refinement when you try to formalize them. The same will be true here. I'd rather have a wrong formal theory that can be refuted than a right informal one that can't be tested.

**Andrea Saltelli**: I agree with Judea about the need for empirics, though maybe not his specific formalization. My point is simpler: you have data. The ATLAS system contains 130 nodes and 400 edges across 1,000 articles. You should have analyzed this systematically to test your claims. Which warrant types survive longer in the literature? Which ones lead to successful field applications? These are empirical questions with empirical answers. Why don't you provide the data?

**Kirsh (implied)**: The framework was developed FROM the ATLAS analysis, so the question is how to present those results credibly. This is fair criticism.

**Sarah Moss**: Can I push on a different angle? The debate between Nancy and Judea is about whether to formalize, but I think there's a prior question: what exactly is being formalized? Judea wants to map warrant types onto SCM identifiability conditions. Nancy wants a conceptual analysis of capacities and manifestation. But maybe what warrant-typing is really capturing is something about EVIDENTIAL STRUCTURE — the information content of different kinds of evidence. If that's what we're formalizing, it might look quite different from either SCM identifiability or capacity ontology.

**Paul Thagard**: Sarah's right. And I'd add that from a computational philosophy of science perspective, what matters is not just the structure of individual evidence, but how that evidence integrates with broader theoretical commitments. A piece of mechanistic evidence in isolation is different from mechanistic evidence that creates theoretical friction. Warrant-typing captures the first but not the second.

**James Woodward**: Let me try to build on this. I think warrant types are fundamentally about what kinds of INTERVENTIONS they support evidence for. A MECHANISM warrant supports evidence for a very specific claim: "If we intervene on X in this specific way, Y will change through this specific pathway." An EMPIRICAL_COVARIANCE warrant supports evidence for a much weaker claim: "X and Y are associated." The warrant types are distinguished by the specificity of the intervention they support evidence for. If we formalize this, we should formalize it in terms of what interventions each warrant type can justify.

**Nancy Cartwright**: That's useful, James. And it connects to my point about manifestation conditions. A warrant type that supports an intervention in the laboratory might not support it in the field because the manifestation conditions differ. So we need to index warrant types to contexts and to the specific interventions they support.

**Andrea Saltelli**: This brings me back to empirical grounding. You're saying that warrant types should be indexed to (context, intervention, manifestation conditions). Fine. But then you need to operationalize this. What counts as "successful manifestation"? When you move from laboratory to field, what measure of success do you use? Do you care whether the effect size is the same, or just that the effect direction is the same? The answer matters enormously for setting discount factors.

**Craig Fox**: And from a decision-making perspective, I'd add that the discount factors should be calibrated to actual user needs. Some decision-makers need high confidence before acting (medical decisions, for instance), while others can tolerate more uncertainty (exploratory design, for instance). The discount factors might not be context-independent; they might depend on the decision context.

**Moderator**: This brings up the question of what practical guidance warrant-typing actually provides. Let me ask directly: suppose I'm an architect deciding whether to include lots of windows in a new building. The evidence says windows increase serotonin production. I know it's a MECHANISM warrant. How does that change my decision compared to if it were an EMPIRICAL_COVARIANCE warrant?

**Paul Thagard**: It should change your confidence in whether the mechanism will activate in your specific building context. The mechanism is stable and well-characterized, so you can have more confidence that if light reaches the retina, serotonin increases. But whether occupants will experience mood benefits depends on downstream factors that might not be mechanistic.

**Nancy Cartwright**: Exactly. The MECHANISM warrant tells you "the capacity exists and here's how it works." But what you need for your decision is "the capacity will manifest in my building under my conditions." To answer that, you need to check the manifestation conditions. Are occupants under circadian-rhythm conditions where serotonin production is responsive? Are they in task conditions where mood matters? Will the window design actually allow sufficient light to reach the retina, or will it be blocked by glare, overexposure, etc.? The warrant type provides one piece of information; manifestation-condition analysis provides the crucial piece.

**Armen Der Kiureghian**: This connects to my frustration with the discount factors. They're presented as fixed (0.8-0.95 for MECHANISM), but in reality, the appropriate discount depends on field-specific factors. The framework would be much more useful if it provided a method for estimating the discount factor given a specific field context, rather than a fixed number.

**Andrea Saltelli**: And you'd want to know the uncertainty in that discount factor. Is it 0.8 ± 0.05 or 0.8 ± 0.3? The latter implies much greater uncertainty about field transferability.

**James Woodward**: Let me push back slightly. I think some of the disagreement here is about what warrant-typing is supposed to do. If it's supposed to solve the complete problem of context-sensitive causal reasoning, then you're right that it needs supplementation with manifestation conditions, context factors, and detailed empirical analysis. But maybe that's asking too much of one framework. Maybe warrant-typing is just one component of a larger epistemic system that also includes capacity analysis (Cartwright), SCM identifiability (Pearl), coherence analysis (Thagard), and practical context analysis (Fox, Der Kiureghian).

**Nancy Cartwright**: That's fair. But then we should be honest about the limits. The paper sometimes oversells what warrant-typing alone can do. It can't by itself tell you whether a claim will transfer to a new context — it just tells you that mechanistic claims transfer better than correlational claims as a statistical tendency, and that tendency can be overcome by specific contextual factors.

**Craig Fox**: I also want to revisit the psychological realism issue. The paper says warrant-typing is prescriptive, not descriptive, and I agree with that. But if it's meant to be a tool for decision-makers, we need to know how people can learn to use it. Does training help people distinguish warrant types? Do visual representations (e.g., showing the mechanistic pathway) help? My research suggests that people can learn to distinguish epistemic from aleatory uncertainty with appropriate prompting, but it's not automatic.

**Sarah Moss**: And there's another psychological question: as people learn about warrant types, does their confidence become better calibrated? Do they overweight mechanistic evidence because it "feels" more reliable? Do they underweight correlational evidence because of the language around confounding vulnerability? You need research on how warrant-typing affects actual judgment and decision-making.

**Andrea Saltelli**: This is why I come back to empirical validation. You need prospective studies where research allocation decisions are made using warrant-typing compared to control groups. You need field experiments where recommendations based on warrant-typing are tested for accuracy. The framework's value should be measured by real-world success, not just conceptual coherence.

**Judea Pearl**: I want to return to the formalization question because I think it's connected to the empirical validation question. If warrant types are formally defined in terms of SCM identifiability, then we can make precise predictions about when warrant-type promotion is possible and what additional evidence is needed. "To promote a claim from EMPIRICAL_COVARIANCE to MECHANISM warrant requires identifying a mediating variable that blocks all backdoor paths." That's a formal, testable prediction. Without formalization, such predictions become vague.

**Nancy Cartwright**: I see your point, Judea, and I'm not opposed to formalization in principle. But I'd want to make sure the formalization captures the phenomenology of how scientists actually reason about mechanisms. Some mechanisms are more "complete" than others — they might identify the overall pathway but not all the molecular details. The question of what counts as sufficient mechanistic understanding to warrant a MECHANISM designation is fundamentally a philosophical question about levels of description, not just a technical question.

**Paul Thagard**: This is where explanatory coherence comes in. A mechanistic claim is more compelling if it explains a broader range of phenomena, if it fits with existing theory, if it generates novel predictions. These are the kinds of considerations that distinguish a well-articulated mechanism from a merely possible mechanism. A formal SCM might capture the structure of the causal claim, but it doesn't capture how well the explanation coheres with the broader knowledge system.

**Armen Der Kiureghian**: I think the real test will be whether warrant-typing provides practical value beyond existing frameworks. We already have Bayesian networks for reasoning under uncertainty. We already have sensitivity analysis for understanding parameter importance. We already have structured expert elicitation for assessing evidence. Does warrant-typing improve on these? Does it lead to better decisions, more efficient research allocation, more accurate predictions? That's the question that matters.

**Andrea Saltelli**: Yes. And that's why I keep asking for empirical validation. Show me data that warrant-typing leads to better decisions than the status quo. Until then, it's an interesting idea with potential, but not a proven improvement.

**Moderator**: This is useful. Let me pose one more question before we move to the recommendations. Nancy and others have criticized the seven-type hierarchy as potentially arbitrary. Are there domains where fewer types suffice? Or are there domains that need more types? Kirsh mentions that other domains might need different typologies. Is warrant-typing a general methodology, or is it domain-specific?

**Paul Thagard**: From a philosophy of science perspective, I think the typology should be relatively stable across domains. All sciences deal with mechanisms, correlations, analogies, and theoretical hypotheses. But the question of which intermediate types matter (FUNCTIONAL, CAPACITY) might vary by domain. In cognitive science, the capacity-manifestation distinction might be crucial because of the importance of contextual influences on behavior. In physics, it might be less important because field conditions are more controlled.

**Andrea Saltelli**: And the priors assigned to each type should definitely vary by domain. In a well-established field like molecular biology, a MECHANISM warrant might deserve prior 0.75 because mechanisms are well-understood and field-validated. In an emerging field like environmental psychology, a MECHANISM warrant might deserve prior 0.40 because the mechanistic claims are newer and less validated. The framework should be flexible about this.

**James Woodward**: I'd like to see the framework developed to show how warrant types could be combined with domain-specific knowledge about intervention efficacy. In medicine, we have decades of data on how laboratory drug efficacy translates to field effectiveness. Those data could inform the discount factors. In architecture, you have less historical data, so discount factors would need to be more conservative. The framework should make this kind of domain-specific reasoning explicit.

**Moderator**: Thank you. Let's move to the constructive phase.

---

## ROUND 4: WHAT WOULD MAKE THIS PAPER EXCELLENT?

### Nancy Cartwright

To make this paper excellent, I would recommend three changes:

**First, develop the manifestation-condition analysis explicitly.** Each major claim should specify not just its warrant type but the conditions under which the corresponding capacity will manifest. For "daylight increases serotonin," specify: "MECHANISM warrant, Prior 0.60, Manifestation conditions: (a) functional retinal cells, (b) functional raphe nuclei, (c) circadian state permitting serotonin modulation, (d) sufficient light intensity reaching the retina, (e) absence of SSRI medications." This transforms the framework from a classification of evidence into a tool for field application.

**Second, provide empirical analysis of warrant-type stability and field transfer.** Present the ATLAS data on which warrant types are associated with stable, reproducible findings. Create survival curves for claims at each warrant type. This provides empirical grounding for the priors assigned to each type.

**Third, develop explicit guidance on context-sensitive discounting.** The fixed discount factors (0.8-0.95 for MECHANISM) should be replaced with a decision procedure: given a laboratory claim with a warrant type, and given information about field manifestation conditions, estimate the probability that the claim will transfer to the field. This is a hard problem, but it's the problem that matters for practical application.

---

### Judea Pearl

Two recommendations:

**First, formalize warrant types in terms of SCM identifiability conditions.** Provide a technical appendix showing how each warrant type corresponds to a particular identifiability status. Prove theorems about when warrant-type promotion is possible (e.g., "A claim with EMPIRICAL_COVARIANCE warrant can be promoted to MECHANISM warrant if and only if confounding variables are measured and a causal model is specified"). This would give the framework rigorous foundations.

**Second, connect warrant-typing to value-of-information analysis formally.** VOI analysis in decision theory tells us the expected benefit of acquiring additional information. Different warrant types should correspond to different information-acquisition problems. Formalize this: what is the VOI of measuring a mediating variable to upgrade EMPIRICAL_COVARIANCE to MECHANISM? This would operationalize the prescriptive research strategies that warrant-typing suggests.

---

### Armen Der Kiureghian

**First, validate discount factors empirically.** Conduct meta-analysis comparing laboratory effect sizes for claims across warrant types with field replication effect sizes. Do MECHANISM claims really maintain 80-95% of laboratory magnitude in the field? Do EMPIRICAL_COVARIANCE claims maintain 40-70%? Provide confidence intervals.

**Second, integrate with existing UQ infrastructure.** Show how warrant types translate into probability distributions for use in Monte Carlo simulation and sensitivity analysis. If a claim has a MECHANISM warrant with prior 0.60 and applies in a new context with 0.9 transfer probability, does this mean we should use a distribution concentrated at 0.54? Show the technical integration concretely.

**Third, demonstrate field success.** Conduct a prospective study where research allocation decisions for an engineering problem are made using warrant-typing guidance versus standard approaches. Measure which approach produces better field outcomes and more efficient research.

---

### Sarah Moss

**First, supplement warrant types with evidence-strength indicators.** Instead of just assigning a warrant type, report the number of independent studies supporting it, effect size ranges, and consistency across populations. Convert the prior probability into a confidence interval. This anchors the framework in actual empirical data.

**Second, formalize the relationship between warrant types and coherence.** Develop a model where warrant type assigns a prior credence to a claim, while coherence with other beliefs modifies this credence. Show how a MECHANISM warrant with poor theoretical coherence might end up with lower final credence than an ANALOGICAL warrant with excellent coherence. This would integrate warrant-typing with broader epistemology.

**Third, model warrant-type transitions explicitly.** When do claims move from ANALOGICAL to MECHANISM status? What evidence triggers this transition? Formalize the conditions under which warrant types change, and show how agents should update their belief systems when claims change warrant type.

---

### Paul Thagard

**First, integrate warrant-typing with explanatory coherence analysis.** For each major claim, assess: how well does this claim cohere with existing accepted theory? What modifications to the theoretical system are required to accommodate it? Use constraint satisfaction to show how warrant type and coherence jointly determine credence.

**Second, model theory choice using warrant types.** When scientists choose between competing theories, they consider not just individual claims but overall theoretical coherence. Show how warrant-typing of individual claims should affect theory choice. Does a theory with all MECHANISM warrants beat a theory with mostly EMPIRICAL_COVARIANCE warrants? Only if other factors are equal; coherence and simplicity might flip the preference.

**Third, use warrant-typing to improve computational philosophy of science.** Extend the ATLAS system to model scientific change as transitions in warrant types and coherence relations. Show how the history of a field (e.g., the history of environmental psychology) can be understood as progressive movement toward more mechanistic understanding and greater theoretical coherence.

---

### Andrea Saltelli

**First, provide complete empirical analysis of ATLAS.** Report frequencies of outcome success for claims at each warrant type. Provide survival curves for 5, 10, and 20-year periods. Control for confounding factors: publication bias, prestige of publishing venue, sample size, interdisciplinary adoption. These data will calibrate the priors and validate the framework.

**Second, conduct inter-rater reliability studies.** Have multiple experts independently assign warrant types to a sample of ATLAS claims. Measure agreement and identify sources of disagreement. If experts disagree about which warrant type applies, the framework has a communication problem that needs solving.

**Third, design prospective validation experiments.** Take a domain (architectural neuroscience, environmental psychology) and make research allocation recommendations based on warrant-typing. Compare to a control group using standard strategies. Measure which approach produces more stable, field-validated knowledge over a 5-year period.

---

### James Woodward

**First, make interventionist scope explicit.** For each claim, specify exactly what causal statement the warrant supports. "MECHANISM warrant for 'light affects serotonin synthesis in humans' but only EMPIRICAL_COVARIANCE warrant for 'improving serotonin improves occupant mood' because the serotonin-mood link is unmeasured." This prevents overreach.

**Second, index warrant types to contexts and timescales.** A MECHANISM warrant might apply for short-term effects (minutes) but not long-term effects (months) when confounding accumulates. A MECHANISM warrant might apply in laboratory conditions but not in field conditions when manifestation factors enter. Make these qualifications explicit.

**Third, develop a formal account of when warrant types support intervention claims.** Specify precisely what it means for a warrant type to "support" an intervention claim. Is it sufficient that the causal pathway is characterized? Or must we also know the magnitudes and the downstream effects? This clarity would prevent overconfidence in mechanistic reasoning.

---

### Craig Fox

**First, design user-centered communication strategies for warrant types.** How should warrant types be presented to decision-makers? Research shows that probability itself is poorly communicated; warrant types are even more complex. Develop and test communication designs that convey warrant information accurately without triggering false confidence in mechanistic claims.

**Second, model how warrant-type judgments are affected by motivation and reasoning biases.** People will interpret evidence in motivated ways (interpreting ambiguous evidence as mechanistic if motivated to believe the claim). Develop protocols for eliciting reliable warrant-type judgments that mitigate this bias, perhaps through structured expert elicitation with explicit justification requirements.

**Third, measure whether training on warrant-typing improves actual decision quality.** Train a group of decision-makers on warrant-typing and compare their decisions to a control group. Measure calibration (are they appropriately confident?), decision speed, and field success rates. This will show whether the framework delivers practical value.

---

## ROUND 5: THE BIG QUESTION — IS THIS A GENUINE CONTRIBUTION?

### Nancy Cartwright

Yes, warrant-typing is a genuine contribution, but it's a conceptual contribution that needs to be much more rigorous about the distinction between universal capacities and their local manifestation. Kirsh has taken an old philosophical idea — that causal properties are real but context-dependent — and given it concrete form in a framework that computational systems can implement. That's valuable. But the framework as currently presented is incomplete because it doesn't fully specify the context-dependence problem. With further development around manifestation conditions, it will be a major contribution to philosophy of science and applied epistemology.

---

### Judea Pearl

Warrant-typing is a useful framework, but it's not a new idea. The distinction between different kinds of causal evidence (mechanisms vs. correlations vs. analogies) is implicit in causal reasoning everywhere. What would make it a genuine contribution is axiomatization. I want to be able to prove theorems about warrant types. "Under what conditions can warrant type X be promoted to warrant type Y?" This requires formalization. Without it, warrant-typing is sophisticated bookkeeping, not a scientific contribution.

---

### Armen Der Kiureghian

From an engineering perspective, warrant-typing makes a genuine contribution by systematizing something we already know intuitively: mechanisms are more robust than correlations. But intuition is not enough for engineering. We need empirical validation. If the paper provided evidence that warrant-typing guidance leads to better field outcomes than standard approaches, then yes, it's a major contribution. Without that evidence, it's a promising framework awaiting validation.

---

### Sarah Moss

Warrant-typing is a genuine contribution to epistemology because it offers a structured way to think about how evidence of different kinds should be weighted. The framework sits between coherentism and foundationalism in a way that hasn't been systematically developed before. But the paper needs to be much more rigorous about formalization and about the interaction between warrant types and other epistemic considerations (coherence, parsimony, explanatory power). With further development, it could be a landmark contribution to formal epistemology.

---

### Paul Thagard

As a contribution to computational philosophy of science, warrant-typing is valuable. The ATLAS implementation shows that you can build a knowledge system that tracks not just probabilities but the kinds of evidence that probabilities rest on. This is exactly the direction the field needs to move. The contribution is genuine, but it's incomplete without explicit attention to coherence and theoretical integration. With that addition, it becomes a major advance.

---

### Andrea Saltelli

Warrant-typing could be a genuine contribution to uncertainty quantification and evidence synthesis, but the paper doesn't prove it because it doesn't provide empirical validation. The ideas are sound and potentially useful, but "potentially useful" isn't the same as "genuinely valuable." Show me data that warrant-typing improves on existing methods. Then it's a genuine contribution. Until then, it's an interesting proposal with the potential to be important, but not proven important.

---

### James Woodward

Warrant-typing is a genuine contribution to causal epistemology because it provides a systematic way to grade the strength of evidence for causal claims based on how much we know about the causal mechanism. This is philosophically sound and practically useful. The contribution is already real, but it would be much stronger if developed more carefully in terms of what specific interventionist claims each warrant type supports. As currently presented, it's a solid contribution; with further refinement, it could be foundational.

---

### Craig Fox

Warrant-typing is a genuine conceptual contribution that psychology and decision science need. Showing that people can (and should) distinguish different sources of epistemic uncertainty, and should make different decisions based on warrant type, is important. But the practical contribution depends on whether the framework actually helps people reason better. If training on warrant-typing improves judgment and decision-making, it's a major contribution. If it doesn't, it's theoretically nice but practically useless. The paper needs to measure this.

---

## SYNTHESIS: Prioritized Recommendations

### Essential Priorities (Must address for credibility)

**1. Provide empirical analysis of ATLAS data on warrant-type stability and field transfer**
- *Panelists:* Saltelli, Der Kiureghian, Cartwright, Fox
- *Requirement level:* Essential
- *Details:* Report frequencies of claim success by warrant type, survival curves for 5/10/20-year periods, empirical calibration of priors, control for confounding factors in analyses. This is the cornerstone of empirical grounding.

**2. Develop explicit manifestation-condition analysis for field application**
- *Panelists:* Cartwright, Woodward, Der Kiureghian
- *Requirement level:* Essential
- *Details:* For each major claim, specify the contextual conditions required for the mechanism/capacity to manifest in the field. Provide decision procedures for estimating transfer probability to specific field contexts.

**3. Clarify the scope of interventionist claims each warrant type supports**
- *Panelists:* Woodward, Pearl, Cartwright
- *Requirement level:* Essential
- *Details:* Make explicit what causal claims each warrant type justifies evidence for. Specify that MECHANISM warrants support specific mechanism claims, not necessarily downstream outcome claims. Index claims to specific interventions and outcomes.

### High-Priority Developments (Needed for robustness)

**4. Formalize warrant types in terms of identifiability conditions or epistemic structure**
- *Panelists:* Pearl, Moss, Woodward
- *Requirement level:* High priority
- *Details:* Either map warrant types to SCM identifiability conditions (Pearl's approach) or formalize the evidential structure problem (Moss's approach). Either choice would give the framework theoretical grounding and enable proof of theorems about warrant-type promotion.

**5. Supplement warrant types with evidence-strength indicators**
- *Panelists:* Moss, Saltelli, Fox
- *Requirement level:* High priority
- *Details:* Don't just assign warrant type; report number of independent studies, effect size ranges, consistency across populations. Convert priors from point estimates to confidence intervals anchored in empirical data.

**6. Integrate with explanatory coherence analysis**
- *Panelists:* Thagard, Moss, Fox
- *Requirement level:* High priority
- *Details:* Show how warrant types interact with theoretical coherence to determine credence. A mechanistic claim with poor coherence might end up with lower credence than an analogical claim with good coherence. Formalize this trade-off.

**7. Conduct inter-rater reliability and warrant-type agreement studies**
- *Panelists:* Saltelli, Fox, Moss
- *Requirement level:* High priority
- *Details:* Have multiple experts independently assign warrant types to a sample of claims. Measure agreement; identify sources of disagreement. If experts disagree, the framework has a communication/operationalization problem.

### Medium-Priority Enhancements (Valuable if resources permit)

**8. Design and test user-centered communication strategies**
- *Panelists:* Fox, Craig Fox, Thagard
- *Requirement level:* Medium priority
- *Details:* Develop communication designs that convey warrant-type information to decision-makers without triggering false confidence. Test these designs empirically to show they improve judgment.

**9. Develop domain-specific instantiations of the framework**
- *Panelists:* Der Kiureghian, Saltelli, Pearl
- *Requirement level:* Medium priority
- *Details:* Apply the framework to 2-3 other domains (medicine, materials science, climate science) and show how warrant typology needs to adapt to domain-specific evidence structures. This will clarify whether warrant-typing is a general methodology or domain-specific.

**10. Conduct prospective validation experiments**
- *Panelists:* Saltelli, Der Kiureghian, Fox
- *Requirement level:* Medium priority
- *Details:* Make research allocation recommendations using warrant-typing guidance; compare to control group using standard approaches. Measure which approach produces more stable, field-validated knowledge over 5+ years. This demonstrates practical value.

---

## CONCLUSION

The expert panel recognizes "Why Warrant Types Matter" as a conceptually sound and potentially important contribution to computational philosophy of science, epistemology, and uncertainty quantification. David Kirsh has identified a real problem — that bare probabilities hide the character of the evidence behind them — and proposed a systematic framework for annotating claims with evidence types. The ATLAS implementation demonstrates that the framework is implementable at non-trivial scale.

However, the paper in its current form is incomplete in four critical ways:

1. **Lack of empirical grounding**: Claims about warrant-type stability and field transfer are presented without supporting data from ATLAS analysis.

2. **Insufficient formalization**: The mapping from warrant types to formal causal or epistemic structures needs to be made explicit, enabling proofs and precise predictions.

3. **Incomplete application framework**: The paper doesn't fully specify how warrant types should guide field application through manifestation-condition analysis and context-sensitive reasoning.

4. **Missing psychological/communication dimension**: The paper doesn't address how warrant types should be communicated to decision-makers or how judgment quality improves with warrant-type reasoning.

With revisions addressing these gaps—particularly the empirical analysis of ATLAS, formalization of the framework, and explicit manifestation-condition analysis—this paper has the potential to become a landmark contribution to how scientific communities reason about and integrate heterogeneous evidence. In its current form, it is a promising proposal; with the recommended revisions, it could be transformative for applied epistemology, computational science, and evidence-based decision-making.

