# TODO: Import-Time PDFPlumber Preprocess (Deferred)

Date: 2026-02-14
Status: Partially implemented (runtime queue preprocess enabled)
Priority: High

## Goal
Add a `pdfplumber` preprocess stage during import, before table/rule extraction.

## Current state
Implemented in runtime pipeline:
- `scripts/preprocess_pdf_queue.py` performs parallel preprocess on queued PDFs.
- Queue metadata now includes preprocess diagnostics (`preprocess_status`, page/text/cid metrics, cache path).
- Realtime worker can run preprocess before extraction and prioritize `ready` PDFs.

Still pending:
- true import-time preprocessing at ingest insertion point (before queue entry creation).

## Why
Current extraction can stall on malformed/complex PDFs. Import-time preprocess will front-load parse diagnostics and reduce runtime stalls during table generation.

## Required scope
1. Run `pdfplumber` at import and persist page-level extraction cache.
2. Persist parse diagnostics (warnings/errors) per PDF.
3. Record quality signals (parse completeness, table-detection confidence, text density).
4. Mark problematic PDFs into a quarantine/deferred lane for slower retry.
5. Expose preprocess status in queue metadata so extraction scheduler can prioritize good PDFs first.

## Integration points
- Article ingest/import pipeline
- `realtime_pdf_completion_queue.csv` status model
- extraction quality gates and manual review queue

## Exit criteria
- New PDFs receive preprocess metadata before entering extraction queue.
- Scheduler can route likely-good vs problematic PDFs.
- End-to-end extraction throughput improves and stall rate drops.
