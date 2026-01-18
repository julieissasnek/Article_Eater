# Article Eater GUI Style Guide & Standards
**Version**: 2.0  
**Date**: November 15, 2025  
**Status**: OFFICIAL STANDARD

---

## 🎯 Executive Summary

This document establishes comprehensive standards for all Article Eater user interfaces to ensure:
- **Cheerful appearance** - Friendly, welcoming, encouraging
- **Pure layout usability** - Intuitive, efficient, accessible
- **Effectiveness** - Users can monitor and guide all system functions
- **Consistency** - Predictable patterns across all pages
- **Professionalism** - Academic rigor with modern design

---

## 📊 Current GUI Inventory

### Active GUIs (9 total)

| File | Purpose | Lines | Status | Issues |
|------|---------|-------|--------|--------|
| `dashboard.html` | Main overview & stats | 343 | ✅ Good | Minor cheerfulness improvements needed |
| `search.html` | Submit new jobs | 513 | ✅ Good | Could use progress visualization |
| `library.html` | Browse papers | 592 | ✅ Good | Filtering could be more visual |
| `rules.html` | View synthesized rules | 653 | ✅ Good | Evidence display could be friendlier |
| `queue.html` | Monitor job processing | 563 | ✅ Good | Real-time updates need emphasis |
| `usage.html` | Track API costs | 451 | ✅ Good | Charts need more cheerful colors |
| `profile.html` | User settings & auth | 557 | ✅ Good | Forms could be more encouraging |
| `interactions.html` | Rule interactions | 15 | ⚠️ **INCOMPLETE** | Needs full implementation |
| `usage_dashboard.html` | Compact usage view | 21 | ⚠️ **MINIMAL** | Needs expansion |

###Missing GUIs (Recommended)

1. **`index.html`** - Landing/demo page showing all GUIs
2. **`findings.html`** - Browse individual findings
3. **`help.html`** - Contextual help & tutorials
4. **`reports.html`** - Generate & download reports
5. **`admin.html`** - Admin-only management (if multi-user)

---

## 🎨 Visual Design Standards

### Color Palette

**Primary Colors** (UCSD Academic):
```css
--primary-blue: #182B49      /* UCSD Navy - headers, nav */
--ucsd-gold: #C69214          /* UCSD Gold - accents, CTAs */
--accent-teal: #00C6D7        /* UCSD Teal - highlights, info */
```

**Cheerful Semantic Colors** (Positive, encouraging):
```css
--success: #00C851            /* Vibrant green - achievements */
--success-light: #D4EDDA      /* Light green background */
--warning: #FFB84D            /* Warm orange - caution */
--warning-light: #FFF3CD      /* Light yellow background */
--error: #FF6B6B              /* Friendly red - errors */
--error-light: #F8D7DA        /* Light pink background */
--info: #4FC3F7               /* Bright blue - information */
--info-light: #D1ECF1         /* Light blue background */
```

**Cheerful Accents** (NEW):
```css
--joy-purple: #9C27B0         /* Purple - celebration */
--joy-pink: #E91E63           /* Pink - highlights */
--joy-lime: #CDDC39           /* Lime - fresh, new */
--joy-cyan: #00BCD4           /* Cyan - progress */
```

**Neutrals** (Softer, friendlier):
```css
--gray-50: #FAFAFA            /* Lightest background */
--gray-100: #F5F5F5           /* Cards, panels */
--gray-200: #EEEEEE           /* Borders, dividers */
--gray-300: #E0E0E0           /* Subtle borders */
--gray-600: #757575           /* Secondary text */
--gray-900: #212121           /* Primary text */
```

### Typography

**Font Stack**:
```css
--font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
--font-mono: 'Fira Code', 'SF Mono', Monaco, monospace;
```

**Type Scale** (Clear hierarchy):
```css
--text-xs: 0.75rem      /* 12px - labels */
--text-sm: 0.875rem     /* 14px - body small */
--text-base: 1rem       /* 16px - body */
--text-lg: 1.125rem     /* 18px - lead */
--text-xl: 1.25rem      /* 20px - subtitle */
--text-2xl: 1.5rem      /* 24px - section header */
--text-3xl: 1.875rem    /* 30px - page header */
--text-4xl: 2.25rem     /* 36px - hero */
```

**Font Weights**:
```css
--font-normal: 400
--font-medium: 500
--font-semibold: 600
--font-bold: 700
```

### Spacing Scale

```css
--space-1: 0.25rem   /* 4px */
--space-2: 0.5rem    /* 8px */
--space-3: 0.75rem   /* 12px */
--space-4: 1rem      /* 16px */
--space-5: 1.25rem   /* 20px */
--space-6: 1.5rem    /* 24px */
--space-8: 2rem      /* 32px */
--space-10: 2.5rem   /* 40px */
--space-12: 3rem     /* 48px */
--space-16: 4rem     /* 64px */
```

### Border Radius (Friendly, rounded)

```css
--radius-sm: 0.375rem   /* 6px - small elements */
--radius-md: 0.5rem     /* 8px - cards */
--radius-lg: 0.75rem    /* 12px - panels */
--radius-xl: 1rem       /* 16px - large cards */
--radius-full: 9999px   /* Pills, badges */
```

### Shadows (Depth, not harshness)

```css
--shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
--shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
--shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
--shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
--shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
```

---

## 🏗️ Layout Standards

### Page Structure

Every page MUST follow this structure:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>[Page Name] - Article Eater</title>
  <link rel="stylesheet" href="css/main.css">
  <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>📚</text></svg>">
</head>
<body>
  <div class="app-container">
    <!-- Sidebar Navigation -->
    <nav class="sidebar">
      <!-- Standard nav menu -->
    </nav>
    
    <!-- Main Content -->
    <main class="main-content">
      <!-- Page Header -->
      <header class="page-header">
        <div class="header-content">
          <div class="header-title">
            <span class="header-icon">[emoji]</span>
            <h1>[Page Title]</h1>
          </div>
          <p class="header-description">[Friendly description]</p>
        </div>
        <div class="header-actions">
          <!-- Action buttons -->
        </div>
      </header>
      
      <!-- Page Content -->
      <div class="page-body">
        <!-- Main content here -->
      </div>
      
      <!-- Optional Footer -->
      <footer class="page-footer">
        <!-- Help text, tips, etc. -->
      </footer>
    </main>
  </div>
  
  <script src="js/api.js"></script>
  <script src="js/[page-specific].js"></script>
</body>
</html>
```

### Sidebar Navigation

**Must include**:
- Logo/branding at top
- All main pages with icons
- Active state highlighting
- Hover effects
- Emoji icons for friendliness

**Standard order**:
1. 📊 Dashboard
2. 🔍 New Search
3. 📚 Library
4. 🔬 Findings (NEW)
5. 📝 Rule Inspector
6. 🔄 Interactions (NEW - when implemented)
7. ⏳ Processing Queue
8. 💰 Usage & Costs
9. 📊 Reports (NEW)
10. ❓ Help (NEW)
11. 👤 Profile

---

## 🎯 Component Standards

### Buttons

**Primary Button** (Main actions):
```html
<button class="btn btn-primary">
  <span class="btn-icon">✨</span>
  <span class="btn-text">Start Magic</span>
</button>
```

**Style**:
- Background: `--ucsd-gold`
- Hover: Slightly darker + lift
- Icon + text for clarity
- Encouraging language

**Secondary Button** (Alternative actions):
```html
<button class="btn btn-secondary">
  <span class="btn-icon">🔄</span>
  <span class="btn-text">Refresh</span>
</button>
```

**Style**:
- Border: `--primary-blue`
- Hover: Light background
- Clear iconography

**Danger Button** (Destructive, but gentle):
```html
<button class="btn btn-danger">
  <span class="btn-icon">🗑️</span>
  <span class="btn-text">Remove (we'll keep a backup)</span>
</button>
```

**Style**:
- Background: `--error` but softer
- Always explain consequences
- Confirm before action

### Cards

**Standard Card**:
```html
<div class="card">
  <div class="card-header">
    <h3 class="card-title">
      <span class="card-icon">📄</span>
      Title Here
    </h3>
    <div class="card-actions">
      <!-- Quick actions -->
    </div>
  </div>
  <div class="card-body">
    <!-- Main content -->
  </div>
  <div class="card-footer">
    <!-- Metadata, actions -->
  </div>
</div>
```

**Style**:
- Background: white
- Border: subtle gray
- Shadow: `--shadow-md`
- Radius: `--radius-lg`
- Hover: Slight lift

### Stats Cards (Cheerful!)

```html
<div class="stat-card stat-card-success">
  <div class="stat-icon">🎉</div>
  <div class="stat-content">
    <div class="stat-label">Papers Processed</div>
    <div class="stat-value">42</div>
    <div class="stat-change stat-change-positive">
      <span class="stat-change-icon">📈</span>
      <span class="stat-change-text">+12 this week!</span>
    </div>
  </div>
</div>
```

**Variants**:
- `.stat-card-success` - Green, achievements
- `.stat-card-info` - Blue, information
- `.stat-card-warning` - Orange, attention
- `.stat-card-primary` - Navy, general

### Forms (Encouraging!)

```html
<div class="form-group">
  <label class="form-label">
    <span class="form-label-icon">🔍</span>
    <span class="form-label-text">What are you researching?</span>
    <span class="form-label-hint">(Be specific for better results)</span>
  </label>
  <input 
    type="text" 
    class="form-input" 
    placeholder="e.g., biophilic design in office spaces"
    aria-describedby="query-help"
  >
  <div class="form-help" id="query-help">
    💡 <strong>Tip:</strong> Include specific terms like "natural light" or "plants"
  </div>
</div>
```

**Style**:
- Clear labels with icons
- Helpful placeholders
- Inline help text
- Validation feedback (gentle!)
- Success states celebrated

### Tables (Clean, scannable)

```html
<div class="table-container">
  <table class="table">
    <thead class="table-header">
      <tr>
        <th class="table-th">
          <span class="th-icon">📄</span>
          Title
          <button class="th-sort">↕️</button>
        </th>
        <!-- More columns -->
      </tr>
    </thead>
    <tbody class="table-body">
      <tr class="table-row">
        <td class="table-cell">
          <!-- Cell content -->
        </td>
      </tr>
    </tbody>
  </table>
</div>
```

**Style**:
- Zebra striping (subtle)
- Hover highlight
- Sortable headers
- Responsive (stack on mobile)

### Alerts & Messages (Friendly!)

**Success**:
```html
<div class="alert alert-success">
  <div class="alert-icon">🎉</div>
  <div class="alert-content">
    <div class="alert-title">Awesome!</div>
    <div class="alert-message">Your job completed successfully!</div>
  </div>
  <button class="alert-close">×</button>
</div>
```

**Info**:
```html
<div class="alert alert-info">
  <div class="alert-icon">💡</div>
  <div class="alert-content">
    <div class="alert-title">Good to know</div>
    <div class="alert-message">This might take a few minutes...</div>
  </div>
</div>
```

**Warning**:
```html
<div class="alert alert-warning">
  <div class="alert-icon">⚠️</div>
  <div class="alert-content">
    <div class="alert-title">Heads up!</div>
    <div class="alert-message">Your API key expires soon</div>
  </div>
</div>
```

**Error** (Gentle!):
```html
<div class="alert alert-error">
  <div class="alert-icon">😅</div>
  <div class="alert-content">
    <div class="alert-title">Oops!</div>
    <div class="alert-message">
      Something went wrong. Don't worry, we saved your work!
    </div>
  </div>
</div>
```

---

## 🎭 Personality & Voice

### Writing Guidelines

**DO**:
- ✅ Use encouraging language: "Great job!", "Almost there!", "You got this!"
- ✅ Explain actions: "We're searching 1000+ papers for you..."
- ✅ Celebrate successes: "🎉 Found 42 relevant papers!"
- ✅ Be specific: "Processing will take ~2 minutes"
- ✅ Use emojis appropriately: 📚🔍✨🎉💡

**DON'T**:
- ❌ Be vague: "Processing..." → "Searching academic databases... ✨"
- ❌ Be harsh: "Error" → "Oops! Something unexpected happened"
- ❌ Be boring: "Submit" → "Start Discovery ✨"
- ❌ Hide information: Always show what's happening
- ❌ Overwhelm with emojis: 1-2 per section is plenty

### Button Text Examples

**Good** ✅:
- "Start Searching ✨"
- "Add to Library 📚"
- "Explore Findings 🔬"
- "Download Report 📊"
- "Save Progress 💾"

**Bad** ❌:
- "Submit"
- "Go"
- "Click Here"
- "OK"
- "Done"

### Loading States (Keep users engaged!)

**Short waits** (<5s):
```html
<div class="loading">
  <div class="loading-spinner"></div>
  <div class="loading-text">Searching... ✨</div>
</div>
```

**Medium waits** (5-30s):
```html
<div class="loading">
  <div class="loading-progress">
    <div class="progress-bar" style="width: 45%"></div>
  </div>
  <div class="loading-text">
    Finding relevant papers... 📚
    <span class="loading-detail">Checked 450 of 1000 papers</span>
  </div>
</div>
```

**Long waits** (>30s):
```html
<div class="loading loading-long">
  <div class="loading-animation">🔄</div>
  <div class="loading-text">
    This is taking a moment... ⏳
  </div>
  <div class="loading-tips">
    <div class="tip-title">💡 While you wait:</div>
    <ul class="tip-list">
      <li>Check your library for existing research</li>
      <li>Review synthesized rules</li>
      <li>Grab a coffee! ☕</li>
    </ul>
  </div>
</div>
```

---

## 📱 Responsiveness

All GUIs MUST be responsive:

### Breakpoints

```css
--breakpoint-sm: 640px    /* Small devices */
--breakpoint-md: 768px    /* Tablets */
--breakpoint-lg: 1024px   /* Laptops */
--breakpoint-xl: 1280px   /* Desktops */
--breakpoint-2xl: 1536px  /* Large screens */
```

### Mobile-First Approach

1. Design for mobile first
2. Enhance for larger screens
3. Sidebar becomes top nav on mobile
4. Cards stack vertically
5. Tables scroll or transform

---

## ♿ Accessibility

All GUIs MUST be accessible:

### Requirements

- ✅ Semantic HTML (`<nav>`, `<main>`, `<article>`, etc.)
- ✅ ARIA labels where needed
- ✅ Keyboard navigation (tab, enter, escape)
- ✅ Focus indicators (visible, high contrast)
- ✅ Color contrast ≥ 4.5:1 for text
- ✅ Alt text for images
- ✅ Screen reader friendly
- ✅ No keyboard traps

### Example

```html
<button 
  class="btn btn-primary"
  aria-label="Start new search for research papers"
  aria-describedby="search-help"
>
  <span class="btn-icon" aria-hidden="true">🔍</span>
  <span class="btn-text">Start Search</span>
</button>
<div class="sr-only" id="search-help">
  This will search academic databases for papers matching your query
</div>
```

---

## 🎯 Page-Specific Guidelines

### Dashboard

**Purpose**: Quick overview, recent activity, key metrics

**Must include**:
- Welcome message with user name
- KPI cards (papers, findings, rules, jobs)
- Recent activity feed
- Quick actions (New Search, View Library)
- System status indicator
- Helpful tips for new users

**Cheerful touches**:
- Celebrate milestones: "🎉 You've processed 100 papers!"
- Show progress: "You're on a 7-day streak! 🔥"
- Encourage action: "Ready to discover more insights? ✨"

### Search/New Job

**Purpose**: Submit new searches easily

**Must include**:
- Clear form with helpful labels
- Query builder with examples
- Parameter controls (limit, filters)
- Cost estimate before submission
- Preview of what will happen
- Submit button with encouraging text

**Cheerful touches**:
- Show example queries: "Try: 'natural light in hospitals'"
- Estimate time: "This will take ~2 minutes ⏱️"
- Confirm submission: "Great! We're on it! 🚀"

### Library

**Purpose**: Browse and filter collected papers

**Must include**:
- Search/filter bar
- Sort options (date, relevance, citations)
- Card or list view toggle
- Pagination or infinite scroll
- Quick actions (view, download, remove)
- Bulk operations
- Empty state for no results

**Cheerful touches**:
- Show collection size: "Your library has 42 papers! 📚"
- Suggest filters: "💡 Try filtering by year or author"
- Celebrate additions: "✨ Just added 5 new papers!"

### Findings

**Purpose**: Browse extracted findings

**Must include**:
- Filter by consequent/antecedent
- Sort by effect size, p-value
- Statistical visualizations
- Link to source paper
- Export options

**Cheerful touches**:
- Highlight strong findings: "⭐ High confidence!"
- Explain stats: "💡 p<0.05 means statistically significant"
- Group related findings: "🔗 5 similar findings found"

### Rules

**Purpose**: View synthesized multi-paper rules

**Must include**:
- Confidence scores (visual!)
- Evidence links
- Contradiction indicators
- Filtering by topic
- Export capabilities

**Cheerful touches**:
- Rate confidence visually: ⭐⭐⭐⭐⭐
- Show paper count: "Based on 12 papers 📚"
- Highlight consensus: "✅ Strong agreement across studies"

### Queue

**Purpose**: Monitor background jobs

**Must include**:
- Real-time status updates
- Progress bars with %
- Estimated completion time
- Error details (if failed)
- Retry options
- Cancel capability

**Cheerful touches**:
- Animate progress: "🔄 Processing L2 (45%)"
- Estimate time: "~3 minutes remaining ⏱️"
- Celebrate completion: "🎉 Job completed in 2m 15s!"

### Usage & Costs

**Purpose**: Track API usage transparently

**Must include**:
- Current period costs
- Historical charts
- Per-operation breakdown
- Remaining quota
- Cost projections
- Export/download invoices

**Cheerful touches**:
- Show savings: "💰 Saved $12 with caching!"
- Budget friendly: "You're under budget! 🎯"
- Explain costs: "Each search costs ~$0.05"

### Profile

**Purpose**: Manage account and preferences

**Must include**:
- User info display
- Password change
- API key management
- Preferences (theme, notifications)
- Data export
- Account deletion (with warnings)

**Cheerful touches**:
- Greet user: "Hey [Name]! 👋"
- Confirm saves: "✅ Settings saved!"
- Protect data: "🔒 Your data is encrypted"

---

## 🚀 Implementation Checklist

For each GUI page:

- [ ] Follows standard page structure
- [ ] Uses semantic HTML5
- [ ] Includes navigation sidebar
- [ ] Has page header with icon and description
- [ ] Uses CSS variables from style guide
- [ ] Implements cheerful color palette
- [ ] Has encouraging copy and button text
- [ ] Includes helpful loading states
- [ ] Shows clear error messages (gentle!)
- [ ] Celebrates successes with emojis
- [ ] Is fully responsive (mobile-first)
- [ ] Meets accessibility standards
- [ ] Has keyboard navigation
- [ ] Includes inline help/tooltips
- [ ] Shows clear empty states
- [ ] Has proper page title and meta
- [ ] Includes favicon
- [ ] Links to correct CSS/JS
- [ ] Has no console errors
- [ ] Tested in Chrome, Firefox, Safari

---

## 📝 File Naming Conventions

### HTML Files
- Lowercase with hyphens: `processing-queue.html`
- Descriptive names: `new-search.html` not `search.html`
- Index for landing: `index.html`

### CSS Files
- `main.css` - Core styles
- `components.css` - Reusable components (optional)
- `utilities.css` - Utility classes (optional)

### JS Files
- `api.js` - API client (shared)
- `[page-name].js` - Page-specific logic
- `components.js` - Reusable components (optional)

---

## 🎨 Quick Reference: Cheerfulness Checklist

Every page should have AT LEAST:

1. **3 emojis** in meaningful places (not random!)
2. **1 encouraging message** (welcome, tip, or celebration)
3. **2 helpful hints** (tooltips, inline help, or tips)
4. **Colorful status** (use semantic colors, not just gray)
5. **Clear next steps** (always guide users forward)

---

## 📚 Resources

**Design Inspiration**:
- Linear (clean, modern)
- Notion (friendly, helpful)
- GitHub (clear, professional)
- Stripe (confident, precise)

**Accessibility**:
- WCAG 2.1 AA standards
- ARIA Authoring Practices Guide
- WebAIM resources

**Components**:
- Tailwind CSS (utility-first inspiration)
- Bootstrap (component patterns)
- Material Design (interaction patterns)

---

## 🔄 Maintenance

This style guide should be:
- **Reviewed** quarterly
- **Updated** when patterns emerge
- **Enforced** in code reviews
- **Referenced** by all developers
- **Celebrated** when followed! 🎉

---

**End of Style Guide**

*Last updated: 2025-11-15*  
*Version: 2.0*  
*Maintained by: Article Eater Team*