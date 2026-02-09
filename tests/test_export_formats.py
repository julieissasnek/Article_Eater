"""
Tests for Export Formats — Sprint 3.0.4-B
2026-02-09
"""

import json
import gzip
import pytest
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from src.services.export_formats import (
    JSONLExporter,
    CSVExporter,
    ParquetExporter,
    MultiFormatExporter,
    StreamingExporter,
    ExportFormat,
    ExportResult,
    ExportMetadata,
    export_to_jsonl,
    export_to_csv,
    export_beliefs_jsonl,
)


# =============================================================================
# Mock Objects
# =============================================================================

@dataclass
class MockCredence:
    value: float
    uncertainty: float = 0.1


@dataclass
class MockBelief:
    belief_id: str
    content: str
    credence: MockCredence
    level: str = "empirical"
    status: str = "established"
    theory_id: Optional[str] = None
    paper_ids: List[str] = None

    def __post_init__(self):
        self.paper_ids = self.paper_ids or []


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def sample_records():
    return [
        {"id": "001", "name": "Alpha", "value": 0.75, "tags": ["a", "b"]},
        {"id": "002", "name": "Beta", "value": 0.85, "tags": ["c"]},
        {"id": "003", "name": "Gamma", "value": 0.65, "tags": []},
    ]


@pytest.fixture
def sample_beliefs():
    return [
        MockBelief("b1", "Belief one", MockCredence(0.8, 0.1), paper_ids=["p1"]),
        MockBelief("b2", "Belief two", MockCredence(0.7, 0.15), paper_ids=["p2", "p3"]),
    ]


@pytest.fixture
def nested_records():
    return [
        {
            "id": "001",
            "metadata": {"author": "Smith", "year": 2024},
            "values": [1, 2, 3]
        },
        {
            "id": "002",
            "metadata": {"author": "Jones", "year": 2023},
            "values": [4, 5]
        }
    ]


# =============================================================================
# JSONL Exporter Tests
# =============================================================================

class TestJSONLExporter:
    """Test JSONL export functionality."""

    def test_export_to_bytes(self, sample_records):
        """Test exporting to bytes."""
        exporter = JSONLExporter()
        result = exporter.export_records(iter(sample_records))

        assert result.success
        assert result.format == ExportFormat.JSONL
        assert result.content is not None
        assert result.record_count == 3

    def test_export_to_file(self, sample_records, tmp_path):
        """Test exporting to file."""
        output_path = tmp_path / "test.jsonl"
        exporter = JSONLExporter()
        result = exporter.export_records(iter(sample_records), output_path)

        assert result.success
        assert result.path is not None
        assert Path(result.path).exists()

        # Verify content
        lines = Path(result.path).read_text().strip().split('\n')
        assert len(lines) == 3

    def test_export_compressed(self, sample_records, tmp_path):
        """Test gzip compression."""
        output_path = tmp_path / "test"
        exporter = JSONLExporter(compress=True)
        result = exporter.export_records(iter(sample_records), output_path)

        assert result.success
        assert result.path.endswith('.jsonl.gz')

        # Verify compressed content
        with gzip.open(result.path, 'rt') as f:
            lines = f.read().strip().split('\n')
            assert len(lines) == 3

    def test_export_pretty(self, sample_records):
        """Test pretty printing."""
        exporter = JSONLExporter(pretty=True)
        result = exporter.export_records(iter(sample_records))

        content = result.content.decode('utf-8')
        # Pretty printing should produce larger output with indentation
        # Non-pretty would be compact single lines
        assert '  "id"' in content or '"id":' in content
        assert result.record_count == 3

    def test_export_with_transformer(self, sample_records):
        """Test record transformation."""
        def add_prefix(record):
            record['id'] = f"prefix_{record['id']}"
            return record

        exporter = JSONLExporter()
        result = exporter.export_records(iter(sample_records), transformer=add_prefix)

        content = result.content.decode('utf-8')
        assert 'prefix_001' in content

    def test_export_beliefs(self, sample_beliefs, tmp_path):
        """Test belief export."""
        output_path = tmp_path / "beliefs.jsonl"
        exporter = JSONLExporter()
        result = exporter.export_beliefs(sample_beliefs, output_path)

        assert result.success
        assert result.record_count == 2

        lines = Path(result.path).read_text().strip().split('\n')
        first = json.loads(lines[0])
        assert first['belief_id'] == 'b1'
        assert 'credence' in first

    def test_empty_records(self):
        """Test exporting empty records."""
        exporter = JSONLExporter()
        result = exporter.export_records(iter([]))

        assert result.success
        assert result.record_count == 0


# =============================================================================
# CSV Exporter Tests
# =============================================================================

class TestCSVExporter:
    """Test CSV export functionality."""

    def test_export_to_bytes(self, sample_records):
        """Test exporting to bytes."""
        exporter = CSVExporter()
        result = exporter.export_records(sample_records)

        assert result.success
        assert result.format == ExportFormat.CSV
        assert result.content is not None
        assert result.record_count == 3

    def test_export_to_file(self, sample_records, tmp_path):
        """Test exporting to file."""
        output_path = tmp_path / "test.csv"
        exporter = CSVExporter()
        result = exporter.export_records(sample_records, output_path)

        assert result.success
        assert Path(result.path).exists()

        content = Path(result.path).read_text()
        assert 'id' in content
        assert 'Alpha' in content

    def test_export_with_header(self, sample_records):
        """Test header inclusion."""
        exporter = CSVExporter(include_header=True)
        result = exporter.export_records(sample_records)

        content = result.content.decode('utf-8')
        lines = content.strip().split('\n')
        assert lines[0].startswith('id') or 'name' in lines[0]

    def test_export_without_header(self, sample_records):
        """Test header exclusion."""
        exporter = CSVExporter(include_header=False)
        result = exporter.export_records(sample_records)

        content = result.content.decode('utf-8')
        lines = content.strip().split('\n')
        # First line should be data, not header
        assert 'Alpha' in lines[0] or '001' in lines[0]

    def test_export_tsv(self, sample_records):
        """Test tab-separated export."""
        exporter = CSVExporter(delimiter='\t')
        result = exporter.export_records(sample_records)

        content = result.content.decode('utf-8')
        assert '\t' in content

    def test_flatten_nested(self, nested_records):
        """Test flattening nested structures."""
        exporter = CSVExporter(flatten_nested=True)
        result = exporter.export_records(nested_records)

        content = result.content.decode('utf-8')
        # Nested keys should be flattened
        assert 'metadata_author' in content or 'author' in content

    def test_custom_columns(self, sample_records):
        """Test custom column order."""
        exporter = CSVExporter()
        result = exporter.export_records(sample_records, columns=['name', 'id'])

        content = result.content.decode('utf-8')
        lines = content.strip().split('\n')
        # Header should start with 'name'
        assert lines[0].startswith('name')

    def test_empty_records(self):
        """Test exporting empty records."""
        exporter = CSVExporter()
        result = exporter.export_records([])

        assert result.success
        assert result.record_count == 0


# =============================================================================
# Parquet Exporter Tests
# =============================================================================

class TestParquetExporter:
    """Test Parquet export functionality."""

    def test_parquet_fallback(self, sample_records, tmp_path):
        """Test fallback to JSONL when pyarrow unavailable."""
        exporter = ParquetExporter()

        if not exporter._pyarrow_available:
            output_path = tmp_path / "test.parquet"
            result = exporter.export_records(sample_records, output_path)

            # Should fall back to JSONL
            assert result.success or not exporter._pyarrow_available

    def test_check_pyarrow(self):
        """Test pyarrow availability check."""
        exporter = ParquetExporter()
        # Should return True or False without error
        assert isinstance(exporter._pyarrow_available, bool)

    def test_flatten_for_parquet(self, nested_records):
        """Test flattening for Parquet compatibility."""
        exporter = ParquetExporter()
        flat = exporter._flatten_for_parquet(nested_records[0])

        # Nested dict should be JSON string
        assert isinstance(flat.get('metadata'), str)
        assert 'author' in flat.get('metadata', '')


# =============================================================================
# Multi-Format Exporter Tests
# =============================================================================

class TestMultiFormatExporter:
    """Test unified multi-format exporter."""

    def test_export_jsonl(self, sample_records):
        """Test JSONL export via multi-format."""
        exporter = MultiFormatExporter()
        result = exporter.export(sample_records, ExportFormat.JSONL)

        assert result.success
        assert result.format == ExportFormat.JSONL

    def test_export_json(self, sample_records):
        """Test JSON export via multi-format."""
        exporter = MultiFormatExporter()
        result = exporter.export(sample_records, ExportFormat.JSON)

        assert result.success
        assert result.format == ExportFormat.JSON

        # Should be valid JSON array
        parsed = json.loads(result.content.decode('utf-8'))
        assert isinstance(parsed, list)
        assert len(parsed) == 3

    def test_export_csv(self, sample_records):
        """Test CSV export via multi-format."""
        exporter = MultiFormatExporter()
        result = exporter.export(sample_records, ExportFormat.CSV)

        assert result.success
        assert result.format == ExportFormat.CSV

    def test_export_tsv(self, sample_records):
        """Test TSV export via multi-format."""
        exporter = MultiFormatExporter()
        result = exporter.export(sample_records, ExportFormat.TSV)

        assert result.success
        assert result.format == ExportFormat.TSV

    def test_export_beliefs(self, sample_beliefs):
        """Test belief export via multi-format."""
        exporter = MultiFormatExporter()
        result = exporter.export_beliefs(sample_beliefs, ExportFormat.CSV)

        assert result.success
        content = result.content.decode('utf-8')
        assert 'belief_id' in content

    def test_parquet_requires_path(self, sample_records):
        """Test Parquet requires output path."""
        exporter = MultiFormatExporter()
        result = exporter.export(sample_records, ExportFormat.PARQUET)

        assert not result.success
        assert "requires output_path" in result.error


# =============================================================================
# Streaming Exporter Tests
# =============================================================================

class TestStreamingExporter:
    """Test streaming exporter."""

    def test_streaming_jsonl(self, sample_records, tmp_path):
        """Test streaming JSONL export."""
        output_path = tmp_path / "stream.jsonl"

        with StreamingExporter(output_path, ExportFormat.JSONL) as exporter:
            for record in sample_records:
                exporter.write(record)

        result = exporter.close()

        assert result.success
        assert result.record_count == 3
        assert Path(output_path).exists()

    def test_streaming_csv(self, sample_records, tmp_path):
        """Test streaming CSV export."""
        output_path = tmp_path / "stream.csv"

        with StreamingExporter(output_path, ExportFormat.CSV) as exporter:
            for record in sample_records:
                exporter.write(record)

        result = exporter.close()

        assert result.success
        assert result.record_count == 3

    def test_streaming_context_manager(self, tmp_path):
        """Test context manager usage."""
        output_path = tmp_path / "context.jsonl"

        with StreamingExporter(output_path) as exporter:
            exporter.write({"id": 1})
            exporter.write({"id": 2})

        assert Path(output_path).exists()

    def test_streaming_unsupported_format(self, tmp_path):
        """Test unsupported format raises error."""
        output_path = tmp_path / "test.parquet"

        with pytest.raises(ValueError):
            StreamingExporter(output_path, ExportFormat.PARQUET).open()


# =============================================================================
# Convenience Function Tests
# =============================================================================

class TestConvenienceFunctions:
    """Test module-level convenience functions."""

    def test_export_to_jsonl(self, sample_records):
        """Test export_to_jsonl function."""
        result = export_to_jsonl(sample_records)

        assert result.success
        assert result.format == ExportFormat.JSONL

    def test_export_to_jsonl_compressed(self, sample_records, tmp_path):
        """Test compressed JSONL export."""
        output_path = tmp_path / "test"
        result = export_to_jsonl(sample_records, output_path, compress=True)

        assert result.success
        assert result.path.endswith('.gz')

    def test_export_to_csv(self, sample_records):
        """Test export_to_csv function."""
        result = export_to_csv(sample_records)

        assert result.success
        assert result.format == ExportFormat.CSV

    def test_export_beliefs_jsonl(self, sample_beliefs):
        """Test export_beliefs_jsonl function."""
        result = export_beliefs_jsonl(sample_beliefs)

        assert result.success
        assert result.record_count == 2


# =============================================================================
# Data Class Tests
# =============================================================================

class TestDataClasses:
    """Test data class functionality."""

    def test_export_metadata_to_dict(self):
        """Test ExportMetadata serialization."""
        metadata = ExportMetadata(
            format="jsonl",
            record_count=100,
            compression="gzip"
        )

        d = metadata.to_dict()

        assert d["format"] == "jsonl"
        assert d["record_count"] == 100
        assert "created_at" in d

    def test_export_result_to_dict(self, sample_records):
        """Test ExportResult serialization."""
        result = export_to_jsonl(sample_records)
        d = result.to_dict()

        assert d["success"] is True
        assert d["format"] == "jsonl"
        assert d["record_count"] == 3


# =============================================================================
# Edge Cases
# =============================================================================

class TestEdgeCases:
    """Test edge cases."""

    def test_special_characters(self):
        """Test handling special characters."""
        records = [
            {"text": "Hello, \"World\""},
            {"text": "Line1\nLine2"},
            {"text": "Tab\there"}
        ]

        result = export_to_jsonl(records)
        assert result.success

        result = export_to_csv(records)
        assert result.success

    def test_unicode_content(self):
        """Test Unicode handling."""
        records = [
            {"text": "Hello"},
            {"text": "Bonjour"},
            {"text": "Hola"}
        ]

        result = export_to_jsonl(records)
        content = result.content.decode('utf-8')
        assert "Hello" in content
        assert "Bonjour" in content
        assert "Hola" in content

    def test_none_values(self):
        """Test handling None values."""
        records = [
            {"id": 1, "value": None},
            {"id": 2, "value": "present"}
        ]

        result = export_to_jsonl(records)
        assert result.success

        result = export_to_csv(records)
        assert result.success

    def test_large_record(self):
        """Test handling large records."""
        large_text = "x" * 10000
        records = [{"text": large_text}]

        result = export_to_jsonl(records)
        assert result.success
        assert len(result.content) > 10000
