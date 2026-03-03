# Smart Book System: Complete Index

**Created**: March 3, 2026
**Version**: 1.0
**Status**: Operational and Ready for Integration

---

## Quick Navigation

### I Want To...

| Goal | Read | Run |
|------|------|-----|
| **Understand WHY this exists** | [SMART_BOOK_DESIGN_2026-03-03.md](docs/SMART_BOOK_DESIGN_2026-03-03.md) | — |
| **Learn HOW to use it** | [SMART_BOOK_README.md](docs/SMART_BOOK_README.md) | — |
| **Get it set up** | [SMART_BOOK_INTEGRATION_GUIDE_2026-03-03.md](docs/SMART_BOOK_INTEGRATION_GUIDE_2026-03-03.md) | — |
| **Check my docs** | — | `python scripts/validate_master_doc.py --mode=validate` |
| **Generate a report** | — | `python scripts/validate_master_doc.py --mode=report` |
| **See suggestions** | — | `python scripts/validate_master_doc.py --mode=suggest` |
| **Understand the manifest** | [SMART_BOOK_README.md (Manifest Structure)](docs/SMART_BOOK_README.md#dependency-manifest-structure) | Look at `docs/master_doc_parts/DEPENDENCY_MANIFEST.json` |
| **Add a new concept** | [SMART_BOOK_README.md (Maintenance)](docs/SMART_BOOK_README.md#maintenance-workflow) | Edit `DEPENDENCY_MANIFEST.json` |
| **Update a concept** | [SMART_BOOK_README.md (Maintenance)](docs/SMART_BOOK_README.md#when-updating-an-existing-concept) | Edit `DEPENDENCY_MANIFEST.json` |

---

## The Five Deliverables

### 1. Design Document (21 KB)
**File**: `docs/SMART_BOOK_DESIGN_2026-03-03.md`

The "why" and "how" at a conceptual level.

**Contains**:
- Executive summary
- Problem motivation (T1.5 count inconsistencies)
- Precedents from other fields (literate programming, Sphinx, knowledge graphs)
- System architecture and components
- Dependency types explained
- Maintenance protocols
- Integration strategies
- Future extensions (genealogy, cross-repo, panelist review, queries)
- References and citations

**Read if**: You want to understand the philosophical and technical foundations.

**Time**: 30–45 minutes

---

### 2. User Guide / README (13 KB)
**File**: `docs/SMART_BOOK_README.md`

The "how" for day-to-day operations.

**Contains**:
- Quick start (30 seconds)
- What the validator checks (5 validation types)
- Manifest structure (JSON walkthrough)
- Maintenance workflows (add/update/supersede)
- Integration options (pre-commit, CI/CD, reflexes)
- Validation patterns (regex examples)
- Current violations found
- FAQ and troubleshooting
- Version history and future work

**Read if**: You need to understand how to use the system in practice.

**Time**: 20–30 minutes

---

### 3. Integration Guide (10 KB)
**File**: `docs/SMART_BOOK_INTEGRATION_GUIDE_2026-03-03.md`

The "when" and "what next."

**Contains**:
- Immediate actions (this week)
- Short-term setup (this month) with 3 options:
  - Pre-commit hook (prevents bad commits)
  - CI/CD integration (GitHub Actions, etc.)
  - Manual validation (run before committing)
- Medium-term maintenance (ongoing)
- Long-term vision (Phase 2–5)
- Common scenarios with step-by-step instructions
- Troubleshooting
- Success metrics

**Read if**: You're responsible for integrating Smart Book into the workflow.

**Time**: 15–20 minutes

---

### 4. Dependency Manifest (29 KB)
**File**: `docs/master_doc_parts/DEPENDENCY_MANIFEST.json`

The machine-readable specification of all concepts and dependencies.

**Contains**:
- Document metadata (version, dates, counts)
- 10 core concepts:
  1. T1_5_COUNT (canonical value: 13)
  2. CREDENCE_FORMULA_LOGODDS (current four-factor formula)
  3. CREDENCE_FORMULA_LEGACY (deprecated three-factor)
  4. WARRANT_TYPES (7 types with transfer reliabilities)
  5. AESHI_SCORING (5-dimension system)
  6. Q_NORMS (7 quality standards)
  7. EPISTEMIC_LEVELS (4-level hierarchy)
  8. WARRANT_STRENGTH_ω (assessment method)
  9. POPULATION_TRANSFER_δ (assessment method)
  10. CREDENCE_CALCULUS_INTEGRATION (architectural note)
- Section dependencies (which sections DEFINE, USE, EXTEND, SUPERSEDE)
- Dependency types (definitions)
- Consistency rules (5 automated rules)
- Validation patterns (regex for finding references)
- Maintenance log

**Edit if**: You're adding/updating concepts or changing section dependencies.

**Time to read**: 10 minutes (skim) or 30 minutes (detailed)

---

### 5. Validation Script (21 KB, executable)
**File**: `scripts/validate_master_doc.py`

The automated consistency checker.

**Features**:
- Loads manifest
- Discovers all PART_*.md files (21 parts)
- Scans for concept references
- 5 validation types:
  1. Numeric constants matching across sections
  2. Stale references to deprecated concepts
  3. Undefined concept references
  4. Sections needing review after concept updates
  5. Missing critical concepts
- 3 modes: validate, report, suggest
- Color-coded output
- Markdown report export

**Run**:
```bash
python scripts/validate_master_doc.py --mode=validate    # Quick check
python scripts/validate_master_doc.py --mode=report      # Full report
python scripts/validate_master_doc.py --mode=suggest     # Recommendations
```

**Time to run**: 3–5 seconds

---

## Current Validation Status

Running `validate_master_doc.py` on the current documentation found:

### CRITICAL (Must Fix)
```
PART_VII_T15_REDUCTIONS: "1 T1.5 theory" should be "13 T1.5 theories"
PART_VII_T15_REDUCTIONS: "22 T1.5 theories" should be "13 T1.5 theories"
```

### MEDIUM (Review Required)
```
T1_5_COUNT updated 2026-02-27
  → Check sections: §35, §40, §54, §78, §100, §115, §142, §147

CREDENCE_FORMULA_LOGODDS updated 2026-02-27
  → Check sections: §48A, §49, §50, §51, §52, §53, §54
```

---

## File Structure

```
Article_Eater_PostQuinean_v1/
├── SMART_BOOK_INDEX_2026-03-03.md               ← You are here
│
├── docs/
│   ├── SMART_BOOK_DESIGN_2026-03-03.md          ← Why & how (architecture)
│   ├── SMART_BOOK_README.md                     ← How (user guide)
│   ├── SMART_BOOK_INTEGRATION_GUIDE_2026-03-03.md ← When & next steps
│   │
│   └── master_doc_parts/
│       ├── DEPENDENCY_MANIFEST.json             ← Machine-readable spec
│       ├── PART_I_EXPLANATION_GAP.md
│       ├── PART_II_THEORETICAL.md
│       ├── PART_III_PREDICTION.md
│       ├── PART_IV_CREDENCE.md
│       ├── ... (17 more PART files)
│       └── PART_XXI_SOURCE_INDEX.md
│
└── scripts/
    └── validate_master_doc.py                   ← Validation script
```

---

## Getting Started: 3 Paths

### Path A: Quick Start (15 Minutes)
**Goal**: See if the system works

1. Read this file (2 min)
2. Run: `python scripts/validate_master_doc.py --mode=validate` (1 min)
3. Read [SMART_BOOK_README.md Quick Start](docs/SMART_BOOK_README.md#quick-start) (5 min)
4. Run: `python scripts/validate_master_doc.py --mode=report` (3 min)
5. Glance at output (4 min)

**Output**: You'll see what's broken and understand the system exists.

---

### Path B: Understanding (60 Minutes)
**Goal**: Understand why this matters and how it works

1. Read [SMART_BOOK_DESIGN_2026-03-03.md](docs/SMART_BOOK_DESIGN_2026-03-03.md) (30 min)
2. Read [SMART_BOOK_README.md](docs/SMART_BOOK_README.md) (20 min)
3. Run validator and review output (10 min)

**Output**: You understand the philosophy, architecture, and practical usage.

---

### Path C: Integration (90 Minutes)
**Goal**: Integrate Smart Book into your workflow

1. Read [SMART_BOOK_INTEGRATION_GUIDE_2026-03-03.md](docs/SMART_BOOK_INTEGRATION_GUIDE_2026-03-03.md) (20 min)
2. Read [SMART_BOOK_DESIGN_2026-03-03.md](docs/SMART_BOOK_DESIGN_2026-03-03.md) (30 min) – optional but recommended
3. Choose integration option:
   - Pre-commit hook (10 min setup)
   - CI/CD (10 min setup)
   - Manual (0 min setup, just discipline)
4. Run validator and fix CRITICAL violations (20 min)
5. Verify integration works (10 min)

**Output**: Smart Book is running on your development machine or CI/CD pipeline.

---

## Key Concepts at a Glance

### The Problem
The ATLAS master documentation had inconsistent counts across sections. T1.5 was stated as 4, 10, 12, and 13 in different places. When the count changed to 13, some sections weren't updated. This eroded credibility.

### The Solution
Make dependencies explicit and machine-readable. The system:
1. **Defines** which section authoritatively specifies each concept (§34 → T1.5 count = 13)
2. **Tracks** which other sections use that concept (§35, §40, §54, ...)
3. **Validates** that all uses match the definition
4. **Alerts** when changes require updates in dependent sections

### The Components
- **Manifest**: Machine-readable spec of concepts and dependencies (JSON)
- **Validator**: Python script that checks consistency (3–5 sec per run)
- **Docs**: Design, README, integration guide explaining why and how

### The Benefits
- Catches inconsistencies before they ship
- Alerts writers: "You changed this in 3 places, affects 8 sections"
- Preserves history: See how concepts evolved over time
- Epistemically responsible: Documentation is consistent and trustworthy

---

## Integration Options at a Glance

| Option | Setup Time | Cost | Benefit |
|--------|-----------|------|---------|
| **Manual** | 0 min | Discipline | None; just remember to run validator |
| **Pre-commit hook** | 5 min | Prevents bad commits | High; impossible to commit violations |
| **CI/CD** | 10 min | Cloud execution | High; automatic on every PR |
| **Reflex** | 20 min | Real-time alerts | Highest; warns as you type |

**Recommended**: Start with pre-commit hook (5 min), can add CI/CD later.

---

## Maintenance at a Glance

### When You Change a Concept
```bash
# 1. Edit the defining section in PART_*.md
# 2. Edit DEPENDENCY_MANIFEST.json:
#    - Update canonical_value
#    - Update last_updated date
#    - Add to update_history
# 3. Run validator to find affected sections
python scripts/validate_master_doc.py --mode=report
# 4. Manually update dependent sections
# 5. Commit with clear message
git commit -m "§34: T1.5 count 12→13; affected §35, §40, §54, §78"
```

### When You Add a Concept
```bash
# 1. Write the section in PART_*.md
# 2. Add to DEPENDENCY_MANIFEST.json under concepts
# 3. Run validator to check
python scripts/validate_master_doc.py --mode=validate
# 4. Commit both markdown and manifest
```

### When You Supersede a Concept
```bash
# 1. Create new section with replacement
# 2. Mark old concept as deprecated in manifest
# 3. Update sections using old concept (or acknowledge deprecation)
# 4. See §48 for example (legacy three-factor → new log-odds formula)
```

---

## Concepts Currently Tracked

| Concept | Value | Defined In | Used In | Status |
|---------|-------|-----------|---------|--------|
| T1.5 count | 13 | §34 | §35, §40, §54, §78, §100, §115, §142, §147 | Critical |
| Credence formula | Log-odds, 4 factors | §48 | §48A–§54 | Current |
| Warrant types | 7 types | §48.1 | §48A–§78 | Current |
| AESHI scoring | 5 dimensions | §54 | §55–§78 | Current |
| Q-norms | 7 standards | §60 | §60–§78 | Current |
| Epistemic levels | T0, T1, T1.5, T2 | §33 | §34, §35, §40, §54, §100 | Current |

---

## Next Steps

### This Week
- [ ] Read this index and SMART_BOOK_README.md quick start (20 min)
- [ ] Run validator: `python scripts/validate_master_doc.py --mode=report` (5 min)
- [ ] Review findings (30 min)

### This Month
- [ ] Read [SMART_BOOK_DESIGN_2026-03-03.md](docs/SMART_BOOK_DESIGN_2026-03-03.md) (30 min)
- [ ] Choose integration option from [SMART_BOOK_INTEGRATION_GUIDE_2026-03-03.md](docs/SMART_BOOK_INTEGRATION_GUIDE_2026-03-03.md) (5 min)
- [ ] Set up chosen integration (5–10 min)
- [ ] Fix CRITICAL violations in PART_VII_T15_REDUCTIONS

### Ongoing
- [ ] Run validator before each commit
- [ ] Update manifest when concepts change
- [ ] Plan Phase 2–5 extensions as needed

---

## Support & Questions

| Question | Answer Location |
|----------|-----------------|
| Why does this matter? | SMART_BOOK_DESIGN_2026-03-03.md (Motivation) |
| How do I use it? | SMART_BOOK_README.md (Quick Start & Maintenance) |
| How do I set it up? | SMART_BOOK_INTEGRATION_GUIDE_2026-03-03.md |
| What does the manifest contain? | SMART_BOOK_README.md (Manifest Structure) |
| What are validation rules? | SMART_BOOK_README.md (What It Checks) |
| What are dependency types? | SMART_BOOK_README.md (Dependency Types) |
| How do I add a concept? | SMART_BOOK_README.md (Maintenance Workflow) |
| How do I fix violations? | SMART_BOOK_README.md (Existing Issues) |
| What's a common scenario? | SMART_BOOK_INTEGRATION_GUIDE_2026-03-03.md (Common Scenarios) |

---

## Document Versions

| File | Version | Date | Size |
|------|---------|------|------|
| SMART_BOOK_DESIGN_2026-03-03.md | 1.0 | 2026-03-03 | 21 KB |
| SMART_BOOK_README.md | 1.0 | 2026-03-03 | 13 KB |
| SMART_BOOK_INTEGRATION_GUIDE_2026-03-03.md | 1.0 | 2026-03-03 | 10 KB |
| DEPENDENCY_MANIFEST.json | 1.0.0 | 2026-03-03 | 29 KB |
| validate_master_doc.py | 1.0 | 2026-03-03 | 21 KB |

**Total**: ~94 KB, all files operational and tested.

---

## Status

**COMPLETE** ✓
**TESTED** ✓
**OPERATIONAL** ✓
**READY FOR INTEGRATION** ✓

The Smart Book system is fully implemented, documented, and ready for immediate use. Choose your integration path from the guide and start validating your documentation.

---

**Created by**: Claude Code
**Date**: March 3, 2026
**Last Updated**: March 3, 2026
