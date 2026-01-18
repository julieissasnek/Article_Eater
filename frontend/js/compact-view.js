/**
 * Compact View Controller
 * Reusable view density management for Article Eater GUIs
 * Version: 1.0
 */

class CompactViewController {
  constructor(containerId, options = {}) {
    this.containerId = containerId;
    this.currentView = options.defaultView || 'cards';
    this.pageName = options.pageName || window.location.pathname.split('/').pop().replace('.html', '');
    this.renderCallbacks = {
      cards: options.renderCards || (() => ''),
      compact: options.renderCompact || (() => ''),
      list: options.renderList || (() => '')
    };
    
    this.init();
  }
  
  init() {
    this.loadViewPreference();
    this.attachEventListeners();
  }
  
  loadViewPreference() {
    // Try page-specific preference first
    let saved = localStorage.getItem(`view_${this.pageName}`);
    
    // Fall back to global preference
    if (!saved) {
      saved = localStorage.getItem('preferredView');
    }
    
    if (saved && ['cards', 'compact', 'list'].includes(saved)) {
      this.setView(saved, false); // false = don't re-render yet
    }
  }
  
  attachEventListeners() {
    document.querySelectorAll('[data-view-toggle]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const viewType = e.currentTarget.getAttribute('data-view-toggle');
        this.setView(viewType);
      });
    });
  }
  
  setView(viewType, shouldRender = true) {
    if (!['cards', 'compact', 'list'].includes(viewType)) {
      console.warn(`Invalid view type: ${viewType}`);
      return;
    }
    
    this.currentView = viewType;
    
    // Update toggle buttons
    document.querySelectorAll('[data-view-toggle]').forEach(btn => {
      btn.classList.remove('active');
      if (btn.getAttribute('data-view-toggle') === viewType) {
        btn.classList.add('active');
      }
    });
    
    // Update container class
    const container = document.getElementById(this.containerId);
    if (container) {
      container.className = `${viewType}-view`;
    }
    
    // Save preference
    localStorage.setItem('preferredView', viewType);
    localStorage.setItem(`view_${this.pageName}`, viewType);
    
    // Re-render if needed
    if (shouldRender) {
      this.render();
    }
  }
  
  render() {
    const container = document.getElementById(this.containerId);
    if (!container) {
      console.error(`Container not found: ${this.containerId}`);
      return;
    }
    
    const renderFn = this.renderCallbacks[this.currentView];
    if (renderFn) {
      container.innerHTML = renderFn();
    } else {
      console.warn(`No render callback for view: ${this.currentView}`);
    }
  }
  
  getCurrentView() {
    return this.currentView;
  }
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
  module.exports = CompactViewController;
}