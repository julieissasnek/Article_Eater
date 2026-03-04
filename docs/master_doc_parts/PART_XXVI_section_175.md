# §175: The Annotation Layer — 25 Types, Three Parallel Systems, and the Integration Problem

*Last revised: 2026-03-04*

## §175.1: What Annotations Are and Why Knowledge Systems Need Them

An extraction captures what a paper claims. An annotation captures what experts think about what the paper claims. This distinction, simple as it seems, is foundational to how a mature knowledge system works.

When the ATLAS system extracts from a study that "daylight exposure reduces cortisol levels by 15%," the extraction is a statement of what the authors reported. But that same statement might be accompanied by several annotations: a calibration note questioning the validity of the cortisol assay used, a sensitivity flag noting that the effect varies wildly by season and latitude, a replication status indicating whether other labs have confirmed the finding, a dispute annotation showing that a competing theory predicts the opposite effect, and a historical context annotation placing this claim within twenty years of research on the topic. The extraction is a data point. The annotations are the interpretive layer that transforms data into knowledge.

Without annotations, every belief in the system carries equal richness. A claim extracted from a single pilot study appears indistinguishable from one extracted from a thirty-year replication program. A parameter value reported in one paper has the same epistemic standing as one confirmed across fifteen independent labs. The system becomes epistemically flat: information-rich in its breadth but impoverished in its depth.

With annotations, the knowledge base becomes stratified. Some beliefs carry dense metadata: they are flagged as clinically important, disputed by three teams, confirmed by replication studies, linked to five related findings, and tied to a broader historical narrative about how the field came to understand the phenomenon. Other beliefs remain bare—extracted once, annotated never—and the system knows to treat them with proportional epistemic caution. Annotations are the system's way of recording not just what we know, but how much confidence we should have in knowing it, and why.

Annotations serve several critical functions in ATLAS:

*First*, they encode expert judgment that cannot easily be captured in extraction schemas. No extraction template can anticipate every type of commentary that a domain expert might need to record. A surprise flag ("this finding contradicts twenty years of conventional wisdom") is too interpretive for extraction. A design implication ("this suggests CCT should be 2700-3000K in hospitality settings") is too prescriptive. An analogical bridge ("neural integration works like a parliament voting on conflicting proposals") is too narrative. Annotations give experts a structured way to add this interpretive layer without forcing them to modify core data models.

*Second*, annotations create feedback loops for quality assurance. When the system discovers that an important parameter is sensitive (varies widely across studies), it can flag that sensitivity and alert downstream consumers to exercise caution. When the gap predictor identifies an unanswered research question, it records that as an annotation so future extraction work can target the gap. When a belief is involved in a dispute, the annotation preserves the controversy so it does not get buried or forgotten.

*Third*, annotations are decoupled from extraction in time and authorship. An extraction is written when a paper is first processed. An annotation might be added weeks later by a different expert. This decoupling allows the system to grow and improve without forcing wholesale re-extraction every time someone notices something new. It also enables collaborative knowledge building: one person extracts what a paper says, another annotates what experts think about it.

*Fourth*, annotations provide what Quine calls the "sustaining power" of the belief system. In Quine's epistemology, a belief's position in the web is what gives it its standing. Annotations make that position explicit and queryable. They encode not whether a belief is true (which is philosophy's job), but where it sits in the epistemic ecosystem and why it deserves the credence it gets.

## §175.2: The 25 Annotation Types Across Six Layers

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

## §175.3: The Three Parallel Systems and Why Fragmentation Occurred

ATLAS's annotation infrastructure currently exists as three separate, non-unified systems, each with its own storage, API, and design logic.

**Layer 1: General-Purpose Annotations (SQLite-backed).** The core annotation service, implemented in `annotation_service.py`, provides CRUD operations on a SQLite table called `annotations`. It stores the 10 basic annotation types (A1–A8 plus CIRCUIT_ASSOCIATION and ARCHETYPE_TAG) with full support for versioning (immutable append-only with supersession), searching (full-text queries across content), and access control (author attribution, confidence scores). This layer was designed first because these ten types are the scaffolding for any knowledge system: evidence quality, relationships, and user feedback. The service is well-tested and production-ready. However, it is walled off from the other two layers.

**Layer 2: CVA-Specific Annotations (JSON file-backed).** The `cva_annotation_service.py` provides separate CRUD for the CVA-specific annotation types: MEASUREMENT_MODALITY, STIMULUS_DESCRIPTION, and MOLECULE_T15_LINK. These were implemented as JSON files in a separate directory (`data/cva_annotations/`) because (a) they were needed urgently for the CVA subsystem's visual analysis work, and (b) their structure differs from Layer 1 annotations (they embed complex objects rather than simple strings). The service includes auto-detection logic: given a template ID, it scans the template text and automatically identifies measurement modalities and stimulus types, populating annotations without human intervention. This pragmatic choice solved an immediate problem but created architectural debt.

**Layer 3: Extended A9–A18 Annotations (Data models only).** The `extended_annotations.py` file defines ten new annotation types as Python dataclasses: `SurpriseFlag`, `DesignImplication`, `Dispute`, `AnalogicalBridge`, `ReplicationStatus`, `EffectMagnitude`, `CrossDomainLink`, `HistoricalContext`, `NarrativeHook`, and `UnansweredQuestion`. These are rich, structured types that require significant expert effort to populate and are valuable for downstream use in QA and narrative generation. However, there is *no persistence service* for Layer 3. The dataclasses exist as in-memory objects; they have no home in the database. This means that if someone generates a DESIGN_IMPLICATION annotation for a finding, there is nowhere to save it so it will be available in the next session.

Why did this fragmentation happen? Because the system evolved pragmatically in response to immediate needs. Layer 1 was built when the core annotation requirement was clear. Layer 2 was added when the CVA team needed specialized annotations and could not wait for a unified design. Layer 3 was designed with deep thought about what a mature annotation system should include (e.g., surprise flags for progressive disclosure in QA) but was never given a persistence backend because the engineering effort to unify all three layers was deferred.

The result is architectural fragmentation with serious consequences. There is no single API to ask: "What annotations exist for belief X?" Instead, code must query Layer 1, Layer 2, and Layer 3 separately and synthesize the results. There is no universal search across all annotation types. Auto-annotation works only for Layer 2 (CVA). Most critically, annotations do not feed back into the rest of the system: SENSITIVITY_FLAGS exist in the database but are not consumed by template QA. OPEN_QUESTIONS are harvested for gap discovery (a win) but other annotation types sit inert, recorded but unused.

## §175.4: Immutable Append-Only Design and Epistemic Memory

ATLAS annotations are never deleted. Only superseded. This is a deliberate epistemic choice, not a default from careless design.

When an expert creates a CALIBRATION_NOTE saying "The cortisol assay in this study is unreliable," and months later a new study validates that assay, the expert does not delete the original annotation. Instead, they create a new annotation that supersedes it. The old annotation is marked as "superseded" but remains in the database. The entire history is preserved.

This design reflects a principle borrowed from event sourcing in software engineering (Fowler, 2005) and from archival science: the history of what was known at what time, and what experts believed about it, is itself an important record. If we delete annotations, we lose the ability to understand how the system's knowledge evolved. We also lose the ability to audit decisions: if someone says the annotation was wrong, we cannot trace why it existed or who created it.

Each annotation carries explicit metadata for this reconstruction:
- **id**: A unique identifier (UUID) for the annotation itself
- **author**: The human expert (or system name) who created it
- **created**: ISO 8601 timestamp of creation
- **provenance**: A JSON object recording how the annotation was created (e.g., "auto-detected from text", "created by panel member X", "harvested from external database Y")
- **confidence**: A 0–1 score representing the annotator's epistemic confidence in the annotation's correctness
- **supersedes**: If this annotation replaces an older one, a pointer to the ID of the superseded annotation

This design allows the system to reconstruct not just the current state of the knowledge base but also its history. It aligns with Quine's emphasis on the holistic character of belief revision: when we change our minds about one claim, the reverberations propagate through the web. By recording annotations as an append-only log, we create the possibility of studying those reverberations.

## §175.5: The Integration Problem — The Gap Between Storage and Use

The most pressing problem with ATLAS's annotation system is not storage, structure, or even unification. It is that annotations are stored but not used.

The database contains OPEN_QUESTION annotations that identify knowledge gaps. The gap predictor exists and runs nightly. These two pieces should connect: each OPEN_QUESTION should feed directly into gap discovery, boosting its priority. Currently, that connection exists only partially. The system harvests OPEN_QUESTION annotations for gap discovery work, a success. But it does not consume SEARCH_PROMPT annotations (which suggest where to search for answers) and does not route them to the VOI search subsystem.

The database contains SENSITIVITY_FLAG annotations marking parameters as uncertain. The template quality assurance subsystem evaluates whether a template's parameters are reliable. These should connect: a parameter with high SENSITIVITY_FLAG count should receive a lower reliability score, triggering manual review. Currently, the connection does not exist. SENSITIVITY_FLAGS are recorded but read from nowhere.

The database contains DISPUTE annotations recording where researchers actively disagree. The belief entrenchment subsystem computes how central a belief is to the web and how resistant it should be to change. Disputed beliefs should be less entrenched (more easily overturned by new evidence) than undisputed ones. This principle is clear. The implementation does not exist.

The dataclasses for A9–A18 annotations define a NARRATIVE_HOOK type, which holds a compelling opening line for engaging readers in progressive disclosure. The QA system generates answers to questions and displays them to users. These should connect: the QA system should check whether a belief has a NARRATIVE_HOOK annotation and, if so, open with that hook to engage the reader. Currently, the QA system does not even know that NARRATIVE_HOOK annotations exist.

This gap between storage and use is the integration problem. It can be solved in principle but requires sustained engineering effort:

1. **Unified query API**: Implement a single `get_all_annotations(target_id, target_type)` method that queries all three layers and returns a unified list. This is a ~1-hour engineering task.

2. **Consumption in QA**: Modify the QA system to query annotations for each belief it serves to users. If SENSITIVITY_FLAGs exist, append a caveat to the answer. If a NARRATIVE_HOOK exists, lead with it. If a DISPUTE annotation exists, present both positions. This is a ~2-hour task.

3. **Consumption in entrenchment**: Modify the belief entrenchment calculation to reduce entrenchment for beliefs that have DISPUTE or OPEN_QUESTION annotations. High dispute count = low entrenchment = easier to revise. This is a ~1-hour task.

4. **Consumption in AESHI**: The system health dashboard (AESHI) should report annotation coverage: what percentage of beliefs have at least one annotation, what is the distribution of annotation types, what are the most-disputed beliefs. This creates pressure to improve annotation coverage. This is a ~1-hour task.

5. **Automated annotation**: Implement persistence and auto-generation for A9–A18 types. When a new extraction is created, auto-generate a SURPRISE_FLAG if it contradicts common assumptions, auto-generate an UNANSWERED_QUESTION if it raises new research questions, auto-generate EFFECT_MAGNITUDE with structured interpretations. This is a ~3-hour task.

A fully integrated annotation system would mean that every belief displayed in a QA answer carries relevant annotations. Disputes appear highlighted. Sensitivities appear flagged. Gaps appear as call-outs. The system stops storing metadata and starts using it.

## §175.6: Design Decision — Why Annotations Rather than Inline Metadata

The alternative architecture would be to add all annotation fields directly to the extraction schema. Instead of storing a template and a separate SENSITIVITY_FLAG, why not add a `sensitivity_notes` field to the template itself? Instead of a separate DISPUTE annotation, why not add a `disputes_field` array to the template? This would be simpler in some respects: one table instead of many, no join operations, no need for a separate API.

The annotation design was chosen instead for several reasons, each grounded in system architecture and epistemology.

*First, decoupling in time and authorship.* An extraction is created when a paper is ingested. Annotations are created when experts review it. These happen on different schedules, by different people, with different incentive structures. The extraction is "what the paper says." The annotation is "what experts think about what the paper says." Conflating them in a single record makes it hard to manage this temporal and social separation. With separate tables, one person can extract papers on a schedule, and a different expert team can annotate them on their own schedule, without blocking each other.

*Second, evolution without re-extraction.* If annotations are inline, then adding a new annotation type requires modifying the template schema, migrating all existing data, and potentially re-extracting old papers to populate the new field. With separate annotations, new types can be added to the system without touching the extraction tables. A new insight about a paper can spawn a new annotation type without any changes to the core data model.

*Third, multiple annotations of the same type.* A single belief might have multiple SENSITIVITY_FLAGS (one for parameter A, one for parameter B, one for an overall effect size sensitivity). A single extraction might have multiple DISPUTE annotations (theory X disputes claim Y, theory Z disputes claim W). With inline metadata, you would need to store arrays, and querying becomes awkward. With separate annotation records, each annotation is its own row, and querying is straightforward: find all SENSITIVITY_FLAG rows for this target ID.

*Fourth, immutable append-only versioning.* The annotation design uses a supersession model: old annotations are marked as superseded but never deleted. This creates an auditable record of how the system's metadata evolved. With inline metadata, you would have to version the entire template or extraction to track changes to metadata—wasteful and brittle. With annotations, changes are lightweight and traceable.

*Fifth, heterogeneous structure.* A SENSITIVITY_FLAG is a simple string. A REPLICATION_STATUS is a complex object with nested arrays of replication entries. A NARRATIVE_HOOK is a string with a type tag. A DESIGN_IMPLICATION carries structured parameter information and cost tiers. If these were inline, the template would need to support all possible structures, leading to sparse, confusing schemas. With annotations, each type has its own dataclass or table structure, optimized for its purpose.

*Sixth, independent persistence and distribution.* Annotations can be stored, queried, and cached independently of templates and beliefs. A query system can be built that indexes annotations but not templates. A caching layer can warm annotations separately from extraction data. With inline metadata, you cannot make these optimizations without reorganizing the template table.

The annotation architecture, then, is not simpler than the inlining alternative. But it is more modular, more evolvable, and more epistemically principled. It says clearly: what a paper says (extraction) and what experts think about what it says (annotations) are separate concerns. They need separate storage, separate versioning, and separate consumption logic.

---

## References

Fowler, M. (2005). Event sourcing. *martinfowler.com*. Retrieved from https://martinfowler.com/eaaDev/EventSourcing.html

Quine, W. V. O. (1951). Two dogmas of empiricism. *The Philosophical Review*, 60(1), 20–43. https://doi.org/10.2307/2181906

Quine, W. V. O., & Ullian, J. S. (1970). *The web of belief*. Random House.

---

*This section documents the current state of the ATLAS annotation system as of Sprint A (2026-03-04). Integration work is scheduled for Sprint B–C. See `AG_QA_ANNOTATION_IMPLEMENTATION_PLAN_2026-03-01.md` for the full roadmap.*
