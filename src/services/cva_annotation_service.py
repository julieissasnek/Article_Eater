"""
CVA Annotation Service — CRUD + Auto-Annotate (Sprint S-6)
============================================================

Manages CVA annotations for templates and findings:
- CRUD operations on CVAAnnotationSet
- Auto-annotate: detect measurement modalities and stimulus types from text
- Batch annotation of templates/findings
- Persistence to annotation store (JSON files)

Usage:
    from src.services.cva_annotation_service import CVAAnnotationService
    
    svc = CVAAnnotationService()
    annotations = svc.auto_annotate("template_biophilia_lighting_01")
    svc.save(annotations)
"""

import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timezone

from src.models.cva_annotations import (
    CVAAnnotationSet,
    MeasurementAnnotation,
    MeasurementModality,
    StimulusAnnotation,
    StimulusType,
    MoleculeLink,
)

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent.parent
ANNOTATION_STORE = PROJECT_ROOT / "data" / "cva_annotations"
TEMPLATES_DIR = PROJECT_ROOT / "data" / "templates"
EXTRACTIONS_DIR = PROJECT_ROOT / "data" / "extractions"
MOLECULES_DIR = PROJECT_ROOT / "data" / "molecules"


# =============================================================================
# Auto-Detection Patterns
# =============================================================================

MODALITY_PATTERNS = {
    MeasurementModality.FMRI: re.compile(
        r'\b(?:fMRI|functional\s+MRI|BOLD|blood\s+oxygen|functional\s+magnetic)\b', re.I),
    MeasurementModality.EEG: re.compile(
        r'\b(?:EEG|electroencephal|brainwave|evoked\s+potential|ERP|P300)\b', re.I),
    MeasurementModality.EYE_TRACKING: re.compile(
        r'\b(?:eye[\s-]*track|gaze|fixation|saccade|pupil(?:ometry)?|EyeLink)\b', re.I),
    MeasurementModality.SKIN_CONDUCTANCE: re.compile(
        r'\b(?:skin\s+conduct|galvanic|GSR|EDA|electrodermal)\b', re.I),
    MeasurementModality.HEART_RATE: re.compile(
        r'\b(?:heart\s+rate|HRV|cardiac|ECG|EKG|pulse)\b', re.I),
    MeasurementModality.SELF_REPORT: re.compile(
        r'\b(?:self[\s-]*report|questionnaire|Likert|survey|rating\s+scale|VAS)\b', re.I),
    MeasurementModality.BEHAVIORAL: re.compile(
        r'\b(?:reaction\s+time|response\s+time|accuracy|task\s+performance|behavioral)\b', re.I),
    MeasurementModality.COMPUTATIONAL_MODEL: re.compile(
        r'\b(?:computational\s+model|agent[\s-]*based|simulation|Monte\s+Carlo)\b', re.I),
    MeasurementModality.OBSERVATIONAL: re.compile(
        r'\b(?:observational|naturalistic|field\s+study|ethnograph)\b', re.I),
}

STIMULUS_PATTERNS = {
    StimulusType.VISUAL_STATIC: re.compile(
        r'\b(?:photograph|image|picture|static\s+visual|still\s+image)\b', re.I),
    StimulusType.VISUAL_DYNAMIC: re.compile(
        r'\b(?:video|animation|dynamic\s+visual|moving\s+image)\b', re.I),
    StimulusType.SPATIAL: re.compile(
        r'\b(?:virtual\s+(?:reality|environment)|VR|immersive|3D\s+model|walk[\s-]*through)\b', re.I),
    StimulusType.AUDITORY: re.compile(
        r'\b(?:soundscape|auditory|sound\s+recording|acoustic\s+stimulus)\b', re.I),
    StimulusType.MULTISENSORY: re.compile(
        r'\b(?:multi[\s-]*sensory|cross[\s-]*modal|audio[\s-]*visual)\b', re.I),
    StimulusType.ARCHITECTURAL: re.compile(
        r'\b(?:building\s+facade|interior\s+space|architectural\s+model|floor\s+plan|room\s+layout)\b', re.I),
    StimulusType.NATURAL_SCENE: re.compile(
        r'\b(?:natural\s+scene|landscape|garden|park|forest|nature\s+view)\b', re.I),
    StimulusType.ABSTRACT: re.compile(
        r'\b(?:abstract\s+pattern|fractal|geometric|Mondrian)\b', re.I),
}


class CVAAnnotationService:
    """CRUD + auto-annotate for CVA annotations."""
    
    def __init__(self, store_dir: Path = ANNOTATION_STORE):
        self.store_dir = store_dir
        self.store_dir.mkdir(parents=True, exist_ok=True)
        self._cache: Dict[str, CVAAnnotationSet] = {}
    
    # ----- CRUD -----
    
    def get(self, target_id: str) -> Optional[CVAAnnotationSet]:
        """Retrieve annotations for a target."""
        if target_id in self._cache:
            return self._cache[target_id]
        
        path = self._path_for(target_id)
        if path.exists():
            with open(path) as f:
                data = json.load(f)
            ann = CVAAnnotationSet.from_json(data)
            self._cache[target_id] = ann
            return ann
        return None
    
    def save(self, annotations: CVAAnnotationSet) -> Path:
        """Save annotations to store."""
        path = self._path_for(annotations.target_id)
        with open(path, "w") as f:
            f.write(annotations.to_json())
        self._cache[annotations.target_id] = annotations
        return path
    
    def delete(self, target_id: str) -> bool:
        """Delete annotations for a target."""
        path = self._path_for(target_id)
        if path.exists():
            path.unlink()
            self._cache.pop(target_id, None)
            return True
        return False
    
    def list_all(self) -> List[str]:
        """List all annotated target IDs."""
        return [p.stem for p in self.store_dir.glob("*.json")]
    
    def _path_for(self, target_id: str) -> Path:
        safe_id = target_id.replace("/", "_").replace(":", "_")
        return self.store_dir / f"{safe_id}.json"
    
    # ----- Auto-Annotate -----
    
    def auto_annotate(self, target_id: str) -> CVAAnnotationSet:
        """Auto-annotate a template or finding by ID.
        
        Loads the template/extraction JSON, detects modalities and stimuli,
        links to molecules, and returns a CVAAnnotationSet.
        """
        text = self._load_text(target_id)
        
        # Detect measurement modalities
        measurements = []
        for modality, pattern in MODALITY_PATTERNS.items():
            if pattern.search(text):
                measurements.append(MeasurementAnnotation(
                    modality=modality,
                    confidence=0.7,
                ))
        
        # Detect stimulus types
        stimuli = []
        for stim_type, pattern in STIMULUS_PATTERNS.items():
            if pattern.search(text):
                stimuli.append(StimulusAnnotation(
                    stimulus_type=stim_type,
                    description=f"Auto-detected in text",
                    confidence=0.6,
                ))
        
        # Link to molecules
        molecule_links = self._detect_molecule_links(target_id, text)
        
        # Detect CVA constraint/valuation tags
        constraint_tags = self._detect_constraint_tags(text)
        valuation_tags = self._detect_valuation_tags(text)
        
        return CVAAnnotationSet(
            target_id=target_id,
            measurements=measurements,
            stimuli=stimuli,
            molecule_links=molecule_links,
            constraint_tags=constraint_tags,
            valuation_tags=valuation_tags,
        )
    
    def auto_annotate_batch(self, target_ids: List[str] = None) -> Dict[str, int]:
        """Auto-annotate all templates and return stats."""
        if target_ids is None:
            target_ids = [p.stem for p in TEMPLATES_DIR.glob("*.json")]
        
        stats = {"annotated": 0, "skipped": 0, "errors": 0}
        for tid in target_ids:
            try:
                ann = self.auto_annotate(tid)
                if ann.measurements or ann.stimuli or ann.constraint_tags:
                    self.save(ann)
                    stats["annotated"] += 1
                else:
                    stats["skipped"] += 1
            except Exception as e:
                logger.warning(f"Auto-annotate failed for {tid}: {e}")
                stats["errors"] += 1
        
        return stats
    
    def _load_text(self, target_id: str) -> str:
        """Load text content for a target (template or extraction)."""
        # Try template first
        safe = target_id.replace("/", "_")
        for pattern in [f"{safe}.json", f"{target_id}.json"]:
            for d in [TEMPLATES_DIR, EXTRACTIONS_DIR]:
                path = d / pattern
                if path.exists():
                    with open(path) as f:
                        data = json.load(f)
                    return " ".join(str(v) for v in data.values() if isinstance(v, str))
        return ""
    
    def _detect_molecule_links(self, target_id: str, text: str) -> List[MoleculeLink]:
        """Detect which molecules relate to this target."""
        links = []
        molecule_keywords = {
            "M_RASA": ["attention restoration", "ART", "directed attention", "restorative"],
            "M_CULTURAL_VALUATION": ["cultural", "valuation", "cross-cultural", "preference"],
            "M_ATTRACTOR_TRANSITION": ["attractor", "transition", "bistable", "phase transition"],
            "M_BEAUTY_COMPRESSION": ["beauty", "compression", "aesthetic", "fluency"],
            "M_CCT_PREFERENCE": ["CCT", "color temperature", "warm", "cool light"],
        }
        
        tl = text.lower()
        for mol_id, keywords in molecule_keywords.items():
            matches = sum(1 for kw in keywords if kw.lower() in tl)
            if matches >= 1:
                links.append(MoleculeLink(
                    molecule_id=mol_id,
                    template_id=target_id,
                    link_type="supports",
                    strength=min(0.9, 0.3 + matches * 0.2),
                ))
        
        return links
    
    def _detect_constraint_tags(self, text: str) -> Dict[str, float]:
        """Detect CVA constraint relevance from text."""
        constraints = {
            "C_SAFETY": ["safety", "danger", "threat", "hazard", "secure"],
            "C_BIOPHILIA": ["biophil", "nature", "green", "natural", "vegetation"],
            "C_COMPLEXITY": ["complex", "fractal", "entropy", "information", "visual richness"],
            "C_PROSPECT_REFUGE": ["prospect", "refuge", "enclosure", "open", "shelter"],
            "C_COHERENCE": ["coherent", "order", "organized", "unity", "harmony"],
            "C_LEGIBILITY": ["legib", "wayfinding", "navigat", "orient", "readable"],
            "C_MYSTERY": ["mystery", "curiosity", "explor", "discover"],
            "C_FASCINATION": ["fascinat", "captivat", "engag", "absorb"],
        }
        
        tags = {}
        tl = text.lower()
        for cid, keywords in constraints.items():
            matches = sum(1 for kw in keywords if kw in tl)
            if matches > 0:
                tags[cid] = min(1.0, matches * 0.25)
        
        return tags
    
    def _detect_valuation_tags(self, text: str) -> Dict[str, float]:
        """Detect CVA valuation axes from text."""
        valuations = {
            "V_SAFETY": ["safe", "protect", "secure", "threat"],
            "V_BEAUTY": ["beaut", "aesthet", "attract", "pleas"],
            "V_COMFORT": ["comfort", "relaxat", "ease", "ergonom"],
            "V_MEANING": ["meaning", "significance", "symbol", "identity"],
            "V_SOCIAL": ["social", "communit", "belong", "together"],
            "V_FUNCTION": ["function", "efficien", "productiv", "perform"],
            "V_NOVELTY": ["novel", "surpris", "unexpect", "creativ"],
            "V_NATURE": ["nature", "biophil", "green", "natural"],
        }
        
        tags = {}
        tl = text.lower()
        for vid, keywords in valuations.items():
            matches = sum(1 for kw in keywords if kw in tl)
            if matches > 0:
                tags[vid] = min(1.0, matches * 0.25)
        
        return tags
