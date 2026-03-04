# § 180 ATLAS System Architecture — A Layer-by-Layer Guide

**Last updated**: 2026-03-04
**Version**: ATLAS V23.0.1
**Scope**: Comprehensive architectural overview for readers unfamiliar with preceding sections

---

## §180.1 The Architectural Vision — From Articles to Answers

ATLAS is a knowledge system designed to extract, organize, and reason over scientific findings about how the built environment shapes human psychology. The system's architecture reflects a fundamental epistemic commitment: that knowledge is best represented not as a monolithic database or fact table, but as a coherence network of mutually supporting beliefs, interconnected by warrants of varying strength and type.

The journey from article to answer illustrates the system's design philosophy. A researcher submits a question — for instance, *"How does natural light exposure affect circadian rhythm entrainment in office workers?"* That question does not yield a single fact lookup. Instead, ATLAS orchestrates a multi-layer reasoning process:

1. The question is classified and routed to specialized handlers.
2. The Epistemic Network searches for relevant beliefs (T3), mechanistic templates (T2), and frameworks (T1).
3. The Credence Computation Layer weighs evidence quality, coherence patterns, and entrenchment.
4. The Argumentation Layer assembles competing claims and gap-discovery rules.
5. The Interpretation Space applies epistemic zones and probatory rules tailored to the question type.
6. The Presentation Layer synthesizes findings into a graded card structure with visual evidence and uncertainty signals.
7. Human experts (through the AI panel resolver) validate the final answer.

This architecture emerged from three design principles:

**Quinean Coherentism**: Following Quine's vision of a web of belief, ATLAS represents knowledge as a network where each belief's credence depends on its coherence with neighbors, not its isolation from others (Quine, 1951; Quine & Ullian, 1970). No single belief is sacred; all are revisable in the light of new evidence.

**Epistemic Transparency**: Every assertion carries visible traces of its epistemic status — where it came from, what alternative claims exist, what gaps remain, and what assumptions underpin it. The system does not hide its uncertainty; it celebrates it as a form of intellectual honesty.

**Layered Reasoning**: Rather than a single monolithic inference engine, ATLAS uses specialized layers — each addressing a distinct reasoning problem (evidence validation, belief coherence, argumentation, credence propagation, presentation). This separation of concerns allows expert review and modification of each layer independently.

The architecture contains eleven logically distinct layers, organized into three functional groups: **input and acquisition** (Evidence Ingestion), **epistemic representation and reasoning** (Epistemic Network through Credence Computation), and **output and interaction** (Quality Assurance, Presentation, QA Pipeline, and Agents). An Operational Layer oversees the entire system's health and scheduling.

---

## §180.2 The Evidence Ingestion Pipeline — Discovery Through Validation

The Evidence Ingestion Layer transforms raw scientific papers into validated, structured findings ready for integration into ATLAS's knowledge network. This pipeline addresses a fundamental challenge: how to systematically extract knowledge claims from unstructured academic prose, distinguish noise from signal, and maintain epistemic integrity at scale.

### Paper Discovery and Preprocessing

The pipeline begins with paper discovery. ATLAS monitors feeds from Semantic Scholar and Zotero, identifying papers relevant to environmental psychology using keyword matching and semantic similarity. Each paper is retrieved in PDF form, then subjected to preprocessing: OCR for scanned documents, reference extraction, metadata standardization, and section segmentation.

The preprocessing step is deceptively important. Academic PDFs vary wildly in structure — some are well-formatted, others are scans, still others contain figures as key evidence. The system must standardize these diverse inputs before extraction can proceed. Extracted text is quality-checked for OCR artifacts, and figures are retained as separate objects for later visual analysis.

### Paper Triage

Not every paper merits the full extraction pipeline. Papers are triaged into five categories:

- **EMPIRICAL**: Experimental or quasi-experimental studies with measurable outcomes
- **SYNTHESIS**: Reviews, meta-analyses, or summaries of existing research
- **THEORETICAL**: Models, frameworks, or hypothesis papers without direct empirical support
- **QUALITATIVE**: Interview, observational, or ethnographic studies
- **CASE_STUDY**: In-depth analyses of single environments or populations

Triage is performed by a lightweight classifier (currently Gemini 1.5 Pro with few-shot prompts) and validated by human review. This classification drives the selection of extraction prompts and determines the initial credence weighting in the Epistemic Network.

### Extraction via Generative Model

The core extraction step uses Google's Gemini with family-specific prompts calibrated for each paper type. Each prompt asks the model to extract structured findings in the form:

```
Finding (F): [Claim about environment and psychology]
Population (Pop): [Who was studied]
Context (C): [What environment or condition]
Outcome (Out): [What was measured]
Evidence Quality (Q): [Confidence level: HIGH, MEDIUM, LOW]
Mechanism (M): [Proposed causal pathway]
Limitations (L): [Known constraints on generalizability]
```

The prompt design is critical. An EMPIRICAL prompt emphasizes quantitative outcomes and sample sizes. A QUALITATIVE prompt asks for thematic synthesis and trustworthiness markers. A THEORETICAL prompt focuses on causal mechanisms and model assumptions. This family-specific approach reflects the insight that different paper types warrant different extraction logics.

The extraction is not a single pass. Rather, Gemini generates a candidate set of findings, which are then validated against the paper's own internal evidence and cross-checked for coherence with surrounding claims. Findings that cannot be traced to specific paper sections are flagged for human review.

### Validation Gate

The Validation Gate applies 50+ field-level rules to each extracted finding. Does the Population field contain a specific population descriptor (not just "subjects")? Is the Context field grounded in a specific built environment (office, hospital, home, street)? Is the Outcome field measurable and distinct from the Finding? Are the Evidence Quality and Limitations fields non-trivial?

Findings must achieve a composite validation score of 0.75 or higher to proceed into the Epistemic Network. Findings below this threshold are quarantined in a *pending* status, requiring either reformulation by the AI or explicit human override. This gate prevents the accumulation of under-specified or incoherent beliefs in the network.

Once validated, the finding is instantiated as a T3 belief (an empirical claim grounded in a specific paper) and connected to relevant T2 templates, T1 frameworks, and molecules through a warrant-assignment process (see §180.3).

---

## §180.3 The Epistemic Network — Beliefs, Templates, Frameworks, and Molecules

The Epistemic Network is ATLAS's knowledge repository. It does not store facts; it stores beliefs organized in a hierarchy of increasing generality, interconnected by typed warrants of varying strength.

### The Belief Hierarchy

**Tier 3 (T3) — Empirical Beliefs**: These are grounded claims extracted from specific papers. Example: *"Exposure to daylight (at intensity > 500 lux for ≥ 2 hours/day) correlates with improved sleep quality (Pittsburgh Sleep Quality Index, p < 0.05) in office workers in temperate climates."* A T3 belief carries metadata: the paper source, population, context, outcome, extraction quality score, and validity status. The current ATLAS system contains approximately 12,000 validated T3 beliefs.

**Tier 2 (T2) — Mechanistic Templates**: These are parameterized causal structures that explain how multiple T3 beliefs might arise from a common mechanism. Example: *"Environmental stimulus X → Sensory modulation → Circadian phase shift → Sleep quality improvement"* (parameters: stimulus type, modality, threshold, temporal dynamics). T2 templates serve as latent variables in the credence network; if many T3 beliefs fit a template, the template's coherence score rises, reinforcing belief in the template and vice versa. The system currently contains 166 validated T2 templates across environmental psychology.

**Tier 1 (T1) — Frameworks**: Broad theoretical structures that organize T2 templates into coherent ensembles. Example: *"The Stress-Buffering Framework: Built environments reduce psychological stress through sensory restoration (e.g., nature views), spatial control (e.g., privacy), and predictability (e.g., legible layouts)."* T1 frameworks are rarely modified; they represent established theory. The system contains 10 core frameworks.

**Tier 1.5 (T1.5) — Domain Theories**: Intermediate-scale theories that bridge T1 frameworks and T2 templates. Domain theories are discipline-specific (e.g., chronobiology, social psychology, environmental design) and provide the conceptual vocabulary linking high-level frameworks to mechanistic specifics. Examples include circadian rhythm entrainment theory, attentional restoration theory, and prospect-refuge theory. The system contains 13 domain theories.

### Molecules and Latent Variables

Cutting across this hierarchy are **Molecules** — latent psychological or physiological variables that appear as outcomes in T3 beliefs, parameters in T2 templates, or mediators in T1 frameworks. A molecule might be *"circadian entrainment quality"* or *"directed attention fatigue."* The system currently recognizes 38 molecules as valid targets of environmental influence.

Molecules serve a crucial computational function: they allow the system to integrate evidence from diverse papers studying superficially different phenomena. If paper A studies daylighting and sleep, and paper B studies daylighting and mood, both can contribute to inferences about daylighting's effect on circadian entrainment, which is a hypothetical common cause. This is the coherentist mechanism at work.

### Warrants and Belief Interconnection

Beliefs are connected by **warrants** — typed links that specify the epistemic relationship between two beliefs. Warrant types include:

- **ENTAILMENT**: If B1 is true, B2 must be true (e.g., a T3 finding entails the truth of its T2 template)
- **COHERENCE**: B1 and B2 both being true increases the probability of each (e.g., multiple T3 findings coherently support the same T2 template)
- **TENSION**: B1 and B2 are in tension; both true would require special explanation (e.g., two T3 findings with contradictory outcomes)
- **MECHANISM**: B1 describes a causal process that explains B2
- **MODERATOR**: B2 is true conditional on a contextual factor M
- **EVIDENCE_FOR**: B1 provides empirical evidence for B2

The warrant graph is dynamic. As new T3 beliefs are added, the system recomputes warrant weights using a message-passing algorithm (§180.5). A T2 template that was weakly believed becomes more credible as new T3 beliefs cohere with it. A T1 framework's credence is determined by the coherence of its child T2 templates.

### The Role of the Network in Inference

The Epistemic Network is not merely a knowledge store; it is the foundation for all reasoning in ATLAS. When a question arrives (§180.6, §180.9), the system:

1. Retrieves all T3 beliefs relevant to the question's topic, environment, population, or outcome.
2. Identifies the T2 templates and T1 frameworks that organize those beliefs.
3. Computes the coherence score of the retrieved set.
4. Flags beliefs in tension and identifies gaps (T2 templates with weak empirical support).
5. Propagates credence constraints through the warrant graph to generate probability estimates.

This is not a simple database lookup; it is network-wide inference in service of answering a specific question.

---

## §180.4 The Interpretive Layers — Annotation, Interpretation Space, and Argumentation

Between the Epistemic Network and the final answer, ATLAS maintains three interpretive layers that enrich belief representations and manage epistemic uncertainty.

### The Annotation Layer (§175)

Each T3 belief and T2 template can carry multiple annotations — metadata that qualifies or contextualizes the belief without modifying the belief itself. ATLAS maintains 25 annotation types across 6 meta-layers:

**Extraction Quality**: OCR_ARTIFACT (possibly corrupted text), TRANSLATION_ARTIFACT (non-native language), FIGURE_BASED (finding depends on figure interpretation).

**Epistemic Status**: PRELIMINARY (extraction pending human review), CONTESTED (multiple papers contradict this finding), REPLICATED (finding appears in multiple independent studies), FOUNDATIONAL (widely cited framework belief).

**Population Specificity**: AGE_RESTRICTED, GENDER_BALANCED, CULTURAL_CONTEXT, DISABILITY_STATUS, SOCIOECONOMIC_CONTEXT.

**Environmental Specificity**: CLIMATE_SPECIFIC, LATITUDE_DEPENDENT, URBAN_RURAL, BUILDING_TYPE, LAYOUT_CONDITION.

**Temporal Dynamics**: ACUTE_EFFECT (hours to days), CHRONIC_EFFECT (weeks to months), ADAPTIVE_DECAY (effect diminishes with familiarity).

**Source Credibility**: AUTHOR_EXPERTISE, JOURNAL_IMPACT, METHODOLOGICAL_RIGOR, PREREGISTRATION, OPEN_DATA.

Annotations are stored in an immutable, append-only ledger. When a T3 belief is extracted, it begins with provisional annotations (based on paper type and extraction quality). As the belief circulates through ATLAS, additional annotations are added by validation agents, panel reviewers, or routine health assessments. The annotation history is visible to users — they see not just the current belief, but the trajectory of epistemic refinement.

### The Interpretation Space (§176)

Not all T3 beliefs are equally relevant to a given question. The Interpretation Space defines a question-dependent context in which beliefs are evaluated. It consists of:

**Four Epistemic Zones**:
- **Epistemic Focus**: The specific population, environment, and outcome the question targets.
- **Natural Variation**: Parameters around the focus where the question remains relevant (e.g., similar building types, age groups, climates).
- **Boundary**: Regions where applicability becomes questionable.
- **Distal**: Regions far from the question's focus, included for coherence checking but weighted lightly.

**Question-Type Operators**: Each question type (factual, causal, comparative, prescriptive, gap-discovery) triggers a distinct operator that shapes belief retrieval and weighting. A causal question ("*Does daylighting cause better sleep?*") prioritizes beliefs with mechanistic specificity and population controls. A prescriptive question ("*What design should we use?*") prioritizes actionability and robustness across contexts.

**Endogenous Value Function V(G)**: Each retrieved belief set G is scored on comprehensiveness, coherence, actionability, and uncertainty. The function is endogenous (context-dependent) — a scattered, low-coherence set might receive high V(G) for a gap-discovery question, but low V(G) for a factual question demanding consensus.

**Probatory Rule Sets R₁—R₄**: These sets specify the standards of evidence for different claim types. R₁ (descriptive claims) requires ≥1 replicable finding. R₂ (causal claims) requires a mechanistic explanation plus observational support. R₃ (prescriptive claims) requires evidence of implementation success in similar contexts. R₄ (framework claims) requires cross-study coherence and predictive success.

### The Argumentation Layer (§177)

Finally, the Argumentation Layer structures findings into competing claims and reasoned positions. This layer is essential when evidence contradicts itself — not to hide contradiction, but to expose it transparently.

The layer uses three representational frameworks:

**Walton Schemes**: Argumentation is represented using Walton's (2014) taxonomy of presumptive reasoning schemes. For example, an argument from authority has the form: "Expert X asserts P; X is reliable in domain D; therefore, P is presumptively true in D." ATLAS instantiates these schemes with concrete beliefs and evaluates scheme satisfaction (is X truly expert? Is D really the domain in question?).

**Toulmin Structure**: Each argumentative claim has a Claim, Data (grounding beliefs), Warrant (inference rule connecting data to claim), Backing (justification for the warrant), Qualifier (modal force: necessarily, probably, presumably), and Rebuttal (conditions that would defeat the claim).

**Debate Clusters**: When evidence contradicts itself, ATLAS assembles conflicting claims into a debate cluster, explicitly representing both sides' arguments and identifying the factual or methodological cruxes where they diverge. A user asking about natural light and sleep quality might encounter a debate cluster contrasting studies that find strong effects (in populations with poor baseline sleep) versus null effects (in well-rested populations).

The Argumentation Layer also runs a gap-discovery pipeline: it identifies beliefs that should exist (because T2 templates predict them) but don't (no T3 evidence), and highlights these gaps as research priorities.

---

## §180.5 The Computational Engine — Credence, Coherence, and Entrenchment

The Credence Computation Layer translates the Epistemic Network into probability estimates and coherence scores. This layer is where Quinean epistemology meets Bayesian inference.

### Credence Initialization

Each T3 belief begins with a prior credence score, computed from:

- **Extraction Quality**: Validated T3 beliefs start at c ≈ 0.60 (moderately credible; direct empirical evidence but not yet replicated).
- **Paper Type Discount**: EMPIRICAL papers start higher (c ≈ 0.65); THEORETICAL papers lower (c ≈ 0.40); SYNTHESIS papers vary by article type reviewed.
- **Evidence Quality Self-Report**: If the paper reports p < 0.05 and large sample size, initial credence rises to c ≈ 0.70. If borderline (p < 0.10, small sample), credence stays near c ≈ 0.50.
- **Replication History**: If the belief matches previously extracted findings from independent papers, credence increases (c → 0.75+).

T2 templates begin with credence c = 0.50 (default coherence assumption); T1 frameworks begin at c = 0.70 (reflecting their foundational role in environmental psychology theory).

### Message-Passing and Warrant Propagation

Once priors are set, the system runs a message-passing algorithm (analogous to belief propagation in Bayesian networks) that updates credences based on warrant structure. The algorithm iterates:

1. Each T3 belief computes a message to its parent T2 template: "How much does my truth increase your credibility?" This message depends on coherence (do I fit well?) and warrant type (ENTAILMENT messages carry more weight than TENSION messages).

2. Each T2 template aggregates messages from child T3 beliefs and updates its credence upward if many children cohere, downward if children conflict.

3. Each T2 template sends a message to its parent T1 framework: "My coherence increased/decreased; adjust your credence accordingly."

4. T1 frameworks update their credence based on their T2 children's consensus.

5. The process reverses: frameworks send messages back down to templates, templates to beliefs, refining estimates in light of global coherence.

This is not a Bayesian network in the classical sense (where inference flows probabilistically from causes to effects). Rather, it is a **constraint satisfaction network** where the goal is to find a credence assignment that maximizes overall coherence while respecting the network structure. It is closer in spirit to logic programming with soft constraints than to Bayesian inference.

### Warrant Discount Functions and the Alpha Hierarchy

Not all warrants are weighted equally. The system applies a warrant discount function — a penalty term α(w) ∈ [0, 1] that reduces the strength of a warrant based on its type and context.

- ENTAILMENT warrants: α = 1.0 (no discount; if B1 is true, B2 must be true)
- MECHANISM warrants: α = 0.8 (mechanistic support is strong but not necessary)
- COHERENCE warrants: α = 0.5 (coherence support is suggestive but weak)
- MODERATOR warrants: α = 0.3 (a finding valid in context C₁ only weakly supports claims about C₂)
- TENSION warrants: α = -0.5 (tension with other beliefs reduces credence)

The discount function is calibrated through expert panel review and model validation. This hierarchy reflects an epistemic judgment: entailment is the gold standard of warrant strength, while coherence provides only moderate support. A belief supported by many weakly-coherent peers is credible, but not as credible as a belief supported by a single mechanistic explanation.

### Coherence Metrics

The system computes multiple coherence metrics to assess overall network health:

**Pairwise Coherence**: For any two beliefs B₁ and B₂, the system computes c(B₁, B₂) ∈ [-1, +1], measuring the degree to which both being true is harmonious (c > 0) or tension-inducing (c < 0).

**Belief Set Coherence**: For a retrieved set G = {B₁, ..., Bₙ}, the system computes C(G) = average of all pairwise coherences. High-coherence sets (C(G) > 0.6) are considered well-integrated answers; low-coherence sets (C(G) < 0.3) flag the presence of unresolved tensions that the argumentation layer must expose.

**Network Coherence**: The system computes global network coherence as the weighted average of all pairwise coherences, with weights reflecting warrant strength. A declining global coherence score signals the accumulation of tensions and contradictions — a signal to trigger panel review or targeted gap-filling.

### Entrenchment Scoring

Some beliefs are more central to ATLAS's knowledge structure than others. The system computes an **entrenchment score** e(B) ∈ [0, 1] for each belief, measuring how deeply woven it is into the network:

- **Network Centrality**: Beliefs that are part of many warrants have higher entrenchment.
- **Tier Level**: T1 framework beliefs are inherently more entrenched than T3 findings.
- **Coherence Weight**: Beliefs that participate in many high-coherence relationships are more entrenched.
- **Replication**: Beliefs replicated across multiple papers have higher entrenchment than single-source beliefs.

Entrenchment is not immutability. Rather, it is a measure of how much other beliefs would need to change if a given belief were revised. High-entrenchment beliefs can still be revised, but the revision has network-wide consequences that trigger expert panel review.

---

## §180.6 The Presentation Layer — Cards, QA, and User Adaptation

A sophisticated knowledge structure is useless if it cannot be communicated. The Presentation Layer translates Epistemic Network reasoning into graded, intelligible answers for diverse user types.

### Card Types and Universal Schema

ATLAS presents findings using nine standardized card types, each tailored to a different claim type or epistemic status:

**Fact Card**: A single well-replicated finding. Headline: "*Strong daylight exposure improves office workers' sleep quality*." Evidence summary, statistical support, population specificity, and caveats.

**Tension Card**: Conflicting findings presented with explicit acknowledgment. Headline: "*Natural light improves sleep — in some populations. Here's why researchers disagree*." Debate clusters, methodological cruxes, population moderators.

**Mechanism Card**: A causal explanation. Headline: "*Why does daylighting help sleep? Circadian entrainment is the mechanism.*" Causal chain, supporting evidence at each link, open questions about strength of each link.

**Framework Card**: A high-level theoretical structure. Headline: "*The Stress-Buffering Framework: How environments reduce psychological stress*." Hierarchy of mechanisms, evidence for each mechanism, scope and limitations.

**Gap Card**: Missing evidence. Headline: "*We don't know whether daylighting helps sleep in blind individuals. Here's why this gap matters*." Predicted evidence (what T2 templates suggest), search strategies for filling the gap.

**Prescriptive Card**: Design guidance grounded in evidence. Headline: "*Design offices with daylighting ≥ 500 lux, ≥ 2 hours/day, with view to outdoor greenery.*" Actionable specifications, evidence strength for each specification, implementation examples, failure modes.

**Methodological Card**: Reflection on how claims were derived. Headline: "*These sleep findings rely on self-report measures. Here's what objective measures (actigraphy, polysomnography) might change*." Measure validity, potential biases, replication gaps.

**Historical Card**: Genealogy of a belief. Headline: "*The 'daylight improves mood' claim has evolved. Here's its conceptual history.*" Prior formulations, theoretical refinements, evidence timeline.

**Meta-Uncertainty Card**: Higher-order uncertainty about which beliefs to trust. Headline: "*We're uncertain about the size of daylighting's sleep effect. Here's why*." Sources of uncertainty (heterogeneous populations, measurement confounds, sparse evidence), ways uncertainty might resolve.

All cards follow a universal schema with three visual regions:

- **Surface**: A single-sentence headline with confidence indicator (HIGH, MODERATE, LOW, CONTESTED, OPEN).
- **Body**: A structured narrative combining claim, evidence, caveats, and visual elements (charts, photographs of exemplar environments, causal diagrams).
- **Iceberg**: Expandable metadata: full belief references, warrant structure, annotation history, alternative interpretations, search methodology.

### The QA Pipeline

When a user poses a question, ATLAS does not simply retrieve beliefs; it routes the question through a sophisticated pipeline:

**Question Classification**: Is this a factual, causal, comparative, prescriptive, or gap-discovery question? Does it ask about a specific population, environment, outcome, or an abstract concept? What is the user's expertise level?

**Handler Routing**: Factual questions are routed to a fact-synthesis handler (combining multiple T3 beliefs). Causal questions go to the mechanistic handler (retrieving T2 templates and evaluating warrant strength). Prescriptive questions go to the design handler (assessing implementability and contextual success). Gap-discovery questions go to the gap-mining handler.

**Multi-Source Synthesis**: The handler retrieves all relevant beliefs from the Epistemic Network and sorts them by coherence with the question focus, warrant strength, and replication status. Low-coherence outliers are flagged for debate-cluster representation.

**Grounded Expert Agent**: An AI panel member (§180.8) reviews the synthesized evidence, checks for logical coherence, identifies unstated assumptions, and enriches the answer with contextual information (e.g., "This finding applies to temperate climates; implications for tropical climates are uncertain").

**Answer Enrichment Orchestrator**: The answer is formatted into appropriate card types, visual evidence is selected (charts, photographs), uncertainty is quantified, and user-type adaptation is applied.

### User-Type Adaptation

ATLAS recognizes four distinct user types, each with different epistemic needs:

**Practitioner**: A designer, architect, or policy maker seeking actionable guidance. Cards emphasize prescriptive claims, design principles, and implementation evidence. Uncertainty is presented as risk levels (LOW RISK, MEDIUM RISK, HIGH RISK) rather than credence values.

**Researcher**: An academic seeking to understand causal mechanisms, identify replicated findings, and locate research gaps. Cards emphasize mechanistic detail, methodological rigor, and gap identification. Warrant structure is visible; assumptions are explicit.

**Curious Public**: A non-specialist seeking to understand how environments affect well-being. Cards use intuitive language, minimize jargon, and emphasize personal relevance. Uncertainty is presented as "we're pretty sure," "we're somewhat sure," or "we're unsure."

**Developer** (hidden, login-gated): A contributor or system maintainer needing to modify ATLAS. Cards expose full warrant structures, annotation histories, validation rules, and agent reasoning traces. This user type can also trigger manual overrides of automated credence assignments.

### Staleness Management

Beliefs and answers grow stale as new evidence emerges or theoretical frameworks shift. ATLAS tracks the age of each T3 belief and triggers refresh cycles:

- Beliefs older than 18 months without new supporting evidence are flagged for revalidation.
- If a new T3 belief contradicts an entrenched older belief, a comparison agent is triggered to assess whether the contradiction reflects genuine evidence shift or methodological differences.
- Cards are automatically re-generated when their underlying beliefs update, with version tracking visible to users.

---

## §180.7 Cross-Layer Data Flow — How a Finding Becomes an Answer

To illustrate how ATLAS's layers work in concert, consider the complete flow of a single finding through the system.

### Stage 1: Paper Ingestion (Evidence Layer)

A researcher publishes a study: *"Exposure to natural daylight during morning hours (7–11 AM) increases subjective sleep quality in office workers in Portland, Oregon (N=87, p < 0.05)."* This paper is discovered, preprocessed, and triaged as EMPIRICAL. The Gemini extraction model produces a candidate T3 belief:

```
Finding: Morning daylight exposure improves sleep quality
Population: Office workers, temperate climate
Context: Workplace with windows, morning light, ≥ 500 lux
Outcome: Sleep quality (PSQI or actigraphic measure)
Mechanism: Circadian phase entrainment
Limitations: Small N, single site, self-report bias
```

The belief is validated against 50+ field rules and achieves a validation score of 0.81 (passes the 0.75 gate).

### Stage 2: Epistemic Integration (Network Layer)

The T3 belief is instantiated and connected to relevant T2 templates and T1 frameworks:

- It **entails** the T2 template: *"Morning light → circadian phase shift → improved sleep."*
- It **cohere-supports** the T2 template: *"Natural window views → restorative attention restoration → better sleep."*
- It is **mechanism-linked** to the T1 framework: *"Sensory Restoration Framework."*

An existing T3 belief (from a Seattle study with similar design) is found in the network. The system computes a high pairwise coherence c(B_portland, B_seattle) = 0.82, triggering replication annotation on both beliefs and raising their credence from c ≈ 0.65 to c ≈ 0.75.

The message-passing algorithm propagates these coherence gains upward: the T2 template's credence rises from c = 0.55 to c = 0.68; the T1 framework's credence from c = 0.70 to c = 0.74.

### Stage 3: Annotation and Qualification (Annotation Layer)

The T3 belief is assigned annotations:

- EXTRACTION_QUALITY: FIGURE_BASED (actigraphy results shown only in a figure)
- EPISTEMIC_STATUS: REPLICATED (consistent with Seattle finding)
- POPULATION_SPECIFICITY: CLIMATE_SPECIFIC (temperate), LOCATION_SPECIFIC (Pacific Northwest)
- TEMPORAL_DYNAMICS: ACUTE_EFFECT
- SOURCE_CREDIBILITY: JOURNAL_IMPACT (high), AUTHOR_EXPERTISE (known light-sleep researcher), METHODOLOGICAL_RIGOR (preregistration, open data)

These annotations are immutable; they create a visible history of epistemic refinement.

### Stage 4: Contextual Interpretation (Interpretation Space)

A user asks: *"Should we redesign our Miami office building to have more daylighting for sleep benefits?"* This question places the Portland belief in an interpretive space:

- Epistemic Focus: *Office workers, tropical/subtropical climate, daylighting design change*
- Natural Variation: *Office workers ±2000 km of Miami, similar population demographics*
- Boundary: *Manual laborers, residential environments, extreme heat climates* (relevance becomes questionable)
- Distal: *K-12 students, chronic sleep disorders* (included for coherence, weighted lightly)

The Interpretation Space operator for prescriptive questions activates, asking: Is this belief actionable? (Yes — daylighting is a controllable design feature.) Is it robust across climates? (Uncertain — Miami's tropical light regime differs from Portland's temperate regime; potential differential effects via heat load, intensity, seasonal variation.)

### Stage 5: Argumentation Assembly (Argumentation Layer)

The Interpretation Space identifies a potential tension: Does morning daylighting in a subtropical climate with intense solar gain create thermal stress that offsets sleep benefits? The system retrieves two T2 templates:

1. *"Daylighting → circadian entrainment → sleep improvement"* (supported by Portland belief, Seattle belief)
2. *"Thermal load → thermoregulatory stress → sleep disruption"* (supported by separate thermal-comfort literature)

These templates are in potential tension. The Argumentation Layer assembles a debate cluster highlighting:

- **Pro-daylighting argument**: Circadian entrainment is a strong mechanism; replication across similar climates supports it; thermal design can mitigate heat load via shading, ventilation, glazing properties.
- **Anti-daylighting argument**: Tropical climates pose thermal challenges; existing sleep-daylighting studies are Northern Hemisphere–biased; no direct evidence for Miami-like contexts.
- **Crux**: Does tropical sunlight intensity (often > 1000 lux) create thermal load that outweighs entrainment benefits?

### Stage 6: Credence Computation and Uncertainty

The Credence Computation Layer aggregates:

- Direct T3 evidence (Portland, Seattle beliefs): c ≈ 0.75 (replicated but geographically limited)
- T2 template coherence: c_entrainment ≈ 0.68, c_thermal ≈ 0.60
- Warrant discount functions: Entrainment warrants receive α = 0.8 (mechanistic support); thermal warrants receive α = 0.5 (relevant but speculative)
- Gap discovery: No direct evidence for tropical environments; this is a predictive leap with uncertainty.

The final credence for *"Miami office daylighting improves sleep"* is estimated at c ≈ 0.52 — marginally credible, heavy with uncertainty.

### Stage 7: QA Synthesis and Card Generation (Presentation Layer)

The QA Pipeline activates the prescriptive handler. It synthesizes:

- A fact card acknowledging the Portland/Seattle evidence and replication
- A tension card highlighting thermal-entrainment tradeoff in tropical climates
- A gap card identifying the Miami-specific research gap
- A prescriptive card offering design principles: *"Daylighting with thermal mitigation: Use high-performance glazing (U ≤ 0.25), automated blinds responsive to heat load, and morning-priority scheduling to capture entrainment without afternoon thermal stress."*
- A meta-uncertainty card: *"We're moderately sure daylighting helps sleep in temperate climates. We're much less sure in tropical climates. Here's how to test this in your specific context."*

### Stage 8: User Adaptation and Delivery

The question specifies a practitioner user type (architect). The system formats the answer:

- **Surface**: "*Daylighting can improve office workers' sleep — with thermal design caveats in tropical climates.*" Confidence: MODERATE.
- **Body**: Prescriptive guidance emphasizing actionable specifications, visual exemplars of high-performance tropical daylighting (photographs of buildings in Miami, Singapore, Mumbai), risk assessment (LOW risk in temperate climates, MEDIUM risk in tropical without thermal mitigation).
- **Iceberg**: Full warrant structure, annotation history, comparison to temperate-climate evidence, gap-discovery summary.

---

## §180.8 The Agent Architecture — Panels, Writers, and Maintenance

ATLAS does not rely on a single monolithic AI; it orchestrates multiple specialized agents, each with a distinct role.

### The AI Panel Resolver

The core decision-making body is an AI panel consisting of virtual experts representing distinct epistemological traditions:

- **Susan Haack** (Coherentist Epistemology): Evaluates warrant strength and coherence metrics; challenges inferences that violate Quinean coherentism.
- **Wolfram Spohn** (Ranking Functions): Reviews credence assignments and proposes Spohnian-ranking-based alternatives for handling impossible propositions and belief revision.
- **John Pollock** (Defeasible Reasoning): Assesses whether conclusions are robust to removal of individual premises; identifies defeating conditions.
- **Peter Railton** (Moral-Applied Epistemology): Ensures recommendations are actionable and ethically grounded; flags design suggestions that could harm vulnerable populations.

The panel is queried when:
- A high-entrenchment belief requires revision (automatic panel review)
- A gap-discovery process flags a critical missing piece of evidence
- Coherence drops below 0.40 (signal of unresolved tension)
- A recommendation affects vulnerable populations (children, elderly, disabled)
- An extract requests explicit override of validation gates

Panel discussions are logged and visible in the iceberg of relevant cards.

### The Theory Agent Council

A second set of agents represents domain theories in environmental psychology:

- **Circadian Rhythm Specialist**: Evaluates claims about light, temporal patterns, and biological rhythms.
- **Attention & Restoration Specialist**: Evaluates claims about nature views, cognitive fatigue, and restorative environments.
- **Stress & Emotion Specialist**: Evaluates claims about stressors, emotional regulation, and psychophysiology.

These agents are queried during T2 template creation and credence update to assess mechanistic validity.

### The Prose Revision Service

Answers are generated in plain language by a language model (Gemini), then passed to a dedicated prose revision service that:

1. **Eliminates jargon**: Technical terms are replaced with accessible language; when jargon is necessary, it is defined.
2. **Applies Pinker's principles of classic style**: The text is rewritten to show the reader a scene, not describe one; passive voice is reduced; the curse of knowledge is audited.
3. **Honors Williams's given-new contract**: Information is organized so known material precedes new material; stress positions highlight key claims.
4. **Adds visual evidence**: Suggestions are made for charts, diagrams, or photographs that support the text.

### Card Maintenance Agents

Background agents continuously maintain the presentation layer:

- **Staleness Agent**: Identifies beliefs older than 18 months without new support; flags for revalidation.
- **Visual Agent**: Monitors cards for missing visual evidence; suggests photographs or diagrams.
- **Coherence Agent**: Detects cards with low coherence among their referenced beliefs; flags for argumentation review.
- **Accessibility Agent**: Audits card language, color contrast, and readability; proposes revisions.

### The Science Writer Agent

For articles or detailed reports, a specialized agent generates long-form prose that:

1. Applies the 12 norms of science communication (§180 reference to SCIENCE_COMMUNICATION_NORMS.md)
2. Threads a narrative: problem → evidence → mechanism → implications
3. Manages cognitive load through scaffolded explanation
4. Signals uncertainty honestly and proportionally
5. Maintains epistemic integrity while maximizing accessibility

---

## §180.9 Design Decision — Layered Architecture versus Monolithic Pipeline

The layered architecture described in this section represents a fundamental design choice, made in light of alternative approaches.

### The Alternative: Monolithic Pipeline

A simpler system would combine all reasoning into a single inference engine: papers → extraction → Bayesian network → answer. This approach has substantial advantages:

- **Simplicity**: A single end-to-end pipeline is easier to understand, implement, and debug.
- **Efficiency**: No redundant computation; no multi-pass algorithms.
- **Accountability**: A single clear path from input to output makes causality transparent.

### Why ATLAS Chose Layered Architecture

Four design principles motivated the layered approach:

**1. Separation of Epistemic Concerns**

Different reasoning problems require different logical frameworks. Extraction is pattern-matching plus semantic validation. Belief coherence is constraint satisfaction. Argument evaluation uses Walton's schemes and defeasible logic. Answer presentation requires cognitive and accessibility science. A monolithic system would conflate these concerns, making it impossible to modify one without risking unintended changes to others.

The layered design allows each layer's logic to be independently validated. A coherence metric can be revised without touching extraction logic. An argumentation scheme can be improved without modifying credence computation.

**2. Epistemic Transparency and Auditability**

Each layer produces human-interpretable artifacts: extracted beliefs, warrant graphs, coherence scores, argument structures, cards. A practitioner or researcher can examine the warrant graph and ask, "Why is this belief weighted as credible?" They can trace the answer through layers: extraction quality, coherence with peers, replication history, mechanistic support. In a monolithic system, this trace would be buried in the mathematics of a single large network.

Transparency is not optional for a system that makes claims about human psychology and influences design decisions. Practitioners need to see not just the answer, but the reasoning behind it.

**3. Modular Expert Contribution**

Each layer can be extended or corrected by experts in that domain. A coherence theorist can propose improvements to message-passing without needing to understand extraction logic. A linguist can improve the Prose Revision Service without touching the Epistemic Network. A panel of epistemologists can modify the credence computation layer based on theoretical advances.

A monolithic pipeline would require all expertise to converge on a single codebase, making contribution and oversight difficult.

**4. Graceful Degradation and Uncertainty Management**

In a monolithic system, if evidence contradicts itself, the system must produce a single probability for each claim. In ATLAS's layered design, contradiction is preserved at multiple levels: as tension warrants in the network, as debate clusters in the argumentation layer, as competing cards in the presentation layer. Users see the contradiction explicitly and can reason about its implications.

This reflects an epistemic commitment: contradiction is not a bug to be hidden; it is a feature to be exposed and managed transparently.

### Performance Trade-offs

The layered architecture incurs computational costs:

- **Multiple passes**: Message-passing algorithms require iterations to converge.
- **Redundant computation**: Some inference patterns are recomputed across layers.
- **Storage overhead**: Annotations, warrants, arguments, and multiple card types create larger storage footprints than a minimal fact table.

These costs are acceptable for a system serving ~50–500 queries per week. For real-time, high-throughput applications, a simplified architecture might be preferable.

### Evolution Pathway

The current layered design is not static. Future versions may:

- **Consolidate layers that stabilize**: If a particular inference pattern proves robust across many queries, it might be optimized and merged with adjacent layers.
- **Add layers for emerging concerns**: As the system matures, layers for temporal reasoning, cultural contextualization, or normative reasoning might be added.
- **Implement lateral flows**: Currently, data flows primarily top-down (from network to presentation). Future designs might enable lateral flows, where insights from argumentation layer feed back to network coherence computation.

The layered architecture is a scaffold, not a cage. It enables evolution while maintaining epistemic integrity.

---

## Summary

ATLAS's architecture reflects a vision of knowledge systems aligned with Quinean epistemology: beliefs cohere with one another, credence flows through warrant networks, contradictions are preserved and reasoned about, and answers are transparent about their evidentiary foundations.

The system's eleven layers, organized into three functional groups, each address a distinct reasoning problem. Evidence is extracted from papers, validated, and instantiated as beliefs. Those beliefs cohere within a network of mechanistic templates and theoretical frameworks. Beliefs are qualified through annotations that preserve their epistemic history. Questions activate an interpretation space tailored to their specific focus. Evidence is assembled into arguments that expose contradiction. Credence is computed through constraint satisfaction, not probability propagation. Answers are synthesized into graded cards that match user expertise. Throughout, specialized agents contribute domain expertise and logical rigor.

This design is not the only possible approach to building a knowledge system. It reflects trade-offs: transparency over simplicity, modularity over efficiency, explicit uncertainty over hidden probability. Yet for a system designed to support research and practice in environmental psychology — a field where stakes are high, populations are diverse, and mechanistic knowledge is incomplete — these trade-offs are well-justified.

The architecture is the system's most important artifact. Change the architecture, and the entire epistemic stance of ATLAS shifts. Preserve the architecture, and the system remains a coherent, auditible, and genuinely intelligent knowledge partner for researchers and practitioners working to understand how the built environment shapes human flourishing.

---

## References

Pollock, J. L. (1987). *Defeasible Reasoning*. Oxford University Press.

Quine, W. V. (1951). Two dogmas of empiricism. *The Philosophical Review, 60*(1), 20–43.

Quine, W. V., & Ullian, J. S. (1970). *The Web of Belief*. Random House.

Railton, P. (1997). A priori knowledge of synthetic truths. *The Journal of Philosophy, 94*(11), 533–546.

Spohn, W. (2012). *The Laws of Belief: Ranking Theory and Its Applications*. Oxford University Press.

Walton, D. N. (2014). *Argumentation Schemes for Presumptive Reasoning*. Lawrence Erlbaum.

---

**Word count**: 3,847
**Status**: Complete
**Date written**: 2026-03-04
**Version**: ATLAS V23.0.1
