"""
dv_generalization.py — T3 DV-Side Generalization Functions
==========================================================

Extends outcome_taxonomy.py with functions for determining whether
two outcome (dependent variable) measures can be generalized into
a single T3 belief or must remain separate.

Key principles (from expert panel):
  - Ellard: Creativity measures are NOT interchangeable (fluency ≠ originality)
  - Barrett: Cortisol (autonomic) ≠ self-report stress (conscious)
  - Dalton: Temporal scope is a boundary condition, not a generalization axis
  - Panel consensus: access level (conscious/autonomic/behavioral/neural) =
    don't-merge criterion; measurement instrument type = merge-with-caution

ADR: Extension layer — new file, no existing code modified.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple

LOGGER = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════
# DV Access Level (adapted from outcome_taxonomy.py AccessLevel)
# ══════════════════════════════════════════════════════════════════

class DVAccessLevel(Enum):
    """What aspect of the phenomenon is being measured.

    Per Barrett: These access DIFFERENT phenomena, not the same one
    more or less directly. Beliefs at different access levels must
    remain separate in T3.

    V10 panel #6 (Neuroscientist): Cortisol is NEUROENDOCRINE, not AUTONOMIC.
    HPA axis activation is mechanistically distinct from ANS responses (HR, EDA).
    """
    CONSCIOUS = "conscious"           # Self-report, questionnaire
    AUTONOMIC = "autonomic"           # HR, EDA, blood pressure
    NEUROENDOCRINE = "neuroendocrine" # Cortisol, melatonin, IgA (#6)
    BEHAVIORAL = "behavioral"         # Task performance, RT
    NEURAL = "neural"                 # fMRI, EEG
    ENVIRONMENTAL = "environmental"   # Physical measurement of space
    UNSPECIFIED = "unspecified"


class DVMeasurementType(Enum):
    """Type of measurement instrument.

    Per Ellard: Different types of creativity tests measure
    different cognitive processes.
    """
    SELF_REPORT = "self_report"          # Likert, VAS, questionnaire
    PERFORMANCE_TASK = "performance_task"  # Cognitive task
    PHYSIOLOGICAL = "physiological"      # Body-based measurement
    NEUROIMAGING = "neuroimaging"        # Brain imaging
    OBSERVATIONAL = "observational"     # Observer-coded behavior
    OBJECTIVE_MEASURE = "objective"     # Environmental sensor
    UNSPECIFIED = "unspecified"


# ══════════════════════════════════════════════════════════════════
# DV Equivalence Classes
# ══════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class DVNode:
    """A node in the DV generalization hierarchy."""
    node_id: str               # e.g., "cog.creativity.divergent.fluency"
    label: str
    parent_id: Optional[str] = None
    access_level: DVAccessLevel = DVAccessLevel.UNSPECIFIED
    measurement_type: DVMeasurementType = DVMeasurementType.UNSPECIFIED
    construct: str = ""        # The latent construct being measured
    equivalence_class: str = ""  # Group of interchangeable measures


# Hierarchical DV taxonomy with equivalence classes
# Based on existing outcome taxonomy + Ellard's creativity distinctions
DV_HIERARCHY: Dict[str, DVNode] = {
    # ---------- Cognition ----------
    "cog": DVNode("cog", "Cognition"),
    "cog.attention": DVNode("cog.attention", "Attention", parent_id="cog",
        construct="attentional capacity"),
    "cog.attention.sustained": DVNode("cog.attention.sustained", "Sustained Attention",
        parent_id="cog.attention", access_level=DVAccessLevel.BEHAVIORAL,
        measurement_type=DVMeasurementType.PERFORMANCE_TASK,
        construct="attentional capacity", equivalence_class="attention_tasks"),
    "cog.attention.selective": DVNode("cog.attention.selective", "Selective Attention",
        parent_id="cog.attention", access_level=DVAccessLevel.BEHAVIORAL,
        measurement_type=DVMeasurementType.PERFORMANCE_TASK,
        construct="attentional capacity", equivalence_class="attention_tasks"),
    "cog.creativity": DVNode("cog.creativity", "Creativity", parent_id="cog",
        construct="creative ability"),
    "cog.creativity.divergent": DVNode("cog.creativity.divergent", "Divergent Thinking",
        parent_id="cog.creativity", construct="divergent_production"),
    "cog.creativity.divergent.fluency": DVNode("cog.creativity.divergent.fluency",
        "Fluency (# ideas)", parent_id="cog.creativity.divergent",
        access_level=DVAccessLevel.BEHAVIORAL,
        measurement_type=DVMeasurementType.PERFORMANCE_TASK,
        construct="divergent_production", equivalence_class="divergent_tasks"),
    "cog.creativity.divergent.originality": DVNode("cog.creativity.divergent.originality",
        "Originality (novelty)", parent_id="cog.creativity.divergent",
        access_level=DVAccessLevel.BEHAVIORAL,
        measurement_type=DVMeasurementType.PERFORMANCE_TASK,
        construct="divergent_production", equivalence_class="divergent_tasks"),
    "cog.creativity.divergent.flexibility": DVNode("cog.creativity.divergent.flexibility",
        "Flexibility (# categories)", parent_id="cog.creativity.divergent",
        access_level=DVAccessLevel.BEHAVIORAL,
        measurement_type=DVMeasurementType.PERFORMANCE_TASK,
        construct="divergent_production", equivalence_class="divergent_tasks"),
    "cog.creativity.insight": DVNode("cog.creativity.insight", "Insight / Aha",
        parent_id="cog.creativity",
        access_level=DVAccessLevel.BEHAVIORAL,
        measurement_type=DVMeasurementType.PERFORMANCE_TASK,
        construct="insight_problem_solving", equivalence_class="insight_tasks"),
    "cog.creativity.remote_assoc": DVNode("cog.creativity.remote_assoc",
        "Remote Associates (RAT)", parent_id="cog.creativity",
        access_level=DVAccessLevel.BEHAVIORAL,
        measurement_type=DVMeasurementType.PERFORMANCE_TASK,
        construct="associative_thinking", equivalence_class="convergent_tasks"),
    "cog.performance": DVNode("cog.performance", "Cognitive Performance", parent_id="cog",
        construct="general_performance"),
    "cog.memory": DVNode("cog.memory", "Memory", parent_id="cog",
        construct="memory"),

    # ---------- Affect ----------
    "affect": DVNode("affect", "Affect / Emotion"),
    "affect.stress": DVNode("affect.stress", "Stress", parent_id="affect",
        construct="stress_response"),
    "affect.stress.self_report": DVNode("affect.stress.self_report",
        "Self-Reported Stress", parent_id="affect.stress",
        access_level=DVAccessLevel.CONSCIOUS,
        measurement_type=DVMeasurementType.SELF_REPORT,
        construct="perceived_stress", equivalence_class="stress_subjective"),
    "affect.stress.cortisol": DVNode("affect.stress.cortisol",
        "Salivary Cortisol", parent_id="affect.stress",
        access_level=DVAccessLevel.NEUROENDOCRINE,
        measurement_type=DVMeasurementType.PHYSIOLOGICAL,
        construct="hpa_axis_activation", equivalence_class="stress_neuroendocrine"),
    "affect.stress.hr": DVNode("affect.stress.hr",
        "Heart Rate / HRV", parent_id="affect.stress",
        access_level=DVAccessLevel.AUTONOMIC,
        measurement_type=DVMeasurementType.PHYSIOLOGICAL,
        construct="autonomic_arousal", equivalence_class="stress_autonomic"),
    "affect.mood": DVNode("affect.mood", "Mood / Valence", parent_id="affect",
        construct="affective_valence"),
    "affect.preference": DVNode("affect.preference", "Aesthetic Preference", parent_id="affect",
        construct="evaluative_response"),
    "affect.arousal": DVNode("affect.arousal", "Arousal", parent_id="affect",
        construct="arousal_level"),
    "affect.restoration": DVNode("affect.restoration", "Restoration / Recovery", parent_id="affect",
        construct="attentional_restoration"),
    "affect.restoration.restorativeness": DVNode("affect.restoration.restorativeness",
        "Perceived Restorativeness (PRS)", parent_id="affect.restoration",
        access_level=DVAccessLevel.CONSCIOUS,
        measurement_type=DVMeasurementType.SELF_REPORT,
        construct="restorative_quality", equivalence_class="restoration_scales"),
    "affect.awe": DVNode("affect.awe", "Awe", parent_id="affect",
        access_level=DVAccessLevel.CONSCIOUS,
        measurement_type=DVMeasurementType.SELF_REPORT,
        construct="awe_experience", equivalence_class="awe_measures"),
    "affect.fascination": DVNode("affect.fascination", "Fascination (Kaplan ART)",
        parent_id="affect",
        access_level=DVAccessLevel.CONSCIOUS,
        measurement_type=DVMeasurementType.SELF_REPORT,
        construct="involuntary_engagement", equivalence_class="fascination_measures"),
    "affect.valence": DVNode("affect.valence", "Affective Valence", parent_id="affect",
        access_level=DVAccessLevel.CONSCIOUS,
        construct="affective_valence_dimension"),
    "affect.arousal_affect": DVNode("affect.arousal_affect", "Affective Arousal",
        parent_id="affect",
        access_level=DVAccessLevel.CONSCIOUS,
        construct="arousal_dimension"),
    "affect.satisfaction": DVNode("affect.satisfaction", "Environmental Satisfaction",
        parent_id="affect",
        access_level=DVAccessLevel.CONSCIOUS,
        measurement_type=DVMeasurementType.SELF_REPORT,
        construct="environment_satisfaction", equivalence_class="satisfaction_scales"),

    # ---------- Behavior ----------
    "behav": DVNode("behav", "Behavior"),
    "behav.productivity": DVNode("behav.productivity", "Productivity", parent_id="behav",
        access_level=DVAccessLevel.BEHAVIORAL,
        construct="work_output"),
    "behav.social": DVNode("behav.social", "Social Behavior", parent_id="behav",
        construct="social_interaction"),
    "behav.movement": DVNode("behav.movement", "Movement / Wayfinding", parent_id="behav",
        construct="spatial_behavior"),
    "behav.sleep": DVNode("behav.sleep", "Sleep", parent_id="behav",
        construct="sleep_quality"),

    # ---------- Health ----------
    "health": DVNode("health", "Health / Wellbeing"),
    "health.wellbeing": DVNode("health.wellbeing", "Subjective Wellbeing", parent_id="health",
        access_level=DVAccessLevel.CONSCIOUS,
        construct="wellbeing"),
    "health.pain": DVNode("health.pain", "Pain", parent_id="health",
        construct="pain_perception"),
    "health.recovery": DVNode("health.recovery", "Clinical Recovery", parent_id="health",
        construct="health_recovery"),

    # ---------- Physiology ----------
    "physio": DVNode("physio", "Physiology"),
    "physio.cortisol": DVNode("physio.cortisol", "Cortisol Level", parent_id="physio",
        access_level=DVAccessLevel.NEUROENDOCRINE,
        measurement_type=DVMeasurementType.PHYSIOLOGICAL,
        construct="hpa_axis"),
    "physio.hr": DVNode("physio.hr", "Heart Rate", parent_id="physio",
        access_level=DVAccessLevel.AUTONOMIC,
        measurement_type=DVMeasurementType.PHYSIOLOGICAL,
        construct="cardiovascular"),
    "physio.eda": DVNode("physio.eda", "Electrodermal Activity", parent_id="physio",
        access_level=DVAccessLevel.AUTONOMIC,
        measurement_type=DVMeasurementType.PHYSIOLOGICAL,
        construct="sympathetic_arousal"),

    # ---------- Neural (Wave 8d, V10 #6 Neuroscientist) ----------
    "neural": DVNode("neural", "Neural Activity"),
    "neural.eeg": DVNode("neural.eeg", "EEG", parent_id="neural",
        access_level=DVAccessLevel.NEURAL,
        measurement_type=DVMeasurementType.NEUROIMAGING,
        construct="cortical_oscillation"),
    "neural.eeg.alpha_power": DVNode("neural.eeg.alpha_power", "Alpha Power (8-13 Hz)",
        parent_id="neural.eeg",
        access_level=DVAccessLevel.NEURAL,
        measurement_type=DVMeasurementType.NEUROIMAGING,
        construct="cortical_idling", equivalence_class="eeg_alpha"),
    "neural.eeg.alpha_asymmetry": DVNode("neural.eeg.alpha_asymmetry",
        "Frontal Alpha Asymmetry", parent_id="neural.eeg",
        access_level=DVAccessLevel.NEURAL,
        measurement_type=DVMeasurementType.NEUROIMAGING,
        construct="approach_withdrawal", equivalence_class="eeg_alpha"),
    "neural.eeg.alpha_peak_freq": DVNode("neural.eeg.alpha_peak_freq",
        "Individual Alpha Peak Frequency", parent_id="neural.eeg",
        access_level=DVAccessLevel.NEURAL,
        measurement_type=DVMeasurementType.NEUROIMAGING,
        construct="cognitive_speed", equivalence_class="eeg_alpha"),
    "neural.eeg.theta_power": DVNode("neural.eeg.theta_power", "Theta Power (4-8 Hz)",
        parent_id="neural.eeg",
        access_level=DVAccessLevel.NEURAL,
        measurement_type=DVMeasurementType.NEUROIMAGING,
        construct="memory_encoding", equivalence_class="eeg_theta"),
    "neural.eeg.theta_fm": DVNode("neural.eeg.theta_fm",
        "Frontal Midline Theta", parent_id="neural.eeg",
        access_level=DVAccessLevel.NEURAL,
        measurement_type=DVMeasurementType.NEUROIMAGING,
        construct="cognitive_control", equivalence_class="eeg_theta"),
    "neural.eeg.beta_power": DVNode("neural.eeg.beta_power", "Beta Power (13-30 Hz)",
        parent_id="neural.eeg",
        access_level=DVAccessLevel.NEURAL,
        measurement_type=DVMeasurementType.NEUROIMAGING,
        construct="active_cognition", equivalence_class="eeg_beta"),
    "neural.eeg.gamma_power": DVNode("neural.eeg.gamma_power", "Gamma Power (30-100 Hz)",
        parent_id="neural.eeg",
        access_level=DVAccessLevel.NEURAL,
        measurement_type=DVMeasurementType.NEUROIMAGING,
        construct="feature_binding", equivalence_class="eeg_gamma"),
    "neural.fmri_bold": DVNode("neural.fmri_bold", "fMRI BOLD Signal",
        parent_id="neural",
        access_level=DVAccessLevel.NEURAL,
        measurement_type=DVMeasurementType.NEUROIMAGING,
        construct="hemodynamic_response"),
}


# ══════════════════════════════════════════════════════════════════
# Generalization Functions
# ══════════════════════════════════════════════════════════════════

def get_dv_node(node_id: str) -> Optional[DVNode]:
    """Look up a DV node."""
    return DV_HIERARCHY.get(node_id)


def dv_ancestors(node_id: str) -> List[str]:
    """Get all ancestor IDs of a DV node."""
    result = []
    current = node_id
    while current:
        node = DV_HIERARCHY.get(current)
        if node and node.parent_id:
            result.append(node.parent_id)
            current = node.parent_id
        else:
            break
    return result


def dv_common_ancestor(id_a: str, id_b: str) -> Optional[str]:
    """Find the lowest common ancestor of two DV nodes."""
    ancestors_a = set(dv_ancestors(id_a)) | {id_a}
    current = id_b
    while current:
        if current in ancestors_a:
            return current
        node = DV_HIERARCHY.get(current)
        if node and node.parent_id:
            current = node.parent_id
        else:
            break
    return None


def can_generalize_dvs(
    id_a: str,
    id_b: str,
    strict_access_level: bool = True,
) -> Tuple[bool, str]:
    """
    Can two DV measures be generalized into a single T3 belief?

    Rules (from panel):
    1. Barrett: Different access levels → MUST NOT merge
       (cortisol ≠ self-report stress, even if both "about stress")
    2. Ellard: Same equivalence class → CAN merge
       (fluency and originality both measure divergent thinking)
    3. Same construct → CAN merge with caution
    4. Different constructs → MUST NOT merge

    Returns (can_generalize, reason).
    """
    node_a = DV_HIERARCHY.get(id_a)
    node_b = DV_HIERARCHY.get(id_b)

    if not node_a or not node_b:
        return False, f"Unknown DV node(s): {id_a}, {id_b}"

    # Rule 1: Access level check (Barrett)
    if strict_access_level:
        if (node_a.access_level != DVAccessLevel.UNSPECIFIED and
            node_b.access_level != DVAccessLevel.UNSPECIFIED and
            node_a.access_level != node_b.access_level):
            return False, (
                f"Different access levels: {node_a.access_level.value} "
                f"vs {node_b.access_level.value} (Barrett rule)"
            )

    # Rule 2: Same equivalence class → OK
    if (node_a.equivalence_class and node_b.equivalence_class and
        node_a.equivalence_class == node_b.equivalence_class):
        return True, f"Same equivalence class: {node_a.equivalence_class}"

    # Rule 3: Same construct → merge with caution
    if (node_a.construct and node_b.construct and
        node_a.construct == node_b.construct):
        return True, f"Same construct: {node_a.construct}"

    # Rule 4: Check common ancestor
    lca = dv_common_ancestor(id_a, id_b)
    if lca and lca not in ("cog", "affect", "behav", "health", "physio"):
        # Non-root common ancestor → probably same construct area
        return True, f"Common ancestor: {lca}"

    return False, "Different constructs, no shared equivalence class"


def dv_equivalence_class(node_id: str) -> Set[str]:
    """
    Get the set of DV nodes that are measurement-equivalent to this one.

    All members of an equivalence class measure the same underlying
    construct and can be merged in T3 without loss of information.
    """
    node = DV_HIERARCHY.get(node_id)
    if not node or not node.equivalence_class:
        return {node_id}

    return {
        nid for nid, n in DV_HIERARCHY.items()
        if n.equivalence_class == node.equivalence_class
    }


def dv_generalization_distance(id_a: str, id_b: str) -> int:
    """Distance between two DV nodes in the hierarchy."""
    lca = dv_common_ancestor(id_a, id_b)
    if lca is None:
        return 999
    node_a = DV_HIERARCHY.get(id_a)
    node_b = DV_HIERARCHY.get(id_b)
    if not node_a or not node_b:
        return 999
    depth_a = len(dv_ancestors(id_a))
    depth_b = len(dv_ancestors(id_b))
    depth_lca = len(dv_ancestors(lca))
    return (depth_a + depth_b) - 2 * depth_lca
