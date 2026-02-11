"""
Tests for Batch Processing Script (MVP-2)
==========================================

Tests the batch paper processor and its components.
"""

import json
import pytest
import tempfile
from pathlib import Path
from datetime import datetime, timezone
from unittest.mock import Mock, patch, MagicMock

import sys
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.process_papers import (
    ProcessingConfig,
    ProcessingResult,
    BatchProgress,
    BatchProcessor,
)


@pytest.fixture
def temp_dirs():
    """Create temporary directories for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        bundles_dir = tmpdir / "bundles"
        bundles_dir.mkdir()
        output_dir = tmpdir / "output"
        output_dir.mkdir()
        yield {
            'root': tmpdir,
            'bundles': bundles_dir,
            'output': output_dir
        }


@pytest.fixture
def sample_bundle(temp_dirs):
    """Create a sample job bundle."""
    bundle_path = temp_dirs['bundles'] / "job_test_paper_001"
    bundle_path.mkdir()

    # Create paper.json
    paper_meta = {
        "schema": "ae.paper.v1",
        "paper_id": "test_paper_001",
        "doi": "10.1234/test.001",
        "title": "Test Paper on Natural Light",
        "authors": [{"name": "Smith, J."}],
        "year": 2024,
        "venue": "Journal of Testing",
        "source": {
            "finder_run_id": "test_run",
            "ingest_method": "test",
            "retrieved_at": "2026-02-11T12:00:00Z"
        },
        "triage": {
            "score": 0.9,
            "decision": "send_to_eater",
            "reasons": ["high relevance"],
            "facet_scores": {"natural_light": 0.9}
        },
        "files": {
            "pdf_sha256": "abc123",
            "pdf_bytes": 1000
        },
        "rights": {
            "license": "CC-BY-4.0",
            "allowed_storage": True
        },
        "notes": {
            "human_notes": "",
            "tags": []
        }
    }
    with open(bundle_path / "paper.json", 'w') as f:
        json.dump(paper_meta, f)

    # Create dummy PDF
    with open(bundle_path / "paper.pdf", 'wb') as f:
        f.write(b'%PDF-1.4 dummy content')

    return bundle_path


class TestProcessingConfig:
    """Test ProcessingConfig class."""

    def test_default_config(self):
        """Test default configuration values."""
        config = ProcessingConfig()
        assert config.profile == "standard"
        assert config.hitl == "auto"
        assert config.max_consecutive_failures == 3
        assert config.skip_already_processed is True

    def test_config_from_yaml(self, temp_dirs):
        """Test loading configuration from YAML."""
        try:
            import yaml
        except ImportError:
            pytest.skip("PyYAML not installed")

        yaml_content = """
bundles_dir: /path/to/bundles
profile: deep
hitl: off
limit: 50
max_consecutive_failures: 5
skip_already_processed: false
verbose: true
"""
        config_path = temp_dirs['root'] / "test_config.yaml"
        with open(config_path, 'w') as f:
            f.write(yaml_content)

        config = ProcessingConfig.from_yaml(config_path)

        assert str(config.bundles_dir) == "/path/to/bundles"
        assert config.profile == "deep"
        assert config.hitl == "off"
        assert config.limit == 50
        assert config.max_consecutive_failures == 5
        assert config.skip_already_processed is False
        assert config.verbose is True


class TestProcessingResult:
    """Test ProcessingResult dataclass."""

    def test_success_result(self):
        result = ProcessingResult(
            paper_id="paper_001",
            success=True,
            status="SUCCESS",
            beliefs_added=5,
            constraints_added=2,
            duration_seconds=10.5
        )
        assert result.success is True
        assert result.beliefs_added == 5
        assert result.error_message is None

    def test_failure_result(self):
        result = ProcessingResult(
            paper_id="paper_002",
            success=False,
            status="ERROR",
            error_message="PDF extraction failed"
        )
        assert result.success is False
        assert result.error_message == "PDF extraction failed"


class TestBatchProgress:
    """Test BatchProgress tracking."""

    def test_empty_progress(self):
        progress = BatchProgress()
        assert progress.processed == 0
        assert progress.succeeded == 0
        assert progress.failed == 0
        assert progress.consecutive_failures == 0

    def test_record_success(self):
        progress = BatchProgress()
        result = ProcessingResult(
            paper_id="paper_001",
            success=True,
            status="SUCCESS",
            beliefs_added=5,
            constraints_added=2
        )
        progress.record_success(result)

        assert progress.processed == 1
        assert progress.succeeded == 1
        assert progress.failed == 0
        assert progress.beliefs_total == 5
        assert progress.constraints_total == 2
        assert progress.consecutive_failures == 0

    def test_record_failure(self):
        progress = BatchProgress()
        result = ProcessingResult(
            paper_id="paper_001",
            success=False,
            status="ERROR"
        )
        progress.record_failure(result)

        assert progress.processed == 1
        assert progress.succeeded == 0
        assert progress.failed == 1
        assert progress.consecutive_failures == 1

    def test_consecutive_failures_reset(self):
        progress = BatchProgress()

        # Two failures
        for _ in range(2):
            progress.record_failure(ProcessingResult(
                paper_id="paper",
                success=False,
                status="ERROR"
            ))
        assert progress.consecutive_failures == 2

        # One success resets counter
        progress.record_success(ProcessingResult(
            paper_id="paper",
            success=True,
            status="SUCCESS"
        ))
        assert progress.consecutive_failures == 0

    def test_to_dict(self):
        progress = BatchProgress(total=10)
        progress.start_time = datetime.now(timezone.utc)
        progress.record_success(ProcessingResult(
            paper_id="paper_001",
            success=True,
            status="SUCCESS",
            beliefs_added=5
        ))

        d = progress.to_dict()
        assert d['total'] == 10
        assert d['succeeded'] == 1
        assert d['beliefs_total'] == 5
        assert len(d['results']) == 1


class TestBatchProcessor:
    """Test BatchProcessor class."""

    def test_discover_bundles(self, temp_dirs, sample_bundle):
        """Test bundle discovery."""
        config = ProcessingConfig(bundles_dir=temp_dirs['bundles'])
        processor = BatchProcessor(config)

        bundles = processor.discover_bundles()

        assert len(bundles) == 1
        assert bundles[0] == sample_bundle

    def test_discover_bundles_with_limit(self, temp_dirs):
        """Test bundle discovery with limit."""
        # Create multiple bundles
        for i in range(5):
            bundle_path = temp_dirs['bundles'] / f"job_paper_{i:03d}"
            bundle_path.mkdir()
            with open(bundle_path / "paper.json", 'w') as f:
                json.dump({"paper_id": f"paper_{i:03d}", "title": f"Paper {i}"}, f)

        config = ProcessingConfig(
            bundles_dir=temp_dirs['bundles'],
            limit=3
        )
        processor = BatchProcessor(config)

        bundles = processor.discover_bundles()

        assert len(bundles) == 3

    def test_circuit_breaker(self, temp_dirs):
        """Test circuit breaker triggers after consecutive failures."""
        # Create 5 bundles
        for i in range(5):
            bundle_path = temp_dirs['bundles'] / f"job_paper_{i:03d}"
            bundle_path.mkdir()
            with open(bundle_path / "paper.json", 'w') as f:
                json.dump({
                    "paper_id": f"paper_{i:03d}",
                    "title": f"Paper {i}",
                    "year": 2024
                }, f)
            with open(bundle_path / "paper.pdf", 'wb') as f:
                f.write(b'%PDF dummy')

        config = ProcessingConfig(
            bundles_dir=temp_dirs['bundles'],
            max_consecutive_failures=3,
            pause_on_circuit_break=True,
            skip_already_processed=False
        )

        # Mock the pipeline to always fail
        with patch('scripts.process_papers.run_from_contract_bundle') as mock_pipeline:
            mock_pipeline.return_value = {
                'status': 'FAIL',
                'error': 'Test failure'
            }

            processor = BatchProcessor(config)
            progress = processor.run()

            # Should stop after 3 consecutive failures
            assert progress.processed == 3
            assert progress.failed == 3
            assert progress.consecutive_failures == 3

    @patch('scripts.process_papers.run_from_contract_bundle')
    @patch('scripts.process_papers.get_accumulator')
    def test_successful_processing(self, mock_get_acc, mock_pipeline, temp_dirs, sample_bundle):
        """Test successful paper processing."""
        # Setup mocks
        mock_accumulator = MagicMock()
        mock_accumulator.get_stats.return_value = MagicMock(papers_processed=[])
        mock_accumulator.integrate_web_state_file.return_value = {
            'status': 'success',
            'beliefs_added': 5,
            'constraints_added': 2
        }
        mock_get_acc.return_value = mock_accumulator

        mock_pipeline.return_value = {
            'status': 'SUCCESS',
            'paper_id': 'test_paper_001'
        }

        config = ProcessingConfig(
            bundles_dir=temp_dirs['bundles'],
            output_dir=temp_dirs['output'],
            skip_already_processed=False
        )

        processor = BatchProcessor(config, accumulator=mock_accumulator)

        # Create a mock web_state.json in expected output location
        expected_output = temp_dirs['output'] / sample_bundle.name
        expected_output.mkdir(parents=True, exist_ok=True)
        web_state = {"schema": "ae.web_state.v1", "beliefs": {}, "constraints": {}}
        with open(expected_output / "web_state.json", 'w') as f:
            json.dump(web_state, f)

        progress = processor.run()

        assert progress.processed == 1
        assert progress.succeeded == 1
        assert mock_pipeline.called


class TestMakeSafeId:
    """Test paper ID sanitization."""

    def test_make_safe_id(self, temp_dirs):
        config = ProcessingConfig(bundles_dir=temp_dirs['bundles'])
        processor = BatchProcessor(config)

        assert processor._make_safe_id("10.1234/test.001") == "10_1234_test_001"
        assert processor._make_safe_id("arxiv:2301.12345") == "arxiv_2301_12345"

        # Test truncation for very long IDs
        long_id = "a" * 100
        assert len(processor._make_safe_id(long_id)) == 50


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
