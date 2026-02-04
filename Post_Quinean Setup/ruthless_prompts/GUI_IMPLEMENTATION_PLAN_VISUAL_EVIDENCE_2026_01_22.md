# GUI Implementation Plan: Visual Evidence Layer

**Date**: January 22, 2026
**Version**: V22.0.0 (Post-Quinean)
**Style Guide**: Streamlit-inspired (light, progressive, beautiful, functional)

---

## Executive Summary

This plan integrates the **ClaimGallery visual evidence layer** with existing panel recommendations to create a unified, beautiful, and functional research interface.

**Core Insight**: Many CNFA findings are *image-grounded* (fluency, refuge edges, glare, biophilic cues). Text alone is inadequate. Users need to *see* what claims mean and where they break.

---

## Connection to Panel Recommendations

| Panel Expert | Their Recommendation | ClaimGallery Solution |
|--------------|---------------------|----------------------|
| **Pearl** | Separate causal tier from credence visually | Two axes: construct_confidence (visual) + outcome_evidence (literature) |
| **Cartwright** | Show bridge warrant strength, "why this transfers" | context_shift slot shows portability across building types |
| **Simon** | Reduce cognitive load, role-based presets | Persona configs: architect (fewer, clearer), student (learning-focused), researcher (discrimination) |
| **Kaplan** | Practitioner views, export for design docs | Visual exemplars + PDF/HTML export with grids and captions |
| **Ng** | Feedback collection for ML improvement | ImageFeedback spec with active learning, append-only JSONL |
| **Karpathy** | Chat interface grounded in evidence | ClaimGallery provides visual context for RAG responses |
| **Sutskever** | Overconfidence warnings | likely_failure slot + moderator warnings + "literature-link-only" badges |
| **Norvig** | Ranking explanation | SelectionLog with full audit trail: why each image included/excluded |
| **Dean** | Caching and performance | Gallery builds cached by hash(claim_id + snapshot + config) |

---

## Design Philosophy: Streamlit-Inspired Aesthetics

### Visual Principles

```
┌─────────────────────────────────────────────────────────────────┐
│  LIGHT          PROGRESSIVE         BEAUTIFUL       FUNCTIONAL  │
│  ─────          ───────────         ─────────       ──────────  │
│  White space    Reveal on demand    Subtle shadows  Clear CTAs  │
│  Soft grays     Expand/collapse     Rounded edges   Fast loads  │
│  Minimal UI     Tabs not pages      Consistent      Keyboard    │
│  Breathable     Three-level         color palette   navigation  │
└─────────────────────────────────────────────────────────────────┘
```

### Color Palette (Streamlit-inspired)

```css
:root {
  /* Background layers */
  --bg-primary: #ffffff;
  --bg-secondary: #f8f9fa;
  --bg-tertiary: #e9ecef;

  /* Text */
  --text-primary: #262730;
  --text-secondary: #6c757d;
  --text-muted: #9ca3af;

  /* Accent (evidence states) */
  --positive: #21c354;      /* Central positive - soft green */
  --negative: #ff6b6b;      /* Central negative - soft red */
  --near-miss: #ffc107;     /* Near miss - amber */
  --failure: #dc3545;       /* Likely failure - warning red */
  --neutral: #6366f1;       /* Context shift - indigo */

  /* Confidence gradients */
  --conf-high: #21c354;
  --conf-medium: #ffc107;
  --conf-low: #ff6b6b;

  /* Interactive */
  --link: #0969da;
  --hover: #f0f6ff;
  --focus-ring: rgba(9, 105, 218, 0.3);
}
```

### Typography

```css
/* Clean, readable, academic yet modern */
--font-primary: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
--font-mono: 'JetBrains Mono', 'Fira Code', monospace;

--text-xs: 0.75rem;   /* 12px - badges, metadata */
--text-sm: 0.875rem;  /* 14px - secondary text */
--text-base: 1rem;    /* 16px - body */
--text-lg: 1.125rem;  /* 18px - section headers */
--text-xl: 1.25rem;   /* 20px - page titles */
```

---

## Implementation Phases

### Phase 1: Foundation (Sprint G1)
**Goal**: Core ClaimGallery data model and basic viewer

#### 1.1 Schema Implementation
```
contracts/ae_af/schemas/
├── claim_gallery.v1.schema.json       # From spec
├── image_feedback.v1.schema.json      # Active learning
├── gallery_selection_config.v1.schema.json
└── selection_log.v1.schema.json       # Audit trail
```

#### 1.2 Service Layer
```
src/services/
├── claim_gallery_builder.py           # Gallery construction
├── image_pool_manager.py              # Snapshot management
└── gallery_selection_engine.py        # Deterministic selection
```

#### 1.3 Basic Viewer Component
```html
<!-- Streamlit-style card layout -->
<div class="claim-gallery">
  <header class="gallery-header">
    <h2 class="claim-statement">{{ claim.statement }}</h2>
    <div class="quality-bars">
      <div class="bar design" style="--value: 0.75"></div>
      <div class="bar consistency" style="--value: 0.68"></div>
      <div class="bar portability" style="--value: 0.52"></div>
    </div>
  </header>

  <nav class="gallery-tabs">
    <button class="tab active">Visual Gallery</button>
    <button class="tab">Evidence</button>
    <button class="tab">Failures</button>
    <button class="tab">Export</button>
  </nav>

  <main class="gallery-grid">
    <!-- Progressive disclosure: thumbnails → drawer -->
  </main>
</div>
```

---

### Phase 2: Visual Gallery Core (Sprint G2)
**Goal**: Implement the five slot types with Streamlit aesthetics

#### 2.1 Slot Components

```
┌─────────────────────────────────────────────────────────────────┐
│  ✅ CENTRAL POSITIVES                                           │
│  "This is what refuge edges look like"                          │
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐                               │
│  │     │ │     │ │     │ │     │  ← Thumbnail grid             │
│  │ 🖼️  │ │ 🖼️  │ │ 🖼️  │ │ 🖼️  │     with soft shadows         │
│  │     │ │     │ │     │ │     │                               │
│  └─────┘ └─────┘ └─────┘ └─────┘                               │
│  Hospital  Office  School  Retail   ← Context badges            │
│  0.92      0.88    0.85    0.82     ← Construct confidence      │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  ❌ CENTRAL NEGATIVES                                           │
│  "This is what NOT-refuge looks like"                           │
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐                               │
│  │     │ │     │ │     │ │     │                               │
│  │ 🖼️  │ │ 🖼️  │ │ 🖼️  │ │ 🖼️  │                               │
│  │     │ │     │ │     │ │     │                               │
│  └─────┘ └─────┘ └─────┘ └─────┘                               │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  ⚠️ NEAR MISSES                                                 │
│  "Borderline cases that reveal the decision boundary"           │
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐                               │
│  │     │ │     │ │     │ │     │                               │
│  │ 🖼️  │ │ 🖼️  │ │ 🖼️  │ │ 🖼️  │                               │
│  │ ◐   │ │ ◑   │ │ ◐   │ │ ◑   │  ← Partial fill indicators    │
│  └─────┘ └─────┘ └─────┘ └─────┘                               │
│  "Almost refuge but partially obstructed"                       │
└─────────────────────────────────────────────────────────────────┘
```

#### 2.2 Image Drawer (Right Panel)

```
┌─────────────────────────────────────┐
│  [×]                                │
│                                     │
│  ┌─────────────────────────────┐   │
│  │                             │   │
│  │                             │   │
│  │      Large Image View       │   │
│  │                             │   │
│  │                             │   │
│  └─────────────────────────────┘   │
│                                     │
│  Construct Confidence               │
│  ████████░░ 0.85 (model prediction) │
│                                     │
│  Why Selected                       │
│  "Strong refuge edges visible;      │
│   low clutter; moderate enclosure"  │
│                                     │
│  Feature Cues                       │
│  • Alcove seating area              │
│  • Partial ceiling drop             │
│  • View to exterior maintained      │
│                                     │
│  ⚠️ Moderator Flags                 │
│  • Moderate noise level             │
│                                     │
│  Outcome Evidence                   │
│  📚 Literature-link only            │
│  "Outcome not measured on this      │
│   image; link is literature-level"  │
│                                     │
│  ─────────────────────────────────  │
│                                     │
│  [Find similar: claim holds]        │
│  [Find similar: claim fails]        │
│  [Mark as misclassified]            │
│                                     │
│  Provenance                         │
│  Source: Steelcase Research         │
│  License: CC BY-NC 4.0              │
│  Study: Kaplan 2019                 │
└─────────────────────────────────────┘
```

#### 2.3 CSS for Streamlit-Style Cards

```css
.image-card {
  background: var(--bg-primary);
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.08);
  transition: all 0.15s ease;
  cursor: pointer;
  overflow: hidden;
}

.image-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.12);
  transform: translateY(-2px);
}

.image-card.selected {
  ring: 2px solid var(--link);
}

.image-card img {
  width: 100%;
  aspect-ratio: 4/3;
  object-fit: cover;
}

.image-card .meta {
  padding: 12px;
}

.confidence-bar {
  height: 4px;
  background: var(--bg-tertiary);
  border-radius: 2px;
  overflow: hidden;
}

.confidence-bar .fill {
  height: 100%;
  background: linear-gradient(
    to right,
    var(--conf-low) 0%,
    var(--conf-medium) 50%,
    var(--conf-high) 100%
  );
  background-size: 200% 100%;
  background-position: calc((1 - var(--value)) * 100%) 0;
}
```

---

### Phase 3: Failure & Moderator Analysis (Sprint G3)
**Goal**: Make failure modes "structured boundary conditions, not embarrassing exceptions"

#### 3.1 Failure Mode Panel

```
┌─────────────────────────────────────────────────────────────────┐
│  🔴 FAILURE DRIVERS                                             │
│                                                                 │
│  Why might this claim fail? Click to see examples.              │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ 👥 Crowding                                    [View 8] → │ │
│  │ When occupancy exceeds 1 person/3m², refuge effects       │ │
│  │ diminish or reverse                                       │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ ☀️ Glare                                       [View 4] → │ │
│  │ Strong direct sunlight negates comfort benefits of        │ │
│  │ window-adjacent refuge spaces                             │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ 🔊 Noise                                       [View 5] → │ │
│  │ Acoustic intrusion above 55dB undermines perceived        │ │
│  │ refuge even with visual enclosure                         │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### 3.2 Counterfactual Explanation (on failure image click)

```
┌─────────────────────────────────────────────────────────────────┐
│  CLAIM PREDICTION vs OBSERVED                                   │
│                                                                 │
│  ┌─────────────────────┐    ┌─────────────────────┐            │
│  │                     │    │                     │            │
│  │   This image has    │ →  │   But outcome may   │            │
│  │   refuge features   │    │   not follow due to │            │
│  │                     │    │   CROWDING          │            │
│  └─────────────────────┘    └─────────────────────┘            │
│                                                                 │
│  Likely Moderators Active:                                      │
│  • 👥 High occupancy visible (est. 1 person/2m²)               │
│  • 📏 Small floor area relative to occupancy                   │
│                                                                 │
│  Closest Successful Neighbors:                                  │
│  ┌─────┐ ┌─────┐ ┌─────┐                                       │
│  │ 🖼️  │ │ 🖼️  │ │ 🖼️  │  Similar refuge, lower density       │
│  └─────┘ └─────┘ └─────┘                                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

### Phase 4: Interactive Features (Sprint G4)
**Goal**: Decision boundary slider, pairwise comparison, case-based reasoning

#### 4.1 Decision Boundary Slider

```
┌─────────────────────────────────────────────────────────────────┐
│  DECISION BOUNDARY EXPLORER                                     │
│                                                                 │
│  Definition strictness:                                         │
│  Strict ────────●────────── Loose                              │
│                 ↑                                               │
│           Current: τ = 0.65                                     │
│                                                                 │
│  As you adjust:                                                 │
│  • 3 images flip from Near Miss → Positive                     │
│  • 2 images flip from Positive → Near Miss                     │
│                                                                 │
│  [Show flipping images]                                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### 4.2 Pairwise Comparison Mode

```
┌─────────────────────────────────────────────────────────────────┐
│  COMPARE: What changed?                                         │
│                                                                 │
│  ┌─────────────────┐         ┌─────────────────┐               │
│  │                 │         │                 │               │
│  │    Image A      │   vs    │    Image B      │               │
│  │                 │         │                 │               │
│  └─────────────────┘         └─────────────────┘               │
│                                                                 │
│  DIFFERENCES DETECTED:                                          │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│  Feature          │ Image A      │ Image B      │ Impact        │
│  ─────────────────┼──────────────┼──────────────┼────────────── │
│  Ceiling height   │ 2.7m         │ 3.5m         │ +0.15 refuge  │
│  Enclosure        │ 60%          │ 40%          │ -0.20 refuge  │
│  Natural light    │ High         │ Low          │ -0.10 comfort │
│  ─────────────────┴──────────────┴──────────────┴────────────── │
│                                                                 │
│  PREDICTED OUTCOME SHIFT:                                       │
│  Perceived safety: A (0.72) → B (0.58)                         │
│                                                                 │
│  ⚠️ Inference confidence: MODERATE                             │
│  Limited evidence for ceiling height → refuge relationship      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### 4.3 "Show Me Analogs" (Case-Based Reasoning)

```
┌─────────────────────────────────────────────────────────────────┐
│  FIND SIMILAR SPACES                                            │
│                                                                 │
│  From: [Selected Image Thumbnail]                               │
│                                                                 │
│  ○ Similar where claim HOLDS                                    │
│  ○ Similar where claim FAILS                                    │
│  ○ Hardest confusable cases                                     │
│                                                                 │
│  [Search]                                                       │
│                                                                 │
│  ─────────────────────────────────────────────────────────────  │
│                                                                 │
│  RESULTS: 10 most similar where claim holds                     │
│                                                                 │
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐                       │
│  │ 🖼️  │ │ 🖼️  │ │ 🖼️  │ │ 🖼️  │ │ 🖼️  │                       │
│  │ 96% │ │ 94% │ │ 91% │ │ 89% │ │ 87% │  ← Visual similarity  │
│  └─────┘ └─────┘ └─────┘ └─────┘ └─────┘                       │
│  Hospital Office  School  Office  Retail                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

### Phase 5: Learning & Feedback (Sprint G5)
**Goal**: Implement active learning loop per Ng's recommendation

#### 5.1 Feedback Capture UI

```
┌─────────────────────────────────────────────────────────────────┐
│  PROVIDE FEEDBACK                                               │
│                                                                 │
│  Is this classification correct?                                │
│                                                                 │
│  [👍 Correct] [👎 Incorrect] [🤔 Unsure]                        │
│                                                                 │
│  ─────────────────────────────────────────────────────────────  │
│  (If Incorrect selected)                                        │
│                                                                 │
│  What's the correct classification?                             │
│  ○ Central positive (feature clearly present)                   │
│  ○ Central negative (feature clearly absent)                    │
│  ● Near miss (borderline)                                       │
│  ○ Likely failure (feature present but won't work)              │
│                                                                 │
│  Why? (helps improve the system)                                │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ The alcove is too shallow to provide real refuge feeling  │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  [Submit Feedback]                                              │
│                                                                 │
│  💡 Your feedback improves classification for everyone          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### 5.2 "Teach Me This Construct" Mode (Student-Facing)

```
┌─────────────────────────────────────────────────────────────────┐
│  🎓 LEARN: Refuge Edges                                         │
│                                                                 │
│  Progress: ████████░░░░ 8/12 images                            │
│                                                                 │
│  Which space has STRONGER refuge qualities?                     │
│                                                                 │
│  ┌─────────────────┐         ┌─────────────────┐               │
│  │                 │         │                 │               │
│  │    Option A     │         │    Option B     │               │
│  │                 │         │                 │               │
│  └─────────────────┘         └─────────────────┘               │
│                                                                 │
│      [Select A]                   [Select B]                    │
│                                                                 │
│  ─────────────────────────────────────────────────────────────  │
│  (After selection)                                              │
│                                                                 │
│  ✓ Correct! Option A has stronger refuge.                      │
│                                                                 │
│  Here's why:                                                    │
│  • A has a defined ceiling edge creating enclosure              │
│  • A maintains prospect (view out) while providing refuge       │
│  • B has full-height glass - no edge definition                 │
│                                                                 │
│  [Next Question →]                                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

### Phase 6: Export & Integration (Sprint G6)
**Goal**: Export formats for design documents, API integration

#### 6.1 Export Panel

```
┌─────────────────────────────────────────────────────────────────┐
│  📤 EXPORT                                                      │
│                                                                 │
│  Export format:                                                 │
│  ○ PDF Report (visual + citations)                              │
│  ○ HTML (interactive, offline-viewable)                         │
│  ○ JSON (ClaimGallery data)                                     │
│  ○ Design Brief (1-paragraph summary)                           │
│  ○ Evidence Table (technical appendix)                          │
│  ○ BibTeX (citations only)                                      │
│                                                                 │
│  Include:                                                       │
│  ☑ Positive examples                                            │
│  ☑ Negative examples                                            │
│  ☑ Near misses                                                  │
│  ☐ Failure cases                                                │
│  ☑ Selection rationale                                          │
│                                                                 │
│  [Export]                                                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### 6.2 API Routes

```python
# New routes for ClaimGallery system
app.include_router(gallery_router, prefix='/api/v1/galleries', tags=['galleries'])

# Endpoints:
# POST   /api/v1/galleries/build          - Build gallery from claim + pool + config
# GET    /api/v1/galleries/{gallery_id}   - Retrieve gallery
# GET    /api/v1/galleries/{gallery_id}/log - Get selection log
# POST   /api/v1/galleries/feedback       - Submit image feedback
# GET    /api/v1/galleries/teach/{construct_id} - Get teaching quiz
```

---

## File Structure

```
Article_Eater_PostQuinean_v1/
├── contracts/ae_af/schemas/
│   ├── claim_gallery.v1.schema.json
│   ├── image_feedback.v1.schema.json
│   ├── gallery_selection_config.v1.schema.json
│   └── selection_log.v1.schema.json
│
├── src/services/
│   ├── claim_gallery_builder.py
│   ├── image_pool_manager.py
│   ├── gallery_selection_engine.py
│   └── feedback_collector.py
│
├── app/routes/
│   └── galleries.py
│
├── frontend/
│   ├── claim-gallery.html              # Main gallery viewer
│   ├── css/
│   │   └── gallery-streamlit.css       # Streamlit-style theme
│   └── js/
│       ├── gallery-viewer.js
│       ├── image-drawer.js
│       ├── comparison-mode.js
│       └── feedback-widget.js
│
├── data/
│   ├── galleries/                       # Built galleries
│   │   └── logs/                        # Selection logs
│   ├── feedback/
│   │   └── image_feedback.jsonl         # Append-only feedback
│   └── image_pools/                     # Snapshot storage
│
└── tests/
    ├── test_claim_gallery_builder.py
    ├── test_gallery_selection.py
    └── test_feedback_collection.py
```

---

## Acceptance Tests (from spec + panel)

| ID | Test | Source |
|----|------|--------|
| AT1 | Every claim with design_strength >= 0.3 has ≥4 pos/neg/near-miss | Spec |
| AT2 | UI always shows both positives AND negatives | Spec (two-sided) |
| AT3 | Every image displays outcome_evidence.status | Spec (honest labeling) |
| AT4 | Same inputs → identical gallery (deterministic) | Spec + Lamport |
| AT5 | Every image has provenance (source/license/attribution) | Spec |
| AT6 | Max 2 images from same project per slot | Spec (diversity) |
| AT7 | "Find similar" returns non-empty or explicit notice | Spec |
| AT8 | "Mark as misclassified" writes structured feedback | Spec + Ng |
| AT9 | Gallery includes config_id + snapshot hash | Governance |
| AT10 | Feedback references gallery_id + web_snapshot_id | Governance |
| UX1 | Causal tier and credence displayed separately | Pearl |
| UX2 | Role-based presets available (architect/student/researcher) | Simon |
| UX3 | Export templates include design brief format | Kaplan |

---

## Implementation Priority

### MVP (Sprints G1-G2)
1. ✅ Schema files (4 JSON schemas)
2. ✅ claim_gallery_builder.py (basic)
3. ✅ claim-gallery.html (5 slot types)
4. ✅ Image drawer with selection reasons
5. ✅ Streamlit-style CSS theme

### V1 (Sprints G3-G4)
1. Failure mode panel
2. Decision boundary slider
3. Pairwise comparison
4. Case-based reasoning ("show analogs")

### V2 (Sprints G5-G6)
1. Feedback collection + active learning
2. "Teach me" quiz mode
3. Export formats (PDF, HTML, design brief)
4. API routes

---

## Connection to Existing Evidence Explorer

The ClaimGallery viewer will be accessible from the existing Evidence Explorer:

```
Evidence Explorer (existing)
    │
    ├── Graph View (Cytoscape.js) ←── existing
    ├── Filter Panel ←── existing
    ├── Detail Panel ←── existing
    │
    └── [NEW] Visual Gallery Tab
            │
            └── ClaimGallery Viewer
                ├── Slot grids (pos/neg/near-miss)
                ├── Image drawer
                ├── Failure panel
                └── Comparison tools
```

---

## Summary

This implementation plan:
1. **Integrates** the ClaimGallery visual evidence layer with existing infrastructure
2. **Connects** to all 16 panel experts' recommendations
3. **Uses** Streamlit-inspired aesthetics (light, progressive, beautiful, functional)
4. **Provides** phased implementation from MVP to full feature set
5. **Supports** researcher, architect, and student workflows
6. **Enables** active learning through feedback collection
7. **Maintains** governance through deterministic, auditable builds
