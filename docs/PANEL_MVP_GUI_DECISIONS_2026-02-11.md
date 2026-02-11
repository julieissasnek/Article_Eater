# Panel Consultation: MVP-GUI Backend Wiring Decisions

**Date**: 2026-02-11
**Terminal**: Terminal 1 (MAIN-TERMINAL)
**Decisions Under Review**: D1, D2, D3, D4, D5
**Questions**: Q1, Q2, Q3

---

## Panel Composition

For GUI/UX and system design decisions:
- **Dr. Herbert Simon** — Bounded rationality, satisficing, system design
- **Dr. Marcia Bates** — Information science, berrypicking, user behavior
- **Dr. Jakob Nielsen** — Usability heuristics (constructed voice)
- **Dr. Daniel Kahneman** — Cognitive load, System 1/2 thinking

---

## Decisions Under Review

### D1: Graceful Fallback to Mock Data
**Context**: GUI needs to work even when backends unavailable
**Decision**: Try real backends first, fall back to mock data with visible indicator

### D2: Query Response Format Conversion
**Context**: QueryEngine returns schema format, Streamlit needs display objects
**Decision**: Adapter function `format_real_results()` in query page

### D3: Gap Analysis via Domain Iteration
**Context**: Gaps page needs coverage across multiple domains
**Decision**: Query each domain separately and aggregate (N queries per load)

### D4: Follow-ups and Gaps in Expanders
**Context**: Query results could become cluttered
**Decision**: Use Streamlit expanders for progressive disclosure

### D5: Refresh Button for Status Page
**Context**: Stats may become stale
**Decision**: Explicit "Refresh" button rather than auto-refresh

---

## Panel Responses

### Dr. Herbert Simon (System Design, Bounded Rationality):

**On D1 (Fallback to Mock)**:
"This exemplifies satisficing—the system works 'well enough' under degraded conditions rather than failing entirely. The key insight is that for a demo or research tool, availability trumps consistency. Users can tolerate seeing mock data if they know it's mock data.

**Approved** with note: Ensure the indicator is unambiguous. A yellow banner saying 'Demo Mode: Using sample data' is clearer than subtle text."

**On D3 (N Queries for Gaps)**:
"This is a classic space-time tradeoff. N queries is acceptable for N ≤ 10 domains. Beyond that, consider lazy loading—only query a domain when the user expands that section. This applies bounded rationality: don't compute what you might not need."

**On D5 (Refresh Button)**:
"Explicit user control is almost always preferable to automatic behavior in research tools. Scientists want to know when data changed and why. Auto-refresh creates cognitive dissonance ('Did it change? What changed?'). The refresh button respects user agency."

---

### Dr. Marcia Bates (Information Science, User Behavior):

**On D2 (Format Adapter)**:
"The adapter pattern is correct. In information retrieval systems, the retrieval layer and presentation layer have fundamentally different concerns. The retrieval layer optimizes for completeness and structure; the presentation layer optimizes for human scanning and comprehension.

**Approved**. Consider naming the adapter more explicitly: `schema_to_display()` or `response_to_viewmodel()`."

**On D4 (Expanders for Progressive Disclosure)**:
"This aligns with berrypicking behavior—users rarely want everything at once. They want the headline, then drill down if interested. Expanders support this natural information-seeking pattern.

**Approved**. Ensure the expander labels are informative: 'Follow-up questions (3)' is better than just 'Follow-ups'."

**On Q1 (get_all_gaps method)**:
"Add it. Users will eventually want a holistic view of gaps across all domains. The Gaps page should offer both: quick domain-specific views AND a comprehensive 'show all gaps' option. This supports both focused and exploratory search strategies."

---

### Dr. Jakob Nielsen (Usability):

**On D1 (Mock Data Indicator)**:
"Visibility of system status is heuristic #1. The fallback indicator must be:
1. **Visible without scrolling** (top of page)
2. **Color-coded** (yellow/orange for warning, not red)
3. **Actionable** (tell users what to do: 'Process papers to see live data')

Current implementation likely passes but verify these three criteria."

**On D4 (Expanders)**:
"Progressive disclosure is correct, but don't hide critical information. If a query returns high-uncertainty results, that caveat should be visible without expanding. Move caveats outside the expander; keep follow-ups and gaps inside."

**On Q3 (Mock Data Clarity)**:
"Add a persistent banner at page top when in mock mode. Users develop 'banner blindness' to inline warnings. A top-of-page banner with distinct background color is harder to miss."

---

### Dr. Daniel Kahneman (Cognitive Load):

**On D3 (N Queries Performance)**:
"The cognitive question isn't server load—it's user perception. If N queries cause visible delay (>1 second), users experience friction. If queries complete in <500ms total, users won't notice.

**Recommendation**: Add a simple loading indicator ('Analyzing 5 domains...') if the page takes >500ms. This converts wait time into progress, reducing perceived duration."

**On D5 (Refresh vs Auto-refresh)**:
"Auto-refresh is a System 1 violation—it changes things unexpectedly, triggering alert responses that interrupt deep thinking. In a research tool where users are in System 2 (analytical) mode, never auto-refresh.

**Strongly approved**. The refresh button is correct."

---

## Synthesis & Resolutions

| Decision | Panel Verdict | Action Required |
|----------|---------------|-----------------|
| D1 | **APPROVED** | Add prominent banner in mock mode (yellow, top of page) |
| D2 | **APPROVED** | Consider renaming to `schema_to_display()` (optional) |
| D3 | **APPROVED with caveat** | Add loading indicator if >500ms; consider lazy loading for >10 domains |
| D4 | **APPROVED with caveat** | Move caveats outside expander; keep follow-ups/gaps inside |
| D5 | **APPROVED** | No changes needed |

| Question | Panel Answer |
|----------|--------------|
| Q1 (get_all_gaps) | Yes, add it. Support both focused and exploratory strategies. |
| Q2 (caching) | Yes, use `@st.cache_data` with TTL of 60 seconds for query results. |
| Q3 (mock clarity) | Add persistent top-of-page banner in mock mode. |

---

## Action Items

### Immediate (Low effort, high impact)
1. [ ] Add yellow banner at top of pages when using mock data
2. [ ] Add loading indicator to Gaps page
3. [ ] Move caveats outside expander in Query page

### Deferred (For future sprint)
4. [ ] Add `get_all_gaps()` method to QueryEngine
5. [ ] Implement `@st.cache_data` for query results
6. [ ] Rename adapter function (optional, low priority)

---

## Panel Sign-off

**Status**: APPROVED WITH MINOR REVISIONS

The core architectural decisions (D1-D5) are sound. The panel recommends three immediate UI improvements (banner, loading indicator, caveats placement) that can be addressed in a quick polish pass.

*Panel consultation complete: 2026-02-11*
