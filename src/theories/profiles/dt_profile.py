"""
Default Mode Network / Task-Positive Network Dynamics — Theory Profile.

TIER 1.4: DMN and TPN are anti-correlated. Sustained TPN engagement suppresses
DMN → directed attention fatigue. DMN recovery requires safe, low-demand
environments. This is the neural mechanism behind ART.
"""

THEORY_ID = "framework:dmn_tpn"
THEORY_NAME = "Default Mode Network / Task-Positive Network Dynamics"

CORE_MECHANISM = """
The brain has two ANTI-CORRELATED networks:
  - DEFAULT MODE NETWORK (DMN): Midline + lateral parietal. Active during
    rest, mind-wandering, self-reflection, future planning, creativity.
  - TASK-POSITIVE NETWORK (TPN): Frontal-parietal. Active during focused
    attention, executive function, external task demands.

KEY PRINCIPLE: Sustained TPN engagement SUPPRESSES DMN. Chronic DMN suppression
→ cortisol increase, immune impairment, cognitive fatigue.

For ARCHITECTURE this means:
- Environments demanding sustained attention (complex navigation, threat
  monitoring, open-plan noise) → TPN dominance → DMN suppression → fatigue
- Restful, safe, familiar environments → DMN engagement → restoration
- "Directed attention fatigue" (Kaplan) = chronic DMN suppression
- "Soft fascination" = gentle DMN engagement without full TPN suppression

This MECHANISTICALLY EXPLAINS what ART describes phenomenologically.

This is DIFFERENT from:
- ART (which describes phenomena; DT explains the neural mechanism)
- PP (which concerns prediction error; DT concerns network balance)
- NM (which concerns specific neurochemicals; DT concerns network dynamics)
"""

EXPLAINS = [
    "Directed attention fatigue in demanding environments",
    "Cognitive restoration in restorative environments (soft fascination)",
    "Why nature is restorative (allows DMN engagement without TPN demands)",
    "Open-plan office fatigue (sustained monitoring = TPN overload)",
    "Creativity benefits of restorative environments (DMN supports divergent thinking)",
    "Mind-wandering patterns in different building types",
    "Why constant interruption is cognitively costly (TPN re-engagement cost)",
]

DOES_NOT_EXPLAIN = [
    "Why nature specifically is preferred (→ Biophilia)",
    "What specific patterns generate prediction error (→ PP)",
    "How spatial layout affects navigation (→ SN)",
    "Specific neurochemical mechanisms (→ NM)",
    "Circadian effects of light (→ CB)",
    "Crossmodal interactions (→ MSI)",
    "Cultural variation in responses (→ MS)",
]

STIMULUS_INCLUDES = [
    "Environments varying in attentional demand (low vs. high)",
    "Nature vs. urban settings (for restoration comparison)",
    "Open-plan vs. enclosed offices (ambient distraction)",
    "Noise levels that affect sustained attention",
    "Complex vs. simple wayfinding requirements",
    "Environments with/without 'soft fascination' qualities",
    "Rest periods in different architectural settings",
]

STIMULUS_EXCLUDES = [
    "Light spectrum/color without attentional component (→ CB)",
    "Social density without attentional demand focus (→ IC/NM)",
    "Material properties without attentional framing (→ PP)",
    "Thermal conditions (→ MSI/NM)",
]

STIMULUS_EDGE_CASES = [
    {
        "item": "Nature views from office windows",
        "judgment": "INCLUDED if measuring attention restoration / DMN recovery",
        "depends_on": "Whether outcome is restoration/fatigue or general preference (→ PP/Biophilia)",
    },
    {
        "item": "Background music in workspaces",
        "judgment": "INCLUDED if testing attentional demand / cognitive performance",
        "depends_on": "Whether music is framed as attentional factor or crossmodal",
    },
]

PREDICTED_OUTCOMES = [
    "directed attention performance (sustained attention tests)",
    "cognitive fatigue / mental exhaustion",
    "cognitive restoration (attention restoration after break)",
    "creativity / divergent thinking",
    "mind-wandering frequency",
    "fMRI DMN/TPN activation patterns",
]

NOT_PREDICTED_OUTCOMES = [
    "aesthetic preference (→ PP)",
    "wayfinding performance specifically (→ SN)",
    "specific stress hormones (→ NM)",
    "circadian/sleep effects (→ CB)",
    "affective valence specifically (→ IC)",
    "social behavior (→ NM/IC)",
]

MATCHING_PROMPT = """
You are evaluating whether an extracted claim falls under the scope of
DEFAULT MODE NETWORK / TASK-POSITIVE NETWORK DYNAMICS.

This framework explains cognitive restoration and fatigue through the balance
between DMN (rest/creativity) and TPN (focused attention). Chronic TPN
engagement causes directed attention fatigue.

INCLUDE if:
- Study measures attention restoration or cognitive fatigue
- Study compares demanding vs. restorative environments
- Outcome involves sustained attention, creativity, or mind-wandering
- Mechanism invokes DMN/TPN balance or ART restoration

EXCLUDE if:
- Study measures preference without cognitive performance (→ PP)
- Study tests specific neurochemicals (→ NM)
- Study tests circadian effects (→ CB)

Given this claim:
{claim}

From paper: {paper_id}
Stimulus variables: {lhs_vars}
Outcome variable: {rhs_var}
Direction: {polarity}

Does this fall under DMN/TPN Dynamics scope?
Respond with CONFIRMS, DISCONFIRMS, CHALLENGES, ORTHOGONAL, EDGE_CASE, or NEEDS_INFO.
Explain your reasoning in 2-3 sentences.
"""

FEW_SHOT_EXAMPLES = [
    {
        "claim": "Nature walks improve sustained attention performance compared to urban walks",
        "lhs": ["env.nature_walk_vs_urban"],
        "rhs": "cog.sustained_attention",
        "polarity": "positive",
        "judgment": "CONFIRMS",
        "reasoning": "Nature environments allow DMN engagement (soft fascination) while urban demands TPN (monitoring traffic, noise). The attention restoration is a DT prediction.",
    },
    {
        "claim": "Open-plan offices reduce creative ideation compared to enclosed offices",
        "lhs": ["env.open_plan_vs_enclosed"],
        "rhs": "cog.creative_ideation",
        "polarity": "negative",
        "judgment": "CONFIRMS",
        "reasoning": "Creativity requires DMN engagement. Open-plan offices force sustained TPN engagement (monitoring interruptions), suppressing DMN and reducing creative output.",
    },
    {
        "claim": "Curved furniture increases aesthetic preference",
        "lhs": ["env.curved_furniture"],
        "rhs": "aff.preference",
        "polarity": "positive",
        "judgment": "ORTHOGONAL",
        "reasoning": "This is a visual preference effect, not an attentional/restoration effect. Falls under PP (contour curvature and prediction).",
    },
]
