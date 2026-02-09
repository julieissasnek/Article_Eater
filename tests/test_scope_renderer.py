"""
Tests for Scope-Aware Output Renderer
Sprint 3.0.2-C

Tests scope extraction, transferability assessment, and response rendering.
"""

import pytest
from src.services.scope_renderer import (
    ScopeRenderer,
    ScopeContext,
    ScopeCondition,
    ScopedEvidence,
    ScopedResponse,
    ScopeConfidence,
    GeneralizabilityLevel,
    TransferabilityAssessment,
    ScopeMismatch,
    render_with_scope,
    format_scope_for_display,
    get_scope_renderer
)


class TestScopeRenderer:
    """Tests for ScopeRenderer class."""

    def setup_method(self):
        self.renderer = ScopeRenderer()

    # =========================================================================
    # Scope Extraction Tests
    # =========================================================================

    def test_extract_population_from_content(self):
        """Should extract population from belief content."""
        scope = self.renderer.extract_scope_from_belief(
            belief_id="b1",
            content="Office workers showed reduced stress after plant exposure"
        )
        assert 'population' in scope
        assert 'workers' in scope['population'].value.lower()
        assert scope['population'].explicit is False

    def test_extract_setting_from_content(self):
        """Should extract setting from belief content."""
        scope = self.renderer.extract_scope_from_belief(
            belief_id="b1",
            content="In hospital environments, natural light improved recovery"
        )
        assert 'setting' in scope
        assert 'hospital' in scope['setting'].value.lower()

    def test_extract_duration_from_content(self):
        """Should extract duration from belief content."""
        scope = self.renderer.extract_scope_from_belief(
            belief_id="b1",
            content="After 20 minutes of nature exposure, cortisol decreased"
        )
        assert 'duration' in scope
        assert '20' in scope['duration'].value or 'minutes' in scope['duration'].value.lower()

    def test_extract_methodology_from_content(self):
        """Should extract methodology from belief content."""
        scope = self.renderer.extract_scope_from_belief(
            belief_id="b1",
            content="An RCT demonstrated that plants reduce stress"
        )
        assert 'methodology' in scope
        assert 'rct' in scope['methodology'].value.lower()

    def test_extract_nature_type_from_content(self):
        """Should extract nature type for CNfA domain."""
        scope = self.renderer.extract_scope_from_belief(
            belief_id="b1",
            content="Indoor plants were associated with improved mood"
        )
        assert 'nature_type' in scope
        assert 'plant' in scope['nature_type'].value.lower()

    def test_existing_scope_takes_precedence(self):
        """Existing scope metadata should take precedence over extraction."""
        existing = {'population': 'healthcare workers', 'setting': 'ICU'}
        scope = self.renderer.extract_scope_from_belief(
            belief_id="b1",
            content="Office workers showed reduced stress",
            existing_scope=existing
        )
        # Should use existing scope, not extracted
        assert scope['population'].value == 'healthcare workers'
        assert scope['population'].explicit is True
        assert scope['population'].confidence == 0.9

    def test_multiple_scope_dimensions(self):
        """Should extract multiple scope dimensions."""
        scope = self.renderer.extract_scope_from_belief(
            belief_id="b1",
            content="A laboratory experiment with healthy adults showed that "
                   "30 minutes of forest imagery reduced stress"
        )
        # Should find population, setting, duration, methodology
        assert 'population' in scope  # adults
        assert 'methodology' in scope  # experiment
        assert 'duration' in scope  # 30 minutes

    # =========================================================================
    # Transferability Assessment Tests
    # =========================================================================

    def test_transferability_with_matching_scope(self):
        """Should assess high transferability when scopes match."""
        evidence_scope = {
            'population': ScopeCondition('population', 'office workers', True, 'b1', 0.9),
            'setting': ScopeCondition('setting', 'office', True, 'b1', 0.9)
        }
        query_scope = ScopeContext(population='workers', setting='office')

        assessment = self.renderer.assess_transferability(evidence_scope, query_scope)

        assert assessment.transferable is True
        assert assessment.confidence in (ScopeConfidence.HIGH, ScopeConfidence.MODERATE)
        assert len(assessment.supporting_factors) > 0

    def test_transferability_with_population_mismatch(self):
        """Should detect population mismatch."""
        evidence_scope = {
            'population': ScopeCondition('population', 'children', True, 'b1', 0.9)
        }
        query_scope = ScopeContext(population='elderly')

        assessment = self.renderer.assess_transferability(evidence_scope, query_scope)

        assert len(assessment.mismatches) > 0
        assert assessment.mismatches[0].dimension == 'population'

    def test_transferability_lab_vs_field_warning(self):
        """Should warn about lab evidence transferring to field."""
        evidence_scope = {
            'methodology': ScopeCondition('methodology', 'laboratory experiment', True, 'b1', 0.9)
        }
        query_scope = ScopeContext(setting='real-world office')

        assessment = self.renderer.assess_transferability(evidence_scope, query_scope)

        assert len(assessment.warnings) > 0
        assert any('controlled' in w.lower() or 'lab' in w.lower()
                  for w in assessment.warnings)

    def test_transferability_unknown_when_no_scope(self):
        """Should return unknown confidence when scope is minimal."""
        evidence_scope = {}
        query_scope = ScopeContext(population='adults')

        assessment = self.renderer.assess_transferability(evidence_scope, query_scope)

        assert assessment.confidence in (ScopeConfidence.UNKNOWN, ScopeConfidence.LOW)
        assert len(assessment.warnings) > 0

    # =========================================================================
    # Scoped Evidence Rendering Tests
    # =========================================================================

    def test_render_scoped_evidence_basic(self):
        """Should render evidence with scope annotation."""
        scoped = self.renderer.render_scoped_evidence(
            belief_id="b1",
            content="Indoor plants reduce stress in office workers",
            credence=0.75
        )

        assert scoped.belief_id == "b1"
        assert scoped.credence == 0.75
        assert scoped.population is not None  # Should extract 'workers'
        assert scoped.nature_type is not None  # Should extract 'plants'

    def test_render_scoped_evidence_with_warnings(self):
        """Should generate warnings when scope is incomplete."""
        scoped = self.renderer.render_scoped_evidence(
            belief_id="b1",
            content="Something affects something",  # Vague, no scope
            credence=0.5
        )

        assert scoped.scope_completeness < 0.5
        assert scoped.requires_warning is True
        assert len(scoped.warning_messages) > 0

    def test_render_scoped_evidence_with_query_scope(self):
        """Should assess transferability when query scope provided."""
        query_scope = ScopeContext(population='elderly', setting='hospital')

        scoped = self.renderer.render_scoped_evidence(
            belief_id="b1",
            content="Young adults in offices showed stress reduction",
            credence=0.75,
            query_scope=query_scope
        )

        assert scoped.transferability is not None
        # Should flag potential mismatch (young adults vs elderly, office vs hospital)

    # =========================================================================
    # Scoped Response Rendering Tests
    # =========================================================================

    def test_render_scoped_response_basic(self):
        """Should render complete response with scope."""
        evidence = [
            {'belief_id': 'b1', 'content': 'Plants reduce stress in adults', 'credence': 0.7},
            {'belief_id': 'b2', 'content': 'Office greenery improves mood', 'credence': 0.65}
        ]

        response = self.renderer.render_scoped_response(
            headline="Plants reduce stress",
            main_finding="Evidence supports stress reduction from plants",
            evidence_items=evidence
        )

        assert response.headline == "Plants reduce stress"
        assert len(response.evidence) == 2
        assert response.scope_summary is not None
        assert 'populations' in response.scope_summary
        assert len(response.generalization_limits) > 0

    def test_render_scoped_response_with_query_scope(self):
        """Should assess transferability for all evidence."""
        evidence = [
            {'belief_id': 'b1', 'content': 'Laboratory study with students', 'credence': 0.7}
        ]
        query_scope = ScopeContext(population='workers', setting='office')

        response = self.renderer.render_scoped_response(
            headline="Test",
            main_finding="Test finding",
            evidence_items=evidence,
            query_scope=query_scope
        )

        assert response.transferability_summary is not None
        assert 'transfer' in response.transferability_summary.lower()

    def test_render_scoped_response_aggregates_scope(self):
        """Should aggregate scope across evidence items."""
        evidence = [
            {'belief_id': 'b1', 'content': 'Adults in offices', 'credence': 0.7,
             'scope': {'population': 'adults', 'setting': 'office'}},
            {'belief_id': 'b2', 'content': 'Workers in hospitals', 'credence': 0.65,
             'scope': {'population': 'healthcare workers', 'setting': 'hospital'}}
        ]

        response = self.renderer.render_scoped_response(
            headline="Test",
            main_finding="Test",
            evidence_items=evidence
        )

        # Should aggregate both populations and settings
        assert len(response.scope_summary['populations']) >= 2
        assert len(response.scope_summary['settings']) >= 2

    def test_applies_when_generated(self):
        """Should generate applicability statements."""
        evidence = [
            {'belief_id': 'b1', 'content': 'RCT with adults in office', 'credence': 0.7,
             'scope': {'population': 'adults', 'setting': 'office'}}
        ]

        response = self.renderer.render_scoped_response(
            headline="Test",
            main_finding="Test",
            evidence_items=evidence
        )

        assert len(response.applies_when) > 0
        assert len(response.does_not_apply_when) > 0

    def test_generalization_limits_for_lab_only(self):
        """Should flag generalization limits for lab-only evidence."""
        evidence = [
            {'belief_id': 'b1', 'content': 'Laboratory experiment showed', 'credence': 0.7},
            {'belief_id': 'b2', 'content': 'Controlled lab study found', 'credence': 0.65}
        ]

        response = self.renderer.render_scoped_response(
            headline="Test",
            main_finding="Test",
            evidence_items=evidence
        )

        # Should warn about lab-only evidence
        limits_text = ' '.join(response.generalization_limits).lower()
        assert 'lab' in limits_text or 'controlled' in limits_text

    # =========================================================================
    # Convenience Function Tests
    # =========================================================================

    def test_render_with_scope_function(self):
        """Should work via convenience function."""
        evidence = [
            {'belief_id': 'b1', 'content': 'Plants reduce stress', 'credence': 0.7}
        ]

        response = render_with_scope(
            headline="Plants help",
            main_finding="Evidence supports plant benefits",
            evidence_items=evidence,
            query_population="office workers"
        )

        assert isinstance(response, ScopedResponse)
        assert response.headline == "Plants help"

    def test_format_scope_for_display(self):
        """Should format response for UI display."""
        evidence = [
            {'belief_id': 'b1', 'content': 'Test evidence', 'credence': 0.7}
        ]

        response = render_with_scope(
            headline="Test",
            main_finding="Test finding",
            evidence_items=evidence
        )

        display = format_scope_for_display(response)

        assert 'headline' in display
        assert 'scope' in display
        assert 'confidence' in display['scope']
        assert 'warnings' in display
        assert 'evidence' in display

    def test_get_scope_renderer_singleton(self):
        """Should return singleton renderer."""
        r1 = get_scope_renderer()
        r2 = get_scope_renderer()
        assert r1 is r2


class TestScopeConfidenceLevels:
    """Test scope confidence assignment."""

    def setup_method(self):
        self.renderer = ScopeRenderer()

    def test_high_confidence_with_explicit_matching_scope(self):
        """High confidence when explicit scope matches."""
        evidence_scope = {
            'population': ScopeCondition('population', 'adults', True, 'b1', 0.9),
            'setting': ScopeCondition('setting', 'office', True, 'b1', 0.9)
        }
        query_scope = ScopeContext(population='adults', setting='office')

        assessment = self.renderer.assess_transferability(evidence_scope, query_scope)
        assert assessment.confidence == ScopeConfidence.HIGH

    def test_moderate_confidence_with_partial_match(self):
        """Moderate confidence with some mismatches."""
        evidence_scope = {
            'population': ScopeCondition('population', 'students', True, 'b1', 0.9),
            'setting': ScopeCondition('setting', 'office', True, 'b1', 0.9)
        }
        # Population differs but setting matches
        query_scope = ScopeContext(population='workers', setting='office')

        assessment = self.renderer.assess_transferability(evidence_scope, query_scope)
        # Should be moderate due to population difference
        assert assessment.confidence in (ScopeConfidence.MODERATE, ScopeConfidence.LOW)

    def test_unknown_confidence_with_no_scope(self):
        """Unknown confidence when scope not available."""
        evidence_scope = {}
        query_scope = ScopeContext()

        assessment = self.renderer.assess_transferability(evidence_scope, query_scope)
        # With no scope info, should default to unknown or low
        assert assessment.confidence in (ScopeConfidence.UNKNOWN, ScopeConfidence.LOW)


class TestGeneralizabilityLevels:
    """Test generalizability level assignment."""

    def setup_method(self):
        self.renderer = ScopeRenderer()

    def test_domain_specific_with_good_match(self):
        """Domain-specific when scope matches well."""
        evidence_scope = {
            'population': ScopeCondition('population', 'workers', True, 'b1', 0.9),
            'setting': ScopeCondition('setting', 'office', True, 'b1', 0.9)
        }
        query_scope = ScopeContext(population='employees', setting='workplace')

        assessment = self.renderer.assess_transferability(evidence_scope, query_scope)
        # Good match should be domain-specific
        assert assessment.generalizability in (
            GeneralizabilityLevel.DOMAIN_SPECIFIC,
            GeneralizabilityLevel.CONTEXT_BOUND
        )

    def test_context_bound_with_mismatches(self):
        """Context-bound when there are scope mismatches."""
        evidence_scope = {
            'population': ScopeCondition('population', 'children', True, 'b1', 0.9)
        }
        query_scope = ScopeContext(population='elderly')

        assessment = self.renderer.assess_transferability(evidence_scope, query_scope)
        # Mismatch should limit generalizability
        assert assessment.generalizability in (
            GeneralizabilityLevel.CONTEXT_BOUND,
            GeneralizabilityLevel.SAMPLE_SPECIFIC
        )


class TestEdgeCases:
    """Test edge cases and error handling."""

    def setup_method(self):
        self.renderer = ScopeRenderer()

    def test_empty_evidence_list(self):
        """Should handle empty evidence list."""
        response = self.renderer.render_scoped_response(
            headline="No evidence",
            main_finding="No evidence found",
            evidence_items=[]
        )

        assert response.headline == "No evidence"
        assert len(response.evidence) == 0
        assert response.overall_scope_confidence == ScopeConfidence.UNKNOWN

    def test_missing_belief_id(self):
        """Should handle evidence without belief_id."""
        evidence = [
            {'content': 'Some finding', 'credence': 0.5}
        ]

        response = self.renderer.render_scoped_response(
            headline="Test",
            main_finding="Test",
            evidence_items=evidence
        )

        assert len(response.evidence) == 1
        assert response.evidence[0].belief_id == 'unknown'

    def test_malformed_scope_data(self):
        """Should handle malformed scope data gracefully."""
        evidence = [
            {'belief_id': 'b1', 'content': 'Test', 'credence': 0.5,
             'scope': 'invalid'}  # Should be dict
        ]

        # Should not raise
        response = self.renderer.render_scoped_response(
            headline="Test",
            main_finding="Test",
            evidence_items=evidence
        )

        assert len(response.evidence) == 1

    def test_unicode_in_content(self):
        """Should handle unicode in content."""
        scoped = self.renderer.render_scoped_evidence(
            belief_id="b1",
            content="研究显示植物减少压力 (plants reduce stress)",
            credence=0.7
        )

        assert scoped.content is not None
        # Should still try to extract nature_type
        assert scoped.nature_type is not None
