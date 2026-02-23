"""
Embodied Cognition — Theory Profile for LLM Matching.

TIER 1.8: Cognition is shaped by the body's morphology, sensorimotor
capacities, and environmental interaction. Includes Gibson's affordances.
Architecture is experienced through the body — movement, posture, haptics.
"""

THEORY_ID = "framework:embodied_cognition"
THEORY_NAME = "Embodied Cognition and Sensorimotor Contingencies"

CORE_MECHANISM = """
Cognition is CONSTITUTIVELY SHAPED by:
  - BODY MORPHOLOGY: Size, reach, mobility affect what is perceivable/actionable
  - SENSORIMOTOR CAPACITIES: What I can see/hear/touch depends on what I can do
  - ENVIRONMENTAL INTERACTION: Active exploration, not passive viewing

KEY CONCEPT — AFFORDANCES (Gibson, 1979):
Architectural features are perceived as ACTION POSSIBILITIES relative to the
body. A stairway affords climbing; a wide corridor affords walking side-by-side;
a low bench affords sitting.

For ARCHITECTURE:
- Experience is THROUGH THE BODY — movement, posture, gait
- Ceiling height affects body posture → affects cognition (expansive/contracted)
- Stair climbing affects physiological state → modulates affect
- Tactile engagement with materials is primary, not incidental
- Proxemics (interpersonal distance) depends on spatial affordances

This is DIFFERENT from:
- PP (which concerns neural prediction models, not bodily action)
- SN (which concerns hippocampal spatial maps, not bodily engagement)
- IC (which concerns interoceptive signals, not motor/action coupling)
"""

EXPLAINS = [
    "How ceiling height affects cognitive style via posture (expansive vs. contracted)",
    "Why movement through architecture matters (not just seeing it)",
    "Tactile/haptic engagement with materials",
    "How stair climbing modulates physiological state and cognition",
    "Proxemic behavior (interpersonal distance) in architectural settings",
    "Affordance perception — what buildings invite us to do",
    "Why VR without motor engagement may miss embodied effects",
    "How accessibility issues change environmental experience",
]

DOES_NOT_EXPLAIN = [
    "Why specific visual patterns are preferred (→ PP)",
    "How spatial layout affects cognitive mapping (→ SN)",
    "Specific neurochemical effects of stress (→ NM)",
    "Circadian effects of light (→ CB)",
    "Crossmodal perceptual binding (→ MSI)",
    "Memory for places (→ MS)",
    "Why living things are preferred (→ Biophilia)",
]

STIMULUS_INCLUDES = [
    "Ceiling height manipulations (with body posture measurement)",
    "Walking / movement through space (promenade, sequence)",
    "Stair vs. elevator comparisons",
    "Material touch/haptic properties",
    "Furniture ergonomics and body engagement",
    "Accessibility features and barriers",
    "Proxemic manipulations (interpersonal distance and space layout)",
    "Posture manipulations in architectural settings",
    "Active exploration vs. passive viewing of environments",
]

STIMULUS_EXCLUDES = [
    "Pure visual viewing (photos, screens) without body engagement (→ PP)",
    "Spatial layout without movement component (→ SN)",
    "Light spectrum (→ CB)",
    "Sound/noise without bodily response (→ MSI)",
]

STIMULUS_EDGE_CASES = [
    {
        "item": "VR environments with locomotion",
        "judgment": "INCLUDED if testing embodied experience; EXCLUDED if just visual",
        "depends_on": "Whether locomotion/body tracking is part of the study",
    },
    {
        "item": "Seated viewing of architectural images",
        "judgment": "EXCLUDED — no bodily engagement with the architecture",
        "depends_on": None,
    },
    {
        "item": "Architectural promenade (sequential spatial experience)",
        "judgment": "INCLUDED — bodily movement through space is the essence",
        "depends_on": None,
    },
]

PREDICTED_OUTCOMES = [
    "postural changes (body openness/closure)",
    "gait patterns (speed, stride, smoothness)",
    "reach/grasp behavior",
    "affordance ratings (what the space invites)",
    "motor cortex activation",
    "proprioceptive/kinesthetic experience",
    "cognitive style changes mediated by posture (abstract vs. concrete)",
]

NOT_PREDICTED_OUTCOMES = [
    "visual preference without body engagement (→ PP)",
    "cognitive map quality (→ SN)",
    "cortisol / stress hormones (→ NM)",
    "circadian phase (→ CB)",
    "memory formation (→ MS)",
    "crossmodal perception (→ MSI)",
]

MATCHING_PROMPT = """
You are evaluating whether an extracted claim falls under the scope of
EMBODIED COGNITION AND SENSORIMOTOR CONTINGENCIES.

This framework claims cognition is shaped by bodily morphology, movement,
and active environmental interaction. Architecture is experienced THROUGH
the body.

INCLUDE if:
- Study involves movement/locomotion through architecture
- Study measures postural responses (ceiling height, space openness)
- Study tests affordance perception or action possibilities
- Study uses haptic/tactile engagement with materials
- Mechanism involves body-environment coupling

EXCLUDE if:
- Study uses only visual viewing of images (→ PP)
- Study tests spatial navigation without body focus (→ SN)
- Study tests physiological stress (→ NM)

Given this claim:
{claim}

From paper: {paper_id}
Stimulus variables: {lhs_vars}
Outcome variable: {rhs_var}
Direction: {polarity}

Does this fall under Embodied Cognition scope?
Respond with CONFIRMS, DISCONFIRMS, CHALLENGES, ORTHOGONAL, EDGE_CASE, or NEEDS_INFO.
Explain your reasoning in 2-3 sentences.
"""

FEW_SHOT_EXAMPLES = [
    {
        "claim": "High ceilings increase abstract thinking via expansive posture",
        "lhs": ["env.ceiling_height"],
        "rhs": "cog.abstract_thinking",
        "polarity": "positive",
        "judgment": "CONFIRMS",
        "reasoning": "Ceiling height → body posture change (expansive) → cognitive style shift. This is embodied cognition: body mediates the environmental effect on cognition.",
    },
    {
        "claim": "Walking through a building sequence produces different affective responses than viewing photos of the same spaces",
        "lhs": ["env.promenade_vs_photos"],
        "rhs": "aff.affective_response",
        "polarity": "positive",
        "judgment": "CONFIRMS",
        "reasoning": "This tests the EC claim that bodily engagement (locomotion) is constitutive of architectural experience, not just a delivery mechanism for visual input.",
    },
    {
        "claim": "Blue-enriched morning light improves alertness",
        "lhs": ["env.morning_light_blue"],
        "rhs": "cog.alertness",
        "polarity": "positive",
        "judgment": "ORTHOGONAL",
        "reasoning": "Light spectrum → circadian effect. No bodily/motor component. Falls under CB.",
    },
]
