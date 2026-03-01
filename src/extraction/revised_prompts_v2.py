#!/usr/bin/env python3
"""
REVISED EXTRACTION PROMPTS — V2.0 (Consolidated)
=================================================

Complete drop-in replacement for PROMPT_MAP in gemini_extraction_queue.py.

Consolidates V1.0 (graceful degradation, terminology bridge, negative examples)
with V1.1 (166-template matching guide, 15 article sub-types in 5 families,
provenance depth, family-specific field contracts).

Changes from original pipeline:
  1. Template matching guide: 166 templates across 10 T1 frameworks
  2. Article type taxonomy: 15 sub-types in 5 families (per article_type_contract.py)
  3. Graceful degradation: 10 explicit rules for missing/partial statistics
  4. Negative examples: What NOT to extract
  5. Domain terminology bridge: 20 common field-specific terms mapped
  6. Provenance depth: Every finding tagged with source location
  7. All prompts use "findings" as canonical key (not pooled_effects/themes/propositions)
  8. Lightweight classification prompt for pre-flight gate

Author: Opus (Architecture)
Date: 2026-02-24
Sprint: Pipeline Repair (consolidated)
"""

# ═══════════════════════════════════════════════════════════════════════════
# PROMPT BASE — shared across all article types
# ═══════════════════════════════════════════════════════════════════════════

PROMPT_BASE = """You are extracting structured data from a scientific paper about the built environment's effects on human cognition, emotion, behavior, and health.

Return ONLY valid JSON. No explanations, no markdown code blocks, no commentary.
If a field is not available in the paper, use null — do NOT invent data.

═══════════════════════════════════════════════════════════════
PART 1: TEMPLATE MATCHING GUIDE (166 templates, 10 frameworks)
═══════════════════════════════════════════════════════════════

When you extract findings, populate "theory_links" with relevant framework codes
and "template_ids" with specific template IDs when the match is clear.

PP — PREDICTIVE PROCESSING (58 templates)
Assign when: prediction error, surprise, expectation violation, Bayesian brain, active inference, free energy, environmental statistics, processing fluency, gist perception, 1/f spectra, fractal dimension, habituation/novelty, cultural priors, controllability, aesthetic complexity.
Key template clusters:
  Core visual: T1 (scene statistics → PE), T2 (complexity Goldilocks/inverted-U), T22 (rapid gist → contextual framing)
  Active inference: T21 (controllability → free energy), PP4 (expected free energy → action)
  Cultural: T15 (cultural ecology → preference set-points)
  Visual form: VF1 (contour curvature PE), VF2 (visual rhythm/scanning), VF3 (spatial proportions/ceiling height)
  Color: COL1 (chromatic PE), COL2 (color-arousal modulation)
  Thermal: MAT2 (thermal adaptive PE), T74 (adaptive thermal comfort/allesthesia)
  Lighting: L1 (luminance contrast PE)
  Olfactory: OLF1 (olfactory PE at transitions)
  Nature: T13 (nature multipath convergence), VIEW1 (nature view multi-channel)
  Implicit-explicit: T_IE_001–T_IE_012 (activity-frame complexity, expertise divergence, semantic override, bridge mechanism, cost-gated engagement, placebo architecture, café paradox, trauma-space, McMansion effect, wayfinding goal-states, sacred space, habituation breakage)
  Music/acoustic: BRECVEMA brainstem/contagion/expectancy/aesthetic templates (M7, M8, M9, M10, M16)
  Dose-response modifiers: AX2 (habituation), AX7 (dose-response), AX9 (cultural modulation), AX12 (VR limitations)
  Cross-framework: ENCLOSURE_SAFETY (enclosure → safety perception), TP1 (motor PE), SC3 (architectural promenade temporal PE)
  Performance: T20 (environmental features → cognitive resource modulation → task performance)

SN — SPATIAL NAVIGATION (13 templates)
Assign when: wayfinding, cognitive maps, place/grid/boundary cells, hippocampus, space syntax (integration, connectivity, intelligibility), spatial memory, legibility (Lynch), isovist analysis, visibility graphs, route learning, exploration.
Key templates:
  Core: T3 (layout → cognitive map), T24 (path → theta sequences), T14 (navigation-stress vicious cycle)
  Space syntax: SC1 (integration as inverse PE), SC2 (isovist visual prediction range)
  Memory: SCM2 (context-dependent encoding), SN1 (boundaries → spatial chunking), SN2 (vista space)
  Social-spatial: SC4 (integration → encounter frequency), XSAD1 (social affordances)
  Navigation modes: T43 (model-based vs. model-free arbitration)
  Incubation: CREA3 (movement, transition, soft fascination → creative mind-wandering)

DP — DUAL-PROCESS EVALUATION (3 templates)
Assign when: System 1/System 2, automatic vs. controlled processing, implicit evaluation, fluency effects, first impressions, approach/avoidance, aesthetic judgment speed.
Key templates:
  T9 (environmental features → rapid implicit evaluation → affective response)
  DP2 (automatic response → effortful override → modified behavior)
  CROSS_PROACTIVE_REACTIVE (proactive-reactive control and predictability)

DT — DMN/TPN DYNAMICS (15 templates)
Assign when: default mode network, task-positive network, mind-wandering, attention restoration (ART), directed attention fatigue, cognitive fatigue, mental rest, salience network, creative ideation networks, aesthetic vs. utilitarian emotion.
Key templates:
  Core restoration: T4 (attentional demand → DMN suppression → fatigue), T16 (restoration timecourse), T27 (low-demand → DMN maintenance)
  Attention: DT1 (salience → network switching), DT2 (directed attention fatigue/restoration), AX10 (attention mediation)
  Creativity: CREA1 (DMN-executive coupling), CREA2 (processing style modulation), CREA3 (incubation architecture), T61 (incubation walking/nature)
  Individual differences: AX8 (trait → differential sensitivity → response variation)
  Music: M14 (aesthetic vs. utilitarian emotions)
  Control: T38 (environmental task structure → cognitive control hierarchy)

NM — NEUROMODULATORY SYSTEMS (18 templates)
Assign when: cortisol, dopamine, serotonin, norepinephrine, acetylcholine, oxytocin, HPA axis, vagal tone, stress hormones, reward, arousal, allostatic load, safety signaling, social bonding, threat detection, wanting vs. liking.
Key templates:
  Stress: NM8 (threat → amygdala → HPA → cortisol), T6 (chronic cortisol → hippocampal damage), AX4 (control × stress interaction)
  Reward: NM1 (reward PE), NM2 (novelty → dopamine → exploration), NM4 (sustained incentive salience)
  Arousal: NM5 (LC-NE explore-exploit), NM6 (cholinergic precision weighting)
  Mood: NM7 (serotonergic mood valence), NM9 (safety signaling → vmPFC-amygdala inhibition)
  Social: NOS3 (oxytocin → prosocial behavior), NVR1 (vagal regulation/social engagement), T52 (social enrichment)
  Allostatic: T29 (cumulative allostatic cost master template), NSIA1 (social isolation allostatic load)
  Proxemics: PPA1 (proxemic PE — interpersonal distance)
  Stress recovery: SRT1 (restorative environment → physiological normalization)
  Chronic: AX11 (acute vs. chronic pathway → different outcomes)

IC — INTEROCEPTIVE / CONSTRUCTIONIST AFFECT (15 templates)
Assign when: interoception, body budget, allostasis, constructed emotion (Barrett), thermal comfort as affect, olfactory hedonic evaluation, social pain, embodied affect, acoustic emotion mapping, privacy regulation.
Key templates:
  Core: T12 (interoceptive PE → affect construction), IC2 (body budget prediction), T7 (allostatic anticipation → wellbeing)
  Thermal: IC_THERMAL_COMFORT (thermoregulatory interoception)
  Olfactory: T53 (olfactory-limbic processing)
  Social: CSMP1 (social mirror/embodied presence), CSAR1 (social affordance reading)
  Privacy/territory: PGR1 (architectural privacy gradient), TAS1 (territorial affordance)
  Music: BRECVEMA_EXPECTANCY, BRECVEMA_MULTI_MECHANISM, M15 (pleasurable sadness)
  Acoustic: ACOUSTIC_EMOTION_MAPPING (acoustic features → affect dimensions)
  Awe: AX3/AX3_SMALL_SELF (small self, vastness)

MS — MEMORY SYSTEMS (15 templates)
Assign when: episodic/semantic/working memory, memory consolidation, place-dependent memory, encoding/retrieval, pattern separation/completion, schema effects, reconsolidation, doorway effect, sharp-wave ripples, systems consolidation.
Key templates:
  Encoding: EHE1 (hippocampal relational binding), EPEP1 (PE-dependent encoding strength), ESE1 (schema-dependent encoding), EPSC1 (pattern separation/completion)
  Consolidation: MCR1 (DMN consolidation in restorative environments), MRR2 (ripple replay), ESC1 (systems consolidation)
  Working memory: T36 (WM load → overflow → performance loss), MS2 (complexity → WM load)
  Reconsolidation: ER1 (reconsolidation in spatial context)
  Boundaries: TEB1 (doorway effect — threshold → episodic boundary)
  Context: T10 (restorative → DMN → consolidation), T35 (olfactory → context-memory binding)
  Acoustic: T32 (chronic acoustic → subcortical plasticity)
  Music: BRECVEMA_MEMORY (cue → retrieval → emotion), BRECVEMA_RHYTHMIC (entrainment)

EC — EMBODIED COGNITION (8 templates)
Assign when: affordances, motor simulation, enactivism, sensorimotor contingencies, posture, vestibular processing, haptic exploration, motor prediction, body-environment coupling, C-tactile touch.
Key templates:
  Core: T8 (affordances → posture → autonomic), T18 (vertical → vestibular → cognitive style), T28 (legibility → cognitive offloading)
  Touch: HSM1 (surface materials → haptic affect), CAT1 (C-tactile affective touch)
  Sensorimotor: EC2 (action-perception coupling), TP1 (motor PE from surfaces/spatial demands)
  Music: M6 (music → visual imagery → emotion)

CB — CHRONOBIOLOGICAL REGULATION (10 templates)
Assign when: circadian rhythms, melatonin, light exposure timing, CCT, melanopic lux, sleep quality, seasonal effects, chronotype, non-visual photoreception, dynamic lighting.
Key templates:
  Core: T30/CLE1/CAR1 (light → circadian entrainment), L2 (circadian regulation via non-visual)
  Lighting detail: L3 (daylight multi-channel), L4 (CCT as temporal/ecological signal), L5 (dynamic light temporal PE)
  Sleep: CSA2 (evening light → melatonin suppression → sleep)
  Music: M11 (auditory-motor plasticity), M13 (neural music-emotion architecture)

MSI — MULTISENSORY INTEGRATION (11 templates)
Assign when: cross-modal effects, audiovisual interaction, sensory congruence, multisensory binding, soundscape-visual, material perception (visual-haptic), spatial audio, inverse effectiveness.
Key templates:
  Congruence: MCP1 (crossmodal congruency → fluency → affect), CC1 (multi-sensory spatial coherence)
  Inverse effectiveness: MIE2 (degraded channel → enhanced compensation)
  Materials: NMC1 (natural material multi-modal convergence), MII1 (multi-modal material identity via Bayesian cue combination), MATD1 (material aging/patina), MCC1 (material-cultural conditioning)
  Audio: AUD_SCENE_ANALYSIS (scene complexity → cognitive load), AUD_REVERBERATION (RT60 → spatial impression), AUD_FRACTAL (1/f soundscape), MSI2 (auditory spatial cues)

ALSO ASSIGN these domain-level theories when relevant:
  ART: Attention Restoration Theory (Kaplan) — soft fascination, being away, extent, compatibility
  SRT: Stress Recovery Theory (Ulrich) — nature reduces physiological stress
  Biophilia: Innate affiliation with nature (Wilson, Kellert)
  Prospect-Refuge: Safe vantage points, views, enclosure (Appleton)
  Privacy Regulation: Personal space control, crowding, territoriality (Altman)

═══════════════════════════════════════════════════════════════
PART 2: CNFA DOMAIN CLASSIFICATION
═══════════════════════════════════════════════════════════════

Classify the paper's environmental features into one or more domains:

A1_Materials: wood, concrete, stone, brick, biophilic materials, texture, material warmth, natural vs synthetic, patina, aging
A2_Spatial_Scale: ceiling height, room volume, spaciousness, openness, perceived size, proportion, scale, vastness, awe
A3_Spatial_Config: layout, floorplan, wayfinding, circulation, connectivity, space syntax, visibility graphs, legibility, isovist, integration
A4_Light: daylight, illuminance, CCT, glare, window views, daylighting factor, circadian lighting, melanopic lux, dynamic lighting, luminance contrast
A5_Acoustic: noise, reverberation (RT60), soundscape, speech privacy, background noise, sound masking, auditory scene complexity, music
A6_Visual_Form: color, pattern, fractal dimension, curvature, visual complexity, symmetry, ornamentation, aesthetic qualities, contour, rhythm
A7_Haptic_Thermal: temperature, thermal comfort, touch, surface feel, PMV/PPD, radiant heat, C-tactile, material haptics
A8_Social: privacy, crowding, collaboration, density, personal space, territoriality, social interaction, proxemics, encounter frequency
A9_Task_Cognition: attention, memory, creativity, problem-solving, cognitive performance, productivity, learning, incubation, mind-wandering
A10_Temporal: exposure duration, adaptation, seasonal, time-of-day, longitudinal, circadian, habituation, dose-response, promenade/sequence

═══════════════════════════════════════════════════════════════
PART 3: DOMAIN TERMINOLOGY BRIDGE
═══════════════════════════════════════════════════════════════

Papers often use field-specific vocabulary. Map to extraction fields:

When the paper says:                    Extract as:
"biophilic design elements"          →  antecedent: specify which elements (plants, water, natural materials, daylight, etc.)
"perceived restorativeness"          →  consequent: perceived restorativeness (specify: PRS, if subscale given note it)
"environmental satisfaction"         →  consequent: environmental satisfaction (specify measure: BUS, POE, Likert scale, etc.)
"physiological stress markers"       →  consequent: specify exactly (cortisol, HRV, skin conductance, blood pressure, etc.)
"spatial configuration"              →  antecedent: specify exactly (open plan, cellular, hybrid, integration value, connectivity, etc.)
"cognitive performance"              →  consequent: specify exactly (Stroop accuracy, d2 test, digit span, reading comprehension, etc.)
"thermal comfort"                    →  consequent: specify (PMV, PPD, thermal sensation vote, thermal acceptability, etc.)
"visual comfort"                     →  consequent: specify (glare rating, visual discomfort frequency, luminance ratio, etc.)
"acoustic comfort"                   →  consequent: specify (speech intelligibility, STI, annoyance rating, noise sensitivity, etc.)
"IEQ" / "indoor environmental quality" → note: composite — extract findings for EACH separate dimension
"occupant satisfaction"              →  consequent: specify which satisfaction (thermal, acoustic, lighting, overall, layout, etc.)
"subjective wellbeing"               →  consequent: specify measure (WEMWBS, SF-36, WHO-5, life satisfaction, positive affect, etc.)
"stress recovery"                    →  consequent: specify (cortisol decline rate, HRV recovery, self-reported relaxation, etc.)
"creative thinking"                  →  consequent: specify (RAT, AUT, divergent thinking score, idea fluency, originality, etc.)
"preference"                         →  consequent: specify (aesthetic preference rating, willingness to return, choice behavior, etc.)
"view quality"                       →  antecedent: specify (nature view %, view content, sky visibility, view layers, etc.)
"soundscape"                         →  antecedent: specify (sound level, frequency spectrum, eventfulness, pleasantness, natural/technological/human)
"prospect-refuge"                    →  antecedent: specify (visual openness, enclosure degree, overhead coverage, back-wall distance)
"complexity"                         →  antecedent: specify (fractal dimension, information rate, edge density, element count, color variety)

═══════════════════════════════════════════════════════════════
PART 4: STATISTICS — GRACEFUL DEGRADATION RULES
═══════════════════════════════════════════════════════════════

EXTRACT EVERY FINDING, even if statistics are incomplete:

RULE 1: p-value but no effect size → extract with effect_size: null
RULE 2: effect size but no p-value → extract with p_value: null
RULE 3: only "p < .05" or "p < .01" → use p_value: "<0.05" or "<0.01"
RULE 4: confidence interval but no p-value → extract CI, p_value: null
RULE 5: odds/hazard/risk ratio → effect_size with type "OR"/"HR"/"RR"
RULE 6: Bayes factor or credible interval → effect_size for BF, type "BF10"/"BF01", p_value: null
RULE 7: beta weights from regression → effect_size for beta, type "beta"
RULE 8: R² or adjusted R² → type "R_squared"
RULE 9: only "significant"/"not significant" with no numbers → p_value: "significant" or "ns", effect_size: null
RULE 10: antecedent + consequent + direction but NO statistics → still extract, p_value: null, effect_size: null

DO NOT skip a finding for lack of statistics. Partial > nothing.
DO NOT invent statistics. DO NOT guess. DO NOT combine findings from different analyses.

═══════════════════════════════════════════════════════════════
PART 5: WHAT NOT TO EXTRACT (NEGATIVE EXAMPLES)
═══════════════════════════════════════════════════════════════

Do NOT extract as findings:
- Citations of OTHER papers' results (e.g., "Smith (2019) found...") unless replicated here
- Hypothesized relationships in the Introduction that are NOT tested
- Descriptive demographics unless age/gender is an independent variable
- Manipulation checks (e.g., "bright room rated as brighter")
- Statistical artifacts of the analytic method
- Pilot study results unless treated as substantive by the authors
- Individual study results from a review — extract only synthesized conclusions

Do NOT extract as theory_links:
- Frameworks merely mentioned in the literature review without guiding hypotheses
- Theory links requiring long inferential chains you're constructing — only assign when the paper makes the connection or it is direct and obvious

═══════════════════════════════════════════════════════════════
PART 6: PROVENANCE DEPTH
═══════════════════════════════════════════════════════════════

Tag each finding with where in the paper it comes from:

  "abstract"       — from abstract text only (least reliable for specifics)
  "caption"        — from figure or table captions
  "table"          — from table body/statistical rows (most reliable for stats)
  "section"        — from section body (methods/results/discussion)
  "fulltext_multi" — corroborated across multiple sections (highest confidence)

Use the MOST SPECIFIC provenance. Table > text for statistics.
"""


# ═══════════════════════════════════════════════════════════════════════════
# EXTRACTION PROMPTS BY FAMILY
# ═══════════════════════════════════════════════════════════════════════════
#
# Aligned with article_type_contract.py:
#   Empirical family:   empirical_v2, observational_field, case_study, mixed_methods
#   Synthesis family:   meta_analysis, systematic_review, narrative_review
#   Theoretical family: theoretical, conceptual_framework, thought_piece
#   Qualitative family: interview_study, ethnographic, grounded_theory, phenomenological
#   Unknown:            unknown


# ---------------------------------------------------------------------------
# EMPIRICAL FAMILY
# ---------------------------------------------------------------------------

EMPIRICAL_PROMPT = PROMPT_BASE + """
═══════════════════════════════════════════════════════════════
EXTRACTION: EMPIRICAL FAMILY
(empirical_v2 | observational_field | case_study | mixed_methods)
═══════════════════════════════════════════════════════════════

Required fields: research_question, design_type, participants,
stimuli_or_exposures, measures, findings, limitations

Return this JSON:
{
  "article_type": "empirical_v2|observational_field|case_study|mixed_methods",
  "article_family": "empirical",
  "title": "exact paper title",
  "authors": "First Author et al., Year",

  "research_question": "the paper's central research question(s)",
  "design_type": "between_subjects|within_subjects|mixed_factorial|cross_sectional|longitudinal|quasi_experiment|pre_post|case_control|cohort|POE|other",

  "participants": {
    "n": number or null,
    "description": "demographics (age range, country, setting)",
    "recruitment": "how recruited if stated"
  },

  "stimuli_or_exposures": [
    {
      "type": "photograph|rendering|VR|video|physical_space|audio|plan_drawing|model|other",
      "description": "BE SPECIFIC",
      "n_stimuli": number or null,
      "source": "Figure N or Methods"
    }
  ],

  "measures": [
    {
      "construct": "what was measured",
      "instrument": "specific instrument/scale name",
      "type": "physiological|behavioral|self_report|cognitive|performance|neural|observational"
    }
  ],

  "findings": [
    {
      "id": 1,
      "antecedent": "environmental feature — BE SPECIFIC (e.g., 'ceiling height 3.0m vs 2.4m', NOT 'ceiling height')",
      "consequent": "human response — BE SPECIFIC (e.g., 'RAT score', NOT 'creativity')",
      "direction": "increase|decrease|no_effect|mixed|curvilinear",
      "claim_type": "causal|associational|moderated|mediated|null",
      "measure_type": "physiological|behavioral|self_report|cognitive|performance|neural|observational",
      "p_value": "exact (e.g. '0.003') or threshold ('<0.05') or 'significant'/'ns' or null",
      "effect_size": number or null,
      "effect_size_type": "Cohen_d|r|eta_squared|partial_eta_squared|beta|R_squared|OR|HR|RR|BF10|Cramers_V|omega_squared|null",
      "test_statistic": "e.g. 'F(2,45)=3.21' or 't(98)=2.45' or null",
      "sample_size": number if different from overall N,
      "confidence_interval": [lower, upper] or null,
      "theory_links": ["PP", "SN", "DP", "DT", "NM", "IC", "MS", "EC", "CB", "MSI", "ART", "SRT", "Biophilia", "Prospect-Refuge", "Privacy"],
      "template_ids": ["T1", "VF2", "AX4", etc. — specific template codes from Part 1],
      "mechanism": "theoretical explanation if proposed, null otherwise",
      "moderators_reported": ["moderating variables"],
      "provenance_depth": "abstract|caption|table|section|fulltext_multi",
      "source": "Table X, Figure Y, or 'p.N'",
      "quote": "exact supporting quote (max 120 chars)"
    }
  ],

  "mechanisms": ["proposed mechanisms or theoretical explanations"],
  "moderators": ["moderating variables examined"],
  "implementation_implications": ["practical implications stated by authors"],

  "domains": ["A1_Materials", "A4_Light", etc.],
  "overall_theory_links": ["frameworks guiding hypotheses — NOT just mentioned in lit review"],

  "tables": [
    {
      "table_id": "Table 1",
      "description": "what the table shows",
      "key_stats": ["F(2,45)=3.2, p<.05", "R²=.24"],
      "n_findings_extracted_from": number
    }
  ],

  "limitations": ["stated by the authors"]
}

CRITICAL RULES:
1. SPECIFICITY: Extract exact operationalizations, not vague constructs.
2. EVERY ANALYSIS = A FINDING: Each regression predictor, each ANOVA effect/interaction, each correlation pair.
3. NULL RESULTS MATTER: "No effect of X on Y" with p=.34 → extract with direction: "no_effect", claim_type: "null".
4. TABLES ARE PRIMARY: Read every table. Cross-check text against tables.
5. MEDIATION: Extract (a) X→Y direct, (b) X→M, (c) M→Y, (d) indirect effect. MODERATION: interaction as separate finding.
6. template_ids: Only assign when finding directly matches the template's causal chain. If unsure → empty [].
"""


# ---------------------------------------------------------------------------
# SYNTHESIS FAMILY
# ---------------------------------------------------------------------------

SYNTHESIS_PROMPT = PROMPT_BASE + """
═══════════════════════════════════════════════════════════════
EXTRACTION: SYNTHESIS FAMILY
(meta_analysis | systematic_review | narrative_review)
═══════════════════════════════════════════════════════════════

Required fields: review_question, inclusion_exclusion_criteria,
evidence_base_summary, synthesis_conclusions, evidence_gaps

Return this JSON:
{
  "article_type": "meta_analysis|systematic_review|narrative_review",
  "article_family": "synthesis",
  "title": "paper title",
  "authors": "First Author et al., Year",

  "review_question": "the central review question",
  "inclusion_exclusion_criteria": "brief summary of what was included/excluded",

  "evidence_base_summary": {
    "n_studies": number or null,
    "total_n": combined sample or null,
    "search_databases": ["PubMed", "Scopus", etc.],
    "date_range": "search date range",
    "review_protocol": "PRISMA|PROSPERO|Cochrane|other|not_specified"
  },

  "findings": [
    {
      "id": 1,
      "antecedent": "factor/intervention — BE SPECIFIC",
      "consequent": "outcome — BE SPECIFIC",
      "direction": "increase|decrease|no_effect|mixed",
      "evidence_strength": "strong|moderate|weak|inconsistent",
      "claim_type": "pooled_effect|synthesized|vote_count|narrative",
      "effect_size": number or null,
      "effect_size_type": "SMD|d|g|r|OR|RR|HR|null",
      "confidence_interval": [lower, upper] or null,
      "p_value": "value or null",
      "k": number of studies for this effect or null,
      "n_total": combined N for this effect or null,
      "I_squared": heterogeneity % or null,
      "tau_squared": between-study variance or null,
      "theory_links": ["framework codes"],
      "template_ids": ["template IDs"],
      "key_citations": ["Author (Year)"],
      "provenance_depth": "abstract|table|section|fulltext_multi",
      "source": "Table/Figure/section",
      "quote": "supporting synthesis statement (max 120 chars)"
    }
  ],

  "synthesis_conclusions": ["main synthesized conclusions"],
  "evidence_gaps": ["identified gaps"],

  "risk_of_bias_assessment": "method and finding or null",
  "heterogeneity_sources": ["identified sources of heterogeneity"],
  "publication_bias": "assessment method and result or null",

  "moderators": [
    {
      "variable": "name",
      "effect": "description of moderation",
      "significant": true|false,
      "subgroup_effects": "brief summary"
    }
  ],

  "domains": ["CNFA domain codes"],
  "overall_theory_links": ["frameworks"],
  "limitations": ["stated limitations"]
}

RULES:
1. Each forest plot / pooled effect = separate finding.
2. Subgroup analyses for same outcome = separate findings.
3. Use "findings" as key — NOT "pooled_effects".
4. Extract synthesized conclusions, NOT individual study results.
5. Always extract I² and k when reported.
"""


# ---------------------------------------------------------------------------
# THEORETICAL FAMILY
# ---------------------------------------------------------------------------

THEORETICAL_PROMPT = PROMPT_BASE + """
═══════════════════════════════════════════════════════════════
EXTRACTION: THEORETICAL FAMILY
(theoretical | conceptual_framework | thought_piece)
═══════════════════════════════════════════════════════════════

Required fields: central_proposition, concept_definitions,
argument_structure, mechanism_or_causal_logic,
testable_hypotheses_or_predictions

Return this JSON:
{
  "article_type": "theoretical|conceptual_framework|thought_piece",
  "article_family": "theoretical",
  "title": "paper title",
  "authors": "First Author et al., Year",

  "central_proposition": "the paper's main claim — one clear sentence",

  "concept_definitions": [
    {"name": "concept", "definition": "as defined in this paper"}
  ],

  "argument_structure": "brief description of how the argument is built",
  "mechanism_or_causal_logic": "the proposed causal mechanism(s)",

  "findings": [
    {
      "id": 1,
      "antecedent": "proposed cause/factor — BE SPECIFIC",
      "consequent": "proposed effect/outcome — BE SPECIFIC",
      "direction": "increase|decrease|modulates",
      "claim_type": "theoretical_proposition",
      "mechanism": "how/why this link works — CRITICAL for theoretical papers",
      "theory_links": ["framework codes"],
      "template_ids": ["template IDs"],
      "testable": true|false,
      "empirical_support_cited": "brief note on cited evidence, null if purely theoretical",
      "provenance_depth": "section|fulltext_multi",
      "source": "section reference",
      "quote": "supporting text (max 120 chars)"
    }
  ],

  "testable_hypotheses_or_predictions": [
    "specific testable predictions derived from the theory"
  ],

  "bridge_warrants": ["connections between this theory and other frameworks"],
  "methodological_critiques": ["critiques of existing methods if present"],

  "model_structure": "description of the overall model/framework architecture if proposed",

  "domains": ["CNFA domain codes"],
  "overall_theory_links": ["frameworks"],
  "limitations": ["boundary conditions or acknowledged limitations"]
}

RULES:
1. Use "findings" as key — NOT "propositions".
2. testable = true if the paper suggests how the proposition could be tested.
3. mechanism is the MAIN contribution — extract thoroughly.
4. bridge_warrants: connections this theory makes to other frameworks (valuable for downstream BN).
"""


# ---------------------------------------------------------------------------
# QUALITATIVE FAMILY
# ---------------------------------------------------------------------------

QUALITATIVE_PROMPT = PROMPT_BASE + """
═══════════════════════════════════════════════════════════════
EXTRACTION: QUALITATIVE FAMILY
(interview_study | ethnographic | grounded_theory | phenomenological)
═══════════════════════════════════════════════════════════════

Required fields: research_focus, sample_context, data_collection_method,
coding_or_analysis_approach, themes_or_constructs,
supporting_quotes_or_evidence_snippets, transferability_limits

Return this JSON:
{
  "article_type": "interview_study|ethnographic|grounded_theory|phenomenological",
  "article_family": "qualitative",
  "title": "paper title",
  "authors": "First Author et al., Year",

  "research_focus": "what the study set out to understand",

  "sample_context": {
    "n_participants": number,
    "description": "who, where, how recruited",
    "setting": "the environment/context studied"
  },

  "data_collection_method": "semi-structured interviews|unstructured interviews|focus groups|participant observation|photo elicitation|walking interviews|other",
  "coding_or_analysis_approach": "thematic analysis|grounded theory coding|IPA|framework analysis|content analysis|narrative analysis|other",

  "findings": [
    {
      "id": 1,
      "antecedent": "contributing environmental factor — or theme name if no clear antecedent",
      "consequent": "experiential outcome — or null if purely descriptive",
      "direction": "increase|decrease|mixed|descriptive",
      "claim_type": "qualitative_theme",
      "theme_name": "theme label as the authors use it",
      "description": "what this theme encompasses",
      "theory_links": ["framework codes"],
      "template_ids": ["template IDs"],
      "supporting_quotes": ["participant quote 1 (max 100 chars)", "quote 2"],
      "saturation": "saturated|emerging|limited|not_reported",
      "provenance_depth": "section|fulltext_multi",
      "source": "section reference"
    }
  ],

  "themes_or_constructs": ["list of ALL identified themes"],
  "supporting_quotes_or_evidence_snippets": ["key participant quotes that anchor major claims"],

  "derived_hypotheses": ["testable hypotheses the authors propose"],
  "mechanism_candidates": ["proposed mechanisms connecting themes to outcomes"],
  "transferability_limits": ["contexts where findings may/may not apply"],

  "domains": ["CNFA domain codes"],
  "overall_theory_links": ["frameworks"],
  "limitations": ["stated limitations"]
}

RULES:
1. Use "findings" as key — NOT "themes".
2. Map themes to antecedent → consequent where data supports it.
3. When purely descriptive → direction: "descriptive", consequent: null.
4. supporting_quotes = actual participant words, NOT authors' interpretations.
"""


# ---------------------------------------------------------------------------
# METHODS PROMPT
# ---------------------------------------------------------------------------

METHODS_PROMPT = PROMPT_BASE + """
═══════════════════════════════════════════════════════════════
EXTRACTION: METHODS PAPER
(instrument | protocol | guidelines | scale_development | validation)
═══════════════════════════════════════════════════════════════

Return this JSON:
{
  "article_type": "methods",
  "article_family": "methods",
  "title": "paper title",
  "authors": "First Author et al., Year",

  "method_type": "instrument|protocol|guidelines|scale_development|validation|simulation|framework",
  "target_construct": "what it measures or does",

  "findings": [
    {
      "id": 1,
      "antecedent": "method/instrument component",
      "consequent": "what it measures or enables",
      "direction": "descriptive",
      "claim_type": "methodological",
      "validation_evidence": "how validated if reported",
      "theory_links": ["framework codes"],
      "template_ids": ["template IDs"],
      "provenance_depth": "section|table",
      "source": "section reference"
    }
  ],

  "components": [
    {"name": "component", "description": "what it does", "validation": "how validated or null"}
  ],

  "psychometric_properties": {
    "reliability": "Cronbach's alpha, test-retest, or description — null if not reported",
    "validity": "convergent, discriminant, or description — null if not reported"
  },

  "recommended_use": "how authors suggest using the instrument/method",
  "domains": ["CNFA domain codes"],
  "overall_theory_links": ["frameworks"],
  "limitations": ["stated limitations"]
}
"""


# ---------------------------------------------------------------------------
# UNKNOWN / PRE-FLIGHT CLASSIFICATION+EXTRACTION
# ---------------------------------------------------------------------------

UNKNOWN_PROMPT = PROMPT_BASE + """
═══════════════════════════════════════════════════════════════
EXTRACTION: UNKNOWN ARTICLE TYPE — CLASSIFY + EXTRACT
═══════════════════════════════════════════════════════════════

The article type has not been pre-classified. First classify, then extract.

Return this JSON:
{
  "detected_article_type": "empirical_v2|observational_field|case_study|mixed_methods|meta_analysis|systematic_review|narrative_review|theoretical|conceptual_framework|thought_piece|interview_study|ethnographic|grounded_theory|phenomenological|methods|other",
  "detected_family": "empirical|synthesis|theoretical|qualitative|methods|unknown",
  "classification_confidence": 0.0 to 1.0,
  "classification_signals": ["specific evidence — page numbers, section headers, methodological details"],

  "title": "paper title",
  "authors": "First Author et al., Year",

  "findings": [
    {
      "id": 1,
      "antecedent": "factor/cause — BE SPECIFIC",
      "consequent": "outcome/effect — BE SPECIFIC",
      "direction": "increase|decrease|no_effect|mixed|unclear",
      "claim_type": "causal|associational|moderated|theoretical_proposition|qualitative_theme|synthesized|methodological",
      "evidence_type": "statistical|cited|claimed|theoretical|qualitative",
      "p_value": "value or null",
      "effect_size": number or null,
      "theory_links": ["framework codes"],
      "template_ids": ["template IDs"],
      "provenance_depth": "abstract|caption|table|section|fulltext_multi",
      "source": "section/table reference",
      "quote": "supporting text (max 120 chars)"
    }
  ],

  "domains": ["CNFA domain codes"],
  "overall_theory_links": ["frameworks"],
  "limitations": ["stated limitations"],
  "minimum_safe_summary": "Q1 (core claim), Q4 (key findings), Q5 (limitations) — one paragraph"
}

RULES:
1. classification_signals must cite SPECIFIC evidence (page, section, method details).
2. Attempt antecedent → consequent mapping even for unfamiliar types.
3. minimum_safe_summary: always provide this as fallback even if extraction is partial.
"""


# ---------------------------------------------------------------------------
# LIGHTWEIGHT CLASSIFICATION PROMPT (pre-flight, intro+conclusion pages only)
# ---------------------------------------------------------------------------

CLASSIFICATION_PROMPT = """You are classifying a scientific paper about the built environment.
Based on the pages shown (typically introduction + conclusion), determine the article type.

Return ONLY this JSON — no other text:
{
  "article_type": "empirical_v2|observational_field|case_study|mixed_methods|meta_analysis|systematic_review|narrative_review|theoretical|conceptual_framework|thought_piece|interview_study|ethnographic|grounded_theory|phenomenological|methods|other",
  "article_family": "empirical|synthesis|theoretical|qualitative|methods|unknown",
  "confidence": 0.0 to 1.0,
  "signals": ["specific evidence (e.g., 'Abstract says N=240 between-subjects experiment', 'PRISMA diagram on p.3')"],
  "has_empirical_findings": true|false,
  "has_statistical_tables": true|false,
  "primary_domain": "A1_Materials|A2_Spatial_Scale|A3_Spatial_Config|A4_Light|A5_Acoustic|A6_Visual_Form|A7_Haptic_Thermal|A8_Social|A9_Task_Cognition|A10_Temporal|multiple|unclear"
}

ARTICLE TYPE GUIDE:

EMPIRICAL: empirical_v2 (controlled experiment), observational_field (field study, POE, cross-sectional survey, cohort), case_study (one/few cases, design rationale), mixed_methods (quant + qual combined)
SYNTHESIS: meta_analysis (forest plots, pooled effects, I², PRISMA), systematic_review (systematic search, inclusion criteria, no pooling), narrative_review (literature overview, no systematic search)
THEORETICAL: theoretical (formal theory/propositions), conceptual_framework (conceptual model, taxonomy), thought_piece (essay, commentary, opinion)
QUALITATIVE: interview_study (interviews, coding, quotes), ethnographic (fieldwork, observation), grounded_theory (constant comparison, saturation), phenomenological (lived experience, essence)
"""


# ═══════════════════════════════════════════════════════════════════════════
# PROMPT MAP — maps article types to complete prompts
# ═══════════════════════════════════════════════════════════════════════════

PROMPT_MAP = {
    # Empirical family
    "empirical": EMPIRICAL_PROMPT,
    "empirical_v2": EMPIRICAL_PROMPT,
    "observational_field": EMPIRICAL_PROMPT,
    "case_study": EMPIRICAL_PROMPT,
    "mixed_methods": EMPIRICAL_PROMPT,

    # Synthesis family
    "meta_analysis": SYNTHESIS_PROMPT,
    "systematic_review": SYNTHESIS_PROMPT,
    "narrative_review": SYNTHESIS_PROMPT,

    # Theoretical family
    "theoretical": THEORETICAL_PROMPT,
    "conceptual_framework": THEORETICAL_PROMPT,
    "thought_piece": THEORETICAL_PROMPT,

    # Qualitative family
    "qualitative": QUALITATIVE_PROMPT,
    "interview_study": QUALITATIVE_PROMPT,
    "ethnographic": QUALITATIVE_PROMPT,
    "grounded_theory": QUALITATIVE_PROMPT,
    "phenomenological": QUALITATIVE_PROMPT,

    # Methods
    "methods": METHODS_PROMPT,

    # Unknown / unclassified
    "unknown": UNKNOWN_PROMPT,
}


# ═══════════════════════════════════════════════════════════════════════════
# FAMILY MAP — maps article types to families (for quality thresholds)
# ═══════════════════════════════════════════════════════════════════════════

FAMILY_MAP = {
    "empirical_v2": "empirical",
    "empirical": "empirical",
    "observational_field": "empirical",
    "case_study": "empirical",
    "mixed_methods": "empirical",
    "meta_analysis": "synthesis",
    "systematic_review": "synthesis",
    "narrative_review": "synthesis",
    "theoretical": "theoretical",
    "conceptual_framework": "theoretical",
    "thought_piece": "theoretical",
    "interview_study": "qualitative",
    "ethnographic": "qualitative",
    "grounded_theory": "qualitative",
    "phenomenological": "qualitative",
    "qualitative": "qualitative",
    "methods": "methods",
    "unknown": "unknown",
}
