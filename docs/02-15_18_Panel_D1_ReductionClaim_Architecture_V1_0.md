# PANEL D-1: REDUCTION CLAIM ARCHITECTURE
## Article Eater — Expert Panel Discussion
## February 15, 2026 — Document 18

---

## Panel Charter

**Primary Question**: What is the correct formal data structure for representing the claim that a Tier 2 theory construct (e.g., ART's "soft fascination") *reduces to* a specific composition of Tier 1 mechanistic templates?

**Secondary Questions**:
1. Should a reduction be a single causal chain or a directed acyclic graph (DAG) with multiple parallel paths?
2. How do we represent the "irreducible residual" — the piece of a Tier 2 theory that the panel judges *cannot* be expressed in Tier 1 templates?
3. Should reduction claims be versioned, given that the template library will grow?
4. How does a `ReductionClaim` integrate with the existing web of belief constraint types (`EPISTEMIC_DERIVATION`, `COHERENCE_SUPPORT`, `SUPPORTS`, `CONTRADICTS`, `CONFIRMS_PREDICTION`, `DISCONFIRMS_PREDICTION`)?
5. What is the relationship between a `ReductionClaim` and the 1,361 theory-link rows already extracted from papers and sitting in staging?

**Existing Codebase Context** (provided to all panelists):
- Nearest implemented structure: `MechanismTrace` (template_ids + causal_links + overall_maturity)
- `parent_theories: List[str]` on Theory dataclass — stores theory IDs but not mechanism chains
- `derivation_path` on beliefs — string-based, no formal structure
- `EPISTEMIC_DERIVATION` and `EPISTEMIC_CROSS_TEMPLATE` constraint types — defined but 0 rows in DB
- `FindingMechanismLink` — commented-out stub in edge_types.py
- 1,361 staging theory-link rows (1,251 ART, 102 biophilia, 3 SRT) with edge labels like `COHERENCE_SUPPORT` / `CONFIRMS_PREDICTION`

**Methodology**: Simulated expert panel with 10 researchers chosen for specific, complementary expertise on this exact question. Each panelist shares knowledge they believe others may not have, producing genuine knowledge exchange. Panelists include philosophers of science specializing in mechanistic explanation, formal epistemologists, causal modelers, knowledge representation experts, and systems neuroscientists who understand what multi-level reduction actually looks like in neural systems.

**Presiding**: Opus (theory architect)

---

## Panelists

| Name | Affiliation | Specific Expertise for This Panel |
|---|---|---|
| **William Bechtel** | UC San Diego | Mechanistic explanation, decomposition and localization, dynamic mechanistic models. Has written the leading accounts of what it means to decompose a phenomenon into component mechanisms. |
| **Carl Craver** | Washington University in St. Louis | Levels of mechanisms, constitutive relevance, the ontic conception of explanation. His work on what counts as a "good" mechanistic explanation directly addresses when a reduction claim is legitimate vs. hand-waving. |
| **Lindley Darden** | University of Maryland | Mechanism schemas, mechanism discovery, computational representations of mechanisms. Pioneer of formal mechanism representation — her "mechanism schemas" are the closest philosophical precursor to what we're building. |
| **Judea Pearl** | UCLA | Structural causal models, do-calculus, interventionism. The formalism of causal DAGs is the mathematical backbone for representing template chains as reductions. |
| **Clark Glymour** | Carnegie Mellon University | Causal discovery, formal epistemology, constraint-based causal inference. Brings the perspective of learning causal structure from data — relevant because the 1,361 staging rows are empirical causal claims that need formal structure. |
| **Peter Gärdenfors** | Lund University | Conceptual spaces, geometric models of meaning, knowledge representation. His work on how conceptual structures map between levels of description is directly relevant to cross-level reduction. |
| **Russell Poldrack** | Stanford University | Cognitive ontology, the mapping problem between psychological and neural constructs, large-scale brain organization. His Cognitive Atlas project attempted exactly the kind of construct-to-mechanism mapping we need. |
| **Danielle Bassett** | University of Pennsylvania | Network neuroscience, how neural systems compose, modular and hierarchical brain organization. Brings the neuroscience of composition — how brain networks combine to produce complex functions. |
| **Karl Friston** | University College London | Free energy principle, hierarchical generative models, variational inference. His framework for how levels relate through prediction and message-passing provides a specific computational account of inter-level reduction. |
| **Sandra Mitchell** | University of Pittsburgh | Integrative pluralism, why single reductions often fail, pragmatic approaches to scientific explanation. Critical voice — will push back on overly neat reduction schemes and insist on representing genuine complexity. |

---

## Part 1: Individual Position Statements

### 1.1 William Bechtel — Decomposition Is Not Linear

The first thing the panel needs to confront is that mechanistic explanation — and therefore mechanistic reduction — is fundamentally about *organized* systems, not linear chains (Bechtel & Abrahamsen, 2005; Bechtel, 2008). When we say "soft fascination reduces to T27 + T31 + T2," we are asserting that the phenomenon of soft fascination is produced by the organized operation of three mechanisms working together. But "working together" is doing heavy lifting in that sentence.

In my framework, a mechanistic explanation specifies: (a) the component parts, (b) the component operations, (c) the organization of parts and operations, and (d) the conditions under which the mechanism operates (Bechtel & Richardson, 1993/2010). The current `MechanismTrace` captures (a) and (b) — which templates, which causal links — but is weak on (c) and (d). Organization means how the components are arranged relative to each other — in series, in parallel, with feedback loops, with enabling conditions. Conditions means scope — when does this reduction hold, and when does it break down?

What the panel may not fully appreciate is how important the *organization* dimension is for architectural neuroscience specifically. Consider "soft fascination": the claim is not just that DMN re-engagement (T27), low auditory scene complexity (T31), and moderate visual prediction error (T2) are all present. The claim is that they operate in a specific organizational arrangement:

1. Low auditory complexity (T31) *enables* DMN re-engagement (T27) by reducing the demand for externally directed attention.
2. Moderate visual prediction error (T2) *sustains* DMN engagement without disrupting it — the prediction errors are interesting enough to maintain mild arousal but not so large as to trigger the TPN switch.
3. DMN re-engagement (T27) is the *constitutive* mechanism of restoration — it is not merely correlated with fascination, it partially constitutes the restorative state.

These are three different *types* of inter-template relationships (enabling, sustaining, constituting), and the reduction claim needs to represent all three. A flat list of template IDs loses this entirely. A single causal chain imposes a serial ordering that may not exist. What we need is a DAG with *typed edges* between the templates.

**Proposal**: The `ReductionClaim` must be a DAG, not a chain. The edges between templates in the DAG should be typed: ENABLES, SUSTAINS, CONSTITUTES, MODULATES, INHIBITS (at minimum). And the overall claim should include a "organizational narrative" — a prose description of *how* the components work together — that is not reducible to the graph structure alone.

### 1.2 Carl Craver — The Constitutive Dimension

I want to build on Bechtel's point but push it further. The central distinction from my work on levels of mechanisms (Craver, 2007; Craver & Bechtel, 2007) is between *etiological* and *constitutive* relations. An etiological relation is a cause-effect chain across time: stimulus → processing → response. A constitutive relation is a part-whole relation at a moment: the mechanism *is* (partially) its components operating together.

Most of the current template library formalizes etiological chains — "environmental feature X causes neural response Y which causes behavioral outcome Z." These are legitimate mechanistic relations, but they are not the only kind. When Kaplan and Berman claim that "soft fascination" is the experience that *arises when* DMN re-engages in the context of low-demand sensory input, they are making a constitutive claim: soft fascination isn't *caused by* DMN re-engagement, it is (partially) *constituted by* it, in the same way that a memory is constituted by hippocampal activity patterns, not caused by them.

This matters for the data structure because the `CausalLink` in `MechanismTrace` is designed for etiological relations — it has `from_variable` and `to_variable` with a temporal-causal direction. Constitutive relations don't have that direction. DMN re-engagement doesn't *cause* soft fascination and soft fascination doesn't *cause* DMN re-engagement. They are related as part to whole, mechanism to phenomenon.

The standard I have proposed for identifying constitutive relevance is the mutual manipulability criterion (Craver, 2007): a component is constitutively relevant to a phenomenon if (1) top-down interventions on the phenomenon change the component, AND (2) bottom-up interventions on the component change the phenomenon. This is testable and it distinguishes genuine constitutive relations from mere correlations.

**Proposal**: The `ReductionClaim` should distinguish between two types of template relationships:
- **ETIOLOGICAL**: Template A's output causes Template B's input (temporal, directional) — use existing `CausalLink`
- **CONSTITUTIVE**: Template A's operation partially constitutes the phenomenon being reduced (part-whole, non-directional) — new relation type needed

And each constitutive claim should carry a `mutual_manipulability_evidence` field indicating how well the constitutive relevance criterion is satisfied.

### 1.3 Lindley Darden — Mechanism Schemas and Abstraction Levels

The representational framework I developed with colleagues (Machamer, Darden, & Craver, 2000; Darden, 2006) provides a middle path between overly formal and overly informal representations. A *mechanism schema* is a truncated abstract description of a mechanism — it specifies the entities and activities at a level of abstraction that can be instantiated in multiple specific cases.

What the Article Eater project is building is, in my terminology, a library of mechanism schemas (the templates) and a set of *schema instantiation rules* (the CMR pipeline). A reduction claim, then, is a statement that a higher-level phenomenon can be *instantiated* by a specific arrangement of lower-level schemas.

What I want to bring to this discussion that the philosophers and neuroscientists may not have considered: mechanism schemas have an inherent *incompleteness*. They contain what I call "black boxes" — steps in the mechanism that are acknowledged but not yet filled in (Darden, 2006). This is not a failure of the representation; it is a feature. Early-stage mechanism discovery always has gaps, and the representation should make those gaps explicit rather than papering over them.

For the `ReductionClaim`, this means we need a way to represent "we believe soft fascination decomposes into these three template operations, BUT there is a step between T31 (low auditory demand) and T27 (DMN re-engagement) where we don't yet know the precise mechanism — we know the auditory system releases attentional resources, and we know DMN re-engages, but the bridge between them involves processes we haven't formalized." This is what David's project might call the "irreducible residual," but it's more nuanced than residual — it's a *gap in the mechanism schema* that future work should fill.

**Proposal**: Each template-to-template link in a reduction should carry a `gap_type` field from the existing 8-value GapType enum (MEDIATION, MECHANISM, BOUNDARY, DIRECTION, INTERACTION, VALIDATION, UNJUSTIFIED_EDGE, CRITICAL_QUESTION, ARGUMENT_ATTACK). This elegantly connects the reduction machinery to the existing gap predictor — gaps in reductions become research targets, prioritized by the research queue.

### 1.4 Judea Pearl — The DAG Is Non-Negotiable

I have a simple and strong position. If the project is committed to causal reasoning — and the existence of Bayesian networks, causal decomposition (CMR Step 1), and mechanism tracing (CMR Step 3) confirms that it is — then the representation of a reduction must be a directed acyclic graph with interventionist semantics (Pearl, 2009).

A DAG with interventionist semantics means: every edge in the graph corresponds to a claim that if we *intervene* on the parent node (setting it to a specific value by external force), the child node's distribution changes. This is Pearl's do-calculus: P(Y | do(X=x)) ≠ P(Y | X=x) for at least some values. This distinguishes genuine causal/mechanistic relations from mere associations.

The practical consequence for the data structure is that each edge in the reduction DAG should carry three pieces of information:
1. **Direction**: from component to phenomenon (constitutive) or from cause to effect (etiological)
2. **Interventionist evidence**: has the do(X) → Y relationship been tested? At what level of directness?
3. **Confounding structure**: what are the known or suspected confounders for this edge?

What the neuroscientists on this panel should appreciate is that the interventionist framework resolves many ambiguities about "levels." When we say T27 (DMN re-engagement) "explains" soft fascination, the interventionist question is precise: if we intervene to suppress DMN re-engagement (e.g., with transcranial magnetic stimulation of medial PFC), does soft fascination disappear? If yes, the edge is supported. If no, the claimed reduction is wrong.

I also want to address a misconception I see in the preliminary construct map. The map lists "ART Extent → T3 (cognitive map) + absence of T14 (navigational stress)." The "absence of" construction is important and tricky. In the DAG, this should be represented not as a positive edge but as a negative edge or an inhibitory relation: T14 *inhibits* the restorative experience, and its absence is required for the reduction to go through. This is straightforwardly represented in a DAG with signed edges, but it is lost in a flat list.

**Proposal**: The reduction must be a DAG with signed, typed, interventionist edges. Non-negotiable. The existing `MechanismTrace` is close but needs signed edges and edge typing. I would also strongly recommend that every edge carry a `testability` field — can this specific edge be tested by intervention, and if so, how?

### 1.5 Clark Glymour — The Staging Data Changes Everything

I want to redirect attention to a concrete problem the other panelists are not yet addressing. There are 1,361 theory-link rows extracted from scientific papers — 1,251 for ART alone — sitting in staging. These rows represent the *empirical claims* that individual researchers have made about how ART relates to underlying mechanisms. They are not theory; they are data about what the scientific community believes.

A reduction claim produced by an expert panel is a *normative* judgment: "the best current understanding says soft fascination reduces to T27 + T31 + T2." The staging data is a *descriptive* record: "paper X claims soft fascination is explained by mechanism Y." These are related but not identical. The descriptive record includes claims that may be wrong, incomplete, or mutually contradictory. The normative judgment is the panel's best synthesis.

From my work on causal discovery (Spirtes, Glymour, & Scheines, 2000), I want to propose a specific relationship between the two:

1. **The panel produces a normative reduction DAG** — the "target" reduction.
2. **Each staging theory-link is scored against the target** — does this empirical claim support, contradict, or extend the reduction?
3. **Contradictions are flagged as high-value** — they indicate either a flawed staging link OR a gap in the panel's understanding.

This means the `ReductionClaim` needs a companion structure — call it `EmpiricalReductionEvidence` — that links individual staging rows to specific edges in the reduction DAG. The staging row "Paper X says nature exposure restores attention via DMN re-engagement" gets linked to the specific T31→T27 edge in the ART soft fascination reduction. Staging rows that don't map to any edge in the reduction are either (a) evidence for a missing edge, or (b) noise.

**Proposal**: The `ReductionClaim` should have a `supporting_evidence` field that is a list of references to staging theory-link rows, each annotated with which edge in the DAG it supports or challenges. This creates a two-way bridge: the panel's theoretical judgment is grounded in empirical claims, and the empirical claims are organized by the theoretical structure.

### 1.6 Peter Gärdenfors — Conceptual Spaces and Level Translation

The problem of reduction across levels is, at its core, a problem of *translation between conceptual spaces* (Gärdenfors, 2000; 2014). ART operates in a conceptual space defined by dimensions like "fascination," "being away," "extent," "compatibility" — experiential, phenomenological dimensions. The Tier 1 templates operate in a conceptual space defined by neural variables like "DMN connectivity," "prediction error magnitude," "auditory scene complexity" — mechanistic, subpersonal dimensions.

A reduction claim is a mapping between these two spaces. And what my work on conceptual spaces tells us is that such mappings are rarely one-to-one. They are typically *many-to-many*: a single experiential dimension maps onto multiple mechanistic variables, and a single mechanistic variable participates in multiple experiential dimensions. "Soft fascination" maps onto at least three templates. But DMN re-engagement (T27) also participates in "being away" (context shift) and potentially in other ART constructs.

This many-to-many structure is essential to represent. The preliminary construct map captures the downward direction (ART construct → templates) but not the upward direction (template → all the ART constructs it participates in). For the data structure, this means:

1. Each `ReductionClaim` is about one specific Tier 2 construct.
2. A single template can appear in multiple `ReductionClaim`s.
3. The system needs a way to query both directions: "what templates explain this construct?" AND "what constructs does this template participate in?"

The second query is powerful: it tells you that if you intervene on T27 (e.g., a building design that prevents DMN re-engagement), you simultaneously affect ART's "soft fascination" AND ART's "being away" AND potentially SRT constructs — the damage propagates through the conceptual space mapping.

**Proposal**: The `ReductionClaim` should be indexed both by Tier 2 construct and by participating templates, enabling bidirectional queries. This is a data modeling decision (proper foreign keys and junction tables) not a theoretical one, but it must be specified in the design.

### 1.7 Russell Poldrack — The Cognitive Ontology Problem

Let me bring a cautionary perspective from my experience building the Cognitive Atlas (Poldrack et al., 2011; Poldrack & Yarkoni, 2016). The Cognitive Atlas attempted exactly the kind of construct-to-mechanism mapping we're discussing, and we encountered a fundamental problem: the *granularity* of psychological constructs does not match the granularity of neural mechanisms.

"Soft fascination" is defined by its phenomenological character — a quality of experience. The templates (T27, T31, T2) are defined by their neural substrates and computational operations. The question "does soft fascination reduce to T27 + T31 + T2?" presupposes that "soft fascination" is a natural kind at the psychological level that carves neural reality at its joints. But it might not. "Soft fascination" might be a folk-psychological category that bundles together several neurally distinct states that happen to feel similar.

The practical consequence for the data structure is that a `ReductionClaim` should carry a `construct_validity` assessment: how confident are we that the Tier 2 construct being reduced is a genuine natural kind rather than a heterogeneous category? This is not the same as the confidence in the reduction itself. You can be highly confident that *if* soft fascination is real, *then* it decomposes into T27 + T31 + T2 — but simultaneously uncertain about whether soft fascination is a coherent enough construct to bear that decomposition.

From the Cognitive Atlas work, I would also add: constructs at different levels of abstraction need different reduction strategies. "Attention restoration" (ART's overarching claim) is a very high-level construct that probably reduces to a complex DAG. "Parasympathetic activation" (one of SRT's intermediate constructs) is already close to the mechanistic level and may reduce to a single template chain. The data structure should accommodate this variation in complexity.

**Proposal**: Add a `construct_validity` field (HIGH/MEDIUM/LOW with justification) and a `reduction_complexity` indicator that flags whether this is a simple chain, a moderate DAG, or a complex multi-path structure. The latter helps the CMR pipeline allocate appropriate computational resources.

### 1.8 Danielle Bassett — Network Composition and Emergence

From the perspective of network neuroscience (Bassett & Sporns, 2017; Bassett et al., 2020), I want to challenge an assumption that seems implicit in the current design: that a phenomenon at the psychological level can always be decomposed into a combination of lower-level mechanisms that, when composed, produce the higher-level phenomenon. This is the assumption of mechanistic *decomposability*. It is often true — but not always.

In network neuroscience, we have clear cases of *emergent* properties that arise from the interaction of components but cannot be localized to any component or combination of components. The classic example is network small-worldness: a property of the whole graph that depends on the interaction topology, not on any individual node or subset of nodes. In the brain, the "rich club" organization — the tendency of highly connected hub regions to be interconnected — produces emergent functional properties (integration of segregated processing streams) that cannot be attributed to any individual hub.

For ART, the relevant question is: is "restoration" an emergent property of the network state, or is it the sum of component mechanisms? If DMN re-engages (T27) AND auditory demand drops (T31) AND visual prediction error is moderate (T2), is the resulting state of restoration *more than* the sum of those three template activations? If so, the reduction is incomplete — not because we're missing a template, but because the interaction produces something that no list of templates captures.

What I propose is a specific field in the `ReductionClaim` for **compositional adequacy**: a judgment by the panel about whether the listed templates, composed as specified, are *sufficient* to produce the phenomenon, or whether there is an interaction effect that goes beyond the components. This is related to Bechtel's "organization" dimension but more specific: it asks whether the organized composition is complete or whether emergence produces a residual.

**Proposal**: Add a `compositional_adequacy` field with values:
- `FULLY_DECOMPOSABLE` — the phenomenon is the sum of its template components
- `INTERACTION_DEPENDENT` — the phenomenon requires specific inter-template interactions not captured by individual templates (specify which interactions)
- `EMERGENT_RESIDUAL` — the phenomenon has properties that go beyond any composition of templates (specify what and why)

### 1.9 Karl Friston — Hierarchical Generative Models and Markov Blankets

I want to offer a unifying formal framework that may reconcile several tensions in this discussion. In the free energy principle and its application to brain architecture (Friston, 2010; Friston et al., 2017), the relationship between levels is formalized through hierarchical generative models. Higher levels generate predictions about lower levels; lower levels send prediction errors upward. Reduction, in this framework, is the statement that a higher-level variable (e.g., "soft fascination") is the *sufficient statistic* of a collection of lower-level states — it is the information about the lower level that is relevant for the level above.

More concretely: each level in a hierarchical generative model has a Markov blanket — the set of variables that separates it from all other levels. The Markov blanket of "soft fascination" in the generative model of restorative experience would be exactly the set of variables from T27, T31, and T2 that mediate between the experiential level and the deeper neural implementation. The reduction claim, formally, is an assertion about what constitutes the Markov blanket.

This addresses Craver's constitutive vs. etiological distinction naturally: within a Markov blanket, you have *active states* (which influence the level below — top-down predictions), *sensory states* (which are influenced by the level below — bottom-up errors), and *internal states* (which are neither — they are the level's own dynamics). A constitutive relation corresponds to an internal or active state being part of the blanket; an etiological relation corresponds to a sensory state from one blanket driving the active states of another.

What the philosophers should consider: the Markov blanket formalization makes the "irreducible residual" question precise. If you can specify the complete Markov blanket of a Tier 2 construct using Tier 1 templates, the reduction is complete. If the blanket includes variables that no template captures, those variables *are* the irreducible residual — and they are formally identified by their statistical independence properties.

**Proposal**: I recognize this framework may be overly abstract for immediate implementation. But I would recommend that the `ReductionClaim` include a field for `boundary_variables` — the specific variables at the interface between the Tier 2 construct and the Tier 1 templates. These boundary variables are the operationalization of the Markov blanket and they make testable predictions: if you measure these variables and find that they do not screen off the Tier 2 construct from all other variables, the reduction is incomplete.

### 1.10 Sandra Mitchell — Against Tidy Reductions

I am here to throw sand in the gears, and I make no apology for it. The history of inter-theoretic reduction in science is largely a history of failure (Mitchell, 2003; 2009). Classical Nagelian reduction — where a higher-level theory is logically derived from a lower-level theory plus bridge laws — works in almost no interesting scientific case. The reduction of thermodynamics to statistical mechanics, often cited as the paradigm case, required multiple approximations, idealizations, and auxiliary assumptions that make the "reduction" more of a creative reconstruction than a logical derivation.

Every proposal on this panel has been more sophisticated than Nagelian reduction, and I credit my colleagues for that. But I want to warn against a different failure mode: *premature closure*. The danger is that a panel of experts produces a tidy-looking reduction DAG for "soft fascination," everyone agrees it's plausible, and the system treats it as settled. Then future research reveals that the reduction was wrong — not because the templates were wrong, but because the organizational structure was different from what the panel specified.

The formal epistemological question is: how revisable should a reduction claim be? In my framework of *integrative pluralism*, the answer is: very revisable, and the representation should make the degree of revisability explicit. Some edges in a reduction DAG are well-established (e.g., the basic neurophysiology of cortisol response in T5). Others are highly speculative (e.g., the claim that auditory scene simplicity specifically enables DMN re-engagement). The data structure should make these confidence differences visible at the individual edge level, not just at the overall claim level.

I also want to push back on the assumption that every Tier 2 construct must reduce to Tier 1 templates. Some Tier 2 claims may be legitimate at their own level of description and may not have clean mechanistic reductions — not because we lack knowledge, but because the phenomenon genuinely operates at a level that resists decomposition. This is Batterman's (2002) point about asymptotic explanations: some higher-level regularities are robust precisely because they are insensitive to lower-level details.

**Proposal**: 
1. Every edge in the reduction DAG should carry its own confidence level (separate from the overall claim confidence). Use the project's existing 4-dimensional confidence stack (extraction, statistical, mechanism, epistemic).
2. The `ReductionClaim` should include an explicit `revision_history` — when it changes, the old version is preserved with a reason for revision.
3. Add a `reducibility_judgment` field: FULLY_REDUCIBLE / PARTIALLY_REDUCIBLE / AUTONOMOUSLY_EXPLANATORY. The last value means the panel judges the Tier 2 construct is legitimate at its own level and should not be forced into a mechanistic reduction.

---

## Part 2: Panel Discussion

### Thread 1: DAG vs. Chain — Rapid Consensus

**Opus** (moderating): Let us begin with the structural question. Bechtel proposed DAGs with typed edges. Pearl says DAGs are non-negotiable. Does anyone argue for simple chains?

**Glymour**: Not seriously. Even the simplest reduction in the preliminary construct map — SRT's "cortisol reduction → T5 reversal" — is a chain only because it has one component. The moment you have two or more templates contributing to a single construct, you have a DAG by definition.

**Darden**: Agreed. The mechanism schema formalism has always been graph-based, not chain-based. The real question is what types of edges the DAG allows.

**Mitchell**: I agree on DAGs as well, but I want to ensure we don't over-formalize. The DAG should allow uncertain or hypothetical edges, not just established ones.

**CONSENSUS (unanimous)**: The reduction is a DAG with typed, signed edges. No further debate needed.

### Thread 2: Edge Types — Substantive Disagreement

**Opus**: Bechtel proposed ENABLES, SUSTAINS, CONSTITUTES, MODULATES, INHIBITS. Craver added the etiological/constitutive distinction. Pearl wants interventionist evidence on every edge. Let's converge.

**Craver**: I want to be precise. The minimal edge types needed are:
1. **ETIOLOGICAL_POSITIVE** — A causes/produces B (temporal, directional, positive)
2. **ETIOLOGICAL_NEGATIVE** — A inhibits/prevents B (temporal, directional, negative)  
3. **CONSTITUTIVE** — A partially constitutes B (non-temporal, part-whole)
4. **ENABLING** — A is a background condition necessary for B but does not produce B
5. **MODULATING** — A changes the magnitude/probability of B without being necessary for B

**Bechtel**: That's close to my proposal. I'd add SUSTAINING — a component that keeps the mechanism running once initiated, distinct from enabling (which is about startup conditions).

**Pearl**: I can accept these types as annotations, but I insist that every typed edge still has a causal semantics that can be tested by intervention. Even a "constitutive" relation, as Craver defines it, is testable by mutual manipulation. The edge type describes the *nature* of the causal relation; it does not excuse the edge from empirical accountability.

**Bassett**: From a network perspective, I'd add that MODULATING edges are especially important. In brain networks, neuromodulators change the gain of connections without being "in" the circuit. Serotonin doesn't compute anything in the visual system, but it changes how the visual system computes. That's a modulating relationship that is neither etiological nor constitutive.

**Friston**: I propose we also include PREDICTING — in a hierarchical generative model, higher levels predict lower levels. This is directional (top-down) but not causal in the interventionist sense. Predictive relations are information-theoretic, not manipulative.

**Pearl**: I respectfully disagree. If a prediction from level N+1 influences processing at level N, then it is causal: do(suppress prediction) → change in level N processing. If it doesn't influence processing, it's merely a mathematical convenience, not a relation that belongs in a mechanistic explanation.

**Friston**: Fair point. If the prediction has no causal consequence, it is not a mechanism. I withdraw the proposal.

**Mitchell**: The list is getting long. Can we be parsimonious? For the implementation, simpler is better — more edge types mean more judgment calls and more opportunities for inconsistency.

**Poldrack**: Agreed. From the Cognitive Atlas experience, too many relation types paralyze annotators. I'd suggest a minimal set of four:
1. **PRODUCES** (etiological positive — covers causes, generates, leads to)
2. **INHIBITS** (etiological negative — covers prevents, suppresses, blocks)
3. **CONSTITUTES** (part-whole, non-directional — covers constitutive relevance)
4. **MODULATES** (changes magnitude/probability without being necessary)

And then use the existing moderators field on templates to capture the finer distinctions (enabling, sustaining, etc.).

**Bechtel**: I can accept that. ENABLES and SUSTAINS are important conceptual distinctions, but in practice they're difficult to distinguish empirically. They can be represented as annotations within a MODULATES or PRODUCES edge.

**Craver**: I can accept four types, provided CONSTITUTES carries its own evidence requirements — specifically, mutual manipulability evidence.

**CONSENSUS**: Four edge types: PRODUCES, INHIBITS, CONSTITUTES, MODULATES. Each edge carries confidence, evidence, and testability annotations. CONSTITUTES edges additionally carry a `mutual_manipulability_evidence` field. Finer distinctions (enabling, sustaining) are captured in edge annotations, not as separate types.

### Thread 3: The Irreducible Residual

**Opus**: Darden proposed using the 8-value GapType enum for gaps in reduction schemas. Mitchell argues some constructs are autonomously explanatory and resist reduction entirely. Bassett raised compositional adequacy. These are related but distinct. Let us disentangle them.

**Darden**: Let me be more precise. There are two different things called "residual":
1. **Schema gaps**: Places in the reduction DAG where we believe a connection exists but haven't formalized it as a template yet. These are future work. They get GapType tags and enter the research queue.
2. **Genuine irreducibility**: Properties of the Tier 2 construct that *in principle* cannot be captured by any combination of Tier 1 templates.

**Mitchell**: And I am asserting that (2) is more common than mechanists typically admit. Not as a mysterian claim, but as a scientific observation: higher-level regularities often persist precisely because they are insensitive to lower-level details. ART's "compatibility" may be an example — it may describe a person-environment fit that operates at a level of description where the specific neural mechanisms implementing the fit don't matter.

**Poldrack**: I've seen this in the Cognitive Atlas. "Cognitive control" (the construct we just declined to make Tier 1) is a high-level construct that resists clean reduction exactly because it's defined functionally, not mechanistically. Different neural mechanisms can implement "control" in different contexts. The construct is real and useful, but it doesn't map neatly onto circuits.

**Friston**: From the free energy perspective, this is the question of whether the Markov blanket of the Tier 2 construct includes variables not captured by any Tier 1 template. If it does, those variables are the formal residual. But I want to point out that this is *testable*: you can assess whether the Tier 1 templates screen off the Tier 2 construct from its inputs and outputs. If they do, reduction is complete. If they don't, there is a measurable residual.

**Bassett**: My `compositional_adequacy` proposal captures part of this. But I want to integrate it with Darden's gap types. Consider: INTERACTION_DEPENDENT means the composition requires specific inter-template interactions that aren't explicitly represented. This is a *schema gap* (Darden's type 1) — we could potentially add a template that captures the interaction. EMERGENT_RESIDUAL means the phenomenon has properties that no template composition will capture — that's Mitchell's genuine irreducibility (type 2).

**Glymour**: I like the Friston test for distinguishing them. If we can specify a set of measurable variables from the Tier 1 templates and show they statistically screen off the Tier 2 construct from its predictors, then any perceived "residual" is just a gap waiting to be filled. If they demonstrably fail to screen it off, we have genuine irreducibility. This is empirically resolvable.

**Gärdenfors**: From a conceptual spaces perspective, a genuine residual means the Tier 2 construct has dimensions that don't map onto any dimension in the Tier 1 space. This is a structural property of the conceptual spaces, not a mere gap in our knowledge. I agree with Mitchell that we should allow for this possibility.

**CONSENSUS**: Three-part representation of the residual:
1. **Schema gaps** (within the DAG): Individual edges tagged with GapType from the 8-value enum. These enter the research queue as high-priority targets.
2. **Compositional adequacy** (of the DAG as a whole): Bassett's three-value field (FULLY_DECOMPOSABLE / INTERACTION_DEPENDENT / EMERGENT_RESIDUAL).
3. **Irreducible residual narrative** (free text): If the panel judges that something cannot be captured by templates, they describe what and why. This is a *scientific judgment*, not a formal object. Future template library growth may resolve it.

### Thread 4: Versioning and Revisability

**Opus**: Mitchell argued for explicit revision history. The template library is growing — Panel IV just added 7 templates. Reductions produced before those templates existed may become obsolete or improvable. How do we handle this?

**Mitchell**: Every `ReductionClaim` should have a `version` and a `valid_as_of_template_count`. When the template library grows, the system can flag reductions that might benefit from revision: "This reduction was produced when only 40 templates existed. There are now 47. Templates T41–T47 may be relevant."

**Pearl**: Versioning is straightforward. Use semantic versioning on the reduction itself. v1.0 is the initial panel judgment. v1.1 is a minor update (e.g., adding a new supporting evidence link). v2.0 is a structural change (adding or removing a template from the DAG).

**Glymour**: I'd add: the system should flag *automatically* when new evidence appears that challenges a reduction edge. If the extraction pipeline ingests a new paper that contradicts the T31→T27 link in the ART soft fascination reduction, the reduction should be flagged for review. This is a form of belief revision — the web of belief already does this for individual claims.

**Darden**: Agreed. And the revision history should preserve the reason for each change. "v2.0: Added T45 (proactive/reactive control) to ART compatibility reduction after Panel IV identified that architectural predictability interacts with control mode."

**CONSENSUS**: 
- Semantic versioning on each `ReductionClaim`
- `valid_as_of_template_count` field for staleness detection
- `revision_history` as a list of (version, date, reason, author) tuples
- Automatic flagging when new contradicting evidence enters the web

### Thread 5: Integration with Web of Belief

**Opus**: The web of belief currently has constraint types: `EXPLAINS`, `SUPPORTS`, `CONTRADICTS`, `EPISTEMIC_DERIVATION`, `COHERENCE_SUPPORT`, `CONFIRMS_PREDICTION`, `DISCONFIRMS_PREDICTION`. How does a `ReductionClaim` relate to these?

**Glymour**: A `ReductionClaim` generates multiple constraint entries in the web of belief:
1. The overall claim "ART soft fascination reduces to T27 + T31 + T2" is an `EPISTEMIC_DERIVATION` from the templates to the construct.
2. Each edge in the reduction DAG is a `SUPPORTS` or `EXPLAINS` relation between specific template outputs and specific aspects of the construct.
3. The 1,361 staging theory-links become `COHERENCE_SUPPORT` entries: they don't *prove* the reduction, but they cohere with it.

**Pearl**: I want to distinguish more carefully. The staging rows that align with the reduction DAG are not all `COHERENCE_SUPPORT`. Some are direct empirical evidence for specific edges. "Paper X shows that DMN connectivity increases in natural vs. urban environments" is not merely coherent with the T27 edge — it is evidence for it. That should be `SUPPORTS`.

**Glymour**: Agreed — I was being imprecise. Let me revise: staging rows that provide evidence for a specific edge in the DAG → `SUPPORTS`. Staging rows that are consistent with the overall reduction but don't speak to any specific edge → `COHERENCE_SUPPORT`. Staging rows that contradict an edge → `CONTRADICTS`.

**Craver**: And when the CMR pipeline generates a prediction *from* a reduction (e.g., "if soft fascination reduces to T27+T31+T2, then we predict that buildings with low auditory complexity and moderate visual complexity should show increased DMN connectivity"), and that prediction is subsequently tested, the result is `CONFIRMS_PREDICTION` or `DISCONFIRMS_PREDICTION`.

**CONSENSUS**: A `ReductionClaim` generates web of belief entries as follows:
- Overall reduction → `EPISTEMIC_DERIVATION` (one entry)
- Each edge → potentially multiple `SUPPORTS` entries from staging data
- Staging rows consistent with overall reduction but not edge-specific → `COHERENCE_SUPPORT`
- CMR-generated predictions from the reduction, once tested → `CONFIRMS_PREDICTION` / `DISCONFIRMS_PREDICTION`
- Staging rows contradicting an edge → `CONTRADICTS`

### Thread 6: The 1,361 Staging Rows — Practical Integration

**Opus**: Glymour emphasized that the staging data changes the panel methodology. Let us be specific about how a Tier 2 panel would use these rows.

**Glymour**: Here is my proposed workflow:
1. **Before the panel**: Query staging rows for the relevant theory (e.g., 1,251 ART rows). Cluster them by which construct they relate to (soft fascination, being away, etc.). Present clusters to the panel.
2. **During the panel**: Experts examine the clusters and assess whether they support, contradict, or are irrelevant to the proposed reduction. The bottom-up empirical evidence constrains the panel's top-down theoretical reasoning.
3. **After the panel**: Link surviving staging rows to specific edges in the reduction DAG. Flag contradictions for further investigation. Remaining unlinked rows are either noise or evidence for reduction edges the panel didn't consider.

**Poldrack**: This is very similar to systematic review methodology in evidence-based medicine. The panel functions as a Delphi exercise informed by a structured evidence base. I'd add: the clusters should be presented to panelists *before* they form their individual positions, so the empirical evidence informs their priors.

**Pearl**: The staging rows also serve as a calibration check. If the panel produces a reduction with 5 edges, and 1,000 of the 1,251 ART staging rows support 2 of those edges while the other 3 edges have almost no staging support, that asymmetry is informative. The well-supported edges are high confidence; the poorly-supported edges need more scrutiny.

**Mitchell**: And the 251 ART rows that don't map to any edge in the panel's reduction — those are the most interesting. They may be noise, or they may indicate mechanisms the panel didn't consider. Either way, they should be preserved as "unaccounted evidence."

**CONSENSUS**: Staging rows are classified relative to each reduction claim:
- `EDGE_SUPPORTING` — mapped to a specific DAG edge as evidence
- `CLAIM_COHERENT` — consistent with overall reduction but not edge-specific
- `EDGE_CONTRADICTING` — contradicts a specific DAG edge
- `UNACCOUNTED` — relevant to the theory but not mappable to the panel's reduction
Each classification is stored as a junction record linking the staging row to the `ReductionClaim`.

---

## Part 3: Consensus Data Structure

### 3.1 ReductionClaim — Main Structure

```python
@dataclass
class ReductionClaim:
    # Identity
    claim_id: str                    # e.g., "RC_ART_SOFT_FASCINATION_001"
    version: str                     # semantic versioning: "1.0.0"
    created_date: str
    created_by: str                  # "Panel T2-A" or "CMR_pipeline"
    revision_history: List[RevisionEntry]

    # What is being reduced
    tier2_theory: str                # e.g., "ART"
    tier2_construct: str             # e.g., "soft_fascination"
    construct_definition: str        # precise definition of the construct
    construct_validity: str          # HIGH / MEDIUM / LOW
    construct_validity_justification: str

    # The reduction DAG
    template_nodes: List[str]        # template_ids participating: ["T27", "T31", "T2"]
    reduction_edges: List[ReductionEdge]  # typed, signed, annotated edges

    # Compositional assessment
    compositional_adequacy: str      # FULLY_DECOMPOSABLE / INTERACTION_DEPENDENT / EMERGENT_RESIDUAL
    compositional_notes: str         # explanation of adequacy judgment

    # Irreducible residual
    schema_gaps: List[SchemaGap]     # identified gaps within the DAG
    irreducible_residual: Optional[str]  # narrative: what cannot be reduced, and why
    reducibility_judgment: str       # FULLY_REDUCIBLE / PARTIALLY_REDUCIBLE / AUTONOMOUSLY_EXPLANATORY

    # Organizational narrative
    mechanism_narrative: str         # prose description of how components work together
                                     # (not reducible to the DAG structure alone — per Bechtel)

    # Evidence linkage
    supporting_evidence: List[EvidenceLink]  # links to staging rows and papers
    boundary_variables: List[str]    # Friston's Markov blanket operationalization

    # Metadata
    valid_as_of_template_count: int  # for staleness detection
    overall_confidence: str          # HIGH / MEDIUM / LOW (panel consensus)
    overall_maturity: str            # how-possibly / how-plausibly / how-actually
    panel_source: str                # which panel produced this
    key_references: List[str]        # APA references supporting the reduction
```

### 3.2 ReductionEdge — Edge in the Reduction DAG

```python
@dataclass
class ReductionEdge:
    edge_id: str
    from_node: str                   # template_id or tier2_construct
    to_node: str                     # template_id or tier2_construct
    edge_type: str                   # PRODUCES / INHIBITS / CONSTITUTES / MODULATES
    
    # Causal link (for PRODUCES / INHIBITS / MODULATES)
    causal_link: Optional[CausalLink]  # reuses existing CausalLink from template library
    
    # Constitutive evidence (for CONSTITUTES)
    mutual_manipulability_evidence: Optional[str]
    
    # Confidence (per-edge, following Mitchell)
    edge_confidence: ConfidenceStack  # 4-dimensional: extraction, statistical, mechanism, epistemic
    
    # Testability (per Pearl)
    testability: str                 # DIRECTLY_TESTABLE / INDIRECTLY_TESTABLE / NOT_YET_TESTABLE
    intervention_method: Optional[str]  # how would you test this edge?
    
    # Gaps (per Darden)
    gap_type: Optional[str]          # from 8-value GapType enum, if this edge has a known gap
    gap_description: Optional[str]
    
    # Evidence
    key_evidence: List[str]          # specific papers supporting this edge
    staging_row_ids: List[str]       # links to staging theory-link rows
```

### 3.3 Supporting Structures

```python
@dataclass
class SchemaGap:
    """A gap in the reduction schema — future research target."""
    gap_id: str
    location: str                    # which edge or between which nodes
    gap_type: str                    # from 8-value GapType enum
    description: str                 # what is missing
    priority: str                    # HIGH / MEDIUM / LOW
    suggested_investigation: str     # how might this gap be filled?

@dataclass
class EvidenceLink:
    """Link between a staging theory-link row and this reduction claim."""
    staging_row_id: str              # FK to staging theory-link table
    classification: str              # EDGE_SUPPORTING / CLAIM_COHERENT / EDGE_CONTRADICTING / UNACCOUNTED
    linked_edge_id: Optional[str]    # which edge in the DAG this supports/contradicts
    notes: Optional[str]

@dataclass
class RevisionEntry:
    """Record of a change to the reduction claim."""
    version: str
    date: str
    reason: str
    author: str                      # panel ID or "CMR_pipeline" or individual
    changes: str                     # description of what changed
```

### 3.4 ConfidenceStack (Reused from Canonical Decision 6)

```python
@dataclass 
class ConfidenceStack:
    extraction_confidence: float     # how well was this extracted from papers
    statistical_confidence: float    # p-values, effect sizes from source papers
    mechanism_confidence: float      # bridging quality + maturity
    epistemic_confidence: float      # entrenchment in web of belief
    # NEVER averaged — per Decision 6
```

---

## Part 4: Web of Belief Integration Spec

When a `ReductionClaim` is persisted, it generates the following web of belief entries:

### 4.1 Belief Nodes

| Node | Type | Content |
|---|---|---|
| The reduction claim itself | `DERIVED_REDUCTION` (new node type) | "ART soft_fascination = T27 + T31 + T2 in DAG configuration [...]" |
| Each participating template | Existing `TEMPLATE` nodes | Already in web from Sprint 7 |
| The Tier 2 construct | `THEORY_CONSTRUCT` (new node type) | "ART soft_fascination: mild involuntary attention to moderately interesting stimuli" |

### 4.2 Constraint Entries

| From | To | Constraint Type | Condition |
|---|---|---|---|
| Template set (via reduction) | Tier 2 construct | `EPISTEMIC_DERIVATION` | Always: the core reduction claim |
| Individual staging row | Specific DAG edge | `SUPPORTS` | When row provides evidence for that edge |
| Individual staging row | Overall reduction | `COHERENCE_SUPPORT` | When row is consistent but not edge-specific |
| Individual staging row | Specific DAG edge | `CONTRADICTS` | When row contradicts that edge |
| CMR prediction from reduction | Observation | `CONFIRMS_PREDICTION` / `DISCONFIRMS_PREDICTION` | After empirical test |

### 4.3 Automatic Flagging Rules

1. **Staleness**: When `template_count` in library exceeds `valid_as_of_template_count` by > 5, flag reduction for review.
2. **Contradiction**: When a new `CONTRADICTS` entry is added against any edge, flag the entire reduction.
3. **Unaccounted evidence**: When > 20% of relevant staging rows classify as `UNACCOUNTED`, flag for possible missing edges.
4. **Prediction failure**: When a CMR-derived prediction from this reduction is `DISCONFIRMED`, flag the specific edges in the prediction's trace.

---

## Part 5: Implementation Plan for CC

### Sprint 7 Tasks (New)

| Task ID | Description | Dependency | Effort |
|---|---|---|---|
| CC-7.9a | Create `ReductionClaim`, `ReductionEdge`, `SchemaGap`, `EvidenceLink`, `RevisionEntry` dataclasses in `src/theory/reduction_models.py` | CC-7.3 (needs CausalLink model) | 0.5 day |
| CC-7.9b | Create SQLAlchemy models + migration for reduction tables | CC-7.9a | 0.5 day |
| CC-7.9c | Add `DERIVED_REDUCTION` and `THEORY_CONSTRUCT` node types to node type enum | CC-1.3 (node type consolidation) | 0.25 day |
| CC-7.9d | Add edge classification fields for staging row linkage (junction table) | CC-7.9b | 0.25 day |

### Sprint 8 Tasks (New)

| Task ID | Description | Dependency | Effort |
|---|---|---|---|
| CC-8.14a | Implement `reduce_tier2_theory()` entry point in CMR pipeline | CC-8.10 + CC-7.9 | 1 day |
| CC-8.14b | Implement automatic flagging rules (staleness, contradiction, unaccounted) | CC-8.14a | 0.5 day |

### Codex Tasks (New)

| Task ID | Description | Dependency | Effort |
|---|---|---|---|
| CX-7.9b | Add `TheoryLevel` enum + `ReductionEdgeType` enum (PRODUCES/INHIBITS/CONSTITUTES/MODULATES) to `canonical_enums.json` | CC-7.9a implemented | 0.25 day |
| CX-7.9c | Add `EvidenceClassification` enum (EDGE_SUPPORTING/CLAIM_COHERENT/EDGE_CONTRADICTING/UNACCOUNTED) to contract | CC-7.9d | 0.25 day |

---

## Part 6: Worked Example — ART Soft Fascination

To validate the data structure, here is a partial worked example using the preliminary construct map:

```python
ReductionClaim(
    claim_id="RC_ART_SOFT_FASCINATION_001",
    version="1.0.0",
    created_date="2026-02-15",
    created_by="Panel T2-A",
    revision_history=[],
    
    tier2_theory="ART",
    tier2_construct="soft_fascination",
    construct_definition=(
        "A quality of attention characterized by mild, effortless, involuntary "
        "engagement with moderately interesting stimuli. Distinguished from "
        "'hard fascination' (high-demand, compelling stimuli) by its compatibility "
        "with simultaneous reflective thought. Theorized by Kaplan & Kaplan (1989) "
        "as a core mechanism of attentional restoration."
    ),
    construct_validity="MEDIUM",
    construct_validity_justification=(
        "Well-established in ART literature with consistent self-report measures "
        "(PRS scale). However, neural operationalization is still debated — "
        "no consensus biomarker distinguishes soft from hard fascination."
    ),
    
    template_nodes=["DT_DMN_MAINTENANCE_002", "AUD_SCENE_ANALYSIS_001", "PP_COMPLEXITY_GOLDILOCKS_002"],
    reduction_edges=[
        ReductionEdge(
            edge_id="RC_ART_SF_E1",
            from_node="AUD_SCENE_ANALYSIS_001",       # T31
            to_node="DT_DMN_MAINTENANCE_002",          # T27
            edge_type="PRODUCES",
            causal_link=CausalLink(
                from_variable="auditory_scene_demand",
                to_variable="dmn_reengagement_probability",
                activity="release_attentional_resources",
                from_level="SUBPERSONAL",
                to_level="SUBPERSONAL",
                bridging_quality="MEDIUM",
                maturity="how-plausibly",
                key_evidence="Berman et al., 2008; inferred from attentional resource theory",
                parameters={"threshold": "ASA demand < 0.3 normalized"}
            ),
            mutual_manipulability_evidence=None,  # not constitutive
            edge_confidence=ConfidenceStack(
                extraction_confidence=0.8,
                statistical_confidence=0.6,
                mechanism_confidence=0.5,
                epistemic_confidence=0.4
            ),
            testability="INDIRECTLY_TESTABLE",
            intervention_method=(
                "Compare DMN connectivity (fMRI or EEG) in matched natural environments "
                "differing only in auditory complexity (e.g., birdsong vs. traffic). "
                "Predict: lower auditory complexity → higher DMN connectivity."
            ),
            gap_type="MECHANISM",
            gap_description=(
                "The precise pathway from reduced auditory processing demand to DMN "
                "re-engagement is not established. Hypothesized: reduced TPN demand → "
                "competitive inhibition release → DMN activation. But the temporal "
                "dynamics and intermediary steps are not formalized."
            ),
            key_evidence=["Berman et al., 2008", "Kaplan & Berman, 2010"],
            staging_row_ids=[]  # to be populated during T2-A panel
        ),
        ReductionEdge(
            edge_id="RC_ART_SF_E2",
            from_node="PP_COMPLEXITY_GOLDILOCKS_002",   # T2
            to_node="DT_DMN_MAINTENANCE_002",           # T27
            edge_type="MODULATES",
            causal_link=CausalLink(
                from_variable="visual_prediction_error_magnitude",
                to_variable="dmn_engagement_stability",
                activity="sustain_without_disrupting",
                from_level="SUBPERSONAL",
                to_level="SUBPERSONAL",
                bridging_quality="LOW",
                maturity="how-possibly",
                key_evidence="Inferred from Goldilocks principle + DMN suppression literature",
                parameters={"optimal_PE_range": "moderate — sufficient for mild interest, insufficient for TPN takeover"}
            ),
            mutual_manipulability_evidence=None,
            edge_confidence=ConfidenceStack(
                extraction_confidence=0.7,
                statistical_confidence=0.4,
                mechanism_confidence=0.3,
                epistemic_confidence=0.3
            ),
            testability="DIRECTLY_TESTABLE",
            intervention_method=(
                "Parametrically vary visual complexity (fractal dimension) in VR "
                "nature scenes while measuring DMN connectivity. Predict inverted-U: "
                "too simple → boredom (no fascination), too complex → TPN activation "
                "(hard fascination), moderate → sustained DMN (soft fascination)."
            ),
            gap_type="BOUNDARY",
            gap_description="The 'moderate' range of PE that sustains DMN without disrupting is not quantified.",
            key_evidence=["Joye et al., 2016", "Berman et al., 2014"],
            staging_row_ids=[]
        ),
        ReductionEdge(
            edge_id="RC_ART_SF_E3",
            from_node="DT_DMN_MAINTENANCE_002",          # T27
            to_node="soft_fascination",                   # the Tier 2 construct itself
            edge_type="CONSTITUTES",
            causal_link=None,  # constitutive, not causal
            mutual_manipulability_evidence=(
                "Top-down: Instructing subjects to focus externally (suppressing "
                "soft fascination) reduces DMN connectivity (Andrews-Hanna et al., 2014). "
                "Bottom-up: TMS disruption of medial PFC (suppressing DMN) reduces "
                "self-reported restoration (preliminary evidence, Bratman et al., 2015 "
                "design implies this). Mutual manipulability: PARTIAL — top-down "
                "demonstrated, bottom-up suggestive but not yet directly tested."
            ),
            edge_confidence=ConfidenceStack(
                extraction_confidence=0.9,
                statistical_confidence=0.7,
                mechanism_confidence=0.6,
                epistemic_confidence=0.5
            ),
            testability="DIRECTLY_TESTABLE",
            intervention_method=(
                "TMS of medial PFC to suppress DMN during nature exposure. "
                "Predict: reduced self-reported soft fascination and reduced "
                "restoration benefit, despite identical sensory input."
            ),
            gap_type=None,
            gap_description=None,
            key_evidence=[
                "Andrews-Hanna et al., 2014",
                "Bratman et al., 2015",
                "Kaplan & Berman, 2010"
            ],
            staging_row_ids=[]
        )
    ],
    
    compositional_adequacy="INTERACTION_DEPENDENT",
    compositional_notes=(
        "The three templates must operate in a specific configuration: low auditory "
        "demand (T31) is a necessary precondition, moderate visual PE (T2) is a "
        "sustaining modulator, and DMN re-engagement (T27) is constitutive of the "
        "phenomenon. The interaction between T2 and T27 is critical — too little PE "
        "and DMN disengages (boredom), too much and TPN takes over (hard fascination). "
        "This interaction is not captured by any individual template."
    ),
    
    schema_gaps=[
        SchemaGap(
            gap_id="RC_ART_SF_G1",
            location="Between T31 and T27",
            gap_type="MECHANISM",
            description="Pathway from reduced auditory demand to DMN re-engagement not formalized",
            priority="HIGH",
            suggested_investigation="fMRI connectivity study: ASA demand manipulation → DMN timecourse"
        ),
        SchemaGap(
            gap_id="RC_ART_SF_G2",
            location="T2 optimal range",
            gap_type="BOUNDARY",
            description="Quantitative bounds on 'moderate' visual PE for soft fascination",
            priority="MEDIUM",
            suggested_investigation="Parametric fractal dimension manipulation in VR"
        )
    ],
    
    irreducible_residual=(
        "The phenomenological quality of 'softness' — the felt sense that attention "
        "is effortless — may not be fully captured by DMN connectivity metrics. "
        "DMN re-engagement is likely necessary but may not be sufficient for the "
        "subjective quality. Individual differences in interoceptive sensitivity "
        "(IC framework) may modulate whether DMN re-engagement is experienced as "
        "'soft fascination' or merely as 'mind wandering.' This suggests a possible "
        "missing link to the IC framework (T12) that the current reduction does not include."
    ),
    
    reducibility_judgment="PARTIALLY_REDUCIBLE",
    
    mechanism_narrative=(
        "Soft fascination arises when a natural environment presents a sensory "
        "configuration that simultaneously releases the default mode network from "
        "externally directed attentional demands and provides a gentle stream of "
        "moderately surprising perceptual input. The low-complexity auditory "
        "environment (T31) reduces the burden on auditory scene analysis, freeing "
        "attentional resources that had been allocated to monitoring environmental "
        "sounds. This resource release permits the DMN (T27) to re-engage in its "
        "characteristic internally directed processing — autobiographical memory "
        "consolidation, prospective planning, social cognition. Meanwhile, the "
        "natural visual scene provides moderate prediction errors (T2) — "
        "fractal patterns, gentle movement, clouds — that sustain a baseline of "
        "perceptual engagement without being demanding enough to trigger a full "
        "task-positive network takeover. The result is a stable state of mild, "
        "involuntary attention that is experienced phenomenologically as "
        "'fascination' and functionally as restoration of directed attention capacity. "
        "The stability of this state depends critically on the interaction between "
        "T2 and T27: the visual input must be calibrated to the Goldilocks zone "
        "where it sustains interest without disrupting internal processing."
    ),
    
    supporting_evidence=[],  # to be populated during T2-A panel with staging row links
    
    boundary_variables=[
        "auditory_scene_demand",          # T31 output
        "visual_prediction_error_magnitude",  # T2 output
        "dmn_connectivity_strength",      # T27 measurable
        "self_reported_fascination_quality"   # phenomenological measure
    ],
    
    valid_as_of_template_count=47,
    overall_confidence="MEDIUM",
    overall_maturity="how-plausibly",
    panel_source="Panel T2-A (pending)",
    key_references=[
        "Kaplan, S. (1995). The restorative benefits of nature. Journal of Environmental Psychology, 15(3), 169-182. [~4,800 citations]",
        "Kaplan, S., & Berman, M. G. (2010). Directed attention as a common resource for executive functioning and self-regulation. Perspectives on Psychological Science, 5(1), 43-57. [~1,200 citations]",
        "Berman, M. G., Jonides, J., & Kaplan, S. (2008). The cognitive benefits of interacting with nature. Psychological Science, 19(12), 1207-1212. [~3,500 citations]",
        "Andrews-Hanna, J. R., Smallwood, J., & Spreng, R. N. (2014). The default network and self-generated thought: Component processes, dynamic control, and clinical relevance. Annals of the New York Academy of Sciences, 1316(1), 29-52. [~1,800 citations]",
        "Joye, Y., & van den Berg, A. E. (2011). Is love for green in our genes? A critical analysis of evolutionary assumptions in restorative environments research. Urban Forestry & Urban Greening, 10(4), 261-268. [~200 citations]"
    ]
)
```

---

## Part 7: Full Reference List

Bassett, D. S., & Sporns, O. (2017). Network neuroscience. *Nature Neuroscience*, *20*(3), 353–364. [~2,800 citations]

Bassett, D. S., Zurn, P., & Gold, J. I. (2020). On the nature and use of models in network neuroscience. *Nature Reviews Neuroscience*, *21*(2), 1–13. [~350 citations]

Batterman, R. W. (2002). *The devil in the details: Asymptotic reasoning in explanation, reduction, and emergence*. Oxford University Press. [~1,200 citations]

Bechtel, W. (2008). *Mental mechanisms: Philosophical perspectives on cognitive neuroscience*. Routledge. [~1,800 citations]

Bechtel, W., & Abrahamsen, A. (2005). Explanation: A mechanist alternative. *Studies in History and Philosophy of Science Part C*, *36*(2), 421–441. [~1,400 citations]

Bechtel, W., & Richardson, R. C. (1993/2010). *Discovering complexity: Decomposition and localization as strategies in scientific research* (2nd ed.). MIT Press. [~3,200 citations]

Craver, C. F. (2007). *Explaining the brain: Mechanisms and the mosaic unity of neuroscience*. Oxford University Press. [~3,500 citations]

Craver, C. F., & Bechtel, W. (2007). Top-down causation without top-down causes. *Biology & Philosophy*, *22*(4), 547–563. [~600 citations]

Darden, L. (2006). *Reasoning in biological discoveries*. Cambridge University Press. [~500 citations]

Friston, K. (2010). The free-energy principle: A unified brain theory? *Nature Reviews Neuroscience*, *11*(2), 127–138. [~7,500 citations]

Friston, K., FitzGerald, T., Rigoli, F., Schwartenbeck, P., & Pezzulo, G. (2017). Active inference: A process theory. *Neural Computation*, *29*(1), 1–49. [~1,200 citations]

Gärdenfors, P. (2000). *Conceptual spaces: The geometry of thought*. MIT Press. [~5,400 citations]

Gärdenfors, P. (2014). *The geometry of meaning: Semantics based on conceptual spaces*. MIT Press. [~800 citations]

Machamer, P., Darden, L., & Craver, C. F. (2000). Thinking about mechanisms. *Philosophy of Science*, *67*(1), 1–25. [~5,500 citations]

Mitchell, S. D. (2003). *Biological complexity and integrative pluralism*. Cambridge University Press. [~1,000 citations]

Mitchell, S. D. (2009). *Unsimple truths: Science, complexity, and policy*. University of Chicago Press. [~800 citations]

Pearl, J. (2009). *Causality: Models, reasoning, and inference* (2nd ed.). Cambridge University Press. [~25,000 citations]

Poldrack, R. A., Kittur, A., Kalar, D., Miller, E., Seppa, C., Gil, Y., ... & Bilder, R. M. (2011). The Cognitive Atlas: Toward a knowledge foundation for cognitive neuroscience. *Frontiers in Neuroinformatics*, *5*, 17. [~300 citations]

Poldrack, R. A., & Yarkoni, T. (2016). From brain maps to cognitive ontologies: Informatics and the search for mental structure. *Annual Review of Psychology*, *67*, 587–612. [~350 citations]

Spirtes, P., Glymour, C., & Scheines, R. (2000). *Causation, prediction, and search* (2nd ed.). MIT Press. [~8,000 citations]

---

*Panel D-1 completed: February 15, 2026*
*Verdicts: DAG with 4 typed edges (PRODUCES/INHIBITS/CONSTITUTES/MODULATES); 3-part residual representation; semantic versioning with automatic staleness detection; web of belief integration via 5 constraint type mappings*
*Implementation: 6 new sub-tasks for CC (Sprint 7.9a-d, 8.14a-b) + 2 for Codex (7.9b-c)*
*Next document sequence number: 19*
