# Expert Panel Review: Implementation Decisions Made Without Prior Consultation

**Date**: January 23, 2026
**Sprint**: G1 (Gallery Foundation)
**Purpose**: Retrospective review of decisions made during implementation

---

## Context

During implementation of the ClaimGallery visual evidence layer, I made several decisions autonomously that would have benefited from panel input beforehand. This document identifies those decisions for retrospective critique and potential revision.

---

## Implementation Decisions Requiring Validation

### ID-1: Diversity Key Hardcoded to `project_id`

**What I Did**: Hardcoded the diversity constraint to use `project_id` as the deduplication key.

```python
def _select_for_slot(self, ...):
    selected_by_project = {}
    for img in candidates:
        project_id = img.get("project_id", "unknown")
        if selected_by_project.get(project_id, 0) >= 2:
            excluded.append(...)
```

**Why I Did It**: Seemed like the most natural grouping unit.

**What I Should Have Asked**:
- Should users be able to configure the diversity key (project_id, source_id, study_id)?
- Should multiple diversity constraints apply simultaneously?
- Is project_id even the right level? Maybe `study_id` or `paper_doi` is more meaningful epistemologically?

**Risk**: If project_id isn't populated, everything falls back to "unknown" and diversity fails silently.

---

### ID-2: Fallback to `source` When Checking Diversity in Tests

**What I Did**: In the test, I used `provenance.source` as a proxy for project:

```python
# In test (wrong approach)
for img in gallery.slots.central_positive:
    proj = img.provenance.source  # Using source as proxy
```

**Problem**: This doesn't match the builder's actual behavior which uses `project_id`. The test was checking the wrong field.

**What I Fixed**: Changed test to use a controlled pool where all images have the same `project_id`.

**What I Should Have Asked**: What's the canonical identity for an image's "source grouping"? This should be specified in the schema, not left ambiguous.

---

### ID-3: Persona Slot Target Numbers (Arbitrary)

**What I Did**: Chose specific target numbers without empirical basis:

```python
PERSONA_SLOT_TARGETS = {
    PersonaProfile.ARCHITECT: {
        SlotRole.CENTRAL_POSITIVE: {"min": 4, "target": 6, "max": 8},
        ...
    },
    PersonaProfile.STUDENT: {
        SlotRole.CENTRAL_POSITIVE: {"min": 6, "target": 8, "max": 10},
        ...
    },
    ...
}
```

**Why I Did It**: Seemed reasonable. Architects want fewer, researchers want more.

**What I Should Have Asked**:
- What does cognitive load research say about optimal gallery sizes?
- Should these be configurable per-claim based on evidence density?
- How do these interact with screen real estate / viewport considerations?

**Risk**: Numbers may be wrong for actual user tasks. No empirical validation.

---

### ID-4: Context Shift Selection Strategy

**What I Did**: For `context_shift` slot, I pick one image per building_type:

```python
def _select_context_shift(self, image_pool, feature_id):
    by_building_type = {}
    for img in image_pool:
        if img.get("feature_score", 0) >= self.feature_threshold_tau:
            bt = img.get("building_type", "unknown")
            by_building_type.setdefault(bt, []).append(img)

    selected = []
    for bt in shuffled_building_types[:target_count]:
        best = max(by_building_type[bt], key=lambda x: x.get("feature_score", 0))
        selected.append(best)
    return selected
```

**Why I Did It**: Ensures visual diversity across building types.

**What I Should Have Asked**:
- Is building_type the right facet for portability testing?
- Should we also vary by culture_region, indoor_outdoor, etc.?
- Should context_shift show the SAME feature_score range, or deliberately show variance?

**Risk**: May not actually test portability if building_type isn't the key moderator.

---

### ID-5: Confidence Bar Color Thresholds

**What I Did**: Set fixed thresholds for confidence bar coloring:

```python
conf_class = 'high' if confidence >= 0.7 else 'medium' if confidence >= 0.5 else 'low'
```

And in CSS:
```css
.confidence-bar--high .confidence-bar__fill { background: var(--gallery-conf-high); }  /* green */
.confidence-bar--medium .confidence-bar__fill { background: var(--gallery-conf-medium); }  /* amber */
.confidence-bar--low .confidence-bar__fill { background: var(--gallery-conf-low); }  /* red */
```

**Why I Did It**: Standard traffic-light convention.

**What I Should Have Asked**:
- Should thresholds be relative to tau, not absolute?
- Does traffic-light coloring create false confidence in the model?
- Should color be based on confidence basis (human vs model) not just score?

**Risk**: Users may over-trust model predictions because they look "green."

---

### ID-6: Empty Slot Handling

**What I Did**: When a slot has no matching images, I show an empty state:

```javascript
if (images.length === 0) {
    grid.innerHTML = `<div class="gallery-empty">
        <div class="gallery-empty__title">No images</div>
        <div class="gallery-empty__text">No images match this slot's criteria</div>
    </div>`;
}
```

**Why I Did It**: Better than nothing. Shows the slot exists but is empty.

**What I Should Have Asked**:
- Should empty slots be hidden entirely to reduce confusion?
- Should empty slots trigger a warning in the UI?
- Is an empty slot a sign the tau/band parameters are miscalibrated?

**Risk**: Users may not understand why a slot is empty.

---

### ID-7: Feedback Schema Ties to gallery_id Only

**What I Did**: Feedback references `gallery_id` and `claim_id` but not `web_snapshot_id`:

```python
class ImageFeedbackRequest(BaseModel):
    gallery_id: str
    claim_id: str
    image_id: str
    slot_role: str
    ...
```

**What the Schema Allows**: The JSON schema includes `web_snapshot_id` in target:

```json
"target": {
    "gallery_id": { "type": "string" },
    "claim_id": { "type": "string" },
    "image_id": { "type": "string" },
    "slot_role": { "type": "string" },
    "web_snapshot_id": { "type": "string" }  // I didn't expose this in API
}
```

**What I Should Have Asked**:
- Should feedback be tied to web_snapshot_id for traceability to the belief system state?
- How do we ensure feedback is attributable to the correct version of the epistemic context?

**Risk**: Feedback may be orphaned from the web of belief state that generated the gallery.

---

### ID-8: SelectionLog Stores Only Top 10 Excluded

**What I Did**: Limited exclusion log to top 10 candidates:

```python
slot_log = SlotLog(
    ...
    excluded_top=excluded[:10]  # Only top 10
)
```

**Why I Did It**: Avoid log bloat. Most users only care about near-misses.

**What I Should Have Asked**:
- Is 10 the right number? Should it be configurable?
- Should we log ALL exclusions for full audit trail?
- Should exclusion logging be optional (governance vs performance trade-off)?

**Risk**: May lose important audit information for governance.

---

### ID-9: No Validation of outcome_evidence Against Actual Measurements

**What I Did**: The `outcome_evidence.status` is taken directly from the image pool without validation:

```python
outcome_evidence=OutcomeEvidence(
    status=OutcomeStatus(pool_img.get("outcome_status", "unknown")),
    measured_outcomes=[],  # Always empty!
    citations=pool_img.get("citations", [])
)
```

**Problem**: `measured_outcomes` is always empty because I don't process it from the pool.

**What I Should Have Asked**:
- Where do measured_outcomes come from?
- Should the builder validate that measured_on_this_image status has actual outcomes?
- Is it dishonest to claim "measured_on_this_image" without the measurements?

**Risk**: Misleading users about evidence quality.

---

### ID-10: Demo Data Uses Random Images from Picsum

**What I Did**: The HTML viewer demo uses placeholder images:

```javascript
uri_or_path: `https://picsum.photos/400/300?random=${type}${i}`
```

**Why I Did It**: Needed something visual for demo.

**What I Should Have Asked**:
- Should demo data use architectural images to be domain-relevant?
- Does random imagery undermine user trust in the system?
- Should we bundle sample images in the repo?

**Risk**: Demo looks unprofessional; doesn't show real use case.

---

## Priority Assessment (My View)

| Decision | Severity | Effort to Fix | Recommendation |
|----------|----------|---------------|----------------|
| ID-1 (diversity key) | Medium | Medium | Make configurable |
| ID-2 (test fix) | Low | Done | Already fixed |
| ID-3 (persona numbers) | Medium | Low | Make configurable, document defaults |
| ID-4 (context shift) | Medium | Medium | Add configurable facets |
| ID-5 (color thresholds) | High | Low | Tie to tau, add basis indicator |
| ID-6 (empty slots) | Low | Low | Add warning icon |
| ID-7 (snapshot link) | High | Low | Add to API |
| ID-8 (exclusion limit) | Medium | Low | Make configurable |
| ID-9 (measured_outcomes) | High | Medium | Implement properly |
| ID-10 (demo images) | Low | Medium | Defer to Phase 2 |

---

## Questions for Panel

1. **Which of these decisions are actually wrong** vs just suboptimal?
2. **Which should block Phase 2** vs can be fixed later?
3. **What decisions did I make that I didn't even realize** were decisions?
4. **Are there integration points** with other system components I missed?

---

*Prepared for retrospective expert panel review, January 23, 2026*
