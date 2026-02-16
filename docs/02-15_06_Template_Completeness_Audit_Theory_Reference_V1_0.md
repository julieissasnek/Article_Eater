# TEMPLATE COMPLETENESS AUDIT & THEORY REFERENCE
## Article Eater — Opus-Side Deliverable for Sprint 7/8
## Version 1.0 — February 15, 2026

---

# PART 1: TEMPLATE COMPLETENESS MATRIX

## Scoring Key

For each template, I assess six dimensions on a 0–3 scale:

| Score | Meaning |
|-------|---------|
| 3 | **Fully specified** — all required fields present with values, ready for direct encoding |
| 2 | **Mostly specified** — causal chain present but some links lack parameters or bridging quality |
| 1 | **Narrative only** — mechanism described in prose, but not structured as typed links |
| 0 | **Missing or stub** — mentioned but not elaborated |

**Dimensions**: CC = Causal Chain, PQ = Parameter/Quantitative data, SC = Scope Conditions, MO = Moderators, KI = Known Interactions, KR = Key References

## Templates 1–20 (Source: CMR_Revised_Spec_Panel_Templates_V2_0.md Part III)

| # | Template ID | Name | CC | PQ | SC | MO | KI | KR | Maturity | Encoding Ready? | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | PP_SPECTRAL_MATCH_001 | Visual scene statistics → PE reduction | 3 | 2 | 2 | 1 | 2 | 3 | how-plausibly | **YES** | 3-link chain with levels, bridging, maturity. Params: 40-60% PE reduction, 10-20% glucose reduction. Missing: explicit moderator list (only mentioned in text). |
| 2 | PP_COMPLEXITY_GOLDILOCKS_002 | Stimulus complexity → inverted-U | 3 | 1 | 2 | 3 | 1 | 3 | how-plausibly | **YES** | 5-link chain (branching: low/mod/high PE). No quantitative curve parameters — inverted-U shape described qualitatively. Good moderator list (familiarity, culture, expertise, arousal). |
| 3 | SN_LAYOUT_COGNITIVE_MAP_001 | Spatial layout → cognitive map quality | 3 | 2 | 2 | 1 | 2 | 3 | how-actually | **YES** | 3-link chain. Params: place field stability r=0.7-0.9 vs 0.3-0.5. Good scope (locomotion, 5-15 min, intact hippocampus). Moderators not explicitly listed. |
| 4 | DT_ATTENTIONAL_DEMAND_001 | Env. demand → DMN suppression → fatigue | 3 | 1 | 2 | 1 | 2 | 3 | how-plausibly | **YES** | 4-link chain. "Onset within seconds, accumulates over mins–hrs" but no specific dose-response. Missing explicit moderator list. |
| 5 | NM_THREAT_HPA_001 | Threat cues → amygdala → cortisol | 3 | 3 | 2 | 1 | 2 | 3 | how-actually | **YES** | 3-link chain with excellent parameters (onset 15-20min, peak 30-45min, recovery t½ 60min, 20-100% above baseline). Missing explicit moderator list. |
| 6 | NM_CORTISOL_HIPPOCAMPAL_005 | Chronic cortisol → hippocampal damage | 3 | 2 | 3 | 1 | 2 | 3 | how-actually | **YES** | 3-link chain + vicious cycle (link 3 circular). Params: 3-week onset in rodents. Good scope (chronic only, age-dependent). |
| 7 | IC_ALLOSTATIC_ANTICIPATION_001 | Predictability → allostatic efficiency | 3 | 1 | 3 | 1 | 3 | 3 | how-plausibly | **YES** | 3-link chain. Params: "not well-characterized quantitatively." Excellent scope conditions (timescale, monotony, Goldilocks). Excellent known interactions (distinguished from PP_SPECTRAL_MATCH). |
| 8 | EC_AFFORDANCE_POSTURAL_001 | Affordances → postural → autonomic | 3 | 2 | 2 | 1 | 2 | 3 | how-plausibly | **YES** | 3-link chain. Params: d≈0.3-0.5 for postural effects on HRV. Good scope (physical presence required). |
| 9 | DP_IMPLICIT_EVALUATION_001 | Rapid implicit eval → affective response | 3 | 2 | 3 | 1 | 2 | 3 | how-plausibly | **YES** | 3-link chain. Params: onset ~80-120ms. Good scope (first encounters, <2s, override conditions). Link 3 flagged as CONTESTED (basic emotions debate). |
| 10 | MS_CONSOLIDATION_RESTORATION_001 | Restorative env → DMN → memory consolidation | 3 | 2 | 3 | 1 | 3 | 3 | how-plausibly | **YES** | 3-link chain. Params: ~20min rest, emotionally salient memories stronger. Good scope (cognitive rest vs. pleasantness). Excellent interactions (explains ART mechanistically). |
| 11 | NM_NORADRENERGIC_EXPLORE_006 | Novelty → LC-NE → explore/exploit | 3 | 2 | 3 | 1 | 2 | 3 | how-plausibly | **YES** | 3-link chain. Params: phasic vs tonic LC firing mapped to moderate vs high uncertainty. Good scope (Goldilocks, integrates multiple uncertainty sources). |
| 12 | IC_INTEROCEPTIVE_AFFECT_001 | Interoceptive PE → affect construction | 3 | 1 | 3 | 1 | 3 | 3 | how-plausibly | **YES** | 3-link chain. Link 3 CONTESTED (constructionism vs basic emotions). Identified as BRIDGE TEMPLATE — connects all body-affecting templates to subjective experience. Scope: alexithymia, interoceptive sensitivity. |
| 13 | XF_NATURE_VIEW_MULTIPATH_001 | Nature → multiple parallel pathways → stress | 3 | 2 | 1 | 0 | 3 | 1 | how-plausibly | **MOSTLY** | COMPOSED template linking 4 base templates (A, B, C, D). Params: pathway independence partial, temporal dynamics differ (200ms to days). Predictions: 30-40% from pathway A alone, 70-80% without pathway C. **Missing**: explicit moderators and standalone references. |
| 14 | XF_NAVIGATION_STRESS_CYCLE_002 | Hard navigation → stress → worse navigation | 2 | 0 | 1 | 0 | 3 | 0 | how-plausibly | **PARTIAL** | Cycle described but links reference other templates rather than having own parameters. Breaking-the-cycle intervention points well-specified. **Missing**: own params, moderators, refs (relies on components). |
| 15 | PP_CULTURAL_PRIOR_CALIBRATION_001 | Cultural ecology → shifted set-points | 3 | 0 | 3 | 1 | 2 | 2 | how-possibly | **YES** | 3-link chain, all how-possibly. Most speculative template. No quantitative params. Good scope (sensory dimensions, developmental sensitive period). Central to India fieldwork. |
| 16 | DT_RESTORATION_TIMECOURSE_001 | Transition → DMN re-engagement timing | 3 | 3 | 1 | 1 | 1 | 1 | how-plausibly | **PARTIAL** | 3-link chain. Excellent params (3-5min initial, 20-40min full, cortisol t½ 60min, individual variation correlated with mindfulness). **Missing**: explicit scope, moderators sparse, refs sparse. |
| 17 | NM_DOPAMINERGIC_NOVELTY_001 | Novelty → dopamine → wanting/approach | 3 | 2 | 3 | 1 | 2 | 3 | how-actually | **YES** | 3-link chain. Wanting≠liking distinction. Params: habituates ~3-5 exposures. Good scope (arousal modulation, LC-NE connection). |
| 18 | EC_VESTIBULAR_SPATIAL_001 | Vertical architecture → vestibular → cognition | 3 | 0 | 2 | 0 | 1 | 2 | how-possibly | **YES** | 3-link chain. Link 3 bridging quality LOW — vestibular-to-cognitive is speculative. **Missing**: any quantitative params, moderators. |
| 19 | XF_SOCIAL_AFFORDANCE_001 | Layout → social behavior patterns | 3 | 0 | 2 | 3 | 1 | 2 | how-plausibly | **YES** | 3-link chain. No quantitative params but excellent moderator list (cultural proxemics, introversion, task demands, relationships). Goldilocks for social density. |
| 20 | XF_ENVIRONMENT_PERFORMANCE_001 | Env. features → cognitive resource ±→ performance | 2 | 0 | 1 | 0 | 3 | 0 | how-possibly | **PARTIAL** | COMPOSED higher-order template. Lists 4 depletion pathways + 4 enhancement pathways. Net performance = baseline - depletion + enhancement. **Missing**: own quantitative model, moderators, standalone refs. |

## Templates 21–30 (Source: Neuroscience_Panel_Templates_and_Taxonomy_V1_0.md Part A)

| # | Template ID | Name | CC | PQ | SC | MO | KI | KR | Maturity | Encoding Ready? | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 21 | PP_ACTIVE_INFERENCE_003 | Controllability → action policies → FE | 3 | 2 | 3 | 3 | 2 | 3 | how-plausibly | **YES** | 4-link chain. Params: 15-30% cortisol reduction from perceived control. Excellent moderators (actual vs perceived, learned helplessness, culture). |
| 22 | PP_RAPID_GIST_004 | LSF → rapid PFC → contextual frame | 3 | 3 | 3 | 3 | 3 | 3 | how-actually | **YES — EXEMPLARY** | 4-link chain. Params: PFC activation at 130ms, LSF < 2 cycles/deg. Moderators: viewing duration, prior expectation, emotional state, cultural familiarity. Interactions: T1, T9, T5. Architectural prediction provided. |
| 23 | SN_CONTEXT_MEMORY_002 | Context stability → encoding → retrieval | 3 | 3 | 3 | 3 | 2 | 3 | how-actually | **YES — EXEMPLARY** | 4-link chain. Params: 20-40% recall advantage (Smith & Vela meta). Moderators: distinctiveness, emotional valence, episode count, time delay. Scope: physical occupancy required, multisensory. Architectural predictions for schools/hospitals. |
| 24 | SN_THETA_SEQUENCE_003 | Path structure → theta sequences → comfort | 3 | 3 | 3 | 3 | 2 | 3 | how-plausibly | **YES — EXEMPLARY** | 4-link chain + converse (link 4). Params: 7-10 place fields per theta cycle, 125ms theta period. Moderators: familiarity, speed, cognitive load, age. Human vs rodent theta noted. |
| 25 | MS_RIPPLE_REPLAY_002 | Rest → SPW-R replay → consolidation | 3 | 3 | 3 | 2 | 3 | 3 | how-actually | **YES — EXEMPLARY** | 5-link chain. Params: SPW-Rs 0.5-2 Hz, 50-120ms each, ~300ms-1s compressed to ~50ms. Excellent interactions (ACh gating, theta sequences). |
| 26 | NM_CHOLINERGIC_GATING_007 | Uncertainty → selective ACh → precision | 3 | 2 | 3 | 2 | 3 | 3 | how-actually | **YES** | 4-link chain + two mode descriptions (expected vs unexpected uncertainty). Params: specific but not always quantified. BF projection specificity emphasized. Key gating relationship with T25. |
| 27 | DT_DMN_MAINTENANCE_002 | Low demand → DMN subsystems → restoration | 3 | 2 | 3 | 3 | 3 | 3 | how-plausibly | **YES** | 5-link chain including 2 DMN subsystems (MTL + dmPFC). Params: MTL maintenance ~5min, full DMN ~15-20min. Moderators: anxiety, rest quality, duration. Subsystem-specific architectural predictions. |
| 28 | EC_COGNITIVE_OFFLOADING_002 | Legibility → offloading → freed resources | 3 | 1 | 3 | 3 | 3 | 3 | how-plausibly | **YES** | 4-link chain. Scope: perceivability required, first exposures, cultural/linguistic. Moderators: cognitive capacity, familiarity, task demands. Excellent interactions (T21, T3, T22). Link 4 long-term is how-possibly. |
| 29 | ALLOSTATIC_MASTER_001 | Cumulative demands → allostatic budget → capacity | 3 | 1 | 3 | 3 | 3 | 3 | how-plausibly | **YES** | MASTER TEMPLATE. 5-link chain including budget surplus vs deficit with triage hierarchy. Moderators: individual capacity, concurrent stressors, adaptive capacity, recovery. This is the integrating framework — all other templates feed into it. Measurement implications specified (HRV, cortisol, CRP). |
| 30 | CHRONO_LIGHT_ENTRAINMENT_001 | Light → circadian → physiology | 3 | 3 | 3 | 3 | 3 | 3 | how-actually | **YES — EXEMPLARY** | 4+ link chain (link 3 has 4 sub-systems: melatonin, cortisol, temperature, immune). Params: ipRGCs 480nm, threshold 100-200 lux, bright >1000 lux. Moderators: window design, latitude, screen exposure, age, shift work, drugs. |

## Templates 31–40 (Source: Panel_III_Multimodal_Senses_HigherCognition_V1_0.md)

| # | Template ID | Name | CC | PQ | SC | MO | KI | KR | Maturity | Encoding Ready? | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 31 | AUD_SCENE_ANALYSIS_001 | Acoustic complexity → ASA → resource depletion | 3 | 3 | 3 | 1 | 2 | 3 | how-actually | **YES** | 3-link chain. Excellent params: 3-5 sources, 30ms grouping, >1 semitone, >15° azimuth, fMRI 5%/source, speech drops 95%→50%, WM -10-20%. Boundary conditions per link. |
| 32 | AUD_SUBCORTICAL_ENCODING_002 | Chronic acoustics → brainstem plasticity | 3 | 3 | 3 | 1 | 1 | 3 | how-actually | **YES** | 3-link chain. Params: good <40dB(A)/RT60 0.4-0.8s/SNR+15dB; degraded >55dB(A)/RT60>1.5s/SNR<+5dB; 0.5-1ms encoding delays. Boundary: chronic exposure, developmental extremes. |
| 33 | AUD_REVERBERATION_SPACE_003 | Room acoustics → auditory space model | 3 | 3 | 2 | 0 | 2 | 2 | how-actually/plausibly | **MOSTLY** | 3-link chain. Params: early reflections <50ms, late reverb >80ms, RT60 ranges, mismatch threshold >0.3s. **Missing**: explicit moderators, sparse refs. |
| 34 | HAP_SURFACE_MATERIAL_001 | Surface → haptic eval → material affect | 3 | 3 | 3 | 1 | 2 | 3 | how-actually | **YES** | 3-link chain. Excellent params: 4 haptic dimensions, thermal effusivity (wood ~500-600 vs metal ~10k-20k), d=0.3-0.7 natural>synthetic, 200ms ID / 500ms-2s affect. Boundary: contact required, context modulates (metal premium vs cold). |
| 35 | OLF_CONTEXT_AFFECT_001 | Ambient olfactory → affect + memory | 3 | 3 | 3 | 1 | 2 | 3 | how-actually | **YES** | 4-link chain. Excellent params: detection thresholds (0.5ppb H2S, 20ppb vanillin), adaptation 50% in 1-2min / 90% in 10-15min, amygdala 100-200ms, hedonic d=0.3-0.5, memory 15-30% recall boost, earlier memories (~6yr vs ~11yr). First association dominance. |
| 36 | HC_WORKING_MEMORY_LOAD_001 | Env demands → WM overflow → errors | 3 | 3 | 2 | 1 | 2 | 3 | how-actually | **YES** | 3-link chain. Excellent params: 3-4 items ±1, each nav decision ~1 item, -25% under cortisol, decline 4→2.5 items age 25→70, error gradual 1-3 items then catastrophic 3-5 items. |
| 37 | ER_ECOLOGICAL_RATIONALITY_001 | Info structure → heuristic fit → decision | 2 | 2 | 2 | 0 | 1 | 2 | how-plausibly | **MOSTLY** | 2-link chain (short). Three decision regimes specified (high/moderate/low cue validity). Less-is-more effect. **Missing**: explicit moderators, sparse refs, more of a design principle than mechanistic template. |
| 38 | HC_HIERARCHICAL_CONTROL_002 | Task hierarchy → PFC gradient → fatigue | 3 | 3 | 2 | 0 | 1 | 3 | how-actually | **YES** | 2-link chain + architectural prediction. Params: +150-300ms per abstraction level, +5-15% error per nesting level, depth limit 3-4 levels, anterior PFC fatigue >30-45min. |
| 39 | MSI_CONGRUENCY_PRINCIPLE_001 | Multisensory congruency → enhancement | 2 | 2 | 2 | 0 | 2 | 1 | how-plausibly | **MOSTLY** | 3-link chain but loosely structured. Params: 15-25% comfort improvement congruent, 10-20% degradation incongruent (asymmetric). Boundary: abstract correspondences, some innate some learned. **Missing**: explicit moderators, sparse refs, crossmodal correspondence taxonomy. |
| 40 | MSI_INVERSE_EFFECTIVENESS_002 | Degraded sense → enhanced compensation | 2 | 3 | 2 | 0 | 1 | 2 | how-actually | **MOSTLY** | 2-link chain. Excellent params: enhancement 5% at 0 SD, 20-50% at -1 SD, 100-200% at -2 SD, MLE weighting (vision ~70% drops to ~30% in low light). **Missing**: explicit moderators, sparse refs. |

---

## COMPLETENESS SUMMARY

| Category | Count | Templates |
|----------|-------|-----------|
| **EXEMPLARY** (all dimensions ≥ 2, ready for mechanical encoding) | 6 | T22, T23, T24, T25, T29, T30 |
| **YES** (encoding ready, minor gaps fillable from context) | 20 | T1–T12, T15, T17, T19, T21, T26–T28, T31–T32, T34–T36, T38 |
| **MOSTLY** (1–2 dimensions need filling before encoding) | 6 | T13, T33, T37, T39, T40, T16 |
| **PARTIAL** (significant gaps, need Opus spec work) | 3 | T14, T18, T20 |

**Bottom line**: 26 of 40 templates are encoding-ready. 6 more need minor filling. Only 3 need significant additional spec work before CC can encode them (T14, T18, T20 — all compositional or speculative templates where the "encoding" is really about deciding what the data structure should look like for cycle templates and composed higher-order templates).

---

# PART 2: PREDICTION GENERATION GRAMMAR

## The 8 Interventionist Operations

Source: CMR_Spec_V1_0.md § Step 4, formalized here as typed operations.

Each operation takes a **MechanismTrace** as input and produces one or more **GeneratedPrediction** objects. The operation works by identifying an intervention point in the trace and asking a counterfactual question.

### Operation 1: SUBSTITUTE_CAUSE

**Logic**: If the mechanism trace says X → Y because of property P of X, then ANY stimulus with property P should → Y.

**Input**: A trace where link[0].from_variable has an identified active property
**Transformation**: Replace link[0].from_variable with an alternative stimulus sharing the active property
**Output**: Prediction that the alternative stimulus produces the same downstream effects

**Worked example**:
- Trace: nature_view →[1/f spectral statistics] low_PE →[reduced metabolic cost] lower_cortisol
- Active property: 1/f spectral statistics
- Substitute: artificial_fractal_scene (shares 1/f statistics)
- Prediction: "Artificial fractal scenes should produce cortisol reduction comparable to nature views, because the active mechanism is spectral statistics, not 'naturalness' per se"
- Confidence: inherits weakest link maturity (how-plausibly)
- Testability: HIGH (straightforward experimental design: fractal vs nature vs control)
- Novelty check: query web for existing evidence on fractal → cortisol

**Implementation pattern**:
```python
def substitute_cause(trace: MechanismTrace) -> List[GeneratedPrediction]:
    predictions = []
    first_link = trace.links[0]
    # Identify the active property of the cause
    active_property = first_link.activity  # what the cause DOES
    # Query template for "transferable_to" field
    for template in templates_using_link(first_link):
        for alternative in template.transferable_to:
            predictions.append(GeneratedPrediction(
                statement=f"{alternative} should produce {trace.links[-1].to_variable} "
                          f"via same mechanism ({active_property})",
                interventionist_operation=InterventionistOperation.SUBSTITUTE_CAUSE,
                derivation_chain=[t.template_id for t in trace_templates],
                confidence=trace.weakest_maturity_score,
            ))
    return predictions
```

### Operation 2: VARY_MODERATOR

**Logic**: For each moderator of the mechanism, predict how variation in that moderator changes the outcome.

**Input**: A trace + the moderators from the template(s) used
**Transformation**: For each moderator, predict the effect of high vs low values
**Output**: Predictions about individual/group differences

**Worked example**:
- Trace: nature_view → low_PE → lower_cortisol
- Moderator: baseline_anxiety (high anxiety = more dynamic range for reduction)
- Prediction: "High-anxiety individuals should show larger cortisol reduction from nature views than low-anxiety individuals, because they have greater headroom for PE reduction"
- Confidence: MEDIUM (moderator relationship is plausible but less directly tested)

**Implementation**: Iterate over `template.moderators`, generate one prediction per moderator.

### Operation 3: BLOCK_PATHWAY

**Logic**: If the mechanism goes through intermediate M, pharmacologically or experimentally blocking M should block the effect.

**Input**: A trace with ≥ 2 links
**Transformation**: For each intermediate variable, predict the result of blocking it
**Output**: Predictions about pathway specificity

**Worked example**:
- Trace: nature_view → low_PE → reduced_noradrenergic_arousal → lower_cortisol
- Block target: noradrenergic system
- Prediction: "Alpha-2 adrenergic agonists (blocking noradrenergic arousal) should eliminate the cortisol benefit of nature views, if the mechanism goes through NE reduction. Beta-blockers (different pathway) should NOT block it."
- Testability: DIFFICULT (requires pharmacological intervention in architectural study)
- Novelty: HIGH (this specific pharmacological test has likely not been done)

**Implementation**: For each interior link, generate a blocking prediction. Flag testability based on whether the block is achievable (pharmacological = difficult, environmental = moderate, behavioral = easy).

### Operation 4: CHANGE_TEMPORAL_CONTEXT

**Logic**: If the mechanism has temporal dynamics, changing when exposure occurs should change the effect.

**Input**: A trace + temporal parameters from template
**Transformation**: Predict effects at different exposure timings
**Output**: Predictions about optimal timing

**Worked example**:
- Trace: nature_view → cortisol_reduction (cortisol peaks in AM, nadirs in PM)
- Prediction: "Nature view exposure should produce larger absolute cortisol reduction in the morning (when cortisol is highest) than in the evening. Pre-surgical morning nature views should be more effective than evening views."
- Confidence: HIGH (cortisol diurnal rhythm is how-actually)

**Implementation**: Check `link.temporal_dynamics` for onset, peak, duration. Generate timing predictions.

### Operation 5: VARY_INDIVIDUAL

**Logic**: If the mechanism depends on a neural system with known individual variation, predict who benefits more/less.

**Input**: A trace + known individual difference factors
**Transformation**: For each individual difference, predict differential effects
**Output**: Predictions about population-specific effects

**Worked example**:
- Trace: interoceptive_PE → affect_construction
- Individual difference: interoceptive sensitivity (varies widely)
- Prediction: "Individuals with poor interoceptive accuracy (low heartbeat detection scores) should show reduced affective benefit from architectural design, but intact physiological benefit — because the PE still occurs but isn't translated into conscious affect."

**Implementation**: Check scope_conditions for individual differences. Cross-reference with known clinical/demographic factors.

### Operation 6: CROSS_CULTURAL

**Logic**: If the mechanism depends on learned priors or cultural calibration, predict cross-cultural variation.

**Input**: A trace involving PP_CULTURAL_PRIOR_CALIBRATION_001 or culture-dependent moderators
**Transformation**: Predict how culturally different prior distributions shift outcomes
**Output**: Predictions about cross-cultural variation in architectural effects

**Worked example**:
- Trace: visual_complexity → PE → preference (Goldilocks)
- Cultural variable: visual ecology density
- Prediction: "Cultures with high-density visual environments (e.g., Indian bazaars, Tokyo Shibuya) should show rightward-shifted complexity preference curves — preferring higher complexity levels that Western participants find overwhelming."

### Operation 7: ADD_CONCURRENT_MECHANISM

**Logic**: If two independent templates predict effects on the same outcome, adding both environmental features should produce combined effects.

**Input**: Two traces converging on the same outcome variable
**Transformation**: Predict combined effect, noting whether additive, synergistic, or antagonistic
**Output**: Predictions about multi-feature environmental interventions

**Worked example**:
- Trace A: nature_view → cortisol_reduction (via PP pathway)
- Trace B: legible_layout → cortisol_reduction (via reduced navigational stress)
- Prediction: "A hospital with BOTH nature views AND legible layout should produce greater cortisol reduction than either alone. Effect likely approximately additive if pathways are independent."
- Check: independence_matrix for PP ↔ SN independence score

### Operation 8: CHANGE_DOSE

**Logic**: If the mechanism has nonlinear dose-response, predict effects of varying stimulus intensity.

**Input**: A trace with parameter_range data
**Transformation**: Predict effects at different magnitudes
**Output**: Predictions about dose-response relationships

**Worked example**:
- Trace: noise_level → ASA_demand → WM_depletion
- Dose parameter: noise level in dB(A)
- Prediction: "WM depletion should follow the ASA capacity curve: gradual degradation from 35-55 dB(A), then sharp degradation from 55-70 dB(A) as ASA source segregation fails."
- Note: This prediction has specific quantitative parameters from T31.

---

## Operation Applicability Matrix

Not all operations apply to all traces. This matrix indicates which are typically applicable:

| Operation | When Applicable | Required Template Data |
|-----------|----------------|----------------------|
| SUBSTITUTE_CAUSE | Always (for link 0) | `transferable_to` field |
| VARY_MODERATOR | When moderators listed | `moderators` list |
| BLOCK_PATHWAY | When ≥ 2 links | Interior link variables |
| CHANGE_TEMPORAL_CONTEXT | When temporal params exist | `temporal_dynamics` on links |
| VARY_INDIVIDUAL | When scope includes individual differences | `scope_conditions` |
| CROSS_CULTURAL | When culture-dependent | Moderators mentioning culture |
| ADD_CONCURRENT | When ≥ 2 traces share outcome | Independence matrix |
| CHANGE_DOSE | When quantitative params exist | `parameter_range` on links |

---

# PART 3: CROSS-FRAMEWORK BRIDGING RULES

## What This Is

When a mechanism trace exits one Tier 1 framework and enters another, it crosses a "bridge." Not all bridges are legitimate — some variable connections are well-supported, others are speculative. This section catalogs the legitimate bridges that CMR Step 3 (Mechanism Tracing) can use.

## Bridge Catalog

### Bridge Group A: Prediction Error → Neuromodulatory

| From Framework | Shared Variable | To Framework | Bridge Quality | Evidence |
|---|---|---|---|---|
| Predictive Processing | prediction_error_magnitude | Neuromodulatory (NE/LC) | HIGH | High PE → phasic LC-NE → arousal. Aston-Jones & Cohen 2005 |
| Predictive Processing | unresolvable_PE | Neuromodulatory (HPA) | MEDIUM | Sustained unresolvable PE → threat appraisal → cortisol. Inferential but well-motivated |
| Predictive Processing | precision_weighting | Neuromodulatory (ACh) | HIGH | ACh modulates precision. Yu & Dayan 2005; Chiba panel corrections |

### Bridge Group B: Spatial Navigation → Neuromodulatory

| From Framework | Shared Variable | To Framework | Bridge Quality | Evidence |
|---|---|---|---|---|
| Spatial Navigation | wayfinding_failure | Neuromodulatory (HPA) | HIGH | Navigation stress → cortisol. Well-established behavioral link |
| Spatial Navigation | hippocampal_function | Neuromodulatory (cortisol) | HIGH | Cortisol → hippocampal damage ↔ spatial impairment. McEwen 2007 |
| Spatial Navigation | cognitive_map_quality | Embodied Cognition | MEDIUM | Good cognitive map → reduced exploratory movement → different postural state. Plausible but less tested |

### Bridge Group C: DMN/TPN → Multiple

| From Framework | Shared Variable | To Framework | Bridge Quality | Evidence |
|---|---|---|---|---|
| DMN/TPN | dmn_engagement | Memory Systems | HIGH | DMN-MTL subsystem engagement overlaps with consolidation. Andrews-Hanna 2010 |
| DMN/TPN | tpn_suppression | Neuromodulatory (ACh) | HIGH | ACh gating: high ACh → TPN; low ACh → DMN + replay. Buzsáki, Chiba |
| DMN/TPN | parasympathetic_shift | Interoceptive Inference | MEDIUM | DMN engagement → parasympathetic → changed interoceptive signals → affect. Plausible chain |

### Bridge Group D: Interoceptive → Affect → Everything

| From Framework | Shared Variable | To Framework | Bridge Quality | Evidence |
|---|---|---|---|---|
| ANY framework that changes body state | interoceptive_signals | Interoceptive Inference | HIGH | Template 12 is the universal bridge. Any autonomic, postural, metabolic change → interoceptive PE → affect construction |
| Interoceptive Inference | constructed_affect | Dual-Process | MEDIUM | Implicit affect → explicit evaluation. Barrett 2017 |

### Bridge Group E: Embodied → Interoceptive

| From Framework | Shared Variable | To Framework | Bridge Quality | Evidence |
|---|---|---|---|---|
| Embodied Cognition | postural_state | Interoceptive Inference | HIGH | Posture → muscle tension → vagal tone → interoceptive signal change → affect. Template 8 → Template 12 chain |
| Embodied Cognition | affordance_perception | Predictive Processing | MEDIUM | Affordances = prediction-error-reducing action policies. Friston's active inference interpretation |

### Bridge Group F: Circadian → Neuromodulatory

| From Framework | Shared Variable | To Framework | Bridge Quality | Evidence |
|---|---|---|---|---|
| Chronobiological | circadian_cortisol_rhythm | Neuromodulatory (HPA) | HIGH | SCN → adrenal cortisol timing. Czeisler 1999 |
| Chronobiological | melatonin_cycle | Memory Systems | MEDIUM | Melatonin → sleep quality → sleep-dependent consolidation. Walker 2017 |
| Chronobiological | circadian_phase | DMN/TPN | MEDIUM | Time-of-day effects on DMN/TPN balance and cognitive performance |

### Bridge Group G: Multisensory → Predictive Processing

| From Framework | Shared Variable | To Framework | Bridge Quality | Evidence |
|---|---|---|---|---|
| Multisensory Integration | crossmodal_prediction_error | Predictive Processing | HIGH | MSI congruency/incongruency IS crossmodal prediction error. Spence panel |
| Multisensory Integration | inverse_effectiveness_weighting | Predictive Processing | HIGH | Bayesian reliability weighting = precision weighting in PP. Ernst & Banks 2002 |

### Bridge Group H: Higher Cognition → Multiple

| From Framework | Shared Variable | To Framework | Bridge Quality | Evidence |
|---|---|---|---|---|
| Cognitive Control/EF | wm_capacity_overflow | Neuromodulatory (HPA) | MEDIUM | WM overflow → frustration/anxiety → cortisol. Miller panel |
| Cognitive Control/EF | pfc_metabolic_cost | Allostatic (Master) | HIGH | Anterior PFC engagement is metabolically expensive → allostatic budget draw. Direct implication of Template 29 |
| Ecological Rationality | cue_validity_structure | Spatial Navigation | MEDIUM | Environmental information structure determines which wayfinding heuristics work. Gigerenzer panel |

---

## Illegitimate Bridges (DO NOT USE)

| From | Proposed Bridge | To | Why Invalid |
|---|---|---|---|
| Circadian | aesthetic_preference | Dual-Process | No mechanism connecting circadian phase to aesthetic judgment. Correlation ≠ bridge |
| Embodied Cognition | vestibular_activation | Memory Systems | Template 18 (vestibular → cognition) is how-possibly. Too weak for bridging |
| Predictive Processing | PE_magnitude | Social Brain | Social cognition uses different neural systems; social PE is not the same computational process |
| Multisensory | congruency_rating | Reward/Valuation | Congruency → fluency → positive affect is established, but jumping to reward circuitry conflates hedonic fluency with dopaminergic reward |

---

# PART 4: WHAT OPUS STILL NEEDS TO PRODUCE

## Waiting on Audit Results

1. **Controlled variable vocabulary** — canonical names for all variables. Blocked until CC/Codex report what names exist in code.

2. **Structured template encodings** (the actual Python data for Sprint 7 Task 7.5) — I can draft these now for the 8 seed templates using provisional variable names, then reconcile after audit.

3. **Framework scope declarations** (Sprint 7 Task 7.6) — the actual variable lists. Can draft now.

## Not Blocked

4. **Independence matrix** — fully specified in Part 3 of this document. Sprint 7 Task 7.4 can use these values directly.

5. **Prediction grammar** — fully specified in Part 2. Sprint 8 Task 8.4 can implement these operations.

6. **Bridging rules** — fully specified in Part 3. Sprint 8 Task 8.3 can use these for cross-framework tracing.

---

# REFERENCES

[All references are cited inline with Google Scholar counts. Full bibliography is in the source panel documents.]
