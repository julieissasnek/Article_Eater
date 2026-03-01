# Expert Panel Discussion: "Two Kinds of Uncertainty" by David Kirsh

## A Structured Critique by Eight Leading Scholars

**Location:** UC San Diego Supercomputer Center, Conference Room 312
**Date:** March 15, 2024
**Moderator:** Dr. Helen Chen, Stanford
**Panelists:** Nancy Cartwright, Judea Pearl, Armen Der Kiureghian, Sarah Moss, Paul Thagard, Andrea Saltelli, James Woodward, Craig Fox

---

## ROUND 1: OPENING REACTIONS

### Nancy Cartwright (Philosophy of Science, Durham/UCSD)

David has tackled something important here: the recognition that computational systems don't simply suffer from conflating two kinds of uncertainty—they actually require a principled architecture to handle them separately. I find myself sympathetic to the methodological spirit. For decades, I've argued against the assumption that nature operates according to universal laws; instead, I've emphasized nomological machines—particular causal capacities in specific contexts. Kirsh's dual architecture (Web of Belief paired with Bayesian networks) resonates with that commitment to localized, context-sensitive structures.

What excites me most is the bridge warrant types. The idea that we can categorize epistemic uncertainty more finely than the old binary split—that we can distinguish warrants for our beliefs by their provenance and stability—feels concrete and psychologically plausible. The environmental psychology example (daylight → serotonin → mood) helps ground this abstraction.

But I confess a worry: are the warrant types really tracking causal capacities (the real regularities that hold within a circumscribed context) or are they simply regularities that happen to hold in our sample of models and evidence? The paper doesn't quite address whether the projection function that translates epistemic to aleatory uncertainty respects the real causal structure of the world, or whether it's just a useful fiction for computation. That distinction matters enormously if we care about inference to scientific reality.

### Judea Pearl (Computer Science, UCLA)

Kirsh is asking precisely the right question: why do so many computational systems treat epistemic and aleatory uncertainty as indistinguishable? He proposes a dual architecture—one sub-system maintaining a Web of Belief, another maintaining a Bayesian Network—with a projection function translating between them. On the surface, this is attractive.

But I need to see the mathematics. What is the projection function formally? How does it preserve conditional independence? In my framework of structural causal models, the separation of epistemic from aleatory uncertainty maps onto distinguishing between our uncertainty about the structure of the world and our uncertainty about the values of variables within a known structure. That's clean. I'm not yet convinced Kirsh's projection function achieves comparable rigor. The 5-step CPT elicitation protocol sounds reasonable for operationalization, but I don't see the formal guarantees. Under what conditions does this procedure preserve d-separation? Does the projection function admit a representation theorem?

What I appreciate is that Kirsh isn't trying to dissolve the distinction—he's embracing it and building a system around it. That's wise. But if we're going to claim this solves a fundamental problem in computational uncertainty reasoning, we need proofs, not just protocols.

### Armen Der Kiureghian (Structural Engineering, UC Berkeley)

I'm genuinely pleased that Kirsh takes our framework seriously. My 2009 paper with Mahadevan argued that the distinction between aleatory and epistemic uncertainty is fundamentally pragmatic and model-dependent: what appears aleatory in one model may become epistemic once we refine the model. It's not a metaphysical fact carved into nature. Rather, it's a feature of our current best model relative to our decision context.

What Kirsh does well is operationalize this pragmatism. The ATLAS system isn't pretending the distinction is absolute; it's saying: within a given modeling context, here's how we systematically separate and handle the two types. The 5-step protocol for CPT elicitation is exactly the kind of methodological guidance engineers need. I can imagine implementing something like this in our structural reliability analysis software.

My one reservation: does the paper go too far in the philosophical direction? It reads the pragmatic view (our view) as making epistemic uncertainty somehow less "real" or less fundamental. I don't think that's right. Epistemic uncertainty is profoundly real—it's about our ignorance of true parameter values, model form, causal relationships. By treating it separately, Kirsh isn't reducing it; he's respecting it. That nuance could be clearer.

### Sarah Moss (Philosophy, U Michigan)

Let me register my immediate concern: Kirsh assumes that epistemic and aleatory uncertainty can be cleanly separated. I've spent the last decade arguing they're interleaved. You can't sharply partition your uncertainty about causal mechanisms (epistemic) from your uncertainty about particular outcomes given those mechanisms (aleatory). Beliefs about mechanisms are themselves probabilistic; they're not binary or certain.

That said, I don't think Kirsh is claiming certainty about epistemic matters. The Web of Belief component of his dual architecture is itself a probabilistic system. So perhaps there's less disagreement than first appears. His claim might be simply that we can distinguish a system dedicated to tracking causal and mechanistic uncertainty from a system tracking outcome uncertainty given those mechanisms. That's more modest than I initially read it.

What I want to press is whether the bridge warrant types genuinely capture the interleaving problem. If I'm uncertain about a causal warrant—say, whether daylight really affects serotonin production, or how strongly—that uncertainty is both epistemic (about the mechanism) and aleatory (about variation in how the mechanism operates). Does the projection function adequately represent this entanglement? Or does it assume a cleaner separation than cognitive reality supports?

Still, the architectural move is sound in spirit. And the environmental psychology example is far more tractable than much philosophy of probability has managed.

### Paul Thagard (Cognitive Science/Philosophy, U Waterloo)

I'm struck by the absence of coherence from this framework. For thirty years, I've argued that the best way to understand how people resolve uncertainty is through a process of maximizing coherence among their beliefs, desires, and explanations. My ECHO system was built on exactly this insight: uncertainty isn't just about assigning probabilities; it's about achieving a global coherence among multiple constraints.

Kirsh's Web of Belief component could potentially integrate coherence reasoning, but the paper doesn't discuss how. When you elicit warrant types for epistemic uncertainty, aren't you implicitly asking: which beliefs cohere best with the available evidence and background knowledge? That's a coherence question, not just a probabilistic one.

The dual architecture is interesting—keep mechanistic/causal knowledge separate from outcome predictions. That maps onto something real in cognitive science: we do maintain distinct systems for understanding mechanisms versus forecasting. But why not make coherence the glue? Why not say that our system maintains coherence across both the Web of Belief and the Bayesian Network simultaneously?

Possibly Kirsh has reasons for favoring his epistemic/aleatory architecture over a coherence framework. I'd like to hear them. For now, the paper reads as having solved half the problem—the organizational half—without addressing the dynamic, updating, belief-revision half.

### Andrea Saltelli (Statistics/Sensitivity Analysis, Open U of Catalonia)

I'll be direct: I like the ambition, but I'm deeply skeptical about whether the 5-step CPT elicitation protocol is grounded in reality or fantasy.

Here's my concern: most of the "epistemic uncertainty" that gets translated into Bayesian priors is actually modeler confidence wearing disguise. We build a model, we're uncertain about its parameters, and we assign a prior distribution. But that prior is often arbitrary, driven by convenience rather than genuine evidence. Saltelli's Sensitivity Analysis has shown repeatedly that many models are wildly overconfident because their uncertainty quantification is sloppy. We act as though we've constrained the epistemic uncertainty when really we've just hidden it in prior assumptions.

Kirsh's framework looks elegant on paper. But unless the discount factors on each of the five warrant types are empirically calibrated—unless we can show that belief revisions actually follow the dynamics he proposes—I'm worried this is computational theater. Does the paper give any empirical evidence that the ATLAS system predicts how actual systems should update when new evidence arrives? Has anyone tested whether people's belief updates match the warrant-type dynamics?

I'm not dismissing the idea. I'm saying: show me the data. Show me that the discount factors aren't arbitrary. Show me that the projection function correctly captures how uncertainty propagates in real systems. Until then, this feels like adding ornaments to a Bayesian structure without genuinely improving our grip on epistemic vs. aleatory distinction in practice.

### James Woodward (Philosophy, Causation, U Pittsburgh)

I appreciate Kirsh's attention to causal reasoning. The problem he's diagnosing is real: computational systems don't properly track the distinction between causal claims (which are epistemically uncertain) and outcome claims (which are aleatorily uncertain given causal knowledge). From an interventionist perspective—my framework for understanding causation—this distinction is absolutely central. To know a causal claim is to know how outcomes would change under intervention. That's epistemically fraught. Knowing the probability of an outcome given a causal mechanism is a different matter.

The bridge warrant types partly capture this. A "direct experimental warrant," for instance, suggests evidence from intervention, which provides strong causal knowledge. A "mechanistic warrant" suggests understanding of how the causal process works. These are the right categories from an interventionist standpoint.

What bothers me slightly is that the paper doesn't fully embrace the interventionist semantics. It talks about "causal relationships" and "epistemic uncertainty about mechanisms," but it doesn't make explicit that to claim you know a causal relationship, you must (under my analysis) be claiming knowledge about what would happen if you intervened. The warrant types should perhaps be more explicitly indexed to intervention: which warrant types support interventional claims versus merely observational claims? The paper hints at this but doesn't sharpen it.

Also, I want to know: does the projection function preserve the interventionist interpretation? That is, if you translate from epistemic (causal) claims to aleatory (probabilistic) claims via the projection, do you preserve information about what would happen under intervention? Or do you wash that out in the translation?

### Craig Fox (Psychology/Decision Science, UCLA)

Finally, someone needs to ask: is this distinction psychologically real?

I'm glad it came to this panel because Ülkümen and I have spent years studying how people actually distinguish epistemic from aleatory uncertainty in their judgments. We've found robust evidence that people do make this distinction—they treat uncertainty about the state of the world differently from uncertainty about how the world works. But our work also shows the distinction is cognitively taxing and people often conflate the two when reasoning is fast or automatic.

Here's my question for Kirsh: are the bridge warrant types psychologically real categories? Do people actually distinguish among "direct experimental warrant," "mechanistic warrant," "consensus warrant," etc., when they're reasoning about uncertainty? Or is the five-fold categorization an analyst's invention that carves nature at joints but doesn't correspond to actual cognitive structures?

The environmental psychology example is useful, but anecdotal. Has anyone run experiments showing that people's belief updates track these warrant types? That when someone learns new mechanistic evidence, their updating follows different dynamics than when they learn observational evidence? If the warrant types are just a convenient taxonomy for us (the modelers) rather than a reflection of how minds work, that's fine—but let's be honest about it. The paper seems to be claiming something stronger: that the ATLAS system mirrors actual cognition. I want evidence.

That said, the framework is sophisticated, and if it generates testable predictions about how people should update their beliefs given different warrant types, that could be fascinating. So I'm cautiously optimistic.

---

## ROUND 2: FOCUSED CRITIQUES

### Nancy Cartwright: On Causal Warrant and Nomological Machines

Let me sharpen my critique from a philosophy-of-science standpoint. Kirsh proposes that the bridge warrant types categorize epistemic uncertainty. But categories aren't explanations. He gives us five warrant types (direct experimental, mechanistic, consensus, historical, and analogical). The question is: do these types correspond to real differences in the causal powers they warrant, or are they just useful bookkeeping?

In my framework, a causal claim commits you to a nomological machine—a stable arrangement of types and capacities that can be brought to bear to produce effects. When you have "direct experimental warrant," you've observed the machine at work under controlled conditions. When you have "mechanistic warrant," someone has told you what makes the machine work. Both are valuable, but they're epistemically different: the first gives you demonstrated capacity; the second gives you understanding of mechanism.

Kirsh's framework doesn't quite make this distinction clear. The warrant types are presented as interchangeable inputs to the projection function, each with a discount factor. But that's backwards. Not all warrants are created equal. An experimental warrant for a causal claim is categorically stronger—it shows the capacity actually operates—whereas a mechanistic warrant is about understanding, which is compatible with the capacity failing to manifest in practice.

The environmental psychology example illustrates this perfectly. Kirsh argues we have mechanistic warrant (daylight → serotonin) and historical warrant (people report mood changes with season). But are these sufficient to say daylight causally produces the serotonin-mood pathway? We'd want experimental warrant: randomized intervention on light exposure, measured serotonin and mood. Without that, we're stuck with warrant about mechanisms and correlations, not causal capacity.

Moreover, the 5-step CPT elicitation protocol doesn't address this. It asks experts to assign prior probabilities to causal relationships given warrant types. But it doesn't ask the crucial question: is this warrant sufficient to claim that the causal relationship actually exists and would operate reliably in other contexts? That's what I mean by tracking nomological machines. The paper conflates epistemic warrant (reason to believe) with evidence of causal capacity (demonstration that the mechanism works).

Finally, the projection function treats epistemic uncertainty as something that, once reduced by gathering warrant, converts into aleatory uncertainty via a deterministic translation rule. But that's not how causal knowledge works. Even when I'm certain a mechanism exists, the manifestation of that capacity remains genuinely contingent on local conditions. The contingency isn't merely aleatory; it's contextual. The projection function should reflect that.

### Judea Pearl: On Formal Representation and d-Separation

I'll be technical here because I think clarity demands it. Kirsh's core claim is that computational systems must maintain dual representations: one for epistemic uncertainty (about causal relationships), one for aleatory uncertainty (about outcomes given causal knowledge). This resonates with my framework, where we distinguish three levels: association (observational), intervention (experimental), and counterfactual (modal). But the implementation matters.

In structural causal models, the separation is mathematically clean. A causal model M is a tuple (U, V, F), where U are exogenous variables (aleatory), V are endogenous variables, and F are functional relationships (epistemic). Once M is specified, I can compute any causal quantity using do-calculus. The distinction between epistemic and aleatory maps onto this structure: epistemic uncertainty is about M; aleatory uncertainty is about the values of U given M.

Kirsh's projection function needs analogous rigor. He describes it informally: it takes warrant types, assigns discount factors, and produces a Bayesian network. But what's missing?

First, the independence structure. In a Bayesian network, d-separation encodes conditional independence. If the projection function simply concatenates beliefs from the Web of Belief into CPT entries, does it preserve d-separation? For instance, if in the Web of Belief I'm uncertain about whether X causes Y, and that uncertainty is independent of my uncertainty about Z, does the projection function preserve that independence in the Bayesian network? If not, the resulting network will make false predictions.

Second, the semantics of the discount factors. Kirsh proposes that different warrant types receive different "discount" when translating to aleatory uncertainty. But a discount to what? If the warrant is weak, do I assign a higher variance to my prior on the causal parameter? Do I add a mixture component reflecting my uncertainty? The paper is vague here, and vagueness in Bayesian specification is a bug, not a feature.

Third, identifiability. Once the projection is complete and I have a Bayesian network, can I recover the original epistemic warrant structure? Or is information lost? If information is lost, how do I know the projection is faithful? Pearl's do-calculus has a theorem: you can recover causal effects from observational data given a causal graph. Does Kirsh's projection have an analogous completeness result?

I suspect the answers are: (a) not automatically, (b) it's underspecified, and (c) no completeness theorem is offered. That's not damning—the engineering question is whether the system works in practice. But if we're making a philosophical claim about necessity (that dual architecture is necessary to properly separate the uncertainties), we need formal guarantees.

The 5-step protocol is sensible as engineering. But it's not a substitute for a formal model. I'd want to see the projection function defined mathematically, the preservation of independence properties proven, and the completeness question addressed.

### Armen Der Kiureghian: On Pragmatism and Modelability

Let me reframe Kirsh's contribution from my pragmatic perspective, and then identify where I think it goes beyond what's sustainable. The distinction between epistemic and aleatory uncertainty is model-relative. Given a model M, some uncertainties are aleatory (inherent randomness in the system) and some are epistemic (our ignorance about M itself—parameters, structure, inputs). Once we advance the model to M', some formerly epistemic uncertainties may become aleatory, and vice versa.

Kirsh embraces this. He's not claiming the distinction is metaphysical; he's saying: within a computational system instantiating a particular model, here's how to organize the two types. That's pragmatic and sensible.

The ATLAS system does this by maintaining a Web of Belief (roughly, the epistemic layer) and a Bayesian Network (roughly, the aleatory layer given that belief). The separation is functional, not ontological. I appreciate this deeply.

But there's a catch. Kirsh seems to think the separation is stable—that once you've correctly identified which uncertainties are epistemic, you can translate them cleanly into aleatory uncertainty via the projection function. My experience in engineering says this is optimistic. Here's why:

First, the mapping from epistemic uncertainty to prior distribution is underdetermined. Suppose I'm epistemically uncertain about a parameter θ. How uncertain? I might express this as a prior p(θ). But p(θ) encodes my state of knowledge only under the assumption that I've thought through all relevant considerations. In practice, epistemic uncertainty about θ often masks epistemic uncertainty about what factors influence θ. I'm using a prior that assumes I've correctly identified the model structure. But maybe I haven't. Maybe there's a hidden confounder.

Second, the discount factors on warrant types lack justification. Kirsh says different warrant types get different weights. But what's the basis? Is it empirical (different warrant types predict differently in historical data)? Theoretical (different warrant types have different epistemic closure properties)? Arbitrary (they just happen to work in the ATLAS system)? The paper doesn't say. Without a principled basis, the discount factors are just tuning knobs. And systems with tuning knobs can fit anything.

Third, the assumption that epistemic uncertainty reduces monotonically. Kirsh seems to assume that as you gather more warrant, epistemic uncertainty declines. But that's not always true. Learning new evidence can increase epistemic uncertainty if the evidence reveals the model structure is more complex than you thought. The projection function needs to accommodate uncertainty growth, not just decline.

My recommendation: operationalize this more carefully. Show how the discount factors are calibrated in actual systems. Show how the projection function behaves when new evidence suggests model misspecification. Show how the Web of Belief and Bayesian Network interact when updating occurs. That's where the real engineering challenge lies.

### Sarah Moss: On Interleaving and Knowledge Attribution

I want to challenge Kirsh's treatment of interleaving directly. In "Probabilistic Knowledge," I argued that knowledge doesn't require certainty; probabilistic belief can constitute knowledge when it's responsive to evidence and properly supported. Importantly, this means epistemic and aleatory uncertainty aren't cleanly separable. When you know a probabilistic claim (e.g., "This coin has a 50% chance of heads"), that knowledge is partly about what the mechanism is (what makes it 50%?) and partly about outcome frequency given that mechanism.

Kirsh's architecture tries to separate these. The Web of Belief tracks your beliefs about mechanisms; the Bayesian Network tracks outcome frequencies given those beliefs. But that assumes the two can be independently specified. They can't be. Your belief about the frequency (aleatory uncertainty) is partly constituted by your belief about the mechanism (epistemic uncertainty).

Consider the environmental psychology example again. Kirsh says you have mechanistic warrant for "daylight affects serotonin production" and historical warrant for "seasonal mood changes." These are epistemic uncertainties. Then he says you translate these into aleatory uncertainty by specifying the strength of the relationship via a CPT.

But here's the problem: your CPT entry for the strength of the daylight-serotonin relationship already encodes a belief about the mechanism. When you say P(serotonin high | daylight high) = 0.8, you're committing to a claim about how reliably the mechanism operates. That's not purely aleatory; it's mechanistic. You can't separate mechanism-belief from frequency-belief because frequency-belief is itself a mechanistic claim about how often the mechanism manifests.

Kirsh might respond: the projection function is designed to handle exactly this. It takes mechanism-beliefs and generates frequency-beliefs. But if mechanism-beliefs and frequency-beliefs are interleaved, the projection function can't be a clean translation. It's more like a coherence revision procedure where both systems update together to maintain consistency.

What I want Kirsh to address: does the ATLAS system update both the Web of Belief and the Bayesian Network together when new evidence arrives? Or does it treat them as independent? If the former, the claimed separation is merely architectural, not fundamental. If the latter, it risks incoherence when beliefs conflict across the two systems.

A concrete suggestion: add a section on "Interleaving and Belief Revision." Show how ATLAS would update when evidence reveals that the mechanistic warrant was wrong (the serotonin-mood pathway is weaker than experts thought) or that the frequency relationship was wrong (mood changes don't correlate with daylight as strongly as historical data suggested). How does the system maintain consistency across both representations?

### Paul Thagard: On Explanation and Coherence Integration

Kirsh identifies a real problem: computational systems conflate epistemic and aleatory uncertainty. His solution is architectural—separate the knowledge sources into two systems. But he doesn't ask whether this separation should be coupled with a coherence mechanism that keeps the two systems aligned.

Here's the issue: explaining something—understanding why a mechanism produces an effect—requires more than listing probabilistic relationships. It requires showing that the explanation coheres with background knowledge, alternative explanations, and observational evidence. My ECHO system was built on this insight. Beliefs (including causal/mechanistic beliefs) are evaluated not just on whether they have strong evidence, but on whether they cohere with other beliefs.

Kirsh's Web of Belief component could incorporate coherence reasoning. When you specify mechanistic warrant for "daylight → serotonin → mood," are you claiming this is the best explanation given the evidence? If so, you should be comparing it to alternative mechanistic explanations (e.g., "seasonal changes in activity → serotonin," "light wavelengths → vitamin D → mood"). The warrant types don't address how to arbitrate among competing mechanistic explanations.

Similarly, when you specify a prior in the Bayesian Network, you're making an explanatory claim about how often the mechanism manifests. That prior should cohere with mechanistic understanding from the Web of Belief. If there's tension—if the mechanism is well-understood but the frequency is unexpected—that's a signal that something is wrong with the model.

I'm not saying coherence is everything. Some beliefs aren't easily coherence-evaluated (e.g., initial priors based on reference classes). But the paper treats coherence as absent from the framework, which seems like a missed opportunity.

Concretely: integrate a coherence checker into the projection function. After translating from mechanistic belief to probabilistic specification, ask: does this probability assignment cohere with how the mechanism is understood? If not, flag the tension. This would add a consistency-checking layer that could improve model calibration.

Also, address belief revision dynamically. The paper presents the CPT elicitation protocol as a one-time procedure. But actual reasoning is iterative. When new evidence arrives, the system should update both mechanistic beliefs and probabilistic beliefs, with coherence serving as the integrating principle. How would ATLAS handle that?

### Andrea Saltelli: On Empirical Calibration and Discount Factors

I'm going to push hard here because I've watched too many models overstate their confidence. Kirsh proposes that different warrant types receive different discount factors when translating epistemic to aleatory uncertainty. That's a clever idea. But it's only as good as the discount factors themselves. And I don't see empirical calibration anywhere in this paper.

Here's what I mean. Suppose you assign a discount factor of 0.7 to "mechanistic warrant"—meaning you're 30% less confident in a causal relationship when you have only mechanistic warrant (vs. experimental warrant). Where does 0.7 come from? Is it based on historical data showing that expert-estimated mechanisms are wrong 30% of the time? Is it based on theoretical reasoning about how reliably we can infer mechanisms from description? Is it just a number Kirsh picked?

The paper doesn't say. And that's a huge problem. Because if the discount factors are arbitrary, the entire projection function is arbitrary. You could have chosen 0.5, or 0.8, and gotten different answers. The system would still feel rigorous, but it would be theater.

Here's my challenge: present data showing how well the discount factors actually predict forecast errors. Take a corpus of prior estimates (made using Kirsh's warrant types and discount factors) and compare them to subsequent data. Do the systems with weak warrant (high discount) really forecast worse than those with strong warrant (low discount)? By how much? Do the differences match the discount factors you chose?

I suspect they don't. I suspect the discount factors are calibrated to make the system feel plausible, not to reflect real epistemic versus aleatory relationships.

Moreover, the paper doesn't address the curse of dimensionality in uncertainty quantification. You're now specifying multiple dimensions: warrant types, discount factors, prior distributions over parameters, aleatory uncertainty within the CPT. Each adds degrees of freedom. Without empirical calibration, you're at risk of fitting the model to noise rather than signal.

My specific recommendations: (1) Conduct a validation study. Use ATLAS on a test dataset where ground truth is known. Compare forecast accuracy against alternatives (standard Bayesian, fully expert elicited, etc.). (2) Present the discount factors with confidence intervals showing historical variation. (3) Conduct sensitivity analysis showing how the projection function output changes when discount factors vary. (4) Discuss how to detect and correct for model overconfidence.

Until you do these things, the discount factors are just decorations.

### James Woodward: On Interventionist Semantics and Projection Fidelity

I want to focus on whether Kirsh's framework properly captures interventionist causal semantics. In my account, to say "X causes Y" is to say that if you intervened to change X, Y would change in a systematic way. That's the mark of causation. Without this interventionist interpretation, you're conflating causation with mere association.

Kirsh's bridge warrant types partly track this. "Direct experimental warrant" suggests evidence from intervention. "Mechanistic warrant" suggests understanding of the causal mechanism. But the paper doesn't make explicit what the warrant types are warrants for. Are they warrants for causal claims (which, on my view, are claims about intervention outcomes)? Or are they warrants for associational claims?

The 5-step CPT elicitation protocol asks experts to estimate relationships. But from an interventionist standpoint, the crucial question is: do these relationships hold under intervention, or only under observation? A causal claim requires intervention-robustness. An observational association is not a causal claim.

Here's my worry: the projection function might be washing out interventionist information. When you translate from the Web of Belief (which may include interventionist causal claims) to the Bayesian Network (which represents probabilistic relationships), you might lose information about what would happen under intervention.

Consider a simple example. You believe that increasing marketing spend causes increased sales (interventionist claim). You also observe that sales and marketing spend are correlated. These are two sources of epistemic warrant. But they point in the same direction only if the causal mechanism is robust. If, in fact, successful firms increase both marketing and sales due to increased profit, then the observational warrant is confounded. The interventionist causal claim and the observational associational claim diverge.

Kirsh's warrant types don't clearly distinguish these cases. An "observational warrant" for a correlation is different from an experimental warrant for a causal effect. The projection function needs to handle this. Does it? The paper doesn't say.

Concretely, I'd recommend: (1) Make explicit that epistemic uncertainty in the Web of Belief concerns causal claims under intervention. (2) Distinguish warrant types by whether they support interventional vs. purely observational claims. (3) Show how the projection function preserves or transforms interventional information. (4) Discuss confounding explicitly—when observational warrants might be confounded and why that requires experimental warrant to resolve.

Without this, the system might produce probabilities that look right statistically but are wrong causal-semantically.

### Craig Fox: On Psychological Reality and Empirical Testing

I'll end this round with a direct empirical challenge. Ülkümen and I have shown people distinguish epistemic from aleatory uncertainty in their judgments. But we've also found that the distinction is fragile, context-dependent, and not always cognitively recoverable. Kirsh's warrant types are theoretically elegant. But are they psychologically real? Do people actually reason with these categories?

Here's what I'd want to see: an experiment where participants are given information about a causal relationship presented as one of Kirsh's warrant types (direct experimental, mechanistic, consensus, etc.). Do participants' belief updates differ depending on warrant type? Specifically, do they display less confidence when warrant is mechanistic (vs. experimental)? Do they adjust beliefs more when warrant is direct experimental?

My hypothesis: they won't, or only weakly. Here's why. People are somewhat (not fully) attuned to the epistemic-aleatory distinction, but they're not naturally carving beliefs into warrant-type categories. When people learn that "experts agree the effect is present," that's warrant. But whether they code it as "consensus warrant" or "mechanistic warrant" or "observational warrant" depends on how the information is framed, what alternatives are available, and what cognitive resources they're using. The categories are analyst-friendly, not necessarily mind-friendly.

This doesn't doom the project. ATLAS might be useful as a prescriptive model (here's how rational agents should reason) even if it's not descriptive (here's how people actually reason). But the paper seems to claim both. The environmental psychology examples suggest that real people do distinguish epistemic and aleatory uncertainty in their reasoning about daylight and mood. That's an empirical claim, and it needs empirical support.

Concretely, I'd recommend: (1) Design an experiment where participants are presented causal information via different warrant types. (2) Measure whether their belief updates and confidence match Kirsh's discount factor predictions. (3) Repeat across multiple causal domains. (4) Discuss implications for whether ATLAS is descriptive, prescriptive, or hybrid.

---

## ROUND 3: CROSS-PANEL DEBATE

**MODERATOR:** Let's open the floor for cross-panel dialogue. Pearl, you wanted to push back on Cartwright's concern about nomological machines?

**PEARL:** Yes. Nancy is right that warrant types alone don't establish that a causal capacity exists. You need intervention, not just description. But I think she's conflating a metaphysical question (does the capacity really exist?) with an epistemological question (do we have sufficient evidence to claim it exists?). Kirsh is addressing the latter. The projection function asks: given warrant of type W, what probability should I assign to the causal claim? That's not a metaphysical question; it's a question about rational belief revision. Cartwright seems to want the system to guarantee that weak warrants don't lead to overconfident causal claims. But that's what the discount factors are for! A mechanistic warrant gets a lower discount (higher epistemic uncertainty carried forward), so the resulting prior is less confident. Nancy, are you saying even that isn't enough?

**CARTWRIGHT:** I'm saying it's not enough because you're still treating all warrants as commensurable. They're not. An experimental warrant doesn't just provide more confident belief in a causal claim; it provides a different kind of evidence—evidence that the capacity actually operates. A mechanistic warrant is evidence about how the mechanism works, which is compatible with the capacity never manifesting. They're categorically different, not just quantitatively different. The discount factor approach treats them as quantitative differences in confidence. That misses the category distinction.

**MOSS:** Can I weigh in? Both of you are right, actually. Pearl is right that we need a normative account of belief revision given different evidence. Cartwright is right that different evidence types have different epistemic force. But here's what's missing: Kirsh doesn't address how to rationally combine different warrant types when they conflict. Suppose I have mechanistic warrant for a causal claim but observational warrant against it. How should ATLAS update? The projection function doesn't address this because it treats warrant types additively—they all flow into the same probability space. But warrant types in conflict don't just add; they need to be reconciled. That's an interleaving problem. You can't separate epistemic uncertainty about mechanism from uncertainty about frequency when they pull in different directions.

**PEARL:** That's a good point about conflict. But Sarah, isn't that exactly what a Bayesian network is designed to handle? If I have conflicting evidence, I incorporate all of it into my posterior via Bayes' rule. The warrant types feed into priors, and then evidence updates the posterior. Conflict is resolved through the likelihood function. Kirsh's system does this, or at least it's designed to.

**MOSS:** Yes, but only if the Web of Belief and the Bayesian Network are being updated together. The paper presents them as separate systems with a one-way projection from belief to probability. If they're truly separate, conflict can't be resolved; it can only be ignored in whichever system you happen to be querying. If they're being updated together (which they must be for the system to remain coherent), then the claimed separation is only architectural, not fundamental.

**THAGARD:** This is where coherence comes in. I've been listening to this debate and thinking: you're all describing aspects of what should be a unified coherence-revision process. Nancy wants to maintain category distinctions between warrant types. Pearl wants to integrate conflicting evidence. Sarah wants to update interdependently across mechanistic and frequency beliefs. You're all right, but you need a framework that treats the entire system—Web of Belief, Bayesian Network, warrant types—as a single coherence graph. When new evidence arrives, you revise the entire graph to maximize overall coherence. That's what ECHO does. Maybe ATLAS should do something similar?

**DER KIUREGHIAN:** Paul, I appreciate the coherence idea, but from an engineering standpoint, it's computationally expensive. If you're trying to build a system that can handle real-world models with hundreds of variables and complex dependencies, you need tractable algorithms. Bayesian networks are tractable (given reasonable structure). Coherence maximization over all beliefs simultaneously is not. Kirsh's architectural separation—Web of Belief separated from Bayesian Network—might be pragmatically justified precisely because coherence is hard. You get most of the benefits with polynomial rather than exponential computation.

**SALTELLI:** Armen, you're assuming the system is well-calibrated. But I haven't heard any evidence of that. We've been debating how to combine warrant types, whether mechanistic warrant is epistemically different, whether coherence should integrate updates. But we haven't asked: in actual practice, do any of these frameworks get the numbers right? Kirsh's discount factors are mysterious. Pearl's d-separation is elegant but requires knowing the correct causal graph. Coherence-based revision is theoretically appealing but untested. My question is simpler: does ATLAS produce better forecasts than simpler alternatives?

**FOX:** Andrea makes a crucial point, and it's empirical. We've been having a philosophical debate about the nature of epistemic and aleatory uncertainty. But at the end, there's a question about psychology. Do people distinguish these kinds of uncertainty? Do they weight warrant types differently? If so, do the weights match Kirsh's discount factors? That's what matters for whether this system explains actual cognition.

**WOODWARD:** I want to return to the causal-semantics question. Everyone here is assuming we know what a "causal claim" is. But we don't agree on that. I say it's a claim about intervention outcomes. Cartwright says it's a claim about nomological machines and capacities. Pearl has his own formal definition via structural causal models. These aren't just linguistic differences; they affect how you implement the projection function. If causal claims are interventionist (my view), then epistemic uncertainty about causation is uncertainty about intervention outcomes, and you can't separate that from outcome probability as cleanly as Kirsh suggests. If causal claims are about capacities (Nancy's view), then epistemic uncertainty is about whether the capacity exists, which is prior to any probability assignment. Kirsh needs to nail down his semantics. What does it mean to be epistemically uncertain about a causal claim in the ATLAS system?

**CARTWRIGHT:** James is exactly right. And I'd push further: Kirsh treats causal claims as though they have a truth value that's epistemically uncertain but fixed. Either the daylight-serotonin relationship exists or it doesn't, and epistemic uncertainty is just about which. But in my framework, causal claims are context-dependent and capacity-relative. It's not that the relationship exists or doesn't; it's that under certain conditions (certain organisms, times of year, genetic backgrounds), the capacity manifests, and under others, it doesn't. You can't have a single probability assignment to "daylight causes mood" because the claim isn't univocal. You need to track context-sensitivity.

**DER KIUREGHIAN:** Nancy, that's a great philosophical point, and it's why the pragmatic distinction between epistemic and aleatory uncertainty is so important. Once you accept that models are context-relative, you're accepting that the distinction is also relative to the model. The same claim is epistemic in one model (parameter uncertainty) and aleatory in another model (once the parameter is specified). Kirsh's dual architecture could accommodate this by updating the Web of Belief when you realize the model is context-dependent. But the paper doesn't address model revision explicitly.

**MOSS:** Here's a concrete question for Kirsh (if he were here): suppose you're using ATLAS to forecast the mood-daylight relationship for someone new. You have warrant types from the original study population. Does the system update the warrant types or discount factors when you realize the person is from a different geographic location, or has a different genetic profile, or is taking medications that affect serotonin? Or does it assume the warrant is context-invariant? Because if it assumes context-invariance, it's begging the question of external validity. It's not actually learning from context-dependence; it's ignoring it.

**SALTELLI:** And here's where calibration becomes crucial. Suppose ATLAS does update the discount factors for context. Great. But is there evidence that the updated discount factors actually improve forecast accuracy? Or are you just fitting another parameter without gaining explanatory power? This is the curse of over-parameterization. You add the ability to adjust discount factors for context, and suddenly you have dozens of tunable parameters. Without systematic validation, that's not science; it's model building that can fit anything.

**THAGARD:** I'm going to step back and say something the whole panel might agree with: Kirsh has identified a real and important problem. Computational systems do conflate epistemic and aleatory uncertainty. His proposed solution—dual architecture with explicit warrant types and discount factors—is promising. But the execution has gaps. The formal representation is underspecified (Pearl's concern). The causal semantics are unclear (Woodward). The warrant types might not be psychologically real (Fox). The discount factors lack empirical calibration (Saltelli). The system doesn't handle interleaving or model revision (Moss). And there's no coherence mechanism to ensure consistency across the Web of Belief and Bayesian Network (my concern).

None of these are fatal. They're all fixable. But they need to be fixed for the paper to be genuinely strong.

**PEARL:** I agree with Paul's synthesis. And I'd add: the philosophical ambitions need to be scaled back slightly, or the technical machinery needs to be scaled up. Right now, Kirsh is claiming both that the distinction is philosophically necessary (it solves a fundamental problem) and that the ATLAS system operationalizes it (it works in practice). One or both of those claims might be true, but they need more support. Either prove the philosophical claim more rigorously (via formal models), or provide empirical evidence for the practical claim (via validation studies). Trying to do both simultaneously without strong support for either is overambitious.

---

## ROUND 4: WHAT WOULD MAKE THIS PAPER EXCELLENT?

### Nancy Cartwright

My top three recommendations:

First, develop a formal semantics for what causal claims mean in the ATLAS system. Are they claims about capacities (my view), intervention outcomes (Woodward's view), or something else? Once that's clear, show how warrant types map onto evidence for causal claims under that semantics. I suspect you'll find that not all warrant types are equal in the way the paper suggests.

Second, address model revision explicitly. The pragmatic view says the epistemic-aleatory distinction is model-relative. So what happens when evidence suggests the model needs revision? Does ATLAS have a procedure for detecting model misspecification and adjusting the Web of Belief accordingly? If not, add one. This is crucial for real-world application.

Third, include a case study where ATLAS is applied to a moderately complex causal system (not just daylight-serotonin) and shown to produce better forecasts or more transparent reasoning than alternatives. The philosophy is important, but practitioners need proof of concept.

### Judea Pearl

Formalize the projection function. I'm not asking for Euclidean rigor, but I do need:

1. **A mathematical definition** of how warrant types and discount factors map onto prior distributions over causal parameters. Show the mapping explicitly. Discuss whether it preserves independence assumptions.

2. **A completeness result** showing that information lost in the projection is negligible (or characterize what's lost). Alternatively, show that the system remains coherent even with information loss.

3. **Validation against benchmark datasets**. Show that ATLAS's causal inferences match ground truth on at least a few well-studied causal systems. This doesn't need to be comprehensive, but it needs to exist.

If you provide these three things, the philosophical claim becomes stronger because it's backed by formal guarantees.

### Armen Der Kiureghian

Three concrete things:

1. **Calibration study**: Apply ATLAS to historical models where both expert estimates and ground truth are available. Show that the discount factors actually improve forecast accuracy compared to uncorrected expert priors. If they don't, recalibrate them.

2. **Sensitivity analysis**: Show how the system's output (the Bayesian network) varies when discount factors change. Which discount factors matter most? Are there regions where small changes in discount factors cause large changes in the posterior? If so, acknowledge that uncertainty and don't overstate confidence in forecasts.

3. **Context-dependence guidance**: Provide a protocol for updating ATLAS when context changes (different population, different timeframe, different measurement methods, etc.). The pragmatic view thrives on context-sensitivity. Show how ATLAS exploits that.

### Sarah Moss

My recommendations focus on interleaving and knowledge:

1. **Explicit interleaving treatment**: Add a section showing how ATLAS handles cases where mechanistic beliefs and frequency beliefs conflict. Use a concrete example (maybe a case from the literature where expert mechanistic understanding proved wrong after data collection). Show how the system updates. Does it maintain coherence across both representations? If not, discuss why not and whether that's problematic.

2. **Knowledge attribution**: Clarify when ATLAS allows you to claim knowledge of a causal relationship. On my account, probabilistic belief can constitute knowledge if it's responsive to evidence. Does ATLAS's framework accommodate this? Can you say you "know" a causal relationship is 80% likely if you have strong empirical warrant? Or is knowledge reserved for higher confidence? Being clear on this matters for how the system is interpreted.

3. **Comparative analysis**: Compare ATLAS to alternatives (full Bayesian, coherence-based revision, ensemble methods). When does ATLAS outperform? When does it struggle? This helps readers understand what the system is good for and what its limitations are.

### Paul Thagard

1. **Integrate coherence checking**: After the projection function generates a Bayesian network, run a coherence checker. Ask: do the probabilities cohere with the mechanistic understanding in the Web of Belief? If not, flag the incoherence and suggest revisions. This wouldn't require solving the full coherence problem, just identifying tensions.

2. **Dynamic belief revision**: The CPT elicitation protocol is static. Real reasoning is dynamic. Show how ATLAS updates both the Web of Belief and the Bayesian Network when new evidence arrives. Describe the procedure and test it on a time-series dataset where evidence arrives sequentially.

3. **Cognitive plausibility discussion**: Address whether the warrant types correspond to how people actually think. Reference psychology of causal reasoning (including Fox's work and others). Even if ATLAS isn't meant to be descriptively accurate, acknowledging whether it is (or isn't) helps readers interpret it correctly.

### Andrea Saltelli

1. **Empirical validation with error bounds**: Test ATLAS on a corpus where ground truth is known. For each forecast, show the confidence interval. Compare forecast accuracy to simpler baselines. Show that ATLAS's uncertainty quantification is reliable—that events assigned 80% confidence actually occur ~80% of the time. Without this, everything else is speculation.

2. **Sensitivity analysis of discount factors**: For each warrant type, show how forecast accuracy varies when the discount factor changes. Identify the optimal values (if any). Discuss whether optimality depends on domain. This helps readers understand how sensitive ATLAS is to its design choices.

3. **Critique of your own method**: Anticipate objections and address them. Where might ATLAS fail? When would simpler methods work as well or better? What are the computational costs? Being honest about limitations builds credibility.

### James Woodward

1. **Formalize interventionist semantics**: Explicitly define what causal claims mean in ATLAS. Are they claims about intervention outcomes? If so, show how warrant types provide evidence for intervention claims specifically (not just associations). Distinguish warrant types that support interventional vs. observational inference.

2. **Confounding analysis**: Discuss explicitly how ATLAS identifies and handles confounding. If an observational warrant suggests a relationship that might be confounded, how does the system respond? What would it take to move from observational to interventional confidence? Concrete examples would help.

3. **Counterfactual reasoning**: Show how ATLAS would answer counterfactual questions ("If I had increased daylight exposure, would mood have improved?"). This tests whether the system preserves causal information in the projection from Web of Belief to Bayesian Network.

### Craig Fox

1. **Psychological experiment**: Design and run an experiment testing whether people's belief updates match the warrant-type dynamics ATLAS proposes. If they don't, discuss implications. If they do, that's a major selling point.

2. **Explicit prescriptive/descriptive positioning**: Be clear about what ATLAS is for. If it's a prescriptive model (how people should reason), frame it that way and compare to how people actually reason. If it's descriptive, provide evidence. If it's hybrid, specify the scope of each.

3. **Uncertainty aversion and framing effects**: Known from decision research that people are sensitive to how uncertainty is framed (Tversky & Kahneman's endowment effect, ambiguity aversion, etc.). How does ATLAS interact with framing? Does it correct for psychological biases, or does it replicate them? Discussing this enriches the paper's relevance to actual decision-making.

---

## ROUND 5: THE BIG QUESTIONS

### Nancy Cartwright

Why should we care? Because science relies on causal inference, and causal inference is much harder than we usually admit. We have regularities (correlations, experimental results), and we want to infer capacities (mechanisms that would produce effects reliably across contexts). That's an enormous inferential leap. Most computational systems blur that leap; they treat regularities and capacities as if they're the same. Kirsh is right that we need to distinguish them.

What hangs on it? Everything in applied science. When an engineer designs a bridge, they need to know not just that certain materials have correlated properties, but that those materials have the capacity to bear load reliably. When a physician prescribes medication, they need to know not just that the medication correlates with recovery, but that the mechanism of action is robust enough to work for this patient. When a policymaker designs an intervention, they need confidence that the causal mechanism will operate in their context, not just in the research lab. ATLAS, if it works, would help automate these distinctions. That's powerful.

How will science change? More carefully. Right now, we publish regularities and call them causal claims, and then we're surprised when they don't replicate across contexts. ATLAS would, at best, force that carefulness into the system from the start. Scientists would have to specify what warrants they have for causal claims, and they'd have to think through whether those warrants track capacities (context-robust) or just regularities (context-sensitive).

Does it make me want to see the ATLAS system? Yes, but with caveats. I want to see it applied to real scientific examples where warrant disputes have occurred. I want to see whether it helps resolve those disputes or just formalizes them differently.

### Judea Pearl

Why should we care? The paper addresses a fundamental gap in computational uncertainty reasoning. For decades, we've had tools for computing probabilities given a known model (Bayesian networks), and we've had intuitions about when models themselves are uncertain (epistemic). But we haven't had a systematic way to translate between them. That gap has caused recurring problems: overconfidence in models, misinterpretation of results, failed replications. Kirsh is pointing at a real architectural problem.

What hangs on it? The ability to build trustworthy AI systems that reason about causation. Right now, machine learning systems can learn associations from data, but they can't learn causal structure reliably because they conflate epistemic uncertainty (about the structure) with aleatory uncertainty (about outcomes). If ATLAS provides a way to separate these at the algorithmic level, that's a game-changer for causal discovery and causal inference in AI.

How will science change? We'll finally have computational tools that match the complexity of causal reasoning in science. Instead of treating all uncertainty uniformly (as Bayesian networks do), we'll be able to maintain explicit distinction between structural/mechanistic uncertainty and outcome uncertainty. That's how human scientists reason, and it's how our computational systems should reason too.

Does it make me want to see the ATLAS system? Absolutely, but formalized. Kirsh's architecture needs mathematical specification. The projection function needs to be defined with the precision of do-calculus or similar formal causal calculi. Once that's done, ATLAS could become a standard tool for causal reasoning in AI.

### Armen Der Kiureghian

Why should we care? Because uncertainty quantification is broken in engineering practice. We assign priors, run models, produce probabilities, and then the probabilities don't match reality. Part of the reason is that we've conflated two different kinds of ignorance: ignorance about parameters we could measure (epistemic) and randomness that's inherent to the system (aleatory). These require different reasoning. ATLAS offers a systematic way to keep them separate.

What hangs on it? Credibility of probabilistic design in engineering. Right now, engineers use probabilistic risk assessment, but the public doesn't trust it because uncertainty quantification feels arbitrary. If ATLAS provides a principled way to specify where probabilities come from—which warrant types justify them—that builds trust. We can explain to a skeptical public: "We're assigning this probability because we have this warrant."

How will science change? Uncertainty quantification becomes more transparent and more justified. Instead of hiding assumptions in prior specifications, we make them explicit via warrant types. That's a huge methodological advance.

Does it make me want to see the ATLAS system? Yes, but applied to real engineering problems. Apply it to structural reliability (predicting bridge failure), to geotechnical uncertainty (predicting soil properties), to climate modeling (separating model uncertainty from inherent variability). If ATLAS can improve forecasts in these domains, it's transformative.

### Sarah Moss

Why should we care? Because epistemology has been stuck on a crude dichotomy: either you know something (certain) or you don't know it (uncertain). But most of what we actually know is probabilistic. I can know a causal claim to degree 0.8, and that can constitute genuine knowledge if I have good evidence for it. ATLAS treats this seriously. It doesn't collapse epistemic uncertainty into aleatory uncertainty; it respects probabilistic knowledge.

What hangs on it? The possibility of a sophisticated account of scientific knowledge. Instead of asking whether a causal claim is true or false, we can ask: what's the warranted degree of confidence in this claim? And what kind of warrant is that confidence based on? That's a more realistic epistemology for science, which deals in probabilities, not certainties.

How will science change? We'll move away from binary hypothesis testing (reject H0 or don't) toward more nuanced epistemic assessment. Science would openly acknowledge that causal knowledge comes in degrees and kinds, depending on warrant.

Does it make me want to see the ATLAS system? Absolutely. But I want to see it handle interleaving—cases where you have conflicting warrants pulling in different directions. Real science is like that. You have experimental evidence pointing one way and mechanistic understanding pointing another. How does ATLAS resolve that without losing information? That's the test.

### Paul Thagard

Why should we care? Because understanding—genuine comprehension of how things work—requires more than probability assignment. It requires seeing how different pieces of knowledge cohere. When you understand why daylight affects mood, you're not just believing the probabilities; you're grasping how multiple pieces of evidence fit together into a coherent picture. ATLAS doesn't explicitly address coherence, but it could. And if it did, it would be much more powerful.

What hangs on it? The possibility of computational systems that achieve genuine understanding, not just accurate prediction. Machine learning systems are good at prediction but weak at understanding. ATLAS's dual architecture is a step toward understanding because it maintains explicit mechanistic knowledge. But without coherence integration, it's still incomplete.

How will science change? We'd build better AI systems for scientific discovery. Right now, AI systems can find patterns in data but can't explain them (or explain them poorly). ATLAS-like systems that maintain rich mechanistic knowledge and cohere it with statistical evidence could automate the kind of scientific reasoning that humans do implicitly.

Does it make me want to see the ATLAS system? Yes, and particularly with coherence integration. Show me that it can maintain consistent understanding across multiple domains, updating both mechanistic knowledge and probabilistic beliefs when new evidence arrives. That would be impressive.

### Andrea Saltelli

Why should we care? Because we're drowning in model uncertainty, and nobody's quite honest about it. We build complex models, assign parameters based on expert judgment, and then pretend the resulting probability distributions mean something. ATLAS could help by forcing us to be explicit about where our confidence comes from. That's a step toward intellectual honesty.

What hangs on it? The credibility of quantitative science. If we can show that our uncertainty quantifications are principled, calibrated, and validated, the public might trust science more. If ATLAS helps automate that transparency, it's valuable.

How will science change? Slower, more careful. Not in a bad way. Right now, we often overstate confidence because we haven't properly accounted for epistemic uncertainty. If ATLAS forces us to separate epistemic from aleatory uncertainty, we'll publish lower confidence bounds. That's uncomfortable but necessary.

Does it make me want to see the ATLAS system? Only if it's validated. Show me data. Show me that systems using ATLAS make better predictions with better-calibrated uncertainty than alternatives. Until then, I'm skeptical. But I'm open to being convinced.

### James Woodward

Why should we care? Because causal reasoning is ubiquitous in science and policy, and we've never had a really satisfactory account of how it should work. The distinction between epistemic uncertainty (about causal mechanisms) and aleatory uncertainty (about outcomes) mirrors the distinction between causal claims and frequency claims. Kirsh is pointing at something real.

What hangs on it? The possibility of principled causal inference in the presence of uncertainty. Right now, we do causal inference (via RCTs, instrumental variables, etc.), but we don't have a unified account of how to handle cases where we're uncertain about the causal structure itself. ATLAS offers one possible account.

How will science change? More careful about when causal claims are justified. We'd openly acknowledge uncertainty about causal mechanisms and distinguish it from uncertainty about outcomes. That's how science should work.

Does it make me want to see the ATLAS system? Yes. But I want to see it explicitly framed in interventionist terms. Show me how warrant types provide evidence for interventional claims. Show me that the projection function preserves or appropriately transforms intervention semantics. Do that, and the system becomes genuinely useful for causal science.

### Craig Fox

Why should we care? Because the evidence is clear that people distinguish epistemic from aleatory uncertainty in their thinking, but we don't know exactly how. Understanding ATLAS might help us understand human causal reasoning better. That's intrinsically interesting and practically important if we want to design better decision support systems.

What hangs on it? The design of human-AI collaborative systems. If ATLAS properly captures how people think about causal uncertainty, we can build interfaces that align with human cognition. If it doesn't, we should know that too and adjust our systems accordingly.

How will science change? We'd pay more attention to uncertainty cognition in experimental design and data communication. Right now, we treat uncertainty as a statistical property of numbers. But it's also a psychological property of beliefs. ATLAS reminds us that both matter.

Does it make me want to see the ATLAS system? Yes, and particularly with empirical psychology integrated. Validate the system against human judgment. If it predicts how people should and do think about causal uncertainty, that's genuinely valuable for cognitive science and decision science both.

---

## SYNTHESIS: Actionable Recommendations

Based on this panel discussion, here are the highest-priority improvements to strengthen the paper:

### Priority 1: Formal Specification (Essential)

The projection function must be defined mathematically. Specifically:
- Provide an explicit mathematical mapping from warrant types + discount factors to prior distributions over causal parameters.
- Prove (or characterize) what properties are preserved (e.g., independence structure, causal interpretation).
- Compare the formal properties to existing causal frameworks (structural causal models, Bayesian networks with latent variables).
- *Owner:* Pearl's recommendations

### Priority 2: Empirical Validation (Essential)

The discount factors must be calibrated against historical data. Specifically:
- Conduct a validation study using archival data where expert estimates (made using warrant types) can be compared to ground truth.
- Compute calibration curves showing whether events assigned 80% confidence actually occur ~80% of the time.
- Compare forecast accuracy to simpler baselines (uncorrected expert priors, fully Bayesian, ensemble methods).
- If discount factors don't perform as expected, recalibrate them or acknowledge their limitations.
- *Owner:* Saltelli's recommendations

### Priority 3: Semantic Clarity (Essential)

The paper must specify what counts as a "causal claim" in ATLAS. Specifically:
- Choose a causal semantics (interventionist à la Woodward, capacity-based à la Cartwright, or structural causal model à la Pearl) and state it explicitly.
- Show how warrant types provide evidence for causal claims under that semantics.
- Discuss whether different warrant types support interventional vs. purely observational inference.
- Explain how the system distinguishes between genuine causal mechanisms and mere associations that might be confounded.
- *Owners:* Woodward and Cartwright's recommendations

### Priority 4: Interleaving and Coherence (High Priority)

The paper should address cases where mechanistic and frequency beliefs conflict. Specifically:
- Provide a detailed example where mechanistic warrant and observational warrant point in different directions. Show how ATLAS updates and resolves the conflict.
- Either incorporate a coherence mechanism that ensures consistency across the Web of Belief and Bayesian Network, or explain why the separation is maintained even when evidence conflicts.
- Discuss whether both systems update simultaneously or in sequence, and why.
- *Owners:* Moss and Thagard's recommendations

### Priority 5: Psychological Reality (High Priority)

The paper should clarify whether warrant types are descriptive or prescriptive. Specifically:
- Run at least one experiment showing whether people's belief updates match ATLAS's predictions when given information via different warrant types.
- If the match is strong, claim psychological validity with caveats about context-dependence. If weak, reframe ATLAS as a normative system (how people should reason) rather than descriptive (how they do).
- Reference existing work on uncertainty cognition (including Fox & Ülkümen's distinction between epistemic and aleatory uncertainty in judgment).
- *Owner:* Fox's recommendations

### Priority 6: Model Revision (Medium Priority)

The paper should address what happens when the model itself is questioned. Specifically:
- Provide a protocol for updating the Web of Belief when evidence suggests model misspecification (e.g., discovering a confounder, finding context-dependence).
- Discuss whether discount factors should adjust when applied to new populations or contexts.
- Include a case study where ATLAS detects and responds to model revision.
- *Owner:* Der Kiureghian's recommendations

### Priority 7: Case Studies and Proof of Concept (Medium Priority)

The paper should apply ATLAS to moderately complex systems beyond the daylight-serotonin example. Specifically:
- Choose 2-3 real causal systems from the literature (possibly from fields where warrant disputes have occurred).
- Show how ATLAS would operationalize the reasoning about those systems.
- Ideally, compare ATLAS's inferences to ground truth or expert consensus.
- *Owners:* Cartwright and Der Kiureghian's recommendations

### Priority 8: Comparative Analysis (Lower Priority)

The paper should situate ATLAS relative to competing approaches. Specifically:
- Compare explicitly to structural causal models (Pearl), coherence-based belief revision (Thagard), and alternative frameworks for handling epistemic uncertainty.
- For each comparison, identify the advantages and disadvantages of ATLAS relative to alternatives.
- Discuss when ATLAS would be preferred over simpler methods and when it would be overkill.
- *Owner:* Moss's recommendations

### Priority 9: Limitation and Failure Modes (Lower Priority)

The paper should honestly address where ATLAS struggles. Specifically:
- Identify causal systems where the dual architecture would be inadequate or unnecessary.
- Discuss computational costs and scalability limits.
- Discuss cases where the warrant types don't naturally apply or where warrant is unavailable.
- *Owner:* Saltelli's recommendations

### Priority 10: Clarity of Presentation (Ongoing)

Finally, across all recommendations:
- Use concrete, worked examples liberally. The daylight-serotonin example is good; more would help.
- Define all technical terms before use. Concepts like "discount factor," "bridge warrant," and "projection function" need intuitive explanation before formal definition.
- Make the motivation (why this problem matters) explicit in the introduction and repeated throughout.
- End with a vision: if ATLAS works as intended, how will computational reasoning about causal systems change?

---

## Conclusion

This panel has identified a genuinely important problem: computational systems do conflate epistemic and aleatory uncertainty, and this conflation causes both theoretical confusion and practical errors. David Kirsh's proposed solution—the dual architecture of ATLAS with explicit warrant types and a principled projection function—is intellectually sophisticated and potentially transformative.

However, the paper is not yet ready for publication in its current form. The three essential gaps (formal specification, empirical validation, semantic clarity) must be addressed. The other recommendations would strengthen the work considerably and address concerns from leading scholars in philosophy of science, computer science, statistics, psychology, and engineering.

If Kirsh addresses these recommendations, the paper will make a significant contribution to how we think about computational reasoning under uncertainty. The intellectual payoff is substantial: better understanding of how causal knowledge differs from frequency knowledge, more principled systems for handling both, and more transparent science that openly acknowledges different types of uncertainty and their sources.

The panel is optimistic about the work's potential and eager to see the strengthened version.
