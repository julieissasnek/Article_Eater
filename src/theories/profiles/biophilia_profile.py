"""
Biophilia Hypothesis — Theory Profile for LLM Matching.

This profile encodes the theory's perspective on what falls within its scope.
Used to determine whether an extracted claim constitutes evidence for/against
this theory's predictions.

Key epistemic question: Would a biophilia theorist recognize this as relevant?
"""

THEORY_ID = "theory:biophilia"
THEORY_NAME = "Biophilia Hypothesis"

# =============================================================================
# CORE MECHANISM
# =============================================================================

CORE_MECHANISM = """
The biophilia hypothesis proposes that humans have an INNATE, EVOLVED tendency
to affiliate with other LIVING systems and life-like processes. This affiliation
was adaptive because:
- Attention to living things (plants, animals) aided survival (food, danger)
- Preference for certain landscapes (with water, vegetation) indicated resources
- Connection to nature supported psychological wellbeing in ancestral environments

The KEY WORD is LIVING. The theory concerns affiliation with:
- Living organisms (plants, animals)
- Life-like processes (growth, organic patterns)
- Natural systems that support life (water, sunlight)

This is DIFFERENT from:
- Predictive Processing (which concerns familiar patterns, not aliveness)
- Stress Recovery Theory (which concerns specific savanna-like landscapes)
- Fractal Fluency (which concerns mathematical pattern statistics)
"""

# =============================================================================
# SCOPE: WHAT THIS THEORY CLAIMS TO EXPLAIN
# =============================================================================

EXPLAINS = [
    "Cross-cultural preference for natural over built environments",
    "Wellbeing benefits from contact with nature/living things",
    "Restorative effects of plants, gardens, natural views",
    "Positive responses to natural materials (wood, stone as natural substrate)",
    "Benefits of daylight (connection to natural rhythms)",
    "Therapeutic value of animals (pet therapy)",
    "Attraction to water features",
]

DOES_NOT_EXPLAIN = [
    "Why specific natural things are feared (snakes, spiders) — that's biophobia",
    "Specific perceptual mechanisms of how nature affects cognition",
    "Crossmodal effects (visual-thermal, visual-auditory)",
    "Why any pleasant environment reduces stress (too broad)",
    "Effects of fractal patterns specifically (that's fractal fluency)",
    "Attention restoration mechanisms specifically (that's ART)",
    "Rapid stress recovery via physiological pathways (that's SRT)",
]

# =============================================================================
# OPERATIONALIZATIONS: WHAT COUNTS AS TESTING THIS THEORY
# =============================================================================

STIMULUS_INCLUDES = [
    "Indoor plants, potted plants",
    "Nature views through windows",
    "Living walls, green facades, vertical gardens",
    "Water features (fountains, aquariums, streams)",
    "Natural materials in their organic form (wood grain, stone texture)",
    "Gardens, parks with vegetation",
    "Animals, fish tanks",
    "Daylight, skylights (connection to sun)",
    "Natural sounds (birdsong, water sounds)",
]

STIMULUS_EXCLUDES = [
    "Fractal patterns without biological reference",
    "Aged/weathered industrial materials (rusty steel, patinated copper without organic context)",
    "Abstract art with nature-like colors",
    "Photographs vs. real nature (contested — representation may not trigger evolved response)",
    "VR nature without multisensory cues (contested)",
    "Biomimetic forms that look organic but aren't living (edge case)",
]

STIMULUS_EDGE_CASES = [
    {
        "item": "Aged wood",
        "judgment": "LIKELY INCLUDED — wood was living, aging shows organic process",
        "depends_on": "Whether the wood retains organic character (grain, texture) vs. processed/painted",
    },
    {
        "item": "Moss on stone",
        "judgment": "INCLUDED — moss is alive",
        "depends_on": None,
    },
    {
        "item": "Rusty steel with patina",
        "judgment": "EXCLUDED — decay but not biological, no evolved affiliation",
        "depends_on": "Unless the rust supports moss/lichen growth",
    },
    {
        "item": "Wabi-sabi aesthetics",
        "judgment": "PARTIALLY INCLUDED — if the aging shows organic process (wood, clay)",
        "depends_on": "The specific materials. Wabi-sabi on ceramics may be PP, not biophilia",
    },
    {
        "item": "Nature photographs",
        "judgment": "CONTESTED — representation may partially trigger response",
        "depends_on": "Quality, size, immersiveness. May be weaker than real nature.",
    },
    {
        "item": "Biomimetic architecture (organic forms)",
        "judgment": "EDGE CASE — looks life-like but isn't alive",
        "depends_on": "Whether evolved response is to appearance or aliveness. Theoretically contested.",
    },
]

# =============================================================================
# OUTCOME CONSTRUCTS: WHAT EFFECTS THIS THEORY PREDICTS
# =============================================================================

PREDICTED_OUTCOMES = [
    "preference / liking / aesthetic judgment",
    "wellbeing (general, self-reported)",
    "connection to nature (feeling affiliated)",
    "restorative experiences",
    "positive affect / mood",
]

NOT_PREDICTED_OUTCOMES = [
    "directed attention performance specifically (that's ART)",
    "cortisol / HRV / physiological stress markers specifically (that's SRT)",
    "perceptual fluency / processing speed (that's PP)",
    "spatial cognition",
    "memory performance",
    "crossmodal perception",
]

# =============================================================================
# MATCHING PROMPT
# =============================================================================

MATCHING_PROMPT = """
You are evaluating whether an extracted claim from a research paper falls under
the scope of the Biophilia Hypothesis.

THE BIOPHILIA HYPOTHESIS claims that humans have an innate, evolved tendency
to affiliate with LIVING systems and life-like processes.

Key question: Does this claim test whether contact with living/natural things
produces the effects biophilia predicts (preference, wellbeing, affiliation)?

INCLUDE if:
- Stimulus involves living things (plants, animals, gardens)
- Stimulus involves natural materials in organic form (wood grain, stone)
- Stimulus involves nature views, daylight, water
- Outcome is preference, wellbeing, or connection to nature

EXCLUDE if:
- Stimulus is fractal patterns without biological reference (→ Fractal Fluency)
- Stimulus is any familiar/predictable environment (→ Predictive Processing)
- Stimulus is savanna-like landscape specifically (→ SRT)
- Outcome is directed attention specifically (→ ART)
- Outcome is physiological stress markers specifically (→ SRT)
- Stimulus is aged industrial materials without organic character

EDGE CASES requiring the paper's actual stimuli:
- Aged wood: Include if organic character preserved
- Biomimetic forms: Depends on theory interpretation
- Nature photographs: May be weaker form of evidence
- Wabi-sabi: Depends on materials (wood=yes, steel=no)

Given this claim:
{claim}

From paper: {paper_id}
Stimulus variables: {lhs_vars}
Outcome variable: {rhs_var}
Direction: {polarity}

Does this fall under Biophilia Hypothesis scope?
Respond with:
- CONFIRMS: If it's positive evidence for biophilia predictions
- DISCONFIRMS: If it's negative evidence against biophilia predictions
- CHALLENGES: If it's a methodological/theoretical critique
- ORTHOGONAL: If it's outside biophilia scope (belongs to different theory)
- EDGE_CASE: If judgment requires reading the paper
- NEEDS_INFO: If critical information is missing

Also explain your reasoning in 2-3 sentences.
"""

# =============================================================================
# FEW-SHOT EXAMPLES
# =============================================================================

# =============================================================================
# PROACTIVE SCOPE SPECULATION
# =============================================================================
# Working with the theory's core mechanism to reason about what it MIGHT subsume.
# These are hypothetical extensions that need empirical validation.

POTENTIAL_SCOPE_EXTENSIONS = [
    {
        "item": "Natural textures (wood grain, bark, stone veins)",
        "reasoning": "If biophilia is about affiliation with living systems, then visual/tactile patterns that signal organic origin might trigger the response even without the organism present.",
        "mechanism_link": "Texture as signature of organic process",
        "status": "plausible",
        "would_test": "Compare organic textures vs. synthetic mimics",
    },
    {
        "item": "Natural sounds (birdsong, running water, wind in trees)",
        "reasoning": "Evolved affiliation should extend to auditory cues of nature, not just visual. Birdsong signals safe environment.",
        "mechanism_link": "Auditory as cross-modal extension of biophilia",
        "status": "likely",
        "would_test": "Compare natural soundscapes vs. urban sounds vs. silence",
    },
    {
        "item": "Natural colors (greens, earth tones, sky blue)",
        "reasoning": "If we evolved to prefer natural environments, color palettes associated with nature might carry some of that response.",
        "mechanism_link": "Color as proxy for environment type",
        "status": "speculative",
        "would_test": "Compare natural-palette interiors vs. artificial colors",
    },
    {
        "item": "Aged organic materials (weathered wood, patinated copper with verdigris)",
        "reasoning": "Aging that reveals organic character (grain emerging, natural patina) may strengthen biophilic response by making the organic nature more salient.",
        "mechanism_link": "Aging as revelation of organic origin",
        "status": "plausible",
        "would_test": "Compare new wood vs. aged wood vs. aged steel",
    },
    {
        "item": "Circadian-aligned lighting (warm morning, bright midday, dim evening)",
        "reasoning": "If biophilia concerns connection to natural rhythms, then lighting that matches sun position might trigger evolved responses.",
        "mechanism_link": "Light as natural rhythm cue",
        "status": "likely (overlaps circadian theory)",
        "would_test": "Compare circadian lighting vs. constant artificial light",
    },
    {
        "item": "Biomorphic forms in architecture (curved, organic shapes)",
        "reasoning": "If response is to living/life-like, then architectural forms that mimic organic shapes might trigger partial response.",
        "mechanism_link": "Form as signal of organic origin",
        "status": "contested",
        "would_test": "Compare biomorphic vs. rectilinear buildings with matched other features",
    },
    {
        "item": "Seasonal variation in interior environment",
        "reasoning": "Natural environments change with seasons. If biophilia is about connection to nature, interiors that vary might be more biophilic than static ones.",
        "mechanism_link": "Change as natural environment signature",
        "status": "speculative",
        "would_test": "Compare seasonally-adaptive vs. constant interiors",
    },
]

# Questions to probe scope boundaries (for LLM reasoning)
SCOPE_PROBING_QUESTIONS = [
    "Does the organism need to be alive, or is evidence of past life sufficient?",
    "Does viewing suffice, or is interaction/touch needed for full effect?",
    "Are some senses primary (vision) and others secondary (smell, touch)?",
    "Does representation (photo, VR) work as well as presence?",
    "Is the response to nature specifically, or to 'not-human-made' more broadly?",
    "Do cultural associations with nature matter, or only innate responses?",
    "Is biophilia satisfied by any living thing, or are some (dangerous) excluded?",
]

FEW_SHOT_EXAMPLES = [
    {
        "claim": "Indoor plants positively affect office worker wellbeing",
        "lhs": ["env.indoor_plants"],
        "rhs": "aff.wellbeing",
        "polarity": "positive",
        "judgment": "CONFIRMS",
        "reasoning": "Indoor plants are living things. Wellbeing is a predicted outcome of biophilia. This directly tests a biophilia prediction.",
    },
    {
        "claim": "Fractal facade patterns positively affect aesthetic preference",
        "lhs": ["env.fractal_facade"],
        "rhs": "aff.preference",
        "polarity": "positive",
        "judgment": "ORTHOGONAL",
        "reasoning": "Fractal patterns are mathematical, not biological. This tests Fractal Fluency hypothesis, not Biophilia, even though the outcome (preference) overlaps.",
    },
    {
        "claim": "Nature views improve directed attention performance",
        "lhs": ["env.nature_view"],
        "rhs": "cog.directed_attention",
        "polarity": "positive",
        "judgment": "ORTHOGONAL",
        "reasoning": "While stimulus (nature view) is within biophilia scope, the specific outcome (directed attention) is the domain of Attention Restoration Theory. This tests ART, not biophilia.",
    },
    {
        "claim": "Aged materials positively affect emotional response",
        "lhs": ["env.aged_materials", "env.weathered_materials"],
        "rhs": "aff.emotional_response",
        "polarity": "positive",
        "judgment": "EDGE_CASE",
        "reasoning": "Depends on what materials. Aged wood with visible grain = biophilia. Rusty steel = not biophilia (Predictive Processing or wabi-sabi aesthetics instead). Need to check paper's actual stimuli.",
    },
    {
        "claim": "Biophilia hypothesis lacks empirical falsifiability",
        "lhs": ["theory.biophilia_hypothesis"],
        "rhs": "misc.theoretical_validity",
        "polarity": "negative",
        "judgment": "CHALLENGES",
        "reasoning": "This is a methodological critique of the theory itself, not empirical evidence for or against its predictions.",
    },
]
