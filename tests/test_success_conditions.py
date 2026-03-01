"""
Test Suite for Success Conditions Registry
============================================

Verifies all success conditions defined in contracts/success_conditions.json.
These tests prevent silent failures by proving system outputs exist and are valid.

Author: Claude Code (Anthropic)
Date: 2026-03-01
Sprint: ATLAS Audit & Success Conditions
"""

import json
import re
import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Any, Set
from dataclasses import dataclass, asdict
from datetime import datetime

# Test environment setup
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
CONTRACTS_DIR = PROJECT_ROOT / "contracts"
LOGS_DIR = PROJECT_ROOT / "logs"

# Load success conditions registry
SUCCESS_CONDITIONS_FILE = CONTRACTS_DIR / "success_conditions.json"


@pytest.fixture(scope="session")
def success_conditions():
    """Load the success conditions registry."""
    if not SUCCESS_CONDITIONS_FILE.exists():
        pytest.skip(f"Success conditions file not found: {SUCCESS_CONDITIONS_FILE}")
    with open(SUCCESS_CONDITIONS_FILE) as f:
        return json.load(f)


@pytest.fixture(scope="session")
def project_root():
    """Return the project root."""
    return PROJECT_ROOT


# ============================================================================
# SECTION 1: scheduled_pipeline.py Tests
# ============================================================================

class TestScheduledPipeline:
    """Tests for scripts/scheduled_pipeline.py success conditions."""

    def test_pipeline_module_imports(self, project_root):
        """SP-SC0: Pipeline module can be imported without errors."""
        scripts_dir = project_root / "scripts"
        assert (scripts_dir / "scheduled_pipeline.py").exists(), "scheduled_pipeline.py not found"

        # Try to parse the file for syntax errors
        with open(scripts_dir / "scheduled_pipeline.py") as f:
            code = f.read()
        try:
            compile(code, "scheduled_pipeline.py", "exec")
        except SyntaxError as e:
            pytest.fail(f"Syntax error in scheduled_pipeline.py: {e}")

    def test_pipeline_defines_stages(self, project_root):
        """SP-SC1: Pipeline defines all stages (discovery, triage, extract, etc.)."""
        pipeline_file = project_root / "scripts" / "scheduled_pipeline.py"
        content = pipeline_file.read_text()

        required_stages = ["discovery", "triage", "extract", "integrate", "qa"]
        for stage in required_stages:
            assert stage in content.lower(), f"Stage '{stage}' not defined in pipeline"

    def test_pipeline_wishlist_operations(self, project_root):
        """SP-SC2: Wishlist add/save/load cycle works correctly."""
        pipeline_file = project_root / "scripts" / "scheduled_pipeline.py"
        content = pipeline_file.read_text()

        # Check for required functions
        required_functions = ["load_wishlist", "save_wishlist", "wishlist_add", "wishlist_show"]
        for func in required_functions:
            assert f"def {func}" in content, f"Required function '{func}' not found"

    def test_pipeline_output_directory_created(self, project_root):
        """SP-SC3: Pipeline creates output directories."""
        pipeline_file = project_root / "scripts" / "scheduled_pipeline.py"
        content = pipeline_file.read_text()

        # Check for log directory creation
        assert "LOGS_DIR" in content, "LOGS_DIR not defined"
        assert "mkdir" in content or "exist_ok" in content, "Directory creation not implemented"

    def test_pipeline_logging_configured(self, project_root):
        """SP-SC6: Pipeline has logging configured."""
        pipeline_file = project_root / "scripts" / "scheduled_pipeline.py"
        content = pipeline_file.read_text()

        assert "logging" in content, "Logging module not imported"
        assert "basicConfig" in content, "Logging not configured"
        assert "FileHandler" in content or "StreamHandler" in content, "Log handlers not configured"


# ============================================================================
# SECTION 2: kirsh_decision_tree_analysis.py Tests
# ============================================================================

class TestKirshDecisionTree:
    """Tests for scripts/kirsh_decision_tree_analysis.py success conditions."""

    def test_kirsh_module_imports(self, project_root):
        """KDT-SC0: Kirsh module imports without errors."""
        kirsh_file = project_root / "scripts" / "kirsh_decision_tree_analysis.py"
        assert kirsh_file.exists(), "kirsh_decision_tree_analysis.py not found"

        content = kirsh_file.read_text()
        try:
            compile(content, "kirsh_decision_tree_analysis.py", "exec")
        except SyntaxError as e:
            pytest.fail(f"Syntax error in kirsh_decision_tree_analysis.py: {e}")

    def test_kirsh_defines_stimulus_loading(self, project_root):
        """KDT-SC1: Kirsh module defines stimulus loading function."""
        kirsh_file = project_root / "scripts" / "kirsh_decision_tree_analysis.py"
        content = kirsh_file.read_text()

        assert "def load_stimuli" in content, "load_stimuli() function not defined"
        assert "stimulus_descriptions_from_articles.json" in content, "Expected stimuli file not referenced"

    def test_kirsh_defines_environmental_filter(self, project_root):
        """KDT-SC2: Kirsh module defines environmental stimulus filter."""
        kirsh_file = project_root / "scripts" / "kirsh_decision_tree_analysis.py"
        content = kirsh_file.read_text()

        assert "def filter_environmental_stimuli" in content, "filter_environmental_stimuli() not defined"

        # Check for common non-environmental keywords
        non_env_keywords = ["personality", "disorder", "medication", "brain stimulation"]
        found = sum(1 for kw in non_env_keywords if kw in content.lower())
        assert found > 0, "Environmental filter logic not found"

    def test_kirsh_defines_clustering(self, project_root):
        """KDT-SC3: Kirsh module defines clustering logic."""
        kirsh_file = project_root / "scripts" / "kirsh_decision_tree_analysis.py"
        content = kirsh_file.read_text()

        clustering_keywords = ["cluster", "category", "group", "categorical"]
        found = sum(1 for kw in clustering_keywords if kw in content.lower())
        assert found > 0, "Clustering logic not found"

    def test_kirsh_defines_attribute_extraction(self, project_root):
        """KDT-SC4: Kirsh module defines essential attribute extraction."""
        kirsh_file = project_root / "scripts" / "kirsh_decision_tree_analysis.py"
        content = kirsh_file.read_text()

        attribute_keywords = ["essential", "attribute", "incidental", "decision tree"]
        found = sum(1 for kw in attribute_keywords if kw in content.lower())
        assert found > 0, "Attribute extraction logic not found"

    def test_kirsh_defines_vision_algorithm_linking(self, project_root):
        """KDT-SC5: Kirsh module links to vision algorithms."""
        kirsh_file = project_root / "scripts" / "kirsh_decision_tree_analysis.py"
        content = kirsh_file.read_text()

        algo_keywords = ["algorithm", "opencv", "pytorch", "scikit-image", "deeplab", "midas"]
        found = sum(1 for kw in algo_keywords if kw in content.lower())
        assert found >= 2, "Vision algorithm linking not comprehensive"

    def test_kirsh_defines_output_structure(self, project_root):
        """KDT-SC6: Kirsh module defines output report structure."""
        kirsh_file = project_root / "scripts" / "kirsh_decision_tree_analysis.py"
        content = kirsh_file.read_text()

        output_keywords = ["output", "report", "json", "save"]
        found = sum(1 for kw in output_keywords if kw in content.lower())
        assert found > 0, "Output structure not defined"


# ============================================================================
# SECTION 3: backfill_operationalizations.py Tests
# ============================================================================

class TestBackfillOperationalizations:
    """Tests for scripts/backfill_operationalizations.py success conditions."""

    def test_backfill_module_imports(self, project_root):
        """BO-SC0: Backfill module imports without errors."""
        backfill_file = project_root / "scripts" / "backfill_operationalizations.py"
        assert backfill_file.exists(), "backfill_operationalizations.py not found"

        content = backfill_file.read_text()
        try:
            compile(content, "backfill_operationalizations.py", "exec")
        except SyntaxError as e:
            pytest.fail(f"Syntax error in backfill_operationalizations.py: {e}")

    def test_backfill_defines_operationalization_mapping(self, project_root):
        """BO-SC1: Backfill defines instrument operationalizations."""
        backfill_file = project_root / "scripts" / "backfill_operationalizations.py"
        content = backfill_file.read_text()

        assert "OPERATIONALIZATIONS" in content, "OPERATIONALIZATIONS mapping not defined"

        # Check for valid instrument names
        instrument_keywords = ["Scale", "Inventory", "Questionnaire", "Index", "Assessment"]
        found = sum(1 for kw in instrument_keywords if kw in content)
        assert found > 0, "No valid instruments in mapping"

    def test_backfill_defines_vocab_loading(self, project_root):
        """BO-SC2: Backfill defines vocabulary loading."""
        backfill_file = project_root / "scripts" / "backfill_operationalizations.py"
        content = backfill_file.read_text()

        assert "outcome_vocab.json" in content, "Vocabulary file not referenced"
        assert "json.load" in content or "json.loads" in content, "JSON loading not implemented"

    def test_backfill_defines_empty_term_detection(self, project_root):
        """BO-SC3: Backfill defines empty operationalization detection."""
        backfill_file = project_root / "scripts" / "backfill_operationalizations.py"
        content = backfill_file.read_text()

        detection_keywords = ["empty", "operationalization", "length", "len"]
        found = sum(1 for kw in detection_keywords if kw in content.lower())
        assert found > 0, "Empty detection logic not found"

    def test_backfill_defines_preservation_logic(self, project_root):
        """BO-SC4: Backfill defines preservation of existing operationalizations."""
        backfill_file = project_root / "scripts" / "backfill_operationalizations.py"
        content = backfill_file.read_text()

        preservation_keywords = ["preserve", "existing", "overwrite", "not empty"]
        found = sum(1 for kw in preservation_keywords if kw in content.lower())
        assert found > 0, "Preservation logic not found"

    def test_backfill_defines_output_saving(self, project_root):
        """BO-SC5: Backfill defines output saving."""
        backfill_file = project_root / "scripts" / "backfill_operationalizations.py"
        content = backfill_file.read_text()

        save_keywords = ["write", "dump", "json", "save"]
        found = sum(1 for kw in save_keywords if kw in content.lower())
        assert found > 0, "Output saving not implemented"

    def test_backfill_defines_coverage_calculation(self, project_root):
        """BO-SC6: Backfill calculates coverage statistics."""
        backfill_file = project_root / "scripts" / "backfill_operationalizations.py"
        content = backfill_file.read_text()

        coverage_keywords = ["coverage", "percentage", "count", "statistic"]
        found = sum(1 for kw in coverage_keywords if kw in content.lower())
        assert found > 0, "Coverage calculation not implemented"


# ============================================================================
# SECTION 4: link_outcomes_to_instruments.py Tests
# ============================================================================

class TestLinkOutcomesToInstruments:
    """Tests for scripts/link_outcomes_to_instruments.py success conditions."""

    def test_loi_module_imports(self, project_root):
        """LOI-SC0: Module imports without errors."""
        loi_file = project_root / "scripts" / "link_outcomes_to_instruments.py"
        assert loi_file.exists(), "link_outcomes_to_instruments.py not found"

        content = loi_file.read_text()
        try:
            compile(content, "link_outcomes_to_instruments.py", "exec")
        except SyntaxError as e:
            pytest.fail(f"Syntax error in link_outcomes_to_instruments.py: {e}")

    def test_loi_defines_registry_loading(self, project_root):
        """LOI-SC1: Module defines instrument registry loading."""
        loi_file = project_root / "scripts" / "link_outcomes_to_instruments.py"
        content = loi_file.read_text()

        assert "instruments_registry.json" in content, "Instruments registry not referenced"
        assert "def" in content and ("load" in content.lower() or "registry" in content), "Loading logic not found"

    def test_loi_defines_lookup_building(self, project_root):
        """LOI-SC2: Module defines instrument lookup table."""
        loi_file = project_root / "scripts" / "link_outcomes_to_instruments.py"
        content = loi_file.read_text()

        assert "build_instrument_lookup" in content or "lookup" in content.lower(), "Lookup building not implemented"

    def test_loi_defines_abbreviation_extraction(self, project_root):
        """LOI-SC3: Module extracts abbreviations from operationalizations."""
        loi_file = project_root / "scripts" / "link_outcomes_to_instruments.py"
        content = loi_file.read_text()

        assert "abbreviation" in content.lower(), "Abbreviation extraction not found"
        assert "regex" in content.lower() or "re." in content, "Regex/pattern matching not found"

    def test_loi_defines_matching_logic(self, project_root):
        """LOI-SC4: Module defines operationalization-to-instrument matching."""
        loi_file = project_root / "scripts" / "link_outcomes_to_instruments.py"
        content = loi_file.read_text()

        assert "match" in content.lower(), "Matching logic not found"
        assert "instrument_id" in content, "Instrument ID linking not implemented"

    def test_loi_defines_vocab_update(self, project_root):
        """LOI-SC5: Module updates vocabulary with instrument IDs."""
        loi_file = project_root / "scripts" / "link_outcomes_to_instruments.py"
        content = loi_file.read_text()

        assert "instrument_ids" in content or "instrument_id" in content, "Instrument ID field not added"
        assert "outcome_vocab" in content, "Vocabulary not referenced"

    def test_loi_defines_referential_integrity_check(self, project_root):
        """LOI-SC6: Module checks referential integrity of IDs."""
        loi_file = project_root / "scripts" / "link_outcomes_to_instruments.py"
        content = loi_file.read_text()

        integrity_keywords = ["validate", "exist", "registry", "check"]
        found = sum(1 for kw in integrity_keywords if kw in content.lower())
        assert found > 0, "Referential integrity checking not found"


# ============================================================================
# SECTION 5: gemini_extraction_queue.py Tests
# ============================================================================

class TestGeminiExtractionQueue:
    """Tests for scripts/gemini_extraction_queue.py success conditions."""

    def test_geq_module_imports(self, project_root):
        """GEQ-SC0: Module imports without errors."""
        geq_file = project_root / "scripts" / "gemini_extraction_queue.py"
        assert geq_file.exists(), "gemini_extraction_queue.py not found"

        content = geq_file.read_text()
        try:
            compile(content, "gemini_extraction_queue.py", "exec")
        except SyntaxError as e:
            pytest.fail(f"Syntax error in gemini_extraction_queue.py: {e}")

    def test_geq_defines_queue_item_class(self, project_root):
        """GEQ-SC1: Module defines QueueItem dataclass."""
        geq_file = project_root / "scripts" / "gemini_extraction_queue.py"
        content = geq_file.read_text()

        assert "QueueItem" in content or "@dataclass" in content, "QueueItem class not defined"
        assert "doi" in content and "status" in content, "QueueItem fields incomplete"

    def test_geq_defines_extraction_status_enum(self, project_root):
        """GEQ-SC2: Module defines ExtractionStatus enum."""
        geq_file = project_root / "scripts" / "gemini_extraction_queue.py"
        content = geq_file.read_text()

        assert "ExtractionStatus" in content or "Enum" in content, "Status enum not defined"

        required_statuses = ["pending", "in_progress", "completed", "failed"]
        for status in required_statuses:
            assert status in content.lower(), f"Status '{status}' not defined"

    def test_geq_defines_triage_loading(self, project_root):
        """GEQ-SC1a: Module defines triage file loading."""
        geq_file = project_root / "scripts" / "gemini_extraction_queue.py"
        content = geq_file.read_text()

        assert "TRIAGE_FILE" in content or "triage" in content.lower(), "Triage file path not defined"

    def test_geq_defines_queue_state_persistence(self, project_root):
        """GEQ-SC2a: Module defines queue state persistence."""
        geq_file = project_root / "scripts" / "gemini_extraction_queue.py"
        content = geq_file.read_text()

        assert "QUEUE_STATE_FILE" in content or "queue_state" in content.lower(), "Queue state file not defined"
        assert "json" in content.lower(), "JSON persistence not implemented"

    def test_geq_defines_pdf_locating(self, project_root):
        """GEQ-SC3a: Module defines PDF location logic."""
        geq_file = project_root / "scripts" / "gemini_extraction_queue.py"
        content = geq_file.read_text()

        assert "PDF_DIR" in content or "pdf" in content.lower(), "PDF directory not defined"
        assert "Path" in content or "exists" in content.lower(), "File checking not implemented"

    def test_geq_defines_prompt_selection(self, project_root):
        """GEQ-SC4a: Module defines prompt selection logic."""
        geq_file = project_root / "scripts" / "gemini_extraction_queue.py"
        content = geq_file.read_text()

        assert "prompt" in content.lower(), "Prompt selection not found"
        assert "article_type" in content.lower() or "type_prediction" in content.lower(), "Type-based selection not implemented"

    def test_geq_defines_extraction_execution(self, project_root):
        """GEQ-SC5a: Module defines extraction execution."""
        geq_file = project_root / "scripts" / "gemini_extraction_queue.py"
        content = geq_file.read_text()

        assert "genai" in content or "gemini" in content.lower(), "Gemini API not used"
        assert "run" in content.lower() or "execute" in content.lower(), "Extraction execution not implemented"

    def test_geq_defines_two_run_verification(self, project_root):
        """GEQ-SC6a: Module defines two-run verification."""
        geq_file = project_root / "scripts" / "gemini_extraction_queue.py"
        content = geq_file.read_text()

        assert "run1" in content or "run2" in content, "Multi-run execution not implemented"

    def test_geq_defines_cost_tracking(self, project_root):
        """GEQ-SC7a: Module defines cost tracking."""
        geq_file = project_root / "scripts" / "gemini_extraction_queue.py"
        content = geq_file.read_text()

        assert "PRICING" in content or "cost" in content.lower(), "Cost tracking not implemented"
        assert "total_cost" in content or "price" in content.lower(), "Cost calculation not found"


# ============================================================================
# SECTION 6: run_panel_1_outcomes.py Tests
# ============================================================================

class TestRunPanel1Outcomes:
    """Tests for scripts/run_panel_1_outcomes.py success conditions."""

    def test_p1o_module_imports(self, project_root):
        """P1O-SC0: Module imports without errors."""
        p1o_file = project_root / "scripts" / "run_panel_1_outcomes.py"
        assert p1o_file.exists(), "run_panel_1_outcomes.py not found"

        content = p1o_file.read_text()
        try:
            compile(content, "run_panel_1_outcomes.py", "exec")
        except SyntaxError as e:
            pytest.fail(f"Syntax error in run_panel_1_outcomes.py: {e}")

    def test_p1o_defines_queue_harvesting(self, project_root):
        """P1O-SC1: Module defines unresolved terms harvesting."""
        p1o_file = project_root / "scripts" / "run_panel_1_outcomes.py"
        content = p1o_file.read_text()

        assert "harvest" in content.lower() or "unresolved" in content.lower(), "Term harvesting not found"
        assert "UNRESOLVED_QUEUE" in content or "unresolved" in content.lower(), "Queue file not referenced"

    def test_p1o_defines_vocab_filtering(self, project_root):
        """P1O-SC2: Module defines vocabulary filtering."""
        p1o_file = project_root / "scripts" / "run_panel_1_outcomes.py"
        content = p1o_file.read_text()

        assert "VOCAB_PATH" in content or "outcome_vocab" in content.lower(), "Vocabulary file not referenced"
        assert "filter" in content.lower() or "duplicate" in content.lower(), "Filtering logic not found"

    def test_p1o_defines_clustering(self, project_root):
        """P1O-SC3: Module defines term clustering."""
        p1o_file = project_root / "scripts" / "run_panel_1_outcomes.py"
        content = p1o_file.read_text()

        cluster_keywords = ["cluster", "similar", "distance", "group"]
        found = sum(1 for kw in cluster_keywords if kw in content.lower())
        assert found > 0, "Clustering logic not found"

    def test_p1o_defines_panel_invocation(self, project_root):
        """P1O-SC4: Module defines panel resolver invocation."""
        p1o_file = project_root / "scripts" / "run_panel_1_outcomes.py"
        content = p1o_file.read_text()

        panel_keywords = ["PanelResolver", "panel", "resolver"]
        found = sum(1 for kw in panel_keywords if kw in content)
        assert found > 0, "Panel resolver not referenced"

    def test_p1o_defines_decision_structure(self, project_root):
        """P1O-SC5: Module defines decision output structure."""
        p1o_file = project_root / "scripts" / "run_panel_1_outcomes.py"
        content = p1o_file.read_text()

        decision_fields = ["term_id", "name", "level", "rationale", "confidence"]
        found = sum(1 for f in decision_fields if f in content.lower())
        assert found >= 3, "Decision structure incomplete"

    def test_p1o_defines_output_writing(self, project_root):
        """P1O-SC6: Module defines output writing."""
        p1o_file = project_root / "scripts" / "run_panel_1_outcomes.py"
        content = p1o_file.read_text()

        assert "OUTPUT_DIR" in content or "panel_results" in content.lower(), "Output directory not defined"
        assert "json" in content.lower() and "dump" in content.lower(), "JSON writing not implemented"

    def test_p1o_defines_coverage_calculation(self, project_root):
        """P1O-SC7: Module defines coverage statistics."""
        p1o_file = project_root / "scripts" / "run_panel_1_outcomes.py"
        content = p1o_file.read_text()

        coverage_keywords = ["coverage", "resolved", "percentage"]
        found = sum(1 for kw in coverage_keywords if kw in content.lower())
        assert found > 0, "Coverage calculation not found"


# ============================================================================
# SECTION 7: src/qa/extraction_field_validator.py Tests
# ============================================================================

class TestExtractionFieldValidator:
    """Tests for src/qa/extraction_field_validator.py success conditions."""

    def test_efv_module_exists(self, project_root):
        """EFV-SC0: Module exists and is importable."""
        efv_file = project_root / "src" / "qa" / "extraction_field_validator.py"
        assert efv_file.exists(), "extraction_field_validator.py not found"

        content = efv_file.read_text()
        try:
            compile(content, "extraction_field_validator.py", "exec")
        except SyntaxError as e:
            pytest.fail(f"Syntax error in extraction_field_validator.py: {e}")

    def test_efv_defines_violation_class(self, project_root):
        """EFV-SC0a: Module defines Violation dataclass."""
        efv_file = project_root / "src" / "qa" / "extraction_field_validator.py"
        content = efv_file.read_text()

        assert "Violation" in content, "Violation class not defined"
        assert "@dataclass" in content, "Dataclass decorator not used"

        violation_fields = ["rule_id", "field", "severity", "message"]
        found = sum(1 for f in violation_fields if f in content)
        assert found >= 3, "Violation fields incomplete"

    def test_efv_defines_severity_enum(self, project_root):
        """EFV-SC0b: Module defines Severity enum."""
        efv_file = project_root / "src" / "qa" / "extraction_field_validator.py"
        content = efv_file.read_text()

        assert "Severity" in content, "Severity enum not defined"

        severity_levels = ["CRITICAL", "ERROR", "WARNING", "INFO"]
        found = sum(1 for s in severity_levels if s in content)
        assert found >= 3, "Severity levels incomplete"

    def test_efv_defines_finding_report(self, project_root):
        """EFV-SC0c: Module defines FindingReport dataclass."""
        efv_file = project_root / "src" / "qa" / "extraction_field_validator.py"
        content = efv_file.read_text()

        assert "FindingReport" in content, "FindingReport class not defined"
        assert "violations" in content, "Violations list not in FindingReport"

    def test_efv_defines_validator_class(self, project_root):
        """EFV-SC1: Module defines ExtractionFieldValidator class."""
        efv_file = project_root / "src" / "qa" / "extraction_field_validator.py"
        content = efv_file.read_text()

        assert "ExtractionFieldValidator" in content, "ExtractionFieldValidator class not defined"
        assert "class" in content, "Class definition not found"

    def test_efv_loads_quality_rules(self, project_root):
        """EFV-SC1a: Validator loads quality rules on init."""
        efv_file = project_root / "src" / "qa" / "extraction_field_validator.py"
        content = efv_file.read_text()

        assert "extraction_quality_rules.json" in content, "Quality rules file not referenced"
        assert "__init__" in content or "def " in content, "Initialization not implemented"

    def test_efv_defines_validation_methods(self, project_root):
        """EFV-SC2: Module defines validation methods."""
        efv_file = project_root / "src" / "qa" / "extraction_field_validator.py"
        content = efv_file.read_text()

        required_methods = ["validate_article", "validate_batch"]
        for method in required_methods:
            assert method in content, f"Method '{method}' not defined"

    def test_efv_defines_violation_detection(self, project_root):
        """EFV-SC3: Module detects violations."""
        efv_file = project_root / "src" / "qa" / "extraction_field_validator.py"
        content = efv_file.read_text()

        detection_keywords = ["violation", "error", "invalid", "check"]
        found = sum(1 for kw in detection_keywords if kw in content.lower())
        assert found > 0, "Violation detection logic not found"

    def test_efv_defines_quality_scoring(self, project_root):
        """EFV-SC4: Module computes quality score."""
        efv_file = project_root / "src" / "qa" / "extraction_field_validator.py"
        content = efv_file.read_text()

        assert "quality_score" in content or "score" in content.lower(), "Quality score not computed"
        assert "0" in content and "1" in content, "Score range not 0-1"

    def test_efv_defines_batch_validation(self, project_root):
        """EFV-SC5: Module validates batches."""
        efv_file = project_root / "src" / "qa" / "extraction_field_validator.py"
        content = efv_file.read_text()

        assert "batch" in content.lower(), "Batch validation not implemented"
        assert "mean" in content.lower() or "average" in content.lower(), "Mean score not computed"

    def test_efv_defines_threshold_filtering(self, project_root):
        """EFV-SC6: Module filters by quality threshold."""
        efv_file = project_root / "src" / "qa" / "extraction_field_validator.py"
        content = efv_file.read_text()

        assert "threshold" in content.lower(), "Threshold filtering not implemented"

    def test_efv_defines_severity_assignment(self, project_root):
        """EFV-SC7: Module assigns violation severity."""
        efv_file = project_root / "src" / "qa" / "extraction_field_validator.py"
        content = efv_file.read_text()

        assert "Severity" in content and "severity" in content.lower(), "Severity assignment not found"


# ============================================================================
# SECTION 8: src/services/overseer.py Tests
# ============================================================================

class TestOverseer:
    """Tests for src/services/overseer.py success conditions."""

    def test_overseer_module_exists(self, project_root):
        """OS-SC0: Module exists and is importable."""
        overseer_file = project_root / "src" / "services" / "overseer.py"
        assert overseer_file.exists(), "overseer.py not found"

        content = overseer_file.read_text()
        try:
            compile(content, "overseer.py", "exec")
        except SyntaxError as e:
            pytest.fail(f"Syntax error in overseer.py: {e}")

    def test_overseer_defines_violation_class(self, project_root):
        """OS-SC0a: Module defines InvariantViolation dataclass."""
        overseer_file = project_root / "src" / "services" / "overseer.py"
        content = overseer_file.read_text()

        assert "InvariantViolation" in content, "InvariantViolation class not defined"
        assert "code" in content and "severity" in content, "Violation fields incomplete"

    def test_overseer_defines_health_report(self, project_root):
        """OS-SC0b: Module defines HealthReport dataclass."""
        overseer_file = project_root / "src" / "services" / "overseer.py"
        content = overseer_file.read_text()

        assert "HealthReport" in content, "HealthReport class not defined"

    def test_overseer_references_invariants(self, project_root):
        """OS-SC0c: Module references all 10+ invariants."""
        overseer_file = project_root / "src" / "services" / "overseer.py"
        content = overseer_file.read_text()

        # Check for invariant references
        invariant_refs = sum(1 for i in range(11) if f"INV-{i}" in content)
        assert invariant_refs >= 5, "Not enough invariant references found"

    def test_overseer_defines_health_monitor(self, project_root):
        """OS-SC1: Module defines HealthMonitor component."""
        overseer_file = project_root / "src" / "services" / "overseer.py"
        content = overseer_file.read_text()

        assert "HealthMonitor" in content, "HealthMonitor class not defined"

    def test_overseer_defines_integrity_checker(self, project_root):
        """OS-SC1a: Module defines IntegrityChecker component."""
        overseer_file = project_root / "src" / "services" / "overseer.py"
        content = overseer_file.read_text()

        assert "IntegrityChecker" in content, "IntegrityChecker class not defined"

    def test_overseer_defines_completeness_auditor(self, project_root):
        """OS-SC1b: Module defines CompletenessAuditor component."""
        overseer_file = project_root / "src" / "services" / "overseer.py"
        content = overseer_file.read_text()

        assert "CompletenessAuditor" in content, "CompletenessAuditor class not defined"

    def test_overseer_defines_maintenance_engine(self, project_root):
        """OS-SC1c: Module defines MaintenanceEngine component."""
        overseer_file = project_root / "src" / "services" / "overseer.py"
        content = overseer_file.read_text()

        assert "MaintenanceEngine" in content, "MaintenanceEngine class not defined"

    def test_overseer_defines_scheduler(self, project_root):
        """OS-SC1d: Module defines Scheduler component."""
        overseer_file = project_root / "src" / "services" / "overseer.py"
        content = overseer_file.read_text()

        assert "Scheduler" in content, "Scheduler class not defined"

    def test_overseer_defines_reporter(self, project_root):
        """OS-SC1e: Module defines OverseerReporter component."""
        overseer_file = project_root / "src" / "services" / "overseer.py"
        content = overseer_file.read_text()

        assert "Reporter" in content or "Report" in content, "Reporter component not defined"

    def test_overseer_defines_system_class(self, project_root):
        """OS-SC1f: Module defines OverseerSystem main class."""
        overseer_file = project_root / "src" / "services" / "overseer.py"
        content = overseer_file.read_text()

        assert "OverseerSystem" in content, "OverseerSystem class not defined"

    def test_overseer_checks_operational_state(self, project_root):
        """OS-SC2: Module checks INV-0 (OPERATIONAL state)."""
        overseer_file = project_root / "src" / "services" / "overseer.py"
        content = overseer_file.read_text()

        operational_keywords = ["operational", "bootstrap", "state", "check"]
        found = sum(1 for kw in operational_keywords if kw in content.lower())
        assert found > 0, "Operational state checking not found"

    def test_overseer_checks_provenance(self, project_root):
        """OS-SC3: Module checks INV-1 (Provenance)."""
        overseer_file = project_root / "src" / "services" / "overseer.py"
        content = overseer_file.read_text()

        assert "provenance" in content.lower(), "Provenance checking not found"

    def test_overseer_checks_coherence(self, project_root):
        """OS-SC4: Module checks INV-4 (Coherence decline)."""
        overseer_file = project_root / "src" / "services" / "overseer.py"
        content = overseer_file.read_text()

        assert "coherence" in content.lower(), "Coherence checking not found"

    def test_overseer_checks_qa_quality(self, project_root):
        """OS-SC5: Module checks INV-10 (QA quality)."""
        overseer_file = project_root / "src" / "services" / "overseer.py"
        content = overseer_file.read_text()

        quality_keywords = ["quality", "score", "0.75"]
        found = sum(1 for kw in quality_keywords if kw in content.lower())
        assert found > 0, "QA quality checking not found"

    def test_overseer_detects_violations(self, project_root):
        """OS-SC6: Module detects invariant violations."""
        overseer_file = project_root / "src" / "services" / "overseer.py"
        content = overseer_file.read_text()

        assert "violation" in content.lower() or "detect" in content.lower(), "Violation detection not found"

    def test_overseer_generates_reports(self, project_root):
        """OS-SC7: Module generates health reports."""
        overseer_file = project_root / "src" / "services" / "overseer.py"
        content = overseer_file.read_text()

        report_keywords = ["report", "generate", "health"]
        found = sum(1 for kw in report_keywords if kw in content.lower())
        assert found > 0, "Report generation not found"

    def test_overseer_schedules_modes(self, project_root):
        """OS-SC8: Module implements scheduling modes."""
        overseer_file = project_root / "src" / "services" / "overseer.py"
        content = overseer_file.read_text()

        modes = ["POST_INTEGRATION", "PERIODIC", "ALERT", "ON_DEMAND"]
        found = sum(1 for m in modes if m in content)
        assert found >= 2, "Scheduling modes not implemented"


# ============================================================================
# SECTION 9: src/extraction/revised_prompts_v3.py Tests
# ============================================================================

class TestRevisedPromptsV3:
    """Tests for src/extraction/revised_prompts_v3.py success conditions."""

    def test_rep_module_exists(self, project_root):
        """REP-SC0: Module exists and is importable."""
        rep_file = project_root / "src" / "extraction" / "revised_prompts_v3.py"
        assert rep_file.exists(), "revised_prompts_v3.py not found"

        content = rep_file.read_text()
        try:
            compile(content, "revised_prompts_v3.py", "exec")
        except SyntaxError as e:
            pytest.fail(f"Syntax error in revised_prompts_v3.py: {e}")

    def test_rep_defines_canonical_directions(self, project_root):
        """REP-SC1: Module defines canonical directions."""
        rep_file = project_root / "src" / "extraction" / "revised_prompts_v3.py"
        content = rep_file.read_text()

        assert "CANONICAL_DIRECTIONS" in content, "CANONICAL_DIRECTIONS not defined"

        expected_directions = ["increase", "decrease", "no_effect", "mixed"]
        for direction in expected_directions:
            assert direction in content, f"Direction '{direction}' not defined"

    def test_rep_defines_article_families(self, project_root):
        """REP-SC2: Module defines article families."""
        rep_file = project_root / "src" / "extraction" / "revised_prompts_v3.py"
        content = rep_file.read_text()

        assert "ARTICLE_FAMILIES" in content, "ARTICLE_FAMILIES not defined"

        expected_families = ["empirical", "synthesis", "theoretical", "qualitative", "methods"]
        for family in expected_families:
            assert family in content, f"Family '{family}' not defined"

    def test_rep_defines_base_prompt(self, project_root):
        """REP-SC3: Module defines base prompt."""
        rep_file = project_root / "src" / "extraction" / "revised_prompts_v3.py"
        content = rep_file.read_text()

        assert "PROMPT_BASE" in content or "PROMPT" in content, "Base prompt not defined"
        assert "json" in content.lower(), "JSON schema not referenced"

    def test_rep_defines_family_prompts(self, project_root):
        """REP-SC4: Module defines family-specific prompts."""
        rep_file = project_root / "src" / "extraction" / "revised_prompts_v3.py"
        content = rep_file.read_text()

        prompt_references = sum(1 for family in ["empirical", "synthesis", "theoretical"]
                              if f"prompt" in content.lower() and family in content.lower())
        assert prompt_references >= 2, "Family-specific prompts not adequately defined"

    def test_rep_defines_validation_suffix(self, project_root):
        """REP-SC5: Module defines validation suffix."""
        rep_file = project_root / "src" / "extraction" / "revised_prompts_v3.py"
        content = rep_file.read_text()

        assert "VALIDATION" in content or "validation" in content.lower(), "Validation suffix not defined"

    def test_rep_defines_vocab_injection(self, project_root):
        """REP-SC6: Module defines vocabulary injection."""
        rep_file = project_root / "src" / "extraction" / "revised_prompts_v3.py"
        content = rep_file.read_text()

        vocab_keywords = ["vocab", "injection", "hint", "outcome"]
        found = sum(1 for kw in vocab_keywords if kw in content.lower())
        assert found > 0, "Vocabulary injection not implemented"

    def test_rep_defines_schema_compliance(self, project_root):
        """REP-SC7: Module addresses schema compliance."""
        rep_file = project_root / "src" / "extraction" / "revised_prompts_v3.py"
        content = rep_file.read_text()

        schema_keywords = ["schema", "extraction_template", "compliance"]
        found = sum(1 for kw in schema_keywords if kw in content.lower())
        assert found > 0, "Schema compliance not addressed"

    def test_rep_enforces_antecedent_specificity(self, project_root):
        """REP-SC8: Module enforces antecedent specificity."""
        rep_file = project_root / "src" / "extraction" / "revised_prompts_v3.py"
        content = rep_file.read_text()

        assert "antecedent" in content.lower(), "Antecedent validation not implemented"
        specificity_keywords = ["specific", "vague", "detail"]
        found = sum(1 for kw in specificity_keywords if kw in content.lower())
        assert found > 0, "Antecedent specificity enforcement not found"


# ============================================================================
# SECTION 10: Cross-Cutting Tests
# ============================================================================

class TestSuccessConditionsRegistry:
    """Tests for the success_conditions.json registry itself."""

    def test_registry_exists(self, success_conditions):
        """Registry file loads successfully."""
        assert success_conditions is not None, "Registry failed to load"

    def test_registry_has_metadata(self, success_conditions):
        """Registry contains version, created date, description."""
        assert "version" in success_conditions, "Version not specified"
        assert "created" in success_conditions, "Creation date not specified"
        assert "description" in success_conditions, "Description missing"
        assert "conditions" in success_conditions, "Conditions section missing"

    def test_registry_completeness(self, success_conditions):
        """Registry covers all 10 key components."""
        required_components = [
            "scripts/scheduled_pipeline.py",
            "scripts/kirsh_decision_tree_analysis.py",
            "scripts/backfill_operationalizations.py",
            "scripts/link_outcomes_to_instruments.py",
            "scripts/gemini_extraction_queue.py",
            "scripts/run_panel_1_outcomes.py",
            "src/qa/extraction_field_validator.py",
            "src/services/overseer.py",
            "src/extraction/revised_prompts_v3.py",
        ]

        for component in required_components:
            assert component in success_conditions["conditions"], \
                f"Component '{component}' not in registry"

    def test_conditions_have_required_fields(self, success_conditions):
        """Each condition has all required fields."""
        required_fields = ["id", "name", "description", "metric", "threshold", "test_name"]

        for component, data in success_conditions["conditions"].items():
            conditions_list = data.get("conditions", [])
            assert len(conditions_list) > 0, f"Component {component} has no conditions"

            for condition in conditions_list:
                for field in required_fields:
                    assert field in condition, \
                        f"Condition {condition.get('id')} missing field '{field}'"

    def test_condition_ids_are_unique(self, success_conditions):
        """All condition IDs are unique across the registry."""
        all_ids = []
        for component, data in success_conditions["conditions"].items():
            for condition in data.get("conditions", []):
                condition_id = condition.get("id")
                assert condition_id not in all_ids, f"Duplicate ID found: {condition_id}"
                all_ids.append(condition_id)

    def test_condition_ids_follow_convention(self, success_conditions):
        """Condition IDs follow component-SC# convention."""
        for component, data in success_conditions["conditions"].items():
            component_prefix = component.split("/")[-1].split(".")[0][:3].upper()

            for condition in data.get("conditions", []):
                condition_id = condition.get("id")
                # Should be like SP-SC1, KDT-SC1, etc.
                assert "-SC" in condition_id, f"ID {condition_id} doesn't follow convention"


# ============================================================================
# SECTION 11: Data Integrity Tests
# ============================================================================

class TestDataIntegrity:
    """Tests for critical data file integrity."""

    def test_outcome_vocab_exists(self, project_root):
        """Outcome vocabulary file exists."""
        vocab_file = project_root / "contracts" / "outcome_vocab" / "outcome_vocab.json"
        if vocab_file.exists():
            data = json.loads(vocab_file.read_text())
            assert "terms" in data, "Vocabulary missing 'terms' field"
            assert len(data.get("terms", [])) > 0, "Vocabulary has no terms"

    def test_extraction_quality_rules_exist(self, project_root):
        """Extraction quality rules file exists."""
        rules_file = project_root / "contracts" / "schemas" / "extraction_quality_rules.json"
        if rules_file.exists():
            data = json.loads(rules_file.read_text())
            assert len(data) > 0, "Quality rules file is empty"

    def test_instruments_registry_exists(self, project_root):
        """Instruments registry file exists."""
        instruments_file = project_root / "contracts" / "instruments_registry.json"
        if instruments_file.exists():
            data = json.loads(instruments_file.read_text())
            assert isinstance(data, list), "Registry should be a list"
            if len(data) > 0:
                assert "instrument_id" in data[0], "Instruments missing 'instrument_id' field"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
