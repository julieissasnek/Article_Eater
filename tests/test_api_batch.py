"""
Tests for Batch API Endpoints.
Sprint 3.0.1-E
"""

import pytest
from unittest.mock import MagicMock, patch
from app.routes.api_batch import batch_router, BatchBeliefRequest, BatchPaperRequest, _batch_jobs
from fastapi import BackgroundTasks

class TestBatchEndpoints:
    @pytest.mark.asyncio
    async def test_batch_beliefs(self):
        from app.routes.api_batch import batch_beliefs
        
        request = BatchBeliefRequest(beliefs=[{"belief_id": "b1", "content": "Test belief 1"}])
        bg_tasks = BackgroundTasks()
        
        result = await batch_beliefs(request, bg_tasks)
        
        assert result.job_id.startswith("job_beliefs_")
        assert result.status == "processing"
        assert result.progress == 0.0
        assert result.job_id in _batch_jobs

    @pytest.mark.asyncio
    async def test_batch_papers(self):
        from app.routes.api_batch import batch_papers
        
        request = BatchPaperRequest(papers=[{"title": "Test Paper", "year": 2026}])
        bg_tasks = BackgroundTasks()
        
        result = await batch_papers(request, bg_tasks)
        
        assert result.job_id.startswith("job_papers_")
        assert result.status == "processing"
        assert result.progress == 0.0
        assert result.job_id in _batch_jobs

    @pytest.mark.asyncio
    async def test_get_batch_job(self):
        from app.routes.api_batch import get_batch_job
        
        # Insert a mock job
        _batch_jobs["test_job_123"] = {
            "job_id": "test_job_123",
            "status": "complete",
            "progress": 1.0,
            "created_at": "2026-02-10T12:00:00Z",
            "result_url": "/api/v1/batch/jobs/test_job_123/result"
        }
        
        result = await get_batch_job("test_job_123")
        assert result.job_id == "test_job_123"
        assert result.status == "complete"
        assert result.progress == 1.0
        
        from fastapi import HTTPException
        with pytest.raises(HTTPException):
            await get_batch_job("not_a_job")
