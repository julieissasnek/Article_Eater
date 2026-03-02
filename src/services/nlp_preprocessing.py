"""
nlp_preprocessing.py — NLP Preprocessing for IV/DV Classifier
================================================================

Expert Panel Guidance:
  - NLP Specialist (#12): "Lemmatize, expand abbreviations, detect multi-word entities"
  - ML Expert (#11): "Active learning loop for classifier improvement"

Provides:
  1. Lemmatization (lighting conditions → lighting condition)
  2. Abbreviation expansion (IAQ → indoor air quality, CCT → correlated color temperature)
  3. Text normalization (stripping units, parentheticals, etc.)
"""

import re
from typing import Optional


# ============================================================================
# Abbreviation Dictionary
# ============================================================================

_ABBREVIATIONS = {
    # Environmental Quality
    "iaq": "indoor air quality",
    "ieq": "indoor environmental quality",
    "sbs": "sick building syndrome",
    "bri": "building related illness",
    "pmv": "predicted mean vote",
    "ppd": "predicted percentage dissatisfied",
    "aqhi": "air quality health index",

    # Lighting
    "cct": "correlated color temperature",
    "cri": "color rendering index",
    "spd": "spectral power distribution",
    "edi": "equivalent daylight illuminance",
    "uf": "utilization factor",
    "dgp": "daylight glare probability",
    "dgi": "daylight glare index",
    "ugr": "unified glare rating",

    # Acoustics
    "spl": "sound pressure level",
    "sti": "speech transmission index",
    "nc": "noise criteria",
    "nrc": "noise reduction coefficient",
    "rt60": "reverberation time",
    "snr": "signal to noise ratio",

    # Thermal
    "hvac": "heating ventilation air conditioning",
    "ashrae": "american society of heating refrigerating air conditioning engineers",
    "tmrt": "mean radiant temperature",

    # Cognitive/Psychological
    "scl": "skin conductance level",
    "scr": "skin conductance response",
    "emg": "electromyography",
    "eeg": "electroencephalography",
    "ecg": "electrocardiography",
    "hrv": "heart rate variability",
    "eda": "electrodermal activity",
    "gsr": "galvanic skin response",
    "prs": "perceived restorativeness scale",
    "svs": "subjective vitality scale",
    "panas": "positive and negative affect schedule",
    "kss": "karolinska sleepiness scale",
    "vas": "visual analogue scale",
    "sam": "self assessment manikin",
    "stai": "state trait anxiety inventory",
    "psqi": "pittsburgh sleep quality index",

    # Research Design
    "rct": "randomized controlled trial",
    "anova": "analysis of variance",
    "sem": "structural equation modeling",
    "mlm": "multilevel modeling",
    "ci": "confidence interval",

    # Biophilia
    "art": "attention restoration theory",
    "srt": "stress reduction theory",
    "pvs": "perceived visual scale",

    # Instruments & Scales
    "nasa-tlx": "nasa task load index",
    "tlx": "task load index",
    "poms": "profile of mood states",
    "bus": "building use studies",
    "poe": "post occupancy evaluation",
    "pss": "perceived stress scale",
    "moca": "montreal cognitive assessment",
    "wais": "wechsler adult intelligence scale",
    "mos": "medical outcomes study",
    "act": "attentional control theory",
    "swb": "subjective well-being",

    # Building Standards
    "leed": "leadership in energy and environmental design",
    "breeam": "building research establishment environmental assessment method",
    "well": "well building standard",

    # Neuroimaging
    "fmri": "functional magnetic resonance imaging",
    "meg": "magnetoencephalography",
    "tms": "transcranial magnetic stimulation",
    "cbt": "correlated body temperature",

    # Organizations
    "who": "world health organization",

    # Units (common in findings)
    "lux": "lux",
    "cd/m2": "candela per square meter",
    "db": "decibel",
    "dba": "a-weighted decibel",
    "pa": "pascal",
}


# ============================================================================
# Lemmatization (lightweight, no external deps)
# ============================================================================

# Common suffix rules for simple lemmatization
_LEMMA_RULES = [
    (r"(\w+)ies$", r"\1y"),        # properties → property
    (r"(\w+)ses$", r"\1s"),        # analyses → analysis (keep s)
    (r"(\w{3,})s$", r"\1"),        # conditions → condition
    (r"(\w+)ness$", r"\1"),        # brightness → bright
    (r"(\w+)ment$", r"\1"),        # improvement → improve
    (r"(\w+)tion$", r"\1te"),      # stimulation → stimulate
    (r"(\w+)ated$", r"\1ate"),     # correlated → correlate
    (r"(\w+)ing$", r"\1"),         # lighting → light
    (r"(\w+)ed$", r"\1"),          # increased → increase
]


def lemmatize_token(word: str) -> str:
    """Simple rule-based lemmatization for a single word."""
    w = word.lower().strip()
    if len(w) <= 3:
        return w
    for pattern, replacement in _LEMMA_RULES:
        result = re.sub(pattern, replacement, w)
        if result != w and len(result) >= 3:
            return result
    return w


def lemmatize_text(text: str) -> str:
    """Lemmatize all words in a text while preserving structure."""
    tokens = re.findall(r'\b\w+\b', text.lower())
    lemmatized = [lemmatize_token(t) for t in tokens]
    return " ".join(lemmatized)


# ============================================================================
# Abbreviation Expansion
# ============================================================================

def expand_abbreviations(text: str) -> str:
    """
    Expand known abbreviations in text.

    'High CCT (6500K)' → 'High correlated color temperature (6500K)'
    'IAQ improvement' → 'indoor air quality improvement'
    """
    result = text
    # Create pattern for word-boundary matching
    for abbr, expansion in _ABBREVIATIONS.items():
        # Match abbreviation as a whole word (case-insensitive)
        pattern = re.compile(r'\b' + re.escape(abbr) + r'\b', re.IGNORECASE)
        result = pattern.sub(expansion, result)
    return result


# ============================================================================
# Text Normalization
# ============================================================================

def normalize_iv_text(text: str) -> str:
    """
    Normalize an IV (antecedent) text for better classification.

    Steps:
      1. Expand abbreviations
      2. Strip parenthetical values (preserve for attributes)
      3. Normalize whitespace
      4. Lowercase

    Returns the normalized text.
    """
    if not text or not isinstance(text, str):
        return ""

    normalized = text.strip()

    # Step 1: Expand abbreviations
    normalized = expand_abbreviations(normalized)

    # Step 2: Normalize whitespace
    normalized = re.sub(r'\s+', ' ', normalized)

    # Step 3: Lowercase
    normalized = normalized.lower().strip()

    return normalized


def extract_parenthetical_values(text: str) -> dict:
    """
    Extract numeric values from parentheticals.

    'High CCT (6500K)' → {'value': 6500, 'unit': 'K'}
    'Noise Level (65 dBA)' → {'value': 65, 'unit': 'dBA'}
    """
    values = {}

    # Pattern: (NUMBER UNIT)
    m = re.search(r'\((\d+\.?\d*)\s*(K|°C|°F|lux|dBA?|Hz|%|cd/m2|Pa|ppm)\)', text, re.I)
    if m:
        values["value"] = float(m.group(1))
        values["unit"] = m.group(2)

    # Pattern: (NUMBER-NUMBER UNIT) for ranges
    m = re.search(r'\((\d+\.?\d*)\s*[-–]\s*(\d+\.?\d*)\s*(K|°C|°F|lux|dBA?|Hz|%)\)', text, re.I)
    if m:
        values["range_low"] = float(m.group(1))
        values["range_high"] = float(m.group(2))
        values["unit"] = m.group(3)

    return values
