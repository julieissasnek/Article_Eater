"""
Tests for Causal API Endpoints.
Sprint 3.0.1-F
"""

import pytest
from unittest.mock import MagicMock, patch
from app.routes.api_causal import causal_router, CounterfactualQuery

class TestCausalEndpoints:
    @pytest.fixture
    def mock_web(self):
        mock_web = MagicMock()
        
        b1 = MagicMock()
        b1.belief_id = "stress"
        b1.credence.value = 0.8
        
        b2 = MagicMock()
        b2.belief_id = "nature_views"
        b2.credence.value = 0.7
        
        mock_web.beliefs = {"stress": b1, "nature_views": b2}
        
        c1 = MagicMock()
        c1.source_id = "nature_views"
        c1.target_id = "stress"
        c1.polarity.value = "NEGATIVE"
        c1.strength = 0.6
        
        mock_web.constraints = {"c1": c1}
        
        return mock_web

    @pytest.mark.asyncio
    async def test_get_causal_paths(self, mock_web):
        from app.routes.api_causal import get_causal_paths
        
        with patch('app.routes.api_causal.get_web', return_value=mock_web):
            result = await get_causal_paths("nature_views", "stress")
            
        assert result.source == "nature_views"
        assert result.target == "stress"
        assert result.path_exists is True
        assert len(result.paths) > 0

    @pytest.mark.asyncio
    async def test_analyze_intervention(self, mock_web):
        from app.routes.api_causal import analyze_intervention
        
        with patch('app.routes.api_causal.get_web', return_value=mock_web):
            result = await analyze_intervention("nature_views", magnitude=1.0)
            
        assert result.target == "nature_views"
        assert len(result.downstream_impacts) == 1
        # magnitude 1.0 * strength 0.6 * polarity NEGATIVE (-1.0) = -0.6
        assert result.downstream_impacts[0]["projected_change"] == -0.6
        assert len(result.upstream_causes) == 0

    @pytest.mark.asyncio
    async def test_query_counterfactual(self, mock_web):
        from app.routes.api_causal import query_counterfactual
        
        query = CounterfactualQuery(
            assumption={"strength_shift": -0.3}, 
            target_variable="stress"
        )
        
        with patch('app.routes.api_causal.get_web', return_value=mock_web):
            result = await query_counterfactual(query)
            
        assert result.original_state == 0.8
        assert result.counterfactual_state == 0.5
        assert result.difference == -0.3
