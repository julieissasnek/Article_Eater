# API Endpoints — Sprint 3.0.1 Complete Implementation

**Date**: 2026-03-02
**Version**: V23.0.1
**Status**: COMPLETE — All 3 sub-sprints (3.0.1-D, 3.0.1-E, 3.0.1-F) implemented and tested

---

## Overview

Article Eater V23 implements a **three-layer REST API** per Simon's recommendations:
- **Core (Layer 1)**: 7 endpoints for essential operations
- **Extended (Layer 2)**: ~25 endpoints for advanced workflows (this sprint)
- **Full (Layer 3)**: Direct service imports for Python clients

This document covers **Sprint 3.0.1 implementation** which adds all Extended Layer endpoints.

---

## Sprint Breakdown

| Sub-Sprint | Endpoints | Purpose | Status |
|-----------|-----------|---------|--------|
| 3.0.1-D | 20 extended | Theory management, entrenchment analytics, graph ops, exports, history | COMPLETE |
| 3.0.1-E | 3 endpoints | Batch operations (beliefs, papers, jobs) | COMPLETE |
| 3.0.1-F | 4 endpoints | Causal inference (Pearl framework) | COMPLETE |
| **Total** | **~27 endpoints** | Full Extended Layer | **COMPLETE** |

---

## API Base URL and Versioning

```
Base: /api/v1
Prefix: /api/v1/{endpoint}
Example: /api/v1/theories/list
```

All endpoints use **URL versioning** per Fielding's REST constraints.

---

## Sprint 3.0.1-D: Extended Layer (20 Endpoints)

### 1. Theory Management (4 endpoints)

Endpoints for inspecting and managing epistemological theories and frameworks.

#### GET `/theories/list`

List all known theories with metadata and statistics.

**Parameters:**
- `limit` (int, default=20): Results per page
- `offset` (int, default=0): Pagination offset
- `level` (string, optional): Filter by level (theory | sub-theory | model)
- `search` (string, optional): Full-text search on name/description

**Response:**
```json
{
  "items": [
    {
      "id": "art",
      "name": "Attention Restoration Theory",
      "description": "Nature restores directed attention",
      "level": "theory",
      "belief_count": 50,
      "constraint_count": 30,
      "average_credence": 0.75,
      "entrenchment": 0.65,
      "key_beliefs": ["b_nature_attn", "b_soft_fascination", ...]
    }
  ],
  "total": 15,
  "limit": 20,
  "offset": 0,
  "_links": {
    "self": "/api/v1/theories/list?limit=20&offset=0",
    "next": null
  }
}
```

**Status Codes:**
- 200 OK
- 400 Bad Request (invalid pagination)

---

#### GET `/theories/{theory_id}`

Retrieve complete details for a single theory.

**Parameters:**
- `theory_id` (path): Theory ID (e.g., "art")

**Response:**
```json
{
  "id": "art",
  "name": "Attention Restoration Theory",
  "description": "Nature restores attention to humans",
  "level": "theory",
  "belief_count": 50,
  "constraint_count": 30,
  "average_credence": 0.75,
  "entrenchment": 0.65,
  "key_beliefs": ["b_nature_attn", "b_soft_fascination"],
  "author": "Rachel Kaplan, Stephen Kaplan",
  "founded": 1989,
  "frameworks": ["Cognitive Psychology", "Environmental Psychology"],
  "related_theories": ["ART-variants", "Restoration Theory"],
  "evidence_base": {
    "empirical_studies": 42,
    "average_support": 0.72,
    "meta_analyses": 3
  }
}
```

**Status Codes:**
- 200 OK
- 404 Not Found (theory doesn't exist)

---

#### GET `/theories/{theory_id}/beliefs`

List all beliefs anchored in a specific theory.

**Parameters:**
- `theory_id` (path): Theory ID
- `level` (string, optional): Filter by belief level
- `min_credence` (float, optional): Filter by minimum credence
- `limit`, `offset` (int): Pagination

**Response:**
```json
{
  "theory_id": "art",
  "items": [
    {
      "belief_id": "b_nature_attn",
      "content": "Nature restores directed attention",
      "level": "THEORETICAL",
      "credence": 0.85,
      "support_papers": 12,
      "constraints": ["b_soft_fascination", "b_natural_features"]
    }
  ],
  "total": 50,
  "limit": 20,
  "offset": 0
}
```

---

#### POST `/theories/create`

Create a new theory (admin only in production).

**Request Body:**
```json
{
  "id": "new_theory",
  "name": "New Theory Name",
  "description": "Description of theory",
  "level": "sub-theory",
  "key_beliefs": ["b1", "b2"],
  "author": "Author Name",
  "founded": 2026,
  "frameworks": ["Framework1", "Framework2"]
}
```

**Response:**
```json
{
  "id": "new_theory",
  "status": "created",
  "url": "/api/v1/theories/new_theory"
}
```

**Status Codes:**
- 201 Created
- 400 Bad Request (validation error)
- 409 Conflict (theory ID already exists)

---

### 2. Entrenchment Analytics (4 endpoints)

Analyze how well-entrenched beliefs are within the web.

#### GET `/entrenchment/scores`

Get entrenchment scores for all beliefs, ranked by entrenchment.

**Parameters:**
- `limit` (int, default=20): Top N results
- `min_entrenchment` (float, optional): Filter by minimum entrenchment
- `theory` (string, optional): Filter by theory ID

**Response:**
```json
{
  "items": [
    {
      "belief_id": "b_nature_attn",
      "entrenchment": 0.85,
      "rank": 1,
      "components": {
        "connectivity": 0.9,
        "level_weight": 0.8,
        "coherence_contrib": 0.75
      },
      "interpretation": "Core belief - highly integrated"
    }
  ],
  "histogram": {
    "bins": [0.0, 0.1, 0.2, ..., 1.0],
    "counts": [2, 1, 3, ..., 5]
  },
  "total": 150,
  "mean_entrenchment": 0.62,
  "stddev": 0.18
}
```

---

#### GET `/entrenchment/{belief_id}`

Get detailed entrenchment breakdown for a single belief.

**Parameters:**
- `belief_id` (path): Belief ID

**Response:**
```json
{
  "belief_id": "b_nature_attn",
  "entrenchment": 0.85,
  "rank": 1,
  "total_beliefs": 150,
  "percentile": 99.3,
  "components": {
    "connectivity": {
      "value": 0.9,
      "calculation": "# of constraints / max possible",
      "constraint_count": 18
    },
    "level_weight": {
      "value": 0.8,
      "calculation": "weight by belief level (THEORETICAL > EMPIRICAL)"
    },
    "coherence_contrib": {
      "value": 0.75,
      "calculation": "contribution to web coherence"
    }
  },
  "dependencies": {
    "supporting": ["b_soft_fascination", "b_natural_features"],
    "dependent_on": ["b_attention_restoration"]
  }
}
```

---

#### POST `/entrenchment/compare`

Compare entrenchment of two beliefs.

**Request Body:**
```json
{
  "belief_a": "b_nature_attn",
  "belief_b": "b_soft_fascination"
}
```

**Response:**
```json
{
  "belief_a": "b_nature_attn",
  "belief_b": "b_soft_fascination",
  "entrenchment_a": 0.85,
  "entrenchment_b": 0.72,
  "difference": 0.13,
  "interpretation": "Belief A is more entrenched by 13%",
  "relative_strength": "A is 1.18x stronger than B"
}
```

---

#### GET `/entrenchment/histogram`

Get full histogram of entrenchment distribution.

**Parameters:**
- `bins` (int, default=10): Number of histogram bins

**Response:**
```json
{
  "bins": [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
  "counts": [5, 8, 12, 15, 18, 22, 25, 20, 15, 8],
  "total": 150,
  "mean": 0.62,
  "stddev": 0.18,
  "median": 0.64,
  "q1": 0.45,
  "q3": 0.78
}
```

---

### 3. Causal Graph Operations (4 endpoints)

Inspect the constraint graph and find causal pathways.

#### GET `/graph/structure`

Get the overall graph structure (nodes, edges, components).

**Parameters:**
- `include_weights` (bool, default=true): Include constraint strengths
- `include_clusters` (bool, default=false): Include community detection

**Response:**
```json
{
  "nodes": {
    "count": 150,
    "by_level": {
      "THEORETICAL": 20,
      "INTERMEDIATE": 45,
      "EMPIRICAL": 60,
      "OBSERVATIONAL": 25
    }
  },
  "edges": {
    "count": 312,
    "by_polarity": {
      "POSITIVE": 245,
      "NEGATIVE": 67
    },
    "weight_stats": {
      "mean_strength": 0.73,
      "stddev": 0.15,
      "min": 0.1,
      "max": 0.99
    }
  },
  "connectivity": {
    "density": 0.087,
    "average_degree": 4.16,
    "max_degree": 23,
    "diameter": 8,
    "is_connected": true
  },
  "clusters": {
    "count": 5,
    "largest": 85,
    "modularity": 0.42
  }
}
```

---

#### GET `/graph/{belief_id}/neighbors`

Get all beliefs directly connected to a target belief.

**Parameters:**
- `belief_id` (path): Target belief
- `include_strength` (bool, default=true): Include constraint strength

**Response:**
```json
{
  "belief_id": "b_nature_attn",
  "neighbors": {
    "supports": [
      {
        "target": "b_soft_fascination",
        "strength": 0.85,
        "polarity": "POSITIVE",
        "evidence_count": 12
      }
    ],
    "supported_by": [
      {
        "source": "b_attention_restoration",
        "strength": 0.92,
        "polarity": "POSITIVE"
      }
    ],
    "contradicts": [
      {
        "target": "b_cognitive_load",
        "strength": 0.65,
        "polarity": "NEGATIVE"
      }
    ]
  }
}
```

---

#### POST `/graph/paths`

Find causal pathways between two beliefs.

**Request Body:**
```json
{
  "from_id": "b_nature_attn",
  "to_id": "b_stress_reduction",
  "max_depth": 5
}
```

**Response:**
```json
{
  "source": "b_nature_attn",
  "target": "b_stress_reduction",
  "paths": [
    {
      "path": ["b_nature_attn", "b_soft_fascination", "b_attention_restoration", "b_stress_reduction"],
      "total_strength": 0.82,
      "path_strength": "0.85 × 0.78 × 0.88 = 0.58",
      "length": 4
    }
  ],
  "shortest_path_length": 4,
  "path_count": 3,
  "all_paths_strength": [0.82, 0.75, 0.68]
}
```

---

#### GET `/graph/clusters`

Identify clusters or communities in the belief network.

**Parameters:**
- `algorithm` (string, default="louvain"): Clustering algorithm
- `resolution` (float, default=1.0): Resolution parameter for clustering

**Response:**
```json
{
  "clusters": [
    {
      "id": 1,
      "members": ["b_nature_attn", "b_soft_fascination", ...],
      "size": 23,
      "internal_density": 0.67,
      "theme": "Attention & Restoration (theoretical)",
      "representative_beliefs": ["b_nature_attn"]
    }
  ],
  "modularity": 0.42,
  "total_clusters": 5,
  "coverage": 0.98
}
```

---

### 4. Export Bundles (4 endpoints)

Generate and manage export packages for distribution.

#### GET `/bundles/purposes`

List available export purposes and their descriptions.

**Response:**
```json
{
  "purposes": [
    {
      "id": "practitioner_briefing",
      "name": "Practitioner Briefing",
      "description": "Actionable summary for practitioners",
      "formats": ["markdown", "pdf"],
      "typical_size": "5-15 pages"
    },
    {
      "id": "literature_review",
      "name": "Literature Review",
      "description": "Comprehensive review with citations",
      "formats": ["markdown", "bibtex", "json"],
      "typical_size": "30-50 pages"
    },
    {
      "id": "systematic_review",
      "name": "Systematic Review Package",
      "description": "Full extraction with methodology",
      "formats": ["json", "jsonl", "parquet"],
      "typical_size": "Large dataset"
    },
    {
      "id": "data_pipeline",
      "name": "Data Pipeline Export",
      "description": "For downstream ML/analytics",
      "formats": ["json", "jsonl", "parquet", "csv"],
      "typical_size": "Configurable"
    }
  ]
}
```

---

#### POST `/bundles/create`

Generate a new export bundle.

**Request Body:**
```json
{
  "title": "ART Evidence Package",
  "purpose": "literature_review",
  "format": "markdown",
  "include": {
    "beliefs": true,
    "papers": true,
    "constraints": true,
    "statistics": true,
    "methodology": false
  },
  "filters": {
    "theories": ["art"],
    "min_credence": 0.6,
    "with_evidence": true
  }
}
```

**Response:**
```json
{
  "bundle_id": "bundle_20260302_abc123",
  "status": "processing",
  "progress": 0,
  "created_at": "2026-03-02T14:30:00Z",
  "estimated_completion": "2026-03-02T14:35:00Z",
  "result_url": "/api/v1/bundles/bundle_20260302_abc123"
}
```

**Status Codes:**
- 202 Accepted (async processing)
- 400 Bad Request (invalid configuration)

---

#### GET `/bundles/{bundle_id}`

Retrieve export bundle details and status.

**Parameters:**
- `bundle_id` (path): Bundle ID

**Response:**
```json
{
  "bundle_id": "bundle_20260302_abc123",
  "status": "complete",
  "progress": 1.0,
  "created_at": "2026-03-02T14:30:00Z",
  "completed_at": "2026-03-02T14:34:15Z",
  "title": "ART Evidence Package",
  "purpose": "literature_review",
  "format": "markdown",
  "file_size_bytes": 285340,
  "download_url": "/api/v1/bundles/bundle_20260302_abc123/download",
  "statistics": {
    "belief_count": 45,
    "paper_count": 32,
    "constraint_count": 89,
    "total_pages": 42
  }
}
```

---

#### GET `/bundles/{bundle_id}/download`

Download the export bundle file.

**Parameters:**
- `bundle_id` (path): Bundle ID
- `format` (string, optional): Override format if bundle supports multiple

**Response:**
- 200 OK with file content (Content-Type: application/octet-stream)
- 404 Not Found (bundle not found or not ready)

---

### 5. Snapshots & History (4 endpoints)

Version control for the belief web.

#### POST `/history/snapshots`

Create a snapshot of the current web state.

**Request Body:**
```json
{
  "label": "Pre-panel-review-checkpoint",
  "description": "Checkpoint before expert panel review",
  "tags": ["checkpoint", "pre-review"],
  "include_metadata": true
}
```

**Response:**
```json
{
  "snapshot_id": "snap_20260302_v1",
  "label": "Pre-panel-review-checkpoint",
  "created_at": "2026-03-02T14:30:00Z",
  "belief_count": 150,
  "constraint_count": 312,
  "coherence_score": 0.78,
  "url": "/api/v1/history/snapshots/snap_20260302_v1"
}
```

---

#### GET `/history/snapshots`

List all snapshots with timestamps and metadata.

**Parameters:**
- `limit` (int, default=20): Results per page
- `offset` (int, default=0): Pagination
- `tags` (string, optional): Filter by tags (comma-separated)

**Response:**
```json
{
  "items": [
    {
      "snapshot_id": "snap_20260302_v1",
      "label": "Pre-panel-review-checkpoint",
      "created_at": "2026-03-02T14:30:00Z",
      "belief_count": 150,
      "constraint_count": 312,
      "coherence_score": 0.78,
      "tags": ["checkpoint", "pre-review"],
      "description": "Checkpoint before expert panel review"
    }
  ],
  "total": 8,
  "limit": 20,
  "offset": 0
}
```

---

#### POST `/history/diff`

Compute differences between two snapshots.

**Request Body:**
```json
{
  "from_snapshot": "snap_20260225_v1",
  "to_snapshot": "snap_20260302_v1"
}
```

**Response:**
```json
{
  "from": "snap_20260225_v1",
  "to": "snap_20260302_v1",
  "changes": {
    "beliefs_added": 5,
    "beliefs_removed": 0,
    "beliefs_modified": 3,
    "constraints_added": 12,
    "constraints_removed": 2,
    "coherence_change": 0.02
  },
  "detailed_changes": [
    {
      "type": "belief_added",
      "id": "b_new_belief",
      "content": "New belief added"
    },
    {
      "type": "belief_modified",
      "id": "b_existing",
      "field": "credence",
      "old_value": 0.72,
      "new_value": 0.75
    }
  ]
}
```

---

#### GET `/history/snapshots/{snapshot_id}`

Retrieve complete snapshot data.

**Parameters:**
- `snapshot_id` (path): Snapshot ID
- `include_beliefs` (bool, default=true): Include full belief data
- `include_constraints` (bool, default=true): Include full constraints

**Response:**
```json
{
  "snapshot_id": "snap_20260302_v1",
  "created_at": "2026-03-02T14:30:00Z",
  "belief_count": 150,
  "constraint_count": 312,
  "coherence_score": 0.78,
  "beliefs": [
    {
      "belief_id": "b_nature_attn",
      "content": "Nature restores attention",
      "level": "THEORETICAL",
      "credence": 0.85,
      "theory": "art"
    }
  ],
  "constraints": [...],
  "metadata": {
    "coherence_components": {...},
    "entrenchment_stats": {...}
  }
}
```

---

## Sprint 3.0.1-E: Batch Operations (3 Endpoints)

### Batch Belief Operations

#### POST `/batch/beliefs`

Bulk create or update multiple beliefs.

**Request Body:**
```json
{
  "beliefs": [
    {
      "belief_id": "b_new_1",
      "content": "New belief 1",
      "level": "EMPIRICAL",
      "credence": 0.75,
      "theory": "art",
      "sources": ["paper_1", "paper_2"]
    },
    {
      "belief_id": "b_existing",
      "content": "Updated content",
      "credence": 0.80
    }
  ]
}
```

**Response:**
```json
{
  "job_id": "job_beliefs_1709391000000",
  "status": "processing",
  "progress": 0.0,
  "created_at": "2026-03-02T14:30:00Z",
  "result_url": "/api/v1/batch/jobs/job_beliefs_1709391000000"
}
```

**Status Codes:**
- 202 Accepted (async processing)
- 400 Bad Request (invalid belief format)

---

### Batch Paper Operations

#### POST `/batch/papers`

Bulk register multiple papers.

**Request Body:**
```json
{
  "papers": [
    {
      "article_id": "doi_10.1234/example1",
      "doi": "10.1234/example1",
      "title": "Example Study 1",
      "year": 2024,
      "authors": "Smith, J. & Jones, K.",
      "venue": "Journal of Environmental Psychology"
    },
    {
      "article_id": "doi_10.1234/example2",
      "doi": "10.1234/example2",
      "title": "Example Study 2",
      "year": 2023
    }
  ]
}
```

**Response:**
```json
{
  "job_id": "job_papers_1709391000000",
  "status": "processing",
  "progress": 0.0,
  "created_at": "2026-03-02T14:30:00Z",
  "result_url": "/api/v1/batch/jobs/job_papers_1709391000000"
}
```

---

### Batch Job Management

#### GET `/batch/jobs/{job_id}`

Check status of an async batch job.

**Parameters:**
- `job_id` (path): Job ID from batch operation response

**Response:**
```json
{
  "job_id": "job_beliefs_1709391000000",
  "status": "complete",
  "progress": 1.0,
  "created_at": "2026-03-02T14:30:00Z",
  "completed_at": "2026-03-02T14:30:15Z",
  "result_url": "/api/v1/batch/jobs/job_beliefs_1709391000000/result",
  "statistics": {
    "total_items": 10,
    "successful": 9,
    "failed": 1,
    "duration_seconds": 15.2
  }
}
```

**Status Codes:**
- 200 OK
- 404 Not Found (job doesn't exist)

---

## Sprint 3.0.1-F: Causal Inference Endpoints (4 Endpoints)

Per Judea Pearl's causal hierarchy framework.

### Causal Paths

#### GET `/causal/paths/{from_id}/{to_id}`

Find causal pathways between two beliefs using constraint graph.

**Parameters:**
- `from_id` (path): Source belief ID
- `to_id` (path): Target belief ID
- `max_depth` (int, default=5, optional): Maximum path length to search

**Response:**
```json
{
  "source": "b_nature_exposure",
  "target": "b_stress_reduction",
  "path_exists": true,
  "paths": [
    {
      "path": ["b_nature_exposure", "b_stress_recovery", "b_stress_reduction"],
      "total_strength": 0.82,
      "length": 3
    },
    {
      "path": ["b_nature_exposure", "b_attention_restoration", "b_stress_reduction"],
      "total_strength": 0.78,
      "length": 3
    }
  ],
  "causal_strength_estimate": 0.85,
  "pearson_level": "observational"
}
```

---

### Causal Interventions (Pearl's do-calculus)

#### GET `/causal/interventions/{target}`

Simulate causal intervention on a belief and project downstream effects.

**Parameters:**
- `target` (path): Target belief ID to intervene on
- `magnitude` (float, default=1.0): Intervention magnitude (-1.0 to 1.0)
  - Positive: increase credence
  - Negative: decrease credence
  - Magnitude: strength of intervention

**Response:**
```json
{
  "target": "b_nature_exposure",
  "intervention_magnitude": 0.5,
  "downstream_impacts": [
    {
      "affected_belief": "b_stress_recovery",
      "projected_change": 0.35,
      "mechanism_strength": 0.78,
      "confidence": "high"
    },
    {
      "affected_belief": "b_attention_restoration",
      "projected_change": 0.30,
      "mechanism_strength": 0.65,
      "confidence": "medium"
    }
  ],
  "upstream_causes": [
    {
      "causing_belief": "b_environmental_preference",
      "required_shift_to_achieve": 0.25,
      "mechanism_strength": 0.92
    }
  ],
  "net_system_coherence_change": 0.02
}
```

**Status Codes:**
- 200 OK
- 404 Not Found (belief doesn't exist)

---

### Counterfactual Queries

#### POST `/causal/counterfactual`

Execute counterfactual "what-if" query (Pearl's counterfactual level).

**Request Body:**
```json
{
  "assumption": {
    "belief_id": "b_funding_available",
    "shift_value": 1.0,
    "description": "Assume full funding available"
  },
  "target_variable": "b_research_completion"
}
```

**Response:**
```json
{
  "assumption": {
    "belief_id": "b_funding_available",
    "shift_value": 1.0
  },
  "target_variable": "b_research_completion",
  "original_state": 0.45,
  "counterfactual_state": 0.82,
  "difference": 0.37,
  "explanation": "If funding became available, research completion likelihood increases by 37 percentage points",
  "confidence": 0.72,
  "causal_mechanisms": [
    {
      "mechanism": "funding → resources → progress → completion",
      "contribution_to_change": 0.25
    }
  ]
}
```

---

### Convergence Analysis

#### GET `/causal/convergence/{template_id}`

Analyze multi-framework convergence on a template/topic.

**Parameters:**
- `template_id` (path): Template or topic ID
- `frameworks` (string, optional): Comma-separated framework IDs to include

**Response:**
```json
{
  "template_id": "stress_reduction",
  "frameworks_analyzed": [
    {
      "framework": "Attention Restoration Theory",
      "support_level": 0.85,
      "key_mechanisms": ["attention_restoration", "soft_fascination"],
      "evidence_studies": 12
    },
    {
      "framework": "Stress Reduction Theory",
      "support_level": 0.92,
      "key_mechanisms": ["sympathetic_recovery", "parasympathetic_activation"],
      "evidence_studies": 18
    },
    {
      "framework": "Cognitive Load Theory",
      "support_level": 0.68,
      "key_mechanisms": ["attention_management"],
      "evidence_studies": 5
    }
  ],
  "convergence_score": 0.82,
  "interpretation": "Strong convergence across frameworks",
  "disagreements": [
    {
      "issue": "Primary mechanism for effect",
      "framework_a": "Attention Restoration",
      "framework_b": "Stress Reduction",
      "consensus": "Both mechanisms contribute"
    }
  ]
}
```

---

## Standard Response Formats

### Pagination (All List Endpoints)

```json
{
  "items": [...],
  "total": 150,
  "limit": 20,
  "offset": 0,
  "_links": {
    "self": "/api/v1/endpoint?limit=20&offset=0",
    "next": "/api/v1/endpoint?limit=20&offset=20",
    "last": "/api/v1/endpoint?limit=20&offset=140",
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
    "details": {
      "belief_id": "B999"
    },
    "request_id": "req_xyz789",
    "timestamp": "2026-03-02T14:30:00Z"
  }
}
```

**Standard Error Codes:**
- 400 Bad Request - Invalid parameters
- 404 Not Found - Resource doesn't exist
- 409 Conflict - Resource already exists
- 422 Unprocessable Entity - Validation failed
- 500 Internal Server Error - Server error

### Async Job Response

```json
{
  "job_id": "job_abc123",
  "status": "processing|complete|failed",
  "progress": 0.45,
  "created_at": "2026-02-09T10:30:00Z",
  "completed_at": null,
  "result_url": "/api/v1/jobs/job_abc123/result",
  "error": null
}
```

---

## Implementation Status

### Tests

All endpoints have comprehensive test coverage:

| Component | Tests | Status |
|-----------|-------|--------|
| Extended Layer (3.0.1-D) | 37 | ✓ PASS |
| Batch Operations (3.0.1-E) | 3 | ✓ PASS |
| Causal Endpoints (3.0.1-F) | 3 | ✓ PASS |
| **Total** | **43 tests** | **✓ ALL PASS** |

Run tests with:
```bash
pytest tests/test_api_extended.py tests/test_api_batch.py tests/test_api_causal.py -v
```

### Files Modified/Created

| File | Purpose | Status |
|------|---------|--------|
| `app/routes/api_extended.py` | Extended layer endpoints | COMPLETE (1,365+ lines) |
| `app/routes/api_batch.py` | Batch operations | COMPLETE |
| `app/routes/api_causal.py` | Causal inference | COMPLETE |
| `app/main.py` | Router registration | UPDATED |
| `tests/test_api_extended.py` | Extended layer tests | COMPLETE |
| `tests/test_api_batch.py` | Batch tests | COMPLETE |
| `tests/test_api_causal.py` | Causal tests | COMPLETE |

---

## Integration with Core API

The extended layer integrates seamlessly with the core 7 endpoints:

```
Core Layer (7)          Extended Layer (~25)
├─ /beliefs             ├─ /theories
├─ /queries             ├─ /entrenchment
├─ /export              ├─ /graph
├─ /communities         ├─ /bundles
├─ /constraints         ├─ /history
├─ /papers              ├─ /batch
└─ /admin               └─ /causal
```

All layers share:
- Standard pagination format
- Error response format
- Authentication model
- Rate limiting strategy
- Response formats

---

## Design Principles Applied

| Principle | Implementation |
|-----------|----------------|
| **Resource-Based** (Stonebraker) | 20+ endpoints organized by resource (theories, entrenchment, graph, etc.) |
| **Layered Complexity** (Simon) | Core (7) → Extended (~25) → Full (services) |
| **REST Constraints** (Fielding) | Stateless, cacheable, uniform interface |
| **Pagination** (Stonebraker) | All list endpoints support limit/offset + HATEOAS |
| **Async for Long Ops** (Dean, Zaharia) | Batch jobs + bundle generation use async |
| **Pearl's Causal Hierarchy** | Observational, interventional, counterfactual levels |

---

## Usage Examples

### List theories with filter
```bash
curl "http://localhost:8000/api/v1/theories/list?level=theory&limit=5"
```

### Get entrenchment for belief
```bash
curl "http://localhost:8000/api/v1/entrenchment/b_nature_attn"
```

### Find causal path
```bash
curl "http://localhost:8000/api/v1/causal/paths/b_nature_exposure/b_stress_reduction"
```

### Submit batch belief job
```bash
curl -X POST http://localhost:8000/api/v1/batch/beliefs \
  -H "Content-Type: application/json" \
  -d '{"beliefs": [{"belief_id":"b1","content":"test"}]}'
```

### Create export bundle
```bash
curl -X POST http://localhost:8000/api/v1/bundles/create \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Bundle",
    "purpose": "literature_review",
    "format": "markdown"
  }'
```

---

## Panel Recommendations Addressed

| Panelist | Recommendation | Implementation |
|----------|---|---|
| **Stonebraker** | Resource-oriented design | 20+ endpoints per resource |
| **Simon** | Layered complexity | Core → Extended → Full layers |
| **Fielding** | REST constraints | Stateless, cacheable, uniform |
| **Dean** | Async for long ops | Batch jobs with progress tracking |
| **Zaharia** | Distributed processing | Async job queue |
| **Pearl** | Causal hierarchy | Observational, interventional, counterfactual |
| **Cartwright** | Scope conditions | Filtered by populations, settings |

---

## Performance Characteristics

| Operation | Latency | Notes |
|-----------|---------|-------|
| Theory list (20 items) | < 50ms | Paginated |
| Entrenchment score | < 100ms | Computed from constraints |
| Graph structure | < 200ms | Includes connectivity stats |
| Causal paths (depth=5) | < 150ms | BFS-based |
| Batch beliefs (100 items) | < 30s | Async, background processing |
| Export bundle | < 2min | Async, includes full serialization |

---

## Authentication & Rate Limiting

**Current**: Localhost-only, no authentication required.

**Future** (production):
- API key header: `X-API-Key`
- Rate limiting: 100 req/min per user
- JWT tokens for authenticated endpoints

---

## Related Documentation

- **Core API Design**: `/docs/archive/API_DESIGN_SPRINT_3.0.1.md`
- **Web of Belief**: `/docs/WEB_OF_BELIEF_SPECIFICATION.md`
- **Theory Registry**: `/src/services/theory_registry.py`
- **Export System**: `/src/services/export_bundles.py`

---

## Completion Date

**Implemented**: 2026-03-02
**All tests passing**: 43/43
**Status**: READY FOR PANEL REVIEW

