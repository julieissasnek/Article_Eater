"""
Memory Systems — Theory Profile for LLM Matching.

TIER 1.7: Hippocampal-cortical consolidation. Rapid episodic encoding +
slow cortical learning. Semantic architectural knowledge = the generative
model's priors. Cultural variation = different priors.
"""

THEORY_ID = "framework:memory_systems"
THEORY_NAME = "Memory Systems (Hippocampal-Cortical Consolidation)"

CORE_MECHANISM = """
Two COMPLEMENTARY LEARNING SYSTEMS interact:
  - HIPPOCAMPUS: Rapid episodic encoding. One-shot learning of specific
    experiences. First impressions of buildings are encoded here.
  - CORTEX: Slow statistical learning. Extracts regularities across many
    experiences. Builds semantic knowledge (priors for future encounters).

For ARCHITECTURE this means:
- FIRST IMPRESSIONS persist strongly (rapid hippocampal encoding)
- Semantic architectural knowledge = the GENERATIVE MODEL'S PRIORS
  (what you expect when entering a building type)
- CULTURAL VARIATION reflects DIFFERENT PRIORS — people from different
  architectural cultures have different expectations
- SLEEP consolidation transfers episodic architectural experiences to
  semantic knowledge

This explains WHY people develop "architectural taste" — it's accumulated
semantic knowledge shaping predictions (connecting to PP).

This is DIFFERENT from:
- SN (which concerns spatial maps; MS concerns episodic/semantic memory)
- PP (which uses the priors; MS explains how priors are formed)
- DP (which concerns processing mode; MS concerns memory formation)
"""

EXPLAINS = [
    "First impression effects (rapid hippocampal encoding)",
    "Cultural variation in architectural preference (different semantic priors)",
    "Expertise effects (architects vs. non-architects have different priors)",
    "Why repeated exposure changes preference (model updates)",
    "How architectural styles are learned and recognized",
    "Place attachment (strong episodic encoding tied to location)",
    "Nostalgia effects in architecture (episodic memory reactivation)",
]

DOES_NOT_EXPLAIN = [
    "Which visual features generate prediction error (→ PP)",
    "How spatial layout affects navigation (→ SN, though hippocampus is shared)",
    "Specific neurochemical stress pathways (→ NM)",
    "Circadian effects (→ CB)",
    "Crossmodal integration (→ MSI)",
    "Why living things are preferred (→ Biophilia)",
]

STIMULUS_INCLUDES = [
    "Repeated exposure to architectural stimuli (learning effects)",
    "Cross-cultural comparisons of architectural preference",
    "Expertise comparisons (architects vs. lay people)",
    "First impression vs. prolonged experience",
    "Familiar vs. novel building types",
    "Place attachment and sense of place measures",
    "Sleep effects on architectural learning (consolidation)",
]

STIMULUS_EXCLUDES = [
    "One-time visual preference without learning component (→ PP)",
    "Spatial layout effects without memory component (→ SN)",
    "Physiological stress without memory framing (→ NM)",
    "Light spectrum effects (→ CB)",
]

STIMULUS_EDGE_CASES = [
    {
        "item": "Nostalgia-inducing architectural elements",
        "judgment": "INCLUDED — episodic memory reactivation driving affect",
        "depends_on": "Whether the study measures memory processes or just generic preference",
    },
    {
        "item": "Expertise effects on architectural judgment",
        "judgment": "INCLUDED — different semantic priors from training/exposure",
        "depends_on": None,
    },
]

PREDICTED_OUTCOMES = [
    "recognition memory / familiarity",
    "first impression persistence",
    "cultural differences in preference",
    "expertise differences in evaluation",
    "exposure effects (mere exposure, learning curves)",
    "place attachment / sense of belonging",
    "architectural style categorization",
]

NOT_PREDICTED_OUTCOMES = [
    "processing fluency without learning component (→ PP)",
    "wayfinding performance (→ SN)",
    "physiological stress (→ NM)",
    "circadian effects (→ CB)",
    "affective construction (→ IC)",
    "attention restoration (→ DT)",
]

MATCHING_PROMPT = """
You are evaluating whether an extracted claim falls under the scope of
MEMORY SYSTEMS (hippocampal-cortical consolidation).

This framework explains how architectural experience involves episodic memory,
semantic knowledge (priors), cultural learning, and expertise effects.

INCLUDE if:
- Study compares first impression vs. later evaluation
- Study compares cultural groups or expertise levels
- Study measures learning or exposure effects on preference
- Study tests place attachment or sense of place
- Mechanism involves memory formation, consolidation, or retrieval

EXCLUDE if:
- Study tests one-time visual preference without learning (→ PP)
- Study tests spatial navigation (→ SN)
- Study tests stress physiology (→ NM)

Given this claim:
{claim}

From paper: {paper_id}
Stimulus variables: {lhs_vars}
Outcome variable: {rhs_var}
Direction: {polarity}

Does this fall under Memory Systems scope?
Respond with CONFIRMS, DISCONFIRMS, CHALLENGES, ORTHOGONAL, EDGE_CASE, or NEEDS_INFO.
Explain your reasoning in 2-3 sentences.
"""

FEW_SHOT_EXAMPLES = [
    {
        "claim": "Architects and non-architects differ in their aesthetic evaluation of building facades",
        "lhs": ["person.expertise"],
        "rhs": "aff.aesthetic_evaluation",
        "polarity": "interaction",
        "judgment": "CONFIRMS",
        "reasoning": "Expertise differences reflect different semantic priors built through years of cortical learning. Architects have different generative models of architecture than lay people.",
    },
    {
        "claim": "First impressions of hospital lobbies predict overall satisfaction better than later evaluations",
        "lhs": ["env.hospital_lobby_first_impression"],
        "rhs": "aff.overall_satisfaction",
        "polarity": "positive",
        "judgment": "CONFIRMS",
        "reasoning": "Rapid hippocampal encoding creates strong, persistent first impressions that anchor subsequent evaluation. A core MS prediction.",
    },
    {
        "claim": "Nature views improve directed attention performance",
        "lhs": ["env.nature_view"],
        "rhs": "cog.directed_attention",
        "polarity": "positive",
        "judgment": "ORTHOGONAL",
        "reasoning": "This is an attention restoration effect (DT/ART), not a memory or learning effect.",
    },
]
