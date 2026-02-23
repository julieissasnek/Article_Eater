"""
Mechanism Belief Seeder
=======================

Seeds mechanism chains from templates into the master web of belief as linked
belief nodes with EPISTEMIC_MEDIATION constraints.

Enables MechanismPattern.traverse() to answer questions like:
  "what mechanism explains why wood is restorative?"
  "do plants and wood share the same restorative mechanism?"
  "why does natural light improve mood?"
  "how does spatial complexity affect cognition?"

Mechanism families seeded:
  ART  — Attention Restoration Theory (Kaplan 1995)
  SRT  — Stress Recovery Theory (Ulrich 1983, 1991)
  MAT4 — Natural Material Multi-Channel Convergence
  L3   — Daylight Multi-Channel Convergence
  NM   — Neuromodulatory (dopamine novelty, oxytocin social)
  DT1  — DMN/TPN Switching (salience network)

Source templates:
  DT_DIRECTED_ATTENTION_001.json, SRT1.json, MAT4_natural_material_convergence.json,
  L3_daylight_multichannel_convergence.json, NM2.json, NM3.json, DT1.json

Run:
    python3 scripts/seed_mechanism_beliefs.py
    python3 scripts/seed_mechanism_beliefs.py --dry-run
"""

from __future__ import annotations

import argparse
import logging
import sys
import os
import uuid
from dataclasses import dataclass, field
from typing import List, Optional

sys.path.insert(0, os.getcwd())

from src.services.web_accumulator import WebAccumulator
from src.services.web_of_belief import (
    Belief, Constraint, Credence,
    EpistemicLevel, BeliefStatus,
    ConstraintType, CausalDirection,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class MechanismBelief:
    belief_id: str
    content: str
    theory_id: str
    credence_value: float
    credence_uncertainty: float
    tags: List[str] = field(default_factory=list)
    causal_direction: CausalDirection = CausalDirection.MEDIATED


@dataclass
class MechanismConstraint:
    source_id: str
    target_id: str
    constraint_type: ConstraintType
    strength: float
    bidirectional: bool = False
    causal_direction: CausalDirection = CausalDirection.FORWARD
    mediator: Optional[str] = None  # mediating variable description
    evidence_ids: List[str] = field(default_factory=list)


# =============================================================================
# ART — Attention Restoration Theory  (Kaplan 1995; Berman et al. 2008)
# Source: DT_DIRECTED_ATTENTION_001.json
# =============================================================================

ART_BELIEFS: List[MechanismBelief] = [
    MechanismBelief(
        belief_id="mechanism:art:biophilic_stimulus",
        content=(
            "Biophilic stimuli (plants, wood grain, water, natural views) share a common "
            "perceptual signature — fractal spatial statistics and biological complexity — "
            "that triggers the same attentional affordance regardless of specific material. "
            "Both indoor plants and naturally-grained wood qualify as biophilic stimuli. "
            "This is the shared entry-point for both ART and SRT mechanism chains."
        ),
        theory_id="attention_restoration_theory",
        credence_value=0.80,
        credence_uncertainty=0.10,
        tags=["mechanism_node", "ART", "SRT", "shared_stimulus_class",
              "wood", "plants", "biophilia", "fractal", "biophilic_stimulus"],
        causal_direction=CausalDirection.FORWARD,
    ),
    MechanismBelief(
        belief_id="mechanism:art:soft_fascination",
        content=(
            "Biophilic stimuli engage 'soft fascination': involuntary, effortless attention "
            "to gently interesting features (moving leaves, wood grain patterns, fractal edges). "
            "Soft fascination does not deplete directed-attention resources, unlike hard "
            "fascination from urban media or screens. (Kaplan 1995)"
        ),
        theory_id="attention_restoration_theory",
        credence_value=0.78,
        credence_uncertainty=0.12,
        tags=["mechanism_node", "ART", "soft_fascination", "involuntary_attention",
              "fractal_fluency", "restorative"],
    ),
    MechanismBelief(
        belief_id="mechanism:art:involuntary_attention",
        content=(
            "Involuntary attention, sustained by soft fascination, allows the directed-attention "
            "system to rest. The prefrontal inhibitory control load drops when involuntary "
            "attention takes over perceptual processing. (Kaplan & Kaplan 1989)"
        ),
        theory_id="attention_restoration_theory",
        credence_value=0.75,
        credence_uncertainty=0.14,
        tags=["mechanism_node", "ART", "involuntary_attention", "directed_attention_fatigue",
              "inhibitory_control", "prefrontal"],
    ),
    MechanismBelief(
        belief_id="mechanism:art:directed_attention_restoration",
        content=(
            "With directed attention at rest, its finite capacity replenishes. Full restorative "
            "potential requires: being-away, fascination, extent (perceiving richness), and "
            "compatibility. After exposure, directed-attention performance improves "
            "(Berman et al. 2008: d ≈ 0.5 nature walk vs. urban walk)."
        ),
        theory_id="attention_restoration_theory",
        credence_value=0.80,
        credence_uncertainty=0.10,
        tags=["mechanism_node", "ART", "restoration", "restorative", "directed_attention",
              "cognitive_restoration", "attention_restoration"],
    ),
]

# =============================================================================
# SRT — Stress Recovery Theory  (Ulrich 1983, 1991; Parsons et al. 1998)
# Source: SRT1.json
#
# Extended with the sub-cortical visual pathway that answers:
#   "why does SIGHT of nature drop sympathetic activation?"
#
# Sub-mechanism chain (all happen within ~150–500ms, before conscious awareness):
#   biophilic_stimulus
#     → visual_ecological_appraisal  (retina → superior colliculus → pulvinar)
#     → amygdala_threat_suppression  (amygdala low-threat → HPA/CRH suppressed)
#     → hpa_suppression              (norepinephrine ~ adrenaline withdrawn)
#     → positive_affect_shift        (the felt shift; Ulrich 1991)
#     → autonomic_recovery
#     → physiological_normalization
# =============================================================================

SRT_BELIEFS: List[MechanismBelief] = [
    MechanismBelief(
        belief_id="mechanism:srt:visual_ecological_appraisal",
        content=(
            "The visual system performs a rapid, sub-cortical ecological appraisal of the "
            "scene before conscious perception. The superior colliculus and pulvinar nucleus "
            "of the thalamus—a pathway bypassing primary visual cortex—scan the image for "
            "gross scene structure (open vs. enclosed, green vs. grey, animate vs. static) "
            "within 50–150ms of image onset. This 'quick and dirty' appraisal routes to the "
            "amygdala and provides the initial safety/threat signal. Natural scenes with "
            "ecological safety features (open sward, water, vegetation, no predators, no "
            "conspecific threat cues) generate a LOW-THREAT signal. Urban or cluttered scenes "
            "tend to generate NEUTRAL or AMBIGUOUS signals, keeping the threat system partially "
            "active. (LeDoux 1996; Vuilleumier 2005; colliculo-pulvinar route)"
        ),
        theory_id="stress_recovery_theory",
        credence_value=0.78,
        credence_uncertainty=0.13,
        tags=["mechanism_node", "SRT", "visual_pathway", "superior_colliculus", "pulvinar",
              "thalamus", "subcortical", "ecological_appraisal", "sight", "vision",
              "fast_pathway", "threat_detection"],
        causal_direction=CausalDirection.FORWARD,
    ),
    MechanismBelief(
        belief_id="mechanism:srt:amygdala_threat_suppression",
        content=(
            "The basolateral amygdala receives the fast thalamo-amygdala signal and the "
            "slower cortical analysis. For biophilic scenes, both routes produce LOW threat "
            "encoding: the amygdala generates minimal CRH (corticotropin-releasing hormone) "
            "output to the hypothalamus. This is the critical step: the amygdala is the "
            "'gate' — its output level determines whether the HPA axis is activated. "
            "Low amygdala output = HPA gate stays CLOSED = no cortisol cascade initiated. "
            "Ulrich (1983) showed this produces measurable ANS changes within 4–7 minutes "
            "of nature image viewing — timescale consistent with amygdala appraisal, not "
            "slow cortical deliberation. (LeDoux 2000; Ochsner & Gross 2005)"
        ),
        theory_id="stress_recovery_theory",
        credence_value=0.76,
        credence_uncertainty=0.14,
        tags=["mechanism_node", "SRT", "amygdala", "HPA_gate", "CRH", "threat_suppression",
              "basolateral_amygdala", "hypothalamus", "subcortical", "ecological_safety"],
    ),
    MechanismBelief(
        belief_id="mechanism:srt:hpa_suppression",
        content=(
            "With the amygdala's CRH output suppressed, the hypothalamic–pituitary–adrenal "
            "(HPA) axis is not activated: ACTH release from the pituitary is prevented, and "
            "the adrenal cortex does not secrete cortisol. In parallel, the locus coeruleus "
            "(norepinephrine source) reduces firing rate. The result is a withdrawal of "
            "sympathetic drive: norepinephrine and adrenaline levels fall, reducing cardiac "
            "output and peripheral vasoconstriction. The answer to 'where does sympathetic "
            "activation drop come from?' is HERE — not from conscious relaxation, but from "
            "the HPA axis simply not being activated in the first place. The seen environment "
            "told the amygdala 'safe', and the amygdala stopped the stress cascade before "
            "it reached the bloodstream. (Ulrich 1983: 4-min HR/blood pressure recovery in "
            "nature vs. urban film clips)"
        ),
        theory_id="stress_recovery_theory",
        credence_value=0.80,
        credence_uncertainty=0.11,
        tags=["mechanism_node", "SRT", "HPA_axis", "ACTH", "cortisol", "norepinephrine",
              "adrenaline", "locus_coeruleus", "sympathetic", "sight", "vision",
              "stress_recovery", "sympathetic_withdrawal",  "the_magic"],
    ),
    MechanismBelief(
        belief_id="mechanism:srt:positive_affect_shift",
        content=(
            "As HPA/sympathetic activation subsides, negative affect (anxiety, tension) "
            "decreases and positive valence increases — felt as 'calming' or 'peaceful'. "
            "This affect shift is the conscious experience of what the sub-cortical pathway "
            "already initiated: it follows the amygdala suppression, not the other way around. "
            "(Ulrich et al. 1991; scope: amplified when baseline stress is elevated)"
        ),
        theory_id="stress_recovery_theory",
        credence_value=0.82,
        credence_uncertainty=0.09,
        tags=["mechanism_node", "SRT", "positive_affect", "stress_recovery",
              "affective_pathway", "restorative", "calming"],
    ),
    MechanismBelief(
        belief_id="mechanism:srt:autonomic_recovery",
        content=(
            "Positive affect shift consolidates parasympathetic rebound: vagal tone increases, "
            "heart rate and blood pressure continue falling toward baseline. The ANS returns "
            "to homeostasis faster in natural vs. urban environments (Parsons et al. 1998). "
            "This is the parasympathetic phase — the sympathetic withdrawal (HPA suppression) "
            "already began 3–5 minutes earlier."
        ),
        theory_id="stress_recovery_theory",
        credence_value=0.78,
        credence_uncertainty=0.11,
        tags=["mechanism_node", "SRT", "autonomic_recovery", "cortisol", "HPA_axis",
              "heart_rate", "parasympathetic", "vagal_tone", "sympathetic"],
    ),
    MechanismBelief(
        belief_id="mechanism:srt:physiological_normalization",
        content=(
            "Autonomic recovery leads to physiological normalization: cortisol, blood "
            "pressure, and heart rate return to pre-stress baseline. This is the measurable "
            "endpoint of SRT. Effect amplified when baseline stress is elevated. "
            "(meta-analytic d ≈ 0.4–0.6; Ulrich et al. 1991)"
        ),
        theory_id="stress_recovery_theory",
        credence_value=0.80,
        credence_uncertainty=0.10,
        tags=["mechanism_node", "SRT", "physiological_normalization", "homeostasis",
              "restorative", "stress_reduction", "cortisol"],
    ),
]

# =============================================================================
# MAT4 — Natural Material Multi-Channel Convergence
# Source: MAT4_natural_material_convergence.json
# (wood, stone, leather — multi-sensory biophilic signal)
# =============================================================================

MAT4_BELIEFS: List[MechanismBelief] = [
    MechanismBelief(
        belief_id="mechanism:mat4:multisensory_biophilic_signal",
        content=(
            "Natural materials (wood grain, stone texture, organic forms) generate convergent "
            "multi-sensory signals — visual fractal statistics, haptic warmth/texture, olfactory "
            "complexity — that together exceed any single channel. This multi-channel convergence "
            "is the mechanism by which natural materials produce stronger restorative effects "
            "than synthetic alternatives matched on any single dimension. (MAT4 template; "
            "Joye & van den Berg 2011)"
        ),
        theory_id="biophilic_design",
        credence_value=0.75,
        credence_uncertainty=0.13,
        tags=["mechanism_node", "MAT4", "biophilic_stimulus", "multisensory", "wood",
              "natural_materials", "convergent_benefit", "fractal"],
    ),
    MechanismBelief(
        belief_id="mechanism:mat4:hedonic_fluency",
        content=(
            "Multi-modal natural material signals produce processing fluency — the brain "
            "processes familiar fractal/organic statistics with less prediction error, "
            "generating positive hedonic tone and reduced cognitive load. This fluency "
            "effect bridges the MAT4 stimulus to both ART (soft fascination) and SRT "
            "(positive affect) entry points."
        ),
        theory_id="biophilic_design",
        credence_value=0.72,
        credence_uncertainty=0.15,
        tags=["mechanism_node", "MAT4", "processing_fluency", "prediction_error",
              "hedonic", "wood", "natural_materials"],
    ),
]

# =============================================================================
# L3 — Daylight Multi-Channel Convergence
# Source: L3_daylight_multichannel_convergence.json
# =============================================================================

L3_BELIEFS: List[MechanismBelief] = [
    MechanismBelief(
        belief_id="mechanism:l3:circadian_signal",
        content=(
            "Daylight provides the primary zeitgeber for the circadian system via "
            "melanopsin-containing ipRGCs sensitive to short-wavelength (~480nm) light. "
            "Morning bright light suppresses melatonin and advances phase; insufficient "
            "daylight causes circadian drift, mood dysregulation, and cognitive slowing. "
            "(L3 template; Czeisler et al. 1989)"
        ),
        theory_id="circadian_regulation",
        credence_value=0.85,
        credence_uncertainty=0.08,
        tags=["mechanism_node", "L3", "circadian", "daylight", "melatonin",
              "ipRGC", "light", "mood"],
    ),
    MechanismBelief(
        belief_id="mechanism:l3:visual_task_performance",
        content=(
            "Appropriate daylight levels (300–500 lux at task plane) reduce visual "
            "accommodation effort and discomfort glare, improving sustained visual task "
            "performance and reducing eye fatigue. This is the direct ergonomic pathway "
            "of daylight, distinct from the circadian pathway."
        ),
        theory_id="circadian_regulation",
        credence_value=0.82,
        credence_uncertainty=0.10,
        tags=["mechanism_node", "L3", "daylight", "visual_performance", "glare",
              "eye_fatigue", "task_performance", "light"],
    ),
    MechanismBelief(
        belief_id="mechanism:l3:mood_alertness_convergence",
        content=(
            "Daylight produces convergent mood and alertness benefits via three concurrent "
            "pathways: (1) circadian phase alignment → improved sleep → positive mood; "
            "(2) ipRGC-driven serotonin synthesis → direct mood uplift; "
            "(3) reduced visual fatigue → sustained attention. "
            "Multi-channel convergence explains robust effect sizes in workplace studies. "
            "(Boubekri et al. 2014; d ≈ 0.4–0.7)"
        ),
        theory_id="circadian_regulation",
        credence_value=0.78,
        credence_uncertainty=0.12,
        tags=["mechanism_node", "L3", "daylight", "mood", "alertness", "serotonin",
              "circadian", "convergent_benefit", "restorative"],
    ),
]

# =============================================================================
# NM — Neuromodulatory mechanisms
# Source: NM2.json (dopamine/novelty), NM3.json (oxytocin/social)
# =============================================================================

NM_BELIEFS: List[MechanismBelief] = [
    MechanismBelief(
        belief_id="mechanism:nm:novelty_dopamine",
        content=(
            "Environmental novelty triggers mesolimbic dopamine release via prediction error "
            "signalling in the VTA. Moderate novelty (not overwhelming) produces approach "
            "motivation, exploratory behaviour, and enhanced encoding. Architectural novelty "
            "at optimal level (curved forms, unexplored paths) activates this route. "
            "(NM2 template; Berlyne 1960; Watanabe et al. 2019)"
        ),
        theory_id="neuromodulatory",
        credence_value=0.76,
        credence_uncertainty=0.13,
        tags=["mechanism_node", "NM2", "dopamine", "novelty", "prediction_error",
              "VTA", "mesolimbic", "exploration", "curiosity"],
    ),
    MechanismBelief(
        belief_id="mechanism:nm:oxytocin_social",
        content=(
            "Social environmental features (visible social activity, semi-public spaces, "
            "threshold conditions enabling encounter) trigger oxytocin release, promoting "
            "prosocial behaviour, trust, and affiliation. Architecture that enables "
            "voluntary social encounter at appropriate interpersonal distance activates "
            "this pathway. (NM3 template; Kosfeld et al. 2005)"
        ),
        theory_id="neuromodulatory",
        credence_value=0.70,
        credence_uncertainty=0.16,
        tags=["mechanism_node", "NM3", "oxytocin", "social", "prosocial",
              "trust", "affiliation", "spatial_encounter"],
    ),
]

# =============================================================================
# DT1 — DMN/TPN Switch  (salience-network triggered)
# Source: DT1.json
# =============================================================================

DT1_BELIEFS: List[MechanismBelief] = [
    MechanismBelief(
        belief_id="mechanism:dt1:salience_detection",
        content=(
            "Salient environmental events (unexpected sounds, movement at periphery, "
            "abrupt light changes) activate the anterior insula / anterior cingulate "
            "salience network, which mediates the switch from default-mode (mind-wandering) "
            "to task-positive network (focused cognition). Architecture that reduces false "
            "salience alarms reduces this costly switching. (DT1 template)"
        ),
        theory_id="DMN_TPN_DYNAMICS",
        credence_value=0.78,
        credence_uncertainty=0.12,
        tags=["mechanism_node", "DT1", "salience_network", "DMN", "TPN",
              "anterior_insula", "ACC", "attention", "distraction"],
    ),
    MechanismBelief(
        belief_id="mechanism:dt1:network_switching",
        content=(
            "Frequent DMN→TPN switching driven by environmental distractors (acoustic "
            "intrusions, visual interruptions) imposes metabolic cost and reduces sustained "
            "attention performance. Environments minimising false salience allow TPN "
            "engagement to persist, benefiting focused work. (DT1 template; Corbetta & "
            "Shulman 2002)"
        ),
        theory_id="DMN_TPN_DYNAMICS",
        credence_value=0.75,
        credence_uncertainty=0.13,
        tags=["mechanism_node", "DT1", "DMN", "TPN", "network_switching",
              "distraction", "attention", "cognitive_cost"],
    ),
]

# =============================================================================
# OLF_SRT — Olfactory parallel route into SRT
# Source: OLF1_olfactory_pe_transition.json + Ulrich SRT
#
# The olfactory route to the amygdala is MORE DIRECT than the visual route:
# it bypasses the thalamus entirely (olfactory bulb → piriform cortex → amygdala)
# making it the fastest sensory route to the HPA gate.
# Wood VOCs (terpenes like alpha-pinene from pine, cedrol from cedar, guaiacol
# from wood smoke) are known to activate this pathway.
# =============================================================================

OLF_SRT_BELIEFS: List[MechanismBelief] = [
    MechanismBelief(
        belief_id="mechanism:srt:olfactory_ecological_appraisal",
        content=(
            "Wood and natural materials release volatile organic compounds (VOCs) — terpenes "
            "such as alpha-pinene (pine, cedar), cedrol (cedar), limonene (citrus), and "
            "guaiacol (wood smoke) — that are detected by olfactory receptor neurons in the "
            "nasal epithelium. Unlike all other senses, olfaction reaches the amygdala and "
            "hippocampus WITHOUT a thalamic relay: the pathway is olfactory bulb → "
            "piriform cortex (primary olfactory cortex) → basolateral amygdala, with only "
            "2–3 synapses. This makes olfaction the FASTEST sensory route to the HPA gate. "
            "(Gottfried et al. 2002; Herz & Engen 1996; OLF1 template; Li et al. 2010 "
            "on alpha-pinene and ANS)"
        ),
        theory_id="stress_recovery_theory",
        credence_value=0.72,
        credence_uncertainty=0.16,
        tags=["mechanism_node", "SRT", "OLF1", "olfactory", "terpenes", "VOC",
              "alpha_pinene", "cedrol", "wood_smell", "wood_scent",
              "olfactory_bulb", "piriform_cortex", "amygdala", "no_thalamic_relay",
              "wood", "ecological_safety", "fastest_pathway"],
        causal_direction=CausalDirection.FORWARD,
    ),
    MechanismBelief(
        belief_id="mechanism:srt:olfactory_safety_classification",
        content=(
            "Piriform cortex performs a rapid, pre-conscious pattern-match of the incoming "
            "VOC mixture against an evolved library of ecological odour categories. This is "
            "NOT perceptual fluency (which operates via cortical prediction error) — it is a "
            "SEPARATE, phylogenetically older classification system tuned by natural selection "
            "to survival-critical scent categories:\n\n"
            "  SAFE/SHELTER: wood terpenes (alpha-pinene, cedrol), fresh-cut grass "
            "(cis-3-hexenal), petrichor, clean water, ripe fruit — signals 'living "
            "habitat, structural shelter available, no fire, no decay'\n\n"
            "  THREAT/AVOIDANCE: predator urine (trimethylamine, 2-phenylethylamine), smoke "
            "(furfural, benzaldehyde), putrefaction (cadaverine, putrescine), conspecific "
            "stress-sweat (androstadienone) — signals 'immediate danger, predator present, "
            "fire, death nearby'\n\n"
            "  NEUTRAL/UNCERTAIN: synthetic chemicals, novel compounds, mixed urban odours — "
            "no clear classification, amygdala stays at baseline vigilance\n\n"
            "Wood VOCs (alpha-pinene, cedrol, guaiacol at low concentrations) are classified "
            "SAFE/SHELTER: they signal 'I can hide here, this is a living structure, no "
            "predator, no fire.' This classification happens in piriform cortex within "
            "~100–200ms and produces a SUPPRESSIVE signal to the amygdala's threat-detection "
            "circuitry. The classification is largely innate (cross-cultural studies show "
            "consistent valence for wood/grass/predator odours) but is MODULATED by associative "
            "memory: hippocampal episodic associations can amplify or attenuate the piriform "
            "classification (e.g., wood smoke = campfire memory = safe; OR wood smoke = "
            "house-fire memory = threat). "
            "(Sezille et al. 2014; Herz & Engen 1996; Doty 2015; Zhou & Chen 2009 "
            "on fear-related chemosignals)"
        ),
        theory_id="stress_recovery_theory",
        credence_value=0.70,
        credence_uncertainty=0.17,
        tags=["mechanism_node", "SRT", "olfactory", "piriform_cortex",
              "safety_classification", "ecological_odour_categories",
              "evolved_classification", "phylogenetic", "safe_shelter",
              "threat_avoidance", "wood_VOC", "predator_urine",
              "hippocampal_modulation", "associative_memory",
              "innate_but_modulated", "pre_conscious"],
        causal_direction=CausalDirection.FORWARD,
    ),
]

ALL_MECHANISM_BELIEFS = (
    ART_BELIEFS + SRT_BELIEFS + OLF_SRT_BELIEFS +
    MAT4_BELIEFS + L3_BELIEFS + NM_BELIEFS + DT1_BELIEFS
)

# =============================================================================
# CONSTRAINTS
# =============================================================================

def build_constraints() -> List[MechanismConstraint]:
    constraints = []

    ART_ENTRY = "mechanism:art:biophilic_stimulus"
    # SRT now enters via the visual pathway, not directly at positive_affect_shift
    SRT_ENTRY = "mechanism:srt:visual_ecological_appraisal"
    MAT4_ENTRY = "mechanism:mat4:multisensory_biophilic_signal"

    # ── Biophilic stimuli → ART & SRT & MAT4 entry points ───────────────────
    for env_id in [
        "env.ae.wood_prominent",
        "env.ae.indoor_plants",
        "env.generic.biophilia",
        "env.v2a_098.natural_materials_wood_stone",
    ]:
        constraints.append(MechanismConstraint(
            source_id=env_id, target_id=ART_ENTRY,
            constraint_type=ConstraintType.SUPPORTS, strength=0.75,
        ))
        constraints.append(MechanismConstraint(
            source_id=env_id, target_id=SRT_ENTRY,
            constraint_type=ConstraintType.SUPPORTS, strength=0.80,
        ))
        constraints.append(MechanismConstraint(
            source_id=env_id, target_id=MAT4_ENTRY,
            constraint_type=ConstraintType.SUPPORTS, strength=0.72,
        ))

    # ── ART intra-chain ──────────────────────────────────────────────────────
    art_chain = [
        "mechanism:art:biophilic_stimulus",
        "mechanism:art:soft_fascination",
        "mechanism:art:involuntary_attention",
        "mechanism:art:directed_attention_restoration",
    ]
    for src, tgt in zip(art_chain, art_chain[1:]):
        constraints.append(MechanismConstraint(
            source_id=src, target_id=tgt,
            constraint_type=ConstraintType.EPISTEMIC_MEDIATION, strength=0.78,
            causal_direction=CausalDirection.MEDIATED,
            mediator="ART causal step (Kaplan 1995)",
        ))

    # ── SRT full chain: visual pathway + affect + autonomic ──────────────────
    # Sub-cortical visual appraisal chain (the 'magic' the user asked about)
    srt_visual_chain = [
        ("mechanism:srt:visual_ecological_appraisal",
         "mechanism:srt:amygdala_threat_suppression",
         "retina → superior colliculus → pulvinar → basolateral amygdala "
         "(fast sub-cortical route, ~50–150ms; LeDoux 1996)"),
        ("mechanism:srt:amygdala_threat_suppression",
         "mechanism:srt:hpa_suppression",
         "low amygdala CRH output → hypothalamus does not activate HPA axis; "
         "locus coeruleus firing reduces → norepinephrine withdrawn"),
        ("mechanism:srt:hpa_suppression",
         "mechanism:srt:positive_affect_shift",
         "sympathetic withdrawal is consciously experienced as calming/positive affect; "
         "followed by parasympathetic recovery"),
        ("mechanism:srt:positive_affect_shift",
         "mechanism:srt:autonomic_recovery",
         "vagal tone increases, cardiac output and vasoconstriction continue falling "
         "(Ulrich 1983; Parsons et al. 1998)"),
        ("mechanism:srt:autonomic_recovery",
         "mechanism:srt:physiological_normalization",
         "HR, BP, cortisol reach pre-stress baseline (SRT endpoint; d ≈ 0.4–0.6)"),
    ]
    for src, tgt, med in srt_visual_chain:
        constraints.append(MechanismConstraint(
            source_id=src, target_id=tgt,
            constraint_type=ConstraintType.EPISTEMIC_MEDIATION, strength=0.78,
            causal_direction=CausalDirection.MEDIATED,
            mediator=med,
        ))

    # ── MAT4 chain → ART and SRT entry ──────────────────────────────────────
    constraints.append(MechanismConstraint(
        source_id="mechanism:mat4:multisensory_biophilic_signal",
        target_id="mechanism:mat4:hedonic_fluency",
        constraint_type=ConstraintType.EPISTEMIC_MEDIATION, strength=0.72,
        causal_direction=CausalDirection.MEDIATED,
        mediator="processing fluency from natural material statistics",
    ))
    constraints.append(MechanismConstraint(
        source_id="mechanism:mat4:hedonic_fluency",
        target_id="mechanism:art:soft_fascination",
        constraint_type=ConstraintType.SUPPORTS, strength=0.68,
    ))
    constraints.append(MechanismConstraint(
        source_id="mechanism:mat4:hedonic_fluency",
        target_id="mechanism:srt:positive_affect_shift",
        constraint_type=ConstraintType.SUPPORTS, strength=0.70,
    ))

    # ── L3 daylight chain ────────────────────────────────────────────────────
    constraints.append(MechanismConstraint(
        source_id="mechanism:l3:circadian_signal",
        target_id="mechanism:l3:mood_alertness_convergence",
        constraint_type=ConstraintType.EPISTEMIC_MEDIATION, strength=0.80,
        causal_direction=CausalDirection.MEDIATED,
        mediator="circadian phase alignment → serotonin → mood",
    ))
    constraints.append(MechanismConstraint(
        source_id="mechanism:l3:visual_task_performance",
        target_id="mechanism:l3:mood_alertness_convergence",
        constraint_type=ConstraintType.SUPPORTS, strength=0.74,
    ))
    # Daylight convergence also feeds SRT (ecological safety signal)
    constraints.append(MechanismConstraint(
        source_id="mechanism:l3:mood_alertness_convergence",
        target_id="mechanism:srt:positive_affect_shift",
        constraint_type=ConstraintType.SUPPORTS, strength=0.65,
    ))

    # ── Olfactory parallel SRT entry ─────────────────────────────────────────
    # Olfactory route: VOC detection → safety classification → amygdala suppression
    # Unlike the visual route (ecological appraisal → amygdala directly), the olfactory
    # route has a distinct CLASSIFICATION step in piriform cortex where the VOC mixture
    # is matched against evolved safe/threat categories.
    constraints.append(MechanismConstraint(
        source_id="mechanism:srt:olfactory_ecological_appraisal",
        target_id="mechanism:srt:olfactory_safety_classification",
        constraint_type=ConstraintType.EPISTEMIC_MEDIATION, strength=0.74,
        causal_direction=CausalDirection.MEDIATED,
        mediator=(
            "olfactory bulb → piriform cortex: VOC molecules bind to receptor neurons, "
            "signal reaches piriform cortex within ~100ms (no thalamic relay)"
        ),
    ))
    constraints.append(MechanismConstraint(
        source_id="mechanism:srt:olfactory_safety_classification",
        target_id="mechanism:srt:amygdala_threat_suppression",
        constraint_type=ConstraintType.EPISTEMIC_MEDIATION, strength=0.72,
        causal_direction=CausalDirection.MEDIATED,
        mediator=(
            "piriform cortex → basolateral amygdala: SAFE/SHELTER classification "
            "(wood terpenes = 'no predator, no fire, shelter available') produces "
            "SUPPRESSIVE signal to amygdala threat circuitry (~100–200ms)"
        ),
    ))

    # ── NM mechanisms ────────────────────────────────────────────────────────
    constraints.append(MechanismConstraint(
        source_id="mechanism:nm:novelty_dopamine",
        target_id="mechanism:art:involuntary_attention",
        constraint_type=ConstraintType.SUPPORTS, strength=0.60,
        mediator="curiosity-driven involuntary attention engagement",
    ))

    # ── DT1 distraction chain ────────────────────────────────────────────────
    constraints.append(MechanismConstraint(
        source_id="mechanism:dt1:salience_detection",
        target_id="mechanism:dt1:network_switching",
        constraint_type=ConstraintType.EPISTEMIC_MEDIATION, strength=0.76,
        causal_direction=CausalDirection.MEDIATED,
        mediator="anterior insula salience network DMN→TPN switch",
    ))
    # Excessive switching depletes directed attention (inverse of ART restoration)
    constraints.append(MechanismConstraint(
        source_id="mechanism:dt1:network_switching",
        target_id="mechanism:art:directed_attention_restoration",
        constraint_type=ConstraintType.COHERENCE_SUPPORT, strength=0.65,
        bidirectional=True,
        mediator="directed-attention depletion ↔ restoration",
    ))

    # ── ART–SRT cross-chain bridge: same biophilic stimulus activates both ──
    constraints.append(MechanismConstraint(
        source_id="mechanism:art:soft_fascination",
        target_id="mechanism:srt:positive_affect_shift",
        constraint_type=ConstraintType.COHERENCE_SUPPORT, strength=0.72,
        bidirectional=True,
        mediator="dual-process biophilic convergence (Ulrich 1991 + Kaplan 1995)",
    ))
    constraints.append(MechanismConstraint(
        source_id="mechanism:art:directed_attention_restoration",
        target_id="mechanism:srt:physiological_normalization",
        constraint_type=ConstraintType.COHERENCE_SUPPORT, strength=0.65,
        bidirectional=True,
        mediator="convergent restorative endpoint (ART cognitive + SRT physiological)",
    ))

    return constraints


# =============================================================================
# SEEDER
# =============================================================================

def seed(dry_run: bool = False) -> None:
    logger.info("Loading master web...")
    acc = WebAccumulator()
    web, _ = acc.get_master_web()

    if web is None:
        logger.error("No master web found. Run the extraction pipeline first.")
        sys.exit(1)

    logger.info(
        f"Loaded web: {len(web.beliefs)} beliefs, "
        f"{len(web.constraints)} constraints"
    )

    # ── Seed mechanism beliefs ──────────────────────────────────────────────
    beliefs_added = beliefs_skipped = 0

    for mb in ALL_MECHANISM_BELIEFS:
        if mb.belief_id in web.beliefs:
            logger.info(f"  SKIP (exists): {mb.belief_id}")
            beliefs_skipped += 1
            continue

        belief = Belief(
            belief_id=mb.belief_id,
            content=mb.content,
            level=EpistemicLevel.THEORETICAL,
            status=BeliefStatus.ESTABLISHED,
            credence=Credence(
                value=mb.credence_value,
                uncertainty=mb.credence_uncertainty,
                n_supporting=3,
            ),
            theory_id=mb.theory_id,
            domain="environmental_psychology",
            tags=list(mb.tags),
            paper_ids=[],
        )
        belief.causal_direction = mb.causal_direction

        if not dry_run:
            web.add_belief(belief)

        logger.info(f"  {'[DRY]' if dry_run else 'ADD'} belief: {mb.belief_id}")
        beliefs_added += 1

    # ── Seed constraints ────────────────────────────────────────────────────
    constraints_added = constraints_skipped = 0
    all_constraints = build_constraints()

    existing_keys = {
        (c.source_id, c.target_id, c.constraint_type)
        for c in web.constraints.values()
    }

    for mc in all_constraints:
        key = (mc.source_id, mc.target_id, mc.constraint_type)
        if key in existing_keys:
            logger.info(
                f"  SKIP (exists): {mc.source_id} → {mc.target_id} "
                f"[{mc.constraint_type.value}]"
            )
            constraints_skipped += 1
            continue

        # Skip if either endpoint isn't a known belief node (avoids FK violation)
        if not dry_run:
            if mc.source_id not in web.beliefs and not mc.source_id.startswith("mechanism:"):
                logger.warning(
                    f"  SKIP (source not a belief node): {mc.source_id} → {mc.target_id}"
                )
                constraints_skipped += 1
                continue
            if mc.target_id not in web.beliefs and not mc.target_id.startswith("mechanism:"):
                logger.warning(
                    f"  SKIP (target not a belief node): {mc.source_id} → {mc.target_id}"
                )
                constraints_skipped += 1
                continue

        constraint = Constraint(
            constraint_id=f"mech_seed_{uuid.uuid4().hex[:12]}",
            source_id=mc.source_id,
            target_id=mc.target_id,
            constraint_type=mc.constraint_type,
            strength=mc.strength,
            bidirectional=mc.bidirectional,
            evidence_ids=list(mc.evidence_ids),
            causal_direction=mc.causal_direction,
            mediator=mc.mediator,
        )

        if not dry_run:
            web.add_constraint(constraint)

        arrow = "↔" if mc.bidirectional else "→"
        logger.info(
            f"  {'[DRY]' if dry_run else 'ADD'} constraint: "
            f"{mc.source_id} {arrow} {mc.target_id} "
            f"[{mc.constraint_type.value}] s={mc.strength}"
        )
        constraints_added += 1
        existing_keys.add(key)

    # ── Persist ─────────────────────────────────────────────────────────────
    if not dry_run and (beliefs_added > 0 or constraints_added > 0):
        logger.info("Saving to master web db...")
        from src.services.db_locator import resolve_web_db
        from src.services.web_persistence import WebPersistenceService
        db_path = resolve_web_db(prefer="integrated")
        svc = WebPersistenceService(str(db_path))
        master_id = svc.get_master_web_id()
        if master_id:
            svc.save_web(web, master_id)
            logger.info("Saved.")
        else:
            logger.error("Could not find master web ID for saving.")
            sys.exit(1)

    print()
    print("=" * 65)
    print(f"Mechanism seeder {'[DRY RUN]' if dry_run else 'COMPLETE'}")
    print(f"  Beliefs    : {beliefs_added} added, {beliefs_skipped} skipped")
    print(f"  Constraints: {constraints_added} added, {constraints_skipped} skipped")
    if not dry_run and beliefs_added + constraints_added > 0:
        print()
        print("Mechanism families now seeded:")
        print("  ART  — Attention Restoration (Kaplan 1995)")
        print("  SRT  — Stress Recovery (Ulrich 1983, 1991)")
        print("  MAT4 — Natural Material Multi-Channel Convergence")
        print("  L3   — Daylight Multi-Channel Convergence")
        print("  NM   — Neuromodulatory (dopamine / oxytocin)")
        print("  DT1  — DMN/TPN Switching (salience network)")
        print()
        print("QA can now answer:")
        print("  • 'what mechanism explains why wood is restorative?'")
        print("  • 'do plants and wood share the same restorative mechanism?'")
        print("  • 'why does natural light improve mood?'")
        print("  • 'how does distraction impair focused attention?'")
    print("=" * 65)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "Seed ART/SRT/MAT4/L3/NM/DT1 mechanism beliefs into the master web of belief"
        )
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without writing to the database",
    )
    args = parser.parse_args()
    seed(dry_run=args.dry_run)
