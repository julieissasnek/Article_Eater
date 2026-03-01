# RUTHLESS V5+ TOUGHENED AUDIT — Data Utilization & Informativeness

**Date:** 2026-02-28T16:15:00-08:00
**Triggered by:** DK requested toughened audit with additional experts in weakest area
**Weakest area identified:** EN/BN data utilization (0% paper integration) and A9-A18 annotation gap
**Score: 5/10 AMBER** (downgraded from V5's 7/10 YELLOW)

---

## Data Utilization Crisis

| Metric | Available | Integrated | Utilization |
|--------|-----------|------------|-------------|
| Papers | 824 | 0 | **0%** |
| Findings | ~28,700 (est.) | 0 | **0%** |
| Templates | 208 | 0 with evidence links | **0%** |
| Templates with CVA mappings | 208 | 0 | **0%** |
| Theories formalized | 24 | 0 with formal spec | **0%** |

## Extraction Field Completeness (300-paper sample)

| Field | Count | Percentage |
|-------|-------|------------|
| Direction | 10,452 | 100.0% |
| Theory links | 9,381 | 89.8% |
| Mechanism | 3,244 | 31.0% |
| Effect size | 2,813 | 26.9% |
| Sample size | 327 | 3.1% |
| Confidence intervals | 0 | 0.0% |
| Images/figures | 0 | 0.0% |

## A9-A18 Implementation Status

| Annotation | Status | Can Auto-Generate? |
|-----------|--------|-------------------|
| A9 Surprise Flag | ✗ NOT IMPLEMENTED | ✅ Yes — flag findings that contradict template consensus |
| A10 Design Implication | ✗ NOT IMPLEMENTED | 🤖 LLM required |
| A11 Controversy/Dispute | ✗ NOT IMPLEMENTED | ✅ Yes — from panel critique data |
| A12 Analogical Bridge | ✗ NOT IMPLEMENTED | 🤖 LLM required |
| A13 Replication Status | ✗ NOT IMPLEMENTED | ✅ Yes — count DOI replications |
| A14 Effect Magnitude | ✗ NOT IMPLEMENTED | ✅ Yes — parse existing effect_size fields |
| A15 Cross-Domain Connection | ✗ NOT IMPLEMENTED | ✅ Partial — from theory_links |
| A16 Historical Context | ✗ NOT IMPLEMENTED | 🛠️ Semi-manual |
| A17 Narrative Hook | ✗ NOT IMPLEMENTED | 🤖 LLM required |
| A18 Unanswered Question | ✗ NOT IMPLEMENTED | ✅ Yes — from gap reports |

## Expert Panel Verdict

**Unanimous: Do NOT acquire more articles. Integrate the 824 you have.**

## Prevention Infrastructure Deployed

| Guard | File | Prevents |
|-------|------|----------|
| Import smoke test | `tests/conftest.py` | Broken enums, circular imports |
| Test count alarm | `tests/conftest.py` | Silent test collection failures |
| Enum lint | `scripts/check_repo_health.py` | Duplicate enum members |
| Module-test manifest | `scripts/check_repo_health.py` | Missing test files |
| EN/BN health diagnostic | `scripts/check_repo_health.py` | Data utilization blindness |

## Top Priority Actions

1. **Complete EN-0C batch integration (batches 1-11)** — CRITICAL
2. **Auto-generate A9/A13/A14** from existing extraction data — HIGH
3. **Calibrate remaining 105 templates** — HIGH
4. **Wire A9-A18 into QA handler** with progressive disclosure — HIGH
5. **Reassess after integration** whether more articles are needed
