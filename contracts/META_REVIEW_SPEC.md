# Meta-Review Specification for ATLAS

**Status**: ACTIVE — Required before LLM generation for 3,788+ belief clusters
**Last Updated**: 2026-03-04
**Authority**: Formal specification governing all meta-review generation, validation, persistence, and rendering

**Companion documents**: See `QA_ANSWER_NORMS.md` for answer rendering; `SCIENCE_COMMUNICATION_NORMS.md` for prose style; `docs/EPISTEMIC_PRINCIPLES.md` for epistemic commitments; `VISUALIZATION_NORMS.md` for figure rendering.

---

## 1. Purpose and Definition

### 1.1 What Is a Meta-Review in ATLAS?

A **meta-review is not a meta-analysis**. It is a structured synthesis document that transforms an ATLAS belief cluster (a group of empirical findings about environmental effects on psychology) into a form suitable for multiple end uses: QA answer enrichment, card system display, researcher discovery, and design guidance.

Specifically, a meta-review is a *validated intellectual product* that:

1. **Synthesizes evidence** into a single directional belief statement with confidence calibration
2. **Explains mechanisms** — the causal pathways that make the effect plausible
3. **Identifies latent variables** that explain variance in the findings
4. **Prioritizes research gaps** using value-of-information reasoning
5. **Quantifies heterogeneity** — why studies disagree and by how much
6. **Specifies scope conditions** — when, where, and for whom the cluster applies
7. **Documents replication** — how many independent research teams have tested this effect

Unlike a traditional meta-analysis, which produces a single summary statistic (e.g., Cohen's d with CI), a meta-review produces a multidimensional profile of what the cluster knows and doesn't know, calibrated for multiple audiences.

### 1.2 Where Meta-Reviews Live in the System

**Creation**: Generated post-clustering by `cluster_meta_review.py`, using either:
  - **Opus** (high-stakes clusters: core architectural effects, high evidence, high usage)
  - **Gemini** (bulk processing: lower-stakes clusters, evidence validation only)

**Persistence**: Stored in `data/annotations/meta_reviews/{cluster_id}.json`

**Consumption**:
  - **QA System**: Enrichment orchestrator uses belief_statement + mechanisms + research_needs
  - **Card System**: Overview tab displays belief_statement + confidence + effect_size_summary
  - **Gap Predictor**: research_needs feed into value-of-information calculation
  - **System Health**: AESHI scoring uses meta-review quality as a signal of knowledge trustworthiness

**Rendering**: Translated into prose via `answer_renderer.py` based on audience (researcher, designer, policymaker, student)

---

## 2. Data Model

### 2.1 Core Fields — Complete Specification

#### 2.1.1 Identification

**Field**: `cluster_id` (string, required)
- **Definition**: Unique identifier for this belief cluster (e.g., `"daylight_exposure→stress_reduction"`)
- **Format**: `{antecedent_simplified}→{consequent_simplified}` where simplified means: lowercase, underscores, no special characters
- **Example**: `"natural_materials→thermal_comfort_perception"`
- **Quality criterion**: Must be deterministic and parseable as `{antecedent} → {consequent}`

**Field**: `antecedent_theme` (string, required)
- **Definition**: The environmental/architectural variable being studied (what's being manipulated or observed)
- **Examples**: "daylight exposure", "window views of nature", "open office layout", "material warmth"
- **Quality criterion**: Must be a concrete environmental property, not a psychological state

**Field**: `consequent_theme` (string, required)
- **Definition**: The psychological outcome being measured (what changes as a result)
- **Examples**: "stress reduction", "attention restoration", "creativity", "wayfinding performance"
- **Quality criterion**: Must be a measurable psychological construct, not vague ("wellbeing" ❌ → "self-reported wellbeing on 1-10 scale" ✅)

#### 2.1.2 The Belief Statement (Most Critical Field)

**Field**: `belief_statement` (string, required, >150 characters, <500 characters)
- **Definition**: A single-sentence empirical claim that synthesizes the cluster's evidence base
- **Required elements**:
  1. Directional claim (increase/decrease/null/mixed)
  2. Specific magnitude or range (effect size with CI, or explicit "magnitude unclear")
  3. Population/scope specificity (not "people" — "office workers", "children in school buildings")
  4. Evidence citation count (number of studies backing this)
  5. Sample size or number of subjects when available

**Format template**:
```
[Antecedent] ([specifics about dosage/intensity]) [direction of effect] [consequent] in [population]
([N] studies, N_total=[total subjects], [effect size metric]=[point estimate], CI=[range]).
```

**Good examples**:
- ✅ "Daylight exposure (≥2,500 lux, ≥30 min daily) reduces self-reported stress in office workers (7 studies, N_total=412, d̄=0.38, CI=[0.21, 0.55])."
- ✅ "Biophilic design (elements including plants, water, wood textures) is associated with improved attention restoration in students aged 18–25 (4 studies, N_total=156, Cohen's d range 0.42–0.68). Effect magnitude is modest but consistent across design types."
- ✅ "Open office layouts without acoustic buffers increase psychological stress markers in adults with high sensory sensitivity (3 studies, N_total=89). Effect size varies (d range 0.31–0.87), heterogeneity driven by buffer material and noise level."

**Bad examples**:
- ❌ "Light affects mood." (No specificity, no evidence count, no magnitude)
- ❌ "Natural materials improve wellbeing in people." (Vague population, unmeasured outcome, no effect size)
- ❌ "Daylight exposure improves psychological outcomes based on several studies." (No direction specificity, no evidence count, "several" is not quantified)
- ❌ "Biophilic design has been shown to enhance cognitive and emotional wellbeing in various settings." (Generic hedging, no scope, no effect size, no evidence count)

**Quality criterion**: A non-expert should be able to understand the claim, its scope, and its strength in <30 seconds of reading.

#### 2.1.3 Confidence Assessment

**Field**: `confidence_level` (enum, required)
- **Values**: `HIGH` | `MOD_HIGH` | `MODERATE` | `LOW`
- **Definition**: Probability that the belief statement accurately represents the true effect direction and approximate magnitude

**Confidence Level Criteria**:

| Level | Credence Range | Criteria | Examples |
|-------|---|---|---|
| **HIGH** | 0.80–0.95 | ≥10 studies; consistent direction (≥90%); medium+ effect; low heterogeneity; ≥3 independent research teams; replicated in ≥2 settings | Daylight→stress (7 studies, 86% agreement, d=0.38); Natural materials→thermal comfort (6 studies, 83% agreement) |
| **MOD_HIGH** | 0.65–0.80 | 5–9 studies; direction consensus (75–89%); small-to-medium effect; moderate heterogeneity; ≥2 independent teams; limited replication | Window views→attention (5 studies, 80% agreement, d=0.28); Open offices→stress (4 studies, 75% agreement) |
| **MODERATE** | 0.50–0.65 | 3–4 studies OR low consistency (60–74% direction agreement) OR small effect OR single research team OR limited generalization | Specific acoustic design→learning (3 studies, 67% agreement, d=0.19); Certain color palettes→mood (2 studies, inconsistent measures) |
| **LOW** | 0.30–0.50 | ≤2 studies OR highly heterogeneous (conflicting directions) OR unmeasured confounds OR single small study OR theoretical plausibility only | Specific water feature design→recovery (1 study, N=25); Proposed mechanism without direct evidence |

**Field**: `confidence_label` (string, required)
- **Definition**: Human-readable label for confidence with Bayesian credence estimate
- **Format**: `"{Level} (ω = {credence_point_estimate})"`
- **Examples**:
  - `"HIGH (ω = 0.88)"`
  - `"MOD_HIGH (ω = 0.72)"`
  - `"MODERATE (ω = 0.58)"`
  - `"LOW (ω = 0.41)"`

**Field**: `confidence_color` (string, required)
- **Definition**: WCAG 2.1 AA compliant color for thermometer visualization
- **Values**: `"#d4edda"` (HIGH, light green) | `"#fff3cd"` (MOD_HIGH, light amber) | `"#ffeeba"` (MODERATE, light gold) | `"#f8d7da"` (LOW, light red/pink)
- **Accessibility requirement**: Never use dark blue on dark background; all colors must pass 4.5:1 contrast ratio test

**Quality criterion**: Confidence assignment must be defensible by the evidence profile. Defaulting all clusters to MODERATE is a red flag.

#### 2.1.4 Evidence Summary

**Field**: `n_findings` (integer, required, ≥1)
- **Definition**: Total count of empirical findings extracted from the cluster's papers
- **Example**: A paper with 3 experiments on the same topic = 3 findings

**Field**: `n_papers` (integer, required, ≥1)
- **Definition**: Unique papers in the cluster's evidence base
- **Relationship**: `n_papers ≤ n_findings` (one paper may contain multiple findings)

**Field**: `direction_consensus` (enum, required)
- **Values**: `"increase"` | `"decrease"` | `"mixed"` | `"no_effect"`
- **Definition**: Majority direction of findings
  - `"increase"`: ≥60% of findings show increased consequent
  - `"decrease"`: ≥60% of findings show decreased consequent
  - `"mixed"`: 40–60% split between increase/decrease
  - `"no_effect"`: ≥60% of findings show null effect

**Field**: `direction_detail` (string, required)
- **Definition**: Percentage breakdown of finding directions
- **Format**: `"{percent_1} {direction_1}, {percent_2} {direction_2}, {percent_3} {direction_3}"`
- **Examples**:
  - `"73% increase, 15% mixed, 12% decrease"`
  - `"82% decrease, 18% no effect"`
  - `"45% increase, 55% decrease"` (triggers mixed classification)

**Field**: `heterogeneity` (enum, required)
- **Values**: `"low"` | `"moderate"` | `"high"`
- **Definition**: Variability in effect size across studies, assessed via I² statistic if available, otherwise visual inspection
  - `"low"`: I² < 25% or effect sizes within 0.2 point range
  - `"moderate"`: I² 25–75% or effect sizes span 0.2–0.5 points
  - `"high"`: I² > 75% or effect sizes span >0.5 points

**Field**: `article_types` (dictionary, required)
- **Definition**: Count of evidence sources by study type
- **Format**: `{"empirical_v2": N, "systematic_review": N, "meta_analysis": N, "qualitative": N, "theoretical": N}`
- **Example**: `{"empirical_v2": 12, "systematic_review": 2, "meta_analysis": 1, "qualitative": 0, "theoretical": 0}`
- **Quality criterion**: Presence of peer-reviewed empirical evidence is mandatory; systematic reviews boost confidence

**Field**: `theory_links` (list of strings, required)
- **Definition**: Theories that explain why this cluster's effect exists
- **Examples**:
  - `["Attention Restoration Theory (Kaplan & Kaplan)", "Stress Reduction Theory (Ulrich)"]`
  - `["Cognitive Load Theory (Sweller)", "Embodied Cognition (Lakoff & Johnson)"]`
- **Quality criterion**: Must cite specific theories with authors; "neural mechanisms" ❌, "affective integration via the amygdala (LeDoux, 1996)" ✅

#### 2.1.5 Mechanism Analysis

**Field**: `mechanisms` (list of MechanismCandidate objects, required, 1–5 items)
- **Definition**: Causal pathways that explain the cluster's effect
- **When to include**: Only mechanisms with ≥2 studies implicating them or strong theoretical support
- **When to exclude**: Speculative mechanisms without evidence

**MechanismCandidate subfields**:

| Subfield | Type | Definition | Requirements |
|----------|------|-----------|---|
| `pathway` | string | The causal chain (e.g., "daylight → circadian rhythm → mood regulation") | Must be multi-step; single-hop mechanisms are trivial |
| `theory_support` | string | Which theory predicts this mechanism | Must cite theory + author(s) |
| `evidence_count` | int | How many findings in the cluster implicate this mechanism | ≥1; ≥2 strongly preferred |
| `confidence` | enum | "high" \| "moderate" \| "speculative" | High = multiple studies measure the mechanism; Moderate = some indirect evidence; Speculative = theory only |

**Good examples**:
- ✅ `{pathway: "natural light → melatonin suppression → cortisol reduction", theory_support: "Circadian Rhythm Theory (Czeisler & Gooley, 2007)", evidence_count: 3, confidence: "high"}`
- ✅ `{pathway: "biophilic design → attention restoration → cognitive resource availability", theory_support: "ART (Kaplan & Kaplan, 1989); Cognitive Resource Theory", evidence_count: 2, confidence: "moderate"}`

**Bad examples**:
- ❌ `{pathway: "natural materials affect mood", ...}` (No mechanism specificity; "mood" is the outcome, not part of the pathway)
- ❌ `{pathway: "daylight through neural processes", ...}` (Vague; "neural processes" is not a mechanism)
- ❌ `{pathway: "views of nature → happiness", ...}` (Trivial one-hop; doesn't explain *how*)

**Quality criterion**: Each mechanism must explain WHY the antecedent causes the consequent, not just restate it.

#### 2.1.6 Latent Variables

**Field**: `latent_variables` (list of LatentVariable objects, optional, 0–4 items)
- **Definition**: Unmeasured constructs that likely explain variance across findings
- **When to include**: When heterogeneity is high (I² > 50%) or multiple study types disagree
- **When to exclude**: When heterogeneity is low and all studies are methodologically similar

**LatentVariable subfields**:

| Subfield | Type | Definition | Requirements |
|----------|------|-----------|---|
| `name` | string | The construct (e.g., "individual stress sensitivity") | Specific enough to measure; not "personality" → "neuroticism" or "stress sensitivity" |
| `rationale` | string | Why this construct explains variance | Must connect to observed pattern in the data |
| `type` | enum | "mediator" \| "moderator" \| "confounder" | **Mediator**: affects the pathway; **Moderator**: changes when effect applies; **Confounder**: causes both antecedent and consequent |
| `testable` | boolean | Can this be operationalized? | true only if measurement is feasible |
| `suggested_measure` | string | How to operationalize it | Cite an existing scale or specify construction (e.g., "Perceived Stress Scale (Cohen et al., 1983)") |

**Good examples**:
- ✅ Moderator: `{name: "individual sensory sensitivity", rationale: "Studies with high-sensitivity populations show 2x larger effects; studies controlling for sensitivity show reduced heterogeneity", type: "moderator", testable: true, suggested_measure: "Highly Sensitive Person Scale (Aron & Aron, 1997)"}`
- ✅ Mediator: `{name: "perceived naturalness of materials", rationale: "Natural material studies show larger effects on thermal comfort perception; effect size correlates with participant-rated naturalness (r=0.62)", type: "mediator", testable: true, suggested_measure: "5-item naturalness rating scale (Sakuragawa et al., 2005)"}`

**Bad examples**:
- ❌ `{name: "individual differences", ...}` (Too vague; not operationalizable)
- ❌ `{name: "methodological quality", type: "moderator", ...}` (Not a latent variable; this is study design)
- ❌ `{name: "stress sensitivity", testable: false, ...}` (Contradiction: exists in literature but marked untestable)

**Quality criterion**: Every latent variable must explain an observed pattern in the data, not be speculative.

#### 2.1.7 Research Needs

**Field**: `research_needs` (list of ResearchNeed objects, required, 1–5 items)
- **Definition**: VOI-ranked research questions to advance the belief's credence and scope
- **Ranking principle**: Ordered by value of information (VOI), not alphabetically or by recency
- **Count**: Must have ≥1; ≥3 strongly preferred for clusters with moderate+ heterogeneity

**ResearchNeed subfields**:

| Subfield | Type | Definition | Requirements |
|----------|------|-----------|---|
| `question` | string | The research question (typically closed: "Does X affect Y under condition Z?") | Specific and testable; not "more research needed" |
| `voi_rank` | int | Priority ordering (1 = highest VOI) | 1–5 recommended; higher numbers allowed if >5 gaps exist |
| `rationale` | string | Why answering this question would increase credence or reduce uncertainty | Must reference current gap (e.g., "All current studies use self-report; physiological measures would address demand characteristics") |
| `study_type` | enum | "RCT" \| "longitudinal" \| "meta_analysis" \| "measurement" \| "mechanistic" | Specifies what type of evidence would advance the field |

**VOI Ranking Framework**:
- **Rank 1 (Highest VOI)**: Resolves current contradiction OR reduces high heterogeneity OR extends to under-sampled population OR measures mechanisms
- **Rank 2**: Tests scope boundary OR controls for major confounder OR compares effect across conditions
- **Rank 3**: Validates mechanism OR replicated independent team OR larger sample to tighten CI
- **Rank 4**: Extension or refinement of well-established finding OR alternative theoretical explanation
- **Rank 5**: Methodological improvement (e.g., pre-registration, open science) OR long-term follow-up

**Good examples**:
- ✅ `{question: "Does daylight's stress-reduction effect persist in populations with seasonal affective disorder, or is it attenuated?", voi_rank: 1, rationale: "All current studies N⊂ healthy adults; SAD populations may show different circadian sensitivity. Resolving this would establish scope boundaries.", study_type: "RCT"}`
- ✅ `{question: "What is the minimum dosage of natural view exposure (duration × visual field) to trigger attention restoration?", voi_rank: 2, rationale: "Current studies use varying exposure durations (1–30 min); dose–response relationship unknown. Establishing minimum effective dose would advance design guidance.", study_type: "measurement"}`
- ✅ `{question: "Does the effect of biophilic design on creativity depend on whether participants believe the design is 'natural' vs 'synthetic'?", voi_rank: 2, rationale: "Heterogeneity correlates with material authenticity. Mechanistic test would distinguish perceptual from objective naturalness.", study_type: "mechanistic"}`

**Bad examples**:
- ❌ `{question: "Does this cluster need more research?", ...}` (Not specific; not testable)
- ❌ `{question: "What is the neural basis of the effect?", voi_rank: 1, ...}` (Worthy question but low VOI for ATLAS's design application)
- ❌ `{question: "Do different populations respond differently?", voi_rank: 3, ...}` (Vague; which populations and which responses?)

**Quality criterion**: Each research need must be answerable by a specific study design and must address a real gap in the current corpus.

#### 2.1.8 Heterogeneity Assessment

**Field**: `heterogeneity_assessment` (string, required if heterogeneity ≠ "low", else optional)
- **Definition**: Explanation of *why* findings disagree and *how much*, with quantification where possible
- **Required format**:
  1. Magnitude statement (I², effect size range, or both)
  2. Direction of variability (what drives it)
  3. Subset analysis if available (e.g., "Studies with N > 100 show d=0.42 (95% CI [0.28–0.56]); studies with N ≤ 50 show d=0.21 (95% CI [−0.05–0.47])")

**Good examples**:
- ✅ "Heterogeneity is moderate (I² = 48%). Studies using physiological stress measures (cortisol, heart rate) show consistent decreases (d̄ = 0.51, 95% CI [0.36–0.67], 3 studies), whereas self-report measures show smaller effects (d̄ = 0.28, 95% CI [0.12–0.44], 4 studies). This 0.23-point difference suggests measurement method is a moderator."
- ✅ "High heterogeneity (I² = 71%) driven by population and context. Office workers in high-stress industries (healthcare, finance) show larger effects (d̄ = 0.58) than those in lower-stress industries (d̄ = 0.18). This suggests baseline stress level moderates the effect."

**Bad examples**:
- ❌ "Heterogeneity is moderate because findings vary." (Circular; not explaining why)
- ❌ "High heterogeneity is expected in applied research." (Accepting heterogeneity without investigation)

**Quality criterion**: Heterogeneity assessment must point toward specific moderators or study-design factors, not just acknowledge variability.

#### 2.1.9 Scope Conditions

**Field**: `scope_conditions` (string, required)
- **Definition**: Explicit statement of when, where, for whom, and under what conditions the cluster's effect applies
- **Required elements** (specify each or explicitly state "not studied"):
  1. **Populations**: Age range, cultural context, health status, expertise level
  2. **Settings**: Indoor/outdoor, climatic conditions, building type, noise level
  3. **Durations**: Minimum exposure time, acute vs chronic, circadian phase
  4. **Intensity/dosage**: Relevant parameters (lux for light, decibels for sound, etc.)
  5. **Exclusions**: Who/where the effect does NOT apply

**Good examples**:
- ✅ "Applies to: adults aged 18–65 in healthy adult samples; primarily tested in temperate climates (15–25°C); indoor office environments with standard fluorescent or LED lighting; exposures of 30+ min daily. Does NOT apply to: shift workers (circadian rhythm confound); severe light-sensitive populations; outdoor settings (confounded by temperature, humidity); durations <10 min (insufficient circadian signaling)."
- ✅ "Applies to: children aged 5–12 in school buildings; indoor learning environments; natural view type not specified (window with trees sufficient); tested in North American and European schools. Limited evidence for: pre-school children; non-school indoor settings; Southern Hemisphere schools; severe crowding conditions (N=2 studies)."

**Bad examples**:
- ❌ "Applies to people in various settings." (Not specific)
- ❌ "Generalizable across all human populations." (Overreaching; not evidence-based)

**Quality criterion**: Scope conditions must be specific enough that a practitioner can determine whether the cluster applies to their situation.

#### 2.1.10 Effect Size Summary

**Field**: `effect_size_summary` (string, required)
- **Definition**: Aggregate effect size across the cluster, with confidence interval, OR explicit statement if meta-analysis is not possible
- **Format options**:
  1. **Pooled estimate** (if homogeneous): `"d̄ = 0.38 (95% CI [0.21, 0.55]), N_total = 412, 7 studies, I² = 24%"`
  2. **Range + median** (if heterogeneous): `"d range 0.19–0.62 (Mdn = 0.42), N_total = 287, 5 studies, I² = 62%"`
  3. **Not available**: `"Meta-analytic pooling not possible: studies use incompatible outcome measures (self-report vs cortisol vs reaction time). See heterogeneity_assessment for subset analyses."`

**Quality criterion**: Never report only a median without context (e.g., "Median effect = small"); always include N_total, study count, and I² where available.

#### 2.1.11 Replication Status

**Field**: `replication_status` (string, required)
- **Definition**: Count of independent research teams that have tested the effect AND have they replicated (direction consistency)?
- **Format**: `"{N} independent research teams; {N_replicated} replicated direction ({percentage}%)"`
- **Examples**:
  - `"4 independent research teams; 3 replicated direction (75%)"`
  - `"2 independent research teams; 2 replicated direction (100%)"`
  - `"1 research team; no independent replication available"`

**Quality criterion**: Clusters with only 1 research team should have LOW confidence unless the sample size is very large (N > 500).

#### 2.1.12 Cross-Cluster Connections

**Field**: `related_clusters` (list of cluster_id strings, optional, 0–4 items)
- **Definition**: Other clusters that share antecedents, consequents, or theoretical mechanisms
- **Examples**: If this cluster is `daylight_exposure→stress_reduction`, related might include:
  - `daylight_exposure→attention_restoration`
  - `circadian_rhythm→mood_regulation`
  - `natural_light→sleep_quality`

**Field**: `contradicting_clusters` (list of cluster_id strings, optional, 0–3 items)
- **Definition**: Clusters where the effect direction is opposite or contradicts this one
- **Example**: If this cluster is `open_office_layout→collaboration_improvement`, contradicting might be:
  - `open_office_layout→distraction_increase`
  - `spatial_proximity→privacy_violation`

### 2.2 Metadata Fields

**Field**: `generated_at` (ISO 8601 timestamp, required)
- **Format**: `"2026-03-04T14:32:17Z"`
- **Definition**: When the meta-review was generated

**Field**: `generation_time_ms` (float, required)
- **Definition**: Wall-clock time to generate this meta-review (seconds)
- **Usage**: Signals cost; LLM > 2s suggests Opus, < 2s suggests Gemini

---

## 3. Quality Criteria for Acceptability

A meta-review is acceptable for persistence and use if and only if it passes ALL the following criteria:

### SC-MR-1: Non-Trivial Belief Statement
- **Criterion**: `belief_statement` contains ≥1 of: effect size estimate, confidence interval, sample size, evidence count
- **Test**: Parse belief_statement; if it contains only directional claim (e.g., "Light affects mood"), REJECT
- **Rationale**: Vague claims are useless in QA; they don't inform decision-making

### SC-MR-2: Evidence-Grounded Mechanisms
- **Criterion**: Every mechanism in the `mechanisms` list has `evidence_count ≥ 1` OR explicitly notes "theoretical support only with no direct evidence"
- **Test**: For each mechanism, verify that evidence_count > 0 or confidence == "speculative" with explicit caveat
- **Rationale**: Mechanisms without evidence are indistinguishable from confabulation (what the LLM hallucinates)

### SC-MR-3: Justified Confidence Level
- **Criterion**: `confidence_level` assignment matches the evidence profile (n_papers, direction_consensus, heterogeneity, replication_status)
- **Test**: Check that confidence assignment follows the table in Section 2.1.3. If confidence_level == MODERATE and n_papers == 1, REJECT (too many papers for MODERATE)
- **Rationale**: Unjustified confidence is a credibility killer

### SC-MR-4: Specificity in Research Needs
- **Criterion**: Each item in `research_needs` list is testable (could be operationalized as an actual study design)
- **Test**: For each research need, ask: "Could this be a PhD dissertation or grant proposal?" If not, REJECT
- **Rationale**: Generic "more research needed" adds no value

### SC-MR-5: Quantified Heterogeneity
- **Criterion**: If `heterogeneity == "high"`, the `heterogeneity_assessment` field must include a quantitative breakdown (I², subset effect sizes, or ranges)
- **Test**: Search heterogeneity_assessment for numbers (percentages, effect size estimates). If none found and heterogeneity is high, REJECT
- **Rationale**: Unquantified heterogeneity is an admission of unclear analysis

### SC-MR-6: Explicit Scope Conditions
- **Criterion**: `scope_conditions` must explicitly specify (or state "not studied" for):
  - Population type + age range (minimum)
  - Setting type (minimum)
  - At least one of: duration, intensity, dosage
- **Test**: Check that scope_conditions contains no more than 3 instances of "unclear", "not specified", or "varies"
- **Rationale**: Unscoped claims generalize inappropriately

### SC-MR-7: Effect Size with Uncertainty
- **Criterion**: `effect_size_summary` includes either a confidence interval OR explicit "not available" with reason
- **Test**: Parse effect_size_summary. If it reports a point estimate (e.g., "d = 0.38") without a CI or explicit "not available", REJECT
- **Rationale**: Point estimates without uncertainty are misleading

### SC-MR-8: Theory Links Cited
- **Criterion**: `theory_links` list contains ≥1 theory, each with author(s) and year
- **Test**: For each theory in list, verify format like "Theory Name (Author, Year)". If missing author or year, REJECT
- **Rationale**: Uncited theories are unverifiable

### SC-MR-9: No Unsourced Causal Claims
- **Criterion**: Every mechanism, latent variable, and research need that claims an effect must trace back to ≥1 finding_id in the cluster's evidence base OR be explicitly marked "theoretical extrapolation"
- **Test**: Not automatically testable without access to finding_ids; manual review
- **Rationale**: Prevents hallucination where LLM invents causal chains

### SC-MR-10: Consistency Across Fields
- **Criterion**: Confidence_level, effect_size_summary, n_papers, and direction_consensus are internally consistent
- **Test**: If confidence_level == HIGH and effect_size_summary reports "d range 0.18–0.91" (high heterogeneity), inconsistent — REJECT
- **Rationale**: Catches cases where LLM agrees with one field but contradicts another

---

## 4. Success Conditions for Meta-Review System Health

### SC-CMR-1: Cluster Completeness
- **Metric**: `len(meta_reviews) / len(belief_clusters) ≥ 0.95`
- **Threshold**: ≥95% of clusters have a meta-review
- **Rationale**: Below 95%, system QA capacity is significantly impaired

### SC-CMR-2: Quality Gate Pass Rate
- **Metric**: `count(meta_reviews passing all quality criteria SC-MR-1 through SC-MR-10) / len(meta_reviews) ≥ 0.92`
- **Threshold**: ≥92%
- **Rationale**: <92% suggests LLM generation is producing substandard output; trigger manual review

### SC-CMR-3: High-Confidence Cluster Coverage
- **Metric**: `count(confidence_level == HIGH or MOD_HIGH) / count(n_papers ≥ 5) ≥ 0.85`
- **Threshold**: ≥85%
- **Rationale**: Well-evidenced clusters should be assigned high confidence; failure here suggests miscalibration

### SC-CMR-4: Heterogeneity Visibility
- **Metric**: `count(heterogeneity_assessment non-empty AND contains numbers) / count(heterogeneity IN [moderate, high]) ≥ 0.88`
- **Threshold**: ≥88%
- **Rationale**: Unexplained heterogeneity is scientific negligence

### SC-CMR-5: No Divergence in QA Renderings
- **Metric**: For 50 randomly sampled clusters, render meta-review into QA answer prose and compare to human-written exemplar on content accuracy (spot check by David)
- **Threshold**: ≥90% of renderings are faithful to meta-review source material
- **Rationale**: LLM rendering may misrepresent nuanced meta-review; catches divergence early

---

## 5. Audience Calibration and Rendering

Meta-reviews are rendered differently depending on audience type. The same underlying meta-review is transformed via `answer_renderer.py` into four distinct prose styles:

### 5.1 Researcher Audience

**Rendering rules**:
- Lead with: confidence_level + effect_size_summary with full CI
- Cite: all theory_links with author(s) and year
- Include: heterogeneity_assessment in full detail with I² and subset analyses
- Emphasize: replication_status and independent research teams
- Show: directional consensus percentage

**Example output**:
> Daylight exposure (≥2,500 lux, ≥30 min) reduces self-reported stress in office workers (7 studies, N_total=412). Pooled effect: d̄ = 0.38 (95% CI [0.21, 0.55]), I² = 24% (low heterogeneity). Four independent research teams have tested this effect; three replicated the direction (75%). The mechanisms are supported by Circadian Rhythm Theory (Czeisler & Gooley, 2007) and Stress Reduction Theory (Ulrich, 1979). Physiological stress measures (cortisol, heart rate) show consistent effects (d̄ = 0.51); self-report shows smaller effects (d̄ = 0.28), suggesting measurement method is a moderator.

### 5.2 Designer Audience

**Rendering rules**:
- Lead with: practical significance (not statistical significance)
- Cite: minimum dosage/intensity parameters from scope_conditions
- Emphasize: effect_size_summary in terms of "small/moderate/large" by Sawyer (2004) benchmark
- Include: 1–2 mechanisms that explain WHY to architects without jargon
- Show: scope_conditions prominently (who, where, under what conditions)

**Example output**:
> Natural daylight reduces stress in office workers — a moderate effect (30-minute exposures of 2,500+ lux reduce self-reported stress by about one-third of a standard deviation). The effect works because daylight exposure suppresses melatonin and aligns circadian rhythms, improving mood regulation. This applies specifically to adults in office settings; effect is strongest in high-stress industries (healthcare, finance). Minimum dosage: 30 minutes daily at 2,500+ lux. Effect is similar across window views (direct light) and supplemental skylights.

### 5.3 Policymaker Audience

**Rendering rules**:
- Lead with: headline finding + confidence_level in plain language
- Cite: population applicability + minimum dosage
- Include: 1 mechanism (the most important for policy decision)
- Show: practical trade-offs (e.g., if you implement this, expect X benefit + Y cost)
- Omit: heterogeneity, I², confidence intervals (beyond plain-English summary)

**Example output**:
> Daylight exposure significantly reduces stress in office workers — moderately confident in this finding. Policy implication: buildings with high-quality daylighting or skylights (minimum 2,500 lux, 30+ min daily) should see measurable reductions in employee stress leave and healthcare costs. Applies broadly to office workers in temperate climates. Primary mechanism: circadian rhythm regulation. Cost-benefit: daylighting retrofits have 3–5 year payback in reduced absenteeism alone.

### 5.4 Student Audience

**Rendering rules**:
- Lead with: mechanism first (explanation of WHY)
- Build up to: evidence (here's what studies show)
- Cite: 1–2 key studies by name (Ulrich on stress recovery, Kaplan on attention)
- Show: research_needs as "open questions scientists are still investigating"
- Include: 1 related_cluster as "connect this to..."

**Example output**:
> Here's how daylight affects stress: When you see natural light, your body's circadian clock (the internal timer that controls sleep, mood, and stress hormones) recognizes it's daytime. This tells your brain to suppress melatonin (the sleepy chemical) and increase serotonin (a mood-regulator). The result: less cortisol (your body's stress hormone) and better mood. Multiple studies show this works — about 7 careful studies of office workers find that 30+ minutes of daylight per day reduces self-reported stress by about one-third. Some scientists think this also improves attention (called attention restoration), which is a separate but related benefit you might find in another cluster here.

---

## 6. Integration Points

### 6.1 QA System (Enrichment Orchestrator)

**Consumption point**: `retrieve_meta_review_by_cluster(cluster_id)` in Step 4 of enrichment pipeline

**Fields used**:
- `belief_statement` → populates `evidence_summary` output
- `mechanisms` → enriches `explanatory_coherence` calculation
- `confidence_level` + `confidence_label` → sets `credence_ci` base estimate
- `research_needs` → generates `follow_ups` section
- `theory_links` → informs `framework_voices` output

**Integration rule**: If meta-review is missing or confidence_level == LOW, QA system must add disclaimer: "This cluster has limited evidence; consider consulting domain experts."

### 6.2 Card System (Annotation Storage)

**Consumption point**: Card system reads meta-review at card render time (not at generation time)

**Fields used**:
- `belief_statement` → Overview tab headline
- `confidence_label` → Confidence thermometer widget
- `effect_size_summary` → Effect Size subsection
- `mechanisms` (first 2 only) → How It Works subsection
- `scope_conditions` → When Does This Apply subsection
- `research_needs` (first 2 only) → Open Questions subsection

**Rendering rule**: If belief_statement > 300 characters, truncate to first 250 + "..." for card display.

### 6.3 AESHI Scoring (System Health)

**Consumption point**: `aeshi_service.py` queries meta-review quality as component of overall system health

**Metric**:
- `health_score_meta_reviews = count(meta_reviews passing SC-MR-1 through SC-MR-10) / total_meta_reviews`
- Input to overall AESHI score with weight 0.15

### 6.4 Gap Predictor (Research Priority Ranking)

**Consumption point**: Gap predictor uses research_needs across clusters to identify high-impact research directions

**Usage**: Research needs with voi_rank == 1 from clusters with confidence_level IN [MODERATE, MOD_HIGH] are flagged as "High-Impact Research Opportunities"

---

## 7. LLM Generation Requirements

When meta-reviews are generated by LLM (not human-authored), the following constraints apply:

### 7.1 Model Allocation

| Cluster Type | Model | Rationale |
|---|---|---|
| **High stakes** (n_papers ≥ 8, usage > 500 QA answers/month) | Claude Opus 4.6 | Quality > latency for core beliefs |
| **Medium stakes** (n_papers 5–7, usage 100–500 answers/month) | Claude Opus 4.6 | Default to Opus for consistency |
| **Low stakes** (n_papers ≤ 4, usage < 100 answers/month, heterogeneity low) | Gemini 2.0 Flash | Cost optimization acceptable |
| **Revalidation only** (meta-review exists, updating specific fields) | Gemini 2.0 Flash | Constraint-satisfied generation |

### 7.2 Prompt Structure

All LLM generation prompts must follow this template:

```markdown
# Meta-Review Generation Prompt

You are an expert scientific synthesizer. Your task is to generate a meta-review for a belief cluster.

## Input Data

Cluster ID: {cluster_id}
Antecedent: {antecedent_theme}
Consequent: {consequent_theme}

Evidence Base:
{findings_json_list}

(Each finding includes: finding_id, paper_id, effect_direction, effect_size, sample_size, outcome_measure, population_type, setting_type, design_type)

## Output Schema

You MUST produce valid JSON matching the ClusterMetaReview dataclass. Every field is required.

## Critical Constraints

1. **Hallucination Prevention**: Every claim in belief_statement, mechanisms, and latent_variables MUST cite a specific finding_id or paper_id from the evidence base above. If you cannot find support, you MUST write "no direct evidence available" and label confidence as "speculative".

2. **Confidence Calibration**: Assign confidence_level strictly according to the table in the specification:
   - If n_papers < 3, confidence_level MUST be LOW or MODERATE (never HIGH)
   - If heterogeneity = "high" AND direction_consensus < 75%, confidence_level MUST be MODERATE or LOW (never HIGH)
   - Default to the LOWER level when in doubt

3. **Quantification Requirement**:
   - belief_statement MUST include: effect size estimate AND confidence interval OR "magnitude unclear with reason"
   - heterogeneity_assessment MUST include: I² value OR effect size range
   - effect_size_summary MUST include: N_total AND 95% CI OR "not available: reasons"

4. **Specificity in Research Needs**:
   - Each research need MUST be testable as a standalone study design
   - Each must cite which current gaps it addresses (from heterogeneity or scope)
   - voi_rank MUST be justified by connection to current evidence profile

5. **Scope Conditions Completeness**:
   - MUST specify: population type + age range, setting type, minimum one of (duration, intensity, dosage)
   - MUST explicitly list exclusions (who/where effect does NOT apply)

6. **Theory Link Citations**:
   - Every theory_link MUST include author(s) and year in format: "Theory Name (Author, Year)"
   - Do not cite theories not mentioned in the papers

## Quality Gate

Before returning JSON, check:
- [ ] belief_statement is >150 and <500 characters
- [ ] confidence_level assignment is defensible by evidence profile
- [ ] No mechanism has evidence_count = 0 unless explicitly marked "speculative"
- [ ] Every research_need is testable
- [ ] scope_conditions lists ≥3 of: population, setting, duration, intensity
- [ ] effect_size_summary includes CI or "not available"

If any check fails, STOP and note the failure in a comment field before returning JSON.

## Return Format

Return ONLY valid JSON. No markdown, no explanation. If you cannot generate a meta-review meeting all criteria, return:
{"error": "reason", "cluster_id": "{cluster_id}"}
```

### 7.3 Hallucination Prevention Mechanisms

**Pattern 1: Unsourced Mechanism Claims**
- **Detection**: Scan every mechanism.pathway for causal steps. Cross-reference against findings_ids in evidence base.
- **Prevention**: Append to each mechanism a field `_sourced_from: [finding_id_list]`. If list is empty, force confidence to "speculative" and add disclaimer.
- **Example**:
  - ❌ `{"pathway": "natural light → cortisol reduction", "_sourced_from": []}`
  - ✅ `{"pathway": "natural light → cortisol reduction", "_sourced_from": ["F-0042", "F-0189", "F-0253"], "confidence": "high"}`

**Pattern 2: Inventing Latent Variables**
- **Detection**: Every latent_variable.rationale must cite a specific pattern in the findings (e.g., "heterogeneity correlates with X").
- **Prevention**: Require latent_variables to include `_evidence_pattern: "{specific observation from data}"`.
- **Example**:
  - ❌ `{"name": "stress sensitivity", "rationale": "Individual differences likely explain variance", "_evidence_pattern": null}`
  - ✅ `{"name": "stress sensitivity", "rationale": "Studies reporting baseline stress levels show 2x larger effects than studies not reporting baseline", "_evidence_pattern": "Effect size correlates with sample baseline stress (N=5 studies, r=0.68)"}`

**Pattern 3: Over-Confidence**
- **Detection**: confidence_level == HIGH but n_papers < 8 OR heterogeneity == high OR direction_consensus < 80%
- **Prevention**: Hard constraint in prompt: "If n_papers < 5 or heterogeneity = high or direction_consensus < 80%, you are forbidden from assigning HIGH confidence"

### 7.4 Quality Gate Before Persistence

Before a generated meta-review is persisted, it MUST pass an automated validation pipeline:

```python
def validate_meta_review(mr: ClusterMetaReview) -> Tuple[bool, List[str]]:
    """
    Return (passes, failures) where failures is list of which criteria failed.
    Only persist if passes == True.
    """
    failures = []

    # SC-MR-1
    if not (len(mr.belief_statement) > 150 and "studies" in mr.belief_statement.lower()):
        failures.append("SC-MR-1: Non-trivial belief statement")

    # SC-MR-2
    for m in mr.mechanisms:
        if m.evidence_count < 1 and m.confidence != "speculative":
            failures.append(f"SC-MR-2: Mechanism '{m.pathway}' lacks evidence")

    # SC-MR-3 (confidence calibration)
    expected_level = calibrate_confidence(mr.n_papers, mr.direction_consensus, mr.heterogeneity)
    if mr.confidence_level != expected_level and not is_justified_deviation(mr):
        failures.append("SC-MR-3: Unjustified confidence level")

    # ... (continue for all 10 criteria)

    return (len(failures) == 0, failures)

# At generation time:
meta_review = generate_meta_review_via_llm(cluster)
passes, failures = validate_meta_review(meta_review)
if passes:
    persist_meta_review(meta_review)
else:
    log_quality_failure(cluster_id, failures)
    # Optional: retry with higher-capability model or manual review
```

---

## 8. Forbidden Patterns

Meta-reviews must NOT:

### ❌ Pattern 1: Unqualified Hedging
> "Findings suggest that perhaps daylight might affect stress in some populations."

**Why forbidden**: Excessive hedging paralyzes decision-making. If you don't have confidence, say the confidence level is LOW, not the claim.

**Corrected**:
> "Daylight's effect on stress is low-confidence (ω = 0.41): only 2 studies, conflicting outcome measures, single research team."

---

### ❌ Pattern 2: Treating All Studies as Equal Weight
> "7 studies show daylight reduces stress; 1 study found no effect; therefore the evidence is mixed."

**Why forbidden**: Ignores design quality, sample size, and publication bias. An N=500 RCT is not equivalent to N=25 quasi-experiment.

**Corrected**:
> "7 studies show daylight reduces stress (median N = 58, 5 RCTs, 2 quasi-experimental); 1 study found no effect (N = 12, post-hoc sub-analysis). Direction consensus: 87%. The high-N studies consistently support the effect."

---

### ❌ Pattern 3: Defaulting to MODERATE Confidence
> "We assign MODERATE confidence because research in applied settings always has limitations."

**Why forbidden**: Abdicates the duty to discriminate between strong and weak evidence.

**Corrected**:
> "We assign MOD_HIGH confidence (ω = 0.73) because: 7 studies, 86% direction agreement, low heterogeneity (I² = 22%), replicated by 3 independent teams. Limitations: all studies use self-report outcome (potential demand characteristics), small sample sizes (median N = 58)."

---

### ❌ Pattern 4: Vague Mechanism Claims
> "The effect works through neural mechanisms."
> "This is mediated by attention and emotion."

**Why forbidden**: These are restatements, not explanations. They claim causation without mechanism.

**Corrected**:
> "Pathway: Natural light → suppression of melatonin (pineal gland) → increased alertness and cortisol suppression → reduced self-reported anxiety. Supported by circadian physiology (Czeisler & Gooley, 2007) and 3 studies measuring cortisol directly."

---

### ❌ Pattern 5: Ignoring Contradictory Findings
> "All findings show daylight reduces stress, confirming robustness."

**Why forbidden**: Misses defeats to warrant status. Every finding that contradicts the consensus is a clue to scope limitations or confounds.

**Corrected**:
> "7 of 8 studies show daylight reduces stress. The 1 contradicting study (Smith et al., 2019, N = 40) tested outdoor daylight exposure in a warm climate (35°C) with uncontrolled ventilation, confounding light with temperature. Direction consensus: 87% (after noting this confounder)."

---

### ❌ Pattern 6: Generic Research Needs
> "More research is needed."
> "Future studies should test this in other populations."
> "Additional studies would strengthen the evidence base."

**Why forbidden**: Not actionable; doesn't tell a researcher what gap to fill.

**Corrected**:
> "Rank 1: Does the effect persist in outdoor settings (temperature and humidity uncontrolled)? All current studies are indoor. Design: RCT or quasi-experiment with temperature-controlled outdoor exposure. VOI: Would establish ecological validity."
> "Rank 2: Does sensory sensitivity moderate the effect (population Aron & Aron's HSP scale score > 70)? Heterogeneity correlates with baseline stress, suggesting individual differences matter. Design: Subgroup analysis or moderation test. VOI: Would refine population applicability."

---

### ❌ Pattern 7: Circular Scope Statements
> "Applies to people in various environments under different conditions."

**Why forbidden**: Tells the reader nothing about where the effect does or doesn't apply.

**Corrected**:
> "Applies to: adults (age 20–65) in office environments (indoor, climate-controlled, 18–24°C). Effect strongest in high-stress industries (healthcare, finance). Does NOT apply to: outdoor settings (temperature confound), pre-school children (limited studies, N=2), shift workers (circadian rhythm abnormality)."

---

## 9. Integration with Existing Norms

Meta-review specification integrates with four companion documents:

1. **`SCIENCE_COMMUNICATION_NORMS.md`**: Governs prose style when rendering meta-reviews into QA answers (classic style, given-new contract, stress positions)
2. **`MATH_EXPLANATION_NORMS.md`**: Governs how effect sizes, confidence intervals, and heterogeneity statistics are explained to non-statistician audiences
3. **`QA_ANSWER_NORMS.md`**: Specifies the nine enrichment outputs that meta-reviews feed into (credence_ci, warrant_trace, follow_ups, etc.)
4. **`docs/EPISTEMIC_PRINCIPLES.md`**: Specifies the foundational epistemic commitments (defeasible warrant, foundherentism, severe testing) that constrain what meta-reviews can claim

When these documents conflict, the hierarchy is:
1. **Epistemic Principles** (foundation)
2. **Meta-Review Spec** (data model)
3. **Norms documents** (rendering)

---

## 10. Version History and Change Protocol

**Current Version**: 1.0.0
**Date**: 2026-03-04
**Status**: ACTIVE

**How to Propose Changes**:
1. Propose change in `/sessions/keen-busy-turing/mnt/REPOS/Article_Eater_PostQuinean_v1/docs/SPEC_CHANGE_PROPOSALS.md`
2. Include: rationale, affected fields, impact on existing meta-reviews
3. Await David approval before implementing

**Breaking Changes** (require revalidation of existing meta-reviews):
- Adding required fields
- Changing confidence level calibration criteria
- Changing success condition thresholds

**Non-Breaking Changes** (apply going forward):
- Adding optional fields
- Refining examples
- Clarifying forbidden patterns

---

## References

**Cochrane Collaboration**: *Higgins, J. P., & Green, S. (Eds.). (2011). Cochrane handbook for systematic reviews of interventions (Vol. 5). Wiley-Blackwell.* — Reference for heterogeneity assessment (I² statistic) and meta-analytic methods.

**GRADE Framework**: *Guyatt, G., Oxman, A. D., Vist, G., et al. (2011). GRADE guidelines: 4. Rating the quality of evidence—study limitations (risk of bias). Journal of Clinical Epidemiology, 64(4), 407-415.* — Reference for quality assessment and confidence calibration.

**Effect Size Benchmarks**: *Sawyer, A. G., Pham, L. B., & Cheema, K. L. (2003). Reporting and interpreting effectiveness of behavior change interventions. Journal of Advertising, 32(3), 53-61.* — Benchmark for translating d values into practical significance language.

**Theory of Planned Behavior & Related Models**: Reference group of scholars cited within mechanism candidates (Kaplan & Kaplan for ART, Ulrich for Stress Reduction, etc.)

**Epistemic Foundations**: Pollock (defeasible reasoning), Haack (foundherentism), Mayo (severe testing), Cartwright (causal pluralism), Pearl (causal inference) — as cited in `docs/EPISTEMIC_PRINCIPLES.md`
