"""
qa_browse — QA Knowledge Base Browse System
============================================

A Streamlit-based interactive knowledge base for the CMR
(Correlation-to-Mechanism Research) system. Provides search,
browse, and deep-dive capabilities across:

- 186 mechanistic templates (T2 level)
- 13 explanatory molecules (T1.5 groupings)
- 94 MASTER_DOC sections (authoritative prose)
- 812 enriched papers with CrossRef/S2 metadata
- 1,735 citation graph edges
- Argumentation system (critiques, evidence hierarchies)

Architecture
------------
    qa_browse/
    ├── __init__.py          # Package exports and contracts
    ├── topic_index.py       # Data layer: loads all sources into searchable index
    ├── topic_renderer.py    # Rendering utilities for topic pages
    └── config.py            # Domain colors, bridge warrant labels, paths

    streamlit_app/pages/
    ├── 9_knowledge_base.py  # Home page: search + domain/theme browse
    └── 10_topic.py          # Topic page: Wikipedia-style article view

Data Sources (read-only)
------------------------
    data/templates/*.json        → 186 mechanistic template definitions
    data/molecules/*.json        → 13 molecule groupings
    data/qa_cache/*_QA.json      → L1/L2/L3 progressive disclosure caches
    data/attributes/AD_*.json    → 5 domain attribute sets
    data/extractions/10.*.json   → Per-paper extraction + metadata
    data/extractions/citation_graph.json → Citation network
    MASTER_DOC_CMR_2026-02-25.md → Authoritative prose (8,662 lines)

Maintenance
-----------
When templates, molecules, or extraction data change, the browse
system automatically reflects changes on next load — no rebuild
needed. The TopicIndex is a lazy singleton that reloads when the
Streamlit app restarts.

If the MASTER_DOC is updated, ensure the file remains at one of:
    - <repo>/docs/MASTER_DOC_CMR_2026-02-25.md
    - <repo>/../MASTER_DOC_CMR_2026-02-25.md

To add a new domain, update DOMAIN_CONFIG and TEMPLATE_DOMAIN_MAP
in config.py.

Usage
-----
    from qa_browse import get_index, TopicIndex, SearchResult

    idx = get_index()
    results = idx.search("biophilia")
    template = idx.get_template("VIEW1")
    section = idx.get_master_doc_section("48")
"""

from __future__ import annotations

__version__ = "0.1.0"
__all__ = [
    "TopicIndex",
    "get_index",
    "SearchResult",
    "TemplateData",
    "MoleculeData",
    "MasterDocSection",
    "DOMAIN_CONFIG",
    "BRIDGE_WARRANT_LABELS",
]

# Re-export from the implementation modules.
# These imports are deferred to avoid circular imports and heavy
# loading when only the package metadata is needed.

def get_index():
    """Get or create the singleton TopicIndex.
    
    Returns:
        TopicIndex: The loaded, searchable index of all CMR content.
    """
    from .topic_index import get_index as _get
    return _get()


def __getattr__(name):
    """Lazy imports for package-level names."""
    if name in ("TopicIndex", "SearchResult", "TemplateData",
                "MoleculeData", "MasterDocSection"):
        from . import topic_index
        return getattr(topic_index, name)
    if name in ("DOMAIN_CONFIG", "BRIDGE_WARRANT_LABELS"):
        from . import config
        return getattr(config, name)
    raise AttributeError(f"module 'qa_browse' has no attribute {name!r}")
