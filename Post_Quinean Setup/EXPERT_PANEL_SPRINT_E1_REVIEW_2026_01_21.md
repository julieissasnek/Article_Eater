# Expert Panel Review: Sprint E1 Implementation Decisions

**Date**: January 21, 2026
**Reviewing**: 5 autonomous decisions from Sprint E1 (Panel HIGH Priority)
**Panel**: Pearl, Cartwright, Simon, Bates, Kaplan

---

## E1.D1: Follow-up Type Nomenclature ("broader" → "scope")

### Pearl:
**Assessment**: APPROVE with minor concern

The change from "broader" to "scope" is epistemically cleaner. "Scope" directly references the conditions under which a causal relationship holds, which is precisely what researchers need to assess external validity. The question "Under what conditions does X affect Y?" is well-formed.

However, I would recommend also capturing the *direction* of scope inquiry. Are we asking about population scope, temporal scope, or mechanistic scope? Consider subdividing or at least documenting which scope dimension the follow-up targets.

### Cartwright:
**Assessment**: APPROVE

"Scope" is exactly right. This aligns with my work on evidence portability—the key question is always "will this work *here*?" not "what else is related?" The term "boundary conditions" was also acceptable but "scope" is more accessible to practitioners.

The implementation asking "Under what conditions..." is appropriate. I would add: consider generating scope questions that reference the *specific* populations or settings mentioned in the evidence, not just generic scope queries.

### Simon:
**Assessment**: APPROVE

From a bounded rationality perspective, "scope" is clearer than "broader" and reduces cognitive load. Users understand intuitively what "scope" means. The three-follow-up structure (deeper, scope, uncertainty) now forms a coherent triad that covers the essential epistemic questions.

No changes needed.

### Bates:
**Assessment**: APPROVE

The terminology change improves search behavior guidance. "Scope" suggests focused exploration of applicability conditions, while "broader" suggested unfocused expansion. Users are more likely to find relevant evidence when guided toward scope conditions.

One suggestion: the vocabulary bridge should include scope-related terms (population, setting, context, applicability) to help users formulate scope queries.

### Kaplan:
**Assessment**: APPROVE

For environmental psychology research, "scope" is essential. Effects of nature on attention, for instance, vary dramatically by duration, setting type (workplace vs. healthcare), and population (children vs. adults with ADHD). The scope question directly addresses these concerns.

Would recommend: the scope follow-up should, when possible, reference the ART components (being away, fascination, extent, compatibility) or prospect-refuge dimensions relevant to the query.

### Consensus: **APPROVE** (No changes required)
The "scope" terminology is appropriate. Minor enhancement opportunities noted for future sprints.

---

## E1.D2: Contested Evidence Structure

### Pearl:
**Assessment**: MODIFY

The structure is sound, but I have concerns about the credence threshold:

1. **0.5 threshold is problematic**: Credence represents belief strength, not support/contradiction. A belief with credence 0.45 might still *support* a claim—it's just uncertain. You're conflating epistemic uncertainty with directionality.

**Recommendation**: Contested evidence should be identified by:
- Explicit `contested=True` flag on beliefs
- Presence of beliefs with *opposite* causal directions (X increases Y vs X decreases Y)
- NOT simply by credence values

2. **Reasons for disagreement**: Good start, but missing the most important reason—different causal model assumptions. Add detection for when studies assume different confounders or causal structures.

### Cartwright:
**Assessment**: MODIFY

I agree with Pearl on the threshold issue. Additionally:

1. **Source depth asymmetry is key**: If supporting evidence is abstract-only and contradicting evidence is full-text, this is not symmetric disagreement—it's an evidence quality gap. The "reasons for disagreement" should distinguish between:
   - Genuine scientific disagreement (same quality, different conclusions)
   - Evidence quality asymmetry (one side has weaker evidence)
   - Scope mismatch (studies measured different things)

2. **Add measurement method differences**: If one study used self-report and another used physiological measures, that's a critical reason for disagreement in neuroarchitecture research.

### Simon:
**Assessment**: APPROVE with minor modification

The structure is appropriate for bounded rationality—users can quickly see both sides. The 5-item limit per side is sensible.

**Modification**: Consider adding a "controversy severity" indicator (low/medium/high) based on the balance of evidence and the strength of disagreement. This helps users quickly assess how much attention the controversy deserves.

### Bates:
**Assessment**: APPROVE

The contested evidence section addresses a core information need. Users searching for evidence need to know when the literature disagrees.

**Enhancement**: Consider showing the *vocabulary* used by each side. Sometimes disagreements are terminological (one side calls it "stress reduction", the other "relaxation response"). Transparent vocabulary helps users understand apparent contradictions.

### Kaplan:
**Assessment**: APPROVE with domain note

For environmental psychology, disagreements often stem from:
- Indoor vs outdoor study settings
- Short-term vs long-term exposure
- Laboratory vs field conditions

Recommend adding these as detection patterns for "reasons for disagreement."

### Consensus: **MODIFY** (Priority: MEDIUM)

**Required changes**:
1. Revise contested detection logic to use explicit flags and directional opposition, not credence threshold
2. Add measurement method differences to reasons for disagreement
3. Distinguish evidence quality asymmetry from genuine scientific disagreement

**Deferred enhancements**:
- Controversy severity indicator
- Vocabulary comparison between sides

---

## E1.D3: Taxonomy-Driven Outcomes

### Pearl:
**Assessment**: APPROVE

Dynamic outcomes from taxonomy is the correct architectural choice. The fallback is appropriate for robustness.

No concerns.

### Cartwright:
**Assessment**: APPROVE with note

The depth limit of 2 is reasonable for gap analysis. Going deeper would overwhelm users with specificity. However, ensure the gap analysis *explains* what each missing outcome means (e.g., "cog.attention" should display as "Cognitive Attention" not the ID).

### Simon:
**Assessment**: APPROVE

The fallback mechanism is good satisficing design. If the taxonomy fails, users still get meaningful gap analysis. The transparency of indicating "taxonomy" vs "fallback" source is excellent.

**Question**: Should the depth be configurable per report type? Executive summaries might want depth 1, detailed reports might want depth 3.

### Bates:
**Assessment**: APPROVE

Taxonomy-driven is the right approach for vocabulary control. Static lists become stale.

**Enhancement**: The fallback outcomes should be periodically reviewed to ensure they still represent the core domain. Consider generating the fallback from taxonomy statistics (most frequently referenced outcomes).

### Kaplan:
**Assessment**: APPROVE

The fallback outcomes appropriately cover the core neuroarchitecture outcomes. I would add `physio.stress` to the fallback (physiological stress measures are distinct from affect.stress).

### Consensus: **APPROVE** (Minor enhancement)

**Minor change**:
- Add `physio.stress` to fallback outcomes
- Display human-readable names, not just IDs, in gap reports

---

## E1.D4: Confounder Coverage Gap Detection

### Pearl:
**Assessment**: MODIFY

This is **critical** functionality and I'm glad it was prioritized. However:

1. **Keyword list is incomplete**. Missing important terms:
   - `propensity score`
   - `instrumental variable`
   - `difference-in-differences`
   - `regression discontinuity`
   - `matching`
   - `stratified`
   - `blocked`
   - `within-subjects` (implicit control)

2. **Should distinguish confounder TYPES**:
   - Known confounders mentioned (good)
   - Statistical control mentioned (partial)
   - Causal identification strategy mentioned (best)

3. **Abstract-only weighting**: YES, absolutely. Abstract-only causal claims without confounder mention should be flagged more severely than full-text claims. The gap report should prioritize these.

### Cartwright:
**Assessment**: MODIFY

I strongly support Pearl's additions. Also:

1. **Add domain-specific confounders**: For neuroarchitecture:
   - `socioeconomic` (access to natural environments correlates with SES)
   - `self-selection` (people who choose window seats may differ)
   - `building age` (older buildings have different characteristics)
   - `climate` / `latitude` (affects daylight availability)

2. **Severity weighting**: Implement Pearl's suggestion. Create three levels:
   - CRITICAL: Abstract-only causal claim, no confounder mention
   - WARNING: Full-text causal claim, no confounder mention
   - INFO: Associational claim, no confounder mention (less concerning)

### Simon:
**Assessment**: APPROVE

The keyword approach is appropriate satisficing. Perfect confounder detection would require NLP/semantic analysis; keywords are good enough for flagging gaps.

**Suggestion**: Consider providing a "confounder checklist" template that researchers can use to assess flagged beliefs manually.

### Bates:
**Assessment**: APPROVE

The keyword list covers standard statistical terminology. Users searching for methodological rigor will find this helpful.

### Kaplan:
**Assessment**: APPROVE with domain additions

Add environmental psychology specific controls:
- `baseline` (baseline measurement before intervention)
- `pre-post` (pre-post design)
- `seasonal` / `seasonality` (outdoor studies vary by season)

### Consensus: **MODIFY** (Priority: HIGH)

**Required changes**:
1. Expand keyword list per Pearl (propensity score, instrumental variable, matching, etc.)
2. Add domain-specific confounders per Cartwright (socioeconomic, self-selection, climate)
3. Implement severity weighting (CRITICAL/WARNING/INFO) based on source depth
4. Add Kaplan's environmental psychology terms (baseline, pre-post, seasonal)

---

## E1.D5: Three-Tier Causal Classification

### Pearl:
**Assessment**: MODIFY

This is the most important decision and requires careful refinement:

1. **Tier definitions need tightening**:
   - CAUSAL should require EITHER experimental design OR explicit causal identification strategy
   - SUGGESTIVE should be the default for observational studies with effect language
   - ASSOCIATIONAL should be clearly correlational only

2. **The "experimental context boost" is problematic**: Currently, experimental context + suggestive language → CAUSAL. This is too permissive. An RCT that says "X affects Y" should still be CAUSAL (because experimental), but the tier should be determined by design, not boosted by it.

**Recommendation**: Restructure as:
```
IF experimental_design THEN
    IF causal_language THEN CAUSAL (high confidence)
    ELIF suggestive_language THEN CAUSAL (medium confidence)
    ELSE ASSOCIATIONAL
ELIF causal_language AND (mechanism OR confounder_control) THEN CAUSAL
ELIF suggestive_language THEN SUGGESTIVE
ELSE ASSOCIATIONAL
```

3. **Add CAUSAL-INSUFFICIENT tier**: For claims that use causal language but from observational designs without confounder control. This is distinct from SUGGESTIVE.

4. **Quasi-experimental designs**: Should be treated as between experimental and observational. Natural experiments, regression discontinuity, etc. should boost toward CAUSAL but not fully.

### Cartwright:
**Assessment**: MODIFY

I agree with Pearl's restructuring. Additional concerns:

1. **Mechanism mention alone shouldn't boost to CAUSAL**: A mechanism description doesn't establish causation—it provides plausibility. Move mechanism from confidence booster to a separate "plausibility" indicator.

2. **Add "scope of causal claim" indicator**: Does the claim assert universal causation ("X always causes Y") or conditional causation ("X causes Y under conditions C")? The latter is more defensible.

3. **Hedged language handling is good**: "May cause" as SUGGESTIVE is correct.

### Simon:
**Assessment**: APPROVE with simplification concern

The three tiers are cognitively appropriate. Users can understand CAUSAL/SUGGESTIVE/ASSOCIATIONAL.

**Concern**: Pearl's 4-tier proposal (adding CAUSAL-INSUFFICIENT) may exceed cognitive capacity. Consider whether the warning system can handle this distinction instead of a fourth tier.

**Suggestion**: Keep three tiers but use confidence scores and warnings to convey the nuances Pearl describes.

### Bates:
**Assessment**: APPROVE

The classification improves search result quality. Users can filter by causal strength.

**Enhancement**: Expose the tier in search results with clear icons/badges. Consider adding tier to the vocabulary bridge so users can search for "causal evidence about X."

### Kaplan:
**Assessment**: APPROVE with domain patterns

Add neuroarchitecture-specific patterns:

CAUSAL:
- `design intervention` (implies experimental manipulation)
- `built environment manipulation`
- `lighting intervention`

SUGGESTIVE:
- `restorative effect` (ART terminology suggests mechanism)
- `biophilic response`

ASSOCIATIONAL:
- `preference for` (preference studies are correlational)
- `rated higher` / `rated as` (rating studies without manipulation)

### Consensus: **MODIFY** (Priority: HIGH)

**Required changes**:
1. Restructure tier logic per Pearl: design-first, then language
2. Remove mechanism from confidence booster; make it separate indicator
3. Add quasi-experimental detection (natural experiment, regression discontinuity)
4. Add neuroarchitecture patterns per Kaplan
5. Keep three tiers (per Simon) but add nuanced warnings

**Keep as-is**:
- Hedged language handling
- Confidence scoring (adjust weights)
- Warning generation

---

## Summary of Panel Recommendations

| Decision | Verdict | Priority | Changes Needed |
|----------|---------|----------|----------------|
| E1.D1 | APPROVE | — | None required |
| E1.D2 | MODIFY | MEDIUM | Fix contested detection logic, add measurement method reasons |
| E1.D3 | APPROVE | LOW | Add physio.stress to fallback, show human-readable names |
| E1.D4 | MODIFY | HIGH | Expand keywords, add severity weighting |
| E1.D5 | MODIFY | HIGH | Restructure tier logic, add domain patterns |

---

## Implementation Priority

### Immediate (This Sprint)
1. **E1.D4**: Expand confounder keywords + severity weighting
2. **E1.D5**: Restructure causal classifier logic + add domain patterns

### Next Sprint
3. **E1.D2**: Fix contested evidence detection
4. **E1.D3**: Minor enhancements

### Deferred
- E1.D2 controversy severity indicator
- E1.D2 vocabulary comparison
- E1.D5 four-tier consideration
