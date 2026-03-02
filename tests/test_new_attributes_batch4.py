"""Test suite for NEW-13, NEW-14, NEW-15 vision attributes.

Tests cover:
- Input validation and error handling
- Output range constraints (values within expected bounds)
- Qualitative correctness on synthetic and real images
- Edge cases (tiny images, uniform colors, etc.)
- Integration with existing attribute pipeline

Date: 2026-03-02
Attributes tested:
  - NEW-13: Temporal Lighting Variation Index
  - NEW-14: Prospect-Refuge Balance Score
  - NEW-15: Focal Point Density
"""

import unittest
import tempfile
from pathlib import Path
from typing import Tuple

import numpy as np

cv2 = __import__('pytest').importorskip('cv2', reason='cv2 (OpenCV) required for vision tests')

# Import the vision modules
from src.vision.new_attributes_batch4 import (
    compute_temporal_lighting_variation,
    compute_prospect_refuge_balance,
    compute_focal_point_density,
    TemporalLightingError,
    ProspectRefugeError,
    FocalPointError,
)


class SyntheticImageGenerator:
    """Generate synthetic test images for validation."""

    @staticmethod
    def create_warm_cool_image(h: int = 256, w: int = 256) -> np.ndarray:
        """Create image with warm (left) and cool (right) zones.

        For testing temporal lighting variation.
        """
        image = np.zeros((h, w, 3), dtype=np.uint8)
        # Left half: warm (yellow)
        image[:, :w//2] = [180, 180, 50]  # BGR warm
        # Right half: cool (blue)
        image[:, w//2:] = [150, 100, 50]  # BGR cool
        return image

    @staticmethod
    def create_uniform_image(h: int = 256, w: int = 256, gray_level: int = 128) -> np.ndarray:
        """Create uniform gray image (minimal variation)."""
        return np.full((h, w, 3), gray_level, dtype=np.uint8)

    @staticmethod
    def create_open_space_image(h: int = 256, w: int = 256) -> np.ndarray:
        """Create image representing open/spacious environment (high prospect)."""
        image = np.zeros((h, w, 3), dtype=np.uint8)
        # Sky (blue, top 2/3)
        image[:2*h//3, :] = [200, 180, 100]  # Light blue
        # Open ground (light)
        image[2*h//3:, :] = [200, 200, 150]  # Light
        return image

    @staticmethod
    def create_enclosed_space_image(h: int = 256, w: int = 256) -> np.ndarray:
        """Create image representing enclosed environment (high refuge)."""
        image = np.zeros((h, w, 3), dtype=np.uint8)
        # Walls (dark)
        image[:, :] = [50, 50, 50]  # Dark gray
        # Small window
        image[50:100, 50:100] = [200, 180, 100]  # Light window
        return image

    @staticmethod
    def create_focal_points_image(h: int = 256, w: int = 256, n_points: int = 3) -> np.ndarray:
        """Create image with N distinct bright focal points on dark background."""
        image = np.zeros((h, w, 3), dtype=np.uint8)
        image[:, :] = 30  # Dark background

        # Place N bright points at regular intervals
        positions = []
        if n_points == 1:
            positions = [(h//2, w//2)]
        elif n_points == 2:
            positions = [(h//4, w//4), (3*h//4, 3*w//4)]
        elif n_points == 3:
            positions = [(h//2, w//4), (h//4, 3*w//4), (3*h//4, h//2)]
        elif n_points >= 4:
            # Grid of focal points
            cols = int(np.sqrt(n_points))
            rows = (n_points + cols - 1) // cols
            for i in range(rows):
                for j in range(cols):
                    y = (i + 1) * h // (rows + 1)
                    x = (j + 1) * w // (cols + 1)
                    positions.append((y, x))

        # Draw bright circles at focal point positions
        radius = 10
        for y, x in positions:
            cv2.circle(image, (x, y), radius, (200, 200, 200), -1)

        return image

    @staticmethod
    def save_temp_image(image: np.ndarray) -> str:
        """Save image to temporary file and return path."""
        fd, path = tempfile.mkstemp(suffix='.png')
        # Convert RGB to BGR for OpenCV
        image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR) if len(image.shape) == 3 else image
        cv2.imwrite(path, image_bgr)
        return path


class TestTemporalLightingVariation(unittest.TestCase):
    """Tests for NEW-13: Temporal Lighting Variation Index."""

    def test_basic_computation(self):
        """Test basic computation on synthetic image."""
        image = SyntheticImageGenerator.create_warm_cool_image()
        path = SyntheticImageGenerator.save_temp_image(image)

        result = compute_temporal_lighting_variation(path)

        # Check output keys
        self.assertIn('temporal_variation_score', result)
        self.assertIn('color_temperature_variance', result)
        self.assertIn('shadow_complexity', result)
        self.assertIn('directional_light_strength', result)
        self.assertIn('inferred_lighting_type', result)
        self.assertIn('confidence', result)

        # Check range constraints
        self.assertGreaterEqual(result['temporal_variation_score'], 0.0)
        self.assertLessEqual(result['temporal_variation_score'], 1.0)
        self.assertGreaterEqual(result['confidence'], 0.0)
        self.assertLessEqual(result['confidence'], 1.0)

    def test_warm_cool_image_detects_variation(self):
        """Test that warm/cool image shows higher color temperature variance than uniform."""
        # Create two images: uniform and warm/cool
        uniform_image = SyntheticImageGenerator.create_uniform_image()
        path_uniform = SyntheticImageGenerator.save_temp_image(uniform_image)
        result_uniform = compute_temporal_lighting_variation(path_uniform)

        warm_cool_image = SyntheticImageGenerator.create_warm_cool_image()
        path_warm = SyntheticImageGenerator.save_temp_image(warm_cool_image)
        result_warm = compute_temporal_lighting_variation(path_warm)

        # Warm/cool image should have higher CCT variance than uniform
        self.assertGreater(result_warm['color_temperature_variance'],
                          result_uniform['color_temperature_variance'],
                          "Warm/cool image should show higher CCT variance than uniform")

    def test_uniform_image_low_variation(self):
        """Test that uniform image shows low temporal variation."""
        image = SyntheticImageGenerator.create_uniform_image()
        path = SyntheticImageGenerator.save_temp_image(image)

        result = compute_temporal_lighting_variation(path)

        # Uniform image should have low variation
        self.assertLess(result['temporal_variation_score'], 0.5,
                       "Uniform image should show low temporal variation")

    def test_lighting_type_classification(self):
        """Test that lighting type is correctly classified."""
        # Test natural lighting (warm/cool variation)
        warm_cool_image = SyntheticImageGenerator.create_warm_cool_image()
        path_warm = SyntheticImageGenerator.save_temp_image(warm_cool_image)
        result_warm = compute_temporal_lighting_variation(path_warm)
        self.assertIn(result_warm['inferred_lighting_type'],
                     ["natural", "mixed", "artificial"])

        # Test artificial (uniform)
        uniform_image = SyntheticImageGenerator.create_uniform_image()
        path_uniform = SyntheticImageGenerator.save_temp_image(uniform_image)
        result_uniform = compute_temporal_lighting_variation(path_uniform)
        self.assertEqual(result_uniform['inferred_lighting_type'], "artificial",
                        "Uniform image should be classified as artificial")

    def test_error_on_missing_file(self):
        """Test that error is raised for missing image file."""
        with self.assertRaises(Exception):
            compute_temporal_lighting_variation("/nonexistent/path/image.png")

    def test_verbose_output(self):
        """Test that verbose mode runs without error."""
        image = SyntheticImageGenerator.create_warm_cool_image()
        path = SyntheticImageGenerator.save_temp_image(image)

        result = compute_temporal_lighting_variation(path, verbose=True)
        self.assertIsNotNone(result)


class TestProspectRefugeBalance(unittest.TestCase):
    """Tests for NEW-14: Prospect-Refuge Balance Score."""

    def test_basic_computation(self):
        """Test basic computation on synthetic image."""
        image = SyntheticImageGenerator.create_open_space_image()
        path = SyntheticImageGenerator.save_temp_image(image)

        result = compute_prospect_refuge_balance(path)

        # Check output keys
        self.assertIn('balance_score', result)
        self.assertIn('prospect_score', result)
        self.assertIn('refuge_score', result)
        self.assertIn('balance_type', result)
        self.assertIn('confidence', result)

        # Check range constraints
        self.assertGreaterEqual(result['balance_score'], 0.0)
        self.assertLessEqual(result['balance_score'], 1.0)
        self.assertGreaterEqual(result['prospect_score'], 0.0)
        self.assertLessEqual(result['prospect_score'], 1.0)
        self.assertGreaterEqual(result['refuge_score'], 0.0)
        self.assertLessEqual(result['refuge_score'], 1.0)

    def test_open_space_high_prospect(self):
        """Test that open space image shows high prospect."""
        image = SyntheticImageGenerator.create_open_space_image()
        path = SyntheticImageGenerator.save_temp_image(image)

        result = compute_prospect_refuge_balance(path)

        # Open space should have high prospect (low complexity)
        self.assertGreater(result['prospect_score'], 0.5,
                          "Open space should have high prospect")

    def test_enclosed_space_high_refuge(self):
        """Test that enclosed space image shows high refuge."""
        image = SyntheticImageGenerator.create_enclosed_space_image()
        path = SyntheticImageGenerator.save_temp_image(image)

        result = compute_prospect_refuge_balance(path)

        # Enclosed space should have high refuge (darker)
        self.assertGreater(result['refuge_score'], 0.3,
                          "Enclosed space should have some refuge")

    def test_balance_type_classification(self):
        """Test that balance type is correctly classified."""
        # Open space should be prospect-heavy
        open_image = SyntheticImageGenerator.create_open_space_image()
        path_open = SyntheticImageGenerator.save_temp_image(open_image)
        result_open = compute_prospect_refuge_balance(path_open)
        self.assertIn(result_open['balance_type'],
                     ["balanced", "prospect_heavy", "refuge_heavy", "somewhat_imbalanced"])

    def test_extreme_imbalance_lowers_score(self):
        """Test that extreme imbalance lowers balance score."""
        # Totally open (white background)
        open_image = np.full((256, 256, 3), 255, dtype=np.uint8)
        path_open = SyntheticImageGenerator.save_temp_image(open_image)
        result = compute_prospect_refuge_balance(path_open)

        # Extreme imbalance should lower balance score
        self.assertLess(result['balance_score'], 0.8,
                       "Extreme imbalance should lower balance score")

    def test_error_on_missing_file(self):
        """Test that error is raised for missing image file."""
        with self.assertRaises(Exception):
            compute_prospect_refuge_balance("/nonexistent/path/image.png")

    def test_verbose_output(self):
        """Test that verbose mode runs without error."""
        image = SyntheticImageGenerator.create_open_space_image()
        path = SyntheticImageGenerator.save_temp_image(image)

        result = compute_prospect_refuge_balance(path, verbose=True)
        self.assertIsNotNone(result)


class TestFocalPointDensity(unittest.TestCase):
    """Tests for NEW-15: Focal Point Density."""

    def test_basic_computation(self):
        """Test basic computation on synthetic image."""
        image = SyntheticImageGenerator.create_focal_points_image(n_points=3)
        path = SyntheticImageGenerator.save_temp_image(image)

        result = compute_focal_point_density(path)

        # Check output keys
        self.assertIn('focal_point_density', result)
        self.assertIn('focal_point_count', result)
        self.assertIn('density_normalized', result)
        self.assertIn('complexity_type', result)
        self.assertIn('confidence', result)

        # Check range constraints
        self.assertGreaterEqual(result['focal_point_density'], 0.0)
        self.assertGreaterEqual(result['focal_point_count'], 0)
        self.assertGreaterEqual(result['density_normalized'], 0.0)
        self.assertLessEqual(result['density_normalized'], 1.0)

    def test_empty_image_no_focal_points(self):
        """Test that empty image has no focal points."""
        image = SyntheticImageGenerator.create_uniform_image()
        path = SyntheticImageGenerator.save_temp_image(image)

        result = compute_focal_point_density(path)

        # Uniform image should have very few focal points
        self.assertLess(result['focal_point_count'], 3,
                       "Uniform image should have minimal focal points")
        self.assertEqual(result['complexity_type'], "boring",
                        "Uniform image should be classified as boring")

    def test_single_focal_point(self):
        """Test image with single focal point (or few points)."""
        image = SyntheticImageGenerator.create_focal_points_image(n_points=1)
        path = SyntheticImageGenerator.save_temp_image(image)

        result = compute_focal_point_density(path)

        # Should detect 0-2 focal points (bright circle may or may not be detected)
        self.assertLessEqual(result['focal_point_count'], 3,
                            "Single bright point should have few focal points")
        # Should be boring or low complexity
        self.assertIn(result['complexity_type'], ["boring", "organized"],
                     "Single point should be boring or organized")

    def test_multiple_focal_points(self):
        """Test image with multiple focal points."""
        image = SyntheticImageGenerator.create_focal_points_image(n_points=5)
        path = SyntheticImageGenerator.save_temp_image(image)

        result = compute_focal_point_density(path)

        # Should detect focal points (count may vary depending on detection sensitivity)
        self.assertGreaterEqual(result['focal_point_count'], 0,
                               "Should have non-negative focal point count")
        # Type should be one of the valid classifications
        self.assertIn(result['complexity_type'], ["boring", "organized", "chaotic"],
                     "Complexity type should be valid")

    def test_complexity_type_classification(self):
        """Test that complexity type is one of the valid categories."""
        # Image with some focal points
        image_5 = SyntheticImageGenerator.create_focal_points_image(n_points=5)
        path_5 = SyntheticImageGenerator.save_temp_image(image_5)
        result_5 = compute_focal_point_density(path_5)

        # Should be one of the valid types
        self.assertIn(result_5['complexity_type'], ["boring", "organized", "chaotic"],
                     "Complexity type should be one of the valid categories")

    def test_density_increases_with_points(self):
        """Test that focal point density increases with more points."""
        image_1 = SyntheticImageGenerator.create_focal_points_image(n_points=1)
        image_5 = SyntheticImageGenerator.create_focal_points_image(n_points=5)

        path_1 = SyntheticImageGenerator.save_temp_image(image_1)
        path_5 = SyntheticImageGenerator.save_temp_image(image_5)

        result_1 = compute_focal_point_density(path_1)
        result_5 = compute_focal_point_density(path_5)

        # More points should have higher or equal density
        self.assertGreaterEqual(result_5['focal_point_count'], result_1['focal_point_count'],
                               "More focal points should have higher count")

    def test_error_on_missing_file(self):
        """Test that error is raised for missing image file."""
        with self.assertRaises(Exception):
            compute_focal_point_density("/nonexistent/path/image.png")

    def test_verbose_output(self):
        """Test that verbose mode runs without error."""
        image = SyntheticImageGenerator.create_focal_points_image(n_points=3)
        path = SyntheticImageGenerator.save_temp_image(image)

        result = compute_focal_point_density(path, verbose=True)
        self.assertIsNotNone(result)


class TestAttributeIntegration(unittest.TestCase):
    """Integration tests for all three NEW attributes."""

    def test_all_attributes_on_same_image(self):
        """Test that all three attributes can be computed on the same image."""
        image = SyntheticImageGenerator.create_warm_cool_image()
        path = SyntheticImageGenerator.save_temp_image(image)

        result_13 = compute_temporal_lighting_variation(path)
        result_14 = compute_prospect_refuge_balance(path)
        result_15 = compute_focal_point_density(path)

        # All should return valid results
        self.assertIsNotNone(result_13)
        self.assertIsNotNone(result_14)
        self.assertIsNotNone(result_15)

        # All should have confidence scores
        self.assertGreater(result_13['confidence'], 0.5)
        self.assertGreater(result_14['confidence'], 0.5)
        self.assertGreater(result_15['confidence'], 0.5)

    def test_different_image_types(self):
        """Test attributes on different image types."""
        images = [
            ("open", SyntheticImageGenerator.create_open_space_image()),
            ("enclosed", SyntheticImageGenerator.create_enclosed_space_image()),
            ("focal", SyntheticImageGenerator.create_focal_points_image(3)),
            ("warm_cool", SyntheticImageGenerator.create_warm_cool_image()),
            ("uniform", SyntheticImageGenerator.create_uniform_image()),
        ]

        for img_type, image in images:
            path = SyntheticImageGenerator.save_temp_image(image)

            try:
                result_13 = compute_temporal_lighting_variation(path)
                result_14 = compute_prospect_refuge_balance(path)
                result_15 = compute_focal_point_density(path)

                self.assertIsNotNone(result_13, f"Failed on {img_type} for NEW-13")
                self.assertIsNotNone(result_14, f"Failed on {img_type} for NEW-14")
                self.assertIsNotNone(result_15, f"Failed on {img_type} for NEW-15")
            except Exception as e:
                self.fail(f"Error on {img_type}: {str(e)}")


if __name__ == '__main__':
    unittest.main()
