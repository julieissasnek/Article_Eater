# Cognitive-Metabolic-Reward (CMR) Specification
*Version 2.0 — Final*

**Date**: February 28, 2026
**Status**: COMPLETE — Released for Sprint 7 implementation
**Primary Author**: Claude Code (Haiku 4.5) on behalf of Professor David Kirsh, UCSD

---

## Executive Summary

The CMR (Cognitive-Metabolic-Reward) Specification defines the architecture and semantics of a unified claim evaluation engine that normalizes empirical and theoretical findings against a library of 208 mechanistic templates grounded in 10 Tier-1 neuroscientific frameworks. The specification enables:

1. **Claim Normalization**: Converting free-text claims into canonical `{IV} {Relationship} {Direction} {DV}` tuples
2. **Template Matching**: Routing normalized claims to applicable mechanistic templates
3. **Theory Anchoring**: Linking empirical patterns to foundational theories via explicit theory_links
4. **WIS Conversion**: Converting raw template outputs into unified Wellbeing Impact Scores
5. **Multi-System Integration**: Composing answers from overlapping, interacting templates

The specification is grounded in Document 68 (frozen CMR Implementation Contract) and references the following canonical files:
- `schemas/template_canonical.json` — Template JSON schema
- `contracts/ae_af/schemas/ae.rule.v2.schema.json` — Rule record schema (extended herein)
- `schemas/canonical_variables.json` — Canonical variable vocabulary
- `data/theories/*.json` — T1.5 theory definitions
- `src/theories/profiles/*.py` — T1 framework agent profiles

---

## Section 1: Template Library Schema

### 1.1 Overview
Templates are the atomic units of the CMR system. Each template encodes a specific mechanistic pathway: a change in one or more environmental features leads to a measurable psychological or behavioral outcome through an identifiable causal chain.

**Source**: 208 JSON template files in `data/templates/`, indexed by `TemplateRecord` database (Doc 68, Part 2.1).

### 1.2 Template Canonical Schema
All templates conform to `schemas/template_canonical.json` (2020-12 JSON Schema draft). Templates declare:

| Field | Type | Required | Purpose |
|-------|------|----------|---------|
| `template_id` | string | Yes | Unique long ID (e.g., `NATURE_VIEW_CONVERGENCE_001`) |
| `display_id` | string | Yes | Short display ID (e.g., `VIEW1`, `CREA2B`) |
| `name` | string | Yes | Human-readable name |
| `t1_frameworks` | array | Yes | List of T1 framework IDs (e.g., `["PP", "IC"]`) |
| `calibration_status` | enum | Yes | `calibrated` / `scaffold` / `partial` / `uncalibrated` |
| `mechanism_chain` | array | No | Sequential causal steps (Gen-2 schema) |
| `bridge_warrant` | enum | No | Warrant type connecting to architecture (see 1.3) |
| `confidence` | number | No | Prior probability 0–1 |
| `residual_gaps` | array | No | Known gaps requiring future work |
| `cross_template_interactions` | array | No | Known interactions with other templates |

### 1.3 Bridge Warrant Types (Canonical)
Each template step involves a **bridge warrant** connecting environmental variables to psychological mechanisms. Seven canonical types defined per `template_canonical.json/$defs/bridge_warrant_type`:

| Type | Description | Discount Factor | Use Case |
|------|-------------|-----------------|----------|
| **CONSTITUTIVE** | The environmental feature IS instantaneously the mechanism | 0.95 | E.g., color → neural activity (direct substrate) |
| **MECHANISM** | Environmental feature triggers a known causal mechanism | 0.85 | E.g., complexity → prediction error → PE-minimization |
| **EMPIRICAL_ASSOCIATION** | Robust empirical correlation without full mechanistic explanation | 0.70 | E.g., nature view → stress reduction (mechanism unclear) |
| **FUNCTIONAL** | Teleological: the mechanism FUNCTIONS to achieve this outcome | 0.65 | E.g., stress response → escape behavior (functional design) |
| **CAPACITY** | Environmental feature enables an organismic capacity | 0.60 | E.g., light levels → circadian phase-locking capacity |
| **ANALOGICAL** | Analogical mapping from known domain to architectural domain | 0.50 | E.g., "flow" in sports → flow in workspace design |
| **THEORY_DERIVED** | Derived from theory but not yet empirically validated in architecture | 0.40 | E.g., Gibsonian affordances → wayfinding clarity |

Discount factors apply in WIS conversion (Section 4.5) to weight template contributions by epistemic warrant strength.

### 1.4 Template Deduplication Status
Per Doc 67 Part 1, templates are classified into five deduplication statuses:

| Status | Meaning | Action |
|--------|---------|--------|
| **active** | Primary template; can be activated | Include in CMR pipeline |
| **superseded** | Newer template replaces this one (see `superseded_by`) | Skip; redirect to newer |
| **residual** | Partial evidence; cannot be independently activated | Used only in composition checks |
| **reference** | Purely informational; not empirical | Metadata only |
| **gap** | Identifies a missing mechanistic template | Flags opportunity for future work |

### 1.5 Template Indexing and Querying
Templates are indexed for rapid retrieval by (IV, DV) pairs. Two indexing schemes:

#### Explicit Indexing
Template `mechanism_chain` steps define explicit `from` (IV) and `to` (DV) node pairs. These are indexed directly.

Example:
```
Template: "CEILING_HEIGHT_001"
Step 1: from="spatial_proportions", to="prospect_perception"
Step 2: from="prospect_perception", to="psychological_openness"
Step 3: from="psychological_openness", to="cognitive_fluency"

Indexed as:
  (spatial_proportions → prospect_perception)
  (prospect_perception → psychological_openness)
  (psychological_openness → cognitive_fluency)
```

#### Semantic Indexing
For templates without explicit steps, semantic matching routes claims by comparing variable names in the claim to known mappings in the template.

### 1.6 Template Interaction Rules

#### Multi-Template Activation
When a single claim activates multiple templates, interaction rules determine how their outputs compose.

**Additive (Default)**:
Most template pairs sum their WIS contributions. Example: a ceiling-height intervention affects both predictive processing (via spatial proportion PE) and interoceptive comfort independently. WIS scores aggregate.

**Sub-Additive (Shared Mechanism)**:
When templates share an underlying mechanism, their effects are capped. Example: CREA2 (creativity via complexity) and VF3 (visual rhythm) both operate through prediction error minimization. When both are active, apply 20% reduction to prevent double-counting.

Interaction matrices are declared in the interaction table (currently: CREA-series, VF-series, Convergence Triad).

#### Supersession Semantics
When a newer Gen-2 template supersedes an older Gen-1 template:
1. Query returns the newer template by default
2. Older template can still be queried explicitly (for historical/audit purposes)
3. WIS conversion applies discount based on `calibration_status` of newer template
4. In interaction calculations, skip the superseded template

Example:
- VF3 (Gen-2, calibrated) supersedes VF1 (Gen-1, scaffold)
- If query triggers "visual flow," activate VF3 only
- VF1 documented in `superseded_by` field but not activated

---

## Section 2: Prediction Grammar and Normalization

### 2.1 Canonical Claim Structure
Every claim evaluated by CMR normalizes to:

```
{IV_1, IV_2, ...} {Relationship} {Direction} {DV}
```

Where:
- **IVs**: Independent variables (environmental features or interventions)
- **Relationship**: Link type from {modulates, predicts, causes, associates_with, mediates, moderates}
- **Direction**: Polarity from {positive, negative, u_shaped, interaction, unknown}
- **DV**: Dependent variable (outcome measure)

### 2.2 Canonical Variable Vocabulary
All variables map to canonical names in `schemas/canonical_variables.json`. This vocabulary covers:

**Environmental Variables**:
- Spatial features: `spatial_enclosure_ratio`, `ceiling_height_proportional`, `floor_area_openness`, `contour_angularity`
- Material/Visual: `material_texture_variance`, `color_saturation`, `chromatic_harmony`, `surface_reflectance`
- Temporal: `light_circadian_alignment`, `acoustic_rhythm_periodicity`, `temperature_oscillation`
- Biological: `biotic_presence_score`, `plant_coverage_fraction`, `faunal_richness_index`

**Psychological Outcomes**:
- Affective: `mood_valence`, `energetic_arousal`, `tense_arousal`, `approach_inclination`
- Cognitive: `creative_divergence`, `focus_sustained`, `memory_encoding_strength`, `learning_rate`
- Physiological: `cortisol_diurnal_slope`, `hrv_parasympathetic_tone`, `sleep_efficiency`, `immune_function_proxy`
- Social: `prosocial_behavior_inclination`, `group_cohesion_strength`, `trust_propensity`

Canonical names use **snake_case** (lowercase, underscores) for machine readability. Extraction prompts convert from paper author's language to canonical names via LLM mapping with human verification.

### 2.3 Relationship Types
Seven canonical relationships:

| Relationship | Meaning | Example |
|--------------|---------|---------|
| **modulates** | IV changes the strength/intensity of DV | "Ceiling height modulates preference ratings" |
| **predicts** | IV is a statistical predictor of DV | "Spatial legibility predicts wayfinding accuracy" |
| **causes** | Causal mechanism proposed (Pearl intervention level) | "Complexity causes stress via prediction error" |
| **associates_with** | Observed correlation without mechanistic claim | "Green space associates with physical activity" |
| **mediates** | IV → Mediator → DV (Mediator is mechanistic link) | "Complexity → prediction-error → arousal" |
| **moderates** | IV changes the relationship between another IV and DV | "Age moderates the ceiling-height effect" |

### 2.4 Direction Heuristics
Computed by keyword analysis on claim text and template description:

**Positive Direction** (+): Keywords like "increase", "improve", "enhance", "promote", "facilitate", "support", "elevate", "amplify", "strengthen"

**Negative Direction** (−): Keywords like "decrease", "reduce", "diminish", "inhibit", "suppress", "undermine", "weaken", "block", "impair"

**U-Shaped**: Keywords like "optimal", "inverted-U", "Goldilocks", "sweet spot", "moderate levels preferred" combined with evidence of non-monotonic relationship

**Interaction**: Keywords like "depends on", "conditional on", "moderated by", "interaction effect" indicating a moderating variable

**Unknown**: No clear directional markers or contradictory signals

### 2.5 Normalization Rules
Free-text claims are converted to canonical form via:

**Step 1: Variable Mapping**
LLM extracts subject (IV) and object (DV) of the claim. Maps them to canonical names using `canonical_variables.json` glossary.

**Step 2: Relationship Identification**
Identifies relationship keyword (modulates, causes, etc.). If absent, defaults to "associates_with" (empirical association).

**Step 3: Direction Inference**
Scans claim text for directional keywords. If polarity unclear, human reviewer makes judgment; default is "unknown".

**Step 4: Scope Conditions**
Notes boundary conditions, moderators, or population restrictions in the claim (e.g., "for children under 8" or "in high-stress occupations"). These populate `applicability` in ae.rule.v2.

**Step 5: Evidence Basis**
Records effect size, sample size, design (RCT, quasi-experiment, observational), and confidence.

### 2.6 Edge Cases in Normalization

**U-Shaped Relationships**:
Some effects are non-monotonic (e.g., complexity has a Goldilocks zone). Represent as:
```
{complexity_level} u_shaped {aesthetic_preference}
  scope: [low_boundary: 2, optimal_zone: 4-6, high_boundary: 8]
```

**Interaction Effects**:
When outcome depends on joint levels of multiple IVs:
```
{ceiling_height, natural_light} interaction {focus_duration}
  scope: [high_ceiling + abundant_light → max effect;
          high_ceiling + dim_light → moderate effect]
```

**Threshold Effects**:
Some variables show step changes:
```
{enclosure_ratio} causes {claustrophobic_response}
  scope: [threshold: 0.7, below: no_response, above: rapid_onset]
```

---

## Section 3: Theory Link Integration

### 3.1 Tier Structure
Article_Eater uses three theory levels:

| Tier | Name | Scope | Examples |
|------|------|-------|----------|
| **T1** | Neural-Architecture Mapping | 10 Tier-1 frameworks grounded in neuroscientific mechanisms | Predictive Processing (PP), Neuromodulation (NM), Interoception (IC) |
| **T1.5** | Mid-Level Theories | ~30 formal reductions bridging T1 and empirical phenomena | Processing Fluency, Affordance Perception, Place Attachment |
| **T2** | Architectural Theories | Domain-specific, less mechanistically explicit | Biophilia, Stress Reduction Theory (SRT), Attention Restoration Theory (ART) |

Templates are grounded in T1 frameworks (`t1_frameworks` field in template schema). Theory links connect rules to T1.5 and T2 theories, enabling cross-tier queries.

### 3.2 Canonical Theory Roster (T1.5 and T2)
The system recognizes 43 formal theories:

**T1.5 (Mid-Level, Mechanistically Reduced)**:
1. Processing Fluency (Reber, Schwarz, Winkielman)
2. Predictive Coding in Music (Koelsch)
3. Auditory Scene Analysis (Bregman)
4. Cognitive Maps (Tolman, O'Keefe)
5. Affordance Perception (Gibson)
6. Prospect-Refuge Theory (Appleton)
7. Space Syntax (Hillier)
8. Chronobiology (Circadian Regulation)
9. Place Attachment (Williams, Vaske)
10. Proxemics (Hall, Sommer)
... and 20+ others (see `data/theories/*.json`)

**T2 (Domain Theories)**:
1. Biophilia (Wilson; E.O. Wilson, Kellert, Heerwagen)
2. Stress Reduction Theory (Kaplan & Kaplan; Ulrich)
3. Attention Restoration Theory (Kaplan & Kaplan)
4. Salutogenic Design (Antonovsky)
5. And ~25 others mapped to T1 via reduction panels

### 3.3 TheoryLink Schema

Rules in `ae.rule.v2` declare their connection to theories via a `theory_links` array. Each link is an object:

```json
{
  "theory_id": "PROCESSING_FLUENCY",
  "from_variable": "visual_complexity",
  "to_variable": "aesthetic_preference",
  "from_level": "T1.5",
  "to_level": "T1",
  "activity": "supports",
  "maturity": "how-actually"
}
```

**Field Definitions**:

| Field | Type | Values | Meaning |
|-------|------|--------|---------|
| `theory_id` | string | e.g., "PROCESSING_FLUENCY", "ART", "BIOPHILIA" | Canonical theory ID from roster |
| `from_variable` | string | Canonical variable name | IV as described by this theory |
| `to_variable` | string | Canonical variable name | DV as described by this theory |
| `from_level` | string | T1, T1.5, T2 | Level of the from_variable in theory hierarchy |
| `to_level` | string | T1, T1.5, T2 | Level of the to_variable in theory hierarchy |
| `activity` | enum | supports, contradicts, extends, qualifies | How the rule relates to theory predictions |
| `maturity` | enum | how-actually, how-plausibly, how-possibly | Confidence level per Spohn |

### 3.4 Theory Agent Profile Contract
Each T1 framework (PP, NM, IC, DT, DP, EC, IE-DPT, AX, CB, MSI) has an agent profile module at `src/theories/profiles/{abbrev}_profile.py`.

Each profile exports 11 required constants:

```python
THEORY_ID: str                           # Framework code (e.g., "framework:predictive_processing")
THEORY_NAME: str                         # Full name
CORE_MECHANISM: str                      # 300-500 word description of the mechanism
EXPLAINS: List[str]                      # Claims this theory explains (20-30 items)
DOES_NOT_EXPLAIN: List[str]              # Scope boundaries (what it doesn't claim)
STIMULUS_INCLUDES: List[str]             # Types of environmental features it addresses
STIMULUS_EXCLUDES: List[str]             # Features it does NOT address
STIMULUS_EDGE_CASES: List[Dict]          # Ambiguous stimuli and judgment heuristics
PREDICTED_OUTCOMES: List[str]            # Psychological/behavioral outcomes it predicts
NOT_PREDICTED_OUTCOMES: List[str]        # Outcomes explicitly outside its scope
MATCHING_PROMPT: str                     # LLM prompt for evaluating claim scope membership
FEW_SHOT_EXAMPLES: List[Dict]            # Examples of CONFIRMS, DISCONFIRMS, ORTHOGONAL judgments
```

These profiles enable the **TheoryAgentCouncil** (in `src/theories/theory_agent_council.py`) to evaluate whether a claim falls under a theory's scope.

### 3.5 Extraction Protocol for Theory Links
When extracting rules from papers:

**Step 1: Claim Extraction**
LLM identifies all causal claims. For each claim, asks: "Which T1.5 or T2 theories would likely predict or explain this finding?"

**Step 2: Theory Matching**
For each claimed theory connection, verify:
- Does the paper explicitly mention this theory?
- Does the claimed connection map to the theory's core constructs?
- What is the maturity level (actual, plausible, possible)?

**Step 3: Link Recording**
Create a `TheoryLink` object with the theory ID, variables, direction, and maturity. Populate `ae.rule.v2.theory_links` array.

**Step 4: Human Review**
Domain expert (or panel) reviews extracted links. Confirms:
- Is this theory actually invoked by the paper?
- Are the variable mappings accurate?
- Is the maturity judgment calibrated correctly?

---

## Section 4: CMR Evaluation Pipeline (Building Assessment)

### 4.1 Pipeline Overview
The Building Evaluation Pipeline converts environmental measurements into domain-level wellbeing assessments. Nine steps (per Doc 68, Part 3.1):

```
Input (Context) → Feature Input → Template Activation → Computation →
WIS Conversion → Interaction Adjustment → Domain Aggregation →
Overall Assessment → Report
```

### 4.2 Step 1: Context Definition
**Input**: Building type, climate zone, occupant profile

**Process**:
- Store building context in CMREvaluation record
- Identify applicable domain set (A1–A10) based on building type
- Apply population-specific parameter adjustments (age, cultural context)

**Output**: CMREvaluation record with context; template-specific parameter adjustments

### 4.3 Step 2: Feature Input
**Input**: Measured/estimated architectural features

**Process**:
- For each feature, identify which templates it feeds
- Check `practical_accessibility` tier (A/B/C/D) in template metadata
- Tier A inputs required for activation; Tier B-D flagged as "not assessed"

**Output**: Structured feature dictionary; list of missing Tier A inputs (data gaps)

### 4.4 Step 3: Template Activation
**Input**: Feature dictionary + context

**Process**:
- For each template with `dedup_status = "active"`:
  - Check if required inputs available
  - If yes: activate (full confidence)
  - If partial: activate with reduced confidence
  - If no required inputs: skip, record as data gap
- Check supersession: if newer template active, skip superseded

**Output**: List of CMRTemplateActivation records

### 4.5 Step 4: Template Computation
**Input**: Activated templates + their inputs

**Process**:
- Execute template-specific computation (template-dependent logic)
- Apply lifespan moderation (AGE-I/DEV-I multipliers) based on occupant_profile.age
- Apply cultural moderation where applicable
- Record raw outputs (effect sizes, zone classifications, indices)

**Output**: Raw template outputs

### 4.6 Step 5: WIS (Wellbeing Impact Score) Conversion
**Input**: Raw template outputs

**Process**:
Apply Doc 67 Part 3 conversion rules. Four conversion methods:

#### Cohen's d Conversion
```
WIS = Φ(d / √2) × 100
```
Where Φ is the standard normal CDF.
- d = 0 → WIS ≈ 50 (no effect)
- d = 0.5 → WIS ≈ 69 (medium effect)
- d = −0.5 → WIS ≈ 31 (negative effect)

#### Goldilocks Zone Conversion
When template output is a zone classification (Low/Optimal/High):
```
WIS =
  20  (if Low zone)
  85  (if Optimal zone)
  30  (if High zone)
```
Adjust boundaries based on template-specific zone definitions.

#### Threshold Conversion
When template output crosses a threshold:
```
WIS = 50 + 35 × tanh(k × distance_from_threshold)
```
Calibrate k per template.

#### Quality Index Conversion
For dimensionless indices (0–1 scales):
```
WIS = index_value × 100
```

#### Confidence Intervals
Propagate from `calibration_status`:
- `calibrated` → ±5 WIS
- `partial` → ±10 WIS
- `protocol` → ±15 WIS
- `uncalibrated` → ±20 WIS

Apply discount factor from bridge warrant type (Section 1.3) to adjust confidence.

**Output**: Template-level WIS scores with confidence intervals

### 4.7 Step 6: Interaction Adjustment
**Input**: Template-level WIS scores + interaction records

**Process**:
Check interaction matrices:

**Sub-Additive (shared mechanism)**:
- CREA2 2×2×2: if multiple pathways active, apply 20% reduction
- Example: ceiling height + visual rhythm both activate → scale down interaction pair

**Additive (independent mechanisms)**:
- VF1 × VF3: add WIS contributions (no adjustment)

**Super-Additive (convergence)**:
- Convergence Triad (L3 + MAT4 + VIEW1): if all three active, apply 15% bonus
- Rationale: multiple independent supports for same outcome

**Deduplication**:
- VF3 (Gen-2) supersedes VF1 → if both trigger, use VF3 only

**Output**: Adjusted WIS scores for each template

### 4.8 Step 7: Domain Aggregation
**Input**: Adjusted template WIS scores

**Process**:
- Group templates by domain (A1–A10)
- Weighted average within each domain:
  ```
  Domain_WIS = Σ(template_WIS × weight) / Σ(weight)
  ```
  Where weights = {calibrated: 1.0, partial: 0.7, protocol: 0.4, uncalibrated: 0.2}
- Propagate confidence intervals via standard error propagation

**Output**: CMRDomainScore record for each assessed domain

### 4.9 Step 8: Overall Assessment
**Input**: Domain WIS scores

**Process**:
- Compute geometric mean of domain WIS scores
- Flag domains with WIS < 30 as "severe deficits"
- Flag domains with insufficient data as "gaps"
- Propagate uncertainty via confidence interval propagation

**Output**: CMROverallScore record

### 4.10 Step 9: Report Generation
**Input**: All above

**Output**: Structured report containing:
- Overall WIS score with confidence interval
- Domain breakdown (table with WIS, confidence, n_templates)
- Strengths (domains WIS > 70)
- Deficits (domains WIS < 40)
- Data gaps (domains not assessable)
- Specific recommendations (templates with lowest WIS; what changes would improve them)
- Uncertainty disclosure (which parameters are expert estimates vs. empirically validated)

---

## Section 5: Query and Activation Semantics

### 5.1 User Query Decomposition
When a user asks: *"What affects productivity in open offices?"*

**Step 1: Parse Query**
Extract key entities: `affects` (relationship), `productivity` (DV), `open office` (setting context)

**Step 2: Canonicalize**
Map "productivity" → canonical variables {`focus_sustained`, `task_completion_rate`, `creative_divergence`}
Map "open office" → building type + occupancy context

**Step 3: Template Lookup**
Query TemplateRecord: "Find all active templates with DV in {focus_sustained, task_completion_rate, creative_divergence} and t1_frameworks matching {cognitive, neuroprotective, ...}"

**Step 4: Activate Matching Templates**
For each matching template, follow Steps 2–8 of the pipeline.

### 5.2 Deduplication Rules for Overlapping Predictions
When multiple templates predict the same or similar outcomes:

**Exact Overlap**: Same template activated multiple times → report once (deduplicate)

**Partial Overlap**: Templates CREA2 and CREA4 both predict creativity, but via different mechanisms (complexity vs. multi-sensory integration).
- Activate both
- Apply interaction adjustment if they share substrate
- Aggregate via weighted average

**Conceptual Overlap**: PP (predictive processing) predicts "engagement via PE minimization"; ART (attention restoration) predicts "engagement via fascination".
- Both activate
- Check interaction matrix: if independent mechanisms → sum WIS; if shared (e.g., both reduce arousal) → apply sub-additivity

### 5.3 Confidence Aggregation
When multiple templates contribute to a domain score:

**Weighted Confidence Propagation**:
```
Domain_confidence = √(Σ(weight^2 × conf^2) / (Σ weight)^2)
```
Gives more weight to high-confidence templates.

**Conflict Resolution**: If templates predict opposite directions (one + positive, one negative):
- Flag as "contested"
- Report both scores with higher uncertainty range
- Suggest additional evidence needed to resolve

### 5.4 Output Format Specification

#### Summary Report
```
Overall Wellbeing Impact Assessment
=====================================
Overall WIS Score: 72 ± 8 points
Confidence: High (calibrated evidence, n=47 templates, 8 domains)

Domains Assessed:
  A1 (Prospect & Spatial Flow):    78 ± 6
  A2 (Visual Coherence):             82 ± 5
  A3 (Acoustic Climate):             58 ± 12
  ...
  A10 (Occupant Agency):             41 ± 15

Strengths (WIS > 70):
  - Natural light integration (VIEW1, PP-framed)
  - Spatial legibility (SN, DP-framed)

Deficits (WIS < 40):
  - Acoustic isolation (NM, CB-framed) — recommend acoustic retrofit
  - Thermal control (MSI, NM-framed) — recommend smart HVAC

Data Gaps:
  - Biotic presence not measured; cannot assess A6 fully
  - Occupant demographics unknown; cannot apply cultural moderators
```

#### Template-Level Details
For each activated template:
```
Template: CEILING_HEIGHT_001 (CEIL1)
  Status: Calibrated
  Activation Reason: Measured ceiling_height = 3.2m
  Input: {ceiling_height: 3.2, floor_area: 250}
  Raw Output: {prospect_score: 0.72, openness_index: 8.1}
  WIS Conversion: Cohen's d = 0.45 → WIS = 68 ± 5
  Domain: A1
  Interactions: None
```

---

## Appendix A: Canonical Bridge Warrant Discount Factors

(Reference Section 1.3 above)

## Appendix B: Template Series Legend

**CREA** (Creativity via Complexity): CREA1–CREA4 + CREA2B
**VF** (Visual Flow): VF1, VF3
**L** (Legibility): L1–L5
**VIEW** (Nature Views): VIEW1, VIEW2
**T** (Thermal): T1–T4
**MAT** (Material Properties): MAT1–MAT4
**AX** (Affordances/Experience): AX1–AX5
**IC** (Interoceptive/Embodied): IC1–IC3
**SN** (Spatial Navigation): SN1–SN3
And 18+ others (see `data/templates/` for complete roster)

## Appendix C: References

1. Document 68 — CMR Implementation Contract V1.0 (Feb 17, 2026)
2. Document 67 — WIS Conversion and Template Deduplication (Codex)
3. ATLAS Bridge Warrants Framework (Cartwright, Pearl, Toulmin)
4. Spohn, W. (2012). The Laws of Belief. Oxford University Press.
5. Barrett, H. C., & Broesch)
$(10 = \prod_i d_i^{w_i})$ in Compositional Analysis
6. Kirsh, D. (2024). Cognitive Architecture and Environmental Design. UCSD CogSci.

---

*CMR Specification Version 2.0*
*Completed February 28, 2026*
*Primary Input: Document 68, Template Registry, Theory Profiles*
*Status: Released for Sprint 7 (S10) implementation*
