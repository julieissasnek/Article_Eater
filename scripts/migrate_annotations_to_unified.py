#!/usr/bin/env python3
"""
migrate_annotations_to_unified.py — Phase β: Annotation Store Unification
==========================================================================

Reads all L2 (CVA JSON) annotations from data/cva_annotations/ and writes
them into the unified SQLite annotation store (annotation_service.py Layer 1).

After this migration:
- All annotation types are queryable via get_all_annotations()
- L2 JSON files are kept for rollback safety (read-only)
- L3 extended annotations that have been generated are also persisted

Usage:
    python3 scripts/migrate_annotations_to_unified.py [--dry-run]
"""

import argparse
import json
import logging
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.services.annotation_service import (
    AnnotationService,
    AnnotationType,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)

CVA_ANNOTATION_DIR = PROJECT_ROOT / "data" / "cva_annotations"

try:
    from src.services.db_locator import resolve_web_db
    DB_PATH = resolve_web_db(prefer="integrated")
except Exception:
    DB_PATH = PROJECT_ROOT / "data" / "web_persistence_v2.db"


def migrate_cva_json_to_sqlite(
    svc: AnnotationService,
    dry_run: bool = False,
) -> dict:
    """Migrate L2 CVA JSON annotations to SQLite.

    Each JSON file in data/cva_annotations/ contains a CVAAnnotationSet
    with measurements, stimuli, molecule_links, constraint_tags, valuation_tags.

    We convert each into one or more Annotation records:
    - measurements → MEASUREMENT_MODALITY annotations
    - stimuli → STIMULUS_DESCRIPTION annotations
    - molecule_links → MOLECULE_T15_LINK annotations
    """
    stats = {"files": 0, "annotations": 0, "skipped": 0, "errors": 0}

    if not CVA_ANNOTATION_DIR.exists():
        logger.warning("CVA annotation directory not found: %s", CVA_ANNOTATION_DIR)
        return stats

    json_files = list(CVA_ANNOTATION_DIR.glob("*.json"))
    logger.info("Found %d CVA annotation files to migrate", len(json_files))

    batch = []

    for jf in json_files:
        stats["files"] += 1
        try:
            with open(jf) as f:
                data = json.load(f)

            target_id = data.get("target_id", jf.stem)

            # Measurements → MEASUREMENT_MODALITY
            for m in data.get("measurements", []):
                modality = m.get("modality", "unknown")
                content_parts = [f"modality={modality}"]
                if m.get("spatial_resolution"):
                    content_parts.append(f"spatial_res={m['spatial_resolution']}")
                if m.get("temporal_resolution"):
                    content_parts.append(f"temporal_res={m['temporal_resolution']}")
                if m.get("sample_size"):
                    content_parts.append(f"n={m['sample_size']}")
                if m.get("population"):
                    content_parts.append(f"population={m['population']}")

                batch.append({
                    "type": AnnotationType.MEASUREMENT_MODALITY,
                    "target_type": "template",
                    "target_id": target_id,
                    "content": "; ".join(content_parts),
                    "author": "cva_auto_annotate",
                    "confidence": m.get("confidence", 0.7),
                    "metadata": m,
                    "provenance": {"source": "cva_json_migration", "file": jf.name},
                })
                stats["annotations"] += 1

            # Stimuli → STIMULUS_DESCRIPTION
            for s in data.get("stimuli", []):
                stim_type = s.get("stimulus_type", "unknown")
                desc = s.get("description", "")
                content = f"type={stim_type}; {desc}" if desc else f"type={stim_type}"

                batch.append({
                    "type": AnnotationType.STIMULUS_DESCRIPTION,
                    "target_type": "template",
                    "target_id": target_id,
                    "content": content,
                    "author": "cva_auto_annotate",
                    "confidence": s.get("confidence", 0.6),
                    "metadata": s,
                    "provenance": {"source": "cva_json_migration", "file": jf.name},
                })
                stats["annotations"] += 1

            # Molecule links → MOLECULE_T15_LINK
            for ml in data.get("molecule_links", []):
                mol_id = ml.get("molecule_id", "unknown")
                link_type = ml.get("link_type", "supports")
                strength = ml.get("strength", 0.5)

                batch.append({
                    "type": AnnotationType.MOLECULE_T15_LINK,
                    "target_type": "template",
                    "target_id": target_id,
                    "content": f"molecule={mol_id}; type={link_type}; strength={strength}",
                    "author": "cva_auto_annotate",
                    "confidence": strength,
                    "metadata": ml,
                    "provenance": {"source": "cva_json_migration", "file": jf.name},
                })
                stats["annotations"] += 1

            # Constraint tags → stored in metadata of a single annotation
            constraint_tags = data.get("constraint_tags", {})
            valuation_tags = data.get("valuation_tags", {})
            if constraint_tags or valuation_tags:
                batch.append({
                    "type": AnnotationType.CROSS_REFERENCE,
                    "target_type": "template",
                    "target_id": target_id,
                    "content": f"CVA tags: {len(constraint_tags)} constraints, {len(valuation_tags)} valuations",
                    "author": "cva_auto_annotate",
                    "confidence": 0.7,
                    "metadata": {
                        "constraint_tags": constraint_tags,
                        "valuation_tags": valuation_tags,
                    },
                    "provenance": {"source": "cva_json_migration", "file": jf.name},
                })
                stats["annotations"] += 1

        except Exception as e:
            logger.warning("Error processing %s: %s", jf.name, e)
            stats["errors"] += 1

    if dry_run:
        logger.info(
            "DRY RUN — would insert %d annotations from %d files (%d errors)",
            stats["annotations"], stats["files"], stats["errors"],
        )
    else:
        if batch:
            # First ensure new types are registered
            registered = svc.ensure_new_types_registered()
            if registered:
                logger.info("Registered %d new annotation types", registered)

            svc.create_annotations_batch(batch)
            logger.info(
                "Inserted %d annotations from %d files (%d errors)",
                stats["annotations"], stats["files"], stats["errors"],
            )

    return stats


def report_coverage(svc: AnnotationService) -> None:
    """Print annotation coverage report."""
    coverage = svc.get_annotation_coverage()
    logger.info("=== Annotation Coverage Report ===")
    logger.info("Total active annotations: %d", coverage.get("total_active", 0))

    logger.info("By layer:")
    for layer, count in sorted(coverage.get("by_layer", {}).items()):
        logger.info("  %-12s %d", layer, count)

    logger.info("By target type:")
    for tt, info in sorted(coverage.get("by_target_type", {}).items()):
        logger.info(
            "  %-12s %d targets, %d annotations",
            tt, info["unique_targets"], info["total_annotations"],
        )

    # Check AN-SC-04: >50% beliefs have annotations
    belief_info = coverage.get("by_target_type", {}).get("belief", {})
    if belief_info:
        logger.info(
            "AN-SC-04: %d beliefs have annotations",
            belief_info.get("unique_targets", 0),
        )


def main():
    parser = argparse.ArgumentParser(
        description="Migrate L2/L3 annotations to unified SQLite store"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show what would be migrated without writing to DB",
    )
    parser.add_argument(
        "--db", type=str, default=str(DB_PATH),
        help="Path to SQLite database",
    )
    args = parser.parse_args()

    svc = AnnotationService(db_path=args.db)

    # Phase β Step 1: Migrate L2 CVA JSON → SQLite
    logger.info("=== Phase β: Migrating L2 CVA annotations ===")
    cva_stats = migrate_cva_json_to_sqlite(svc, dry_run=args.dry_run)
    logger.info("CVA migration: %s", json.dumps(cva_stats))

    # Report coverage
    if not args.dry_run:
        report_coverage(svc)

    # Summary
    total = cva_stats["annotations"]
    logger.info(
        "=== Migration complete: %d annotations %s ===",
        total,
        "(dry-run)" if args.dry_run else "inserted",
    )


if __name__ == "__main__":
    main()
