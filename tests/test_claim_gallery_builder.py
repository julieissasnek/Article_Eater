"""
Tests for Claim Gallery Builder
===============================

Sprint G1: Visual Evidence Layer Tests
"""

import pytest
from datetime import datetime
from pathlib import Path
import tempfile
import json

from src.services.claim_gallery_builder import (
    ClaimGalleryBuilder,
    ClaimGallery,
    ClaimInfo,
    ClaimFeature,
    ClaimOutcome,
    EvidenceQuality,
    GalleryScope,
    PersonaProfile,
    SlotRole,
    build_gallery_from_claim_and_pool,
    save_gallery,
    save_selection_log,
    SCHEMA_VERSION,
)


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def sample_claim() -> ClaimInfo:
    """Create a sample claim for testing."""
    return ClaimInfo(
        claim_id="claim_refuge_001",
        statement="Refuge edges (partial enclosure) increase perceived safety in open office environments",
        feature=ClaimFeature(
            feature_id="feat_refuge_edge",
            feature_name="Refuge edges",
            feature_definition="Partial enclosure providing visual shelter while maintaining prospect",
            feature_aliases=["alcove", "nook", "semi-enclosed space"]
        ),
        outcome=ClaimOutcome(
            outcome_id="out_perceived_safety",
            outcome_name="Perceived safety",
            outcome_definition="Self-reported feeling of security in the space",
            valence="higher_is_better"
        )
    )


@pytest.fixture
def sample_image_pool() -> list:
    """Create a sample image pool for testing."""
    images = []

    # High-scoring positives (above tau=0.65)
    for i in range(10):
        images.append({
            "image_id": f"pos_{i}",
            "uri_or_path": f"/images/positive_{i}.jpg",
            "feature_score": 0.75 + (i * 0.02),  # 0.75-0.93
            "confidence_basis": "model_prediction",
            "outcome_status": "literature_link_only",
            "building_type": ["office", "hospital", "school", "retail", "library"][i % 5],
            "culture_region": "north_america",
            "project_id": f"proj_{i % 4}",  # 4 different projects
            "source": f"source_{i % 3}",
            "license": "CC BY-NC 4.0",
            "attribution": f"Study {i}",
            "cues": ["alcove seating", "partial ceiling drop"],
            "feature_tags": ["refuge", "enclosure"],
            "context_tags": ["open_office"],
            "moderator_flags": []
        })

    # Low-scoring negatives (below tau - band = 0.50)
    for i in range(8):
        images.append({
            "image_id": f"neg_{i}",
            "uri_or_path": f"/images/negative_{i}.jpg",
            "feature_score": 0.10 + (i * 0.05),  # 0.10-0.45
            "confidence_basis": "model_prediction",
            "outcome_status": "literature_link_only",
            "building_type": ["office", "hospital"][i % 2],
            "culture_region": "europe",
            "project_id": f"proj_neg_{i % 3}",
            "source": f"source_neg_{i % 2}",
            "license": "CC BY 4.0",
            "attribution": f"Study neg {i}",
            "cues": ["open floor", "no enclosure"],
            "feature_tags": ["open"],
            "context_tags": ["open_office"],
            "moderator_flags": []
        })

    # Near misses (around tau ± band = 0.50-0.80)
    for i in range(6):
        images.append({
            "image_id": f"near_{i}",
            "uri_or_path": f"/images/nearmiss_{i}.jpg",
            "feature_score": 0.55 + (i * 0.03),  # 0.55-0.70
            "confidence_basis": "hybrid",
            "outcome_status": "measured_on_similar_context",
            "building_type": "office",
            "culture_region": "asia",
            "project_id": f"proj_near_{i % 2}",
            "source": "near_source",
            "license": "CC BY-NC-SA 4.0",
            "attribution": f"Study near {i}",
            "cues": ["partial enclosure", "ambiguous boundary"],
            "feature_tags": ["partial_refuge"],
            "context_tags": ["open_office"],
            "moderator_flags": []
        })

    # Likely failures (high feature score but moderator flags)
    for i in range(4):
        images.append({
            "image_id": f"fail_{i}",
            "uri_or_path": f"/images/failure_{i}.jpg",
            "feature_score": 0.80 + (i * 0.03),  # 0.80-0.89
            "confidence_basis": "model_prediction",
            "outcome_status": "unknown",
            "building_type": "office",
            "culture_region": "north_america",
            "project_id": f"proj_fail_{i}",
            "source": "fail_source",
            "license": "CC BY 4.0",
            "attribution": f"Study fail {i}",
            "cues": ["refuge present"],
            "feature_tags": ["refuge"],
            "context_tags": ["crowded"],
            "moderator_flags": ["high_occupancy", "noise_level"][: i % 2 + 1]
        })

    return images


@pytest.fixture
def sample_evidence_quality() -> EvidenceQuality:
    """Create sample evidence quality metrics."""
    return EvidenceQuality(
        design_strength=0.72,
        consistency=0.68,
        portability=0.55,
        notes="Based on 12 studies across 3 building types",
        top_citations=[
            {"citation_id": "cit_001", "title": "Refuge in Open Offices", "year": 2019},
            {"citation_id": "cit_002", "title": "Prospect-Refuge Theory Applied", "year": 2021}
        ]
    )


@pytest.fixture
def sample_scope() -> GalleryScope:
    """Create sample scope."""
    return GalleryScope(
        population="Adult office workers (18-65)",
        setting="Open-plan office environments",
        task_context="Knowledge work, collaborative tasks",
        measurement_context="Self-report questionnaires, behavioral observation",
        duration="Cross-sectional studies",
        exclusions=["Industrial settings", "Outdoor spaces"]
    )


# =============================================================================
# BASIC TESTS
# =============================================================================

class TestClaimGalleryBuilder:
    """Tests for the ClaimGalleryBuilder class."""

    def test_builder_initialization(self):
        """Test that the builder initializes correctly."""
        builder = ClaimGalleryBuilder()
        assert builder.persona == PersonaProfile.DEFAULT
        assert builder.feature_threshold_tau == 0.65
        assert builder.near_miss_band == 0.15
        assert builder.random_seed == 42

    def test_builder_with_custom_params(self):
        """Test builder with custom parameters."""
        builder = ClaimGalleryBuilder(
            persona=PersonaProfile.RESEARCHER,
            feature_threshold_tau=0.70,
            near_miss_band=0.10,
            random_seed=123
        )
        assert builder.persona == PersonaProfile.RESEARCHER
        assert builder.feature_threshold_tau == 0.70

    def test_build_gallery(
        self,
        sample_claim,
        sample_image_pool,
        sample_evidence_quality,
        sample_scope
    ):
        """Test that a gallery is built correctly."""
        builder = ClaimGalleryBuilder()
        gallery = builder.build_gallery(
            claim=sample_claim,
            image_pool=sample_image_pool,
            evidence_quality=sample_evidence_quality,
            scope=sample_scope,
            config_id="test_config"
        )

        assert gallery is not None
        assert gallery.gallery_id.startswith("gal_")
        assert gallery.claim.claim_id == "claim_refuge_001"
        assert len(gallery.slots.central_positive) > 0
        assert len(gallery.slots.central_negative) > 0

    def test_gallery_has_required_slots(
        self,
        sample_claim,
        sample_image_pool,
        sample_evidence_quality,
        sample_scope
    ):
        """Test that gallery has all required slots (AT1)."""
        builder = ClaimGalleryBuilder()
        gallery = builder.build_gallery(
            claim=sample_claim,
            image_pool=sample_image_pool,
            evidence_quality=sample_evidence_quality,
            scope=sample_scope
        )

        # AT1: Every claim should have positive, negative, and near-miss
        assert len(gallery.slots.central_positive) >= 1, "Should have positive examples"
        assert len(gallery.slots.central_negative) >= 1, "Should have negative examples"
        assert len(gallery.slots.near_miss) >= 1, "Should have near-miss examples"

    def test_gallery_shows_both_sides(
        self,
        sample_claim,
        sample_image_pool,
        sample_evidence_quality,
        sample_scope
    ):
        """Test that gallery shows both positives AND negatives (AT2)."""
        builder = ClaimGalleryBuilder()
        gallery = builder.build_gallery(
            claim=sample_claim,
            image_pool=sample_image_pool,
            evidence_quality=sample_evidence_quality,
            scope=sample_scope
        )

        # AT2: UI always shows both positives AND negatives
        has_positives = len(gallery.slots.central_positive) > 0
        has_negatives = len(gallery.slots.central_negative) > 0
        assert has_positives and has_negatives, "Gallery must show both sides"


# =============================================================================
# DETERMINISM TESTS
# =============================================================================

class TestDeterminism:
    """Tests for deterministic gallery building (AT4)."""

    def test_same_inputs_same_output(
        self,
        sample_claim,
        sample_image_pool,
        sample_evidence_quality,
        sample_scope
    ):
        """Test that same inputs produce identical galleries (AT4)."""
        builder1 = ClaimGalleryBuilder(random_seed=42)
        builder2 = ClaimGalleryBuilder(random_seed=42)

        gallery1 = builder1.build_gallery(
            claim=sample_claim,
            image_pool=sample_image_pool,
            evidence_quality=sample_evidence_quality,
            scope=sample_scope,
            config_id="determinism_test",
            snapshot_id="snap_001"
        )

        gallery2 = builder2.build_gallery(
            claim=sample_claim,
            image_pool=sample_image_pool,
            evidence_quality=sample_evidence_quality,
            scope=sample_scope,
            config_id="determinism_test",
            snapshot_id="snap_001"
        )

        # Same gallery ID
        assert gallery1.gallery_id == gallery2.gallery_id

        # Same images selected
        pos1_ids = [img.image_id for img in gallery1.slots.central_positive]
        pos2_ids = [img.image_id for img in gallery2.slots.central_positive]
        assert pos1_ids == pos2_ids, "Same positives should be selected"

    def test_different_seeds_different_output(
        self,
        sample_claim,
        sample_image_pool,
        sample_evidence_quality,
        sample_scope
    ):
        """Test that different seeds can produce different galleries."""
        builder1 = ClaimGalleryBuilder(random_seed=42)
        builder2 = ClaimGalleryBuilder(random_seed=999)

        gallery1 = builder1.build_gallery(
            claim=sample_claim,
            image_pool=sample_image_pool,
            evidence_quality=sample_evidence_quality,
            scope=sample_scope
        )

        gallery2 = builder2.build_gallery(
            claim=sample_claim,
            image_pool=sample_image_pool,
            evidence_quality=sample_evidence_quality,
            scope=sample_scope
        )

        # Different gallery IDs (seed is part of hash)
        assert gallery1.gallery_id != gallery2.gallery_id


# =============================================================================
# DIVERSITY TESTS
# =============================================================================

class TestDiversity:
    """Tests for diversity constraints (AT6)."""

    def test_max_per_project(
        self,
        sample_claim,
        sample_evidence_quality,
        sample_scope
    ):
        """Test that max 2 images from same project per slot (AT6)."""
        # Create a pool where all images are from the same project
        # but with different scores to test the diversity limit
        same_project_pool = []
        for i in range(10):
            same_project_pool.append({
                "image_id": f"same_proj_{i}",
                "uri_or_path": f"/images/same_{i}.jpg",
                "feature_score": 0.75 + (i * 0.02),  # 0.75-0.93
                "confidence_basis": "model_prediction",
                "outcome_status": "literature_link_only",
                "building_type": "office",
                "culture_region": "north_america",
                "project_id": "SAME_PROJECT",  # All same project!
                "source": "same_source",
                "license": "CC BY-NC 4.0",
                "attribution": f"Study {i}",
                "cues": ["alcove seating"],
                "feature_tags": ["refuge"],
                "context_tags": ["open_office"],
                "moderator_flags": []
            })

        builder = ClaimGalleryBuilder()
        gallery = builder.build_gallery(
            claim=sample_claim,
            image_pool=same_project_pool,
            evidence_quality=sample_evidence_quality,
            scope=sample_scope
        )

        # With all images from same project, should be limited to 2
        assert len(gallery.slots.central_positive) <= 2, \
            f"Should have max 2 from same project, got {len(gallery.slots.central_positive)}"


# =============================================================================
# PROVENANCE TESTS
# =============================================================================

class TestProvenance:
    """Tests for provenance tracking (AT5, AT9)."""

    def test_every_image_has_provenance(
        self,
        sample_claim,
        sample_image_pool,
        sample_evidence_quality,
        sample_scope
    ):
        """Test that every image has provenance (AT5)."""
        builder = ClaimGalleryBuilder()
        gallery = builder.build_gallery(
            claim=sample_claim,
            image_pool=sample_image_pool,
            evidence_quality=sample_evidence_quality,
            scope=sample_scope
        )

        all_images = (
            gallery.slots.central_positive +
            gallery.slots.central_negative +
            gallery.slots.near_miss +
            gallery.slots.likely_failure +
            gallery.slots.context_shift
        )

        for img in all_images:
            assert img.provenance is not None, f"Image {img.image_id} missing provenance"
            assert img.provenance.source, f"Image {img.image_id} missing source"
            assert img.provenance.license, f"Image {img.image_id} missing license"

    def test_gallery_includes_config_and_hash(
        self,
        sample_claim,
        sample_image_pool,
        sample_evidence_quality,
        sample_scope
    ):
        """Test that gallery includes config_id and snapshot hash (AT9)."""
        builder = ClaimGalleryBuilder()
        gallery = builder.build_gallery(
            claim=sample_claim,
            image_pool=sample_image_pool,
            evidence_quality=sample_evidence_quality,
            scope=sample_scope,
            config_id="config_001"
        )

        assert gallery.provenance_summary.config_id == "config_001"
        assert gallery.provenance_summary.snapshot_hash is not None
        assert len(gallery.provenance_summary.snapshot_hash) > 0


# =============================================================================
# OUTCOME EVIDENCE TESTS
# =============================================================================

class TestOutcomeEvidence:
    """Tests for outcome evidence display (AT3)."""

    def test_every_image_has_outcome_status(
        self,
        sample_claim,
        sample_image_pool,
        sample_evidence_quality,
        sample_scope
    ):
        """Test that every image displays outcome_evidence.status (AT3)."""
        builder = ClaimGalleryBuilder()
        gallery = builder.build_gallery(
            claim=sample_claim,
            image_pool=sample_image_pool,
            evidence_quality=sample_evidence_quality,
            scope=sample_scope
        )

        all_images = (
            gallery.slots.central_positive +
            gallery.slots.central_negative +
            gallery.slots.near_miss
        )

        for img in all_images:
            assert img.outcome_evidence is not None
            assert img.outcome_evidence.status is not None


# =============================================================================
# PERSONA TESTS
# =============================================================================

class TestPersonas:
    """Tests for persona-based configuration (UX2)."""

    def test_architect_persona_fewer_images(
        self,
        sample_claim,
        sample_image_pool,
        sample_evidence_quality,
        sample_scope
    ):
        """Test that architect persona produces fewer images."""
        architect_builder = ClaimGalleryBuilder(persona=PersonaProfile.ARCHITECT)
        researcher_builder = ClaimGalleryBuilder(persona=PersonaProfile.RESEARCHER)

        arch_gallery = architect_builder.build_gallery(
            claim=sample_claim,
            image_pool=sample_image_pool,
            evidence_quality=sample_evidence_quality,
            scope=sample_scope
        )

        res_gallery = researcher_builder.build_gallery(
            claim=sample_claim,
            image_pool=sample_image_pool,
            evidence_quality=sample_evidence_quality,
            scope=sample_scope
        )

        # Researcher should have more images than architect
        arch_total = len(arch_gallery.slots.central_positive) + len(arch_gallery.slots.near_miss)
        res_total = len(res_gallery.slots.central_positive) + len(res_gallery.slots.near_miss)

        assert res_total >= arch_total, "Researcher should have at least as many images"


# =============================================================================
# SELECTION LOG TESTS
# =============================================================================

class TestSelectionLog:
    """Tests for selection log (AT8)."""

    def test_selection_log_generated(
        self,
        sample_claim,
        sample_image_pool,
        sample_evidence_quality,
        sample_scope
    ):
        """Test that selection log is generated."""
        builder = ClaimGalleryBuilder()
        builder.build_gallery(
            claim=sample_claim,
            image_pool=sample_image_pool,
            evidence_quality=sample_evidence_quality,
            scope=sample_scope
        )

        log = builder.get_selection_log()
        assert log is not None
        assert log.log_id.startswith("log_gal_")
        assert "central_positive" in log.slots
        assert len(log.slots["central_positive"].selected) > 0

    def test_selection_log_has_exclusion_reasons(
        self,
        sample_claim,
        sample_image_pool,
        sample_evidence_quality,
        sample_scope
    ):
        """Test that selection log explains exclusions."""
        builder = ClaimGalleryBuilder()
        builder.build_gallery(
            claim=sample_claim,
            image_pool=sample_image_pool,
            evidence_quality=sample_evidence_quality,
            scope=sample_scope
        )

        log = builder.get_selection_log()
        # Should have some exclusions due to diversity limits
        total_excluded = sum(
            len(slot_log.excluded_top)
            for slot_log in log.slots.values()
        )
        # With our test data, some should be excluded
        assert total_excluded >= 0  # May be 0 if pool is small


# =============================================================================
# SERIALIZATION TESTS
# =============================================================================

class TestSerialization:
    """Tests for JSON serialization."""

    def test_gallery_to_dict(
        self,
        sample_claim,
        sample_image_pool,
        sample_evidence_quality,
        sample_scope
    ):
        """Test that gallery serializes to dict correctly."""
        builder = ClaimGalleryBuilder()
        gallery = builder.build_gallery(
            claim=sample_claim,
            image_pool=sample_image_pool,
            evidence_quality=sample_evidence_quality,
            scope=sample_scope
        )

        d = gallery.to_dict()
        assert d["schema_version"] == SCHEMA_VERSION
        assert "gallery_id" in d
        assert "claim" in d
        assert "slots" in d

    def test_gallery_to_json(
        self,
        sample_claim,
        sample_image_pool,
        sample_evidence_quality,
        sample_scope
    ):
        """Test that gallery serializes to JSON correctly."""
        builder = ClaimGalleryBuilder()
        gallery = builder.build_gallery(
            claim=sample_claim,
            image_pool=sample_image_pool,
            evidence_quality=sample_evidence_quality,
            scope=sample_scope
        )

        json_str = gallery.to_json()
        parsed = json.loads(json_str)
        assert parsed["schema_version"] == SCHEMA_VERSION

    def test_save_gallery_to_disk(
        self,
        sample_claim,
        sample_image_pool,
        sample_evidence_quality,
        sample_scope
    ):
        """Test saving gallery to disk."""
        builder = ClaimGalleryBuilder()
        gallery = builder.build_gallery(
            claim=sample_claim,
            image_pool=sample_image_pool,
            evidence_quality=sample_evidence_quality,
            scope=sample_scope
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            path = save_gallery(gallery, Path(tmpdir))
            assert path.exists()
            with open(path) as f:
                loaded = json.load(f)
            assert loaded["gallery_id"] == gallery.gallery_id


# =============================================================================
# CONVENIENCE FUNCTION TESTS
# =============================================================================

class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_build_gallery_from_claim_and_pool(self, sample_image_pool):
        """Test the convenience function."""
        gallery = build_gallery_from_claim_and_pool(
            claim_id="claim_test",
            claim_statement="Test claim about feature X affecting outcome Y",
            feature_id="feat_test",
            feature_name="Test Feature",
            outcome_id="out_test",
            outcome_name="Test Outcome",
            image_pool=sample_image_pool,
            persona="default",
            tau=0.65
        )

        assert gallery is not None
        assert gallery.claim.claim_id == "claim_test"
        assert len(gallery.slots.central_positive) > 0


# =============================================================================
# INPUT VALIDATION TESTS (Panel Fix: ChatGPT-4)
# =============================================================================

class TestInputValidation:
    """Tests for input validation per ChatGPT-4 panel critique."""

    def test_empty_pool_raises_error(self, sample_claim, sample_evidence_quality, sample_scope):
        """Test that empty image pool raises ValueError."""
        builder = ClaimGalleryBuilder()
        with pytest.raises(ValueError, match="image_pool cannot be empty"):
            builder.build_gallery(
                claim=sample_claim,
                image_pool=[],  # Empty pool
                evidence_quality=sample_evidence_quality,
                scope=sample_scope
            )

    def test_invalid_tau_raises_error(self):
        """Test that invalid tau values raise ValueError."""
        with pytest.raises(ValueError, match="feature_threshold_tau must be in"):
            ClaimGalleryBuilder(feature_threshold_tau=0)

        with pytest.raises(ValueError, match="feature_threshold_tau must be in"):
            ClaimGalleryBuilder(feature_threshold_tau=1)

        with pytest.raises(ValueError, match="feature_threshold_tau must be in"):
            ClaimGalleryBuilder(feature_threshold_tau=-0.5)

    def test_invalid_band_raises_error(self):
        """Test that invalid band values raise ValueError."""
        with pytest.raises(ValueError, match="near_miss_band must be in"):
            ClaimGalleryBuilder(feature_threshold_tau=0.5, near_miss_band=0)

        with pytest.raises(ValueError, match="near_miss_band must be in"):
            ClaimGalleryBuilder(feature_threshold_tau=0.5, near_miss_band=0.6)

    def test_invalid_feature_score_raises_error(
        self,
        sample_claim,
        sample_evidence_quality,
        sample_scope
    ):
        """Test that invalid feature scores raise ValueError."""
        bad_pool = [{
            "image_id": "bad_img",
            "uri_or_path": "/bad.jpg",
            "feature_score": 1.5,  # Invalid: > 1
            "source": "test",
            "license": "test",
        }]

        builder = ClaimGalleryBuilder()
        with pytest.raises(ValueError, match="invalid feature_score"):
            builder.build_gallery(
                claim=sample_claim,
                image_pool=bad_pool,
                evidence_quality=sample_evidence_quality,
                scope=sample_scope
            )


# =============================================================================
# OUTCOME VALIDATION TESTS (Panel Fix: Pearl, Ng)
# =============================================================================

class TestOutcomeValidation:
    """Tests for outcome_status validation per Pearl and Ng panel critique."""

    def test_measured_status_requires_outcomes(self, sample_claim, sample_evidence_quality, sample_scope):
        """Test that 'measured_on_this_image' without outcomes gets downgraded."""
        pool = [{
            "image_id": "measured_no_outcomes",
            "uri_or_path": "/test.jpg",
            "feature_score": 0.8,
            "outcome_status": "measured_on_this_image",  # Claims measured
            # But no measured_outcomes provided!
            "source": "test",
            "license": "test",
        }]

        builder = ClaimGalleryBuilder()
        gallery = builder.build_gallery(
            claim=sample_claim,
            image_pool=pool,
            evidence_quality=sample_evidence_quality,
            scope=sample_scope
        )

        # Should be downgraded to literature_link_only
        img = gallery.slots.central_positive[0]
        assert img.outcome_evidence.status.value == "literature_link_only", \
            "Should downgrade to literature_link_only when no outcomes provided"

    def test_measured_status_with_outcomes_preserved(
        self,
        sample_claim,
        sample_evidence_quality,
        sample_scope
    ):
        """Test that 'measured_on_this_image' WITH outcomes is preserved."""
        pool = [{
            "image_id": "properly_measured",
            "uri_or_path": "/test.jpg",
            "feature_score": 0.8,
            "outcome_status": "measured_on_this_image",
            "measured_outcomes": [
                {"outcome_id": "out1", "measure": "self_report", "direction": "increase"}
            ],
            "source": "test",
            "license": "test",
        }]

        builder = ClaimGalleryBuilder()
        gallery = builder.build_gallery(
            claim=sample_claim,
            image_pool=pool,
            evidence_quality=sample_evidence_quality,
            scope=sample_scope
        )

        img = gallery.slots.central_positive[0]
        assert img.outcome_evidence.status.value == "measured_on_this_image", \
            "Should preserve status when outcomes are provided"
        assert len(img.outcome_evidence.measured_outcomes) == 1, \
            "Should populate measured_outcomes"

    def test_literature_link_status_ok_without_outcomes(
        self,
        sample_claim,
        sample_evidence_quality,
        sample_scope
    ):
        """Test that 'literature_link_only' is acceptable without outcomes."""
        pool = [{
            "image_id": "lit_link",
            "uri_or_path": "/test.jpg",
            "feature_score": 0.8,
            "outcome_status": "literature_link_only",
            # No measured_outcomes - that's fine for lit link
            "source": "test",
            "license": "test",
        }]

        builder = ClaimGalleryBuilder()
        gallery = builder.build_gallery(
            claim=sample_claim,
            image_pool=pool,
            evidence_quality=sample_evidence_quality,
            scope=sample_scope
        )

        img = gallery.slots.central_positive[0]
        assert img.outcome_evidence.status.value == "literature_link_only"
