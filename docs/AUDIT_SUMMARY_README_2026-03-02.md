# Article Recommendation Flow Audit — Summary

**Date**: March 2, 2026
**Status**: Complete
**Scope**: How article search recommendations flow; VOI integration; user-specific personalization

---

## Documents in This Audit

This audit consists of 4 detailed documents:

### 1. Main Audit Report
**File**: `AUDIT_RECOMMENDATION_FLOW_2026-03-02.md`
- Complete findings on all 4 recommendation sources
- VOI integration status (what's real vs. stub)
- User-specific VOI analysis
- Master doc topics needed
- Evidence and call chains

**Read this if**: You want full context on the current state

### 2. Flow Diagrams
**File**: `RECOMMENDATION_FLOW_DIAGRAM_2026-03-02.md`
- Visual current state (actual implementation)
- Visual intended state (aspirational design)
- Shows disconnects between sources and execution
- Color-coded: working, broken, aspirational, opt-in

**Read this if**: You prefer visual representation

### 3. Detailed Source Inventory
**File**: `RECOMMENDATION_SOURCES_INVENTORY_2026-03-02.md`
- Deep dive on each of 6 recommendation sources
- Code snippets and data structures
- What's REAL, STUB, ASPIRATIONAL
- Who calls what and when
- Matrix comparison

**Read this if**: You need to understand a specific source component

### 4. Actionable Fixes
**File**: `AUDIT_FINDINGS_AND_FIXES_2026-03-02.md`
- 6 critical findings with specific fixes
- Code examples for each fix
- Effort/risk/impact assessment
- Implementation order
- Success metrics

**Read this if**: You're planning the remediation work

---

## Key Findings (Executive Summary)

### What Works
- ✓ Gap detection from argument structure
- ✓ Query generation from gaps
- ✓ Queue management and collector claiming
- ✓ Semantic Scholar search integration
- ✓ VOI score computation (as utility module)

### What's Broken
- ✗ VOI not used for queue prioritization (hardcoded 0.5)
- ✗ User-specific VOI completely missing
- ✗ Interpretation space queries undefined table
- ✗ Automated search not auto-triggered
- ✗ No feedback loops (closure → VOI revision)

### Reality Check

**Gap Predictor** generates 6 types of knowledge gaps and produces article search suggestions → **WORKS**

**VOI System** computes value-of-information scores → **WORKS** (but unused)

**Research Queue** manages targets and lets collectors claim them → **WORKS**

**Automated Searcher** claims targets and searches Semantic Scholar → **WORKS** (but opt-in only)

**BUT**: Queue ignores VOI scores (FIFO order) → **BROKEN**

**AND**: No researcher-specific VOI → **MISSING**

**AND**: Interpretation space monitoring assumes table that doesn't exist → **ASPIRATIONAL**

---

## The Core Issue

**Aspirational vs. Actual**:

The system was designed to be VOI-driven and researcher-aware, but:

1. Gap predictor hardcodes VOI=0.5 (doesn't call VOI scorer)
2. Queue stores targets but doesn't sort by VOI
3. CollectorProfile exists but context not used
4. Interpretation space phase outputs are offline
5. Searcher must be manually invoked

Result: **System works, but not as intended. VOI computed but not used. Personalization framework exists but not implemented.**

---

## Quick Fix Priority

**Immediate (2-3 hours)**:
1. Sort queue by VOI instead of FIFO
2. Call VOI scorer from gap predictor
3. Wire these two together

**Next Sprint (4-5 hours)**:
4. Add scheduler for automated searcher
5. Define/populate interpretation_space_suggestions table

**Design Review (6+ hours)**:
6. Implement researcher-specific VOI fit factors
7. Add closure feedback loop for learning

---

## Architectural Insight

The system has THREE conceptually separate but connected layers:

**Layer 1: GAP DETECTION**
- Inputs: Argument structure, annotations, QA results
- Output: PredictedGap objects
- Status: WORKING
- Issue: VOI hardcoded, not computed

**Layer 2: PRIORITIZATION**
- Input: PredictedGap collection
- Output: Ranked list for researchers
- Status: BROKEN (FIFO instead of VOI)
- Issue: Queue doesn't use VOI or researcher context

**Layer 3: EXECUTION**
- Input: ResearchTarget from queue
- Output: Articles found and integrated
- Status: WORKING (when manually triggered)
- Issue: Searcher is opt-in, not auto-invoked

Fixes in Layer 1 + 2 are high-impact. Fix in Layer 3 enables full automation.

---

## Questions to Ask David

1. **Interpretation Space**: Is the phase2-4 output actually meant to feed article searches? Should we wire it up or mark it offline?

2. **User Context**: You mentioned "researcher-specific VOI" — what's the ranking? (Expert in mechanisms vs. novice in validation?)

3. **Auto-Search**: Should searcher run every N hours? Or on-demand when queue backs up?

4. **Feedback**: Should closure assessment (found strongly vs. weakly) revise VOI estimates for similar gaps?

5. **QA Integration**: Should arbitrary_qa_handler follow-up suggestions trigger article searches, or are they just reactive?

---

## Files to Review

**Core recommendation logic**:
- `/src/services/gap_predictor.py` (1582 lines) — Gap detection
- `/src/services/voi_search.py` (1945 lines) — VOI computation
- `/src/queue/service.py` — ResearchQueueService
- `/src/queue/models.py` — Data structures
- `/src/queue/automated_searcher.py` (188 lines) — Search execution

**Supporting**:
- `/src/services/overseer_management.py` — Monitoring (assumes undefined table)
- `/src/services/discovery_funnel.py` — Gap tracking
- `/src/services/arbitrary_qa_handler.py` (51.8 KB) — QA routing
- `/src/cmr/voi_scoring.py` (108 lines) — Finding-level VOI utility

---

## Next Steps

1. **Review these audit documents** (30 min)
2. **Schedule panel discussion** on fixes (1 hour)
3. **Prioritize** what to fix first (depends on David's answers)
4. **Implement** fixes in priority order
5. **Test** each fix (unit + integration)
6. **Deploy** and monitor

---

## Audit Methodology

This audit:
- Read 1582 + 1945 + 188 lines of core services
- Traced call chains from gap detection to search execution
- Searched for VOI imports across 40+ files
- Examined CollectorProfile and researcher context
- Verified table schemas and data flow
- Documented what's REAL vs. STUB vs. ASPIRATIONAL
- Provided specific code fixes with effort/risk assessment

Confidence level: **HIGH** (code-based evidence, not speculation)

---

**Report Generated**: 2026-03-02 by Claude Code
**Questions?** See AUDIT_FINDINGS_AND_FIXES_2026-03-02.md for detailed fixes with code examples
