#!/usr/bin/env python3
"""
IMG-PIPE CLI: Run the complete image search/download/tag/link pipeline.

Supports multiple modes:
- --search: Generate search queries from templates
- --download: Download images
- --tag: Auto-tag images with vocabulary
- --link: Link images to ATLAS evidence
- --full: Execute complete pipeline (search → download → tag → link)

Usage:
    python scripts/run_image_pipeline.py --full --templates data/templates.json
    python scripts/run_image_pipeline.py --search --stimulus "natural garden setting"
    python scripts/run_image_pipeline.py --tag --image data/images/img-001.jpg
    python scripts/run_image_pipeline.py --link --image-id img-001 --belief-id belief-42

Author: Claude Code
Date: 2026-03-02
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "services"))

from image_pipeline_service import ImagePipelineService
from image_tag_service import ImageTagService
from image_pipeline_models import ImageSource

# Logging setup
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(
            LOG_DIR / f"image_pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        ),
    ],
)
logger = logging.getLogger(__name__)


# =============================================================================
# Configuration
# =============================================================================

PROJECT_ROOT = Path(__file__).parent.parent

VOCABULARY_PATH = PROJECT_ROOT / "data" / "attributes" / "image_tagging_vocabulary.json"
SCHEMA_PATH = PROJECT_ROOT / "data" / "attributes" / "image_tagging_schema.json"
EQUIVALENCE_CLASSES_PATH = PROJECT_ROOT / "data" / "decision_tree_equivalence_classes.json"
STIMULUS_DESCRIPTIONS_PATH = PROJECT_ROOT / "data" / "stimulus_descriptions_from_articles.json"

IMAGE_STORAGE_DIR = PROJECT_ROOT / "data" / "images"
OUTPUT_DIR = PROJECT_ROOT / "data" / "image_pipeline_outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# =============================================================================
# Mode: Search
# =============================================================================

def mode_search(args):
    """Generate search queries from stimulus description or template."""
    logger.info("=== MODE: SEARCH ===")

    # Initialize services
    try:
        tag_service = ImageTagService(
            vocabulary_path=str(VOCABULARY_PATH),
            schema_path=str(SCHEMA_PATH),
        )
    except Exception as e:
        logger.error(f"Failed to initialize tag service: {e}")
        return 1

    pipeline = ImagePipelineService(
        tag_service=tag_service,
        equivalence_classes_path=str(EQUIVALENCE_CLASSES_PATH),
        base_storage_dir=str(IMAGE_STORAGE_DIR),
    )

    # Generate queries
    if args.stimulus:
        stimulus = args.stimulus
    elif args.template_id:
        stimulus = f"Template {args.template_id}"
    else:
        logger.error("Must provide --stimulus or --template-id")
        return 1

    queries = pipeline.query_generator.generate_queries(
        source_template_id=args.template_id or "generic",
        stimulus_description=stimulus,
        equivalence_class=args.equivalence_class,
    )

    logger.info(f"Generated {len(queries)} search queries")

    # Display results
    results = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "stimulus": stimulus,
        "num_queries": len(queries),
        "queries": [
            {
                "query_id": q.query_id,
                "text": q.query_text,
                "type": q.query_type,
                "sources": [s.value for s in q.image_sources],
                "equivalence_class": q.equivalence_class,
            }
            for q in queries
        ],
    }

    # Save results
    output_file = OUTPUT_DIR / f"search_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    print(json.dumps(results, indent=2))
    logger.info(f"Search results saved to {output_file}")

    return 0


# =============================================================================
# Mode: Download
# =============================================================================

def mode_download(args):
    """Download images (STUB - mock implementation)."""
    logger.info("=== MODE: DOWNLOAD ===")

    if not args.url and not args.query:
        logger.error("Must provide --url or --query")
        return 1

    # Initialize pipeline
    try:
        tag_service = ImageTagService(
            vocabulary_path=str(VOCABULARY_PATH),
            schema_path=str(SCHEMA_PATH),
        )
    except Exception as e:
        logger.error(f"Failed to initialize tag service: {e}")
        return 1

    pipeline = ImagePipelineService(
        tag_service=tag_service,
        base_storage_dir=str(IMAGE_STORAGE_DIR),
    )

    results = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "downloads": [],
    }

    # Download from URL
    if args.url:
        source = ImageSource[args.source.upper()] if args.source else ImageSource.UNSPLASH
        dl_result = pipeline.download_manager.download_image(
            image_url=args.url,
            source=source,
        )

        results["downloads"].append({
            "image_id": dl_result.image_id,
            "url": args.url,
            "source": source.value,
            "success": dl_result.success,
            "filename": dl_result.filename if dl_result.success else None,
            "error": dl_result.error_message if not dl_result.success else None,
        })

        logger.info(f"Download result: {dl_result.image_id} - {'SUCCESS' if dl_result.success else 'FAILED'}")

    print(json.dumps(results, indent=2))

    return 0


# =============================================================================
# Mode: Tag
# =============================================================================

def mode_tag(args):
    """Auto-tag an image with vocabulary."""
    logger.info("=== MODE: TAG ===")

    if not args.image:
        logger.error("Must provide --image <path>")
        return 1

    image_path = Path(args.image)
    if not image_path.exists():
        logger.error(f"Image not found: {image_path}")
        return 1

    # Initialize services
    try:
        tag_service = ImageTagService(
            vocabulary_path=str(VOCABULARY_PATH),
            schema_path=str(SCHEMA_PATH),
        )
    except Exception as e:
        logger.error(f"Failed to initialize tag service: {e}")
        return 1

    pipeline = ImagePipelineService(
        tag_service=tag_service,
        base_storage_dir=str(IMAGE_STORAGE_DIR),
    )

    # Extract metadata
    metadata = pipeline.metadata_extractor.extract(str(image_path), ImageSource.LOCAL_PDF)

    # Auto-tag
    tagging_result = pipeline.auto_tagger.tag_image(
        image_id=image_path.stem,
        image_path=str(image_path),
        metadata=metadata,
        source_description=args.description,
    )

    results = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "image_id": tagging_result.image_id,
        "num_inferred_attributes": len(tagging_result.inferred_attributes),
        "domains": list(tagging_result.tags.keys()),
        "domain_scores": tagging_result.domain_scores,
        "relevant_templates": tagging_result.relevant_templates,
        "confidence_level": tagging_result.confidence_level,
        "validation_notes": tagging_result.validation_notes,
    }

    # Save results
    output_file = OUTPUT_DIR / f"tag_results_{tagging_result.tagging_result_id}.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(json.dumps(results, indent=2, default=str))
    logger.info(f"Tag results saved to {output_file}")

    return 0


# =============================================================================
# Mode: Link
# =============================================================================

def mode_link(args):
    """Link an image to ATLAS evidence."""
    logger.info("=== MODE: LINK ===")

    if not args.image_id or not args.belief_id:
        logger.error("Must provide --image-id and --belief-id")
        return 1

    # Initialize services
    try:
        tag_service = ImageTagService(
            vocabulary_path=str(VOCABULARY_PATH),
            schema_path=str(SCHEMA_PATH),
        )
    except Exception as e:
        logger.error(f"Failed to initialize tag service: {e}")
        return 1

    pipeline = ImagePipelineService(
        tag_service=tag_service,
        base_storage_dir=str(IMAGE_STORAGE_DIR),
    )

    logger.info(f"Linking image {args.image_id} to belief {args.belief_id}")

    results = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "image_id": args.image_id,
        "belief_id": args.belief_id,
        "status": "linking-stub",
        "note": "Evidence linking requires full pipeline context (tagged images). Use --full mode.",
    }

    print(json.dumps(results, indent=2))

    return 0


# =============================================================================
# Mode: Full
# =============================================================================

def mode_full(args):
    """Execute complete pipeline for templates."""
    logger.info("=== MODE: FULL PIPELINE ===")

    # Load templates
    if args.templates:
        template_file = Path(args.templates)
        if not template_file.exists():
            logger.error(f"Templates file not found: {template_file}")
            return 1

        with open(template_file, "r") as f:
            templates_data = json.load(f)
            if isinstance(templates_data, dict) and "templates" in templates_data:
                templates = templates_data["templates"]
            else:
                templates = templates_data if isinstance(templates_data, list) else []
    else:
        # Use sample templates from stimulus descriptions
        templates = []
        if STIMULUS_DESCRIPTIONS_PATH.exists():
            with open(STIMULUS_DESCRIPTIONS_PATH, "r") as f:
                stim_data = json.load(f)
                sample_stims = list(stim_data.get("categories", {}).items())[:3]
                for cat_name, cat_data in sample_stims:
                    stimuli = cat_data.get("stimuli", [])[:1]
                    for stim in stimuli:
                        templates.append({
                            "template_id": f"t-{cat_name}",
                            "belief_id": f"belief-{cat_name}",
                            "stimulus_description": stim.get("antecedent", ""),
                            "equivalence_class": cat_name,
                        })

    if not templates:
        logger.error("No templates found")
        return 1

    logger.info(f"Processing {len(templates)} templates")

    # Initialize services
    try:
        tag_service = ImageTagService(
            vocabulary_path=str(VOCABULARY_PATH),
            schema_path=str(SCHEMA_PATH),
        )
    except Exception as e:
        logger.error(f"Failed to initialize tag service: {e}")
        return 1

    pipeline = ImagePipelineService(
        tag_service=tag_service,
        equivalence_classes_path=str(EQUIVALENCE_CLASSES_PATH),
        base_storage_dir=str(IMAGE_STORAGE_DIR),
    )

    # Process templates
    batch_results = pipeline.process_batch(templates[:args.limit])

    # Summarize results
    total_searches = sum(len(r.get("searches", [])) for r in batch_results)
    total_downloads = sum(len(r.get("downloads", [])) for r in batch_results)
    total_tags = sum(len(r.get("tagged_images", [])) for r in batch_results)
    total_links = sum(len(r.get("evidence_links", [])) for r in batch_results)

    summary = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "num_templates_processed": len(batch_results),
        "total_searches": total_searches,
        "total_downloads": total_downloads,
        "total_images_tagged": total_tags,
        "total_evidence_links": total_links,
        "results": batch_results,
    }

    # Save results
    output_file = OUTPUT_DIR / f"pipeline_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, "w") as f:
        json.dump(summary, f, indent=2)

    # Save evidence links
    if pipeline.evidence_links:
        links_file = OUTPUT_DIR / f"evidence_links_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        pipeline.save_evidence_links(str(links_file))

    print(json.dumps(summary, indent=2))
    logger.info(f"Pipeline results saved to {output_file}")
    logger.info(
        f"Summary: {total_searches} searches, {total_downloads} downloads, "
        f"{total_tags} tags, {total_links} evidence links"
    )

    return 0


# =============================================================================
# Main
# =============================================================================

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="IMG-PIPE: Image Search/Download/Tag/Link Pipeline"
    )

    # Mode selection
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument(
        "--search",
        action="store_true",
        help="Generate search queries from stimulus",
    )
    mode_group.add_argument(
        "--download",
        action="store_true",
        help="Download images",
    )
    mode_group.add_argument(
        "--tag",
        action="store_true",
        help="Auto-tag an image",
    )
    mode_group.add_argument(
        "--link",
        action="store_true",
        help="Link image to evidence",
    )
    mode_group.add_argument(
        "--full",
        action="store_true",
        help="Execute full pipeline",
    )

    # Search mode options
    parser.add_argument(
        "--stimulus",
        help="Stimulus description for search queries",
    )
    parser.add_argument(
        "--template-id",
        help="Template ID (for search mode)",
    )
    parser.add_argument(
        "--equivalence-class",
        help="Equivalence class label",
    )

    # Download mode options
    parser.add_argument(
        "--url",
        help="Image URL to download",
    )
    parser.add_argument(
        "--source",
        choices=["unsplash", "flickr", "wikimedia", "arxiv-figures"],
        default="unsplash",
        help="Image source",
    )
    parser.add_argument(
        "--query",
        help="Search query for finding images",
    )

    # Tag mode options
    parser.add_argument(
        "--image",
        help="Path to image file",
    )
    parser.add_argument(
        "--description",
        help="Image source description for heuristic tagging",
    )

    # Link mode options
    parser.add_argument(
        "--image-id",
        help="Image ID to link",
    )
    parser.add_argument(
        "--belief-id",
        help="ATLAS belief ID",
    )

    # Full pipeline options
    parser.add_argument(
        "--templates",
        help="Path to templates JSON file",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Max templates to process (default: 5)",
    )

    # General options
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without executing",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    logger.info("IMG-PIPE CLI started")

    # Route to appropriate mode
    if args.search:
        return mode_search(args)
    elif args.download:
        return mode_download(args)
    elif args.tag:
        return mode_tag(args)
    elif args.link:
        return mode_link(args)
    elif args.full:
        return mode_full(args)

    return 1


if __name__ == "__main__":
    sys.exit(main())
