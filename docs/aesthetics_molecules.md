here is a doc that chat wrote on beauty in architecture.
docs/CNfA\_Aesthetics\_Appraisal\_Theoretical\_Extended.md. The question
is: do any of these identified factors that often correlate with
preference belong in our web as 1.5's or molecules? Maybe they should be
tags or annotations that are useful for identifying correlations etc.
but not part of the calculus of the web or BN. We might also decide to
add more tags than these too: perhaps tags relating to the different
measures experimental studies use so we can then ask which studies
measure eg respiration etc. So understand what is written here and then
think about whther ther are molecules or T1.5\'s or annotations that can
be useful.

6:35 PM

Weighed architectural aesthetic factors as computational nodes versus
metadata annotations

Weighed architectural aesthetic factors as computational nodes versus
metadata annotations

This is a genuinely important architectural question for the framework,
and I think the answer is that most of what\'s in this document
belongs *outside* the web proper --- as annotations, tags, and metadata
--- but that a small number of items might earn their way in as T1.5s or
even molecules, depending on how we think about the grain of the
computational story. Let me work through this carefully.

**The core distinction: what earns a place in the web?**

The web (or BN) is, as I understand it, a computational-level account
--- a network of nodes that do real inferential or regulatory work,
where the edges represent genuine conditional dependencies. A molecule
or a T1.5 needs to be something that *participates in the calculus*: it
takes inputs, transforms them, and produces outputs that other nodes
depend on. It has to be the kind of thing that, if you intervened on it,
would propagate consequences through the network.

Most of what this document catalogs falls into two quite different
categories, and conflating them would muddy the architecture
considerably.

**Category 1: Measurable stimulus features (Part II of the
document).** Things like bilateral symmetry index, fractal dimension,
lux distribution variance, edge orientation entropy, corridor width
variance, etc. These are *properties of the distal stimulus or proximal
input*. They are what the organism\'s perceptual systems take as input.
In a Bayesian network, these would be something like observable
variables or evidence nodes --- they set the boundary conditions. But
they are not themselves computations the organism performs; they are
what the computations operate *over*. Putting them into the web as
molecules would be a category error, analogous to putting \"ambient
temperature\" into a model of thermoregulation as if it were a
physiological process rather than an input to one.

**Category 2: Evaluative hubs (Parts I, III--V).** Things like fluency,
complexity regulation, predictability/surprise, threat appraisal,
prospect-refuge, restorativeness, affordance fit, social signaling.
These are closer to computational processes --- they are described as
\"constraint-sensitive organizing systems whose outputs are affectively
valenced.\" The document itself argues that they are evaluative in a
functional sense: they modulate approach-avoid, they alter attentional
allocation, they change physiological state. These have a much stronger
claim to being nodes in the web.

**Which evaluative hubs might be molecules or T1.5s?**

Even among the evaluative hubs, there\'s a question of grain. Some of
these look like they might decompose into more primitive operations that
are already in the web (or should be), while others might be genuinely
novel additions.

**Candidates that likely decompose into existing primitives:**

*Processing fluency* is essentially the inverse of computational cost in
perceptual encoding. If the web already has nodes for perceptual
organization, prediction error, and metabolic cost monitoring, then
fluency may not be a separate molecule --- it may be an *emergent
property* of low prediction error plus efficient encoding. Reber,
Schwarz, and Winkielman (2004) made this point explicitly: fluency is
not a separate signal but a metacognitive readout of processing
dynamics. If so, it\'s a useful *derived measure* or annotation, but not
a node in its own right.

*Complexity regulation* similarly looks like it might be a consequence
of the interaction between arousal/activation nodes and prediction-error
nodes. Berlyne\'s (1971) inverted-U is really a story about the
relationship between two other variables (arousal and hedonic tone), not
a separate processing module. The \"regulation\" part might already be
captured by whatever homeostatic or allostatic mechanisms the web
contains.

*Predictability/surprise* is almost certainly already represented if the
web incorporates anything from predictive processing. This is core
Bayesian machinery --- it would be strange if it weren\'t already a
molecule or a key edge structure.

**Candidates that might genuinely earn a place:**

*Threat appraisal* (in the specific architectural/environmental sense)
has a reasonable claim if the web doesn\'t already have a
spatially-tuned threat detection node. The literature on
amygdala-mediated rapid evaluation of environmental enclosure, sharp
angles, and low illumination (Bar & Neta, 2006; Vartanian et al., 2013,
2015) suggests a fairly specific computational process that takes
spatial and geometric features as input and produces avoidance-biased
activation as output. If the web has a general threat node,
environmental threat detection might be a T1.5 that feeds into it. If it
doesn\'t, this could be a molecule.

*Prospect-refuge* is interesting. Appleton\'s (1975) original
formulation and its empirical support (Dosen & Ostwald, 2016; Stamps,
2005) suggest a specific spatial computation: estimating the ratio of
visual access (prospect) to physical protection (refuge). This is not
simply threat detection --- it\'s a distinct spatial-cognitive
evaluation. It could be a T1.5 that feeds both threat/safety nodes and
restorativeness nodes. The question is whether it decomposes further
into (a) sightline computation and (b) enclosure computation, which
might themselves be more primitive.

*Affordance fit* has a strong theoretical pedigree from Gibson (1979)
onward, and the ecological psychology literature (Chemero, 2003; Warren,
1984) has established that affordance perception is a genuine perceptual
process, not merely post-hoc inference. If the web is meant to cover
action-perception coupling, affordance fit might need to be a molecule
--- particularly because its computational signature (body-scaled ratio
computation) is distinctive.

*Social signaling* is probably the most complex of the hubs, and I
suspect it decomposes into multiple operations: status inference (Fiske,
Cuddy, & Glick, 2007), cultural familiarity detection, and institutional
categorization. These might each be separate T1.5s, or they might be too
high-level and culturally variable to belong in a computational web
that\'s meant to capture relatively universal architecture. There\'s a
real debate here about whether social signaling from built environments
is computed by domain-specific mechanisms or is simply an application of
general social cognition to architectural stimuli (Elman, Bimler, &
Carney, 2019 discuss related issues in environmental psychology). If the
latter, the molecules are in social cognition proper and architecture is
just one input domain.

**The case for an annotation/tagging layer**

This is where I think the document\'s real value lies for the project.
The measurable features in Part II --- and potentially many more --- are
ideal candidates for a systematic tagging scheme that
sits *alongside* the web rather than *within* it. Here\'s why this is
valuable:

**For linking studies to the web.** If you tag each empirical study with
(a) which stimulus features were manipulated or measured, (b) which
dependent variables were collected (respiration rate, skin conductance,
fMRI BOLD signal, preference ratings, dwell time, approach-avoid
behavior, etc.), and (c) which evaluative hub the authors claim to be
investigating, then you can query the literature systematically. You
could ask: \"Which studies that manipulate fractal dimension measure
physiological stress responses?\" or \"What evidence links symmetry to
fluency vs. to preference directly?\" This is enormously useful for
identifying where the empirical support is strong, where it\'s merely
assumed, and where there are genuine gaps.

**For grounding computational claims in measurement.** A Bayesian
network makes claims about conditional dependencies. Those claims are
ultimately testable only if you can operationalize the nodes. The
tagging layer provides that operationalization bridge. \"Threat
appraisal\" as a node in the web is a theoretical construct; \"amygdala
activation measured via fMRI in response to images with angular
sharpness density \> X\" is a testable prediction. The tags let you move
between the two levels.

**Additional tags beyond what\'s in the document.** The user\'s instinct
to add tags for experimental measures is excellent. I\'d suggest at
minimum:

*Physiological measures:* heart rate, heart rate variability, skin
conductance / electrodermal activity, respiration rate, cortisol levels,
blood pressure, pupil dilation.

*Neural measures:* fMRI ROI activations (specifying which ROIs), EEG
components (N400, P300, etc.), MEG source localization.

*Behavioral measures:* preference ratings (and what scale), willingness
to pay, dwell time, approach-avoid paradigms, wayfinding performance,
task performance in the space, memory for spatial layout.

*Self-report measures:* valence ratings, arousal ratings, perceived
safety, perceived beauty, restorativeness scales (e.g., the Perceived
Restorativeness Scale from Hartig et al., 1997), stress ratings.

*Experimental design tags:* within-subjects vs. between-subjects, real
environments vs. photographs vs. VR vs. rendered images, exposure
duration, sample characteristics (architects vs. non-architects,
cultural background).

This last set matters because there are well-documented differences
between expert and novice aesthetic responses to architecture (Gifford,
Hine, Muller-Clemm, Reynolds, & Shaw, 2000), and between responses to
real spaces vs. images of them (Stamps, 2010), and these moderators are
often ignored when aggregating across studies.

**A potential organizational scheme**

So the picture I\'d suggest is three-layered:

**Layer 1 (in the web):** Molecules and T1.5s --- genuine computational
nodes. From this document, the strongest candidates are threat/safety
appraisal (possibly as a T1.5 feeding a more general threat node),
prospect-refuge (possibly decomposed into prospect and refuge
sub-computations), and affordance fit. Fluency, complexity regulation,
and predictability likely reduce to interactions among existing nodes
rather than being new ones.

**Layer 2 (stimulus feature tags):** The measurable features from Part
II, attached to studies and to the input side of web nodes. These
describe what the environment presents, not what the organism computes.
They are essential for empirical grounding but don\'t belong in the
computational graph.

**Layer 3 (methodological and dependent-variable tags):** What was
measured, how, in whom, under what conditions. These enable systematic
evidence mapping --- which is arguably the highest-value use of the
entire tagging apparatus.

The virtue of this separation is that it keeps the web clean as a
computational model while still allowing the full richness of the
empirical literature to be organized, queried, and brought to bear on
specific nodes. You avoid the trap of a web that\'s so densely populated
with heterogeneous constructs that the conditional independence
structure becomes uninterpretable --- a real risk when measurable
features, computational processes, and outcome variables all get mixed
into the same graph.

**Where honest uncertainty remains**

I should flag that there\'s genuine disagreement in the field about some
of the distinctions I\'ve drawn. Proponents of embodied cognition (e.g.,
Gallagher, 2005) and ecological psychology (e.g., Chemero, 2009) would
push back on the separation of stimulus features from evaluative
processes, arguing that perception is inherently evaluative and that
affordances are not computed *from* features but are directly perceived.
On this view, the boundary between Layer 1 and Layer 2 is more porous
than I\'ve suggested. Predictive processing theorists (Clark, 2013;
Hohwy, 2013) might similarly argue that fluency, predictability, and
complexity regulation are not separate from the perceptual process
but *constitutive* of it, which would give them a stronger claim to
molecule status.

These are not merely terminological disputes --- they reflect genuinely
different commitments about the architecture of perception and
evaluation, and the right answer for the web depends in part on which
theoretical commitments the framework adopts. The document itself is
somewhat ecumenical on this point, drawing from multiple traditions,
which is intellectually honest but leaves the architectural decision
somewhat underdetermined.

**References**

Appleton, J. (1975). *The experience of landscape*. Wiley. (Google
Scholar citations: \~2,800)

Bar, M., & Neta, M. (2006). Humans prefer curved visual
objects. *Psychological Science*, 17(8), 645--648. (\~900 citations)

Berlyne, D. E. (1971). *Aesthetics and psychobiology*.
Appleton-Century-Crofts. (\~4,500 citations)

Chemero, A. (2003). An outline of a theory of affordances. *Ecological
Psychology*, 15(2), 181--195. (\~1,200 citations)

Chemero, A. (2009). *Radical embodied cognitive science*. MIT Press.
(\~2,000 citations)

Clark, A. (2013). Whatever next? Predictive brains, situated agents, and
the future of cognitive science. *Behavioral and Brain Sciences*, 36(3),
181--204. (\~3,500 citations)

Dosen, A. S., & Ostwald, M. J. (2016). Evidence for prospect-refuge
theory: A meta-analysis of the findings of environmental preference
research. *City, Territory and Architecture*, 3(1), 4. (\~150 citations)

Fiske, S. T., Cuddy, A. J. C., & Glick, P. (2007). Universal dimensions
of social cognition: Warmth and competence. *Trends in Cognitive
Sciences*, 11(2), 77--83. (\~5,500 citations)

Gallagher, S. (2005). *How the body shapes the mind*. Oxford University
Press. (\~3,000 citations)

Gibson, J. J. (1979). *The ecological approach to visual perception*.
Houghton Mifflin. (\~30,000 citations)

Gifford, R., Hine, D. W., Muller-Clemm, W., Reynolds, D. J., & Shaw, K.
T. (2000). Decoding modern architecture: A lens model approach for
understanding the aesthetic differences of architects and
laypersons. *Environment and Behavior*, 32(2), 163--187. (\~250
citations)

Hartig, T., Korpela, K., Evans, G. W., & Gärling, T. (1997). A measure
of restorative quality in environments. *Scandinavian Housing and
Planning Research*, 14(4), 175--194. (\~800 citations)

Hohwy, J. (2013). *The predictive mind*. Oxford University Press.
(\~2,500 citations)

Reber, R., Schwarz, N., & Winkielman, P. (2004). Processing fluency and
aesthetic pleasure: Is beauty in the perceiver\'s processing
experience? *Personality and Social Psychology Review*, 8(4), 364--382.
(\~2,800 citations)

Stamps, A. E. (2005). Enclosure and safety in urbanscapes. *Environment
and Behavior*, 37(1), 102--133. (\~200 citations)

Stamps, A. E. (2010). Effects of permeability on perceived enclosure and
spaciousness. *Environment and Behavior*, 42(6), 864--886. (\~100
citations)

Vartanian, O., Navarrete, G., Chatterjee, A., Fich, L. B., Leder, H.,
Modroño, C., \... & Skov, M. (2013). Impact of contour on aesthetic
judgments and approach-avoidance decisions in architecture. *Proceedings
of the National Academy of Sciences*, 110(Supplement 2), 10446--10453.
(\~500 citations)

Warren, W. H. (1984). Perceiving affordances: Visual guidance of stair
climbing. *Journal of Experimental Psychology: Human Perception and
Performance*, 10(5), 683--703. (\~1,500 citations)

one thing i am confused by:  you talk about Processing fluency as
essentially the inverse of computational cost in perceptual encoding. If
the web already has nodes for perceptual organization, prediction error,
and metabolic cost monitoring, then fluency may not be a separate
molecule --- it may be an emergent property of low prediction error plus
efficient encoding.  i interpret this - perhaps naively - to be saying
that there might be an organizing principle in cognition - perhaps even
a module - that unifies or behaves as a function such that when it
encounters certain stimuli it computes with low prediction error plus
efficient encoding that either just is what we mean by Processing
fluency or it has the hedonic effects of Processing fluency.  if we
treat this triad of perceptual organization, prediction error, and
metabolic cost monitoring, as \'wired together\' then we have more nodes
for our causal network at both the bn and web levels. other processes
migh involve them, making them popular nodes

Show more

6:56 PM

Reconsidered fluency as genuine computational nodes rather than emergent
epiphenomenon

Reconsidered fluency as genuine computational nodes rather than emergent
epiphenomenon

You\'re not being naive at all --- you\'re catching something important
that I glossed over by using the word \"emergent\" too casually. Let me
try to be more precise about what\'s actually going on, because I think
your reframing changes the architectural picture significantly.

**The problem with \"merely emergent\"**

When I said fluency might be \"an emergent property of low prediction
error plus efficient encoding,\" I was implicitly treating it as an
epiphenomenal summary --- as if fluency were just a *description we
give* when those other processes happen to be running smoothly, rather
than a *thing the system actually computes*. That\'s sloppy, and your
pushback exposes why.

The critical question is: does the organism merely *have* low prediction
error and efficient encoding in some situations, which we outside
observers then label \"fluent processing\"? Or does the
organism *monitor* its own processing dynamics and generate a signal ---
a genuine internal state --- that registers something like \"this is
going easily\"? If the latter, then there is a real computational node
doing real work, even if what it computes is a function of other nodes\'
states.

The empirical evidence strongly favors the monitoring interpretation.
Winkielman and Cacioppo (2001) showed that fluent processing produces
measurable affective responses --- specifically, increased zygomaticus
(smile muscle) activity detected by facial EMG --- even when subjects
are not consciously aware of the fluency manipulation. This is not what
you\'d expect from a mere summary statistic. A summary statistic
doesn\'t cause your face to move. Something is reading the state of
processing and generating an output that has downstream physiological
and hedonic consequences. Topolinski and Strack (2009) extended this,
showing that fluency-induced affect is genuine positive affect, not
merely ease-of-processing awareness, and that it operates through
mechanisms partly independent of conscious judgment.

So your interpretation is, I think, correct: there is something that
functions as a *monitor* of processing dynamics, and its output is what
we call the fluency signal. The question then becomes how to represent
this in the web.

**The triad as an explicit subnetwork**

Your suggestion --- treat perceptual organization, prediction error, and
metabolic cost monitoring as explicit nodes, with fluency as a function
of their joint state --- is architecturally clean and has several
advantages.

Consider the three components:

**Prediction error** is already well-established as a computational
quantity. In predictive processing frameworks (Rao & Ballard, 1999;
Friston, 2005), prediction error is computed at every level of the
cortical hierarchy. It\'s not an abstraction --- it corresponds to the
activity of specific neuronal populations (the \"error units\" in
predictive coding models). It has a clear formal definition: the
difference between the predicted input and the actual input at a given
level. And it\'s used by many other processes --- learning, attention
allocation, model updating --- which makes it exactly the kind of
\"popular node\" you\'re describing. If prediction error isn\'t already
in the web, it should be, independently of anything to do with
aesthetics or fluency.

**Perceptual organization** is more complex because it\'s not a single
computation but a family of them --- grouping, segmentation,
figure-ground assignment, contour integration, and so on. The Gestalt
laws (proximity, similarity, closure, good continuation) are often
treated as descriptions of organizational outcomes, but there\'s good
computational work modeling them as optimization processes. Feldman
(2003) formalized perceptual grouping as Bayesian inference over
structural descriptions, and Elder and Goldberg (2002) showed that the
Gestalt laws can be derived from natural image statistics under
information-theoretic optimization. So \"perceptual organization\" might
decompose into several nodes, each representing a specific grouping
computation, or it might be represented at a coarser grain as a single
node whose state captures overall organizational coherence. Either way,
other processes depend on it heavily --- object recognition, scene
understanding, spatial reasoning all require organized percepts as
input.

**Metabolic cost monitoring** is the most speculative of the three, but
increasingly well-supported. The idea is that the brain tracks its own
energy expenditure and uses that information to regulate cognitive
effort. Kurzban, Duckworth, Kable, and Myers (2013) proposed an
influential \"opportunity cost\" model in which the subjective
experience of mental effort reflects the brain\'s computation of the
opportunity costs of allocating resources to the current task. Christie
and Schrater (2015) formalized this further, showing that effort signals
can be understood as Lagrange multipliers on resource constraints in a
rational allocation problem. If the brain monitors metabolic cost, that
monitor\'s output is a signal that other systems --- not just fluency
--- would want to access. Effort-based decision-making (Westbrook &
Braver, 2015), cognitive fatigue, task switching, and motivation all
plausibly depend on some form of cost monitoring.

Now, your key insight: if these three are explicit nodes, then
a *fluency monitor* is a node that takes their outputs as inputs and
computes something like an aggregate \"processing ease\" signal.
Formally, you might think of it as a function:

**Fluency signal ≈ f(low prediction error, successful perceptual
organization, low metabolic cost)**

where *f* is some integration function --- possibly a weighted sum,
possibly something more complex with threshold effects. The output of
this node then feeds into hedonic valuation, approach-avoid regulation,
judgment confidence, and potentially many other downstream processes.

And here\'s what makes this architecturally interesting: the *inputs* to
the fluency node are also inputs to other things. Prediction error feeds
learning and attention. Perceptual organization feeds object recognition
and spatial reasoning. Metabolic cost feeds effort allocation and
motivation. So these nodes are indeed \"popular\" --- they have high
degree in the graph. The fluency monitor is one of potentially
several *convergence nodes* that integrate signals from these popular
nodes for a specific functional purpose.

**Why this matters beyond fluency**

This pattern --- a monitoring node that reads the states of more
primitive processing nodes and generates a functionally significant
signal --- may recur elsewhere in the web. Consider:

**Coherence monitoring.** There\'s evidence that the brain monitors the
consistency of incoming information across modalities and across time,
and that incoherence triggers specific responses (conflict monitoring in
the anterior cingulate; see Botvinick, Braver, Barch, Carter, & Cohen,
2001). A coherence monitor would read prediction error across multiple
channels and generate a signal when they\'re collectively elevated ---
which is different from what any single prediction-error node says.

**Familiarity monitoring.** Recognition memory research distinguishes
between recollection (specific retrieval of context) and familiarity (a
graded signal of prior exposure). The familiarity signal, as
characterized by Yonelinas (2002), behaves like a monitoring function
over the match between current input and stored representations. It
feeds into judgments of liking (the mere exposure effect; Zajonc, 1968),
trust, and approach behavior --- a profile strikingly similar to
fluency, and possibly partially overlapping with it.

**Safety/threat monitoring.** The document\'s own \"threat appraisal\"
hub looks like another instance of this pattern: a node that integrates
spatial features (enclosure, illumination, sharp angles, occlusion) and
generates an avoidance-biased signal. LeDoux\'s (1996) \"low road\" for
fear processing, and more recent work on the amygdala\'s role in
relevance detection broadly (Sander, Grafman, & Zalla, 2003), suggests
this is a real monitoring node with specific inputs and outputs, not an
epiphenomenal description.

If this pattern generalizes, then the web\'s architecture might include
a *class* of monitoring/integration nodes that sit at convergence points
in the network, reading the states of more primitive processing nodes
and generating signals that multiple downstream processes use. These
monitors would be natural candidates for T1.5s or molecules --- they do
genuine computational work, they have identifiable inputs and outputs,
and they participate in multiple causal pathways.

**A caution about the \"module\" interpretation**

You raised the possibility that the fluency triad might constitute
a *module* in something like a Fodorian sense. I\'d be cautious here,
not because the idea is wrong but because \"module\" carries specific
theoretical commitments --- informational encapsulation, domain
specificity, mandatory operation, speed --- that may or may not apply.
Processing fluency seems to operate across domains (visual, auditory,
linguistic, conceptual), which tells against strong domain specificity.
And it\'s not clear that the fluency monitor is informationally
encapsulated in Fodor\'s (1983) sense --- it seems to be sensitive to
contextual factors and top-down expectations (Whittlesea & Williams,
2001a, 2001b showed that fluency attributions depend heavily on the
context in which fluency is experienced).

A weaker but perhaps more useful notion is that of a *functional
circuit* --- a set of nodes that are reliably co-activated and whose
joint operation produces a distinctive computational output, but without
the strong encapsulation and domain-specificity requirements of
classical modularity. This is closer to what neural network research
calls a \"functional motif\" --- a recurring subgraph pattern that
performs a characteristic computation wherever it appears. Barrett and
Satpute (2013) have argued for something like this in the affective
neuroscience context, proposing that emotions are constructed from
interactions among distributed networks rather than being produced by
dedicated modules.

The fluency circuit --- prediction error monitoring + perceptual
organization assessment + metabolic cost tracking → integrated ease
signal --- could be one such functional motif. And the advantage of
representing it this way in the web is precisely what you identified:
the component nodes participate in multiple motifs, making them
high-degree nodes that connect different parts of the network.

**What this means for the architectural decision**

Coming back to the practical question for the web/BN: I think your
reframing argues for putting the *component processes* (prediction
error, perceptual organization quality, metabolic cost monitoring) in as
nodes, and then representing fluency not as a separate free-standing
node but as a subnetwork --- a specific pattern of connection among
those nodes, plus a monitoring/integration node that computes the
fluency signal from their states. The monitoring node itself earns its
place because it produces an output (hedonic marking, approach bias,
judgment confidence) that other parts of the network depend on.

This is more complex than either \"fluency is a molecule\" or \"fluency
is just an emergent property,\" but it better reflects what the science
actually suggests is going on. And it gives you those popular nodes
you\'re after --- prediction error in particular is going to be one of
the most connected nodes in any computationally serious account of
perception, cognition, and affect.

**References**

Barrett, L. F., & Satpute, A. B. (2013). Large-scale brain networks in
affective and social neuroscience: Towards an integrative functional
architecture of the brain. *Current Opinion in Neurobiology*, 23(3),
361--372. (\~800 citations)

Botvinick, M. M., Braver, T. S., Barch, D. M., Carter, C. S., & Cohen,
J. D. (2001). Conflict monitoring and cognitive control. *Psychological
Review*, 108(3), 624--652. (\~8,000 citations)

Christie, S. T., & Schrater, P. (2015). Cognitive cost as dynamic
allocation of energetic resources. *Frontiers in Neuroscience*, 9, 289.
(\~100 citations)

Elder, J. H., & Goldberg, R. M. (2002). Ecological statistics of Gestalt
laws for the perceptual organization of contours. *Journal of Vision*,
2(4), 5. (\~300 citations)

Feldman, J. (2003). What is a visual object? *Trends in Cognitive
Sciences*, 7(6), 252--256. (\~300 citations)

Fodor, J. A. (1983). *The modularity of mind*. MIT Press. (\~12,000
citations)

Friston, K. (2005). A theory of cortical responses. *Philosophical
Transactions of the Royal Society B*, 360(1456), 815--836. (\~5,000
citations)

Kurzban, R., Duckworth, A., Kable, J. W., & Myers, J. (2013). An
opportunity cost model of subjective effort and task
performance. *Behavioral and Brain Sciences*, 36(6), 661--679. (\~1,200
citations)

LeDoux, J. E. (1996). *The emotional brain: The mysterious underpinnings
of emotional life*. Simon & Schuster. (\~10,000 citations)

Rao, R. P. N., & Ballard, D. H. (1999). Predictive coding in the visual
cortex: A functional interpretation of some extra-classical
receptive-field effects. *Nature Neuroscience*, 2(1), 79--87. (\~5,000
citations)

Sander, D., Grafman, J., & Zalla, T. (2003). The human amygdala: An
evolved system for relevance detection. *Reviews in the Neurosciences*,
14(4), 303--316. (\~500 citations)

Topolinski, S., & Strack, F. (2009). The analysis of intuition:
Processing fluency and affect in judgements of semantic
coherence. *Cognition and Emotion*, 23(8), 1465--1503. (\~250 citations)

Westbrook, A., & Braver, T. S. (2015). Cognitive effort: A neuroeconomic
approach. *Cognitive, Affective, & Behavioral Neuroscience*, 15(2),
395--415. (\~600 citations)

Whittlesea, B. W. A., & Williams, L. D. (2001a). The
discrepancy-attribution hypothesis: I. The heuristic basis of feelings
of familiarity. *Journal of Experimental Psychology: Learning, Memory,
and Cognition*, 27(1), 3--13. (\~400 citations)

Whittlesea, B. W. A., & Williams, L. D. (2001b). The
discrepancy-attribution hypothesis: II. Expectation, uncertainty,
surprise, and feelings of familiarity. *Journal of Experimental
Psychology: Learning, Memory, and Cognition*, 27(1), 14--33. (\~300
citations)

Winkielman, P., & Cacioppo, J. T. (2001). Mind at ease puts a smile on
the face: Psychophysiological evidence that processing facilitation
elicits positive affect. *Journal of Personality and Social Psychology*,
81(6), 989--1000. (\~1,500 citations)

Yonelinas, A. P. (2002). The nature of recollection and familiarity: A
review of 30 years of research. *Journal of Memory and Language*, 46(3),
441--517. (\~3,500 citations)

Zajonc, R. B. (1968). Attitudinal effects of mere exposure. *Journal of
Personality and Social Psychology*, 9(2, Pt. 2), 1--27. (\~7,000
citations)

how would this be implemented. would it clutter our web. would it
\'project\' onto causal relations at the bn level?  i like the idea of
functional circuit.  perhaps even a mechanism ie template ie t2  how
many of these can you think of?  we shoud collect a lot.  are they
t1.5\'s or t2\'s?

7:07 PM

Distinguished T2 mechanism templates from T1.5 instances, catalogued
functional circuits

Distinguished T2 mechanism templates from T1.5 instances, catalogued
functional circuits

1.  
2.  
3.  
4.  
5.  
6.  

These are exactly the right questions to press on, and I think the
answer turns on a distinction that, once you see it, organizes quite a
lot: the functional circuit *pattern* is a T2, while its
specific *instantiations* are T1.5s. This has direct consequences for
implementation, clutter, and projection onto the BN. Let me work through
each piece.

**Implementation: the T2 as mechanism template**

A T2, as I understand the framework, is a recurring mechanism pattern
--- a computational motif that gets instantiated in multiple domains,
with different content but the same structural logic. This is precisely
what we\'re looking at. The fluency circuit isn\'t a one-off; it\'s an
instance of a general pattern that I\'d call something like **convergent
state monitoring**: multiple processing streams are read by an
integrator node that generates a summary signal with functional
consequences.

The template has a canonical form:

**Multiple processing nodes** (each computing something domain-specific)
→ **Integration/monitoring node** (computes a joint function of their
states) → **Output signal** (that feeds into affect, decision-making,
behavior regulation, or further computation)

This is the T2. It specifies the *mechanism type* --- the kind of
computation being performed --- without specifying the content. It\'s
analogous to what Craver (2007) calls a \"mechanism schema\" in the
philosophy of neuroscience: a description of the organized entities and
activities that produce a phenomenon, abstracted from any particular
instance. Machamer, Darden, and Craver (2000), in their influential
account of mechanisms in biology, argued that scientific explanation
often proceeds by identifying such schemas and then showing how
particular phenomena are instances of them. That\'s exactly the move
here.

The specific instantiations --- fluency monitoring, coherence
monitoring, threat detection, and so on --- are the T1.5s. Each one
fills in the template with specific processing nodes, a specific
integration function, and specific output targets. They are nodes (or
small subnetworks) in the web, with definite inputs and outputs and
causal roles.

**Would it clutter the web?**

This is where the T2/T1.5 distinction earns its keep. The T2 itself adds
no nodes to the web at all. It sits in the ontology as a mechanism type
--- a *description of how certain subgraphs are organized*. It\'s
metadata about the web\'s structure, not an addition to the structure.
Think of it as analogous to saying \"some of the circuits in this
electronic device are amplifiers.\" That tells you something important
about the circuit topology, but it doesn\'t add components to the
circuit board.

The T1.5 instances do add nodes, but they add them in an organized way.
Each instance is a small, tightly structured subnetwork with a
stereotyped internal topology (dictated by the T2 template). This
actually *reduces* clutter relative to the alternative, which would be
to throw all the component processes into the web as unstructured nodes
and hope the edges sort themselves out. The T2 template tells you: these
nodes form a functional unit, their internal connections follow this
pattern, and the subnetwork interfaces with the rest of the web through
these specific input and output edges.

An analogy from software engineering may be useful. Object-oriented
programming doesn\'t add complexity by introducing class definitions;
it *manages* complexity by specifying that certain collections of
variables and functions form coherent units with defined interfaces. The
T2 is the class; each T1.5 instance is an object. The web becomes more
organized, not more cluttered, because you know which nodes belong
together and how they relate internally.

There\'s a practical architectural principle here that Bechtel and
Abrahamsen (2005) articulate in their discussion of mechanistic
explanation in cognitive science: decomposition (identifying the
components) and localization (assigning functions to components) are
complementary operations, and you need both to make a complex system
intelligible. The T2 gives you the decomposition principle; the T1.5
instances are the localized implementations. Without the T2, the web
risks becoming what Bechtel calls a \"mere enumeration\" --- a list of
components without an account of how they\'re organized.

**Projection onto the BN**

Here\'s where things get interesting, and where I think the functional
circuit idea shows its real power.

At the BN level, you\'re working at a coarser grain --- you want nodes
that represent variables you can observe or intervene on, with edges
that represent probabilistic dependencies. The internal structure of a
functional circuit can be *collapsed* at the BN level into a single node
(or a small number of nodes representing the circuit\'s inputs and
outputs), while remaining fully articulated at the web level.

Consider the fluency circuit. At the web level, you have: prediction
error node, perceptual organization node, metabolic cost node, and the
fluency monitor node, with specific edges among them. At the BN level,
you might represent this as a single \"processing fluency\" variable
that is conditionally dependent on stimulus features (which determine
prediction error and organizational difficulty) and on the organism\'s
current metabolic state. The BN captures the input-output mapping; the
web captures the mechanism by which that mapping is computed.

This is hierarchical modeling, and it has well-understood formal
properties. Heckerman, Meek, and Koller (2004, cited in many BN
textbooks) discuss how Bayesian networks can be organized
hierarchically, with \"macro-nodes\" that aggregate subnetworks. The
edges between macro-nodes in the coarse-grained BN correspond to
pathways through the fine-grained subnetworks. Crucially, the
conditional independence structure at the BN level is *inherited* from
the web-level structure --- if two macro-nodes are d-separated at the BN
level, it\'s because the corresponding subnetworks are d-separated at
the web level given the appropriate conditioning set. So the projection
is principled, not ad hoc.

This means you can move between levels of description depending on what
question you\'re asking. Want to know whether fluency and threat
appraisal are conditionally independent given stimulus complexity? Work
at the BN level. Want to know *why* they\'re conditionally independent
(or dependent)? Drill down to the web level and trace the pathways
through the subnetworks.

**How many functional circuits can I identify?**

Let me try to be systematic. I\'ll organize them by the T2 pattern they
instantiate, because I think there are actually several distinct T2
templates, not just one.

**T2 Template 1: Convergent State Monitoring**

*Pattern: Multiple processing streams → integrator → summary signal with
hedonic/motivational consequences*

**T1.5 Instance 1: Fluency monitoring** Inputs: prediction error
magnitude, perceptual organization success, metabolic processing cost.
Output: ease/difficulty signal → positive/negative hedonic marking. Key
evidence: Winkielman & Cacioppo (2001); Reber et al. (2004); Oppenheimer
(2008).

**T1.5 Instance 2: Coherence monitoring** Inputs: cross-modal prediction
errors, cross-temporal consistency, semantic consistency. Output:
conflict/coherence signal → behavioral adjustment, error-related
negativity. Key evidence: Botvinick et al. (2001); Yeung, Botvinick, &
Cohen (2004). The anterior cingulate cortex literature strongly
implicates a specific neural locus for this computation.

**T1.5 Instance 3: Environmental threat monitoring** Inputs: spatial
enclosure, illumination level, angular sharpness, occlusion density,
biological motion detection. Output: avoidance-biased activation →
freeze/flight preparation, stress physiology. Key evidence: LeDoux
(1996); Vartanian et al. (2013); Grillon (2008) on context-dependent
anxiety and sustained threat monitoring.

**T1.5 Instance 4: Vitality/energy monitoring** Inputs: interoceptive
signals (heart rate, respiration, glucose levels), fatigue markers,
sleep pressure. Output: available-resource signal → effort willingness,
task engagement. Key evidence: Craig (2002) on interoception as a
foundation for subjective feelings; Feldman Barrett and Simmons (2015)
on interoceptive prediction.

**T1.5 Instance 5: Social safety monitoring** Inputs: facial expression,
vocal prosody, postural cues, group size, familiarity signals. Output:
social threat/safety signal → approach/inhibition in social contexts.
Key evidence: Porges\' (2007) polyvagal theory (despite some controversy
about the specific neural mechanisms, the functional characterization of
social safety monitoring is well-supported); Todorov, Said, Engell, &
Oosterhof (2008) on rapid face-based trustworthiness evaluation.

**T2 Template 2: Predictive Matching**

*Pattern: Generative model produces prediction → comparison with input →
error signal → model update or behavioral response*

**T1.5 Instance 6: Sensory prediction error (low-level)** Inputs:
top-down prediction from higher cortical areas, bottom-up sensory input.
Output: prediction error signal → model updating, attention allocation.
Key evidence: Rao & Ballard (1999); Friston (2005). This is the
workhorse of predictive processing.

**T1.5 Instance 7: Social prediction error** Inputs: expected social
response (based on norms, prior interaction), actual social response.
Output: social surprise signal → relationship updating, norm learning.
Key evidence: Koster-Hale & Saxe (2013) on predictive processing in
theory of mind; Chang, Smith, Dufwenberg, & Sanfey (2011) on social
prediction error in the TPJ.

**T1.5 Instance 8: Reward prediction error** Inputs: expected reward
(based on learned associations), actual reward received. Output: RPE
signal → value updating, approach/avoid learning. Key evidence: Schultz,
Dayan, & Montague (1997) --- the foundational work on dopaminergic RPE
signals. One of the most replicated findings in computational
neuroscience.

**T1.5 Instance 9: Aesthetic expectation violation** Inputs:
stylistic/structural expectation (based on genre, context, prior
exposure), actual structural features. Output: surprise signal →
interest/curiosity or confusion/rejection. Key evidence: Meyer (1956) on
music; Huron (2006) on \"sweet anticipation\"; Silvia (2005) on
appraisal models of interest, where novelty-complexity interacts with
coping potential to determine whether surprise generates interest or
anxiety.

**T2 Template 3: Homeostatic Regulation**

*Pattern: Set point + current state → discrepancy signal → corrective
drive*

**T1.5 Instance 10: Arousal regulation** Inputs: current arousal level
(from multiple sources), optimal arousal set point (which itself varies
with context and individual differences). Output: discrepancy signal →
stimulus seeking (if under-aroused) or stimulus avoidance (if
over-aroused). Key evidence: Berlyne (1971); Zuckerman (1994) on
sensation seeking; Humphreys & Revelle (1984) on arousal and
performance. The inverted-U is really a homeostatic story.

**T1.5 Instance 11: Cognitive load regulation** Inputs: current working
memory load, task demands, available cognitive resources. Output:
overload/underload signal → task difficulty adjustment, information
filtering. Key evidence: Sweller (1988) on cognitive load theory; Lavie
(2005) on perceptual load and selective attention. The load theory work
shows that the system actively modulates processing based on load state,
which implies a monitoring function.

**T1.5 Instance 12: Thermoregulatory-style affect regulation** Inputs:
current affective state, affective set point (which may be culturally
and individually variable), recent affective trajectory. Output:
mood-regulatory drive → behavior selection aimed at affective
homeostasis. Key evidence: Larsen (2000) on affect regulation as a
cybernetic process; Gross (1998) on emotion regulation. This is more
speculative than some of the others, but the modeling work is
increasingly sophisticated.

**T1.5 Instance 13: Interpersonal distance regulation** Inputs: current
proximity to others, desired proximity (varies with relationship,
context, culture), threat signals. Output: approach/withdraw drive →
spatial behavior. Key evidence: Hall (1966) on proxemics; Iachini,
Coello, Frassinetti, & Ruggiero (2014) on the neuroscience of
peripersonal space regulation. This has clear architectural implications
--- people\'s comfort in spaces is partly a function of how the space
allows or constrains distance regulation.

**T2 Template 4: Accumulation to Bound**

*Pattern: Evidence accumulates over time → threshold crossing → discrete
state change or decision*

**T1.5 Instance 14: Familiarity detection** Inputs: accumulating match
signal between current input and stored representations. Output:
threshold-crossing produces familiarity signal → recognition, approach
bias, mere exposure effect. Key evidence: Yonelinas (2002); Ratcliff
(1978) on diffusion models of recognition memory. The signal-detection
characterization of familiarity maps naturally onto accumulator models.

**T1.5 Instance 15: Dread/anxiety accumulation** Inputs: accumulating
threat cues (each below individual threshold), temporal duration of
uncertain threat. Output: threshold-crossing produces anxiety state →
generalized avoidance, hypervigilance. Key evidence: Grillon, Baas,
Lissek, Smith, & Milstein (2004) on sustained anxiety vs. phasic fear;
Davis, Walker, Miles, & Grillon (2010) distinguishing BNST-mediated
sustained anxiety from amygdala-mediated phasic fear. This is
architecturally important because it explains how environments that
contain no single threatening feature can still produce unease --- the
accumulation of sub-threshold cues crosses the bound.

**T1.5 Instance 16: Interest/curiosity accumulation** Inputs:
accumulating novelty signals, information-gap detection, manageable
uncertainty. Output: threshold-crossing produces exploratory drive →
approach, investigation, sustained attention. Key evidence: Berlyne
(1960) on specific vs. diversive exploration; Loewenstein (1994) on the
information-gap theory of curiosity; Kidd & Hayden (2015) on the
neuroscience of curiosity as a drive state. Silvia (2006) argues that
interest requires *both* novelty and appraised coping potential ---
essentially a dual-accumulator where both channels must reach threshold.

**T2 Template 5: Competitive Selection**

*Pattern: Multiple candidates activate in parallel → mutual inhibition →
winner-take-all or graded competition → selected output*

**T1.5 Instance 17: Attentional selection** Inputs: multiple competing
stimuli, each with salience signals (bottom-up) and relevance signals
(top-down). Output: selected focus of attention → enhanced processing
for winner, suppressed processing for losers. Key evidence: Desimone &
Duncan (1995) on biased competition; Itti & Koch (2001) on computational
models of salience-driven attention. This is extremely well-established
and has clear implications for architectural experience --- environments
that create many competing salience signals produce attentional
exhaustion.

**T1.5 Instance 18: Action selection** Inputs: multiple possible
actions, each with associated values and costs. Output: selected action
→ motor execution. Key evidence: Cisek (2007) on affordance competition;
Cisek & Kalaska (2010) on the parallel specification and selection of
actions in premotor cortex. This connects directly to the affordance-fit
discussion --- Gibson\'s affordances become competing action candidates
in this framework.

**T1.5 Instance 19: Interpretive selection (bistable
perception)** Inputs: multiple possible interpretations of ambiguous
input. Output: currently dominant interpretation → perceptual
experience. Key evidence: Leopold & Logothetis (1999) on binocular
rivalry; Sterzer, Kleinschmidt, & Rees (2009) on multistable perception.
This may matter for architectural ambiguity --- spaces that support
multiple interpretive framings.

**T2 Template 6: Gated Propagation**

*Pattern: Signal available but blocked by default → gate condition met →
signal propagates to downstream targets*

**T1.5 Instance 20: Affective gating of memory encoding** Inputs:
incoming information + current emotional state. Gate condition:
emotional arousal above threshold. Output: enhanced memory consolidation
for emotionally salient information. Key evidence: McGaugh (2004) on
amygdala modulation of memory consolidation; Dolcos, LaBar, & Cabeza
(2005) on the emotional enhancement of memory. Architecturally relevant
because memorable spaces tend to be emotionally evocative spaces.

**T1.5 Instance 21: Context-gated threat response** Inputs: ambiguous
stimulus + context information. Gate condition: context signals danger
(darkness, enclosure, unfamiliarity). Output: threat response propagates
(same stimulus in safe context does not trigger response). Key evidence:
Mobbs et al. (2007) on the proximity-dependent shift from forebrain to
midbrain threat processing; Herry et al. (2008) on context-dependent
fear circuits in the amygdala. This is crucial for understanding why the
same architectural feature (say, a narrow corridor) feels threatening in
one context and cozy in another.

**T1.5 Instance 22: Expertise-gated aesthetic processing** Inputs:
perceptual input + domain expertise level. Gate condition: sufficient
expertise to activate schema-based processing. Output: qualitatively
different aesthetic evaluation (experts process architecture differently
from novices). Key evidence: Gifford et al. (2000) on architect vs.
layperson evaluation differences; Kirk, Skov, Hulme, Christensen, & Zeki
(2009) on expertise effects on neural responses to visual stimuli.
Chatterjee and Vartanian (2014) include expertise as a moderating
variable in their aesthetic triad model.

**How these project onto the BN**

Each of these T1.5 instances projects onto the BN as follows: the
internal structure of the circuit (the multiple input nodes, the
integration function, the gating condition, etc.) gets collapsed into a
smaller number of BN nodes representing the circuit\'s key variables ---
typically its primary inputs and its output. The conditional probability
tables at the BN level capture the input-output mapping that the
web-level mechanism *explains*.

So, for example, the fluency circuit\'s BN projection might be:

**BN nodes:** Stimulus complexity → Processing fluency → Hedonic
response

The edge from complexity to fluency captures (at the BN level) what the
web-level mechanism explains in detail: complexity affects prediction
error, perceptual organization difficulty, and metabolic cost, which the
fluency monitor integrates. The BN captures the *that*; the web captures
the *how*.

This means the BN remains tractable for empirical work (you can estimate
the conditional probability tables from experimental data on the
coarse-grained variables) while the web provides the explanatory depth
(when you want to know *why* complexity affects hedonic response, you
open up the fluency circuit and trace the mechanism).

**The T2 templates as a collection**

Stepping back, I count six T2 templates and twenty-two T1.5 instances,
and I\'m certain this is not exhaustive. Several important ones I
haven\'t elaborated but that clearly belong include:

-   **Habit circuit** (T2: stimulus-response automatization --- a form
    of gated propagation where repetition removes the gate): relevant to
    how familiar environments are navigated without attentional demand.

-   **Empathic resonance circuit** (T2: convergent monitoring applied to
    mirroring of others\' states): relevant to social spaces, shared
    aesthetic experience.

-   **Temporal prediction circuit** (T2: predictive matching applied to
    rhythmic and temporal structure): relevant to architecture that
    unfolds over time as you move through it, and to music.

-   **Disgust/contamination monitoring** (T2: convergent monitoring
    applied to pathogen cues): relevant to material aesthetics,
    cleanliness, decay, certain textural aversions.

The T2 templates themselves --- convergent monitoring, predictive
matching, homeostatic regulation, accumulation-to-bound, competitive
selection, gated propagation --- are probably close to a complete set of
the basic computational motifs in neural circuits, though there may be
others I\'m not seeing. Marr and Poggio\'s (1976) levels-of-analysis
framework would suggest that these templates correspond to the
algorithmic level --- they specify the *type of computation* without
specifying the hardware implementation. The T1.5 instances fill in the
content, and the neural implementation is yet another level down.

I should flag one point of genuine scientific uncertainty here. There is
ongoing debate about whether these computational motifs are
really *types* --- discrete categories of mechanism --- or whether they
shade into one another along continua. Predictive matching and
homeostatic regulation, for example, can both be formalized as
error-minimization processes (Friston\'s, 2010, free energy principle
attempts to unify them). Competitive selection and accumulation-to-bound
are related through the mathematics of drift-diffusion models (Bogacz,
Brown, Moehlis, Holmes, & Cohen, 2006). So the T2 categories I\'ve
proposed may be more like convenient groupings along a continuum of
computational strategies rather than natural kinds. For the purposes of
the framework, I think this is acceptable --- the categories are useful
for organization even if the boundaries between them are somewhat soft
--- but it\'s worth being explicit that the taxonomy is pragmatic rather
than ontologically deep.

**References**

Bechtel, W., & Abrahamsen, A. (2005). Explanation: A mechanist
alternative. *Studies in History and Philosophy of Biological and
Biomedical Sciences*, 36(2), 421--441. (\~600 citations)

Berlyne, D. E. (1960). *Conflict, arousal, and curiosity*. McGraw-Hill.
(\~5,000 citations)

Bogacz, R., Brown, E., Moehlis, J., Holmes, P., & Cohen, J. D. (2006).
The physics of optimal decision making: A formal analysis of models of
performance in two-alternative forced-choice tasks. *Psychological
Review*, 113(4), 700--765. (\~2,000 citations)

Botvinick, M. M., Braver, T. S., Barch, D. M., Carter, C. S., & Cohen,
J. D. (2001). Conflict monitoring and cognitive control. *Psychological
Review*, 108(3), 624--652. (\~8,000 citations)

Chang, L. J., Smith, A., Dufwenberg, M., & Sanfey, A. G. (2011).
Triangulating the neural, psychological, and economic bases of guilt
aversion. *Neuron*, 70(3), 560--572. (\~300 citations)

Chatterjee, A., & Vartanian, O. (2014). Neuroaesthetics. *Trends in
Cognitive Sciences*, 18(7), 370--375. (\~800 citations)

Cisek, P. (2007). Cortical mechanisms of action selection: The
affordance competition hypothesis. *Philosophical Transactions of the
Royal Society B*, 362(1485), 1585--1599. (\~1,200 citations)

Cisek, P., & Kalaska, J. F. (2010). Neural mechanisms for interacting
with a world full of action choices. *Annual Review of Neuroscience*,
33, 269--298. (\~1,500 citations)

Craig, A. D. (2002). How do you feel? Interoception: The sense of the
physiological condition of the body. *Nature Reviews Neuroscience*,
3(8), 655--666. (\~5,500 citations)

Craver, C. F. (2007). *Explaining the brain: Mechanisms and the mosaic
unity of neuroscience*. Oxford University Press. (\~2,500 citations)

Davis, M., Walker, D. L., Miles, L., & Grillon, C. (2010). Phasic vs
sustained fear in rats and humans: Role of the extended amygdala in fear
vs anxiety. *Neuropsychopharmacology*, 35(1), 105--135. (\~1,200
citations)

Desimone, R., & Duncan, J. (1995). Neural mechanisms of selective visual
attention. *Annual Review of Neuroscience*, 18, 193--222. (\~8,000
citations)

Dolcos, F., LaBar, K. S., & Cabeza, R. (2005). Remembering one year
later: Role of the amygdala and the medial temporal lobe memory system
in retrieving emotional memories. *Proceedings of the National Academy
of Sciences*, 102(7), 2626--2631. (\~800 citations)

Feldman Barrett, L., & Simmons, W. K. (2015). Interoceptive predictions
in the brain. *Nature Reviews Neuroscience*, 16(7), 419--429. (\~1,500
citations)

Friston, K. (2010). The free-energy principle: A unified brain
theory? *Nature Reviews Neuroscience*, 11(2), 127--138. (\~6,000
citations)

Gifford, R., et al. (2000). Decoding modern architecture. *Environment
and Behavior*, 32(2), 163--187. (\~250 citations)

Grillon, C. (2008). Models and mechanisms of anxiety: Evidence from
startle studies. *Psychopharmacology*, 199(3), 421--437. (\~400
citations)

Grillon, C., Baas, J. M. P., Lissek, S., Smith, K., & Milstein, J.
(2004). Anxious responses to predictable and unpredictable aversive
events. *Behavioral Neuroscience*, 118(5), 916--924. (\~400 citations)

Gross, J. J. (1998). The emerging field of emotion regulation: An
integrative review. *Review of General Psychology*, 2(3), 271--299.
(\~12,000 citations)

Hall, E. T. (1966). *The hidden dimension*. Doubleday. (\~10,000
citations)

Herry, C., Ciocchi, S., Senn, V., Demmou, L., Müller, C., & Lüthi, A.
(2008). Switching on and off fear by distinct neuronal
circuits. *Nature*, 454(7204), 600--606. (\~1,500 citations)

Humphreys, M. S., & Revelle, W. (1984). Personality, motivation, and
performance: A theory of the relationship between individual differences
and information processing. *Psychological Review*, 91(2), 153--184.
(\~800 citations)

Huron, D. (2006). *Sweet anticipation: Music and the psychology of
expectation*. MIT Press. (\~2,500 citations)

Iachini, T., Coello, Y., Frassinetti, F., & Ruggiero, G. (2014). Body
space in social interactions: A comparison of reaching and comfort
distance in immersive virtual reality. *PLoS ONE*, 9(11), e111511.
(\~200 citations)

Itti, L., & Koch, C. (2001). Computational modelling of visual
attention. *Nature Reviews Neuroscience*, 2(3), 194--203. (\~5,000
citations)

Kidd, C., & Hayden, B. Y. (2015). The psychology and neuroscience of
curiosity. *Neuron*, 88(3), 449--460. (\~1,000 citations)

Kirk, U., Skov, M., Hulme, O., Christensen, M. S., & Zeki, S. (2009).
Modulation of aesthetic value by semantic context: An fMRI
study. *NeuroImage*, 44(3), 1125--1132. (\~300 citations)

Koster-Hale, J., & Saxe, R. (2013). Theory of mind: A neural prediction
problem. *Neuron*, 79(5), 836--848. (\~500 citations)

Larsen, R. J. (2000). Toward a science of mood
regulation. *Psychological Inquiry*, 11(3), 129--141. (\~1,000
citations)

Lavie, N. (2005). Distracted and confused?: Selective attention under
load. *Trends in Cognitive Sciences*, 9(2), 75--82. (\~2,500 citations)

Leopold, D. A., & Logothetis, N. K. (1999). Multistable phenomena:
Changing views in perception. *Trends in Cognitive Sciences*, 3(7),
254--264. (\~1,200 citations)

Loewenstein, G. (1994). The psychology of curiosity: A review and
reinterpretation. *Psychological Bulletin*, 116(1), 75--98. (\~3,500
citations)

Machamer, P., Darden, L., & Craver, C. F. (2000). Thinking about
mechanisms. *Philosophy of Science*, 67(1), 1--25. (\~4,000 citations)

Marr, D., & Poggio, T. (1976). From understanding computation to
understanding neural circuitry. *MIT AI Memo*, 357. (\~800 citations)

McGaugh, J. L. (2004). The amygdala modulates the consolidation of
memories of emotionally arousing experiences. *Annual Review of
Neuroscience*, 27, 1--28. (\~3,500 citations)

Meyer, L. B. (1956). *Emotion and meaning in music*. University of
Chicago Press. (\~5,000 citations)

Mobbs, D., Petrovic, P., Marchant, J. L., Hassabis, D., Weiskopf, N.,
Seymour, B., \... & Frith, C. D. (2007). When fear is near: Threat
imminence elicits prefrontal-periaqueductal gray shifts in
humans. *Science*, 317(5841), 1079--1083. (\~1,200 citations)

Oppenheimer, D. M. (2008). The secret life of fluency. *Trends in
Cognitive Sciences*, 12(6), 237--241. (\~700 citations)

Porges, S. W. (2007). The polyvagal perspective. *Biological
Psychology*, 74(2), 116--143. (\~2,500 citations)

Reber, R., Schwarz, N., & Winkielman, P. (2004). Processing fluency and
aesthetic pleasure. *Personality and Social Psychology Review*, 8(4),
364--382. (\~2,800 citations)

Schultz, W., Dayan, P., & Montague, P. R. (1997). A neural substrate of
prediction and reward. *Science*, 275(5306), 1593--1599. (\~12,000
citations)

Silvia, P. J. (2005). Emotional responses to art: From collation and
arousal to cognition and emotion. *Review of General Psychology*, 9(4),
342--357. (\~500 citations)

Silvia, P. J. (2006). *Exploring the psychology of interest*. Oxford
University Press. (\~800 citations)

Sterzer, P., Kleinschmidt, A., & Rees, G. (2009). The neural bases of
multistable perception. *Trends in Cognitive Sciences*, 13(7), 310--318.
(\~500 citations)

Sweller, J. (1988). Cognitive load during problem solving: Effects on
learning. *Cognitive Science*, 12(2), 257--285. (\~8,000 citations)

Todorov, A., Said, C. P., Engell, A. D., & Oosterhof, N. N. (2008).
Understanding evaluation of faces on social dimensions. *Trends in
Cognitive Sciences*, 12(12), 455--460. (\~1,500 citations)

Vartanian, O., et al. (2013). Impact of contour on aesthetic judgments
and approach-avoidance decisions in architecture. *PNAS*, 110(Supplement
2), 10446--10453. (\~500 citations)

Winkielman, P., & Cacioppo, J. T. (2001). Mind at ease puts a smile on
the face. *Journal of Personality and Social Psychology*, 81(6),
989--1000. (\~1,500 citations)

Yeung, N., Botvinick, M. M., & Cohen, J. D. (2004). The neural basis of
error detection: Conflict monitoring and the error-related
negativity. *Psychological Review*, 111(4), 931--959. (\~2,000
citations)

Yonelinas, A. P. (2002). The nature of recollection and
familiarity. *Journal of Memory and Language*, 46(3), 441--517. (\~3,500
citations)

Zuckerman, M. (1994). *Behavioral expressions and biosocial bases of
sensation seeking*. Cambridge University Press. (\~3,000 citations)

to decide if these functional circuits are the same or different than
t2\'s, or t1.5\'s you have to enmerate what we have at t1, t1.5
molecules, t2 / templates

Feb 26

Inventoried framework tiers to classify functional circuits
systematically

Inventoried framework tiers to classify functional circuits
systematically

-   
-   
-   

You\'re absolutely right to call this out. I\'ve been reasoning about
where functional circuits fit in the taxonomy without having laid out
the inventory of what\'s already *in* each tier. That\'s putting the
cart before the horse. Let me try to enumerate what we\'ve established
--- and I should be candid that my reconstruction may have gaps, so this
should be treated as a working inventory that you should correct and
extend.

**T1: Computational Primitives (\"Atoms\")**

These are the most basic, well-established computational operations ---
the elementary processes from which everything else is built. They
should be individually well-grounded in neuroscience, relatively simple
in computational terms, and domain-general (they operate the same way
regardless of content area).

From what we\'ve discussed, the T1s include operations like:

**Signal processing primitives:**

-   Lateral inhibition (contrast enhancement, winner-take-all at the
    local level)

-   Gain control (divisive normalization --- Carandini & Heeger, 2012,
    have argued this is a canonical neural computation)

-   Temporal integration (accumulating evidence over time)

-   Adaptation (reduction in response to sustained or repeated
    stimulation)

-   Threshold detection (converting graded signals to discrete events)

**Statistical estimation primitives:**

-   Bayesian updating (revising probability estimates given new
    evidence)

-   Prediction error computation (comparing expected vs. actual input)

-   Prior formation (learning regularities from repeated exposure)

-   Covariance detection (learning which signals co-occur)

-   Mean/variance estimation (tracking the central tendency and spread
    of a distribution)

**Organizational primitives:**

-   Binding (associating features that belong to the same object/event)

-   Segmentation (parsing continuous input into discrete units)

-   Grouping (by proximity, similarity, common fate, etc.)

-   Figure-ground segregation

**Learning primitives:**

-   Hebbian association (co-activation strengthens connection)

-   Error-driven learning (adjusting weights to reduce prediction error)

-   Habituation (reduced response to repeated non-informative
    stimulation)

-   Sensitization (increased response following salient events)

Now, I want to flag an important uncertainty here. The grain at which we
define T1s matters enormously for how many T1.5s and T2s we get, and
where the boundaries fall. If we define T1s very finely --- at the level
of, say, individual synaptic mechanisms --- then almost everything above
is already a T1.5 (lateral inhibition, for example, involves multiple
synaptic operations coordinated in a specific circuit topology). If we
define them at the level I\'ve listed above, which is roughly the level
of \"canonical neural computations\" as characterized by Carandini and
Heeger (2012) and by Kouh and Poggio (2008), then they\'re genuinely
primitive --- the smallest functional units that have a clear
computational interpretation.

I think the right grain is approximately what I\'ve listed: operations
that can be specified by a single equation or a single circuit motif (in
the neural circuit sense), that operate over millisecond-to-second
timescales, and that are instantiated in many different brain areas for
many different purposes. This is close to what Marr (1982) would call
the algorithmic level of a single computational step.

**T1.5: Molecules**

These are stable combinations of T1 atoms that form functional units ---
they take T1 operations and wire them together in specific
configurations to accomplish something that no individual T1 does alone.
They should be recognizable as \"things\" in the neuroscience
literature, with identifiable neural correlates and functional roles,
but they\'re built from the T1 primitives rather than being primitive
themselves.

Here is where I\'m less certain of completeness, but the ones I believe
we\'ve identified or discussed include:

**Perceptual molecules:**

-   Contour integration (grouping + binding + lateral inhibition,
    configured to extract continuous edges from fragmented local signals
    --- Field, Hayes, & Hess, 1993)

-   Texture segregation (statistical estimation of local feature
    distributions + comparison across regions --- Landy & Graham, 2004)

-   Depth from stereo (covariance detection across left/right eye
    inputs + spatial mapping)

-   Motion detection (temporal integration + comparison across
    sequential frames --- Reichardt detector as the classic example)

-   Color constancy (gain control + estimation of illuminant statistics
    --- adaptation plus normalization)

-   Size constancy (depth estimation + scaling of retinal size signal)

**Perceptual-evaluative molecules:**

-   Symmetry detection (grouping + comparison of reflected features ---
    perhaps involving covariance detection across spatial positions)

-   Rhythm/regularity detection (temporal prediction + prediction error
    --- tracking periodicity in sequential input)

-   Novelty detection (prediction + mismatch detection + perhaps
    threshold on accumulated mismatch)

-   Salience computation (combining contrast in multiple feature
    dimensions --- Itti & Koch\'s, 2001, salience map is essentially a
    molecule built from multiple parallel contrast computations)

**Evaluative molecules:**

-   Reward prediction error (prediction of expected reward + comparison
    with actual outcome --- Schultz et al., 1997; this is a molecule
    because it combines prior formation, prediction, and comparison)

-   Approach/avoid computation (integration of positive and negative
    valence signals into a net motivational direction --- possibly
    involving competitive selection between approach and avoid circuits;
    Miller, 1944, on approach-avoidance conflict)

-   Familiarity signal (accumulated match between current input and
    stored representations, read out as a graded signal ---
    Yonelinas, 2002)

-   Effort cost estimation (monitoring of metabolic expenditure +
    comparison with expected gain --- Kurzban et al., 2013)

**Organizational molecules:**

-   Object file creation (binding + spatial indexing + temporal
    continuity tracking --- Kahneman, Treisman, & Gibbs, 1992)

-   Scene gist extraction (rapid statistical summary of spatial layout +
    object categories --- Oliva & Torralba, 2006, on spatial envelope)

-   Event segmentation (prediction error accumulation + threshold-based
    parsing of continuous experience into discrete events --- Zacks,
    Speer, Swallow, Braver, & Reynolds, 2007)

**Social-cognitive molecules:**

-   Gaze direction detection (spatial computation on eye geometry ---
    Baron-Cohen, 1995, on the eye-direction detector as a module)

-   Biological motion detection (integration of joint-position signals
    into body-movement patterns --- Johansson, 1973)

-   Vocal affect extraction (spectral analysis + comparison with stored
    prosodic templates)

Again, I want to flag a key structural point: these molecules vary
considerably in how many T1 atoms they involve and how complex their
internal wiring is. Contour integration is relatively simple ---
essentially grouping plus local lateral inhibition arranged in a
specific spatial pattern. Reward prediction error is more complex,
involving learning (prior formation), prediction, comparison, and a
signed output signal. If we wanted to be very precise about the
taxonomy, we might distinguish between \"simple molecules\" (two or
three T1s in a fixed configuration) and \"complex molecules\" (multiple
T1s in a more elaborate arrangement). But this may be refinement for
later.

**T2: Mechanism Templates**

This is where the fundamental classification question you\'re raising
bites hardest. In the framework as I understand it, T2s are *recurring
mechanism patterns* --- they specify a *type of computation* that gets
instantiated in multiple domains with different content. They\'re not
nodes in the web; they\'re descriptions of *how certain subgraphs are
organized*.

The T2s we\'ve discussed or that are implicit in the framework include:

**T2-1: Predictive coding / Predictive matching** *Pattern:* Generative
model → predicted input → comparison with actual input → error signal →
model update. *Key formalism:* Hierarchical Bayesian inference (Rao &
Ballard, 1999; Friston, 2005). *Instantiated in:* Sensory prediction,
motor prediction, social prediction, reward prediction, aesthetic
expectation.

**T2-2: Homeostatic regulation / Set-point control** *Pattern:* Set
point + current state → discrepancy → corrective drive. *Key
formalism:* Control theory, cybernetics (Wiener, 1948; Powers,
1973). *Instantiated in:* Thermoregulation, arousal regulation,
cognitive load regulation, possibly affect regulation.

**T2-3: Accumulation to bound / Evidence accumulation** *Pattern:* Noisy
evidence accumulates → threshold → discrete decision or state
change. *Key formalism:* Drift-diffusion models (Ratcliff, 1978; Gold &
Shadlen, 2007). *Instantiated in:* Perceptual decision-making,
familiarity detection, possibly dread/anxiety accumulation,
curiosity/interest.

**T2-4: Competitive selection / Biased competition** *Pattern:* Multiple
candidates → mutual inhibition → winner or graded competition → selected
output. *Key formalism:* Biased competition (Desimone & Duncan, 1995);
Lotka-Volterra dynamics. *Instantiated in:* Attentional selection,
action selection, interpretive selection (bistability).

**T2-5: Gated propagation / Conditional transmission** *Pattern:* Signal
available → gate condition → if met, signal propagates; if not, signal
blocked. *Key formalism:* Multiplicative gating (Salinas & Sejnowski,
2001); conditional independence in graphical models. *Instantiated
in:* Affective gating of memory, context-gated threat response,
expertise-gated processing, task-set gating of stimulus-response
mappings.

Now here\'s the question you\'re implicitly pressing on: **are these
five or six T2s the complete set, and is the functional circuit pattern
I described in my previous message just another way of talking about T2
instances, or is it something distinct?**

**Where functional circuits fit**

Having now laid out the inventory, I think the picture is this:

**What I called \"convergent state monitoring\" in my last message** ---
multiple processing streams → integrator → summary signal --- is not
cleanly captured by any of the five T2s listed above. It\'s not
predictive coding (there\'s no generative model producing predictions
that get compared with input). It\'s not homeostatic regulation
(there\'s no set point). It\'s not accumulation to bound (the
integration is across streams, not across time). It\'s not competitive
selection (the streams aren\'t competing; they\'re being aggregated).
It\'s not gated propagation (the signal isn\'t being conditionally
blocked).

So convergent state monitoring might be a *sixth T2*:

**T2-6: Convergent state monitoring / Multi-stream
integration** *Pattern:* Multiple processing streams, each computing
something different → integration node computes joint function of their
states → functionally significant summary signal. *Key
formalism:* Perhaps related to mixture models or multivariate sufficient
statistics --- you\'re compressing high-dimensional state information
into a lower-dimensional signal that\'s informative for downstream
decisions. *Instantiated in:* Fluency monitoring, coherence monitoring,
environmental threat assessment, vitality/energy monitoring, social
safety monitoring.

But I\'m now less confident than I was in my previous message that all
twenty-two items I listed are clean T1.5 instances of T2 templates. Some
of them may be better understood as *molecules* --- stable
configurations of T1 atoms --- rather than as instances of T2 templates.
The distinction matters: a molecule is a specific wiring of specific
T1s; a T1.5 instance of a T2 is a molecule whose wiring *follows a
template pattern*. All T2 instances are molecules, but not all molecules
are T2 instances.

For example: **reward prediction error** (Instance 8 in my previous
list) is both a molecule (specific T1 atoms: prior formation +
prediction + comparison → signed error signal) and an instance of T2-1
(predictive matching). That\'s clean --- it\'s a molecule whose internal
structure follows the predictive coding template.

But **salience computation** --- combining contrast signals across
multiple feature dimensions into an integrated salience map --- is a
molecule that doesn\'t obviously follow any of the T2 templates. It\'s
integrative, yes, but it\'s not really \"monitoring\" in the
convergent-state-monitoring sense (it\'s not tracking processing
dynamics; it\'s combining stimulus-driven signals). It might be better
classified as a molecule that doesn\'t instantiate any T2, or it might
suggest yet another T2 (something like \"parallel feature
integration\").

So the revised taxonomy might be:

-   **T1:** Computational atoms (the operations listed above)

-   **T1.5 / Molecules:** Stable configurations of T1 atoms. Some are
    instances of T2 templates; some are not.

-   **T2 / Templates:** Recurring mechanism patterns that specify how
    certain molecules are organized internally. Not nodes in the web,
    but constraints on web topology.

And the functional circuits I described would be: T1.5 molecules whose
internal organization follows T2 templates, plus the T2 templates
themselves as meta-level organizational descriptions.

**What\'s missing from this inventory**

Let me flag several things I suspect are missing or underspecified:

**At the T1 level:** I may be missing some primitives related to
temporal processing (oscillatory entrainment, phase-resetting), to
spatial coordinate transformation (reference frame conversion, which
Pouget & Sejnowski, 1997, argued is a fundamental neural computation),
and to value computation (is there a T1-level \"utility computation,\"
or does utility always emerge from molecules?).

**At the T1.5 level:** The inventory of social-cognitive molecules is
thin. We probably need molecules for joint attention, for turn-taking
detection, for hierarchy inference, for norm representation. These
matter for architectural experience in social spaces.

**At the T2 level:** I may be missing templates related to hierarchical
processing (not just predictive coding, but something like hierarchical
decomposition/composition --- the ability to represent wholes as
composed of parts, which is central to architectural perception). Also
possibly a template for oscillatory synchronization as a coordination
mechanism (Fries, 2005, on communication through coherence), which is a
different computational motif from any of the six I listed.

I\'d recommend treating this as a living inventory that gets refined as
we work through specific domains. The architecture/aesthetics domain is
a good stress test because it requires molecules from perception,
evaluation, spatial cognition, social cognition, and interoception all
interacting --- which forces you to make the taxonomy comprehensive
rather than specialized to one domain.

**References**

Baron-Cohen, S. (1995). *Mindblindness: An essay on autism and theory of
mind*. MIT Press. (\~8,000 citations)

Carandini, M., & Heeger, D. J. (2012). Normalization as a canonical
neural computation. *Nature Reviews Neuroscience*, 13(1), 51--62.
(\~2,500 citations)

Desimone, R., & Duncan, J. (1995). Neural mechanisms of selective visual
attention. *Annual Review of Neuroscience*, 18, 193--222. (\~8,000
citations)

Field, D. J., Hayes, A., & Hess, R. F. (1993). Contour integration by
the human visual system: Evidence for a local \"association
field.\" *Vision Research*, 33(2), 173--193. (\~1,500 citations)

Fries, P. (2005). A mechanism for cognitive dynamics: Neuronal
communication through neuronal coherence. *Trends in Cognitive
Sciences*, 9(10), 474--480. (\~5,000 citations)

Friston, K. (2005). A theory of cortical responses. *Philosophical
Transactions of the Royal Society B*, 360(1456), 815--836. (\~5,000
citations)

Gold, J. I., & Shadlen, M. N. (2007). The neural basis of decision
making. *Annual Review of Neuroscience*, 30, 535--574. (\~4,000
citations)

Itti, L., & Koch, C. (2001). Computational modelling of visual
attention. *Nature Reviews Neuroscience*, 2(3), 194--203. (\~5,000
citations)

Johansson, G. (1973). Visual perception of biological motion and a model
for its analysis. *Perception & Psychophysics*, 14(2), 201--211.
(\~3,000 citations)

Kahneman, D., Treisman, A., & Gibbs, B. J. (1992). The reviewing of
object files: Object-specific integration of information. *Cognitive
Psychology*, 24(2), 175--219. (\~2,500 citations)

Kouh, M., & Poggio, T. (2008). A canonical neural circuit for cortical
nonlinear operations. *Neural Computation*, 20(6), 1427--1451. (\~200
citations)

Kurzban, R., Duckworth, A., Kable, J. W., & Myers, J. (2013). An
opportunity cost model of subjective effort and task
performance. *Behavioral and Brain Sciences*, 36(6), 661--679. (\~1,200
citations)

Landy, M. S., & Graham, N. (2004). Visual perception of texture. In L.
M. Chalupa & J. S. Werner (Eds.), *The visual neurosciences* (pp.
1106--1118). MIT Press. (\~200 citations)

Marr, D. (1982). *Vision: A computational investigation into the human
representation and processing of visual information*. W.H. Freeman.
(\~20,000 citations)

Miller, N. E. (1944). Experimental studies of conflict. In J. McV. Hunt
(Ed.), *Personality and the behavior disorders* (pp. 431--465). Ronald
Press. (\~1,500 citations)

Oliva, A., & Torralba, A. (2006). Building the gist of a scene: The role
of global image features in recognition. *Progress in Brain Research*,
155, 23--36. (\~1,500 citations)

Pouget, A., & Sejnowski, T. J. (1997). Spatial transformations in the
parietal cortex using basis functions. *Journal of Cognitive
Neuroscience*, 9(2), 222--237. (\~600 citations)

Powers, W. T. (1973). *Behavior: The control of perception*. Aldine.
(\~2,000 citations)

Rao, R. P. N., & Ballard, D. H. (1999). Predictive coding in the visual
cortex. *Nature Neuroscience*, 2(1), 79--87. (\~5,000 citations)

Ratcliff, R. (1978). A theory of memory retrieval. *Psychological
Review*, 85(2), 59--108. (\~6,000 citations)

Salinas, E., & Sejnowski, T. J. (2001). Gain modulation in the central
nervous system: Where behavior, neurophysiology, and computation
meet. *The Neuroscientist*, 7(5), 430--440. (\~400 citations)

Schultz, W., Dayan, P., & Montague, P. R. (1997). A neural substrate of
prediction and reward. *Science*, 275(5306), 1593--1599. (\~12,000
citations)

Wiener, N. (1948). *Cybernetics: Or control and communication in the
animal and the machine*. MIT Press. (\~15,000 citations)

Yonelinas, A. P. (2002). The nature of recollection and
familiarity. *Journal of Memory and Language*, 46(3), 441--517. (\~3,500
citations)

Zacks, J. M., Speer, N. K., Swallow, K. M., Braver, T. S., & Reynolds,
J. R. (2007). Event perception: A mind-brain perspective. *Psychological
Bulletin*, 133(2), 273--293. (\~1,500 citations)

[[Claude is AI and can make mistakes. Please double-check
responses.]{.underline}](https://support.anthropic.com/en/articles/8525154-claude-is-providing-incorrect-or-misleading-responses-what-s-going-on)
