"""
Tier A Quick Assessment Mode.

Sprint 12 Task 12.6: Simplified building assessment using only Tier A inputs
(visual observation, no specialized equipment).

10 templates usable with zero specialized equipment:
VF3, VIEW1, CREA3, SC4, COL1, COL2, TP1, MAT1, SOC3, MAT4
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from src.cmr.lifespan_moderation import compute_template_with_lifespan


TIER_A_TEMPLATES = ["VF3", "VIEW1", "CREA3", "SC4", "COL1", "COL2", "TP1", "MAT1", "SOC3", "MAT4"]
TIER_B_SUPPLEMENTAL_TEMPLATES = [
    "L1",
    "L2",
    "L3",
    "L4",
    "L5",
    "CREA2",
    "SOC1",
    "SOC2",
    "SC1",
    "TP2",
    "VF1",
    "VF2",
]


@dataclass
class QuickAssessResult:
    """Result of a quick assessment."""
    overall_rating: str  # "Good" | "Fair" | "Needs Attention" | "Poor"
    overall_wis: float
    template_scores: Dict[str, float]
    strengths: List[Dict[str, Any]]
    deficits: List[Dict[str, Any]]
    recommendations: List[str]
    tier_b_suggestions: List[str]
    tier_mode: str
    tier_b_reveals: List[str]
    templates_assessed: int
    templates_skipped: List[str]


def _get_rating(wis: float) -> str:
    """Convert WIS score to qualitative rating."""
    if wis >= 65:
        return "Good"
    elif wis >= 50:
        return "Fair"
    elif wis >= 35:
        return "Needs Attention"
    else:
        return "Poor"


def _wis_to_label(wis: float) -> str:
    """Convert WIS to human-friendly label."""
    if wis >= 70:
        return "excellent"
    elif wis >= 55:
        return "good"
    elif wis >= 45:
        return "adequate"
    elif wis >= 30:
        return "problematic"
    else:
        return "poor"


def quick_assess(
    ceiling_height_m: Optional[float] = None,
    floor_area_m2: Optional[float] = None,
    has_nature_view: Optional[bool] = None,
    view_content: Optional[str] = None,
    walking_paths_available: Optional[bool] = None,
    wayfinding_clear: Optional[bool] = None,
    wall_colors: Optional[List[str]] = None,
    color_sequence_varied: Optional[bool] = None,
    floor_surface: Optional[str] = None,
    stair_dimensions_standard: Optional[bool] = None,
    thermal_system: Optional[str] = None,
    primary_material: Optional[str] = None,
    max_group_size: Optional[int] = None,
    illuminance_lux: Optional[float] = None,
    ambient_noise_dba: Optional[float] = None,
    rt60_seconds: Optional[float] = None,
    occupant_age: int = 35,
) -> QuickAssessResult:
    """
    Perform Tier A quick assessment using visual observation only.

    Args:
        ceiling_height_m: Ceiling height in meters
        floor_area_m2: Floor area in square meters
        has_nature_view: Whether natural view is available
        view_content: Description of view content ("nature", "urban", "none")
        walking_paths_available: Whether walking/movement paths exist
        wayfinding_clear: Whether navigation is intuitive
        wall_colors: List of dominant wall colors
        color_sequence_varied: Whether color varies through space
        floor_surface: Floor surface type ("level", "stairs", etc.)
        stair_dimensions_standard: Whether stairs meet standards
        thermal_system: Type of thermal control ("operable_windows", "hvac", etc.)
        primary_material: Primary surface material ("wood", "concrete", etc.)
        max_group_size: Maximum expected group size
        illuminance_lux: Tier B light measurement (lux)
        ambient_noise_dba: Tier B noise measurement (dBA)
        rt60_seconds: Tier B reverberation time (seconds)
        occupant_age: Occupant age for lifespan moderation

    Returns:
        QuickAssessResult with ratings, scores, and recommendations
    """
    template_scores = {}
    skipped = []
    occupant_profile = {"age": occupant_age}

    # VF3: Volume/Form - needs ceiling height and floor area
    if ceiling_height_m is not None and floor_area_m2 is not None:
        result = compute_template_with_lifespan(
            template_id="VF3",
            measured_features={"ceiling_height_m": ceiling_height_m, "floor_area_m2": floor_area_m2},
            occupant_profile=occupant_profile,
        )
        if not result.get("needs_computation"):
            template_scores["VF3"] = result["wis"]
    else:
        skipped.append("VF3")

    # VIEW1: View Quality - needs view info
    if has_nature_view is not None:
        # Simplified VQI estimation
        if has_nature_view and view_content == "nature":
            view_wis = 75.0
        elif has_nature_view:
            view_wis = 60.0
        elif view_content == "urban":
            view_wis = 45.0
        else:
            view_wis = 35.0
        template_scores["VIEW1"] = view_wis
    else:
        skipped.append("VIEW1")

    # SC4: Wayfinding
    if wayfinding_clear is not None:
        template_scores["SC4"] = 70.0 if wayfinding_clear else 40.0
    else:
        skipped.append("SC4")

    # CREA3: Walking/movement paths
    if walking_paths_available is not None:
        template_scores["CREA3"] = 65.0 if walking_paths_available else 35.0
    else:
        skipped.append("CREA3")

    # COL1/COL2: Color
    if wall_colors is not None:
        # Basic color assessment
        has_warm = any(c.lower() in ["yellow", "orange", "red", "brown", "beige", "cream"] for c in wall_colors)
        has_natural = any(c.lower() in ["green", "blue", "wood", "earth"] for c in wall_colors)
        if has_natural and has_warm:
            template_scores["COL1"] = 65.0
        elif has_natural or has_warm:
            template_scores["COL1"] = 55.0
        else:
            template_scores["COL1"] = 45.0

        if color_sequence_varied:
            template_scores["COL2"] = 60.0
        else:
            template_scores["COL2"] = 45.0
    else:
        skipped.extend(["COL1", "COL2"])

    # TP1: Trip/fall safety
    if floor_surface is not None:
        if floor_surface == "level" and (stair_dimensions_standard is None or stair_dimensions_standard):
            template_scores["TP1"] = 70.0
        elif floor_surface == "level":
            template_scores["TP1"] = 60.0
        else:
            template_scores["TP1"] = 45.0
    else:
        skipped.append("TP1")

    # MAT1: Thermal comfort
    if thermal_system is not None:
        if thermal_system == "operable_windows":
            template_scores["MAT1"] = 70.0
        elif thermal_system == "hvac":
            template_scores["MAT1"] = 55.0
        else:
            template_scores["MAT1"] = 45.0
    else:
        skipped.append("MAT1")

    # MAT4: Natural materials
    if primary_material is not None:
        natural_mats = ["wood", "stone", "bamboo", "brick", "cork"]
        if primary_material.lower() in natural_mats:
            template_scores["MAT4"] = 70.0
        elif primary_material.lower() in ["concrete", "metal", "glass"]:
            template_scores["MAT4"] = 45.0
        else:
            template_scores["MAT4"] = 50.0
    else:
        skipped.append("MAT4")

    # SOC3: Social/group accommodation
    if max_group_size is not None:
        if max_group_size >= 6:
            template_scores["SOC3"] = 65.0
        elif max_group_size >= 3:
            template_scores["SOC3"] = 55.0
        else:
            template_scores["SOC3"] = 45.0
    else:
        skipped.append("SOC3")

    tier_mode = "A+B" if any(v is not None for v in (illuminance_lux, ambient_noise_dba, rt60_seconds)) else "A"
    tier_b_reveals: List[str] = []

    if tier_mode == "A+B":
        # Tier B expands activation with measurement-driven templates.
        b_scores = _compute_tier_b_scores(
            template_scores=template_scores,
            illuminance_lux=illuminance_lux,
            ambient_noise_dba=ambient_noise_dba,
            rt60_seconds=rt60_seconds,
            wayfinding_clear=wayfinding_clear,
            color_sequence_varied=color_sequence_varied,
            max_group_size=max_group_size,
            occupant_age=occupant_age,
        )
        template_scores.update(b_scores)
        tier_b_reveals = _build_tier_b_reveals(
            b_scores=b_scores,
            illuminance_lux=illuminance_lux,
            ambient_noise_dba=ambient_noise_dba,
            rt60_seconds=rt60_seconds,
        )

    # Calculate overall WIS
    if template_scores:
        overall_wis = sum(template_scores.values()) / len(template_scores)
    else:
        overall_wis = 50.0  # Neutral if no data

    # Identify strengths (WIS >= 60) and deficits (WIS < 45)
    strengths = []
    deficits = []
    for tid, wis in sorted(template_scores.items(), key=lambda x: -x[1]):
        if wis >= 60:
            strengths.append({"template": tid, "wis": wis, "label": _wis_to_label(wis)})
        elif wis < 45:
            deficits.append({"template": tid, "wis": wis, "label": _wis_to_label(wis)})

    # Generate recommendations
    recommendations = _generate_recommendations(template_scores, deficits)

    # Suggest Tier B measurements
    tier_b_suggestions = [
        "Light level measurements (illuminance lux) would enable L1, L2, L3 templates",
        "Sound level measurements (dBA) would enable acoustic comfort templates",
        "Temperature measurements would improve MAT1 precision",
    ]

    return QuickAssessResult(
        overall_rating=_get_rating(overall_wis),
        overall_wis=round(overall_wis, 1),
        template_scores={k: round(v, 1) for k, v in template_scores.items()},
        strengths=strengths[:3],
        deficits=deficits[:3],
        recommendations=recommendations,
        tier_b_suggestions=tier_b_suggestions,
        tier_mode=tier_mode,
        tier_b_reveals=tier_b_reveals,
        templates_assessed=len(template_scores),
        templates_skipped=skipped,
    )


def _clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def _compute_tier_b_scores(
    *,
    template_scores: Dict[str, float],
    illuminance_lux: Optional[float],
    ambient_noise_dba: Optional[float],
    rt60_seconds: Optional[float],
    wayfinding_clear: Optional[bool],
    color_sequence_varied: Optional[bool],
    max_group_size: Optional[int],
    occupant_age: int,
) -> Dict[str, float]:
    lux = float(illuminance_lux if illuminance_lux is not None else 400.0)
    noise = float(ambient_noise_dba if ambient_noise_dba is not None else 45.0)
    rt60 = float(rt60_seconds if rt60_seconds is not None else 0.6)
    vf3 = float(template_scores.get("VF3", 55.0))
    view1 = float(template_scores.get("VIEW1", 50.0))

    l1 = _clamp(82.0 - abs(lux - 450.0) / 7.0, 20.0, 85.0)
    l2 = _clamp(30.0 + (lux / 10.0), 20.0, 85.0)
    l4 = _clamp(68.0 - abs(lux - 400.0) / 16.0, 30.0, 80.0)
    l5 = _clamp(58.0 + (5.0 if view1 >= 60 else -4.0), 35.0, 75.0)
    l3 = _clamp((l1 + l2 + l4 + l5 + view1) / 5.0, 25.0, 90.0)

    crea2_noise = _clamp(75.0 - abs(noise - 68.0) * 1.8, 20.0, 85.0)
    crea2_light = _clamp(70.0 - abs(lux - 180.0) / 8.0, 20.0, 85.0)
    crea2 = _clamp(0.4 * crea2_noise + 0.3 * crea2_light + 0.3 * vf3, 20.0, 88.0)

    soc2_noise = _clamp(95.0 - max(0.0, noise - 35.0) * 2.0, 15.0, 85.0)
    soc2_rt60 = _clamp(85.0 - abs(rt60 - 0.5) * 90.0, 15.0, 85.0)
    soc2 = _clamp(0.7 * soc2_noise + 0.3 * soc2_rt60, 15.0, 85.0)

    if max_group_size is None:
        group_score = 50.0
    elif max_group_size <= 2:
        group_score = 45.0
    elif max_group_size <= 6:
        group_score = 72.0
    elif max_group_size <= 12:
        group_score = 62.0
    else:
        group_score = 45.0
    soc1 = _clamp(0.6 * group_score + 0.4 * soc2, 20.0, 85.0)

    sc1 = _clamp(70.0 if wayfinding_clear else 46.0, 25.0, 85.0)
    tp2 = _clamp(78.0 - abs(rt60 - 0.45) * 95.0, 20.0, 85.0)

    vf1 = _clamp((view1 * 0.55) + (15.0 if color_sequence_varied else 0.0) + 20.0, 25.0, 85.0)
    vf2 = _clamp(58.0 + (8.0 if color_sequence_varied else -6.0), 20.0, 82.0)

    # Mild age moderation for Tier B-measured cognition/social sensitivities.
    age_modifier = 1.0
    if occupant_age < 25:
        age_modifier = 1.04
    elif occupant_age > 65:
        age_modifier = 0.97

    scored = {
        "L1": l1,
        "L2": l2,
        "L3": l3,
        "L4": l4,
        "L5": l5,
        "CREA2": crea2 * age_modifier,
        "SOC1": soc1,
        "SOC2": soc2 * age_modifier,
        "SC1": sc1,
        "TP2": tp2,
        "VF1": vf1,
        "VF2": vf2,
    }
    return {k: round(_clamp(v), 1) for k, v in scored.items()}


def _build_tier_b_reveals(
    *,
    b_scores: Dict[str, float],
    illuminance_lux: Optional[float],
    ambient_noise_dba: Optional[float],
    rt60_seconds: Optional[float],
) -> List[str]:
    reveals: List[str] = []

    if illuminance_lux is not None:
        if b_scores.get("L2", 50.0) < 50:
            reveals.append("Measured light levels suggest circadian support is weaker than visual inspection implied.")
        else:
            reveals.append("Measured light levels confirm acceptable daytime lighting performance.")

    if ambient_noise_dba is not None:
        if b_scores.get("SOC2", 50.0) < 50:
            reveals.append("Measured noise indicates privacy/attention stress risk that Tier A cannot quantify.")
        else:
            reveals.append("Measured noise is within a range compatible with social-acoustic comfort.")

    if rt60_seconds is not None:
        if b_scores.get("TP2", 50.0) < 50:
            reveals.append("Reverberation suggests boundary perception/acoustic transitions need refinement.")
        else:
            reveals.append("Reverberation profile supports clear acoustic boundaries and transitions.")

    if not reveals:
        reveals.append("Tier B inputs expanded assessment coverage without major measurement surprises.")
    return reveals[:4]


def _generate_recommendations(scores: Dict[str, float], deficits: List[Dict]) -> List[str]:
    """Generate actionable recommendations based on scores."""
    recs = []

    if "VIEW1" in scores and scores["VIEW1"] < 50:
        recs.append("Add plants or nature imagery to improve visual connection to nature")

    if "VF3" in scores and scores["VF3"] < 50:
        recs.append("Consider ceiling height modifications or furniture to improve spatial proportions")

    if "SC4" in scores and scores["SC4"] < 50:
        recs.append("Improve wayfinding with clearer signage or spatial landmarks")

    if "MAT4" in scores and scores["MAT4"] < 50:
        recs.append("Incorporate wood or natural materials in surfaces or furnishings")

    if "MAT1" in scores and scores["MAT1"] < 50:
        recs.append("Consider adding operable windows or personal thermal control")

    if "COL1" in scores and scores["COL1"] < 50:
        recs.append("Introduce warmer or nature-inspired colors")

    if not recs and deficits:
        recs.append(f"Focus improvement on {deficits[0]['template']} (current: {deficits[0]['label']})")

    if not recs:
        recs.append("Space performs well across assessed dimensions")

    return recs[:5]


def format_quick_report(result: QuickAssessResult) -> str:
    """Format quick assessment as readable report."""
    lines = []
    lines.append("=" * 50)
    lines.append("QUICK BUILDING ASSESSMENT")
    lines.append("=" * 50)
    lines.append("")
    lines.append(f"Overall Rating: {result.overall_rating}")
    lines.append(f"Wellness Score: {result.overall_wis}/100")
    total_pool = len(TIER_A_TEMPLATES) + (len(TIER_B_SUPPLEMENTAL_TEMPLATES) if result.tier_mode == "A+B" else 0)
    lines.append(f"Assessment Tier: {result.tier_mode}")
    lines.append(f"Templates Assessed: {result.templates_assessed}/{total_pool}")
    lines.append("")

    if result.strengths:
        lines.append("STRENGTHS:")
        for s in result.strengths:
            lines.append(f"  + {s['template']}: {s['label']} ({s['wis']})")
        lines.append("")

    if result.deficits:
        lines.append("NEEDS ATTENTION:")
        for d in result.deficits:
            lines.append(f"  - {d['template']}: {d['label']} ({d['wis']})")
        lines.append("")

    lines.append("RECOMMENDATIONS:")
    for r in result.recommendations:
        lines.append(f"  * {r}")
    lines.append("")

    lines.append("TO LEARN MORE:")
    for s in result.tier_b_suggestions[:2]:
        lines.append(f"  > {s}")

    if result.tier_b_reveals:
        lines.append("")
        lines.append("TIER B REVEALS:")
        for reveal in result.tier_b_reveals:
            lines.append(f"  > {reveal}")

    if result.templates_skipped:
        lines.append("")
        lines.append(f"Note: {len(result.templates_skipped)} templates skipped due to missing inputs")

    return "\n".join(lines)
