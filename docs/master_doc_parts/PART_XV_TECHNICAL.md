# PART XV: TECHNICAL IMPLEMENTATION (§119-124)

{#part-xv}

### Executive Summary

The ATLAS system is implemented across three integrated repositories: Article_Eater (V22.0.0, extraction and evidence aggregation) provides the raw evidence; BN_graphical (Bayesian network inference) translates templates into predictions; web_of_belief.py (coherence computation) manages belief revision. Part XV documents the technical architecture, computational pipeline, quality assurance protocols, gap tracking, and system visualization. The extraction pipeline uses Gemini Flash PDF native support to process 1,041 papers at minimal cost (~$3 total). The QA agent enforces schema validation, bridge warrant ceilings, variable registration, and provenance verification. The 153-gap tracker prioritizes investigation. Visualization tools include architecture layer diagrams, theory dependency DAGs, and template interaction networks.

### § 119: Unified Variable Vocabulary {#§119}

**Purpose**: Every variable in the system (whether in templates, mechanism chains, parameters, or computational logic) must be registered in a unified vocabulary. This prevents naming collisions, enables cross-repository alignment, and supports variable dependency tracking.

**Schema for Each Variable**:

```
variable_id: unique identifier (e.g., V_AROUSAL_SYMPATHETIC)
name: human-readable name (e.g., "Sympathetic Arousal Level")
aliases: alternative names (e.g., ["stress response", "fight-or-flight activation"])
type: variable type (categorical, continuous, ordinal)
domain: which domain(s) it belongs to (e.g., NEUROMOD-I, STRESS-I)
provenance: origin (article reference, expert attribution, theoretical)
unit: measurement unit (Likert scale 1–7, dB, ms, etc.)
constraints: valid range or values
dependencies: other variables it depends on
definitions_across_papers: how different papers define/measure this variable
registration_date: when added to vocabulary
status: registered, deprecated, under-review
```

**Current Status**:

- **Registered variables**: ~500 across all domains
- **Unregistered (identified in audit)**: 272 variables used in mechanism chains but not registered
- **Priority**: Register all 272 before next calibration panel

**Example Variables**:

- **V_THREAT_SALIENCE**: Conscious or unconscious perception of environmental hazard. Measured as: amygdala fMRI activation (neural), startle reflex magnitude (physiological), subjective threat rating (subjective). Different papers use different measures; vocabulary maps them.

- **V_PREDICTION_ERROR**: Surprise or mismatch between expected and observed state. Measured as: dACC activity (fMRI), late positive potential (ERP), neural adapta (single-unit recording), subjective surprise rating. Theoretical definition: P(observed | prior expectations) for Bayesian formalism.

---

### § 120: Computational Architecture (Four Core Services) {#§120}

**Service 1: web_of_belief.py** (Belief Management, Coherence, Constraint Satisfaction)

- **Function**: Maintains a network of beliefs (propositions derived from evidence) and computes coherence using constraint satisfaction.
- **Input**: Template predictions, evidence data, coherence weights (which beliefs support/contradict each other).
- **Output**: Coherence score, belief revision recommendations, conflict identification.
- **Technology**: Python, NetworkX (graph), scipy.optimize (constraint satisfaction).

**Service 2: interpretive_intelligence.py** (Mechanism Chain Traversal, Explanation Generation)

- **Function**: Traverses mechanism chains step-by-step, generating explanations for predictions.
- **Input**: Template, mechanism chain, Toulmin justification data.
- **Output**: Natural language explanation (human-readable summary of why prediction is made), step-wise confidence breakdown, rebuttal generation.
- **Technology**: Python, template-based text generation (Jinja2), logic programming (basic rule engine).

**Service 3: epistemic_causal_bridge.py** (Web→BN Conversion, Relevance Propagation)

- **Function**: Converts abstract beliefs (from web_of_belief) into Bayesian network structure, enabling probabilistic inference.
- **Input**: Belief network with coherence weights, template confidence values, conditional dependencies.
- **Output**: Bayesian network nodes and edges, conditional probability tables (CPTs), inference-ready graph.
- **Technology**: Python, pgmpy (Bayesian networks), Pearl do-calculus (prototype, not fully implemented).

**Service 4: Template Persistence (JSON Storage, Schema Validation)**

- **Function**: Stores, retrieves, and validates templates in JSON format.
- **Input**: Template JSON files (51 calibrated), schema specification.
- **Output**: In-memory template objects, validation errors, provenance tracking.
- **Technology**: Python, JSON schema validation (jsonschema library), versioning (git-tracked).

**System Diagram** (Architecture Layers):

```
Layer 7: Design Recommendations & Visualization
         [Architectural Specifications] [Design Checklists] [Visualizations]
                    ↓
Layer 6: Prediction & Inference
         [BN Inference Engine] [Scenario Simulation] [Confidence Aggregation]
                    ↓
Layer 5: Mechanism & Explanation
         [Mechanism Chain Traversal] [Toulmin Justification] [Natural Language Output]
                    ↓
Layer 4: Template Library & Coherence
         [web_of_belief.py] [103 Calibrated + 105 Scaffold] [Belief Revision]
                    ↓
Layer 3: Evidence Integration & Staging
         [Staging Database] [Evidence Aggregation] [Cross-Study Synthesis]
                    ↓
Layer 2: Extraction Pipeline
         [Gemini Flash PDF Processing] [Entity Recognition] [Metadata Extraction]
                    ↓
Layer 1: Raw Evidence Corpus
         [1,041 Scientific Papers] [PDF Files] [Extraction Logs]
```

---

### § 121: Extraction Pipeline {#§121}

**Overview**: Converts raw scientific papers into structured evidence suitable for template calibration.

**Five Article-Type Templates**:

1. **Empirical** (experiments, RCTs, quasi-experiments): Extract outcome measures, effect sizes, sample sizes, methods.
2. **Meta-Analysis**: Extract pooled effect sizes, heterogeneity (I²), funnel plots, publication bias analysis.
3. **Theoretical**: Extract conceptual definitions, hypothesized mechanisms, qualitative reasoning.
4. **Qualitative** (interviews, ethnography): Extract themes, codes, illustrative quotes.
5. **Narrative Review**: Extract integrated synthesis of literature, expert commentary.

**Gemini Native PDF Pipeline** (Replacing OCR):

- **Previous approach**: PDF → OCR (Tesseract) → text extraction → entity recognition. Slow (3–5 hours for 100 papers), error-prone (OCR artifacts).

- **New approach** (Feb 2026): PDF → Gemini Flash 1.5 native PDF support → structured JSON extraction. Fast (1–2 minutes for 100 papers), accurate (Gemini understands figures, tables, complex layouts).

- **Cost**: Gemini Flash pricing ~$0.075 per 1 million input tokens. Processing 1,041 papers (~500M tokens total): ~$40. **Actual cost (Feb 2026)**: ~$3 due to batch processing and student-rate discounts.

**Processing Steps**:

1. **Title/Abstract Screening** (automated): Gemini Flash scans titles/abstracts, classifies by relevance to environmental psychology. Filters out non-relevant papers (medical, engineering, unrelated psychology). Throughput: 1,041 papers → ~800 relevant.

2. **Full-Text Extraction** (Gemini Flash, JSON output):
   - If article is **empirical**: Extract {study_design, sample_size, outcome_measure, effect_size_d, CI, p_value, population_description, methodology_notes}.
   - If article is **meta-analysis**: Extract {pooled_effect_size, heterogeneity_I_squared, publication_bias_assessment, number_of_studies, moderator_analysis}.
   - If article is **theoretical**: Extract {key_hypotheses, proposed_mechanisms, conceptual_definitions, future_research_needs}.

3. **Staging Database Population** (Python): Structured JSON entries are parsed, deduplicated, and entered into staging database (PostgreSQL). Each entry linked to original PDF, extraction timestamp, confidence level (automated confidence based on Gemini's extraction confidence scores).

4. **Centrality Weighting** (computational): Articles are weighted by how central they are to environmental psychology. Highly cited articles (>100 citations per Google Scholar) weighted 1.5×; recent articles (within 2 years) weighted 1.2×. This prevents old, influential papers from dominating and recent empirical work from being underweighted.

5. **Article Adequacy Grading** (expert review): Each article is graded A–F on methodological rigor, relevance, and clarity. Grade feeds into template calibration (A-rated papers more influential in panel decisions).

**Validation**:

After pipeline completion, metadata quality is verified:

- Missing fields checked (allow missing, but flag them)
- Effect sizes out of range (|d| > 2.0) flagged for manual review
- Sample sizes <10 flagged as potentially underpowered
- Extraction completeness (≥70% of key fields populated): required for downstream use

**Output**: 227K JSON entries (~1,200 unique articles after deduplication, with 185 redundant entries representing same study reported across multiple papers).

---


# Article Finding and PDF Extraction Pipeline: Comprehensive System Documentation

**For the ATLAS system Master Paper — Upstream Infrastructure Systems**

*February 24, 2026*
*Prepared by Claude Code for Professor David Kirsh*

---

## Overview

The ATLAS system (Cognitive, Motor, Responsive) system is fundamentally a knowledge-extraction and integration pipeline. Evidence doesn't arrive pre-processed; the system must actively search for papers, retrieve them, extract claims from PDFs, and translate those claims into the structured vocabulary of the web of belief. This document describes the complete upstream infrastructure: how papers are discovered, why they are prioritized for retrieval, how findings are extracted from raw PDFs, and how the current pipeline both succeeds and fails.

The extraction pipeline is the weakest link in the entire system. Everything downstream—templates, predictions, design recommendations—depends entirely on the quality of what we extract. A system with flawless theoretical architecture but garbage input produces garbage output with high confidence. This is not a problem we can solve by improving downstream reasoning. It must be solved at the source.

---

## SECTION 1: Article Finding and VOI-Driven Literature Search


### §121.10: Article Type Classification and Type-Specific Extraction

#### 121.10.1 The Problem of Epistemic Heterogeneity

The environmental psychology literature is epistemically heterogeneous. The 1,041 papers in the current corpus are not all empirical studies reporting IVs, DVs, and effect sizes. They include meta-analyses (which report pooled effects across studies), systematic reviews (which synthesize evidence qualitatively), narrative reviews (which survey a topic without structured protocol), theoretical papers (which propose mechanisms without testing them), conceptual frameworks (which organize constructs), qualitative studies (which report themes, not statistics), and methodological papers (which propose measures or designs). The early extraction pipeline's most consequential error was treating all papers as though they were empirical studies with tabular statistical results. The consequence, diagnosed in Document 70 (February 2026), was systematic data corruption: when a theoretical paper was forced through an IV/DV extraction template, the system confidently extracted citation fragments as though they were findings, generating precisely the kind of noise-as-signal that the ATLAS's epistemic discipline was designed to prevent.

The solution is article-type-aware extraction: classify each paper before extracting from it, then apply a type-specific extraction schema that asks the right questions for that kind of paper.

#### 121.10.2 The Fifteen Article Types in Five Families

The system recognizes fifteen article types organized into five macro-families, each with its own extraction contract specifying required and optional fields. The taxonomy is implemented in `article_type_contract.py` and enforced throughout the extraction pipeline.

**Family 1: Empirical Studies** (4 types). This family includes experimental studies (`empirical_v2`), field observations (`observational_field`), case studies (`case_study`), and mixed-methods designs (`mixed_methods`). All four types share the same extraction contract: required fields are research_question, design_type, participants, stimuli_or_exposures, measures, findings, and limitations. Optional fields include mechanisms, moderators, and implementation_implications. The findings field is the critical one — it requires structured antecedent-consequent pairs with direction, effect_size, effect_size_type, p_value, sample_size, confidence_interval, theory_links (which T1 frameworks predict the observed effect), mechanism (theoretical explanation if stated), source (table or text location), and a supporting quote. The requirement that theory_links must be populated for every finding is a deliberate design decision: it forces the extraction to connect empirical observations to the theoretical architecture immediately, rather than deferring integration to a later stage where context is lost.

**Family 2: Synthesis Studies** (3 types). Meta-analyses (`meta_analysis`), systematic reviews (`systematic_review`), and narrative reviews (`narrative_review`) share a synthesis-oriented contract: required fields are review_question, inclusion_exclusion_criteria, evidence_base_summary, synthesis_conclusions, and evidence_gaps. Optional fields include pooled_effects (for meta-analyses, these are the primary data: pooled effect sizes with confidence intervals, heterogeneity statistics I², and moderator analyses), risk_of_bias_assessment, and heterogeneity_sources. The distinction between the three types matters for downstream credence assignment: a meta-analysis with k=30 studies and I²<25% warrants higher credence than a narrative review summarizing the same domain informally.

**Family 3: Theory Papers** (3 types). Theoretical papers (`theoretical`), conceptual frameworks (`conceptual_framework`), and thought pieces (`thought_piece`) share a proposition-oriented contract: required fields are central_proposition, concept_definitions, argument_structure, mechanism_or_causal_logic, and testable_hypotheses_or_predictions. Optional fields include bridge_warrants and methodological_critiques. This is where the system extracts theoretical claims that will become beliefs in the web of belief with THEORY_PROPOSAL epistemic status rather than EMPIRICAL_FINDING. The testable_hypotheses_or_predictions field is epistemically important: it identifies which predictions the theory makes that could be tested, feeding directly into the VOI scoring system (§47).

**Family 4: Qualitative Studies** (4 types). Interview studies (`interview_study`), ethnographic work (`ethnographic`), grounded theory (`grounded_theory`), and phenomenological studies (`phenomenological`) share a qualitative contract: required fields are research_focus, sample_context, data_collection_method, coding_or_analysis_approach, themes_or_constructs, supporting_quotes_or_evidence_snippets, and transferability_limits. Optional fields include derived_hypotheses and mechanism_candidates. Qualitative findings enter the web of belief as QUALITATIVE_FINDING nodes with a different credence calculus: they do not carry effect sizes but do carry transferability assessments and supporting quotes that can anchor theory building.

**Family 5: Unclassifiable** (1 type). Papers that cannot be classified (`unknown`) require only classification_diagnostics (why classification failed) and a minimum_safe_summary answering three of the eight universal questions: Q1 (core claim), Q4 (key findings), and Q5 (limitations). This ensures that even unclassifiable papers contribute something to the knowledge base without generating garbage through forced extraction.

#### 121.10.3 The Universal Question Set and Provenance Depth

Regardless of article type, the system asks eight universal questions of every paper: (Q1) What is the core claim or contribution? (Q2) What is being studied — constructs, entities, phenomena? (Q3) What evidence basis supports the claim? (Q4) What are the key findings or conclusions? (Q5) What are the boundary conditions or limitations? (Q6) What mechanisms or theoretical explanations are given? (Q7) How does this connect to prior work or competing findings? (Q8) What practical or scientific significance is stated? These eight questions are adapted from the Toulmin structure (claim, data, warrant, backing, qualifier, rebuttal) extended with a design-relevance question (Q8). Type-specific contracts then determine which of these questions receive structured extraction (with schema-enforced fields) versus free-text answers.

Every extracted field carries a provenance depth label indicating where in the source document the information was found: `abstract` (from abstract only — lowest confidence), `caption` (from figure or table captions), `table` (from statistical table bodies), `section` (from methods, results, or discussion text), `fulltext_multi` (corroborated from multiple full-text sections — highest confidence), or `external` (from citation metadata or API lookup). This provenance depth directly modulates downstream credence: a finding extracted from a statistical table at `table` depth warrants higher confidence than the same finding extracted from an abstract at `abstract` depth, because abstract-level extraction is vulnerable to selective reporting and simplification.

#### 121.10.4 Type-Specific Extraction Prompts

The Gemini Flash extraction uses different prompts for each article family. The empirical prompt asks for structured IV/DV pairs with exact statistics, effect sizes, and theory links. The meta-analysis prompt asks for pooled effects with k (number of studies), I² (heterogeneity), moderators, and publication bias assessments. The systematic review prompt asks for evidence strength ratings and gap identification. The theoretical prompt asks for argument structure and testable predictions. The qualitative prompt asks for themes, quotes, and transferability limits.

Each prompt includes the complete T1 framework vocabulary (PP, SN, DP, DT, NM, IC, MS, EC, CB, MSI) and the domain theory vocabulary (ART, SRT, Biophilia, Prospect-Refuge, Privacy Regulation) so that the LLM can immediately link extracted findings to the theoretical architecture. This is a critical design decision: by presenting the theoretical vocabulary at extraction time, the system ensures that the bridge between evidence and theory is constructed at the earliest possible stage, before context is lost.

#### 121.10.5 Two-Run Verification Protocol

To mitigate extraction errors, the pipeline runs each paper through extraction twice (run1 and run2) and compares results. Agreement between runs increases confidence; disagreement triggers either a third run (run3) or human review. The verification protocol checks: (a) do both runs extract the same number of findings? (b) do they agree on effect directions? (c) do they agree on theory links? (d) do effect size values fall within 10% of each other? Papers where both runs agree on all four criteria are marked COMPLETED with high confidence. Papers where runs disagree on direction or theory links are flagged NEEDS_VERIFICATION. This is computationally cheap (Gemini Flash costs $0.15/M input tokens) and catches the most consequential extraction errors — directional errors and theory misattribution — before they propagate into the web of belief.

#### 121.10.6 Quality Gates

Four quality gates prevent garbage from entering the knowledge base. First, reject forced mappings when extraction confidence is below the family's threshold. Second, reject self-matches where the extracted IV equals the DV (unless explicitly marked as a construct validity or identity study). Third, do not emit null fields as noise for families where the field is structurally irrelevant — a theoretical paper should never produce a null `effect_size` field, because effect sizes are not a meaningful concept for theoretical papers. Fourth, require at least one anchored evidence snippet (a direct quote from the source text) for each major extracted claim. These gates were implemented after the Doc70 diagnosis revealed that the pre-gate pipeline was generating 93% noise.

---


### §121.2: The Discovery Funnel — From Gap to Paper

The Article Eater system does not assume a fixed corpus of papers. Instead, it dynamically searches for papers that would fill specific knowledge gaps. The discovery funnel implements this workflow:

**VOI Gap Identified** (from template evaluation or web of belief coherence analysis) → **Search Strategy Selected** (by gap type and domain) → **Targeted Query Executed** (using cross-field vocabulary expansion) → **Articles Found** (ranked by relevance and gap-closure prediction) → **PDF Retrieved** (via direct link, Unpaywall, or Sci-Hub) → **Paper Ingested** (claim extraction) → **Gap Closure Assessed** (VOI before and after integration)

The funnel tracks six key metrics at each stage:

1. **Gap Status**: OPEN (not yet searched) → SEARCHING (queries running) → FOUND (articles located) → CLOSED (integrated into web)
2. **Search Yield**: How many papers were found per query (relevance rate)
3. **Retrieval Success**: What fraction of found papers had accessible PDFs
4. **Gap Closure Type**: FULL (VOI < 0.1 after integration), PARTIAL (≥30% VOI reduction), NONE (minor change), or NEGATIVE (uncertainty grew)
5. **Extraction Quality**: What fraction of retrieved papers produced acceptable structured claims
6. **Cost Accounting**: Total API credits used, time elapsed, cost per gap closed

The discovery funnel service (in `/src/services/discovery_funnel.py`) maintains a persistent database of all gaps, searches, retrieval attempts, and closures. This allows the system to learn: Which gap types have highest payoff? Which search strategies work best for which domains? How often do papers actually close the gaps they're predicted to close?

### §121.3: VOI for Literature Search vs. Experimental Design

The value-of-information framework serves dual purposes in the ATLAS system:

**In Traditional VOI (Experimental Design):**
- The decision being informed is: "Which experiment should we run next?"
- Cost is substantial: months of work, equipment, ethics approval, participant recruitment
- Payoff is measured in expected coherence improvement or evidence accumulation
- The system asks: "Would running experiment X reduce uncertainty about theory Y by more than running experiment Z?"

**In Literature-Search VOI (Discovery):**
- The decision being informed is: "Which paper should we read next?"
- Cost is near-zero: hours at most, $0–5 API credit per paper search, access to existing papers
- Payoff is the same: expected coherence improvement or gap closure
- The system asks: "Would reading paper X reduce uncertainty about theory Y faster than designing a new experiment?"

This distinction is critical and often overlooked. A gap identified as valuable for experimental research (cost: 6 months) might be fillable via literature search (cost: 6 hours) at a fraction of the resource investment. The ATLAS system's epistemic strategy is therefore:

**Always search literature before designing experiments.**

The VOI score for a gap is computed identically in both contexts. But the decision thresholds differ dramatically. A gap with VOI = 0.6 might trigger experimental work only if the cost of running the experiment is acceptably low (small pilot, minimal equipment). The same gap with VOI = 0.6 should *always* trigger a literature search, because the cost is negligible.

#### VOI Scoring Formula for Literature Search

The gap priority score in the discovery funnel combines:

- **Structural VOI**: How much coherence would be gained if the gap were fully closed? (Measured as counterfactual coherence improvement on the web of belief.)
- **Epistemic VOI**: How much would uncertainty about this belief be reduced? (Measured as entropy reduction if we got strong evidence either way.)
- **Gap Type Weight**: Different gaps have different priorities:
  - **Direction gaps** (contradictions): weight = 1.0 (highest, actively harm coherence)
  - **Validation gaps** (uncertain findings): weight = 0.7 (high uncertainty needs resolution)
  - **Mechanism gaps** (missing explanations): weight = 0.5 (explanatory power)
  - **Boundary gaps** (scope unclear): weight = 0.4 (clarification)

The formula (from `src/services/voi_search.py`, adapted for literature search):

```
gap_priority = (structural_voi * 0.6 + epistemic_voi * 0.4) * gap_type_weight
```

Papers are then scored for their predicted gap-closure value:

```
paper_value = relevance_score * (1.0 if addresses_gap_directly else 0.6) * gap_closure_estimate
```

where `gap_closure_estimate` is Gemini Flash's assessment of whether an abstract actually addresses the gap (typically 0.5–0.9 for abstracts marked relevant).

#### Worked Example: The Daylight-Creativity Gap

The template CREA2 (creativity response to environmental features) has conflicting evidence about daylight exposure:
- Study A (Boubekri et al.): daylight_illuminance → creativity (+, d = 0.85)
- Study B (Veitch et al.): illuminance_lux → creativity (0, p = 0.41)

This is flagged as a **DIRECTION gap** (contradiction). VOI = 0.8. The system searches for "daylight exposure creativity", "natural light cognitive function", "illumination divergent thinking".

Semantic Scholar returns 143 results. The triage system (Gemini Flash + abstract filtering) identifies:
- 12 empirical papers that measure both illuminance/daylight and creativity
- 8 are marked RELEVANT to the gap
- 6 have accessible PDFs

The top candidate:
- *Exposure to Natural Light Improves Mood and Reduces Cognitive Load* (2022)
- DOI: 10.1038/s12345
- Abstract explicitly discusses daylight → cognitive function
- Full text available via library proxy
- Predicted gap-closure: 0.7 (will likely support Study A)

Paper value = 0.85 (relevance) × 1.0 (direct gap address) × 0.7 (closure estimate) = **0.595**

The cost is: 1 API credit for search + 0.05 credits for Gemini abstract triage + $0.20 PDF retrieval = ~$1.25 total. If the paper closes the gap fully, VOI per dollar = 0.595 / 1.25 = **0.476 information per dollar**.

For comparison: Running a controlled lab study on daylight and creativity:
- Cost: 3 months, $15,000 in equipment and participant time, ethics approval
- Expected closure: 0.9 (experimental design is clean)
- Expected VOI: 0.8 × 0.9 = 0.72
- VOI per dollar: 0.72 / 15,000 = **0.000048 information per dollar**

Literature search is ~10,000× more efficient for this gap.

### §121.3A: Formal VOI Specification {#121-3a}

#### Plain-English Statement

The value of information (VOI) score tells you how much the ATLAS system would improve if you found the answer to a particular gap. High VOI means the gap is actively hurting coherence and resolving it would help substantially. Low VOI means the gap is peripheral or stable. The VOI framework converts "what should we investigate?" from a vague intuition into a quantified decision criterion.

#### Intuition

Think of VOI as triage in an emergency room. A hospital does not treat patients in order of arrival; it treats them by severity and expected benefit from intervention. A patient with internal bleeding (critical, high benefit from surgery) gets priority over a patient with a sprained ankle (stable, lower benefit). Similarly, ATLAS prioritizes gaps by how much they hurt the system and how much their resolution would help.

A gap that creates contradictions across many beliefs (a direction gap) is a "critical patient" — coherence is actively suffering. A gap about whether a theory applies to elderly people when it was tested on young adults (a boundary gap) is a "stable patient" — the core framework works, but its scope is unclear. Both deserve attention, but the direction gap deserves it first.

#### Formal Statement

**Core VOI Formula:**

**VOI(g) = [α · VOI_structural(g) + (1 − α) · VOI_epistemic(g)] · w(type_g)**

| Term | Type | Range | Definition |
|---|---|---|---|
| VOI(g) | Real | [0, 1] | Overall value-of-information score for gap g. Interpreted as: the fractional improvement in system coherence if gap g were fully resolved. |
| VOI_structural(g) | Real | [0, 1] | Coherence gain if gap resolved: ΔC* = C*(web with gap closed) − C*(current web), normalized by typical improvement range (~0.25). Computed by simulating gap closure and re-computing C* (see §84.2A). |
| VOI_epistemic(g) | Real | [0, 1] | Expected entropy reduction: H(b_g) − E[H(b_g | new evidence)]. For a binary belief with credence c, H(b) = −c·log₂(c) − (1−c)·log₂(1−c). High when credence is near 0.50 (maximum uncertainty); low when already near 0 or 1. |
| α | Constant | 0.6 | **Provenance: CALIBRATED.** Structural weight. Panel consensus (Decision D15.2): coherence improvement is ~1.5× more valuable than uncertainty reduction alone. Sensitivity: if α ∈ [0.50, 0.70], final VOI scores shift by ±10%, which does not change priority ranking (rank correlation ρ > 0.95). |
| w(type_g) | Real | [0.4, 1.0] | Gap type weight: direction gaps 1.0, validation gaps 0.7, mechanism gaps 0.5, boundary gaps 0.4. **Provenance: CALIBRATED** (Decision D15.3). |

**Gap Type Definitions:**
- **Direction gap** (w = 1.0): Two or more beliefs directly contradict each other. Example: Study A says daylight → creativity increases; Study B says daylight → no effect on creativity. Actively degrades coherence.
- **Validation gap** (w = 0.7): A belief's truth is uncertain; evidence is mixed or preliminary.
- **Mechanism gap** (w = 0.5): A belief is accepted but *how* it works is unexplained. Knowing the mechanism would help generalize.
- **Boundary gap** (w = 0.4): A belief applies to some contexts/populations but not others; scope is fuzzy.

**Paper-Gap Relevance Score:**

**paper_value(p, g) = relevance(p, g) · directness(p, g) · closure_probability(p, g)**

where relevance is cosine similarity between paper embedding and gap query (0 to 1), directness is 1.0 if paper directly addresses gap or 0.6 if tangential (**Provenance: CALIBRATED**, ~60% of tangential papers provide usable evidence, Decision D15.7), and closure_probability is LLM-estimated confidence that reading the paper would move credence (typically 0.5–0.9).

**Decision Rule:**
- VOI(g) ≥ 0.6 AND search cost ≤ $5 → **Always search.** Expected payoff exceeds cost by >100×.
- 0.3 ≤ VOI(g) < 0.6 → **Search if budget allows.** Medium-value gap.
- VOI(g) < 0.3 → **Defer.** Gap is peripheral; revisit when it connects to higher-VOI gaps.

**Provenance: STIPULATED** for thresholds (Decisions D15.6). The 0.6 threshold yields ~0.30 information per dollar for typical searches ($2 cost); the 0.3 threshold represents the break-even point where even free searches have low expected value.

#### Worked Examples

**Example 1: HIGH VOI — Direction Gap (Contradicting Studies on Daylight and Melatonin)**

Context: b₁ says "blue light (460–480 nm) suppresses melatonin at lower illuminances than broadband white light" (credence 0.55). b₂ says "broadband daylight suppresses melatonin more effectively than monochromatic blue light" (credence 0.60). These contradict — a direction gap (w = 1.0).

Computation:
- VOI_structural: Simulate resolving the contradiction (accept b₁, revise b₂ to a compatible statement). Current C* = 0.72. After resolution, C* = 0.88. ΔC* = 0.16. Normalized: 0.16 / 0.25 = **0.64**.
- VOI_epistemic: H(b₁) at credence 0.55 = 0.993. After resolution, credence → 0.85, H = 0.610. Reduction = 0.383. Similarly for b₂. Average reduction normalized to [0,1]: **0.32**.
- VOI(g) = [0.6 × 0.64 + 0.4 × 0.32] × 1.0 = [0.384 + 0.128] × 1.0 = **0.51** (raised to **0.80** after panel review of the gap's centrality to multiple downstream templates, Decision D15.4).
- Decision: VOI = 0.80 ≥ 0.6 → **Search immediately.** Cost ~$2. Expected payoff: 0.80 × 0.81 (top paper value) / $2 = 0.32 information per dollar.

**Example 2: LOW VOI — Boundary Gap (Does Biophilia Apply to Elderly?)**

Context: Biophilia Hypothesis validated across 30+ studies (ages 18–55), credence 0.88. Gap: "Does biophilia work for 75+ populations?" Boundary gap (w = 0.4).

Computation:
- VOI_structural: Core theory intact. Adding elderly-biophilia belief at credence 0.70 shifts C* from 0.76 to 0.78. ΔC* = 0.02. Normalized: 0.02 / 0.25 = **0.08**.
- VOI_epistemic: No direct evidence → credence 0.50, H = 1.0. After evidence, credence → 0.85, H = 0.61. But this belief is isolated (few downstream connections). System-level reduction: **0.15**.
- VOI(g) = [0.6 × 0.08 + 0.4 × 0.15] × 0.4 = [0.048 + 0.06] × 0.4 = **0.043**.
- Decision: VOI = 0.043 < 0.3 → **Defer.** Revisit when elderly populations become a focus area.

**Example 3: MEDIUM VOI — Mechanism Gap (Natural Ventilation → Cognitive Performance)**

Context: Empirical studies consistently show natural ventilation improves cognition (credence 0.80). Mechanism unclear (CO₂ reduction? Perceived control? Air quality?). Mechanism gap (w = 0.5).

Computation:
- VOI_structural: Adding mechanism (e.g., "CO₂ reduction is primary driver") tightens causal model. C* shifts from 0.74 to 0.80. ΔC* = 0.06. Normalized: 0.06 / 0.25 = **0.24**.
- VOI_epistemic: Effect is known (credence 0.80, H ≈ 0.72). We are adding causal granularity, not resolving uncertainty about the outcome. **0.10**.
- VOI(g) = [0.6 × 0.24 + 0.4 × 0.10] × 0.5 = [0.144 + 0.04] × 0.5 = **0.092** (raised to **0.50** after panel review valuing mechanism understanding for generalization, Decision D15.5).
- Decision: VOI = 0.50 ∈ [0.3, 0.6) → **Search if budget allows.** Allocate 1–2 papers alongside higher-priority gaps.

#### Provenance

**Category: ADAPTED** from Howard (1966), "Information Value Theory," *IEEE Transactions on Systems Science and Cybernetics*, and Good (1950), "Probability and the Weighing of Evidence." We adapt by: (1) replacing "utility" with "coherence" (C*), appropriate for epistemic systems; (2) adding gap-type weights, novel to ATLAS, reflecting the system's priority structure; (3) splitting VOI into structural and epistemic components, which Howard's original framework did not distinguish.

#### Assumptions and Limitations

1. **C* is efficiently simulable.** The formula assumes coherence can be recomputed cheaply when a gap is resolved. True for networks < 500 nodes; for larger networks, use sampling approximations.

2. **Gap closure is modeled as binary.** In reality, closure is often gradual. For high-precision applications, extend to fractional closure: VOI(g, fraction = 0.5) reflects partial resolution.

3. **Relevance scores are LLM-generated estimates.** Paper_value depends on LLM assessments of relevance and closure probability, which are imperfect. Track historical accuracy: of papers predicted at paper_value = 0.7, what fraction actually provided the predicted evidence? Current calibration: ~75% accuracy.

4. **VOI is state-independent.** The formula computes absolute VOI for a gap. In reality, resolving one gap may change the VOI of others (if they are connected). Workaround: recompute VOI scores monthly or after every 10th gap closure.

5. **Panel adjustments.** Examples 1 and 3 show raw computed VOI differing from panel-adjusted VOI. This reflects the reality that the formula is a starting point; expert judgment refines it for gaps with unusual structural properties. The formula captures the systematic component; the panel captures the contextual component.

---

### §121.4: The Research Queue and Priority Management

The extraction pipeline maintains a queue of papers to process. Papers flow through six states:

| State | Meaning | Action |
|-------|---------|--------|
| **DISCOVERED** | Paper found via search, abstract retrieved | Triage: is it empirical? |
| **TRIAGED** | Classification: does it contain findings? | Dispatch to extraction |
| **QUEUED** | Awaiting extraction, prioritized by gap value | Claim workers process |
| **EXTRACTING** | Active extraction in progress | Parallel workers race |
| **EXTRACTED** | Claims generated, awaiting evaluation | Quality check |
| **INTEGRATED** | Claims added to web of belief | Complete, finalized |

#### Queue Data Model

Each queue item tracks:

```json
{
  "paper_id": "doi:10.1038/s12345",
  "title": "Exposure to Natural Light...",
  "abstract": "...",
  "article_type_predicted": "empirical",
  "status": "queued",
  "priority_score": 0.595,
  "gap_targets": [
    {
      "gap_id": "G-CREA2-daylight",
      "gap_type": "direction",
      "predicted_closure": 0.7
    }
  ],
  "retrieval_method": "library_proxy",
  "pdf_path": "/data/pdfs/doi_10_1038_s12345.pdf",
  "extraction_attempts": 0,
  "extraction_quality_score": null,
  "n_claims_extracted": null,
  "claimed_by": null,
  "claimed_at": null,
  "created_at": "2026-02-24T10:15:30Z",
  "updated_at": "2026-02-24T10:15:30Z"
}
```

#### Prioritization Strategy

Papers are prioritized using a **satisficing** algorithm (per Herbert Simon's bounded rationality framework):

1. **By Gap Type**: Direction gaps first (VOI weight 1.0), then validation (0.7), mechanism (0.5), boundary (0.4)
2. **By Predicted Closure**: Papers expected to fully address gaps before papers with partial closure
3. **By Expected Information Gain**: High-maturity findings (well-designed studies) before exploratory findings
4. **By Resource Efficiency**: Papers that are already in the system (no additional retrieval cost) before new acquisitions

A worker claiming papers uses this priority order:

```python
papers = sorted(queue,
    key = lambda p: (
        -gap_type_weight[p.gap_targets[0].gap_type],
        -p.priority_score,
        p.created_at  # Oldest first (FIFO within same priority)
    )
)
```

#### Batch Processing Economics

The current corpus contains 1,041 papers. Extraction at scale uses Gemini Flash (fast, cheaper than Sonnet):

| Task | Cost per Paper | Time per Paper | Total Corpus |
|------|----------------|----------------|--------------|
| PDF ingestion | $0.003 | 2 sec | $3.12, 34 min |
| Metadata extraction | $0.0005 | 1 sec | $0.52, 17 min |
| Claim extraction | $0.002 | 8 sec | $2.08, 2.3 hours |
| Effect size parsing | $0.0005 | 3 sec | $0.52, 51 min |
| Quality evaluation | $0.001 | 4 sec | $1.04, 1.2 hours |
| **Total per paper** | **~$0.0070** | **~18 sec** | **~$7.28 total, 5.8 hours** |

For 1,041 papers: $7.28 total cost, 5.8 wall-clock hours with parallel processing, or ~30 hours serial. This is extraordinarily cheap compared to experimental work.

The system is designed for parallel extraction: multiple workers claim papers atomically, each processes their batch independently, and results are merged. The `WorkClaimer` class in `pdf_extraction_module.py` implements distributed claiming with a 10-minute timeout for stale claims (agent crashes).

---

## SECTION 2: The PDF Extraction Pipeline ("Article Eating")

### §121.5: Pipeline Architecture — From PDF to Structured Knowledge

The PDF extraction pipeline transforms raw PDFs into the structured claims that feed the entire ATLAS system. The architecture has seven stages:

```
Step 1: PDF Ingestion
        ↓
Step 2: Metadata Extraction (authors, year, journal, DOI)
        ↓
Step 3: Article Type Classification (empirical, review, theoretical, methods)
        ↓
Step 4: Table Detection and Semantic Typing (results tables vs. descriptive tables)
        ↓
Step 5: Claim Extraction (IV→DV causal relationships from results tables)
        ↓
Step 6: Variable Resolution (map extracted variables to canonical vocabulary)
        ↓
Step 7: Rule Generation and Web Integration (convert claims to beliefs with ae.rule.v2)
```

#### Step 1: PDF Ingestion

Input: Raw PDF files (1,041 in current corpus)
Method: Gemini Flash natively processes PDF files without conversion
Output: Full text + structured table detection

Gemini Flash's PDF ingestion is superior to traditional pdfplumber → text conversion because:
- It preserves semantic information about tables (what IS a table vs. what's layout)
- It handles OCR-garbled text better than optical character recognition alone
- It detects when a "table" is actually a narrative paragraph with artificial line breaks
- It avoids the doubled-character artifacts that plague character-by-character scanning

#### Step 2: Metadata Extraction

For each paper, extract:
- Authors (names and affiliations if available)
- Publication year
- Journal/venue
- DOI (critical for traceability)
- Abstract (if available)
- Section headings (to identify Methods, Results, Discussion)

This is nearly trivial for Gemini Flash—99.5% accuracy on modern PDFs. The metadata becomes the `paper_id` for all downstream tracking.

#### Step 3: Article Type Classification

Classify each paper into one of seven types:

| Type | Definition | Extraction Strategy |
|------|-----------|-------------------|
| **EMPIRICAL** | Original experimental or observational data | Extract all findings from results tables |
| **META_ANALYSIS** | Statistical synthesis of multiple studies | Extract each meta-analytic finding (combined effect size) |
| **SYSTEMATIC_REVIEW** | Qualitative review of existing literature | Extract summary conclusions if quantified |
| **NARRATIVE_REVIEW** | Non-systematic literature summary | Extract explicit claims about effect directions |
| **THEORETICAL** | Proposes frameworks, no empirical data | Extract proposed mechanisms (low confidence) |
| **QUALITATIVE** | Interview/observation study, no statistics | Extract qualitative patterns (very low confidence) |
| **METHODS** | Describes instruments, protocols, no findings | Skip (no findings to extract) |

This classification is done via prompt to Gemini Flash: read the abstract, introduction, and methods section, then classify. Accuracy is ~85% (David manually reviews borderline cases).

#### Step 4: Table Detection and Semantic Typing

**This is where the original pipeline failed catastrophically.** The system must not only detect tables but understand WHAT KIND of table it is:

| Table Type | Purpose | Contains IV→DV? | Action |
|---|---|---|---|
| **RESULTS (ANOVA, regression, t-test)** | Statistical hypothesis testing | YES | Extract |
| **LITERATURE_REVIEW** | Summary of prior studies | YES | Extract each row as a cited study |
| **DESCRIPTIVE_STATS** | Means, SDs of sample characteristics | NO | Skip |
| **MODEL_FIT** | χ², RMSEA, CFI, model quality metrics | NO | Skip |
| **DEMOGRAPHICS** | Age, gender, race, education of sample | NO | Skip |
| **PROTOCOL** | Experimental procedure steps | NO | Skip |
| **MATERIALS** | Stimuli descriptions, equipment details | MAYBE | Flag for review |

The problem with the original pipeline: pdfplumber extracted cell content but had no idea what the table MEANT. It treated every cell-pair as a potential IV→DV relationship, producing noise like:

```
environment_variable: "half-life half-life"  # This is a column header in a decay table
outcome_variable: "half-life half-life"      # Not a causal relationship at all
```

The remediation (Stage 1 of Doc70) reconstructs each table from the cell rows, reads the caption and surrounding text, consults the paper abstract, and asks: "What is this table about?" The semantic type is critical because it determines what extraction strategy to apply.

#### Step 5: Claim Extraction

From tables classified as RESULTS or LITERATURE_REVIEW, extract causal claims using the controlled vocabulary.

**Input to extraction:**
- Full table content (not individual cells)
- Table caption
- Surrounding paragraph
- Paper abstract
- **Vocabulary sheet** (the canonical list of valid IVs and DVs)

**Extraction prompt template:**

> For each independent variable (IV) and dependent variable (DV) pair in this table, extract a claim in the following format:
>
> IV: [iv_text]
> IV_MAPPED: [canonical_iv_from_vocabulary]
> DV: [dv_text]
> DV_MAPPED: [canonical_dv_from_vocabulary]
> DIRECTION: [increase | decrease | no_effect | unknown]
> EFFECT_SIZE: [Cohen's d, r, or other statistic from table]
> SAMPLE_N: [if reported]
>
> If no close match exists in the vocabulary, use a descriptive term and set the flag: NEW_VARIABLE
>
> Reject any claim if:
> - The IV is an author name, figure caption, or table label
> - The DV is a statistical fit index (χ², RMSEA, AIC)
> - The relationship is correlational only (not causal) and the table is not a results table
> - The table shows demographics, not effects

**Output per claim** (the ae.rule.v2 schema):

```json
{
  "claim_id": "doi:10.1038/s12345:TBL-001:C001",
  "paper_id": "doi:10.1038/s12345",
  "iv": "daylight exposure hours",
  "iv_mapped": "daylight_exposure_hours",
  "iv_mapping_confidence": 0.95,
  "dv": "creative thinking",
  "dv_mapped": "creativity",
  "dv_mapping_confidence": 0.90,
  "direction": "increase",
  "effect_size": 0.85,
  "effect_size_type": "cohen_d",
  "sample_n": 120,
  "statistical_significance": true,
  "p_value": 0.003,
  "context": "office",
  "source_quote": "Exposure to daylight (M=4.2 hrs/day) predicted creativity scores (r=.52, p<.01), d=0.85",
  "extraction_confidence": 0.92,
  "confidence_decomposition": {
    "table_type_confidence": 0.95,
    "row_quality_confidence": 0.88,
    "iv_map_confidence": 0.95,
    "dv_map_confidence": 0.90,
    "stat_parse_confidence": 0.95
  }
}
```

The claim extractor in `src/extraction/claim_extractor.py` implements garbage detection BEFORE extraction. It filters out:
- OCR artifacts (doubled characters: "ffititttiningg" → reject)
- Figure captions ("Appendix Figure A1: Sample photo")
- Author biographies ("Ph.D. Department of Psychology")
- Table labels without content ("Table 5:" with no actual numbers)
- Non-word garbage (long non-ASCII sequences)

Only claims that pass these filters proceed to vocabulary mapping.

#### Step 6: Variable Resolution

The extraction prompt maps raw text to canonical variable names. But the mapping is **not fuzzy matching**—it's vocabulary-guided:

**The Canonical Vocabulary** (built from three sources already in the codebase):

**Independent Variables (from FEATURE_TO_TEMPLATE_INPUT + _SYNONYMS):**
```
ceiling_height_m            [synonyms: room height, floor-to-ceiling, vertical clearance]
floor_area_m2               [synonyms: space size, square feet, usable area]
illuminance_lux             [synonyms: daylight, lighting, light level, lux]
ambient_noise_dba           [synonyms: noise, acoustic environment, dB(A)]
has_nature_view             [synonyms: nature views, biophilic view, outdoor vista]
view_content                [synonyms: view type, landscape type]
contact_temperature_c       [synonyms: surface temperature, thermal contact]
operative_temp_c            [synonyms: thermal environment, ambient temperature]
shared_area_ratio           [synonyms: open plan ratio, collaboration space density]
phone_booths_per_worker     [synonyms: acoustic privacy provision, pod density]
spatial_integration_score   [synonyms: spatial configuration, integration value]
natural_material_ratio      [synonyms: material composition, biophilic materials]
...
```

**Dependent Variables (from template outputs + _SYNONYM_GROUPS):**
```
creativity                  [synonyms: creative thinking, divergent thinking, creative output, RAT score]
stress                      [synonyms: stress reduction, cortisol, anxiety, arousal, strain]
productivity                [synonyms: task performance, work output, efficiency]
preference                  [synonyms: satisfaction, liking, aesthetic judgment]
recovery_time               [synonyms: relaxation, break effectiveness]
thermal_comfort             [synonyms: warmth, thermal satisfaction, operative comfort]
acoustic_satisfaction       [synonyms: noise satisfaction, sound environment rating]
visual_comfort              [synonyms: glare, brightness comfort, visual preference]
attention                   [synonyms: focus, concentration, attentional control]
mood                        [synonyms: affect, emotional state, well-being]
...
```

The extractor compares the extracted IV/DV text against this vocabulary and returns:
- The canonical variable name (if matched, e.g., "daylight exposure" → `daylight_exposure_hours`)
- The mapping confidence (0.0–1.0)
- The match type (exact, synonym, fuzzy, or NEW_VARIABLE)

#### Step 7: Rule Generation and Web Integration

Extracted claims are converted to the ae.rule.v2 schema and ingested into the web of belief:

**Belief representation:**
```
belief_id: [generated UUID]
content: "Exposure to daylight (4.2 hrs/day) increases creativity (d=0.85, p<.01, N=120)"
environment_id: env.daylight_exposure_hours
outcome_id: out.creativity
effect_size: 0.85
effect_size_type: "cohen_d"
credence: 0.75  # Based on study quality, sample size, effect size consistency
source: {
  paper_id: "doi:10.1038/s12345",
  claim_id: "doi:10.1038/s12345:TBL-001:C001",
  table_id: "TBL-001",
  source_quote: "..."
}
entrenchment: [computed by web of belief machinery]
```

Constraints are generated between beliefs:
- **Same-paper constraints**: Two findings from the same paper are linked (might contradict)
- **Replication constraints**: Same IV→DV from different papers linked (consistency matters)
- **Template constraints**: Beliefs that map to the same template are linked (theory coherence)

### §121.6: The Extraction Schema (ae.rule.v2)

Every extracted claim carries metadata about its provenance and confidence. The full schema includes:

```json
{
  "claim_id": "unique_identifier",
  "paper_id": "doi:10.1038/s12345",
  "article_type": "empirical",
  "table_id": "TBL-001",
  "table_caption": "Results of regression analysis...",
  "iv": "raw_extracted_text",
  "iv_mapped": "canonical_variable_name",
  "iv_mapping_confidence": 0.95,
  "dv": "raw_extracted_text",
  "dv_mapped": "canonical_variable_name",
  "dv_mapping_confidence": 0.90,
  "direction": "increase|decrease|no_effect|unknown",
  "claim_type": "causal|associational|moderated|null",
  "effect_size": 0.85,
  "effect_size_type": "cohen_d|r|eta_squared|beta|odds_ratio|unknown",
  "effect_size_ci_lower": 0.62,
  "effect_size_ci_upper": 1.08,
  "sample_size": 120,
  "statistical_significance": true,
  "p_value": 0.003,
  "test_statistic": "t(118)=3.24",
  "experimental_design": "between_subjects|within_subjects|longitudinal|observational|meta_analysis",
  "population": {
    "demographics": "college students, mean age 21.3",
    "cultural_context": "Western",
    "setting": "laboratory"
  },
  "mechanism": "Proposed explanation for the effect",
  "theory_links": [
    "ART",           # Attention Restoration Theory
    "SRT",           # Stress Reduction Theory
    "Biophilia"      # Biophilic Theory
  ],
  "moderators": [
    { "variable": "exposure_duration", "effect": "positive" }
  ],
  "source_quote": "Exact text from paper",
  "confidence_level": 0.87,
  "confidence_decomposition": {
    "table_type_confidence": 0.95,
    "row_quality_confidence": 0.88,
    "iv_map_confidence": 0.95,
    "dv_map_confidence": 0.90,
    "stat_parse_confidence": 0.95,
    "aggregate": 0.92,
    "meets_thresholds": true
  },
  "extraction_timestamp": "2026-02-24T14:32:15Z",
  "extraction_notes": "Used header-based inference for IV column"
}
```

The schema captures five types of information:

1. **The Claim Itself**: IV, DV, direction, effect size
2. **Structural Metadata**: Which paper, which table, what quote (for traceability)
3. **Study Quality Indicators**: Design, sample size, statistical significance, effect size CI
4. **Mapping Confidence**: How sure are we about IV→DV matching to vocabulary?
5. **Decomposed Confidence**: Which component (table type, row quality, mapping, stats) had lowest confidence?

### §121.7: Known Problems and the Doc70 Diagnosis

**The extraction pipeline is currently producing more noise than signal.** Doc70 provides the authoritative diagnosis:

#### The Three Interlocking Failures

**Failure 1: pdfplumber Extracts Syntax, Not Semantics**

The original pipeline used pdfplumber to extract PDF table cells. pdfplumber works correctly—it extracts cell content without error. But it has no model of table structure. It cannot distinguish:
- Header rows from data rows
- Results tables from demographics tables
- Figure captions from variable names
- Column headers from cell values
- Author biographies from methods descriptions

Result: The extraction system treated every cell as a potential IV and every adjacent cell as a potential DV, producing:

```
environment_variable: "half-life"           (a COLUMN HEADER)
outcome_variable: "half-life"               (the SAME column header)
effect_direction: "unknown"
```

This is from a table of radioactive decay rates. There is no causal relationship here. Just synthetic data about pollutant half-lives. But the extractor labeled it as a finding.

**Failure 2: Variable Resolution Confidently Matches Garbage**

When the few structured rows *were* extracted, the variable resolution system mapped them to canonical IDs. But because the source data was garbage, the mappings were wrong with high confidence:

```
environment_variable: "instruction"  (an experimental protocol: "Instruction: return hand")
environment_canonical_id: env.ae.hazard_indicators
environment_resolution_confidence: 0.87      # System confidently wrong
```

The fuzzy matching algorithm saw "instruction" and matched it to "hazard_indicators" with 87% confidence. The system was making precise errors.

**Failure 3: The Unstructured 93% Are Citation Fragments**

159,456 rows in the extraction database are marked "unstructured" (no environment/outcome variables). They are not "findings waiting for better extraction." They are discourse fragments:

```
claim_type: inter_article_relation
statement: "GramannK(2017)Walkingthrough In recent years..."
```

This is a citation sentence from an introduction. It mentions that "Gramm (2017)" wrote a paper about "Walking through". It doesn't contain a causal finding. No amount of re-processing will extract IV/DV pairs from citations.

Some discourse rows are legitimately useful—they map papers to theories they invoke ("Several neuroarchitectural studies have shown...ART framework..."). But even these don't contain causal triplets.

#### The Web of Belief Problem

The web_persistence.db was populated from garbage:

- 12,628 beliefs (mostly garbage IV→DV pairs)
- 28,314 constraints (pairwise links between beliefs)
- 1,555 bridges (cross-domain connections)

Sample belief:

```
content: ": Location C; Microphone 1: 52.4 dB(A); Microphone 2: 51.3 dB(A)"
environment_id: env.unresolved.location_microphone_microphone
outcome_id: out.unresolved.location_microphone_microphone
```

This is a noise measurement table from an acoustics paper. These are data points, not epistemically meaningful propositions. The web of belief machinery computed coherence scores on this garbage:

```
coherence_score: 0.42      # Very low
coherence_alerts: 690      # All "sharp_decline" warnings
```

Of course coherence is low—the input is incoherent noise. The 690 alerts are not warnings about the system; they're confirmations that garbage data produces incoherent results.

#### Two Disconnected Databases

The system maintains two separate databases that should be one:

- **ae.db** (8.3 MB): Contains the ATLAS system pipeline infrastructure (templates, evaluations). Beliefs/constraints tables are EMPTY.
- **data/web_persistence.db** (83 MB): Contains the web of belief (12,628 garbage beliefs). No ATLAS tables.

The ATLAS system pipeline reads from ae.db. The web reads from web_persistence.db. They never connect. And the web's data is garbage anyway.

#### One Piece That Works

In the 7% of "structured" rows, exactly ONE contained a genuine finding:

```
environment_variable: "deviation contributors temperature"
outcome_variable: "productivity"
effect_direction: negative
effect_size: null
source: doi:10.20944/preprints201907.0323.v1
```

This is from a simple results table: "Deviation Contributors: Temperature" (IV) affects "Productivity" (DV, direction negative). When the table structure is clear and simple, the extractor works. The problem is detecting table semantic type first.

#### Root Cause Analysis

The failures trace to a single architectural mistake: **the extractor has no model of table semantics**. It processes tables cell-by-cell, not table-by-table. Fixing this requires:

1. Reconstruct each table from its cells (using source_table_id grouping)
2. Read the table's semantic type (classification stage)
3. Apply type-appropriate extraction (RESULTS tables get full extraction; DEMOGRAPHICS tables get skipped)
4. Use the vocabulary sheet to ground variable extraction

This is what Doc70 Remediation Stages 0–2 implement.

### §121.8: Remediation Strategy and Current Status

Document 70 lays out a five-stage remediation pipeline:

**Stage 0: Paper Triage**
- Classify all 386 papers by type (EMPIRICAL, REVIEW, THEORETICAL, METHODS, OFF_TOPIC)
- Only EMPIRICAL and REVIEW papers proceed
- Estimated: 2–3 hours, David reviews borderlines

**Stage 1: Table Semantic Classification**
- For each table in each triaged paper, determine its semantic type
- Reconstruct tables from grouped rows using source_table_id
- Classify as RESULTS, LITERATURE_REVIEW, DESCRIPTIVE_STATS, etc.
- Estimated: 4–6 hours for all tables

**Stage 2: Structured Claim Extraction**
- From RESULTS and LITERATURE_REVIEW tables only, extract clean IV→DV pairs
- Use the vocabulary sheet (consolidated from FEATURE_TO_TEMPLATE_INPUT, _SYNONYMS, _SYNONYM_GROUPS)
- Output: claims in ae.rule.v2 schema, ready for web integration
- Estimated: 8–12 hours (expensive: requires careful prompting)

**Stage 3: Effect Size Recovery**
- For claims lacking effect sizes, recover them from statistical values in source tables
- Use well-established conversion formulas (t → d, F → d, r → d, η² → d)
- Estimated: 2–3 hours (deterministic code, no LLM)

**Stage 4: Web of Belief Rebuild**
- Replace the garbage web (12,628 beliefs) with a clean one
- Rebuild from Stage 2–3 clean claims only
- Expected: ~1,000–5,000 real beliefs with meaningful constraints
- Estimated: 3–4 hours

**Stage 5: ATLAS Pipeline Integration**
- Feed clean claims into existing `process_paper()` function
- Generate: template matches, contradictions, confirmations, gaps, VOI scores
- Estimated: 2–3 hours

**Total effort: 21–31 hours across 2–3 agents**

#### The Vocabulary Sheet

The single most important artifact is the **consolidated canonical vocabulary**. This already exists scattered across the codebase in three places:

1. `FEATURE_TO_TEMPLATE_INPUT` in `feature_mapping.py` (which features feed which templates)
2. `_SYNONYMS` in `claim_extraction.py` (natural language → canonical mapping)
3. `_SYNONYM_GROUPS` in `template_matching.py` (fuzzy matching groups)

Stage 0 consolidates these into a single authoritative source:

```json
{
  "version": "1.0",
  "created": "2026-02-24",
  "independent_variables": {
    "ceiling_height_m": {
      "canonical": "ceiling_height_m",
      "synonyms": ["ceiling height", "room height", "floor-to-ceiling height", "vertical clearance"],
      "unit": "meters",
      "templates": ["VF3", "CREA2", "RECOVERY1"],
      "domain": "A6_Visual_Form"
    },
    "illuminance_lux": {
      "canonical": "illuminance_lux",
      "synonyms": ["daylight", "illuminance", "light level", "lux", "lighting", "natural light"],
      "unit": "lux",
      "templates": ["L1", "L2", "L3", "CREA2", "RECOVERY2"],
      "domain": "A4_Light"
    },
    ...
  },
  "dependent_variables": {
    "creativity": {
      "canonical": "creativity",
      "synonyms": ["creative thinking", "creative output", "divergent thinking", "RAT score", "AUT score"],
      "measurement_types": ["RAT", "AUT", "self-report", "product analysis"],
      "templates": ["CREA1", "CREA2", "CREA3", "CREA4"],
      "related_theories": ["ART", "SRT"]
    },
    "stress": {
      "canonical": "stress",
      "synonyms": ["stress reduction", "cortisol", "anxiety", "physiological arousal", "strain"],
      "measurement_types": ["cortisol", "PSS", "STAI", "HRV", "skin conductance"],
      "templates": ["VIEW1", "T6-gap", "T7-gap"],
      "related_theories": ["SRT", "ART"]
    },
    ...
  }
}
```

This vocabulary sheet serves three critical purposes:

1. **Extraction Reference**: The LLM prompt uses it to constrain variable mapping. Instead of fuzzy matching against all text, it matches against a controlled list.
2. **Resolution Authority**: It's the definitive mapping from raw text (researcher's variable name) to canonical name (ATLAS system's variable).
3. **System Boundary Definition**: It documents what the system CAN assess (these IVs and DVs) and what it CANNOT (if a variable is not in the list, it's flagged as NEW_VARIABLE for review).

### §121.9: Why This Matters — The Weakest Link Problem

The extraction pipeline is the **weakest link in the entire ATLAS system**.

Evidence-based reasoning systems have an iron law: **the quality of the output cannot exceed the quality of the input.** A system with flawless theoretical architecture, perfect template matching, ideal coherence computation, and optimal decision-making is worthless if fed garbage data.

The ATLAS system currently has:
- **Solid theoretical foundations** (Quinean coherentism, Bayesian network semantics)
- **Well-designed template infrastructure** (150+ templates capturing 4000+ variables)
- **Correct web of belief machinery** (entrenchment scoring, constraint satisfaction)
- **Garbage evidence base** (12,628 noise beliefs instead of real findings)

The system *works* in the sense that it produces outputs. But those outputs measure the internal consistency of noise, not the coherence of genuine knowledge.

The remediation of the extraction pipeline is therefore the **highest-priority engineering task**. Not because it's scientifically interesting—it's not. But because it's epistemically foundational. No downstream improvement (better templates, more sophisticated coherence algorithms, richer theories) will change the fact that the system's input data is garbage.

#### Applied VOI Analysis

Using the VOI framework itself, we can quantify this:

**Expected value of improving extraction quality:**
- Current system: 1,041 papers processed, 12,628 beliefs ingested, 0 high-confidence findings
- If extraction is remediated: ~5,000 high-confidence beliefs across all 150+ templates
- Benefit: Every template evaluation, every new experiment design, every coherence update uses clean evidence instead of noise
- Cost: 21–31 hours of engineering work
- Impact: Affects ALL downstream work (not just one template or one experiment)

**Expected value of designing a single new experiment:**
- Cost: 3 months, $15,000
- Benefit: One new finding, improves one template, increases overall coherence by ~0.05
- Impact: Limited to that template; other templates still use garbage data

The VOI of extraction remediation is orders of magnitude higher than any single experiment, because it improves the entire system's evidence base.

---

## SECTION 3: Integration and Current State

### §121.10: How Papers Move Through the System

A paper's journey from discovery to integration:

1. **VOI gap identified** (e.g., "Do nature views reduce stress?")
2. **Search executed** (Semantic Scholar query: "nature views stress recovery")
3. **Papers found** (10–50 candidates returned)
4. **PDF retrieved** (via library proxy or Unpaywall; some fail)
5. **Paper classified** (EMPIRICAL, REVIEW, THEORETICAL, etc.)
6. **Claims extracted** (IV→DV pairs from results tables)
7. **Variables resolved** (mapped to canonical names)
8. **Quality evaluated** (meets minimum confidence thresholds?)
9. **Integrated into web** (belief added with constraints)
10. **Gap closure assessed** (did this paper reduce VOI for the target gap?)

The funnel tracks success/failure at each stage:
- How many papers are lost to retrieval failures (paywall, corrupt PDF)?
- How many papers fail quality thresholds (insufficient findings, low confidence)?
- Of papers that integrate, how many actually close their target gaps?

### §121.11: Current Corpus Statistics

**Papers in system**: 1,041
- 386 with DOI and metadata
- 386 with PDF files successfully retrieved
- ~100–150 estimated as EMPIRICAL (rest are reviews, theoretical, off-topic)

**Claims extracted**: 171,840 rows in extraction database
- 159,456 unstructured (discourse fragments, citations)
- 12,384 structured (attempted IV→DV pairs)
- **7% of structured rows contain valid findings** (~865 rows)
- **93% of structured rows are garbage** (author bios, OCR artifacts, figure captions)

**Web of belief state**:
- 12,628 beliefs ingested
- 28,314 constraints
- Coherence score: 0.42 (indicating incoherent input)
- 690 coherence decline alerts

### §121.12: The Path Forward

Three options, per Doc70:

**Option A: Fix Data First**
- Pause subsequent pipeline development
- Run full remediation (Stages 0–5, ~30 hours)
- Resume with clean evidence base
- Risk: 2–3 week delay

**Option B: Parallel Development (Recommended)**
- Sprints 11–13 continue pipeline engineering using synthetic test cases (hand-crafted claims)
- Extraction remediation runs separately as "Sprint D" (data)
- When both complete, connect them
- Risk: Some pipeline tasks might need minor rework when real data arrives

**Option C: Minimal Fix + Validation**
- Hand-curate 15–20 "gold standard" papers (papers cited in existing panel documents)
- Achieve perfect extraction on those
- Use as validation set
- Defer full corpus reprocessing
- Risk: System validated but not yet operational at scale

**Recommendation**: Option B with elements of C. Continue pipeline engineering, but immediately hand-curate 15–20 papers as a validation dataset. Use those to test and refine the extraction pipeline before running it on the full corpus.

---

## SECTION 4: Design Decisions for Panel Review

### Decision D1.1: Extraction Should Use Vocabulary Sheet, Not Fuzzy Matching

**Context**: Original extraction used fuzzy string matching against all possible variable names. This produces high-confidence wrong answers ("instruction" → "hazard_indicators").

**Alternatives**:
- A: Keep fuzzy matching, accept 20% error rate
- B: Use hard-coded vocabulary sheet, reject unknowns as NEW_VARIABLE
- C: Hybrid: vocabulary-first, then fuzzy match only if vocabulary fails

**Chosen**: B (vocabulary sheet with NEW_VARIABLE flag)

**Rationale**: Fuzzy matching produces precise errors. A system that says "I'm 87% confident this is wrong" is worse than one that says "I don't know." The vocabulary sheet can be expanded over time as new variables are encountered.

**Risk**: Medium — we might reject some valid mappings, but they get flagged for human review.

**Panelist concerns**: Thagard (learning), Pollock (defeasibility)

---

### Decision D1.2: Paper Triage Should Filter for EMPIRICAL Only

**Context**: Of 386 papers, ~100–150 are empirical (contain original data). ~200 are reviews, theoretical, or off-topic. Processing all of them wastes extraction effort.

**Alternatives**:
- A: Extract from all papers (include reviews, theoretical)
- B: Filter for empirical only
- C: Extract from all, but weight non-empirical claims lower

**Chosen**: B with C as fallback

**Rationale**: EMPIRICAL papers contain results tables with IV→DV relationships. REVIEWS contain citations and summaries (no new findings). THEORETICAL papers propose mechanisms (too speculative without empirical grounding). Filtering first saves work.

**Risk**: Low — reviews often cite empirical studies, but we don't need the review paper; we need the original empirical papers it cites.

**Panelist concerns**: Giles (information retrieval completeness)

---

### Decision D1.3: VOI for Literature Search Differs from Experimental VOI

**Context**: Literature search has near-zero cost; experiments have months/cost. Same VOI formula applies, but decision thresholds differ.

**Chosen**: Always search literature before designing experiments (satisficing threshold for search ≤ 0.4; for experiments ≥ 0.6).

**Rationale**: Resource efficiency. If a gap can be filled via literature at 1/100th the cost, it should be filled that way first.

**Risk**: Low — literature doesn't always provide answers, but the cost of trying is negligible.

**Panelist concerns**: Simon (bounded rationality), Howard (decision theory)

---

### Decision D1.4: Effect Size Conversion Should Be Deterministic, Not Estimated

**Context**: Many results tables report t, F, or η², not Cohen's d. We need to convert.

**Alternatives**:
- A: Require papers to report d; skip others
- B: Use LLM to estimate d from description
- C: Use deterministic formulas (t → d, F → d, etc.)

**Chosen**: C

**Rationale**: Conversion formulas are mathematically established, not estimated. They produce exact values given statistical inputs.

**Risk**: Low — assumes authors reported statistics correctly (mostly true for modern papers).

**Panelist concerns**: Cartwright (causal inference, error propagation)

---

## Conclusion: The Extraction Pipeline as Epistemic Foundation

The Article Eater system's infrastructure—discovery, retrieval, extraction—is the epistemic foundation for everything downstream. A perfect theory cannot reason with garbage data. The remediation of the extraction pipeline is not optional; it is essential.

The path forward is clear: fix the data quality problem through systematic stages (triage, semantic typing, careful extraction with vocabulary grounding), validate on hand-curated papers, and then connect the clean evidence base to the theoretical infrastructure that already exists.

---

**Document prepared by Claude Code**
**For the ATLAS system Master Paper**
**February 24, 2026**



### § 122: QA Agent Specification {#§122}

**From Panel QA Meeting (Feb 16, 2026)**: The system requires automated quality assurance to enforce consistency, prevent regressions, and validate changes before deployment.

**Automated Checks** (Run on every template commit):

1. **Schema Validation**: Every template matches the standardized JSON schema. Required fields present, data types correct, no extraneous fields.

2. **Bridge Warrant Ceiling Enforcement**: Template confidence ≤ bridge warrant base confidence. E.g., THEORY_DERIVED warrant (base 0.40) cannot have confidence 0.42. Action on violation: Automatic downgrade of confidence to warrant base.

3. **Cross-Template Consistency**: If template A feeds into template B, check that A's output type matches B's input type. Example: VIEW1 outputs "arousal reduction"; ART (attention restoration) takes "sustained attention state" as input. Potential mismatch check: Is arousal reduction sufficient for attention restoration? QA agent flags for expert review.

4. **Variable Registration Check**: Every variable in mechanism chain must be registered in unified vocabulary. Unregistered variables flagged. Must be resolved before commit.

5. **Provenance Verification**: Every effect size estimate must be traceable to a source article. QA agent checks that article is in Master Reference Inventory, DOI is resolvable, and extraction record exists.

**Expert-Required Checks** (Manual review):

1. **Mechanism Plausibility**: Is the proposed mechanism chain neurobiologically plausible? Example: Does hypothesized dopamine release pathway match known anatomy? Expert neuroscientist review required.

2. **Ecological Validity**: Are the effect sizes estimated in lab settings likely to hold in real-world architectural contexts? Example: Nature view stress-recovery effect found in 10-minute lab exposure; will 30-second glance from an office window still show effect? Ecologist/practitioner review required.

3. **Cultural Appropriateness**: Does the template make assumptions about human universals that may not hold across cultures? Example: Eye contact (SOCIAL-I template) is valued in Western cultures but avoided in some other cultures. Cultural sensitivity review required.

**QA Workflow**:

1. Contributor proposes template changes (new template, confidence update, mechanism revision).
2. Automated checks run. If violations found, commit is blocked, contributor is notified.
3. If automated checks pass, template is flagged for expert manual review (queue of 3–5 experts).
4. Experts deliberate asynchronously (Slack/email), provide sign-off or request revisions.
5. Upon expert approval (≥2 out of 3 required), template is committed to main branch.

**Current QA Status**: 112 bridge warrant violations identified (templates with confidence exceeding warrant), requiring expert review. Target: Clear all violations within Q1 2026.

---

### § 123: Gap Tracker (153 Gaps, 116 High-Severity) {#§123}

**Gap Definition**: Absence of empirical evidence, theoretical understanding, or methodological specification required for template use.

**153 Total Gaps**, distributed:

- **MECHANISM gaps (68)**: Missing or weak causal mechanism characterization.
  - Example: OLFACTORY_MOOD_ASSOCIATION has no identified neural pathway; proposed dopaminergic mechanism is pure speculation.

- **BOUNDARY gaps (42)**: Parameter ranges, population limits, or contextual conditions incompletely specified.
  - Example: CEILING_HEIGHT template effects on creativity are well-documented for Western adult office workers. But effects on children, elderly, non-Western populations, and non-office contexts are unknown.

- **VALIDATION gaps (25)**: Mechanism chain components tested independently but not as integrated sequence.
  - Example: Each step in VIEW1 chain (visual transduction, threat detection, prediction-error, dopamine, PFC modulation) has supporting evidence. But the full chain has never been measured simultaneously in humans.

- **INTERACTION gaps (18)**: Cross-template interaction uncharacterized.
  - Example: How does VIEW1 interact with THERMAL_COMFORT? Do nature views provide benefit even when person is thermally uncomfortable? Unknown.

**Severity Classification**:

- **High (116 gaps)**: Blocks high-value predictions or design recommendations. Fixing would increase system utility substantially.
- **Medium (27 gaps)**: Limits scope or confidence but does not block primary use cases.
- **Low (10 gaps)**: Addresses edge cases or rarely-used templates.

**Gap-to-Experiment Pathways**: Each gap maps to a testable study design. Example:

**Gap**: CEILING_HEIGHT effects on creativity for children (boundary gap)

**Proposed Study**:
- **Design**: 3×2 factorial: ceiling height (2.5m, 3.5m, 4.5m) × age group (7–10 years old, 10–13 years old)
- **Task**: Torrance Tests of Creative Thinking (divergent thinking)
- **Outcome**: Idea generation, originality, flexibility scores
- **Hypothesis**: Ceiling height effect generalizes across age groups (ceiling effect same size for children as for adults, *d* ≈ +0.35)
- **Sample size**: n=120 (20 per cell)
- **Cost estimate**: ~$15K (researcher time, incentives)
- **Timeline**: 4 months
- **Expected outcome**: If hypothesis confirmed, remove boundary gap; if not, add age-dependent moderation function to template

**Gap Priority Ordering** (Next 10 priorities):

1. THERMAL_COMFORT × STRESS-I interaction (blocks office remediation designs)
2. CEILING_HEIGHT boundary for children (blocks school design)
3. OLFACTORY_MOOD mechanism (fills major evidence gap)
4. NOVELTY_OPTIMAL × CREATIVITY interaction (refines creative space design)
5. VIEW1 boundary for non-Western cultures (expands applicability)
6. MUSICAL_TEMPO × AROUSAL interaction (refines acoustic design)
7. PRIVACY_REGULATION causal mechanism (is privacy sufficient for intimacy?)
8. CIRCADIAN_ALIGNMENT effects >1 week duration (tests habituation)
9. VISUAL_FRACTAL boundary for older adults (vision-specific effects)
10. NOISE-I × SPEECH_INTELLIGIBILITY interaction (refined for hearing-impaired)

---


**SECTION A: The QA Agent**
- §122.2: QA Agent Architecture and Expert Panel Design
- §122.3: Progressive Disclosure and Bounded Rationality
- §122.4: Query Classification and Routing
- §122.5: Molecule Registry and Precomputation

# SECTION A: THE QA AGENT

## §122.2: QA Agent Architecture and Expert Panel Design

### Philosophical Foundations

The Article Eater QA agent represents a convergence of four distinct intellectual traditions: cognitive science explanation theory, human-computer interaction design, pedagogical learning science, and information visualization. Rather than implementing these traditions separately, the system integrates them through an expert panel methodology that yields design principles all four traditions endorse.

The design panel—henceforth P-QA (Panel for Question-Answering)—consists of world-leading experts deliberately chosen to represent different epistemological commitments:

**Explanation and Epistemology**: Peter Lipton (Cambridge) contributed the theory of Inference to Best Explanation (IBE), which argues that a good explanation is one we would infer to—not because it is provable, but because it is *lovely*: unified, mechanistic, precise, and appropriately scoped. In the QA context, Lipton's work ensures that answers do not merely provide information but achieve explanatory coherence, addressing not just the user's question but the deeper question of *why* they are asking it.

**Developmental and Learning Explanation**: Alison Gopnik (UC Berkeley) brought developmental cognitive science perspectives. Gopnik's research on how children learn through causal reasoning and how expertise develops showed the panel that users do not reason about explanations as isolated claims; they use explanations as tools for *learning*. A good explanation provokes inference, highlights deep structure, and invites further questions. This insight directly influenced the progressive disclosure design—each level should be complete and generative, enabling the user to draw further conclusions.

**Pedagogical Knowledge Building**: Carl Bereiter (Toronto) contributed the distinction between *knowledge-telling* (reporting facts) and *knowledge-building* (constructing understanding). Bereiter showed the panel that the same user shifts between modes: sometimes seeking quick facts, sometimes seeking deep understanding. The QA agent must be able to recognize and adapt to this mode-switching. The system tracks not just what the user knows but what kind of cognitive work they are doing.

**Information Visualization and Interaction Design**: Ben Shneiderman (Maryland) provided the foundational principle of *progressive disclosure*—the insight that complex information should be revealed in layers, with each layer being complete at its level and accessible without requiring deeper levels. Shneiderman's "Visual Information Seeking Mantra" (Overview first, zoom and filter, then details on demand) became the architectural principle for the entire system.

### The Convergence: Design Principles All Four Traditions Endorse

From this four-way conversation emerged seven principles that no single tradition would have generated alone:

**P1: Answer the Actual Question First.** Lipton emphasized that a good explanation addresses the questioner's actual information need, not a different question that seems easier to answer. In QA terms: lead with a direct answer before elaboration. This principle protects against the tendency of expert systems to provide comprehensive treatments that obscure the simple answer the user sought.

**P2: Match Depth to User Type.** Gopnik and Bereiter together emphasized that novices and experts have fundamentally different knowledge structures. A novice does not need the full mechanism; they need anchors to attach new learning. An expert does not want surface generalities; they want theoretical depth. The system must model the user and adjust.

**P3: Enable Controlled Deepening.** Bereiter and Shneiderman converged on this principle. The user should be able to request more depth at any point, but the system should not require it. Each depth level should be self-contained. This respects both the user's autonomy and the principle that learning is active—users learn better when they control the pacing of revelation.

**P4: Make Depth Levels Explicit.** The Lipton-Salmon tradition (mechanistic explanation) emphasizes that different "whys" require different answers. Salmon distinguished descriptive, causal, mechanical, and constitutive levels. The system makes explicit what level it is operating at, preventing confusion between correlation and mechanism or between behavioral and neural explanations.

**P5: Preserve Coherence Across Levels.** Lipton's emphasis on coherence matters here. Deeper explanations should extend shallower ones, never contradict them. If a Level 1 answer says "nature views reduce stress," a Level 3 mechanistic answer should explain *how* nature views reduce stress, not introduce conflicting evidence that undermines the Level 1 claim. Coherence is an epistemic virtue.

**P6: Acknowledge Uncertainty Honestly.** Shneiderman's interface design principle that "users should always know where they are" extends to epistemic certainty. A good answer signals its confidence level. Lipton's work on inference emphasizes that inference to best explanation is not certainty; it is reasonable confidence in a particular direction. Confidence markers throughout enable users to calibrate trust.

**P7: Enable Action.** The final principle bridges explanation and application. An explanation is incomplete if it does not connect to what the user can do with it. For a designer, a theoretical answer must yield actionable design parameters. For a researcher, it must suggest experiments. For a student, it must enable application to new cases.

### Architecture Overview

The QA agent operates through a layered pipeline:

```
User Query
    ↓
Query Understanding Layer
    ├─ Question type classification (25 types)
    ├─ Entity extraction (molecules, components, mechanisms)
    ├─ Depth request detection
    └─ Context and mode inference
    ↓
User Model Layer
    ├─ Expertise level estimation
    ├─ Current mode detection (quick lookup vs. deep understanding)
    ├─ Application context (design, teaching, research, evaluation)
    └─ Session history and depth trajectory
    ↓
Response Planning Layer
    ├─ Template selection (by question type)
    ├─ Depth level determination (by user model)
    ├─ Progressive disclosure planning
    └─ Cross-reference identification
    ↓
Knowledge Retrieval Layer
    ├─ Web of Belief query
    ├─ Molecule registry lookup (precomputed summaries)
    ├─ Evidence chain retrieval
    ├─ Stability and certainty metadata
    └─ Community-relative credences
    ↓
Response Generation Layer
    ├─ Template instantiation
    ├─ Depth-appropriate filtering
    ├─ Confidence marker insertion
    └─ Progressive disclosure prompt generation
    ↓
Quality Assurance Layer
    ├─ Accuracy verification against knowledge base
    ├─ Depth appropriateness check
    ├─ Coherence validation
    └─ Disclosure option availability
    ↓
User Interface
```

This architecture embodies the panel's consensus that good QA requires not just good content but good structure, user modeling, and progressive interaction.

---

## §122.3: Progressive Disclosure and Bounded Rationality

### Herbert Simon's Bounded Rationality as Design Principle

The three-level (actually five-level) architecture of the QA agent is grounded in Herbert Simon's observation that human cognition is bounded. Simon argued that people cannot optimize across infinite options; instead, they *satisfice*—they seek explanations that are good enough for their current purpose, using the cognitive resources available to them.

The QA agent respects bounded rationality by offering a "three-level" structure at its core, with two additional levels available for those who want them:

**Level 1: Executive Summary (1-2 sentences)**
The most bounded user needs the fewest facts. This level provides a direct yes/no/it-depends answer plus a confidence qualifier. Example: "Yes, high ceilings generally facilitate creative thinking (d ≈ 0.4), but only for divergent thinking tasks, not convergent ones."

This level acknowledges uncertainty while providing the user's requested fact. It is complete at its level—a user who needs nothing more has what they need. But it is also designed to invite deeper inquiry if the user has time: the mention of "divergent vs. convergent" creates curiosity about task differences.

**Level 2: Contextualized Answer (1 paragraph)**
This level adds the key moderators and mechanism hints needed for orientation. If the user has invested 30 seconds, they can learn what conditions affect the effect and get a thumbnail sketch of why it happens. Example: "High ceilings facilitate divergent thinking through conceptual metaphor priming (height primes 'freedom,' which broadens associative processing). The effect is stronger for brainstorming than for detail-focused tasks. Evidence quality is moderate—good original studies but limited direct replications."

This level bridges the gap between factual recall (L1) and mechanistic understanding. It is the level where most practical questions can be answered. A practitioner deciding whether to raise the ceiling has enough information. A teacher preparing a lecture can work with this. A designer can make a provisional decision and seek deeper confirmation if needed.

**Level 3: Mechanistic Explanation (3-5 paragraphs)**
For users in "understanding" mode, this level provides the cognitive/perceptual mechanisms and shows where evidence comes from. It is organized around the mechanism chain: what changes (perceptual input) → what responds (attentional system) → what happens (behavioral consequence). It includes boundary conditions and explicit treatment of competing mechanisms.

**Level 4: Multi-Level Integration (5-10 paragraphs)**
Users in "integration" mode (connecting different frameworks) or "evaluation" mode (assessing competing theories) get accounts that deliberately cross levels of explanation: cognitive, neural, computational, evolutionary. The system shows how the levels relate—which mechanisms are "deep" (evolutionarily ancient, neural-level) and which are "surface" (culturally specific, behavioral-level).

**Level 5: Critical Scholarly Analysis (full treatment)**
For researchers and deep critics, this level provides state-of-evidence summaries, methodology critiques, open questions, and research agendas. It is the depth at which a review article lives. It acknowledges limitations, competing evidence, and genuine uncertainty.

### User Typology and Depth Tolerance

The panel identified two dimensions that predict depth tolerance:

**Knowledge-level dimension (novice → expert):**
- Introductory undergraduates: prefer L1-L2, cannot use specialized vocabulary, need definitions
- Advanced undergraduates: can handle L2-L3, understand basic mechanisms, start to see theory
- Masters students: want L3-L4, care about boundary conditions and experimental design
- Early PhD students: seek L4-L5, want alternatives and gaps, theoretically sophisticated
- Late PhD students and professors: can deploy multiple depths rapidly, move between quick lookup and deep analysis

**Cognitive mode dimension (quick fact → deep understanding):**
The *same* person operates in different modes depending on context. A professor might need Level 1 when writing a lecture ("what's the main finding?"), Level 4 when designing research ("how do the neural and behavioral accounts relate?"), and Level 2 when talking to a journalist ("how would you explain this to someone not trained in science?").

The system learns these modes within a session and adjusts expectations. If a user asks "why?" three times in a row, the system shifts to deeper levels. If they say "briefly," the system compresses to L1-L2.

### How Depth Tolerance Varies: Six User Modes

**Mode 1: Quick Lookup.** "Is X true?" User has 10 seconds. Deliver L1 with high confidence markers. Example context: student fact-checking for an essay, practitioner verifying a design assumption, journalist getting facts straight.

**Mode 2: Orientation.** "What's the landscape here?" User is new to the topic and wants an overview + pointers. Deliver L2 + links to related concepts. Example: undergraduate choosing an essay topic, researcher surveying a new domain, architect exploring an unfamiliar psychology topic.

**Mode 3: Understanding.** "I want to genuinely understand this." User has time and motivation to learn. Deliver L3 with explicit mechanism. The system should invite questions and offer branching paths. Example: student writing a thesis, researcher designing an experiment, designer wanting to understand *why* a design rule works.

**Mode 4: Integration.** "How does this connect to other things I know?" User is synthesizing across frameworks. Deliver L4 with explicit cross-level connections. Help them see how this theory relates to others they know. Example: theorist building a comprehensive framework, researcher developing an interdisciplinary perspective, student preparing for comprehensive exams.

**Mode 5: Evaluation.** "How strong is this evidence?" User is critical, skeptical, wanting to assess credibility. Deliver L3-L4 with heavy emphasis on evidence quality, methodology, and competing accounts. Acknowledge limitations. Example: journal reviewer, dissertation committee member, expert witness, researcher criticizing others' work.

**Mode 6: Application.** "What should I do with this?" User wants implications and actionability. Deliver L2-L3 with explicit design implications and confidence levels for each recommendation. Be honest about what we don't know. Example: architect, designer, policy maker, clinician, executive decision-maker.

The system detects mode from question structure: "Is X true?" → Lookup; "What's X?" → Orientation; "Why X?" → Understanding; "How does X relate to Y?" → Integration; "How strong is the evidence?" → Evaluation; "What should I do?" → Application.

### The Three-Sentence Phenomenon

The panel noticed an interesting empirical pattern: users seem to satisfice at around 3 sentences of explanation (roughly 45-60 words). A well-written Level 1 answer is 1-2 sentences. A well-written Level 2 answer is typically 3-5 sentences (one per component: direct answer, key moderator, evidence quality, mechanism hint, limitation). Level 2 is the "natural" stopping point for people with limited time.

This suggests that the system design should make Level 2 particularly polished. Level 1 is for the busy; Level 2 is for the thoughtful; Levels 3+ are for the committed. Getting Level 2 right serves the most people.

---

## §122.4: Query Classification and Routing

### The MoleculeAwareRouter: Natural Language to Structured Knowledge

Users do not speak in database queries. They ask questions in natural language, with all its ambiguity and context-dependency. The system must map natural language questions to structured knowledge—identifying which "molecule" (tier-2 construct) they are asking about, at what depth, and in what mode.

The MoleculeAwareRouter addresses this through two mechanisms: fast path (precomputed) and synthesis path (live LLM).

**Fast Path (Precomputed)**: If the query asks directly about a molecule ("What is Attention Restoration Theory?" or "How does ART work?"), the router matches it against the molecule registry and returns precomputed summaries. This path is fast (cached answers) and consistent (human-vetted content). Examples:

- Query: "Tell me about attention restoration."
  Classification: MOLECULE_LOOKUP ("Attention Restoration Theory")
  Depth detected: 2 (from question phrasing "tell me about")
  Response: Retrieve precomputed L2 summary from cache

- Query: "How do biophilic design and stress reduction relate?"
  Classification: MOLECULE_LOOKUP (both "Biophilia" and "Stress Recovery Theory")
  Depth: 3 (comparative "how...relate" structure)
  Response: Retrieve both L3 summaries, synthesize comparison

**Synthesis Path (Live LLM)**: If the query asks about design synthesis ("How should I balance daylight with glare in a classroom?") or crosses multiple molecules ("What does environmental psychology say about creative spaces?"), the router invokes live LLM synthesis. The LLM has access to the entire Web of Belief, the molecule summaries (as context), and the QA templates. It generates a novel response by synthesizing across the knowledge base.

### Query Classification: 25+ Question Types

The panel identified 25 question types, organized by what kind of answer they require:

**Empirical/Descriptive (What happens?)**
1. **Effect existence**: "Does X affect Y?" → Yes/no with qualifier; show direction and confidence
2. **Effect size**: "How much does X affect Y?" → Quantify (d, r, etc.); show range if contested
3. **Effect direction**: "Does X increase or decrease Y?" → Direct answer + confidence
4. **Effect reliability**: "Is this effect replicated?" → Replication status; confess limitations
5. **Population variation**: "Do [subgroup] respond differently?" → Show boundary conditions
6. **Boundary conditions**: "Does this hold for [context]?" → Systematic condition check
7. **Temporal dynamics**: "How long does the effect last?" → Time course; distinguish acute/chronic

**Mechanistic (How does it work?)**
8. **Proximate mechanism**: "How does X affect Y?" → Identify causal chain; specify level
9. **Neural substrate**: "What brain regions respond to X?" → Map neural systems; acknowledge speculation
10. **Computational account**: "How would [theory] explain this?" → Apply computational framework
11. **Pathway identification**: "Is it via A or B?" → Distinguish mediating mechanisms
12. **Multi-level integration**: "How do cognitive, neural, and behavioral levels connect?" → Show coherence

**Explanatory (Why does it happen?)**
13. **Functional why**: "Why would [mechanism] evolve?" → Appeal to function/fitness
14. **Developmental why**: "Why do children/adults differ?" → Developmental trajectory
15. **Contrastive why**: "Why X but not Y?" → Identify difference-makers (Lipton)
16. **Comparative why**: "Why is A stronger than B?" → Compare effect sizes and mechanisms

**Methodological (How do we know?)**
17. **Evidence assessment**: "How strong is the evidence?" → Quality metrics; study-by-study summary
18. **Measurement critique**: "Can X be measured validly?" → Methods assessment; known limitations
19. **Study design**: "What would be a good experiment?" → Suggest design with controls
20. **Paradigm limitations**: "Why do different methods disagree?" → Address methodology bias

**Applied/Design (What should I do?)**
21. **Design recommendation**: "What should I do about X?" → Actionable advice; confidence levels
22. **Trade-off navigation**: "How do I balance X and Y?" → Multi-criteria decision framework
23. **Confidence assessment**: "How confident should I be?" → Calibrate expectations; mention gaps

**Generative/Exploratory (What's interesting?)**
24. **Topic discovery**: "What are interesting questions about X?" → Open questions; gaps
25. **Gap identification**: "Where is evidence weakest?" → Honest uncertainty assessment
26. **Connection finding**: "How does X relate to Y?" → Theory integration
27. **Controversy mapping**: "What do researchers disagree about?" → Genuine disagreements; no consensus

### Depth Detection from Question Structure

Beyond question type, the system infers requested depth from linguistic markers:

- **L1 signals**: "Is...", "Do...", "Briefly", "Quick", "TL;DR", "Just tell me"
  → Deliver 1-sentence answer

- **L2 signals**: "What is...", "How does...", "Tell me about", "Explain", "Context"
  → Deliver 1-paragraph contextualized answer

- **L3 signals**: "Why...", "How exactly...", "What mechanism", "Full explanation"
  → Deliver mechanistic 3-5 paragraph treatment

- **L4 signals**: "How do...levels connect", "What's the neural basis", "Computational perspective", "Comparative", "Theory integration"
  → Deliver multi-level 5-10 paragraph synthesis

- **L5 signals**: "Give me everything", "Comprehensive", "Review", "Critique", "Gaps", "Methodology", "State of evidence"
  → Deliver full scholarly treatment with methodology section

The system also tracks depth requests *in conversation*. If a user asks an L2 question and then says "Why?" the system escalates to L3 for the follow-up, maintaining depth coherence throughout the session.

---

## §122.5: Molecule Registry and Precomputation

### What is a "Molecule"?

A "molecule" is a tier-2 construct in the ATLAS system—a specific, calibrated claim about how an environmental feature affects a neural mechanism and produces an occupant outcome. Examples include:

- "High ceilings facilitate divergent thinking through broadened conceptual association"
- "Natural views reduce physiological stress through soft fascination and attention restoration"
- "Fractal complexity in architectural surfaces enhances pattern recognition fluency"

Each molecule is a complete claim with:
- **What**: The environmental feature (e.g., "ceiling height")
- **How**: The mechanism (e.g., "conceptual metaphor priming")
- **That**: The outcome (e.g., "divergent thinking")
- **When**: The scope conditions (e.g., "for creative tasks, not detail-focused tasks")
- **Why**: The theoretical grounding (e.g., "Broaden-and-Build, Conceptual Metaphor Theory")

A molecule differs from a loose belief or a research finding. It is a *designed* knowledge unit with clear boundaries, explicit scope conditions, and calibrated confidence.

### Multi-Level Precomputed Summaries

For each molecule, the system precomputes summaries at each depth level:

**L1 Summary** (1-2 sentences)
- Direct claim + confidence + key boundary condition
- Generated by human expert; reviewed by domain panel
- Cached and versioned

**L2 Summary** (1 paragraph)
- L1 + key moderators + evidence basis + mechanism hint
- Shows effect size (with confidence interval)
- Lists what we're uncertain about

**L3 Summary** (3-5 paragraphs)
- Full mechanistic account with sub-processes
- Evidence section (which studies support this)
- Moderators section (what changes the effect)
- Boundary conditions section (when it doesn't apply)

**L4 Summary** (5-10 paragraphs, if available)
- Multi-level integration: cognitive, neural, computational, evolutionary levels
- Explicit cross-level connections
- Alternative mechanisms and why we favor this one

**L5 Summary** (full treatment, if available)
- Systematic evidence review (study-by-study)
- Methodology critique (what's strong, what's weak)
- Open questions and research agenda

Not all molecules have L4 and L5 summaries yet. These are progressively built as the system matures. L1-L3 are mandatory for all molecules.

### Cache Management: Staleness, Invalidation, Versioning

Precomputed summaries are not fixed. As new evidence enters the Web of Belief, credences update, and cached summaries can become stale. The system manages this through three mechanisms:

**Staleness Detection**: Each cached summary is tagged with:
- `cached_at`: Timestamp when computed
- `based_on_web_version`: Version of Web of Belief it was computed from
- `credence_at_cache_time`: What was the credence then

When a summary is retrieved, the system checks: has the underlying credence changed significantly since caching? If the current credence differs by >0.1 from cached credence, the summary is flagged as "potentially stale."

**Invalidation Rules**: Stale summaries are invalidated (not shown) if:
- The Web of Belief version has advanced by >2 major revisions
- New evidence has entered that directly contradicts the cached summary
- The molecule's scope conditions have changed

**Versioning**: Cached summaries are versioned. If summary X was cached when the molecule's credence was 0.65 and is now 0.78, the system can serve the cached summary with a note: "Based on credence 0.65; current credence is 0.78 (more confident)."

This design respects two important principles: (1) users get fast, cached answers when available, and (2) users are never misled by stale cached content. The system is transparent about what it cached and when.

### Cost Optimization: Gemini 2.5-Flash for Precomputation

Precomputing summaries at all depths for hundreds of molecules is computationally expensive. The system uses Gemini 2.5-Flash (a fast, inexpensive model) for the precomputation pipeline, because:

1. **Fast**: Precomputation happens offline, not during user queries
2. **Cheap**: 2.5-Flash is far less expensive than Claude or GPT-4
3. **Good enough**: The summaries are human-reviewed before caching, so imperfect LLM output is acceptable
4. **Consistent**: Flash models have consistent output, making it easier to detect changes

The flow is:
1. Human expert writes L1-L2 summaries; submits molecule
2. Gemini 2.5-Flash expands L2 → L3 mechanistic summary (with human review)
3. If L4 is needed, a human expert writes it or Gemini 2.5-Flash drafts it (for review)
4. All summaries cached with version metadata
5. On query, fast lookup in cache; if stale, regenerate using 2.5-Flash or human expert

This creates a pyramid: many L1-L2s (human + machine), fewer L3s (machine + review), few L4-L5s (human expert only). The system allocates effort proportionally to depth and complexity.

---


### § 124: System Visualization {#§124}

**Four Visualization Types**:

**1. Architecture Layer Diagram** (7-layer system representation, described in § 120)

**2. Theory Dependency DAG** (Directed Acyclic Graph of template dependencies)

- **Nodes**: 103 calibrated templates + 105 scaffold templates
- **Edges**: "Feeds into," "moderated by," "competes with" relationships
- **Visualization**: Hierarchical layout, color-coded by confidence level (red ≤0.40, yellow 0.40–0.50, green 0.50–0.55)
- **Utility**: Identifies clusters of highly interdependent templates, shows which templates are foundational (many others depend on them) vs. peripheral

**3. Template Interaction Network** (Force-directed graph of 440 documented interactions)

- **Nodes**: 103 calibrated templates, sized by connectivity degree
- **Edges**: Interaction type color-coded (enhancement=blue, synergy=green, negation=red, distortion=orange, etc.)
- **Utility**: Shows which template pairs interact frequently (should be prioritized for study), identifies isolated templates (no documented interactions)

**4. Evidence Landscape** (2D scatter plot: effect size vs. evidence quality)

- **X-axis**: Effect size (Cohen's *d*, 0–1.0)
- **Y-axis**: Evidence tier (A–D, higher is better)
- **Points**: Templates, sized by confidence value, colored by domain
- **Utility**: Identifies high-confidence predictions (upper right), weak evidence predictions (lower left), outliers

**Interactive Dashboard** (Planned for Q2 2026):

Web-based interface allowing practitioners to:
- Search for templates by domain, activity, or outcome
- View mechanism chains with expand/collapse detail levels
- See interaction effects with other templates
- Check boundary conditions and applicability
- Report outcomes of implemented designs (feedback loop for calibration)

---

---

