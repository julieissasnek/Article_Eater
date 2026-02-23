# VOI Discovery & PDF Retrieval Infrastructure Tasks

**Added**: 2026-02-11
**Priority**: P0 (Blocking DISC-3 through DISC-9)
**Context**: Assessment of 2026-02-11 revealed that while VOI gap detection is 95% complete, the infrastructure to actually find and retrieve papers is critically incomplete. The system can identify what it needs but cannot acquire it.

**TO BE MERGED INTO TASKS.md**

---

## Problem Statement

1. **VOI search generates queries but doesn't execute them** — `voi_search.py` (1880 lines) identifies gaps and generates search terms, but no orchestrator calls external APIs
2. **Only Semantic Scholar stub exists** — 31 lines of code, no relevance scoring, deduplication, or multi-source coordination
3. **Zero PDF retrieval methods implemented** — Discovery funnel defines 6 methods (DIRECT_LINK, UNPAYWALL, SCIHUB, LIBRARY, AUTHOR_REQUEST, MANUAL) but none are coded
4. **Zotero is filesystem-only** — Can list PDFs in `~/Zotero/storage` but cannot query `zotero.sqlite` for metadata (titles, DOIs, tags)
5. **PDF sectioning is fragile** — Regex-based heuristics fail on non-standard paper formats

---

## Current State Summary

| Component | Lines of Code | Completeness | Notes |
|-----------|---------------|--------------|-------|
| Gap Detection (`voi_search.py`) | 1880 | 95% | Works well |
| Query Generation | ~200 | 85% | Cross-field vocab expansion done |
| Search Execution | 0 | 0% | **MISSING** |
| Semantic Scholar API | 31 | 10% | Stub only |
| PubMed/ERIC/CrossRef APIs | 0 | 0% | **NOT STARTED** |
| Unpaywall Integration | 0 | 0% | **NOT STARTED** |
| Sci-Hub Integration | 0 | 0% | **NOT STARTED** |
| Library Proxy Support | 0 | 0% | **NOT STARTED** |
| Zotero Metadata Access | 0 | 0% | **NOT STARTED** |
| PDF Sectioning | ~100 | 40% | Fragile regex |

---

## Tasks

| ID | Task | Description | Priority | Dependencies |
|----|------|-------------|----------|--------------|
| INFRA-1 | Implement VOI search executor | Orchestrator that takes gap → queries → calls APIs → returns ranked results | P0 | — |
| INFRA-2 | Extend Semantic Scholar integration | Add relevance scoring, deduplication, pagination, rate limiting | P1 | INFRA-1 |
| INFRA-3 | Add Unpaywall API integration | DOI → open access PDF URL resolution | P1 | — |
| INFRA-4 | Add CrossRef API integration | DOI validation, metadata enrichment, reference extraction | P2 | — |
| INFRA-5 | Add PubMed API integration | Biomedical literature search via E-utilities | P2 | INFRA-1 |
| INFRA-6 | Add ERIC API integration | Education literature search | P3 | INFRA-1 |
| INFRA-7 | Implement PDF direct download | Fetch PDFs from publisher URLs, handle redirects | P1 | — |
| INFRA-8 | Implement Unpaywall PDF retrieval | Use INFRA-3 to get OA links, download PDFs | P1 | INFRA-3 |
| INFRA-9 | Implement library proxy support | Route requests through institutional proxy (CalTech, etc.) | P2 | — |
| INFRA-10 | Add Zotero database access | Query `zotero.sqlite` for metadata (DOIs, titles, tags, collections) | P1 | — |
| INFRA-11 | Add Zotero sync capability | Bi-directional: import Zotero metadata, export AE findings | P3 | INFRA-10 |
| INFRA-12 | Improve PDF sectioning | Replace regex with SciSpacy or BERT-based section classification | P2 | — |
| INFRA-13 | Add OCR support | Handle scanned/image-based PDFs via Tesseract or similar | P3 | — |
| INFRA-14 | Multi-source search coordinator | Parallel queries across sources, deduplication, relevance fusion | P1 | INFRA-1, INFRA-2, INFRA-5 |
| INFRA-15 | Citation network traversal | Given paper, find citing/cited papers for gap closure | P2 | INFRA-2, INFRA-4 |

---

## Implementation Order (Recommended)

**Phase 1: Core Search (Unblocks DISC-3)**
1. INFRA-1 (VOI search executor)
2. INFRA-2 (Semantic Scholar extension)
3. INFRA-14 (Multi-source coordinator - basic version)

**Phase 2: PDF Acquisition (Unblocks DISC-4)**
4. INFRA-3 (Unpaywall API)
5. INFRA-7 (Direct download)
6. INFRA-8 (Unpaywall retrieval)
7. INFRA-10 (Zotero database access)

**Phase 3: Extended Sources**
8. INFRA-4 (CrossRef)
9. INFRA-5 (PubMed)
10. INFRA-9 (Library proxy)

**Phase 4: Quality Improvements**
11. INFRA-12 (Better PDF sectioning)
12. INFRA-15 (Citation traversal)
13. INFRA-6 (ERIC)
14. INFRA-11 (Zotero sync)
15. INFRA-13 (OCR)

---

## API Keys & Configuration Required

| Service | Env Variable | Status |
|---------|--------------|--------|
| Semantic Scholar | `SEMANTIC_SCHOLAR_API_KEY` | ✓ Configured |
| Unpaywall | `UNPAYWALL_EMAIL` | ☐ Need to add |
| CrossRef | `CROSSREF_MAILTO` | ☐ Need to add (polite pool) |
| PubMed | `NCBI_API_KEY` | ☐ Optional (higher rate limits) |
| ERIC | — | ☐ Free, no key needed |

---

## Panel Consultation Recommended

For INFRA-1 and INFRA-14 (search orchestration), consult:
- **Bates** (berrypicking, information foraging)
- **Simon** (satisficing, bounded rationality in search)
- **Pearl** (relevance as causal contribution to gap closure)
- **Cartwright** (source reliability, evidence quality)
