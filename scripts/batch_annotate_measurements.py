#!/usr/bin/env python3
"""
Batch Annotate Measurements — Phase 5, Task 5.4
=================================================

Scans templates and extraction JSONs to auto-annotate with
MEASUREMENT_MODALITY tags (HR, eye-tracking, fMRI, EDA, cortisol,
self-report, behavioral).

Target: measurement tags on ≥50% of the 209 templates.

Usage:
    python scripts/batch_annotate_measurements.py
    python scripts/batch_annotate_measurements.py --dry-run
"""

import argparse
import json
import re
import sys
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime, timezone

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

TEMPLATES_DIR = PROJECT_ROOT / "data" / "templates"
EXTRACTIONS_DIR = PROJECT_ROOT / "data" / "extractions"
OUTPUT_PATH = PROJECT_ROOT / "data" / "annotations" / "measurement_modalities.json"


# =============================================================================
# Measurement Modality Detection
# =============================================================================

MODALITY_PATTERNS = {
    "eye_tracking": [
        re.compile(r'\beye[\s-]?track', re.IGNORECASE),
        re.compile(r'\bfixation\b', re.IGNORECASE),
        re.compile(r'\bsaccade', re.IGNORECASE),
        re.compile(r'\bgaze\b', re.IGNORECASE),
    ],
    "fMRI": [
        re.compile(r'\bfMRI\b'),
        re.compile(r'\bfunctional\s+(?:magnetic\s+)?resonance\b', re.IGNORECASE),
        re.compile(r'\bBOLD\b'),
        re.compile(r'\bneuroimaging\b', re.IGNORECASE),
    ],
    "EEG": [
        re.compile(r'\bEEG\b'),
        re.compile(r'\belectroencephalogra', re.IGNORECASE),
        re.compile(r'\bevent[\s-]related\s+potential', re.IGNORECASE),
        re.compile(r'\bERP\b'),
    ],
    "EDA": [
        re.compile(r'\bEDA\b'),
        re.compile(r'\belectrodermal\b', re.IGNORECASE),
        re.compile(r'\bskin\s+conductance\b', re.IGNORECASE),
        re.compile(r'\bgalvanic\s+skin\b', re.IGNORECASE),
        re.compile(r'\bGSR\b'),
    ],
    "heart_rate": [
        re.compile(r'\bheart\s+rate\b', re.IGNORECASE),
        re.compile(r'\bHRV\b'),
        re.compile(r'\bcardiac\b', re.IGNORECASE),
        re.compile(r'\bECG\b'),
    ],
    "cortisol": [
        re.compile(r'\bcortisol\b', re.IGNORECASE),
        re.compile(r'\bsaliva', re.IGNORECASE),
        re.compile(r'\bneuroendocrine\b', re.IGNORECASE),
    ],
    "self_report": [
        re.compile(r'\bquestionnaire\b', re.IGNORECASE),
        re.compile(r'\bself[\s-]?report\b', re.IGNORECASE),
        re.compile(r'\bLikert\b', re.IGNORECASE),
        re.compile(r'\bsurvey\b', re.IGNORECASE),
        re.compile(r'\brating\s+scale\b', re.IGNORECASE),
        re.compile(r'\bPANAS\b'),
        re.compile(r'\bVAS\b'),
        re.compile(r'\bPSS\b'),
    ],
    "behavioral": [
        re.compile(r'\breaction\s+time\b', re.IGNORECASE),
        re.compile(r'\bresponse\s+time\b', re.IGNORECASE),
        re.compile(r'\bperformance\s+(?:measure|task|test)', re.IGNORECASE),
        re.compile(r'\bwayfinding\s+(?:task|performance|time)', re.IGNORECASE),
        re.compile(r'\bnavigation\s+(?:task|performance)', re.IGNORECASE),
    ],
    "physiological": [
        re.compile(r'\bblood\s+pressure\b', re.IGNORECASE),
        re.compile(r'\brespiration\b', re.IGNORECASE),
        re.compile(r'\bEMG\b'),
        re.compile(r'\bmuscle\b', re.IGNORECASE),
        re.compile(r'\bpupil\b', re.IGNORECASE),
    ],
    "acoustic": [
        re.compile(r'\bdecibel\b', re.IGNORECASE),
        re.compile(r'\bdB\(?\s*A\)?', re.IGNORECASE),
        re.compile(r'\bsound\s+(?:level|pressure|meter)', re.IGNORECASE),
        re.compile(r'\breverberation\s+time\b', re.IGNORECASE),
        re.compile(r'\bRT60\b'),
    ],
    "photometric": [
        re.compile(r'\blux\b', re.IGNORECASE),
        re.compile(r'\billuminance\b', re.IGNORECASE),
        re.compile(r'\bcolor\s+temperature\b', re.IGNORECASE),
        re.compile(r'\bCCT\b'),
        re.compile(r'\bspectro', re.IGNORECASE),
    ],
    "VR": [
        re.compile(r'\bvirtual\s+reality\b', re.IGNORECASE),
        re.compile(r'\bVR\b'),
        re.compile(r'\bhead[\s-]?mounted\s+display\b', re.IGNORECASE),
        re.compile(r'\bHMD\b'),
        re.compile(r'\bimmersive\b', re.IGNORECASE),
    ],
}


def detect_modalities(text: str) -> dict:
    """Detect measurement modalities in text. Returns {modality: count}."""
    detected = {}
    for modality, patterns in MODALITY_PATTERNS.items():
        total = sum(len(p.findall(text)) for p in patterns)
        if total > 0:
            detected[modality] = total
    return detected


def extract_text_from_template(template: dict) -> str:
    """Extract searchable text from a template."""
    parts = []
    for field in ["name", "bridge_warrant", "description"]:
        if field in template and isinstance(template[field], str):
            parts.append(template[field])
    
    if "mechanism_chain" in template:
        chain = template["mechanism_chain"]
        if isinstance(chain, list):
            for step in chain:
                if isinstance(step, dict):
                    for v in step.values():
                        if isinstance(v, str):
                            parts.append(v)
    
    if "calibrated_parameters" in template:
        params = template["calibrated_parameters"]
        if isinstance(params, dict):
            for k, v in params.items():
                parts.append(k)
                if isinstance(v, str):
                    parts.append(v)
    
    return " ".join(parts)


def extract_text_from_extraction(extraction: dict) -> str:
    """Extract searchable text from an extraction JSON."""
    parts = []
    for field in ["title", "abstract", "methodology", "discussion", "conclusions"]:
        if field in extraction and isinstance(extraction[field], str):
            parts.append(extraction[field])
    
    if "findings" in extraction:
        for f in extraction["findings"]:
            for k in ["antecedent", "consequent", "mechanism", "quote"]:
                if k in f and isinstance(f[k], str):
                    parts.append(f[k])
    
    return " ".join(parts)


def main():
    parser = argparse.ArgumentParser(description="Batch annotate measurement modalities")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    
    annotations = []
    stats = Counter()
    
    # Process templates
    template_files = sorted(TEMPLATES_DIR.glob("*.json"))
    print(f"Processing {len(template_files)} templates...")
    
    for tf in template_files:
        try:
            with open(tf) as f:
                template = json.load(f)
            text = extract_text_from_template(template)
            modalities = detect_modalities(text)
            
            if modalities:
                ann = {
                    "type": "MEASUREMENT_MODALITY",
                    "target_type": "template",
                    "target_id": template.get("template_id", tf.stem),
                    "modalities": modalities,
                    "confidence": min(0.9, sum(modalities.values()) / 10),
                    "source": "auto_batch_v1",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
                annotations.append(ann)
                stats["templates_annotated"] += 1
                for m in modalities:
                    stats[f"modality_{m}"] += 1
            else:
                stats["templates_no_modality"] += 1
        except Exception as e:
            stats["template_errors"] += 1
    
    # Process extractions
    extraction_files = sorted(EXTRACTIONS_DIR.glob("*.json"))
    print(f"Processing {len(extraction_files)} extractions...")
    
    for i, ef in enumerate(extraction_files):
        try:
            with open(ef) as f:
                extraction = json.load(f)
            text = extract_text_from_extraction(extraction)
            modalities = detect_modalities(text)
            
            if modalities:
                ann = {
                    "type": "MEASUREMENT_MODALITY",
                    "target_type": "extraction",
                    "target_id": ef.stem,
                    "modalities": modalities,
                    "confidence": min(0.9, sum(modalities.values()) / 10),
                    "source": "auto_batch_v1",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
                annotations.append(ann)
                stats["extractions_annotated"] += 1
        except Exception:
            stats["extraction_errors"] += 1
        
        if (i + 1) % 200 == 0:
            print(f"  Processed {i+1}/{len(extraction_files)}...")
    
    # Output
    if not args.dry_run:
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(OUTPUT_PATH, "w") as f:
            json.dump({"annotations": annotations, "stats": dict(stats)}, f, indent=2)
        print(f"\nSaved {len(annotations)} annotations to {OUTPUT_PATH}")
    
    print(f"\n{'='*60}")
    print(f"MEASUREMENT MODALITY ANNOTATION COMPLETE")
    print(f"{'='*60}")
    for k, v in sorted(stats.items()):
        print(f"  {k}: {v}")
    
    coverage = stats.get("templates_annotated", 0) / max(len(template_files), 1)
    print(f"\nTemplate coverage: {coverage:.1%} ({stats.get('templates_annotated', 0)}/{len(template_files)})")


if __name__ == "__main__":
    main()
