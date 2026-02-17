# Corpus Quality Assessment Report
**Date**: 2026-02-16
**Status**: CRITICAL FINDING

## Executive Summary
The user's suspicion is confirmed. The current "Tables" (Panel extractions) in the production database are **100% provisional and abstract-derived**. There are **zero** high-quality, PDF-verified tables in the current `realtime_tables.jsonl` dataset.

## 1. Population Statistics
*   **Total Papers in Article Finder**: 16,073
*   **Papers with PDFs**: 1,111 (6.9%)
*   **Papers with Extracted Tables**: 595 (3.7%)

## 2. Quality Breakdown
Of the 595 papers with extracted tables:

| Metric | Count | Percentage |
| :--- | :--- | :--- |
| **Total extracted tables** | 595 | 100% |
| **Abstract-derived (Provisional)** | 595 | **100%** |
| **PDF-derived (Confirmed)** | 0 | **0%** |
| **Requires PDF Confirmation** | 595 | 100% |

## 3. Detailed Findings
*   **Source**: Analysis of `data/production/realtime_tables.jsonl`.
*   **Evidence Level**: All entries are marked as `"evidence_level": "abstract_only_reduced_table"`.
*   **Provenance**: All entries are marked as `"provenance_tier": "abstract_provisional"`.
*   **PDF Status**: Even papers that *have* PDFs (e.g., `ZHKHNN33`, `HUMANNESS AND ARCHITECTURE`) are processed only at the abstract level in this log, likely because the "Full PDF Extraction" pipeline has not been run or merged.

## 4. Conclusion
The current "Knowledge Base" of extracted findings is essentially a collection of abstract-based stubs. To improve quality, we must:
1.  **Activate PDF Extraction**: The pipeline exists but seemingly hasn't been run on the 1,111 PDFs.
2.  **Reprocess**: Run the full extraction flow on the `pdfs/` directory.

---

## Addendum (2026-02-16, 15:xx local)
This report's "0 PDF-derived" finding is accurate for `data/production/realtime_tables.jsonl` specifically, but **does not reflect** the separate PDF-confirmed artifact stream.

Current production state:
- `data/production/realtime_pdf_confirmed_rows.csv`: **184,091 rows**
  - `pdf_table_extracted`: **28,573**
  - `pdf_discourse_extracted`: **155,518**
- Queue status in `data/production/realtime_pdf_completion_queue.csv`:
  - `completed_pdf_extracted`: **355 papers**
  - `completed_pdf_no_claims`: **157 papers**
  - `error_pdf_processing`: **3 papers**
  - `queued_pdf_backfill`: **518 papers** (pending)

Interpretation:
- PDF extraction is real and already populated in production (`realtime_pdf_confirmed_rows.csv`).
- The "0 processed" readout occurs when only `realtime_tables.jsonl` (abstract-provisional stream) is inspected.
