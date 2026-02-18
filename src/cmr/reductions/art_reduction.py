"""
ART (Attention Restoration Theory) Reduction to Template Mechanisms.

Sprint 12 Task 12.1: Reduce Kaplan (1995) ART constructs to CMR templates.

ART posits five core constructs that explain why natural environments restore
directed attention capacity:
1. Being Away - psychological/physical distance from routine demands
2. Fascination (soft) - effortless attention capture that allows rest
3. Fascination (hard) - intense engagement requiring directed attention
4. Extent - scope and coherence enabling sustained engagement
5. Compatibility - fit between environment and purposes

Each construct is reduced to template mechanisms with coverage fractions.
The irreducible residual captures what cannot be reduced to environmental features.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import json
from pathlib import Path

from src.cmr.models import ReductionClaim, get_session


@dataclass
class TemplateMappingEntry:
    """A single template mapping within a reduction."""
    template_id: str
    mechanism: str
    coverage: float  # 0-1: how much of construct this template explains
    channel: Optional[str] = None  # For templates with multiple channels


@dataclass
class ConstructReduction:
    """Complete reduction of a Tier 2 construct."""
    theory: str
    construct: str
    template_mappings: List[TemplateMappingEntry]
    total_coverage: float
    irreducible_residual: str
    confidence: str  # "high" | "moderate" | "low"
    notes: str = ""


# ART Reduction Definitions
# Based on Kaplan (1995), Kaplan & Kaplan (1989), and subsequent research

ART_REDUCTIONS: Dict[str, ConstructReduction] = {
    "Being_Away": ConstructReduction(
        theory="ART",
        construct="Being_Away",
        template_mappings=[
            TemplateMappingEntry(
                template_id="VIEW1",
                mechanism="Visual access to distant elements (Channel 3: depth/openness) creates psychological distance from immediate concerns",
                coverage=0.40,
                channel="3"
            ),
            TemplateMappingEntry(
                template_id="SC2",
                mechanism="Vista/prospect isovist expansion provides spatial refuge from routine environment",
                coverage=0.25,
            ),
            TemplateMappingEntry(
                template_id="VF3",
                mechanism="R_h ratio shift at threshold creates sense of entering different spatial realm",
                coverage=0.20,
            ),
        ],
        total_coverage=0.85,
        irreducible_residual="The intentional component — the person's active choice to disengage from routine mental demands. Environmental features can facilitate Being Away but cannot compel it. Also: temporal dimension (duration of disengagement) not captured by spatial metrics.",
        confidence="moderate",
        notes="Strong evidence for VIEW1 contribution (Ulrich 1984, 1991). SC2/VF3 contributions inferred from spatial perception literature."
    ),

    "Fascination_Soft": ConstructReduction(
        theory="ART",
        construct="Fascination_Soft",
        template_mappings=[
            TemplateMappingEntry(
                template_id="VIEW1",
                mechanism="Soft fascination weight in VQI computation (Channel 3) - natural content captures attention without cognitive effort",
                coverage=0.45,
                channel="3"
            ),
            TemplateMappingEntry(
                template_id="VF1",
                mechanism="Contour curvature at moderate complexity levels induces aesthetic engagement without effortful processing",
                coverage=0.30,
            ),
            TemplateMappingEntry(
                template_id="T1",
                mechanism="Auditory 1/f spectral matching in natural soundscapes (residual - gap template)",
                coverage=0.15,
            ),
        ],
        total_coverage=0.90,
        irreducible_residual="Individual differences in what constitutes 'fascinating' content. Prior experience, cultural background, and current mood modulate fascination response. The subjective quality of 'being drawn' cannot be fully captured by stimulus features.",
        confidence="high",
        notes="VIEW1 soft fascination well-supported by Kaplan's original work and subsequent replications. VF1 contribution supported by processing fluency literature."
    ),

    "Fascination_Hard": ConstructReduction(
        theory="ART",
        construct="Fascination_Hard",
        template_mappings=[
            TemplateMappingEntry(
                template_id="CREA2",
                mechanism="Disfluency pathway - moderate processing difficulty triggers deeper engagement",
                coverage=0.35,
            ),
            TemplateMappingEntry(
                template_id="VF2",
                mechanism="SCI (Spatial Complexity Index) scaling violation creates cognitive challenge that commands attention",
                coverage=0.25,
            ),
            TemplateMappingEntry(
                template_id="T11",
                mechanism="Noradrenergic exploration drive activation (residual - gap template)",
                coverage=0.10,
            ),
        ],
        total_coverage=0.70,
        irreducible_residual="Goal-directed interest not captured by environmental features. Hard fascination often tied to pursuit of personal goals (solving a puzzle, mastering a skill) that depend on individual motivation rather than environmental affordances.",
        confidence="moderate",
        notes="Hard fascination less central to restoration than soft fascination per Kaplan. CREA2 link based on processing fluency literature."
    ),

    "Extent": ConstructReduction(
        theory="ART",
        construct="Extent",
        template_mappings=[
            TemplateMappingEntry(
                template_id="SC1",
                mechanism="Spatial legibility provides coherent framework for extended exploration",
                coverage=0.25,
            ),
            TemplateMappingEntry(
                template_id="SC3",
                mechanism="Path topology supports scope - ability to imagine continued engagement",
                coverage=0.20,
            ),
            TemplateMappingEntry(
                template_id="SC4",
                mechanism="Wayfinding clarity enables exploration without cognitive load",
                coverage=0.15,
            ),
            TemplateMappingEntry(
                template_id="VIEW1",
                mechanism="Depth/openness channel (Channel 5) provides physical extent cues",
                coverage=0.20,
                channel="5"
            ),
        ],
        total_coverage=0.80,
        irreducible_residual="Conceptual extent vs physical extent. ART's 'extent' includes the sense that an environment is 'a whole other world' with its own rules and contents - a richness of meaning that transcends measurable spatial features. Also: the 'connectedness' component (elements relate to each other) is partially captured by legibility but not fully.",
        confidence="moderate",
        notes="Extent is the most abstract ART construct. Template coverage may underestimate actual mechanism coverage."
    ),

    "Compatibility": ConstructReduction(
        theory="ART",
        construct="Compatibility",
        template_mappings=[
            TemplateMappingEntry(
                template_id="SOC2",
                mechanism="Privacy-encounter match to current task/intention - environment supports what person wants to do",
                coverage=0.35,
            ),
            TemplateMappingEntry(
                template_id="CREA4",
                mechanism="Workspace-task match for cognitive work (where applicable)",
                coverage=0.25,
            ),
            TemplateMappingEntry(
                template_id="MAT1",
                mechanism="Thermal comfort match to activity level and preference",
                coverage=0.15,
            ),
        ],
        total_coverage=0.75,
        irreducible_residual="Fine-grained task specificity. Compatibility requires knowing what the person intends to DO in the environment, which varies infinitely. Templates capture common task categories but cannot address unique individual goals. Also: the 'required effort' dimension - even when supported, some goals require effort that may not be compatible with restoration.",
        confidence="moderate",
        notes="Compatibility is inherently person-task-environment specific. Template coverage is for common task categories."
    ),
}


def reduce_art_construct(construct: str) -> Optional[ConstructReduction]:
    """
    Get the template reduction for an ART construct.

    Args:
        construct: ART construct name (Being_Away, Fascination_Soft,
                   Fascination_Hard, Extent, Compatibility)

    Returns:
        ConstructReduction with template mappings and residual, or None if not found
    """
    # Normalize construct name
    normalized = construct.replace(" ", "_").replace("-", "_")
    return ART_REDUCTIONS.get(normalized)


def get_art_template_coverage(template_id: str) -> List[Dict[str, Any]]:
    """
    Reverse lookup: which ART constructs use this template?

    Args:
        template_id: Template display ID (e.g., "VIEW1", "SC2")

    Returns:
        List of {construct, mechanism, coverage} dicts
    """
    results = []
    for construct_name, reduction in ART_REDUCTIONS.items():
        for mapping in reduction.template_mappings:
            if mapping.template_id == template_id:
                results.append({
                    "construct": construct_name,
                    "mechanism": mapping.mechanism,
                    "coverage": mapping.coverage,
                    "channel": mapping.channel,
                })
    return results


def get_art_constructs() -> List[str]:
    """Get list of all ART constructs."""
    return list(ART_REDUCTIONS.keys())


def get_art_summary() -> Dict[str, Any]:
    """Get summary statistics for ART reduction."""
    all_templates = set()
    total_coverage = 0
    n_constructs = len(ART_REDUCTIONS)

    for reduction in ART_REDUCTIONS.values():
        for mapping in reduction.template_mappings:
            all_templates.add(mapping.template_id)
        total_coverage += reduction.total_coverage

    return {
        "theory": "ART",
        "n_constructs": n_constructs,
        "n_templates_used": len(all_templates),
        "templates_used": sorted(all_templates),
        "average_coverage": total_coverage / n_constructs,
        "constructs": list(ART_REDUCTIONS.keys()),
    }


def create_art_reduction_claims(session, staging_links_count: int = 1251) -> List[ReductionClaim]:
    """
    Create ReductionClaim DB records for all ART constructs.

    Args:
        session: SQLAlchemy session
        staging_links_count: Number of ART staging theory-links (default: 1,251)

    Returns:
        List of created ReductionClaim objects
    """
    claims = []
    links_per_construct = staging_links_count // len(ART_REDUCTIONS)

    for construct_name, reduction in ART_REDUCTIONS.items():
        # Convert template mappings to JSON-serializable format
        mappings_json = [
            {
                "template_id": m.template_id,
                "mechanism": m.mechanism,
                "coverage": m.coverage,
                "channel": m.channel,
            }
            for m in reduction.template_mappings
        ]

        claim = ReductionClaim(
            tier2_theory="ART",
            tier2_construct=construct_name,
            reduction_type="partial",  # All have irreducible residual
            template_mappings=mappings_json,
            irreducible_residual=reduction.irreducible_residual,
            confidence=reduction.confidence,
            source_panel="T2-A",  # ART reduction panel
            staging_links_reconciled=links_per_construct,
            staging_links_total=links_per_construct,
        )
        session.add(claim)
        claims.append(claim)

    session.commit()
    return claims


def export_art_reductions_json(output_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Export ART reductions to JSON format.

    Args:
        output_path: If provided, write JSON to this path

    Returns:
        The JSON-serializable reduction data
    """
    data = {
        "theory": "ART",
        "full_name": "Attention Restoration Theory",
        "source": "Kaplan (1995); Kaplan & Kaplan (1989)",
        "constructs": {}
    }

    for construct_name, reduction in ART_REDUCTIONS.items():
        data["constructs"][construct_name] = {
            "template_mappings": [
                {
                    "template_id": m.template_id,
                    "mechanism": m.mechanism,
                    "coverage": m.coverage,
                    "channel": m.channel,
                }
                for m in reduction.template_mappings
            ],
            "total_coverage": reduction.total_coverage,
            "irreducible_residual": reduction.irreducible_residual,
            "confidence": reduction.confidence,
            "notes": reduction.notes,
        }

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)

    return data
