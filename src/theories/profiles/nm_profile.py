"""
Neuromodulatory Systems — Theory Profile for LLM Matching.

TIER 1.5: Dopamine, norepinephrine, cortisol/HPA, serotonin, oxytocin,
endogenous opioids modulate cognition and affect through well-characterized
pharmacology. Subsumes the old Allostatic Load Model.
"""

THEORY_ID = "framework:neuromodulatory"
THEORY_NAME = "Neuromodulatory Systems"

CORE_MECHANISM = """
The brain's major NEUROMODULATORY SYSTEMS modulate cognition and affect:
  - DOPAMINE: Reward prediction error. Novelty, beauty, architectural
    delight ↑DA in mesolimbic pathway.
  - NOREPINEPHRINE (LC-NE): Gain modulation and explore/exploit.
    Alarming environments → high NE → exploration mode; safe → low NE → exploit.
  - CORTISOL / HPA AXIS: Chronic stress → allostatic load → hippocampal
    damage, immune suppression. Architectural stressors accumulate.
  - SEROTONIN: Mood regulation, social behavior. Light affects serotonin.
  - OXYTOCIN: Social bonding. Social architectural features modulate.
  - ENDOGENOUS OPIOIDS: Pleasure, comfort. Aesthetic experiences activate.

SUBSUMES the old "Allostatic Load Model" (just the HPA axis component).

For ARCHITECTURE: specific environmental features have specific neurochemical
effects — this is NOT a general "environments affect mood" claim.

This is DIFFERENT from:
- PP (which concerns prediction error computation, not neurochemistry)
- IC (which concerns body-to-brain interoception, not transmitter systems)
- DT (which concerns network dynamics, not neurochemistry)
"""

EXPLAINS = [
    "Chronic environmental stress → allostatic load → health consequences",
    "Reward/pleasure from architectural beauty (dopaminergic)",
    "Arousal modulation by environmental novelty/threat (noradrenergic)",
    "How light affects mood (serotonergic, separate from circadian CB effects)",
    "Social behavior in architectural spaces (oxytocinergic)",
    "Explore-exploit tradeoffs in building navigation (LC-NE)",
    "Why environmental stressors accumulate over time (allostatic load)",
    "Acute vs. chronic stress distinction in environmental response",
]

DOES_NOT_EXPLAIN = [
    "Which patterns generate prediction error (→ PP)",
    "How spatial layout affects navigation (→ SN)",
    "Why living things are preferred (→ Biophilia)",
    "Circadian timing mechanisms (→ CB, though cortisol has circadian rhythm)",
    "DMN/TPN balance and attention fatigue (→ DT)",
    "Crossmodal perceptual integration (→ MSI)",
]

STIMULUS_INCLUDES = [
    "Environmental stressors (noise, crowding, pollution, lack of control)",
    "Chronic environmental exposure (occupational settings, housing)",
    "Social environmental features (privacy, territory, encounter patterns)",
    "Rewarding architectural experiences (beauty, delight, awe)",
    "Light exposure with mood outcomes (serotonergic pathway)",
    "Novel vs. familiar environments (dopaminergic, noradrenergic)",
    "Controllability manipulations (perceived control over environment)",
]

STIMULUS_EXCLUDES = [
    "Visual patterns without stress/reward component (→ PP)",
    "Spatial layout without stress/social component (→ SN)",
    "Light spectrum effects on circadian timing specifically (→ CB)",
    "Body posture / motor effects (→ EC)",
]

STIMULUS_EDGE_CASES = [
    {
        "item": "Open-plan office stress",
        "judgment": "INCLUDED for cortisol/NE effects; also DT for attention fatigue",
        "depends_on": "Whether outcome is physiological stress markers (NM) or cognitive fatigue (DT)",
    },
    {
        "item": "Architectural awe (cathedrals, dramatic spaces)",
        "judgment": "INCLUDED — likely dopaminergic reward + possible opioidergic pleasure",
        "depends_on": "Whether the study measures neurochemical correlates or just self-report",
    },
]

PREDICTED_OUTCOMES = [
    "cortisol levels (HPA axis)",
    "heart rate variability (HRV — autonomic regulation)",
    "blood pressure (sympathetic activation)",
    "immune markers (allostatic load consequences)",
    "mood / affective valence",
    "reward-related behavior / willingness to pay",
    "social behavior / prosociality",
    "arousal / anxiety",
]

NOT_PREDICTED_OUTCOMES = [
    "processing fluency / reaction time (→ PP)",
    "wayfinding performance (→ SN)",
    "directed attention specifically (→ DT)",
    "circadian phase / melatonin (→ CB)",
    "thermal perception (→ MSI)",
    "memory encoding specifically (→ MS)",
]

MATCHING_PROMPT = """
You are evaluating whether an extracted claim falls under the scope of
NEUROMODULATORY SYSTEMS (dopamine, norepinephrine, cortisol, serotonin,
oxytocin).

This framework explains how specific environmental features modulate cognition
and affect through well-characterized neurochemical pathways.

INCLUDE if:
- Study measures physiological stress markers (cortisol, HRV, BP)
- Study tests chronic environmental exposure → health outcomes
- Study measures reward/pleasure from architectural features
- Mechanism involves specific neurotransmitter systems

EXCLUDE if:
- Study tests prediction error / visual patterns (→ PP)
- Study tests spatial navigation (→ SN)
- Study tests circadian timing specifically (→ CB)
- Study tests attention restoration (→ DT)

Given this claim:
{claim}

From paper: {paper_id}
Stimulus variables: {lhs_vars}
Outcome variable: {rhs_var}
Direction: {polarity}

Does this fall under Neuromodulatory Systems scope?
Respond with CONFIRMS, DISCONFIRMS, CHALLENGES, ORTHOGONAL, EDGE_CASE, or NEEDS_INFO.
Explain your reasoning in 2-3 sentences.
"""

FEW_SHOT_EXAMPLES = [
    {
        "claim": "Chronic noise exposure increases cortisol levels in office workers",
        "lhs": ["env.chronic_noise"],
        "rhs": "physio.cortisol",
        "polarity": "positive",
        "judgment": "CONFIRMS",
        "reasoning": "Chronic environmental stressor → HPA axis activation → cortisol increase. This is a core allostatic load prediction of the NM framework.",
    },
    {
        "claim": "Beautiful architectural spaces activate the brain's reward circuit",
        "lhs": ["env.architectural_beauty"],
        "rhs": "neuro.reward_circuit_activation",
        "polarity": "positive",
        "judgment": "CONFIRMS",
        "reasoning": "Architectural beauty → dopaminergic reward signal. This tests the DA-mediated aesthetic reward pathway.",
    },
    {
        "claim": "Fractal patterns in facades increase visual preference",
        "lhs": ["env.fractal_pattern"],
        "rhs": "aff.preference",
        "polarity": "positive",
        "judgment": "ORTHOGONAL",
        "reasoning": "This tests visual pattern processing and preference, not neurochemical mechanisms. Falls under PP (fractal structure matches generative model).",
    },
]
