"""
Tests for the Annotation Service (EN-0D)
=========================================

Tests all CRUD operations, supersession chains, filtering,
and the three annotation layers.
"""

import json
import os
import sqlite3
import tempfile
import pytest
from pathlib import Path

# Ensure project root is on path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.services.annotation_service import (
    AnnotationService,
    AnnotationType,
    AnnotationLayer,
    Annotation,
    TYPE_TO_LAYER,
    VALID_TARGET_TYPES,
)


@pytest.fixture
def svc(tmp_path):
    """Create an AnnotationService backed by a temporary database."""
    db_path = str(tmp_path / "test_annotations.db")
    return AnnotationService(db_path=db_path)


# =========================================================================
# Layer 1: Evidence Annotations
# =========================================================================

class TestLayer1Evidence:

    def test_create_calibration_note(self, svc):
        ann = svc.create_annotation(
            type=AnnotationType.CALIBRATION_NOTE,
            target_type="template",
            target_id="CLE1",
            content="Panel felt circadian threshold was well-supported by meta-analysis",
            author="LIGHT-I panel",
            confidence=0.9,
            metadata={"panel_session": "2026-02-15"},
        )
        assert ann.id is not None
        assert ann.type == AnnotationType.CALIBRATION_NOTE
        assert ann.status == "active"
        assert ann.confidence == 0.9
        assert ann.layer == AnnotationLayer.EVIDENCE

    def test_create_sensitivity_flag(self, svc):
        ann = svc.create_annotation(
            type=AnnotationType.SENSITIVITY_FLAG,
            target_type="parameter",
            target_id="CLE1:melanopic_threshold",
            content="This threshold varies 3× across studies (0.3–0.9 lux)",
            author="system",
            confidence=0.7,
            metadata={"min_value": 0.3, "max_value": 0.9, "ratio": 3.0},
        )
        assert ann.target_type == "parameter"
        assert ann.target_id == "CLE1:melanopic_threshold"

    def test_create_evidence_override(self, svc):
        ann = svc.create_annotation(
            type=AnnotationType.EVIDENCE_OVERRIDE,
            target_type="causal_link",
            target_id="AX1:AX1.L1",
            content="Upgraded from how-plausibly to how-actually after 2025 RCT",
            author="Dr. Martinez",
            metadata={"old_maturity": "how-plausibly", "new_maturity": "how-actually"},
        )
        assert ann.type == AnnotationType.EVIDENCE_OVERRIDE

    def test_create_provenance_patch(self, svc):
        ann = svc.create_annotation(
            type=AnnotationType.PROVENANCE_PATCH,
            target_type="template",
            target_id="T54",
            content="Added missing DOI from panel meeting transcript",
            metadata={"doi": "10.1234/example.2025"},
        )
        assert ann.type == AnnotationType.PROVENANCE_PATCH


# =========================================================================
# Layer 2: Relational Annotations
# =========================================================================

class TestLayer2Relational:

    def test_create_cross_reference(self, svc):
        ann = svc.create_annotation(
            type=AnnotationType.CROSS_REFERENCE,
            target_type="template",
            target_id="CLE1",
            content="Shares circadian mechanism with L4 but via different receptor pathway",
            metadata={"related_template": "L4", "relation": "complementary"},
        )
        assert ann.layer == AnnotationLayer.RELATIONAL

    def test_create_molecule_link(self, svc):
        ann = svc.create_annotation(
            type=AnnotationType.MOLECULE_LINK,
            target_type="template",
            target_id="AX1",
            content="Touches pain-overlap pathway in allostatic regulation molecule",
            metadata={"molecule_id": "allostatic_regulation", "pathway": "pain-overlap"},
        )
        assert ann.type == AnnotationType.MOLECULE_LINK

    def test_create_clinical_caution(self, svc):
        ann = svc.create_annotation(
            type=AnnotationType.CLINICAL_CAUTION,
            target_type="causal_link",
            target_id="CLE1:CLE1.L2",
            content="Contraindicated in photosensitive epilepsy patients",
            confidence=0.95,
            metadata={"severity": "high", "population": "photosensitive_epilepsy"},
        )
        assert ann.confidence == 0.95


# =========================================================================
# Layer 3: QA/User-Facing Annotations
# =========================================================================

class TestLayer3QAUser:

    def test_create_open_question(self, svc):
        ann = svc.create_annotation(
            type=AnnotationType.OPEN_QUESTION,
            target_type="template",
            target_id="CLE1",
            content="No studies on circadian entrainment in elderly hospital populations",
            metadata={"gap_severity": "high", "population": "elderly"},
        )
        assert ann.layer == AnnotationLayer.QA_USER

    def test_create_search_prompt(self, svc):
        ann = svc.create_annotation(
            type=AnnotationType.SEARCH_PROMPT,
            target_type="template",
            target_id="CLE1",
            content="Search: 'circadian entrainment elderly hospital melanopic'",
            metadata={"databases": ["PubMed", "Google Scholar"]},
        )
        assert ann.type == AnnotationType.SEARCH_PROMPT

    def test_create_user_feedback(self, svc):
        ann = svc.create_annotation(
            type=AnnotationType.USER_FEEDBACK,
            target_type="answer",
            target_id="q_circadian_recovery_2026-02-27",
            content="Answer was thorough but missed recent Danish hospital study",
            confidence=0.8,
            metadata={"rating": 4, "missing_ref": "Hansen et al. 2025"},
        )
        assert ann.metadata["rating"] == 4


# =========================================================================
# CRUD & Filtering
# =========================================================================

class TestCRUD:

    def test_get_annotation_by_id(self, svc):
        ann = svc.create_annotation(
            type=AnnotationType.CALIBRATION_NOTE,
            target_type="template",
            target_id="CLE1",
            content="Test note",
        )
        fetched = svc.get_annotation(ann.id)
        assert fetched is not None
        assert fetched.id == ann.id
        assert fetched.content == "Test note"

    def test_get_annotation_not_found(self, svc):
        assert svc.get_annotation("nonexistent-id") is None

    def test_get_annotations_for_target(self, svc):
        svc.create_annotation(
            type=AnnotationType.CALIBRATION_NOTE,
            target_type="template", target_id="CLE1",
            content="Note 1",
        )
        svc.create_annotation(
            type=AnnotationType.SENSITIVITY_FLAG,
            target_type="template", target_id="CLE1",
            content="Flag 1",
        )
        svc.create_annotation(
            type=AnnotationType.CALIBRATION_NOTE,
            target_type="template", target_id="L4",
            content="Different template",
        )

        cle1_anns = svc.get_annotations("template", "CLE1")
        assert len(cle1_anns) == 2

        l4_anns = svc.get_annotations("template", "L4")
        assert len(l4_anns) == 1

    def test_get_active_annotations_excludes_superseded(self, svc):
        ann1 = svc.create_annotation(
            type=AnnotationType.CALIBRATION_NOTE,
            target_type="template", target_id="CLE1",
            content="Original",
        )
        svc.supersede_annotation(ann1.id, "Updated", "reviewer")

        active = svc.get_active_annotations("template", "CLE1")
        assert len(active) == 1
        assert active[0].content == "Updated"

        all_anns = svc.get_annotations("template", "CLE1")
        assert len(all_anns) == 2

    def test_get_annotations_by_type(self, svc):
        svc.create_annotation(
            type=AnnotationType.SENSITIVITY_FLAG,
            target_type="parameter", target_id="CLE1:threshold",
            content="Flag A",
        )
        svc.create_annotation(
            type=AnnotationType.SENSITIVITY_FLAG,
            target_type="parameter", target_id="L4:intensity",
            content="Flag B",
        )
        svc.create_annotation(
            type=AnnotationType.CALIBRATION_NOTE,
            target_type="template", target_id="CLE1",
            content="Not a flag",
        )

        flags = svc.get_annotations_by_type(AnnotationType.SENSITIVITY_FLAG)
        assert len(flags) == 2
        assert all(f.type == AnnotationType.SENSITIVITY_FLAG for f in flags)

    def test_search_annotations(self, svc):
        svc.create_annotation(
            type=AnnotationType.OPEN_QUESTION,
            target_type="template", target_id="CLE1",
            content="No studies on circadian effects in elderly patients",
        )
        svc.create_annotation(
            type=AnnotationType.CALIBRATION_NOTE,
            target_type="template", target_id="L4",
            content="Light intensity thresholds well-established",
        )

        results = svc.search_annotations("circadian")
        assert len(results) == 1
        assert "circadian" in results[0].content

    def test_invalid_target_type_raises(self, svc):
        with pytest.raises(ValueError, match="Invalid target_type"):
            svc.create_annotation(
                type=AnnotationType.CALIBRATION_NOTE,
                target_type="invalid_type",
                target_id="CLE1",
                content="Test",
            )


# =========================================================================
# Supersession Chain
# =========================================================================

class TestSupersession:

    def test_supersession_chain(self, svc):
        # Create original
        v1 = svc.create_annotation(
            type=AnnotationType.CALIBRATION_NOTE,
            target_type="template", target_id="CLE1",
            content="Version 1: initial estimate",
            author="Panel A",
        )
        assert v1.status == "active"

        # Supersede
        v2 = svc.supersede_annotation(v1.id, "Version 2: revised after RCT", "Panel B")
        assert v2.status == "active"
        assert v2.supersedes == v1.id
        assert v2.provenance["superseded_from"] == v1.id

        # Check old is superseded
        v1_reloaded = svc.get_annotation(v1.id)
        assert v1_reloaded.status == "superseded"

        # Supersede again
        v3 = svc.supersede_annotation(v2.id, "Version 3: final consensus", "Panel C")
        assert v3.supersedes == v2.id

        # Only v3 should be active
        active = svc.get_active_annotations("template", "CLE1")
        assert len(active) == 1
        assert active[0].id == v3.id

        # All 3 should exist
        all_anns = svc.get_annotations("template", "CLE1")
        assert len(all_anns) == 3

    def test_cannot_supersede_superseded(self, svc):
        v1 = svc.create_annotation(
            type=AnnotationType.CALIBRATION_NOTE,
            target_type="template", target_id="CLE1",
            content="Original",
        )
        svc.supersede_annotation(v1.id, "V2", "author")

        with pytest.raises(ValueError, match="Cannot supersede"):
            svc.supersede_annotation(v1.id, "V3 from old", "author")

    def test_cannot_supersede_nonexistent(self, svc):
        with pytest.raises(ValueError, match="not found"):
            svc.supersede_annotation("nonexistent", "Content", "author")


# =========================================================================
# Batch & Stats
# =========================================================================

class TestBatchAndStats:

    def test_batch_create(self, svc):
        specs = [
            {
                "type": "CALIBRATION_NOTE",
                "target_type": "template",
                "target_id": f"T{i}",
                "content": f"Batch note {i}",
                "author": "system",
            }
            for i in range(10)
        ]
        results = svc.create_annotations_batch(specs)
        assert len(results) == 10
        assert all(r.type == AnnotationType.CALIBRATION_NOTE for r in results)

    def test_stats(self, svc):
        svc.create_annotation(
            type=AnnotationType.CALIBRATION_NOTE,
            target_type="template", target_id="CLE1",
            content="Note 1",
        )
        svc.create_annotation(
            type=AnnotationType.SENSITIVITY_FLAG,
            target_type="parameter", target_id="CLE1:x",
            content="Flag 1",
        )
        svc.create_annotation(
            type=AnnotationType.OPEN_QUESTION,
            target_type="template", target_id="CLE1",
            content="Question 1",
        )

        stats = svc.get_annotation_stats()
        assert stats["total"] == 3
        assert stats["by_type"]["CALIBRATION_NOTE"] == 1
        assert stats["by_type"]["SENSITIVITY_FLAG"] == 1
        assert stats["by_type"]["OPEN_QUESTION"] == 1
        assert stats["by_layer"]["evidence"] == 2
        assert stats["by_layer"]["qa_user"] == 1
        assert stats["by_status"]["active"] == 3


# =========================================================================
# QA Integration Helpers
# =========================================================================

class TestQAIntegration:

    def test_get_template_annotations(self, svc):
        svc.create_annotation(
            type=AnnotationType.CALIBRATION_NOTE,
            target_type="template", target_id="CLE1",
            content="Note",
        )
        svc.create_annotation(
            type=AnnotationType.OPEN_QUESTION,
            target_type="template", target_id="CLE1",
            content="Gap",
        )
        svc.create_annotation(
            type=AnnotationType.SENSITIVITY_FLAG,
            target_type="parameter", target_id="CLE1:x",
            content="Flag (different target_type)",
        )

        all_template = svc.get_template_annotations("CLE1")
        assert len(all_template) == 2  # excludes parameter annotations

        only_questions = svc.get_template_annotations(
            "CLE1", types=[AnnotationType.OPEN_QUESTION]
        )
        assert len(only_questions) == 1

    def test_get_parameter_sensitivity_flags(self, svc):
        svc.create_annotation(
            type=AnnotationType.SENSITIVITY_FLAG,
            target_type="parameter", target_id="CLE1:melanopic_threshold",
            content="Varies 3×",
        )
        svc.create_annotation(
            type=AnnotationType.SENSITIVITY_FLAG,
            target_type="parameter", target_id="CLE1:circadian_period",
            content="Individual variation ±2h",
        )
        svc.create_annotation(
            type=AnnotationType.SENSITIVITY_FLAG,
            target_type="parameter", target_id="L4:intensity",
            content="Different template",
        )

        flags = svc.get_parameter_sensitivity_flags("CLE1")
        assert len(flags) == 2
        assert all("CLE1:" in f.target_id for f in flags)


# =========================================================================
# Type Coverage
# =========================================================================

class TestTypeCoverage:
    """Ensure all annotation types and layers are properly mapped."""

    def test_all_types_have_layers(self):
        for t in AnnotationType:
            assert t in TYPE_TO_LAYER, f"{t} missing from TYPE_TO_LAYER"

    def test_layer_counts(self):
        evidence = [t for t, l in TYPE_TO_LAYER.items() if l == AnnotationLayer.EVIDENCE]
        relational = [t for t, l in TYPE_TO_LAYER.items() if l == AnnotationLayer.RELATIONAL]
        qa = [t for t, l in TYPE_TO_LAYER.items() if l == AnnotationLayer.QA_USER]
        assert len(evidence) == 4
        assert len(relational) == 3
        assert len(qa) == 3

    def test_valid_target_types(self):
        assert "template" in VALID_TARGET_TYPES
        assert "belief" in VALID_TARGET_TYPES
        assert "answer" in VALID_TARGET_TYPES
        assert "parameter" in VALID_TARGET_TYPES
        assert "causal_link" in VALID_TARGET_TYPES


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
