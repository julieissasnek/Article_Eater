"""
Outcome Attribute Granular Seeder
===================================

Seeds granular outcome nodes at the downstream end of mechanism chains.

The insight: "physiological_normalization" is not one thing — it is a BUNDLE
of parallel biomarker trajectories, each with its own:
  - Mechanism (different neural pathway)
  - Latency  (how fast it changes after stimulus)
  - Measurement (what instrument captures it)
  - Effect size (how reliably it responds)
  - Condition sensitivity (who responds and when)

Current coarse chain:            Expanded granular chain:
                                   ┌→ outcome:srt:heart_rate_reduction
autonomic_recovery                 ├→ outcome:srt:hrv_increase         ← most sensitive
  ↓                     ──→        ├→ outcome:srt:cortisol_reduction   ← slowest (~15–20 min)
physiological_normalization         ├→ outcome:srt:blood_pressure_reduction
                                   ├→ outcome:srt:skin_conductance_reduction  ← fastest
                                   └→ outcome:srt:respiratory_normalization

Similarly on the ART cognitive side:
directed_attention_restoration ──→ ┌→ outcome:art:working_memory_recovery
                                   ├→ outcome:art:inhibitory_control_recovery
                                   └→ outcome:art:sustained_attention_recovery

And on the subjective/self-report side (not biomarker):
                                   ┌→ outcome:subjective:calm
                                   ├→ outcome:subjective:vitality
                                   └→ outcome:subjective:positive_valence

Each outcome node:
  1. Has specific latency (when it appears after stimulus onset)
  2. Has specific measurement method
  3. Potentially has its own further mechanism trajectory
     (e.g., HRV increase → better vagal regulation → improved sleep → ...)

Run:
    python3 scripts/seed_outcome_attributes.py
    python3 scripts/seed_outcome_attributes.py --dry-run
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
import uuid
from dataclasses import dataclass, field
from typing import List

sys.path.insert(0, os.getcwd())

from src.services.web_accumulator import WebAccumulator
from src.services.web_of_belief import (
    Belief, Constraint, Credence,
    EpistemicLevel, BeliefStatus, ConstraintType, CausalDirection,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


@dataclass
class OutcomeNode:
    belief_id: str
    content: str
    latency_seconds: tuple  # (min, max) seconds from stimulus onset
    measurement: str
    effect_size: str
    upstream_node: str      # which mechanism node feeds this outcome
    upstream_strength: float
    credence_value: float
    credence_uncertainty: float
    tags: List[str] = field(default_factory=list)


# =============================================================================
# SRT PHYSIOLOGICAL OUTCOMES
# Upstream: mechanism:srt:autonomic_recovery
# =============================================================================

SRT_OUTCOMES: List[OutcomeNode] = [

    OutcomeNode(
        belief_id="outcome:srt:skin_conductance_reduction",
        content=(
            "Skin conductance (galvanic skin response, GSR) drops within 30–90 seconds "
            "of biophilic stimulus onset — the fastest measurable physiological outcome. "
            "Eccrine sweat glands are directly innervated by sympathetic cholinergic fibres; "
            "as sympathetic withdrawal begins (HPA gate closed), sweat gland secretion falls "
            "within one or two autonomic reflex loops. Ulrich (1983) used GSR as primary "
            "measure; 4-minute recovery curves are clearly visible. This is the earliest "
            "detectable marker of SRT activation — before conscious calming is reported."
        ),
        latency_seconds=(30, 120),
        measurement="GSR / EDA (electrodermal activity); wrist or finger electrode",
        effect_size="Cohen's d ≈ 0.5–0.8 vs. urban scenes (Ulrich 1983)",
        upstream_node="mechanism:srt:autonomic_recovery",
        upstream_strength=0.82,
        credence_value=0.84, credence_uncertainty=0.09,
        tags=["outcome_node", "SRT", "GSR", "EDA", "skin_conductance",
              "fastest_biomarker", "sympathetic", "measurement:EDA"],
    ),

    OutcomeNode(
        belief_id="outcome:srt:heart_rate_reduction",
        content=(
            "Heart rate (HR) reduction occurs 2–5 minutes after biophilic stimulus onset, "
            "driven by increased cardiac vagal tone (parasympathetic rebound) and reduced "
            "sympathetic cardiac drive. The sino-atrial node receives both sympathetic "
            "(accelerate) and vagal (decelerate) input; as sympathetic withdrawal proceeds, "
            "vagal tone dominates, slowing HR. Typical reductions: 3–8 bpm relative to "
            "stress-elevated baseline. Sensitive to individual differences in resting HR "
            "and baseline stress state — effect is larger when baseline is elevated. "
            "(Ulrich et al. 1991; Laumann et al. 2003)"
        ),
        latency_seconds=(120, 400),
        measurement="ECG R-R interval or photoplethysmography (PPG); chest or fingertip",
        effect_size="3–8 bpm reduction; d ≈ 0.4–0.6",
        upstream_node="mechanism:srt:autonomic_recovery",
        upstream_strength=0.80,
        credence_value=0.82, credence_uncertainty=0.10,
        tags=["outcome_node", "SRT", "heart_rate", "HR", "cardiac", "vagal",
              "parasympathetic", "sino_atrial", "measurement:ECG"],
    ),

    OutcomeNode(
        belief_id="outcome:srt:hrv_increase",
        content=(
            "Heart rate variability (HRV) — specifically RMSSD and HF power — increases "
            "during and after biophilic exposure, reflecting improved autonomic balance and "
            "vagal dominance. HRV is the most sensitive continuous marker of autonomic "
            "state: it responds faster than discrete HR measures and reflects the balance "
            "between sympathetic tone (low HRV) and parasympathetic capacity (high HRV). "
            "A 5-minute window of HF HRV during nature exposure vs. urban control shows "
            "consistently higher values in nature condition. HRV also predicts downstream "
            "outcomes: higher HRV correlates with better cognitive flexibility, immune "
            "function, and emotional regulation. This makes HRV a 'gateway biomarker' — "
            "seeding a further mechanism trajectory toward cognitive and immune outcomes. "
            "(Park et al. 2010: forest bathing; RMSSD +8.3 ms; d ≈ 0.6)"
        ),
        latency_seconds=(60, 300),
        measurement="RMSSD or HF power from ECG; requires 5-min epoch minimum",
        effect_size="RMSSD +5–10ms; HF power +15–25%; d ≈ 0.5–0.7",
        upstream_node="mechanism:srt:autonomic_recovery",
        upstream_strength=0.83,
        credence_value=0.80, credence_uncertainty=0.11,
        tags=["outcome_node", "SRT", "HRV", "RMSSD", "HF_power", "vagal_tone",
              "autonomic_balance", "gateway_biomarker", "measurement:HRV",
              "most_sensitive_biomarker"],
    ),

    OutcomeNode(
        belief_id="outcome:srt:blood_pressure_reduction",
        content=(
            "Systolic and diastolic blood pressure (SBP/DBP) fall 5–15 minutes after "
            "biophilic exposure onset, driven by peripheral vasodilation as sympathetic "
            "vasoconstrictor tone drops. Arterial smooth muscle is innervated by sympathetic "
            "adrenergic fibres; as norepinephrine withdrawal proceeds, vessels dilate, "
            "reducing peripheral resistance. Effect requires sustained exposure (>5 min); "
            "brief glances are insufficient. Effect is substantially larger in participants "
            "with elevated baseline BP (hypertensive range). "
            "(Laumann et al. 2003: SBP –4 mmHg; Tsunetsugu et al. 2010: forest vs. city)"
        ),
        latency_seconds=(300, 900),
        measurement="sphygmomanometer or continuous arterial tonometry",
        effect_size="SBP –2–6 mmHg; DBP –1–4 mmHg; larger in stress-elevated state",
        upstream_node="mechanism:srt:autonomic_recovery",
        upstream_strength=0.75,
        credence_value=0.76, credence_uncertainty=0.13,
        tags=["outcome_node", "SRT", "blood_pressure", "SBP", "DBP",
              "vasodilation", "peripheral_resistance", "measurement:BP",
              "condition:baseline_elevated"],
    ),

    OutcomeNode(
        belief_id="outcome:srt:cortisol_reduction",
        content=(
            "Salivary or serum cortisol falls 15–30 minutes after biophilic stimulus — "
            "the slowest SRT biomarker because the HPA axis operates on a slow hormonal "
            "timescale. Even though the amygdala gate closes quickly (minutes), the cortisol "
            "already in circulation has a half-life of ~60–90 minutes; 'reduction' means "
            "the rate of new cortisol secretion falls while existing cortisol is metabolised. "
            "This slow trajectory is why Ulrich's original 4–7 min GSR studies are more "
            "convincing than cortisol studies for immediate effects — cortisol is the "
            "'invoice' that arrives after the 'stress order' was cancelled. "
            "Forest bathing studies (Park et al. 2010) show cortisol –13% vs. urban control "
            "over a 3-hour programme. For brief (<15 min) exposures, cortisol reduction may "
            "be statistically undetectable despite genuine autonomic recovery."
        ),
        latency_seconds=(900, 2400),
        measurement="salivary cortisol immunoassay; timing critical (circadian confound)",
        effect_size="–10–20% salivary cortisol vs. urban control (3-hr forest bathing)",
        upstream_node="mechanism:srt:hpa_suppression",
        upstream_strength=0.78,
        credence_value=0.74, credence_uncertainty=0.14,
        tags=["outcome_node", "SRT", "cortisol", "HPA_axis", "salivary_cortisol",
              "slowest_biomarker", "measurement:cortisol",
              "condition:duration_GT_15min"],
    ),

    OutcomeNode(
        belief_id="outcome:srt:respiratory_normalization",
        content=(
            "Respiratory rate slows and respiratory depth increases during biophilic "
            "exposure, driven by parasympathetic activation of respiratory nuclei in the "
            "brainstem (NTS, Bötzinger complex). Natural environments also reduce the "
            "urge to breathe shallowly associated with anxiety ('stress breathing'). "
            "The respiratory change is also a DRIVER of further HRV improvement: "
            "slow deep breathing (respiratory sinus arrhythmia, RSA) amplifies "
            "parasympathetic cardiac influence, creating a positive feedback loop. "
            "This makes respiratory normalization both an outcome AND a mediator of "
            "further HRV/HR improvement. (Chang et al. 2016: forest vs. city, breath rate –2/min)"
        ),
        latency_seconds=(60, 300),
        measurement="chest band, nasal airflow, or PPG-derived respiratory signal",
        effect_size="–1.5–3 breaths/min; VT increase ~15%",
        upstream_node="mechanism:srt:autonomic_recovery",
        upstream_strength=0.72,
        credence_value=0.74, credence_uncertainty=0.14,
        tags=["outcome_node", "SRT", "respiratory_rate", "breathing", "RSA",
              "brainstem", "NTS", "HRV_driver", "measurement:respiration",
              "outcome_and_mediator"],
    ),
]

# =============================================================================
# ART COGNITIVE OUTCOMES
# Upstream: mechanism:art:directed_attention_restoration
# =============================================================================

ART_OUTCOMES: List[OutcomeNode] = [

    OutcomeNode(
        belief_id="outcome:art:working_memory_recovery",
        content=(
            "Working memory capacity (measured by n-back, digit span backward, or "
            "operation span) improves after nature exposure vs. urban control. Working "
            "memory relies on prefrontal dorsolateral regions that are also responsible "
            "for directed attention; shared prefrontal resource pool means WM and directed "
            "attention co-recover. Kaplan & Berman (2010) propose WM as a direct proxy for "
            "directed attention capacity. Effect requires >10 min nature exposure. "
            "(Berto 2014 meta-analysis: d ≈ 0.3–0.5)"
        ),
        latency_seconds=(600, 2400),
        measurement="n-back task, backward digit span, operation span",
        effect_size="d ≈ 0.3–0.5; requires >10 min exposure",
        upstream_node="mechanism:art:directed_attention_restoration",
        upstream_strength=0.75,
        credence_value=0.72, credence_uncertainty=0.14,
        tags=["outcome_node", "ART", "working_memory", "prefrontal",
              "cognitive_performance", "n_back", "measurement:WM"],
    ),

    OutcomeNode(
        belief_id="outcome:art:inhibitory_control_recovery",
        content=(
            "Inhibitory control (Stroop interference, go/no-go accuracy) recovers after "
            "nature exposure. Inhibitory control requires sustained prefrontal inhibition "
            "of prepotent responses — the same resource depleted by directed attention "
            "fatigue. Recovery is faster for interference suppression (Stroop) than for "
            "pure WM tasks. This is clinically important: impaired inhibitory control "
            "after sustained cognitive work predicts risk-taking and reduced self-regulation "
            "— nature exposure 'resets' the inhibitory threshold. "
            "(van der Berg et al. 2015: Stroop d ≈ 0.4 nature vs. built)"
        ),
        latency_seconds=(300, 1800),
        measurement="Stroop task, go/no-go, or stop-signal reaction time",
        effect_size="d ≈ 0.35–0.55; faster recovery than WM",
        upstream_node="mechanism:art:directed_attention_restoration",
        upstream_strength=0.72,
        credence_value=0.70, credence_uncertainty=0.15,
        tags=["outcome_node", "ART", "inhibitory_control", "Stroop", "prefrontal",
              "self_regulation", "measurement:Stroop"],
    ),

    OutcomeNode(
        belief_id="outcome:art:sustained_attention_recovery",
        content=(
            "Sustained attention (vigilance task performance, SART, CPT) improves after "
            "nature exposure. Sustained attention is the most directly tested ART outcome: "
            "Kaplan's original (1989) and Berman et al. (2008) studies used attention tasks "
            "as primary measures. Effect is clearest when participants are pre-fatigued by "
            "demanding cognitive work. Architecture that provides nature views during work "
            "may produce continuous micro-restorations rather than requiring discrete "
            "nature breaks. (Berman et al. 2008: backward digit span d ≈ 0.5 walk vs. city)"
        ),
        latency_seconds=(300, 1800),
        measurement="SART (Sustained Attention to Response Task), CPT, digit span",
        effect_size="d ≈ 0.4–0.6 post-fatigue; smaller without pre-fatigue",
        upstream_node="mechanism:art:directed_attention_restoration",
        upstream_strength=0.80,
        credence_value=0.78, credence_uncertainty=0.11,
        tags=["outcome_node", "ART", "sustained_attention", "vigilance", "SART",
              "CPT", "fatigue_recovery", "measurement:attention"],
    ),
]

# =============================================================================
# SUBJECTIVE SELF-REPORT OUTCOMES (bridge between biomarker and felt experience)
# =============================================================================

SUBJECTIVE_OUTCOMES: List[OutcomeNode] = [

    OutcomeNode(
        belief_id="outcome:subjective:calm",
        content=(
            "Subjective calm / tranquillity (measured by Perceived Restorativeness Scale, "
            "PANAS negative affect subscale, VAS calm–anxious) is reported within minutes "
            "of biophilic stimulus. Subjective calm is the conscious correlate of the "
            "HPA suppression + autonomic recovery, not its cause. It arrives AFTER the "
            "physiological changes have begun but BEFORE biomarker changes are complete. "
            "Critically, subjective calm can be elicited by images, not just real "
            "environments — suggesting the visual/olfactory appraisal pathway is "
            "sufficient without full environmental immersion."
        ),
        latency_seconds=(60, 300),
        measurement="PANAS, PRS, VAS; self-report immediately or after 5-min exposure",
        effect_size="PANAS negative affect d ≈ 0.5–0.7",
        upstream_node="mechanism:srt:positive_affect_shift",
        upstream_strength=0.85,
        credence_value=0.82, credence_uncertainty=0.09,
        tags=["outcome_node", "SRT", "subjective", "calm", "tranquillity",
              "PANAS", "PRS", "self_report", "measurement:questionnaire"],
    ),

    OutcomeNode(
        belief_id="outcome:subjective:vitality",
        content=(
            "Subjective vitality / energy (Ryan & Frederick 1997 vitality scale) increases "
            "after nature exposure — paradoxically, 'restoration' produces felt energy not "
            "lethargy. This reflects the directed-attention recovery trajectory: replenished "
            "inhibitory control feels like increased capacity/energy. Vitality is "
            "distinguishable from arousal (which is non-specific) and from calm (which is "
            "the SRT subjective outcome). Vitality specifically indexes ART outcome — "
            "cognitive resources felt as available and 'ready to engage'. "
            "(Ryan et al. 2010: nature walk +vitality, –negative affect)"
        ),
        latency_seconds=(600, 2400),
        measurement="SVS (Subjective Vitality Scale); 5-min exposure minimum",
        effect_size="d ≈ 0.4–0.5; stronger when baseline fatigue present",
        upstream_node="mechanism:art:directed_attention_restoration",
        upstream_strength=0.72,
        credence_value=0.70, credence_uncertainty=0.15,
        tags=["outcome_node", "ART", "subjective", "vitality", "energy",
              "SVS", "self_report", "measurement:questionnaire"],
    ),
]

ALL_OUTCOMES = SRT_OUTCOMES + ART_OUTCOMES + SUBJECTIVE_OUTCOMES


def seed(dry_run: bool = False) -> None:
    logger.info("Loading master web...")
    acc = WebAccumulator()
    web, _ = acc.get_master_web()
    if web is None:
        logger.error("No master web found.")
        sys.exit(1)

    beliefs_added = beliefs_skipped = 0
    constraints_added = constraints_skipped = 0
    existing_keys = {
        (c.source_id, c.target_id, c.constraint_type)
        for c in web.constraints.values()
    }

    for out in ALL_OUTCOMES:
        # Belief
        if out.belief_id in web.beliefs:
            logger.info(f"  SKIP (exists): {out.belief_id}")
            beliefs_skipped += 1
        else:
            belief = Belief(
                belief_id=out.belief_id,
                content=out.content,
                level=EpistemicLevel.THEORETICAL,
                status=BeliefStatus.ESTABLISHED,
                credence=Credence(
                    value=out.credence_value,
                    uncertainty=out.credence_uncertainty,
                    n_supporting=3,
                ),
                theory_id="stress_recovery_theory",
                domain="environmental_psychology",
                tags=list(out.tags),
                paper_ids=[],
            )
            if not dry_run:
                web.add_belief(belief)
            logger.info(f"  {'[DRY]' if dry_run else 'ADD'} outcome belief: {out.belief_id}")
            beliefs_added += 1

        # Upstream constraint
        key = (out.upstream_node, out.belief_id, ConstraintType.EPISTEMIC_MEDIATION)
        if key in existing_keys:
            constraints_skipped += 1
        else:
            if not dry_run and out.upstream_node not in web.beliefs:
                logger.warning(f"  SKIP (upstream not seeded): {out.upstream_node}")
                constraints_skipped += 1
            else:
                c = Constraint(
                    constraint_id=f"outcome_seed_{uuid.uuid4().hex[:12]}",
                    source_id=out.upstream_node,
                    target_id=out.belief_id,
                    constraint_type=ConstraintType.EPISTEMIC_MEDIATION,
                    strength=out.upstream_strength,
                    bidirectional=False,
                    causal_direction=CausalDirection.MEDIATED,
                    mediator=(
                        f"latency {out.latency_seconds[0]}–{out.latency_seconds[1]}s "
                        f"| measured by: {out.measurement[:60]}"
                    ),
                )
                if not dry_run:
                    web.add_constraint(c)
                logger.info(
                    f"  {'[DRY]' if dry_run else 'ADD'} constraint: "
                    f"{out.upstream_node} → {out.belief_id} [mediation] s={out.upstream_strength}"
                )
                constraints_added += 1
                existing_keys.add(key)

    print()
    print("=" * 70)
    print(f"Outcome seeder {'[DRY RUN]' if dry_run else 'COMPLETE'}")
    print(f"  Beliefs    : {beliefs_added} added, {beliefs_skipped} skipped")
    print(f"  Constraints: {constraints_added} added, {constraints_skipped} skipped")
    print()
    print("Outcome biomarker nodes by latency:")
    print()
    for out in sorted(ALL_OUTCOMES, key=lambda x: x.latency_seconds[0]):
        lat = f"{out.latency_seconds[0]}–{out.latency_seconds[1]}s"
        print(f"  [{lat:>14}] {out.belief_id}")
        print(f"               Effect: {out.effect_size}")
    print()
    print("=" * 70)

    if not dry_run and (beliefs_added + constraints_added > 0):
        from src.services.db_locator import resolve_web_db
        from src.services.web_persistence import WebPersistenceService
        db_path = resolve_web_db(prefer="integrated")
        svc = WebPersistenceService(str(db_path))
        master_id = svc.get_master_web_id()
        if master_id:
            svc.save_web(web, master_id)
            logger.info("Saved.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Seed granular outcome attribute nodes downstream of mechanism chains"
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    seed(dry_run=args.dry_run)
