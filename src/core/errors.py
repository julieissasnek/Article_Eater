"""Centralized Error Types for Article Eater.

This module defines domain-specific exceptions to replace generic ValueError/RuntimeError
with meaningful, catchable error types.

Usage:
    from src.core.errors import BeliefNotFoundError, ValidationError

    try:
        belief = web.get_belief(belief_id)
    except BeliefNotFoundError:
        # Handle missing belief
        pass

Exception Hierarchy:
    ArticleEaterError (base)
    ├── EntityNotFoundError
    │   ├── BeliefNotFoundError
    │   ├── TheoryNotFoundError
    │   ├── BridgeNotFoundError
    │   └── PaperNotFoundError
    ├── ValidationError
    │   ├── SchemaValidationError
    │   ├── ConstraintViolationError
    │   └── InvalidParameterError
    ├── ProcessingError
    │   ├── ExtractionError
    │   ├── LLMError
    │   └── ParsingError
    ├── ConfigurationError
    │   ├── MissingConfigError
    │   └── InvalidConfigError
    └── DatabaseError
        ├── MigrationError
        └── IntegrityError
"""

from __future__ import annotations

from typing import Any, Optional


class ArticleEaterError(Exception):
    """Base exception for all Article Eater errors."""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        if self.details:
            return f"{self.message} | {self.details}"
        return self.message


# =============================================================================
# ENTITY NOT FOUND ERRORS
# =============================================================================

class EntityNotFoundError(ArticleEaterError):
    """Base class for entity-not-found errors."""

    entity_type: str = "entity"

    def __init__(self, entity_id: str, message: Optional[str] = None):
        msg = message or f"{self.entity_type} not found: {entity_id}"
        super().__init__(msg, {"entity_id": entity_id, "entity_type": self.entity_type})
        self.entity_id = entity_id


class BeliefNotFoundError(EntityNotFoundError):
    """Raised when a belief ID doesn't exist in the web."""
    entity_type = "Belief"


class TheoryNotFoundError(EntityNotFoundError):
    """Raised when a theory ID doesn't exist."""
    entity_type = "Theory"


class BridgeNotFoundError(EntityNotFoundError):
    """Raised when a bridge warrant ID doesn't exist."""
    entity_type = "Bridge"


class PaperNotFoundError(EntityNotFoundError):
    """Raised when a paper ID doesn't exist."""
    entity_type = "Paper"


class TemplateNotFoundError(EntityNotFoundError):
    """Raised when a template ID doesn't exist."""
    entity_type = "Template"


# =============================================================================
# VALIDATION ERRORS
# =============================================================================

class ValidationError(ArticleEaterError):
    """Base class for validation errors."""
    pass


class SchemaValidationError(ValidationError):
    """Raised when data doesn't match expected schema."""

    def __init__(self, message: str, schema: Optional[str] = None, errors: Optional[list] = None):
        super().__init__(message, {"schema": schema, "errors": errors or []})
        self.schema = schema
        self.errors = errors or []


class ConstraintViolationError(ValidationError):
    """Raised when an operation would violate system constraints."""

    def __init__(self, message: str, constraint: str):
        super().__init__(message, {"constraint": constraint})
        self.constraint = constraint


class InvalidParameterError(ValidationError):
    """Raised when a function parameter is invalid."""

    def __init__(self, param_name: str, value: Any, reason: str):
        message = f"Invalid parameter '{param_name}': {reason} (got {value!r})"
        super().__init__(message, {"param": param_name, "value": value, "reason": reason})
        self.param_name = param_name
        self.value = value
        self.reason = reason


# =============================================================================
# PROCESSING ERRORS
# =============================================================================

class ProcessingError(ArticleEaterError):
    """Base class for processing/pipeline errors."""
    pass


class ExtractionError(ProcessingError):
    """Raised when claim extraction fails."""

    def __init__(self, message: str, paper_id: Optional[str] = None):
        super().__init__(message, {"paper_id": paper_id})
        self.paper_id = paper_id


class LLMError(ProcessingError):
    """Raised when LLM call fails."""

    def __init__(self, message: str, provider: Optional[str] = None, model: Optional[str] = None):
        super().__init__(message, {"provider": provider, "model": model})
        self.provider = provider
        self.model = model


class ParsingError(ProcessingError):
    """Raised when parsing (JSON, text, etc.) fails."""

    def __init__(self, message: str, content: Optional[str] = None):
        # Truncate content for error message
        truncated = content[:200] + "..." if content and len(content) > 200 else content
        super().__init__(message, {"content_preview": truncated})
        self.content = content


# =============================================================================
# CONFIGURATION ERRORS
# =============================================================================

class ConfigurationError(ArticleEaterError):
    """Base class for configuration errors."""
    pass


class MissingConfigError(ConfigurationError):
    """Raised when required configuration is missing."""

    def __init__(self, config_key: str, source: Optional[str] = None):
        message = f"Missing required configuration: {config_key}"
        if source:
            message += f" (expected in {source})"
        super().__init__(message, {"key": config_key, "source": source})
        self.config_key = config_key


class InvalidConfigError(ConfigurationError):
    """Raised when configuration value is invalid."""

    def __init__(self, config_key: str, value: Any, reason: str):
        message = f"Invalid configuration '{config_key}': {reason}"
        super().__init__(message, {"key": config_key, "value": value, "reason": reason})
        self.config_key = config_key


# =============================================================================
# DATABASE ERRORS
# =============================================================================

class DatabaseError(ArticleEaterError):
    """Base class for database errors."""
    pass


class MigrationError(DatabaseError):
    """Raised when database migration fails."""

    def __init__(self, message: str, version: Optional[int] = None):
        super().__init__(message, {"version": version})
        self.version = version


class IntegrityError(DatabaseError):
    """Raised when database integrity check fails."""

    def __init__(self, message: str, table: Optional[str] = None):
        super().__init__(message, {"table": table})
        self.table = table


# =============================================================================
# EPISTEMIC ERRORS (domain-specific)
# =============================================================================

class EpistemicError(ArticleEaterError):
    """Base class for epistemic/reasoning errors."""
    pass


class CoherenceError(EpistemicError):
    """Raised when coherence computation fails or detects anomaly."""

    def __init__(self, message: str, belief_id: Optional[str] = None):
        super().__init__(message, {"belief_id": belief_id})
        self.belief_id = belief_id


class CircularDependencyError(EpistemicError):
    """Raised when circular warrant dependency is detected."""

    def __init__(self, message: str, cycle: Optional[list[str]] = None):
        super().__init__(message, {"cycle": cycle})
        self.cycle = cycle
