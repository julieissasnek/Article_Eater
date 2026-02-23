"""
Dual-Process Theory — Theory Profile for LLM Matching.

TIER 1.3: Fast implicit (System 1) vs. slow deliberate (System 2) processing.
Most architectural experience is processed implicitly; physiological measures
detect effects missed by self-report.
"""

THEORY_ID = "framework:dual_process"
THEORY_NAME = "Dual-Process Theory (Implicit vs. Explicit)"

CORE_MECHANISM = """
Two processing systems operate constantly:
  - System 1 (Type 1): FAST, automatic, implicit. Uses subcortical circuits
    (amygdala, basal ganglia) and sensory cortices. First affective response
    within hundreds of milliseconds.
  - System 2 (Type 2): SLOW, deliberate, explicit. Recruits prefrontal cortex
    and working memory. Can override System 1 but requires effort.

For ARCHITECTURE this means:
- MOST environmental experience is processed IMPLICITLY — first (<500ms)
- Self-report captures only the explicit (System 2) response
- Physiological measures (cortisol, HRV, EDA, EEG) capture implicit responses
- Discrepancy between self-report and physiology is MEANINGFUL — reveals
  implicit-explicit conflict

KEY METHODOLOGICAL IMPLICATION: Studies using only self-report may MISS
environmental effects that are processed implicitly.

This is DIFFERENT from:
- Predictive Processing (which concerns prediction error, not System 1/2 distinction)
- Interoception (which concerns body-to-brain signals, not processing mode)
"""

EXPLAINS = [
    "Why physiological measures detect effects self-report misses",
    "Implicit-explicit dissociations in environmental preference",
    "Rapid affective responses to architecture (<500ms)",
    "Why conscious evaluation sometimes contradicts bodily response",
    "Methodological importance of multi-measure approaches",
    "Implicit priming effects of environmental features",
]

DOES_NOT_EXPLAIN = [
    "What specific environmental features trigger prediction error (→ PP)",
    "How spatial layout affects navigation (→ SN)",
    "Why living things are preferred (→ Biophilia)",
    "Specific neurochemical mechanisms of stress/reward (→ NM)",
    "Circadian effects (→ CB)",
    "Crossmodal interactions (→ MSI)",
]

STIMULUS_INCLUDES = [
    "Any environmental manipulation measured with BOTH physiological AND self-report",
    "Subliminal or brief environmental exposures (testing implicit processing)",
    "Implicit Association Tests (IAT) for architectural features",
    "Eye-tracking during architectural evaluation (implicit attention)",
    "EEG event-related potentials during environmental viewing",
    "Priming paradigms using architectural stimuli",
]

STIMULUS_EXCLUDES = [
    "Studies using only self-report (cannot test dual-process claim)",
    "Studies using only physiological measures without self-report comparison",
    "Environmental manipulations without measurement method as focus",
]

STIMULUS_EDGE_CASES = [
    {
        "item": "VR environments with physiological monitoring",
        "judgment": "INCLUDED if comparing implicit and explicit responses",
        "depends_on": "Whether the study specifically tests implicit-explicit dissociation",
    },
    {
        "item": "Post-occupancy evaluation surveys",
        "judgment": "EXCLUDED — pure self-report, cannot test DP claims",
        "depends_on": None,
    },
    {
        "item": "Thermal comfort with skin temperature + self-report",
        "judgment": "INCLUDED if testing whether implicit body response differs from reported comfort",
        "depends_on": "Whether the study frames this as implicit-explicit comparison",
    },
]

PREDICTED_OUTCOMES = [
    "implicit-explicit dissociations (physiology ≠ self-report)",
    "rapid affective response (ERP, EDA) preceding conscious evaluation",
    "implicit preference (IAT, priming effects)",
    "measurement method moderation (effect found with one method but not another)",
]

NOT_PREDICTED_OUTCOMES = [
    "specific affective valence (which emotions → IC/NM)",
    "wayfinding performance (→ SN)",
    "aesthetic preference per se (→ PP)",
    "circadian effects (→ CB)",
    "memory for environments (→ MS)",
]

MATCHING_PROMPT = """
You are evaluating whether an extracted claim falls under the scope of
DUAL-PROCESS THEORY (System 1/System 2, implicit vs. explicit processing).

This framework claims most architectural experience is processed implicitly
(System 1), and that physiological measures reveal effects missed by self-report.

INCLUDE if:
- Study compares implicit and explicit measures of same environmental effect
- Study uses physiological measures alongside self-report
- Finding involves implicit-explicit dissociation
- Study uses rapid exposure paradigms testing pre-conscious processing

EXCLUDE if:
- Study uses only self-report (cannot test DP claims)
- Study uses only physiological measures without comparison
- Environmental effect is domain-specific (wayfinding → SN, light → CB)

Given this claim:
{claim}

From paper: {paper_id}
Stimulus variables: {lhs_vars}
Outcome variable: {rhs_var}
Direction: {polarity}

Does this fall under Dual-Process Theory scope?
Respond with CONFIRMS, DISCONFIRMS, CHALLENGES, ORTHOGONAL, EDGE_CASE, or NEEDS_INFO.
Explain your reasoning in 2-3 sentences.
"""

FEW_SHOT_EXAMPLES = [
    {
        "claim": "Physiological stress markers increase in open-plan offices while self-reported satisfaction remains stable",
        "lhs": ["env.open_plan"],
        "rhs": "physio.stress_markers + self_report.satisfaction",
        "polarity": "dissociation",
        "judgment": "CONFIRMS",
        "reasoning": "This is a classic implicit-explicit dissociation: the body detects environmental stress that conscious self-report does not acknowledge. Core DP prediction.",
    },
    {
        "claim": "ERP N400 amplitude increases when viewing incongruent architectural scenes",
        "lhs": ["env.scene_incongruence"],
        "rhs": "physio.erp_n400",
        "polarity": "positive",
        "judgment": "EDGE_CASE",
        "reasoning": "ERP N400 is an implicit measure of semantic violation. This tests implicit processing of architectural coherence but may also be PP (prediction error). Needs context on whether explicit measures were also collected.",
    },
    {
        "claim": "Nature views improve directed attention",
        "lhs": ["env.nature_view"],
        "rhs": "cog.directed_attention",
        "polarity": "positive",
        "judgment": "ORTHOGONAL",
        "reasoning": "This is an ART/DT claim about attention restoration, not about implicit vs. explicit processing. No implicit-explicit comparison is present.",
    },
]
