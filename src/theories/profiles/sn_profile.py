"""
Spatial Navigation and Cognitive Mapping — Theory Profile for LLM Matching.

TIER 1.2: Hippocampal-entorhinal system constructs cognitive maps using
place cells, grid cells, head direction cells. Architecture's legibility
directly affects map quality, navigation stress, and spatial cognition.
"""

THEORY_ID = "framework:spatial_navigation"
THEORY_NAME = "Spatial Navigation and Cognitive Mapping"

CORE_MECHANISM = """
The HIPPOCAMPAL-ENTORHINAL system constructs an ALLOCENTRIC COGNITIVE MAP
using specialized cell types:
  - Place cells (hippocampus) — fire at specific locations
  - Grid cells (entorhinal cortex) — fire in hexagonal grid pattern
  - Head direction cells — encode orientation
  - Border cells — encode environmental boundaries

Architecture's LEGIBILITY, COMPLEXITY, and SPATIAL STRUCTURE directly affect
cognitive map quality and stability. Poor legibility → unstable maps →
navigation failure → measurable stress increases (cortisol, hippocampal theta).

KEY FEATURE: This concerns SPATIAL LAYOUT and WAYFINDING, not general
visual properties. The theory explains:
- Why some buildings are easy/hard to navigate
- Why wayfinding failure is stressful (hippocampal error signals)
- How landmarks at decision points stabilize cognitive maps
- Why spatial hierarchy (building > floor > corridor > room) aids navigation

This is DIFFERENT from:
- Predictive Processing (which concerns general prediction, not spatial maps)
- Embodied Cognition (which concerns body interaction, not spatial representation)
"""

EXPLAINS = [
    "Why some buildings are easy vs. hard to navigate",
    "Wayfinding failure and associated stress",
    "Landmark effectiveness at decision points",
    "Effects of spatial hierarchy and legibility on navigation",
    "Space syntax effects (integration, connectivity)",
    "How spatial configuration shapes movement patterns",
    "Navigation anxiety in complex buildings (hospitals, airports)",
    "How spatial layout affects social encounter patterns",
]

DOES_NOT_EXPLAIN = [
    "Visual aesthetics or beauty judgments (→ PP)",
    "Biophilic responses to nature in buildings (→ Biophilia)",
    "How lighting affects mood/circadian rhythms (→ CB/NM)",
    "Crossmodal environmental effects (→ MSI)",
    "Why specific architectural styles are preferred (→ PP/MS)",
    "Embodied/motor aspects of spatial experience (→ EC)",
]

STIMULUS_INCLUDES = [
    "Floor plan complexity and layout",
    "Spatial integration values (Space Syntax metrics)",
    "Landmark placement and visibility",
    "Corridor connectivity and depth",
    "Building legibility (signage, visual access)",
    "Decision point complexity (junctions, intersections)",
    "Isovist properties (visible area, occluding edges)",
    "Spatial hierarchy clarity (building > floor > zone > room)",
    "Path choice and route selection scenarios",
]

STIMULUS_EXCLUDES = [
    "Surface materials without spatial component (→ PP/Biophilia)",
    "Lighting color/spectrum (→ CB)",
    "Sound/noise levels (→ MSI)",
    "Furniture/decoration without spatial layout effects",
    "Window views without spatial orientation role (→ Biophilia/PP)",
]

STIMULUS_EDGE_CASES = [
    {
        "item": "Ceiling height",
        "judgment": "PARTIALLY INCLUDED — affects spatial perception but also PP and EC",
        "depends_on": "Whether the study measures spatial cognition/navigation or aesthetic preference",
    },
    {
        "item": "Windows and visual access",
        "judgment": "INCLUDED if about spatial orientation; EXCLUDED if about nature views",
        "depends_on": "Whether windows provide spatial reference frames or biophilic content",
    },
    {
        "item": "Open plan offices",
        "judgment": "INCLUDED for spatial encounter patterns; EXCLUDED for noise/privacy (→ IC/NM)",
        "depends_on": "Whether the dependent variable is spatial behavior or psychological wellbeing",
    },
]

PREDICTED_OUTCOMES = [
    "wayfinding performance (time, errors, routes)",
    "navigation stress / anxiety",
    "spatial orientation accuracy",
    "cognitive map quality (sketch maps, pointing tasks)",
    "movement patterns (pedestrian flow)",
    "social encounter frequency (via spatial configuration)",
]

NOT_PREDICTED_OUTCOMES = [
    "aesthetic preference (→ PP)",
    "general wellbeing (→ multiple theories)",
    "circadian/sleep effects (→ CB)",
    "affective valence without spatial component (→ IC/NM)",
    "cortisol specifically without wayfinding failure (→ NM)",
    "crossmodal perception (→ MSI)",
]

MATCHING_PROMPT = """
You are evaluating whether an extracted claim falls under the scope of
SPATIAL NAVIGATION AND COGNITIVE MAPPING.

This framework explains how the hippocampal-entorhinal system constructs
cognitive maps of space, and how architecture's legibility affects navigation,
stress, and spatial cognition.

INCLUDE if:
- Stimulus involves spatial layout, floor plan, or building configuration
- Stimulus involves landmarks, signage, or wayfinding cues
- Outcome involves navigation performance or spatial orientation
- Mechanism invokes cognitive mapping or spatial representation

EXCLUDE if:
- Stimulus is visual aesthetics without spatial layout (→ PP)
- Outcome is general mood/wellbeing without navigation component (→ IC/NM)
- Mechanism is circadian/light effects (→ CB)

Given this claim:
{claim}

From paper: {paper_id}
Stimulus variables: {lhs_vars}
Outcome variable: {rhs_var}
Direction: {polarity}

Does this fall under Spatial Navigation scope?
Respond with CONFIRMS, DISCONFIRMS, CHALLENGES, ORTHOGONAL, EDGE_CASE, or NEEDS_INFO.
Explain your reasoning in 2-3 sentences.
"""

FEW_SHOT_EXAMPLES = [
    {
        "claim": "Higher spatial integration values positively affect pedestrian movement rates",
        "lhs": ["env.spatial_integration"],
        "rhs": "beh.movement_rate",
        "polarity": "positive",
        "judgment": "CONFIRMS",
        "reasoning": "Spatial integration is a Space Syntax metric directly measuring how well-connected a space is. Higher integration → more coherent cognitive map → more natural movement.",
    },
    {
        "claim": "Landmarks at decision points improve wayfinding performance",
        "lhs": ["env.landmark_placement"],
        "rhs": "cog.wayfinding_performance",
        "polarity": "positive",
        "judgment": "CONFIRMS",
        "reasoning": "Landmarks anchor the cognitive map at choice points where spatial decisions are made. This directly tests hippocampal mapping predictions.",
    },
    {
        "claim": "Indoor plants improve office worker wellbeing",
        "lhs": ["env.indoor_plants"],
        "rhs": "aff.wellbeing",
        "polarity": "positive",
        "judgment": "ORTHOGONAL",
        "reasoning": "Indoor plants are not a spatial navigation manipulation. This tests Biophilia, not cognitive mapping.",
    },
    {
        "claim": "Complex hospital layouts increase patient anxiety",
        "lhs": ["env.layout_complexity"],
        "rhs": "aff.anxiety",
        "polarity": "positive",
        "judgment": "CONFIRMS",
        "reasoning": "Complex layouts impair cognitive map formation → wayfinding failure → navigation anxiety. This is a core SN prediction in healthcare design.",
    },
]
