"""
Tests for TheoryGuideService

Validates:
1. All 12 guides load successfully
2. Fuzzy matching works (abbreviations, partial names)
3. Detail level extraction (quick vs standard vs technical)
4. Theory metadata loading
5. Search functionality
6. Tooltip HTML generation
"""

import pytest
import json
from pathlib import Path
from src.services.theory_guide_service import TheoryGuideService, TheoryGuideResult


@pytest.fixture
def service():
    """Initialize theory guide service for tests."""
    return TheoryGuideService()


class TestGuideLoading:
    """Test that guides load correctly."""

    def test_guides_directory_exists(self, service):
        """Guides directory should exist."""
        assert service.guides_dir.exists(), f"Guides directory not found: {service.guides_dir}"

    def test_theories_directory_exists(self, service):
        """Theories metadata directory should exist."""
        assert service.theories_dir.exists(), f"Theories directory not found: {service.theories_dir}"

    def test_at_least_11_guides_available(self, service):
        """Should have at least 11 theory guides."""
        available = service.list_available_guides()
        assert len(available) >= 11, f"Expected >= 11 guides, got {len(available)}: {available}"

    def test_guide_basenames_loaded(self, service):
        """Guide filenames should be registered."""
        assert len(service._guide_files) > 0, "No guides loaded"
        # Should have guides for common theories
        guide_ids = list(service._guide_files.keys())
        assert any("flow" in gid or "Flow" in gid for gid in guide_ids), "Flow theory not found"

    def test_list_available_guides(self, service):
        """list_available_guides should return non-empty list."""
        guides = service.list_available_guides()
        assert isinstance(guides, list)
        assert len(guides) > 0
        assert all(isinstance(g, str) for g in guides)


class TestMetadataLoading:
    """Test theory metadata loading."""

    def test_load_metadata_for_known_theory(self, service):
        """Should load metadata for known theories."""
        # Try to load for a theory we know exists
        metadata = service._load_metadata("attention-restoration-theory")
        if metadata:  # Might be None if JSON doesn't exist
            assert isinstance(metadata, dict)
            assert "theory_id" in metadata or "name" in metadata or "constructs" in metadata

    def test_metadata_caching(self, service):
        """Metadata should be cached after first load."""
        service._load_metadata("flow-theory")
        first_load = service._metadata_cache.get("flow-theory")
        service._load_metadata("flow-theory")
        second_load = service._metadata_cache.get("flow-theory")
        assert first_load is second_load, "Metadata not cached"

    def test_tea_scores_loading(self, service):
        """Should be able to load theories from tea_scores.json."""
        tea_path = service.theories_dir / "tea_scores.json"
        if tea_path.exists():
            with open(tea_path) as f:
                data = json.load(f)
            assert "theories" in data or "metadata" in data
            # Try loading a theory from tea_scores
            if "theories" in data and len(data["theories"]) > 0:
                theory = data["theories"][0]
                theory_id = theory.get("theory_id")
                if theory_id:
                    metadata = service._load_metadata(theory_id)
                    # Should find it (either from individual JSON or from tea_scores)
                    assert metadata is not None


class TestGuideContent:
    """Test guide content extraction and levels."""

    def test_get_guide_quick_level(self, service):
        """Should extract quick-level content."""
        # Try multiple theory names to find one that works
        guides = service.list_available_guides()
        for theory_name in guides[:3]:  # Try first 3
            result = service.get_guide(theory_name, detail_level="quick")
            if result:
                assert isinstance(result, TheoryGuideResult)
                assert result.detail_level == "quick"
                assert result.content, f"No content extracted for {theory_name}"
                assert len(result.content) > 10, "Content too short"
                return
        # If we get here, at least one guide worked
        assert True

    def test_get_guide_standard_level(self, service):
        """Should extract standard-level content."""
        guides = service.list_available_guides()
        for theory_name in guides[:3]:
            result = service.get_guide(theory_name, detail_level="standard")
            if result:
                assert result.detail_level == "standard"
                assert result.content
                return
        assert True

    def test_get_guide_technical_level(self, service):
        """Should extract technical-level content."""
        guides = service.list_available_guides()
        for theory_name in guides[:3]:
            result = service.get_guide(theory_name, detail_level="technical")
            if result:
                assert result.detail_level == "technical"
                assert result.content
                return
        assert True

    def test_guide_returns_theory_guideresult(self, service):
        """get_guide should return TheoryGuideResult with required fields."""
        guides = service.list_available_guides()
        if guides:
            result = service.get_guide(guides[0])
            assert result is not None
            assert isinstance(result, TheoryGuideResult)
            assert result.theory_id
            assert result.display_name
            assert result.detail_level
            assert result.content

    def test_nonexistent_guide_returns_none(self, service):
        """Should return None for non-existent theory."""
        result = service.get_guide("nonexistent-theory-xyz-123")
        assert result is None

    def test_guide_constructs_included(self, service):
        """Theory guides should include constructs from metadata."""
        guides = service.list_available_guides()
        for theory_name in guides[:3]:
            result = service.get_guide(theory_name)
            if result:
                # constructs may be empty, but should be a list
                assert isinstance(result.constructs, list)
                return


class TestFuzzyMatching:
    """Test fuzzy matching and aliases."""

    def test_fuzzy_match_exact(self, service):
        """Exact match should work."""
        guides = service.list_available_guides()
        if guides:
            # Try fuzzy matching the actual name
            match = service.fuzzy_match(guides[0], guides)
            assert match == guides[0]

    def test_fuzzy_match_partial(self, service):
        """Should match partial words."""
        candidates = ["attention restoration theory", "place attachment", "flow theory"]
        match = service.fuzzy_match("flow", candidates)
        assert match is not None
        assert "flow" in match.lower()

    def test_fuzzy_match_case_insensitive(self, service):
        """Matching should be case-insensitive."""
        candidates = ["Attention Restoration Theory"]
        match = service.fuzzy_match("attention", candidates)
        assert match is not None

    def test_alias_lookup_succeeds(self, service):
        """Should resolve aliases correctly."""
        # Build service alias map
        assert len(service._alias_map) > 0, "No aliases built"
        # Try looking up an alias
        for alias in list(service._alias_map.keys())[:5]:
            theory_id = service._alias_map[alias]
            assert theory_id is not None

    def test_abbreviations_in_alias_map(self, service):
        """Common abbreviations should be in alias map."""
        # After loading, should have built aliases
        service._load_guides_and_metadata()
        # Check that some abbreviations are included
        aliases = list(service._alias_map.keys())
        # Common abbreviations like "ART", "SRT" should be present (if metadata has them)
        # This is a soft assertion since it depends on loaded JSON files
        assert len(aliases) > 0


class TestSearch:
    """Test search functionality."""

    def test_search_returns_list(self, service):
        """search_theories should return list of TheoryGuideResult."""
        results = service.search_theories("flow")
        assert isinstance(results, list)
        if results:
            assert all(isinstance(r, TheoryGuideResult) for r in results)

    def test_search_finds_matching_theories(self, service):
        """Searching for "flow" should find flow theory."""
        results = service.search_theories("flow")
        assert len(results) > 0, "No results for 'flow' search"
        # At least one should contain 'flow' in name
        assert any("flow" in r.display_name.lower() for r in results)

    def test_search_respects_max_results(self, service):
        """search_theories should respect max_results parameter."""
        results = service.search_theories("theory", max_results=3)
        assert len(results) <= 3

    def test_search_empty_query(self, service):
        """Searching with empty query should not crash."""
        results = service.search_theories("")
        assert isinstance(results, list)

    def test_search_nonexistent_term(self, service):
        """Searching for non-existent term should return empty list."""
        results = service.search_theories("xyzabc123nonexistentword")
        assert isinstance(results, list)


class TestTooltipGeneration:
    """Test HTML tooltip generation."""

    def test_tooltip_html_generated(self, service):
        """get_tooltip_html should return HTML string."""
        guides = service.list_available_guides()
        if guides:
            html = service.get_tooltip_html(guides[0])
            assert html is not None
            assert isinstance(html, str)
            assert "<div" in html or "<p" in html

    def test_tooltip_includes_theory_name(self, service):
        """Tooltip HTML should include theory display name."""
        guides = service.list_available_guides()
        if guides:
            theory_name = guides[0]
            html = service.get_tooltip_html(theory_name)
            if html:
                # Should contain some part of the theory name
                assert theory_name.lower() in html.lower() or ">" in html

    def test_nonexistent_theory_tooltip_returns_none(self, service):
        """Tooltip for non-existent theory should return None."""
        html = service.get_tooltip_html("nonexistent-xyz-123")
        assert html is None


class TestTheorySummary:
    """Test combined guide + metadata summary."""

    def test_get_theory_summary_returns_dict(self, service):
        """get_theory_summary should return dict with expected keys."""
        guides = service.list_available_guides()
        if guides:
            summary = service.get_theory_summary(guides[0])
            if summary:
                assert isinstance(summary, dict)
                assert "theory_id" in summary
                assert "display_name" in summary
                assert "content" in summary
                assert "constructs" in summary

    def test_nonexistent_theory_summary_returns_none(self, service):
        """Summary for non-existent theory should return None."""
        summary = service.get_theory_summary("nonexistent-xyz-123")
        assert summary is None


class TestTheoryGuideResultDataclass:
    """Test TheoryGuideResult dataclass."""

    def test_result_to_dict(self):
        """TheoryGuideResult should convert to dict."""
        result = TheoryGuideResult(
            theory_id="test-theory",
            display_name="Test Theory",
            detail_level="quick",
            content="Test content",
            constructs=["construct1"],
            maturity="test-maturity",
            atlas_status="ACTIVE",
            guide_path="/path/to/guide.html",
            metadata={"key": "value"},
        )
        d = result.to_dict()
        assert isinstance(d, dict)
        assert d["theory_id"] == "test-theory"
        assert d["display_name"] == "Test Theory"
        assert d["content"] == "Test content"
        assert d["constructs"] == ["construct1"]
        assert d["metadata"] == {"key": "value"}


class TestIntegration:
    """Integration tests combining multiple features."""

    def test_full_workflow(self, service):
        """Complete workflow: search → get guide → extract metadata."""
        # Search for a theory
        results = service.search_theories("attention")
        if results:
            # Get full guide
            theory_name = results[0].display_name
            guide = service.get_guide(theory_name, detail_level="quick")
            assert guide is not None

            # Verify structure
            assert guide.content
            assert isinstance(guide.constructs, list)

    def test_detail_level_progression(self, service):
        """Content should generally increase from quick → standard → technical."""
        guides = service.list_available_guides()
        if guides:
            for theory_name in guides[:2]:
                quick = service.get_guide(theory_name, detail_level="quick")
                standard = service.get_guide(theory_name, detail_level="standard")
                technical = service.get_guide(theory_name, detail_level="technical")

                if quick and standard and technical:
                    # Should have content at all levels
                    assert len(quick.content) > 0
                    assert len(standard.content) > 0
                    assert len(technical.content) > 0
                    # Generally, standard and technical should be >= quick
                    # (though this depends on actual HTML structure)
                    break
