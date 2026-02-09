"""
Pipeline-Friendly Export Formats — Sprint 3.0.4-B
2026-02-09

Provides JSONL, Parquet, CSV, and other pipeline-friendly export formats.
Per Zaharia's recommendation for ML/data science workflows.
"""

from __future__ import annotations

import csv
import gzip
import io
import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, Iterator, List, Optional, Union

logger = logging.getLogger(__name__)


# =============================================================================
# Enums
# =============================================================================

class ExportFormat(Enum):
    """Supported export formats."""
    JSONL = "jsonl"
    JSON = "json"
    CSV = "csv"
    TSV = "tsv"
    PARQUET = "parquet"
    ARROW = "arrow"


class CompressionType(Enum):
    """Supported compression types."""
    NONE = "none"
    GZIP = "gzip"
    SNAPPY = "snappy"
    ZSTD = "zstd"


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class ExportMetadata:
    """Metadata for exported files."""
    format: str
    version: str = "1.0"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    source: str = "article_eater"
    record_count: int = 0
    schema_version: Optional[str] = None
    compression: Optional[str] = None
    checksum: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class ExportResult:
    """Result of an export operation."""
    success: bool
    format: ExportFormat
    path: Optional[str] = None
    content: Optional[bytes] = None
    record_count: int = 0
    metadata: Optional[ExportMetadata] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "format": self.format.value,
            "path": self.path,
            "record_count": self.record_count,
            "error": self.error
        }


# =============================================================================
# JSONL Exporter
# =============================================================================

class JSONLExporter:
    """
    JSONL (JSON Lines) exporter for streaming/pipeline use.

    Each line is a valid JSON object, suitable for:
    - Spark/Databricks ingestion
    - Unix pipeline tools (jq, grep, etc.)
    - Streaming processing
    """

    def __init__(
        self,
        compress: bool = False,
        pretty: bool = False,
        include_metadata: bool = True
    ):
        self.compress = compress
        self.pretty = pretty
        self.include_metadata = include_metadata

    def export_records(
        self,
        records: Iterator[Dict[str, Any]],
        output_path: Optional[Union[str, Path]] = None,
        transformer: Optional[Callable[[Dict], Dict]] = None
    ) -> ExportResult:
        """
        Export records to JSONL format.

        Args:
            records: Iterator of record dicts
            output_path: Optional file path (returns bytes if None)
            transformer: Optional function to transform each record

        Returns:
            ExportResult with success status and path/content
        """
        try:
            lines = []
            count = 0

            for record in records:
                if transformer:
                    record = transformer(record)

                if self.pretty:
                    line = json.dumps(record, indent=2, default=str)
                else:
                    line = json.dumps(record, separators=(',', ':'), default=str)

                lines.append(line)
                count += 1

            content = '\n'.join(lines)
            if lines:
                content += '\n'

            content_bytes = content.encode('utf-8')

            if self.compress:
                content_bytes = gzip.compress(content_bytes)

            metadata = ExportMetadata(
                format="jsonl",
                record_count=count,
                compression="gzip" if self.compress else None
            )

            if output_path:
                path = Path(output_path)
                suffix = ".jsonl.gz" if self.compress else ".jsonl"
                if not str(path).endswith(suffix):
                    path = path.with_suffix(suffix)

                path.write_bytes(content_bytes)

                return ExportResult(
                    success=True,
                    format=ExportFormat.JSONL,
                    path=str(path),
                    record_count=count,
                    metadata=metadata
                )
            else:
                return ExportResult(
                    success=True,
                    format=ExportFormat.JSONL,
                    content=content_bytes,
                    record_count=count,
                    metadata=metadata
                )

        except Exception as e:
            logger.error("JSONL export failed: %s", e)
            return ExportResult(
                success=False,
                format=ExportFormat.JSONL,
                error=str(e)
            )

    def export_beliefs(
        self,
        beliefs: List[Any],
        output_path: Optional[Union[str, Path]] = None,
        include_entrenchment: bool = True,
        web: Optional[Any] = None
    ) -> ExportResult:
        """Export beliefs to JSONL format."""
        def belief_to_dict(belief) -> Dict[str, Any]:
            d = {
                "belief_id": getattr(belief, 'belief_id', None),
                "content": getattr(belief, 'content', None),
                "level": getattr(belief, 'level', None),
                "status": getattr(belief, 'status', None),
                "theory_id": getattr(belief, 'theory_id', None),
                "paper_ids": getattr(belief, 'paper_ids', None)
            }

            # Handle level and status enums
            if hasattr(d.get('level'), 'value'):
                d['level'] = d['level'].value
            if hasattr(d.get('status'), 'value'):
                d['status'] = d['status'].value

            # Handle credence
            credence = getattr(belief, 'credence', None)
            if credence:
                d['credence'] = {
                    "value": getattr(credence, 'value', None),
                    "uncertainty": getattr(credence, 'uncertainty', None)
                }

            # Add entrenchment if requested
            if include_entrenchment and web:
                try:
                    ent = web.get_entrenchment(belief.belief_id)
                    d['entrenchment'] = ent
                except Exception:
                    pass

            return {k: v for k, v in d.items() if v is not None}

        records = (belief_to_dict(b) for b in beliefs)
        return self.export_records(records, output_path)


# =============================================================================
# CSV Exporter
# =============================================================================

class CSVExporter:
    """
    CSV exporter for spreadsheet and tabular use.

    Handles nested fields by flattening or JSON-encoding.
    """

    def __init__(
        self,
        delimiter: str = ',',
        include_header: bool = True,
        flatten_nested: bool = True,
        null_value: str = ''
    ):
        self.delimiter = delimiter
        self.include_header = include_header
        self.flatten_nested = flatten_nested
        self.null_value = null_value

    def export_records(
        self,
        records: List[Dict[str, Any]],
        output_path: Optional[Union[str, Path]] = None,
        columns: Optional[List[str]] = None
    ) -> ExportResult:
        """
        Export records to CSV format.

        Args:
            records: List of record dicts
            output_path: Optional file path
            columns: Optional column order (auto-detected if None)

        Returns:
            ExportResult
        """
        if not records:
            return ExportResult(
                success=True,
                format=ExportFormat.CSV,
                content=b'',
                record_count=0
            )

        try:
            # Flatten records
            flat_records = [self._flatten_record(r) for r in records]

            # Determine columns
            if columns is None:
                all_keys = set()
                for r in flat_records:
                    all_keys.update(r.keys())
                columns = sorted(all_keys)

            # Write CSV
            output = io.StringIO()
            writer = csv.DictWriter(
                output,
                fieldnames=columns,
                delimiter=self.delimiter,
                extrasaction='ignore'
            )

            if self.include_header:
                writer.writeheader()

            for record in flat_records:
                # Replace None with null_value
                row = {k: (v if v is not None else self.null_value) for k, v in record.items()}
                writer.writerow(row)

            content = output.getvalue().encode('utf-8')

            metadata = ExportMetadata(
                format="csv",
                record_count=len(flat_records)
            )

            if output_path:
                path = Path(output_path)
                path.write_bytes(content)

                return ExportResult(
                    success=True,
                    format=ExportFormat.CSV,
                    path=str(path),
                    record_count=len(flat_records),
                    metadata=metadata
                )
            else:
                return ExportResult(
                    success=True,
                    format=ExportFormat.CSV,
                    content=content,
                    record_count=len(flat_records),
                    metadata=metadata
                )

        except Exception as e:
            logger.error("CSV export failed: %s", e)
            return ExportResult(
                success=False,
                format=ExportFormat.CSV,
                error=str(e)
            )

    def _flatten_record(self, record: Dict[str, Any], prefix: str = '') -> Dict[str, Any]:
        """Flatten nested dict structure."""
        flat = {}

        for key, value in record.items():
            full_key = f"{prefix}{key}" if prefix else key

            if isinstance(value, dict) and self.flatten_nested:
                flat.update(self._flatten_record(value, f"{full_key}_"))
            elif isinstance(value, list):
                # JSON-encode lists
                flat[full_key] = json.dumps(value, default=str)
            elif hasattr(value, 'value'):
                # Handle enums
                flat[full_key] = value.value
            else:
                flat[full_key] = value

        return flat


# =============================================================================
# Parquet Exporter (Stub - requires pyarrow)
# =============================================================================

class ParquetExporter:
    """
    Parquet exporter for columnar analytics.

    Requires pyarrow. Falls back to JSONL if unavailable.
    """

    def __init__(
        self,
        compression: str = 'snappy',
        row_group_size: int = 10000
    ):
        self.compression = compression
        self.row_group_size = row_group_size
        self._pyarrow_available = self._check_pyarrow()

    def _check_pyarrow(self) -> bool:
        """Check if pyarrow is available."""
        try:
            import pyarrow  # noqa: F401
            return True
        except ImportError:
            return False

    def export_records(
        self,
        records: List[Dict[str, Any]],
        output_path: Union[str, Path],
        schema: Optional[Any] = None
    ) -> ExportResult:
        """
        Export records to Parquet format.

        Falls back to JSONL if pyarrow unavailable.
        """
        if not self._pyarrow_available:
            logger.warning("pyarrow not available, falling back to JSONL")
            jsonl = JSONLExporter()
            result = jsonl.export_records(iter(records), output_path)
            result.format = ExportFormat.JSONL
            return result

        try:
            import pyarrow as pa
            import pyarrow.parquet as pq

            # Convert records to table
            if not records:
                return ExportResult(
                    success=True,
                    format=ExportFormat.PARQUET,
                    path=str(output_path),
                    record_count=0
                )

            # Flatten records for Parquet
            flat_records = []
            for record in records:
                flat = self._flatten_for_parquet(record)
                flat_records.append(flat)

            # Infer schema from first record
            table = pa.Table.from_pylist(flat_records)

            # Write Parquet
            path = Path(output_path)
            pq.write_table(
                table,
                path,
                compression=self.compression,
                row_group_size=self.row_group_size
            )

            metadata = ExportMetadata(
                format="parquet",
                record_count=len(records),
                compression=self.compression
            )

            return ExportResult(
                success=True,
                format=ExportFormat.PARQUET,
                path=str(path),
                record_count=len(records),
                metadata=metadata
            )

        except Exception as e:
            logger.error("Parquet export failed: %s", e)
            return ExportResult(
                success=False,
                format=ExportFormat.PARQUET,
                error=str(e)
            )

    def _flatten_for_parquet(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Flatten and convert types for Parquet compatibility."""
        flat = {}

        for key, value in record.items():
            if isinstance(value, dict):
                # JSON-encode nested dicts
                flat[key] = json.dumps(value, default=str)
            elif isinstance(value, list):
                # JSON-encode lists
                flat[key] = json.dumps(value, default=str)
            elif hasattr(value, 'value'):
                flat[key] = value.value
            else:
                flat[key] = value

        return flat


# =============================================================================
# Multi-Format Exporter
# =============================================================================

class MultiFormatExporter:
    """
    Unified exporter supporting multiple formats.

    Provides consistent interface for all export formats.
    """

    def __init__(self):
        self.jsonl = JSONLExporter()
        self.csv = CSVExporter()
        self.parquet = ParquetExporter()

    def export(
        self,
        records: List[Dict[str, Any]],
        format: ExportFormat,
        output_path: Optional[Union[str, Path]] = None,
        **kwargs
    ) -> ExportResult:
        """
        Export records in the specified format.

        Args:
            records: List of record dicts
            format: Export format
            output_path: Optional output path
            **kwargs: Format-specific options

        Returns:
            ExportResult
        """
        if format == ExportFormat.JSONL:
            return self.jsonl.export_records(iter(records), output_path)
        elif format == ExportFormat.JSON:
            return self._export_json(records, output_path)
        elif format == ExportFormat.CSV:
            return self.csv.export_records(records, output_path, kwargs.get('columns'))
        elif format == ExportFormat.TSV:
            self.csv.delimiter = '\t'
            result = self.csv.export_records(records, output_path)
            result.format = ExportFormat.TSV
            return result
        elif format == ExportFormat.PARQUET:
            if output_path is None:
                return ExportResult(
                    success=False,
                    format=ExportFormat.PARQUET,
                    error="Parquet requires output_path"
                )
            return self.parquet.export_records(records, output_path)
        else:
            return ExportResult(
                success=False,
                format=format,
                error=f"Unsupported format: {format.value}"
            )

    def _export_json(
        self,
        records: List[Dict[str, Any]],
        output_path: Optional[Union[str, Path]] = None
    ) -> ExportResult:
        """Export as single JSON array."""
        try:
            content = json.dumps(records, indent=2, default=str)
            content_bytes = content.encode('utf-8')

            metadata = ExportMetadata(
                format="json",
                record_count=len(records)
            )

            if output_path:
                path = Path(output_path)
                path.write_bytes(content_bytes)
                return ExportResult(
                    success=True,
                    format=ExportFormat.JSON,
                    path=str(path),
                    record_count=len(records),
                    metadata=metadata
                )
            else:
                return ExportResult(
                    success=True,
                    format=ExportFormat.JSON,
                    content=content_bytes,
                    record_count=len(records),
                    metadata=metadata
                )

        except Exception as e:
            return ExportResult(
                success=False,
                format=ExportFormat.JSON,
                error=str(e)
            )

    def export_beliefs(
        self,
        beliefs: List[Any],
        format: ExportFormat,
        output_path: Optional[Union[str, Path]] = None,
        web: Optional[Any] = None
    ) -> ExportResult:
        """Export beliefs in the specified format."""
        if format == ExportFormat.JSONL:
            return self.jsonl.export_beliefs(beliefs, output_path, web=web)

        # Convert beliefs to dicts for other formats
        records = []
        for belief in beliefs:
            d = {
                "belief_id": getattr(belief, 'belief_id', None),
                "content": getattr(belief, 'content', None),
                "level": getattr(belief, 'level', None),
                "status": getattr(belief, 'status', None),
                "theory_id": getattr(belief, 'theory_id', None),
            }
            if hasattr(d.get('level'), 'value'):
                d['level'] = d['level'].value
            if hasattr(d.get('status'), 'value'):
                d['status'] = d['status'].value

            credence = getattr(belief, 'credence', None)
            if credence:
                d['credence_value'] = getattr(credence, 'value', None)
                d['credence_uncertainty'] = getattr(credence, 'uncertainty', None)

            records.append({k: v for k, v in d.items() if v is not None})

        return self.export(records, format, output_path)


# =============================================================================
# Streaming Exporter
# =============================================================================

class StreamingExporter:
    """
    Streaming exporter for large datasets.

    Writes records incrementally without loading all into memory.
    """

    def __init__(self, output_path: Union[str, Path], format: ExportFormat = ExportFormat.JSONL):
        self.output_path = Path(output_path)
        self.format = format
        self._file = None
        self._count = 0
        self._writer = None

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def open(self):
        """Open the output file."""
        if self.format == ExportFormat.JSONL:
            self._file = open(self.output_path, 'w', encoding='utf-8')
        elif self.format == ExportFormat.CSV:
            self._file = open(self.output_path, 'w', encoding='utf-8', newline='')
        else:
            raise ValueError(f"Streaming not supported for {self.format.value}")

    def write(self, record: Dict[str, Any]):
        """Write a single record."""
        if self._file is None:
            raise RuntimeError("Exporter not opened")

        if self.format == ExportFormat.JSONL:
            line = json.dumps(record, separators=(',', ':'), default=str)
            self._file.write(line + '\n')
        elif self.format == ExportFormat.CSV:
            if self._writer is None:
                self._writer = csv.DictWriter(self._file, fieldnames=list(record.keys()))
                self._writer.writeheader()
            self._writer.writerow(record)

        self._count += 1

    def close(self) -> ExportResult:
        """Close the file and return result."""
        if self._file:
            self._file.close()
            self._file = None

        return ExportResult(
            success=True,
            format=self.format,
            path=str(self.output_path),
            record_count=self._count,
            metadata=ExportMetadata(
                format=self.format.value,
                record_count=self._count
            )
        )


# =============================================================================
# Convenience Functions
# =============================================================================

def export_to_jsonl(
    records: List[Dict[str, Any]],
    output_path: Optional[Union[str, Path]] = None,
    compress: bool = False
) -> ExportResult:
    """Export records to JSONL format."""
    exporter = JSONLExporter(compress=compress)
    return exporter.export_records(iter(records), output_path)


def export_to_csv(
    records: List[Dict[str, Any]],
    output_path: Optional[Union[str, Path]] = None,
    columns: Optional[List[str]] = None
) -> ExportResult:
    """Export records to CSV format."""
    exporter = CSVExporter()
    return exporter.export_records(records, output_path, columns)


def export_to_parquet(
    records: List[Dict[str, Any]],
    output_path: Union[str, Path]
) -> ExportResult:
    """Export records to Parquet format."""
    exporter = ParquetExporter()
    return exporter.export_records(records, output_path)


def export_beliefs_jsonl(
    beliefs: List[Any],
    output_path: Optional[Union[str, Path]] = None,
    web: Optional[Any] = None
) -> ExportResult:
    """Export beliefs to JSONL format."""
    exporter = JSONLExporter()
    return exporter.export_beliefs(beliefs, output_path, web=web)
