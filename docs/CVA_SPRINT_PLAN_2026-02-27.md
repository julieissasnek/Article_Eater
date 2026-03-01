# CVA Sprint Plan: Implementation of Constraint–Valuation Architecture

**Date**: February 27, 2026
**Based on**: Expert Panel CVA Formal Review (12 panelists, 5 deliberation rounds)
**Decision Basis**: 10 ADOPT PARTIALLY, 2 DEFER, 0 FULL, 0 REJECT
**Plan Horizon**: 9 sequential sprints across 4 phases, ~20–24 weeks
**Status**: DRAFT — Ready for David's review and panel steering

---

## EXECUTIVE SUMMARY

The expert panel has endorsed CVA as an architectural addition to ATLAS under seven mandatory conditions:

1. **Analytical, not causal**: Constraint–valuation separation is analytical, not ontological. Feedback loops permitted.
2. **Explicit dynamics**: System F (constraints) and G (valuations) must be formally specified with stability proofs.
3. **Identifiability validated**: Empirical tests must demonstrate constraints and valuations can be independently manipulated and measured.
4. **Cultural contingency**: Valuation structure varies by culture; not just weights. Build in structural variation from Sprint CVA-2.
5. **Incremental adoption**: Pilot 20-template reclassification before full 208. Create no-go decision gate.
6. **Design thinking grounded**: Use as architectural thinking tool (Zumthor), not just prediction engine.
7. **Minority concerns tracked**: Monitor whether technical debt is accumulating (Strogatz), structural cultural variance is real (Barrett), and design utility is evident (Zumthor).

This plan breaks CVA adoption into four phases:

- **Phase A (Sprints CVA-1 to CVA-3)**: Foundation. Build constraint and valuation registries, activity frame module, without touching existing ATLAS templates.
- **Phase B (Sprints CVA-4 to CVA-6)**: Pilot validation. Reclassify 20 templates, extend projection function, test compression models.
- **Phase C (Sprints CVA-7 to CVA-8)**: Empirical design. Pre-register identifiability experiments and cross-cultural validation.
- **Phase D (Sprint CVA-9)**: Integration and decision. Update Master Document, run second panel, make GO/NO-GO for full 208-template adoption.

---

## PHASE A: FOUNDATION (Sprints CVA-1 to CVA-3)

### Dependencies and Prerequisites

CVA sprints are **independent from existing ATLAS sprint plan** (Sprints 0–8). They do not modify core ATLAS code, templates, or Master Document until Phase D. This allows parallel development.

- **Prerequisite**: No code changes required. New modules only.
- **Input data**: White Paper classification table (20 template examples) + existing ATLAS feature ontology.
- **Output**: Three new infrastructure modules + documentation for panel review.

---

### Sprint CVA-1: Constraint Variable Registry (2 weeks)

**Objective**: Operationalize the eight constraint variables with measurement protocols, data sources, and integration points to existing ATLAS measures.

**Background**: The panel emphasized Ruth Dalton's concern: constraints must be context-sensitive operational definitions, not abstract quantities. Constraints are what can be *measured* about the environment; they are not objective ground truth but inter-subjective constructs that describe the space in terms relevant to human perception and action.

**Key Tasks**:

1. **Define eight constraints formally**:
   - **ProcessingCost**: Computational burden of perceiving and interpreting the environment. Measure via: entropy of feature distribution (from visibility graphs, material diversity, color distribution). Units: bits/feature or normalized 0–1.
   - **LoadRate**: Temporal density of relevant events or changes. Measure via: motion events per second (eye-tracking), sound events per minute, visual transience (flicker, change detection). Units: events/second.
   - **PredictionError**: Variance between expected and actual sensory input. Measure via: entropy of salient features, deviation from statistical regularity, surprisal per feature. Units: bits/event.
   - **ControlEfficacy**: Affordance clarity—how readily can a person perceive actionable pathways? Measure via: visibility graph metrics (node accessibility, path distribution), wayfinding time, signage clarity. Units: graph connectivity (0–1) or trial-and-error steps.
   - **AffordanceDensity**: Quantity of perceptually salient action possibilities. Measure via: count of morphological breaks, access points, interactive surfaces; entropy of feature granularity. Units: affordances/m² or normalized 0–1.
   - **SocialCueDensity**: Presence of social information (people, portraits, activity indicators). Measure via: person count, occupancy signals, social signage density. Units: social cues/area or presence/absence flags.
   - **MultisensoryCoherence**: Alignment of information across sensory modalities (sight, sound, touch, proprioception). Measure via: cross-modal entropy reduction (how much does hearing a sound reduce visual uncertainty?), modality agreement scores. Units: coherence index 0–1.
   - **NarrativeCoherence**: Consistency of spatial storytelling (form, program, material, symbolic meaning). Measure via: thematic consistency score (rated by trained panel), program-form alignment, material continuity. Units: score 0–1 or narrative theme tags.

2. **Map to existing ATLAS measures**:
   - Visibility graph architecture (Dalton) → **ControlEfficacy**
   - Entropy measures in current feature space → **ProcessingCost**, **PredictionError**
   - Room-use patterns (occupancy, flow) → **LoadRate**, **AffordanceDensity**
   - Create integration function `constraints_from_atlas_features(feature_vector) → constraint_vector`.

3. **Create constraint_variables.py**:
   - Data class for Constraint (name, definition, measurement_protocol, units, data_source, aliases).
   - Registry class: `ConstraintRegistry` with 8 registered constraints.
   - Measurement functions for each constraint (stubs + reference implementations for ProcessingCost, ControlEfficacy).
   - Integration interface to existing ATLAS feature extraction (`extract_constraint_vector(atlas_features) → ConstraintVector`).

4. **Document measurement protocols**:
   - For each constraint, specify: (a) operational definition, (b) measurement instruments/algorithms, (c) data requirements, (d) validation approach, (e) known limitations (Ruth Dalton caveat: context sensitivity).
   - Flag constraints that require subjective judgment (e.g., NarrativeCoherence) and specify inter-rater protocols.

5. **Address panel concerns**:
   - **Dalton's context-sensitivity concern**: Document that all measures are relative to activity frame and observer state. Include examples of how the same spatial feature produces different constraint values under different frames.
   - **Friston's precision-weighting note**: For each constraint, estimate measurement noise and precision (will be used in later phases for dynamic weighting).

**Deliverables**:

- `src/services/cva/constraint_variables.py` (250 lines) — Registry, data classes, measurement stubs.
- `docs/CVA_CONSTRAINT_VARIABLE_REGISTRY.md` (500–800 lines) — Full specifications for all 8 constraints with examples.
- `src/services/cva/constraint_atlas_integration.py` (150 lines) — Functions to extract constraint vectors from existing ATLAS features.
- Test file: `tests/cva/test_constraint_variables.py` (100 lines) — Basic instantiation and registry lookup tests.

**Risks**:

- **Measurement operationalization ambiguity**: Some constraints (especially NarrativeCoherence) may resist algorithmic measurement. Mitigation: Mark as requiring expert annotation in pilot phase; plan for semi-supervised learning in Phase B.
- **Data availability**: Some constraints require new data collection (e.g., eye-tracking for LoadRate). Mitigation: Use proxy measures for pilot (e.g., visual complexity metrics as LoadRate proxy); identify data collection needs for Phase C studies.
- **Constraint correlation**: Some constraints may be highly correlated (e.g., ProcessingCost and PredictionError). Mitigation: Document correlations in registry; test orthogonality empirically in Phase B.

**Dependencies**:

- Existing ATLAS feature extraction pipeline must be available for reading.
- White Paper classification table (20 templates) should be reviewed for constraint applicability.

**Estimated Effort**:

- David: 1.5 days (review/guidance on spatial measures, constraint definitions)
- Claude (Code + AI systems): 8 days (registry design, measurement functions, documentation, testing)
- Panel review (async): 2 days (Dalton on operationalization, Friston on measurement noise model)
- **Total**: ~11.5 person-days

---

### Sprint CVA-2: Valuation Axes Schema (2 weeks)

**Objective**: Formally define nine valuation axes with measurement instruments, neural correlate hypotheses, SDT interactions, and cultural variation structure.

**Background**: The panel was clear: valuation axes are not discovered universals. They are theoretical proposals that must be culturally and contextually validated. Barrett and Kitayama both emphasized that axis *structure* varies by culture, not just weights. Deci emphasized that the SDT axes (Autonomy, Competence, Relatedness) are interactive, not independent.

**Key Tasks**:

1. **Define nine valuation axes with formal specifications**:

   - **SafetyValue** (ζ₁): Preference for environmental predictability, low threat, low ambiguity. Measure via: threat questionnaire (Jackson & Deci's threat-appraisal scale), physiological threat markers (HR, cortisol). Neural: amygdala, anterior insula. Interactions: reduces with high ControlEfficacy (constraints help disarm threat).

   - **Esthetic/Mastery Value** (ζ₂): Preference for coherence, beauty, technical excellence. Measure via: aesthetic judgment tasks, beauty rating scales (Chatterjee). Neural: anterior insula, anterior cingulate (processing fluency). Interactions: rises with ProcessingCost moderate range, falls at extremes (inverted-U).

   - **AutonomySupportValue** (ζ₃): Preference for volition, choice, self-determination. Measure via: self-determination questionnaire (Deci), choice availability, perceived volition. Neural: ventromedial prefrontal cortex (vmPFC), reward circuits. Interactions: **not independent**—scales with RelatednessSupportValue (autonomy within community), modulated by cultural individualism.

   - **CompetenceSupportValue** (ζ₄): Preference for appropriate challenge, mastery opportunity, skill-building. Measure via: task-demand matched to skill (Csikszentmihalyi flow), mastery opportunity rating. Neural: dorsolateral prefrontal cortex (dPFC), posterior parietal cortex (action planning). Interactions: modulated by LoadRate (challenge increases when load is parseable).

   - **RelatednessSupportValue** (ζ₅): Preference for community, belonging, social connection. Measure via: social connection scale (UCLA Loneliness), presence of others, social cue resonance. Neural: temporoparietal junction (TPJ), mentalizing circuits. Interactions: **not independent**—modulates interpretation of all other axes (what is mastery in isolation is failure if socially devalued).

   - **BelongingValue** (ζ₆): Specific sense of "fitting in," group membership, shared identity. Measure via: belonging scale (Walton & Cohen), in-group/out-group markers, reference group salience. Neural: evidence emerging (Eisenberger note: not yet independent from vmPFC value). Interactions: culture-dependent weight; collectivist cultures weight heavily, individualist cultures weight lower but remain present.

   - **StatusValue/IdentityCongruenceValue** (ζ₇): Preference for signals congruent with self-concept and social position; avoidance of status incongruence. Measure via: identity congruence questionnaire, self-concept–environment fit, social comparison. Neural: medial prefrontal cortex (mPFC) self-reference, posterior cingulate (social hierarchy). Interactions: modulated by SocialCueDensity (status cues visible); culture-modulated (status less salient in egalitarian cultures).

   - **EnviroNarrativeAlignment** (ζ₈): Preference for spaces that tell coherent stories, have symbolic depth, and align with conceptual frameworks. Measure via: narrative comprehension, thematic resonance rating, cultural symbol recognition. Neural: language networks, default mode network (conceptual processing). Interactions: culture-specific (symbols are culture-local); depends on NarrativeCoherence (constraints).

   - **NoveltyValue/InformationalValue** (ζ₉): Preference for variation, discovery, learning, information gain. Measure via: novelty-seeking scale, information-sampling behavior, exploration rate. Neural: ventral striatum (reward to novelty), anterior cingulate (information value). Interactions: inverted-U with PredictionError (moderate surprise preferred; high surprisal aversive). Note: Berlyne's formulation; Goldilocks Principle in T1.5 provides subsumption.

2. **Specify interaction matrix** (Deci + Kitayama requirement):
   - Create 9×9 matrix showing how axes modulate one another.
   - Mark which are **conditionally independent** (can be manipulated separately) vs. **interactive** (must co-vary).
   - Example: AutonomySupportValue and RelatednessSupportValue are interactive; you cannot maximize autonomy while minimizing relatedness in most cultural contexts without generating stress.

3. **Build cultural variation structure** (Barrett + Kitayama requirement):
   - Rather than single universal valuation vector, allow *cultural instances*.
   - Each cultural instance specifies:
     - Which axes are salient (present/absent, or weighted near-zero).
     - Interaction matrix (culturally specific).
     - Measurement instruments (adapted for cultural validity).
   - Example: Individualist-West cultural instance weights AutonomySupportValue heavily; collectivist-East instance weights RelatednessSupportValue heavily and makes the interaction matrix different.
   - Create `CulturalValuationInstance` class to represent this.

4. **Create valuation_axes.py**:
   - Data class for ValuationAxis (name, definition, measurement_instruments, neural_hypothesis, interaction_partners, cultural_variants).
   - ValuationRegistry with 9 axes.
   - `CulturalValuationInstance`: defines which axes are active, interaction matrix, measurement modifications.
   - Function: `compute_valuation_vector(measurement_data, cultural_instance) → ζ_vector`.
   - Interaction function: `apply_interaction_effects(ζ_vector, interaction_matrix) → adjusted_ζ_vector`.

5. **Address panel concerns**:
   - **Barrett's cultural construction caveat**: Note in documentation that axes are not discovered facts; they are analytical frameworks. Their salience and structure are culturally constructed. Add a section on why existing psychology conflates universal *functions* (needs for safety, belonging) with universal *dimensions* (the specific way those needs structure preference).
   - **Deci's interaction requirement**: Provide worked examples of how to compute interaction effects for autonomous competence-building in relatedness context (the SDT sweet spot).
   - **Leary's social-hierarchy concern**: StatusValue section explicitly models reference-group membership and social positioning. Include examples of how status signals change meaning across contexts (scientist in lab vs. scientist at cocktail party).

6. **Neural hypothesis framework** (Eisenberger, Friston):
   - For each axis, specify the neural hypothesis (region + function) and confidence level (high/medium/low).
   - Flag axes with uncertain neural correlates (e.g., BelongingValue), to be tested in Phase C.
   - Include note on dynamic neural coupling (Friston): these regions do not operate independently; they show functional integration that may underlie the interaction effects.

**Deliverables**:

- `src/services/cva/valuation_axes.py` (400 lines) — Axis definitions, registry, interaction matrix, cultural instances, computation functions.
- `docs/CVA_VALUATION_AXES_SPECIFICATION.md` (800–1000 lines) — Formal specification for all 9 axes, interaction matrix, cultural variants, neural hypotheses.
- `docs/CVA_CULTURAL_VARIATION_FRAMEWORK.md` (300–400 lines) — Explanation of why axes are culturally contingent and how to instantiate the model for a new culture.
- `src/services/cva/cultural_instances.py` (200 lines) — Instantiated cultural instances (Individualist-West, Collectivist-East, TBA placeholder for additional cultures).
- Test file: `tests/cva/test_valuation_axes.py` (150 lines) — Instantiation, interaction effects, cultural instance switching.

**Risks**:

- **Measurement ambiguity**: Some axes lack established measurement instruments (e.g., EnviroNarrativeAlignment, BelongingValue). Mitigation: Mark as requiring expert annotation or development in Phase B; identify collaborators for cultural adaptation.
- **Cultural overfitting**: Different cultures may have entirely different dimensional structures. Mitigation: This sprint creates the *infrastructure* for cultural variation; actual validation comes in Phase C.
- **Neural hypothesis uncertainty**: Some neural hypotheses may be wrong or change as neuroscience evolves. Mitigation: Mark confidence levels; make neural hypotheses falsifiable and updatable.
- **Interaction explosion**: 9×9 interaction matrix is complex; estimating all interactions may be infeasible. Mitigation: Focus first on theoretically-grounded interactions (Deci's SDT triad, Friston's precision-weighting). Treat others as "TBD" and refine empirically.

**Dependencies**:

- Existing SDT literature (Deci & Ryan) for autonomy/competence/relatedness definitions.
- Emotion science literature (Barrett, Scherer) for emotion-dimension validation.
- Neuroscience literature for neural hypotheses (Eisenberger on belonging, Leary on social-status circuits).

**Estimated Effort**:

- David: 2 days (review cultural variation architecture, interaction matrix, neural hypotheses)
- Panel consultation (async): Deci (SDT interactions), Barrett/Kitayama (cultural variation), Eisenberger (neural hypotheses) — ~3 days distributed
- Claude (Code + AI systems): 10 days (axis definitions, interaction functions, cultural instances, documentation)
- **Total**: ~15 person-days

---

### Sprint CVA-3: ActivityFrame Implementation (2 weeks)

**Objective**: Formalize ActivityFrame as a structuring principle that modulates goal activation, valuation weights, and constraint salience.

**Background**: The panel (especially Deci and Ulrich) emphasized that the same physical constraints produce different responses under different activity frames. An ActivityFrame is a top-level goal or context that determines which valuations are active and how constraints are weighted. Friston framed this as "active policy expectation"—the frame specifies which policies (goal-guided behaviors) are expected to apply.

**Key Tasks**:

1. **Define ActivityFrame formally**:
   - ActivityFrame = (name, primary_goals, valuation_weights, constraint_relevance_mask)
   - Example: ActivityFrame("hospital_recovery") with goals=[SafetyValue, CompetenceSupportValue], weights=[0.8, 0.6, 0.3, 0.3, 0.7, 0, 0.3, 0, 0.1], constraint_mask=[1, 0.5, 1, 1, 0.3, 0, 0.8, 1, 0].
   - The mask indicates which constraints are perceptually salient under that frame. In recovery, ProcessingCost and PredictionError (stress from unexpected events) are salient; AffordanceDensity (action opportunities) is less relevant; SocialCueDensity is zero (isolation for infection control).

2. **Create ActivityFrame registry** with canonical frames:
   - Hospital recovery (healing-focused, safety-dominant)
   - Office work (productivity, focus, autonomy support)
   - Social gathering (belonging, status, relatedness)
   - Yoga/meditation (internal awareness, autonomy, EnviroNarrativeAlignment)
   - Museum/gallery visiting (learning, novelty, EnviroNarrativeAlignment)
   - Home living (autonomy, competence, belonging, identity congruence)
   - Retail shopping (agency, novelty, status)
   - Sacred space (narrative alignment, belonging, reverence—requires special axis weighting)

   For each frame, specify: (a) primary goals, (b) valuation weight vector ζ, (c) constraint salience mask σ, (d) context examples, (e) typical duration (is this a 30-minute frame or multi-hour?).

3. **Implement frame-dependent goal activation** (Deci's insight):
   - Different frames activate different subsets of needs/goals.
   - Implement as: `active_goals = frames[frame_name].primary_goals`
   - When computing overall valuation, only active goals contribute.
   - This is different from reweighting: if an axis is not in the active-goals set, it contributes zero to the final policy, not a small positive value.
   - Implement function: `compute_frame_adjusted_valuation(ζ_vector, frame, constraint_vector) → adjusted_ζ`.

4. **Implement frame-dependent constraint salience** (Ulrich's evidence):
   - Same spatial feature (e.g., visual complexity) has different effects under different frames.
   - In recovery frame, complexity is stress-inducing (high ProcessingCost is bad).
   - In creative studio frame, complexity is stimulating (moderate ProcessingCost is good).
   - Implement constraint salience mask σ such that: `constraint_contribution_to_valuation = σ ⊙ c` (element-wise multiply constraint vector by mask).
   - Document examples: hospital vs. creative studio, same room physical layout, opposite constraints inferred by frame.

5. **Create activity_frame.py**:
   - Data class: ActivityFrame (name, description, primary_goal_ids, valuation_weights_base, constraint_salience_mask, context_examples, typical_duration_minutes).
   - ActivityFrameRegistry: 8 canonical frames (above) + extensible interface for custom frames.
   - Computation functions:
     - `activate_frame(frame_name, constraint_vector, base_ζ) → active_ζ_vector` — Apply frame weights and goal activation.
     - `frame_matches_context(frame_name, contextual_cues) → confidence_score` — Infer which frame applies from context.
   - Integration with constraint registry: `validate_frame_constraints(frame_name, available_constraint_variables) → missing_constraints`.

6. **Create worked examples** (3–5 concrete cases):
   - **Example 1**: Hospital room. Same room. Recovery frame: SafetyValue weights high, PredictionError is salient, AffordanceDensity is masked (disabled bed = zero affordances is safe). Visitor frame: Relatedness weights high, constraint salience different (AffordanceDensity may be positive—room for movement with patient).
   - **Example 2**: Creative studio. Same room. Creative work frame: NoveltyValue high, ProcessingCost moderate-to-high is preferred. Administrative frame: ProcessingCost low preferred, NoveltyValue masked.
   - **Example 3**: Museum gallery. Two galleries with similar architecture. Art appreciation frame activates EnviroNarrativeAlignment, NoveltyValue, processing cost high okay. School group frame: safety, group cohesion, manageable cognitive load.
   - **Example 4**: Home office. Autonomy-support frame (freelancer) vs. control frame (regulated employment). Same desk, different constraint salience: autonomy supporter wants high AffordanceDensity (equipment choices); control-frame worker wants low ProcessingCost (minimized distraction).
   - **Example 5**: Yoga studio. Meditation frame (internal focus): SafetyValue high, SocialCueDensity masked (ignore others). Social frame (community yoga): Relatedness high, SocialCueDensity salient.

7. **Friston's active-inference interpretation**:
   - Frame = policy expectation. Friston would say: ActivityFrame specifies a generative model where the environment is expected to support a particular set of policies (goals).
   - Precision-weight the constraints accordingly: constraints relevant to frame policies are high-precision (trusted); irrelevant constraints are low-precision (ignored).
   - Document this in a section: "ActivityFrame as Active Policy Expectation (Friston)."

**Deliverables**:

- `src/services/cva/activity_frame.py` (350 lines) — Frame definitions, registry, computation functions, frame inference.
- `docs/CVA_ACTIVITY_FRAME_SPECIFICATION.md` (600–800 lines) — Frame definitions, worked examples (5 cases), frame-dependent constraint salience, Friston interpretation.
- `tests/cva/test_activity_frame.py` (150 lines) — Frame instantiation, computation of adjusted valuation, frame matching.
- Visualization (optional PNG/SVG): Frame weight matrices for 2–3 example frames, constraint salience masks.

**Risks**:

- **Frame ambiguity**: Unclear how to infer which frame applies in real-time. Mitigation: Sprint CVA-4 (pilot) will test frame inference against real template classification.
- **Frame proliferation**: May end up with dozens of frames, each with hand-specified weights. Mitigation: Focus pilot on 8 canonical frames; plan for learning frame structures from data in Phase B/C.
- **Interaction with cultural variation**: Frames may vary by culture (e.g., status frame more salient in hierarchical cultures). Mitigation: Allow CulturalValuationInstance to override frame weights; test empirically in Phase C.

**Dependencies**:

- Completed Sprint CVA-2 (valuation axes defined).
- Completed Sprint CVA-1 (constraints defined).

**Estimated Effort**:

- David: 1 day (review activity frame concept, worked examples, integration)
- Claude (Code + AI systems): 8 days (frame registry, computation functions, worked examples, testing)
- Panel consultation (async): Deci (goal activation), Friston (active inference interpretation) — ~1 day
- **Total**: ~10 person-days

---

## PHASE B: PILOT VALIDATION (Sprints CVA-4 to CVA-6)

### Dependencies and Prerequisites

- All of Phase A complete (registries, axes, frames defined in code).
- White Paper classification table (20 templates) available for annotation.
- Existing ATLAS templates and feature vectors accessible.

---

### Sprint CVA-4: 20-Template Pilot Reclassification (3 weeks)

**Objective**: Take the 20 templates from the White Paper classification table; reclassify each under CVA; document where reclassification is clean vs. where it requires conceptual work; identify gaps and contradictions.

**Background**: The panel's condition was explicit: do not attempt full 208-template reclassification without pilot validation. Pilot on 20 carefully selected templates from the White Paper. Jordan's criterion: can constraints and valuations be independently manipulated? If yes, the separation is real. Ulrich's criterion: can you cross-context predict? If a template reclassified on office data predicts hospital behavior, the model transfers.

**Key Tasks**:

1. **Select and prepare 20 templates**:
   - Use the 20 templates from White Paper classification table (these should already be well-documented).
   - For each template, assemble: original rule statement, calibrated tier, confidence, white-paper classification, context examples (if any).
   - Create a spreadsheet with these 20 rows (to be annotated in parallel).

2. **Develop CVA annotation format**:
   - Extend existing ae.rule.v2 schema to include CVA metadata:
     ```yaml
     cva_annotation:
       constraints_primary: [list of primary constraint variables]
       constraints_secondary: [list of secondary/modulatory constraints]
       constraint_operationalizations: {constraint_name: "how this constraint manifests in this rule"}
       valuations_primary: [list of primary valuation axes]
       valuations_secondary: [list of modulating axes]
       valuation_vector: [optional: quantified weights if available]
       activity_frames: [list of frames under which this rule applies]
       frame_dependence: {frame_name: "how does this rule change under this frame?"}
       cross_context_hypotheses: [predictions for how rule applies in different contexts]
       identifiability_assumptions: ["can constraints be held constant while varying valuations?", ...]
       gaps_and_uncertainties: [things we don't understand about this template]
     ```

3. **Annotate 20 templates**:
   - For each template:
     - Identify primary constraint variable(s). Example: A template about openness to light → ControlEfficacy, ProcessingCost.
     - Identify primary valuation axis/axes. Example: Same openness template → SafetyValue (predictability of light sources), EstheticValue (beauty of natural light), NoveltyValue (variation in daylight).
     - Map to activity frames. Does this rule apply equally in recovery (safety frame) vs. creative work (novelty frame)? How does the weight shift?
     - Document where classification is clean (easy mapping) vs. ambiguous (multiple valid interpretations).
     - For ambiguous cases, note why (e.g., "Same rule applies in two frames but with opposite valuation drivers").
     - Identify missing constraints or valuations that the template seems to invoke but are not yet in the registry.

4. **Jordan's identifiability criterion**:
   - For each template, ask: Can we independently vary constraints vs. valuations?
   - Example: A template about colors (saturation) maps to ProcessingCost and EstheticValue. Can we:
     - Hold EstheticValue constant (same preference), vary saturation perception (ProcessingCost)? Prediction: if saturation is the only constraint, no aesthetic change. Result: identifiable.
     - Hold ProcessingCost constant, vary cultural EstheticValue? Prediction: saturation unchanged, aesthetic rating differs. Result: identifiable.
   - For each template, document whether this test is feasible and what manipulations it would require.

5. **Create pilot gap report**:
   - For each of the 20 templates, a one-paragraph summary: constraint mapping, valuation mapping, frames, identifiability feasibility.
   - Section: "Ambiguous mappings" — templates where CVA classification is unclear.
   - Section: "Missing constraints/valuations" — axes or constraints needed for this template set that are not yet in registries.
   - Section: "Cross-context predictions" — hypotheses about how each rule generalizes to hospital, office, home contexts.
   - Section: "Frame dependencies" — do the 20 rules weight frames equally, or do some apply only under specific frames?

6. **Format: CVA-annotated template format** (new file in codebase):
   - Create template JSON/YAML spec for storing these annotations.
   - Implement parser: `load_cva_annotations(template_id) → CVAAnnotation`.
   - Store in `data/templates/cva_annotations/` directory (parallel to existing template store).

7. **Quality assurance**:
   - Panel review (async): 2–3 panelists (Ulrich, Dalton, Friston) review 5 annotations each for consistency.
   - Inter-rater check: If two team members annotate the same 3 templates independently, compare. Target: >80% agreement on primary constraint/valuation assignment.

**Deliverables**:

- `data/templates/cva_annotations/` directory with 20 JSON files (one per template).
- `docs/CVA_PILOT_ANNOTATION_REGISTRY.md` (400–600 lines) — Summary table of all 20 annotations, with constraint and valuation assignments.
- `docs/CVA_PILOT_GAP_REPORT.md` (800–1000 lines) — Detailed analysis of ambiguities, missing axes, cross-context predictions, frame dependencies.
- `src/services/cva/template_annotation_parser.py` (150 lines) — Parser for CVA annotation files, validation functions.
- Test file: `tests/cva/test_template_annotations.py` (100 lines) — Parser tests, annotation validation.

**Risks**:

- **Annotation disagreement**: Different annotators may classify the same template differently. Mitigation: Inter-rater protocol; resolve disagreements by discussion or panel arbitration.
- **Missing conceptual framework**: The 20 templates may require constraints or valuations not yet in the registries. Mitigation: Document gaps; loop back to CVA-1/CVA-2 to extend registries if needed (may extend timeline by 1 week).
- **Frame ambiguity**: Unclear which frames apply to each template. Mitigation: Ulrich and Deci provide expert guidance on frame assignments during panel review.

**Dependencies**:

- Phase A complete (registries defined).
- White Paper classification table available.
- Existing ATLAS template database accessible.

**Estimated Effort**:

- David: 1.5 days (review gap report, guide annotation ambiguities)
- Claude (Code + AI systems): 10 days (annotation schema design, 20 annotations, gap report, parser, testing)
- Panel review (async): 2–3 days (5 annotations each from Ulrich, Dalton, Friston)
- **Total**: ~15 person-days

---

### Sprint CVA-5: Goal-Modulated Projection Function (2 weeks)

**Objective**: Extend the epistemic projection calculus to incorporate goal and frame modulation; implement as parallel system alongside existing projection; compare predictive accuracy.

**Background**: The panel (especially Friston, Jordan) emphasized that the goal is not to replace existing ATLAS projection but to augment it with goal-dependent weighting. Friston's minimal change: add a goal-dependent discount factor d(τ, goal) that modulates the existing projection formula.

**Key Tasks**:

1. **Extend projection calculus**:
   - Current ATLAS: `logit(p_target) = d · ω · logit(p_lab)`
   - Extended CVA: `logit(p_target) = d(τ, goal, frame) · ω · logit(p_lab)`
   - Where d(τ, goal, frame) is a discount factor that depends on:
     - τ = warrant type (existing)
     - goal = primary goal(s) activated by the activity frame
     - frame = activity frame
   - Implementation: `d = d_base(τ) · d_goal(goal) · d_frame(frame)`
   - Where each factor is between 0 and 1, and the product allows the goal/frame to down-weight the baseline discount.

2. **Specify d_goal and d_frame functions**:
   - `d_goal(goal_vector, warrant_type) → discount_adjustment` — Function that takes the set of active goals and returns a multiplier to d_base based on goal-warrant alignment.
   - Example: If goal is SafetyValue and warrant is AUTHORITY (expert says it's safe), then d_goal = 1.0 (full weight). If goal is NoveltyValue and warrant is AUTHORITY, then d_goal = 0.7 (authority is less relevant to novelty-seeking; you discount the expert advice).
   - `d_frame(frame_name, warrant_type, constraint_vector) → discount_adjustment` — Frame-specific adjustment. Example: In recovery frame (hospital), ANALOGY warrants are down-weighted because the frame is safety-focused, and analogies can transfer incorrectly across contexts. d_frame(recovery, ANALOGY, constraints) = 0.5.

3. **Implement alongside existing projection**:
   - Create `epistemic_projection_cva.py` (not replacing existing `epistemic_projection.py`).
   - Implement three projection functions:
     - `project_baseline(p_lab, warrant_type, d_base, ω) → p_target` — Current ATLAS projection.
     - `project_goal_modulated(p_lab, warrant_type, goal_vector, frame, constraint_vector, d_base, ω) → p_target` — CVA-extended projection.
     - `project_comparison(p_lab, warrant_type, d_base, ω, goals, frame, constraints) → {baseline: p1, goal_modulated: p2, difference: p2-p1}` — For side-by-side comparison.

4. **Implement multi-edge aggregation** (log-odds sum):
   - When multiple warrants feed into a single belief, combine via log-odds sum.
   - Baseline: `logit(p_combined) = Σᵢ dᵢ · ωᵢ · logit(pᵢ)`
   - CVA-extended: `logit(p_combined) = Σᵢ dᵢ(goal, frame) · ωᵢ · logit(pᵢ)`
   - Implement `aggregate_projections_goal_modulated(warrants_with_goals_frames) → p_combined`.

5. **Implement path composition** (for entailment chains):
   - When a belief depends on another belief (entailment), compose discounts via min().
   - Path: B1 --[ENTAILMENT, d₁]--> B2 --[DIRECT_OBSERVATION, d₂]--> B3
   - Effective discount to B3 through B1: d_effective = d₁ · d₂ · ... (multiplicative, or min() if using path-wise composition).
   - Implement `compose_path_discounts(path) → min(d_i) or product(d_i)` — panel to decide multiplicative vs. min.

6. **Create goal-warrant alignment matrix**:
   - 9 valuations × 13 warrant types = 117-cell matrix specifying d_goal for each pair.
   - Example cells:
     - SafetyValue + AUTHORITY = 0.95 (experts give safety advice credibly)
     - SafetyValue + ANALOGY = 0.6 (analogies can fail in novel contexts; be cautious)
     - NoveltyValue + ANALOGY = 0.85 (analogies help understand novel situations)
     - EstheticValue + TESTIMONY = 0.4 (beauty is subjective; testimony less reliable)
     - EstheticValue + PHENOMENOLOGICAL_OBSERVATION = 0.95 (direct aesthetic observation is reliable)
   - Document sources for these values (expert judgment + empirical data from calibration if available).

7. **Test against held-out templates**:
   - Split 20 pilot templates into train (15) and test (5).
   - Train: Fit goal-modulation parameters (if any free parameters) using the 15 templates.
   - Test: Compare baseline vs. goal-modulated prediction on held-out 5.
   - Metric: Accuracy, log-loss, or similar.
   - Expected outcome: goal-modulated should be comparable or better (likely not dramatically better on this small test set; real test comes in Phase C).

8. **Address panel concerns**:
   - **Jordan's caution**: "Don't claim this is truly causal." Document clearly that this is post-hoc weighting of an analytical decomposition. No claim that goals *cause* the discount; rather, goals are useful for modeling the discount.
   - **Friston's precision-weighting note**: Interpret d_goal and d_frame as precision weights in a Bayesian model: high precision → trust the evidence; low precision → be skeptical. Document this interpretation.

**Deliverables**:

- `src/services/cva/epistemic_projection_cva.py` (400 lines) — Goal-modulated projection, multi-edge aggregation, path composition.
- `docs/CVA_PROJECTION_EXTENSION_SPECIFICATION.md` (400–500 lines) — Extended formula, d_goal and d_frame functions, goal-warrant alignment matrix.
- `data/cva/goal_warrant_alignment_matrix.json` (117-cell matrix with sources and confidence levels).
- Test file: `tests/cva/test_projection_cva.py` (150 lines) — Multi-edge aggregation, path composition, held-out template comparison.
- Results: `docs/CVA_PROJECTION_PILOT_RESULTS.md` (200–300 lines) — Baseline vs. goal-modulated accuracy on 5 held-out templates, analysis, lessons learned.

**Risks**:

- **Free parameter proliferation**: If d_goal and d_frame are fit to data, risk of overfitting to 20 templates. Mitigation: Specify most d_goal/d_frame values theoretically (based on warrant type + goal conceptual alignment); fit only if evidence is strong.
- **Non-orthogonality**: Goals and frames may not be independent; may create redundant weighting. Mitigation: Test empirically; document correlations.
- **Complexity growth**: Adding goal modulation makes the system more complex. Mitigation: Ensure new complexity is justified by accuracy gain (should be tested against current ATLAS baseline on same 20 templates).

**Dependencies**:

- Phase A complete (goals/frames defined).
- Sprint CVA-4 complete (20 templates annotated with goal/frame information).
- Existing `epistemic_projection.py` available and documented.

**Estimated Effort**:

- David: 1 day (review projection extension, goal-warrant alignment matrix, interpretation)
- Claude (Code + AI systems): 8 days (projection implementation, multi-edge/path composition, goal-warrant matrix, testing, results analysis)
- **Total**: ~9 person-days

---

### Sprint CVA-6: Beauty Compression Testing (2 weeks)

**Objective**: Test whether aesthetic beauty can be "compressed" (predicted) from the 9-dimensional valuation vector; compare three models (linear, Bradley-Terry, neural); evaluate whether residuals suggest missing cultural axes.

**Background**: Scherer's suggestion: test categorical compression (cluster patterns → beauty category). Barrett's challenge: test whether residual variance suggests missing cultural variation. Friston's insight: test whether fluency (ProcessingCost) alone predicts beauty as well as full vector (i.e., is beauty just fluency, or are the 9 dimensions necessary?).

**Key Tasks**:

1. **Operationalize aesthetic beauty**:
   - Beauty = aesthetic preference judgment (e.g., 1–7 scale "How beautiful is this space?" or pairwise comparison "Is A or B more beautiful?").
   - Collect or identify existing aesthetic rating data for a set of ~50–100 spaces/images.
   - Ideally, data should cover multiple contexts (offices, hospitals, homes, museums) to test context-dependence.
   - If no existing dataset, use 20 pilot templates + expert beauty ratings (3–5 experts rate each).

2. **Compute valuation vector for each space/image**:
   - For each space, compute constraint vector c using Sprint CVA-1 measures.
   - For each space, compute baseline valuation vector ζ using Sprint CVA-2 axes (on default activity frame or pooled across frames).
   - Result: 50–100 spaces, each with (c, ζ, observed_beauty_rating).

3. **Test three compression models**:

   **Model 1: Linear**
   - Assume: `beauty = β₀ + βᵀζ` (linear combination of valuations).
   - Fit via regression to training data.
   - Evaluate on test set: R², mean-squared error, Spearman ρ.
   - Ablation: Fit model with each single valuation dimension to test which axes predict beauty alone (Friston's fluency test).

   **Model 2: Bradley-Terry**
   - If data is pairwise comparisons (A > B, A < C, etc.), use Bradley-Terry model: `P(A > B) = exp(θ_A) / (exp(θ_A) + exp(θ_B))`.
   - Here θ = function of valuation vector (e.g., θ_i = βᵀζ_i).
   - Fit via maximum likelihood.
   - Evaluate: Accuracy on held-out pairwise comparisons.

   **Model 3: Neural**
   - Implement small neural network: input = 9-dimensional ζ, output = beauty prediction (scalar).
   - 2–3 hidden layers, dropout for regularization.
   - Train on 80% of data; test on 20%.
   - Compare to linear model: is nonlinearity helping (or just overfitting)?

4. **Residual analysis** (Scherer, Barrett):
   - Compute residuals: `residual_i = observed_beauty_i - predicted_beauty_i`.
   - Plot residuals vs. context (office, hospital, home, museum). Do residuals cluster by context? If yes, suggests missing context-specific axes.
   - Plot residuals vs. cultural origin of space (if available). Do residuals cluster by culture? If yes, suggests missing cultural axes (Barrett's hypothesis).
   - Perform PCA on residuals: are they structured (have low-rank subspace) or random? If structured, estimate dimensionality of missing space.

5. **Categorical compression** (Scherer):
   - Cluster valuation vectors: use K-means or hierarchical clustering on ζ vectors.
   - Assign cluster labels: "traditional" (high EnviroNarrativeAlignment, low NoveltyValue), "modern" (high NoveltyValue, high ProcessingCost), "restorative" (high SafetyValue), etc.
   - Test: Do spaces in the same cluster have similar beauty ratings within context? Prediction: if clusters capture meaningful aesthetic categories, yes.
   - Result: a "beauty taxonomy" based on valuation patterns.

6. **Test fluency hypothesis** (Friston):
   - Fit Model 1 (linear) using only ProcessingCost (fluency): `beauty = β₀ + β₁ · ProcessingCost`.
   - Compare R² to full model (9 dimensions).
   - Prediction: R²(fluency-only) < R²(full), but difference is modest (maybe 0.5 correlation to 0.6 correlation). This would suggest fluency is a major driver but not the only driver.
   - If R²(fluency-only) ≈ R²(full), conclude that beauty is primarily fluency (simpler model wins).

7. **Create comparison report**:
   - For each model: R², coefficients (or feature importance for neural), interpretation.
   - Comparison table: Linear vs. Bradley-Terry vs. Neural (accuracy metrics).
   - Residual analysis: context-dependence, cultural dependence, dimensionality of missing space.
   - Fluency hypothesis test result.
   - Categorical compression: cluster taxonomy and within-cluster beauty consistency.

**Deliverables**:

- `src/services/cva/beauty_compression.py` (300 lines) — Linear, Bradley-Terry, neural models. Fit and predict functions. Residual analysis.
- `docs/CVA_BEAUTY_COMPRESSION_ANALYSIS.md` (800–1000 lines) — Models, results, residual analysis, fluency test, categorical clusters, interpretation.
- Test file: `tests/cva/test_beauty_compression.py` (150 lines) — Model instantiation, fit, predict, residual analysis.
- Results: `data/cva/beauty_model_results.json` — Model coefficients, R² values, cluster assignments.
- Visualization (optional): Plots of residuals by context, cluster taxonomy (word cloud or tree), Model 1 coefficients (which valuations drive beauty).

**Risks**:

- **Small sample size**: 20 pilot templates may be too few to fit three models reliably. Mitigation: Use cross-validation (leave-one-out or k-fold) to reduce overfitting risk. Acknowledge that this is exploratory; real validation requires larger dataset.
- **Measurement noise**: Beauty ratings may be noisy. Mitigation: Multiple raters per space, average ratings, report inter-rater reliability.
- **Missing confounds**: Beauty may depend on factors not in valuation vector (e.g., cost, rarity, novelty of material). Mitigation: Identify confounds; document limitations.
- **Cultural bias in model**: If training data is all WEIRD spaces, model will overfit to WEIRD aesthetic. Mitigation: Barrett's point; note this in results. Plan for cross-cultural retraining in Phase C.

**Dependencies**:

- Sprints CVA-1 to CVA-4 complete (constraints, valuations, frames, 20 templates annotated).
- Aesthetic rating data for 20–100 spaces (existing or collected).

**Estimated Effort**:

- David: 0.5 days (review beauty model results, interpretation)
- Claude (Code + AI systems): 8 days (model implementations, training, residual analysis, visualization, results documentation)
- Data collection (if needed): 2 days (recruiting raters, collecting beauty judgments)
- **Total**: ~10.5 person-days

---

## PHASE C: EMPIRICAL DESIGN (Sprints CVA-7 to CVA-8)

### Dependencies and Prerequisites

- All Phase A and Phase B complete.
- 20-template pilot successful (no major conceptual contradictions).
- CVA projection extends ATLAS competitively (no worse accuracy).
- Beauty models working (predictive power demonstrated).

### Note on Phase C Methodology

Phase C is *design* only—not implementation. These are pre-registered experiment protocols, ready to execute in a future sprint with collaborators. The goal is to operationalize the identifiability and cross-cultural validation tests that the panel unanimously requested.

---

### Sprint CVA-7: Identifiability Experiment Design (2 weeks)

**Objective**: Design three experiments that test whether constraints and valuations are empirically dissociable; specify statistical power analysis and identifiability conditions.

**Background**: Jordan's core concern: identifiability. Can we actually estimate constraints and valuations separately, or are they confounded? Three experiments test different aspects: (1) Goal manipulation (vary valuations, hold constraints constant); (2) Constraint manipulation (vary constraints, hold goals constant); (3) Cross-context transfer (train on one context, predict another).

**Key Tasks**:

1. **Experiment 1: Goal Manipulation (Hold Constraints, Vary Valuations)**

   **Hypothesis**: If constraints and valuations are separable, then holding spatial constraints constant and varying activity goals should shift valuation weights but leave constraint perception unchanged.

   **Design**:
   - Single environment (e.g., hospital patient room or office).
   - Participant pool: 60–80 healthy adults (counterbalanced; half of each culture if cross-cultural).
   - Manipulate activity frame via instructions:
     - Condition A: Recovery frame ("Imagine you are recovering from surgery; you need rest and safety.")
     - Condition B: Creative work frame ("Imagine you are a designer working on a project; you need inspiration and novelty.")
     - Condition C: Control frame ("Observe the room objectively; describe what you see.")
   - Measure within-subject:
     - Constraint perception: Rate perceived complexity (ProcessingCost), clarity of layout (ControlEfficacy), etc. via questionnaire or interview.
     - Valuation: Rate how much you prefer various features (safety, beauty, novelty, comfort, etc.) under the assigned frame.
   - Dependent variables:
     - Constraint scores (should be frame-independent; if frame affects ProcessingCost rating, constraints are confounded with valuations).
     - Valuation scores (should vary by frame; SafetyValue high in Recovery, NoveltyValue high in Creative).

   **Statistical model**:
   - Mixed model: `constraint_rating ~ frame + (1 | participant) + (1 | feature)`.
   - If frame effect on constraint is non-significant (or small effect size d < 0.3), supports separability.
   - `valuation_rating ~ frame + (1 | participant)`.
   - If frame effect on valuation is large (d > 0.8), supports that valuations are malleable.

   **Power analysis**:
   - Target: 80% power to detect frame effect on valuations (d = 0.6) with α = 0.05.
   - n = 60 provides 80% power for between-subject comparison of 3 frames (α = 0.05, two-tailed).

   **Identifiability condition**:
   - Separability is demonstrated if: (1) frame does NOT significantly affect constraint perception, AND (2) frame DOES significantly affect valuation.

2. **Experiment 2: Constraint Manipulation (Hold Goals, Vary Constraints)**

   **Hypothesis**: If constraints and valuations are separable, then varying spatial constraints (e.g., via redesign) while holding activity goals constant should change constraint perception but leave valuation structure unchanged.

   **Design**:
   - Two versions of the same space (e.g., office): one high-complexity (high ProcessingCost), one low-complexity.
   - Participant pool: 60–80 healthy adults.
   - Single activity frame: All participants are told "You are doing focused knowledge work in this office for 30 minutes."
   - Measure within-subject (each participant visits both offices, counterbalanced order):
     - Constraint perception: Rate ProcessingCost, ControlEfficacy, LoadRate, etc.
     - Valuation: Rate CompetenceSupportValue, AutonomySupportValue, etc.
   - Dependent variables:
     - Constraint scores (should differ between low- and high-complexity offices; confirm manipulation worked).
     - Valuation scores (should be stable; if constraint change induces valuation change, separability is violated).

   **Statistical model**:
   - `constraint_score ~ office_version + (1 | participant)`.
   - If office effect is large (d > 0.8), manipulation succeeded.
   - `valuation_score ~ office_version + (1 | participant)`.
   - If valuation is frame-stable (no significant office effect, or d < 0.3), supports separability.

   **Power analysis**:
   - n = 60 provides 80% power for within-subject detection of constraint effect d = 0.6.

   **Identifiability condition**:
   - Separability demonstrated if: (1) constraint perception changes by office version, AND (2) valuation structure does NOT change.

3. **Experiment 3: Cross-Context Transfer (Train on Office, Predict Hospital/Home)**

   **Hypothesis**: If CVA learns a structure that transfers across contexts, it supports the claim that constraints and valuations are genuine separable components, not just artifacts of a single context.

   **Design**:
   - Three contexts: office, hospital, home.
   - Data collection:
     - Office sample: 30 workers rate aesthetic preference and constraints in their workplaces (20 diverse offices, 1–2 people per office).
     - Hospital sample: 30 patients rate comfort, safety, and constraints in hospital rooms (10 diverse rooms, 3 people per room).
     - Home sample: 30 people rate comfort, beauty, and constraints in their homes (20 diverse homes, 1–2 per home).
   - CVA model training (on office data):
     - Extract constraints c and valuations ζ for each office setting.
     - Fit projection model: `preference_office = project(constraints, valuations, frame="office_work")`.
   - Cross-context prediction:
     - Apply learned CVA model to hospital and home data.
     - Prediction: `preference_predicted = project(constraints_measured, valuations_fitted, frame="recovery" or "home_living")`.
     - Compare to observed preferences.
   - Baseline comparison:
     - Fit a context-specific model on office data: `preference_office = f(all features)` (black-box; no constraint-valuation separation).
     - Compare transfer accuracy: CVA model vs. context-specific model.

   **Metric**:
   - Mean absolute error (MAE) or R² on held-out hospital/home data.
   - Hypothesis: CVA transfer accuracy > naive context-specific model (if CVA captures real structure).

   **Power analysis**:
   - n = 30 per context; statistical power depends on effect size of CVA transfer gain.
   - Exploratory; aiming for post-hoc power estimate.

   **Identifiability condition**:
   - Transfer success (R² > 0.4 on held-out contexts) supports claim that constraints and valuations generalize across contexts.
   - Transfer failure (R² < 0.2) suggests either constraints or valuations are context-specific.

---

2. **Pre-registration protocol** (Jordan's requirement):
   - Write up all three experiments with:
     - Hypotheses
     - Sample size (power-analyzed)
     - Statistical tests (pre-specified, not exploratory)
     - Decision rules (what result count as supporting/refuting separability?)
   - Register on Open Science Framework (OSF) or similar before data collection.
   - This prevents p-hacking and ensures results are credible.

3. **Strogatz's dynamics requirement**:
   - In the experiment design document, explain what *dynamical* predictions each experiment tests.
   - Experiment 1 tests whether F (constraint function) and G (valuation function) can change independently; if frame affects constraint perception, it violates assumption that F is goal-independent.
   - Experiment 2 tests whether constraint changes propagate to valuation changes; if they do, dynamics are coupled, not separable.
   - Experiment 3 tests whether the learned dynamics F and G transfer to new contexts; transfer success supports claim that these are genuine structural functions.

---

**Deliverables**:

- `docs/CVA_EXPERIMENT_1_GOAL_MANIPULATION_PROTOCOL.md` (300–400 lines) — Full protocol, hypotheses, measurements, statistical analysis plan, power analysis.
- `docs/CVA_EXPERIMENT_2_CONSTRAINT_MANIPULATION_PROTOCOL.md` (300–400 lines) — Same structure.
- `docs/CVA_EXPERIMENT_3_CROSS_CONTEXT_TRANSFER_PROTOCOL.md` (300–400 lines) — Same structure.
- `docs/CVA_IDENTIFIABILITY_PRE_REGISTRATION_SUMMARY.md` (200–300 lines) — Summary of all three experiments, identifiability conditions, statistical decision rules.
- OSF pre-registration URLs (once registered).

**Risks**:

- **Experimental feasibility**: Some manipulations may be impractical (e.g., getting hospital access for research). Mitigation: Identify institutional partners early (hospital IRBs, corporate office partners).
- **Confounds**: Frame manipulation may confound with other variables (e.g., instructions may make people more introspective, which changes all ratings). Mitigation: Include control conditions; pre-test instructions for unintended effects.
- **Measurement validity**: Constraint and valuation ratings may not be independently interpretable. Mitigation: Use multiple instruments per construct; test convergent validity (e.g., do ProcessingCost self-reports correlate with eye-tracking entropy?).

**Dependencies**:

- Phase A and B complete (registries, pilot annotation, projections working).
- Collaborators identified for data collection (e.g., hospital partners for Experiment 2).

**Estimated Effort**:

- David: 2 days (review experiment designs, statistical power, dynamics interpretation)
- Claude (Code + AI systems): 6 days (write protocols, power analyses, OSF setup, methodological documentation)
- Panel consultation (async): Jordan (identifiability conditions, statistical tests), Strogatz (dynamics predictions) — ~2 days
- **Total**: ~10 person-days

---

### Sprint CVA-8: Cross-Cultural Validation Design (2 weeks)

**Objective**: Design a cross-cultural CVA validation study; specify measurement instruments and cultural adaptations; identify collaborators.

**Background**: Barrett and Kitayama were emphatic: if CVA is adopted without cross-cultural validation, it will replicate WEIRD bias. The goal of this sprint is to design a study that tests whether the nine valuation axes are universal or culturally constructed.

**Key Tasks**:

1. **Define research questions**:
   - **RQ1 (Structure)**: Do the nine valuation axes have the same latent structure across cultures, or does the structure differ? Example: In individualist cultures, AutonomySupportValue and RelatednessSupportValue may be independent; in collectivist cultures, they may be fused.
   - **RQ2 (Salience)**: Which axes are perceptually salient and important in each culture? Example: StatusValue may be high-salience in hierarchical cultures, low in egalitarian.
   - **RQ3 (Measurement)**: Do existing measurement instruments (designed in WEIRD psychology labs) work cross-culturally, or must they be adapted?
   - **RQ4 (Prediction)**: Does a CVA model trained in one culture predict aesthetic preferences in another? If transfer is poor, suggests deep cultural differences.

2. **Select cultural sites** (3 minimum, ideally 5+):
   - **Site A: Individualist-West** (e.g., US, Western Europe)
   - **Site B: Collectivist-East** (e.g., Japan, Korea, China) — Kitayama's expertise
   - **Site C: High-context hierarchical** (e.g., India, parts of Middle East) — Leary's social-hierarchy focus
   - **Optional Site D: Small-scale / Indigenous** (e.g., Scandinavia, Native communities) — Different valuation of space (community-vs-individual balance)
   - **Optional Site E: Newly-industrializing** (e.g., Brazil, Vietnam) — Hybrid cultural values

   For each site, identify in-country collaborators with IRB connections, participant pools, and cultural expertise.

3. **Design cross-cultural measurement protocol**:
   - **RQ1 (Structure)**: Collect aesthetic ratings + constraint/valuation self-reports from 50–100 participants per site. Use exploratory factor analysis (EFA) to extract dimensions. Compare factor structures across sites. Prediction: Individualist and Collectivist sites will show different factor solutions.
   - **RQ2 (Salience)**: Ask participants to sort valuation axes by importance ("Which matters most for judging this space: safety, beauty, autonomy, belonging, status, ...?"). Compare rank orderings across sites.
   - **RQ3 (Measurement)**: Administer existing instruments (e.g., autonomy-support scale from SDT literature) and cultural adaptations side-by-side. Test convergent validity. If original and adapted versions correlate poorly, adapt measurement.
   - **RQ4 (Prediction)**: Collect aesthetic/preference data from 3 sites. Train CVA on Site A (Individualist-West), test on Sites B and C. Compare accuracy to within-site model.

4. **Measurement instruments**:
   - **Aesthetic preference**: Pairwise comparison or Likert rating ("How much do you prefer this space?"). Use standardized stimulus set (same room photos shown across all sites).
   - **Constraint perception**: Questionnaire with items like "This space feels complex," "It's easy to find my way," "There's a lot happening," etc. Translate and back-translate to ensure cultural validity.
   - **Valuation axes**: For each of the 9 axes, write 3–5 items. Example for SafetyValue: "I feel safe in this space," "I can predict what will happen here," "There are no surprises." Adapt language for cultural context (e.g., "fitting with my family expectations" for RelatednessSupportValue in collectivist cultures).
   - **Demographic / confound variables**: Collect age, gender, education, time in current city, cultural identification. These will be covariates.

5. **Study design specification**:
   - **Participants**: n = 50–100 per site (5 sites = 250–500 total). Recruited locally via universities, design firms, community centers.
   - **Stimuli**: 20–30 interior space photos (office, hospital, home, public) covering diverse designs. Selected to represent different points in valuation space (high beauty, high safety, high openness, etc.).
   - **Procedure**: 1–2 hour session. Complete constraint and valuation questionnaires; rate aesthetic preference for all 20 spaces; provide demographic info. Compensate appropriately (culture-dependent).
   - **Timing**: Parallel data collection across sites, ~3 months of fieldwork.

6. **Analysis plan**:
   - **RQ1**: EFA on 9 valuation axes per site. Compare factor structures (invariance testing via multi-group CFA).
   - **RQ2**: Rank correlations of axis importance across sites (Spearman ρ between rank orderings).
   - **RQ3**: Correlate original and adapted measurement items; test DIF (differential item functioning) for cultural bias.
   - **RQ4**: Fit CVA on Site A; predict Site B and C. Compare MAE to within-site baseline model.

7. **Collaboration and IRB strategy**:
   - Identify 3–5 in-country collaborators early (contact Kitayama, Leary, and others on panel for referrals).
   - Prepare template IRB protocol that can be adapted for each site.
   - Plan for asynchronous collaboration (video meetings, shared documents).
   - Budget for international collaboration: travel, participant compensation, translation.

8. **Contingency planning**:
   - If measurement cannot be aligned across sites (e.g., concept doesn't translate), plan for site-specific analysis instead of comparative analysis.
   - If cross-cultural transfer fails dramatically (R² < 0.2), it falsifies the universality assumption and informs redesign of CVA.

---

**Deliverables**:

- `docs/CVA_CROSS_CULTURAL_STUDY_PROTOCOL.md` (800–1000 lines) — Full protocol, RQs, sites, measurement, statistical analysis plan, cultural adaptation strategy.
- `docs/CVA_MEASUREMENT_INSTRUMENTS_CROSS_CULTURAL.md` (400–600 lines) — Questionnaires (original English + guidelines for translation), stimuli descriptions, demographic form.
- `docs/CVA_CROSS_CULTURAL_COLLABORATOR_LIST.md` (100–200 lines) — In-country collaborators by site, contact info, expertise, IRB status (to be filled in).
- `docs/CVA_CROSS_CULTURAL_IRB_TEMPLATE.md` (300 lines) — Template IRB protocol, adaptable for each site.
- Analysis scripts (stubs): `src/services/cva/cross_cultural_analysis.py` (100 lines) — EFA, invariance testing, transfer evaluation functions.

**Risks**:

- **Translation and cultural adaptation**: Concepts may not translate directly (e.g., "autonomy support" has different connotations in collectivist cultures). Mitigation: Back-translation; cognitive interviewing with pilot participants at each site.
- **Recruitment and attrition**: May be difficult to recruit participants across sites, especially in hierarchical cultures where volunteering is less common. Mitigation: Leverage collaborators' networks; offer fair compensation.
- **Measurement invariance failure**: If measurement invariance tests fail, cannot compare constructs across sites. Mitigation: Accept site-specific models; use qualitative interviews to understand differences.
- **Resource constraints**: International collaboration is expensive. Mitigation: Seek funding from NSF, NIH, international science foundations. Plan for phased data collection (Site A + B first, then expand).

**Dependencies**:

- Phase A and B complete (CVA framework working on 20 templates).
- In-country collaborators identified and committed.
- Funding secured (or identified).

**Estimated Effort**:

- David: 1.5 days (review cross-cultural protocol, identify collaborators, cultural considerations)
- Claude (Code + AI systems): 6 days (protocol documentation, measurement instruments, IRB template, analysis scripts)
- Panel consultation (async): Kitayama (collectivist structures), Barrett (cultural construction), Leary (social hierarchy) — ~2 days
- Collaborator identification: ~3 days (outreach, discussion, commitment)
- **Total**: ~12.5 person-days (plus collaborator time, which is external)

---

## PHASE D: INTEGRATION (Sprint CVA-9)

### Sprint CVA-9: Master Document Update + Full Integration Decision (4 weeks)

**Objective**: Update the Master Document with all CVA findings; run second expert panel review; make final GO/NO-GO decision on full 208-template reclassification.

**Background**: This is the decision gate. The panel will review:
1. Results from 20-template pilot (Sprint CVA-4).
2. Extended projection accuracy (Sprint CVA-5).
3. Beauty compression models (Sprint CVA-6).
4. Approved experiment designs (Sprints CVA-7 and CVA-8).

Then the panel will vote: Proceed to full reclassification (GO) or pause CVA and integrate useful components without full commitment (NO-GO)?

**Key Tasks**:

1. **Update Master Document with CVA sections**:
   - New chapter (Part XXII): "Constraint–Valuation Architecture Pilot Results"
     - Section A: Constraint Variable Registry summary (8 constraints, operationalizations)
     - Section B: Valuation Axes specification (9 axes, interactions, cultural variation)
     - Section C: Activity Frame module (canonical frames, frame-dependent weighting)
     - Section D: Pilot annotation results (20 templates, constraint-valuation mappings, gaps)
     - Section E: Projection extension (goal-modulated formula, multi-edge aggregation)
     - Section F: Beauty compression models (linear, Bradley-Terry, neural; results)
     - Section G: Identified research needs (identifiability studies, cross-cultural validation)
   - Cross-references to existing Master Doc sections (e.g., link CVA valuations to SDT in Part XVII, aesthetic judgments in Part X).
   - Disclaimer: "CVA is an analytical framework under development. This chapter documents the pilot phase and planned empirical validation. Adoption of full CVA depends on outcomes of identifiability and cross-cultural studies."

2. **Pilot results summary**:
   - Synthesis of Sprint CVA-4 gap report: Which constraint-valuation mappings were clean? Which ambiguous? Which gaps identified?
   - Synthesis of Sprint CVA-5 projection results: How does goal-modulated projection compare to baseline ATLAS on 20 templates?
   - Synthesis of Sprint CVA-6 beauty models: Which model best predicts aesthetic preference? What is the R²? Do residuals suggest missing axes or cultural variation?
   - Synthesis of findings: Did the pilot succeed (few contradictions, reasonable predictive accuracy) or reveal fundamental problems?

3. **Prepare second expert panel review**:
   - **Panel composition**: Same 12 panelists (to enable continuity), or subset (Scherer, Friston, Barrett, Deci, Jordan, Strogatz — the 6 most critical voices)?
   - **Pre-read**: Updated Master Doc chapter (Part XXII) + summary document (~10 pages) of pilot results and lessons learned.
   - **Review questions** (5–7, parallel to first panel):
     1. Do the pilot results support the claim that constraints and valuations are empirically dissociable?
     2. Which valuation axes appear robust across the 20 templates? Which are uncertain?
     3. Does the goal-modulated projection add value, or is it adding unjustified complexity?
     4. Are the proposed identifiability experiments well-designed and feasible?
     5. Is the cross-cultural validation protocol sufficiently rigorous?
     6. Given pilot results and planned validation, should we proceed to full 208-template reclassification (GO) or defer pending empirical validation (NO-GO)?
     7. If NO-GO, which components of CVA should be integrated into ATLAS as optional layers?

   - **Voting**: Same as first panel (Full, Partial, Defer, Reject); collect minority statements.

4. **Decision framework**:
   - **GO condition**: Pilot shows no contradictions, projections improve accuracy, panel consensus that empirical validation is sound.
   - **DEFER condition**: Pilot reveals gaps or ambiguities; empirical studies planned but results TBD; proceed with identifiability + cross-cultural studies before full adoption.
   - **PARTIAL condition**: Integrate useful components (e.g., constraint layer, some valuations) without claiming separability; revisit after empirical validation.
   - **NO-GO condition**: Fundamental problems revealed; archive CVA, return to ATLAS-only architecture.

5. **If GO: Plan Sprint CVA-10** (tentative, dependent on panel vote):
   - Full 208-template reclassification (~8–10 weeks).
   - CVA-integrated ATLAS system (combine CVA components with existing ATLAS architecture).
   - Deprecate old ATLAS projection; adopt goal-modulated projection.
   - Update calibration procedures to incorporate frame-dependent discount factors.

6. **If DEFER: Document decision and next steps**:
   - CVA remains "experimental" in codebase (tagged as cva_experimental/).
   - Identifiability studies launched (external collaboration, ~6–12 months to completion).
   - Code maintained but not integrated into main ATLAS pipeline.
   - Master Doc notes: "Awaiting empirical validation of constraint-valuation separability."

7. **If PARTIAL: Plan integration sprint** (3–4 weeks):
   - Decide which CVA components to integrate (e.g., constraint layer as optional feature descriptor, valuation axes as analytical dimensions without causal claims).
   - Update Master Doc to reflect partial adoption.
   - Version ATLAS as v2.5 (constraint-aware but not fully separated-causality).
   - Plan for future revisiting (after empirical studies).

8. **If NO-GO: Archive CVA, document lessons**:
   - Move CVA codebase to `archive/cva_deprecated/`.
   - Write post-mortem: What was learned? Why didn't CVA work out?
   - Identify specific ideas that might be salvaged for future work.

---

**Deliverables**:

- **Master Document update**: New Part XXII (~3000 lines), cross-references, disclaimer.
- **CVA Pilot Results Summary** (~1500 lines): Synthesis of Sprints CVA-4 through CVA-8, key findings, gaps.
- **Expert Panel 2 Pre-Read** (~1000 lines): Concise summary of pilot results, proposed experiments, decision questions.
- **Panel 2 Voting Record**: Record of votes, minority statements.
- **CVA Integration Decision Report** (~1000 lines): GO/DEFER/PARTIAL/NO-GO decision, rationale, next steps.
- **Sprint CVA-10 Plan** (if GO) or **CVA Archive Summary** (if NO-GO).

**Risks**:

- **Pilot failure**: If pilot reveals contradictions or poor predictive accuracy, GO decision is unlikely. Mitigation: Address issues in Phase B iteration (extend timelines if needed).
- **Panel disagreement**: Panelists may split on integration decision (e.g., 6 GO, 4 DEFER, 2 NO-GO). Mitigation: Use supermajority decision rule (2/3 required for GO; absent that, default to DEFER).
- **Resource constraints**: Full 208 reclassification is ~8–10 weeks of effort. May exceed available time/budget. Mitigation: Plan in incremental batches (50 templates, then 100, then 208).

**Dependencies**:

- All of Phase B complete and results documented.
- Phase C experiment designs complete and pre-registered.
- Second expert panel convened and available.

**Estimated Effort**:

- David: 3 days (review Phase B/C results, prepare panel pre-read, attend panel, decide)
- Claude (Code + AI systems): 12 days (Master Doc update, results synthesis, decision documentation)
- Panel 2 review: ~5 days (panelists' pre-read and deliberation)
- **Total**: ~20 person-days

---

## PHASE A/B/C/D SUMMARY

| Phase | Sprints | Timeline | Effort | Key Deliverable | Decision Gate |
|-------|---------|----------|--------|-----------------|--------------|
| A (Foundation) | CVA-1 to CVA-3 | 6–8 weeks | ~31 person-days | Registries + Activity Frame code | None; proceed to Phase B |
| B (Pilot Validation) | CVA-4 to CVA-6 | 6–8 weeks | ~34 person-days | 20-template annotation, projection test, beauty models | Pilot success? Proceed to Phase C? |
| C (Empirical Design) | CVA-7 to CVA-8 | 4 weeks | ~22.5 person-days | Pre-registered experiments, cross-cultural protocol | Internal review; proceed to Phase D |
| D (Integration) | CVA-9 | 4 weeks | ~20 person-days | Master Doc update, expert panel 2, GO/NO-GO decision | Final: GO (Sprint CVA-10) or DEFER (empirical studies) or PARTIAL (selective integration) or NO-GO (archive) |

**Total effort**: ~107.5 person-days across all phases.
**Estimated calendar time**: 20–24 weeks (roughly May–October 2026), assuming parallel work and panel availability.

---

## DEPENDENCIES ON EXISTING ATLAS SPRINTS

CVA sprints are **independent** from Sprints 0–8 (Master Doc, Setup, Overseer, etc.) until Phase D.

- **No conflicts**: CVA does not modify core ATLAS code, templates, or doctrings until Sprint CVA-9.
- **Parallel feasible**: Sprints CVA-1 to CVA-8 can run in parallel with Sprints 1–8.
- **Phase D integration**: Sprint CVA-9 depends on completion of Sprint 8 (Master Doc stable). If Sprint 8 finishes ~Mar 10, CVA Phase B can start Mar 15; Phase D decision can occur ~early August.

---

## PANEL MINORITY CONCERNS TRACKING

The panel's two DEFER votes (Jordan, Strogatz) included strong caveats about technical debt and half-measures. This sprint plan explicitly addresses their concerns:

### Strogatz: "Half-measures create technical debt"

**Risk**: Adopting CVA without specifying full dynamics (F and G functions) will create a hybrid system that's complex but not principled.

**Mitigation in this plan**:
- Sprint CVA-7 explicitly requires formal specification of F (constraint dynamics) and G (valuation dynamics) with stability proofs.
- Pre-registration protocol ensures that dynamics specifications are tested empirically (not just theoretical).
- Phase D decision point: If empirical validation fails, archive CVA entirely rather than keeping half-integrated system.

**Monitoring action**: In Sprint CVA-9, explicitly audit code for "orphaned CVA components"—parts of CVA integrated without full validation. Flag as technical debt if found.

### Barrett: "Cultural variation must be structural, not parametric"

**Risk**: Treating the 9 valuation axes as universal and only allowing cultural *weights* to vary (parametric) will replicate WEIRD bias.

**Mitigation in this plan**:
- Sprint CVA-2 explicitly builds cultural variation into axis structure: different cultures can have different axes, interaction matrices, and measurement instruments.
- Sprint CVA-8 (cross-cultural validation) tests whether axis *structure* differs across cultures (RQ1).
- Master Doc Part XXII disclaimer: "Axes are culturally contingent analytical frameworks, not discovered universals."

**Monitoring action**: In Sprint CVA-9, generate a "cultural variance report" showing whether significant structural differences emerged in Phase C data. If structure is truly universal (only weights vary), flag as unresolved concern for future work.

### Zumthor: "Use as design-thinking tool, not prediction engine"

**Risk**: Treating CVA as a predictive model (what is the aesthetic rating of this space?) rather than as a thinking tool (what dimensions should I consider in designing this space?).

**Mitigation in this plan**:
- Master Doc Part XXII includes a section: "CVA for Design Thinking" with examples of how architects can use the framework to think systematically about constraint-valuation relationships.
- Sprint CVA-6 (beauty compression) tests predictive power, but results are clearly labeled as "exploratory" not "deployable predictions."
- Phase D decision can include a separate question: "Does CVA improve architectural design quality?" (qualitative, from collaborators).

**Monitoring action**: If CVA achieves high predictive accuracy but no architectural benefit (e.g., designers still rely on intuition, not framework), classify as "prediction-only" and lower priority for integration.

---

## ESTIMATED BUDGET AND TIMELINE

### Person-Effort Breakdown

| Role | Phase A | Phase B | Phase C | Phase D | Total |
|------|---------|---------|---------|---------|-------|
| David | 4.5 days | 2.5 days | 3.5 days | 3 days | 13.5 days |
| Claude Code + AI | 37 days | 26 days | 12 days | 12 days | 87 days |
| Panel (async) | 4 days | 5 days | 4 days | 5 days | 18 days |
| Collaborators (ext.) | 0 days | 0 days | 3 days (design) | — | 3 days |
| **Total** | **45.5** | **33.5** | **22.5** | **20** | **121.5** |

**Notes**:
- David's role: strategic guidance, conceptual review, panel liaison.
- Claude: code, documentation, analysis.
- Panel: async pre-reads, reviews, voting (no real-time meetings assumed).
- Collaborators: external (cross-cultural study partners, hospital IRBs, etc.).

### Calendar Timeline (Nominal, Parallel Work)

```
Mar 1–15: Phase A Sprint Kickoff
├─ CVA-1: Constraint Variables (weeks 1–2)
├─ CVA-2: Valuation Axes (weeks 1–2, overlaps with CVA-1)
└─ CVA-3: Activity Frame (weeks 2–3, after CVA-1 draft)

Mar 15–May 1: Phase B Validation (6 weeks)
├─ CVA-4: 20-Template Pilot (weeks 1–3)
├─ CVA-5: Projection Extension (weeks 2–3)
└─ CVA-6: Beauty Compression (weeks 4–6)

May 1–15: Phase C Empirical Design (2 weeks)
├─ CVA-7: Identifiability Experiment Design (weeks 1–2)
└─ CVA-8: Cross-Cultural Protocol (weeks 1–2, parallel)

May 15–June 15: Phase D Integration (4 weeks)
├─ CVA-9a: Master Doc update (weeks 1–2)
├─ CVA-9b: Expert Panel 2 (weeks 2–3)
└─ CVA-9c: Go/No-Go Decision Report (weeks 3–4)

June 1 onwards (contingent):
├─ If GO: Sprint CVA-10 (Full 208-template reclassification, ~8–10 weeks, July–September)
├─ If DEFER: Launch identifiability studies (external partners, ~6–12 months, parallel to other work)
└─ If PARTIAL: Integration sprint (3–4 weeks, June–July)
```

**Total elapsed time**: ~20–24 weeks (approximately May–October 2026, with some parallelization).

---

## RISKS AND CONTINGENCIES

### Major Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| Phase A schemas overly ambitious; require iteration | Medium | 2–3 weeks timeline slip | Design with flexibility; allow Sprint CVA-2 to inform CVA-1 revisions. |
| Phase B pilot reveals fundamental contradictions (e.g., valuations confound with constraints) | Low–Medium | 4–6 weeks; loop back to Phase A or escalate to panel | Pre-read through literature; pilot design review before implementation. |
| Identifiability experiments (Phase C) are infeasible (e.g., hospital access impossible) | Medium | Plan becomes exploratory only; empirical validation delayed | Identify alternative participant pools (e.g., architecture students, online simulation). |
| Cross-cultural study recruitment fails | Medium | Reduced cultural scope; findings less generalizable | Prioritize 2–3 high-value sites; defer to 5-site goal until Phase D +1. |
| Panel 2 votes NO-GO; CVA abandoned | Low–Medium | ~100 person-days effort with limited integration | Escalation to David; consider partial compromise (integrate constraint layer only). |
| Resource constraints (time, budget) exceed plan | Medium | Extend timeline or reduce scope | Prioritize Phase B over Phase C; Phase C can be pre-registered and handed to external collaborators. |

### Contingency Plans

- **If Phase A exceeds estimate**: Extend by 1–2 weeks; push Phase B start to late Mar.
- **If Phase B pilot fails**: Run diagnostic sprint (~2 weeks) to understand failure; loop back to Phase A for remedial work if needed.
- **If Phase C experiments are infeasible**: Pre-register simplified alternative (e.g., correlational study instead of RCT); proceed with Phase D decision using observational data.
- **If Panel 2 deadlocks**: Revert to PARTIAL adoption (integrate constraint layer, optional valuations); defer full CVA.

---

## MONITORING AND CHECKPOINTS

### Sprint Completion Criteria

Each sprint should end with:
1. **Code completion**: All deliverables in code (registries, modules, tests) passing tests.
2. **Documentation**: Markdown specifications matching code.
3. **Panel checkpoint**: (Optional) Brief async review from 1–2 panelists to catch major errors early.

### Phase Checkpoints

- **End of Phase A** (March 15): Registries + Activity Frame module code complete; no blocking issues.
- **End of Phase B** (May 1): 20 templates annotated; projection outperforms baseline; beauty models R² > 0.4.
- **End of Phase C** (May 15): Experiments pre-registered; no design flaws identified.
- **End of Phase D** (June 15): Master Doc updated; Panel 2 convened; GO/NO-GO decision documented.

### Success Metrics

| Phase | Metric | Target |
|-------|--------|--------|
| A | Code quality, documentation completeness | 95%+ test coverage, specs >500 lines each |
| B | Pilot consistency, projection accuracy | <5 major gaps in 20 annotations, CVA projection ≥ baseline accuracy |
| C | Experiment feasibility, protocol rigor | Pre-registration complete, no fatal design flaws in panel review |
| D | Integration clarity, panel consensus | 2/3+ panelists vote GO or PARTIAL (not DEFER/REJECT) |

---

## VERSIONING AND DOCUMENTATION STANDARDS

All deliverables follow David's CLAUDE.md standards:

- **File naming**: Descriptive, dated. Example: `CVA_CONSTRAINT_VARIABLE_REGISTRY_2026-03-15.md` (not `registry.md`).
- **Documentation**: Markdown with headers, tables, examples, cross-references.
- **Code style**: Docstrings, type hints, test coverage >80%.
- **Accessibility**: No dark blue on dark backgrounds; WCAG 2.1 AA contrast.
- **Versioning**: Track decisions in `docs/CVA_DECISIONS_LOG.md` (parallel to existing `TIER2_DECISIONS_LOG.md`).

---

## CONCLUSION

This sprint plan operationalizes the expert panel's CVA recommendation: adopt partially, with rigorous empirical validation. The 9-sprint, 4-phase structure:

1. **Builds infrastructure** (Phase A) without disrupting ATLAS.
2. **Validates pilot** (Phase B) on 20 manageable templates before full commitment.
3. **Designs rigorous experiments** (Phase C) to test the core separability assumption.
4. **Makes explicit GO/NO-GO decision** (Phase D) based on evidence, not hope.

Throughout, the plan tracks minority concerns (Strogatz's debt warning, Barrett's cultural critique, Zumthor's design-tool emphasis) and treats them as design requirements, not exceptions.

The result: if CVA is adopted, it will be on a foundation of empirical validation and explicit dynamics. If it's not adopted, the system will have learned what doesn't work and can pivot accordingly.

---

**Document Status**: DRAFT for David's review
**Prepared**: February 27, 2026
**Next Step**: David's approval; feedback loop with 3–4 panelists; finalize and commit to TASKS.md

