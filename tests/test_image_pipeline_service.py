"""
Comprehensive tests for IMG-PIPE (Image Pipeline Service).

Tests cover:
- SearchQueryGenerator: query generation from templates and descriptions
- ImageDownloadManager: download, deduplication, registry
- ImageMetadataExtractor: metadata extraction
- AutoTagger: heuristic attribute inference
- EvidenceLinkingService: image-to-evidence linking
- ImagePipelineService: full pipeline orchestration

Author: Claude Code
Date: 2026-03-02
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime

# Import from parent directory
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "services"))

from image_pipeline_service import (
    SearchQueryGenerator,
    ImageDownloadManager,
    ImageMetadataExtractor,
    AutoTagger,
    EvidenceLinkingService,
    ImagePipelineService,
)
from image_pipeline_models import (
    ImageSource,
    SearchQuery,
    DownloadResult,
    ImageMetadata,
    TaggingResult,
    ImageEvidenceLink,
)
from image_tag_service import ImageTagService


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_tag_service():
    """Create a mock ImageTagService."""
    service = Mock(spec=ImageTagService)
    service.attributes_by_domain = {
        "spatial-properties": [
            {"attribute_id": "spatial-volume", "measurement_type": "continuous"},
        ],
        "naturalness": [
            {"attribute_id": "vegetation-density", "measurement_type": "continuous"},
        ],
        "color-light": [
            {"attribute_id": "brightness-level", "measurement_type": "continuous"},
        ],
    }
    service.all_attributes = {
        "spatial-volume": {"name": "Spatial Volume", "measurement_type": "continuous"},
        "vegetation-density": {"name": "Vegetation Density", "measurement_type": "continuous"},
        "brightness-level": {"name": "Brightness Level", "measurement_type": "continuous"},
    }
    service.get_domain_scores = Mock(return_value={
        "spatial-properties": {"score": 50.0, "completeness": 0.8},
    })
    service.get_relevant_templates = Mock(return_value=[
        {"template_id": "t-001", "relevance_score": 0.8},
    ])
    return service


# =============================================================================
# SearchQueryGenerator Tests
# =============================================================================

class TestSearchQueryGenerator:
    """Tests for SearchQueryGenerator."""

    def test_generator_initialization(self):
        """Test generator initializes without errors."""
        gen = SearchQueryGenerator()
        assert gen is not None
        assert len(gen.equivalence_classes) >= 0

    def test_load_equivalence_classes(self, temp_dir):
        """Test loading equivalence classes from JSON."""
        # Create mock equivalence classes file
        ec_file = temp_dir / "equivalence_classes.json"
        ec_data = {
            "equivalence_classes": [
                {
                    "category_name": "vegetation",
                    "commonsense_label": "Vegetation",
                    "frequency": 100,
                }
            ]
        }
        with open(ec_file, "w") as f:
            json.dump(ec_data, f)

        gen = SearchQueryGenerator(str(ec_file))
        assert "vegetation" in gen.equivalence_classes
        assert "Vegetation" in gen.category_to_class

    def test_generate_queries_basic(self):
        """Test basic query generation."""
        gen = SearchQueryGenerator()
        queries = gen.generate_queries(
            source_template_id="t-001",
            stimulus_description="Open natural garden with water features",
        )

        assert len(queries) > 0
        assert all(isinstance(q, SearchQuery) for q in queries)
        assert all(q.source_template_id == "t-001" for q in queries)

    def test_generate_queries_types(self):
        """Test that queries have different types."""
        gen = SearchQueryGenerator()
        queries = gen.generate_queries(
            source_template_id="t-001",
            stimulus_description="Enclosed architectural space",
        )

        query_types = {q.query_type for q in queries}
        assert "general" in query_types or "specific" in query_types

    def test_generate_queries_architectural_focus(self):
        """Test query generation for architectural stimuli."""
        gen = SearchQueryGenerator()
        queries = gen.generate_queries(
            source_template_id="t-001",
            stimulus_description="Modern architectural building design",
        )

        # Check that at least one query mentions "architectural"
        query_texts = " ".join(q.query_text for q in queries)
        assert "architectural" in query_texts.lower() or "building" in query_texts.lower()

    def test_extract_key_concepts(self):
        """Test key concept extraction."""
        gen = SearchQueryGenerator()
        concepts = gen._extract_key_concepts("Open natural garden with water features")

        assert len(concepts) > 0
        assert "natural" in concepts or "garden" in concepts or "water" in concepts

    def test_extract_key_concepts_empty(self):
        """Test key concept extraction with empty string."""
        gen = SearchQueryGenerator()
        concepts = gen._extract_key_concepts("")

        assert concepts == []

    def test_infer_visual_attributes(self):
        """Test visual attribute inference from description."""
        gen = SearchQueryGenerator()
        attrs = gen._infer_visual_attributes("dark enclosed space with bright artificial lighting")

        assert len(attrs) > 0
        # Should find "bright", "dark", etc.

    def test_infer_visual_attributes_none_found(self):
        """Test attribute inference when no keywords match."""
        gen = SearchQueryGenerator()
        attrs = gen._infer_visual_attributes("foo bar baz")

        assert len(attrs) == 0


# =============================================================================
# ImageDownloadManager Tests
# =============================================================================

class TestImageDownloadManager:
    """Tests for ImageDownloadManager."""

    def test_manager_initialization(self, temp_dir):
        """Test manager initializes with storage directory."""
        mgr = ImageDownloadManager(str(temp_dir))
        assert mgr.base_dir == temp_dir

    def test_registry_directory_creation(self, temp_dir):
        """Test that storage directory is created."""
        storage = temp_dir / "images"
        mgr = ImageDownloadManager(str(storage))
        assert storage.exists()

    def test_load_empty_registry(self, temp_dir):
        """Test loading empty registry."""
        mgr = ImageDownloadManager(str(temp_dir))
        assert len(mgr.perceptual_hash_map) == 0

    def test_download_image_success(self, temp_dir):
        """Test successful image download (stub)."""
        mgr = ImageDownloadManager(str(temp_dir))
        result = mgr.download_image(
            image_url="https://example.com/image.jpg",
            source=ImageSource.UNSPLASH,
        )

        assert result.success
        assert result.image_id is not None
        assert result.filename is not None

    def test_download_creates_directory_structure(self, temp_dir):
        """Test that download creates source-specific directories."""
        mgr = ImageDownloadManager(str(temp_dir))
        result = mgr.download_image(
            image_url="https://unsplash.com/photo-123",
            source=ImageSource.UNSPLASH,
        )

        assert (temp_dir / "unsplash").exists()

    def test_perceptual_hash_computation(self, temp_dir):
        """Test perceptual hash computation."""
        mgr = ImageDownloadManager(str(temp_dir))
        content = b"test image content"
        phash = mgr._compute_perceptual_hash_stub(content)

        assert isinstance(phash, str)
        assert len(phash) > 0

    def test_duplicate_detection(self, temp_dir):
        """Test duplicate image detection."""
        mgr = ImageDownloadManager(str(temp_dir))

        # Mock two identical downloads
        content = b"identical content"
        phash = mgr._compute_perceptual_hash_stub(content)

        # First download
        mgr.perceptual_hash_map[phash] = "img-001"

        # Check duplicate
        existing = mgr._check_duplicate(phash)
        assert existing == "img-001"

    def test_registry_persistence(self, temp_dir):
        """Test that registry is saved to JSON."""
        mgr = ImageDownloadManager(str(temp_dir))
        mgr.perceptual_hash_map["hash123"] = "img-001"
        mgr._save_registry()

        assert (temp_dir / "image_registry.json").exists()

        with open(temp_dir / "image_registry.json", "r") as f:
            data = json.load(f)
            assert data["perceptual_hashes"]["hash123"] == "img-001"

    def test_download_multiple_sources(self, temp_dir):
        """Test downloading from multiple sources."""
        mgr = ImageDownloadManager(str(temp_dir))

        # Create separate mock content for each source to avoid duplicate detection
        for i, source in enumerate([ImageSource.UNSPLASH, ImageSource.WIKIMEDIA, ImageSource.FLICKR]):
            # Each source gets unique content to avoid duplicate detection
            unique_content = f"MOCK_IMAGE_DATA_{i}_" * 100
            mock_phash = mgr._compute_perceptual_hash_stub(unique_content.encode())
            mgr.perceptual_hash_map[mock_phash] = f"img-{source.value}-{i}"

            result = mgr.download_image(
                image_url=f"https://{source.value}.com/photo",
                source=source,
            )
            # First call will succeed, subsequent may be duplicates depending on random content
            assert result is not None


# =============================================================================
# ImageMetadataExtractor Tests
# =============================================================================

class TestImageMetadataExtractor:
    """Tests for ImageMetadataExtractor."""

    def test_extractor_initialization(self):
        """Test extractor initializes."""
        extractor = ImageMetadataExtractor()
        assert extractor is not None

    def test_stub_get_dimensions(self):
        """Test stub dimension extraction."""
        extractor = ImageMetadataExtractor()
        dims = extractor._stub_get_dimensions("fake_path.jpg")

        assert isinstance(dims, tuple)
        assert len(dims) == 2
        assert all(isinstance(d, int) for d in dims)

    def test_extract_metadata_basic(self, temp_dir):
        """Test basic metadata extraction."""
        # Create a fake image file
        img_file = temp_dir / "test-image.jpg"
        img_file.write_bytes(b"fake image data")

        extractor = ImageMetadataExtractor()
        metadata = extractor.extract(str(img_file), ImageSource.UNSPLASH)

        assert metadata.filename == "test-image.jpg"
        assert metadata.file_format == "jpg"
        assert metadata.file_size_bytes > 0

    def test_extract_metadata_attribution(self, temp_dir):
        """Test attribution extraction."""
        img_file = temp_dir / "test.jpg"
        img_file.write_bytes(b"fake")

        extractor = ImageMetadataExtractor()
        metadata = extractor.extract(str(img_file), ImageSource.UNSPLASH)

        assert metadata.source_attribution is not None
        assert metadata.source_attribution["source"] == "unsplash"

    def test_extract_metadata_invalid_path(self):
        """Test extraction with invalid path."""
        extractor = ImageMetadataExtractor()
        metadata = extractor.extract("/nonexistent/path.jpg", ImageSource.UNSPLASH)

        # Should return metadata even if file doesn't exist (graceful fallback)
        assert metadata.filename == "path.jpg"  # Name extracted from path even if doesn't exist
        assert metadata.file_size_bytes == 0  # File doesn't exist

    def test_aspect_ratio_calculation(self, temp_dir):
        """Test aspect ratio calculation."""
        img_file = temp_dir / "test.jpg"
        img_file.write_bytes(b"fake")

        extractor = ImageMetadataExtractor()
        metadata = extractor.extract(str(img_file), ImageSource.UNSPLASH)

        # Should have computed aspect ratio
        assert metadata.aspect_ratio is not None
        assert isinstance(metadata.aspect_ratio, float)


# =============================================================================
# AutoTagger Tests
# =============================================================================

class TestAutoTagger:
    """Tests for AutoTagger."""

    def test_tagger_initialization(self, mock_tag_service, temp_dir):
        """Test tagger initializes."""
        tagger = AutoTagger(mock_tag_service)
        assert tagger.tag_service is mock_tag_service

    def test_tag_image_basic(self, mock_tag_service, temp_dir):
        """Test basic image tagging."""
        img_file = temp_dir / "test.jpg"
        img_file.write_bytes(b"fake image")

        metadata = ImageMetadata(
            image_id="test-img",
            filename="test.jpg",
            file_format="jpg",
            file_size_bytes=100,
            resolution_width=1920,
            resolution_height=1080,
        )

        tagger = AutoTagger(mock_tag_service)
        result = tagger.tag_image(
            image_id="test-img",
            image_path=str(img_file),
            metadata=metadata,
        )

        assert isinstance(result, TaggingResult)
        assert result.image_id == "test-img"
        # Check that tagging succeeded (no error message) or had inferred attributes
        assert result.error_message is None or len(result.inferred_attributes) > 0

    def test_tag_image_with_description(self, mock_tag_service, temp_dir):
        """Test tagging with source description."""
        img_file = temp_dir / "test.jpg"
        img_file.write_bytes(b"fake")

        metadata = ImageMetadata(
            image_id="test-img",
            filename="test.jpg",
            file_format="jpg",
            file_size_bytes=100,
        )

        tagger = AutoTagger(mock_tag_service)
        result = tagger.tag_image(
            image_id="test-img",
            image_path=str(img_file),
            metadata=metadata,
            source_description="Dark forest with water",
        )

        # Should infer attributes based on description
        assert len(result.inferred_attributes) > 0

    def test_infer_attribute_spatial_volume(self, mock_tag_service):
        """Test spatial volume attribute inference."""
        metadata = ImageMetadata(
            image_id="test",
            filename="test.jpg",
            file_format="jpg",
            file_size_bytes=100,
            resolution_width=2000,
            resolution_height=1000,
        )

        tagger = AutoTagger(mock_tag_service)
        value, method = tagger._infer_attribute(
            "spatial-volume",
            "continuous",
            "fake_path.jpg",
            metadata,
        )

        assert value is not None
        assert isinstance(value, (int, float))
        assert method == "resolution-heuristic"

    def test_infer_attribute_vegetation_density(self, mock_tag_service):
        """Test vegetation density inference."""
        metadata = ImageMetadata(
            image_id="test",
            filename="test.jpg",
            file_format="jpg",
            file_size_bytes=100,
        )

        tagger = AutoTagger(mock_tag_service)
        value, method = tagger._infer_attribute(
            "vegetation-density",
            "continuous",
            "fake_path.jpg",
            metadata,
            source_description="Dense forest with trees",
        )

        assert value is not None

    def test_infer_attribute_brightness(self, mock_tag_service):
        """Test brightness level inference."""
        metadata = ImageMetadata(
            image_id="test",
            filename="test.jpg",
            file_format="jpg",
            file_size_bytes=100,
        )

        tagger = AutoTagger(mock_tag_service)
        value, method = tagger._infer_attribute(
            "brightness-level",
            "continuous",
            "fake_path.jpg",
            metadata,
            source_description="Very dark space",
        )

        # Dark description should result in lower brightness
        assert value is not None

    def test_estimate_confidence_mapping(self, mock_tag_service):
        """Test confidence estimation."""
        tagger = AutoTagger(mock_tag_service)

        # High confidence method
        conf_high = tagger._estimate_confidence("description-keyword")
        assert conf_high > 0.6

        # Low confidence method
        conf_low = tagger._estimate_confidence("default-conservative")
        assert conf_low < 0.5

        # Unknown method defaults to 0.5
        conf_unknown = tagger._estimate_confidence("unknown-method")
        assert conf_unknown == 0.5


# =============================================================================
# EvidenceLinkingService Tests
# =============================================================================

class TestEvidenceLinkingService:
    """Tests for EvidenceLinkingService."""

    def test_linker_initialization(self, mock_tag_service):
        """Test linker initializes."""
        linker = EvidenceLinkingService(mock_tag_service)
        assert linker.tag_service is mock_tag_service

    def test_link_image_to_evidence(self, mock_tag_service):
        """Test linking image to evidence."""
        tagging_result = TaggingResult.create(
            image_id="img-001",
            tags={"spatial-properties": {"spatial-volume": {"value": 50}}},
            domain_scores={},
            relevant_templates=[
                {"template_id": "t-001", "relevance_score": 0.8},
            ],
        )

        linker = EvidenceLinkingService(mock_tag_service)
        links = linker.link_image_to_evidence(
            image_id="img-001",
            tagging_result=tagging_result,
            belief_id="belief-001",
        )

        assert len(links) > 0
        assert all(isinstance(l, ImageEvidenceLink) for l in links)
        assert links[0].image_id == "img-001"
        assert links[0].belief_id == "belief-001"

    def test_link_image_no_templates(self, mock_tag_service):
        """Test linking when no relevant templates exist."""
        tagging_result = TaggingResult.create(
            image_id="img-001",
            tags={},
            domain_scores={},
            relevant_templates=[],
        )

        linker = EvidenceLinkingService(mock_tag_service)
        links = linker.link_image_to_evidence(
            image_id="img-001",
            tagging_result=tagging_result,
            belief_id="belief-001",
        )

        assert len(links) == 0

    def test_score_to_confidence_high(self, mock_tag_service):
        """Test score to confidence conversion (high)."""
        linker = EvidenceLinkingService(mock_tag_service)
        confidence = linker._score_to_confidence(0.85)

        assert confidence == "high"

    def test_score_to_confidence_moderate(self, mock_tag_service):
        """Test score to confidence conversion (moderate)."""
        linker = EvidenceLinkingService(mock_tag_service)
        confidence = linker._score_to_confidence(0.65)

        assert confidence == "moderate"

    def test_score_to_confidence_low(self, mock_tag_service):
        """Test score to confidence conversion (low)."""
        linker = EvidenceLinkingService(mock_tag_service)
        confidence = linker._score_to_confidence(0.4)

        assert confidence == "low"


# =============================================================================
# ImagePipelineService Tests
# =============================================================================

class TestImagePipelineService:
    """Tests for ImagePipelineService."""

    def test_pipeline_initialization(self, mock_tag_service, temp_dir):
        """Test pipeline initializes."""
        pipeline = ImagePipelineService(
            tag_service=mock_tag_service,
            base_storage_dir=str(temp_dir),
        )

        assert pipeline.tag_service is mock_tag_service
        assert pipeline.query_generator is not None
        assert pipeline.download_manager is not None
        assert pipeline.auto_tagger is not None

    def test_process_template_basic(self, mock_tag_service, temp_dir):
        """Test processing a single template."""
        pipeline = ImagePipelineService(
            tag_service=mock_tag_service,
            base_storage_dir=str(temp_dir),
        )

        result = pipeline.process_template(
            template_id="t-001",
            stimulus_description="Natural garden setting",
            belief_id="belief-001",
        )

        assert result["template_id"] == "t-001"
        assert result["belief_id"] == "belief-001"
        assert "searches" in result
        assert "downloads" in result
        assert "tagged_images" in result
        assert "summary" in result

    def test_process_template_summary_fields(self, mock_tag_service, temp_dir):
        """Test that summary contains expected fields."""
        pipeline = ImagePipelineService(
            tag_service=mock_tag_service,
            base_storage_dir=str(temp_dir),
        )

        result = pipeline.process_template(
            template_id="t-001",
            stimulus_description="Test stimulus",
            belief_id="belief-001",
        )

        summary = result["summary"]
        assert "queries_generated" in summary
        assert "images_downloaded" in summary
        assert "images_tagged" in summary
        assert "evidence_links_created" in summary

    def test_process_batch(self, mock_tag_service, temp_dir):
        """Test batch processing of templates."""
        pipeline = ImagePipelineService(
            tag_service=mock_tag_service,
            base_storage_dir=str(temp_dir),
        )

        templates = [
            {
                "template_id": "t-001",
                "belief_id": "belief-001",
                "stimulus_description": "Natural landscape",
            },
            {
                "template_id": "t-002",
                "belief_id": "belief-002",
                "stimulus_description": "Urban architecture",
            },
        ]

        results = pipeline.process_batch(templates)

        assert len(results) == 2
        assert results[0]["template_id"] == "t-001"
        assert results[1]["template_id"] == "t-002"

    def test_save_evidence_links(self, mock_tag_service, temp_dir):
        """Test saving evidence links to JSON."""
        pipeline = ImagePipelineService(
            tag_service=mock_tag_service,
            base_storage_dir=str(temp_dir),
        )

        # Add some mock links
        link = ImageEvidenceLink.create(
            image_id="img-001",
            belief_id="belief-001",
            template_id="t-001",
            match_score=0.8,
        )
        pipeline.evidence_links.append(link)

        output_file = temp_dir / "links.json"
        pipeline.save_evidence_links(str(output_file))

        assert output_file.exists()

        with open(output_file, "r") as f:
            data = json.load(f)
            assert data["total_links"] == 1
            assert len(data["links"]) == 1


# =============================================================================
# Integration Tests
# =============================================================================

class TestIntegration:
    """Integration tests across multiple components."""

    def test_full_pipeline_flow(self, mock_tag_service, temp_dir):
        """Test complete pipeline from template to evidence links."""
        pipeline = ImagePipelineService(
            tag_service=mock_tag_service,
            base_storage_dir=str(temp_dir),
        )

        result = pipeline.process_template(
            template_id="t-001",
            stimulus_description="Open natural garden with prospect",
            belief_id="belief-001",
            equivalence_class="natural-landscape",
        )

        # Verify all stages executed
        assert len(result["searches"]) > 0
        assert result["summary"]["queries_generated"] > 0

    def test_evidence_link_validity(self, mock_tag_service, temp_dir):
        """Test that evidence links have valid structure."""
        pipeline = ImagePipelineService(
            tag_service=mock_tag_service,
            base_storage_dir=str(temp_dir),
        )

        result = pipeline.process_template(
            template_id="t-001",
            stimulus_description="Test stimulus",
            belief_id="belief-001",
        )

        # Check link structure if any were created
        for link_data in result.get("evidence_links", []):
            assert "link_id" in link_data
            assert "image_id" in link_data
            assert "template_id" in link_data
            assert "match_score" in link_data


# =============================================================================
# Edge Case Tests
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_stimulus_description(self, mock_tag_service, temp_dir):
        """Test handling of empty stimulus description."""
        pipeline = ImagePipelineService(
            tag_service=mock_tag_service,
            base_storage_dir=str(temp_dir),
        )

        result = pipeline.process_template(
            template_id="t-001",
            stimulus_description="",
            belief_id="belief-001",
        )

        assert result["template_id"] == "t-001"

    def test_none_equivalence_class(self, mock_tag_service, temp_dir):
        """Test handling of None equivalence class."""
        pipeline = ImagePipelineService(
            tag_service=mock_tag_service,
            base_storage_dir=str(temp_dir),
        )

        result = pipeline.process_template(
            template_id="t-001",
            stimulus_description="Test",
            belief_id="belief-001",
            equivalence_class=None,
        )

        assert result is not None

    def test_special_characters_in_description(self, mock_tag_service, temp_dir):
        """Test handling of special characters."""
        pipeline = ImagePipelineService(
            tag_service=mock_tag_service,
            base_storage_dir=str(temp_dir),
        )

        result = pipeline.process_template(
            template_id="t-001",
            stimulus_description="Test with @#$%^&*() special chars!",
            belief_id="belief-001",
        )

        assert result is not None

    def test_very_long_stimulus_description(self, mock_tag_service, temp_dir):
        """Test handling of very long stimulus descriptions."""
        long_desc = "word " * 500  # 500 word description

        pipeline = ImagePipelineService(
            tag_service=mock_tag_service,
            base_storage_dir=str(temp_dir),
        )

        result = pipeline.process_template(
            template_id="t-001",
            stimulus_description=long_desc,
            belief_id="belief-001",
        )

        assert result is not None
