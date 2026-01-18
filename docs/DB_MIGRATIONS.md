# Article Eater Database Schema and Migrations

Article Eater uses a relational schema (SQLite by default) alongside a
JSONL-based graph store. The SQL schema files live in `db/sql/` and are
referenced by tests such as `tests/test_relational_analysis.py`.

## 1. Schema Files

The key SQL files are:

- `010_rules_core.sql` / `015_core_tables.sql` / `015_complete_schema.sql`:
  core tables for papers, findings, rules, and related entities.
- `015b_findings_ci_patch.sql`:
  adds confidence interval fields (`ci_lower`, `ci_upper`) to findings.
- `016_rule_interactions.sql`:
  introduces the `rule_interactions` table used for relational conflict
  analysis (see `tests/test_relational_analysis.py`).
- `014_security.sql`:
  defines tables required for security/auth modules.

## 2. Initializing a Fresh SQLite Database

For lab/teaching usage, a typical one-time initialization looks like:

```bash
sqlite3 article_eater.db < db/sql/015_complete_schema.sql
sqlite3 article_eater.db < db/sql/015b_findings_ci_patch.sql
sqlite3 article_eater.db < db/sql/016_rule_interactions.sql
sqlite3 article_eater.db < db/sql/014_security.sql
```

Consult the release notes for the exact sequence if additional migration
files are added in future versions.

## 3. Relational Conflict Analysis

- `tests/test_relational_analysis.py` demonstrates how conflicting
  findings (with overlapping CIs) are detected and materialized as
  rows in `rule_interactions`.
- That test builds a temporary SQLite DB, applies the schema, inserts
  sample findings, and verifies that `analyze_conflicts` writes the
  expected interaction row.

## 4. Migration Strategy

For now, migrations are maintained as versioned SQL files. For more
complex or multi-environment deployments, you can:

- Wrap these SQL scripts into a simple migration runner (e.g., Alembic),
  or
- Use a dedicated `migrations/` directory and maintain a linear history
  of schema changes, each applied exactly once.

This document captures the current manual process and gives new
operators a clear starting point for automating DB migrations.
