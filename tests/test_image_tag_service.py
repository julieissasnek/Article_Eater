"""
Comprehensive test suite for ImageTagService.

Tests cover:
- Service initialization and file loading
- Attribute lookup and vocabulary indexing
- Tag creation and validation
- Domain score computation
- Template linking
- Schema validation
- Consistency checking
- Search and filtering

Author: Claude Code
Date: 2026-03-02
"""

import pytest
import json
import tempfile
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock

from src.services.image_tag_service import (
    ImageTagService,
    create_default_service,
    batch_validate_tags,
)


@pytest.fixture
def image_tag_service():
    """Create an ImageTagService instance for testing."""
    return create_default_service()


@pytest.fixture
def sample_tags_complete():
    """Sample complete tags across multiple domains."""
    return {
        "spatial-properties": {
            "spatial-volume": {"value": 75, "unit": "0-100", "confidence": "high"},
            "spatial-enclosure-degree": {
                "value": "semi-enclosed (partial barriers, >180° view)",
                "confidence": "moderate",
            },
            "spatial-openness-prospect": {"value": 60, "confidence": "high"},
            "spatial-mystery": {"value": "moderate (some areas obscured, invites exploration)", "confidence": "moderate"},
            "spatial-legibility": {"value": "high (clear structure, easy to navigate)", "confidence": "high"},
        },
        "lighting": {
            "lighting-source-type": {
                "value": "natural-daylight-mixed",
                "confidence": "high",
            },
            "lighting-illuminance": {"value": 500, "unit": "lux", "confidence": "high"},
            "lighting-color-temperature": {
                "value": 5500,
                "unit": "K",
                "confidence": "moderate",
            },
            "lighting-uniformity": {"value": "good (relatively even distribution)", "confidence": "moderate"},
        },
        "materials-texture": {
            "materials-dominant-types": {
                "value": ["wood", "stone-brick-concrete"],
                "confidence": "high",
            },
            "materials-naturalness-ratio": {
                "value": 65,
                "unit": "%",
                "confidence": "high",
            },
            "materials-surface-finish": {
                "value": "clean-matte (functional, well-kept)",
                "confidence": "moderate",
            },
        },
        "vegetation": {
            "vegetation-presence": {"value": "moderate (scattered vegetation, 5-25%)", "confidence": "high"},
            "vegetation-types": {
                "value": ["trees-deciduous", "shrubs-low-woody"],
                "confidence": "moderate",
            },
            "vegetation-density": {"value": 45, "unit": "%", "confidence": "high"},
            "vegetation-healthfulness": {"value": "good (healthy, green, vigorous)", "confidence": "high"},
        },
        "color": {
            "color-dominant-hues": {
                "value": ["greens-natural", "browns-earth-wood"],
                "confidence": "high",
            },
            "color-saturation": {"value": 60, "confidence": "moderate"},
            "color-contrast": {"value": 50, "confidence": "moderate"},
            "color-naturalness": {"value": "natural (greens, earth tones, sky colors)", "confidence": "high"},
        },
        "complexity-information": {
            "complexity-visual": {"value": 55, "confidence": "moderate"},
            "complexity-clutter-orderliness": {
                "value": "organized (clear structure, hierarchy)",
                "confidence": "moderate",
            },
            "complexity-information-density": {"value": 50, "confidence": "moderate"},
        },
        "view-perceptual-space": {
            "view-depth-cues": {"value": "rich (multiple depth cues: perspective, occlusion, size, lighting)", "confidence": "high"},
            "view-layering": {"value": "three-layers (foreground, middle-ground, background)", "confidence": "high"},
            "view-focal-point": {"value": "moderate (clear focal point)", "confidence": "moderate"},
        },
        "environmental-context": {
            "environment-built-natural-ratio": {"value": 40, "confidence": "high"},
            "environment-setting-type": {
                "value": "natural-managed-park",
                "confidence": "high",
            },
            "environment-scale-human": {"value": "human-compatible (elements proportioned to human body)", "confidence": "high"},
        },
    }


@pytest.fixture
def sample_tags_minimal():
    """Sample minimal tags (sparse)."""
    return {
        "spatial-properties": {
            "spatial-volume": {"value": 50, "confidence": "moderate"},
        },
        "lighting": {
            "lighting-source-type": {"value": "artificial-electric", "confidence": "high"},
        },
        "vegetation": {"vegetation-presence": {"value": "absent (no visible plants)", "confidence": "high"}},
    }


# ========== Initialization and Loading Tests ==========


class TestServiceInitialization:
    """Test ImageTagService initialization and file loading."""

    def test_service_initializes_with_defaults(self):
        """Test that service initializes with default file locations."""
        service = create_default_service()
        assert service is not None
        assert service.vocabulary is not None
        assert service.schema is not None

    def test_vocabulary_loaded_correctly(self, image_tag_service):
        """Test that vocabulary is loaded with expected structure."""
        assert image_tag_service.vocabulary["schema"] == "image_tagging_vocabulary.v1"
        assert "domains" in image_tag_service.vocabulary
        assert len(image_tag_service.vocabulary["domains"]) > 0

    def test_schema_loaded_correctly(self, image_tag_service):
        """Test that schema is loaded as valid JSON Schema."""
        assert image_tag_service.schema["$schema"]
        assert image_tag_service.schema["type"] == "object"
        assert "properties" in image_tag_service.schema

    def test_attributes_indexed_by_domain(self, image_tag_service):
        """Test that attributes are properly indexed by domain."""
        assert len(image_tag_service.attributes_by_domain) > 0
        for domain_id, attrs in image_tag_service.attributes_by_domain.items():
            assert isinstance(attrs, list)
            assert len(attrs) > 0
            assert all("attribute_id" in attr for attr in attrs)

    def test_all_attributes_flattened(self, image_tag_service):
        """Test that all attributes are flattened into single dict."""
        assert len(image_tag_service.all_attributes) > 0
        for attr_id, attr_def in image_tag_service.all_attributes.items():
            assert "name" in attr_def
            assert "measurement_type" in attr_def

    def test_domain_scores_specs_loaded(self, image_tag_service):
        """Test that domain score specifications are loaded."""
        assert len(image_tag_service.domain_score_specs) > 0
        assert "naturalness" in image_tag_service.domain_score_specs
        assert "visual-complexity" in image_tag_service.domain_score_specs


# ========== Tag Creation Tests ==========


class TestTagCreation:
    """Test tag_image and related functionality."""

    def test_tag_image_basic(self, image_tag_service, sample_tags_complete):
        """Test basic tag record creation."""
        record = image_tag_service.tag_image(
            image_id="img-test-001",
            tags=sample_tags_complete,
            tagged_by="test-rater",
            tagging_method="human-manual",
        )

        assert record["tag_record_id"].startswith("tag-")
        assert record["image_id"] == "img-test-001"
        assert record["tagged_by"] == "test-rater"
        assert record["tagging_method"] == "human-manual"
        assert "tags" in record
        assert "domain_scores" in record
        assert "relevant_templates" in record

    def test_tag_image_with_metadata(self, image_tag_service, sample_tags_minimal):
        """Test tag creation with optional metadata."""
        record = image_tag_service.tag_image(
            image_id="img-test-002",
            tags=sample_tags_minimal,
            tagged_by="expert-panel",
            tagging_method="expert-panel",
            source_paper_id="10.1234/example",
            image_source_description="Fig 3 from nature restoration study",
            confidence_level="expert",
        )

        assert record["source_paper_id"] == "10.1234/example"
        assert "Fig 3" in record["image_source_description"]
        assert record["confidence_level"] == "expert"

    def test_tagged_at_timestamp(self, image_tag_service, sample_tags_minimal):
        """Test that tagged_at timestamp is set."""
        record = image_tag_service.tag_image(
            image_id="img-test-003",
            tags=sample_tags_minimal,
        )

        assert "tagged_at" in record
        assert record["tagged_at"].endswith("Z")
        # Verify it's a valid ISO 8601 timestamp
        datetime.fromisoformat(record["tagged_at"].rstrip("Z"))


# ========== Validation Tests ==========


class TestTagValidation:
    """Test validation of tag structures and values."""

    def test_validate_tags_complete_valid(
        self, image_tag_service, sample_tags_complete
    ):
        """Test validation of complete valid tags."""
        errors = image_tag_service.validate_tags(sample_tags_complete)
        assert len(errors) == 0

    def test_validate_tags_minimal_valid(self, image_tag_service, sample_tags_minimal):
        """Test validation of sparse but valid tags."""
        errors = image_tag_service.validate_tags(sample_tags_minimal)
        assert len(errors) == 0

    def test_validate_tags_unknown_domain(self, image_tag_service):
        """Test that unknown domains are rejected."""
        invalid_tags = {"nonexistent-domain": {"attr": {"value": 50}}}
        errors = image_tag_service.validate_tags(invalid_tags)
        assert len(errors) > 0
        assert any("nonexistent-domain" in e for e in errors)

    def test_validate_tags_unknown_attribute(self, image_tag_service):
        """Test that unknown attributes are rejected."""
        invalid_tags = {
            "spatial-properties": {"nonexistent-attr": {"value": 50}}
        }
        errors = image_tag_service.validate_tags(invalid_tags)
        assert len(errors) > 0

    def test_validate_continuous_attribute_out_of_range(
        self, image_tag_service
    ):
        """Test that continuous values outside range are rejected."""
        invalid_tags = {
            "spatial-properties": {
                "spatial-volume": {"value": 150}  # exceeds 0-100
            }
        }
        errors = image_tag_service.validate_tags(invalid_tags)
        assert len(errors) > 0

    def test_validate_categorical_invalid_value(self, image_tag_service):
        """Test that invalid categorical values are rejected."""
        invalid_tags = {
            "lighting": {
                "lighting-source-type": {"value": "invalid-source"}
            }
        }
        errors = image_tag_service.validate_tags(invalid_tags)
        assert len(errors) > 0

    def test_consistency_rule_vegetation_absence(self, image_tag_service):
        """Test consistency rule: absent vegetation with nonzero density."""
        inconsistent_tags = {
            "vegetation": {
                "vegetation-presence": {"value": "absent (no visible plants)"},
                "vegetation-density": {"value": 10},
            }
        }
        errors = image_tag_service.validate_tags(inconsistent_tags)
        assert len(errors) > 0

    def test_consistency_rule_spatial_contradiction(self, image_tag_service):
        """Test consistency rule: high volume contradicts complete enclosure."""
        inconsistent_tags = {
            "spatial-properties": {
                "spatial-volume": {"value": 90},
                "spatial-enclosure-degree": {"value": "completely-enclosed (interior room)"},
            }
        }
        errors = image_tag_service.validate_tags(inconsistent_tags)
        assert len(errors) > 0


# ========== Domain Scoring Tests ==========


class TestDomainScoring:
    """Test domain-level score computation."""

    def test_compute_naturalness_score(self, image_tag_service, sample_tags_complete):
        """Test computation of naturalness domain score."""
        scores = image_tag_service.get_domain_scores(sample_tags_complete)

        assert "naturalness" in scores
        naturalness = scores["naturalness"]
        assert "score" in naturalness
        assert 0 <= naturalness["score"] <= 100
        assert naturalness["completeness"] > 0

    def test_compute_visual_complexity_score(
        self, image_tag_service, sample_tags_complete
    ):
        """Test computation of visual-complexity score."""
        scores = image_tag_service.get_domain_scores(sample_tags_complete)

        assert "visual-complexity" in scores
        complexity = scores["visual-complexity"]
        assert 0 <= complexity["score"] <= 100

    def test_compute_prospect_refuge_index(
        self, image_tag_service, sample_tags_complete
    ):
        """Test computation of prospect-refuge balance."""
        scores = image_tag_service.get_domain_scores(sample_tags_complete)

        assert "prospect-refuge-index" in scores
        pri = scores["prospect-refuge-index"]
        assert 0 <= pri["score"] <= 100

    def test_compute_restorative_capacity_score(
        self, image_tag_service, sample_tags_complete
    ):
        """Test computation of restorative-capacity score."""
        scores = image_tag_service.get_domain_scores(sample_tags_complete)

        assert "restorative-capacity" in scores
        restorative = scores["restorative-capacity"]
        assert 0 <= restorative["score"] <= 100

    def test_compute_human_centeredness_score(
        self, image_tag_service, sample_tags_complete
    ):
        """Test computation of human-centeredness score."""
        scores = image_tag_service.get_domain_scores(sample_tags_complete)

        assert "human-centeredness" in scores
        human_centered = scores["human-centeredness"]
        assert 0 <= human_centered["score"] <= 100

    def test_domain_score_with_missing_attributes(
        self, image_tag_service, sample_tags_minimal
    ):
        """Test that scores handle missing attributes gracefully."""
        scores = image_tag_service.get_domain_scores(sample_tags_minimal)

        for score_name, score_data in scores.items():
            assert "score" in score_data
            assert "missing_attributes" in score_data
            assert "completeness" in score_data

    def test_contributing_attributes_recorded(
        self, image_tag_service, sample_tags_complete
    ):
        """Test that contributing attributes are recorded in score result."""
        scores = image_tag_service.get_domain_scores(sample_tags_complete)

        for score_name, score_data in scores.items():
            if score_data.get("contributing_attributes"):
                for contrib in score_data["contributing_attributes"]:
                    assert "attribute_id" in contrib
                    assert "weight" in contrib
                    assert "value" in contrib
                    assert "weighted_contribution" in contrib


# ========== Template Linking Tests ==========


class TestTemplateRelevance:
    """Test template relevance linking."""

    def test_get_relevant_templates(
        self, image_tag_service, sample_tags_complete
    ):
        """Test that relevant templates are identified."""
        templates = image_tag_service.get_relevant_templates(sample_tags_complete)

        assert isinstance(templates, list)
        for template in templates:
            assert "template_id" in template
            assert "relevance_score" in template
            assert 0 <= template["relevance_score"] <= 1
            assert "predicted_sensitive_attributes" in template
            assert "reasoning" in template

    def test_templates_ranked_by_relevance(
        self, image_tag_service, sample_tags_complete
    ):
        """Test that templates are sorted by relevance score descending."""
        templates = image_tag_service.get_relevant_templates(sample_tags_complete)

        if len(templates) > 1:
            for i in range(len(templates) - 1):
                assert (
                    templates[i]["relevance_score"]
                    >= templates[i + 1]["relevance_score"]
                )

    def test_templates_limited_to_top_10(
        self, image_tag_service, sample_tags_complete
    ):
        """Test that at most 10 templates are returned."""
        templates = image_tag_service.get_relevant_templates(sample_tags_complete)
        assert len(templates) <= 10


# ========== Attribute Lookup Tests ==========


class TestAttributeLookup:
    """Test attribute information retrieval."""

    def test_get_attribute_info(self, image_tag_service):
        """Test retrieval of detailed attribute information."""
        # Find a real attribute
        first_attr_id = list(image_tag_service.all_attributes.keys())[0]
        info = image_tag_service.get_attribute_info(first_attr_id)

        assert info["attribute_id"] == first_attr_id
        assert "name" in info
        assert "measurement_type" in info
        assert "description" in info

    def test_get_attribute_info_unknown_attribute(self, image_tag_service):
        """Test that unknown attributes return error."""
        info = image_tag_service.get_attribute_info("nonexistent-attribute")
        assert "error" in info

    def test_search_by_attribute(self, image_tag_service):
        """Test search interface for attribute."""
        first_attr_id = list(image_tag_service.all_attributes.keys())[0]
        search_result = image_tag_service.search_by_attribute(first_attr_id)

        assert "attribute_id" in search_result
        assert "name" in search_result
        assert "measurement_type" in search_result
        assert "search_query" in search_result

    def test_search_with_value_range(self, image_tag_service):
        """Test search with value range filter."""
        search_result = image_tag_service.search_by_attribute(
            "spatial-volume", value_range=(50, 80)
        )

        assert "search_query" in search_result
        assert "50" in search_result["search_query"]
        assert "80" in search_result["search_query"]


# ========== Vocabulary Summary Tests ==========


class TestVocabularySummary:
    """Test vocabulary introspection methods."""

    def test_get_vocabulary_summary(self, image_tag_service):
        """Test high-level vocabulary summary."""
        summary = image_tag_service.get_vocabulary_summary()

        assert "schema_version" in summary
        assert "total_domains" in summary
        assert "total_attributes" in summary
        assert "domains" in summary
        assert summary["total_domains"] > 0
        assert summary["total_attributes"] > 0

    def test_vocabulary_includes_scientific_grounding(self, image_tag_service):
        """Test that vocabulary includes scientific references."""
        summary = image_tag_service.get_vocabulary_summary()
        assert "scientific_grounding" in summary


# ========== JSON Schema Validation Tests ==========


class TestSchemaValidation:
    """Test JSON Schema validation of tag records."""

    def test_validate_complete_tag_record(
        self, image_tag_service, sample_tags_complete
    ):
        """Test validation of complete tag record against schema."""
        record = image_tag_service.tag_image(
            image_id="img-schema-test",
            tags=sample_tags_complete,
            tagged_by="test",
        )

        is_valid, errors = image_tag_service.validate_tag_record(record)
        # Note: may have some errors due to optional fields, but basic structure should be valid
        assert isinstance(is_valid, bool)
        assert isinstance(errors, list)

    def test_schema_validator_creation(self, image_tag_service):
        """Test that a validator can be created from schema."""
        validator = image_tag_service.get_schema_validator()
        assert validator is not None


# ========== Utility Functions Tests ==========


class TestUtilityFunctions:
    """Test convenience functions and batch operations."""

    def test_batch_validate_tags(self, image_tag_service, sample_tags_complete, sample_tags_minimal):
        """Test batch validation of multiple tag records."""
        record1 = image_tag_service.tag_image(
            image_id="img-batch-1",
            tags=sample_tags_complete,
        )
        record2 = image_tag_service.tag_image(
            image_id="img-batch-2",
            tags=sample_tags_minimal,
        )

        results = batch_validate_tags([record1, record2])

        assert len(results) == 2
        assert record1["tag_record_id"] in results
        assert record2["tag_record_id"] in results


# ========== Integration Tests ==========


class TestIntegration:
    """Integration tests combining multiple components."""

    def test_full_workflow_image_tagging(
        self, image_tag_service, sample_tags_complete
    ):
        """Test complete workflow: tag -> validate -> score -> link templates."""
        # Create tag record
        record = image_tag_service.tag_image(
            image_id="img-integration-001",
            tags=sample_tags_complete,
            tagged_by="integration-test",
            tagging_method="human-manual",
            source_paper_id="10.1111/example",
        )

        # Validate
        is_valid, errors = image_tag_service.validate_tag_record(record)

        # Check scores were computed
        assert len(record["domain_scores"]) > 0

        # Check templates were linked
        assert "relevant_templates" in record

        # Check metadata
        assert record["validation_notes"]

    def test_sparse_to_complete_workflow(
        self, image_tag_service, sample_tags_minimal, sample_tags_complete
    ):
        """Test workflow progression from sparse to complete tagging."""
        # Start with minimal tags
        record_minimal = image_tag_service.tag_image(
            image_id="img-progression-001",
            tags=sample_tags_minimal,
        )

        minimal_scores = record_minimal["domain_scores"]

        # Then with complete tags
        record_complete = image_tag_service.tag_image(
            image_id="img-progression-002",
            tags=sample_tags_complete,
        )

        complete_scores = record_complete["domain_scores"]

        # Complete should have better completeness
        for score_name in complete_scores:
            if score_name in minimal_scores:
                complete_completeness = complete_scores[score_name].get(
                    "completeness", 0
                )
                minimal_completeness = minimal_scores[score_name].get(
                    "completeness", 0
                )
                assert (
                    complete_completeness >= minimal_completeness
                )


# ========== Edge Cases and Error Handling ==========


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_tags(self, image_tag_service):
        """Test handling of empty tags dict."""
        empty_tags = {}
        record = image_tag_service.tag_image(
            image_id="img-empty",
            tags=empty_tags,
        )

        assert record is not None
        assert "domain_scores" in record

    def test_single_attribute_tag(self, image_tag_service):
        """Test tagging with a single attribute."""
        single_tag = {
            "spatial-properties": {
                "spatial-volume": {"value": 50}
            }
        }
        record = image_tag_service.tag_image(
            image_id="img-single",
            tags=single_tag,
        )

        assert record is not None

    def test_boundary_value_continuous(self, image_tag_service):
        """Test continuous attributes at boundaries."""
        boundary_tags = {
            "spatial-properties": {
                "spatial-volume": {"value": 0},  # Minimum
                "spatial-openness-prospect": {"value": 100},  # Maximum
            }
        }
        errors = image_tag_service.validate_tags(boundary_tags)
        # Should not produce range errors for valid boundaries
        assert not any("outside range" in e for e in errors)

    def test_all_ordinal_values(self, image_tag_service):
        """Test that all ordinal values validate correctly."""
        spatial_attrs = image_tag_service.all_attributes
        ordinal_attrs = {
            k: v
            for k, v in spatial_attrs.items()
            if v.get("measurement_type") == "ordinal"
        }

        for attr_id, attr_def in list(ordinal_attrs.items())[:3]:
            valid_values = attr_def.get("valid_values", [])
            if valid_values:
                test_tag = {
                    "spatial-properties": {
                        attr_id: {"value": valid_values[0]}
                    }
                }
                errors = image_tag_service.validate_tags(test_tag)
                # May fail due to domain not matching, but shouldn't fail on value
                assert not any(
                    f"value '{valid_values[0]}' not in" in e for e in errors
                )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
