"""
Modality Gap Discovery
=======================

Walks ALL templates to extract stimulus→outcome causal links, then
cross-references against seeded mechanism:, stimulus:, and outcome: nodes
to find UN-SEEDED gaps — i.e., stimulus/outcome variables that appear in
templates but have NO corresponding mechanism node in the web.

Outputs three reports:
  1. UNSEEDED STIMULI   — template variables that need stimulus: channel nodes
  2. UNSEEDED OUTCOMES  — template variables that need outcome: biomarker nodes
  3. MISSING MECHANISM ROUTES — (stimulus, outcome) pairs with no connecting chain

For each gap, suggests:
  - Which modality(ies) might apply (visual, olfactory, haptic, acoustic)
  - Which existing mechanism family could potentially cover it
  - What encounter conditions would gate the stimulus

Run:
    python3 scripts/discover_modality_gaps.py
    python3 scripts/discover_modality_gaps.py --focus wood
    python3 scripts/discover_modality_gaps.py --focus daylight --top 10
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import List, Dict, Set, Tuple, Optional

sys.path.insert(0, os.getcwd())

TEMPLATE_DIR = "data/templates"

# Known modality keywords — used to infer which modality a variable belongs to
MODALITY_SIGNATURES: Dict[str, List[str]] = {
    "visual":       ["visual", "view", "sight", "scene", "fractal", "color", "colour",
                     "light", "gaze", "look", "image", "window", "prospect", "isovist"],
    "olfactory":    ["odor", "olfact", "scent", "smell", "VOC", "terpene", "aroma",
                     "fragrance", "chemical"],
    "haptic":       ["touch", "haptic", "texture", "thermal", "temperature", "warm",
                     "tactile", "surface", "material"],
    "acoustic":     ["sound", "acoustic", "noise", "auditory", "music", "birdsong",
                     "silence", "reverberation", "speech"],
    "kinesthetic":  ["movement", "walking", "locomotion", "motion", "gait", "navigation",
                     "wayfinding", "exploration"],
    "temporal":     ["duration", "exposure_time", "circadian", "rhythm", "phase",
                     "temporal", "dynamic", "variation"],
    "social":       ["social", "crowd", "people", "interpersonal", "group", "communal",
                     "encounter", "presence"],
    "cognitive":    ["attention", "memory", "cognitive", "executive", "inhibit",
                     "working_memory", "concentration", "focus"],
    "affective":    ["affect", "emotion", "mood", "valence", "arousal", "stress",
                     "anxiety", "calm", "pleasure", "pain"],
    "physiological": ["heart_rate", "cortisol", "blood_pressure", "HRV", "EDA", "GSR",
                      "respiratory", "autonomic", "sympathetic", "parasympathetic",
                      "HPA", "amygdala"],
}

# Known mechanism families and their keywords
MECHANISM_FAMILIES: Dict[str, List[str]] = {
    "ART":   ["attention", "fascination", "involuntary", "directed_attention", "restoration",
              "cognitive", "biophilic", "fractal"],
    "SRT":   ["stress", "recovery", "autonomic", "cortisol", "sympathetic", "amygdala",
              "HPA", "affect", "calming", "physiological"],
    "MAT4":  ["material", "multisensory", "wood", "stone", "haptic", "texture",
              "convergent", "fluency"],
    "L3":    ["daylight", "circadian", "light", "melatonin", "serotonin", "ipRGC",
              "visual_performance"],
    "NM":    ["dopamine", "novelty", "oxytocin", "social", "reward", "exploration",
              "curiosity"],
    "DT1":   ["distraction", "DMN", "TPN", "salience", "switching", "noise",
              "interruption"],
}


@dataclass
class GapEntry:
    variable: str
    template_ids: List[str]
    side: str  # "stimulus" or "outcome"
    inferred_modalities: List[str]
    suggested_mechanism: Optional[str]
    count: int
    example_partner: str  # what it connects to in the template


def load_templates() -> List[Dict]:
    templates = []
    for f in sorted(os.listdir(TEMPLATE_DIR)):
        if not f.endswith(".json"):
            continue
        try:
            t = json.loads(open(os.path.join(TEMPLATE_DIR, f)).read())
            t["_filename"] = f
            templates.append(t)
        except Exception as e:
            import logging; logging.getLogger(__name__).debug(f"Skipped: {e}")
            continue
    return templates


def infer_modalities(variable: str) -> List[str]:
    v_lower = variable.lower().replace("_", " ")
    matches = []
    for modality, keywords in MODALITY_SIGNATURES.items():
        if any(kw.lower() in v_lower for kw in keywords):
            matches.append(modality)
    return matches or ["unknown"]


def suggest_mechanism(variable: str) -> Optional[str]:
    v_lower = variable.lower().replace("_", " ")
    best_family = None
    best_score = 0
    for family, keywords in MECHANISM_FAMILIES.items():
        score = sum(1 for kw in keywords if kw.lower() in v_lower)
        if score > best_score:
            best_score = score
            best_family = family
    return best_family if best_score > 0 else None


def discover_gaps(focus: Optional[str] = None, top_n: int = 20) -> Tuple[List[GapEntry], List[GapEntry], Dict]:
    """Returns (stimulus_gaps, outcome_gaps, stats)."""
    templates = load_templates()

    # Collect all from/to variables across templates
    stim_sources: Dict[str, List[str]] = defaultdict(list)   # var → [template_id]
    outcome_sources: Dict[str, List[str]] = defaultdict(list)
    stim_partners: Dict[str, str] = {}  # var → example partner
    outcome_partners: Dict[str, str] = {}
    pair_count: Counter = Counter()  # (from, to) → count

    for t in templates:
        tid = t.get("template_id", t.get("_filename", "?"))
        links = t.get("causal_links", [])
        for lk in links:
            frm = lk.get("from_variable", lk.get("from_entity", ""))
            to = lk.get("to_variable", lk.get("to_entity", ""))
            if not frm or not to:
                continue
            stim_sources[frm].append(tid)
            outcome_sources[to].append(tid)
            stim_partners[frm] = to
            outcome_partners[to] = frm
            pair_count[(frm, to)] += 1

    # Load seeded nodes from web
    try:
        from src.services.web_accumulator import WebAccumulator
        acc = WebAccumulator()
        web, _ = acc.get_master_web()
        seeded_ids = set(web.beliefs.keys()) if web else set()
    except Exception:
        seeded_ids = set()

    # Build set of "covered" variable names (fuzzy match against seeded belief IDs)
    def is_covered(variable: str) -> bool:
        v_words = set(variable.lower().replace("_", " ").split())
        for sid in seeded_ids:
            if not any(sid.startswith(p) for p in ("mechanism:", "stimulus:", "outcome:")):
                continue
            sid_words = set(sid.lower().replace(":", " ").replace("_", " ").split())
            overlap = len(v_words & sid_words)
            if overlap >= 2 or (overlap >= 1 and len(v_words) <= 2):
                return True
        return False

    # Build gap lists
    stim_gaps: List[GapEntry] = []
    for var, tids in stim_sources.items():
        if focus and focus.lower() not in var.lower():
            continue
        if not is_covered(var):
            stim_gaps.append(GapEntry(
                variable=var,
                template_ids=tids,
                side="stimulus",
                inferred_modalities=infer_modalities(var),
                suggested_mechanism=suggest_mechanism(var),
                count=len(tids),
                example_partner=stim_partners.get(var, "?"),
            ))

    outcome_gaps: List[GapEntry] = []
    for var, tids in outcome_sources.items():
        if focus and focus.lower() not in var.lower():
            continue
        if not is_covered(var):
            outcome_gaps.append(GapEntry(
                variable=var,
                template_ids=tids,
                side="outcome",
                inferred_modalities=infer_modalities(var),
                suggested_mechanism=suggest_mechanism(var),
                count=len(tids),
                example_partner=outcome_partners.get(var, "?"),
            ))

    stim_gaps.sort(key=lambda g: -g.count)
    outcome_gaps.sort(key=lambda g: -g.count)

    stats = {
        "total_templates_with_links": sum(1 for t in templates if t.get("causal_links")),
        "total_distinct_stimuli": len(stim_sources),
        "total_distinct_outcomes": len(outcome_sources),
        "seeded_mechanism_nodes": len([s for s in seeded_ids if s.startswith("mechanism:")]),
        "seeded_stimulus_nodes": len([s for s in seeded_ids if s.startswith("stimulus:")]),
        "seeded_outcome_nodes": len([s for s in seeded_ids if s.startswith("outcome:")]),
        "unseeded_stimuli": len(stim_gaps),
        "unseeded_outcomes": len(outcome_gaps),
    }

    return stim_gaps[:top_n], outcome_gaps[:top_n], stats


def main():
    parser = argparse.ArgumentParser(
        description="Discover unseeded stimulus/outcome variables from templates"
    )
    parser.add_argument("--focus", default=None,
                        help="Filter to variables containing this keyword (e.g., 'wood', 'light')")
    parser.add_argument("--top", type=int, default=20,
                        help="Show top N gaps (default: 20)")
    args = parser.parse_args()

    stim_gaps, outcome_gaps, stats = discover_gaps(focus=args.focus, top_n=args.top)

    print()
    print("=" * 72)
    print("MODALITY GAP DISCOVERY REPORT")
    if args.focus:
        print(f"  Focused on: '{args.focus}'")
    print("=" * 72)
    print()
    print("COVERAGE STATISTICS:")
    for k, v in stats.items():
        label = k.replace("_", " ").title()
        print(f"  {label:40s} {v}")
    print()

    if stim_gaps:
        print(f"{'='*72}")
        print(f"UNSEEDED STIMULI ({len(stim_gaps)} gaps)")
        print(f"{'='*72}")
        for g in stim_gaps:
            mods = ", ".join(g.inferred_modalities)
            mech = g.suggested_mechanism or "—"
            print(f"\n  [{g.count}x] {g.variable}")
            print(f"       Modalities: {mods}")
            print(f"       Suggested mechanism family: {mech}")
            print(f"       Example target: → {g.example_partner}")
            print(f"       Templates: {', '.join(g.template_ids[:3])}")

    if outcome_gaps:
        print(f"\n{'='*72}")
        print(f"UNSEEDED OUTCOMES ({len(outcome_gaps)} gaps)")
        print(f"{'='*72}")
        for g in outcome_gaps:
            mods = ", ".join(g.inferred_modalities)
            mech = g.suggested_mechanism or "—"
            print(f"\n  [{g.count}x] {g.variable}")
            print(f"       Modalities: {mods}")
            print(f"       Suggested mechanism family: {mech}")
            print(f"       Example source: {g.example_partner} →")
            print(f"       Templates: {', '.join(g.template_ids[:3])}")

    if not stim_gaps and not outcome_gaps:
        print("No unseeded gaps found! All template variables are covered.")

    print()
    print("=" * 72)


if __name__ == "__main__":
    main()
