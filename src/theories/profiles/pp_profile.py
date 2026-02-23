"""
Predictive Processing / Active Inference — Theory Profile for LLM Matching.

TIER 1.1: The brain minimizes prediction error through hierarchical generative
models. Perception is inference; affect tracks model confidence.
"""

THEORY_ID = "framework:predictive_processing"
THEORY_NAME = "Predictive Processing / Active Inference"

CORE_MECHANISM = """
The brain maintains a HIERARCHICAL GENERATIVE MODEL of its environment and
minimizes PREDICTION ERROR through:
  - Perception (updating the model to match input)
  - Action (changing the environment to match predictions)
  - Attention (precision-weighting which errors matter)

KEY PRINCIPLE: The brain predicts sensory input top-down; bottom-up signals
carry only the RESIDUAL ERROR (surprise). Chronic high prediction error is
metabolically costly and generates stress/negative affect.

For ARCHITECTURE this means:
- Familiar, learnable environments → low PE → comfort, fluency
- Novel but comprehensible → moderate PE → engagement, aesthetic pleasure
- Chaotic, illegible environments → chronic high PE → stress, avoidance
- The Goldilocks zone of complexity is where learning is possible

This is DIFFERENT from:
- Biophilia (which concerns living things, not pattern learnability)
- SRT (which concerns specific landscapes, not prediction mechanisms)
- Fractal Fluency (which concerns a specific statistical property, not
  the general prediction framework)
"""

EXPLAINS = [
    "Preference for familiar environments (low prediction error → fluency)",
    "Inverted-U relationship between complexity and preference (Goldilocks zone)",
    "Aesthetic pleasure from moderate surprise/novelty",
    "Stress from chaotic, illegible environments (chronic high PE)",
    "Rapid scene gist processing (<100ms) via low-spatial-frequency predictions",
    "Contour curvature effects on approach/avoidance (sharp angles = threat PE)",
    "Visual rhythm and fractal scaling effects (predictable hierarchical structure)",
    "Why spatial legibility matters (supports generative model updating)",
]

DOES_NOT_EXPLAIN = [
    "Why living things specifically are preferred (→ Biophilia)",
    "Why specific landscapes (savanna) are preferred (→ SRT/Biophilia)",
    "How navigation failure leads to stress (→ Spatial Navigation)",
    "Circadian effects of light (→ Chronobiological Regulation)",
    "Crossmodal interactions specifically (→ Multisensory Integration)",
    "Cultural variation in preferences (→ Memory Systems — different priors)",
    "Embodied/motor contributions to experience (→ Embodied Cognition)",
]

STIMULUS_INCLUDES = [
    "Visual complexity manipulations (simple → complex)",
    "Spatial legibility / wayfinding clarity",
    "Contour curvature (curved vs. angular/sharp)",
    "Fractal dimension manipulations",
    "Scene coherence / visual noise",
    "Lighting uniformity vs. contrast (luminance PE)",
    "Architectural rhythm and repetition patterns",
    "Ceiling height (spatial proportion PE)",
    "Material texture predictability",
    "Novel vs. familiar building exposure",
]

STIMULUS_EXCLUDES = [
    "Living things, plants, animals without pattern manipulation (→ Biophilia)",
    "Specific landscape types without complexity component (→ SRT)",
    "Light spectrum / color temperature without PE framing (→ CB)",
    "Sound / noise levels without crossmodal component (→ MSI)",
    "Social density / crowding without predictability framing (→ IC/NM)",
]

STIMULUS_EDGE_CASES = [
    {
        "item": "Nature views",
        "judgment": "PARTIALLY INCLUDED — nature provides learnable statistical structure (1/f spectra)",
        "depends_on": "Whether the study manipulates/measures prediction error or just 'nature vs. urban'",
    },
    {
        "item": "Music / soundscapes in buildings",
        "judgment": "INCLUDED if framed as auditory prediction; EXCLUDED if just pleasantness ratings",
        "depends_on": "Whether the study measures prediction dynamics or static preference",
    },
    {
        "item": "Wayfinding difficulty",
        "judgment": "INCLUDED if framed as spatial prediction error; also relevant to SN",
        "depends_on": "Whether the mechanism invoked is PE or hippocampal mapping",
    },
]

PREDICTED_OUTCOMES = [
    "aesthetic preference / liking / beauty ratings",
    "processing fluency (reaction time, identification speed)",
    "engagement / interest / curiosity",
    "stress / anxiety (from chronic high PE)",
    "approach / avoidance behavior",
    "comfort / discomfort",
    "skin conductance / physiological arousal",
]

NOT_PREDICTED_OUTCOMES = [
    "directed attention restoration specifically (→ ART/DT)",
    "cortisol specifically (→ NM)",
    "circadian phase / melatonin (→ CB)",
    "wayfinding performance specifically (→ SN)",
    "social behavior / prosociality (→ IC/NM)",
    "memory encoding specifically (→ MS)",
    "thermal comfort specifically (→ MSI)",
]

MATCHING_PROMPT = """
You are evaluating whether an extracted claim falls under the scope of
PREDICTIVE PROCESSING / ACTIVE INFERENCE.

This framework claims the brain minimizes prediction error through hierarchical
generative models. Architecture affects us by generating prediction errors
(surprise) or enabling fluent predictions (comfort).

INCLUDE if:
- Stimulus involves pattern complexity, coherence, or predictability
- Stimulus involves contour/form properties that trigger threat or fluency
- Outcome involves preference, fluency, engagement, or PE-related stress
- Mechanism invokes prediction, expectation, or surprise

EXCLUDE if:
- Stimulus is living things specifically without PE framing (→ Biophilia)
- Outcome is circadian / sleep effects (→ CB)
- Outcome is directed attention performance (→ ART/DT)
- Mechanism is navigation / cognitive mapping (→ SN)
- Mechanism is crossmodal interaction (→ MSI)

Given this claim:
{claim}

From paper: {paper_id}
Stimulus variables: {lhs_vars}
Outcome variable: {rhs_var}
Direction: {polarity}

Does this fall under Predictive Processing scope?
Respond with CONFIRMS, DISCONFIRMS, CHALLENGES, ORTHOGONAL, EDGE_CASE, or NEEDS_INFO.
Explain your reasoning in 2-3 sentences.
"""

FEW_SHOT_EXAMPLES = [
    {
        "claim": "Higher visual complexity positively affects preference up to a moderate level, then decreases",
        "lhs": ["env.visual_complexity"],
        "rhs": "aff.preference",
        "polarity": "inverted_u",
        "judgment": "CONFIRMS",
        "reasoning": "The inverted-U complexity–preference curve is a core PP prediction: moderate PE is engaging (Goldilocks zone), while too much PE is aversive.",
    },
    {
        "claim": "Curved contours positively affect approach behavior compared to sharp angles",
        "lhs": ["env.contour_curvature"],
        "rhs": "beh.approach",
        "polarity": "positive",
        "judgment": "CONFIRMS",
        "reasoning": "Sharp angles generate threat-related PE (angular contours signal potential harm); curved contours are predicted/safe. This is PP operating on low-level visual features.",
    },
    {
        "claim": "Indoor plants improve office worker wellbeing",
        "lhs": ["env.indoor_plants"],
        "rhs": "aff.wellbeing",
        "polarity": "positive",
        "judgment": "ORTHOGONAL",
        "reasoning": "While plants could reduce PE via natural statistical regularities, the study tests living things → wellbeing, which is more directly Biophilia. A PP framing would need to manipulate/measure prediction error.",
    },
    {
        "claim": "Blue-enriched morning light improves alertness",
        "lhs": ["env.morning_light_blue"],
        "rhs": "cog.alertness",
        "polarity": "positive",
        "judgment": "ORTHOGONAL",
        "reasoning": "This is a circadian effect (light → SCN → alertness), not a prediction error mechanism. Falls under Chronobiological Regulation.",
    },
    {
        "claim": "Fractal patterns in building facades affect visual preference",
        "lhs": ["env.fractal_pattern"],
        "rhs": "aff.preference",
        "polarity": "positive",
        "judgment": "CONFIRMS",
        "reasoning": "Fractal patterns have predictable self-similar structure (1/f spectra) that the visual system can efficiently predict. PP explains why — the hierarchical structure matches the brain's generative model at multiple scales.",
    },
]
