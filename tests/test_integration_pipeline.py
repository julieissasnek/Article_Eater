"""
test_integration_pipeline.py — End-to-End Integration Tests
=============================================================

Tests the full pipeline: extraction → classification → T3 beliefs → bridge → interpretation space.

Expert Panel Guidance:
  - Test Engineer (#3): "No integration tests. Test end-to-end together."
  - Expert System Designer (#16): "Contract-first: verify interfaces match."
  - Data Engineer (#4): "Check data flows correctly between stages."
"""

import json
import os
import sys
import tempfile
from pathlib import Path

import pytest

# Add project root to path
REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT))


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def sample_extraction():
    """A minimal but complete extraction JSON."""
    return {
        "doi": "10.1234/test.integration",
        "title": "Effects of CCT on Mood and Performance",
        "article_family": "empirical",
        "year": 2023,
        "extraction_version": "v3",
        "findings": [
            {
                "id": 1,
                "antecedent": "High CCT (6500K)",
                "consequent": "Self-reported alertness",
                "direction": "positive",
                "effect_size": 0.42,
                "p_value": 0.003,
                "sample_n": 48,
                "study_design": "within-subjects RCT",
            },
            {
                "id": 2,
                "antecedent": "High CCT (6500K)",
                "consequent": "Task accuracy on Stroop test",
                "direction": "positive",
                "effect_size": 0.31,
                "p_value": 0.02,
                "sample_n": 48,
                "study_design": "within-subjects RCT",
            },
            {
                "id": 3,
                "antecedent": "Low illuminance (150 lux)",
                "consequent": "Sleepiness (KSS score)",
                "direction": "positive",
                "effect_size": 0.55,
                "p_value": 0.001,
                "sample_n": 48,
                "study_design": "within-subjects RCT",
            },
        ],
    }


@pytest.fixture
def sample_extraction_file(sample_extraction, tmp_path):
    """Write sample extraction to a temp file."""
    fpath = tmp_path / "10.1234_test.integration.json"
    fpath.write_text(json.dumps(sample_extraction, indent=2))
    return fpath


# ============================================================================
# Test 1: Extraction → Classification (IV/DV Classifier)
# ============================================================================

class TestExtractionToClassification:
    """Verify that extraction findings get classified by the IV/DV classifier."""

    def test_iv_classification(self, sample_extraction):
        """All IVs should get classified (not left as 'unclassified')."""
        import src.services.stimulus_taxonomy as st
        st._taxonomy = None
        from src.services.image_attribute_sync import sync_image_attributes
        sync_image_attributes()
        from src.services.iv_dv_classifier import IVDVClassifier

        clf = IVDVClassifier()
        for finding in sample_extraction["findings"]:
            result = clf.classify_iv(finding["antecedent"])
            assert result.method != "unclassified", (
                f"IV '{finding['antecedent']}' was unclassified — should match taxonomy"
            )
            assert result.confidence > 0.0, (
                f"IV '{finding['antecedent']}' has zero confidence"
            )
            assert result.node_id, (
                f"IV '{finding['antecedent']}' has no node_id"
            )

    def test_dv_classification(self, sample_extraction):
        """All DVs should get classified."""
        import src.services.stimulus_taxonomy as st
        st._taxonomy = None
        from src.services.image_attribute_sync import sync_image_attributes
        sync_image_attributes()
        from src.services.iv_dv_classifier import IVDVClassifier

        clf = IVDVClassifier()
        for finding in sample_extraction["findings"]:
            result = clf.classify_dv(finding["consequent"])
            # DVs may be unclassified for novel measures, but should have a result
            assert result is not None
            assert result.raw_text == finding["consequent"]

    def test_batch_classify(self, sample_extraction):
        """Batch classification produces enriched findings."""
        import src.services.stimulus_taxonomy as st
        st._taxonomy = None
        from src.services.image_attribute_sync import sync_image_attributes
        sync_image_attributes()
        from src.services.iv_dv_classifier import IVDVClassifier

        clf = IVDVClassifier()
        enriched = clf.batch_classify(sample_extraction["findings"])
        assert len(enriched) == len(sample_extraction["findings"])
        for e in enriched:
            assert "iv_node" in e
            assert "dv_node" in e
            assert "iv_confidence" in e
            assert "dv_confidence" in e


# ============================================================================
# Test 2: Classification → T3 Beliefs
# ============================================================================

class TestClassificationToT3:
    """Verify that classified findings become T3 beliefs."""

    def test_t3_belief_creation(self, sample_extraction):
        """Findings should create T3 beliefs via T3Adapter."""
        import src.services.stimulus_taxonomy as st
        st._taxonomy = None
        from src.services.image_attribute_sync import sync_image_attributes
        sync_image_attributes()
        from src.services.t3_integration import T3Adapter
        from src.services.generalization_tree import BeliefStatus

        # Build belief dicts as the integration pipeline does
        doi = sample_extraction["doi"]
        belief_dicts = []
        for finding in sample_extraction["findings"]:
            belief_dicts.append({
                "belief_id": f"{doi}:f{finding['id']}",
                "content": f"{finding['antecedent']} → {finding['consequent']}",
                "environment_id": finding["antecedent"],
                "outcome_id": finding["consequent"],
                "paper_ids": [doi],
                "tags": [],
            })

        adapter = T3Adapter()
        adapter.on_batch_complete(belief_dicts)
        t3 = adapter.engine.t3_beliefs

        # Should produce at least some beliefs
        assert len(t3) > 0, "No T3 beliefs created from sample findings"

        # Check each belief has required fields
        for belief in t3.values():
            assert belief.t3_id
            assert belief.iv_node
            assert belief.dv_node
            assert belief.status in (
                BeliefStatus.NASCENT, BeliefStatus.TENTATIVE,
                BeliefStatus.ESTABLISHED, BeliefStatus.CONTESTED,
            )
            assert belief.confidence >= 0.0
            assert belief.confidence <= 1.0

    def test_sample_n_propagation(self, sample_extraction):
        """Sample size data should propagate to T3 beliefs."""
        import src.services.stimulus_taxonomy as st
        st._taxonomy = None
        from src.services.image_attribute_sync import sync_image_attributes
        sync_image_attributes()
        from src.services.t3_integration import T3Adapter

        doi = sample_extraction["doi"]
        belief_dicts = []
        for finding in sample_extraction["findings"]:
            belief_dicts.append({
                "belief_id": f"{doi}:f{finding['id']}",
                "content": f"{finding['antecedent']} → {finding['consequent']}",
                "environment_id": finding["antecedent"],
                "outcome_id": finding["consequent"],
                "paper_ids": [doi],
                "tags": [],
                "sample_n": finding.get("sample_n"),
            })

        adapter = T3Adapter()
        adapter.on_batch_complete(belief_dicts)

        # Check that total_sample_n field exists on all beliefs
        for belief in adapter.engine.t3_beliefs.values():
            assert hasattr(belief, "total_sample_n"), (
                f"Belief {belief.t3_id} missing total_sample_n"
            )


# ============================================================================
# Test 3: T3 → Interpretation Space Bridge
# ============================================================================

class TestT3ToInterpSpaceBridge:
    """Verify that T3 beliefs can be bridged to interpretation space suggestions."""

    def test_bridge_importable(self):
        """The bridge module should import without errors."""
        from src.services.t3_interp_bridge import T3InterpBridge
        assert T3InterpBridge is not None

    def test_bridge_sync_smoke(self, sample_extraction):
        """Bridge sync should run without errors on real T3 data."""
        import src.services.stimulus_taxonomy as st
        st._taxonomy = None
        from src.services.image_attribute_sync import sync_image_attributes
        sync_image_attributes()
        from src.services.t3_integration import T3Adapter
        from src.services.t3_interp_bridge import T3InterpBridge
        from src.services.interpretation_space_suggestions import (
            InterpretationSpaceSuggestionsManager,
        )

        # Create T3 beliefs
        doi = sample_extraction["doi"]
        belief_dicts = []
        for finding in sample_extraction["findings"]:
            belief_dicts.append({
                "belief_id": f"{doi}:f{finding['id']}",
                "content": f"{finding['antecedent']} → {finding['consequent']}",
                "environment_id": finding["antecedent"],
                "outcome_id": finding["consequent"],
                "paper_ids": [doi],
                "tags": [],
            })

        adapter = T3Adapter()
        adapter.on_batch_complete(belief_dicts)

        # Create suggestions manager with temp DB
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            temp_db = f.name

        try:
            suggestions = InterpretationSpaceSuggestionsManager(temp_db)

            bridge = T3InterpBridge(
                engine=adapter.engine.engine,
                suggestion_manager=suggestions,
            )

            # Get summary should work
            summary = bridge.get_summary()
            assert "total_beliefs" in summary
            assert "nascent" in summary
            assert summary["total_beliefs"] > 0
        finally:
            os.unlink(temp_db)


# ============================================================================
# Test 4: DB Locator Resolution
# ============================================================================

class TestDBLocatorResolution:
    """Verify DB locator resolves correctly (no phantom v2 creation)."""

    def test_get_web_db_returns_existing(self):
        """get_web_db() should return a path that exists or will be created."""
        from src.services.db_locator import get_web_db
        db_path = get_web_db()
        # Either the returned path exists or we're in a test env
        assert db_path is not None
        assert db_path.name in ("web_persistence.db", "web_persistence_v2.db")

    def test_no_phantom_v2_creation(self, tmp_path):
        """Resolving DB should not create phantom v2 file."""
        from src.services.db_locator import candidate_web_dbs
        candidates = candidate_web_dbs()
        # v2 should NOT be in candidates if it doesn't exist on disk
        for c in candidates:
            if c.name == "web_persistence_v2.db":
                assert c.exists(), (
                    f"v2 DB {c} in candidates but doesn't exist on disk"
                )


# ============================================================================
# Test 5: Moderator Analysis
# ============================================================================

class TestModeratorAnalysis:
    """Verify moderator analysis works on contested beliefs."""

    def test_analyze_moderators(self, sample_extraction):
        """Moderator analysis should return structured results."""
        import src.services.stimulus_taxonomy as st
        st._taxonomy = None
        from src.services.image_attribute_sync import sync_image_attributes
        sync_image_attributes()
        from src.services.t3_integration import T3Adapter
        from src.services.generalization_tree import BeliefStatus

        doi = sample_extraction["doi"]
        belief_dicts = []
        for finding in sample_extraction["findings"]:
            belief_dicts.append({
                "belief_id": f"{doi}:f{finding['id']}",
                "content": f"{finding['antecedent']} → {finding['consequent']}",
                "environment_id": finding["antecedent"],
                "outcome_id": finding["consequent"],
                "paper_ids": [doi],
                "tags": [],
            })

        adapter = T3Adapter()
        adapter.on_batch_complete(belief_dicts)

        # Get any belief to test analyze_moderators
        engine = adapter.engine.engine
        beliefs = list(engine.beliefs.values())
        if beliefs:
            analysis = engine.analyze_moderators(beliefs[0])
            assert isinstance(analysis, dict)
            # Should have at least status or belief_id
            assert "status" in analysis or "belief_id" in analysis

    def test_cross_modal_analysis(self, sample_extraction):
        """Cross-modal analysis should return structured results."""
        import src.services.stimulus_taxonomy as st
        st._taxonomy = None
        from src.services.image_attribute_sync import sync_image_attributes
        sync_image_attributes()
        from src.services.t3_integration import T3Adapter

        doi = sample_extraction["doi"]
        belief_dicts = []
        for finding in sample_extraction["findings"]:
            belief_dicts.append({
                "belief_id": f"{doi}:f{finding['id']}",
                "content": f"{finding['antecedent']} → {finding['consequent']}",
                "environment_id": finding["antecedent"],
                "outcome_id": finding["consequent"],
                "paper_ids": [doi],
                "tags": [],
            })

        adapter = T3Adapter()
        adapter.on_batch_complete(belief_dicts)

        engine = adapter.engine.engine
        cm = engine.cross_modal_analysis()
        assert isinstance(cm, dict)
        assert "total_cross_modal_pairs" in cm
        assert "consistent" in cm
        assert "generalizable" in cm


# ============================================================================
# Test 6: Classification Stats (with TF-IDF)
# ============================================================================

class TestClassificationStats:
    """Verify classification stats include tfidf method."""

    def test_stats_include_tfidf(self):
        """Stats dict should include 'tfidf' key."""
        import src.services.stimulus_taxonomy as st
        st._taxonomy = None
        from src.services.image_attribute_sync import sync_image_attributes
        sync_image_attributes()
        from src.services.iv_dv_classifier import IVDVClassifier

        clf = IVDVClassifier()
        # Classify something to initialize stats
        clf.classify_iv("test input")
        stats = clf.classification_stats()
        assert "tfidf" in stats["by_method"], (
            f"Stats missing 'tfidf' key: {stats['by_method']}"
        )
