# Article Finder ↔ Article Eater Contract Pack (v2)

**Updated**: 2026-02-11
**Version**: 2.0 (added canonical data source, quality selection)

This pack defines the canonical file-bundle contract between **Article Finder (AF)** and **Article Eater (AE)**.

---

## Canonical Data Source

### Article Finder Database (NORMATIVE)

The **single source of truth** for papers is the Article Finder database:

```
/Users/davidusa/REPOS/Article_Finder_v3_2_3/data/article_finder.db
```

| Table | Purpose |
|-------|---------|
| `papers` | All paper metadata, abstracts, PDF paths, triage scores |
| `claims` | Extracted claims (populated by AE) |
| `rules` | Synthesized rules (populated by AE) |
| `extracted_tables` | Tables extracted from PDFs |
| `citations` | Citation relationships |
| `facets` | Topic taxonomy |

### Current Statistics (as of 2026-02-11)

| Metric | Count |
|--------|-------|
| Total papers | 16,073 |
| With abstracts | 11,957 |
| With PDFs | 1,111 |
| Triaged "send_to_eater" | 73 |

---

## Paper Selection Criteria

### Quality Markers (papers table columns)

| Column | Type | Description |
|--------|------|-------------|
| `triage_score` | REAL | Relevance score (0-1) |
| `triage_decision` | TEXT | `send_to_eater` \| `review` \| `reject` |
| `topic_decision` | TEXT | `on_topic` \| `off_topic` |
| `topic_score` | REAL | Topic relevance score |
| `off_topic_flag` | INTEGER | 1 if manually flagged off-topic |

### Selection Query (recommended)

```sql
-- Select "good" papers ready for extraction
SELECT paper_id, title, abstract, pdf_path
FROM papers
WHERE triage_decision = 'send_to_eater'
  AND topic_decision = 'on_topic'
  AND off_topic_flag = 0
  AND abstract IS NOT NULL
  AND LENGTH(abstract) > 200
ORDER BY triage_score DESC;
```

### Stratified Sampling (for balanced topic coverage)

```sql
-- Equal representation across CNfA domains
WITH ranked AS (
  SELECT *,
    ROW_NUMBER() OVER (PARTITION BY topic_category ORDER BY triage_score DESC) as rn
  FROM papers
  WHERE triage_decision = 'send_to_eater'
    AND topic_decision = 'on_topic'
)
SELECT * FROM ranked WHERE rn <= 10;  -- 10 per topic
```

---

## Design Goals

- **Stable interface**: AF depends on files + schemas, not AE internals.
- **Idempotent**: Dedupe via `paper_id` + `pdf_sha256`.
- **HITL-capable**: AE can request review without breaking automation.
- **BN-ready**: AE emits normalized claims + Bayesian rule candidates.
- **Real data only**: No synthetic/fake articles in production pipelines.

---

## Invocation (normative)

AE MUST support a CLI that consumes an input bundle directory and writes an output bundle directory:

```bash
article_eater eat --in <JOB_IN_DIR> --out <JOB_OUT_DIR> --profile deep --hitl auto
```

AF SHOULD treat AE as a black box, and only read `result.json` plus referenced artifacts.

---

## Bundle Structure (normative)

### Input Bundle (AF → AE)

**Required**:
- `paper.pdf` — The PDF file
- `paper.json` — Paper metadata (schema: `schemas/ae.paper.v1.schema.json`)

**Optional**:
- `abstract.txt` — Pre-extracted abstract
- `fulltext.txt` — Pre-extracted full text
- `citations.json` — Citation list
- `figures/` — Extracted figures
- `tables/` — Extracted tables
- `overrides.json` — HITL overrides

### Output Bundle (AE → AF)

**Required**:
- `result.json` — Processing result (schema: `schemas/ae.result.v1.schema.json`)
- `claims.jsonl` — Extracted claims (schema: `schemas/ae.claim.v2.schema.json`)
- `rules.jsonl` — Synthesized rules (schema: `schemas/ae.rule.v2.schema.json`)
- `provenance.json` — Extraction provenance (schema: `schemas/ae.provenance.v1.schema.json`)
- `audit.log.jsonl` — Audit events (schema: `schemas/ae.audit_event.v1.schema.json`)

**Optional**:
- `review_items.jsonl` — Items needing human review
- `fulltext.extracted.txt` — Extracted text
- `tables/`, `figures/` — Extracted artifacts
- `web_state.json` — Web of belief state
- `article_essence.json` — Structured extraction output

---

## Extraction Templates

AE supports multiple extraction templates based on article type:

| Template | Article Type |
|----------|--------------|
| `EMPIRICAL` | Experimental studies, RCTs |
| `META_ANALYSIS` | Statistical meta-analyses |
| `SYSTEMATIC_REVIEW` | Systematic literature reviews |
| `THEORETICAL` | Theory development papers |
| `CONCEPTUAL_FRAMEWORK` | Framework papers |
| `CASE_STUDY` | Case study research |
| `ETHNOGRAPHIC` | Ethnographic studies |
| `GROUNDED_THEORY` | Grounded theory studies |
| `INTERVIEW_STUDY` | Interview-based research |
| `MIXED_METHODS` | Mixed methods studies |
| `PHENOMENOLOGICAL` | Phenomenological research |
| `NARRATIVE_REVIEW` | Narrative reviews |
| `OBSERVATIONAL_FIELD` | Field observations |
| `THOUGHT_PIECE` | Commentary, opinion |

See `docs/EXTRACTION_TEMPLATE_*.md` for template specifications.

---

## Status Mapping (recommended)

AE status (`result.json.status`) → AF corpus status:

| AE Status | AF Status |
|-----------|-----------|
| `SUCCESS` | `processed_success` |
| `PARTIAL_SUCCESS` | `processed_partial` |
| `FAIL` | `processed_fail` |
| `NEEDS_REVIEW` | `needs_human_review` |

---

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      ARTICLE FINDER (AF)                         │
│  article_finder.db                                               │
│  ├── papers (16,073 records)                                     │
│  │   ├── paper_id, title, abstract, pdf_path                     │
│  │   ├── triage_score, triage_decision                           │
│  │   └── topic_decision, topic_category                          │
│  ├── extracted_tables (0 records - pending)                      │
│  └── claims, rules (populated by AE)                             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ SELECT papers WHERE triage_decision='send_to_eater'
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      JOB BUNDLE (AF → AE)                        │
│  /path/to/job_bundles/{paper_id}/                                │
│  ├── paper.pdf                                                   │
│  ├── paper.json                                                  │
│  └── abstract.txt (optional)                                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ article_eater eat --in ... --out ...
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      ARTICLE EATER (AE)                          │
│  Article Essence Extraction                                      │
│  ├── Template selection based on article type                    │
│  ├── LLM-based extraction                                        │
│  ├── Web of Belief integration                                   │
│  └── Rule synthesis                                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ Output bundle
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      OUTPUT BUNDLE (AE → AF)                     │
│  /path/to/output/{paper_id}/                                     │
│  ├── result.json                                                 │
│  ├── claims.jsonl                                                │
│  ├── rules.jsonl                                                 │
│  ├── web_state.json                                              │
│  └── article_essence.json                                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ Update AF database
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      AF DATABASE UPDATE                          │
│  UPDATE papers SET ae_status='SUCCESS', ae_n_claims=N, ...       │
│  INSERT INTO claims SELECT * FROM claims.jsonl                   │
│  INSERT INTO rules SELECT * FROM rules.jsonl                     │
└─────────────────────────────────────────────────────────────────┘
```

---

## Versioning

Each schema has a `schema_id` (e.g., `ae.paper.v1`). Bump versions only with backwards-compatible care.

| Schema | Current Version | Description |
|--------|-----------------|-------------|
| `ae.paper` | v1 | Paper metadata |
| `ae.claim` | v2 | Extracted claims |
| `ae.rule` | v2 | Synthesized rules |
| `ae.result` | v1 | Processing result |
| `ae.web_state` | v1 | Web of belief state |

---

## Revision History

| Date | Version | Changes |
|------|---------|---------|
| 2026-02-11 | v2.0 | Added canonical data source, quality selection, extraction templates |
| 2026-01-10 | v1.0 | Initial contract |
