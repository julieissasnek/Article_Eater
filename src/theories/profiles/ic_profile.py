"""
Interoception and Constructed Affect — Theory Profile for LLM Matching.

TIER 1.6: Affective experience is constructed by integrating interoceptive
signals (from the body), exteroceptive signals (from the environment), and
prior beliefs. Individual differences in interoceptive sensitivity modulate
environmental affect effects.
"""

THEORY_ID = "framework:interoception"
THEORY_NAME = "Interoception and Constructed Affect"

CORE_MECHANISM = """
Affective experience is CONSTRUCTED through integration of:
  - INTEROCEPTIVE signals: Heart rate, respiration, gut, temperature, pain —
    the body's internal state as detected by the insular cortex
  - EXTEROCEPTIVE signals: What the senses detect in the environment
  - PRIOR BELIEFS: Semantic knowledge, expectations, cultural context

KEY PRINCIPLE: Interoceptive PREDICTION ERROR — mismatch between predicted
and actual body state — is a primary driver of affect. Architecture modulates
body state; the brain constructs affect by integrating these changes with
predictions.

CRITICAL INDIVIDUAL DIFFERENCE: People vary in interoceptive sensitivity
(accuracy at detecting heartbeat, etc.). High interoceptive sensitivity
→ stronger environmental affect effects.

For ARCHITECTURE:
- Cold draft → interoceptive PE → discomfort (if unexpected)
- Stuffy room → CO2 → interoceptive PE → restlessness
- Open atrium → postural/breathing change → interoceptive signal → awe

This is DIFFERENT from:
- NM (which names specific neurochemicals; IC explains how body signals
  become feelings)
- PP (which concerns exteroceptive prediction; IC concerns interoceptive)
- DP (which concerns processing mode; IC concerns what signals are processed)
"""

EXPLAINS = [
    "Individual differences in environmental sensitivity (interoceptive accuracy)",
    "Why same environment affects people differently (different priors + sensitivity)",
    "How architecture modulates bodily state → constructed affect",
    "Cultural variation in environmental response (different conceptual priors)",
    "Alexithymia and reduced environmental affect sensitivity",
    "Why thermal, air quality, and acoustic environments affect mood",
    "Social monitoring costs in open-plan environments (interoceptive arousal)",
]

DOES_NOT_EXPLAIN = [
    "Specific visual pattern effects (→ PP)",
    "Spatial navigation (→ SN)",
    "Why living things are preferred (→ Biophilia)",
    "Specific neurochemical pathways (→ NM)",
    "Circadian timing (→ CB)",
    "Crossmodal perceptual interactions (→ MSI)",
    "Memory for environments (→ MS)",
]

STIMULUS_INCLUDES = [
    "Thermal environment manipulations (temperature, drafts)",
    "Air quality (CO2, pollutants, ventilation)",
    "Social density and crowding (interoceptive arousal from monitoring)",
    "Privacy and territory manipulations (body boundary regulation)",
    "Acoustic environments affecting physiological state",
    "Studies measuring interoceptive sensitivity as moderator",
    "Studies measuring individual differences in environmental response",
]

STIMULUS_EXCLUDES = [
    "Visual pattern manipulations without body-state component (→ PP)",
    "Spatial layout without social/monitoring component (→ SN)",
    "Light spectrum without body-state framing (→ CB)",
    "Material texture without haptic/thermal component (→ PP)",
]

STIMULUS_EDGE_CASES = [
    {
        "item": "Ceiling height effects on body posture",
        "judgment": "INCLUDED if measuring somatic/interoceptive response; EXCLUDED if measuring abstract thinking (→ EC/PP)",
        "depends_on": "Whether the mechanism involves body state change or cognitive framing",
    },
    {
        "item": "Awe-inspiring spaces (cathedrals, dramatic views)",
        "judgment": "INCLUDED if measuring physiological response (chills, breathing change)",
        "depends_on": "Whether the study measures interoceptive/somatic aspects of awe or just self-report",
    },
]

PREDICTED_OUTCOMES = [
    "affective valence (constructed emotion)",
    "individual differences in environmental sensitivity",
    "interoceptive accuracy × environmental effect interactions",
    "physiological arousal (HR, RR, EDA) as mediator of affect",
    "thermal comfort / discomfort",
    "air quality comfort",
    "social comfort / discomfort in shared spaces",
]

NOT_PREDICTED_OUTCOMES = [
    "processing fluency (→ PP)",
    "wayfinding (→ SN)",
    "directed attention (→ DT)",
    "specific cortisol levels (→ NM)",
    "circadian phase (→ CB)",
    "visual aesthetics (→ PP)",
]

MATCHING_PROMPT = """
You are evaluating whether an extracted claim falls under the scope of
INTEROCEPTION AND CONSTRUCTED AFFECT.

This framework claims affective experience is constructed by integrating
body signals with environmental input and prior beliefs. Individual differences
in interoceptive sensitivity modulate environmental effects.

INCLUDE if:
- Study measures body-state changes from environmental features
- Study tests individual differences in environmental sensitivity
- Study measures thermal, air quality, or social comfort
- Mechanism involves interoceptive prediction error or body-to-brain signaling

EXCLUDE if:
- Study tests visual patterns (→ PP)
- Study tests spatial navigation (→ SN)
- Study tests specific neurochemicals (→ NM)
- Study tests circadian timing (→ CB)

Given this claim:
{claim}

From paper: {paper_id}
Stimulus variables: {lhs_vars}
Outcome variable: {rhs_var}
Direction: {polarity}

Does this fall under Interoception scope?
Respond with CONFIRMS, DISCONFIRMS, CHALLENGES, ORTHOGONAL, EDGE_CASE, or NEEDS_INFO.
Explain your reasoning in 2-3 sentences.
"""

FEW_SHOT_EXAMPLES = [
    {
        "claim": "People with high interoceptive accuracy show stronger emotional responses to architectural spaces",
        "lhs": ["person.interoceptive_accuracy", "env.architectural_space"],
        "rhs": "aff.emotional_response",
        "polarity": "positive",
        "judgment": "CONFIRMS",
        "reasoning": "This directly tests the IC prediction that interoceptive sensitivity moderates environmental affect. People who detect body signals more accurately construct stronger affective responses.",
    },
    {
        "claim": "Poor air quality reduces workplace satisfaction",
        "lhs": ["env.air_quality"],
        "rhs": "aff.satisfaction",
        "polarity": "negative",
        "judgment": "CONFIRMS",
        "reasoning": "CO2, pollutants change body state (breathing difficulty, headache) → interoceptive PE → negative constructed affect. The body detects the air quality problem before conscious awareness.",
    },
    {
        "claim": "Fractal patterns improve visual preference",
        "lhs": ["env.fractal_pattern"],
        "rhs": "aff.preference",
        "polarity": "positive",
        "judgment": "ORTHOGONAL",
        "reasoning": "This is a visual pattern → preference effect without body-state mediation. Falls under PP (fractal structure and visual prediction).",
    },
]
