"""
Data models for the IMG-PIPE (Image Pipeline) system.

Defines the core data structures for image search, download, tagging, and linking.

Author: Claude Code
Date: 2026-03-02
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum
from datetime import datetime
import uuid


class ImageSource(Enum):
    """Enumeration of supported image sources."""
    UNSPLASH = "unsplash"
    FLICKR = "flickr"
    WIKIMEDIA = "wikimedia"
    ARXIV_FIGURES = "arxiv-figures"
    LOCAL_PDF = "local-pdf"
    USER_UPLOAD = "user-upload"


@dataclass
class SearchQuery:
    """Represents a single search query for images."""
    query_id: str
    source_template_id: str
    query_text: str
    query_type: str  # "general", "specific", "theoretical"
    equivalence_class: Optional[str] = None
    image_sources: List[ImageSource] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    notes: Optional[str] = None

    @classmethod
    def create(
        cls,
        source_template_id: str,
        query_text: str,
        query_type: str,
        equivalence_class: Optional[str] = None,
        image_sources: Optional[List[ImageSource]] = None,
        notes: Optional[str] = None,
    ) -> "SearchQuery":
        """Factory method to create a SearchQuery with auto-generated ID."""
        return cls(
            query_id=f"query-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{str(uuid.uuid4())[:8]}",
            source_template_id=source_template_id,
            query_text=query_text,
            query_type=query_type,
            equivalence_class=equivalence_class,
            image_sources=image_sources or [ImageSource.UNSPLASH, ImageSource.WIKIMEDIA],
            notes=notes,
        )


@dataclass
class DownloadResult:
    """Result of downloading a single image."""
    image_id: str
    source: ImageSource
    source_url: str
    local_path: str
    filename: str
    success: bool
    file_size_bytes: int = 0
    file_format: str = "unknown"
    downloaded_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    error_message: Optional[str] = None
    perceptual_hash: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create_success(
        cls,
        source: ImageSource,
        source_url: str,
        local_path: str,
        filename: str,
        file_size_bytes: int = 0,
        file_format: str = "unknown",
        metadata: Optional[Dict[str, Any]] = None,
        perceptual_hash: Optional[str] = None,
    ) -> "DownloadResult":
        """Create a successful download result."""
        return cls(
            image_id=f"img-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{str(uuid.uuid4())[:8]}",
            source=source,
            source_url=source_url,
            local_path=local_path,
            filename=filename,
            success=True,
            file_size_bytes=file_size_bytes,
            file_format=file_format,
            metadata=metadata or {},
            perceptual_hash=perceptual_hash,
        )

    @classmethod
    def create_failure(
        cls,
        source: ImageSource,
        source_url: str,
        error_message: str,
    ) -> "DownloadResult":
        """Create a failed download result."""
        return cls(
            image_id=f"img-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{str(uuid.uuid4())[:8]}",
            source=source,
            source_url=source_url,
            local_path="",
            filename="",
            success=False,
            error_message=error_message,
        )


@dataclass
class ImageMetadata:
    """Image metadata extracted from file and source."""
    image_id: str
    filename: str
    file_format: str
    file_size_bytes: int
    resolution_width: Optional[int] = None
    resolution_height: Optional[int] = None
    aspect_ratio: Optional[float] = None
    color_space: Optional[str] = None
    bit_depth: Optional[int] = None
    exif_data: Dict[str, Any] = field(default_factory=dict)
    source_attribution: Dict[str, str] = field(default_factory=dict)  # license, photographer, url
    extracted_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    notes: Optional[str] = None


@dataclass
class TaggingResult:
    """Result of automatic tagging for a single image."""
    image_id: str
    tagging_result_id: str
    tags: Dict[str, Dict[str, Any]]
    domain_scores: Dict[str, Dict[str, Any]]
    relevant_templates: List[Dict[str, Any]]
    confidence_level: str  # "low", "moderate", "high"
    tagging_method: str  # "auto-heuristic", "ml-model", "human-manual"
    inferred_attributes: Dict[str, Any]  # Details on how each attribute was inferred
    tagged_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    validation_notes: Optional[str] = None
    error_message: Optional[str] = None

    @classmethod
    def create(
        cls,
        image_id: str,
        tags: Dict[str, Dict[str, Any]],
        domain_scores: Dict[str, Dict[str, Any]],
        relevant_templates: List[Dict[str, Any]],
        confidence_level: str = "moderate",
        tagging_method: str = "auto-heuristic",
        inferred_attributes: Optional[Dict[str, Any]] = None,
        validation_notes: Optional[str] = None,
    ) -> "TaggingResult":
        """Factory method to create a TaggingResult with auto-generated ID."""
        return cls(
            image_id=image_id,
            tagging_result_id=f"tag-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{str(uuid.uuid4())[:8]}",
            tags=tags,
            domain_scores=domain_scores,
            relevant_templates=relevant_templates,
            confidence_level=confidence_level,
            tagging_method=tagging_method,
            inferred_attributes=inferred_attributes or {},
            validation_notes=validation_notes,
        )


@dataclass
class ImageRecord:
    """Complete record for a processed image."""
    image_id: str
    source: ImageSource
    source_url: str
    local_path: str
    metadata: ImageMetadata
    tagging_result: Optional[TaggingResult] = None
    ingest_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    search_query_id: Optional[str] = None
    equivalence_class: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class ImageEvidenceLink:
    """Link between an image and ATLAS evidence (belief/template)."""
    link_id: str
    image_id: str
    belief_id: str
    template_id: str
    match_score: float  # 0.0 to 1.0
    matching_attributes: List[str]  # attribute_ids that matched
    match_method: str  # "attribute-overlap", "template-relevance", "manual"
    confidence_level: str  # "low", "moderate", "high", "expert"
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    reasoning: Optional[str] = None

    @classmethod
    def create(
        cls,
        image_id: str,
        belief_id: str,
        template_id: str,
        match_score: float,
        matching_attributes: Optional[List[str]] = None,
        match_method: str = "attribute-overlap",
        confidence_level: str = "moderate",
        reasoning: Optional[str] = None,
    ) -> "ImageEvidenceLink":
        """Factory method to create an ImageEvidenceLink with auto-generated ID."""
        return cls(
            link_id=f"link-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{str(uuid.uuid4())[:8]}",
            image_id=image_id,
            belief_id=belief_id,
            template_id=template_id,
            match_score=match_score,
            matching_attributes=matching_attributes or [],
            match_method=match_method,
            confidence_level=confidence_level,
            reasoning=reasoning,
        )
