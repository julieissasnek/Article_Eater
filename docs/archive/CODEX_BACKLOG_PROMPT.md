# CODEX BACKLOG COMPLETION PROMPT
## February 18, 2026

You are a Codex agent assigned to complete the remaining backlog tasks for Article_Eater_PostQuinean_v1.

---

## PARALLEL EXECUTION PROTOCOL

Multiple Codex instances may run simultaneously. **You MUST claim tasks before working.**

### Check-In (Before Starting Any Task)

1. Read `ACTIVE_TASKS.md` in repo root
2. Pick an **unclaimed** task from the list below
3. Add your claim to `ACTIVE_TASKS.md`:
   ```
   | TASK_ID | Description | CODEX-{timestamp} | {now} | IN_PROGRESS | Starting |
   ```
4. Begin work

### Check-Out (When Done)

1. Move your row from "Active Claims" to "Completed Today" in `ACTIVE_TASKS.md`
2. Append to `docs/DONE.md`:
   ```
   TASK_ID DONE [Codex] YYYY-MM-DDTHH:MM
   ```
3. Pick next unclaimed task

### Conflict Resolution

- If a task is claimed for >2 hours with no file changes, you may reclaim it
- If you get blocked, note the blocker in ACTIVE_TASKS.md and move to another task

---

## TASK LIST

### PRIORITY 1: Sprint D Completion (if AG hasn't done these)

| ID | Task | Context Files | Notes |
|----|------|---------------|-------|
| D.11 | Web of Belief Rebuild | `src/services/web_of_belief.py`, `data/web_persistence.db`, `data/production/structured_claims_codex_semantic.json` | Replace garbage web with clean claims. Produce `docs/web_health_report_post_rebuild.md`. See `docs/SprintD_Data_Remediation.md` lines 912-974 for full spec. |
| D.13 | Sprint D Validation | All Sprint D outputs in `data/production/`, `data/gold_standard/` | Final validation report. Compare extraction accuracy, web health before/after. See `docs/SprintD_Data_Remediation.md` lines 976-1000. |

---

### PRIORITY 2: Sprint 10 Residuals

| ID | Task | Context Files | Notes |
|----|------|---------------|-------|
| 1.1 | Enum Drift Fix | `scripts/check_enum_drift.py`, `src/epistemic/schema.py` | Run `python scripts/check_enum_drift.py` to identify drift. Fix deprecated enum values across codebase. |
| 1.3 | Load Staging Theory-Links | `src/cmr/models.py`, `data/templates/*.json` | Load theory links from template JSONs into staging tables. See template `causal_links` field. |
| 1.4 | WIS Conversion Module | `src/extraction/effect_size_converter.py` | WIS = Within-study Information Score. Add conversion utilities if not present. Check if D.8 already covers this. |

---

### PRIORITY 3: Enum Drift Fixes (Phase C)

These are enum standardization fixes in external/legacy code.

| ID | Task | File | Fix |
|----|------|------|-----|
| 1.5.C2a | ClaimType aliases | `article_decomposer.py` | `boundary`→`moderated`, `effect`→`causal`, `mechanism`→`mechanistic`, `null_result`→`null`, `replication`→`descriptive` |
| 1.5.C2b | EvidenceType alias | `enhanced_edge.py` | `empirical` → `observational` |
| 1.5.C2d | CI Shape schema | `contracts/bn.api.v2.schema.json` | Migrate to `{ci_lower, ci_upper}` object format |
| 1.5.C3a | ArticleTypeCrosswalk | `article_extraction_contracts.py` | Replace 8 deprecated values with canonical equivalents |
| 1.5.C3b | ArticleTypeCrosswalk | `article_type_classifier.py` | Replace 8 deprecated values with canonical equivalents |

**Context:** Canonical enum values are defined in `src/epistemic/schema.py`. Use `scripts/check_enum_drift.py` to verify fixes.

---

### PRIORITY 4: Panel Recommendations

| ID | Task | Context | Notes |
|----|------|---------|-------|
| EC-1 | Thagard two-layer architecture docs | `src/services/epistemic_causal_integration.py` | Document the explanatory coherence layer. Output: `docs/architecture/thagard_two_layer.md` |
| EC-3 | Cartwright scope metadata | `src/epistemic/schema.py`, Belief dataclass | Add boundary condition fields to Belief. Fields: `scope_population`, `scope_context`, `scope_temporal` |
| SY-9 | Chang belief value analysis | `src/services/web_of_belief.py` | Already has `belief_value()` method. Document usage and add examples to `docs/belief_value_analysis.md` |

---

### PRIORITY 5: Architectural Tasks (Lower Priority)

These can be deferred but are good cleanup items.

| ID | Task | Context | Notes |
|----|------|---------|-------|
| ARCH-2a | Transportability analysis | `src/services/epistemic_causal_bridge.py` | Pearl/Bareinboim selection diagrams. Theoretical. |
| ARCH-3a | Lab/institution tracking | `src/epistemic/schema.py` Belief class | Add `source_lab`, `source_institution` fields |
| ARCH-3b | Independence scoring | `src/services/web_of_belief.py` | Score: lab × method × population diversity |
| ARCH-5d | Break up web_of_belief.py | `src/services/web_of_belief.py` (2000+ lines) | Split into <500 line modules |
| ARCH-6b | Severity computation | Mayo's severe testing | Add `compute_severity()` to Belief |

---

### PRIORITY 6: Admin/API (Deferred)

These are nice-to-have features, not blocking.

| ID | Task | Notes |
|----|------|-------|
| 3.0.5-A | Admin dashboard | Streamlit page at `streamlit_app/pages/admin.py` |
| 3.0.5-B | Belief inspector | Browse, search, filter beliefs |
| 3.0.5-C | Constraint viewer | Network visualization |
| ATK-2 | Attack pattern extraction | Add argument attack patterns to claim extraction |
| ATK-4 | Attack review UI | Streamlit page for reviewing detected attacks |

---

## KEY FILE LOCATIONS

| Purpose | Path |
|---------|------|
| Enum definitions | `src/epistemic/schema.py` |
| Web of belief engine | `src/services/web_of_belief.py` |
| Causal bridge | `src/services/epistemic_causal_bridge.py` |
| Claim extraction | `src/extraction/claim_extractor.py` |
| Effect size converter | `src/extraction/effect_size_converter.py` |
| Template computations | `src/cmr/template_computations.py` |
| CMR models | `src/cmr/models.py` |
| Templates JSON | `data/templates/*.json` |
| Production data | `data/production/` |
| Gold standard | `data/gold_standard/` |
| Sprint D spec | `docs/SprintD_Data_Remediation.md` |
| Enum drift checker | `scripts/check_enum_drift.py` |
| Tests | `tests/` |

---

## DECISIONS NEEDED (Flag for David)

These tasks require human decision before proceeding:

| ID | Question | Options |
|----|----------|---------|
| 1.5.C1a | GapType unknown values | `coverage`, `neural`, `theory` not in canonical. (a) add to canonical, (b) map to existing, (c) remove |
| 1.5.C2c | EvidenceType unknown values | `direct`, `indirect`, `meta`, `review` not canonical. (a) add to canonical, (b) map |

If you encounter these, document your recommendation in `docs/DECISIONS.md` and proceed with option (b) mapping as default.

---

## COMPLETION TRACKING

When done with ALL tasks:
1. Update `TASKS.md` to mark items complete
2. Run `python scripts/check_enum_drift.py` to verify no drift remains
3. Run `pytest tests/` to verify no regressions
4. Create `docs/BACKLOG_COMPLETION_REPORT.md` summarizing what was done

---

## BLANKET PERMISSIONS

- Create, modify, delete files as needed
- Run tests, scripts, code
- Make decisions and document in `docs/DECISIONS.md`
- Do NOT ask for confirmation — just do the work
- Do NOT stop until blocked or complete

---

## QUICK START

```bash
# 1. Check what's already claimed
cat ACTIVE_TASKS.md

# 2. Claim your first task (edit ACTIVE_TASKS.md)

# 3. Run enum drift check to understand current state
python scripts/check_enum_drift.py

# 4. Start with Priority 1 or 2 tasks first

# 5. When done, mark in DONE.md and pick next task
```

Good luck!
