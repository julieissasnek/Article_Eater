"""
Biophilia Reduction to Template Mechanisms.

Sprint 12 Task 12.3: Reduce Wilson (1984) and Kellert (2005) Biophilia constructs.

Biophilia posits innate human affiliation with nature, organized into pattern groups:
1. Nature in the Space - direct experience of nature
2. Natural Analogues - indirect nature references (materials, patterns)
3. Nature of the Space - spatial configurations evoking natural settings
4. Remaining patterns - specific biophilic elements

Each construct is reduced to template mechanisms with coverage fractions.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json
from pathlib import Path

from src.cmr.models import ReductionClaim


@dataclass
class TemplateMappingEntry:
    template_id: str
    mechanism: str
    coverage: float
    channel: Optional[str] = None


@dataclass
class ConstructReduction:
    theory: str
    construct: str
    template_mappings: List[TemplateMappingEntry]
    total_coverage: float
    irreducible_residual: str
    confidence: str
    notes: str = ""


BIOPHILIA_REDUCTIONS: Dict[str, ConstructReduction] = {
    "Nature_In_Space": ConstructReduction(
        theory="Biophilia",
        construct="Nature_In_Space",
        template_mappings=[
            TemplateMappingEntry(
                template_id="VIEW1",
                mechanism="Visual connection to nature - VQI channels 1-3 capture nature presence, content, and quality",
                coverage=0.50,
                channel="1-3"
            ),
            TemplateMappingEntry(
                template_id="OLF1",
                mechanism="Non-visual connection through olfactory pathway - natural scents",
                coverage=0.20,
            ),
            TemplateMappingEntry(
                template_id="MAT4",
                mechanism="Natural materials provide tactile nature connection",
                coverage=0.20,
            ),
        ],
        total_coverage=0.90,
        irreducible_residual="Dynamic sensory variability - living nature changes moment-to-moment in ways static features cannot capture. Also: multi-sensory integration effects beyond single-channel contributions.",
        confidence="high",
        notes="Core biophilic pattern with strong evidence base. VIEW1 is primary mechanism."
    ),

    "Natural_Analogues": ConstructReduction(
        theory="Biophilia",
        construct="Natural_Analogues",
        template_mappings=[
            TemplateMappingEntry(
                template_id="VF1",
                mechanism="Biomorphic forms and patterns - curved contours mimic natural forms",
                coverage=0.30,
            ),
            TemplateMappingEntry(
                template_id="VF2",
                mechanism="Fractal scaling (SCI) - self-similar patterns across scales",
                coverage=0.25,
            ),
            TemplateMappingEntry(
                template_id="MAT2",
                mechanism="Natural materials mimicry in surface patterns",
                coverage=0.15,
            ),
            TemplateMappingEntry(
                template_id="MAT4",
                mechanism="Authentic natural materials (wood, stone) as analogue",
                coverage=0.15,
            ),
        ],
        total_coverage=0.85,
        irreducible_residual="Symbolic/metaphorical nature references that operate through cultural meaning rather than perceptual features. Art, images, and representational content cannot be reduced to geometric properties.",
        confidence="moderate",
        notes="Browning et al. (2014) 14 Patterns framework. VF1/VF2 capture geometric analogues."
    ),

    "Nature_Of_Space": ConstructReduction(
        theory="Biophilia",
        construct="Nature_Of_Space",
        template_mappings=[
            TemplateMappingEntry(
                template_id="SC2",
                mechanism="Prospect - open views evoking savanna/landscape vistas",
                coverage=0.25,
            ),
            TemplateMappingEntry(
                template_id="T2",
                mechanism="Refuge - enclosed spaces evoking cave/den safety (gap template)",
                coverage=0.15,
            ),
            TemplateMappingEntry(
                template_id="VF3",
                mechanism="Spatial ratios (R_h) creating nature-like proportions",
                coverage=0.15,
            ),
            TemplateMappingEntry(
                template_id="SC3",
                mechanism="Mystery - partially obscured views inviting exploration",
                coverage=0.15,
            ),
            TemplateMappingEntry(
                template_id="T5",
                mechanism="Risk/peril - controlled exposure to depth/height (gap template)",
                coverage=0.10,
            ),
        ],
        total_coverage=0.80,
        irreducible_residual="Evolutionary habitat preferences that may not manifest consistently across cultures or individuals. The 'savanna hypothesis' is debated; actual preference patterns may be more complex than prospect-refuge model suggests.",
        confidence="moderate",
        notes="Appleton (1975) prospect-refuge theory. SC2 well-supported; T2/T5 are gaps."
    ),

    "Remaining_Patterns": ConstructReduction(
        theory="Biophilia",
        construct="Remaining_Patterns",
        template_mappings=[
            TemplateMappingEntry(
                template_id="MAT1",
                mechanism="Thermal variability - natural environments have thermal gradients",
                coverage=0.25,
            ),
            TemplateMappingEntry(
                template_id="L5",
                mechanism="Dynamic and diffuse light - mimicking natural daylight variation",
                coverage=0.25,
            ),
            TemplateMappingEntry(
                template_id="TP4",
                mechanism="Connection with natural systems - circadian-aligned lighting",
                coverage=0.20,
            ),
        ],
        total_coverage=0.70,
        irreducible_residual="Several biophilic patterns (e.g., presence of water, biodiversity) lack dedicated templates. These require future development or remain as documented gaps.",
        confidence="moderate",
        notes="Captures remaining Kellert/Browning patterns not in primary categories."
    ),
}


def reduce_biophilia_construct(construct: str) -> Optional[ConstructReduction]:
    normalized = construct.replace(" ", "_").replace("-", "_")
    return BIOPHILIA_REDUCTIONS.get(normalized)


def get_biophilia_template_coverage(template_id: str) -> List[Dict[str, Any]]:
    results = []
    for construct_name, reduction in BIOPHILIA_REDUCTIONS.items():
        for mapping in reduction.template_mappings:
            if mapping.template_id == template_id:
                results.append({
                    "construct": construct_name,
                    "mechanism": mapping.mechanism,
                    "coverage": mapping.coverage,
                    "channel": mapping.channel,
                })
    return results


def get_biophilia_constructs() -> List[str]:
    return list(BIOPHILIA_REDUCTIONS.keys())


def get_biophilia_summary() -> Dict[str, Any]:
    all_templates = set()
    total_coverage = 0
    n_constructs = len(BIOPHILIA_REDUCTIONS)
    for reduction in BIOPHILIA_REDUCTIONS.values():
        for mapping in reduction.template_mappings:
            all_templates.add(mapping.template_id)
        total_coverage += reduction.total_coverage
    return {
        "theory": "Biophilia",
        "n_constructs": n_constructs,
        "n_templates_used": len(all_templates),
        "templates_used": sorted(all_templates),
        "average_coverage": total_coverage / n_constructs,
        "constructs": list(BIOPHILIA_REDUCTIONS.keys()),
    }


def create_biophilia_reduction_claims(session, staging_links_count: int = 102) -> List[ReductionClaim]:
    claims = []
    links_per_construct = staging_links_count // len(BIOPHILIA_REDUCTIONS)
    for construct_name, reduction in BIOPHILIA_REDUCTIONS.items():
        mappings_json = [
            {"template_id": m.template_id, "mechanism": m.mechanism, "coverage": m.coverage, "channel": m.channel}
            for m in reduction.template_mappings
        ]
        claim = ReductionClaim(
            tier2_theory="Biophilia",
            tier2_construct=construct_name,
            reduction_type="partial",
            template_mappings=mappings_json,
            irreducible_residual=reduction.irreducible_residual,
            confidence=reduction.confidence,
            source_panel="T2-B",
            staging_links_reconciled=links_per_construct,
            staging_links_total=links_per_construct,
        )
        session.add(claim)
        claims.append(claim)
    session.commit()
    return claims


def export_biophilia_reductions_json(output_path: Optional[Path] = None) -> Dict[str, Any]:
    data = {
        "theory": "Biophilia",
        "full_name": "Biophilia Hypothesis",
        "source": "Wilson (1984); Kellert (2005); Browning et al. (2014)",
        "constructs": {}
    }
    for construct_name, reduction in BIOPHILIA_REDUCTIONS.items():
        data["constructs"][construct_name] = {
            "template_mappings": [
                {"template_id": m.template_id, "mechanism": m.mechanism, "coverage": m.coverage, "channel": m.channel}
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
