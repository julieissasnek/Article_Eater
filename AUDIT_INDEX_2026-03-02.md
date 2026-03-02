# Article Recommendation Flow Audit Index

**Date**: March 2, 2026
**Status**: Complete
**Location**: `/docs/AUDIT_*` and `/docs/RECOMMENDATION_*`

## Quick Navigation

### For Executives/Managers
Start here: `/docs/AUDIT_SUMMARY_README_2026-03-02.md`
- 1-page executive summary
- What works, what's broken
- Quick fix priority
- 5 questions for David

### For Architects/Technical Leads
Start here: `/docs/AUDIT_RECOMMENDATION_FLOW_2026-03-02.md`
- Complete findings with evidence
- All 4 sources analyzed
- Call chains and data flow
- Master doc topics needed

### For Visual Learners
Start here: `/docs/RECOMMENDATION_FLOW_DIAGRAM_2026-03-02.md`
- ASCII diagrams (current vs intended)
- Visual gap analysis
- Disconnects highlighted

### For Implementing Engineers
Start here: `/docs/AUDIT_FINDINGS_AND_FIXES_2026-03-02.md`
- 6 specific issues with code fixes
- Effort/risk/impact for each
- Implementation priority
- Success metrics

### For Deep Dives
Start here: `/docs/RECOMMENDATION_SOURCES_INVENTORY_2026-03-02.md`
- Line-by-line breakdown of each source
- Data structures and schemas
- Who calls what and when

## Audit Questions Answered

### Q: How do article search recommendations flow from different sources?

**Answer**: Through 6 parallel sources (4 real, 1 aspirational, 1 stub):

1. **Gap Predictor** (REAL) → detects 6 gap types → produces PredictedGap → feeds into queue
2. **VOI System** (REAL but unused) → computes VOI scores → exists but queue ignores
3. **Interpretation Space** (ASPIRATIONAL) → queries undefined table → no population mechanism
4. **QA System** (STUB) → generates follow-ups → not connected to queue
5. **Automated Searcher** (REAL, opt-in) → claims targets from queue → searches Semantic Scholar
6. **Discovery Funnel** (TRACKING only) → records gap closure → no feedback to queue

See: AUDIT_RECOMMENDATION_FLOW_2026-03-02.md (Part 1)

### Q: Is VOI actually hooked up?

**Answer**: Partially. Code is written but integration is broken.

- VOI computation: YES (1945 lines, fully implemented)
- VOI in gap predictor: NO (hardcoded 0.5, never computed)
- VOI in queue prioritization: NO (queue uses FIFO, ignores voi_score field)
- VOI in personalization: NO (no user context in calculation)

See: AUDIT_RECOMMENDATION_FLOW_2026-03-02.md (Part 2)
And: AUDIT_FINDINGS_AND_FIXES_2026-03-02.md (Issues 1, 3, 5)

### Q: Does user-specific VOI exist?

**Answer**: No. Framework exists but not implemented.

- CollectorProfile: YES (has preferred_domains, gap_closure_rate)
- VOI adjustment by profile: NO (all researchers get same VOI)
- Researcher expertise modeling: NO
- Researcher fit factor: NO
- Personalization code: NO

See: AUDIT_RECOMMENDATION_FLOW_2026-03-02.md (Part 3)
And: AUDIT_FINDINGS_AND_FIXES_2026-03-02.md (Issue 2)

## Critical Findings (TL;DR)

| Finding | Status | Impact | Fix Effort |
|---------|--------|--------|-----------|
| VOI computed but not used | BROKEN | HIGH | 2-3 hours |
| Queue ignores VOI scores | BROKEN | HIGH | 1 hour |
| User-specific VOI missing | MISSING | HIGH | 2+ hours |
| Interpretation space table undefined | ASPIRATIONAL | MEDIUM | 2 hours |
| Searcher not auto-triggered | INCOMPLETE | HIGH | 2-3 hours |
| No closure feedback loop | MISSING | MEDIUM | 2-3 hours |

## What Works Well

- Gap detection from argument structure (6 types identified)
- Query generation from gaps
- Queue management and collector claiming
- Semantic Scholar integration
- VOI computation algorithm
- Discovery funnel tracking

## What's Broken

- VOI not used for prioritization (FIFO instead)
- User context ignored (all researchers identical)
- Interpretation space monitoring non-functional
- Automated search requires manual invocation
- No learning from closure outcomes
- QA suggestions not integrated

## Recommended Action Plan

**Week 1 (Immediate)**:
- [ ] Read all audit documents (2-3 hours)
- [ ] Schedule panel discussion (1 hour)
- [ ] Decide on fixes and prioritization

**Week 2-3 (High Priority)**:
- [ ] Fix #1: VOI queue prioritization
- [ ] Fix #2: VOI computation in gap predictor
- [ ] Fix #3: Searcher auto-triggering
- [ ] Fix #4: Interpretation space table

**Week 4+ (Design Review)**:
- [ ] Fix #5: Researcher-specific VOI
- [ ] Fix #6: Closure feedback loop

## Key Files Referenced

**Core logic**:
- `/src/services/gap_predictor.py` (1582 lines)
- `/src/services/voi_search.py` (1945 lines)
- `/src/queue/service.py` (ResearchQueueService)
- `/src/queue/models.py` (data structures)
- `/src/queue/automated_searcher.py` (188 lines)

**Supporting**:
- `/src/services/overseer_management.py` (monitoring)
- `/src/services/discovery_funnel.py` (tracking)
- `/src/services/arbitrary_qa_handler.py` (QA routing)

## Questions for David

1. **Interpretation Space**: Should we wire up phase2-4 outputs to feed queue, or mark as offline?
2. **Researcher VOI**: How should expertise/domain adjust VOI? Expert vs. novice weights?
3. **Automatic Search**: Should searcher run hourly? Daily? On-demand when queue backs up?
4. **Closure Feedback**: Should closure assessment (strong vs. weak) revise future VOI estimates?
5. **QA Integration**: Should follow-up suggestions trigger article searches?

## Success Metrics (After Fixes)

- Queue targets ranked by VOI, not FIFO
- Researchers see personalized recommendations
- Average search latency < 1 hour from gap detection
- System learns which gaps are most resolvable
- Searcher runs automatically on schedule
- No interpretation space queries fail

## Audit Confidence

**HIGH** — All findings based on:
- Direct code inspection (5000+ lines read)
- Import chain analysis (grep across 40+ files)
- Call chain tracing (gap → queue → search)
- Schema verification (table existence checked)
- Data structure analysis (models and fields)

Not speculation. Ground truth from source code.

## Document Map

```
AUDIT_SUMMARY_README_2026-03-02.md
├─ Executive summary
├─ What works / what's broken
├─ 5 questions for David
└─ Next steps

AUDIT_RECOMMENDATION_FLOW_2026-03-02.md
├─ Part 1: All sources analyzed
├─ Part 2: VOI wiring status
├─ Part 3: User-specific VOI analysis
├─ Part 4: Flow diagrams (text)
├─ Part 5: Master doc topics
└─ Part 7: Code issues

RECOMMENDATION_FLOW_DIAGRAM_2026-03-02.md
├─ Current (actual) architecture
├─ Aspirational (intended) architecture
└─ Disconnect analysis

RECOMMENDATION_SOURCES_INVENTORY_2026-03-02.md
├─ Source A: QA System
├─ Source B: Interpretation Space
├─ Source C: Gap Predictor
├─ Source D: VOI System
├─ Source E: Discovery Funnel
├─ Source F: Automated Searcher
└─ Summary matrix

AUDIT_FINDINGS_AND_FIXES_2026-03-02.md
├─ Finding 1: VOI not used (fix provided)
├─ Finding 2: No user-specific VOI (fix provided)
├─ Finding 3: VOI hardcoded (fix provided)
├─ Finding 4: Interp space table undefined (fix provided)
├─ Finding 5: Searcher not auto-triggered (fix provided)
├─ Finding 6: No feedback loop (fix provided)
├─ Implementation priority order
└─ Success metrics
```

## How to Use These Documents

**1. Get oriented** (30 min):
   - Read: AUDIT_SUMMARY_README_2026-03-02.md
   - skim: RECOMMENDATION_FLOW_DIAGRAM_2026-03-02.md

**2. Understand the issues** (1 hour):
   - Read: AUDIT_RECOMMENDATION_FLOW_2026-03-02.md
   - Skim: RECOMMENDATION_SOURCES_INVENTORY_2026-03-02.md

**3. Plan the fixes** (1 hour):
   - Read: AUDIT_FINDINGS_AND_FIXES_2026-03-02.md
   - Decide priority with David

**4. Implement** (varies):
   - Follow code examples in AUDIT_FINDINGS_AND_FIXES_2026-03-02.md
   - Use RECOMMENDATION_SOURCES_INVENTORY_2026-03-02.md for context

## Conclusion

The Article_Eater system has solid components but incomplete integration. The infrastructure for VOI-driven, researcher-aware recommendations exists but isn't connected. Six specific fixes will complete the architecture. All fixes are documented with code examples and effort estimates.

System quality: 70% (infrastructure present, integration incomplete)
Fix complexity: MEDIUM (no architectural redesign needed)
Timeline: 2-3 weeks to complete all fixes
Impact: HIGH (enables intended VOI-driven research allocation)

---

**Audit completed by**: Claude Code
**Date**: March 2, 2026
**Next step**: David reviews findings, schedules panel, prioritizes fixes
