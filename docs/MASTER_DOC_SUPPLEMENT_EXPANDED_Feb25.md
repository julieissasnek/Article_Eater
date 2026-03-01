# MASTER_DOC SUPPLEMENT — EXPANDED EDITION
## February 25, 2026 | Session 10 | CMR Project

---

## About This Document

This supplement contains new intellectual content from the February 23–25, 2026 Opus/Chat sessions that should be integrated into MASTER_DOC_CMR. It supersedes the preliminary supplement (MASTER_DOC_SUPPLEMENT_Feb25.md, 465 lines) with a fully expanded treatment of all new material.

The primary source is **WEB_OF_BELIEF_AND_BAYESIAN_NETWORK_ARCHITECTURE.md** (108K, 2,084 lines), the project's most significant architectural philosophy document to date. Secondary sources include the FOUNDATIONS-I panel specification, the NEUROMOD-I Opus review, and the CROSSCUT-I pre-panel clearance review.

**Integration instructions**: The material falls into three categories.

**Category A — New sections (§125–131).** These contain original analysis with no existing counterpart in the master document. They constitute a proposed **Part XIV: Architectural Philosophy — The Web of Belief and Bayesian Network Relationship** and **Part XV: Meta-Epistemological Foundations**. Each section specifies an insertion target. The prose is written at full MASTER_DOC density and can be inserted without further editing.

**Category B — Deepening of existing sections.** These refine or extend material already in §36–39, §49, §56, §70, §71, §85–88. They should be merged into those sections at the specified insertion points rather than duplicated.

**Category C — Technical appendices and the Cowork New-Files Alert Specification.** These contain pseudocode, formal specifications, testing protocols, and a working specification for automated integration monitoring. Appendix material should be placed at the end of the relevant Part or in a dedicated Appendices section.

**Priority order for integration**:

1. §125–126 (epistemic-aleatory distinction + narrowed BN role) — these sharpen the existing §49 and §85 significantly
2. §128 (FOUNDATIONS-I specification) — entirely new intellectual content
3. §129 (six algorithms with pseudocode) — makes §128 operational
4. §130 (testing protocol) — makes §129 testable
5. §127 (reflective equilibrium formalized) — philosophical deepening of §49
6. §131 (three frontiers) — research directions
7. Category B updates to §49, §70, §85, §56 — corrections and additions

---

# CATEGORY A: NEW SECTIONS

---

# PART XIV: ARCHITECTURAL PHILOSOPHY — THE WEB-BN RELATIONSHIP (§125–127)

*This Part deepens the foundational analysis of the Web of Belief and Bayesian Network relationship first introduced in Part II (§36–39) and Part IV (§48–53). Where those earlier sections established the operational framework, this Part provides the philosophical architecture: the distinction between the two kinds of probability the system tracks, the precise delimitation of what the BN uniquely contributes, and the formalization of reflective equilibrium as the web's deepest epistemic operation. The material here draws on the tradition from Quine and Ullian (1970) through Thagard (1989, 2000) and Pearl (2009), and connects that tradition to the specific computational structures the CMR has built.*

---

## §125: The Epistemic-Aleatory Distinction and Its Architectural Consequences

**Insert after**: §88 (Mechanism Chain Traversal) or as Part XIV opener  
**Source**: WEB_OF_BELIEF_AND_BAYESIAN_NETWORK_ARCHITECTURE.md, Part IV §14, Part III §§9–10

---

### 125.1 Two Kinds of Probability

Suppose you roll a fair die. You do not know what number will come up, and this ignorance is not a defect of your understanding — it is a feature of the die. The outcome is genuinely random. No amount of additional information about the die, the table, or your throwing technique (short of a complete Laplacian specification of every molecule) will eliminate this uncertainty. This is *aleatory uncertainty* — from *alea*, the Latin word for die. It describes the inherent stochasticity of a process.

Now suppose someone hands you a die and asks you whether it is fair. You examine it, roll it twenty times, get an unusual distribution of outcomes, and form a tentative judgment: "I believe with about 70% confidence that this die is biased." That 70% does not describe anything about the die's randomness. It describes your state of knowledge about the die. If you rolled it another thousand times, or cut it open and examined its weight distribution, your confidence would change — perhaps to 95% or perhaps to 20%. The die itself has not changed. What changed is what you know. This is *epistemic uncertainty* — from *episteme*, the Greek word for knowledge.

The distinction matters because the two kinds of uncertainty respond to entirely different interventions. Aleatory uncertainty is reduced by changing the process (engineering a more predictable system) or by averaging over many instances (the law of large numbers). Epistemic uncertainty is reduced by learning — by gathering evidence, refining theories, improving measurements, or simply thinking harder about what the existing evidence implies. Conflating the two leads to one of two errors: treating a knowledge gap as if it were inherent randomness (and therefore giving up on reducing it), or treating genuine randomness as if it were a knowledge gap (and therefore wasting effort trying to eliminate it).

In science, the distinction runs deep. When a meta-analysis reports that the effect of daylight on mood is *d* = 0.38 with a 95% confidence interval of [0.22, 0.54], two different kinds of uncertainty are tangled together. Part of the spread reflects genuine variation across people, settings, and measurement occasions — aleatory uncertainty in the population. Part reflects our imperfect knowledge of the true effect size — epistemic uncertainty due to finite samples, heterogeneous study designs, and possible publication bias. Separating these two components is not merely a philosophical nicety; it determines what you do next. If the spread is mostly aleatory (people genuinely differ in their response to daylight), then no amount of additional research will narrow it — you need to design for individual variation. If the spread is mostly epistemic (we just don't have enough good studies yet), then a well-designed replication will narrow it, and you should invest in that replication.

The Bayesian tradition in statistics has struggled with this distinction since at least de Finetti (1937), who argued that all probability is epistemic — a subjective degree of belief — and that aleatory probability is a fiction we impose on processes we do not fully understand. The frequentist tradition takes the opposite view: probability is a property of repeatable processes, and subjective degrees of belief are not probabilities at all. The modern consensus, articulated most clearly by Hacking (1975) and elaborated by Spohn (2012), is that both kinds are real, they serve different roles, and a mature probabilistic framework must track them separately.

In computational modelling, this separation has practical architectural consequences. A Bayesian network whose conditional probability tables contain aleatory probabilities (population frequencies) does something different from a system whose confidence scores contain epistemic probabilities (how certain we are that the model is correctly specified). The first system computes what will probably happen if you intervene. The second system computes how much you should trust the first system's answer. Mixing the two in a single numerical representation is a category error — like adding a distance and a temperature because both happen to be numbers.

### 125.1a The Distinction in the CMR Architecture

The CMR system tracks both kinds of probability in architecturally distinct data structures. The failure to distinguish them is one of the most common sources of confusion in applied neuroscience, and the distinction maps directly onto the division of labour between the Web of Belief and the Bayesian Network.

**Aleatory probability** is what the Bayesian Network computes. The BN's conditional probability tables (CPTs) aspire to contain aleatory probabilities: P(Mood = positive | Daylight = high) = 0.70 is meant as a statement about population frequencies, not about the scientific community's confidence in a theory.

**Epistemic probability** is what the Web of Belief tracks. The web's confidence scores — the numbers that populate every template's calibration — are epistemic probabilities. They encode the scientific community's current best judgment about how much to trust each claim.

What is distinctive about the CMR is the claim that a working computational system should maintain both kinds simultaneously, in different data structures, with explicit translation protocols between them. That is the CMR's architectural commitment, and it has consequences.

### 125.2 Bridge Warrant Types as Categorisations of Epistemic Uncertainty

The bridge warrant types — CONSTITUTIVE, MECHANISM, EMPIRICAL_COVARIANCE, FUNCTIONAL, CAPACITY, ANALOGICAL, and THEORETICAL_DEFAULT — are not merely labels. They are *categorisations of epistemic uncertainty*. They tell you not just how confident the community is in a claim, but *why* the confidence is at its current level and, crucially, *what kind of evidence would change it*.

Consider two claims that happen to have the same numerical confidence of 0.35:

A MECHANISM bridge at 0.35 says: "The causal pathway from environmental feature to neural mechanism to outcome is well-characterised in laboratory conditions, but the architectural instantiation is uncertain. We know that the daylight → retinal stimulation → raphe nuclei → tryptophan hydroxylase → 5-HT synthesis chain operates in principle; we are uncertain whether it operates at sufficient magnitude in real buildings with real occupants over real time scales." The research that would raise this confidence is measurement of the mechanism *in architectural conditions* — ambulatory neurochemical monitoring, or at least measurement of the relevant behavioural outcomes in buildings with known daylight parameters.

An ANALOGICAL bridge at 0.35 says: "We are reasoning from a parallel case. The drug-related incentive sensitisation model (Berridge & Robinson, 1998) is structurally analogous to architectural place attachment, but the analogy may not hold. The neural substrate (mesolimbic DA) is shared, but the temporal dynamics, the stimulus parameters, and the phenomenological character of the experience may differ in ways that break the analogy." The research that would raise this confidence is fundamentally different: it requires establishing that the analogy *actually holds* — that the same mechanism operates in both domains, not merely that the two domains look similar from a distance.

These two claims carry completely different implications for research planning, for confidence in predictions, and for the appropriate caution when advising architectural practitioners. The warrant type captures information that a bare number cannot. This is why the web preserves warrant types as first-class annotations, and why the projection from web to BN is necessarily lossy: the BN receives a number (the CPT entry); the web retains the epistemological reasoning behind the number.

### 125.3 The Practical Import: Different Uncertainties Require Different Interventions

The distinction between epistemic and aleatory probability matters practically because the two kinds of probability respond to different interventions.

**Aleatory uncertainty is reduced by collecting more data from the same process.** If you want to narrow the confidence interval on P(Mood = positive | Daylight = high), you measure more occupants in more buildings. The population frequency becomes better estimated as the sample grows. This is the domain of classical statistics — larger N, tighter confidence intervals, more precise effect sizes.

**Epistemic uncertainty is reduced by improving the theoretical model.** If you want to increase confidence that the daylight → 5-HT → mood pathway is correctly specified, you do not (primarily) measure more occupants. You specify the mechanism more precisely. You resolve the competing account (circadian entrainment rather than direct serotonergic modulation). You replicate the Lambert et al. (2002) study with better methodology. You upgrade the bridge warrant from EMPIRICAL_COVARIANCE to MECHANISM by tracing the pathway in an architectural context. These are qualitatively different research activities.

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
| EMPIRICAL_COVARIANCE | 0.70 |
| FUNCTIONAL | 0.60 |
| CAPACITY | 0.55 |
| ANALOGICAL | 0.45 |
| THEORETICAL_DEFAULT | 0.50 |

These factors are themselves epistemic judgments, and they should be treated as calibratable parameters of the projection function. The retrodiction test (§130, Level 2) provides an opportunity to calibrate them empirically.

**Step 3 — Qualifier narrowing.** Apply domain-specific conditions from the template's qualifier field. If the qualifier states "effect strongest for morning light in buildings with high spatial complexity," the CPT entry should be conditioned on these variables (or alternatively, the BN should include these as moderator nodes).

**Step 4 — Rebuttal-derived uncertainty bands.** The rebuttal field specifies conditions under which the claim fails. These translate into the width of the uncertainty band around the CPT entry. A template with a strong rebuttal ("mechanism may not apply in naturally ventilated buildings because thermal comfort co-varies with daylight in these settings") has wider uncertainty bands than one with a weak rebuttal.

**Step 5 — Competing-account adjustment.** If the template has an unresolved competing account, the CPT entry should reflect the ambiguity. In the strongest case, the CPT entry is computed as a weighted average of the two accounts' implied values, with weights proportional to their respective credences.

This protocol should be formalised and applied retroactively to the entire calibrated corpus after CROSSCUT-I completes. The resulting CPTs will be the first numerically grounded aleatory probabilities in the CMR system, and they will carry explicit provenance — each entry will record the epistemic reasoning (steps 1–5) from which it was derived. This provenance is lost in the BN itself (which sees only numbers), but it is preserved in the web (which retains the full Toulmin structure). This asymmetry is by design: the BN is a computationally tractable snapshot of the web's current epistemic state, regenerated whenever the web revises.

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

**Insert after**: §125, or merge into §85  
**Source**: WEB_OF_BELIEF_AND_BAYESIAN_NETWORK_ARCHITECTURE.md, Part III §§9–10, Part IV §§11–12

---

### 126.1 The Web's Surprising Self-Sufficiency

One of the most important revisions to the CMR's architectural self-understanding, achieved in the February 25 session, concerns the scope of what the web can accomplish on its own. The earlier understanding (reflected in §85 and §49 of the master document) treated the Web of Belief and the Bayesian Network as roughly symmetrical partners: the web provided qualitative reasoning and the BN provided quantitative reasoning, each contributing what the other lacked. This picture is wrong in a consequential way.

The web can compute quantitative consequences *through its own mechanism chains* by compositional reasoning. When the web encodes a mechanism chain such as:

> daylight increases 5-HT synthesis (d = 0.38) → 5-HT moderates the wanting-liking balance (d = 0.45) → wanting drives approach motivation (d = 0.55)

the web can propagate these effect sizes compositionally along the chain to derive the expected compound effect. Each step in the chain carries a numerical parameter (the effect size from the Toulmin data), a bridge warrant type (governing the attenuation of confidence across the inferential step), and qualifier conditions (specifying where the step applies). The web can multiply these along the chain, apply the appropriate bridge warrant discounts, and produce a numerical estimate of the downstream effect. It does not need the BN for this.

This is not a minor point. It means that the compositional quantitative reasoning the CMR performs when tracing a mechanism chain from environmental feature through neural mechanism to occupant outcome — the central operation described in Part I's 30 worked examples — is a *web* operation, not a BN operation. The web is where mechanism chains live, where their parameters are calibrated, and where the compositional multiplication is performed. The BN enters the picture only when the question shifts from "what does our theory predict?" to "what happens if we intervene, controlling for confounders?"

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

These are not minor contributions — they are precisely what makes the CMR useful for architectural practice, where the fundamental question is always "if I change the design, what will happen?" The web tells you *why* high ceilings facilitate creative cognition and *how much*. The BN tells you what will happen if you *intervene* to raise the ceiling, controlling for everything else that covaries with ceiling height. The web tells you what would change your mind. The BN tells you what would have happened in a world you did not build.

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

**Insert after**: §126, or merge into §49.4  
**Source**: WEB_OF_BELIEF_AND_BAYESIAN_NETWORK_ARCHITECTURE.md, Part I §4.2, Part IV §13

---

### 127.1 The Concept and Its History

Reflective equilibrium is the deepest kind of reasoning the Web of Belief supports, and it has no counterpart in the Bayesian Network. The concept originates with Nelson Goodman's (1955) analysis of inductive inference in *Fact, Fiction, and Forecast*. Goodman argued that our rules of inductive inference and our particular inductive judgments are justified *together*: a rule is justified when it codifies accepted practice, and a practice is justified when it follows from an accepted rule. When they conflict, we adjust both — the rule and the practice — until they cohere. Neither has epistemic priority.

John Rawls (1971) imported this idea into moral and political philosophy in *A Theory of Justice*, where reflective equilibrium describes the process of mutual adjustment between general principles of justice and particular moral intuitions. You start with some principles (e.g., "the most disadvantaged members of society should be made as well off as possible") and some particular judgments (e.g., "slavery is unjust even if it maximises average utility"). When principles and judgments conflict, you adjust both until they reach a stable, mutually supporting configuration. The resulting equilibrium is "reflective" because it involves conscious deliberation about the fit between general and particular beliefs, not merely passive absorption of evidence.

The philosophical literature on reflective equilibrium is substantial and contains several important distinctions. Daniels (1979) distinguished *narrow* reflective equilibrium (adjusting only principles and particular judgments) from *wide* reflective equilibrium (also adjusting background theories about moral psychology, social institutions, and the nature of persons). The CMR's practice corresponds to wide reflective equilibrium: the panels adjust not only the template parameters (particular judgments) and the working models (principles) but also the T1 framework assignments, the bridge warrant hierarchy, and the cross-cutting axioms (background theories).

### 127.2 The CMR Panel Process as Reflective Equilibrium

The CMR panel process is, in essence, a structured method for achieving reflective equilibrium. The correspondence between the philosophical concept and the panel procedure is precise:

**The Round Table phase presents general principles.** Each simulated expert articulates a T1 framework — a general theory of how some aspect of cognition relates to the environment. Barrett's constructionist theory of emotion, Craig's labelled-line theory of interoception, Berridge's incentive salience theory, Dayan's neuromodulatory uncertainty theory — these are the "principles" that will be tested against particular findings.

**The Crucible phase tests principles against particular findings and competing accounts.** The Crucible confronts each theory with evidence that supports it, challenges it, or supports a rival. The Barrett-Craig debate in THERMAL-I was a paradigmatic Crucible: Barrett's constructionism predicted that interoceptive processing is context-dependent and constructed; Craig's labelled-line theory predicted that it is modality-specific and direct. The evidence (posterior insula shows modality-specific responses, anterior insula shows constructionist processing) was inconsistent with either theory in its pure form.

**The Calibration phase adjusts both principles and particular findings until they cohere.** In the Barrett-Craig case, the general principles were adjusted: neither pure constructionism nor pure labelled-line theory survived intact. The particular findings were reinterpreted: the posterior/anterior dissociation was understood not as evidence for one theory over the other but as evidence for a two-stage model in which the first stage is modality-specific (Craig) and the second stage is constructionist (Barrett). The result — the Barrett-Craig two-stage model — is a reflective equilibrium outcome. Both the principles and the interpretation of the evidence were adjusted until they cohered.

This is not an isolated example. The differential-mode model (low stimulation → divergent/exploratory processing; moderate stimulation → convergent/exploitative processing) is another reflective equilibrium product: the general principle (there is an optimal stimulation level for cognition) was refined by particular findings from both CREATIVE-I (cognitive psychology perspective) and NEUROMOD-I (computational neuroscience perspective), and the principle was adjusted to include a mode distinction that neither tradition had fully articulated before the panel process brought them into contact.

### 127.3 Why the BN Cannot Achieve Reflective Equilibrium

A Bayesian Network cannot achieve reflective equilibrium because it has no principles — only parameters. It has conditional probability tables, which are numbers, not theories. You cannot adjust a CPT entry in response to a theoretical consideration, because the CPT does not know what theory it is expressing. The entry P(Mood = positive | Daylight = high) = 0.70 is a number; it carries no memory of the serotonergic pathway, no awareness of the Barrett-Craig model, no knowledge of the competing circadian account.

The BN's parameters are revised by Bayes' rule in response to evidence. This is a different epistemic operation from reflective equilibrium. Bayesian updating adjusts beliefs in response to *evidence*: when new data arrives, the posterior is updated via the likelihood function. Reflective equilibrium adjusts beliefs in response to *coherence with other beliefs*: when a principle conflicts with a particular judgment, both are adjusted to restore mutual support. The two processes have different inputs (evidence vs. inter-belief coherence), different operations (likelihood weighting vs. mutual adjustment), and different products (updated posteriors vs. a coherent belief system).

It is worth being precise about this, because Bayesian epistemologists have sometimes argued that Bayesian updating subsumes reflective equilibrium — that the process of adjusting prior probabilities in response to evidence is all the "equilibrium" one needs (see Bovens & Hartmann, 2003, for a sophisticated version of this argument). The CMR's experience suggests otherwise. The Barrett-Craig compromise was not the result of updating a prior distribution over theories in response to evidence. It was the result of *reconceptualising* the theoretical landscape: creating a new theory (the two-stage model) that neither tradition had articulated, and that emerged only from the confrontation between them. Bayesian updating operates within a fixed hypothesis space; reflective equilibrium can *expand* the hypothesis space by generating new theories that accommodate previously incompatible evidence. Algorithm 4 (Structural Revision, §129) formalises this distinction: parametric revision (updating numbers) is Bayesian; structural revision (adding nodes, changing edges, creating new theories) is reflective equilibrium.

### 127.4 Formal Properties of Reflective Equilibrium in the CMR

Several formal properties of reflective equilibrium, as instantiated in the CMR panel process, deserve articulation:

**Non-monotonicity.** Reflective equilibrium is non-monotonic: adding new evidence can *decrease* confidence in a belief that was previously well-supported. When NEUROMOD-I introduced the 5-HT pathway evidence, it both supported NM7 (Serotonergic Mood) and created a new vulnerability — the Lambert et al. (2002) single-study dependency. The web's confidence in the serotonergic account of daylight-mood effects may have *decreased* even as the web's total knowledge *increased*, because the new knowledge revealed a previously unrecognised fragility. This is a standard property of reflective equilibrium (Elgin, 1996) and a standard failure mode for naive coherentism that the CMR's constraint system is designed to handle.

**Path dependence (open question).** Would the Barrett-Craig compromise have emerged if CREATIVE-I had been run before THERMAL-I? Would AX4 have been elevated at the same threshold if STRESS-I had come after NEUROMOD-I rather than before? These are questions about the path dependence of the reflective equilibrium process, and they connect to Frontier 1 (§131) — the temporal dynamics of the web. The answer has philosophical implications: if the equilibrium is path-dependent, then the order of panels constitutes an epistemologically significant design decision that must be justified. If it is path-independent (i.e., any ordering converges to the same equilibrium), then the process is more robust than it might appear.

**Stability.** A reflective equilibrium is *stable* when small perturbations (new evidence, new competing accounts) do not produce large changes in the equilibrium state. The CMR web appears to have achieved a relatively stable equilibrium after 11 panels: the major theoretical commitments (T1 frameworks, working models, cross-cutting axioms) have been revised only incrementally since approximately SOCIAL-I. This stability is a positive indicator, but it must be distinguished from *rigidity* — a system that never revises is not in equilibrium; it is stuck. The CROSSCUT-I panel will serve as a test of this distinction: it introduces genuinely new theoretical material (awe, neurodiversity, ecological rationality) that should perturb the equilibrium. If the web can accommodate this material through modest adjustments (the hallmark of stability), the equilibrium is genuine. If CROSSCUT-I requires wholesale restructuring, the apparent stability was illusory.

### 127.5 References for §127

Bovens, L., & Hartmann, S. (2003). *Bayesian epistemology*. Oxford University Press. https://doi.org/10.1093/0199269750.001.0001 [Google Scholar citations: ~1,600]

Daniels, N. (1979). Wide reflective equilibrium and theory acceptance in ethics. *Journal of Philosophy*, 76(5), 256–282. https://doi.org/10.2307/2025881 [Google Scholar citations: ~1,400]

Elgin, C. Z. (1996). *Considered judgment*. Princeton University Press. [Google Scholar citations: ~700]

Goodman, N. (1955). *Fact, fiction, and forecast*. Harvard University Press. [Google Scholar citations: ~7,500]

Rawls, J. (1971). *A theory of justice*. Harvard University Press. [Google Scholar citations: ~65,000]


---

# PART XV: META-EPISTEMOLOGICAL FOUNDATIONS (§128–131)

*This Part addresses the CMR system's capacity for formal reasoning about its own structure. Where Part XIV established the philosophical architecture of the web-BN relationship, this Part specifies the formal inference calculus that makes the web's reasoning explicit and computable: a panel specification for deriving the calculus (§128), the algorithms that implement it (§129), the testing protocol that validates it (§130), and the three research frontiers that extend it (§131). The ambition is substantial: to transform the web from a static repository of calibrated beliefs into a dynamic reasoner that can propagate credences, resolve competitions, measure its own coherence, and identify its own most productive research directions — all with polynomial-time algorithms that execute in milliseconds on the CMR's actual graph.*

---

## §128: FOUNDATIONS-I — Toward a Formal Inference Calculus for the Web

**Insert as**: Part XV opener  
**Source**: PANEL_SPECIFICATION_FOUNDATIONS_I.md, WEB_OF_BELIEF_AND_BAYESIAN_NETWORK_ARCHITECTURE.md Part VI §§17–19

---

### 128.1 The Problem: Informal Reasoning Doesn't Scale

The CMR web has approximately 130 nodes (93 calibrated T2 templates, 10 T1 frameworks, 10 T1.5 domain theories, 8 cross-cutting axioms, 2 working models, and a small number of stub and candidate nodes) connected by approximately 300–400 typed edges (reduction, bridge warrant (7 subtypes), competition, cross-template interaction, inheritance, working model, axiom, and partial-out). It can answer lookup queries ("what is the mechanism chain for ceiling height → creativity?") and compositional queries ("what is the expected compound effect?") through direct traversal of its graph structure.

What it cannot do is reason formally over its own structure. When the system adopts the Barrett-Craig two-stage model, elevates AX4 (Perceived Control) to a formally recognised cross-cutting moderator, or defers Aesthetic Anchoring pending further evaluation, these decisions are informal expert judgments — the product of Crucible debate, calibration adjustment, and David's supervisory approval. They are *good* judgments, supported by extensive evidence and deliberation. But they are not *formally derivable* from explicit rules applied to the web's current state. A formal inference calculus would make them derivable — or, where the calculus disagrees with the informal judgment, would identify the disagreement as a diagnostic signal worth investigating.

The need for formalization has both intellectual and practical motivations. Intellectually, a system that reasons about its own beliefs should be able to articulate the rules by which it reasons. Practically, as the web grows beyond 130 nodes (future domains — air pollution and cognition, psychedelic therapy, urban noise — would add hundreds more), informal reasoning will not scale. A human supervisor can hold the coherence of a 130-node web in mind; a 500-node web exceeds human working memory, and a 1000-node web is beyond any individual's comprehension. The formal calculus is the tool that makes the web manageable at scale.

### 128.2 The Eight Edge Types: An Exhaustive Inventory

The inference calculus must specify rules for every edge type in the web. The CMR uses eight edge types, and this inventory is exhaustive — every connection between any two nodes in the web falls into one of these categories.

**1. REDUCTION (T1 → T1.5 → T2).** A higher-tier belief is explained by a lower-tier mechanism. Prospect-Refuge theory (T1.5) is reduced to Predictive Processing + Default Mode / Place Cells (T1). This means that the credibility of Prospect-Refuge depends on the credibility of PP and DP. The key formal question — on which FOUNDATIONS-I must adjudicate — is the multi-parent rule: when a T1.5 theory reduces to *multiple* T1 frameworks, do the parent credences combine conjunctively (both must be credible), disjunctively (either suffices), or compositionally (the reduction specifies which aspects of each T1 contribute)? The current practice is closest to a noisy-OR combination for complementary parents (each independently supports) and a max operation for overlapping parents (redundant support with no double-counting), but this has not been formally justified.

**2. BRIDGE WARRANT (7 subtypes).** These connect theoretical claims to evidence with a typed inferential bridge. The seven subtypes — CONSTITUTIVE, MECHANISM, EMPIRICAL_COVARIANCE, FUNCTIONAL, CAPACITY, ANALOGICAL, and THEORETICAL_DEFAULT — are defined in §125.2 and in the original master document at §37. The key formal question is whether the bridge warrant hierarchy is *discovered* (an empirical fact about how different kinds of evidence support theoretical claims) or *stipulated* (a methodological convention). The FOUNDATIONS-I panel addresses this directly in Crucible 5.

**3. COMPETITION.** Rival hypotheses for the same evidence. The Barrett-Craig debate is a resolved competition (COMPROMISE via domain partition); the motor-afferent vs. attentional-release accounts of walking-creativity are an unresolved equilibrium. Three outcomes are possible: VICTORY (one account wins decisively), COMPROMISE (both are partially correct, typically via domain partition), and EQUILIBRIUM (the evidence does not discriminate, and both accounts retain credence). The key formal question is whether competition resolution should follow argumentation semantics (Dung, 1995; Prakken, 2010), Bayesian model comparison, or a hybrid approach. Algorithm 2 (§129) proposes a hybrid.

**4. CROSS-TEMPLATE INTERACTION.** Templates that share a mechanism or environmental input. NEUROMOD-I produced 8 cross-template interactions, including the NE-ACh interaction (explore/exploit × precision weighting) and the 5-HT moderation of wanting-liking balance. These edges carry a valence (synergistic, antagonistic, or conditional) and a strength (the magnitude of the interaction effect). The key formal question is whether interaction effects should be computed additively, multiplicatively, or through a more complex compositional function.

**5. INHERITANCE.** Parameter sharing across templates. CREATIVE-I's incubation template inherits DMN re-engagement conditions from MEMORY-I; NEUROMOD-I's threat template inherits HPA parameters from STRESS-I. Inheritance edges prevent double-counting and ensure consistency. The formal property is simple: inherited parameters are identical in all templates that share them, and updating the parameter in any one template updates it everywhere.

**6. WORKING MODEL.** A theoretical commitment constraining multiple templates. Barrett-Craig two-stage interoceptive processing and the differential-mode model are the two adopted working models. A working model sits between T1 and T1.5 in the tier hierarchy: it is not as fundamental as a T1 framework, but it constrains many templates and resists casual revision. Working models carry explicit revision clauses — conditions under which the model should be abandoned or modified.

**7. AX-AXIOM.** A meta-parameter that modifies all templates. AX4 (Perceived Control) is the most prominent example, with a modulation range of [0.6, 1.4] across all templates. AX-axioms are like the constants of nature for the web: they define the background conditions under which all other claims hold. The key formal question is priority: when an AX-axiom and a domain-specific calibration conflict, which prevails?

**8. PARTIAL-OUT.** A scope partition preventing double-counting. When two templates would otherwise claim the same effect independently (e.g., a daylight template and a view template both claiming a restoration effect mediated by the same neural pathway), a partial-out edge restricts each template's scope to its non-overlapping contribution. Partial-out edges carry no credence and no attenuation — they are purely structural, defining boundaries rather than transmitting support.

### 128.3 The FOUNDATIONS-I Expert Panel

The inference calculus will be derived through a FOUNDATIONS-I panel following the same methodology as the domain panels, but with a meta-epistemological rather than domain-specific focus. The panel comprises nine experts, selected to represent the intellectual traditions most relevant to formalising scientific belief revision:

1. **Paul Thagard** (coherence theory) — ECHO model of explanatory coherence, constraint satisfaction approach
2. **Clark Glymour** (theory-evidence bridge) — bootstrapping, theory testing, the PC algorithm for causal discovery
3. **Stephan Hartmann** (Bayesian coherentism) — probabilistic measures of coherence, the relationship between coherence and truth
4. **Peter Gärdenfors** (belief revision) — conceptual spaces, AGM theory of rational belief revision
5. **Henry Prakken** (argumentation) — structured argumentation frameworks, formal models of legal and scientific argument
6. **Kevin Kelly** (formal learning theory) — topological characterization of inductive methods, convergence to truth
7. **Judea Pearl** (causal inference) — Bayesian networks, do-calculus, the structural causal model framework
8. **Erik Olsson** (collective belief) — social epistemology, models of consensus and aggregation
9. **Marcello D'Agostino** (computational tractability) — bounded rationality, efficient inference in graphical models

### 128.4 Five Crucible Debates

The panel will adjudicate five foundational debates, each of which corresponds to an unresolved formal question in the calculus:

**Crucible 1: Credence propagation through reduction chains.** When a T2 template reduces through a T1.5 theory to a T1 framework, how does credence propagate? Conjunctive combination (strict: the weakest link governs), disjunctive combination (lenient: any support suffices), or compositional combination (intermediate: typed attenuation at each step with the specific combination rule depending on whether parents are complementary or overlapping)? The existing CMR practice is closest to compositional, but this is informal.

**Crucible 2: Competition resolution.** When two accounts compete for the same evidence, should the resolution follow argumentation defeat semantics (Dung, 1995; Prakken, 2010), Bayesian model comparison (Jeffreys, 1961), or the reflective equilibrium approach the panels have used informally? Each produces different outcomes for close competitions. Argumentation defeat tends toward binary outcomes (one account is defeated). Bayesian comparison tends toward continuous weighting (both accounts retain credence proportional to their Bayes factors). Reflective equilibrium allows structural innovation (creating a new compromise theory that subsumes both accounts).

**Crucible 3: The coherence metric.** How should overall web coherence be measured? Thagard's (1989) constraint satisfaction approach (maximise the satisfaction of coherence and incoherence constraints), Bovens and Hartmann's (2003) probabilistic measure (coherence as the degree to which evidence confirms a conjunction of hypotheses), or a hybrid that uses typed constraints weighted by edge type?

**Crucible 4: Structural revision.** When new evidence conflicts with the web, how should the web be revised? The AGM theory (Alchourrón, Gärdenfors, & Makinson, 1985) provides a formal framework for rational belief revision with the principle of minimal change. Laudan's (1977) problem-solving model provides an alternative emphasising empirical and conceptual problem-solving capacity. The CMR's entrenchment ordering (T1 beliefs resist revision more than T2 beliefs) has affinities with Gärdenfors' (2000) epistemic entrenchment but has not been formally derived from it.

**Crucible 5: Bridge warrant hierarchy — discovered or stipulated?** Is the ordering CONSTITUTIVE > MECHANISM > EMPIRICAL_COVARIANCE > FUNCTIONAL > CAPACITY > ANALOGICAL > THEORETICAL_DEFAULT an empirical discovery (reflecting an objective fact about how different kinds of evidence support theoretical claims) or a methodological stipulation (a convention that could be replaced by an alternative hierarchy)? This question connects to deep issues in the philosophy of evidence and confirmation theory. If the hierarchy is discovered, it constrains the calculus absolutely. If it is stipulated, it is a parameter of the calculus that can be revised by experience.

### 128.5 Seven Success Conditions

The FOUNDATIONS-I panel succeeds when it delivers:

**S-1**: Formal semantics for every edge type (precise mathematical definition of what each edge type means and how it transmits credence)

**S-2**: Implementable credence propagation rules (given a web state, an algorithm that computes updated credences for all nodes in polynomial time)

**S-3**: A competition resolution protocol (given competing accounts, an algorithm that determines VICTORY, COMPROMISE, or EQUILIBRIUM with explicit thresholds)

**S-4**: A global coherence metric (a computable function from web states to a numerical coherence score, with diagnostic decomposition by edge type and region)

**S-5**: A structural revision protocol (given new evidence that conflicts with the web, an algorithm that determines the minimal revision restoring coherence)

**S-6**: A Value of Information ranking (given the web's current uncertainties, an algorithm that ranks them by their expected impact on coherence)

**S-7**: A BN projection function (given the current web, an algorithm that generates a Bayesian Network with CPTs derived from the web's calibrated parameters)

All seven conditions are addressed by the six algorithms specified in §129.

### 128.6 References for §128

Alchourrón, C. E., Gärdenfors, P., & Makinson, D. (1985). On the logic of theory change: Partial meet contraction and revision functions. *Journal of Symbolic Logic*, 50(2), 510–530. https://doi.org/10.2307/2274239 [Google Scholar citations: ~4,500]

Dung, P. M. (1995). On the acceptability of arguments and its fundamental role in nonmonotonic reasoning, logic programming and n-person games. *Artificial Intelligence*, 77(2), 321–357. https://doi.org/10.1016/0004-3702(94)00041-X [Google Scholar citations: ~7,500]

Gärdenfors, P. (2000). *Conceptual spaces: The geometry of thought*. MIT Press. [Google Scholar citations: ~4,200]

Jeffreys, H. (1961). *Theory of probability* (3rd ed.). Oxford University Press. [Google Scholar citations: ~8,000]

Laudan, L. (1977). *Progress and its problems: Towards a theory of scientific growth*. University of California Press. [Google Scholar citations: ~4,000]

Prakken, H. (2010). An abstract framework for argumentation with structured arguments. *Argument and Computation*, 1(2), 93–124. https://doi.org/10.1080/19462161003734514 [Google Scholar citations: ~800]

---

## §129: Six Algorithms for the Inference Calculus

**Insert after**: §128  
**Source**: WEB_OF_BELIEF_AND_BAYESIAN_NETWORK_ARCHITECTURE.md, Part IX §§29–37

---

### 129.1 Design Principles

Any well-specified formalism must meet two computational requirements. The rules must be **decidable** — there exists an algorithm that produces an answer in finite time for any valid input. And they should be **efficiently computable** — the algorithm runs in time that is practical for the web's actual size. A beautiful calculus that requires exponential time to evaluate a 130-node web is a philosophical contribution, not a working system. These six algorithms are designed to be both decidable and efficient, completing in milliseconds for the CMR's graph.

The web is represented as a directed graph G = (N, E, τ_N, τ_E, θ) where:

- **N** is the set of nodes. |N| ≈ 130 for the complete CMR.
- **E** ⊆ N × N is the set of directed edges. |E| ≈ 300–400.
- **τ_N : N → {T1, T1.5, T2, AX, WM, stub}** is the node type function.
- **τ_E : E → {reduction, bridge(subtype), competition, interaction, inheritance, working_model, ax_axiom, partial_out}** is the edge type function.
- **θ** is the annotation function assigning to each node its credence score c ∈ [0, 1], bridge warrant ceiling w ∈ [0, 1], and Toulmin structure (data, backing, qualifier, rebuttal, competing_accounts).

### 129.2 Algorithm 1: Typed Credence Propagation

**Problem**: Given the current credence assignments and edge structure, compute updated credences for all nodes that reflect the evidential support flowing through the web's typed edges.

**Approach**: Iterative message-passing with typed propagation rules, inspired by belief propagation in graphical models (Pearl, 1988) but modified for typed edges. In standard belief propagation, every edge transmits the same kind of message. In the typed web, different edge types transmit different kinds of evidential support with different attenuation factors.

**Typed Attenuation Factors**:

| Edge Type | α Factor | Rationale |
|-----------|----------|-----------|
| reduction | 0.90 | Credence flows downward with modest attenuation |
| bridge(CONSTITUTIVE) | 0.90 | Strongest evidence bridge |
| bridge(MECHANISM) | 0.75 | Complete causal pathway |
| bridge(EMPIRICAL_COV) | 0.70 | Replicated association, mechanism unspecified |
| bridge(FUNCTIONAL) | 0.60 | Functional analogy, detail may differ |
| bridge(CAPACITY) | 0.55 | Neural capacity confirmed, architectural operation unconfirmed |
| bridge(ANALOGICAL) | 0.45 | Structural analogy only |
| bridge(THEO_DEFAULT) | 0.50 | Expert-assigned placeholder |
| inheritance | 0.95 | Parameter sharing, minimal loss |
| competition | −0.30 | Negative: competitors reduce each other's credence |
| interaction | 0.10 | Weak positive: interacting templates mildly support each other |
| working_model | 0.85 | Strong theoretical commitment |
| ax_axiom | 0.80 | Meta-parameter constraint |
| partial_out | 0.00 | No credence flow; scope partition only |

**The Algorithm** (pseudocode):

```
TYPED_CREDENCE_PROPAGATION(G, θ, max_iterations, ε)

  1. Initialize: c⁰(n) = θ(n).credence for all n ∈ N.

  2. For iteration t = 1 to max_iterations:
     a. For each node n ∈ N:
        - Compute support(n) = Σ_{(m,n) ∈ E} α(τ_E(m,n)) × c^{t-1}(m)
        - Handle multi-parent reduction:
            IF complementary parents (different T1 frameworks):
              parent_support = 1 - Π_i (1 - α_red × c(p_i))  [noisy-OR]
            ELSE IF overlapping parents (same T1 framework):
              parent_support = max_i(α_red × c(p_i))          [max, no double-count]
        - Apply bridge warrant ceiling:
            c_raw(n) = (1 - λ) × c^{t-1}(n) + λ × sigmoid(support(n))
            c^t(n) = min(c_raw(n), θ(n).warrant_ceiling)
     b. Apply entrenchment:
        - T1 nodes: max decrease per iteration = 0.01
        - T1.5, AX, WM: max decrease per iteration = 0.05
        - T2 nodes: no constraint (revise freely)
     c. Convergence check:
        IF max_n |c^t(n) - c^{t-1}(n)| < ε: RETURN c^t

  3. IF max_iterations reached: FLAG WARNING (possible oscillation).

  Complexity: O(max_iterations × |E|). For CMR: ~1000 × 400 = 400K ops. Milliseconds.
  Convergence: Guaranteed when λ < 1/(1 + max_degree). For CMR (max_degree ≈ 15 for T29), λ = 0.3 suffices.
```

**Correctness concern**: The α values are parameters of the algorithm. They instantiate the bridge warrant hierarchy computationally, but they are not identical to the bridge warrant ceilings — they represent rates of credence propagation, not maximum credence. These values should be calibrated by the retrodiction test (§130, Level 2): adjust them until the algorithm best reproduces the panels' historical credence assignments.

### 129.3 Algorithm 2: Graded Competition Resolution

**Problem**: Given two or more nodes connected by competition edges, determine which (if any) should be preferred, and update credences accordingly.

**Approach**: Graded argumentation semantics, extending Dung (1995). The algorithm computes attack strengths between competing hypotheses based on their Toulmin structures (data contradiction, domain restriction, explanatory superiority, warrant superiority), then determines one of three outcomes: VICTORY (one account dominates), COMPROMISE (domain partition), or EQUILIBRIUM (no resolution).

The victory threshold (default 0.30 net advantage) and the equilibrium uncertainty parameter (default δ = 0.15) are adjustable. In the COMPROMISE case, a composite node is generated with domain-conditional credences — this is how the Barrett-Craig two-stage model would be represented formally.

**Complexity**: O(k² × |T|) where k is the number of competitors and |T| is the Toulmin structure size. For CMR's typical 2–3 way competitions with |T| ≈ 10: trivial.

**The hard part**: Computing rebuttal strength requires comparing Toulmin structures — a semantic comparison that cannot be fully automated with string matching. The pragmatic approach represents qualifiers as feature vectors over a pre-defined vocabulary of conditions (building type, occupant type, mechanism domain, temporal scale). Two qualifiers overlap when their feature vectors overlap. A domain partition exists when qualifiers are feature-disjoint.

### 129.4 Algorithm 3: Typed Global Coherence Metric

**Problem**: Compute a diagnostic measure of how well the web's beliefs hang together.

**Approach**: Typed weighted constraint satisfaction, extending Thagard (1989). Each edge is evaluated for the degree to which the beliefs at its endpoints satisfy the coherence constraint implied by the edge type. Positive-coherence edges (reduction, bridge, inheritance, interaction, working model, axiom) are satisfied when both connected nodes have high credence. Competition edges contribute positively when resolved (VICTORY or COMPROMISE) and negatively when unresolved (EQUILIBRIUM). Partial-out edges are neutral.

The global score C ∈ [-1, 1] is the ratio of total constraint satisfaction to maximum possible satisfaction. The diagnostic decomposition — by edge type (which *kinds* of connections are working well?) and by node (which *specific* templates are problematic?) — is more informative than the global score. For example, the decomposition might reveal that the web's reduction edges are highly coherent (the T1 → T1.5 → T2 structure is well-supported) but competition edges are dragging coherence down (too many unresolved competitions), or that NM4 has the lowest node coherence because its ANALOGICAL bridge is weak and it has an unresolved competition with goal-directed approach.

**Complexity**: O(|E|). For CMR: ~400 operations. Instantaneous.

### 129.5 Algorithm 4: AGM-Style Structural Revision

**Problem**: Given new evidence that conflicts with the web's current state, determine the minimal revision that restores coherence.

**Approach**: The algorithm extends AGM belief revision theory (Alchourrón, Gärdenfors, & Makinson, 1985) for typed graphs with entrenchment ordering. It first assesses impact (which nodes would change by more than a threshold δ if the new evidence were incorporated), classifies the revision type (PARAMETRIC if only T2 nodes are affected, STRUCTURAL_MODERATE if T1.5/AX/WM nodes are affected, STRUCTURAL_DEEP if T1 nodes are affected), computes entrenchment for each affected node (combining tier-based resistance, local coherence, and connectivity), then processes nodes in ascending entrenchment order, selecting at each step the least drastic revision option that restores coherence.

The five revision options, in order of increasing structural impact:

- **Option A**: Update credence (parametric change)
- **Option B**: Change edge types (e.g., upgrade bridge warrant from THEORETICAL_DEFAULT to EMPIRICAL_COVARIANCE)
- **Option C**: Add or remove edges (structural change)
- **Option D**: Change node tier (promote or demote theory)
- **Option E**: Add new node (new hypothesis or template)

The algorithm is greedy — it selects the best revision at each step without exploring all combinations. This sacrifices global optimality for tractability. The justification for greediness is that the entrenchment ordering provides a strong heuristic: revising the least entrenched belief first is almost always the correct first move. The algorithm falls back to human review when the greedy strategy fails to restore coherence.

**Complexity**: O(|affected_nodes| × 5 × |E|). For CMR: ~20 × 5 × 400 = 40K ops. Fast.

### 129.6 Algorithm 5: Value of Information

**Problem**: Rank all uncertain parameters by the expected improvement in web coherence that would result from resolving each uncertainty.

**Approach**: For each uncertainty (THEORETICAL_DEFAULTs, unresolved competitions, low-confidence mechanism steps), the algorithm simulates two scenarios — optimistic (credence set to ceiling) and pessimistic (credence set to 0.10) — and computes the expected coherence change. This is multiplied by the downstream reach (number of nodes reachable via directed edges), producing a VOI score that balances coherence impact with graph-structural importance.

The output is a ranked research agenda: "Study 1: Measure relative neuromodulatory weights in T29 (VOI = 8.3, resolves 7 THEORETICAL_DEFAULTs). Study 2: Replicate Lambert et al. 2002 with in-vivo methodology (VOI = 5.1, resolves 1 THEORETICAL_DEFAULT but high reach because 5-HT feeds T29, NM7, NM2, and LIGHT-I)."

**Complexity**: O(|uncertainties| × (|E| + |N|)). For CMR: ~50 × 530 = 26.5K ops. Fast.

### 129.7 Algorithm 6: BN Projection

**Problem**: Generate a Bayesian Network from the web's current state.

**Approach**: The algorithm identifies the observable/manipulable variables (environmental parameters and outcome variables — the endpoints of mechanism chains), compresses multi-step mechanism chains into single BN edges, populates CPTs via the elicitation protocol from §125.4, checks the DAG property, and validates conditional independence assumptions.

The key compression step is where the web's epistemological richness is lost and the BN's computational tractability is gained. A four-step mechanism chain (environmental feature → neural step 1 → neural step 2 → outcome) becomes a single BN edge with a CPT entry derived from the product of step-by-step probabilities. The intermediate neural mechanisms are not BN variables; they are compressed into the edges. The BN knows *that* daylight improves mood (with probability 0.70). The web knows *why* — through the 5-HT synthesis pathway, with Lambert et al. (2002) as primary evidence, with the circadian entrainment account as a competitor. The projection is lossy by design. This is why the web must remain the primary representation and the BN must be regenerated whenever the web changes.

When multiple mechanism chains connect the same environmental parameter to the same outcome (e.g., daylight affects mood through both the serotonergic pathway and the circadian pathway), the algorithm uses noisy-OR combination for independent pathways and noisy-AND for dependent pathways (those sharing intermediate mechanisms).

**Complexity**: O(|chains| × |length| + |V|³). For CMR: ~93 × 4 + 30³ = 27,372 ops. Trivially fast.

### 129.8 Computational Complexity Summary

| Algorithm | Complexity | CMR Runtime |
|-----------|-----------|-------------|
| 1. Credence Propagation | O(iter × \|E\|) | Milliseconds |
| 2. Competition Resolution | O(k² × \|T\|) | Microseconds per competition |
| 3. Global Coherence | O(\|E\|) | Microseconds |
| 4. Structural Revision | O(\|affected\| × \|E\|) | Milliseconds |
| 5. Value of Information | O(\|uncertainties\| × (\|E\| + \|N\|)) | Milliseconds |
| 6. BN Projection | O(\|chains\| × \|length\| + \|V\|³) | Milliseconds |

All polynomial. All milliseconds or less. The calculus can run interactively — a user can modify the web and see updated coherence, credence propagation, and VOI ranking in real time.

### 129.9 What the Algorithms Do Not Do

Honesty requires specifying limitations:

**Semantic interpretation.** The algorithms operate over the web's formal structure, not the natural-language content of the Toulmin fields. The semantic interpretation is done once, when the template is encoded, not at runtime.

**Theory generation.** The algorithms can evaluate theories, propagate credences, detect incoherence, and revise parameters. They cannot *generate* new theories. If the web needs a new T1.5 theory, Algorithm 3 will detect the gap (low coherence region) and Algorithm 5 will identify it as high-VOI, but they cannot fill it. Theory generation remains a creative act requiring human or LLM-simulated-panel intelligence.

**Causal discovery.** The algorithms take the web's causal structure as given. They do not discover new causal relationships from data. For causal discovery, the CMR would need Glymour's PC/FCI algorithms (Spirtes, Glymour, & Scheines, 2000) applied to observational building data.

**Ground truth.** Coherence is not truth. A perfectly coherent web could be perfectly wrong. The safeguard is empirical testing (§130, Levels 3–5): the web's predictions are tested against reality, and failures trigger revision.

### 129.10 References for §129

Alchourrón, C. E., Gärdenfors, P., & Makinson, D. (1985). On the logic of theory change. *Journal of Symbolic Logic*, 50(2), 510–530. [Google Scholar citations: ~4,500]

Dung, P. M. (1995). On the acceptability of arguments. *Artificial Intelligence*, 77(2), 321–357. [Google Scholar citations: ~7,500]

Pearl, J. (1988). *Probabilistic reasoning in intelligent systems*. Morgan Kaufmann. [Google Scholar citations: ~22,000]

Spirtes, P., Glymour, C., & Scheines, R. (2000). *Causation, prediction, and search* (2nd ed.). MIT Press. [Google Scholar citations: ~7,800]

Thagard, P. (1989). Explanatory coherence. *Behavioral and Brain Sciences*, 12(3), 435–467. [Google Scholar citations: ~2,400]

---

## §130: Five-Level Testing Protocol

**Insert after**: §129  
**Source**: WEB_OF_BELIEF_AND_BAYESIAN_NETWORK_ARCHITECTURE.md, Part VIII §§23–28

---

### 130.1 Testing Philosophy

A formal calculus that has not been tested against reality is an elaborate exercise in self-consistency — internally coherent but epistemically vacuous. The testing protocol specifies five levels of increasingly severe validation, each of which tests a different aspect of the calculus. The levels are cumulative: success at Level 1 is necessary before attempting Level 2, and so on. Failure at any level is diagnostic — it identifies which component of the calculus needs work, not merely that something is wrong.

### 130.2 Level 1: Internal Consistency (Sanity Checks)

**What it tests**: The calculus does not contradict itself.

**Procedure**: Encode the full CMR web (~130 nodes, all edge types) as a typed graph. Implement the six algorithms. Run them. Check the outputs against formal constraints: (a) credence propagation produces values in [0, 1] for every node, (b) the coherence metric produces a finite, non-degenerate value, (c) structural revision terminates (does not loop infinitely), (d) partial-out rules produce non-overlapping scopes, (e) inheritance chains produce consistent parameter values, and (f) bridge warrant ceilings are respected.

**What failure means**: A calculus that fails internal consistency is formally broken — the rules produce contradictions, infinities, or non-termination. Fix before proceeding.

**Computational requirement**: One pass of all algorithms over the complete web. Minutes on standard hardware.

### 130.3 Level 2: Retrodiction — Reproducing Historical Decisions

**What it tests**: The calculus captures the reasoning that the CMR panels actually performed.

**Procedure**: Reconstruct the web as it existed *before* each historical decision. Apply the calculus. Check whether it recommends the same decision. Five major test cases:

1. Barrett-Craig two-stage model adoption (THERMAL-I → CREATIVE-I)
2. Differential-mode model adoption (CREATIVE-I + NEUROMOD-I convergence)
3. AX4 perceived control elevation (CREATIVE-I Decision 2)
4. ART/SRT demotion to T1.5 (pre-pipeline assessment)
5. Aesthetic Anchoring deferral (CREATIVE-I Decision 3)

**Hard version**: Sample 50–100 micro-decisions from panel outputs and post-panel reviews (which competing account to favour, what confidence to assign, whether a template is Tier A or Tier B). Reconstruct the web state at each decision point. Apply the calculus. Score agreement.

**Scoring**: >80% agreement = strong evidence the calculus captures the panels' reasoning. 60–80% = moderate, investigate disagreement patterns. <60% = the calculus imposes a different logic than the panels used, requiring revision.

**What failure means**: Systematic disagreement patterns are diagnostic. If the calculus consistently disagrees on competition resolution but agrees on everything else, the competition-resolution protocol needs work. If it consistently disagrees on credence propagation through reduction edges, the multi-parent rule needs revision.

### 130.4 Level 3: Prediction — CROSSCUT-I as a Prospective Test

**What it tests**: The calculus can predict outcomes it has not seen.

**Procedure**: Before CROSSCUT-I execution, use the calculus to predict: (1) which AX parameters will be most contested, (2) whether ER_ECOLOGICAL_RATIONALITY_001 will achieve EMPIRICAL_COVARIANCE or be downgraded, (3) what numerical ranges AX_DOSE_RESPONSE_007 will produce, and (4) how the Aesthetic Anchoring evaluation will resolve. Write predictions down. Seal them. Execute CROSSCUT-I. Compare.

**Scoring**: 3 of 4 correct = non-trivial predictive power. All 4 = strong evidence. 0 of 4 = something is wrong. 1–2 of 4 = investigate which predictions failed and why.

**Harder test**: Can the calculus identify *errors in the existing web that the panels missed*? If the coherence metric finds a locally incoherent region (two templates with incompatible assumptions that no panel flagged), this is a testable prediction: the incompatibility should produce measurable problems when both templates' predictions are combined in the BN.

### 130.5 Level 4: Cross-Domain Transfer

**What it tests**: The calculus captures something general about scientific belief revision, not just the CMR's specific content.

**Procedure**: Encode a different scientific knowledge base — structurally similar to the CMR but content-independent — as a typed belief web using the same edge types. Apply the calculus. Have domain experts review the outputs for reasonableness.

**Candidate domains**: (a) Air pollution and cognitive decline (PM2.5 → neuroinflammation → hippocampal atrophy → memory decline), (b) Psychedelic-assisted therapy (psilocybin → 5-HT2A agonism → DMN disruption → therapeutic effect), (c) Urban noise and cardiovascular health (traffic noise → cortisol elevation → endothelial dysfunction → CVD).

**Scoring**: Domain experts rate calculus outputs without knowing the calculus was developed for architecture. If outputs are sensible, the calculus is domain-general. If specific outputs are bizarre, those disagreements diagnose domain-specificity.

### 130.6 Level 5: Adversarial Stress Testing

**What it tests**: The calculus handles pathological inputs gracefully.

**Procedure**: Construct deliberately pathological webs:

| Pathological Case | Expected Behaviour |
|------|------|
| Credence cycle (A supports B, B supports C, C supports A) | Propagation converges to fixed point, no oscillation |
| Contradictory inheritance (B inherits X from A, but B's evidence says X differs) | Conflict detection fires; determinate resolution |
| Total competition equilibrium (every competition unresolved) | Coherence degrades gracefully; imprecise credences widen but remain bounded |
| Working model contradicted by strong evidence | Structural revision fires; revision clause triggers |
| AX axiom contradicts domain-specific calibration everywhere | Priority rule produces consistent result |
| Template with 0 confidence on all mechanism steps | Template becomes inert but is not deleted |
| Circular partial-out (A partial-outs to B, B to A) | Error detection fires; circularity flagged |
| 1000-node web (10× the CMR) | Algorithm completes in < 1 hour on standard hardware |

### 130.7 The Ultimate Test: Discovery

The deepest test is whether the calculus can discover something the human experts missed — a non-obvious consequence of the web's structure that follows from formal rules but was invisible to informal reasoning. Candidate discoveries: a T1.5 theory more strongly supported than the panels recognised (because independent support from three T1 frameworks was not noticed), a THEORETICAL_DEFAULT with far higher VOI than anyone realised (because it sits at a graph bottleneck), or a pair of templates with incompatible assumptions that no panel flagged. If the calculus produces genuine discoveries, it has demonstrated that it extends the community's reasoning capacity beyond what informal deliberation can achieve.

### 130.8 References for §130

Campbell, D. T., & Stanley, J. C. (1963). *Experimental and quasi-experimental designs for research*. Houghton Mifflin. [Google Scholar citations: ~52,000]

Kelly, K. T. (1996). *The logic of reliable inquiry*. Oxford University Press. [Google Scholar citations: ~600]

---

## §131: Three Frontiers — Pushing the Architecture Further

**Insert after**: §130  
**Source**: WEB_OF_BELIEF_AND_BAYESIAN_NETWORK_ARCHITECTURE.md, Part VII §§20–22

---

### 131.1 Frontier 1: Temporal Dynamics — The Web as a History, Not a Snapshot

The FOUNDATIONS-I specification treats the web as a static structure — here are the beliefs, here are the edges, here is the coherence score. But the web has a history. It was different after STRESS-I (3 templates, sparse edges) than after NEUROMOD-I (96 templates, dense edges). The Barrett-Craig model did not exist before THERMAL-I. AX4 was an informal pattern before CREATIVE-I and a formally elevated moderator after.

A complete calculus needs to reason about the web's *trajectory* — how it has changed, whether the changes have been improvements, and what trajectory it is on. This requires tracking coherence over time and asking whether each panel left the web in a better state than it found it.

**The path dependence question.** Would the web have reached a different state if the panels had been run in a different order? If NEUROMOD-I had come before STRESS-I, the HPA parameters would have been calibrated in a different context. A useful formal analogy is the theory of Markov chain convergence. If the panel process is like a Markov chain on the space of possible webs, the question is whether the chain is ergodic — whether it converges to a unique stationary distribution regardless of starting state. If ergodic, panel ordering does not matter in the long run. If non-ergodic, the final web depends on the path, and the path constitutes an epistemologically significant design decision.

**Implementation**: Instrument the web with typed diffs between snapshots (before/after each panel). A script that takes two web states and produces: new nodes, removed nodes, new edges, changed edges, changed credences, changed warrants. Run Algorithm 3 (coherence metric) on each snapshot. Plot coherence trajectory. Answer: is it monotonically increasing? Path-dependent? Does it show signs of convergence?

### 131.2 Frontier 2: Imprecise Credences — Honest Uncertainty

The FOUNDATIONS-I specification assumes point-valued credences. But some scientific disagreements may be genuinely irresolvable given current evidence. The motor-afferent and attentional-release accounts of walking-creativity both have evidence; neither has enough to win. The current solution (recording the disagreement, capping confidence at 0.50) is a hack — it assigns a spuriously precise point value to a genuinely imprecise state of knowledge.

The formal tool for representing irresolvable disagreement is **imprecise probability** (Levi, 1980; Walley, 1991). Instead of a single credence, assign an interval: the walking-creativity mechanism has credence [0.30, 0.60] under the motor-afferent account and [0.25, 0.55] under the attentional-release account. The overlapping intervals formally represent the irresolvability.

**Implementation**: Extend Algorithm 1 to interval-valued credences. Implement interval arithmetic (the product of two intervals is [a_lo × b_lo, a_hi × b_hi]; the noisy-OR of two intervals uses the outer hull). Test whether output intervals are informatively narrow (useful for practitioners) or vacuously wide (meaning the science is too uncertain for practical guidance). Interval-valued web credences project into interval-valued BN CPTs, producing interval-valued interventional predictions: "If you increase daylight, mood improves by d ∈ [0.15, 0.45]." The width of the interval is directly informative for the architect — it says how much residual scientific uncertainty remains.

### 131.3 Frontier 3: Meta-Uncertainty — The Calculus's Uncertainty About Itself

The FOUNDATIONS-I panel will produce inference rules. But how confident should we be that those rules are correct? The calculus is itself a theory (about how scientific belief revision works), and like any theory, it could be wrong. A truly self-aware system would carry meta-level credences on its own inference rules: "I am 0.70 confident that the conjunctive rule for multi-parent reduction is correct, and 0.50 confident that the argumentation-defeat protocol for competition resolution is correct."

This creates a regress (meta-meta-credences on the meta-credences), which is a well-known problem in epistemology. The pragmatic resolution is to fix a depth: one level of meta-uncertainty, treated as THEORETICAL_DEFAULTs that can be revised by experience. When the retrodiction test (Level 2) shows that the competition-resolution protocol reproduces only 60% of historical decisions, the meta-credence for that protocol drops, and the system treats competition-resolution outputs with greater caution.

The epistemic/aleatory distinction applies here too. The calculus's aleatory properties are its formal consequences (given this web state, the coherence metric produces this value — a mathematical fact). The epistemic properties are our uncertainty about whether the calculus is the *right* one (maybe the coherence metric tracks something other than truth). Testing reduces the epistemic uncertainty while relying on the aleatory properties.

**Implementation**: Sensitivity analysis over algorithmic parameters (α values, victory thresholds, impact deltas). Run the full algorithm suite with 100 parameter samples drawn from prior distributions over the α values. Measure output variance. If the outputs are stable across parameter samples, the meta-uncertainty is low. If outputs vary widely, the specific parameters that drive the variance are the highest-priority targets for empirical calibration.

### 131.4 References for §131

Kelly, K. T. (1996). *The logic of reliable inquiry*. Oxford University Press. [Google Scholar citations: ~600]

Levi, I. (1980). *The enterprise of knowledge*. MIT Press. [Google Scholar citations: ~2,000]

Walley, P. (1991). *Statistical reasoning with imprecise probabilities*. Chapman & Hall. [Google Scholar citations: ~3,700]

---

# CATEGORY B: DEEPENING OF EXISTING SECTIONS

---

## B.1 Additions to §49 (Quinean Webs and Bayesian Networks)

### For §49.5: Web Self-Sufficiency

**Insert into §49.5 as a new paragraph or subsection.**

The web can perform its own compositional quantitative reasoning along mechanism chains. When the web encodes a chain such as daylight → 5-HT synthesis (d = 0.38) → wanting-liking balance moderation (d = 0.45) → approach motivation (d = 0.55), it can propagate these effect sizes compositionally to derive the expected compound effect. The BN's unique contribution is therefore narrowed to two formally precise capabilities: (1) interventional reasoning via do-calculus, which separates causation from association in the presence of confounders by severing incoming edges on intervention (Pearl, 2009), and (2) counterfactual reasoning, which computes probabilities in hypothetical worlds by combining abduction (conditioning on actual observations), action (intervening on hypothetical variables), and prediction (computing the counterfactual probability via structural equations). This is a stronger claim than the current §49.5 makes — it means the web is nearly self-sufficient for everything except formal causal inference. The BN provides causal logic, not quantitative computation. See §126 for the full argument and the revised asymmetric flow diagram.

### For §49.7: Haack's Critique Now Has a Proposed Answer

**Insert into §49.7 as a new paragraph.**

Susan Haack's critique of coherentism — that coherence is underspecified as a criterion of justification unless the coherence metric is itself explicitly defined — now has a proposed answer within the CMR system. The FOUNDATIONS-I panel specification (§128) addresses this directly by specifying a formal coherence metric (Algorithm 3, §129) based on typed constraint satisfaction. The metric is computable in O(|E|) time, produces both a global score and a diagnostic decomposition by edge type and by node, and treats resolved competitions differently from unresolved ones. Whether this metric fully answers Haack's critique depends on whether it tracks truth (not just internal consistency), which is the purpose of the Level 3–5 testing protocol (§130). But the critique can no longer be sustained in its strongest form: the CMR has a formal, computable coherence metric with explicit semantics for every edge type.

---

## B.2 Additions to §70 (NEUROMOD-I Panel)

**Insert after the current §70 content.**

### Post-Panel Opus Review Results

The Opus review (OPUS_REVIEW_NEUROMOD_I_FINAL.md, 17K) cleared NEUROMOD-I as the best panel in the pipeline to date. Key findings:

**T29 verification confirmed.** The allostatic load master template — the most cross-connected template in the corpus — was verified against all 12 integration constraints. One mild double-count was identified (the NE alerting term in T29 overlaps with the STRESS-I cortisol pathway) and accepted as within tolerance, with a partial-out edge recommended for future refinement.

**Differential-mode model formally adopted.** The convergence between CREATIVE-I's cognitive analysis (low stimulation → divergent thinking, moderate stimulation → convergent thinking) and NEUROMOD-I's computational analysis (explore-exploit trade-off mediated by NE tonic/phasic balance) constitutes independent derivation from different theoretical traditions. The differential-mode model was formally adopted as the third CMR working model, alongside Barrett-Craig two-stage interoceptive processing and (pending CROSSCUT-I evaluation) Aesthetic Anchoring.

**17 THEORETICAL_DEFAULTs appropriate.** The Opus review confirmed that NEUROMOD-I's 17 THEORETICAL_DEFAULT parameters are justified — they represent honest placeholders in a domain where the computational neuroscience is well-characterised at the systems level but the architectural application is largely untested. The review ranked these by VOI, with the relative neuromodulatory weights in T29 as the highest-priority empirical target.

**NM4 weakest template.** NM4 (Incentive Sensitisation) was flagged as the weakest template in the set (0.40 confidence, ANALOGICAL bridge). The analogy between drug-related incentive sensitisation and architectural place attachment is suggestive but unconfirmed. The review recommended retaining NM4 as a placeholder but cautioned against relying on its predictions.

**Lambert et al. (2002) single-study flag.** The 5-HT pathway (critical for NM7, NM2, and the T29 w_5HT term) rests primarily on Lambert et al. (2002), a single study with an unusual methodology (jugular venous sampling to infer brain 5-HT turnover from peripheral metabolites). Replication with modern in-vivo methodology was flagged as a high-priority research target.

---

## B.3 Additions to §71 (CROSSCUT-I Panel)

**Insert as new content for §71 (which may currently be skeleton or brief).**

### Pre-Panel Clearance Results

The CROSSCUT-I pre-panel clearance review (REVIEW_CROSSCUT_I_CLEARANCE.md, 21K) identified two structural decisions requiring human approval and seven issues to resolve before panel execution.

**Decision A: Panel structure.** Keep a unified panel with Phase A (AX parameters) / Phase B (CROSS-template interactions) and a hard checkpoint at C-09, versus splitting into separate AX-I and CROSS-I panels. Recommendation: keep unified, because AX-CROSS interactions are the panel's distinctive contribution and splitting them would lose the synergies.

**Decision B: Awe templates.** Include 2 of the 3 proposed awe templates: consolidate AX3_HIGH_PE + AX3_NEED_FOR_ACCOMMODATION into a single template; keep AX3_SMALL_SELF as a separate template; defer standalone accommodation. This reduces the panel's workload while preserving the most theoretically distinctive contributions.

**Seven issues flagged**: (1) Differential-mode model not yet documented in the CROSSCUT-I specification, (2) AX4 canonical specification needed, (3) Neurodiversity treatment missing from the individual differences model, (4) IE-DPT integration requirements for AX templates not specified, (5) Ecological rationality template needs conditional status (EMPIRICAL_COVARIANCE achievable only if specific evidence criteria met), (6) VR limitation discount needs temporal curve specification, (7) Friston panel management protocol needed for predictive processing templates.

**Updated constraints**: C-01 through C-11 documented in the review.

---

## B.4 Additions to §85 (BN-Web Relationship)

**Insert as a revision note and new subsection.**

### §85 Revision Note: The Asymmetric Architecture

The current §85 treats the BN-Web relationship as bidirectionally constraining with roughly symmetric contributions. The February 25, 2026 architectural analysis (WEB_OF_BELIEF_AND_BAYESIAN_NETWORK_ARCHITECTURE.md) sharpens this: the relationship is **asymmetric**. The web is epistemically primary and can compute quantitative consequences on its own through compositional chain propagation. The BN's unique contribution is narrowed to interventional reasoning (do-calculus, for separating causation from association in the presence of confounders) and counterfactual reasoning (computing what would have happened under alternative conditions) — not quantitative prediction, which the web performs through its own mechanism chains.

The flow diagram in §85 should be updated to reflect this asymmetry: the web as the larger, primary structure generating the BN as a derived projection, with the BN feeding back only causal logic and empirical accountability. The full argument is in §126. The revised flow diagram appears in the WEB_OF_BELIEF document, Part X §38.

---

## B.5 Additions to §56.2 (12-Panel Roster) and §56.4 (Panel Contributions)

### For §56.2: Updated Template Counts

Update the panel roster to reflect actual panel outputs: CREATIVE-I = 7 templates, NEUROMOD-I = 11 templates (expanded from the initially planned 7, reflecting the T29 master template, the Dayan taxonomy implementation, and the addition of NM10 and NM11), CROSSCUT-I = 17 templates (8 AX + 7 CROSS + 2 awe, expanded from 15 in earlier plans). Total calibrated pipeline templates: 96 (after NEUROMOD-I; 113 projected after CROSSCUT-I).

### For §56.4: What Each New Panel Contributes

**NEUROMOD-I** contributed: (a) the T29 allostatic load master template — the most cross-connected template in the corpus, integrating DA, NE, ACh, 5-HT, and cortisol pathway inputs into a unified measure of physiological regulation cost; (b) the Dayan computational taxonomy (DA = reward prediction error, NE = unexpected uncertainty, ACh = expected uncertainty, 5-HT = aversive prediction), which provides the computational substrate for the differential-mode model; and (c) convergence with CREATIVE-I on the differential-mode model, constituting independent derivation from different theoretical traditions.

**CROSSCUT-I** (projected contributions): (a) AX3 awe templates, resolving orphaned VISUAL-I cross-template flags that identified awe-relevant visual properties (scale, complexity, prospect) without a dedicated theoretical treatment; (b) the three-tier individual differences model including neurodiversity as a structural variable (not merely a moderator); and (c) the era-dependent VR limitation discount, replacing the current fixed discount with a temporal curve that reflects improving VR fidelity over time.

---

# CATEGORY C: COWORK NEW-FILES ALERT SPECIFICATION

---

## Cowork New-Files Integration Monitor — Working Specification

### C.1 Purpose

Automated detection of new or modified files in the CMR project that contain material warranting integration into MASTER_DOC_CMR. This monitor should execute as a check at the START of every Cowork session. Its output is a structured integration brief that tells the current session what new material exists and where it should go.

### C.2 Monitored Locations

```
/mnt/user-data/outputs/          — Opus/Chat session outputs (primary)
/mnt/user-data/uploads/          — User-uploaded documents (secondary)
```

### C.3 File Patterns That Trigger Alerts

```
Pattern                           Type
------                            ----
REVIEW_*                          Panel reviews (pre-panel or post-panel)
OPUS_REVIEW_*                     Opus clearance reviews
*_Panel_Output.md                 Panel execution outputs
*_PANEL_OUTPUT.md                 Panel execution outputs (variant)
TRANSFER_*.md                     Session transfer documents
WEB_OF_BELIEF_*                   Architectural philosophy documents
PANEL_SPECIFICATION_*             New panel specifications
FOUNDATIONS_I_*                    Meta-epistemological foundations
CMR_ARCHITECTURE_*                Architecture explanation updates
MASTER_DOC_SUPPLEMENT_*           Supplement documents
```

### C.4 Integration Classification Protocol

When Cowork encounters a new file matching the patterns above, it should:

**Step 1**: Read the file (or at minimum the first 200 lines and any table of contents).

**Step 2**: Compare its content against the MASTER_DOC table of contents (Parts I–XV, §§1–131 after this supplement is integrated).

**Step 3**: Classify new material using this rubric:

| Classification | Description | Example |
|----------------|-------------|---------|
| **A (New Section)** | Content not covered by any existing section | WEB_OF_BELIEF doc → new §125–131 |
| **B (Deepening)** | Content that extends an existing section | OPUS_REVIEW_NEUROMOD → extends §70 |
| **C (Technical Appendix)** | Pseudocode, formal specs, testing protocols | Algorithm pseudocode → Appendix to §129 |
| **D (Correction)** | Content that corrects or supersedes existing material | Revised template counts → corrects §56.2 |

**Step 4**: Generate an integration brief in this format:

```
═══════════════════════════════════════════════
INTEGRATION ALERT
═══════════════════════════════════════════════
File:            [filename]
Date detected:   [date]
File size:       [size in K]
Classification:  A / B / C / D
Target section:  §[number] or Part [number]
Summary:         [2-3 sentences describing what's new]
Priority:        HIGH / MEDIUM / LOW
Integration est: [estimated effort: TRIVIAL / MODERATE / SUBSTANTIAL]
═══════════════════════════════════════════════
```

### C.5 Priority Rules

- **HIGH**: New intellectual content not in any existing section (Classification A), or corrections to existing material (Classification D)
- **MEDIUM**: Extensions to existing sections (Classification B)
- **LOW**: Technical appendices (Classification C), transfer documents (used for session continuity, not permanent integration)

### C.6 Current Backlog (February 25, 2026)

Files produced in Sessions 9–10 needing integration:

| File | Classification | Target | Priority | Status |
|------|---------------|--------|----------|--------|
| WEB_OF_BELIEF_AND_BAYESIAN_NETWORK_ARCHITECTURE.md | A | New §125–131 (Part XIV–XV) | HIGH | **Addressed by this supplement** |
| PANEL_SPECIFICATION_FOUNDATIONS_I.md | A | §128 (Part XV) | HIGH | **Addressed by this supplement** |
| OPUS_REVIEW_NEUROMOD_I_FINAL.md | B | §70 | MEDIUM | **Addressed by this supplement** |
| REVIEW_CROSSCUT_I_CLEARANCE.md | B | §71 | MEDIUM | **Addressed by this supplement** |
| REVIEW_CREATIVE_I_CLEARANCE_AND_DECISIONS.md | B | §69 | MEDIUM | Pending |
| REVIEW_NEUROMOD_I_CLEARANCE.md | B | §70 | MEDIUM | Partially addressed |
| FOUNDATIONS_I_PANEL_OUTPUT.md | A/C | §128, Appendix | MEDIUM | Pending |

### C.7 Session-Start Prompt Template

The following prompt should be executed at the start of every Cowork session that may involve MASTER_DOC maintenance:

```
COWORK SESSION START — INTEGRATION CHECK

1. List all files in /mnt/user-data/outputs/ and /mnt/user-data/uploads/
   matching the monitored patterns in C.3.

2. For each matching file, check whether it has been integrated into
   MASTER_DOC_CMR by searching for a reference to the filename in the
   master document's changelog or integration notes.

3. For any unintegrated file, generate an Integration Alert (format C.4).

4. Present all alerts to David for prioritisation before proceeding
   with other work.

5. If no unintegrated files are found, report "Integration backlog clear"
   and proceed.
```

### C.8 Implementation Notes

This alert system operates at the prompt level (instructions to Cowork), not at the code level (no scripts or daemons). It depends on Cowork reading and following the instructions in this specification. The specification should be stored in a stable location that Cowork can access at every session start — either as a section of MASTER_DOC itself or as a referenced companion document.

For a future code-level implementation, the file-matching and classification steps (C.3–C.4) could be implemented as a Python script that scans the directories, matches patterns, reads file headers, and generates structured JSON alerts. The classification step (C.4 Step 2–3) would require either keyword matching against the MASTER_DOC TOC or a lightweight LLM call to classify each file. The priority assignment (C.5) is rule-based and trivially automatable.

---

# CONSOLIDATED REFERENCES

*All references cited in this supplement, in APA format. Google Scholar citation counts are approximate as of February 2026.*

Alchourrón, C. E., Gärdenfors, P., & Makinson, D. (1985). On the logic of theory change: Partial meet contraction and revision functions. *Journal of Symbolic Logic*, 50(2), 510–530. https://doi.org/10.2307/2274239 [~4,500 citations]

Berridge, K. C., & Robinson, T. E. (1998). What is the role of dopamine in reward: Hedonic impact, reward learning, or incentive salience? *Brain Research Reviews*, 28(3), 309–369. https://doi.org/10.1016/S0165-0173(98)00019-8 [~5,500 citations]

Bovens, L., & Hartmann, S. (2003). *Bayesian epistemology*. Oxford University Press. https://doi.org/10.1093/0199269750.001.0001 [~1,600 citations]

Campbell, D. T., & Stanley, J. C. (1963). *Experimental and quasi-experimental designs for research*. Houghton Mifflin. [~52,000 citations]

Daniels, N. (1979). Wide reflective equilibrium and theory acceptance in ethics. *Journal of Philosophy*, 76(5), 256–282. https://doi.org/10.2307/2025881 [~1,400 citations]

de Finetti, B. (1937). La prévision: Ses lois logiques, ses sources subjectives. *Annales de l'Institut Henri Poincaré*, 7(1), 1–68. [~4,200 citations]

Dung, P. M. (1995). On the acceptability of arguments and its fundamental role in nonmonotonic reasoning, logic programming and n-person games. *Artificial Intelligence*, 77(2), 321–357. https://doi.org/10.1016/0004-3702(94)00041-X [~7,500 citations]

Elgin, C. Z. (1996). *Considered judgment*. Princeton University Press. [~700 citations]

Gärdenfors, P. (2000). *Conceptual spaces: The geometry of thought*. MIT Press. [~4,200 citations]

Goodman, N. (1955). *Fact, fiction, and forecast*. Harvard University Press. [~7,500 citations]

Hacking, I. (1975). *The emergence of probability*. Cambridge University Press. [~3,800 citations]

Hájek, A. (2019). Interpretations of probability. In E. N. Zalta (Ed.), *Stanford Encyclopedia of Philosophy*. Stanford University.

Jeffreys, H. (1961). *Theory of probability* (3rd ed.). Oxford University Press. [~8,000 citations]

Kelly, K. T. (1996). *The logic of reliable inquiry*. Oxford University Press. [~600 citations]

Lambert, G. W., Reid, C., Kaye, D. M., Jennings, G. L., & Esler, M. D. (2002). Effect of sunlight and season on serotonin turnover in the brain. *The Lancet*, 360(9348), 1840–1842. https://doi.org/10.1016/S0140-6736(02)11737-5 [~1,100 citations]

Laudan, L. (1977). *Progress and its problems: Towards a theory of scientific growth*. University of California Press. [~4,000 citations]

Levi, I. (1980). *The enterprise of knowledge*. MIT Press. [~2,000 citations]

Pearl, J. (1988). *Probabilistic reasoning in intelligent systems: Networks of plausible inference*. Morgan Kaufmann. [~22,000 citations]

Pearl, J. (2009). *Causality: Models, reasoning, and inference* (2nd ed.). Cambridge University Press. https://doi.org/10.1017/CBO9780511803161 [~28,000 citations]

Prakken, H. (2010). An abstract framework for argumentation with structured arguments. *Argument and Computation*, 1(2), 93–124. https://doi.org/10.1080/19462161003734514 [~800 citations]

Quine, W. V. O., & Ullian, J. S. (1970). *The web of belief*. Random House. [~2,500 citations]

Rawls, J. (1971). *A theory of justice*. Harvard University Press. [~65,000 citations]

Reichenbach, H. (1949). *The theory of probability*. University of California Press. [~2,000 citations]

Savage, L. J. (1954). *The foundations of statistics*. Wiley. [~15,000 citations]

Spirtes, P., Glymour, C., & Scheines, R. (2000). *Causation, prediction, and search* (2nd ed.). MIT Press. [~7,800 citations]

Thagard, P. (1989). Explanatory coherence. *Behavioral and Brain Sciences*, 12(3), 435–467. https://doi.org/10.1017/S0140525X00057046 [~2,400 citations]

Thagard, P. (2000). *Coherence in thought and action*. MIT Press. [~2,200 citations]

von Mises, R. (1928). *Wahrscheinlichkeit, Statistik und Wahrheit*. Springer. [~2,100 citations]

Walley, P. (1991). *Statistical reasoning with imprecise probabilities*. Chapman & Hall. [~3,700 citations]

---

*MASTER_DOC_SUPPLEMENT_EXPANDED_Feb25.md — CMR Project*  
*Generated by Opus/Chat, February 25, 2026 (Session 11)*  
*Supersedes: MASTER_DOC_SUPPLEMENT_Feb25.md (465 lines, pre-crash version)*  
*For integration by Cowork into MASTER_DOC_CMR at insertion points specified above*  
*Total: ~2,000 lines | Covers §125–131 (new), §49/§56/§70/§71/§85 (deepening), Cowork alert spec*
