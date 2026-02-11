# Implementation Decisions: MVP-GUI Backend Wiring

**Date**: 2026-02-11
**Terminal**: Terminal 1 (MAIN-TERMINAL)
**Status**: Pending Panel Review

---

## Decisions Made

### D1: Graceful Fallback to Mock Data
**Context**: GUI needs to work even when backends unavailable (demo resilience)
**Decision**: All pages try real backends first, fall back to mock data with visible indicator
**Alternatives**:
- Hard fail if backends unavailable (confusing UX)
- Always use mock data (no live demo capability)
**Risk Level**: Low

### D2: Query Response Format Conversion
**Context**: QueryEngine returns ae.query_response.v1 schema, Streamlit needs display objects
**Decision**: Created `format_real_results()` adapter function in query page
**Alternatives**:
- Modify QueryEngine to return display-ready format (violates separation)
- Have QueryEngine return both formats (bloat)
**Risk Level**: Low

### D3: Gap Analysis via Domain Iteration
**Context**: Gaps page needs coverage across multiple domains
**Decision**: Query each domain separately ("what affects {domain}") and aggregate gaps
**Alternatives**:
- Single "show all gaps" query (QueryEngine doesn't support this)
- Pre-compute gaps in batch processor (adds complexity)
**Risk Level**: Medium (N queries per page load)

### D4: Follow-ups and Gaps Shown in Expanders
**Context**: Query results page could become cluttered with metadata
**Decision**: Use Streamlit expanders for follow-ups and gaps (progressive disclosure)
**Alternatives**:
- Always show (cluttered)
- Separate tabs (more clicks)
**Risk Level**: Low

### D5: Refresh Button for Status Page
**Context**: Stats are loaded on page load, may become stale
**Decision**: Added explicit "Refresh" button that calls st.rerun()
**Alternatives**:
- Auto-refresh on interval (resource intensive)
- No refresh (user must reload browser)
**Risk Level**: Low

---

## Questions for Panel

1. **D3 concern**: Is querying each domain separately acceptable, or should we add a `get_all_gaps()` method to QueryEngine?

2. **Performance**: Should we cache QueryEngine results with `@st.cache_data`?

3. **UX**: Is the fallback to mock data clear enough to users, or should we add a more prominent banner?

---

## Files Modified

- `streamlit_app/mvp/pages/1_status.py` - Added refresh button
- `streamlit_app/mvp/pages/2_query.py` - Wired to QueryEngine, format adapter
- `streamlit_app/mvp/pages/3_gaps.py` - Wired to QueryEngine gap analysis

---

*Awaiting panel review before MVP-5 (Polish & Demo)*
