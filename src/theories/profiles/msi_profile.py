"""
Multisensory Integration — Theory Profile for LLM Matching.

TIER 1.10: The brain integrates signals across modalities using inverse
effectiveness, temporal/spatial congruence, and reliability weighting.
Architectural experience is inherently multisensory.
"""

THEORY_ID = "framework:multisensory_integration"
THEORY_NAME = "Multisensory Integration"

CORE_MECHANISM = """
The brain INTEGRATES information across sensory modalities using:
  - INVERSE EFFECTIVENESS: Weak unisensory signals benefit MOST from
    combination. A dim visual cue + quiet sound together > each alone.
  - TEMPORAL CONGRUENCE: Signals arriving together are bound as one event.
  - SPATIAL CONGRUENCE: Signals from same location are preferentially bound.
  - RELIABILITY WEIGHTING: More precise modalities get more weight in the
    integrated percept (Bayesian cue integration).

NEURAL SUBSTRATES:
  - Superior colliculus (SC): multisensory integration hub
  - Parietal cortex: crossmodal binding
  - Superior temporal sulcus (STS): audiovisual integration

For ARCHITECTURE:
- Visual-thermal crossmodal effects (warm colors → feel warmer)
- Visual-auditory coherence (matching soundscape to visual space)
- Material perception across senses (visual texture + haptic texture)
- Crossmodal congruence → environmental comfort/coherence
- Crossmodal incongruence → discomfort, uncanny effects

This is DIFFERENT from:
- PP (which concerns prediction within modalities; MSI concerns across modalities)
- IC (which concerns body-to-brain; MSI concerns sense-to-sense binding)
- EC (which concerns body-environment action; MSI concerns perceptual binding)
"""

EXPLAINS = [
    "Visual-thermal crossmodal effects (warm colors feel warmer)",
    "Visual-auditory environmental coherence (matching sound to space)",
    "Material quality perception across senses (visual + tactile + acoustic)",
    "Why congruent multisensory environments feel more comfortable",
    "Why incongruent senses create uncanny or unpleasant experiences",
    "Ambient scent effects on space perception",
    "How acoustic properties affect perceived room size",
    "Crossmodal compensation (when one sense is degraded)",
]

DOES_NOT_EXPLAIN = [
    "Within-modality visual pattern effects (→ PP)",
    "Spatial navigation / cognitive maps (→ SN)",
    "Implicit vs. explicit processing (→ DP)",
    "Specific neurochemistry (→ NM)",
    "Circadian light effects (→ CB)",
    "Memory for environments (→ MS)",
    "Why living things are preferred (→ Biophilia)",
]

STIMULUS_INCLUDES = [
    "Visual-thermal crossmodal manipulations (color temperature + actual temperature)",
    "Visual-auditory congruence manipulations (soundscape + visual space)",
    "Material perception across modalities (see + touch + hear)",
    "Ambient scent combined with visual/thermal conditions",
    "Acoustic properties affecting perceived space (reverberation + visual size)",
    "Crossmodal conflict paradigms (incongruent stimuli across senses)",
    "Multi-channel environmental interventions (light + sound + scent)",
]

STIMULUS_EXCLUDES = [
    "Single-modality visual studies (→ PP)",
    "Pure auditory studies (noise levels only, → NM for stress)",
    "Pure thermal studies (→ IC for interoception)",
    "Light spectrum without crossmodal component (→ CB)",
]

STIMULUS_EDGE_CASES = [
    {
        "item": "Wood material assessment (visual + tactile)",
        "judgment": "INCLUDED if testing crossmodal (visual vs. tactile) perception",
        "depends_on": "Whether the study manipulates cross-modal matching or tests single modality",
    },
    {
        "item": "Background music in architectural spaces",
        "judgment": "INCLUDED if testing visual-auditory congruence; EXCLUDED if just 'music = pleasant'",
        "depends_on": "Whether musical properties are matched/mismatched with visual architectural features",
    },
    {
        "item": "Daylight quality (visual + thermal)",
        "judgment": "INCLUDED if testing crossmodal effects; may also be CB for circadian",
        "depends_on": "Whether the study separates visual and thermal contributions of daylight",
    },
]

PREDICTED_OUTCOMES = [
    "crossmodal congruence rating / environmental coherence",
    "thermal perception (when visually modulated — Hue-Heat hypothesis)",
    "room size perception (when acoustically modulated)",
    "material quality perception (when multimodally assessed)",
    "environmental comfort (from multisensory congruence)",
    "crossmodal enhancement or suppression",
]

NOT_PREDICTED_OUTCOMES = [
    "visual preference without crossmodal component (→ PP)",
    "wayfinding (→ SN)",
    "stress physiology (→ NM)",
    "circadian / sleep (→ CB)",
    "memory (→ MS)",
    "directed attention (→ DT)",
]

MATCHING_PROMPT = """
You are evaluating whether an extracted claim falls under the scope of
MULTISENSORY INTEGRATION (MSI).

This framework explains how the brain integrates signals across sensory
modalities and how crossmodal congruence/conflict affects environmental
experience.

INCLUDE if:
- Study manipulates stimuli across TWO OR MORE modalities (visual + auditory,
  visual + thermal, etc.)
- Outcome involves crossmodal effects (one sense modulating another)
- Study tests environmental coherence/congruence across senses
- Mechanism involves sensory binding or cue integration

EXCLUDE if:
- Study uses only one modality (visual → PP, auditory → NM/DT)
- Study tests circadian light effects (→ CB)
- Study tests general stress (→ NM)

Given this claim:
{claim}

From paper: {paper_id}
Stimulus variables: {lhs_vars}
Outcome variable: {rhs_var}
Direction: {polarity}

Does this fall under Multisensory Integration scope?
Respond with CONFIRMS, DISCONFIRMS, CHALLENGES, ORTHOGONAL, EDGE_CASE, or NEEDS_INFO.
Explain your reasoning in 2-3 sentences.
"""

FEW_SHOT_EXAMPLES = [
    {
        "claim": "Warm-colored lighting makes occupants feel the room is warmer than it actually is",
        "lhs": ["env.warm_color_light"],
        "rhs": "percept.thermal_comfort",
        "polarity": "positive",
        "judgment": "CONFIRMS",
        "reasoning": "Visual color temperature modulating thermal perception is a classic crossmodal effect (Hue-Heat hypothesis). The visual signal influences the thermal percept — core MSI.",
    },
    {
        "claim": "Matching natural soundscapes to nature views increases relaxation more than mismatched conditions",
        "lhs": ["env.nature_view + env.nature_sound_congruence"],
        "rhs": "aff.relaxation",
        "polarity": "positive",
        "judgment": "CONFIRMS",
        "reasoning": "Visual-auditory congruence enhances the environmental percept. Congruent multisensory stimuli produce superadditive effects per MSI principles.",
    },
    {
        "claim": "Fractal facade patterns increase visual preference",
        "lhs": ["env.fractal_pattern"],
        "rhs": "aff.preference",
        "polarity": "positive",
        "judgment": "ORTHOGONAL",
        "reasoning": "Single-modality visual effect. No crossmodal component. Falls under PP.",
    },
    {
        "claim": "Blue-enriched light improves morning alertness",
        "lhs": ["env.blue_light"],
        "rhs": "cog.alertness",
        "polarity": "positive",
        "judgment": "ORTHOGONAL",
        "reasoning": "This is a circadian (non-visual photoreception) effect, not a crossmodal perceptual integration effect. Falls under CB.",
    },
]
