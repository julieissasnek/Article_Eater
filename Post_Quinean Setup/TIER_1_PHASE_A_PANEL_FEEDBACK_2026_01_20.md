# Expert Panel Feedback on Phase A Implementation
## Tier 1 Backend Infrastructure Review
**Date**: January 20, 2026
**Status**: Panel Review Complete

---

## PANEL RESPONSES TO IMPLEMENTATION DECISIONS

---

### DR. JUDEA PEARL — Causal Inference

**On D5 (Graph Export Format)**:

The correlational edge flagging is correct. I want to emphasize: the `is_correlational` flag must be used consistently in visualization. CORRELATIONAL edges should NEVER have arrowheads in the GUI—this is not just a style preference but a semantic requirement.

**Additional concern**: I see that `CausalDirection.COMMON_CAUSE` and `CausalDirection.MEDIATED` are tracked but I don't see explicit handling in the graph export for latent variables. When a belief has `causal_direction=COMMON_CAUSE`, the graph should ideally show the latent confounder as a separate (grayed/dashed) node.

**Recommendation for Phase B**: Add optional latent variable nodes for COMMON_CAUSE relationships. Even if users can't edit them, seeing "Unknown Common Cause" nodes will prevent causal misinterpretation.

**On Q4 (Publication Bias)**:

Option A (simple null ratio) is acceptable for now, but I recommend planning for Option B (funnel plot) in a future phase. The funnel plot is standard in meta-analysis for a reason—it visualizes asymmetry that a single ratio cannot capture.

---

### DR. NANCY CARTWRIGHT — Philosophy of Science

**On D1 (SourceDepth) and Q1 (Credence Adjustment)**:

The current implementation (Option C: warning badge only) is too permissive. Abstracts systematically overstate effect sizes and omit crucial methodology details.

**My recommendation**: Option B (cap at 0.5 maximum) for causal claims specifically.

Implementation logic:
```python
if belief.source_depth == SourceDepth.ABSTRACT:
    if is_causal_claim(belief):
        belief.credence.value = min(belief.credence.value, 0.5)
    # Non-causal claims can keep original credence with badge
```

This respects epistemic humility without penalizing descriptive findings.

**On D2 (EnablingConditions)**:

The structure is good but incomplete. Add:
- `temporal_order`: Optional[str] — "exposure must precede outcome by >1 hour"
- `dose_response`: Optional[bool] — Does the effect scale with dosage?

These are critical for capacity claims. Without temporal order, we cannot distinguish "A enables B" from "A and B co-occur."

**On Q3 (Duplicate Matching)**:

Option B (title + year fuzzy match) is necessary. Researchers cite the same paper with slightly different titles all the time. However, add a confirmation step—don't auto-merge, show "Possible duplicate: [title]. Merge?"

---

### DR. HERBERT SIMON — Bounded Rationality

**On D3 (Credence History) and D11 (Stopping Rules)**:

The implementation is sound. The stability-based stopping is exactly what I advocated for.

One refinement: The current `stability_window=5` is fixed. Consider adaptive windows based on topic maturity:
- New topic (few papers): window=3
- Established topic (many papers): window=7

This prevents premature stopping in well-studied areas where 5 papers is noise.

**On D6 (Progressive Disclosure)**:

The simplified view is good, but I'd add one more level:

1. **Headline**: Single sentence ("Natural light improves mood — High confidence")
2. **Summary**: Traffic light + source count + disagreement flag (current simplified)
3. **Detail**: Full panel

The headline level serves quick scanning when users are reviewing many beliefs.

**On Q2 (Oscillation Threshold)**:

Option B (adaptive based on mean) is theoretically better but adds complexity. For now, Option A (fixed 0.5) is acceptable because:
- 0.5 is the natural decision boundary (more likely true vs. false)
- Users understand "crossed the 50% line multiple times"

Revisit if users report false positives (contested flag on beliefs that aren't truly contested).

---

### DR. MARCIA BATES — Information Science

**On D9 (Citation Suggestions)**:

Excellent implementation. Add one more category:

- `methodologically_diverse`: Papers using different methods to study the same question

This counteracts the citation network's tendency toward methodological homogeneity. Implementation: track `study_type` in PaperMetadata and suggest papers with different study types.

**On Q3 (Duplicate Matching)**:

Strongly support Option B. Also consider matching on DOI variations:
- `10.1234/abc` should match `https://doi.org/10.1234/abc`
- Handle case differences (`10.1234/ABC` = `10.1234/abc`)

I see you normalize DOIs already—good. Make sure the duplicate check uses the same normalization.

**On Q5 (API Key Strategy)**:

Option C (start shared, migrate at scale) is correct. But add explicit logging:
- Track API calls per user
- Alert when approaching rate limits
- Provide clear migration path documentation

Users should know their API usage before being asked to provide keys.

---

### DR. RACHEL KAPLAN — Environmental Psychology

**On D2 (EnablingConditions)**:

Add domain-specific enabling conditions for environmental psychology:
- `environmental_quality`: Optional[str] — "quiet, no traffic noise"
- `temporal_context`: Optional[str] — "during work hours", "morning exposure"
- `social_context`: Optional[str] — "alone", "with others"

Many environmental effects are moderated by these factors. A finding about "natural light improves mood" may only hold when the person is alone (social facilitation effects), during work hours (not leisure), in quiet environments (not competing stressors).

**On Publication Bias (D10)**:

Environmental psychology has particularly severe publication bias. The field loves positive results about nature and design interventions.

**Domain-specific recommendation**: When the topic involves nature/biophilia, automatically upgrade publication bias risk by one level:
- LOW → MODERATE
- MODERATE → HIGH

This isn't pessimism—it's empirically justified (see Ferguson & Heene, 2012, on effect size inflation in psychology).

---

### WORKFLOW DESIGNER

**On D6 (Progressive Disclosure)**:

The implementation is on track. For Phase B, ensure the GUI transitions smoothly between levels:
- Click belief → show summary
- Click "Details" → expand to full
- Click outside → collapse back

Avoid modal dialogs—they break flow. Use slide-out panels or expandable cards.

**On D11 (Stopping Rules)**:

The stability report is comprehensive but dense. For the GUI, create a visual summary:

```
┌─────────────────────────────────────────────────┐
│ STABILITY STATUS                                │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│ [████████████░░░░░░] 72% Stable                │
│                                                 │
│ 📊 47 papers processed                         │
│ ✅ 36 beliefs stable                           │
│ ⚠️  8 beliefs converging                       │
│ ❌  3 beliefs contested                        │
│                                                 │
│ ⚡ Publication bias: MODERATE                  │
│                                                 │
│ [View Details] [Continue Search] [Stop]        │
└─────────────────────────────────────────────────┘
```

---

### GUI/UX EXPERT

**On D5 (Graph Export)**:

The data structure is good. For Phase B visualization:

1. **Node encoding confirmed**:
   - Size = credence (0.3–1.0 scale) ✓
   - Color = outcome category ✓
   - Border = conflict indicator ✓

2. **Edge encoding refinement**:
   - CORRELATIONAL: dotted line, no arrowhead, 40% opacity
   - SUPPORTS: solid green, arrowhead
   - CONTRADICTS: solid red, arrowhead
   - BRIDGES: purple dashed, arrowhead
   - EXPLAINS: blue solid, arrowhead

3. **Contested belief encoding**:
   - Pulsing/breathing animation (subtle)
   - Or: dual-colored node (split down middle)

**On Phase B priority**:

Build the graph visualization first, then the detail panel. Users need to SEE the web before they need details about individual nodes.

---

### SYSTEMS ARCHITECT

**On D7 (Identifier Detection) and D8 (Duplicate Detection)**:

Implementation is clean. For production:

1. **Add retry logic** for transient API failures
2. **Add circuit breaker** for persistent failures (don't keep hitting a dead API)
3. **Cache API responses** for 24 hours (papers don't change often)

**On Q5 (API Key Strategy)**:

Option C with modification:
- Phase 1: Shared key with strict rate limiting (3 req/sec for PubMed)
- Phase 2: User keys stored encrypted, used preferentially when available
- Phase 3: Require user keys when shared quota exhausted

Store keys in environment variables or a secrets manager, never in code or config files.

**On mock clients**:

The mock clients are good for testing. For production, create real clients with the same interface. Consider using `httpx` with async support for better performance when fetching multiple papers.

---

### EPISTEMOLOGIST

**On D4 (Oscillation Detection)**:

The implementation correctly identifies oscillation as epistemically significant.

**Refinement needed**: Distinguish between:
1. **Measurement oscillation**: Same construct, different operationalizations give different results
2. **Scope oscillation**: Same construct, different contexts give different results
3. **Genuine disagreement**: Same methods, same context, different results

Only type 3 is true scientific disagreement. Types 1 and 2 suggest we need belief splitting (per Cartwright's scope conditions).

**Implementation suggestion**: When marking a belief contested, log the oscillation pattern. In Phase B, allow users to "explain oscillation" by specifying whether it's measurement, scope, or genuine.

**On D11 (Stopping Rules) framing**:

The framing "given current evidence" is exactly right. One addition to the recommendation text:

> "Genuinely new evidence (different methods, populations, or paradigms) could still cause substantial revision."

Add:

> "The system cannot distinguish between 'consensus because true' and 'consensus because of shared biases.' Methodological diversity in sources is as important as quantity."

This honors Quinean fallibilism and warns against false confidence from apparent stability.

---

## PANEL DECISIONS ON OPEN QUESTIONS

### Q1: Abstract-Only Credence Adjustment

**Panel Decision**: Option B for causal claims, Option C for descriptive claims.

- Causal claims from abstracts: cap at 0.5
- Descriptive claims from abstracts: warning badge only

**Rationale** (Cartwright): Causal claims require methodology verification; descriptive claims are more robust to abstract-only extraction.

### Q2: Oscillation Threshold

**Panel Decision**: Option A (fixed at 0.5) for now.

**Rationale** (Simon): 0.5 is semantically meaningful and user-interpretable. Revisit if false positive rate exceeds 10%.

### Q3: Duplicate Matching

**Panel Decision**: Option B (title + year fuzzy match) with confirmation.

**Implementation**:
- Levenshtein distance < 3 on normalized title
- Year must match exactly
- Show confirmation dialog, don't auto-merge

**Rationale** (Bates): Citation variations are common; users should approve merges.

### Q4: Publication Bias Depth

**Panel Decision**: Option A now, Option B in Phase E.

**Rationale** (Pearl): Funnel plot requires minimum 10 studies and is a visualization feature. Implement in Phase E (Reporting & Visualization).

### Q5: API Key Strategy

**Panel Decision**: Option C with architect's modifications.

**Implementation**:
1. Shared key with rate limiting and logging
2. User keys when provided (encrypted storage)
3. Require user keys when shared quota exceeded
4. Clear documentation of migration path

---

## ADDITIONAL PANEL RECOMMENDATIONS

### R1: Add Temporal Order to EnablingConditions (Cartwright)

```python
temporal_order: Optional[str] = None  # "exposure precedes outcome by >1 hour"
dose_response: Optional[bool] = None
```

**Priority**: HIGH — Add before Phase B.

### R2: Add Methodological Diversity to Citation Suggestions (Bates)

Track `study_type` in citation suggestions. Suggest papers with different study types.

**Priority**: MEDIUM — Add in Phase C.

### R3: Add Latent Variable Visualization (Pearl)

For COMMON_CAUSE relationships, show placeholder latent nodes in graph.

**Priority**: MEDIUM — Add in Phase B.

### R4: Domain-Specific Bias Adjustment (Kaplan)

For nature/biophilia topics, auto-upgrade publication bias risk.

**Priority**: LOW — Add in Phase D.

### R5: Add Headline View Level (Simon)

Three levels instead of two: Headline → Summary → Detail.

**Priority**: MEDIUM — Add in Phase B.

### R6: Add Oscillation Type Classification (Epistemologist)

Track whether oscillation is measurement, scope, or genuine disagreement.

**Priority**: LOW — Add in Phase D.

---

## PHASE B APPROVED

The panel approves proceeding to Phase B (Evidence Explorer GUI) with the following incorporation:

**Must include in Phase B**:
1. R1 (Temporal order in EnablingConditions) — quick data model fix
2. Correlational edge rendering (no arrowhead, reduced opacity)
3. Three-level progressive disclosure (headline/summary/detail)
4. Slide-out detail panel (not modal)
5. Stability status visual summary

**Can defer to later phases**:
- R2 (Methodological diversity) → Phase C
- R3 (Latent variables) → Phase B if time permits, else Phase E
- R4 (Domain bias adjustment) → Phase D
- R6 (Oscillation types) → Phase D

---

## UPDATED DECISION LOG

| ID | Decision | Panel Verdict |
|----|----------|---------------|
| Q1 | Abstract credence | Cap causal claims at 0.5; badge for descriptive |
| Q2 | Oscillation threshold | Fixed at 0.5; revisit if >10% false positives |
| Q3 | Duplicate matching | Fuzzy match (Levenshtein < 3) + confirmation dialog |
| Q4 | Publication bias | Simple ratio now; funnel plot in Phase E |
| Q5 | API keys | Shared → User when provided → Required at quota |

---

*End of Panel Feedback*

**Proceed to Phase B implementation.**
