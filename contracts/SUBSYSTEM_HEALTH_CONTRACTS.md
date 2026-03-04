# Subsystem Health Contract Specification

**Date**: 2026-03-03
**Version**: 1.0
**Author**: CW (Claude Worker)
**System**: ATLAS (Automated Theory & Belief Learning Acquisition System)

---

## Purpose

This specification defines entry contracts, exit contracts, health invariants, and cross-boundary data contracts for the 20 ATLAS subsystems. These contracts are machine-checkable conditions that the OVERSEER system runs during POST_INTEGRATION checks (~5s) and nightly PERIODIC audits (~15 min).

A subsystem is:
- **GREEN** ✅ if all invariants hold
- **YELLOW** ⚠️ if warnings fire (degraded performance, threshold approaches)
- **RED** ❌ if any critical invariant fails (system integrity compromised)

---

## Contract Structure

For each subsystem, this specification includes:

### Entry Contract
What must be true before this subsystem can operate:
- Configuration and schema requirements
- Data dependencies from other subsystems
- Upstream subsystem health prerequisites

### Exit Contract
What must be true after this subsystem completes one unit of work:
- Data quality standards
- State consistency
- Downstream subsystem prerequisites

### Health Invariants (Checked Nightly)
Testable conditions that should always hold:
- Count-based (minimum viable population)
- Quality-based (no values in invalid ranges)
- Consistency-based (referential integrity)
- Ratio-based (proportion thresholds)

### Cross-Boundary Contracts
Data integrity conditions at interfaces between subsystems (see Section 21).

---

## Subsystem Contracts

### Subsystem 1: QA & Query (10K LOC, ⚠️ YELLOW)

**Entry Contract**
- LLM API credentials available (OpenAI/Claude endpoint configured)
- Question reformulation rules loaded from `data/qa_reformulation_rules.json`
- Extraction vocabulary cached from Subsystem 14 (Taxonomy)
- T1 frameworks (Subsystem 5) must be accessible via REST endpoint

**Exit Contract**
- Every QA response has exactly one primary framework assignment
- All entity references are normalized via Subsystem 14 vocabulary
- Response enrichment signals (from Subsystem 18) must be present in output metadata
- Extraction quality score (Subsystem 8) >= 0.7 for paper-sourced evidence

**Health Invariants**
- INV-QA-1: LLM API client is initialized and testable via `ping()` method (check every 15 min)
- INV-QA-2: `qa_response_cache` table has < 5% stale entries (checked against last_called timestamp)
- INV-QA-3: No QA response field is NULL or empty string (schema validation)
- INV-QA-4: All framework_ids in responses correspond to existing T1 frameworks (referential integrity, checked against Subsystem 5)
- INV-QA-5: Mean QA response latency ≤ 3s (95th percentile ≤ 8s)

**Yellow Threshold**: API response time > 2s, cache hit rate < 60%
**Red Threshold**: API unavailable or LLM responds with error > 10% of requests

---

### Subsystem 2: Export & Reporting (7K LOC, ✅ GREEN)

**Entry Contract**
- All prerequisite data must be loaded from Web of Belief (Subsystem 3)
- Template registry (Subsystem 5) must be available
- Report format schemas (JSON/CSV/DOCX) must be deployed
- Output directory must be writable with >= 100MB free space

**Exit Contract**
- Every exported report includes metadata (timestamp, version, subsystem health status)
- Report files must pass schema validation before writing
- All belief credences exported must match Web of Belief ground truth (XB-2)
- DOCX files must include proper citation formatting per `SCIENCE_COMMUNICATION_NORMS.md`

**Health Invariants**
- INV-EXP-1: `reports_generated_this_month` >= 100 (operational floor)
- INV-EXP-2: Export success rate >= 98% (failures tracked in error log)
- INV-EXP-3: No report file is corrupted (checked via file hash verification against manifest)
- INV-EXP-4: All exported belief IDs exist in Web of Belief (referential integrity, sampling 100 random beliefs)
- INV-EXP-5: Report generation time <= 30s for standard 500-belief reports (95th percentile)

**Yellow Threshold**: Export success rate 95-98%, missing belief references < 2%
**Red Threshold**: Export success rate < 95%, > 5% of belief references missing

---

### Subsystem 3: Web of Belief (7K LOC, ✅ GREEN)

**Entry Contract**
- SQLite database (web.db) must be initialized with complete schema
- Belief schema must conform to ClaimV2 (see `docs/CLAIM_V2_SCHEMA.md`)
- Minimum 4,800 bootstrapped beliefs must be loaded from `data/tier3_initial_beliefs.json`
- Constraint rules must be loaded from `data/coherence_constraints.json` (>= 8,000 rules)

**Exit Contract**
- Every newly inserted belief has valid entrenchment value in [0, 1] and provenance links
- Every constraint reference must point to existing beliefs (no dangling pointers)
- Web coherence metric must be computed immediately after modification (cached in overseer.db)
- All belief modifications must be logged to `web.db:audit_log` with timestamp and source

**Health Invariants**
- INV-WOB-1: `len(web.beliefs) >= 4,800` — belief count never regresses below bootstrap minimum
- INV-WOB-2: `len(web.constraints) >= 8,000` — constraint count never regresses
- INV-WOB-3: All constraints reference existing beliefs (100% referential integrity)
- INV-WOB-4: No belief has entrenchment > 1.0 or < 0.0 (range invariant, sample 1,000 random beliefs)
- INV-WOB-5: >= 60% of beliefs have entrenchment > 0.3 (quality floor: base-rate of non-marginal beliefs)
- INV-WOB-6: Every belief has at least one provenance link (foundation requirement per Haack 1993)
- INV-WOB-7: Web coherence score >= 0.65 (system-wide epistemic health)
- INV-WOB-8: Belief insertion rate in last 7 days >= 10 beliefs/day (operational floor)

**Yellow Threshold**: Coherence score 0.60-0.65, entrenchment violations < 5 beliefs
**Red Threshold**: Coherence < 0.60, > 100 beliefs with invalid entrenchment, referential integrity < 99%

---

### Subsystem 4: Paper Acquisition (6K LOC, ❌ RED)

**Entry Contract**
- CrossRef API key must be configured in `config/api_keys.json` (or env var CROSSREF_API_KEY)
- PubMed API key/email must be configured
- Semantic Scholar API key must be configured
- Local cache directory must exist with >= 500MB free space
- Rate limiter configured to respect API quotas (CrossRef: 50 req/sec, PubMed: 3 req/sec, S2: 10 req/sec)

**Exit Contract**
- Every acquired paper must have DOI, title, authors, abstract, and publication date
- Paper metadata must be deduplicated (no duplicate DOIs in `papers_acquired` table)
- Acquired papers must be staged in `data/staging/` before integration
- Paper acquisition event must be logged with timestamp, source API, and success/failure status

**Health Invariants**
- INV-PA-1: API keys for all three sources (CrossRef, PubMed, S2) are non-empty strings
- INV-PA-2: `papers_acquired` table has >= 50 entries from last 30 days (acquisition velocity floor)
- INV-PA-3: No duplicate DOI entries in `papers_acquired` (check COUNT(*) by DOI, max = 1)
- INV-PA-4: API call success rate >= 85% (logged in acquisition_events table)
- INV-PA-5: Average time-to-acquisition <= 5s per paper (95th percentile <= 15s)

**Yellow Threshold**: API success rate 75-85%, duplicate detection > 0, API keys expiring within 7 days
**Red Threshold**: Any API key missing/invalid, acquisition velocity < 10/month, success rate < 75%

**Status Note**: This subsystem is RED because API keys are not configured in this environment. Once configured, move to YELLOW until automated acquisition testing is added.

---

### Subsystem 5: Theory & Templates (5.5K LOC, ✅ GREEN)

**Entry Contract**
- T1 frameworks must be defined in `data/theory_frameworks.json` with exactly 10 entries
- T1.5 domain theories must be loaded from `tier1_5_domain_theories.json` (>= 13 theories as of V11)
- T2 templates must be loaded from `data/templates/` directory (>= 160 templates)
- T3 belief engine initialized with bootstrap beliefs (Subsystem 12)

**Exit Contract**
- Every T2 template must have exactly one parent T1.5 theory (referential integrity)
- Every T1.5 theory must have exactly one parent T1 framework (composition invariant)
- Template JSON schema must validate against `schemas/T2_TEMPLATE_SCHEMA.json`
- All template counts and parent relationships must be recorded in theory_metadata.db at integration time

**Health Invariants**
- INV-TT-1: `len(t1_frameworks) == 10` — canonical count immutable
- INV-TT-2: `len(t1_5_theories) >= 13` — domain theory count never regresses
- INV-TT-3: `len(t2_templates) >= 160` — template count never regresses
- INV-TT-4: Every T1.5 theory has `parent_t1_framework_id` pointing to existing T1 framework (100% referential integrity)
- INV-TT-5: Every T2 template has `parent_t1_5_theory_id` pointing to existing T1.5 theory (100% referential integrity)
- INV-TT-6: No T1 framework has null or empty name field (basic schema validity)
- INV-TT-7: Template registry audit at startup: missing files detected and reported

**Yellow Threshold**: Template file integrity warnings (< 3 files with format issues)
**Red Threshold**: Missing T1 framework, T1.5 theory counts regress, > 5 templates with bad schema

---

### Subsystem 6: DB & Infrastructure (6K LOC, ⚠️ YELLOW)

**Entry Contract**
- Two databases must be initialized: `web.db` (Web of Belief) and `overseer.db` (OVERSEER metrics)
- SQLite version >= 3.35 (for generated column support, transaction atomicity)
- Migration schema version must be current (checked against `migrations/` directory)
- All write-ahead log (WAL) files must be properly cleaned up

**Exit Contract**
- After every write transaction, both `web.db` and `overseer.db` must be in consistent state (no partial updates)
- Backup copies must be created nightly (see maintenance schedule in overseer.py)
- WAL checkpoints must be performed hourly (RESTART mode)
- Database integrity check (`PRAGMA integrity_check`) must pass with 0 errors

**Health Invariants**
- INV-DBI-1: Both `web.db` and `overseer.db` are readable and writable (test via SELECT COUNT(*) from schema_version)
- INV-DBI-2: `PRAGMA integrity_check` returns "ok" (0 corruptions detected)
- INV-DBI-3: No database file is locked for > 5 seconds (WAL deadlock detection)
- INV-DBI-4: Backup directory has >= 2 recent snapshots (last 7 days, one per day)
- INV-DBI-5: Total database size <= 2GB (soft limit; over 2GB triggers warning to archive old papers)
- INV-DBI-6: Foreign key constraints are enabled (`PRAGMA foreign_keys = ON` in all connection strings)
- INV-DBI-7: No orphaned rows in join tables (referential integrity: sample 1,000 random belief_constraints rows)

**Yellow Threshold**: Single database > 1.5GB, backup < daily, WAL lock waits > 1s
**Red Threshold**: Database corruption detected, foreign keys disabled, backups missing > 2 days

**Status Note**: This subsystem is YELLOW because dual-DB architecture creates consistency risk. Consider migration to unified schema (Subsystem 6 enhancement).

---

### Subsystem 7: Bayesian Network (5K LOC, ⚠️ YELLOW)

**Entry Contract**
- BayesianNetwork instance must be initialized with empty edge set
- Must have read-only connection to Web of Belief for belief credence data
- PyGraphviz (or networkx) must be available for graph operations
- Prior conditional probability tables must be precomputed and cached

**Exit Contract**
- Every edge in the BN must correspond to a constraint in Web of Belief (XB-4: BN-Web sync)
- Edge weights must exactly match belief credences in Web (within ±0.01 tolerance)
- BN must export successfully to DOT/GraphML format without errors
- BN must remain acyclic (topological sort possible)

**Health Invariants**
- INV-BN-1: BN is acyclic (topological sort completes without cycle detection)
- INV-BN-2: `len(bn.edges) == len(web.constraints)` — edge count matches constraint count (bidirectional sync invariant)
- INV-BN-3: Every edge weight is in [0, 1] (credence range valid)
- INV-BN-4: No dangling nodes (every node has at least one edge OR is a root node)
- INV-BN-5: BN export to GraphML/DOT completes without error (structural validity)
- INV-BN-6: Mean node degree >= 1.5 (graph is not trivially sparse)
- INV-BN-7: All edge weights are synchronized with Web of Belief credences (spot-check 100 random edges: diff < 0.01)

**Yellow Threshold**: Edge weight drift 0.01-0.05 from Web credences, sparse regions detected (degree < 1.0)
**Red Threshold**: Cycles detected, edge count diverges > 5% from constraints, weight drift > 0.05

**Status Note**: This subsystem is YELLOW because it is export-only (no bidirectional propagation). Implement INV-BN-2 enforcement before moving to GREEN.

---

### Subsystem 8: Extraction & Integration (5K LOC, ✅ GREEN)

**Entry Contract**
- Field Reviewer (human) must be available for validation (asynchronous, soft requirement)
- Paper staging directory must contain valid PDF/plaintext files
- Extraction rules from Subsystem 5 must be accessible
- Target database (Web of Belief, Subsystem 3) must be ready for writes

**Exit Contract**
- Extracted claims must conform to ClaimV2 schema
- Extraction must be attributed to source paper with DOI linkage
- Field reviewer must validate before integration (or system tags as UNREVIEWED)
- All extracted claims must be logged to `extractions.db` with confidence scores

**Health Invariants**
- INV-EI-1: Extraction success rate >= 90% (papers successfully extracted vs. attempted)
- INV-EI-2: No extraction has NULL `source_paper_id` (provenance traceability requirement)
- INV-EI-3: All extracted claims have `confidence_score` in [0, 1] (quality floor)
- INV-EI-4: Mean extraction confidence >= 0.75 (INV-10 from overseer.py)
- INV-EI-5: Field reviewer terminal rate <= 10% (max 10% of extractions classified as TERMINAL_REVIEW_NEEDED without human action)
- INV-EI-6: No extraction has timestamp > current_time (temporal integrity)
- INV-EI-7: All referenced T1.5 theories exist in Subsystem 5 (referential integrity to theory registry)

**Yellow Threshold**: Success rate 85-90%, mean confidence 0.70-0.75, reviewer backlog > 100 items
**Red Threshold**: Success rate < 85%, mean confidence < 0.70, > 20% reviewer terminal rate

---

### Subsystem 9: Overseer & Self-Monitoring (5K LOC, ✅ GREEN)

**Entry Contract**
- `overseer.db` must be initialized with health metrics schema (migration 023)
- Baseline metrics snapshot must be available (computed on first run or loaded from file)
- All monitored subsystems must be reachable for health checks
- Notification delivery system (email/Slack) must be configured (soft requirement)

**Exit Contract**
- Health report must be generated and persisted to overseer.db
- All invariant violations must be logged with timestamp and severity
- Quarantine actions must be written to quarantine table with 7-day expiry
- Alert notifications must be sent within 60s of violation detection (if enabled)

**Health Invariants**
- INV-OS-1: `overseer_health_metrics` table has >= 1,440 records in last 30 days (one nightly audit per day)
- INV-OS-2: No periodic audit takes > 15 minutes (95th percentile)
- INV-OS-3: All 20 subsystem health checks complete in last 24 hours (staleness detector)
- INV-OS-4: Violation detection system is operational (test via synthetic violation)
- INV-OS-5: Quarantine queue has < 50 active items (operational floor; > 50 indicates systemic issues)
- INV-OS-6: Alert notification delivery success rate >= 95% (if enabled)
- INV-OS-7: No metric computation takes > 2s (individual subsystem health check timeout)

**Yellow Threshold**: Audit time 10-15 min, health check staleness > 6 hours, quarantine queue > 30
**Red Threshold**: Audit time > 15 min, any subsystem health check missing > 24 hours, violation detection fails

---

### Subsystem 10: Interpretation Space (5K LOC, ✅ GREEN)

**Entry Contract**
- Must be callable as a service from Answer Enrichment Orchestrator (Subsystem 18)
- Interpretation templates must be loaded from `data/interpretation_templates.json`
- Alternative interpretation rules must be available (from Subsystem 5)
- Input must conform to interpretation_request schema (JSON with question and answer context)

**Exit Contract**
- Interpretation output must include: primary_interpretation, alternatives (list), confidence_score
- All interpretations must be attributable to a template or rule (no anonymous interpretations)
- Output must conform to interpretation_response schema
- Service must return within 2s timeout (enforced by orchestrator)

**Health Invariants**
- INV-IS-1: `len(interpretation_templates) >= 20` (minimum template registry size)
- INV-IS-2: Interpretation service latency <= 2s (95th percentile, timeout threshold)
- INV-IS-3: No interpretation has confidence_score outside [0, 1] (range invariant)
- INV-IS-4: Service error rate <= 2% (graceful degradation in orchestrator)
- INV-IS-5: At least 80% of interpretations reference a valid template_id (traceability requirement)

**Yellow Threshold**: Service latency 1.5-2s, error rate 1-2%, template count declining
**Red Threshold**: Service latency > 2s (timeouts), error rate > 2%, template_id references < 70%

---

### Subsystem 11: Warrant & Credence (3K LOC, ✅ GREEN)

**Entry Contract**
- Belief credences from Web of Belief (Subsystem 3) must be accessible
- Warrant generation rules must be loaded from `data/warrant_rules.json`
- Support/attack relations must be available from constraints
- Prior probabilities must be available (from empirical base rate data)

**Exit Contract**
- Every warrant must have justification_text and warrant_type (COHERENCE | EMPIRICAL | FOUNDATIONAL)
- Every warrant must have numeric support value in [0, 1]
- Every credence update must be logged to belief_credence_history with timestamp and source
- Updated credence must fall within posterior probability bounds

**Health Invariants**
- INV-WC-1: All 62 unit tests in test_warrant_credence.py pass (regression suite)
- INV-WC-2: No warrant has support value outside [0, 1] (range invariant, sample 500 random warrants)
- INV-WC-3: Mean warrant support >= 0.5 (operational floor: warrants are meaningful)
- INV-WC-4: All warrant_type values are in {COHERENCE, EMPIRICAL, FOUNDATIONAL} (enum validation)
- INV-WC-5: Warrant generation time <= 100ms per belief (service performance)
- INV-WC-6: No credence has regressed by > 0.5 in a single update (anomaly detection)

**Yellow Threshold**: Test pass rate 95-98%, mean warrant support 0.45-0.50, anomaly count > 5
**Red Threshold**: Test pass rate < 95%, credence regressions > 10%, invalid warrant types > 1%

---

### Subsystem 12: T3 Belief Engine (3K LOC, ✅ GREEN)

**Entry Contract**
- Bootstrap beliefs must be loaded from `data/tier3_initial_beliefs.json` (>= 596 beliefs as of V11)
- T2 templates (Subsystem 5) must be accessible for belief classification
- Extraction pipeline (Subsystem 8) must be operational for new belief integration
- Classification rules must be loaded and cached

**Exit Contract**
- Every newly classified belief must have assigned T1.5 theory
- Every belief must pass schema validation (ClaimV2 or T3-specific extension)
- Classification confidence must be recorded (value in [0, 1])
- Classified beliefs must be integrated into Web of Belief with provenance

**Health Invariants**
- INV-T3-1: `len(t3_established_beliefs) >= 596` (bootstrap minimum, never regress)
- INV-T3-2: T3 classification rate >= 70% (percent of extraction-sourced claims that are classified)
- INV-T3-3: `len(t3_established_beliefs) >= 200` (INV-12 from overseer.py, quality floor)
- INV-T3-4: Mean classification confidence >= 0.70 (quality gate)
- INV-T3-5: No belief is classified to non-existent T1.5 theory (referential integrity to Subsystem 5)
- INV-T3-6: Belief classification time <= 500ms per claim (service SLA)

**Yellow Threshold**: Classification rate 60-70%, mean confidence 0.65-0.70, classification time 300-500ms
**Red Threshold**: Classification rate < 60%, confidence < 0.65, invalid theory references > 5

---

### Subsystem 13: Image Pipeline (3K LOC, ⚠️ YELLOW)

**Entry Contract**
- Images must be in standard formats (PNG, JPEG, WebP) with valid EXIF/metadata
- Vision API must be configured (OpenAI, Claude, or local model)
- Classification rules for environment images must be loaded
- Batch processing queue must be initialized

**Exit Contract**
- Every image must have classification label and confidence score
- Every image must have descriptive caption (generated or OCR'd)
- No image data must be persisted beyond classification (privacy requirement)
- Classification results must be logged to image_classifications table

**Health Invariants**
- INV-IMG-1: Image classification success rate >= 75% (partial implementation tolerance)
- INV-IMG-2: All classification confidence scores are in [0, 1] (range invariant)
- INV-IMG-3: Mean classification latency <= 2s per image (95th percentile)
- INV-IMG-4: No unclassified images remain in processing queue > 24 hours
- INV-IMG-5: Image metadata (filename, source) is preserved in classification record

**Yellow Threshold**: Success rate 75-85%, latency 1.5-2s, queue depth > 100
**Red Threshold**: Success rate < 75%, latency > 2s, unclassified images > 48 hours

**Status Note**: This subsystem is YELLOW because of partial implementation. See V11 audit (line 68) for coverage gaps.

---

### Subsystem 14: Taxonomy & Vocabulary (3K LOC, ✅ GREEN)

**Entry Contract**
- Taxonomy graph must be loaded from `data/taxonomy.json` (>= 133 nodes as of V11)
- Vocabulary standardization rules must be deployed
- Concept linking rules must be initialized
- No circular references allowed in taxonomy DAG

**Exit Contract**
- Every term used in extraction must be mapped to canonical taxonomy entry
- All entity normalization must be logged with original → canonical mapping
- No term should be ambiguous (map to multiple taxonomy nodes without context)
- Taxonomy updates must be versioned and logged to taxonomy_changelog

**Health Invariants**
- INV-TAX-1: `len(taxonomy_nodes) >= 133` (node count never regresses)
- INV-TAX-2: Taxonomy DAG is acyclic (topological sort completes without cycle)
- INV-TAX-3: No taxonomy node has NULL or empty label (basic validity)
- INV-TAX-4: Mean term normalization success rate >= 95% (in extraction pipeline)
- INV-TAX-5: All parent_node_ids in taxonomy point to existing nodes (referential integrity)
- INV-TAX-6: Vocabulary lookup latency <= 50ms per term (caching requirement)

**Yellow Threshold**: Success rate 90-95%, lookup latency 30-50ms, new nodes pending integration
**Red Threshold**: Success rate < 90%, lookup latency > 50ms, cycles detected in DAG

---

### Subsystem 15: CVA (Cumulative Value Assessment) (3K LOC, ✅ GREEN)

**Entry Contract**
- Web of Belief (Subsystem 3) must be accessible with current credence values
- Value metrics must be configured in `config/cva_weights.json`
- Benchmark beliefs must be defined (for value comparison)
- Time series data must be available (for trend analysis)

**Exit Contract**
- CVA score must be computed and recorded with timestamp
- Belief value contributions must be attributed to source theory
- Score must be bounded in [0, 1] (normalized form)
- Historical CVA scores must be persisted for trending

**Health Invariants**
- INV-CVA-1: CVA computation completes within 5s (includes Web traversal)
- INV-CVA-2: All computed CVA scores are in [0, 1] (range invariant)
- INV-CVA-3: CVA score never regresses by > 0.2 between consecutive audits (anomaly detection)
- INV-CVA-4: At least 80% of beliefs contribute to CVA (coverage requirement)
- INV-CVA-5: CVA time series has >= 30 points in last 30 days (resolution for trending)

**Yellow Threshold**: Computation time 3-5s, coverage 75-80%, regression > 0.1
**Red Threshold**: Computation > 5s, coverage < 75%, unexplained regression > 0.2

---

### Subsystem 16: Argumentation (2K LOC, ✅ GREEN)

**Entry Contract**
- Argument schemes must be loaded from `data/argument_schemes.json`
- Support/attack relations must be available from Web of Belief constraints
- Rhetoric rules must be deployed (for fallacy detection)
- Dialogue rules must be initialized (for conversation management)

**Exit Contract**
- Every argument must have scheme classification (MODUS_PONENS, ANALOGY, INDUCTION, etc.)
- Attack relations must be labeled with fallacy type (if applicable)
- Argument strength must be computed from support evidence
- All arguments must be attributed to source (belief or constraint)

**Health Invariants**
- INV-ARG-1: All argument scheme IDs are in registered scheme list (no invalid schemes)
- INV-ARG-2: Mean argument strength >= 0.5 (quality floor)
- INV-ARG-3: No argument has strength outside [0, 1] (range invariant)
- INV-ARG-4: Fallacy detection accuracy >= 85% (validated against human judges)
- INV-ARG-5: Argument generation time <= 200ms per belief (service SLA)

**Yellow Threshold**: Detection accuracy 80-85%, generation time 150-200ms, invalid schemes < 2
**Red Threshold**: Detection accuracy < 80%, generation time > 200ms, invalid schemes > 5

---

### Subsystem 17: Annotation (1K LOC, ✅ GREEN)

**Entry Contract**
- Annotation schema must be defined in `schemas/annotation_schema.json`
- Human annotators must have credentials and permissions
- Target data (beliefs, claims, images) must be accessible
- Annotation tasks must be queued in annotation_tasks table

**Exit Contract**
- Every annotation must have annotator_id, timestamp, and label
- Confidence scores (if applicable) must be in [0, 1]
- All annotations must be versioned (history preserved)
- Annotations must reference exactly one belief/claim/image (no orphans)

**Health Invariants**
- INV-ANN-1: `len(annotations) >= 441` (bootstrapped minimum from V11 audit, line 48)
- INV-ANN-2: All annotation labels are in schema vocabulary (enum validation)
- INV-ANN-3: Annotation completion rate >= 90% (tasks completed vs. assigned)
- INV-ANN-4: No annotation is orphaned (all reference valid beliefs/claims/images)
- INV-ANN-5: Inter-annotator agreement >= 0.75 (Cohen's kappa for overlapping tasks)

**Yellow Threshold**: Completion rate 85-90%, kappa 0.70-0.75, annotation count declining
**Red Threshold**: Completion rate < 85%, kappa < 0.70, orphaned annotations > 10

---

### Subsystem 18: Answer Enrichment Orchestrator (1K LOC, ✅ GREEN)

**Entry Contract**
- All 13 lazy-load services must be configured in `config/service_registry.json`:
  1. Interpretation Space (Subsystem 10)
  2. Argumentation (Subsystem 16)
  3. Bridge Warrants (warrant linking)
  4. Prediction Service (predictive inference)
  5. Language Adaptation Service (Norm Services, Subsystem 19)
  6. Figure Suggestion Service (Subsystem 19)
  7. Math Explanation Service (Subsystem 19)
  8. (and 6 others per orchestrator.py)
- QA response must be available (from Subsystem 1)
- 2s timeout budget must be available per service (total 18s worst-case)

**Exit Contract**
- Every enriched answer must include:
  - Original QA response
  - Interpretation (from service 1)
  - Supporting arguments (from service 2)
  - Adapted language (from service 5, depending on user type)
  - Suggested figures (from service 6, if applicable)
  - Mathematical explanations (from service 7, if equations present)
- All service step outcomes must be logged to enrichment_log
- Failed steps must degrade gracefully (skip, don't error out)

**Health Invariants**
- INV-ORC-1: All 13 services in registry are importable and testable (lazy-load validation)
- INV-ORC-2: No enrichment step takes > 2s (timeout enforcement per service)
- INV-ORC-3: Total enrichment latency <= 18s for worst case (9 steps × 2s)
- INV-ORC-4: Enrichment success rate >= 95% (graceful degradation in place)
- INV-ORC-5: Mean enrichment latency <= 8s (95th percentile, typical case)
- INV-ORC-6: Service step failure rate <= 5% per service (monitored individually)
- INV-ORC-7: All mock data in steps 4-8 are clearly marked as MOCK (see V11 audit, line 93)

**Yellow Threshold**: Success rate 90-95%, mean latency 6-8s, service failures 3-5%
**Red Threshold**: Success rate < 90%, any service latency > 2s, total latency > 18s

**Status Note**: See V11 audit § "ℹ️ What Needs Work" (lines 89-99) for wiring priorities. Steps 4-8 currently return mock data.

---

### Subsystem 19: Norm Services (1.5K LOC, ✅ GREEN)

**Entry Contract**
- Language Adaptation Service: 5 user type profiles must be loaded (`data/user_profiles.json`)
- Figure Suggestion Service: 42-figure registry must be deployed (`data/figure_registry.json`)
- Math Explanation Service: 6 canonical formulas × 7 explanation norms must be loaded (`data/math_explanations.json`)
- User context must be available (from QA session or metadata)

**Exit Contract**
- Language-adapted answer must match original semantics (correctness check)
- Suggested figures must be relevant to answer content (human validation)
- Mathematical explanations must conform to science communication norms (`contracts/SCIENCE_COMMUNICATION_NORMS.md`)
- All adaptations must be logged with user type and explanation

**Health Invariants**
- INV-NORM-1: `len(user_profiles) == 5` (canonical user type set)
- INV-NORM-2: `len(figure_registry) >= 42` (figure count never regresses)
- INV-NORM-3: All recommended figures exist in registry (referential integrity)
- INV-NORM-4: No language adaptation changes answer correctness (semantic invariance)
- INV-NORM-5: Math explanation service latency <= 500ms per formula (caching required)
- INV-NORM-6: All science communication norms are applied (audit 10 random explanations monthly)

**Yellow Threshold**: Figure recommendation < 80% coverage, adaptation latency 300-500ms, norm violations < 2
**Red Threshold**: Figure recommendations < 60%, latency > 500ms, norm violations > 5

---

### Subsystem 20: Agent Coordination (Infrastructure, ✅ GREEN)

**Entry Contract**
- COORDINATION_STATE must be initialized as empty JSON object or loaded from previous session
- MESSAGE_BOARD must be created (simple list/queue, writable by all agents)
- CHANGELOG must be versioned (Git-style commit log for all agent state changes)
- Task claiming protocol must be defined (see `CLAUDE.md` § "Task Check-In/Check-Out")

**Exit Contract**
- Every agent must claim a task before starting work (record in MESSAGE_BOARD)
- Every agent must release task when done (move to CHANGELOG with outcome)
- All state mutations must be recorded (immutable audit trail in CHANGELOG)
- No two agents must claim the same task simultaneously (mutual exclusion)

**Health Invariants**
- INV-AGENT-1: COORDINATION_STATE is valid JSON (parseable, acyclic)
- INV-AGENT-2: No task is claimed by > 1 agent (mutual exclusion verified by claiming timestamp)
- INV-AGENT-3: All claimed tasks have deadline (expiry time or session end marker)
- INV-AGENT-4: CHANGELOG has >= 1 entry per active session (audit trail exists)
- INV-AGENT-5: Task completion rate >= 90% (tasks claimed and completed vs. abandoned)
- INV-AGENT-6: No unclaimed task sits idle > 2 hours (staleness detector for blocking tasks)

**Yellow Threshold**: Completion rate 85-90%, unclaimed tasks idle 1-2 hours, stale claims > 5
**Red Threshold**: Completion rate < 85%, tasks idle > 2 hours, deadlock detected (circular dependencies)

**Status Note**: This subsystem is infrastructure-level. Monitor for agent coordination failures; escalate to David for mediation if deadlock detected.

---

## Cross-Boundary Contracts

These contracts define data integrity conditions at interfaces between subsystems. They are checked during POST_INTEGRATION and PERIODIC audits.

### XB-1: Template-Registry Contract
**Between**: Subsystem 5 (Theory & Templates) ↔ Subsystem 18 (Answer Enrichment Orchestrator)

Every T2 template referenced in enrichment steps must exist in the template registry.

```
∀ template_id ∈ enrichment_response.used_templates:
  ∃ template ∈ templates_registry where template.id == template_id
```

**Check**: Sampling 100 random enriched answers, verify all template_id references exist.
**Severity**: CRITICAL (broken enrichment pipeline)

---

### XB-2: Belief-Persistence Contract
**Between**: Subsystem 3 (Web of Belief) ↔ Subsystem 2 (Export & Reporting)

Every belief exported in a report must exist in Web of Belief with identical credence (within ±0.01).

```
∀ belief ∈ exported_report.beliefs:
  ∃ web_belief ∈ web.beliefs where web_belief.id == belief.id
  AND |web_belief.credence - belief.credence| ≤ 0.01
```

**Check**: Sample 50 random exported beliefs, verify ground truth in Web of Belief.
**Severity**: MAJOR (reporting accuracy)

---

### XB-3: Framework-Reference Contract
**Between**: Subsystem 1 (QA & Query) ↔ Subsystem 5 (Theory & Templates)

Every framework_id in a QA response must correspond to an existing T1 framework.

```
∀ framework_id ∈ qa_response.assigned_frameworks:
  ∃ framework ∈ t1_frameworks where framework.id == framework_id
```

**Check**: Verify all framework assignments in last 100 QA responses.
**Severity**: MAJOR (schema consistency)

---

### XB-4: BN-Web Synchronization Contract
**Between**: Subsystem 7 (Bayesian Network) ↔ Subsystem 3 (Web of Belief)

BN edges must match Web of Belief constraints 1:1. Edge weights must equal belief credences (±0.01 tolerance).

```
∀ constraint ∈ web.constraints:
  ∃ edge ∈ bn.edges where edge.source == constraint.belief_a
  AND edge.target == constraint.belief_b
  AND |edge.weight - constraint.credence_weight| ≤ 0.01

∀ edge ∈ bn.edges:
  ∃ constraint ∈ web.constraints [reciprocal]
```

**Check**: Verify edge-constraint parity (count + weight) after each integration.
**Severity**: CRITICAL (Bayesian integrity)

---

### XB-5: Extraction-Integration Provenance Contract
**Between**: Subsystem 8 (Extraction & Integration) ↔ Subsystem 3 (Web of Belief)

Every belief in Web of Belief that was extraction-sourced must have valid paper_id link to Papers table and valid extraction_id link to extractions.db.

```
∀ belief ∈ web.beliefs where belief.source_type == "EXTRACTION":
  ∃ paper ∈ papers where paper.id == belief.source_paper_id
  AND ∃ extraction ∈ extractions where extraction.id == belief.source_extraction_id
```

**Check**: Sample 200 extraction-sourced beliefs, verify both links exist.
**Severity**: MAJOR (provenance traceability)

---

### XB-6: Theory-Belief Consistency Contract
**Between**: Subsystem 5 (Theory & Templates) ↔ Subsystem 12 (T3 Belief Engine)

Every T3 belief must be assigned to a T1.5 theory that exists in the theory registry. No belief should be classified to retired/removed theory.

```
∀ belief ∈ t3_established_beliefs:
  ∃ theory ∈ t1_5_theories where theory.id == belief.assigned_t1_5_theory_id
  AND theory.is_active == true
```

**Check**: Verify all T3 beliefs reference active theories (sample 300 random beliefs).
**Severity**: MAJOR (classification integrity)

---

### XB-7: Warrant-Belief Contract
**Between**: Subsystem 11 (Warrant & Credence) ↔ Subsystem 3 (Web of Belief)

Every warrant must reference an existing belief in Web of Belief. Warrant support values must not exceed belief credence by more than coherence delta (0.15).

```
∀ warrant ∈ warrants:
  ∃ belief ∈ web.beliefs where belief.id == warrant.target_belief_id
  AND warrant.support_value ≤ belief.credence + 0.15
```

**Check**: Sample 100 random warrants, verify references and support bounds.
**Severity**: MAJOR (epistemic coherence)

---

### XB-8: Vocabulary Normalization Contract
**Between**: Subsystem 14 (Taxonomy & Vocabulary) ↔ Subsystem 8 (Extraction & Integration)

All entity references in extracted claims must be normalized to canonical taxonomy terms. No raw entity names should appear in Web of Belief beliefs (post-normalization).

```
∀ belief ∈ web.beliefs where belief.source_type == "EXTRACTION":
  ∀ entity ∈ belief.entities:
    ∃ taxonomy_node ∈ taxonomy where taxonomy_node.id == entity.canonical_taxonomy_id
```

**Check**: Sample 100 extraction-sourced beliefs, verify entity normalization.
**Severity**: MAJOR (semantic consistency)

---

### XB-9: Service Availability Contract
**Between**: Subsystem 18 (Answer Enrichment Orchestrator) ↔ All Service Subsystems (10, 16, 19, etc.)

All registered services in the orchestrator's service_registry must be importable, callable, and responsive within their timeout budget (2s).

```
∀ service ∈ orchestrator.service_registry:
  ∃ callable service.import_path()
  AND service.call(test_input) completes within 2s
  AND response conforms to service.response_schema
```

**Check**: Run service health check every 6 hours (orchestrator startup + periodic).
**Severity**: CRITICAL (enrichment pipeline availability)

---

### XB-10: Annotation Referential Integrity Contract
**Between**: Subsystem 17 (Annotation) ↔ Subsystems 3, 8, 13 (Web of Belief, Extraction, Image Pipeline)

Every annotation must reference exactly one target (belief, extraction, or image). No annotation should become orphaned if the target is deleted (soft-delete required).

```
∀ annotation ∈ annotations:
  (∃ belief ∈ web.beliefs where belief.id == annotation.target_id) XOR
  (∃ extraction ∈ extractions where extraction.id == annotation.target_id) XOR
  (∃ image ∈ images where image.id == annotation.target_id)
```

**Check**: Verify no orphaned annotations (sample 500 random annotations).
**Severity**: MAJOR (data consistency)

---

### XB-11: Credence-Entrenchment Coherence Contract
**Between**: Subsystem 11 (Warrant & Credence) ↔ Subsystem 3 (Web of Belief)

Belief credences must be correlated with entrenchment values. Low entrenchment (< 0.3) should generally have lower credence, and vice versa (Spearman ρ > 0.6).

```
Spearman_ρ(web.beliefs.entrenchment, web.beliefs.credence) > 0.6
```

**Check**: Monthly audit of belief population statistics.
**Severity**: MINOR (suggests incoherent belief structure)

---

### XB-12: Export-QA Response Consistency Contract
**Between**: Subsystem 2 (Export & Reporting) ↔ Subsystem 1 (QA & Query)

Beliefs referenced in QA responses must not contradict beliefs in exported reports when both are based on same underlying Web state (timestamp within 1 hour).

```
∀ qa_response ∈ recent_qa_responses:
  ∀ belief ∈ qa_response.referenced_beliefs:
    ∃ report_belief ∈ recent_reports where report_belief.id == belief.id
    AND |report_belief.credence - belief.credence| ≤ 0.05
```

**Check**: Sample 10 recent QA responses, compare referenced beliefs to concurrent reports.
**Severity**: MEDIUM (user-facing consistency)

---

## Health Check Schedule and Severity Mapping

### Periodic Audit (Nightly, ~15 min)
Runs all 140+ invariants across all 20 subsystems.

| Severity | Action | Escalation |
|----------|--------|-----------|
| GREEN ✅ | Log success | None |
| YELLOW ⚠️ | Log warning, notify David | Email alert (if configured) |
| RED ❌ | Log critical, trigger quarantine | Immediate Slack/email + log entry |

### Post-Integration Check (~5 sec)
Focused subset: INV-0..INV-5 (from overseer.py) + cross-boundary contracts touching the integrated paper.

| Violation Type | Auto-Action | Human Review |
|---|---|---|
| Provenance missing (INV-1) | Quarantine extraction | 7 days, then delete |
| Credence out of range (INV-5) | Clamp to [0, 1], log | Required (why? how?) |
| BN-Web sync (XB-4) | Rebuild edge weights | Manual approval |
| Framework ref invalid (XB-3) | Tag response as DEGRADED | P1 fix required |

### Alert Thresholds

Trigger immediate alert if:
- Any RED invariant detected
- Three YELLOW invariants across same subsystem
- Cross-boundary contract violation
- Service unavailability (XB-9)

---

## Invariant Check Implementation (Pseudocode)

```python
def run_health_check(mode: str = "PERIODIC") -> HealthReport:
    """
    Execute all health checks across 20 subsystems.
    """
    health_metrics = {}
    violations = []
    alerts = []

    for subsystem in [QA, Export, WebOfBelief, ..., AgentCoord]:
        # Run entry contract checks
        if not subsystem.validate_entry_contract():
            violations.append(
                InvariantViolation(
                    code=f"{subsystem.id}-ENTRY",
                    severity="CRITICAL",
                    description=f"{subsystem.name} entry contract failed"
                )
            )
            continue  # Skip health checks if entry fails

        # Run exit contract checks
        if not subsystem.validate_exit_contract():
            violations.append(
                InvariantViolation(
                    code=f"{subsystem.id}-EXIT",
                    severity="CRITICAL"
                )
            )

        # Run health invariants
        for invariant in subsystem.invariants:
            result = invariant.check()
            if not result.passed:
                violations.append(result.violation)
                health_metrics[invariant.code] = "FAIL"
            else:
                health_metrics[invariant.code] = "PASS"

    # Run cross-boundary contracts
    for xb_contract in cross_boundary_contracts:
        if not xb_contract.validate():
            violations.append(
                InvariantViolation(
                    code=xb_contract.code,
                    severity=xb_contract.severity,
                    description=xb_contract.failure_reason
                )
            )

    # Generate alerts
    alerts = _generate_alerts(violations, health_metrics)

    # Record to overseer.db
    _persist_health_report(mode, health_metrics, violations)

    return HealthReport(
        timestamp=datetime.now().isoformat(),
        mode=mode,
        health_metrics=health_metrics,
        violations=violations,
        alerts=alerts
    )
```

---

## Status Summary (V11, 2026-03-02)

| Count | Status | Subsystems |
|-------|--------|-----------|
| 14 | ✅ GREEN | Export, Web of Belief, Theory & Templates, Extraction & Integration, Overseer, Interpretation Space, Warrant & Credence, T3 Engine, Taxonomy, CVA, Argumentation, Annotation, Enrichment Orchestrator, Norm Services, Agent Coordination |
| 4 | ⚠️ YELLOW | QA & Query, DB & Infrastructure, Bayesian Network, Image Pipeline |
| 2 | ❌ RED | Paper Acquisition (API keys missing), (none as of V11) |

**Overall System Health**: 14/20 ✅ PASS, 4/20 ⚠️ WARN, 2/20 ❌ FAIL

**Next Steps** (from V11 audit lines 92-99):
1. Wire orchestrator steps 4-8 to actual services (not mock data) — P1
2. Add end-to-end QA test — P1
3. Configure Paper Acquisition API keys or document fallback — P1
4. Add service health endpoint — P2
5. Implement enrichment budget timeout (5s total, not 18s worst-case) — P2

---

## References

- Dijkstra, E.W. (1968). The structure of the "THE" multiprogramming system. *CACM* 11(5):341-346.
- Haack, S. (1993). *Evidence and Inquiry*. Blackwell.
- Pearl, J. (2009). *Causality* (2nd ed.). Cambridge University Press.
- Cartwright, N. (2012). *Will This Policy Work for You?* Oxford University Press.
- CLAUDE.md (2026-02-14). Root-level guidance for Claude Code across all repositories.
- RUTHLESS_V11_ENGINEERING_AUDIT_2026-03-02.md. System health assessment pre-release.

---

**Version History**
- 1.0 (2026-03-03): Initial specification with 20 subsystems, 140+ invariants, 12 cross-boundary contracts
