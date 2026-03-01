#!/usr/bin/env python3
"""
Batch Annotate Stimuli — Phase 5, Task 5.5
===========================================

Scans extraction JSONs and templates to auto-annotate with
STIMULUS_DESCRIPTION tags. Identifies presentation modality,
abstraction level, parametric control, stimulus type.

Usage:
    python scripts/batch_annotate_stimuli.py
    python scripts/batch_annotate_stimuli.py --dry-run
"""

import argparse
import json
import re
import sys
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

TEMPLATES_DIR = PROJECT_ROOT / "data" / "templates"
EXTRACTIONS_DIR = PROJECT_ROOT / "data" / "extractions"
OUTPUT_PATH = PROJECT_ROOT / "data" / "annotations" / "stimulus_descriptions.json"


# =============================================================================
# Stimulus Classification
# =============================================================================

PRESENTATION_PATTERNS = {
    "real_environment": [
        re.compile(r'\b(?:field\s+(?:study|experiment))', re.IGNORECASE),
        re.compile(r'\b(?:in[\s-]?situ)', re.IGNORECASE),
        re.compile(r'\b(?:real[\s-]?world|actual\s+(?:building|space|environment))', re.IGNORECASE),
        re.compile(r'\b(?:on[\s-]?site|real\s+setting)', re.IGNORECASE),
    ],
    "VR_scene": [
        re.compile(r'\bvirtual\s+(?:reality|environment|scene|room)', re.IGNORECASE),
        re.compile(r'\bVR\b'),
        re.compile(r'\bimmersive\b', re.IGNORECASE),
        re.compile(r'\bhead[\s-]?mounted\b', re.IGNORECASE),
    ],
    "photograph": [
        re.compile(r'\bphoto(?:graph)?s?\b', re.IGNORECASE),
        re.compile(r'\bpictures?\s+of\b', re.IGNORECASE),
        re.compile(r'\bimages?\s+of\s+(?:buildings?|rooms?|spaces?|environments?)', re.IGNORECASE),
        re.compile(r'\bslides?\b', re.IGNORECASE),
    ],
    "video": [
        re.compile(r'\bvideo\s+(?:clip|recording|footage)', re.IGNORECASE),
        re.compile(r'\bfilm\b', re.IGNORECASE),
        re.compile(r'\bwalk[\s-]?through\s+video', re.IGNORECASE),
    ],
    "soundscape": [
        re.compile(r'\bsoundscape\b', re.IGNORECASE),
        re.compile(r'\baudio\s+(?:stimulus|recording|clip)', re.IGNORECASE),
        re.compile(r'\bbinaural\b', re.IGNORECASE),
        re.compile(r'\bambisonic\b', re.IGNORECASE),
    ],
    "rendering_3D": [
        re.compile(r'\b3D\s+(?:model|render)', re.IGNORECASE),
        re.compile(r'\bCAD\b'),
        re.compile(r'\bBIM\b'),
        re.compile(r'\brendering\b', re.IGNORECASE),
    ],
    "diagram_abstract": [
        re.compile(r'\bdiagram\b', re.IGNORECASE),
        re.compile(r'\bschematic\b', re.IGNORECASE),
        re.compile(r'\bfloor\s+plan\b', re.IGNORECASE),
        re.compile(r'\babstract\s+(?:pattern|display|stimulus)', re.IGNORECASE),
    ],
    "text_vignette": [
        re.compile(r'\bscenario\s+description\b', re.IGNORECASE),
        re.compile(r'\bwritten\s+(?:scenario|vignette|description)', re.IGNORECASE),
        re.compile(r'\bvignette\b', re.IGNORECASE),
    ],
}

ABSTRACTION_MARKERS = {
    "high_realism": [
        re.compile(r'\bphoto[\s-]?realistic\b', re.IGNORECASE),
        re.compile(r'\breal[\s-]?world\b', re.IGNORECASE),
        re.compile(r'\bactual\s+(?:building|environment)', re.IGNORECASE),
    ],
    "medium_realism": [
        re.compile(r'\bsimulated\b', re.IGNORECASE),
        re.compile(r'\brealistic\s+rendering', re.IGNORECASE),
    ],
    "low_realism": [
        re.compile(r'\babstract\b', re.IGNORECASE),
        re.compile(r'\bsimplified\b', re.IGNORECASE),
        re.compile(r'\bschematic\b', re.IGNORECASE),
    ],
}

PARAMETRIC_MARKERS = [
    re.compile(r'\bsystematic(?:ally)?\s+vari', re.IGNORECASE),
    re.compile(r'\bparametric\b', re.IGNORECASE),
    re.compile(r'\bmanipulat', re.IGNORECASE),
    re.compile(r'\bconditions?\s*[:=]\s*\d', re.IGNORECASE),
    re.compile(r'\b(?:2|3|4)\s*×\s*(?:2|3|4)\b', re.IGNORECASE),
    re.compile(r'\bfactorial\b', re.IGNORECASE),
    re.compile(r'\bbetween[\s-]?subjects?\b', re.IGNORECASE),
    re.compile(r'\bwithin[\s-]?subjects?\b', re.IGNORECASE),
]


def classify_stimulus(text: str) -> dict:
    """Classify stimulus characteristics from text."""
    result = {
        "presentation_modalities": {},
        "abstraction_level": "unknown",
        "has_parametric_control": False,
        "parametric_indicators": [],
    }
    
    # Detect presentation modalities
    for modality, patterns in PRESENTATION_PATTERNS.items():
        count = sum(len(p.findall(text)) for p in patterns)
        if count > 0:
            result["presentation_modalities"][modality] = count
    
    # Detect abstraction level
    for level, patterns in ABSTRACTION_MARKERS.items():
        if any(p.search(text) for p in patterns):
            result["abstraction_level"] = level
            break
    
    # Detect parametric control
    for p in PARAMETRIC_MARKERS:
        matches = p.findall(text)
        if matches:
            result["has_parametric_control"] = True
            result["parametric_indicators"].extend(matches[:2])
    
    return result


def main():
    parser = argparse.ArgumentParser(description="Batch annotate stimulus descriptions")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    
    annotations = []
    stats = Counter()
    
    # Process extractions first (richer text)
    extraction_files = sorted(EXTRACTIONS_DIR.glob("*.json"))
    print(f"Processing {len(extraction_files)} extractions...")
    
    for i, ef in enumerate(extraction_files):
        try:
            with open(ef) as f:
                extraction = json.load(f)
            
            parts = []
            for field in ["title", "abstract", "methodology", "discussion"]:
                if field in extraction and isinstance(extraction[field], str):
                    parts.append(extraction[field])
            if "findings" in extraction:
                for f_item in extraction["findings"]:
                    for k in ["antecedent", "consequent", "mechanism", "quote"]:
                        if k in f_item and isinstance(f_item[k], str):
                            parts.append(f_item[k])
            
            text = " ".join(parts)
            classification = classify_stimulus(text)
            
            if classification["presentation_modalities"]:
                ann = {
                    "type": "STIMULUS_DESCRIPTION",
                    "target_type": "extraction",
                    "target_id": ef.stem,
                    "presentation_modalities": classification["presentation_modalities"],
                    "abstraction_level": classification["abstraction_level"],
                    "has_parametric_control": classification["has_parametric_control"],
                    "parametric_indicators": classification["parametric_indicators"][:3],
                    "confidence": min(0.85, sum(classification["presentation_modalities"].values()) / 5),
                    "source": "auto_batch_v1",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
                annotations.append(ann)
                stats["extractions_annotated"] += 1
                for m in classification["presentation_modalities"]:
                    stats[f"stimulus_{m}"] += 1
                if classification["has_parametric_control"]:
                    stats["with_parametric_control"] += 1
        except Exception:
            stats["extraction_errors"] += 1
        
        if (i + 1) % 200 == 0:
            print(f"  Processed {i+1}/{len(extraction_files)}...")
    
    # Process templates
    template_files = sorted(TEMPLATES_DIR.glob("*.json"))
    print(f"Processing {len(template_files)} templates...")
    
    for tf in template_files:
        try:
            with open(tf) as f:
                template = json.load(f)
            
            parts = []
            for field in ["name", "bridge_warrant", "description"]:
                if field in template and isinstance(template[field], str):
                    parts.append(template[field])
            
            text = " ".join(parts)
            classification = classify_stimulus(text)
            
            if classification["presentation_modalities"]:
                ann = {
                    "type": "STIMULUS_DESCRIPTION",
                    "target_type": "template",
                    "target_id": template.get("template_id", tf.stem),
                    "presentation_modalities": classification["presentation_modalities"],
                    "abstraction_level": classification["abstraction_level"],
                    "has_parametric_control": classification["has_parametric_control"],
                    "confidence": min(0.85, sum(classification["presentation_modalities"].values()) / 5),
                    "source": "auto_batch_v1",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
                annotations.append(ann)
                stats["templates_annotated"] += 1
        except Exception:
            stats["template_errors"] += 1
    
    # Output
    if not args.dry_run:
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(OUTPUT_PATH, "w") as f:
            json.dump({"annotations": annotations, "stats": dict(stats)}, f, indent=2)
        print(f"\nSaved {len(annotations)} annotations to {OUTPUT_PATH}")
    
    print(f"\n{'='*60}")
    print(f"STIMULUS DESCRIPTION ANNOTATION COMPLETE")
    print(f"{'='*60}")
    for k, v in sorted(stats.items()):
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
