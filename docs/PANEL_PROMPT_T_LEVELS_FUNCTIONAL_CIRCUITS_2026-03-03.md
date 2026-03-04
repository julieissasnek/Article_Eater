# Panel Prompt: The T-Level Taxonomy and Functional Circuits

**Date**: 2026-03-03
**Author**: AG (first draft), CW (substantive revision 2026-03-03)
**Status**: READY FOR PANEL EXECUTION

---

## Background for the Panel

We have built a knowledge system (ATLAS) for organizing scientific findings about how built environments affect human experience. The system extracts causal claims from ~800 scientific papers, integrates them into a web of belief (~4,900 beliefs, ~8,400 constraints), and answers questions through a multi-level explanatory architecture. In the course of this work we developed a layered taxonomy of theoretical entities that we designate T1, T1.5, T2, and T3, plus several auxiliary entity types (molecules, archetypes, functional circuits, T1 atoms). We currently have 10 T1 frameworks, 13 T1.5 domain theories, ~166 T2 mechanism templates, 6 T2 computational archetypes, 18 molecules, ~519 T3 empirical beliefs, ~30 T1 atom candidates, and 22 candidate functional circuits.

We ask the panel to examine three questions with increasing specificity: (1) whether this taxonomy constitutes a genuine explanatory hierarchy or a pragmatic bookkeeping device; (2) whether the recently introduced entities — functional circuits, T1 atoms, T2 archetypes — are well-motivated or proliferating beyond what the evidence warrants; and (3) where, concretely, the taxonomy goes wrong, with suggestions for revision.

**What the panel should know about our commitments**: We are *not* neutral. We believe the T-levels reflect genuine differences in explanatory grain, that T1.5 theories are not eliminable in favor of T1 frameworks (the irreducible residuals are real, not just epistemic ignorance), and that the molecule/archetype/circuit extensions — while still immature — are tracking real structure in the evidence. We want the panel to pressure-test these commitments, not to rubber-stamp them.

### The Current Taxonomy

| Level | Name | Example | Count | What It Is | Epistemic Status |
|:------|:-----|:--------|:------|:-----------|:----------------|
| T1 | Frameworks | Predictive Processing, Neuromodulatory Systems, Interoceptive Constructionism | 10 | Neurally grounded, cross-domain frameworks — the only fundamental explanatory level | Well-established; admission requires neural substrate + cross-domain generativity + convergent multi-method evidence |
| T1 atoms | Computational primitives | Prediction error, lateral inhibition, Bayesian updating, Hebbian association | ~30 | Elementary computational operations from which T1 frameworks are composed | **Speculative** — theoretically postulated, not all empirically validated as "canonical" in Carandini & Heeger's sense |
| T1.5 | Domain theories | Attention Restoration Theory, Prospect-Refuge, Stress Recovery Theory | 13 | Author-attributed domain theories with published construct definitions; *explained by* T1 but retaining irreducible residuals | Formally reduced (60-86% coverage); strict subset of molecules; requires published provenance |
| T2 templates | Mechanism chains | "Daylight exposure → circadian entrainment → alertness" | ~166 | Specific testable causal pathways: Architectural Feature → Neural/Cognitive Process → Psychological Outcome | Core unit of mechanistic explanation; ~103 calibrated with confidence scores |
| T2 archetypes | Computational motifs | Predictive Coding, Homeostatic Regulation, Accumulation to Bound, Competitive Selection, Gated Propagation, Convergent State Monitoring | 6 | Recurring computational patterns that T2 templates instantiate | **Recent addition** — motivated by recurrence patterns across templates but not yet empirically validated as a closed set |
| Molecules | Latent variables | ART-as-molecule = {Soft Fascination + Being Away + Extent + Compatibility}, each decomposed into constituent T2 templates | 18 | Compositional constructs — latent factors inferred from T2 template co-activation patterns | Analogous to latent factors in psychometrics; 13 are T1.5 theories, 5 are system composites |
| Functional Circuits | Stereotyped subnetworks | Fluency monitor, coherence monitor, threat monitor, reward PE circuit, familiarity detector | 22 | Molecules whose internal structure follows a specific T2 archetype pattern — i.e., molecules with a computational skeleton | **Most speculative layer** — functional identification without guaranteed neural specificity |
| T3 | Empirical beliefs | "Nature views reduce salivary cortisol by 15-20% within 10 min" (12 supporting articles, entrenchment 0.72) | ~519 | Ground-level empirical claims in the Web of Belief, each supported by one or more extracted article findings | Variable quality; entrenched beliefs well-supported, but many are single-article claims |

**Critical distinction for the panel**: T1.5 theories are a *strict subset* of molecules. All T1.5 theories are molecules with literature provenance (named originator, canonical citations, published construct definitions). Other molecules are system-defined composites or computationally discovered. This means T1.5 is not a separate level of reality — it is a *distinguished subset* within the molecule level, distinguished by sociological rather than ontological criteria (having an author and a literature).

### Key Structural Relations

The hierarchy has two orthogonal directions that the panel should scrutinize:

**Explanatory direction** (top-down): T1 frameworks explain T1.5 theories explain T2 templates
**Evidential direction** (bottom-up): T3 beliefs provide evidence for T2 templates which support T1.5 theories

```
T1 frameworks ──explains──► T1.5 theories (= distinguished molecules)
    │                              │
    │                              ├──composed of──► T2 templates
    │                              │
    └──composed of──► T1 atoms ──wire into──► Functional circuits
                                                     │
                                              follow pattern of──► T2 archetypes

T3 empirical beliefs ──evidence for──► T2 templates ──support──► T1.5 theories
```

**What is NOT in this diagram**: The arrows are labeled with different relations (explains, composed-of, evidence-for) and these relations have different logical properties. "Explains" is not transitive in the same way "composed-of" is. The panel should examine whether cramming these into a single hierarchy is legitimate.

### What the Taxonomy Actually Does in Practice

To ground the discussion: the taxonomy is not purely theoretical. It drives operational behavior in the system:

1. **Question answering**: When a user asks "How does daylight affect alertness?", the system traverses T2 templates, composes them into molecules, generates T1.5-level explanations, and cites T3 evidence. The T-levels determine the *structure of the answer*.
2. **Confidence propagation**: T3 belief credence propagates upward through T2 template support to calibrate T1.5 theory coverage percentages. The hierarchy is a *computational object*, not just a diagram.
3. **Gap detection**: Missing links in the hierarchy (T2 templates without T3 evidence, T1.5 theories with low coverage) drive research priority recommendations.
4. **Design guidance**: Architects receive recommendations at the molecule level ("consider ART principles") backed by T2-level specifics ("specifically, increase view access to natural elements") with T3-level evidence ("12 studies show 15-20% cortisol reduction").

---

## Panel Composition

### Philosophy of Science & Mechanistic Explanation (primary battery)

| Panelist | Role | Why Needed |
|:---------|:-----|:-----------|
| **Carl Craver** | Mechanistic explanation | His "constitutive relevance" criterion (Craver, 2007) is the sharpest test: do our T-levels pick out genuine constitutive levels, or are we conflating levels of *description* with levels of *mechanism*? His distinction between "levels of mechanisms" and "levels of nature" is directly relevant. |
| **Lindley Darden** | Mechanism discovery | Co-author of the MDC account (Machamer, Darden & Craver, 2000). Expert on how mechanism schemas are discovered, refined, and related across fields. Can she see genuine mechanism schemas in our T2 templates, or do they lack the causal specificity MDC requires? |
| **William Bechtel** | Dynamic mechanistic explanation | His work on how decomposition and localization relate (Bechtel & Abrahamsen, 2005) is critical because our hierarchy presupposes that T1 frameworks *decompose into* T1 atoms and *compose into* molecules. Is this decomposition/composition well-defined, or are we equivocating on what "composed of" means at different levels? |
| **Sandra Mitchell** | Integrative pluralism | Her framework (Mitchell, 2003) directly addresses multi-level explanatory systems. Are we doing integrative pluralism well (each level adds genuine explanatory value) or badly (proliferating levels to avoid choosing between competing explanations)? |
| **Nancy Cartwright** | Capacities and nomological machines | Her account of how causal capacities compose (Cartwright, 1999) is directly relevant to how T2 templates compose into molecules. If composition is non-additive (as she argues), our molecule construction may be systematically misleading. Her "dappled world" ontology may also challenge whether any clean hierarchy is possible. |
| **James Woodward** | Interventionist causation | Do our T2 templates satisfy Woodward's invariance conditions (Woodward, 2003)? Is the T1 → T1.5 → T2 chain an explanatory chain in his sense, or are we conflating causal explanation with theoretical subsumption? His distinction between *causal* and *constitutive* explanation is essential. |
| **Angela Potochnik** | Idealization & explanatory aims | Our taxonomy serves dual purposes (scientific understanding + engineering guidance). Potochnik's work (2017) on how idealization serves explanatory aims can tell us whether this dual purpose is coherent or whether it systematically distorts the taxonomy toward engineering convenience at the cost of scientific accuracy. |
| **Michael Strevens** | Depth of explanation | His kairetic account (Strevens, 2008) — include only difference-makers — is a razor for our granularity. Are T1 atoms too fine-grained (below the difference-making threshold)? Are T3 metabeliefs too coarse (lumping things that differ in explanatorily relevant ways)? |
| **Robert Batterman** | Asymptotic explanation & universality | His account of minimal models and universality classes (Batterman, 2002) could illuminate whether our T2 archetypes are analogous to universality classes — i.e., whether "homeostatic regulation" names a genuine mathematical structure that multiple systems fall into, or is an analogy that obscures important differences. |

### Cognitive Science & Computational Theory

| Panelist | Role | Why Needed |
|:---------|:-----|:-----------|
| **David Marr** (via framework) | Levels of analysis | Marr's three levels (Marr, 1982) are the ur-example in cognitive science. Critical question: our T-levels do NOT map cleanly onto Marr's. T1 atoms are implementation-ish, T1 frameworks are algorithm-ish, T1.5 theories are computational-ish — but this mapping is uncomfortable. The panel should make this discomfort explicit. |
| **Karl Friston** | Free energy principle | If Friston (2010) is right that all neural computation reduces to variational free energy minimization, our 6-archetype T2 taxonomy is either (a) wrong (there's only one archetype: predictive coding under FEP) or (b) a useful decomposition of FEP into sub-patterns. Friston should adjudicate. |
| **Joshua Tenenbaum** | Hierarchical Bayesian models | His work on probabilistic generative models (Tenenbaum et al., 2011) provides a formal vocabulary for what our hierarchy might be: each T-level is a prior over the level below. If this interpretation is correct, we should be able to derive the hierarchy from Bayesian model selection, not postulate it. |
| **Stanislas Dehaene** | Conscious access & global workspace | His empirical decomposition of processing stages (subliminal, preconscious, conscious; Dehaene & Changeux, 2011) is a rival hierarchical framework grounded in neural data rather than theoretical postulation. How does our framework compare to one that starts from data rather than theory? |
| **Paul Cisek** | Affordance competition | His work on parallel action specification (Cisek, 2007) is a clean instance of our "competitive selection" archetype. We want him to evaluate whether the other 5 archetypes are equally visible from inside motor neuroscience, or whether we've reified one pattern and forced the others. |

### Neuroscience & Neural Computation

| Panelist | Role | Why Needed |
|:---------|:-----|:-----------|
| **Matteo Carandini** | Canonical neural computations | Carandini & Heeger (2012) argue that divisive normalization is canonical based on *neural data*. Our T1 atoms are postulated from *theory*. Are we making the same kind of claim by a less rigorous method? How many canonical computations does the neuroscience support — is ~30 defensible or inflated? |
| **Konrad Kording** | Bayesian brain & neural data science | Can our T2 archetypes be identified in neural recordings, or are they purely computational-level constructs that leave no neural signature? If the latter, what is their ontological status? |
| **György Buzsáki** | Neural oscillations & "inside-out" | Buzsáki (2019) argues that brain dynamics are self-organized from the inside, not shaped primarily by external inputs. Our T2 templates are all "external feature → internal process → outcome" chains. Does this stimulus-response framing misrepresent how the brain actually works? |
| **Eve Marder** | Circuit degeneracy | Marder's STG work (Marder & Taylor, 2011) shows that the same behavior can arise from radically different parameter configurations. If our "functional circuits" have this degeneracy property, they are not types in the usual sense — they are equivalence classes over behaviorally similar but mechanistically different configurations. The panel should decide whether this is acceptable or fatal. |

### Developmental & Evolutionary Perspective (CW addition)

| Panelist | Role | Why Needed |
|:---------|:-----|:-----------|
| **Esther Thelen** (via dynamic systems) | Developmental dynamics | Thelen & Smith (1994) showed that cognitive categories that look like fixed types are actually attractors in a developmental landscape — they emerge, shift, and disappear with context. Do our T-levels look like fixed types that are actually developmental attractors? This is especially relevant for T1.5 theories, which may be historically contingent framings rather than natural kinds. |
| **Cecilia Heyes** | Cultural evolutionary psychology | Heyes (2018) argues that much of what looks like innate cognitive architecture is culturally inherited "cognitive gadgets." If some of our T1 atoms (imitation, mindreading) are cultural inventions rather than biological primitives, our foundational level is contaminated by cultural contingency. |
| **Peter Godfrey-Smith** | Philosophy of biology & levels | His work on biological individuality and levels of selection (Godfrey-Smith, 2009) provides a framework for asking: are our levels "real" in the way that biological levels (cell, organism, population) are, or are they more like convenience groupings? His evolutionary perspective on functional decomposition is missing from AG's original panel. |

### Formal Ontology & AI/ML (CW addition)

| Panelist | Role | Why Needed |
|:---------|:-----|:-----------|
| **Barry Smith** | Formal ontology (BFO) | Smith's Basic Formal Ontology (Smith et al., 2015) is the standard framework for biomedical ontology engineering. Our taxonomy makes ontological commitments (entities exist at levels, composition relations hold between them) that BFO could formalize or reject. Does our hierarchy satisfy basic ontological constraints (e.g., no entity at two levels, composition is well-defined, instances vs. universals are distinguished)? |
| **Judea Pearl** | Causal hierarchy & SCMs | Pearl's causal hierarchy theorem (Pearl & Mackenzie, 2018) distinguishes observational, interventional, and counterfactual levels. Our T-levels conflate causal explanation with observational pattern. Pearl could tell us whether our T2 templates are genuine causal models (with do-calculus semantics) or observational associations dressed up in causal language. |

### Psychology & Environmental Psychology

| Panelist | Role | Why Needed |
|:---------|:-----|:-----------|
| **Lisa Feldman Barrett** | Constructed emotion & population thinking | Barrett's critique (2017) of emotion "circuits" extends directly to our functional circuits. Her alternative — population thinking, where categories are statistical distributions, not types — may force us to reconceptualize functional circuits as attractors in a high-dimensional space rather than discrete entities. |
| **Rachel & Stephen Kaplan** (via ART) | Attention Restoration Theory | Would the Kaplans recognize ART in our decomposition: {Soft Fascination = templates T12+T14+T19, Being Away = templates T31+T33, ...}? Or have we carved their theory at joints they would not endorse? This is a test of whether our "formal reduction" preserves or distorts the phenomena. |
| **Roger Ulrich** (via SRT) | Stress Recovery Theory | Same question for SRT. Additionally: SRT was originally a *process theory* (recovery unfolds over time), but our templates are static mechanism chains. Does temporal structure matter, and if so, are our templates systematically losing it? |

### Systems Theory & Complex Systems

| Panelist | Role | Why Needed |
|:---------|:-----|:-----------|
| **Herbert Simon** | Hierarchy & near-decomposability | Simon (1962) argued hierarchical structure arises from temporal scale separation — subsystems that interact fast internally and slow externally. Do our T-levels have this scale-separation property? Are T1 frameworks really operating at a different temporal scale than T2 templates? If not, the hierarchy may be imposed rather than discovered. |
| **Stuart Kauffman** | Self-organization & NK landscapes | Does the notion of a "functional circuit" import an engineering metaphor (designed, specified, testable) that misrepresents what may be a self-organizing, context-sensitive, degenerate process? Kauffman's work on the structure of fitness landscapes may illuminate whether our circuits sit in deep basins (robust types) or shallow ones (fragile constructions). |

---

## Questions for the Panel

### Block A: What Are the T-Levels? (Ontological Status)

**A1.** Our T-levels (T1 → T1.5 → T2 → T3) are organized as a hierarchy from general principles to specific empirical claims. Is this hierarchy:
- (a) a genuine ontological stratification (different levels of reality, as in Craver's "levels of mechanisms")?
- (b) a pragmatic bookkeeping device (useful but not "real" — organizational, not ontological)?
- (c) an epistemic hierarchy (levels of abstraction in *our descriptions*, not in nature)?
- (d) something else — and if so, what?

We suspect the answer is "mostly (c) with some genuine (a) at the T1/T2 boundary." We want the panel to tell us whether this is defensible.

**A2.** The T1.5 level was introduced because certain domain theories (ART, Prospect-Refuge, SRT) are *explained by* T1 frameworks but retain *irreducible residuals* that resist full reduction. The residuals range from 14% (SRT, Privacy Regulation) to 40% (Place Attachment). Is the irreducible residual a principled ontological feature (these theories posit domain-specific organizational principles that are not mere consequences of T1 mechanisms), or are we naming our current ignorance? If the latter, T1.5 is a temporary staging area and we should plan for its eventual dissolution. What evidence would distinguish these two interpretations?

**A3.** T2 "archetypes" (predictive coding, homeostatic regulation, accumulation to bound, competitive selection, gated propagation, convergent state monitoring) are claimed to be recurring computational motifs. Three concerns:
- (i) Is the set of 6 principled or arbitrary? Could there be 4? 12? What determines closure?
- (ii) Do archetypes constitute natural kinds (in the sense relevant for explanation) or are they family resemblances — useful for heuristic pattern-matching but lacking the projectibility that genuine kinds have?
- (iii) Friston's FEP claims to unify all 6 under variational inference. If he is right, our archetypes are not fundamental — they are special cases of a single principle. How should we respond?

**A4.** We have ~30 "T1 atoms" (computational primitives like prediction error, lateral inhibition, Bayesian updating, Hebbian association, gain control). Some of these (divisive normalization, prediction error) have strong empirical grounding in the sense of Carandini & Heeger (2012). Others (e.g., "affordance computation," "empathic resonance") are speculative postulations from psychological-level descriptions. Is it legitimate to have atoms at different levels of empirical maturity? Or should we distinguish *empirically identified* canonical computations from *theoretically postulated* computational primitives, and if so, what are the consequences for the taxonomy?

**A5. (CW addition)** T1.5 theories are a strict subset of molecules — they are molecules with published authorship and literature provenance. This means the T1/T1.5 distinction is partly *sociological* (does this molecule have an author?) rather than ontological. Is this defensible? In scientific taxonomy we normally want our levels to be carved by the structure of nature, not by the sociology of who published what. Does this boundary need rethinking?

### Block B: Functional Circuits (The New Entities)

**B1.** We have identified 22 "functional circuits" — stereotyped patterns of T1 atoms wired according to T2 archetypes, producing functionally significant outputs (e.g., fluency monitor: prediction error + perceptual organization + metabolic cost → ease signal → hedonic marking). We acknowledge that these are the *most speculative* entities in our taxonomy. Are they:
- (a) genuine computational modules in Fodor's (1983) sense (encapsulated, domain-specific, mandatory)?
- (b) functional motifs in Alon's (2007) sense (recurring subgraph patterns with characteristic input-output profiles, but multiply realizable and context-dependent)?
- (c) phenomenological summaries (we observe certain co-activations and label them, but the label adds nothing explanatory)?
- (d) something else?

We lean toward (b) and want to know what constraints this imposes.

**B2.** Degeneracy (Edelman & Gally, 2001; Marder & Taylor, 2011) — the same function achieved by structurally different mechanisms — is a general property of biological systems. If our functional circuits have this property (the same "fluency signal" generated by different T1 atom configurations), then the circuit is not a *type* but an *equivalence class* over behaviorally similar configurations. What are the implications for explanation? Can equivalence classes be explanatory, or must explanation bottom out in specific mechanism instances?

**B3.** Barrett (2017) argues that traditional "circuits" in emotion neuroscience (fear circuit, reward circuit) are artifacts of psychological essentialism — they reify categorical boundaries that do not exist in the brain's degenerate, distributed, population-coded processing. Our functional circuits are defined *functionally* (by input-output profile) rather than *anatomically* (by brain region). Does this functional definition escape Barrett's critique, or does it merely relocate the problem?

**B4.** We need cross-domain calibration. Are our functional circuits analogous to:
- Network motifs in gene regulatory networks (Alon, 2007)?
- Canonical circuit topologies in electrical engineering (amplifier, filter, oscillator)?
- Design patterns in software engineering (Observer, Strategy, Factory)?
- Universality classes in statistical physics?

Each analogy carries different implications for how seriously to take the circuits as "real." Which analogy is most apt?

**B5. (CW addition)** Several of our "functional circuits" (social safety monitoring, empathic resonance, aesthetic evaluation) invoke psychological-level constructs that have contested or absent neural correlates. The word "circuit" implies mechanistic specificity that we may not be able to discharge at the neural level. Should we use different terminology (e.g., "functional motif," "computational pattern," "processing routine") that does not carry neural connotations? Or is the neural connotation desirable because it constrains our theorizing even when we can't yet verify it?

### Block C: The Hierarchy as a Whole

**C1.** Our hierarchy mixes two relations with different logical properties:
- **Explanatory direction** (top-down): T1 explains T1.5 explains T2
- **Evidential direction** (bottom-up): T3 data supports T2 which supports T1.5

These two directions coexist in the same hierarchy. Is this legitimate? Or are we committing a category error — confusing the order of explanation with the order of evidence? Should they be represented as two separate hierarchies (one explanatory, one evidential) that happen to share entities?

**C2.** We further mix a third relation — **compositional** — into the same hierarchy:
- T1 frameworks are composed of T1 atoms
- Molecules are composed of T2 templates
- Functional circuits are T1 atoms wired according to T2 archetypes

Composition, explanation, and evidential support are three different relations. Is our single hierarchy an admirably integrated structure or an unprincipled mashup? What formal framework (if any) would allow us to represent all three relations coherently?

**C3.** Marr's three levels (computational, algorithmic, implementational) do not map cleanly onto our T-levels. Our T3 beliefs are closest to Marr's computational level (what function is being computed — "nature reduces cortisol"). Our T2 templates are algorithmic (the mechanism chain that does it). Our T1 frameworks are... what? Not implementation (we don't specify brain regions for T1 frameworks — they're cross-domain principles). Perhaps T1 frameworks are meta-algorithmic constraints? How should we understand our T-levels relative to Marr's, and is the mismatch a bug or a feature?

**C4.** The system serves a dual purpose: scientific (organizing knowledge for researchers) and engineering (providing design guidance for architects). Does this dual purpose *constrain beneficially* (the taxonomy must be both explanatorily adequate AND practically useful, so it can't be either too abstract or too concrete) or *distort* (engineering convenience deforms scientific accuracy — e.g., we may keep molecules as entities because they are useful for architects even if they are not scientifically real)?

**C5.** Simon's (1962) near-decomposability criterion: complex systems have hierarchical structure because subsystems interact strongly internally and weakly externally. Does our hierarchy satisfy this? Specifically: is within-molecule interaction (between constituent T2 templates) really stronger than between-molecule interaction? We have preliminary evidence that T2 templates participate in multiple molecules (multi-loading), which would violate near-decomposability. How serious is this?

### Block D: Epistemics of the Taxonomy

**D1.** The taxonomy was built by a combination of (a) reading the environmental psychology literature, (b) AI-assisted extraction of causal claims from 800+ papers, and (c) theoretical postulation by the system builders. This is an unusual epistemic situation — the "data" informing the taxonomy was partially generated by AI extraction, which may have systematic biases (over-extraction of simple cause-effect claims, under-extraction of complex interactions, anchoring on certain theoretical vocabularies). How should we think about the epistemic status of a taxonomy built partly on AI-extracted data? What validation procedures would increase confidence?

**D2.** Several of our T-levels were introduced *ad hoc* to solve specific problems:
- T1.5 was introduced because domain theories didn't reduce to T1 frameworks
- Molecules were introduced because T2 templates needed compositional structure for QA
- T2 archetypes were introduced because templates seemed to fall into recurring patterns
- Functional circuits were introduced because some molecules had internal computational structure

Each addition solved a local problem. But the cumulative effect is a taxonomy with 8 entity types. Is this principled complexity or ad hoc proliferation? How do we distinguish the two?

**D3.** What would *disconfirm* each T-level? We want specific, operationalizable conditions:
- What evidence would make us abandon T1 atoms?
- What evidence would make us dissolve T1.5 into T1 + T2?
- What evidence would make us collapse T2 archetypes?
- What evidence would make us eliminate functional circuits?

If we cannot specify disconfirmation conditions, we risk unfalsifiability.

**D4.** Are there important phenomena in the built environment literature that our taxonomy *systematically cannot represent*? We are worried about:
- Temporal dynamics (our templates are static causal chains; processes unfold in time)
- Context-dependence (the same architectural feature has different effects in different contexts; our templates don't capture this well)
- Cultural variation (the same stimulus can have opposite valence across cultures; our taxonomy has limited cultural parameterization)
- Developmental change (children, adolescents, elderly may have different T1 atom repertoires)
- Individual differences (neurodivergent populations may have structurally different circuits)

### Block E: Constructive Alternatives

**E1.** Where does this taxonomy most resemble a scheme that future scientists would look back on as having been useful but ultimately wrong? Historical parallels to consider: phlogiston (a theoretical entity that seemed necessary but wasn't), Linnaeus's original taxonomy (a classification scheme that was approximately right but needed fundamental revision), faculty psychology (a decomposition of mind into faculties that maps loosely onto reality but carves at the wrong joints), the periodic table before quantum mechanics (a useful organization that was missing its explanatory foundation). Which parallel is most apt?

**E2.** If you were building this system from scratch, what would you do differently? We are specifically interested in:
- Would you use different foundational commitments (e.g., start from neural data bottom-up rather than theories top-down)?
- Would you use fewer or more levels?
- Would you organize differently (e.g., by temporal scale rather than by explanatory grain)?
- Would you avoid some of our entity types entirely?

**E3.** What are the most productive *next steps* for validating or refining the taxonomy? We have access to ~800 papers worth of extracted claims, a Bayesian network, and the full web of belief. What analyses would most efficiently distinguish genuine structure from imposed organization?

---

## Panel Process

1. **Written responses** from each panelist to all Blocks (async, ~2000 words each). Panelists should prioritize the questions most relevant to their expertise but are encouraged to comment on any question.
2. **Cross-commentary** round: panelists read each other's responses and write rebuttals, agreements, or novel observations (~500 words each). We are particularly interested in inter-disciplinary disagreements (e.g., a philosopher of science vs. a neuroscientist on what "canonical computation" means).
3. **Synthesis round**: CW + AG synthesize panel responses into:
   - Unanimous concerns (MUST address — revise taxonomy)
   - Majority concerns (SHOULD address — flag for revision)
   - Minority but incisive concerns (MAY address — track for future work)
   - Novel suggestions (evaluate for incorporation)
   - Specific disconfirmation criteria extracted from panel responses
4. **Implementation round**: Where the panel recommends taxonomy revision, CW + AG implement changes and report back with before/after comparison.

---

## CW's Preliminary Assessment of Weaknesses

The panel should know what we are already worried about, so they can either confirm these worries or redirect our attention to problems we haven't noticed:

1. **The T1.5 boundary is sociological, not ontological.** T1.5 = molecule + published author. This feels unprincipled. We would prefer a structural criterion (e.g., T1.5 theories are molecules whose irreducible residual exceeds some threshold, or whose constituent templates form a cohesive cluster in the co-occurrence space).

2. **T1 atoms are at mixed levels of empirical maturity.** Prediction error and divisive normalization have strong neural evidence. "Affordance computation" and "social safety evaluation" are theoretical postulations with weak neural grounding. We are lumping well-established canonical computations with speculative functional descriptions.

3. **Functional circuits may be Barrett's essentialist error in new clothing.** We define them functionally rather than anatomically, which we think helps, but Barrett's deeper critique — that population-coded, context-dependent neural processing does not carve into discrete "circuits" at all — may still apply.

4. **The hierarchy conflates three relations** (explanation, evidence, composition). We are not sure whether this is a strength (integrated) or a weakness (confused). We want the panel to adjudicate.

5. **Temporal dynamics are systematically absent.** Our T2 templates are static mechanism chains (A → B → C). But many environmental effects unfold in time (adaptation, habituation, sensitization, circadian variation). The taxonomy has no way to represent these temporal patterns.

6. **The 6 archetypes may not be a closed set.** We chose these 6 because they recurred across our template corpus, but we did not do a principled enumeration. There may be archetypes we missed, or our current 6 may not be carving at the right joints.

7. **Multi-loading undermines near-decomposability.** Several T2 templates participate in multiple molecules (e.g., cortisol reduction templates appear in both SRT and ART molecules). This multi-loading means molecules are not cleanly separable, which violates Simon's near-decomposability condition for legitimate hierarchical levels.

8. **The molecule schema absorbs functional circuits too easily.** During implementation (2026-03-03), we found that adding functional circuits to the system required only three new fields on the Molecule dataclass (`linked_archetypes`, `inputs`, `outputs`) and one new `molecule_type` value. The existing infrastructure — registry, indexes, QA routing — needed only a `find_by_archetype()` method. This ease of absorption is either (a) evidence that the molecule abstraction is well-designed and the circuits are natural extensions, or (b) evidence that the molecule abstraction is so flexible it absorbs anything, which means it constrains nothing. The panel should consider which interpretation is correct.

9. **The domain distribution of functional circuits is uneven and revealing.** Of our 20 registered circuits, the distribution is: perception (5), safety (3), affect (4), cognition (2), social (2), behavior (1), aesthetics (2), restoration (1). This mirrors the field's bias toward perceptual-affective mechanisms and away from social, cultural, and long-term developmental processes. But is this a bias to correct or an accurate reflection of where the mechanistic evidence is strongest?

10. **Three relations are being indexed in the same data structure.** The MoleculeRegistry now maintains three reverse indexes: `_template_index` (composition), `_framework_index` (theoretical affiliation), `_archetype_index` (computational pattern). These three indexes implement the three different relations the hierarchy conflates (evidential, explanatory, compositional). The fact that they are *implementationally independent* (three separate dictionaries, queried via separate methods) suggests they are *conceptually independent* and should perhaps be formalized as such. The panel should consider whether the hierarchy should be formally decomposed into three aligned but distinct structures.

**After panel execution, the synthesis document should explicitly address each of these 10 concerns.**
