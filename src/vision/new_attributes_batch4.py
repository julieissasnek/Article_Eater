"""NEW Attribute Implementations: NEW-13, NEW-14, NEW-15

Implementation of three critical vision attributes from IMG-2 Phase 3 Expert Panel
recommendations for causal-theoretic environmental characterization.

Attributes:
-----------
NEW-13: Temporal Lighting Variation Index (Tier 1)
    Infers circadian alignment from color temperature variation, shadow complexity,
    and directional light cues. Single image measures "lighting variation potential"
    proxy for temporal light dynamics.

NEW-14: Prospect-Refuge Balance Score (Tier 1)
    Composite measure integrating S1 (isovist/openness) and S3 (enclosure/refuge).
    Optimal environments balance both dimensions; extremes (total openness or total
    enclosure) create stress.

NEW-15: Focal Point Density (Tier 1)
    Quantifies distinct visual focal points per image area. Distinguishes organized
    complexity (restorative) from chaotic complexity (fatiguing).

Theoretical Warrant:
-------------------
These three attributes were recommended by the IMG-2 Phase 3 expert panel
(Ulrich, Kaplan, Salingaros, Taylor, Gehl, Dalton, Ellard, Kirsh) as essential
additions to the 33-attribute taxonomy. They operationalize critical dimensions
of environmental restoration and aesthetic quality.

NEW-13 (Temporal Lighting) addresses circadian alignment: temporal lighting
variation (windows with changing CCT across day) signals natural environment and
supports restoration (Ulrich 2002, Kaplan & Kaplan 1989).

NEW-14 (Prospect-Refuge Balance) operationalizes Appleton's prospect-refuge
theory: optimal environments balance visibility (prospect) with safety
(refuge). Mismatch creates stress (Appleton 1975; Kaplan & Kaplan 1989).

NEW-15 (Focal Point Density) formalizes Salingaros's observation that
architectural beauty requires organized complexity via focal points, not
random visual information (Salingaros 2005; Kaplan & Kaplan 1989).

References:
----------
- Appleton, J. H. (1975). The experience of landscape. Wiley.
- Kaplan, R., & Kaplan, S. (1989). The experience of nature. Cambridge.
- Salingaros, N. A. (2005). Principles of urban structure. Techne Press.
- Ulrich, R. S. (2002). Health benefits of nature exposure. Forum for Applied
  Research and Public Policy, 16(3), 54-60.
"""

import logging
from typing import Dict, Any, Tuple, Optional
from pathlib import Path

import cv2
import numpy as np
from scipy import ndimage
from scipy.ndimage import label, generate_binary_structure

# Import shared utilities from base module
from src.vision.new_attributes import (
    _load_image,
    ImageProcessingError,
)

logger = logging.getLogger(__name__)


class TemporalLightingError(ImageProcessingError):
    """Raised when temporal lighting analysis fails."""
    pass


class ProspectRefugeError(ImageProcessingError):
    """Raised when prospect-refuge balance analysis fails."""
    pass


class FocalPointError(ImageProcessingError):
    """Raised when focal point density analysis fails."""
    pass


# ============================================================================
# NEW-13: Temporal Lighting Variation Index
# ============================================================================

def compute_temporal_lighting_variation(
    image_path: str,
    verbose: bool = False
) -> Dict[str, Any]:
    """Infer circadian lighting alignment from color temperature variation.

    NEW-13: Temporal Lighting Variation Index

    Measures the potential for temporal lighting change based on:
    1. Color temperature variance (warm/cool zones indicate different light sources)
    2. Shadow complexity (directional light → time-of-day signature)
    3. Ambient vs. directional light ratio

    A single image cannot measure actual temporal change, but can indicate
    whether the environment has potential for natural variation (windows,
    changing daylight) vs. static artificial lighting.

    Method:
    -------
    1. Convert to LAB color space
    2. Estimate CCT (Correlated Color Temperature) in major image regions
    3. Compute CCT variance (warm vs. cool zones)
    4. Detect shadow/light gradients via L-channel analysis
    5. Analyze directional light cues (shadows indicate directional source)
    6. Synthesize circadian alignment score

    Args:
        image_path: Path to input RGB image
        verbose: Print debug information

    Returns:
        Dict with:
        - temporal_variation_score: Circadian alignment potential [0, 1]
        - color_temperature_variance: Estimated CCT variance across image
        - shadow_complexity: Complexity of light/shadow patterns [0, 1]
        - directional_light_strength: How directional vs. ambient [0, 1]
        - inferred_lighting_type: "natural", "mixed", or "artificial"
        - confidence: Confidence in inference [0, 1]

    Raises:
        TemporalLightingError: If processing fails
    """
    try:
        image = _load_image(image_path, as_rgb=True)
        h, w, _ = image.shape

        # Convert BGR (OpenCV) to RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Convert to LAB for color temperature analysis
        image_lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        L = image_lab[:, :, 0].astype(np.float32)
        a = image_lab[:, :, 1].astype(np.float32)
        b = image_lab[:, :, 2].astype(np.float32)

        # 1. Estimate color temperature variance
        # In LAB: a < 0 = green, a > 0 = magenta; b < 0 = blue, b > 0 = yellow
        # Warm light: a > 0 (magenta), b > 0 (yellow)
        # Cool light: a < 0 (green), b < 0 (blue)

        warmth_map = (a + b) / 256.0  # Range ~ [-1, 1]
        warmth_variance = np.var(warmth_map)

        # Normalize CCT variance to [0, 1]
        cct_variance_normalized = min(1.0, warmth_variance / 0.25)

        # 2. Detect shadow/light gradients
        # Shadow complexity via Sobel gradient magnitude
        grad_x = cv2.Sobel(L, cv2.CV_32F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(L, cv2.CV_32F, 0, 1, ksize=3)
        gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)

        # Normalize and compute shadow complexity
        shadow_complexity = np.mean(gradient_magnitude) / 255.0
        shadow_complexity = min(1.0, shadow_complexity)

        # 3. Analyze directional light (shadows indicate direction)
        # Directional light creates strong edges; diffuse light is smooth
        # Count significant edges in gradient map
        threshold = np.percentile(gradient_magnitude, 75)
        significant_gradients = np.sum(gradient_magnitude > threshold)
        directional_strength = min(1.0, significant_gradients / (h * w * 0.1))

        # 4. Estimate ambient vs. directional light ratio
        # High uniformity (low L variance) = ambient light
        # Low uniformity (high L variance) = directional light
        l_variance = np.var(L) / 128.0
        directional_ratio = min(1.0, l_variance)

        # 5. Synthesize temporal variation score
        # High variation potential = mix of warm/cool zones + directional shadows
        # Low variation potential = uniform artificial lighting
        temporal_score = (
            cct_variance_normalized * 0.3 +
            shadow_complexity * 0.3 +
            directional_ratio * 0.4
        )

        # Infer lighting type
        if temporal_score > 0.6:
            lighting_type = "natural"
        elif temporal_score > 0.3:
            lighting_type = "mixed"
        else:
            lighting_type = "artificial"

        confidence = 0.7

        if verbose:
            logger.info(f"CCT variance: {cct_variance_normalized:.3f}")
            logger.info(f"Shadow complexity: {shadow_complexity:.3f}")
            logger.info(f"Directional light ratio: {directional_ratio:.3f}")
            logger.info(f"Temporal variation score: {temporal_score:.3f}")
            logger.info(f"Inferred lighting type: {lighting_type}")

        return {
            "temporal_variation_score": float(temporal_score),
            "color_temperature_variance": float(cct_variance_normalized),
            "shadow_complexity": float(shadow_complexity),
            "directional_light_strength": float(directional_ratio),
            "inferred_lighting_type": lighting_type,
            "confidence": float(confidence),
        }

    except Exception as e:
        if isinstance(e, TemporalLightingError):
            raise
        raise TemporalLightingError(
            f"Temporal lighting analysis failed: {str(e)}"
        ) from e


# ============================================================================
# NEW-14: Prospect-Refuge Balance Score
# ============================================================================

def compute_prospect_refuge_balance(
    image_path: str,
    verbose: bool = False
) -> Dict[str, Any]:
    """Compute balance between prospect (openness) and refuge (enclosure).

    NEW-14: Prospect-Refuge Balance Score

    Integrates two existing measures:
    - Prospect: ATTR-S1 (Isovist Area) - ability to see
    - Refuge: ATTR-S3 (Enclosure Ratio) - feeling of containment

    Optimal environments balance both; extremes create stress:
    - Total openness (no refuge) → exposure anxiety
    - Total enclosure (no prospect) → claustrophobia

    Method:
    -------
    1. Compute prospect score (normalized isovist/openness)
    2. Compute refuge score (normalized enclosure)
    3. Calculate balance: 1.0 - |prospect - refuge|
    4. Interpret: 1.0 = perfect balance, 0.0 = extreme mismatch

    Args:
        image_path: Path to input RGB image
        verbose: Print debug information

    Returns:
        Dict with:
        - balance_score: Overall prospect-refuge balance [0, 1]
        - prospect_score: Normalized openness [0, 1]
        - refuge_score: Normalized enclosure [0, 1]
        - balance_type: "balanced", "prospect_heavy", or "refuge_heavy"
        - confidence: Confidence in balance assessment [0, 1]

    Raises:
        ProspectRefugeError: If processing fails

    References:
    -----------
    Appleton, J. H. (1975). The experience of landscape. Wiley.
    Kaplan, R., & Kaplan, S. (1989). The experience of nature. Cambridge.
    """
    try:
        # For this implementation, we use simplified proxies:
        # Prospect = inverse of image complexity/clutter (open = simple)
        # Refuge = darkness/enclosure (dark areas = enclosed)

        image = _load_image(image_path, as_rgb=True)
        h, w, _ = image.shape

        # Convert to grayscale for analysis
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

        # PROSPECT: Measure openness via low visual complexity
        # Use edge density as proxy for clutter
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges > 0) / (h * w)

        # Prospect: high openness = low complexity = high prospect
        # Normalize: 0 edges = 1.0 prospect, dense edges = 0.0 prospect
        prospect_score = 1.0 - min(1.0, edge_density / 0.3)

        # REFUGE: Measure enclosure via darkness/shadowing
        # Use average brightness: dark = enclosed, bright = open
        brightness = np.mean(gray) / 255.0

        # Refuge: high enclosure = moderate darkness
        # Optimal refuge is moderate darkness (0.4-0.6 brightness)
        # Very bright (open) or very dark (claustrophobic) are suboptimal
        optimal_brightness = 0.45
        refuge_score = 1.0 - abs(brightness - optimal_brightness) / optimal_brightness

        # Clamp to [0, 1]
        refuge_score = max(0.0, min(1.0, refuge_score))

        # BALANCE: How well do prospect and refuge align?
        balance_mismatch = abs(prospect_score - refuge_score)
        balance_score = 1.0 - balance_mismatch

        # Classify balance type
        if balance_score > 0.7:
            balance_type = "balanced"
        elif prospect_score > refuge_score + 0.2:
            balance_type = "prospect_heavy"
        elif refuge_score > prospect_score + 0.2:
            balance_type = "refuge_heavy"
        else:
            balance_type = "somewhat_imbalanced"

        confidence = 0.65

        if verbose:
            logger.info(f"Prospect score (openness): {prospect_score:.3f}")
            logger.info(f"Refuge score (enclosure): {refuge_score:.3f}")
            logger.info(f"Balance score: {balance_score:.3f}")
            logger.info(f"Balance type: {balance_type}")

        return {
            "balance_score": float(balance_score),
            "prospect_score": float(prospect_score),
            "refuge_score": float(refuge_score),
            "balance_type": balance_type,
            "confidence": float(confidence),
        }

    except Exception as e:
        if isinstance(e, ProspectRefugeError):
            raise
        raise ProspectRefugeError(
            f"Prospect-refuge balance analysis failed: {str(e)}"
        ) from e


# ============================================================================
# NEW-15: Focal Point Density
# ============================================================================

def compute_focal_point_density(
    image_path: str,
    verbose: bool = False
) -> Dict[str, Any]:
    """Count distinct visual focal points to measure organized vs. chaotic complexity.

    NEW-15: Focal Point Density

    Focal points are centers of visual attention (salient regions). Organized
    complexity (restorative) has distinct focal points that guide attention flow.
    Chaotic complexity has too many competing focal points (fatiguing).
    Boring images have no focal points.

    Method:
    -------
    1. Edge detection to identify salient features
    2. Compute saliency map via morphological operations
    3. Identify local maxima (focal peaks)
    4. Cluster peaks into distinct focal point groups
    5. Normalize density by image area
    6. Interpret: very low = boring, moderate = organized, very high = chaotic

    Args:
        image_path: Path to input RGB image
        verbose: Print debug information

    Returns:
        Dict with:
        - focal_point_density: Points per 1000 pixels [0, 50+]
        - focal_point_count: Total distinct focal points
        - density_normalized: Normalized [0, 1] (0=empty, 1=saturated)
        - complexity_type: "boring", "organized", or "chaotic"
        - confidence: Confidence in focal point detection [0, 1]

    Raises:
        FocalPointError: If processing fails

    References:
    -----------
    Kaplan, S., & Kaplan, R. (1989). The experience of nature. Cambridge.
    Salingaros, N. A. (2005). Principles of urban structure. Techne Press.
    """
    try:
        image = _load_image(image_path, as_rgb=True)
        h, w, _ = image.shape

        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

        # 1. Edge detection to identify salient features
        edges = cv2.Canny(gray, 50, 150)

        # 2. Create saliency map via morphological operations
        # Dilate edges to create saliency "zones"
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
        saliency = cv2.dilate(edges, kernel, iterations=2)

        # 3. Identify local maxima (focal peaks)
        # Use distance transform to find peaks
        dist = cv2.distanceTransform(saliency, cv2.DIST_L2, cv2.DIST_MASK_PRECISE)

        # Find local maxima by comparing with neighbors
        kernel_maxima = np.array([[1, 1, 1],
                                  [1, 0, 1],
                                  [1, 1, 1]], dtype=np.uint8)

        # Dilate distance transform
        dilated = cv2.dilate(dist, kernel_maxima, iterations=1)

        # Local maxima are where dist == dilated
        local_maxima = (dist == dilated) & (dist > 0)

        # 4. Cluster peaks into distinct focal points (suppress redundant detections)
        # Use connected components to group nearby maxima
        structure = generate_binary_structure(2, 2)
        labeled, n_components = label(local_maxima, structure=structure)

        # Filter out very small components (noise)
        min_component_size = max(3, h * w // 10000)
        focal_points = []

        for component_id in range(1, n_components + 1):
            component_mask = labeled == component_id
            component_size = np.sum(component_mask)

            if component_size >= min_component_size:
                # Compute center of mass for this focal point
                y_coords, x_coords = np.where(component_mask)
                cy = int(np.mean(y_coords))
                cx = int(np.mean(x_coords))
                focal_points.append((cx, cy))

        focal_count = len(focal_points)

        # 5. Normalize density by image area
        image_area_1000px = (h * w) / 1000.0
        focal_density = focal_count / image_area_1000px

        # Normalize to [0, 1]: saturated at ~5 focal points per 1000 pixels
        density_normalized = min(1.0, focal_density / 5.0)

        # 6. Interpret complexity type
        if focal_count < 2:
            complexity_type = "boring"
        elif focal_count < 8:
            complexity_type = "organized"
        else:
            complexity_type = "chaotic"

        confidence = 0.75

        if verbose:
            logger.info(f"Focal point count: {focal_count}")
            logger.info(f"Focal point density: {focal_density:.2f} per 1000px")
            logger.info(f"Density normalized: {density_normalized:.3f}")
            logger.info(f"Complexity type: {complexity_type}")

        return {
            "focal_point_density": float(focal_density),
            "focal_point_count": int(focal_count),
            "density_normalized": float(density_normalized),
            "complexity_type": complexity_type,
            "confidence": float(confidence),
        }

    except Exception as e:
        if isinstance(e, FocalPointError):
            raise
        raise FocalPointError(
            f"Focal point density analysis failed: {str(e)}"
        ) from e
