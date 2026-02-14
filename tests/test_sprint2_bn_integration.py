"""
Tests for Sprint 2: BN Integration.

Verifies:
- Task 2.1: All 10 epistemic BN variables defined correctly
- Task 2.2: Environmental subgraph edges wired correctly
- Task 2.3: Source quality subgraph (added later)
- Task 2.4: Pathway type tagging
"""

import pytest


class TestTask21EpistemicBNNodes:
    """Task 2.1: Verify all 10 epistemic BN node definitions."""

    def test_can_import_epistemic_module(self):
        """The epistemic module is importable."""
        from src.epistemic import bn_nodes
        assert bn_nodes is not None

    def test_all_10_variables_defined(self):
        """All 10 required epistemic variables exist."""
        from src.epistemic.bn_nodes import EPISTEMIC_VARIABLES

        required_vars = [
            "environmental_legibility",
            "belief_coherence",
            "epistemic_fluency",
            "epistemic_affect",
            "functional_PE",
            "navigational_PE",
            "social_PE",
            "source_quality",
            "claim_acceptance",
            "claim_coherence",
        ]

        assert len(EPISTEMIC_VARIABLES) == 10
        for var_id in required_vars:
            assert var_id in EPISTEMIC_VARIABLES, f"Missing variable: {var_id}"

    def test_environmental_legibility_properties(self):
        """Environmental legibility has correct properties."""
        from src.epistemic.bn_nodes import ENVIRONMENTAL_LEGIBILITY

        assert ENVIRONMENTAL_LEGIBILITY.var_id == "environmental_legibility"
        assert ENVIRONMENTAL_LEGIBILITY.domain == (0.0, 1.0)
        assert ENVIRONMENTAL_LEGIBILITY.is_latent is True

    def test_epistemic_affect_bipolar_scale(self):
        """Epistemic affect has bipolar scale (-1, 1)."""
        from src.epistemic.bn_nodes import EPISTEMIC_AFFECT

        assert EPISTEMIC_AFFECT.var_id == "epistemic_affect"
        assert EPISTEMIC_AFFECT.domain == (-1.0, 1.0)
        assert EPISTEMIC_AFFECT.is_observable is True

    def test_pe_variables_grouped(self):
        """Prediction error variables are properly grouped."""
        from src.epistemic.bn_nodes import get_pe_variables

        pe_vars = get_pe_variables()
        assert len(pe_vars) == 3

        pe_ids = [v.var_id for v in pe_vars]
        assert "functional_PE" in pe_ids
        assert "navigational_PE" in pe_ids
        assert "social_PE" in pe_ids

    def test_variable_serialization(self):
        """Variables can be serialized to dict."""
        from src.epistemic.bn_nodes import ENVIRONMENTAL_LEGIBILITY

        d = ENVIRONMENTAL_LEGIBILITY.to_dict()
        assert d["var_id"] == "environmental_legibility"
        assert d["var_type"] == "continuous"
        assert isinstance(d["domain"], list)


class TestTask22EnvironmentalSubgraph:
    """Task 2.2: Verify environmental subgraph edges."""

    def test_can_import_edges_module(self):
        """The bn_edges module is importable."""
        from src.epistemic import bn_edges
        assert bn_edges is not None

    def test_all_required_edges_exist(self):
        """All 8 required environmental edges are wired."""
        from src.epistemic.bn_edges import ENVIRONMENTAL_EDGES

        # Convert to set of (source, target) tuples for easy checking
        edge_tuples = {(e.source, e.target) for e in ENVIRONMENTAL_EDGES}

        required_edges = [
            ("environmental_legibility", "epistemic_fluency"),
            ("epistemic_fluency", "epistemic_affect"),
            ("epistemic_affect", "overall_wellbeing"),
            ("functional_PE", "epistemic_affect"),
            ("navigational_PE", "epistemic_affect"),
            ("social_PE", "epistemic_affect"),
            ("environmental_legibility", "wayfinding_success"),
            ("epistemic_affect", "allostatic_regulation"),
        ]

        for src, tgt in required_edges:
            assert (src, tgt) in edge_tuples, f"Missing edge: {src} -> {tgt}"

    def test_edges_are_acyclic(self):
        """The environmental subgraph is a valid DAG (no cycles)."""
        from src.epistemic.bn_edges import is_acyclic

        assert is_acyclic() is True

    def test_edge_connectivity_valid(self):
        """All edge endpoints reference defined variables."""
        from src.epistemic.bn_edges import validate_edge_connectivity

        missing = validate_edge_connectivity()
        assert len(missing) == 0, f"Missing variables: {missing}"

    def test_stub_nodes_defined(self):
        """Stub nodes for external connections are defined."""
        from src.epistemic.bn_edges import STUB_NODES

        assert "overall_wellbeing" in STUB_NODES
        assert "wayfinding_success" in STUB_NODES
        assert "allostatic_regulation" in STUB_NODES

    def test_topological_order(self):
        """Variables can be topologically sorted."""
        from src.epistemic.bn_edges import get_topological_order

        order = get_topological_order()

        # environmental_legibility should come before epistemic_fluency
        assert order.index("environmental_legibility") < order.index("epistemic_fluency")

        # epistemic_fluency should come before epistemic_affect
        assert order.index("epistemic_fluency") < order.index("epistemic_affect")

    def test_edges_have_pathway_type(self):
        """All edges are tagged with pathway_type."""
        from src.epistemic.bn_edges import ENVIRONMENTAL_EDGES

        for edge in ENVIRONMENTAL_EDGES:
            assert edge.pathway_type is not None, f"Edge {edge.source} -> {edge.target} missing pathway_type"

    def test_pe_edges_negative_weight(self):
        """Prediction error edges have negative weights (reduce affect)."""
        from src.epistemic.bn_edges import ENVIRONMENTAL_EDGES

        pe_sources = {"functional_PE", "navigational_PE", "social_PE"}

        for edge in ENVIRONMENTAL_EDGES:
            if edge.source in pe_sources and edge.target == "epistemic_affect":
                assert edge.weight < 0, f"PE edge {edge.source} should have negative weight"

    def test_get_edges_as_tuples(self):
        """Edges can be exported as (source, target) tuples for DAG libraries."""
        from src.epistemic.bn_edges import get_edges_as_tuples

        tuples = get_edges_as_tuples()
        # 8 environmental + 6 source quality = 14 total
        assert len(tuples) == 14
        assert all(isinstance(t, tuple) and len(t) == 2 for t in tuples)

    def test_get_edges_for_variable(self):
        """Can query edges by source or target variable."""
        from src.epistemic.bn_edges import get_edges_for_variable

        # epistemic_affect has 4 incoming edges
        incoming = get_edges_for_variable("epistemic_affect", as_source=False)
        assert len(incoming) == 4

        # epistemic_affect has 2 outgoing edges
        outgoing = get_edges_for_variable("epistemic_affect", as_source=True)
        assert len(outgoing) == 2


class TestTask23SourceQualitySubgraph:
    """Task 2.3: Source quality subgraph edges."""

    def test_source_quality_component_nodes_exist(self):
        """All 4 source quality component nodes are defined."""
        from src.epistemic.bn_nodes import SOURCE_QUALITY_COMPONENTS

        required = [
            "methodological_rigor",
            "theoretical_commitment",
            "independence_of_evidence",
            "replication_status",
        ]

        assert len(SOURCE_QUALITY_COMPONENTS) == 4
        for var_id in required:
            assert var_id in SOURCE_QUALITY_COMPONENTS, f"Missing: {var_id}"

    def test_source_quality_edges_exist(self):
        """All 6 source quality subgraph edges are wired."""
        from src.epistemic.bn_edges import SOURCE_QUALITY_EDGES

        edge_tuples = {(e.source, e.target) for e in SOURCE_QUALITY_EDGES}

        required_edges = [
            ("methodological_rigor", "source_quality"),
            ("theoretical_commitment", "source_quality"),
            ("independence_of_evidence", "source_quality"),
            ("replication_status", "source_quality"),
            ("source_quality", "claim_acceptance"),
            ("claim_coherence", "claim_acceptance"),
        ]

        assert len(SOURCE_QUALITY_EDGES) == 6
        for src, tgt in required_edges:
            assert (src, tgt) in edge_tuples, f"Missing edge: {src} -> {tgt}"

    def test_theoretical_commitment_negative_weight(self):
        """Theoretical commitment has negative influence on source quality."""
        from src.epistemic.bn_edges import SOURCE_QUALITY_EDGES

        for edge in SOURCE_QUALITY_EDGES:
            if edge.source == "theoretical_commitment" and edge.target == "source_quality":
                assert edge.weight < 0, "Theoretical commitment should have negative weight"
                break
        else:
            pytest.fail("theoretical_commitment -> source_quality edge not found")

    def test_combined_graph_still_acyclic(self):
        """The combined (environmental + source quality) graph is still acyclic."""
        from src.epistemic.bn_edges import is_acyclic, ALL_EPISTEMIC_EDGES

        # Verify we have all edges combined
        assert len(ALL_EPISTEMIC_EDGES) == 14  # 8 environmental + 6 source quality
        assert is_acyclic() is True

    def test_all_source_quality_edges_tagged(self):
        """All source quality edges have pathway_type."""
        from src.epistemic.bn_edges import SOURCE_QUALITY_EDGES

        for edge in SOURCE_QUALITY_EDGES:
            assert edge.pathway_type is not None

    def test_get_source_quality_edges_function(self):
        """Helper function returns source quality edges."""
        from src.epistemic.bn_edges import get_source_quality_edges

        edges = get_source_quality_edges()
        assert len(edges) == 6

    def test_get_all_variables_includes_components(self):
        """get_all_variables() includes source quality component nodes."""
        from src.epistemic.bn_edges import get_all_variables

        all_vars = get_all_variables()

        # Should have: 10 epistemic + 4 source quality components + 3 stubs = 17
        assert "methodological_rigor" in all_vars
        assert "theoretical_commitment" in all_vars
        assert "independence_of_evidence" in all_vars
        assert "replication_status" in all_vars


class TestTask24PathwayTagging:
    """Task 2.4: Pathway type tagging."""

    def test_pathway_defaults_exists(self):
        """PATHWAY_DEFAULTS lookup table is defined."""
        from src.epistemic.bn_edges import PATHWAY_DEFAULTS, PathwayType

        assert isinstance(PATHWAY_DEFAULTS, dict)
        assert len(PATHWAY_DEFAULTS) > 0

        # Check some expected entries
        assert PATHWAY_DEFAULTS["temperature"] == PathwayType.SUBPERSONAL
        assert PATHWAY_DEFAULTS["wayfinding"] == PathwayType.PERSONAL_EPISTEMIC
        assert PATHWAY_DEFAULTS["lighting"] == PathwayType.MIXED

    def test_assign_pathway_type_basic(self):
        """assign_pathway_type correctly assigns based on source keyword."""
        from src.epistemic.bn_edges import assign_pathway_type, PathwayType, EpistemicEdge

        # Create test edges
        thermal_edge = EpistemicEdge(source="thermal_comfort", target="wellbeing")
        spatial_edge = EpistemicEdge(source="spatial_layout", target="wayfinding")
        light_edge = EpistemicEdge(source="lighting_quality", target="productivity")

        assert assign_pathway_type(thermal_edge) == PathwayType.SUBPERSONAL
        assert assign_pathway_type(spatial_edge) == PathwayType.PERSONAL_EPISTEMIC
        assert assign_pathway_type(light_edge) == PathwayType.MIXED

    def test_assign_pathway_type_default(self):
        """assign_pathway_type defaults to MIXED for unknown sources."""
        from src.epistemic.bn_edges import assign_pathway_type, PathwayType, EpistemicEdge

        unknown_edge = EpistemicEdge(source="xyz_unknown_var", target="output")
        assert assign_pathway_type(unknown_edge) == PathwayType.MIXED

    def test_assign_pathway_type_tuple_input(self):
        """assign_pathway_type works with tuple edges."""
        from src.epistemic.bn_edges import assign_pathway_type, PathwayType

        edge_tuple = ("temperature_level", "thermal_comfort")
        assert assign_pathway_type(edge_tuple) == PathwayType.SUBPERSONAL

    def test_all_epistemic_edges_tagged(self):
        """Every edge in the epistemic BN has a non-null pathway_type."""
        from src.epistemic.bn_edges import validate_all_edges_tagged

        untagged = validate_all_edges_tagged()
        assert len(untagged) == 0, f"Untagged edges: {[e.source for e in untagged]}"

    def test_get_edges_by_pathway(self):
        """Can filter edges by pathway type."""
        from src.epistemic.bn_edges import get_edges_by_pathway, PathwayType

        personal_edges = get_edges_by_pathway(PathwayType.PERSONAL_EPISTEMIC)
        assert len(personal_edges) > 0
        for edge in personal_edges:
            assert edge.pathway_type == "personal_epistemic"

    def test_tag_edges_with_pathway(self):
        """tag_edges_with_pathway returns (edge, pathway) tuples."""
        from src.epistemic.bn_edges import tag_edges_with_pathway, PathwayType, EpistemicEdge

        test_edges = [
            EpistemicEdge(source="thermal_x", target="y"),
            EpistemicEdge(source="legibility_x", target="y"),
        ]

        tagged = tag_edges_with_pathway(test_edges)
        assert len(tagged) == 2
        assert tagged[0][1] == PathwayType.SUBPERSONAL
        assert tagged[1][1] == PathwayType.PERSONAL_EPISTEMIC

    def test_pathway_categories_comprehensive(self):
        """PATHWAY_DEFAULTS covers subpersonal, personal, and mixed categories."""
        from src.epistemic.bn_edges import PATHWAY_DEFAULTS, PathwayType

        pathways = set(PATHWAY_DEFAULTS.values())
        assert PathwayType.SUBPERSONAL in pathways
        assert PathwayType.PERSONAL_EPISTEMIC in pathways
        assert PathwayType.MIXED in pathways


class TestTask25SourceQualityComputation:
    """Task 2.5: Source quality computation function."""

    def test_can_import_source_quality(self):
        """Source quality module is importable."""
        from src.epistemic import source_quality
        assert source_quality is not None

    def test_compute_source_quality_basic(self):
        """compute_source_quality returns value in [0, 1]."""
        from src.epistemic.source_quality import compute_source_quality

        result = compute_source_quality(0.5, 0.5, 0.5, 0.5)
        assert 0.0 <= result <= 1.0

    def test_high_quality_case(self):
        """High quality: good methods, independent, replicated, low commitment."""
        from src.epistemic.source_quality import compute_source_quality

        # Best case scenario
        quality = compute_source_quality(0.9, 0.1, 0.9, 0.9)
        assert quality > 0.8, f"Expected > 0.8, got {quality}"

    def test_low_quality_case(self):
        """Low quality: weak methods, single lab, unreplicated, high commitment."""
        from src.epistemic.source_quality import compute_source_quality

        # Worst case scenario
        quality = compute_source_quality(0.2, 0.9, 0.1, 0.0)
        assert quality < 0.3, f"Expected < 0.3, got {quality}"

    def test_commitment_penalty(self):
        """High theoretical commitment should reduce quality score."""
        from src.epistemic.source_quality import compute_source_quality

        # Identical except commitment differs
        high_commit = compute_source_quality(0.8, 0.8, 0.7, 0.7)
        low_commit = compute_source_quality(0.8, 0.2, 0.7, 0.7)

        assert low_commit > high_commit, "Low commitment should yield higher quality"

    def test_input_validation(self):
        """Out-of-range inputs should raise ValueError."""
        from src.epistemic.source_quality import compute_source_quality

        with pytest.raises(ValueError):
            compute_source_quality(1.5, 0.5, 0.5, 0.5)  # rigor > 1

        with pytest.raises(ValueError):
            compute_source_quality(0.5, -0.1, 0.5, 0.5)  # commitment < 0

    def test_custom_weights(self):
        """Custom weights can be provided."""
        from src.epistemic.source_quality import compute_source_quality

        # All weight on rigor
        custom_weights = {
            "rigor": 1.0,
            "commitment": 0.0,
            "independence": 0.0,
            "replication": 0.0,
        }

        quality = compute_source_quality(0.9, 0.9, 0.1, 0.1, weights=custom_weights)
        assert quality == pytest.approx(0.9, abs=0.01)

    def test_detailed_result(self):
        """compute_source_quality_detailed returns SourceQualityResult."""
        from src.epistemic.source_quality import compute_source_quality_detailed

        result = compute_source_quality_detailed(0.8, 0.2, 0.7, 0.6)

        assert hasattr(result, 'composite_score')
        assert hasattr(result, 'quality_level')
        assert hasattr(result, 'to_dict')

        # Verify component contributions sum to composite
        contributions = (
            result.rigor_contribution +
            result.commitment_contribution +
            result.independence_contribution +
            result.replication_contribution
        )
        assert contributions == pytest.approx(result.composite_score, abs=0.001)

    def test_quality_level_classification(self):
        """Quality levels are correctly classified."""
        from src.epistemic.source_quality import classify_quality

        assert classify_quality(0.9) == "high"
        assert classify_quality(0.6) == "moderate"
        assert classify_quality(0.35) == "low"
        assert classify_quality(0.2) == "very_low"

    def test_default_weights_sum_to_one(self):
        """Default weights should sum to 1.0."""
        from src.epistemic.source_quality import DEFAULT_SOURCE_QUALITY_WEIGHTS

        total = sum(DEFAULT_SOURCE_QUALITY_WEIGHTS.values())
        assert total == pytest.approx(1.0, abs=0.001)
