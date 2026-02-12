# CLAUDE.md

*Last updated: Saturday, February 8, 2026 (V23.0.0 - Emergent Entrenchment)*

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Article Eater V23.0.0 (Post-Quinean) extracts evidence-backed rules from scientific articles for CNFA neuroarchitecture research. **Foundherentist epistemology** (Haack, 1993) now explicitly adopted: coherentist at core with soft epistemic level constraints. V23.0.0 makes entrenchment emergent from web structure per panel consultation (Quine, Haack, Thagard).

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
- **Sprint 1.5**: COMPLETE - Epistemic-Causal Integration (2026-02-08)
  - Bridges Quinean epistemic layer with Pearlian causal inference
  - Van Fraassen contrast classes for population-relative meaning
  - New module: `src/services/epistemic_causal_bridge.py` (~2000 lines)
  - Key classes: `EpistemicCausalBridge`, `ContrastClass`, `PopulationContext`
  - Five influence pathways: Level→Confidence, Entrenchment→Robustness, Arguments→Contrast, Coherence→Admissibility, Meta-uncertainty→Propagation
  - WebOfBelief new methods: `create_causal_bridge()`, `counterfactual()`, `causal_bridge_available()`
  - Panel resolutions: Entrenchment decomposition, temporal dynamics, coherence caching
  - 34 tests passing
- **Sprint 2.5**: COMPLETE - Social Epistemology (2026-02-08)
  - Scientific knowledge is produced by communities, not isolated individuals
  - New module: `src/services/social_epistemology.py` (~1300 lines)
  - Schema: `contracts/schemas/social_epistemology.schema.json`
  - Key classes: `EpistemicCommunity`, `BeliefProvenance`, `ContestationTracker`, `MethodologicalDiversityAssessor`, `CommunityRegistry`
  - Panel P-SE consulted (Longino, Kitcher, Knorr Cetina, Collins, Kuhn)
  - SE-1: Community identification by theory (0.35), exemplars (0.25), methods (0.25), citations (0.15)
  - SE-2: Report disagreement by default; average only for empirical within-paradigm
  - SE-3: Track power separately from credence; use domain-specific track record
  - SE-4: Snapshot-based history with event annotations
  - SE-5: Three-tier hierarchy (Field > Paradigm > Lab)
  - WebOfBelief Belief class extended: `provenance`, `community_associations`, `get_community_credence()`, `is_community_contested()`
  - Seed data: ART, SRT, Biophilia, Environmental Psychology communities
  - 54 tests passing

## Foundherentist Epistemology (V23.0.0)

This project uses **foundherentism** (Haack, 1993) with Quinean inspiration:
- Coherentist at core—justification comes from mutual support, not accumulation
- **Soft** epistemic level constraints—theoretical beliefs naturally more entrenched, but not foundational
- The BN (Bayesian Network) is a *derivative* of the web, not primary
- **V23.0.0 BREAKING CHANGE**: Entrenchment is now **emergent**, computed from:
  - 40% connectivity (constraint count)
  - 30% epistemic level weight (THEORETICAL=0.8, EMPIRICAL=0.3, etc.)
  - 30% coherence contribution (credence + status)
- This is NOT pure Quine (foundationalism through the back door was fixed) but explicit foundherentism
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
├── src/services/web_of_belief.py       (1900+ lines - THE key file)
├── src/services/extraction_to_web.py   (Sprint 1 mapper: claims→beliefs)
├── src/services/refined_epistemic.py   (Boghossian semantics, Glymour dependencies)
├── src/services/abstraction_levels.py  (Theory nesting, model zoom)
└── src/services/dual_epistemology.py   (Foundationalist vs coherentist comparison)
    │
    ▼
CAUSAL LAYER (Track B.1 - Epistemic-Causal Bridge, Sprint 1.5)
├── src/services/epistemic_causal_bridge.py  (2000+ lines - Quinean→Pearlian)
│   ├── EpistemicCausalBridge       (Main orchestration)
│   ├── ContrastClass               (Van Fraassen contrast specification)
│   ├── PopulationContext           (Baseline-dependent meaning)
│   └── MultiTheoryModel            (Per-theory structural equations)
└── WebOfBelief.counterfactual()    (Convenience method)
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

## Security Model (Local Research Tool)

**Deployment Model**: This system is designed as a **local-only research tool** (Model A per panel review).

### Write Endpoint Authorization

Write endpoint policy currently differs by surface:
1. `/api/v1/ingestion/*` is still local-first and unauthenticated.
2. Key/profile/admin routes (`/profile/api-keys/*`, `/profile/keys`, `/profile`, `/admin`, `/admin/stats`, `/usage/admin/summary`, `/api/v1/web/admin/*`) require `X-Admin-Token` (`AE_ADMIN_TOKEN`).
3. Public/network deployment still requires full auth hardening across all write/admin surfaces.

### Production Exposure Warning

**DO NOT expose this API to public networks without adding authentication.**

If network exposure is required:
1. Add `Depends(get_current_user)` to write endpoints
2. Implement proper API key validation
3. Consider rate limiting
4. Review CORS configuration for your deployment

### CORS Configuration

CORS is configured for specific origins (localhost dev servers + production domain).
The wildcard `"*"` origin is **not used** when `allow_credentials=True` per security best practices (fixed 2026-01-22).

## Task Coordination (Parallel Terminals)

**Before starting ANY task**, check `ACTIVE_TASKS.md` to see what's claimed by other terminals.

| File | Purpose |
|------|---------|
| `ACTIVE_TASKS.md` | Real-time task claims (who's working on what NOW) |
| `TASKS.md` | Full task history and project backlog |
| `PARALLEL_WORK.md` | File ownership for lane-based work |

**Protocol**: Check in → Claim task → Work → Check out → Update TASKS.md

See root `/Users/davidusa/REPOS/CLAUDE.md` for full check-in/check-out protocol.

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
| `src/services/web_of_belief.py` | Quinean coherentist engine (1900+ lines) |
| `src/services/epistemic_causal_bridge.py` | Sprint 1.5 Quinean→Pearlian bridge (2000+ lines) |
| `src/services/social_epistemology.py` | Sprint 2.5 community-relative credence (1300+ lines) |
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
| `contracts/schemas/social_epistemology.schema.json` | Sprint 2.5 social epistemology schema |
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
pytest -q                                    # Quick test run (discovery constrained to tests/ via pytest.ini)
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
- **V21.0.0** = Post-Quinean initial release (Sprints 1-9)
- **V22.0.0** = Sprint F panel validation + Phase 1 security fixes + GUI/UX review
- **V22.1.0** = Sprint 2.5 Social Epistemology + Strategic TODOs 1-3
- **V23.0.0** = Current release (Emergent Entrenchment - BREAKING CHANGE)
- **PostQuinean_v1** = Repo branch name (first Quinean architecture iteration)
- Aggressive version increments preferred
- Always create dated minimal ZIPs: `PostQuinean_v1_ESSENTIAL_2026_02_08.zip`

### V23.0.0 Changelog (2026-02-08) **BREAKING CHANGE**
- **Entrenchment is now emergent, not settable** (Panel consultation: Quine, Haack, Thagard)
- `Belief.entrenchment` field removed → use `WebOfBelief.get_entrenchment(belief_id)`
- Thagard formula: 40% connectivity + 30% level_weight + 30% coherence_contrib
- Lazy caching with invalidation on constraint changes (Simon)
- Philosophy clarified: **Foundherentism** (Haack), not pure Quinean coherentism
- Fixed bugs from ChatGPT ruthless review:
  - Constraint index purge bug in `scalable_coherence.py`
  - Boundary status staleness after removals
  - Decision semantics mismatch in `credibility_testing.py` (ACCEPT default for clean reports)
- New tests: `tests/test_scalable_coherence_benchmark.py` (8 tests)
- Panel documentation: `docs/PANEL_CONSULTATION_ENTRENCHMENT_2026-02-08.md`

### V22.1.0 Changelog (2026-02-08)
- Sprint 2.5 Social Epistemology complete (P-SE panel consulted)
- New module: `src/services/social_epistemology.py` (~1300 lines, 54 tests)
- Community-relative credence, contestation tracking, methodological diversity assessment
- WebOfBelief extended with provenance and community associations
- TODO 1: Credibility Testing enhancements (feedback module, semantic coherence)
- TODO 2: Interpretive Intelligence enhancements (MECHANISM + DISAGREEMENT patterns)
- TODO 3: VOI-Driven Search enhancements (cross-field vocabulary)
- Panels P-TC and P-QW consulted

### V22.0.0 Changelog (2026-01-22)
- Sprint F panel validation (16 experts)
- Phase 1 security fixes (CORS, router wiring test, auth documentation)
- GUI/UX ruthless review with AI-enhanced UX recommendations
- Version alignment across all source files

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

### Extended Panel (Task Context & Cognitive Work)
For task-related decisions, also include:
- **Dr. Gary Klein** — Naturalistic Decision Making, expertise in context
- **Dr. K. Anders Ericsson** — Deliberate practice, skill acquisition
- **Dr. Daniel Kahneman** — System 1/2, cognitive load, attention
- **Dr. Lucy Suchman** — Situated action, ecological validity

## Decision Tracking & Panel Consultation (MANDATORY)

**This workflow is REQUIRED for all implementation work.** Claude Code MUST follow this process.

### Step 1: Track Decisions As You Work

During implementation, record every non-trivial decision in WHERE_WE_STAND.md under "Implementation Decisions Pending Panel Review":

```markdown
| ID | Decision | Context | Alternatives Considered | Risk Level |
|----|----------|---------|------------------------|------------|
| D1 | [What you decided] | [Why it came up] | [Other options] | Low/Med/High |
```

**What counts as a decision:**
- Default values or thresholds chosen
- Data structure choices
- Algorithm selections
- Confidence scoring approaches
- Fallback behaviors
- Edge case handling
- Anything where reasonable alternatives exist

### Step 2: Trigger Panel Consultation

Invoke the expert panel when ANY of these conditions are met:
1. **Decision count ≥ 5** — Accumulated enough decisions to warrant review
2. **Sprint boundary** — Before starting a new sprint
3. **High-risk decision** — Any single decision with significant architectural impact
4. **User request** — David asks for panel review
5. **Uncertainty** — You're genuinely unsure about a decision

### Step 3: Panel Consultation Format

When consulting the panel, use this structure:

```markdown
## Panel Consultation: [Topic]
**Date**: [YYYY-MM-DD]
**Decisions Under Review**: D1, D2, D3...

### Decision D1: [Title]
**Context**: [Why this decision arose]
**Current Choice**: [What was implemented]
**Alternatives**: [Other options considered]
**Risk**: [What could go wrong]

[Repeat for each decision]

---

## Panel Responses

### Dr. [Name] ([Expertise]):
[Constructed response based on their published work and methodology]

[Repeat for each relevant panelist]

---

## Synthesis & Resolutions
| Decision | Panel Verdict | Action Required |
|----------|---------------|-----------------|
| D1 | Approved / Revise / Defer | [Specific action if any] |
```

### Step 4: Record Outcomes

After panel consultation:
1. Update WHERE_WE_STAND.md — Mark decisions as "Panel Approved" or note required changes
2. Update CLAUDE.md sprint status — If significant, add to changelog
3. Create dated panel doc — `docs/PANEL_CONSULTATION_[TOPIC]_[DATE].md`
4. Clear the pending decisions table — Move reviewed decisions to "Resolved" section

### Enforcement

**Claude Code MUST NOT proceed past a sprint boundary without panel consultation.**

If decision count reaches 5+ during implementation:
1. Pause implementation
2. Notify user: "I've accumulated [N] implementation decisions that warrant panel review."
3. Offer to conduct panel consultation before continuing

### Decision Tracking Location

Primary tracking file: `/Users/davidusa/REPOS/Outcome_Contractor/WHERE_WE_STAND.md`

Section: "Implementation Decisions Pending Panel Review"

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
