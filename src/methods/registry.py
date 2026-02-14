"""
Method Registry (Sprint 4b / Task 4b.1).

Data structure for profiling measurement instruments and presentation modalities.
Each entry contains temporal dynamics, confound structure, construct validity maps,
and VR-specific threats.

References:
- Methodological_Validity_Framework_Tier2b_V1.0.docx
- Ecological_Validity_CNFA_Background_Notes_V1.0.docx
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, List
from enum import Enum
from datetime import datetime


# =============================================================================
# ENUMS
# =============================================================================

class MethodType(str, Enum):
    """Type of measurement method or presentation modality."""
    PHYSIOLOGICAL_BIOMARKER = "physiological_biomarker"
    NEURAL_IMAGING = "neural_imaging"
    BEHAVIORAL_MEASURE = "behavioral_measure"
    SELF_REPORT = "self_report"
    PRESENTATION_MODALITY = "presentation_modality"
    EXPERIMENTAL_DESIGN = "experimental_design"


class MovementCompatibility(str, Enum):
    """Whether the method is compatible with participant movement."""
    YES = "yes"           # Works during movement
    CONFOUNDED = "confounded"  # Works but movement introduces confounds
    NO = "no"             # Cannot be used during movement


class ProfileStatus(str, Enum):
    """Characterization status of the method profile."""
    WELL_CHARACTERIZED = "well_characterized"
    PARTIALLY_CHARACTERIZED = "partially_characterized"
    UNCHARACTERIZED = "uncharacterized"


# =============================================================================
# METHOD ENTRY DATACLASS
# =============================================================================

@dataclass
class MethodEntry:
    """
    Complete profile for a measurement instrument or presentation modality.

    Captures temporal dynamics, confound structure, and construct validity
    for use in automated challenge generation and validity scoring.
    """
    method_id: str
    method_type: MethodType
    construct_measured: str

    # Temporal characteristics
    temporal_onset: Optional[str] = None      # e.g., "15-20 min"
    temporal_peak: Optional[str] = None       # e.g., "20-40 min"
    temporal_recovery: Optional[str] = None   # e.g., "40-60 min"
    minimum_sampling_window: Optional[str] = None  # e.g., "20 min post-stressor"

    # Spatial characteristics (for imaging)
    spatial_resolution: Optional[str] = None  # e.g., "centimeters"

    # Confound structure
    confounds: List[str] = field(default_factory=list)
    vr_specific_confounds: List[str] = field(default_factory=list)

    # Measurement characteristics
    valence_sensitivity: bool = False  # Can distinguish positive/negative
    movement_compatible: MovementCompatibility = MovementCompatibility.CONFOUNDED

    # Construct validity map: {construct_name: validity_score}
    # Score in [0, 1] indicating how well this method measures that construct
    construct_validity_map: Dict[str, float] = field(default_factory=dict)

    # Hardware variants (for physiological measures)
    hardware_variants: List[dict] = field(default_factory=list)

    # Registry metadata
    first_encountered: Optional[str] = None  # Date string
    profile_status: ProfileStatus = ProfileStatus.UNCHARACTERIZED
    evidence_count: int = 0
    last_updated: Optional[str] = None

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "method_id": self.method_id,
            "method_type": self.method_type.value,
            "construct_measured": self.construct_measured,
            "temporal_onset": self.temporal_onset,
            "temporal_peak": self.temporal_peak,
            "temporal_recovery": self.temporal_recovery,
            "minimum_sampling_window": self.minimum_sampling_window,
            "spatial_resolution": self.spatial_resolution,
            "confounds": self.confounds,
            "vr_specific_confounds": self.vr_specific_confounds,
            "valence_sensitivity": self.valence_sensitivity,
            "movement_compatible": self.movement_compatible.value,
            "construct_validity_map": self.construct_validity_map,
            "hardware_variants": self.hardware_variants,
            "first_encountered": self.first_encountered,
            "profile_status": self.profile_status.value,
            "evidence_count": self.evidence_count,
            "last_updated": self.last_updated,
        }

    def get_construct_validity(self, construct: str) -> float:
        """Get validity score for a specific construct, 0.0 if not mapped."""
        return self.construct_validity_map.get(construct, 0.0)

    def has_vr_confounds(self) -> bool:
        """Check if this method has VR-specific confounds."""
        return len(self.vr_specific_confounds) > 0

    def requires_minimum_duration(self) -> Optional[str]:
        """Return minimum sampling window if specified."""
        return self.minimum_sampling_window


# =============================================================================
# METHOD REGISTRY CLASS
# =============================================================================

class MethodRegistry:
    """
    Queryable registry of measurement instruments and presentation modalities.

    The registry is NOT static — it learns as new papers are processed.
    New/unknown methods are flagged as UNCHARACTERIZED for expert profiling.
    """

    def __init__(self):
        self._entries: Dict[str, MethodEntry] = {}

    def add(self, entry: MethodEntry) -> None:
        """Add or update a method entry."""
        if entry.last_updated is None:
            entry.last_updated = datetime.now().isoformat()
        self._entries[entry.method_id] = entry

    def get(self, method_id: str) -> Optional[MethodEntry]:
        """Retrieve a method by ID."""
        return self._entries.get(method_id)

    def find_by_type(self, method_type: MethodType) -> List[MethodEntry]:
        """Find all methods of a given type."""
        return [e for e in self._entries.values() if e.method_type == method_type]

    def find_by_construct(self, construct: str, min_validity: float = 0.5) -> List[MethodEntry]:
        """Find methods that validly measure a given construct."""
        return [
            e for e in self._entries.values()
            if e.get_construct_validity(construct) >= min_validity
        ]

    def list_uncharacterized(self) -> List[MethodEntry]:
        """List all methods flagged as uncharacterized."""
        return [
            e for e in self._entries.values()
            if e.profile_status == ProfileStatus.UNCHARACTERIZED
        ]

    def list_well_characterized(self) -> List[MethodEntry]:
        """List all well-characterized methods."""
        return [
            e for e in self._entries.values()
            if e.profile_status == ProfileStatus.WELL_CHARACTERIZED
        ]

    def update_evidence_count(self, method_id: str) -> None:
        """Increment evidence count when method is encountered in a paper."""
        if method_id in self._entries:
            self._entries[method_id].evidence_count += 1
            self._entries[method_id].last_updated = datetime.now().isoformat()

    def flag_as_uncharacterized(self, method_id: str, construct: str) -> MethodEntry:
        """Create a placeholder entry for an unknown method."""
        entry = MethodEntry(
            method_id=method_id,
            method_type=MethodType.BEHAVIORAL_MEASURE,  # Default, can be updated
            construct_measured=construct,
            profile_status=ProfileStatus.UNCHARACTERIZED,
            first_encountered=datetime.now().isoformat(),
        )
        self.add(entry)
        return entry

    def all_entries(self) -> List[MethodEntry]:
        """Return all entries in the registry."""
        return list(self._entries.values())

    def count(self) -> int:
        """Return total number of entries."""
        return len(self._entries)

    def to_dict(self) -> dict:
        """Serialize entire registry."""
        return {
            "entries": [e.to_dict() for e in self._entries.values()],
            "total_count": self.count(),
            "uncharacterized_count": len(self.list_uncharacterized()),
        }
