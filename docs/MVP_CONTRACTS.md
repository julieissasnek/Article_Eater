# MVP Contracts Documentation

*Version: MVP-0 (2026-02-11)*
*Owner: Terminal 2*

This document describes the JSON schemas that define the contract between MVP components.

---

## Overview

The MVP uses five key schemas:

| Schema | Purpose | Direction |
|--------|---------|-----------|
| `ae.paper.v1` | Paper input from Article Finder | AF → AE |
| `ae.rule.v1` | Extracted rules from papers | AE → Output |
| `ae.query_request.v1` | Query submission | User → QueryEngine |
| `ae.query_response.v1` | Query results | QueryEngine → User |
| `ae.gap_report.v1` | Knowledge gaps | QueryEngine → User |

---

## Schema Locations

All schemas are in `contracts/ae_af/schemas/`:

```
contracts/ae_af/schemas/
├── ae.paper.v1.schema.json       # Paper input (existing)
├── ae.rule.v1.schema.json        # Rule output (existing)
├── ae.query_request.v1.schema.json   # NEW: Query input
├── ae.query_response.v1.schema.json  # NEW: Query output
└── ae.gap_report.v1.schema.json      # NEW: Gap report
```

---

## 1. ae.paper.v1 — Paper Input

**Purpose**: Describes a paper submitted to Article Eater for processing.

**Required Fields**:
- `paper_id`: Unique identifier
- `title`: Paper title
- `authors`: List of author objects with `name` (required) and `orcid` (optional)
- `year`: Publication year (1500-3000)
- `source`: Provenance info (`finder_run_id`, `ingest_method`, `retrieved_at`)
- `files`: File info (`pdf_sha256`, `pdf_bytes`)

**Optional Fields**:
- `doi`, `venue`, `abstract`, `publisher`, `url`
- `triage`: Score, decision, reasons
- `rights`: License, allowed_storage
- `notes`: Human notes, tags

**Example**:
```json
{
  "schema": "ae.paper.v1",
  "paper_id": "kaplan_1989_001",
  "title": "The Experience of Nature",
  "authors": [{"name": "Rachel Kaplan"}, {"name": "Stephen Kaplan"}],
  "year": 1989,
  "source": {
    "finder_run_id": "af_run_123",
    "ingest_method": "manual",
    "retrieved_at": "2026-02-11T12:00:00Z"
  },
  "files": {
    "pdf_sha256": "abc123...",
    "pdf_bytes": 1500000
  }
}
```

---

## 2. ae.rule.v1 — Extracted Rule

**Purpose**: Describes a rule extracted from a paper.

**Required Fields**:
- `rule_id`, `paper_id`
- `rule_type`: "edge" | "cpd_hint" | "prior" | "constraint" | "interaction"
- `lhs`, `rhs`: Arrays of `{var, state}` objects
- `polarity`: "positive" | "negative" | "null" | "u_shaped" | "unknown"
- `strength`: Kind and optional value
- `applicability`: Population, setting, boundary conditions
- `evidence_links`: References to claims
- `bn_mapping`: Node suggestions, discretization hint
- `ae_confidence`: 0.0-1.0

**Example**:
```json
{
  "schema": "ae.rule.v1",
  "rule_id": "rule_001",
  "paper_id": "kaplan_1989_001",
  "rule_type": "edge",
  "lhs": [{"var": "nature_exposure", "state": "high"}],
  "rhs": [{"var": "attention_restoration", "state": "increased"}],
  "polarity": "positive",
  "strength": {"kind": "qualitative", "value": null},
  "applicability": {
    "population": [{"id": "general"}],
    "setting": [{"id": "outdoor"}],
    "boundary_conditions": []
  },
  "evidence_links": [{"claim_id": "claim_001"}],
  "bn_mapping": {
    "node_suggestions": ["nature_exposure", "attention"],
    "discretization_hint": "binary"
  },
  "ae_confidence": 0.75
}
```

---

## 3. ae.query_request.v1 — Query Input (NEW)

**Purpose**: Submit a natural language query to the Query Engine.

**Required Fields**:
- `query_id`: Unique identifier for tracking
- `query_text`: Natural language question (max 2000 chars)

**Optional Fields**:
- `response_mode`: Progressive disclosure level
  - `"headline"`: One-sentence answer
  - `"summary"`: Key evidence + confidence (default)
  - `"detail"`: Full trace with citations
  - `"deep_dive"`: Complete epistemology
- `query_type_hint`: Help parser (e.g., "what_is", "does_affect")
- `causal_level_hint`: Causal level (per Pearl)
- `subject_terms`, `outcome_terms`: Focus search
- `include_gaps`: Include gap analysis (default: false)
- `max_results`: Limit results (default: 10)
- `min_credence`: Credence threshold (default: 0.3)
- `context`: Population, setting, theory filter

**Example**:
```json
{
  "schema": "ae.query_request.v1",
  "query_id": "q_20260211_001",
  "query_text": "What is the effect of natural light on productivity?",
  "response_mode": "summary",
  "include_gaps": true,
  "max_results": 5,
  "context": {
    "population": "office workers",
    "setting": "indoor"
  }
}
```

---

## 4. ae.query_response.v1 — Query Output (NEW)

**Purpose**: Response from the Query Engine with progressive disclosure.

**Required Fields**:
- `query_id`: Matches request
- `status`: "success" | "partial" | "no_results" | "error" | "clarification_needed"
- `headline`: One-sentence answer (always provided)

**Progressive Disclosure** (per Simon):
1. **headline**: Always included — single sentence answer
2. **summary**: Key evidence, confidence, scope conditions, implications
3. **detail**: Full evidence list, theories, methodological notes
4. **deep_dive**: Constraint network, entrenchment scores, community credences

**Follow-ups** (per Simon): Exactly 3 types:
- `deeper`: More specific question
- `broader`: Related topic
- `uncertainty`: What we don't know

**Example**:
```json
{
  "schema": "ae.query_response.v1",
  "query_id": "q_20260211_001",
  "status": "success",
  "response_mode": "summary",
  "headline": "Natural light increases productivity by 5-15% (credence: 0.72 ± 0.15)",
  "summary": {
    "answer_confidence": 0.72,
    "answer_uncertainty": 0.15,
    "key_evidence": [
      {
        "belief_id": "b_light_prod_001",
        "content": "Daylight exposure improves task performance",
        "credence": 0.75,
        "source_depth": "full_text",
        "paper_ids": ["edwards_2002_001"],
        "is_causal": true,
        "needs_caution": false
      }
    ],
    "scope_conditions": {
      "population": "Office workers in temperate climates",
      "setting": "Indoor workplaces with window access"
    },
    "practical_implications": [
      "Maximize daylight in workspace design",
      "Consider light levels of 300-500 lux for desk work"
    ],
    "caveats": [
      "Most studies in Western populations",
      "Long-term effects less studied"
    ]
  },
  "follow_ups": [
    {
      "question": "What is the optimal light level for productivity?",
      "type": "deeper",
      "executable_query": "optimal light level productivity lux"
    },
    {
      "question": "What other environmental factors affect productivity?",
      "type": "broader",
      "executable_query": "environmental factors affect productivity"
    },
    {
      "question": "What don't we know about light and productivity?",
      "type": "uncertainty",
      "executable_query": "gaps light productivity research"
    }
  ],
  "metadata": {
    "processing_time_ms": 245,
    "n_beliefs_searched": 1250,
    "n_beliefs_matched": 23,
    "causal_level": "interventional",
    "query_type": "does_affect"
  }
}
```

---

## 5. ae.gap_report.v1 — Gap Report (NEW)

**Purpose**: Identify knowledge gaps and suggest research directions.

**Required Fields**:
- `report_id`: Unique identifier
- `generated_at`: ISO timestamp
- `summary`: Gap statistics
- `gaps`: List of identified gaps

**Gap Types**:
| Type | Description |
|------|-------------|
| `uncertain` | High uncertainty in existing beliefs |
| `unexplored` | Topic not covered by evidence |
| `missing_contrast` | Contrast class not specified (per van Fraassen) |
| `low_coverage` | Few beliefs in area |
| `theory_conflict` | Theories disagree |
| `baseline_unknown` | Missing baseline data |
| `blocked_beliefs` | Enabling conditions unmet (per Cartwright) |

**Example**:
```json
{
  "schema": "ae.gap_report.v1",
  "report_id": "gap_20260211_001",
  "generated_at": "2026-02-11T12:30:00Z",
  "context": {
    "topic": "biophilic design",
    "query_id": "q_20260211_001"
  },
  "summary": {
    "n_gaps": 7,
    "n_high_priority": 2,
    "coverage_score": 0.65,
    "gap_type_counts": {
      "uncertain": 2,
      "unexplored": 3,
      "missing_contrast": 2
    },
    "most_impacted_theories": ["ART", "SRT"]
  },
  "gaps": [
    {
      "gap_id": "gap_001",
      "gap_type": "unexplored",
      "description": "No evidence on biophilic design effects in healthcare settings",
      "priority": 0.85,
      "voi_score": 12.5,
      "affected_theories": ["SRT", "Biophilia"],
      "resolution_approach": "Search healthcare architecture literature",
      "evidence": {
        "source_type": "coverage_scan",
        "details": "Zero beliefs with tags [setting:healthcare, exposure:biophilic]"
      }
    }
  ],
  "suggested_searches": [
    {
      "search_id": "search_001",
      "query": "biophilic design hospital patient outcomes",
      "target_gaps": ["gap_001"],
      "expected_fill": 0.6,
      "search_domain": "PubMed",
      "vocabulary_expansions": ["healing gardens", "nature-based interventions"]
    }
  ]
}
```

---

## Integration Points

### MVP-1 → MVP-3 (Persistence → Query)
- MVP-1 saves `accumulated_web.json`
- MVP-3 loads it via `WebAccumulator.load()`

### MVP-0 → MVP-3 (Contracts → Query)
- MVP-3 implements `ae.query_request.v1` as input
- MVP-3 produces `ae.query_response.v1` as output
- MVP-3 produces `ae.gap_report.v1` when requested

### MVP-3 → MVP-GUI (Query → UI)
- Streamlit calls QueryEngine with `ae.query_request.v1`
- Streamlit renders `ae.query_response.v1` progressively
- Gaps page displays `ae.gap_report.v1` as heatmap

---

## Validation

Schemas can be validated with any JSON Schema validator:

```python
import jsonschema
import json

with open('contracts/ae_af/schemas/ae.query_request.v1.schema.json') as f:
    schema = json.load(f)

request = {
    "schema": "ae.query_request.v1",
    "query_id": "test_001",
    "query_text": "What affects attention?"
}

jsonschema.validate(request, schema)  # Raises if invalid
```

---

## Changelog

| Date | Change |
|------|--------|
| 2026-02-11 | MVP-0: Created query_request, query_response, gap_report schemas |
| 2026-02-11 | Verified existing ae.paper.v1 and ae.rule.v1 schemas |
