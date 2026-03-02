"""NEW Attribute Implementations: NEW-01, NEW-02, NEW-09, NEW-11

Implementation of four CPU-friendly vision attributes for environmental characterization
using only OpenCV, NumPy, and SciPy (no deep learning models).

Attributes:
-----------
NEW-01: Vegetation Segmentation Ratio
    Detects vegetation using HSV green color segmentation and morphological
    operations. Returns vegetation coverage and spatial distribution.

NEW-02: Scene Depth Estimation (Monocular Cues)
    Estimates relative depth using monocular visual cues (texture gradient,
    perspective convergence, focus blur) without neural networks.

NEW-09: Acoustic Privacy Proxy
    Estimates acoustic characteristics from visual features (proxy measurement).
    Combines enclosure detection, material classification, and volume estimation.

NEW-11: Visual Privacy
    Estimates visual privacy/exposure level from edge density, openness,
    and enclosure detection.

Theoretical Warrant:
-------------------
These attributes operationalize environmental design dimensions identified in
biophilic design and environmental psychology literature.

Vegetation (NEW-01) relates to biophilic design principles and restoration
(Kellert et al. 2008; Kaplan & Kaplan 1989).

Depth estimation (NEW-02) supports spatial perception and comfort (Gibson 1950;
Cutting & Vishton 1995).

Acoustic privacy (NEW-09) and visual privacy (NEW-11) address environmental control
and stress reduction (Evans & Cohen 2004; Sundstrom et al. 1996).

References:
----------
- Cutting, J. E., & Vishton, P. M. (1995). Perceiving layout and knowing
  distances. Handbook of Perception and Cognition, 5, 69-117.
- Evans, G. W., & Cohen, S. (2004). Environmental stress. Handbook of
  Environmental Psychology, 571-610.
- Gibson, J. J. (1950). The perception of the visual world. Houghton Mifflin.
- Kaplan, R., & Kaplan, S. (1989). The experience of nature. Cambridge.
- Kellert, S. R., Heerwagen, J., & Mador, M. (Eds.). (2008). Biophilic design:
  The theory, science and practice of bringing buildings to life. Wiley.
- Sundstrom, E., Town, J. P., Rice, R. W., Osborn, D. P., & Brill, M. (1996).
  Office noise, satisfaction, and performance. Environment and Behavior, 28(2),
  195-222.
"""

import logging
from typing import Dict, List, Any, Tuple, Optional
from pathlib import Path

import cv2
import numpy as np
from scipy import ndimage
from scipy.ndimage import label, find_objects

# Import helpers and exceptions from parent module
from .new_attributes import _load_image, ImageProcessingError

logger = logging.getLogger(__name__)


class VegetationDetectionError(ImageProcessingError):
    """Raised when vegetation detection fails."""
    pass


class DepthEstimationError(ImageProcessingError):
    """Raised when depth estimation fails."""
    pass


class AcousticProxyError(ImageProcessingError):
    """Raised when acoustic proxy analysis fails."""
    pass


class VisualPrivacyError(ImageProcessingError):
    """Raised when visual privacy analysis fails."""
    pass


def compute_vegetation_segmentation(
    image_path: str,
    verbose: bool = False
) -> Dict[str, Any]:
    """Detect vegetation using HSV green color segmentation.

    NEW-01: Vegetation Segmentation Ratio

    Identifies green vegetation in scenes using HSV color space filtering
    and morphological operations. Provides spatial distribution across
    quadrants.

    Method:
    -------
    1. Convert RGB to HSV color space
    2. Define green hue range [35-85] with saturation and value thresholds
    3. Morphological operations (closing, opening) to clean mask
    4. Connected component analysis to identify vegetation regions
    5. Spatial distribution analysis across quadrants

    Args:
        image_path: Path to input RGB image
        verbose: Print debug information

    Returns:
        Dict with:
        - vegetation_ratio: Proportion of image covered by vegetation [0, 1]
        - vegetation_pixels: Number of pixels classified as vegetation
        - total_pixels: Total image size
        - green_chromaticity: Mean green chromaticity of vegetation areas
        - has_vegetation: Boolean indicating vegetation presence
        - vegetation_distribution: Dict with quadrant ratios (top, bottom, left, right)
        - largest_connected_component_size: Size of largest vegetation region
        - component_count: Number of distinct vegetation regions
        - confidence: Confidence in vegetation detection [0, 1]

    Raises:
        VegetationDetectionError: If processing fails

    References:
    -----------
    Kellert, S. R., Heerwagen, J., & Mador, M. (2008). Biophilic design:
    The theory, science and practice of bringing buildings to life. Wiley.

    HSV green range from color analysis of plant materials (H: 35-85 in
    OpenCV HSV, where H is [0-180]).
    """
    try:
        image = _load_image(image_path, as_rgb=True)
        h, w = image.shape[:2]
        total_pixels = h * w

        if image.dtype != np.uint8:
            image = (image / image.max() * 255).astype(np.uint8)

        # Convert to HSV
        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)

        # Green color range in HSV:
        # H: 35-85 (green hues in OpenCV HSV [0-180])
        # S: 40-255 (saturation, vegetation has moderate to high saturation)
        # V: 40-255 (brightness, vegetation is not too dark)
        lower_green = np.array([35, 40, 40])
        upper_green = np.array([85, 255, 255])

        vegetation_mask = cv2.inRange(hsv, lower_green, upper_green)

        # Morphological cleanup
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        vegetation_mask = cv2.morphologyEx(vegetation_mask, cv2.MORPH_CLOSE, kernel)
        vegetation_mask = cv2.morphologyEx(vegetation_mask, cv2.MORPH_OPEN, kernel)

        # Count vegetation pixels
        vegetation_pixels = cv2.countNonZero(vegetation_mask)
        vegetation_ratio = vegetation_pixels / total_pixels

        # Connected component analysis
        labeled_array, num_features = label(vegetation_mask)
        component_count = num_features

        if component_count > 0:
            component_sizes = np.bincount(labeled_array.ravel())
            largest_component_size = component_sizes[1:].max() if len(component_sizes) > 1 else 0
        else:
            largest_component_size = 0

        # Green chromaticity calculation (for vegetation areas only)
        rgb = image
        g_channel = rgb[:, :, 1].astype(float)
        r_channel = rgb[:, :, 0].astype(float)
        b_channel = rgb[:, :, 2].astype(float)

        total_color = r_channel + g_channel + b_channel
        # Avoid division by zero
        total_color[total_color == 0] = 1
        chromaticity_map = g_channel / total_color
        veg_chromaticity_values = chromaticity_map[vegetation_mask > 0]
        green_chromaticity = float(veg_chromaticity_values.mean()) if len(veg_chromaticity_values) > 0 else 0.0
        # Handle NaN values
        if np.isnan(green_chromaticity):
            green_chromaticity = 0.0

        # Spatial distribution across quadrants
        mid_h, mid_w = h // 2, w // 2

        def quadrant_ratio(mask_region):
            return cv2.countNonZero(mask_region) / (mask_region.size) if mask_region.size > 0 else 0.0

        top_half = vegetation_mask[:mid_h, :]
        bottom_half = vegetation_mask[mid_h:, :]
        left_half = vegetation_mask[:, :mid_w]
        right_half = vegetation_mask[:, mid_w:]

        vegetation_distribution = {
            "top": float(quadrant_ratio(top_half)),
            "bottom": float(quadrant_ratio(bottom_half)),
            "left": float(quadrant_ratio(left_half)),
            "right": float(quadrant_ratio(right_half)),
        }

        # Confidence based on vegetation coverage
        if vegetation_ratio < 0.001:
            confidence = 0.95  # Very confident: no vegetation
            has_vegetation = False
        elif vegetation_ratio < 0.05:
            confidence = 0.7  # Some vegetation detected
            has_vegetation = True
        elif vegetation_ratio < 0.5:
            confidence = 0.85  # Good vegetation coverage
            has_vegetation = True
        else:
            confidence = 0.8  # Very high vegetation
            has_vegetation = True

        if verbose:
            logger.info(f"Vegetation ratio: {vegetation_ratio:.3f}")
            logger.info(f"Components: {component_count}")
            logger.info(f"Green chromaticity: {green_chromaticity:.3f}")

        return {
            "vegetation_ratio": float(vegetation_ratio),
            "vegetation_pixels": int(vegetation_pixels),
            "total_pixels": int(total_pixels),
            "green_chromaticity": float(green_chromaticity),
            "has_vegetation": bool(has_vegetation),
            "vegetation_distribution": vegetation_distribution,
            "largest_connected_component_size": int(largest_component_size),
            "component_count": int(component_count),
            "confidence": float(confidence),
        }

    except Exception as e:
        if isinstance(e, VegetationDetectionError):
            raise
        raise VegetationDetectionError(f"Vegetation detection failed: {str(e)}") from e


def compute_depth_estimation_monocular(
    image_path: str,
    verbose: bool = False
) -> Dict[str, Any]:
    """Estimate relative depth using monocular cues (no deep learning).

    NEW-02: Scene Depth Estimation (Monocular Cues)

    Combines three monocular depth cues without neural networks:
    1. Vertical texture gradient (texture density decreases upward)
    2. Perspective convergence (lines converge toward horizon)
    3. Focus/blur gradient (near objects sharper than far)

    Method:
    -------
    Uses edge density vertical profile, Hough line convergence, and
    blur estimation to create a composite depth map.

    Args:
        image_path: Path to input RGB image
        verbose: Print debug information

    Returns:
        Dict with:
        - mean_depth_estimate: Estimated mean depth [0, 1] (0=far, 1=near)
        - depth_gradient_vertical: Depth change from top to bottom
        - depth_gradient_horizontal: Depth change left to right
        - perspective_convergence_score: Strength of perspective cues [0, 1]
        - texture_gradient_score: Texture density gradient strength [0, 1]
        - blur_gradient_score: Focus gradient from near/far [0, 1]
        - scene_type: "deep" (far dominant), "flat", or "mixed"
        - confidence: Confidence in depth estimate [0, 1]

    Raises:
        DepthEstimationError: If processing fails

    References:
    -----------
    Cutting, J. E., & Vishton, P. M. (1995). Perceiving layout and knowing
    distances. Handbook of Perception and Cognition, 5, 69-117.

    Gibson, J. J. (1950). The perception of the visual world. Houghton Mifflin.
    """
    try:
        image = _load_image(image_path, as_rgb=True)
        h, w = image.shape[:2]

        if image.dtype != np.uint8:
            image = (image / image.max() * 255).astype(np.uint8)

        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

        # ---- Cue 1: Texture gradient (vertical) ----
        # Assumption: bottom of image (near) has more texture detail
        edges = cv2.Canny(gray, 50, 150)

        # Divide into top and bottom halves
        mid = h // 2
        top_edges = edges[:mid, :]
        bottom_edges = edges[mid:, :]

        top_texture = cv2.countNonZero(top_edges) / top_edges.size
        bottom_texture = cv2.countNonZero(bottom_edges) / bottom_edges.size

        # Texture gradient: positive if bottom has more texture (typical for near)
        texture_gradient = bottom_texture - top_texture
        texture_gradient_score = min(abs(texture_gradient), 1.0)

        # ---- Cue 2: Perspective convergence ----
        # Detect lines and measure convergence toward horizon
        lines = cv2.HoughLines(edges, rho=1, theta=np.pi/180, threshold=50)

        convergence_score = 0.0
        if lines is not None and len(lines) > 0:
            # Count near-vertical lines (perspective lines in scenes)
            vertical_lines = []
            for line in lines:
                rho, theta = line[0]
                angle = np.degrees(theta)

                # Near-vertical lines: angle close to 90 or -90 degrees
                if 70 < angle < 110 or -110 < angle < -70:
                    vertical_lines.append(rho)

            if len(vertical_lines) >= 2:
                # Variance in rho indicates convergence
                rho_variance = np.var(vertical_lines)
                # Normalize to [0, 1]
                convergence_score = min(rho_variance / (w / 2), 1.0)

        perspective_convergence_score = float(convergence_score)

        # ---- Cue 3: Blur/focus gradient ----
        # Estimate local sharpness using Laplacian variance
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        sharpness = laplacian.var()

        # High sharpness = near, low sharpness = far
        # Normalize relative to a typical sharp image variance
        blur_gradient_score = min(sharpness / 100.0, 1.0)

        # ---- Combine cues into depth estimate ----
        # Weight combination: texture heavily influences perceived depth
        depth_estimate = (
            0.4 * (texture_gradient + 1.0) / 2.0 +  # Normalize texture_gradient to [0, 1]
            0.3 * perspective_convergence_score +
            0.3 * blur_gradient_score
        )
        depth_estimate = np.clip(depth_estimate, 0.0, 1.0)

        # Vertical gradient: positive if deeper at bottom
        vertical_grad = texture_gradient

        # Horizontal gradient: rough estimate from left-right edge distribution
        left_edges = edges[:, :w//2]
        right_edges = edges[:, w//2:]
        left_texture = cv2.countNonZero(left_edges) / left_edges.size
        right_texture = cv2.countNonZero(right_edges) / right_edges.size
        horizontal_grad = right_texture - left_texture

        # Scene classification
        if depth_estimate < 0.3:
            scene_type = "deep"  # Far-dominant
        elif depth_estimate > 0.7:
            scene_type = "flat"  # Near-dominant (unusual, typically means flat perspective)
        else:
            scene_type = "mixed"

        # Confidence: high if multiple cues agree
        cue_agreement = (
            abs(texture_gradient_score - perspective_convergence_score) < 0.3 or
            abs(perspective_convergence_score - blur_gradient_score) < 0.3
        )
        confidence = 0.75 if cue_agreement else 0.55

        if verbose:
            logger.info(f"Depth estimate: {depth_estimate:.3f}")
            logger.info(f"Texture gradient: {texture_gradient:.3f}")
            logger.info(f"Perspective score: {perspective_convergence_score:.3f}")
            logger.info(f"Blur gradient: {blur_gradient_score:.3f}")

        return {
            "mean_depth_estimate": float(depth_estimate),
            "depth_gradient_vertical": float(vertical_grad),
            "depth_gradient_horizontal": float(horizontal_grad),
            "perspective_convergence_score": float(perspective_convergence_score),
            "texture_gradient_score": float(texture_gradient_score),
            "blur_gradient_score": float(blur_gradient_score),
            "scene_type": scene_type,
            "confidence": float(confidence),
        }

    except Exception as e:
        if isinstance(e, DepthEstimationError):
            raise
        raise DepthEstimationError(f"Depth estimation failed: {str(e)}") from e


def compute_acoustic_privacy_proxy(
    image_path: str,
    verbose: bool = False
) -> Dict[str, Any]:
    """Estimate acoustic properties from visual features (proxy measurement).

    NEW-09: Acoustic Privacy Proxy

    IMPORTANT: This is an EXPLICIT PROXY that estimates visual correlates
    of acoustic properties. It does NOT measure actual sound or acoustics.
    It estimates RT60 (reverberation time) category from:
    1. Enclosure level (sky detection, ceiling)
    2. Hard vs. soft surface ratios
    3. Room volume proxy from depth cues
    4. Material reflectivity estimation

    Method:
    -------
    Combines visual cues to estimate acoustic environment category:
    - Open/outdoor (high RT60): low enclosure, sky visible, hard ground
    - Medium (medium RT60): mixed enclosure, varied materials
    - Enclosed/absorbent (low RT60): high enclosure, soft materials

    Args:
        image_path: Path to input RGB image
        verbose: Print debug information

    Returns:
        Dict with:
        - enclosure_ratio: Proportion of image showing enclosed vs. open [0, 1]
        - hard_surface_ratio: Estimated hard (reflective) surface area
        - soft_surface_ratio: Estimated soft (absorbent) surface area
        - estimated_RT60_category: "low" (absorptive), "medium", "high" (reflective)
        - acoustic_privacy_score: Privacy from sound [0, 1]
        - confidence: Confidence in estimate [0, 1]

    Raises:
        AcousticProxyError: If processing fails

    References:
    -----------
    Evans, G. W., & Cohen, S. (2004). Environmental stress. Handbook of
    Environmental Psychology, 571-610.

    Note:
    ----
    This attribute is a VISUAL PROXY and should NOT be used for actual
    acoustic analysis. Acoustic properties depend on material properties,
    geometry, and absorption coefficients that cannot be reliably inferred
    from images alone.
    """
    try:
        image = _load_image(image_path, as_rgb=True)
        h, w = image.shape[:2]
        total_pixels = h * w

        if image.dtype != np.uint8:
            image = (image / image.max() * 255).astype(np.uint8)

        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

        # ---- Enclosure detection (sky, ceiling) ----
        # Sky detection
        lower_blue = np.array([90, 50, 150])
        upper_blue = np.array([170, 255, 255])
        sky_mask = cv2.inRange(hsv, lower_blue, upper_blue)
        sky_ratio = cv2.countNonZero(sky_mask) / total_pixels

        # Dark regions typically are ceilings/indoor
        # Low brightness + medium saturation = ceiling/indoor
        lower_ceiling = np.array([0, 0, 0])
        upper_ceiling = np.array([180, 255, 100])
        ceiling_mask = cv2.inRange(hsv, lower_ceiling, upper_ceiling)
        ceiling_ratio = cv2.countNonZero(ceiling_mask) / total_pixels

        # Enclosure ratio: 1 - sky_ratio (if you see sky, it's open)
        enclosure_ratio = 1.0 - sky_ratio

        # ---- Hard vs. soft surface estimation ----
        # Hard surfaces: high saturation, intermediate brightness (concrete, glass)
        # Soft surfaces: low saturation, intermediate brightness (fabric, carpet)

        # Hard surfaces: moderately saturated, not too dark
        lower_hard = np.array([0, 80, 50])
        upper_hard = np.array([180, 255, 200])
        hard_mask = cv2.inRange(hsv, lower_hard, upper_hard)

        # Soft surfaces: low saturation
        lower_soft = np.array([0, 0, 50])
        upper_soft = np.array([180, 100, 200])
        soft_mask = cv2.inRange(hsv, lower_soft, upper_soft)

        hard_surface_pixels = cv2.countNonZero(hard_mask)
        soft_surface_pixels = cv2.countNonZero(soft_mask)

        hard_surface_ratio = hard_surface_pixels / total_pixels
        soft_surface_ratio = soft_surface_pixels / total_pixels

        # Normalize if sum exceeds 1
        total_surface = hard_surface_ratio + soft_surface_ratio
        if total_surface > 0:
            hard_surface_ratio /= total_surface
            soft_surface_ratio /= total_surface

        # ---- Room volume proxy (from depth) ----
        edges = cv2.Canny(gray, 50, 150)
        edge_density = cv2.countNonZero(edges) / total_pixels

        # High edge density + high enclosure suggests enclosed small room
        volume_proxy = enclosure_ratio * (1.0 - edge_density)

        # ---- Material reflectivity ----
        # Higher saturation and brightness = more reflective
        saturation = hsv[:, :, 1].mean() / 255.0
        brightness = hsv[:, :, 2].mean() / 255.0
        reflectivity = saturation * brightness

        # ---- RT60 category estimation ----
        # RT60: Reverberation time (0.5s typical, up to 3s in live rooms)
        # Estimate based on enclosure, hard/soft ratio, and reflectivity

        # Low RT60 (absorptive, private): high enclosure + soft surfaces
        # Medium RT60: mixed
        # High RT60 (reflective, open): low enclosure OR high reflectivity + hard surfaces

        rt60_score = (
            0.3 * enclosure_ratio +
            0.3 * hard_surface_ratio +
            0.2 * reflectivity +
            0.2 * (edge_density / 0.5)  # More edges = less reflective
        )

        if rt60_score < 0.4:
            rt60_category = "low"  # Absorptive, quiet
            acoustic_privacy_score = 0.8
        elif rt60_score < 0.65:
            rt60_category = "medium"
            acoustic_privacy_score = 0.5
        else:
            rt60_category = "high"  # Reflective, echoey
            acoustic_privacy_score = 0.2

        # Confidence based on clear signals
        if sky_ratio > 0.5 or (enclosure_ratio > 0.8 and soft_surface_ratio > 0.4):
            confidence = 0.7
        else:
            confidence = 0.5

        if verbose:
            logger.info(f"Enclosure ratio: {enclosure_ratio:.3f}")
            logger.info(f"Hard/soft ratio: {hard_surface_ratio:.3f}/{soft_surface_ratio:.3f}")
            logger.info(f"RT60 category: {rt60_category}")
            logger.info(f"Acoustic privacy: {acoustic_privacy_score:.3f}")

        return {
            "enclosure_ratio": float(enclosure_ratio),
            "hard_surface_ratio": float(hard_surface_ratio),
            "soft_surface_ratio": float(soft_surface_ratio),
            "estimated_RT60_category": rt60_category,
            "acoustic_privacy_score": float(acoustic_privacy_score),
            "reflectivity_estimate": float(reflectivity),
            "edge_density": float(edge_density),
            "confidence": float(confidence),
        }

    except Exception as e:
        if isinstance(e, AcousticProxyError):
            raise
        raise AcousticProxyError(f"Acoustic proxy analysis failed: {str(e)}") from e


def compute_visual_privacy(
    image_path: str,
    verbose: bool = False
) -> Dict[str, Any]:
    """Estimate visual privacy/exposure level from image features.

    NEW-11: Visual Privacy

    Estimates how exposed or private a scene appears based on:
    1. Edge density at image periphery (barriers = high edge density)
    2. Sky/ceiling detection (open = low privacy)
    3. Depth of field (short depth = enclosed, more private)
    4. Window/opening detection (bright rectangular regions)

    Method:
    -------
    Combines multiple visual cues into a privacy score. High privacy means
    scene is enclosed with barriers. Low privacy means scene is open
    with clear sightlines.

    Args:
        image_path: Path to input RGB image
        verbose: Print debug information

    Returns:
        Dict with:
        - privacy_score: Privacy level [0, 1] (0=exposed, 1=private)
        - openness_ratio: How much of scene is open space [0, 1]
        - barrier_count: Estimated number of barriers (edges at periphery)
        - sightline_depth: Estimated depth of scene [0, 1]
        - enclosure_level: "open", "semi", or "enclosed"
        - window_ratio: Proportion of bright openings (windows, etc.)
        - confidence: Confidence in estimate [0, 1]

    Raises:
        VisualPrivacyError: If processing fails

    References:
    -----------
    Evans, G. W., & Cohen, S. (2004). Environmental stress. Handbook of
    Environmental Psychology, 571-610.

    Sundstrom, E., Town, J. P., Rice, R. W., Osborn, D. P., & Brill, M. (1996).
    Office noise, satisfaction, and performance. Environment and Behavior,
    28(2), 195-222.
    """
    try:
        image = _load_image(image_path, as_rgb=True)
        h, w = image.shape[:2]
        total_pixels = h * w

        if image.dtype != np.uint8:
            image = (image / image.max() * 255).astype(np.uint8)

        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)

        # ---- Barrier detection (edge density at periphery) ----
        edges = cv2.Canny(gray, 50, 150)

        # Periphery: edges near borders (assume barriers are on edges)
        border_width = max(w // 6, 20)
        border_height = max(h // 6, 20)

        top_border = edges[:border_height, :]
        bottom_border = edges[h-border_height:, :]
        left_border = edges[:, :border_width]
        right_border = edges[:, w-border_width:]

        border_edge_pixels = (
            cv2.countNonZero(top_border) +
            cv2.countNonZero(bottom_border) +
            cv2.countNonZero(left_border) +
            cv2.countNonZero(right_border)
        )

        border_edge_density = border_edge_pixels / (
            (border_width * h * 2) + (border_height * w * 2)
        )

        # Estimate barrier count from edge density
        # Rough heuristic: cluster edges to estimate number of barriers
        barrier_count = max(int(border_edge_density * 20), 0)

        # ---- Openness ratio (inverse of sky detection) ----
        lower_blue = np.array([90, 50, 150])
        upper_blue = np.array([170, 255, 255])
        sky_mask = cv2.inRange(hsv, lower_blue, upper_blue)
        sky_ratio = cv2.countNonZero(sky_mask) / total_pixels
        openness_ratio = sky_ratio

        # ---- Sightline depth (from depth cues) ----
        # Estimate using texture gradient
        mid_h = h // 2
        top_edges = edges[:mid_h, :]
        bottom_edges = edges[mid_h:, :]

        top_texture = cv2.countNonZero(top_edges) / top_edges.size
        bottom_texture = cv2.countNonZero(bottom_edges) / bottom_edges.size

        # Positive gradient (more texture at bottom) suggests depth
        sightline_depth = max(bottom_texture - top_texture, 0.0)

        # ---- Window detection (bright rectangular regions) ----
        # Windows are typically bright (high value in HSV)
        lower_bright = np.array([0, 0, 200])
        upper_bright = np.array([180, 100, 255])
        bright_mask = cv2.inRange(hsv, lower_bright, upper_bright)

        # Look for rectangular bright regions (characteristic of windows)
        # Use morphological operations to identify cohesive regions
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        bright_mask = cv2.morphologyEx(bright_mask, cv2.MORPH_CLOSE, kernel)

        window_pixels = cv2.countNonZero(bright_mask)
        window_ratio = window_pixels / total_pixels

        # ---- Enclosure level classification ----
        # Combine openness and barriers
        enclosure_level_score = (
            (1.0 - openness_ratio) * 0.5 +  # How enclosed (inverted openness)
            border_edge_density * 0.5  # How many barriers
        )

        if enclosure_level_score < 0.2:
            enclosure_level = "open"
        elif enclosure_level_score < 0.6:
            enclosure_level = "semi"
        else:
            enclosure_level = "enclosed"

        # ---- Privacy score ----
        # High privacy: enclosed, many barriers, low openness, short sightline
        privacy_score = (
            (1.0 - openness_ratio) * 0.3 +
            border_edge_density * 0.3 +
            (1.0 - sightline_depth) * 0.2 +
            (1.0 - window_ratio) * 0.2
        )
        privacy_score = np.clip(privacy_score, 0.0, 1.0)

        # Confidence: high if signals are consistent
        signals_agree = (
            abs((1.0 - openness_ratio) - border_edge_density) < 0.3
        )
        confidence = 0.75 if signals_agree else 0.6

        if verbose:
            logger.info(f"Privacy score: {privacy_score:.3f}")
            logger.info(f"Enclosure level: {enclosure_level}")
            logger.info(f"Openness: {openness_ratio:.3f}")
            logger.info(f"Barrier count: {barrier_count}")

        return {
            "privacy_score": float(privacy_score),
            "openness_ratio": float(openness_ratio),
            "barrier_count": int(barrier_count),
            "sightline_depth": float(sightline_depth),
            "enclosure_level": enclosure_level,
            "window_ratio": float(window_ratio),
            "border_edge_density": float(border_edge_density),
            "confidence": float(confidence),
        }

    except Exception as e:
        if isinstance(e, VisualPrivacyError):
            raise
        raise VisualPrivacyError(f"Visual privacy analysis failed: {str(e)}") from e
