# PART XXVI: System Presentation and Knowledge Artifacts

**Last updated:** 4 March 2026
**Section numbers:** §174–§180
**Word count:** ~22,000 (across main file + section files)

---

## §174. The 18 Molecules — Latent Variables in the ATLAS Web

### §174.1 What Molecules Are and Why They Matter

In the vocabulary of classical factor analysis, a latent variable is a construct that cannot be observed directly but is inferred from patterns in observed data—a dimension of variation that emerges from covariation among measured variables (Borsboom, Mellenbergh, & van Heuven, 2003). The ATLAS system employs a mathematically and epistemologically homologous approach at the level of mechanistic templates. Molecules are latent variables discovered through co-activation patterns in the 166 Tier 2 templates that themselves specify environmental-to-psychological pathways. They are not stipulated a priori by investigator intuition. They are mined from the correlational structure of template employment: which templates do cognitive scientists and environmental psychologists invoke together when explaining the same environmental phenomena? When the same human psychological outcome is traced back through different empirical studies and literatures, do the same clusters of templates recur?

This methodological commitment to discovering rather than stipulating organizational units reflects a fundamental epistemic choice: to respect the structure of the data—the actual patterns of co-occurrence in scientific practice—rather than to impose the theoretician's preferred categories. As Donald Cunningham and Byron Yu have demonstrated in the context of latent variable modeling in computational neuroscience, latent variables discovered through unsupervised learning often reveal structure that manual taxonomy misses (Cunningham & Yu, 2014). The brain does not compartmentalize its computations according to anatomical labels invented by neuroscientists; it organizes according to functional principles that may cut across traditional boundaries. Similarly, the psychological and environmental design literatures do not organize themselves according to pre-existing theoretical categories. They self-organize through citation networks, empirical replication, and mechanistic convergence. Molecules capture that self-organization.

The justification for introducing molecules between Tier 1 frameworks and Tier 2 templates rests on three converging arguments. *First, the completeness argument*: a T1 framework like predictive processing is vast enough to encompass hundreds of specific template instantiations. Not all of these templates co-occur with equal probability. Some clusters of templates arise together reliably enough that they merit recognition as named entities—searchable, communicable, and functionally coherent units. Naming them serves the same function that naming subfields serves in physics: it accelerates communication and focuses experimental effort. *Second, the compositionality argument*: many environmental design outcomes are better explained as products of multiple templates interacting in specific patterns than as applications of single templates. Attention Restoration Theory (ART), for instance, is not reducible to any single template specifying soft fascination, or to being away, or to extent alone. Its explanatory power lies in the synergistic interaction of these components. Molecules make this compositionality explicit and queryable. *Third, the empirical-web argument*: Quine's web of belief teaches that empirical support flows horizontally through networks of interconnected claims rather than vertically from observation to theory (Quine & Ullian, 1978). A belief about the restorative power of natural scenes is not isolated; it sits within a web of commitments about attention, processing fluency, stress physiology, and memory. When scientists assert that natural environments restore depleted attention, they implicitly invoke this entire web. Molecules make the web structure visible and computable.

### §174.2 The Discovery Method: Factor Analysis on Template Co-Occurrence

The technical procedure for identifying molecules proceeds in three phases: aggregation, factor analysis, and interpretation.

In the *aggregation phase*, the system scans all 12,000+ Tier 3 empirical beliefs (individual claims extracted from the scientific literature) and records which T2 templates serve as their mechanistic justification. Each belief links to one or more templates via evidence linkage warrants. This creates a belief-by-template matrix M where rows are beliefs and columns are templates. Each cell M[i,j] is 1 if belief i invokes template j in its justification, and 0 otherwise. The matrix captures the empirical frequency with which templates co-occur as justifications for related claims.

In the *factor analysis phase*, the system performs dimensionality reduction on the belief-by-template matrix using standard factor extraction methods (e.g., principal components analysis with subsequent Promax rotation to permit correlated factors). This yields a smaller set of latent variables—each one a weighted linear combination of templates—such that the covariance structure among beliefs is preserved in the lower-dimensional factor space. Each latent variable accumulates templates that consistently co-vary: templates that appear together in multiple belief justifications receive positive weight; templates that rarely co-occur receive near-zero weight.

The *interpretation phase* examines each discovered latent variable—each factor—and asks: does this cluster of templates correspond to a recognizable psychological phenomenon, architectural mechanism, or design principle already named in the literature? For instance, if a factor loads heavily on templates specifying soft fascination, being away, environmental scope, and personal preference alignment, and if this factor reliably explains variance in restoration-related empirical beliefs, then it is reasonable to identify this factor with Attention Restoration Theory. The name ART already exists in psychology; the factor is a computational instantiation of that existing concept. Conversely, if a factor emerges that does not align with any named theory—say, a cluster of templates about temporal coherence monitoring, cross-modal prediction errors, and conflict signal generation—then the molecule is given a functional descriptor like "Coherence Monitoring Circuit" and treated as a newly discovered mechanism.

Two critical distinctions separate signal from noise. *Stability*: a molecule must be recoverable across multiple subsamples of the belief set. If a cluster of templates co-occurs in a single belief or in a handful of outlier claims but not consistently, it fails the stability criterion and is rejected. *Functional interpretability*: the templates in a molecule must form a mechanistically coherent unit. Random clusters of templates that happen to co-occur statistically but have no functional relationship are not named as molecules. The criterion is not merely statistical correlation but functional coherence—the templates must jointly specify a process or state that makes sense neurobiologically or psychologically.

### §174.3 The Current Inventory: 38 Molecules Across Four Types

The ATLAS system currently maintains 38 molecules distributed across four primary types: nine THEORY molecules, five MECHANISM molecules, two PHENOMENON molecules, two DESIGN_PATTERN molecules, and twenty FUNCTIONAL_CIRCUIT molecules. Understanding the current state of the system requires a tour through this inventory, organized by type and maturity.

**THEORY Molecules (9 total).** These are molecules that correspond to named, published domain theories—typically with identified historical authors and literatures supporting them. Six of the nine theory molecules are part of the formal T1.5 reduction set: Attention Restoration Theory (ART, Rachel and Stephen Kaplan; 10 constituent T2 templates, ESTABLISHED empirical support), Stress Recovery Theory (SRT, Roger Ulrich; 5 templates, ESTABLISHED support), Biophilia Hypothesis (E.O. Wilson; 5 templates, ESTABLISHED support), Prospect-Refuge Theory (Jay Appleton; 2 templates, MIXED support), Goldilocks Principle (historically attributed to Berlyne's Wundt curve and Kaplan's preference matrix, formalized by Kirsh; 16 templates, SUPPORTED/SUPPORTED), and Wayfinding Theory (space syntax, barrier cognition, landmark salience; 6 templates, SUPPORTED). Three additional theory molecules—Beauty as Compression (M_BEAUTY_COMPRESSION), Rasa Aesthetic States (M_RASA), and Attractor Transition Dynamics (M_ATTRACTOR_TRANSITION)—represent higher-order theoretical frameworks that cut across multiple domains and are derived from information-theoretic or classical aesthetic principles rather than from hypothesis-driven empirical psychology. These three are less established in empirical support but represent important theoretical bridges: Beauty as Compression draws on Schmidhuber's compression progress theory and processing fluency aesthetics; Rasa states formalize classical Indian aesthetic theory (Bharata's Natyashastra) as attractor configurations in the constraint-valuation-affect (CVA) state space; Attractor Transition Dynamics models phase transitions in aesthetic and affective states.

**MECHANISM Molecules (5 total).** These are clusters of templates that specify neurobiological or cognitive mechanisms rather than named domain theories. Allostatic Regulation (4 templates, TENTATIVE/SUPPORTED) captures the homeostatic-to-allostatic shift in regulatory physiology—how architectural features modulate the brain's baseline set-point and predictive load rather than reactive restoration. Circadian Architecture (3 templates, TENTATIVE/SUPPORTED) specifies the collection of light-timing templates that entrain circadian and circannual rhythms. Cognitive Load Architecture (5 templates, SUPPORTED/SUPPORTED) aggregates templates specifying how environmental complexity, information density, and cognitive demand interact to shift cognitive processing style. Multisensory Design (6 templates, TENTATIVE/PRELIMINARY) groups templates about cross-modal binding, temporal synchrony, and multisensory coherence. Wayfinding (6 templates, SUPPORTED/SUPPORTED)—though it appears in the theory category as well—also functions as a mechanism molecule capturing spatial cognition, landmark detection, and route memory formation.

**PHENOMENON Molecules (2 total).** These capture observable, measurable human responses to environment that emerge from multiple underlying mechanisms. Architectural Awe (10 templates, TENTATIVE/PRELIMINARY) specifies the phenomenon of awe elicitation through vast, sublime, or complex architectural spaces—involving vastness perception, small-self effects, attentional broadening, and prosocial behavioral shifts (Keltner & Haidt, 2003; Piff et al., 2015). Goldilocks Principle (16 templates, SUPPORTED/SUPPORTED) occupies an unusual position as both a theoretical framework and a phenomenon: it captures the empirical observation that preference follows an inverted-U curve across multiple modalities (visual complexity, thermal variation, acoustic intensity, social density, temporal variation, cognitive complexity), with an optimal point specific to each dimension and person.

**DESIGN_PATTERN Molecules (2 total).** These specify architectural or design solutions—recurring templates for creating particular environmental outcomes. Creative Environments (7 templates, TENTATIVE/PRELIMINARY) clusters templates about environmental novelty, diversity, reduced cognitive constraints, and reduced social/evaluative pressure that together promote creative problem-solving and divergent thinking. Social Architecture (6 templates, TENTATIVE/PRELIMINARY) aggregates templates specifying spatial configurations, visual fields, proximity patterns, and visual accessibility that support social interaction, group cohesion, and impression formation.

**FUNCTIONAL_CIRCUIT Molecules (20 total).** These represent the largest and most recent category of molecules—computational circuits that implement specific T2 archetypes and are hypothesized to have neurobiological instantiations in predictive processing, attention, affect regulation, and threat detection systems. All twenty functional circuits currently carry TENTATIVE maturity ratings and PRELIMINARY empirical support, reflecting their status as neurocomputational hypotheses rather than established psychological phenomena. The twenty functional circuits include: Action Selection (gating between competing behavioral options), Aesthetic Expectation Violation (detecting and evaluating deviations from aesthetic expectations), Affective Memory Gating (using emotional valence to modulate memory consolidation), Arousal Regulation (maintaining arousal in an optimal window), Attentional Selection (competitive selection among spatial and feature-based attention targets), Cognitive Load Regulation (monitoring working memory demand and triggering offloading strategies), Coherence Monitoring (cross-modal prediction error integration and conflict detection), Context-Gated Threat (threat detection modulated by contextual safety signals), Curiosity Accumulation (building intrinsic motivation through novel information discovery), Dread Accumulation (building aversive anticipation for avoided scenarios), Expertise-Gated Aesthetics (aesthetic preferences modulated by domain expertise and schema development), Familiarity Detection (fluency-based monitoring of schema match), Interpretive Selection (choosing among competing semantic/narrative interpretations), Reward Prediction Error (tracking unexpected positive outcomes), Sensory Prediction Error (tracking unexpected sensory surprises), Social Prediction Error (tracking unexpected social behavior), Social Safety Monitoring (detecting signals of social threat or safety), Thermoregulatory Affect (affective valence tied to thermal deviations from comfort), Threat Monitoring (vigilance and threat-related attention allocation), and Vitality Monitoring (monitoring the integrity and coherence of the self as a unified agent).

The distribution of molecules across these types reflects the maturity asymmetry in the system. The nine theory molecules correspond largely to published, peer-reviewed frameworks with decades of empirical support. The five mechanism molecules capture intermediate-level organization between frameworks and templates. The two phenomenon molecules describe observable effects that emerge from multiple mechanisms. The two design pattern molecules translate mechanism knowledge into actionable architectural guidance. The twenty functional circuits represent nascent neurocomputational hypotheses that require further empirical validation but offer mechanistic specificity at the template-architecture level.

### §174.4 Molecules vs. Tier 1.5 Theories: The Critical Distinction

A frequent source of confusion in the ATLAS architecture concerns the relationship between molecules and Tier 1.5 (T1.5) domain theories. It is essential to clarify this relationship, as it forms a critical architectural choice.

A molecule is a latent variable: a cluster of co-activated T2 templates discovered empirically from the structure of scientific belief networks. A T1.5 domain theory is a named, authored, historically situated theoretical framework that has been formally reduced to a specific subset of T1 frameworks and T2 templates with documented coverage fractions.

The key distinction is this: *not all molecules are T1.5 theories, but all T1.5 theories are molecules*. T1.5 is a strict subset of molecules.

The ATLAS system currently maintains thirteen T1.5 domain theories: Attention Restoration Theory, Stress Recovery Theory, Biophilia Hypothesis, Prospect-Refuge Theory, Privacy Regulation (Altman), Kaplan Preference Matrix, Adaptive Thermal Comfort (de Dear & Brager), Space Syntax (Hillier & Hanson), Soundscape Theory (Schäfer), Place Attachment (Scannell & Gifford), BRECVEMA Model (Juslin), Flow Theory (Csikszentmihalyi), and Goldilocks Principle (Berlyne/Kirsh). Each of these has been formally reduced to specific combinations of T1 frameworks, documented in a separate T1.5 registry, with coverage percentages showing what fraction of the theory's explanatory scope is captured by the T2 templates in its molecule.

The other twenty-five molecules in the system—including Allostatic Regulation, Circadian Architecture, Awe Architecture, the five mechanism clusters, the two design patterns, and all twenty functional circuits—are discovered latent variables that have not (yet) been reduced to T1.5 theories. They may be emerging scientific concepts like Awe Architecture (only recently formalized by Keltner, Haidt, and collaborators); they may be mechanisms lying beneath multiple T1.5 theories (like Multisensory Design, which is invoked by ART, SRT, and Biophilia simultaneously); they may be computational circuits hypothesized to implement T2 archetypes but not yet linked to named published theories.

This distinction matters operationally. When a user queries the ATLAS system about Attention Restoration Theory, the system returns not just the ART molecule but the full T1.5 reduction document for ART, which specifies (a) the historical provenance of ART (Kaplan & Kaplan, 1989), (b) the specific T1 frameworks from which ART is derived (primarily predictive processing and memory systems), (c) the T2 template coverage (10 of ~166 templates, ~6% coverage), (d) the irreducible residual—what aspects of ART's explanatory reach are not captured by the current T2 template set and hence point to missing templates or T1 framework extensions. Conversely, when a user queries Coherence Monitoring Circuit, the system returns the molecule definition, the constituent templates, and the neurocomputational interpretation, but not a T1.5 reduction document, because Coherence Monitoring Circuit has not been mapped to the formal T1 reduction hierarchy.

The existence of this distinction creates a productive asymmetry. It preserves the ATLAS system's fidelity to published, peer-reviewed domain theories (via the T1.5 tier) while allowing the system to grow beyond those theories by discovering new molecular structures in the template co-occurrence data. Over time, some of the currently non-T1.5 molecules may be elevated to T1.5 status when sufficient empirical evidence accumulates and theoretical convergence is achieved. Conversely, new T1.5 theories from the literature may be added to the system as they are formally reduced to T1 and T2 components.

### §174.5 Design Decision: Why Latent Variables (Not Clusters, Categories, or Stipulated Groupings)

The choice to model molecules as latent variables emerging from template co-occurrence patterns, rather than as pre-specified categories or clusters, reflects several methodological commitments worth making explicit.

*An alternative approach might be clustering.* One could apply k-means or hierarchical clustering to the template-by-belief matrix, assigning each template to a cluster based on similarity of co-occurrence patterns, and then name the clusters post-hoc. This approach has the virtue of simplicity and the vice of ignoring template centrality. In clustering, each template belongs fully to one cluster. But in latent variable modeling, templates can load onto multiple latent variables simultaneously with varying weights. Predictive processing templates, for instance, load heavily on Biophilia, Goldilocks Principle, and Coherence Monitoring simultaneously because these mechanisms all rest on predictive-error-reduction principles. Clustering would force an arbitrary choice about which molecule each template "belongs to." Latent variable modeling allows templates to participate in multiple molecules according to their actual role in the scientific literature.

*An alternative approach might be categorical taxonomy.* One could impose a hierarchical classification scheme—organizing molecules into bins like "restoration," "perception," "social," "thermal"—and assign molecules to bins a priori. This approach has the virtue of matching familiar category systems used in environmental psychology textbooks and the vice of imposing the theorist's categories rather than letting data speak. The latent variable approach is theory-light: it does not assume that the world divides into restoration, perception, social, and thermal domains. It discovers which organizational principles actually structure the scientific literature. If the data revealed that restoration effects always co-varied with social effects, the latent variables would reveal that structure rather than hiding it under separate categorical bins.

*An alternative approach might be expert stipulation.* One could convene a panel of domain experts—specialists in environmental psychology, neuroscience, and architecture—and ask them to propose a list of "core mechanisms" they believe underlie human response to environment. This approach has the virtue of leveraging expert intuition and the vice of circular reasoning: the list of mechanisms would reflect the biases, blind spots, and current consensus of the expert panel. It would miss mechanisms that are implicit in the scientific literature but not yet explicitly discussed by experts. Latent variable discovery respects the collective structure of science as it has been practiced, not the current consensus about what science ought to practice.

The epistemological principle underlying the latent variable choice is Quine's fallibilism: all theoretical commitments, including commitments about what constitutes a basic mechanism, are revisable in light of evidence. The evidence here is not experimental data but bibliographic data—the structure of scientific practice as revealed through citation networks and belief interconnection. By allowing molecules to emerge from this structure rather than imposing structure onto it, the ATLAS system remains epistemically humble about its own taxonomy. The molecules are hypotheses about the true functional organization of human environmental response. They can be revised when new belief networks emerge or when existing templates are reconceptualized.

This choice has consequences for system scalability and maintenance. As new T2 templates are added to the system (because new mechanistic insights emerge from research), the co-occurrence matrix M changes, and so the discovered latent variables will shift. A template once central to a molecule might become peripheral; a new template might activate an entirely new molecular structure. The system's taxonomy is not static. This requires periodic re-factoring of the molecule registry—re-running the factor analysis, re-interpreting the factors, updating T1.5 reductions as needed. It is work. But the work respects the dynamic character of science. The ATLAS system is designed to evolve as knowledge evolves, not to ossify around an initial category scheme.

---

## §175. The Annotation Layer — 25 Types, Three Parallel Systems, and the Integration Problem

*Last revised: 2026-03-04*

### §175.1: What Annotations Are and Why Knowledge Systems Need Them

An extraction captures what a paper claims. An annotation captures what experts think about what the paper claims. This distinction, simple as it seems, is foundational to how a mature knowledge system works.

When the ATLAS system extracts from a study that "daylight exposure reduces cortisol levels by 15%," the extraction is a statement of what the authors reported. But that same statement might be accompanied by several annotations: a calibration note questioning the validity of the cortisol assay used, a sensitivity flag noting that the effect varies wildly by season and latitude, a replication status indicating whether other labs have confirmed the finding, a dispute annotation showing that a competing theory predicts the opposite effect, and a historical context annotation placing this claim within twenty years of research on the topic. The extraction is a data point. The annotations are the interpretive layer that transforms data into knowledge.

Without annotations, every belief in the system carries equal richness. A claim extracted from a single pilot study appears indistinguishable from one extracted from a thirty-year replication program. A parameter value reported in one paper has the same epistemic standing as one confirmed across fifteen independent labs. The system becomes epistemically flat: information-rich in its breadth but impoverished in its depth.

With annotations, the knowledge base becomes stratified. Some beliefs carry dense metadata: they are flagged as clinically important, disputed by three teams, confirmed by replication studies, linked to five related findings, and tied to a broader historical narrative about how the field came to understand the phenomenon. Other beliefs remain bare—extracted once, annotated never—and the system knows to treat them with proportional epistemic caution. Annotations are the system's way of recording not just what we know, but how much confidence we should have in knowing it, and why.

Annotations serve several critical functions in ATLAS:

*First*, they encode expert judgment that cannot easily be captured in extraction schemas. No extraction template can anticipate every type of commentary that a domain expert might need to record. A surprise flag ("this finding contradicts twenty years of conventional wisdom") is too interpretive for extraction. A design implication ("this suggests CCT should be 2700-3000K in hospitality settings") is too prescriptive. An analogical bridge ("neural integration works like a parliament voting on conflicting proposals") is too narrative. Annotations give experts a structured way to add this interpretive layer without forcing them to modify core data models.

*Second*, annotations create feedback loops for quality assurance. When the system discovers that an important parameter is sensitive (varies widely across studies), it can flag that sensitivity and alert downstream consumers to exercise caution. When the gap predictor identifies an unanswered research question, it records that as an annotation so future extraction work can target the gap. When a belief is involved in a dispute, the annotation preserves the controversy so it does not get buried or forgotten.

*Third*, annotations are decoupled from extraction in time and authorship. An extraction is written when a paper is first processed. An annotation might be added weeks later by a different expert. This decoupling allows the system to grow and improve without forcing wholesale re-extraction every time someone notices something new. It also enables collaborative knowledge building: one person extracts what a paper says, another annotates what experts think about it.

*Fourth*, annotations provide what Quine calls the "sustaining power" of the belief system. In Quine's epistemology, a belief's position in the web is what gives it its standing. Annotations make that position explicit and queryable. They encode not whether a belief is true (which is philosophy's job), but where it sits in the epistemic ecosystem and why it deserves the credence it gets.

### §175.2: The 25 Annotation Types Across Six Layers

ATLAS currently supports 25 distinct annotation types, organized into six conceptual layers. The inventory below defines what information can be annotated and in what category it belongs.

| Layer | Type | Target | Purpose | Status |
|-------|------|--------|---------|--------|
| **1: Evidence** | CALIBRATION_NOTE | template, belief | Expert commentary on measurement quality and methodological reliability | SQLite-backed |
| | SENSITIVITY_FLAG | parameter, template | Identifies parameters that are uncertain or vary widely across studies | SQLite-backed |
| | EVIDENCE_OVERRIDE | belief, causal_link | Manual upgrade or downgrade of a belief's maturity level or strength | SQLite-backed |
| | PROVENANCE_PATCH | template, belief | Backfills missing provenance: DOI, funding source, author credentials, panel reference | SQLite-backed |
| **2: Relational** | CROSS_REFERENCE | template, template | Documents that two templates interact, share mechanisms, or form a complex system | SQLite-backed |
| | MOLECULE_LINK | template, finding | Connects a specific finding to a molecule (a theoretical primitive in the CVA system) | SQLite-backed |
| | CLINICAL_CAUTION | causal_link, parameter | Safety-relevant annotation: this parameter or relationship has clinical or real-world implications | SQLite-backed |
| **3: QA/User** | OPEN_QUESTION | template, belief | Knowledge gap marker: identifies what the system knows it does not know | SQLite-backed |
| | SEARCH_PROMPT | template, belief | Directed search suggestion for filling a knowledge gap | SQLite-backed |
| | USER_FEEDBACK | answer, extraction | User-reported quality rating and commentary on an answer or extraction | SQLite-backed |
| **4: CVA** | MEASUREMENT_MODALITY | finding, extraction | Records how a finding was measured: fMRI, EEG, behavioral, eye-tracking, etc. | JSON files |
| | STIMULUS_DESCRIPTION | finding, extraction | Describes the stimulus type used in a study: visual, auditory, spatial, naturalistic | JSON files |
| | MOLECULE_T15_LINK | finding, template | Links a finding to a T1.5 molecule through CVA analysis | JSON files |
| **5: Extended (A9–A18)** | SURPRISE_FLAG | finding, template | Marks counterintuitive findings that challenge common assumptions | No persistence |
| | DESIGN_IMPLICATION | finding, template | Translates a finding into actionable design guidance with cost and scope | No persistence |
| | DISPUTE | claim, template | Records where researchers actively disagree and what would resolve the controversy | No persistence |
| | ANALOGICAL_BRIDGE | finding, concept | Maps a technical concept to everyday experience with intellectual honesty about where the analogy breaks | No persistence |
| | REPLICATION_STATUS | finding, extraction | Tracks replication history: original study plus all replication attempts and outcomes | No persistence |
| | EFFECT_MAGNITUDE | finding, extraction | Provides human-interpretable effect size: Cohen's d, odds ratio, NNT, "magnitude in plain language" | No persistence |
| | CROSS_DOMAIN | finding, template | Identifies where a finding connects across disciplinary boundaries | No persistence |
| | HISTORICAL_CONTEXT | concept, finding | Tracks how an idea evolved over decades, including paradigm shifts | No persistence |
| | NARRATIVE_HOOK | finding, extraction | Provides a compelling opening line for progressive disclosure in QA answers | No persistence |
| | UNANSWERED_QUESTION | domain, template | Names a knowledge frontier: what would we need to study next, and how hard is it? | No persistence |
| **6: Circuits** | CIRCUIT_ASSOCIATION | finding, template | Links a finding to a functional circuit in the brain or a behavioral system | SQLite-backed |
| | ARCHETYPE_TAG | finding, template | Tags a finding with a T2 archetype (a common pattern across multiple studies) | SQLite-backed |

*The Evidence layer* (Layer 1) focuses on the reliability and context of individual claims. A CALIBRATION_NOTE might read: "The cortisol assay used in this study (BioRad) is known to be sensitive to circadian variation; interpret results with caution." A SENSITIVITY_FLAG identifies which parameters cause downstream uncertainty: "The effect size varies by season (r=0.15 to 0.45) and building latitude (r=0.10 to 0.60)." These annotations are not corrections—the extraction stands as reported—but they add interpretive scaffolding.

*The Relational layer* connects beliefs to each other and to the system's theoretical vocabulary. A CROSS_REFERENCE might note: "This finding on daylight and attention interacts with the arousal modulation template (TBL-A012) and should be read jointly." A MOLECULE_LINK anchors a finding to ATLAS's deeper theoretical framework: "This supports the Restorative Attention mechanism in Kaplan & Kaplan's ART theory." A CLINICAL_CAUTION surfaces safety concerns: "High-intensity blue light (>3000K) at night may suppress melatonin in vulnerable populations; recommend professional review before implementation."

*The QA/User layer* captures what the system and its users do not understand. OPEN_QUESTION marks genuine gaps: "Does biophilia enhance attention restoration more for introverts or extroverts? No study directly compares." SEARCH_PROMPT suggests where to look: "Search for studies comparing green space access by income quintile in school districts." USER_FEEDBACK records practical assessments from people who have used ATLAS answers: "This answer was too abstract for practitioners; needs design guidelines."

*The CVA layer* records methodological details specific to the computational visual analysis system. MEASUREMENT_MODALITY notes whether a finding came from fMRI (which measures brain blood flow with spatial but not temporal precision) or EEG (which has the opposite tradeoff) or behavioral observation (which measures what people actually do). STIMULUS_DESCRIPTION records what was shown: a photograph of nature, a video of a cityscape, a virtual reality environment, or a spatial configuration of real objects. MOLECULE_T15_LINK connects findings to theoretical molecules through this methodological lens.

*The Extended layer* (A9–A18) captures rich, interpretive knowledge that requires expert judgment and time to generate. A SURPRISE_FLAG might note: "Studies on dense vegetation consistently show it increases anxiety near crime hotspots—opposite to biophilia theory's prediction. Suggests negative conditions can override nature's restorative power." A DESIGN_IMPLICATION translates this into actionable guidance: "In high-crime neighborhoods, recommend naturalistic designs (curved forms, soft plant texture) rather than dense vegetation; cost tier: low to medium; applies to street-facing facades in commercial districts." A REPLICATION_STATUS tracks confidence through replication: "Original finding (N=120, 2015) was fully replicated in three independent studies (2017, 2019, 2021); one failed replication (2020) used different outcome measure; overall robustness score: 0.78." A DISPUTE records controversy: "Theory A predicts green space → stress reduction. Theory B predicts green space → cognitive load increase. Studies support both under different conditions (neighborhood safety, population demographics). Open question: what moderates the effect?" A HISTORICAL_CONTEXT provides narrative: "The attention restoration theory emerged from Kaplan & Kaplan's 1989 work on restorative environments. Challenged in the 1990s by cognitive load theory. Integrated in the 2010s through mechanistic studies showing dual pathways (bottom-up fascination + top-down restoration). Current consensus: both processes operate; conditions determine which dominates."

### §175.3: The Three Parallel Systems and Why Fragmentation Occurred

ATLAS's annotation infrastructure currently exists as three separate, non-unified systems, each with its own storage, API, and design logic.

**Layer 1: General-Purpose Annotations (SQLite-backed).** The core annotation service, implemented in `annotation_service.py`, provides CRUD operations on a SQLite table called `annotations`. It stores the 10 basic annotation types (A1–A8 plus CIRCUIT_ASSOCIATION and ARCHETYPE_TAG) with full support for versioning (immutable append-only with supersession), searching (full-text queries across content), and access control (author attribution, confidence scores). This layer was designed first because these ten types are the scaffolding for any knowledge system: evidence quality, relationships, and user feedback. The service is well-tested and production-ready. However, it is walled off from the other two layers.

**Layer 2: CVA-Specific Annotations (JSON file-backed).** The `cva_annotation_service.py` provides separate CRUD for the CVA-specific annotation types: MEASUREMENT_MODALITY, STIMULUS_DESCRIPTION, and MOLECULE_T15_LINK. These were implemented as JSON files in a separate directory (`data/cva_annotations/`) because (a) they were needed urgently for the CVA subsystem's visual analysis work, and (b) their structure differs from Layer 1 annotations (they embed complex objects rather than simple strings). The service includes auto-detection logic: given a template ID, it scans the template text and automatically identifies measurement modalities and stimulus types, populating annotations without human intervention. This pragmatic choice solved an immediate problem but created architectural debt.

**Layer 3: Extended A9–A18 Annotations (Data models only).** The `extended_annotations.py` file defines ten new annotation types as Python dataclasses: `SurpriseFlag`, `DesignImplication`, `Dispute`, `AnalogicalBridge`, `ReplicationStatus`, `EffectMagnitude`, `CrossDomainLink`, `HistoricalContext`, `NarrativeHook`, and `UnansweredQuestion`. These are rich, structured types that require significant expert effort to populate and are valuable for downstream use in QA and narrative generation. However, there is *no persistence service* for Layer 3. The dataclasses exist as in-memory objects; they have no home in the database. This means that if someone generates a DESIGN_IMPLICATION annotation for a finding, there is nowhere to save it so it will be available in the next session.

Why did this fragmentation happen? Because the system evolved pragmatically in response to immediate needs. Layer 1 was built when the core annotation requirement was clear. Layer 2 was added when the CVA team needed specialized annotations and could not wait for a unified design. Layer 3 was designed with deep thought about what a mature annotation system should include (e.g., surprise flags for progressive disclosure in QA) but was never given a persistence backend because the engineering effort to unify all three layers was deferred.

The result is architectural fragmentation with serious consequences. There is no single API to ask: "What annotations exist for belief X?" Instead, code must query Layer 1, Layer 2, and Layer 3 separately and synthesize the results. There is no universal search across all annotation types. Auto-annotation works only for Layer 2 (CVA). Most critically, annotations do not feed back into the rest of the system: SENSITIVITY_FLAGS exist in the database but are not consumed by template QA. OPEN_QUESTIONS are harvested for gap discovery (a win) but other annotation types sit inert, recorded but unused.

### §175.4: Immutable Append-Only Design and Epistemic Memory

ATLAS annotations are never deleted. Only superseded. This is a deliberate epistemic choice, not a default from careless design.

When an expert creates a CALIBRATION_NOTE saying "The cortisol assay in this study is unreliable," and months later a new study validates that assay, the expert does not delete the original annotation. Instead, they create a new annotation that supersedes it. The old annotation is marked as "superseded" but remains in the database. The entire history is preserved.

This design reflects a principle borrowed from event sourcing in software engineering (Fowler, 2005) and from archival science: the history of what was known at what time, and what experts believed about it, is itself an important record. If we delete annotations, we lose the ability to understand how the system's knowledge evolved. We also lose the ability to audit decisions: if someone says the annotation was wrong, we cannot trace why it existed or who created it.

Each annotation carries explicit metadata for this reconstruction: a unique identifier (UUID), author attribution (human expert or system name), ISO 8601 timestamp of creation, provenance recording how the annotation was created (e.g., "auto-detected from text," "created by panel member X," "harvested from external database Y"), a 0–1 confidence score representing the annotator's epistemic confidence, and a supersession pointer linking to the ID of any replaced annotation.

This design allows the system to reconstruct not just the current state of the knowledge base but also its history. It aligns with Quine's emphasis on the holistic character of belief revision: when we change our minds about one claim, the reverberations propagate through the web. By recording annotations as an append-only log, we create the possibility of studying those reverberations.

### §175.5: The Integration Problem — The Gap Between Storage and Use

The most pressing problem with ATLAS's annotation system is not storage, structure, or even unification. It is that annotations are stored but not used.

The database contains OPEN_QUESTION annotations that identify knowledge gaps. The gap predictor exists and runs nightly. These two pieces should connect: each OPEN_QUESTION should feed directly into gap discovery, boosting its priority. Currently, that connection exists only partially. The system harvests OPEN_QUESTION annotations for gap discovery work, a success. But it does not consume SEARCH_PROMPT annotations (which suggest where to search for answers) and does not route them to the VOI search subsystem.

The database contains SENSITIVITY_FLAG annotations marking parameters as uncertain. The template quality assurance subsystem evaluates whether a template's parameters are reliable. These should connect: a parameter with high SENSITIVITY_FLAG count should receive a lower reliability score, triggering manual review. Currently, the connection does not exist. SENSITIVITY_FLAGS are recorded but read from nowhere.

The database contains DISPUTE annotations recording where researchers actively disagree. The belief entrenchment subsystem computes how central a belief is to the web and how resistant it should be to change. Disputed beliefs should be less entrenched (more easily overturned by new evidence) than undisputed ones. This principle is clear. The implementation does not exist.

The dataclasses for A9–A18 annotations define a NARRATIVE_HOOK type, which holds a compelling opening line for engaging readers in progressive disclosure. The QA system generates answers to questions and displays them to users. These should connect: the QA system should check whether a belief has a NARRATIVE_HOOK annotation and, if so, open with that hook to engage the reader. Currently, the QA system does not even know that NARRATIVE_HOOK annotations exist.

This gap between storage and use is the integration problem. It can be solved in principle but requires sustained engineering effort: a unified query API across all three layers (~1 hour), consumption in QA with caveat insertion and hook-led progressive disclosure (~2 hours), consumption in entrenchment to reduce stability for disputed beliefs (~1 hour), consumption in AESHI for annotation coverage reporting (~1 hour), and automated annotation generation for A9–A18 types (~3 hours). A fully integrated annotation system would mean that every belief displayed in a QA answer carries relevant annotations. Disputes appear highlighted. Sensitivities appear flagged. Gaps appear as call-outs. The system stops storing metadata and starts using it.

### §175.6: Design Decision — Why Annotations Rather than Inline Metadata

The alternative architecture would be to add all annotation fields directly to the extraction schema. Instead of storing a template and a separate SENSITIVITY_FLAG, why not add a `sensitivity_notes` field to the template itself? Instead of a separate DISPUTE annotation, why not add a `disputes_field` array to the template? This would be simpler in some respects: one table instead of many, no join operations, no need for a separate API.

The annotation design was chosen instead for six reasons, each grounded in system architecture and epistemology.

*First, decoupling in time and authorship.* An extraction is created when a paper is ingested. Annotations are created when experts review it. These happen on different schedules, by different people, with different incentive structures. Conflating them in a single record makes it hard to manage this temporal and social separation.

*Second, evolution without re-extraction.* If annotations are inline, then adding a new annotation type requires modifying the template schema, migrating all existing data, and potentially re-extracting old papers. With separate annotations, new types can be added without touching the extraction tables.

*Third, multiple annotations of the same type.* A single belief might have multiple SENSITIVITY_FLAGS (one for parameter A, one for parameter B). With separate annotation records, each is its own row, and querying is straightforward.

*Fourth, immutable append-only versioning.* The annotation design uses a supersession model: old annotations are marked as superseded but never deleted. With inline metadata, you would have to version the entire template or extraction to track changes—wasteful and brittle.

*Fifth, heterogeneous structure.* A SENSITIVITY_FLAG is a simple string. A REPLICATION_STATUS is a complex object with nested arrays. A DESIGN_IMPLICATION carries structured parameter information and cost tiers. If these were inline, the template would need to support all possible structures, leading to sparse, confusing schemas.

*Sixth, independent persistence and distribution.* Annotations can be stored, queried, and cached independently of templates and beliefs. A query system can be built that indexes annotations but not templates. A caching layer can warm annotations separately from extraction data.

The annotation architecture, then, is not simpler than the inlining alternative. But it is more modular, more evolvable, and more epistemically principled. It says clearly: what a paper says (extraction) and what experts think about what it says (annotations) are separate concerns. They need separate storage, separate versioning, and separate consumption logic.

---

## §176. The Interpretation Space — Four Epistemic Zones, Question Taxonomy, and Gap Discovery

*Last revised: 2026-03-04*

### §176.1: The System's Self-Model of Knowledge

A knowledge system, if it is to improve its own epistemic standing, must first answer a prior question: what does it actually know, and how does it know it? This is not a rhetorical gesture toward self-awareness but a practical requirement. The ATLAS system maintains thousands of beliefs about the built environment, human perception, and design principles. These beliefs have different epistemic credentials. Some rest on multiple randomized trials with consistent findings. Others stand on single studies, or on theoretical derivation with sparse empirical grounding. Still others are explicit gaps — questions the system recognizes it cannot answer. And beyond these, there lie the unknowns that the system does not yet even recognize as questions.

The Interpretation Space is ATLAS's formal representation of this epistemic landscape. It is not a static classification scheme where beliefs are sorted into bins labeled "certain," "probable," and "uncertain." Rather, it is a dynamic model of what the system knows and doesn't know, organized into zones of epistemic proximity and probed by systematic question-type operators that reveal weaknesses in understanding, warrant grounding, mechanistic explanation, and actionable guidance.

The epistemological motivation is Quinean: the web of belief does not face the tribunal of experience one proposition at a time. Instead, it meets experience as a corporate body. A belief's epistemic standing is partly local—determined by its own warrant chain and argumentation defense—but partly holistic, determined by how it integrates with the rest of the web. The Interpretation Space extends Quine's intuition to an operational level: it identifies precisely where the web is coherent and robust, where tensions exist that demand resolution, where knowledge is well-formed but incomplete, and where the system confronts genuine unknowns it cannot yet articulate.

This self-model serves a critical function. The standard approach to knowledge management in deployed systems is demand-driven: observe what users ask about, notice where the system gives weak answers, and prioritize acquisition accordingly. This works when the users happen to ask about the system's weaknesses. But it samples the periphery of knowledge according to the arbitrary distribution of human interests, not according to the intrinsic structure of the knowledge base itself. A user might never ask about olfactory cues in the built environment, but the Interpretation Space can recognize—through its own systematic self-interrogation—that the system has a blind spot in multi-sensory biophilia, a gap whose resolution would reshape multiple belief clusters and improve the coherence of the whole web.

### §176.2: The Four Epistemic Zones

The Interpretation Space partitions ATLAS's epistemic territory into four zones, ordered by epistemic security and distance from the core of well-established knowledge.

**Zone 1: The Known Interior.** This is the region of credences ≥ 0.7, supported by strong warrants (CONSTITUTIVE or MECHANISM warrants with discount factors d ≥ 0.80), and defended against argumentation attacks of severity > 0.3. These are beliefs that have achieved epistemic stability in the Quinean sense: revising them would require substantial reorganization of the surrounding web. When the QA system draws on beliefs from Zone 1, it provides confident, well-sourced answers that can explain not merely what is true but why, how much, for whom, and what evidence would change the conclusion.

**Zone 2: The Active Boundary.** Here lie beliefs with moderate credence (0.4–0.7), or claims whose warrant chains contain gaps, or propositions subject to active argumentation disputes. The system can answer questions about these beliefs with meaningful caveats. This is the frontier where scientific activity is most productive. The claims are well-formed enough to test, but uncertain enough that new evidence would make a genuine difference to what the system believes.

**Zone 3: The Identified Periphery.** Beyond the boundary lies a region of explicit, well-formed gaps. These are questions the system recognizes it cannot answer, classified by gap type (MECHANISM, VALIDATION, BOUNDARY, DIRECTION, INTERACTION, MEDIATION) and linked to the beliefs they would affect if resolved. Zone 3 gaps are not absences; they are demands that the system can articulate precisely.

**Zone 4: The Uncharted Exterior.** Beyond the periphery lies genuinely uncharted territory—regions signaled by QA failures and conceptual blind spots. These are queries that cannot be classified, questions that fall through all handlers to the arbitrary fallback, follow-up chains that terminate in "I do not know" without the system being able to articulate what kind of knowledge is missing. The system does not know what it does not know.

The four-zone model matters because it tells the system where attention should be invested. Zone 1 beliefs require maintenance: defending their warrant chains, documenting boundary conditions as new evidence emerges. Zone 2 beliefs demand investigation: targeted research to resolve warrant gaps or boundary uncertainties. Zone 3 gaps are the system's research agenda—questions formulated but not yet answered. Zone 4 signals need for conceptual work: expanding the vocabulary and theoretical frameworks that allow the system to recognize and formulate questions it cannot yet pose.

### §176.3: The Question-Type Taxonomy as Epistemic Operators

The QA system's question taxonomy is typically understood as a classification scheme: given a user query, identify its type (MECHANISM, VALIDATION, BOUNDARY, etc.) and route it to the appropriate handler. But in the context of the Interpretation Space, the question types function differently. They are not merely categories; they are epistemic operators—functions that, when applied to a belief, generate specific kinds of follow-up questions and reveal specific kinds of incompleteness.

All ten operators—MECHANISM, VALIDATION, BOUNDARY, DIRECTION, COMPARISON, SURPRISE, CROSS_DOMAIN, EFFECT_SIZE, DESIGN_GUIDANCE, FRONTIER—can be systematically applied to any belief. A belief for which all operators produce high-quality answers occupies Zone 1. One for which some operators produce weak answers sits on the boundary between Zones 1 and 2. One for which most operators produce weak but articulate answers lies in Zone 2. One for which the operators reveal well-formed gaps occupies the threshold to Zone 3. And if the operators themselves fail to produce coherent questions, the belief approaches Zone 4.

This operationalization has a crucial property: it is uniform and exhaustive. Rather than waiting for users to probe the system's knowledge in arbitrary ways, the interpretation space probes every belief along every epistemic dimension. The result is a complete map of the system's strengths and weaknesses, not a sample biased by the distribution of user queries.

### §176.4: Endogenous Value and the Coherence-Driven Landscape

The Interpretation Space computes the epistemic value of resolving a gap not from external user demand but from the internal structure of the web of belief itself. This is a fundamental shift in how knowledge acquisition is prioritized.

Formally, the endogenous value of resolving a gap G is:

**V(G) = Structural_Impact(G) × Tractability(G) × Coherence_Tension(G)**

**Structural Impact(G)** measures how many beliefs would change credence if G were resolved, and by how much. This is computed via counterfactual coherence analysis: the system hypothetically resolves the gap, recomputes the credences of downstream beliefs via Bayesian update, and measures the magnitude of shift.

**Tractability(G)** estimates the difficulty of resolving the gap, inferred from the warrant structure of surrounding beliefs and the type of gap. MECHANISM gaps between mechanistically warranted beliefs have high tractability; BOUNDARY gaps for empirically warranted beliefs have moderate tractability; MECHANISM gaps in regions dominated by analogical warrants have low tractability; any gap in Zone 4 has very low tractability.

**Coherence_Tension(G)** measures whether the gap sits at a point of active stress in the web. If the gap is located near unresolved argumentation attacks, or near beliefs that push in different directions, or near contradictions in the empirical evidence, then resolving the gap would settle a dispute and stabilize the web. High tension means the gap is consequential not just structurally but emotionally—its resolution would bring harmony to a discordant region.

Together, these three factors identify gaps of genuine epistemic value. This value function reveals something that demand-driven systems routinely miss: what we might call *silent gaps*—regions of incompleteness invisible to users because they don't think to ask about them.

### §176.5: Probatory Rule Sets and Epistemic Closure

The Interpretation Space is not merely an overlay on the web of belief; it is an extension of the web itself. To formalize this extension, we require a notion of *probatory rules*—rules that govern the relationships between beliefs, not in the sense of logical entailment but in the sense of warrant adequacy, mechanism specification, argumentation integrity, and interpretive completeness.

Four rule sets define these probatory relationships:

**Rule Set R₁: Argumentation Rules.** Based on Walton's schemes for defeasible inference, these rules govern whether arguments supporting beliefs are closed against critical questions. An argument from expert opinion is *open* when constructed; it closes only when all critical questions—Is the source credible? Is the claim in the expert's domain? Do peers agree? Is the evidence consistent?—are answered with traceable evidence.

**Rule Set R₂: Warrant Rules.** These establish sufficiency conditions for each warrant type. An EMPIRICAL_ASSOCIATION warrant requires at least one replication or meta-analysis, quantified effect sizes with confidence intervals, a mechanism at the how-possibly level, at least one tested boundary condition, and cumulative sample size ≥ 100 or ≥ 3 independent studies.

**Rule Set R₃: Mechanism Rules.** These govern the specification of causal mechanisms according to a maturity ladder: how-possibly, how-plausibly, and how-actually.

**Rule Set R₄: Interpretation Rules.** Based on the ten question-type operators, R₄ rules specify when a belief has been adequately *interpreted*—not merely believed but explained, quantified, contextualized, and situated within a landscape of known unknowns.

The system is *closed under rule set Rᵢ* when, for every belief in the epistemic network to which Rᵢ applies, either the rule is satisfied or the unmet condition is explicitly tracked as a gap. Different purposes require different closures. An architect needs closure under R₂ and R₄-EFFECT_SIZE and R₄-DESIGN_GUIDANCE. A researcher writing a grant proposal needs closure under R₃ and R₄-FRONTIER. The system, when receiving a query, checks which rule sets define adequacy for the query's purpose.

This gives us a formal definition of epistemic adequacy: the system is adequate for purpose P when it achieves closure (≥80% of relevant rule conditions satisfied) under the rule sets that P demands.

### §176.6: Design Decision: A Separate Epistemic Layer

A natural question arises: why formalize the Interpretation Space as a separate computational layer rather than embed gap detection and value computation directly within the QA pipeline?

The answer lies in a distinction between two different epistemic tasks that are often conflated. The QA pipeline's task is to *answer questions*: given a query, retrieve relevant beliefs, compute their coherence, and generate an answer. The Interpretation Space's task is to *ask questions*: given the current state of the epistemic network, identify gaps, classify them, compute their value, and prioritize them for resolution.

If gap detection were embedded in the QA pipeline, the system would only probe gaps when users happened to ask questions that triggered gap-generating operators. The coverage would be incomplete and biased toward user interests. A separate layer allows the system to apply all operators to all beliefs, exhaustively and uniformly, independent of what users happen to ask.

Furthermore, separating the two layers creates clarity about epistemic standards. The QA system's criterion for success is: "Did I answer the user's question truthfully and well?" The Interpretation Space's criterion is different: "Did I identify all significant gaps, classify them correctly, and rank them by epistemic value?" By formalizing them separately, we avoid the confusion of mixing demand-driven (QA) with supply-driven (endogenous) value.

A third virtue of separation is modularity. The Interpretation Space can be updated, refined, and evolved independently of the QA system. New question-type operators can be added; rule sets can be revised; the value function can be recalibrated. The Interpretation Space thus represents a recognition of an elementary truth about knowledge systems: not all knowledge work is reactive. Some of the most important knowledge work is proactive: asking questions that should be answered, prioritizing investigation by the intrinsic structure of the knowledge base, and systematically seeking out gaps before users stumble upon them.

---

## §177. The Argumentation System — Walton Schemes, Citation Structure, and Debate Resolution

*Last revised: 2026-03-04*

### §177.1 Why Epistemic Flat Maps Must Become Structured Debates

A knowledge system that stores beliefs and their credences but does not model the arguments for and against them is epistemically impoverished. It resembles a map that marks terrain elevations but ignores the routes by which one might travel between peaks and valleys. ATLAS must do more than accumulate beliefs; it must represent the structure of scientific disagreement itself.

Science advances through debate, not through passive data accumulation. Kuhn's (1962) account of paradigm shifts makes this clear: scientific progress is not a smooth accumulation of facts but a punctuated series of crises in which competing frameworks clash. Lakatos (1978) refined Kuhn's account by arguing that scientific progress is the competition of research programmes, each with a hard core of foundational commitments and a protective belt of auxiliary hypotheses. Research programmes advance by generating novel predictions and explaining anomalies through modifications of the protective belt while preserving the core.

ATLAS must model this argumentative structure because it is the mechanism by which credences should be updated. When a new finding challenges a belief in the system, the relevant question is not merely "Is this finding true?" but "Does this finding undermine the arguments that support the belief?" Without an argumentation model, ATLAS would treat every belief as an isolated unit. With such a model, ATLAS can see that beliefs are embedded in networks of mutual support and attack.

### §177.2 The ArgumentationGraph: Citation Relationships as Typed Edges

The ArgumentationGraph service represents the scholarly argumentation structure as a directed multigraph in which nodes are papers and edges are citation relationships enriched with polarity information.

**Nodes** represent individual papers in the extraction corpus. Each node carries bibliographic metadata, theoretical scaffolding (list of theories referenced), quantitative markers (number of claims extracted, citation count), and temporal position.

**Edges** represent directed citation relationships between papers. Each edge is typed (cites, supports, challenges, extends, supersedes) and scored with a continuous polarity from −1.0 (directly contradicts) through 0.0 (neutral) to +1.0 (strongly supports), a confidence score, and a textual evidence explanation.

**Debate clusters** are detected through community analysis. Co-citation networks reveal groups of papers in active conversation. Each cluster is annotated with a contestation level (0.0 for consensus, 1.0 for highly contested) computed from the variance in polarities within the cluster.

### §177.3 Walton's Argumentation Schemes: The Grammar of Scientific Reasoning

Douglas Walton (1996) identified argumentation schemes—stereotypical patterns of reasoning that underlie defeasible inference. A scheme is a template: it says "If you have premises of this form and these critical questions are satisfied, then you are licensed to draw this conclusion." ATLAS implements five operationally central schemes: argument from expert opinion, argument from sign, argument from cause to effect, argument from analogy, and argument from correlation to cause. Each scheme structures how evidence transfers its evidential force to a conclusion.

When ATLAS extracts a claim from a paper, it identifies the argumentation scheme used to support that claim. It also identifies which critical questions the paper addresses and which remain open. An unaddressed critical question becomes a research gap: a place where future investigation would most efficiently resolve scientific uncertainty.

### §177.4 Toulmin Structure: The Microarchitecture of Warrants

Alongside Walton's schemes, ATLAS uses Toulmin's (1958) model of argument structure. Where Walton describes how inferences are licensed, Toulmin describes the components that must be present for a license to be legitimate.

Toulmin's classical structure has six parts: Data (the factual ground), Warrant (the bridge from data to claim), Backing (the evidence for the warrant), Claim (the conclusion), Qualifier (the strength expression), and Rebuttal (conditions under which the claim would fail).

ATLAS stores each claim with its Toulmin structure. This is not mere annotation; it is the foundation of the system's competition resolution algorithm (§129.3). When two papers make competing claims, the system can compare them structurally. Moreover, unaddressed components constitute research gaps. The combination of Walton and Toulmin creates a two-level architecture: Walton identifies the type of reasoning; Toulmin specifies what components must be present for that reasoning to be sound.

### §177.5 From Unaddressed Questions to Research Gaps

The epistemic value of the argumentation system is realized through the gap discovery pipeline. When ATLAS processes a claim, it identifies the argumentation scheme, extracts the critical questions, checks whether the source paper addresses each, and generates research gaps for unaddressed questions.

This gap then feeds into the Interpretation Space (§176). The system computes how many beliefs depend on the resolution and assigns research value accordingly. Unaddressed critical questions are not mere absences; they are structural vulnerabilities.

This becomes especially powerful when debates involve multiple schemes. Different papers on the same topic may use different argumentation strategies—expert opinion, cause-to-effect, analogy, correlation-to-cause—each leaving different critical questions in play. The argumentation graph surfaces these differences, showing not just that papers disagree, but *how* they disagree.

### §177.6 Design Decision: Formal Argumentation versus Informal Debate Tracking

ATLAS uses formal argumentation rather than informal narrative summaries for three reasons. *First, computational tractability*: formal schemes are decidable. Given a paper and an argument from expert opinion scheme, the system can ask computably: "Is expert status documented?" *Second, rational reconstruction of strength*: formal argumentation enables computational strength analysis, borrowing the core insight from Dung's (1995) abstract argumentation frameworks. *Third, gap discovery as feedback*: the research gaps discovered through unaddressed critical questions are only possible because the system understands the formal structure.

The cost of formalization is loss of nuance. Some debates cannot be cleanly classified into Walton schemes. ATLAS addresses this through explicit representation of competing complete arguments: if three schools of thought exist, each is modeled as a separate argument, and the system represents their competition without forcing one to "win." But the gain in tractability and gap discovery justifies the cost. Science progresses not by eliminating disagreement but by making disagreement precise, testable, and resolvable.

### §177.7 Connection to Web of Belief and Interpretation Space

The ArgumentationGraph integrates with three other systems. **Web of Belief (§140)**: every belief carries not only a credence and warrant type but also a location in the argumentation graph. A finding that addresses an unaddressed critical question has greater impact than one that merely adds to a large literature. **Interpretation Space (§176)**: the research gaps discovered through critical question analysis populate the gap inventory. The Coherence_Tension metric explicitly computes unresolved argumentation attacks. **QA System**: when users ask about contested claims, the system draws on the ArgumentationGraph to provide balanced responses with explicit presentation of competing arguments and their respective strengths and vulnerabilities

---

## §178. The Card System — Nine Types, Universal Schema, and the Iceberg Architecture

*Last revised: 2026-03-04*

*[Full content: /docs/master_doc_parts/PART_XXVI_section_178.md — ~4,200 words covering §178.1–§178.9: knowledge presentation problem, nine card types across three tiers, universal schema (surface/body/iceberg), tab architecture and user-type adaptation, ReductionClaim DAGs with premium irreducible-residual treatment, staleness and regeneration lifecycle, science writer agent and card maintenance, and design decision on cards versus documents.]*

---

## §179. Math Cards — The Three-Layer Explanation Architecture

*Last revised: 2026-03-04*

*[Full content: /docs/master_doc_parts/PART_XXVI_section_179.md — ~2,900 words covering §179.1–§179.8: why mathematical transparency matters, three layers (Intuition/Transparent/Details) with concrete examples, math card inventory (10 domains), science writer agent for intuition layers, design decision on progressive disclosure versus separate technical docs, quality assurance for math cards, math card library with status, and integration with QA and documentation systems.]*

---

## §180. ATLAS System Architecture — A Layer-by-Layer Guide

*Last revised: 2026-03-04*

*[Full content: /docs/master_doc_parts/PART_XXVI_section_180.md — ~3,800 words covering §180.1–§180.9: architectural vision (Quinean coherentism, epistemic transparency, layered reasoning), evidence ingestion pipeline, epistemic network (beliefs/templates/frameworks/molecules), interpretive layers (annotation/interpretation/argumentation), computational engine (credence/coherence/entrenchment), presentation layer (cards/QA/user adaptation), cross-layer data flow worked example, agent architecture (panels/writers/maintenance), and design decision on layered versus monolithic architecture.]*

---

## References (Part XXVI)

Alchourrón, C. E., Gärdenfors, P., & Makinson, D. (1985). On the logic of theory change: Partial meet contraction and revision functions. *The Journal of Symbolic Logic*, 50(2), 510–530.

Bechtel, W., & Abrahamsen, A. (2005). Explanation: A mechanistic alternative. *Studies in History and Philosophy of Science Part C*, 36(2), 421–441.

Borsboom, D., Mellenbergh, G. J., & van Heerden, J. (2003). The theoretical status of latent variables. *Psychological Review*, 110(2), 203–219. https://doi.org/10.1037/0033-295X.110.2.203

Craver, C. F. (2007). *Explaining the brain: Mechanisms and the mosaic unity of neuroscience*. Oxford University Press.

Cunningham, J. P., & Yu, B. M. (2014). Dimensionality reduction for large-scale neural recordings. *Nature Neuroscience*, 17(11), 1500–1509. https://doi.org/10.1038/nn.3776

Dung, P. M. (1995). On the acceptability of arguments and its fundamental role in nonmonotonic reasoning, logic programming and n-person games. *Artificial Intelligence*, 77(2), 321–357. https://doi.org/10.1016/0004-3702(94)00041-X

Fowler, M. (2005). Event sourcing. *martinfowler.com*. Retrieved from https://martinfowler.com/eaaDev/EventSourcing.html

Hintikka, J. (1962). *Knowledge and belief: An introduction to the logic of the two notions*. Cornell University Press.

Howard, R. A. (1966). Information value theory. *IEEE Transactions on Systems Science and Cybernetics*, SSC-2(1), 22–26.

Kuhn, T. S. (1962). *The structure of scientific revolutions*. University of Chicago Press.

Lakatos, I. (1978). *The methodology of scientific research programmes*. Cambridge University Press.

Pollock, J. L. (1995). *Cognitive carpentry: A blueprint for how to build a person*. MIT Press.

Quine, W. V. O. (1951). Two dogmas of empiricism. *The Philosophical Review*, 60(1), 20–43. https://doi.org/10.2307/2181906

Quine, W. V. O., & Ullian, J. S. (1970, 1978). *The web of belief*. Random House (1970); 2nd edition (1978).

Toulmin, S. E. (1958). *The uses of argument*. Cambridge University Press.

van Fraassen, B. C. (1980). *The scientific image*. Oxford University Press.

Walton, D. N. (1996). *Argumentation schemes for presumptive reasoning*. Lawrence Erlbaum Associates.

---

**End of PART XXVI**
