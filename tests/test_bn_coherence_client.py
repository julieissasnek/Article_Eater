"""
Tests for BN Coherence Client (ARCH-4 Integration).

Tests the Article_Eater → BN_graphical integration layer.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import unittest
from services.bn_coherence_client import (
    BNCoherenceClient,
    CoherenceCheckResult,
    CoherenceCheckStatus,
    check_beliefs_coherence,
    convert_to_dual_format,
    pre_integration_check,
    should_integrate_belief
)


class TestBNCoherenceClientAvailability(unittest.TestCase):
    """Test client availability and initialization."""

    def test_client_initializes(self):
        """Client should initialize without error."""
        client = BNCoherenceClient()
        # Should not raise

    def test_is_available_property(self):
        """is_available should return True if BN_graphical is accessible."""
        client = BNCoherenceClient()
        # Will be True if BN_graphical path exists and imports work
        self.assertIsInstance(client.is_available, bool)


class TestCoherenceCheckResult(unittest.TestCase):
    """Test CoherenceCheckResult dataclass."""

    def test_result_defaults(self):
        """Result should have sensible defaults."""
        result = CoherenceCheckResult(status=CoherenceCheckStatus.PASSED)

        self.assertEqual(result.status, CoherenceCheckStatus.PASSED)
        self.assertEqual(result.conflicts, [])
        self.assertEqual(result.resolutions, [])
        self.assertEqual(result.calibration_issues, [])

    def test_has_conflicts_property(self):
        """has_conflicts should reflect conflict list."""
        result = CoherenceCheckResult(
            status=CoherenceCheckStatus.CONFLICT,
            conflicts=[{"conflict_id": "c1"}]
        )
        self.assertTrue(result.has_conflicts)

        clean_result = CoherenceCheckResult(status=CoherenceCheckStatus.PASSED)
        self.assertFalse(clean_result.has_conflicts)

    def test_is_clean_property(self):
        """is_clean should be True only for PASSED status."""
        passed = CoherenceCheckResult(status=CoherenceCheckStatus.PASSED)
        self.assertTrue(passed.is_clean)

        warning = CoherenceCheckResult(status=CoherenceCheckStatus.WARNING)
        self.assertFalse(warning.is_clean)

    def test_to_dict(self):
        """Should serialize to dictionary."""
        result = CoherenceCheckResult(
            status=CoherenceCheckStatus.CONFLICT,
            conflicts=[{"id": "c1"}],
            errors=["test error"]
        )

        d = result.to_dict()
        self.assertEqual(d["status"], "conflict")
        self.assertEqual(len(d["conflicts"]), 1)
        self.assertEqual(d["errors"], ["test error"])


class TestBNCoherenceClientValidation(unittest.TestCase):
    """Test belief validation through BN coherence."""

    def setUp(self):
        self.client = BNCoherenceClient()

    @unittest.skipUnless(
        BNCoherenceClient().is_available,
        "BN_graphical not available"
    )
    def test_validate_single_belief(self):
        """Should validate a single belief."""
        belief = {
            "belief_id": "test_1",
            "content": "Natural light improves mood",
            "confidence": 0.8,
            "level": "OBSERVATIONAL"
        }

        result = self.client.validate_beliefs([belief])

        self.assertIn(result.status, [
            CoherenceCheckStatus.PASSED,
            CoherenceCheckStatus.WARNING
        ])
        self.assertEqual(len(result.processed_beliefs), 1)

    @unittest.skipUnless(
        BNCoherenceClient().is_available,
        "BN_graphical not available"
    )
    def test_validate_conflicting_beliefs(self):
        """Should detect conflicts between beliefs."""
        new_belief = {
            "belief_id": "new_1",
            "content": "Daylight increases focus",
            "confidence": 0.85,
            "level": "EMPIRICAL"
        }

        existing = {
            "existing_1": {
                "belief_id": "existing_1",
                "content": "Daylight decreases focus",
                "confidence": 0.7,
                "level": "EMPIRICAL"
            }
        }

        result = self.client.validate_beliefs([new_belief], existing)

        self.assertTrue(result.has_conflicts)

    @unittest.skipUnless(
        BNCoherenceClient().is_available,
        "BN_graphical not available"
    )
    def test_validate_empty_list(self):
        """Should handle empty belief list."""
        result = self.client.validate_beliefs([])

        self.assertEqual(result.status, CoherenceCheckStatus.PASSED)
        self.assertEqual(len(result.processed_beliefs), 0)

    def test_unavailable_returns_status(self):
        """When BN unavailable, should return appropriate status."""
        # Force unavailable state for testing
        client = BNCoherenceClient()
        if not client.is_available:
            result = client.validate_beliefs([{"belief_id": "test"}])
            self.assertEqual(result.status, CoherenceCheckStatus.BN_UNAVAILABLE)


class TestFormatConversion(unittest.TestCase):
    """Test belief format conversion."""

    @unittest.skipUnless(
        BNCoherenceClient().is_available,
        "BN_graphical not available"
    )
    def test_convert_to_dual_format(self):
        """Should convert belief to dual format."""
        belief = {
            "belief_id": "convert_1",
            "confidence": 0.8,
            "level": "OBSERVATIONAL"
        }

        result = convert_to_dual_format(belief)

        self.assertIn("status_v1", result)
        self.assertIn("status_v2", result)

    @unittest.skipUnless(
        BNCoherenceClient().is_available,
        "BN_graphical not available"
    )
    def test_convert_preserves_original_fields(self):
        """Conversion should preserve original belief fields."""
        belief = {
            "belief_id": "preserve_1",
            "content": "Test content",
            "confidence": 0.8,
            "custom_field": "custom_value"
        }

        result = convert_to_dual_format(belief)

        self.assertEqual(result["belief_id"], "preserve_1")
        self.assertEqual(result["content"], "Test content")
        self.assertEqual(result["custom_field"], "custom_value")


class TestConvenienceFunctions(unittest.TestCase):
    """Test convenience functions."""

    @unittest.skipUnless(
        BNCoherenceClient().is_available,
        "BN_graphical not available"
    )
    def test_check_beliefs_coherence_function(self):
        """Convenience function should work."""
        beliefs = [{"belief_id": "conv_1", "confidence": 0.8, "level": "OBSERVATIONAL"}]

        result = check_beliefs_coherence(beliefs)

        self.assertIsInstance(result, CoherenceCheckResult)

    @unittest.skipUnless(
        BNCoherenceClient().is_available,
        "BN_graphical not available"
    )
    def test_check_single_belief_method(self):
        """check_single_belief should work."""
        client = BNCoherenceClient()
        belief = {"belief_id": "single_1", "confidence": 0.8, "level": "OBSERVATIONAL"}

        result = client.check_single_belief(belief)

        self.assertIsInstance(result, CoherenceCheckResult)


class TestWebIntegrationHooks(unittest.TestCase):
    """Test WebOfBelief integration hooks."""

    @unittest.skipUnless(
        BNCoherenceClient().is_available,
        "BN_graphical not available"
    )
    def test_pre_integration_check(self):
        """pre_integration_check should process beliefs."""
        new_beliefs = [
            {"belief_id": "new_1", "confidence": 0.8, "level": "OBSERVATIONAL"}
        ]

        web_state = {
            "beliefs": [
                {"belief_id": "existing_1", "confidence": 0.7, "level": "OBSERVATIONAL"}
            ],
            "constraints": []
        }

        processed, result = pre_integration_check(new_beliefs, web_state)

        self.assertEqual(len(processed), 1)
        self.assertIsInstance(result, CoherenceCheckResult)

    @unittest.skipUnless(
        BNCoherenceClient().is_available,
        "BN_graphical not available"
    )
    def test_pre_integration_extracts_support_relations(self):
        """Should extract support relations from constraints."""
        new_beliefs = [
            {"belief_id": "new_1", "confidence": 0.8, "level": "EMPIRICAL"}
        ]

        web_state = {
            "beliefs": [
                {"belief_id": "obs_1", "confidence": 0.9, "level": "OBSERVATIONAL"},
                {"belief_id": "emp_1", "confidence": 0.8, "level": "EMPIRICAL"}
            ],
            "constraints": [
                {
                    "constraint_type": "SUPPORTS",
                    "source_id": "obs_1",
                    "target_id": "emp_1"
                }
            ]
        }

        processed, result = pre_integration_check(new_beliefs, web_state)

        # Should complete without error
        self.assertIsInstance(result, CoherenceCheckResult)

    def test_should_integrate_belief_passed(self):
        """Should allow integration when passed."""
        belief = {"belief_id": "test_1"}
        result = CoherenceCheckResult(status=CoherenceCheckStatus.PASSED)

        should, reason = should_integrate_belief(belief, result)

        self.assertTrue(should)

    def test_should_integrate_belief_failed(self):
        """Should block integration when failed."""
        belief = {"belief_id": "test_1"}
        result = CoherenceCheckResult(
            status=CoherenceCheckStatus.FAILED,
            errors=["Test failure"]
        )

        should, reason = should_integrate_belief(belief, result)

        self.assertFalse(should)
        self.assertIn("failed", reason.lower())

    def test_should_integrate_conflict_with_allow(self):
        """Should allow conflict when allow_conflicts=True."""
        belief = {"belief_id": "conflict_1"}
        result = CoherenceCheckResult(
            status=CoherenceCheckStatus.CONFLICT,
            conflicts=[{
                "conflict_id": "c1",
                "prediction_id": "conflict_1",
                "severity": "critical"
            }]
        )

        # Without allow
        should, reason = should_integrate_belief(belief, result, allow_conflicts=False)
        self.assertFalse(should)

        # With allow
        should, reason = should_integrate_belief(belief, result, allow_conflicts=True)
        self.assertTrue(should)

    def test_should_integrate_bn_unavailable(self):
        """Should allow integration when BN unavailable (graceful degradation)."""
        belief = {"belief_id": "test_1"}
        result = CoherenceCheckResult(status=CoherenceCheckStatus.BN_UNAVAILABLE)

        should, reason = should_integrate_belief(belief, result)

        self.assertTrue(should)
        self.assertIn("unavailable", reason.lower())


class TestClientConfiguration(unittest.TestCase):
    """Test client configuration options."""

    def test_custom_output_format(self):
        """Should accept custom output format."""
        client = BNCoherenceClient(output_format="v1")
        # Should not raise

    def test_custom_threshold(self):
        """Should accept custom incoherence threshold."""
        client = BNCoherenceClient(incoherence_threshold=0.5)
        # Should not raise

    def test_disable_calibration(self):
        """Should accept run_calibration=False."""
        client = BNCoherenceClient(run_calibration=False)
        # Should not raise


if __name__ == '__main__':
    unittest.main()
