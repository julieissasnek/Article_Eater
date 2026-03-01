#!/usr/bin/env python3
"""
Sprint S-4: Cross-Taxonomy Mapping & Gap Analysis
===================================================

Creates a cross-reference table between the three classification systems:
1. tag_engine (3 dimensions: topic, mechanism, methodology)
2. outcome_taxonomy (8 domains: cog, affect, behav, social, physio, neural, health, env)
3. image_tagger (12 categories from feature_cva_mapping.json)

Identifies overlaps, gaps, and generates a reconciliation report.

Usage:
    python scripts/taxonomy_cross_reference.py
"""

import json
import sys
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timezone

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

OUTPUT_DIR = PROJECT_ROOT / "data" / "taxonomy_analysis"


# =============================================================================
# Load All Three Taxonomies
# =============================================================================

def load_outcome_vocab():
    """Load outcome vocabulary."""
    path = PROJECT_ROOT / "contracts" / "outcome_vocab" / "outcome_vocab.json"
    with open(path) as f:
        data = json.load(f)
    
    terms_by_domain = defaultdict(list)
    for term in data["terms"]:
        terms_by_domain[term["domain"]].append({
            "id": term["term_id"],
            "name": term["name"],
            "level": term.get("level", 1),
            "cognates": term.get("cognates", []),
        })
    
    return terms_by_domain


def load_tag_engine():
    """Load tag_engine dimensions from its source."""
    tag_path = PROJECT_ROOT / "src" / "services" / "tag_engine.py"
    
    # Define known tag_engine dimensions based on codebase analysis
    dimensions = {
        "topic": {
            "description": "Research topic tags",
            "tags": ["biophilia", "attention_restoration", "stress_recovery",
                     "wayfinding", "lighting", "acoustic", "thermal_comfort",
                     "color", "prospect_refuge", "social_design",
                     "cognitive_load", "creativity", "circadian",
                     "multisensory", "awe", "complexity", "materiality"],
        },
        "mechanism": {
            "description": "Causal mechanism tags",
            "tags": ["perceptual", "affective", "cognitive", "physiological",
                     "social", "evolutionary", "cultural", "developmental",
                     "neurological", "allostatic"],
        },
        "methodology": {
            "description": "Research methodology tags",
            "tags": ["experiment", "quasi_experiment", "survey",
                     "field_study", "VR", "eye_tracking", "fMRI",
                     "EEG", "physiological_measures", "behavioral_observation",
                     "interview", "mixed_methods", "meta_analysis",
                     "systematic_review", "simulation"],
        },
    }
    
    return dimensions


def load_image_features():
    """Load image feature taxonomy from feature_cva_mapping.json."""
    path = PROJECT_ROOT / "data" / "feature_cva_mapping.json"
    if not path.exists():
        return {}
    
    with open(path) as f:
        data = json.load(f)
    
    features = {}
    for feature_name, mapping in data.get("feature_to_cva", {}).items():
        features[feature_name] = {
            "cva_constraints": mapping.get("constraints", []),
            "related_outcomes": mapping.get("outcomes", []),
            "templates": mapping.get("templates", []),
        }
    
    return features


# =============================================================================
# Cross-Reference Analysis
# =============================================================================

def build_cross_reference(outcome_vocab, tag_engine, image_features):
    """Build cross-reference matrix between all three systems."""
    
    # Define mappings (curated based on semantic analysis)
    cross_ref = {
        "tag_to_outcome": {},
        "tag_to_image": {},
        "outcome_to_image": {},
        "outcome_to_tag": {},
    }
    
    # Tag → Outcome mappings
    tag_outcome_map = {
        "biophilia": ["affect.restorativeness", "health.wellbeing", "env.natural_features"],
        "attention_restoration": ["cog.attention", "affect.restorativeness", "health.recovery"],
        "stress_recovery": ["affect.stress", "physio.stress_hormones", "health.recovery"],
        "wayfinding": ["behav.wayfinding", "cog.spatial_cognition", "cog.cognitive_load"],
        "lighting": ["env.lighting", "physio.alertness", "health.circadian_health"],
        "acoustic": ["env.noise", "env.acoustic_quality", "cog.attention"],
        "thermal_comfort": ["physio.thermal_comfort", "affect.satisfaction"],
        "color": ["affect.mood", "cog.perception", "env.lighting"],
        "prospect_refuge": ["env.prospect_refuge", "affect.safety_perception"],
        "social_design": ["social.interaction", "social.privacy", "social.crowding"],
        "cognitive_load": ["cog.cognitive_load", "cog.performance"],
        "creativity": ["cog.creativity", "behav.engagement"],
        "circadian": ["health.circadian_health", "physio.alertness", "behav.sleep"],
        "multisensory": ["cog.perception", "physio.alertness", "env.acoustic_quality"],
        "awe": ["affect.awe", "affect.fascination", "neural.reward"],
        "complexity": ["env.complexity", "env.coherence", "cog.cognitive_load"],
        "materiality": ["env.materiality", "affect.aesthetic_pleasure"],
    }
    cross_ref["tag_to_outcome"] = tag_outcome_map
    
    # Reverse: outcome → tags
    for tag, outcomes in tag_outcome_map.items():
        for outcome in outcomes:
            if outcome not in cross_ref["outcome_to_tag"]:
                cross_ref["outcome_to_tag"][outcome] = []
            cross_ref["outcome_to_tag"][outcome].append(tag)
    
    # Tag → Image feature mappings
    tag_image_map = {
        "biophilia": ["cnfa.green_view_index", "cnfa.nature_content"],
        "lighting": ["cnfa.light.color_temperature", "cnfa.light.level"],
        "acoustic": ["cnfa.acoustic_quality"],
        "color": ["cnfa.color_palette", "cnfa.material_warmth"],
        "prospect_refuge": ["cnfa.spatial_openness", "cnfa.ceiling_height"],
        "complexity": ["cnfa.visual_complexity", "cnfa.fractal_dimension"],
        "materiality": ["cnfa.material_warmth", "cnfa.surface_texture"],
        "social_design": ["cnfa.density_occupancy"],
        "wayfinding": ["cnfa.spatial_openness", "cnfa.visual_complexity"],
    }
    cross_ref["tag_to_image"] = tag_image_map
    
    # Outcome → Image feature mappings
    outcome_image_map = {
        "affect.restorativeness": ["cnfa.green_view_index", "cnfa.nature_content"],
        "affect.aesthetic_pleasure": ["cnfa.visual_complexity", "cnfa.fractal_dimension", "cnfa.color_palette"],
        "affect.safety_perception": ["cnfa.spatial_openness", "cnfa.light.level"],
        "cog.spatial_cognition": ["cnfa.spatial_openness", "cnfa.ceiling_height"],
        "cog.cognitive_load": ["cnfa.visual_complexity", "cnfa.density_occupancy"],
        "physio.alertness": ["cnfa.light.color_temperature", "cnfa.light.level"],
        "env.complexity": ["cnfa.visual_complexity", "cnfa.fractal_dimension"],
        "env.materiality": ["cnfa.material_warmth", "cnfa.surface_texture"],
        "env.enclosure": ["cnfa.spatial_openness", "cnfa.ceiling_height"],
    }
    cross_ref["outcome_to_image"] = outcome_image_map
    
    return cross_ref


def gap_analysis(outcome_vocab, tag_engine, image_features, cross_ref):
    """Identify gaps in cross-system coverage."""
    gaps = {
        "outcomes_without_tags": [],
        "outcomes_without_images": [],
        "tags_without_outcomes": [],
        "tags_without_images": [],
        "image_features_without_outcomes": [],
        "opaque_zones": [],  # Areas where all three miss
    }
    
    # Outcome terms not linked to any tag
    all_outcome_ids = set()
    for domain_terms in outcome_vocab.values():
        for t in domain_terms:
            if t["level"] >= 2:  # Skip domain roots
                all_outcome_ids.add(t["id"])
    
    linked_outcomes = set()
    for outcomes in cross_ref["tag_to_outcome"].values():
        linked_outcomes.update(outcomes)
    
    gaps["outcomes_without_tags"] = sorted(all_outcome_ids - linked_outcomes)
    
    # Outcomes not linked to image features
    image_linked = set()
    for outcomes in cross_ref.get("outcome_to_image", {}).keys():
        image_linked.add(outcomes)
    
    gaps["outcomes_without_images"] = sorted(all_outcome_ids - image_linked)
    
    # Tags not linked to outcomes
    all_tags = set()
    for dim in tag_engine.values():
        all_tags.update(dim.get("tags", []))
    
    linked_tags = set(cross_ref["tag_to_outcome"].keys())
    gaps["tags_without_outcomes"] = sorted(all_tags - linked_tags)
    
    # Tags not linked to images
    image_linked_tags = set(cross_ref.get("tag_to_image", {}).keys())
    gaps["tags_without_images"] = sorted(all_tags - image_linked_tags)
    
    # Image features not linked to any outcome
    all_image_features = set(image_features.keys()) if image_features else set()
    outcome_linked_images = set()
    for features in cross_ref.get("outcome_to_image", {}).values():
        outcome_linked_images.update(features)
    
    gaps["image_features_without_outcomes"] = sorted(all_image_features - outcome_linked_images)
    
    # Opaque zones: outcome domains with neither tag nor image coverage
    for oid in gaps["outcomes_without_tags"]:
        if oid in gaps["outcomes_without_images"]:
            gaps["opaque_zones"].append(oid)
    
    return gaps


def generate_report(cross_ref, gaps, outcome_vocab, tag_engine, image_features):
    """Generate markdown gap analysis report."""
    lines = [
        "# Taxonomy Cross-Reference & Gap Analysis",
        f"**Generated**: {datetime.now(timezone.utc).isoformat()}",
        "",
        "## System Inventory",
        "",
        f"| System | Coverage |",
        f"|--------|----------|",
        f"| Outcome Vocab | {sum(len(ts) for ts in outcome_vocab.values())} terms across {len(outcome_vocab)} domains |",
        f"| Tag Engine | {sum(len(d.get('tags', [])) for d in tag_engine.values())} tags across {len(tag_engine)} dimensions |",
        f"| Image Features | {len(image_features)} features |",
        "",
        "## Cross-Reference Summary",
        "",
        f"| Mapping | Count |",
        f"|---------|-------|",
        f"| Tag → Outcome links | {sum(len(v) for v in cross_ref['tag_to_outcome'].values())} |",
        f"| Tag → Image links | {sum(len(v) for v in cross_ref['tag_to_image'].values())} |",
        f"| Outcome → Image links | {sum(len(v) for v in cross_ref['outcome_to_image'].values())} |",
        "",
        "## Gap Analysis",
        "",
        f"### Outcomes Without Tag Coverage ({len(gaps['outcomes_without_tags'])})",
        "These outcome constructs have no corresponding tag_engine tag:",
        "",
    ]
    
    for oid in gaps["outcomes_without_tags"][:15]:
        lines.append(f"- `{oid}`")
    if len(gaps["outcomes_without_tags"]) > 15:
        lines.append(f"- ... and {len(gaps['outcomes_without_tags']) - 15} more")
    
    lines.extend([
        "",
        f"### Outcomes Without Image Representation ({len(gaps['outcomes_without_images'])})",
        "These outcomes cannot be visually searched or matched to images:",
        "",
    ])
    for oid in gaps["outcomes_without_images"][:15]:
        lines.append(f"- `{oid}`")
    if len(gaps["outcomes_without_images"]) > 15:
        lines.append(f"- ... and {len(gaps['outcomes_without_images']) - 15} more")
    
    lines.extend([
        "",
        f"### Tags Without Outcome Mapping ({len(gaps['tags_without_outcomes'])})",
        "",
    ])
    for tag in gaps["tags_without_outcomes"]:
        lines.append(f"- `{tag}`")
    
    lines.extend([
        "",
        f"### Opaque Zones ({len(gaps['opaque_zones'])})",
        "Outcomes with **neither** tag nor image coverage — blind spots:",
        "",
    ])
    for oid in gaps["opaque_zones"]:
        lines.append(f"- ⚠️ `{oid}`")
    
    lines.extend([
        "",
        "## Recommendations",
        "",
        "1. **Priority mappings**: Wire opaque zone outcomes to tags and image features",
        "2. **Tag expansion**: Add tags for outcomes like `social.belonging`, `affect.place_attachment`",
        "3. **Image feature gaps**: Add CNfA features for neural and health outcomes",
        "4. **Unified search**: Build query layer that searches all three systems",
    ])
    
    return "\n".join(lines)


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Load
    outcome_vocab = load_outcome_vocab()
    tag_engine = load_tag_engine()
    image_features = load_image_features()
    
    print(f"Loaded: {sum(len(ts) for ts in outcome_vocab.values())} outcomes, "
          f"{sum(len(d.get('tags', [])) for d in tag_engine.values())} tags, "
          f"{len(image_features)} image features")
    
    # Cross-reference
    cross_ref = build_cross_reference(outcome_vocab, tag_engine, image_features)
    
    # Gap analysis
    gaps = gap_analysis(outcome_vocab, tag_engine, image_features, cross_ref)
    
    # Save
    with open(OUTPUT_DIR / "cross_reference.json", "w") as f:
        json.dump(cross_ref, f, indent=2)
    
    with open(OUTPUT_DIR / "gap_analysis.json", "w") as f:
        json.dump(gaps, f, indent=2)
    
    report = generate_report(cross_ref, gaps, outcome_vocab, tag_engine, image_features)
    with open(OUTPUT_DIR / "gap_analysis_report.md", "w") as f:
        f.write(report)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"TAXONOMY CROSS-REFERENCE COMPLETE")
    print(f"{'='*60}")
    print(f"Outcomes without tags: {len(gaps['outcomes_without_tags'])}")
    print(f"Outcomes without images: {len(gaps['outcomes_without_images'])}")
    print(f"Tags without outcomes: {len(gaps['tags_without_outcomes'])}")
    print(f"Opaque zones (blind spots): {len(gaps['opaque_zones'])}")
    print(f"\nReports saved to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
