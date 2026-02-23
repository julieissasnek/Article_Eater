"""
Conditional Modality Stimulus Seeder
=====================================

Seeds stimulus channel beliefs that are CONDITIONAL on the mode of encounter —
how the subject actually experiences the material (wood, plants, etc.).

The key insight: wood is not a single stimulus. It is a BUNDLE of potential
sensory channels, each activating different mechanism pathways. Which channels
fire depends entirely on the encounter conditions:

    Encounter mode          → Activated channel              → Mechanism entry
    ─────────────────────────────────────────────────────────────────────────
    Can see the wood        → stimulus:wood:visual           → SRT visual_ecological_appraisal
    Can smell it            → stimulus:wood:olfactory        → SRT olfactory_ecological_appraisal
    Can touch it            → stimulus:wood:haptic           → MAT4 multisensory_biophilic_signal
    High ambient noise       → stimulus:wood:acoustic         → DT1 network_switching (reduced)
    In motion near it       → stimulus:wood:kinesthetic      → NM novelty_dopamine
    Looking at its grain    → stimulus:wood:fractal_visual   → ART biophilic_stimulus (high fidelity)

The seeder creates:
  1. Stimulus channel belief nodes (stimulus:wood:*, stimulus:plants:*)
  2. Encounter-condition → stimulus channel constraints (SUPPORTS, conditional)
  3. Stimulus channel → mechanism entry constraints

Then the question "do plants and wood share the same mechanism?" has a richer
answer: "at the VISUAL channel, yes — both trigger visual_ecological_appraisal.
At the olfactory channel, wood does (wood VOCs) but plants do (different VOCs,
different valence). At the haptic channel, wood does if touched; plants may not."

Run:
    python3 scripts/seed_modality_stimuli.py
    python3 scripts/seed_modality_stimuli.py --dry-run
    python3 scripts/seed_modality_stimuli.py --material wood
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
import uuid
from dataclasses import dataclass, field
from typing import List, Optional, Dict

sys.path.insert(0, os.getcwd())

from src.services.web_accumulator import WebAccumulator
from src.services.web_of_belief import (
    Belief, Constraint, Credence,
    EpistemicLevel, BeliefStatus,
    ConstraintType, CausalDirection,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


# =============================================================================
# DATA MODEL
# =============================================================================

@dataclass
class StimulusChannel:
    """A modality-specific stimulus channel for a material/element."""
    belief_id: str          # stimulus:wood:visual
    material: str           # wood, plants, water, stone
    modality: str           # visual, olfactory, haptic, acoustic, fractal_visual, kinesthetic
    content: str
    encounter_condition: str  # human-readable condition for this channel to be active
    credence_value: float
    credence_uncertainty: float
    tags: List[str] = field(default_factory=list)
    # Which mechanism node this channel feeds into
    mechanism_targets: List[str] = field(default_factory=list)
    # Strength of the connection to each target
    mechanism_strengths: List[float] = field(default_factory=list)


# =============================================================================
# WOOD STIMULUS CHANNELS
# =============================================================================

WOOD_CHANNELS: List[StimulusChannel] = [

    StimulusChannel(
        belief_id="stimulus:wood:visual",
        material="wood", modality="visual",
        content=(
            "Wood grain visible in the environment activates the visual biophilic stimulus "
            "pathway. The natural fractal statistics of wood grain (1/f spatial frequency "
            "profile, fractal dimension D ≈ 1.2–1.5) match the visual system's processing "
            "structure, producing soft fascination and initial ecological safety appraisal. "
            "ENCOUNTER CONDITION: subject has line-of-sight to exposed wood surface; surface "
            "grain must be visible (not painted over or obscured)."
        ),
        encounter_condition="subject can see exposed wood grain (not painted or hidden)",
        credence_value=0.82, credence_uncertainty=0.10,
        tags=["stimulus_channel", "wood", "visual", "fractal", "biophilic_stimulus",
              "line_of_sight", "encounter_conditional"],
        mechanism_targets=[
            "mechanism:srt:visual_ecological_appraisal",
            "mechanism:art:biophilic_stimulus",
        ],
        mechanism_strengths=[0.78, 0.80],
    ),

    StimulusChannel(
        belief_id="stimulus:wood:fractal_visual",
        material="wood", modality="fractal_visual",
        content=(
            "Close-range or high-resolution view of wood grain engages the fractal fluency "
            "pathway specifically — the visual system matches the 1/f statistics, generating "
            "prediction confirmation rather than prediction error. This is distinct from the "
            "generic 'biophilic presence' signal: requires that the fractal texture be "
            "resolvable at the subject's viewing distance. Fine-grained oak, walnut, or "
            "cedar visible at <2m activates this channel. MDF or laminate at the same distance "
            "does not. ENCOUNTER CONDITION: subject within 2m of visible wood grain surface, "
            "with sufficient illumination (>150 lux) to resolve texture."
        ),
        encounter_condition="close-range view (<2m) of real wood grain with adequate light",
        credence_value=0.75, credence_uncertainty=0.14,
        tags=["stimulus_channel", "wood", "visual", "fractal", "fractal_fluency",
              "T1", "processing_fluency", "encounter_conditional", "distance_conditional"],
        mechanism_targets=["mechanism:art:biophilic_stimulus"],
        mechanism_strengths=[0.85],
    ),

    StimulusChannel(
        belief_id="stimulus:wood:olfactory",
        material="wood", modality="olfactory",
        content=(
            "Wood releases volatile organic compounds (VOCs) — alpha-pinene, cedrol, "
            "guaiacol — that activate olfactory receptor neurons and route directly to the "
            "amygdala via olfactory bulb → piriform cortex (no thalamic relay). This pathway "
            "is always running in parallel with visual processing but is only significant when "
            "the ambient VOC concentration is above detection threshold. ENCOUNTER CONDITIONS: "
            "(1) fresh-cut, untreated, or naturally-weathering wood; (2) cedar or pine species "
            "are strongest emitters; (3) sealed/lacquered wood emits little; (4) adequate "
            "ventilation to carry VOCs to subject (stagnant rooms may accumulate or dissipate). "
            "Most uncertain channel because inter-individual olfactory sensitivity varies 1000x."
        ),
        encounter_condition=(
            "ambient wood VOC concentration above detection threshold — "
            "fresh/untreated/natural wood; NOT sealed/lacquered; subject has functional olfaction"
        ),
        credence_value=0.65, credence_uncertainty=0.20,
        tags=["stimulus_channel", "wood", "olfactory", "VOC", "terpenes",
              "alpha_pinene", "cedrol", "amygdala", "no_thalamic_relay",
              "encounter_conditional", "individual_variation"],
        mechanism_targets=["mechanism:srt:olfactory_ecological_appraisal"],
        mechanism_strengths=[0.72],
    ),

    StimulusChannel(
        belief_id="stimulus:wood:haptic",
        material="wood", modality="haptic",
        content=(
            "Physical contact with wood activates multi-sensory biophilic signal processing: "
            "natural thermal properties (wood is ~10°C warmer to touch than steel at same temp "
            "due to low thermal conductivity), texture gradient confirming organic origin, "
            "variable micro-surface morphology matching neural predictions for biological "
            "materials. Somatosensory inputs from skin receptors join the visual stream via "
            "parietal cortex integration, strengthening the overall biophilic stimulus. "
            "ENCOUNTER CONDITION: subject physically touches exposed wood surface; NOT "
            "applicable for seated or visual-only exposure."
        ),
        encounter_condition=(
            "subject physically touches wood surface — relevant for handrails, "
            "furniture, flooring (barefoot or socked), panelling at arm reach"
        ),
        credence_value=0.70, credence_uncertainty=0.17,
        tags=["stimulus_channel", "wood", "haptic", "touch", "thermal_properties",
              "somatosensory", "texture", "MAT4", "multisensory", "encounter_conditional"],
        mechanism_targets=[
            "mechanism:mat4:multisensory_biophilic_signal",
            "mechanism:art:biophilic_stimulus",
        ],
        mechanism_strengths=[0.75, 0.60],
    ),

    StimulusChannel(
        belief_id="stimulus:wood:acoustic",
        material="wood", modality="acoustic",
        content=(
            "Wood surfaces absorb mid-frequency sound (500Hz–4kHz) due to fibrous pore "
            "structure, reducing reverberation and speech intelligibility degradation in "
            "high-noise environments. The mechanism here is NEGATIVE: wood reduces acoustic "
            "distraction (false salience signals) rather than generating a positive stimulus. "
            "In a high-ambient-noise environment, wooden surfaces reduce unnecessary "
            "DMN→TPN switching, protecting focused attention. Effect is greatest when: "
            "(1) room has high hard-surface area (glass, concrete); (2) there are multiple "
            "talkers or background noise sources; (3) subject is performing sustained cognitive "
            "work. ENCOUNTER CONDITION: subject in a space where wood constitutes >30% of "
            "interior surface area AND ambient noise >55dB(A). No effect in quiet spaces."
        ),
        encounter_condition=(
            "wood constitutes >30% of interior surface AND ambient noise >55dB(A) — "
            "open-plan offices, restaurants, corridors; NOT silent private offices"
        ),
        credence_value=0.72, credence_uncertainty=0.15,
        tags=["stimulus_channel", "wood", "acoustic", "sound_absorption", "reverberation",
              "DT1", "distraction", "noise", "encounter_conditional", "noise_conditional",
              "negative_stimulus"],  # reduces bad signal rather than generating positive
        mechanism_targets=["mechanism:dt1:salience_detection"],
        mechanism_strengths=[0.68],  # inverse: wood reduces salience detection firing
    ),

    StimulusChannel(
        belief_id="stimulus:wood:kinesthetic",
        material="wood", modality="kinesthetic",
        content=(
            "Moving through or past wood-dominated environments — walking on wood floors, "
            "passing through wood-panelled corridors — engages kinesthetic novelty at low "
            "level. Each step on wood produces a distinct acoustic + haptic signal that varies "
            "with grain and surface condition. This micro-novelty activates the dopamine "
            "reward-prediction-error pathway at a subthreshold level, maintaining exploratory "
            "engagement without overwhelming. ENCOUNTER CONDITION: subject in motion (walking) "
            "in a wood-floored or wood-panelled space; NOT applicable for static seated occupancy."
        ),
        encounter_condition=(
            "subject is in motion through space (walking on wood floor, passing panelling) — "
            "NOT applicable for static seated positions"
        ),
        credence_value=0.58, credence_uncertainty=0.22,
        tags=["stimulus_channel", "wood", "kinesthetic", "movement", "novelty",
              "dopamine", "NM2", "walking", "encounter_conditional", "motion_conditional"],
        mechanism_targets=["mechanism:nm:novelty_dopamine"],
        mechanism_strengths=[0.55],
    ),
]

# =============================================================================
# PLANTS STIMULUS CHANNELS
# =============================================================================

PLANTS_CHANNELS: List[StimulusChannel] = [

    StimulusChannel(
        belief_id="stimulus:plants:visual",
        material="plants", modality="visual",
        content=(
            "Indoor plants visible in the environment activate the same visual biophilic "
            "stimulus pathway as wood grain, but via different features: leaf morphology "
            "(bilateral symmetry, lanceolate/ovate forms), fractal branching structure, "
            "dynamic motion (leaves moving). These generate low PE via biological pattern "
            "recognition. ENCOUNTER CONDITION: at least one plant with visible foliage, "
            "in direct line of sight; potted plants behind glass or occluded by furniture "
            "have reduced effect."
        ),
        encounter_condition="plant(s) with visible foliage in line-of-sight",
        credence_value=0.80, credence_uncertainty=0.11,
        tags=["stimulus_channel", "plants", "visual", "biophilic_stimulus", "foliage",
              "fractal", "biological_motion", "encounter_conditional"],
        mechanism_targets=[
            "mechanism:srt:visual_ecological_appraisal",
            "mechanism:art:biophilic_stimulus",
        ],
        mechanism_strengths=[0.78, 0.80],
    ),

    StimulusChannel(
        belief_id="stimulus:plants:olfactory",
        material="plants", modality="olfactory",
        content=(
            "Plants emit volatile compounds (isoprene, monoterpenes, green leaf volatiles "
            "like cis-3-hexenal) that signal 'living vegetation — no decay, no fire'. These "
            "carry different chemical signatures from wood VOCs but route through the same "
            "olfactory bulb → piriform cortex → amygdala pathway. The ecological safety "
            "signal is 'living plant = safe environment'. ENCOUNTER CONDITION: plants must "
            "be actively metabolising — living, not dried or artificial; adequate "
            "nearby proximity (<1.5m) for VOC concentration to exceed threshold."
        ),
        encounter_condition=(
            "living (not dried/artificial) plants within ~1.5m; concentration highest "
            "with recently watered soil, disturbed leaves, or multiple plants"
        ),
        credence_value=0.60, credence_uncertainty=0.22,
        tags=["stimulus_channel", "plants", "olfactory", "VOC", "isoprene",
              "green_leaf_volatiles", "ecological_safety", "encounter_conditional"],
        mechanism_targets=["mechanism:srt:olfactory_ecological_appraisal"],
        mechanism_strengths=[0.65],
    ),
]


ALL_CHANNELS = WOOD_CHANNELS + PLANTS_CHANNELS

MATERIAL_MAP: Dict[str, List[StimulusChannel]] = {
    "wood": WOOD_CHANNELS,
    "plants": PLANTS_CHANNELS,
    "all": ALL_CHANNELS,
}


# =============================================================================
# SEEDER
# =============================================================================

def seed(dry_run: bool = False, material: str = "all") -> None:
    logger.info("Loading master web...")
    acc = WebAccumulator()
    web, _ = acc.get_master_web()

    if web is None:
        logger.error("No master web found.")
        sys.exit(1)

    channels = MATERIAL_MAP.get(material, ALL_CHANNELS)
    logger.info(f"Seeding {len(channels)} stimulus channels for material='{material}'")

    beliefs_added = beliefs_skipped = 0
    constraints_added = constraints_skipped = 0

    existing_constraint_keys = {
        (c.source_id, c.target_id, c.constraint_type)
        for c in web.constraints.values()
    }

    for ch in channels:
        # ── Belief ──────────────────────────────────────────────────────────
        if ch.belief_id in web.beliefs:
            logger.info(f"  SKIP (exists): {ch.belief_id}")
            beliefs_skipped += 1
        else:
            belief = Belief(
                belief_id=ch.belief_id,
                content=ch.content,
                level=EpistemicLevel.THEORETICAL,
                status=BeliefStatus.ESTABLISHED,
                credence=Credence(
                    value=ch.credence_value,
                    uncertainty=ch.credence_uncertainty,
                    n_supporting=2,
                ),
                theory_id="biophilic_design",
                domain="environmental_psychology",
                tags=list(ch.tags),
                paper_ids=[],
            )
            if not dry_run:
                web.add_belief(belief)
            logger.info(
                f"  {'[DRY]' if dry_run else 'ADD'} belief: {ch.belief_id}"
                f" [{ch.modality}] | condition: {ch.encounter_condition[:60]}..."
            )
            beliefs_added += 1

        # ── Constraints to mechanism targets ─────────────────────────────────
        for target_id, strength in zip(ch.mechanism_targets, ch.mechanism_strengths):
            key = (ch.belief_id, target_id, ConstraintType.SUPPORTS)
            if key in existing_constraint_keys:
                constraints_skipped += 1
                continue

            if not dry_run and target_id not in web.beliefs:
                logger.warning(f"  SKIP (target not seeded): {ch.belief_id} → {target_id}")
                constraints_skipped += 1
                continue

            constraint = Constraint(
                constraint_id=f"modality_seed_{uuid.uuid4().hex[:12]}",
                source_id=ch.belief_id,
                target_id=target_id,
                constraint_type=ConstraintType.SUPPORTS,
                strength=strength,
                bidirectional=False,
                causal_direction=CausalDirection.FORWARD,
                mediator=f"{ch.modality} sensory channel | active when: {ch.encounter_condition[:80]}",
            )
            if not dry_run:
                web.add_constraint(constraint)
            logger.info(
                f"  {'[DRY]' if dry_run else 'ADD'} constraint: "
                f"{ch.belief_id} → {target_id} [supports] s={strength}"
            )
            constraints_added += 1
            existing_constraint_keys.add(key)

    # ── Print encounter condition summary ────────────────────────────────────
    print()
    print("=" * 70)
    print(f"Modality seeder {'[DRY RUN]' if dry_run else 'COMPLETE'} — material={material}")
    print(f"  Beliefs    : {beliefs_added} added, {beliefs_skipped} skipped")
    print(f"  Constraints: {constraints_added} added, {constraints_skipped} skipped")
    print()
    print("Encounter-conditional channels seeded:")
    print()
    for ch in channels:
        print(f"  [{ch.material}:{ch.modality}]")
        print(f"    Condition: {ch.encounter_condition}")
        targets = ", ".join(ch.mechanism_targets)
        print(f"    → Activates: {targets}")
        print()
    print("=" * 70)

    if not dry_run and (beliefs_added + constraints_added > 0):
        logger.info("Saving...")
        from src.services.db_locator import resolve_web_db
        from src.services.web_persistence import WebPersistenceService
        db_path = resolve_web_db(prefer="integrated")
        svc = WebPersistenceService(str(db_path))
        master_id = svc.get_master_web_id()
        if master_id:
            svc.save_web(web, master_id)
            logger.info("Saved.")
        else:
            logger.error("Could not find master web ID.")
            sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "Seed encounter-conditional modality stimulus channels for wood, plants, etc. "
            "Each channel is active only under specific encounter conditions."
        )
    )
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview without writing")
    parser.add_argument("--material", default="all",
                        choices=["all", "wood", "plants"],
                        help="Which material to seed (default: all)")
    args = parser.parse_args()
    seed(dry_run=args.dry_run, material=args.material)
