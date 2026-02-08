"""
Tests for Sprint 2.0.2: Output Serialization

Tests verify:
1. Manifest generation with checksums
2. Theory inference export (TD-A)
3. Scope condition export (TD-B)
4. Cluster stats export (TD-C)
5. BN edge export (TD-E)
6. Enhanced belief serialization
"""

import pytest
import json
import tempfile
from pathlib import Path
from datetime import datetime, timezone


class TestSchemaVersions:
    """Test schema version constants."""

    def test_schema_versions_exist(self):
        """All required schemas should be defined."""
        from src.services.output_serializer import SCHEMA_VERSIONS

        required = [
            "manifest", "web_state", "coherence_summary",
            "theory_inference", "scope_export", "temporal_export",
            "cluster_stats", "bn_edges", "claim", "rule",
            "stub", "tension", "bridge", "anomaly"
        ]
        for schema in required:
            assert schema in SCHEMA_VERSIONS
            assert SCHEMA_VERSIONS[schema].startswith("ae.")

    def test_schema_versions_format(self):
        """Schema versions should follow ae.<type>.v<n> format."""
        from src.services.output_serializer import SCHEMA_VERSIONS
        import re

        pattern = re.compile(r"^ae\.\w+\.v\d+$")
        for name, version in SCHEMA_VERSIONS.items():
            assert pattern.match(version), f"Schema {name} = {version} doesn't match pattern"


class TestOutputFile:
    """Test OutputFile dataclass."""

    def test_output_file_creation(self):
        """Should create OutputFile with required fields."""
        from src.services.output_serializer import OutputFile

        of = OutputFile(
            filename="test.json",
            schema="ae.test.v1",
            description="Test file",
            record_count=10
        )
        assert of.filename == "test.json"
        assert of.schema == "ae.test.v1"
        assert of.record_count == 10
        assert of.sha256 is None
        assert of.size_bytes == 0


class TestManifestGeneration:
    """Test manifest generation."""

    def test_generate_manifest_empty(self):
        """Should generate manifest with no files."""
        from src.services.output_serializer import generate_manifest, OutputFile

        with tempfile.TemporaryDirectory() as tmpdir:
            manifest = generate_manifest(
                out_dir=Path(tmpdir),
                run_id="test-run",
                paper_id="paper:001",
                outputs={}
            )

            assert manifest["schema"] == "ae.manifest.v1"
            assert manifest["run_id"] == "test-run"
            assert manifest["paper_id"] == "paper:001"
            assert manifest["file_count"] == 0
            assert manifest["files"] == []

    def test_generate_manifest_with_files(self):
        """Should generate manifest with checksums."""
        from src.services.output_serializer import generate_manifest, OutputFile

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a test file
            test_file = Path(tmpdir) / "test.json"
            test_file.write_text('{"test": true}')

            outputs = {
                "test": OutputFile(
                    filename="test.json",
                    schema="ae.test.v1",
                    description="Test file",
                    record_count=1
                )
            }

            manifest = generate_manifest(
                out_dir=Path(tmpdir),
                run_id="test-run",
                paper_id="paper:001",
                outputs=outputs
            )

            assert manifest["file_count"] == 1
            assert len(manifest["files"]) == 1
            assert manifest["files"][0]["sha256"] is not None
            assert manifest["files"][0]["size_bytes"] > 0
            assert manifest["files"][0]["exists"] is True


class TestTheoryInferenceExport:
    """Test theory inference serialization (TD-A)."""

    def test_serialize_empty(self):
        """Should handle empty mapping results."""
        from src.services.output_serializer import serialize_theory_inference

        result = serialize_theory_inference([], "run-1", "paper:001")

        assert result["schema"] == "ae.theory_inference.v1"
        assert result["n_inferences"] == 0
        assert result["inferences"] == []

    def test_serialize_with_results(self):
        """Should serialize theory inference results."""
        from src.services.output_serializer import serialize_theory_inference

        mapping_results = [
            {
                "entity_id": "claim:001",
                "primary_theory_id": "ART",
                "theory_ids": {"ART": 0.8, "SRT": 0.2},
                "theory_inference_method": "embedding",
                "theory_confidence": 0.85,
                "needs_theory_review": False,
            },
            {
                "entity_id": "claim:002",
                "primary_theory_id": None,
                "is_stub": True,
                "stub_reason": "no_matching_theory",
                "needs_theory_review": True,
            }
        ]

        result = serialize_theory_inference(mapping_results, "run-1", "paper:001")

        assert result["n_inferences"] == 2
        assert result["n_needs_review"] == 1
        assert "embedding" in result["methods_used"]
        assert "claim:002" in result["review_queue"]


class TestScopeExport:
    """Test scope condition serialization (TD-B)."""

    def test_serialize_scope_conditions(self):
        """Should serialize scope conditions."""
        from src.services.output_serializer import serialize_scope_conditions

        beliefs = [
            {
                "belief_id": "b1",
                "scope": {
                    "population": "college students",
                    "setting": "laboratory",
                    "scope_specified": True,
                    "explicit_fields": ["population", "setting"],
                }
            },
            {
                "belief_id": "b2",
                "scope": {
                    "population": None,
                    "setting": None,
                    "scope_specified": False,
                }
            }
        ]

        result = serialize_scope_conditions(beliefs, "run-1", "paper:001")

        assert result["schema"] == "ae.scope_export.v1"
        assert result["n_beliefs"] == 2
        assert result["n_scope_specified"] == 1
        assert result["n_with_population"] == 1
        assert result["scope_coverage"] == 0.5


class TestTemporalExport:
    """Test temporal expression serialization (TD-D)."""

    def test_serialize_temporal_expressions(self):
        """Should serialize temporal extractions."""
        from src.services.output_serializer import serialize_temporal_expressions

        claims = [
            {
                "claim_id": "c1",
                "temporal": {
                    "duration_minutes": 30,
                    "duration_text": "30 minutes",
                    "exposure_type": "acute",
                }
            },
            {
                "claim_id": "c2",
                "temporal": {
                    "duration_minutes": 10080,  # 1 week
                    "exposure_type": "chronic",
                    "frequency": "daily",
                    "frequency_per_week": 7,
                }
            }
        ]

        result = serialize_temporal_expressions(claims, "run-1", "paper:001")

        assert result["schema"] == "ae.temporal_export.v1"
        assert result["n_claims"] == 2
        assert result["n_with_duration"] == 2
        assert result["n_with_frequency"] == 1
        assert "acute" in result["exposure_type_distribution"]
        assert "chronic" in result["exposure_type_distribution"]


class TestClusterStatsExport:
    """Test cluster statistics serialization (TD-C)."""

    def test_serialize_cluster_stats_none(self):
        """Should handle None coherence manager."""
        from src.services.output_serializer import serialize_cluster_stats

        result = serialize_cluster_stats(None, "run-1", "paper:001")

        assert result["schema"] == "ae.cluster_stats.v1"
        assert result["available"] is False
        assert "reason" in result

    def test_serialize_cluster_stats_with_manager(self):
        """Should serialize real cluster stats."""
        from src.services.output_serializer import serialize_cluster_stats
        from src.services.scalable_coherence import CoherenceManager

        manager = CoherenceManager()
        manager.on_belief_added("b1", "ART", "empirical", "cog")
        manager.on_belief_added("b2", "ART", "empirical", "cog")
        manager.on_constraint_added("c1", "b1", "b2", "supports", 0.8)

        result = serialize_cluster_stats(manager, "run-1", "paper:001")

        assert result["schema"] == "ae.cluster_stats.v1"
        assert result["available"] is True
        assert "network" in result
        assert "clusters_summary" in result
        assert "cache" in result


class TestBNEdgesExport:
    """Test BN edge serialization (TD-E)."""

    def test_serialize_bn_edges_none(self):
        """Should handle None BN builder."""
        from src.services.output_serializer import serialize_bn_edges

        result = serialize_bn_edges(None, "run-1", "paper:001")

        assert result["schema"] == "ae.bn_edges.v1"
        assert result["available"] is False

    def test_serialize_bn_edges_with_builder(self):
        """Should serialize BN edges with uncertainty."""
        from src.services.output_serializer import serialize_bn_edges
        from src.services.incremental_bn import IncrementalBNBuilder

        builder = IncrementalBNBuilder()
        builder.observe_evidence("nature", "stress", True, 0.8, "paper1")
        builder.observe_evidence("nature", "stress", True, 0.7, "paper2")
        builder.observe_evidence("plants", "attention", True, 0.6)

        result = serialize_bn_edges(builder, "run-1", "paper:001")

        assert result["schema"] == "ae.bn_edges.v1"
        assert result["available"] is True
        assert result["n_edges"] == 2
        assert len(result["edges"]) == 2

        # Check edge details
        nature_stress = [e for e in result["edges"] if e["source"] == "nature"][0]
        assert nature_stress["n_papers"] == 2
        assert "ci_95_lower" in nature_stress
        assert "ci_95_upper" in nature_stress
        assert "uncertainty" in nature_stress


class TestEnhancedBeliefSerialization:
    """Test enhanced belief serialization."""

    def test_serialize_belief_minimal(self):
        """Should serialize belief with minimal fields."""
        from src.services.output_serializer import serialize_belief_enhanced
        from src.services.web_of_belief import Belief, Credence, EpistemicLevel

        belief = Belief(
            belief_id="b1",
            content="Test belief",
            level=EpistemicLevel.EMPIRICAL,
            credence=Credence(value=0.7, uncertainty=0.1),
        )

        result = serialize_belief_enhanced(belief)

        assert result["belief_id"] == "b1"
        assert result["content"] == "Test belief"
        assert result["level"] == "empirical"
        # Credence.to_dict() uses 'credence' not 'value' for the value field
        assert result["credence"]["credence"] == 0.7 or result["credence"]["value"] == 0.7

    def test_serialize_belief_with_mapping_result(self):
        """Should include mapping result details."""
        from src.services.output_serializer import serialize_belief_enhanced
        from src.services.web_of_belief import Belief, Credence, EpistemicLevel

        belief = Belief(
            belief_id="b1",
            content="Test belief",
            level=EpistemicLevel.EMPIRICAL,
            credence=Credence(value=0.7, uncertainty=0.1),
            theory_id="ART",
        )

        mapping_result = {
            "theory_inference_method": "embedding",
            "theory_confidence": 0.85,
            "theory_ids": {"ART": 0.8, "SRT": 0.2},
            "needs_theory_review": False,
            "inference_basis": "stated",
            "review_recommended": False,
            "mechanism_only": False,
        }

        result = serialize_belief_enhanced(belief, mapping_result)

        assert "theory_inference" in result
        assert result["theory_inference"]["method"] == "embedding"
        assert result["theory_inference"]["confidence"] == 0.85
        assert "task_context" in result
        assert result["task_context"]["inference_basis"] == "stated"


class TestPipelineIntegration:
    """Test integration with pipeline."""

    def test_output_serializer_available(self):
        """Output serializer should be available in pipeline."""
        from app.tasks.pipeline import OUTPUT_SERIALIZER_AVAILABLE
        assert OUTPUT_SERIALIZER_AVAILABLE is True

    def test_serialize_functions_available(self):
        """All serialize functions should be importable."""
        from app.tasks.pipeline import (
            serialize_theory_inference,
            serialize_cluster_stats,
            serialize_bn_edges,
            generate_manifest,
            OutputFile,
            SCHEMA_VERSIONS,
        )

        assert serialize_theory_inference is not None
        assert serialize_cluster_stats is not None
        assert serialize_bn_edges is not None
        assert generate_manifest is not None
        assert OutputFile is not None
        assert SCHEMA_VERSIONS is not None


class TestUtilityFunctions:
    """Test utility functions."""

    def test_write_json(self):
        """Should write JSON with consistent formatting."""
        from src.services.output_serializer import write_json

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.json"
            write_json(path, {"key": "value", "number": 42})

            content = path.read_text()
            assert '"key": "value"' in content
            assert '"number": 42' in content

    def test_write_jsonl(self):
        """Should write JSONL records."""
        from src.services.output_serializer import write_jsonl

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.jsonl"
            count = write_jsonl(path, [
                {"id": 1, "name": "a"},
                {"id": 2, "name": "b"},
            ])

            assert count == 2
            lines = path.read_text().strip().split("\n")
            assert len(lines) == 2
            assert json.loads(lines[0])["id"] == 1

    def test_verify_outputs(self):
        """Should verify outputs against manifest."""
        from src.services.output_serializer import (
            write_json, generate_manifest, verify_outputs, OutputFile
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            out_dir = Path(tmpdir)

            # Create test files
            write_json(out_dir / "test.json", {"test": True})

            outputs = {
                "test": OutputFile(
                    filename="test.json",
                    schema="ae.test.v1",
                    description="Test file",
                    record_count=1
                )
            }

            manifest = generate_manifest(out_dir, "run-1", "paper:001", outputs)
            write_json(out_dir / "manifest.json", manifest)

            # Verify
            results = verify_outputs(out_dir)
            assert results["manifest_exists"] is True
            assert results["test.json"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
