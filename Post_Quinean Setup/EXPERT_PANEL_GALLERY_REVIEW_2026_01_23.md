# Expert Panel Review: ClaimGallery Visual Evidence Layer

**Date**: January 23, 2026
**Sprint**: G1 (Gallery Foundation)
**Version**: V22.0.0 (Post-Quinean)
**Review Type**: Implementation Critique & Key Decision Validation

---

## Executive Summary

We have implemented Phase 1 of the ClaimGallery visual evidence layer, which provides visual exemplars for claims. This review requests expert panel critique of key design decisions before proceeding to Phase 2.

---

## Implementation Overview

### What Was Built

1. **4 JSON Schemas** defining data contracts
2. **ClaimGalleryBuilder service** (750+ lines) for deterministic gallery construction
3. **Streamlit-style CSS theme** (700+ lines) for visual presentation
4. **Interactive HTML viewer** with drawer-based detail view
5. **RESTful API** with 5 endpoints

### Core Architecture

```
ClaimGallery
├── claim (statement, feature, outcome, moderators)
├── evidence_quality (design_strength, consistency, portability)
├── scope (population, setting, task_context)
├── slots
│   ├── central_positive[]   # Feature clearly present
│   ├── central_negative[]   # Feature clearly absent
│   ├── near_miss[]          # Borderline cases
│   ├── likely_failure[]     # Feature present, outcome may not follow
│   └── context_shift[]      # Different building types
└── provenance_summary (sources, licenses, config_id, snapshot_hash)
```

---

## Key Decisions Requiring Panel Critique

### Decision G1.1: Five-Slot Taxonomy

**What**: We implemented 5 slot types for organizing visual evidence.

| Slot | Purpose | Selection Criterion |
|------|---------|---------------------|
| central_positive | Clear positive examples | feature_score >= tau |
| central_negative | Clear negative examples | feature_score <= tau - band |
| near_miss | Decision boundary cases | abs(feature_score - tau) <= band |
| likely_failure | Moderator-affected cases | feature_score >= tau AND moderator_flags present |
| context_shift | Portability test | feature_score >= tau, diverse building_types |

**Rationale**: This taxonomy emerged from the need to show not just what a claim means, but where it breaks and how portable it is.

**Questions for Panel**:
1. Is five slots the right granularity? Too many? Too few?
2. Should "near_miss" be further subdivided (e.g., "barely positive" vs "barely negative")?
3. Is the likely_failure concept sound, or does it conflate distinct failure modes?

---

### Decision G1.2: Single Threshold (tau) with Band

**What**: We use a single threshold tau (default 0.65) with a near-miss band (default 0.15) for classification.

```python
central_positive: feature_score >= 0.65
central_negative: feature_score <= 0.50  (tau - band)
near_miss: 0.50 < feature_score < 0.80   (within band of tau)
```

**Rationale**: Simple, interpretable, auditable. The band creates explicit uncertainty zones.

**Questions for Panel**:
1. Should tau be claim-specific or global?
2. Is a symmetric band appropriate, or should positive/negative boundaries differ?
3. How should tau be calibrated? By domain experts? By model confidence?

---

### Decision G1.3: Construct Confidence vs Outcome Evidence (Two Axes)

**What**: Every image carries two independent measures:

1. **construct_confidence**: How certain are we the feature is present? (0-1 score + basis)
2. **outcome_evidence.status**: How was the outcome linked?
   - `measured_on_this_image`: Direct measurement
   - `measured_on_similar_context`: Transfer from similar settings
   - `literature_link_only`: Theoretical link only
   - `unknown`: No outcome evidence

**Rationale**: Following Pearl's advice to separate causal tier from credence. A high construct_confidence doesn't mean we have outcome evidence.

**Questions for Panel**:
1. Is this separation clear enough for users?
2. Should we add a third axis for "mechanism plausibility"?
3. How do we prevent users from conflating these?

---

### Decision G1.4: Persona-Based Slot Targets

**What**: Different user personas get different gallery sizes:

| Persona | Positive Target | Negative Target | Near-Miss Target | Failure Target |
|---------|----------------|-----------------|------------------|----------------|
| architect | 6 | 4 | 4 | 2 |
| student | 8 | 6 | 8 | 4 |
| researcher | 12 | 10 | 12 | 10 |
| default | 8 | 8 | 8 | 4 |

**Rationale**: Following Simon's cognitive load principles. Architects need quick answers; researchers need discrimination.

**Questions for Panel**:
1. Are these target numbers well-calibrated?
2. Should personas affect tau/band, not just counts?
3. What happens when pool is too small to meet targets?

---

### Decision G1.5: Diversity Constraint (Max 2 per Project)

**What**: No more than 2 images from the same project_id can appear in a single slot.

**Rationale**: Prevents one study from dominating a slot. Forces representation across sources.

**Questions for Panel**:
1. Is 2 the right limit? Should it be configurable?
2. Should diversity also consider building_type, culture_region?
3. What if violating diversity is necessary to meet minimum coverage?

---

### Decision G1.6: Deterministic Selection (hash-based caching)

**What**: Same (claim_id, snapshot_id, config_id, random_seed) → identical gallery.

```python
gallery_id = hash(claim_id + config_id + snapshot_id + seed)
```

**Rationale**: Reproducibility for governance. Any gallery can be exactly recreated.

**Questions for Panel**:
1. Is determinism worth the complexity?
2. Should we allow "refresh" that generates a new seed?
3. How do we handle image pool updates?

---

### Decision G1.7: Append-Only Feedback (JSONL)

**What**: User feedback is written to `image_feedback.jsonl` in append-only mode.

**Rationale**: Following Ng's active learning advice + governance requirements (no deletion).

**Questions for Panel**:
1. How should feedback affect future galleries? Immediately or batched?
2. Should feedback require minimum confidence threshold?
3. How do we handle conflicting feedback from different users?

---

### Decision G1.8: Selection Log with Exclusion Reasons

**What**: Every gallery build produces a SelectionLog explaining:
- Why each image was selected (reason_codes, reason_text)
- Why top candidates were excluded (excluded_because)

**Rationale**: Following Norvig's ranking explanation principle. Users should understand selection.

**Questions for Panel**:
1. Is this level of explanation sufficient?
2. Should exclusion reasons be shown in the UI?
3. How verbose should reason_text be?

---

## Code Samples for Review

### Gallery Builder Core Logic

```python
def _select_for_slot(self, slot_role, image_pool, filter_fn, sort_key, reason_prefix):
    """Select images for a slot with logging."""
    candidates = [img for img in image_pool if filter_fn(img)]
    candidates.sort(key=sort_key)

    selected_by_project = {}
    selected_images = []
    excluded = []

    for img in candidates:
        project_id = img.get("project_id", "unknown")

        # Diversity constraint
        if selected_by_project.get(project_id, 0) >= 2:
            excluded.append(ExclusionEntry(
                image_id=img["image_id"],
                excluded_because=["diversity_limit:max_per_project"]
            ))
            continue

        # Slot capacity
        if len(selected_images) >= max_count:
            excluded.append(ExclusionEntry(
                image_id=img["image_id"],
                excluded_because=["slot_full"]
            ))
            continue

        selected_images.append(self._pool_image_to_entry(img, reason_prefix))
        selected_by_project[project_id] = selected_by_project.get(project_id, 0) + 1

    return selected_images, SlotLog(...)
```

### API Endpoint Structure

```python
@router.post("/build", response_model=GalleryResponse)
async def build_gallery(request: BuildGalleryRequest):
    """Build a visual evidence gallery for a claim."""
    builder = ClaimGalleryBuilder(
        persona=PersonaProfile(request.persona),
        feature_threshold_tau=request.feature_threshold_tau,
        near_miss_band=request.near_miss_band,
        random_seed=request.random_seed
    )
    gallery = builder.build_gallery(claim, image_pool, evidence_quality, scope)
    save_gallery(gallery, DATA_DIR)
    return GalleryResponse(...)
```

---

## Test Coverage

18 tests covering:
- AT1: Every claim has positive/negative/near-miss
- AT2: Gallery shows both sides (not just confirmatory)
- AT3: Every image displays outcome_evidence.status
- AT4: Deterministic (same inputs → identical gallery)
- AT5: Every image has provenance
- AT6: Max 2 images per project per slot
- UX2: Persona-based presets work

---

## Request to Panel

Please review the 8 key decisions above and provide:

1. **Critiques**: What's wrong or risky?
2. **Alternatives**: What would you do differently?
3. **Priorities**: Which issues are blocking vs nice-to-have?
4. **Missing concerns**: What haven't we considered?

Focus especially on:
- Epistemological soundness (Pearl, Cartwright)
- Usability (Simon, Bates, Kaplan)
- ML/feedback loop design (Ng)
- System robustness (Dean, Lamport)

---

## Panel Composition

| Expert | Domain | Primary Concerns |
|--------|--------|------------------|
| Dr. Judea Pearl | Causal inference, BN | Causal vs correlational distinction |
| Dr. Nancy Cartwright | Philosophy of science | Bridge warrants, external validity |
| Dr. Herbert Simon | Bounded rationality | Cognitive load, satisficing |
| Dr. Marcia Bates | Information science | Search behavior, berrypicking |
| Dr. Rachel Kaplan | Environmental psychology | Domain validity, practitioner needs |
| Dr. Andrew Ng | Machine learning | Active learning, feedback loops |
| Dr. Andrej Karpathy | Deep learning, vision | Visual model calibration |
| Dr. Ilya Sutskever | AI systems | Uncertainty, overconfidence |
| Dr. Peter Norvig | AI, search | Ranking, explanation |
| Dr. Jeff Dean | Systems engineering | Scalability, caching |
| Dr. Leslie Lamport | Distributed systems | Determinism, reproducibility |
| Dr. Martin Fowler | Software design | API design, maintainability |
| ChatGPT-4 | Adversarial review | Edge cases, failure modes |
| Claude-3 Opus | Coherence review | Consistency, completeness |
| Gemini Pro | Integration review | Interoperability |
| Local Llama | Resource constraints | Efficiency, local deployment |

---

*Document prepared for expert panel review, January 23, 2026*
