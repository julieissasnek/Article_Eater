"""
Validation modules for epistemic web integration (Sprint 6a).
"""

from .node_template_mapping import (
    NODE_TYPE_TEMPLATE_MAP,
    validate_node_for_template,
    get_valid_node_types_for_template,
)

__all__ = [
    "NODE_TYPE_TEMPLATE_MAP",
    "validate_node_for_template",
    "get_valid_node_types_for_template",
]
