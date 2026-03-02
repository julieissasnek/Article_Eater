#!/usr/bin/env python3
"""
link_local.py — Pattern-based theory/molecule/instrument linking (NO API)
==========================================================================

Links extractions to theories/molecules using keyword matching from
existing extraction text. Much faster than API calls (seconds vs hours).

For each extraction:
  1. Scan findings text for theory keywords → theory_links
  2. Scan findings text for molecule keywords → molecule_ids
  3. Detect measurement instruments from methodology fields → instruments

Success conditions:
  SC-1: ≥400/801 extractions get theory_links
  SC-2: ≥100/801 extractions get molecule_ids
  SC-3: ≥300/801 extractions get instruments
  SC-4: No data corruption (all files valid JSON after)
"""

import json
import re
import sys
import logging
from pathlib import Path
from datetime import datetime, timezone

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

EXTRACTIONS_DIR = PROJECT_ROOT / "data" / "extractions"
THEORIES_DIR = PROJECT_ROOT / "data" / "theories"
MOLECULES_DIR = PROJECT_ROOT / "data" / "molecules"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
    handlers=[
        logging.FileHandler("/tmp/link_local.log"),
        logging.StreamHandler(),
    ]
)
log = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════
# Build keyword indexes from theory/molecule JSON
# ═══════════════════════════════════════════════════════════════════

def build_theory_index():
    """Build {theory_id: [keywords]} from theory JSON files."""
    index = {}
    for tf in THEORIES_DIR.glob("*.json"):
        try:
            t = json.load(open(tf))
            tid = tf.stem
            keywords = set()
            
            # From explicit keywords
            for kw in t.get("keywords", []):
                keywords.add(kw.lower())
            
            # From name (split on spaces)
            name = t.get("name", tid)
            keywords.add(name.lower())
            for word in name.lower().replace("_", " ").replace("-", " ").split():
                if len(word) > 3:
                    keywords.add(word)
            
            # From originator
            orig = t.get("originator", "")
            if orig and len(orig) > 3:
                keywords.add(orig.lower())
            
            # From description (extract key phrases)
            desc = t.get("description", "")
            if desc:
                # Add main noun phrases
                for phrase in re.findall(r'\b([A-Z][a-z]+(?:\s+[a-z]+){0,2})\b', desc):
                    if len(phrase) > 5:
                        keywords.add(phrase.lower())
            
            # Theory-specific aliases
            aliases = THEORY_ALIASES.get(tid, [])
            for a in aliases:
                keywords.add(a.lower())
            
            index[tid] = list(keywords)
        except Exception as e:
            import logging; logging.getLogger(__name__).debug(f"Non-critical: {e}")
    return index


# Manual aliases for theories that are often referenced by different names
THEORY_ALIASES = {
    "biophilia": ["biophilic", "nature preference", "biophilia hypothesis", "wilson"],
    "prospect_refuge": ["prospect-refuge", "appleton", "prospect and refuge", "vista", "visual refuge"],
    "processing_fluency": ["fluency", "perceptual fluency", "disfluency", "processing ease"],
    "berlyne_arousal": ["berlyne", "arousal potential", "hedonic tone", "collative variables", "optimal arousal"],
    "predictive_coding_music": ["predictive coding", "prediction error", "expectancy violation", "musical expectation"],
    "allesthesia": ["alliesthesia", "cabanac", "pleasant sensation"],
    "brecvema": ["chills", "musical emotion", "frisson", "ITPRA"],
    "art": ["attention restoration", "ART", "kaplan", "restorative environment", "directed attention fatigue"],
    "srt": ["stress recovery", "stress reduction", "Ulrich", "psychophysiological stress"],
    "soundscape": ["acoustic ecology", "sound environment", "noise annoyance", "sound quality"],
    "space_syntax": ["spatial configuration", "visibility graph", "axial map", "Hillier"],
    "auditory_scene_analysis": ["ASA", "bregman", "auditory streaming", "auditory grouping"],
    "adaptive_thermal": ["thermal comfort", "adaptive comfort", "ASHRAE", "PMV", "thermal adaptation"],
    "chronobiology": ["circadian", "circadian rhythm", "melatonin", "light-dark cycle"],
    "cognitive_map": ["cognitive mapping", "mental map", "spatial cognition", "wayfinding"],
    "cpted": ["crime prevention", "defensible space", "natural surveillance", "territorial"],
    "episodic_memory": ["episodic", "autobiographical memory", "place memory"],
    "flow_theory": ["flow state", "csikszentmihalyi", "optimal experience", "autotelic"],
    "goldilocks_principle": ["goldilocks", "not too much", "optimal level", "inverted U"],
    "kaplan_preference": ["preference matrix", "mystery", "complexity", "coherence", "legibility"],
    "pad_model": ["pleasure arousal dominance", "PAD", "mehrabian", "emotional space"],
    "place_attachment": ["place identity", "sense of place", "place bonding", "topophilia"],
    "privacy_regulation": ["privacy", "altman", "personal space", "crowding"],
    "proxemics": ["proxemic", "interpersonal distance", "hall", "social distance", "personal space"],
}


def build_molecule_index():
    """Build {molecule_id: [keywords]} from molecule JSON files."""
    index = {}
    for mf in MOLECULES_DIR.glob("*.json"):
        try:
            m = json.load(open(mf))
            mid = mf.stem
            keywords = set()
            
            name = m.get("name", mid)
            keywords.add(name.lower())
            for word in name.lower().replace("_", " ").replace("-", " ").split():
                if len(word) > 3:
                    keywords.add(word)
            
            # From description
            desc = m.get("description", "")
            for word in desc.lower().split()[:20]:
                if len(word) > 5:
                    keywords.add(word.strip(".,;:"))
            
            # From source theories
            for st in m.get("source_theories", []):
                keywords.add(st.lower())
            
            index[mid] = list(keywords)
        except Exception as e:
            import logging; logging.getLogger(__name__).debug(f"Non-critical: {e}")
    return index


# Instrument detection patterns
INSTRUMENT_PATTERNS = {
    "fMRI": re.compile(r'\bf?MRI\b|functional\s+magnetic|BOLD', re.I),
    "EEG": re.compile(r'\bEEG\b|electroencephalogra', re.I),
    "eye_tracking": re.compile(r'eye[\s-]*track|gaze\s+fixat|saccad|pupillom', re.I),
    "skin_conductance": re.compile(r'skin\s+conductance|galvanic|EDA|electrodermal', re.I),
    "heart_rate": re.compile(r'heart\s+rate|HR\s+variab|HRV|cardio', re.I),
    "cortisol": re.compile(r'cortisol|salivary\s+sample', re.I),
    "questionnaire": re.compile(r'questionnaire|self[\s-]*report|Likert|survey\s+instrument', re.I),
    "behavioral": re.compile(r'reaction\s+time|response\s+time|button\s+press|forced[\s-]*choice', re.I),
    "psychophysical": re.compile(r'psychophysi|threshold|just[\s-]*noticeable|Weber', re.I),
    "VR": re.compile(r'virtual\s+realit|VR\s+headset|immersive|HMD', re.I),
    "photometry": re.compile(r'photometr|lux\s+meter|illuminance\s+sensor|spectroradiom', re.I),
    "thermal_sensor": re.compile(r'thermometer|thermal\s+sensor|globe\s+temperature|PMV\s+calculation', re.I),
    "sound_level_meter": re.compile(r'sound\s+level|decibel\s+meter|acoustic\s+measur|noise\s+dosimeter', re.I),
    "accelerometer": re.compile(r'acceleromet|motion\s+sensor|actigraph|pedometer', re.I),
    "post_occupancy": re.compile(r'post[\s-]*occupancy|POE|building\s+performance\s+eval', re.I),
    "GIS": re.compile(r'\bGIS\b|geographic\s+information|spatial\s+analysis', re.I),
    "isovist": re.compile(r'\bisovist|visual\s+field|visibility\s+graph|space\s+syntax\s+tool', re.I),
    "computational_model": re.compile(r'simulation|computational\s+model|agent[\s-]*based|Monte\s+Carlo', re.I),
}


def extract_text(data: dict) -> str:
    """Combine all searchable text from an extraction."""
    parts = []
    parts.append(data.get("title", ""))
    parts.append(data.get("abstract", ""))
    
    for f in data.get("findings", []):
        parts.append(str(f.get("antecedent", "")))
        parts.append(str(f.get("consequent", "")))
        parts.append(str(f.get("summary", "")))
        parts.append(str(f.get("methodology", "")))
        for tl in f.get("theory_links", []):
            parts.append(str(tl))
    
    constructs = data.get("constructs", {})
    for key in ["outcomes", "mechanisms", "moderators"]:
        for item in constructs.get(key, []):
            parts.append(str(item))
    
    return " ".join(parts).lower()


def match_theories(text: str, theory_index: dict) -> list:
    """Find matching theories based on keyword presence."""
    matches = []
    for tid, keywords in theory_index.items():
        score = 0
        for kw in keywords:
            if kw in text:
                score += 1
        if score >= 2:  # Need at least 2 keyword matches
            matches.append(tid)
    return matches


def match_molecules(text: str, molecule_index: dict) -> list:
    """Find matching molecules based on keyword presence."""
    matches = []
    for mid, keywords in molecule_index.items():
        score = 0
        for kw in keywords:
            if kw in text:
                score += 1
        if score >= 2:
            matches.append(mid)
    return matches


def detect_instruments(text: str) -> list:
    """Detect measurement instruments from text."""
    found = []
    for instrument, pattern in INSTRUMENT_PATTERNS.items():
        if pattern.search(text):
            found.append(instrument)
    return found


def main():
    log.info("=== LOCAL PATTERN-BASED LINKING ===")
    
    theory_index = build_theory_index()
    molecule_index = build_molecule_index()
    log.info(f"Theory index: {len(theory_index)} theories, {sum(len(v) for v in theory_index.values())} keywords")
    log.info(f"Molecule index: {len(molecule_index)} molecules, {sum(len(v) for v in molecule_index.values())} keywords")
    
    files = sorted(EXTRACTIONS_DIR.glob("10.*.json"))
    log.info(f"Processing {len(files)} extractions")
    
    with_theories = 0
    with_molecules = 0
    with_instruments = 0
    updated = 0
    errors = 0
    
    for i, ef in enumerate(files):
        try:
            data = json.load(open(ef))
            
            if not data.get("findings"):
                continue
            
            text = extract_text(data)
            changed = False
            
            # Theory linking
            if not data.get("theory_links"):
                theories = match_theories(text, theory_index)
                if theories:
                    data["theory_links"] = theories
                    changed = True
                    with_theories += 1
            else:
                with_theories += 1  # Already had them
            
            # Molecule linking
            if not data.get("molecule_ids"):
                molecules = match_molecules(text, molecule_index)
                if molecules:
                    data["molecule_ids"] = molecules
                    changed = True
                    with_molecules += 1
            else:
                with_molecules += 1
            
            # Instrument detection
            if not data.get("instruments"):
                instruments = detect_instruments(text)
                if instruments:
                    data["instruments"] = instruments
                    changed = True
                    with_instruments += 1
            else:
                with_instruments += 1
            
            if changed:
                data["linked_date"] = datetime.now(timezone.utc).isoformat()
                data["linking_method"] = "local_pattern_v1"
                with open(ef, "w") as f:
                    json.dump(data, f, indent=2)
                updated += 1
                
        except Exception as e:
            errors += 1
            log.error(f"Error processing {ef.stem}: {e}")
        
        if (i + 1) % 100 == 0:
            log.info(f"  Progress: {i+1}/{len(files)} ({with_theories} theories, {with_molecules} molecules)")
    
    total = len(files)
    # Success conditions
    log.info(f"\n{'='*60}")
    log.info(f"  LOCAL LINKING RESULTS")
    log.info(f"{'='*60}")
    log.info(f"  Total extractions: {total}")
    log.info(f"  Updated: {updated}")
    log.info(f"  With theory_links: {with_theories} ({100*with_theories//total}%)")
    log.info(f"  With molecule_ids: {with_molecules} ({100*with_molecules//total}%)")
    log.info(f"  With instruments: {with_instruments} ({100*with_instruments//total}%)")
    log.info(f"  Errors: {errors}")
    
    sc1 = with_theories >= 400
    sc2 = with_molecules >= 100
    sc3 = with_instruments >= 300
    sc4 = errors == 0
    log.info(f"  SC-1 (≥400 with theory_links): {'✓' if sc1 else '✗'} ({with_theories})")
    log.info(f"  SC-2 (≥100 with molecule_ids): {'✓' if sc2 else '✗'} ({with_molecules})")
    log.info(f"  SC-3 (≥300 with instruments):  {'✓' if sc3 else '✗'} ({with_instruments})")
    log.info(f"  SC-4 (0 errors):               {'✓' if sc4 else '✗'} ({errors})")
    log.info(f"{'='*60}")
    
    # Write progress
    progress = {
        "status": "complete",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "method": "local_pattern_v1",
        "total": total,
        "updated": updated,
        "with_theories": with_theories,
        "with_molecules": with_molecules,
        "with_instruments": with_instruments,
        "errors": errors,
        "success_conditions": {
            "sc1_theories_400": sc1,
            "sc2_molecules_100": sc2,
            "sc3_instruments_300": sc3,
            "sc4_no_errors": sc4,
        }
    }
    with open(EXTRACTIONS_DIR / "linking_progress.json", "w") as f:
        json.dump(progress, f, indent=2)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
