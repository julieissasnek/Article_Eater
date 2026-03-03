"""
test_iv_dv_classifier.py — Tests for the IV/DV taxonomy classifier
===================================================================
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.services.iv_dv_classifier import (
    IVDVClassifier, IVClassification, DVClassification, get_classifier,
)
from src.services.dv_generalization import DVAccessLevel, DVMeasurementType


class TestIVClassification:
    """Test IV (antecedent) classification."""

    def setup_method(self):
        self.clf = IVDVClassifier()

    # ── Stage 1: Pattern matching ──

    def test_cct_with_kelvin(self):
        """CCT with explicit K value → luminous.color_temp."""
        result = self.clf.classify_iv("CCT (5700 K vs 2700 K)")
        assert "luminous.color_temp" in result.node_id
        assert result.confidence >= 0.85
        assert result.method == "pattern"
        assert "CCT_K" in result.abstract_attributes

    def test_blue_enriched_light(self):
        """Blue-enriched white light → luminous.color_temp.enriched."""
        result = self.clf.classify_iv("Exposure to blue-enriched white light (17000K)")
        assert "luminous.color_temp" in result.node_id
        assert result.confidence >= 0.85

    def test_lux_value(self):
        """Lux value → luminous.illuminance."""
        result = self.clf.classify_iv("Illuminance level 300 lux vs 500 lux")
        assert "luminous.illuminance" in result.node_id
        assert result.confidence >= 0.80

    def test_ceiling_height_numeric(self):
        """Ceiling height with ft → spatial.height."""
        result = self.clf.classify_iv("Ceiling height 9.5 ft experimental condition")
        assert "spatial.height" in result.node_id
        assert result.confidence >= 0.85

    def test_temperature_celsius(self):
        """Temperature with °C → thermal.temperature."""
        result = self.clf.classify_iv("Temperature (29°C vs 24°C)")
        assert "thermal.temperature" in result.node_id
        assert result.confidence >= 0.80

    def test_fractal_dimension(self):
        """Fractal dimension → natural.biomorphic.fractal."""
        result = self.clf.classify_iv("fractal dimension (D-value) of 'global-forest' patterns")
        assert "fractal" in result.node_id
        assert result.confidence >= 0.85

    # ── Stage 3: Semantic map ──

    def test_open_plan_semantic(self):
        """Open plan office → spatial.openness.open_plan via semantic map."""
        result = self.clf.classify_iv("open plan office workspace")
        assert "spatial.openness" in result.node_id

    def test_natural_light_semantic(self):
        """Natural light → luminous.daylight."""
        result = self.clf.classify_iv("Natural light")
        assert "luminous.daylight" in result.node_id

    def test_window_presence(self):
        """Visual connection to outdoors → spatial.view."""
        result = self.clf.classify_iv("Visual connection to outdoors via a window (vs. windowless)")
        assert "spatial.view" in result.node_id

    def test_crowding_perception(self):
        """Crowding Perception → spatial.density."""
        result = self.clf.classify_iv("Crowding Perception")
        assert "spatial.density" in result.node_id or "crowding" in result.node_id.lower()

    # ── Stage 2: Keyword matching ──

    def test_dynamic_lighting_keywords(self):
        """Dynamic lighting pattern → luminous.artificial via keywords."""
        result = self.clf.classify_iv("Dynamic lighting pattern (DL) vs. Static lighting pattern (SL)")
        assert "luminous" in result.node_id

    def test_wood_material_keywords(self):
        """Japanese cedar lumber → material.wood."""
        result = self.clf.classify_iv("Room A (planed Japanese cedar lumber) vs Room B (printed grain resin sheet)")
        assert "material" in result.node_id or "wood" in result.node_id.lower()

    # ── Unclassified ──

    def test_unclassified_returns_raw(self):
        """Truly novel IV stays unclassified with confidence 0."""
        result = self.clf.classify_iv("XYZ-qwertyuiop-novel-zxcvbnm-99")
        assert result.confidence == 0.0
        assert result.method == "unclassified"
        assert result.node_id == "XYZ-qwertyuiop-novel-zxcvbnm-99"

    # ── Caching ──

    def test_caching(self):
        """Same input returns same result from cache."""
        r1 = self.clf.classify_iv("natural light")
        r2 = self.clf.classify_iv("natural light")
        assert r1.node_id == r2.node_id
        assert r1.confidence == r2.confidence


class TestDVClassification:
    """Test DV (consequent) classification."""

    def setup_method(self):
        self.clf = IVDVClassifier()

    def test_visual_comfort(self):
        result = self.clf.classify_dv("Visual comfort")
        assert "comfort" in result.node_id
        assert result.access_level == DVAccessLevel.CONSCIOUS
        assert result.measure_type == DVMeasurementType.SELF_REPORT

    def test_heart_rate(self):
        result = self.clf.classify_dv("Heart Rate (HR)")
        assert "heart_rate" in result.node_id or "physiology" in result.node_id
        assert result.access_level == DVAccessLevel.AUTONOMIC
        assert result.measure_type == DVMeasurementType.PHYSIOLOGICAL

    def test_rmssd(self):
        result = self.clf.classify_dv("RMSSD")
        assert "hrv" in result.node_id or "physiology" in result.node_id
        assert result.access_level == DVAccessLevel.AUTONOMIC

    def test_reaction_time(self):
        result = self.clf.classify_dv("Reaction time")
        assert "reaction_time" in result.node_id or "performance" in result.node_id
        assert result.access_level == DVAccessLevel.BEHAVIORAL

    def test_perceived_happiness(self):
        result = self.clf.classify_dv("perceived happiness")
        assert "happiness" in result.node_id or "positive" in result.node_id
        assert result.access_level == DVAccessLevel.CONSCIOUS

    def test_anxiety(self):
        result = self.clf.classify_dv("Student anxiety (likelihood)")
        assert "anxiety" in result.node_id or "negative" in result.node_id

    def test_place_attachment(self):
        result = self.clf.classify_dv("Place Attachment")
        assert "place_attachment" in result.node_id or "spatial_behavior" in result.node_id

    def test_thermal_comfort(self):
        result = self.clf.classify_dv("Thermal comfort")
        assert "comfort" in result.node_id
        assert result.access_level == DVAccessLevel.CONSCIOUS

    def test_eeg(self):
        result = self.clf.classify_dv("Alpha power EEG")
        assert result.access_level == DVAccessLevel.NEURAL
        assert result.measure_type == DVMeasurementType.NEUROIMAGING

    def test_unclassified_dv(self):
        result = self.clf.classify_dv("XYZ-completely-unknown-measure-42")
        assert result.confidence == 0.0
        assert result.method == "unclassified"


class TestBatchClassification:
    """Test batch processing."""

    def test_batch(self):
        clf = IVDVClassifier()
        findings = [
            {"antecedent": "CCT (5700 K)", "consequent": "Visual comfort"},
            {"antecedent": "Natural light", "consequent": "perceived happiness"},
            {"antecedent": "noise level", "consequent": "Reaction time"},
        ]
        results = clf.batch_classify(findings)
        assert len(results) == 3
        assert all("iv_node" in r for r in results)
        assert all("dv_node" in r for r in results)
        assert all("iv_confidence" in r for r in results)
        # First should classify to CCT
        assert "luminous.color_temp" in results[0]["iv_node"]

    def test_stats(self):
        clf = IVDVClassifier()
        clf.classify_iv("CCT (5700 K)")
        clf.classify_iv("unknown-thing-xyz")
        stats = clf.classification_stats()
        assert stats["total_classified"] == 2
        assert stats["by_method"]["unclassified"] == 1


class TestAccessLevelInference:
    """Test that access level and measure type are inferred correctly."""

    def setup_method(self):
        self.clf = IVDVClassifier()

    def test_self_report_inference(self):
        result = self.clf.classify_dv("overall satisfaction rating")
        assert result.access_level == DVAccessLevel.CONSCIOUS

    def test_physiological_inference(self):
        result = self.clf.classify_dv("salivary cortisol level")
        # V10 #6 Neuroscientist: Cortisol is NEUROENDOCRINE (HPA axis), not AUTONOMIC
        assert result.access_level == DVAccessLevel.NEUROENDOCRINE

    def test_performance_inference(self):
        result = self.clf.classify_dv("serial recall task accuracy")
        assert result.access_level == DVAccessLevel.BEHAVIORAL


class TestSingleton:
    """Test singleton behavior."""

    def test_singleton(self):
        c1 = get_classifier()
        c2 = get_classifier()
        assert c1 is c2
