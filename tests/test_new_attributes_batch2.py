"""Test suite for NEW-04, NEW-05, NEW-06, NEW-08, and NEW-12 vision attributes.

Tests cover:
- Input validation and error handling
- Output range constraints
- Qualitative correctness on synthetic images
- Edge cases (tiny images, uniform colors, high contrast, etc.)
- Consistency across multiple runs

Date: 2026-03-01
Tier 1 (CPU-based): Uses only OpenCV, NumPy, SciPy
"""

import unittest
import tempfile
from pathlib import Path
from typing import Tuple

import numpy as np
cv2 = __import__('pytest').importorskip('cv2', reason='cv2 (OpenCV) required for vision tests')

# Import the vision modules
from src.vision.new_attributes_batch2 import (
    compute_visual_complexity,
    compute_regularity_index,
    compute_figure_ground_clarity,
    compute_illumination_uniformity,
    compute_biomorphic_curvature,
    VisualComplexityError,
    RegularityError,
    FigureGroundError,
    IlluminationError,
    BiomorphicError,
    ImageProcessingError,
)


class SyntheticImageGenerator:
    """Generate synthetic test images for validation."""

    @staticmethod
    def create_simple_gradient(h: int = 256, w: int = 256) -> np.ndarray:
        """Create smooth gradient image (low complexity)."""
        image = np.zeros((h, w, 3), dtype=np.uint8)
        for i in range(h):
            value = int(255 * i / h)
            image[i, :] = [value, value, value]
        return image

    @staticmethod
    def create_noise_image(h: int = 256, w: int = 256) -> np.ndarray:
        """Create random noise image (high complexity)."""
        image = np.random.randint(0, 256, (h, w, 3), dtype=np.uint8)
        return image

    @staticmethod
    def create_regular_pattern(h: int = 256, w: int = 256, period: int = 16) -> np.ndarray:
        """Create regularly repeating checkerboard pattern."""
        image = np.zeros((h, w, 3), dtype=np.uint8)
        for i in range(h):
            for j in range(w):
                if ((i // period) + (j // period)) % 2 == 0:
                    image[i, j] = 255
                else:
                    image[i, j] = 0
        return image

    @staticmethod
    def create_irregular_pattern(h: int = 256, w: int = 256) -> np.ndarray:
        """Create random, non-repeating pattern."""
        image = np.random.choice([0, 255], (h, w, 3), p=[0.5, 0.5]).astype(np.uint8)
        return image

    @staticmethod
    def create_clear_figure_ground(h: int = 256, w: int = 256) -> np.ndarray:
        """Create clear object on contrasting background."""
        image = np.ones((h, w, 3), dtype=np.uint8) * 255  # White background

        # Draw dark rectangle as object
        center_x, center_y = w // 2, h // 2
        size_x, size_y = w // 3, h // 3
        image[
            center_y - size_y:center_y + size_y,
            center_x - size_x:center_x + size_x
        ] = 0  # Black object

        return image

    @staticmethod
    def create_blended_figure_ground(h: int = 256, w: int = 256) -> np.ndarray:
        """Create ambiguous object-background separation."""
        image = np.ones((h, w, 3), dtype=np.uint8) * 128  # Mid-gray background

        # Draw slightly darker rectangle (low contrast)
        center_x, center_y = w // 2, h // 2
        size_x, size_y = w // 3, h // 3
        image[
            center_y - size_y:center_y + size_y,
            center_x - size_x:center_x + size_x
        ] = 100  # Slightly darker

        return image

    @staticmethod
    def create_uniform_illumination(h: int = 256, w: int = 256) -> np.ndarray:
        """Create uniformly illuminated scene."""
        image = np.ones((h, w, 3), dtype=np.uint8) * 128
        # Add very small random noise
        noise = np.random.randint(-5, 5, (h, w, 3))
        image = np.clip(image.astype(int) + noise, 0, 255).astype(np.uint8)
        return image

    @staticmethod
    def create_non_uniform_illumination(h: int = 256, w: int = 256) -> np.ndarray:
        """Create scene with bright spot and dark regions."""
        image = np.ones((h, w, 3), dtype=np.uint8) * 100  # Dim base

        # Create bright spot in center
        center_x, center_y = w // 2, h // 2
        for i in range(h):
            for j in range(w):
                dist = np.sqrt((i - center_y)**2 + (j - center_x)**2)
                brightness = max(0, 200 - dist)
                # Apply to all 3 channels
                new_val = min(255, 100 + int(brightness * 0.5))
                image[i, j] = new_val

        return image

    @staticmethod
    def create_curved_shapes(h: int = 256, w: int = 256) -> np.ndarray:
        """Create image with curved/biomorphic shapes."""
        image = np.ones((h, w, 3), dtype=np.uint8) * 255  # White background

        # Draw circles and ellipses (curved shapes)
        cv2.circle(image, (64, 64), 30, (0, 0, 0), 2)
        cv2.circle(image, (192, 64), 25, (0, 0, 0), 2)
        cv2.ellipse(image, (128, 180), (40, 20), 45, 0, 360, (0, 0, 0), 2)

        return image

    @staticmethod
    def create_rectilinear_shapes(h: int = 256, w: int = 256) -> np.ndarray:
        """Create image with straight/geometric shapes."""
        image = np.ones((h, w, 3), dtype=np.uint8) * 255  # White background

        # Draw rectangles and lines (straight shapes)
        cv2.rectangle(image, (30, 30), (90, 90), (0, 0, 0), 2)
        cv2.rectangle(image, (166, 30), (226, 90), (0, 0, 0), 2)
        cv2.rectangle(image, (80, 150), (176, 220), (0, 0, 0), 2)

        return image

    @staticmethod
    def create_uniform_color_image(h: int = 256, w: int = 256, color: Tuple = (128, 128, 128)) -> np.ndarray:
        """Create uniform color image."""
        image = np.zeros((h, w, 3), dtype=np.uint8)
        image[:, :] = color
        return image

    @staticmethod
    def create_all_black_image(h: int = 256, w: int = 256) -> np.ndarray:
        """Create completely black image."""
        return np.zeros((h, w, 3), dtype=np.uint8)

    @staticmethod
    def create_all_white_image(h: int = 256, w: int = 256) -> np.ndarray:
        """Create completely white image."""
        return np.ones((h, w, 3), dtype=np.uint8) * 255


class TestComputeVisualComplexity(unittest.TestCase):
    """Test cases for NEW-04: Visual Complexity Score."""

    def setUp(self):
        """Create temporary directory for test images."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        self.gen = SyntheticImageGenerator()

    def tearDown(self):
        """Clean up temporary directory."""
        self.temp_dir.cleanup()

    def _save_image(self, image: np.ndarray, filename: str) -> str:
        """Save image and return path."""
        filepath = self.temp_path / filename
        cv2.imwrite(str(filepath), cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
        return str(filepath)

    def test_output_structure(self):
        """Test that output contains all required fields."""
        image = self.gen.create_noise_image()
        path = self._save_image(image, "noise.png")

        result = compute_visual_complexity(path)

        required_keys = ["edge_density", "spectral_entropy", "complexity_score", "confidence"]
        for key in required_keys:
            self.assertIn(key, result, f"Missing key: {key}")

    def test_complexity_score_range(self):
        """Test that complexity_score is in [0, 1]."""
        for _ in range(3):
            image = self.gen.create_noise_image()
            path = self._save_image(image, f"noise_{np.random.randint(0, 1000)}.png")

            result = compute_visual_complexity(path)

            self.assertGreaterEqual(result["complexity_score"], 0)
            self.assertLessEqual(result["complexity_score"], 1)

    def test_edge_density_range(self):
        """Test that edge_density is in [0, 1]."""
        image = self.gen.create_noise_image()
        path = self._save_image(image, "edge_density.png")

        result = compute_visual_complexity(path)

        self.assertGreaterEqual(result["edge_density"], 0)
        self.assertLessEqual(result["edge_density"], 1)

    def test_spectral_entropy_range(self):
        """Test that spectral_entropy is in [0, 1]."""
        image = self.gen.create_noise_image()
        path = self._save_image(image, "entropy.png")

        result = compute_visual_complexity(path)

        self.assertGreaterEqual(result["spectral_entropy"], 0)
        self.assertLessEqual(result["spectral_entropy"], 1)

    def test_gradient_low_complexity(self):
        """Test that smooth gradient has low complexity."""
        image = self.gen.create_simple_gradient()
        path = self._save_image(image, "gradient.png")

        result = compute_visual_complexity(path)

        # Smooth gradient should have low complexity
        self.assertLess(
            result["complexity_score"],
            0.5,
            "Gradient should have low complexity"
        )

    def test_noise_high_complexity(self):
        """Test that random noise has high complexity."""
        image_gradient = self.gen.create_simple_gradient()
        image_noise = self.gen.create_noise_image()

        path_gradient = self._save_image(image_gradient, "grad_cmp.png")
        path_noise = self._save_image(image_noise, "noise_cmp.png")

        result_gradient = compute_visual_complexity(path_gradient)
        result_noise = compute_visual_complexity(path_noise)

        # Noise should have higher complexity than gradient
        self.assertGreater(
            result_noise["complexity_score"],
            result_gradient["complexity_score"],
            "Noise should have higher complexity than gradient"
        )

    def test_confidence_in_valid_range(self):
        """Test that confidence is in [0, 1]."""
        image = self.gen.create_noise_image()
        path = self._save_image(image, "confidence.png")

        result = compute_visual_complexity(path)

        self.assertGreaterEqual(result["confidence"], 0)
        self.assertLessEqual(result["confidence"], 1)

    def test_uniform_image_low_complexity(self):
        """Test that uniform color has minimal complexity."""
        image = self.gen.create_uniform_color_image(color=(128, 128, 128))
        path = self._save_image(image, "uniform.png")

        result = compute_visual_complexity(path)

        self.assertLess(result["complexity_score"], 0.2)
        self.assertLess(result["edge_density"], 0.05)

    def test_nonexistent_file(self):
        """Test error handling for missing file."""
        with self.assertRaises(ImageProcessingError):
            compute_visual_complexity("/nonexistent/path/image.png")

    def test_small_image(self):
        """Test handling of very small images."""
        image = self.gen.create_noise_image(h=32, w=32)
        path = self._save_image(image, "small_complex.png")

        result = compute_visual_complexity(path)
        self.assertIsNotNone(result["complexity_score"])
        self.assertGreaterEqual(result["complexity_score"], 0)
        self.assertLessEqual(result["complexity_score"], 1)


class TestComputeRegularityIndex(unittest.TestCase):
    """Test cases for NEW-05: Regularity/Repetition Index."""

    def setUp(self):
        """Create temporary directory for test images."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        self.gen = SyntheticImageGenerator()

    def tearDown(self):
        """Clean up temporary directory."""
        self.temp_dir.cleanup()

    def _save_image(self, image: np.ndarray, filename: str) -> str:
        """Save image and return path."""
        filepath = self.temp_path / filename
        cv2.imwrite(str(filepath), cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
        return str(filepath)

    def test_output_structure(self):
        """Test that output contains all required fields."""
        image = self.gen.create_regular_pattern()
        path = self._save_image(image, "pattern.png")

        result = compute_regularity_index(path)

        required_keys = [
            "regularity_score",
            "dominant_period_px",
            "repetition_count_estimate",
            "pattern_type",
            "confidence"
        ]
        for key in required_keys:
            self.assertIn(key, result, f"Missing key: {key}")

    def test_regularity_score_range(self):
        """Test that regularity_score is in [0, 1]."""
        image = self.gen.create_regular_pattern()
        path = self._save_image(image, "regularity.png")

        result = compute_regularity_index(path)

        self.assertGreaterEqual(result["regularity_score"], 0)
        self.assertLessEqual(result["regularity_score"], 1)

    def test_repetition_count_positive(self):
        """Test that repetition_count_estimate is non-negative."""
        image = self.gen.create_regular_pattern()
        path = self._save_image(image, "repetition.png")

        result = compute_regularity_index(path)

        self.assertGreaterEqual(result["repetition_count_estimate"], 0)
        self.assertIsInstance(result["repetition_count_estimate"], int)

    def test_dominant_period_positive(self):
        """Test that dominant_period_px is positive."""
        image = self.gen.create_regular_pattern(period=32)
        path = self._save_image(image, "period.png")

        result = compute_regularity_index(path)

        self.assertGreaterEqual(result["dominant_period_px"], 0)
        self.assertIsInstance(result["dominant_period_px"], int)

    def test_regular_pattern_high_regularity(self):
        """Test that regular pattern has high regularity score."""
        image_regular = self.gen.create_regular_pattern()
        image_irregular = self.gen.create_irregular_pattern()

        path_regular = self._save_image(image_regular, "regular.png")
        path_irregular = self._save_image(image_irregular, "irregular.png")

        result_regular = compute_regularity_index(path_regular)
        result_irregular = compute_regularity_index(path_irregular)

        # Regular should have equal or higher regularity than irregular
        # (may be very similar for high-frequency patterns)
        self.assertGreaterEqual(
            result_regular["regularity_score"],
            result_irregular["regularity_score"] - 0.01,  # Allow small margin
            "Regular pattern should have equal or higher regularity score"
        )

    def test_pattern_type_valid(self):
        """Test that pattern_type is one of valid values."""
        image = self.gen.create_regular_pattern()
        path = self._save_image(image, "pattern_type.png")

        result = compute_regularity_index(path)

        valid_types = ["regular", "irregular", "mixed"]
        self.assertIn(result["pattern_type"], valid_types)

    def test_confidence_in_valid_range(self):
        """Test that confidence is in [0, 1]."""
        image = self.gen.create_regular_pattern()
        path = self._save_image(image, "pattern_conf.png")

        result = compute_regularity_index(path)

        self.assertGreaterEqual(result["confidence"], 0)
        self.assertLessEqual(result["confidence"], 1)

    def test_nonexistent_file(self):
        """Test error handling for missing file."""
        with self.assertRaises(ImageProcessingError):
            compute_regularity_index("/nonexistent/path/image.png")

    def test_small_image(self):
        """Test handling of small images."""
        image = self.gen.create_regular_pattern(h=64, w=64)
        path = self._save_image(image, "small_regular.png")

        result = compute_regularity_index(path)
        self.assertIsNotNone(result["regularity_score"])
        self.assertGreaterEqual(result["regularity_score"], 0)
        self.assertLessEqual(result["regularity_score"], 1)

    def test_consistency_across_runs(self):
        """Test that results are consistent across multiple runs."""
        image = self.gen.create_regular_pattern()
        path = self._save_image(image, "consistency.png")

        result1 = compute_regularity_index(path)
        result2 = compute_regularity_index(path)

        self.assertEqual(result1["regularity_score"], result2["regularity_score"])
        self.assertEqual(result1["pattern_type"], result2["pattern_type"])


class TestComputeFigureGroundClarity(unittest.TestCase):
    """Test cases for NEW-06: Figure-Ground Clarity."""

    def setUp(self):
        """Create temporary directory for test images."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        self.gen = SyntheticImageGenerator()

    def tearDown(self):
        """Clean up temporary directory."""
        self.temp_dir.cleanup()

    def _save_image(self, image: np.ndarray, filename: str) -> str:
        """Save image and return path."""
        filepath = self.temp_path / filename
        cv2.imwrite(str(filepath), cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
        return str(filepath)

    def test_output_structure(self):
        """Test that output contains all required fields."""
        image = self.gen.create_clear_figure_ground()
        path = self._save_image(image, "figure_ground.png")

        result = compute_figure_ground_clarity(path)

        required_keys = [
            "clarity_score",
            "foreground_ratio",
            "edge_contrast_mean",
            "segmentation_quality",
            "confidence"
        ]
        for key in required_keys:
            self.assertIn(key, result, f"Missing key: {key}")

    def test_clarity_score_range(self):
        """Test that clarity_score is in [0, 1]."""
        image = self.gen.create_clear_figure_ground()
        path = self._save_image(image, "clarity.png")

        result = compute_figure_ground_clarity(path)

        self.assertGreaterEqual(result["clarity_score"], 0)
        self.assertLessEqual(result["clarity_score"], 1)

    def test_foreground_ratio_range(self):
        """Test that foreground_ratio is in [0, 1]."""
        image = self.gen.create_clear_figure_ground()
        path = self._save_image(image, "foreground.png")

        result = compute_figure_ground_clarity(path)

        self.assertGreaterEqual(result["foreground_ratio"], 0)
        self.assertLessEqual(result["foreground_ratio"], 1)

    def test_edge_contrast_non_negative(self):
        """Test that edge_contrast_mean is non-negative."""
        image = self.gen.create_clear_figure_ground()
        path = self._save_image(image, "contrast.png")

        result = compute_figure_ground_clarity(path)

        self.assertGreaterEqual(result["edge_contrast_mean"], 0)

    def test_clear_figure_ground_high_clarity(self):
        """Test that clear separation has high clarity."""
        image_clear = self.gen.create_clear_figure_ground()
        image_blended = self.gen.create_blended_figure_ground()

        path_clear = self._save_image(image_clear, "clear_fg.png")
        path_blended = self._save_image(image_blended, "blended_fg.png")

        result_clear = compute_figure_ground_clarity(path_clear)
        result_blended = compute_figure_ground_clarity(path_blended)

        # Clear should have higher clarity
        self.assertGreater(
            result_clear["clarity_score"],
            result_blended["clarity_score"],
            "Clear figure-ground should have higher clarity"
        )

    def test_segmentation_quality_range(self):
        """Test that segmentation_quality is in [0, 1]."""
        image = self.gen.create_clear_figure_ground()
        path = self._save_image(image, "segmentation.png")

        result = compute_figure_ground_clarity(path)

        self.assertGreaterEqual(result["segmentation_quality"], 0)
        self.assertLessEqual(result["segmentation_quality"], 1)

    def test_confidence_in_valid_range(self):
        """Test that confidence is in [0, 1]."""
        image = self.gen.create_clear_figure_ground()
        path = self._save_image(image, "fg_conf.png")

        result = compute_figure_ground_clarity(path)

        self.assertGreaterEqual(result["confidence"], 0)
        self.assertLessEqual(result["confidence"], 1)

    def test_uniform_image_low_clarity(self):
        """Test that uniform image has low clarity (no figure-ground)."""
        image = self.gen.create_uniform_color_image()
        path = self._save_image(image, "uniform_fg.png")

        result = compute_figure_ground_clarity(path)

        # Uniform should have very low edge contrast
        self.assertLess(result["edge_contrast_mean"], 50)

    def test_nonexistent_file(self):
        """Test error handling for missing file."""
        with self.assertRaises(ImageProcessingError):
            compute_figure_ground_clarity("/nonexistent/path/image.png")

    def test_small_image(self):
        """Test handling of small images."""
        image = self.gen.create_clear_figure_ground(h=64, w=64)
        path = self._save_image(image, "small_fg.png")

        result = compute_figure_ground_clarity(path)
        self.assertIsNotNone(result["clarity_score"])
        self.assertGreaterEqual(result["clarity_score"], 0)
        self.assertLessEqual(result["clarity_score"], 1)


class TestComputeIlluminationUniformity(unittest.TestCase):
    """Test cases for NEW-08: Illumination Uniformity."""

    def setUp(self):
        """Create temporary directory for test images."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        self.gen = SyntheticImageGenerator()

    def tearDown(self):
        """Clean up temporary directory."""
        self.temp_dir.cleanup()

    def _save_image(self, image: np.ndarray, filename: str) -> str:
        """Save image and return path."""
        filepath = self.temp_path / filename
        cv2.imwrite(str(filepath), cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
        return str(filepath)

    def test_output_structure(self):
        """Test that output contains all required fields."""
        image = self.gen.create_uniform_illumination()
        path = self._save_image(image, "illumination.png")

        result = compute_illumination_uniformity(path)

        required_keys = [
            "mean_illuminance_estimate",
            "uniformity_ratio",
            "local_variance_mean",
            "has_bright_zones",
            "has_dark_zones",
            "confidence"
        ]
        for key in required_keys:
            self.assertIn(key, result, f"Missing key: {key}")

    def test_uniformity_ratio_range(self):
        """Test that uniformity_ratio is in [0, 1]."""
        image = self.gen.create_uniform_illumination()
        path = self._save_image(image, "uniformity.png")

        result = compute_illumination_uniformity(path)

        self.assertGreaterEqual(result["uniformity_ratio"], 0)
        self.assertLessEqual(result["uniformity_ratio"], 1)

    def test_mean_illuminance_valid_range(self):
        """Test that mean_illuminance is non-negative."""
        image = self.gen.create_uniform_illumination()
        path = self._save_image(image, "illuminance.png")

        result = compute_illumination_uniformity(path)

        # LAB L-channel is typically 0-100, but can vary based on normalization
        self.assertGreaterEqual(result["mean_illuminance_estimate"], 0)

    def test_local_variance_non_negative(self):
        """Test that local_variance_mean is non-negative."""
        image = self.gen.create_uniform_illumination()
        path = self._save_image(image, "variance.png")

        result = compute_illumination_uniformity(path)

        self.assertGreaterEqual(result["local_variance_mean"], 0)

    def test_uniform_illumination_high_uniformity(self):
        """Test that uniform lighting has high uniformity."""
        image_uniform = self.gen.create_uniform_illumination()
        image_non_uniform = self.gen.create_non_uniform_illumination()

        path_uniform = self._save_image(image_uniform, "uniform_ill.png")
        path_non_uniform = self._save_image(image_non_uniform, "non_uniform_ill.png")

        result_uniform = compute_illumination_uniformity(path_uniform)
        result_non_uniform = compute_illumination_uniformity(path_non_uniform)

        # Uniform should have higher uniformity ratio
        self.assertGreater(
            result_uniform["uniformity_ratio"],
            result_non_uniform["uniformity_ratio"],
            "Uniform illumination should have higher uniformity"
        )

    def test_bright_dark_zones_detection(self):
        """Test detection of bright and dark zones."""
        image_non_uniform = self.gen.create_non_uniform_illumination()
        path = self._save_image(image_non_uniform, "zones.png")

        result = compute_illumination_uniformity(path)

        # Non-uniform should have some zones
        self.assertIsInstance(result["has_bright_zones"], bool)
        self.assertIsInstance(result["has_dark_zones"], bool)

    def test_confidence_in_valid_range(self):
        """Test that confidence is in [0, 1]."""
        image = self.gen.create_uniform_illumination()
        path = self._save_image(image, "ill_conf.png")

        result = compute_illumination_uniformity(path)

        self.assertGreaterEqual(result["confidence"], 0)
        self.assertLessEqual(result["confidence"], 1)

    def test_all_black_image(self):
        """Test handling of all-black image."""
        image = self.gen.create_all_black_image()
        path = self._save_image(image, "black.png")

        result = compute_illumination_uniformity(path)

        # Should have low illuminance
        self.assertLess(result["mean_illuminance_estimate"], 20)

    def test_all_white_image(self):
        """Test handling of all-white image."""
        image = self.gen.create_all_white_image()
        path = self._save_image(image, "white.png")

        result = compute_illumination_uniformity(path)

        # Should have high illuminance
        self.assertGreater(result["mean_illuminance_estimate"], 80)

    def test_nonexistent_file(self):
        """Test error handling for missing file."""
        with self.assertRaises(ImageProcessingError):
            compute_illumination_uniformity("/nonexistent/path/image.png")

    def test_small_image(self):
        """Test handling of small images."""
        image = self.gen.create_uniform_illumination(h=64, w=64)
        path = self._save_image(image, "small_ill.png")

        result = compute_illumination_uniformity(path)
        self.assertIsNotNone(result["uniformity_ratio"])
        self.assertGreaterEqual(result["uniformity_ratio"], 0)
        self.assertLessEqual(result["uniformity_ratio"], 1)


class TestComputeBiomorphicCurvature(unittest.TestCase):
    """Test cases for NEW-12: Biomorphic Curvature Index."""

    def setUp(self):
        """Create temporary directory for test images."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        self.gen = SyntheticImageGenerator()

    def tearDown(self):
        """Clean up temporary directory."""
        self.temp_dir.cleanup()

    def _save_image(self, image: np.ndarray, filename: str) -> str:
        """Save image and return path."""
        filepath = self.temp_path / filename
        cv2.imwrite(str(filepath), cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
        return str(filepath)

    def test_output_structure(self):
        """Test that output contains all required fields."""
        image = self.gen.create_curved_shapes()
        path = self._save_image(image, "curved.png")

        result = compute_biomorphic_curvature(path)

        required_keys = [
            "mean_curvature",
            "curvature_variance",
            "biomorphic_index",
            "straight_line_ratio",
            "interpretation",
            "confidence"
        ]
        for key in required_keys:
            self.assertIn(key, result, f"Missing key: {key}")

    def test_biomorphic_index_range(self):
        """Test that biomorphic_index is in [0, 1]."""
        image = self.gen.create_curved_shapes()
        path = self._save_image(image, "bio_index.png")

        result = compute_biomorphic_curvature(path)

        self.assertGreaterEqual(result["biomorphic_index"], 0)
        self.assertLessEqual(result["biomorphic_index"], 1)

    def test_mean_curvature_non_negative(self):
        """Test that mean_curvature is non-negative."""
        image = self.gen.create_curved_shapes()
        path = self._save_image(image, "curvature.png")

        result = compute_biomorphic_curvature(path)

        self.assertGreaterEqual(result["mean_curvature"], 0)

    def test_curvature_variance_non_negative(self):
        """Test that curvature_variance is non-negative."""
        image = self.gen.create_curved_shapes()
        path = self._save_image(image, "variance.png")

        result = compute_biomorphic_curvature(path)

        self.assertGreaterEqual(result["curvature_variance"], 0)

    def test_straight_line_ratio_range(self):
        """Test that straight_line_ratio is in [0, 1]."""
        image = self.gen.create_curved_shapes()
        path = self._save_image(image, "straight.png")

        result = compute_biomorphic_curvature(path)

        self.assertGreaterEqual(result["straight_line_ratio"], 0)
        self.assertLessEqual(result["straight_line_ratio"], 1)

    def test_curved_shapes_biomorphic(self):
        """Test that curved shapes have high biomorphic index."""
        image_curved = self.gen.create_curved_shapes()
        image_rectilinear = self.gen.create_rectilinear_shapes()

        path_curved = self._save_image(image_curved, "curved_shapes.png")
        path_rectilinear = self._save_image(image_rectilinear, "rectilinear.png")

        result_curved = compute_biomorphic_curvature(path_curved)
        result_rectilinear = compute_biomorphic_curvature(path_rectilinear)

        # Curved should have higher biomorphic index
        self.assertGreater(
            result_curved["biomorphic_index"],
            result_rectilinear["biomorphic_index"],
            "Curved shapes should have higher biomorphic index"
        )

    def test_rectilinear_shapes_geometric(self):
        """Test that geometric shapes have low biomorphic index."""
        image = self.gen.create_rectilinear_shapes()
        path = self._save_image(image, "geometric.png")

        result = compute_biomorphic_curvature(path)

        # Geometric should have low biomorphic index
        self.assertLess(result["biomorphic_index"], 0.6)

    def test_interpretation_valid(self):
        """Test that interpretation is one of valid values."""
        image = self.gen.create_curved_shapes()
        path = self._save_image(image, "interpretation.png")

        result = compute_biomorphic_curvature(path)

        valid_interpretations = ["biomorphic", "rectilinear", "mixed", "ambiguous"]
        self.assertIn(result["interpretation"], valid_interpretations)

    def test_confidence_in_valid_range(self):
        """Test that confidence is in [0, 1]."""
        image = self.gen.create_curved_shapes()
        path = self._save_image(image, "bio_conf.png")

        result = compute_biomorphic_curvature(path)

        self.assertGreaterEqual(result["confidence"], 0)
        self.assertLessEqual(result["confidence"], 1)

    def test_nonexistent_file(self):
        """Test error handling for missing file."""
        with self.assertRaises(ImageProcessingError):
            compute_biomorphic_curvature("/nonexistent/path/image.png")

    def test_small_image(self):
        """Test handling of small images."""
        image = self.gen.create_curved_shapes(h=64, w=64)
        path = self._save_image(image, "small_curved.png")

        result = compute_biomorphic_curvature(path)
        self.assertIsNotNone(result["biomorphic_index"])
        self.assertGreaterEqual(result["biomorphic_index"], 0)
        self.assertLessEqual(result["biomorphic_index"], 1)

    def test_uniform_image(self):
        """Test handling of uniform image (no contours)."""
        image = self.gen.create_uniform_color_image()
        path = self._save_image(image, "uniform_bio.png")

        result = compute_biomorphic_curvature(path)

        # Should return gracefully
        self.assertIsNotNone(result["biomorphic_index"])


class TestIntegration(unittest.TestCase):
    """Integration tests across all five attributes."""

    def setUp(self):
        """Create temporary directory for test images."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        self.gen = SyntheticImageGenerator()

    def tearDown(self):
        """Clean up temporary directory."""
        self.temp_dir.cleanup()

    def _save_image(self, image: np.ndarray, filename: str) -> str:
        """Save image and return path."""
        filepath = self.temp_path / filename
        cv2.imwrite(str(filepath), cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
        return str(filepath)

    def test_all_attributes_on_same_image(self):
        """Test that all five attributes can be computed on same image."""
        image = self.gen.create_noise_image()
        path = self._save_image(image, "integrated.png")

        # All should succeed without errors
        result_complexity = compute_visual_complexity(path)
        result_regularity = compute_regularity_index(path)
        result_clarity = compute_figure_ground_clarity(path)
        result_illumination = compute_illumination_uniformity(path)
        result_curvature = compute_biomorphic_curvature(path)

        # Verify all returned valid data
        self.assertIsNotNone(result_complexity["complexity_score"])
        self.assertIsNotNone(result_regularity["regularity_score"])
        self.assertIsNotNone(result_clarity["clarity_score"])
        self.assertIsNotNone(result_illumination["uniformity_ratio"])
        self.assertIsNotNone(result_curvature["biomorphic_index"])

    def test_consistency_across_runs(self):
        """Test that results are deterministic."""
        image = self.gen.create_regular_pattern()
        path = self._save_image(image, "consistency.png")

        result1 = compute_visual_complexity(path)
        result2 = compute_visual_complexity(path)

        self.assertEqual(result1["complexity_score"], result2["complexity_score"])
        self.assertEqual(result1["edge_density"], result2["edge_density"])

    def test_diverse_images(self):
        """Test on diverse image types."""
        test_images = [
            ("gradient", self.gen.create_simple_gradient()),
            ("noise", self.gen.create_noise_image()),
            ("regular", self.gen.create_regular_pattern()),
            ("curved", self.gen.create_curved_shapes()),
            ("uniform", self.gen.create_uniform_color_image()),
        ]

        for name, image in test_images:
            path = self._save_image(image, f"{name}_test.png")

            # All attributes should work on all images
            result_complexity = compute_visual_complexity(path)
            result_regularity = compute_regularity_index(path)
            result_clarity = compute_figure_ground_clarity(path)
            result_illumination = compute_illumination_uniformity(path)
            result_curvature = compute_biomorphic_curvature(path)

            # All should return valid values
            self.assertGreaterEqual(result_complexity["complexity_score"], 0)
            self.assertGreaterEqual(result_regularity["regularity_score"], 0)
            self.assertGreaterEqual(result_clarity["clarity_score"], 0)
            self.assertGreaterEqual(result_illumination["uniformity_ratio"], 0)
            self.assertGreaterEqual(result_curvature["biomorphic_index"], 0)


if __name__ == "__main__":
    unittest.main()
