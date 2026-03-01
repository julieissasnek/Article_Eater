# RUTHLESS AUDIT RV5-5: Tagging System Quality Review

**Date**: 2026-02-28
**Auditor**: Claude Code (Adversarial Assessment Mode)
**Scope**: stimulus_descriptions_from_articles.json + outcome_vocab.json + decision_tree_equivalence_classes.json
**Overall Score**: 3.5/10

---

## Executive Summary

The tagging system suffers from **three critical systemic failures**:

1. **Semantic category leakage** — shared word boundaries between supposedly distinct categories
2. **Overly generic equivalence classes** — 8 major categories reduced to "primary_feature" (essentially unmeasurable)
3. **Circular operationalizations** — 32 of 116 outcome terms operationalized as re-statements of themselves

The system is **not yet scientifically defensible** without major remediation.

---

## Part 1: Stimulus Categorization Quality

### Finding 1: CRITICAL — "Other" Catch-All Dominance

**Fact**: 8,710 of 23,029 stimuli (37.8%) are tagged as "other."

**Why This Is Critical**:
- "Other" is not a category; it's an admission of classification failure
- When 38% of data is unclassified, the remaining 62% is not a valid sample distribution
- These 8,710 stimuli represent **missing signal** that should inform system design

**Sample "Other" Antecedents**:
```
- "Rupture in interpersonal relationships / alienation from community"
- "Psychological withdrawal from reality (when feeling threatened)"
- "Schizophrenia"
- "Staff placement"
- "Ambiguity and uncertainty in the environment/structure"
```

**Assessment**: These are clearly measurable environmental constructs. They are not in "other" because they're unmeasurable; they're in "other" because the categorization scheme was **not derived from the data**. The categories (lighting, color, plants) are researcher-intuitive, not corpus-grounded.

**Recommendation**: Conduct an unsupervised clustering analysis on antecedent text to discover **actual** categories in the data.

---

### Finding 2: WARNING — Multi-Category Over-Tagging

**Distribution**:
- 58.4% of stimuli: 1 category (good)
- 24.4%: 2 categories (acceptable)
- 10.9%: 3 categories (questionable)
- 4.1%: 4 categories (problematic)
- 2.2%: 5+ categories (critical)

**Examples of 6-8 Category Over-Tagging**:
```
"Distinctive personal living space (furniture, possessions, rugs, pictures, wall decorations...)"
-> [lighting, color_material, furniture_interior, building_type, art_decoration]

"Restorative design elements (privacy nooks, stimulus shelter...)"
-> [plants_greenery, lighting, views, nature, art_decoration]

"Sound Design (Nature sound, Music) + Architectural Features..."
-> [lighting, views, spatial_configuration, color_material, sound_acoustic, nature, art_decoration]
```

**Why This Is Problematic**:
- Stimuli with 5+ tags are essentially **describing entire environments**, not specific antecedents
- This violates the principle that an antecedent is an **isolable feature**, not a compound design
- Creates ambiguity: Is this about the sound design or the lighting? Both? Neither?

**Assessment**: The system conflates **stimulus isolation** with **ecological validity**. A real psychiatric ward has all 8 elements, but tagging it as such defeats the purpose of understanding which specific features drive outcomes.

**Recommendation**: Enforce a maximum of 2 categories per stimulus. For complex antecedents, decompose them into constituent stimuli or flag them as "needs_decomposition".

---

### Finding 3: CRITICAL — Category Boundary Leakage

#### Example A: "Green" Semantic Bleed

Found **7 stimuli** tagged as `color_material` that are really about the word "green":
```
- "Colors (green, blue, white, red, purple, gold, emerald)"
- "pale green color samples with low saturation"
- "Colors in architecture (black, orange, red, yellow, green, blue, white)"
```

These belong in `color_material` by definition, but they bleed conceptually because:
- "Green" also appears in `plants_greenery` and `nature` contexts
- Extractors cannot distinguish semantic green (plant-related) from chromatic green (color-related)

#### Example B: "Design" and "Aesthetic" Leakage into Building Type

Found **14 stimuli** in `building_type` that are really about aesthetics:
```
- "Ward design that makes patients' biological life easy..."
- "Distinctive personal living space (furniture, possessions, rugs, pictures...)"
- "Building design that is an expression of patient needs"
- "hospital space designed to incorporate sound, good space qualities..."
```

These are tagged as "building type" but describe **how buildings are designed** (art_decoration dimension), not which type of building (hospital vs. home vs. school).

**Root Cause**: The category system lacks a **semantic boundary definition file**. What makes something "art_decoration" vs "building_type"? The current approach is intuitive, not formal.

**Assessment**: Without explicit boundary rules, category assignment will continue to leak across semantic domains.

**Recommendation**: Create `contracts/category_boundaries.json` specifying:
- Must contain / must not contain keywords
- Minimum specificity (e.g., "color" ≠ "red wall"; "building" ≠ "hospital lobby")
- Canonical examples for each category

---

## Part 2: Outcome Vocabulary Quality

### Finding 1: CRITICAL — Duplicate Term Across Domains

**Fact**: "Privacy" appears in BOTH `social` and `env` domains.

```json
- privacy (social.privacy) — Interpersonal privacy in group settings
- privacy (env.privacy) — Environmental perception of privacy
```

**Why This Is Critical**:
- These ARE the same psychological construct, just measured at different levels
- Having them in separate domains invites **double-counting** when aggregating psychological outcomes
- Downstream analysis cannot know whether to sum, average, or treat as redundant

**Assessment**: This is not a minor duplicate; it's an **ontological error**. Privacy is fundamentally a **perceptual outcome** that varies by social context. Splitting it across domains suggests the taxonomy itself is flawed.

**Recommendation**:
1. Merge into single domain (likely `affect` or `social`)
2. Add domain-specific operationalizations: "social.privacy" → dyadic privacy measures; "env.privacy" → spatial enclosure measures
3. Add `cognate_domains` field to track cross-domain reuse

---

### Finding 2: CRITICAL — 32 Circular Operationalizations (27.6% of Terms)

These operationalizations **restate the construct rather than operationalize it**:

```
"Attention"
  -> "Attention Network Test (ANT)" [CIRCULAR: name includes "Attention"]

"Divided Attention"
  -> "Divided attention RT cost" [CIRCULAR: restates the construct]

"Frustration"
  -> "Frustration Discomfort Scale" [CIRCULAR: name includes "Frustration"]

"Place Attachment"
  -> "Place Attachment Inventory" [CIRCULAR: name includes "Attachment"]

"Sleep"
  -> "Sleep diary" [CIRCULAR: name includes "Sleep"]

"Social Cohesion"
  -> "Social cohesion index" [CIRCULAR: name includes "Cohesion"]
```

**Why This Is Critical**:
- A valid operationalization shows **how to measure** the construct, not what it is called
- "Attention Network Test" is a valid operationalization ONLY if it explains what the test measures (e.g., "reaction time difference between congruent and incongruent cues")
- 27.6% of the vocabulary is **scientifically indefensible** in current form

**Assessment**: These operationalizations were likely auto-generated or filled with instrument names without subject-matter review. They satisfy the requirement of "having an operationalization" while providing zero scientific value.

**Recommendation**:
1. For each circular operationalization, add **substantive detail**. Example:
   - Before: `"Attention" -> ["Attention Network Test (ANT)"]`
   - After: `"Attention" -> ["Reaction time to target detection; ANT measures congruency effects"]`
2. Create a validation script that flags operationalizations containing the construct name

---

### Finding 3: WARNING — Incomplete Instrument Reference Coverage

**Fact**: Only 52 of 116 terms (44.8%) have `instrument_ids` populated.

**Example of sparse references**:
```
"Wayfinding" (spatial.wayfinding) — no instruments
"Territoriality" (social.territoriality) — no instruments
"Sense of Community" (social.community) — no instruments
```

**Why This Matters**:
- These terms are defined but not operationalized via measurement tools
- A researcher reading the vocabulary cannot know how to measure half the constructs
- Downstream work will either ignore these terms or invent ad-hoc measurements

**Assessment**: Not critical, but a sign of incomplete vocabulary development. These terms may be theoretical placeholders rather than validated outcome measures.

**Recommendation**:
1. For terms without instruments, either: (a) add valid instrument references, or (b) mark as "theoretical_only" and exclude from empirical analyses
2. Audit cognates to ensure every cognate also has instrument coverage

---

### Finding 4: INFO — Cognate Consistency is Good

**Sample cognates**:
```
"Attention" -> ["focus", "concentration"]
"Divided Attention" -> ["multitasking", "parallel processing"]
"Sustained Attention" -> ["vigilance", "continuous focus"]
```

**Assessment**: Cognates are semantically reasonable and not over-generalized. This section is adequate.

---

## Part 3: Decision Tree Equivalence Classes

### Finding 1: CRITICAL — 8 Equivalence Classes Reduced to "Primary Feature"

**Classes affected**:
1. `other_unclassified` (4,601 stimuli)
2. `acoustic_soundscape` (1,858 stimuli)
3. `space_ceiling` (915 stimuli)
4. `thermal_comfort` (283 stimuli)
5. `complexity_clutter_organization` (257 stimuli)
6. [3 others with 100+ stimuli each]

**The Problem**: These classes are defined as:
```
"essential_attributes": ["primary_feature"]
"equivalence_class_definition": "Generic category requiring manual review"
```

This is a **non-operationalization**. "Primary feature" is not measurable. It means: "we know these stimuli are different from each other but don't know how to describe the difference."

**Example Analysis for "Acoustic Soundscape"**:

Representative stimuli:
```
- "Monotonous acoustic environment"
- "Chronic noise exposure (high congestion, crowds)"
- "Increased thickness and blend of blackout and dimout materials"
- "Sounds and visual stimuli"
- "Intermittent loud noise events"
- "White noise level (theoretically attributed to acoustics...)"
```

Do these share a common essential feature? The decision tree claims "primary_feature" (essentially unmeasurable). But obviously they involve:
- **Complexity**: monotonous (simple) vs. multi-event (complex)
- **Frequency composition**: steady noise vs. intermittent
- **Source variety**: single source vs. multiple

The class **should** have essential attributes like:
```
"essential_attributes": ["acoustic_complexity", "temporal_pattern"]
"incidental_attributes": ["noise_level_db", "frequency_range"]
```

**Assessment**: The Kirsh Decision Tree method was either not applied rigorously, or the stimuli are genuinely non-homogeneous and should not be grouped.

**Recommendation**:
1. For each class with "primary_feature" as essential:
   - Sample 10 representative stimuli
   - Conduct human expert card sort to identify shared dimensions
   - Replace "primary_feature" with concrete attributes
2. Or: Admit these classes are heterogeneous and split them into sub-classes

---

### Finding 2: WARNING — "Context" Marked Incidental But May Be Essential

**Classes where context is marked incidental**: 8

**Example**: `acoustic_soundscape` and `space_ceiling`

**The Question**: Is context really incidental, or is the entire class defined by context?

For instance:
- "Monotonous acoustic environment" (in what type of building? office? hospital?)
- "Public spaces (promote connectivity)" (connectivity for whom? children? elderly?)

**Assessment**: Context may be incidental within a well-defined domain, but for catch-all classes, context is often the **primary differentiator**.

**Recommendation**: Explicitly define what "context" means. If context is truly incidental, show that variation across contexts doesn't destroy the stimulus equivalence.

---

### Finding 3: INFO — New Attributes Discovered is Productive

**Good news**: 17 of 25 classes discovered new attributes like:
```
- illuminance_distribution_uniformity
- vegetation_segmentation_ratio
- chromatic_dominance_percentage
- plant_health_vigor_estimation
```

These are **concrete, measurable attributes** derived from the decision tree method.

**Assessment**: This section shows the method is generating actionable insights. Keep this up.

---

## Comparative Category Quality: Ranked

**Best-Defined Categories**:
1. `artificial_lighting` — Essential: illumination_level; Boundary cases clearly identified (CCT, source type)
2. `room_with_plants_greenery` — Essential: plant_presence, green_chromaticity, biomorphic_form
3. `windows_natural_light` — Scene depth, sky proportion, horizon presence

**Worst-Defined Categories**:
1. `other_unclassified` — 4,601 stimuli; no distinguishing features
2. `space_ceiling` — 915 stimuli; aesthetic language mixed with spatial language
3. `acoustic_soundscape` — 1,858 stimuli; includes material properties (acoustic panels) alongside perceptual properties

---

## Summary: Critical Issues by Severity

| Severity | Count | Issue |
|----------|-------|-------|
| **CRITICAL** | 4 | "Other" dominance (38% catch-all); Duplicates (Privacy); Circular operationalizations (27.6%); Generic "primary_feature" essentials (8 classes) |
| **WARNING** | 5 | Multi-category over-tagging (2.2%); Semantic leakage (green, design); Incomplete instrument coverage (55.2%); Context essentiality ambiguity |
| **INFO** | 3 | Cognates adequate; New attributes productive; Boundary case validation clean |

---

## Recommendations (Ranked by Impact)

### Tier 1: Foundational (Must Do)

1. **Eliminate the "Other" category.** Conduct unsupervised text clustering on antecedent descriptions to discover corpus-grounded categories. Current categories are researcher-intuitive, not data-driven.

2. **Operationalize the "primary_feature" classes.** Use human expert review to identify actual shared attributes in stimuli currently tagged as "primary_feature."

3. **Eliminate circular operationalizations.** Add substantive measurement details (e.g., "reaction time to target detection under congruency conditions" instead of just "Attention Network Test").

4. **Merge Privacy domains.** Consolidate social.privacy and env.privacy into a single construct with multi-level operationalizations.

### Tier 2: Structural (Should Do)

5. **Create category boundary rules** (`contracts/category_boundaries.json`). Define what makes something art_decoration vs. building_type with explicit keyword lists and canonical examples.

6. **Limit multi-category tags to 2 maximum.** Decompose complex antecedents into constituent features or flag for manual review.

7. **Add instrument coverage validation.** All non-theoretical terms must have at least one instrument_id; others must be marked "theoretical_only."

8. **Document the Kirsh Decision Tree application.** Show the actual decision tree splits for classes currently reduced to "primary_feature."

### Tier 3: Refinement (Nice to Have)

9. **Add a confidence score to category assignments.** Quantify how confidently each stimulus belongs to its assigned category.

10. **Validate cognate-instrument alignment.** Ensure cognates of a term share instrument coverage.

---

## Final Assessment

**Current Score: 3.5/10**

**Why Not Lower?**
- Lighting and plants_greenery categories are reasonably well-defined
- Outcome vocabulary has structure and partial instrument coverage
- No data integrity errors (missing fields, malformed JSON)

**Why Not Higher?**
- 38% of stimuli are unclassified (institutional failure)
- 27.6% of outcome operationalizations are circular (scientific failure)
- 8 major equivalence classes are unmeasurable (methodological failure)
- Semantic category boundaries are not formally defined (design failure)

**Path to 7+/10**:
1. Resolve the "Other" category via corpus analysis → +2 points
2. Operationalize "primary_feature" classes → +1.5 points
3. Eliminate circular operationalizations → +1 point

**Recommendation**: Do not use this system for inference until Tier 1 remediation is complete. Current state is exploratory/provisional, not production-ready.

---

*Report compiled by Claude Code under adversarial assumption: "The categorization is wrong until proven otherwise."*
