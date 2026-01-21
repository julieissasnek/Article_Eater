# Expert Panel Responses: Phase C-D Implementation Review

**Date**: January 21, 2026
**Review Type**: Retrospective design validation
**Decisions Reviewed**: 12 (Phases C1-C4, D1-D2)

---

## Panel Response: Decision Point 1 — Query Type Taxonomy

### Pearl:
**Assessment**: Modify

The taxonomy conflates epistemically distinct query types. DOES_X_AFFECT_Y and WHAT_IS both handle causal questions without distinguishing *causal* from *associational* queries. In my framework, "Does X affect Y?" implies intervention (do-calculus), while "Is X associated with Y?" is observational. The system should distinguish:
- `DOES_X_CAUSE_Y` (interventional)
- `IS_X_ASSOCIATED_WITH_Y` (observational)
- `WHAT_MEDIATES_X_Y` (mechanism identification)

**Priority**: High

### Cartwright:
**Assessment**: Modify

I support Pearl's concern but add: the FOR_WHOM and WHEN_DOES categories are critically important but underspecified. These scope queries are where evidence transferability lives or dies. The taxonomy should elevate scope queries and perhaps add:
- `UNDER_WHAT_CONDITIONS` (enabling conditions)
- `WITH_WHAT_MECHANISMS` (the *how* question)

**Priority**: High

### Simon:
**Assessment**: Approve

Thirteen types is already approaching cognitive limits. The current taxonomy is *satisficing*—it covers the main use cases without overwhelming users. I would resist adding more types unless usage data shows clear gaps. The meta-queries (WHY_BELIEVE, WHAT_CONTRADICTS) are appropriate for researchers who need to understand the epistemic structure, not just the conclusions.

**Priority**: Low (if changes made, ensure UI simplicity)

### Bates:
**Assessment**: Modify

The taxonomy is oriented toward question *answering* but neglects question *exploration*. Researchers often don't know what to ask. Consider adding:
- `BROWSE_TOPIC` (non-question exploration)
- `RELATED_TO` (associative discovery)

Also: the WHAT_EVIDENCE type should distinguish "evidence for" vs "evidence against"—these are different search behaviors.

**Priority**: Medium

### Kaplan:
**Assessment**: Modify

For neuroarchitecture specifically, I note missing query types for *design implications*:
- `HOW_TO_DESIGN_FOR` (translating evidence to practice)
- `WHAT_ARE_TRADEOFFS` (multi-outcome considerations)

Environmental design decisions always involve tradeoffs between competing outcomes (e.g., natural light vs. thermal comfort). The taxonomy should support this.

**Priority**: Medium

### Consensus:
**Assessment**: MODIFY
**Priority**: High

**Required Changes**:
1. Add DOES_X_CAUSE_Y vs IS_X_ASSOCIATED distinction (Pearl) — HIGH
2. Add UNDER_WHAT_CONDITIONS for scope (Cartwright) — HIGH
3. Consider BROWSE_TOPIC for exploration (Bates) — MEDIUM
4. Defer design-translation queries to Phase E (Kaplan) — LOW

---

## Panel Response: Decision Point 2 — Vocabulary Bridge (Static Mappings)

### Pearl:
**Assessment**: Approve

Static mappings are appropriate here. Causal vocabulary is precise—"cause," "effect," "intervention" have specific meanings that shouldn't be diluted by embedding similarity. Dynamic expansion risks conflating causally distinct concepts.

**Priority**: N/A

### Cartwright:
**Assessment**: Modify

I'm concerned about *directional* synonyms. "Improve" and "enhance" imply positive direction; "reduce" and "decrease" imply negative. The vocabulary bridge should preserve directionality metadata so we know when synonyms flip valence. Also: domain-specific terms like "biophilic" may not have good synonyms—flag these as *terminus* terms.

**Priority**: Medium

### Simon:
**Assessment**: Approve

Static mappings are maintainable and interpretable. Dynamic/embedding approaches create a black box. For a research tool, users need to understand *why* a query retrieved certain results. Static mappings support this transparency. The 20+ terms is a reasonable starting vocabulary.

**Priority**: N/A

### Bates:
**Assessment**: Modify

Static is fine for the core vocabulary, but the system needs a **growth mechanism**. I recommend:
1. Log unmatched query terms
2. Surface frequent unmatched terms to administrators
3. Allow curated additions (not user-editable, but admin-reviewable)

This prevents vocabulary drift while maintaining control. Also: show users the expansions applied ("Also searching for: daylight, sunlight...") per my transparency principle.

**Priority**: Medium

### Kaplan:
**Assessment**: Modify

The neuroarchitecture domain has evolving terminology. "Biophilic design" didn't exist 30 years ago. The vocabulary should include:
- Historical synonyms (e.g., "nature contact" → "biophilia")
- Construct mappings (e.g., "restoration" → "stress recovery" + "attention restoration")

Consider a versioned vocabulary with date ranges for when terms were in use.

**Priority**: Medium

### Consensus:
**Assessment**: MODIFY
**Priority**: Medium

**Required Changes**:
1. Add directionality metadata to synonyms (Cartwright) — MEDIUM
2. Implement unmatched term logging for vocabulary growth (Bates) — MEDIUM
3. Ensure expansion transparency in UI (Bates) — Already implemented ✓
4. Document domain-specific term evolution (Kaplan) — LOW

---

## Panel Response: Decision Point 3 — Causal Claim Detection via Keywords

### Pearl:
**Assessment**: Rethink

This is my primary concern. Keyword detection fundamentally misunderstands causation. "Improve," "reduce," "affect" are **not** causal claims—they are directional associations that *may* reflect causation. True causal claims require:
1. Explicit causal language ("X causes Y")
2. Interventional study design (RCT, natural experiment)
3. Mechanism specification

The current approach will flag correlational findings as causal, polluting the evidence base. I recommend a three-tier classification:
- **Causal**: Explicit causal language + experimental design
- **Suggestive**: Directional language, observational design
- **Associational**: Correlation only

**Priority**: HIGH

### Cartwright:
**Assessment**: Rethink

I strongly support Pearl here. Additionally, "affect" and "impact" are often used loosely in abstracts to attract attention. The *abstract* may say "natural light improves productivity" while the *full text* reveals a correlational study with numerous confounds. This is exactly why I insisted on the abstract-only warning—but we should go further and distinguish *claimed* causation from *supported* causation.

**Priority**: HIGH

### Simon:
**Assessment**: Modify

Pearl and Cartwright are technically correct, but we must balance precision against usability. A three-tier system adds complexity. I suggest:
1. Keep keyword detection as a **flag** (not a classification)
2. Present flagged items with a "causal language detected—verify study design" prompt
3. Allow users to upgrade/downgrade the classification after review

This satisfices: we catch potential causal claims without requiring perfect automated classification.

**Priority**: Medium (compromise position)

### Bates:
**Assessment**: Approve with reservations

For *retrieval* purposes, keyword detection is appropriate—we want to find documents that *discuss* causation, even if they don't establish it. The classification (causal vs. not) should happen at a separate layer, not in the retrieval system. Don't conflate search with epistemics.

**Priority**: Low (retrieval is fine; classification needs work)

### Kaplan:
**Assessment**: Modify

In environmental psychology, many findings are quasi-experimental (can't randomly assign people to buildings). The field has conventions for describing these: "associated with," "linked to," "predicts." The keyword list should be calibrated to our field's hedging conventions. "Predicts" is common in our literature and implies a statistical relationship, not necessarily causation.

**Priority**: Medium

### Consensus:
**Assessment**: RETHINK
**Priority**: HIGH

**Required Changes**:
1. Implement three-tier classification: Causal / Suggestive / Associational (Pearl) — HIGH
2. Require study design information to confirm causal tier (Cartwright) — HIGH
3. Use keyword detection as flag, not classification (Simon compromise) — MEDIUM
4. Add field-specific hedging terms: "predicts," "linked to" (Kaplan) — MEDIUM

---

## Panel Response: Decision Point 4 — Confidence Level Thresholds

### Pearl:
**Assessment**: Modify

The thresholds are arbitrary without calibration data. More importantly, averaging credences is epistemically problematic. If I have two beliefs at 0.90 and 0.30 about the same claim, the average (0.60) misrepresents the situation—we have *conflicting* evidence, not *medium* confidence. The system should report:
- Central tendency (mean or median)
- Dispersion (variance or range)
- Conflict indicator (bimodality)

**Priority**: High

### Cartwright:
**Assessment**: Modify

I agree with Pearl on conflict detection. Additionally, the 0.70 threshold for "high confidence" is too generous for causal claims from abstracts. I would apply different thresholds based on source depth:
- Full text: 0.70 = high
- Abstract only: 0.85 = high (higher bar)
- Metadata only: Cannot be "high"

This builds source quality into the confidence interpretation.

**Priority**: High

### Simon:
**Assessment**: Approve

Three tiers (high/medium/low) is cognitively appropriate. Users can't meaningfully distinguish more gradations. The specific thresholds (0.70/0.40) are reasonable starting points. I would resist adding complexity unless user studies show confusion. The conflict detection Pearl suggests is valuable but should be a separate indicator, not a fourth tier.

**Priority**: Low

### Bates:
**Assessment**: Approve

For information *presentation*, three tiers is appropriate. Users need actionable categories, not precise probabilities. I agree with Simon that conflict should be a separate indicator. Consider visual encoding: color + icon rather than just label.

**Priority**: Low

### Kaplan:
**Assessment**: Approve

In our field, 0.70 is reasonable for "preponderance of evidence." Environmental psychology rarely achieves higher certainty due to the complexity of real-world settings. The thresholds seem calibrated to our domain.

**Priority**: Low

### Consensus:
**Assessment**: MODIFY
**Priority**: Medium

**Required Changes**:
1. Add conflict/dispersion indicator separate from confidence level (Pearl) — HIGH
2. Apply source-depth-adjusted thresholds for causal claims (Cartwright) — MEDIUM
3. Keep three tiers for display; add variance metadata (Simon/Bates) — MEDIUM
4. Current thresholds acceptable for domain (Kaplan) — No change needed

---

## Panel Response: Decision Point 5 — Five Stopping Criteria Selection

### Pearl:
**Assessment**: Modify

The criteria are reasonable but missing a crucial one: **causal sufficiency**. For causal queries, we should not stop until we have:
1. Evidence on the main effect
2. Evidence on at least one mechanism
3. Evidence on key confounders

Saturation of correlational evidence doesn't establish causation.

**Priority**: High (for causal queries)

### Cartwright:
**Assessment**: Modify

I want to add: **scope coverage**. We should not stop until we have evidence from multiple populations/settings, or explicitly flag that evidence is scope-limited. A belief supported by 10 studies all from Scandinavian offices has poor scope coverage.

**Priority**: High

### Simon:
**Assessment**: Approve

Five criteria is appropriate. More criteria create decision paralysis. The current set covers quantity (count), quality (confidence), diversity (coverage), diminishing returns (saturation), and stability. This is a reasonable satisficing set. Pearl and Cartwright's additions are valid but should be query-type-specific, not universal.

**Priority**: Low (resist complexity creep)

### Bates:
**Assessment**: Modify

The saturation detection (first-5-words theme hashing) is indeed crude. Saturation should be detected by:
1. Diminishing new vocabulary (new terms per document decreasing)
2. Increasing citation overlap (new papers citing same sources)
3. Redundant claim content (semantic similarity)

First-5-words is a proxy but misses thematic saturation.

**Priority**: Medium

### Kaplan:
**Assessment**: Approve

For systematic reviews in our field, these criteria match standard practice. Saturation (sometimes called "theoretical saturation") is how we know when to stop literature review. Five studies is a bit low as a minimum for environmental psychology—I'd suggest 8-10 for empirical claims.

**Priority**: Low (consider raising min_beliefs default)

### Consensus:
**Assessment**: MODIFY
**Priority**: Medium

**Required Changes**:
1. Add query-type-specific criteria: causal sufficiency for causal queries (Pearl) — MEDIUM
2. Add scope coverage criterion for external validity (Cartwright) — MEDIUM
3. Improve saturation algorithm beyond first-5-words (Bates) — MEDIUM
4. Consider raising min_beliefs default to 8 (Kaplan) — LOW

---

## Panel Response: Decision Point 6 — Stopping Decision Logic (60% Threshold)

### Pearl:
**Assessment**: Modify

60% majority is reasonable for exploratory queries but inappropriate for causal claims. For causal queries, I would require:
- Minimum evidence: MET
- Confidence: MET
- At least one mechanism belief: MET

This is not 60%—it's specific required criteria.

**Priority**: High (for causal queries)

### Cartwright:
**Assessment**: Modify

I agree the threshold should be query-type-dependent. For policy-relevant claims (which neuroarchitecture often produces), I would require scope coverage before stopping. We should not recommend stopping if all evidence comes from a single context.

**Priority**: High

### Simon:
**Assessment**: Approve

60% is a reasonable satisficing threshold. It prevents premature stopping while not requiring perfection. The logic (minimum evidence as gate + 60% of quality criteria) is sound. I would resist making this configurable per query type—it adds cognitive burden on users.

**Priority**: Low

### Bates:
**Assessment**: Approve

The 60% threshold with minimum evidence gate is sensible. It's transparent and explainable. Making it configurable adds complexity without clear benefit for most users.

**Priority**: Low

### Kaplan:
**Assessment**: Approve

For our field, 60% seems reasonable. We rarely achieve certainty. The recommendation to continue searching is valuable guidance for researchers who might otherwise stop too early.

**Priority**: Low

### Consensus:
**Assessment**: MODIFY (for specific cases)
**Priority**: Medium

**Required Changes**:
1. Implement query-type-specific logic for causal queries (Pearl) — HIGH
2. Add scope coverage requirement before stopping (Cartwright) — MEDIUM
3. Keep 60% as default for exploratory queries (Simon/Bates/Kaplan) — No change

---

## Panel Response: Decision Point 7 — Expected Outcome Categories

### Pearl:
**Assessment**: Approve

Eight categories is manageable. The categories cover the main outcomes studied in neuroarchitecture. I have no strong objection.

**Priority**: N/A

### Cartwright:
**Assessment**: Modify

The categories should map to established outcome taxonomies in the field. Are these the CNFA canonical outcomes? If so, approve. If not, align with whatever taxonomy the domain uses. Also: outcomes should have **defined measurement indicators** so "cognition" means something specific.

**Priority**: Medium

### Simon:
**Assessment**: Approve

Eight is a reasonable number of categories. More would strain users' ability to reason about gaps. The current list covers the major areas of neuroarchitecture research.

**Priority**: Low

### Bates:
**Assessment**: Modify

Hardcoding is problematic. The expected outcomes should be **derived from the taxonomy** used elsewhere in the system (Sprint 4 outcome taxonomy). Don't maintain two separate lists. This creates synchronization bugs.

**Priority**: High (architecture concern)

### Kaplan:
**Assessment**: Modify

The list is missing key environmental psychology outcomes:
- **Sleep/circadian**: Major area of light research
- **Social behavior**: Collaboration, interaction
- **Wayfinding/navigation**: Spatial cognition
- **Restorative experience**: Core to my work

I would expand to 12 categories aligned with APA Division 34 (Environmental Psychology) standard outcomes.

**Priority**: High (domain completeness)

### Consensus:
**Assessment**: MODIFY
**Priority**: High

**Required Changes**:
1. Derive expected outcomes from Sprint 4 taxonomy, not hardcoded (Bates) — HIGH
2. Add missing domain outcomes: sleep, social, wayfinding, restoration (Kaplan) — HIGH
3. Ensure outcomes have measurement indicators (Cartwright) — MEDIUM

---

## Panel Response: Decision Point 8 — Quality Score Formula (40/30/30)

### Pearl:
**Assessment**: Modify

The formula doesn't account for study design. A well-designed RCT at the abstract level may be higher quality than a poorly-designed observational study with full text. I would add:
- Study design quality (0.20)
- Adjust source depth to 0.30

**Priority**: Medium

### Cartwright:
**Assessment**: Modify

I appreciate that source depth is weighted highest—this reflects my concern about abstract-only claims. However, 40% may not be enough for causal claims. For causal claims specifically, I would weight source depth at 50% or higher. Corroboration (multiple sources saying the same thing) is only valuable if those sources are independent—replication, not citation chains.

**Priority**: High

### Simon:
**Assessment**: Approve

The 40/30/30 formula is transparent and reasonable. Users can understand what drives quality scores. I would resist adding more factors—each addition reduces interpretability. Keep it simple.

**Priority**: Low

### Bates:
**Assessment**: Approve

The formula is reasonable for a composite score. I appreciate that it's documented and explainable. Consider showing the component scores (not just the total) so users understand what's driving quality.

**Priority**: Low (add component display)

### Kaplan:
**Assessment**: Modify

Recency should factor in. Environmental psychology has evolved significantly—a 1990 study of "sick building syndrome" uses different methods than a 2020 study. Older evidence isn't necessarily lower quality, but recency affects applicability. Consider a recency adjustment factor.

**Priority**: Medium

### Consensus:
**Assessment**: MODIFY
**Priority**: Medium

**Required Changes**:
1. Add study design quality factor (Pearl) — MEDIUM
2. Increase source depth weight for causal claims (Cartwright) — MEDIUM
3. Display component scores, not just total (Bates) — LOW
4. Consider recency adjustment for applicability (Kaplan) — LOW

---

## Panel Response: Decision Point 9 — Gap Analysis Categories

### Pearl:
**Assessment**: Modify

Missing gap category: **Confounder coverage**. For causal claims, we should flag when known confounders haven't been addressed in the evidence. If light affects productivity, have we controlled for temperature, noise, time of day? Gap analysis should surface missing confounder evidence.

**Priority**: High

### Cartwright:
**Assessment**: Approve

The five categories are well-chosen. Abstract-only causal claims is exactly what I would flag. The 25% uncertainty threshold is reasonable—it's roughly where credence intervals start to overlap meaningfully with alternatives.

**Priority**: N/A

### Simon:
**Assessment**: Approve

Five gap categories is appropriate. More would overwhelm users. The categories are distinct and actionable. I would not add more unless specific needs emerge.

**Priority**: Low

### Bates:
**Assessment**: Modify

Add: **Vocabulary gaps**. If user queries frequently use terms not in the vocabulary bridge, that's a gap in the system's coverage, not just the evidence. Surface these to administrators.

**Priority**: Medium

### Kaplan:
**Assessment**: Modify

Add: **Methodological diversity gap**. In our field, we value triangulation—lab studies, field studies, surveys, physiological measures. If all evidence comes from one method, that's a gap even if saturation is reached within that method.

**Priority**: Medium

### Consensus:
**Assessment**: MODIFY
**Priority**: Medium

**Required Changes**:
1. Add confounder coverage gap for causal claims (Pearl) — HIGH
2. Add vocabulary/system gap tracking (Bates) — MEDIUM
3. Add methodological diversity gap (Kaplan) — MEDIUM
4. Current 25% uncertainty threshold is acceptable (Cartwright) — No change

---

## Panel Response: Decision Point 10 — Ingestion Warnings

### Pearl:
**Assessment**: Approve

Warnings at ingestion are valuable. Catching problems early prevents downstream contamination of the evidence base. The three warning types are appropriate.

**Priority**: N/A

### Cartwright:
**Assessment**: Approve

This is exactly what I advocated for. Proactive warnings about abstract-only causal claims are essential. The prompt to reconsider when causal language is detected but `is_causal=False` is particularly valuable—it catches unconscious assumptions.

**Priority**: N/A

### Simon:
**Assessment**: Modify

Three warnings per ingestion risks warning fatigue. Consider:
1. Collapsing related warnings (not three separate alerts)
2. Progressive disclosure (show primary warning, details on expand)
3. "Don't show again for this session" option for experienced users

The warnings are valuable but presentation matters.

**Priority**: Medium

### Bates:
**Assessment**: Modify

I agree with Simon on presentation. Also: warnings should be **logged**, not just displayed. This creates an audit trail and allows batch review. "Show all warnings from today's ingestion session" is a useful feature.

**Priority**: Medium

### Kaplan:
**Assessment**: Approve

For researchers in our field, these warnings are educational. Many researchers don't think carefully about the abstract-vs-full-text distinction. The warnings serve a training function.

**Priority**: Low

### Consensus:
**Assessment**: APPROVE with presentation modifications
**Priority**: Medium

**Required Changes**:
1. Implement warning consolidation and progressive disclosure (Simon) — MEDIUM
2. Add warning logging for audit/batch review (Bates) — MEDIUM
3. Keep all three warning types (Cartwright) — No change

---

## Panel Response: Decision Point 11 — Follow-up Question Generation

### Pearl:
**Assessment**: Modify

The "Deeper" follow-up ("What are the mechanisms...") is excellent—it pushes toward causal understanding. However, the templates are too generic. Follow-ups should be generated from **actual gaps in the evidence**:
- If no mechanism evidence exists: "What mechanisms might explain this effect?"
- If mechanism evidence exists: "Does [specific mechanism] fully account for the effect?"

**Priority**: Medium

### Cartwright:
**Assessment**: Modify

Add a fourth follow-up type: **Scope**. "Under what conditions does this hold?" is distinct from uncertainty and crucial for evidence-based practice. The current "uncertainty" follow-up is too broad—it conflates "what don't we know" with "when does this apply."

**Priority**: High (scope is critical)

### Simon:
**Assessment**: Approve

Exactly 3 follow-ups is correct. It provides structure without overwhelming. I specifically recommended this number. Adding a fourth (Cartwright's scope) would require removing one of the existing three. If scope is critical, replace "broader" with "scope"—they overlap conceptually.

**Priority**: Low (resist adding fourth)

### Bates:
**Assessment**: Modify

Follow-ups should be **clickable queries**, not just displayed text. Users should be able to click a follow-up and immediately run that search. This supports berrypicking behavior—following trails through the information space.

**Priority**: High (interaction design)

### Kaplan:
**Assessment**: Approve

The three directions (deeper, broader, uncertainty) cover the main ways researchers explore topics. For our field, "broader" is particularly valuable—environmental effects rarely occur in isolation.

**Priority**: Low

### Consensus:
**Assessment**: MODIFY
**Priority**: Medium

**Required Changes**:
1. Generate follow-ups from actual evidence gaps, not just templates (Pearl) — MEDIUM
2. Replace "broader" with "scope" to address Cartwright's concern while keeping N=3 (Simon compromise) — MEDIUM
3. Make follow-ups clickable/executable queries (Bates) — HIGH
4. Keep exactly 3 follow-ups (Simon) — No change

---

## Panel Response: Decision Point 12 — Evidence Limit Defaults

### Pearl:
**Assessment**: Approve

Ten items is reasonable. Users can request more if needed. The sort order (relevance then credence) is appropriate—relevance first ensures topical fit; credence second ensures quality within relevant results.

**Priority**: N/A

### Cartwright:
**Assessment**: Modify

Should contested beliefs be surfaced even if lower relevance? Yes—but with a separate presentation. Show "Top 10 Evidence" followed by "Contested/Disputed (N items)" as a separate section. Don't hide disagreement by relevance filtering.

**Priority**: High

### Simon:
**Assessment**: Approve

Ten is a good satisficing number. It's enough to assess the evidence landscape without overwhelming. Miller's 7±2 suggests humans handle ~10 items well. The "and N more..." indicator is a good suggestion for transparency.

**Priority**: Low

### Bates:
**Assessment**: Modify

The limit should vary by **response type**:
- Direct answer: 5 items (focused)
- Summary: 10 items (balanced)
- Evidence list: 20 items (comprehensive)

One-size-fits-all limits don't match different information needs.

**Priority**: Medium

### Kaplan:
**Assessment**: Approve

Ten is appropriate for our field. Researchers often start with a quick scan before deep-diving. Ten items allows scanning while the "show more" option supports deeper exploration.

**Priority**: Low

### Consensus:
**Assessment**: MODIFY
**Priority**: Medium

**Required Changes**:
1. Add separate "Contested Evidence" section regardless of relevance (Cartwright) — HIGH
2. Vary limits by response type: 5/10/20 (Bates) — MEDIUM
3. Add "and N more..." indicator (already suggested) — LOW
4. Default of 10 is acceptable (Pearl/Simon/Kaplan) — No change to default

---

## Summary: Panel Recommendations by Priority

### HIGH Priority (Implement before next release)

| Decision | Change | Owner |
|----------|--------|-------|
| D3 | Three-tier causal classification (Causal/Suggestive/Associational) | Pearl |
| D7 | Derive outcomes from taxonomy, add sleep/social/wayfinding/restoration | Bates/Kaplan |
| D9 | Add confounder coverage gap for causal claims | Pearl |
| D11 | Make follow-ups clickable/executable | Bates |
| D12 | Add separate "Contested Evidence" section | Cartwright |

### MEDIUM Priority (Address in next sprint)

| Decision | Change | Owner |
|----------|--------|-------|
| D1 | Add DOES_X_CAUSE_Y vs IS_X_ASSOCIATED distinction | Pearl |
| D1 | Add UNDER_WHAT_CONDITIONS query type | Cartwright |
| D2 | Add directionality metadata to synonyms | Cartwright |
| D2 | Implement unmatched term logging | Bates |
| D4 | Add conflict/dispersion indicator | Pearl |
| D5 | Add scope coverage criterion | Cartwright |
| D5 | Improve saturation algorithm | Bates |
| D6 | Query-type-specific stopping logic for causal queries | Pearl |
| D8 | Add study design quality factor | Pearl |
| D10 | Warning consolidation and logging | Simon/Bates |
| D11 | Replace "broader" with "scope" follow-up | Cartwright/Simon |
| D12 | Vary limits by response type | Bates |

### LOW Priority (Consider for future)

| Decision | Change | Owner |
|----------|--------|-------|
| D1 | Add BROWSE_TOPIC exploration mode | Bates |
| D2 | Document term evolution history | Kaplan |
| D4 | Source-depth-adjusted thresholds | Cartwright |
| D5 | Raise min_beliefs default to 8 | Kaplan |
| D8 | Display quality component scores | Bates |
| D8 | Add recency adjustment | Kaplan |

---

## Panel Closing Statement

**Pearl**: The system shows promise but conflates association with causation. The three-tier classification is essential before this can be used for policy-relevant research.

**Cartwright**: I'm pleased to see source depth and abstract-only warnings implemented. The scope coverage additions will significantly improve evidence transferability assessment.

**Simon**: The system demonstrates good satisficing principles. Resist the temptation to add complexity for every edge case. The 181 passing tests suggest solid engineering.

**Bates**: The vocabulary transparency and follow-up structure are well-designed. Making follow-ups clickable will significantly improve the search experience.

**Kaplan**: The system serves our field's needs. The outcome category expansion will make gap analysis more relevant to environmental psychology research.

---

*Panel review completed January 21, 2026*
