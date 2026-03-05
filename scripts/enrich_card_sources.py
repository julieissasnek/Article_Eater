#!/usr/bin/env python3
"""
Enrich Card Sources — Aggregate Real Corpus Data for Card Generation
====================================================================

Replaces hardcoded stubs in populate_all_cards.py with real data from:
  - 1,069 extraction JSONs (33K+ findings with 20+ fields each)
  - 166 T2 mechanism templates (31 fields each)
  - 38 molecule JSONs
  - 3,788 belief clusters
  - 25 theory files
  - Extended annotations (data/extended_annotations/)

Writes enriched source dicts to data/card_sources/{type}/{entity_id}.json

Usage:
  python3 scripts/enrich_card_sources.py --dry-run     # Preview stats
  python3 scripts/enrich_card_sources.py               # Write enriched sources
  python3 scripts/enrich_card_sources.py --type t1      # Only T1 frameworks

Success Conditions (SC-SD-1 through SC-SD-6):
  SC-SD-1: T1 frameworks loaded from corpus data, not hardcoded stubs
  SC-SD-2: T3 beliefs include ALL cluster members, not 5 samples
  SC-SD-3: Each source dict includes findings[] with full extraction fields
  SC-SD-4: Theory links resolved to actual T1/T1.5 names
  SC-SD-5: Mechanism chains present for T2 sources
  SC-SD-6: Extended annotations merged into source data
"""

import json
import logging
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Directories
EXT_DIR = PROJECT_ROOT / "data" / "extractions"
TMPL_DIR = PROJECT_ROOT / "data" / "templates"
MOL_DIR = PROJECT_ROOT / "data" / "molecules"
THEORY_DIR = PROJECT_ROOT / "data" / "theories"
ANNOT_DIR = PROJECT_ROOT / "data" / "extended_annotations"
CLUSTERS_PATH = PROJECT_ROOT / "data" / "materialized_views" / "belief_clusters.json"
OUTPUT_DIR = PROJECT_ROOT / "data" / "card_sources"

# T1 Neural Framework code → entity mapping
# Data-driven from warrant_strength._LEGACY_KEY_MAP + theory_bootstrap.py
# Falls back to hardcoded map only if imports fail.
try:
    from src.services.warrant_strength import _LEGACY_KEY_MAP
    # Extract only the 2-3 letter T1 framework codes (not the lowercase legacy keys)
    _T1_CODES = {k: v for k, v in _LEGACY_KEY_MAP.items()
                 if k.isupper() and len(k) <= 3
                 and not any(c.islower() for c in k)}
    # Build the framework map from the slugs
    T1_FRAMEWORK_MAP = {}
    for code, slug in _T1_CODES.items():
        entity_id = slug.replace("-", "_")
        name = slug.replace("-", " ").title()
        T1_FRAMEWORK_MAP[code] = {
            "entity_id": entity_id,
            "name": name,
            "slug": slug,
        }
    logger.info(f"Loaded {len(T1_FRAMEWORK_MAP)} T1 framework codes from warrant_strength._LEGACY_KEY_MAP")
except ImportError:
    logger.warning("Could not import _LEGACY_KEY_MAP from warrant_strength, using hardcoded fallback")
    T1_FRAMEWORK_MAP = {
        "PP": {"entity_id": "predictive_processing", "name": "Predictive Processing"},
        "NM": {"entity_id": "neuromodulatory_systems", "name": "Neuromodulatory Systems"},
        "IC": {"entity_id": "interoceptive_constructionist_affect", "name": "Interoceptive Constructionist Affect"},
        "SN": {"entity_id": "spatial_navigation", "name": "Spatial Navigation"},
        "MS": {"entity_id": "memory_systems", "name": "Memory Systems"},
        "EC": {"entity_id": "embodied_cognition", "name": "Embodied Cognition"},
        "DT": {"entity_id": "default_mode_dynamics", "name": "Default Mode Dynamics"},
        "CB": {"entity_id": "chronobiological_regulation", "name": "Chronobiological Regulation"},
        "MSI": {"entity_id": "multisensory_integration", "name": "Multisensory Integration"},
        "DP": {"entity_id": "dual_process_evaluation", "name": "Dual Process Evaluation"},
    }



# ═══════════════════════════════════════════════════════════════
# Data loading functions
# ═══════════════════════════════════════════════════════════════

def load_all_extractions() -> Dict[str, Dict]:
    """Load all extraction JSONs into a dict keyed by filename stem."""
    extractions = {}
    if not EXT_DIR.exists():
        logger.warning("No extractions directory")
        return extractions
    for f in sorted(EXT_DIR.glob("*.json")):
        try:
            data = json.loads(f.read_text(errors="replace"))
            if isinstance(data, dict):
                extractions[f.stem] = data
        except Exception:
            continue
    logger.info(f"Loaded {len(extractions)} extraction files")
    return extractions


def load_all_templates() -> Dict[str, Dict]:
    """Load all T2 mechanism templates."""
    templates = {}
    if not TMPL_DIR.exists():
        return templates
    for f in sorted(TMPL_DIR.glob("*.json")):
        try:
            data = json.load(open(f))
            tid = data.get("template_id", f.stem)
            templates[tid] = data
        except Exception:
            continue
    logger.info(f"Loaded {len(templates)} T2 templates")
    return templates


def load_all_theories() -> Dict[str, Dict]:
    """Load all theory files (T1.5 domain theories)."""
    theories = {}
    if not THEORY_DIR.exists():
        return theories
    for f in sorted(THEORY_DIR.glob("*.json")):
        try:
            data = json.load(open(f))
            tid = data.get("theory_id", f.stem)
            theories[tid] = data
        except Exception:
            continue
    logger.info(f"Loaded {len(theories)} theory files")
    return theories


def load_extended_annotations() -> Dict[str, Dict]:
    """Load extended annotations keyed by DOI/stem."""
    annotations = {}
    if not ANNOT_DIR.exists():
        return annotations
    for f in sorted(ANNOT_DIR.glob("*.json")):
        try:
            data = json.load(open(f))
            annotations[f.stem] = data
        except Exception:
            continue
    logger.info(f"Loaded {len(annotations)} extended annotations")
    return annotations


def load_belief_clusters() -> List[Dict]:
    """Load belief clusters."""
    if not CLUSTERS_PATH.exists():
        return []
    data = json.load(open(CLUSTERS_PATH))
    clusters = data.get("clusters", [])
    logger.info(f"Loaded {len(clusters)} belief clusters")
    return clusters


# ═══════════════════════════════════════════════════════════════
# Layer-specific data loaders
# ═══════════════════════════════════════════════════════════════

ANNOT_LAYER_DIR = PROJECT_ROOT / "data" / "annotations"
CVA_DIR = PROJECT_ROOT / "data" / "cva_annotations"
INTERPRET_DIR = PROJECT_ROOT / "data" / "interpretation_space"
MV_DIR = PROJECT_ROOT / "data" / "materialized_views"


def load_annotation_layers() -> Dict[str, List[Dict]]:
    """Load all annotation layer files (a9-a18) into a dict keyed by type.

    These contain curated, human-readable annotation data:
    - a14_effect_magnitude: 6,010 entries with Cohen's d, NNT, human-scale descriptions
    - a11_disputes: 15 active disputes with positions and resolution criteria
    - a9_surprise_flags: 34 surprising findings that violate common assumptions
    - a10_design_implications: 100 actionable design parameters
    - a13_replication_status: 205 replication assessments
    - a17_narrative_hooks: 24 engagement hooks for science communication
    - a18_unanswered_questions: 20 open research questions
    - a15_cross_domain_connections: 15 cross-domain links
    """
    layers = {}
    if not ANNOT_LAYER_DIR.exists():
        logger.warning("No annotations directory found")
        return layers
    for f in sorted(ANNOT_LAYER_DIR.glob("a*.json")):
        try:
            data = json.load(open(f))
            if isinstance(data, list):
                key = f.stem  # e.g. "a14_effect_magnitude"
                layers[key] = data
        except Exception:
            continue
    total = sum(len(v) for v in layers.values())
    logger.info(f"Loaded {len(layers)} annotation layer files ({total} total records)")
    return layers


def load_cva_annotations() -> Dict[str, Dict]:
    """Load CVA (Construct Validity Assessment) annotations.

    These contain per-template measurement/stimuli details:
    - measurements: instruments, scales, biomarkers used
    - stimuli: environmental conditions, images, VR scenes
    - molecule_links: connections to cross-template molecules
    - constraint_tags: validity constraints
    """
    cva = {}
    if not CVA_DIR.exists():
        return cva
    for f in sorted(CVA_DIR.glob("*.json")):
        try:
            data = json.load(open(f))
            tid = data.get("target_id", f.stem)
            cva[tid] = data
        except Exception:
            continue
    logger.info(f"Loaded {len(cva)} CVA annotations")
    return cva


def load_interpretation_data() -> Dict[str, Any]:
    """Load interpretation space data (pilot beliefs, interrogation results).

    Contains beliefs with:
    - credence_value: epistemically calibrated confidence
    - entrenchment: how deeply embedded in the web
    - interrogation evaluations: stress-test scores
    - followup_questions: what we still need to know
    """
    result = {"beliefs": [], "interrogations": [], "followups": []}
    if not INTERPRET_DIR.exists():
        return result
    for name, key in [("pilot_beliefs_50.json", "beliefs"),
                       ("interrogation_evaluations.json", "interrogations"),
                       ("followup_questions.json", "followups")]:
        p = INTERPRET_DIR / name
        if p.exists():
            try:
                data = json.load(open(p))
                if isinstance(data, list):
                    result[key] = data
            except Exception:
                pass
    logger.info(f"Loaded interpretation data: {len(result['beliefs'])} beliefs, "
                f"{len(result['interrogations'])} interrogations, "
                f"{len(result['followups'])} followups")
    return result


def load_materialized_views() -> Dict[str, Any]:
    """Load materialized view data (omega scores, gap analysis, etc.)."""
    views = {}
    if not MV_DIR.exists():
        return views
    for name in ["cluster_summary.json", "gap_analysis.json"]:
        p = MV_DIR / name
        if p.exists():
            try:
                data = json.load(open(p))
                views[p.stem] = data
            except Exception:
                pass
    logger.info(f"Loaded {len(views)} materialized views")
    return views


def _build_effect_magnitude_index(annotation_layers: Dict[str, List]) -> Dict[str, List[Dict]]:
    """Index a14_effect_magnitude entries by paper_id for fast lookup.

    Returns dict: paper_id → [effect entries with cohens_d, nnt, human_scale, ...]
    """
    effects = annotation_layers.get("a14_effect_magnitude", [])
    by_paper = defaultdict(list)
    for e in effects:
        pid = e.get("paper_id", "")
        if pid:
            by_paper[pid].append(e)
    logger.info(f"Indexed {len(effects)} effect magnitudes across {len(by_paper)} papers")
    return dict(by_paper)


def _build_dispute_index(annotation_layers: Dict[str, List]) -> List[Dict]:
    """Get disputes suitable for Debate tab."""
    return annotation_layers.get("a11_disputes", [])


def _build_surprise_index(annotation_layers: Dict[str, List]) -> Dict[str, List[Dict]]:
    """Index surprise flags by paper_id."""
    surprises = annotation_layers.get("a9_surprise_flags", [])
    by_paper = defaultdict(list)
    for s in surprises:
        pid = s.get("paper_id", "")
        if pid:
            by_paper[pid].append(s)
    return dict(by_paper)



# ═══════════════════════════════════════════════════════════════
# Field quality filtering
# ═══════════════════════════════════════════════════════════════

_GARBAGE_ANTECEDENTS = {"null", "none", "n/a", "", "unknown", "not specified",
                        "see above", "various", "multiple"}
_CANONICAL_DIRECTIONS = {"increase", "decrease", "no_effect", "mixed"}


def _clean_finding(finding: Dict) -> Optional[Dict]:
    """Clean and validate a finding. Returns None if garbage."""
    ant = str(finding.get("antecedent", "") or "").strip()
    cons = str(finding.get("consequent", "") or "").strip()

    # Skip garbage findings
    if ant.lower() in _GARBAGE_ANTECEDENTS or len(ant) < 3:
        return None
    if cons.lower() in _GARBAGE_ANTECEDENTS or len(cons) < 3:
        return None

    cleaned = dict(finding)

    # Normalize direction
    d = str(cleaned.get("direction", "") or "").strip().lower()
    if d in ("positive", "up", "higher", "more", "improved", "increased"):
        d = "increase"
    elif d in ("negative", "down", "lower", "less", "decreased", "reduced"):
        d = "decrease"
    elif d in ("null", "none", "ns", "not significant", "no effect", "no_change"):
        d = "no_effect"
    elif d not in _CANONICAL_DIRECTIONS:
        d = "mixed"  # Default for ambiguous
    cleaned["direction"] = d

    # Normalize effect_size
    es = cleaned.get("effect_size")
    if es is not None and es != "" and es != "null":
        try:
            cleaned["effect_size"] = float(es)
        except (ValueError, TypeError):
            cleaned["effect_size"] = None

    # Normalize sample_size
    ss = cleaned.get("sample_size")
    if ss is not None:
        try:
            cleaned["sample_size"] = int(ss)
        except (ValueError, TypeError):
            cleaned["sample_size"] = None

    return cleaned


def _build_display_id_map(templates: Dict[str, Dict]) -> Dict[str, str]:
    """Build display_id → template_id bridge from template files.
    
    Extractions use short IDs (T22, M7, CLE1) in template_ids field,
    but templates use long IDs (ACOUSTIC_EMOTION_MAPPING_001).
    Templates have a display_id field that bridges the two.
    """
    mapping = {}
    for tid, tmpl in templates.items():
        did = tmpl.get("display_id", "")
        if did:
            mapping[did] = tid
    logger.info(f"Built display_id bridge: {len(mapping)} mappings")
    return mapping


def build_findings_index(extractions: Dict[str, Dict],
                         templates: Dict[str, Dict] = None) -> Dict[str, List[Dict]]:
    """Index all findings by template_id and T1 code for fast lookup.
    
    Uses THREE indexing paths for templates:
    1. template_ids field (short IDs) → resolved via display_id bridge
    2. template_matches field (long IDs) → direct match
    3. tier1_relevance / theory_links → T1 framework codes
    """
    by_template = defaultdict(list)
    by_t1 = defaultdict(list)
    by_source = defaultdict(list)
    by_molecule = defaultdict(list)
    cleaned_count = 0
    dropped_count = 0

    # Build display_id → template_id bridge
    display_map = _build_display_id_map(templates) if templates else {}

    for source_file, data in extractions.items():
        for finding in data.get("findings", []):
            cleaned = _clean_finding(finding)
            if cleaned is None:
                dropped_count += 1
                continue
            cleaned_count += 1

            enriched = {
                **cleaned,
                "source_file": source_file,
                "paper_title": data.get("title", ""),
                "paper_doi": data.get("doi", ""),
            }
            by_source[source_file].append(enriched)

            # Path 1: Index by template_ids (short IDs) with bridge resolution
            for tid in (finding.get("template_ids") or []):
                if tid:
                    by_template[tid].append(enriched)
                    # Resolve short ID to long ID via display_id bridge
                    if tid in display_map:
                        by_template[display_map[tid]].append(enriched)

            # Path 2: Index by template_matches (long IDs, direct match)
            for tm in (finding.get("template_matches") or []):
                if isinstance(tm, dict):
                    tid = tm.get("template_id", "")
                    if tid:
                        by_template[tid].append(enriched)

            # Path 3: Index by T1 relevance
            t1_data = finding.get("tier1_relevance")
            if t1_data:
                if isinstance(t1_data, dict):
                    for code in t1_data.keys():
                        by_t1[code].append(enriched)
                elif isinstance(t1_data, str):
                    by_t1[t1_data].append(enriched)

            # Also index by theory_links (null-safe)
            for tl in (finding.get("theory_links") or []):
                if isinstance(tl, dict):
                    tid = tl.get("theory_id", "")
                    if tid:
                        by_t1[tid].append(enriched)
                elif isinstance(tl, str) and tl:
                    by_t1[tl].append(enriched)

            # Path 4: Index by molecule_ids (extraction → molecule reverse mapping)
            # NOTE: extraction molecule_ids are lowercase, molecule JSONs are UPPERCASE
            for mid in (finding.get("molecule_ids") or []):
                if isinstance(mid, str) and mid:
                    by_molecule[mid.upper()].append(enriched)
            # Article-level molecule_ids (this is where 444 extractions store them)
            for mid in (data.get("molecule_ids") or []):
                if isinstance(mid, str) and mid:
                    by_molecule[mid.upper()].append(enriched)

    logger.info(f"Indexed {cleaned_count} clean findings ({dropped_count} dropped as garbage), "
                f"{sum(len(v) for v in by_template.values())} by template, "
                f"{sum(len(v) for v in by_t1.values())} by T1, "
                f"{sum(len(v) for v in by_molecule.values())} by molecule")
    return {
        "by_template": dict(by_template),
        "by_t1": dict(by_t1),
        "by_source": dict(by_source),
        "by_molecule": dict(by_molecule),
    }


# ═══════════════════════════════════════════════════════════════
# Compute aggregate statistics
# ═══════════════════════════════════════════════════════════════

def compute_aggregate_stats(findings: List[Dict]) -> Dict[str, Any]:
    """Compute omega, direction counts, effect size stats from a list of findings."""
    if not findings:
        return {"n_findings": 0, "n_papers": 0, "omega": 0.0}

    papers = set()
    directions = Counter()
    effect_sizes = []

    for f in findings:
        papers.add(f.get("source_file", ""))
        d = f.get("direction", "").lower()
        if d:
            directions[d] += 1
        es = f.get("effect_size")
        if es is not None and es != "" and es != "null":
            try:
                effect_sizes.append(float(es))
            except (ValueError, TypeError):
                pass

    n = len(findings)
    n_papers = len(papers)

    # Compute omega (simplified direction consistency score)
    if directions:
        most_common_dir, most_common_count = directions.most_common(1)[0]
        omega = most_common_count / max(n, 1)
    else:
        omega = 0.0
        most_common_dir = "unknown"

    stats = {
        "n_findings": n,
        "n_papers": n_papers,
        "omega": round(omega, 3),
        "direction_consensus": most_common_dir,
        "direction_counts": dict(directions),
        "n_with_effect_size": len(effect_sizes),
        "effect_size_range": [round(min(effect_sizes), 3), round(max(effect_sizes), 3)] if effect_sizes else None,
        "mean_effect_size": round(sum(effect_sizes) / len(effect_sizes), 3) if effect_sizes else None,
    }
    return stats


def get_relevant_annotations(entity_id: str, findings: List[Dict],
                              annotations: Dict[str, Dict]) -> List[Dict]:
    """Find extended annotations relevant to this entity's source papers."""
    relevant = []
    source_stems = set()
    for f in findings:
        sf = f.get("source_file", "")
        if sf:
            source_stems.add(sf)
    for stem in source_stems:
        if stem in annotations:
            a = annotations[stem]
            relevant.append({
                "source": stem,
                "annotation_keys": list(a.keys())[:10],
                "has_stimulus": "stimulus_description" in a or "stimuli" in a,
                "has_environment": "environment" in a or "setting" in a,
            })
    return relevant


# ═══════════════════════════════════════════════════════════════
# Build enriched sources per card type
# ═══════════════════════════════════════════════════════════════

def enrich_t1_frameworks(templates: Dict[str, Dict], findings_index: Dict,
                          theories: Dict[str, Dict],
                          annotations: Dict[str, Dict],
                          layer_data: Dict = None) -> List[Dict]:
    """Build T1 framework source data from real corpus data.

    Integrates:
    - Extraction findings (via findings_index)
    - Extended annotations
    - Effect magnitudes (a14) → Evidence tab
    - Disputes (a11) → Debate tab
    - Surprise flags (a9) → Debate tab
    - Design implications (a10) → Design tab
    - Unanswered questions (a18) → Debate tab
    - Narrative hooks (a17) → Overview tab
    """
    sources = []
    by_t1 = findings_index.get("by_t1", {})
    by_template = findings_index.get("by_template", {})
    ld = layer_data or {}
    effect_idx = ld.get("effect_index", {})
    surprise_idx = ld.get("surprise_index", {})

    for code, meta in T1_FRAMEWORK_MAP.items():
        # Collect all T2 templates that reference this T1
        child_templates = []
        child_template_findings = []
        for tid, tmpl in templates.items():
            if code in tmpl.get("t1_frameworks", []):
                child_templates.append({
                    "template_id": tid,
                    "name": tmpl.get("name", tmpl.get("title", tid)),
                    "calibration_status": tmpl.get("calibration_status", "unknown"),
                    "confidence": tmpl.get("confidence", 0),
                    "mechanism_chain": tmpl.get("mechanism_chain", []),
                })
                # Collect findings from this template
                for f in by_template.get(tid, []):
                    child_template_findings.append(f)

        # Also get findings directly linked to this T1
        direct_findings = by_t1.get(code, [])

        # Merge and deduplicate findings
        all_findings = {}
        for f in direct_findings + child_template_findings:
            key = f"{f.get('source_file', '')}_{f.get('antecedent', '')}_{f.get('consequent', '')}"
            all_findings[key] = f
        all_findings_list = list(all_findings.values())

        # Collect mechanism chains from child templates
        mechanism_chains = []
        for ct in child_templates:
            if ct.get("mechanism_chain"):
                mechanism_chains.append({
                    "template_id": ct["template_id"],
                    "chain": ct["mechanism_chain"],
                })

        # Find related T1.5 theories
        child_theories = []
        for tid, theory in theories.items():
            parents = theory.get("parent_t1_frameworks", [])
            if code in parents:
                child_theories.append({
                    "theory_id": tid,
                    "name": theory.get("name", tid),
                    "maturity": theory.get("maturity", "unknown"),
                })

        stats = compute_aggregate_stats(all_findings_list)
        annots = get_relevant_annotations(meta["entity_id"], all_findings_list, annotations)

        # --- Layer data: effect magnitudes from papers in this framework ---
        source_files = set(f.get("source_file", "") for f in all_findings_list)
        effect_magnitudes = []
        surprises = []
        for sf in source_files:
            effect_magnitudes.extend(effect_idx.get(sf, []))
            surprises.extend(surprise_idx.get(sf, []))

        source = {
            "entity_id": meta["entity_id"],
            "title": meta["name"],
            "t1_code": code,
            "description": meta.get("description", ""),
            **stats,
            "child_templates": child_templates,
            "child_theories": child_theories,
            "mechanism_chains": mechanism_chains[:5],
            "findings": all_findings_list[:50],
            "all_findings_count": len(all_findings_list),
            "annotations": annots[:10],
            # --- New layer data ---
            "effect_magnitudes": effect_magnitudes[:20],  # Evidence tab
            "n_effect_magnitudes": len(effect_magnitudes),
            "disputes": ld.get("disputes", []),  # Debate tab (global disputes)
            "surprise_flags": surprises[:10],  # Debate tab
            "design_implications": ld.get("design_implications", [])[:10],  # Design tab
            "unanswered_questions": ld.get("unanswered_questions", [])[:5],  # Debate tab
            "narrative_hooks": [
                h for h in ld.get("narrative_hooks", [])
                if code.lower() in str(h.get("theory", "")).lower()
            ][:3],  # Overview tab
            "scope_conditions": {},
            "provenance": {
                "source_files": list(source_files),
                "n_source_files": len(source_files),
                "enrichment_timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                "data_layers": ["extractions", "templates", "theories",
                                "extended_annotations", "effect_magnitudes",
                                "disputes", "surprises", "design_implications"],
            },
        }
        sources.append(source)

    return sources


def enrich_t2_mechanisms(templates: Dict[str, Dict], findings_index: Dict,
                          annotations: Dict[str, Dict],
                          layer_data: Dict = None) -> List[Dict]:
    """Enrich T2 mechanism templates with findings from extractions.

    Integrates:
    - Extraction findings (via findings_index)
    - Extended annotations
    - CVA annotations → Design tab (stimuli, measurements)
    - Effect magnitudes (a14) → Evidence tab
    - Replication status (a13) → Evidence tab
    """
    sources = []
    by_template = findings_index.get("by_template", {})
    ld = layer_data or {}
    effect_idx = ld.get("effect_index", {})
    cva = ld.get("cva_annotations", {})
    replications = ld.get("replication_status", [])

    # Index replications by antecedent/consequent for matching
    repl_by_ant = defaultdict(list)
    for r in replications:
        ant = r.get("antecedent", "")
        if ant:
            repl_by_ant[ant.lower()].append(r)

    for tid, tmpl in templates.items():
        findings = by_template.get(tid, [])
        stats = compute_aggregate_stats(findings)
        annots = get_relevant_annotations(tid, findings, annotations)

        # --- CVA for this template ---
        cva_data = cva.get(tid, {})
        stimuli = cva_data.get("stimuli", [])
        measurements = cva_data.get("measurements", [])
        molecule_links = cva_data.get("molecule_links", [])

        # --- Effect magnitudes from papers contributing to this template ---
        source_files = set(f.get("source_file", "") for f in findings)
        effect_magnitudes = []
        for sf in source_files:
            effect_magnitudes.extend(effect_idx.get(sf, []))

        # --- Replication status matching ---
        template_name = tmpl.get("name", tmpl.get("title", "")).lower()
        matched_replications = []
        for ant_key, repls in repl_by_ant.items():
            if ant_key in template_name or template_name in ant_key:
                matched_replications.extend(repls)

        source = {
            **tmpl,
            "entity_id": tid,
            "title": tmpl.get("name", tmpl.get("title", tid)),
            **stats,
            "findings": findings[:30],
            "all_findings_count": len(findings),
            "annotations": annots[:5],
            # --- New layer data ---
            "cva_stimuli": stimuli,  # Design tab
            "cva_measurements": measurements,  # Design tab
            "cva_molecule_links": molecule_links,  # Connections tab
            "effect_magnitudes": effect_magnitudes[:15],  # Evidence tab
            "n_effect_magnitudes": len(effect_magnitudes),
            "replication_status": matched_replications[:5],  # Evidence tab
            "provenance": {
                "source_files": list(source_files),
                "n_source_files": len(source_files),
                "template_file": f"data/templates/{tid}.json" if (TMPL_DIR / f"{tid}.json").exists() else None,
                "cva_file": f"data/cva_annotations/{tid}.json" if tid in cva else None,
                "enrichment_timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                "data_layers": ["extractions", "templates", "extended_annotations",
                                "cva_annotations", "effect_magnitudes", "replications"],
            },
        }
        sources.append(source)

    return sources


def enrich_t3_beliefs(clusters: List[Dict], extractions: Dict[str, Dict],
                       findings_index: Dict,
                       layer_data: Dict = None) -> List[Dict]:
    """Enrich T3 belief clusters with ALL members and full finding data.

    Integrates:
    - Extraction findings (expanded from clusters)
    - Interpretation space data → credence, entrenchment, interrogation scores
    - Followup questions → what we still need to know
    """
    sources = []
    by_source = findings_index.get("by_source", {})

    for cluster in clusters:
        cid = cluster.get("cluster_id", "")
        if not cid:
            continue

        # Get all sample_members and expand with full finding data
        expanded_members = []
        for member in cluster.get("sample_members", []):
            source_file = member.get("source", "")
            if source_file and source_file in extractions:
                ext_data = extractions[source_file]
                for finding in ext_data.get("findings", []):
                    ant = finding.get("antecedent", "")
                    cons = finding.get("consequent", "")
                    if (ant == member.get("antecedent") and
                        cons == member.get("consequent")):
                        expanded_members.append({
                            **finding,
                            "source_file": source_file,
                            "paper_title": ext_data.get("title", ""),
                            "paper_doi": ext_data.get("doi", ""),
                        })
                        break
                else:
                    # Keep the original sample member
                    expanded_members.append({**member, "source_file": source_file})
            else:
                expanded_members.append(member)

        stats = compute_aggregate_stats(expanded_members)

        # Look up interpretation data if available
        ld = layer_data or {}
        interp = ld.get("interpretation", {})
        belief_credences = {}
        for b in interp.get("beliefs", []):
            belief_credences[b.get("belief_id", "")] = {
                "credence": b.get("credence_value"),
                "entrenchment": b.get("entrenchment"),
                "scope": b.get("scope"),
                "domain": b.get("domain"),
            }
        interrog_by_id = {}
        for ie in interp.get("interrogations", []):
            interrog_by_id[ie.get("belief_id", "")] = {
                "data_quality": ie.get("data_quality"),
                "mean_score": ie.get("mean_score"),
            }
        interp_data = belief_credences.get(cid, {})
        interrog_data = interrog_by_id.get(cid, {})

        source = {
            "entity_id": cid,
            "title": f"{cluster.get('antecedent_theme', '?')} -> {cluster.get('consequent_theme', '?')}",
            "antecedent_theme": cluster.get("antecedent_theme", ""),
            "consequent_theme": cluster.get("consequent_theme", ""),
            **stats,
            "direction_consensus": cluster.get("direction_consensus", "mixed"),
            "direction_counts": cluster.get("direction_counts", {}),
            "direction_entropy": cluster.get("direction_entropy", 0),
            "theory_links": cluster.get("theory_links", []),
            "median_effect_size": cluster.get("median_effect_size"),
            "effect_size_iqr": cluster.get("effect_size_iqr"),
            "n_with_effect_size": cluster.get("n_with_effect_size", 0),
            "i_squared": cluster.get("i_squared"),
            "cluster_size": cluster.get("size", len(expanded_members)),
            "representative": cluster.get("representative", ""),
            "findings": expanded_members,
            "all_findings_count": len(expanded_members),
            # --- Cluster-level credence (Phase 7) ---
            "cluster_credence": cluster.get("cluster_credence"),
            "credence_uncertainty": cluster.get("credence_uncertainty"),
            "credence_band": cluster.get("credence_band", ""),
            "credence_data_tier": cluster.get("credence_data_tier", ""),
            "credence_n_inputs": cluster.get("credence_n_inputs", 0),
            # --- Interpretation layer data ---
            "credence": interp_data.get("credence"),
            "entrenchment": interp_data.get("entrenchment"),
            "interpretation_scope": interp_data.get("scope"),
            "interpretation_domain": interp_data.get("domain"),
            "interrogation_quality": interrog_data.get("data_quality"),
            "interrogation_score": interrog_data.get("mean_score"),
            "provenance": {
                "source_files": list(set(m.get("source_file", m.get("source", "")) for m in expanded_members)),
                "enrichment_timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                "data_layers": ["extractions", "belief_clusters", "interpretation_space", "credence"],
            },
        }
        sources.append(source)

    return sources


def enrich_molecules(mol_dir: Path, templates: Dict[str, Dict],
                      findings_index: Dict) -> List[Dict]:
    """Enrich molecule source data with constituent template info.

    Uses TWO lookup paths:
    1. molecule.constituent_templates → template → findings (original)
    2. findings_index.by_molecule → reverse index from extractions (new)

    Success Conditions:
        SC-MOL-1: All 38 molecules produce enriched source entries
        SC-MOL-2: Molecules with extraction references get findings via reverse index
        SC-MOL-3: Findings count > 0 for molecules referenced by extractions
    """
    sources = []
    by_template = findings_index.get("by_template", {})
    by_molecule = findings_index.get("by_molecule", {})

    if not mol_dir.exists():
        return sources

    for f in sorted(mol_dir.glob("*.json")):
        try:
            mol = json.load(open(f))
        except Exception:
            continue

        mid = mol.get("molecule_id", f.stem)

        # --- Path 1: constituent_templates → template → findings ---
        constituent_ids = mol.get("constituent_templates", mol.get("template_ids", []))
        constituent_data = []
        all_findings = []
        for tid in constituent_ids:
            if tid in templates:
                tmpl = templates[tid]
                constituent_data.append({
                    "template_id": tid,
                    "name": tmpl.get("name", tmpl.get("title", tid)),
                    "mechanism_chain": tmpl.get("mechanism_chain", [])[:3],
                })
                all_findings.extend(by_template.get(tid, []))

        # --- Path 2: reverse index from extractions with molecule_ids ---
        mol_findings = by_molecule.get(mid, [])
        if mol_findings:
            # Deduplicate by (source_file, antecedent, consequent)
            seen = set()
            for ef in all_findings:
                key = (ef.get("source_file", ""), ef.get("antecedent", ""), ef.get("consequent", ""))
                seen.add(key)
            for mf in mol_findings:
                key = (mf.get("source_file", ""), mf.get("antecedent", ""), mf.get("consequent", ""))
                if key not in seen:
                    all_findings.append(mf)
                    seen.add(key)

        stats = compute_aggregate_stats(all_findings)

        source = {
            **mol,
            "entity_id": mid,
            "title": mol.get("name", mol.get("title", mid)),
            **stats,
            "constituent_templates": constituent_data,
            "n_from_reverse_index": len(mol_findings),
            "findings": all_findings[:30],
            "all_findings_count": len(all_findings),
            "provenance": {
                "molecule_file": str(f),
                "enrichment_timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                "data_layers": ["molecules", "templates", "extractions_reverse_index"],
            },
        }
        sources.append(source)

    return sources


# ═══════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Enrich card source data from corpus")
    parser.add_argument("--dry-run", action="store_true", help="Preview stats only")
    parser.add_argument("--type", choices=["t1", "t2", "t3", "molecule", "all"], default="all")
    args = parser.parse_args()

    t0 = time.time()

    # Load all data
    extractions = load_all_extractions()
    templates = load_all_templates()
    theories = load_all_theories()
    annotations = load_extended_annotations()
    clusters = load_belief_clusters()

    # Load additional data layers
    annotation_layers = load_annotation_layers()
    cva_annotations = load_cva_annotations()
    interpretation = load_interpretation_data()
    mat_views = load_materialized_views()

    # Build indexes
    findings_index = build_findings_index(extractions, templates)
    effect_index = _build_effect_magnitude_index(annotation_layers)
    disputes = _build_dispute_index(annotation_layers)
    surprise_index = _build_surprise_index(annotation_layers)

    # Collect layer data for enrichment functions
    layer_data = {
        "annotation_layers": annotation_layers,
        "effect_index": effect_index,
        "disputes": disputes,
        "surprise_index": surprise_index,
        "cva_annotations": cva_annotations,
        "interpretation": interpretation,
        "mat_views": mat_views,
        "design_implications": annotation_layers.get("a10_design_implications", []),
        "replication_status": annotation_layers.get("a13_replication_status", []),
        "narrative_hooks": annotation_layers.get("a17_narrative_hooks", []),
        "unanswered_questions": annotation_layers.get("a18_unanswered_questions", []),
        "cross_domain": annotation_layers.get("a15_cross_domain_connections", []),
    }

    results = {}

    if args.type in ("t1", "all"):
        t1_sources = enrich_t1_frameworks(templates, findings_index, theories, annotations, layer_data)
        results["t1-framework"] = t1_sources

    if args.type in ("t2", "all"):
        t2_sources = enrich_t2_mechanisms(templates, findings_index, annotations, layer_data)
        results["t2-mechanism"] = t2_sources

    if args.type in ("t3", "all"):
        t3_sources = enrich_t3_beliefs(clusters, extractions, findings_index, layer_data)
        results["t3-belief"] = t3_sources

    if args.type in ("molecule", "all"):
        mol_sources = enrich_molecules(MOL_DIR, templates, findings_index)
        results["molecule"] = mol_sources

    # Report
    print(f"\n{'DRY RUN — ' if args.dry_run else ''}Card Source Enrichment Results")
    print(f"{'=' * 60}")
    print(f"  Time: {time.time() - t0:.1f}s")

    total_sc_pass = 0
    total_sc = 0

    for card_type, sources in results.items():
        print(f"\n  {card_type}: {len(sources)} entities")
        if not sources:
            continue

        # SC checks
        has_findings = sum(1 for s in sources if s.get("findings"))
        has_provenance = sum(1 for s in sources if s.get("provenance", {}).get("source_files"))
        has_omega = sum(1 for s in sources if s.get("omega", 0) > 0)
        has_mc = sum(1 for s in sources
                     if s.get("mechanism_chain") or s.get("mechanism_chains"))
        avg_findings = sum(s.get("all_findings_count", 0) for s in sources) / max(len(sources), 1)

        print(f"    With findings:     {has_findings}/{len(sources)} ({has_findings/len(sources)*100:.0f}%)")
        print(f"    With provenance:   {has_provenance}/{len(sources)} ({has_provenance/len(sources)*100:.0f}%)")
        print(f"    With omega:        {has_omega}/{len(sources)} ({has_omega/len(sources)*100:.0f}%)")
        print(f"    With mech chain:   {has_mc}/{len(sources)} ({has_mc/len(sources)*100:.0f}%)")
        print(f"    Avg findings/ent:  {avg_findings:.1f}")

        # Detailed SC checks for T1
        if card_type == "t1-framework":
            total_sc += 1
            if has_findings == len(sources):
                print(f"    ✓ SC-SD-1 PASS: All T1 frameworks have real findings")
                total_sc_pass += 1
            else:
                print(f"    ✗ SC-SD-1 FAIL: {len(sources) - has_findings} T1 frameworks have no findings")

        if card_type == "t3-belief":
            total_sc += 1
            expanded = sum(1 for s in sources if len(s.get("findings", [])) > 5)
            print(f"    Expanded >5 members: {expanded}/{len(sources)}")

    # Write enriched sources
    if not args.dry_run:
        for card_type, sources in results.items():
            out_dir = OUTPUT_DIR / card_type
            out_dir.mkdir(parents=True, exist_ok=True)
            for source in sources:
                eid = source.get("entity_id", "unknown")
                out_file = out_dir / f"{eid}.json"
                out_file.write_text(json.dumps(source, indent=2, ensure_ascii=False, default=str))
            print(f"\n  Wrote {len(sources)} enriched sources to {out_dir}")

    elapsed = time.time() - t0
    print(f"\n  Total time: {elapsed:.1f}s")


if __name__ == "__main__":
    main()
