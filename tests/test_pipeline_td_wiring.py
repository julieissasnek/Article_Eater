"""
Tests for Sprint 2.0.1: TD-C and TD-E wiring into pipeline.py

Tests verify that:
1. Scalable coherence (TD-C) is available and can be used
2. Incremental BN (TD-E) is available and can be used
3. The pipeline integration initializes without errors
"""

import pytest


class TestTDModuleAvailability:
    """Test that TD modules are available in pipeline."""

    def test_scalable_coherence_available(self):
        """TD-C module should be importable from pipeline."""
        from app.tasks.pipeline import SCALABLE_COHERENCE_AVAILABLE
        assert SCALABLE_COHERENCE_AVAILABLE is True

    def test_incremental_bn_available(self):
        """TD-E module should be importable from pipeline."""
        from app.tasks.pipeline import INCREMENTAL_BN_AVAILABLE
        assert INCREMENTAL_BN_AVAILABLE is True

    def test_scalable_coherence_imports(self):
        """TD-C classes should be importable."""
        from app.tasks.pipeline import (
            CoherenceManager,
            ClusterManager,
            ConstraintNetwork,
            ClusterType,
        )
        assert CoherenceManager is not None
        assert ClusterManager is not None
        assert ConstraintNetwork is not None
        assert ClusterType is not None

    def test_incremental_bn_imports(self):
        """TD-E classes should be importable."""
        from app.tasks.pipeline import (
            IncrementalBNBuilder,
            BetaBernoulliEdge,
            ActiveLearningScheduler,
            EdgeType,
        )
        assert IncrementalBNBuilder is not None
        assert BetaBernoulliEdge is not None
        assert ActiveLearningScheduler is not None
        assert EdgeType is not None


class TestCoherenceManagerInPipeline:
    """Test CoherenceManager integration in pipeline."""

    def test_coherence_manager_creation(self):
        """Should be able to create a CoherenceManager."""
        from app.tasks.pipeline import CoherenceManager
        manager = CoherenceManager()
        assert manager is not None

    def test_coherence_manager_add_belief(self):
        """Should be able to add beliefs to CoherenceManager."""
        from app.tasks.pipeline import CoherenceManager
        manager = CoherenceManager()

        manager.on_belief_added(
            belief_id="b1",
            theory_id="ART",
            level="empirical",
            domain="cog"
        )

        # Verify belief was added (stats are nested)
        stats = manager.stats()
        assert stats["network"]["n_nodes"] == 1

    def test_coherence_manager_add_constraint(self):
        """Should be able to add constraints to CoherenceManager."""
        from app.tasks.pipeline import CoherenceManager
        manager = CoherenceManager()

        # Add two beliefs first
        manager.on_belief_added("b1", "ART", "empirical", "cog")
        manager.on_belief_added("b2", "ART", "empirical", "cog")

        # Add constraint
        manager.on_constraint_added(
            constraint_id="c1",
            source_id="b1",
            target_id="b2",
            constraint_type="supports",
            strength=0.8
        )

        stats = manager.stats()
        assert stats["network"]["n_constraints"] == 1

    def test_coherence_manager_compute_coherence(self):
        """Should be able to compute coherence."""
        from app.tasks.pipeline import CoherenceManager
        manager = CoherenceManager()

        manager.on_belief_added("b1", "ART", "empirical", "cog")
        manager.on_belief_added("b2", "ART", "empirical", "cog")
        manager.on_constraint_added("c1", "b1", "b2", "supports", 0.8)

        coherence = manager.compute_coherence()
        assert 0.0 <= coherence <= 1.0


class TestIncrementalBNInPipeline:
    """Test IncrementalBNBuilder integration in pipeline."""

    def test_bn_builder_creation(self):
        """Should be able to create an IncrementalBNBuilder."""
        from app.tasks.pipeline import IncrementalBNBuilder
        builder = IncrementalBNBuilder()
        assert builder is not None

    def test_bn_builder_observe_evidence(self):
        """Should be able to observe evidence."""
        from app.tasks.pipeline import IncrementalBNBuilder
        builder = IncrementalBNBuilder()

        edge = builder.observe_evidence(
            source="nature_exposure",
            target="stress_reduction",
            supports=True,
            weight=0.8,
            paper_id="paper:001"
        )

        assert edge is not None
        assert edge.source == "nature_exposure"
        assert edge.target == "stress_reduction"
        assert edge.mean > 0.5  # Supporting evidence increases mean

    def test_bn_builder_to_dict(self):
        """Should be able to serialize BN state."""
        from app.tasks.pipeline import IncrementalBNBuilder
        builder = IncrementalBNBuilder()

        builder.observe_evidence("A", "B", True, 0.8)
        builder.observe_evidence("B", "C", False, 0.5)

        state = builder.to_dict()
        assert "edges" in state
        assert len(state["edges"]) == 2

    def test_bn_builder_multiple_papers(self):
        """Should track multiple papers for same edge."""
        from app.tasks.pipeline import IncrementalBNBuilder
        builder = IncrementalBNBuilder()

        builder.observe_evidence("X", "Y", True, 0.8, "paper1")
        builder.observe_evidence("X", "Y", True, 0.7, "paper2")
        builder.observe_evidence("X", "Y", False, 0.5, "paper3")

        edge = builder.get_or_create_edge("X", "Y")
        assert edge.n_papers == 3
        assert "paper1" in edge.paper_ids
        assert "paper2" in edge.paper_ids
        assert "paper3" in edge.paper_ids


class TestIntegrationWorkflow:
    """Test the pipeline integration workflow."""

    def test_mock_integration_workflow(self):
        """Test the workflow that pipeline uses for integration."""
        from app.tasks.pipeline import (
            CoherenceManager,
            IncrementalBNBuilder,
        )

        # Simulate what pipeline does
        coherence_manager = CoherenceManager()
        bn_builder = IncrementalBNBuilder()

        # Simulate adding beliefs from web
        beliefs = [
            {"belief_id": "b1", "theory_id": "ART", "level": "empirical", "domain": "cog"},
            {"belief_id": "b2", "theory_id": "SRT", "level": "empirical", "domain": "affect"},
        ]

        for b in beliefs:
            coherence_manager.on_belief_added(
                belief_id=b["belief_id"],
                theory_id=b["theory_id"],
                level=b["level"],
                domain=b["domain"]
            )

        # Simulate adding rules to BN
        rules = [
            {"lhs": [{"var": "nature"}], "rhs": [{"var": "stress"}], "polarity": "positive", "ae_confidence": 0.8},
            {"lhs": [{"var": "plants"}], "rhs": [{"var": "attention"}], "polarity": "positive", "ae_confidence": 0.7},
        ]

        bn_updates = 0
        for rule in rules:
            lhs = rule.get("lhs", [])
            rhs = rule.get("rhs", [])
            polarity = rule.get("polarity", "unknown")
            ae_confidence = rule.get("ae_confidence", 0.5)

            for lhs_item in lhs:
                for rhs_item in rhs:
                    source = lhs_item.get("var", "")
                    target = rhs_item.get("var", "")

                    if source and target:
                        supports = polarity not in ("negative", "null")
                        bn_builder.observe_evidence(
                            source=source,
                            target=target,
                            supports=supports,
                            weight=ae_confidence,
                            paper_id="test:paper"
                        )
                        bn_updates += 1

        # Verify results
        assert coherence_manager.stats()["network"]["n_nodes"] == 2
        assert bn_updates == 2

        bn_state = bn_builder.to_dict()
        assert len(bn_state["edges"]) == 2

        coherence = coherence_manager.compute_coherence()
        assert 0.0 <= coherence <= 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
