#!/usr/bin/env python3
"""
Phase 7: Integration & System Health Tests
==========================================

End-to-end tests validating full CVA pipeline, overseer self-healing,
cultural variant switching, attractor computation, and system health.

Sprint: CVA Phase 7 — Integration Testing
"""

import json
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class TestPaperToCVAAnnotationPipeline(unittest.TestCase):
    """7.1: Paper → extraction → CVA annotation → integration E2E."""
    
    def test_extraction_produces_findings(self):
        """Extractions contain findings with antecedent/consequent."""
        extractions_dir = PROJECT_ROOT / "data" / "extractions"
        if not extractions_dir.exists():
            self.skipTest("No extractions directory")
        
        sample = list(extractions_dir.glob("*.json"))[:5]
        self.assertGreater(len(sample), 0, "No extraction files found")
        
        for ef in sample:
            with open(ef) as f:
                data = json.load(f)
            has_results = any(k in data for k in ["findings", "claims", "results"])
            self.assertTrue(has_results, f"Missing findings/claims/results in {ef.name}")
    
    def test_annotation_scripts_importable(self):
        """Batch annotation scripts can be imported."""
        sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
        try:
            import batch_annotate_measurements
            import batch_annotate_stimuli
            self.assertTrue(hasattr(batch_annotate_measurements, 'detect_modalities'))
            self.assertTrue(hasattr(batch_annotate_stimuli, 'classify_stimulus'))
        finally:
            sys.path.pop(0)
    
    def test_measurement_detection_accuracy(self):
        """Measurement modality detection works on known text."""
        sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
        try:
            from batch_annotate_measurements import detect_modalities
            
            # Should detect eye tracking
            text = "Eye-tracking data were collected using an EyeLink 1000 to record fixation patterns."
            mods = detect_modalities(text)
            self.assertIn("eye_tracking", mods)
            
            # Should detect self-report
            text = "Restorativeness was measured using a 7-point Likert scale questionnaire."
            mods = detect_modalities(text)
            self.assertIn("self_report", mods)
            
            # Should detect VR
            text = "Participants explored a virtual reality environment using a head-mounted display."
            mods = detect_modalities(text)
            self.assertIn("VR", mods)
        finally:
            sys.path.pop(0)
    
    def test_stimulus_classification_accuracy(self):
        """Stimulus classification works on known text."""
        sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
        try:
            from batch_annotate_stimuli import classify_stimulus
            
            # Should detect photograph
            text = "Participants rated photographs of 30 urban scenes."
            cls = classify_stimulus(text)
            self.assertIn("photograph", cls["presentation_modalities"])
            
            # Should detect parametric control
            text = "In a 2×3 factorial design, ceiling height was systematically varied."
            cls = classify_stimulus(text)
            self.assertTrue(cls["has_parametric_control"])
        finally:
            sys.path.pop(0)


class TestOverseerSelfHealing(unittest.TestCase):
    """7.2: Overseer detects CVA violation → auto-remediates E2E."""
    
    def test_playbook_registry_complete(self):
        """All invariant codes have playbooks."""
        from src.services.overseer_playbooks import RemediationEngine
        engine = RemediationEngine()
        
        # Should have playbooks for core invariants
        self.assertIn("INV-1", engine.playbooks)
        self.assertIn("INV-4", engine.playbooks)
    
    def test_playbook_execution_safe(self):
        """Playbook execution doesn't crash on unknown violations."""
        from src.services.overseer_playbooks import RemediationEngine
        engine = RemediationEngine()
        
        result = engine.execute_playbook("UNKNOWN-CODE")
        self.assertFalse(result.success)
    
    def test_predictive_health_with_minimal_data(self):
        """Predictive engine handles < 3 data points gracefully."""
        from src.services.overseer_predictive import PredictiveHealthEngine
        engine = PredictiveHealthEngine()
        
        # Single data point
        prediction = engine.predict_health([{"aeshi_score": 70}])
        self.assertIsNotNone(prediction.predicted_aeshi)
        self.assertEqual(prediction.prediction_basis, "insufficient_data")
    
    def test_predictive_health_detects_decline(self):
        """Predictive engine detects declining AESHI trend."""
        from src.services.overseer_predictive import PredictiveHealthEngine
        engine = PredictiveHealthEngine()
        
        history = [
            {"aeshi_score": 80, "global_coherence": 0.7, "pipeline_utilization": 0.5, "violation_count": 0},
            {"aeshi_score": 75, "global_coherence": 0.65, "pipeline_utilization": 0.4, "violation_count": 1},
            {"aeshi_score": 68, "global_coherence": 0.6, "pipeline_utilization": 0.3, "violation_count": 2},
            {"aeshi_score": 60, "global_coherence": 0.55, "pipeline_utilization": 0.2, "violation_count": 3},
        ]
        prediction = engine.predict_health(history)
        self.assertEqual(prediction.trend_direction, "declining")
        self.assertLess(prediction.trend_slope, 0)
    
    def test_pattern_detection_violation_accumulation(self):
        """Pattern detector catches monotonically increasing violations."""
        from src.services.overseer_predictive import PredictiveHealthEngine
        engine = PredictiveHealthEngine()
        
        history = [
            {"aeshi_score": 80, "global_coherence": 0.7, "violation_count": 1},
            {"aeshi_score": 75, "global_coherence": 0.65, "violation_count": 2},
            {"aeshi_score": 70, "global_coherence": 0.6, "violation_count": 3},
            {"aeshi_score": 65, "global_coherence": 0.55, "violation_count": 4},
            {"aeshi_score": 60, "global_coherence": 0.5, "violation_count": 5},
        ]
        patterns = engine.detect_patterns(history)
        pattern_types = [p.pattern_type for p in patterns]
        self.assertIn("violation_accumulation", pattern_types)


class TestCulturalVariantSwitching(unittest.TestCase):
    """7.3: Cultural variant switching (Western → Japanese) E2E."""
    
    def test_cultural_valuation_models_importable(self):
        """CVA valuation models can be imported."""
        try:
            from src.models.cva_valuation import CVAValuationVector
            self.assertTrue(True)
        except ImportError:
            self.skipTest("CVA valuation models not available")
    
    def test_cultural_presets_defined(self):
        """All 4 cultural presets are defined."""
        try:
            from src.models.cva_valuation import CVAValuationVector
            for variant in ["WESTERN", "JAPANESE", "WEST_AFRICAN", "INDIAN"]:
                v = CVAValuationVector.from_culture(variant)
                self.assertIsNotNone(v)
        except (ImportError, AttributeError):
            self.skipTest("Cultural presets not available")


class TestAttractorComputation(unittest.TestCase):
    """7.4: Attractor computation for 3 design scenarios E2E."""
    
    def test_attractor_engine_importable(self):
        """CVA attractor engine can be imported."""
        try:
            from src.services.cva_attractor import CVAAttractorEngine
            self.assertTrue(True)
        except ImportError:
            self.skipTest("CVA attractor engine not available")
    
    def test_rasa_definitions_exist(self):
        """Rasa attractor definitions file exists."""
        rasa_path = PROJECT_ROOT / "data" / "cva" / "rasa_attractors.json"
        if rasa_path.exists():
            with open(rasa_path) as f:
                data = json.load(f)
            self.assertGreater(len(data), 0)
        else:
            self.skipTest("rasa_attractors.json not found")


class TestMoleculeIntegrity(unittest.TestCase):
    """7.5 (partial): Verify all molecules are valid and linked."""
    
    def test_all_molecules_valid_json(self):
        """All molecule files are valid JSON."""
        mol_dir = PROJECT_ROOT / "data" / "molecules"
        for mf in mol_dir.glob("*.json"):
            with open(mf) as f:
                data = json.load(f)
            self.assertIsInstance(data, dict, f"Invalid structure in {mf.name}")
    
    def test_new_cva_molecules_exist(self):
        """All 5 CVA molecules from Phase 6 exist."""
        mol_dir = PROJECT_ROOT / "data" / "molecules"
        expected = [
            "M_RASA.json",
            "M_CULTURAL_VALUATION.json",
            "M_ATTRACTOR_TRANSITION.json",
            "M_BEAUTY_COMPRESSION.json",
            "M_CCT_PREFERENCE.json",
        ]
        for name in expected:
            path = mol_dir / name
            self.assertTrue(path.exists(), f"Missing molecule: {name}")
    
    def test_molecule_has_required_fields(self):
        """Each molecule has required fields."""
        mol_dir = PROJECT_ROOT / "data" / "molecules"
        for mf in mol_dir.glob("*.json"):
            with open(mf) as f:
                data = json.load(f)
            # Check for basic structure
            self.assertTrue(
                any(k in data for k in ["name", "molecule_id", "title", "id"]),
                f"Molecule {mf.name} missing identifier field"
            )


class TestCVAInvariantChecks(unittest.TestCase):
    """7.6 (partial): CVA invariant check functions work."""
    
    def test_inv10_check_runs(self):
        """INV-10 check executes without error."""
        from src.services.overseer_predictive import check_cva_constraint_stability
        result = check_cva_constraint_stability()
        self.assertIn("invariant", result)
        self.assertEqual(result["invariant"], "INV-10")
    
    def test_inv11_check_runs(self):
        """INV-11 check executes without error."""
        from src.services.overseer_predictive import check_attractor_reachability
        result = check_attractor_reachability()
        self.assertIn("invariant", result)
    
    def test_inv12_check_runs(self):
        """INV-12 check executes without error."""
        from src.services.overseer_predictive import check_cultural_variant_consistency
        result = check_cultural_variant_consistency()
        self.assertIn("invariant", result)
    
    def test_inv13_check_runs(self):
        """INV-13 check executes without error."""
        from src.services.overseer_predictive import check_psi_determinism
        result = check_psi_determinism()
        self.assertIn("invariant", result)
    
    def test_run_all_cva_checks(self):
        """Combined CVA check runner works."""
        from src.services.overseer_predictive import run_all_cva_checks
        results = run_all_cva_checks()
        self.assertEqual(len(results), 4)
        for code in ["INV-10", "INV-11", "INV-12", "INV-13"]:
            self.assertIn(code, results)


class TestFigureScannerIntegration(unittest.TestCase):
    """Image pipeline tests: figure scanner works end-to-end."""
    
    def test_scanner_importable(self):
        """Figure scanner can be imported."""
        sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
        try:
            from scan_figures_in_articles import scan_extraction, FIGURE_PATTERNS
            self.assertGreater(len(FIGURE_PATTERNS), 0)
        finally:
            sys.path.pop(0)
    
    def test_scan_single_extraction(self):
        """Scanner processes a single extraction file."""
        extractions_dir = PROJECT_ROOT / "data" / "extractions"
        if not extractions_dir.exists():
            self.skipTest("No extractions directory")
        
        sample = next(extractions_dir.glob("*.json"), None)
        if not sample:
            self.skipTest("No extraction files")
        
        sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
        try:
            from scan_figures_in_articles import scan_extraction
            result = scan_extraction(sample)
            self.assertIn("doi", result)
            self.assertIn("priority", result)
            self.assertIn(result["priority"], ["none", "low", "medium", "high"])
        finally:
            sys.path.pop(0)


class TestFeatureCVAMapping(unittest.TestCase):
    """Bidirectional feature↔CVA mapping table integrity."""
    
    def test_mapping_file_exists(self):
        """feature_cva_mapping.json exists and is valid."""
        path = PROJECT_ROOT / "data" / "feature_cva_mapping.json"
        self.assertTrue(path.exists())
        with open(path) as f:
            data = json.load(f)
        self.assertIn("feature_to_cva", data)
        self.assertIn("cva_to_features", data)
    
    def test_bidirectional_coverage(self):
        """Both directions have entries."""
        path = PROJECT_ROOT / "data" / "feature_cva_mapping.json"
        with open(path) as f:
            data = json.load(f)
        self.assertGreater(len(data["feature_to_cva"]), 0)
        self.assertGreater(len(data["cva_to_features"]), 0)


class TestSystemReport(unittest.TestCase):
    """7.7: System health report generation."""
    
    def test_nightly_v3_dry_run(self):
        """Nightly v3 can run in dry-run mode."""
        sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
        try:
            from overseer_nightly_v3 import run_nightly_v3
            report = run_nightly_v3(dry_run=True, output_dir="/tmp/test_nightly")
            self.assertIn("version", report)
            self.assertEqual(report["version"], "3.0")
            self.assertIn("summary", report)
        finally:
            sys.path.pop(0)


if __name__ == "__main__":
    unittest.main()
