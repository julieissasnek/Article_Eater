# Engineering Decisions

## 2026-02-17 — Sprint 10 Task 2.2 (CMR Data Models)

- The sprint text says "Alembic migration", but this repository currently uses
  SQL file migrations under `migrations/` and does not have an Alembic setup.
- Decision: implement migration as `migrations/021_add_cmr_models.sql` to stay
  consistent with existing migration infrastructure and runtime patterns.
