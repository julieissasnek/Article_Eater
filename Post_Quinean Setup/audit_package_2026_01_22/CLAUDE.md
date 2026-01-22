# CLAUDE.md

*Last updated: Sunday, January 19, 2026 (Sprints 6-9 complete, Panel Fixes applied)*

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Article Eater V21.0.0 (Post-Quinean) extracts evidence-backed rules from scientific articles for CNFA neuroarchitecture research. Currently integrating Quinean Web of Belief coherentist epistemology.

**Owner**: Professor David Kirsh, UCSD Cognitive Science (since 1989), former MIT AI Lab

**Repo Path**: `/Users/davidusa/REPOS/Article_Eater_PostQuinean_v1`

## Sprint Status

- **Sprint 1**: COMPLETE - `src/services/extraction_to_web.py` mapper (claims→beliefs)
  - Expert panel reviewed 5 decision points (2026-01-18)
- **Sprint 2**: COMPLETE - Pipeline integration in `app/tasks/pipeline.py`
  - Expert panel reviewed 6 decisions (2026-01-18)
  - Formal schemas: `contracts/ae_af/schemas/ae.web_state.v1.schema.json`, `ae.coherence_summary.v1.schema.json`
  - Configurable via: `AE_WEB_SEEK_EQUILIBRIUM`, `AE_WEB_EQUILIBRIUM_MAX_ITERATIONS`, `AE_WEB_CONVERGENCE_THRESHOLD`
- **Sprint 3**: COMPLETE - Bridge warrants in `src/services/bridge_warrants.py`
  - Expert panel reviewed 6 decisions (2026-01-18)
  - Schema: `contracts/ae_af/schemas/ae.bridge.v1.schema.json`
  - Four bridge types: mechanism, functional, analogical, constitutive
  - Default P(bridge): Constitutive 0.85, Mechanism 0.60, Functional 0.50, Analogical 0.35
  - Pipeline outputs: bridges.jsonl, anomalies.jsonl
  - All 27 tests passing
- **Sprint 4**: COMPLETE - Outcome taxonomy extensions in `src/services/outcome_taxonomy.py`
  - Expert panel refinements applied (2026-01-18)
  - CNFA restructured to feature/percept/response/config hierarchy
  - ART constructs, prospect-refuge theory, contextual epistemic levels
  - Schema: `ae.extended_outcome_lookup.v2`
  - All 26 tests passing
- **Sprint 5**: COMPLETE - Persistence & accumulation in `src/services/web_persistence.py`
  - Expert panel refinements applied (2026-01-18)
  - Inverse-variance weighting (DerSimonian-Laird)
  - Conflict type categorization, coherence dashboard, paper quality weighting
  - Web snapshots for disaster recovery
  - All 31 tests passing
- **Sprint 6**: COMPLETE - Causal Structure & Scope Conditions in `src/services/web_of_belief.py`
  - Expert panel reviewed (2026-01-19)
  - CausalDirection enum (UNKNOWN, CORRELATIONAL, FORWARD, REVERSE, BIDIRECTIONAL, COMMON_CAUSE, MEDIATED)
  - ScopeConditions with scope_specified field (Panel Fix 3)
  - PRECISION_BOUNDARY conflict type
  - Mediator required for MEDIATED causal direction (Panel Fix 1)
  - 31 tests passing
- **Sprint 7**: COMPLETE - Environment Taxonomy in `src/services/environment_taxonomy.py`
  - Expert panel reviewed (2026-01-19)
  - Hierarchical taxonomy: spatial, natural, sensory, config, aesthetic (Panel Fix 4)
  - Synonym resolution and antonym detection
  - Antonym-aware conflict detection (antonym pairs with opposite effects = same finding)
  - Diversity index (0.6 * env_entropy + 0.4 * outcome_entropy)
  - 35 tests passing
- **Sprint 8**: COMPLETE - Multi-Theory & Validation in `src/services/validation.py`
  - Expert panel reviewed (2026-01-19)
  - Validation phases: ANNOTATION (10), CALIBRATION (20), LOO (30), BRIDGES (50)
  - Evidence clusters for same-study beliefs (prevent double-counting)
  - Ecological validity affects uncertainty, not credence (Panel Fix 5)
  - Coherence contribution metric for theoretical beliefs (Panel Fix 2)
  - 47 tests passing
- **Sprint 9**: COMPLETE - Gold Standard corpus in `src/services/gold_standard.py`
  - Corpus structure: `gold_standard/v1.0/` with manifest and annotations
  - Annotation schema: `gold_standard/v1.0/schema/annotation.schema.yaml`
  - Example annotations: kaplan_1989.yaml (ART theory), ulrich_1984.yaml (SRT empirical)
  - GoldStandardCorpus loader with theory/type filtering
  - ExtractionComparator with content similarity, credence range, level checking
  - Negative test validation (should_NOT_extract patterns)
  - 21 tests passing

## Quinean Commitment (Why This Matters)

This project uses **coherentist epistemology** (Quine's Web of Belief):
- Nothing is foundational—all beliefs are revisable
- Justification comes from coherence, not accumulation
- The BN (Bayesian Network) is a *derivative* of the web, not primary
- When evidence conflicts, ANY node can be revised (theory, auxiliary assumptions, measurement)
- Stubs = findings that don't fit current ontology (held, not forced or dropped)

## Architecture

```
PDF Corpus
    │
    ▼
EXTRACTION LAYER (Track A - Production)
├── app/tasks/pipeline.py          (Main extraction pipeline)
├── app/cli/article_eater_contract_cli.py
└── contracts/ae_af/schemas/       (Claim and rule schemas)
    │
    ▼
EPISTEMIC LAYER (Track B - Quinean Engine)
├── src/services/web_of_belief.py       (1300+ lines - THE key file)
├── src/services/extraction_to_web.py   (Sprint 1 mapper: claims→beliefs)
├── src/services/refined_epistemic.py   (Boghossian semantics, Glymour dependencies)
├── src/services/abstraction_levels.py  (Theory nesting, model zoom)
└── src/services/dual_epistemology.py   (Foundationalist vs coherentist comparison)
    │
    ▼
THEORY SYSTEM (Track C - Database)
├── src/services/theory_registry.py     (SQLite CRUD)
├── src/data/theory_bootstrap.py        (Initial theory population)
└── db/sql/017_theories.sql             (Schema)
    │
    ▼
OUTPUT
├── claims.jsonl, rules.jsonl           (Extraction output)
├── web_state.json                      (Web of belief state - Sprint 2)
├── stubs.jsonl, tensions.jsonl         (Epistemic diagnostics - Sprint 2)
└── bn_export/                          (BN-ready format - Sprint 7)
```

## Essential Files (Canonical Locations)

### PRIORITY 1 - Context & Planning
| File | Purpose |
|------|---------|
| `docs/ARCHITECTURE.md` | System architecture documentation |
| `docs/SPRINT_1_COMPLETION.md` | Sprint 1 summary and decision points |
| `docs/EXPERT_PANEL_SPRINT_2_3_REVIEW_2026_01_18.md` | Sprint 2 review + Sprint 3 specification request |
| `Project_Constitution.md` | Core project rules |

### PRIORITY 2 - Core Engine Code
| File | Purpose |
|------|---------|
| `src/services/web_of_belief.py` | Quinean coherentist engine (1300+ lines) |
| `src/services/extraction_to_web.py` | Sprint 1 mapper (claims→beliefs) |
| `src/services/bridge_warrants.py` | Sprint 3 bridge warrants (knowledge transfer) |
| `src/services/refined_epistemic.py` | Boghossian semantics, Glymour dependencies |
| `src/services/abstraction_levels.py` | Theory nesting, model zoom |

### PRIORITY 3 - Pipeline & Integration
| File | Purpose |
|------|---------|
| `app/tasks/pipeline.py` | Main extraction pipeline (Sprint 2 integration point) |
| `app/cli/article_eater_contract_cli.py` | CLI entry point |

### PRIORITY 4 - Schemas
| File | Purpose |
|------|---------|
| `contracts/ae_af/schemas/ae.claim.v1.schema.json` | Claim schema |
| `contracts/ae_af/schemas/ae.rule.v1.schema.json` | Rule schema |
| `contracts/vocab/outcome_lookup.json` | Outcome taxonomy |
| `contracts/vocab/environment_lookup.json` | Environment/tag taxonomy |

### PRIORITY 5 - Theory System
| File | Purpose |
|------|---------|
| `src/services/theory_registry.py` | SQLite theory storage |
| `src/data/theory_bootstrap.py` | Initial theory population |

## Key Directories

| Directory | Purpose |
|-----------|---------|
| `src/services/` | Core Python - epistemic engines |
| `app/tasks/` | Pipeline integration |
| `contracts/ae_af/` | Schemas for claims and rules |
| `docs/` | Architecture and planning docs |
| `quarantine/` | Obsolete files (never delete, always quarantine) |
| `governance_kit/` | Immutable governance files |
| `tests/` | Test files |

## Commands

```bash
# Run tests
pytest -q                                    # Quick test run
pytest tests/test_extraction_to_web.py -v   # Specific test file

# Linting (ruff configured in pyproject.toml)
ruff check .

# Environment setup
bash install_ae_envkit.sh                   # Install dependencies
bash doctor.sh                              # Verify installation

# Smoke test the pipeline
./bin/article_eater eat --in contracts/ae_af/examples/input_bundle_minimal --out /tmp/ae_out_example --profile standard --hitl auto

# Production verification
./bin/prod_smoke.sh
```

## Governance Rules (MUST FOLLOW)

1. **NO DELETIONS** - Move obsolete files to `quarantine/YYYY-MM-DD/`
2. **Governance kit is immutable** - Don't modify files listed in `release.keep.yml`
3. **Contract-first** - Schema changes require micro-contract updates in `contracts/`
4. **Date everything** - All docs get timestamps in filename AND header
5. **No bypass of release gates** - Run `./bin/prod_smoke.sh` before commits
6. **Descriptive names** - Never use generic filenames (always versioned + dated)

## Version Strategy

- **V20.8.0** = Legacy frozen release (reference baseline)
- **PostQuinean_v1** = Current release with Sprints 1-5 complete
- Aggressive version increments preferred
- Always create dated minimal ZIPs: `PostQuinean_v1_ESSENTIAL_2026_01_18.zip`

## Coding Conventions

- Python 3.11+ (see pyproject.toml)
- Type hints required
- Ruff for linting: `line-length = 100`, select `["E","F","I"]`
- Docstrings for public functions
- Tests in `tests/` directory

## Expert Panel (Constructed Voices)

For design decisions, convene these voices (constructed from their published work):
- **Dr. Judea Pearl** — Bayesian networks, causal inference
- **Dr. Nancy Cartwright** — Philosophy of science, bridge warrants
- **Dr. Herbert Simon** — Bounded rationality, system design
- **Dr. Marcia Bates** — Information science, knowledge organization
- **Dr. Rachel Kaplan** — Environmental psychology (the domain)

## Forbidden Operations

```bash
# NEVER run these
rm -rf, sudo, git reset --hard, git clean, curl | bash
```

## Decision Automation Preferences

Claude Code should assess risk and automate low-risk decisions while always asking for high-risk ones.

### ALWAYS PROCEED (No confirmation needed)
Low risk, easily reversible, or read-only:
- `ls`, `cat`, `head`, `tail`, `find`, `grep`, `du`, `wc` — read-only commands
- `git status`, `git diff`, `git log` — informational git commands
- `pwd`, `echo`, `which`, `type` — system info
- Reading any file in this repo
- `pytest`, `ruff check` — testing/linting (doesn't modify)

### PROCEED WITH SESSION PERMISSION (Ask once, then allow)
Medium risk, but within active work scope:
- File edits within this repo during housekeeping/development
- `git add`, `git commit` — tracked and reversible
- Creating new files in this repo
- Moving files within this repo (with git mv)
- `git rm --cached` — untracking files (doesn't delete)

### ALWAYS ASK (Never auto-approve)
High risk, destructive, or external:
- `rm`, `rm -rf` — deletion (use quarantine instead)
- `git reset --hard`, `git clean` — destructive git
- `git push` — external communication
- `sudo` anything
- `curl | bash`, `wget | bash` — external code execution
- Any command outside this repo
- Any command involving `/Downloads`, `/Desktop`, or `~` paths

**When in doubt, ASK.** David prefers occasional interruption over accidental damage.

### MULTI-CHOICE PROMPT BUG WORKAROUND

Claude Code has a known bug where option 2 sometimes references `/Downloads` or other wrong directories instead of the current repo.

**Rule**: When option 2 mentions a path OTHER than `/Users/davidusa/REPOS/Article_Eater_PostQuinean_v1`, NEVER choose it. Choose option 1 instead.

## Communication Style

David prefers:
- Clean academic writing (Bertrand Russell style)
- Thorough explanations over brevity
- Clear timestamps on everything
- Explicit about what's certain vs. uncertain
- APA citations with DOIs where relevant
- Descriptive versioned filenames (never generic names)

## Testing CLAUDE.md

Verify this file is working by asking:
1. "What should I do if I want to delete an old file?" → Move to quarantine/
2. "What's the current sprint status?" → Sprint 1 complete, Sprint 2 in progress
3. "Where is the Quinean engine?" → src/services/web_of_belief.py
4. "What's the canonical location of extraction_to_web.py?" → src/services/extraction_to_web.py
