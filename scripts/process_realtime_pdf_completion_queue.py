#!/usr/bin/env python3
"""
Process realtime PDF completion queue in batches.

Consumes rows from `data/production/realtime_pdf_completion_queue.csv` and:
1. Extracts PDF tables/claims for queued papers.
2. Emits PDF-confirmed rows to `data/production/realtime_pdf_confirmed_rows.csv`.
3. Integrates PDF-confirmed beliefs into Web of Belief (optional).
4. Updates incremental BN with higher-weight evidence (optional).
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import sqlite3
import sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
from src.services.db_locator import resolve_article_finder_db, resolve_web_db

from src.services.table_extractor import ExtractionMethod  # noqa: E402
from src.services.table_to_claims import PipelineTableIntegrator  # noqa: E402
from src.epistemic.extraction.paper_classifier import classify_paper  # noqa: E402
from lib.environment_resolver import resolve_environment, resolve_or_queue_environment  # noqa: E402
from lib.outcome_resolver import queue_unknown_outcome, resolve_or_queue, resolve_outcome  # noqa: E402

DEFAULT_AF_ROOT = PROJECT_ROOT.parent / "Article_Finder_v3_2_3"
DEFAULT_AF_DB = DEFAULT_AF_ROOT / "data" / "article_finder.db"
DEFAULT_WEB_DB = PROJECT_ROOT / "data" / "web_persistence.db"

CONTRACT_ENV_LOOKUP = PROJECT_ROOT / "contracts" / "vocab" / "environment_lookup.json"
CONTRACT_OUTCOME_LOOKUP = PROJECT_ROOT / "contracts" / "outcome_vocab" / "outcome_lookup.json"

_STOPWORDS = {
    "the",
    "and",
    "for",
    "with",
    "from",
    "that",
    "this",
    "into",
    "toward",
    "study",
    "effect",
    "effects",
    "impact",
    "influence",
    "association",
    "relationship",
    "analysis",
}

GENERIC_ENV_KEYWORDS = {
    "daylight": ["daylight", "sunlight", "natural light", "lighting", "illuminance", "light exposure"],
    "noise": ["noise", "acoustic", "sound", "speech noise", "irrelevant speech", "auditory distraction"],
    "air_quality": ["air quality", "iaq", "co2", "ventilation", "voc", "particulate"],
    "thermal": ["thermal", "temperature", "humidity", "heat", "cooling", "comfort"],
    "biophilia": ["biophilic", "biophilia", "plants", "vegetation", "greenery", "nature view", "natural elements"],
    "spatial_layout": ["layout", "open plan", "density", "ceiling", "enclosure", "wayfinding", "geometry"],
}

GENERIC_OUTCOME_KEYWORDS = {
    "stress": ["stress", "cortisol", "anxiety", "tension", "arousal"],
    "attention": ["attention", "focus", "concentration", "vigilance", "distraction"],
    "cognition": ["cognitive", "memory", "executive function", "mental fatigue", "cognition"],
    "productivity": ["productivity", "performance", "task performance", "efficiency", "output"],
    "mood": ["mood", "affect", "emotion", "wellbeing", "well-being", "emotion regulation"],
    "sleep": ["sleep", "circadian", "alertness", "fatigue", "sleepiness"],
}

CONTRADICT_MARKERS = [
    "failed to replicate",
    "fails to replicate",
    "no effect",
    "no significant",
    "not significant",
    "null effect",
    "contradict",
    "challenge",
    "inconsistent",
    "did not support",
    "not supported",
    "attenuated",
]

EXPLAIN_MARKERS = [
    "mechanism",
    "mediate",
    "mediated",
    "pathway",
    "explains",
    "refine",
    "elaborate",
    "nuance",
    "boundary condition",
    "moderator",
    "heterogeneity",
]

SUPPORT_MARKERS = [
    "support",
    "verify",
    "replicate",
    "consistent with",
    "convergent",
    "confirm",
    "validated",
    "robust",
]

NEGATIVE_EFFECT_MARKERS = [
    "decrease",
    "decreased",
    "reduce",
    "reduced",
    "lower",
    "worse",
    "impaired",
    "impairment",
    "decline",
]

SECTION_HEADER_PATTERNS: Dict[str, List[str]] = {
    "introduction": [
        r"^\s*(?:\d+(?:\.\d+)*[.)]?\s*)?introduction\b[:.]?\s*$",
        r"^\s*background\s*$",
    ],
    "related_work": [
        r"^\s*(?:\d+(?:\.\d+)*[.)]?\s*)?related\s+work\b[:.]?\s*$",
        r"^\s*(?:\d+(?:\.\d+)*[.)]?\s*)?literature\s+review\b[:.]?\s*$",
    ],
    "methods": [
        r"^\s*(?:\d+(?:\.\d+)*[.)]?\s*)?(methods?|materials\s+and\s+methods?)\b[:.]?\s*$",
        r"^\s*(?:\d+(?:\.\d+)*[.)]?\s*)?procedure\b[:.]?\s*$",
    ],
    "results": [
        r"^\s*(?:\d+(?:\.\d+)*[.)]?\s*)?results?\b[:.]?\s*$",
        r"^\s*(?:\d+(?:\.\d+)*[.)]?\s*)?findings\b[:.]?\s*$",
    ],
    "discussion": [
        r"^\s*(?:\d+(?:\.\d+)*[.)]?\s*)?discussion\b[:.]?\s*$",
    ],
    "conclusion": [
        r"^\s*(?:\d+(?:\.\d+)*[.)]?\s*)?conclusions?\b[:.]?\s*$",
    ],
}

THEORY_TERMS: Dict[str, List[str]] = {
    "ART": ["attention restoration theory", "art", "directed attention fatigue", "soft fascination"],
    "SRT": ["stress recovery theory", "srt", "psychophysiological stress recovery"],
    "biophilia": ["biophilia", "biophilic", "innate attraction to nature"],
    "prospect_refuge": ["prospect-refuge", "prospect refuge"],
    "predictive_processing": ["predictive processing", "predictive coding"],
    "embodied_cognition": ["embodied cognition", "4e cognition", "enactivism"],
}

ARTICLE_RELATION_RULES: List[Tuple[str, List[str], str, float]] = [
    ("fails_to_replicate", ["failed to replicate", "fails to replicate", "non-replication"], "contradicts", 0.72),
    ("challenges", ["challenge", "contradict", "inconsistent with", "did not support"], "contradicts", 0.66),
    ("refines", ["refine", "nuance", "boundary condition", "moderate", "heterogeneity"], "explains", 0.58),
    ("elaborates", ["elaborate", "extends", "expand", "mechanism"], "explains", 0.56),
    ("verifies", ["verify", "confirm", "replicate", "consistent with"], "supports", 0.60),
    ("tests", ["test", "evaluate", "examine"], "explains", 0.48),
    ("cites_background", ["according to", "as reported by", "prior work", "previous studies"], "explains", 0.40),
]

CANONICAL_FAMILIES = {
    "empirical_v2",
    "meta_analysis",
    "systematic_review",
    "narrative_review",
    "theoretical",
    "conceptual_framework",
    "mixed_methods",
    "observational_field",
    "case_study",
    "interview_study",
    "ethnographic",
    "grounded_theory",
    "phenomenological",
    "thought_piece",
    "panel_additions",
    "unknown",
}

FAMILY_DEFAULT_NODE_TYPE = {
    "empirical_v2": "EMPIRICAL_FINDING",
    "meta_analysis": "SYNTHESIS_CONCLUSION",
    "systematic_review": "SYNTHESIS_CONCLUSION",
    "narrative_review": "EXPERT_SYNTHESIS",
    "theoretical": "THEORETICAL_PROPOSITION",
    "conceptual_framework": "CONCEPTUAL_DEFINITION",
    "mixed_methods": "EMPIRICAL_FINDING",
    "observational_field": "EMPIRICAL_FINDING",
    "case_study": "EMPIRICAL_FINDING",
    "interview_study": "QUALITATIVE_FINDING",
    "ethnographic": "QUALITATIVE_FINDING",
    "grounded_theory": "QUALITATIVE_FINDING",
    "phenomenological": "QUALITATIVE_FINDING",
    "thought_piece": "EXPERT_SYNTHESIS",
    "panel_additions": "BRIDGE_WARRANT",
    "unknown": "EMPIRICAL_FINDING",
}

REVIEW_FAMILIES = {"meta_analysis", "systematic_review", "narrative_review", "thought_piece"}


@dataclass
class PaperProcessResult:
    row_index: int
    status: str
    n_tables: int = 0
    n_claims: int = 0
    resolved_pdf_path: str = ""
    error: str = ""
    confirmed_rows: List[Dict[str, Any]] = None
    belief_specs: List[Dict[str, Any]] = None
    bridge_claims: List[Dict[str, Any]] = None
    extraction_audit: Dict[str, Any] = None

    def __post_init__(self) -> None:
        if self.confirmed_rows is None:
            self.confirmed_rows = []
        if self.belief_specs is None:
            self.belief_specs = []
        if self.bridge_claims is None:
            self.bridge_claims = []
        if self.extraction_audit is None:
            self.extraction_audit = {}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Process realtime PDF completion queue.")
    parser.add_argument("--af-db", default=None, help="Path to article_finder.db (auto-resolved if omitted)")
    parser.add_argument("--web-db", default=None, help="Path to web DB (auto-resolved if omitted)")
    parser.add_argument(
        "--web-db-prefer",
        choices=("integrated", "latest"),
        default="integrated",
        help="Auto-resolution policy when --web-db is omitted",
    )
    parser.add_argument(
        "--queue-csv",
        default="data/production/realtime_pdf_completion_queue.csv",
        help="Queue CSV path",
    )
    parser.add_argument(
        "--confirmed-csv",
        default="data/production/realtime_pdf_confirmed_rows.csv",
        help="Output CSV for PDF-confirmed rows",
    )
    parser.add_argument(
        "--no-claims-csv",
        default="data/production/realtime_pdf_no_claims_review.csv",
        help="Output CSV for no-claims PDF review list",
    )
    parser.add_argument(
        "--audit-jsonl",
        default="data/production/realtime_extraction_audit.jsonl",
        help="Output JSONL for per-paper extraction audit",
    )
    parser.add_argument(
        "--manual-review-csv",
        default="data/review/table_quality_manual_queue.csv",
        help="Output CSV for manual extraction quality review queue",
    )
    parser.add_argument(
        "--quality-thresholds",
        default="config/table_extraction_quality_thresholds.json",
        help="Quality thresholds config for review triage",
    )
    parser.add_argument(
        "--article-type-review-csv",
        default="data/review/article_type_manual_queue.csv",
        help="Output CSV for article-type verification review queue",
    )
    parser.add_argument(
        "--article-type-min-confidence",
        type=float,
        default=0.60,
        help="Minimum classification confidence before forcing type review",
    )
    parser.add_argument(
        "--article-type-min-margin",
        type=float,
        default=0.35,
        help="Minimum winner-vs-runner-up margin before forcing type review",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=30,
        help="Max queued papers to process this run",
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=4,
        help="Parallel workers for PDF extraction",
    )
    parser.add_argument(
        "--prioritize-preprocessed",
        action="store_true",
        help="Prioritize rows with preprocess_status=ready before unknown/quarantine rows",
    )
    parser.add_argument(
        "--skip-preprocess-quarantine",
        action="store_true",
        help="Skip queued rows marked preprocess_status=quarantine or error",
    )
    parser.add_argument(
        "--integrate-web",
        action="store_true",
        help="Integrate PDF-confirmed beliefs into Web of Belief",
    )
    parser.add_argument(
        "--update-bn",
        action="store_true",
        help="Update incremental BN from PDF-confirmed beliefs",
    )
    parser.add_argument(
        "--bn-state-path",
        default="data/production/realtime_incremental_bn.json",
        help="Path for incremental BN state JSON",
    )
    parser.add_argument(
        "--bn-pdf-weight",
        type=float,
        default=0.90,
        help="Evidence weight for PDF-confirmed BN updates",
    )
    parser.add_argument("--dry-run", action="store_true", help="Inspect queue without writing")
    return parser.parse_args()


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip().lower())


def classify_template_family(title: str, abstract: str, venue: str = "") -> str:
    return classify_template_family_with_diagnostics(title, abstract, venue)["family"]


def classify_template_family_with_diagnostics(title: str, abstract: str, venue: str = "") -> Dict[str, Any]:
    result = classify_paper(title=title, abstract=abstract, venue=venue)
    confidence = round(float(result.confidence), 4)
    margin = round(float(result.margin), 4)
    needs_review = bool(result.needs_manual_review)
    family = result.template_family.value
    diagnostics = list(result.diagnostics[:8])
    if needs_review and confidence < 0.60:
        family = "unknown"
        diagnostics.append("downgraded_to_unknown_low_confidence")
    return {
        "family": family,
        "predicted_family": result.template_family.value,
        "confidence": confidence,
        "runner_up": result.runner_up_family.value if result.runner_up_family else "",
        "margin": margin,
        "needs_review": needs_review,
        "signals": "|".join(result.signals_matched[:8]),
        "diagnostics": "|".join(diagnostics),
        "classifier_version": "paper_classifier_v2",
    }


def infer_node_type(article_type_family: str, claim_type: str, statement: str) -> str:
    family = article_type_family if article_type_family in CANONICAL_FAMILIES else "unknown"
    text = normalize(statement)
    ctype = normalize(claim_type)

    if "gap" in text or "unknown" in text or "future research" in text:
        return "KNOWLEDGE_GAP"
    if any(k in text for k in ["must distinguish", "must not conflate", "distinguish from"]):
        return "CONCEPTUAL_CONSTRAINT"
    if any(k in text for k in ["defines", "defined as", "we use the term", "conceptualization"]):
        return "CONCEPTUAL_DEFINITION"
    if any(k in text for k in ["hypothesis", "predicts", "prediction"]):
        return "DERIVED_HYPOTHESIS"
    if any(k in text for k in ["mechanism", "pathway", "mediat"]):
        if family in {"theoretical", "narrative_review", "mixed_methods", "case_study"}:
            return "BRIDGE_WARRANT"
    if family == "systematic_review" and any(k in text for k in ["bias", "quality concern", "methodological"]):
        return "METHODOLOGICAL_CRITIQUE"
    if family == "thought_piece" and any(k in text for k in ["invalid", "artifact", "flaw", "bias", "method"]):
        return "METHODOLOGICAL_CRITIQUE"
    if family == "conceptual_framework" and any(k in text for k in ["taxonomy", "framework", "organizes", "typology"]):
        return "FRAMEWORK_STRUCTURE"
    if family == "theoretical" and ctype == "theory_link":
        return "THEORETICAL_PROPOSITION"

    if family == "meta_analysis":
        return "SYNTHESIS_CONCLUSION"
    if family == "systematic_review":
        return "SYNTHESIS_CONCLUSION"
    if family == "narrative_review":
        return "EXPERT_SYNTHESIS"
    if family == "theoretical":
        return "THEORETICAL_PROPOSITION"
    if family == "conceptual_framework":
        return "CONCEPTUAL_DEFINITION"
    if family == "mixed_methods":
        if any(k in text for k in ["theme", "participant", "interview"]):
            return "QUALITATIVE_FINDING"
        return "EMPIRICAL_FINDING"
    if family in {"interview_study", "ethnographic", "grounded_theory", "phenomenological"}:
        return "QUALITATIVE_FINDING"
    if family == "thought_piece":
        return "EXPERT_SYNTHESIS"
    return FAMILY_DEFAULT_NODE_TYPE.get(family, "EMPIRICAL_FINDING")


def infer_causal_level(article_type_family: str, statement: str) -> str:
    family = article_type_family
    text = normalize(statement)
    if family in {"theoretical"}:
        return "counterfactual"
    if family in {"observational_field", "interview_study", "ethnographic", "phenomenological", "grounded_theory"}:
        return "association"
    if any(k in text for k in ["randomized", "intervention", "manipulat", "do("]):
        return "intervention"
    return "association"


def infer_argument_scheme(article_type_family: str, claim_type: str, statement: str) -> str:
    family = article_type_family
    text = normalize(statement)
    if claim_type in {"theory_link", "inter_article_relation"}:
        if any(k in text for k in ["predict", "hypothesis"]):
            return "causal_argument"
        return "argument_from_expert_opinion"
    if family in {"theoretical", "conceptual_framework"}:
        return "practical_reasoning"
    if family in {"interview_study", "ethnographic", "phenomenological", "grounded_theory"}:
        return "argument_from_position_to_know"
    if family in {"systematic_review", "meta_analysis", "narrative_review"}:
        return "argument_from_expert_opinion"
    return "causal_argument"


def infer_edge_type_for_theory(sentence: str, relation_name: str) -> str:
    t = normalize(sentence)
    if relation_name in {"contradicts"}:
        return "DISCONFIRMS_PREDICTION"
    if relation_name in {"supports"}:
        return "CONFIRMS_PREDICTION"
    if relation_name in {"extends"}:
        return "SUBSUMES_THEORY"
    if relation_name in {"tests"}:
        return "THEORETICALLY_PREDICTS"
    if any(k in t for k in ["mechanism", "pathway", "mediate"]):
        return "PROPOSES_MECHANISM"
    if any(k in t for k in ["tension", "incompatible"]):
        return "THEORY_TENSION"
    return "COHERENCE_SUPPORT"


def infer_edge_type_for_article(sentence: str, relation_name: str) -> str:
    t = normalize(sentence)
    if any(k in t for k in ["includes in analysis", "pooled", "n studies"]):
        return "INCLUDES_IN_SYNTHESIS"
    if relation_name in {"fails_to_replicate", "challenges"}:
        return "COHERENCE_TENSION"
    if relation_name in {"verifies"}:
        return "CONFIRMS_PREDICTION"
    if relation_name in {"refines", "elaborates"}:
        return "COHERENCE_SUPPORT"
    if any(k in t for k in ["defines", "we use the term"]):
        return "DEFINES_CONSTRUCT"
    if any(k in t for k in ["must be distinguished", "must distinguish"]):
        return "MUST_DISTINGUISH"
    if relation_name in {"cites_background", "mentions", "cites"}:
        return "ATTRIBUTES_FINDING"
    if relation_name in {"tests"}:
        return "INTERPRETS_AS"
    return "COHERENCE_SUPPORT"


def infer_edge_evidence_basis(edge_type: str) -> str:
    if edge_type in {"ATTRIBUTES_FINDING", "INTERPRETS_AS"}:
        return "reviewer_interpretation"
    if edge_type in {"COHERENCE_SUPPORT", "COHERENCE_TENSION", "THEORY_TENSION"}:
        return "implicit_connection"
    return "explicit_statement"


def safe_var_name(name: str) -> str:
    return re.sub(r"[^a-z0-9_]+", "_", normalize(name))


def safe_node_component(name: str) -> str:
    s = normalize(name)
    s = re.sub(r"[^a-z0-9_.]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("._")
    return s or "unknown"


def load_lookup_terms(path: Path) -> List[str]:
    if not path.exists():
        return []
    try:
        import json

        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []
    lookup = data.get("lookup", {})
    terms = [normalize(k) for k in lookup.keys() if isinstance(k, str)]
    terms = [t for t in terms if len(t) >= 3]
    return sorted(set(terms), key=len, reverse=True)


ENV_LOOKUP_TERMS = load_lookup_terms(CONTRACT_ENV_LOOKUP)
OUTCOME_LOOKUP_TERMS = load_lookup_terms(CONTRACT_OUTCOME_LOOKUP)


def _maybe_unwrap_quotes(raw: str) -> str:
    s = (raw or "").strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in {"'", '"'}:
        return s[1:-1].strip()
    return s


def resolve_pdf_path(raw_path: str, queue_csv_path: Path) -> Path:
    queue_dir = queue_csv_path.resolve().parent
    candidates: List[Path] = []
    variants = []
    raw = (raw_path or "").strip()
    if raw:
        variants.append(raw)
        unwrapped = _maybe_unwrap_quotes(raw)
        if unwrapped and unwrapped != raw:
            variants.append(unwrapped)

    for variant in variants:
        p = Path(variant)
        if p.is_absolute():
            candidates.append(p)
        else:
            candidates.append((queue_dir / p).resolve())
            candidates.append((PROJECT_ROOT / p).resolve())
            candidates.append((DEFAULT_AF_ROOT / p).resolve())

    for candidate in candidates:
        if candidate.exists():
            return candidate

    return candidates[0] if candidates else Path(raw_path or "")


def contains_term(text: str, term: str) -> bool:
    if not term:
        return False
    if " " in term or "-" in term or "." in term:
        return term in text
    return bool(re.search(rf"\b{re.escape(term)}\b", text))


def extract_lookup_matches(text: str, lookup_terms: Sequence[str], max_terms: int = 8) -> List[str]:
    matches: List[str] = []
    for term in lookup_terms:
        if contains_term(text, term):
            if not any(term in m or m in term for m in matches):
                matches.append(term)
            if len(matches) >= max_terms:
                break
    return matches


def extract_of_on_pair(text: str) -> Tuple[str, str]:
    patterns = [
        r"(?:effect|effects|impact|influence|association|relationship)\s+of\s+(.{3,80}?)\s+on\s+(.{3,80}?)(?:[.;,:]|$)",
        r"between\s+(.{3,80}?)\s+and\s+(.{3,80}?)(?:[.;,:]|$)",
    ]
    for pattern in patterns:
        m = re.search(pattern, text)
        if m:
            left = normalize(m.group(1))
            right = normalize(m.group(2))
            if left and right:
                return left, right
    return "", ""


def fallback_term(text: str, default: str) -> str:
    words = [w for w in re.findall(r"[a-zA-Z][a-zA-Z0-9\-]{2,}", text) if normalize(w) not in _STOPWORDS]
    if not words:
        return default
    return " ".join(normalize(w) for w in words[:3])


def detect_generic_class(text: str, mapping: Dict[str, List[str]]) -> str:
    norm = normalize(text)
    best = ""
    best_score = 0
    for canonical, keywords in mapping.items():
        score = sum(1 for kw in keywords if normalize(kw) in norm)
        if score > best_score:
            best = canonical
            best_score = score
    return best if best_score > 0 else ""


def candidate_variants(raw_term: str) -> List[str]:
    base = normalize(raw_term)
    variants = [base]
    tokens = [t for t in re.findall(r"[a-z0-9]+", base) if len(t) >= 3]
    if len(tokens) > 1:
        for n in range(len(tokens), 0, -1):
            for i in range(0, len(tokens) - n + 1):
                phrase = " ".join(tokens[i : i + n])
                if phrase not in variants:
                    variants.append(phrase)
    return variants[:12]


def semantic_lookup_fallback(
    raw_term: str,
    context_text: str,
    lookup_map: Dict[str, str],
    min_score: float = 0.70,
) -> Dict[str, Any]:
    """Constrained semantic fallback over known lookup terms."""
    raw = normalize(raw_term)
    if not raw:
        return {"canonical_id": "", "confidence": 0.0, "matched_term": ""}

    raw_tokens = set(re.findall(r"[a-z0-9]{3,}", raw))
    context = normalize(context_text)

    best_term = ""
    best_canonical = ""
    best_score = 0.0

    for term, canonical in lookup_map.items():
        if not isinstance(term, str) or not isinstance(canonical, str):
            continue
        term_n = normalize(term)
        term_tokens = set(re.findall(r"[a-z0-9]{3,}", term_n))
        if not term_tokens:
            continue

        ratio = SequenceMatcher(None, raw, term_n).ratio()
        overlap = len(raw_tokens & term_tokens) / max(1, len(term_tokens))
        score = (0.65 * ratio) + (0.35 * overlap)
        if term_n and term_n in context:
            score += 0.05

        if score > best_score:
            best_score = score
            best_term = term_n
            best_canonical = canonical

    if best_canonical and best_score >= min_score:
        conf = max(0.40, min(0.74, round(best_score, 4)))
        return {"canonical_id": best_canonical, "confidence": conf, "matched_term": best_term}
    return {"canonical_id": "", "confidence": 0.0, "matched_term": ""}


def lookup_candidate_score(raw_term: str, lookup_term: str, context_text: str = "") -> float:
    raw = normalize(raw_term)
    term = normalize(lookup_term)
    if not raw or not term:
        return 0.0
    raw_tokens = set(re.findall(r"[a-z0-9]{3,}", raw))
    term_tokens = set(re.findall(r"[a-z0-9]{3,}", term))
    if not term_tokens:
        return 0.0
    ratio = SequenceMatcher(None, raw, term).ratio()
    overlap = len(raw_tokens & term_tokens) / max(1, len(term_tokens))
    score = (0.65 * ratio) + (0.35 * overlap)
    if term and term in normalize(context_text):
        score += 0.05
    return min(score, 1.0)


def rank_lookup_candidates(
    raw_term: str,
    context_text: str,
    lookup_map: Dict[str, str],
    limit: int = 20,
) -> List[Tuple[str, str, float]]:
    ranked: List[Tuple[str, str, float]] = []
    for term, canonical in lookup_map.items():
        if not isinstance(term, str) or not isinstance(canonical, str):
            continue
        score = lookup_candidate_score(raw_term, term, context_text=context_text)
        if score <= 0.0:
            continue
        ranked.append((normalize(term), canonical, score))
    ranked.sort(key=lambda item: item[2], reverse=True)
    return ranked[: max(1, limit)]


def llm_lookup_fallback(
    raw_term: str,
    context_text: str,
    lookup_map: Dict[str, str],
    min_shortlist_score: float = 0.45,
) -> Dict[str, Any]:
    """Optional LLM fallback over constrained lookup shortlist."""
    if os.getenv("AE_ENABLE_LLM_FALLBACK", "0").lower() not in {"1", "true", "yes"}:
        return {"canonical_id": "", "confidence": 0.0, "matched_term": ""}
    if not os.getenv("OPENAI_API_KEY"):
        return {"canonical_id": "", "confidence": 0.0, "matched_term": ""}

    ranked = rank_lookup_candidates(raw_term, context_text, lookup_map, limit=20)
    if not ranked or ranked[0][2] < min_shortlist_score:
        return {"canonical_id": "", "confidence": 0.0, "matched_term": ""}

    candidates = [term for term, _canonical, _score in ranked]
    term_to_canonical = {term: canonical for term, canonical, _score in ranked}
    model = os.getenv("AE_LLM_FALLBACK_MODEL", "gpt-4o-mini")
    prompt = (
        "Choose one candidate term for ontology mapping.\n"
        "Return ONLY the exact candidate term string from the list, or NONE.\n\n"
        f"Raw phrase: {raw_term}\n"
        f"Context: {context_text[:600]}\n"
        f"Candidates: {json.dumps(candidates)}"
    )
    try:
        from openai import OpenAI  # type: ignore

        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a precise ontology mapper. Do not explain."},
                {"role": "user", "content": prompt},
            ],
            temperature=0,
            max_tokens=24,
        )
        chosen = (response.choices[0].message.content or "").strip().strip('"').strip("'")
        if chosen in term_to_canonical:
            return {
                "canonical_id": term_to_canonical[chosen],
                "confidence": 0.60,
                "matched_term": chosen,
            }
    except Exception:
        return {"canonical_id": "", "confidence": 0.0, "matched_term": ""}

    return {"canonical_id": "", "confidence": 0.0, "matched_term": ""}


def to_node_id(kind: str, canonical_id: str, raw_term: str) -> str:
    canonical_n = normalize(canonical_id)
    if canonical_n and not canonical_n.startswith("unresolved:"):
        component = safe_node_component(canonical_n)
        if component.startswith(f"{kind}."):
            return component
        return f"{kind}.{component}"
    return f"{kind}.unresolved.{safe_node_component(raw_term)[:80]}"


def resolve_env_outcome_from_claim(content: str, metadata: Dict[str, Any], paper_id: str) -> Dict[str, Any]:
    env_hint = normalize(str(metadata.get("intervention", "") or ""))
    outcome_hint = normalize(str(metadata.get("outcome", "") or ""))
    text = normalize(f"{content} {env_hint} {outcome_hint}")

    env_candidates = extract_lookup_matches(text, ENV_LOOKUP_TERMS)
    out_candidates = extract_lookup_matches(text, OUTCOME_LOOKUP_TERMS)

    env_raw = env_candidates[0] if env_candidates else ""
    out_raw = out_candidates[0] if out_candidates else ""

    if not env_raw or not out_raw:
        left, right = extract_of_on_pair(text)
        if left and not env_raw:
            env_raw = left
        if right and not out_raw:
            out_raw = right

    if not env_raw:
        env_raw = fallback_term(text, "unspecified_environment")
    if not out_raw:
        out_raw = fallback_term(text, "unspecified_outcome")

    env_resolved = None
    resolved_env_raw = env_raw
    if callable(resolve_environment):
        for variant in candidate_variants(env_raw):
            env_resolved = resolve_environment(variant, fuzzy_threshold=0.74)
            if env_resolved:
                resolved_env_raw = variant
                break

    if not env_resolved and callable(resolve_or_queue_environment):
        try:
            env_resolved, _queued = resolve_or_queue_environment(env_raw)
        except Exception:
            env_resolved = None

    out_resolved = None
    resolved_out_raw = out_raw
    if callable(resolve_outcome):
        for variant in candidate_variants(out_raw):
            out_resolved = resolve_outcome(variant, fuzzy_threshold=0.8)
            if out_resolved:
                resolved_out_raw = variant
                break

    if not out_resolved and callable(resolve_or_queue):
        try:
            queued = resolve_or_queue(out_raw, paper_id=paper_id, context=text[:500])
            if queued and not str(queued.get("canonical_id", "")).startswith("UNRESOLVED:"):
                out_resolved = queued
        except Exception:
            out_resolved = None

    if not env_resolved:
        llm_env = llm_lookup_fallback(env_raw, text, ENV_LOOKUP_MAP)
        if llm_env["canonical_id"]:
            env_resolved = {
                "tag_id": llm_env["canonical_id"],
                "canonical_name": llm_env["canonical_id"],
                "confidence": llm_env["confidence"],
                "match_type": "llm_lookup_fallback",
            }

    if not env_resolved:
        semantic_env = semantic_lookup_fallback(env_raw, text, ENV_LOOKUP_MAP)
        if semantic_env["canonical_id"]:
            env_resolved = {
                "tag_id": semantic_env["canonical_id"],
                "canonical_name": semantic_env["canonical_id"],
                "confidence": semantic_env["confidence"],
                "match_type": "semantic_lookup_fallback",
            }

    if not out_resolved:
        llm_out = llm_lookup_fallback(out_raw, text, OUTCOME_LOOKUP_MAP)
        if llm_out["canonical_id"]:
            out_resolved = {
                "canonical_id": llm_out["canonical_id"],
                "name": llm_out["canonical_id"],
                "confidence": llm_out["confidence"],
                "match_type": "llm_lookup_fallback",
            }

    if not out_resolved:
        semantic_out = semantic_lookup_fallback(out_raw, text, OUTCOME_LOOKUP_MAP)
        if semantic_out["canonical_id"]:
            out_resolved = {
                "canonical_id": semantic_out["canonical_id"],
                "name": semantic_out["canonical_id"],
                "confidence": semantic_out["confidence"],
                "match_type": "semantic_lookup_fallback",
            }

    env_canonical = str(env_resolved.get("tag_id", "")) if env_resolved else f"UNRESOLVED:environment:{safe_var_name(env_raw)[:48]}"
    out_canonical = str(out_resolved.get("canonical_id", "")) if out_resolved else f"UNRESOLVED:outcome:{safe_var_name(out_raw)[:48]}"

    if env_canonical.startswith("UNRESOLVED:"):
        generic_env = detect_generic_class(text, GENERIC_ENV_KEYWORDS)
        if generic_env:
            env_canonical = f"env.generic.{generic_env}"

    if out_canonical.startswith("UNRESOLVED:"):
        generic_out = detect_generic_class(text, GENERIC_OUTCOME_KEYWORDS)
        if generic_out:
            out_canonical = f"out.generic.{generic_out}"
        elif callable(queue_unknown_outcome):
            try:
                queue_unknown_outcome(out_raw, paper_id=paper_id, context=text[:500])
            except Exception:
                pass

    return {
        "paper_id": paper_id,
        "environment_raw_term": resolved_env_raw if env_resolved else env_raw,
        "outcome_raw_term": resolved_out_raw if out_resolved else out_raw,
        "environment_candidates": ([env_raw] + env_candidates)[:8] if env_raw not in env_candidates else env_candidates[:8],
        "outcome_candidates": ([out_raw] + out_candidates)[:8] if out_raw not in out_candidates else out_candidates[:8],
        "environment_canonical_id": env_canonical,
        "outcome_canonical_id": out_canonical,
        "environment_resolution_confidence": float(env_resolved.get("confidence", 0.0)) if env_resolved else (0.35 if "env.generic." in env_canonical else 0.0),
        "outcome_resolution_confidence": float(out_resolved.get("confidence", 0.0)) if out_resolved else (0.35 if "out.generic." in out_canonical else 0.0),
        "environment_resolution_match_type": str(env_resolved.get("match_type", "resolver")) if env_resolved else ("generic_keyword" if "env.generic." in env_canonical else "unresolved"),
        "outcome_resolution_match_type": str(out_resolved.get("match_type", "resolver")) if out_resolved else ("generic_keyword" if "out.generic." in out_canonical else "unresolved"),
        "environment_node_id": to_node_id("env", env_canonical, resolved_env_raw if env_resolved else env_raw),
        "outcome_node_id": to_node_id("out", out_canonical, resolved_out_raw if out_resolved else out_raw),
    }


def _to_float(value: Any) -> Optional[float]:
    try:
        if value is None:
            return None
        return float(value)
    except Exception:
        return None


def claim_effect_direction(content: str, metadata: Optional[Dict[str, Any]] = None, claim_type: str = "") -> str:
    text = normalize(content)
    md = metadata or {}

    significant = md.get("significant")
    if isinstance(significant, bool) and not significant:
        return "null"

    p_value = _to_float(md.get("p_value"))
    if p_value is not None and p_value >= 0.05:
        return "null"

    if any(marker in text for marker in CONTRADICT_MARKERS):
        return "null"

    effect_size = _to_float(md.get("effect_size"))
    if effect_size is not None and effect_size < 0:
        return "negative"

    if any(marker in text for marker in NEGATIVE_EFFECT_MARKERS):
        return "negative"

    if claim_type.lower() == "effect" and p_value is not None and p_value < 0.05:
        return "positive"

    return "positive"


def classify_argument_relation(
    text: str,
    *,
    effect_direction: str = "unknown",
    claim_type: str = "",
    metadata: Optional[Dict[str, Any]] = None,
) -> Tuple[str, float, str]:
    """
    Map claim signals to a Web constraint type with explicit provenance.
    """
    t = normalize(text or "")
    ct = (claim_type or "").strip().lower()
    md = metadata or {}

    if effect_direction in {"negative", "null"}:
        reason = "argument:null_or_negative_effect"
        if effect_direction == "negative":
            reason = "argument:negative_direction_effect"
        return ("contradicts", 0.62, reason)

    if any(m in t for m in CONTRADICT_MARKERS):
        return ("contradicts", 0.65, "argument:challenge_or_failure")

    if any(m in t for m in EXPLAIN_MARKERS):
        return ("explains", 0.58, "argument:elaborate_or_refine")

    if ct in {"methodology", "sample"}:
        return ("explains", 0.45, "argument:method_or_sample_context")

    p_value = _to_float(md.get("p_value"))
    if ct == "effect" and p_value is not None and p_value < 0.05:
        return ("supports", 0.60, "argument:effect_with_significance")

    if any(m in t for m in SUPPORT_MARKERS):
        return ("supports", 0.52, "argument:verify_or_test")

    # Avoid collapsing all unknowns into SUPPORTS.
    return ("explains", 0.40, "argument:default_contextual")


def short_quote(text: str, limit: int = 320) -> str:
    cleaned = re.sub(r"\s+", " ", (text or "").strip())
    return cleaned[:limit]


def quote_hash(text: str) -> str:
    return hashlib.sha1(normalize(text).encode("utf-8")).hexdigest()[:16]


def detect_section_header(line: str) -> Optional[str]:
    stripped = (line or "").strip()
    if not stripped:
        return None
    for section_name, patterns in SECTION_HEADER_PATTERNS.items():
        for pattern in patterns:
            if re.match(pattern, stripped, flags=re.IGNORECASE):
                return section_name
    return None


def split_sentences(text: str) -> List[str]:
    if not text:
        return []
    chunks = re.split(r"(?<=[\.\!\?])\s+(?=[A-Z0-9])", text)
    out: List[str] = []
    for chunk in chunks:
        c = re.sub(r"\s+", " ", chunk).strip()
        if len(c) >= 40:
            out.append(c)
    return out


def extract_sectioned_sentences(pdf_path: Path) -> List[Dict[str, Any]]:
    try:
        import pdfplumber
    except Exception:
        return []

    sentences: List[Dict[str, Any]] = []
    current_section = "other"
    with pdfplumber.open(str(pdf_path)) as pdf:
        for page_idx, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
            for line in lines:
                maybe_header = detect_section_header(line)
                if maybe_header:
                    current_section = maybe_header
                    continue
                for sentence in split_sentences(line):
                    sentences.append(
                        {
                            "page": page_idx,
                            "section": current_section,
                            "sentence": sentence,
                        }
                    )
    return sentences


def extract_citations(sentence: str) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    seen = set()

    for doi_match in re.finditer(r"(10\.\d{4,9}/[^\s\]\)\.;,]+)", sentence, flags=re.IGNORECASE):
        doi = doi_match.group(1).strip()
        key = f"doi:{doi.lower()}"
        if key in seen:
            continue
        seen.add(key)
        items.append(
            {
                "citation_text": doi,
                "doi": doi,
                "lead_author": "",
                "year": "",
            }
        )

    auth_year_pattern = re.compile(
        r"\b([A-Z][A-Za-z'`\-]+)(?:\s+et\s+al\.)?\s*,?\s*(?:\(|\[)?((?:19|20)\d{2})(?:\)|\])?",
        flags=re.IGNORECASE,
    )
    for match in auth_year_pattern.finditer(sentence):
        lead_author = match.group(1).strip()
        year = match.group(2).strip()
        citation_text = match.group(0).strip()
        key = f"ay:{lead_author.lower()}:{year}"
        if key in seen:
            continue
        seen.add(key)
        items.append(
            {
                "citation_text": citation_text,
                "doi": "",
                "lead_author": lead_author,
                "year": year,
            }
        )
    return items


def classify_article_relation(sentence: str) -> Tuple[str, str, float]:
    s = normalize(sentence)
    for relation_name, markers, web_relation, strength in ARTICLE_RELATION_RULES:
        if any(marker in s for marker in markers):
            return relation_name, web_relation, strength
    return "mentions", "explains", 0.35


def classify_theory_relation(sentence: str) -> Tuple[str, str, float]:
    s = normalize(sentence)
    if any(k in s for k in ["failed to replicate", "contradict", "inconsistent"]):
        return "contradicts", "contradicts", 0.65
    if any(k in s for k in ["test", "evaluate", "examine"]):
        return "tests", "explains", 0.52
    if any(k in s for k in ["extend", "refine", "elaborate"]):
        return "extends", "explains", 0.56
    if any(k in s for k in ["support", "confirm", "consistent with"]):
        return "supports", "supports", 0.60
    return "cites", "explains", 0.40


def resolve_citation_to_paper(
    conn: sqlite3.Connection,
    citation: Dict[str, Any],
) -> Tuple[str, float, str]:
    doi = normalize(str(citation.get("doi", "")))
    if doi:
        row = conn.execute(
            "SELECT paper_id FROM papers WHERE lower(doi) = ? LIMIT 1",
            (doi,),
        ).fetchone()
        if row and row[0]:
            return str(row[0]), 1.0, "doi_exact"

    lead_author = normalize(str(citation.get("lead_author", "")))
    year = str(citation.get("year", "")).strip()
    if lead_author and year.isdigit():
        rows = conn.execute(
            """
            SELECT paper_id
            FROM papers
            WHERE year = ?
              AND lower(authors) LIKE ?
            LIMIT 3
            """,
            (int(year), f"%{lead_author}%"),
        ).fetchall()
        if len(rows) == 1 and rows[0][0]:
            return str(rows[0][0]), 0.75, "author_year_unique"
        if len(rows) > 1:
            return "", 0.3, "author_year_ambiguous"

    return "", 0.0, "unresolved"


def extract_discourse_rows(
    pdf_path: Path,
    paper_id: str,
    article_type_family: str,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    primary_sections = {"introduction", "related_work", "discussion", "conclusion"}
    fallback_sections = {"methods", "results"}
    sentences = extract_sectioned_sentences(pdf_path)
    if not sentences:
        return [], {"section_counts": {}, "theory_links": 0, "inter_article_relations": 0}
    seen_sections = {str(entry.get("section", "other")) for entry in sentences}
    if seen_sections & primary_sections:
        target_sections = primary_sections
    else:
        # If expected sections are never detected, fall back to methods/results
        # to avoid zero-claim collapse on PDFs with atypical heading formats.
        target_sections = primary_sections | fallback_sections

    conn = sqlite3.connect(str(DEFAULT_AF_DB))
    conn.row_factory = sqlite3.Row
    rows: List[Dict[str, Any]] = []
    seen_keys = set()
    section_counts: Counter = Counter()
    theory_link_count = 0
    inter_article_count = 0

    try:
        for entry in sentences:
            section = str(entry.get("section", "other"))
            if section not in target_sections:
                continue
            sentence = str(entry.get("sentence", "")).strip()
            if not sentence:
                continue
            page = int(entry.get("page", 0) or 0)
            section_counts[section] += 1
            qhash = quote_hash(sentence)

            sentence_norm = normalize(sentence)
            detected_theories = [
                theory_name
                for theory_name, terms in THEORY_TERMS.items()
                if any(term in sentence_norm for term in terms)
            ]
            if detected_theories:
                t_relation, rel_hint, rel_strength = classify_theory_relation(sentence)
                for theory_name in detected_theories:
                    claim_id = f"disc:{paper_id}:theory:{theory_name}:{qhash[:10]}"
                    row_key = (claim_id, "theory_link")
                    if row_key in seen_keys:
                        continue
                    seen_keys.add(row_key)
                    edge_type = infer_edge_type_for_theory(sentence, t_relation)
                    evidence_basis = infer_edge_evidence_basis(edge_type)
                    statement = short_quote(sentence)
                    ae_conf = 0.62
                    rows.append(
                        {
                            "paper_id": paper_id,
                            "claim_id": claim_id,
                            "claim_type": "theory_link",
                            "node_id": claim_id,
                            "statement": statement,
                            "ae_confidence": f"{ae_conf:.6g}",
                            "node_type": infer_node_type(article_type_family, "theory_link", sentence),
                            "article_type_family": article_type_family,
                            "template_version": "unknown_with_reason:runtime_discourse_scan",
                            "causal_level": infer_causal_level(article_type_family, sentence),
                            "argument_scheme": infer_argument_scheme(article_type_family, "theory_link", sentence),
                            "edge_id": f"edge:{claim_id}",
                            "edge_type": edge_type,
                            "source_node_id": f"node:{paper_id}:{article_type_family}",
                            "target_node_id": f"theory:{safe_node_component(theory_name)}",
                            "weight": round(rel_strength, 4),
                            "evidence_basis": evidence_basis,
                            "needs_verification": "false",
                            "justification": statement,
                            "relation_type_hint": rel_hint,
                            "relation_strength_hint": round(rel_strength, 4),
                            "argument_relation_type": t_relation,
                            "theory_name": theory_name,
                            "source_section": section,
                            "source_page_start": page,
                            "source_page_end": page,
                            "source_quote": short_quote(sentence),
                            "source_quote_hash": qhash,
                            "source": "pdf_discourse_scan",
                            "evidence_level": "pdf_discourse_extracted",
                            "provenance_tier": "pdf_confirmed",
                            "requires_pdf_confirmation": "no",
                            "source_zone": section,
                            "extraction_difficulty": "moderate",
                            "processed_at": datetime.now(timezone.utc).isoformat(),
                            "quality_flag": "ok",
                        }
                    )
                    theory_link_count += 1

            citations = extract_citations(sentence)
            if not citations:
                continue

            relation_name, rel_hint, rel_strength = classify_article_relation(sentence)
            for citation in citations:
                target_paper_id, match_conf, match_type = resolve_citation_to_paper(conn, citation)
                claim_id = (
                    f"disc:{paper_id}:xref:{qhash[:10]}:"
                    f"{safe_node_component(citation.get('citation_text', 'cite'))[:18]}"
                )
                row_key = (claim_id, "inter_article_relation")
                if row_key in seen_keys:
                    continue
                seen_keys.add(row_key)
                edge_type = infer_edge_type_for_article(sentence, relation_name)
                evidence_basis = infer_edge_evidence_basis(edge_type)
                needs_verification = edge_type in {"ATTRIBUTES_FINDING", "INTERPRETS_AS"} or article_type_family in REVIEW_FAMILIES
                if target_paper_id:
                    target_node_id = f"node:{target_paper_id}"
                else:
                    target_node_id = f"citation:{safe_node_component(str(citation.get('citation_text', 'unknown')))}"
                statement = short_quote(sentence)
                rows.append(
                    {
                        "paper_id": paper_id,
                        "claim_id": claim_id,
                        "claim_type": "inter_article_relation",
                        "node_id": claim_id,
                        "statement": statement,
                        "ae_confidence": f"{max(0.45, rel_strength * 0.9):.6g}",
                        "node_type": infer_node_type(article_type_family, "inter_article_relation", sentence),
                        "article_type_family": article_type_family,
                        "template_version": "unknown_with_reason:runtime_discourse_scan",
                        "causal_level": infer_causal_level(article_type_family, sentence),
                        "argument_scheme": infer_argument_scheme(article_type_family, "inter_article_relation", sentence),
                        "edge_id": f"edge:{claim_id}",
                        "edge_type": edge_type,
                        "source_node_id": f"node:{paper_id}:{article_type_family}",
                        "target_node_id": target_node_id,
                        "weight": round(max(0.45, rel_strength * 0.9), 4),
                        "evidence_basis": evidence_basis,
                        "needs_verification": "true" if needs_verification else "false",
                        "justification": statement,
                        "relation_type_hint": rel_hint,
                        "relation_strength_hint": round(rel_strength, 4),
                        "argument_relation_type": relation_name,
                        "citation_text": citation.get("citation_text", ""),
                        "citation_doi": citation.get("doi", ""),
                        "target_paper_id": target_paper_id,
                        "citation_match_confidence": round(match_conf, 4),
                        "citation_match_type": match_type,
                        "source_section": section,
                        "source_page_start": page,
                        "source_page_end": page,
                        "source_quote": short_quote(sentence),
                        "source_quote_hash": qhash,
                        "source": "pdf_discourse_scan",
                        "evidence_level": "pdf_discourse_extracted",
                        "provenance_tier": "pdf_confirmed",
                        "requires_pdf_confirmation": "no",
                        "source_zone": section,
                        "extraction_difficulty": "moderate",
                        "processed_at": datetime.now(timezone.utc).isoformat(),
                        "quality_flag": "ok" if target_paper_id or match_type != "unresolved" else "needs_citation_resolution",
                    }
                )
                inter_article_count += 1
    finally:
        conn.close()

    return (
        rows,
        {
            "section_counts": dict(section_counts),
            "theory_links": theory_link_count,
            "inter_article_relations": inter_article_count,
        },
    )


def build_extraction_audit(
    paper_id: str,
    pdf_path: Path,
    status: str,
    n_tables: int,
    table_claim_count: int,
    confirmed_rows: List[Dict[str, Any]],
    discourse_summary: Dict[str, Any],
    error: str = "",
) -> Dict[str, Any]:
    claim_counts = Counter(str(r.get("claim_type", "")) for r in confirmed_rows)
    total_rows = len(confirmed_rows)
    anchored_rows = sum(1 for r in confirmed_rows if str(r.get("source_quote_hash", "")).strip())
    unresolved_env = sum(
        1
        for r in confirmed_rows
        if str(r.get("environment_canonical_id", "")).upper().startswith("UNRESOLVED:")
    )
    unresolved_out = sum(
        1
        for r in confirmed_rows
        if str(r.get("outcome_canonical_id", "")).upper().startswith("UNRESOLVED:")
    )
    section_counts = Counter(str(r.get("source_section", "") or "unknown") for r in confirmed_rows)
    env_match_counts = Counter(
        str(r.get("environment_resolution_match_type", "") or "missing").strip() or "missing"
        for r in confirmed_rows
    )
    out_match_counts = Counter(
        str(r.get("outcome_resolution_match_type", "") or "missing").strip() or "missing"
        for r in confirmed_rows
    )
    node_typed = sum(1 for r in confirmed_rows if str(r.get("node_type", "")).strip())
    relation_rows = [
        r
        for r in confirmed_rows
        if str(r.get("claim_type", "")).strip() in {"theory_link", "inter_article_relation"}
    ]
    edge_typed = sum(1 for r in relation_rows if str(r.get("edge_type", "")).strip())

    anchor_coverage = (anchored_rows / total_rows) if total_rows else 0.0
    unresolved_env_rate = (unresolved_env / total_rows) if total_rows else 0.0
    unresolved_out_rate = (unresolved_out / total_rows) if total_rows else 0.0
    env_llm_rate = (env_match_counts.get("llm_lookup_fallback", 0) / total_rows) if total_rows else 0.0
    out_llm_rate = (out_match_counts.get("llm_lookup_fallback", 0) / total_rows) if total_rows else 0.0
    env_semantic_rate = (env_match_counts.get("semantic_lookup_fallback", 0) / total_rows) if total_rows else 0.0
    out_semantic_rate = (out_match_counts.get("semantic_lookup_fallback", 0) / total_rows) if total_rows else 0.0
    node_type_tag_rate = (node_typed / total_rows) if total_rows else 0.0
    edge_type_tag_rate = (edge_typed / len(relation_rows)) if relation_rows else 1.0
    theory_links = int(discourse_summary.get("theory_links", 0))
    inter_article_relations = int(discourse_summary.get("inter_article_relations", 0))
    warnings: List[str] = []

    if n_tables == 0:
        warnings.append("no_tables_extracted")
    if table_claim_count == 0:
        warnings.append("no_table_claims")
    if anchor_coverage < 0.9:
        warnings.append("low_anchor_coverage")
    if theory_links == 0:
        warnings.append("no_theory_links")
    if inter_article_relations == 0:
        warnings.append("no_inter_article_relations")
    if unresolved_env_rate > 0.6 or unresolved_out_rate > 0.6:
        warnings.append("high_unresolved_construct_rate")
    if env_match_counts.get("missing", 0) > 0 or out_match_counts.get("missing", 0) > 0:
        warnings.append("missing_resolution_match_type")
    if node_type_tag_rate < 0.95:
        warnings.append("low_node_type_tag_rate")
    if relation_rows and edge_type_tag_rate < 0.90:
        warnings.append("low_edge_type_tag_rate")
    if error:
        warnings.append("worker_error")

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "paper_id": paper_id,
        "pdf_path": str(pdf_path),
        "status": status,
        "n_tables": n_tables,
        "table_claim_count": table_claim_count,
        "n_claims_total": total_rows,
        "claim_type_counts": dict(claim_counts),
        "anchor_coverage": round(anchor_coverage, 4),
        "unresolved_environment_rate": round(unresolved_env_rate, 4),
        "unresolved_outcome_rate": round(unresolved_out_rate, 4),
        "environment_resolution_match_type_counts": dict(env_match_counts),
        "outcome_resolution_match_type_counts": dict(out_match_counts),
        "environment_llm_fallback_rate": round(env_llm_rate, 4),
        "outcome_llm_fallback_rate": round(out_llm_rate, 4),
        "environment_semantic_fallback_rate": round(env_semantic_rate, 4),
        "outcome_semantic_fallback_rate": round(out_semantic_rate, 4),
        "node_type_tag_rate": round(node_type_tag_rate, 4),
        "edge_type_tag_rate": round(edge_type_tag_rate, 4),
        "section_coverage_counts": dict(section_counts),
        "discourse_section_hits": discourse_summary.get("section_counts", {}),
        "theory_link_count": theory_links,
        "inter_article_relation_count": inter_article_relations,
        "warnings": warnings,
        "error": error,
    }


def process_single_row(
    row_index: int,
    row: Dict[str, Any],
    queue_csv_path: Path,
    article_type_family: str,
    article_type_needs_review: bool = False,
) -> PaperProcessResult:
    paper_id = row.get("paper_id", "")
    pdf_path = resolve_pdf_path(row.get("pdf_path", ""), queue_csv_path)
    if not pdf_path.exists():
        return PaperProcessResult(
            row_index=row_index,
            status="missing_pdf",
            resolved_pdf_path=str(pdf_path),
            error="pdf_not_found",
            extraction_audit={
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "paper_id": paper_id,
                "pdf_path": str(pdf_path),
                "status": "missing_pdf",
                "warnings": ["missing_pdf"],
                "error": "pdf_not_found",
            },
        )

    try:
        integrator = PipelineTableIntegrator(
            api_client=None,
            extraction_method=ExtractionMethod.PDFPLUMBER,
            model="claude-3-haiku-20240307",
        )
        result = integrator.extract_and_convert(pdf_path=pdf_path, paper_id=paper_id)
        table_page_map: Dict[str, int] = {
            str(getattr(tbl, "table_id", "")): int(getattr(tbl, "page_number", 0) or 0)
            for tbl in result.tables
        }
        confirmed_rows: List[Dict[str, Any]] = []
        belief_specs: List[Dict[str, Any]] = []
        bridge_claims: List[Dict[str, Any]] = []

        for claim in result.claims:
            meta = claim.metadata or {}
            construct = resolve_env_outcome_from_claim(claim.content, meta, paper_id=paper_id)
            direction = claim_effect_direction(
                claim.content,
                metadata=meta,
                claim_type=str(claim.claim_type or ""),
            )
            confidence = float(claim.confidence or 0.6)
            rel_type, rel_strength, rel_prov = classify_argument_relation(
                claim.content,
                effect_direction=direction,
                claim_type=str(claim.claim_type or ""),
                metadata=meta,
            )
            source_page = int(table_page_map.get(str(getattr(claim, "source_table_id", "")), 0) or 0)
            claim_quote = short_quote(claim.content)
            qhash = quote_hash(claim_quote)
            statement = claim.content
            ae_confidence = float(claim.confidence or 0.6)
            node_type = infer_node_type(article_type_family, str(claim.claim_type or ""), statement)
            edge_type = "COHERENCE_SUPPORT"
            evidence_basis = "explicit_statement"
            needs_verification = "false"
            if node_type == "KNOWLEDGE_GAP":
                evidence_basis = "consensus"
            if node_type in {"EXPERT_SYNTHESIS", "METHODOLOGICAL_CRITIQUE"}:
                evidence_basis = "expert_opinion"
            if article_type_needs_review:
                needs_verification = "true"
            quality_flag = "ok" if source_page > 0 else "unanchored_claim"
            if article_type_needs_review:
                quality_flag = (
                    "needs_article_type_verification"
                    if quality_flag == "ok"
                    else f"{quality_flag}|needs_article_type_verification"
                )
            confirmed_rows.append(
                {
                    "paper_id": paper_id,
                    "claim_id": claim.claim_id,
                    "claim_type": claim.claim_type,
                    "node_id": claim.claim_id,
                    "statement": statement,
                    "ae_confidence": f"{ae_confidence:.6g}",
                    "node_type": node_type,
                    "article_type_family": article_type_family,
                    "article_type_needs_review": "true" if article_type_needs_review else "false",
                    "template_version": "unknown_with_reason:runtime_table_extractor",
                    "environment_variable": construct["environment_raw_term"],
                    "outcome_variable": construct["outcome_raw_term"],
                    "environment_candidates": construct["environment_candidates"],
                    "outcome_candidates": construct["outcome_candidates"],
                    "environment_canonical_id": construct["environment_canonical_id"],
                    "outcome_canonical_id": construct["outcome_canonical_id"],
                    "environment_resolution_confidence": round(float(construct["environment_resolution_confidence"]), 4),
                    "outcome_resolution_confidence": round(float(construct["outcome_resolution_confidence"]), 4),
                    "environment_resolution_match_type": construct["environment_resolution_match_type"],
                    "outcome_resolution_match_type": construct["outcome_resolution_match_type"],
                    "environment_node_id": construct["environment_node_id"],
                    "outcome_node_id": construct["outcome_node_id"],
                    "effect_direction": direction,
                    "edge_id": f"edge:{claim.claim_id}",
                    "edge_type": edge_type,
                    "source_node_id": construct["environment_node_id"],
                    "target_node_id": construct["outcome_node_id"],
                    "weight": round(float(rel_strength), 4),
                    "evidence_basis": evidence_basis,
                    "needs_verification": needs_verification,
                    "justification": claim_quote,
                    "relation_type_hint": rel_type,
                    "relation_strength_hint": round(float(rel_strength), 4),
                    "relation_provenance_hint": rel_prov,
                    "argument_relation_type": "table_claim",
                    "causal_level": infer_causal_level(article_type_family, statement),
                    "argument_scheme": infer_argument_scheme(article_type_family, str(claim.claim_type or ""), statement),
                    "source_section": "table",
                    "source_page_start": source_page,
                    "source_page_end": source_page,
                    "source_quote": claim_quote,
                    "source_quote_hash": qhash,
                    "source_table_id": str(getattr(claim, "source_table_id", "")),
                    "source_table_row": int(getattr(claim, "source_row", -1)),
                    "citation_context": str(meta.get("citation", "")),
                    "source": "codex_pdfplumber",
                    "evidence_level": "pdf_table_extracted",
                    "provenance_tier": "pdf_confirmed",
                    "requires_pdf_confirmation": "no",
                    "source_zone": "table",
                    "extraction_difficulty": "moderate",
                    "processed_at": datetime.now(timezone.utc).isoformat(),
                    "quality_flag": quality_flag,
                }
            )
            belief_specs.append(
                {
                    "belief_id": f"pdf:{paper_id}:{claim.claim_id}",
                    "content": claim.content,
                    "paper_id": paper_id,
                    "environment_id": construct["environment_node_id"],
                    "outcome_id": construct["outcome_node_id"],
                    "credence": confidence,
                    "claim_type": str(claim.claim_type or ""),
                    "effect_direction": direction,
                    "relation_type_hint": rel_type,
                    "relation_strength_hint": float(rel_strength),
                    "relation_provenance_hint": rel_prov,
                    "metadata": meta,
                }
            )
            bridge_claims.append(
                {
                    "paper_id": paper_id,
                    "claim_id": f"pdf:{paper_id}:{claim.claim_id}",
                    "statement": str(claim.content or ""),
                    "constructs": {
                        "outcomes": [{"id": construct["outcome_node_id"]}],
                        "inputs": [{"id": construct["environment_node_id"]}],
                    },
                    "metadata": meta,
                }
            )

        discourse_rows, discourse_summary = extract_discourse_rows(
            pdf_path=pdf_path,
            paper_id=paper_id,
            article_type_family=article_type_family,
        )
        if article_type_needs_review:
            for drow in discourse_rows:
                drow["needs_verification"] = "true"
                flag = str(drow.get("quality_flag", "ok") or "ok")
                if "needs_article_type_verification" not in flag:
                    drow["quality_flag"] = (
                        "needs_article_type_verification"
                        if flag == "ok"
                        else f"{flag}|needs_article_type_verification"
                    )
        confirmed_rows.extend(discourse_rows)

        status = "completed_pdf_extracted"
        if not confirmed_rows:
            status = "completed_pdf_no_claims"

        audit = build_extraction_audit(
            paper_id=paper_id,
            pdf_path=pdf_path,
            status=status,
            n_tables=len(result.tables),
            table_claim_count=len(result.claims),
            confirmed_rows=confirmed_rows,
            discourse_summary=discourse_summary,
            error="; ".join(result.errors) if result.errors else "",
        )

        return PaperProcessResult(
            row_index=row_index,
            status=status,
            n_tables=len(result.tables),
            n_claims=len(confirmed_rows),
            resolved_pdf_path=str(pdf_path),
            error="; ".join(result.errors) if result.errors else "",
            confirmed_rows=confirmed_rows,
            belief_specs=belief_specs,
            bridge_claims=bridge_claims,
            extraction_audit=audit,
        )
    except Exception as exc:
        return PaperProcessResult(
            row_index=row_index,
            status="error_pdf_processing",
            resolved_pdf_path=str(pdf_path),
            error=str(exc),
            extraction_audit={
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "paper_id": paper_id,
                "pdf_path": str(pdf_path),
                "status": "error_pdf_processing",
                "warnings": ["worker_error"],
                "error": str(exc),
            },
        )


def append_confirmed_rows(path: Path, rows: List[Dict[str, Any]]) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    ordered = [
        "paper_id",
        "claim_id",
        "claim_type",
        "node_id",
        "statement",
        "ae_confidence",
        "node_type",
        "article_type_family",
        "template_version",
        "environment_variable",
        "outcome_variable",
        "environment_candidates",
        "outcome_candidates",
        "environment_canonical_id",
        "outcome_canonical_id",
        "environment_resolution_confidence",
        "outcome_resolution_confidence",
        "environment_resolution_match_type",
        "outcome_resolution_match_type",
        "environment_node_id",
        "outcome_node_id",
        "effect_direction",
        "edge_id",
        "edge_type",
        "source_node_id",
        "target_node_id",
        "weight",
        "evidence_basis",
        "needs_verification",
        "justification",
        "relation_type_hint",
        "relation_strength_hint",
        "relation_provenance_hint",
        "argument_relation_type",
        "causal_level",
        "argument_scheme",
        "theory_name",
        "target_paper_id",
        "citation_text",
        "citation_doi",
        "citation_context",
        "citation_match_confidence",
        "citation_match_type",
        "source_section",
        "source_page_start",
        "source_page_end",
        "source_quote",
        "source_quote_hash",
        "source_table_id",
        "source_table_row",
        "quality_flag",
        "source",
        "evidence_level",
        "provenance_tier",
        "requires_pdf_confirmation",
        "source_zone",
        "extraction_difficulty",
        "processed_at",
    ]

    existing_rows: List[Dict[str, Any]] = []
    existing_fields: List[str] = []
    if path.exists():
        with path.open(encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            existing_fields = list(reader.fieldnames or [])
            existing_rows = list(reader)

    fieldnames = set(existing_fields)
    for row in existing_rows:
        fieldnames.update(row.keys())
    for row in rows:
        fieldnames.update(row.keys())

    for key in sorted(fieldnames):
        if key not in ordered:
            ordered.append(key)

    all_rows = existing_rows + rows
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=ordered)
        writer.writeheader()
        writer.writerows(all_rows)


def write_queue(path: Path, rows: List[Dict[str, Any]]) -> None:
    fieldnames = set()
    for row in rows:
        fieldnames.update(row.keys())
    ordered = [
        "paper_id",
        "doi",
        "title",
        "year",
        "venue",
        "pdf_path",
        "status",
        "queued_at",
        "processed_at",
        "reason",
        "source",
        "resolved_pdf_path",
        "n_tables",
        "n_claims",
        "error",
    ]
    for k in sorted(fieldnames):
        if k not in ordered:
            ordered.append(k)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=ordered)
        writer.writeheader()
        writer.writerows(rows)


def _as_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def _as_bool(value: Any) -> bool:
    return normalize(str(value)) in {"1", "true", "yes", "y"}


def write_article_type_review(
    path: Path,
    queue_rows: List[Dict[str, Any]],
    min_confidence: float,
    min_margin: float,
) -> int:
    rows: List[Dict[str, Any]] = []
    for row in queue_rows:
        family = str(row.get("article_type_family", "") or "")
        if not family:
            continue
        conf = _as_float(row.get("article_type_confidence", 0.0), default=0.0)
        margin = _as_float(row.get("article_type_margin", 0.0), default=0.0)
        flagged = _as_bool(row.get("article_type_needs_review", "false"))
        if not flagged and conf >= min_confidence and margin >= min_margin:
            continue

        reasons: List[str] = []
        if flagged:
            reasons.append("classifier_flagged")
        if conf < min_confidence:
            reasons.append("low_confidence")
        if margin < min_margin:
            reasons.append("low_margin")

        rows.append(
            {
                "paper_id": row.get("paper_id", ""),
                "doi": row.get("doi", ""),
                "title": row.get("title", ""),
                "year": row.get("year", ""),
                "venue": row.get("venue", ""),
                "status": row.get("status", ""),
                "article_type_family": family,
                "article_type_predicted_family": row.get("article_type_predicted_family", ""),
                "article_type_confidence": f"{conf:.4f}",
                "article_type_runner_up": row.get("article_type_runner_up", ""),
                "article_type_margin": f"{margin:.4f}",
                "article_type_signals": row.get("article_type_signals", ""),
                "article_type_diagnostics": row.get("article_type_diagnostics", ""),
                "type_review_flags": "|".join(reasons),
                "processed_at": row.get("processed_at", ""),
            }
        )

    fieldnames = [
        "paper_id",
        "doi",
        "title",
        "year",
        "venue",
        "status",
        "article_type_family",
        "article_type_predicted_family",
        "article_type_confidence",
        "article_type_runner_up",
        "article_type_margin",
        "article_type_signals",
        "article_type_diagnostics",
        "type_review_flags",
        "processed_at",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


def classify_no_claims_reason(title: str, venue: str) -> str:
    text = normalize(f"{title} {venue}")
    if any(k in text for k in ["theory", "theoretical", "framework", "conceptual", "model"]):
        return "likely_deep_theory_or_conceptual"
    if any(k in text for k in ["systematic review", "meta-analysis", "review"]):
        return "likely_synthesis_non_tabular"
    return "likely_non_tabular_or_table_unreadable"


def write_no_claims_review(path: Path, queue_rows: List[Dict[str, Any]]) -> None:
    rows: List[Dict[str, Any]] = []
    for row in queue_rows:
        if row.get("status") != "completed_pdf_no_claims":
            continue
        reason = classify_no_claims_reason(row.get("title", ""), row.get("venue", ""))
        rows.append(
            {
                "paper_id": row.get("paper_id", ""),
                "doi": row.get("doi", ""),
                "title": row.get("title", ""),
                "year": row.get("year", ""),
                "venue": row.get("venue", ""),
                "pdf_path": row.get("pdf_path", ""),
                "resolved_pdf_path": row.get("resolved_pdf_path", ""),
                "status": row.get("status", ""),
                "processed_at": row.get("processed_at", ""),
                "reason": reason,
                "needs_deep_theory_review": "yes",
            }
        )

    fieldnames = [
        "paper_id",
        "doi",
        "title",
        "year",
        "venue",
        "pdf_path",
        "resolved_pdf_path",
        "status",
        "processed_at",
        "reason",
        "needs_deep_theory_review",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def append_extraction_audits(path: Path, audits: List[Dict[str, Any]]) -> None:
    if not audits:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        for audit in audits:
            f.write(json.dumps(audit, ensure_ascii=True) + "\n")


def load_quality_thresholds(path: Path) -> Dict[str, float]:
    defaults = {
        "min_anchor_coverage": 0.9,
        "max_unresolved_environment_rate": 0.65,
        "max_unresolved_outcome_rate": 0.65,
        "min_theory_links_per_pdf": 1.0,
        "min_inter_article_relations_per_pdf": 1.0,
        "min_node_type_tag_rate": 0.95,
        "min_edge_type_tag_rate": 0.90,
    }
    if not path.exists():
        return defaults
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        for key, value in defaults.items():
            raw = data.get(key, value)
            try:
                defaults[key] = float(raw)
            except Exception:
                defaults[key] = value
    except Exception:
        return defaults
    return defaults


def write_manual_review_queue(
    path: Path,
    queue_rows: List[Dict[str, Any]],
    audits: List[Dict[str, Any]],
    thresholds: Dict[str, float],
) -> None:
    queue_index = {str(row.get("paper_id", "")): row for row in queue_rows}
    rows: List[Dict[str, Any]] = []
    seen: set = set()

    for audit in audits:
        paper_id = str(audit.get("paper_id", ""))
        if not paper_id or paper_id in seen:
            continue
        seen.add(paper_id)
        q = queue_index.get(paper_id, {})
        flags: List[str] = list(audit.get("warnings", []) or [])

        anchor_coverage = float(audit.get("anchor_coverage", 0.0) or 0.0)
        unresolved_env = float(audit.get("unresolved_environment_rate", 0.0) or 0.0)
        unresolved_out = float(audit.get("unresolved_outcome_rate", 0.0) or 0.0)
        theory_links = int(audit.get("theory_link_count", 0) or 0)
        inter_article = int(audit.get("inter_article_relation_count", 0) or 0)
        node_type_tag_rate = float(audit.get("node_type_tag_rate", 0.0) or 0.0)
        edge_type_tag_rate = float(audit.get("edge_type_tag_rate", 0.0) or 0.0)

        if anchor_coverage < thresholds["min_anchor_coverage"]:
            flags.append("below_anchor_coverage_threshold")
        if unresolved_env > thresholds["max_unresolved_environment_rate"]:
            flags.append("high_unresolved_environment_rate")
        if unresolved_out > thresholds["max_unresolved_outcome_rate"]:
            flags.append("high_unresolved_outcome_rate")
        if theory_links < int(thresholds["min_theory_links_per_pdf"]):
            flags.append("insufficient_theory_links")
        if inter_article < int(thresholds["min_inter_article_relations_per_pdf"]):
            flags.append("insufficient_inter_article_relations")
        if node_type_tag_rate < thresholds["min_node_type_tag_rate"]:
            flags.append("insufficient_node_type_tagging")
        if edge_type_tag_rate < thresholds["min_edge_type_tag_rate"]:
            flags.append("insufficient_edge_type_tagging")
        if str(q.get("status", "")).strip() == "completed_pdf_no_claims":
            flags.append("completed_pdf_no_claims")

        if not flags:
            continue

        rows.append(
            {
                "paper_id": paper_id,
                "doi": q.get("doi", ""),
                "title": q.get("title", ""),
                "year": q.get("year", ""),
                "venue": q.get("venue", ""),
                "status": q.get("status", ""),
                "n_tables": q.get("n_tables", ""),
                "n_claims": q.get("n_claims", ""),
                "anchor_coverage": f"{anchor_coverage:.4f}",
                "unresolved_environment_rate": f"{unresolved_env:.4f}",
                "unresolved_outcome_rate": f"{unresolved_out:.4f}",
                "theory_link_count": theory_links,
                "inter_article_relation_count": inter_article,
                "node_type_tag_rate": f"{node_type_tag_rate:.4f}",
                "edge_type_tag_rate": f"{edge_type_tag_rate:.4f}",
                "quality_flags": "|".join(sorted(set(flags))),
                "processed_at": q.get("processed_at", ""),
            }
        )

    fieldnames = [
        "paper_id",
        "doi",
        "title",
        "year",
        "venue",
        "status",
        "n_tables",
        "n_claims",
        "anchor_coverage",
        "unresolved_environment_rate",
        "unresolved_outcome_rate",
        "theory_link_count",
        "inter_article_relation_count",
        "node_type_tag_rate",
        "edge_type_tag_rate",
        "quality_flags",
        "processed_at",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def ensure_web_persistence_epistemic_v2(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    try:
        cols = [r[1] for r in conn.execute("PRAGMA table_info(beliefs)").fetchall()]
        if cols and "epistemic_v2" not in cols:
            conn.execute("ALTER TABLE beliefs ADD COLUMN epistemic_v2 TEXT")
            conn.commit()
    finally:
        conn.close()


def load_existing_abstract_belief(db_path: Path, paper_id: str) -> Dict[str, str]:
    """
    Load the abstract provisional belief that PDF processing should supersede.
    """
    belief_id = f"rt:{paper_id}:abstract_rule"
    conn = sqlite3.connect(str(db_path))
    try:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            """
            SELECT belief_id, content, environment_id, outcome_id
            FROM beliefs
            WHERE belief_id = ?
            LIMIT 1
            """,
            (belief_id,),
        ).fetchone()
        if not row:
            return {}
        return {
            "belief_id": row["belief_id"] or belief_id,
            "content": row["content"] or "",
            "environment_id": row["environment_id"] or "",
            "outcome_id": row["outcome_id"] or "",
        }
    finally:
        conn.close()


def _node_specificity(node_id: str) -> int:
    nid = normalize(node_id or "")
    if ".unresolved." in nid:
        return 0
    if ".generic." in nid:
        return 1
    return 2


def choose_primary_pdf_belief(beliefs: List[Any]) -> Any:
    """
    Prefer the most specific (canonical > generic > unresolved) and highest-confidence PDF belief.
    """
    def score(belief: Any) -> float:
        env_id = getattr(belief, "environment_id", "") or ""
        out_id = getattr(belief, "outcome_id", "") or ""
        cred = getattr(getattr(belief, "credence", None), "value", 0.0) or 0.0
        return float(_node_specificity(env_id) + _node_specificity(out_id)) * 10.0 + float(cred)

    return max(beliefs, key=score)


def make_constraint_id(source_id: str, target_id: str, ctype: str, provenance: str) -> str:
    raw = f"{source_id}|{target_id}|{ctype}|{provenance}"
    digest = hashlib.sha1(raw.encode("utf-8")).hexdigest()[:20]
    return f"c:arg:{digest}"


def primary_paper_id_from_json(raw: str) -> str:
    try:
        vals = json.loads(raw or "[]")
        if isinstance(vals, list) and vals:
            return str(vals[0])
    except Exception:
        pass
    return ""


def paper_year(paper_id: str) -> int:
    if not paper_id:
        return 0
    conn = sqlite3.connect(str(DEFAULT_AF_DB))
    try:
        row = conn.execute("SELECT year FROM papers WHERE paper_id = ? LIMIT 1", (paper_id,)).fetchone()
        if not row or row[0] is None:
            return 0
        try:
            return int(row[0])
        except Exception:
            return 0
    finally:
        conn.close()


def temporal_adjust(
    relation_type: str,
    base_strength: float,
    source_year: int,
    target_year: int,
    base_provenance: str,
) -> Tuple[str, float, str]:
    if not source_year or not target_year:
        return relation_type, base_strength, base_provenance

    lag = source_year - target_year
    prov = base_provenance
    strength = base_strength
    rel = relation_type

    # Later supporting replications contribute to consolidation.
    if rel == "supports" and lag >= 3:
        strength = min(0.85, strength + min(0.2, 0.03 * lag))
        prov = f"{prov}|temporal:consolidation_lag_{lag}"

    # Early challenges are expected turbulence, but still contradictions.
    if rel == "contradicts" and 0 <= lag <= 2:
        strength = min(0.8, strength + 0.05)
        prov = f"{prov}|temporal:early_challenge_lag_{lag}"

    # Late refinement/explanation often indicates maturation.
    if rel == "explains" and lag >= 4:
        strength = min(0.8, strength + 0.08)
        prov = f"{prov}|temporal:maturation_lag_{lag}"

    return rel, strength, prov


def fetch_peer_belief_ids(
    db_path: Path,
    environment_id: str,
    outcome_id: str,
    exclude_belief_ids: List[str],
    limit: int = 3,
) -> List[Dict[str, str]]:
    if not environment_id or not outcome_id:
        return []
    conn = sqlite3.connect(str(db_path))
    try:
        conn.row_factory = sqlite3.Row
        placeholders = ", ".join(["?"] * len(exclude_belief_ids)) if exclude_belief_ids else ""
        where_exclude = f"AND belief_id NOT IN ({placeholders})" if exclude_belief_ids else ""
        sql = f"""
        SELECT belief_id, paper_ids
        FROM beliefs
        WHERE web_id = 'master:web:accumulated'
          AND environment_id = ?
          AND outcome_id = ?
          {where_exclude}
        ORDER BY updated_at DESC
        LIMIT ?
        """
        params: List[Any] = [environment_id, outcome_id]
        if exclude_belief_ids:
            params.extend(exclude_belief_ids)
        params.append(limit)
        rows = conn.execute(sql, params).fetchall()
        out: List[Dict[str, str]] = []
        for r in rows:
            bid = str(r["belief_id"]) if r["belief_id"] else ""
            if not bid:
                continue
            out.append(
                {
                    "belief_id": bid,
                    "peer_paper_id": primary_paper_id_from_json(str(r["paper_ids"] or "[]")),
                }
            )
        return out
    finally:
        conn.close()


def preprocess_priority(row: Dict[str, Any]) -> int:
    status = normalize(str(row.get("preprocess_status", "")))
    if status == "ready":
        return 0
    if not status:
        return 1
    if status in {"quarantine", "error"}:
        return 3
    return 2


def load_family_context_for_papers(
    queue_rows: List[Dict[str, Any]],
    selected_indices: List[int],
) -> Dict[str, Dict[str, Any]]:
    paper_ids = [str(queue_rows[idx].get("paper_id", "")).strip() for idx in selected_indices]
    paper_ids = [pid for pid in paper_ids if pid]
    if not paper_ids:
        return {}

    placeholders = ",".join(["?"] * len(paper_ids))
    out: Dict[str, Dict[str, Any]] = {}
    conn = sqlite3.connect(str(DEFAULT_AF_DB))
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            f"""
            SELECT paper_id, title, abstract, venue
            FROM papers
            WHERE paper_id IN ({placeholders})
            """,
            paper_ids,
        ).fetchall()
        for row in rows:
            pid = str(row["paper_id"] or "").strip()
            if not pid:
                continue
            fam = classify_template_family_with_diagnostics(
                title=str(row["title"] or ""),
                abstract=str(row["abstract"] or ""),
                venue=str(row["venue"] or ""),
            )
            out[pid] = fam
    finally:
        conn.close()

    for idx in selected_indices:
        pid = str(queue_rows[idx].get("paper_id", "")).strip()
        if not pid or pid in out:
            continue
        out[pid] = classify_template_family_with_diagnostics(
            title=str(queue_rows[idx].get("title", "") or ""),
            abstract="",
            venue=str(queue_rows[idx].get("venue", "") or ""),
        )
    return out


def main() -> int:
    args = parse_args()
    global DEFAULT_AF_DB, DEFAULT_WEB_DB
    DEFAULT_AF_DB = resolve_article_finder_db(args.af_db)
    DEFAULT_WEB_DB = resolve_web_db(args.web_db, prefer=args.web_db_prefer)
    print(f"[pdf_completion] using af_db={DEFAULT_AF_DB} web_db={DEFAULT_WEB_DB}")

    queue_csv_path = Path(args.queue_csv)
    confirmed_csv_path = Path(args.confirmed_csv)
    no_claims_csv_path = Path(args.no_claims_csv)
    audit_jsonl_path = Path(args.audit_jsonl)
    manual_review_csv_path = Path(args.manual_review_csv)
    quality_thresholds_path = Path(args.quality_thresholds)
    article_type_review_csv_path = Path(args.article_type_review_csv)

    if not queue_csv_path.exists():
        print(f"Queue file not found: {queue_csv_path}")
        return 0

    with queue_csv_path.open(encoding="utf-8", newline="") as f:
        queue_rows = list(csv.DictReader(f))

    queued_indices = [
        idx
        for idx, row in enumerate(queue_rows)
        if str(row.get("status", "")).startswith("queued_")
    ]
    if args.skip_preprocess_quarantine:
        queued_indices = [
            idx
            for idx in queued_indices
            if normalize(str(queue_rows[idx].get("preprocess_status", ""))) not in {"quarantine", "error"}
        ]

    if args.prioritize_preprocessed:
        queued_indices.sort(key=lambda idx: preprocess_priority(queue_rows[idx]))

    selected_indices = queued_indices[: args.batch_size]

    if args.dry_run:
        print(f"Queued rows total: {len(queued_indices)}")
        print(f"Would process this run: {len(selected_indices)}")
        return 0

    if not selected_indices:
        print("No queued PDF rows to process.")
        return 0

    family_by_paper = load_family_context_for_papers(queue_rows, selected_indices)

    results: List[PaperProcessResult] = []
    max_workers = max(1, int(args.max_workers))
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = {}
        for idx in selected_indices:
            paper_id = str(queue_rows[idx].get("paper_id", "")).strip()
            fam_meta = family_by_paper.get(paper_id, {})
            futures[
                ex.submit(
                    process_single_row,
                    idx,
                    queue_rows[idx],
                    queue_csv_path,
                    str(fam_meta.get("family", "unknown")),
                    bool(fam_meta.get("needs_review", False)),
                )
            ] = idx
        for fut in as_completed(futures):
            results.append(fut.result())

    # Sort for deterministic status updates
    results.sort(key=lambda r: r.row_index)

    # Integrate into web/BN (serial to avoid concurrency races in persistence layers)
    web_integrated = 0
    bn_updated = 0
    bridges_integrated = 0
    if args.integrate_web or args.update_bn:
        if args.integrate_web:
            ensure_web_persistence_epistemic_v2(DEFAULT_WEB_DB)

        from src.services.bridge_warrants import BridgeRegistry, detect_bridge_from_claim
        from src.services.web_accumulator import get_accumulator
        from src.services.web_of_belief import (
            Belief,
            BeliefStatus,
            Constraint,
            ConstraintType,
            Credence,
            EpistemicLevel,
            SourceDepth,
            create_neuroarchitecture_web,
        )
        from src.services.incremental_bn import get_bn_builder

        accumulator = get_accumulator()
        bn_builder = get_bn_builder(Path(args.bn_state_path)) if args.update_bn else None

        by_paper: Dict[str, List[Belief]] = {}
        claims_by_paper: Dict[str, List[Dict[str, Any]]] = {}
        for res in results:
            for spec in res.belief_specs:
                belief = Belief(
                    belief_id=spec["belief_id"],
                    content=spec["content"],
                    level=EpistemicLevel.EMPIRICAL,
                    status=BeliefStatus.ESTABLISHED if float(spec["credence"]) >= 0.75 else BeliefStatus.TENTATIVE,
                    credence=Credence(value=float(spec["credence"]), uncertainty=0.30),
                    paper_ids=[spec["paper_id"]],
                    domain="realtime_pdf",
                    tags=[
                        "source:pdf",
                        "provenance:pdf_confirmed",
                        "requires_pdf_confirmation:false",
                        f"effect_direction:{spec.get('effect_direction', 'unknown')}",
                        f"claim_type:{spec.get('claim_type', 'unknown')}",
                    ],
                    environment_id=spec["environment_id"],
                    outcome_id=spec["outcome_id"],
                    source_depth=SourceDepth.FULL_TEXT,
                )
                by_paper.setdefault(spec["paper_id"], []).append(belief)
            for claim in res.bridge_claims:
                pid = str(claim.get("paper_id", "")).strip()
                if not pid:
                    continue
                claims_by_paper.setdefault(pid, []).append(claim)

        for paper_id, beliefs in by_paper.items():
            primary = choose_primary_pdf_belief(beliefs)
            existing_abstract = load_existing_abstract_belief(DEFAULT_WEB_DB, paper_id)
            bridge_registry = BridgeRegistry()
            bridge_keys = set()

            # Use the abstract belief_id so PDF canonical mapping supersedes abstract inference.
            override_content = (
                existing_abstract.get("content")
                or f"PDF-canonical override: {primary.environment_id} -> {primary.outcome_id}"
            )
            override_belief = Belief(
                belief_id=f"rt:{paper_id}:abstract_rule",
                content=override_content,
                level=EpistemicLevel.EMPIRICAL,
                status=BeliefStatus.ESTABLISHED,
                credence=Credence(value=max(0.8, float(primary.credence.value)), uncertainty=0.22),
                paper_ids=[paper_id],
                domain="realtime_pdf",
                tags=[
                    "source:pdf",
                    "provenance:pdf_confirmed",
                    "canonical_override:true",
                    "supersedes:abstract_provisional",
                ],
                environment_id=primary.environment_id,
                outcome_id=primary.outcome_id,
                source_depth=SourceDepth.FULL_TEXT,
            )

            if args.integrate_web:
                web = create_neuroarchitecture_web()
                web.beliefs.clear()
                web.constraints.clear()
                web.add_belief(override_belief)
                for b in beliefs:
                    tags = list(getattr(b, "tags", []) or [])
                    effect_direction = "unknown"
                    claim_type = "unknown"
                    for tag in tags:
                        if tag.startswith("effect_direction:"):
                            effect_direction = tag.split(":", 1)[1]
                        elif tag.startswith("claim_type:"):
                            claim_type = tag.split(":", 1)[1]
                    rel_type, rel_strength, rel_prov = classify_argument_relation(
                        b.content,
                        effect_direction=effect_direction,
                        claim_type=claim_type,
                    )
                    ctype = ConstraintType(rel_type)
                    web.add_belief(b)
                    # Add provenance-bearing constraint explicitly (for DB fields warrant/provenance).
                    c = Constraint(
                        constraint_id=make_constraint_id(
                            b.belief_id, override_belief.belief_id, ctype.value, rel_prov
                        ),
                        source_id=b.belief_id,
                        target_id=override_belief.belief_id,
                        constraint_type=ctype,
                        strength=rel_strength,
                        bidirectional=False,
                        evidence_ids=[paper_id],
                    )
                    c.warrant_type = "argument_relation"  # type: ignore[attr-defined]
                    c.provenance = rel_prov  # type: ignore[attr-defined]
                    web.add_constraint(c)

                # Cross-paper bridge: connect this paper's canonical override to a few prior
                # beliefs with same env/out to encode convergent/contested argument structure.
                peer_refs = fetch_peer_belief_ids(
                    DEFAULT_WEB_DB,
                    environment_id=primary.environment_id,
                    outcome_id=primary.outcome_id,
                    exclude_belief_ids=[override_belief.belief_id] + [b.belief_id for b in beliefs],
                    limit=3,
                )
                rel_type, rel_strength, rel_prov = classify_argument_relation(primary.content)
                src_year = paper_year(paper_id)
                for ref in peer_refs:
                    peer_id = ref["belief_id"]
                    peer_year = paper_year(ref.get("peer_paper_id", ""))
                    adj_type, adj_strength, adj_prov = temporal_adjust(
                        rel_type, rel_strength, src_year, peer_year, rel_prov
                    )
                    c = Constraint(
                        constraint_id=make_constraint_id(
                            override_belief.belief_id,
                            peer_id,
                            adj_type,
                            f"cross_paper:shared_env_out|{adj_prov}",
                        ),
                        source_id=override_belief.belief_id,
                        target_id=peer_id,
                        constraint_type=ConstraintType(adj_type),
                        strength=adj_strength,
                        bidirectional=False,
                        evidence_ids=[paper_id],
                    )
                    c.warrant_type = "cross_paper_alignment"  # type: ignore[attr-defined]
                    c.provenance = f"cross_paper:shared_env_out|{adj_prov}"  # type: ignore[attr-defined]
                    web.add_constraint(c)
                for claim in claims_by_paper.get(paper_id, []):
                    bridge = detect_bridge_from_claim(claim, target_domain="architectural_perception")
                    if not bridge:
                        continue
                    key = (bridge.source_domain, bridge.target_domain, bridge.bridge_type.value)
                    if key in bridge_keys:
                        continue
                    bridge_keys.add(key)
                    if override_belief.belief_id not in bridge.target_beliefs:
                        bridge.target_beliefs.append(override_belief.belief_id)
                    bridge_registry.add(bridge)
                accumulator.integrate_paper(web, paper_id=paper_id, bridge_registry=bridge_registry)
                bridges_integrated += len(bridge_registry.all())
                web_integrated += len(beliefs) + 1

            if args.update_bn and bn_builder is not None:
                bn_builder.observe_belief(override_belief, weight=float(args.bn_pdf_weight))
                bn_updated += 1
                for b in beliefs:
                    bn_builder.observe_belief(b, weight=float(args.bn_pdf_weight))
                    bn_updated += 1

                # If abstract mapping differs from PDF-canonical mapping, add counter-evidence
                # to the old abstract edge so BN no longer keeps that mapping as-is.
                old_env = existing_abstract.get("environment_id", "")
                old_out = existing_abstract.get("outcome_id", "")
                if old_env and old_out and (old_env != primary.environment_id or old_out != primary.outcome_id):
                    superseded = Belief(
                        belief_id=f"rt:{paper_id}:abstract_rule:superseded",
                        content="Superseded abstract mapping by PDF canonical evidence",
                        level=EpistemicLevel.EMPIRICAL,
                        status=BeliefStatus.ANOMALOUS,
                        credence=Credence(value=0.0, uncertainty=0.15),
                        paper_ids=[paper_id],
                        domain="realtime_pdf",
                        tags=[
                            "source:pdf",
                            "supersedes:abstract_provisional",
                            "bn_counterevidence:true",
                        ],
                        environment_id=old_env,
                        outcome_id=old_out,
                        source_depth=SourceDepth.FULL_TEXT,
                    )
                    bn_builder.observe_belief(superseded, weight=float(args.bn_pdf_weight))
                    bn_updated += 1

        if args.update_bn and bn_builder is not None:
            bn_builder.save_state(Path(args.bn_state_path))

    # Update queue rows and collect confirmed rows
    now_iso = datetime.now(timezone.utc).isoformat()
    confirmed_rows: List[Dict[str, Any]] = []
    extraction_audits: List[Dict[str, Any]] = []
    for res in results:
        row = queue_rows[res.row_index]
        paper_id = str(row.get("paper_id", "")).strip()
        fam_meta = family_by_paper.get(paper_id, {})
        if paper_id:
            row["article_type_family"] = fam_meta.get("family", row.get("article_type_family", "unknown"))
            row["article_type_predicted_family"] = fam_meta.get(
                "predicted_family",
                row.get("article_type_predicted_family", ""),
            )
            row["article_type_confidence"] = fam_meta.get("confidence", row.get("article_type_confidence", ""))
            row["article_type_runner_up"] = fam_meta.get("runner_up", row.get("article_type_runner_up", ""))
            row["article_type_margin"] = fam_meta.get("margin", row.get("article_type_margin", ""))
            row["article_type_needs_review"] = fam_meta.get("needs_review", row.get("article_type_needs_review", ""))
            row["article_type_signals"] = fam_meta.get("signals", row.get("article_type_signals", ""))
            row["article_type_diagnostics"] = fam_meta.get("diagnostics", row.get("article_type_diagnostics", ""))
            row["article_type_classifier_version"] = fam_meta.get(
                "classifier_version",
                row.get("article_type_classifier_version", ""),
            )
        row["status"] = res.status
        row["processed_at"] = now_iso
        row["resolved_pdf_path"] = res.resolved_pdf_path
        row["n_tables"] = str(res.n_tables)
        row["n_claims"] = str(res.n_claims)
        row["error"] = res.error
        confirmed_rows.extend(res.confirmed_rows)
        if res.extraction_audit:
            extraction_audits.append(res.extraction_audit)

    append_confirmed_rows(confirmed_csv_path, confirmed_rows)
    write_queue(queue_csv_path, queue_rows)
    write_no_claims_review(no_claims_csv_path, queue_rows)
    append_extraction_audits(audit_jsonl_path, extraction_audits)
    thresholds = load_quality_thresholds(quality_thresholds_path)
    write_manual_review_queue(
        manual_review_csv_path,
        queue_rows=queue_rows,
        audits=extraction_audits,
        thresholds=thresholds,
    )
    type_review_count = write_article_type_review(
        article_type_review_csv_path,
        queue_rows=queue_rows,
        min_confidence=float(args.article_type_min_confidence),
        min_margin=float(args.article_type_min_margin),
    )

    ok = sum(1 for r in results if r.status.startswith("completed_"))
    missing = sum(1 for r in results if r.status == "missing_pdf")
    failed = sum(1 for r in results if r.status.startswith("error_"))
    print(f"Processed queue rows: {len(results)}")
    print(f"Completed: {ok}, Missing PDF: {missing}, Errors: {failed}")
    print(f"Confirmed rows appended: {len(confirmed_rows)} -> {confirmed_csv_path}")
    print(f"No-claims review rows written: {sum(1 for r in queue_rows if r.get('status') == 'completed_pdf_no_claims')} -> {no_claims_csv_path}")
    print(f"Extraction audits appended: {len(extraction_audits)} -> {audit_jsonl_path}")
    print(f"Manual quality review queue written: {manual_review_csv_path}")
    print(f"Article-type review rows written: {type_review_count} -> {article_type_review_csv_path}")
    if args.integrate_web:
        print(f"Integrated PDF-confirmed beliefs into web: {web_integrated}")
        print(f"Bridge warrants integrated: {bridges_integrated}")
    if args.update_bn:
        print(f"Updated incremental BN from PDF-confirmed beliefs: {bn_updated}")
    print(f"Queue updated: {queue_csv_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
