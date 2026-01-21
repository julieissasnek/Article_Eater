# Expert Panel Feedback on Tier 1 Implementation Plan
## Article Eater Post-Quinean v1
**Date**: January 20, 2026
**Status**: Panel Review Complete

---

## DR. JUDEA PEARL — Feedback on Plan

### On GUI (Decision 1.1.3: Edge encoding for CORRELATIONAL)

**Question asked**: Should CORRELATIONAL edges be shown differently (dotted AND grayed)?

**Response**: Yes, but go further. CORRELATIONAL findings should be visually distinct enough that users cannot confuse them with causal edges. My recommendation:

1. **Causal edges**: Solid line with arrowhead, full opacity
2. **Correlational edges**: Dotted line, NO arrowhead, 50% opacity, different color (gray or blue)

The absence of an arrowhead is critical. An arrowhead implies direction; correlations have none.

Additionally, consider a toggle in the UI: "Show correlational edges" (default: OFF for causal reasoning; ON for exploration). This prevents the visual noise of correlations while preserving access to them.

### On Stopping Rules (Question 15: Quality vs. recency weighting)

**Question asked**: Should we weight by study quality rather than recency to prevent oscillation?

**Response**: Yes, but not as a replacement—as an addition. The problem of oscillating credences typically occurs when:
1. Two studies of equal quality report opposite results
2. No clear methodological reason favors one over the other

In such cases, neither recency nor quality resolves the tension. The correct response is to:
1. Flag the belief as "contested"
2. Report the effect size range (not a point estimate)
3. Recommend additional studies designed to resolve the disagreement

**Concrete implementation**: When credence oscillates > 3 times, set `belief.status = CONTESTED` and `belief.credence_range = [min, max]` rather than a point credence.

### Additional Concern: BN Not in Tier 1

I note that BN export was downgraded from Tier 1. While I understand the rationale (GUI first), I want to flag that UC1 (the architect use case) depends entirely on BN queries. Without BN export, the Evidence Explorer shows beliefs but cannot answer "What happens if I add natural light to this design?"

**Recommendation**: Add a Tier 1.5 item: "BN Query Interface (read-only)" that allows querying the BN even if full export is deferred. This gives architects minimal functionality.

---

## DR. NANCY CARTWRIGHT — Feedback on Plan

### On NLQ (Question 8: Bridge warrant default)

**Question asked**: Should bridge warrants default to conservative or optimistic?

**Response**: Conservative, always. The entire point of explicit bridge warrants is to force users to think about generalizability. If the system defaults to "bridges are valid," users will never question them.

**Specific implementation**:
- When a query involves cross-domain inference, include a warning: "This answer assumes findings from [source domain] apply to [target domain]. Bridge confidence: 0.55"
- Offer a "strict mode" toggle that excludes bridged evidence entirely
- Log when users proceed despite low bridge confidence (this is valuable feedback)

### On Ingestion (Question 10: Full-text for causal claims)

**Question asked**: Should we require full-text for causal claims?

**Response**: Not "require," but strongly encourage and clearly label.

Causal claims extracted from abstracts are inherently limited because:
1. Abstracts often overstate effect sizes
2. Methodology details (confound control, sample characteristics) are absent
3. Scope conditions are usually omitted

**Implementation**:
- Extract causal claims from abstracts but mark them `causal_confidence: "abstract_only"`
- Display these beliefs with a warning badge: "⚠️ Causal claim from abstract—methodology unverified"
- When full text is later uploaded, re-extract and compare

### On Stopping Rules (Question 16: Publication bias warning)

**Question asked**: Should stability reporting include publication bias warning?

**Response**: Absolutely. This is one of the most important features you could add.

When the system declares stability, it should calculate and report:
1. **Funnel plot asymmetry** (if sufficient studies): Visual indication of bias
2. **Null result ratio**: What percentage of studies report null/negative results? If < 10%, flag as "likely biased"
3. **Recommendation**: "Stability may reflect publication bias. Consider searching grey literature, preprint servers, or registered reports."

This directly addresses UC11 (Publication Bias Assessment) and should be part of standard stopping reports.

### Additional Concern: Enabling Conditions Still Missing

The plan does not address enabling conditions (from my earlier feedback). Beliefs like "Natural light improves mood" require enabling conditions to be actionable (e.g., "requires > 30 min exposure, baseline mood not severely depressed").

**Recommendation**: Add to GUI-3 (detail panel) a field for enabling conditions. Even if empty initially, the data model should support it.

---

## DR. HERBERT SIMON — Feedback on Plan

### On GUI (Question 4: Default view)

**Question asked**: Should default view show ALL beliefs or start focused?

**Response**: Start focused. Showing all beliefs at once violates every principle of bounded rationality:
1. Users cannot process hundreds of nodes simultaneously
2. Attention is a limited resource
3. The system should guide, not overwhelm

**Specific recommendation**:
- Default view: Show the 20-30 highest-credence beliefs
- Provide clear entry points: "Start with: Stress | Creativity | Wayfinding | ..."
- Expand on demand: "Show related beliefs" button on each node

This is progressive disclosure applied to graph visualization.

### On NLQ (Question 6: Follow-up suggestions)

**Question asked**: How many follow-up suggestions is too many?

**Response**: Three is the right number. This is based on the "magical number" research—people can comfortably choose among 3-5 options without decision paralysis.

Show exactly 3 follow-ups:
1. One that goes deeper (more specific)
2. One that goes broader (related topic)
3. One that addresses uncertainty (what don't we know)

If more are available, add "More suggestions..." link.

### On Stopping (Question 13: Structural stability)

**Question asked**: Is credence stability the right metric, or also structural?

**Response**: Both, with credence primary.

Structural stability matters when:
1. New papers keep introducing NEW beliefs (not just updating existing ones)
2. The web topology is still being discovered

**Implementation**:
- Primary: Credence stability (as proposed)
- Secondary: If > 3 new beliefs added in last 5 papers, report "Structural growth ongoing—consider continuing"

This handles the case where credences are stable but the topic landscape is still being mapped.

### Additional Concern: Cognitive Load in Detail Panel

The detail panel mockup shows a lot of information. This is fine for expert mode, but novice users will be overwhelmed.

**Recommendation**: Add a "simplified view" option:
```
┌─────────────────────────────────────┐
│ Natural light improves mood         │
│ ─────────────────────────────────── │
│ Confidence: HIGH 🟢                 │
│ Based on 3 studies                  │
│ Some disagreement exists            │
│                                     │
│ [Show Details]                      │
└─────────────────────────────────────┘
```

One-click to expand to full detail panel.

---

## DR. MARCIA BATES — Feedback on Plan

### On GUI (Question 3: Search scope)

**Question asked**: Should search match belief content only, or also papers/authors?

**Response**: All of the above, with clear result categories.

Researchers search in multiple modes:
1. **Concept search**: "stress" → find beliefs about stress
2. **Author search**: "Ulrich" → find papers by Ulrich
3. **Paper search**: "stress recovery theory" → find that specific paper

**Implementation**:
```
Search: ulrich

Results:
─────────────────────────────────
BELIEFS (3)
• Natural views reduce stress (supported by Ulrich 1984)
• Hospital rooms with windows improve recovery
• ...

PAPERS (5)
• Ulrich, R. (1984). View through a window...
• Ulrich, R. (1991). Stress recovery during exposure...
• ...

AUTHORS (1)
• Roger Ulrich (23 papers in web)
─────────────────────────────────
```

### On NLQ (Question 5: Precision/recall balance)

**Question asked**: What's the right precision/recall balance in query parsing?

**Response**: Favor recall in initial retrieval, precision in ranking.

In exploratory information seeking (Bates, 1989), users don't know exactly what they're looking for. A system that interprets queries too narrowly misses relevant results.

**Implementation**:
1. **Broad retrieval**: Parse "creativity" to include synonyms (innovation, creative thinking, ideation, divergent thinking)
2. **Ranked results**: Put exact matches first, then synonyms, then related concepts
3. **Transparent expansion**: Show "Also searching for: innovation, ideation, ..."

This respects the "berrypicking" model—users will refine their search based on what they find.

### On Ingestion (Question 9: Auto-suggest related papers)

**Question asked**: Should we auto-suggest related papers based on citations?

**Response**: Yes, but with care.

Citation-based suggestions are valuable for:
1. Building complete evidence networks
2. Discovering foundational papers
3. Finding recent replications

But they can also create filter bubbles—if you start with one perspective, citations lead to more of the same.

**Implementation**:
- Suggest cited papers: "This paper cites 5 papers in your web"
- Suggest citing papers: "This paper is cited by 3 papers in your web"
- Suggest methodologically diverse papers: "These 2 papers use different methods to study the same question"

The third category counteracts homogeneity bias.

### Additional Concern: Missing Search History

The plan mentions "Query history" but doesn't elaborate. This is critical for exploratory search.

**Recommendation**: Implement full search session history:
1. All queries in current session (with timestamps)
2. Clickable to re-run
3. "Branch from here" to explore alternative paths
4. Export session as report

Researchers often want to document their search process. This serves both utility and reproducibility.

---

## DR. RACHEL KAPLAN — Feedback on Plan

### On Ingestion (Question 12: Domain-specific databases)

**Question asked**: Are there domain-specific databases beyond PubMed?

**Response**: Yes, several are important for environmental psychology:

1. **PsycINFO** (APA): Primary psychology database; better coverage of environmental psychology than PubMed
2. **Web of Science**: Broader science coverage; important for architecture and design journals
3. **Scopus**: Similar to WoS; some unique coverage
4. **ERIC**: Education-focused; relevant for school environment research
5. **Avery Index**: Architecture-specific; critical for built environment research

**Priority recommendation**:
1. PubMed (already planned)
2. Semantic Scholar (already planned—good because it aggregates)
3. Add PsycINFO API if available
4. Consider Avery Index for architecture-specific queries

PsycINFO is the most important addition. Environmental psychology literature often isn't indexed in PubMed.

### On GUI (Detail panel: Scope conditions)

The detail panel shows scope conditions as a list. This is good, but the format could be more actionable.

**Recommendation**: Structure scope conditions as:
```
SCOPE CONDITIONS
✓ Applies: office settings, healthcare facilities
✗ Does NOT apply: residential, outdoor
? Unknown: industrial, educational
```

Explicit "does not apply" and "unknown" categories help users assess applicability.

### On Stopping Rules (Publication bias for environmental psychology)

Environmental psychology has significant publication bias issues. Effect sizes in the literature are probably inflated.

**Domain-specific recommendation**: When reporting stability in environmental psychology topics, include a standard warning:
"Note: Environmental psychology literature shows evidence of publication bias (Ferguson & Heene, 2012). Reported effect sizes may be inflated."

This calibrates user expectations appropriately.

---

## WORKFLOW DESIGNER — Feedback on Plan

### On GUI (Decision 1.1.5: Detail panel)

The detail panel is well-designed for experts but needs a workflow-oriented alternative for practitioners.

**Recommendation**: Add an "Implications" tab to the detail panel:
```
┌─────────────────────────────────────────┐
│ [Overview] [Sources] [Implications]     │
├─────────────────────────────────────────┤
│ DESIGN IMPLICATIONS                     │
│                                         │
│ If you're designing an office:          │
│ • Include access to natural light       │
│ • Consider window placement for views   │
│ • Effect is stronger with >30 min       │
│   exposure                              │
│                                         │
│ Confidence: MODERATE                    │
│ Key uncertainty: optimal lux levels     │
│ ─────────────────────────────────────── │
│ CAUTION                                 │
│ • Lab→field transfer uncertain          │
│ • Individual differences significant    │
└─────────────────────────────────────────┘
```

This serves the architect user journey directly.

### On NLQ (Response format)

The proposed response format is comprehensive but dense. For the researcher journey, add a "Quick Answer" mode:

```
Q: What affects creativity?

QUICK ANSWER: Noise (negative), privacy (positive),
natural light (positive). Moderate confidence.

[Show full analysis]
```

This serves the common case where users want a fast answer before deciding whether to dig deeper.

### On Overall Workflow Integration

The plan treats GUI, NLQ, Ingestion, and Stopping as separate features. They need to be integrated into coherent workflows.

**Recommendation**: Define three "mission modes" in the UI:

1. **Explore Mode**: Start with Evidence Explorer, browse freely, ask questions
2. **Ingest Mode**: Add papers, review extractions, build the web
3. **Research Mode**: Define a question, search systematically, reach stability

Each mode shows relevant controls and hides irrelevant ones. This reduces cognitive load and guides users through appropriate workflows.

---

## GUI/UX EXPERT — Feedback on Plan

### On Decision 1.1.2 (Layout algorithm)

Force-directed is the right default, but add layout options:

1. **Force-directed** (default): Good for exploration
2. **Outcome-grouped**: Cluster by outcome category
3. **Source-grouped**: Cluster by source paper
4. **Timeline**: Arrange by publication date

Users should be able to switch layouts to see different perspectives on the same data.

### On Decision 1.1.4 (Interaction model)

Add keyboard shortcuts for power users:
- `/` — Focus search box
- `Esc` — Clear selection
- `Enter` — Open detail panel for selected node
- `[` / `]` — Navigate through search results
- `?` — Show keyboard shortcuts

### On Visual Design (Not addressed in plan)

The plan describes functionality but not visual design. Recommendations:

1. **Color scheme**: Use a muted palette with high-contrast accents for alerts
2. **Typography**: Monospace for credence values; proportional for text
3. **Density**: Provide "compact" and "comfortable" display modes
4. **Accessibility**: Ensure color is not the only differentiator (add patterns/icons)

### On Mobile/Responsive

The plan assumes desktop use. Is mobile support needed?

**Recommendation**: For initial release, desktop-first is acceptable. But ensure the UI is not broken on tablets—researchers may want to review the web on iPad during meetings.

---

## SYSTEMS ARCHITECT — Feedback on Plan

### On ING-1 (API clients)

The plan proposes building four separate API clients. Consider a unified approach:

```python
class PaperFetcher:
    def fetch(self, identifier: str) -> PaperMetadata:
        id_type = self.detect_type(identifier)
        if id_type == "doi":
            return self.crossref.fetch(identifier)
        elif id_type == "pmid":
            return self.pubmed.fetch(identifier)
        # etc.
```

This simplifies the ingestion UI—users just paste any identifier.

### On Rate Limiting (Question 11)

**Question asked**: Should users register for API keys, or use shared key?

**Response**: Shared key for initial release, with clear path to user keys.

1. **Phase 1**: Use institutional API key with conservative rate limiting
2. **Phase 2**: Add "Bring your own API key" option for heavy users
3. **Phase 3**: If usage grows, require user keys

Log API usage per user to identify when phase transitions are needed.

### On Data Model for Stability Tracking

The plan adds credence history to beliefs. Clarify the data model:

```python
class CredenceHistory:
    belief_id: str
    timestamp: datetime
    credence: float
    delta: float
    triggered_by: str  # paper_id that caused update
```

Store the full history, not just last N values. This enables:
1. Stability calculation
2. Historical analysis
3. Audit trail

### On API Design for GUI

The plan proposes `/api/v1/web/graph` for the Evidence Explorer. Define the response schema:

```json
{
  "nodes": [
    {
      "id": "belief_123",
      "label": "Natural light improves mood",
      "credence": 0.78,
      "outcome_category": "affect.mood",
      "status": "INTEGRATED",
      "conflict": false
    }
  ],
  "edges": [
    {
      "source": "belief_123",
      "target": "belief_456",
      "type": "SUPPORTS",
      "strength": 0.65,
      "causal_direction": "FORWARD"
    }
  ],
  "metadata": {
    "total_beliefs": 234,
    "total_constraints": 567,
    "coherence_score": 0.82
  }
}
```

Document this schema early; the GUI team needs it.

---

## EPISTEMOLOGIST — Feedback on Plan

### On NLQ (Question 7: Coherence display)

**Question asked**: Should we expose full coherence calculation or use traffic-light?

**Response**: Traffic-light as default, full calculation available.

The coherence score is a computational artifact—it's useful for the system but not meaningful to most users. "High/Medium/Low confidence" communicates what users need to know.

However, researchers studying the system itself will want the raw numbers. Provide:
- Default: Traffic-light (🟢 🟡 🔴)
- Expert toggle: Show numeric coherence, constraint satisfaction breakdown

### On Stopping (Question 14: Oscillating credences)

**Question asked**: How should we handle oscillating credences?

**Response**: Oscillation is epistemically significant—it indicates genuine disagreement in the literature, not noise.

**Implementation**:
1. Detect oscillation: credence crosses a threshold (e.g., 0.5) more than twice
2. Flag as "contested belief"
3. Report both positions with their supporting evidence
4. Do NOT force convergence to a single credence

This is the Quinean approach—when evidence genuinely conflicts, the web should reflect that conflict, not paper it over with an average.

### On Quinean Fidelity (General)

The plan is well-designed but risks a subtle violation of Quinean principles:

**Concern**: The stopping rule "no belief changed > 0.01" assumes that beliefs SHOULD converge to stable values. But Quine's web is never truly stable—new evidence can always cause revision.

**Recommendation**: Frame stability not as "the web is done" but as "the web is stable given current evidence." The report should say:
> "The web has reached equilibrium with the evidence currently available. This does not mean beliefs are certain—only that additional papers from the same literature are unlikely to change them significantly. Genuinely new evidence (different methods, populations, or paradigms) could still cause substantial revision."

This preserves Quinean fallibilism while providing practical stopping guidance.

---

# SYNTHESIS: REVISED DECISIONS

Based on panel feedback, here are the revised decisions:

| ID | Original | Revised | Rationale |
|----|----------|---------|-----------|
| 1.1.3 | Edge color for type | Add: No arrowhead for correlational | Pearl: Arrows imply direction |
| 1.1.4 | Default shows all | Default shows top 20-30 by credence | Simon: Bounded rationality |
| 1.1.5 | Single detail panel | Add simplified view + Implications tab | Simon, Workflow: Cognitive load |
| 1.2.3 | 3+ follow-ups | Exactly 3 (deeper, broader, uncertainty) | Simon: Magical number |
| 1.2.4 | Ask on ambiguity | Ask + show vocabulary expansion | Bates: Transparent expansion |
| 1.3.2 | Metadata + structured | Add warning badge for abstract-only causal | Cartwright: Methodology matters |
| 1.4.1 | Credence stability only | Add structural stability check | Simon: Topology discovery |
| 1.4.5 | Basic VOI integration | Add oscillation detection → "contested" | Epistemologist: Genuine conflict |
| NEW | - | Add publication bias to stability report | Cartwright: Critical feature |
| NEW | - | Add enabling conditions to data model | Cartwright: Still missing |
| NEW | - | Add "mission modes" (Explore/Ingest/Research) | Workflow: Coherent journeys |
| NEW | - | Add PsycINFO to ingestion sources | Kaplan: Domain coverage |

---

# IMPLEMENTATION ADJUSTMENTS

## Added to Scope

1. **Correlational edge styling** (no arrowhead, grayed): Add to GUI-2
2. **Simplified detail view**: Add to GUI-3
3. **Implications tab**: Add to GUI-3
4. **Oscillation detection**: Add to STOP-1
5. **Publication bias warning**: Add to STOP-2
6. **Enabling conditions field**: Add to data model (GUI-1)
7. **Mission modes UI**: Add to GUI-4
8. **PsycINFO client**: Add to ING-1

## Deferred (Tier 1.5)

1. **BN Query Interface**: Pearl flagged this as needed for UC1
   - Minimal implementation: Query existing beliefs with outcome filters
   - Full BN deferred to Tier 2

## Revised Timeline

| Sprint | Feature | Duration | Change |
|--------|---------|----------|--------|
| GUI-1 | Backend API + enabling conditions | 2.5 days | +0.5 for data model |
| GUI-2 | Basic visualization + correlational styling | 2.5 days | +0.5 for edge types |
| ING-1 | API clients + PsycINFO | 2.5 days | +0.5 for extra API |
| GUI-3 | Interaction + simplified view + implications | 3 days | +1 for extra views |
| STOP-1 | Stability + oscillation detection | 1.5 days | +0.5 for oscillation |
| STOP-2 | Reporting + publication bias | 1.5 days | +0.5 for bias warning |
| GUI-4 | Polish + mission modes | 2 days | +1 for modes |

**Revised total**: ~27 sprint-days (was 22)

---

# REMAINING QUESTIONS FOR IMPLEMENTATION

These questions were not fully resolved by panel feedback:

1. **Mobile support**: Defer or include basic tablet view?
   - **Panel consensus**: Desktop-first acceptable; don't break on tablets

2. **User API keys**: When to require?
   - **Panel consensus**: Shared key initially; monitor usage

3. **Search history persistence**: Session-only or cross-session?
   - **Bates recommends**: Persist across sessions for reproducibility

4. **Contested belief display**: How to show credence range?
   - **Options**: Error bars, min-max text, or dual nodes
   - **Recommendation needed from UX**

---

*End of Panel Feedback*

**Plan is approved with revisions. Implementation may proceed.**
