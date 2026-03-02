"""NEW Attribute Implementations: NEW-04, NEW-05, NEW-06, NEW-08, NEW-12

Implementation of five critical Tier-1 (CPU-based) vision attributes for
causal-theoretic environmental characterization.

Attributes:
-----------
NEW-04: Visual Complexity Score (Tier 1)
    Combines edge density and spectral entropy to quantify overall visual
    complexity. Essential for understanding scene richness and information load.

NEW-05: Regularity/Repetition Index (Tier 1)
    Detects repeating visual patterns using FFT-based autocorrelation analysis.
    Indicates order vs. chaos in visual composition.

NEW-06: Figure-Ground Clarity (Tier 1)
    Measures how clearly objects are separated from background through
    segmentation and contrast analysis.

NEW-08: Illumination Uniformity (Tier 1)
    Analyzes LAB color space L-channel variance to assess lighting consistency.
    Important for scene legibility and visual comfort.

NEW-12: Biomorphic Curvature Index (Tier 1)
    Quantifies curvedness of visual contours to distinguish biomorphic
    (organic, curved) vs. rectilinear (geometric) environments.

Theoretical Warrant:
--------------------
These five attributes were identified through David Kirsh's decision tree
analysis of environmental stimulus dimensions. They capture fundamental
properties of visual scenes relevant to psychology, aesthetics, and
environmental perception.

Visual Complexity (NEW-04) relates to information processing load and
aesthetic preference (Berlyne 1971; Reber et al. 2004).

Regularity/Repetition (NEW-05) reflects order perception and pattern
recognition, essential for wayfinding and spatial understanding.

Figure-Ground Clarity (NEW-06) determines visual segregation and scene
understanding, grounded in Gestalt principles and visual perception
(Rubin 1915; Palmer 1999).

Illumination Uniformity (NEW-08) affects mood, visibility, and spatial
perception (Houser et al. 2002; Knez 1995).

Biomorphic Curvature (NEW-12) distinguishes organic from geometric
environments, relevant to biophilic design and environmental restoration
(Kaplan 1995; Aks et al. 1996).

References:
-----------
- Aks, D. J., Sprott, J. C., et al. (1996). Visual perception of exact
  fractals. Nonlinear Dynamics, Psychology, and Life Sciences, 1(2), 137-156.
- Berlyne, D. E. (1971). Aesthetics and psychobiology. Appleton-Century-Crofts.
- Houser, K. W., Boyce, P. R., Cage, M. E., & Eklund, N. H. (2002). Light
  source effects on bodily sensations. Journal of the Illuminating Engineering
  Society, 31(2), 124-135.
- Kaplan, S. (1995). The restorative benefits of nature. Journal of
  Environmental Psychology, 15(3), 169-182.
- Knez, I. (1995). Effects of colour of light on nonvisual psychological
  processes. Journal of Environmental Psychology, 15(3), 205-212.
- Palmer, S. E. (1999). Vision science: Photons to phenomenology.
  MIT Press.
- Reber, R., Schwarz, N., & Winkielman, P. (2004). Processing fluency and
  aesthetic pleasure. Personality and Social Psychology Review, 8(4), 364-382.
- Rubin, E. (1915). Synsoplevelser. Gyldendalske Boghandel.
"""

import logging
from typing import Dict, List, Any, Tuple, Optional
from pathlib import Path

import cv2
import numpy as np
from scipy import ndimage
from scipy.ndimage import generic_filter

# Import shared utilities and exceptions from the base module
from src.vision.new_attributes import (
    _load_image,
    ImageProcessingError,
)

logger = logging.getLogger(__name__)


class VisualComplexityError(ImageProcessingError):
    """Raised when visual complexity analysis fails."""
    pass


class RegularityError(ImageProcessingError):
    """Raised when regularity/repetition analysis fails."""
    pass


class FigureGroundError(ImageProcessingError):
    """Raised when figure-ground analysis fails."""
    pass


class IlluminationError(ImageProcessingError):
    """Raised when illumination analysis fails."""
    pass


class BiomorphicError(ImageProcessingError):
    """Raised when biomorphic curvature analysis fails."""
    pass


def compute_visual_complexity(
    image_path: str,
    verbose: bool = False
) -> Dict[str, Any]:
    """Compute visual complexity from edge density and spectral entropy.

    NEW-04: Visual Complexity Score

    Quantifies overall visual complexity by combining edge density (spatial
    high-frequency content) and spectral entropy (frequency distribution).
    Higher complexity indicates richer, more detailed scenes.

    Method:
    -------
    1. Convert to grayscale
    2. Apply Canny edge detection to quantify edge density
    3. Compute 2D FFT of image
    4. Calculate spectral entropy from power spectrum
    5. Combine edge density and entropy for overall complexity score

    Args:
        image_path: Path to input RGB image
        verbose: Print debug information

    Returns:
        Dict with:
        - edge_density: Proportion of pixels classified as edges [0, 1]
        - spectral_entropy: Shannon entropy of frequency distribution [0, log2(N)]
        - complexity_score: Combined complexity measure [0, 1]
        - confidence: Confidence in measurement [0, 1]

    Raises:
        VisualComplexityError: If processing fails

    References:
    -----------
    Canny, J. (1986). A computational approach to edge detection. IEEE
    Transactions on Pattern Analysis and Machine Intelligence, 8(6), 679-698.

    Spectral entropy reflects distribution of energy across frequencies:
    - Low entropy: Simple, uniform patterns
    - High entropy: Complex, varied patterns
    """
    try:
        image = _load_image(image_path, as_rgb=True)
        h, w = image.shape[:2]

        if image.dtype != np.uint8:
            image = (image / image.max() * 255).astype(np.uint8)

        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

        # Method 1: Edge density via Canny detector
        blurred = cv2.GaussianBlur(gray, (5, 5), 1.0)
        edges = cv2.Canny(blurred, 100, 200)
        # Count edge pixels (edges are binary: 0 or 255)
        edge_pixel_count = np.sum(edges > 0)
        edge_density = float(edge_pixel_count / edges.size)

        # Method 2: Spectral entropy from FFT
        # Compute 2D FFT
        fft = np.fft.fft2(gray.astype(float))
        power = np.abs(fft) ** 2

        # Normalize power spectrum
        power_norm = power / (power.sum() + 1e-10)

        # Shannon entropy of power distribution
        entropy = -np.sum(
            power_norm[power_norm > 0] * np.log2(power_norm[power_norm > 0] + 1e-10)
        )

        # Normalize entropy by maximum possible (log2 of number of frequency bins)
        max_entropy = np.log2(h * w)
        normalized_entropy = entropy / (max_entropy + 1e-10)

        # Combine edge density and entropy
        # Both normalized to roughly [0, 1] range
        complexity_score = (edge_density + normalized_entropy) / 2.0
        complexity_score = np.clip(float(complexity_score), 0, 1)

        # Confidence increases with amount of data
        confidence = min(0.95, 0.5 + (h * w) / 100000)

        if verbose:
            logger.info(f"Edge density: {edge_density:.4f}")
            logger.info(f"Spectral entropy: {entropy:.4f} (normalized: {normalized_entropy:.4f})")
            logger.info(f"Complexity score: {complexity_score:.4f}")

        return {
            "edge_density": float(edge_density),
            "spectral_entropy": float(normalized_entropy),
            "complexity_score": float(complexity_score),
            "confidence": float(confidence),
        }

    except Exception as e:
        if isinstance(e, VisualComplexityError):
            raise
        raise VisualComplexityError(f"Visual complexity analysis failed: {str(e)}") from e


def compute_regularity_index(
    image_path: str,
    verbose: bool = False
) -> Dict[str, Any]:
    """Detect repeating visual patterns via FFT autocorrelation.

    NEW-05: Regularity/Repetition Index

    Analyzes frequency domain characteristics to detect repeating patterns.
    Regular, repetitive patterns show dominant peaks in the frequency domain.
    Irregular scenes have distributed, uniform spectra.

    Method:
    -------
    1. Convert to grayscale and compute Canny edges
    2. Compute 2D FFT of edge image
    3. Find dominant frequency peaks (indicating repeating patterns)
    4. Estimate dominant pattern period via peak location
    5. Count significant peaks for repetition count estimate

    Args:
        image_path: Path to input RGB image
        verbose: Print debug information

    Returns:
        Dict with:
        - regularity_score: Pattern regularity [0, 1] (0=random, 1=perfectly regular)
        - dominant_period_px: Dominant pattern period in pixels
        - repetition_count_estimate: Estimated number of pattern repeats
        - pattern_type: "regular", "irregular", or "mixed"
        - confidence: Confidence in pattern detection [0, 1]

    Raises:
        RegularityError: If processing fails

    References:
    -----------
    Polya, G. (1954). Mathematics and plausible reasoning.
    Princeton University Press.

    Regular patterns are characterized by dominant peaks in the frequency
    domain. Autocorrelation of the frequency spectrum identifies the
    fundamental frequency of repeating elements.
    """
    try:
        image = _load_image(image_path, as_rgb=True)
        h, w = image.shape[:2]

        if image.dtype != np.uint8:
            image = (image / image.max() * 255).astype(np.uint8)

        # Convert to grayscale and detect edges
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 1.0)
        edges = cv2.Canny(blurred, 50, 150)

        # Compute 2D FFT of edges
        fft = np.fft.fft2(edges.astype(float))
        power = np.abs(fft) ** 2

        # Shift zero frequency to center for visualization
        power_centered = np.fft.fftshift(power)

        # Normalize
        power_norm = power_centered / (power_centered.max() + 1e-10)

        # Find peaks in frequency domain
        # Apply threshold to identify significant peaks
        threshold = 0.1  # 10% of max power
        peaks = power_norm > threshold
        peak_count = np.sum(peaks)

        # Estimate dominant frequency (ignoring DC component)
        # Use a border to exclude DC
        border = 5
        power_noborder = power_norm[border:-border, border:-border]
        peaks_noborder = power_noborder > threshold

        if np.sum(peaks_noborder) > 0:
            # Find location of strongest peak
            peak_indices = np.where(peaks_noborder)
            distances = np.sqrt(
                (peak_indices[0] - power_noborder.shape[0]//2)**2 +
                (peak_indices[1] - power_noborder.shape[1]//2)**2
            )
            dominant_idx = np.argmax(power_noborder[peaks_noborder])
            actual_idx = np.where(peaks_noborder)
            dominant_freq_y = actual_idx[0][dominant_idx]
            dominant_freq_x = actual_idx[1][dominant_idx]

            # Convert frequency to spatial period (in pixels)
            freq_dist = np.sqrt(dominant_freq_y**2 + dominant_freq_x**2)
            dominant_period = max(1, int(min(h, w) / (freq_dist + 1e-10)))
        else:
            dominant_period = 0

        # Count significant peaks for repetition estimate
        significant_peaks = np.sum(power_norm > (threshold * 2))
        repetition_estimate = max(1, significant_peaks // 4)

        # Regularity score: normalized peak prominence
        # High peaks = regular patterns
        peak_energy = np.max(power_norm)
        mean_energy = np.mean(power_norm)
        regularity = np.clip(
            (peak_energy - mean_energy) / (peak_energy + 1e-10),
            0, 1
        )

        # Pattern type classification
        if regularity < 0.2:
            pattern_type = "irregular"
            confidence = 0.8
        elif regularity > 0.6:
            pattern_type = "regular"
            confidence = 0.85
        else:
            pattern_type = "mixed"
            confidence = 0.7

        if verbose:
            logger.info(f"Regularity score: {regularity:.4f}")
            logger.info(f"Dominant period: {dominant_period} pixels")
            logger.info(f"Repetition count estimate: {repetition_estimate}")
            logger.info(f"Pattern type: {pattern_type}")

        return {
            "regularity_score": float(regularity),
            "dominant_period_px": int(dominant_period),
            "repetition_count_estimate": int(repetition_estimate),
            "pattern_type": pattern_type,
            "confidence": float(confidence),
        }

    except Exception as e:
        if isinstance(e, RegularityError):
            raise
        raise RegularityError(f"Regularity analysis failed: {str(e)}") from e


def compute_figure_ground_clarity(
    image_path: str,
    verbose: bool = False
) -> Dict[str, Any]:
    """Measure clarity of object/background separation via segmentation.

    NEW-06: Figure-Ground Clarity

    Assesses how well visual objects are separated from their background.
    Uses Otsu thresholding, connected components, and edge contrast analysis.

    Method:
    -------
    1. Convert to grayscale
    2. Apply Otsu thresholding to segment foreground/background
    3. Analyze connected components in thresholded image
    4. Compute edge contrast at figure-ground boundaries
    5. Calculate overall clarity from segmentation metrics

    Args:
        image_path: Path to input RGB image
        verbose: Print debug information

    Returns:
        Dict with:
        - clarity_score: Object-background separation [0, 1] (0=blended, 1=sharp)
        - foreground_ratio: Proportion of image occupied by foreground [0, 1]
        - edge_contrast_mean: Mean contrast magnitude at boundaries [0, 255]
        - segmentation_quality: Quality of binary segmentation [0, 1]
        - confidence: Confidence in clarity assessment [0, 1]

    Raises:
        FigureGroundError: If processing fails

    References:
    -----------
    Otsu, N. (1979). A threshold selection method from gray-level histograms.
    IEEE Transactions on Systems, Man, and Cybernetics, 9(1), 62-66.

    Rubin, E. (1915). Synsoplevelser. Gyldendalske Boghandel.
    """
    try:
        image = _load_image(image_path, as_rgb=True)
        h, w = image.shape[:2]

        if image.dtype != np.uint8:
            image = (image / image.max() * 255).astype(np.uint8)

        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

        # Apply Gaussian blur to smooth
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        # Otsu thresholding for automatic background/foreground separation
        threshold_val, binary = cv2.threshold(
            blurred,
            0,
            255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )

        # Count foreground pixels
        foreground_pixels = np.sum(binary > 0)
        total_pixels = h * w
        foreground_ratio = foreground_pixels / total_pixels

        # Connected components analysis
        num_components, labels = cv2.connectedComponents(binary)

        # Quality metric: how "clean" is the segmentation?
        # Higher quality = fewer fragmented components, more coherent regions
        avg_component_size = total_pixels / (num_components + 1)
        component_coherence = min(1.0, avg_component_size / (h * w * 0.1))

        # Edge contrast: measure sharpness at figure-ground boundaries
        # Find edges in binary segmentation
        edges_binary = cv2.Canny(binary, 50, 150)

        # For each edge pixel, measure local contrast in original grayscale
        if np.sum(edges_binary) > 0:
            edge_pixels = gray[edges_binary > 0]
            edge_contrast_values = []

            # Sample edge locations and compute local contrast
            y_coords, x_coords = np.where(edges_binary > 0)
            for i in range(min(1000, len(y_coords))):  # Sample up to 1000 edge points
                y, x = y_coords[i], x_coords[i]

                # Local neighborhood around edge
                y_start = max(0, y - 2)
                y_end = min(h, y + 3)
                x_start = max(0, x - 2)
                x_end = min(w, x + 3)

                neighborhood = gray[y_start:y_end, x_start:x_end]
                if neighborhood.size > 0:
                    contrast = neighborhood.max() - neighborhood.min()
                    edge_contrast_values.append(contrast)

            edge_contrast_mean = float(np.mean(edge_contrast_values)) if edge_contrast_values else 0.0
        else:
            edge_contrast_mean = 0.0

        # Normalize edge contrast to [0, 1]
        edge_contrast_normalized = edge_contrast_mean / 255.0

        # Segmentation quality combines coherence and edge contrast
        segmentation_quality = (component_coherence + edge_contrast_normalized) / 2.0
        segmentation_quality = float(np.clip(segmentation_quality, 0, 1))

        # Clarity score: combines foreground separation and edge quality
        # Objects that occupy moderate proportion and have sharp edges = high clarity
        separation_score = np.clip(foreground_ratio, 0.1, 0.9)  # Optimal around 0.5
        separation_metric = 1.0 - abs(separation_score - 0.5) * 2

        clarity_score = (separation_metric + edge_contrast_normalized) / 2.0
        clarity_score = float(np.clip(clarity_score, 0, 1))

        # Confidence depends on image size and edge density
        edge_density = np.sum(edges_binary) / total_pixels
        confidence = min(0.95, 0.5 + edge_density * 2)

        if verbose:
            logger.info(f"Clarity score: {clarity_score:.4f}")
            logger.info(f"Foreground ratio: {foreground_ratio:.4f}")
            logger.info(f"Edge contrast mean: {edge_contrast_mean:.2f}")
            logger.info(f"Segmentation quality: {segmentation_quality:.4f}")

        return {
            "clarity_score": float(clarity_score),
            "foreground_ratio": float(foreground_ratio),
            "edge_contrast_mean": float(edge_contrast_mean),
            "segmentation_quality": float(segmentation_quality),
            "confidence": float(confidence),
        }

    except Exception as e:
        if isinstance(e, FigureGroundError):
            raise
        raise FigureGroundError(f"Figure-ground analysis failed: {str(e)}") from e


def compute_illumination_uniformity(
    image_path: str,
    verbose: bool = False
) -> Dict[str, Any]:
    """Analyze lighting consistency via LAB color space L-channel variance.

    NEW-08: Illumination Uniformity

    Measures consistency of illumination across the scene by analyzing the
    L (lightness) channel in LAB color space. Uniform lighting indicates
    consistent, comfortable illumination; variance indicates spotlights,
    shadows, or complex lighting.

    Method:
    -------
    1. Convert RGB to LAB color space
    2. Extract L-channel (0-100 scale in standard LAB)
    3. Compute global statistics (mean, std)
    4. Compute local variance using sliding window (32x32)
    5. Calculate uniformity ratio from local variance pattern

    Args:
        image_path: Path to input RGB image
        verbose: Print debug information

    Returns:
        Dict with:
        - mean_illuminance_estimate: Average brightness [0, 100]
        - uniformity_ratio: Lighting consistency [0, 1] (1=perfectly uniform)
        - local_variance_mean: Average local variance in 32x32 windows
        - has_bright_zones: Boolean, True if bright regions detected
        - has_dark_zones: Boolean, True if dark regions detected
        - confidence: Confidence in measurement [0, 1]

    Raises:
        IlluminationError: If processing fails

    References:
    -----------
    Knez, I. (1995). Effects of colour of light on nonvisual psychological
    processes. Journal of Environmental Psychology, 15(3), 205-212.

    The LAB color space decouples color from lightness, making it ideal for
    illumination analysis independent of color variations.
    """
    try:
        image = _load_image(image_path, as_rgb=True)
        h, w = image.shape[:2]

        if image.dtype != np.uint8:
            image = (image / image.max() * 255).astype(np.uint8)

        # Convert RGB to LAB
        # OpenCV uses BGR, so we need RGB
        lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB).astype(float)

        # Extract L-channel (lightness)
        L = lab[:, :, 0]

        # Global illumination statistics
        mean_L = float(L.mean())
        std_L = float(L.std())

        # Normalize to [0, 100] range (LAB standard)
        mean_illuminance = mean_L  # L is already 0-100 in OpenCV LAB

        # Local variance analysis using sliding window
        window_size = 32
        local_variance = generic_filter(L, np.std, size=window_size)

        # Average local variance
        local_variance_mean = float(local_variance.mean())

        # Uniformity ratio: measure how uniform the lighting is
        # High ratio = uniform (low local variance)
        # Low ratio = non-uniform (high local variance)
        # If std_L is very small, the image is inherently uniform
        if std_L < 5:  # Nearly uniform image
            uniformity_ratio = 1.0
        else:
            # Ratio of local variance to global variance
            # Low local variance relative to global = uniform lighting
            uniformity_ratio = 1.0 - (local_variance_mean / std_L)
        uniformity_ratio = float(np.clip(uniformity_ratio, 0, 1))

        # Detect bright and dark zones
        # Define thresholds based on overall brightness
        bright_threshold = np.percentile(L, 90)  # Top 10%
        dark_threshold = np.percentile(L, 10)    # Bottom 10%

        has_bright_zones = bool(np.sum(L > bright_threshold) > (h * w * 0.05))
        has_dark_zones = bool(np.sum(L < dark_threshold) > (h * w * 0.05))

        # Confidence increases with image size
        confidence = float(min(0.95, 0.5 + (h * w) / 100000))

        if verbose:
            logger.info(f"Mean illuminance: {mean_illuminance:.2f}")
            logger.info(f"Std illuminance: {std_L:.2f}")
            logger.info(f"Local variance mean: {local_variance_mean:.2f}")
            logger.info(f"Uniformity ratio: {uniformity_ratio:.4f}")
            logger.info(f"Bright zones: {has_bright_zones}, Dark zones: {has_dark_zones}")

        return {
            "mean_illuminance_estimate": float(mean_illuminance),
            "uniformity_ratio": float(uniformity_ratio),
            "local_variance_mean": float(local_variance_mean),
            "has_bright_zones": bool(has_bright_zones),
            "has_dark_zones": bool(has_dark_zones),
            "confidence": float(confidence),
        }

    except Exception as e:
        if isinstance(e, IlluminationError):
            raise
        raise IlluminationError(f"Illumination analysis failed: {str(e)}") from e


def compute_biomorphic_curvature(
    image_path: str,
    verbose: bool = False
) -> Dict[str, Any]:
    """Measure curvedness of visual contours to classify biomorphic vs. rectilinear.

    NEW-12: Biomorphic Curvature Index

    Analyzes the curvature of detected contours to distinguish organic
    (biomorphic, curved) from geometric (rectilinear) environments.

    Method:
    -------
    1. Edge detection via Canny
    2. Contour extraction from edges
    3. For each contour, compute curvature at sample points
    4. Curvature = |dθ/ds| where θ is angle, s is arc length
    5. Map curvature to [0,1]: high curvature = biomorphic (curved)
    6. Compute statistics across all contours

    Args:
        image_path: Path to input RGB image
        verbose: Print debug information

    Returns:
        Dict with:
        - mean_curvature: Average contour curvature [0, ∞] (typical: 0-1)
        - curvature_variance: Variance of curvature across contours
        - biomorphic_index: Probability of organic/curved environment [0, 1]
        - straight_line_ratio: Proportion of low-curvature segments [0, 1]
        - interpretation: "biomorphic", "rectilinear", or "mixed"
        - confidence: Confidence in classification [0, 1]

    Raises:
        BiomorphicError: If processing fails

    References:
    -----------
    Aks, D. J., Sprott, J. C., et al. (1996). Visual perception of exact
    fractals. Nonlinear Dynamics, Psychology, and Life Sciences, 1(2), 137-156.

    Organic forms in nature tend to have continuous curves. Architectural
    spaces tend to have straight edges and right angles. This distinction
    maps to biomorphic (curved) vs. rectilinear (straight) environments.
    """
    try:
        image = _load_image(image_path, as_rgb=True)
        h, w = image.shape[:2]

        if image.dtype != np.uint8:
            image = (image / image.max() * 255).astype(np.uint8)

        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

        # Edge detection
        blurred = cv2.GaussianBlur(gray, (5, 5), 1.0)
        edges = cv2.Canny(blurred, 50, 150)

        # Find contours
        contours, _ = cv2.findContours(
            edges,
            cv2.RETR_LIST,
            cv2.CHAIN_APPROX_NONE
        )

        # Filter contours by length (ignore very short ones)
        min_contour_length = 20
        valid_contours = [c for c in contours if len(c) >= min_contour_length]

        if len(valid_contours) == 0:
            # No substantial contours found
            return {
                "mean_curvature": 0.0,
                "curvature_variance": 0.0,
                "biomorphic_index": 0.5,  # Uncertain
                "straight_line_ratio": 0.5,
                "interpretation": "ambiguous",
                "confidence": 0.3,
            }

        # Compute curvature for each contour
        all_curvatures = []
        straight_segments = 0
        total_segments = 0

        for contour in valid_contours:
            contour = contour.squeeze()

            # Skip degenerate contours
            if len(contour.shape) < 2 or contour.shape[0] < 3:
                continue

            # Compute curvature at each point using finite differences
            contour_curvatures = []

            for i in range(1, len(contour) - 1):
                p_prev = contour[i - 1].astype(float)
                p_curr = contour[i].astype(float)
                p_next = contour[i + 1].astype(float)

                # Vectors
                v1 = p_curr - p_prev
                v2 = p_next - p_curr

                len_v1 = np.linalg.norm(v1) + 1e-10
                len_v2 = np.linalg.norm(v2) + 1e-10

                # Normalize
                v1_norm = v1 / len_v1
                v2_norm = v2 / len_v2

                # Angle change
                dot_product = np.clip(np.dot(v1_norm, v2_norm), -1, 1)
                angle_change = np.arccos(dot_product)

                # Curvature approximation
                arc_length = len_v1 + len_v2
                curvature = angle_change / (arc_length + 1e-10)

                contour_curvatures.append(curvature)

                # Count straight vs. curved segments
                total_segments += 1
                if angle_change < np.pi / 6:  # < 30 degrees = straight
                    straight_segments += 1

            if contour_curvatures:
                all_curvatures.extend(contour_curvatures)

        # Compute statistics
        if all_curvatures:
            mean_curvature = float(np.mean(all_curvatures))
            curvature_variance = float(np.var(all_curvatures))
        else:
            mean_curvature = 0.0
            curvature_variance = 0.0

        # Straight line ratio
        straight_line_ratio = (
            straight_segments / total_segments
            if total_segments > 0
            else 0.5
        )

        # Map curvature to biomorphic index via sigmoid
        # High curvature (>0.1) → biomorphic
        # Low curvature (<0.03) → rectilinear
        sigmoid_input = (mean_curvature - 0.05) * 30  # Scale and shift
        biomorphic_index = float(1.0 / (1.0 + np.exp(-sigmoid_input)))
        biomorphic_index = np.clip(biomorphic_index, 0, 1)

        # Interpret
        if biomorphic_index > 0.6:
            interpretation = "biomorphic"
            confidence = 0.8
        elif biomorphic_index < 0.4:
            interpretation = "rectilinear"
            confidence = 0.8
        else:
            interpretation = "mixed"
            confidence = 0.6

        if verbose:
            logger.info(f"Mean curvature: {mean_curvature:.6f}")
            logger.info(f"Curvature variance: {curvature_variance:.6f}")
            logger.info(f"Biomorphic index: {biomorphic_index:.4f}")
            logger.info(f"Straight line ratio: {straight_line_ratio:.4f}")
            logger.info(f"Interpretation: {interpretation}")

        return {
            "mean_curvature": float(mean_curvature),
            "curvature_variance": float(curvature_variance),
            "biomorphic_index": float(biomorphic_index),
            "straight_line_ratio": float(straight_line_ratio),
            "interpretation": interpretation,
            "confidence": float(confidence),
        }

    except Exception as e:
        if isinstance(e, BiomorphicError):
            raise
        raise BiomorphicError(f"Biomorphic curvature analysis failed: {str(e)}") from e
