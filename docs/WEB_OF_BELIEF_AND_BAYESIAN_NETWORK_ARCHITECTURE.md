# The Web of Belief and the Bayesian Network: Two Kinds of Knowing

## An Architectural Philosophy for the CMR System

### David Kirsh's CMR Project — February 2026

---

## Preface: What This Document Is About

Imagine you are an architect designing a new office building. You want to know
whether high ceilings will make the occupants more creative. This sounds like a
simple question, but it conceals an extraordinary amount of intellectual
machinery. To answer it well, you need two very different kinds of reasoning —
and understanding the difference between them is the subject of this document.

The first kind of reasoning asks: **What do we believe about how the world
works, and how confident are we?** This is the province of the Web of Belief.
It is concerned with theories, mechanisms, evidence, competing explanations,
and the coherence of our total picture of the mind-environment relationship.
When we ask "does ceiling height facilitate creative cognition?", the Web of
Belief reasons about *why* it might (the broaden-and-build theory, the
predictive processing account of spatial volume, the affect-broadening
pathway), *what evidence supports or undermines each account*, and *how
confident the relevant scientific community should be* in the claim.

The second kind of reasoning asks: **If I intervene on the world — if I raise
the ceiling — what will actually happen?** This is the province of the Bayesian
Network. It is concerned with causal relationships between observable
variables, with the mathematics of intervention, and with the distinction
between correlation and causation. When we ask "what will happen if I raise the
ceiling?", the Bayesian Network computes the expected downstream effects by
propagating the intervention through a causal graph.

These are not the same question, and they require different intellectual tools.
The Web of Belief is an epistemological structure — it represents *what a
community of scientists believes and why*. The Bayesian Network is a causal
structure — it represents *how variables in the world are connected*. The CMR
(Compositional Mechanistic Reasoning) system uses both, and the relationship
between them is the architectural question that this document addresses.

---

## Part I: The Web of Belief

### 1. A Brief History of Webs

The metaphor of knowledge as a web has a distinguished philosophical lineage.
W.V.O. Quine and J.S. Ullian's *The Web of Belief* (1970) argued that our
beliefs form an interconnected network in which no single belief is immune from
revision. Even apparently certain beliefs — that 2 + 2 = 4, that the earth
existed five minutes ago — are in principle revisable if the total web of
belief would become more coherent by revising them. Beliefs at the centre of
the web (logic, mathematics, fundamental physics) are more resistant to
revision because changing them would require revising many other beliefs that
depend on them. Beliefs at the periphery (today's weather, the colour of the
neighbour's cat) can be revised easily because few other beliefs depend on
them.

This metaphor captures something important: knowledge is not a list of
independent facts. It is a structure in which everything is connected to
everything else, and the *reasons for believing something* are as important as
the belief itself. When a scientist tells you that high ceilings facilitate
creative thinking, the interesting question is not just whether this is true
but *why they believe it*, *what would change their mind*, and *how this belief
connects to their other beliefs about cognition, architecture, and the brain*.

Paul Thagard (1989, 2000) formalised this intuition into a computational
theory of **explanatory coherence**. Thagard proposed that beliefs are accepted
or rejected not in isolation but on the basis of how well they cohere with
other beliefs. Specifically, Thagard identified several principles that govern
coherence in a belief network:

**Principle 1: Symmetry.** If belief A coheres with belief B, then B coheres
with A. Coherence is a relationship between beliefs, not a property of a
single belief.

**Principle 2: Explanation.** If a hypothesis H explains evidence E, then H
and E cohere with each other. The more evidence a hypothesis explains, the
more coherent it is with the overall web.

**Principle 3: Analogy.** If hypothesis H1 is analogous to hypothesis H2, and
H2 is well-supported, then H1 gains some coherence from the analogy. This is
weaker than explanation — an analogy is not proof — but it contributes to the
overall coherence of the web.

**Principle 4: Data priority.** Beliefs that are directly grounded in
observation have a default advantage over beliefs that are purely theoretical.
Empirical findings anchor the web.

**Principle 5: Contradiction.** If belief A contradicts belief B, they
incohere. Accepting one puts pressure on rejecting the other.

**Principle 6: Competition.** If two hypotheses both explain the same evidence
but are incompatible, they compete. Accepting one puts pressure on rejecting
the other, unless they can be reconciled.

These principles describe the kind of reasoning that happens when scientists
evaluate a complex, multi-theory, multi-evidence domain — which is exactly
what the CMR does. And notice that none of these principles is about
probability in the mathematical sense. They are about the *relationships
between beliefs* — explanation, analogy, contradiction, competition — which
are qualitative, structural relationships that cannot be reduced to numbers
without losing something essential.

### 2. The CMR Web of Belief: What It Contains

The CMR Web of Belief is a concrete instantiation of these philosophical ideas.
It represents the current state of scientific knowledge about the relationship
between buildings and the human brain. Here is what it contains:

**Tier 1 Framework Theories (10 nodes).** These are the major theoretical
frameworks from cognitive neuroscience that ground the system: Predictive
Processing, Salience Network theory, Default Mode / Place Cells, Dual-Task /
Cognitive Load, Neuromodulation, Interoception / Body Budget, Multisensory
Integration, Embodied Cognition, Circadian Biology, and Motor-Sensory
Integration. Each of these is a substantial scientific theory with decades of
empirical support. They sit near the centre of the web — revising any of them
would require revising hundreds of downstream beliefs.

**Tier 1.5 Domain Theories (10 nodes).** These are intermediate theories that
apply T1 frameworks to the specific domain of human-environment interaction:
Biophilia, Prospect-Refuge, Attention Restoration, Stress Reduction, Fractal
Fluency, Awe/Kama Muta, Space Syntax, Soundscape Ecology, Place Attachment,
and Aesthetic Anchoring (candidate). Each T1.5 theory is *reduced* to one or
more T1 frameworks — that is, its claims are explained by T1 mechanisms. For
example, Prospect-Refuge theory (Appleton, 1975) is reduced to Predictive
Processing (the brain predicts threat based on spatial configuration) and
Default Mode / Place Cells (hippocampal place cells encode spatial refuge
locations). These reduction links are edges in the web.

**Tier 2 Templates (~93 nodes after CROSSCUT-I).** These are specific,
calibrated claims about how particular environmental features affect particular
neural mechanisms and produce particular occupant outcomes. Each template
contains a mechanism chain (a sequence of causal steps from environmental
feature to neural mechanism to behavioural/experiential outcome), a bridge
warrant (the type and strength of the inferential bridge from neuroscience to
architecture), Toulmin justification at each step (data, backing, qualifier,
rebuttal, competing accounts), and a confidence score.

**Cross-cutting Axioms (AX nodes).** These are meta-level parameters that
modify all templates: dose-response functions, habituation dynamics, individual
differences, cultural modulation, perceived control (AX4), and the temporal
distinction between acute and chronic effects. They are like the laws of
physics for the web — they constrain what every other node can claim.

**Working Models (Barrett-Craig, Differential-Mode).** These are theoretical
commitments that the web has adopted as default assumptions, with explicit
revision clauses. They sit between T1 and T1.5 in influence — they are not as
fundamental as the T1 frameworks but they constrain many templates.

### 3. The Edges: What Connects the Nodes

The web is not just a collection of nodes. It is the connections between them
that give the web its power. The CMR web has several distinct types of edges,
and understanding what each type means is crucial for understanding what kind
of reasoning the web supports.

**Reduction edges (T1 → T1.5, T1.5 → T2).** These connect theories at
different levels. A reduction edge says: "this higher-level claim is explained
by this lower-level mechanism." Prospect-Refuge theory is reduced to PP + DP.
This means that when we evaluate the credibility of Prospect-Refuge theory, we
consider the credibility of PP and DP as part of the calculation. The CMR
credence formula makes this explicit:

```
P(CNFA effect) = P(parent theory) × P(bridge) × P(CNFA-specific)
```

If Predictive Processing were seriously undermined (e.g., by a devastating
critique showing that the brain does not actually compute prediction errors),
then every T1.5 theory that reduces to PP — Prospect-Refuge, Fractal Fluency,
Space Syntax — would lose credibility, and every T2 template downstream of
those T1.5 theories would need revision. This is exactly Quine's point about
central vs. peripheral beliefs: T1 frameworks are central, and revising them
propagates widely.

**Bridge warrant edges (T2 ↔ empirical evidence).** These connect theoretical
claims to empirical evidence, but they carry a *type* that specifies the
strength and character of the connection:

- **CONSTITUTIVE** (ceiling 0.75): The mechanism *is* the phenomenon. The VTA
  dopamine neuron firing IS the reward prediction error signal. This is the
  strongest bridge — it says that measuring the mechanism is measuring the
  phenomenon.

- **MECHANISM** (ceiling 0.60): There is a complete causal pathway at the
  neural/molecular level connecting the environmental feature to the outcome.
  We can trace each step.

- **EMPIRICAL_COVARIANCE** (ceiling 0.60): There is a replicated statistical
  association between the environmental feature and the outcome, but the
  complete mechanism is not specified.

- **FUNCTIONAL** (ceiling 0.50): The same function (e.g., "alerting") operates
  in both the laboratory context and the architectural context, but the
  detailed mechanism may differ.

- **CAPACITY** (ceiling 0.45): A neural system has the *capacity* to respond
  to the environmental feature, but its actual operation in architectural
  contexts is unconfirmed.

- **ANALOGICAL** (ceiling 0.35): We are reasoning from a parallel case. Drug-
  related incentive sensitisation is analogous to architectural place
  attachment, but the analogy may not hold.

- **THEORETICAL_DEFAULT** (ceiling 0.40): An expert-assigned value that awaits
  empirical calibration. This is an honest placeholder — it says "we think
  this is approximately right, but we have not measured it directly."

Notice what these types give you. They are not numbers (though they have
numerical ceilings). They are *epistemological categories* — they tell you
what *kind of inferential bridge* connects the evidence to the claim. A
MECHANISM bridge and an ANALOGICAL bridge might happen to produce the same
numerical confidence (say, 0.35), but they mean very different things. The
MECHANISM bridge at 0.35 says "the causal pathway is well-characterised, but
the architectural instantiation is uncertain." The ANALOGICAL bridge at 0.35
says "we are reasoning from a parallel case that may not apply." These
carry completely different implications for what research would resolve the
uncertainty (for the MECHANISM bridge: measure the mechanism in a real
building; for the ANALOGICAL bridge: establish that the analogy actually
holds).

**Competition edges.** These connect hypotheses that are in tension. In the
THERMAL-I panel, Barrett's constructionist model of interoception competed
with Craig's labelled-line model. The competition was resolved by a
compromise (the two-stage model), but the competition edge remains in the
web as a record of the theoretical landscape. Future evidence that favours
one account over the other would reactivate this edge.

**Cross-template interaction edges.** These connect templates that share
mechanisms or environmental inputs. NEUROMOD-I produced 8 cross-template
interactions, including the NE-ACh interaction (explore/exploit × precision
weighting) and the 5-HT moderation of wanting-liking balance. These edges
are where the web is thickest — they represent the insight that environmental
effects are not independent but interact through shared neural substrates.

**Inheritance edges.** These connect templates that share calibrated
parameters. CREATIVE-I's incubation template inherits DMN re-engagement
conditions from MEMORY-I, and NEUROMOD-I's threat template inherits HPA
parameters from STRESS-I. Inheritance edges prevent double-counting (two
templates claiming the same effect independently) and ensure consistency
(the same mechanism cannot have different parameter values in different
templates).

### 4. What Kind of Reasoning Does the Web Support?

The Web of Belief supports reasoning that a Bayesian Network cannot. Here are
the major types:

#### 4.1 Explanatory Coherence Assessment

You can ask: "How coherent is the total web?" — that is, how well do the
beliefs hang together? This is Thagard's central question. A web is coherent
when its beliefs mutually support each other (many explanation links, few
contradiction links) and incoherent when they conflict. The CMR web's
coherence is maintained by the constraint system: no template may contradict
calibrated values from other templates without explicit reconciliation, bridge
warrant ceilings prevent confidence inflation, and the Coburn ceiling (no
single d > 0.80) prevents implausible effect sizes.

But coherence is not just the absence of contradiction. It is the *positive
mutual support* between beliefs. When CREATIVE-I and NEUROMOD-I independently
converge on the differential-mode model (low stimulation → divergent thinking;
moderate stimulation → convergent thinking) from completely different starting
points (cognitive psychology and computational neuromodulation respectively),
this convergence *increases the coherence of the web*. The differential-mode
model now has two independent lines of support, which makes it more resistant
to revision. A Bayesian Network has no way to represent this — it treats the
two supporting lines as correlated evidence, but it does not capture the
epistemological significance of *independent derivation from different
theoretical traditions*.

#### 4.2 Reflective Equilibrium

This is the deepest kind of reasoning the web supports, and it has no
counterpart in the Bayesian Network. The concept comes from Nelson Goodman
(1955) and was elaborated by John Rawls (1971), and it describes a process of
mutual adjustment between principles and particular judgments.

Here is how it works in the CMR. Suppose the web contains a general principle
(e.g., "predictive processing accounts for environmental preference: we prefer
environments that match our generative model of safe, navigable spaces") and a
particular finding (e.g., "people prefer high ceilings for creative work, even
though high ceilings increase spatial prediction error relative to the typical
indoor generative model"). The principle and the particular finding are in
tension — high ceilings *violate* the prediction-matching principle, yet
people prefer them in creative contexts.

Reflective equilibrium resolves this tension by adjusting *both* the
principle and the interpretation of the finding until they cohere:

- Adjust the principle: "Predictive processing accounts for environmental
  preference *in routine contexts*. In creative contexts, moderate prediction
  error is desirable because it promotes model updating (the explore mode of
  the differential-mode model)."
- Adjust the interpretation: "People do not prefer high ceilings because they
  are comfortable. They prefer them because the increased spatial volume
  generates a moderate prediction error that shifts processing from exploit
  (convergent) to explore (divergent)."

Now the principle and the finding cohere. The principle has been refined (it now
has a domain restriction — "in routine contexts"), and the finding has been
reinterpreted (ceiling height preference is not about comfort but about
cognitive mode). Both have changed. This is reflective equilibrium: a
back-and-forth between general principles and particular cases until they
reach a stable, mutually supporting configuration.

The CMR's panel process is, in essence, a structured method for achieving
reflective equilibrium. The Round Table phase presents the general principles
(each expert's theoretical framework). The Crucible phase tests these
principles against particular findings and competing accounts. The calibration
phase adjusts both the principles (working models, T1.5 reductions) and the
particular findings (template parameters, confidence scores) until they
cohere. The Barrett-Craig two-stage model is a product of reflective
equilibrium: the general principles (Barrett's constructionism, Craig's
labelled-line theory) were adjusted to accommodate the particular findings
(posterior insula shows modality-specific responses, anterior insula shows
constructionist processing) and vice versa.

A Bayesian Network cannot do this. A BN takes its structure as given (the DAG
is specified in advance) and updates its parameters in response to evidence
(the CPTs are revised by Bayes' rule). It does not revise its own structure in
response to theoretical considerations. It does not ask "should this edge exist?"
— it only asks "given that this edge exists, what is the conditional
probability?" The BN is structurally rigid; the Web of Belief is structurally
fluid. The web is *where* you decide what the BN's structure should be.

#### 4.3 Value of Information Analysis

You can ask: "What should we study next?" The web supports this question
naturally because it tracks not just what we believe but *how uncertain we are
and why*. Every THEORETICAL_DEFAULT is a node where the web says: "I have an
estimate here, but it is not empirically grounded — someone should measure
this." Every competing account is a branch point where the web says: "Two
explanations are viable — someone should design an experiment that
discriminates between them."

Value of Information (VOI) analysis ranks these uncertainties by their
downstream consequences. A THEORETICAL_DEFAULT in T29 (the allostatic load
master template) has high VOI because T29 integrates across all other
templates — resolving that uncertainty improves the entire system. A
THEORETICAL_DEFAULT in a single, peripheral template has low VOI because
resolving it improves only one template.

The web can compute VOI because it has the graph structure: it knows which
nodes are upstream of which other nodes, which nodes are highly connected,
and which uncertainties propagate most widely. The BN can also compute
expected information gain, but only for the variables it represents — and
the BN's variables are environmental parameters and outcomes, not theoretical
uncertainties. The question "should we replicate the Lambert et al. (2002)
study on daylight and serotonin synthesis?" is a web question, not a BN
question, because it is about the evidential support for a theoretical claim,
not about the value of a particular variable.

#### 4.4 Theory Evaluation and Revision

You can ask: "Should we promote this theory? Should we demote that one? Should
we adopt this working model?" These are the decisions that the CMR project has
made throughout its panel process: ART and SRT were demoted from T1 to T1.5.
AX4 was elevated to a formally recognised cross-cutting moderator. The
Barrett-Craig model was adopted as a working model. Aesthetic Anchoring was
kept as a candidate pending further evaluation.

Each of these decisions is a *structural modification to the web*. It changes
which nodes exist, which edges connect them, and how credence flows through the
network. A Bayesian Network has no mechanism for this kind of self-modification.
The BN's structure is fixed; only its parameters change. The web's structure
is the thing that changes.

---

## Part II: The Bayesian Network

### 5. What a Bayesian Network Is

A Bayesian Network (BN) is a directed acyclic graph (DAG) in which the nodes
represent random variables and the directed edges represent conditional
dependencies between those variables. Each node has a conditional probability
table (CPT) that specifies the probability of each state of the variable given
the states of its parent variables.

For a simple example: if the BN has three nodes — Daylight (high/low), Mood
(positive/negative), and Productivity (high/low) — with edges Daylight → Mood
and Mood → Productivity, then the CPTs specify:

- P(Mood = positive | Daylight = high) = 0.70
- P(Mood = positive | Daylight = low) = 0.40
- P(Productivity = high | Mood = positive) = 0.65
- P(Productivity = high | Mood = negative) = 0.35

Given these CPTs, the BN can answer several kinds of questions:

**Observational queries.** "What is P(Productivity = high | Daylight = high)?"
This is computed by propagating through the network: P(Productivity = high |
Daylight = high) = P(Prod | Mood = pos) × P(Mood = pos | Daylight = high) +
P(Prod | Mood = neg) × P(Mood = neg | Daylight = high) = 0.65 × 0.70 + 0.35
× 0.30 = 0.455 + 0.105 = 0.56.

**Interventional queries (do-calculus).** "What happens if I *set* Daylight =
high (regardless of its current value)?" This is Judea Pearl's (2009)
fundamental insight: intervening on a variable is different from observing it.
When you observe that daylight is high, you learn something about the
building's orientation, the weather, the time of day — all of which might
independently affect mood and productivity. When you *intervene* to make
daylight high (by installing full-spectrum lighting), you cut the incoming
edges to the Daylight node (because you have fixed its value, its own causes
no longer matter) and propagate only the outgoing effects. The do-calculus
formalises this distinction between seeing and doing.

**Counterfactual queries.** "Given that we observed low mood in this building,
would mood have been positive if daylight had been high?" This combines
observation (conditioning on the actual evidence) with intervention (imagining
a change) and requires the most sophisticated BN reasoning.

### 6. What the BN Is Good At

The BN excels at reasoning about **causation versus association**. This is
critically important for architecture. Consider: buildings with high ceilings
tend to be newer, more expensive, better maintained, and occupied by
higher-income people. If you observe that high-ceiling buildings have more
creative occupants, you cannot conclude that the ceiling caused the
creativity — the association might be confounded by wealth, maintenance
quality, or building age. The BN, with its causal structure, can distinguish
the direct causal effect of ceiling height from the confounded association, by
conditioning on (or intervening to control) the confounding variables.

The BN also excels at **propagating interventions through complex systems**.
If you raise the ceiling, the BN computes the downstream effects on affect
broadening (d = 0.40 via the CREA2B pathway from VISUAL-I), on spatial
prediction error (increased PE → potentially increased NE → shift toward
explore mode), on thermal stratification (higher ceilings → different
temperature gradient → changed thermal comfort), and on daylight distribution
(higher windows → deeper daylight penetration → more 5-HT synthesis). The
BN handles these multiple pathways simultaneously, accounting for their
interactions and dependencies.

The BN also provides **quantitative answers**. When an architect asks "how
much improvement in creative performance can I expect if I raise the ceiling
from 2.7m to 3.5m?", the BN can provide a numerical estimate (with
uncertainty bounds) by propagating the intervention through the calibrated
CPTs. The Web of Belief can tell you *whether* ceiling height affects
creativity and *why*; the BN tells you *how much*.

### 7. What the BN Cannot Do

The BN takes its structure as given. Someone — or something — must decide which
variables to include, which edges to draw, and what the CPTs should be. The BN
itself cannot evaluate whether its own structure is correct, whether an edge
should be added or removed, whether a variable has been omitted, or whether the
CPTs faithfully represent the underlying science.

The BN has **no concept of explanation**. It can tell you that P(Mood = pos |
do(Daylight = high)) = 0.70, but it cannot tell you *why* daylight improves
mood. The mechanism (daylight → retinal stimulation → raphe nuclei → tryptophan
hydroxylase → serotonin synthesis → positive processing bias) is not
represented in the BN. The BN has a single edge "Daylight → Mood" with a CPT.
If you ask "why does daylight improve mood?", the BN can only say "because the
CPT says so." The *why* lives in the Web of Belief.

The BN has **no concept of theoretical coherence**. If you add a new variable
and a new edge to the BN, the BN does not check whether this new addition is
consistent with any theory of how the brain works. It just updates its
computations. The coherence checking — "does this new claim cohere with
Predictive Processing? Does it conflict with the Barrett-Craig model? Is it
consistent with the bridge warrant hierarchy?" — must happen elsewhere.

The BN has **no concept of warrant types**. All edges in a BN are the same
kind of thing: conditional probabilities. But as we have seen, the CMR's edges
carry qualitatively different epistemological characters: CONSTITUTIVE,
MECHANISM, ANALOGICAL, and so on. Two edges might have the same numerical
value in the CPT but mean entirely different things epistemologically. The BN
erases this distinction.

The BN has **no concept of reflective equilibrium**. It cannot revise its own
structure in response to the tension between a general principle and a
particular finding. It cannot decide to adopt a working model, or promote a
theory, or defer a candidate. It computes with whatever structure it is given.

---

## Part III: The Conversation Between Web and Network

### 8. What the BN Gets from the Web

The Web of Belief provides the BN with **everything the BN cannot generate
for itself**:

**Structure.** The web's mechanism chains determine the BN's DAG. Each step in
a mechanism chain (architectural novelty → sensory PE → phasic DA release →
approach motivation) becomes one or more edges in the BN. The web decides which
variables exist, which causal connections hold, and which conditional
independencies are justified. When the web revises a mechanism chain — adding a
step, removing one, or reordering the causal sequence — the BN's DAG is
regenerated.

**Parameters.** The web's calibrated template values, confidence scores, and
effect sizes are the raw material from which the BN's CPTs are computed. The
translation is not straightforward (as discussed in the section on CPT
elicitation), but the web provides all the information that the translation
protocol needs: effect sizes, sample sizes, warrant types, qualifiers, and
rebuttals.

**Boundary conditions.** The web's qualifiers and rebuttals tell the BN where
its computations are valid and where they break down. NM1's qualifier ("the RPE
mechanism habituates; architecturally complex buildings may sustain RPE over
many visits") tells the BN that its Daylight → Mood edge should be moderated
by a "building complexity" variable. Without this qualifier, the BN would
produce the same answer for a Peter Zumthor building and a featureless box.

**Revision signals.** When the web adopts a new working model, promotes a
theory, or revises a mechanism chain, the BN receives a regeneration signal.
The BN is not self-revising; it is revised *by the web*.

### 9. What the Web Gets from the BN

Now here is where many people get confused, and where precision matters. The
web is nearly self-sufficient in one important respect: it can, in principle,
compute quantitative consequences *through its own mechanism chains* by
compositional reasoning. When the web says "daylight increases 5-HT synthesis
(d = 0.38) AND 5-HT moderates the wanting-liking balance (d = 0.45) AND
wanting drives approach motivation (d = 0.55)", the web can propagate these
values compositionally along the chain to derive the expected compound effect.
It does not need the BN for this — the mechanism chains are causal pathways
with numerical parameters, and compositional reasoning along them yields
quantitative predictions.

What the web *cannot* do — and what the BN uniquely provides — falls into two
categories:

**Interventional reasoning (do-calculus).** The web can trace causal pathways,
but it cannot formally distinguish *observing* that daylight is high from
*intervening* to make daylight high. This is Pearl's (2009) fundamental
insight: observation and intervention are different operations. When you
observe high daylight, you learn about the building's orientation, the
weather, the season — all of which may independently affect mood. When you
intervene (install full-spectrum lighting), you sever the incoming causal
connections to daylight and propagate only the outgoing effects. The do-
calculus formalises when and how observational data can be used to estimate
interventional effects, even in the presence of confounders. The web's
compositional reasoning along mechanism chains implicitly assumes
intervention (each step is "if this input is present, this output follows"),
but it does not rigorously handle confounding, selection bias, or the
difference between correlation and causation in observational data. For this,
you need the BN's formal causal inference machinery.

**Counterfactual reasoning.** "Given that we observed low mood in this
building, *would* mood have been positive if daylight had been high?" This
combines actual observation (conditioning on what happened) with hypothetical
intervention (imagining what would have happened under different conditions).
Counterfactual reasoning requires a formal causal model that can compute
probabilities in hypothetical worlds — a capacity the BN provides through
its structural equations and the do-calculus framework, and that the web's
qualitative reasoning about mechanisms cannot replicate.

These two capacities — interventional and counterfactual reasoning — are the
BN's irreducible contribution. They are precisely what an architect needs:
"If I *do* X (raise the ceiling, improve the daylight, add nature views),
what will happen, controlling for everything else?" and "If this building
*had been* designed differently, would the outcomes have been better?" The
web provides the knowledge; the BN provides the causal logic for acting on it.

**Ground-truth feedback.** There is one additional flow from BN to web that
does not involve the BN's unique computational capacities but is practically
important. When the BN's interventional predictions are tested against real-
world data (occupant satisfaction surveys, cognitive performance measures,
physiological recordings in actual buildings), the results feed back to the
web. If the BN consistently overpredicts the benefit of nature views, the web
investigates: is the VISUAL-I VIEW1 template overcalibrated? Is the
restoration term in T29 too generous? Is there a confounding variable? The
web does the diagnosis; the BN provides the empirical accountability that
prevents the web from becoming an internally coherent but empirically
disconnected theoretical fantasy.

### 10. The Bidirectional Flow, Summarised

The relationship between web and BN is therefore asymmetric but genuinely
bidirectional:

```
Web of Belief                          Bayesian Network
                                       
Theories, mechanisms,          ──→     DAG structure
warrant types, Toulmin                 (which variables, which edges)
                                       
Calibrated parameters,         ──→     CPT values
effect sizes, confidences              (conditional probabilities)
                                       
Qualifiers, boundary           ──→     Domain restrictions
conditions, rebuttals                  (where the BN is valid)
                                       
                               ←──     Interventional predictions
                                       (do-calculus: if I do X, what happens?)
                                       
                               ←──     Counterfactual analysis
                                       (would Y have occurred if X had been different?)
                                       
                               ←──     Empirical feedback
                                       (predictions vs. observations)
```

The arrows that flow from web to BN carry *structure, parameters, and
meaning*. The arrows that flow from BN to web carry *causal logic and
empirical accountability*. The web can reason about mechanisms, coherence,
evidence, and theory on its own. The BN provides the two things the web
cannot do for itself: rigorous interventional inference (separating causation
from association in the presence of confounders) and counterfactual reasoning
(computing what would have happened under alternative conditions). These are
not minor contributions — they are precisely what makes the CMR useful for
architectural practice, where the fundamental question is always "if I change
the design, what will happen?"

---

## Part IV: Why Both Are Necessary

### 11. The Limits of the Web Without the BN

A web of belief without causal inference machinery is epistemologically rich
but interventionally naive. The web can tell you that high ceilings facilitate
creative cognition through the affect-broadening pathway (CREA2B, d = 0.40,
from VISUAL-I VF3), and it can propagate this effect compositionally through
its mechanism chains to derive downstream consequences. It can even compute
quantitative predictions by chaining effect sizes along causal pathways.

But when an architect asks "should I raise the ceiling in this research
laboratory, given that my only data is an observational study showing that
buildings with high ceilings have more creative occupants?", the web cannot
distinguish the causal effect from the confounded association. High-ceiling
buildings are newer, more expensive, better maintained, and occupied by
higher-income people. The observed correlation between ceiling height and
creativity might be entirely driven by these confounders. The web knows that
the *mechanism* runs through affect broadening, but it cannot compute the
*interventional effect* controlling for confounders from observational data.
For this, you need do-calculus.

Similarly, when the architect asks "if this building had been designed with
3.5m ceilings instead of 2.7m, would the occupants have been more creative?",
this is a counterfactual query that requires formal causal machinery. The
web can reason qualitatively ("yes, probably, because the affect-broadening
pathway would have been more strongly activated"), but it cannot compute the
counterfactual probability rigorously.

Without the BN, the web is epistemologically complete but causally informal.
It has all the knowledge but no rigorous method for separating causation from
association or computing what-if scenarios.

### 12. The Limits of the BN Without the Web

A Bayesian Network without a web of belief is a calculator without a theory.
It computes, but it does not understand. Consider what happens when the BN
produces a surprising result — say, it predicts that improving daylight has
a negligible effect on occupant satisfaction. Without the web, you have no way
to diagnose why. You can check the CPTs, verify the arithmetic, and confirm
that the BN is computing correctly. But you cannot ask: "Does this result
make sense given what we know about serotonin synthesis? Is the Lambert et al.
(2002) study being given too much or too little weight? Is there a competing
pathway (NE alerting) that is absorbing the effect? Is the VR limitation
axiom discounting the supporting evidence too aggressively?"

These diagnostic questions require the web's epistemological structure. They
require knowing that the daylight → mood pathway goes through 5-HT synthesis,
that the evidence for this pathway rests on a single study (Lambert et al.,
2002) with an unusual methodology, that there is a competing account
(circadian entrainment rather than direct serotonergic modulation), and that
the VR limitation axiom applies a discount factor to the supporting evidence
that may be too aggressive for modern VR studies.

Without the web, the BN is a black box. It produces numbers, but it cannot
explain them, justify them, or revise them in response to theoretical
considerations. It cannot participate in scientific reasoning. It can only
compute.

### 13. Reflective Equilibrium: The Web's Deepest Advantage

Let us return to the concept of reflective equilibrium, because it is the
single most important intellectual advantage of the web over the BN, and it
is worth understanding deeply.

In John Rawls' (1971) original formulation, reflective equilibrium is the end
state of a process of mutual adjustment between general principles and
particular judgments. You start with some principles (say, "environments that
confirm predictions are preferred") and some particular judgments (say, "people
enjoy spatially surprising buildings"). These conflict. You adjust the
principles ("prediction confirmation is preferred *for safety*; prediction
violation is preferred *for stimulation*"). You adjust the judgments ("people
enjoy spatially surprising buildings *in safe contexts where the prediction
violation is experienced as stimulating rather than threatening*"). You continue
adjusting until the principles and judgments cohere.

The CMR web does this continuously. Every panel is a reflective equilibrium
exercise: general theories (T1 frameworks) are tested against particular
findings (empirical studies cited in the Toulmin data arrays), and both are
adjusted until they cohere. The Barrett-Craig compromise is a reflective
equilibrium outcome — neither Barrett's pure constructionism nor Craig's pure
labelled-line theory survived intact; both were adjusted to accommodate the
full range of evidence. The differential-mode model is another — the general
principle (there is an optimal stimulation level) was refined by the particular
finding (the optimum differs for divergent vs. convergent processing) until a
coherent, empirically supported model emerged.

A BN cannot achieve reflective equilibrium because it has no principles — only
parameters. It has CPTs, which are numbers, not theories. You cannot adjust a
CPT entry in response to a theoretical consideration, because the CPT does not
know what theory it is expressing. The BN's parameters are revised by Bayes'
rule in response to data, which is a different process entirely: Bayesian
updating adjusts beliefs in response to *evidence*, but reflective equilibrium
adjusts beliefs in response to *coherence with other beliefs*. These are
different epistemic operations, and both are necessary for a system that aims
to represent a community's scientific understanding of a complex domain.

### 14. The Epistemic vs. Aleatory Distinction, Revisited

Early in our discussion, you identified the distinction between epistemic and
aleatory probability as "absolutely fundamental." Let me now show why this
distinction maps directly onto the web/BN division.

**Aleatory probability** describes the inherent randomness of the world.
When we say "the probability that this occupant will report positive mood given
high daylight is 0.70", we are describing a frequency — in the population of
occupants exposed to high daylight, approximately 70% report positive mood.
This is a fact about the world, not about our knowledge. It is what the BN
computes.

**Epistemic probability** describes our uncertainty about the world. When we
say "our confidence that the daylight → 5-HT → mood pathway is correctly
specified is 0.45", we are describing our state of knowledge — how much
evidence we have, how strong it is, how many competing accounts exist. This is
a fact about us, not about the world. It is what the web tracks.

The BN's CPTs contain aleatory probabilities (or at least, that is what they
aspire to contain — in practice, as we discussed, many CPT entries are
estimated from epistemic probabilities, which is a source of considerable
imprecision). The web's confidence scores contain epistemic probabilities. The
bridge warrant types are *categorisations of epistemic uncertainty* — they tell
you why your confidence is at the level it is (because you have a complete
mechanism, because you have a statistical correlation, because you are
reasoning from analogy).

This distinction matters practically because the two kinds of probability
respond to different interventions. Aleatory uncertainty is reduced by
*collecting more data from the same process* — measuring more occupants,
running more buildings through the same protocol. Epistemic uncertainty is
reduced by *improving the theoretical model* — specifying the mechanism more
precisely, resolving a competing account, replicating a key study with better
methodology. The web's VOI analysis is fundamentally about reducing epistemic
uncertainty; the BN's statistical analysis is fundamentally about estimating
aleatory parameters. Both are needed, and confusing them leads to bad science
(e.g., collecting more occupant data when the real problem is that the
mechanism chain is wrong, or endlessly refining the theoretical model when
the real problem is insufficient data).

---

## Part V: Building the CMR Web — How We Got Here

### 15. The Panel Process as Epistemology Engineering

The CMR web was not specified in advance by a single designer. It was built
through an iterative process of expert panel deliberation — eleven panels
(STRESS-I through CROSSCUT-I, plus three pre-pipeline panels) in which
simulated expert voices debated, contested, and calibrated the web's contents.

This process embodies a particular philosophy of knowledge construction that
is worth making explicit. The panels did not merely collect facts and deposit
them in a database. They performed a series of epistemological operations:

**Reduction**: Connecting higher-level theories to lower-level mechanisms (T1.5
theories explained by T1 frameworks).

**Calibration**: Assigning numerical parameters to mechanism steps, with
explicit uncertainty ranges and warrant types.

**Adjudication**: Resolving competing accounts through Crucible debates,
producing either a consensus (one account wins), a compromise (both accounts
are partially correct), or a recorded disagreement (the competition remains
for future resolution).

**Inheritance**: Establishing which parameters are shared across panels and
ensuring consistency.

**Constraint enforcement**: Preventing confidence inflation, double-counting,
bridge warrant violations, and theoretical incoherence.

Each of these operations modifies the web. Reduction adds edges. Calibration
populates nodes with parameter values. Adjudication resolves or records
competition edges. Inheritance adds sharing edges. Constraint enforcement
removes or revises nodes and edges that violate coherence norms.

The result is not a static repository of facts. It is a dynamic structure
that reflects the *current best judgment of a community of scientists* about
a complex domain. It encodes not just what they believe but *why they believe
it*, *what would change their minds*, and *where they disagree*. This is what
makes it a web of belief rather than a database.

### 16. Why the Web Is Special as a Community Belief Representation

Most scientific knowledge systems are either databases (collections of
facts without epistemological structure) or formal models (mathematical
structures without epistemological context). The CMR web is neither. It is a
**structured representation of a community's reasoning** — not just the
conclusions but the arguments, the evidence, the competing accounts, the
boundary conditions, and the uncertainty.

This is unusual. Consider how scientific knowledge is typically represented in
computational systems. A meta-analysis collapses a research literature into an
effect size and a confidence interval: "daylight improves mood, d = 0.38, 95%
CI [0.25, 0.51]." This is useful, but it throws away everything except the
bottom line. It does not tell you why daylight improves mood, which theoretical
framework supports the claim, what the competing accounts are, or what
evidence would change the conclusion. A systematic review preserves more of
the reasoning but is a natural-language document, not a computationally
queryable structure.

The CMR web preserves the reasoning in a structured, queryable form. Each
template's Toulmin justification records the data (with source, paradigm,
effect size, N, and design), the backing (why the evidence supports the
warrant), the qualifier (conditions of applicability), the rebuttal (conditions
of failure), and the competing accounts (alternative explanations). This
information is not decoration — it is the epistemological substance that
makes the web more than a collection of numbers.

Here is a concrete example of why this matters. Suppose a new study is
published tomorrow showing that the Lambert et al. (2002) finding (daylight →
5-HT synthesis) does not replicate. In a standard database, you would update
the daylight effect size and move on. In the CMR web, the consequences
propagate:

1. NM7 (Serotonergic Mood) loses its primary evidence. The template's
   confidence drops from 0.45 to (say) 0.25. The competing account (circadian
   entrainment rather than direct serotonergic modulation) gains weight.

2. T29 (Allostatic Load Master) is affected because the w_5HT input term
   becomes much more uncertain. The VOI for the 5-HT pathway increases — it is
   now the highest-priority research target.

3. The LIGHT-I cross-template interaction (daylight → 5-HT synthesis) is
   undermined, which weakens the melanopic → serotonergic chain.

4. The "sick building syndrome" mechanism (poor daylight → low 5-HT → negative
   processing bias → amplified complaints) loses its neurochemical substrate.
   The web does not delete it — it flags it as now resting on a
   THEORETICAL_DEFAULT rather than EMPIRICAL_COVARIANCE.

5. The Crucible 1 consensus from NEUROMOD-I (wanting-liking balance moderated
   by 5-HT) is weakened, because the 5-HT moderation depends on the daylight
   → 5-HT link.

All of this propagation is possible because the web encodes the *reasons* for
each belief, not just the belief itself. A database would know that the effect
size changed; the web knows *what else changes as a consequence*.

---

## Part VI: Looking Forward — What the Architecture Needs

### 17. The Projection Function: Web → BN

The most urgent technical need is a formal **projection function** that takes
the current state of the web and generates a BN. This function must:

- **Compress mechanism chains into BN edges.** A four-step mechanism chain
  becomes one or more BN edges between observable/manipulable variables, with
  CPTs derived from the chain's compound probability.

- **Translate epistemic probabilities into aleatory parameters.** This is the
  hardest part, and it requires the CPT elicitation protocol discussed
  separately. The key insight is that the translation is *lossy* — the BN
  cannot represent everything the web knows about a link. The warrant type,
  the Toulmin justification, the competing accounts, the qualifier/rebuttal
  structure — all of this is lost in the projection. The BN gets a number;
  the web retains the reasoning behind the number.

- **Regenerate whenever the web is updated.** The BN is a snapshot of the
  web's current state, projected into a computationally tractable form. When
  the web revises (a new study, a new working model, a revised mechanism
  chain), the BN must be regenerated. This "self-healing" property comes not
  from the BN's internal mechanisms but from its dependence on the web.

### 18. The Argumentation Engine

The web needs software that traverses its structure and performs the reasoning
operations described above: coherence checking, reflective equilibrium
(flagging tensions between principles and findings), VOI analysis, and
competing-account monitoring. This is not a BN task — it is a graph traversal
and constraint-satisfaction task over the web's epistemological structure.

### 19. The Feedback Loop

The BN's predictions must be systematically compared against empirical data,
and the discrepancies must be fed back to the web for diagnosis. This closes
the loop: the web generates the BN; the BN generates predictions; the
predictions are tested; the results revise the web; the web regenerates the
BN. Each cycle improves both structures.

---

## Part VII: Three Frontiers — Pushing the Architecture Further

### 20. Frontier 1: Temporal Dynamics — The Web as a History, Not a Snapshot

The FOUNDATIONS-I specification treats the web as a static structure — here are
the beliefs, here are the edges, here is the coherence score. But the web has
a history. It was different after STRESS-I (3 templates, sparse edges) than
after NEUROMOD-I (76 templates, dense edges). The Barrett-Craig model did not
exist before THERMAL-I. AX4 was an informal pattern before CREATIVE-I and a
formally elevated moderator after.

A complete calculus needs to reason about the web's *trajectory* — how it has
changed, whether the changes have been improvements, and what trajectory it is
on. This requires tracking coherence over time and asking whether each panel
left the web in a better state than it found it.

Consider a concrete example. After NEUROMOD-I added 11 templates and 17
THEORETICAL_DEFAULTs, the web gained substantial content (the neuromodulatory
systems, the allostatic load master template) but also gained substantial
uncertainty (17 parameters without empirical calibration). Did coherence
increase or decrease? The answer is not obvious. Adding well-connected nodes
that explain previously unexplained phenomena (why do people develop place
attachment? NM4 provides a mechanism) increases coherence. But adding nodes
with many THEORETICAL_DEFAULTs introduces unresolved uncertainty, which
decreases coherence. The net effect depends on the relative magnitude of these
two forces, and the calculus's coherence metric should be able to quantify it.

This leads to the question of **path dependence.** Would the web have reached
a different state if the panels had been run in a different order? If
NEUROMOD-I had come before STRESS-I, the HPA parameters would have been
calibrated in a different context. Kelly's topological methods can characterise
this: some revision strategies are order-independent (they converge to the same
state regardless of evidence ordering), while others are not. Knowing whether
the CMR's panel process is order-independent would be a significant
meta-epistemological result.

A useful formal analogy is the theory of Markov chain convergence. If the
panel process is like a Markov chain on the space of possible webs, the
question is whether the chain is ergodic — whether it converges to a unique
stationary distribution regardless of its starting state. If it is ergodic,
panel ordering does not matter in the long run. If it is not, the final web
depends on the path, and the path constitutes an epistemologically
significant design decision that must be justified.

### 21. Frontier 2: Rational Disagreement and Imprecise Credences

The FOUNDATIONS-I specification assumes that competitions are eventually
resolvable — Barrett beats Craig, or a compromise is reached. But some
scientific disagreements may be genuinely irresolvable given the available
evidence. The motor-afferent and attentional-release accounts of walking-
creativity both have some evidence. Neither has enough to win. The Crucible
resolved this by recording the disagreement and capping the confidence at 0.50.

What does it mean formally for the web to carry an unresolved competition
indefinitely? Is this a stable state (the web can function well with
unresolved competitions, producing appropriately wide uncertainty bounds on
predictions) or an unstable one (unresolved competitions accumulate and
eventually degrade the web's utility)?

The formal tool for representing irresolvable disagreement is **imprecise
probability** (Levi, 1980; Walley, 1991). Instead of assigning a single
credence to each competitor, you assign an interval: the walking-creativity
mechanism has credence [0.30, 0.60] under the motor-afferent account and
[0.25, 0.55] under the attentional-release account. The intervals overlap,
which formally represents the irresolvability. The web can compute with
interval-valued credences, and the resulting predictions inherit the
imprecision — they are wider than point-valued predictions, honestly
reflecting the genuine uncertainty.

Imprecise probabilities also interact with the BN interface. When the web
projects into the BN, interval-valued credences become interval-valued CPTs.
The BN's do-calculus then produces interval-valued interventional predictions:
"If you increase daylight, mood improves by d ∈ [0.15, 0.45]." The width of
the interval is directly informative for the architect — it says "the science
supports an effect in this range, but we genuinely cannot pin it down further
without additional research." This is more honest and more useful than a
spuriously precise point estimate.

### 22. Frontier 3: Meta-Uncertainty — The Calculus's Uncertainty About Itself

The FOUNDATIONS-I panel will produce a set of inference rules. How confident
should we be that those rules are correct? The calculus is itself a theory
(about how scientific belief revision works), and like any theory, it could be
wrong. A truly self-aware system would carry meta-level credences on its own
inference rules: "I am 0.70 confident that the conjunctive rule for
multi-parent reduction is correct, and 0.50 confident that the argumentation-
defeat protocol for competition resolution is correct."

This creates a regress (you need meta-meta-credences on the meta-credences),
which is a well-known problem in epistemology. The pragmatic resolution is to
fix a depth: one level of meta-uncertainty, treated as THEORETICAL_DEFAULTs
that can be revised by experience. When the retrodiction test (Level 2 below)
shows that the competition-resolution protocol reproduces only 60% of
historical decisions, the meta-credence for that protocol drops, and the
system knows to treat its competition-resolution outputs with greater caution.

The epistemic/aleatory distinction applies here too. The calculus's aleatory
properties are its formal consequences (given this web state, the coherence
metric produces this value — that is a mathematical fact, not uncertain). The
epistemic properties are our uncertainty about whether the calculus is the
*right* one (maybe the coherence metric tracks something other than truth).
Testing reduces the epistemic uncertainty while relying on the aleatory
properties — we trust the mathematics, and we test whether the mathematics
models the right thing.

---

## Part VIII: Testing the Calculus — Five Levels of Increasing Severity

### 23. Level 1: Internal Consistency (Sanity Checks)

**What it tests**: The calculus does not contradict itself.

**Procedure**: Encode the CMR web (93 templates, all edge types) as a typed
graph. Implement the inference rules from FOUNDATIONS-I. Run them. Check the
outputs against formal constraints:

- Do credence propagation rules produce credences in [0, 1] for every node?
- Does the coherence metric produce a finite, non-degenerate value?
- Does the structural revision protocol terminate (not loop infinitely)?
- Do partial-out rules produce non-overlapping scopes?
- Do inheritance chains produce consistent parameter values (if B inherits
  from A and C inherits from B, does C get the same value as A)?
- Are bridge warrant ceilings respected (no node's credence exceeds its
  warrant ceiling)?

**What failure means**: A calculus that fails internal consistency is formally
broken. This is not subtle — it means the rules produce contradictions,
infinities, or non-termination. Fix the rules before proceeding.

**Computational requirement**: One pass of all inference rules over the
complete web. Should complete in minutes on a modern machine if the algorithms
are properly implemented (see Part IX).

### 24. Level 2: Retrodiction — Reproducing Historical Decisions

**What it tests**: The calculus captures the reasoning that the CMR panels
actually performed.

**Procedure**: Reconstruct the web as it existed *before* each historical
decision. Apply the calculus. Check whether it recommends the same decision.

The five major decisions from the specification:
1. Barrett-Craig two-stage model adoption (THERMAL-I → CREATIVE-I)
2. Differential-mode model adoption (CREATIVE-I + NEUROMOD-I convergence)
3. AX4 perceived control elevation (CREATIVE-I Decision 2)
4. ART/SRT demotion to T1.5 (pre-pipeline assessment)
5. Aesthetic Anchoring deferral (CREATIVE-I Decision 3)

**The hard version**: There are many more decisions than these five. Every
panel made dozens of micro-decisions — which competing account to favour,
what confidence to assign, whether a cross-template interaction needed
resolution or deferral, whether a template should be Tier A or Tier B. Sample
50–100 micro-decisions from the panel outputs and post-panel reviews,
reconstruct the web state at the time each was made, apply the calculus, and
score the agreement rate.

**Scoring**:
- > 80% agreement: Strong evidence the calculus captures the panels' reasoning
- 60–80%: Moderate evidence; investigate the disagreements for systematic
  patterns (does the calculus consistently disagree on a particular edge type
  or decision type?)
- < 60%: The calculus imposes a different logic than the panels used —
  either the calculus is wrong, or the panels' informal reasoning was
  inconsistent, or both

**What failure means**: Systematic disagreement patterns are diagnostic. If
the calculus consistently disagrees on competition resolution but agrees on
everything else, the competition-resolution protocol needs work. If it
consistently disagrees on credence propagation through reduction edges, the
multi-parent rule needs revision. Each failure mode points to a specific
component of the calculus.

### 25. Level 3: Prediction — CROSSCUT-I as a Prospective Test

**What it tests**: The calculus can predict outcomes it has not seen.

**Procedure**: CROSSCUT-I has not yet been executed. Before execution, apply
the calculus to predict:

1. Which AX parameters will be most contested (the coherence metric should
   identify parameters where the web is most internally conflicted)
2. Whether ER_ECOLOGICAL_RATIONALITY_001 will achieve EMPIRICAL_COVARIANCE or
   be downgraded to stub (the bridge warrant rules should produce a
   prediction)
3. What numerical ranges AX_DOSE_RESPONSE_007 will produce (credence
   propagation over prior panel outputs should yield a prior distribution)
4. How the Aesthetic Anchoring evaluation will resolve (the competition-
   resolution protocol should predict whether the evidence suffices for
   promotion)

Write the predictions down. Seal them. Execute CROSSCUT-I. Compare.

**Scoring**: Correct prediction of 3 of 4 demonstrates non-trivial predictive
power. Correct prediction of all 4 is strong evidence. 0 of 4 means something
is wrong with the calculus. 1–2 of 4 requires investigation — which
predictions failed, and does the failure pattern point to a specific component?

**The harder test**: The calculus should also be able to identify **errors in
the existing web that the panels missed.** If the coherence metric identifies
a locally incoherent region (two templates with incompatible assumptions that
no panel flagged), that is a testable prediction: the incompatibility should
produce a measurable problem when both templates' predictions are combined in
the BN. Run the BN with both templates active and check whether the combined
prediction is degraded. If so, the calculus has detected a real problem. If
not, the "incoherence" was a false positive — which is also informative about
the coherence metric's sensitivity.

### 26. Level 4: Cross-Domain Transfer

**What it tests**: The calculus captures something general about scientific
belief revision, not just the CMR's specific content.

**Procedure**: Take a different scientific knowledge base — structurally
similar to the CMR (applied neuroscience with mechanistic pathways, bridge
warrant issues, competing accounts, and practical design implications) but
content-independent. Encode 20–30 core claims as a typed belief web using the
same edge types. Apply the FOUNDATIONS-I calculus.

**Candidate domains for transfer**:
- Air pollution and cognitive decline (PM2.5 → neuroinflammation →
  hippocampal atrophy → memory decline; bridge warrant issues between animal
  models and epidemiological associations; competing accounts of direct
  neurotoxicity vs. cardiovascular mediation)
- Psychedelic-assisted therapy (psilocybin → 5-HT2A agonism → default mode
  network disruption → therapeutic effect; bridge warrant issues between
  receptor pharmacology and clinical outcomes; competing accounts of
  mystical experience vs. neuroplasticity vs. psychological insight)
- Urban noise and cardiovascular health (traffic noise → cortisol elevation →
  endothelial dysfunction → cardiovascular disease; bridge warrant issues
  between laboratory noise studies and real-world exposure; competing
  accounts of direct autonomic vs. sleep disruption vs. psychological
  annoyance pathways)

**Scoring**: Domain experts review the calculus's outputs (coherence
assessment, competition resolution, credence propagation) and rate them for
reasonableness. If experts in the transfer domain find the outputs sensible
without knowing the calculus was developed for architecture, the calculus is
domain-general. If they find specific outputs bizarre ("why does the calculus
rate the cardiovascular mediation account so low?"), those disagreements
diagnose domain-specificity in the calculus.

### 27. Level 5: Adversarial Stress Testing

**What it tests**: The calculus handles pathological inputs gracefully.

**Procedure**: Deliberately construct webs that should stress the calculus:

| Pathological Case | Expected Behaviour |
|-------------------|--------------------|
| Credence cycle (A supports B, B supports C, C supports A) | Propagation algorithm converges to a fixed point, does not oscillate |
| Contradictory inheritance (B inherits X from A, but B's own evidence says X is different) | Conflict detection fires; resolution rule produces a determinate outcome |
| Total competition equilibrium (every competition edge is unresolved) | Coherence metric degrades gracefully; imprecise credences widen but remain bounded |
| Working model contradicted by strong evidence | Structural revision protocol fires; revision clause triggers; dependent templates are flagged |
| AX axiom contradicts domain-specific calibration at every point | Priority rule produces consistent result; either axiom overrides domain or domain overrides axiom, not a mix |
| Template with 0 confidence on all mechanism steps | Template is effectively inert; it does not contribute to downstream computations but is not deleted (preserving its structure for future evidence) |
| Circular partial-out (A partial-outs to B, B partial-outs to A) | Error detection fires; circularity is flagged as a structural defect |
| 1000-node web (10× the CMR) | Algorithm completes in reasonable time (< 1 hour on standard hardware) |

**What failure means**: Each pathological case tests a specific formal
property. Failure on the credence cycle tests convergence. Failure on
contradictory inheritance tests conflict resolution. Failure on the 1000-node
web tests scalability. Each failure is a specific bug report for the calculus.

### 28. The Ultimate Test: Discovery

The deepest test is whether the calculus can discover something that the human
experts missed. Not detect a known problem (retrodiction) or predict a
forthcoming result (prediction), but identify a *non-obvious consequence* of
the web's current state that nobody has noticed.

Examples of what a discovery would look like:
- The calculus's credence propagation reveals that a T1.5 theory (say,
  Fractal Fluency) is more strongly supported than the panels recognised,
  because it receives independent support from three T1 frameworks that
  nobody noticed converge on it.
- The calculus's VOI computation identifies that a particular
  THEORETICAL_DEFAULT has far higher value-of-information than anyone
  realised, because it sits at a bottleneck in the web's graph structure
  where many credence paths intersect.
- The calculus's coherence metric identifies a region of the web where two
  templates make incompatible assumptions that no panel flagged — and the
  incompatibility, when corrected, shifts the downstream predictions in a
  measurable way.

If the calculus can produce genuine discoveries — non-obvious truths about the
web's own structure that follow from the formal rules but were invisible to
informal reasoning — then it has demonstrated that it is not just codifying
what the panels already do but *extending their reasoning capacity*. That is
the ultimate success condition: the formal calculus makes the system smarter
than the humans who built it.

---

## Part IX: The Algorithms — How It Actually Computes

Any well-specified formalism must meet two computational requirements: the
rules must be **decidable** (there exists an algorithm that produces an answer
in finite time for any valid input) and they should be **efficiently
computable** (the algorithm runs in time that is practical for the web's actual
size). A beautiful calculus that requires exponential time to evaluate a
93-node web is a philosophical contribution, not a working system. This
section specifies the algorithms.

### 29. Data Structures: The Typed Belief Graph

The web is represented as a directed graph G = (N, E, τ_N, τ_E, θ) where:

- **N** is the set of nodes (templates, theories, axioms, working models).
  |N| ≈ 130 for the complete CMR (93 templates + 10 T1 + 10 T1.5 + 8 AX +
  2 working models + stub/candidate nodes).

- **E** ⊆ N × N is the set of directed edges. |E| ≈ 300–400 (estimated from
  the reduction links, bridge warrants, competition edges, cross-template
  interactions, inheritance links, working-model constraints, AX-axiom
  links, and partial-outs).

- **τ_N : N → {T1, T1.5, T2, AX, WM, stub}** is the node type function.

- **τ_E : E → {reduction, bridge(subtype), competition, interaction,
  inheritance, working_model, ax_axiom, partial_out}** is the edge type
  function, where bridge(subtype) ∈ {CONSTITUTIVE, MECHANISM,
  EMPIRICAL_COVARIANCE, FUNCTIONAL, CAPACITY, ANALOGICAL,
  THEORETICAL_DEFAULT}.

- **θ** is the annotation function assigning to each node its parameters:
  credence score c ∈ [0, 1] (or interval [c_lo, c_hi] for imprecise
  credences), bridge warrant ceiling w ∈ [0, 1], Toulmin structure
  (data, backing, qualifier, rebuttal, competing_accounts), and any
  domain-specific calibrated values.

The graph is stored as an adjacency list with typed edges. Each node carries
its annotation as a structured record. Total memory: O(|N| + |E| + |annotations|),
which for the CMR is on the order of megabytes — trivially small.

### 30. Algorithm 1: Credence Propagation

**Problem**: Given the current credence assignments and edge structure, compute
updated credences for all nodes that reflect the evidential support flowing
through the web's typed edges.

**Approach**: Iterative message-passing with typed propagation rules.

The algorithm is inspired by belief propagation in graphical models (Pearl,
1988) but modified for typed edges. In standard belief propagation, every edge
transmits the same kind of message (a probability distribution). In the typed
web, different edge types transmit different kinds of evidential support with
different attenuation factors.

```
ALGORITHM: TypedCredencePropagation(G, θ, max_iterations, ε)

  Input:  Typed belief graph G = (N, E, τ_N, τ_E, θ)
          max_iterations: convergence limit
          ε: convergence threshold

  Output: Updated credence assignment c'(n) for all n ∈ N

  1. Initialize: For all n ∈ N, set c⁰(n) = θ(n).credence
     (i.e., start with current credences)

  2. Define typed attenuation factors α(edge_type):
       reduction:           α = 0.90  (credence flows downward with
                                       modest attenuation)
       bridge(CONSTITUTIVE): α = 0.90
       bridge(MECHANISM):    α = 0.75
       bridge(EMPIRICAL_COV): α = 0.70
       bridge(FUNCTIONAL):   α = 0.60
       bridge(CAPACITY):     α = 0.55
       bridge(ANALOGICAL):   α = 0.45
       bridge(THEO_DEFAULT): α = 0.50
       inheritance:          α = 0.95  (parameter sharing, minimal loss)
       competition:          α = −0.30 (negative: competitors reduce
                                        each other's credence)
       interaction:          α = 0.10  (weak positive: interacting
                                        templates mildly support each other)
       working_model:        α = 0.85
       ax_axiom:             α = 0.80
       partial_out:          α = 0.00  (no credence flow; scope
                                        partition only)

  3. For iteration t = 1 to max_iterations:

     a. For each node n ∈ N:
        Compute incoming support:
          support(n) = Σ_{(m,n) ∈ E} α(τ_E(m,n)) × c^{t-1}(m)

        Handle multi-parent reduction:
          IF n has multiple reduction parents {p₁, ..., p_k}:
            IF parents provide complementary mechanisms
              (different T1 frameworks):
                parent_support = 1 - Π_i (1 - α_red × c(p_i))
                [noisy-OR: each parent independently supports]
            ELSE IF parents provide overlapping mechanisms
              (same T1 framework):
                parent_support = max_i(α_red × c(p_i))
                [max: redundant support, no double-counting]

        Apply bridge warrant ceiling:
          c_raw(n) = f(c^{t-1}(n), support(n))
          c^t(n) = min(c_raw(n), θ(n).warrant_ceiling)

        where f is the update function:
          c_raw(n) = (1 - λ) × c^{t-1}(n) + λ × sigmoid(support(n))
          λ = damping factor (0.3 recommended for convergence)
          sigmoid maps support to [0, 1]

     b. Apply entrenchment:
        T1 nodes: c^t(n) = max(c^t(n), c^{t-1}(n) - 0.01)
          [T1 nodes resist downward revision: max decrease per
           iteration is 0.01]
        T2 nodes: no entrenchment constraint
          [T2 nodes revise freely]
        T1.5, AX, WM: intermediate entrenchment
          max decrease per iteration is 0.05

     c. Convergence check:
        IF max_n |c^t(n) - c^{t-1}(n)| < ε: RETURN c^t
        [All credences have stabilised]

  4. IF max_iterations reached without convergence: FLAG WARNING
     (possible oscillation; investigate for credence cycles)

  RETURN c^{max_iterations}
```

**Decidability**: The algorithm terminates in at most max_iterations steps.
Each iteration is O(|E|) (one pass over all edges). Total worst-case:
O(max_iterations × |E|). For the CMR (|E| ≈ 400, max_iterations = 1000),
this is 400,000 operations — completes in milliseconds.

**Convergence**: The damping factor λ and the sigmoid nonlinearity guarantee
convergence for acyclic graphs. For graphs with cycles (mutual support between
beliefs), convergence is guaranteed when λ < 1/(1 + max_degree), which is a
standard result from iterative methods. For the CMR's degree distribution
(max degree ≈ 15 for T29), λ = 0.3 satisfies this condition.

**Correctness concern**: The typed attenuation factors (α values) are
themselves parameters of the algorithm. They are the computational
instantiation of the bridge warrant hierarchy's ceiling values, but they are
not identical to the ceilings — they represent the rate at which credence
propagates, not the maximum credence a node can achieve. The α values should be
calibrated by the retrodiction test (Level 2): adjust them until the
algorithm best reproduces the panels' historical credence assignments.

### 31. Algorithm 2: Competition Resolution

**Problem**: Given two or more nodes connected by competition edges, determine
which (if any) should be preferred, and update credences accordingly.

**Approach**: Graded argumentation semantics, extending Dung (1995).

```
ALGORITHM: GradedCompetitionResolution(G, θ, n_competitors)

  Input:  Set of competing nodes C = {h₁, h₂, ..., h_k}
          connected by competition edges
          Each h_i has: credence c(h_i), Toulmin structure T(h_i),
          set of supporting evidence E(h_i)

  Output: Updated credences c'(h_i) for each competitor
          Resolution status: VICTORY | COMPROMISE | EQUILIBRIUM

  1. Compute attack strength for each pair:
     For each (h_i, h_j) where i ≠ j:
       attack(h_i → h_j) = rebuttal_strength(T(h_i), T(h_j))

     where rebuttal_strength examines:
       a. Does h_i's data directly contradict h_j's data? (strong attack)
       b. Does h_i's qualifier restrict h_j's domain? (domain attack)
       c. Does h_i's mechanism provide a more complete causal pathway
          than h_j? (explanatory attack)
       d. Does h_i have a higher bridge warrant than h_j? (warrant attack)

     Each attack factor contributes additively:
       attack(h_i → h_j) = w_data × data_contradiction
                          + w_domain × domain_restriction
                          + w_explain × explanatory_superiority
                          + w_warrant × warrant_superiority
       where weights w sum to 1.0

  2. Compute net support for each competitor:
     net(h_i) = c(h_i) + Σ_{supporters} support_strength
                        - Σ_{j ≠ i} attack(h_j → h_i)

  3. Resolution:
     IF max_i(net(h_i)) - second_max > victory_threshold (e.g., 0.30):
       STATUS = VICTORY for argmax(net)
       Winner: c'(h_winner) = min(c(h_winner) + 0.10, ceiling)
       Losers: c'(h_loser) = max(c(h_loser) - 0.15, 0.05)
       [Losers retain minimal credence; they are not deleted]

     ELSE IF domain_partition_detected(attacks):
       [Domain partition: h_i attacks h_j only outside h_i's domain]
       STATUS = COMPROMISE (domain partition)
       For each h_i: c'(h_i | domain_i) = c(h_i)
                     c'(h_i | ¬domain_i) = 0.10
       Generate composite node h_composite with domain-conditional
       credences

     ELSE:
       STATUS = EQUILIBRIUM
       For each h_i: c'(h_i) = net(h_i) / Σ_j net(h_j)
       [Normalise to sum to 1; credences reflect relative support]
       Flag for imprecise probability treatment:
         c_interval(h_i) = [c'(h_i) - δ, c'(h_i) + δ]
         where δ = 0.15 (equilibrium uncertainty)

  RETURN updated credences, resolution status
```

**Decidability**: The algorithm is O(k² × |T|) where k is the number of
competitors and |T| is the size of the largest Toulmin structure. For the CMR's
typical competition (k = 2–3, |T| ≈ 10 fields), this is trivial.

**The hard part**: Computing rebuttal_strength (Step 1) requires comparing
Toulmin structures, which involves semantic comparison of qualifiers and
rebuttals. This cannot be fully automated with simple string matching — it
requires either a structured representation of qualifier domains (which the CMR
templates provide, since qualifiers specify conditions like "in buildings with
high spatial complexity") or a human/LLM-in-the-loop for ambiguous cases.

The pragmatic approach: represent qualifiers as feature vectors over a
pre-defined vocabulary of conditions (building type, occupant type, mechanism
domain, temporal scale, etc.). Two qualifiers overlap when their feature
vectors overlap. This makes domain_partition_detected computable: a domain
partition exists when h_i's qualifier features and h_j's qualifier features
are disjoint.

### 32. Algorithm 3: Global Coherence Metric

**Problem**: Compute a single number (or a small set of diagnostic numbers)
that represents how well the web's beliefs hang together.

**Approach**: Typed weighted constraint satisfaction, extending Thagard (1989).

```
ALGORITHM: TypedCoherenceMetric(G, θ)

  Input:  Typed belief graph G with current credences

  Output: Global coherence score C ∈ [-1, 1]
          Diagnostic decomposition by edge type and region

  1. For each edge (m, n) ∈ E, compute the constraint satisfaction:

     IF τ_E(m,n) ∈ {reduction, inheritance, interaction, working_model,
                     ax_axiom, bridge(any)}:
       [Positive constraint: these edges SUPPORT coherence]
       sat(m,n) = c(m) × c(n) × type_weight(τ_E(m,n))
       [High credence in both connected nodes × edge importance
        = high constraint satisfaction]

     IF τ_E(m,n) = competition:
       [Negative constraint: competition edges REDUCE coherence
        unless resolved]
       IF resolution_status(m,n) = VICTORY or COMPROMISE:
         sat(m,n) = +0.5 × type_weight(competition)
         [Resolved competition contributes positively —
          it shows the web has dealt with a tension]
       ELSE (EQUILIBRIUM / unresolved):
         sat(m,n) = -|c(m) - c(n)| × type_weight(competition)
         [Unresolved competition with similar credences =
          incoherence; the web cannot decide]

     IF τ_E(m,n) = partial_out:
       [Neutral: partial-outs neither help nor hurt coherence;
        they are structural boundaries]
       sat(m,n) = 0

  2. Edge type weights:
       reduction:      1.0  (most important for coherence)
       bridge(CONST):  0.9
       bridge(MECH):   0.8
       bridge(EMP_COV): 0.7
       bridge(FUNC):   0.5
       bridge(CAP):    0.4
       bridge(ANAL):   0.3
       bridge(THEO_D): 0.35
       competition:    0.8  (competitions are important)
       interaction:    0.4
       inheritance:    0.6
       working_model:  0.7
       ax_axiom:       0.6

  3. Compute global score:
       C = Σ_{(m,n) ∈ E} sat(m,n) / Σ_{(m,n) ∈ E} |type_weight(τ_E(m,n))|

     C ∈ [-1, 1] where:
       C = 1:  Perfect coherence (all positive constraints maximally
               satisfied, all competitions resolved)
       C = 0:  Neutral (constraints neither satisfied nor violated)
       C = -1: Perfect incoherence (all constraints violated)

  4. Diagnostic decomposition:
     For each edge type t:
       C_t = Σ_{τ_E(m,n)=t} sat(m,n) / Σ_{τ_E(m,n)=t} |type_weight(t)|
     [Shows which edge types contribute most to coherence or
      incoherence]

     For each node n:
       C_n = Σ_{(m,n) or (n,m) ∈ E} sat / Σ |weight|
     [Shows which nodes are most coherent or incoherent with
      their neighbourhood]

  RETURN C, {C_t}, {C_n}
```

**Decidability**: O(|E|) — one pass over all edges. For the CMR, this is
~400 operations. Instantaneous.

**Diagnostic value**: The decomposition is the important part. The global
score C tells you the web's overall health. The type decomposition {C_t} tells
you which kinds of connections are working well and which are not (e.g., "the
web's reduction edges are highly coherent but competition edges are dragging
coherence down — there are too many unresolved competitions"). The node
decomposition {C_n} tells you which specific templates are problematic ("NM4
has the lowest node coherence in the web because its ANALOGICAL bridge is weak
and it has an unresolved competition with goal-directed approach").

### 33. Algorithm 4: Structural Revision

**Problem**: Given new evidence that conflicts with the web's current state,
determine the minimal revision that restores coherence.

**Approach**: AGM-style revision with entrenchment ordering, extended for typed
edges.

```
ALGORITHM: StructuralRevision(G, θ, new_evidence)

  Input:  Current web G, new evidence E_new
  Output: Revised web G'

  1. Assess impact: Identify all nodes whose credence would change
     by > δ_impact (e.g., 0.10) if E_new is incorporated via
     Algorithm 1 (credence propagation).

     affected_nodes = {n : |c_new(n) - c_old(n)| > δ_impact}

  2. Classify revision type:
     IF affected_nodes all have τ_N ∈ {T2, stub}:
       TYPE = PARAMETRIC (only peripheral beliefs change)
       Apply credence propagation (Algorithm 1). DONE.

     IF any affected_node has τ_N ∈ {T1.5, AX, WM}:
       TYPE = STRUCTURAL_MODERATE (intermediate beliefs change)
       Proceed to Step 3.

     IF any affected_node has τ_N = T1:
       TYPE = STRUCTURAL_DEEP (framework-level beliefs change)
       Proceed to Step 3 with elevated caution.

  3. Compute entrenchment ordering:
     For each affected node n, compute entrenchment:
       ent(n) = base_entrenchment(τ_N(n)) × local_coherence(C_n)
                × connectivity(degree(n) / max_degree)

     where base_entrenchment:
       T1:  0.95 (very resistant)
       WM:  0.80
       AX:  0.75
       T1.5: 0.70
       T2:  0.40 (least resistant)
       stub: 0.10

     [Entrenchment combines tier (T1 beliefs resist revision),
      local coherence (well-supported beliefs resist revision),
      and connectivity (highly connected beliefs resist revision
      because revising them propagates widely)]

  4. Minimal revision:
     Sort affected_nodes by entrenchment (ascending).
     For each node n in order (least entrenched first):
       Attempt revision:
         Option A: Update credence (parametric change)
         Option B: Change edge types (e.g., upgrade bridge warrant)
         Option C: Add/remove edges (structural change)
         Option D: Change node tier (promote/demote theory)
         Option E: Add new node (new hypothesis or template)

       For each option, compute resulting coherence C' via Algorithm 3.
       Select the option that:
         (a) Accommodates E_new (the new evidence is now consistent)
         (b) Maximises C' (coherence is restored or improved)
         (c) Minimises structural change (prefer A over B over C
             over D over E — least drastic revision first)

       IF coherence restored (C' ≥ C_old - δ_acceptable): DONE.

  5. IF coherence not restored after revising all affected nodes:
     This is a DEEP REVISION — the new evidence fundamentally
     conflicts with the web's structure. Flag for human review.
     Report: which nodes were revised, what the coherence
     trajectory looked like, and where the residual incoherence is.

  RETURN G'
```

**Decidability**: The outer loop is O(|affected_nodes|), which is typically
small (new evidence usually affects < 20 nodes). For each node, evaluating
revision options requires running Algorithm 3 once per option (5 options),
which is O(|E|) each. Total: O(|affected_nodes| × 5 × |E|). For the CMR:
~20 × 5 × 400 = 40,000 operations. Fast.

**The hard part**: Option selection (Step 4) requires evaluating
counterfactual web states ("what would the web look like if I changed this
edge type?"). Each counterfactual is cheap to compute (run Algorithm 3 on
the modified graph), but the *space* of possible modifications is large
(potentially exponential in the number of affected nodes). The algorithm
handles this by processing nodes in entrenchment order and greedily selecting
the best revision at each step, which is not globally optimal but is
tractable. Optimality would require exploring all revision combinations,
which is NP-hard in general.

**Justification for greediness**: The entrenchment ordering provides a strong
heuristic. Revising the least entrenched belief first (a peripheral T2
template) is almost always the right first move, because it has the smallest
downstream impact. If that does not restore coherence, revise the next least
entrenched, and so on. The greedy approach fails only when the correct
revision involves simultaneously changing two highly-entrenched beliefs
while leaving their less-entrenched neighbours unchanged — a scenario that
is rare in practice and can be handled by the human-review fallback (Step 5).

### 34. Algorithm 5: Value of Information

**Problem**: Rank all uncertain parameters (THEORETICAL_DEFAULTs, unresolved
competitions, low-confidence mechanism steps) by their value — how much
resolving each uncertainty would improve the web.

**Approach**: Sensitivity analysis via perturbation.

```
ALGORITHM: ValueOfInformation(G, θ)

  Input:  Current web G with uncertain parameters
  Output: Ranked list of parameters by VOI

  1. Identify uncertain parameters:
     uncertainties = {
       (n, param) : θ(n).param has THEORETICAL_DEFAULT flag
                     OR c(n) < 0.50
                     OR n is in an unresolved competition
     }

  2. For each uncertain parameter u ∈ uncertainties:

     a. Compute current coherence: C_base = Algorithm3(G, θ)

     b. Simulate resolution (optimistic):
        θ_resolved = θ with u.credence = u.ceiling
        C_optimistic = Algorithm3(G, θ_resolved)

     c. Simulate resolution (pessimistic):
        θ_refuted = θ with u.credence = 0.10
        C_pessimistic = Algorithm3(G, θ_refuted)

     d. Compute expected coherence change:
        ΔC(u) = 0.5 × |C_optimistic - C_base|
               + 0.5 × |C_pessimistic - C_base|
        [Average of absolute changes under optimistic and
         pessimistic scenarios]

     e. Compute downstream reach:
        reach(u) = number of nodes reachable from u via
                   directed edges (BFS on the graph)

     f. VOI(u) = ΔC(u) × reach(u)
        [Value = coherence impact × downstream reach]

  3. Sort uncertainties by VOI (descending).
     Top of list = highest-priority research targets.

  RETURN ranked list with VOI scores
```

**Decidability**: O(|uncertainties| × (|E| + |N|)). For the CMR with
~50 THEORETICAL_DEFAULTs and ~130 nodes: 50 × 530 = 26,500 operations.
Fast.

**Practical output**: The ranked list directly produces a research agenda.
"Study 1: Measure relative neuromodulatory weights in T29 (VOI = 8.3,
resolves 7 THEORETICAL_DEFAULTs). Study 2: Replicate Lambert et al. 2002
with in-vivo methodology (VOI = 5.1, resolves 1 THEORETICAL_DEFAULT but
high reach because 5-HT feeds T29, NM7, NM2, and LIGHT-I)."

### 35. Algorithm 6: BN Projection

**Problem**: Generate a Bayesian Network from the web's current state.

**Approach**: Compress mechanism chains into BN edges; populate CPTs from web
parameters.

```
ALGORITHM: ProjectToBN(G, θ)

  Input:  Current web G
  Output: Bayesian Network B = (V, E_BN, CPTs)

  1. Identify observable/manipulable variables:
     V = {environmental parameters (daylight, noise, temperature,
          spatial configuration, social density, nature access, etc.)
         ∪ outcome variables (mood, creativity, productivity,
          satisfaction, allostatic load, etc.)}

     [These are the endpoints of mechanism chains — the variables
      an architect can control or measure. Intermediate neural
      mechanisms (DA release, 5-HT synthesis, NE tonic level) are
      NOT BN variables; they are compressed into the edges.]

  2. For each mechanism chain in the web that connects an
     environmental parameter to an outcome:

     a. Identify the endpoints: env_var → ... → outcome_var

     b. Compress the chain into a single BN edge:
        (env_var) → (outcome_var)

     c. Compute the CPT for this edge:
        For each step i in the mechanism chain:
          p_step(i) = base_effect(i) × α(bridge_type(i))
          [base_effect from the Toulmin data; α from the typed
           attenuation factors in Algorithm 1]

        CPT entry = Π_i p_step(i)
        [Product of step probabilities along the chain]

        Confidence bounds:
          CPT_lo = Π_i (p_step(i) - σ_i)
          CPT_hi = Π_i (p_step(i) + σ_i)
          where σ_i = uncertainty from Toulmin qualifier/rebuttal

     d. If multiple mechanism chains connect the same env_var to
        the same outcome_var:
        Use noisy-OR combination (independent pathways) or
        noisy-AND (dependent pathways), depending on whether
        the chains share intermediate mechanisms.

  3. Check DAG property:
     The BN must be acyclic. If the compression introduces a cycle
     (rare, because mechanism chains are temporally ordered), break
     the cycle at the weakest edge (lowest CPT value).

  4. Validate conditional independence:
     For each pair (A, B) that are d-separated in the BN given some
     set S: check that the web's mechanism chains do not contain a
     direct pathway from A to B that bypasses S. If they do, the
     BN's conditional independence assumption is violated, and an
     edge must be added.

  RETURN B = (V, E_BN, CPTs)
```

**Decidability**: Step 2 is O(|chains| × |chain_length|), which for the CMR
is approximately 93 chains × 4 steps average = 372 operations. Step 3 is
O(|V| + |E_BN|) via topological sort. Step 4 is O(|V|³) for d-separation
checking, which for ~30 variables is 27,000 operations. Total: trivially fast.

**The key compression step**: Collapsing multi-step mechanism chains into
single BN edges is where the web's epistemological richness is lost and the
BN's computational tractability is gained. The BN knows that "daylight improves
mood with probability 0.70." The web knows *why* — through the 5-HT synthesis
pathway, with Lambert et al. (2002) as primary evidence, with the circadian
entrainment account as a competitor, with the qualifier that the effect is
strongest for morning light. The BN discards all of this. The projection is
lossy by design. This is why the web must remain the primary representation
and the BN must be regenerated whenever the web changes.

### 36. Computational Complexity Summary

| Algorithm | Time Complexity | Space | CMR Runtime |
|-----------|----------------|-------|-------------|
| Credence Propagation | O(iter × \|E\|) | O(\|N\| + \|E\|) | Milliseconds |
| Competition Resolution | O(k² × \|T\|) | O(k × \|T\|) | Microseconds per competition |
| Global Coherence | O(\|E\|) | O(\|N\|) | Microseconds |
| Structural Revision | O(\|affected\| × \|E\|) | O(\|N\| + \|E\|) | Milliseconds |
| Value of Information | O(\|uncertain\| × (\|E\| + \|N\|)) | O(\|N\| + \|E\|) | Milliseconds |
| BN Projection | O(\|chains\| × \|length\| + \|V\|³) | O(\|V\| + \|E_BN\|) | Milliseconds |

All algorithms are polynomial in the web's size. All complete in milliseconds
or less for the CMR's actual graph (~130 nodes, ~400 edges). The calculus is
not only decidable but efficiently computable. It can run interactively — a
user can modify the web (add a new study, revise a parameter, introduce a
competing account) and see the updated coherence, credence propagation, and
VOI ranking in real time.

The only operation that could potentially be expensive is Algorithm 4
(Structural Revision) with a large number of affected nodes requiring
combinatorial option evaluation. The greedy heuristic (entrenchment-ordered
processing) keeps this tractable at the cost of optimality. For the rare
cases where greedy revision is inadequate, the algorithm defers to human
review — an honest acknowledgment that some revision decisions are beyond
the scope of automated inference.

### 37. What The Algorithms Do Not Do

Honesty requires specifying the algorithms' limitations:

**Semantic interpretation.** The algorithms operate over the web's formal
structure — nodes, edges, types, and numerical annotations. They do not
interpret the *meaning* of the Toulmin fields. When Algorithm 2 compares
the rebuttals of two competing hypotheses, it compares their formally
encoded features (domain restrictions, effect sizes, warrant types), not
the natural-language arguments. A rebuttal that says "this mechanism may not
apply in naturally ventilated buildings" is represented as a domain restriction
on a building-type feature, not as a prose argument. The semantic
interpretation is done once, when the template is encoded, not at runtime.

**Theory generation.** The algorithms can evaluate theories, propagate
credences, detect incoherence, and revise parameters. They cannot *generate*
new theories. If the web needs a new T1.5 theory to explain a pattern that
no existing theory covers, the algorithms will detect the gap (Algorithm 3
will show a region of low coherence, Algorithm 5 will identify high-VOI
questions) but they cannot fill it. Theory generation remains a creative act
that requires human (or LLM-simulated-panel) intelligence.

**Causal discovery.** The algorithms take the web's causal structure as given.
They do not discover new causal relationships from data. For causal discovery,
the CMR would need to supplement the web with Glymour's PC/FCI algorithms
(Spirtes, Glymour, & Scheines, 2000) or similar methods — but this requires
observational data from actual buildings, which connects to the BN's role in
empirical testing.

**Ground truth.** The algorithms compute coherence, but coherence is not
truth. A perfectly coherent web could be perfectly wrong if all its beliefs
are mutually supporting but collectively false. The safeguard against this is
empirical testing (Part VIII, Levels 3–4): the web's predictions are tested
against real-world observations, and failures trigger revision. The algorithms
handle the revision once failure is detected, but they do not detect failure
on their own — that requires the BN's predictions to be compared with data.

---

## Part X: The Full Architecture — How Everything Fits Together

### 38. The System Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    WEB OF BELIEF                             │
│                                                             │
│  ┌──────┐  reduction  ┌───────┐  reduction  ┌──────────┐   │
│  │  T1  │────────────→│ T1.5  │────────────→│    T2    │   │
│  │frames│←────────────│domain │←────────────│templates │   │
│  └──┬───┘ (bottom-up) └───┬───┘             └────┬─────┘   │
│     │                     │                      │          │
│     │    ┌────────┐       │    ┌──────────┐      │          │
│     └───→│Working │───────┘───→│ AX axioms│──────┘          │
│          │Models  │            └──────────┘                  │
│          └────────┘                                         │
│                                                             │
│  Algorithms: Credence Propagation, Competition Resolution,  │
│  Coherence Metric, Structural Revision, Value of Info       │
│                                                             │
│  Edge types: reduction, bridge(7), competition, interaction,│
│  inheritance, working_model, ax_axiom, partial_out          │
│                                                             │
│  Epistemic probabilities: confidence scores, warrant types, │
│  Toulmin justifications, competing accounts                 │
│                                                             │
└───────────────┬──────────────────────────┬──────────────────┘
                │                          │
                │  Structure + Parameters  │  Interventional
                │  (Web → BN projection)   │  predictions +
                │          │               │  Empirical feedback
                ▼          │               │  (BN → Web)
┌──────────────────────────┴───────────────┴──────────────────┐
│                    BAYESIAN NETWORK                          │
│                                                             │
│  ┌───────────┐    CPT     ┌───────────┐    CPT    ┌──────┐ │
│  │Environment│───────────→│Intermediate│─────────→│Outcome│ │
│  │ variables │            │(optional)  │          │  vars │ │
│  └───────────┘            └───────────┘          └──────┘ │
│                                                             │
│  Operations: do-calculus, counterfactual queries,           │
│  interventional prediction, confounding control             │
│                                                             │
│  Aleatory probabilities: CPTs, conditional distributions,   │
│  population frequencies                                     │
│                                                             │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            │  Predictions
                            ▼
                ┌───────────────────────┐
                │    REAL WORLD         │
                │  (buildings, people,  │
                │   measurements)       │
                │                       │
                │  Observations feed    │
                │  back to Web (via BN  │
                │  prediction errors)   │
                └───────────────────────┘
```

### 39. The Information Cycle

The full system operates as a cycle:

**Step 1 — Web generates BN.** Algorithm 6 (BN Projection) compresses the
web's mechanism chains into a BN with CPTs derived from the web's calibrated
parameters. This happens whenever the web is updated.

**Step 2 — BN generates predictions.** The BN uses do-calculus to answer
interventional questions: "If we increase daylight in this building, what is
the expected change in occupant mood, controlling for confounders?" The BN
produces point estimates with uncertainty bounds (derived from the web's
imprecise credences).

**Step 3 — Predictions are tested.** The BN's predictions are compared with
real-world observations. Discrepancies are recorded.

**Step 4 — Discrepancies feed back to web.** Large discrepancies (observed
effect differs from predicted effect by more than the uncertainty bounds)
trigger Algorithm 4 (Structural Revision) in the web. The web investigates:
is the mechanism chain wrong? Is a parameter miscalibrated? Is there a
confounding variable the BN missed? Is a competing account actually correct?

**Step 5 — Web revises.** Algorithm 4 determines the minimal revision that
accommodates the new evidence. Parameters are updated. If necessary, edges are
added, removed, or retyped. If necessary, theories are promoted, demoted, or
replaced. Algorithm 3 verifies that the revision improves coherence.

**Step 6 — Revised web generates new BN.** The cycle repeats.

Each cycle is an iteration of the fundamental epistemic process: theorise
(web), predict (BN), test (real world), revise (web). The algorithms
formalise each step. The typed edges ensure that revision respects the
structure of scientific reasoning — peripheral beliefs are revised before
central ones, mechanism claims are treated differently from analogies, and
coherence is the guiding criterion throughout.

---

## Conclusion: Two Modes of Rationality, One System

The CMR system instantiates two complementary modes of rationality. The Web of
Belief embodies what philosophers call **theoretical rationality** — the
pursuit of coherent, well-supported, explanatorily powerful understanding. It
asks: What do we believe? Why do we believe it? How does it all hang together?
What should we investigate next?

The Bayesian Network embodies what philosophers call **practical rationality**
— the pursuit of effective action under uncertainty. It asks: If I do this,
what will happen? How do I separate causation from correlation? What would have
happened in a world I did not build?

Neither mode is sufficient on its own. Theoretical rationality without
practical consequences is scholasticism — beautiful theory with no connection
to the world. Practical rationality without theoretical grounding is
engineering by curve-fitting — effective prediction with no understanding of
why it works or when it will fail.

The CMR needs both. The web provides the understanding — and can compute
quantitative consequences through its own mechanism chains. The BN provides
the causal logic: the rigorous distinction between seeing and doing, the
formal machinery for computing interventional effects in the presence of
confounders, and the counterfactual reasoning that answers "what would have
happened if?" The web tells you why high ceilings facilitate creative
cognition and how much. The BN tells you what will happen if you *intervene*
to raise the ceiling, controlling for everything else that covaries with
ceiling height. The web tells you what would change your mind. The BN tells
you what would have happened in a world you did not build. Together, they
constitute a system that not only knows things but *knows that it knows them,
knows why it knows them, and knows what it does not yet know*.

The algorithms in Part IX make this operational. They are polynomial,
implementable, and testable. They transform the philosophical architecture
from an aspiration into a computation. And the testing protocol in Part VIII
provides the empirical discipline that prevents the computation from becoming
an elaborate exercise in self-consistency — the system must not only be
coherent but must be right, and the only way to know whether it is right is
to test its predictions against the world.

That, in the end, is what a well-built epistemic architecture looks like: a
system that reasons about its own beliefs with formal precision, computes the
consequences of those beliefs with causal rigour, tests those consequences
against reality with empirical honesty, and revises itself with the minimal
change needed to accommodate what it learns. The cycle of theorise — predict —
test — revise is the oldest pattern in science. The CMR makes it explicit,
formal, and computable.

---

## References

Alchourrón, C. E., Gärdenfors, P., & Makinson, D. (1985). On the logic of
theory change: Partial meet contraction and revision functions. *Journal of
Symbolic Logic*, 50(2), 510-530.

Appleton, J. (1975). *The experience of landscape*. Wiley.

Aston-Jones, G., & Cohen, J. D. (2005). An integrative theory of locus
coeruleus-norepinephrine function: Adaptive gain and optimal performance.
*Annual Review of Neuroscience*, 28, 403-450.

Barrett, L. F. (2017). *How emotions are made: The secret life of the brain*.
Houghton Mifflin Harcourt.

Berridge, K. C. (2003). Pleasures of the brain. *Brain and Cognition*, 52(1),
106-128.

Berridge, K. C., & Robinson, T. E. (1998). What is the role of dopamine in
reward: Hedonic impact, reward learning, or incentive salience? *Brain
Research Reviews*, 28(3), 309-369.

Bovens, L., & Hartmann, S. (2003). *Bayesian epistemology*. Oxford University
Press.

Clark, A. (2013). Whatever next? Predictive brains, situated agents, and the
future of cognitive science. *Behavioral and Brain Sciences*, 36(3), 181-204.

Craig, A. D. (2002). How do you feel? Interoception: The sense of the
physiological condition of the body. *Nature Reviews Neuroscience*, 3(8),
655-666.

Dung, P. M. (1995). On the acceptability of arguments and its fundamental role
in nonmonotonic reasoning, logic programming and n-person games. *Artificial
Intelligence*, 77(2), 321-357.

Friston, K. (2010). The free-energy principle: A unified brain theory?
*Nature Reviews Neuroscience*, 11(2), 127-138.

Gärdenfors, P. (2000). *Conceptual spaces: The geometry of thought*. MIT
Press.

Glymour, C. (1980). *Theory and evidence*. Princeton University Press.

Goodman, N. (1955). *Fact, fiction, and forecast*. Harvard University Press.

Keltner, D., & Haidt, J. (2003). Approaching awe, a moral, spiritual, and
aesthetic emotion. *Cognition and Emotion*, 17(2), 297-314.

Kelly, K. T. (1996). *The logic of reliable inquiry*. Oxford University Press.

Lambert, G. W., Reid, C., Kaye, D. M., Jennings, G. L., & Esler, M. D.
(2002). Effect of sunlight and season on serotonin turnover in the brain.
*The Lancet*, 360(9348), 1840-1842.

Laudan, L. (1977). *Progress and its problems: Towards a theory of scientific
growth*. University of California Press.

Levi, I. (1980). *The enterprise of knowledge*. MIT Press.

McEwen, B. S. (1998). Stress, adaptation, and disease: Allostasis and
allostatic load. *Annals of the New York Academy of Sciences*, 840(1), 33-44.

Pearl, J. (1988). *Probabilistic reasoning in intelligent systems: Networks
of plausible inference*. Morgan Kaufmann.

Pearl, J. (2009). *Causality: Models, reasoning, and inference* (2nd ed.).
Cambridge University Press.

Prakken, H. (2010). An abstract framework for argumentation with structured
arguments. *Argument and Computation*, 1(2), 93-124.

Quine, W. V. O., & Ullian, J. S. (1970). *The web of belief*. Random House.

Rawls, J. (1971). *A theory of justice*. Harvard University Press.

Schultz, W. (1998). Predictive reward signal of dopamine neurons. *Journal of
Neurophysiology*, 80(1), 1-27.

Seeman, T. E., McEwen, B. S., Rowe, J. W., & Singer, B. H. (2001).
Allostatic load as a marker of cumulative biological risk. *Proceedings of the
National Academy of Sciences*, 98(8), 4770-4775.

Spirtes, P., Glymour, C., & Scheines, R. (2000). *Causation, prediction, and
search* (2nd ed.). MIT Press.

Thagard, P. (1989). Explanatory coherence. *Behavioral and Brain Sciences*,
12(3), 435-467.

Thagard, P. (2000). *Coherence in thought and action*. MIT Press.

Walley, P. (1991). *Statistical reasoning with imprecise probabilities*.
Chapman & Hall.

Yu, A. J., & Dayan, P. (2005). Uncertainty, neuromodulation, and attention.
*Neuron*, 46(4), 681-692.

---

*WEB_OF_BELIEF_AND_BAYESIAN_NETWORK_ARCHITECTURE.md — CMR Project*
*February 23, 2026*
*Draft for discussion — to be reduced to article-length paper*
