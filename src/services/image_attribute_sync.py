"""
image_attribute_sync.py — Auto-sync Image Attributes → IV Taxonomy
===================================================================

Reads the causal_theoretic_image_attributes.json and registers
any new attributes as taxonomy nodes, ensuring that the IV taxonomy
always reflects the latest image attribute definitions.

This creates an auto-update path: when Claude or another agent adds
new image attributes, running this sync will extend the taxonomy
to classify those attributes.

Usage:
  from src.services.image_attribute_sync import sync_image_attributes
  new_count = sync_image_attributes()
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

LOGGER = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent.parent
ATTRIBUTES_PATH = PROJECT_ROOT / "data" / "attributes" / "causal_theoretic_image_attributes.json"

# Mapping from image attribute names → taxonomy domain + parent
# This is the "knowledge bridge" between the image pipeline and the IV taxonomy
_ATTRIBUTE_TO_TAXONOMY: Dict[str, Dict] = {
    "Fractal Dimension (Box-Counting)": {
        "node_id": "natural.biomorphic.fractal",
        "parent_id": "natural.biomorphic",
        "domain": "natural",
        "keywords": ("fractal dimension", "box-counting", "D-value"),
        "parametric_unit": "D",
    },
    "1/f Spectral Slope": {
        "node_id": "natural.biomorphic.spectral_slope",
        "parent_id": "natural.biomorphic",
        "domain": "natural",
        "keywords": ("1/f", "spectral slope", "pink noise", "power spectrum"),
    },
    "Lacunarity": {
        "node_id": "natural.biomorphic.lacunarity",
        "parent_id": "natural.biomorphic",
        "domain": "natural",
        "keywords": ("lacunarity", "gap distribution", "texture gap"),
    },
    "Edge Density and Distribution": {
        "node_id": "spatial.complexity.edge_density",
        "parent_id": "spatial.complexity",
        "domain": "spatial",
        "keywords": ("edge density", "edge distribution", "canny edges"),
    },
    "Correlated Color Temperature (CCT)": {
        "node_id": "luminous.color_temp",
        "parent_id": "luminous",
        "domain": "luminous",
        "keywords": ("CCT", "correlated color temperature"),
        "parametric_unit": "kelvin",
    },
    "Chromatic Distribution (CIE Lab)": {
        "node_id": "luminous.color.chromatic_distribution",
        "parent_id": "luminous.color",
        "domain": "luminous",
        "keywords": ("CIE Lab", "chromatic distribution", "color distribution", "Lab"),
    },
    "Green Chromaticity": {
        "node_id": "natural.vegetation.green_chromaticity",
        "parent_id": "natural.vegetation",
        "domain": "natural",
        "keywords": ("green chromaticity", "vegetation index", "greenness"),
    },
    "Isovist Area and Properties": {
        "node_id": "spatial.openness.isovist",
        "parent_id": "spatial.openness",
        "domain": "spatial",
        "keywords": ("isovist", "isovist area", "visibility polygon", "visual field"),
    },
    "Ceiling Height / Vertical Proportion": {
        "node_id": "spatial.height",
        "parent_id": "spatial",
        "domain": "spatial",
        "keywords": ("ceiling height", "vertical proportion"),
    },
    "Enclosure Ratio": {
        "node_id": "spatial.openness.enclosure_ratio",
        "parent_id": "spatial.openness",
        "domain": "spatial",
        "keywords": ("enclosure ratio", "enclosure", "openness ratio"),
    },
    "Spatial Legibility": {
        "node_id": "spatial.navigation.legibility",
        "parent_id": "spatial.navigation",
        "domain": "spatial",
        "keywords": ("spatial legibility", "legibility", "wayfinding ease"),
    },
    "Material Naturalness Index": {
        "node_id": "material.natural_vs_artificial.naturalness_index",
        "parent_id": "material.natural_vs_artificial",
        "domain": "material",
        "keywords": ("material naturalness", "naturalness index", "natural material percentage"),
    },
    "Haptic Expectation from Visual Input": {
        "node_id": "material.texture.haptic_expectation",
        "parent_id": "material.texture",
        "domain": "material",
        "keywords": ("haptic expectation", "visual-haptic", "tactile expectation"),
        "modality": "haptic",
    },
    "Biomorphic Form Index": {
        "node_id": "natural.biomorphic.form_index",
        "parent_id": "natural.biomorphic",
        "domain": "natural",
        "keywords": ("biomorphic form", "form index", "organic form percentage"),
        "status": "deprecated",
    },
    "Water Feature Presence": {
        "node_id": "natural.water.presence",
        "parent_id": "natural.water",
        "domain": "natural",
        "keywords": ("water feature", "water presence", "fountain", "stream"),
    },
    "Biophilic Design Score (Composite)": {
        "node_id": "natural.biophilic_score",
        "parent_id": "natural",
        "domain": "natural",
        "keywords": ("biophilic design score", "biophilic composite", "nature quotient"),
    },
    "Figure-Ground Clarity": {
        "node_id": "spatial.complexity.figure_ground",
        "parent_id": "spatial.complexity",
        "domain": "spatial",
        "keywords": ("figure-ground", "figure ground clarity", "gestalt"),
    },
    "Symmetry Score": {
        "node_id": "spatial.symmetry.score",
        "parent_id": "spatial.symmetry",
        "domain": "spatial",
        "keywords": ("symmetry score", "bilateral symmetry"),
    },
    "Sky Proportion and Horizon Ratio": {
        "node_id": "spatial.view.sky_proportion",
        "parent_id": "spatial.view",
        "domain": "spatial",
        "keywords": ("sky proportion", "horizon ratio", "sky view factor"),
    },
    "Material Diversity Index": {
        "node_id": "material.diversity",
        "parent_id": "material",
        "domain": "material",
        "keywords": ("material diversity", "material variety", "diversity index"),
    },
    "Vegetation Segmentation Ratio": {
        "node_id": "natural.vegetation.segmentation_ratio",
        "parent_id": "natural.vegetation",
        "domain": "natural",
        "keywords": ("vegetation ratio", "green ratio", "green percentage", "vegetation segmentation"),
    },
    "Scene Depth Estimation (Monocular Cues)": {
        "node_id": "spatial.volume.scene_depth",
        "parent_id": "spatial.volume",
        "domain": "spatial",
        "keywords": ("scene depth", "monocular depth", "depth estimation"),
    },
    "Visual Complexity Score": {
        "node_id": "spatial.complexity.visual_score",
        "parent_id": "spatial.complexity",
        "domain": "spatial",
        "keywords": ("visual complexity score", "information density", "visual entropy"),
    },
    "Regularity/Repetition Index": {
        "node_id": "spatial.symmetry.regularity",
        "parent_id": "spatial.symmetry",
        "domain": "spatial",
        "keywords": ("regularity", "repetition index", "pattern regularity"),
    },
    "Illumination Uniformity": {
        "node_id": "luminous.illuminance.uniformity",
        "parent_id": "luminous.illuminance",
        "domain": "luminous",
        "keywords": ("illumination uniformity", "lighting uniformity", "luminance ratio"),
    },
    "Acoustic Privacy Proxy": {
        "node_id": "acoustic.speech.privacy_proxy",
        "parent_id": "acoustic.speech",
        "domain": "acoustic",
        "keywords": ("acoustic privacy", "speech privacy proxy"),
    },
    "Visual Privacy": {
        "node_id": "social_spatial.privacy.visual",
        "parent_id": "social_spatial.privacy",
        "domain": "social_spatial",
        "keywords": ("visual privacy", "visual exposure", "visibility from outside"),
    },
    "Biomorphic Curvature Index": {
        "node_id": "natural.biomorphic.curvature_index",
        "parent_id": "natural.biomorphic",
        "domain": "natural",
        "keywords": ("biomorphic curvature", "curvature index", "curve ratio"),
    },
    "Temporal Lighting Variation Index": {
        "node_id": "luminous.artificial.temporal_variation",
        "parent_id": "luminous.artificial",
        "domain": "luminous",
        "keywords": ("temporal lighting", "lighting variation", "dynamic lighting index"),
    },
    "Prospect-Refuge Balance Score": {
        "node_id": "spatial.openness.prospect_refuge",
        "parent_id": "spatial.openness",
        "domain": "spatial",
        "keywords": ("prospect-refuge", "prospect refuge balance", "Appleton"),
    },
    "Focal Point Density": {
        "node_id": "spatial.complexity.focal_points",
        "parent_id": "spatial.complexity",
        "domain": "spatial",
        "keywords": ("focal point", "focal density", "attention anchor"),
    },
}


def load_image_attributes() -> List[Dict]:
    """Load image attributes from JSON."""
    if not ATTRIBUTES_PATH.exists():
        LOGGER.warning("Image attributes file not found: %s", ATTRIBUTES_PATH)
        return []
    with open(ATTRIBUTES_PATH) as f:
        data = json.load(f)
    return data.get("attributes", [])


def sync_image_attributes(taxonomy=None) -> int:
    """
    Sync image attributes → taxonomy nodes.
    
    For each image attribute that maps to a known taxonomy node:
    - If the node exists, ensure keywords are up to date
    - If the node doesn't exist, register it
    
    Returns the number of new nodes registered.
    """
    from src.services.stimulus_taxonomy import get_stimulus_taxonomy, TaxonomyNode

    if taxonomy is None:
        taxonomy = get_stimulus_taxonomy()

    attrs = load_image_attributes()
    new_count = 0
    synced_count = 0

    for attr in attrs:
        name = attr.get("name", "")
        status = attr.get("status", "active")

        if status in ("retired",):
            continue

        mapping = _ATTRIBUTE_TO_TAXONOMY.get(name)
        if not mapping:
            LOGGER.debug("No taxonomy mapping for image attribute: %s", name)
            continue

        node_id = mapping["node_id"]
        existing = taxonomy.get(node_id)

        if existing:
            synced_count += 1
            continue

        # Register new node
        parent_id = mapping["parent_id"]
        parent = taxonomy.get(parent_id)
        if not parent:
            LOGGER.warning("Parent node %s not found for image attribute %s", parent_id, name)
            continue

        new_node = TaxonomyNode(
            node_id=node_id,
            label=name,
            parent_id=parent_id,
            depth=parent.depth + 1,
            keywords=mapping.get("keywords", ()),
            parametric_unit=mapping.get("parametric_unit"),
        )
        taxonomy.register_node(new_node)
        new_count += 1
        LOGGER.info("Registered new taxonomy node from image attribute: %s → %s", name, node_id)

    LOGGER.info("Image attribute sync: %d synced, %d new, %d total attrs",
                synced_count, new_count, len(attrs))
    return new_count


def get_iv_keywords_from_attributes() -> Dict[str, List[str]]:
    """
    Get additional IV keywords from image attribute definitions.
    
    This can be used to augment the IV classifier's keyword/semantic maps
    when new attributes are added by Claude or another agent.
    """
    result = {}
    for name, mapping in _ATTRIBUTE_TO_TAXONOMY.items():
        node_id = mapping["node_id"]
        keywords = list(mapping.get("keywords", []))
        result[node_id] = keywords
    return result
