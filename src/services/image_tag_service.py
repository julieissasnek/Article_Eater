"""
Image Tag Service for environmental and architectural image characterization.

This service provides a complete implementation for:
- Loading and managing the image tagging vocabulary
- Validating tags against the JSON schema
- Computing domain-level summary scores
- Linking tagged attributes to relevant T2 templates
- Searching and filtering images by attribute

Author: Claude Code
Date: 2026-03-02
"""

import json
import os
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path
import uuid
from collections import defaultdict
from statistics import mean, stdev

import jsonschema
from jsonschema import ValidationError, Draft7Validator

logger = logging.getLogger(__name__)


class ImageTagService:
    """Service for managing image tags and vocabulary."""

    def __init__(
        self,
        vocabulary_path: Optional[str] = None,
        schema_path: Optional[str] = None,
    ):
        """
        Initialize the Image Tag Service.

        Args:
            vocabulary_path: Path to image_tagging_vocabulary.json
            schema_path: Path to image_tagging_schema.json
        """
        # Auto-locate files if not provided
        if vocabulary_path is None:
            vocabulary_path = self._find_file("image_tagging_vocabulary.json")
        if schema_path is None:
            schema_path = self._find_file("image_tagging_schema.json")

        self.vocabulary_path = vocabulary_path
        self.schema_path = schema_path

        # Load vocabulary and schema
        self.vocabulary = self._load_json(vocabulary_path)
        self.schema = self._load_json(schema_path)

        # Build internal lookup structures
        self.attributes_by_domain = self._index_attributes_by_domain()
        self.all_attributes = self._flatten_attributes()
        self.attribute_lookup = self._build_attribute_lookup()
        self.domain_score_specs = self._load_domain_score_specs()
        self.template_relevance_map = self._build_template_relevance_map()

        logger.info(
            f"ImageTagService initialized: {len(self.all_attributes)} attributes "
            f"across {len(self.attributes_by_domain)} domains"
        )

    @staticmethod
    def _find_file(filename: str) -> str:
        """Auto-locate files by searching common project paths."""
        search_paths = [
            Path.cwd() / "data" / "attributes" / filename,
            Path.cwd() / filename,
            Path(__file__).parent.parent.parent / "data" / "attributes" / filename,
        ]
        for path in search_paths:
            if path.exists():
                return str(path)
        raise FileNotFoundError(
            f"Could not locate {filename} in common project paths"
        )

    @staticmethod
    def _load_json(path: str) -> Dict[str, Any]:
        """Load JSON file with error handling."""
        with open(path, "r") as f:
            return json.load(f)

    def _index_attributes_by_domain(self) -> Dict[str, List[Dict[str, Any]]]:
        """Create a mapping of domain_id -> attributes."""
        result = {}
        for domain in self.vocabulary["domains"]:
            domain_id = domain["domain_id"]
            result[domain_id] = domain.get("attributes", [])
        return result

    def _flatten_attributes(self) -> Dict[str, Dict[str, Any]]:
        """Create a flat dict of attribute_id -> attribute definition."""
        result = {}
        for domain in self.vocabulary["domains"]:
            for attr in domain.get("attributes", []):
                result[attr["attribute_id"]] = attr
        return result

    def _build_attribute_lookup(self) -> Dict[str, Dict[str, Any]]:
        """Build rich lookup with attribute metadata."""
        lookup = {}
        for attr_id, attr in self.all_attributes.items():
            lookup[attr_id] = {
                "name": attr.get("name"),
                "measurement_type": attr.get("measurement_type"),
                "unit": attr.get("unit"),
                "valid_values": attr.get("valid_values"),
                "value_range": attr.get("value_range"),
                "t1_theories": attr.get("t1_theories", []),
                "t2_templates": attr.get("t2_templates", []),
            }
        return lookup

    def _load_domain_score_specs(self) -> Dict[str, Dict[str, Any]]:
        """Extract domain score computation specifications."""
        return self.vocabulary.get("domain_summary_scores", {})

    def _build_template_relevance_map(self) -> Dict[str, List[str]]:
        """Map template IDs to attributes that affect them."""
        template_map = defaultdict(set)
        for attr_id, attr in self.all_attributes.items():
            for template in attr.get("t2_templates", []):
                template_map[template].add(attr_id)
        return {k: list(v) for k, v in template_map.items()}

    # ========== Core Tagging Methods ==========

    def tag_image(
        self,
        image_id: str,
        tags: Dict[str, Dict[str, Any]],
        tagged_by: str = "system",
        tagging_method: str = "human-manual",
        source_paper_id: Optional[str] = None,
        image_source_description: Optional[str] = None,
        confidence_level: str = "moderate",
    ) -> Dict[str, Any]:
        """
        Create a complete tag record for an image.

        Args:
            image_id: Unique identifier for the image
            tags: Nested dict of domain -> attribute -> tag_value
            tagged_by: Identifier of the person/system doing the tagging
            tagging_method: one of human-manual, computational-automated, etc.
            source_paper_id: Optional paper DOI
            image_source_description: Optional description of image source
            confidence_level: one of low, moderate, high, expert

        Returns:
            Complete tag record dict
        """
        tag_record_id = f"tag-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{str(uuid.uuid4())[:8]}"

        # Validate tags before creating record
        validation_errors = self.validate_tags(tags)
        validation_notes = (
            "; ".join(validation_errors) if validation_errors else "All tags valid"
        )

        # Compute domain scores
        domain_scores = self.get_domain_scores(tags)

        # Find relevant templates
        relevant_templates = self.get_relevant_templates(tags)

        # Create tag record
        tag_record = {
            "tag_record_id": tag_record_id,
            "image_id": image_id,
            "source_paper_id": source_paper_id,
            "image_source_description": image_source_description,
            "tagged_at": datetime.utcnow().isoformat() + "Z",
            "tagged_by": tagged_by,
            "tagging_method": tagging_method,
            "confidence_level": confidence_level,
            "tags": tags,
            "domain_scores": domain_scores,
            "relevant_templates": relevant_templates,
            "validation_notes": validation_notes,
        }

        logger.info(f"Created tag record {tag_record_id} for image {image_id}")
        return tag_record

    def validate_tags(self, tags: Dict[str, Dict[str, Any]]) -> List[str]:
        """
        Validate tag structure and content.

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        # Check domain structure
        valid_domains = set(self.attributes_by_domain.keys())
        provided_domains = set(tags.keys())
        unknown_domains = provided_domains - valid_domains
        if unknown_domains:
            errors.append(f"Unknown domains: {unknown_domains}")

        # Check attributes within each domain
        for domain_id, domain_tags in tags.items():
            if domain_id not in self.attributes_by_domain:
                continue

            valid_attrs = {
                attr["attribute_id"]
                for attr in self.attributes_by_domain[domain_id]
            }
            provided_attrs = set(domain_tags.keys())
            unknown_attrs = provided_attrs - valid_attrs
            if unknown_attrs:
                errors.append(
                    f"Unknown attributes in {domain_id}: {unknown_attrs}"
                )

            # Validate attribute values
            for attr_id, tag_value in domain_tags.items():
                if attr_id not in self.all_attributes:
                    continue
                attr_def = self.all_attributes[attr_id]
                validation_error = self._validate_attribute_value(
                    attr_id, attr_def, tag_value
                )
                if validation_error:
                    errors.append(validation_error)

        # Check consistency rules
        consistency_errors = self._check_consistency_rules(tags)
        errors.extend(consistency_errors)

        return errors

    def _validate_attribute_value(
        self, attr_id: str, attr_def: Dict[str, Any], tag_value: Any
    ) -> Optional[str]:
        """Validate a single attribute value against its definition."""
        measurement_type = attr_def.get("measurement_type")

        if measurement_type == "continuous":
            if not isinstance(tag_value, dict) or "value" not in tag_value:
                return f"{attr_id}: continuous attribute requires {{value: number, ...}}"
            if not isinstance(tag_value["value"], (int, float)):
                return f"{attr_id}: value must be numeric"
            value_range = attr_def.get("value_range")
            if value_range and len(value_range) == 2:
                min_val, max_val = value_range
                if not (min_val <= tag_value["value"] <= max_val):
                    return f"{attr_id}: value {tag_value['value']} outside range [{min_val}, {max_val}]"

        elif measurement_type == "categorical":
            if not isinstance(tag_value, dict) or "value" not in tag_value:
                return f"{attr_id}: categorical attribute requires {{value: ..., ...}}"
            valid_values = attr_def.get("valid_values", [])
            tag_vals = tag_value["value"]
            if isinstance(tag_vals, str):
                tag_vals = [tag_vals]
            if valid_values:
                invalid = set(tag_vals) - set(valid_values)
                if invalid:
                    return f"{attr_id}: invalid values {invalid}, must be in {valid_values}"

        elif measurement_type == "ordinal":
            if not isinstance(tag_value, dict) or "value" not in tag_value:
                return f"{attr_id}: ordinal attribute requires {{value: string, ...}}"
            valid_values = attr_def.get("valid_values", [])
            if valid_values and tag_value["value"] not in valid_values:
                return f"{attr_id}: value '{tag_value['value']}' not in {valid_values}"

        return None

    def _check_consistency_rules(self, tags: Dict[str, Dict[str, Any]]) -> List[str]:
        """Check logical consistency rules across tags."""
        errors = []

        # Extract tag values for easier access
        def get_tag_value(domain: str, attr: str) -> Optional[Any]:
            if domain not in tags or attr not in tags[domain]:
                return None
            tag_obj = tags[domain][attr]
            return tag_obj.get("value") if isinstance(tag_obj, dict) else tag_obj

        # Rule 1: vegetation-presence = absent implies vegetation-density ≤ 5
        veg_presence = get_tag_value("vegetation", "vegetation-presence")
        veg_density = get_tag_value("vegetation", "vegetation-density")
        if veg_presence and "absent" in veg_presence and veg_density:
            if isinstance(veg_density, dict):
                veg_density = veg_density.get("value", 0)
            if veg_density and veg_density > 5:
                errors.append(
                    "Inconsistent: vegetation-presence=absent but vegetation-density > 5"
                )

        # Rule 2: naturalness score > 80 should have vegetation-presence ≥ moderate
        # (This is a warning, not an error, as it depends on computed score)

        # Rule 3: spatial-volume > 80 contradicts spatial-enclosure-degree = completely-enclosed
        sp_volume = get_tag_value("spatial-properties", "spatial-volume")
        sp_enclosure = get_tag_value("spatial-properties", "spatial-enclosure-degree")
        if sp_volume and sp_enclosure:
            if isinstance(sp_volume, dict):
                sp_volume = sp_volume.get("value", 0)
            if sp_volume > 80 and "completely-enclosed" in sp_enclosure:
                errors.append(
                    "Inconsistent: spatial-volume > 80 contradicts completely-enclosed"
                )

        return errors

    # ========== Domain Scoring Methods ==========

    def get_domain_scores(self, tags: Dict[str, Dict[str, Any]]) -> Dict[str, Dict]:
        """
        Compute domain-level summary scores from tagged attributes.

        Returns:
            Dict of domain_name -> scoring result
        """
        scores = {}

        for score_name, score_spec in self.domain_score_specs.items():
            if score_name in ["description", "computation", "weights"]:
                continue

            score_result = self._compute_domain_score(
                score_name, score_spec, tags
            )
            scores[score_name] = score_result

        return scores

    def _compute_domain_score(
        self, score_name: str, score_spec: Dict[str, Any], tags: Dict
    ) -> Dict[str, Any]:
        """Compute a single domain summary score."""
        weights = score_spec.get("weights", {})
        contributing = []
        missing = []
        weighted_sum = 0.0
        weight_total = 0.0

        for attr_id, weight in weights.items():
            # Handle negative weights (e.g., for refuge component in prospect-refuge-index)
            abs_weight = abs(weight)

            # Find attribute value
            attr_value = self._find_attribute_in_tags(attr_id, tags)

            if attr_value is None:
                missing.append(attr_id)
                continue

            # Normalize attribute value to 0-100 scale
            normalized_value = self._normalize_attribute_value(attr_id, attr_value)

            # Apply sign to weight if negative
            actual_weight = weight
            if weight < 0:
                normalized_value = 100 - normalized_value  # Invert the value

            weighted_contribution = normalized_value * abs_weight
            weighted_sum += weighted_contribution
            weight_total += abs_weight

            contributing.append(
                {
                    "attribute_id": attr_id,
                    "weight": weight,
                    "value": normalized_value,
                    "weighted_contribution": weighted_contribution,
                }
            )

        # Compute final score
        if weight_total > 0:
            final_score = weighted_sum / weight_total
        else:
            final_score = 50.0  # Default if no weights

        completeness = len(contributing) / (len(contributing) + len(missing))

        return {
            "score": round(final_score, 2),
            "computed_at": datetime.utcnow().isoformat() + "Z",
            "contributing_attributes": contributing,
            "missing_attributes": missing,
            "completeness": round(completeness, 2),
            "notes": f"Computed from {len(contributing)}/{len(contributing) + len(missing)} attributes"
            if missing
            else "All expected attributes present",
        }

    def _find_attribute_in_tags(
        self, attr_id: str, tags: Dict
    ) -> Optional[Any]:
        """Find an attribute value in the tags dict, handling nested structure."""
        for domain_tags in tags.values():
            if attr_id in domain_tags:
                tag_obj = domain_tags[attr_id]
                return tag_obj.get("value") if isinstance(tag_obj, dict) else tag_obj
        return None

    def _normalize_attribute_value(self, attr_id: str, value: Any) -> float:
        """Normalize an attribute value to 0-100 scale for scoring."""
        if attr_id not in self.all_attributes:
            return 50.0  # Unknown attribute

        attr_def = self.all_attributes[attr_id]
        measurement_type = attr_def.get("measurement_type")

        if measurement_type == "continuous":
            value_range = attr_def.get("value_range", [0, 100])
            if len(value_range) == 2:
                min_val, max_val = value_range
                if max_val == min_val:
                    return 50.0
                normalized = ((float(value) - min_val) / (max_val - min_val)) * 100.0
                return max(0.0, min(100.0, normalized))
            return float(value)

        elif measurement_type == "ordinal":
            valid_values = attr_def.get("valid_values", [])
            if isinstance(value, str) and value in valid_values:
                # Ordinal values are ranked 0, 25, 50, 75, 100
                index = valid_values.index(value)
                return (index / max(1, len(valid_values) - 1)) * 100.0
            return 50.0

        elif measurement_type == "categorical":
            # Categorical attributes don't directly translate to numeric scores
            # Map presence to 0 or 100 (absent/present logic)
            if isinstance(value, list):
                return 100.0 if value else 0.0
            return 100.0 if value else 0.0

        return 50.0

    # ========== Template Linking Methods ==========

    def get_relevant_templates(
        self, tags: Dict[str, Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Find T2 templates where the tagged visual attributes have explanatory power.

        Returns:
            List of template relevance records
        """
        # Collect all tagged attributes
        tagged_attrs = set()
        for domain_tags in tags.values():
            tagged_attrs.update(domain_tags.keys())

        # Find templates that depend on these attributes
        template_scores = defaultdict(lambda: {"attrs": [], "relevance": 0.0})

        for attr_id in tagged_attrs:
            if attr_id not in self.all_attributes:
                continue

            attr_def = self.all_attributes[attr_id]
            for template_id in attr_def.get("t2_templates", []):
                template_scores[template_id]["attrs"].append(attr_id)

        # Compute relevance scores
        relevant_templates = []
        for template_id, info in template_scores.items():
            # Relevance is proportion of this template's sensitive attributes that are tagged
            all_sensitive = self.template_relevance_map.get(template_id, [])
            if all_sensitive:
                relevance = len(info["attrs"]) / len(all_sensitive)
            else:
                relevance = 0.5

            relevant_templates.append(
                {
                    "template_id": template_id,
                    "relevance_score": round(relevance, 3),
                    "predicted_sensitive_attributes": info["attrs"],
                    "reasoning": f"{len(info['attrs'])} of {len(all_sensitive)} "
                    f"sensitive visual attributes tagged for this template",
                }
            )

        # Sort by relevance score descending
        relevant_templates.sort(
            key=lambda x: x["relevance_score"], reverse=True
        )

        return relevant_templates[:10]  # Return top 10

    # ========== Search and Filter Methods ==========

    def search_by_attribute(
        self, attr_id: str, value_range: Optional[Tuple[float, float]] = None
    ) -> Dict[str, Any]:
        """
        Get vocabulary and guidance for searching images by a specific attribute.

        Args:
            attr_id: The attribute to search for
            value_range: Optional (min, max) range for continuous attributes

        Returns:
            Attribute definition and search guidance
        """
        if attr_id not in self.all_attributes:
            raise ValueError(f"Unknown attribute: {attr_id}")

        attr_def = self.all_attributes[attr_id]

        return {
            "attribute_id": attr_id,
            "name": attr_def.get("name"),
            "measurement_type": attr_def.get("measurement_type"),
            "description": attr_def.get("description"),
            "valid_values": attr_def.get("valid_values"),
            "value_range": attr_def.get("value_range"),
            "unit": attr_def.get("unit"),
            "theoretical_grounding": attr_def.get("theoretical_grounding", []),
            "measurement_guidance": attr_def.get("measurement_guidance"),
            "search_query": self._build_search_query(attr_id, value_range),
        }

    def _build_search_query(
        self, attr_id: str, value_range: Optional[Tuple[float, float]] = None
    ) -> str:
        """Build a database query string for searching by attribute."""
        if value_range:
            return (
                f"tags.{attr_id}.value >= {value_range[0]} "
                f"AND tags.{attr_id}.value <= {value_range[1]}"
            )
        return f"tags.{attr_id} EXISTS"

    def get_vocabulary_summary(self) -> Dict[str, Any]:
        """Return high-level summary of the vocabulary."""
        return {
            "schema_version": self.vocabulary.get("version"),
            "generated_at": self.vocabulary.get("generated_at"),
            "total_domains": len(self.attributes_by_domain),
            "total_attributes": len(self.all_attributes),
            "domains": [
                {
                    "domain_id": domain_id,
                    "attribute_count": len(attrs),
                }
                for domain_id, attrs in self.attributes_by_domain.items()
            ],
            "scientific_grounding": self.vocabulary.get("scientific_grounding", {}),
        }

    def get_attribute_info(self, attr_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific attribute."""
        if attr_id not in self.all_attributes:
            return {"error": f"Attribute {attr_id} not found"}

        attr = self.all_attributes[attr_id]
        return {
            "attribute_id": attr_id,
            "name": attr.get("name"),
            "measurement_type": attr.get("measurement_type"),
            "description": attr.get("description"),
            "unit": attr.get("unit"),
            "value_range": attr.get("value_range"),
            "valid_values": attr.get("valid_values"),
            "theoretical_grounding": attr.get("theoretical_grounding"),
            "measurement_guidance": attr.get("measurement_guidance"),
            "assessment_method": attr.get("assessment_method"),
            "reliability_notes": attr.get("reliability_notes"),
            "t1_theories": attr.get("t1_theories", []),
            "t2_templates": attr.get("t2_templates", []),
        }

    # ========== JSON Schema Validation ==========

    def validate_tag_record(self, tag_record: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate a complete tag record against the JSON schema.

        Returns:
            (is_valid, list_of_errors)
        """
        validator = Draft7Validator(self.schema)
        errors = []

        for error in validator.iter_errors(tag_record):
            errors.append(f"{error.path}: {error.message}")

        return len(errors) == 0, errors

    def get_schema_validator(self) -> Draft7Validator:
        """Return a validator for the tag record schema."""
        return Draft7Validator(self.schema)


# ========== Convenience Functions ==========


def create_default_service() -> ImageTagService:
    """Create an ImageTagService with default file locations."""
    return ImageTagService()


def batch_validate_tags(
    tag_records: List[Dict[str, Any]],
) -> Dict[str, List[str]]:
    """
    Validate multiple tag records and return errors by record ID.

    Args:
        tag_records: List of tag record dicts

    Returns:
        Dict mapping record IDs to error lists
    """
    service = create_default_service()
    results = {}

    for record in tag_records:
        record_id = record.get("tag_record_id", "unknown")
        is_valid, errors = service.validate_tag_record(record)
        results[record_id] = errors

    return results
