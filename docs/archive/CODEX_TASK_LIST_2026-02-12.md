# Codex Task List

**Date**: 2026-02-12
**Task List ID**: CODEX-TASKS-2026-02-12
**Repos**: Article_Eater_PostQuinean_v1, BN_graphical

---

## MASTER PROMPT FOR CODEX

```
You are Codex, working on the Article_Eater + BN_graphical system for Professor David Kirsh at UCSD Cognitive Science.

YOUR TASK LIST IS IN THIS FILE. Execute tasks in order starting with TASK-0.

REPO LOCATIONS:
- Article_Eater: /Users/davidusa/REPOS/Article_Eater_PostQuinean_v1
- BN_graphical: /Users/davidusa/REPOS/BN_graphical

KEY CONTEXT FILES (read these first):
1. /Users/davidusa/REPOS/CLAUDE.md (root governance)
2. /Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/CLAUDE.md (project details)
3. /Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/docs/CODEX_TASK_LIST_2026-02-12.md (this file - your task list)

Work through tasks sequentially. For each task:
1. Read the task specification completely
2. Execute the task thoroughly
3. Document your findings/outputs as specified
4. Mark the task complete with date and summary
5. Move to next task

Be ruthless. Be thorough. The professor wants real critique, not politeness.

START WITH TASK-0 NOW.
```

---

## TASK-0: Ruthless System Evaluation (PRIORITY: CRITICAL)

**Status**: [ ] PENDING
**Output**: `docs/CODEX_EVALUATION_REPORT_2026-02-12.md`

### Objective
Conduct a comprehensive, ruthless code review of the entire Article_Eater + BN_graphical system. Identify every flaw, every anti-pattern, every security hole.

### System Overview

You are evaluating **two interconnected repositories**:

**Repository 1: Article_Eater_PostQuinean_v1**
- Purpose: Extract evidence-backed causal rules from scientific papers using foundherentist (Quinean/Haack) epistemology
- Core engine: `src/services/web_of_belief.py` (1900+ lines)
- Causal bridge: `src/services/epistemic_causal_bridge.py` (2000+ lines)
- Gap detection: `src/services/gap_predictor.py`
- Edge justification: `src/services/edge_justification.py`
- Persistence: `src/services/web_persistence.py` (SQLite)

**Repository 2: BN_graphical**
- Purpose: React/TypeScript frontend for Bayesian network visualization
- Main view: `src/components/CausalGraphView.tsx`
- API integration: `src/services/api.ts`

**Integration Points (INT-1 through INT-6)**:
- INT-1: Edge Justification - BN edges get epistemic support from web
- INT-2: Gap Prediction - VOI-prioritized knowledge gaps
- INT-3: Evidence Panel - Click edge → see supporting papers
- INT-4: Web Visualization - Epistemic web as graph
- INT-5: Cross-Layer Query - Query across epistemic levels
- INT-6: User Modes - Expert vs novice interface

### Evaluation Dimensions

Score each dimension 1-10 with detailed justification:

#### 1. ARCHITECTURE (30% weight)
- Is the 12-layer architecture (Attribute→Mediator→Outcome) sound?
- Is the epistemic-causal bridge (Quinean→Pearlian) coherent?
- Are there circular dependencies?
- Is separation of concerns clear?
- Does the integration between repos make sense?
- Are there architectural anti-patterns?

#### 2. CODE QUALITY (25% weight)
- Code smells? Dead code? Copy-paste violations?
- Error handling consistent and thorough?
- Obvious bugs or race conditions?
- Maintainability - could a new developer understand it?
- Magic numbers or hardcoded values?
- Naming consistency?

#### 3. SECURITY (15% weight)
- Injection vulnerabilities (SQL, command, XSS)?
- Authentication/authorization properly implemented?
- Secrets properly managed?
- OWASP Top 10 violations?
- Input validation adequate?

#### 4. TESTING (15% weight)
- Test coverage? Critical paths tested?
- Integration tests for API endpoints?
- Edge cases covered?
- Tests maintainable or brittle?
- Tests for repo integration?

#### 5. DOCUMENTATION (10% weight)
- System understandable from docs alone?
- APIs documented (OpenAPI/Swagger)?
- Epistemological foundations explained?
- Developer onboarding docs?

#### 6. SCALABILITY (5% weight)
- Handle thousands of papers?
- Obvious performance bottlenecks?
- SQLite appropriate or need PostgreSQL?
- N+1 query problems?

### Files to Examine

**Article_Eater - Core Engine**:
```
src/services/web_of_belief.py        # 1900+ lines - THE key file
src/services/epistemic_causal_bridge.py  # 2000+ lines - Quinean→Pearlian
src/services/gap_predictor.py        # Gap detection + VOI
src/services/edge_justification.py   # BN-Web bridge
src/services/cross_layer_query.py    # Cross-level queries
src/services/web_persistence.py      # SQLite persistence
src/services/belief_validator.py     # NEW - canonical ID validation
```

**Article_Eater - API Layer**:
```
app/main.py                          # App wiring
app/routes/integration.py            # Integration endpoints
app/routes/ingestion.py              # Paper ingestion
```

**Article_Eater - Tests**:
```
tests/test_gap_predictor.py
tests/test_edge_justification.py
tests/test_int_pipeline.py
```

**BN_graphical - Frontend**:
```
frontend-v2/src/features/explorer/CausalGraphView.tsx
frontend-v2/src/features/explorer/EvidencePanel.tsx
frontend-v2/src/lib/api-client.ts
frontend-v2/src/features/explorer/WebView.tsx
```

**Configuration**:
```
CLAUDE.md                            # System documentation
contracts/ae_af/schemas/*.json       # Data contracts
config/app.policy.json               # Security policy
```

### Known Technical Debt (verify these still exist)
1. Ingestion endpoint returns 405 (not wired correctly)
2. Hot reload not implemented (requires server restart)
3. Some duplicate Operation IDs in FastAPI routes
4. SQLite might not scale beyond ~10K papers

### Output Format

Create `docs/CODEX_EVALUATION_REPORT_2026-02-12.md` with:

```markdown
# Codex System Evaluation Report

**Date**: 2026-02-12
**Evaluator**: Codex
**Task ID**: CODEX-TASKS-2026-02-12/TASK-0

## Executive Summary
[2-3 paragraphs: Overall assessment, biggest concerns, biggest strengths]

## Critical Issues (Must Fix)
[Numbered list with file:line references]

## Major Issues (Should Fix)
[Numbered list with file:line references]

## Minor Issues (Nice to Fix)
[Numbered list]

## Architecture Assessment
[Detailed analysis]

## Scores

| Dimension | Score | Justification |
|-----------|-------|---------------|
| Architecture | ?/10 | ... |
| Code Quality | ?/10 | ... |
| Security | ?/10 | ... |
| Testing | ?/10 | ... |
| Documentation | ?/10 | ... |
| Scalability | ?/10 | ... |
| **OVERALL** | ?/10 | ... |

## Recommended Refactors (Priority Order)
[Numbered list]

## Questions for Developer
[Things needing clarification]
```

### How to Run Tests/Verification

```bash
# Article_Eater
cd /Users/davidusa/REPOS/Article_Eater_PostQuinean_v1
source venv/bin/activate
pytest -v
ruff check .

# Start server and test endpoints
python -m uvicorn app.main:app --port 8001
curl http://localhost:8001/api/v1/integration/health
curl http://localhost:8001/api/v1/integration/gaps

# BN_graphical
cd /Users/davidusa/REPOS/BN_graphical
npm install
npm test
npm run build
```

---

## TASK-1: Fix Critical Issues from Evaluation

**Status**: [ ] PENDING (depends on TASK-0)
**Output**: Commits with fixes, update to `TASKS.md`

After TASK-0, fix all CRITICAL issues identified. Document each fix.

---

## TASK-2: Fix Major Issues from Evaluation

**Status**: [ ] PENDING (depends on TASK-1)
**Output**: Commits with fixes

Fix MAJOR issues in priority order.

---

## TASK-3: Integration Test Suite

**Status**: [ ] PENDING
**Output**: `tests/test_full_integration.py`

Create comprehensive integration tests that:
1. Start Article_Eater API
2. Verify all endpoints respond correctly
3. Test the full gap → evidence → belief cycle
4. Test cross-repo integration (if BN_graphical has test mode)

---

## TASK-4: Documentation Audit

**Status**: [ ] PENDING
**Output**: Updated docs, new onboarding guide

1. Verify all public APIs are documented
2. Create developer onboarding guide
3. Document the epistemological foundations for non-philosophers
4. Ensure CLAUDE.md is current

---

## TASK-5: Performance Profiling

**Status**: [ ] PENDING
**Output**: `docs/PERFORMANCE_REPORT_2026-02-12.md`

1. Profile key operations with 100, 1000, 10000 beliefs
2. Identify bottlenecks
3. Recommend optimizations
4. Assess SQLite vs PostgreSQL decision

---

## TASK-6: Security Hardening

**Status**: [ ] PENDING
**Output**: Security fixes, updated policy

Based on TASK-0 security findings:
1. Fix any injection vulnerabilities
2. Implement proper input validation
3. Review authentication requirements
4. Update security documentation

---

## Progress Tracking

Update this section as you complete tasks:

| Task | Status | Completed | Summary |
|------|--------|-----------|---------|
| TASK-0 | PENDING | - | - |
| TASK-1 | PENDING | - | - |
| TASK-2 | PENDING | - | - |
| TASK-3 | PENDING | - | - |
| TASK-4 | PENDING | - | - |
| TASK-5 | PENDING | - | - |
| TASK-6 | PENDING | - | - |

---

## Context: Philosophical Foundation

This system implements **foundherentism** (Susan Haack, 1993):
- Coherentist at core: justification from mutual support
- Soft epistemic level constraints: theory naturally more entrenched
- The BN is DERIVATIVE of the epistemic web, not primary
- Entrenchment is EMERGENT (computed from connectivity, level, coherence)

**Domain**: Built environment psychology - how physical spaces affect human cognition, mood, stress, productivity.

**Expert Panel**: Design decisions reviewed by constructed voices:
- Judea Pearl (causal inference)
- Susan Haack (foundherentism)
- Herbert Simon (bounded rationality)
- Nancy Cartwright (causation philosophy)
- Rachel Kaplan (environmental psychology)

---

## Contact

Questions go to Professor David Kirsh, UCSD Cognitive Science.
Report issues via commits and documentation updates.
