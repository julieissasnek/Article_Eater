"""
Annotation Service — Unified Annotation Layer for the Web of Belief
====================================================================

Created: 2026-02-27
Sprint: EN-0D (merges Sprint 0.5)
Phase α unification: 2026-03-01 (Sprint A)

Design Decisions (approved by David via Cowork):
  - Storage: Separate SQLite table (NOT in template JSONs)
  - Authorship: System + named human experts (no crowdsourcing initially)
  - Lifecycle: Immutable append-only with supersession
  - Priority: SENSITIVITY_FLAG and CALIBRATION_NOTE first
  - Molecule links: As annotations (lightweight, versionable)
  - Preprocessing: Applied at query time (always fresh)

Annotation Types (5 layers, 23 types):
  Layer 1 Evidence:    CALIBRATION_NOTE, SENSITIVITY_FLAG, EVIDENCE_OVERRIDE, PROVENANCE_PATCH
  Layer 2 Relational:  CROSS_REFERENCE, MOLECULE_LINK, CLINICAL_CAUTION
  Layer 3 QA/User:     OPEN_QUESTION, SEARCH_PROMPT, USER_FEEDBACK
  Layer 4 CVA:         MEASUREMENT_MODALITY, STIMULUS_DESCRIPTION, MOLECULE_T15_LINK
  Layer 5 Extended:    SURPRISE_FLAG, DESIGN_IMPLICATION, DISPUTE, ANALOGICAL_BRIDGE,
                       REPLICATION_STATUS, EFFECT_MAGNITUDE, CROSS_DOMAIN,
                       HISTORICAL_CONTEXT, NARRATIVE_HOOK, UNANSWERED_QUESTION

Phase α (additive): All types can be stored in SQLite. L2 JSON and L3 data models
still work as before. Phase β will switch consumers to unified API.
"""

from __future__ import annotations

import json
import logging
import sqlite3
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


# =============================================================================
# ENUMS & DATACLASSES
# =============================================================================

class AnnotationType(str, Enum):
    """23 annotation types across 5 layers."""
    # Layer 1: Evidence
    CALIBRATION_NOTE = "CALIBRATION_NOTE"
    SENSITIVITY_FLAG = "SENSITIVITY_FLAG"
    EVIDENCE_OVERRIDE = "EVIDENCE_OVERRIDE"
    PROVENANCE_PATCH = "PROVENANCE_PATCH"
    # Layer 2: Relational
    CROSS_REFERENCE = "CROSS_REFERENCE"
    MOLECULE_LINK = "MOLECULE_LINK"
    CLINICAL_CAUTION = "CLINICAL_CAUTION"
    # Layer 3: QA/User
    OPEN_QUESTION = "OPEN_QUESTION"
    SEARCH_PROMPT = "SEARCH_PROMPT"
    USER_FEEDBACK = "USER_FEEDBACK"
    # Layer 4: CVA (previously L2 JSON-backed)
    MEASUREMENT_MODALITY = "MEASUREMENT_MODALITY"
    STIMULUS_DESCRIPTION = "STIMULUS_DESCRIPTION"
    MOLECULE_T15_LINK = "MOLECULE_T15_LINK"
    # Layer 5: Extended A9-A18 (previously L3 no persistence)
    SURPRISE_FLAG = "SURPRISE_FLAG"                # A9
    DESIGN_IMPLICATION = "DESIGN_IMPLICATION"      # A10
    DISPUTE = "DISPUTE"                            # A11
    ANALOGICAL_BRIDGE = "ANALOGICAL_BRIDGE"        # A12
    REPLICATION_STATUS = "REPLICATION_STATUS"       # A13
    EFFECT_MAGNITUDE = "EFFECT_MAGNITUDE"          # A14
    CROSS_DOMAIN = "CROSS_DOMAIN"                  # A15
    HISTORICAL_CONTEXT = "HISTORICAL_CONTEXT"      # A16
    NARRATIVE_HOOK = "NARRATIVE_HOOK"              # A17
    UNANSWERED_QUESTION = "UNANSWERED_QUESTION"    # A18


class AnnotationLayer(str, Enum):
    EVIDENCE = "evidence"
    RELATIONAL = "relational"
    QA_USER = "qa_user"
    CVA = "cva"
    EXTENDED = "extended"


TYPE_TO_LAYER = {
    # Layer 1: Evidence
    AnnotationType.CALIBRATION_NOTE: AnnotationLayer.EVIDENCE,
    AnnotationType.SENSITIVITY_FLAG: AnnotationLayer.EVIDENCE,
    AnnotationType.EVIDENCE_OVERRIDE: AnnotationLayer.EVIDENCE,
    AnnotationType.PROVENANCE_PATCH: AnnotationLayer.EVIDENCE,
    # Layer 2: Relational
    AnnotationType.CROSS_REFERENCE: AnnotationLayer.RELATIONAL,
    AnnotationType.MOLECULE_LINK: AnnotationLayer.RELATIONAL,
    AnnotationType.CLINICAL_CAUTION: AnnotationLayer.RELATIONAL,
    # Layer 3: QA/User
    AnnotationType.OPEN_QUESTION: AnnotationLayer.QA_USER,
    AnnotationType.SEARCH_PROMPT: AnnotationLayer.QA_USER,
    AnnotationType.USER_FEEDBACK: AnnotationLayer.QA_USER,
    # Layer 4: CVA
    AnnotationType.MEASUREMENT_MODALITY: AnnotationLayer.CVA,
    AnnotationType.STIMULUS_DESCRIPTION: AnnotationLayer.CVA,
    AnnotationType.MOLECULE_T15_LINK: AnnotationLayer.CVA,
    # Layer 5: Extended A9-A18
    AnnotationType.SURPRISE_FLAG: AnnotationLayer.EXTENDED,
    AnnotationType.DESIGN_IMPLICATION: AnnotationLayer.EXTENDED,
    AnnotationType.DISPUTE: AnnotationLayer.EXTENDED,
    AnnotationType.ANALOGICAL_BRIDGE: AnnotationLayer.EXTENDED,
    AnnotationType.REPLICATION_STATUS: AnnotationLayer.EXTENDED,
    AnnotationType.EFFECT_MAGNITUDE: AnnotationLayer.EXTENDED,
    AnnotationType.CROSS_DOMAIN: AnnotationLayer.EXTENDED,
    AnnotationType.HISTORICAL_CONTEXT: AnnotationLayer.EXTENDED,
    AnnotationType.NARRATIVE_HOOK: AnnotationLayer.EXTENDED,
    AnnotationType.UNANSWERED_QUESTION: AnnotationLayer.EXTENDED,
}


VALID_TARGET_TYPES = frozenset([
    "template", "belief", "answer", "causal_link", "parameter",
    "molecule", "theory", "finding", "extraction",
])


@dataclass
class Annotation:
    """A single annotation in the web of belief."""
    id: str
    type: AnnotationType
    target_type: str
    target_id: str
    content: str
    author: str
    created: str  # ISO 8601
    provenance: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    supersedes: Optional[str] = None
    status: str = "active"
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def layer(self) -> AnnotationLayer:
        return TYPE_TO_LAYER.get(self.type, AnnotationLayer.EVIDENCE)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["type"] = self.type.value if isinstance(self.type, AnnotationType) else self.type
        return d


# =============================================================================
# ANNOTATION SERVICE
# =============================================================================

class AnnotationService:
    """
    CRUD service for the annotation system.

    Backed by SQLite. Applies migration 024 on first use if needed.
    All operations are append-only with supersession for versioning.
    """

    MIGRATION_SQL = str(
        Path(__file__).resolve().parent.parent.parent
        / "migrations" / "024_annotation_system.sql"
    )

    def __init__(self, db_path: str = None):
        if db_path is None:
            try:
                from src.services.db_locator import resolve_web_db
                db_path = str(resolve_web_db(prefer="integrated"))
            except Exception:
                db_path = str(get_web_db())
        self.db_path = db_path
        self._ensure_schema()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    def _ensure_schema(self) -> None:
        """Apply migration 024 if tables don't exist, then register new types."""
        conn = self._get_connection()
        try:
            # Check if table exists
            row = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='annotations'"
            ).fetchone()
            if row is None:
                migration_path = Path(self.MIGRATION_SQL)
                if migration_path.exists():
                    sql = migration_path.read_text()
                    conn.executescript(sql)
                    logger.info("Applied migration 024_annotation_system.sql")
                else:
                    # Inline fallback
                    self._create_tables_inline(conn)
            conn.commit()
        finally:
            conn.close()
        # Phase α: ensure L4 (CVA) and L5 (A9-A18) types are registered
        # even on databases that already had the original 10 types
        self.ensure_new_types_registered()

    def _create_tables_inline(self, conn: sqlite3.Connection) -> None:
        """Fallback: create tables directly if migration file not found."""
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS annotation_types (
                type TEXT PRIMARY KEY,
                layer TEXT NOT NULL,
                description TEXT NOT NULL
            );
            -- Layer 1: Evidence
            INSERT OR IGNORE INTO annotation_types (type, layer, description) VALUES
                ('CALIBRATION_NOTE',      'evidence',    'Expert commentary on calibration quality'),
                ('SENSITIVITY_FLAG',      'evidence',    'Marks parameters that are uncertain or vary widely'),
                ('EVIDENCE_OVERRIDE',     'evidence',    'Manual upgrade/downgrade of maturity level'),
                ('PROVENANCE_PATCH',      'evidence',    'Backfills missing provenance');
            -- Layer 2: Relational
            INSERT OR IGNORE INTO annotation_types (type, layer, description) VALUES
                ('CROSS_REFERENCE',       'relational',  'Links interacting templates'),
                ('MOLECULE_LINK',         'relational',  'Connects template to molecule/T1.5'),
                ('CLINICAL_CAUTION',      'relational',  'Safety-relevant annotation');
            -- Layer 3: QA/User
            INSERT OR IGNORE INTO annotation_types (type, layer, description) VALUES
                ('OPEN_QUESTION',         'qa_user',     'Knowledge gap marker'),
                ('SEARCH_PROMPT',         'qa_user',     'Directed search suggestion'),
                ('USER_FEEDBACK',         'qa_user',     'User quality rating');
            -- Layer 4: CVA (Phase α — migrated from JSON backing store)
            INSERT OR IGNORE INTO annotation_types (type, layer, description) VALUES
                ('MEASUREMENT_MODALITY',  'cva',         'How a finding was measured (fMRI, EEG, behavioral, etc.)'),
                ('STIMULUS_DESCRIPTION',  'cva',         'Stimulus type used in study (visual, auditory, spatial, etc.)'),
                ('MOLECULE_T15_LINK',     'cva',         'Links finding to T1.5 molecule via CVA analysis');
            -- Layer 5: Extended A9-A18 (Phase α — now has persistence)
            INSERT OR IGNORE INTO annotation_types (type, layer, description) VALUES
                ('SURPRISE_FLAG',         'extended',    'A9: Counterintuitive finding that challenges common assumptions'),
                ('DESIGN_IMPLICATION',    'extended',    'A10: Actionable design guidance derived from finding'),
                ('DISPUTE',               'extended',    'A11: Active disagreement between researchers on a claim'),
                ('ANALOGICAL_BRIDGE',     'extended',    'A12: Maps technical concept to everyday experience'),
                ('REPLICATION_STATUS',    'extended',    'A13: Tracks replication history for key findings'),
                ('EFFECT_MAGNITUDE',      'extended',    'A14: Human-interpretable effect size (NNT, Cohens d)'),
                ('CROSS_DOMAIN',          'extended',    'A15: Finding bridges two or more research domains'),
                ('HISTORICAL_CONTEXT',    'extended',    'A16: Historical development of research on this topic'),
                ('NARRATIVE_HOOK',        'extended',    'A17: Compelling story angle for science communication'),
                ('UNANSWERED_QUESTION',   'extended',    'A18: Open research question identified from this finding');
            CREATE TABLE IF NOT EXISTS annotations (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL REFERENCES annotation_types(type),
                target_type TEXT NOT NULL,
                target_id TEXT NOT NULL,
                content TEXT NOT NULL,
                author TEXT NOT NULL DEFAULT 'system',
                created TEXT NOT NULL,
                provenance TEXT NOT NULL DEFAULT '{}',
                confidence REAL NOT NULL DEFAULT 1.0,
                supersedes TEXT,
                status TEXT NOT NULL DEFAULT 'active',
                metadata TEXT NOT NULL DEFAULT '{}',
                CHECK (status IN ('active', 'superseded', 'retracted')),
                CHECK (confidence >= 0.0 AND confidence <= 1.0)
            );
            CREATE INDEX IF NOT EXISTS idx_annotations_target ON annotations(target_type, target_id);
            CREATE INDEX IF NOT EXISTS idx_annotations_type ON annotations(type);
            CREATE INDEX IF NOT EXISTS idx_annotations_status ON annotations(status);
        """)

    # -----------------------------------------------------------------
    # CREATE
    # -----------------------------------------------------------------

    def create_annotation(
        self,
        type: AnnotationType,
        target_type: str,
        target_id: str,
        content: str,
        author: str = "system",
        confidence: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None,
        provenance: Optional[Dict[str, Any]] = None,
    ) -> Annotation:
        """
        Create a new annotation. Returns the persisted Annotation.

        Immutable — once created, an annotation cannot be edited.
        Use supersede_annotation() to create a newer version.
        """
        if target_type not in VALID_TARGET_TYPES:
            raise ValueError(
                f"Invalid target_type '{target_type}'. "
                f"Valid: {sorted(VALID_TARGET_TYPES)}"
            )

        annotation = Annotation(
            id=str(uuid.uuid4()),
            type=type,
            target_type=target_type,
            target_id=target_id,
            content=content,
            author=author,
            created=datetime.now(timezone.utc).isoformat(),
            provenance=provenance or {},
            confidence=confidence,
            supersedes=None,
            status="active",
            metadata=metadata or {},
        )

        conn = self._get_connection()
        try:
            conn.execute(
                """INSERT INTO annotations
                   (id, type, target_type, target_id, content, author,
                    created, provenance, confidence, supersedes, status, metadata)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    annotation.id,
                    annotation.type.value,
                    annotation.target_type,
                    annotation.target_id,
                    annotation.content,
                    annotation.author,
                    annotation.created,
                    json.dumps(annotation.provenance),
                    annotation.confidence,
                    annotation.supersedes,
                    annotation.status,
                    json.dumps(annotation.metadata),
                ),
            )
            conn.commit()
        finally:
            conn.close()

        logger.debug(
            "Created annotation %s [%s] on %s:%s",
            annotation.id[:8], type.value, target_type, target_id,
        )
        return annotation

    # -----------------------------------------------------------------
    # READ
    # -----------------------------------------------------------------

    def _row_to_annotation(self, row: sqlite3.Row) -> Annotation:
        """Convert a database row to an Annotation dataclass."""
        type_str = row["type"]
        try:
            ann_type = AnnotationType(type_str)
        except ValueError:
            ann_type = type_str  # Gracefully handle unknown types

        return Annotation(
            id=row["id"],
            type=ann_type,
            target_type=row["target_type"],
            target_id=row["target_id"],
            content=row["content"],
            author=row["author"],
            created=row["created"],
            provenance=json.loads(row["provenance"]) if row["provenance"] else {},
            confidence=row["confidence"],
            supersedes=row["supersedes"],
            status=row["status"],
            metadata=json.loads(row["metadata"]) if row["metadata"] else {},
        )

    def get_annotation(self, annotation_id: str) -> Optional[Annotation]:
        """Get a single annotation by ID."""
        conn = self._get_connection()
        try:
            row = conn.execute(
                "SELECT * FROM annotations WHERE id = ?", (annotation_id,)
            ).fetchone()
            return self._row_to_annotation(row) if row else None
        finally:
            conn.close()

    def get_annotations(
        self, target_type: str, target_id: str
    ) -> List[Annotation]:
        """Get ALL annotations (including superseded) for a target."""
        conn = self._get_connection()
        try:
            rows = conn.execute(
                "SELECT * FROM annotations WHERE target_type = ? AND target_id = ? ORDER BY created",
                (target_type, target_id),
            ).fetchall()
            return [self._row_to_annotation(r) for r in rows]
        finally:
            conn.close()

    def get_active_annotations(
        self, target_type: str, target_id: str
    ) -> List[Annotation]:
        """Get only active (non-superseded, non-retracted) annotations for a target."""
        conn = self._get_connection()
        try:
            rows = conn.execute(
                """SELECT * FROM annotations
                   WHERE target_type = ? AND target_id = ? AND status = 'active'
                   ORDER BY created""",
                (target_type, target_id),
            ).fetchall()
            return [self._row_to_annotation(r) for r in rows]
        finally:
            conn.close()

    def get_annotations_by_type(
        self, ann_type: AnnotationType, status: str = "active"
    ) -> List[Annotation]:
        """Get all annotations of a given type."""
        conn = self._get_connection()
        try:
            rows = conn.execute(
                "SELECT * FROM annotations WHERE type = ? AND status = ? ORDER BY created",
                (ann_type.value, status),
            ).fetchall()
            return [self._row_to_annotation(r) for r in rows]
        finally:
            conn.close()

    def search_annotations(self, query_text: str) -> List[Annotation]:
        """Full-text search across annotation content."""
        conn = self._get_connection()
        try:
            rows = conn.execute(
                "SELECT * FROM annotations WHERE content LIKE ? AND status = 'active' ORDER BY created DESC",
                (f"%{query_text}%",),
            ).fetchall()
            return [self._row_to_annotation(r) for r in rows]
        finally:
            conn.close()

    # -----------------------------------------------------------------
    # SUPERSEDE (versioning)
    # -----------------------------------------------------------------

    def supersede_annotation(
        self,
        old_id: str,
        new_content: str,
        author: str,
        confidence: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Annotation:
        """
        Create a new annotation that supersedes an older one.

        The old annotation's status is set to 'superseded'.
        The new annotation carries a `supersedes` pointer.
        """
        old = self.get_annotation(old_id)
        if old is None:
            raise ValueError(f"Annotation {old_id} not found")
        if old.status != "active":
            raise ValueError(
                f"Cannot supersede annotation {old_id} with status '{old.status}'"
            )

        conn = self._get_connection()
        try:
            # Mark old as superseded
            conn.execute(
                "UPDATE annotations SET status = 'superseded' WHERE id = ?",
                (old_id,),
            )

            # Create new annotation
            new_ann = Annotation(
                id=str(uuid.uuid4()),
                type=old.type,
                target_type=old.target_type,
                target_id=old.target_id,
                content=new_content,
                author=author,
                created=datetime.now(timezone.utc).isoformat(),
                provenance={
                    "superseded_from": old_id,
                    "original_author": old.author,
                    "original_created": old.created,
                },
                confidence=confidence if confidence is not None else old.confidence,
                supersedes=old_id,
                status="active",
                metadata=metadata if metadata is not None else old.metadata,
            )

            conn.execute(
                """INSERT INTO annotations
                   (id, type, target_type, target_id, content, author,
                    created, provenance, confidence, supersedes, status, metadata)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    new_ann.id,
                    new_ann.type.value if isinstance(new_ann.type, AnnotationType) else new_ann.type,
                    new_ann.target_type,
                    new_ann.target_id,
                    new_ann.content,
                    new_ann.author,
                    new_ann.created,
                    json.dumps(new_ann.provenance),
                    new_ann.confidence,
                    new_ann.supersedes,
                    new_ann.status,
                    json.dumps(new_ann.metadata),
                ),
            )
            conn.commit()
        finally:
            conn.close()

        logger.info(
            "Superseded annotation %s → %s", old_id[:8], new_ann.id[:8]
        )
        return new_ann

    # -----------------------------------------------------------------
    # RETRACT
    # -----------------------------------------------------------------

    def retract_annotation(self, annotation_id: str, reason: str = "") -> None:
        """Mark an annotation as retracted (soft delete)."""
        conn = self._get_connection()
        try:
            conn.execute(
                "UPDATE annotations SET status = 'retracted' WHERE id = ?",
                (annotation_id,),
            )
            conn.commit()
        finally:
            conn.close()

    # -----------------------------------------------------------------
    # STATS
    # -----------------------------------------------------------------

    def get_annotation_stats(self) -> Dict[str, Any]:
        """Summary statistics for the annotation system."""
        conn = self._get_connection()
        try:
            total = conn.execute("SELECT COUNT(*) FROM annotations").fetchone()[0]

            by_type = {}
            for row in conn.execute(
                "SELECT type, COUNT(*) as n FROM annotations GROUP BY type"
            ).fetchall():
                by_type[row["type"]] = row["n"]

            by_layer = {}
            for row in conn.execute(
                """SELECT at.layer, COUNT(*) as n
                   FROM annotations a JOIN annotation_types at ON a.type = at.type
                   GROUP BY at.layer"""
            ).fetchall():
                by_layer[row["layer"]] = row["n"]

            by_status = {}
            for row in conn.execute(
                "SELECT status, COUNT(*) as n FROM annotations GROUP BY status"
            ).fetchall():
                by_status[row["status"]] = row["n"]

            by_target_type = {}
            for row in conn.execute(
                "SELECT target_type, COUNT(*) as n FROM annotations GROUP BY target_type"
            ).fetchall():
                by_target_type[row["target_type"]] = row["n"]

            return {
                "total": total,
                "by_type": by_type,
                "by_layer": by_layer,
                "by_status": by_status,
                "by_target_type": by_target_type,
            }
        finally:
            conn.close()

    # -----------------------------------------------------------------
    # BATCH OPERATIONS
    # -----------------------------------------------------------------

    def create_annotations_batch(
        self, annotations: List[Dict[str, Any]]
    ) -> List[Annotation]:
        """
        Create multiple annotations in a single transaction.

        Each dict should have: type, target_type, target_id, content,
        and optionally: author, confidence, metadata, provenance.
        """
        results = []
        conn = self._get_connection()
        try:
            for spec in annotations:
                ann_type = spec["type"]
                if isinstance(ann_type, str):
                    ann_type = AnnotationType(ann_type)

                annotation = Annotation(
                    id=str(uuid.uuid4()),
                    type=ann_type,
                    target_type=spec["target_type"],
                    target_id=spec["target_id"],
                    content=spec["content"],
                    author=spec.get("author", "system"),
                    created=datetime.now(timezone.utc).isoformat(),
                    provenance=spec.get("provenance", {}),
                    confidence=spec.get("confidence", 1.0),
                    supersedes=None,
                    status="active",
                    metadata=spec.get("metadata", {}),
                )

                conn.execute(
                    """INSERT INTO annotations
                       (id, type, target_type, target_id, content, author,
                        created, provenance, confidence, supersedes, status, metadata)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        annotation.id,
                        annotation.type.value,
                        annotation.target_type,
                        annotation.target_id,
                        annotation.content,
                        annotation.author,
                        annotation.created,
                        json.dumps(annotation.provenance),
                        annotation.confidence,
                        annotation.supersedes,
                        annotation.status,
                        json.dumps(annotation.metadata),
                    ),
                )
                results.append(annotation)

            conn.commit()
        finally:
            conn.close()

        logger.info("Created %d annotations in batch", len(results))
        return results

    # -----------------------------------------------------------------
    # QA INTEGRATION HELPERS
    # -----------------------------------------------------------------

    def get_template_annotations(
        self, template_id: str, types: Optional[List[AnnotationType]] = None
    ) -> List[Annotation]:
        """
        Get all active annotations for a template (convenience method).

        If types is specified, filters to only those annotation types.
        Used by QA preprocessor to inject SENSITIVITY_FLAGS and OPEN_QUESTIONS.
        """
        conn = self._get_connection()
        try:
            if types:
                placeholders = ",".join("?" for _ in types)
                rows = conn.execute(
                    f"""SELECT * FROM annotations
                        WHERE target_type = 'template' AND target_id = ?
                        AND status = 'active' AND type IN ({placeholders})
                        ORDER BY created""",
                    (template_id, *[t.value for t in types]),
                ).fetchall()
            else:
                rows = conn.execute(
                    """SELECT * FROM annotations
                       WHERE target_type = 'template' AND target_id = ?
                       AND status = 'active' ORDER BY created""",
                    (template_id,),
                ).fetchall()
            return [self._row_to_annotation(r) for r in rows]
        finally:
            conn.close()

    def get_parameter_sensitivity_flags(
        self, template_id: str
    ) -> List[Annotation]:
        """
        Get SENSITIVITY_FLAG annotations for all parameters of a template.

        target_id format for parameters: 'template_id:param_name'
        """
        conn = self._get_connection()
        try:
            rows = conn.execute(
                """SELECT * FROM annotations
                   WHERE type = 'SENSITIVITY_FLAG'
                   AND target_type = 'parameter'
                   AND target_id LIKE ?
                   AND status = 'active'
                   ORDER BY created""",
                (f"{template_id}:%",),
            ).fetchall()
            return [self._row_to_annotation(r) for r in rows]
        finally:
            conn.close()

    # -----------------------------------------------------------------
    # UNIFIED QUERY API (Phase α — Sprint A)
    # -----------------------------------------------------------------

    def get_all_annotations(
        self,
        target_id: str,
        target_type: Optional[str] = None,
        layers: Optional[List[AnnotationLayer]] = None,
        include_inactive: bool = False,
    ) -> List[Annotation]:
        """
        Unified query: get ALL annotations for a target across all layers.

        This is the primary API for Phase β+ consumers. It replaces the need
        to query L1 (SQLite), L2 (JSON), and L3 (in-memory) separately.

        Args:
            target_id: The entity ID (belief ID, template ID, finding ID, etc.)
            target_type: Optional filter by target type (belief, template, etc.)
                         If None, returns annotations across all target types.
            layers: Optional filter by annotation layers.
                    If None, returns annotations from all 5 layers.
            include_inactive: If True, includes superseded and retracted.

        Returns:
            List of Annotation objects, ordered by creation time.
        """
        conn = self._get_connection()
        try:
            conditions = ["a.target_id = ?"]
            params: list = [target_id]

            if target_type:
                conditions.append("a.target_type = ?")
                params.append(target_type)

            if not include_inactive:
                conditions.append("a.status = 'active'")

            if layers:
                layer_values = [l.value for l in layers]
                placeholders = ",".join("?" for _ in layer_values)
                conditions.append(f"at.layer IN ({placeholders})")
                params.extend(layer_values)

            where = " AND ".join(conditions)
            rows = conn.execute(
                f"""SELECT a.* FROM annotations a
                    LEFT JOIN annotation_types at ON a.type = at.type
                    WHERE {where}
                    ORDER BY a.created""",
                params,
            ).fetchall()
            return [self._row_to_annotation(r) for r in rows]
        finally:
            conn.close()

    def get_annotation_coverage(self) -> Dict[str, Any]:
        """
        Report annotation coverage across the system.

        Returns counts of annotated vs unannotated targets,
        useful for AN-SC-04 (>50% beliefs have annotations).
        """
        conn = self._get_connection()
        try:
            # Count unique targets with active annotations
            by_target_type = {}
            for row in conn.execute(
                """SELECT target_type, COUNT(DISTINCT target_id) as targets,
                          COUNT(*) as annotations
                   FROM annotations WHERE status = 'active'
                   GROUP BY target_type"""
            ).fetchall():
                by_target_type[row["target_type"]] = {
                    "unique_targets": row["targets"],
                    "total_annotations": row["annotations"],
                }

            # Count by layer
            by_layer = {}
            for row in conn.execute(
                """SELECT at.layer, COUNT(*) as n
                   FROM annotations a
                   JOIN annotation_types at ON a.type = at.type
                   WHERE a.status = 'active'
                   GROUP BY at.layer"""
            ).fetchall():
                by_layer[row["layer"]] = row["n"]

            return {
                "by_target_type": by_target_type,
                "by_layer": by_layer,
                "total_active": sum(
                    v["total_annotations"] for v in by_target_type.values()
                ),
            }
        finally:
            conn.close()

    def ensure_new_types_registered(self) -> int:
        """
        Ensure all AnnotationType enum values are registered in the
        annotation_types table. Useful for upgrading existing databases.

        Returns the number of newly registered types.
        """
        conn = self._get_connection()
        added = 0
        try:
            existing = set(
                row["type"]
                for row in conn.execute(
                    "SELECT type FROM annotation_types"
                ).fetchall()
            )
            for ann_type in AnnotationType:
                if ann_type.value not in existing:
                    layer = TYPE_TO_LAYER.get(ann_type, AnnotationLayer.EXTENDED)
                    conn.execute(
                        "INSERT OR IGNORE INTO annotation_types (type, layer, description) VALUES (?, ?, ?)",
                        (ann_type.value, layer.value, f"Auto-registered: {ann_type.value}"),
                    )
                    added += 1
            conn.commit()
            if added:
                logger.info("Registered %d new annotation types in DB", added)
        finally:
            conn.close()
        return added
