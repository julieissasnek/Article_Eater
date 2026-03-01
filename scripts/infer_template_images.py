#!/usr/bin/env python3
"""Template → Image Query & CVA Constraint Profile Inference.

Reads article templates and infers:
  1. Candidate API image search queries from mechanism_chain + calibrated_parameters
  2. Hypothesized CVA constraint profiles from template content
  3. Suggested feature_cva_mapping entries for each template

Usage:
    python scripts/infer_template_images.py                   # All templates
    python scripts/infer_template_images.py --template T1     # Single template
    python scripts/infer_template_images.py --output data/template_image_inference.json
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any

PROJECT_ROOT = Path(__file__).parent.parent
TEMPLATES_DIR = PROJECT_ROOT / "data" / "templates"
MAPPING_PATH = PROJECT_ROOT / "data" / "feature_cva_mapping.json"


# =============================================================================
# Keyword → CVA Constraint Mapping
# =============================================================================

CONSTRAINT_KEYWORDS = {
    "prediction_error": [
        "complexity", "fractal", "entropy", "1/f", "spatial frequency",
        "prediction", "surprise", "novelty", "expectation", "mismatch",
        "pattern", "regularity", "disorder", "chaos", "random",
    ],
    "control_efficacy": [
        "wayfinding", "legibility", "navigation", "visibility", "sightline",
        "prospect", "refuge", "enclosure", "control", "agency",
        "choice", "affordance", "access", "path", "circulation",
    ],
    "load_rate": [
        "cognitive load", "attention", "distraction", "processing",
        "information density", "clutter", "visual complexity", "busy",
        "overstimulat", "understimulat",
    ],
    "affordance_density": [
        "affordance", "function", "flexibility", "adapt", "multi-use",
        "action", "interact", "furniture", "equipment", "tool",
    ],
    "temporal_coherence": [
        "circadian", "daylight", "seasonal", "diurnal", "dynamic",
        "rhythm", "temporal", "variation", "change", "flicker",
    ],
    "symmetry_regularity": [
        "symmetr", "balance", "proportion", "golden ratio", "order",
        "grid", "alignment", "formal",
    ],
    "figure_ground_separation": [
        "contrast", "figure-ground", "silhouette", "boundary",
        "edge", "articulation", "legib",
    ],
    "spatial_frequency_match": [
        "fractal", "1/f", "natural", "biophili", "wood", "stone",
        "texture", "grain", "material", "organic",
    ],
}

# Keyword → Image Search Query Categories
SEARCH_QUERY_TEMPLATES = {
    "lighting": [
        "soft diffuse {modifier} lighting interior",
        "{modifier} light workspace architecture",
        "natural daylight {modifier}",
    ],
    "spatial": [
        "{modifier} space architecture",
        "{modifier} interior design",
        "{modifier} building interior",
    ],
    "material": [
        "{modifier} material interior",
        "{modifier} surface texture design",
        "{modifier} finish architecture",
    ],
    "view": [
        "{modifier} view window architecture",
        "prospect {modifier} interior",
        "{modifier} vista building",
    ],
    "thermal": [
        "{modifier} thermal comfort space",
        "{modifier} temperature environment",
    ],
    "acoustic": [
        "{modifier} acoustic environment",
        "{modifier} sound interior",
    ],
    "social": [
        "{modifier} social space architecture",
        "{modifier} gathering space",
    ],
}


def extract_key_terms(text: str) -> List[str]:
    """Extract meaningful terms from template text."""
    if not text:
        return []
    # Remove common words and extract descriptive terms
    stop_words = {
        "the", "a", "an", "in", "of", "to", "and", "or", "is", "are",
        "was", "were", "be", "been", "being", "have", "has", "had",
        "do", "does", "did", "will", "would", "could", "should",
        "for", "with", "at", "by", "from", "on", "as", "not", "but",
        "that", "this", "these", "those", "it", "its", "if", "than",
        "when", "which", "who", "what", "how", "where", "there",
        "can", "may", "all", "each", "every", "both", "few", "more",
        "most", "other", "some", "such", "no", "nor", "only", "own",
        "same", "so", "too", "very", "just",
    }
    words = re.findall(r'\b[a-z]+\b', text.lower())
    return [w for w in words if w not in stop_words and len(w) > 3]


def infer_constraints(template: dict) -> Dict[str, float]:
    """Infer CVA constraint profile from template content."""
    # Collect all text
    text_parts = []
    for field in ["name", "bridge_warrant"]:
        if field in template and isinstance(template[field], str):
            text_parts.append(template[field])
    
    # Extract from mechanism chain
    if "mechanism_chain" in template:
        chain = template["mechanism_chain"]
        if isinstance(chain, list):
            for step in chain:
                if isinstance(step, dict):
                    for v in step.values():
                        if isinstance(v, str):
                            text_parts.append(v)
        elif isinstance(chain, str):
            text_parts.append(chain)
    
    # Extract from calibrated parameters
    if "calibrated_parameters" in template:
        params = template["calibrated_parameters"]
        if isinstance(params, dict):
            for key, val in params.items():
                text_parts.append(key)
                if isinstance(val, dict):
                    for k2, v2 in val.items():
                        if isinstance(v2, str):
                            text_parts.append(v2)
    
    full_text = " ".join(text_parts).lower()
    
    # Score each constraint
    scores = {}
    for constraint, keywords in CONSTRAINT_KEYWORDS.items():
        score = 0
        matches = 0
        for kw in keywords:
            if kw.lower() in full_text:
                matches += 1
        if matches > 0:
            score = min(1.0, matches / 3)  # Normalize: 3+ matches = 1.0
            scores[constraint] = round(score, 2)
    
    return scores


def generate_search_queries(template: dict) -> List[str]:
    """Generate API image search queries from template content."""
    queries = []
    
    name = template.get("name", "")
    building_types = template.get("building_types", [])
    
    # Extract key modifiers from the name
    key_terms = extract_key_terms(name)
    
    # Generate queries from mechanism chain
    if "mechanism_chain" in template:
        chain = template["mechanism_chain"]
        if isinstance(chain, list):
            for step in chain:
                if isinstance(step, dict):
                    from_field = step.get("from", "")
                    to_field = step.get("to", "")
                    desc = step.get("description", "")
                    
                    # Create queries from mechanism descriptors
                    for modifier in [from_field, to_field]:
                        if modifier:
                            readable = modifier.replace("_", " ")
                            queries.append(f"{readable} interior architecture")
    
    # Generate queries from building types
    if building_types:
        bt_list = building_types if isinstance(building_types, list) else list(building_types.values()) if isinstance(building_types, dict) else []
        for bt in bt_list[:3]:
            if isinstance(bt, str):
                clean = bt.split("—")[0].strip() if "—" in bt else bt.strip()
                queries.append(f"{clean} interior")
    
    # Generate queries from calibrated parameters
    if "calibrated_parameters" in template:
        params = template["calibrated_parameters"]
        if isinstance(params, dict):
            for param_name in list(params.keys())[:3]:
                readable = param_name.replace("_", " ")
                queries.append(f"{readable} architecture example")
    
    # Deduplicate and clean
    seen = set()
    clean_queries = []
    for q in queries:
        q = q.strip()
        if q and q.lower() not in seen:
            seen.add(q.lower())
            clean_queries.append(q)
    
    return clean_queries[:10]  # Cap at 10


def infer_feature_matches(constraints: Dict[str, float]) -> List[str]:
    """Given inferred constraints, suggest matching image tagger features."""
    feature_map = {
        "prediction_error": [
            "cnfa.fluency.visual_entropy_spatial",
            "cnfa.fluency.edge_clarity_mean",
            "cnfa.fluency.pattern_rhythm_regularity",
        ],
        "control_efficacy": [
            "cnfa.spatial.prospect_to_refuge_ratio",
            "cnfa.cognitive.legibility_score",
            "cnfa.spatial.enclosure_index",
        ],
        "load_rate": [
            "cnfa.fluency.clutter_density_count",
            "cnfa.fluency.processing_load_proxy",
            "cnfa.light.diffuse_vs_direct_ratio",
        ],
        "affordance_density": [
            "cnfa.cognitive.activity_zones_count",
            "cnfa.haptic.texture_variation_index",
        ],
        "temporal_coherence": [
            "cnfa.light.warm_vs_cool_ratio",
            "cnfa.dynamic.optic_flow_magnitude",
        ],
        "symmetry_regularity": [
            "cnfa.fluency.symmetry_score_horizontal",
            "cnfa.fluency.pattern_rhythm_regularity",
        ],
        "spatial_frequency_match": [
            "component.wall.material.wood_slat",
            "component.wall.material.stone_wall",
            "component.wall.material.brick_exposed",
        ],
    }
    
    features = []
    for constraint, score in sorted(constraints.items(), key=lambda x: -x[1]):
        if constraint in feature_map:
            features.extend(feature_map[constraint])
    
    return list(dict.fromkeys(features))  # Dedup preserving order


def process_template(filepath: Path) -> Optional[dict]:
    """Process a single template file."""
    try:
        with open(filepath) as f:
            template = json.load(f)
    except Exception as e:
        return None
    
    result = {
        "template_id": template.get("template_id", filepath.stem),
        "display_id": template.get("display_id", filepath.stem),
        "name": template.get("name", "Unknown"),
        "inferred_constraints": infer_constraints(template),
        "search_queries": generate_search_queries(template),
        "matched_features": [],
        "building_types": template.get("building_types", []),
        "has_mechanism_chain": "mechanism_chain" in template,
        "has_calibrated_params": "calibrated_parameters" in template,
    }
    
    result["matched_features"] = infer_feature_matches(result["inferred_constraints"])
    
    return result


def main():
    parser = argparse.ArgumentParser(description="Infer image queries from templates")
    parser.add_argument("--template", type=str, help="Single template ID (e.g., T1)")
    parser.add_argument("--output", type=str, 
                        default=str(PROJECT_ROOT / "data" / "template_image_inference.json"))
    parser.add_argument("--limit", type=int, help="Max templates to process")
    args = parser.parse_args()
    
    if args.template:
        filepath = TEMPLATES_DIR / f"{args.template}.json"
        if not filepath.exists():
            # Try case-insensitive
            for f in TEMPLATES_DIR.glob("*.json"):
                if f.stem.upper() == args.template.upper():
                    filepath = f
                    break
        
        result = process_template(filepath)
        if result:
            print(json.dumps(result, indent=2))
        else:
            print(f"Failed to process {filepath}")
        return
    
    # Process all templates
    template_files = sorted(TEMPLATES_DIR.glob("*.json"))
    if args.limit:
        template_files = template_files[:args.limit]
    
    print(f"Processing {len(template_files)} templates...")
    
    results = []
    for i, filepath in enumerate(template_files):
        result = process_template(filepath)
        if result:
            results.append(result)
        if (i + 1) % 50 == 0:
            print(f"  Processed {i + 1}/{len(template_files)}...")
    
    # Summary
    with_constraints = sum(1 for r in results if r["inferred_constraints"])
    with_queries = sum(1 for r in results if r["search_queries"])
    total_queries = sum(len(r["search_queries"]) for r in results)
    
    output = {
        "generated_at": __import__("datetime").datetime.utcnow().isoformat() + "Z",
        "summary": {
            "templates_processed": len(results),
            "templates_with_constraints": with_constraints,
            "templates_with_queries": with_queries,
            "total_search_queries": total_queries,
        },
        "results": results,
    }
    
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"\n{'='*60}")
    print(f"TEMPLATE IMAGE INFERENCE COMPLETE")
    print(f"{'='*60}")
    print(f"Templates processed: {len(results)}")
    print(f"With constraint inferences: {with_constraints}")
    print(f"With search queries: {with_queries}")
    print(f"Total search queries generated: {total_queries}")
    print(f"\nOutput: {output_path}")
    
    # Print top 5 most-constrained templates
    by_constraints = sorted(results, key=lambda r: len(r["inferred_constraints"]), reverse=True)
    print(f"\nTop 5 most-constrained templates:")
    for r in by_constraints[:5]:
        constraints = ", ".join(f"{k}={v}" for k, v in r["inferred_constraints"].items())
        print(f"  {r['display_id']}: {r['name'][:60]}")
        print(f"    Constraints: {constraints}")
        print(f"    Queries: {r['search_queries'][:3]}")


if __name__ == "__main__":
    main()
