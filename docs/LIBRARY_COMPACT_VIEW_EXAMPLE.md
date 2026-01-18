# Library.html with Compact View - Implementation Example

This shows how to add compact view to library.html. Apply this pattern to other GUIs.

## Key Changes

### 1. Add View Toggle to Header

```html
<header class="page-header">
  <div class="header-content">
    <div class="header-title">
      <span class="header-icon">📚</span>
      <h1>Library</h1>
    </div>
    <p class="header-description">
      <span id="total-papers">42</span> papers in your collection
    </p>
  </div>
  <div class="header-actions">
    <!-- NEW: View Density Toggle -->
    <div class="view-toggle">
      <button class="view-toggle-btn active" data-view-toggle="cards" title="Card view - detailed">
        <span>📱</span> Cards
      </button>
      <button class="view-toggle-btn" data-view-toggle="compact" title="Compact view - 2-3x more items">
        <span>📋</span> Compact
      </button>
      <button class="view-toggle-btn" data-view-toggle="list" title="List view - maximum density">
        <span>📊</span> List
      </button>
    </div>
    
    <button class="btn btn-secondary" onclick="refreshLibrary()">
      <span class="btn-icon">🔄</span>
      Refresh
    </button>
    <a href="search.html" class="btn btn-primary">
      <span class="btn-icon">➕</span>
      Add Papers
    </a>
  </div>
</header>
```

### 2. Wrap Content in View Container

```html
<!-- Items container with view class -->
<div id="papers-container" class="cards-view">
  <!-- Papers will be rendered here based on current view -->
</div>
```

### 3. Add JavaScript Implementation

```javascript
<script src="js/compact-view.js"></script>
<script>
let allPapers = [];
let viewController;

// Initialize on page load
window.addEventListener('DOMContentLoaded', () => {
  // Create view controller
  viewController = new CompactViewController('papers-container', {
    pageName: 'library',
    defaultView: 'cards',
    renderCards: renderPapersCards,
    renderCompact: renderPapersCompact,
    renderList: renderPapersList
  });
  
  // Load data
  loadPapers();
});

async function loadPapers() {
  // In production: fetch from API
  allPapers = generateMockPapers();
  viewController.render();
}

// Card View (Default - Detailed)
function renderPapersCards() {
  return allPapers.map(paper => `
    <div class="card" style="margin-bottom: var(--space-5);">
      <div class="card-header">
        <h3 class="card-title">
          <span class="card-icon">📄</span>
          ${paper.title}
        </h3>
        <div style="display: flex; gap: var(--space-2);">
          <span class="badge badge-${paper.processed ? 'success' : 'warning'}">
            ${paper.processed ? 'Processed' : 'Pending'}
          </span>
        </div>
      </div>
      <div class="card-body">
        <p style="margin-bottom: var(--space-3); color: var(--gray-700);">
          ${paper.abstract || 'No abstract available'}
        </p>
        <div style="display: flex; gap: var(--space-4); flex-wrap: wrap; font-size: var(--text-sm); color: var(--gray-600);">
          <span>👤 ${paper.authors}</span>
          <span>📅 ${paper.year}</span>
          <span>📊 ${paper.citations} citations</span>
          <span>🔬 ${paper.findings || 0} findings</span>
        </div>
      </div>
      <div class="card-footer">
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <div style="font-size: var(--text-sm); color: var(--gray-600);">
            DOI: ${paper.doi || 'N/A'}
          </div>
          <div style="display: flex; gap: var(--space-2);">
            <button class="btn btn-secondary" onclick="viewPaper('${paper.id}')">
              <span class="btn-icon">👁️</span>
              View
            </button>
            <button class="btn btn-primary" onclick="processPaper('${paper.id}')">
              <span class="btn-icon">⚡</span>
              ${paper.processed ? 'Re-process' : 'Process'}
            </button>
          </div>
        </div>
      </div>
    </div>
  `).join('');
}

// Compact View (2-3x more items)
function renderPapersCompact() {
  return allPapers.map(paper => `
    <div class="card" style="margin-bottom: var(--space-2);">
      <div class="card-header" style="padding: var(--space-3) var(--space-4);">
        <div style="flex: 1;">
          <h3 class="card-title" style="font-size: var(--text-base); margin-bottom: var(--space-1);">
            📄 ${paper.title}
          </h3>
          <div style="font-size: var(--text-sm); color: var(--gray-600);">
            ${paper.authors} • ${paper.year} • ${paper.citations} cites • ${paper.findings || 0} findings
          </div>
        </div>
        <div style="display: flex; gap: var(--space-2); align-items: center;">
          <span class="badge badge-${paper.processed ? 'success' : 'warning'}" style="font-size: var(--text-xs);">
            ${paper.processed ? '✓' : '⏳'}
          </span>
          <button class="btn btn-secondary" onclick="viewPaper('${paper.id}')" 
                  style="padding: var(--space-2) var(--space-3); font-size: var(--text-sm);">
            View
          </button>
          <button class="btn btn-primary" onclick="processPaper('${paper.id}')"
                  style="padding: var(--space-2) var(--space-3); font-size: var(--text-sm);">
            ${paper.processed ? 'Re-process' : 'Process'}
          </button>
        </div>
      </div>
    </div>
  `).join('');
}

// List View (5-6x more items - table format)
function renderPapersList() {
  return `
    <div class="table-container">
      <table class="table compact-table">
        <thead class="table-header">
          <tr>
            <th class="table-th" style="width: 40%;">Title</th>
            <th class="table-th" style="width: 20%;">Authors</th>
            <th class="table-th" style="width: 8%;">Year</th>
            <th class="table-th" style="width: 8%;">Cites</th>
            <th class="table-th" style="width: 10%;">Status</th>
            <th class="table-th" style="width: 14%;">Actions</th>
          </tr>
        </thead>
        <tbody class="table-body">
          ${allPapers.map(paper => `
            <tr class="table-row">
              <td class="table-cell">
                <strong>${paper.title}</strong>
              </td>
              <td class="table-cell">${paper.authors}</td>
              <td class="table-cell">${paper.year}</td>
              <td class="table-cell">${paper.citations}</td>
              <td class="table-cell">
                <span class="badge badge-${paper.processed ? 'success' : 'warning'}" 
                      style="font-size: var(--text-xs); padding: var(--space-1) var(--space-2);">
                  ${paper.processed ? 'Processed' : 'Pending'}
                </span>
              </td>
              <td class="table-cell">
                <div style="display: flex; gap: var(--space-1);">
                  <button class="btn btn-secondary" onclick="viewPaper('${paper.id}')"
                          style="padding: var(--space-1) var(--space-2); font-size: var(--text-xs);">
                    View
                  </button>
                  <button class="btn btn-primary" onclick="processPaper('${paper.id}')"
                          style="padding: var(--space-1) var(--space-2); font-size: var(--text-xs);">
                    Process
                  </button>
                </div>
              </td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    </div>
  `;
}

// Mock data generator
function generateMockPapers() {
  return [
    {
      id: 'paper-001',
      title: 'Effects of Natural Light on Workplace Productivity',
      authors: 'Smith et al.',
      year: 2023,
      citations: 42,
      doi: '10.1234/example.001',
      processed: true,
      findings: 12,
      abstract: 'This study examines the impact of natural lighting conditions on employee productivity in office environments.'
    },
    {
      id: 'paper-002',
      title: 'Biophilic Design in Modern Office Spaces',
      authors: 'Jones & Brown',
      year: 2022,
      citations: 18,
      doi: '10.1234/example.002',
      processed: true,
      findings: 8,
      abstract: 'An investigation into how natural elements integrated into office design affect worker wellbeing and performance.'
    },
    {
      id: 'paper-003',
      title: 'Indoor Air Quality and Cognitive Performance',
      authors: 'Davis',
      year: 2024,
      citations: 7,
      doi: '10.1234/example.003',
      processed: false,
      findings: 0,
      abstract: 'Research on the relationship between indoor air quality metrics and cognitive task performance.'
    },
    // ... more papers
  ];
}

function viewPaper(paperId) {
  alert(`Opening paper: ${paperId}`);
}

function processPaper(paperId) {
  alert(`Processing paper: ${paperId}`);
}

function refreshLibrary() {
  loadPapers();
}
</script>
```

## Visual Comparison

### Cards View (Current)
- Height per item: ~200px
- Items in 1000px: ~5 papers
- Info shown: Full abstract, all metadata, large buttons

### Compact View (NEW)
- Height per item: ~65px
- Items in 1000px: ~15 papers  
- Info shown: Title, key metadata, small buttons
- **3x more items visible**

### List View (NEW)
- Height per item: ~35px
- Items in 1000px: ~28 papers
- Info shown: Essential data only, tiny buttons
- **5-6x more items visible**

## Mobile Responsiveness

```javascript
// Auto-switch to compact on mobile
if (window.innerWidth < 768 && viewController.getCurrentView() === 'cards') {
  viewController.setView('compact');
}

// Listen for resize
window.addEventListener('resize', () => {
  if (window.innerWidth < 768 && viewController.getCurrentView() === 'cards') {
    viewController.setView('compact');
  }
});
```

## Accessibility

All views maintain:
- ✅ Keyboard navigation
- ✅ Screen reader support
- ✅ ARIA labels
- ✅ Focus indicators
- ✅ Semantic HTML

## Performance

For large datasets (100+ items):
- Implement virtual scrolling
- Paginate in list view
- Lazy load card bodies
- Cache rendered HTML

---

**Apply this pattern to**: findings.html, rules.html, interactions.html, queue.html, reports.html