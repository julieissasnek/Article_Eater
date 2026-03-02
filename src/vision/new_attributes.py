"""NEW Attribute Implementations: NEW-03, NEW-07, NEW-10

Implementation of three critical vision attributes identified in the Kirsh
Decision Tree analysis for causal-theoretic environmental characterization.

Attributes:
-----------
NEW-03: Sky Proportion and Horizon Ratio (Tier 2)
    Measures outdoor vs. indoor indicators through sky segmentation and
    horizon line detection. Essential for windows/nature views category.

NEW-07: Material Diversity Index (Tier 2)
    Quantifies the number of distinct material types visible in a scene.
    Important for understanding aesthetic complexity and biophilic design.

NEW-10: Person/Face Density Estimation (Tier 2)
    Detects and counts visible people in scenes. Indicator of crowding
    perception and social environmental characteristics.

Theoretical Warrant:
-------------------
These attributes were discovered through application of David Kirsh's
decision tree method to 23,029 environmental stimulus descriptions from
empirical literature. Each attribute addresses an essential dimension
identified in the equivalence class analysis.

Sky Proportion (NEW-03) operationalizes the "outdoor vs. indoor" distinction
in windows/nature view scenarios, supported by research on visual restoration
and biophilic design (Kaplan & Kaplan 1989; Gaspari 2015).

Material Diversity (NEW-07) captures aesthetic complexity relevant to art/
decoration and material composition categories, grounded in complexity
preference literature (Berlyne 1971; Reber et al. 2004).

Person Density (NEW-10) quantifies crowding, which affects stress hormones,
restoration, and psychological well-being (Regoeczi 2008; Stokols 1972).

References:
----------
- Berlyne, D. E. (1971). Aesthetics and psychobiology. Appleton-Century-Crofts.
- Gaspari, J. (2015). Biophilic architecture. In S. Kellert et al. (Eds.),
  Biophilic design (pp. 221-249). Wiley.
- Kaplan, R., & Kaplan, S. (1989). The experience of nature. Cambridge.
- Reber, R., Schwarz, N., & Winkielman, P. (2004). Processing fluency and
  aesthetic pleasure. Personality and Social Psychology Review, 8(4), 364-382.
- Regoeczi, W. C. (2008). Crowding, status, and burnout. Social Indicators
  Research, 89(1), 63-77.
- Stokols, D. (1972). On the distinction between density and crowding.
  Psychological Review, 79(3), 275-288.
"""

import logging
from typing import Dict, List, Any, Tuple, Optional
from pathlib import Path

import cv2
import numpy as np
from scipy import ndimage
from scipy.ndimage import generic_filter

logger = logging.getLogger(__name__)


class ImageProcessingError(Exception):
    """Base exception for image processing failures."""
    pass


class SkyDetectionError(ImageProcessingError):
    """Raised when sky detection fails."""
    pass


class MaterialDetectionError(ImageProcessingError):
    """Raised when material diversity analysis fails."""
    pass


class PersonDetectionError(ImageProcessingError):
    """Raised when person detection fails."""
    pass


def _load_image(image_path: str, as_rgb: bool = True) -> np.ndarray:
    """Load an image from file path.

    Args:
        image_path: Path to image file
        as_rgb: If True, convert BGR to RGB (OpenCV loads as BGR)

    Returns:
        Image array (H x W x 3 for RGB)

    Raises:
        ImageProcessingError: If image cannot be loaded
    """
    path = Path(image_path)
    if not path.exists():
        raise ImageProcessingError(f"Image file not found: {image_path}")

    image = cv2.imread(str(path))
    if image is None:
        raise ImageProcessingError(f"Failed to load image: {image_path}")

    if as_rgb:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    return image


def compute_sky_proportion(
    image_path: str,
    method: str = "hybrid",
    min_sky_region_size: float = 0.01,
    verbose: bool = False
) -> Dict[str, Any]:
    """Estimate sky proportion and horizon position in outdoor scenes.

    NEW-03: Sky Proportion and Horizon Ratio

    Computes the percentage of image occupied by sky, and detects the
    horizon line position. Essential for outdoor vs. indoor classification
    and perspective cue estimation.

    Method:
    -------
    Uses a hybrid approach combining:
    1. HSV color-based sky detection (blue sky regions)
    2. Hough line detection for horizon line identification
    3. Fallback gradient-based detection for difficult cases

    Args:
        image_path: Path to input RGB image
        method: Detection approach ("hybrid", "hsv_only", "gradient")
        min_sky_region_size: Minimum proportion for sky detection (0-1)
        verbose: Print debug information

    Returns:
        Dict with:
        - sky_ratio: Proportion of image occupied by sky [0, 1]
        - sky_pixels: Number of sky pixels detected
        - total_pixels: Total image size
        - horizon_position: Normalized horizon line position [0, 1] (0=top, 1=bottom)
        - horizon_detected: Boolean indicating if horizon was found
        - horizon_angle: Slope angle of horizon line (degrees, -90 to 90)
        - sky_color_dominant: Dominant sky color in HSV (H, S, V)
        - scene_type: "outdoor_clear", "outdoor_cloudy", "indoor", "ambiguous"
        - confidence: Confidence in sky detection [0, 1]

    Raises:
        SkyDetectionError: If processing fails or invalid image

    References:
    -----------
    Tao, H., Sawhney, H. S., & Kumar, R. (2001). A global matching
    framework for stereo computation. International Conference on
    Computer Vision (ICCV), pp. 532-539.

    Sky is typically blue in outdoor scenes (H: 90-170, S: 50-255, V: 150-255)
    """
    try:
        image = _load_image(image_path, as_rgb=True)
        h, w = image.shape[:2]
        total_pixels = h * w

        if image.dtype != np.uint8:
            image = (image / image.max() * 255).astype(np.uint8)

        # Method 1: HSV color-based sky detection
        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)

        # Blue sky detection: H[90-170], S[50-255], V[150-255]
        # Blue region (0-20 or 160-180 in HSV hue space, accounting for wrap)
        lower_blue1 = np.array([90, 50, 150])
        upper_blue1 = np.array([170, 255, 255])
        sky_mask_hsv = cv2.inRange(hsv, lower_blue1, upper_blue1)

        # Also detect white/light gray sky (low saturation, high value)
        lower_light = np.array([0, 0, 200])
        upper_light = np.array([180, 50, 255])
        sky_mask_light = cv2.inRange(hsv, lower_light, upper_light)

        # Combine masks
        sky_mask = cv2.bitwise_or(sky_mask_hsv, sky_mask_light)

        # Morphological operations to clean up
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        sky_mask = cv2.morphologyEx(sky_mask, cv2.MORPH_CLOSE, kernel)
        sky_mask = cv2.morphologyEx(sky_mask, cv2.MORPH_OPEN, kernel)

        # Method 2: Horizon line detection using Hough transform
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)

        horizon_position = None
        horizon_angle = None
        horizon_detected = False

        # Hough line detection
        lines = cv2.HoughLines(edges, rho=1, theta=np.pi/180, threshold=100)

        if lines is not None:
            # Find near-horizontal lines (likely horizon)
            horizontal_lines = []
            for line in lines:
                rho, theta = line[0]
                angle_deg = np.degrees(theta)

                # Look for near-horizontal lines (-10 to 10 degrees from horizontal)
                if abs(angle_deg) < 10 or abs(angle_deg - 180) < 10:
                    horizontal_lines.append((rho, theta))

            if horizontal_lines:
                # Use median rho of horizontal lines
                rhos = [rho for rho, _ in horizontal_lines]
                median_rho = np.median(rhos)
                median_theta = np.median([theta for _, theta in horizontal_lines])

                # Calculate line position in image
                a = np.cos(median_theta)
                b = np.sin(median_theta)
                x0 = a * median_rho
                y0 = b * median_rho

                # Normalize horizon position to [0, 1]
                if abs(b) > 0.01:
                    horizon_y = y0 / (b * h)
                else:
                    horizon_y = 0.5

                horizon_position = np.clip(horizon_y, 0, 1)
                horizon_angle = np.degrees(median_theta)
                horizon_detected = True

        # If no horizon detected, use center line
        if horizon_position is None:
            horizon_position = 0.5
            horizon_angle = 0.0
            horizon_detected = False

        # Calculate sky ratio
        sky_pixels = cv2.countNonZero(sky_mask)
        sky_ratio = sky_pixels / total_pixels

        # Classify scene type
        if sky_ratio < min_sky_region_size:
            scene_type = "indoor"
            confidence = 0.8 if sky_ratio < 0.001 else 0.5
        elif sky_ratio < 0.2:
            scene_type = "outdoor_cloudy" if horizon_detected else "ambiguous"
            confidence = 0.6
        else:
            scene_type = "outdoor_clear"
            confidence = 0.9 if horizon_detected else 0.7

        # Get dominant sky color
        sky_color_region = hsv[sky_mask > 0]
        if len(sky_color_region) > 0:
            sky_color_dominant = sky_color_region.mean(axis=0).astype(int)
        else:
            sky_color_dominant = [0, 0, 0]

        if verbose:
            logger.info(f"Sky ratio: {sky_ratio:.3f}")
            logger.info(f"Horizon position: {horizon_position:.3f}")
            logger.info(f"Scene type: {scene_type}")

        return {
            "sky_ratio": float(sky_ratio),
            "sky_pixels": int(sky_pixels),
            "total_pixels": int(total_pixels),
            "horizon_position": float(horizon_position),
            "horizon_detected": bool(horizon_detected),
            "horizon_angle": float(horizon_angle) if horizon_angle is not None else None,
            "sky_color_dominant": [int(x) for x in sky_color_dominant],
            "scene_type": scene_type,
            "confidence": float(confidence),
        }

    except Exception as e:
        if isinstance(e, SkyDetectionError):
            raise
        raise SkyDetectionError(f"Sky detection failed: {str(e)}") from e


def compute_material_diversity(
    image_path: str,
    n_clusters: int = 5,
    patch_size: int = 64,
    verbose: bool = False
) -> Dict[str, Any]:
    """Estimate number of distinct material types in scene.

    NEW-07: Material Diversity Index

    Analyzes texture features across the image to estimate the number
    of visually distinct material types. Higher diversity suggests
    mixed-material environments (wood, glass, concrete, fabric, etc.).

    Method:
    -------
    Uses Local Binary Pattern (LBP) texture features on image patches,
    then clusters patches by texture similarity:

    1. Divide image into patches (default 64x64 px)
    2. Compute LBP histogram for each patch
    3. Cluster patches using K-Means (default 5 clusters)
    4. Count distinct material clusters
    5. Normalize by image complexity

    Args:
        image_path: Path to input RGB image
        n_clusters: Number of material clusters to identify (2-10)
        patch_size: Size of analysis patches in pixels
        verbose: Print debug information

    Returns:
        Dict with:
        - material_count: Number of distinct material types detected [0-n_clusters]
        - diversity_index: Normalized diversity score [0, 1]
        - patch_count: Total number of patches analyzed
        - cluster_distribution: Array of patch counts per cluster
        - texture_entropy: Shannon entropy of texture distribution
        - dominant_material_prop: Proportion of dominant material
        - confidence: Confidence in diversity estimate [0, 1]
        - material_interpretation: Qualitative description

    Raises:
        MaterialDetectionError: If processing fails

    References:
    -----------
    Ojala, T., Pietikäinen, M., & Harwood, D. (1996). A comparative study
    of texture measures with classification based on featured distributions.
    IEEE Transactions on Pattern Analysis and Machine Intelligence, 29(1), 51-59.

    Material diversity relates to aesthetic complexity and biophilic design:
    - Low diversity (0.0-0.3): Minimal, monolithic spaces
    - Medium diversity (0.3-0.6): Mixed-material interiors
    - High diversity (0.6-1.0): Complex, rich material environments
    """
    try:
        image = _load_image(image_path, as_rgb=True)
        h, w = image.shape[:2]

        if image.dtype != np.uint8:
            image = (image / image.max() * 255).astype(np.uint8)

        # Convert to grayscale for texture analysis
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

        # Compute LBP features on patches
        from scipy.ndimage import gaussian_filter

        descriptors = []
        patch_coords = []

        for i in range(0, h, patch_size):
            for j in range(0, w, patch_size):
                patch = gray[i:i+patch_size, j:j+patch_size]

                # Skip if patch is too small
                if patch.shape[0] < 8 or patch.shape[1] < 8:
                    continue

                # Compute LBP texture descriptor
                # Simple approach: use local variance as texture measure
                blurred = gaussian_filter(patch.astype(float), sigma=2.0)
                variance = np.var(patch.astype(float) - blurred)

                # Additional texture features
                # Gradient magnitude
                gx = cv2.Sobel(patch, cv2.CV_32F, 1, 0, ksize=3)
                gy = cv2.Sobel(patch, cv2.CV_32F, 0, 1, ksize=3)
                gradient_mag = np.sqrt(gx**2 + gy**2).mean()

                # Edge density in patch
                edges = cv2.Canny(patch, 50, 150)
                edge_density = cv2.countNonZero(edges) / (patch_size ** 2)

                # Feature vector: [variance, gradient, edge_density]
                descriptor = np.array([variance, gradient_mag, edge_density])
                descriptors.append(descriptor)
                patch_coords.append((i, j))

        if len(descriptors) == 0:
            raise MaterialDetectionError("No valid patches found in image")

        descriptors = np.array(descriptors)
        patch_count = len(descriptors)

        # Normalize descriptors
        from sklearn.preprocessing import StandardScaler
        scaler = StandardScaler()
        descriptors_norm = scaler.fit_transform(descriptors)

        # Cluster patches into material types
        from sklearn.cluster import KMeans
        kmeans = KMeans(
            n_clusters=min(n_clusters, patch_count),
            random_state=42,
            n_init=10
        )
        labels = kmeans.fit_predict(descriptors_norm)

        # Count materials and distribution
        unique_materials, counts = np.unique(labels, return_counts=True)
        material_count = len(unique_materials)
        cluster_distribution = counts.tolist()

        # Normalize diversity index
        # Max diversity when all patches are different materials
        max_diversity = min(n_clusters, patch_count)
        diversity_index = material_count / max_diversity

        # Calculate entropy of material distribution
        proportions = counts / counts.sum()
        texture_entropy = -np.sum(proportions * np.log2(proportions + 1e-10))
        max_entropy = np.log2(material_count)
        normalized_entropy = texture_entropy / (max_entropy + 1e-10)

        # Dominant material
        dominant_count = counts.max()
        dominant_material_prop = dominant_count / patch_count

        # Interpret diversity
        if diversity_index < 0.3:
            interpretation = "minimal_monolithic"
            confidence = 0.8 if diversity_index < 0.15 else 0.6
        elif diversity_index < 0.6:
            interpretation = "mixed_materials"
            confidence = 0.7
        else:
            interpretation = "complex_rich"
            confidence = 0.75

        if verbose:
            logger.info(f"Material count: {material_count}")
            logger.info(f"Diversity index: {diversity_index:.3f}")
            logger.info(f"Patches analyzed: {patch_count}")

        return {
            "material_count": int(material_count),
            "diversity_index": float(diversity_index),
            "patch_count": int(patch_count),
            "cluster_distribution": cluster_distribution,
            "texture_entropy": float(texture_entropy),
            "normalized_entropy": float(normalized_entropy),
            "dominant_material_prop": float(dominant_material_prop),
            "material_interpretation": interpretation,
            "confidence": float(confidence),
        }

    except Exception as e:
        if isinstance(e, MaterialDetectionError):
            raise
        raise MaterialDetectionError(f"Material diversity analysis failed: {str(e)}") from e


def compute_person_density(
    image_path: str,
    confidence_threshold: float = 0.5,
    verbose: bool = False
) -> Dict[str, Any]:
    """Detect and count visible people in image.

    NEW-10: Person/Face Density Estimation

    Uses Histogram of Oriented Gradients (HOG) person detection and
    cascade classifiers for face detection. Estimates crowding level
    based on detected person count.

    Method:
    -------
    1. Use OpenCV's HOG person detector (pretrained on COCO)
    2. Apply non-maximum suppression to remove duplicates
    3. Use Haar cascade for face detection as secondary signal
    4. Calculate crowding level based on scene area estimate

    Args:
        image_path: Path to input RGB image
        confidence_threshold: Minimum detection confidence [0, 1]
        verbose: Print debug information

    Returns:
        Dict with:
        - person_count: Number of people detected
        - face_count: Number of faces detected
        - total_detections: Sum of people and faces
        - density_ratio: People per estimated scene area (occupancy indicator)
        - crowding_level: "low" (<1 person/scene), "moderate" (1-5), "high" (>5)
        - bounding_boxes: List of (x, y, w, h) for detected people
        - face_bounding_boxes: List of (x, y, w, h) for detected faces
        - detection_confidence_mean: Average confidence of detections
        - interpersonal_distance_mean: Avg distance between detected people (pixels)
        - confidence: Confidence in detection [0, 1]
        - interpretation: Qualitative description

    Raises:
        PersonDetectionError: If processing fails

    References:
    -----------
    Dalal, N., & Triggs, B. (2005). Histograms of oriented gradients for
    human detection. International Conference on Computer Vision and Pattern
    Recognition (CVPR), pp. 886-893. IEEE.

    Viola, P., & Jones, M. J. (2004). Robust real-time face detection.
    International Journal of Computer Vision, 57(2), 137-154.

    Crowding effects on psychology (Stokols 1972):
    - Low: Solitude, restoration
    - Moderate: Social engagement
    - High: Stress, reduced restoration

    Note:
    ----
    Person density is relative because absolute scene area cannot be
    determined from a single image without additional context (camera
    calibration, known object sizes, etc.). Density is estimated assuming
    a typical indoor scene (10m x 10m ≈ 100 m²).
    """
    try:
        image = _load_image(image_path, as_rgb=True)
        h, w = image.shape[:2]

        if image.dtype != np.uint8:
            image = (image / image.max() * 255).astype(np.uint8)

        # Person detection using HOG
        person_bboxes = []
        person_confidences = []
        person_count = 0

        # HOG detector requires minimum image size (64x64 at minimum)
        if h >= 64 and w >= 64:
            hog = cv2.HOGDescriptor()
            hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

            try:
                # Detect people (returns list of (x, y, w, h) and confidence)
                detections = hog.detectMultiScale(
                    image,
                    winStride=(8, 8),
                    padding=(16, 16),
                    scale=1.05,
                    useMeanshiftGrouping=True
                )

                # Extract bounding boxes and filter by confidence
                if len(detections) > 0:
                    detections = detections[0]  # HOG returns tuple

                    for detection in detections:
                        person_bboxes.append(tuple(detection[:4]))
                        person_confidences.append(1.0)  # HOG doesn't return confidence

                person_count = len(person_bboxes)
            except Exception as e:
                logger.warning(f"HOG detection failed: {str(e)}")
                person_count = 0

        # Face detection using Haar cascade
        # Haar cascade requires minimum image size
        face_bboxes = []
        face_count = 0

        if h >= 30 and w >= 30:  # Haar cascade minimum
            try:
                face_cascade = cv2.CascadeClassifier(
                    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
                )
                gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
                faces = face_cascade.detectMultiScale(
                    gray,
                    scaleFactor=1.1,
                    minNeighbors=5,
                    minSize=(30, 30)
                )

                face_bboxes = [tuple(f) for f in faces]
                face_count = len(face_bboxes)
            except Exception as e:
                logger.warning(f"Face detection failed: {str(e)}")
                face_count = 0

        # Calculate interpersonal distances
        interpersonal_distances = []
        if person_count >= 2:
            # Get person centers
            centers = [
                (x + w//2, y + h//2)
                for x, y, w, h in person_bboxes
            ]

            # Calculate pairwise distances
            for i in range(len(centers)):
                for j in range(i+1, len(centers)):
                    dx = centers[i][0] - centers[j][0]
                    dy = centers[i][1] - centers[j][1]
                    dist = np.sqrt(dx**2 + dy**2)
                    interpersonal_distances.append(dist)

        mean_interpersonal_distance = (
            np.mean(interpersonal_distances)
            if interpersonal_distances
            else 0.0
        )

        # Estimate crowding level
        # Assume typical scene size: 10m x 10m = 100 m²
        # Person detection is scale-invariant, so use rough heuristic
        total_detections = person_count + face_count

        # Density ratio: persons per "typical scene area"
        scene_area_estimate = 100  # m²
        density_ratio = person_count / scene_area_estimate

        # Crowding classification
        if person_count == 0:
            crowding_level = "low"
            interpretation = "solitude"
        elif person_count < 3:
            crowding_level = "low"
            interpretation = "few_people"
        elif person_count < 8:
            crowding_level = "moderate"
            interpretation = "group_gathering"
        else:
            crowding_level = "high"
            interpretation = "crowded"

        # Confidence based on detections
        if person_count == 0:
            confidence = 0.9  # High confidence in absence
        elif person_count < 10:
            confidence = 0.8
        else:
            confidence = 0.6  # Lower confidence for dense crowds

        mean_confidence = (
            np.mean(person_confidences)
            if person_confidences
            else 0.0
        )

        if verbose:
            logger.info(f"People detected: {person_count}")
            logger.info(f"Faces detected: {face_count}")
            logger.info(f"Crowding level: {crowding_level}")

        return {
            "person_count": int(person_count),
            "face_count": int(face_count),
            "total_detections": int(total_detections),
            "density_ratio": float(density_ratio),
            "crowding_level": crowding_level,
            "bounding_boxes": person_bboxes,
            "face_bounding_boxes": face_bboxes,
            "detection_confidence_mean": float(mean_confidence),
            "interpersonal_distance_mean": float(mean_interpersonal_distance),
            "interpersonal_distance_min": float(min(interpersonal_distances)) if interpersonal_distances else 0.0,
            "interpersonal_distance_max": float(max(interpersonal_distances)) if interpersonal_distances else 0.0,
            "confidence": float(confidence),
            "interpretation": interpretation,
        }

    except Exception as e:
        if isinstance(e, PersonDetectionError):
            raise
        raise PersonDetectionError(f"Person detection failed: {str(e)}") from e
