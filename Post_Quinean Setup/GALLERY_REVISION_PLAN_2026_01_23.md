# Gallery Revision Plan Based on Panel Feedback

**Date**: January 23, 2026
**Sprint**: G1 Revisions

---

## Blocking Issues to Fix Now

### B1: Validate outcome_status Against measured_outcomes (Pearl, Ng)

**Problem**: `measured_outcomes` is always empty, making `status: measured_on_this_image` dishonest.

**Fix**:
1. If pool provides measured_outcomes, populate them
2. If status is "measured_on_this_image" but no outcomes provided, downgrade to "literature_link_only"
3. Add warning to selection log when downgrade occurs

**Files**: `src/services/claim_gallery_builder.py`

---

### B2: Add web_snapshot_id to Feedback API (Ng)

**Problem**: Feedback can't be traced to epistemic state that generated the gallery.

**Fix**:
1. Add `web_snapshot_id` to `ImageFeedbackRequest`
2. Include in feedback record
3. Make it optional (for backwards compatibility) but log warning if missing

**Files**: `app/routes/galleries.py`

---

### B3: Input Validation (ChatGPT-4)

**Problem**: No validation for degenerate inputs.

**Fix**:
1. Validate pool is not empty
2. Validate tau is in (0, 1) exclusive
3. Validate band is reasonable (< tau)
4. Add max pool size limit (configurable, default 10000)
5. Sanitize string inputs (image_id, reason_text)

**Files**: `src/services/claim_gallery_builder.py`, `app/routes/galleries.py`

---

### B4: Outcome Evidence Visual Separation (Pearl)

**Problem**: Color thresholds conflate construct confidence with outcome reliability.

**Fix**:
1. Add separate outcome evidence badge in image cards
2. Show both construct confidence bar AND outcome badge
3. Add tooltip explaining the difference

**Files**: `frontend/claim-gallery.html`, `frontend/css/gallery-streamlit.css`

---

## Implementation Order

1. B1 (outcome validation) - core logic fix
2. B3 (input validation) - safety
3. B2 (snapshot_id) - API addition
4. B4 (visual separation) - UI enhancement

---

## Deferred to Phase 2

- Multi-facet diversity (Bates) - needs config schema update
- likely_failure split (Cartwright) - needs new slot types
- Feature attribution in logs (Norvig) - logging enhancement
- Demo images (Kaplan) - content creation

---
