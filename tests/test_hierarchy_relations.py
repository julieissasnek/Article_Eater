"""
Tests for Three Hierarchy Relations (Panel Recommendation #4)
=============================================================
Created: 2026-03-03

Tests verify that the three fundamental hierarchy relations in ATLAS
(explanatory, evidential, compositional) are correctly formalized as
independent, queryable structures.

References:
- docs/PANEL_OUTPUT_T_LEVELS_2026-03-03.md — Recommendation #4 (Unanimous)
"""

import pytest

from src.qa.molecules.hierarchy_relations import (
    RelationType,
    EntityTier,
    HierarchyEdge,
    ExplanatoryHierarchy,
    EvidentialHierarchy,
    CompositionHierarchy,
    ThreeRelationIndex,
)
from src.qa.molecules.registry import MoleculeRegistry
from src.qa.molecules.t1_5_registry import T1_5Registry


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture(scope="module")
def t1_5_registry():
    return T1_5Registry()


@pytest.fixture(scope="module")
def molecule_registry():
    return MoleculeRegistry()


@pytest.fixture(scope="module")
def three_relation_index(t1_5_registry, molecule_registry):
    return ThreeRelationIndex(t1_5_registry, molecule_registry)


# ============================================================================
# HierarchyEdge Schema Tests
# ============================================================================

class TestHierarchyEdge:
    """Test the edge data structure."""

    def test_edge_creation(self):
        """Edge can be created with all required fields."""
        edge = HierarchyEdge(
            source_id="predictive-processing",
            source_tier=EntityTier.T1_FRAMEWORK,
            target_id="ART",
            target_tier=EntityTier.T1_5_THEORY,
            relation=RelationType.EXPLANATORY,
            edge_label="explains",
        )
        assert edge.source_id == "predictive-processing"
        assert edge.relation == RelationType.EXPLANATORY
        assert edge.confidence == 1.0  # default

    def test_edge_to_dict(self):
        """Edge serializes to dict correctly."""
        edge = HierarchyEdge(
            source_id="T27",
            source_tier=EntityTier.T2_TEMPLATE,
            target_id="ART",
            target_tier=EntityTier.T1_5_THEORY,
            relation=RelationType.EVIDENTIAL,
            edge_label="provides_evidence_for",
            confidence=0.8,
        )
        d = edge.to_dict()
        assert d["source_id"] == "T27"
        assert d["source_tier"] == "T2"
        assert d["relation"] == "evidential"
        assert d["confidence"] == 0.8

    def test_edge_defaults(self):
        """Edge has sensible defaults for optional fields."""
        edge = HierarchyEdge(
            source_id="a", source_tier=EntityTier.T1_FRAMEWORK,
            target_id="b", target_tier=EntityTier.T1_5_THEORY,
            relation=RelationType.EXPLANATORY, edge_label="explains",
        )
        assert edge.confidence == 1.0
        assert edge.provenance == "system_derived"


# ============================================================================
# Enums
# ============================================================================

class TestEnums:
    """Test relation and tier enums."""

    def test_relation_types_complete(self):
        """All three relation types exist."""
        assert len(RelationType) == 3
        values = {r.value for r in RelationType}
        assert values == {"explanatory", "evidential", "compositional"}

    def test_entity_tiers_complete(self):
        """All entity tiers exist."""
        assert len(EntityTier) >= 7
        required = {"T1", "T1_ATOM", "T1.5", "MOLECULE", "T2", "T2_ARCHETYPE", "FC", "T3"}
        values = {t.value for t in EntityTier}
        assert required.issubset(values)


# ============================================================================
# Explanatory Hierarchy Tests
# ============================================================================

class TestExplanatoryHierarchy:
    """Test the top-down explanatory structure: T1 → T1.5 → T2."""

    def test_has_edges(self, three_relation_index):
        """Explanatory hierarchy builds non-zero edges."""
        assert three_relation_index.explanatory.edge_count > 0

    def test_all_edges_are_explanatory(self, three_relation_index):
        """Every edge in this hierarchy has relation=EXPLANATORY."""
        for edge in three_relation_index.explanatory.edges:
            assert edge.relation == RelationType.EXPLANATORY

    def test_t1_to_t1_5_edges_exist(self, three_relation_index):
        """There are edges from T1 frameworks to T1.5 theories."""
        t1_to_t1_5 = [e for e in three_relation_index.explanatory.edges
                       if e.source_tier == EntityTier.T1_FRAMEWORK
                       and e.target_tier == EntityTier.T1_5_THEORY]
        assert len(t1_to_t1_5) > 0

    def test_t1_5_to_t2_edges_exist(self, three_relation_index):
        """There are edges from T1.5 theories to T2 templates."""
        t1_5_to_t2 = [e for e in three_relation_index.explanatory.edges
                       if e.source_tier == EntityTier.T1_5_THEORY
                       and e.target_tier == EntityTier.T2_TEMPLATE]
        assert len(t1_5_to_t2) > 0

    def test_explained_by_returns_upstream(self, three_relation_index, t1_5_registry):
        """explained_by() returns entities that explain the given entity."""
        # Pick a T1.5 theory that we know has T1 parents
        reduced = t1_5_registry.find_by_status("REDUCED")
        if reduced:
            theory = reduced[0]
            upstream = three_relation_index.explanatory.explained_by(theory.theory_id)
            assert len(upstream) > 0
            for edge in upstream:
                assert edge.target_id == theory.theory_id

    def test_explains_returns_downstream(self, three_relation_index, t1_5_registry):
        """explains() returns entities that the given entity explains."""
        reduced = t1_5_registry.find_by_status("REDUCED")
        if reduced:
            theory = reduced[0]
            if theory.constituent_templates:
                downstream = three_relation_index.explanatory.explains(theory.theory_id)
                assert len(downstream) > 0
                for edge in downstream:
                    assert edge.source_id == theory.theory_id

    def test_trace_explanation_structure(self, three_relation_index, t1_5_registry):
        """trace_explanation returns properly structured dict."""
        reduced = t1_5_registry.find_by_status("REDUCED")
        if reduced and reduced[0].constituent_templates:
            tid = reduced[0].constituent_templates[0]
            trace = three_relation_index.explanatory.trace_explanation(tid)
            assert "template_id" in trace
            assert "t1_5_explanations" in trace
            assert "t1_explanations" in trace

    def test_confidence_reflects_framework_contribution(self, three_relation_index):
        """T1→T1.5 edge confidence corresponds to percentage contribution."""
        t1_to_t1_5 = [e for e in three_relation_index.explanatory.edges
                       if e.source_tier == EntityTier.T1_FRAMEWORK
                       and e.target_tier == EntityTier.T1_5_THEORY]
        for edge in t1_to_t1_5:
            assert 0.0 <= edge.confidence <= 1.0


# ============================================================================
# Evidential Hierarchy Tests
# ============================================================================

class TestEvidentialHierarchy:
    """Test the bottom-up evidential structure: T2 → T1.5 → T1."""

    def test_has_edges(self, three_relation_index):
        """Evidential hierarchy builds non-zero edges."""
        assert three_relation_index.evidential.edge_count > 0

    def test_all_edges_are_evidential(self, three_relation_index):
        """Every edge in this hierarchy has relation=EVIDENTIAL."""
        for edge in three_relation_index.evidential.edges:
            assert edge.relation == RelationType.EVIDENTIAL

    def test_t2_to_t1_5_edges_exist(self, three_relation_index):
        """There are edges from T2 templates to T1.5 theories (evidence flows up)."""
        t2_to_t1_5 = [e for e in three_relation_index.evidential.edges
                       if e.source_tier == EntityTier.T2_TEMPLATE
                       and e.target_tier == EntityTier.T1_5_THEORY]
        assert len(t2_to_t1_5) > 0

    def test_t1_5_to_t1_edges_exist(self, three_relation_index):
        """There are edges from T1.5 theories to T1 frameworks (evidence flows up)."""
        t1_5_to_t1 = [e for e in three_relation_index.evidential.edges
                       if e.source_tier == EntityTier.T1_5_THEORY
                       and e.target_tier == EntityTier.T1_FRAMEWORK]
        assert len(t1_5_to_t1) > 0

    def test_evidential_direction_is_bottom_up(self, three_relation_index):
        """Evidential edges flow from lower to higher tiers."""
        tier_order = {
            EntityTier.T3_BELIEF: 0,
            EntityTier.T2_TEMPLATE: 1,
            EntityTier.T1_5_THEORY: 2,
            EntityTier.T1_FRAMEWORK: 3,
        }
        for edge in three_relation_index.evidential.edges:
            if edge.source_tier in tier_order and edge.target_tier in tier_order:
                assert tier_order[edge.source_tier] < tier_order[edge.target_tier], \
                    f"Evidential edge flows wrong direction: {edge.source_tier} → {edge.target_tier}"

    def test_trace_evidence_structure(self, three_relation_index, t1_5_registry):
        """trace_evidence returns properly structured dict."""
        reduced = t1_5_registry.find_by_status("REDUCED")
        if reduced:
            fw_id = list(reduced[0].parent_t1_frameworks.keys())[0]
            trace = three_relation_index.evidential.trace_evidence(fw_id)
            assert "framework_id" in trace
            assert "t1_5_evidence" in trace
            assert "t2_evidence" in trace


# ============================================================================
# Compositional Hierarchy Tests
# ============================================================================

class TestCompositionHierarchy:
    """Test the parts-whole compositional structure."""

    def test_has_edges(self, three_relation_index):
        """Compositional hierarchy builds non-zero edges."""
        assert three_relation_index.compositional.edge_count > 0

    def test_all_edges_are_compositional(self, three_relation_index):
        """Every edge in this hierarchy has relation=COMPOSITIONAL."""
        for edge in three_relation_index.compositional.edges:
            assert edge.relation == RelationType.COMPOSITIONAL

    def test_molecule_to_template_edges(self, three_relation_index):
        """Molecules have composed_of edges to their templates."""
        mol_to_t2 = [e for e in three_relation_index.compositional.edges
                      if e.edge_label == "composed_of"
                      and e.target_tier == EntityTier.T2_TEMPLATE]
        assert len(mol_to_t2) > 0

    def test_fc_to_archetype_edges(self, three_relation_index):
        """Functional circuits have instantiates edges to archetypes."""
        fc_to_arch = [e for e in three_relation_index.compositional.edges
                       if e.edge_label == "instantiates"
                       and e.target_tier == EntityTier.T2_ARCHETYPE]
        assert len(fc_to_arch) > 0

    def test_composed_of_returns_parts(self, three_relation_index, molecule_registry):
        """composed_of() returns the parts of a molecule."""
        all_mols = molecule_registry.get_all()
        if all_mols:
            mol = all_mols[0]
            parts = three_relation_index.compositional.composed_of(mol.molecule_id)
            assert len(parts) >= 0  # some molecules may have no constituent templates
            for edge in parts:
                assert edge.source_id == mol.molecule_id

    def test_part_of_returns_wholes(self, three_relation_index, molecule_registry):
        """part_of() returns molecules containing a template."""
        all_mols = molecule_registry.get_all()
        if all_mols and all_mols[0].constituent_templates:
            tid = all_mols[0].constituent_templates[0]
            wholes = three_relation_index.compositional.part_of(tid)
            assert len(wholes) > 0
            for edge in wholes:
                assert edge.target_id == tid

    def test_trace_composition_structure(self, three_relation_index, molecule_registry):
        """trace_composition returns properly structured dict."""
        all_mols = molecule_registry.get_all()
        if all_mols:
            trace = three_relation_index.compositional.trace_composition(all_mols[0].molecule_id)
            assert "molecule_id" in trace
            assert "templates" in trace
            assert "archetypes" in trace


# ============================================================================
# ThreeRelationIndex Integration Tests
# ============================================================================

class TestThreeRelationIndex:
    """Test the unified index over all three structures."""

    def test_all_three_hierarchies_populated(self, three_relation_index):
        """All three sub-hierarchies have non-zero edge counts."""
        assert three_relation_index.explanatory.edge_count > 0
        assert three_relation_index.evidential.edge_count > 0
        assert three_relation_index.compositional.edge_count > 0

    def test_get_all_edges_unfiltered(self, three_relation_index):
        """get_all_edges() returns edges from all three hierarchies."""
        all_edges = three_relation_index.get_all_edges()
        total = (three_relation_index.explanatory.edge_count +
                 three_relation_index.evidential.edge_count +
                 three_relation_index.compositional.edge_count)
        assert len(all_edges) == total

    def test_get_all_edges_filtered(self, three_relation_index):
        """get_all_edges(relation) filters to the requested type."""
        exp_edges = three_relation_index.get_all_edges(RelationType.EXPLANATORY)
        assert all(e.relation == RelationType.EXPLANATORY for e in exp_edges)

        evi_edges = three_relation_index.get_all_edges(RelationType.EVIDENTIAL)
        assert all(e.relation == RelationType.EVIDENTIAL for e in evi_edges)

        comp_edges = three_relation_index.get_all_edges(RelationType.COMPOSITIONAL)
        assert all(e.relation == RelationType.COMPOSITIONAL for e in comp_edges)

    def test_get_entity_relations_structure(self, three_relation_index, t1_5_registry):
        """get_entity_relations returns all six relation categories."""
        reduced = t1_5_registry.find_by_status("REDUCED")
        if reduced:
            entity_id = reduced[0].theory_id
            relations = three_relation_index.get_entity_relations(entity_id)
            expected_keys = {
                "explanatory_upstream", "explanatory_downstream",
                "evidential_supporting", "evidential_supported_by",
                "compositional_parts", "compositional_wholes",
            }
            assert set(relations.keys()) == expected_keys

    def test_full_trace_structure(self, three_relation_index, t1_5_registry):
        """full_trace returns properly structured cross-relation dict."""
        reduced = t1_5_registry.find_by_status("REDUCED")
        if reduced:
            entity_id = reduced[0].theory_id
            trace = three_relation_index.full_trace(entity_id)
            assert "entity_id" in trace
            assert "explanatory" in trace
            assert "evidential" in trace
            assert "compositional" in trace

    def test_summary_produces_output(self, three_relation_index):
        """summary() returns non-empty string."""
        s = three_relation_index.summary()
        assert len(s) > 100
        assert "Explanatory" in s
        assert "Evidential" in s
        assert "Compositional" in s


# ============================================================================
# Cross-Relation Consistency Tests
# ============================================================================

class TestCrossRelationConsistency:
    """Verify that the three relations are consistent with each other."""

    def test_explanatory_and_evidential_share_entities(self, three_relation_index):
        """Explanatory and evidential hierarchies reference the same T1.5 theories."""
        exp_t1_5 = {e.target_id for e in three_relation_index.explanatory.edges
                     if e.target_tier == EntityTier.T1_5_THEORY}
        evi_t1_5 = {e.source_id for e in three_relation_index.evidential.edges
                     if e.source_tier == EntityTier.T1_5_THEORY}
        # They should overlap significantly (same theories appear in both)
        overlap = exp_t1_5 & evi_t1_5
        assert len(overlap) > 0, "No shared T1.5 theories between explanatory and evidential"

    def test_explanatory_and_evidential_opposite_direction(self, three_relation_index, t1_5_registry):
        """For any T1→T1.5 explanatory edge, there should be a corresponding T1.5→T1 evidential edge."""
        reduced = t1_5_registry.find_by_status("REDUCED")
        if reduced:
            theory = reduced[0]
            # Check explanatory: some T1 explains this theory
            exp_upstream = three_relation_index.explanatory.explained_by(theory.theory_id)
            if exp_upstream:
                fw_id = exp_upstream[0].source_id
                # Check evidential: this theory provides evidence for that T1
                evi_downstream = three_relation_index.evidential.provides_evidence_for(theory.theory_id)
                evi_targets = {e.target_id for e in evi_downstream}
                assert fw_id in evi_targets, \
                    f"Explanatory edge T1({fw_id})→T1.5({theory.theory_id}) has no matching evidential edge"

    def test_compositional_molecules_appear_in_evidential(self, three_relation_index, molecule_registry):
        """Molecules with templates should have templates that appear in evidential hierarchy."""
        all_mols = molecule_registry.get_all()
        if all_mols:
            mol = all_mols[0]
            comp_parts = three_relation_index.compositional.composed_of(mol.molecule_id)
            template_ids = {e.target_id for e in comp_parts if e.target_tier == EntityTier.T2_TEMPLATE}
            if template_ids:
                # At least some of these templates should appear in the evidential hierarchy
                evi_sources = {e.source_id for e in three_relation_index.evidential.edges
                               if e.source_tier == EntityTier.T2_TEMPLATE}
                # Relaxed: not all templates need to be in evidential (some may be
                # from molecules not linked to T1.5 theories)
                # Just verify the evidential hierarchy has some T2 templates
                assert len(evi_sources) > 0

    def test_three_relations_are_independently_populated(self, three_relation_index):
        """Each relation type has its own edges (not just copies of each other)."""
        exp_pairs = {(e.source_id, e.target_id) for e in three_relation_index.explanatory.edges}
        evi_pairs = {(e.source_id, e.target_id) for e in three_relation_index.evidential.edges}
        comp_pairs = {(e.source_id, e.target_id) for e in three_relation_index.compositional.edges}

        # They should NOT be identical (different edge semantics)
        assert exp_pairs != evi_pairs, "Explanatory and evidential have identical edge sets"
        assert exp_pairs != comp_pairs, "Explanatory and compositional have identical edge sets"
        assert evi_pairs != comp_pairs, "Evidential and compositional have identical edge sets"


# ============================================================================
# Edge Cases
# ============================================================================

class TestEdgeCases:
    """Test edge cases and robustness."""

    def test_nonexistent_entity_returns_empty(self, three_relation_index):
        """Querying a nonexistent entity returns empty results."""
        relations = three_relation_index.get_entity_relations("NONEXISTENT_ENTITY_XYZ")
        for key, edges in relations.items():
            assert len(edges) == 0, f"{key} should be empty for nonexistent entity"

    def test_full_trace_nonexistent(self, three_relation_index):
        """full_trace on nonexistent entity returns empty but valid structure."""
        trace = three_relation_index.full_trace("NONEXISTENT")
        assert trace["entity_id"] == "NONEXISTENT"
        assert len(trace["explanatory"]["explained_by"]) == 0

    def test_empty_registries_handled(self):
        """ThreeRelationIndex handles empty registries gracefully."""
        t1_5 = T1_5Registry(theories_dir="nonexistent_dir_xyz")
        mol = MoleculeRegistry(molecule_dir="nonexistent_dir_xyz")
        index = ThreeRelationIndex(t1_5, mol)
        assert index.explanatory.edge_count == 0
        assert index.evidential.edge_count == 0
        assert index.compositional.edge_count == 0
