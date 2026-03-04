# PART XXV: Writing and Communication Infrastructure

**Last updated:** 4 March 2026
**Section numbers:** §168–§173
**Word count:** ~5,400

---

## §168 Introduction: Why a Research System Needs a Writing Theory

Most knowledge engineering systems treat text generation as a formatting problem: the system knows things, and the output layer renders that knowledge as prose. ATLAS takes a fundamentally different position. How something is written determines what the reader can learn from it. Poorly constructed prose does not merely annoy; it actively obstructs understanding, misrepresents epistemic status, and undermines the trust that is the currency of scientific communication.

This Part documents the writing infrastructure that governs all ATLAS prose output — from QA answers to master document sections to formal papers. The infrastructure has three layers: a normative foundation (§169), an automated diagnostic service (§170), and an integration architecture that embeds prose quality into the system's operational pipeline (§171). The guiding decision is that writing quality is not a cosmetic concern to be addressed at the end of a project but a structural property to be engineered into the system from the beginning.

---

## §169 Science Communication Norms: The Normative Foundation

The normative layer consists of twelve writing principles, each grounded in a named practitioner of science communication or writing research. The decision to anchor norms in named practitioners rather than abstract principles reflects a commitment to provenance: every rule in the system should be traceable to a source, and writing rules are no exception. The twelve norms are documented in full in `contracts/SCIENCE_COMMUNICATION_NORMS.md`; here we summarize the architecture and the rationale for the selection.

### §169.1 The Reference Group

The ten writers and writing researchers were selected because each has articulated not only what good science writing looks like but *why* specific techniques work — grounding their advice in cognitive science, psycholinguistics, or extensive empirical observation:

Steven Pinker (Harvard) contributes the concept of *classic style* — writing as showing the reader something rather than performing expertise — and the *curse of knowledge* diagnostic, which identifies places where the writer assumes knowledge the reader does not have (Pinker, 2014). Joseph Williams (University of Chicago) provides the two foundational sentence-level principles: the *Given-New contract* (begin with familiar information, end with new) and the *stress position* (readers treat the end of a sentence as the point of emphasis) (Williams & Bizup, 2016). Richard Lanham (UCLA) provides the *Paramedic Method*, an eight-step revision procedure that systematically removes nominalized, passive, bloated academic prose (Lanham, 2006). Helen Sword (Auckland) provides the *Writer's Diet* diagnostic — a five-category word health test grounded in the largest empirical study of academic writing style ever conducted (Sword, 2012).

The remaining six practitioners address article-level architecture: Oliver Sacks demonstrated that neurological mechanisms become comprehensible when embedded in the texture of a patient's lived experience. Carl Sagan contributed *scale bridging* and *honest uncertainty* — admitting what science does not know strengthens rather than weakens a text. Ed Yong represents current best practice in *slow complexity building* — introducing one concept at a time through concrete examples. Atul Gawande provides *narrative arc* — the dramatic structure that makes evidence not just intelligible but compelling. Rachel Carson pioneered *ethical embedding* — conveying moral implications through sensory immersion rather than sermonizing. Jean-Luc Doumont brings engineering discipline: *structure is communication* — how content is organized conveys meaning as strongly as the content itself (Doumont, 2009).

### §169.2 The Twelve Norms

The norms fall into three categories corresponding to the three-pass revision protocol:

**Structural norms** (Pass 1, Doumont): (1) Classic style — write as a guide, not a lecturer (Pinker). (2) Structure as communication — organization carries meaning (Doumont). (3) Narrative threading — every section follows a dramatic arc (Gawande/Sacks).

**Sentence-level norms** (Pass 2, Lanham + Williams): (4) Given-New contract — begin sentences with familiar information (Williams). (5) Stress position — end sentences with the point of emphasis (Williams). (6) Kill zombie nouns — replace nominalizations with active verbs (Lanham/Sword). (7) Paramedic Method — systematic lard removal on revision (Lanham).

**Knowledge-curse norms** (Pass 3, Pinker): (8) Curse of knowledge audit — identify terms and assumptions the reader does not share (Pinker). (9) Honest uncertainty — admit what is unknown, preliminary, or contested (Sagan). (10) Scaffolded explanation — one new concept at a time, always through a concrete example (Yong). (11) Defamiliarization — show the reader that something familiar is actually surprising (Yong/Sacks). (12) Ethical embedding — let moral implications emerge from the evidence rather than being asserted (Carson).

### §169.3 Design Decision: Norms as Binding Constraints

The decision to treat these norms as binding constraints rather than aspirational guidelines was deliberate. The alternative — treating prose quality as a "nice to have" — leads to the situation that Sword (2012) documented across 1,000 academic articles: poorly written papers are less cited, less understood, and less influential, regardless of the quality of their findings. Since ATLAS produces prose that must be understood by users ranging from 3rd-year undergraduates to domain experts, writing quality is a functional requirement, not a stylistic preference.

The norms connect to the existing writing infrastructure as follows: `WRITING_STYLE_GUIDE.md` provides sentence/paragraph/section mechanics. `MATH_EXPLANATION_NORMS.md` provides formula presentation standards. `SCIENCE_COMMUNICATION_NORMS.md` provides article-level architecture and the revision protocol. `EPISTEMIC_PRINCIPLES.md` (Principles 11–17) provides epistemic content norms for QA answers. Together these four documents form a layered writing specification from the sentence to the document level.

---

## §170 The Prose Revision Service: Automated Diagnostics

The normative foundation would be merely aspirational without an enforcement mechanism. The Prose Revision Service (`src/services/prose_revision_service.py`, 956 LOC, 55 tests) is the operational implementation: a real-time prose diagnostic engine that converts the twelve science communication norms into quantitative, automated checks.

### §170.1 Architecture

The service implements the three-pass revision protocol as a composable set of diagnostic functions:

**Pass 1 — Structural audit (Doumont).** Checks heading informativeness (do headings state findings or merely name topics?), paragraph length distribution (flagging under-4 and over-7 sentence paragraphs), first-sentence/last-sentence coherence (does each paragraph open with its point and close with its "so what"?), and section flow (are sections connected by bridging sentences?).

**Pass 2 — Sentence-level diagnostics (Lanham + Williams).** Implements six quantitative detectors: (a) nominalization density — counts zombie nouns (words ending in -tion, -ment, -ness, -ity that could be verbs) per 100 words; (b) passive voice frequency — identifies passive constructions via auxiliary + past participle patterns; (c) hedge stack detection — finds sequences of more than two hedging expressions ("It might be possible that perhaps..."); (d) throat-clearing — identifies meta-commentary that delays the point ("In this section, we will discuss..."); (e) sentence length distribution — flags sentences exceeding 40 words; (f) weak opener detection — counts sentences beginning with "It is," "There are," "This is."

**Pass 3 — Knowledge-curse audit (Pinker).** Identifies undefined abbreviations (first use of a term without expansion), jargon density (technical terms per 100 words), citation clusters (more than 3 consecutive citations without prose), and overclaiming (strong causal language paired with weak evidence markers).

### §170.2 Quantitative Scoring

Each diagnostic produces a severity-tagged finding (INFO, ADVISORY, WARNING, CRITICAL). The service aggregates these into a composite prose health score on a 0–10 scale, where thresholds are context-sensitive:

For QA responses, the threshold is lenient (score ≥ 5.0 is acceptable) because these are short, informal, and generated under latency constraints. For master document sections, the threshold is moderate (≥ 6.5). For formal papers, the threshold is strict (≥ 7.5). These thresholds were calibrated against David Kirsh's explicit feedback on prose quality during the Goldilocks paper revision (March 2026).

### §170.3 Sword's Writer's Diet

The service independently implements Sword's Writer's Diet diagnostic, which counts five categories of words — "be" verbs, abstract nouns, prepositions, adjectives/adverbs, and impersonal openers ("it," "this," "there") — and classifies each as Fit, Needs Toning, Flabby, or Heart Attack. High concentrations of any category signal sick prose. This provides a quick-check complement to the more detailed three-pass analysis.

### §170.4 Lanham's Lard Factor

The lard factor estimates the percentage of words in a passage that carry no semantic information — filler, redundancy, throat-clearing, and padding. Typical academic prose runs 50–70% lard (Lanham, 2006). ATLAS targets ≤15% for formal papers and ≤20% for internal documentation. The service computes an approximate lard factor by identifying common filler patterns and computing their proportion of total word count.

### §170.5 Applied Example: Goldilocks Paper Revision

The service was applied to the full Goldilocks Principle paper draft (18,750 words). Results: 33 critical issues, 113 warnings, nominalization density 5.0/100 words, passive voice 11%, lard factor 12%. A side-by-side revision document was produced showing 10 representative passages with original prose, diagnostic annotations citing the specific norm violated, and revised prose. Estimated improvement: nominalization density 5.0 → ~3.2/100. The revision document demonstrates that the diagnostics produce actionable, specific guidance rather than generic "write better" advice.

---

## §171 Integration Architecture

The prose revision service is not a standalone tool; it is wired into the ATLAS operational pipeline at two integration points.

### §171.1 QA Pipeline Integration

The `arbitrary_qa_handler.py` accepts an `enable_prose_review=True` flag. When enabled, every QA response passes through the prose revision service before being returned to the user. The service adds a `prose_review` field to the response containing the composite score, verdict (PASS/ADVISORY/FAIL), and the top 3 specific suggestions for improvement. This is non-blocking — QA responses are always returned, but the prose review metadata enables downstream monitoring of answer quality.

### §171.2 Answer Enrichment Pipeline

The answer enrichment orchestrator (`answer_enrichment_orchestrator.py`) can invoke prose review as one of its optional enrichment steps. This allows prose diagnostics to be applied selectively: enabled for complex, multi-paragraph answers; disabled for brief factual responses. The enrichment step adds prose health metrics to the answer metadata, which the overseer can aggregate for nightly quality reports.

### §171.3 Design Decision: Advisory, Not Blocking

The decision to make prose review advisory rather than blocking was deliberate. Blocking on prose quality would add unacceptable latency to the QA pipeline (the three-pass analysis takes 200–500ms on a long answer). More importantly, blocking would prevent the system from returning answers that are substantively correct but stylistically imperfect — a worse outcome than returning imperfect prose with attached diagnostic metadata. The overseer monitors aggregate prose quality trends and can trigger systematic revision campaigns when quality degrades across the corpus.

---

## §172 The Smart Book: Dependency-Aware Documentation Validation

*Added 2026-03-04.*

The master document, at 21 Parts and ~25,000 words, contains numerous cross-cutting concepts (the count of T1.5 theories, the credence formula, AESHI subscores) that appear in multiple sections. When one section updates a number or definition, other sections may become inconsistent. The Smart Book is a machine-readable dependency tracking system that catches these inconsistencies automatically.

### §172.1 Architecture

The system has two components. The **Dependency Manifest** (`docs/master_doc_parts/DEPENDENCY_MANIFEST.json`) is a JSON file that declares which Parts reference which cross-cutting concepts and what the canonical values are. It tracks 10 core concepts including T1.5 theory count, T1 framework count, credence formula version, AESHI subscores, and Q-norm count. Each concept entry specifies the canonical value, the source Part (where the concept is defined), and the dependent Parts (where the concept is referenced).

The **Validation Script** (`scripts/validate_master_doc.py`, 21KB) reads the manifest and all 21 Parts, checks for count mismatches, stale cross-references, undefined concepts, and sections that need review after upstream changes. It produces a severity-graded report (CRITICAL, MEDIUM, LOW) identifying exactly which lines in which Parts contain values that no longer match the canonical source.

### §172.2 Design Decision: Why a Manifest Rather Than Inline Markers

The alternative approach — embedding dependency markers directly in the master doc text (e.g., `{{T1.5_COUNT}}` placeholders) — was rejected because it would make the prose unreadable to human authors. The manifest approach keeps the master doc as clean prose while maintaining a parallel machine-readable dependency graph. The cost is that the manifest must be updated manually when new cross-cutting concepts are introduced, but this is a small burden compared to the benefit of catching silent inconsistencies in a 25,000-word document.

---

## §173 The Card Architecture: Epistemic Loci and Source Cards

*Added 2026-03-04.*

The ATLAS system generates two fundamentally different kinds of knowledge artifacts, and conflating them produces both architectural confusion and epistemic error. The distinction — between what we now call *source cards* and *epistemic loci* — reflects the difference between what a single study contributes and what the system collectively understands about a question.

### §173.1 Source Cards

A source card is tied to an individual article extraction. It captures what one study contributes to the web of belief: a finding, an effect size, a methodological qualification, a population scope. Source cards are the atomic units of evidence. Their provenance is unambiguous — each traces to a specific article, a specific extraction, a specific warrant type. When the backing article is retracted or superseded, the source card is revised or deprecated. Source cards are numerous (the system currently holds >12,000 T3 beliefs, each potentially generating one or more source cards) and relatively stable: a study's findings do not change, though their interpretation may.

### §173.2 Epistemic Loci

An epistemic locus (plural: *loci*) is the organized understanding that emerges when multiple source cards are synthesized around a coherent question or theme. The term draws on the Latin *locus* — a point or region in a space defined by a set of conditions — and on Aristotle's *topoi* (Topics, Book I), where a topos is a "place" in conceptual space around which arguments converge. An epistemic locus is precisely this: a region of the belief web where multiple beliefs, warrants, and evidential connections converge around a thematic question, such as "How does visual exposure to nature affect stress physiology?" or "What is the evidence for circadian disruption from artificial lighting?"

Unlike source cards, epistemic loci are synthetic. They aggregate across dozens of extractions, weigh conflicting evidence, track the current credence, identify active frontiers and unresolved tensions, and present the system's *position* on a topic — not a single study's contribution. An epistemic locus has internal structure: sub-questions (facets), competing interpretations, scope conditions, and confidence gradations. It is the unit at which the system's understanding can be interrogated by a user who wants to know not "what did Smith et al. (2019) find?" but "what does the evidence say about X?"

### §173.3 The Three-Zone Architecture

Each epistemic locus is organized into three zones, reflecting the distinction between stable knowledge and volatile evidence:

**Zone 1: Committed Prose.** The locus's current answer — a paragraph or short section of flowing academic prose that synthesizes the evidence, acknowledges uncertainty, and presents the system's current position. This zone is written at high quality (prose health score ≥ 6.5) and is the primary user-facing artifact. It changes only when the evidence base shifts enough to alter the position.

**Zone 2: Flagged Developments.** A structured diff layer that tracks recent changes to the backing evidence since the committed prose was last generated. New supporting studies, contradictory findings, methodological critiques, and scope expansions are logged here as dated entries. When the accumulated flagged developments are substantial enough to potentially alter the committed prose (a threshold determined by staleness scoring; see §173.4), the locus is queued for regeneration.

**Zone 3: Source Map.** A dependency graph linking the locus to its backing source cards, warrant types, T2 templates, and T1 framework connections. This zone is machine-readable and provides the provenance chain that makes the committed prose epistemically auditable. A reviewer can trace any claim in Zone 1 back through Zone 3 to the specific articles that support it.

### §173.4 Staleness Scoring and Regeneration

An epistemic locus becomes stale when its backing evidence has changed enough that the committed prose may no longer accurately represent the system's understanding. Staleness is computed as a weighted function of three factors: (a) the number of new source cards added since last generation, weighted by their credence and warrant type; (b) the magnitude of credence shifts in backing T2 templates; and (c) the resolution of previously unresolved competitions relevant to the locus. When staleness exceeds a configurable threshold (default: 0.40 on a 0–1 scale), the locus is queued for regeneration.

Regeneration is a two-step process. First, the system re-synthesizes the evidence from Zone 3, incorporating all Zone 2 flagged developments. Second, the committed prose (Zone 1) is rewritten — ideally by an Opus-class model for theoretical loci, or a Sonnet-class model for engineering loci (see §173.5). The previous committed prose is archived for version comparison.

### §173.5 Model Allocation for Card Generation

Empirical comparison (March 2026) of Opus and Sonnet models writing identical fattening inserts for §129.2 (Typed Credence Propagation) revealed a consistent pattern: Opus produces deeper philosophical grounding, richer cross-reference to named intellectual traditions, and more authoritative academic prose, but occasionally hallucinates bibliographic entries. Sonnet produces tighter, more efficient prose with reliable references and sharper engineering insights, but thinner philosophical development. The recommended workflow allocates Opus to epistemic loci that are primarily theoretical (e.g., "Why does the system use typed warrants?" or "What is the relationship between coherentism and foundationalism in ATLAS?") and Sonnet to loci that are primarily engineering-focused (e.g., "How does the credence propagation algorithm handle multi-parent nodes?" or "What is the computational complexity of the coherence metric?"). All Opus outputs require a reference-verification pass.

### §173.6 Design Decision: Why "Epistemic Loci"

The term was chosen over several alternatives — "belief kernels," "belief constellations," "dossiers," "topoi" — for three reasons. First, *locus* preserves the spatial metaphor that the web-of-belief architecture already employs: a locus is literally a place in the web where inquiry converges. Second, the mathematical resonance is useful: a locus is a set of points satisfying a condition, and an epistemic locus is the set of beliefs satisfying a thematic coherence condition. Third, the term is semantically transparent in academic writing — any reader with Latin or mathematical training will parse it immediately — without carrying the domain-specific baggage of "topos" (which also denotes a category-theoretic construct) or the operational connotations of "dossier" (which suggests intelligence analysis rather than epistemic synthesis). The pairing of "epistemic loci" with "source cards" creates a clean two-level vocabulary: source cards are atomic evidence units; epistemic loci are the structured places where that evidence converges into understanding.

---

## References

Borsboom, D., Mellenbergh, G. J., & van Heerden, J. (2003). The theoretical status of latent variables. *Psychological Review*, 110(2), 203–219. https://doi.org/10.1037/0033-295X.110.2.203

Carson, R. (1962). *Silent Spring*. Houghton Mifflin.

Doumont, J.-L. (2009). *Trees, maps, and theorems: Effective communication for rational minds*. Principiae.

Gawande, A. (2009). *The checklist manifesto: How to get things right*. Metropolitan Books.

Lanham, R. A. (2006). *Revising prose* (5th ed.). Longman.

Pinker, S. (2014). *The sense of style: The thinking person's guide to writing in the 21st century*. Viking.

Sagan, C. (1980). *Cosmos*. Random House.

Sword, H. (2012). *Stylish academic writing*. Harvard University Press.

Williams, J. M., & Bizup, J. (2016). *Style: Lessons in clarity and grace* (12th ed.). Pearson.

Yong, E. (2022). *An immense world: How animal senses reveal the hidden realms around us*. Random House.
