#!/usr/bin/env python3
"""
REVISED EXTRACTION PROMPTS — V3.0 (Complete Rewrite)
======================================================

Comprehensive prompt set for article extraction via Gemini API, implementing
the ATLAS Evidence Synthesis System. This is a complete rewrite of v2.0 with
major enhancements:

  1. Strict direction field validation (4 canonical values only)
  2. Antecedent specificity enforcement (no vague language)
  3. Sample size coverage improvements (required when empirical)
  4. Theory commitment linking (explicit connection rules)
  5. Mechanism chains for causal papers (mandatory 2+ steps)
  6. Instrument naming (specific names, not generic terms)
  7. Full compatibility with extraction_template.v2.schema.json

Changes from V2.0:
  - PROMPT_BASE_V3: Enhanced JSON spec, explicit validation suffix
  - Family-specific prompts restructured with clearer requirements
  - VALIDATION_SUFFIX_V3: Comprehensive pre-submission checks
  - Helper functions for prompt assembly and vocabulary injection
  - Outcome vocab hint generation from outcome_vocab.json
  - Success conditions explicitly documented

Author: Claude Opus 4.6 (Architecture)
Date: 2026-03-01
Sprint: ATLAS Extraction Robustness (V3.0)
"""

import json
import os
from typing import Dict, List, Optional, Tuple


# ═══════════════════════════════════════════════════════════════════════════
# CONSTANTS AND ENUMERATIONS
# ═══════════════════════════════════════════════════════════════════════════

# Canonical direction values (NO other values permitted)
CANONICAL_DIRECTIONS = [
    "increase",
    "decrease",
    "no_effect",
    "mixed"
]

# Article families and their member types
ARTICLE_FAMILIES = {
    "empirical": [
        "empirical_v2",
        "observational_field",
        "case_study",
        "mixed_methods"
    ],
    "synthesis": [
        "meta_analysis",
        "systematic_review",
        "narrative_review"
    ],
    "theoretical": [
        "theoretical",
        "conceptual_framework",
        "thought_piece"
    ],
    "qualitative": [
        "interview_study",
        "ethnographic",
        "grounded_theory",
        "phenomenological"
    ],
    "methods": [
        "methods",
        "instrument",
        "protocol",
        "guidelines",
        "scale_development",
        "validation"
    ]
}

# Mechanism types (for mechanism_chain)
MECHANISM_TYPES = [
    "neural",
    "perceptual",
    "cognitive",
    "affective",
    "behavioral",
    "physiological"
]

# Evidence strength levels (for mechanism_chain)
EVIDENCE_STRENGTHS = [
    "direct",
    "indirect",
    "theoretical",
    "assumed"
]

# Theory commitment types
COMMITMENT_TYPES = [
    "tests",
    "extends",
    "contradicts",
    "assumes",
    "proposes"
]


# ═══════════════════════════════════════════════════════════════════════════
# PROMPT_BASE_V3 — Shared foundation for all families
# ═══════════════════════════════════════════════════════════════════════════

PROMPT_BASE_V3 = """# Article Extraction v3.0 — ATLAS Evidence Synthesis System

You are extracting structured data from a scientific paper about the built environment's
effects on human cognition, emotion, behavior, and health.

## JSON Output Specification

Return ONLY valid, well-formed JSON. No explanations, no markdown code blocks, no commentary.
Every JSON field must be properly quoted and typed. Validate before returning.

If a field is not available in the paper, use null — do NOT invent data.

## Critical Direction Field Rules

Direction MUST be one of exactly 4 canonical values:
  - "increase" — the consequent increases with the antecedent
  - "decrease" — the consequent decreases with the antecedent
  - "no_effect" — no significant relationship found
  - "mixed" — conflicting results across conditions/analyses

NO other values allowed. NOT "positive", "negative", "curvilinear", "unknown", etc.
If results are unclear, use "mixed", not null.

## Critical Antecedent Specification Rules

Antecedent MUST be specific and operationalized:

GOOD:
  - "ceiling height 3.0 m vs 2.4 m"
  - "65 dB pink noise at 4 kHz"
  - "2700K LED at 300 lux with 94% CRI"
  - "room with 3 potted plants (Pothos, 0.5 m height) + 15-minute exposure"
  - "open plan layout with space syntax integration value > 1.2"

BAD (NEVER USE):
  - "the environment"
  - "the condition"
  - "exposure"
  - "the intervention"
  - "environmental features"
  - "design characteristics"
  - "stimulus" (without specifics)

For every antecedent, ask: "Could someone run this study based on this description alone?"
If the answer is no, rewrite it more specifically.

## Critical Consequent Specification Rules

Consequent MUST use specific outcome vocabulary terms:

GOOD:
  - "psych.stress" (not "stress")
  - "PANAS positive affect subscale" (not "positive emotion")
  - "digit span working memory accuracy" (not "memory")
  - "cortisol concentration (ng/mL)" (not "stress hormones")
  - "thermal comfort vote (ASHRAE scale)" (not "thermal comfort")

For every consequent, cite the specific measurement or outcome vocabulary term used.

## Article Classification Requirements

Extract these classification fields:
  - article_type: specific type from article_type_contract.py
  - article_family: one of {empirical, synthesis, theoretical, qualitative, methods}
  - detected_article_type: if unknown, your best guess with confidence score
  - detected_family: if unknown, your best guess with confidence score
  - classification_confidence: 0.0-1.0 (1.0 = certain)
  - classification_signals: list of specific evidence (e.g., "PRISMA diagram on p.3",
    "empirical N=240 reported in methods", "forest plot in Figure 2", etc.)

## Template Matching Guide (166 templates across 10 frameworks)

When extracting findings, populate "template_ids" with relevant template codes when clear:

### PP — PREDICTIVE PROCESSING (58 templates)
  Assign when: prediction error, surprise, expectation violation, Bayesian brain,
  active inference, free energy, environmental statistics, processing fluency,
  gist perception, 1/f spectra, fractal dimension, habituation/novelty.
  Key: T1 (scene statistics → PE), T2 (complexity Goldilocks), T21 (controllability),
       T22 (rapid gist), VF1 (contour PE), COL1 (chromatic PE), L1 (luminance contrast PE)

### SN — SPATIAL NAVIGATION (13 templates)
  Assign when: wayfinding, cognitive maps, space syntax, legibility, isovist analysis,
  spatial memory, route learning, exploration.
  Key: T3 (layout → cognitive map), T24 (path → theta), SC1 (integration as PE),
       SC2 (isovist), SN1 (boundaries → chunking)

### DP — DUAL-PROCESS (3 templates)
  Assign when: System 1/System 2, automatic vs. controlled, implicit evaluation,
  fluency effects, first impressions, aesthetic judgment speed.
  Key: T9 (features → rapid implicit → affect), DP2 (automatic → override)

### DT — DMN/TPN DYNAMICS (15 templates)
  Assign when: default mode, task-positive, mind-wandering, attention restoration,
  directed attention fatigue, cognitive fatigue, creative ideation.
  Key: T4 (attentional demand → DMN suppression), T16 (restoration timecourse),
       CREA1 (DMN-executive coupling), ART (Attention Restoration Theory)

### NM — NEUROMODULATORY SYSTEMS (18 templates)
  Assign when: cortisol, dopamine, serotonin, norepinephrine, acetylcholine,
  oxytocin, HPA axis, vagal tone, reward, arousal, allostatic load.
  Key: NM8 (threat → HPA → cortisol), NM1 (reward PE), NM2 (novelty → dopamine),
       SRT (Stress Recovery Theory)

### IC — INTEROCEPTIVE / CONSTRUCTIONIST AFFECT (15 templates)
  Assign when: interoception, body budget, allostasis, constructed emotion,
  thermal comfort, olfactory affect, privacy regulation, embodied affect.
  Key: T12 (interoceptive PE → affect), IC2 (body budget), T7 (allostatic anticipation)

### MS — MEMORY SYSTEMS (15 templates)
  Assign when: episodic/semantic/working memory, consolidation, place-dependent memory,
  encoding/retrieval, pattern separation, doorway effect.
  Key: EHE1 (hippocampal relational binding), MCR1 (DMN consolidation),
       TEB1 (doorway effect), T36 (WM load)

### EC — EMBODIED COGNITION (8 templates)
  Assign when: affordances, motor simulation, enactivism, sensorimotor contingencies,
  posture, vestibular, haptic exploration.
  Key: T8 (affordances → posture), T18 (vertical → vestibular), T28 (legibility)

### CB — CHRONOBIOLOGICAL (10 templates)
  Assign when: circadian rhythms, melatonin, light exposure timing, CCT, sleep quality,
  seasonal effects, chronotype.
  Key: T30/CLE1 (light → circadian), CSA2 (evening light → melatonin → sleep)

### MSI — MULTISENSORY INTEGRATION (11 templates)
  Assign when: cross-modal effects, audiovisual, sensory congruence, soundscape-visual,
  material perception.
  Key: MCP1 (crossmodal congruency), NMC1 (natural material convergence)

Also assign domain-level theories when relevant:
  - ART: Attention Restoration Theory (Kaplan & Kaplan)
  - SRT: Stress Recovery Theory (Ulrich)
  - Biophilia: Innate affiliation with nature (Wilson, Kellert)
  - Prospect-Refuge: Safe vantage points (Appleton)
  - Privacy Regulation: Personal space control (Altman)

## CNFA Domain Classification

Classify environmental features into these 10 domains:

  A1_Materials: wood, concrete, stone, brick, biophilic materials, texture, patina
  A2_Spatial_Scale: ceiling height, room volume, spaciousness, perceived size, vastness
  A3_Spatial_Config: layout, wayfinding, connectivity, space syntax, legibility, integration
  A4_Light: daylight, illuminance, CCT, glare, window views, melanopic lux
  A5_Acoustic: noise, reverberation (RT60), soundscape, speech privacy, music
  A6_Visual_Form: color, pattern, fractal dimension, curvature, complexity, symmetry
  A7_Haptic_Thermal: temperature, thermal comfort, touch, surface feel, radiant heat
  A8_Social: privacy, crowding, collaboration, density, personal space, encounter frequency
  A9_Task_Cognition: attention, memory, creativity, problem-solving, cognitive performance
  A10_Temporal: exposure duration, adaptation, seasonal, circadian, dose-response

## Domain Terminology Bridge

Papers often use field-specific vocabulary. Map these terms precisely:

  "biophilic design elements" → antecedent: specify which (plants, water, daylight, etc.)
  "perceived restorativeness" → consequent: use PRS scale name if specified
  "physiological stress markers" → consequent: specify exactly (cortisol, HRV, etc.)
  "spatial configuration" → antecedent: specify (open plan, cellular, integration value)
  "cognitive performance" → consequent: specify (Stroop accuracy, d2 test, etc.)
  "IEQ" (indoor environmental quality) → extract findings for EACH separate dimension
  "occupant satisfaction" → consequent: specify which (thermal, acoustic, layout, etc.)
  "environmental satisfaction" → consequent: use specific measure (BUS, POE, etc.)

## Statistics Graceful Degradation Rules

EXTRACT EVERY FINDING, even if statistics are incomplete:

  RULE 1: p-value but no effect size → extract with effect_size: null
  RULE 2: effect size but no p-value → extract with p_value: null
  RULE 3: only "p < .05" or "p < .01" → use p_value: "<0.05" or "<0.01"
  RULE 4: confidence interval but no p-value → extract CI, p_value: null
  RULE 5: odds/hazard/risk ratio → effect_size with type "OR"/"HR"/"RR"
  RULE 6: Bayes factor → effect_size for BF, type "BF10" or "BF01", p_value: null
  RULE 7: beta weights from regression → effect_size for beta, type "beta"
  RULE 8: R² or adjusted R² → type "R_squared"
  RULE 9: only "significant"/"not significant" with no numbers → p_value: "significant"/"ns"
  RULE 10: antecedent + consequent + direction but NO statistics → still extract

DO NOT skip findings for lack of statistics. Partial > nothing.
DO NOT invent statistics. DO NOT guess. DO NOT combine analyses.

## Provenance Depth Specification

Tag each finding with location specificity:

  "direct_quote" — directly quoted from paper with page number
  "paraphrase" — paraphrased from specific location
  "inferred" — logically inferred from paper content
  "synthesized" — synthesized across multiple sections
  null — if completely unclear where finding came from

## What NOT to Extract

Do NOT extract as findings:
  - Citations of OTHER papers' results unless replicated here
  - Hypothesized relationships in Introduction NOT tested
  - Descriptive demographics unless age/gender is an independent variable
  - Manipulation checks (e.g., "bright room rated brighter")
  - Statistical artifacts
  - Pilot study results unless treated substantively
  - Individual study results from reviews — extract only synthesized conclusions

Do NOT extract as theory_links:
  - Frameworks merely mentioned without guiding hypotheses
  - Theory links requiring inferential chains you're constructing
"""


# ═══════════════════════════════════════════════════════════════════════════
# VALIDATION_SUFFIX_V3 — Appended to all family prompts
# ═══════════════════════════════════════════════════════════════════════════

VALIDATION_SUFFIX_V3 = """

## FINAL VALIDATION CHECKLIST

BEFORE RETURNING YOUR JSON, verify EVERY item below. If any check fails, revise:

1. **Direction Field**: Every finding's direction ∈ {increase, decrease, no_effect, mixed}
   - NOT: positive, negative, curvilinear, unclear, ambiguous
   - NOT: null (use "mixed" if truly ambiguous)
   - Check: 0 findings should fail this test

2. **Antecedent Specificity**: Every finding has operationalized antecedent
   - NOT vague: "the environment", "the condition", "exposure", "intervention"
   - Rule: If you can't describe it to a research assistant in < 30 seconds, rewrite
   - Target: <10% vague antecedents (v2 had 32%)
   - Check: Search JSON for these banned words → 0 occurrences

3. **Sample Size Coverage**: For EVERY empirical finding:
   - sample_size must be filled (integer > 0)
   - If not stated, ESTIMATE from methods and set sample_size_source: "estimated"
   - Target: >80% of empirical findings (v2 had 18%)
   - Check: Count nulls in sample_size field for empirical papers

4. **Theory Commitments**: For papers mentioning theoretical frameworks:
   - If paper cites a theory AND uses it to frame hypotheses → extract theory_commitments[]
   - Each commitment must have: theory_name, commitment_type (tests/extends/contradicts/assumes/proposes), specific_claim
   - Target: >50% of papers with theory mentions have theory_commitments[]
   - Check: Papers with "Attention Restoration Theory" mention should have ART commitment

5. **Mechanism Chains**: For papers making causal claims:
   - mechanism_chain MUST have at least 2 steps
   - Each step: {step: int, from_construct, to_construct, mechanism_type, evidence_strength}
   - Mechanism types: neural, perceptual, cognitive, affective, behavioral, physiological
   - Evidence strengths: direct, indirect, theoretical, assumed
   - Example: [{step: 1, from: "red light (600nm)", to: "melatonin suppression", mechanism_type: "physiological"},
               {step: 2, from: "melatonin suppression", to: "sleep onset latency", mechanism_type: "physiological"}]
   - Target: >60% of causal-claim papers have 2+ steps
   - Check: Count findings with claim_type="causal" that have mechanism_chain.length < 2

6. **Instrument Naming**: For EVERY empirical finding:
   - instruments_used[] must contain SPECIFIC instrument names
   - NOT vague: "questionnaire", "survey", "scale", "test", "inventory"
   - GOOD: "PANAS", "NASA-TLX", "State-Trait Anxiety Inventory", "polysomnography"
   - Each instrument needs: {name, construct_measured, abbreviation, n_items}
   - Target: >70% of empirical papers have named instruments
   - Check: Search for generic terms → 0 occurrences

7. **JSON Schema Validity**: Entire output must conform to extraction_template.v2.schema.json
   - All required fields present (doi, article_type, title, authors, findings)
   - Finding IDs must match pattern ^[A-Z0-9_]+$
   - confidence_interval (if present) must be [lower, upper] with both numeric
   - effect_size_type enum must be valid (Cohen's d, eta_squared, etc.)
   - Check: Run JSON against schema validator

8. **No Empty/Null Critical Fields**:
   - No finding should have null antecedent or consequent
   - No finding should have null claim_type
   - For empirical papers: p_value and effect_size should not BOTH be null
   - For qualitative papers: either "descriptive" direction or specific theme_name
   - Check: Search JSON for {"antecedent": null} → 0 occurrences

9. **Outcome Vocabulary Alignment**: consequent field uses canonical terms where possible
   - Reference the outcome_vocab.json domains: cog, affect, behav, social, physio, neural, health, env
   - Example consequents: "cog.attention", "affect.anxiety", "physio.cortisol"
   - Not: bare words like "stress", "creativity", "satisfaction"
   - Check: Consequents should map to recognized outcome vocab terms

10. **Classification Confidence**: If detecting article type:
    - classification_confidence must be 0.0-1.0
    - classification_signals must cite SPECIFIC evidence (page numbers, section headers, methods details)
    - NOT vague: "looks like an experiment" (bad)
    - GOOD: "Abstract reports N=240 between-subjects design", "PRISMA diagram on p.3"
    - Check: Every signal must be traceable to paper content

11. **Stimulus Description Coverage** (NEW): For EVERY empirical finding:
    - stimulus_description MUST be populated (NEVER null for empirical claims)
    - primary_type must be one of: visual_scene, soundscape, thermal, olfactory, spatial, lighting, material, mixed
    - components array MUST have at least 1 entry describing the stimulus
    - delivery_method must be specified: in_situ, VR, photo, video, audio, or imagined
    - If paper lacks details, document this in components with {"name": "Details not provided", "essential": false}
    - Target: 100% of empirical findings (v2 had 0% populated)
    - Check: Search findings for stimulus_description: null → 0 occurrences for empirical papers

12. **Stimulus Images Coverage**: For findings describing visual manipulations (lighting, spatial, visual_form):
    - stimulus_images should be populated if figures are available
    - Each image: {description: string, figure_ref: string (e.g., "Figure 2A"), image_type: photo|rendering|diagram|floor_plan|graph}
    - Target: 70%+ of visually-described stimuli have at least 1 image reference
    - Check: Count findings with visual primary_type that reference figures

---

If you find issues during validation:
  1. Stop validation
  2. Revise the problematic field(s)
  3. Re-validate from the top
  4. Only return JSON when ALL 10 checks pass

This validation is NOT optional. It directly impacts downstream system quality.
"""


# ═══════════════════════════════════════════════════════════════════════════
# EMPIRICAL_PROMPT_V3 — For empirical, observational, case_study, mixed_methods
# ═══════════════════════════════════════════════════════════════════════════

EMPIRICAL_PROMPT_V3 = PROMPT_BASE_V3 + """

═══════════════════════════════════════════════════════════════════════════════
EXTRACTION: EMPIRICAL FAMILY (v3.0)
(empirical_v2 | observational_field | case_study | mixed_methods)
═══════════════════════════════════════════════════════════════════════════════

Required fields: research_question, design_type, participants, stimuli_or_exposures,
measures, findings, limitations

Return this JSON structure:

{
  "doi": "10.xxxx/xxxxx",
  "article_type": "empirical_v2|observational_field|case_study|mixed_methods",
  "article_family": "empirical",
  "detected_article_type": "if not pre-classified, your best guess",
  "detected_family": "empirical",
  "classification_confidence": 0.95,
  "classification_signals": ["specific evidence"],

  "title": "exact paper title",
  "authors": ["First Author", "Second Author"],

  "research_question": "the paper's central research question(s)",
  "design_type": "between_subjects|within_subjects|mixed_factorial|cross_sectional|longitudinal|quasi_experiment|pre_post|case_control|cohort|POE|other",

  "participants": {
    "n": number or null,
    "n_source": "reported|estimated|inferred",
    "description": "demographics (age range, country, setting, recruitment criteria)",
    "recruitment": "how recruited if stated",
    "attrition": "dropout rate if reported"
  },

  "stimuli_or_exposures": [
    {
      "exposure_id": "E1",
      "type": "photograph|rendering|VR|video|physical_space|audio|plan_drawing|model|real_world|other",
      "description": "BE SPECIFIC. If lighting: include CCT, lux, direction. If space: include dimensions, materials, layout details",
      "n_stimuli": number or null,
      "source": "Figure reference, methods section p.X, or supplementary material",
      "variables_manipulated": ["list of exactly what was varied across conditions"]
    }
  ],

  "measures": [
    {
      "measure_id": "M1",
      "construct": "what was measured",
      "instrument": "specific instrument/scale name (NOT 'questionnaire')",
      "abbreviation": "STAI, PANAS, etc.",
      "type": "self_report|behavioral|physiological|cognitive|performance|neural|observational",
      "n_items": number or null,
      "reliability": {"cronbach_alpha": 0.89, "test_retest": 0.84}
    }
  ],

  "findings": [
    {
      "id": "F1",
      "antecedent": "specific environmental condition or independent variable — OPERATIONALIZED",
      "consequent": "specific outcome measured — use outcome vocab term if available",
      "direction": "increase|decrease|no_effect|mixed",
      "claim_type": "empirical_finding|causal|associational|moderated|mediated|null",
      "measure_type": "self_report|behavioral|physiological|cognitive|performance|neural|observational",

      "p_value": 0.003 or "<0.001" or "significant" or null,
      "effect_size": -0.45 or null,
      "effect_size_type": "Cohen's d|eta_squared|partial_eta_squared|r|OR|HR|RR|beta|R_squared|Cramer's V|null",
      "test_statistic": "F(2,45)=3.21 or t(98)=2.45 or χ²(1)=3.84 or null",
      "sample_size": 240,
      "sample_size_source": "reported|estimated|inferred",
      "confidence_interval": [0.15, 0.75] or null,

      "stimulus_description": {
        "primary_type": "visual_scene|soundscape|thermal|olfactory|spatial|lighting|material|mixed",
        "components": [
          {"name": "ceiling height", "category": "spatial", "essential": true},
          {"name": "LED color temperature", "category": "visual", "essential": true}
        ],
        "delivery_method": "in_situ|VR|photo|video|audio|imagined",
        "duration_seconds": 120 or null
      },

      "stimulus_images": [
        {
          "description": "photo of low ceiling condition",
          "figure_ref": "Figure 2A",
          "image_type": "photo|rendering|diagram|floor_plan|graph"
        }
      ],

      "instruments_used": [
        {
          "name": "State-Trait Anxiety Inventory",
          "abbreviation": "STAI",
          "instrument_id": "STAI",
          "construct_measured": "trait and state anxiety",
          "n_items": 40,
          "reliability": {"cronbach_alpha": 0.91}
        }
      ],

      "theory_commitments": [
        {
          "theory_name": "Attention Restoration Theory",
          "commitment_type": "tests",
          "specific_claim": "that natural scenes reduce directed attention fatigue more than urban scenes"
        }
      ],

      "mechanism_chain": [
        {
          "step": 1,
          "from_construct": "natural scene (high complexity, 1/f spectrum)",
          "to_construct": "soft fascination (bottom-up attention capture)",
          "mechanism_type": "perceptual",
          "evidence_strength": "theoretical"
        },
        {
          "step": 2,
          "from_construct": "soft fascination",
          "to_construct": "default mode network engagement",
          "mechanism_type": "neural",
          "evidence_strength": "indirect"
        },
        {
          "step": 3,
          "from_construct": "DMN engagement",
          "to_construct": "directed attention fatigue recovery",
          "mechanism_type": "cognitive",
          "evidence_strength": "indirect"
        }
      ],

      "molecule_ids": ["RASA_001", "RASA_015"],

      "theory_links": ["ART", "DT", "PP"],
      "template_ids": ["T4", "CREA1"],

      "moderators_reported": ["age", "prior nature exposure"],
      "provenance_depth": "direct_quote|paraphrase|inferred|synthesized",
      "source": "Results section, p.12 or Table 3",
      "quote": "exact quote from paper (max 150 chars)"
    }
  ],

  "implementation_implications": ["practical implications stated by authors"],
  "domains": ["A1_Materials", "A4_Light", "A9_Task_Cognition"],
  "overall_theory_links": ["ART", "SRT", "PP"],

  "tables": [
    {
      "table_id": "Table 2",
      "description": "means and SDs for all outcome measures by condition",
      "key_stats": ["F(2,45)=3.2, p<.05", "R²=.24"],
      "n_findings_extracted_from": 6
    }
  ],

  "limitations": ["stated by authors"],
  "minimum_safe_summary": "Brief summary suitable for low-tolerance downstream systems"
}

## CRITICAL EMPIRICAL EXTRACTION RULES

1. **SPECIFICITY FIRST**: Extract exact operationalizations, not vague constructs.
   - Antecedent: dimensions, values, units, controls
   - Consequent: exact measurement used (score type, scale range, units)

2. **EVERY ANALYSIS = A FINDING**: Each regression predictor, ANOVA effect/interaction,
   correlation pair, mediation path. Do NOT drop analyses because they're "not significant".

3. **NULL RESULTS MATTER**: "No effect of X on Y" with p=0.34 → extract as finding with
   direction: "no_effect", claim_type: "null", p_value: 0.34.

4. **TABLES ARE PRIMARY**: Read every table. Cross-check text against tables.
   Extract from tables FIRST, then confirm with text.

5. **MODERATION vs MEDIATION**:
   - Moderation (interaction): extract as separate finding with claim_type: "moderated"
   - Mediation: extract (a) X→Y direct, (b) X→M, (c) M→Y, (d) indirect effect as 4 findings

6. **STIMULUS DESCRIPTION**: For EVERY empirical finding, ALWAYS populate stimulus_description
   with these fields (DO NOT leave as null):

   - primary_type: One of {visual_scene, soundscape, thermal, olfactory, spatial, lighting, material, mixed}
     Pick the dominant sensory modality of the experimental manipulation

   - components: Array describing each key component of the stimulus. For architectural:
     Include room dimensions, ceiling height, window area, material finishes, lighting (CCT, lux).
     For lighting: include CCT (e.g., 2700K, 4000K, 6500K), illuminance (lux), CRI if available.
     For acoustic: include dB levels, frequency content, source type (mechanical, natural, speech).
     For materials: include material types, textures, colors, finish (matte/glossy).
     Each component object: {"name": string, "category": string, "essential": true/false}

   - delivery_method: How stimulus was presented: in_situ (real environment), VR, photo, video,
     audio, or imagined (mental imagery)

   - duration_seconds: How long exposure lasted (null if not applicable or not stated)

   MANDATE: DO NOT use null for stimulus_description in empirical findings. If the paper does not
   report stimulus details, write "Details not provided in paper" in the first component's name field,
   set essential: false, and note what you inferred. Example: {"name": "room_type: inferred_office",
   "category": "spatial", "essential": false}

7. **SAMPLE SIZE MANDATORY**: For every empirical finding:
   - If N is stated in paper: sample_size: N, sample_size_source: "reported"
   - If N not stated but inferrable (e.g., "90 completed questionnaire"): estimate from methods,
     sample_size: 90, sample_size_source: "inferred"
   - If completely absent: estimate from analysis (e.g., from F-test df), mark sample_size_source: "estimated"
   - NEVER leave as null for empirical findings.

8. **INSTRUMENTS NAMED, NOT GENERIC**: Do NOT write "questionnaire", "survey", "inventory".
   Write exact names: "PANAS", "NASA-TLX", "Perceived Restorativeness Scale (PRS)",
   "Profile of Mood States (POMS)".

9. **TEMPLATE MATCHING**: Only assign template_ids when the finding DIRECTLY matches the
   template's causal chain (not just nearby). If unsure, leave empty [].

""" + VALIDATION_SUFFIX_V3


# ═══════════════════════════════════════════════════════════════════════════
# SYNTHESIS_PROMPT_V3 — For meta_analysis, systematic_review, narrative_review
# ═══════════════════════════════════════════════════════════════════════════

SYNTHESIS_PROMPT_V3 = PROMPT_BASE_V3 + """

═══════════════════════════════════════════════════════════════════════════════
EXTRACTION: SYNTHESIS FAMILY (v3.0)
(meta_analysis | systematic_review | narrative_review)
═══════════════════════════════════════════════════════════════════════════════

Required fields: review_question, inclusion_exclusion_criteria, evidence_base_summary,
findings (pooled effects AND notable divergent studies), synthesis_conclusions

Return this JSON structure:

{
  "doi": "10.xxxx/xxxxx",
  "article_type": "meta_analysis|systematic_review|narrative_review",
  "article_family": "synthesis",
  "detected_article_type": "meta_analysis",
  "classification_confidence": 0.99,
  "classification_signals": ["PRISMA diagram on p.3", "forest plot in Figure 2"],

  "title": "exact paper title",
  "authors": ["First Author", "Second Author"],

  "review_question": "the central review question (often from PICO/PICOT framework)",
  "inclusion_exclusion_criteria": "summary of what was included/excluded (populations, interventions, comparisons, outcomes, study designs)",

  "evidence_base_summary": {
    "k": 47,
    "total_n": 5240,
    "search_databases": ["PubMed", "Scopus", "Web of Science"],
    "search_date_range": "1990-2026",
    "review_protocol": "PRISMA|PROSPERO|Cochrane|other|not_specified",
    "protocol_registration": "PROSPERO ID or null"
  },

  "findings": [
    {
      "id": "F1_POOLED",
      "antecedent": "factor/intervention — BE SPECIFIC",
      "consequent": "primary outcome — BE SPECIFIC (use outcome vocab)",
      "direction": "increase|decrease|no_effect|mixed",
      "evidence_strength": "strong|moderate|weak|inconsistent",
      "claim_type": "pooled_effect",

      "effect_size": 0.35,
      "effect_size_type": "Cohen's d",
      "confidence_interval": [0.22, 0.48],
      "p_value": "<0.001",

      "k": 47,
      "k_source": "exact count from paper",
      "n_total": 5240,
      "I_squared": 62.5,
      "tau_squared": 0.08,
      "Q_statistic": "Q(46)=125.3, p<.001",

      "theory_links": ["ART", "DT"],
      "template_ids": ["T4"],
      "moderators_reported": ["study_quality", "follow_up_duration"],

      "provenance_depth": "direct_quote",
      "source": "Table 2, Figure 3 forest plot",
      "quote": "The pooled effect was significantly positive (SMD = 0.35, 95% CI [0.22, 0.48])"
    },
    {
      "id": "F2_DIVERGENT_STUDIES",
      "antecedent": "same factor with moderator: study quality (high vs low)",
      "consequent": "same outcome",
      "direction": "mixed",
      "evidence_strength": "moderate",
      "claim_type": "moderated",
      "description": "High-quality studies (GRADE A) showed stronger effects than low-quality studies",

      "subgroup_effects": [
        {
          "subgroup": "high_quality_studies",
          "k": 12,
          "effect_size": 0.52,
          "effect_size_type": "Cohen's d",
          "confidence_interval": [0.38, 0.66]
        },
        {
          "subgroup": "low_quality_studies",
          "k": 35,
          "effect_size": 0.24,
          "effect_size_type": "Cohen's d",
          "confidence_interval": [0.08, 0.40]
        }
      ],

      "provenance_depth": "inferred",
      "source": "Subgroup analysis, p.15",
      "quote": "Quality moderated the pooled effect (test of moderation p=.042)"
    }
  ],

  "synthesis_conclusions": [
    "Strong evidence for effect of natural light exposure on sleep quality",
    "Effect sizes larger in long-term exposure (>6 months) than acute (single session)",
    "Heterogeneity driven by study quality and participant age groups"
  ],

  "evidence_gaps": [
    "Few studies of circadian-misaligned populations",
    "Limited evidence for ecological validity of lab studies"
  ],

  "risk_of_bias_assessment": "Cochrane Risk of Bias 2 tool; 72% of studies rated as low risk",
  "heterogeneity_sources": [
    "Study quality (high vs. low)",
    "Follow-up duration (acute vs. chronic)",
    "Population age (young vs. older adults)"
  ],
  "publication_bias": "Egger's test p=0.12 (no significant publication bias detected)",

  "moderators": [
    {
      "variable": "study_quality_GRADE",
      "effect": "higher quality studies showed effect size 0.52 vs 0.24 for lower quality",
      "significant": true,
      "test_statistic": "z=2.14, p=.032"
    }
  ],

  "domains": ["A4_Light", "A9_Task_Cognition", "CB"],
  "overall_theory_links": ["CB", "SRT"],
  "limitations": ["heterogeneity remains substantial", "publication bias possible for small studies"]
}

## CRITICAL SYNTHESIS EXTRACTION RULES

1. **POOLED EFFECT AS PRIMARY FINDING**: Extract the main meta-analytic or synthesized result
   as ONE finding with claim_type: "pooled_effect". This is the TOP-LINE RESULT.

2. **SUBGROUP EFFECTS AS SEPARATE FINDINGS**: Each important subgroup analysis (by quality,
   age, duration, etc.) = separate finding with claim_type: "moderated".

3. **FOREST PLOT READING**: For every forest plot:
   - Extract k (number of studies)
   - Extract pooled effect (center diamond)
   - Extract I² (heterogeneity %)
   - Extract tau² if reported
   - Extract individual study effects if they visibly diverge from pooled estimate

4. **INDIVIDUAL STUDIES IN REVIEWS**: Do NOT extract individual study results from narrative
   reviews as separate findings. Extract only the synthesized conclusion (finding type: "synthesized").

5. **ALWAYS EXTRACT I² and tau²**: These measure heterogeneity. Critical for judging credibility.
   If not reported: p_value: null, I_squared: null, tau_squared: null (don't invent).

6. **EVIDENCE STRENGTH**: Assess as:
   - "strong": multiple well-powered RCTs, low heterogeneity, large effect size, consistent direction
   - "moderate": mixed quality studies, moderate heterogeneity, moderate effect size
   - "weak": few studies, small N total, high heterogeneity, inconsistent direction
   - "inconsistent": high heterogeneity with conflicting directions across studies

7. **K (NUMBER OF STUDIES)**: Must be reported for every pooled finding. This is NOT optional.

""" + VALIDATION_SUFFIX_V3


# ═══════════════════════════════════════════════════════════════════════════
# THEORETICAL_PROMPT_V3 — For theoretical, conceptual_framework, thought_piece
# ═══════════════════════════════════════════════════════════════════════════

THEORETICAL_PROMPT_V3 = PROMPT_BASE_V3 + """

═══════════════════════════════════════════════════════════════════════════════
EXTRACTION: THEORETICAL FAMILY (v3.0)
(theoretical | conceptual_framework | thought_piece)
═══════════════════════════════════════════════════════════════════════════════

Required fields: central_proposition, concept_definitions, argument_structure,
mechanism_or_causal_logic, testable_hypotheses_or_predictions, findings

Return this JSON structure:

{
  "doi": "10.xxxx/xxxxx",
  "article_type": "theoretical|conceptual_framework|thought_piece",
  "article_family": "theoretical",
  "detected_article_type": "theoretical",
  "classification_confidence": 0.92,
  "classification_signals": ["No empirical methods section", "All findings are theoretical propositions"],

  "title": "exact paper title",
  "authors": ["First Author", "Second Author"],

  "central_proposition": "The paper's main claim in one clear sentence. This is the core thesis.",

  "concept_definitions": [
    {
      "name": "Soft Fascination",
      "definition": "As defined in this paper: involuntary attention to stimuli that is gentle and effortless",
      "source_reference": "p.4, Section 2.1"
    }
  ],

  "argument_structure": "Brief description of how the argument is built (e.g., 'builds from neural mechanisms → cognitive processes → environmental design implications')",
  "mechanism_or_causal_logic": "The proposed causal mechanism(s) linking key constructs",

  "findings": [
    {
      "id": "T1",
      "antecedent": "proposed cause/environmental feature — BE SPECIFIC",
      "consequent": "proposed effect/cognitive outcome — BE SPECIFIC",
      "direction": "increase|decrease|modulates|mixed",
      "claim_type": "theoretical_proposition",

      "mechanism": "detailed explanation of how/why this link works — CRITICAL for theoretical papers",
      "testable": true,
      "falsifiable": true,
      "empirical_support_cited": "brief note on cited evidence or empirical support, null if purely theoretical",

      "theory_commitments": [
        {
          "theory_name": "Predictive Processing",
          "commitment_type": "extends",
          "specific_claim": "extends predictive processing by proposing that environmental complexity statistics signal prediction error in aesthetic perception"
        }
      ],

      "mechanism_chain": [
        {
          "step": 1,
          "from_construct": "environmental scene statistics (1/f power spectrum)",
          "to_construct": "visual cortex population coding (V1, V2)",
          "mechanism_type": "neural",
          "evidence_strength": "theoretical"
        },
        {
          "step": 2,
          "from_construct": "V1/V2 prediction error signal",
          "to_construct": "affective response (aesthetic pleasure)",
          "mechanism_type": "affective",
          "evidence_strength": "theoretical"
        }
      ],

      "theory_links": ["PP", "DT"],
      "template_ids": ["T2"],

      "bridge_warrants": [
        "connects to empirical work on fractal dimension preference (Taylor et al., 1999)",
        "extends Berlyne's arousal-modulation theory via predictive processing"
      ],

      "provenance_depth": "paraphrase",
      "source": "Section 3.2, 'A Predictive Processing Account of Aesthetic Response'",
      "quote": "environmental scenes with power law 1/f spectra minimize prediction error in visual cortex"
    }
  ],

  "testable_hypotheses_or_predictions": [
    "Scenes with 1/f power spectra should evoke faster aesthetic judgments (lower RT) than scenes with flat or pink noise spectra",
    "Individual differences in fractal dimension preference should correlate with trait openness to experience"
  ],

  "bridge_warrants": [
    "This theory connects to empirical work by Taylor et al. (2011) on fractal dimension in nature",
    "Links through Kaplan's Information Rate Theory to Orians & Heerwagen's habitat selection theory"
  ],

  "methodological_critiques": [
    "Prior work on aesthetic preference confounds stimulus properties with participant expectations",
    "Need for neuroimaging studies to test the proposed V1/V2 mechanism directly"
  ],

  "model_structure": "description of the overall model/framework architecture if proposed (e.g., 'hierarchical: environmental features → neural signals → perception → affect → behavior')",

  "domains": ["A6_Visual_Form", "DT"],
  "overall_theory_links": ["PP", "DT", "IC"],
  "limitations": ["boundary conditions or acknowledged limitations"]
}

## CRITICAL THEORETICAL EXTRACTION RULES

1. **MECHANISM CHAIN NOW MANDATORY**: Every theoretical paper proposes at least an implicit
   mechanism. Extract it as mechanism_chain with 2+ steps:
   - Step 1: Environmental feature → neural/perceptual process
   - Step 2: Neural process → cognitive process
   - Step 3: Cognitive process → behavioral outcome (if proposed)

2. **TESTABLE PREDICTION**: If a mechanism is proposed, what predictions follow?
   testable_hypotheses_or_predictions should be specific and falsifiable.
   - GOOD: "scenes with 1/f power spectra should receive higher preference ratings than pink noise"
   - BAD: "environmental complexity affects people's responses"

3. **THEORY COMMITMENTS**: Extract how this paper engages with existing frameworks:
   - tests: empirically evaluates a theory (rare for pure theory papers)
   - extends: builds on existing theory with new claims
   - contradicts: refutes prior work
   - assumes: takes certain theoretical claims as given
   - proposes: introduces wholly novel theoretical claims

4. **BRIDGE WARRANTS**: Valuable for downstream Bayesian network construction. How does this
   theory connect to other frameworks? What existing empirical work supports it?

5. **FALSIFIABILITY**: Mark testable: true/false for each proposition. A theory that cannot
   be tested has limited value for architecture research.

6. **USE "findings" AS KEY**: Not "propositions", "claims", or "arguments". Standardize on
   the "findings" array.

""" + VALIDATION_SUFFIX_V3


# ═══════════════════════════════════════════════════════════════════════════
# QUALITATIVE_PROMPT_V3 — For interview, ethnographic, grounded_theory, phenomenological
# ═══════════════════════════════════════════════════════════════════════════

QUALITATIVE_PROMPT_V3 = PROMPT_BASE_V3 + """

═══════════════════════════════════════════════════════════════════════════════
EXTRACTION: QUALITATIVE FAMILY (v3.0)
(interview_study | ethnographic | grounded_theory | phenomenological)
═══════════════════════════════════════════════════════════════════════════════

Required fields: research_focus, sample_context, data_collection_method,
coding_or_analysis_approach, themes_or_constructs, supporting_quotes, transferability

Return this JSON structure:

{
  "doi": "10.xxxx/xxxxx",
  "article_type": "interview_study|ethnographic|grounded_theory|phenomenological",
  "article_family": "qualitative",
  "detected_article_type": "interview_study",
  "classification_confidence": 0.88,
  "classification_signals": ["Thematic analysis methodology", "40 semi-structured interviews", "direct participant quotes provided"],

  "title": "exact paper title",
  "authors": ["First Author", "Second Author"],

  "research_focus": "what the study set out to understand",

  "sample_context": {
    "n_participants": 40,
    "description": "urban professionals, age 25-65, worked in open plan offices for >2 years",
    "recruitment": "snowball sampling from 3 companies in San Francisco",
    "setting": "urban office buildings in downtown SF"
  },

  "data_collection_method": "semi_structured_interviews|unstructured_interviews|focus_groups|participant_observation|photo_elicitation|walking_interviews|other",
  "data_collection_details": "e.g., '45-minute semi-structured interviews conducted in-situ at workstations'",

  "coding_or_analysis_approach": "thematic_analysis|grounded_theory_coding|IPA|framework_analysis|content_analysis|narrative_analysis|other",
  "analysis_details": "brief description of coding process (e.g., 'initial open coding of 5 transcripts, then axial coding for theme clustering')",

  "findings": [
    {
      "id": "Q1",
      "antecedent": "environmental factor (often a theme trigger) — or null if purely descriptive theme",
      "consequent": "experiential outcome (or null if purely descriptive)",
      "direction": "descriptive|increase|decrease|mixed",
      "claim_type": "qualitative_theme",

      "theme_name": "open_plan_noise_disruption",
      "description": "Participants reported that constant background noise in open plan offices disrupts focused work and creates chronic stress",
      "theme_richness": "rich|moderate|minimal",
      "saturation": "saturated|emerging|limited|not_reported",

      "supporting_quotes": [
        "I can't concentrate with everyone talking around me. By 2pm my head is pounding" [Participant 12]",
        "The noise here is relentless. There's no escape" [Participant 28]"
      ],

      "n_participants_expressing": 28,
      "frequency": "all but 2 participants mentioned noise as a problem",

      "mechanism_candidates": [
        "acoustic startle → amygdala vigilance → sustained attention drain → cognitive fatigue",
        "social proximity → heightened awareness of others → self-consciousness → productivity loss"
      ],

      "derived_hypotheses": [
        "workers with higher neuroticism should report greater noise sensitivity",
        "private office spaces should predict lower cortisol and higher job satisfaction"
      ],

      "theory_links": ["DT", "NM"],
      "template_ids": ["T4", "AX10"],

      "transferability_context": "findings likely transfer to other open plan office contexts in developed nations; may not transfer to noise-normalized work environments (factories, construction sites)",

      "provenance_depth": "paraphrase",
      "source": "Theme 2, Results section, p.8-10"
    }
  ],

  "themes_or_constructs": [
    "open_plan_noise_disruption",
    "spatial_proximity_social_stress",
    "lack_of_spatial_personalization",
    "desire_for_privacy_and_control"
  ],

  "supporting_quotes_or_evidence_snippets": [
    "key quotes that anchor major claims (30-100 chars each)"
  ],

  "derived_hypotheses": [
    "testable hypotheses the authors propose for future work"
  ],

  "mechanism_candidates": [
    "proposed mechanisms connecting themes to outcomes based on participant experience"
  ],

  "transferability_limits": [
    "contexts where findings may/may not apply (cultures, settings, populations)"
  ],

  "methodological_rigor": {
    "research_design": "interview_study|ethnographic|etc.",
    "sample_n": 40,
    "sampling_strategy": "snowball|purposive|theoretical|convenience|other",
    "data_collection_method": "semi_structured interviews",
    "analysis_approach": "thematic analysis",
    "coding_strategy": "deductive|inductive|hybrid",
    "intercoder_agreement": "Cohen's kappa = 0.87 or N/A if single coder",
    "saturation_evidence": "yes - new interviews after N=32 produced no new themes"
  },

  "domains": ["A3_Spatial_Config", "A5_Acoustic", "A8_Social"],
  "overall_theory_links": ["DT", "NM"],
  "limitations": ["stated limitations (e.g., self-selection bias, retrospective recall)"]
}

## CRITICAL QUALITATIVE EXTRACTION RULES

1. **THEMES AS FINDINGS**: Use "findings" array with claim_type: "qualitative_theme".
   Each theme = one finding with description, supporting_quotes, saturation evidence.

2. **ANTECEDENT MAPPING**: Where possible, map themes to environmental antecedent → experiential
   consequent. Example:
   - antecedent: "open plan office layout (>80% visual openness)"
   - consequent: "sense of lack of privacy and control"
   - direction: "descriptive" (since no comparison/measurement)

3. **SUPPORTING QUOTES ARE SACRED**: Extract actual participant words, NOT authors' interpretations.
   - GOOD: "I can't focus with everyone watching me"
   - BAD: "Participants reported lack of privacy" (that's interpretation)

4. **SATURATION EVIDENCE**: Did the paper report reaching saturation?
   - "saturated" — explicitly stated saturation reached
   - "emerging" — new themes appearing in final interviews
   - "limited" — few participants, themes underdeveloped
   - "not_reported" — no mention of saturation

5. **TRANSFERABILITY CONTEXT**: Qualitative findings are contextual. What settings/populations
   do findings transfer to? Be explicit about boundary conditions.

6. **MECHANISM CANDIDATES**: If participants describe WHY something happens, extract as
   mechanism_candidate (not proven, just suggested by lived experience).

7. **DERIVED HYPOTHESES**: If authors propose testable hypotheses from qualitative findings,
   extract them. These bridge to future empirical work.

""" + VALIDATION_SUFFIX_V3


# ═══════════════════════════════════════════════════════════════════════════
# METHODS_PROMPT_V3 — For methods/measurement papers
# ═══════════════════════════════════════════════════════════════════════════

METHODS_PROMPT_V3 = PROMPT_BASE_V3 + """

═══════════════════════════════════════════════════════════════════════════════
EXTRACTION: METHODS FAMILY (v3.0)
(instrument | protocol | guidelines | scale_development | validation)
═══════════════════════════════════════════════════════════════════════════════

Return this JSON structure:

{
  "doi": "10.xxxx/xxxxx",
  "article_type": "methods|instrument|protocol|guidelines|scale_development|validation",
  "article_family": "methods",
  "detected_article_type": "scale_development",
  "classification_confidence": 0.95,
  "classification_signals": ["Describes development of new measurement scale", "Psychometric validation reported"],

  "title": "exact paper title",
  "authors": ["First Author", "Second Author"],

  "method_type": "instrument|protocol|guidelines|scale_development|validation|simulation|framework",
  "target_construct": "what it measures or does",

  "findings": [
    {
      "id": "M1",
      "antecedent": "method/instrument component or procedure step",
      "consequent": "what it measures or enables",
      "direction": "descriptive",
      "claim_type": "methodological",

      "validation_evidence": "how validated if reported (e.g., 'factor analysis confirms 3-factor structure')",
      "theory_links": ["framework codes"],
      "template_ids": ["template IDs"],

      "provenance_depth": "direct_quote",
      "source": "Methods section, p.5"
    }
  ],

  "instrument_details": {
    "name": "Environmental Perception Survey - Revised (EPS-R)",
    "construct": "perceived environmental quality",
    "n_items": 28,
    "subscales": [
      {"name": "spatial_comfort", "n_items": 8},
      {"name": "acoustic_comfort", "n_items": 7},
      {"name": "thermal_comfort", "n_items": 7},
      {"name": "aesthetic_satisfaction", "n_items": 6}
    ],
    "item_example": "I feel satisfied with the light quality in this space (1=strongly disagree, 5=strongly agree)",
    "reliability": {
      "cronbach_alpha_overall": 0.91,
      "cronbach_alpha_subscales": [0.88, 0.84, 0.86, 0.89],
      "test_retest_reliability": 0.79
    },
    "validity_evidence": {
      "convergent": "correlates r=0.72 with Indoor Environmental Quality (IEQ) index",
      "discriminant": "r=0.18 with trait neuroticism (expected to be low)",
      "known_groups": "significantly distinguishes certified green buildings from conventional buildings (p<0.001)"
    }
  },

  "comparison_instruments": [
    {
      "instrument_name": "IEQ Scale",
      "construct": "indoor environmental quality",
      "correlation_with_epr": 0.72,
      "strengths": "established in literature",
      "limitations": "longer (42 items vs 28)"
    }
  ],

  "applicable_populations": [
    "office workers in temperate climates",
    "ages 22-65",
    "English-speaking populations"
  ],

  "applicable_settings": [
    "office buildings",
    "open plan and cellular spaces",
    "temperate climate regions"
  ],

  "domains": ["A4_Light", "A5_Acoustic", "A7_Haptic_Thermal"],
  "overall_theory_links": ["IC"],
  "limitations": ["narrow age range", "single-language development"]
}

## CRITICAL METHODS EXTRACTION RULES

1. **METHODOLOGICAL FINDINGS**: Extract components and procedures as "findings" with
   claim_type: "methodological". Direction is always "descriptive".

2. **PSYCHOMETRIC PROPERTIES**: Report reliability (Cronbach's alpha, test-retest) and
   validity (convergent, discriminant, known-groups) where reported.

3. **APPLICABLE BOUNDARIES**: Document explicitly what populations and settings this
   instrument/method is designed for.

""" + VALIDATION_SUFFIX_V3


# ═══════════════════════════════════════════════════════════════════════════
# PROMPT MAP — Maps article families to complete prompts
# ═══════════════════════════════════════════════════════════════════════════

PROMPT_MAP = {
    # Empirical family
    "empirical": EMPIRICAL_PROMPT_V3,
    "empirical_v2": EMPIRICAL_PROMPT_V3,
    "observational_field": EMPIRICAL_PROMPT_V3,
    "case_study": EMPIRICAL_PROMPT_V3,
    "mixed_methods": EMPIRICAL_PROMPT_V3,

    # Synthesis family
    "meta_analysis": SYNTHESIS_PROMPT_V3,
    "systematic_review": SYNTHESIS_PROMPT_V3,
    "narrative_review": SYNTHESIS_PROMPT_V3,

    # Theoretical family
    "theoretical": THEORETICAL_PROMPT_V3,
    "conceptual_framework": THEORETICAL_PROMPT_V3,
    "thought_piece": THEORETICAL_PROMPT_V3,

    # Qualitative family
    "qualitative": QUALITATIVE_PROMPT_V3,
    "interview_study": QUALITATIVE_PROMPT_V3,
    "ethnographic": QUALITATIVE_PROMPT_V3,
    "grounded_theory": QUALITATIVE_PROMPT_V3,
    "phenomenological": QUALITATIVE_PROMPT_V3,

    # Methods
    "methods": METHODS_PROMPT_V3,
    "instrument": METHODS_PROMPT_V3,
    "protocol": METHODS_PROMPT_V3,
    "guidelines": METHODS_PROMPT_V3,
    "scale_development": METHODS_PROMPT_V3,
    "validation": METHODS_PROMPT_V3,
}

# Family map for quality thresholds and validation
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
    "instrument": "methods",
    "protocol": "methods",
    "guidelines": "methods",
    "scale_development": "methods",
    "validation": "methods",
}


# ═══════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def get_prompt_for_family(family: str) -> str:
    """
    Return the appropriate complete prompt (base + family + validation suffix)
    for the given article family or article type.

    Args:
        family: Article type or family name (e.g., "empirical_v2", "meta_analysis", "theoretical")

    Returns:
        Complete prompt string ready for Gemini API
    """
    if family not in PROMPT_MAP:
        raise ValueError(
            f"Unknown article family/type: {family}. "
            f"Valid options: {list(PROMPT_MAP.keys())}"
        )
    return PROMPT_MAP[family]


def get_outcome_vocab_hint(domains: Optional[List[str]] = None) -> str:
    """
    Load outcome_vocab.json and return a compact hint list for the specified domains.
    If no domains specified, returns a sample across all 8 domains.

    This hint is meant to be injected into prompts to guide outcome vocabulary usage.

    Args:
        domains: list of domain IDs (e.g., ['cog', 'affect', 'physio'])
                 or None to use all domains

    Returns:
        Formatted string with outcome vocabulary samples, suitable for prompt injection
    """
    # Hardcoded outcome vocab sample based on the first 20 entries
    # In production, this would load outcome_vocab.json dynamically
    vocab_sample = {
        "cog": [
            "cog.attention",
            "cog.attention.broad",
            "cog.memory",
            "cog.working_memory",
            "cog.cognitive_load"
        ],
        "affect": [
            "affect.anxiety",
            "affect.mood",
            "affect.stress",
            "affect.arousal",
            "affect.valence"
        ],
        "behav": [
            "behav.activity_level",
            "behav.approach_avoidance",
            "behav.exploration",
            "behav.social_interaction"
        ],
        "social": [
            "social.affiliation",
            "social.cooperation",
            "social.trust",
            "social.engagement"
        ],
        "physio": [
            "physio.cortisol",
            "physio.heart_rate",
            "physio.blood_pressure",
            "physio.skin_conductance",
            "physio.sleep_quality"
        ],
        "neural": [
            "neural.fmri_activation",
            "neural.eeg_oscillations",
            "neural.brain_structure",
            "neural.network_connectivity"
        ],
        "health": [
            "health.wellbeing",
            "health.life_satisfaction",
            "health.burnout",
            "health.physical_health"
        ],
        "env": [
            "env.comfort",
            "env.satisfaction",
            "env.preference",
            "env.perceived_quality"
        ]
    }

    if domains is None:
        # Use all domains
        domains = list(vocab_sample.keys())
    else:
        # Filter to specified domains
        domains = [d for d in domains if d in vocab_sample]

    hint_lines = [
        "OUTCOME VOCABULARY HINTS (use specific terms from these domains):",
        ""
    ]

    for domain in sorted(domains):
        terms = vocab_sample.get(domain, [])
        if terms:
            domain_name = {
                "cog": "Cognitive",
                "affect": "Affective",
                "behav": "Behavioral",
                "social": "Social",
                "physio": "Physiological",
                "neural": "Neural",
                "health": "Health",
                "env": "Environmental"
            }.get(domain, domain)

            hint_lines.append(f"{domain_name} ({domain}):")
            for term in terms:
                hint_lines.append(f"  - {term}")
            hint_lines.append("")

    return "\n".join(hint_lines)


def validate_direction(direction: Optional[str]) -> bool:
    """
    Validate that a direction value is one of the 4 canonical values.

    Args:
        direction: Direction string to validate

    Returns:
        True if valid, False otherwise
    """
    if direction is None:
        return False
    return direction in CANONICAL_DIRECTIONS


def validate_finding_structure(finding: Dict) -> Tuple[bool, List[str]]:
    """
    Validate a finding dict against critical requirements.

    Args:
        finding: Finding dictionary to validate

    Returns:
        Tuple of (is_valid: bool, issues: List[str])
    """
    issues = []

    # Check required fields
    if not finding.get("antecedent"):
        issues.append("Missing or empty antecedent")
    elif len(finding["antecedent"]) < 5:
        issues.append("Antecedent too vague (< 5 chars)")

    if not finding.get("consequent"):
        issues.append("Missing or empty consequent")

    if not finding.get("claim_type"):
        issues.append("Missing claim_type")

    # Check direction
    direction = finding.get("direction")
    if direction and not validate_direction(direction):
        issues.append(f"Invalid direction: {direction}. Must be one of {CANONICAL_DIRECTIONS}")

    # Check for vague antecedents
    vague_terms = ["the environment", "the condition", "exposure", "intervention"]
    if finding.get("antecedent"):
        for term in vague_terms:
            if term.lower() in finding["antecedent"].lower():
                issues.append(f"Vague antecedent: contains '{term}'")
                break

    return len(issues) == 0, issues


# ═══════════════════════════════════════════════════════════════════════════
# SUCCESS CONDITIONS (as per specification)
# ═══════════════════════════════════════════════════════════════════════════

"""
SUCCESS CONDITIONS for revised_prompts_v3.py:

SC-1: Direction Canonical Values
  - Direction field uses only 4 canonical values (increase/decrease/no_effect/mixed)
  - Across 100 extracted findings: 0% invalid direction values
  - Validation: Check enum in extraction_template.v2.schema.json

SC-2: Antecedent Specificity
  - Vague antecedents ("the environment", "condition", "exposure") < 10% (was 32% in v2)
  - Measurable specificity: Can someone replicate from antecedent description?
  - Validation: Manual review of sample of 50 findings

SC-3: Sample Size Coverage (Empirical Papers Only)
  - >80% of empirical findings have sample_size filled (was 18% in v2)
  - sample_size_source properly set (reported/inferred/estimated)
  - Validation: Count non-null sample_size across empirical family

SC-4: Theory Linkage
  - >50% of papers with theory mentions have theory_commitments[] (was ~20% in v2)
  - Each commitment has required fields: theory_name, commitment_type, specific_claim
  - Validation: Papers citing "Attention Restoration Theory" should have ART commitment

SC-5: Mechanism Chains
  - >60% of papers with causal claims have mechanism_chain with 2+ steps (was ~15% in v2)
  - Each step has consecutive integers, from_construct, to_construct, mechanism_type, evidence_strength
  - Validation: count findings with claim_type="causal" having mechanism_chain.length >= 2

SC-6: Instrument Naming
  - >70% of empirical papers have instruments_used[] with specific names (was ~45% in v2)
  - NOT generic terms: "questionnaire", "survey", "scale", "test"
  - GOOD: "PANAS", "NASA-TLX", "STAI", "polysomnography"
  - Validation: grep for generic terms in instruments_used[].name

SC-7: Schema Compliance
  - 100% of extracted JSON matches extraction_template.v2.schema.json
  - All required fields present: doi, article_type, title, authors, findings
  - Finding IDs match pattern ^[A-Z0-9_]+$
  - All enums properly constrained
  - Validation: JSON schema validator

SC-8: No Critical Nulls
  - No finding with null antecedent or consequent
  - No finding with null claim_type
  - For empirical: p_value and effect_size should not BOTH be null (graceful degradation rule)
  - Validation: count null antecedents/consequents across sample
"""


if __name__ == "__main__":
    # Quick validation test
    print("REVISED PROMPTS V3.0 — ATLAS Evidence Synthesis System")
    print("=" * 70)
    print(f"\nPrompt families available: {len(PROMPT_MAP)} types")
    print(f"Article families: {len(ARTICLE_FAMILIES)}")
    print(f"\nMechanism types: {MECHANISM_TYPES}")
    print(f"Evidence strengths: {EVIDENCE_STRENGTHS}")
    print(f"Canonical directions: {CANONICAL_DIRECTIONS}")
    print(f"\nOutcome vocabulary hint (sample):\n{get_outcome_vocab_hint(['cog', 'affect'])}")

    # Test prompt assembly
    sample_prompt = get_prompt_for_family("empirical_v2")
    print(f"\nSample empirical prompt length: {len(sample_prompt)} chars")
    print(f"Contains validation suffix: {'FINAL VALIDATION CHECKLIST' in sample_prompt}")
