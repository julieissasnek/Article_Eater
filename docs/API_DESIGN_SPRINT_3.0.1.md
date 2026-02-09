# API Design — Sprint 3.0.1

**Date**: 2026-02-09
**Version**: V23.0.1
**Status**: Design Complete

## Design Principles (Panel Recommendations)

| Principle | Source | Implementation |
|-----------|--------|----------------|
| Resource-based design | Stonebraker, Fielding | ~25 endpoints organized by resource |
| Layered API | Simon | Core (7) → Extended (~20) → Full |
| URL versioning | Dean, Fowler | `/api/v1/` prefix |
| Pagination built-in | Stonebraker | `limit`, `offset` on all list endpoints |
| Async for long ops | Dean, Zaharia | Job IDs for queries/exports |
| HATEOAS links | Fielding | `_links` in responses |

---

## Layer 1: Core API (7 Endpoints)

These cover 80% of use cases and are the primary documentation focus.

### 1. Beliefs `/api/v1/beliefs/`

| Method | Path | Description |
|--------|------|-------------|
| GET | `/beliefs/` | List beliefs with filtering/pagination |
| GET | `/beliefs/{id}` | Get single belief with full details |
| POST | `/beliefs/` | Create new belief |
| PUT | `/beliefs/{id}` | Update belief |
| DELETE | `/beliefs/{id}` | Soft-delete belief (quarantine) |
| GET | `/beliefs/{id}/constraints` | Get constraints involving belief |
| GET | `/beliefs/{id}/sources` | Get source papers for belief |

**Filters** (query params):
- `status`: ACCEPTED, REJECTED, CONTESTED, STUB
- `level`: THEORETICAL, INTERMEDIATE, EMPIRICAL, OBSERVATIONAL
- `theory`: Theory ID
- `min_credence`: 0.0-1.0
- `search`: Full-text search
- `limit`, `offset`: Pagination

### 2. Queries `/api/v1/queries/`

| Method | Path | Description |
|--------|------|-------------|
| POST | `/queries/` | Submit natural language query |
| GET | `/queries/{id}` | Get query result |
| GET | `/queries/{id}/status` | Check query status (async) |
| GET | `/queries/history` | Recent queries for user |

**Query Request Fields**:
```json
{
  "query": "What reduces stress in hospitals?",
  "mode": "standard",  // quick | standard | deep
  "user_type": "practitioner",
  "include_scope": true,
  "include_practitioner_implications": true,
  "max_evidence": 10
}
```

**Query Response (Progressive Disclosure)**:
```json
{
  "query_id": "q_abc123",
  "status": "complete",
  "query_type": "WHAT",
  "causal_level": "interventional",
  "headline": "Plants, windows, and natural views consistently reduce stress.",
  "summary": { ... },
  "detail": { ... },
  "practical_implications": ["Add plants in waiting areas", ...],
  "scope_conditions": {"population": "adults", "setting": "healthcare"},
  "caveats": ["Most studies in Western contexts"],
  "key_sources": ["ulrich_1984", "kaplan_1989"]
}
```

### 3. Export `/api/v1/export/`

| Method | Path | Description |
|--------|------|-------------|
| POST | `/export/` | Generate export package |
| GET | `/export/{id}` | Get export result |
| GET | `/export/{id}/download/{filename}` | Download specific file |
| GET | `/export/formats` | List available formats |

**Formats**: markdown, json, bibtex, jsonl, parquet
**Purposes**: practitioner_briefing, literature_review, systematic_review, data_pipeline

### 4. Communities `/api/v1/communities/`

| Method | Path | Description |
|--------|------|-------------|
| GET | `/communities/` | List epistemic communities |
| GET | `/communities/{id}` | Get community details |
| GET | `/communities/{id}/beliefs` | Beliefs in community |
| GET | `/communities/{id}/credences` | Community-relative credences |

### 5. Constraints `/api/v1/constraints/`

| Method | Path | Description |
|--------|------|-------------|
| GET | `/constraints/` | List constraints |
| GET | `/constraints/{id}` | Get constraint details |
| POST | `/constraints/` | Create constraint |
| GET | `/constraints/tensions` | Get belief tensions |

### 6. Papers `/api/v1/papers/`

| Method | Path | Description |
|--------|------|-------------|
| GET | `/papers/` | List papers |
| GET | `/papers/{id}` | Get paper details |
| POST | `/papers/` | Register new paper |
| GET | `/papers/{id}/beliefs` | Beliefs from paper |
| GET | `/papers/{id}/lifecycle` | Paper processing status |

### 7. Admin `/api/v1/admin/`

| Method | Path | Description |
|--------|------|-------------|
| GET | `/admin/stats` | System statistics |
| GET | `/admin/health` | Health check |
| GET | `/admin/coherence` | Overall coherence metrics |
| POST | `/admin/recompute` | Trigger coherence recomputation |

---

## Layer 2: Extended API (~20 additional endpoints)

### Causal Endpoints (per Pearl)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/causal/paths/{from}/{to}` | Causal pathways between concepts |
| GET | `/causal/interventions/{target}` | Effects of intervening on X |
| POST | `/causal/counterfactual` | Counterfactual query |

### Scope Endpoints (per Cartwright)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/scope/populations` | Known populations in scope conditions |
| GET | `/scope/settings` | Known settings |
| GET | `/beliefs/{id}/scope` | Detailed scope for belief |

### Search Endpoints (per Bates)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/search/related/{id}` | Beliefs related to given belief |
| GET | `/search/trending` | Beliefs with changing credence |
| GET | `/search/canonical/{topic}` | Seminal works on topic |
| GET | `/search/gaps` | Research gaps |

### Lifecycle Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/lifecycle/health` | Pipeline health summary |
| GET | `/lifecycle/papers` | Papers by lifecycle stage |
| GET | `/lifecycle/blocked` | Blocked papers |

### Batch Operations (per Dean)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/batch/beliefs` | Bulk belief operations |
| POST | `/batch/papers` | Bulk paper registration |
| GET | `/batch/jobs/{id}` | Batch job status |

---

## Layer 3: Full Programmatic Access

All 225+ service methods exposed via:
- Direct service imports for Python clients
- GraphQL endpoint (future)
- WebSocket for real-time updates (future)

---

## Standard Response Formats

### Pagination
```json
{
  "items": [...],
  "total": 150,
  "limit": 20,
  "offset": 0,
  "_links": {
    "self": "/api/v1/beliefs/?limit=20&offset=0",
    "next": "/api/v1/beliefs/?limit=20&offset=20",
    "last": "/api/v1/beliefs/?limit=20&offset=140"
  }
}
```

### Error Response
```json
{
  "error": {
    "code": "BELIEF_NOT_FOUND",
    "message": "Belief with ID 'B999' not found",
    "details": {},
    "request_id": "req_xyz789"
  }
}
```

### Async Job Response
```json
{
  "job_id": "job_abc123",
  "status": "processing",
  "progress": 0.45,
  "created_at": "2026-02-09T10:30:00Z",
  "result_url": "/api/v1/queries/job_abc123/result"
}
```

---

## Authentication (Future)

Per security model in CLAUDE.md:
- Currently localhost-only, no auth required
- Future: API key header `X-API-Key`
- Rate limiting: 100 req/min default

---

## Implementation Status

| Endpoint Group | Status | File |
|----------------|--------|------|
| /beliefs/ | **Wired** | `app/routes/api_unified.py` |
| /queries/ | Scaffold (→3.0.2) | `app/routes/api_unified.py` |
| /export/ | Scaffold (→3.0.4) | `app/routes/api_unified.py` |
| /communities/ | **Wired** | `app/routes/api_unified.py` |
| /constraints/ | **Wired** | `app/routes/api_unified.py` |
| /papers/ | **Wired** | `app/routes/api_unified.py` |
| /admin/ | **Wired** | `app/routes/api_unified.py` |
| /lifecycle/ | **Complete** | `app/routes/lifecycle.py` |
| /causal/ | Not started (→3.0.1-F) | — |

### 3.0.1-B Wiring Complete (2026-02-09)

Endpoints now connected to actual services:
- `/beliefs/` → `WebOfBelief` service (list, get, create, constraints, evidence)
- `/papers/` → SQLite database (articles table)
- `/admin/stats` → Real counts from WebOfBelief + database
- `/admin/health` → Real connectivity checks (DB, WebOfBelief, registry)
- `/constraints/` → WebOfBelief constraint system
- `/communities/` → CommunityRegistry with seed data fallback

### Remaining (Sprint 3.0.2+)

- `/queries/` → LLM bridge integration (Sprint 3.0.2)
- `/export/` → Export engine integration (Sprint 3.0.4)

---

*Design complete: 2026-02-09*
*Core wiring complete: 2026-02-09*
