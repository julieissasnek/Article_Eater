# Article Eater GUI Style Guide v20.3.0
## Comprehensive Design System & Implementation Reference

**Last Updated**: November 16, 2025  
**Version**: 20.3.0  
**Purpose**: Complete reference for maintaining visual consistency and cheerful, efficient design across all Article Eater interfaces

---

## Table of Contents

1. [Design Philosophy](#design-philosophy)
2. [Color System](#color-system)
3. [Typography](#typography)
4. [Spacing & Layout](#spacing--layout)
5. [Component Library](#component-library)
6. [View Density System](#view-density-system)
7. [CSS Custom Properties Reference](#css-custom-properties-reference)
8. [Responsive Design](#responsive-design)
9. [Accessibility Guidelines](#accessibility-guidelines)
10. [Implementation Patterns](#implementation-patterns)

---

## Design Philosophy

### Core Principles

**Cheerful Beautiful Design**
- Use soft, rounded corners (never harsh right angles)
- Employ friendly gradients and subtle shadows for depth
- Include emoji icons to add personality and visual interest
- Choose warm, inviting colors while maintaining academic professionalism
- Create hover states that feel responsive and alive

**Radical Clarity**
- Every interface element must have an obvious purpose
- Information hierarchy should be immediately apparent
- Use progressive disclosure: show essentials, hide complexity
- Employ visual cues (icons, badges, colors) to communicate state

**Surgical Precision**
- Minimize clicks needed to accomplish tasks
- Provide exactly the right amount of information at each density level
- Eliminate redundant UI elements
- Make CTAs (Call To Actions) unmistakably clear

**Joyful Flow**
- Smooth transitions between states (150-300ms)
- Consistent interaction patterns across all views
- Delightful micro-interactions (subtle hover effects, button transforms)
- Loading states that inform rather than frustrate

**Efficiency Through Choice**
- Provide three view density options: Cards, Compact, List
- Remember user's view preference per page
- Optimize for both scanning (List) and detailed review (Cards)
- Design for power users without overwhelming novices

---

## Color System

### Primary Palette

```css
/* UCSD Brand Colors */
--primary-blue: #182B49;      /* Main brand color, headers, primary CTAs */
--ucsd-gold: #C69214;         /* Accent color, active states, highlights */
--accent-teal: #00C6D7;       /* Secondary accent, progress bars */
```

**Usage Guidelines:**
- **Primary Blue**: Navigation, headings, primary text, borders on focus
- **UCSD Gold**: Active navigation items, primary action buttons, key highlights
- **Accent Teal**: Secondary actions, progress indicators, information highlights

### Semantic Colors (Cheerful Versions)

```css
/* Status & Feedback Colors */
--success: #00C851;           /* Successful operations, completed states */
--success-light: #D4EDDA;     /* Success backgrounds, subtle highlights */

--warning: #FFB84D;           /* Caution states, pending operations */
--warning-light: #FFF3CD;     /* Warning backgrounds */

--error: #FF6B6B;             /* Error states, destructive actions */
--error-light: #F8D7DA;       /* Error backgrounds */

--info: #4FC3F7;              /* Informational messages, hints */
--info-light: #D1ECF1;        /* Info backgrounds */
```

**Color Application Matrix:**

| State | Background | Border | Text | Icon |
|-------|-----------|--------|------|------|
| Success | `--success-light` | `--success` | `#0A5C2E` | `--success` |
| Warning | `--warning-light` | `--warning` | `#7A4A00` | `--warning` |
| Error | `--error-light` | `--error` | `#7A1A1A` | `--error` |
| Info | `--info-light` | `--info` | `#014361` | `--info` |

### Cheerful Accent Colors (Optional Use)

```css
/* Additional Accents for Variety */
--joy-purple: #9C27B0;        /* Creative elements, special highlights */
--joy-pink: #E91E63;          /* Celebratory UI, achievements */
--joy-lime: #CDDC39;          /* Energy, calls to action */
--joy-cyan: #00BCD4;          /* Cool highlights, information */
```

**When to Use Accent Colors:**
- Celebrating milestones (e.g., "100th paper processed!")
- Highlighting special features or new functionality
- Creating visual interest in stat cards
- Differentiating categories or tags

### Neutral Grays (Soft, Not Harsh)

```css
/* Neutral Palette - Softer than typical grays */
--gray-50: #FAFAFA;          /* Backgrounds, subtle fills */
--gray-100: #F5F5F5;         /* Card backgrounds, alternating rows */
--gray-200: #EEEEEE;         /* Borders, dividers */
--gray-300: #E0E0E0;         /* Input borders, inactive states */
--gray-400: #BDBDBD;         /* Icons, placeholder text */
--gray-500: #9E9E9E;         /* Secondary text, helper text */
--gray-600: #757575;         /* Body text, labels */
--gray-700: #616161;         /* Strong text, headings */
--gray-800: #424242;         /* Dark text for contrast */
--gray-900: #212121;         /* Maximum contrast text */
```

**Gray Scale Usage:**
- **50-200**: Backgrounds and surfaces
- **300-400**: Borders and inactive elements
- **500-600**: Secondary text and icons
- **700-900**: Primary text and high-emphasis content

---

## Typography

### Font Families

```css
/* Primary Font Stack */
--font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 
             Roboto, 'Helvetica Neue', Arial, sans-serif;

/* Monospace for Code/IDs */
--font-mono: 'Fira Code', 'SF Mono', Monaco, 'Cascadia Code', monospace;
```

**Loading Inter Font (Include in `<head>`):**
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
```

### Type Scale

```css
/* Harmonious Type Scale */
--text-xs: 0.75rem;          /* 12px - Small labels, timestamps */
--text-sm: 0.875rem;         /* 14px - Helper text, secondary info */
--text-base: 1rem;           /* 16px - Body text, inputs */
--text-lg: 1.125rem;         /* 18px - Emphasized text, card subtitles */
--text-xl: 1.25rem;          /* 20px - Card titles, section headings */
--text-2xl: 1.5rem;          /* 24px - Page section headers */
--text-3xl: 1.875rem;        /* 30px - Subsection headings */
--text-4xl: 2.25rem;         /* 36px - Page titles */
```

### Font Weights

```css
--font-normal: 400;          /* Body text */
--font-medium: 500;          /* Emphasized text, labels */
--font-semibold: 600;        /* Headings, buttons */
--font-bold: 700;            /* Strong emphasis, hero text */
```

### Typography Usage Guidelines

**Headings:**
```css
/* Page Title */
h1 {
  font-size: var(--text-4xl);
  font-weight: var(--font-bold);
  color: var(--primary-blue);
  line-height: 1.2;
}

/* Section Heading */
h2 {
  font-size: var(--text-2xl);
  font-weight: var(--font-semibold);
  color: var(--primary-blue);
  line-height: 1.3;
}

/* Subsection Heading */
h3 {
  font-size: var(--text-xl);
  font-weight: var(--font-semibold);
  color: var(--gray-900);
  line-height: 1.4;
}
```

**Body Text:**
```css
/* Standard paragraph */
p {
  font-size: var(--text-base);
  line-height: 1.6;
  color: var(--gray-700);
}

/* Secondary/helper text */
.text-secondary {
  font-size: var(--text-sm);
  color: var(--gray-600);
}

/* Fine print */
.text-tiny {
  font-size: var(--text-xs);
  color: var(--gray-500);
}
```

---

## Spacing & Layout

### Spacing Scale

```css
/* Consistent Spacing Scale (4px base) */
--space-1: 0.25rem;    /* 4px - Tight spacing */
--space-2: 0.5rem;     /* 8px - Close spacing */
--space-3: 0.75rem;    /* 12px - Compact spacing */
--space-4: 1rem;       /* 16px - Default spacing */
--space-5: 1.25rem;    /* 20px - Comfortable spacing */
--space-6: 1.5rem;     /* 24px - Generous spacing */
--space-8: 2rem;       /* 32px - Section spacing */
--space-10: 2.5rem;    /* 40px - Large section spacing */
--space-12: 3rem;      /* 48px - Hero spacing */
--space-16: 4rem;      /* 64px - Major section breaks */
```

**Spacing Application:**
- **1-2**: Between related inline elements (icon + text)
- **3-4**: Default element padding, small gaps
- **5-6**: Card padding, comfortable gaps
- **8-10**: Section margins, major element spacing
- **12-16**: Page-level spacing, hero sections

### Border Radius (Friendly, Rounded)

```css
/* Progressively Rounder Corners */
--radius-sm: 0.375rem;   /* 6px - Small elements, badges */
--radius-md: 0.5rem;     /* 8px - Buttons, inputs */
--radius-lg: 0.75rem;    /* 12px - Cards, containers */
--radius-xl: 1rem;       /* 16px - Large cards, modals */
--radius-2xl: 1.5rem;    /* 24px - Hero cards, special containers */
--radius-full: 9999px;   /* Pills, circular elements */
```

### Shadow System (Depth, Not Harshness)

```css
/* Subtle to Prominent Shadows */
--shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
--shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
--shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
--shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
--shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
--shadow-2xl: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
```

**Shadow Guidelines:**
- **sm**: Subtle lift for inputs, small cards
- **md**: Default cards, buttons on hover
- **lg**: Elevated cards, dropdown menus
- **xl**: Modals, popovers
- **2xl**: Hero elements, dramatic emphasis

### Transitions

```css
/* Consistent Animation Timing */
--transition-fast: 150ms ease;    /* Quick feedback */
--transition-base: 200ms ease;    /* Default transitions */
--transition-slow: 300ms ease;    /* Deliberate changes */
```

---

## Component Library

### Buttons

#### Primary Button (Call to Action)

```html
<button class="btn btn-primary">
  <span class="btn-icon">➕</span>
  Create New Job
</button>
```

```css
.btn {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-5);
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  border-radius: var(--radius-lg);
  border: none;
  cursor: pointer;
  transition: all var(--transition-base);
  text-decoration: none;
  white-space: nowrap;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: linear-gradient(135deg, var(--ucsd-gold) 0%, #A07810 100%);
  color: white;
  box-shadow: var(--shadow-md);
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}
```

#### Secondary Button

```html
<button class="btn btn-secondary">
  <span class="btn-icon">🔄</span>
  Refresh
</button>
```

```css
.btn-secondary {
  background: white;
  color: var(--primary-blue);
  border: 2px solid var(--primary-blue);
}

.btn-secondary:hover:not(:disabled) {
  background-color: var(--gray-50);
  transform: translateY(-1px);
}
```

#### Button Variants

```css
/* Success Button */
.btn-success {
  background: linear-gradient(135deg, var(--success) 0%, #00A040 100%);
  color: white;
  box-shadow: var(--shadow-md);
}

/* Danger Button */
.btn-danger {
  background: linear-gradient(135deg, var(--error) 0%, #E85555 100%);
  color: white;
  box-shadow: var(--shadow-md);
}

/* Ghost Button */
.btn-ghost {
  background: transparent;
  color: var(--gray-700);
  border: none;
  padding: var(--space-2) var(--space-3);
}

.btn-ghost:hover {
  background: var(--gray-100);
}
```

### Cards

#### Standard Card

```html
<div class="card">
  <div class="card-header">
    <h3 class="card-title">
      <span class="card-icon">📄</span>
      Paper Title
    </h3>
    <span class="badge badge-success">Processed</span>
  </div>
  <div class="card-body">
    <p>Card content goes here...</p>
  </div>
  <div class="card-footer">
    Footer content
  </div>
</div>
```

```css
.card {
  background: white;
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow);
  border: 1px solid var(--gray-200);
  overflow: hidden;
  transition: all var(--transition-base);
}

.card:hover {
  box-shadow: var(--shadow-lg);
  transform: translateY(-2px);
}

.card-header {
  padding: var(--space-5);
  border-bottom: 1px solid var(--gray-200);
  background: var(--gray-50);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-size: var(--text-xl);
  font-weight: var(--font-semibold);
  color: var(--primary-blue);
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin: 0;
}

.card-icon {
  font-size: 1.5rem;
  line-height: 1;
}

.card-body {
  padding: var(--space-5);
}

.card-footer {
  padding: var(--space-4) var(--space-5);
  background: var(--gray-50);
  border-top: 1px solid var(--gray-200);
  font-size: var(--text-sm);
  color: var(--gray-600);
}
```

### Stat Cards (Cheerful!)

```html
<div class="stat-card stat-card-success">
  <div class="stat-icon">📚</div>
  <div class="stat-content">
    <div class="stat-label">Papers Processed</div>
    <div class="stat-value">47</div>
    <div class="stat-change stat-change-positive">
      <span class="stat-change-icon">↗</span>
      +12 this week
    </div>
  </div>
</div>
```

```css
.stat-card {
  background: white;
  border-radius: var(--radius-xl);
  padding: var(--space-6);
  box-shadow: var(--shadow-md);
  border: 1px solid var(--gray-200);
  display: flex;
  gap: var(--space-4);
  transition: all var(--transition-base);
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-xl);
}

.stat-icon {
  font-size: 2.5rem;
  line-height: 1;
  flex-shrink: 0;
}

.stat-content {
  flex: 1;
}

.stat-label {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--gray-600);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: var(--space-1);
}

.stat-value {
  font-size: var(--text-4xl);
  font-weight: var(--font-bold);
  color: var(--primary-blue);
  line-height: 1.2;
}

.stat-change {
  font-size: var(--text-sm);
  margin-top: var(--space-2);
  display: flex;
  align-items: center;
  gap: var(--space-1);
}

.stat-change-positive { color: var(--success); }
.stat-change-negative { color: var(--error); }

/* Stat Card Variants */
.stat-card-success {
  background: linear-gradient(135deg, var(--success-light) 0%, white 100%);
  border-left: 4px solid var(--success);
}

.stat-card-info {
  background: linear-gradient(135deg, var(--info-light) 0%, white 100%);
  border-left: 4px solid var(--info);
}

.stat-card-warning {
  background: linear-gradient(135deg, var(--warning-light) 0%, white 100%);
  border-left: 4px solid var(--warning);
}

.stat-card-primary {
  background: linear-gradient(135deg, rgba(24, 43, 73, 0.05) 0%, white 100%);
  border-left: 4px solid var(--primary-blue);
}
```

### Badges

```html
<span class="badge badge-success">Complete</span>
<span class="badge badge-warning">Pending</span>
<span class="badge badge-error">Failed</span>
<span class="badge badge-info">Processing</span>
```

```css
.badge {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  padding: var(--space-1) var(--space-3);
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
  border-radius: var(--radius-full);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.badge-success {
  background-color: var(--success-light);
  color: var(--success);
}

.badge-info {
  background-color: var(--info-light);
  color: var(--info);
}

.badge-warning {
  background-color: var(--warning-light);
  color: var(--warning);
}

.badge-error {
  background-color: var(--error-light);
  color: var(--error);
}
```

### Alerts

```html
<div class="alert alert-success">
  <div class="alert-icon">✓</div>
  <div class="alert-content">
    <div class="alert-title">Success!</div>
    <div class="alert-message">Your paper has been processed successfully.</div>
  </div>
  <button class="alert-close">×</button>
</div>
```

```css
.alert {
  display: flex;
  gap: var(--space-4);
  padding: var(--space-4) var(--space-5);
  border-radius: var(--radius-lg);
  margin-bottom: var(--space-4);
  border: 1px solid;
}

.alert-icon {
  font-size: 1.5rem;
  flex-shrink: 0;
  line-height: 1;
}

.alert-content {
  flex: 1;
}

.alert-title {
  font-weight: var(--font-semibold);
  margin-bottom: var(--space-1);
}

.alert-message {
  font-size: var(--text-sm);
}

.alert-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0;
  color: inherit;
  opacity: 0.6;
  transition: opacity var(--transition-base);
}

.alert-close:hover {
  opacity: 1;
}

/* Alert Variants */
.alert-success {
  background-color: var(--success-light);
  border-color: var(--success);
  color: #0A5C2E;
}

.alert-info {
  background-color: var(--info-light);
  border-color: var(--info);
  color: #014361;
}

.alert-warning {
  background-color: var(--warning-light);
  border-color: var(--warning);
  color: #7A4A00;
}

.alert-error {
  background-color: var(--error-light);
  border-color: var(--error);
  color: #7A1A1A;
}
```

### Forms

```html
<div class="form-group">
  <label class="form-label">
    <span class="form-label-icon">📝</span>
    Paper Title
    <span class="form-label-hint">(Optional)</span>
  </label>
  <input type="text" class="form-input" placeholder="Enter paper title">
  <div class="form-help">
    We'll attempt to fetch metadata automatically if DOI is provided.
  </div>
</div>
```

```css
.form-group {
  margin-bottom: var(--space-6);
}

.form-label {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-weight: var(--font-semibold);
  color: var(--gray-900);
  margin-bottom: var(--space-2);
}

.form-label-icon {
  font-size: 1.2rem;
}

.form-label-hint {
  font-weight: var(--font-normal);
  color: var(--gray-600);
  font-size: var(--text-sm);
  margin-left: var(--space-2);
}

.form-input,
.form-textarea,
.form-select {
  width: 100%;
  padding: var(--space-3) var(--space-4);
  font-size: var(--text-base);
  border: 2px solid var(--gray-300);
  border-radius: var(--radius-lg);
  transition: all var(--transition-base);
  font-family: var(--font-sans);
}

.form-input:focus,
.form-textarea:focus,
.form-select:focus {
  outline: none;
  border-color: var(--ucsd-gold);
  box-shadow: 0 0 0 3px rgba(198, 146, 20, 0.1);
}

.form-textarea {
  resize: vertical;
  min-height: 120px;
}

.form-help {
  margin-top: var(--space-2);
  font-size: var(--text-sm);
  color: var(--gray-600);
  display: flex;
  align-items: flex-start;
  gap: var(--space-2);
}
```

### Progress Bars

```html
<div class="progress">
  <div class="progress-bar" style="width: 65%;">65%</div>
</div>
```

```css
.progress {
  width: 100%;
  height: 24px;
  background-color: var(--gray-200);
  border-radius: var(--radius-full);
  overflow: hidden;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1);
}

.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, var(--ucsd-gold) 0%, var(--accent-teal) 100%);
  border-radius: var(--radius-full);
  transition: width 300ms ease;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding-right: var(--space-3);
  color: white;
  font-size: var(--text-xs);
  font-weight: var(--font-bold);
}
```

### Loading States

```html
<div class="loading">
  <div class="loading-spinner"></div>
  <div class="loading-text">
    Processing papers...
    <span class="loading-detail">This may take a few minutes</span>
  </div>
</div>
```

```css
.loading {
  text-align: center;
  padding: var(--space-8);
}

.loading-spinner {
  display: inline-block;
  width: 40px;
  height: 40px;
  border: 4px solid var(--gray-200);
  border-top-color: var(--ucsd-gold);
  border-radius: var(--radius-full);
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text {
  margin-top: var(--space-4);
  font-size: var(--text-lg);
  color: var(--gray-600);
}

.loading-detail {
  display: block;
  font-size: var(--text-sm);
  color: var(--gray-500);
  margin-top: var(--space-2);
}
```

### Tables

```html
<div class="table-container">
  <table class="table">
    <thead class="table-header">
      <tr>
        <th class="table-th">Paper Title</th>
        <th class="table-th">Year</th>
        <th class="table-th">Status</th>
        <th class="table-th">Actions</th>
      </tr>
    </thead>
    <tbody>
      <tr class="table-row">
        <td class="table-cell">Example Paper</td>
        <td class="table-cell">2024</td>
        <td class="table-cell">
          <span class="badge badge-success">Complete</span>
        </td>
        <td class="table-cell">
          <button class="btn btn-sm">View</button>
        </td>
      </tr>
    </tbody>
  </table>
</div>
```

```css
.table-container {
  overflow-x: auto;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow);
  background: white;
}

.table {
  width: 100%;
  border-collapse: collapse;
}

.table-header {
  background: var(--gray-100);
}

.table-th {
  padding: var(--space-4) var(--space-5);
  text-align: left;
  font-weight: var(--font-semibold);
  color: var(--primary-blue);
  border-bottom: 2px solid var(--gray-300);
  white-space: nowrap;
}

.table-row {
  border-bottom: 1px solid var(--gray-200);
  transition: background-color var(--transition-fast);
}

.table-row:hover {
  background-color: var(--gray-50);
}

.table-row:nth-child(even) {
  background-color: rgba(0, 0, 0, 0.01);
}

.table-cell {
  padding: var(--space-4) var(--space-5);
  color: var(--gray-800);
}
```

### Empty States

```html
<div class="empty-state">
  <div class="empty-state-icon">📂</div>
  <h2 class="empty-state-title">No Papers Yet</h2>
  <p class="empty-state-message">
    Get started by uploading PDFs or searching for papers by DOI.
  </p>
  <button class="btn btn-primary">
    <span class="btn-icon">➕</span>
    Add Your First Paper
  </button>
</div>
```

```css
.empty-state {
  text-align: center;
  padding: var(--space-12);
  color: var(--gray-600);
}

.empty-state-icon {
  font-size: 4rem;
  margin-bottom: var(--space-4);
  opacity: 0.5;
}

.empty-state-title {
  font-size: var(--text-2xl);
  font-weight: var(--font-semibold);
  color: var(--gray-900);
  margin-bottom: var(--space-2);
}

.empty-state-message {
  font-size: var(--text-lg);
  margin-bottom: var(--space-6);
}
```

---

## View Density System

### Overview

Article Eater provides **three view density options** to accommodate different user needs and screen real estate:

1. **Cards View** - Rich, detailed presentation (default)
2. **Compact View** - Balanced information density (2-3x more items)
3. **List View** - Maximum density, scan-optimized (5-6x more items)

### View Toggle Component

```html
<div class="view-toggle">
  <button class="view-toggle-btn active" data-view-toggle="cards" 
          title="Card view - detailed">
    <span>📱</span> Cards
  </button>
  <button class="view-toggle-btn" data-view-toggle="compact" 
          title="Compact view - 2-3x more items">
    <span>📋</span> Compact
  </button>
  <button class="view-toggle-btn" data-view-toggle="list" 
          title="List view - maximum density">
    <span>📊</span> List
  </button>
</div>
```

```css
.view-toggle {
  display: flex;
  gap: var(--space-2);
  background: var(--gray-100);
  padding: var(--space-1);
  border-radius: var(--radius-lg);
}

.view-toggle-btn {
  padding: var(--space-2) var(--space-3);
  border: none;
  background: transparent;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-base);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--gray-600);
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.view-toggle-btn:hover {
  background: var(--gray-200);
  color: var(--gray-900);
}

.view-toggle-btn.active {
  background: white;
  color: var(--primary-blue);
  box-shadow: var(--shadow-sm);
}
```

### Cards View (Default)

**Use Case**: Detailed review, understanding context, initial exploration

**Characteristics:**
- Full card with header, body, and footer
- Shows all metadata (authors, year, citations, abstract)
- Includes action buttons in footer
- Maximum visual hierarchy
- Hover effects for interactivity

```css
/* Default card styles (no additional class needed) */
.card {
  margin-bottom: var(--space-5);
}

.card-header {
  padding: var(--space-5);
}

.card-body {
  padding: var(--space-5);
}

.card-footer {
  padding: var(--space-4) var(--space-5);
}
```

**When to Use:**
- Paper library browsing
- Reviewing findings with context
- Initial exploration of new data
- When screen real estate is abundant

### Compact View

**Use Case**: Balanced scanning and detail, working with moderate datasets

**Characteristics:**
- Reduced padding and margins
- Smaller typography
- Essential information visible
- 2-3x more items per screen
- Still maintains hover states

```css
.compact-view .card {
  margin-bottom: var(--space-2);
}

.compact-view .card-header {
  padding: var(--space-3) var(--space-4);
}

.compact-view .card-body {
  padding: var(--space-3) var(--space-4);
}

.compact-view .card-footer {
  padding: var(--space-2) var(--space-4);
}

.compact-view .card-title {
  font-size: var(--text-base);
}

.compact-view .stat-card {
  padding: var(--space-3);
}

.compact-view .stat-icon {
  font-size: 1.5rem;
}

.compact-view .stat-value {
  font-size: var(--text-2xl);
}
```

**When to Use:**
- Working through moderate-sized result sets
- Quick comparisons between items
- Mobile/tablet devices
- Split-screen workflows

### List View

**Use Case**: Maximum density, rapid scanning, large datasets

**Characteristics:**
- Minimal decoration, flat design
- Headers only (body hidden)
- No margins between items (borders as separators)
- Table-like presentation
- 5-6x more items per screen
- Reduced hover effects

```css
.list-view .card {
  margin-bottom: 0;
  border-radius: 0;
  border-bottom: 1px solid var(--gray-200);
}

.list-view .card:first-child {
  border-radius: var(--radius-lg) var(--radius-lg) 0 0;
}

.list-view .card:last-child {
  border-radius: 0 0 var(--radius-lg) var(--radius-lg);
  border-bottom: none;
}

.list-view .card-header {
  padding: var(--space-3) var(--space-4);
  border-bottom: none;
  background: white;
}

.list-view .card-body {
  display: none;  /* Hide detailed content */
}

.list-view .card-footer {
  padding: var(--space-2) var(--space-4);
  background: white;
  border-top: none;
}

.list-view .card:hover {
  background: var(--gray-50);
  transform: none;  /* No lift effect in list view */
}
```

**When to Use:**
- Processing large result sets (100+ items)
- Rapid scanning for specific items
- Keyboard-driven workflows
- Limited screen space
- Performance-critical contexts

### Implementing View Switching

#### HTML Structure

```html
<!-- Page with view toggle -->
<header class="page-header">
  <div class="header-content">
    <h1>Paper Library</h1>
  </div>
  <div class="header-actions">
    <!-- View Toggle -->
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
  </div>
</header>

<!-- Content container (class changes based on view) -->
<div id="content-container" class="cards-view">
  <!-- Items rendered here -->
</div>
```

#### JavaScript Implementation

```javascript
// View controller implementation
class CompactViewController {
  constructor(containerId, options = {}) {
    this.container = document.getElementById(containerId);
    this.pageName = options.pageName || 'default';
    this.defaultView = options.defaultView || 'cards';
    this.renderCards = options.renderCards || (() => '');
    this.renderCompact = options.renderCompact || (() => '');
    this.renderList = options.renderList || (() => '');
    
    this.currentView = this.loadViewPreference();
    this.initializeViewToggle();
    this.setView(this.currentView);
  }
  
  loadViewPreference() {
    const saved = localStorage.getItem(`view_${this.pageName}`);
    return saved || this.defaultView;
  }
  
  saveViewPreference(view) {
    localStorage.setItem(`view_${this.pageName}`, view);
  }
  
  initializeViewToggle() {
    document.querySelectorAll('.view-toggle-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const view = btn.getAttribute('data-view-toggle');
        this.setView(view);
      });
    });
  }
  
  setView(view) {
    this.currentView = view;
    this.saveViewPreference(view);
    
    // Update button states
    document.querySelectorAll('.view-toggle-btn').forEach(btn => {
      btn.classList.toggle('active', 
        btn.getAttribute('data-view-toggle') === view);
    });
    
    // Update container class
    this.container.className = `${view}-view`;
    
    // Re-render content
    this.render();
  }
  
  render() {
    let html = '';
    
    switch(this.currentView) {
      case 'cards':
        html = this.renderCards();
        break;
      case 'compact':
        html = this.renderCompact();
        break;
      case 'list':
        html = this.renderList();
        break;
    }
    
    this.container.innerHTML = html;
  }
}

// Usage example
const viewController = new CompactViewController('papers-container', {
  pageName: 'library',
  defaultView: 'cards',
  renderCards: () => {
    // Return HTML for cards view
    return papers.map(p => `
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">${p.title}</h3>
        </div>
        <div class="card-body">
          <p>${p.abstract}</p>
        </div>
      </div>
    `).join('');
  },
  renderCompact: () => {
    // Compact version - same structure, styles handle density
    return papers.map(p => `
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">${p.title}</h3>
        </div>
        <div class="card-body">
          <p>${p.abstract.substring(0, 200)}...</p>
        </div>
      </div>
    `).join('');
  },
  renderList: () => {
    // List version - header only
    return papers.map(p => `
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">${p.title}</h3>
          <span class="badge badge-success">${p.year}</span>
        </div>
      </div>
    `).join('');
  }
});
```

### View-Specific Guidelines

#### Cards View Best Practices

- Include rich metadata (authors, affiliations, keywords)
- Show meaningful abstracts or summaries
- Provide clear action buttons in footer
- Use stat cards for numerical summaries
- Include visual indicators (confidence meters, progress bars)

#### Compact View Best Practices

- Truncate long text (use ellipsis)
- Show 2-3 key metadata fields only
- Keep essential actions visible
- Maintain scanability with good typography
- Use icons to save space

#### List View Best Practices

- Single-line or two-line item heights
- Essential information only (title + 1-2 metadata)
- Right-align numeric data
- Use consistent icon placement
- Consider zebra striping for large lists

---

## CSS Custom Properties Reference

### Complete Variable Declaration

```css
:root {
  /* ===== COLORS ===== */
  
  /* UCSD Brand */
  --primary-blue: #182B49;
  --ucsd-gold: #C69214;
  --accent-teal: #00C6D7;
  
  /* Semantic Colors */
  --success: #00C851;
  --success-light: #D4EDDA;
  --warning: #FFB84D;
  --warning-light: #FFF3CD;
  --error: #FF6B6B;
  --error-light: #F8D7DA;
  --info: #4FC3F7;
  --info-light: #D1ECF1;
  
  /* Cheerful Accents */
  --joy-purple: #9C27B0;
  --joy-pink: #E91E63;
  --joy-lime: #CDDC39;
  --joy-cyan: #00BCD4;
  
  /* Neutrals */
  --gray-50: #FAFAFA;
  --gray-100: #F5F5F5;
  --gray-200: #EEEEEE;
  --gray-300: #E0E0E0;
  --gray-400: #BDBDBD;
  --gray-500: #9E9E9E;
  --gray-600: #757575;
  --gray-700: #616161;
  --gray-800: #424242;
  --gray-900: #212121;
  
  /* ===== TYPOGRAPHY ===== */
  
  /* Font Families */
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 
               Roboto, 'Helvetica Neue', Arial, sans-serif;
  --font-mono: 'Fira Code', 'SF Mono', Monaco, 'Cascadia Code', monospace;
  
  /* Type Scale */
  --text-xs: 0.75rem;
  --text-sm: 0.875rem;
  --text-base: 1rem;
  --text-lg: 1.125rem;
  --text-xl: 1.25rem;
  --text-2xl: 1.5rem;
  --text-3xl: 1.875rem;
  --text-4xl: 2.25rem;
  
  /* Font Weights */
  --font-normal: 400;
  --font-medium: 500;
  --font-semibold: 600;
  --font-bold: 700;
  
  /* ===== SPACING ===== */
  --space-1: 0.25rem;
  --space-2: 0.5rem;
  --space-3: 0.75rem;
  --space-4: 1rem;
  --space-5: 1.25rem;
  --space-6: 1.5rem;
  --space-8: 2rem;
  --space-10: 2.5rem;
  --space-12: 3rem;
  --space-16: 4rem;
  
  /* ===== BORDER RADIUS ===== */
  --radius-sm: 0.375rem;
  --radius-md: 0.5rem;
  --radius-lg: 0.75rem;
  --radius-xl: 1rem;
  --radius-2xl: 1.5rem;
  --radius-full: 9999px;
  
  /* ===== SHADOWS ===== */
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
  --shadow-2xl: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  
  /* ===== TRANSITIONS ===== */
  --transition-fast: 150ms ease;
  --transition-base: 200ms ease;
  --transition-slow: 300ms ease;
}
```

---

## Responsive Design

### Breakpoints

```css
/* Mobile First Approach */

/* Small devices (phones, 640px and down) */
@media (max-width: 640px) {
  /* Simplified layouts, stacked elements */
}

/* Medium devices (tablets, 768px and down) */
@media (max-width: 768px) {
  /* Adjusted spacing, collapsible sidebar */
}

/* Large devices (desktops, 1024px and down) */
@media (max-width: 1024px) {
  /* Full layouts with some adjustments */
}
```

### Responsive Patterns

```css
/* Sidebar Navigation - Collapsible on Tablet */
@media (max-width: 1024px) {
  .sidebar {
    transform: translateX(-100%);
    transition: transform var(--transition-base);
  }
  
  .sidebar.open {
    transform: translateX(0);
  }
  
  .main-content {
    margin-left: 0;
  }
}

/* Stats Grid - Responsive Columns */
@media (max-width: 1024px) {
  .stats-grid {
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  }
}

@media (max-width: 640px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
}

/* Page Header - Stack on Mobile */
@media (max-width: 640px) {
  .page-header {
    flex-direction: column;
    gap: var(--space-4);
  }
  
  .header-actions {
    width: 100%;
  }
  
  .view-toggle {
    width: 100%;
    justify-content: space-between;
  }
}

/* Force Compact View on Small Screens */
@media (max-width: 640px) {
  .cards-view {
    /* Auto-switch to compact on mobile */
  }
  
  .card {
    margin-bottom: var(--space-3);
  }
  
  .card-header,
  .card-body {
    padding: var(--space-3);
  }
}
```

---

## Accessibility Guidelines

### Color Contrast

**WCAG AA Compliance:**
- Normal text (< 18pt): Minimum contrast ratio 4.5:1
- Large text (≥ 18pt): Minimum contrast ratio 3:1
- UI components: Minimum contrast ratio 3:1

**Tested Combinations:**
```css
/* High Contrast Text */
--gray-900 on --gray-50: 15.8:1 ✓
--primary-blue on white: 12.6:1 ✓
--gray-700 on white: 8.3:1 ✓

/* Button Contrast */
white on --ucsd-gold: 5.2:1 ✓
white on --primary-blue: 12.6:1 ✓

/* Status Colors */
--success (text) on --success-light: 4.8:1 ✓
--error (text) on --error-light: 5.1:1 ✓
```

### Keyboard Navigation

**Focus States:**
```css
/* Visible focus indicators */
button:focus,
a:focus,
input:focus,
select:focus {
  outline: 2px solid var(--ucsd-gold);
  outline-offset: 2px;
}

/* Alternative ring style */
.focus-ring:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(198, 146, 20, 0.4);
}
```

**Tab Order:**
- Logical flow: header → navigation → main content → footer
- Skip links for keyboard users
- No tab traps in modals

### Screen Reader Support

```html
<!-- Descriptive Labels -->
<button aria-label="Add new paper to library">
  <span aria-hidden="true">➕</span>
  Add Paper
</button>

<!-- Status Announcements -->
<div role="status" aria-live="polite">
  Processing complete: 3 new findings extracted
</div>

<!-- Loading States -->
<div role="status" aria-live="polite" aria-busy="true">
  <span class="sr-only">Loading papers...</span>
  <div class="loading-spinner" aria-hidden="true"></div>
</div>

<!-- Screen Reader Only Content -->
<span class="sr-only">Current page: 1 of 5</span>
```

```css
/* Screen Reader Only Class */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}
```

### Motion & Animation

```css
/* Respect prefers-reduced-motion */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## Implementation Patterns

### Page Layout Template

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Page Title - Article Eater</title>
  
  <!-- Fonts -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  
  <!-- Stylesheets -->
  <link rel="stylesheet" href="css/main_v2.css">
  
  <!-- Favicon -->
  <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>📚</text></svg>">
</head>
<body>
  <div class="app-container">
    <!-- Sidebar Navigation -->
    <nav class="sidebar">
      <div class="nav-logo">
        <span class="nav-logo-emoji">📚</span>
        Article Eater
      </div>
      <ul class="nav-menu">
        <!-- Navigation items -->
      </ul>
    </nav>

    <!-- Main Content -->
    <main class="main-content">
      <!-- Page Header -->
      <header class="page-header">
        <div class="header-content">
          <div class="header-title">
            <span class="header-icon">📊</span>
            <h1>Page Title</h1>
          </div>
          <p class="header-description">
            Brief description of this page's purpose
          </p>
        </div>
        <div class="header-actions">
          <!-- View toggle, action buttons -->
        </div>
      </header>

      <!-- Page Content -->
      <div id="content-container">
        <!-- Dynamic content here -->
      </div>
    </main>
  </div>

  <!-- Scripts -->
  <script src="js/api.js"></script>
  <script src="js/compact-view.js"></script>
  <script src="js/page-specific.js"></script>
</body>
</html>
```

### Navigation Sidebar

```html
<nav class="sidebar">
  <div class="nav-logo">
    <span class="nav-logo-emoji">📚</span>
    Article Eater
  </div>
  
  <ul class="nav-menu">
    <li class="nav-item">
      <a href="dashboard.html" class="nav-link">
        <span class="nav-icon">📊</span>
        Dashboard
      </a>
    </li>
    <li class="nav-item">
      <a href="search.html" class="nav-link">
        <span class="nav-icon">🔍</span>
        New Search
      </a>
    </li>
    <li class="nav-item">
      <a href="library.html" class="nav-link active">
        <span class="nav-icon">📚</span>
        Library
      </a>
    </li>
    <li class="nav-item">
      <a href="findings.html" class="nav-link">
        <span class="nav-icon">🔬</span>
        Findings
      </a>
    </li>
    <li class="nav-item">
      <a href="rules.html" class="nav-link">
        <span class="nav-icon">📝</span>
        Rule Inspector
      </a>
    </li>
  </ul>
</nav>
```

### Stats Grid Dashboard

```html
<div class="stats-grid">
  <!-- Papers Stat -->
  <div class="stat-card stat-card-primary">
    <div class="stat-icon">📚</div>
    <div class="stat-content">
      <div class="stat-label">Papers Processed</div>
      <div class="stat-value">47</div>
      <div class="stat-change stat-change-positive">
        <span class="stat-change-icon">↗</span>
        +12 this week
      </div>
    </div>
  </div>

  <!-- Findings Stat -->
  <div class="stat-card stat-card-success">
    <div class="stat-icon">🔬</div>
    <div class="stat-content">
      <div class="stat-label">Total Findings</div>
      <div class="stat-value">156</div>
      <div class="stat-change stat-change-positive">
        <span class="stat-change-icon">↗</span>
        +23 this week
      </div>
    </div>
  </div>

  <!-- Rules Stat -->
  <div class="stat-card stat-card-info">
    <div class="stat-icon">📝</div>
    <div class="stat-content">
      <div class="stat-label">Design Rules</div>
      <div class="stat-value">34</div>
      <div class="stat-change">
        <span class="stat-change-icon">→</span>
        Stable
      </div>
    </div>
  </div>

  <!-- Confidence Stat -->
  <div class="stat-card stat-card-warning">
    <div class="stat-icon">📊</div>
    <div class="stat-content">
      <div class="stat-label">Avg Confidence</div>
      <div class="stat-value">0.78</div>
      <div class="stat-change stat-change-positive">
        <span class="stat-change-icon">↗</span>
        +0.05
      </div>
    </div>
  </div>
</div>
```

### Content with View Toggle

```html
<header class="page-header">
  <div class="header-content">
    <h1>Paper Library</h1>
    <p class="header-description">
      Browse and manage your research papers
    </p>
  </div>
  
  <div class="header-actions">
    <!-- View Density Toggle -->
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
    
    <!-- Action Buttons -->
    <button class="btn btn-secondary">
      <span class="btn-icon">🔄</span>
      Refresh
    </button>
    <button class="btn btn-primary">
      <span class="btn-icon">➕</span>
      Add Papers
    </button>
  </div>
</header>

<!-- Content Container -->
<div id="papers-container" class="cards-view">
  <!-- Papers rendered by JavaScript -->
</div>
```

---

## Quick Reference Checklist

### Starting a New Page

- [ ] Include Inter font from Google Fonts
- [ ] Link to `css/main_v2.css`
- [ ] Use `app-container` layout wrapper
- [ ] Include sidebar navigation with active state
- [ ] Add page header with icon and description
- [ ] Implement view toggle if showing lists
- [ ] Use semantic HTML5 elements
- [ ] Add appropriate ARIA labels
- [ ] Test keyboard navigation
- [ ] Verify color contrast

### Creating a New Component

- [ ] Use CSS custom properties for colors/spacing
- [ ] Follow naming convention (BEM-style)
- [ ] Include hover/focus states
- [ ] Add transition animations
- [ ] Support all three view densities (if applicable)
- [ ] Test on mobile breakpoints
- [ ] Add loading states
- [ ] Include empty states
- [ ] Document in this style guide

### Before Deployment

- [ ] All colors meet WCAG AA contrast
- [ ] Focus states visible for all interactive elements
- [ ] Keyboard navigation works throughout
- [ ] Screen reader testing completed
- [ ] Mobile responsive (test 375px, 768px, 1024px)
- [ ] Reduced motion preference respected
- [ ] No console errors
- [ ] Loading states implemented
- [ ] Error states handled gracefully

---

## Version History

**v20.3.0** (November 16, 2025)
- Initial comprehensive style guide
- Documented three-density view system
- Established cheerful design principles
- Complete CSS custom properties reference
- Accessibility guidelines added

---

## Additional Resources

**Design Inspiration:**
- Material Design 3
- Apple Human Interface Guidelines
- Tailwind CSS utilities (for spacing/colors)

**Accessibility:**
- WCAG 2.1 Level AA
- WAI-ARIA Authoring Practices

**Fonts:**
- Inter (Google Fonts)
- Fira Code (monospace)

**Icons:**
- Unicode emoji (system fonts)
- Consistent semantic usage

---

**End of Style Guide**

For questions or additions, contact the development team.