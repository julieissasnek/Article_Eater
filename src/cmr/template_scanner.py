"""
Template Scanner — Populates TemplateRecord DB table from JSON files.

This module implements Doc 68 Part 4.1: scan data/templates/*.json,
extract metadata, classify per Doc 67 deduplication map, and insert records.

The scanner:
1. Reads each JSON template file in data/templates/
2. Extracts top-level metadata fields (template_id, display_id, name, etc.)
3. Classifies dedup_status using Doc 67 Part 1 deduplication map
4. Defaults missing fields per spec:
   - pe_contribution: "organizational" if not specified
   - practical_accessibility: "B" if not specified
5. Inserts TemplateRecord into the database
"""

import json
import logging
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, make_transient

from src.cmr.models import Base, TemplateRecord, get_engine, get_session

logger = logging.getLogger(__name__)


# =============================================================================
# DOC 67 DEDUPLICATION MAP
# =============================================================================
# Per Doc 67 Part 1, each Gen-1 template falls into one of four categories:
# S (Superseded), P (Partial), G (Gap), R (Reference)
#
# Gen-2 templates are all "active" by default.
#
# This map encodes the explicit classifications from Doc 67.

# T-series deduplication (from Doc 67 Part 1 table)
T_SERIES_DEDUP: Dict[str, Tuple[str, Optional[str]]] = {
    # display_id: (dedup_status, superseded_by or None)
    "T1": ("residual", None),  # P - residual: auditory 1/f
    "T2": ("residual", None),  # P - residual: refuge component
    "T3": ("superseded", "VF1"),  # S - fully covered by VF + T1 residual
    "T4": ("gap", None),  # G - attention demand not in Gen-2
    "T5": ("residual", None),  # P - residual: threat pathway
    "T6": ("gap", None),  # G - cortisol cascade
    "T7": ("gap", None),  # G - allostatic anticipation
    "T8": ("residual", None),  # P - neural place/grid cell mechanism
    "T9": ("superseded", "SC4"),  # S - fully captured by SC4
    "T10": ("gap", None),  # G - sleep consolidation
    "T11": ("residual", None),  # P - LC-NE arousal
    "T12": ("reference", None),  # R - PE computational framework
    "T13": ("superseded", "VIEW1"),  # S - fully superseded
    "T14": ("gap", None),  # G - nav-stress loop
    "T15": ("residual", None),  # P - environmental control
    "T16": ("residual", None),  # P - restoration time-course
    "T17": ("gap", None),  # G - dopaminergic novelty
    "T18": ("gap", None),  # G - vestibular-spatial
    "T19": ("superseded", "SOC1"),  # S - fully superseded by SOC series
    "T20": ("residual", None),  # P - convergent cognitive performance
    "T21": ("reference", None),  # R - active inference framework
    "T22": ("residual", None),  # P - scene categorization LSF
    "T23": ("gap", None),  # G - context-dependent memory
    "T24": ("residual", None),  # P - theta oscillation neural mechanism
    "T25": ("superseded", "VIEW1"),  # S - soft fascination in VIEW1
    "T26": ("reference", None),  # R - ACh attention gating
    "T27": ("residual", None),  # P - non-thermal interoception
    "T28": ("gap", None),  # G - cognitive offloading
    "T29": ("reference", None),  # R - multi-channel summation
    "T30": ("reference", None),  # R - precision weighting
    "T31": ("superseded", "MAT1"),  # S - thermal adaptive PE
    "T32": ("residual", None),  # P - subcortical auditory
    "T33": ("residual", None),  # P - acoustic space perception
    "T34": ("superseded", "MAT2"),  # S - haptic CT-afferent
    "T35": ("superseded", "OLF1"),  # S - olfactory context
    "T36": ("reference", None),  # R - WM capacity constraint
    "T37": ("reference", None),  # R - ecological rationality
    "T38": ("residual", None),  # P - hierarchical depth constraint
    "T39": ("superseded", "MAT3"),  # S - cross-modal congruence
    "T40": ("residual", None),  # P - inverse effectiveness
    # T41-T47: Panel IV - deferred to individual assessment
    # T48-T52: Panel V Social Brain - mostly superseded by SOC calibration
}

# Gen-2 domain series are all active
GEN2_SERIES = {"L", "MAT", "TP", "SOC", "CREA", "VIEW", "SC", "COL", "VF", "OLF"}

# AX (Auxiliary) and M (Music) series - Gen-1, default to gap unless specified
AX_M_SERIES = {"AX", "M"}


def extract_series(display_id: str) -> str:
    """
    Extract the series prefix from a display_id.

    Examples:
        CREA4 -> CREA
        L1 -> L
        MAT3 -> MAT
        T27 -> T
        AX12 -> AX
        VIEW1 -> VIEW
    """
    # Match letters at start
    match = re.match(r"^([A-Z]+)", display_id)
    if match:
        return match.group(1)
    return display_id


def determine_generation(display_id: str, series: str) -> int:
    """
    Determine template generation (1 or 2) per Doc 67.

    Generation 1: T-series, M-series, AX-series
    Generation 2: L, MAT, TP, SOC, CREA, VIEW, SC, COL, VF, OLF series
    """
    if series in GEN2_SERIES:
        return 2
    elif series in {"T", "M", "AX"}:
        return 1
    else:
        # CROSS-series and others: default to Gen-1 (framework templates)
        return 1


def classify_dedup_status(display_id: str, series: str, generation: int) -> Tuple[str, Optional[str]]:
    """
    Classify template dedup_status per Doc 67 Part 1.

    Returns:
        (dedup_status, superseded_by or None)
    """
    # Gen-2 templates are all active
    if generation == 2:
        return ("active", None)

    # Check explicit T-series map
    if display_id in T_SERIES_DEDUP:
        return T_SERIES_DEDUP[display_id]

    # T-series not in map (T41-T52): default to residual (need individual assessment)
    if series == "T":
        return ("residual", None)

    # AX and M series: default to gap (uncalibrated Gen-1)
    if series in AX_M_SERIES:
        return ("gap", None)

    # CROSS-series and others: default to active (cross-framework templates)
    # These are organizational/structural templates
    return ("active", None)


def extract_maturity(data: Dict[str, Any]) -> str:
    """
    Extract maturity level from template JSON.

    Checks 'overall_maturity', 'maturity', 'maturity_note' fields.
    Default: "speculative" if no maturity information found.
    """
    # Try overall_maturity first (most common)
    if "overall_maturity" in data:
        return str(data["overall_maturity"])

    # Fall back to maturity field
    if "maturity" in data:
        return str(data["maturity"])

    # Check causal links for maturity
    if "causal_links" in data and isinstance(data["causal_links"], list):
        maturities = []
        for link in data["causal_links"]:
            if isinstance(link, dict) and "maturity" in link:
                maturities.append(link["maturity"])
        if maturities:
            # Return the most common or first
            return maturities[0]

    return "speculative"


def extract_calibration_status(data: Dict[str, Any]) -> str:
    """
    Extract calibration status from template JSON.

    Checks 'calibration_status', 'calibration_data', 'calibration_parameters' fields.
    Default: "uncalibrated" if no calibration information found.
    """
    # Direct field
    if "calibration_status" in data:
        status = str(data["calibration_status"])
        # Normalize values
        if "substantial" in status.lower():
            return "substantial"
        elif "partial" in status.lower() or "deepened" in status.lower():
            return "partial"
        elif "protocol" in status.lower():
            return "protocol"
        else:
            return status

    # Has calibration data = at least partial
    if "calibration_data" in data or "calibration_parameters" in data:
        return "partial"

    # Check if template has calibration_panel
    if "calibration_panel" in data:
        return "partial"

    return "uncalibrated"


def extract_ecological_validation(data: Dict[str, Any]) -> bool:
    """
    Extract ecological validation status.

    Default: False
    """
    if "ecological_validation" in data:
        return bool(data["ecological_validation"])

    # Check maturity for ecological evidence
    maturity = extract_maturity(data).lower()
    if "validated" in maturity or "ecological" in maturity:
        return True

    return False


def extract_source_docs(data: Dict[str, Any]) -> str:
    """
    Extract source document numbers from template.

    Returns comma-separated doc numbers, e.g. "55,58,65"
    Default: empty string if no source docs found.
    """
    if "source_docs" in data:
        docs = data["source_docs"]
        if isinstance(docs, list):
            return ",".join(str(d) for d in docs)
        return str(docs)

    # Try to extract from source_panel
    if "source_panel" in data:
        panel = data["source_panel"]
        # Extract numbers from panel name like "55_Panel_CREA_I_Creative_Cognition_V1_0.md"
        match = re.match(r"^(\d+)", panel)
        if match:
            return match.group(1)

    # Try source_panel_doc
    if "source_panel_doc" in data:
        panel = data["source_panel_doc"]
        # Extract numbers from panel name like "02-15_20_Panel_V_Social_Brain_V1_0.md"
        match = re.search(r"_(\d+)_", panel)
        if match:
            return match.group(1)

    return ""


def extract_pe_contribution(data: Dict[str, Any]) -> str:
    """
    Extract PE contribution type.

    Default: "organizational" if not specified (per spec).
    """
    if "pe_contribution" in data:
        return str(data["pe_contribution"])

    # Infer from template content
    framework_ids = data.get("framework_ids", [])
    if "predictive_processing" in framework_ids:
        return "predictive"

    # Check causal links for bridging
    if "causal_links" in data and isinstance(data["causal_links"], list):
        for link in data["causal_links"]:
            if isinstance(link, dict):
                if link.get("bridging_quality") in ["strong", "moderate"]:
                    return "explanatory"

    return "organizational"


def extract_practical_accessibility(data: Dict[str, Any]) -> str:
    """
    Extract practical accessibility tier.

    Default: "B" if not specified (per spec).
    """
    if "practical_accessibility" in data:
        return str(data["practical_accessibility"]).upper()

    # Infer from inputs if present
    if "inputs_required" in data and isinstance(data["inputs_required"], list):
        accessibilities = []
        for inp in data["inputs_required"]:
            if isinstance(inp, dict) and "accessibility" in inp:
                accessibilities.append(inp["accessibility"])
        if accessibilities:
            # Return highest tier needed (worst case)
            tier_order = {"A": 0, "B": 1, "C": 2, "D": 3}
            highest = max(accessibilities, key=lambda x: tier_order.get(x.upper(), 1))
            return highest.upper()

    return "B"


def scan_template_file(json_path: Path) -> Optional[TemplateRecord]:
    """
    Scan a single template JSON file and create a TemplateRecord.

    Returns None if the file cannot be processed.
    """
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Failed to read {json_path}: {e}")
        return None

    # Required fields
    template_id = data.get("template_id")
    display_id = data.get("display_id")
    name = data.get("name")

    if not all([template_id, display_id, name]):
        logger.warning(
            f"Skipping {json_path}: missing required fields "
            f"(template_id={template_id}, display_id={display_id}, name={name})"
        )
        return None

    # Derived fields
    series = extract_series(display_id)
    generation = determine_generation(display_id, series)
    dedup_status, superseded_by = classify_dedup_status(display_id, series, generation)

    # Extracted fields with defaults
    maturity = extract_maturity(data)
    calibration_status = extract_calibration_status(data)
    ecological_validation = extract_ecological_validation(data)
    source_docs = extract_source_docs(data)
    pe_contribution = extract_pe_contribution(data)
    practical_accessibility = extract_practical_accessibility(data)

    # Build record
    return TemplateRecord(
        template_id=template_id,
        display_id=display_id,
        name=name,
        series=series,
        generation=generation,
        dedup_status=dedup_status,
        superseded_by=superseded_by,
        pe_contribution=pe_contribution,
        maturity=maturity,
        calibration_status=calibration_status,
        practical_accessibility=practical_accessibility,
        ecological_validation=ecological_validation,
        json_path=str(json_path.relative_to(json_path.parent.parent.parent)),
        source_docs=source_docs,
    )


def scan_templates(
    templates_dir: str = "data/templates",
    db_path: str = "ae.db",
    clear_existing: bool = True,
) -> List[TemplateRecord]:
    """
    Scan all template JSON files and populate the TemplateRecord table.

    Args:
        templates_dir: Path to the templates directory
        db_path: Path to the SQLite database
        clear_existing: Whether to clear existing records before inserting

    Returns:
        List of created TemplateRecord instances
    """
    # Resolve paths
    base_path = Path(__file__).parent.parent.parent
    templates_path = base_path / templates_dir
    db_full_path = base_path / db_path

    if not templates_path.exists():
        raise FileNotFoundError(f"Templates directory not found: {templates_path}")

    # Setup database
    engine = get_engine(str(db_full_path))
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Clear existing records if requested
        if clear_existing:
            session.query(TemplateRecord).delete()
            session.commit()

        # Scan all JSON files
        json_files = sorted(templates_path.glob("*.json"))
        logger.info(f"Found {len(json_files)} template JSON files")

        records = []
        for json_path in json_files:
            record = scan_template_file(json_path)
            if record:
                records.append(record)
                session.add(record)

        session.commit()
        logger.info(f"Inserted {len(records)} TemplateRecord entries")

        # Expunge records from session so they remain usable after close
        # First refresh all attributes, then make transient
        for record in records:
            session.refresh(record)
            session.expunge(record)
            make_transient(record)

        return records

    except Exception as e:
        session.rollback()
        logger.error(f"Failed to scan templates: {e}")
        raise
    finally:
        session.close()


def query_active_gen2_series(session, series: str) -> List[TemplateRecord]:
    """
    Query all active Gen-2 templates in a given series.

    Example: query_active_gen2_series(session, "CREA") returns CREA1-CREA4.
    """
    return (
        session.query(TemplateRecord)
        .filter(
            TemplateRecord.series == series,
            TemplateRecord.generation == 2,
            TemplateRecord.dedup_status == "active",
        )
        .order_by(TemplateRecord.display_id)
        .all()
    )


def query_by_dedup_status(session, status: str) -> List[TemplateRecord]:
    """Query all templates with a given dedup_status."""
    return (
        session.query(TemplateRecord)
        .filter(TemplateRecord.dedup_status == status)
        .order_by(TemplateRecord.display_id)
        .all()
    )


if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.INFO)

    # Run scanner
    try:
        records = scan_templates()
        print(f"\nSuccessfully scanned {len(records)} templates")

        # Summary statistics
        from collections import Counter

        status_counts = Counter(r.dedup_status for r in records)
        gen_counts = Counter(r.generation for r in records)
        series_counts = Counter(r.series for r in records)

        print(f"\nBy dedup_status:")
        for status, count in sorted(status_counts.items()):
            print(f"  {status}: {count}")

        print(f"\nBy generation:")
        for gen, count in sorted(gen_counts.items()):
            print(f"  Gen-{gen}: {count}")

        print(f"\nBy series (top 10):")
        for series, count in series_counts.most_common(10):
            print(f"  {series}: {count}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
