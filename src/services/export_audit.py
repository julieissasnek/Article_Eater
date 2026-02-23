"""
Export Audit Trail Service — Sprint 3.0.5-G
2026-02-10

Tracks all export operations for compliance, reproducibility, and provenance.

Features:
- Log all export operations with metadata
- Track what was exported, when, by whom, and why
- Store query context for reproducibility
- Generate audit reports
- Support compliance requirements (GDPR, research ethics)

Expert Panel Guidance:
- Simon: Audit should not impede workflow
- Parnas: Clear separation between audit and export logic
"""

import json
import hashlib
import logging
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime, timezone
import sqlite3
import threading

logger = logging.getLogger(__name__)


# =============================================================================
# Data Structures
# =============================================================================

class ExportType(Enum):
    """Types of exports that can be audited."""
    BIBTEX = "bibtex"
    EVIDENCE_SUMMARY = "evidence_summary"
    RESEARCH_BRIEF = "research_brief"
    TECHNICAL_REPORT = "technical_report"
    BELIEF_DATA = "belief_data"
    CONSTRAINT_DATA = "constraint_data"
    NETWORK_GRAPH = "network_graph"
    QUERY_RESULTS = "query_results"
    VERIFICATION_CHECKLIST = "verification_checklist"
    FULL_WEB_SNAPSHOT = "full_web_snapshot"
    CUSTOM = "custom"


class ExportFormat(Enum):
    """Export file formats."""
    JSON = "json"
    MARKDOWN = "markdown"
    PDF = "pdf"
    HTML = "html"
    BIBTEX = "bibtex"
    CSV = "csv"
    JSONL = "jsonl"


class AuditStatus(Enum):
    """Status of an audit entry."""
    INITIATED = "initiated"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ExportContext:
    """Context for an export operation."""
    query: Optional[str] = None
    belief_ids: List[str] = field(default_factory=list)
    filters_applied: Dict[str, Any] = field(default_factory=dict)
    scope_conditions: Dict[str, Any] = field(default_factory=dict)
    user_notes: Optional[str] = None
    purpose: Optional[str] = None


@dataclass
class AuditEntry:
    """A single audit log entry."""
    audit_id: str
    timestamp: str
    export_type: ExportType
    export_format: ExportFormat
    status: AuditStatus
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    context: Optional[ExportContext] = None
    # Content metadata
    item_count: int = 0
    content_hash: Optional[str] = None
    file_size_bytes: int = 0
    output_path: Optional[str] = None
    # Timing
    duration_ms: int = 0
    # Error info
    error_message: Optional[str] = None
    # Provenance
    system_version: str = "V23.0.0"
    web_state_hash: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        d = asdict(self)
        d["export_type"] = self.export_type.value
        d["export_format"] = self.export_format.value
        d["status"] = self.status.value
        if self.context:
            d["context"] = asdict(self.context)
        return d

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'AuditEntry':
        """Create from dictionary."""
        d["export_type"] = ExportType(d["export_type"])
        d["export_format"] = ExportFormat(d["export_format"])
        d["status"] = AuditStatus(d["status"])
        if d.get("context"):
            d["context"] = ExportContext(**d["context"])
        return cls(**d)


@dataclass
class AuditSummary:
    """Summary statistics from audit log."""
    total_exports: int = 0
    exports_by_type: Dict[str, int] = field(default_factory=dict)
    exports_by_format: Dict[str, int] = field(default_factory=dict)
    exports_by_status: Dict[str, int] = field(default_factory=dict)
    total_items_exported: int = 0
    total_bytes_exported: int = 0
    date_range_start: Optional[str] = None
    date_range_end: Optional[str] = None
    unique_users: int = 0
    average_duration_ms: float = 0.0


# =============================================================================
# Audit Service
# =============================================================================

class ExportAuditService:
    """
    Service for tracking and auditing export operations.

    Provides:
    - Logging of all export operations
    - Query context preservation
    - Content hashing for verification
    - Audit report generation
    - SQLite persistence
    """

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize the audit service.

        Args:
            db_path: Path to SQLite database. If None, uses in-memory database.
        """
        self.db_path = db_path or ":memory:"
        self._conn: Optional[sqlite3.Connection] = None
        self._lock = threading.Lock()
        self._init_db()

    def _init_db(self) -> None:
        """Initialize the database schema."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS export_audit (
                audit_id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                export_type TEXT NOT NULL,
                export_format TEXT NOT NULL,
                status TEXT NOT NULL,
                user_id TEXT,
                session_id TEXT,
                context_json TEXT,
                item_count INTEGER DEFAULT 0,
                content_hash TEXT,
                file_size_bytes INTEGER DEFAULT 0,
                output_path TEXT,
                duration_ms INTEGER DEFAULT 0,
                error_message TEXT,
                system_version TEXT,
                web_state_hash TEXT
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_audit_timestamp
            ON export_audit(timestamp)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_audit_user
            ON export_audit(user_id)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_audit_type
            ON export_audit(export_type)
        """)

        conn.commit()

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self._conn.row_factory = sqlite3.Row
        return self._conn

    # =========================================================================
    # Audit Logging
    # =========================================================================

    def log_export_start(
        self,
        export_type: ExportType,
        export_format: ExportFormat,
        context: Optional[ExportContext] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> str:
        """
        Log the start of an export operation.

        Returns audit_id for tracking.
        """
        audit_id = self._generate_audit_id()
        timestamp = datetime.now(timezone.utc).isoformat()

        entry = AuditEntry(
            audit_id=audit_id,
            timestamp=timestamp,
            export_type=export_type,
            export_format=export_format,
            status=AuditStatus.INITIATED,
            user_id=user_id,
            session_id=session_id,
            context=context
        )

        self._save_entry(entry)
        logger.info(f"Export audit started: {audit_id} ({export_type.value})")

        return audit_id

    def log_export_complete(
        self,
        audit_id: str,
        content: bytes,
        output_path: Optional[str] = None,
        item_count: int = 0,
        duration_ms: int = 0,
        web_state_hash: Optional[str] = None
    ) -> None:
        """Log successful completion of an export."""
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()

            content_hash = self._compute_hash(content)
            file_size = len(content)

            cursor.execute("""
                UPDATE export_audit SET
                    status = ?,
                    content_hash = ?,
                    file_size_bytes = ?,
                    output_path = ?,
                    item_count = ?,
                    duration_ms = ?,
                    web_state_hash = ?
                WHERE audit_id = ?
            """, (
                AuditStatus.COMPLETED.value,
                content_hash,
                file_size,
                output_path,
                item_count,
                duration_ms,
                web_state_hash,
                audit_id
            ))

            conn.commit()

        logger.info(f"Export audit completed: {audit_id} ({item_count} items, {file_size} bytes)")

    def log_export_failed(
        self,
        audit_id: str,
        error_message: str,
        duration_ms: int = 0
    ) -> None:
        """Log failed export."""
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE export_audit SET
                    status = ?,
                    error_message = ?,
                    duration_ms = ?
                WHERE audit_id = ?
            """, (
                AuditStatus.FAILED.value,
                error_message,
                duration_ms,
                audit_id
            ))

            conn.commit()

        logger.warning(f"Export audit failed: {audit_id} - {error_message}")

    def log_export_cancelled(
        self,
        audit_id: str,
        reason: Optional[str] = None
    ) -> None:
        """Log cancelled export."""
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE export_audit SET
                    status = ?,
                    error_message = ?
                WHERE audit_id = ?
            """, (
                AuditStatus.CANCELLED.value,
                reason or "User cancelled",
                audit_id
            ))

            conn.commit()

        logger.info(f"Export audit cancelled: {audit_id}")

    def _save_entry(self, entry: AuditEntry) -> None:
        """Save audit entry to database."""
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()

            context_json = json.dumps(asdict(entry.context)) if entry.context else None

            cursor.execute("""
                INSERT INTO export_audit (
                    audit_id, timestamp, export_type, export_format, status,
                    user_id, session_id, context_json, item_count, content_hash,
                    file_size_bytes, output_path, duration_ms, error_message,
                    system_version, web_state_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                entry.audit_id,
                entry.timestamp,
                entry.export_type.value,
                entry.export_format.value,
                entry.status.value,
                entry.user_id,
                entry.session_id,
                context_json,
                entry.item_count,
                entry.content_hash,
                entry.file_size_bytes,
                entry.output_path,
                entry.duration_ms,
                entry.error_message,
                entry.system_version,
                entry.web_state_hash
            ))

            conn.commit()

    # =========================================================================
    # Query Methods
    # =========================================================================

    def get_entry(self, audit_id: str) -> Optional[AuditEntry]:
        """Get a specific audit entry."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM export_audit WHERE audit_id = ?", (audit_id,))
        row = cursor.fetchone()

        if row:
            return self._row_to_entry(row)
        return None

    def get_entries(
        self,
        limit: int = 100,
        offset: int = 0,
        export_type: Optional[ExportType] = None,
        status: Optional[AuditStatus] = None,
        user_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[AuditEntry]:
        """Get audit entries with filtering."""
        conn = self._get_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM export_audit WHERE 1=1"
        params: List[Any] = []

        if export_type:
            query += " AND export_type = ?"
            params.append(export_type.value)

        if status:
            query += " AND status = ?"
            params.append(status.value)

        if user_id:
            query += " AND user_id = ?"
            params.append(user_id)

        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date)

        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date)

        query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cursor.execute(query, params)
        rows = cursor.fetchall()

        return [self._row_to_entry(row) for row in rows]

    def get_summary(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> AuditSummary:
        """Get summary statistics from audit log."""
        conn = self._get_connection()
        cursor = conn.cursor()

        where_clause = "WHERE 1=1"
        params: List[Any] = []

        if start_date:
            where_clause += " AND timestamp >= ?"
            params.append(start_date)

        if end_date:
            where_clause += " AND timestamp <= ?"
            params.append(end_date)

        # Total exports
        cursor.execute(f"SELECT COUNT(*) FROM export_audit {where_clause}", params)
        total = cursor.fetchone()[0]

        # By type
        cursor.execute(f"""
            SELECT export_type, COUNT(*) as count
            FROM export_audit {where_clause}
            GROUP BY export_type
        """, params)
        by_type = {row[0]: row[1] for row in cursor.fetchall()}

        # By format
        cursor.execute(f"""
            SELECT export_format, COUNT(*) as count
            FROM export_audit {where_clause}
            GROUP BY export_format
        """, params)
        by_format = {row[0]: row[1] for row in cursor.fetchall()}

        # By status
        cursor.execute(f"""
            SELECT status, COUNT(*) as count
            FROM export_audit {where_clause}
            GROUP BY status
        """, params)
        by_status = {row[0]: row[1] for row in cursor.fetchall()}

        # Totals
        cursor.execute(f"""
            SELECT
                COALESCE(SUM(item_count), 0),
                COALESCE(SUM(file_size_bytes), 0),
                COALESCE(AVG(duration_ms), 0)
            FROM export_audit {where_clause}
        """, params)
        row = cursor.fetchone()
        total_items = row[0]
        total_bytes = row[1]
        avg_duration = row[2]

        # Date range
        cursor.execute(f"""
            SELECT MIN(timestamp), MAX(timestamp)
            FROM export_audit {where_clause}
        """, params)
        date_row = cursor.fetchone()

        # Unique users
        cursor.execute(f"""
            SELECT COUNT(DISTINCT user_id)
            FROM export_audit {where_clause}
            AND user_id IS NOT NULL
        """, params)
        unique_users = cursor.fetchone()[0]

        return AuditSummary(
            total_exports=total,
            exports_by_type=by_type,
            exports_by_format=by_format,
            exports_by_status=by_status,
            total_items_exported=total_items,
            total_bytes_exported=total_bytes,
            date_range_start=date_row[0],
            date_range_end=date_row[1],
            unique_users=unique_users,
            average_duration_ms=avg_duration
        )

    def _row_to_entry(self, row: sqlite3.Row) -> AuditEntry:
        """Convert database row to AuditEntry."""
        context = None
        if row["context_json"]:
            context_dict = json.loads(row["context_json"])
            context = ExportContext(**context_dict)

        return AuditEntry(
            audit_id=row["audit_id"],
            timestamp=row["timestamp"],
            export_type=ExportType(row["export_type"]),
            export_format=ExportFormat(row["export_format"]),
            status=AuditStatus(row["status"]),
            user_id=row["user_id"],
            session_id=row["session_id"],
            context=context,
            item_count=row["item_count"],
            content_hash=row["content_hash"],
            file_size_bytes=row["file_size_bytes"],
            output_path=row["output_path"],
            duration_ms=row["duration_ms"],
            error_message=row["error_message"],
            system_version=row["system_version"],
            web_state_hash=row["web_state_hash"]
        )

    # =========================================================================
    # Verification
    # =========================================================================

    def verify_export(
        self,
        audit_id: str,
        content: bytes
    ) -> bool:
        """
        Verify that content matches the audited export.

        Returns True if content hash matches.
        """
        entry = self.get_entry(audit_id)
        if not entry or not entry.content_hash:
            return False

        computed_hash = self._compute_hash(content)
        return computed_hash == entry.content_hash

    def get_provenance(self, audit_id: str) -> Dict[str, Any]:
        """
        Get full provenance information for an export.

        Useful for research reproducibility.
        """
        entry = self.get_entry(audit_id)
        if not entry:
            return {}

        provenance = {
            "audit_id": entry.audit_id,
            "timestamp": entry.timestamp,
            "system_version": entry.system_version,
            "export_type": entry.export_type.value,
            "export_format": entry.export_format.value,
            "content_hash": entry.content_hash,
            "web_state_hash": entry.web_state_hash,
            "item_count": entry.item_count,
        }

        if entry.context:
            provenance["query"] = entry.context.query
            provenance["belief_ids"] = entry.context.belief_ids
            provenance["filters"] = entry.context.filters_applied
            provenance["scope"] = entry.context.scope_conditions
            provenance["purpose"] = entry.context.purpose

        return provenance

    # =========================================================================
    # Export Audit Report
    # =========================================================================

    def generate_audit_report(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        format: str = "markdown"
    ) -> str:
        """Generate an audit report."""
        summary = self.get_summary(start_date, end_date)
        entries = self.get_entries(limit=100, start_date=start_date, end_date=end_date)

        if format == "markdown":
            return self._generate_markdown_report(summary, entries)
        elif format == "json":
            return json.dumps({
                "summary": asdict(summary),
                "entries": [e.to_dict() for e in entries]
            }, indent=2)
        else:
            return self._generate_markdown_report(summary, entries)

    def _generate_markdown_report(
        self,
        summary: AuditSummary,
        entries: List[AuditEntry]
    ) -> str:
        """Generate markdown audit report."""
        lines = [
            "# Export Audit Report",
            "",
            f"Generated: {datetime.now(timezone.utc).isoformat()}",
            "",
            "## Summary",
            "",
            f"- **Total Exports**: {summary.total_exports}",
            f"- **Total Items Exported**: {summary.total_items_exported:,}",
            f"- **Total Data Volume**: {summary.total_bytes_exported:,} bytes",
            f"- **Unique Users**: {summary.unique_users}",
            f"- **Average Duration**: {summary.average_duration_ms:.1f} ms",
            "",
        ]

        if summary.date_range_start and summary.date_range_end:
            lines.append(f"**Date Range**: {summary.date_range_start[:10]} to {summary.date_range_end[:10]}")
            lines.append("")

        # By type
        lines.append("### Exports by Type")
        lines.append("")
        for export_type, count in sorted(summary.exports_by_type.items()):
            lines.append(f"- {export_type}: {count}")
        lines.append("")

        # By status
        lines.append("### Exports by Status")
        lines.append("")
        for status, count in sorted(summary.exports_by_status.items()):
            lines.append(f"- {status}: {count}")
        lines.append("")

        # Recent entries
        lines.append("## Recent Export Operations")
        lines.append("")

        if entries:
            lines.append("| Timestamp | Type | Format | Status | Items | Size |")
            lines.append("|-----------|------|--------|--------|-------|------|")

            for entry in entries[:50]:
                timestamp = entry.timestamp[:19]
                lines.append(
                    f"| {timestamp} | {entry.export_type.value} | "
                    f"{entry.export_format.value} | {entry.status.value} | "
                    f"{entry.item_count} | {entry.file_size_bytes} |"
                )
        else:
            lines.append("*No export operations found*")

        lines.append("")
        lines.append("---")
        lines.append("*Generated by Article Eater V23 Export Audit Service*")

        return "\n".join(lines)

    # =========================================================================
    # Utility Methods
    # =========================================================================

    def _generate_audit_id(self) -> str:
        """Generate a unique audit ID."""
        import uuid
        return f"EXP-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"

    def _compute_hash(self, content: bytes) -> str:
        """Compute SHA-256 hash of content."""
        if isinstance(content, str):
            content = content.encode('utf-8')
        return hashlib.sha256(content).hexdigest()

    def close(self) -> None:
        """Close database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None


# =============================================================================
# Context Manager for Audited Exports
# =============================================================================

class AuditedExport:
    """
    Context manager for audited export operations.

    Usage:
        with AuditedExport(service, ExportType.BIBTEX, ExportFormat.BIBTEX) as audit:
            content = generate_bibtex()
            audit.set_content(content, item_count=10)
    """

    def __init__(
        self,
        service: ExportAuditService,
        export_type: ExportType,
        export_format: ExportFormat,
        context: Optional[ExportContext] = None,
        user_id: Optional[str] = None
    ):
        self.service = service
        self.export_type = export_type
        self.export_format = export_format
        self.context = context
        self.user_id = user_id
        self.audit_id: Optional[str] = None
        self._start_time: Optional[float] = None
        self._content: Optional[bytes] = None
        self._item_count: int = 0
        self._output_path: Optional[str] = None

    def __enter__(self) -> 'AuditedExport':
        import time
        self._start_time = time.time()
        self.audit_id = self.service.log_export_start(
            export_type=self.export_type,
            export_format=self.export_format,
            context=self.context,
            user_id=self.user_id
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        import time
        duration_ms = int((time.time() - (self._start_time or 0)) * 1000)

        if exc_type is not None:
            # Exception occurred
            self.service.log_export_failed(
                self.audit_id,
                str(exc_val),
                duration_ms
            )
            return False  # Re-raise exception

        if self._content is not None:
            self.service.log_export_complete(
                self.audit_id,
                self._content,
                self._output_path,
                self._item_count,
                duration_ms
            )
        else:
            self.service.log_export_cancelled(self.audit_id, "No content provided")

        return False

    def set_content(
        self,
        content: bytes,
        item_count: int = 0,
        output_path: Optional[str] = None
    ) -> None:
        """Set the exported content for auditing."""
        if isinstance(content, str):
            content = content.encode('utf-8')
        self._content = content
        self._item_count = item_count
        self._output_path = output_path


# =============================================================================
# Singleton and Convenience Functions
# =============================================================================

_audit_service: Optional[ExportAuditService] = None


def get_audit_service(db_path: Optional[str] = None) -> ExportAuditService:
    """Get or create singleton audit service."""
    global _audit_service
    if _audit_service is None:
        _audit_service = ExportAuditService(db_path)
    return _audit_service


def audit_export(
    export_type: ExportType,
    export_format: ExportFormat,
    content: bytes,
    context: Optional[ExportContext] = None,
    user_id: Optional[str] = None,
    item_count: int = 0
) -> str:
    """
    Convenience function to log a complete export operation.

    Returns audit_id.
    """
    service = get_audit_service()

    audit_id = service.log_export_start(
        export_type=export_type,
        export_format=export_format,
        context=context,
        user_id=user_id
    )

    service.log_export_complete(
        audit_id=audit_id,
        content=content,
        item_count=item_count
    )

    return audit_id
