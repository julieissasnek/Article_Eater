"""
IMG-PIPE: Image Search/Find/Download/Tag/Link Pipeline Service.

Orchestrates the complete image lifecycle: searching, downloading, tagging,
and linking to ATLAS evidence. Integrates with image_tag_service for vocabulary
and evidence linking.

Author: Claude Code
Date: 2026-03-02
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
import hashlib
import math

from image_pipeline_models import (
    ImageSource,
    SearchQuery,
    DownloadResult,
    ImageMetadata,
    TaggingResult,
    ImageRecord,
    ImageEvidenceLink,
)

logger = logging.getLogger(__name__)


class SearchQueryGenerator:
    """Generate optimal search queries from templates or stimulus descriptions."""

    def __init__(self, equivalence_classes_path: Optional[str] = None):
        """
        Initialize the query generator.

        Args:
            equivalence_classes_path: Path to decision_tree_equivalence_classes.json
        """
        self.equivalence_classes = {}
        self.category_to_class = {}

        if equivalence_classes_path:
            self._load_equivalence_classes(equivalence_classes_path)

    def _load_equivalence_classes(self, path: str):
        """Load equivalence classes from JSON."""
        try:
            with open(path, "r") as f:
                data = json.load(f)
                if "equivalence_classes" in data:
                    for ec in data["equivalence_classes"]:
                        cat_name = ec.get("category_name")
                        self.equivalence_classes[cat_name] = ec
                        self.category_to_class[ec.get("commonsense_label", cat_name)] = cat_name
            logger.info(f"Loaded {len(self.equivalence_classes)} equivalence classes")
        except Exception as e:
            logger.warning(f"Failed to load equivalence classes: {e}")

    def generate_queries(
        self,
        source_template_id: str,
        stimulus_description: Optional[str] = None,
        equivalence_class: Optional[str] = None,
    ) -> List[SearchQuery]:
        """
        Generate 3-5 search queries from a template or stimulus description.

        Returns list of SearchQuery objects with types: general, specific, theoretical
        """
        queries = []

        # Parse the stimulus description for key concepts
        key_concepts = self._extract_key_concepts(stimulus_description or "")
        attr_hints = self._infer_visual_attributes(stimulus_description or "")

        # 1. General query (broad terms from description)
        if key_concepts:
            general_text = " ".join(key_concepts[:3])
            q1 = SearchQuery.create(
                source_template_id=source_template_id,
                query_text=general_text,
                query_type="general",
                equivalence_class=equivalence_class,
                notes=f"Generated from stimulus: {stimulus_description[:50]}..."
                if stimulus_description
                else None,
            )
            queries.append(q1)

        # 2. Specific query (architectural/environmental focus)
        if stimulus_description:
            if "architectural" in stimulus_description.lower() or "building" in stimulus_description.lower():
                q2 = SearchQuery.create(
                    source_template_id=source_template_id,
                    query_text=f"architectural {key_concepts[0] if key_concepts else 'environment'}",
                    query_type="specific",
                    equivalence_class=equivalence_class,
                    image_sources=[ImageSource.UNSPLASH, ImageSource.WIKIMEDIA, ImageSource.ARXIV_FIGURES],
                    notes="Focused on architectural/built environment",
                )
                queries.append(q2)

        # 3. Theoretical query (attribute-based)
        if attr_hints:
            attr_text = " ".join(attr_hints[:2])
            q3 = SearchQuery.create(
                source_template_id=source_template_id,
                query_text=attr_text,
                query_type="theoretical",
                equivalence_class=equivalence_class,
                notes=f"Inferred from visual attributes: {attr_hints}",
            )
            queries.append(q3)

        # 4. Alternative phrasing if available
        if len(key_concepts) > 1:
            alt_text = " ".join(key_concepts[1:3])
            q4 = SearchQuery.create(
                source_template_id=source_template_id,
                query_text=alt_text,
                query_type="specific",
                equivalence_class=equivalence_class,
                notes="Alternative phrasing of key concepts",
            )
            queries.append(q4)

        return queries[:5]  # Return up to 5 queries

    def _extract_key_concepts(self, text: str) -> List[str]:
        """Extract key noun phrases and concepts from text."""
        if not text:
            return []

        # Simple heuristic: split by common delimiters, filter short words
        words = text.lower().split()
        filtered = [w.strip(",.;:") for w in words if len(w) > 3]

        # Remove common stop words
        stop_words = {
            "that", "this", "with", "from", "have", "been", "which", "their",
            "environment", "design", "studied", "impact"
        }
        key_words = [w for w in filtered if w not in stop_words]

        return key_words[:5]

    def _infer_visual_attributes(self, text: str) -> List[str]:
        """Infer visual/attribute-related keywords from stimulus description."""
        keywords = ["natural", "artificial", "enclosed", "open", "bright", "dark",
                    "complex", "simple", "vegetation", "water", "symmetry", "prospect", "refuge"]

        found = []
        text_lower = text.lower()
        for keyword in keywords:
            if keyword in text_lower:
                found.append(keyword)

        return found[:3]


class ImageDownloadManager:
    """Download, deduplicate, and store images."""

    def __init__(self, base_storage_dir: Optional[str] = None):
        """
        Initialize the download manager.

        Args:
            base_storage_dir: Base directory for image storage (default: data/images)
        """
        self.base_dir = Path(base_storage_dir or "data/images")
        self.base_dir.mkdir(parents=True, exist_ok=True)

        self.registry_path = self.base_dir / "image_registry.json"
        self.perceptual_hash_map = {}  # Track phashes to detect duplicates

        self._load_registry()

    def _load_registry(self):
        """Load existing image registry."""
        if self.registry_path.exists():
            try:
                with open(self.registry_path, "r") as f:
                    data = json.load(f)
                    self.perceptual_hash_map = data.get("perceptual_hashes", {})
                logger.info(f"Loaded registry with {len(self.perceptual_hash_map)} images")
            except Exception as e:
                logger.warning(f"Failed to load registry: {e}")

    def _compute_perceptual_hash_stub(self, content: bytes) -> str:
        """Stub implementation of perceptual hash (placeholder for real phash library)."""
        # In real implementation, would use imagehash library
        # For now, use simple hash of file content
        return hashlib.md5(content).hexdigest()[:16]

    def _check_duplicate(self, phash: str) -> Optional[str]:
        """Check if image with this phash already exists. Returns image_id if found."""
        return self.perceptual_hash_map.get(phash)

    def download_image(
        self,
        image_url: str,
        source: ImageSource,
        max_retries: int = 2,
    ) -> DownloadResult:
        """
        Download an image from a URL (STUBBED - mock implementation).

        In production, would make real HTTP requests to Unsplash, Flickr, etc.
        For now, returns mock success with synthetic data.
        """
        # STUB: Mock successful download
        try:
            # Generate mock image ID and path
            image_id = f"img-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{source.value}"
            filename = f"{image_id}.jpg"
            source_dir = self.base_dir / source.value
            source_dir.mkdir(parents=True, exist_ok=True)
            local_path = str(source_dir / filename)

            # Mock content and metadata
            mock_content = b"MOCK_IMAGE_DATA_" * 100
            phash = self._compute_perceptual_hash_stub(mock_content)

            # Check for duplicates
            if existing_id := self._check_duplicate(phash):
                logger.info(f"Image {image_id} is duplicate of {existing_id}")
                return DownloadResult.create_failure(
                    source=source,
                    source_url=image_url,
                    error_message=f"Duplicate of {existing_id}",
                )

            # Record in registry
            self.perceptual_hash_map[phash] = image_id
            self._save_registry()

            metadata = {
                "source_url": image_url,
                "phash": phash,
                "fetched_at": datetime.utcnow().isoformat() + "Z",
            }

            result = DownloadResult.create_success(
                source=source,
                source_url=image_url,
                local_path=local_path,
                filename=filename,
                file_size_bytes=len(mock_content),
                file_format="jpg",
                metadata=metadata,
                perceptual_hash=phash,
            )

            logger.info(f"Downloaded {image_id} from {source.value}")
            return result

        except Exception as e:
            logger.error(f"Download failed for {image_url}: {e}")
            return DownloadResult.create_failure(
                source=source,
                source_url=image_url,
                error_message=str(e),
            )

    def _save_registry(self):
        """Persist image registry to JSON."""
        try:
            registry_data = {
                "generated_at": datetime.utcnow().isoformat() + "Z",
                "total_images": len(self.perceptual_hash_map),
                "perceptual_hashes": self.perceptual_hash_map,
            }
            with open(self.registry_path, "w") as f:
                json.dump(registry_data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save registry: {e}")


class ImageMetadataExtractor:
    """Extract metadata from downloaded images."""

    def extract(self, image_path: str, source: ImageSource) -> ImageMetadata:
        """
        Extract metadata from an image file (STUB - simplified implementation).

        Collects EXIF, file properties, source attribution.
        """
        try:
            path = Path(image_path)
            file_size = path.stat().st_size if path.exists() else 0
            filename = path.name

            # Stub: mock dimension extraction
            resolution_w, resolution_h = self._stub_get_dimensions(image_path)
            aspect_ratio = (resolution_w / resolution_h) if resolution_h else None

            # Mock EXIF data
            exif_data = {
                "creation_date": None,
                "camera_model": None,
                "iso_speed": None,
            }

            # Mock attribution
            attribution = {
                "source": source.value,
                "license": "cc0" if source == ImageSource.UNSPLASH else "unknown",
                "photographer": "Unknown",
            }

            metadata = ImageMetadata(
                image_id=path.stem,
                filename=filename,
                file_format=path.suffix[1:].lower(),
                file_size_bytes=file_size,
                resolution_width=resolution_w,
                resolution_height=resolution_h,
                aspect_ratio=aspect_ratio,
                color_space="RGB",
                bit_depth=8,
                exif_data=exif_data,
                source_attribution=attribution,
            )

            logger.info(f"Extracted metadata for {filename}")
            return metadata

        except Exception as e:
            logger.error(f"Metadata extraction failed for {image_path}: {e}")
            # Return minimal metadata on error
            return ImageMetadata(
                image_id="unknown",
                filename=Path(image_path).name,
                file_format="unknown",
                file_size_bytes=0,
            )

    def _stub_get_dimensions(self, image_path: str) -> Tuple[int, int]:
        """Stub: mock image dimension extraction."""
        # In production, would use PIL/Pillow
        # For now, return reasonable defaults
        common_dims = [(1920, 1080), (1024, 768), (800, 600), (1200, 800)]
        import random
        return random.choice(common_dims)


class AutoTagger:
    """Automatically tag images with 41-attribute vocabulary (heuristic-based)."""

    def __init__(self, tag_service):
        """
        Initialize auto-tagger with reference to ImageTagService.

        Args:
            tag_service: ImageTagService instance for vocabulary access
        """
        self.tag_service = tag_service

    def tag_image(
        self,
        image_id: str,
        image_path: str,
        metadata: ImageMetadata,
        source_description: Optional[str] = None,
    ) -> TaggingResult:
        """
        Automatically tag an image using heuristics.

        Infers attributes from:
        - Image metadata (resolution, aspect ratio, color space)
        - Filename analysis
        - Source description
        - Basic image properties
        """
        try:
            tags = {}
            inferred_attrs = {}

            # Process each domain
            for domain_id, attributes in self.tag_service.attributes_by_domain.items():
                domain_tags = {}

                for attr in attributes:
                    attr_id = attr.get("attribute_id")
                    measurement_type = attr.get("measurement_type")

                    # Infer value for this attribute
                    inferred_value, inference_method = self._infer_attribute(
                        attr_id,
                        measurement_type,
                        image_path,
                        metadata,
                        source_description,
                    )

                    if inferred_value is not None:
                        # Store as tag
                        if measurement_type == "continuous":
                            domain_tags[attr_id] = {"value": inferred_value, "method": inference_method}
                        elif measurement_type in ["categorical", "ordinal"]:
                            domain_tags[attr_id] = {"value": inferred_value, "method": inference_method}

                        # Track inference
                        inferred_attrs[attr_id] = {
                            "value": inferred_value,
                            "method": inference_method,
                            "confidence": self._estimate_confidence(inference_method),
                        }

                if domain_tags:
                    tags[domain_id] = domain_tags

            # Compute domain scores using tag service
            domain_scores = self.tag_service.get_domain_scores(tags)

            # Find relevant templates
            relevant_templates = self.tag_service.get_relevant_templates(tags)

            # Create tagging result
            result = TaggingResult.create(
                image_id=image_id,
                tags=tags,
                domain_scores=domain_scores,
                relevant_templates=relevant_templates,
                confidence_level="moderate",
                tagging_method="auto-heuristic",
                inferred_attributes=inferred_attrs,
                validation_notes=f"Auto-tagged {len(inferred_attrs)} attributes across {len(tags)} domains",
            )

            logger.info(f"Tagged {image_id} with {len(inferred_attrs)} attributes")
            return result

        except Exception as e:
            logger.error(f"Tagging failed for {image_id}: {e}")
            return TaggingResult(
                image_id=image_id,
                tagging_result_id=f"tag-error-{image_id}",
                tags={},
                domain_scores={},
                relevant_templates=[],
                confidence_level="low",
                tagging_method="auto-heuristic",
                inferred_attributes={},
                error_message=str(e),
            )

    def _infer_attribute(
        self,
        attr_id: str,
        measurement_type: str,
        image_path: str,
        metadata: ImageMetadata,
        source_description: Optional[str] = None,
    ) -> Tuple[Optional[Any], str]:
        """
        Infer a single attribute value using heuristics.

        Returns (value, inference_method_name)
        """
        # Spatial properties
        if attr_id == "spatial-volume" and metadata.resolution_width:
            # Infer from resolution: higher res = larger/more detailed space
            volume = min(100, (metadata.resolution_width / 1920.0) * 100)
            return volume, "resolution-heuristic"

        if attr_id == "spatial-enclosure-degree":
            # Aspect ratio hints: narrow aspect suggests enclosed, wide suggests open
            if metadata.aspect_ratio:
                if metadata.aspect_ratio < 1.0:
                    return "moderately-enclosed", "aspect-ratio-heuristic"
                elif metadata.aspect_ratio > 1.5:
                    return "open-prospect", "aspect-ratio-heuristic"
            return None, "unavailable"

        # Naturalness domain
        if attr_id == "vegetation-density":
            # Infer from filename/description mentions of natural elements
            if source_description:
                if any(word in source_description.lower() for word in ["forest", "garden", "tree", "park"]):
                    return 70, "description-keyword"
            return 30, "default-conservative"

        if attr_id == "water-presence":
            if source_description and any(word in source_description.lower() for word in ["water", "lake", "river", "ocean"]):
                return "present", "description-keyword"
            return "absent", "default-conservative"

        # Color and light domain
        if attr_id == "color-temperature":
            # Stub: infer from filename patterns
            if image_path and ("warm" in image_path.lower() or "sunset" in image_path.lower()):
                return "warm", "filename-heuristic"
            if image_path and ("cool" in image_path.lower() or "winter" in image_path.lower()):
                return "cool", "filename-heuristic"
            return "neutral", "default"

        if attr_id == "brightness-level":
            # Stub: estimate based on metadata or description
            if source_description and "dark" in source_description.lower():
                return 30, "description-keyword"
            if source_description and "bright" in source_description.lower():
                return 80, "description-keyword"
            return 50, "default-neutral"

        # Visual complexity
        if attr_id == "visual-complexity":
            # Rough estimate: higher resolution often means more detail/complexity
            if metadata.resolution_width and metadata.resolution_width > 2000:
                return 70, "resolution-heuristic"
            elif metadata.resolution_width and metadata.resolution_width < 800:
                return 40, "resolution-heuristic"
            return 55, "default-moderate"

        # No inference available for this attribute
        return None, "unavailable"

    def _estimate_confidence(self, method: str) -> float:
        """Estimate confidence (0.0-1.0) based on inference method."""
        confidence_map = {
            "description-keyword": 0.7,
            "filename-heuristic": 0.6,
            "resolution-heuristic": 0.65,
            "aspect-ratio-heuristic": 0.6,
            "default-conservative": 0.4,
            "default": 0.5,
            "default-neutral": 0.5,
            "default-moderate": 0.5,
            "unavailable": 0.0,
        }
        return confidence_map.get(method, 0.5)


class EvidenceLinkingService:
    """Link tagged images to ATLAS evidence (beliefs/templates)."""

    def __init__(self, tag_service):
        """
        Initialize linking service.

        Args:
            tag_service: ImageTagService instance for template relevance lookup
        """
        self.tag_service = tag_service

    def link_image_to_evidence(
        self,
        image_id: str,
        tagging_result: TaggingResult,
        belief_id: str,
    ) -> List[ImageEvidenceLink]:
        """
        Create links between a tagged image and relevant ATLAS evidence.

        Returns list of ImageEvidenceLink records.
        """
        links = []

        try:
            # Get templates from tagging result
            if not tagging_result.relevant_templates:
                logger.warning(f"No relevant templates found for {image_id}")
                return links

            for template_info in tagging_result.relevant_templates:
                template_id = template_info.get("template_id")
                relevance_score = template_info.get("relevance_score", 0.5)
                attrs = template_info.get("predicted_sensitive_attributes", [])

                # Create link
                link = ImageEvidenceLink.create(
                    image_id=image_id,
                    belief_id=belief_id,
                    template_id=template_id,
                    match_score=relevance_score,
                    matching_attributes=attrs,
                    match_method="attribute-overlap",
                    confidence_level=self._score_to_confidence(relevance_score),
                    reasoning=f"Overlap on {len(attrs)} visual attributes relevant to this template",
                )
                links.append(link)

            logger.info(f"Created {len(links)} evidence links for {image_id}")
            return links

        except Exception as e:
            logger.error(f"Evidence linking failed for {image_id}: {e}")
            return links

    def find_images_for_template(
        self,
        template_id: str,
        min_match_score: float = 0.5,
    ) -> List[str]:
        """
        Find all images that match a given template ID.

        Returns list of image_ids that link to this template.
        """
        # Stub: would query image registry for links
        return []

    def _score_to_confidence(self, score: float) -> str:
        """Convert numeric score to confidence level."""
        if score >= 0.8:
            return "high"
        elif score >= 0.6:
            return "moderate"
        else:
            return "low"


class ImagePipelineService:
    """Orchestrates the complete image pipeline."""

    def __init__(
        self,
        tag_service,
        equivalence_classes_path: Optional[str] = None,
        base_storage_dir: Optional[str] = None,
    ):
        """
        Initialize the complete IMG-PIPE pipeline.

        Args:
            tag_service: ImageTagService instance
            equivalence_classes_path: Path to equivalence classes JSON
            base_storage_dir: Base directory for image storage
        """
        self.tag_service = tag_service

        self.query_generator = SearchQueryGenerator(equivalence_classes_path)
        self.download_manager = ImageDownloadManager(base_storage_dir)
        self.metadata_extractor = ImageMetadataExtractor()
        self.auto_tagger = AutoTagger(tag_service)
        self.evidence_linker = EvidenceLinkingService(tag_service)

        self.processed_images: Dict[str, ImageRecord] = {}
        self.evidence_links: List[ImageEvidenceLink] = []

    def process_template(
        self,
        template_id: str,
        stimulus_description: str,
        belief_id: str,
        equivalence_class: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Process a complete pipeline for a single template.

        Returns summary of search, download, tagging, and linking results.
        """
        results = {
            "template_id": template_id,
            "belief_id": belief_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "searches": [],
            "downloads": [],
            "tagged_images": [],
            "evidence_links": [],
            "summary": {},
        }

        try:
            # Step 1: Generate search queries
            queries = self.query_generator.generate_queries(
                source_template_id=template_id,
                stimulus_description=stimulus_description,
                equivalence_class=equivalence_class,
            )
            results["searches"] = [
                {
                    "query_id": q.query_id,
                    "text": q.query_text,
                    "type": q.query_type,
                    "sources": [s.value for s in q.image_sources],
                }
                for q in queries
            ]

            # Step 2: Download images (stub - would iterate through queries and sources)
            for query in queries[:2]:  # Limit to 2 queries for demo
                for source in query.image_sources[:2]:  # Limit to 2 sources per query
                    # Stub: construct mock URL
                    mock_url = f"https://{source.value}.example.com/images/{query.query_text.replace(' ', '-')}"

                    dl_result = self.download_manager.download_image(
                        image_url=mock_url,
                        source=source,
                    )

                    if dl_result.success:
                        results["downloads"].append(
                            {
                                "image_id": dl_result.image_id,
                                "source": source.value,
                                "filename": dl_result.filename,
                                "size_bytes": dl_result.file_size_bytes,
                            }
                        )

                        # Step 3: Extract metadata
                        metadata = self.metadata_extractor.extract(
                            dl_result.local_path,
                            source,
                        )

                        # Step 4: Auto-tag
                        tagging_result = self.auto_tagger.tag_image(
                            image_id=dl_result.image_id,
                            image_path=dl_result.local_path,
                            metadata=metadata,
                            source_description=stimulus_description,
                        )

                        results["tagged_images"].append(
                            {
                                "image_id": dl_result.image_id,
                                "num_attributes": len(tagging_result.inferred_attributes),
                                "domains": list(tagging_result.tags.keys()),
                                "confidence": tagging_result.confidence_level,
                            }
                        )

                        # Step 5: Link to evidence
                        links = self.evidence_linker.link_image_to_evidence(
                            image_id=dl_result.image_id,
                            tagging_result=tagging_result,
                            belief_id=belief_id,
                        )

                        results["evidence_links"].extend(
                            [
                                {
                                    "link_id": link.link_id,
                                    "image_id": link.image_id,
                                    "template_id": link.template_id,
                                    "match_score": link.match_score,
                                }
                                for link in links
                            ]
                        )

                        self.evidence_links.extend(links)

            # Summary
            results["summary"] = {
                "queries_generated": len(queries),
                "images_downloaded": len(results["downloads"]),
                "images_tagged": len(results["tagged_images"]),
                "evidence_links_created": len(results["evidence_links"]),
            }

            logger.info(f"Completed pipeline for template {template_id}: {results['summary']}")

        except Exception as e:
            logger.error(f"Pipeline failed for template {template_id}: {e}")
            results["error"] = str(e)

        return results

    def process_batch(
        self,
        templates: List[Dict[str, str]],
    ) -> List[Dict[str, Any]]:
        """
        Process multiple templates in batch.

        Args:
            templates: List of dicts with keys: template_id, belief_id, stimulus_description

        Returns list of pipeline results
        """
        batch_results = []
        for template in templates:
            result = self.process_template(
                template_id=template.get("template_id"),
                stimulus_description=template.get("stimulus_description", ""),
                belief_id=template.get("belief_id"),
                equivalence_class=template.get("equivalence_class"),
            )
            batch_results.append(result)

        logger.info(f"Batch processing complete: {len(batch_results)} templates")
        return batch_results

    def save_evidence_links(self, output_path: str):
        """Save evidence links to JSON."""
        try:
            data = {
                "generated_at": datetime.utcnow().isoformat() + "Z",
                "total_links": len(self.evidence_links),
                "links": [
                    {
                        "link_id": link.link_id,
                        "image_id": link.image_id,
                        "belief_id": link.belief_id,
                        "template_id": link.template_id,
                        "match_score": link.match_score,
                        "confidence_level": link.confidence_level,
                    }
                    for link in self.evidence_links
                ],
            }
            with open(output_path, "w") as f:
                json.dump(data, f, indent=2)
            logger.info(f"Saved {len(self.evidence_links)} evidence links to {output_path}")
        except Exception as e:
            logger.error(f"Failed to save evidence links: {e}")
