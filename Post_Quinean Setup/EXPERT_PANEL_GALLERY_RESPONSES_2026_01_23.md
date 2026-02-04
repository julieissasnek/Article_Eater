# Expert Panel Responses: ClaimGallery Visual Evidence Layer

**Date**: January 23, 2026
**Sprint**: G1 Review
**Documents Reviewed**:
- `EXPERT_PANEL_GALLERY_REVIEW_2026_01_23.md` (Architecture)
- `EXPERT_PANEL_IMPLEMENTATION_DECISIONS_2026_01_23.md` (Implementation)

---

## Panel Responses

### Dr. Judea Pearl (Causal Inference)

**On G1.3 (Construct Confidence vs Outcome Evidence)**:

This is the RIGHT separation. You correctly distinguished between:
- P(feature | image) — construct confidence
- P(outcome | feature, context) — outcome evidence

However, **ID-9 is a serious problem**. You claim `measured_on_this_image` status but provide no actual measurements. This is epistemically dishonest. If status is "measured," then `measured_outcomes` MUST be populated.

**Critique of ID-5 (Color Thresholds)**:
The traffic-light coloring conflates construct presence with outcome reliability. A green confidence bar on an image with `literature_link_only` outcome status could mislead users into thinking the OUTCOME is reliable when only FEATURE DETECTION is confident.

**Recommendation**:
1. **BLOCKING**: Fix ID-9 — either populate measured_outcomes or downgrade status
2. Add a SEPARATE visual indicator for outcome evidence strength
3. Consider a 2x2 matrix visual: {high/low construct} × {measured/linked outcome}

**Priority**: HIGH — this is an epistemological integrity issue.

---

### Dr. Nancy Cartwright (Philosophy of Science)

**On G1.1 (Five-Slot Taxonomy)**:

The slot taxonomy is reasonable but **likely_failure conflates distinct mechanisms**. A refuge space might "fail" because of:
- Crowding (capacity moderator)
- Noise (acoustic moderator)
- Glare (visual moderator)
- Cultural mismatch (validity moderator)

These are DIFFERENT failure types requiring different responses. Lumping them into one slot loses diagnostic value.

**On ID-4 (Context Shift Strategy)**:

Building type is a **weak portability test**. What matters for external validity is whether the *mechanism* transfers, not the building label. A hospital and office might share the same mechanism (prospect-refuge), while two "offices" might differ completely (open-plan vs private).

**Recommendation**:
1. Consider splitting likely_failure by moderator TYPE, not just flagging presence
2. For context_shift, vary the MECHANISM-RELEVANT dimensions, not just building labels
3. Add explicit bridge warrant references to context_shift images

**Priority**: MEDIUM — improves diagnostic value but doesn't block core functionality.

---

### Dr. Herbert Simon (Bounded Rationality)

**On ID-3 (Persona Slot Targets)**:

Your numbers seem pulled from thin air. The cognitive psychology literature suggests:
- **Miller's Law**: 7±2 items in working memory
- **Satisficing**: Users stop searching when "good enough" is found
- **Visual search**: Performance degrades beyond ~12-15 items per view

For architects making quick decisions, 4-6 examples is appropriate. For researchers doing systematic review, 12+ is appropriate. Your numbers are in the right ballpark but should be JUSTIFIED, not arbitrary.

**On ID-6 (Empty Slots)**:

Never hide empty slots — that's deceptive. But your current message is too passive. Change from:

> "No images match this slot's criteria"

To:

> "No near-miss examples found. This may indicate: (a) tau is set too strictly, (b) the pool lacks borderline cases, or (c) the claim boundary is unusually sharp. [Adjust tau] [Expand pool]"

Give users ACTIONABLE guidance.

**Recommendation**:
1. Document cognitive justification for target numbers
2. Make empty slots diagnostic, not just informative
3. Add "why empty" heuristics to selection log

**Priority**: MEDIUM — affects usability but not correctness.

---

### Dr. Marcia Bates (Information Science)

**On the Overall Design**:

This is a **berrypicking** interface, which is good. Users don't search linearly; they browse, sample, and adjust. The drawer-based detail view supports this.

**Concern about ID-1 (Diversity Key)**:

Using only `project_id` for diversity is too narrow. Users engaging in berrypicking need diversity across MULTIPLE facets:
- Source diversity (don't let one lab dominate)
- Building type diversity (portability)
- Methodology diversity (not all self-report, not all behavioral)
- Time diversity (not all from 2019)

**On G1.4 (Persona-Based Targets)**:

The persona model is too coarse. Consider Bates' "facets of searchers":
- Novice vs Expert
- Directed vs Undirected
- Known-item vs Exploratory
- Time-pressed vs Thorough

"Architect" conflates several of these. An architect doing a quick check differs from one doing design development.

**Recommendation**:
1. Implement multi-facet diversity (configurable)
2. Consider task-based personas, not role-based
3. Add "explore more like this" that preserves user's berry path

**Priority**: MEDIUM — improves search effectiveness.

---

### Dr. Rachel Kaplan (Environmental Psychology)

**Domain Validation**:

As the domain expert, I'm concerned about **ecological validity**. The system assumes we can judge "refuge edges" from static images, but refuge is experiential. Key issues:

1. **Temporal dimension missing**: Refuge depends on who else is present, time of day, ambient noise — none of which static images capture
2. **Scale ambiguity**: Photos don't convey actual dimensions; a "cozy alcove" at 2m² differs from one at 20m²
3. **Cultural variation**: My work is primarily North American/European; Asian concepts of refuge differ

**On ID-10 (Demo Images)**:

Random images are worse than no images. They undermine credibility. For domain demonstrations, you MUST use actual architectural images, even if just 10-20 curated examples.

**Recommendation**:
1. Add metadata for scale (estimated area, ceiling height)
2. Add cultural context flags with honest uncertainty
3. BLOCKING: Replace demo with real architectural images before any user testing
4. Consider adding "confidence in static image judgment" as a construct

**Priority**: HIGH for demo images (credibility); MEDIUM for metadata enrichment.

---

### Dr. Andrew Ng (Machine Learning)

**On G1.7 (Append-Only Feedback)**:

Good decision. Append-only is correct for active learning. However, your feedback loop is incomplete:

1. **No feedback → model update path**: Feedback goes to JSONL but nothing reads it
2. **No confidence calibration**: User corrections should update tau, not just image labels
3. **No inter-rater tracking**: If two users disagree, who's right?

**On ID-7 (Snapshot Link)**:

**CRITICAL**: Feedback MUST link to `web_snapshot_id`. Without it, you can't:
- Trace feedback to model version that produced the gallery
- Do proper A/B testing of model improvements
- Understand if feedback reflects model error vs belief evolution

**On ID-9 (measured_outcomes Empty)**:

This breaks the active learning contract. If users give feedback on images without outcome data, you can't improve outcome prediction — only construct detection.

**Recommendation**:
1. **BLOCKING**: Add web_snapshot_id to feedback API
2. Design feedback → retrain pipeline (even if not implemented yet)
3. Track feedback source quality (expert vs novice)
4. Implement inter-rater reliability checks

**Priority**: HIGH — affects learning loop integrity.

---

### Dr. Andrej Karpathy (Deep Learning, Vision)

**On ID-5 (Color Thresholds)**:

Your thresholds are arbitrary. In production vision systems, we use **calibrated confidence** based on held-out validation. Your 0.7/0.5 thresholds may not match actual model reliability.

**Recommendation**:
1. Calibrate thresholds to actual precision/recall on validation set
2. Show uncertainty (confidence interval), not point estimate
3. Display "model says 0.72 ± 0.15" not just "72%"

**On Visual Representation**:

The image cards are too small for architectural detail. Refuge edges require seeing CONTEXT — ceiling relationships, sightlines, adjacencies. 180px thumbnails may not convey this.

**Recommendation**:
1. Larger default thumbnails (250-300px)
2. Quick-zoom on hover (not just click-to-drawer)
3. Consider side-by-side comparison mode as first-class feature

**Priority**: MEDIUM — affects judgment quality.

---

### Dr. Ilya Sutskever (AI Systems)

**On Overconfidence**:

The system lacks appropriate humility. Every gallery should display:

1. **Model uncertainty**: Not just confidence in feature, but uncertainty ABOUT the confidence
2. **Coverage warnings**: "This gallery draws from N images; claim is based on M studies; generalization uncertain"
3. **Disagreement signals**: If construct_confidence varies widely across selected images, that's signal

**On the likely_failure Slot**:

This is the most important slot, yet it has the LOWEST targets in architect persona. Failure modes are precisely what practitioners need to know. Consider:
- Making likely_failure targets higher for architects (they need to know risks)
- Adding "likelihood of failure" metric per image, not just presence of flags

**Recommendation**:
1. Add uncertainty quantification throughout
2. Increase likely_failure emphasis for practitioners
3. Add "disagreement flag" when images in same slot have high variance

**Priority**: HIGH — affects decision quality under uncertainty.

---

### Dr. Peter Norvig (AI, Search)

**On G1.8 (Selection Log)**:

Good instinct, but insufficient. Modern explainability requires:
1. **Counterfactual explanations**: "This image was excluded because of X; if X were different, it would be ranked #3"
2. **Feature attribution**: "Selection was driven 60% by feature_score, 25% by diversity, 15% by moderator absence"
3. **Comparative ranking**: "Image A ranked above B because..."

**On ID-8 (Top 10 Exclusions)**:

10 is too few for audit. Store ALL exclusions, but DISPLAY top 10. Storage is cheap; comprehensiveness matters for governance.

**Recommendation**:
1. Store complete exclusion log
2. Add feature attribution to selection reasons
3. Support "why not this image?" queries

**Priority**: MEDIUM — improves explainability.

---

### Dr. Jeff Dean (Systems Engineering)

**On G1.6 (Deterministic Selection)**:

Determinism is correct, but your caching strategy is incomplete:

```python
gallery_id = hash(claim_id + config_id + snapshot_id + seed)
```

You hash the IDS but not the actual CONTENT. If the image pool changes but snapshot_id stays the same, you'll return stale results.

**Recommendation**:
1. Include `snapshot_hash` (content hash) in cache key, not just `snapshot_id`
2. Add cache invalidation when pool changes
3. Consider gallery TTL for pools that update frequently

**On Performance**:

Your `_select_for_slot` iterates the full pool 5 times (once per slot). Consider single-pass partitioning:

```python
def partition_pool(pool, tau, band):
    positive, negative, near_miss, failure = [], [], [], []
    for img in pool:
        score = img["feature_score"]
        flags = img.get("moderator_flags", [])
        if score >= tau:
            if flags:
                failure.append(img)
            else:
                positive.append(img)
        elif score <= tau - band:
            negative.append(img)
        else:
            near_miss.append(img)
    return positive, negative, near_miss, failure
```

**Priority**: LOW for now (pool sizes are small), but note for scale.

---

### Dr. Leslie Lamport (Distributed Systems)

**On Determinism**:

Your determinism is fragile. You use `random.Random(seed)` but:
1. Python's random is not guaranteed stable across versions
2. The shuffle order depends on list iteration order, which depends on dict ordering

For true reproducibility, you need:
1. Explicit sort before any shuffle
2. Documented Python version requirement
3. Consider using a hash-based deterministic shuffle

**On Append-Only Feedback**:

Append-only is the right pattern, but you need:
1. Log rotation (files will grow forever)
2. Checksums for integrity verification
3. Sequence numbers for ordering

**Recommendation**:
1. Use explicit stable sort keys before randomization
2. Add sequence numbers to feedback records
3. Document exact reproducibility requirements

**Priority**: MEDIUM — affects long-term reproducibility.

---

### Dr. Martin Fowler (Software Design)

**On API Design**:

Your `BuildGalleryRequest` is too flat. Consider:

```python
# Current (flat)
class BuildGalleryRequest:
    claim: ClaimRequest
    image_pool: List[ImagePoolItem]
    evidence_quality: EvidenceQualityRequest
    scope: ScopeRequest
    persona: str
    feature_threshold_tau: float
    near_miss_band: float
    random_seed: int
    config_id: Optional[str]
    snapshot_id: Optional[str]

# Better (separated concerns)
class GalleryConfig:
    persona: str
    tau: float
    band: float
    seed: int
    config_id: str

class BuildGalleryRequest:
    claim: ClaimRequest
    pool_reference: PoolReference  # ID, not full data
    evidence_quality: EvidenceQualityRequest
    scope: ScopeRequest
    config: GalleryConfig
```

Don't pass the entire image pool in the request body. Pass a reference and let the server load it.

**On Service Layer**:

`ClaimGalleryBuilder` does too much. Consider separating:
- `ImagePoolManager` — pool loading, caching, hashing
- `SlotClassifier` — tau/band logic
- `DiversityEnforcer` — deduplication logic
- `GalleryAssembler` — final assembly

**Recommendation**:
1. Separate config object
2. Use pool references, not inline data
3. Split builder responsibilities

**Priority**: LOW — refactoring, not functional change.

---

### ChatGPT-4 (Adversarial Review)

**Edge Cases Found**:

1. **Empty pool**: What if `image_pool` is empty? Builder doesn't check.
2. **All same project**: If all images have same project_id, diversity kicks everything out
3. **Negative tau**: API allows tau=0, creating degenerate galleries
4. **Unicode in image_id**: What if image_id contains special characters?
5. **Circular reference**: What if an image appears in both positive and likely_failure?

**Attack Vectors**:

1. **Log injection**: `reason_text` in feedback could contain malicious content
2. **Path traversal**: `uri_or_path` in images could be `../../etc/passwd`
3. **Denial of service**: Huge image_pool could exhaust memory

**Recommendation**:
1. Add input validation for pool size, tau range
2. Sanitize all string inputs
3. Validate uri_or_path format
4. Add explicit handling for degenerate cases

**Priority**: HIGH for input validation; MEDIUM for edge cases.

---

### Claude-3 Opus (Coherence Review)

**Consistency Issues Found**:

1. **Schema vs Implementation mismatch**: Schema allows `confusion_set` and `controlled_comparison` pairs, but builder doesn't populate them
2. **Provenance inconsistency**: ImageEntry has `provenance.source` but builder uses `project_id` for diversity — these might differ
3. **Status enum mismatch**: Python uses `OutcomeStatus.MEASURED_ON_THIS_IMAGE` but JSON schema says `"measured_on_this_image"` — case handling?

**Missing Integration Points**:

1. No link to `web_of_belief.py` — galleries should reference belief IDs
2. No link to `bridge_warrants.py` — context_shift should show bridge warrant strength
3. No link to `outcome_taxonomy.py` — outcome_id should validate against taxonomy

**Recommendation**:
1. Add confusion_set/controlled_comparison population (Phase 2)
2. Clarify project_id vs source semantics
3. Add belief_id to gallery for web integration
4. Validate outcome_id against taxonomy

**Priority**: MEDIUM — integration completeness.

---

### Gemini Pro (Integration Review)

**Interoperability Concerns**:

1. **No OpenAPI schema generation**: Pydantic models don't auto-export JSON Schema
2. **No GraphQL support**: REST-only limits integration options
3. **No webhook support**: Can't notify external systems when galleries built

**Recommendation**:
1. Export Pydantic models as JSON Schema for client generation
2. Consider GraphQL for flexible querying
3. Add optional webhook on gallery completion

**Priority**: LOW — future integration.

---

### Local Llama (Resource Constraints)

**Efficiency Concerns**:

1. **Full pool in memory**: For large pools (10K+ images), this won't work
2. **No streaming**: Gallery must be fully built before response
3. **No incremental builds**: Can't add images to existing gallery

**Recommendation**:
1. Add pagination for pool loading
2. Consider streaming JSON response
3. Add "append to gallery" endpoint

**Priority**: LOW for research use; MEDIUM for production.

---

## Consensus Summary

### BLOCKING Issues (Must Fix Before Phase 2)

| Issue | Source | Fix |
|-------|--------|-----|
| ID-9: measured_outcomes always empty | Pearl, Ng | Populate from pool or downgrade status |
| ID-7: Missing web_snapshot_id in feedback | Ng | Add to API |
| ID-10: Random demo images | Kaplan | Replace with architectural images |
| Input validation missing | ChatGPT-4 | Add pool size, tau range, sanitization |

### HIGH Priority (Fix Soon)

| Issue | Source | Fix |
|-------|--------|-----|
| ID-5: Color thresholds conflate construct/outcome | Pearl | Separate visual indicators |
| Uncertainty quantification missing | Sutskever | Add uncertainty throughout |
| Multi-facet diversity | Bates | Make diversity configurable |

### MEDIUM Priority (Phase 2)

| Issue | Source | Fix |
|-------|--------|-----|
| likely_failure conflation | Cartwright | Split by moderator type |
| Persona numbers unjustified | Simon | Document cognitive basis |
| Context shift weak | Cartwright | Vary mechanism-relevant facets |
| Selection log incomplete | Norvig | Add feature attribution |
| Integration with web/bridges | Claude-3 | Add belief_id, bridge refs |

### LOW Priority (Defer)

| Issue | Source | Fix |
|-------|--------|-----|
| API refactoring | Fowler | Separate concerns |
| Performance optimization | Dean | Single-pass partitioning |
| GraphQL/webhooks | Gemini | Future integration |

---

## Recommended Revision Plan

### Immediate (Before User Testing)

1. Fix ID-9: Validate outcome_status against measured_outcomes presence
2. Fix ID-7: Add web_snapshot_id to feedback API
3. Fix ID-10: Create curated demo image set (10-20 images)
4. Add input validation per ChatGPT-4

### Short-Term (Phase 2)

5. Separate construct confidence and outcome evidence visuals (Pearl)
6. Add uncertainty display (Sutskever)
7. Make diversity multi-faceted and configurable (Bates)
8. Improve empty slot messaging (Simon)

### Medium-Term (Phase 3)

9. Split likely_failure by moderator type (Cartwright)
10. Add feature attribution to selection log (Norvig)
11. Integrate with web_of_belief (add belief_id)
12. Integrate with bridge_warrants (context_shift references)

---

*Panel responses compiled January 23, 2026*
