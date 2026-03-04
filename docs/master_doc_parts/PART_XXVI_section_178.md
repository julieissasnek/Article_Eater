# §178. The Card System — Nine Types, Universal Schema, and the Iceberg Architecture

**Date**: 2026-03-04

---

## §178.1 The Problem of Knowledge Presentation

ATLAS stores knowledge at every level of its hierarchy: T1 frameworks, T1.5 domain theories, T2 mechanistic templates, T3 empirical beliefs, molecules, argumentation structures, and the system's own architectural specifications. But a system that stores knowledge silently is not a knowledge *system*; it is a warehouse. For the knowledge to matter — for it to inform research, guide design, support clinical decisions, or shape policy — it must be presented clearly to different audiences, at different depths, with different emphases.

The problem of knowledge presentation has two parts. First, there is the *structural* problem: What are the natural units of knowledge that users encounter? Is a user seeking to understand a single empirical finding, a mechanistic principle, or a broad theoretical framework? Different questions require different kinds of answers, and a single monolithic document cannot serve all of these functions simultaneously. Wikipedia solves this problem through the entry — a focused article explaining one concept at encyclopedic depth. The entry format is familiar, modular, and navigable. ATLAS needs an analogous structure.

Second, there is the *epistemic* problem: What information should a user see immediately, and what should lie beneath the surface? A clinician does not need to see the full formal specification of the credence propagation algorithm; a system developer does. A policymaker needs design implications and population-level evidence; a researcher needs mechanistic details and sources. The same knowledge artifact can serve these different audiences only if it has layers — a visible surface that adapts to user needs, and a depth layer that contains the full provenance chain, raw data, and technical detail.

The card system solves both problems through three design principles:

**First, modular units**: ATLAS produces knowledge in nine distinct types, organized across three tiers by their level of synthesis. Each type has a fixed structure, visual requirements, and set of tabs. This modularization makes it possible to design each card type once and render it correctly everywhere.

**Second, layered presentation**: Every card has three layers. The *surface* is what the user sees in a list or search results — a thumbnail that communicates the card's identity, confidence, and freshness at a glance. The *body* consists of seven tabs that adapt to user type: researchers see different tabs in a different order than designers or clinicians. The *iceberg* is what lies beneath, invisible by default but accessible for deepening, regeneration, and audit.

**Third, adaptive UI**: The same card is rendered differently depending on who is viewing it. A researcher opening a T2 mechanism card sees Overview → Evidence → Mechanism tabs first; a designer sees Design → Overview → Mechanism. A student sees simplified prose; a developer sees full technical detail. This is not multiple cards; it is one card with adaptive presentation.

---

## §178.2 Nine Card Types Across Three Tiers

The audit of ATLAS's knowledge production (§173) identified nine distinct card types, grouped into three tiers by their epistemic function. Each tier has a characteristic purpose, audience, and update frequency.

### Tier A: Entity Cards — The Epistemic Loci

Entity cards are synthesized, multi-source entries that explain a concept in depth. They are the primary knowledge artifacts that users encounter when seeking to understand the system's domain. There are four types in this tier.

**T1 Framework Cards (10 cards)** explain one of the ten neurally grounded frameworks that form the foundation of environmental psychology in ATLAS's architecture. Examples include Predictive Processing (how hierarchical prediction-error minimization shapes perception, action, and affect) and Affective Event Theory (how environmental affordances map to emotional responses through their predictability and controllability). Each T1 card presents the framework's core mechanism, its neural implementation, its empirical support across multiple methods (fMRI, lesion, computational modeling, behavioral), and its cross-domain implications — which T1.5 theories it partially constitutes, which T2 templates it grounds. These cards are rarely updated (perhaps annually) unless new neurobiological evidence fundamentally reshapes the framework's scope or credibility.

**T1.5 Domain Theory Cards (13 cards)** explain one of the thirteen formally reduced domain theories that integrate T1 frameworks with ATLAS's specialized knowledge base. Examples include Attention Restoration Theory (how nature exposure reduces directed-attention fatigue via default-mode network release) and Prospect-Refuge Theory (how environments that offer both visual openness and protective barriers produce preferred affective states). A T1.5 card is distinguished by its *reduction claim* — a formal specification of how T1 frameworks combine to produce the theory's core predictions, and what irreducible residual remains. This residual is not a failure of theoretical reduction; it is a precise description of the new knowledge the theory adds. As David has emphasized, the card must explain what each irreducible residual *means* — not merely list it, but justify its necessity through worked examples and references to the empirical landscape. These cards are updated when major new evidence challenges the reduction claim or when T1 frameworks themselves are revised.

**T2 Mechanism Cards (166 cards)** explain one of the 166 mechanistic templates in ATLAS's inventory — specific causal pathways from environmental features through neural processes to psychological outcomes. An example: "LIGHT-01: How morning daylight (≥2,500 lux) entrains the circadian system via melanopsin-ipRGC activation, leading to improved sleep quality (medium effect, conditioned on prior sleep deprivation)." Each T2 card presents the mechanism chain with every step parameterized, the empirical evidence backing each step, design parameters with recommended ranges, known moderators and boundary conditions, and relationships to other templates (synergistic, antagonistic, conditional dependencies). T2 cards are updated frequently — when new evidence changes effect size estimates, when boundary conditions are narrowed or broadened, or when competing mechanistic accounts emerge.

**Molecule Cards (18 cards)** explain one of the eighteen latent variable bundles — patterns of co-occurrence of mechanisms that are reliably observed in nature or that co-activate together reliably in human experience. An example: "Soft Fascination — The co-occurrence of low-threat salience, moderate visual complexity, and perceptual input that permits default-mode network engagement." Each molecule card explains why these mechanisms co-occur, how they interact (multiplicatively, synergistically, conditionally), what environmental designs engage them together, and what psychological outcomes result from their co-engagement. Molecule cards are updated as T2 templates are revised or as new co-occurrence evidence emerges.

**Total Tier A: 10 + 13 + 166 + 18 = 207 entity cards.** These are the conceptual backbone of ATLAS. They should be precomputed, reviewed for accuracy and clarity, and maintained against degradation through staleness monitoring.

### Tier B: Evidence Cards — Source-Anchored Findings

Evidence cards are atomic units tied to specific empirical studies or to scientific debates. They are typically generated on demand rather than precomputed, though the most important examples should be precomputed as exemplars.

**T3 Belief Cards (12,000+ cards)** represent individual empirical claims with full provenance. An example: "Bratman et al. (2015): 90-minute nature walk reduced subgenual PFC activity (d = 0.48, 95% CI [0.04, 0.92], N = 38, one-tailed paired t-test, p < 0.05)." Each T3 card displays the claim, the source article, the effect size with confidence interval, the population and scope conditions, the warrant type (is this evidence of mechanism, of association, or of analogy?), and the confidence score assigned by ATLAS's credence system. The iceberg contains the full extraction record, quality check results, and the reflex system's assessment of whether the extraction was faithful to the original.

**Competition Cards (~120 cards)** represent contested claims — places where two or more accounts of the same phenomenon disagree. An example: "Barrett vs. Craig on affect construction — Does emotion depend on conceptual learning (Barrett) or is it constituted by interoceptive certainty (Craig)? Resolution status: EQUILIBRIUM (both accounts have strong empirical support; differences may be about conceptualization rather than mechanism)." Each competition card presents the competing accounts, the evidence for each, which theories or mechanisms depend on the outcome, and what empirical work would resolve the disagreement. These are typically generated on demand when a user asks about an active debate, but precomputed for high-stakes competitions affecting multiple T2 templates.

**Total Tier B: 12,000+ cards.** These are generated on demand from the database and serve as the empirical foundation that T2 mechanism cards synthesize.

### Tier C: System Cards — Explaining ATLAS Itself

System cards explain the architecture, algorithms, and methods that make ATLAS work. They are essential for transparency and for enabling others to extend or critique the system. There are two types in this tier.

**Layer Cards (~12 cards)** explain one major architectural layer of ATLAS. The twelve layers are: (1) Extraction Module (converting articles to structured data), (2) Web of Belief (coherence engine), (3) Bayesian Network (causal inference), (4) Credence Propagation (Algorithms 1–6), (5) Interpretation Space (question taxonomy and routing), (6) Annotation Layer (25 annotation types enriching evidence), (7) Argumentation System (Walton schemes and Toulmin structure), (8) Expert Panels (simulated deliberation), (9) QA Pipeline (question to answer workflow), (10) Prose Revision Service (writing quality), (11) Card Architecture (the system being described now), and (12) Agent Coordination (multi-agent orchestration). Each layer card explains what the layer does, how it works (with architecture diagrams), why it exists (epistemological grounding), and how it connects to other layers. These cards are updated when the layer itself is substantially refactored or when its relationship to other layers changes.

**Method Cards (~20 cards)** explain specific algorithms, processes, or decision rules within ATLAS. Examples include Typed Credence Propagation (Algorithm 1, how evidence flows through the web of belief), Graded Competition Resolution (Algorithm 2, how to assign credence when accounts disagree), Typed Global Coherence Metric (Algorithm 3, how to measure coherence at different scales), the Log-Odds Projection Calculus (the credence formula p_target = logit^{−1}(logit(p_lab) + log(d·ω·δ))), Quinean Entrenchment rate limits (which beliefs are immune to revision), and Bridge Warrant Assignment (how to classify the epistemic link between evidence and claim). Each method card presents the algorithm in pseudocode, justifies the design through philosophical and engineering rationale, provides worked examples, and analyzes sensitivity to parameter choices. These cards reference the master doc sections that provide formal fattening inserts (§129 series) for the deepest technical detail.

**Total Tier C: 12 + 20 = 32 system cards.** These are publicly documented specifications that build transparency and enable external review.

**Grand total: 207 + 12,000+ + 32 = 12,239+ cards.** Not all will be precomputed. Tier A and most of Tier C should be precomputed; Tier B is mostly generated on demand.

---

## §178.3 The Universal Schema — Surface, Body, and Iceberg

Every card, regardless of type, has three layers. This universality is essential: it means that the rendering infrastructure need only be built once, and every card type benefits from updates to the presentation system.

### The Surface: The Card Face

The surface is what the user sees before clicking in — the card as it appears in a search results list, a cluster view, or a dashboard. The surface must communicate the essential identity and epistemic status at a glance, because users often scan dozens of cards and have limited attention. The surface consists of seven fields, each with a specific visual treatment:

**Title (assertion-evidence headline).** The title is not a topic label like "Attention Restoration Theory" but an assertion that makes a claim: "Attention Restoration Reduces Directed-Attention Fatigue Through Default-Mode Network Engagement." This is the core finding or mechanism the card explains. It is written as a complete sentence, rendered in bold 16pt type, sentence case. The assertion-evidence structure ensures that the user knows immediately what the card is about without needing to read further.

**Type Badge.** A color-coded chip indicates the card's tier and type: "T1 Framework" (dark blue), "T1.5 Domain Theory" (blue), "T2 Mechanism" (teal), "T3 Belief" (green), "Molecule" (purple), "Layer" (orange), "Method" (red), "Math" (magenta). This allows users to quickly identify what kind of knowledge they are looking at.

**Confidence Thermometer.** A colored bar (from red to green) and a numeric ω score (0.0–1.0) indicate the system's assessment of the claim's credibility. The colors represent four bands: HIGH (0.8–1.0, bright green), MODERATE-HIGH (0.6–0.79, light green), MODERATE (0.4–0.59, amber), LOW (0.0–0.39, orange-red). Alongside the bar, a short gloss indicates the basis of the confidence: "14 studies, mostly consistent" or "Mixed evidence, high heterogeneity" or "Expert consensus with residual doubt." This allows users to quickly assess whether they should treat the claim as well-established or as preliminary.

**Direction Arrow.** A small icon indicates whether the card is about an increase (↑), decrease (↓), mixed effect (↔), or no effect (∅). For example, a T2 card about morning light might show ↑ next to "Sleep Quality." This is crucial for rapid scanning: users often care whether a mechanism produces a benefit, a harm, or an ambiguous effect.

**Evidence Count.** Small text below the thermometer indicates "N findings from M papers" — how many individual T3 beliefs back up this card's claims. This number is the transparency metric: if it is zero, the card is entirely theoretical; if it is high, the card rests on a substantial empirical base.

**Staleness Indicator.** A colored dot indicates the card's freshness: green (fresh, regenerated in last 3 months), amber (aging, regenerated 3–6 months ago), red (stale, regenerated >6 months ago). The staleness score (§173.4) combines the age of the backing evidence, credence shifts, and new competitions. When staleness exceeds 0.40, the card is flagged for regeneration by the agent system. This visual signal tells users at a glance which cards might be out of date.

**Key Visual.** A small thumbnail — typically a mechanism diagram, evidence chart, or conceptual illustration — gives visual salience to the card's core content. Users who process information visually can grasp the card's essence from the image alone. The visual is expandable: clicking it reveals a full-size version.

Together, these seven fields occupy roughly 3–4 inches of screen space and present a complete epistemic gestalt: What does the card claim? How confident is the system? How much evidence supports it? Is it recent? The user can decide in seconds whether to click in and read more.

### The Body: The Readable Entry

The body is what the user reads when they click open the card. It is organized as seven tabs, each addressing a different question a user might ask. Not all tabs appear in all cards (see below), but the structure is consistent.

**Overview Tab (all cards).** A 2–3 paragraph prose summary written in accessible language, targeting prose health score ≥6.5 (§170). The Overview addresses the "what and why" question: What is this card about? Why does it matter? Who should care about it? For a T2 mechanism card, the Overview might read: "When the morning light is bright (≥2,500 lux), your eye's intrinsically photosensitive retinal ganglion cells detect this as a signal that it is daytime. This signal travels to your brain's suprachiasmatic nucleus, a clock-like structure that governs your circadian rhythm. As a result, your body anticipates the day ahead — increasing alertness, core temperature, and sleep drive at appropriate times — and this leads to better sleep quality at night." This is mechanistic but not technical; it explains the causal chain in terms anyone with secondary education can follow. Key references are cited inline (author, year) to ground the narrative in evidence.

**Mechanism Tab (T1, T1.5, T2, Molecule cards).** This tab goes deeper into causal architecture. For T2 cards, the mechanism describes every step in the causal chain, parameterized with effect sizes, latencies, and necessary conditions. The tab includes a mandatory visual: a mechanism chain diagram showing the flow from environmental feature through neural process to outcome. For T1 cards, the mechanism describes the framework's neural implementation — key brain regions, neurotransmitter systems, circuit motifs — with a mandatory neural circuit diagram. For T1.5 cards, the mechanism shows the ReductionClaim DAG (§178.5) that decomposes the theory into T1 frameworks, with a mandatory visual showing the reduction and the irreducible residual. For Molecule cards, the mechanism describes how constituent templates interact (additively, synergistically, conditionally, prerequisites) with a mandatory component interaction graph.

**Evidence Tab (T1, T1.5, T2, T3, Competition cards).** This tab presents quantitative evidence summaries. For T1 and T1.5 cards: a convergence table showing which empirical methods support the framework (fMRI, lesion, single-cell, computational modeling, behavioral). For T2 and T3 cards: effect sizes with 95% confidence intervals, study counts, replication status, population scope. A mandatory visual is required: for T2 and T3, a forest plot or evidence weight chart showing effect size point estimates and intervals across studies. For T1, a methods convergence matrix. For Competition cards, a comparative strength chart showing evidence aligned with each competing account.

**Design Tab (T1.5, T2, T3, Molecule cards).** This tab addresses the practical question: What does this knowledge mean for design? For T1 cards, three to five broad architectural principles with examples (e.g., "Environments should minimize prediction error by providing stable, learnable patterns"). For T2 cards, specific design parameters with recommended ranges — for LIGHT-01, this might be "Lux level: 2,500–10,000 lux; Timing: within 30 minutes of waking; Duration: 15–60 minutes; Spectrum: blue-enriched (460–470 nm wavelength peak)." A mandatory visual is a design parameter table with ranges, optima, and population modifiers. For T3 cards, the design section distills what the single finding implies for practice. For Molecule cards, how to design environments that engage all components simultaneously.

**Connections Tab (all cards).** This tab shows how the card relates to others in the ATLAS hierarchy. For T1 cards: which T1.5 theories does this framework partially constitute (with coverage fractions), which T2 templates does it ground (with bridge warrant types)? For T1.5 cards: upward links to constituent T1 frameworks, downward links to child T2 templates, lateral links to sibling T1.5 theories sharing constituents. For T2 cards: parent T1/T1.5 theories, molecule memberships, cross-template interactions (synergistic, antagonistic, conditional). A mandatory visual is a network neighborhood diagram showing this card's local position in the web of belief. For T3 cards, the connections show which T2 templates this belief supports and which T1/T1.5 theories it connects to via bridge warrants, with a small ego-network diagram centered on this belief.

**Debate Tab (present only if competition exists).** This tab surfaces unresolved tensions, competing accounts, and open frontiers. It answers the question: Where do experts disagree about this topic? For T1 cards: known limitations, boundary conditions, competing frameworks that challenge or extend this one. For T2 cards: competing mechanism accounts, unresolved moderators, populations where the mechanism might fail. For Competition cards: full argument structure, evidence for each side, what would resolve the debate. A mandatory visual is an argument map (pro/con/rebuttal structure) or comparison chart. This tab is hidden by default for users who prefer to avoid complexity, but it is essential for researchers and system developers.

**History Tab (all cards).** A collapsed-by-default version log showing when the card was created, when it was last regenerated, and what changed. Users can expand this to see diffs: what was the previous prose? How did confidence scores shift? Did the effect size estimate change? This tab provides editorial transparency and allows users to audit whether a card has been manipulated or has drifted from its source base.

### The Iceberg: The Depth Layer

The iceberg is what lies beneath — not visible by default but essential for regeneration, audit, deepening, and provenance. When a user asks "Tell me more about this" or "What's the evidence behind this claim?" the system uses the iceberg to regenerate the card with greater depth, additional examples, or updated evidence in seconds rather than minutes. The iceberg consists of eight components:

**Source Map.** A dependency graph showing which cards, articles, theories, and molecules back this card. For a T2 mechanism card, the source map shows which T3 belief cards (empirical findings) support each step in the mechanism, which T1/T1.5 theories constitute the mechanism, and which competing mechanisms exist. For a T1.5 domain theory card, it shows which T1 frameworks contribute to the reduction (with coverage fractions) and what irreducible residual remains. This is the provenance chain that auditors and deepening algorithms use to verify claims and answer follow-up questions.

**Internal References.** Pointers to other parts of ATLAS: which master doc sections cover related topics? Which panel deliberation records discuss this card? Which sprint reports document its creation or revision? These links enable "read more" functionality within the system itself — users can jump from a card to the theoretical foundations or architectural context.

**External References.** Full APA bibliographic entries with DOIs, Google Scholar citation counts, and links to full text where available. This allows users to examine the original sources and credit the researchers whose work backs the card.

**Raw Data.** The actual database records that this card synthesizes. For T2 cards: the full T3 beliefs (with effect sizes, CIs, populations, quality scores) that empirically support the mechanism. For T1 cards: the full list of papers that provide multi-method evidence for the framework, organized by method (fMRI, lesion, computational, behavioral). For T1.5 cards: the full reduction claim specification with mutual manipulability evidence and coverage fractions. This raw data is what regeneration agents use to update the card when staleness thresholds are crossed.

**Staleness Ledger.** A dated log of all changes to backing evidence since the last card regeneration. When new T3 beliefs are added to the database that should affect the T2 card's confidence or design parameters, these are logged. When T1 framework credences shift, the ledger records this. When a new competition emerges, it is logged. This ledger is the input to the staleness calculation (§173.4): it shows exactly why a card's staleness score increased.

**Agent Context.** The prompt, model name, and parameters used to generate this card's committed prose. For cards generated by Opus, this includes the system message, the specific prompt, temperature, max_tokens, and any custom instructions about tone or depth. This record enables reproducibility: another Opus instance can be given the same inputs and should produce similar output. It also enables quality assessment: if cards generated under certain parameter settings have lower prose health or confidence calibration, the prompt or parameters can be adjusted.

**Quality Scores.** Numeric assessments of the card's quality: prose health score (0.0–10.0, from §170), confidence calibration (is ω realistic given the evidence?), coverage completeness (does the card address all major sub-questions in the interpretation space?), visual quality (do the mandatory visuals communicate clearly?). These scores are determined by automated tools and periodic expert review. Cards with low quality scores are flagged for regeneration.

**Diff Archive.** Previous versions of the card's committed prose with annotated diffs showing what changed, when, and why. If the card's evidence score increased from 0.65 to 0.78 between versions, the diff shows what new evidence drove this shift. This archive is the system's institutional memory and enables editorial review of card changes.

---

## §178.4 Tab Architecture and User-Type Adaptation

The same card is rendered differently depending on who is viewing it. This is not multiple cards; it is one logical card with adaptive presentation. The system recognizes six user types, each with distinct priorities and technical sophistication:

**Researcher.** A scientist or graduate student seeking to understand the evidence base and engage with scientific uncertainties. Default tab: Overview. Tab order: Overview → Evidence → Mechanism → Connections → Debate → Design → History. All tabs visible, full access to iceberg. This user wants to see evidence first and debate second because they care about the state of scientific knowledge.

**Designer.** An architect, landscape designer, or urban planner seeking actionable design parameters and examples of successful application. Default tab: Design. Tab order: Design → Overview → Mechanism → Evidence → Connections → History. Debate tab hidden by default (visible only if a major competition exists). This user wants design implications first; they care less about unresolved scientific tensions.

**Clinician.** A therapist, counselor, or healthcare provider seeking to understand what this knowledge means for patient care. Default tab: Overview. Tab order: Overview → Design → Evidence → Mechanism → Connections → History. Debate tab hidden unless directly relevant to clinical decisions. This user wants balanced understanding of what works and why, without getting lost in scientific minutiae.

**Policymaker.** A government official or administrator seeking evidence-based guidance for policy or resource allocation. Default tab: Overview. Tab order: Overview → Design → Evidence → History. Mechanism, Connections, and Debate tabs hidden. This user wants to know what the recommendation is and whether the evidence is solid; mechanistic details are not essential.

**Student.** An undergraduate or high school student seeking clear, scaffolded explanation of concepts. Default tab: Overview. All tabs available. Prose in Overview tab simplified to health score 8.0+, use of analogies and everyday language prioritized, technical jargon minimized. All visuals include detailed captions and legends. This user needs clarity above all else.

**Developer (hidden).** A software engineer or computer scientist extending ATLAS or integrating it with other systems. This type requires login-gated access. Default tab: Mechanism (for system cards) or Evidence (for domain cards). All tabs visible including Debate. Full access to iceberg. Developer users see additional technical documentation in sidebars: code references, API endpoints, data schema, version compatibility notes. This user needs complete transparency for integration and extension.

The adaptation is not limited to tab order. The prose health score requirements also shift by user type:

| User Type | Prose Health Target | Complexity Level |
|-----------|-------------------|-----------------|
| Student | ≥8.0 | Simple, metaphorical, everyday |
| Clinician | ≥7.0 | Applied, practical, case-inclusive |
| Policymaker | ≥6.5 | Evidence-focused, summary-oriented |
| Designer | ≥6.5 | Mechanism-linked, parameter-rich |
| Researcher | ≥6.5 | Evidence-comprehensive, debate-inclusive |
| Developer | ≥6.5 | Technical, specification-precise, formal |

When a card is regenerated, the system generates multiple versions of the Overview, Mechanism, and Design tabs to match these different prose health targets. This means Opus spends effort once (during regeneration) to produce multiple prose variants, which are cached and retrieved on demand depending on the logged-in user type.

---

## §178.5 ReductionClaim DAGs — Visualizing Theory Decomposition (Premium Treatment)

A T1.5 domain theory card is distinguished by its *reduction claim* — the formal specification of how T1 frameworks combine to produce the theory. This is the card system's most cognitively demanding visual component, and David has emphasized that "the cards that show them have to be very well designed and filled with justifications and a good visualization rather than a crappy but informative list."

### The Structure of a ReductionClaim

A reduction claim has the form: "Theory X is constituted by frameworks F₁, F₂, ..., Fₙ combined through causal interaction types I₁, I₂, ..., Iₘ, with a combined coverage fraction of α%, leaving an irreducible residual of (100−α)% that is explained by novel mechanisms R₁, R₂, ..., Rₖ."

For example, consider Attention Restoration Theory. It claims that nature exposure reduces directed-attention fatigue. The reduction breaks down as follows:

- **Predictive Processing (F₁)** contributes 25%: Nature's patterns are stable and learnable, reducing prediction error and freeing cognitive resources.
- **Affective Event Theory (F₂)** contributes 35%: Nature's affordances (openness, complexity, soft fascination) map reliably to positive emotions.
- **Default-Mode Network Theory (F₃)** contributes 20%: Directed-attention tasks suppress the DMN; nature permits its reactivation, enabling self-referential processing that replenishes attention.
- Combined framework coverage: 80%
- **Irreducible residual (20%)**: A theory-specific mechanism — the restorative power of *soft fascination* (moderate visual complexity + low threat salience) — that is not fully explained by combining the three T1 frameworks. This residual is empirically important: experiments show that nature works better than urban parks even when both offer visual complexity and low threat.

### The Visualization: A DAG with Justified Edges

The reduction is visualized as a directed acyclic graph (DAG) in which:

- **Nodes** represent T1 frameworks and the domain theory. Each node is labeled with its name and its contribution percentage (e.g., "Predictive Processing 25%").
- **Edges** represent causal interaction types:
  - **PRODUCES**: Framework F produces an outcome Y that the theory predicts. (Solid arrow)
  - **INHIBITS**: Framework F suppresses a mechanism that would interfere with the theory's predicted outcome. (Dashed red arrow)
  - **CONSTITUTES**: Framework F partially constitutes the mechanism the theory describes. (Solid green arrow)
  - **MODULATES**: Framework F's strength depends on conditions set by the theory. (Dotted blue arrow)
- **Residual node**: A labeled box showing "Irreducible Residual (20%)" with an asterisk linking to a footnote.

The DAG is rendered cleanly using Mermaid or D3, with good spacing and color contrast. Each edge is labeled with the specific causal relationship: not just "PRODUCES" but "PRODUCES: Directedness reduction via DMN suppression release."

### The Justification: Necessity and Footprint

For each edge in the DAG, the card must include a paragraph justifying why that framework is necessary — why the theory's predictions cannot be achieved by the remaining frameworks alone. The justification has three parts:

**1. Necessity proof**: An argument showing that without F, the theory's predictions fail. For example, "Without Affective Event Theory, Attention Restoration Theory cannot explain why nature is *more* restorative than other environments with similar complexity. Affective Event Theory is necessary because it links environmental affordances specifically to emotion regulation, a mechanism that Predictive Processing and DMN Theory alone cannot account for."

**2. Empirical footprint**: Concrete evidence that the framework's mechanism is active in the relevant domain. For Affective Event Theory, this might be: "Studies by Valtchanov & Ellard (2015) and others show that emotional response to nature predicts attention recovery independent of cognitive engagement, demonstrating that AET's mechanism is empirically footprinted in the literature."

**3. Coverage fraction justification**: Why is this framework assigned 25% (or 35%, or 20%) rather than another value? The justification might rest on: "Meta-analytic evidence suggests that emotional response mediates ~35% of the total variance in attention recovery (Barrett & Russell 2020), assigning Affective Event Theory 35%." Or: "Computational models of predictive processing account for ~25% of individual differences in restorative responses (Smith & Clark 2019), assigning that percentage to Predictive Processing."

### The Irreducible Residual: Explaining What Cannot Be Reduced

This is where David's requirement for premium treatment becomes critical. The irreducible residual is not a failure; it is a statement of epistemic honesty — a declaration that the domain theory adds *novel knowledge* beyond what the constituent frameworks provide.

For the Attention Restoration Theory residual, the card includes:

**A defamiliarization paragraph** (per SCIENCE_COMMUNICATION_NORMS): "Soft fascination is a perceptual state that most people encounter but rarely name. It is what you experience when watching clouds move, leaves rustle in a breeze, or light patterns dance on water. These stimuli are complex enough to hold attention but do not demand the focused, goal-directed effort that 'hard fascination' requires (e.g., watching a suspenseful movie). Soft fascination is special because it engages the visual system without exhausting directed-attention resources. This is not predictable from general principles about complexity or emotion; it is a specific perceptual configuration that has restoration power."

**A conceptual grounding**: "The irreducible residual points to a gap in neuroscience: we lack a complete theory of why certain low-salience complex stimuli are intrinsically valuable for cognitive recovery. Affective Event Theory tells us that nature is emotionally positive; Predictive Processing tells us that its patterns are learnable; DMN Theory tells us that it permits introspective engagement. But none of these frameworks predict that *moderate, threat-free visual complexity* specifically is the optimal configuration. Soft fascination is the concept that closes this gap."

**A research implication**: "This residual is high-value to identify and study. If soft fascination can be engineered into urban environments — through careful control of visual complexity and threat affordances — then attention restoration is no longer exclusive to natural settings. This would be a major design insight. The irreducible residual is thus not a limitation but a research frontier."

The card ends with a note: "See §173.3 for the formal definition of irreducible residuals and §175 for the quality criteria (structural tests) that confirm this residual is genuine and not merely an artifact of incomplete analysis."

---

## §178.6 Staleness, Regeneration, and the Card Lifecycle

Every card has a staleness score, computed according to §173.4. The score combines three weighted factors:

- **Δsource**: How long since the backing evidence was last updated? If new T3 beliefs have been extracted that should inform this card, the score increases.
- **Δcredence**: Have confidence scores shifted? If a mechanism was estimated at ω=0.65 but new meta-analyses shift it to ω=0.75, the credence component increases.
- **Δcompetition**: Have new competing accounts emerged, or have existing competitions been resolved? If a card claimed "no debate" but a new competition has been logged, this component increases.

S(card) = w₁·Δsource + w₂·Δcredence + w₃·Δcompetition

With w₁=0.3, w₂=0.5, w₃=0.2 (credence shifts matter most; new competitions matter less), the staleness score ranges from 0.0 (fully fresh) to 1.0 (maximally stale). When S(card) > 0.40, the card enters the regeneration queue.

### The Regeneration Trigger

When staleness exceeds 0.40, the card is flagged for regeneration by an agent system (§178.7). The agent receives:

1. The card's current committed prose and confidence scores
2. The iceberg: all backing evidence, the staleness ledger, the raw data
3. Updated information that has accumulated since the last regeneration

The agent's task is not to rewrite the card from scratch but to *update* it carefully:

- If the mechanism is still correct but effect sizes have shifted, the agent updates the Effect Size statement and regenerates the Evidence tab.
- If new competing accounts have emerged, the agent updates the Debate tab and may revise the confidence score.
- If the backing evidence has expanded significantly, the agent regenerates the Overview and Evidence tabs to reflect the broader base.
- If the card's scope conditions (populations, settings, moderators) have narrowed or broadened, the agent updates the Design tab.

The regenerated card is presented to a human reviewer (or to a secondary verification agent) before being committed to the canonical version. This review gate ensures that staleness-driven updates do not accidentally degrade quality.

### The Card Lifecycle

A card's lifecycle follows a simple pattern:

1. **Creation** (0 days): Agent generates committed prose, visuals, and iceberg components. Staleness = 0.0 (fresh).
2. **Deployment** (days 1–90): Card is visible to users. Backing evidence accumulates in the staleness ledger. Staleness gradually increases as Δsource increases.
3. **Aging** (days 91–180): Staleness exceeds 0.25; the amber dot appears on the surface, signaling users that the card is aging.
4. **Regeneration trigger** (day ~180–240): Staleness exceeds 0.40. The card is moved to the regeneration queue.
5. **Regeneration** (days 240–250): Agent updates the card using the iceberg and staleness ledger. Human reviewer gates the update.
6. **Recommitment** (day 250): The card's committed prose is updated. Staleness resets to 0.0 (fresh). The green dot reappears.
7. **Return to Deployment**: The cycle continues.

For entity cards (Tier A), the expected cycle is ~180 days (6 months) before regeneration is triggered. For evidence cards (Tier B), regeneration is triggered on demand as new evidence accumulates. For system cards (Tier C), regeneration is triggered when the underlying system changes significantly.

---

## §178.7 The Science Writer Agent and Card Maintenance

The card system as described above is not a static database; it is an actively maintained knowledge artifact that requires agents to generate, regenerate, verify, and update cards as the evidence base and theoretical landscape shift.

### Four Agent Roles

**Theoretical Card Agent (Opus-class).** Generates and regenerates T1, T1.5, and theoretical method cards. This requires deep knowledge integration across multiple papers, the ability to synthesize competing perspectives, and judgment about what constitutes an irreducible residual. Opus is the appropriate model for this work. The agent works from a prompt that specifies: the card type, the core claim or framework being explained, the list of T1 frameworks to be integrated (for T1.5 cards), the backing literature, the target prose health score, and any specific decisions made by expert panels. The agent is instructed to read the backing literature, cross-reference with the master doc for theoretical context, and produce committed prose that meets the Russell-style clarity standard (§170). Output is handed to a verification agent before commitment.

**Evidence Card Agent (Sonnet-class).** Generates and regenerates T2 mechanism cards, T3 belief cards on demand, and competition cards. This work requires precise statistical handling (effect sizes, confidence intervals, replication assessment) and careful extraction fidelity checking but less deep theoretical synthesis. Sonnet is sufficient. The agent works from a prompt specifying: the mechanism chain (for T2), or the empirical finding (for T3), or the competing accounts (for competition). It accesses the iceberg to retrieve raw data, generates the appropriate card body, and produces visuals.

**System Card Agent (Opus or Sonnet).** Generates and regenerates layer cards and method cards. Opus is preferable for justification (the "why" of algorithmic choices), Sonnet is sufficient for implementation description (the "how"). The agent is given the relevant master doc section (e.g., §129.2 for credence propagation fattening inserts) and produces a card that explains the architecture or algorithm in terms appropriate to the card's audience.

**Visual Agent (Sonnet-class).** Generates all card visuals — mechanism chain diagrams, forest plots, network neighborhood graphs, ReductionClaim DAGs, argument maps, design parameter tables, etc. This agent works from card data (the iceberg) and produces SVG or raster images that meet accessibility standards (WCAG 2.1 AA contrast, clear legends, semantic markup). The visual agent is invoked whenever a card is generated or regenerated.

### Coordination and Quality Gates

Agents are orchestrated by AG (§10.2 of the specification plan), which monitors staleness thresholds, calls agents when regeneration is triggered, and manages the verification pipeline. The workflow is:

1. **Staleness monitoring**: AG continuously computes S(card) for all entity and system cards. When S > 0.40, the card is flagged.
2. **Agent invocation**: AG invokes the appropriate agent (Theoretical, Evidence, System) with the card's current state and the staleness ledger.
3. **Generation**: The agent produces regenerated committed prose, updated iceberg components, and calls the visual agent.
4. **Verification gate**: The regenerated card is handed to a reference verification agent (Haiku or Sonnet) that checks: (1) Are all citations accurate? (2) Do effect size reports match the source data? (3) Is the new prose consistent with the old? (4) Is prose health ≥ target? If any gate fails, the card is returned to the generation agent with feedback.
5. **Commitment**: Once the gate passes, the card is written to canonical storage (JSON in `data/cards/`, registered in the card database). The History tab is updated with a Diff noting what changed.
6. **Master doc propagation** (optional): If the card's regeneration significantly changes domain knowledge coverage (e.g., a T1.5 card's irreducible residual is redefined), the system alerts the master doc update agent to regenerate the corresponding master doc section.

---

## §178.8 Design Decision — Cards versus Documents, Tabs versus Sections

### Why Cards Instead of a Master Document

The master document (Part I through XXVI) is a comprehensive, scholarly treatment of ATLAS's theory and architecture. It is the source of truth for formal definitions, philosophical grounding, and detailed justifications. But the master document has three limitations as a knowledge-presentation medium:

**1. Monolithic structure.** The master document is meant to be read sequentially or searched; it is not designed for quick lookup or skimming. A user asking "What does T2-041 mean?" must either search the document or navigate to the Mechanisms section and scroll. Cards solve this by making each concept a first-class entity with a dedicated URL and visual identity.

**2. Uniform prose depth.** The master document targets a single audience (researchers and system developers). It cannot adapt to clinicians, policymakers, or students without becoming unwieldy. Cards can be rendered at different prose health scores and tab orders depending on user type.

**3. Static versioning.** The master document is versioned as a whole (Part XXVI v1.0, Part XXVI v1.1). When a new paper arrives that shifts confidence in a T2 mechanism, the entire document would need to be regenerated. Cards regenerate individually, at the granularity where updates matter.

Cards are the appropriate medium for this knowledge because they are modular, adaptive, and agile. The master document remains the authoritative theoretical foundation; cards are the practical interface.

### Why Tabs Instead of Separate Sections

Each card could be rendered as a separate document with sections (Overview, Mechanism, Evidence, etc.). But tabs have three advantages:

**1. Information scent.** When a user opens a card, all tabs are visible (as labels). This gives the user an immediate sense of what information is available without requiring them to navigate elsewhere. A user can see "This card has Evidence, but no Debate" at a glance. Documents lack this scent.

**2. Scroll depth control.** By organizing content into tabs, the card prevents any single tab from becoming too long to read comfortably. The Overview tab is 2–3 paragraphs; if it were a section in a document, readers would need to scroll past Evidence, Mechanism, etc. to find what they want. Tabs keep cognitive load bounded.

**3. User agency.** Users self-select which tabs to read based on their interests. A designer who never cares about the Debate tab can ignore it; a researcher can focus on Evidence and Debate without scrolling past design parameters. Documents impose a single reading order; tabs enable multiple reading orders.

The downside of tabs is that they are less suitable for printing and require JavaScript. But ATLAS is primarily a digital system; the benefits of tabs outweigh the printing limitation.

### Why Iceberg Depth is Essential

The iceberg could be hidden deeper (require more clicks to access). But the current design — iceberg is one click away from any tab — is justified by three use cases:

**1. Deepening on demand.** A user reads the Overview and wants to know the source of a specific claim. They click "Evidence" tab → see a claim → click a reference link → the iceberg shows the full extraction record and original paper. This is frictionless deepening.

**2. Regeneration efficiency.** When a card is regenerated, the iceberg contains all the data the agent needs to update it intelligently. Without the iceberg, the agent would have to re-query the database, re-search the literature, and re-analyze the evidence from scratch. The iceberg cuts regeneration time from hours to minutes.

**3. Auditing and trust.** Users who are skeptical of a claim can dive into the iceberg and verify it themselves. A policymaker concerned about the evidence base for a design recommendation can navigate to the raw T3 beliefs, see sample sizes and effect sizes, and draw their own conclusions. This transparency is essential for building trust in the system.

### Why Precompute Some Cards, Generate Others On Demand

Precomputing all 12,000+ T3 belief cards would create massive storage and maintenance overhead. But some cards are worth precomputing:

**Tier A entity cards (207 cards).** These are the conceptual backbone. Users frequently consult them, they change infrequently, and they are expensive to generate well (especially T1 and T1.5 cards). Precompute these.

**High-leverage Tier B cards (~150 cards).** The most cited empirical findings and the highest-stakes competitions are worth precomputing. These cards are accessed frequently and serve as anchor points for other knowledge.

**Tier C system cards (32 cards).** Precompute these; they are the system's documentation.

**Remaining Tier B cards (~11,000+ cards).** Generate on demand. When a user queries the QA system asking "What does the evidence say about morning light and sleep quality?" the system retrieves the relevant T3 beliefs from the database and generates a temporary card. This is stored in a cache and reused if the same question is asked again, but it is not permanently committed to the card database.

---

## §178.9 Summary: The Card as a Design Pattern

The card system is a design pattern that solves three problems:

1. **Modularity**: Knowledge is organized into 207 entity cards, 12,000+ evidence cards, and 32 system cards. Each card is a self-contained knowledge unit with fixed structure.

2. **Adaptation**: The same card is presented differently to researchers, designers, clinicians, policymakers, students, and developers. Tabs reorder, prose adapts, visuals simplify or complexify based on user type.

3. **Lifecycle management**: Cards are born fresh (S=0), age as evidence accumulates, regenerate when staleness exceeds threshold, and re-enter the deployment cycle. This keeps the system current without requiring whole-document rewrites.

The iceberg architecture enables both user agency (deepening on demand) and system efficiency (regeneration without re-searching). The nine card types and universal schema enable once-and-done rendering infrastructure. The agent-based regeneration system enables the knowledge base to evolve continuously without human bottlenecks.

---

## References

Kuhn, T. S. (1962). *The structure of scientific revolutions*. University of Chicago Press. [~50,000 GS]

Lakatos, I. (1978). *The methodology of scientific research programmes*. Cambridge University Press. [~15,000 GS]

Pinker, S. (2014). *The sense of style: The thinking person's guide to writing in the 21st century*. Penguin Press. [~5,000 GS]

Quine, W. V. O., & Ullian, J. S. (1970). *The web of belief*. Random House. [~10,000 GS]

Toulmin, S. E. (1958). *The uses of argument*. Cambridge University Press. [~15,000 GS]

Tufte, E. R. (2001). *The visual display of quantitative information* (2nd ed.). Graphics Press. [~15,000 GS]

Walton, D. N. (1996). *Argumentation schemes for presumptive reasoning*. Lawrence Erlbaum. [~3,000 GS]

Williams, J. M. (1990). *Style: Toward clarity and grace*. University of Chicago Press. [~2,000 GS]
