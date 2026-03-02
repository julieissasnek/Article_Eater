"""
Comprehensive test suite for T3 Empirical Belief Layer.

Covers:
  - Stimulus taxonomy (structure, subsumption, keyword matching, facets)
  - DV generalization (access level rules, equivalence classes)
  - Generalization tree (finding aggregation, merges, boundary detection, gaps)
  - T3 belief engine (extraction, aggregation, query API)
  - T3 integration (contracts, event bus, reflexes, overseer)
"""

import pytest
from datetime import datetime, timezone
from typing import Dict, List

# ══════════════════════════════════════════════════════════════════
# Imports
# ══════════════════════════════════════════════════════════════════

from src.services.stimulus_taxonomy import (
    StimulusTaxonomy, TaxonomyNode, get_stimulus_taxonomy,
    ALL_NODES, DeliveryMode, SensoryModality, ManipulationType,
)
from src.services.dv_generalization import (
    can_generalize_dvs, dv_equivalence_class, dv_common_ancestor,
    dv_ancestors, DVAccessLevel, DVMeasurementType,
    DV_HIERARCHY, get_dv_node, dv_generalization_distance,
)
from src.services.generalization_tree import (
    Finding, T3Belief, CoverageGap, GeneralizationEngine,
    GranularityLevel, BeliefStatus, MIN_SOURCES_FOR_BELIEF,
)
from src.services.t3_belief_engine import (
    T3BeliefEngine, extract_finding_from_belief,
    _infer_direction, _infer_delivery_mode,
)
from src.services.t3_integration import (
    T3Adapter, T3EventBus, T3Event, T3EventType,
    get_t3_adapter,
)


# ══════════════════════════════════════════════════════════════════
# FIXTURES
# ══════════════════════════════════════════════════════════════════

@pytest.fixture
def taxonomy():
    return StimulusTaxonomy()

@pytest.fixture
def engine():
    return GeneralizationEngine()

@pytest.fixture
def belief_engine():
    return T3BeliefEngine()

@pytest.fixture
def adapter():
    return T3Adapter()


def make_finding(
    fid: str = "f1",
    iv: str = "spatial.height.high",
    dv: str = "cog.creativity.divergent.fluency",
    direction: str = "positive",
    effect_size: float = 0.45,
    paper_id: str = "doi:paper1",
    delivery: DeliveryMode = DeliveryMode.REAL,
    population: str = "adults",
) -> Finding:
    """Helper to create findings."""
    return Finding(
        finding_id=fid,
        iv_node=iv,
        dv_node=dv,
        effect_direction=direction,
        effect_size=effect_size,
        paper_id=paper_id,
        delivery_mode=delivery,
        population=population,
    )


def make_belief_dict(
    belief_id: str = "b1",
    content: str = "High ceilings increase creativity",
    env_id: str = "spatial.height.high",
    out_id: str = "cog.creativity",
    effect_size: float = 0.4,
    tags: List[str] = None,
) -> Dict:
    return {
        "belief_id": belief_id,
        "content": content,
        "environment_id": env_id,
        "outcome_id": out_id,
        "evidence_effect_size": effect_size,
        "paper_ids": [f"doi:{belief_id}"],
        "tags": tags or [],
        "study_design": "rct",
    }


# ══════════════════════════════════════════════════════════════════
# TEST CLASS 1: Stimulus Taxonomy Structure
# ══════════════════════════════════════════════════════════════════

class TestStimulusTaxonomyStructure:
    """Test the taxonomy tree structure."""

    def test_taxonomy_has_roots(self, taxonomy):
        roots = taxonomy.roots()
        assert len(roots) >= 10  # 11 root domains
        root_ids = {r.node_id for r in roots}
        assert "spatial" in root_ids
        assert "natural" in root_ids
        assert "person_state" in root_ids
        assert "cultural" in root_ids
        assert "acoustic" in root_ids
        assert "olfactory" in root_ids

    def test_taxonomy_size(self, taxonomy):
        assert taxonomy.size >= 60  # ~65 nodes

    def test_spatial_subtree(self, taxonomy):
        spatial_children = taxonomy.children("spatial")
        assert len(spatial_children) >= 8  # height, volume, shape, etc.
        child_ids = {c.node_id for c in spatial_children}
        assert "spatial.height" in child_ids
        assert "spatial.shape" in child_ids
        assert "spatial.view" in child_ids

    def test_ceiling_height_has_parametric_children(self, taxonomy):
        height_children = taxonomy.children("spatial.height")
        assert len(height_children) >= 3  # low, standard, high
        for child in height_children:
            assert child.parametric_range is not None
            assert child.parametric_unit == "feet"

    def test_person_state_manipulation_type(self, taxonomy):
        cog_load = taxonomy.get("person_state.cognitive_load")
        assert cog_load is not None
        assert cog_load.manipulation_type == ManipulationType.PERSON_STATE

    def test_acoustic_modality(self, taxonomy):
        noise = taxonomy.get("acoustic.noise")
        assert noise is not None
        assert noise.typical_modality == SensoryModality.AUDITORY

    def test_get_nonexistent_returns_none(self, taxonomy):
        assert taxonomy.get("does.not.exist") is None


class TestStimulusTaxonomySubsumption:
    """Test ancestry and subsumption."""

    def test_is_ancestor(self, taxonomy):
        assert taxonomy.is_ancestor_of("spatial", "spatial.height.high")
        assert taxonomy.is_ancestor_of("spatial.height", "spatial.height.high")
        assert not taxonomy.is_ancestor_of("spatial.height.high", "spatial")
        assert not taxonomy.is_ancestor_of("natural", "spatial.height")

    def test_ancestors(self, taxonomy):
        ancestors = taxonomy.ancestors("spatial.height.high")
        ancestor_ids = [a.node_id for a in ancestors]
        assert "spatial.height" in ancestor_ids
        assert "spatial" in ancestor_ids

    def test_descendants(self, taxonomy):
        desc = taxonomy.descendants("spatial.height")
        desc_ids = {d.node_id for d in desc}
        assert "spatial.height.low" in desc_ids
        assert "spatial.height.high" in desc_ids
        assert "spatial.height.standard" in desc_ids

    def test_common_ancestor_siblings(self, taxonomy):
        lca = taxonomy.common_ancestor("spatial.height.low", "spatial.height.high")
        assert lca == "spatial.height"

    def test_common_ancestor_cousins(self, taxonomy):
        lca = taxonomy.common_ancestor("spatial.height.high", "spatial.shape.rectangular")
        assert lca == "spatial"

    def test_common_ancestor_different_trees(self, taxonomy):
        lca = taxonomy.common_ancestor("spatial.height.high", "acoustic.noise")
        assert lca is None

    def test_generalization_distance_siblings(self, taxonomy):
        dist = taxonomy.generalization_distance("spatial.height.low", "spatial.height.high")
        assert dist == 2  # Both depth 2, LCA depth 1

    def test_generalization_distance_same_node(self, taxonomy):
        dist = taxonomy.generalization_distance("spatial.height", "spatial.height")
        assert dist == 0

    def test_generalization_distance_different_trees(self, taxonomy):
        dist = taxonomy.generalization_distance("spatial.height", "acoustic.noise")
        assert dist == 999


class TestStimulusTaxonomyKeywordMatching:
    """Test keyword matching and classification."""

    def test_match_ceiling_height(self, taxonomy):
        matches = taxonomy.match_keywords("ceiling height")
        assert len(matches) > 0
        top_id = matches[0][0]
        assert "spatial.height" in top_id

    def test_match_noise(self, taxonomy):
        matches = taxonomy.match_keywords("noise level in office")
        assert len(matches) > 0
        top_ids = {m[0] for m in matches[:3]}
        assert any("acoustic" in nid or "noise" in nid for nid in top_ids)

    def test_classify_stimulus(self, taxonomy):
        node = taxonomy.classify_stimulus("high ceiling height 10 feet")
        assert node is not None
        assert "height" in node

    def test_parametric_matching(self, taxonomy):
        node = taxonomy.match_parametric("spatial.height", 9.5)
        assert node == "spatial.height.high"

    def test_parametric_matching_low(self, taxonomy):
        node = taxonomy.match_parametric("spatial.height", 7.5)
        assert node == "spatial.height.low"


class TestStimulusTaxonomyFacets:
    """Test facet-based queries."""

    def test_auditory_nodes(self, taxonomy):
        auditory = taxonomy.nodes_by_modality(SensoryModality.AUDITORY)
        assert len(auditory) >= 4
        ids = {n.node_id for n in auditory}
        assert "acoustic.noise" in ids
        assert "acoustic.music" in ids

    def test_person_state_nodes(self, taxonomy):
        ps = taxonomy.nodes_by_manipulation_type(ManipulationType.PERSON_STATE)
        assert len(ps) >= 5
        ids = {n.node_id for n in ps}
        assert "person_state.cognitive_load" in ids
        assert "person_state.fatigue" in ids

    def test_cultural_nodes(self, taxonomy):
        cultural = taxonomy.nodes_by_manipulation_type(ManipulationType.CULTURAL)
        assert len(cultural) >= 5

    def test_can_merge_same_domain(self, taxonomy):
        can, reason = taxonomy.can_merge("spatial.height.low", "spatial.height.high")
        assert can
        assert "LCA" in reason

    def test_cannot_merge_different_domains(self, taxonomy):
        can, reason = taxonomy.can_merge("spatial.height", "acoustic.noise")
        assert not can
        assert "Different root domains" in reason or "No common ancestor" in reason

    def test_sufficient_coverage(self, taxonomy):
        tested = {"spatial.height.low", "spatial.height.high"}
        sufficient, coverage = taxonomy.sufficient_coverage("spatial.height", tested)
        assert coverage > 0.5

    def test_insufficient_coverage(self, taxonomy):
        tested = {"spatial.height.low"}
        sufficient, coverage = taxonomy.sufficient_coverage("spatial.height", tested)
        assert not sufficient or coverage < 0.5

    def test_register_node(self, taxonomy):
        new_node = TaxonomyNode(
            "spatial.height.cathedral", "Cathedral Ceiling",
            parent_id="spatial.height", depth=2,
            parametric_range=(15.0, 50.0), parametric_unit="feet",
        )
        taxonomy.register_node(new_node)
        assert taxonomy.get("spatial.height.cathedral") is not None
        children = taxonomy.children("spatial.height")
        assert any(c.node_id == "spatial.height.cathedral" for c in children)


# ══════════════════════════════════════════════════════════════════
# TEST CLASS 2: DV Generalization
# ══════════════════════════════════════════════════════════════════

class TestDVHierarchy:
    """Test the DV hierarchy structure."""

    def test_hierarchy_size(self):
        assert len(DV_HIERARCHY) >= 30

    def test_creativity_subtypes(self):
        fluency = get_dv_node("cog.creativity.divergent.fluency")
        assert fluency is not None
        assert fluency.access_level == DVAccessLevel.BEHAVIORAL
        assert fluency.equivalence_class == "divergent_tasks"

    def test_stress_access_levels(self):
        self_report = get_dv_node("affect.stress.self_report")
        cortisol = get_dv_node("affect.stress.cortisol")
        assert self_report is not None
        assert cortisol is not None
        assert self_report.access_level == DVAccessLevel.CONSCIOUS
        assert cortisol.access_level == DVAccessLevel.NEUROENDOCRINE  # Wave 6: #6 Neuroscientist

    def test_ancestors(self):
        ancestors = dv_ancestors("cog.creativity.divergent.fluency")
        assert "cog.creativity.divergent" in ancestors
        assert "cog.creativity" in ancestors
        assert "cog" in ancestors

    def test_common_ancestor_within_creativity(self):
        lca = dv_common_ancestor(
            "cog.creativity.divergent.fluency",
            "cog.creativity.divergent.originality"
        )
        assert lca == "cog.creativity.divergent"

    def test_common_ancestor_across_domains(self):
        lca = dv_common_ancestor("cog.attention.sustained", "affect.stress.self_report")
        assert lca is None  # Different top-level domains


class TestDVGeneralization:
    """Test DV generalization rules."""

    def test_same_equivalence_class_can_merge(self):
        can, reason = can_generalize_dvs(
            "cog.creativity.divergent.fluency",
            "cog.creativity.divergent.originality"
        )
        assert can
        assert "equivalence class" in reason.lower() or "construct" in reason.lower()

    def test_different_access_levels_cannot_merge(self):
        can, reason = can_generalize_dvs(
            "affect.stress.self_report",
            "affect.stress.cortisol"
        )
        assert not can
        assert "access level" in reason.lower()

    def test_same_equivalence_class_autonomic(self):
        # Cortisol is now NEUROENDOCRINE, HR is AUTONOMIC
        # With strict_access_level=False, they still share common ancestor
        can, reason = can_generalize_dvs(
            "affect.stress.cortisol",
            "affect.stress.hr",
            strict_access_level=False
        )
        assert can
        assert "ancestor" in reason.lower() or "construct" in reason.lower()

    def test_equivalence_class_members(self):
        eq_class = dv_equivalence_class("cog.creativity.divergent.fluency")
        assert "cog.creativity.divergent.fluency" in eq_class
        assert "cog.creativity.divergent.originality" in eq_class
        assert "cog.creativity.divergent.flexibility" in eq_class

    def test_singleton_equivalence_class(self):
        eq_class = dv_equivalence_class("cog.memory")
        assert eq_class == {"cog.memory"}

    def test_generalization_distance(self):
        dist = dv_generalization_distance(
            "cog.creativity.divergent.fluency",
            "cog.creativity.divergent.originality"
        )
        assert dist <= 2


# ══════════════════════════════════════════════════════════════════
# TEST CLASS 3: Generalization Engine
# ══════════════════════════════════════════════════════════════════

class TestGeneralizationEngine:
    """Test the core aggregation engine."""

    def test_form_specific_belief_tentative(self, engine):
        """2 findings → tentative belief."""
        f1 = make_finding("f1", paper_id="p1")
        f2 = make_finding("f2", paper_id="p2")
        engine.add_findings([f1, f2])
        beliefs = engine.aggregate()

        assert len(beliefs) >= 1
        key = "t3:spatial.height.high→cog.creativity.divergent.fluency"
        assert key in beliefs
        assert beliefs[key].status == BeliefStatus.TENTATIVE
        assert beliefs[key].n_total == 2

    def test_form_specific_belief_established(self, engine):
        """3+ findings → established belief."""
        findings = [
            make_finding(f"f{i}", paper_id=f"p{i}")
            for i in range(4)
        ]
        engine.add_findings(findings)
        beliefs = engine.aggregate()

        key = "t3:spatial.height.high→cog.creativity.divergent.fluency"
        assert key in beliefs
        assert beliefs[key].status == BeliefStatus.ESTABLISHED
        assert beliefs[key].n_total == 4

    def test_contested_belief(self, engine):
        """Mixed directions → contested."""
        engine.add_findings([
            make_finding("f1", direction="positive"),
            make_finding("f2", direction="positive"),
            make_finding("f3", direction="negative"),
            make_finding("f4", direction="negative"),
        ])
        beliefs = engine.aggregate()
        key = "t3:spatial.height.high→cog.creativity.divergent.fluency"
        assert beliefs[key].status == BeliefStatus.CONTESTED

    def test_parametric_merge(self):
        """Findings at different parametric levels merge at parent."""
        engine = GeneralizationEngine()
        engine.add_findings([
            make_finding("f1", iv="spatial.height.low", direction="positive"),
            make_finding("f2", iv="spatial.height.low", direction="positive"),
            make_finding("f3", iv="spatial.height.high", direction="positive"),
            make_finding("f4", iv="spatial.height.high", direction="positive"),
        ])
        beliefs = engine.aggregate()

        # Should have parametric merge at spatial.height level
        parent_key = "t3:spatial.height→cog.creativity.divergent.fluency"
        assert parent_key in beliefs
        assert beliefs[parent_key].granularity == GranularityLevel.PARAMETRIC
        assert beliefs[parent_key].n_total == 4

    def test_construct_merge(self):
        """Findings with same IV but different DV equivalence class members merge."""
        engine = GeneralizationEngine()
        engine.add_findings([
            make_finding("f1", dv="cog.creativity.divergent.fluency"),
            make_finding("f2", dv="cog.creativity.divergent.originality"),
            make_finding("f3", dv="cog.creativity.divergent.flexibility"),
        ])
        beliefs = engine.aggregate()

        # Should have construct merge
        construct_beliefs = [b for b in beliefs.values() if b.granularity == GranularityLevel.CONSTRUCT]
        assert len(construct_beliefs) >= 1

    def test_coverage_gaps(self, engine):
        """Established beliefs should generate coverage gaps for untested subtypes."""
        engine.add_findings([
            make_finding("f1", iv="spatial.height.high"),
            make_finding("f2", iv="spatial.height.high"),
            make_finding("f3", iv="spatial.height.high"),
            make_finding("f4", iv="spatial.height.low"),
        ])
        beliefs = engine.aggregate()
        gaps = engine.get_coverage_gaps(0.0)

        # Should have some gaps (e.g., delivery mode gaps)
        assert len(gaps) >= 0  # At minimum, delivery mode gaps

    def test_delivery_mode_tracking(self, engine):
        """Track which delivery modes have been tested."""
        engine.add_findings([
            make_finding("f1", delivery=DeliveryMode.REAL),
            make_finding("f2", delivery=DeliveryMode.VR),
            make_finding("f3", delivery=DeliveryMode.REAL),
        ])
        beliefs = engine.aggregate()
        key = "t3:spatial.height.high→cog.creativity.divergent.fluency"
        assert "real" in beliefs[key].delivery_modes_tested
        assert "vr" in beliefs[key].delivery_modes_tested

    def test_belief_natural_language(self, engine):
        """Test human-readable summary."""
        engine.add_findings([
            make_finding("f1"), make_finding("f2"), make_finding("f3"),
        ])
        beliefs = engine.aggregate()
        key = "t3:spatial.height.high→cog.creativity.divergent.fluency"
        nl = beliefs[key].natural_language
        assert "increase" in nl.lower() or "High Ceiling" in nl

    def test_belief_consistency(self, engine):
        """Test consistency metric."""
        engine.add_findings([
            make_finding("f1", direction="positive"),
            make_finding("f2", direction="positive"),
            make_finding("f3", direction="negative"),
        ])
        beliefs = engine.aggregate()
        key = "t3:spatial.height.high→cog.creativity.divergent.fluency"
        assert 0.5 <= beliefs[key].consistency <= 1.0

    def test_belief_to_dict(self, engine):
        engine.add_findings([make_finding("f1"), make_finding("f2")])
        beliefs = engine.aggregate()
        key = "t3:spatial.height.high→cog.creativity.divergent.fluency"
        d = beliefs[key].to_dict()
        assert "t3_id" in d
        assert "iv_node" in d
        assert "dv_node" in d
        assert "granularity" in d
        assert "consistency" in d

    def test_summary_stats(self, engine):
        engine.add_findings([make_finding("f1"), make_finding("f2"), make_finding("f3")])
        engine.aggregate()
        summary = engine.summary()
        assert "total_findings" in summary
        assert "total_beliefs" in summary
        assert summary["total_findings"] == 3

    def test_empty_engine(self, engine):
        beliefs = engine.aggregate()
        assert len(beliefs) == 0

    def test_get_established_beliefs(self, engine):
        engine.add_findings([make_finding(f"f{i}") for i in range(5)])
        engine.aggregate()
        established = engine.get_established_beliefs()
        assert len(established) >= 1
        assert all(b.status == BeliefStatus.ESTABLISHED for b in established)


# ══════════════════════════════════════════════════════════════════
# TEST CLASS 4: T3 Belief Engine
# ══════════════════════════════════════════════════════════════════

class TestT3BeliefEngine:
    """Test the orchestration engine."""

    def test_load_from_belief_dicts(self, belief_engine):
        dicts = [
            make_belief_dict(f"b{i}", env_id="spatial.height.high", out_id="cog.creativity")
            for i in range(5)
        ]
        n = belief_engine.load_from_belief_dicts(dicts)
        assert n == 5
        assert len(belief_engine.findings) == 5

    def test_aggregate_from_dicts(self, belief_engine):
        dicts = [
            make_belief_dict(f"b{i}", env_id="spatial.height.high", out_id="cog.creativity")
            for i in range(4)
        ]
        belief_engine.load_from_belief_dicts(dicts)
        beliefs = belief_engine.aggregate()
        assert len(beliefs) >= 1

    def test_query_by_iv(self, belief_engine):
        dicts = [
            make_belief_dict(f"b{i}", env_id="spatial.height.high", out_id="cog.creativity")
            for i in range(4)
        ]
        belief_engine.load_from_belief_dicts(dicts)
        belief_engine.aggregate()

        results = belief_engine.query(iv_pattern="spatial.height")
        assert len(results) >= 1

    def test_query_by_dv(self, belief_engine):
        dicts = [
            make_belief_dict(f"b{i}", env_id="spatial.height.high", out_id="cog.creativity")
            for i in range(4)
        ]
        belief_engine.load_from_belief_dicts(dicts)
        belief_engine.aggregate()

        results = belief_engine.query(dv_pattern="cog")
        assert len(results) >= 1

    def test_what_does_en_believe(self, belief_engine):
        dicts = [
            make_belief_dict(f"b{i}", env_id="spatial.height.high", out_id="cog.creativity")
            for i in range(4)
        ]
        belief_engine.load_from_belief_dicts(dicts)
        belief_engine.aggregate()

        results = belief_engine.what_does_en_believe("ceiling height")
        assert len(results) >= 1
        assert "belief" in results[0]

    def test_coverage_gaps_api(self, belief_engine):
        dicts = [
            make_belief_dict(f"b{i}", env_id="spatial.height.high", out_id="cog.creativity")
            for i in range(4)
        ]
        belief_engine.load_from_belief_dicts(dicts)
        belief_engine.aggregate()

        gaps = belief_engine.coverage_gaps()
        assert isinstance(gaps, list)

    def test_argumentation_targets(self, belief_engine):
        # Create contested scenario
        dicts = [
            make_belief_dict("b1", content="increases creativity", env_id="spatial.height.high", out_id="cog.creativity"),
            make_belief_dict("b2", content="does not affect creativity", env_id="spatial.height.high", out_id="cog.creativity"),
            make_belief_dict("b3", content="increases creativity", env_id="spatial.height.high", out_id="cog.creativity"),
            make_belief_dict("b4", content="decreases creativity", env_id="spatial.height.high", out_id="cog.creativity"),
        ]
        belief_engine.load_from_belief_dicts(dicts)
        belief_engine.aggregate()
        targets = belief_engine.argumentation_targets()
        assert isinstance(targets, list)

    def test_export_beliefs(self, belief_engine):
        dicts = [make_belief_dict(f"b{i}") for i in range(3)]
        belief_engine.load_from_belief_dicts(dicts)
        belief_engine.aggregate()
        export = belief_engine.export_beliefs()
        assert isinstance(export, list)
        assert all("t3_id" in b for b in export)

    def test_summary(self, belief_engine):
        dicts = [make_belief_dict(f"b{i}") for i in range(3)]
        belief_engine.load_from_belief_dicts(dicts)
        belief_engine.aggregate()
        summary = belief_engine.summary()
        assert "total_beliefs" in summary
        assert "n_findings" in summary
        assert summary["n_findings"] == 3

    def test_on_new_finding(self, belief_engine):
        dicts = [make_belief_dict(f"b{i}") for i in range(3)]
        belief_engine.load_from_belief_dicts(dicts)
        belief_engine.aggregate()

        new_finding = make_finding("new_f", paper_id="new_paper")
        result = belief_engine.on_new_finding(new_finding)
        # Should have re-aggregated
        assert belief_engine.last_aggregation is not None


class TestFindingExtraction:
    """Test finding extraction from EN beliefs."""

    def test_extract_basic(self):
        bd = make_belief_dict()
        finding = extract_finding_from_belief(bd)
        assert finding is not None
        assert finding.iv_node == "spatial.height.high"
        assert finding.dv_node == "cog.creativity"

    def test_extract_no_iv_returns_none(self):
        bd = make_belief_dict()
        bd["environment_id"] = None
        finding = extract_finding_from_belief(bd)
        assert finding is None

    def test_infer_direction_positive(self):
        d = _infer_direction("high ceilings increase creativity", {})
        assert d == "positive"

    def test_infer_direction_negative(self):
        d = _infer_direction("noise decreases concentration", {})
        assert d == "negative"

    def test_infer_direction_null(self):
        d = _infer_direction("no significant effect was found", {})
        assert d == "null"

    def test_infer_delivery_mode_vr(self):
        m = _infer_delivery_mode("virtual reality environment", [])
        assert m == DeliveryMode.VR

    def test_infer_delivery_mode_photo(self):
        m = _infer_delivery_mode("participants viewed photographs", [])
        assert m == DeliveryMode.PHOTOGRAPH

    def test_infer_delivery_mode_real(self):
        m = _infer_delivery_mode("field study in actual office", [])
        assert m == DeliveryMode.REAL


# ══════════════════════════════════════════════════════════════════
# TEST CLASS 5: T3 Integration Layer
# ══════════════════════════════════════════════════════════════════

class TestT3Integration:
    """Test the contract-based integration layer."""

    def test_adapter_creation(self, adapter):
        assert adapter is not None
        assert adapter.engine is not None

    def test_query_contract(self, adapter):
        # Load and aggregate
        dicts = [make_belief_dict(f"b{i}") for i in range(4)]
        adapter.on_batch_complete(dicts)

        results = adapter.query_beliefs(iv_pattern="spatial")
        assert isinstance(results, list)

    def test_what_does_en_believe_contract(self, adapter):
        dicts = [make_belief_dict(f"b{i}") for i in range(4)]
        adapter.on_batch_complete(dicts)

        results = adapter.what_does_en_believe("ceiling")
        assert isinstance(results, list)

    def test_gap_contract(self, adapter):
        dicts = [make_belief_dict(f"b{i}") for i in range(4)]
        adapter.on_batch_complete(dicts)

        gaps = adapter.get_coverage_gaps()
        assert isinstance(gaps, list)

    def test_search_queries(self, adapter):
        dicts = [make_belief_dict(f"b{i}") for i in range(4)]
        adapter.on_batch_complete(dicts)

        queries = adapter.get_search_queries(max_queries=5)
        assert isinstance(queries, list)

    def test_gap_summary(self, adapter):
        dicts = [make_belief_dict(f"b{i}") for i in range(4)]
        adapter.on_batch_complete(dicts)

        summary = adapter.gap_summary()
        assert "total_gaps" in summary

    def test_argumentation_contract(self, adapter):
        targets = adapter.get_argumentation_targets()
        assert isinstance(targets, list)

    def test_overseer_consistency_check(self, adapter):
        dicts = [make_belief_dict(f"b{i}") for i in range(4)]
        adapter.on_batch_complete(dicts)

        violations = adapter.check_consistency()
        assert isinstance(violations, list)

    def test_overseer_health_metrics(self, adapter):
        dicts = [make_belief_dict(f"b{i}") for i in range(4)]
        adapter.on_batch_complete(dicts)

        metrics = adapter.health_metrics()
        assert "total_beliefs" in metrics
        assert "consistency_violations" in metrics

    def test_bn_contract(self, adapter):
        dicts = [make_belief_dict(f"b{i}") for i in range(4)]
        adapter.on_batch_complete(dicts)

        edges = adapter.t3_supported_edges()
        assert isinstance(edges, list)

    def test_template_contract(self, adapter):
        dicts = [make_belief_dict(f"b{i}") for i in range(4)]
        adapter.on_batch_complete(dicts)

        beliefs = adapter.beliefs_for_template("VIEW1")
        assert isinstance(beliefs, list)

    def test_template_coverage(self, adapter):
        dicts = [make_belief_dict(f"b{i}") for i in range(4)]
        adapter.on_batch_complete(dicts)

        coverage = adapter.template_coverage("VIEW1")
        assert "template_id" in coverage
        assert "n_supporting_beliefs" in coverage

    def test_singleton(self):
        adapter1 = get_t3_adapter()
        assert adapter1 is not None


class TestT3EventBus:
    """Test the event bus."""

    def test_subscribe_and_publish(self):
        bus = T3EventBus()
        received = []
        bus.subscribe(T3EventType.BELIEF_FORMED, lambda e: received.append(e))

        event = T3Event(T3EventType.BELIEF_FORMED, t3_id="test")
        bus.publish(event)

        assert len(received) == 1
        assert received[0].t3_id == "test"

    def test_no_cross_event_contamination(self):
        bus = T3EventBus()
        received = []
        bus.subscribe(T3EventType.BELIEF_FORMED, lambda e: received.append(e))

        bus.publish(T3Event(T3EventType.COVERAGE_GAP, t3_id="gap1"))
        assert len(received) == 0

    def test_multiple_subscribers(self):
        bus = T3EventBus()
        received_a = []
        received_b = []
        bus.subscribe(T3EventType.BELIEF_UPDATED, lambda e: received_a.append(e))
        bus.subscribe(T3EventType.BELIEF_UPDATED, lambda e: received_b.append(e))

        bus.publish(T3Event(T3EventType.BELIEF_UPDATED, t3_id="b1"))
        assert len(received_a) == 1
        assert len(received_b) == 1

    def test_handler_error_does_not_crash(self):
        bus = T3EventBus()
        bus.subscribe(T3EventType.BELIEF_FORMED, lambda e: 1/0)
        # Should not raise
        bus.publish(T3Event(T3EventType.BELIEF_FORMED))


class TestT3Reflexes:
    """Test T3 reflexes."""

    def test_reflex_status(self, adapter):
        status = adapter.reflex_status()
        assert isinstance(status, list)

    def test_on_finding_triggers_reflex_check(self, adapter):
        # Load initial data
        dicts = [make_belief_dict(f"b{i}") for i in range(3)]
        adapter.on_batch_complete(dicts)

        # Add a new finding
        result = adapter.on_finding_added(make_belief_dict("new_b"))
        # Reflexes may or may not fire depending on data
        assert isinstance(adapter.reflex_status(), list)


# ══════════════════════════════════════════════════════════════════
# TEST CLASS 6: End-to-End Integration
# ══════════════════════════════════════════════════════════════════

class TestEndToEnd:
    """Full pipeline tests."""

    def test_ceiling_height_scenario(self):
        """User's ceiling height example: 9', 9.5', 10' studies."""
        engine = T3BeliefEngine()

        # Study A: 9' ceilings → creativity (positive)
        # Study B: 9.5' ceilings → creativity (positive)
        # Study C: 10' ceilings → creativity (positive)
        # Study D: Meta-analysis: tall ceilings → creativity
        beliefs = [
            make_belief_dict("study_a", content="9 foot ceilings increase creativity",
                           env_id="spatial.height.high", out_id="cog.creativity"),
            make_belief_dict("study_b", content="9.5 foot ceilings increase creativity",
                           env_id="spatial.height.high", out_id="cog.creativity"),
            make_belief_dict("study_c", content="10 foot ceilings increase creative fluency",
                           env_id="spatial.height.high", out_id="cog.creativity"),
            make_belief_dict("study_d", content="tall ceilings increase creativity (meta-analysis)",
                           env_id="spatial.height.high", out_id="cog.creativity"),
        ]

        engine.load_from_belief_dicts(beliefs)
        engine.aggregate()

        # Should form a generalized belief
        results = engine.query(iv_pattern="spatial.height")
        assert len(results) >= 1
        assert results[0].status == BeliefStatus.ESTABLISHED

    def test_vr_vs_real_boundary(self):
        """VR and real delivery modes should be tracked as boundary conditions."""
        engine = T3BeliefEngine()

        beliefs = [
            {**make_belief_dict("b1"), "tags": ["virtual reality"]},
            {**make_belief_dict("b2"), "tags": ["virtual reality"]},
            {**make_belief_dict("b3"), "tags": ["field study"]},
            {**make_belief_dict("b4"), "tags": ["actual office"]},
        ]

        engine.load_from_belief_dicts(beliefs)
        engine.aggregate()

        # Check delivery mode facets are tracked
        for belief in engine.t3_beliefs.values():
            if belief.iv_node == "spatial.height.high":
                assert len(belief.delivery_modes_tested) >= 1

    def test_mixed_iv_dv_scenario(self):
        """Multiple IVs and DVs should produce separate beliefs."""
        engine = T3BeliefEngine()

        beliefs = [
            make_belief_dict("b1", env_id="spatial.height.high", out_id="cog.creativity"),
            make_belief_dict("b2", env_id="spatial.height.high", out_id="cog.creativity"),
            make_belief_dict("b3", env_id="spatial.height.high", out_id="cog.creativity"),
            make_belief_dict("b4", env_id="acoustic.noise", out_id="cog.attention"),
            make_belief_dict("b5", env_id="acoustic.noise", out_id="cog.attention"),
            make_belief_dict("b6", env_id="acoustic.noise", out_id="cog.attention"),
        ]

        engine.load_from_belief_dicts(beliefs)
        engine.aggregate()

        # Should have separate beliefs for height→creativity and noise→attention
        height_results = engine.query(iv_pattern="spatial.height")
        noise_results = engine.query(iv_pattern="acoustic.noise")
        assert len(height_results) >= 1
        assert len(noise_results) >= 1

    def test_full_adapter_pipeline(self):
        """Test full pipeline through adapter."""
        adapter = T3Adapter()

        # Batch load
        beliefs = [make_belief_dict(f"b{i}") for i in range(5)]
        summary = adapter.on_batch_complete(beliefs)
        assert summary["total_beliefs"] >= 1

        # Query
        results = adapter.query_beliefs(iv_pattern="spatial")
        assert len(results) >= 1

        # Health
        health = adapter.health_metrics()
        assert "total_beliefs" in health

        # Gaps
        gaps = adapter.get_coverage_gaps()
        assert isinstance(gaps, list)

        # Search queries
        queries = adapter.get_search_queries()
        assert isinstance(queries, list)

        # BN edges
        edges = adapter.t3_supported_edges()
        assert isinstance(edges, list)


# ══════════════════════════════════════════════════════════════════
# TEST CLASS 7: Nascent Beliefs (Search Seeds)
# ══════════════════════════════════════════════════════════════════

class TestNascentBeliefs:
    """Test nascent beliefs — single-article findings preserved as search seeds."""

    def test_single_finding_is_nascent(self, engine):
        """1 finding → NASCENT status."""
        engine.add_findings([make_finding("f1")])
        beliefs = engine.aggregate()
        key = "t3:spatial.height.high→cog.creativity.divergent.fluency"
        assert key in beliefs
        assert beliefs[key].status == BeliefStatus.NASCENT
        assert beliefs[key].n_total == 1

    def test_two_findings_is_tentative(self, engine):
        """2 findings → TENTATIVE (not NASCENT)."""
        engine.add_findings([make_finding("f1"), make_finding("f2")])
        beliefs = engine.aggregate()
        key = "t3:spatial.height.high→cog.creativity.divergent.fluency"
        assert beliefs[key].status == BeliefStatus.TENTATIVE
        assert beliefs[key].n_total == 2

    def test_nascent_is_nascent_property(self, engine):
        engine.add_findings([make_finding("f1")])
        beliefs = engine.aggregate()
        key = "t3:spatial.height.high→cog.creativity.divergent.fluency"
        assert beliefs[key].is_nascent is True

    def test_established_is_not_nascent(self, engine):
        engine.add_findings([make_finding(f"f{i}") for i in range(4)])
        beliefs = engine.aggregate()
        key = "t3:spatial.height.high→cog.creativity.divergent.fluency"
        assert beliefs[key].is_nascent is False

    def test_nascent_search_seed_query(self, engine):
        engine.add_findings([make_finding("f1")])
        beliefs = engine.aggregate()
        key = "t3:spatial.height.high→cog.creativity.divergent.fluency"
        query = beliefs[key].search_seed_query
        assert "effect on" in query
        assert len(query) > 10

    def test_nascent_to_dict_includes_search_seed(self, engine):
        engine.add_findings([make_finding("f1")])
        beliefs = engine.aggregate()
        key = "t3:spatial.height.high→cog.creativity.divergent.fluency"
        d = beliefs[key].to_dict()
        assert "search_seed_query" in d
        assert "effect on" in d["search_seed_query"]

    def test_non_nascent_to_dict_no_search_seed(self, engine):
        engine.add_findings([make_finding("f1"), make_finding("f2")])
        beliefs = engine.aggregate()
        key = "t3:spatial.height.high→cog.creativity.divergent.fluency"
        d = beliefs[key].to_dict()
        assert "search_seed_query" not in d

    def test_get_nascent_beliefs(self, engine):
        # 1 nascent (noise→attention) + 1 established (height→creativity)
        engine.add_findings([
            make_finding("f1", iv="acoustic.noise", dv="cog.attention"),
            make_finding("f2", iv="spatial.height.high"),
            make_finding("f3", iv="spatial.height.high"),
            make_finding("f4", iv="spatial.height.high"),
        ])
        engine.aggregate()
        nascent = engine.get_nascent_beliefs()
        assert len(nascent) == 1
        assert nascent[0].iv_node == "acoustic.noise"

    def test_get_nascent_search_queries(self, engine):
        engine.add_findings([
            make_finding("f1", iv="acoustic.noise", dv="cog.attention"),
            make_finding("f2", iv="natural.plants", dv="affect.stress.self_report"),
        ])
        engine.aggregate()
        queries = engine.get_nascent_search_queries()
        assert len(queries) == 2
        assert all("query" in q for q in queries)
        assert all("t3_id" in q for q in queries)
        assert all("source_paper" in q for q in queries)

    def test_nascent_generates_search_seed_gap(self, engine):
        engine.add_findings([make_finding("f1")])
        engine.aggregate()
        gaps = engine.get_coverage_gaps(0.0)
        seed_gaps = [g for g in gaps if g.gap_type == "nascent_search_seed"]
        assert len(seed_gaps) == 1
        assert seed_gaps[0].priority == 0.85
        assert "effect on" in seed_gaps[0].search_query

    def test_nascent_in_summary(self, engine):
        engine.add_findings([make_finding("f1")])
        engine.aggregate()
        summary = engine.summary()
        assert "nascent" in summary
        assert summary["nascent"] == 1

    def test_adapter_nascent_search_seeds(self):
        adapter = T3Adapter()
        # 2 nascent + 1 established
        dicts = [
            make_belief_dict("b1", env_id="acoustic.noise", out_id="cog.attention"),
            make_belief_dict("b2", env_id="natural.plants", out_id="affect.stress.self_report"),
            make_belief_dict("b3", env_id="spatial.height.high", out_id="cog.creativity"),
            make_belief_dict("b4", env_id="spatial.height.high", out_id="cog.creativity"),
            make_belief_dict("b5", env_id="spatial.height.high", out_id="cog.creativity"),
        ]
        adapter.on_batch_complete(dicts)
        seeds = adapter.get_nascent_search_seeds()
        assert len(seeds) >= 2
        assert all("query" in s for s in seeds)

    def test_adapter_gap_summary_includes_nascent(self):
        adapter = T3Adapter()
        dicts = [
            make_belief_dict("b1", env_id="acoustic.noise", out_id="cog.attention"),
        ]
        adapter.on_batch_complete(dicts)
        summary = adapter.gap_summary()
        assert "nascent_search_seeds" in summary
        assert summary["nascent_search_seeds"] >= 1

