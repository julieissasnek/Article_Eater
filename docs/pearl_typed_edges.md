**Addressing Pearl:**

**Why Typed Edges Are Not Ornamental**

*The Information That Structural Causal Models Deliberately Discard*

*and Why It Matters for Cross-Context Transfer*

David Kirsh

Department of Cognitive Science, UC San Diego

February 2026

**1. The Elegance of Pearl's Deliberate Amnesia**

Judea Pearl's Structural Causal Model (SCM) framework is one of the
great intellectual achievements of late twentieth-century science. It
took the nebulous concept of causation---tangled for centuries in
philosophical dispute, banished from respectable statistics by the
positivist tradition that ran from Pearson through Fisher---and gave it
a rigorous mathematical foundation. The SCM framework provides a compact
notation (structural equations), a graphical representation (directed
acyclic graphs), a formal semantics for intervention (the do-calculus),
and a hierarchy of causal reasoning (the Pearl Causal Hierarchy, or
"ladder of causation": association, intervention, counterfactual). It
is, by any reasonable measure, a triumph of formalization.

But every triumph of formalization involves a decision about what to
formalize and what to discard. The power of Pearl's framework comes
precisely from its willingness to strip away information that it deems
irrelevant to the computational task at hand. A structural equation Y =
f(X, U) says that Y is determined by X and exogenous noise U through
some function f. It does not say why this relationship holds. It does
not say what kind of evidence established it. It does not say whether f
was discovered through randomized experiment, observational correlation,
mechanistic theory, analogy from another domain, or expert stipulation.
The structural equation is epistemically anonymous: the provenance of
the causal claim has been deliberately discarded.

This amnesia is not a bug. It is the central design decision that makes
the framework tractable. Pearl recognized that for the purposes of
computing causal effects---answering questions like "What is P(Y \| do(X
= x))?"---you do not need to know how you came to believe that X causes
Y. You need only the structural equation and the graph. Once the causal
structure is specified, the do-calculus can derive interventional and
counterfactual distributions without ever consulting the evidence that
established the structure. This is an enormous computational advantage.
It is what allows Pearl's framework to scale to complex systems with
dozens of variables and to provide mathematically guaranteed
identification results.

The question we address in this paper is: what is lost in this
deliberate amnesia? And does what is lost matter for the specific
problem that the ATLAS system confronts---the problem of transferring
laboratory findings from environmental psychology to real-world
architectural applications?

Our answer is: yes, profoundly. What Pearl discards is exactly what the
Epistemic Warrant Graph preserves. And what the EWG preserves is exactly
what you need for responsible cross-context transfer.

**2. Pearl's Likely Objection: Typed Edges as Unnecessary Complexity**

Let us construct Pearl's objection as charitably and precisely as we
can. Pearl would likely say something like this:

> *"A causal relationship is a causal relationship. The structural
> equation Y = f(X, U) makes a precise claim: Y is a function of X and
> noise. Whether this claim was established by experiment, by
> observation, by mechanism, or by analogy is irrelevant to the
> computation of causal effects. Once the graph is drawn and the
> structural equations specified, the do-calculus tells you everything
> you need to know about interventions. Attaching labels to
> edges---calling one 'MECHANISM' and another
> 'EMPIRICAL\_COVARIANCE'---adds complexity without adding computational
> power. The Bayesian Network produced by your projection function π is
> a standard BN. My do-calculus already handles it. Your seven warrant
> types are epistemic decoration."*

This objection is powerful because it is largely correct---for the
specific computational task that Pearl's framework was designed to
handle. If your only goal is to compute P(Y \| do(X = x)) given a
specified causal graph, then you do not need typed edges. The
do-calculus is complete for this task (Huang & Valtorta, 2006; Shpitser
& Pearl, 2006). No typed-edge machinery will improve on it.

But the ATLAS system is not trying to compute causal effects from a
given graph. It is trying to do something harder: to construct a graph
in a new context from evidence gathered in other contexts. This is the
problem of cross-context transfer, and it is where Pearl's framework,
for all its power, has a genuine blind spot.

**3. The Cross-Context Transfer Problem: Where Pearl's Amnesia Hurts**

**3.1 The Problem in a Nutshell**

Environmental psychology confronts a specific epistemic challenge that
most applications of causal inference do not. The typical application of
Pearl's framework proceeds as follows: you have a causal graph for a
domain; you have data from that domain; you use the do-calculus to
compute causal effects within that domain. The graph and the data
inhabit the same context. This is what Pearl calls
"identification"---determining whether a causal effect can be computed
from available data given the assumed graph.

The ATLAS system confronts a different problem. The evidence comes from
context A (the laboratory), and the application is in context B (a real
building). The causal graph in context A may not hold in context B. A
mechanism that operates under laboratory conditions (controlled
lighting, uniform populations, short exposure durations) may fail,
attenuate, or reverse under real-world conditions (variable lighting,
diverse populations, chronic exposure). The central question is not "can
we compute the causal effect?" but "should we believe the causal graph
transfers?"

This is the problem that Pearl's framework was not designed to
solve---and it is precisely the problem where typed edges earn their
keep.

**3.2 What Pearl's Framework Can Say About Transfer**

Pearl is not unaware of the transfer problem. His work on
"transportability" (Pearl & Bareinboim, 2011; Bareinboim & Pearl, 2016)
addresses exactly the question of when a causal effect estimated in one
context can be validly transported to another. The key insight of
transportability theory is that transfer is warranted when the causal
mechanisms that differ between contexts can be identified and controlled
for. Pearl introduces "selection diagrams"---DAGs with special "S-nodes"
that mark where the two contexts differ---and derives conditions under
which transport is valid.

This is elegant work. But it has a critical limitation: it assumes you
know which mechanisms differ between contexts. The S-nodes must be
placed by the analyst, based on domain knowledge. Pearl's framework
provides the formal machinery for computing transport given the S-node
placement, but it provides no guidance on where to put the S-nodes in
the first place.

And this is exactly where warrant types become indispensable.

**3.3 What Warrant Types Tell You That Structural Equations Cannot**

Consider a specific causal claim: "Daylight exposure increases serotonin
production." In Pearl's framework, this is represented by a structural
equation S = f(D, U) and an arrow D → S in the causal graph. Full stop.
The structural equation is the same regardless of how we know this.

But the warrant type carries information that is critically relevant to
transfer. Consider the difference:

**If the warrant is MECHANISM** (we know the pathway: photons → retinal
ganglion cells → raphe nuclei → tryptophan hydroxylase → serotonin),
then we know *why* the relationship holds. This has three consequences
for transfer. First, we can predict when the relationship will fail: it
will fail whenever a link in the chain is disrupted (e.g., if the
building's glazing filters out the relevant wavelengths, or if the
population includes individuals on SSRIs that block serotonin reuptake).
Second, we can predict that the relationship will transfer to any
context where the mechanistic chain is intact, even contexts that have
never been studied. Third, we know where to place Pearl's S-nodes in a
transportability analysis: they belong on any variable that differs
between contexts and that participates in the mechanistic chain.

**If the warrant is EMPIRICAL\_COVARIANCE** (we have replicated
correlations between daylight and serotonin, but the pathway is not
established), then we cannot make any of these predictions. We cannot
say when the relationship will fail, because we do not know what
sustains it. We cannot predict transfer to novel contexts, because the
covariance may be mediated by confounders that differ across contexts.
And we have no principled basis for placing S-nodes, because we do not
know which mechanisms to mark as context-sensitive.

**If the warrant is ANALOGICAL** (we know that daylight affects
serotonin in rats, and we are reasoning by analogy to humans), then we
face an additional transfer gap: the analogy between rat neurochemistry
and human neurochemistry might break down in ways that no amount of rat
data can reveal. The S-nodes would need to include every point at which
the rat-to-human analogy might fail---but identifying those points
requires precisely the kind of cross-species mechanistic knowledge that
the analogical warrant does not provide.

**If the warrant is CAPACITY** (we know the human visual system can
detect the relevant wavelengths, and we know the raphe nuclei can
synthesize serotonin, but nobody has connected the two in a building
context), then we are asserting that the causal mechanism could operate
but has not been shown to operate. The transfer is speculative---the
system has the hardware but may not be running the software.

In every case, the structural equation is the same: S = f(D, U). Pearl's
framework treats all four cases identically. But they are not the same.
They differ in their vulnerability to context-dependent failure, in
their predictive power for novel contexts, and in the kind of new
evidence that would strengthen or weaken them. The warrant type carries
information about the robustness of the causal claim to contextual
perturbation---information that Pearl's framework explicitly discards.

**4. The Information-Theoretic Argument: Typed Edges Reduce Posterior
Entropy**

There is a precise information-theoretic way to state why typed edges
matter. Pearl's objection implicitly assumes that the only relevant
uncertainty is uncertainty about causal effects: P(Y \| do(X)). But the
ATLAS system operates in a regime where there is also uncertainty about
whether the graph transfers---what we might call "structural
uncertainty" or "transportability uncertainty."

Let G\_lab be the causal graph established in the laboratory, and let
G\_building be the (unknown) causal graph that holds in the real
building. The question is: how much can we learn about G\_building from
G\_lab? The answer depends on the warrant types.

Define the structural uncertainty H(G\_building \| G\_lab, τ) as the
entropy of the posterior distribution over possible building graphs,
conditional on the lab graph and the warrant types. We claim:

**Claim:** H(G\_building \| G\_lab, τ) \< H(G\_building \| G\_lab) for
any informative assignment of warrant types. That is, knowing the
warrant types reduces structural uncertainty beyond what is achievable
from the graph structure alone.

The argument is straightforward. Knowing that an edge is supported by
MECHANISM evidence tells you that the edge will transfer unless a
specific link in the mechanism is disrupted---a low-probability event
for well-established mechanisms. Knowing that an edge is supported by
EMPIRICAL\_COVARIANCE evidence tells you that the edge may fail to
transfer whenever the confounding structure changes---a
higher-probability event in novel contexts. Knowing that an edge is
supported only by THEORETICAL\_DEFAULT evidence tells you that the edge
is a conjecture with no empirical support---a very high-probability
candidate for transfer failure. Each of these probabilities constrains
the posterior distribution over G\_building, reducing H(G\_building \|
G\_lab, τ) below H(G\_building \| G\_lab).

This is not merely a philosophical point. It has computational
consequences. The discount factors in the projection function π are
precisely the system's encoding of how much structural uncertainty is
reduced by each warrant type. A MECHANISM warrant with d = 0.80
transmits 80% of the deviation from ignorance because mechanistic
knowledge is robust to contextual perturbation. An ANALOGICAL warrant
with d = 0.40 transmits only 40% because analogical knowledge is fragile
across contexts. These are not decorations; they are quantitative
measures of information content for the cross-context transfer problem.

Pearl might respond that this information should be encoded in the
confidence one has in the structural equation itself---that instead of
typing the edge, one should simply assign a lower probability to the
graph containing that edge. This is a reasonable position, but it loses
the structure of the uncertainty. Knowing that an edge might fail
because the mechanism is disrupted is different from knowing that it
might fail because the correlation was confounded, and these two failure
modes call for different remedies (new mechanistic studies vs. new
observational studies in the target context). Collapsing these distinct
failure modes into a single probability over graph structures discards
actionable information.

**5. The Pearl Causal Hierarchy and the Orthogonal Axis of Warrant
Types**

**5.1 Pearl's Vertical Hierarchy**

Pearl's Causal Hierarchy (PCH)---the "ladder of causation" described in
Pearl and Mackenzie (2018) and formalized in Bareinboim, Correa,
Ibeling, and Icard (2022)---organizes causal reasoning into three
levels. Level 1 (Association) concerns observational distributions: P(Y
\| X). Level 2 (Intervention) concerns interventional distributions: P(Y
\| do(X)). Level 3 (Counterfactual) concerns hypothetical distributions:
P(Y\_x \| X = x′, Y = y). The Causal Hierarchy Theorem (CHT) proves that
these levels almost always separate: observational data alone cannot
answer interventional questions, and interventional data alone cannot
answer counterfactual questions. Climbing the ladder requires additional
causal assumptions.

This hierarchy is vertical: it organizes the complexity of the causal
question being asked. It says nothing about the evidential basis for the
causal assumptions being made. A Level 2 question ("What happens if I
install larger windows?") receives the same treatment in Pearl's
framework regardless of whether the causal assumptions rest on
randomized experiments, observational studies, mechanistic models, or
theoretical defaults.

**5.2 The EWG's Horizontal Axis**

The warrant type system introduces an orthogonal axis---what we might
call the evidential provenance axis. This axis does not organize the
complexity of the question; it organizes the quality and character of
the evidence supporting the causal assumptions. It is horizontal where
Pearl's hierarchy is vertical.

The two axes cross-cut each other completely. Any warrant type can
support causal assumptions at any level of Pearl's hierarchy. A
MECHANISM warrant can support a Level 1 claim (the mechanism predicts an
observed association), a Level 2 claim (the mechanism predicts what will
happen under intervention), or a Level 3 claim (the mechanism predicts
what would have happened had conditions been different). Similarly, an
EMPIRICAL\_COVARIANCE warrant supports Level 1 claims directly and Level
2 claims only with additional assumptions (no unmeasured confounders).
An ANALOGICAL warrant provides weak support at all three levels.

This orthogonality is the key to the argument. The warrant types do not
compete with Pearl's hierarchy; they complement it. Pearl's hierarchy
tells you what kind of question you can answer. The warrant types tell
you how much you should trust the answer. Pearl tells you what is
computable given your assumptions. The EWG tells you how robust those
assumptions are likely to be in a new context.

**5.3 The Interaction: Why the Two Axes Together Are More Than Either
Alone**

The interaction between the two axes produces insights that neither can
generate alone. Consider an architect asking: "If I install larger
windows in this hospital, will patients recover faster?" This is a Level
2 (interventional) question in Pearl's hierarchy. Pearl's framework
says: draw the causal graph, specify the structural equations, and
compute P(Recovery \| do(Windows = large)) using the do-calculus. If the
graph is identified, you get a number.

But the architect also needs to know: how much should I trust this
number? The answer depends on the warrant types supporting the causal
graph. If the path from window-size to recovery runs through a MECHANISM
warrant (larger windows → more daylight → serotonin → mood → recovery),
the architect can have moderate confidence that the effect will
replicate in this hospital, because the mechanism is understood and can
be checked (Does this building's glazing transmit the relevant
wavelengths? Are there obstructions to direct sunlight?). If the path
runs through an EMPIRICAL\_COVARIANCE warrant (hospitals with larger
windows show faster recovery in observational studies), the architect
should be more cautious, because the correlation might be confounded by
building age, HVAC quality, or patient socioeconomic status---factors
that may differ in this hospital. If the path runs through an ANALOGICAL
warrant (larger windows improve worker productivity in offices, and we
reason by analogy to patient recovery), the architect should be quite
cautious indeed.

Pearl's framework gives the same answer in all three cases---the
computed causal effect is determined by the structural equations, not by
how those equations were established. The EWG gives different answers,
because it tracks the evidential basis and computes transfer reliability
accordingly. The architect gets not just a number but a reliability
estimate for that number in this specific context, derived from the
types of evidence that support it.

**6. Five Things You Cannot Do Without Typed Edges**

To make the argument concrete, we identify five specific tasks that the
ATLAS system performs and that Pearl's untyped framework cannot support.

**6.1 Targeted Evidence Acquisition**

When the EWG identifies a claim supported only by weak warrant types
(e.g., ANALOGICAL or THEORETICAL\_DEFAULT), it generates a specific
recommendation for what kind of new evidence would most improve
confidence. A claim supported by ANALOGICAL warrant needs a direct
empirical study in the target domain (to upgrade the warrant to
EMPIRICAL\_COVARIANCE or MECHANISM). A claim supported by
EMPIRICAL\_COVARIANCE needs either a randomized experiment (to address
confounding) or a mechanistic study (to upgrade to MECHANISM). A claim
supported by CAPACITY needs a bridging experiment showing that the
capacity is exercised in practice (to upgrade to FUNCTIONAL or
MECHANISM).

In Pearl's framework, all you know is that the structural equation
exists. You cannot generate these targeted research recommendations
because you do not know what kind of evidence established the equation
in the first place. The untyped framework says "get more data"; the
typed framework says "get this specific kind of data."

**6.2 Differential Sensitivity to New Evidence**

When new evidence arrives, the update to the system should depend on the
type of the existing warrant. If you have a MECHANISM warrant and new
correlational data confirms the prediction, the update should be
modest---the mechanism already explained the correlation. But if you
have only an EMPIRICAL\_COVARIANCE warrant and new mechanistic evidence
identifies the pathway, the update should be substantial---you have
gained explanatory depth that increases transfer reliability. In Pearl's
framework, an update to the conditional probability P(Y \| X) looks the
same regardless of whether the prior was based on mechanism or
correlation. The typed system computes different updates depending on
the evidential interaction between old and new warrants.

**6.3 Confounding Risk Assessment**

The warrant types implicitly encode vulnerability to confounding.
CONSTITUTIVE warrants are immune to confounding (you cannot confound an
identity). MECHANISM warrants are partially protected (the mechanism
identifies the causal pathway, making specific confounders
identifiable). EMPIRICAL\_COVARIANCE warrants are fully vulnerable (any
unmeasured common cause could explain the association). In Pearl's
framework, confounding is addressed through the back-door criterion and
instrumental variables---but these require knowing the complete causal
graph, including unmeasured variables. The warrant types provide a
heuristic confounding risk assessment that is available even when the
complete graph is not known.

**6.4 Explanation and Audit**

When an architect asks "Why does the system recommend larger windows?",
the EWG can provide a Toulminian explanation: "The data show that
daylight increases serotonin production (MECHANISM warrant, based on
Lambert et al., 2002, identifying the retinal-raphe pathway), and that
serotonin elevation improves mood (MECHANISM warrant, based on Aan het
Rot et al., 2009, identifying the 5-HT receptor pathway). The combined
mechanistic chain from daylight to mood has a projected confidence of
0.70." This explanation traces the claim through specific pieces of
evidence of specific types. In Pearl's framework, the explanation would
be: "The structural equation predicts that do(windows = large) increases
P(mood = positive) by 0.20." This is a correct answer to a different
question---it tells you what the model predicts but not why you should
believe the model.

**6.5 Graceful Degradation Under Evidential Challenge**

When a key study is retracted or fails to replicate, the system needs to
update. In the EWG, the impact of the retraction depends on the warrant
type of the affected edge. If a MECHANISM warrant is invalidated (the
proposed pathway does not exist), the claim may still be supported by an
EMPIRICAL\_COVARIANCE warrant (the correlation is still observed),
though with reduced confidence and increased vulnerability to
confounding. If an EMPIRICAL\_COVARIANCE warrant fails (the correlation
does not replicate), a MECHANISM warrant may still support the claim
(the pathway exists, so the effect should occur even if it was not
observed in the failed study---perhaps due to a methodological problem).
The system degrades gracefully because different warrant types provide
independent lines of evidence.

In Pearl's framework, retracting a study means either removing an edge
from the graph (if no other evidence supports it) or leaving it
unchanged (if other evidence supports it). But the system cannot
distinguish between a claim that lost its mechanistic support but
retains correlational support and a claim that lost its correlational
support but retains mechanistic support---two situations that call for
very different responses.

**7. The Deeper Point: Two Kinds of Uncertainty Require Two Kinds of
Structure**

The deepest response to Pearl is that the ATLAS system is built around a
distinction that Pearl's framework deliberately collapses: the
distinction between aleatory and epistemic uncertainty. This
distinction, which Der Kiureghian and Ditlevsen (2009) showed is
fundamental to engineering reliability, maps directly onto the dual
architecture of the system.

Aleatory uncertainty concerns the stochastic variability of
outcomes---the inherent randomness in how people respond to
architectural features. Even in a perfectly understood system, different
individuals will respond differently to daylight. This uncertainty is
irreducible and is properly represented by probability distributions in
a Bayesian Network. Pearl's framework handles this beautifully.

Epistemic uncertainty concerns our ignorance about the causal structure
itself---whether the right variables are in the model, whether the
structural equations have the right form, whether the relationships will
transfer to new contexts. This uncertainty is reducible by gathering new
evidence, and its magnitude depends on the quality and character of
existing evidence. It is this uncertainty that the warrant types encode.

Pearl's framework collapses these two kinds of uncertainty into one:
both are represented as probabilities over model structures (in Bayesian
model averaging) or as error terms in structural equations. This
collapse is deliberate and, for many purposes, harmless. But for the
specific problem of cross-context transfer, it is actively harmful,
because it prevents the system from distinguishing between claims that
are uncertain because the world is noisy (aleatory) and claims that are
uncertain because our evidence is weak (epistemic). The architect needs
to know: is this 0.70 probability uncertain because people genuinely
vary (in which case, the 0.70 is a reliable estimate of a noisy
phenomenon), or is it uncertain because the evidence is analogical
rather than mechanistic (in which case, the 0.70 might be wildly wrong
in a new context)?

The dual architecture of the ATLAS system---the EWG for epistemic
uncertainty, the BN for aleatory uncertainty---exists to preserve this
distinction. The projection function π is the bridge between the two: it
translates epistemic assessments (warrant types, confidence weights)
into aleatory parameters (conditional probabilities). The typed edges
live in the epistemic layer and carry information that the aleatory
layer cannot represent. Removing them---collapsing the dual architecture
into a single BN---would destroy the distinction between aleatory and
epistemic uncertainty, which is the very distinction that makes
responsible evidence-based design possible.

**8. Warrant Types as Operationalizations of Woodward's Invariance
Conditions**

**8.1 Woodward's Key Insight: Not All Causal Relationships Are Equally
Stable**

James Woodward's interventionist account of causation provides an
independent philosophical argument for why typed edges are necessary,
one that complements the information-theoretic argument of Section 4 and
cuts to the heart of Pearl's framework from within. Woodward's central
contribution---developed across a series of landmark publications
(Woodward, 1997, 2000, 2003, 2010)---is the concept of invariance: a
causal generalization is invariant to the extent that it continues to
hold under changes in background conditions and interventions on the
cause variable.

The crucial point is that invariance comes in degrees. Woodward is
explicit about this. Some causal relationships are highly invariant:
they hold under a wide range of background conditions and survive many
kinds of perturbation. The relationship between gravitational force and
mass is invariant across virtually all earthly contexts. Other causal
relationships are fragile: they hold under narrow conditions and
collapse when background factors shift. The relationship between a
particular teaching method and student performance may hold in one
cultural context and fail in another. Woodward argues that the degree of
invariance is not merely an empirical curiosity but a fundamental
feature of the causal relationship itself, one that determines its
explanatory depth and its usefulness for prediction and control
(Woodward, 2000, 2003, 2010).

Pearl's framework represents both relationships identically: as arrows
in a DAG with structural equations. The arrow from "mass" to
"gravitatonal force" looks the same as the arrow from "teaching method"
to "student performance." The structural equations make no distinction
in kind. But Woodward insists that they are different in kind---that the
degree of invariance is part of what it means for a relationship to be
causal, and that collapsing this distinction loses information that is
essential for prediction, explanation, and intervention planning.

**8.2 The EWG Discount Factors Track Woodward's Invariance Hierarchy**

Here is the connection to the EWG: the seven warrant types, and their
associated discount factors, operationalize Woodward's invariance
conditions for the specific domain of environmental psychology. They
encode, in quantitative form, how invariant each evidential bridge is
likely to be across contexts.

Consider the ordering:

**CONSTITUTIVE (d = 0.95)** represents maximal invariance. If ceiling
height *is* room volume divided by floor area, this identity holds in
every context, under every intervention, in every culture. It is as
invariant as a relationship can be. In Woodward's terms, it would
survive any intervention on any background variable---because it is not
a causal relationship at all but a definitional one, and definitional
relationships are trivially invariant.

**MECHANISM (d = 0.80)** represents high invariance. If we know the
mechanistic pathway from daylight to serotonin, we know the specific
conditions under which the relationship holds (the relevant wavelengths
must reach the retina, the raphe nuclei must be functional). The
relationship is invariant under all interventions that preserve the
mechanism---a wide range of contexts---and fails only when a specific
link in the chain is disrupted. Woodward's stability, proportionality,
and specificity conditions (Woodward, 2010) are all addressed: we know
how fine-grained the mapping between cause and effect is, and under what
perturbations it holds.

**EMPIRICAL\_COVARIANCE (d = 0.80)** represents moderate invariance with
a specific vulnerability. The replicated correlation may be robust
across many observed contexts, but because the mechanism is unknown, we
cannot predict which background changes will disrupt it. The invariance
range is empirically bounded by the contexts in which the correlation
has been observed---but it could collapse in any novel context that
introduces a confounding shift. Woodward himself notes that
generalizations supported only by observed covariance have less
explanatory depth than those supported by mechanistic understanding,
precisely because their invariance range is harder to characterize
(Woodward, 2003, Ch. 5).

**ANALOGICAL (d = 0.40)** represents low invariance. The relationship
holds in a different domain and is being extended by structural
similarity. But analogical transfer is notoriously sensitive to surface
features that mask deep structural differences (Holyoak & Thagard,
1995). The invariance range is the set of contexts that share the
relevant structural features with the source domain---a set that is
itself uncertain. This is why the discount is severe: the relationship
might be invariant across contexts, or it might not, and we lack the
domain-specific knowledge to tell.

**THEORETICAL\_DEFAULT (d = 0.25)** represents minimal invariance. The
relationship is conjectured on theoretical grounds without empirical
testing. Its invariance range is entirely speculative. The discount
reflects the historical base rate at which theoretically plausible
causal claims turn out to be empirically supported---a sobering
fraction, as the replication crisis in psychology has demonstrated (Open
Science Collaboration, 2015).

The discount ordering is thus not arbitrary. It tracks the expected
invariance range of each warrant type, from definitional (maximally
invariant) through mechanistic (invariant across mechanism-preserving
contexts) through correlational (invariant across observed contexts)
through analogical (invariant across structurally similar contexts) to
theoretical (invariance unknown). Woodward's concept of invariance
provides the philosophical justification; the discount factors provide
the quantitative implementation.

**8.3 The Argument Pearl Cannot Make: Invariance Requires Provenance**

This is where the argument bites. Pearl can represent the existence of a
causal relationship. He can represent its strength (the structural
equation specifies the function). He can even, through the
transportability framework, represent that a relationship may differ
between contexts (the S-nodes). But he cannot represent the invariance
range of a causal relationship, because the invariance range depends on
why the relationship holds---the very information that the structural
equation discards.

Woodward's invariance is inherently provenance-dependent. To assess
whether a generalization is invariant under a class of perturbations,
you need to know what sustains the generalization. Is it sustained by a
mechanism? Then it is invariant under perturbations that preserve the
mechanism. Is it sustained by a confounded correlation? Then it is
invariant under perturbations that preserve the confounding
structure---but fragile otherwise. Is it sustained by analogy? Then it
is invariant to the extent that the analogy holds. Each answer requires
knowing the evidential basis---the warrant type---of the causal claim.

Pearl might respond that invariance should be encoded directly in the
structural equations---that f should be specified as a function not just
of X and U but of the background conditions B, so that the equation Y =
f(X, B, U) explicitly represents the dependence on context. This is
formally possible, but it begs the question. To specify how Y depends on
B, you need to know the mechanism by which X affects Y, which is
precisely the information that the warrant type provides. The typed edge
is not an alternative to the structural equation; it is the metadata
that tells you how to construct the structural equation for a new
context.

**9. A Formal Worked Example: Daylight, Mood, and Hospital Recovery**

Abstract arguments have their virtues, but they also have limitations.
To make the case concrete, we trace a single architectural claim through
both Pearl's framework and the EWG, showing exactly where the typed
edges produce different and more informative outputs.

**9.1 The Claim**

The claim is: "Increasing the window-to-wall ratio in hospital patient
rooms will reduce average length of stay by 0.7 days." This is a real
claim with empirical support (Beauchemin & Hays, 1996; Walch et al.,
2005) that an evidence-based design system like ATLAS would need to
evaluate for a specific new hospital project.

**9.2 Pearl's Representation**

In Pearl's framework, the claim is represented by a causal path:

**W → D → S → M → R**

where W = window-to-wall ratio, D = daylight exposure, S = serotonin
levels, M = mood state, and R = recovery time. Each arrow corresponds to
a structural equation. The do-calculus can compute P(R \| do(W = w)) if
the graph is identified and the structural equations are specified.

The output is a single number: the expected change in R under the
intervention do(W = w). For a specified graph, this is a definitive
answer. Pearl's framework is entirely correct in its computation.

**9.3 The EWG Representation**

In the EWG, the same causal path is represented, but each edge carries a
warrant type and confidence weight:

**W → D:** CONSTITUTIVE (τ = CONSTITUTIVE, d = 0.95, ω = 0.95). Larger
windows admit more daylight by the definition of fenestration. This is
an identity, not a causal claim. It transfers to any building with
transparent glazing.

**D → S:** MECHANISM (τ = MECHANISM, d = 0.80, ω = 0.85). Lambert et al.
(2002) identified the specific neurochemical pathway: bright light
stimulates retinal ganglion cells, which project to the raphe nuclei via
the retinohypothalamic tract, increasing tryptophan hydroxylase activity
and serotonin turnover. The mechanism is established in controlled
conditions.

**S → M:** MECHANISM (τ = MECHANISM, d = 0.80, ω = 0.80). The
serotonergic system's role in mood regulation is well-established
through the pharmacological literature (Aan het Rot et al., 2009). SSRIs
work by increasing serotonin availability. The 5-HT receptor pathway is
characterized.

**M → R:** EMPIRICAL\_COVARIANCE (τ = EMPIRICAL\_COVARIANCE, d = 0.80, ω
= 0.65). Multiple observational studies show that depressed patients
have longer hospital stays (Saravay et al., 2004). But the mechanism is
unclear---does mood affect recovery directly (e.g., through immune
function), or is the correlation confounded by treatment adherence,
social support, or disease severity? The covariance is robust but the
pathway is unresolved.

**9.4 What the EWG Reveals That Pearl's Framework Does Not**

**The weakest link.** The minimum-discount composition principle (from
the parent paper's Section 5) tells us that the effective discount for
the full path is d\_eff = min(0.95, 0.80, 0.80, 0.80) = 0.80, but this
is misleading because the final link (M → R) is of a different and
weaker warrant type than the mechanistic links. The system flags that
although the first three links form a robust mechanistic chain, the
final link---the one that connects the proximate cognitive outcome
(mood) to the distal practical outcome (recovery)---rests on
correlational evidence vulnerable to confounding.

**The specific vulnerability.** Because M → R is EMPIRICAL\_COVARIANCE,
the system can identify exactly where transfer risk is highest. The
mechanistic chain W → D → S → M will transfer to any hospital where the
glazing transmits relevant wavelengths and the patient population has
functional serotonergic systems. But the M → R link could fail to
transfer if the correlation between mood and recovery is confounded by
factors that differ between the study hospitals and the target
hospital---for example, if the study hospitals served populations with
different socioeconomic profiles, comorbidity burdens, or care
protocols.

**The targeted research recommendation.** The EWG generates a specific
recommendation: to strengthen this claim for the target hospital, the
highest-value investment is a study investigating the mechanism by which
mood affects recovery---for example, testing whether mood influences
immune function (Kiecolt-Glaser et al., 2002) or treatment adherence
(DiMatteo et al., 2000). This would upgrade M → R from
EMPIRICAL\_COVARIANCE to MECHANISM, increasing the effective discount of
the final link and reducing vulnerability to confounding. Pearl's
framework cannot generate this recommendation because it does not know
that M → R's structural equation was established by correlation rather
than mechanism.

**The S-node placement.** For Pearl's own transportability analysis, the
EWG tells the analyst where to place S-nodes. The mechanistic links (D →
S, S → M) need S-nodes only on variables that could disrupt the specific
mechanism (wavelength spectrum, serotonergic function). The
correlational link (M → R) needs S-nodes on every potential confounder
of the mood-recovery association---a much larger and less well-defined
set. The warrant types thus directly inform the transportability
analysis, generating different S-node placements for different links
based on the character of the evidence.

**9.5 The Quantitative Difference**

To make this difference numerically concrete, consider two scenarios for
the target hospital:

**Scenario A:** The target hospital serves a similar population to the
study hospitals (similar socioeconomic profile, similar comorbidity
burden). In this case, the confounders that might mediate the M → R
correlation are likely preserved, and the full path can be projected
with moderate confidence. The BN computed by π will show a meaningful
effect of window-to-wall ratio on recovery time.

**Scenario B:** The target hospital is a psychiatric facility with a
very different patient population (different comorbidities, different
treatment protocols, different socioeconomic profile). Now the
confounders of M → R are likely different, and the EMPIRICAL\_COVARIANCE
warrant for that link is less trustworthy. The EWG system attenuates the
projected confidence for this link specifically, while preserving the
full confidence in the mechanistic chain W → D → S → M. The BN still
shows a confident effect of windows on mood but a reduced and uncertain
effect of mood on recovery.

In Pearl's framework, both scenarios produce the same output: the
structural equation for M → R is the same in both cases, and the
computed P(R \| do(W = w)) does not change unless the analyst manually
adjusts the structural equations. The EWG system automatically produces
different outputs for different target contexts, because the typed edges
carry information about which links are context-sensitive and which are
not.

**10. What the Causal Hierarchy Theorem Itself Implies for Typed Edges**

There is a delicious irony in the relationship between the Causal
Hierarchy Theorem (CHT) and the case for typed edges. The CHT is Pearl's
strongest formal result, and it actually supports the EWG's
architecture.

The CHT (Bareinboim et al., 2022) proves that the three levels of the
Pearl Causal Hierarchy almost always separate: knowledge at Level i is
insufficient to answer questions at Level i+1. Observational data
cannot, in general, answer interventional questions. Interventional data
cannot, in general, answer counterfactual questions. Climbing the ladder
requires additional causal assumptions.

Now observe: the CHT says that climbing the ladder requires assumptions,
but it says nothing about where those assumptions come from or how
confident we should be in them. The theorem is about the logical
structure of causal reasoning, not about the epistemology of causal
belief. It tells you that you need to assume an SCM to go from Level 1
to Level 2, but it does not tell you whether your assumed SCM is any
good.

This is precisely the gap that the EWG fills. The CHT establishes that
every Level 2 or Level 3 analysis rests on causal assumptions that go
beyond the data. The EWG provides a principled account of how confident
we should be in those assumptions, based on the type and quality of
evidence that supports them. A Level 2 analysis grounded in MECHANISM
warrants rests on assumptions that are well-supported by evidence of the
right kind. A Level 2 analysis grounded in THEORETICAL\_DEFAULT warrants
rests on assumptions that are, by the CHT's own logic, almost entirely
unsupported---the analyst has assumed an SCM without providing evidence
that it is the right one.

Pearl might object that the quality of assumptions is the analyst's
problem, not the framework's. This is true in one sense---the
do-calculus is correct given any consistent SCM. But it is false in
another: a framework that provides no tools for assessing the quality of
its own inputs is incomplete for practical use. The EWG provides those
tools. It is, in a precise sense, the epistemological complement to
Pearl's computational framework: where the CHT proves that assumptions
are needed, the EWG evaluates whether the assumptions are warranted.

To put this in terms Pearl himself would appreciate: the CHT proves that
you cannot get something (Level 2 knowledge) from nothing (Level 1 data
alone). The EWG asks: but exactly how much of something do you have? The
answer is the discount factor.

**11. Anticipating the Counter: "Encode It in the Structural
Equations"**

**11.1 The Objection**

The most sophisticated version of Pearl's objection would not deny that
provenance information is valuable. Instead, it would argue that
provenance information should be encoded within the SCM framework
itself, not in a parallel data structure. The argument would run: "If
you know that a relationship is mechanistic, encode the mechanism as
intermediate variables in the structural equations. If you know that a
relationship is correlational, leave the intermediate variables
unspecified and add appropriate error terms. If you know that a
relationship is analogical, add a selection variable representing the
domain of the analogy. Every piece of information your warrant types
carry can be represented as structural equations over an expanded
variable set. Your typed edges are just a shorthand for a richer SCM."

**11.2 Why This Fails: The Representation Theorem**

This objection fails for three reasons, each of which is fatal.

**First: the expansion is unbounded.** To encode the mechanistic pathway
from daylight to serotonin as explicit intermediate variables, you need
to include every component of the mechanism (retinal ganglion cells,
retinohypothalamic tract, raphe nuclei, tryptophan hydroxylase). For N
mechanisms in the graph, each with M intermediate variables, the SCM
grows from the original variable set to a variable set of size N × M. In
the ATLAS domain, where the EWG may contain hundreds of edges, each
supported by evidence from different experimental paradigms, the
expanded SCM would be enormous and practically unmanageable. The EWG's
type annotations achieve the same informational work with a
seven-element label on each edge---a constant-size annotation regardless
of the underlying complexity.

**Second: the expansion presupposes the knowledge it is supposed to
replace.** To expand a MECHANISM edge into an explicit mechanistic
chain, you must already know the mechanism. But knowing the mechanism is
exactly what the MECHANISM warrant type asserts. The expansion is
circular: it replaces a warrant type annotation with an expanded graph
that can only be constructed if you have the information that the
annotation carries. For an EMPIRICAL\_COVARIANCE edge, the whole point
is that the intermediate variables are unknown---you cannot expand them
into explicit structural equations because you do not know what they
are. The warrant type is not a shorthand for a richer SCM; it is a
description of the epistemic state of the analyst regarding a structural
equation whose internal structure is partially or wholly unknown.

**Third: the expansion loses the categorical distinction between warrant
types.** In an expanded SCM, all relationships are represented as
structural equations. A mechanistic chain and an unexpanded
correlational edge are both just arrows with equations. The categorical
information---that one relationship is understood mechanistically and
the other is not---is lost in the expansion. You would need a
meta-annotation on the structural equations to indicate which ones
represent fully specified mechanisms and which represent placeholders
for unknown mechanisms. But this meta-annotation is precisely the
warrant type. The expansion has not eliminated the need for typed edges;
it has merely moved the type labels to a different location in the
representation.

**11.3 The Deeper Issue: Pearl's Framework Is a Theory of Causal
Computation, Not Causal Epistemology**

The fundamental issue is that Pearl's SCM framework is a theory of
causal computation: given a causal model, it computes causal effects. It
is not a theory of causal epistemology: it does not address how to
assess the credibility of a causal model or how to construct a causal
model for a new context from evidence gathered elsewhere.

This is not a criticism. It is a description of scope. Newton's
mechanics tells you how to compute trajectories given forces and masses;
it does not tell you how to measure forces and masses. Maxwell's
equations tell you how to compute electromagnetic fields given charge
distributions; they do not tell you how to determine charge
distributions in a new system. In each case, the computational theory is
incomplete without an epistemological theory that specifies how its
inputs are to be determined.

The EWG is the epistemological theory that Pearl's computational theory
needs. It specifies how to assess the credibility of each causal
assumption (through warrant types and confidence weights), how to
aggregate multiple lines of evidence (through the multi-edge log-odds
combination), and how to translate epistemic assessments into
computational inputs (through the projection function π). It does not
replace Pearl's framework. It completes it.

Or, to put this in a phrase that a theorist of Pearl's sophistication
would appreciate: the EWG is the model of model uncertainty. Pearl's
framework assumes a model and computes. The EWG evaluates how well the
model is warranted and computes the consequences for trust in the
computation's outputs. Both are necessary for any system that must act
on evidence rather than certainty---which is to say, for any system that
operates in the real world.

**12. A Concession, a Challenge, and a Synthesis**

**12.1 The Concession**

Pearl is right that, once the projection is complete and the BN is
specified, his do-calculus is the correct tool for computing causal
effects. The EWG does not improve on the do-calculus for computational
purposes. It does not provide a more efficient algorithm for causal
inference. It does not extend the class of identifiable causal effects.
Pearl's computational machinery is, within its domain, complete and
optimal.

Pearl is also right that adding complexity to a formal system requires
justification. The seven warrant types, the discount factors, the
projection function---these are substantial additions to the conceptual
and computational apparatus. If they did not carry information that the
simpler framework cannot represent, Occam's razor would favor Pearl's
leaner system.

**12.2 The Challenge**

But the challenge to Pearl is equally direct: show us how to solve the
cross-context transfer problem without provenance information. Show us
how an untyped structural equation, stripped of its evidential history,
can generate the five capabilities described in Section 6: targeted
evidence acquisition, differential sensitivity to new evidence,
confounding risk assessment, explanation and audit, and graceful
degradation under evidential challenge.

The transportability framework (Pearl & Bareinboim, 2011) is the closest
Pearl's framework comes, but it presupposes knowledge of where contexts
differ (the S-node placement). In the ATLAS domain---where the "source
context" is a laboratory and the "target context" is a building that has
not yet been built---the S-node placement is itself uncertain and
depends on the warrant types. MECHANISM warrants reduce S-node
uncertainty (because knowing the mechanism tells you where
context-sensitivity can enter). EMPIRICAL\_COVARIANCE warrants leave
S-node uncertainty high (because the mediating pathway is unknown, so
context-sensitivity could enter anywhere). The typed edges are not
decorating the graph; they are informing the transportability analysis
that Pearl's own framework requires.

**12.3 The Synthesis: Division of Labor**

We can now state the relationship between the EWG and Pearl's SCM
framework with full precision:

**Pearl's framework answers:** Given a causal graph, what are the causal
effects? (The do-calculus.)

**Pearl's framework also answers:** Given two contexts with known
differences, when does a causal effect transport? (Transportability
theory.)

**The EWG answers:** Where does the causal graph come from? How
trustworthy is each edge? What kind of evidence supports it? How will it
behave in a new context? Where should the S-nodes go?

**Woodward's invariance provides:** The philosophical justification for
why different warrant types yield different transfer reliabilities.
Invariance range depends on evidential provenance.

**The projection function π answers:** How should the epistemic
assessments in the EWG be translated into the aleatory parameters that
Pearl's framework needs?

**The CHT itself implies:** That the assumptions feeding the do-calculus
cannot be derived from data alone---they require justification, and the
EWG provides the accounting system for that justification.

This is a division of labor, not a competition. The EWG and the SCM
framework operate at different levels of the epistemological stack. The
SCM operates at the level of causal computation: given structure,
compute effects. The EWG operates at the level of evidential assessment:
given evidence, assess structure. The projection function π is the
interface between the two levels.

Pearl's likely objection---that typed edges add complexity without
adding computational power---is correct about computational power
narrowly construed (computing P(Y \| do(X)) within a given graph). But
it overlooks the problem that the ATLAS system was built to solve:
constructing trustworthy causal models for architectural contexts that
have never been studied, using evidence gathered in laboratory contexts
that may differ in unknown ways. For this problem, the typed edges are
not ornamental. They are the primary data structure.

To put it in a phrase that Pearl himself might appreciate: the EWG is to
the SCM what the specification of the structural equations is to the
computation of the do-calculus. The do-calculus tells you what follows
from the structural equations. The EWG tells you how much to believe the
structural equations. Both are necessary. Neither is sufficient alone.

**13. References**

Aan het Rot, M., Mathew, S. J., & Bhagwagar, Z. (2009). Neurobiological
mechanisms in major depressive disorder. CMAJ, 180(3), 305--313.
https://doi.org/10.1503/cmaj.080697

Bareinboim, E., Correa, J., Ibeling, D., & Icard, T. (2022). On Pearl's
hierarchy and the foundations of causal inference. In H. Geffner, R.
Dechter, & J. Halpern (Eds.), Probabilistic and causal inference: The
works of Judea Pearl (pp. 507--556). ACM Books.

Bareinboim, E., & Pearl, J. (2016). Causal inference and the data-fusion
problem. Proceedings of the National Academy of Sciences, 113(27),
7345--7352. https://doi.org/10.1073/pnas.1510507113

Beauchemin, K. M., & Hays, P. (1996). Sunny hospital rooms expedite
recovery from severe and refractory depressions. Journal of Affective
Disorders, 40(1--2), 49--51.
https://doi.org/10.1016/0165-0327(96)00040-7

Cartwright, N. (1989). Nature's capacities and their measurement. Oxford
University Press.

Craver, C. F. (2007). Explaining the brain: Mechanisms and the mosaic
unity of neuroscience. Oxford University Press.

Der Kiureghian, A., & Ditlevsen, O. (2009). Aleatory or epistemic? Does
it matter? Structural Safety, 31(2), 105--112.
https://doi.org/10.1016/j.strusafe.2008.06.020

DiMatteo, M. R., Lepper, H. S., & Croghan, T. W. (2000). Depression is a
risk factor for noncompliance with medical treatment: Meta-analysis of
the effects of anxiety and depression on patient adherence. Archives of
Internal Medicine, 160(14), 2101--2107.
https://doi.org/10.1001/archinte.160.14.2101

Holyoak, K. J., & Thagard, P. (1995). Mental leaps: Analogy in creative
thought. MIT Press.

Huang, Y., & Valtorta, M. (2006). Pearl's calculus of intervention is
complete. In Proceedings of the 22nd Conference on Uncertainty in
Artificial Intelligence (pp. 217--224). AUAI Press.

Kiecolt-Glaser, J. K., McGuire, L., Robles, T. F., & Glaser, R. (2002).
Emotions, morbidity, and mortality: New perspectives from
psychoneuroimmunology. Annual Review of Psychology, 53, 83--107.
https://doi.org/10.1146/annurev.psych.53.100901.135217

Lambert, G. W., Reid, C., Kaye, D. M., Jennings, G. L., & Esler, M. D.
(2002). Effect of sunlight and season on serotonin turnover in the
brain. The Lancet, 360(9348), 1840--1842.
https://doi.org/10.1016/S0140-6736(02)11737-5

Machamer, P., Darden, L., & Craver, C. F. (2000). Thinking about
mechanisms. Philosophy of Science, 67(1), 1--25.
https://doi.org/10.1086/392759

Open Science Collaboration. (2015). Estimating the reproducibility of
psychological science. Science, 349(6251), aac4716.
https://doi.org/10.1126/science.aac4716

Pearl, J. (1988). Probabilistic reasoning in intelligent systems:
Networks of plausible inference. Morgan Kaufmann.

Pearl, J. (2009). Causality: Models, reasoning, and inference (2nd ed.).
Cambridge University Press.

Pearl, J., & Bareinboim, E. (2011). Transportability of causal and
statistical relations: A formal approach. In Proceedings of the 25th
AAAI Conference on Artificial Intelligence (pp. 247--254). AAAI Press.

Pearl, J., & Mackenzie, D. (2018). The book of why: The new science of
cause and effect. Basic Books.

Saravay, S. M., Pollack, S., Steinberg, M. D., Weinschel, B., & Habert,
M. (2004). Four-year follow-up of the influence of psychological
comorbidity on medical rehospitalization. American Journal of
Psychiatry, 153(3), 397--403. https://doi.org/10.1176/ajp.153.3.397

Shpitser, I., & Pearl, J. (2006). Identification of joint interventional
distributions in recursive semi-Markovian causal models. In Proceedings
of the 21st National Conference on Artificial Intelligence (pp.
1219--1226). AAAI Press.

Toulmin, S. E. (1958). The uses of argument. Cambridge University Press.

Walch, J. M., Rabin, B. S., Day, R., Williams, J. N., Choi, K., & Kang,
J. D. (2005). The effect of sunlight on postoperative analgesic
medication use: A prospective study of patients undergoing spinal
surgery. Psychosomatic Medicine, 67(1), 156--163.
https://doi.org/10.1097/01.psy.0000149258.42508.70

Woodward, J. (1997). Explanation, invariance, and intervention.
Philosophy of Science, 64(Supplement), S26--S41.

Woodward, J. (2000). Explanation and invariance in the special sciences.
The British Journal for the Philosophy of Science, 51(2), 197--254.
https://doi.org/10.1093/bjps/51.2.197

Woodward, J. (2003). Making things happen: A theory of causal
explanation. Oxford University Press.

Woodward, J. (2010). Causation in biology: Stability, specificity, and
the choice of levels of explanation. Biology & Philosophy, 25(3),
287--318. https://doi.org/10.1007/s10539-010-9200-z
