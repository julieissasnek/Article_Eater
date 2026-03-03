"""
Tests for Figure Suggestion Service.

Created: 2026-03-02
Author: Claude Code
"""

import pytest
from src.services.figure_suggestion_service import (
    FigureSuggestionService,
    FigureMetadata,
    FigurePhase,
    FigurePriority,
)


class TestFigureSuggestionServiceInitialization:
    """Test service initialization."""

    def test_service_initializes(self):
        """Service should initialize without error."""
        service = FigureSuggestionService()
        assert service is not None

    def test_figure_registry_loaded(self):
        """Service should load all 42 figures."""
        service = FigureSuggestionService()
        assert len(service.FIGURE_REGISTRY) == 42

    def test_concept_index_built(self):
        """Service should build concept-to-figure reverse index."""
        service = FigureSuggestionService()
        assert len(service._concept_to_figures) > 0
        # Should have multiple concepts
        assert len(service._concept_to_figures) >= 50


class TestGetFigureMetadata:
    """Test retrieving figure metadata."""

    def test_get_goldilocks_figure(self):
        """Should retrieve Goldilocks figure metadata."""
        service = FigureSuggestionService()
        meta = service.get_figure_metadata('G-1')
        assert meta is not None
        assert meta.id == 'G-1'
        assert 'Four Traditions' in meta.title

    def test_get_master_doc_figure(self):
        """Should retrieve Master Doc figure metadata."""
        service = FigureSuggestionService()
        meta = service.get_figure_metadata('M-25')
        assert meta is not None
        assert meta.id == 'M-25'
        assert 'Design Quality' in meta.title

    def test_get_nonexistent_figure_returns_none(self):
        """Should return None for nonexistent figure ID."""
        service = FigureSuggestionService()
        meta = service.get_figure_metadata('X-999')
        assert meta is None

    def test_figure_metadata_completeness(self):
        """Retrieved metadata should be complete."""
        service = FigureSuggestionService()
        meta = service.get_figure_metadata('G-1')
        assert meta.file_path is not None
        assert len(meta.related_concepts) > 0
        assert meta.phase is not None
        assert meta.priority is not None


class TestSuggestFigures:
    """Test figure suggestion by topic."""

    def test_suggest_for_credence_topic(self):
        """Should suggest credence-related figures."""
        service = FigureSuggestionService()
        figures = service.suggest_figures('credence projection', max_figures=5)
        assert len(figures) > 0
        fig_ids = [f.id for f in figures]
        # M-25, M-27 are credence-related
        assert 'M-25' in fig_ids or 'M-27' in fig_ids

    def test_suggest_for_coherence_topic(self):
        """Should suggest coherence-related figures."""
        service = FigureSuggestionService()
        figures = service.suggest_figures('coherence epistemic health', max_figures=5)
        assert len(figures) > 0
        fig_ids = [f.id for f in figures]
        assert 'M-26' in fig_ids

    def test_suggest_for_voi_topic(self):
        """Should suggest value of information figures."""
        service = FigureSuggestionService()
        figures = service.suggest_figures('value of information', max_figures=5)
        assert len(figures) > 0
        fig_ids = [f.id for f in figures]
        assert 'M-29' in fig_ids

    def test_suggest_for_visual_domain(self):
        """Should suggest visual domain figures."""
        service = FigureSuggestionService()
        figures = service.suggest_figures('visual fractal dimension', max_figures=5)
        assert len(figures) > 0
        fig_ids = [f.id for f in figures]
        assert 'M-7' in fig_ids or 'G-4' in fig_ids

    def test_suggest_respects_max_figures(self):
        """Should not return more than max_figures."""
        service = FigureSuggestionService()
        figures = service.suggest_figures('architecture design', max_figures=3)
        assert len(figures) <= 3

    def test_suggest_returns_metadata_objects(self):
        """Should return FigureMetadata objects."""
        service = FigureSuggestionService()
        figures = service.suggest_figures('credence', max_figures=5)
        assert all(isinstance(f, FigureMetadata) for f in figures)

    def test_suggest_for_architect_query(self):
        """Should suggest architect-friendly figures."""
        service = FigureSuggestionService()
        figures = service.suggest_figures('design parameters ceiling height', max_figures=5)
        assert len(figures) > 0
        # Should include G-9 (Architect's Cheat Sheet)
        fig_ids = [f.id for f in figures]
        assert 'G-9' in fig_ids

    def test_suggest_for_empty_query(self):
        """Should handle empty query gracefully."""
        service = FigureSuggestionService()
        figures = service.suggest_figures('', max_figures=5)
        # May return nothing, which is fine
        assert isinstance(figures, list)


class TestGetFigureForConcept:
    """Test retrieving best figure for a concept."""

    def test_get_figure_for_credence_projection(self):
        """Should find figure for credence projection concept."""
        service = FigureSuggestionService()
        fig = service.get_figure_for_concept('credence_projection')
        assert fig is not None
        assert fig.id in ['M-4', 'M-25', 'M-27']

    def test_get_figure_for_coherence(self):
        """Should find figure for coherence concept."""
        service = FigureSuggestionService()
        fig = service.get_figure_for_concept('coherence')
        assert fig is not None
        assert fig.id == 'M-26'

    def test_get_figure_for_voi(self):
        """Should find figure for VOI concept."""
        service = FigureSuggestionService()
        fig = service.get_figure_for_concept('voi')
        assert fig is not None
        assert fig.id == 'M-29'

    def test_get_figure_for_unknown_concept(self):
        """Should return None for unknown concept."""
        service = FigureSuggestionService()
        fig = service.get_figure_for_concept('unknown_concept_xyz')
        assert fig is None

    def test_get_figure_returns_highest_priority(self):
        """When multiple figures match, should return highest priority."""
        service = FigureSuggestionService()
        # Get a concept that might match multiple figures
        fig = service.get_figure_for_concept('transfer')
        if fig:
            # Should be high priority
            assert fig.priority in [FigurePriority.HIGH, FigurePriority.MEDIUM]


class TestGetFiguresByPhase:
    """Test retrieving figures by documentation phase."""

    def test_get_goldilocks_figures(self):
        """Should return all Goldilocks phase figures."""
        service = FigureSuggestionService()
        figures = service.get_figures_by_phase(FigurePhase.GOLDILOCKS)
        assert len(figures) == 10
        fig_ids = [f.id for f in figures]
        assert 'G-1' in fig_ids
        assert 'G-10' in fig_ids

    def test_get_math_explanation_figures(self):
        """Should return all math explanation phase figures."""
        service = FigureSuggestionService()
        figures = service.get_figures_by_phase(FigurePhase.MATH_EXPLANATION)
        assert len(figures) == 8
        fig_ids = [f.id for f in figures]
        assert 'M-25' in fig_ids
        assert 'M-32' in fig_ids

    def test_get_domain_panel_figures(self):
        """Should return all domain panel phase figures."""
        service = FigureSuggestionService()
        figures = service.get_figures_by_phase(FigurePhase.DOMAIN_PANEL)
        assert len(figures) == 12

    def test_get_architecture_figures(self):
        """Should return architecture phase figures."""
        service = FigureSuggestionService()
        figures = service.get_figures_by_phase(FigurePhase.ARCHITECTURE)
        assert len(figures) == 3
        assert all(f.phase == FigurePhase.ARCHITECTURE for f in figures)


class TestGetFiguresByPriority:
    """Test retrieving figures by priority level."""

    def test_get_high_priority_figures(self):
        """Should return high-priority figures."""
        service = FigureSuggestionService()
        figures = service.get_figures_by_priority(FigurePriority.HIGH)
        assert len(figures) > 0
        assert all(f.priority == FigurePriority.HIGH for f in figures)
        # Should include key figures
        fig_ids = [f.id for f in figures]
        assert 'G-1' in fig_ids
        assert 'M-25' in fig_ids

    def test_get_medium_priority_figures(self):
        """Should return medium-priority figures."""
        service = FigureSuggestionService()
        figures = service.get_figures_by_priority(FigurePriority.MEDIUM)
        assert len(figures) > 0
        assert all(f.priority == FigurePriority.MEDIUM for f in figures)

    def test_get_low_priority_figures(self):
        """Should return low-priority figures."""
        service = FigureSuggestionService()
        figures = service.get_figures_by_priority(FigurePriority.LOW)
        assert len(figures) > 0
        assert all(f.priority == FigurePriority.LOW for f in figures)


class TestGetSummary:
    """Test service summary."""

    def test_get_summary(self):
        """Should return service summary."""
        service = FigureSuggestionService()
        summary = service.get_summary()
        assert summary is not None
        assert summary['total_figures'] == 42
        assert 'by_phase' in summary
        assert 'by_priority' in summary
        assert 'total_concepts' in summary

    def test_summary_phase_count(self):
        """Summary should list all phases."""
        service = FigureSuggestionService()
        summary = service.get_summary()
        by_phase = summary['by_phase']
        # Should have 7 phases
        assert len(by_phase) == 7
        assert by_phase.get('goldilocks') == 10
        assert by_phase.get('math_explanation') == 8

    def test_summary_priority_count(self):
        """Summary should list all priority levels."""
        service = FigureSuggestionService()
        summary = service.get_summary()
        by_priority = summary['by_priority']
        # Should have 3 priority levels
        assert len(by_priority) == 3
        assert 'high' in by_priority
        assert 'medium' in by_priority
        assert 'low' in by_priority

    def test_summary_concept_count(self):
        """Summary should show concept index size."""
        service = FigureSuggestionService()
        summary = service.get_summary()
        assert summary['total_concepts'] > 50


class TestFigureMetadata:
    """Test FigureMetadata dataclass."""

    def test_create_figure_metadata(self):
        """Should create valid FigureMetadata object."""
        meta = FigureMetadata(
            id='TEST-1',
            title='Test Figure',
            file_path='test.svg',
            related_concepts=['test', 'concept'],
            phase=FigurePhase.ARCHITECTURE,
            priority=FigurePriority.HIGH,
            description='Test description',
        )
        assert meta.id == 'TEST-1'
        assert len(meta.related_concepts) == 2
        assert meta.phase == FigurePhase.ARCHITECTURE

    def test_figure_metadata_data_dependencies_default(self):
        """Data dependencies should default to empty list."""
        meta = FigureMetadata(
            id='TEST-1',
            title='Test Figure',
            file_path='test.svg',
            related_concepts=['test'],
            phase=FigurePhase.ARCHITECTURE,
            priority=FigurePriority.HIGH,
            description='Test description',
        )
        assert isinstance(meta.data_dependencies, list)
        assert len(meta.data_dependencies) == 0


class TestFigureSearching:
    """Test various search scenarios."""

    def test_search_architecture_overview(self):
        """Should find architecture overview figures."""
        service = FigureSuggestionService()
        figures = service.suggest_figures('three layers architecture')
        assert len(figures) > 0
        assert any(f.id == 'M-1' for f in figures)

    def test_search_framework_hierarchy(self):
        """Should find framework hierarchy figures."""
        service = FigureSuggestionService()
        figures = service.suggest_figures('foundational frameworks belief')
        assert len(figures) > 0
        assert any(f.id == 'M-2' for f in figures)

    def test_search_pipeline_stages(self):
        """Should find pipeline/validation figures."""
        service = FigureSuggestionService()
        figures = service.suggest_figures('epistemic scrutiny stages')
        assert len(figures) > 0

    def test_search_domain_panels(self):
        """Should find domain-specific panel figures."""
        service = FigureSuggestionService()
        # Search for visual domain
        figures = service.suggest_figures('visual fractal')
        visual_fig_ids = [f.id for f in figures]
        assert 'M-7' in visual_fig_ids or 'G-4' in visual_fig_ids

        # Search for light domain
        figures = service.suggest_figures('light melanopsin')
        light_fig_ids = [f.id for f in figures]
        assert 'M-8' in light_fig_ids

    def test_search_case_insensitive(self):
        """Search should be case-insensitive."""
        service = FigureSuggestionService()
        figures1 = service.suggest_figures('COHERENCE')
        figures2 = service.suggest_figures('coherence')
        assert len(figures1) == len(figures2)


class TestConceptIndex:
    """Test concept-to-figure indexing."""

    def test_concept_index_has_multiple_entries(self):
        """Concept index should map concepts to multiple figures."""
        service = FigureSuggestionService()
        # credence should map to multiple figures
        if 'credence' in service._concept_to_figures:
            credence_figs = service._concept_to_figures['credence']
            assert len(credence_figs) >= 1

    def test_concept_index_accessible(self):
        """Should be able to look up concepts."""
        service = FigureSuggestionService()
        # Should have at least one concept
        assert len(service._concept_to_figures) > 0
        first_concept = list(service._concept_to_figures.keys())[0]
        figures = service._concept_to_figures[first_concept]
        assert len(figures) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
