# Expert Panel Review: Image Collector & Inspector GUIs

**Date**: January 28, 2026
**Sprint**: Image Pool Management System
**Components Reviewed**: `image-collector.html`, `image-inspector.html`, `image_pool_manager.py`

---

## Panel Composition

### Workflow Experts
- **Dr. Bonnie John** (CMU) — Task analysis, GOMS modeling, workflow efficiency
- **Dr. Ben Shneiderman** (UMD) — Direct manipulation, information visualization
- **Dr. Gary Olson** (UCI) — Collaborative work, distributed cognition

### GUI/UX Designers
- **Julie Zhuo** (Former Facebook VP Design) — Consumer product design, usability
- **Luke Wroblewski** — Mobile-first design, form optimization
- **Jared Spool** — Usability testing, design research

### Domain Expert
- **Dr. Rachel Kaplan** — Environmental psychology, the actual use case

---

## Image Collector GUI Review

### Strengths Identified

**Shneiderman**: "The preset-based design follows the 'overview first, zoom and filter, then details-on-demand' mantra. Good information scent with the category icons."

**Julie Zhuo**: "Clean Streamlit-style aesthetics. The progressive disclosure of query chips when a preset is selected reduces cognitive load."

**Wroblewski**: "The sidebar stays visible during scrolling (sticky). Good for maintaining context during long download sessions."

### Critical Issues

#### C1: No Progress Feedback During Multi-Query Downloads (BLOCKING)
**Bonnie John**: "When downloading a preset with 10 queries, there's a progress bar but no indication of WHICH query is being processed. Users lose context."

**Fix**: Show current query name in progress modal:
```javascript
showProgress(i + 1, queries.length, queries[i]); // Add query name
// Progress modal: "Downloading: cozy reading nook (3/10)"
```

#### C2: No Duplicate Prevention Visible to User
**Shneiderman**: "The system silently skips duplicates but doesn't tell the user. This violates the principle of visibility of system status."

**Fix**: Show "X skipped (already in pool)" in results:
```javascript
showToast(`Downloaded ${result.downloaded} images (${result.skipped} already in pool)`, 'success');
```

#### C3: Source Selection Doesn't Remember User Preference
**Wroblewski**: "If I prefer Pexels, I have to reselect it every search. Form fields should remember state."

**Fix**: Use localStorage for source preference:
```javascript
const savedSource = localStorage.getItem('preferred_source') || 'unsplash';
document.getElementById('searchSource').value = savedSource;
```

#### C4: No Preview Before Download
**Julie Zhuo**: "Users commit to downloading without seeing what they'll get. This is a trust issue, especially for research where image quality matters."

**Fix**: Add "Preview" button that shows thumbnails from API before committing to download:
```javascript
async function previewSearch(query, source) {
    // Show modal with thumbnails, let user select which to download
}
```

#### C5: Query Chips Should Support Keyboard Navigation
**Bonnie John**: "Power users can't Tab through query chips. This slows down the workflow significantly."

**Fix**: Add `tabindex` and keyboard handlers to chips.

### Medium Priority Issues

#### M1: No Undo for Downloads
**Shneiderman**: "If I accidentally download the wrong preset, there's no bulk delete. Users fear making mistakes."

**Recommendation**: Add "Undo last download" that deletes images from most recent batch.

#### M2: Stats Bar Could Show More Context
**Gary Olson**: "Knowing there are 47 images is less useful than knowing '47 images across 6 queries, 12 tagged'."

**Recommendation**: Richer stats with sparklines or mini-charts.

#### M3: No API Key Setup Guidance
**Wroblewski**: "The system falls back to demo mode silently. Users might not know they need API keys for real images."

**Recommendation**: Show setup instructions when in demo mode:
```html
<div class="api-notice">Using demo images. <a href="/docs/api-setup">Set up API keys</a> for real images.</div>
```

---

## Image Inspector GUI Review

### Strengths Identified

**Julie Zhuo**: "The three-panel layout is familiar from email/photo apps. Users will intuit the workflow immediately."

**Shneiderman**: "Direct manipulation of tags via clicking is good. The quick-tag buttons accelerate common cases."

**Rachel Kaplan**: "The environmental psychology feature tags (refuge, prospect, etc.) are correctly named. Good domain alignment."

### Critical Issues

#### C6: Slider Values Don't Persist During Selection Change (BLOCKING)
**Bonnie John**: "If I adjust sliders for Image A, then click Image B, then back to A, my slider values are LOST because they weren't saved. This is a data loss bug."

**Fix**: Auto-save on image change OR warn user:
```javascript
function selectImage(imageId) {
    if (hasUnsavedChanges()) {
        if (!confirm('You have unsaved changes. Discard?')) return;
    }
    // ... proceed
}
```

#### C7: No Keyboard Shortcuts for Tagging
**Bonnie John**: "Tagging 100 images requires too many clicks. Expert users need shortcuts like 1=refuge, 2=prospect, etc."

**Fix**: Add keyboard shortcuts:
```javascript
document.addEventListener('keydown', e => {
    if (e.key >= '1' && e.key <= '7') {
        const tag = quickFeatureTags[parseInt(e.key) - 1];
        toggleTag('feature', tag);
    }
});
```

#### C8: Batch Tagging Modal Has No Tag Removal Option
**Shneiderman**: "I can ADD tags to multiple images but can't REMOVE a tag from all selected. Asymmetric functionality."

**Fix**: Add "Remove these tags" toggle in batch modal.

#### C9: No Visual Feedback for Already-Tagged Images
**Julie Zhuo**: "In the grid, I can't quickly see which images are tagged vs. untagged without clicking each one."

**Fix**: Add visual indicator (checkmark badge, colored border) for tagged images:
```css
.thumb-card.tagged::after {
    content: '✓';
    position: absolute;
    bottom: 4px;
    right: 4px;
    background: var(--gallery-positive);
    color: white;
    border-radius: 50%;
    width: 18px;
    height: 18px;
}
```

#### C10: Export Doesn't Show What Will Be Exported
**Gary Olson**: "Clicking Export starts a download immediately. Users should see a summary first."

**Fix**: Show export preview modal with count and sample.

### Medium Priority Issues

#### M4: No Bulk Score Assignment
**Wroblewski**: "Setting refuge=0.8 for 20 similar images requires 20 individual edits. Add batch scoring."

#### M5: No Image Comparison Mode
**Rachel Kaplan**: "For research, I need to compare two images side-by-side to calibrate my scoring. Add split-screen view."

#### M6: No Tag Suggestions Based on Query
**Shneiderman**: "Images downloaded with query 'cozy reading nook' should auto-suggest 'refuge' tag. Use the preset metadata."

**Fix**: Pre-populate suggested tags from the query's preset:
```javascript
if (img.query_used) {
    const preset = findPresetForQuery(img.query_used);
    if (preset) {
        suggestedTags = preset.feature_tags;
    }
}
```

#### M7: Notes Field Too Small
**Julie Zhuo**: "60px height for notes is cramped. Make it expandable."

---

## Workflow Analysis (Bonnie John)

### Current Workflow: Collect → Tag → Export

**Step 1: Collect Images**
- Select preset OR enter custom query
- Choose source and count
- Download

**Issues**:
- No preview = uncertainty
- No duplicate awareness = wasted effort
- No progress detail = anxiety during long downloads

**Step 2: Tag Images**
- Select image in grid
- Adjust sliders
- Click quick-tags
- Add custom tags
- Save

**Issues**:
- No batch operations for similar images
- No keyboard shortcuts
- No unsaved change protection

**Step 3: Export for Gallery**
- Select images (or use "tagged only")
- Click Export
- JSON downloads

**Issues**:
- No preview of export
- No format options (JSON only)

### Recommended Workflow Improvements

1. **Add "Smart Collect" mode**: System suggests queries based on gaps in current pool coverage.

2. **Add "Similar Images" grouping**: After download, group visually similar images to enable batch tagging.

3. **Add "Tagging Queue"**: Show untagged images in a focused single-image view with keyboard navigation.

4. **Add "Export Templates"**: Pre-configured exports for different gallery builder scenarios.

---

## Accessibility Review (Summary)

| Issue | Severity | Fix |
|-------|----------|-----|
| No keyboard navigation in grids | High | Add tabindex, arrow key handlers |
| Color contrast on muted text | Medium | Increase contrast ratio to 4.5:1 |
| No ARIA labels on icon buttons | Medium | Add aria-label attributes |
| Progress announcements not screen-reader friendly | Medium | Add aria-live regions |
| No skip links | Low | Add "Skip to main content" |

---

## Streamlit Design Alignment (Julie Zhuo)

The current design captures Streamlit's aesthetic but misses some key patterns:

### Streamlit Patterns to Add

1. **Expanders**: Collapsible sections for advanced options
2. **Metrics**: Large number displays with delta indicators
3. **Data Editor**: Inline table editing for batch operations
4. **Columns**: Better use of horizontal space in forms
5. **Toast Notifications**: Already implemented, good!

### Recommended Enhancements

```html
<!-- Streamlit-style metric -->
<div class="st-metric">
    <div class="st-metric-label">Images Tagged</div>
    <div class="st-metric-value">47</div>
    <div class="st-metric-delta positive">+12 today</div>
</div>

<!-- Streamlit-style expander -->
<details class="st-expander">
    <summary>Advanced Options</summary>
    <div class="st-expander-content">
        <!-- Content here -->
    </div>
</details>
```

---

## Priority Recommendations

### BLOCKING (Fix Before Use)
1. **C1**: Progress feedback during multi-query downloads
2. **C6**: Slider values lost on selection change
3. **C9**: No visual indicator for tagged images

### HIGH (Fix This Week)
4. **C2**: Show duplicate skip count
5. **C4**: Preview before download
6. **C7**: Keyboard shortcuts for tagging
7. **C8**: Batch tag removal
8. **M6**: Tag suggestions from query preset

### MEDIUM (Phase 2)
9. **C3**: Remember source preference
10. **C5**: Keyboard navigation in chips
11. **C10**: Export preview modal
12. **M1**: Undo last download
13. **M4**: Bulk score assignment
14. **M5**: Image comparison mode

### LOW (Phase 3)
15. **M2**: Richer stats display
16. **M3**: API key setup guidance
17. **M7**: Expandable notes field

---

## Simulated User Testing

### Test Scenario 1: First-Time User Collects Refuge Images

**Task**: "Download 20 images showing refuge/enclosure for a gallery about cozy workspaces"

**Expected Path**:
1. Click "Refuge" preset
2. See 10 queries selected
3. Set count to 5 per query
4. Click "Download Selected Queries"

**Observed Issues**:
- User didn't notice they could deselect queries
- Progress bar showed 3/10 but user didn't know which query
- After download, user asked "How do I know which ones downloaded?"

**Recommendation**: Add query-level success/fail indicators in results.

### Test Scenario 2: Researcher Tags 50 Images

**Task**: "Tag these 50 office images with appropriate features and export for gallery"

**Expected Path**:
1. Go to Inspector
2. Click first image
3. Adjust sliders, add tags
4. Save, move to next
5. Repeat 50 times

**Observed Issues**:
- User tried keyboard navigation, failed
- User wanted to tag similar images together
- User accidentally clicked away, lost unsaved changes
- User asked "Is there a faster way?"

**Recommendation**: Add tagging queue mode with keyboard-driven workflow.

### Test Scenario 3: Export for Gallery Builder

**Task**: "Export all tagged refuge images for the gallery builder"

**Expected Path**:
1. Filter by feature tag "refuge"
2. Select all (or leave tagged_only)
3. Click Export

**Observed Issues**:
- User wasn't sure what format the export was in
- User wanted to see what would be exported first
- Export downloaded immediately without confirmation

**Recommendation**: Show export preview with format info.

---

## Conclusion

The Image Collector and Inspector GUIs provide solid foundational functionality but need workflow optimizations before heavy research use. The three BLOCKING issues (C1, C6, C9) should be fixed immediately. The keyboard shortcut additions (C7) would dramatically improve tagging efficiency.

The Streamlit aesthetic is well-executed. Adding expanders and better metrics would complete the look.

*Panel review completed January 28, 2026*
