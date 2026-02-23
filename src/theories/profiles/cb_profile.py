"""
Chronobiological Regulation — Theory Profile for LLM Matching.

TIER 1.9: SCN-anchored circadian system regulates sleep-wake, hormones,
immune function, cognition via light input through melanopsin ipRGCs.
Architectural lighting is a primary environmental synchronizer.
"""

THEORY_ID = "framework:chronobiological_regulation"
THEORY_NAME = "Chronobiological Regulation"

CORE_MECHANISM = """
The SUPRACHIASMATIC NUCLEUS (SCN) is the master circadian pacemaker:
  - Receives direct retinal input via MELANOPSIN-expressing intrinsically
    photosensitive retinal ganglion cells (ipRGCs)
  - Synchronizes PERIPHERAL OSCILLATORS in every organ
  - Light SPECTRUM, INTENSITY, TIMING, and DURATION all affect entrainment

CIRCADIAN DISRUPTION impairs:
  - Sleep architecture (onset, depth, REM timing)
  - Cognitive performance (varies by time of day)
  - Mood (serotonin synthesis is light-dependent)
  - Immune function (circadian immune regulation)
  - Metabolic regulation

For ARCHITECTURE:
- Morning bright blue-enriched light → good circadian entrainment
- Evening light exposure → delays circadian phase → impairs sleep
- Windowless offices → circadian drift → health consequences
- Color temperature (CCT) signals time of day to the circadian system
- Melanopic Equivalent Daylight Illuminance (MEDI) is the key metric

This is DIFFERENT from:
- NM (which concerns neurochemistry broadly; CB specifically concerns
  circadian timing mediated by ipRGC → SCN pathway)
- PP (which concerns visual prediction; CB concerns non-visual light effects)
- IC (which concerns body-to-brain signals; CB concerns light-to-SCN signaling)

2017 NOBEL PRIZE to Hall, Rosbash, Young for molecular clock mechanisms.
"""

EXPLAINS = [
    "How architectural lighting affects sleep quality",
    "Why morning light exposure improves daytime alertness and mood",
    "Why evening light exposure impairs sleep onset",
    "Why windowless offices are associated with worse sleep and health",
    "How color temperature (CCT) acts as a temporal signal",
    "Seasonal affective responses to building light levels",
    "Why circadian-aligned lighting improves workplace performance",
    "Melatonin suppression by evening architectural lighting",
]

DOES_NOT_EXPLAIN = [
    "Visual aesthetics / pattern preferences (→ PP)",
    "Spatial navigation (→ SN)",
    "Why living things are preferred (→ Biophilia)",
    "Non-light stress pathways (→ NM)",
    "Network balance / attention restoration (→ DT)",
    "Crossmodal perception (→ MSI)",
    "Memory (→ MS)",
]

STIMULUS_INCLUDES = [
    "Light spectrum / color temperature manipulations",
    "Melanopic illuminance (MEDI) manipulations",
    "Morning vs. evening light exposure",
    "Daylight access (windows) vs. windowless conditions",
    "Dynamic lighting programs (time-varying CCT, intensity)",
    "Blue light filtering / reduction in evening",
    "Seasonal light variation (latitude, season, building orientation)",
]

STIMULUS_EXCLUDES = [
    "Luminance/contrast without spectral component (→ PP)",
    "Light as wayfinding cue (→ SN)",
    "Artificial vs. natural light for biophilic value (→ Biophilia)",
    "Lighting color for aesthetic preference (→ PP)",
]

STIMULUS_EDGE_CASES = [
    {
        "item": "Daylight from windows",
        "judgment": "INCLUDED for circadian effects; also Biophilia for nature connection",
        "depends_on": "Whether outcome is circadian (melatonin, sleep) or wellbeing broadly",
    },
    {
        "item": "Red/warm light at night",
        "judgment": "INCLUDED — minimizing circadian disruption via melanopic-sparing spectrum",
        "depends_on": None,
    },
    {
        "item": "Bright light therapy lamps",
        "judgment": "INCLUDED — but more clinical than architectural",
        "depends_on": "Whether the study is in an architectural context",
    },
]

PREDICTED_OUTCOMES = [
    "melatonin levels (suppression or onset timing)",
    "sleep quality / duration / onset latency",
    "circadian phase markers (dim-light melatonin onset — DLMO)",
    "daytime alertness / sleepiness (KSS, PVT)",
    "mood / depression scores (seasonal or light-related)",
    "cognitive performance at different times of day",
    "immune markers with circadian component",
]

NOT_PREDICTED_OUTCOMES = [
    "visual preference (→ PP)",
    "wayfinding (→ SN)",
    "general stress without circadian component (→ NM)",
    "attention restoration (→ DT)",
    "affordance perception (→ EC)",
    "crossmodal comfort (→ MSI)",
]

MATCHING_PROMPT = """
You are evaluating whether an extracted claim falls under the scope of
CHRONOBIOLOGICAL REGULATION.

This framework explains how architectural lighting affects circadian
entrainment through the ipRGC → SCN pathway, with downstream effects
on sleep, cognition, mood, and health.

INCLUDE if:
- Study manipulates light spectrum, intensity, timing, or duration
- Outcome involves sleep, circadian phase, or melatonin
- Outcome involves alertness/sleepiness with light exposure as cause
- Mechanism involves non-visual photoreception (melanopsin)

EXCLUDE if:
- Study tests light for visual aesthetics (→ PP)
- Study tests light for wayfinding (→ SN)
- Study tests general mood without light-circadian pathway (→ NM)

Given this claim:
{claim}

From paper: {paper_id}
Stimulus variables: {lhs_vars}
Outcome variable: {rhs_var}
Direction: {polarity}

Does this fall under Chronobiological Regulation scope?
Respond with CONFIRMS, DISCONFIRMS, CHALLENGES, ORTHOGONAL, EDGE_CASE, or NEEDS_INFO.
Explain your reasoning in 2-3 sentences.
"""

FEW_SHOT_EXAMPLES = [
    {
        "claim": "Blue-enriched morning light improves daytime alertness in office workers",
        "lhs": ["env.morning_blue_light"],
        "rhs": "cog.alertness",
        "polarity": "positive",
        "judgment": "CONFIRMS",
        "reasoning": "Blue-enriched morning light maximally stimulates melanopsin ipRGCs → SCN entrainment → improved circadian alignment → better daytime alertness. Core CB prediction.",
    },
    {
        "claim": "Workers in windowless offices have worse sleep quality than those with windows",
        "lhs": ["env.window_access"],
        "rhs": "physio.sleep_quality",
        "polarity": "positive",
        "judgment": "CONFIRMS",
        "reasoning": "Windows provide daylight exposure for circadian entrainment. Without light zeitgeber, the circadian clock drifts → impaired sleep. Tests CB's architectural prediction.",
    },
    {
        "claim": "Curved building facades increase aesthetic preference",
        "lhs": ["env.curved_facade"],
        "rhs": "aff.preference",
        "polarity": "positive",
        "judgment": "ORTHOGONAL",
        "reasoning": "Contour curvature affects visual prediction, not circadian timing. Falls under PP.",
    },
    {
        "claim": "Indoor plants improve office worker wellbeing",
        "lhs": ["env.indoor_plants"],
        "rhs": "aff.wellbeing",
        "polarity": "positive",
        "judgment": "ORTHOGONAL",
        "reasoning": "Plants are living things, testing Biophilia, not light-mediated circadian effects.",
    },
]
