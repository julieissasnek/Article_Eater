# Health and Maintenance Infrastructure Update

**Date:** February 23, 2026
**Author:** Claude Code
**Version:** 1.0

---

## Executive Summary

This document describes the health monitoring and maintenance infrastructure added to Article Eater. The system now has three layers of operational observability:

1. **Runtime Health Endpoints** — Continuous monitoring via HTTP
2. **Periodic Maintenance Script** — Scheduled housekeeping tasks
3. **Data Quality Audits** — On-demand analysis of belief network health

Additionally, supporting infrastructure was added:
- Pinned dependencies for reproducible builds
- Test coverage tracking
- Database migration system
- Centralized error types
- Structured logging

---

## 1. What Was Implemented

### 1.1 Health Check Endpoints (`app/routes/health.py`)

HTTP endpoints for runtime monitoring, compatible with load balancers, Kubernetes, and monitoring systems.

| Endpoint | Purpose | Response Time |
|----------|---------|---------------|
| `GET /health` | Basic liveness | <1ms |
| `GET /health/live` | Process alive check | <1ms |
| `GET /health/ready` | Full subsystem validation | ~50ms |

#### Subsystems Checked by `/health/ready`

| Subsystem | What It Checks | Status Levels |
|-----------|----------------|---------------|
| `database` | ae.db connectivity | ok / unhealthy |
| `web_persistence` | Main belief store, belief count | ok / degraded / unhealthy |
| `templates` | Template directory, count, calibration | ok / unhealthy |
| `schemas` | Schema directory existence | ok / degraded |
| `migrations` | Pending database migrations | ok / degraded |
| `environment` | Required env vars (GOOGLE_API_KEY) | ok / degraded |
| `disk` | Free disk space percentage | ok / degraded / unhealthy |

#### Example Response

```json
{
  "status": "degraded",
  "timestamp": "2026-02-23T17:45:00Z",
  "subsystems": [
    {"name": "database", "status": "ok", "latency_ms": 2.1},
    {"name": "web_persistence", "status": "ok", "details": {"beliefs": 4888}},
    {"name": "migrations", "status": "degraded", "details": {"pending": 4}},
    {"name": "disk", "status": "degraded", "details": {"free_percent": 9.4}}
  ],
  "checks_passed": 5,
  "checks_failed": 0
}
```

---

### 1.2 Maintenance Script (`scripts/maintenance.py`)

Periodic housekeeping tasks for database health and cleanup.

```bash
# Check what would be done (safe, no changes)
python scripts/maintenance.py --check

# Run all maintenance tasks
python scripts/maintenance.py

# Run specific task
python scripts/maintenance.py --task db        # Migrations only
python scripts/maintenance.py --task integrity # DB integrity check
python scripts/maintenance.py --task cache     # Clean old cache
python scripts/maintenance.py --task temp      # Clean temp files
```

#### Tasks

| Task | What It Does | When to Run |
|------|--------------|-------------|
| `db` | Run pending migrations | Before deployments |
| `integrity` | SQLite PRAGMA integrity_check | After crashes, weekly |
| `cache` | Remove cache files >7 days old | Weekly |
| `temp` | Remove *.bak, *.tmp, *.swp files | Weekly |

---

### 1.3 Database Migration System (`src/services/db_migrations.py`)

Lightweight migration tracking for SQLite databases.

```python
from src.services.db_migrations import MigrationManager, check_migration_status

# Check status
status = check_migration_status("data/web_persistence.db")
print(status)  # {'current_version': 4, 'pending_count': 0, ...}

# Run migrations
conn = sqlite3.connect("data/web_persistence.db")
mgr = MigrationManager(conn)
mgr.run_pending_migrations()
```

#### Adding New Migrations

```python
# In src/services/db_migrations.py

@migration(5)
def _m005_add_new_column(cursor: sqlite3.Cursor) -> None:
    """Add foo column to beliefs table."""
    cursor.execute("ALTER TABLE beliefs ADD COLUMN foo TEXT")
```

Migrations are:
- **Versioned** — Integer version numbers, run in order
- **Tracked** — Applied migrations recorded in `_schema_migrations` table
- **Idempotent** — Safe to run multiple times (use IF NOT EXISTS)

---

### 1.4 Centralized Error Types (`src/core/errors.py`)

Domain-specific exceptions replacing generic ValueError/RuntimeError.

```python
from src.core import BeliefNotFoundError, ValidationError, LLMError

# Instead of: raise ValueError("Belief not found: b123")
raise BeliefNotFoundError("b123")

# Catchable by type
try:
    belief = web.get_belief(belief_id)
except BeliefNotFoundError:
    # Handle missing belief specifically
    pass
```

#### Exception Hierarchy

```
ArticleEaterError (base)
├── EntityNotFoundError
│   ├── BeliefNotFoundError
│   ├── TheoryNotFoundError
│   ├── BridgeNotFoundError
│   ├── PaperNotFoundError
│   └── TemplateNotFoundError
├── ValidationError
│   ├── SchemaValidationError
│   ├── ConstraintViolationError
│   └── InvalidParameterError
├── ProcessingError
│   ├── ExtractionError
│   ├── LLMError
│   └── ParsingError
├── ConfigurationError
│   ├── MissingConfigError
│   └── InvalidConfigError
├── DatabaseError
│   ├── MigrationError
│   └── IntegrityError
└── EpistemicError
    ├── CoherenceError
    └── CircularDependencyError
```

---

### 1.5 Structured Logging (`src/core/logging.py`)

JSON-structured logging for production, human-readable for development.

```python
from src.core import get_logger, configure_logging

# Configure at startup
configure_logging(json_logs=True, log_level="INFO")  # Production
configure_logging(json_logs=False, log_level="DEBUG")  # Development

# Use in modules
logger = get_logger(__name__)
logger.info("processing_paper", paper_id="p123", pages=42)
logger.warning("low_coherence", belief_id="b456", score=0.3)
logger.error("extraction_failed", paper_id="p789", error="timeout")
```

#### Output Formats

**Development (console):**
```
2026-02-23T09:45:12Z [info] processing_paper  paper_id=p123 pages=42
```

**Production (JSON):**
```json
{"event": "processing_paper", "paper_id": "p123", "pages": 42, "timestamp": "2026-02-23T09:45:12Z", "level": "info"}
```

---

### 1.6 Dependency Pinning

Reproducible builds with pip-compile.

```bash
# Top-level dependencies (edit these)
requirements.in          # Production dependencies
requirements-dev.in      # Development dependencies

# Pinned versions (auto-generated, commit these)
requirements.txt         # pip-compile requirements.in
requirements-dev.txt     # pip-compile requirements-dev.in

# Regenerate after editing .in files
pip-compile requirements.in -o requirements.txt
pip-compile requirements-dev.in -o requirements-dev.txt
```

---

### 1.7 Test Coverage (`pyproject.toml`, CI)

Coverage tracking with pytest-cov.

```bash
# Run tests with coverage
pytest --cov=src --cov=app --cov-report=term-missing

# Generate HTML report
pytest --cov=src --cov=app --cov-report=html
open htmlcov/index.html
```

CI automatically uploads coverage to Codecov on push.

---

## 2. Current System Status

As of February 23, 2026:

| Check | Status | Details |
|-------|--------|---------|
| Database (ae.db) | OK | Connectable |
| Web Persistence | OK | 4,888 beliefs |
| Templates | OK | 166 total, 55 calibrated |
| Schemas | OK | 15 schemas |
| Migrations | **DEGRADED** | 4 pending |
| Environment | **DEGRADED** | GOOGLE_API_KEY not set |
| Disk Space | **DEGRADED** | 9.4% free (86 GB) |

### Immediate Actions Needed

```bash
# 1. Run pending migrations
python scripts/maintenance.py --task db

# 2. Check what's using disk space
du -sh */ | sort -hr | head -10

# 3. Ensure .env has GOOGLE_API_KEY before running LLM operations
```

---

## 3. Best Practices Assessment

### What We Have (Industry Standard)

| Practice | Status | Notes |
|----------|--------|-------|
| Health endpoints (liveness/readiness) | ✅ Done | K8s compatible |
| Dependency pinning | ✅ Done | pip-compile |
| Database migrations | ✅ Done | Version tracked |
| Structured logging | ✅ Done | JSON + console |
| CI pipeline | ✅ Done | GitHub Actions |
| Pre-commit hooks | ✅ Done | Ruff, isort, template validation |
| Centralized errors | ✅ Done | Domain-specific hierarchy |
| Test coverage tracking | ✅ Done | pytest-cov + Codecov |

### What's Missing (Recommended Additions)

| Practice | Priority | Effort | Recommendation |
|----------|----------|--------|----------------|
| **Alerting** | High | Medium | Integrate with PagerDuty/Slack when health degrades |
| **Metrics (Prometheus)** | High | Low | Already have prometheus_client, expose /metrics |
| **Log aggregation** | Medium | Medium | Ship logs to Loki/CloudWatch/Datadog |
| **Backup automation** | High | Low | Cron job for SQLite backups |
| **Secret management** | Medium | Medium | Use AWS Secrets Manager or similar |
| **Rate limiting** | Medium | Low | Add to FastAPI for API protection |
| **Request tracing** | Medium | Medium | Add request IDs, OpenTelemetry |
| **Load testing** | Low | Medium | Locust or k6 for capacity planning |
| **Chaos testing** | Low | High | Test failure scenarios |

### Recommended Next Steps (Priority Order)

1. **Run pending migrations** — Immediate
   ```bash
   python scripts/maintenance.py --task db
   ```

2. **Free up disk space** — Immediate (9.4% is concerning)
   ```bash
   # Find large files
   find . -size +100M -type f 2>/dev/null
   # Clean up old backups in data/
   python scripts/maintenance.py --task temp
   ```

3. **Add /metrics endpoint** — Low effort, high value
   ```python
   # Already have prometheus_client installed
   from prometheus_client import make_asgi_app
   metrics_app = make_asgi_app()
   app.mount("/metrics", metrics_app)
   ```

4. **Automate SQLite backups** — Critical for data safety
   ```bash
   # Add to crontab
   0 2 * * * sqlite3 data/web_persistence.db ".backup data/backups/web_$(date +\%Y\%m\%d).db"
   ```

5. **Set up alerting** — When health endpoint returns degraded/unhealthy

---

## 4. Operational Runbook

### Daily Operations

No daily tasks required. Health endpoints run automatically.

### Weekly Operations

```bash
# Run full maintenance
python scripts/maintenance.py

# Check for any degraded status
curl -s http://localhost:8000/health/ready | jq '.subsystems[] | select(.status != "ok")'
```

### Before Each Deployment

```bash
# 1. Run migrations
python scripts/maintenance.py --task db

# 2. Verify health
curl http://localhost:8000/health/ready

# 3. Run tests
pytest tests/ -q
```

### After Data Imports/Changes

```bash
# Run data quality audit
python scripts/analyze_web_health.py
```

### After System Issues

```bash
# Check database integrity
python scripts/maintenance.py --task integrity

# Review logs
tail -100 logs/app.log | grep -E "error|warning"
```

---

## 5. File Reference

| File | Purpose |
|------|---------|
| `app/routes/health.py` | HTTP health endpoints |
| `scripts/maintenance.py` | Periodic maintenance tasks |
| `scripts/analyze_web_health.py` | Data quality audit |
| `src/services/db_migrations.py` | Migration system |
| `src/core/errors.py` | Exception hierarchy |
| `src/core/logging.py` | Structured logging |
| `src/config/validate.py` | Startup validation |
| `requirements.in` | Top-level dependencies |
| `requirements-dev.in` | Dev dependencies |
| `pyproject.toml` | Tool configs (pytest, coverage, mypy, ruff) |
| `.pre-commit-config.yaml` | Pre-commit hooks |
| `.github/workflows/ci.yml` | CI pipeline |

---

## 6. Commits

| Commit | Description |
|--------|-------------|
| `ecfc9d8` | Fix missing ConstraintType import |
| `242578f` | Add infrastructure (migrations, errors, logging, maintenance) |
| `b380bb2` | Expand health checks (migrations, env, disk, web_persistence) |

---

## Appendix: Health Check Integration Examples

### Kubernetes Probes

```yaml
livenessProbe:
  httpGet:
    path: /health/live
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /health/ready
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 30
```

### Docker Healthcheck

```dockerfile
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1
```

### Monitoring with curl

```bash
# Simple check
curl -sf http://localhost:8000/health && echo "OK" || echo "FAIL"

# Detailed check with jq
curl -s http://localhost:8000/health/ready | jq '.'

# Alert on degraded
STATUS=$(curl -s http://localhost:8000/health/ready | jq -r '.status')
[ "$STATUS" != "ok" ] && echo "ALERT: System status is $STATUS"
```
