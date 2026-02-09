"""
Tests for Extended API Endpoints.
Sprint 3.0.1-D — 2026-02-09

Tests for 20 additional API endpoints covering:
- Theory management
- Entrenchment analytics
- Graph operations
- Export bundles
- History/versioning

Created: 2026-02-09
"""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime

# Import Pydantic models
from app.routes.api_extended import (
    # Models
    TheoryResponse,
    TheoryCreate,
    EntrenchmentScore,
    EntrenchmentComparison,
    GraphNode,
    GraphEdge,
    GraphStructure,
    PathInfo,
    ExportBundleRequest,
    ExportBundleResponse,
    SnapshotResponse,
    SnapshotDiff,
    DiffEntry,
    # Routers
    theories_router,
    entrenchment_router,
    graph_router,
    bundles_router,
    history_router,
    # Helper functions
    _compute_histogram,
)


# =============================================================================
# MODEL TESTS
# =============================================================================


class TestPydanticModels:
    """Tests for Pydantic model validation."""

    def test_theory_response(self):
        """Test TheoryResponse model."""
        theory = TheoryResponse(
            id="art",
            name="Attention Restoration Theory",
            description="Nature restores attention",
            level="theory",
            belief_count=50,
            constraint_count=30,
            average_credence=0.75,
            entrenchment=0.65,
            key_beliefs=["b1", "b2", "b3"]
        )
        assert theory.id == "art"
        assert theory.belief_count == 50

    def test_theory_create(self):
        """Test TheoryCreate model validation."""
        create = TheoryCreate(
            name="New Theory",
            description="A new theory",
            level="sub-theory",
            key_beliefs=["b1"]
        )
        assert create.level == "sub-theory"

    def test_entrenchment_score(self):
        """Test EntrenchmentScore model."""
        score = EntrenchmentScore(
            belief_id="b1",
            entrenchment=0.75,
            components={
                "connectivity": 0.3,
                "level_weight": 0.8,
                "coherence_contrib": 0.6
            },
            rank=5
        )
        assert score.entrenchment == 0.75
        assert score.components["connectivity"] == 0.3

    def test_entrenchment_comparison(self):
        """Test EntrenchmentComparison model."""
        comp = EntrenchmentComparison(
            belief_a="b1",
            belief_b="b2",
            entrenchment_a=0.8,
            entrenchment_b=0.6,
            difference=0.2,
            more_entrenched="b1"
        )
        assert comp.more_entrenched == "b1"

    def test_graph_node(self):
        """Test GraphNode model."""
        node = GraphNode(
            id="b1",
            label="Test belief",
            type="belief",
            credence=0.85,
            entrenchment=0.7,
            level="EMPIRICAL"
        )
        assert node.type == "belief"
        assert node.credence == 0.85

    def test_graph_edge(self):
        """Test GraphEdge model."""
        edge = GraphEdge(
            source="b1",
            target="b2",
            polarity="POSITIVE",
            strength=0.9
        )
        assert edge.polarity == "POSITIVE"

    def test_graph_structure(self):
        """Test GraphStructure model."""
        structure = GraphStructure(
            nodes=[GraphNode(id="b1", label="Test", type="belief")],
            edges=[GraphEdge(source="b1", target="b2", polarity="POSITIVE", strength=0.8)],
            metadata={"node_count": 1, "edge_count": 1}
        )
        assert len(structure.nodes) == 1
        assert len(structure.edges) == 1

    def test_path_info(self):
        """Test PathInfo model."""
        path = PathInfo(
            source="b1",
            target="b3",
            path_exists=True,
            path=["b1", "b2", "b3"],
            length=2,
            total_strength=1.5
        )
        assert path.path_exists
        assert path.length == 2

    def test_export_bundle_request(self):
        """Test ExportBundleRequest model."""
        request = ExportBundleRequest(
            topic="Biophilic Design",
            purpose="literature_review",
            min_credence=0.5
        )
        assert request.purpose == "literature_review"
        assert request.min_credence == 0.5

    def test_export_bundle_response(self):
        """Test ExportBundleResponse model."""
        response = ExportBundleResponse(
            bundle_id="bundle_123",
            topic="Test",
            purpose="data_pipeline",
            generated_at="2026-02-09T22:00:00Z",
            file_count=3,
            files=[{"filename": "data.jsonl", "format": "jsonl"}],
            warnings=[]
        )
        assert response.file_count == 3

    def test_snapshot_response(self):
        """Test SnapshotResponse model."""
        snapshot = SnapshotResponse(
            snapshot_id="snap_123",
            created_at="2026-02-09T22:00:00Z",
            belief_count=100,
            constraint_count=50,
            description="Test snapshot",
            hash="abc123"
        )
        assert snapshot.belief_count == 100

    def test_diff_entry(self):
        """Test DiffEntry model."""
        entry = DiffEntry(
            type="added",
            entity_type="belief",
            entity_id="b1",
            details={"content": "New belief"}
        )
        assert entry.type == "added"

    def test_snapshot_diff(self):
        """Test SnapshotDiff model."""
        diff = SnapshotDiff(
            from_snapshot="snap_1",
            to_snapshot="snap_2",
            changes=[DiffEntry(type="added", entity_type="belief", entity_id="b1")],
            summary={"added": 1, "removed": 0, "modified": 0}
        )
        assert diff.summary["added"] == 1


# =============================================================================
# HELPER FUNCTION TESTS
# =============================================================================


class TestHelperFunctions:
    """Tests for helper functions."""

    def test_compute_histogram_basic(self):
        """Test basic histogram computation."""
        values = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        histogram = _compute_histogram(values, bins=5)

        assert len(histogram) == 5
        assert all("bin" in h for h in histogram)
        assert all("count" in h for h in histogram)
        assert sum(h["count"] for h in histogram) == len(values)

    def test_compute_histogram_empty(self):
        """Test histogram with empty values."""
        histogram = _compute_histogram([], bins=5)
        assert histogram == []

    def test_compute_histogram_single_value(self):
        """Test histogram with single value."""
        histogram = _compute_histogram([0.5], bins=3)
        assert len(histogram) == 3
        assert sum(h["count"] for h in histogram) == 1


# =============================================================================
# ROUTER ENDPOINT TESTS
# =============================================================================


class TestTheoryEndpoints:
    """Tests for theory endpoints."""

    @pytest.fixture
    def mock_web(self):
        """Create mock WebOfBelief."""
        from unittest.mock import MagicMock

        # Create mock beliefs
        mock_belief_1 = MagicMock()
        mock_belief_1.belief_id = "b1"
        mock_belief_1.content = "Nature restores attention"
        mock_belief_1.theory_id = "art"
        mock_belief_1.credence.value = 0.85
        mock_belief_1.level.value.upper.return_value = "EMPIRICAL"
        mock_belief_1.status.value.upper.return_value = "ACCEPTED"

        mock_belief_2 = MagicMock()
        mock_belief_2.belief_id = "b2"
        mock_belief_2.content = "Views reduce stress"
        mock_belief_2.theory_id = "srt"
        mock_belief_2.credence.value = 0.80
        mock_belief_2.level.value.upper.return_value = "EMPIRICAL"
        mock_belief_2.status.value.upper.return_value = "ACCEPTED"

        mock_belief_3 = MagicMock()
        mock_belief_3.belief_id = "b3"
        mock_belief_3.content = "Another ART belief"
        mock_belief_3.theory_id = "art"
        mock_belief_3.credence.value = 0.75
        mock_belief_3.level.value.upper.return_value = "EMPIRICAL"
        mock_belief_3.status.value.upper.return_value = "ACCEPTED"

        mock_web = MagicMock()
        mock_web.beliefs = {
            "b1": mock_belief_1,
            "b2": mock_belief_2,
            "b3": mock_belief_3
        }

        # Create mock constraints
        mock_constraint = MagicMock()
        mock_constraint.constraint_id = "c1"
        mock_constraint.source_id = "b1"
        mock_constraint.target_id = "b3"
        mock_constraint.polarity.value.upper.return_value = "POSITIVE"
        mock_constraint.strength = 0.9

        mock_web.constraints = {"c1": mock_constraint}
        mock_web.get_entrenchment.return_value = 0.65

        return mock_web

    @pytest.mark.asyncio
    async def test_list_theories_structure(self, mock_web):
        """Test that list_theories returns proper structure."""
        from app.routes.api_extended import list_theories

        with patch('app.routes.api_extended.get_web', return_value=mock_web):
            result = await list_theories(level=None, limit=20, offset=0)

        assert "theories" in result
        assert "total" in result
        assert isinstance(result["theories"], list)

    @pytest.mark.asyncio
    async def test_get_theory_beliefs(self, mock_web):
        """Test getting beliefs for a specific theory."""
        from app.routes.api_extended import get_theory_beliefs

        with patch('app.routes.api_extended.get_web', return_value=mock_web):
            result = await get_theory_beliefs(theory_id="art", limit=20, offset=0, min_credence=0.0)

        assert "theory_id" in result
        assert "beliefs" in result
        assert result["theory_id"] == "art"


class TestEntrenchmentEndpoints:
    """Tests for entrenchment endpoints."""

    @pytest.fixture
    def mock_web(self):
        """Create mock WebOfBelief."""
        mock_belief = MagicMock()
        mock_belief.belief_id = "b1"
        mock_belief.content = "Test belief"
        mock_belief.credence.value = 0.85
        mock_belief.level.value.upper.return_value = "EMPIRICAL"
        mock_belief.status.value.upper.return_value = "ACCEPTED"

        mock_web = MagicMock()
        mock_web.beliefs = {"b1": mock_belief}
        mock_web.constraints = {}
        mock_web.get_entrenchment.return_value = 0.65

        return mock_web

    @pytest.mark.asyncio
    async def test_get_entrenchment_scores(self, mock_web):
        """Test entrenchment scores endpoint."""
        from app.routes.api_extended import get_entrenchment_scores

        with patch('app.routes.api_extended.get_web', return_value=mock_web):
            result = await get_entrenchment_scores(limit=20, offset=0, min_entrenchment=0.0)

        assert "scores" in result
        assert "total" in result

    @pytest.mark.asyncio
    async def test_get_belief_entrenchment(self, mock_web):
        """Test individual belief entrenchment."""
        from app.routes.api_extended import get_belief_entrenchment

        with patch('app.routes.api_extended.get_web', return_value=mock_web):
            result = await get_belief_entrenchment("b1")

        assert result.belief_id == "b1"
        assert result.entrenchment == 0.65
        assert "connectivity" in result.components

    @pytest.mark.asyncio
    async def test_compare_entrenchment(self, mock_web):
        """Test entrenchment comparison."""
        mock_belief_2 = MagicMock()
        mock_belief_2.belief_id = "b2"
        mock_web.beliefs["b2"] = mock_belief_2
        mock_web.get_entrenchment.side_effect = lambda bid: 0.8 if bid == "b1" else 0.5

        from app.routes.api_extended import compare_entrenchment

        with patch('app.routes.api_extended.get_web', return_value=mock_web):
            result = await compare_entrenchment(belief_a="b1", belief_b="b2")

        assert result.belief_a == "b1"
        assert result.belief_b == "b2"
        assert result.more_entrenched == "b1"


class TestGraphEndpoints:
    """Tests for graph endpoints."""

    @pytest.fixture
    def mock_web(self):
        """Create mock WebOfBelief with graph structure."""
        beliefs = {}
        for i in range(5):
            mock_b = MagicMock()
            mock_b.belief_id = f"b{i}"
            mock_b.content = f"Belief {i}"
            mock_b.theory_id = "art" if i < 3 else "srt"
            mock_b.credence.value = 0.7 + i * 0.05
            mock_b.level.value.upper.return_value = "EMPIRICAL"
            beliefs[f"b{i}"] = mock_b

        constraints = {}
        for i in range(4):
            mock_c = MagicMock()
            mock_c.constraint_id = f"c{i}"
            mock_c.source_id = f"b{i}"
            mock_c.target_id = f"b{i+1}"
            mock_c.polarity.value.upper.return_value = "POSITIVE"
            mock_c.strength = 0.8
            constraints[f"c{i}"] = mock_c

        mock_web = MagicMock()
        mock_web.beliefs = beliefs
        mock_web.constraints = constraints
        mock_web.get_entrenchment.return_value = 0.6

        return mock_web

    @pytest.mark.asyncio
    async def test_get_graph_structure(self, mock_web):
        """Test graph structure endpoint."""
        from app.routes.api_extended import get_graph_structure

        with patch('app.routes.api_extended.get_web', return_value=mock_web):
            result = await get_graph_structure(include_theories=True, min_credence=0.0, max_nodes=100)

        assert len(result.nodes) > 0
        assert "metadata" in result.model_dump()

    @pytest.mark.asyncio
    async def test_get_belief_neighbors(self, mock_web):
        """Test neighbors endpoint."""
        from app.routes.api_extended import get_belief_neighbors

        with patch('app.routes.api_extended.get_web', return_value=mock_web):
            result = await get_belief_neighbors(belief_id="b1", depth=2)

        assert "center" in result
        assert "levels" in result
        assert result["center"] == "b1"

    @pytest.mark.asyncio
    async def test_find_path(self, mock_web):
        """Test path finding endpoint."""
        from app.routes.api_extended import find_path

        with patch('app.routes.api_extended.get_web', return_value=mock_web):
            result = await find_path(source="b0", target="b4")

        assert result.source == "b0"
        assert result.target == "b4"
        # Path should exist through the chain
        assert result.path_exists

    @pytest.mark.asyncio
    async def test_get_belief_clusters(self, mock_web):
        """Test clustering endpoint."""
        from app.routes.api_extended import get_belief_clusters

        with patch('app.routes.api_extended.get_web', return_value=mock_web):
            result = await get_belief_clusters(algorithm="theory")

        assert "clusters" in result
        assert "cluster_count" in result


class TestBundleEndpoints:
    """Tests for export bundle endpoints."""

    @pytest.mark.asyncio
    async def test_list_bundle_purposes(self):
        """Test listing bundle purposes."""
        from app.routes.api_extended import list_bundle_purposes

        result = await list_bundle_purposes()

        assert "purposes" in result
        assert len(result["purposes"]) > 0
        # Should have at least the basic purposes
        purpose_names = [p.get("purpose") for p in result["purposes"]]
        assert "literature_review" in purpose_names

    @pytest.mark.asyncio
    async def test_create_export_bundle(self):
        """Test bundle creation."""
        from app.routes.api_extended import create_export_bundle

        # Create minimal mock
        mock_web = MagicMock()
        mock_web.beliefs = {}
        mock_web.constraints = {}

        request = ExportBundleRequest(
            topic="Test Topic",
            purpose="practitioner_briefing",
            min_credence=0.5
        )

        with patch('app.routes.api_extended.get_web', return_value=mock_web):
            with patch('app.routes.api_extended._get_db_connection'):
                result = await create_export_bundle(request)

        assert result.topic == "Test Topic"
        assert result.purpose == "practitioner_briefing"


class TestHistoryEndpoints:
    """Tests for history/snapshot endpoints."""

    @pytest.fixture
    def mock_web(self):
        """Create mock WebOfBelief."""
        mock_belief = MagicMock()
        mock_belief.belief_id = "b1"
        mock_belief.content = "Test belief"
        mock_belief.credence.value = 0.85
        mock_belief.status.value = "accepted"
        mock_belief.level.value = "empirical"
        mock_belief.theory_id = "art"

        mock_web = MagicMock()
        mock_web.beliefs = {"b1": mock_belief}
        mock_web.constraints = {}

        return mock_web

    @pytest.mark.asyncio
    async def test_create_snapshot(self, mock_web):
        """Test snapshot creation."""
        from app.routes.api_extended import create_snapshot, _snapshots

        # Clear existing snapshots
        _snapshots.clear()

        with patch('app.routes.api_extended.get_web', return_value=mock_web):
            result = await create_snapshot(description="Test snapshot")

        assert result.description == "Test snapshot"
        assert result.belief_count == 1
        assert result.hash is not None

    @pytest.mark.asyncio
    async def test_list_snapshots(self, mock_web):
        """Test listing snapshots."""
        from app.routes.api_extended import list_snapshots, create_snapshot, _snapshots

        _snapshots.clear()

        with patch('app.routes.api_extended.get_web', return_value=mock_web):
            await create_snapshot(description="Snapshot 1")
            await create_snapshot(description="Snapshot 2")
            result = await list_snapshots()

        assert "snapshots" in result
        assert result["total"] == 2

    @pytest.mark.asyncio
    async def test_diff_snapshots(self, mock_web):
        """Test snapshot diffing."""
        from app.routes.api_extended import diff_snapshots, create_snapshot, _snapshots

        _snapshots.clear()

        # Create first snapshot
        with patch('app.routes.api_extended.get_web', return_value=mock_web):
            snap1 = await create_snapshot(description="Before")

            # Modify mock
            mock_belief_2 = MagicMock()
            mock_belief_2.belief_id = "b2"
            mock_belief_2.content = "New belief"
            mock_belief_2.credence.value = 0.70
            mock_belief_2.status.value = "accepted"
            mock_belief_2.level.value = "empirical"
            mock_belief_2.theory_id = "srt"
            mock_web.beliefs["b2"] = mock_belief_2

            snap2 = await create_snapshot(description="After")

            result = await diff_snapshots(from_snapshot=snap1.snapshot_id, to_snapshot=snap2.snapshot_id)

        assert result.from_snapshot == snap1.snapshot_id
        assert result.to_snapshot == snap2.snapshot_id
        assert "added" in result.summary


# =============================================================================
# ROUTER STRUCTURE TESTS
# =============================================================================


class TestRouterStructure:
    """Tests for router configuration."""

    def test_theories_router_prefix(self):
        """Test theories router has correct prefix."""
        assert theories_router.prefix == "/theories"

    def test_entrenchment_router_prefix(self):
        """Test entrenchment router has correct prefix."""
        assert entrenchment_router.prefix == "/entrenchment"

    def test_graph_router_prefix(self):
        """Test graph router has correct prefix."""
        assert graph_router.prefix == "/graph"

    def test_bundles_router_prefix(self):
        """Test bundles router has correct prefix."""
        assert bundles_router.prefix == "/bundles"

    def test_history_router_prefix(self):
        """Test history router has correct prefix."""
        assert history_router.prefix == "/history"

    def test_get_extended_router(self):
        """Test extended router aggregation."""
        from app.routes.api_extended import get_extended_router

        router = get_extended_router()
        assert router.prefix == "/api/v1"

        # Check sub-routers are included
        route_paths = [route.path for route in router.routes]
        assert any("/theories" in path for path in route_paths)
        assert any("/entrenchment" in path for path in route_paths)
        assert any("/graph" in path for path in route_paths)
        assert any("/bundles" in path for path in route_paths)
        assert any("/history" in path for path in route_paths)


# =============================================================================
# INTEGRATION TESTS
# =============================================================================


class TestEndpointCount:
    """Verify we have 20 endpoints in the extended API."""

    def test_endpoint_count(self):
        """Count all endpoints in extended API."""
        from app.routes.api_extended import (
            theories_router,
            entrenchment_router,
            graph_router,
            bundles_router,
            history_router
        )

        theory_endpoints = len([r for r in theories_router.routes if hasattr(r, 'path')])
        entrenchment_endpoints = len([r for r in entrenchment_router.routes if hasattr(r, 'path')])
        graph_endpoints = len([r for r in graph_router.routes if hasattr(r, 'path')])
        bundle_endpoints = len([r for r in bundles_router.routes if hasattr(r, 'path')])
        history_endpoints = len([r for r in history_router.routes if hasattr(r, 'path')])

        total = (theory_endpoints + entrenchment_endpoints + graph_endpoints +
                bundle_endpoints + history_endpoints)

        # We should have ~20 endpoints (4 per category)
        assert total >= 20, f"Expected at least 20 endpoints, got {total}"
