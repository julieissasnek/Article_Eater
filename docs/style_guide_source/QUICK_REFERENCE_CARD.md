# Article Eater GUI Quick Reference Card
## Fast Lookup for Common Patterns & CSS Variables

**Version**: 20.3.0 | **Last Updated**: November 16, 2025

---

## 🎨 CSS Custom Properties Cheat Sheet

### Colors
```css
/* Brand */
--primary-blue: #182B49
--ucsd-gold: #C69214
--accent-teal: #00C6D7

/* Status */
--success: #00C851       --success-light: #D4EDDA
--warning: #FFB84D       --warning-light: #FFF3CD
--error: #FF6B6B         --error-light: #F8D7DA
--info: #4FC3F7          --info-light: #D1ECF1

/* Grays (50-900) */
--gray-50 to --gray-900 (lightest to darkest)
```

### Typography
```css
/* Sizes: xs, sm, base, lg, xl, 2xl, 3xl, 4xl */
--text-xs: 0.75rem       --text-2xl: 1.5rem
--text-sm: 0.875rem      --text-3xl: 1.875rem
--text-base: 1rem        --text-4xl: 2.25rem
--text-lg: 1.125rem
--text-xl: 1.25rem

/* Weights */
--font-normal: 400    --font-semibold: 600
--font-medium: 500    --font-bold: 700
```

### Spacing
```css
/* 1-16 (in powers/multiples) */
--space-1: 0.25rem    --space-6: 1.5rem
--space-2: 0.5rem     --space-8: 2rem
--space-3: 0.75rem    --space-10: 2.5rem
--space-4: 1rem       --space-12: 3rem
--space-5: 1.25rem    --space-16: 4rem
```

### Other
```css
/* Radius: sm, md, lg, xl, 2xl, full */
--radius-lg: 0.75rem

/* Shadows: sm, (default), md, lg, xl, 2xl */
--shadow-md: 0 4px 6px -1px rgba(0,0,0,0.1)

/* Transitions */
--transition-fast: 150ms ease
--transition-base: 200ms ease
--transition-slow: 300ms ease
```

---

## 🧱 Component Snippets

### Button Patterns
```html
<!-- Primary CTA -->
<button class="btn btn-primary">
  <span class="btn-icon">➕</span>
  Action Text
</button>

<!-- Secondary -->
<button class="btn btn-secondary">Text</button>

<!-- Variants: success, danger, ghost -->
```

### Card
```html
<div class="card">
  <div class="card-header">
    <h3 class="card-title">
      <span class="card-icon">📄</span>
      Title
    </h3>
    <span class="badge badge-success">Status</span>
  </div>
  <div class="card-body">
    Content
  </div>
  <div class="card-footer">
    Footer
  </div>
</div>
```

### Stat Card
```html
<div class="stat-card stat-card-success">
  <div class="stat-icon">📚</div>
  <div class="stat-content">
    <div class="stat-label">Label</div>
    <div class="stat-value">47</div>
    <div class="stat-change stat-change-positive">
      <span class="stat-change-icon">↗</span>
      +12 change
    </div>
  </div>
</div>

<!-- Variants: stat-card-success, info, warning, primary -->
```

### Alert
```html
<div class="alert alert-success">
  <div class="alert-icon">✓</div>
  <div class="alert-content">
    <div class="alert-title">Title</div>
    <div class="alert-message">Message</div>
  </div>
  <button class="alert-close">×</button>
</div>

<!-- Variants: success, info, warning, error -->
```

### Badge
```html
<span class="badge badge-success">Complete</span>
<!-- Variants: success, info, warning, error -->
```

### Form
```html
<div class="form-group">
  <label class="form-label">
    <span class="form-label-icon">📝</span>
    Label Text
    <span class="form-label-hint">(Optional)</span>
  </label>
  <input type="text" class="form-input" placeholder="...">
  <div class="form-help">Helper text</div>
</div>
```

### Progress Bar
```html
<div class="progress">
  <div class="progress-bar" style="width: 65%;">65%</div>
</div>
```

### Empty State
```html
<div class="empty-state">
  <div class="empty-state-icon">📂</div>
  <h2 class="empty-state-title">No Items</h2>
  <p class="empty-state-message">Description</p>
  <button class="btn btn-primary">Action</button>
</div>
```

### Loading Spinner
```html
<div class="loading">
  <div class="loading-spinner"></div>
  <div class="loading-text">
    Loading...
    <span class="loading-detail">Detail text</span>
  </div>
</div>
```

---

## 📊 View Density System

### View Toggle Component
```html
<div class="view-toggle">
  <button class="view-toggle-btn active" data-view-toggle="cards">
    <span>📱</span> Cards
  </button>
  <button class="view-toggle-btn" data-view-toggle="compact">
    <span>📋</span> Compact
  </button>
  <button class="view-toggle-btn" data-view-toggle="list">
    <span>📊</span> List
  </button>
</div>

<div id="content-container" class="cards-view">
  <!-- Content -->
</div>
```

### View-Specific Classes

**Cards View** (Default)
- Full padding and spacing
- All content visible
- Maximum detail

**Compact View**
```css
.compact-view .card { margin-bottom: var(--space-2); }
.compact-view .card-header { padding: var(--space-3) var(--space-4); }
.compact-view .card-body { padding: var(--space-3) var(--space-4); }
.compact-view .card-title { font-size: var(--text-base); }
```

**List View**
```css
.list-view .card { 
  margin-bottom: 0;
  border-radius: 0;
  border-bottom: 1px solid var(--gray-200);
}
.list-view .card-body { display: none; }
.list-view .card:hover { background: var(--gray-50); }
```

---

## 🎯 Common Layout Patterns

### Page Structure
```html
<div class="app-container">
  <nav class="sidebar">
    <div class="nav-logo">
      <span class="nav-logo-emoji">📚</span>
      Article Eater
    </div>
    <ul class="nav-menu">
      <li class="nav-item">
        <a href="#" class="nav-link active">
          <span class="nav-icon">📊</span>
          Dashboard
        </a>
      </li>
    </ul>
  </nav>

  <main class="main-content">
    <header class="page-header">
      <div class="header-content">
        <div class="header-title">
          <span class="header-icon">📊</span>
          <h1>Page Title</h1>
        </div>
        <p class="header-description">Description</p>
      </div>
      <div class="header-actions">
        <!-- Actions -->
      </div>
    </header>

    <!-- Content -->
  </main>
</div>
```

### Stats Grid
```html
<div class="stats-grid">
  <!-- 2-4 stat cards -->
  <div class="stat-card stat-card-primary">...</div>
  <div class="stat-card stat-card-success">...</div>
  <div class="stat-card stat-card-info">...</div>
</div>
```

---

## ⚡ JavaScript Patterns

### View Controller Setup
```javascript
const viewController = new CompactViewController('container-id', {
  pageName: 'library',
  defaultView: 'cards',
  renderCards: () => { /* return HTML */ },
  renderCompact: () => { /* return HTML */ },
  renderList: () => { /* return HTML */ }
});
```

### View Preference Storage
```javascript
// Save
localStorage.setItem('view_pagename', 'cards');

// Load
const view = localStorage.getItem('view_pagename') || 'cards';
```

---

## 🎨 Design Principles Checklist

When building new UI:

✓ **Cheerful**: Rounded corners, friendly gradients, emoji icons  
✓ **Clear**: Obvious hierarchy, visible states, progressive disclosure  
✓ **Precise**: Minimal clicks, right amount of info, obvious CTAs  
✓ **Efficient**: Three view options, space-optimized, fast interactions  
✓ **Accessible**: Contrast ≥4.5:1, keyboard nav, ARIA labels  

---

## 🔍 Common CSS Utilities

```css
/* Text */
.text-center { text-align: center; }
.text-right { text-align: right; }
.text-gray-600 { color: var(--gray-600); }
.text-success { color: var(--success); }

/* Spacing */
.mt-4 { margin-top: var(--space-4); }
.mb-4 { margin-bottom: var(--space-4); }

/* Flex */
.flex { display: flex; }
.flex-col { flex-direction: column; }
.items-center { align-items: center; }
.justify-between { justify-content: space-between; }
.gap-4 { gap: var(--space-4); }

/* Screen Reader */
.sr-only { /* visually hidden but readable */ }
```

---

## 📱 Responsive Breakpoints

```css
/* Mobile */
@media (max-width: 640px) { }

/* Tablet */
@media (max-width: 768px) { }

/* Desktop */
@media (max-width: 1024px) { }
```

**Mobile Guidelines:**
- Auto-switch to compact/list view
- Stack page header vertically
- Full-width view toggle
- Collapsible sidebar

---

## 🎯 Quick Decision Matrix

| Need | Use |
|------|-----|
| Primary action | `.btn-primary` |
| Status indicator | `.badge-{variant}` |
| Numerical summary | `.stat-card` |
| Detailed content | `.card` with header/body/footer |
| User feedback | `.alert-{variant}` |
| Form field | `.form-group` wrapper |
| Empty content | `.empty-state` |
| Processing | `.loading` with spinner |
| List of items | View density toggle |
| High emphasis | `--ucsd-gold` background |
| Moderate emphasis | `--primary-blue` |
| Low emphasis | Gray shades |

---

## 🚀 Performance Tips

1. **View Density**: Use list view for 100+ items
2. **Lazy Loading**: Paginate in cards/compact view
3. **Debounce**: Search inputs, filter changes
4. **LocalStorage**: Save view preferences per page
5. **Transitions**: Use `transform` over position changes

---

## ✅ Pre-Flight Checklist

Before committing new UI:

- [ ] All colors from CSS variables
- [ ] Consistent spacing (use --space-N)
- [ ] Hover/focus states added
- [ ] Works in all 3 view densities (if list-based)
- [ ] Mobile responsive
- [ ] Keyboard accessible
- [ ] ARIA labels where needed
- [ ] Loading states handled
- [ ] Empty states handled
- [ ] Error states handled

---

**Quick Tip**: When in doubt, copy an existing similar component and modify. Consistency > novelty.

---

## 📚 Full Documentation

See `ARTICLE_EATER_GUI_STYLE_GUIDE.md` for:
- Complete design philosophy
- Detailed component documentation
- Accessibility guidelines
- Implementation patterns
- Code examples

---

**Last Updated**: November 16, 2025 | **Version**: 20.3.0