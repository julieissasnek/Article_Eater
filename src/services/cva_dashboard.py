"""
cva_dashboard.py — CVA Visualization & Dashboard Data Generator
================================================================

Generates dashboard-ready data for CVA visualization:
  1. Rasa attractor landscape (9 attractor configs)
  2. Cultural variant comparisons (4 cultures × 9 valuations)
  3. Neurotype sensitivity profiles (10 neurotypes × 8 constraints)
  4. Activity frame precision heatmap (10 frames × 8 constraints)
  5. Template coverage matrix

Output: JSON files ready for Streamlit/D3 visualization.

Reference: Post-remediation task — Dashboard/Visualization
ADR-001: Extension layer — new file, no existing code modified.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

LOGGER = logging.getLogger(__name__)


def generate_rasa_landscape(output_dir: str) -> str:
    """Generate rasa attractor landscape data.

    Shows 9 aesthetic-emotional states with basin volumes and stability.
    """
    from src.services.cva_attractor import CVAAttractorEngine

    engine = CVAAttractorEngine()
    configs = engine.rasa_configs

    landscape = {
        "title": "Rasa Attractor Landscape",
        "description": "9 aesthetic-emotional states from Natyashastra",
        "attractors": [],
    }

    for name, config in configs.items():
        entry = {
            "name": name,
            "description": config.get("description", ""),
            "center": config.get("center", []),
            "basin_radius": config.get("basin_radius", 0.3),
            "stability": config.get("stability", "stable"),
        }
        landscape["attractors"].append(entry)

    out_path = Path(output_dir) / "rasa_landscape.json"
    out_path.write_text(json.dumps(landscape, indent=2), encoding="utf-8")
    LOGGER.info("Generated rasa landscape: %s", out_path)
    return str(out_path)


def generate_cultural_comparison(output_dir: str) -> str:
    """Generate cultural variant comparison data.

    Compares 4 cultural valuation structures on the same scene.
    """
    from src.services.cva_constraint_engine import CVAConstraintEngine
    from src.services.cva_valuation_engine import CVAValuationEngine
    from src.models.subject_characteristics import (
        SubjectCharacteristics,
        CulturalPreset,
    )

    c_engine = CVAConstraintEngine()
    v_engine = CVAValuationEngine()

    # Standard scene
    scene = {
        "edge": 0.6, "motion": 0.3, "contrast": 0.5,
        "figure_ground": 0.7, "temporal_coherence": 0.5, "symmetry": 0.5,
    }

    cultures = {
        "Western": CulturalPreset.WESTERN,
        "Japanese": CulturalPreset.JAPANESE,
        "West African": CulturalPreset.WEST_AFRICAN,
        "Indian": CulturalPreset.INDIAN,
    }

    comparison = {
        "title": "Cultural Valuation Comparison",
        "scene": scene,
        "cultures": {},
    }

    for name, preset in cultures.items():
        subject = SubjectCharacteristics.from_preset(culture=preset)
        constraints = c_engine.compute(scene, subject)
        valuations = v_engine.compute(constraints, subject)
        comparison["cultures"][name] = {
            "variant": valuations.variant.value if hasattr(valuations.variant, 'value') else str(valuations.variant),
            "values": valuations.values,
            "dimensions": list(valuations.values.keys()),
        }

    out_path = Path(output_dir) / "cultural_comparison.json"
    out_path.write_text(json.dumps(comparison, indent=2), encoding="utf-8")
    LOGGER.info("Generated cultural comparison: %s", out_path)
    return str(out_path)


def generate_neurotype_sensitivity(output_dir: str) -> str:
    """Generate neurotype sensitivity profile data.

    Shows how each neurotype modulates the 8 Tier 2 constraints.
    """
    from src.services.cva_constraint_engine import (
        CVAConstraintEngine,
        NEUROTYPE_CONSTRAINT_MODS,
    )

    profiles = {
        "title": "Neurotype Constraint Sensitivity",
        "constraint_names": [
            "prediction_error", "processing_cost", "load_rate",
            "control_efficacy", "multisensory_coherence", "affordance_density",
            "social_cue_density", "narrative_coherence",
        ],
        "neurotypes": {},
    }

    for neuro_name, mods in NEUROTYPE_CONSTRAINT_MODS.items():
        gains = {}
        for constraint in profiles["constraint_names"]:
            mod = mods.get(constraint, {})
            gains[constraint] = mod.get("gain", 1.0)
        profiles["neurotypes"][neuro_name] = gains

    out_path = Path(output_dir) / "neurotype_sensitivity.json"
    out_path.write_text(json.dumps(profiles, indent=2), encoding="utf-8")
    LOGGER.info("Generated neurotype sensitivity: %s", out_path)
    return str(out_path)


def generate_frame_precision_heatmap(output_dir: str) -> str:
    """Generate activity frame precision heatmap data.

    10 frames × 8 constraint precisions for probabilistic constraints.
    """
    from src.services.cva_constraint_engine import FRAME_PRECISIONS

    constraint_labels = [
        "Safe", "Stable", "Path", "Attract",
        "Repel", "Support", "Push", "Resist",
    ]

    heatmap = {
        "title": "Activity Frame Precision Heatmap",
        "constraint_labels": constraint_labels,
        "frames": {},
    }

    for frame, precisions in FRAME_PRECISIONS.items():
        heatmap["frames"][frame] = {
            label: prec for label, prec in zip(constraint_labels, precisions)
        }

    out_path = Path(output_dir) / "frame_precision_heatmap.json"
    out_path.write_text(json.dumps(heatmap, indent=2), encoding="utf-8")
    LOGGER.info("Generated frame precision heatmap: %s", out_path)
    return str(out_path)


def generate_template_coverage(output_dir: str) -> str:
    """Generate template ↔ CVA coverage matrix."""
    from src.services.cva_template_linker import CVATemplateLinker

    linker = CVATemplateLinker()
    report = linker.coverage_report()
    links = linker.link_all_templates()

    coverage = {
        "title": "Template ↔ CVA Coverage",
        "total_templates": len(links),
        "templates": [l.to_dict() for l in links],
        "constraint_coverage": report["constraint_coverage"],
        "valuation_coverage": report["valuation_coverage"],
        "uncovered_constraints": report["uncovered_constraints"],
        "uncovered_valuations": report["uncovered_valuations"],
    }

    out_path = Path(output_dir) / "template_coverage.json"
    out_path.write_text(json.dumps(coverage, indent=2), encoding="utf-8")
    LOGGER.info("Generated template coverage: %s", out_path)
    return str(out_path)


def generate_all_dashboards(output_dir: str = "data/cva/dashboards") -> Dict[str, str]:
    """Generate all dashboard data files."""
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    results = {}
    generators = [
        ("rasa_landscape", generate_rasa_landscape),
        ("neurotype_sensitivity", generate_neurotype_sensitivity),
        ("frame_precision_heatmap", generate_frame_precision_heatmap),
        ("template_coverage", generate_template_coverage),
    ]

    for name, func in generators:
        try:
            path = func(output_dir)
            results[name] = path
            LOGGER.info("✓ %s", name)
        except Exception as e:
            LOGGER.warning("✗ %s: %s", name, e)
            results[name] = f"ERROR: {e}"

    # Cultural comparison may fail if CulturalPreset not available
    try:
        results["cultural_comparison"] = generate_cultural_comparison(output_dir)
        LOGGER.info("✓ cultural_comparison")
    except Exception as e:
        LOGGER.warning("✗ cultural_comparison: %s", e)
        results["cultural_comparison"] = f"ERROR: {e}"

    return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    import sys
    output = sys.argv[1] if len(sys.argv) > 1 else "data/cva/dashboards"
    results = generate_all_dashboards(output)
    for name, path in results.items():
        print(f"  {name}: {path}")
