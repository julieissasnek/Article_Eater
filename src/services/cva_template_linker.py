"""
cva_template_linker.py — Template ↔ CVA Linking Service
=========================================================

Annotates existing discovery templates with CVA constraint and valuation tags.
Links templates to CVA molecules and maps their predictions to the 14D
constraint space and cultural valuation variants.

Reference: Post-remediation task — Template ↔ CVA Linking
ADR-001: Extension layer — new file, no existing code modified.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

LOGGER = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────
# Template → CVA Constraint Mappings
# ──────────────────────────────────────────────────────────────────

# Which Tier 2 constraints each discovery template primarily predicts about
TEMPLATE_CONSTRAINT_TAGS: Dict[str, List[str]] = {
    # Environmental preference templates
    "T1_affordance_density": ["affordance_density", "control_efficacy"],
    "T2_complexity_preference": ["processing_cost", "prediction_error", "load_rate"],
    "T3_restoration_attention": ["processing_cost", "load_rate", "multisensory_coherence"],
    "T4_prospect_refuge": ["control_efficacy", "prediction_error"],
    "T5_fascination_soft": ["prediction_error", "affordance_density", "processing_cost"],

    # Social / cultural templates
    "T6_social_density": ["social_cue_density", "narrative_coherence"],
    "T7_identity_place": ["narrative_coherence", "control_efficacy"],
    "T8_cultural_meaning": ["narrative_coherence", "social_cue_density"],

    # Safety / danger templates
    "T9_perceived_safety": ["prediction_error", "control_efficacy"],
    "T10_legibility_wayfinding": ["prediction_error", "affordance_density"],

    # Aesthetics / beauty
    "T11_beauty_order": ["multisensory_coherence", "processing_cost"],
    "T12_beauty_complexity": ["prediction_error", "processing_cost", "multisensory_coherence"],
}

# Which valuation axes each template primarily relates to
TEMPLATE_VALUATION_TAGS: Dict[str, List[str]] = {
    "T1_affordance_density": ["AutonomySupportValue", "CompetenceSupportValue"],
    "T2_complexity_preference": ["InterestValue", "RestorationValue"],
    "T3_restoration_attention": ["RestorationValue", "SafetyValue"],
    "T4_prospect_refuge": ["SafetyValue", "AutonomySupportValue"],
    "T5_fascination_soft": ["InterestValue", "RestorationValue"],
    "T6_social_density": ["BelongingValue", "RelatednessSupportValue"],
    "T7_identity_place": ["IdentityCongruenceValue", "BelongingValue"],
    "T8_cultural_meaning": ["IdentityCongruenceValue", "StatusValue"],
    "T9_perceived_safety": ["SafetyValue"],
    "T10_legibility_wayfinding": ["SafetyValue", "CompetenceSupportValue"],
    "T11_beauty_order": ["InterestValue"],
    "T12_beauty_complexity": ["InterestValue"],
}

# Template → Molecule links
TEMPLATE_MOLECULE_LINKS: Dict[str, List[str]] = {
    "T4_prospect_refuge": ["M_CCT_PREFERENCE"],
    "T5_fascination_soft": ["M_BEAUTY_COMPRESSION"],
    "T8_cultural_meaning": ["M_CULTURAL_VALUATION", "M_RASA"],
    "T11_beauty_order": ["M_BEAUTY_COMPRESSION"],
    "T12_beauty_complexity": ["M_BEAUTY_COMPRESSION", "M_ATTRACTOR_TRANSITION"],
}


@dataclass
class TemplateCVALink:
    """CVA annotation for a single template."""
    template_id: str
    constraint_tags: List[str]
    valuation_tags: List[str]
    molecule_links: List[str]
    activity_frames: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "template_id": self.template_id,
            "constraint_tags": self.constraint_tags,
            "valuation_tags": self.valuation_tags,
            "molecule_links": self.molecule_links,
            "activity_frames": self.activity_frames,
        }


class CVATemplateLinker:
    """Links discovery templates to CVA constraint/valuation tags and molecules."""

    def __init__(
        self,
        constraint_tags: Optional[Dict[str, List[str]]] = None,
        valuation_tags: Optional[Dict[str, List[str]]] = None,
        molecule_links: Optional[Dict[str, List[str]]] = None,
    ):
        self.constraint_tags = constraint_tags or TEMPLATE_CONSTRAINT_TAGS
        self.valuation_tags = valuation_tags or TEMPLATE_VALUATION_TAGS
        self.molecule_links = molecule_links or TEMPLATE_MOLECULE_LINKS

    def link_template(self, template_id: str) -> TemplateCVALink:
        """Get CVA links for a single template."""
        return TemplateCVALink(
            template_id=template_id,
            constraint_tags=self.constraint_tags.get(template_id, []),
            valuation_tags=self.valuation_tags.get(template_id, []),
            molecule_links=self.molecule_links.get(template_id, []),
        )

    def link_all_templates(self) -> List[TemplateCVALink]:
        """Get CVA links for all known templates."""
        all_ids = set(self.constraint_tags.keys()) | set(self.valuation_tags.keys())
        return [self.link_template(tid) for tid in sorted(all_ids)]

    def export_links(self, output_path: str) -> int:
        """Export all template-CVA links to JSON file."""
        links = self.link_all_templates()
        data = {
            "template_cva_links": [l.to_dict() for l in links],
            "total_templates": len(links),
            "total_constraint_tags": sum(len(l.constraint_tags) for l in links),
            "total_valuation_tags": sum(len(l.valuation_tags) for l in links),
            "total_molecule_links": sum(len(l.molecule_links) for l in links),
        }
        Path(output_path).write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        LOGGER.info(
            "Exported %d template-CVA links to %s", len(links), output_path
        )
        return len(links)

    def get_templates_for_constraint(self, constraint_name: str) -> List[str]:
        """Find all templates that predict about a given constraint."""
        return [
            tid for tid, tags in self.constraint_tags.items()
            if constraint_name in tags
        ]

    def get_templates_for_valuation(self, valuation_name: str) -> List[str]:
        """Find all templates that relate to a given valuation axis."""
        return [
            tid for tid, tags in self.valuation_tags.items()
            if valuation_name in tags
        ]

    def coverage_report(self) -> Dict:
        """Generate a coverage report: which constraints/valuations have templates."""
        all_constraints = [
            "prediction_error", "processing_cost", "load_rate",
            "control_efficacy", "multisensory_coherence", "affordance_density",
            "social_cue_density", "narrative_coherence",
        ]
        all_valuations = [
            "SafetyValue", "InterestValue", "RestorationValue",
            "StatusValue", "BelongingValue", "IdentityCongruenceValue",
            "AutonomySupportValue", "CompetenceSupportValue",
            "RelatednessSupportValue",
        ]

        constraint_coverage = {
            c: len(self.get_templates_for_constraint(c))
            for c in all_constraints
        }
        valuation_coverage = {
            v: len(self.get_templates_for_valuation(v))
            for v in all_valuations
        }

        return {
            "constraint_coverage": constraint_coverage,
            "valuation_coverage": valuation_coverage,
            "uncovered_constraints": [c for c, n in constraint_coverage.items() if n == 0],
            "uncovered_valuations": [v for v, n in valuation_coverage.items() if n == 0],
        }
