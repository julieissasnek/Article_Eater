#!/usr/bin/env python3
"""
Sprint S-1: Outcome Vocabulary Expansion
==========================================

Processes the unresolved outcomes queue to:
1. Filter noise (fragments, off-domain terms, measurement artifacts)
2. Cluster remaining terms by domain
3. Match against existing vocab (fuzzy)
4. Propose new canonical entries for gaps
5. Update outcome_vocab.json with approved additions

Usage:
    python scripts/expand_outcome_vocab.py                    # Full analysis
    python scripts/expand_outcome_vocab.py --apply            # Write expanded vocab
    python scripts/expand_outcome_vocab.py --report-only      # Just generate report
"""

import argparse
import json
import re
import sys
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime, timezone
from difflib import SequenceMatcher

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

VOCAB_PATH = PROJECT_ROOT / "contracts" / "outcome_vocab" / "outcome_vocab.json"
UNRESOLVED_PATH = PROJECT_ROOT / "data" / "unresolved_outcomes.jsonl"
OUTPUT_DIR = PROJECT_ROOT / "data" / "vocab_expansion"


# =============================================================================
# Pass 1: Noise Filtering
# =============================================================================

# Terms that are clearly NOT outcomes of built environment experiences
NOISE_PATTERNS = [
    # Numeric fragments
    re.compile(r'^\d+[\.\,\s]'),
    re.compile(r'^\d+$'),
    re.compile(r'^[\d\.\,\s\(\)\%]+$'),
    # Medical/clinical (not arch-relevant)
    re.compile(r'\b(?:patient|surgical|tumor|cancer|genomic|protein|chemotherapy|dosage|transplant)\b', re.I),
    # ML/CS jargon
    re.compile(r'\b(?:neural network|deep learning|dataset|algorithm|GPU|tensorflow|pytorch|segmentation model)\b', re.I),
    # Engineering (non-architectural)
    re.compile(r'\b(?:hydrogen production|truck platooning|cosmolog|mining|server|robot(?:ic)?s?\b)', re.I),
    # Very short fragments
    re.compile(r'^.{1,5}$'),
    # Clear measurement artifacts
    re.compile(r'\b(?:p\s*[<>]\s*0|95%\s*CI|odds ratio|hazard ratio)\b', re.I),
    # Drug/pharma
    re.compile(r'\b(?:dexmedetomidine|propofol|morphine|opioid|antibiotic)\b', re.I),
    # Generic method descriptions
    re.compile(r'\b(?:proposed method|our approach|this paper|we present|is investigated)\b', re.I),
]


def is_noise(term: str) -> bool:
    """Check if a term is noise (not an outcome)."""
    return any(p.search(term) for p in NOISE_PATTERNS)


# =============================================================================
# Pass 2: Domain Classification
# =============================================================================

DOMAIN_KEYWORDS = {
    "affect": {
        "kw": ["emotion", "mood", "affect", "feeling", "anxiety", "stress", "happiness",
               "satisfaction", "frustration", "joy", "awe", "wonder", "fear", "anger",
               "pleasure", "displeasure", "valence", "arousal", "calm", "relax",
               "contentment", "delight", "serenity", "boredom", "excitement",
               "nostalgia", "sense of place", "attachment", "beauty", "aesthet",
               "preference", "liking", "appreciation"],
        "weight": 1.0,
    },
    "cog": {
        "kw": ["attention", "memory", "cognit", "perception", "wayfinding", "legibility",
               "creativity", "focus", "concentrat", "processing", "mental", "thinking",
               "decision", "judgment", "spatial", "visual", "learning", "executive",
               "reasoning", "problem solving", "comprehension", "recognition",
               "imagination", "mental model", "cognitive load", "information"],
        "weight": 1.0,
    },
    "behav": {
        "kw": ["behavior", "behaviour", "activity", "movement", "performance", "productiv",
               "dwell", "staying", "walking", "exploration", "navigation", "sleep",
               "engagement", "participation", "social behav", "risk taking",
               "comfort seeking", "avoidance", "approach", "occupancy"],
        "weight": 1.0,
    },
    "physio": {
        "kw": ["heart rate", "HRV", "cortisol", "skin conduct", "blood pressure",
               "respiration", "breathing", "pupil", "eye movement", "gaze",
               "fatigue", "alertness", "arousal", "thermal", "pain",
               "galvanic", "electrodermal", "circadian", "melatonin",
               "body temperature", "sweat"],
        "weight": 1.0,
    },
    "neural": {
        "kw": ["brain", "neural", "fMRI", "EEG", "cortex", "amygdala",
               "hippocampus", "prefrontal", "BOLD", "oscillation", "brainwave",
               "synchrony", "activation pattern", "neural correlate"],
        "weight": 1.0,
    },
    "social": {
        "kw": ["social", "interaction", "collaboration", "community", "trust",
               "cohesion", "belonging", "interpersonal", "communication",
               "privacy", "personal space", "crowding", "isolation",
               "territoriality", "identity", "place attachment"],
        "weight": 1.0,
    },
    "health": {
        "kw": ["wellbeing", "well-being", "health", "recovery", "healing",
               "resilience", "restoration", "restorative", "recuperat",
               "quality of life", "sick building", "symptom", "headache",
               "allergy", "asthma", "chronic"],
        "weight": 1.0,
    },
    "env": {
        "kw": ["lighting", "noise", "sound", "acoustic", "air quality",
               "ventilation", "temperature", "humidity", "daylight", "nature",
               "biophil", "green", "prospect", "refuge", "spacious", "enclosure",
               "material", "texture", "color", "colour", "view", "window",
               "ceiling", "density", "complexity", "order", "symmetry"],
        "weight": 1.0,
    },
}


def classify_domain(term: str) -> list:
    """Classify a term into one or more domains. Returns [(domain, score)]."""
    tl = term.lower()
    scores = {}
    for domain, config in DOMAIN_KEYWORDS.items():
        score = sum(1 for kw in config["kw"] if kw in tl) * config["weight"]
        if score > 0:
            scores[domain] = score
    
    if not scores:
        return [("unclassified", 0)]
    
    return sorted(scores.items(), key=lambda x: -x[1])


# =============================================================================
# Pass 3: Fuzzy Match Against Existing Vocab
# =============================================================================

def fuzzy_match(term: str, vocab_terms: list, threshold: float = 0.6) -> list:
    """Find existing vocab terms that fuzzy-match the raw term."""
    matches = []
    tl = term.lower()
    
    for vt in vocab_terms:
        # Check cognates too
        candidates = [vt["name"].lower()] + [c.lower() for c in vt.get("cognates", [])]
        for cand in candidates:
            ratio = SequenceMatcher(None, tl, cand).ratio()
            if ratio >= threshold:
                matches.append({
                    "term_id": vt["term_id"],
                    "name": vt["name"],
                    "matched_on": cand,
                    "similarity": round(ratio, 3),
                })
                break  # One match per vocab term is enough
    
    return sorted(matches, key=lambda x: -x["similarity"])


# =============================================================================
# Pass 4: Propose New Canonical Entries
# =============================================================================

# Gaps identified in architectural cognition research that current vocab misses
PROPOSED_NEW_TERMS = [
    # Cognitive — missing spatial and visual cognition
    {"term_id": "cog.spatial_cognition", "name": "Spatial Cognition", "domain": "cog",
     "parent_id": "cog", "definition": "Mental representation and reasoning about space",
     "level": 2, "cognates": ["spatial awareness", "spatial reasoning", "mental rotation", "cognitive map"],
     "operationalizations": ["Mental rotation task", "Pointing task", "Map drawing"]},
    
    {"term_id": "cog.cognitive_load", "name": "Cognitive Load", "domain": "cog",
     "parent_id": "cog", "definition": "Mental effort required to process environmental information",
     "level": 2, "cognates": ["mental load", "mental effort", "information overload", "processing demand"],
     "operationalizations": ["NASA-TLX", "Dual-task paradigm", "Pupil dilation"]},
    
    {"term_id": "cog.place_recognition", "name": "Place Recognition", "domain": "cog",
     "parent_id": "cog.memory", "definition": "Ability to identify and remember locations",
     "level": 3, "cognates": ["landmark recognition", "place memory", "environmental familiarity"],
     "operationalizations": ["Scene recognition task", "Familiarity rating"]},
    
    # Affective — missing aesthetic/environmental emotions
    {"term_id": "affect.restorativeness", "name": "Perceived Restorativeness", "domain": "affect",
     "parent_id": "affect", "definition": "Subjective experience of mental resource recovery",
     "level": 2, "cognates": ["restorative quality", "restorative potential", "restorative experience"],
     "operationalizations": ["PRS (Perceived Restorativeness Scale)", "ROS (Restoration Outcome Scale)"]},
    
    {"term_id": "affect.place_attachment", "name": "Place Attachment", "domain": "affect",
     "parent_id": "affect", "definition": "Emotional bond between person and place",
     "level": 2, "cognates": ["sense of place", "place identity", "place dependence", "topophilia"],
     "operationalizations": ["Place Attachment Inventory", "Sense of Place Scale"]},
    
    {"term_id": "affect.aesthetic_pleasure", "name": "Aesthetic Pleasure", "domain": "affect",
     "parent_id": "affect", "definition": "Positive response to beauty and visual harmony",
     "level": 2, "cognates": ["beauty appreciation", "aesthetic experience", "visual pleasure", "aesthetic emotion"],
     "operationalizations": ["Aesthetic rating scale", "Semantic differential (beautiful-ugly)"]},
    
    {"term_id": "affect.fascination", "name": "Fascination", "domain": "affect",
     "parent_id": "affect", "definition": "Effortless attention capture by environmental features",
     "level": 2, "cognates": ["soft fascination", "captivation", "interest", "intrigue"],
     "operationalizations": ["Fascination subscale (PRS)", "Interest rating"]},
    
    {"term_id": "affect.mystery", "name": "Mystery", "domain": "affect",
     "parent_id": "affect", "definition": "Promise of further information if one explores deeper",
     "level": 2, "cognates": ["environmental mystery", "cognitive mystery", "exploration promise"],
     "operationalizations": ["Mystery subscale (PRS)", "Exploration willingness rating"]},
    
    {"term_id": "affect.safety_perception", "name": "Perceived Safety", "domain": "affect",
     "parent_id": "affect", "definition": "Subjective sense of security in an environment",
     "level": 2, "cognates": ["safety feeling", "perceived danger", "security", "threat perception"],
     "operationalizations": ["Safety perception scale", "Fear of crime survey"]},
    
    # Behavioral — missing wayfinding, exploration, dwelling
    {"term_id": "behav.wayfinding", "name": "Wayfinding Performance", "domain": "behav",
     "parent_id": "behav", "definition": "Ability to navigate through built environments",
     "level": 2, "cognates": ["navigation performance", "route finding", "orientation", "path selection"],
     "operationalizations": ["Completion time", "Wrong turns", "Distance traveled ratio"]},
    
    {"term_id": "behav.exploration", "name": "Exploration Behavior", "domain": "behav",
     "parent_id": "behav", "definition": "Voluntary movement and investigation of environments",
     "level": 2, "cognates": ["environmental exploration", "spatial exploration", "curiosity behavior"],
     "operationalizations": ["Distance walked", "Areas visited", "Dwell time distribution"]},
    
    {"term_id": "behav.dwell_time", "name": "Dwell Time", "domain": "behav",
     "parent_id": "behav", "definition": "Duration of voluntary staying in a location",
     "level": 2, "cognates": ["length of stay", "occupancy duration", "time spent"],
     "operationalizations": ["Time in zone (seconds)", "Stay/leave ratio"]},
    
    # Social — missing privacy, crowding, territoriality
    {"term_id": "social.privacy", "name": "Privacy", "domain": "social",
     "parent_id": "social", "definition": "Control over personal information and social access",
     "level": 2, "cognates": ["personal space", "visual privacy", "acoustic privacy"],
     "operationalizations": ["Privacy satisfaction scale", "Interruption frequency"]},
    
    {"term_id": "social.crowding", "name": "Perceived Crowding", "domain": "social",
     "parent_id": "social", "definition": "Negative evaluation of spatial density",
     "level": 2, "cognates": ["density perception", "overcrowding", "spatial density"],
     "operationalizations": ["Crowding scale", "Density preference rating"]},
    
    {"term_id": "social.belonging", "name": "Sense of Belonging", "domain": "social",
     "parent_id": "social", "definition": "Feeling of being accepted and included in a place",
     "level": 2, "cognates": ["environmental belonging", "inclusion", "community feeling"],
     "operationalizations": ["Belonging scale", "Community attachment"]},
    
    # Environmental perception — missing key constructs
    {"term_id": "env.complexity", "name": "Environmental Complexity", "domain": "env",
     "parent_id": "env", "definition": "Richness and variety of environmental elements",
     "level": 2, "cognates": ["visual complexity", "scene complexity", "information richness", "entropy"],
     "operationalizations": ["Fractal dimension", "Edge density", "Shannon entropy"]},
    
    {"term_id": "env.coherence", "name": "Environmental Coherence", "domain": "env",
     "parent_id": "env", "definition": "Orderliness and unity of environmental composition",
     "level": 2, "cognates": ["visual order", "unity", "harmony", "organization"],
     "operationalizations": ["Coherence rating", "Order scale"]},
    
    {"term_id": "env.enclosure", "name": "Enclosure", "domain": "env",
     "parent_id": "env", "definition": "Degree to which space is bounded by vertical surfaces",
     "level": 2, "cognates": ["containment", "openness", "boundedness", "volumetric quality"],
     "operationalizations": ["Vertical/horizontal surface ratio", "Sky visible fraction"]},
    
    {"term_id": "env.materiality", "name": "Material Quality", "domain": "env",
     "parent_id": "env", "definition": "Perception of surface materials and textures",
     "level": 2, "cognates": ["material warmth", "texture quality", "surface quality", "haptic quality"],
     "operationalizations": ["Material preference scale", "Semantic differential (warm-cold, rough-smooth)"]},
    
    {"term_id": "env.visual_access", "name": "Visual Access", "domain": "env",
     "parent_id": "env", "definition": "Extent of unobstructed visual field in environment",
     "level": 2, "cognates": ["view extent", "visibility", "openness", "prospect"],
     "operationalizations": ["Isovist area", "Visual field angle", "Sightline count"]},
    
    {"term_id": "env.acoustic_quality", "name": "Acoustic Quality", "domain": "env",
     "parent_id": "env", "definition": "Overall perception of sound environment",
     "level": 2, "cognates": ["soundscape quality", "acoustic comfort", "aural environment"],
     "operationalizations": ["Soundscape questionnaire", "Acoustic satisfaction scale"]},
    
    # Health — missing specific built-environment health outcomes
    {"term_id": "health.sick_building", "name": "Sick Building Symptoms", "domain": "health",
     "parent_id": "health", "definition": "Health symptoms attributed to building environment",
     "level": 2, "cognates": ["SBS", "building-related illness", "indoor environment symptoms"],
     "operationalizations": ["SBS symptom checklist", "MM-040 questionnaire"]},
    
    {"term_id": "health.circadian_health", "name": "Circadian Health", "domain": "health",
     "parent_id": "health", "definition": "Alignment of biological rhythms with environmental light",
     "level": 2, "cognates": ["circadian rhythm", "chronobiology", "light exposure health"],
     "operationalizations": ["Actigraphy", "Melatonin onset", "Sleep-wake timing"]},
    
    # Neural — missing specific architectural cognition neural measures
    {"term_id": "neural.reward", "name": "Neural Reward Response", "domain": "neural",
     "parent_id": "neural", "definition": "Activation of reward circuits to environmental stimuli",
     "level": 2, "cognates": ["dopaminergic response", "nucleus accumbens", "ventral striatum"],
     "operationalizations": ["fMRI reward ROI", "ERP reward positivity"]},
    
    {"term_id": "neural.default_mode", "name": "Default Mode Network Activity", "domain": "neural",
     "parent_id": "neural", "definition": "Activity in DMN during environmental experience",
     "level": 2, "cognates": ["DMN", "mind wandering", "self-referential", "resting state"],
     "operationalizations": ["fMRI DMN connectivity", "EEG alpha power"]},
]


def main():
    parser = argparse.ArgumentParser(description="Expand outcome vocabulary")
    parser.add_argument("--apply", action="store_true", help="Write expanded vocab")
    parser.add_argument("--report-only", action="store_true", help="Only generate report")
    args = parser.parse_args()
    
    # Load current vocab
    with open(VOCAB_PATH) as f:
        vocab = json.load(f)
    
    current_terms = vocab["terms"]
    current_ids = {t["term_id"] for t in current_terms}
    
    print(f"Current vocab: {len(current_terms)} terms")
    
    # Load unresolved
    with open(UNRESOLVED_PATH) as f:
        raw_entries = [json.loads(l) for l in f]
    
    unique_terms = list(set(r["raw_term"] for r in raw_entries))
    print(f"Unresolved queue: {len(raw_entries)} entries, {len(unique_terms)} unique terms")
    
    # Pass 1: Filter noise
    noise_terms = []
    clean_terms = []
    for t in unique_terms:
        if is_noise(t):
            noise_terms.append(t)
        else:
            clean_terms.append(t)
    
    print(f"\nPass 1 — Noise filtering:")
    print(f"  Noise removed: {len(noise_terms)} ({len(noise_terms)/len(unique_terms)*100:.0f}%)")
    print(f"  Clean remaining: {len(clean_terms)}")
    
    # Pass 2: Domain classification
    by_domain = defaultdict(list)
    for t in clean_terms:
        domains = classify_domain(t)
        primary = domains[0][0]
        by_domain[primary].append(t)
    
    print(f"\nPass 2 — Domain classification:")
    for domain, terms in sorted(by_domain.items()):
        print(f"  {domain}: {len(terms)} terms")
    
    # Pass 3: Fuzzy match against existing vocab
    matched = 0
    unmatched_relevant = []
    for t in clean_terms:
        matches = fuzzy_match(t, current_terms, threshold=0.65)
        if matches:
            matched += 1
        else:
            domains = classify_domain(t)
            if domains[0][0] != "unclassified":
                unmatched_relevant.append((t, domains[0][0]))
    
    print(f"\nPass 3 — Fuzzy matching:")
    print(f"  Matched to existing vocab: {matched}")
    print(f"  Unmatched but domain-relevant: {len(unmatched_relevant)}")
    
    # Pass 4: Propose new entries
    new_entries_to_add = []
    for entry in PROPOSED_NEW_TERMS:
        if entry["term_id"] not in current_ids:
            new_entries_to_add.append(entry)
    
    print(f"\nPass 4 — Proposed new canonical entries: {len(new_entries_to_add)}")
    for entry in new_entries_to_add:
        print(f"  + {entry['term_id']}: {entry['name']}")
        if entry.get("operationalizations"):
            print(f"    Ops: {', '.join(entry['operationalizations'][:2])}")
    
    # Generate report
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "current_vocab_size": len(current_terms),
        "unresolved_total": len(raw_entries),
        "unresolved_unique": len(unique_terms),
        "noise_filtered": len(noise_terms),
        "clean_remaining": len(clean_terms),
        "fuzzy_matched": matched,
        "unmatched_relevant": len(unmatched_relevant),
        "new_entries_proposed": len(new_entries_to_add),
        "projected_final_vocab_size": len(current_terms) + len(new_entries_to_add),
        "domain_distribution": {d: len(ts) for d, ts in by_domain.items()},
        "sample_noise": sorted(noise_terms)[:20],
        "sample_unmatched": [{"term": t, "domain": d} for t, d in unmatched_relevant[:30]],
        "new_entries": new_entries_to_add,
    }
    
    with open(OUTPUT_DIR / "expansion_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    # Also save the noise terms for reference
    with open(OUTPUT_DIR / "filtered_noise_terms.json", "w") as f:
        json.dump(sorted(noise_terms), f, indent=2)
    
    if args.report_only:
        print(f"\nReport saved to {OUTPUT_DIR}")
        return
    
    # Apply if requested
    if args.apply:
        # Add new terms
        for entry in new_entries_to_add:
            current_terms.append(entry)
        
        # Sort by term_id
        current_terms.sort(key=lambda t: t["term_id"])
        
        vocab["terms"] = current_terms
        vocab["version"] = "2.0.0"
        vocab["generated_at"] = datetime.now(timezone.utc).isoformat()
        
        with open(VOCAB_PATH, "w") as f:
            json.dump(vocab, f, indent=2)
        
        print(f"\n✅ Vocab updated: {len(current_terms)} terms (was {len(current_terms) - len(new_entries_to_add)})")
        
        # Re-run resolver on unresolved queue to drain
        resolved_count = 0
        remaining = []
        
        # Rebuild lookup including new terms
        lookup = {}
        for t in current_terms:
            lookup[t["name"].lower()] = t["term_id"]
            for c in t.get("cognates", []):
                lookup[c.lower()] = t["term_id"]
        
        for entry in raw_entries:
            raw = entry["raw_term"].lower().strip()
            if raw in lookup:
                resolved_count += 1
            elif is_noise(entry["raw_term"]):
                resolved_count += 1  # Filtered as noise
            else:
                # Try fuzzy match
                best = None
                best_score = 0
                for name, tid in lookup.items():
                    ratio = SequenceMatcher(None, raw, name).ratio()
                    if ratio > best_score:
                        best_score = ratio
                        best = tid
                
                if best_score >= 0.75:
                    resolved_count += 1
                else:
                    remaining.append(entry)
        
        # Write remaining unresolved
        with open(UNRESOLVED_PATH, "w") as f:
            for entry in remaining:
                f.write(json.dumps(entry) + "\n")
        
        print(f"Resolved from queue: {resolved_count} (noise + matched)")
        print(f"Remaining unresolved: {len(remaining)}")
    
    print(f"\n{'='*60}")
    print(f"VOCABULARY EXPANSION COMPLETE")
    print(f"{'='*60}")
    print(f"Current vocab: {len(current_terms)} terms")
    print(f"New entries proposed: {len(new_entries_to_add)}")
    print(f"Report: {OUTPUT_DIR / 'expansion_report.json'}")


if __name__ == "__main__":
    main()
