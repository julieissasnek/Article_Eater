"""
Tests for Network Visualization Service — Sprint 3.0.3-E
2026-02-10

Tests cover graph construction, clustering, filtering, and HTML generation.
"""

import pytest
import json
from typing import Dict, List, Any

from src.services.network_service import (
    NetworkService,
    GraphNode,
    GraphEdge,
    GraphData,
    GraphMetrics,
    LayoutAlgorithm,
    ClusterMode,
    EdgeType,
    STATUS_COLORS,
    get_network_service,
    build_network_visualization,
)


# =============================================================================
# Test Data
# =============================================================================

def create_test_beliefs() -> List[Dict[str, Any]]:
    """Create test belief data."""
    return [
        {
            "id": "B001",
            "content": "Plants reduce stress in office environments",
            "credence": 0.75,
            "status": "ACCEPTED",
            "level": "EMPIRICAL",
            "theory": "Biophilia",
        },
        {
            "id": "B002",
            "content": "Attention Restoration Theory explains cognitive recovery",
            "credence": 0.85,
            "status": "ESTABLISHED",
            "level": "THEORETICAL",
            "theory": "ART",
        },
        {
            "id": "B003",
            "content": "Window views improve patient recovery",
            "credence": 0.65,
            "status": "CONTESTED",
            "level": "EMPIRICAL",
            "theory": "SRT",
        },
        {
            "id": "B004",
            "content": "Blue light affects circadian rhythms",
            "credence": 0.55,
            "status": "TENTATIVE",
            "level": "EMPIRICAL",
            "theory": None,
        },
        {
            "id": "B005",
            "content": "Nature exposure reduces cortisol levels",
            "credence": 0.70,
            "status": "ACCEPTED",
            "level": "EMPIRICAL",
            "theory": "SRT",
        },
    ]


def create_test_constraints() -> List[Dict[str, Any]]:
    """Create test constraint data."""
    return [
        {
            "source_id": "B001",
            "target_id": "B002",
            "polarity": "POSITIVE",
            "weight": 0.8,
        },
        {
            "source_id": "B001",
            "target_id": "B005",
            "polarity": "POSITIVE",
            "weight": 0.7,
        },
        {
            "source_id": "B002",
            "target_id": "B003",
            "polarity": "POSITIVE",
            "weight": 0.6,
        },
        {
            "source_id": "B003",
            "target_id": "B004",
            "polarity": "NEGATIVE",
            "weight": -0.4,
        },
    ]


# =============================================================================
# Graph Construction Tests
# =============================================================================

class TestGraphConstruction:
    """Tests for graph building from beliefs and constraints."""

    def test_build_graph_creates_nodes(self):
        """Test that nodes are created from beliefs."""
        service = NetworkService()
        beliefs = create_test_beliefs()
        graph = service.build_graph_from_beliefs(beliefs)

        assert len(graph.nodes) == 5
        assert all(isinstance(n, GraphNode) for n in graph.nodes)

    def test_build_graph_creates_edges(self):
        """Test that edges are created from constraints."""
        service = NetworkService()
        beliefs = create_test_beliefs()
        constraints = create_test_constraints()
        graph = service.build_graph_from_beliefs(beliefs, constraints)

        assert len(graph.edges) == 4
        assert all(isinstance(e, GraphEdge) for e in graph.edges)

    def test_node_color_based_on_status(self):
        """Test that node colors match status."""
        service = NetworkService()
        beliefs = create_test_beliefs()
        graph = service.build_graph_from_beliefs(beliefs)

        # Find the ACCEPTED belief
        accepted_node = next(n for n in graph.nodes if n.id == "B001")
        assert accepted_node.color == STATUS_COLORS["ACCEPTED"]

        # Find the CONTESTED belief
        contested_node = next(n for n in graph.nodes if n.id == "B003")
        assert contested_node.color == STATUS_COLORS["CONTESTED"]

    def test_node_size_based_on_credence(self):
        """Test that node size scales with credence."""
        service = NetworkService()
        beliefs = create_test_beliefs()
        graph = service.build_graph_from_beliefs(beliefs)

        # Higher credence = larger size
        high_cred = next(n for n in graph.nodes if n.id == "B002")  # 0.85
        low_cred = next(n for n in graph.nodes if n.id == "B004")   # 0.55

        assert high_cred.size > low_cred.size

    def test_edge_type_from_polarity(self):
        """Test that edge types are determined by polarity."""
        service = NetworkService()
        beliefs = create_test_beliefs()
        constraints = create_test_constraints()
        graph = service.build_graph_from_beliefs(beliefs, constraints)

        # Find positive edge
        pos_edge = next(e for e in graph.edges if e.source == "B001" and e.target == "B002")
        assert pos_edge.edge_type == EdgeType.POSITIVE

        # Find negative edge
        neg_edge = next(e for e in graph.edges if e.source == "B003" and e.target == "B004")
        assert neg_edge.edge_type == EdgeType.NEGATIVE
        assert neg_edge.dashes is True  # Negative edges are dashed

    def test_respects_max_nodes(self):
        """Test that max_nodes limit is respected."""
        service = NetworkService()
        beliefs = create_test_beliefs()
        graph = service.build_graph_from_beliefs(beliefs, max_nodes=3)

        assert len(graph.nodes) == 3
        # Should keep highest credence nodes
        ids = {n.id for n in graph.nodes}
        assert "B002" in ids  # 0.85 credence

    def test_respects_min_credence(self):
        """Test that min_credence filter is applied."""
        service = NetworkService()
        beliefs = create_test_beliefs()
        graph = service.build_graph_from_beliefs(beliefs, min_credence=0.7)

        # Should only include beliefs with credence >= 0.7
        assert all(n.credence >= 0.7 for n in graph.nodes)

    def test_edges_filtered_to_valid_nodes(self):
        """Test that edges with missing nodes are excluded."""
        service = NetworkService()
        beliefs = create_test_beliefs()[:2]  # Only B001 and B002
        constraints = create_test_constraints()  # Includes edges to B003, B004, B005
        graph = service.build_graph_from_beliefs(beliefs, constraints)

        # Only edge between B001-B002 should exist
        assert len(graph.edges) == 1
        assert graph.edges[0].source == "B001"
        assert graph.edges[0].target == "B002"


# =============================================================================
# Graph Metrics Tests
# =============================================================================

class TestGraphMetrics:
    """Tests for graph metric computation."""

    def test_metrics_computed(self):
        """Test that metrics are computed."""
        service = NetworkService()
        beliefs = create_test_beliefs()
        constraints = create_test_constraints()
        graph = service.build_graph_from_beliefs(beliefs, constraints)

        assert graph.metrics.node_count == 5
        assert graph.metrics.edge_count == 4

    def test_density_calculation(self):
        """Test density is computed correctly."""
        service = NetworkService()
        beliefs = create_test_beliefs()
        constraints = create_test_constraints()
        graph = service.build_graph_from_beliefs(beliefs, constraints)

        # Density = 2*E / (N*(N-1))
        expected_density = (2 * 4) / (5 * 4)
        assert abs(graph.metrics.density - expected_density) < 0.01

    def test_status_breakdown(self):
        """Test status counts are computed."""
        service = NetworkService()
        beliefs = create_test_beliefs()
        graph = service.build_graph_from_beliefs(beliefs)

        # ACCEPTED + ESTABLISHED = 3, CONTESTED = 1, STUB/TENTATIVE = 1
        assert graph.metrics.accepted_count == 3
        assert graph.metrics.contested_count == 1
        assert graph.metrics.stub_count == 1

    def test_node_degree_computed(self):
        """Test that node degrees are computed."""
        service = NetworkService()
        beliefs = create_test_beliefs()
        constraints = create_test_constraints()
        graph = service.build_graph_from_beliefs(beliefs, constraints)

        # B001 has edges to B002 and B005
        b001 = next(n for n in graph.nodes if n.id == "B001")
        assert b001.degree == 2


# =============================================================================
# Clustering Tests
# =============================================================================

class TestClustering:
    """Tests for graph clustering."""

    def test_cluster_by_theory(self):
        """Test clustering by theory."""
        service = NetworkService()
        beliefs = create_test_beliefs()
        graph = service.build_graph_from_beliefs(beliefs)

        clusters = service.apply_clustering(ClusterMode.THEORY, graph)

        assert "Biophilia" in clusters
        assert "ART" in clusters
        assert "SRT" in clusters
        assert "Unassigned" in clusters  # B004 has no theory

        assert "B001" in clusters["Biophilia"]
        assert "B002" in clusters["ART"]

    def test_cluster_by_level(self):
        """Test clustering by epistemic level."""
        service = NetworkService()
        beliefs = create_test_beliefs()
        graph = service.build_graph_from_beliefs(beliefs)

        clusters = service.apply_clustering(ClusterMode.LEVEL, graph)

        assert "THEORETICAL" in clusters
        assert "EMPIRICAL" in clusters

        assert "B002" in clusters["THEORETICAL"]
        assert "B001" in clusters["EMPIRICAL"]

    def test_cluster_by_status(self):
        """Test clustering by status."""
        service = NetworkService()
        beliefs = create_test_beliefs()
        graph = service.build_graph_from_beliefs(beliefs)

        clusters = service.apply_clustering(ClusterMode.STATUS, graph)

        assert "ACCEPTED" in clusters
        assert "CONTESTED" in clusters

    def test_clustering_assigns_groups(self):
        """Test that clustering assigns group property to nodes."""
        service = NetworkService()
        beliefs = create_test_beliefs()
        graph = service.build_graph_from_beliefs(beliefs)

        service.apply_clustering(ClusterMode.THEORY, graph)

        b001 = next(n for n in graph.nodes if n.id == "B001")
        assert b001.group == "Biophilia"


# =============================================================================
# Filtering Tests
# =============================================================================

class TestFiltering:
    """Tests for node/edge filtering."""

    def test_filter_by_status(self):
        """Test filtering nodes by status."""
        service = NetworkService()
        beliefs = create_test_beliefs()
        graph = service.build_graph_from_beliefs(beliefs)

        visible = service.filter_nodes(status=["ACCEPTED", "ESTABLISHED"], graph_data=graph)

        # Should show B001, B002, B005
        assert visible == 3
        hidden_count = sum(1 for n in graph.nodes if n.hidden)
        assert hidden_count == 2

    def test_filter_by_level(self):
        """Test filtering nodes by level."""
        service = NetworkService()
        beliefs = create_test_beliefs()
        graph = service.build_graph_from_beliefs(beliefs)

        visible = service.filter_nodes(level=["THEORETICAL"], graph_data=graph)

        assert visible == 1

    def test_filter_by_credence(self):
        """Test filtering nodes by minimum credence."""
        service = NetworkService()
        beliefs = create_test_beliefs()
        graph = service.build_graph_from_beliefs(beliefs)

        visible = service.filter_nodes(min_credence=0.7, graph_data=graph)

        assert visible == 3  # B001 (0.75), B002 (0.85), B005 (0.70)

    def test_filter_by_search(self):
        """Test filtering nodes by search term."""
        service = NetworkService()
        beliefs = create_test_beliefs()
        graph = service.build_graph_from_beliefs(beliefs)

        visible = service.filter_nodes(search="stress", graph_data=graph)

        assert visible == 1  # B001 contains "stress"

    def test_filter_hides_orphan_edges(self):
        """Test that filtering hides edges with hidden endpoints."""
        service = NetworkService()
        beliefs = create_test_beliefs()
        constraints = create_test_constraints()
        graph = service.build_graph_from_beliefs(beliefs, constraints)

        service.filter_nodes(status=["ACCEPTED"], graph_data=graph)

        # Edges involving hidden nodes should be hidden
        visible_edges = [e for e in graph.edges if not e.hidden]
        for edge in visible_edges:
            source_visible = not next(n for n in graph.nodes if n.id == edge.source).hidden
            target_visible = not next(n for n in graph.nodes if n.id == edge.target).hidden
            assert source_visible and target_visible


# =============================================================================
# Neighborhood Tests
# =============================================================================

class TestNeighborhood:
    """Tests for neighborhood exploration."""

    def test_get_neighborhood_depth_1(self):
        """Test getting immediate neighbors."""
        service = NetworkService()
        beliefs = create_test_beliefs()
        constraints = create_test_constraints()
        graph = service.build_graph_from_beliefs(beliefs, constraints)

        neighbors = service.get_neighborhood("B001", depth=1, graph_data=graph)

        # B001 connects to B002 and B005
        assert "B001" in neighbors
        assert "B002" in neighbors
        assert "B005" in neighbors
        assert len(neighbors) == 3

    def test_get_neighborhood_depth_2(self):
        """Test getting 2-hop neighbors."""
        service = NetworkService()
        beliefs = create_test_beliefs()
        constraints = create_test_constraints()
        graph = service.build_graph_from_beliefs(beliefs, constraints)

        neighbors = service.get_neighborhood("B001", depth=2, graph_data=graph)

        # B001 -> B002 -> B003
        assert "B003" in neighbors

    def test_focus_on_node(self):
        """Test focusing view on a node."""
        service = NetworkService()
        beliefs = create_test_beliefs()
        constraints = create_test_constraints()
        graph = service.build_graph_from_beliefs(beliefs, constraints)

        service.focus_on_node("B001", depth=1, graph_data=graph)

        # B001, B002, B005 should be visible
        visible_ids = {n.id for n in graph.nodes if not n.hidden}
        assert "B001" in visible_ids
        assert "B002" in visible_ids
        assert "B005" in visible_ids

        # B003, B004 should be hidden
        assert "B003" not in visible_ids
        assert "B004" not in visible_ids


# =============================================================================
# Layout Tests
# =============================================================================

class TestLayoutOptions:
    """Tests for layout configuration."""

    def test_force_directed_options(self):
        """Test force-directed layout options."""
        service = NetworkService()
        options = service.get_layout_options(LayoutAlgorithm.FORCE_DIRECTED)

        assert options["solver"] == "forceAtlas2Based"
        assert "forceAtlas2Based" in options

    def test_hierarchical_options(self):
        """Test hierarchical layout options."""
        service = NetworkService()
        options = service.get_layout_options(hierarchical=True, direction="LR")

        assert options["direction"] == "LR"
        assert "levelSeparation" in options

    def test_barnes_hut_options(self):
        """Test Barnes-Hut layout options."""
        service = NetworkService()
        options = service.get_layout_options(LayoutAlgorithm.BARNESHET)

        assert options["solver"] == "barnesHut"


# =============================================================================
# HTML Generation Tests
# =============================================================================

class TestHTMLGeneration:
    """Tests for vis.js HTML generation."""

    def test_generate_html_returns_string(self):
        """Test that HTML generation returns string."""
        service = NetworkService()
        beliefs = create_test_beliefs()
        graph = service.build_graph_from_beliefs(beliefs)

        html = service.generate_vis_html(graph)

        assert isinstance(html, str)
        assert len(html) > 100

    def test_html_contains_vis_script(self):
        """Test that HTML includes vis.js script."""
        service = NetworkService()
        beliefs = create_test_beliefs()
        graph = service.build_graph_from_beliefs(beliefs)

        html = service.generate_vis_html(graph)

        assert "vis-network" in html
        assert "new vis.Network" in html

    def test_html_contains_nodes_data(self):
        """Test that HTML includes node data."""
        service = NetworkService()
        beliefs = create_test_beliefs()
        graph = service.build_graph_from_beliefs(beliefs)

        html = service.generate_vis_html(graph)

        assert "B001" in html
        assert "B002" in html

    def test_html_contains_legend(self):
        """Test that HTML includes legend when requested."""
        service = NetworkService()
        beliefs = create_test_beliefs()
        graph = service.build_graph_from_beliefs(beliefs)

        html_with_legend = service.generate_vis_html(graph, show_legend=True)
        html_without = service.generate_vis_html(graph, show_legend=False)

        assert "legend" in html_with_legend
        assert "legend" not in html_without or html_without.count("legend") < html_with_legend.count("legend")

    def test_html_respects_height(self):
        """Test that HTML respects height parameter."""
        service = NetworkService()
        beliefs = create_test_beliefs()
        graph = service.build_graph_from_beliefs(beliefs)

        html = service.generate_vis_html(graph, height=800)

        assert "800px" in html


# =============================================================================
# Serialization Tests
# =============================================================================

class TestSerialization:
    """Tests for graph data serialization."""

    def test_graph_to_vis_dict(self):
        """Test converting graph to vis.js dict format."""
        service = NetworkService()
        beliefs = create_test_beliefs()
        constraints = create_test_constraints()
        graph = service.build_graph_from_beliefs(beliefs, constraints)

        vis_dict = graph.to_vis_dict()

        assert "nodes" in vis_dict
        assert "edges" in vis_dict
        assert len(vis_dict["nodes"]) == 5
        assert len(vis_dict["edges"]) == 4

    def test_graph_to_json(self):
        """Test serializing graph to JSON."""
        service = NetworkService()
        beliefs = create_test_beliefs()
        graph = service.build_graph_from_beliefs(beliefs)

        json_str = graph.to_json()

        # Should be valid JSON
        parsed = json.loads(json_str)
        assert "nodes" in parsed
        assert "edges" in parsed

    def test_hidden_nodes_excluded_from_serialization(self):
        """Test that hidden nodes are excluded from serialization."""
        service = NetworkService()
        beliefs = create_test_beliefs()
        graph = service.build_graph_from_beliefs(beliefs)

        # Hide some nodes
        service.filter_nodes(status=["ACCEPTED"], graph_data=graph)

        vis_dict = graph.to_vis_dict()

        # Should only include visible nodes
        assert len(vis_dict["nodes"]) == 2  # B001 and B005 are ACCEPTED


# =============================================================================
# Convenience Function Tests
# =============================================================================

class TestConvenienceFunctions:
    """Tests for module-level convenience functions."""

    def test_get_network_service_singleton(self):
        """Test singleton pattern."""
        s1 = get_network_service()
        s2 = get_network_service()
        assert s1 is s2

    def test_build_network_visualization(self):
        """Test convenience function for building visualization."""
        beliefs = create_test_beliefs()
        constraints = create_test_constraints()

        html = build_network_visualization(
            beliefs=beliefs,
            constraints=constraints,
            layout=LayoutAlgorithm.FORCE_DIRECTED,
            height=500
        )

        assert isinstance(html, str)
        assert "vis-network" in html
        assert "500px" in html

    def test_build_with_clustering(self):
        """Test building visualization with clustering."""
        beliefs = create_test_beliefs()

        html = build_network_visualization(
            beliefs=beliefs,
            cluster_by=ClusterMode.THEORY
        )

        assert isinstance(html, str)


# =============================================================================
# Edge Cases
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_beliefs(self):
        """Test handling of empty beliefs list."""
        service = NetworkService()
        graph = service.build_graph_from_beliefs([])

        assert len(graph.nodes) == 0
        assert len(graph.edges) == 0
        assert graph.metrics.node_count == 0

    def test_no_constraints(self):
        """Test handling of no constraints."""
        service = NetworkService()
        beliefs = create_test_beliefs()
        graph = service.build_graph_from_beliefs(beliefs, constraints=None)

        assert len(graph.nodes) == 5
        assert len(graph.edges) == 0

    def test_belief_with_dict_credence(self):
        """Test handling of credence as dict (with 'point' key)."""
        service = NetworkService()
        beliefs = [{
            "id": "B001",
            "content": "Test belief",
            "credence": {"point": 0.75, "uncertainty": 0.1},
            "status": "ACCEPTED",
            "level": "EMPIRICAL",
        }]

        graph = service.build_graph_from_beliefs(beliefs)

        assert graph.nodes[0].credence == 0.75

    def test_belief_with_enum_status(self):
        """Test handling of status as enum-like object."""
        from enum import Enum

        class MockStatus(Enum):
            ACCEPTED = "accepted"

        service = NetworkService()
        beliefs = [{
            "id": "B001",
            "content": "Test",
            "credence": 0.5,
            "status": MockStatus.ACCEPTED,
            "level": "EMPIRICAL",
        }]

        graph = service.build_graph_from_beliefs(beliefs)

        assert graph.nodes[0].status == "ACCEPTED"

    def test_generate_html_with_no_data(self):
        """Test HTML generation with no graph data."""
        service = NetworkService()
        html = service.generate_vis_html(None)

        assert "No graph data" in html

    def test_filter_with_no_graph(self):
        """Test filtering with no graph loaded."""
        service = NetworkService()
        result = service.filter_nodes(status=["ACCEPTED"])

        assert result == 0
