"""
SRT (Stress Recovery Theory) Reduction to Template Mechanisms.

Sprint 12 Task 12.2: Reduce Ulrich (1983, 1991) SRT constructs to CMR templates.

SRT posits that natural environments promote recovery from stress through
three primary mechanisms:
1. Autonomic stress reduction - physiological calming via parasympathetic activation
2. Affective response - immediate positive emotional reaction to environmental features
3. Approach/avoidance - behavioral tendencies based on evolutionary threat/safety cues

Each construct is reduced to template mechanisms with coverage fractions.
The irreducible residual captures what cannot be reduced to environmental features.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json
from pathlib import Path

from src.cmr.models import ReductionClaim


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


# SRT Reduction Definitions
# Based on Ulrich (1983, 1991), Ulrich et al. (1991)

SRT_REDUCTIONS: Dict[str, ConstructReduction] = {
    "Autonomic_Stress_Reduction": ConstructReduction(
        theory="SRT",
        construct="Autonomic_Stress_Reduction",
        template_mappings=[
            TemplateMappingEntry(
                template_id="VIEW1",
                mechanism="Visual access to natural content (Channels 1-2: nature presence, biomorphic elements) triggers parasympathetic nervous system activation",
                coverage=0.30,
                channel="1-2"
            ),
            TemplateMappingEntry(
                template_id="MAT4",
                mechanism="Wood and natural materials reduce sympathetic arousal via warmth/naturalness perception",
                coverage=0.20,
            ),
            TemplateMappingEntry(
                template_id="T6",
                mechanism="Cortisol pathway modulation (gap template - mechanism known but not fully calibrated)",
                coverage=0.10,
            ),
            TemplateMappingEntry(
                template_id="L4",
                mechanism="Warm CCT (correlated color temperature) promotes relaxation and reduced cortisol",
                coverage=0.10,
            ),
        ],
        total_coverage=0.70,
        irreducible_residual="Speed of recovery varies by individual and pre-existing stress level. Temporal dynamics of physiological response (onset latency, recovery curve shape) not captured by spatial features. Also: individual differences in baseline autonomic tone and stress reactivity.",
        confidence="moderate",
        notes="Core SRT mechanism well-supported by Ulrich et al. (1991) surgical recovery study and subsequent replications. Fich et al. (2014) provides strongest CNFA evidence."
    ),

    "Affective_Response": ConstructReduction(
        theory="SRT",
        construct="Affective_Response",
        template_mappings=[
            TemplateMappingEntry(
                template_id="VF1",
                mechanism="Contour curvature preference - curved forms elicit positive affect via processing fluency",
                coverage=0.30,
            ),
            TemplateMappingEntry(
                template_id="COL1",
                mechanism="Color-affect mapping - certain hues/saturations linked to immediate affective response",
                coverage=0.20,
            ),
            TemplateMappingEntry(
                template_id="OLF1",
                mechanism="Olfactory hedonic response - natural scents (wood, plants) trigger positive valence",
                coverage=0.15,
            ),
        ],
        total_coverage=0.65,
        irreducible_residual="Pre-attentive evaluation component - SRT posits affective response occurs before conscious perception. This rapid appraisal pathway cannot be fully captured by static environmental features. Also: individual differences in affective temperament and current mood state.",
        confidence="moderate",
        notes="Affective response is the most immediate SRT mechanism. Links to IAPS research on emotional images. VF1 contribution supported by Bar & Neta (2006) contour preference findings."
    ),

    "Approach_Avoidance": ConstructReduction(
        theory="SRT",
        construct="Approach_Avoidance",
        template_mappings=[
            TemplateMappingEntry(
                template_id="SC2",
                mechanism="Prospect (vista/outlook) triggers approach behavior via evolutionary safety signal",
                coverage=0.30,
            ),
            TemplateMappingEntry(
                template_id="T5",
                mechanism="Threat perception pathway (residual - gap template) - detection of threat cues triggers avoidance",
                coverage=0.15,
            ),
            TemplateMappingEntry(
                template_id="T2",
                mechanism="Refuge/safety perception (residual - gap template) - enclosure cues enable approach",
                coverage=0.15,
            ),
        ],
        total_coverage=0.60,
        irreducible_residual="Phylogenetic threat detection cannot be fully reduced to spatial features. Evolutionary psychology posits rapid, pre-conscious detection of ancestrally-relevant threats (snakes, spiders, heights, darkness) that operates through specialized neural circuits. Also: individual differences in threat sensitivity (e.g., anxiety disorders).",
        confidence="low",
        notes="Approach/avoidance has weakest evidence base of SRT constructs. T2 and T5 are gap templates requiring future calibration. SC2 prospect-refuge link better supported."
    ),
}


def reduce_srt_construct(construct: str) -> Optional[ConstructReduction]:
    """
    Get the template reduction for an SRT construct.

    Args:
        construct: SRT construct name (Autonomic_Stress_Reduction,
                   Affective_Response, Approach_Avoidance)

    Returns:
        ConstructReduction with template mappings and residual, or None if not found
    """
    # Normalize construct name
    normalized = construct.replace(" ", "_").replace("-", "_")
    return SRT_REDUCTIONS.get(normalized)


def get_srt_template_coverage(template_id: str) -> List[Dict[str, Any]]:
    """
    Reverse lookup: which SRT constructs use this template?

    Args:
        template_id: Template display ID (e.g., "VIEW1", "MAT4")

    Returns:
        List of {construct, mechanism, coverage} dicts
    """
    results = []
    for construct_name, reduction in SRT_REDUCTIONS.items():
        for mapping in reduction.template_mappings:
            if mapping.template_id == template_id:
                results.append({
                    "construct": construct_name,
                    "mechanism": mapping.mechanism,
                    "coverage": mapping.coverage,
                    "channel": mapping.channel,
                })
    return results


def get_srt_constructs() -> List[str]:
    """Get list of all SRT constructs."""
    return list(SRT_REDUCTIONS.keys())


def get_srt_summary() -> Dict[str, Any]:
    """Get summary statistics for SRT reduction."""
    all_templates = set()
    total_coverage = 0
    n_constructs = len(SRT_REDUCTIONS)

    for reduction in SRT_REDUCTIONS.values():
        for mapping in reduction.template_mappings:
            all_templates.add(mapping.template_id)
        total_coverage += reduction.total_coverage

    return {
        "theory": "SRT",
        "n_constructs": n_constructs,
        "n_templates_used": len(all_templates),
        "templates_used": sorted(all_templates),
        "average_coverage": total_coverage / n_constructs,
        "constructs": list(SRT_REDUCTIONS.keys()),
    }


def create_srt_reduction_claims(session, staging_links_count: int = 3) -> List[ReductionClaim]:
    """
    Create ReductionClaim DB records for all SRT constructs.

    Args:
        session: SQLAlchemy session
        staging_links_count: Number of SRT staging theory-links (default: 3)

    Returns:
        List of created ReductionClaim objects
    """
    claims = []
    links_per_construct = max(1, staging_links_count // len(SRT_REDUCTIONS))

    for construct_name, reduction in SRT_REDUCTIONS.items():
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
            tier2_theory="SRT",
            tier2_construct=construct_name,
            reduction_type="partial",  # All have irreducible residual
            template_mappings=mappings_json,
            irreducible_residual=reduction.irreducible_residual,
            confidence=reduction.confidence,
            source_panel="T2-S",  # SRT reduction panel
            staging_links_reconciled=links_per_construct,
            staging_links_total=links_per_construct,
        )
        session.add(claim)
        claims.append(claim)

    session.commit()
    return claims


def export_srt_reductions_json(output_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Export SRT reductions to JSON format.

    Args:
        output_path: If provided, write JSON to this path

    Returns:
        The JSON-serializable reduction data
    """
    data = {
        "theory": "SRT",
        "full_name": "Stress Recovery Theory",
        "source": "Ulrich (1983, 1991); Ulrich et al. (1991)",
        "constructs": {}
    }

    for construct_name, reduction in SRT_REDUCTIONS.items():
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
