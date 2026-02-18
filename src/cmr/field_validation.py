"""
Field Validation Protocol Generator (Sprint 13 Task 13.10).

Given a template_id, generates a field study protocol including:
- Prediction to test
- Study design (type, N, IV manipulation, DV measures, controls, duration)
- Measurements needed with tier
- Success criteria
- Estimated cost/duration
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional
import json

from src.cmr.models import TemplateRecord, get_session


class StudyDesignType(str, Enum):
    """Types of field study designs."""
    WITHIN_SUBJECTS = "within_subjects"  # Same participants, multiple conditions
    BETWEEN_SUBJECTS = "between_subjects"  # Different participant groups
    MIXED_DESIGN = "mixed_design"  # Both within and between factors
    QUASI_EXPERIMENTAL = "quasi_experimental"  # Non-random assignment
    LONGITUDINAL = "longitudinal"  # Track over time
    CROSS_SECTIONAL = "cross_sectional"  # Single time point comparison


class MeasurementTier(str, Enum):
    """Measurement accessibility tiers."""
    A = "A"  # Easy: visual inspection, basic questionnaires
    B = "B"  # Moderate: basic instruments (lux meter, sound meter)
    C = "C"  # Specialized: advanced instruments (spectrometer, HRV monitor)
    D = "D"  # Expert: lab equipment (fMRI, cortisol assay)


@dataclass
class DVMeasure:
    """Dependent variable measurement specification."""
    name: str
    instrument: str
    tier: MeasurementTier
    frequency: str  # "single", "pre_post", "continuous", "daily"
    estimated_cost_usd: float
    notes: str = ""


@dataclass
class Control:
    """Control variable specification."""
    name: str
    method: str  # "match", "measure_covary", "randomize", "stratify"
    critical: bool = True


@dataclass
class FieldStudyProtocol:
    """Complete field study protocol for template validation."""
    template_id: str
    template_name: str
    prediction: str
    study_design: StudyDesignType
    sample_n: int
    sample_justification: str
    iv_manipulation: str
    dv_measures: list[DVMeasure]
    controls: list[Control]
    duration_weeks: int
    success_criteria: list[str]
    estimated_total_cost_usd: float
    cost_breakdown: dict[str, float]
    ethical_considerations: list[str]
    practical_notes: list[str]
    generated_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "template_id": self.template_id,
            "template_name": self.template_name,
            "prediction": self.prediction,
            "study_design": self.study_design.value,
            "sample_n": self.sample_n,
            "sample_justification": self.sample_justification,
            "iv_manipulation": self.iv_manipulation,
            "dv_measures": [
                {
                    "name": m.name,
                    "instrument": m.instrument,
                    "tier": m.tier.value,
                    "frequency": m.frequency,
                    "estimated_cost_usd": m.estimated_cost_usd,
                    "notes": m.notes,
                }
                for m in self.dv_measures
            ],
            "controls": [
                {"name": c.name, "method": c.method, "critical": c.critical}
                for c in self.controls
            ],
            "duration_weeks": self.duration_weeks,
            "success_criteria": self.success_criteria,
            "estimated_total_cost_usd": self.estimated_total_cost_usd,
            "cost_breakdown": self.cost_breakdown,
            "ethical_considerations": self.ethical_considerations,
            "practical_notes": self.practical_notes,
            "generated_at": self.generated_at.isoformat(),
        }


# Template-specific protocol generators
PROTOCOL_GENERATORS: dict[str, callable] = {}


def _register_generator(template_id: str):
    """Decorator to register a protocol generator for a template."""
    def decorator(func):
        PROTOCOL_GENERATORS[template_id.upper()] = func
        return func
    return decorator


@_register_generator("L2")
def _generate_l2_protocol() -> FieldStudyProtocol:
    """Generate protocol for L2 (Circadian Architectural Regulation)."""
    return FieldStudyProtocol(
        template_id="L2",
        template_name="Circadian Architectural Regulation via Non-Visual Photoreception",
        prediction="Buildings with higher melanopic daylight availability (mEDI > 250 lux for 4+ hours morning) will produce better circadian alignment (DLMO timing, sleep quality) than buildings with poor daylight access.",
        study_design=StudyDesignType.QUASI_EXPERIMENTAL,
        sample_n=60,
        sample_justification="Power analysis for d=0.5 effect, α=0.05, power=0.80, accounting for 20% attrition in 2-week protocol",
        iv_manipulation="Compare occupants in high vs. low daylight offices (matched for work type). IV = morning mEDI exposure (measured via wearable spectroradiometer).",
        dv_measures=[
            DVMeasure(
                name="Circadian phase (DLMO)",
                instrument="Salivary melatonin ELISA (5-point evening protocol)",
                tier=MeasurementTier.D,
                frequency="pre_post",
                estimated_cost_usd=3000,
                notes="Gold standard but expensive; consider dim-light protocol"
            ),
            DVMeasure(
                name="Sleep quality",
                instrument="Pittsburgh Sleep Quality Index (PSQI)",
                tier=MeasurementTier.A,
                frequency="pre_post",
                estimated_cost_usd=0,
                notes="Validated questionnaire, free"
            ),
            DVMeasure(
                name="Objective sleep",
                instrument="Actigraphy (wrist-worn)",
                tier=MeasurementTier.C,
                frequency="continuous",
                estimated_cost_usd=2500,
                notes="2-week wear protocol; analyze sleep onset/offset, efficiency"
            ),
            DVMeasure(
                name="Daytime alertness",
                instrument="Karolinska Sleepiness Scale (KSS)",
                tier=MeasurementTier.A,
                frequency="daily",
                estimated_cost_usd=0,
                notes="3x daily sampling (morning, afternoon, evening)"
            ),
            DVMeasure(
                name="Light exposure",
                instrument="Wearable spectroradiometer (Daysimeter/ActLumus)",
                tier=MeasurementTier.C,
                frequency="continuous",
                estimated_cost_usd=3500,
                notes="Essential for quantifying actual exposure; calculate CS/mEDI"
            ),
        ],
        controls=[
            Control("Chronotype", "measure_covary", True),
            Control("Season", "stratify", True),
            Control("Work schedule", "match", True),
            Control("Home light environment", "measure_covary", False),
            Control("Caffeine/alcohol", "measure_covary", False),
        ],
        duration_weeks=4,
        success_criteria=[
            "DLMO phase difference ≥30 min between groups",
            "PSQI score difference ≥1.5 points",
            "Sleep efficiency difference ≥5% from actigraphy",
            "Significant correlation between mEDI exposure and DLMO timing (r > 0.4)",
        ],
        estimated_total_cost_usd=15000,
        cost_breakdown={
            "melatonin_assays": 3000,
            "actigraphy_devices": 2500,
            "light_sensors": 3500,
            "participant_compensation": 3000,
            "analysis_software": 1500,
            "personnel_time": 1500,
        },
        ethical_considerations=[
            "Minimal intervention (observational)",
            "Wearable devices are non-invasive",
            "Saliva collection requires informed consent",
            "No deception involved",
        ],
        practical_notes=[
            "Partner with buildings of varying daylight quality",
            "Recruit during spring/fall to control seasonal effects",
            "Ensure participants have stable work schedules",
            "Consider remote monitoring to reduce burden",
        ],
    )


@_register_generator("VF3")
def _generate_vf3_protocol() -> FieldStudyProtocol:
    """Generate protocol for VF3 (Ceiling Height R_h ratio)."""
    return FieldStudyProtocol(
        template_id="VF3",
        template_name="Ceiling Height and Cognitive Mode (R_h Ratio)",
        prediction="Rooms with higher R_h (ceiling height / √floor area > 0.5) will produce better performance on abstract/creative tasks, while lower R_h rooms (<0.3) will produce better performance on detail-oriented tasks.",
        study_design=StudyDesignType.WITHIN_SUBJECTS,
        sample_n=48,
        sample_justification="Power analysis for d=0.4 effect in within-subjects design, α=0.05, power=0.80",
        iv_manipulation="Participants complete cognitive tasks in two rooms: High R_h (3.2m ceiling, 25m² = R_h 0.64) vs. Low R_h (2.4m ceiling, 25m² = R_h 0.48). Counterbalanced order.",
        dv_measures=[
            DVMeasure(
                name="Abstract processing",
                instrument="Remote Associates Test (RAT)",
                tier=MeasurementTier.A,
                frequency="single",
                estimated_cost_usd=0,
                notes="10 items per condition; validated for creative insight"
            ),
            DVMeasure(
                name="Detail-oriented processing",
                instrument="Proofreading task (error detection)",
                tier=MeasurementTier.A,
                frequency="single",
                estimated_cost_usd=0,
                notes="Standardized text with embedded errors"
            ),
            DVMeasure(
                name="Processing style",
                instrument="Navon letter task (global/local)",
                tier=MeasurementTier.A,
                frequency="single",
                estimated_cost_usd=500,
                notes="Computer-based, measures global vs. local precedence"
            ),
            DVMeasure(
                name="Subjective confinement",
                instrument="Visual Analog Scale (0-100)",
                tier=MeasurementTier.A,
                frequency="single",
                estimated_cost_usd=0,
                notes="Manipulation check for perceived confinement"
            ),
            DVMeasure(
                name="Physiological stress",
                instrument="Heart Rate Variability (HRV)",
                tier=MeasurementTier.C,
                frequency="continuous",
                estimated_cost_usd=1500,
                notes="Optional; confinement may affect autonomic state"
            ),
        ],
        controls=[
            Control("Room luminance", "match", True),
            Control("Temperature", "match", True),
            Control("Acoustic environment", "match", True),
            Control("View content", "match", True),
            Control("Time of day", "counterbalance", True),
            Control("Task order", "counterbalance", True),
        ],
        duration_weeks=2,
        success_criteria=[
            "RAT performance: High R_h > Low R_h (p < 0.05)",
            "Proofreading: Low R_h > High R_h (p < 0.05)",
            "Navon task: Global precedence stronger in High R_h room",
            "Subjective confinement: Low R_h rated higher confinement",
        ],
        estimated_total_cost_usd=5500,
        cost_breakdown={
            "room_rental_setup": 2000,
            "cognitive_tests_software": 500,
            "hrv_monitors": 1500,
            "participant_compensation": 1200,
            "personnel_time": 300,
        },
        ethical_considerations=[
            "Minimal discomfort expected",
            "Brief exposure duration (30-45 min per condition)",
            "No deception about room differences",
            "Participants informed of cognitive testing purpose",
        ],
        practical_notes=[
            "Find two adjacent rooms with different ceiling heights but similar footprints",
            "Match lighting to lux level, not fixture type",
            "Allow 5-min adaptation period in each room before testing",
            "Consider portable ceiling panels for controlled manipulation",
        ],
    )


@_register_generator("VIEW1")
def _generate_view1_protocol() -> FieldStudyProtocol:
    """Generate protocol for VIEW1 (Nature View VQI)."""
    return FieldStudyProtocol(
        template_id="VIEW1",
        template_name="Nature View Convergence (View Quality Index)",
        prediction="Higher View Quality Index (VQI > 0.6, combining nature content, depth, and visual access) will produce faster stress recovery and better attention restoration compared to low VQI (<0.3) or no view.",
        study_design=StudyDesignType.QUASI_EXPERIMENTAL,
        sample_n=90,
        sample_justification="Three groups (high VQI, low VQI, no view) × n=30, power=0.80 for d=0.6 between groups",
        iv_manipulation="Recruit office workers from three building zones: (1) High VQI windows facing park/trees, (2) Low VQI windows facing urban structures, (3) Interior offices with no view. VQI calculated from photos and spatial metrics.",
        dv_measures=[
            DVMeasure(
                name="Perceived stress",
                instrument="Perceived Stress Scale (PSS-10)",
                tier=MeasurementTier.A,
                frequency="pre_post",
                estimated_cost_usd=0,
                notes="Validated 10-item scale"
            ),
            DVMeasure(
                name="Attention restoration",
                instrument="Backward Digit Span Test",
                tier=MeasurementTier.A,
                frequency="pre_post",
                estimated_cost_usd=0,
                notes="Working memory measure sensitive to directed attention fatigue"
            ),
            DVMeasure(
                name="Mood",
                instrument="Profile of Mood States - Brief (POMS-B)",
                tier=MeasurementTier.A,
                frequency="pre_post",
                estimated_cost_usd=0,
                notes="30-item mood assessment"
            ),
            DVMeasure(
                name="Salivary cortisol",
                instrument="ELISA cortisol assay",
                tier=MeasurementTier.D,
                frequency="pre_post",
                estimated_cost_usd=2500,
                notes="Optional physiological stress marker"
            ),
            DVMeasure(
                name="View Quality Index",
                instrument="Standardized photography + rating protocol",
                tier=MeasurementTier.B,
                frequency="single",
                estimated_cost_usd=500,
                notes="Document view content, depth, nature percentage"
            ),
        ],
        controls=[
            Control("Job role", "match", True),
            Control("Office size", "measure_covary", True),
            Control("Light level", "measure_covary", True),
            Control("Noise level", "measure_covary", True),
            Control("View frequency (desk orientation)", "measure_covary", True),
        ],
        duration_weeks=2,
        success_criteria=[
            "PSS score: High VQI < Low VQI < No View (p < 0.05)",
            "Digit span: High VQI > Low VQI > No View (p < 0.05)",
            "Linear relationship between VQI and outcomes (r > 0.35)",
            "Effect survives controlling for light/noise covariates",
        ],
        estimated_total_cost_usd=7000,
        cost_breakdown={
            "cortisol_assays": 2500,
            "view_documentation": 500,
            "participant_compensation": 2250,
            "light_noise_meters": 800,
            "analysis_software": 450,
            "personnel_time": 500,
        },
        ethical_considerations=[
            "No manipulation of work environment",
            "Observational comparison only",
            "Saliva collection optional",
            "Participants informed of study purpose",
        ],
        practical_notes=[
            "Recruit from same building/organization to control culture",
            "Document view at participant's typical viewing position",
            "Account for seasonal variation in nature content",
            "Consider ESM (experience sampling) for ecological validity",
        ],
    )


@_register_generator("SOC2")
def _generate_soc2_protocol() -> FieldStudyProtocol:
    """Generate protocol for SOC2 (Privacy Gradient)."""
    return FieldStudyProtocol(
        template_id="SOC2",
        template_name="Privacy Gradient and Territorial Behavior",
        prediction="Workspaces with clear privacy gradients (distinct transition from public to private zones) will produce higher perceived control, lower stress, and better concentration than open-plan offices without privacy gradients.",
        study_design=StudyDesignType.QUASI_EXPERIMENTAL,
        sample_n=80,
        sample_justification="Two groups × n=40, power=0.80 for d=0.5 effect",
        iv_manipulation="Compare workers in (1) offices with designed privacy gradient (reception → team zone → focus pods → private offices) vs. (2) undifferentiated open plan. IV operationalized as Privacy Gradient Score (0-10 scale).",
        dv_measures=[
            DVMeasure(
                name="Perceived control",
                instrument="Environmental Control Scale (adapted)",
                tier=MeasurementTier.A,
                frequency="single",
                estimated_cost_usd=0,
                notes="8-item scale on control over space, noise, interruptions"
            ),
            DVMeasure(
                name="Workplace stress",
                instrument="Job Content Questionnaire - Demand/Control subscales",
                tier=MeasurementTier.A,
                frequency="single",
                estimated_cost_usd=0,
                notes="Validated occupational stress measure"
            ),
            DVMeasure(
                name="Concentration/focus",
                instrument="Perceived Ability to Concentrate Scale",
                tier=MeasurementTier.A,
                frequency="single",
                estimated_cost_usd=0,
                notes="6-item self-report"
            ),
            DVMeasure(
                name="Interruption frequency",
                instrument="Daily diary (ESM)",
                tier=MeasurementTier.B,
                frequency="daily",
                estimated_cost_usd=800,
                notes="5-day sampling, 3x daily prompts"
            ),
            DVMeasure(
                name="Territorial behavior",
                instrument="Behavioral observation protocol",
                tier=MeasurementTier.B,
                frequency="single",
                estimated_cost_usd=1000,
                notes="Code personalization, boundary marking, space use patterns"
            ),
        ],
        controls=[
            Control("Job role", "match", True),
            Control("Tenure", "measure_covary", True),
            Control("Density (m²/person)", "measure_covary", True),
            Control("Noise level", "measure_covary", True),
            Control("Team size", "measure_covary", False),
        ],
        duration_weeks=2,
        success_criteria=[
            "Perceived control: Gradient > Open plan (p < 0.05)",
            "Workplace stress: Gradient < Open plan (p < 0.05)",
            "Interruption frequency: Gradient < Open plan (p < 0.05)",
            "Privacy Gradient Score correlates with outcomes (r > 0.3)",
        ],
        estimated_total_cost_usd=5500,
        cost_breakdown={
            "esm_platform": 800,
            "observation_training": 1000,
            "participant_compensation": 2000,
            "environmental_measurement": 700,
            "personnel_time": 1000,
        },
        ethical_considerations=[
            "Privacy of observation data",
            "Voluntary participation",
            "No identifying information in behavioral coding",
            "Results aggregated, not individual feedback",
        ],
        practical_notes=[
            "Partner with organizations redesigning offices",
            "Before/after design is ideal but rare",
            "Use floor plan analysis to calculate Privacy Gradient Score",
            "Consider acoustic privacy as key component",
        ],
    )


@_register_generator("MAT1")
def _generate_mat1_protocol() -> FieldStudyProtocol:
    """Generate protocol for MAT1 (Thermal Comfort - Affective Touch)."""
    return FieldStudyProtocol(
        template_id="MAT1",
        template_name="Affective Touch Pathway and Material Perception",
        prediction="Natural materials (wood, textiles) that engage C-tactile afferents (CT fibers optimal at ~3 cm/s, ~32°C) will produce more positive affective responses and lower stress than synthetic materials (plastic, metal), mediated by insular cortex activation.",
        study_design=StudyDesignType.WITHIN_SUBJECTS,
        sample_n=40,
        sample_justification="Power for d=0.45 effect in within-subjects design, α=0.05, power=0.80",
        iv_manipulation="Participants touch 6 material samples in counterbalanced order: Wood (oak), Textile (wool), Stone (marble), Metal (aluminum), Plastic (acrylic), Composite (laminate). Standardized stroking protocol (3 cm/s, 10s duration).",
        dv_measures=[
            DVMeasure(
                name="Affective response",
                instrument="Self-Assessment Manikin (SAM)",
                tier=MeasurementTier.A,
                frequency="single",
                estimated_cost_usd=0,
                notes="Valence, arousal, dominance per material"
            ),
            DVMeasure(
                name="Pleasantness rating",
                instrument="Visual Analog Scale (0-100)",
                tier=MeasurementTier.A,
                frequency="single",
                estimated_cost_usd=0,
                notes="Simple pleasantness judgment"
            ),
            DVMeasure(
                name="Perceived naturalness",
                instrument="Semantic differential scale",
                tier=MeasurementTier.A,
                frequency="single",
                estimated_cost_usd=0,
                notes="Natural-Artificial, Warm-Cold, Soft-Hard"
            ),
            DVMeasure(
                name="Skin conductance",
                instrument="EDA (electrodermal activity)",
                tier=MeasurementTier.C,
                frequency="continuous",
                estimated_cost_usd=1200,
                notes="Autonomic arousal measure during touch"
            ),
            DVMeasure(
                name="Heart rate variability",
                instrument="HRV monitor",
                tier=MeasurementTier.C,
                frequency="continuous",
                estimated_cost_usd=1000,
                notes="Parasympathetic activation (HF-HRV)"
            ),
        ],
        controls=[
            Control("Material temperature", "match", True),
            Control("Lighting", "match", True),
            Control("Visual appearance (blindfolded)", "match", True),
            Control("Touch pressure", "standardize", True),
            Control("Prior material associations", "measure_covary", False),
        ],
        duration_weeks=1,
        success_criteria=[
            "Pleasantness: Natural > Synthetic (p < 0.05)",
            "SAM valence: Natural > Synthetic (p < 0.05)",
            "EDA: Lower arousal for natural materials",
            "HRV: Higher HF-HRV for natural materials",
            "Correlation between perceived naturalness and pleasantness (r > 0.5)",
        ],
        estimated_total_cost_usd=5200,
        cost_breakdown={
            "material_samples": 500,
            "eda_equipment": 1200,
            "hrv_monitors": 1000,
            "participant_compensation": 1200,
            "lab_setup": 800,
            "personnel_time": 500,
        },
        ethical_considerations=[
            "Touch is non-invasive",
            "Blindfolding is brief and consensual",
            "No allergens in material samples",
            "Right to withdraw at any time",
        ],
        practical_notes=[
            "Temperature-match all samples to skin temperature (~32°C)",
            "Use blindfold or occluding screen to isolate tactile modality",
            "Allow 30s recovery between materials",
            "Consider adding fMRI condition for mechanism confirmation (insular activation)",
        ],
    )


def generate_protocol(template_id: str) -> Optional[FieldStudyProtocol]:
    """
    Generate a field study protocol for a given template.

    Args:
        template_id: Template display ID (e.g., "L2", "VF3", "VIEW1")

    Returns:
        FieldStudyProtocol or None if no generator exists
    """
    normalized = template_id.upper().strip()
    generator = PROTOCOL_GENERATORS.get(normalized)
    if generator:
        return generator()
    return None


def get_available_protocols() -> list[str]:
    """Return list of template IDs with protocol generators."""
    return sorted(PROTOCOL_GENERATORS.keys())


def generate_all_protocols() -> list[FieldStudyProtocol]:
    """Generate protocols for all available templates."""
    return [generator() for generator in PROTOCOL_GENERATORS.values()]


def format_protocol_report(protocol: FieldStudyProtocol) -> str:
    """Format a protocol as a readable report."""
    lines = []
    lines.append("=" * 70)
    lines.append(f"FIELD VALIDATION PROTOCOL: {protocol.template_id}")
    lines.append("=" * 70)
    lines.append("")
    lines.append(f"Template: {protocol.template_name}")
    lines.append(f"Generated: {protocol.generated_at.strftime('%Y-%m-%d %H:%M')}")
    lines.append("")

    lines.append("-" * 50)
    lines.append("PREDICTION")
    lines.append("-" * 50)
    lines.append(protocol.prediction)
    lines.append("")

    lines.append("-" * 50)
    lines.append("STUDY DESIGN")
    lines.append("-" * 50)
    lines.append(f"Design Type: {protocol.study_design.value}")
    lines.append(f"Sample Size: N = {protocol.sample_n}")
    lines.append(f"Justification: {protocol.sample_justification}")
    lines.append(f"Duration: {protocol.duration_weeks} weeks")
    lines.append("")
    lines.append("IV Manipulation:")
    lines.append(f"  {protocol.iv_manipulation}")
    lines.append("")

    lines.append("-" * 50)
    lines.append("DEPENDENT VARIABLES")
    lines.append("-" * 50)
    for i, dv in enumerate(protocol.dv_measures, 1):
        lines.append(f"[{i}] {dv.name}")
        lines.append(f"    Instrument: {dv.instrument}")
        lines.append(f"    Tier: {dv.tier.value} | Frequency: {dv.frequency}")
        lines.append(f"    Est. Cost: ${dv.estimated_cost_usd:,.0f}")
        if dv.notes:
            lines.append(f"    Notes: {dv.notes}")
        lines.append("")

    lines.append("-" * 50)
    lines.append("CONTROLS")
    lines.append("-" * 50)
    for ctrl in protocol.controls:
        critical = "CRITICAL" if ctrl.critical else "optional"
        lines.append(f"- {ctrl.name}: {ctrl.method} ({critical})")
    lines.append("")

    lines.append("-" * 50)
    lines.append("SUCCESS CRITERIA")
    lines.append("-" * 50)
    for i, criterion in enumerate(protocol.success_criteria, 1):
        lines.append(f"{i}. {criterion}")
    lines.append("")

    lines.append("-" * 50)
    lines.append("COST ESTIMATE")
    lines.append("-" * 50)
    lines.append(f"Total: ${protocol.estimated_total_cost_usd:,.0f}")
    lines.append("")
    for category, cost in protocol.cost_breakdown.items():
        lines.append(f"  {category}: ${cost:,.0f}")
    lines.append("")

    lines.append("-" * 50)
    lines.append("ETHICAL CONSIDERATIONS")
    lines.append("-" * 50)
    for item in protocol.ethical_considerations:
        lines.append(f"- {item}")
    lines.append("")

    lines.append("-" * 50)
    lines.append("PRACTICAL NOTES")
    lines.append("-" * 50)
    for item in protocol.practical_notes:
        lines.append(f"- {item}")

    lines.append("")
    lines.append("=" * 70)
    return "\n".join(lines)


def export_protocols_json(output_path: Optional[Path] = None) -> dict:
    """Export all protocols to JSON."""
    protocols = generate_all_protocols()
    data = {
        "generated_at": datetime.utcnow().isoformat(),
        "n_protocols": len(protocols),
        "protocols": [p.to_dict() for p in protocols],
    }
    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    return data


__all__ = [
    "StudyDesignType",
    "MeasurementTier",
    "DVMeasure",
    "Control",
    "FieldStudyProtocol",
    "generate_protocol",
    "get_available_protocols",
    "generate_all_protocols",
    "format_protocol_report",
    "export_protocols_json",
]
