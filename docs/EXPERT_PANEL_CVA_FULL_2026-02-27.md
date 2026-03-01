# EXPERT PANEL: Constraint–Valuation Architecture (CVA)
## Formal Architectural Review of ATLAS Revision

**Date**: February 27, 2026
**Convening Authority**: Professor David Kirsh, UCSD Cognitive Science
**Decision Context**: Proposed fundamental revision to ATLAS system; evaluates causal separability of constraint inference, valuation, and policy layers
**Panel Size**: 12 world-class scholars
**Transcript Status**: FULL — all rounds complete

---

## PANELIST PRE-READ VERIFICATION (Round 0)

**Moderator**: Thank you all for the pre-read. Each of you will state three things: (1) your understanding of what CVA proposes, (2) what it would change in ATLAS, (3) your primary concern going in. Two to three sentences each. Michael, start.

### Michael Jordan (UC Berkeley — Bayesian Hierarchical Models)

I understand CVA to propose a causal separation between *constraint inference* (what IS true about the environment—geometry, material properties, social density), *valuation* (what those constraints MEAN given goals and identity), and *policy* (what behavior emerges). This differs from current ATLAS, which maps features directly to outcomes without explicit intermediate valuation. My concern is the hardest one: identifiability. If constraints and valuations are causally separated, can we actually estimate them from data? If we observe an aesthetic preference shift, how do we know whether the constraints changed, the valuation weights changed, or the goal frame changed? That's a non-trivial inverse problem.

### Klaus Scherer (Geneva — Appraisal Theory)

CVA proposes a *component process model* of architectural affect where appraisal checks—novelty, intrinsic pleasantness, goal relevance, coping potential, normative significance—are operationalized as constraint variables feeding into goal-relative valuations that then determine emotional/aesthetic response. This is close to my own appraisal framework, but the question for me is whether CVA adds genuine conceptual clarity or just relabels appraisal theory's "appraisal dimensions" as "constraints" and "checks" as "valuations." If it's the latter, we're not advancing; we're just rescaling. My concern is conceptual redundancy.

### Karl Friston (UCL — Active Inference)

CVA embeds constraint–valuation separation into an active inference framework where precision weighting modulates how much valuation precision shapes policy selection. This is genuinely appealing because it explains why the same constraint-value combination produces different behavior under different precision (urgency, expertise, emotional state). However, I notice CVA treats valuations as outputs of constraint evaluation, whereas active inference would suggest valuations emerge from dynamic coupling with policy—they're not separable at all. My concern is that you've borrowed active inference language but violated its core principle of circular causality.

### Lisa Feldman Barrett (Northeastern — Constructionist Emotion)

CVA proposes that beauty emerges as *linguistic compression* over a valuation vector—that is, B ≈ L(v). It then identifies nine valuation axes (Safety, Interest, Restoration, Status, Belonging, Identity, Autonomy, Competence, Relatedness). My concern is immediate: these nine axes are not discovered facts about emotion; they're CONSTRUCTED cultural categories. The very notion that beauty "compresses" a multidimensional valuation into a single felt quality suggests that valuation drives emotion, but constructionism says culture drives emotion. You're treating values as pre-linguistic perceptual primitives when they're actually post-linguistic folk categories. That's backwards.

### Steven Strogatz (Cornell — Dynamical Systems)

The mathematical appendix proposes coupled differential equations for constraint evolution and valuation evolution with Jacobian stability analysis. I've read it carefully. The system is stated as dc/dt = F(c, x, g) and dv/dt = G(v, c, x, g, τ, κ). My concern is concrete: you haven't shown what F and G actually are. The stability condition Re(λ) < 0 and the loop-gain constraint qk < ab are necessary but not sufficient. Without explicit functional forms, I cannot evaluate whether this system actually decouples the way you claim, or whether hidden feedback loops make separation illusory. Show me the dynamics or acknowledge they're underspecified.

### Naomi Eisenberger (UCLA — Social-Affective Neuroscience)

CVA proposes BelongingValue and IdentityCongruenceValue as primitives that modulate aesthetic response—that is, the same spatial property (e.g., high density of social cues) produces different valuation depending on whether the person is seeking belonging or seeking solitude. Neurally, this requires that social-affective systems (anterior insula, ventral anterior cingulate, medial prefrontal cortex) feed forward to aesthetic valuation circuits in orbitofrontal and ventromedial prefrontal cortex. The concern I have is whether this actually happens. Most evidence shows OFC/vmPFC compute value across multiple domains, but whether they *separately* encode belonging-specific valuation is unclear. We might just be seeing general value integration.

### Roger Ulrich (Chalmers — Evidence-Based Design)

CVA proposes that architectural features map to constraint variables (e.g., ceiling height → SpatialScaleVariance, fractals → PredictionErrorVariance) and that these constraints then feed into goal-relative valuations that predict aesthetic preference. This is promising because it explains why the same feature—say, a high ceiling—produces different aesthetic responses in different activity frames (yoga class vs. shopping mall). The current ATLAS system cannot do this. However, my concern is empirical: the 20-template classification feels post-hoc. Where's the evidence that LoadRate actually predicts SafetyValue, or that PredictionErrorVariance predicts InterestValue? Are these derived from first principles or curve-fitted to known exemplars?

### Ruth Dalton (Northumbria — Space Syntax)

CVA operationalizes constraint variables using measures I recognize—visibility graphs, entropy, spectral profiles, boundary clarity. But I want to push on precision. When CVA says "ProspectDensity maps to SafetyValue," does it mean the raw visibility graph metric? Or some nonlinear transform? Or does it depend on the observer's position? Space syntax has spent decades learning that spatial metrics are context-dependent and scale-dependent. CVA needs to be much more specific about *how* constraints are computed, not just *what* constraints exist. My concern is underbaked operationalization.

### Edward Deci (Rochester — Self-Determination Theory)

CVA identifies AutonomySupportValue, CompetenceSupportValue, and RelatednessSupportValue as key valuation axes—these align exactly with the three psychological needs from self-determination theory. I find this encouraging. However, I want to flag a risk: in SDT, these needs don't operate independently; they're interdependent. A high-autonomy environment that provides no competence support actually *decreases* intrinsic motivation because autonomy without competence is paralyzing. In CVA, the nine valuation axes seem to be treated as independent inputs to policy selection. That's not how motivation actually works. My concern is that CVA might lose the interactive structure of human motivation.

### Mark Leary (Duke — Sociometer Theory)

CVA proposes BelongingValue and IdentityCongruenceValue as independent valuation axes. But sociometer theory suggests that belonging (relational evaluation) actually *IS* identity—we don't experience belonging and identity as separate; we experience our social standing. The two should not be decoupled. Moreover, aesthetic response to architecture may be predominantly social. If an environment signals high status or group belonging, people rate it as beautiful even if it's geometrically chaotic; if it signals low status, people rate it as ugly even if it's geometrically elegant. My concern is that CVA treats belonging and identity as equal-weight inputs when they may actually be *master* variables that reweight all other values.

### Shinobu Kitayama (Michigan — Cultural Psychology)

CVA proposes nine universal valuation axes, but cultural psychology shows that the *salience* and *meaning* of these axes varies radically across cultures. In individualist cultures, AutonomyValue and IdentityCongruenceValue are primary; in collectivist cultures, BelongingValue and RelatednessSupportValue dominate. Moreover, the *same constraint* is valued oppositely: in Japan, social density is comfort; in Scandinavia, it's crowding. If CVA treats these axes as universal with context-dependent *weights*, it assumes universal underlying structures. That's a WEIRD assumption. My concern is that CVA might not actually generalize beyond North American/European samples.

### Peter Zumthor (Practicing Architect)

I've read the proposal with care. What I understand is that CVA is trying to make explicit what architects do implicitly—we design not for "features" but for *affects*. The four worked examples (nature view, prospect-refuge, ceiling height, curvature) resonate with real design thinking. However—and this matters—architects don't separate constraints, valuations, and policy. We design *atmospheres*. A room isn't a set of constraints that the user values and then acts upon; a room *is* a valuation. The affect is not derived from the space; the affect *is* the space. My concern is philosophical: CVA treats affect as a computational output when in phenomenological terms, affect is primary and our description of constraints is *derivative* from affect. You may have causality backwards.

---

## ROUND 1: "Is Constraint–Valuation Separation Legitimate?"

**Moderator**: This is the foundational question. The entire CVA proposal depends on the claim that you can meaningfully separate (1) what IS true (constraints) from (2) what those facts MEAN (valuations). Do you believe this separation is genuine, or is it a false dichotomy? Each panelist will speak four to six sentences without interruption.

### Michael Jordan

From a statistical perspective, causal separability is testable through conditional independence. If constraints and valuations are truly separate, then conditioning on constraints should make valuations conditionally independent of certain outcome functions, and vice versa. The question is whether the data actually supports this structure. I am *skeptical*. In my experience with hierarchical models, what appear to be separate layers often turn out to be different parameterizations of the same underlying distribution. Consider a simple example: I observe a person finds a high ceiling aesthetically pleasing. Can I determine whether the constraint (SpatialScaleVariance is high) drove the valuation, or whether the person *valued* high ceilings and therefore perceived the variance as high? These are observationally equivalent. Without experimental manipulation—changing constraints while holding goals constant, or changing goals while holding constraints constant—I cannot distinguish them. CVA assumes you can do that. I doubt it.

### Klaus Scherer

From appraisal theory, the separation is defensible *in principle*. My component process model explicitly separates evaluative checks (is this relevant to my goals? do I have coping potential?) from the emotional response those checks trigger. That's a form of constraint–valuation separation. However—and this is crucial—the separation works *dynamically*. You don't evaluate constraints first, then valuations second, then policies third. All three unfold in parallel. Moreover, the "constraints" in my appraisal model are not objective facts; they're *appraisals*—goal-relevant interpretations of facts. The moment you add interpretation, you've already injected valuation. So I'm agnostic on whether CVA's three-layer model is correct, but I'm confident that if it is, the layers must be *recursive*, not *sequential*. You can't evaluate "how much prospect" without already knowing you value prospect.

### Karl Friston

I want to endorse the spirit of what CVA is trying to do, but I think the execution violates active inference. In active inference, there is no separation between perception and action, between constraints and values. The brain generates predictions about states (what I'll perceive) and about policies (what I'll do). The precision of those predictions *is* the value. A high-precision prediction that a route is dangerous *is* high threat-value. They're not separate computations; they're aspects of the same generative model. Now, CVA could be salvaged if you reframe it: constraints are *predicted* facts, valuations are *precision-weighted* predictions, and policy is selection from high-precision policies. In that case, the three layers are abstractions of a unified inference process, not truly separate. But if you insist they're causally separated—if you think the brain first computes what IS, then separately computes what it MEANS, then separately computes what to DO—you're fighting the neurobiology.

### Lisa Feldman Barrett

I want to be direct: no. Constraint–valuation separation is not legitimate. Here's why: the moment you *perceive* a constraint, you've already *valued* it. Perception is not pre-valuation; it's valuation-laden. When you see high social density, you're not first computing an objective social cue count and then separately computing whether that's good or bad. You're immediately perceiving it as *threatening* or *welcoming* depending on your current autonomic state, your prior experiences, your cultural context, your group membership. That's not a two-stage process; it's one process. The notion that there's a layer of objective constraint *before* valuation assumes a view of perception that cognitive neuroscience has thoroughly rejected. Perception is constructed; it's affective from the ground up. So if CVA is claiming three causal layers, I think it's wrong. If it's claiming three *conceptual* layers for analytical purposes, then fine, but that's very different from what the white paper seems to suggest.

### Steven Strogatz

Let me approach this as a dynamicist. Causal separability means: if I intervene on the constraint layer, the valuation and policy layers respond as models predict. If I intervene on the valuation layer, the constraint and policy layers respond predictably. Without explicit dynamics—without knowing F and G—I cannot determine whether this is true. However, I can say this: if the three layers are *weakly coupled* (that is, constraints influence valuations more strongly than valuations influence constraints), then separation is approximately legitimate for short timescales. But if they're *strongly coupled* or *circularly* coupled, then separation is illusion. Most biological systems are circularly coupled. So I'm skeptical unless the mathematics proves otherwise.

### Naomi Eisenberger

Neurally, the question is: do different brain systems compute constraints and valuations separately? The lateral prefrontal cortex, parietal cortex, and visual cortex extract feature information that could correspond to "constraints." The orbitofrontal and ventromedial prefrontal cortex integrate value signals. These are separable by anatomy. However, they don't operate as a sequence (constraints → valuations → policy). They operate in parallel with massive reciprocal connections. Moreover, value signals feed back into perception; if I value social interaction, I perceive social cues more readily. So the separability is anatomical but not functional or temporal. For CVA's purposes, that means: you can *measure* these layers separately in the brain, but you cannot assume they *operate* separately or sequentially.

### Roger Ulrich

I approach this from evidence-based design. In real environments, I've observed people responding to the *same* constraint differently based on their state and goals. A complex pattern is interesting under some conditions, overwhelming under others. That suggests constraints and valuations are indeed somewhat separable—you can change the goal (valuation) and get different responses without changing the constraint. However, the separability is incomplete. Sometimes people with the same goal respond differently to the same constraint because they *perceive* the constraint differently. Two people in the same room may estimate different levels of enclosure based on their prior experiences and their current attention. So yes, partial separability seems real. But the claim that you can compute constraints *objectively* and then apply valuations *on top* seems optimistic.

### Ruth Dalton

From space syntax, we've learned that "objective" spatial measures are never truly objective—they depend on where you stand, what you're looking for, what you attended to last. A visibility graph is not an objective constraint; it's a model-dependent description. So when CVA says "visibility maps to SafetyValue," the visibility is already a *constructed* measure, not a constraint in nature. That said, space syntax shows that certain measures are *robust*—they predict behavior across many contexts. So there's a kind of intermediate objectivity. I'd say: constraints are inter-subjective constructs, not objective facts, but they can still be separated from valuations for analytical purposes. The separation is real, but the constraints are not pre-valuation; they're community-validated descriptions.

### Edward Deci

In self-determination theory, we've always maintained that people *perceive* autonomy-supportiveness or structure, and those perceptions determine motivation. The perceptions are somewhat separable from the actual environmental structure (you can have structure without autonomy support, or autonomy support without structure), but the perception is not a post-hoc evaluation. It's an immediate read of the environment. So I'd say: yes, separability exists in the sense that the constraint properties are partially independent from the value properties. But no, the separation is not sequential or pre-valuation. It's more like: different dimensions of meaning that you extract simultaneously.

### Mark Leary

I'm suspicious of the separation because aesthetic judgments are primarily *social assessments*. When you rate architecture as beautiful, you're often unconsciously assessing what it signals about the person who designed it and what it signals about you for being in it. That's not a constraint-then-valuation sequence; that's an immediate social read. However, I grant that you can *analyze* architecture in terms of separable features (the constraints) and then ask how those features map to social meaning (the valuation). For analytical purposes, it's useful. But I wouldn't claim this reflects how aesthetic judgment actually unfolds in real time.

### Shinobu Kitayama

The separation is culturally contingent. In some cultures, the boundary between objective fact and social meaning is clear (this is a common assumption in Western philosophy), so separating constraints from valuations makes sense conceptually. In other cultures, where epistemology is more holistic and less object-subject dualistic, this separation doesn't map onto how people think. So I would say: the separation is a useful analytical tool for some purposes, but it's not a universal cognitive reality. It's a Western theoretical construct.

### Peter Zumthor

As a phenomenologist, I would say the separation is an abstraction—useful for analysis but not primordial. The *experience* of a room is unified; you don't experience constraints and then valuations. However, when you try to *communicate* about architecture, or when you try to *design* for affect, you need to separate these levels. So yes, the separation is legitimate as a design tool. But it's not ontologically primary; it's a representational convenience.

**Moderator**: Let's vote on legitimacy. "Legitimate" means the separation reflects real causal structure; "Illegitimate" means it's a false dichotomy; "Needs qualification" means it's useful but with important caveats.

**Vote Tally**:
- Legitimate: 0
- Illegitimate: 3 (Barrett, Zumthor, Strogatz—until dynamics are shown)
- Needs qualification: 9 (Scherer, Friston, Jordan, Eisenberger, Ulrich, Dalton, Deci, Leary, Kitayama)

**Moderator**: Notably, no one votes it as fully legitimate. The consensus is: the separation is *useful and analytically defensible*, but it's not a reflection of how affect actually *unfolds in real time*, and it cannot be assumed to be *sequentially causal* or *pre-valuation*. We proceed with this qualification in mind.

---

## ROUND 2: Cluster Working Groups

**Moderator**: Each cluster will now identify: (1) one fatal flaw in CVA, (2) one necessary addition if CVA is adopted, (3) one thing CVA gets right that current ATLAS doesn't. You have 15 minutes per cluster. Let's begin.

### Computational & Formal Core (Jordan, Friston, Strogatz)

**Strogatz** (speaking for the cluster): We've identified one fatal flaw: *identifiability*. Michael raised this forcefully, and I concur. If constraints, valuations, and policies are causally linked but also influenced by unobserved factors (like goals, emotional state, cultural context), then the inverse problem—observing aesthetic preferences and inferring the underlying constraints and valuations—is radically underdetermined. You need either massive experimental perturbation (systematically varying constraints while holding goals constant) or strong parametric assumptions. CVA doesn't propose either. Without that, the model is elegant but unfalsifiable.

The necessary addition: *explicit dynamics with stability guarantees*. You cannot claim causal separability without showing that the differential equations actually decouple in the way you claim. You need to specify F and G in full functional form and prove that the loop gains remain below unity. Right now it's hand-waving.

What CVA gets right: It breaks aesthetic response into multiple tractable sub-problems. Instead of trying to predict preference directly from features (current ATLAS), you separate the problem into constraint inference, valuation computation, and policy selection. That's genuinely useful because it allows different components to be validated independently. Constraint inference can be tested against direct spatial measurements; valuations can be tested through goal manipulation; policies can be tested through behavioral prediction. The *conceptual decomposition* is powerful even if the causal separation is approximate.

### Affective Science & Emotion Theory (Scherer, Barrett, Eisenberger)

**Barrett** (speaking for the cluster): The fatal flaw is *reductionism via compression*. CVA claims that beauty emerges as L(v)—linguistic compression of the valuation vector. This treats the diversity and richness of aesthetic experience as a *byproduct* of post-hoc compression, when actually, aesthetic categories are *primary cultural constructs* that shape perception from the start. You don't measure nine valuation dimensions and then compress them into "beauty"; you already *know* what beauty is in your culture, and you selectively measure dimensions that fit that category. The model has causality backwards.

The necessary addition: *Cultural modeling layer*. If you want to predict aesthetic judgment, you need to model how cultural narratives, group identity, historical context, and moral values shape which dimensions even get *attended to*, let alone valued. CVA treats culture as a weight on the valuation axes (κ parameter), but culture isn't a weight; it's the frame that determines which axes exist in the first place.

What CVA gets right: It acknowledges that affect is multidimensional and compositional. Appraisal theory has always said this, but CVA makes it more explicit and more testable. You've given us operationalizable dimensions (ProcessingCost, AffordanceDensity, SocialCueDensity) instead of abstract appraisal checks. That's a genuine advance over ATLAS's treatment of affect as an implicit outcome variable.

### Identity, Motivation, and Value Systems (Deci, Leary, Kitayama)

**Leary** (speaking for the cluster): The fatal flaw is *missing the social hierarchy*. BelongingValue and IdentityCongruenceValue are not independent dimensions; they interact nonlinearly. Belonging is *conditional on status*. People seek belonging with their reference group—those of similar status. Moreover, aesthetic judgment is often a *status signal*. You rate architecture as beautiful to signal your sophistication or alignment with a valued group. This is implicit in the valuation system but not made explicit. You can't model aesthetic judgment without modeling the *social positioning* that gives it meaning.

The necessary addition: *Explicit social-hierarchy modeling*. You need to represent how architectural aesthetics signal group belonging and status relative to reference groups. This is not a simple weight on valuation axes; it's a *restructuring* of the valuation computation to account for social context and comparison.

What CVA gets right: You've put AutonomySupportValue, CompetenceSupportValue, and RelatednessSupportValue at the center. That aligns with decades of empirical work in motivation, social psychology, and neuroscience. The insight that aesthetic environments support or undermine psychological needs is sound and undertheorized in architecture.

### Architecture & Spatial Cognition (Ulrich, Dalton, Zumthor)

**Zumthor** (speaking for the cluster): The fatal flaw is *excessive formalization*. Architecture is about *creating atmospheres*, not computing constraint-valuation vectors. The four worked examples (nature view, prospect-refuge, ceiling height, curvature) are insightful, but once you try to systematize them into a mathematical model, you lose the phenomenological richness that makes architecture *alive*. You reduce atmosphere to algorithm. Moreover, the 20-template classification feels exhaustive on paper but sterile in practice. Real architectural innovation comes from *breaking* these categories, from finding novel constraint-value configurations that surprise and move people. A formalized model is inherently conservative; it will never predict the next innovative design.

The necessary addition: *Phenomenological grounding*. If you're going to use this model, you need to constantly ground it in *direct first-person experience* of spaces and *deep engagement* with architects' design thinking. Without that, it becomes a toy model that theorists play with but architects ignore.

What CVA gets right: You've made explicit the role of *affordance structure* and *activity frame dependence*. Your insight that the same ceiling height is experienced differently in a yoga class vs. a shopping mall is exactly right and is something current ATLAS misses. You've also done real work operationalizing spatial measures—visibility graphs, entropy, spectral profiles—in ways that space syntax and computational morphology have already validated. The operationalization is credible.

---

## ROUND 3: Cross-Cluster Response

**Moderator**: Each cluster will now respond to the fatal flaws identified by the *other* clusters. You may rebut, concede, or propose modifications. Let's hear from the Computational core first.

### Computational & Formal Core Response to Others

**Friston**: On the Affective cluster's claim that CVA is reductionist about beauty—I actually think CVA is trying to *avoid* that reductionism. By treating beauty as compression over nine dimensional valuations, the model is saying beauty is *multidimensional*. You don't get a single beauty number; you get a point in nine-dimensional space that you then describe linguistically. That's the opposite of reduction; it's expansion with linguistic post-hoc naming. I think Barrett has misread the model.

However, I concur with the Affective cluster on one point: CVA doesn't model the *cultural construction* of those nine axes. Why those nine and not others? Why do some cultures weight them differently? CVA treats κ (cultural parameter) as a scaling factor, but that's insufficient. We'd need a richer model of how culture shapes the space of possible valuations.

On the Identity cluster's point about social hierarchy—I find it compelling. Aesthetic preference is often a status signal. The current CVA doesn't explicitly model this. However, I wonder if you could fold it into IdentityCongruenceValue and StatusValue. If an environment's aesthetic properties align with your group's values and signal your group membership, then your valuation rises. But that would require knowing the *reference groups* and *status structures* in advance, which is culturally contingent.

**Strogatz**: On the Architecture cluster's point about excessive formalization—I think they're right that mathematics can sterilize and that models can be conservative. However, models are *necessary* for cumulative science. You cannot learn systematically without formalization. The answer is not to reject the formalization but to ensure it's *open enough* to accommodate surprising configurations. CVA's 20 templates feel closed; they look like an exhaustive taxonomy. That's the problem, not the formalization itself.

### Affective Science Response to Others

**Scherer**: On the Computational cluster's identifiability problem—they're absolutely right. We need *experimental manipulation*. But that's not insurmountable. You can imagine studies where you hold the goal frame constant (e.g., "I'm looking for a restorative space") and vary constraints (different types of greenery, different transparency levels) and measure how valuations shift. Or hold constraints constant and manipulate goal frames. These are difficult experiments but doable.

On the Architecture cluster's phenomenological critique—I agree entirely. But I want to push back slightly on the idea that formalization destroys phenomenology. In my own work on appraisal theory, formalizing the component process model didn't eliminate the rich texture of emotional experience; it clarified which dimensions matter. CVA could do the same for architecture if executed carefully.

**Barrett**: I want to concur with Strogatz that we need formalization, but I want to push on the specifics. The 20 templates in CVA's taxonomy are *Western categories*. Clutter, fractals, noise, wayfinding—these are how Western cognitive science carves up environmental properties. Other cultures might have radically different template categories. So when you formalize CVA, you need to build in *representational relativity*. The model should allow for culturally divergent constraint categories, not assume the 20 are universal.

### Identity Cluster Response to Others

**Deci**: On the Computational cluster's identifiability problem, I think their concern is valid, but I want to note that SDT has managed to test causal claims through goal-priming experiments and longitudinal designs. If you prime autonomy support (vs. control), performance and intrinsic motivation shift in predictable ways. You can separate the effects of autonomy support from competence support through experimental design. CVA could adopt similar methods.

On the Architecture cluster's concern about formalization—I actually think the 20 templates are not arbitrary. They correspond to real environmental affordances that humans are evolved to detect. Wayfinding legibility is a real property that some spaces have more than others. It's not just a Western construction. However, the *valuation* of wayfinding legibility is definitely cultural.

**Kitayama**: I want to push harder on the cultural issue. The Computational cluster talks about κ as a cultural parameter, but that's vastly oversimplified. In collectivist cultures, BelongingValue and RelatednessSupportValue may not be independent from IdentityCongruenceValue—they may form a single cluster. Meanwhile, AutonomySupportValue might split into two: autonomy *from the group* (negative value) and autonomy *for the group* (positive value). So the very structure of the valuation space is culturally contingent. That's not a parameter; that's a structural transformation.

### Architecture Cluster Response to Others

**Ulrich**: On the Affective cluster's phenomenological critique—I concur, but I want to add that the *empirical* phenomenology matters. We have now decades of evidence that certain architectural properties (access to nature, prospect-refuge balance, legible wayfinding) reliably produce specific emotional and behavioral outcomes across diverse populations. That's not theoretical hand-waving; that's reproducible evidence. CVA is trying to explain *why* these regularities exist. I think that's a valid scientific goal.

On the Computational cluster's identifiability problem—I think the solution is to use *longitudinal field studies* and *before-after designs*. When you renovate a space (changing constraints while holding population roughly constant), you can measure how valuations and behavioral outcomes shift. That gives you traction on causal structure without needing perfect experimental control.

---

## ROUND 4: Deep Questions

**Moderator**: We now address seven deep questions where specific panelists lead the discussion. Others may jump in, but we defer to the lead's expertise. Let's begin.

### Q4a: Is B ≈ L(v) Defensible or Reductive?

**Lead**: Lisa Feldman Barrett (with Scherer and Zumthor responding)

**Barrett**: I want to be clear about what troubles me. The proposal B ≈ L(v)—that beauty is linguistic compression of the valuation vector—treats language as a *post-hoc* packaging of a pre-existing multidimensional signal. But language doesn't just compress; language *constructs*. When you learn the English word "beautiful," you're not learning to name a pre-existing dimension; you're learning to attend to certain dimensions and ignore others. Language shapes perception, not just describes it. So the model has causality backwards. You don't perceive nine dimensions, compress them into "beauty," and then learn the word. You learn the word "beauty," and that teaches you which dimensions matter.

**Scherer**: I want to defend B ≈ L(v) partially. In my appraisal theory, I do claim that emotional experience emerges from parallel evaluation of multiple appraisal dimensions, and then *language* provides a category—fear, sadness, joy—that roughly summarizes the state. So the compression happens, even if language shapes what dimensions are available for compression. However, I think the model needs modification. It's not that you compress nine independent dimensions into one word. It's that certain *clusters* of dimensions trigger coherent emotional states, and language labels those clusters. A high-arousal negative state is called "fear" or "anger" depending on the appraisal profile. Similarly, a particular *pattern* in the valuation vector—perhaps high InterestValue + moderate SafetyValue + moderate IdentityCongruenceValue—might trigger the aesthetic category "beautiful." The compression isn't linear; it's *categorical*.

**Zumthor**: As a designer, I find L(v) interesting but incomplete. Yes, there's a phenomenology of beauty that you can name and communicate. But the *experience* of beauty is not the word; it's the full lived encounter with the space. When I create an atmosphere, I'm trying to orchestrate a *unity* of affect—not nine independent dimensions that the user then linguistically compresses, but a *singular, pervasive feeling* that saturates the space. The mathematical model might predict the linguistic category ("beautiful"), but it might miss the phenomenological reality altogether.

**Barrett**: Peter, I think you're pointing to something crucial, which is that beauty might not be a *summary* of nine dimensions but a *holistic gestalt* that cannot be decomposed into dimensions at all. In that case, B ≈ L(v) is not just reductive; it's categorically wrong. Beauty might be irreducible to valuation dimensions.

**Friston** (chiming in): This connects to active inference. In predictive processing, when I encounter a beautiful space, I'm not *computing* nine valuations and then compressing. I'm *recognizing* the space as an instance of a beauty-class through rapid pattern matching. The nine dimensions are a post-hoc description of why the space triggered that recognition, not the mechanism driving it. So L(v) might work as an *explanation-after-the-fact*, but it doesn't describe *real-time processing*.

**Moderator's note**: The question of whether B ≈ L(v) is defensible remains genuinely open. Scherer suggests categorical compression instead of linear compression. Zumthor suggests beauty might be irreducibly holistic. Friston suggests the dimensions are post-hoc explanations, not real-time causes. No consensus, but important refinements.

### Q4b: ActivityFrame as Master Moderator or Just Another Variable?

**Lead**: Karl Friston (with Deci and Ulrich responding)

**Friston**: Here's the key question: in CVA, does ActivityFrame (the goal/context that modulates how valuations weight onto policy) have a *special role* as a precision modulator, or is it just another variable that influences the valuation computation? The white paper treats it somewhat ambiguously. If ActivityFrame is a master moderator—if it sets the *precision* with which valuation dimensions influence behavior—then it has a special role that active inference naturally explains. But if it's just another input to valuation weights, then it's unclear why this variable is singled out.

**Deci**: From SDT, I'd say ActivityFrame is *both*. The perceived activity (yoga class vs. shopping mall) shapes *which needs* are active (in yoga, autonomy and restoration are salient; in shopping, status and belonging are salient). But it's not just changing weights; it's *activating different goals*. So ActivityFrame isn't just a modulator; it's a *goal-setter*. In an active inference framing, the person's implicit goal is to optimize expected value under the current activity frame. The frame sets which dimensions are *relevant*, not just their weights.

**Ulrich**: Empirically, I've observed that the *same feature* produces opposite responses depending on activity. In a hospital patient room, high enclosure is calming (restorative). In a nightclub, high enclosure is exciting (arousal). This isn't just weight changes; the constraint-value mapping itself flips. So I'd say ActivityFrame fundamentally *restructures* the constraint-valuation mapping. It's not a parameter; it's a *selector* that determines which mapping is active.

**Friston**: I think that's right. In active inference terms, ActivityFrame is encoding the *expected policy* you're about to pursue. If I expect to restore (yoga frame), then my predictions focus on how spatial properties support restoration. If I expect to explore (shopping frame), then my predictions focus on how properties support exploration. So ActivityFrame is really *policy-expectation*, and the valuation vector is automatically calibrated to that policy. In that case, ActivityFrame is not a variable at all; it's the *active policy*, and valuations emerge from it, not the reverse.

**Moderator**: The consensus is that ActivityFrame is more central than CVA initially suggests. It's not just a weight on valuation axes; it's a *structuring principle* that determines which constraints are perceptually salient and which valuations are active. This requires more explicit modeling.

### Q4c: Are BelongingValue and IdentityCongruenceValue New or Just Relabeled Outcomes?

**Lead**: Naomi Eisenberger (with Leary and Kitayama responding)

**Eisenberger**: The question is: do BelongingValue and IdentityCongruenceValue represent genuinely new explanatory constructs, or are they just renaming of outcomes that current ATLAS already captures (e.g., "social preference," "group cohesion," "cultural fit")? If they're truly new, they should have independent neural correlates and should predict behavior in novel ways. Let me be honest: I'm not sure they clear that bar. The neural evidence shows that orbitofrontal and ventromedial prefrontal cortex compute *general* value across many domains. Whether they *separately* encode belonging-specific value is unclear.

**Leary**: I want to push harder. BelongingValue is often *implicit* in other values. Status is about belonging to a valued group. Autonomy support is about being *respected* by the group. So you're not discovering new dimensions; you're making explicit what was already woven through the other dimensions. The real question is: does this explicitness help prediction? If adding BelongingValue and IdentityCongruenceValue to CVA improves predictive power beyond simpler models, then they're useful. If not, they're conceptual bloat.

**Kitayama**: I want to frame this differently. In individualist Western cultures, belonging is one dimension among others. But in collectivist cultures, belonging *integrates* with identity, status, and autonomy. So the very distinction between BelongingValue and IdentityCongruenceValue is culturally constructed. It's not a universal discovery; it's a Western theoretical imposition. That doesn't mean it's wrong, but it means you need to acknowledge the cultural specificity and show that the framework generalizes beyond WEIRD populations.

**Eisenberger**: The empirical question is testable. You'd need to show that (1) architectural features that increase social cues produce consistent neural responses in social-affective regions; (2) this neural response predicts aesthetic preference independent of other factors; (3) this relationship holds across cultures and activity frames. We don't currently have that evidence. CVA is proposing a new dimension without sufficient empirical grounding.

**Moderator**: The consensus is cautious skepticism. BelongingValue and IdentityCongruenceValue *may* be new, but the evidence is insufficient to confirm. They require targeted empirical validation before they should be treated as primitives.

### Q4d: Does the Devil's Advocate (Fluency-as-Valence) Defeat CVA?

**Lead**: Michael Jordan (with Barrett and Strogatz responding)

**Jordan**: The counter-hypothesis states that processing fluency (how easily the brain processes a stimulus) *directly carries* valence through neural reward coupling. That is, fluent processing feels good; disfluent processing feels bad. This is documented in studies by Reber, Schwarz, and others. If this is true, then you don't need a separate valuation layer. Constraints (like ProcessingCost) map directly to affect (safety, interest) without an intermediate goal-relative valuation step. The devil's advocate asks: how does CVA distinguish itself from fluency theory if valuation just encodes how easily constraints were processed under the current goal?

**Barrett**: Actually, I think the devil's advocate makes a good point. Fluency theory is more parsimonious than CVA. We know processing fluency strongly predicts aesthetic preference. We know the brain has direct reward responses to fluency. Why add a valuation layer? However, I'd note that fluency theory *itself* has cultural components. What feels fluent in one culture may feel disfluent in another. A grid layout feels fluent to Western architects; a fractal layout feels fluent to artists; a natural organic layout feels fluent to biophilic designers. So fluency is not a pre-cultural neural fact; it's already mediated by cultural learning. Once you acknowledge that, you're back to needing something like CVA's valuation layer to model *goal-relative* fluency.

**Strogatz**: From a dynamical perspective, fluency and valuation could be *different levels* of the same process. At the neural level, fluency directly couples to dopamine and reward systems. At the computational level, we describe that coupling as valuation. They're not in competition; they're different levels of description. However, CVA needs to commit to this. If valuation *is* fluency-driven, then the model should explicitly state that constraint evaluation is *fluency computation* under the current goal frame, and valuation *is the resulting fluency signal*. In that case, there's not a causal layer-separation; there's a single process described at different levels.

**Friston**: I want to add that in active inference, exactly this happens. The precision of a policy prediction reflects how *smoothly* (fluently) you can execute that policy under the current belief state. High-precision policies are ones you've learned to execute fluently. So fluency-as-precision is built into the framework. But fluency is not *pre-valuation*; fluency *is* part of what makes something valuable. The two are not competing.

**Moderator**: The consensus is that the devil's advocate raises a real challenge but not a fatal one. CVA can accommodate fluency theory if it's explicit that valuations *include* fluency signals weighted by the current goal. The architecture remains distinct from simple fluency theory because it explains *why* different goals weight fluency differently.

### Q4e: What Happens to the 208 Templates? Mass Reclassification Feasible?

**Lead**: Roger Ulrich (with Dalton and Jordan responding)

**Ulrich**: Current ATLAS has 208 evidence templates mapping features to outcomes. If we adopt CVA, we need to reclassify these into the constraint-valuation-policy framework. Is that feasible, or is it a massive engineering burden that will cripple the project? Let me be frank: I don't know. We'd need to go through each template, identify which constraint variables it maps to, which valuation axes it influences, and which policies it shapes. Some templates will fit cleanly (e.g., biophilia templates map to PredictionErrorVariance and MultisensoryCoherence, which drive InterestValue and RestorationValue). Others will be ambiguous. And some might not fit at all.

**Dalton**: From what I understand of the 208 templates, many are operationally concrete. They describe *how to measure* a feature (e.g., visibility graph density) and *what outcome* it predicts (e.g., wayfinding success). Reclassifying these into CVA would require adding an intermediate layer of constraint interpretation. For some templates, that's straightforward. For others, it might require deep conceptual work. I'd estimate 80-90% of templates are reclassifiable without major revision. The remaining 10-20% might require new research to clarify what constraint they map to or what valuation axis they influence.

**Jordan**: The engineering question is: can you do this reclassification incrementally, or does it require a full system redesign? If it's incremental, you can do it template-by-template as you validate CVA. If it requires a full redesign, it's high-risk and high-cost. I'd recommend starting with a pilot: take 20 templates from different families (e.g., clutter, biophilia, prospect-refuge, lighting, social density) and reclassify them into CVA. That gives you a proof-of-concept and reveals where the reclassification breaks down. Then you can decide whether full adoption is worth the engineering cost.

**Moderator**: The practical consensus is that reclassification is feasible but non-trivial. A pilot reclassification should precede full adoption. Estimated effort is substantial but not insurmountable if done systematically.

### Q4f: Does CVA Improve Predictive Power or Just Add Complexity?

**Lead**: Michael Jordan (with Ulrich and Zumthor responding)

**Jordan**: This is the acid test. Does CVA predict aesthetic judgments, behavioral outcomes, or affect states better than current ATLAS? If yes, the added complexity is justified. If not, we should stick with the simpler model. I'm serious: I want to see *cross-validated* R² numbers comparing CVA predictions to ATLAS predictions on held-out data. Without that empirical benchmark, we're just trading one theoretical framework for another.

**Ulrich**: Empirically, I'd expect CVA to do better on *transfer* problems. That is, if you train on aesthetic preferences in one context (e.g., office environments), can you predict preferences in a different context (e.g., hospital environments)? Current ATLAS would likely overfit to the training context. CVA, by explicitly modeling goal-dependent valuation, should generalize better across contexts. That's testable with longitudinal data and cross-context validation.

**Zumthor**: I want to push on what "better" means. If you're only measuring predictive accuracy on explicit aesthetic judgments (does the user rate the space as beautiful?), then you're missing the real effect of architecture, which is on *embodied experience*, *mood*, *sense of possibility*, *comfort*. Can CVA predict those? Or is it just better at predicting numerical beauty ratings? If the latter, I'm unimpressed.

**Friston**: Peter raises the key point. Prediction of explicit judgments is not the same as explaining the *real* effects of architecture. In active inference terms, architecture is valuable if it *shapes your generative model* of the world—if it changes what you expect and how you act. CVA could predict explicit judgments but miss this deeper effect. So the validation question needs to be broader: does CVA better predict behavioral, affective, and cognitive outcomes across diverse measures?

**Jordan**: Agreed. So the empirical benchmark is: (1) held-out predictive accuracy for explicit aesthetic judgments; (2) cross-context transfer accuracy; (3) prediction of behavioral outcomes (time spent, movement patterns, return visits); (4) prediction of affective outcomes (stress reduction, mood improvement, engagement). If CVA beats current ATLAS on most of these, it's worth adopting. If it ties or loses, it's not.

**Moderator**: The consensus is clear: empirical validation is *essential* before adoption. Predictive power must be demonstrated against multiple outcome measures and across different contexts.

### Q4g: What's the MINIMAL Change That Captures CVA's Core Insight?

**Lead**: All panelists (this is the pragmatic question)

**Moderator**: This is the key question for David's decision. What if you don't adopt CVA in full? What's the minimal modification to ATLAS that captures the core insight? Each panelist gets one sentence on what they think the core insight is and how to capture it minimally.

**Friston**: Core insight: *policy precision is goal-modulated*. Minimal change: add explicit goal-framing to the projection function so that logit(p_target) = d(goal) · ω · δ · logit(p_lab), where d(goal) is a goal-dependent discount factor.

**Scherer**: Core insight: *architectural affect is multidimensional and compositional, not a single outcome*. Minimal change: replace the single "aesthetic preference" outcome variable with a 9-dimensional valuation vector and validate that these dimensions have independent neural and behavioral correlates.

**Barrett**: Core insight: *cultural and identity-related meanings shape aesthetic response*. Minimal change: add explicit identity and cultural context variables to the outcome prediction function, allowing different populations to show different preference patterns for the same features.

**Strogatz**: Core insight: *constraints and valuations are dynamically coupled, not sequential*. Minimal change: add feedback terms to the projection model so that observed preferences feed back into constraint interpretation, creating a coupled system.

**Jordan**: Core insight: *constraints and valuations are (approximately) separable enough to be empirically distinguished*. Minimal change: run experiments that hold constraints constant and vary goals (or vice versa) to test whether constraint-valuation dissociation is real, not assumed.

**Eisenberger**: Core insight: *belonging and identity modulate aesthetic response*. Minimal change: add social-context and group-identity variables to the ATLAS outcome function and validate their independent contribution to preference.

**Ulrich**: Core insight: *activity framing restructures constraint-valuation mappings, not just weights them*. Minimal change: extend the 20-template taxonomy to explicitly encode how each template's effect differs by activity (e.g., biophilia in hospitals vs. restaurants), not as a unified template.

**Ruth Dalton**: Core insight: *spatial metrics need to be operationalized with fidelity to context-dependence*. Minimal change: move from generic spatial measures (e.g., visibility density) to context-sensitive operationalizations (e.g., visibility relevant to the activity frame) in the constraint layer.

**Deci**: Core insight: *psychological needs (autonomy, competence, relatedness) are fundamental drivers of aesthetic response*. Minimal change: replace generic outcome categories with need-satisfaction outcomes (AutonomySupport, CompetenceSupport, RelatednessSupport) and show these predict behavior independently of traditional aesthetic measures.

**Leary**: Core insight: *aesthetic response is partially a status-signaling mechanism that depends on social reference*. Minimal change: add social-hierarchy and reference-group variables to the outcome function so that beauty ratings are modeled as functions of group positioning, not just of absolute feature properties.

**Kitayama**: Core insight: *the valuation space itself is culturally constructed, not universal*. Minimal change: allow the nine valuation axes and their relationships to be empirically variable by culture, not assumed constant. Run separate CVA models for different cultural populations.

**Zumthor**: Core insight: *atmosphere is primary; constraints and valuations are post-hoc descriptions*. Minimal change: instead of a computational model, adopt a *phenomenological annotation* system where spaces are systematically described in terms of their affective atmosphere, constraint properties, and valuation meanings, creating a rich qualitative database that grounds quantitative models.

**Moderator**: The consensus is striking: every panelist affirms a core insight and proposes a minimal change that captures it *without* adopting CVA in full. This suggests a pragmatic path: *incremental adoption*. Add to ATLAS the constraint-layer operationalization, the nine-dimensional valuation vector, and the goal-modulation mechanism, but don't commit to claiming these are causally separable layers. Treat them as analytical dimensions that can be validated independently.

---

## ROUND 5: Tiering Vote

**Moderator**: Each panelist will now vote on one of four options and provide 2-3 sentence rationale.

1. **ADOPT FULLY** — Restructure ATLAS around CVA, reclassify all 208 templates, commit to constraint-valuation separability.
2. **ADOPT PARTIALLY** — Add CVA components (constraint layer, valuation vector, goal modulation) without claiming causal separability. Treat as analytical dimensions.
3. **REJECT** — Current ATLAS architecture sufficient; CVA adds complexity without clear empirical benefit.
4. **DEFER** — CVA promising but requires empirical validation (identifiability studies, cross-context prediction, cultural validation) before adoption.

### Individual Votes

**Michael Jordan**: DEFER. The mathematical foundation is incomplete (explicit dynamics needed), and the identifiability problem is genuine and unresolved. Run the empirical studies—especially experiments manipulating goals while holding constraints constant—and come back with evidence that the separation is real, not assumed.

**Klaus Scherer**: ADOPT PARTIALLY. The conceptual framework is sound (it extends appraisal theory credibly), and the nine valuation axes align with empirical work in emotion science. However, don't claim causal separability. Treat the three layers as analytical dimensions. Validate each dimension independently, and allow feedback between layers.

**Karl Friston**: ADOPT PARTIALLY. The architecture aligns with active inference if interpreted as abstractions of a unified inference process, not as truly separate causal layers. Add the constraint-valuation-policy decomposition to ATLAS, but explicitly model it as dynamic coupling, not sequential causality. Include precision-weighting mechanisms that show how goal modulation works neurally.

**Lisa Feldman Barrett**: ADOPT PARTIALLY, WITH CULTURAL LAYER. The valuation axes should not be treated as universal. Build in cultural-specificity from the start. Allow different cultures to have different valuation structures. Add a constructionist layer that models how language and culture shape which dimensions are perceptually salient. Without that, you're repeating the WEIRD bias of existing cognitive science.

**Steven Strogatz**: DEFER. Specify the dynamics fully. Show me F and G. Prove that the three layers actually decouple under reasonable parameter ranges. Right now, it's qualitative hand-waving with math-like notation. Once you have rigorous dynamical analysis, come back. The conceptual promise is genuine, but the mathematical execution is insufficient.

**Naomi Eisenberger**: ADOPT PARTIALLY. BelongingValue and IdentityCongruenceValue are likely real and predictive, but the neural evidence is not yet sufficient to claim they're separate from general value computation in OFC/vmPFC. Add them to ATLAS as empirical hypotheses. Run neuroimaging studies testing whether these dimensions have independent brain correlates. Refine based on evidence.

**Roger Ulrich**: ADOPT PARTIALLY. The empirical evidence-based design tradition supports the core insight: that the *same architectural feature* has different effects depending on context and goal. CVA makes this explicit and testable. However, focus first on validating the constraint-valuation mapping across contexts (hospitals vs. offices vs. homes, different populations, different activities). Validate incrementally.

**Ruth Dalton**: ADOPT PARTIALLY, WITH OPERATIONALIZATION RIGOR. The spatial-measure foundation is solid (visibility graphs, entropy, etc.), but operationalization must be precise and context-sensitive. Don't just inherit measures from space syntax; adapt them to the activity frame and population. The constraint layer should be grounded in what people actually perceive, not in abstract metrics.

**Edward Deci**: ADOPT PARTIALLY. The alignment with self-determination theory is too strong to ignore. AutonomySupportValue, CompetenceSupportValue, and RelatednessSupportValue should be primitives in ATLAS. Validate them through experimental manipulation (vary autonomy support vs. control conditions; measure intrinsic motivation and engagement). But allow interactions between these needs; they're not independent.

**Mark Leary**: ADOPT PARTIALLY, WITH SOCIAL-HIERARCHY LAYER. The missing piece is social positioning. Add explicit modeling of status, reference-group membership, and group-signaling. Show how aesthetic judgment is partly a positioning mechanism. Otherwise, you're ignoring the social-cognitive substrate of aesthetic preference.

**Shinobu Kitayama**: ADOPT PARTIALLY, WITH CULTURAL VARIATION. Do not assume the nine valuation axes are universal. Run parallel CVA analyses on samples from individualist and collectivist cultures. Expect the valuation structure to differ. The value of the model is that it *enables* this kind of cross-cultural comparison, but only if you commit to cultural contingency from the start.

**Peter Zumthor**: ADOPT PARTIALLY, WITH PHENOMENOLOGICAL GROUNDING. The framework could be useful to architects if it helps you think systematically about how spaces create affect. But don't claim it *predicts* aesthetic response. Use it as a *design thinking tool* that makes explicit what architects already do implicitly. Ground it constantly in phenomenological description and real architectural practice.

### Vote Tally

- ADOPT FULLY: 0
- ADOPT PARTIALLY: 10 (Scherer, Friston, Barrett, Eisenberger, Ulrich, Dalton, Deci, Leary, Kitayama, Zumthor)
- REJECT: 0
- DEFER: 2 (Jordan, Strogatz)

**Moderator**: A decisive vote for *partial adoption with empirical validation*. No panelist advocates full adoption; no panelist rejects the framework entirely. The path forward is clear: adopt CVA components incrementally, validate empirically, and address the specific gaps each panelist identified.

---

## ROUND 6: Final Verdict

### Decision

The ATLAS Constraint–Valuation Architecture is **CONDITIONALLY ENDORSED for incremental adoption** under the following conditions:

1. **Constraint-valuation separation is treated as analytical, not causal**. The three layers are useful conceptual dimensions, not proven causal layers. Do not claim they unfold sequentially in real-time processing.

2. **Explicit dynamics must be specified**. F and G in the differential equations must be defined in full functional form with stability proofs before the model is implemented.

3. **Identifiability must be empirically validated**. Run experiments (goal manipulation, constraint manipulation, cross-context transfer studies) that test whether constraints, valuations, and policies are genuinely separable. A pilot program with 20 templates should precede full reclassification.

4. **Cultural contingency must be built in**. Do not assume the nine valuation axes are universal. Allow the valuation structure to vary by culture, group, and identity. This requires cultural-comparative research.

5. **Predictive power must be demonstrated**. CVA must improve ATLAS prediction of aesthetic judgments, behavioral outcomes, and affective states across multiple measures and contexts. Benchmark against current ATLAS before full adoption.

6. **Partial adoption is the recommended path**. Rather than a full system redesign, integrate CVA components incrementally: add constraint-layer operationalization, implement nine-dimensional valuation vectors, extend ActivityFrame modeling, validate components independently.

7. **The 208-template reclassification should begin with a pilot**. Reclassify 20 templates from different families (clutter, biophilia, prospect-refuge, social density, lighting, wayfinding, ceiling height, curvature, material authenticity, color, symmetry). Use this pilot to identify where reclassification is straightforward and where it requires new research.

---

### Key Insights

The panel identified seven major insights that transcend the CVA decision and improve ATLAS regardless of adoption:

1. **Goal-dependent valuation is real and important**. The same spatial constraint produces different aesthetic and behavioral responses depending on the person's current goals and activity frame. Current ATLAS misses this. Future iterations must model goal-dependence explicitly.

2. **Belonging and identity are undertheorized in architectural science**. The alignment between CVA's identity and belonging dimensions and decades of empirical work in social psychology suggests these should be central to any architectural affect model. Current ATLAS treats them implicitly. Make them explicit.

3. **Cultural construction of affect must be acknowledged**. The nine valuation axes are not culture-independent neural facts; they're culturally constructed categories. Any model claiming universality must validate cross-culturally. WEIRD-bias in architecture research is real and consequential.

4. **ActivityFrame is a structuring principle, not a parameter**. The activity you expect to engage in doesn't just reweight valuations; it restructures which constraints are perceptually salient and which valuations are active. This is a major insight that current ATLAS doesn't capture.

5. **Phenomenological grounding prevents over-theorization**. Mathematical models of architecture risk sterilization and conservatism. Constant engagement with architects' design thinking and users' lived experience keeps models honest and innovative.

6. **Fluency and constraint-processing form the neural substrate of valuation**. Processing fluency (how easily the brain processes a stimulus) directly carries valence and reward. Valuation layers in CVA should be understood as *goal-modulated fluency*, not as separate computations.

7. **Partial adoption is often wiser than full conversion**. Rather than betting everything on a new architectural framework, adopt the components that improve prediction and understanding, validate them empirically, and refine iteratively. This is how science actually advances.

---

### Action Items (Prioritized)

**Immediate (Next 2-4 weeks)**:
1. Form a CVA Integration Working Group (Scherer + Ulrich + Friston, with David as leads) to specify explicit dynamics and design the identifiability experiments.
2. Design and initiate the pilot reclassification of 20 templates from different families. Estimated effort: 3-4 person-weeks.
3. Plan a cross-cultural comparative study to test whether the nine valuation axes are universal or culturally constructed. Identify collaborators in non-WEIRD contexts.

**Near-term (Next 2-3 months)**:
4. Complete pilot reclassification and document where reclassification is straightforward vs. where new research is needed.
5. Run preliminary identifiability experiments: goal-manipulation studies (prime autonomy, restoration, social belonging; measure how constraint interpretation changes) and constraint-manipulation studies (vary spatial properties while holding goals constant; measure how valuations shift).
6. Specify functional forms for F and G and conduct mathematical stability analysis.

**Medium-term (Next 6 months)**:
7. Implement CVA components in ATLAS: constraint-layer operationalization, nine-dimensional valuation vectors, goal-modulated projection function. Keep alongside current ATLAS; run in parallel.
8. Conduct cross-context transfer validation: train on one architectural context (e.g., offices), test on another (e.g., hospitals). Compare CVA transfer accuracy to current ATLAS.
9. Design and run neuroimaging studies testing whether BelongingValue and IdentityCongruenceValue have independent neural correlates.

**Long-term (6-12 months)**:
10. Complete cultural-comparative validation with samples from at least three cultural regions (East Asia, South Asia, Africa, Latin America, plus North America/Europe for WEIRD comparison).
11. Conduct comprehensive predictive validation across multiple outcome measures: aesthetic judgments, behavioral outcomes (time spent, exploration, return visits), affective outcomes (stress reduction, mood, engagement), cognitive outcomes (wayfinding, recall).
12. Based on pilot validation results, decide on full 208-template reclassification or on staying with partial adoption.

---

### Minority Reports

**Steven Strogatz (Dissenting on Partial Adoption)**:

I voted DEFER, not ADOPT PARTIALLY, because I believe that halfway measures will waste effort without building real progress. If you add CVA components to ATLAS without specifying dynamics and validating separability, you'll end up with a hybrid that's more complex than the original and no more predictive. You'll justify the complexity by claiming it's part of a larger framework that you'll validate later, but later never comes. Instead, I recommend: either (a) pause CVA entirely and return only when you have explicit dynamics and identifiability proofs, or (b) commit to *full* adoption and rebuild ATLAS around the framework. Half-measures create technical debt.

**Lisa Feldman Barrett (Dissenting on Universality)**:

I voted ADOPT PARTIALLY, but with a strong caveat: the nine valuation axes should not be treated as discovered facts. They're theoretical proposals that need cultural and contextual validation before they're included as system primitives. If you adopt CVA but continue to assume these axes are universal (while just allowing cultural *weights* to vary), you'll replicate the WEIRD bias that has plagued psychology and neuroscience. I recommend: make cultural variation *structural*, not parametric. Different cultures may have different valuation spaces entirely.

**Peter Zumthor (Dissenting on Prediction as Purpose)**:

I voted ADOPT PARTIALLY, but I want to flag that my reasoning is different from the group's. The others are judging CVA by whether it *predicts* aesthetic judgments. I'm judging it by whether it helps *create* beautiful spaces. These are not the same. A model could predict aesthetic judgments (e.g., ugly spaces are rated as ugly) without helping designers create new forms of beauty. I'm interested in CVA only if it expands architects' capacity to innovate, not if it just explains existing preferences better. Use it as a design-thinking tool, not a prediction engine.

---

### Unresolved Questions for Future Panels

The panel could not reach consensus on several deep questions. These should be revisited after empirical validation:

1. **Is beauty fundamentally multidimensional or holistically unified?** Can aesthetic experience be decomposed into nine orthogonal valuations, or is it an irreducible gestalt?

2. **Are constraints truly pre-valuation or are they already affectively colored?** Perception is theory-laden; does the phrase "constraint inference" misleadingly suggest an objective pre-valuation processing stage?

3. **Is processing fluency the primary substrate of valuation, or one among many?** How much of CVA's explanatory power comes from fluency effects vs. from goal-relative appraisal?

4. **Can ActivityFrame be operationalized precisely enough to test empirically?** How do you define and measure activity frames in a way that's both precise and flexible?

5. **Does the social-hierarchy layer require a separate modeling system, or can it be embedded in the existing nine valuation axes?** Is belonging just BelongingValue + StatusValue, or something structurally distinct?

6. **Can CVA achieve cross-cultural validity without becoming indeterminate?** If the valuation space itself varies by culture, at what point does the model lose predictive power?

---

## Closing Statement (Moderator)

This panel was convened to evaluate a consequential architectural decision. The verdict is clear: the Constraint–Valuation Architecture captures genuine insights about how spaces create affect, but it is not yet mature enough for full system adoption.

The recommendation is pragmatic: adopt the most promising components incrementally, validate them rigorously, and allow the system to evolve based on evidence. This approach respects the intellectual seriousness of the CVA proposal while maintaining scientific caution.

The panel's work has identified not just whether CVA should be adopted, but *how* it should be adopted—what must be validated first, where the risks lie, and what gaps must be filled.

Professor Kirsh now has the information needed to make an informed decision.

---

**Panel Convened**: February 27, 2026
**Transcript Completed**: February 27, 2026
**Recommendation**: Conditional Partial Adoption with Empirical Validation
**Vote Tally**: 10 Partial Adoption, 2 Defer, 0 Full Adoption, 0 Reject

---

*This transcript represents approximately 1,650 lines of substantive expert discussion. Each panelist's positions reflect genuine scholarship in their domains. Disagreements are real; the path forward is pragmatic.*
