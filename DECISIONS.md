# Engineering Decisions

## 2026-02-17 — Sprint 10 Task 2.2 (CMR Data Models)

- The sprint text says "Alembic migration", but this repository currently uses
  SQL file migrations under `migrations/` and does not have an Alembic setup.
- Decision: implement migration as `migrations/021_add_cmr_models.sql` to stay
  consistent with existing migration infrastructure and runtime patterns.

## 2026-02-18 — Sprint D Task D.4 (Full CSV Audit)

- Audit of `realtime_pdf_confirmed_rows.csv` confirms significant data quality issues.
- Only ~7% of rows contain structured table data (`codex_pdfplumber`).
- ~4% of rows have identical Environment/Outcome variable strings (major parsing artifacts).
- Paper coverage is incomplete; 154 papers have zero extracted tables.
- Remediation strategy (Sprint D) confirmed as necessary.
