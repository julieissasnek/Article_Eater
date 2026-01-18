
PHASE 1: COMPLETE TEMPLATES & UI COMPONENTS

Article Eater v17.0 - Dual-Hierarchy Visualization

Component: Frontend Templates, refactored for "Findings" and "Mechanisms"
Files: 3 HTML templates + 1 CSS
Integration: Replaces existing v16 templates [cite: 317-319, 343].

TEMPLATE 1: HIERARCHICAL FINDINGS VIEW

File: templates/finding_view_hierarchical.html (Replaces rules_view_hierarchical.html)

<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Findings — {{ job_id }}</title>
  <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
  <link rel="stylesheet" href="{{ url_for('static', filename='hierarchy_v17.css') }}">
</head>
<body>
  {% include '_partials/nav.html' %}
  
  <div class="container">
    <div class="breadcrumb">
      <a href="/jobs">Jobs</a> &raquo;
      <a href="/shortlist/{{ job_id }}/view">{{ job_id }}</a> &raquo;
      <span class="current">Findings</span>
    </div>
    
    <header class="page-header">
      <div class="header-content">
        <h1>Empirical Findings</h1>
        <p class="header-description">
          {{ stats.micro_count }} micro-findings aggregated into {{ stats.meso_count }} meso-findings
        </p>
      </div>
      
      <!-- View Mode Selector (Unchanged) -->
      <div class="view-selector">
        <button class="view-btn active" data-view="hierarchy" title="Hierarchical tree view">
          <span class="icon">🌳</span> <span class="label">Tree</span>
        </button>
        <button class="view-btn" data-view="flat" title="Flat list view">
          <span class="icon">📋</span> <span class="label">List</span>
        </button>
        <button class="view-btn disabled" data-view="network" title="Network graph (coming soon)">
          <span class="icon">🕸️</span> <span class="label">Network</span>
        </button>
      </div>
    </header>
    
    <!-- Stats Grid (Unchanged) -->
    <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-value">{{ stats.total_count }}</div>
          <div class="stat-label">Total Findings</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ stats.micro_count }}</div>
          <div class="stat-label">Micro-Findings</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ stats.meso_count }}</div>
          <div class="stat-label">Meso-Findings</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ stats.avg_triangulation|round(1) }}</div>
          <div class="stat-label">Avg Triangulation</div>
        </div>
    </div>
    
    <!-- Hierarchical View -->
    <div id="hierarchy-view" class="view-container active">
        <!-- Tree Controls (Unchanged) -->
        <div class="tree-controls">
            <button class="control-btn" id="expand-all">⊞ Expand All</button>
            <button class="control-btn" id="collapse-all">⊟ Collapse All</button>
            <!-- ... filters ... -->
            <div class="legend">
              <span class="legend-badge meso">MESO</span> Findings
              <span class="legend-badge micro">MICRO</span> Findings
            </div>
        </div>
        
        <!-- Tree Container -->
        <div class="tree-container">
            {% for macro in macro_findings %}
                <!-- ... (macro-finding node here) ... -->
                <div class="rule-children">
                    {% for meso in macro.child_findings %}
                        {% include '_partials/meso_finding_node.html' %}
                    {% endfor %}
                </div>
            {% endfor %}
            
            {% for meso in standalone_meso_findings %}
                {% include '_partials/meso_finding_node.html' %}
            {% endfor %}
            
            {% if orphan_micro_findings %}
                <!-- ... (orphan micro-findings section) ... -->
            {% endif %}
        </div>
    </div>
    
    <!-- Flat List View -->
    <div id="flat-view" class="view-container" style="display: none;">
      {% include '_partials/findings_flat.html' %}
    </div>
    
  </div>
  
  <script src="{{ url_for('static', filename='hierarchy.js') }}"></script>
</body>
</html>


TEMPLATE 2: MESO-FINDING NODE (Refactored)

File: templates/_partials/meso_finding_node.html (Replaces meso_rule_node.html)

<!-- 
  Meso-Finding Node (v17)
  Replaces meso_rule_node.html [cite: 343]
  CRITICAL CHANGE: Removes direct 'mechanism' display and adds
  a loop over the new 'explanation_links' relationship.
-->
<div class="finding-node meso-node" data-construct="{{ meso.consequent }}">
  <div class="finding-header" onclick="toggleNode(this)">
    <span class="expand-icon expanded">▼</span>
    <span class="finding-badge meso">MESO</span>
    
    <div class="finding-content">
      <h3 class="finding-text">{{ meso.finding }}</h3>
      
      <!-- Aggregation Summary (Unchanged from v16 [cite: 343]) -->
      <div class="aggregation-summary">
        <span class="summary-badge">
          🔬 {{ meso.operational_measures_used|length }} measures
        </span>
        <span class="summary-badge">
          👥 N={{ meso.total_sample_size }}
        </span>
        <span class="summary-badge">
          📊 {{ meso.num_child_rules }} studies
        </span>
      </div>
      
      <!-- Confidence Breakdown (Unchanged from v16 [cite: 343]) -->
      <div class="confidence-breakdown">
        <div class="confidence-bar-container">
          <!-- ... (confidence segments) ... -->
        </div>
        <div class="confidence-total">
          Total Confidence: <strong>{{ (meso.weight * 100)|round }}%</strong>
        </div>
      </div>
      
      <!-- 
        *** NEW v17 EXPLANATION SECTION ***
        This replaces the v16 'mechanism-display'.
        It loops over the `finding_mechanism_links` table.
      -->
      {% if meso.explanation_links %}
      <div class="explanation-section">
        <h4 class="explanation-header">Proposed Explanations (The "Why")</h4>
        <ul class="explanation-list">
          {% for link in meso.explanation_links %}
          <li class="explanation-item">
            <div class="explanation-link">
              <span class="mechanism-icon">⚙️</span>
              <a href="/mechanism/{{ link.mechanism.id }}" class="mechanism-link">
                {{ link.mechanism.name }}
              </a>
            </div>
            <div class="explanation-provenance">
              Linked by 
              <a href="/paper/{{ link.paper.doi|urlencode }}/analysis" class="paper-link">
                {{ link.paper.title[:40] }}...
              </a>
              (Strength: <span class="strength-badge {{ link.evidence_strength }}">
                {{ link.evidence_strength }}
              </span>)
            </div>
            {% if link.snippet %}
            <blockquote class="explanation-snippet">
              "{{ link.snippet }}"
            </blockquote>
            {% endif %}
          </li>
          {% endfor %}
        </ul>
      </div>
      {% endif %}
      <!-- *** END NEW v17 SECTION *** -->
      
    </div>
  </div>
  
  <!-- Child Micro-Findings (Unchanged from v16 [cite: 343]) -->
  <div class="finding-children">
    {% for micro in meso.child_findings %}
    <div class="finding-node micro-node">
      <!-- ... (micro-finding details) ... -->
    </div>
    {% endfor %}
  </div>
</div>


TEMPLATE 3: FLAT LIST PARTIAL (Refactored)

File: templates/_partials/findings_flat.html (Replaces rules_flat.html)

This file is largely the same as the v16 rules_flat.html [cite: 319], but with all instances of rule renamed to finding and the mechanism display logic updated.

CSS STYLESHEET: Hierarchy v17

File: static/hierarchy_v17.css (Modified)

This file contains all styles from hierarchy.css [cite: 344], with the following additions/modifications to support the new explanation display:

/* ... (All v16 styles [cite: 344] remain) ... */

/* Rename 'rule' to 'finding' */
.finding-node { ... }
.finding-header { ... }
.finding-badge { ... }
.finding-text { ... }
.finding-children { ... }

/* *** NEW v17 STYLES *** */

.explanation-section {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 2px dashed #e2e8f0;
}

.explanation-header {
  font-size: 0.875rem;
  font-weight: 700;
  color: #4a5568;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.75rem;
}

.explanation-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.explanation-item {
  background: #f7fafc;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 0.75rem 1rem;
  margin-bottom: 0.5rem;
}

.explanation-link {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.25rem;
}

.mechanism-icon {
  font-size: 1.125rem;
}

.mechanism-link {
  font-size: 1rem;
  font-weight: 600;
  color: #3182ce;
  text-decoration: none;
}
.mechanism-link:hover {
  text-decoration: underline;
}

.explanation-provenance {
  font-size: 0.8125rem;
  color: #718096;
  padding-left: 1.625rem; /* Align with link */
}

.explanation-provenance .paper-link {
  color: #4a5568;
  font-weight: 500;
}

.strength-badge {
  font-weight: 700;
  font-size: 0.75rem;
  text-transform: capitalize;
}
.strength-badge.strong { color: #48bb78; }
.strength-badge.moderate { color: #ed8936; }
.strength-badge.speculative { color: #a0aec0; }

.explanation-snippet {
  font-family: 'Georgia', serif;
  font-style: italic;
  color: #2d3748;
  border-left: 3px solid #cbd5e0;
  padding-left: 0.75rem;
  margin: 0.5rem 0 0.25rem 1.625rem;
  font-size: 0.875rem;
}