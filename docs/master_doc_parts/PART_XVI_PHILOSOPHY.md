# PART XVI: ARCHITECTURAL PHILOSOPHY — THE WEB-BN RELATIONSHIP (§125–127)

*Editorial Transition: This Part continues from the architectural foundations established in Part IX (§84–89), where mechanism chain traversal and the role of the Bayesian Network in architectural reasoning were first introduced. Here we deepen that analysis through three complementary perspectives: the philosophical distinction between epistemic and aleatory probability that governs how the system tracks uncertainty, the precise delimitation of what the Bayesian Network uniquely contributes (interventional and counterfactual reasoning), and the formalization of reflective equilibrium as the web's deepest epistemic operation. The material here draws on the tradition from Quine and Ullian (1970) through Thagard (1989, 2000) and Pearl (2009), and connects that tradition to the specific computational structures the ATLAS system has built.*

---

## §125: The Epistemic-Aleatory Distinction and Its Architectural Consequences

### 125.1 Two Kinds of Probability

Suppose you roll a fair die. You do not know what number will come up, and this ignorance is not a defect of your understanding — it is a feature of the die. The outcome is genuinely random. No amount of additional information about the die, the table, or your throwing technique (short of a complete Laplacian specification of every molecule) will eliminate this uncertainty. This is *aleatory uncertainty* — from *alea*, the Latin word for die. It describes the inherent stochasticity of a process.

Now suppose someone hands you a die and asks you whether it is fair. You examine it, roll it twenty times, get an unusual distribution of outcomes, and form a tentative judgment: "I believe with about 70% confidence that this die is biased." That 70% does not describe anything about the die's randomness. It describes your state of knowledge about the die. If you rolled it another thousand times, or cut it open and examined its weight distribution, your confidence would change — perhaps to 95% or perhaps to 20%. The die itself has not changed. What changed is what you know. This is *epistemic uncertainty* — from *episteme*, the Greek word for knowledge.

The distinction matters because the two kinds of uncertainty respond to entirely different interventions. Aleatory uncertainty is reduced by changing the process (engineering a more predictable system) or by averaging over many instances (the law of large numbers). Epistemic uncertainty is reduced by learning — by gathering evidence, refining theories, improving measurements, or simply thinking harder about what the existing evidence implies. Conflating the two leads to one of two errors: treating a knowledge gap as if it were inherent randomness (and therefore giving up on reducing it), or treating genuine randomness as if it were a knowledge gap (and therefore wasting effort trying to eliminate it).

In science, the distinction runs deep. When a meta-analysis reports that the effect of daylight on mood is *d* = 0.38 with a 95% confidence interval of [0.22, 0.54], two different kinds of uncertainty are tangled together. Part of the spread reflects genuine variation across people, settings, and measurement occasions — aleatory uncertainty in the population. Part reflects our imperfect knowledge of the true effect size — epistemic uncertainty due to finite samples, heterogeneous study designs, and possible publication bias. Separating these two components is not merely a philosophical nicety; it determines what you do next. If the spread is mostly aleatory (people genuinely differ in their response to daylight), then no amount of additional research will narrow it — you need to design for individual variation. If the spread is mostly epistemic (we just don't have enough good studies yet), then a well-designed replication will narrow it, and you should invest in that replication.

The Bayesian tradition in statistics has struggled with this distinction since at least de Finetti (1937), who argued that all probability is epistemic — a subjective degree of belief — and that aleatory probability is a fiction we impose on processes we do not fully understand. The frequentist tradition takes the opposite view: probability is a property of repeatable processes, and subjective degrees of belief are not probabilities at all. The modern consensus, articulated most clearly by Hacking (1975) and elaborated by Spohn (2012), is that both kinds are real, they serve different roles, and a mature probabilistic framework must track them separately.

In computational modelling, this separation has practical architectural consequences. A Bayesian network whose conditional probability tables contain aleatory probabilities (population frequencies) does something different from a system whose confidence scores contain epistemic probabilities (how certain we are that the model is correctly specified). The first system computes what will probably happen if you intervene. The second system computes how much you should trust the first system's answer. Mixing the two in a single numerical representation is a category error — like adding a distance and a temperature because both happen to be numbers.

### 125.1a The Distinction in the ATLAS system Architecture

The ATLAS system tracks both kinds of probability in architecturally distinct data structures. The failure to distinguish them is one of the most common sources of confusion in applied neuroscience, and the distinction maps directly onto the division of labour between the Web of Belief and the Bayesian Network.

**Aleatory probability** is what the Bayesian Network computes. The BN's conditional probability tables (CPTs) aspire to contain aleatory probabilities: P(Mood = positive | Daylight = high) = 0.70 is meant as a statement about population frequencies, not about the scientific community's confidence in a theory.

**Epistemic probability** is what the Web of Belief tracks. The web's confidence scores — the numbers that populate every template's calibration — are epistemic probabilities. They encode the scientific community's current best judgment about how much to trust each claim.

What is distinctive about the ATLAS system is the claim that a working computational system should maintain both kinds simultaneously, in different data structures, with explicit translation protocols between them. That is the ATLAS's architectural commitment, and it has consequences.

### 125.2 Bridge Warrant Types as Categorisations of Epistemic Uncertainty

The bridge warrant types — CONSTITUTIVE, MECHANISM, EMPIRICAL_ASSOCIATION, FUNCTIONAL, CAPACITY, ANALOGICAL, and THEORY_DERIVED — are not merely labels. They are *categorisations of epistemic uncertainty*. They tell you not just how confident the community is in a claim, but *why* the confidence is at its current level and, crucially, *what kind of evidence would change it*.

Consider two claims that happen to have the same numerical confidence of 0.35:

A MECHANISM bridge at 0.35 says: "The causal pathway from environmental feature to neural mechanism to outcome is well-characterised in laboratory conditions, but the architectural instantiation is uncertain. We know that the daylight → retinal stimulation → raphe nuclei → tryptophan hydroxylase → 5-HT synthesis chain operates in principle; we are uncertain whether it operates at sufficient magnitude in real buildings with real occupants over real time scales." The research that would raise this confidence is measurement of the mechanism *in architectural conditions* — ambulatory neurochemical monitoring, or at least measurement of the relevant behavioural outcomes in buildings with known daylight parameters.

An ANALOGICAL bridge at 0.35 says: "We are reasoning from a parallel case. The drug-related incentive sensitisation model (Berridge & Robinson, 1998) is structurally analogous to architectural place attachment, but the analogy may not hold. The neural substrate (mesolimbic DA) is shared, but the temporal dynamics, the stimulus parameters, and the phenomenological character of the experience may differ in ways that break the analogy." The research that would raise this confidence is fundamentally different: it requires establishing that the analogy *actually holds* — that the same mechanism operates in both domains, not merely that the two domains look similar from a distance.

These two claims carry completely different implications for research planning, for confidence in predictions, and for the appropriate caution when advising architectural practitioners. The warrant type captures information that a bare number cannot. This is why the web preserves warrant types as first-class annotations, and why the projection from web to BN is necessarily lossy: the BN receives a number (the CPT entry); the web retains the epistemological reasoning behind the number.

### 125.3 The Practical Import: Different Uncertainties Require Different Interventions

The distinction between epistemic and aleatory probability matters practically because the two kinds of probability respond to different interventions.

**Aleatory uncertainty is reduced by collecting more data from the same process.** If you want to narrow the confidence interval on P(Mood = positive | Daylight = high), you measure more occupants in more buildings. The population frequency becomes better estimated as the sample grows. This is the domain of classical statistics — larger N, tighter confidence intervals, more precise effect sizes.

**Epistemic uncertainty is reduced by improving the theoretical model.** If you want to increase confidence that the daylight → 5-HT → mood pathway is correctly specified, you do not (primarily) measure more occupants. You specify the mechanism more precisely. You resolve the competing account (circadian entrainment rather than direct serotonergic modulation). You replicate the Lambert et al. (2002) study with better methodology. You upgrade the bridge warrant from EMPIRICAL_ASSOCIATION to MECHANISM by tracing the pathway in an architectural context. These are qualitatively different research activities.

Confusing the two kinds of uncertainty leads to bad science. One common error is endlessly collecting more occupant data when the real problem is that the mechanism chain is wrong — this reduces aleatory uncertainty but leaves epistemic uncertainty untouched. Another common error is endlessly refining the theoretical model when the real problem is insufficient data — this increases theoretical sophistication but does not reduce aleatory imprecision. The web's Value of Information analysis (§129, Algorithm 5) is fundamentally about ranking epistemic uncertainties by their downstream consequences. The BN's statistical analysis is fundamentally about estimating aleatory parameters. Both are needed, and the architectural distinction between web and BN ensures that neither is confused with the other.

### 125.4 The CPT Elicitation Problem

The conditional probabilities in the BN's CPTs are never directly available from the web's epistemic content. The web's templates contain effect sizes (which are not conditional probabilities), confidence scores (which are epistemic, not aleatory), warrant types (which constrain ceilings, not CPTs), and qualifiers and rebuttals (which define domain restrictions, not numerical values). Translating this epistemic content into aleatory CPT entries is the CPT elicitation problem, and it is one of the most technically demanding steps in the web-to-BN projection.

A CPT elicitation protocol is needed — a structured method that converts Toulmin evidence structures into explicit CPT entries. The protocol should proceed as follows:

**Step 1 — Base rate extraction.** Start with the effect size from the strongest study in the Toulmin data array; convert to a base conditional probability. For example, if the strongest study reports d = 0.38 for daylight → mood, convert this to an approximate conditional probability via the standard normal CDF transformation: P ≈ Φ(d/√2) ≈ 0.61 for the treatment condition versus a baseline of 0.50.

**Step 2 — Bridge warrant discount.** Apply a multiplicative discount factor that reflects the epistemic distance between the laboratory evidence and the architectural application. The discount factors are derived from the bridge warrant hierarchy:

| Bridge Warrant Type | Discount Factor |
|---------------------|-----------------|
| CONSTITUTIVE | 0.90 |
| MECHANISM | 0.75 |
| EMPIRICAL_ASSOCIATION | 0.70 |
| FUNCTIONAL | 0.60 |
| CAPACITY | 0.55 |
| ANALOGICAL | 0.45 |
| THEORY_DERIVED | 0.50 |

These factors are themselves epistemic judgments, and they should be treated as calibratable parameters of the projection function. The retrodiction test (§130, Level 2) provides an opportunity to calibrate them empirically.

**Step 3 — Qualifier narrowing.** Apply domain-specific conditions from the template's qualifier field. If the qualifier states "effect strongest for morning light in buildings with high spatial complexity," the CPT entry should be conditioned on these variables (or alternatively, the BN should include these as moderator nodes).

**Step 4 — Rebuttal-derived uncertainty bands.** The rebuttal field specifies conditions under which the claim fails. These translate into the width of the uncertainty band around the CPT entry. A template with a strong rebuttal ("mechanism may not apply in naturally ventilated buildings because thermal comfort co-varies with daylight in these settings") has wider uncertainty bands than one with a weak rebuttal.

**Step 5 — Competing-account adjustment.** If the template has an unresolved competing account, the CPT entry should reflect the ambiguity. In the strongest case, the CPT entry is computed as a weighted average of the two accounts' implied values, with weights proportional to their respective credences.

This protocol should be formalised and applied retroactively to the entire calibrated corpus after CROSSCUT-I completes. The resulting CPTs will be the first numerically grounded aleatory probabilities in the ATLAS system, and they will carry explicit provenance — each entry will record the epistemic reasoning (steps 1–5) from which it was derived. This provenance is lost in the BN itself (which sees only numbers), but it is preserved in the web (which retains the full Toulmin structure). This asymmetry is by design: the BN is a computationally tractable snapshot of the web's current epistemic state, regenerated whenever the web revises.

### 125.5 References for §125

de Finetti, B. (1937). La prévision: Ses lois logiques, ses sources subjectives. *Annales de l'Institut Henri Poincaré*, 7(1), 1–68. [Google Scholar citations: ~4,500]

Der Kiureghian, A., & Ditlevsen, O. (2009). Aleatory or epistemic? Does it matter? *Structural Safety*, 31(2), 105–112. https://doi.org/10.1016/j.strusafe.2008.06.020 [Google Scholar citations: ~1,800]

Fox, C. R., & Ülkümen, G. (2011). Distinguishing two dimensions of uncertainty. In W. Brun, G. Keren, G. Kirkebøen, & H. Montgomery (Eds.), *Perspectives on thinking, judging, and decision making* (pp. 21–35). Universitetsforlaget. [Google Scholar citations: ~250]

Hacking, I. (1975). *The emergence of probability*. Cambridge University Press. [Google Scholar citations: ~3,200]

Hájek, A. (2019). Interpretations of probability. In E. N. Zalta (Ed.), *Stanford Encyclopedia of Philosophy*. Stanford University. [Authoritative reference entry]

Lambert, G. W., Reid, C., Kaye, D. M., Jennings, G. L., & Esler, M. D. (2002). Effect of sunlight and season on serotonin turnover in the brain. *The Lancet*, 360(9348), 1840–1842. https://doi.org/10.1016/S0140-6736(02)11737-5 [Google Scholar citations: ~1,100]

Pearl, J. (2009). *Causality: Models, reasoning, and inference* (2nd ed.). Cambridge University Press. https://doi.org/10.1017/CBO9780511803161 [Google Scholar citations: ~28,000]

Quine, W. V. O., & Ullian, J. S. (1970). *The web of belief*. Random House. [Google Scholar citations: ~2,500]

Reichenbach, H. (1949). *The theory of probability*. University of California Press. [Google Scholar citations: ~2,000]

Savage, L. J. (1954). *The foundations of statistics*. Wiley. [Google Scholar citations: ~15,000]

Spohn, W. (2012). *The laws of belief: Ranking theory and its philosophical applications*. Oxford University Press. [Google Scholar citations: ~600]

Thagard, P. (1989). Explanatory coherence. *Behavioral and Brain Sciences*, 12(3), 435–467. https://doi.org/10.1017/S0140525X00057046 [Google Scholar citations: ~2,400]

von Mises, R. (1928). *Wahrscheinlichkeit, Statistik und Wahrheit*. Springer. [Google Scholar citations: ~2,100]

---

## §126: The Bayesian Network's Irreducible Contribution — Do-Calculus and Counterfactuals

### 126.1 The Web's Surprising Self-Sufficiency

One of the most important revisions to the ATLAS's architectural self-understanding, achieved in the February 25 session, concerns the scope of what the web can accomplish on its own. The earlier understanding (reflected in §85 and §49 of the master document) treated the Web of Belief and the Bayesian Network as roughly symmetrical partners: the web provided qualitative reasoning and the BN provided quantitative reasoning, each contributing what the other lacked. This picture is wrong in a consequential way.

The web can compute quantitative consequences *through its own mechanism chains* by compositional reasoning. When the web encodes a mechanism chain such as:

> daylight increases 5-HT synthesis (d = 0.38) → 5-HT moderates the wanting-liking balance (d = 0.45) → wanting drives approach motivation (d = 0.55)

the web can propagate these effect sizes compositionally along the chain to derive the expected compound effect. Each step in the chain carries a numerical parameter (the effect size from the Toulmin data), a bridge warrant type (governing the attenuation of confidence across the inferential step), and qualifier conditions (specifying where the step applies). The web can multiply these along the chain, apply the appropriate bridge warrant discounts, and produce a numerical estimate of the downstream effect. It does not need the BN for this.

This is not a minor point. It means that the compositional quantitative reasoning the ATLAS system performs when tracing a mechanism chain from environmental feature through neural mechanism to occupant outcome — the central operation described in Part I's 30 worked examples — is a *web* operation, not a BN operation. The web is where mechanism chains live, where their parameters are calibrated, and where the compositional multiplication is performed. The BN enters the picture only when the question shifts from "what does our theory predict?" to "what happens if we intervene, controlling for confounders?"

### 126.2 The Two Things the Web Cannot Do

What the web *cannot* do — and what the BN uniquely provides — falls into two tightly defined categories.

**First: Interventional reasoning (do-calculus).** The web can trace causal pathways, but it cannot formally distinguish *observing* that daylight is high from *intervening* to make daylight high. This is Pearl's (2009) fundamental insight, and it is not a technicality — it is the core of causal inference. When you *observe* that daylight is high in a building, you learn something about the building's orientation, the weather, the season, the latitude, the window-to-wall ratio, and the maintenance of the glazing. All of these may independently affect mood and productivity. The observed correlation between high daylight and positive mood is confounded by every common cause of daylight and mood that you have not controlled. When you *intervene* to make daylight high (by installing full-spectrum lighting, say, or by redesigning the window configuration), you sever the incoming causal connections to the Daylight variable and propagate only the outgoing effects. Pearl's do-calculus formalises this distinction — it specifies the conditions under which observational data can be used to estimate interventional effects, and it provides the mathematical machinery for computing those effects in the presence of known confounders.

The web's compositional reasoning along mechanism chains *implicitly* assumes intervention: each step says "if this input is present, this output follows," which is an interventional claim. But the web does not rigorously handle the cases where the "input" covaries with other causes of the "output" — confounding, selection bias, and the general problem of separating causation from association in observational data. For this, you need the BN's formal causal inference machinery.

Consider a concrete example that matters for architectural practice. Buildings with high ceilings tend to be newer, more expensive, better maintained, and occupied by higher-income people who have access to more creative-supporting resources. If an observational study finds that high-ceiling buildings have more creative occupants, the web's mechanism chain (ceiling height → spatial volume → prediction error → explore-mode shift → creative cognition) provides one explanation. But the confounded association (ceiling height → building quality → occupant demographics → creativity resources) provides another. The web knows about the mechanism chain but cannot compute the *interventional* effect of ceiling height while controlling for the confounders. The BN can, because it represents the confounders explicitly and uses do-calculus to separate the causal effect from the confounded association.

**Second: Counterfactual reasoning.** "Given that we observed low mood in this building, *would* mood have been positive if daylight had been high?" This question combines actual observation (conditioning on what happened) with hypothetical intervention (imagining what would have happened under different conditions). Counterfactual reasoning requires a formal causal model that can compute probabilities in hypothetical worlds — worlds that did not happen but might have. The BN provides this capacity through its structural equations and the three-step counterfactual inference procedure (Pearl, 2009, Chapter 7): (1) condition on the actual evidence (abduction), (2) intervene on the hypothetical variable (action), (3) compute the counterfactual probability (prediction).

The web's qualitative reasoning about mechanisms cannot replicate this. The web can say "yes, probably, the affect-broadening pathway would have been more strongly activated if daylight had been higher." But it cannot compute the counterfactual probability rigorously, because it does not have the structural equations that formalize the functional relationships between variables, and it does not have the abduction step that conditions on what was actually observed.

### 126.3 The Asymmetric Relationship, Summarised

The relationship between web and BN is therefore **asymmetric but genuinely bidirectional**:

**From web to BN**: The web provides structure (which variables exist, which edges connect them), parameters (CPTs derived from calibrated templates via the CPT elicitation protocol), boundary conditions (where the BN's computations are valid), and revision signals (when the web updates, the BN is regenerated).

**From BN to web**: The BN provides interventional predictions (do-calculus: "if I do X, what happens, controlling for confounders?"), counterfactual analysis ("would Y have occurred if X had been different?"), and empirical feedback (predictions tested against real-world observations, with discrepancies feeding back to the web for diagnosis).

The arrows that flow from web to BN carry *structure, parameters, and meaning*. The arrows that flow from BN to web carry *causal logic and empirical accountability*. The web is epistemically primary — it can reason about mechanisms, coherence, evidence, and theory on its own, and it can compute quantitative consequences through compositional chain propagation. The BN provides the two things the web cannot do for itself: rigorous interventional inference (separating causation from association in the presence of confounders) and counterfactual reasoning (computing what would have happened under alternative conditions).

These are not minor contributions — they are precisely what makes the ATLAS system useful for architectural practice, where the fundamental question is always "if I change the design, what will happen?" The web tells you *why* high ceilings facilitate creative cognition and *how much*. The BN tells you what will happen if you *intervene* to raise the ceiling, controlling for everything else that covaries with ceiling height. The web tells you what would change your mind. The BN tells you what would have happened in a world you did not build.

### 126.3A Implementation Status: BN↔EN Bidirectional Propagation (March 2, 2026)

The architecture described in §126.3 is correct as a specification, but as of March 2026 the bidirectional propagation is **not implemented** in code. The current state:

- **EN → BN (partial)**: The EN provides structure to the BN through token-overlap matching (`bn_touch()` in `compute_system_health.py`), achieving 95.9% coverage as of Session 21. However, EN belief entrenchment changes do not automatically regenerate BN conditional probability distributions. The BN CPDs are static snapshots created during initial calibration.

- **BN → EN (not implemented)**: BN posteriors (e.g., P(outcome | features) = 0.78 from Bayesian inference) do not currently feed back to update linked belief entrenchment or credence values in the EN. This means the system cannot yet close the loop described in §126.3: empirical feedback from BN predictions tested against real-world observations does not propagate back to the web for diagnosis.

This gap is identified as major future work (P1 priority). The target architecture: when the BN computes an interventional posterior that diverges significantly (> 0.15) from the EN's credence for the corresponding belief, this triggers a reconciliation process — either the BN's structural assumptions need revision (missing confounder, incorrect edge direction) or the EN's credence is based on insufficient evidence and should be updated toward the BN posterior. The reconciliation protocol is not yet designed.

### 126.4 Consequences for §85 Revision

The current §85 in the master document treats the BN-Web relationship as bidirectionally constraining with roughly symmetric contributions. This should be revised to reflect the asymmetric architecture described above. Specifically:

1. The flow diagram in §85 should show the web as the larger, primary structure with the BN as a derived projection — not as two boxes of equal size with symmetric arrows.

2. The text in §85 that describes the BN as providing "quantitative prediction" should be revised: the BN provides *causal inference* (interventional and counterfactual), not quantitative prediction per se. The web can compute quantitative predictions on its own through compositional chain propagation.

3. The §85 discussion of the BN's "self-healing" property should be sharpened: the BN does not self-heal. It is regenerated by the web whenever the web revises. The appearance of self-healing is a consequence of the web's structural revision capacity (Algorithm 4 in §129), not any property of the BN itself.

### 126.5 References for §126

Berridge, K. C., & Robinson, T. E. (1998). What is the role of dopamine in reward: Hedonic impact, reward learning, or incentive salience? *Brain Research Reviews*, 28(3), 309–369. https://doi.org/10.1016/S0165-0173(98)00019-8 [Google Scholar citations: ~5,500]

Pearl, J. (2009). *Causality: Models, reasoning, and inference* (2nd ed.). Cambridge University Press. https://doi.org/10.1017/CBO9780511803161 [Google Scholar citations: ~28,000]

Spirtes, P., Glymour, C., & Scheines, R. (2000). *Causation, prediction, and search* (2nd ed.). MIT Press. [Google Scholar citations: ~7,800]

---

## §127: Reflective Equilibrium as a Formal Operation

### 127.1 The Concept and Its History

Reflective equilibrium is the deepest kind of reasoning the Web of Belief supports, and it has no counterpart in the Bayesian Network. The concept originates with Nelson Goodman's (1955) analysis of inductive inference in *Fact, Fiction, and Forecast*. Goodman argued that our rules of inductive inference and our particular inductive judgments are justified *together*: a rule is justified when it codifies accepted practice, and a practice is justified when it follows from an accepted rule. When they conflict, we adjust both — the rule and the practice — until they cohere. Neither has epistemic priority.

John Rawls (1971) imported this idea into moral and political philosophy in *A Theory of Justice*, where reflective equilibrium describes the process of mutual adjustment between general principles of justice and particular moral intuitions. You start with some principles (e.g., "the most disadvantaged members of society should be made as well off as possible") and some particular judgments (e.g., "slavery is unjust even if it maximises average utility"). When principles and judgments conflict, you adjust both until they reach a stable, mutually supporting configuration. The resulting equilibrium is "reflective" because it involves conscious deliberation about the fit between general and particular beliefs, not merely passive absorption of evidence.

The philosophical literature on reflective equilibrium is substantial and contains several important distinctions. Daniels (1979) distinguished *narrow* reflective equilibrium (adjusting only principles and particular judgments) from *wide* reflective equilibrium (also adjusting background theories about moral psychology, social institutions, and the nature of persons). The ATLAS's practice corresponds to wide reflective equilibrium: the panels adjust not only the template parameters (particular judgments) and the working models (principles) but also the T1 framework assignments, the bridge warrant hierarchy, and the cross-cutting axioms (background theories).

### 127.2 The ATLAS system Panel Process as Reflective Equilibrium

The ATLAS system panel process is, in essence, a structured method for achieving reflective equilibrium. The correspondence between the philosophical concept and the panel procedure is precise:

**The Round Table phase presents general principles.** Each simulated expert articulates a T1 framework — a general theory of how some aspect of cognition relates to the environment. Barrett's constructionist theory of emotion, Craig's labelled-line theory of interoception, Berridge's incentive salience theory, Dayan's neuromodulatory uncertainty theory — these are the "principles" that will be tested against particular findings.

**The Crucible phase tests principles against particular findings and competing accounts.** The Crucible confronts each theory with evidence that supports it, challenges it, or supports a rival. The Barrett-Craig debate in THERMAL-I was a paradigmatic Crucible: Barrett's constructionism predicted that interoceptive processing is context-dependent and constructed; Craig's labelled-line theory predicted that it is modality-specific and direct. The evidence (posterior insula shows modality-specific responses, anterior insula shows constructionist processing) was inconsistent with either theory in its pure form.

**The Calibration phase adjusts both principles and particular findings until they cohere.** In the Barrett-Craig case, the general principles were adjusted: neither pure constructionism nor pure labelled-line theory survived intact. The particular findings were reinterpreted: the posterior/anterior dissociation was understood not as evidence for one theory over the other but as evidence for a two-stage model in which the first stage is modality-specific (Craig) and the second stage is constructionist (Barrett). The result — the Barrett-Craig two-stage model — is a reflective equilibrium outcome. Both the principles and the interpretation of the evidence were adjusted until they cohered.

This is not an isolated example. The differential-mode model (low stimulation → divergent/exploratory processing; moderate stimulation → convergent/exploitative processing) is another reflective equilibrium product: the general principle (there is an optimal stimulation level for cognition) was refined by particular findings from both CREATIVE-I (cognitive psychology perspective) and NEUROMOD-I (computational neuroscience perspective), and the principle was adjusted to include a mode distinction that neither tradition had fully articulated before the panel process brought them into contact.

### 127.3 Why the BN Cannot Achieve Reflective Equilibrium

A Bayesian Network cannot achieve reflective equilibrium because it has no principles — only parameters. It has conditional probability tables, which are numbers, not theories. You cannot adjust a CPT entry in response to a theoretical consideration, because the CPT does not know what theory it is expressing. The entry P(Mood = positive | Daylight = high) = 0.70 is a number; it carries no memory of the serotonergic pathway, no awareness of the Barrett-Craig model, no knowledge of the competing circadian account.

The BN's parameters are revised by Bayes' rule in response to evidence. This is a different epistemic operation from reflective equilibrium. Bayesian updating adjusts beliefs in response to *evidence*: when new data arrives, the posterior is updated via the likelihood function. Reflective equilibrium adjusts beliefs in response to *coherence with other beliefs*: when a principle conflicts with a particular judgment, both are adjusted to restore mutual support. The two processes have different inputs (evidence vs. inter-belief coherence), different operations (likelihood weighting vs. mutual adjustment), and different products (updated posteriors vs. a coherent belief system).

It is worth being precise about this, because Bayesian epistemologists have sometimes argued that Bayesian updating subsumes reflective equilibrium — that the process of adjusting prior probabilities in response to evidence is all the "equilibrium" one needs (see Bovens & Hartmann, 2003, for a sophisticated version of this argument). The ATLAS's experience suggests otherwise. The Barrett-Craig compromise was not the result of updating a prior distribution over theories in response to evidence. It was the result of *reconceptualising* the theoretical landscape: creating a new theory (the two-stage model) that neither tradition had articulated, and that emerged only from the confrontation between them. Bayesian updating operates within a fixed hypothesis space; reflective equilibrium can *expand* the hypothesis space by generating new theories that accommodate previously incompatible evidence. Algorithm 4 (Structural Revision, §129) formalises this distinction: parametric revision (updating numbers) is Bayesian; structural revision (adding nodes, changing edges, creating new theories) is reflective equilibrium.

### 127.4 Formal Properties of Reflective Equilibrium in ATLAS

Several formal properties of reflective equilibrium, as instantiated in the ATLAS system panel process, deserve articulation:

**Non-monotonicity.** Reflective equilibrium is non-monotonic: adding new evidence can *decrease* confidence in a belief that was previously well-supported. When NEUROMOD-I introduced the 5-HT pathway evidence, it both supported NM7 (Serotonergic Mood) and created a new vulnerability — the Lambert et al. (2002) single-study dependency. The web's confidence in the serotonergic account of daylight-mood effects may have *decreased* even as the web's total knowledge *increased*, because the new knowledge revealed a previously unrecognised fragility. This is a standard property of reflective equilibrium (Elgin, 1996) and a standard failure mode for naive coherentism that the ATLAS's constraint system is designed to handle.

**Path dependence (open question).** Would the Barrett-Craig compromise have emerged if CREATIVE-I had been run before THERMAL-I? Would AX4 have been elevated at the same threshold if STRESS-I had come after NEUROMOD-I rather than before? These are questions about the path dependence of the reflective equilibrium process, and they connect to Frontier 1 (§131) — the temporal dynamics of the web. The answer has philosophical implications: if the equilibrium is path-dependent, then the order of panels constitutes an epistemologically significant design decision that must be justified. If it is path-independent (i.e., any ordering converges to the same equilibrium), then the process is more robust than it might appear.

**Stability.** A reflective equilibrium is *stable* when small perturbations (new evidence, new competing accounts) do not produce large changes in the equilibrium state. The ATLAS system web appears to have achieved a relatively stable equilibrium after 11 panels: the major theoretical commitments (T1 frameworks, working models, cross-cutting axioms) have been revised only incrementally since approximately SOCIAL-I. This stability is a positive indicator, but it must be distinguished from *rigidity* — a system that never revises is not in equilibrium; it is stuck. The CROSSCUT-I panel will serve as a test of this distinction: it introduces genuinely new theoretical material (awe, neurodiversity, ecological rationality) that should perturb the equilibrium. If the web can accommodate this material through modest adjustments (the hallmark of stability), the equilibrium is genuine. If CROSSCUT-I requires wholesale restructuring, the apparent stability was illusory.

### 127.5 References for §127

Bovens, L., & Hartmann, S. (2003). *Bayesian epistemology*. Oxford University Press. https://doi.org/10.1093/0199269750.001.0001 [Google Scholar citations: ~1,600]

Daniels, N. (1979). Wide reflective equilibrium and theory acceptance in ethics. *Journal of Philosophy*, 76(5), 256–282. https://doi.org/10.2307/2025881 [Google Scholar citations: ~1,400]

Elgin, C. Z. (1996). *Considered judgment*. Princeton University Press. [Google Scholar citations: ~700]

Goodman, N. (1955). *Fact, fiction, and forecast*. Harvard University Press. [Google Scholar citations: ~7,500]

Rawls, J. (1971). *A theory of justice*. Harvard University Press. [Google Scholar citations: ~65,000]

---

