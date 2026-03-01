"""
Compatibility shim — re-exports from the qa_browse package.

Streamlit pages can import from either location:
    from topic_index import get_index     # old (still works)
    from qa_browse import get_index       # new (preferred)
"""

from qa_browse.topic_index import (
    TopicIndex,
    get_index,
    SearchResult,
    TemplateData,
    MoleculeData,
    MasterDocSection,
)
from qa_browse.config import (
    DOMAIN_CONFIG,
    TEMPLATE_DOMAIN_MAP,
    BRIDGE_WARRANT_LABELS,
)

__all__ = [
    "TopicIndex",
    "get_index",
    "SearchResult",
    "TemplateData",
    "MoleculeData",
    "MasterDocSection",
    "DOMAIN_CONFIG",
    "TEMPLATE_DOMAIN_MAP",
    "BRIDGE_WARRANT_LABELS",
]
