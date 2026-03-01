#!/usr/bin/env python3
"""
Integrated CMR Prediction Pipeline
====================================

Composes three subsystems into a single prediction pipeline that generates
CONCRETE, INSTANCE-LEVEL predictions situated in specific activity-space
contexts with lighting × time × task interactions:

  1. Prediction Discovery Engine     → type-level prediction candidates
  2. Instance Library Builder        → concrete instances for each typed slot
  3. Ambience-Activity Priors        → contextual fit, interactions, anomalies
  4. Architectural Typology Priors   → space types, conditional probs, cross-domain dependencies

The output is a ranked set of SITUATED PREDICTIONS of the form:

  "In a [SPACE_TYPE] during [TIME_OF_DAY], with [INSTANCE_A] (causal attr = X)
   and [INSTANCE_B] (causal attr = Y), the CMR predicts [OUTCOME]
   via [MECHANISM_CHAIN]. Informativeness = Z."

This is the operationalization of Kirsh (2026) Section 9: predicting from
typed relational graphs instantiated with concrete objects and situated in
realistic (or anomalous) environmental contexts.

Usage:
    python integrated_prediction_pipeline.py --run
    python integrated_prediction_pipeline.py --run --json --output predictions.json
    python integrated_prediction_pipeline.py --run --top 50

Author: David Kirsh & Claude Opus 4.6
Date:   2026-02-24
"""

import json
import sys
import os
import argparse
from dataclasses import dataclass, field, asdict
from typing import Optional
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# ─── Import subsystems ────────────────────────────────────────

# Add scripts directory to path
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from prediction_discovery_engine import (
    load_all_templates, discover_shared_nodes, generate_single_template_predictions,
    generate_composition_predictions, generate_cross_modal_interference_predictions,
    TemplateGraph, Prediction, MechanismNode, classify_modality, classify_type,
    score_informativeness, informativeness_label
)
from instance_library_builder import (
    build_library as build_instance_library, Instance, SlotType, InstanceLibrary,
    _classify_slot_type, _classify_modality_from_text
)
from ambience_activity_priors import (
    ACTIVITY_PROFILES, TIME_OF_DAY_MODIFIERS, FEATURE_COOCCURRENCE,
    compute_lighting_task_fit, compute_noise_activity_fit,
    detect_anomalous_combinations, AmbientProfile
)
from architectural_typology_priors import (
    SPACE_TYPES, CROSS_DOMAIN_CONDITIONALS,
    get_feature_profile, compute_space_similarity,
    find_anomalous_feature_in_space, generate_activity_space_matrix,
    SpaceType
)


# ─── Situated Prediction ──────────────────────────────────────

@dataclass
class SituatedPrediction:
    """A concrete, instance-level prediction situated in a space-activity context."""
    prediction_id: str
    # From the type-level prediction
    base_prediction_id: str
    prediction_type: str          # single_slot, composition, cross_modal, situated_interaction
    interaction_type: str         # enhancement, catalysis, etc.
    # Instance-level content
    instances: list = field(default_factory=list)   # list of {name, causal_attribute, value, slot_type}
    instance_names: list = field(default_factory=list)
    # Spatial-temporal context
    activity_type: str = ""
    time_of_day: str = ""
    space_description: str = ""
    # Lighting × task interaction
    lighting_fit: float = 0.0
    lighting_predictions: list = field(default_factory=list)
    lighting_interactions: list = field(default_factory=list)
    # Noise × activity interaction
    noise_fit: float = 0.0
    noise_predictions: list = field(default_factory=list)
    noise_interactions: list = field(default_factory=list)
    # Co-occurrence context
    co_occurrence_anomalies: list = field(default_factory=list)
    is_anomalous_context: bool = False
    # Combined informativeness
    type_level_informativeness: float = 0.0
    contextual_informativeness: float = 0.0
    combined_informativeness: float = 0.0
    # Narrative
    narrative: str = ""
    testable_hypothesis: str = ""
    discriminating_experiment: str = ""
    modalities: list = field(default_factory=list)
    template_ids: list = field(default_factory=list)


# ─── Scenario Generator (from Architectural Typology) ────────

def generate_scenarios_from_typology() -> list:
    """
    Generate ecologically grounded scenarios from the architectural typology.

    For each space type, we generate:
      1. PROTOTYPICAL scenarios — the activity the space was designed for,
         at an appropriate time of day, with typical feature values.
         These test CMR predictions under ecologically valid conditions.
      2. MISMATCH scenarios — an activity that is ill-suited to the space,
         or the space at an inappropriate time of day.
         These are more informative because correct predictions under
         adverse conditions are stronger evidence.
    """
    scenarios = []
    TIME_SLOTS = [
        "morning_0800_1200",
        "afternoon_1200_1700",
        "late_afternoon_1700_1900",
        "evening_1900_2200",
    ]

    # Activity → best time of day mapping
    ACTIVITY_TIMES = {
        "deep_reading": ["evening_1900_2200", "afternoon_1200_1700"],
        "focused_study": ["morning_0800_1200", "afternoon_1200_1700"],
        "quiet_contemplation": ["evening_1900_2200", "late_afternoon_1700_1900"],
        "focused_computer_work": ["morning_0800_1200", "afternoon_1200_1700"],
        "collaborative_work": ["morning_0800_1200", "afternoon_1200_1700"],
        "creative_brainstorming": ["afternoon_1200_1700", "morning_0800_1200"],
        "painting_drawing": ["morning_0800_1200", "afternoon_1200_1700"],
        "creative_work": ["morning_0800_1200", "afternoon_1200_1700"],
        "meditation_quiet_rest": ["evening_1900_2200", "late_afternoon_1700_1900"],
        "rest_recovery": ["morning_0800_1200", "afternoon_1200_1700"],
        "nature_walk_garden": ["late_afternoon_1700_1900", "morning_0800_1200"],
        "casual_socializing": ["evening_1900_2200", "afternoon_1200_1700"],
        "formal_dining": ["evening_1900_2200"],
        "intimate_conversation": ["evening_1900_2200"],
        "classroom_lecture": ["morning_0800_1200", "afternoon_1200_1700"],
        "browsing": ["afternoon_1200_1700", "morning_0800_1200"],
        "sleep": ["evening_1900_2200"],
        "aesthetic_contemplation": ["afternoon_1200_1700", "morning_0800_1200"],
        "fabrication": ["morning_0800_1200", "afternoon_1200_1700"],
    }

    for sid, st in SPACE_TYPES.items():
        # Midpoint of typical ranges
        mid_lux = (st.illuminance_lux[0] + st.illuminance_lux[1]) / 2
        mid_cct = (st.cct_kelvin[0] + st.cct_kelvin[1]) / 2
        mid_noise = (st.background_noise_dB[0] + st.background_noise_dB[1]) / 2

        # Derive feature tags from the space profile
        feature_tags = [sid]
        if st.dominant_material_warmth == "warm":
            feature_tags.append("warm_materials")
        if st.nature_view_probability > 0.5:
            feature_tags.append("nature_view_present")
        if any(p > 0.5 for p in st.biophilic_elements.values()):
            feature_tags.append("biophilic_elements_present")

        # Natural sound fraction: estimate from biophilic elements
        natural_sound = 0.0
        if "birdsong" in st.biophilic_elements:
            natural_sound = max(natural_sound, st.biophilic_elements["birdsong"] * 0.8)
        if "water_feature" in st.biophilic_elements:
            natural_sound = max(natural_sound, st.biophilic_elements["water_feature"] * 0.5)

        # ── Prototypical scenario (first activity, best time) ──
        for activity in st.prototypical_activities[:2]:
            best_times = ACTIVITY_TIMES.get(activity, ["afternoon_1200_1700"])
            time = best_times[0]

            scenarios.append({
                "activity": activity,
                "time": time,
                "space": f"{st.name} (prototypical for {activity})",
                "space_type_id": sid,
                "features": feature_tags,
                "lighting": {"illuminance_lux": mid_lux, "cct_kelvin": mid_cct},
                "noise": {
                    "noise_dB": mid_noise,
                    "speech_intelligibility": st.speech_intelligibility_target,
                    "natural_sound_fraction": natural_sound,
                },
                "is_mismatch": False,
                "pad_target": {"P": st.pad_pleasure, "A": st.pad_arousal, "D": st.pad_dominance},
            })

    # ── Mismatch scenarios: activity in wrong space type ──
    MISMATCH_PAIRS = [
        # (activity, wrong_space_id, why)
        ("deep_reading", "open_plan_office", "noisy, socially dense, cool lighting"),
        ("deep_reading", "cafe", "noisy babble, warm but distracting"),
        ("meditation_quiet_rest", "open_plan_office", "speech noise, high arousal, no privacy"),
        ("meditation_quiet_rest", "retail_store", "bright, noisy, high social density"),
        ("creative_brainstorming", "library_reading_room", "quiet, low arousal, solitary"),
        ("creative_brainstorming", "hospital_patient_room", "clinical, low agency, restricted"),
        ("painting_drawing", "conference_room", "no natural light, cool CCT, carpeted"),
        ("focused_computer_work", "spa_meditation", "too dim, too warm, no task lighting"),
        ("formal_dining", "workshop_makerspace", "industrial, noisy, bright cool light"),
        ("sleep", "open_plan_office", "bright, noisy, socially exposed"),
        ("aesthetic_contemplation", "workshop_makerspace", "noisy, bright, industrial"),
        ("classroom_lecture", "spa_meditation", "too dim, too quiet, too private"),
    ]

    for activity, wrong_sid, reason in MISMATCH_PAIRS:
        st = SPACE_TYPES[wrong_sid]
        mid_lux = (st.illuminance_lux[0] + st.illuminance_lux[1]) / 2
        mid_cct = (st.cct_kelvin[0] + st.cct_kelvin[1]) / 2
        mid_noise = (st.background_noise_dB[0] + st.background_noise_dB[1]) / 2

        feature_tags = [wrong_sid]

        natural_sound = 0.0
        if "birdsong" in st.biophilic_elements:
            natural_sound = st.biophilic_elements["birdsong"] * 0.8
        if "water_feature" in st.biophilic_elements:
            natural_sound = max(natural_sound, st.biophilic_elements["water_feature"] * 0.5)

        # Pick a time that makes the mismatch worse
        bad_times = {
            "deep_reading": "evening_1900_2200",
            "meditation_quiet_rest": "afternoon_1200_1700",
            "creative_brainstorming": "morning_0800_1200",
            "sleep": "afternoon_1200_1700",
        }
        time = bad_times.get(activity, "afternoon_1200_1700")

        scenarios.append({
            "activity": activity,
            "time": time,
            "space": f"{st.name} — MISMATCH for {activity} ({reason})",
            "space_type_id": wrong_sid,
            "features": feature_tags,
            "lighting": {"illuminance_lux": mid_lux, "cct_kelvin": mid_cct},
            "noise": {
                "noise_dB": mid_noise,
                "speech_intelligibility": st.speech_intelligibility_target,
                "natural_sound_fraction": natural_sound,
            },
            "is_mismatch": True,
            "mismatch_reason": reason,
            "pad_target": {"P": st.pad_pleasure, "A": st.pad_arousal, "D": st.pad_dominance},
        })

    return scenarios


CANONICAL_SCENARIOS = generate_scenarios_from_typology()


# ─── Instance Matcher ─────────────────────────────────────────

def match_instances_to_prediction(
    prediction: Prediction,
    library: InstanceLibrary,
    max_per_slot: int = 3,
    used_instance_ids: set = None,
) -> list:
    """
    For a type-level prediction, find concrete instances from the library
    that populate its mechanism chain slots.

    Uses a multi-signal scoring approach:
      1. Modality match (prediction modality → slot modality)
      2. Keyword overlap between prediction text and slot/instance names
      3. Interaction type alignment (e.g., detractors need contrast instances)
      4. Diversity bonus (prefer instances not yet used in this scenario)

    Returns a list of instance groups — each group is one possible
    instantiation of the prediction.
    """
    if used_instance_ids is None:
        used_instance_ids = set()

    needed_modalities = set(prediction.modalities)
    pred_text = f"{prediction.description} {prediction.testable_hypothesis} {prediction.discriminating_experiment}".lower()

    # Extract keywords from prediction for finer matching
    pred_keywords = set()
    for word in pred_text.split():
        w = word.strip("(),.:;\"'").lower()
        if len(w) > 3 and w not in {"with", "from", "that", "this", "have", "been", "will", "does", "more", "than", "their"}:
            pred_keywords.add(w)

    # Score each slot type for relevance
    slot_scores = []
    for slot_type in library.slot_types:
        score = 0.0

        # Primary: modality match
        if slot_type.modality in needed_modalities:
            score += 0.4
        elif slot_type.modality == "general":
            score += 0.1

        # Secondary: keyword match against slot name, causal attribute, slot_id
        slot_text = f"{slot_type.name} {slot_type.causal_attribute} {slot_type.slot_id} {slot_type.description}".lower()
        slot_words = set(w for w in slot_text.split() if len(w) > 3)
        keyword_overlap = len(pred_keywords & slot_words)
        score += 0.15 * min(keyword_overlap, 4)

        # Tertiary: check if any instance names appear in prediction text
        for inst in slot_type.instances[:10]:
            inst_words = set(w.lower() for w in inst.name.split() if len(w) > 3)
            if inst_words & pred_keywords:
                score += 0.2
                break

        # Bonus for effect-size-backed instances when prediction is discriminating
        if prediction.prediction_type in ("single_slot",) and prediction.discriminating_power > 0.7:
            has_effect_sizes = any(i.effect_size is not None for i in slot_type.instances[:10])
            if has_effect_sizes:
                score += 0.15

        if score > 0.1:
            slot_scores.append((slot_type, score))

    slot_scores.sort(key=lambda x: -x[1])

    # Select instances from top-scoring slots
    instance_groups = []
    for slot_type, slot_score in slot_scores[:4]:
        instances = slot_type.instances
        if not instances:
            continue

        # Score each instance within the slot
        inst_scores = []
        for inst in instances:
            iscore = 0.0
            # Validity
            iscore += {"HIGH": 0.4, "VALID": 0.3, "PARTIAL": 0.15, "LOW": 0.05}.get(inst.validity, 0.1)
            # Has numeric value (more useful for predictions)
            if inst.causal_value_numeric is not None:
                iscore += 0.2
            # Has effect size
            if inst.effect_size is not None:
                iscore += 0.25
            # Keyword match with prediction text
            inst_words = set(w.lower() for w in inst.name.split() if len(w) > 3)
            if inst_words & pred_keywords:
                iscore += 0.3
            # Diversity bonus: prefer unused instances
            if inst.instance_id not in used_instance_ids:
                iscore += 0.35
            # Prefer literature-sourced over template-parameter
            if "literature" in inst.source:
                iscore += 0.15

            inst_scores.append((inst, iscore))

        inst_scores.sort(key=lambda x: -x[1])

        # Select diverse set: optimal, boundary, contrast
        selected = []
        seen_categories = set()

        for inst, iscore in inst_scores:
            if len(selected) >= max_per_slot:
                break
            # Category diversity: don't pick two instances from same category
            if inst.category in seen_categories and len(selected) > 0:
                continue
            selected.append(inst)
            seen_categories.add(inst.category)
            used_instance_ids.add(inst.instance_id)

        if not selected:
            continue

        instance_groups.append({
            "slot_type": slot_type.slot_id,
            "slot_name": slot_type.name,
            "causal_attribute": slot_type.causal_attribute,
            "optimal_range": slot_type.optimal_range,
            "instances": [
                {
                    "name": inst.name,
                    "causal_attribute": inst.causal_attribute,
                    "causal_value": inst.causal_value,
                    "causal_value_numeric": inst.causal_value_numeric,
                    "causal_unit": inst.causal_unit,
                    "validity": inst.validity,
                    "source": inst.source,
                    "effect_size": inst.effect_size,
                    "context": inst.context,
                }
                for inst in selected
            ],
        })

    return instance_groups


# ─── Situated Prediction Generator ────────────────────────────

def generate_situated_predictions(
    type_predictions: list,
    library: InstanceLibrary,
    scenario: dict,
    max_predictions: int = 20,
) -> list:
    """
    Take type-level predictions and ground them in a specific scenario
    with concrete instances and contextual interactions.
    """
    situated = []

    activity = scenario["activity"]
    time = scenario["time"]
    space = scenario["space"]
    features = scenario.get("features", [])
    lighting_params = scenario.get("lighting", {})
    noise_params = scenario.get("noise", {})

    # Compute contextual fits
    lighting_result = compute_lighting_task_fit(
        illuminance_lux=lighting_params.get("illuminance_lux", 300),
        cct_kelvin=lighting_params.get("cct_kelvin", 4000),
        time_of_day=time,
        activity_type=activity,
    )

    noise_result = compute_noise_activity_fit(
        noise_dB=noise_params.get("noise_dB", 45),
        speech_intelligibility=noise_params.get("speech_intelligibility", 0.2),
        natural_sound_fraction=noise_params.get("natural_sound_fraction", 0.0),
        activity_type=activity,
    )

    anomalies = detect_anomalous_combinations(features)
    is_anomalous = len(anomalies) > 0

    # Context informativeness: anomalous contexts are more informative
    context_informativeness_bonus = 0.0
    if is_anomalous:
        context_informativeness_bonus = 0.15
    # Low fit scores also boost informativeness (testing under adverse conditions)
    if lighting_result["fit_score"] < 0.4:
        context_informativeness_bonus += 0.10
    if noise_result["fit_score"] < 0.4:
        context_informativeness_bonus += 0.10
    # Circadian mismatches are especially informative
    if "HARMFUL" in lighting_result.get("circadian_alignment", ""):
        context_informativeness_bonus += 0.15

    # Generate situated predictions for the most informative type-level ones
    sorted_preds = sorted(type_predictions, key=lambda p: p.informativeness, reverse=True)

    # Track used instances across the scenario for diversity
    scenario_used_ids = set()

    for pred in sorted_preds[:max_predictions]:
        # Match instances (with diversity tracking)
        instance_groups = match_instances_to_prediction(pred, library, used_instance_ids=scenario_used_ids)

        # Build narrative
        instance_names = []
        instance_details = []
        for group in instance_groups:
            for inst in group["instances"][:1]:  # lead instance per group
                instance_names.append(inst["name"])
                val_str = f"{inst['causal_attribute']}={inst['causal_value']}"
                instance_details.append({
                    "name": inst["name"],
                    "causal_attribute": inst["causal_attribute"],
                    "value": inst["causal_value"],
                    "slot_type": group["slot_type"],
                })

        # Build narrative sentence
        narrative_parts = [f"In a {space}"]
        time_label = time.replace("_", " ").replace("0", "").strip()
        narrative_parts.append(f"during {time_label}")
        if instance_names:
            narrative_parts.append(f"with {', '.join(instance_names[:3])}")
        narrative_parts.append(f"the CMR predicts: {pred.description[:200]}")

        if lighting_result.get("predictions"):
            narrative_parts.append(f"[Lighting interaction: {lighting_result['predictions'][0][:100]}]")
        if noise_result.get("predictions"):
            narrative_parts.append(f"[Acoustic interaction: {noise_result['predictions'][0][:100]}]")

        narrative = ". ".join(narrative_parts)

        # Combined informativeness
        type_info = pred.informativeness
        contextual_info = min(1.0, 0.5 + context_informativeness_bonus)
        # Geometric mean of type-level and contextual
        combined = (type_info * contextual_info) ** 0.5

        sp = SituatedPrediction(
            prediction_id=f"SIT_{activity}_{time}_{pred.prediction_id}",
            base_prediction_id=pred.prediction_id,
            prediction_type=pred.prediction_type,
            interaction_type=pred.interaction_type,
            instances=instance_details,
            instance_names=instance_names[:5],
            activity_type=activity,
            time_of_day=time,
            space_description=space,
            lighting_fit=lighting_result["fit_score"],
            lighting_predictions=lighting_result.get("predictions", []),
            lighting_interactions=lighting_result.get("interactions", []),
            noise_fit=noise_result["fit_score"],
            noise_predictions=noise_result.get("predictions", []),
            noise_interactions=noise_result.get("interactions", []),
            co_occurrence_anomalies=[
                f"{a['anchor']} + {a['co_feature']} ({a['classification']})"
                for a in anomalies
            ],
            is_anomalous_context=is_anomalous,
            type_level_informativeness=type_info,
            contextual_informativeness=contextual_info,
            combined_informativeness=combined,
            narrative=narrative,
            testable_hypothesis=pred.testable_hypothesis,
            discriminating_experiment=pred.discriminating_experiment,
            modalities=pred.modalities,
            template_ids=pred.templates,
        )
        situated.append(sp)

    return situated


# ─── Interior Typology Co-occurrence Extractor ────────────────

def extract_interior_conditional_probs() -> dict:
    """
    Extract P(feature_B | space_type) and P(feature_B | feature_A)
    from the architectural typology model.

    This produces the conditional probability matrices that encode:
    "rooms designed for different activities have non-random architectural
    signatures, and those signatures constrain which predictions are
    ecologically valid."

    Sources: architectural_typology_priors.py (16 space types, 45 cross-domain
    conditionals) + ambience_activity_priors.py (11 activity profiles).
    """
    results = {
        "p_feature_given_space": {},
        "p_feature_given_anchor": {},
        "p_activity_given_space": {},
        "cross_domain_conditionals": {},
        "high_conditional_pairs": [],
        "low_conditional_pairs": [],
        "space_type_count": len(SPACE_TYPES),
        "cross_domain_count": len(CROSS_DOMAIN_CONDITIONALS),
    }

    # ── P(feature | space_type) from architectural typology ──
    for sid, st in SPACE_TYPES.items():
        profile = get_feature_profile(sid)
        results["p_feature_given_space"][sid] = {
            "name": st.name,
            "activities": st.prototypical_activities,
            "features": {k: v for k, v in profile.items() if v > 0},
        }

    # ── P(feature_B | feature_A) from cross-domain conditionals ──
    for (fa, fb), prob in CROSS_DOMAIN_CONDITIONALS.items():
        key = f"{fa} → {fb}"
        results["cross_domain_conditionals"][key] = prob
        if prob >= 0.65:
            results["high_conditional_pairs"].append({
                "anchor": fa,
                "feature": fb,
                "probability": prob,
                "interpretation": f"P({fb} | {fa}) = {prob:.2f} — strong design regularity",
            })
        elif prob <= 0.15:
            results["low_conditional_pairs"].append({
                "anchor": fa,
                "feature": fb,
                "probability": prob,
                "interpretation": f"P({fb} | {fa}) = {prob:.2f} — rare co-occurrence, HIGH informativeness",
            })

    # ── P(activity | space_type) from architectural typology ──
    for sid, st in SPACE_TYPES.items():
        results["p_activity_given_space"][sid] = st.prototypical_activities

    # ── Add ambience model priors ──
    for anchor, cooccurrences in FEATURE_COOCCURRENCE.items():
        results["p_feature_given_anchor"][anchor] = {}
        for feature, prob in cooccurrences.items():
            results["p_feature_given_anchor"][anchor][feature] = prob
            if prob >= 0.65:
                results["high_conditional_pairs"].append({
                    "anchor": anchor,
                    "feature": feature,
                    "probability": prob,
                    "interpretation": f"P({feature} | {anchor}) = {prob:.2f} — ambience regularity",
                })
            elif prob <= 0.15:
                results["low_conditional_pairs"].append({
                    "anchor": anchor,
                    "feature": feature,
                    "probability": prob,
                    "interpretation": f"P({feature} | {anchor}) = {prob:.2f} — rare, HIGH informativeness",
                })

    results["high_conditional_pairs"].sort(key=lambda x: -x["probability"])
    results["low_conditional_pairs"].sort(key=lambda x: x["probability"])

    return results


# ─── Report Generator ─────────────────────────────────────────

def generate_integrated_report(
    all_situated: list,
    cond_probs: dict,
    library: InstanceLibrary,
    n_type_predictions: int,
) -> str:
    """Generate the integrated human-readable report."""
    lines = []
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")

    lines.append("=" * 80)
    lines.append("CMR INTEGRATED PREDICTION PIPELINE — SITUATED PREDICTIONS")
    lines.append(f"Generated: {ts}")
    lines.append("=" * 80)
    lines.append("")

    # ── Summary ──
    lines.append("SUMMARY")
    lines.append("-" * 50)
    lines.append(f"  Type-level predictions:     {n_type_predictions}")
    lines.append(f"  Situated predictions:       {len(all_situated)}")
    lines.append(f"  Instance library:           {library.total_instances} instances across {len(library.slot_types)} slot types")
    lines.append(f"  Scenarios evaluated:        {len(CANONICAL_SCENARIOS)}")
    lines.append(f"  Conditional prob. pairs:    {len(cond_probs['high_conditional_pairs'])} high / {len(cond_probs['low_conditional_pairs'])} low")
    lines.append("")

    # Count by context
    activity_counts = defaultdict(int)
    anomalous_count = 0
    for sp in all_situated:
        activity_counts[sp.activity_type] += 1
        if sp.is_anomalous_context:
            anomalous_count += 1

    lines.append("  By activity context:")
    for act, count in sorted(activity_counts.items(), key=lambda x: -x[1]):
        lines.append(f"    {act:40s} {count:4d}")
    lines.append(f"  Anomalous contexts:         {anomalous_count}")
    lines.append("")

    # ── Top 30 situated predictions ──
    sorted_situated = sorted(all_situated, key=lambda s: s.combined_informativeness, reverse=True)

    lines.append("=" * 80)
    lines.append("TOP 30 MOST INFORMATIVE SITUATED PREDICTIONS")
    lines.append("=" * 80)
    lines.append("")

    for i, sp in enumerate(sorted_situated[:30], 1):
        lines.append(f"  [{i:2d}] {sp.prediction_id}")
        lines.append(f"       Type:                {sp.prediction_type} / {sp.interaction_type}")
        lines.append(f"       Context:             {sp.space_description}")
        lines.append(f"       Activity:            {sp.activity_type} @ {sp.time_of_day}")
        lines.append(f"       Instances:           {', '.join(sp.instance_names[:3])}")
        lines.append(f"       Combined inform.:    {sp.combined_informativeness:.3f}")
        lines.append(f"         Type-level:        {sp.type_level_informativeness:.3f}")
        lines.append(f"         Contextual:        {sp.contextual_informativeness:.3f}")
        lines.append(f"       Lighting fit:        {sp.lighting_fit:.3f}")
        lines.append(f"       Noise fit:           {sp.noise_fit:.3f}")
        if sp.is_anomalous_context:
            lines.append(f"       ANOMALOUS CONTEXT:   {'; '.join(sp.co_occurrence_anomalies[:2])}")
        if sp.lighting_predictions:
            lines.append(f"       Light interaction:    {sp.lighting_predictions[0][:100]}")
        if sp.noise_predictions:
            lines.append(f"       Noise interaction:    {sp.noise_predictions[0][:100]}")
        lines.append(f"       Narrative:            {sp.narrative[:200]}")
        lines.append("")

    # ── Scenarios ranked by informativeness ──
    lines.append("=" * 80)
    lines.append("SCENARIO INFORMATIVENESS RANKING")
    lines.append("=" * 80)
    lines.append("")

    scenario_info = defaultdict(list)
    for sp in all_situated:
        key = f"{sp.activity_type} @ {sp.time_of_day} in {sp.space_description[:50]}"
        scenario_info[key].append(sp.combined_informativeness)

    scenario_ranks = []
    for key, scores in scenario_info.items():
        avg = sum(scores) / len(scores) if scores else 0
        scenario_ranks.append((key, avg, len(scores)))
    scenario_ranks.sort(key=lambda x: -x[1])

    for rank, (key, avg, count) in enumerate(scenario_ranks, 1):
        label = "ANOMALOUS" if "MISMATCH" in key else "TYPICAL"
        lines.append(f"  [{rank:2d}] {key}")
        lines.append(f"       Avg informativeness: {avg:.3f}  ({count} predictions) [{label}]")
        lines.append("")

    # ── Conditional probability summary ──
    lines.append("=" * 80)
    lines.append("INTERIOR TYPOLOGY CONDITIONAL PROBABILITIES")
    lines.append("=" * 80)
    lines.append("")

    lines.append("  HIGH CO-OCCURRENCE (P > 0.70) — expected, lower informativeness:")
    for pair in cond_probs["high_conditional_pairs"][:10]:
        lines.append(f"    P({pair['feature'][:35]:35s} | {pair['anchor'][:25]:25s}) = {pair['probability']:.2f}")
    lines.append("")

    lines.append("  LOW CO-OCCURRENCE (P < 0.15) — rare, HIGHER informativeness:")
    for pair in cond_probs["low_conditional_pairs"][:10]:
        lines.append(f"    P({pair['feature'][:35]:35s} | {pair['anchor'][:25]:25s}) = {pair['probability']:.2f}")
    lines.append("")

    lines.append("  ACTIVITY-SPACE PROTOTYPES:")
    for space, activities in cond_probs["p_activity_given_space"].items():
        lines.append(f"    {space:35s} → {', '.join(activities)}")
    lines.append("")

    # ── Instance diversity summary ──
    lines.append("=" * 80)
    lines.append("INSTANCE LIBRARY UTILIZATION")
    lines.append("=" * 80)
    lines.append("")

    used_instances = set()
    for sp in all_situated:
        for inst in sp.instances:
            used_instances.add(inst.get("name", ""))

    lines.append(f"  Instances referenced:       {len(used_instances)} / {library.total_instances}")
    lines.append(f"  Coverage:                   {len(used_instances) / max(1, library.total_instances) * 100:.1f}%")
    lines.append("")

    # Most-referenced instances
    inst_counts = defaultdict(int)
    for sp in all_situated:
        for inst in sp.instances:
            inst_counts[inst.get("name", "")] += 1

    lines.append("  Most-referenced instances:")
    for name, count in sorted(inst_counts.items(), key=lambda x: -x[1])[:15]:
        if name:
            lines.append(f"    {name[:50]:50s} {count:3d} references")
    lines.append("")

    return "\n".join(lines)


# ─── Main Pipeline ────────────────────────────────────────────

def run_integrated_pipeline(
    templates_dir: str,
    data_dir: str,
    output_file: str = None,
    json_output: bool = False,
    top_n: int = 30,
) -> dict:
    """Run the full integrated prediction pipeline."""

    print("=" * 70, file=sys.stderr)
    print("CMR INTEGRATED PREDICTION PIPELINE", file=sys.stderr)
    print("=" * 70, file=sys.stderr)

    # ── Step 1: Build type-level predictions ──
    print("\n[1/6] Loading templates and generating type-level predictions...", file=sys.stderr)
    graphs = load_all_templates(templates_dir)
    print(f"       Loaded {len(graphs)} calibrated templates", file=sys.stderr)

    shared_nodes = discover_shared_nodes(graphs, min_similarity=0.40)
    print(f"       Found {len(shared_nodes)} composition candidates", file=sys.stderr)

    # Generate all type-level predictions
    all_type_preds = []
    for g in graphs:
        all_type_preds.extend(generate_single_template_predictions(g))

    graph_map = {g.template_id: g for g in graphs}
    for sn in shared_nodes:
        if sn.template_a in graph_map and sn.template_b in graph_map:
            all_type_preds.extend(generate_composition_predictions(
                graph_map[sn.template_a], graph_map[sn.template_b], sn))

    all_type_preds.extend(generate_cross_modal_interference_predictions(graphs))
    all_type_preds.sort(key=lambda p: p.informativeness, reverse=True)
    print(f"       Generated {len(all_type_preds)} type-level predictions", file=sys.stderr)

    # ── Step 2: Build instance library ──
    print("\n[2/6] Building instance library...", file=sys.stderr)
    library = build_instance_library(data_dir, templates_dir)
    print(f"       {library.total_instances} instances across {len(library.slot_types)} slot types", file=sys.stderr)

    # ── Step 3: Extract conditional probabilities ──
    print("\n[3/6] Extracting interior typology conditional probabilities...", file=sys.stderr)
    cond_probs = extract_interior_conditional_probs()
    print(f"       {len(cond_probs['high_conditional_pairs'])} high-probability pairs", file=sys.stderr)
    print(f"       {len(cond_probs['low_conditional_pairs'])} low-probability pairs (informative)", file=sys.stderr)

    # ── Step 4: Generate situated predictions for each scenario ──
    print("\n[4/6] Generating situated predictions across scenarios...", file=sys.stderr)
    all_situated = []
    for scenario in CANONICAL_SCENARIOS:
        print(f"       Scenario: {scenario['activity']} @ {scenario['time']} in {scenario['space'][:40]}...", file=sys.stderr)
        situated = generate_situated_predictions(
            all_type_preds[:200],  # top 200 type-level predictions
            library,
            scenario,
            max_predictions=20,
        )
        all_situated.extend(situated)
        print(f"         → {len(situated)} situated predictions", file=sys.stderr)

    print(f"       Total situated predictions: {len(all_situated)}", file=sys.stderr)

    # ── Step 5: Rank by combined informativeness ──
    print("\n[5/6] Ranking by combined informativeness...", file=sys.stderr)
    all_situated.sort(key=lambda s: s.combined_informativeness, reverse=True)

    # Print top 5 to stderr
    for i, sp in enumerate(all_situated[:5], 1):
        print(f"       [{i}] {sp.combined_informativeness:.3f} | {sp.activity_type} @ {sp.time_of_day}", file=sys.stderr)
        print(f"           {sp.narrative[:120]}", file=sys.stderr)

    # ── Step 6: Generate output ──
    print(f"\n[6/6] Generating output...", file=sys.stderr)

    if json_output:
        result = {
            "timestamp": datetime.now().isoformat(),
            "pipeline_version": "1.0.0",
            "type_level_predictions": len(all_type_preds),
            "situated_predictions": len(all_situated),
            "instance_library_size": library.total_instances,
            "scenarios_evaluated": len(CANONICAL_SCENARIOS),
            "conditional_probabilities": cond_probs,
            "top_predictions": [asdict(sp) for sp in all_situated[:top_n]],
        }
        json_str = json.dumps(result, indent=2, default=str)
        if output_file:
            with open(output_file, "w") as f:
                f.write(json_str)
            print(f"JSON written to: {output_file}", file=sys.stderr)
        else:
            print(json_str)
        return result

    report = generate_integrated_report(all_situated, cond_probs, library, len(all_type_preds))
    if output_file:
        with open(output_file, "w") as f:
            f.write(report)
        print(f"Report written to: {output_file}", file=sys.stderr)
    else:
        print(report)

    return {
        "type_predictions": len(all_type_preds),
        "situated_predictions": len(all_situated),
        "instances": library.total_instances,
    }


# ─── CLI ──────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="CMR Integrated Prediction Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--run", action="store_true", help="Run the full pipeline")
    parser.add_argument("--templates-dir", "-t", default=None)
    parser.add_argument("--data-dir", "-d", default=None)
    parser.add_argument("--output", "-o", default=None)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--top", type=int, default=30, help="Number of top predictions")
    parser.add_argument("--cond-probs-only", action="store_true",
        help="Only output conditional probability analysis")

    args = parser.parse_args()

    # Auto-detect directories
    base = Path("/sessions/practical-zen-darwin/mnt/REPOS/Article_Eater_PostQuinean_v1")
    data_dir = args.data_dir
    templates_dir = args.templates_dir

    if not data_dir:
        for c in ["data", str(base / "data")]:
            if os.path.isdir(c):
                data_dir = c
                break
    if not templates_dir:
        for c in ["data/templates", str(base / "data" / "templates")]:
            if os.path.isdir(c):
                templates_dir = c
                break

    if args.cond_probs_only:
        cond_probs = extract_interior_conditional_probs()
        print(json.dumps(cond_probs, indent=2, default=str))
        return

    if not args.run:
        parser.print_help()
        return

    if not data_dir or not templates_dir:
        print("ERROR: Could not find data directories.", file=sys.stderr)
        sys.exit(1)

    run_integrated_pipeline(
        templates_dir=templates_dir,
        data_dir=data_dir,
        output_file=args.output,
        json_output=args.json,
        top_n=args.top,
    )


if __name__ == "__main__":
    main()
