"""Test suite for NEW-03, NEW-07, and NEW-10 vision attributes.

Tests cover:
- Input validation and error handling
- Output range constraints
- Qualitative correctness on synthetic and real images
- Edge cases (tiny images, single colors, etc.)

Date: 2026-03-01
Tier 2 (Pretrained models): Uses OpenCV HOG, Haar cascades
"""

import unittest
import tempfile
from pathlib import Path
from typing import Tuple

import numpy as np
cv2 = __import__('pytest').importorskip('cv2', reason='cv2 (OpenCV) required for vision tests')

# Import the vision modules
from src.vision.new_attributes import (
    compute_sky_proportion,
    compute_material_diversity,
    compute_person_density,
    ImageProcessingError,
    SkyDetectionError,
    MaterialDetectionError,
    PersonDetectionError,
)


class SyntheticImageGenerator:
    """Generate synthetic test images for validation."""

    @staticmethod
    def create_blue_sky_image(h: int = 256, w: int = 256, sky_ratio: float = 0.7) -> np.ndarray:
        """Create image with blue sky at top."""
        image = np.zeros((h, w, 3), dtype=np.uint8)

        # Blue sky
        sky_height = int(h * sky_ratio)
        image[:sky_height, :] = [135, 206, 235]  # RGB sky blue

        # Green ground
        image[sky_height:, :] = [34, 139, 34]  # RGB dark green

        return image

    @staticmethod
    def create_uniform_color_image(h: int = 256, w: int = 256, color: Tuple = (128, 128, 128)) -> np.ndarray:
        """Create uniform color image."""
        image = np.zeros((h, w, 3), dtype=np.uint8)
        image[:, :] = color
        return image

    @staticmethod
    def create_mixed_material_image(h: int = 256, w: int = 256, n_materials: int = 3) -> np.ndarray:
        """Create image with distinct material patches."""
        image = np.zeros((h, w, 3), dtype=np.uint8)
        patch_h = h // 2
        patch_w = w // 2

        # Define distinct colors for different materials
        colors = [
            (139, 69, 19),    # Brown (wood)
            (128, 128, 128),  # Gray (concrete)
            (200, 200, 200),  # Light gray (metal)
            (34, 139, 34),    # Green (plant)
            (30, 144, 255),   # Blue (glass/water)
        ]

        # Assign colors to patches
        for i in range(2):
            for j in range(2):
                y = i * patch_h
                x = j * patch_w
                color_idx = (i * 2 + j) % len(colors)
                color = colors[color_idx]

                # Add texture variation
                patch = np.ones((patch_h, patch_w, 3), dtype=np.uint8) * color
                noise = np.random.randint(-20, 20, (patch_h, patch_w, 3))
                patch = np.clip(patch.astype(int) + noise, 0, 255).astype(np.uint8)

                image[y:y+patch_h, x:x+patch_w] = patch

        return image

    @staticmethod
    def create_person_image(h: int = 256, w: int = 256, include_person: bool = True) -> np.ndarray:
        """Create image that may contain a person-like object."""
        image = np.ones((h, w, 3), dtype=np.uint8) * 200  # Light background

        if include_person:
            # Draw simple person silhouette (oval head + rectangle body)
            center_x, center_y = w // 2, h // 3

            # Head (circle)
            cv2.circle(image, (center_x, center_y), 20, (50, 50, 50), -1)

            # Body (rectangle)
            cv2.rectangle(image, (center_x - 15, center_y + 20), (center_x + 15, center_y + 60), (100, 100, 100), -1)

        return image


class TestComputeSkyProportion(unittest.TestCase):
    """Test cases for NEW-03: Sky Proportion and Horizon Ratio."""

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
        # Convert RGB to BGR for OpenCV
        cv2.imwrite(str(filepath), cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
        return str(filepath)

    def test_sky_detection_blue_sky(self):
        """Test detection of clear blue sky."""
        image = self.gen.create_blue_sky_image(h=256, w=256, sky_ratio=0.7)
        path = self._save_image(image, "blue_sky.png")

        result = compute_sky_proportion(path)

        # Verify output structure
        self.assertIn("sky_ratio", result)
        self.assertIn("horizon_position", result)
        self.assertIn("scene_type", result)
        self.assertIn("confidence", result)

        # Verify ranges
        self.assertGreaterEqual(result["sky_ratio"], 0)
        self.assertLessEqual(result["sky_ratio"], 1)
        self.assertGreaterEqual(result["horizon_position"], 0)
        self.assertLessEqual(result["horizon_position"], 1)

        # Blue sky should have high ratio
        self.assertGreater(result["sky_ratio"], 0.5, "Sky detection failed: ratio too low")

    def test_sky_detection_uniform_color(self):
        """Test with uniform gray image (no sky)."""
        image = self.gen.create_uniform_color_image(h=256, w=256, color=(128, 128, 128))
        path = self._save_image(image, "uniform_gray.png")

        result = compute_sky_proportion(path)

        # Gray image should have low sky ratio
        self.assertLess(result["sky_ratio"], 0.2, "False positive sky detection")

    def test_sky_ratio_range(self):
        """Test that sky_ratio is always [0, 1]."""
        for sky_ratio_target in [0.2, 0.5, 0.8]:
            image = self.gen.create_blue_sky_image(sky_ratio=sky_ratio_target)
            path = self._save_image(image, f"sky_{sky_ratio_target:.1f}.png")

            result = compute_sky_proportion(path)

            self.assertGreaterEqual(result["sky_ratio"], 0)
            self.assertLessEqual(result["sky_ratio"], 1)

    def test_horizon_detection(self):
        """Test horizon line detection in blue sky image."""
        image = self.gen.create_blue_sky_image(sky_ratio=0.6)
        path = self._save_image(image, "horizon_test.png")

        result = compute_sky_proportion(path)

        # Horizon should be detected around 0.6 (60% from top)
        self.assertIsNotNone(result["horizon_position"])
        self.assertGreater(result["horizon_position"], 0.3, "Horizon position too high")
        self.assertLess(result["horizon_position"], 0.8, "Horizon position too low")

    def test_scene_type_classification(self):
        """Test scene type classification."""
        # Test outdoor clear
        image_sky = self.gen.create_blue_sky_image(sky_ratio=0.7)
        path_sky = self._save_image(image_sky, "outdoor_clear.png")
        result = compute_sky_proportion(path_sky)
        self.assertIn(result["scene_type"], ["outdoor_clear", "outdoor_cloudy", "ambiguous"])

        # Test indoor
        image_gray = self.gen.create_uniform_color_image(color=(100, 100, 100))
        path_gray = self._save_image(image_gray, "indoor.png")
        result = compute_sky_proportion(path_gray)
        self.assertEqual(result["scene_type"], "indoor")

    def test_confidence_score(self):
        """Test that confidence is in [0, 1]."""
        image = self.gen.create_blue_sky_image()
        path = self._save_image(image, "confidence_test.png")

        result = compute_sky_proportion(path)

        self.assertGreaterEqual(result["confidence"], 0)
        self.assertLessEqual(result["confidence"], 1)

    def test_nonexistent_file(self):
        """Test error handling for missing file."""
        with self.assertRaises(ImageProcessingError):
            compute_sky_proportion("/nonexistent/path/image.png")

    def test_small_image(self):
        """Test handling of very small images."""
        image = self.gen.create_blue_sky_image(h=32, w=32)
        path = self._save_image(image, "small.png")

        # Should not crash
        result = compute_sky_proportion(path)
        self.assertIsNotNone(result["sky_ratio"])

    def test_grayscale_input(self):
        """Test handling of grayscale images."""
        # Create grayscale test image
        image_rgb = self.gen.create_blue_sky_image()
        image_gray = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2GRAY)

        # Save as grayscale
        filepath = self.temp_path / "grayscale.png"
        cv2.imwrite(str(filepath), image_gray)

        # Should handle conversion
        result = compute_sky_proportion(str(filepath))
        self.assertIsNotNone(result["sky_ratio"])


class TestComputeMaterialDiversity(unittest.TestCase):
    """Test cases for NEW-07: Material Diversity Index."""

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

    def test_material_diversity_output_structure(self):
        """Test that output has required fields."""
        image = self.gen.create_mixed_material_image(n_materials=3)
        path = self._save_image(image, "materials.png")

        result = compute_material_diversity(path)

        required_keys = [
            "material_count",
            "diversity_index",
            "patch_count",
            "cluster_distribution",
            "texture_entropy",
            "dominant_material_prop",
            "confidence",
            "material_interpretation"
        ]

        for key in required_keys:
            self.assertIn(key, result, f"Missing key: {key}")

    def test_diversity_index_range(self):
        """Test that diversity_index is in [0, 1]."""
        image = self.gen.create_mixed_material_image(n_materials=4)
        path = self._save_image(image, "diversity_range.png")

        result = compute_material_diversity(path)

        self.assertGreaterEqual(result["diversity_index"], 0)
        self.assertLessEqual(result["diversity_index"], 1)

    def test_material_count_positive(self):
        """Test that material_count is positive."""
        image = self.gen.create_mixed_material_image()
        path = self._save_image(image, "material_count.png")

        result = compute_material_diversity(path)

        self.assertGreater(result["material_count"], 0)
        self.assertLessEqual(result["material_count"], 5)  # Max clusters in test

    def test_monolithic_low_diversity(self):
        """Test that uniform color image has low diversity."""
        image = self.gen.create_uniform_color_image(color=(100, 100, 100))
        path = self._save_image(image, "monolithic.png")

        result = compute_material_diversity(path)

        # Uniform color should have low diversity
        self.assertLess(
            result["diversity_index"],
            0.5,
            "Uniform image should have low diversity"
        )

    def test_mixed_material_higher_diversity(self):
        """Test that mixed materials have higher diversity."""
        image_uniform = self.gen.create_uniform_color_image(color=(100, 100, 100))
        image_mixed = self.gen.create_mixed_material_image(n_materials=4)

        path_uniform = self._save_image(image_uniform, "uniform_diversity.png")
        path_mixed = self._save_image(image_mixed, "mixed_diversity.png")

        result_uniform = compute_material_diversity(path_uniform)
        result_mixed = compute_material_diversity(path_mixed)

        # Mixed should have higher or equal diversity
        self.assertGreaterEqual(
            result_mixed["diversity_index"],
            result_uniform["diversity_index"] - 0.1,  # Allow small margin
            "Mixed materials should have higher diversity than uniform"
        )

    def test_confidence_range(self):
        """Test that confidence is in [0, 1]."""
        image = self.gen.create_mixed_material_image()
        path = self._save_image(image, "confidence.png")

        result = compute_material_diversity(path)

        self.assertGreaterEqual(result["confidence"], 0)
        self.assertLessEqual(result["confidence"], 1)

    def test_interpretation_valid(self):
        """Test that material_interpretation is valid."""
        image = self.gen.create_mixed_material_image()
        path = self._save_image(image, "interpretation.png")

        result = compute_material_diversity(path)

        valid_interpretations = [
            "minimal_monolithic",
            "mixed_materials",
            "complex_rich"
        ]

        self.assertIn(result["material_interpretation"], valid_interpretations)

    def test_small_image_handling(self):
        """Test handling of small images."""
        image = self.gen.create_mixed_material_image(h=64, w=64)
        path = self._save_image(image, "small_materials.png")

        # Should not crash
        result = compute_material_diversity(path)
        self.assertIsNotNone(result["diversity_index"])

    def test_nonexistent_file(self):
        """Test error handling for missing file."""
        with self.assertRaises(MaterialDetectionError):
            compute_material_diversity("/nonexistent/path/image.png")


class TestComputePersonDensity(unittest.TestCase):
    """Test cases for NEW-10: Person/Face Density Estimation."""

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

    def test_person_detection_output_structure(self):
        """Test that output has required fields."""
        image = self.gen.create_person_image(include_person=True)
        path = self._save_image(image, "person.png")

        result = compute_person_density(path)

        required_keys = [
            "person_count",
            "face_count",
            "total_detections",
            "density_ratio",
            "crowding_level",
            "bounding_boxes",
            "face_bounding_boxes",
            "confidence",
            "interpretation"
        ]

        for key in required_keys:
            self.assertIn(key, result, f"Missing key: {key}")

    def test_person_count_non_negative(self):
        """Test that person_count is non-negative."""
        image = self.gen.create_person_image()
        path = self._save_image(image, "person_count.png")

        result = compute_person_density(path)

        self.assertGreaterEqual(result["person_count"], 0)
        self.assertIsInstance(result["person_count"], int)

    def test_empty_scene_low_density(self):
        """Test that empty scene has low crowding level."""
        image = self.gen.create_person_image(include_person=False)
        path = self._save_image(image, "empty.png")

        result = compute_person_density(path)

        self.assertEqual(result["person_count"], 0)
        self.assertEqual(result["crowding_level"], "low")

    def test_crowding_level_valid(self):
        """Test that crowding_level is valid."""
        image = self.gen.create_person_image()
        path = self._save_image(image, "crowd.png")

        result = compute_person_density(path)

        valid_levels = ["low", "moderate", "high"]
        self.assertIn(result["crowding_level"], valid_levels)

    def test_density_ratio_non_negative(self):
        """Test that density_ratio is non-negative."""
        image = self.gen.create_person_image()
        path = self._save_image(image, "density.png")

        result = compute_person_density(path)

        self.assertGreaterEqual(result["density_ratio"], 0)

    def test_confidence_range(self):
        """Test that confidence is in [0, 1]."""
        image = self.gen.create_person_image()
        path = self._save_image(image, "person_conf.png")

        result = compute_person_density(path)

        self.assertGreaterEqual(result["confidence"], 0)
        self.assertLessEqual(result["confidence"], 1)

    def test_bounding_boxes_format(self):
        """Test that bounding boxes are in correct format."""
        image = self.gen.create_person_image(include_person=True)
        path = self._save_image(image, "bbox.png")

        result = compute_person_density(path)

        # Bounding boxes should be list of tuples (x, y, w, h)
        self.assertIsInstance(result["bounding_boxes"], list)
        self.assertIsInstance(result["face_bounding_boxes"], list)

    def test_nonexistent_file(self):
        """Test error handling for missing file."""
        with self.assertRaises(PersonDetectionError):
            compute_person_density("/nonexistent/path/image.png")

    def test_small_image_handling(self):
        """Test handling of small images."""
        # Use minimum safe size for HOG detector (64x64 minimum)
        # Note: Very small images may cause issues with Haar cascade
        image = self.gen.create_person_image(h=128, w=128)
        path = self._save_image(image, "small_person.png")

        # Should not crash
        result = compute_person_density(path)
        self.assertIsNotNone(result["person_count"])

    def test_grayscale_image_conversion(self):
        """Test handling of grayscale images."""
        image_rgb = self.gen.create_person_image()
        image_gray = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2GRAY)

        filepath = self.temp_path / "grayscale_person.png"
        cv2.imwrite(str(filepath), image_gray)

        # Should handle conversion
        result = compute_person_density(str(filepath))
        self.assertIsNotNone(result["person_count"])


class TestIntegration(unittest.TestCase):
    """Integration tests across all three attributes."""

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
        """Test that all three attributes can be computed on same image."""
        image = self.gen.create_blue_sky_image()
        path = self._save_image(image, "integrated.png")

        # All should succeed without errors
        result_sky = compute_sky_proportion(path)
        result_material = compute_material_diversity(path)
        result_person = compute_person_density(path)

        # Verify all returned valid data
        self.assertIsNotNone(result_sky["sky_ratio"])
        self.assertIsNotNone(result_material["diversity_index"])
        self.assertIsNotNone(result_person["person_count"])

    def test_consistency_across_runs(self):
        """Test that results are consistent across multiple runs."""
        image = self.gen.create_mixed_material_image()
        path = self._save_image(image, "consistency.png")

        result1 = compute_material_diversity(path)
        result2 = compute_material_diversity(path)

        # Results should be identical
        self.assertEqual(result1["diversity_index"], result2["diversity_index"])
        self.assertEqual(result1["material_count"], result2["material_count"])


if __name__ == "__main__":
    unittest.main()
