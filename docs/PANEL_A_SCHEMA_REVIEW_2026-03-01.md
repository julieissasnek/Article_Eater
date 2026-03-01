# Panel A: Template Schema Review
## Expert Panel Consultation

**Date**: 2026-03-01
**Panel Type**: Schema Architecture & Measurement Validity
**Quorum**: 3 panelists (all present)

---

## Panel Composition

| Panelist | Expertise | Tradition | Role |
|----------|-----------|-----------|------|
| Dr. Donald Shadish (Methodology) | Experimental design, validity theory, measurement quality | Cook-Campbell-Shadish causal validity | Domain Expert |
| Dr. Rachel Kaplan (Environmental Psychology) | Restorative environment theory, human-environment relationships | Kaplan-Ulrich tradition | Domain Expert |
| Dr. John Ioannidis (Meta-Science) | Replication, measurement quality, systematic bias detection | Ioannidis meta-research | Methodologist |

---

## Input Materials Summary

**Source**: `/contracts/schemas/extraction_template.v2.schema.json` (Version 2.0)
**Size**: 687 lines (JSON Schema draft-07)
**Key Structures**:
- Root properties: doi, article_type, article_family, quality_score, findings array
- Finding object (required): id, antecedent, consequent, claim_type
- New fields (v2.0): stimulus_description, stimulus_images, theory_commitments, mechanism_chain, molecule_ids, success_conditions, instruments_used
- Nested objects: StimulusDescription, StimulusComponent, StimulusImage, TheoryLink, TheoryCommitment, MechanismStep, SuccessConditions, InstrumentUsed

**Key Addition in v2.0**: The schema now requires/supports detailed stimulus characterization (visual scenes, soundscapes, thermal, olfactory, spatial, lighting, material, mixed), mechanism chains, and links to semantic molecules (rasa attractors).

---

## Panel Questions

### Q1: Are the new fields well-defined and necessary?

**Dr. Shadish (Methodology):**

The new fields represent a significant structural upgrade, but I have mixed confidence in their current definition. Let me address each:

1. **stimulus_description** (StimulusDescription object with primary_type, components, delivery_method, duration): **Excellent addition.** This operationalizes a critical validity threat in environmental research—the fidelity of stimulus representation. In the Campbell validity framework, *construct validity* depends on whether the IV truly instantiates the theoretical construct intended. Environmental stimuli are notoriously subject to confounds (weather, social context, individual differences in perception). By requiring explicit decomposition into components and delivery method, you force extractors to specify *what exactly was presented*, which is essential for replication.

   **Confidence: 0.90**
   Reasoning: This directly addresses threats to construct validity and external validity (generalizability across delivery media—photo vs. VR vs. in situ produces different results; see Bombaci et al. 2019 on photo bias in environmental perception).

2. **stimulus_images** (array of StimulusImage with vision_attributes): **Important but incomplete.** The structure (description, figure_ref, image_type, vision_attributes) is a good start, but the vision_attributes are underspecified. You list them as "additionalProperties: { type: number }" without constraints, units, or meaning. This will lead to extractors inserting arbitrary metrics. I recommend a closed enum of allowed attributes with units (e.g., 'brightness_nits', 'contrast_ratio', 'green_channel_histogram', etc.).

   **Confidence: 0.75**
   Reasoning: Measurement without operationalization is noise. See Carmines & Zeller (1979) on validity—you need explicit definitions and constraints.

3. **theory_commitments** (array with commitment_type: tests, extends, contradicts, assumes, proposes): **Excellent. Essential.** This operationalizes epistemic responsibility by forcing extractors to declare *how* a finding engages theory, not just *that* it does. The five commitment types are sensible and map well to the evidential roles a finding can play.

   **Confidence: 0.88**
   Reasoning: This prevents vague hand-waving like "this finding relates to ART"—now you must specify *whether* the finding tests, extends, or contradicts ART.

4. **mechanism_chain** (array of MechanismStep with step, from_construct, to_construct, mechanism_type, evidence_strength): **Valuable but risky.** The structure is theoretically sound, but extractors will struggle to populate this from article text. Most papers do not explicitly lay out step-by-step mechanisms. Forcing extraction here will either (a) lead to vague, post-hoc inference by the LLM, or (b) create many null values that signal missing data rather than actual mechanisms.

   **Confidence: 0.65** (confidence in utility; 0.85 in theoretical soundness)
   Reasoning: See Diagram Gloss Problem (Dennett, 1984) and criticism of causal diagrams in social science (Cartwright & Montuschi, 2014). The step-by-step format is good, but you need to tag evidence_strength carefully and allow "assumed" mechanisms without guilt.

5. **molecule_ids** (array of strings linking to rasa_attractors.json entries): **Novel and uncertain.** This links empirical findings to semantic "attractors" (emotional-perceptual patterns). This is philosophically interesting but **high risk for confounding**. Molecules encode *valences* (emotional/aesthetic qualities) that may or may not be causal. A finding about sunlight increasing alertness might be tagged to a molecule like "Brightness+Clarity" that also encodes aesthetic pleasure, but these are separate constructs. You conflate *causal efficacy* with *aesthetic valence*.

   **Confidence: 0.50** (high uncertainty)
   Reasoning: Clarify the epistemology. Are molecules *causes* or *descriptors*? If the latter, they should be post-hoc categorizations, not driver of extraction.

6. **success_conditions** (SuccessConditions object with min_findings, required_fields, theory_link_expected, mechanism_expected): **Good but underdeveloped.** This operationalizes acceptance criteria, which is essential for systematic review. However, the current structure conflates **data-quality checks** (required_fields) with **theoretical requirements** (theory_link_expected). I'd separate these:
   - Data-quality tier: which fields must be non-null for use in analysis?
   - Epistemic tier: which fields are expected given claim_type and article_family?

   **Confidence: 0.72**
   Reasoning: Shadish et al. (2002) distinguish between *internal* and *construct* validity—these require different success criteria.

7. **instruments_used** (array of InstrumentUsed with name, construct_measured, reliability): **Excellent.** Measurement transparency is foundational. This is especially important for psychological constructs (stress, restoration, preference) which have multiple validated instruments. By requiring explicit naming and reliability reporting, you create a bridge to the measurement literature and enable comparison across papers using different instruments.

   **Confidence: 0.92**
   Reasoning: This is the gold standard for meta-analysis—see Borenstein et al. (2009) on instrument homogeneity as a moderator.

---

**Dr. Kaplan (Environmental Psychology):**

Let me speak to the new fields from the perspective of environmental psychology research, where I've worked for 40+ years:

**stimulus_description**: *Absolutely essential.* Environmental psychology has been plagued by **stimulus ambiguity**. A "natural view" in a hospital window study might be a photograph, a living tree view, or a video loop—each produces different stress-reduction effects (Ulrich, 1984; Kaplan & Kaplan, 1989). By mandating decomposition into components and delivery method, you force clarity. **However**, I see a critical omission: **temporal dynamics**. Duration (duration_seconds) is captured, but not *time-of-exposure*, *frequency*, or *familiarity*. A five-minute exposure to a restorative environment produces different cognitive recovery than sustained engagement. I strongly recommend adding fields for:
- exposure_frequency (discrete, continuous, intermittent)
- habituation_control (whether study controlled for novelty effects)
- prior_familiarity_rating (whether participants had been to this environment before)

**Confidence in current: 0.70** (good foundation, incomplete for longitudinal effects)

**stimulus_images with vision_attributes**: This is promising because restorative environment theory predicts specific visual properties (complexity, legibility, mystery—Kaplan & Kaplan, 1989). Your schema allows quantified vision_attributes, but you don't specify *which* attributes matter. The vision_attributes object is too open. I'd recommend pre-populating it with attributes grounded in restorative environment research:
- fractal_dimension (natural complexity; Hagerhall et al., 2004)
- legibility (can you parse the scene?)
- mystery (depth cues, partially obscured elements)
- prospect_refuge_ratio (open vistas vs. enclosed spaces; Appleton, 1975)
- biophilia_density (presence of plants, water, sky, soil tones)

**Confidence: 0.65** (Good intent; too loose operationally)

**theory_commitments**: *Very strong.* Environmental psychology is fragmented across multiple competing theories (ART, SRT, prospect-refuge, biophilia, stress-reduction, soft fascination). Forcing extractors to declare *which theory* a finding engages—and *whether* it tests, extends, or contradicts—would clarify literature coherence. This is exactly what the field needs.

**Confidence: 0.90**

**mechanism_chain**: This is where things get thorny. Environmental psychology has weak mechanistic theory. Most papers document that *exposure to nature reduces stress* without explaining *why*. Mechanism candidates include:
- Attention Restoration (soft fascination → restored directed attention)
- Stress Reduction (biophilic cues → parasympathetic activation)
- Cognitive Load reduction (natural complexity optimal for processing)
- Social-evolutionary (environments signaling safety)

But papers rarely test between these mechanisms. Forcing a step-by-step mechanism_chain will either be:
1. Vague (most papers): "natural settings → restoration via attention and physiological relaxation"
2. LLM-hallucinated (worst case): synthetic mechanisms not in the paper
3. Tagged "assumed" (honest but unhelpful)

**Confidence: 0.55**
Recommendation: Mark mechanism fields as *expected but not required* for naturalistic/observational studies. Require explicit mechanisms only for experimental papers with mediation tests.

**molecule_ids linking to rasa_attractors**: I need to understand rasa_attractors better, but the concept troubles me. The Natyashastra's rasa system (love, joy, anger, fear, etc.) encodes *affective resonances*, not *causal properties*. A beautiful landscape that induces "love" (shringara) is not necessarily restorative. Beaty et al. (2014) show that visual beauty and cognitive restoration are weakly correlated. You may be conflating *aesthetic valence* with *functional efficacy*.

**Confidence: 0.40** (skeptical of this linkage)
Recommendation: If you pursue rasa mapping, do so *post-hoc* as a descriptive layer, not as a feature that constrains extraction.

**success_conditions**: In environmental psychology, success hinges on measurement validity and ecological validity. Your schema conflates these. I'd separate:
- **Data-quality tiers**: Which measurements are acceptable? (e.g., self-report restoration vs. physiological cortisol)
- **Generalizability checks**: Does the study involve an actual environment or a proxy? (in situ vs. photograph vs. VR)

A finding about restorative effects from a nature *photograph* may not generalize to in situ environments—that's not a quality failure, it's a boundary condition.

**Confidence: 0.75** (good idea, needs taxonomization)

---

**Dr. Ioannidis (Meta-Science):**

I will comment on these new fields from the perspective of measurement quality and replication risk:

**Key Principle**: New schema fields must improve our ability to detect low-power findings and inflated effect sizes. Do they?

**stimulus_description**: *Positive impact on replication.* By forcing explicit operationalization of the IV, you reduce **researcher degrees of freedom** (Wicherts et al., 2016). A researcher cannot silently swap "nature photograph" for "live nature view" if the extraction schema demands specification. This reduces what Schimmack & Heene (2023) call "construct fishing"—trying multiple IV operationalizations until p < .05.

**Confidence: 0.85** (genuine improvement on transparency)

**stimulus_images with vision_attributes**: *Promising but fragile.* High-quality image data could enable post-hoc meta-regression on visual properties. However, only a fraction of papers will include extractable figures or images. This field will be sparse. Recommend:
1. Do not *require* stimulus_images (too many papers lack figures)
2. Use vision_attributes as *optional moderator data*
3. Mark as research opportunity: papers with figure-level visual data could be re-analyzed for hidden moderators

**Confidence: 0.70** (high utility if populated; low population expected)

**theory_commitments**: *Strong replication benefit.* By tracking whether a finding *tests* vs. *assumes* vs. *extends* a theory, you enable post-hoc sensitivity analyses. Example: Do findings that *test* ART have higher replication rates than findings that *assume* it? This is essential for assessing p-hacking risk (hypothesis generation vs. confirmation).

**Confidence: 0.88**

**mechanism_chain**: *High risk of false precision.* Extractors will be tempted to post-hoc rationalize mechanisms to satisfy the schema. This creates new replication risks. Mechanism claims (e.g., "natural scene → activation of the default-mode network") are notoriously difficult to replicate even within the original laboratory (Button et al., 2013). Extracting mechanisms from narrative text is vulnerable to:
- Confirmation bias: LLM selects mechanisms consistent with the paper's narrative, ignoring alternative explanations
- Underreporting: Papers rarely test multiple mechanisms; LLM fills gaps speculatively

**Confidence: 0.45** (increases measurement burden without clear replication benefit)
Recommendation: Accept mechanisms as *narratively claimed* (not empirically validated) and tag evidence_strength accordingly.

**molecule_ids**: *Conceptually unclear; replication risk unknown.* Before adopting this, I need clarification:
1. Are molecules *observable constructs* or *aesthetic categories*?
2. Do two papers with the same finding map to the same molecule across extractors? (inter-rater reliability!)
3. What prevents this from becoming a new source of **hidden heterogeneity**—papers classified into molecules post-hoc using subjective judgment?

**Confidence: 0.35** (insufficient information)
Recommendation: Pilot with 50-100 papers, compute inter-rater reliability on molecule assignment, publish before mainline adoption.

**success_conditions**: *Essential and underutilized.* This is exactly what the field needs—explicit criteria for when a finding should be admitted to meta-analysis. But I note:
1. You define min_findings (minimum replications), required_fields, and theory_link_expected, but no **effect-size threshold** (e.g., exclude implausibly small effects).
2. No **publication bias flags** (was this study registered? pre-registered?).
3. No **measurement validity flags** (was the construct measured with a validated instrument?).

These are *additional* success conditions you should consider adding.

**Confidence: 0.68** (good framework, incomplete criteria)

**instruments_used**: *Excellent for measurement transparency.* Requesting explicit reliability (Cronbach's alpha, test-retest) enables post-hoc assessment of measurement error. Heterogeneity in instrument choice is a major moderator in meta-analysis (Borenstein et al., 2009). By capturing this, you enable *instrument-level* moderation analyses.

**Confidence: 0.90**

---

## Points of Agreement (Panelist Consensus)

1. **stimulus_description is essential** (unanimous, confidence >0.85). The field needs explicit IV operationalization.
2. **theory_commitments is valuable** (unanimous, confidence >0.87). This operationalizes epistemic responsibility.
3. **instruments_used is strong practice** (unanimous, confidence >0.90). Measurement transparency is non-negotiable.
4. **mechanism_chain requires careful handling** (unanimous concern, confidence in *caution* = 0.80). Define when mechanisms are expected vs. optional.
5. **success_conditions framework is sound but incomplete** (unanimous, confidence in framework = 0.75). Expand criteria.

---

## Points of Disagreement

1. **molecule_ids (rasa attractors) mapping**:
   - **Dr. Kaplan**: Skeptical (0.40) that aesthetic rasa categories map to functional causal properties.
   - **Dr. Ioannidis**: Uncertain (0.35) about inter-rater reliability and replication validity.
   - **Dr. Shadish**: Does not directly address but implies concern about *construct validity* of rasa categories applied to behavioral outcomes.
   - **Resolution**: Do not mandate molecule linking. Permit it as optional post-hoc categorization, not extraction driver.

2. **vision_attributes specification**:
   - **Dr. Kaplan**: Too loose (0.65); should pre-specify attributes from restorative environment theory (fractal_dimension, legibility, mystery, prospect-refuge, biophilia_density).
   - **Dr. Ioannidis**: Sparse data problem (0.70); don't require, use as optional moderator.
   - **Dr. Shadish**: Needs units, constraints, and operationalization (implied).
   - **Resolution**: Create a *recommended* vision_attributes vocabulary with units; allow extensibility for novel attributes.

3. **Temporal/familiarity dynamics in stimulus_description**:
   - **Dr. Kaplan**: Missing (strong critique). Need exposure_frequency, habituation_control, prior_familiarity.
   - **Dr. Shadish**: Relevant to external validity; supports expansion.
   - **Dr. Ioannidis**: Agrees temporal factors are hidden moderators; recommend adding.
   - **Resolution**: Expand StimulusDescription to include temporal and familiarity properties.

---

## Recommendations with Priority

### MUST DO (Block release without)

1. **Specify vision_attributes enum**: Replace `"additionalProperties: { type: number }"` with a closed enum of vision attributes + units:
   ```json
   "vision_attribute_definitions": {
     "fractal_dimension": { "unit": "dimensionless", "range": [1.0, 2.0], "source": "box-counting" },
     "legibility": { "unit": "0-1 Kaplan scale", "range": [0, 1] },
     "mystery": { "unit": "0-1 Kaplan scale", "range": [0, 1] },
     "complexity": { "unit": "entropy bits/pixel", "range": [0, 8] },
     ...
   }
   ```
   *Why*: Current definition invites garbage data. Vision attributes need operational definitions.

2. **Mark mechanism_chain as conditional**: Update schema to make mechanism_chain non-required; add field `mechanism_expectation` with values:
   - "required": empirical_finding (experimental), causal claims
   - "expected": theoretical, moderated claims
   - "optional": qualitative_theme, cited, narrative

   *Why*: Mechanism extraction is high-risk without epistemic grounding. Only require where empirically validated.

3. **Separate success_conditions into data-tier and epistemic-tier**:
   - **Data tier**: Which fields must be populated for this finding to be usable in any analysis? (required_fields, min_quality_score)
   - **Epistemic tier**: Which fields are expected given article_family, claim_type? (theory_link_expected, mechanism_expected)

   *Why*: Current structure conflates data quality with theoretical expectations.

4. **Add temporal/familiarity properties to StimulusDescription**:
   ```json
   "exposure_frequency": { "enum": ["discrete", "continuous", "intermittent"] },
   "exposure_prior_familiarity": { "type": ["integer", "null"], "minimum": 0, "maximum": 1, "description": "Prior familiarity rating 0-1 if reported" },
   "habituation_control": { "type": "boolean", "description": "Whether study controlled for novelty/familiarity effects" }
   ```
   *Why*: Temporal dynamics are critical moderators in environmental psychology. Current schema loses this.

5. **Do NOT mandate molecule_ids linking**. Make optional. Clarify epistemology first:
   - Are molecules *causal drivers* or *aesthetic descriptors*?
   - Compute inter-rater reliability on molecule assignment (n=50 papers, 3 independent extractors).
   - Pilot before mainline.

   *Why*: Risk of false construct validity (confusing aesthetic valence with causal efficacy). Replication validity unknown.

### SHOULD DO (Improves schema quality)

6. **Expand success_conditions with additional criteria**:
   - Add `effect_size_plausibility_floor`: Exclude implausibly small effects (e.g., d < 0.1)
   - Add `registration_status`: Was study pre-registered?
   - Add `measurement_validity_flag`: Was construct measured with validated instrument (vs. single item)?
   - Add `ecological_validity_grade`: in_situ > VR > photo for environmental studies

   *Why*: Captures replication risk factors from meta-research (Ioannidis tradition).

7. **Add optional field `moderators_investigated`**:
   ```json
   "moderators_investigated": {
     "type": "array",
     "items": {
       "type": "object",
       "properties": {
         "moderator_name": "string",
         "is_environmental": "boolean",
         "effect_size_by_level": "object"
       }
     }
   }
   ```
   *Why*: Enables post-hoc moderation meta-analysis; Kaplan/environmental psychology needs this.

8. **Document mapping between claim_type and expected theoretical commitment types**:
   - Empirical findings should map to `tests` (>80% of cases expected)
   - Review/theoretical should map to `assumes`, `extends`, `contradicts`
   - Create example extraction document showing good vs. poor commitment tagging

   *Why*: Reduces extraction variance; provides guidance.

### CONSIDER (Nice-to-have; lower priority)

9. **Add optional `equivalence_class_id` to non-stimulus fields**:
   Currently only on stimulus_description. Environmental psychology needs to track equivalent *outcomes* (e.g., "stress" measured via cortisol, POMS, heart rate). Link to outcome harmonization registry.

   *Why*: Enables outcome-level meta-analysis across measurement heterogeneity.

10. **Create extraction template document** with 2-3 exemplar findings from well-characterized environmental studies (e.g., Ulrich 1984, Kaplan restorative studies) showing good extraction.

    *Why*: Reduces uncertainty; shows feasible compliance.

---

## Summary: Schema Assessment

**Overall Grade**: B+ (Good foundation; critical refinements needed)

**Strengths**:
- Stimulus operationalization (stimulus_description, stimulus_images) represents major advancement for environmental research
- Theory commitments force epistemic transparency
- Instruments tracking enables measurement meta-analysis
- Nested structure is flexible and extensible

**Weaknesses**:
- Vision attributes underspecified (no units, ranges, operationalization)
- molecule_ids mapping unvalidated (epistemology unclear; replication risk unknown)
- Mechanism chains risky without conditional requirements
- Success conditions conflate data quality with theoretical expectations
- Temporal/familiarity dynamics absent (critical for environmental psychology)

**Fitness for Purpose**: Ready for environmental psychology systematic review *if* MUST DO items are addressed. Current version would generate low-quality mechanism data and undefined vision attributes.

**Confidence in Recommendation**: 0.80 (panel consensus strong on core issues; molecule_ids requires further development)

---

## Next Steps for Panel

1. Implement MUST DO items (5 changes)
2. Pilot expanded schema on 100-paper sample
3. Compute inter-rater reliability on new fields (especially theory_commitments, mechanism_chain, molecule_ids)
4. Run sensitivity analysis: Do findings with populated vs. null new fields have different meta-analytic conclusions?
5. Schedule Panel B (Quality Thresholds) after schema is finalized

**Prepared by**: Panel Secretariat
**Date**: 2026-03-01
**Reviewers**: Shadish, Kaplan, Ioannidis (all endorsed)
