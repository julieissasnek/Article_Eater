# Part XXVIII: Article Classification and Field Schema Reference

*Date: 2026-03-05*
*Version: V4.0 Staged Extraction*
*Status: Formative specification — governs all extraction pipeline behavior*

---

## §185. The Classification Problem and Its Architectural Consequences

Classification is the single most consequential decision in the extraction pipeline. Every downstream operation — which prompt template is used, which fields are required, what quality thresholds apply, how findings are validated — depends on correctly identifying the article type. A misclassification cascades: an empirical paper classified as a narrative review will never be asked for p-values, effect sizes, or sample sizes, and those fields will be permanently absent from the knowledge base.

### §185.1 Current Architecture: Who Classifies, and When

In the V4 staged extraction pipeline, classification occurs at **Stage 1** and is performed by the **same model that will do the extraction** (currently Gemini 2.5 Flash). The pipeline sends the full PDF to Gemini with a classification prompt (defined in `v4_prompts.py :: PROMPT_CLASSIFY_V4`) and receives back a JSON object containing:

```json
{
  "article_type": "EMPIRICAL_RESEARCH",
  "family_group": "empirical",
  "classification_confidence": 0.95,
  "classification_signals": ["Methods section present", "sample_size reported", ...],
  "brief_rationale": "why this classification"
}
```

The `article_type` value then determines which **family-specific extraction prompt** is used in Stage 2. The mapping is:

| Classification → | Stage 2 Prompt | Family Group |
|-----------------|---------------|--------------|
| EMPIRICAL_RESEARCH | `PROMPT_EMPIRICAL_V4` | empirical |
| META_ANALYSIS | `PROMPT_META_ANALYSIS_V4` | review |
| SYSTEMATIC_REVIEW | `PROMPT_SYSTEMATIC_REVIEW_V4` | review |
| NARRATIVE_REVIEW | `PROMPT_NARRATIVE_REVIEW_V4` | review |
| THEORETICAL | `PROMPT_THEORETICAL_V4` | theoretical |
| QUALITATIVE | `PROMPT_QUALITATIVE_V4` | qualitative |
| INSTRUMENT_VALIDATION | `PROMPT_INSTRUMENT_V4` | methods |
| MIXED_METHODS | `PROMPT_EMPIRICAL_V4` (default) | empirical |
| OBSERVATIONAL | `PROMPT_EMPIRICAL_V4` (default) | empirical |
| LONGITUDINAL | `PROMPT_EMPIRICAL_V4` (default) | empirical |
| INTERVENTION_DESIGN | `PROMPT_EMPIRICAL_V4` (default) | empirical |
| COMPARATIVE_ANALYSIS | `PROMPT_EMPIRICAL_V4` (default) | empirical |
| CONCEPTUAL_FRAMEWORK | `PROMPT_THEORETICAL_V4` (default) | theoretical |
| REPORT | `PROMPT_NARRATIVE_REVIEW_V4` (default) | review |
| COMMENTARY | `PROMPT_NARRATIVE_REVIEW_V4` (default) | review |

**Architectural concern**: Notice that 8 of the 15 canonical types default to the empirical or narrative review prompts. This means the system currently has only **7 truly distinct extraction templates** for 15 article types. Types like LONGITUDINAL, OBSERVATIONAL, and INTERVENTION_DESIGN have meaningfully different extraction needs (e.g., longitudinal studies need time-point data, intervention designs need protocol details) that the generic empirical prompt does not address.

### §185.2 The Case for Pre-Classification by a Stronger Model

There is a strong argument — which David has raised — that classification should not be delegated to the extraction model, particularly when that model is a cost-optimized one like Gemini Flash. The reasoning:

1. **Classification is cheap but consequential.** A single classification call costs fractions of a cent. A misclassification wastes the entire extraction call and produces systematically wrong output.

2. **Classification requires domain judgment.** Distinguishing a systematic review from a narrative review, or an empirical study from an observational one, often requires understanding disciplinary conventions that cheaper models may not grasp. For example, many environmental psychology papers combine survey data with quasi-experimental designs — is that EMPIRICAL_RESEARCH or MIXED_METHODS? The answer determines whether we demand effect sizes.

3. **The 7-panel schema was designed for human navigation.** David's original 7-panel system was built to let a reader quickly locate what matters in a paper. The classification determines which panels are relevant. Getting it wrong defeats the purpose.

**Recommendation**: Pre-classify with Claude Opus (or have the gold-standard extractions serve as classification ground truth), then pass the classification to whatever model does extraction. This decouples classification quality from extraction cost.

---

## §186. The 15 Canonical Article Types: Definitions and Discrimination Criteria

### Type 1: EMPIRICAL_RESEARCH

**Definition**: Original data collection with quantitative analysis. The paper presents experiments, surveys, or field studies conducted by the authors, with a Methods section describing procedures and a Results section reporting statistical tests.

**Discrimination signals**:
- Has explicit Methods and Results sections
- Reports original sample (N = ...)
- Contains statistical tests (t, F, χ², regression)
- Has tables with means, SDs, p-values
- May include figures of experimental setup or stimuli

**Common confusions**:
- vs. OBSERVATIONAL: Empirical implies researcher-designed conditions (manipulation); observational is naturalistic measurement without intervention
- vs. MIXED_METHODS: If the paper has *both* quantitative results *and* qualitative themes (e.g., interviews + surveys), it is MIXED_METHODS
- vs. INSTRUMENT_VALIDATION: If the primary purpose is validating a scale/instrument rather than testing a hypothesis, it is INSTRUMENT_VALIDATION

### Type 2: META_ANALYSIS

**Definition**: Quantitative synthesis of multiple studies using pooled effect sizes. Computes aggregate statistics across k studies.

**Discrimination signals**:
- Reports "k studies" or "k = NN"
- Contains forest plots
- Reports pooled/aggregate effect sizes (d, g, r) with confidence intervals
- Reports heterogeneity statistics (I², Q, τ²)
- May include funnel plots (publication bias assessment)

**Common confusions**:
- vs. SYSTEMATIC_REVIEW: A systematic review follows PRISMA but may not compute pooled effects. If there are forest plots and pooled effect sizes, it is a meta-analysis. Some papers are both — classify as META_ANALYSIS if pooled effects are present.
- vs. NARRATIVE_REVIEW: A narrative review never has pooled statistics.

### Type 3: SYSTEMATIC_REVIEW

**Definition**: Structured literature review following a defined protocol (typically PRISMA), with explicit search strategy, inclusion/exclusion criteria, and bias assessment, but without quantitative pooling of effect sizes.

**Discrimination signals**:
- PRISMA flowchart
- Explicit search strategy (databases, date ranges, keywords)
- Inclusion/exclusion criteria table
- Risk of bias assessment
- Structured evidence tables
- No forest plots or pooled effect sizes

**Common confusions**:
- vs. META_ANALYSIS: If pooled effects are computed → META_ANALYSIS
- vs. NARRATIVE_REVIEW: Systematic reviews have explicit, reproducible search methodology; narrative reviews do not

### Type 4: NARRATIVE_REVIEW

**Definition**: Traditional literature overview that synthesizes and discusses prior work without a systematic search protocol. The author's expertise and judgment guide the selection and interpretation of studies.

**Discrimination signals**:
- "This paper reviews..." or "We examine the literature on..."
- No PRISMA flowchart
- No systematic search strategy
- Author-selected references
- Emphasis on interpretation and synthesis rather than exhaustive coverage

**Common confusions**:
- vs. SYSTEMATIC_REVIEW: Narrative reviews lack the methodological apparatus (PRISMA, search protocols, bias assessment)
- vs. THEORETICAL: Theoretical papers propose new frameworks; narrative reviews survey existing ones. If the paper's primary contribution is a new model or framework → THEORETICAL
- vs. COMMENTARY: Commentaries are shorter, opinion-driven, and respond to specific papers. Narrative reviews are comprehensive surveys.

### Type 5: THEORETICAL

**Definition**: Proposes or develops a conceptual framework, theoretical model, or set of propositions without presenting original empirical data. The contribution is the framework itself.

**Discrimination signals**:
- "We propose a framework..." or "This paper develops a model..."
- Diagrams of theoretical models (box-and-arrow figures)
- Lists of propositions or hypotheses for future testing
- No Methods/Results sections (or only illustrative examples)
- May review literature to support the framework, but the framework is the contribution

**Common confusions**:
- vs. NARRATIVE_REVIEW: If the paper surveys literature without proposing a new framework → NARRATIVE_REVIEW
- vs. CONCEPTUAL_FRAMEWORK: These are synonymous; classify as THEORETICAL

### Type 6: QUALITATIVE

**Definition**: Uses qualitative methods (interviews, ethnography, phenomenology, grounded theory, thematic analysis) as the primary methodology. Data are words, observations, or experiences rather than numbers.

**Discrimination signals**:
- "Semi-structured interviews" or "focus groups"
- "Thematic analysis" or "grounded theory" or "phenomenological"
- Participant quotes as evidence
- Themes/categories as findings (not statistical tests)
- Often small N with rich description

**Common confusions**:
- vs. MIXED_METHODS: If the paper has both qualitative themes AND quantitative statistics → MIXED_METHODS
- vs. REPORT: Case studies with qualitative data may be either. If the methodology is explicitly qualitative (thematic analysis, etc.) → QUALITATIVE

### Type 7: MIXED_METHODS

**Definition**: Combines quantitative and qualitative data collection and analysis within a single study. Both types of evidence contribute to the findings.

**Discrimination signals**:
- Explicit "mixed methods" in title or methods
- Both statistical results AND qualitative themes
- May have separate quantitative and qualitative results sections
- Integration of both data types in discussion

**Common confusions**:
- vs. EMPIRICAL_RESEARCH: If the qualitative component is trivial (e.g., one open-ended question) → EMPIRICAL_RESEARCH
- vs. QUALITATIVE: If the quantitative component is trivial → QUALITATIVE

### Type 8: OBSERVATIONAL

**Definition**: Measures naturally occurring phenomena without researcher manipulation. Includes cohort studies, cross-sectional surveys, case-control studies, and ecological studies.

**Discrimination signals**:
- No experimental manipulation (no random assignment to conditions)
- "We observed..." or "We measured..."
- Correlational or regression analyses (not ANOVA comparing experimental conditions)
- Often larger N than experimental studies
- May involve archival data

**Common confusions**:
- vs. EMPIRICAL_RESEARCH: The key distinction is manipulation. If the researcher assigned participants to conditions → EMPIRICAL. If the researcher measured existing conditions → OBSERVATIONAL.
- In environmental psychology, many studies measure people's responses to existing spaces without manipulation — these are OBSERVATIONAL even if they use surveys.

### Type 9: REPORT

**Definition**: Technical or clinical reports, case studies, design documentation, or project descriptions. Primary purpose is to document rather than to test hypotheses.

**Discrimination signals**:
- "Case study" or "case report"
- Project documentation
- No formal hypothesis testing
- Descriptive rather than inferential

### Type 10: COMMENTARY

**Definition**: Opinion pieces, editorials, perspectives, letters to the editor, or responses to other papers. Short, opinion-driven, and typically without original data.

**Discrimination signals**:
- Short (typically < 3000 words)
- "In response to..." or "We argue that..."
- Published in commentary/opinion section
- No Methods section

### Type 11: LONGITUDINAL

**Definition**: Studies that follow participants over time, with measurements at multiple time points. The temporal dimension is the defining feature.

**Discrimination signals**:
- "Follow-up" or "wave 1, wave 2"
- Time-point comparisons
- Attrition reporting
- Growth curves or trajectory analyses

**Note**: Currently routed to the EMPIRICAL prompt. Needs its own template to capture time-point structure, attrition, and trajectory data.

### Type 12: INTERVENTION_DESIGN

**Definition**: Describes the design of an intervention, often including pilot testing and feasibility assessment, but the primary contribution is the intervention protocol itself.

**Discrimination signals**:
- "Intervention protocol" or "design rationale"
- Logic model or theory of change
- Feasibility/pilot data (small scale)
- Implementation details

**Note**: Currently routed to the EMPIRICAL prompt. Needs its own template to capture intervention components, dosage, and implementation fidelity.

### Type 13: INSTRUMENT_VALIDATION

**Definition**: Primary purpose is to develop, validate, or evaluate a measurement instrument (questionnaire, scale, assessment tool).

**Discrimination signals**:
- Reports Cronbach's alpha, factor loadings
- Confirmatory/exploratory factor analysis
- Test-retest reliability
- Convergent/discriminant validity
- Item analysis

### Type 14: CONCEPTUAL_FRAMEWORK

**Definition**: Synonymous with THEORETICAL. Proposes a new conceptual model. Currently routed to the THEORETICAL prompt.

### Type 15: COMPARATIVE_ANALYSIS

**Definition**: Compares findings, methods, or outcomes across populations, contexts, or time periods. The comparison is the primary contribution.

**Discrimination signals**:
- "Cross-cultural comparison" or "comparative analysis"
- Multiple populations or contexts compared
- Emphasis on similarities/differences rather than main effects

**Note**: Currently routed to the EMPIRICAL prompt.

---

## §187. Field Schema by Article Type

The following tables specify which fields are **critical** (must be extracted for the paper to pass quality control), **expected** (should be extracted if present in the paper), and **optional** (extract if readily available) for each article type.

### §187.1 EMPIRICAL_RESEARCH — Full Field Schema

This is the most demanding extraction template. Environmental psychology papers with experimental designs require every field below.

**Critical Fields** (extraction fails quality if these are missing):

| Field | Description | Example Value | Why Critical |
|-------|-------------|---------------|-------------|
| `antecedent` | Specific, operationalized IV/condition | "Wooden interior (W) vs. control (C) in VR" | Core of the finding — what was manipulated |
| `consequent` | Measured DV/outcome | "Alpha-to-theta ratio (ATR) via EEG" | Core of the finding — what was measured |
| `direction` | increase \| decrease \| no_effect \| mixed | "increase" | Sign of the relationship |
| `claim_type` | Type of epistemic claim | "empirical_finding" | Determines downstream warrant type |
| `p_value` | Statistical significance | 0.007 or "<0.001" | Evidence strength |
| `effect_size` | Magnitude of effect | 0.27 | Practical significance |
| `effect_size_type` | Which metric | "partial_eta_squared" | Needed for cross-study comparison |
| `sample_size` | N of participants | 36 | Statistical power indicator |
| `sample_size_source` | reported \| inferred \| estimated | "reported" | Epistemic confidence in N |
| `test_statistic` | Full test result | "F(3,105) = 4.35, p = .007" | Verifiability |
| `confidence_interval` | [lower, upper] | [0.03, 0.51] | Precision of estimate |
| `instruments_used` | Array of measurement tools | [{name: "STAI", construct: "anxiety"}] | Replication and construct validity |
| `measure_type` | self_report \| behavioral \| physiological \| cognitive_task | "physiological" | Measurement quality indicator |
| `scope_conditions` | Setting, population, duration, etc. | {setting: "laboratory", population: "students"} | Cartwright P4 — where does this hold? |
| `causal_tier` | EXPERIMENTAL \| QUASI_EXPERIMENTAL \| CORRELATIONAL | "EXPERIMENTAL" | Pearl's causal hierarchy |
| `source` | Location in paper | "Results section, Table 3" | Verifiability |
| `quote` | Direct text from paper | "Wooden interior significantly increased ATR..." | Provenance |
| `provenance_depth` | direct_quote \| paraphrase \| inferred | "direct_quote" | Epistemic distance from source |

**Expected Fields** (should be present for a complete extraction):

| Field | Description | Why Expected |
|-------|-------------|-------------|
| `mechanism` | Proposed causal pathway | Understanding *why* the effect occurs |
| `mechanism_chain` | Step-by-step causal chain | Formal mechanism representation |
| `theory_links` | Connected theories | Theoretical grounding |
| `theory_commitments` | How findings relate to theories | Tests, extends, contradicts |
| `moderators_reported` | Variables that moderate the effect | Boundary conditions |
| `stimulus_description` | What participants experienced | Critical for environmental psychology |
| `stimulus_images` | Figures documenting stimuli | Visual verification |
| `source_quality_indicators` | Pre-registration, blinding, etc. | Study quality assessment |
| `constructs` | IV/DV construct mappings | Construct-level analysis |
| `argument_scheme` | Walton argumentation scheme | Argument structure |
| `critical_questions` | Probing questions for the argument | Dialectical completeness |
| `defeat_relationships` | Known defeaters | Epistemic resilience |
| `contrast_class` | Lipton's "why X rather than Y?" | Explanatory precision |
| `epistemic_level` | OBSERVATIONAL through THEORETICAL | Epistemic hierarchy |

**Quality Thresholds**: Min 1 finding; ≥50% must have stats; ≥90% must have direction; min score 0.6.

### §187.2 META_ANALYSIS — Full Field Schema

**Critical Fields**:

| Field | Description | Example | Why Critical |
|-------|-------------|---------|-------------|
| `antecedent` | Meta-level IV with k | "Nature exposure interventions (k=15)" | What was synthesized |
| `consequent` | Pooled outcome | "Stress reduction (cortisol)" | What was measured across studies |
| `direction` | increase \| decrease \| no_effect \| mixed | "decrease" | Aggregate direction |
| `effect_size` | Pooled effect | 0.52 | The whole point of meta-analysis |
| `effect_size_type` | d, g, r, OR | "Hedges' g" | Comparability |
| `confidence_interval` | [lower, upper] | [0.38, 0.66] | Precision of pooled estimate |
| `p_value` | Pooled significance | "<0.001" | Statistical evidence |
| `claim_type` | pooled_effect \| synthesized | "pooled_effect" | Distinguishes from individual findings |
| `source` | Figure/table reference | "Figure 2: Forest Plot" | Verifiability |
| `quote` | Text stating result | "Pooled effect was g = 0.52..." | Provenance |
| `provenance_depth` | direct_quote \| paraphrase | "direct_quote" | Source fidelity |

**Expected Fields**:

| Field | Description | Why Expected |
|-------|-------------|-------------|
| `moderators_reported` | Subgroup moderators | Key for understanding heterogeneity |
| `theory_links` | Connected theories | Theoretical grounding |
| `mechanism` | Proposed mechanism | Understanding the aggregate |
| `heterogeneity` | I², Q, τ² | How consistent are the studies? |
| `k_studies` | Number of studies | Sample of studies |
| `total_n` | Total participants | Statistical power |
| `publication_bias` | Funnel plot, Egger's test | Validity threat assessment |
| `search_strategy` | Databases, date range | Reproducibility |
| `inclusion_criteria` | What was included/excluded | Scope definition |

**Quality Thresholds**: Min 1 finding; ≥80% must have stats; ≥90% must have direction; min score 0.7.

### §187.3 SYSTEMATIC_REVIEW — Full Field Schema

**Critical Fields**:

| Field | Description | Why Critical |
|-------|-------------|-------------|
| `antecedent` | Synthesized factor | What was reviewed |
| `consequent` | Synthesized outcome | What outcomes were examined |
| `direction` | increase \| decrease \| no_effect \| mixed | Aggregate direction |
| `claim_type` | synthesized | Distinguishes synthesis from primary finding |
| `source` | Section reference | Verifiability |
| `quote` | Synthesis statement | Provenance |

**Expected Fields**: `theory_links`, `mechanism`, `search_strategy`, `inclusion_criteria`, `risk_of_bias_summary`.

**Quality Thresholds**: Min 1 finding; stats not required; ≥70% must have direction; min score 0.5.

### §187.4 NARRATIVE_REVIEW — Full Field Schema

**Critical Fields**:

| Field | Description | Why Critical |
|-------|-------------|-------------|
| `antecedent` | Discussed factor | What the review covers |
| `consequent` | Discussed outcome | What effects are described |
| `direction` | increase \| decrease \| no_effect \| mixed | Direction of claimed relationship |
| `claim_type` | narrative \| cited \| theoretical | Type of evidence claim |
| `quote` | Author's synthesis | Provenance |

**Expected Fields**: `theory_links`, `source`.

**Quality Thresholds**: Min 1 finding; stats not required; ≥50% must have direction; min score 0.4.

### §187.5 THEORETICAL — Full Field Schema

**Critical Fields**:

| Field | Description | Why Critical |
|-------|-------------|-------------|
| `antecedent` | Theoretical construct (cause) | What the theory posits as causal |
| `consequent` | Theoretical construct (effect) | What the theory predicts |
| `direction` | increase \| decrease \| modulates | Predicted direction |
| `claim_type` | theoretical_proposition \| derived_guideline | Type of theoretical claim |
| `mechanism_chain` | 2+ step causal chain | *The* contribution of theoretical papers |
| `quote` | Proposition statement | Provenance |

**Expected Fields**: `theory_links`, `theory_commitments` (tests/extends/contradicts).

**Quality Thresholds**: Min 0 empirical findings; stats not required; ≥30% direction; min score 0.3.

### §187.6 QUALITATIVE — Full Field Schema

**Critical Fields**:

| Field | Description | Why Critical |
|-------|-------------|-------------|
| `antecedent` | Contextual factor or experience | What context was studied |
| `consequent` | Theme or outcome identified | What emerged from analysis |
| `claim_type` | qualitative_theme | Distinguishes from quantitative findings |
| `quote` | Participant quote or theme description | The primary evidence |
| `provenance_depth` | direct_quote \| paraphrase | How close to participants' words |

**Expected Fields**: `theory_links`, `source`.

**Quality Thresholds**: Min 1 finding; stats not required; direction not strictly required; min score 0.4 (adjusted from table which shows no qualitative row — this is interpolated).

### §187.7 INSTRUMENT_VALIDATION — Full Field Schema

**Critical Fields**:

| Field | Description | Why Critical |
|-------|-------------|-------------|
| `instruments_used` | Full instrument details | *The* contribution |
| `source` | Validation results location | Verifiability |
| `quote` | Reliability/validity statement | Provenance |

Each entry in `instruments_used` must include:

| Sub-field | Description | Example |
|-----------|-------------|---------|
| `name` | Full instrument name | "State-Trait Anxiety Inventory" |
| `abbreviation` | Standard abbreviation | "STAI" |
| `construct_measured` | What it measures | "state anxiety" |
| `n_items` | Number of items | 20 |
| `reliability.cronbach_alpha` | Internal consistency | 0.89 |
| `reliability.test_retest` | Temporal stability | 0.91 |

**Expected Fields**: `antecedent`, `consequent`, `effect_size`, `p_value` (for validity evidence).

---

## §188. Classification Signals: Decision Tree

The following decision tree formalizes the classification logic. It should be used by any model performing classification, and can serve as a verification checklist for human reviewers.

```
START
  │
  ├─ Does the paper report POOLED EFFECT SIZES across k studies?
  │   └─ YES → META_ANALYSIS
  │
  ├─ Does the paper follow PRISMA protocol with systematic search?
  │   └─ YES → SYSTEMATIC_REVIEW
  │
  ├─ Does the paper present ORIGINAL QUANTITATIVE DATA?
  │   ├─ YES → Does it MANIPULATE conditions (random assignment)?
  │   │   ├─ YES → EMPIRICAL_RESEARCH
  │   │   └─ NO → OBSERVATIONAL
  │   │
  │   ├─ Does it combine quantitative AND qualitative methods?
  │   │   └─ YES → MIXED_METHODS
  │   │
  │   ├─ Is the primary purpose INSTRUMENT VALIDATION?
  │   │   └─ YES → INSTRUMENT_VALIDATION
  │   │
  │   └─ Does it follow participants OVER TIME (multiple waves)?
  │       └─ YES → LONGITUDINAL
  │
  ├─ Does the paper use QUALITATIVE methods as primary?
  │   └─ YES → QUALITATIVE
  │
  ├─ Does the paper propose a NEW FRAMEWORK or MODEL?
  │   └─ YES → THEORETICAL (or CONCEPTUAL_FRAMEWORK)
  │
  ├─ Does the paper review literature WITHOUT systematic method?
  │   └─ YES → NARRATIVE_REVIEW
  │
  ├─ Is it an OPINION piece, EDITORIAL, or RESPONSE?
  │   └─ YES → COMMENTARY
  │
  ├─ Is it a CASE STUDY, TECHNICAL REPORT, or PROJECT DESCRIPTION?
  │   └─ YES → REPORT
  │
  ├─ Does it describe an INTERVENTION PROTOCOL (design focus)?
  │   └─ YES → INTERVENTION_DESIGN
  │
  └─ Does it COMPARE across populations/contexts as primary goal?
      └─ YES → COMPARATIVE_ANALYSIS
```

### §188.1 Ambiguous Cases and Resolution Rules

Several common ambiguities arise in our corpus (environmental psychology, neuroarchitecture, building science):

1. **Survey study with no manipulation**: Many papers administer questionnaires in existing buildings. There is no random assignment. These are **OBSERVATIONAL**, not EMPIRICAL_RESEARCH. The distinction matters because OBSERVATIONAL studies cannot support causal claims at the EXPERIMENTAL tier.

2. **Systematic review WITH meta-analysis**: Classify as **META_ANALYSIS** (the more informative type). The systematic review methodology is documented within the meta-analysis extraction.

3. **Theoretical paper with illustrative examples**: If the examples include original data → **MIXED_METHODS** or **EMPIRICAL_RESEARCH**. If examples are from published literature → **THEORETICAL**.

4. **Paper validates an instrument AND tests hypotheses with it**: If the primary contribution is the instrument → **INSTRUMENT_VALIDATION**. If the instrument is a tool used to test a substantive hypothesis → **EMPIRICAL_RESEARCH**.

5. **Longitudinal empirical study**: If the temporal dimension is the primary contribution → **LONGITUDINAL**. If the study happens to be longitudinal but the focus is on a specific intervention → **EMPIRICAL_RESEARCH** with a note about longitudinal design.

---

## §189. Gaps and Recommended Improvements

### §189.1 Missing Dedicated Templates

The following article types currently default to generic prompts but would benefit from dedicated extraction templates:

| Type | Current Default | What's Missing |
|------|----------------|---------------|
| LONGITUDINAL | Empirical | Time-point structure, attrition data, trajectory models |
| OBSERVATIONAL | Empirical | Distinction between measured vs. manipulated variables |
| MIXED_METHODS | Empirical | Qualitative theme extraction alongside quantitative |
| INTERVENTION_DESIGN | Empirical | Protocol components, dosage, implementation fidelity |
| COMPARATIVE_ANALYSIS | Empirical | Cross-population comparison structure |

### §189.2 Pre-Classification Recommendation

Given the cascading consequences of misclassification, the recommended architecture is:

1. **Phase 1: Pre-classify with high-accuracy model** (Claude Opus or human review)
   - Run classification on all 1,068 papers
   - Store classifications in a lookup table
   - Human-verify any classification with confidence < 0.85

2. **Phase 2: Extract with cost-optimized model** (Gemini Flash or equivalent)
   - Pass the pre-classified type to the extraction model
   - The extraction model does NOT re-classify; it trusts the classification
   - This prevents the extraction model from overriding a better classifier's judgment

3. **Phase 3: Verify with independent model** (Claude Haiku or Opus)
   - Stage 3 verification checks whether the extraction is consistent with the classification
   - If the verifier disagrees with the classification, flag for human review

### §189.3 The Seven-Panel Problem

David's original seven-panel system was designed to make papers navigable at a glance. The extraction schema must support generating those panels. The current field schema covers the content, but the mapping from extracted fields to panels should be made explicit:

| Panel | Source Fields |
|-------|-------------|
| 1. What's the paper about? | `title`, `article_type`, `antecedent` (across findings), `consequent` (across findings) |
| 2. What did they find? | `findings[].statement`, `findings[].direction`, `findings[].effect_size` |
| 3. How strong is the evidence? | `findings[].p_value`, `findings[].effect_size`, `findings[].sample_size`, `causal_tier` |
| 4. What methods? | `instruments_used`, `measure_type`, `scope_conditions`, `stimulus_description` |
| 5. What theories? | `theory_links`, `theory_commitments`, `mechanism_chain` |
| 6. What are the limits? | `limitations`, `scope_conditions.scope_unknown_dimensions`, `defeat_relationships` |
| 7. What's next? | `moderators_reported`, future research suggestions (not currently extracted as a field) |

**Note**: Panel 7 ("What's next?") lacks a dedicated extraction field. Adding a `future_directions` field to the schema would complete the seven-panel mapping.

---

## §190. Appendix: Complete Field Enumeration

For reference, the complete set of fields in `extraction_template.v2.schema.json` is enumerated below, grouped by function.

### Article-Level Fields (19)
`doi`, `title`, `authors`, `publication_year`, `journal`, `volume`, `issue`, `article_type`, `article_family`, `detected_article_type`, `detected_family`, `quality_action`, `quality_score`, `n_findings`, `extracted_at`, `model`, `cost` (object with `input_tokens`, `output_tokens`, `usd`), `domains`, `limitations`

### Finding-Level Fields (52)
**Identity**: `id`
**Core Claim**: `antecedent`, `consequent`, `direction`, `claim_type`, `statement`
**Statistics**: `p_value`, `effect_size`, `effect_size_type`, `test_statistic`, `confidence_interval`
**Sample**: `sample_size`, `sample_size_source`, `sample` (object: `n`, `population`, `age_mean`, `country`)
**Design**: `measure_type`, `causal_tier`, `epistemic_level`
**Provenance**: `source`, `quote`, `source_zone`, `provenance_depth`
**Constructs**: `constructs` (object: `environment_factors`, `outcomes`, `mediators`, `moderators`)
**Mechanism**: `mechanism`, `mechanism_chain` (array of steps)
**Theory**: `theory_links` (array), `theory_commitments` (array), `argument_scheme`, `critical_questions`
**Moderation**: `moderators_reported`
**Instruments**: `instruments_used` (array with `name`, `abbreviation`, `construct_measured`, `n_items`, `reliability`)
**Scope**: `scope_conditions` (object: `setting`, `population`, `climate`, `duration`, `measurement_type`, `scope_unknown_dimensions`)
**Stimulus**: `stimulus_description` (object: `primary_type`, `delivery_method`, `duration_seconds`, `components`), `stimulus_images`
**Epistemic**: `contrast_class`, `difference_maker`, `defeat_relationships` (array), `defeater_search_status`, `justification_status`
**Quality**: `ae_confidence`, `extraction_difficulty`, `source_quality_indicators` (object: `pre_registered`, `blinding`, `independence_flag`, `replication_status`, `study_type_for_commitment_penalty`)
**Conflict**: `conflict_type`

**Total unique fields per finding**: 52 (counting sub-objects as single fields) or ~85 (counting all leaf values)

---

*This document should be reviewed whenever the extraction schema is modified, and updated to reflect any new article types, field additions, or quality threshold changes.*
