# P8.5 Zotero -> BibTeX -> Extraction E2E Verification

**Date**: 2026-02-17  
**Task**: P8.5 (Sprint 8 — Pipeline Reliability Hardening)  
**Author**: Codex

## Objective

Verify and document end-to-end path from Zotero/BibTeX intake into extraction pipeline outputs.

## Verified Flow

### A) BibTeX parsing and matching layer

Validated through tests:
- `tests/test_bibtex_utils.py`
- `tests/test_bibtex_ingestion.py`
- `tests/test_bibtex_e2e_flow.py` (new integration test)

Command:
```bash
./venv/bin/pytest -q tests/test_bibtex_e2e_flow.py tests/test_bibtex_ingestion.py tests/test_bibtex_utils.py
```

Result:
- `57 passed`

What this covers:
1. Parse BibTeX into structured entries.
2. Match PDFs to entries (`PDFBibTeXMatcher`) via DOI/text strategies.
3. Build ingestion payloads and input bundles.
4. Execute ingestion service batch flow into pipeline boundary (pipeline call mocked in tests, as intended for deterministic E2E contract testing).

### B) UI/entrypoint confirmation

Confirmed relevant entrypoints exist and remain wired:
- Streamlit BibTeX wizard: `streamlit_app/pages/1_bibtex_import.py`
- Ingestion service: `src/services/bibtex_ingestion.py`
- Realtime extraction intake: `scripts/run_realtime_table_rule_intake.py`
- PDF completion extraction: `scripts/process_realtime_pdf_completion_queue.py`

### C) Runtime smoke note

Attempted `scripts/offline_pipeline_smoke.py`, blocked by missing local dependency:
- `ModuleNotFoundError: jsonschema`

This does not invalidate BibTeX ingestion E2E contract tests above, but full offline smoke requires dependency installation in the runtime environment.

## Conclusion

P8.5 acceptance target (document + verify workflow) is satisfied with executable test evidence for BibTeX->matching->ingestion boundary and concrete runtime path documentation for downstream extraction scripts.

