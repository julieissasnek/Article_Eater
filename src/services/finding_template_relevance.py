"""Resolve template and theory relevance for WebOfBelief findings."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
import re
import sqlite3
from datetime import datetime, timezone
from typing import Any, Dict, Iterable
from difflib import SequenceMatcher

try:
    from src.services.extraction_to_web import infer_theory_relevance
except Exception:  # pragma: no cover - optional fallback
    infer_theory_relevance = None


OUTCOME_LEVELS = {
    "cognitive",
    "affective",
    "physiological",
    "behavioral",
    "neural",
    "psychological",
    "systems",
    "subcortical",
}

STOPWORDS = {
    "the",
    "a",
    "an",
    "and",
    "or",
    "to",
    "of",
    "in",
    "on",
    "for",
    "with",
    "by",
    "from",
    "at",
    "as",
    "is",
    "are",
    "was",
    "were",
    "that",
    "this",
    "it",
    "be",
}

ENV_BRIDGES = {
    "has_nature_view": {
        "nature_scene_exposure",
        "nature_view",
        "green_view",
        "biophilic_input",
    },
    "ambient_noise_dba": {
        "ambient_noise_level",
        "acoustic_load",
        "auditory_stress",
        "auditory_spatial_cues",
    },
    "illuminance_lux": {
        "light_intensity",
        "luminance",
        "light_exposure",
        "corneal_melanopic_irradiance",
    },
    "window_area_ratio": {
        "daylight_access",
        "view_access",
        "natural_light_availability",
    },
    "ceiling_height_m": {
        "ceiling_height",
        "spatial_volume",
        "perceived_confinement",
    },
    "primary_material": {
        "material_identity",
        "haptic_signal",
        "thermal_effusivity",
    },
    "floor_area_m2": {
        "spatial_extent",
        "navigability",
    },
    "time_of_day": {
        "circadian_phase",
        "temporal_context",
    },
    "color": {
        "chromatic_environment",
        "hue_saturation",
    },
}

OUTCOME_BRIDGES = {
    "attention": {
        "directed_attention",
        "attention_control",
        "processing_style",
        "tpn_deactivation",
        "dmn_re_engagement",
    },
    "stress": {
        "hpa_axis_dysregulation",
        "cortisol",
        "allostatic_load",
        "autonomic_arousal",
    },
    "mood": {
        "affective_response",
        "felt_emotion",
        "positive_affect_shift",
    },
    "well_being": {
        "allostatic_load",
        "restorative_outcome",
        "mood",
    },
    "productivity": {
        "cognitive_performance",
        "executive_function",
        "working_memory_load",
    },
    "recovery_time": {
        "stress_recovery",
        "autonomic_recovery",
    },
    "sleep_quality": {
        "circadian_alignment",
        "melatonin_cortisol_rhythm",
        "sleep_consolidation",
    },
    "creativity": {
        "divergent_thinking",
        "processing_style",
        "exploration_exploitation_balance",
    },
    "memory": {
        "episodic_boundary_strength",
        "memory_retrieval",
        "working_memory_load",
    },
    "cognitive_load": {
        "working_memory_load",
        "directed_attention_fatigue",
    },
    "visual_comfort": {
        "luminance_pe_magnitude",
        "visual_strain",
    },
    "preference": {
        "aesthetic_emotion",
        "approach_avoidance",
    },
    "social_interaction": {
        "perceived_social_isolation",
        "proxemic_regulation",
    },
    "physiological_arousal": {
        "autonomic_arousal",
        "hpa_axis_dysregulation",
    },
    "cortisol": {
        "hpa_axis_dysregulation",
        "melatonin_cortisol_rhythm",
    },
}

TIER1_TAXONOMY: dict[str, set[str]] = {
    "ART": {
        "ART",
        "ATTENTION_RESTORATION",
        "ATTENTION_RESTORATION_THEORY",
        "DIRECTED_ATTENTION",
        "RESTORATIVE_ENVIRONMENTS",
    },
    "SRT": {
        "SRT",
        "STRESS_RECOVERY",
        "STRESS_RECOVERY_THEORY",
        "STRESS_PHYSIOLOGY",
        "ALLOSTATIC_LOAD",
        "ALLOSTATIC_REGULATION",
        "ENVIRONMENTAL_STRESS",
        "NM_STRESS",
        "HPA",
    },
    "BIOPHILIA": {
        "BIOPHILIA",
        "BIOPHILIC_DESIGN",
        "PROSPECT_REFUGE",
        "PROSPECT_REFUGE_THEORY",
        "NATURE",
    },
    "PREDICTIVE_PROCESSING": {
        "PREDICTIVE_PROCESSING",
        "HIERARCHICAL_PREDICTIVE_CODING",
        "PP",
    },
    "CIRCADIAN_REGULATION": {
        "CIRCADIAN",
        "CHRONOBIOLOGICAL",
        "CHRONOBIOLOGICAL_REGULATION",
        "CIRCADIAN_NEUROSCIENCE",
        "RETINAL_ACTIVATION",
        "TEMPORAL_COGNITION",
        "TIME_PERCEPTION_THEORY",
    },
    "COGNITIVE_CONTROL": {
        "COGNITIVE_CONTROL",
        "COGNITIVE_LOAD_THEORY",
        "EXECUTIVE",
        "WORKING_MEMORY",
        "DUAL_PROCESS",
        "ECOLOGICAL_RATIONALITY",
    },
    "MULTISENSORY_INTEGRATION": {
        "MULTISENSORY_INTEGRATION",
        "MSI",
        "MS",
        "SENSORY",
    },
    "SPATIAL_COGNITION": {
        "SPATIAL_NAVIGATION",
        "SPACE_SYNTAX",
        "WAYFINDING",
        "HIPPOCAMPAL_SPATIAL_COGNITION",
        "VISUAL_GRAPH_ANALYSIS",
    },
    "AFFECTIVE_EMOTION": {
        "AFFECTIVE_NEUROSCIENCE",
        "AFFECTIVE_SCIENCE",
        "AESTHETIC_EMOTIONS",
        "EMOTION_PERCEPTION",
        "PAD_EMOTIONAL_MODEL",
        "COGNITIVE_APPRAISAL",
        "APPROACH_AVOIDANCE",
    },
    "SOCIAL_COGNITION": {
        "SOCIAL",
        "SOCIAL_PSYCHOLOGY",
        "SOCIAL_NEUROSCIENCE",
        "SOCIAL_BRAIN_HYPOTHESIS",
        "PROXEMICS",
        "PRIVACY_REGULATION",
        "TERRITORIAL",
    },
    "NEUROMODULATORY_REWARD": {
        "NEUROMODULATORY",
        "NM",
        "NM_REWARD",
        "NM_AROUSAL",
        "REWARD_PROCESSING",
        "DOPAMINERGIC",
        "AROUSAL_THEORY",
    },
    "MEMORY_LEARNING": {
        "MEMORY",
        "MEMORY_SYSTEMS",
        "EPISODIC_MEMORY",
        "CONTEXT_DEPENDENT_MEMORY",
        "EVENT_SEGMENTATION_THEORY",
        "SITUATION_MODELS",
        "STATISTICAL_LEARNING",
    },
    "CREATIVE_COGNITION": {
        "CREATIVE_COGNITION",
        "CREATIVE_COGNITION_THEORY",
        "INCUBATION_THEORY",
        "GROUP_CREATIVITY",
    },
    "MATERIAL_HAPTIC_THERMAL": {
        "MATERIAL",
        "MATERIALS",
        "SOMATOSENSORY_PROCESSING",
        "HAPTIC",
        "THERMAL",
        "ADAPTIVE_THERMAL_COMFORT",
        "INTEROCEPTION",
        "INTEROCEPTION_ALLOSTASIS",
        "INTEROCEPTION_CONSTRUCTIONIST",
    },
    "AUDIO_COGNITION": {
        "ACOUSTIC_COMMUNICATION",
        "MUSIC_COGNITION",
        "AUDITORY",
    },
    "EMBODIED_ECOLOGICAL": {
        "EMBODIED_COGNITION",
        "ECOLOGICAL_PSYCHOLOGY",
        "AFFORDANCE_THEORY",
        "FORWARD_MODELS",
        "MOTOR_CONTROL_THEORY",
    },
    "ARCHITECTURAL_PHENOMENOLOGY": {
        "ARCHITECTURAL_PHENOMENOLOGY",
        "ARCHITECTURAL_COMPOSITION",
        "BEHAVIORAL_ARCHITECTURE",
        "ARCHITECTURAL_HEALTH",
        "ARCHITECTURAL_MATHEMATICS",
    },
    "VISUAL_PERCEPTION_AESTHETICS": {
        "VISUAL_PERCEPTION",
        "PROCESSING_FLUENCY",
        "ECOLOGICAL_VALENCE_THEORY",
        "CATEGORICAL_COLOR_PERCEPTION",
        "FRACTAL_FLUENCY",
        "FRACTAL_AESTHETICS",
    },
}

DOMAIN_KEYWORDS: dict[str, set[str]] = {
    "nature": {"nature", "green", "vegetation", "biophilic", "tree", "view"},
    "acoustics": {"noise", "acoustic", "auditory", "sound", "dba", "rt60"},
    "music": {"music", "musical", "melody", "rhythm", "harmony", "song", "tonal"},
    "light": {"light", "illuminance", "luminance", "lux", "daylight", "cct", "melanopic"},
    "thermal": {"thermal", "temperature", "heat", "cold", "comfort", "alliesthesia"},
    "spatial": {"spatial", "space", "ceiling", "isovist", "wayfinding", "navigation", "layout"},
    "material": {"material", "texture", "haptic", "wood", "stone", "concrete"},
    "social": {"social", "proxemic", "privacy", "territorial", "interaction"},
    "color": {"color", "colour", "hue", "saturation", "chromatic"},
    "olfaction": {"olfaction", "olfactory", "odor", "smell", "scent"},
    "creative": {"creative", "creativity", "divergent", "incubation"},
    "cognitive": {"attention", "memory", "executive", "control", "load"},
}

GENERIC_TEMPLATE_DOMAINS = {"cross_framework", "predictive_processing"}

DOMAIN_ALIAS_MAP: dict[str, set[str]] = {
    "music": {"music"},
    "music_emotion": {"music"},
    "light_luminance": {"light"},
    "spatial_configuration": {"spatial"},
    "social_configuration": {"social"},
    "social_cognition": {"social"},
    "creative_cognition": {"creative"},
    "materials": {"material"},
    "visual_form": {"spatial", "color"},
    "color": {"color"},
    "olfaction": {"olfaction"},
    "cross_framework": {"cross_framework"},
    "predictive_processing": {"predictive_processing"},
}

ATTRIBUTE_DOMAIN_MAP: dict[str, set[str]] = {
    "a1": {"material", "thermal"},
    "a3": {"spatial"},
    "a4": {"light"},
    "a6": {"color"},
    "a8": {"social"},
    "a9": {"creative", "cognitive"},
}


def _normalize(value: Any) -> str:
    text = str(value or "").strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return re.sub(r"_+", "_", text).strip("_")


def _tokenize(value: Any) -> set[str]:
    text = str(value or "").lower()
    tokens = re.findall(r"[a-z0-9]+", text)
    return {token for token in tokens if len(token) > 2 and token not in STOPWORDS}


def _first_present(mapping: Dict[str, Any], keys: Iterable[str], default: str = "") -> str:
    for key in keys:
        if key in mapping:
            value = str(mapping.get(key) or "").strip()
            if value:
                return value
    return default


def _diminishing_returns_combine(current: float, new_score: float) -> float:
    if current <= 0.0:
        return new_score * 0.5
    return 1.0 - (1.0 - current) * (1.0 - new_score * 0.5)


def _best_term_match(terms: set[str], candidates: set[str]) -> float:
    if not terms or not candidates:
        return 0.0
    best = 0.0
    for term in terms:
        for candidate in candidates:
            if term == candidate:
                score = 1.0
            elif term in candidate or candidate in term:
                score = 0.85 if min(len(term), len(candidate)) >= 4 else 0.65
            else:
                score = SequenceMatcher(None, term, candidate).ratio()
            if score > best:
                best = score
    return best


def _expand_with_bridges(base_term: str, bridges: Dict[str, set[str]]) -> set[str]:
    if not base_term:
        return set()
    expanded = {base_term}
    if base_term in bridges:
        expanded.update({_normalize(item) for item in bridges[base_term]})
    return expanded


def _normalized_tokens(value: str) -> set[str]:
    normalized = _normalize(value)
    if not normalized:
        return set()
    return set(part for part in normalized.split("_") if part)


def _framework_to_tier1_candidates(framework: str) -> set[str]:
    normalized = _normalize(framework).upper()
    if not normalized:
        return set()
    framework_tokens = set(part for part in normalized.split("_") if part)
    matches: set[str] = set()
    for tier1_id, indicators in TIER1_TAXONOMY.items():
        for indicator in indicators:
            ind_norm = _normalize(indicator).upper()
            ind_tokens = set(part for part in ind_norm.split("_") if part)
            if ind_norm == normalized:
                matches.add(tier1_id)
                break
            if ind_tokens and ind_tokens.issubset(framework_tokens):
                matches.add(tier1_id)
                break
    return matches


def _domains_from_tokens(tokens: set[str]) -> set[str]:
    domains: set[str] = set()
    for domain, keywords in DOMAIN_KEYWORDS.items():
        if tokens & keywords:
            domains.add(domain)
    return domains


def _canonicalize_declared_domain(raw: Any) -> set[str]:
    normalized = _normalize(raw)
    if not normalized:
        return set()
    mapped = DOMAIN_ALIAS_MAP.get(normalized)
    if mapped:
        return set(mapped)
    if normalized in ATTRIBUTE_DOMAIN_MAP:
        return set(ATTRIBUTE_DOMAIN_MAP[normalized])
    tokens = set(part for part in normalized.split("_") if part)
    return _domains_from_tokens(tokens)


def _extract_declared_template_domains(payload: dict[str, Any]) -> set[str]:
    declared: set[str] = set()
    for key in ("domain", "attribute_domain"):
        declared.update(_canonicalize_declared_domain(payload.get(key)))
    for tag in payload.get("domain_tags") or []:
        declared.update(_canonicalize_declared_domain(tag))
    return declared


def _infer_finding_domains(finding: "FindingRecord") -> set[str]:
    tokens = set()
    for env_term in _expand_with_bridges(finding.environment_id, ENV_BRIDGES):
        tokens.update(_normalized_tokens(env_term))
    for out_term in _expand_with_bridges(finding.outcome_id, OUTCOME_BRIDGES):
        tokens.update(_normalized_tokens(out_term))
    tokens.update(_tokenize(finding.content))
    return _domains_from_tokens(tokens)


def _infer_template_domains(
    frameworks: list[str],
    name: str,
    endpoint_terms: set[str],
    mechanism_terms: set[str],
    declared_domains: set[str],
) -> set[str]:
    tokens = set()
    for framework in frameworks:
        tokens.update(_normalized_tokens(framework))
    tokens.update(_tokenize(name))
    for term in endpoint_terms:
        tokens.update(_normalized_tokens(term))
    tokens.update(mechanism_terms)
    inferred = _domains_from_tokens(tokens)
    return inferred | declared_domains


def _domain_guard_multiplier(
    template_domains: set[str],
    finding_domains: set[str],
) -> tuple[float, str | None]:
    if not template_domains:
        return 1.0, None

    specific_domains = template_domains - GENERIC_TEMPLATE_DOMAINS
    if not specific_domains:
        return 1.0, None
    if not finding_domains:
        if "music" in specific_domains:
            return 0.18, "music-domain guard"
        return 1.0, None

    overlap = specific_domains & finding_domains
    if overlap:
        if "music" in specific_domains and "music" not in finding_domains:
            return 0.18, "music-domain guard"
        return 1.0, None

    if "music" in specific_domains and "acoustics" in finding_domains:
        return 0.12, "music-domain guard"

    return 0.35, "domain mismatch penalty"


@dataclass(frozen=True)
class FindingRecord:
    belief_id: str
    content: str
    environment_id: str
    outcome_id: str
    paper_ids: str = ""


@dataclass(frozen=True)
class TemplateProfile:
    template_id: str
    display_id: str
    name: str
    frameworks: list[str]
    input_terms: set[str]
    output_terms: set[str]
    endpoint_terms: set[str]
    mechanism_terms: set[str]
    domains: set[str]


@dataclass(frozen=True)
class TemplateCandidate:
    template_id: str
    display_id: str
    score: float
    reasons: list[str]


@dataclass(frozen=True)
class FindingResolution:
    belief_id: str
    environment_id: str
    outcome_id: str
    top_templates: list[TemplateCandidate]
    tier1_relevance: dict[str, float]
    tier2_relevance: dict[str, float]


@dataclass(frozen=True)
class ResolverConfig:
    min_template_score: float = 0.35
    top_k_templates: int = 5
    min_tier_support_score: float = 0.45
    persist_annotation_key: str = "template_relevance_v1"


def load_findings_from_web_db(db_path: Path) -> list[FindingRecord]:
    conn = sqlite3.connect(str(db_path))
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT belief_id, content, environment_id, outcome_id, paper_ids
            FROM beliefs
            """
        )
        rows = cur.fetchall()
    finally:
        conn.close()
    findings: list[FindingRecord] = []
    for belief_id, content, environment_id, outcome_id, paper_ids in rows:
        findings.append(
            FindingRecord(
                belief_id=str(belief_id),
                content=str(content or ""),
                environment_id=_normalize(environment_id),
                outcome_id=_normalize(outcome_id),
                paper_ids=str(paper_ids or ""),
            )
        )
    return findings


def load_template_profiles(templates_dir: Path) -> list[TemplateProfile]:
    profiles: list[TemplateProfile] = []
    for path in sorted(templates_dir.glob("*.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        template_id = str(payload.get("template_id") or path.stem)
        display_id = str(payload.get("display_id") or template_id)
        name = str(payload.get("name") or display_id)
        # Load frameworks from either framework_ids or t1_frameworks (most templates use t1_frameworks)
        frameworks = [str(item) for item in (payload.get("framework_ids") or payload.get("t1_frameworks") or []) if item]
        declared_domains = _extract_declared_template_domains(payload)

        input_terms: set[str] = set()
        output_terms: set[str] = set()
        endpoint_terms: set[str] = set()
        mechanism_terms: set[str] = set()

        mechanism_terms.update(_tokenize(payload.get("structural_pattern")))
        mechanism_terms.update(_tokenize(payload.get("higher_order_principle")))
        mechanism_terms.update(_tokenize(payload.get("short_description")))
        for framework in frameworks:
            mechanism_terms.update(_tokenize(framework))

        for link in payload.get("causal_links") or []:
            if not isinstance(link, dict):
                continue
            src = _normalize(
                _first_present(link, ["from_entity", "from_variable", "source", "from"])
            )
            dst = _normalize(
                _first_present(link, ["to_entity", "to_variable", "target", "to"])
            )
            from_level = _normalize(_first_present(link, ["from_level", "level", "source_level"]))
            to_level = _normalize(_first_present(link, ["to_level", "target_level", "bridging_to"]))
            endpoint_terms.update({term for term in (src, dst) if term})
            mechanism_terms.update(_tokenize(link.get("activity")))
            mechanism_terms.update(_tokenize(link.get("evidence_base")))
            mechanism_terms.update(_tokenize(link.get("key_evidence")))
            mechanism_terms.update(_tokenize(link.get("notes")))

            if src and from_level == "environmental":
                input_terms.add(src)
            if dst and to_level in OUTCOME_LEVELS:
                output_terms.add(dst)

        profiles.append(
            TemplateProfile(
                template_id=template_id,
                display_id=display_id,
                name=name,
                frameworks=frameworks,
                input_terms=input_terms,
                output_terms=output_terms,
                endpoint_terms=endpoint_terms,
                mechanism_terms=mechanism_terms,
                domains=_infer_template_domains(
                    frameworks,
                    name,
                    endpoint_terms,
                    mechanism_terms,
                    declared_domains,
                ),
            )
        )
    return profiles


def _score_template_for_finding(
    finding: FindingRecord,
    template: TemplateProfile,
) -> tuple[float, list[str]]:
    finding_domains = _infer_finding_domains(finding)
    env_terms = _expand_with_bridges(finding.environment_id, ENV_BRIDGES)
    out_terms = _expand_with_bridges(finding.outcome_id, OUTCOME_BRIDGES)
    content_terms = _tokenize(finding.content)

    env_target = template.input_terms | template.endpoint_terms
    out_target = template.output_terms | template.endpoint_terms

    env_score = _best_term_match(env_terms, env_target)
    out_score = _best_term_match(out_terms, out_target)
    bridge_score = max(
        _best_term_match(env_terms, template.endpoint_terms),
        _best_term_match(out_terms, template.endpoint_terms),
    )
    mechanism_overlap = 0.0
    if content_terms and template.mechanism_terms:
        overlap = len(content_terms & template.mechanism_terms)
        mechanism_overlap = min(1.0, overlap / max(4, min(len(content_terms), 12)))

    score = (
        0.42 * env_score
        + 0.33 * out_score
        + 0.17 * bridge_score
        + 0.08 * mechanism_overlap
    )

    domain_multiplier, domain_reason = _domain_guard_multiplier(template.domains, finding_domains)
    score *= domain_multiplier

    score = max(0.0, min(1.0, score))

    reasons: list[str] = []
    if env_score >= 0.65:
        reasons.append("environmental endpoint alignment")
    if out_score >= 0.65:
        reasons.append("outcome endpoint alignment")
    if bridge_score >= 0.60:
        reasons.append("latent bridge compatibility")
    if mechanism_overlap >= 0.25:
        reasons.append("mechanism text overlap")
    if domain_reason:
        reasons.append(domain_reason)
    return score, reasons


def _infer_tier1_from_claim(finding: FindingRecord) -> dict[str, float]:
    if infer_theory_relevance is None:
        return {}
    claim = {
        "statement": finding.content,
        "constructs": {
            "outcomes": [{"id": finding.outcome_id}],
            "environment_factors": [{"id": finding.environment_id}],
        },
    }
    try:
        raw = infer_theory_relevance(claim, outcome_lookup=None)
    except Exception:
        return {}
    normalized: dict[str, float] = {}
    for key, value in raw.items():
        raw_theory = str(key).strip()
        candidates = _framework_to_tier1_candidates(raw_theory)
        if not candidates:
            theory = _normalize(raw_theory).upper()
            if theory in TIER1_TAXONOMY:
                candidates = {theory}
        for candidate in candidates:
            normalized[candidate] = max(normalized.get(candidate, 0.0), float(value))
    return normalized


def resolve_finding(
    finding: FindingRecord,
    templates: list[TemplateProfile],
    config: ResolverConfig,
) -> FindingResolution:
    ranked: list[TemplateCandidate] = []
    for template in templates:
        score, reasons = _score_template_for_finding(finding, template)
        if score < config.min_template_score:
            continue
        ranked.append(
            TemplateCandidate(
                template_id=template.template_id,
                display_id=template.display_id,
                score=round(score, 4),
                reasons=reasons,
            )
        )
    ranked.sort(key=lambda item: (-item.score, item.display_id))
    top = ranked[: config.top_k_templates]

    tier1: dict[str, float] = _infer_tier1_from_claim(finding)
    tier2: dict[str, float] = {}
    by_display = {template.display_id: template for template in templates}

    for candidate in top:
        if float(candidate.score) < config.min_tier_support_score:
            continue
        profile = by_display.get(candidate.display_id)
        if not profile:
            continue
        weight = float(candidate.score)
        for framework in profile.frameworks:
            framework_key = _normalize(framework).upper()
            if not framework_key:
                continue
            tier2[framework_key] = _diminishing_returns_combine(tier2.get(framework_key, 0.0), weight)
            for tier1_id in _framework_to_tier1_candidates(framework):
                tier1[tier1_id] = _diminishing_returns_combine(tier1.get(tier1_id, 0.0), weight)

    tier1_sorted = {
        key: round(value, 4)
        for key, value in sorted(tier1.items(), key=lambda item: (-item[1], item[0]))
        if value > 0.0
    }
    tier2_sorted = {
        key: round(value, 4)
        for key, value in sorted(tier2.items(), key=lambda item: (-item[1], item[0]))
        if value > 0.0
    }

    return FindingResolution(
        belief_id=finding.belief_id,
        environment_id=finding.environment_id,
        outcome_id=finding.outcome_id,
        top_templates=top,
        tier1_relevance=tier1_sorted,
        tier2_relevance=tier2_sorted,
    )


def resolve_findings(
    findings: list[FindingRecord],
    templates: list[TemplateProfile],
    config: ResolverConfig,
) -> dict[str, Any]:
    resolutions = [resolve_finding(finding, templates, config) for finding in findings]
    findings_with_templates = [item for item in resolutions if item.top_templates]
    findings_with_tier1 = [item for item in resolutions if item.tier1_relevance]
    unique_templates = {
        candidate.display_id
        for resolution in resolutions
        for candidate in resolution.top_templates
    }
    unique_tier2 = {
        framework
        for resolution in resolutions
        for framework in resolution.tier2_relevance.keys()
    }
    total_candidate_links = sum(len(item.top_templates) for item in resolutions)
    avg_links = total_candidate_links / len(resolutions) if resolutions else 0.0

    return {
        "summary": {
            "findings_total": len(resolutions),
            "findings_with_template_candidates": len(findings_with_templates),
            "findings_with_tier1_relevance": len(findings_with_tier1),
            "unique_templates_linked": len(unique_templates),
            "unique_tier2_frameworks_linked": len(unique_tier2),
            "candidate_template_links_total": total_candidate_links,
            "candidate_template_links_avg": round(avg_links, 4),
        },
        "resolutions": [asdict(item) for item in resolutions],
    }


def write_resolution_output(payload: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=False), encoding="utf-8")


def persist_relevance_to_web_db(
    db_path: Path,
    payload: dict[str, Any],
    *,
    annotation_key: str = "template_relevance_v1",
) -> dict[str, int]:
    conn = sqlite3.connect(str(db_path))
    try:
        cur = conn.cursor()
        cur.execute("PRAGMA table_info(beliefs)")
        cols = {row[1] for row in cur.fetchall()}
        if "epistemic_v2" not in cols:
            cur.execute("ALTER TABLE beliefs ADD COLUMN epistemic_v2 TEXT")
            cols.add("epistemic_v2")
        has_updated_at = "updated_at" in cols

        updated = 0
        missing = 0
        now_iso = datetime.now(timezone.utc).isoformat()
        for resolution in payload.get("resolutions", []):
            belief_id = str(resolution.get("belief_id") or "").strip()
            if not belief_id:
                continue
            row = cur.execute(
                "SELECT epistemic_v2 FROM beliefs WHERE belief_id = ?",
                (belief_id,),
            ).fetchone()
            if row is None:
                missing += 1
                continue
            existing_raw = row[0]
            existing = {}
            if existing_raw:
                try:
                    existing = json.loads(existing_raw)
                except Exception:
                    existing = {}
            existing[annotation_key] = {
                "schema_version": 1,
                "updated_at_utc": now_iso,
                "environment_id": resolution.get("environment_id"),
                "outcome_id": resolution.get("outcome_id"),
                "top_templates": resolution.get("top_templates", []),
                "tier1_relevance": resolution.get("tier1_relevance", {}),
                "tier2_relevance": resolution.get("tier2_relevance", {}),
            }
            serialized = json.dumps(existing, sort_keys=True)
            if has_updated_at:
                cur.execute(
                    "UPDATE beliefs SET epistemic_v2 = ?, updated_at = ? WHERE belief_id = ?",
                    (serialized, now_iso, belief_id),
                )
            else:
                cur.execute(
                    "UPDATE beliefs SET epistemic_v2 = ? WHERE belief_id = ?",
                    (serialized, belief_id),
                )
            updated += 1
        conn.commit()
        return {"updated_beliefs": updated, "missing_beliefs": missing}
    finally:
        conn.close()
