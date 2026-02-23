"""
Method Identification (Sprint 4b / Task 4b.5).

Preprocessing step that scans papers for measurement instruments and
presentation modalities before claim extraction.

Detects:
- Physiological biomarkers (cortisol, HRV, EDA, etc.)
- Neural imaging (EEG, fMRI, fNIRS)
- Self-report measures (STAI, PANAS, PRS, etc.)
- Presentation modalities (VR, photos, real building)
- Task types and state characterization

Flags:
- Uncharacterized methods for expert review
- Temporal alignment issues (e.g., cortisol sampled too early)
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict
import re

from src.methods.registry import MethodRegistry
from src.methods.task_ecology import (
    TaskClass,
    StateCharacterization,
    classify_task_from_text,
)


# =============================================================================
# KEYWORD PATTERNS FOR METHOD DETECTION
# =============================================================================

METHOD_KEYWORDS: Dict[str, List[str]] = {
    # Physiological biomarkers
    "salivary_cortisol": [
        "cortisol", "salivary", "hpa", "endocrine", "salivette"
    ],
    "hrv_frequency_domain": [
        "heart rate variability", "hrv", "hf-hrv", "lf/hf", "frequency domain",
        "spectral analysis"
    ],
    "hrv_time_domain": [
        "rmssd", "sdnn", "time domain hrv"
    ],
    "eda_scr": [
        "skin conductance response", "scr", "galvanic skin", "electrodermal",
        "gsr"
    ],
    "eda_scl": [
        "skin conductance level", "scl", "tonic eda"
    ],
    "blood_pressure": [
        "blood pressure", "systolic", "diastolic", "bp"
    ],

    # Neural imaging
    "eeg_frequency_bands": [
        "electroencephalog", "eeg", "alpha power", "theta", "beta",
        "erp", "p300", "frontal asymmetry"
    ],
    "fmri_bold": [
        "fmri", "bold", "functional magnetic", "functional mri"
    ],
    "fnirs": [
        "fnirs", "near-infrared", "nirs", "prefrontal oxygenation"
    ],

    # Behavioral
    "eye_tracking": [
        "eye track", "fixation", "saccade", "pupil", "gaze", "dwell time"
    ],

    # Self-report
    "self_report_stai": [
        "stai", "state-trait anxiety", "spielberger"
    ],
    "self_report_panas": [
        "panas", "positive and negative affect", "positive affect schedule"
    ],
    "self_report_prs": [
        "prs", "perceived restorativeness", "restoration scale"
    ],
    "self_report_preference": [
        "preference rating", "likert", "semantic differential",
        "visual analog", "rating scale"
    ],

    # Presentation modalities
    "photographs_2d": [
        "photograph", "photo", "image", "picture", "2d", "slide"
    ],
    "vr_hmd_stationary": [
        "vr", "virtual reality", "hmd", "head-mounted", "oculus", "vive",
        "stationary vr"
    ],
    "vr_hmd_room_scale": [
        "room-scale", "roomscale", "locomotion", "walking vr", "ambulatory vr"
    ],
    "vr_cave": [
        "cave", "cave2", "projection", "immersive projection"
    ],
    "real_building_controlled": [
        "real building", "actual building", "in situ", "field study",
        "real environment", "physical space"
    ],
}

# Temporal alignment warnings
TEMPORAL_CONSTRAINTS: Dict[str, Dict] = {
    "salivary_cortisol": {
        "min_post_stressor_minutes": 20,
        "warning": "cortisol_temporal_misalignment",
        "explanation": "Cortisol sampled < 20 min post-stressor measures baseline, not response"
    },
    "hrv_frequency_domain": {
        "min_recording_minutes": 5,
        "warning": "hrv_insufficient_duration",
        "explanation": "HRV frequency domain requires minimum 5 min recording"
    },
}


# =============================================================================
# RESULT DATACLASS
# =============================================================================

@dataclass
class MethodIdentificationResult:
    """
    Result of method identification from paper text.

    Provides all detected instruments, modalities, and flags.
    """
    instruments_found: List[Dict] = field(default_factory=list)
    presentation_modality: Optional[Dict] = None
    task_class: TaskClass = TaskClass.EXPLICIT_EVALUATION
    state_measured: StateCharacterization = field(default_factory=StateCharacterization)
    uncharacterized_methods: List[str] = field(default_factory=list)
    temporal_alignment_flags: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "instruments_found": self.instruments_found,
            "presentation_modality": self.presentation_modality,
            "task_class": self.task_class.value,
            "state_measured": self.state_measured.to_dict(),
            "uncharacterized_methods": self.uncharacterized_methods,
            "temporal_alignment_flags": self.temporal_alignment_flags,
        }


# =============================================================================
# IDENTIFICATION FUNCTIONS
# =============================================================================

def _find_method_matches(
    text: str,
    registry: Optional[MethodRegistry] = None
) -> List[Dict]:
    """
    Find all method keyword matches in text.

    Returns list of {method_id, confidence, matched_keywords}.
    """
    text_lower = text.lower()
    matches = []

    for method_id, keywords in METHOD_KEYWORDS.items():
        matched_keywords = [kw for kw in keywords if kw in text_lower]
        if matched_keywords:
            # Confidence based on number of keywords matched
            confidence = min(0.95, 0.5 + len(matched_keywords) * 0.15)

            match_info = {
                "method_id": method_id,
                "confidence": confidence,
                "matched_keywords": matched_keywords,
            }

            # Check if in registry
            if registry:
                entry = registry.get(method_id)
                if entry:
                    match_info["profile_status"] = entry.profile_status.value
                    match_info["construct_measured"] = entry.construct_measured

            matches.append(match_info)

    return matches


def _find_presentation_modality(matches: List[Dict]) -> Optional[Dict]:
    """
    Find the primary presentation modality from matches.

    Priority: real_building > vr_cave > vr_hmd_room_scale > vr_hmd_stationary > photographs
    """
    modality_priority = [
        "real_building_controlled",
        "vr_cave",
        "vr_hmd_room_scale",
        "vr_hmd_stationary",
        "photographs_2d",
    ]

    for modality_id in modality_priority:
        for match in matches:
            if match["method_id"] == modality_id:
                return match

    return None


def _detect_state_characterization(text: str) -> StateCharacterization:
    """
    Detect what participant states were measured/controlled.
    """
    text_lower = text.lower()
    state = StateCharacterization()

    # Affective state
    if any(kw in text_lower for kw in ["mood", "affect", "emotion", "panas", "stai"]):
        state.affective_state = 0.7 if "baseline" in text_lower else 0.3

    # Cognitive load
    if any(kw in text_lower for kw in ["cognitive load", "mental workload", "working memory"]):
        state.cognitive_load = 0.7

    # Goal urgency
    if any(kw in text_lower for kw in ["time pressure", "deadline", "urgency"]):
        state.goal_urgency = 0.7

    # Familiarity
    if any(kw in text_lower for kw in ["familiar", "novel", "first time", "prior experience"]):
        state.familiarity = 0.7

    # Physical state
    if any(kw in text_lower for kw in ["fatigue", "sleep", "caffeine", "exercise"]):
        state.physical_state = 0.7

    # Social context
    if any(kw in text_lower for kw in ["alone", "with others", "social", "companion"]):
        state.social_context = 0.7

    return state


def _check_temporal_alignment(
    text: str,
    methods_found: List[Dict]
) -> List[str]:
    """
    Check for temporal alignment issues between methods and protocols.
    """
    flags = []
    text_lower = text.lower()

    for method in methods_found:
        method_id = method["method_id"]

        if method_id in TEMPORAL_CONSTRAINTS:
            constraint = TEMPORAL_CONSTRAINTS[method_id]

            # Look for timing information
            if method_id == "salivary_cortisol":
                # Check for short exposure durations
                duration_patterns = [
                    r"(\d+)\s*min(?:ute)?s?\s*(?:exposure|session|vr)",
                    r"(\d+)\s*min(?:ute)?s?\s+vr",
                    r"exposure\s*(?:of|for)?\s*(\d+)\s*min",
                    r"(\d+)\s*-?\s*min(?:ute)?",  # More general pattern
                ]
                for pattern in duration_patterns:
                    match = re.search(pattern, text_lower)
                    if match:
                        duration = int(match.group(1))
                        if duration < constraint["min_post_stressor_minutes"]:
                            flags.append(constraint["warning"])
                            break

            elif method_id == "hrv_frequency_domain":
                # Check for insufficient recording duration
                if "2 min" in text_lower or "1 min" in text_lower:
                    flags.append(constraint["warning"])

    return flags


def _find_uncharacterized_methods(
    text: str,
    known_methods: List[str],
    registry: Optional[MethodRegistry] = None
) -> List[str]:
    """
    Find method-like terms that aren't in our known list.
    """
    uncharacterized = []
    text_lower = text.lower()

    # Generic biomarker patterns
    biomarker_patterns = [
        r"salivary\s+(\w+)",
        r"(\w+)\s+biomarker",
        r"(\w+)\s+assay",
    ]

    for pattern in biomarker_patterns:
        matches = re.findall(pattern, text_lower)
        for match in matches:
            if match not in known_methods and len(match) > 3:
                if match not in uncharacterized:
                    uncharacterized.append(match)

    # Filter out common false positives
    false_positives = {"the", "and", "for", "with", "from", "were", "was"}
    uncharacterized = [u for u in uncharacterized if u not in false_positives]

    return uncharacterized


def identify_methods(
    paper_text: str,
    registry: Optional[MethodRegistry] = None
) -> MethodIdentificationResult:
    """
    Scan paper text for measurement instruments and presentation modalities.

    This preprocessing step runs before claim extraction to:
    1. Identify all instruments used
    2. Determine presentation modality
    3. Classify task type
    4. Assess state characterization
    5. Flag uncharacterized methods
    6. Check temporal alignment

    Args:
        paper_text: Full paper text (or Methods section)
        registry: Optional MethodRegistry for status lookup

    Returns:
        MethodIdentificationResult with all detected information

    Example:
        >>> text = "We measured salivary cortisol using Salivettes..."
        >>> result = identify_methods(text)
        >>> assert any(m["method_id"] == "salivary_cortisol" for m in result.instruments_found)
    """
    # Find all method matches
    all_matches = _find_method_matches(paper_text, registry)

    # Separate instruments from presentation modalities
    presentation_ids = {
        "photographs_2d", "vr_hmd_stationary", "vr_hmd_room_scale",
        "vr_cave", "real_building_controlled"
    }
    instruments = [m for m in all_matches if m["method_id"] not in presentation_ids]

    # Find primary presentation modality
    presentation_modality = _find_presentation_modality(all_matches)

    # Classify task type
    task_class = classify_task_from_text(paper_text)

    # Detect state characterization
    state_measured = _detect_state_characterization(paper_text)

    # Check temporal alignment
    temporal_flags = _check_temporal_alignment(paper_text, instruments)

    # Find uncharacterized methods
    known_method_ids = list(METHOD_KEYWORDS.keys())
    uncharacterized = _find_uncharacterized_methods(paper_text, known_method_ids, registry)

    return MethodIdentificationResult(
        instruments_found=instruments,
        presentation_modality=presentation_modality,
        task_class=task_class,
        state_measured=state_measured,
        uncharacterized_methods=uncharacterized,
        temporal_alignment_flags=temporal_flags,
    )
