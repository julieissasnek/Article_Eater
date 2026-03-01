"""
cva_annotations.py — CVA Annotation Types for QA (Phase 5)
============================================================

Annotation types for measurement modality, stimulus description,
and molecule/template linkage. These wire CVA data into the
existing QA/template preprocessing pipeline.

Reference: AG_ASSIGNMENT Phase 5, Tasks 5.1–5.6
ADR-001: Extension layer — new file, no existing code modified.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional
import json


class AnnotationType(Enum):
    """CVA annotation types for templates and findings."""
    # Phase 5 original types (A1-A5)
    MEASUREMENT_MODALITY = "measurement_modality"
    STIMULUS_DESCRIPTION = "stimulus_description"
    MOLECULE_T15_LINK = "molecule_t15_link"
    CVA_CONSTRAINT_TAG = "cva_constraint_tag"
    CVA_VALUATION_TAG = "cva_valuation_tag"
    # Phase 6 expansion types (A9-A18)
    SURPRISE_FLAG = "surprise_flag"                 # A9
    DESIGN_IMPLICATION = "design_implication"        # A10
    DISPUTE = "dispute"                              # A11
    ANALOGICAL_BRIDGE = "analogical_bridge"          # A12
    REPLICATION_STATUS = "replication_status"         # A13
    EFFECT_MAGNITUDE = "effect_magnitude"             # A14
    CROSS_DOMAIN = "cross_domain"                    # A15
    HISTORICAL_CONTEXT = "historical_context"         # A16
    NARRATIVE_HOOK = "narrative_hook"                 # A17
    UNANSWERED_QUESTION = "unanswered_question"      # A18
    # Phase 5 Task 5.1: Additional scope types
    NEUROTYPE_RELEVANCE = "neurotype_relevance"       # Which ψ_neuro profiles apply
    CULTURAL_SCOPE = "cultural_scope"                 # Which ψ_culture profiles tested


class MeasurementModality(Enum):
    """How a finding was measured."""
    FMRI = "fMRI"
    EEG = "EEG"
    MEG = "MEG"
    BEHAVIORAL = "behavioral"
    PSYCHOPHYSICAL = "psychophysical"
    SELF_REPORT = "self_report"
    EYE_TRACKING = "eye_tracking"
    SKIN_CONDUCTANCE = "skin_conductance"
    HEART_RATE = "heart_rate"
    COMPUTATIONAL_MODEL = "computational_model"
    OBSERVATIONAL = "observational"
    MIXED = "mixed"


class StimulusType(Enum):
    """Type of stimulus used in study."""
    VISUAL_STATIC = "visual_static"
    VISUAL_DYNAMIC = "visual_dynamic"
    AUDITORY = "auditory"
    MULTISENSORY = "multisensory"
    SPATIAL = "spatial"
    SOCIAL = "social"
    NARRATIVE = "narrative"
    ARCHITECTURAL = "architectural"
    NATURAL_SCENE = "natural_scene"
    ABSTRACT = "abstract"


@dataclass
class MeasurementAnnotation:
    """Annotate a finding/template with measurement modality."""
    modality: MeasurementModality
    spatial_resolution: Optional[str] = None  # e.g., "~3mm" for fMRI
    temporal_resolution: Optional[str] = None  # e.g., "~1ms" for EEG
    sample_size: Optional[int] = None
    population: Optional[str] = None  # e.g., "neurotypical adults"
    confidence: float = 0.8

    def to_dict(self) -> Dict:
        return {
            "type": AnnotationType.MEASUREMENT_MODALITY.value,
            "modality": self.modality.value,
            "spatial_resolution": self.spatial_resolution,
            "temporal_resolution": self.temporal_resolution,
            "sample_size": self.sample_size,
            "population": self.population,
            "confidence": self.confidence,
        }


@dataclass
class StimulusAnnotation:
    """Annotate a finding/template with stimulus description."""
    stimulus_type: StimulusType
    duration_ms: Optional[float] = None
    complexity: Optional[float] = None  # 0-1
    description: str = ""
    cva_constraints_relevant: List[str] = field(default_factory=list)
    confidence: float = 0.8

    def to_dict(self) -> Dict:
        return {
            "type": AnnotationType.STIMULUS_DESCRIPTION.value,
            "stimulus_type": self.stimulus_type.value,
            "duration_ms": self.duration_ms,
            "complexity": self.complexity,
            "description": self.description,
            "cva_constraints_relevant": self.cva_constraints_relevant,
            "confidence": self.confidence,
        }


@dataclass
class MoleculeLink:
    """Link a finding to a molecule via T15-level specification."""
    molecule_id: str
    template_id: str
    link_type: str = "supports"  # supports, constrains, extends
    strength: float = 0.5
    cva_constraint_mappings: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "type": AnnotationType.MOLECULE_T15_LINK.value,
            "molecule_id": self.molecule_id,
            "template_id": self.template_id,
            "link_type": self.link_type,
            "strength": self.strength,
            "cva_constraint_mappings": self.cva_constraint_mappings,
        }


@dataclass
class CVAAnnotationSet:
    """Complete set of CVA annotations for a template or finding."""
    target_id: str  # template_id or finding_id
    measurements: List[MeasurementAnnotation] = field(default_factory=list)
    stimuli: List[StimulusAnnotation] = field(default_factory=list)
    molecule_links: List[MoleculeLink] = field(default_factory=list)
    constraint_tags: Dict[str, float] = field(default_factory=dict)
    valuation_tags: Dict[str, float] = field(default_factory=dict)

    def to_json(self) -> str:
        return json.dumps({
            "target_id": self.target_id,
            "measurements": [m.to_dict() for m in self.measurements],
            "stimuli": [s.to_dict() for s in self.stimuli],
            "molecule_links": [l.to_dict() for l in self.molecule_links],
            "constraint_tags": self.constraint_tags,
            "valuation_tags": self.valuation_tags,
        }, indent=2)

    @classmethod
    def from_json(cls, data: str | dict) -> "CVAAnnotationSet":
        if isinstance(data, str):
            data = json.loads(data)
        measurements = [
            MeasurementAnnotation(
                modality=MeasurementModality(m["modality"]),
                spatial_resolution=m.get("spatial_resolution"),
                temporal_resolution=m.get("temporal_resolution"),
                sample_size=m.get("sample_size"),
                population=m.get("population"),
                confidence=m.get("confidence", 0.8),
            )
            for m in data.get("measurements", [])
        ]
        stimuli = [
            StimulusAnnotation(
                stimulus_type=StimulusType(s["stimulus_type"]),
                duration_ms=s.get("duration_ms"),
                complexity=s.get("complexity"),
                description=s.get("description", ""),
                cva_constraints_relevant=s.get("cva_constraints_relevant", []),
            )
            for s in data.get("stimuli", [])
        ]
        molecule_links = [
            MoleculeLink(
                molecule_id=l["molecule_id"],
                template_id=l["template_id"],
                link_type=l.get("link_type", "supports"),
                strength=l.get("strength", 0.5),
                cva_constraint_mappings=l.get("cva_constraint_mappings", {}),
            )
            for l in data.get("molecule_links", [])
        ]
        return cls(
            target_id=data.get("target_id", ""),
            measurements=measurements,
            stimuli=stimuli,
            molecule_links=molecule_links,
            constraint_tags=data.get("constraint_tags", {}),
            valuation_tags=data.get("valuation_tags", {}),
        )


@dataclass
class NeurotypeRelevance:
    """Which neurotype profiles a finding applies to."""
    neurotypes: List[str] = field(default_factory=list)  # e.g., ["neurotypical", "ASD", "ADHD"]
    exclusions: List[str] = field(default_factory=list)
    confidence: float = 0.7
    source_text: str = ""

    def to_dict(self) -> Dict:
        return {
            "type": AnnotationType.NEUROTYPE_RELEVANCE.value,
            "neurotypes": self.neurotypes,
            "exclusions": self.exclusions,
            "confidence": self.confidence,
            "source_text": self.source_text,
        }


@dataclass
class CulturalScope:
    """Which cultural profiles a finding was tested in."""
    cultures: List[str] = field(default_factory=list)  # e.g., ["Western", "East Asian"]
    generalizability: str = "unknown"  # universal, culture_specific, partially_universal
    sample_description: str = ""
    confidence: float = 0.7

    def to_dict(self) -> Dict:
        return {
            "type": AnnotationType.CULTURAL_SCOPE.value,
            "cultures": self.cultures,
            "generalizability": self.generalizability,
            "sample_description": self.sample_description,
            "confidence": self.confidence,
        }
