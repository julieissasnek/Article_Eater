"""Test suite for NEW-01, NEW-02, NEW-09, NEW-11 vision attributes.

Tests cover:
- Input validation and error handling
- Output range constraints
- Qualitative correctness on synthetic images
- Edge cases (tiny images, single colors, outdoor scenes)

Date: 2026-03-01
Batch 3: CPU-friendly attributes (no deep learning)
"""

import unittest
import tempfile
from pathlib import Path
from typing import Tuple

import pytest

numpy = pytest.importorskip("numpy")
cv2 = pytest.importorskip("cv2")
import numpy as np

# Import the vision modules
from src.vision.new_attributes_batch3 import (
    compute_vegetation_segmentation,
    compute_depth_estimation_monocular,
    compute_acoustic_privacy_proxy,
    compute_visual_privacy,
    VegetationDetectionError,
    DepthEstimationError,
    AcousticProxyError,
    VisualPrivacyError,
)


class SyntheticImageGenerator:
    """Generate synthetic test images for validation."""

    @staticmethod
    def save_image(image: np.ndarray, temp_dir: Path) -> str:
        """Save image to temporary file and return path."""
        filename = temp_dir / f"test_{np.random.randint(0, 1000000)}.png"
        cv2.imwrite(str(filename), cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
        return str(filename)

    @staticmethod
    def create_green_vegetation_image(
        h: int = 256, w: int = 256, vegetation_ratio: float = 0.3
    ) -> np.ndarray:
        """Create image with green vegetation regions."""
        image = np.ones((h, w, 3), dtype=np.uint8) * 200  # Light gray background

        # Green vegetation regions
        veg_area = int(np.sqrt(vegetation_ratio) * h)
        image[:veg_area, :] = [34, 139, 34]  # RGB dark green

        # Add some noise for realism
        noise = np.random.randint(-10, 10, (h, w, 3))
        image = np.clip(image.astype(int) + noise, 0, 255).astype(np.uint8)

        return image

    @staticmethod
    def create_outdoor_scene(h: int = 256, w: int = 256) -> np.ndarray:
        """Create outdoor scene: sky + green ground."""
        image = np.zeros((h, w, 3), dtype=np.uint8)

        # Blue sky (top 60%)
        sky_height = int(h * 0.6)
        image[:sky_height, :] = [135, 206, 235]  # RGB sky blue

        # Green grass (bottom 40%)
        image[sky_height:, :] = [34, 139, 34]  # RGB grass green

        return image

    @staticmethod
    def create_indoor_scene(h: int = 256, w: int = 256) -> np.ndarray:
        """Create indoor scene: walls + floor + ceiling."""
        image = np.ones((h, w, 3), dtype=np.uint8) * 150

        # Ceiling (top 20%)
        ceiling_height = int(h * 0.2)
        image[:ceiling_height, :] = [200, 200, 200]  # Light gray ceiling

        # Floor (bottom 30%)
        floor_start = int(h * 0.7)
        image[floor_start:, :] = [139, 69, 19]  # Brown floor

        # Walls (middle)
        image[ceiling_height:floor_start, :] = [211, 211, 211]  # Light walls

        return image

    @staticmethod
    def create_uniform_color_image(
        h: int = 256, w: int = 256, color: Tuple = (128, 128, 128)
    ) -> np.ndarray:
        """Create uniform color image."""
        image = np.zeros((h, w, 3), dtype=np.uint8)
        image[:, :] = color
        return image

    @staticmethod
    def create_all_black_image(h: int = 256, w: int = 256) -> np.ndarray:
        """Create all-black image."""
        return np.zeros((h, w, 3), dtype=np.uint8)

    @staticmethod
    def create_all_white_image(h: int = 256, w: int = 256) -> np.ndarray:
        """Create all-white image."""
        return np.ones((h, w, 3), dtype=np.uint8) * 255

    @staticmethod
    def create_tiny_image(h: int = 16, w: int = 16) -> np.ndarray:
        """Create tiny test image."""
        return np.ones((h, w, 3), dtype=np.uint8) * 128

    @staticmethod
    def create_enclosed_room(h: int = 256, w: int = 256) -> np.ndarray:
        """Create image resembling enclosed room with barriers."""
        image = np.ones((h, w, 3), dtype=np.uint8) * 150

        # Dark borders (walls/barriers)
        border_width = 20
        image[:border_width, :] = [50, 50, 50]  # Top wall
        image[-border_width:, :] = [50, 50, 50]  # Bottom wall
        image[:, :border_width] = [50, 50, 50]  # Left wall
        image[:, -border_width:] = [50, 50, 50]  # Right wall

        # Soft furnishings in center (low saturation)
        center_h = int(h * 0.25)
        center_w = int(w * 0.25)
        image[center_h:center_h+100, center_w:center_w+100] = [120, 120, 120]

        return image

    @staticmethod
    def create_open_space(h: int = 256, w: int = 256) -> np.ndarray:
        """Create image of open space with high visibility."""
        image = np.ones((h, w, 3), dtype=np.uint8) * 200

        # Large sky area (top 70%)
        sky_height = int(h * 0.7)
        image[:sky_height, :] = [135, 206, 235]  # Sky blue

        # Distant ground/horizon
        image[sky_height:, :] = [100, 200, 100]

        return image


class TestVegetationSegmentation(unittest.TestCase):
    """Test NEW-01: Vegetation Segmentation Ratio."""

    def setUp(self):
        """Create temporary directory for test images."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self):
        """Clean up temporary files."""
        self.temp_dir.cleanup()

    def test_green_vegetation_high_ratio(self):
        """Test detection of high vegetation coverage."""
        image = SyntheticImageGenerator.create_green_vegetation_image(
            vegetation_ratio=0.5
        )
        image_path = SyntheticImageGenerator.save_image(image, self.temp_path)

        result = compute_vegetation_segmentation(image_path)

        # Should detect significant vegetation
        self.assertGreater(result["vegetation_ratio"], 0.3)
        self.assertTrue(result["has_vegetation"])
        # Check that ratio is in valid range [0, 1]
        self.assertGreaterEqual(result["vegetation_ratio"], 0.0)
        self.assertLessEqual(result["vegetation_ratio"], 1.0)
        self.assertGreater(result["confidence"], 0.6)

    def test_no_vegetation_uniform_gray(self):
        """Test detection absence of vegetation in uniform gray."""
        image = SyntheticImageGenerator.create_uniform_color_image(color=(128, 128, 128))
        image_path = SyntheticImageGenerator.save_image(image, self.temp_path)

        result = compute_vegetation_segmentation(image_path)

        # Should detect no vegetation
        self.assertLess(result["vegetation_ratio"], 0.1)
        self.assertFalse(result["has_vegetation"])
        self.assertEqual(result["component_count"], 0)

    def test_outdoor_scene_green_detection(self):
        """Test vegetation detection in outdoor scene."""
        image = SyntheticImageGenerator.create_outdoor_scene()
        image_path = SyntheticImageGenerator.save_image(image, self.temp_path)

        result = compute_vegetation_segmentation(image_path)

        # Should detect grass in bottom half
        self.assertTrue(result["has_vegetation"])
        self.assertGreater(result["vegetation_distribution"]["bottom"], 0.0)
        self.assertGreater(result["green_chromaticity"], 0.2)

    def test_all_black_image(self):
        """Test handling of all-black image."""
        image = SyntheticImageGenerator.create_all_black_image()
        image_path = SyntheticImageGenerator.save_image(image, self.temp_path)

        result = compute_vegetation_segmentation(image_path)

        # Should have minimal vegetation
        self.assertLess(result["vegetation_ratio"], 0.05)
        self.assertFalse(result["has_vegetation"])

    def test_all_white_image(self):
        """Test handling of all-white image."""
        image = SyntheticImageGenerator.create_all_white_image()
        image_path = SyntheticImageGenerator.save_image(image, self.temp_path)

        result = compute_vegetation_segmentation(image_path)

        # Should have minimal vegetation
        self.assertLess(result["vegetation_ratio"], 0.05)
        self.assertFalse(result["has_vegetation"])

    def test_tiny_image(self):
        """Test handling of very small image."""
        image = SyntheticImageGenerator.create_tiny_image(h=32, w=32)
        image_path = SyntheticImageGenerator.save_image(image, self.temp_path)

        result = compute_vegetation_segmentation(image_path)

        # Should still return valid result
        self.assertIsNotNone(result)
        self.assertIn("vegetation_ratio", result)
        self.assertIn("confidence", result)

    def test_result_keys(self):
        """Test that all required keys are present in result."""
        image = SyntheticImageGenerator.create_outdoor_scene()
        image_path = SyntheticImageGenerator.save_image(image, self.temp_path)

        result = compute_vegetation_segmentation(image_path)

        required_keys = [
            "vegetation_ratio",
            "vegetation_pixels",
            "total_pixels",
            "green_chromaticity",
            "has_vegetation",
            "vegetation_distribution",
            "largest_connected_component_size",
            "component_count",
            "confidence",
        ]

        for key in required_keys:
            self.assertIn(key, result, f"Missing key: {key}")

    def test_invalid_image_path(self):
        """Test handling of non-existent image path."""
        with self.assertRaises(Exception):
            compute_vegetation_segmentation("/nonexistent/path/image.png")

    def test_range_constraints(self):
        """Test that numeric outputs are within valid ranges."""
        image = SyntheticImageGenerator.create_green_vegetation_image()
        image_path = SyntheticImageGenerator.save_image(image, self.temp_path)

        result = compute_vegetation_segmentation(image_path)

        # All ratios should be [0, 1]
        self.assertGreaterEqual(result["vegetation_ratio"], 0.0)
        self.assertLessEqual(result["vegetation_ratio"], 1.0)
        self.assertGreaterEqual(result["confidence"], 0.0)
        self.assertLessEqual(result["confidence"], 1.0)
        self.assertGreaterEqual(result["green_chromaticity"], 0.0)


class TestDepthEstimation(unittest.TestCase):
    """Test NEW-02: Scene Depth Estimation (Monocular Cues)."""

    def setUp(self):
        """Create temporary directory for test images."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self):
        """Clean up temporary files."""
        self.temp_dir.cleanup()

    def test_outdoor_scene_depth(self):
        """Test depth estimation on outdoor scene."""
        image = SyntheticImageGenerator.create_outdoor_scene()
        image_path = SyntheticImageGenerator.save_image(image, self.temp_path)

        result = compute_depth_estimation_monocular(image_path)

        # Outdoor scenes should have detectable depth
        self.assertGreater(result["texture_gradient_score"], 0.0)
        self.assertIn(result["scene_type"], ["deep", "flat", "mixed"])

    def test_uniform_image_no_depth_cues(self):
        """Test depth estimation on uniform image (minimal cues)."""
        image = SyntheticImageGenerator.create_uniform_color_image()
        image_path = SyntheticImageGenerator.save_image(image, self.temp_path)

        result = compute_depth_estimation_monocular(image_path)

        # Uniform image should have low texture gradient
        self.assertLess(result["texture_gradient_score"], 0.5)

    def test_all_black_image(self):
        """Test depth estimation on all-black image."""
        image = SyntheticImageGenerator.create_all_black_image()
        image_path = SyntheticImageGenerator.save_image(image, self.temp_path)

        result = compute_depth_estimation_monocular(image_path)

        # Should still return valid result
        self.assertIsNotNone(result)
        self.assertGreaterEqual(result["mean_depth_estimate"], 0.0)
        self.assertLessEqual(result["mean_depth_estimate"], 1.0)

    def test_tiny_image(self):
        """Test depth estimation on tiny image."""
        image = SyntheticImageGenerator.create_tiny_image()
        image_path = SyntheticImageGenerator.save_image(image, self.temp_path)

        result = compute_depth_estimation_monocular(image_path)

        # Should handle tiny images gracefully
        self.assertIsNotNone(result)
        self.assertIn("mean_depth_estimate", result)

    def test_result_keys(self):
        """Test that all required keys are present."""
        image = SyntheticImageGenerator.create_outdoor_scene()
        image_path = SyntheticImageGenerator.save_image(image, self.temp_path)

        result = compute_depth_estimation_monocular(image_path)

        required_keys = [
            "mean_depth_estimate",
            "depth_gradient_vertical",
            "depth_gradient_horizontal",
            "perspective_convergence_score",
            "texture_gradient_score",
            "blur_gradient_score",
            "scene_type",
            "confidence",
        ]

        for key in required_keys:
            self.assertIn(key, result, f"Missing key: {key}")

    def test_range_constraints(self):
        """Test that numeric outputs are within valid ranges."""
        image = SyntheticImageGenerator.create_outdoor_scene()
        image_path = SyntheticImageGenerator.save_image(image, self.temp_path)

        result = compute_depth_estimation_monocular(image_path)

        # Depth estimate should be [0, 1]
        self.assertGreaterEqual(result["mean_depth_estimate"], 0.0)
        self.assertLessEqual(result["mean_depth_estimate"], 1.0)

        # Scores should be [0, 1]
        self.assertGreaterEqual(result["perspective_convergence_score"], 0.0)
        self.assertLessEqual(result["perspective_convergence_score"], 1.0)
        self.assertGreaterEqual(result["texture_gradient_score"], 0.0)
        self.assertLessEqual(result["texture_gradient_score"], 1.0)

    def test_invalid_image_path(self):
        """Test handling of non-existent image path."""
        with self.assertRaises(Exception):
            compute_depth_estimation_monocular("/nonexistent/path/image.png")


class TestAcousticPrivacyProxy(unittest.TestCase):
    """Test NEW-09: Acoustic Privacy Proxy."""

    def setUp(self):
        """Create temporary directory for test images."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self):
        """Clean up temporary files."""
        self.temp_dir.cleanup()

    def test_outdoor_open_space(self):
        """Test acoustic proxy on open space (high RT60)."""
        image = SyntheticImageGenerator.create_open_space()
        image_path = SyntheticImageGenerator.save_image(image, self.temp_path)

        result = compute_acoustic_privacy_proxy(image_path)

        # Open space should have low enclosure
        self.assertLess(result["enclosure_ratio"], 0.5)
        self.assertGreater(result["acoustic_privacy_score"], 0.0)

    def test_indoor_enclosed_room(self):
        """Test acoustic proxy on enclosed room."""
        image = SyntheticImageGenerator.create_enclosed_room()
        image_path = SyntheticImageGenerator.save_image(image, self.temp_path)

        result = compute_acoustic_privacy_proxy(image_path)

        # Enclosed room should have high enclosure
        self.assertGreater(result["enclosure_ratio"], 0.3)

    def test_rt60_category_values(self):
        """Test that RT60 category is valid."""
        image = SyntheticImageGenerator.create_outdoor_scene()
        image_path = SyntheticImageGenerator.save_image(image, self.temp_path)

        result = compute_acoustic_privacy_proxy(image_path)

        self.assertIn(result["estimated_RT60_category"], ["low", "medium", "high"])

    def test_uniform_image(self):
        """Test acoustic proxy on uniform image."""
        image = SyntheticImageGenerator.create_uniform_color_image()
        image_path = SyntheticImageGenerator.save_image(image, self.temp_path)

        result = compute_acoustic_privacy_proxy(image_path)

        # Should return valid result
        self.assertIsNotNone(result)
        self.assertIn("acoustic_privacy_score", result)

    def test_result_keys(self):
        """Test that all required keys are present."""
        image = SyntheticImageGenerator.create_indoor_scene()
        image_path = SyntheticImageGenerator.save_image(image, self.temp_path)

        result = compute_acoustic_privacy_proxy(image_path)

        required_keys = [
            "enclosure_ratio",
            "hard_surface_ratio",
            "soft_surface_ratio",
            "estimated_RT60_category",
            "acoustic_privacy_score",
            "reflectivity_estimate",
            "edge_density",
            "confidence",
        ]

        for key in required_keys:
            self.assertIn(key, result, f"Missing key: {key}")

    def test_range_constraints(self):
        """Test that numeric outputs are within valid ranges."""
        image = SyntheticImageGenerator.create_enclosed_room()
        image_path = SyntheticImageGenerator.save_image(image, self.temp_path)

        result = compute_acoustic_privacy_proxy(image_path)

        # All ratios should be [0, 1]
        self.assertGreaterEqual(result["enclosure_ratio"], 0.0)
        self.assertLessEqual(result["enclosure_ratio"], 1.0)
        self.assertGreaterEqual(result["hard_surface_ratio"], 0.0)
        self.assertLessEqual(result["hard_surface_ratio"], 1.0)
        self.assertGreaterEqual(result["acoustic_privacy_score"], 0.0)
        self.assertLessEqual(result["acoustic_privacy_score"], 1.0)

    def test_tiny_image(self):
        """Test acoustic proxy on tiny image."""
        image = SyntheticImageGenerator.create_tiny_image()
        image_path = SyntheticImageGenerator.save_image(image, self.temp_path)

        result = compute_acoustic_privacy_proxy(image_path)

        # Should handle tiny images gracefully
        self.assertIsNotNone(result)
        self.assertIn("confidence", result)

    def test_invalid_image_path(self):
        """Test handling of non-existent image path."""
        with self.assertRaises(Exception):
            compute_acoustic_privacy_proxy("/nonexistent/path/image.png")


class TestVisualPrivacy(unittest.TestCase):
    """Test NEW-11: Visual Privacy."""

    def setUp(self):
        """Create temporary directory for test images."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self):
        """Clean up temporary files."""
        self.temp_dir.cleanup()

    def test_enclosed_room_high_privacy(self):
        """Test visual privacy in enclosed room."""
        image = SyntheticImageGenerator.create_enclosed_room()
        image_path = SyntheticImageGenerator.save_image(image, self.temp_path)

        result = compute_visual_privacy(image_path)

        # Enclosed room should have high privacy
        self.assertGreater(result["privacy_score"], 0.3)
        # Should be semi or enclosed (may vary based on border width)
        self.assertIn(result["enclosure_level"], ["semi", "enclosed"])

    def test_open_space_low_privacy(self):
        """Test visual privacy in open space."""
        image = SyntheticImageGenerator.create_open_space()
        image_path = SyntheticImageGenerator.save_image(image, self.temp_path)

        result = compute_visual_privacy(image_path)

        # Open space should have low privacy
        self.assertLess(result["privacy_score"], 0.6)
        self.assertGreater(result["openness_ratio"], 0.4)

    def test_enclosure_level_values(self):
        """Test that enclosure level is valid."""
        image = SyntheticImageGenerator.create_indoor_scene()
        image_path = SyntheticImageGenerator.save_image(image, self.temp_path)

        result = compute_visual_privacy(image_path)

        self.assertIn(result["enclosure_level"], ["open", "semi", "enclosed"])

    def test_uniform_image(self):
        """Test visual privacy on uniform image."""
        image = SyntheticImageGenerator.create_uniform_color_image()
        image_path = SyntheticImageGenerator.save_image(image, self.temp_path)

        result = compute_visual_privacy(image_path)

        # Should return valid result
        self.assertIsNotNone(result)
        self.assertIn("privacy_score", result)

    def test_result_keys(self):
        """Test that all required keys are present."""
        image = SyntheticImageGenerator.create_enclosed_room()
        image_path = SyntheticImageGenerator.save_image(image, self.temp_path)

        result = compute_visual_privacy(image_path)

        required_keys = [
            "privacy_score",
            "openness_ratio",
            "barrier_count",
            "sightline_depth",
            "enclosure_level",
            "window_ratio",
            "border_edge_density",
            "confidence",
        ]

        for key in required_keys:
            self.assertIn(key, result, f"Missing key: {key}")

    def test_range_constraints(self):
        """Test that numeric outputs are within valid ranges."""
        image = SyntheticImageGenerator.create_outdoor_scene()
        image_path = SyntheticImageGenerator.save_image(image, self.temp_path)

        result = compute_visual_privacy(image_path)

        # Privacy score should be [0, 1]
        self.assertGreaterEqual(result["privacy_score"], 0.0)
        self.assertLessEqual(result["privacy_score"], 1.0)

        # Ratios should be [0, 1]
        self.assertGreaterEqual(result["openness_ratio"], 0.0)
        self.assertLessEqual(result["openness_ratio"], 1.0)
        self.assertGreaterEqual(result["window_ratio"], 0.0)
        self.assertLessEqual(result["window_ratio"], 1.0)

    def test_barrier_count_non_negative(self):
        """Test that barrier count is non-negative."""
        image = SyntheticImageGenerator.create_enclosed_room()
        image_path = SyntheticImageGenerator.save_image(image, self.temp_path)

        result = compute_visual_privacy(image_path)

        self.assertGreaterEqual(result["barrier_count"], 0)

    def test_tiny_image(self):
        """Test visual privacy on tiny image."""
        image = SyntheticImageGenerator.create_tiny_image()
        image_path = SyntheticImageGenerator.save_image(image, self.temp_path)

        result = compute_visual_privacy(image_path)

        # Should handle tiny images gracefully
        self.assertIsNotNone(result)
        self.assertIn("confidence", result)

    def test_all_black_image(self):
        """Test visual privacy on all-black image."""
        image = SyntheticImageGenerator.create_all_black_image()
        image_path = SyntheticImageGenerator.save_image(image, self.temp_path)

        result = compute_visual_privacy(image_path)

        # Should have high privacy (enclosed, no openness)
        self.assertGreater(result["privacy_score"], 0.5)

    def test_invalid_image_path(self):
        """Test handling of non-existent image path."""
        with self.assertRaises(Exception):
            compute_visual_privacy("/nonexistent/path/image.png")


if __name__ == "__main__":
    unittest.main()
