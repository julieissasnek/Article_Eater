# API Endpoints Quick Reference

**Sprint 3.0.1 — 26 New Endpoints (all active at /api/v1)**
**Status**: ✓ Complete | 43/43 Tests Passing | Ready for Production

---

## Sprint 3.0.1-D: Extended Layer (20 Endpoints)

### Theory Management (4 endpoints)
```
GET    /theories/list                           - List all theories with pagination
GET    /theories/{theory_id}                    - Get single theory details
GET    /theories/{theory_id}/beliefs            - List beliefs within theory
POST   /theories/create                         - Create new theory
```

### Entrenchment Analytics (4 endpoints)
```
GET    /entrenchment/scores                     - Ranked entrenchment scores (all beliefs)
GET    /entrenchment/{belief_id}                - Detailed entrenchment for one belief
POST   /entrenchment/compare                    - Compare entrenchment of two beliefs
GET    /entrenchment/histogram                  - Distribution histogram with stats
```

### Causal Graph Operations (4 endpoints)
```
GET    /graph/structure                         - Full graph topology (nodes, edges, density)
GET    /graph/{belief_id}/neighbors             - Neighbors: supports/supported-by/contradicts
POST   /graph/paths                             - Find causal pathways between beliefs
GET    /graph/clusters                          - Community detection (clustering)
```

### Export Bundles (4 endpoints)
```
GET    /bundles/purposes                        - Available export purposes
POST   /bundles/create                          - Generate new export bundle (async)
GET    /bundles/{bundle_id}                     - Get bundle status and metadata
GET    /bundles/{bundle_id}/download            - Download bundle file
```

### Snapshots & History (4 endpoints)
```
POST   /history/snapshots                       - Create snapshot of web state
GET    /history/snapshots                       - List all snapshots (paginated)
POST   /history/diff                            - Diff between two snapshots
GET    /history/snapshots/{snapshot_id}         - Get complete snapshot data
```

---

## Sprint 3.0.1-E: Batch Operations (3 Endpoints)

```
POST   /batch/beliefs                           - Bulk create/update beliefs (async)
POST   /batch/papers                            - Bulk register papers (async)
GET    /batch/jobs/{job_id}                     - Check batch job status and progress
```

---

## Sprint 3.0.1-F: Causal Inference (3 Endpoints)

**Per Pearl's causal hierarchy framework:**

```
GET    /causal/paths/{from_id}/{to_id}          - Observational: find causal pathways
GET    /causal/interventions/{target}           - Interventional: project do(X=x) effects
POST   /causal/counterfactual                   - Counterfactual: "what-if" queries
GET    /causal/convergence/{template_id}        - Multi-framework convergence analysis
```

---

## Standard Query Parameters

### Pagination (all list endpoints)
```
limit=20          - Items per page (default 20)
offset=0          - Pagination offset (default 0)
```

### Filtering (varies by endpoint)
```
theory=X          - Filter by theory ID
level=THEORETICAL - Filter by level
min_credence=0.6  - Filter by minimum credence
search=keyword    - Full-text search
tags=tag1,tag2    - Filter by tags (comma-separated)
```

---

## Response Status Codes

| Code | Meaning | Common When |
|------|---------|---|
| 200 | OK | Successful GET/POST |
| 201 | Created | New resource created |
| 202 | Accepted | Async job submitted |
| 400 | Bad Request | Invalid parameters |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Resource already exists |
| 422 | Unprocessable | Validation failed |
| 500 | Server Error | Internal error |

---

## Standard Response Format

### List Response (Pagination)
```json
{
  "items": [...],
  "total": 150,
  "limit": 20,
  "offset": 0,
  "_links": {
    "self": "/api/v1/theories/list?limit=20&offset=0",
    "next": "/api/v1/theories/list?limit=20&offset=20",
    "prev": null
  }
}
```

### Error Response
```json
{
  "error": {
    "code": "BELIEF_NOT_FOUND",
    "message": "Belief with ID 'B999' not found",
    "request_id": "req_xyz789",
    "timestamp": "2026-03-02T14:30:00Z"
  }
}
```

### Async Job Response
```json
{
  "job_id": "job_beliefs_1709391000000",
  "status": "processing|complete|failed",
  "progress": 0.45,
  "created_at": "2026-03-02T14:30:00Z",
  "result_url": "/api/v1/batch/jobs/job_beliefs_1709391000000"
}
```

---

## Usage Examples

### List theories
```bash
curl "http://localhost:8000/api/v1/theories/list?limit=10&level=theory"
```

### Get entrenchment ranking
```bash
curl "http://localhost:8000/api/v1/entrenchment/scores?limit=5"
```

### Find causal paths
```bash
curl "http://localhost:8000/api/v1/causal/paths/b_nature_attn/b_stress_reduction?max_depth=5"
```

### Analyze intervention
```bash
curl "http://localhost:8000/api/v1/causal/interventions/b_nature_exposure?magnitude=0.5"
```

### Submit batch belief job
```bash
curl -X POST http://localhost:8000/api/v1/batch/beliefs \
  -H "Content-Type: application/json" \
  -d '{
    "beliefs": [
      {"belief_id":"b1","content":"New belief","credence":0.75}
    ]
  }'
```

### Check batch job status
```bash
curl "http://localhost:8000/api/v1/batch/jobs/job_beliefs_1709391000000"
```

### Create export bundle
```bash
curl -X POST http://localhost:8000/api/v1/bundles/create \
  -H "Content-Type: application/json" \
  -d '{
    "title":"ART Review",
    "purpose":"literature_review",
    "format":"markdown",
    "filters":{"theories":["art"],"min_credence":0.6}
  }'
```

### List snapshots
```bash
curl "http://localhost:8000/api/v1/history/snapshots?limit=10"
```

---

## Implementation Files

| File | Purpose | Lines |
|------|---------|-------|
| `/app/routes/api_extended.py` | 20 extended endpoints | 1,365 |
| `/app/routes/api_batch.py` | 3 batch endpoints | 164 |
| `/app/routes/api_causal.py` | 3-4 causal endpoints | 142 |
| `/app/main.py` | Router registration | +10 modified |
| `/tests/test_api_extended.py` | 37 tests | 656 |
| `/tests/test_api_batch.py` | 3 tests | 50+ |
| `/tests/test_api_causal.py` | 3 tests | 50+ |

---

## Testing

Run all tests:
```bash
pytest tests/test_api_extended.py tests/test_api_batch.py tests/test_api_causal.py -v
```

Result: **43 tests, all passing** ✓

---

## Documentation

- **Full API Spec**: `/docs/API_ENDPOINTS_SPRINT_3.0.1_COMPLETE.md`
- **Completion Report**: `/docs/SPRINT_3.0.1_COMPLETION_REPORT.md`
- **Design Document**: `/docs/archive/API_DESIGN_SPRINT_3.0.1.md`

---

## Key Features

- ✓ RESTful design (Fielding)
- ✓ Layered complexity (Simon)
- ✓ Resource-oriented (Stonebraker)
- ✓ Pagination with HATEOAS
- ✓ Async batch processing (Dean)
- ✓ Pearl's causal hierarchy
- ✓ Multi-format export
- ✓ Version control (snapshots)
- ✓ Comprehensive testing
- ✓ Production-ready

---

**All endpoints active at**: `http://localhost:8000/api/v1/`
**Swagger UI**: `http://localhost:8000/docs`
**ReDoc**: `http://localhost:8000/redoc`

