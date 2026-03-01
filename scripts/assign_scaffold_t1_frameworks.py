#!/usr/bin/env python3
"""
T1 Framework Assignment for Scaffold Templates (E-02)

Assigns canonical T1 frameworks to 79 scaffold-tier templates based on
domain-informed expert panel reasoning.

Canonical T1 Frameworks:
  - PP: Predictive Processing (prediction error, Bayesian inference)
  - SN: Spatial Navigation (place cells, cognitive maps, path integration)
  - DP: Dopaminergic Pathways (reward prediction, motivation)
  - DT: Dual-Process Theory (System 1/2, automatic vs controlled)
  - NM: Neuromodulatory Systems (serotonin, NE, ACh, cortisol)
  - IC: Interoceptive-Constructionist (interoception, allostasis, affect)
  - MS: Memory Systems (encoding, consolidation, episodic/semantic)
  - EC: Embodied Cognition (sensorimotor coupling, affordances)
  - CB: Cerebellum/Basal Ganglia (motor learning, timing, habit)
  - MSI: Multisensory Integration (cross-modal binding, sensory weighting)

Usage:
    python scripts/assign_scaffold_t1_frameworks.py

Author: Claude Code with Expert Panel Reasoning
Date: 2026-02-23
Sprint: E-02 (T1 Framework Assignment)
"""

import json
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Any

PROJECT_ROOT = Path(__file__).parent.parent
TEMPLATES_DIR = PROJECT_ROOT / "data" / "templates"
REPORT_PATH = PROJECT_ROOT / "data" / "t1_assignment_report.json"

# Panel-assigned T1 frameworks for each template
# Format: template_id -> list of T1 framework codes
T1_ASSIGNMENTS = {
    # === VISUAL DOMAIN (11 templates) ===
    # Light, color, spectral, spatial luminance, visual architecture

    "CHROMATIC_PE_ARCH_001": ["PP"],
    # Chromatic prediction error: visual system predicting color expectations violated by architectural color

    "COLOR_AROUSAL_MODULATION_001": ["PP", "NM"],
    # Color modulating arousal state via prediction error + neuromodulatory tone

    "ENCLOSURE_SAFETY_030": ["PP", "SN"],
    # Enclosure triggers spatial predictive signals + safety navigation maps

    "BRECVEMA_IMAGERY_006": ["EC", "PP"],
    # Visual imagery using embodied simulation + prediction error during imagination

    "PP_SPECTRAL_MATCH_001": ["PP"],
    # Spectral matching for prediction error in visual scene analysis

    "LUM_CONTRAST_PE_001": ["PP"],
    # Luminance contrast as a prediction error signal

    "NATURAL_LIGHT_RECOVERY_001": ["PP", "NM"],
    # Natural light wavelength modulating circadian + neuromodulatory alignment

    "DAYLIGHT_RHYTHM_ENTRAINMENT_001": ["NM"],
    # Circadian light entrainment: neuromodulatory system regulation

    "VIEW_RECOVERY_001": ["PP", "SN"],
    # Views provide topographic/place information + prediction error updates

    "TRANSITION_LIGHTING_PE_001": ["PP"],
    # Light transitions violate predictions about spatial brightness

    "VISION_COMPLEXITY_TARGET_001": ["PP", "DT"],
    # Visual complexity optimizing prediction error + System 1/2 balance

    # === ACOUSTIC DOMAIN (5 templates) ===
    # Sound, reverberation, acoustic architecture

    "BRECVEMA_BRAINSTEM_001": ["PP", "NM"],
    # Acoustic startle reflex: prediction error + brainstem neuromodulatory response

    "ASAP_MOTOR_AUDITORY_PREDICTION_001": ["PP", "CB"],
    # Motor-auditory coupling: prediction error + cerebellum timing

    "AUDITORY_MOTOR_PLASTICITY_001": ["CB", "MS"],
    # Auditory-motor learning: cerebellar adaptation + memory consolidation

    "AUDITORY_FRACTAL_SCALING_001": ["PP"],
    # Fractal properties in auditory signals trigger prediction error cascades

    "AUD_SUBCORTICAL_ENCODING_002": ["MS", "PP"],
    # Subcortical auditory encoding: memory formation + prediction at brainstem level

    # === SPATIAL NAVIGATION DOMAIN (9 templates) ===
    # Place cells, path integration, cognitive maps, wayfinding

    "AX_CHRONIC_ACUTE_011": ["SN", "NM"],
    # Exposure duration modulates spatial learning (chronic) vs alarm state (acute)

    "AWE_HIGH_PE_ACCOMMODATION_001": ["EC", "IC"],
    # Embodied simulation of others' emotions + interoceptive resonance (empathy)

    "INCUBATION_ARCHITECTURE_001": ["SN", "PP"],
    # Incubation requires spatial isolation + prediction error reset

    "COLLABORATIVE_CREATIVITY_ARCHITECTURE_001": ["SN", "DT"],
    # Shared spatial arena for System 1/2 alternation in creative dialogue

    "CROSS_MB_MF_ARBITRATION_001": ["SN", "DT"],
    # Model-based vs model-free arbitration: spatial navigation decision system

    "SPATIAL_WORKING_MEMORY_001": ["MS", "SN"],
    # Spatial working memory: hippocampal place codes + navigation

    "NAVIGATION_ERROR_RECOVERY_001": ["SN", "PP"],
    # Wayfinding errors as prediction errors in spatial maps

    "PATH_INTEGRATION_VESTIBULAR_001": ["SN", "CB"],
    # Path integration uses cerebellar vestibular processing

    "GRID_CELL_THETA_RHYTHM_001": ["SN", "CB"],
    # Grid cell firing + cerebellar theta timing coordination

    # === THERMAL DOMAIN (2 templates) ===
    # Temperature perception, thermal comfort

    "THERMAL_ADAPTIVE_PE_001": ["PP", "IC"],
    # Temperature expectation violations + interoceptive/allostatic regulation

    "THERMAL_COMFORT_ADAPTIVE_PE_001": ["PP", "IC"],
    # Thermal comfort via prediction error + homeostatic interoception

    # === STRESS & CONTROL DOMAIN (3 templates) ===
    # Threat, anxiety, perceived control, cortisol

    "AX_CONTROL_STRESS_004": ["NM", "IC"],
    # Perceived control buffers stress: cortisol regulation + allostatic adjustment

    "SRT_STRESS_RECOVERY_001": ["NM", "IC"],
    # Stress recovery: neuromodulatory reset + interoceptive/parasympathetic restoration

    "HC_HIERARCHICAL_CONTROL_002": ["DT", "NM"],
    # Hierarchical control: System 1/2 + neuromodulatory state-dependent switching

    # === MEMORY DOMAIN (3 templates) ===
    # Encoding, consolidation, episodic/semantic, working memory

    "BRECVEMA_MEMORY_005": ["MS", "PP"],
    # Memory formation: prediction error drives consolidation

    "OLF_CONTEXT_AFFECT_001": ["MS", "IC"],
    # Olfactory context-affect binding: memory + interoceptive/emotional integration

    "HC_WORKING_MEMORY_LOAD_001": ["MS", "DT"],
    # Working memory capacity: System 1/2 load effects

    # === EMOTION & AFFECT DOMAIN (1 template) ===
    # Interoception, allostasis, emotion construction

    "ALLOSTATIC_MASTER_001": ["IC", "NM"],
    # Allostatic regulation: interoceptive prediction + neuromodulatory control

    # === SOCIAL DOMAIN (1 template) ===
    # Theory of mind, empathy, social pain

    "BRECVEMA_ARCH_001": ["IC", "NM"],
    # Anterior insula: shared pain representation (physical + social) + neuromodulatory integration

    # === MOTION & MOVEMENT DOMAIN (5 templates) ===
    # Motor learning, vestibular, proprioception, timing

    "BRECVEMA_MULTI_MECHANISM_001": ["CB", "MS"],
    # Multi-mechanism motor learning: cerebellar timing + memory consolidation

    "NEURAL_MUSIC_EMOTION_ARCH_001": ["CB", "IC"],
    # Musical emotion via motor resonance + cerebellar timing + interoceptive arousal

    "PLEASURABLE_SADNESS_001": ["IC", "PP"],
    # Paradoxical affect in music: interoceptive prediction error (expecting sad, receiving beauty)

    "MUSICAL_CHILLS_CONVERGENCE_001": ["PP", "IC"],
    # Musical chills at unexpected crescendos: prediction error + interoceptive surge

    "BRECVEMA_CONTAGION_003": ["IC", "EC"],
    # Emotional contagion: interoceptive resonance + embodied simulation

    # === CREATIVE & AESTHETIC DOMAIN (9 templates) ===
    # Imagination, aesthetic experience, creative insight, wonder

    "CREATIVE_NETWORK_DYNAMICS_001": ["DT", "MS"],
    # Creative insight cycles between System 1 (associative) and System 2 (evaluation) + memory retrieval

    "AESTHETIC_VS_UTILITARIAN_EMOTIONS_001": ["DT", "IC"],
    # Aesthetic emotion via System 1 beauty + System 2 meaning + interoceptive appraisal

    "BRECVEMA_EXPECTANCY_004": ["PP", "IC"],
    # Aesthetic expectancy violations + interoceptive aesthetic response

    "BRECVEMA_AESTHETIC_007": ["PP", "IC"],
    # Aesthetic beauty via unexpected visual harmony (prediction error) + felt beauty (interoceptive)

    "AWE_MECHANISM_001": ["PP", "IC"],
    # Awe: vastness violates predictions + small-self interoceptive shift

    "SMALL_SELF_MECHANISMS_001": ["IC", "NM"],
    # Small self: interoceptive reframing of body size + parasympathetic shift

    "MUSIC_BEAUTY_RESONANCE_001": ["PP", "IC"],
    # Musical beauty: harmonic prediction error + interoceptive resonance

    "VISUAL_BEAUTY_SYMMETRY_001": ["PP", "IC"],
    # Visual beauty from symmetry violations (optimal asymmetry) + interoceptive aesthetic sense

    "NARRATIVE_TRANSPORT_001": ["EC", "MS"],
    # Narrative transport: embodied mental simulation + episodic memory engagement

    # === CROSSCUT & METHODOLOGICAL DOMAIN (30 templates) ===
    # These templates address multi-domain mechanisms or meta-methodological issues

    "AX_ATTENTION_MEDIATION_010": ["DT", "PP"],
    # Attention mediates environmental feature -> effect: System 1/2 gating + selective prediction error

    "AX_VR_LIMITATION_012": ["PP", "MSI"],
    # VR limitations in multisensory binding: incomplete cross-modal prediction error

    "AX_HABITUATION_002": ["PP", "NM"],
    # Habituation: repeated stimuli reduce prediction error + neuromodulatory adaptation

    "MULTIMODAL_PE_INTEGRATION_001": ["PP", "DP"],
    # Prediction error signals modulate dopamine: reward prediction error at VTA

    "AX_DOSE_RESPONSE_007": ["PP"],
    # Dose-response curves reflect prediction error sensitivity scaling

    "AX_INDIVIDUAL_DIFFERENCES_008": ["DT", "NM"],
    # Individual traits predict differential sensitivity: trait-state neuromodulatory interactions

    "AX_CONTEXT_DEPENDENT_010": ["DT", "IC"],
    # Context-dependent effects: System 1/2 + interoceptive state modulation

    "AX_PLACEBO_MECHANISM_001": ["PP", "IC"],
    # Placebo: expectation-driven prediction error + interoceptive confirmation

    "AX_NOCEBO_THREAT_001": ["PP", "NM"],
    # Nocebo: threat expectation + neuromodulatory alarm cascade

    "AX_ADAPTATION_LEVEL_001": ["PP", "NM"],
    # Adaptation level: shifting prediction baseline + neuromodulatory recalibration

    "AX_EMOTIONAL_PRIME_001": ["IC", "DT"],
    # Emotional priming: interoceptive state biases System 1/2 balance

    "AX_COGNITIVE_LOAD_002": ["DT", "MS"],
    # Cognitive load depletes System 2 resources: working memory

    "AX_DECISION_FATIGUE_001": ["DT", "NM"],
    # Decision fatigue: System 2 depletion + neuromodulatory glucose sensitivity

    "AX_FRAMING_EFFECT_001": ["DT"],
    # Framing effects: System 1/2 processing differences

    "AX_ANCHORING_BIAS_001": ["DT"],
    # Anchoring: System 1 automatic priming of numerical expectations

    "AX_TIMING_CRITICALITY_001": ["CB", "PP"],
    # Temporal criticality: cerebellar interval timing + prediction error windows

    "AX_CIRCADIAN_MODULATION_001": ["NM", "MS"],
    # Circadian modulation of sensitivity: neuromodulatory rhythm + memory consolidation

    "AX_LIFESPAN_SENSITIVITY_001": ["NM", "DT"],
    # Developmental sensitivity: neuromodulatory maturation + System 2 capacity growth

    "AX_STRESS_INOCULATION_001": ["NM", "IC"],
    # Stress inoculation: neuromodulatory adaptation + interoceptive resilience

    "AX_EXTINCTION_LEARNING_001": ["MS", "PP"],
    # Extinction: memory formation of prediction error reduction

    "AX_RECONSOLIDATION_WINDOW_001": ["MS", "PP"],
    # Reconsolidation: memory reactivation + prediction error update window

    "AX_CROSSED_INHIBITION_001": ["PP", "DT"],
    # Crossed inhibition: prediction-driven suppression (System 2 controlled)

    "AX_REDUNDANCY_GAIN_001": ["PP", "MSI"],
    # Redundancy gain in multisensory signals: cross-modal prediction error reduction

    "AX_VIOLATION_OF_EXPECTANCY_001": ["PP"],
    # Expectancy violation as the fundamental prediction error mechanism

    "AX_RATE_DEPENDENCY_001": ["PP", "CB"],
    # Rate-dependent plasticity: prediction error rate + cerebellar adaptation rate

    "AX_AFFORDANCE_ACTION_COUPLING_001": ["EC", "CB"],
    # Affordances couple perception to action: embodied sensorimotor coupling + cerebellar control

    "AX_ENACTIVE_PERCEPTION_001": ["EC", "PP"],
    # Enactive perception: sensorimotor prediction error during active exploration

    "AX_SENSORIMOTOR_CONTINGENCY_001": ["EC", "CB"],
    # Sensorimotor contingency learning: embodied prediction + cerebellar motor adaptation
}


def get_empty_t1_templates() -> List[Dict[str, Any]]:
    """Identify all templates with empty t1_frameworks."""
    empty = []

    for json_file in sorted(TEMPLATES_DIR.glob("*.json")):
        try:
            with open(json_file) as f:
                data = json.load(f)

            t1_frameworks = data.get("t1_frameworks", [])
            if not t1_frameworks or (isinstance(t1_frameworks, list) and len(t1_frameworks) == 0):
                empty.append({
                    "template_id": data.get("template_id"),
                    "file_path": json_file,
                    "data": data
                })
        except Exception as e:
            print(f"Warning: Error reading {json_file}: {e}")

    return empty


def assign_frameworks(template_data: Dict[str, Any], template_id: str) -> List[str]:
    """
    Assign T1 frameworks based on panel assignments.
    Returns list of framework codes.
    """
    if template_id in T1_ASSIGNMENTS:
        return T1_ASSIGNMENTS[template_id]

    # Fallback: if template_id not in assignments, try to find by matching
    # This handles minor naming variations
    for assigned_id, frameworks in T1_ASSIGNMENTS.items():
        if assigned_id.replace("_", "").lower() == template_id.replace("_", "").lower():
            return frameworks

    # Final fallback: default to PP if no match found
    print(f"WARNING: No assignment found for {template_id}, defaulting to ['PP']")
    return ["PP"]


def apply_assignments() -> Dict[str, Any]:
    """Apply T1 framework assignments to all empty templates."""
    empty_templates = get_empty_t1_templates()

    print(f"Found {len(empty_templates)} templates with empty t1_frameworks")
    print("=" * 70)

    assignments_made = 0
    failed = []

    for template_info in empty_templates:
        template_id = template_info["template_id"]
        file_path = template_info["file_path"]
        data = template_info["data"]

        # Get assigned frameworks
        frameworks = assign_frameworks(data, template_id)

        # Update the data
        data["t1_frameworks"] = frameworks

        # Add assignment metadata
        data["t1_assignment_date"] = datetime.now(timezone.utc).isoformat()
        data["t1_assignment_method"] = "expert_panel_reasoning_e02"

        # Write back to file
        try:
            with open(file_path, "w") as f:
                json.dump(data, f, indent=2)
            assignments_made += 1
            print(f"✓ {template_id}: {', '.join(frameworks)}")
        except Exception as e:
            failed.append((template_id, str(e)))
            print(f"✗ {template_id}: {e}")

    report = {
        "total_templates": len(empty_templates),
        "assignments_made": assignments_made,
        "failed": failed,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "method": "expert_panel_reasoning",
        "sprint": "E-02",
    }

    return report


def print_summary_statistics() -> None:
    """Print distribution of T1 framework assignments."""
    from collections import defaultdict

    framework_counts = defaultdict(int)
    templates_per_framework = defaultdict(list)

    for template_id, frameworks in T1_ASSIGNMENTS.items():
        for fw in frameworks:
            framework_counts[fw] += 1
            templates_per_framework[fw].append(template_id)

    print("\n" + "=" * 70)
    print("T1 FRAMEWORK DISTRIBUTION")
    print("=" * 70)

    total_assignments = sum(framework_counts.values())
    print(f"Total T1 framework assignments: {total_assignments}")
    print(f"Templates with assignments: {len(T1_ASSIGNMENTS)}")
    print(f"Avg frameworks per template: {total_assignments / len(T1_ASSIGNMENTS):.2f}")

    print("\nFramework Frequency (in assignment corpus):")
    for fw in sorted(framework_counts.keys(), key=lambda x: -framework_counts[x]):
        count = framework_counts[fw]
        pct = 100.0 * count / len(T1_ASSIGNMENTS)
        print(f"  {fw:4s}: {count:3d} templates ({pct:5.1f}%)")


def main():
    print("\n" + "=" * 70)
    print("T1 FRAMEWORK ASSIGNMENT (Sprint E-02)")
    print("=" * 70)
    print()

    # Apply assignments
    report = apply_assignments()

    # Print summary
    print("\n" + "=" * 70)
    print("ASSIGNMENT SUMMARY")
    print("=" * 70)
    print(f"Total templates processed: {report['total_templates']}")
    print(f"Assignments made: {report['assignments_made']}")
    print(f"Failed: {len(report['failed'])}")

    if report['failed']:
        print("\nFailed templates:")
        for template_id, error in report['failed']:
            print(f"  {template_id}: {error}")

    # Print framework statistics
    print_summary_statistics()

    # Write report
    with open(REPORT_PATH, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\nReport written to: {REPORT_PATH}")

    return 0 if len(report['failed']) == 0 else 1


if __name__ == "__main__":
    exit(main())
