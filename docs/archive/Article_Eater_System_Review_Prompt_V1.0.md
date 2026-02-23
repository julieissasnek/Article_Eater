# ARTICLE EATER: COMPREHENSIVE SYSTEM REVIEW PROMPT
## Version 1.0 — February 14, 2026
## For use with: Claude, Gemini, ChatGPT, Antigravity, or human reviewers

---

# INSTRUCTIONS FOR THE REVIEWER

You are conducting a comprehensive, adversarial review of **Article Eater**, a research software system that extracts causal claims from scientific literature and assembles them into Bayesian networks using Quinean coherentist epistemology. The system is being developed for the field of cognitive neuroscience of architecture (CNFA) — studying how built environments affect human cognition, emotion, physiology, and behavior.

**Your job is to be ruthlessly honest.** The developer (a professor of cognitive science with 35 years experience, former MIT AI Lab researcher) wants to know what's wrong, what's fragile, what won't scale, what's intellectually dishonest, what's over-engineered, and what's missing. Flattery is useless. Qualified praise for things that genuinely work is welcome. The goal is a system that actually advances the field, not one that merely impresses.

**How to proceed:**

1. Read the SYSTEM DESCRIPTION below carefully.
2. Then work through each of the NINE REVIEW DIMENSIONS in order.
3. For each dimension, convene the specified expert panel. Each panelist should speak in their own voice, with their own concerns and intellectual commitments. Panelists should disagree with each other where genuine disagreement exists.
4. After each panel, provide a VERDICT with specific, actionable findings rated CRITICAL / SERIOUS / MODERATE / MINOR / STRENGTH.
5. After all seven dimensions, provide a FINAL ASSESSMENT addressing the meta-question: is this enterprise sound?

**Important ground rules:**
- Cite specific architectural decisions, data structures, or algorithms from the system description when making claims. Vague criticism is useless.
- When you identify a problem, also indicate whether it's a design problem (wrong approach), an implementation problem (right approach, poor execution), or a scope problem (shouldn't be attempted at all).
- Distinguish between problems that are fatal if not addressed, problems that degrade quality, and problems that are theoretical concerns but unlikely to bite in practice.
- If the codebase is available to you (e.g., you're running in Antigravity or Claude Code with file access), READ THE ACTUAL CODE, don't just review the specification. Specifications lie; code is ground truth.

---

# SYSTEM DESCRIPTION

## What Article Eater Does

Article Eater reads scientific papers (PDFs), extracts causal claims with structured metadata, and inserts them into a web of belief — a graph where nodes are claims and edges are typed relationships (coherence, tension, evidential support, bridge warrants). The system then:

1. Computes entrenchment scores via iterative constraint satisfaction (Quinean coherence)
2. Assembles justified claims into causal Bayesian networks (Pearl-style DAGs)
3. Assesses evidence quality using a multi-dimensional validity framework
4. Monitors its own epistemic health via reflexive algorithms
5. Communicates confidence calibration to users

## Architecture

### Three Processing Layers
- **Extraction pipeline**: PDF → structured claim objects with metadata (study design, sample size, methods, argumentative structure, source quality indicators)
- **Web of belief**: Typed graph (nodes + edges) with entrenchment scoring via constraint satisfaction
- **BN assembly**: Converts justified web claims into causal DAG structures

### Three Theoretical Tiers
- **Tier 1**: Eight neurally-grounded theoretical frameworks (Predictive Processing, Attention Restoration, Stress Recovery, Biophilia, Embodied Cognition, Default Mode/Task-Positive Networks, Neuromodulatory Systems, Allostasis). These are hand-authored context for interpretation, not extracted from papers.
- **Tier 2**: Epistemic infrastructure — four epistemic templates (E1: Coherence-Based Belief Maintenance, E2: Social Epistemics, E3: Epistemic Emotions, E4: Reflective Equilibrium), plus reflexive monitoring algorithms
- **Tier 2b**: Methodological validity framework — measurement instrument profiles, presentation modality validity, task-ecological validity scoring
- **Tier 3**: Extracted empirical claims (the actual nodes in the BN)

### Four Channels of Epistemic Confidence
Every claim assessed on:
1. **Network Coherence** — mutual support within the web (Quinean)
2. **Source Quality** — composite of methodological_rigor, presentation_validity, measurement_validity, task_ecological_validity, independence_of_evidence
3. **Bayesian Integration** — posterior updating via causal inference
4. **Meta-Epistemic Monitoring** — structural vulnerability detection

### Source Quality Computation
Five sub-scores combined via weighted sum:
- `methodological_rigor` (0.40) — design quality, sample size, pre-registration, blinding
- `theoretical_commitment` (0.15, inverted) — author bias from championing the theory
- `independence_of_evidence` (0.25) — lab diversity, paradigm diversity, method diversity
- `replication_status` (0.20) — replicated / partially / unreplicated / failed

### Claim Type Bifurcation
- **Type A (Evaluative-response)**: "People prefer X" — well-supported by standard lab paradigm
- **Type B (Functional-effect)**: "X reduces stress / improves performance" — requires ecological evidence
- Connected by GENERALIZABILITY_WARRANT links (default weight 0.5 — moderate confidence that evaluative findings generalize to functional effects)

### Effect Pathways
Every functional-effect claim tagged:
- EXPLICIT: requires conscious awareness
- IMPLICIT_COGNITIVE: operates below awareness through cognitive pathways
- IMPLICIT_PHYSIOLOGICAL: operates through physiological pathways
- MIXED: both pathways active

### Method Registry
A growing data structure profiling every measurement instrument and presentation modality:
- Temporal dynamics (onset, peak, recovery, minimum sampling window)
- Confound structure (known confounders, VR-specific threats)
- Construct validity maps ({construct: validity_score})
- Hardware variants
- UNCHARACTERIZED flagging for new/unknown methods

### Task-Ecological Validity
Five weighted components:
- task_authenticity (0.30): ecological task vs. artificial evaluation
- state_characterization (0.20): incoming participant state measured/controlled?
- attentional_ecology (0.20): attention naturally distributed or directed?
- temporal_ecology (0.15): exposure duration representative?
- social_ecology (0.15): social context representative?

Task classification: EXPLICIT_EVALUATION (0.2) → LAB_COGNITIVE_TASK (0.4) → SIMULATED_ECOLOGICAL (0.6) → REAL_TASK_CONTROLLED (0.8) → NATURAL_BEHAVIOR (1.0)

### Reflexive Monitoring (4 algorithms)
1. **Coherence Audit**: Detects entrenchment changes without new direct evidence (coherence drift)
2. **Entrenchment Asymmetry Monitor**: Flags claims with high entrenchment but weak direct evidence
3. **Structural Bias Detection**: Checks evidence_independence, paradigm_diversity, method_diversity
4. **Adversarial Review Cycle**: Stress-tests most entrenched claims by boosting counter-evidence

### Five Automatic Argumentative Challenges
Generated during extraction by checking methods against registry:
1. Temporal misalignment (instrument lag exceeds protocol)
2. Presentation lacks critical sensory channel
3. VR confounded measurement (no cybersickness control)
4. Single-modality measurement
5. Exposure duration inadequate for construct

### Typed Link Taxonomy
Edges include: EPISTEMIC_DERIVATION, EPISTEMIC_CROSS_TEMPLATE, EPISTEMIC_MEDIATION, COHERENCE_SUPPORT, COHERENCE_TENSION, ARGUMENTATIVE_SUPPORT, ARGUMENTATIVE_CHALLENGE, GENERALIZABILITY_WARRANT, plus existing types (bridge warrants, causal links, etc.)

### Extraction Pipeline
From each paper, extracts: causal claims, study_design, sample_size, pre_registration, author_affiliations, funding_source, argument_for/against, replication_type, pathway_type (SUBPERSONAL/PERSONAL_EPISTEMIC/MIXED), PE_subtype (FUNCTIONAL/NAVIGATIONAL/SOCIAL), and matches methods against registry.

---

# REVIEW DIMENSION 1: CODE ARCHITECTURE & ENGINEERING QUALITY

## Panel: Software Architecture Review Board

Convene the following panelists:
- **Martin Fowler** — refactoring, code smells, enterprise patterns
- **Robert C. Martin (Uncle Bob)** — clean code, SOLID principles, test-driven development
- **Sandi Metz** — object-oriented design, practical simplicity, "you're not gonna need it"
- **Rich Hickey** — simplicity vs. complexity, value of immutability, accidental vs. essential complexity
- **Bryan Cantrill** — systems programming, debugging, production reliability

## Questions to Address

1. **Coupling and Cohesion**: The system has three main layers (extraction, web, BN assembly) plus the method registry, reflexive monitors, and validity scoring. How tightly coupled are these? Can any layer be tested independently? If the extraction pipeline changes output format, how many downstream modules break?

2. **Enum Proliferation**: The system defines numerous enums (NodeDomain, NodeSubtype, LinkType, PathwayType, ReplicationStatus, PESubtype, BridgeWarrantSubtype, TaskClass, EffectPathway, ClaimType, EmpiricalStatus). Is this appropriate categorical precision or is it type system overengineering? Would a more flexible schema (e.g., tagged metadata dictionaries) serve better for a system that must evolve as the field evolves?

3. **The God Object Problem**: Does the claim node try to be too many things? It carries: causal text, study metadata, argumentative metadata, pathway classification, PE subtype, validity scores, entrenchment, source quality, method matches, ecological validity scores. Is this a well-factored data object or a kitchen sink?

4. **Test Architecture**: Each sprint has acceptance tests. But are there integration tests that verify the whole pipeline from PDF ingestion through web assembly through BN output? What happens when tests pass individually but the system fails end-to-end?

5. **Configuration Debt**: Multiple configurable weights and thresholds (source quality weights, coherence audit threshold, entrenchment asymmetry threshold, task ecological validity component weights, generalizability warrant default, adversarial review precision boost). Where are these managed? Is there a single configuration surface, or are magic numbers scattered throughout?

6. **Error Handling and Graceful Degradation**: What happens when the extraction pipeline encounters a paper it can't parse? When a method isn't in the registry? When the BN assembly produces a cycle? When constraint satisfaction doesn't converge? Is there a unified error handling strategy or ad hoc try/catches?

7. **Data Persistence**: How is the web of belief stored? Is it in-memory only? File-based? Database? What happens to 500 papers worth of claims after a crash? Is there any versioning of the web state?

8. **Performance at Scale**: The system currently targets CNFA (~500-2000 papers). But constraint satisfaction is iterative, coherence audit runs after every integration, adversarial review re-runs constraint satisfaction N times. What's the computational complexity? At what web size does this become impractical?

---

# REVIEW DIMENSION 2: THEORETICAL COHERENCE & INTELLECTUAL HONESTY

## Panel: Philosophy of Science Review Board

Convene:
- **Larry Laudan** — scientific progress, problem-solving effectiveness, methodology
- **Helen Longino** — social epistemology, values in science, critical contextual empiricism
- **Bas van Fraassen** — constructive empiricism, pragmatics of explanation, anti-realism
- **Paul Thagard** — computational epistemology, ECHO, coherence theory (the closest existing system)
- **Judea Pearl** — causal inference, DAGs, do-calculus

## Questions to Address

1. **Quinean Coherentism vs. Bayesian Inference**: The system claims to use BOTH Quinean coherentism (no foundations, mutual support) AND Bayesian networks (conditional probabilities, directed causation). These are fundamentally different epistemologies. Quine's web is holistic — revision propagates bidirectionally. Pearl's DAGs are directional — causation flows parent to child. How are these reconciled? Is the system actually implementing one while claiming both? Is the "Quinean web" just providing entrenchment weights that feed into a conventional Bayesian network?

2. **The Circularity Problem**: The system uses reflexive monitoring to detect its own biases. But the monitoring algorithms use the same coherence framework they're monitoring. Coherence audit detects coherence drift, but what counts as "drift" versus "legitimate update" depends on the very coherence scores being audited. Is this genuinely reflexive or is it the system checking itself with its own ruler?

3. **Operationalization Fidelity**: The theoretical framework is sophisticated (Predictive Processing, Quinean epistemology, Pearl's causal inference). But the implementation reduces these to: keyword matching for pathway classification, weighted sums for source quality, threshold comparisons for monitoring flags. Is there a dangerous gap between the theoretical sophistication of the DESCRIPTION and the mechanical simplicity of the IMPLEMENTATION? Are we putting a philosophy-of-science costume on what is actually a weighted scoring system?

4. **The Hand-Authored Tier 1 Problem**: Eight theoretical frameworks are hand-authored, not extracted from literature. Who writes them? With what biases? The system claims to be evidence-driven but its interpretive framework is manually imposed. How is this different from a literature review where the author chose which theories to feature?

5. **Generalizability Warrant Default**: The system sets GENERALIZABILITY_WARRANT default weight to 0.5, meaning evaluative findings get 50% credit toward functional effects. This is a profoundly consequential assumption. On what basis? The system is making a strong empirical claim (lab preference studies half-predict real-world outcomes) and embedding it as a default parameter. Is there evidence for this specific number?

6. **Is Coherence Epistemically Virtuous?**: The system treats coherence as a positive epistemic property. But many things that cohere are false (conspiracy theories are maximally coherent). Coherence is only epistemically virtuous when the input evidence is independently reliable. Does the system adequately weight evidential independence to prevent coherent-but-wrong webs?

---

# REVIEW DIMENSION 3: EXTRACTION PIPELINE ROBUSTNESS

## Panel: NLP and Information Extraction Specialists

Convene:
- **Christopher Manning** — NLP, dependency parsing, information extraction
- **Dan Jurafsky** — computational linguistics, pragmatics of scientific language
- **Oren Etzioni** — Open Information Extraction, semantic web, machine reading
- **A working CNFA researcher** (e.g., Colin Ellard, environmental psychologist) — domain expert who knows how papers in this field actually read

## Questions to Address

1. **Causal Claim Extraction Accuracy**: What is the expected precision and recall of causal claim extraction from CNFA papers? Scientific claims are hedged, qualified, contextualized. "Our results suggest a possible association between ceiling height and creative cognition, though the effect was moderated by..." — how does the extractor handle this? Is there a validation study?

2. **Argumentative Structure Detection**: The pipeline extracts argument_for and argument_against by looking for phrases like "consistent with [Theory]" and "challenges [Theory]." But scientific papers are rhetorically complex — authors frame everything as supporting their position. Even null results get spun as "consistent with a modified version of the theory." How does the extractor handle motivated framing?

3. **Method Identification Robustness**: The pipeline matches methods against the registry using Methods section parsing. But papers describe methods inconsistently. "Heart rate variability" vs. "HRV" vs. "time-domain HRV" vs. "RMSSD" vs. "the root mean square of successive differences in R-R intervals." How robust is matching? What's the false-negative rate for non-standard descriptions?

4. **Pathway Classification via Keywords**: The classifier uses keyword lists (EPISTEMIC_KEYWORDS, SUBPERSONAL_KEYWORDS) to tag claims. But keywords are context-dependent: "temperature" is SUBPERSONAL when referring to air temperature but PERSONAL_EPISTEMIC when referring to "color temperature affects emotional interpretation." How bad is the error rate from context-free keyword matching?

5. **PDF Parsing and Table Extraction Quality**: The entire pipeline depends on accurate PDF text extraction. Scientific PDFs have multi-column layouts, equations, tables, figures with captions, references sections. How robust is the PDF parser? The system also needs structured data from PDF tables (results tables, participant demographics, effect sizes). Table extraction from PDFs is notoriously error-prone. What's the error rate on numeric data? Is there validation?

6. **LLM-Based vs. Rule-Based Extraction — The Hybrid Problem**: The implementation specifies keyword-based classifiers for pathway type and PE subtype (checking if "thermal" or "wayfinding" appears in claim text). But causal claim extraction itself presumably uses LLM calls. This creates a strange hybrid: sophisticated LLM extraction of claims, followed by crude keyword classification of properties. Why not use the LLM for classification too? And if you do — how do you handle non-determinism? Two LLM calls on the same paper may produce different claim counts, different causal directions, different argument_for assignments. Is there a canonical extraction that gets frozen?

7. **What About Non-English Literature?**: CNFA has active research communities in China, Japan, South Korea, Germany, Scandinavia, Turkey, Iran. The extraction pipeline appears English-only. How much of the literature is being missed? Does this introduce systematic geographic/cultural bias into the web?

---

# REVIEW DIMENSION 4: USER SCENARIOS & PRACTICAL VIABILITY

## Panel: End Users and Stakeholders

Convene:
- **A junior CNFA PhD student** — needs to understand the field, find gaps, plan studies
- **A senior CNFA researcher writing a review paper** — needs comprehensive, trustworthy synthesis
- **An evidence-based design practitioner** — needs actionable guidelines for building design
- **A research funding agency program officer** — needs to evaluate which CNFA claims are well-supported

## Scenarios to Walk Through

**Scenario A — First Use**: A PhD student loads 50 papers on biophilic design. What does the system produce? How long does it take? What does the output look like? Is it a graph visualization? A report? A queryable database? How does the student know whether to trust the output?

**Scenario B — Contested Claim**: The system has processed 200 papers. A researcher asks: "Is there good evidence that natural materials reduce stress?" The web contains 15 supporting claims (mostly Type A evaluative from photo studies) and 3 challenging claims (one failed replication, two methodological critiques). How does the system represent this? Does it give a clear answer or a nuanced hedge? Can the researcher see WHY the system rates the evidence as it does?

**Scenario C — Method Registry Gap**: A new paper uses continuous glucose monitoring as a stress biomarker in a workplace study. The method registry has no entry for continuous glucose monitoring. What happens? Does the claim get extracted? Does it get lower confidence because the method is UNCHARACTERIZED? Can the user add a method profile?

**Scenario D — Contradictory Evidence**: Two high-quality RCTs report opposite results on the same question (ceiling height and creativity). The web now has strong evidence on both sides. How does constraint satisfaction handle genuine equipoise? Does the system represent uncertainty well, or does it pick a winner?

**Scenario E — Scale Test**: The system has ingested 1000 papers over 6 months. A new high-profile meta-analysis is published that contradicts several entrenched claims. How does the system handle this? Does coherence audit flag the downstream effects? How disruptive is one high-quality paper to a mature web?

**Scenario F — Abuse Case**: A commercial design firm loads cherry-picked papers supporting their proprietary "wellness design" product. The system's structural bias detection should catch this — but only if the papers are from a limited lab network. What if the cherry-picking is more subtle (selecting only positive results from diverse labs)?

---

# REVIEW DIMENSION 5: METHODOLOGICAL VALIDITY FRAMEWORK (TIER 2b)

## Panel: Research Methodology Specialists

Convene:
- **Jacob Cohen** — statistical power, effect sizes, "the earth is round (p < .05)"
- **John Ioannidis** — why most published research findings are false, meta-science
- **Deborah Mayo** — error-statistical philosophy, severe testing
- **Harry Heft** — ecological psychology, ecological validity in environmental research
- **Karl Friston** — predictive processing, active inference, free energy principle

## Questions to Address

1. **Weight Assignments**: The task-ecological validity weights (task_authenticity=0.30, state_characterization=0.20, etc.) and source quality weights (rigor=0.40, commitment=0.15, etc.) determine the system's entire evidence evaluation. Where do these numbers come from? Are they empirically grounded or expert intuition? How sensitive is the system to changes in these weights? Has anyone done a sensitivity analysis?

2. **The Implicit Effects Assumption**: The system claims that implicit cognitive and physiological pathways are "probably more consequential" than explicit evaluative responses. This is a strong empirical claim that drives the entire task-ecological validity framework. But is there actually evidence that implicit effects dominate? Or is this a theoretical prediction from Predictive Processing that hasn't been tested?

3. **Temporal Dynamics Adequacy**: The method registry stores onset, peak, and recovery for physiological measures. But many architectural effects are chronic, not acute. Years of poor lighting affect circadian rhythms cumulatively. The temporal dynamics in the registry are designed for acute experimental paradigms. How does the system handle chronic/cumulative effects that play out over months or years?

4. **The Demand Characteristics Catch-22**: The system penalizes studies where participants' attention is directed to architectural features (low attentional_ecology score). But almost ALL experimental studies necessarily direct attention — that's how experiments work. Is the system systematically devaluing experimental evidence in favor of observational evidence? Is that epistemically justified?

5. **VR Validity Assumptions**: The immersion hierarchy places photos at Level 2 and room-scale VR at Level 5. But this assumes VR is "more valid" than photos for all constructs. For material texture, photos might be MORE valid than VR (at least photos show real materials; VR shows rendered textures). Is the hierarchy too coarse?

---

# REVIEW DIMENSION 6: BAYESIAN NETWORK ASSEMBLY & CAUSAL REASONING

## Panel: Causal Inference and Probabilistic Modeling Specialists

Convene:
- **Judea Pearl** — structural causal models, do-calculus, interventions
- **Clark Glymour** — causal discovery, PC algorithm, graph search
- **Richard McElreath** — statistical rethinking, Bayesian workflow, causal salad
- **Andrew Gelman** — Bayesian data analysis, model checking, garden of forking paths

## Questions to Address

1. **DAG Construction from Text**: The system extracts causal claims from text and assembles them into DAGs. But causal direction is notoriously hard to determine from correlational studies (most CNFA research). How does the system decide edge direction? If a paper reports "ceiling height was associated with creativity," does that become ceiling_height → creativity? What prevents the DAG from encoding correlational findings as causal?

2. **Causal Sufficiency**: Pearl's framework assumes causal sufficiency (no unmeasured common causes). In CNFA, unmeasured confounders are ubiquitous (socioeconomic status, personality, prior experience, cultural background). The DAG pretends these don't exist unless someone has studied them. How does the system represent causal uncertainty?

3. **Parameter Learning**: The BN has structure (DAG topology from extracted claims). But does it have parameters (conditional probability tables)? If so, where do they come from? If the BN is purely structural (qualitative), what kind of queries can it answer?

4. **Contradictory Edge Directions**: Paper A says ceiling_height → creativity. Paper B says creativity → ceiling_height_preference (creative people seek out high ceilings). The web has both. What happens in BN assembly? Is there a cycle resolution mechanism?

5. **What Queries Can Users Actually Ask?**: What can you DO with the assembled BN? Intervention queries ("what happens if we raise ceilings?")? Counterfactual queries ("would this patient have recovered faster in a room with a view?")? Or just conditional probability queries ("given high ceiling, what's the probability of increased creativity?")? The answer determines whether the system is useful for design decisions or only for theoretical understanding.

---

# REVIEW DIMENSION 7: SECURITY, DATA INTEGRITY, AND REPRODUCIBILITY

## Panel: Systems Reliability and Data Integrity Specialists

Convene:
- **Leslie Lamport** — distributed systems, formal verification, correctness
- **Peter Chen** — data modeling, entity-relationship integrity
- **A research data management specialist** — FAIR principles, provenance, reproducibility

## Questions to Address

1. **Provenance Tracking**: Every claim in the web came from a specific paper, extracted by a specific version of the pipeline, scored by a specific version of the validity framework. Is this provenance fully tracked? If a claim's score changes, can you trace WHY — which weight changed, which method profile was updated, which new paper triggered re-convergence? Without this, the system is a black box.

2. **Extraction Reproducibility**: If you run the same paper through the extraction pipeline twice, do you get identical claims? If extraction uses an LLM (which it likely does), outputs are stochastic. Two runs on the same paper could produce different claims, different argument_for assignments, different pathway classifications. How is this non-determinism handled? Is there a canonical extraction that gets frozen?

3. **Web State Versioning**: The web evolves as papers are added. Is there a version history? Can you roll back to the web state before a problematic paper was ingested? Can you diff two web states to see what changed? Without versioning, a single bad extraction can silently corrupt the web and there's no way to undo it.

4. **Input Validation and Adversarial Robustness**: What happens if someone feeds the system a retracted paper? A predatory journal paper? A paper that's been cited 5000 times but for being wrong (e.g., Bem's precognition study)? Does the system have any defense against low-quality input beyond the source_quality scoring, which only works after extraction?

5. **Configuration Integrity**: The system has dozens of configurable parameters (weights, thresholds, defaults). If someone accidentally changes the coherence_audit threshold from 0.1 to 0.01, the system will flag everything as coherence drift. Is there validation on configuration values? Are defaults documented with rationale? Is there a "known good" configuration that can be restored?

6. **Concurrent Modification**: If multiple users (or multiple pipeline instances) are adding papers to the web simultaneously, is there a concurrency model? Can two constraint satisfaction runs interfere with each other? Is the web thread-safe?

---

# REVIEW DIMENSION 8: USER INTERFACE AND EXPERIENCE

## Panel: HCI and Information Visualization Specialists

Convene:
- **Ben Shneiderman** — information visualization, direct manipulation, visual analytics
- **Tamara Munzner** — visualization design, task abstraction, evaluation
- **Don Norman** — design of everyday things, human error, cognitive engineering (and the developer's UCSD colleague and co-author)

## Questions to Address

1. **What Does the User Actually See?**: The system description is entirely backend — data structures, algorithms, scores. But what is the USER INTERFACE? A command-line tool? A web dashboard? A graph visualization? A report generator? If the interface doesn't exist yet, this is a serious gap — the most sophisticated backend is useless if researchers can't interact with it.

2. **Communicating Uncertainty**: The system produces multi-dimensional confidence scores (coherence, source quality, Bayesian, meta-epistemic). How are these communicated to a researcher who doesn't understand Quinean epistemology? If the system says "claim X has entrenchment 0.73, source quality 0.45, ecological validity 0.3" — what does the researcher DO with that? Is there a translation layer between internal scores and user-facing confidence?

3. **Explainability**: When the system rates a claim as low-confidence, can it explain WHY in terms a domain researcher understands? "This claim scores low because: (a) the only supporting study used photographs (presentation validity penalty), (b) participants rated preferences rather than performing ecological tasks (task-ecological validity penalty), (c) the study has not been independently replicated." That's useful. Raw scores are not.

4. **The Overwhelming Complexity Problem**: The system has at minimum: 7 link types, 4 epistemic templates, 5 source quality dimensions, 5 ecological validity components, 4 reflexive monitors, 5 auto-challenges, 3 pathway types, 3 PE subtypes, 2 claim types, 5 task classes. That's ~50 conceptual categories a user must understand. Is this manageable? How does the system introduce its own complexity without overwhelming the user?

5. **Progressive Disclosure**: Can the user start simple ("show me what the evidence says about biophilic design") and drill down into complexity only when needed? Or must they understand the full framework to use the system at all?

---

# REVIEW DIMENSION 9: THE BIG PICTURE — IS THIS ENTERPRISE SOUND?

## Panel: Senior Advisors

Convene:
- **Herbert Simon** — bounded rationality, satisficing, sciences of the artificial
- **Vannevar Bush** — "As We May Think," information systems, the memex vision
- **Douglas Engelbart** — augmenting human intellect, bootstrapping, tool-building
- **Thomas Kuhn** — paradigm shifts, normal science, incommensurability
- **The developer's own inner skeptic** — the voice that wakes you at 3am wondering if this whole thing is over-engineered nonsense

## Questions to Address

1. **The Ambition/Execution Gap**: This system attempts to simultaneously solve: PDF information extraction, scientific claim normalization, causal graph assembly, coherence-based belief revision, Bayesian network construction, methodological quality assessment, reflexive epistemic monitoring, and user-facing evidence synthesis. Each of these is a research problem in its own right. Is the system trying to do too many hard things at once? Would it be better to do ONE of these things really well?

2. **The 500-Paper Test**: Realistically, how many papers will this system process in its first year? 50? 200? 500? At 50 papers, is the web dense enough for coherence reasoning to be meaningful? At 500 papers, can a human still understand what the system is doing? What's the minimum viable corpus size?

3. **Validation Strategy**: How will anyone know if Article Eater is producing good results? Is there a gold standard? Could you take 20 well-understood CNFA claims, feed the system the underlying papers, and check whether its confidence ratings match expert consensus? Has this been planned?

4. **The Competition**: What existing tools do something similar? How does Article Eater compare to: (a) Semantic Scholar's citation graph, (b) Elicit's literature synthesis, (c) Consensus.app, (d) standard systematic review methodology with GRADE quality ratings, (e) a domain expert with a spreadsheet? What does Article Eater provide that these don't? Is the added complexity justified by the added value?

5. **Bus Factor**: One professor designed the theoretical framework, the implementation architecture, the methodology, and the domain application. Claude Code is implementing it from detailed specs, Codex is processing PDFs. If the professor walks away, can anyone else understand, maintain, or extend this system? Is there documentation adequate for a new developer to onboard?

6. **The Honest Value Proposition**: Strip away the sophisticated epistemology. What does this system actually DO for a CNFA researcher that they can't do today? If the answer is "produces a confidence-calibrated synthesis of the literature that's more systematic than a narrative review and more nuanced than a meta-analysis" — is that valuable enough to justify this level of complexity?

7. **What Would Kill It?**: What are the failure modes that would render the system useless? (a) Extraction accuracy too low? (b) Web too sparse for coherence reasoning? (c) Users don't trust automated quality assessment? (d) The field moves faster than the system can ingest? (e) A simpler approach works just as well?

8. **The Simpler Baseline Test**: Imagine a spreadsheet with columns: Claim, Supporting Papers, Study Design, Sample Size, Replicated?, Effect Size. A domain expert fills it in manually for 200 key claims in CNFA. Compare this to Article Eater's output for the same 200 claims. What does Article Eater's output contain that the spreadsheet doesn't? Is the delta worth the engineering cost? This is the test the system must pass.

9. **Domain Lock-In vs. Generalizability**: The system is built for CNFA specifically. But the architecture (Quinean web + source quality + BN assembly + reflexive monitoring) is domain-general. Is CNFA the right pilot domain? It's small (~2000 papers), interdisciplinary (architecture + neuroscience + psychology), methodologically diverse (photos to fMRI), and has known quality problems. These make it a good testbed. But they also mean the corpus may be too small for coherence reasoning to work. Would the system be more convincing on a larger, more mature literature?

---

# FINAL ASSESSMENT

After completing all seven dimensions, provide:

1. **The Three Most Critical Problems** — things that must be addressed or the system fails
2. **The Three Most Impressive Strengths** — things the system gets genuinely right
3. **The Single Hardest Question** — the one question the developer most needs to sit with
4. **Recommended Next Steps** — prioritized list of what to do first, second, third
5. **Overall Verdict** — on a scale from "abandon this" through "promising but fragile" through "this could actually work" to "this is genuinely important" — where does Article Eater sit, and why?

---

# APPENDIX: HOW TO USE THIS PROMPT

## For Claude (claude.ai or Claude Code)
Paste this entire document. If you have access to the codebase, say: "Read the codebase first. Then work through the review." If not, work from the system description.

## For Gemini (Antigravity or Gemini CLI)
Paste this document. Point it at the codebase if available. Say: "Read every Python file before starting the review. I want you to review actual code, not just specs."

## For ChatGPT
Paste this document. Upload relevant codebase files if possible. Note: ChatGPT may need the review broken into sections due to output length limits.

## For Multiple Reviewers
Run the same prompt through all three systems independently. Then compare their findings. Where all three agree, you have a high-confidence finding. Where they disagree, you have an interesting question to investigate.

## For Human Reviewers
This prompt works for humans too. The panel structure can be used as a checklist of concerns. Ignore the "convene panelists" framing and just address the questions under each dimension.
