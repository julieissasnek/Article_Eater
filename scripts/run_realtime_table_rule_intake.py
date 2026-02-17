#!/usr/bin/env python3
"""
Realtime table+rule intake for newly discovered articles.

For each newly found AF paper (incremental by event timestamp):
1. Create an abstract-based provisional table record immediately.
2. Create an abstract-based provisional rule record immediately.
3. If a PDF path exists, enqueue the paper for PDF completion.
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
from difflib import SequenceMatcher
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple


PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
DEFAULT_AF_DB = Path("/Users/davidusa/REPOS/Article_Finder_v3_2_3/data/article_finder.db")
DEFAULT_WEB_DB = PROJECT_ROOT / "data" / "web_persistence.db"
from src.epistemic.extraction.paper_classifier import classify_paper

try:
    from lib.environment_resolver import resolve_environment, resolve_or_queue_environment
except Exception:
    resolve_environment = None
    resolve_or_queue_environment = None

try:
    from lib.outcome_resolver import queue_unknown_outcome, resolve_or_queue, resolve_outcome
except Exception:
    resolve_outcome = None
    resolve_or_queue = None
    queue_unknown_outcome = None

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

POSITIVE_TERMS = ["increase", "improve", "enhance", "boost", "higher", "better", "reduce stress"]
NEGATIVE_TERMS = ["decrease", "reduce", "lower", "impair", "worse", "higher stress"]
NULL_TERMS = ["no significant", "not significant", "no association", "null effect", "no effect"]

EMPIRICAL_ABSTRACT_RULE_FAMILIES = {
    "empirical_v2",
    "mixed_methods",
    "observational_field",
    "case_study",
}


@dataclass
class IntakeState:
    last_event_ts: str = ""
    last_paper_id: str = ""


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


def infer_node_type_for_family(article_type_family: str, statement: str) -> str:
    s = normalize(statement)
    if "gap" in s or "future research" in s:
        return "KNOWLEDGE_GAP"
    if article_type_family in {"meta_analysis", "systematic_review"}:
        return "SYNTHESIS_CONCLUSION"
    if article_type_family in {"interview_study", "ethnographic", "grounded_theory", "phenomenological"}:
        return "QUALITATIVE_FINDING"
    if article_type_family == "theoretical":
        if "hypothesis" in s or "predict" in s:
            return "DERIVED_HYPOTHESIS"
        if "define" in s:
            return "CONCEPTUAL_DEFINITION"
        return "THEORETICAL_PROPOSITION"
    if article_type_family == "conceptual_framework":
        if "must distinguish" in s or "must not conflate" in s:
            return "CONCEPTUAL_CONSTRAINT"
        if "taxonomy" in s or "framework" in s:
            return "FRAMEWORK_STRUCTURE"
        return "CONCEPTUAL_DEFINITION"
    if article_type_family == "narrative_review":
        return "EXPERT_SYNTHESIS"
    if article_type_family == "thought_piece":
        if any(k in s for k in ["bias", "methodological", "validity", "artifact"]):
            return "METHODOLOGICAL_CRITIQUE"
        return "EXPERT_SYNTHESIS"
    return "EMPIRICAL_FINDING"


def safe_node_component(name: str) -> str:
    s = normalize(name)
    s = re.sub(r"[^a-z0-9_.]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("._")
    return s or "unknown"


def load_lookup_terms(path: Path) -> List[str]:
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []
    lookup = data.get("lookup", {})
    terms = [normalize(k) for k in lookup.keys() if isinstance(k, str)]
    terms = [t for t in terms if len(t) >= 3]
    return sorted(set(terms), key=len, reverse=True)


def load_lookup_map(path: Path) -> Dict[str, str]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    lookup = data.get("lookup", {})
    out: Dict[str, str] = {}
    for raw, canonical in lookup.items():
        if isinstance(raw, str) and isinstance(canonical, str):
            out[normalize(raw)] = canonical
    return out


ENV_LOOKUP_TERMS = load_lookup_terms(CONTRACT_ENV_LOOKUP)
OUTCOME_LOOKUP_TERMS = load_lookup_terms(CONTRACT_OUTCOME_LOOKUP)
ENV_LOOKUP_MAP = load_lookup_map(CONTRACT_ENV_LOOKUP)
OUTCOME_LOOKUP_MAP = load_lookup_map(CONTRACT_OUTCOME_LOOKUP)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Realtime table+rule intake for new AF papers.")
    parser.add_argument("--db", default=str(DEFAULT_AF_DB), help="Path to Article Finder DB")
    parser.add_argument("--limit", type=int, default=250, help="Max new papers per run")
    parser.add_argument("--min-abstract-len", type=int, default=200, help="Min abstract length")
    parser.add_argument(
        "--state-file",
        default="data/production/realtime_intake_state.json",
        help="Incremental watermark state file",
    )
    parser.add_argument(
        "--tables-jsonl",
        default="data/production/realtime_tables.jsonl",
        help="Output JSONL for provisional table records",
    )
    parser.add_argument(
        "--rules-jsonl",
        default="data/production/realtime_rules.jsonl",
        help="Output JSONL for provisional rule records",
    )
    parser.add_argument(
        "--pdf-queue-csv",
        default="data/production/realtime_pdf_completion_queue.csv",
        help="Output CSV queue for PDF completion",
    )
    parser.add_argument(
        "--integrate-web",
        action="store_true",
        help="Integrate generated provisional abstract beliefs into Web of Belief",
    )
    parser.add_argument(
        "--update-bn",
        action="store_true",
        help="Update incremental BN from generated provisional abstract beliefs",
    )
    parser.add_argument(
        "--bn-state-path",
        default="data/production/realtime_incremental_bn.json",
        help="Path for persisted incremental BN state",
    )
    parser.add_argument(
        "--bn-abstract-weight",
        type=float,
        default=0.45,
        help="Evidence weight for abstract-provisional BN updates",
    )
    parser.add_argument("--dry-run", action="store_true", help="Read and report without writing")
    return parser.parse_args()


def load_state(path: Path) -> IntakeState:
    if not path.exists():
        return IntakeState()
    data = json.loads(path.read_text(encoding="utf-8"))
    return IntakeState(
        last_event_ts=data.get("last_event_ts", ""),
        last_paper_id=data.get("last_paper_id", ""),
    )


def save_state(path: Path, state: IntakeState) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"last_event_ts": state.last_event_ts, "last_paper_id": state.last_paper_id}
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


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


def detect_generic_class(text: str, mapping: Dict[str, List[str]]) -> Optional[str]:
    norm = normalize(text)
    best = ""
    best_score = 0
    for canonical, keywords in mapping.items():
        score = sum(1 for kw in keywords if normalize(kw) in norm)
        if score > best_score:
            best = canonical
            best_score = score
    return best if best_score > 0 else None


def queue_unresolved_environment(raw_term: str) -> None:
    path = PROJECT_ROOT / "data" / "unresolved_environment.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"raw_term": normalize(raw_term)}
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload) + "\n")


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


def resolve_from_lookup(raw_term: str, lookup_map: Dict[str, str]) -> str:
    for variant in candidate_variants(raw_term):
        canonical = lookup_map.get(variant)
        if canonical:
            return canonical
    return ""


def semantic_lookup_fallback(
    raw_term: str,
    context_text: str,
    lookup_map: Dict[str, str],
    min_score: float = 0.70,
) -> Dict[str, Any]:
    """
    Constrained semantic fallback when exact lookup misses.

    This is a bounded fallback over known lookup terms only, reducing unresolved
    IDs without inventing out-of-vocabulary canonical IDs.
    """
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
        # Keep fallback confidence lower than exact resolver confidence.
        conf = max(0.40, min(0.74, round(best_score, 4)))
        return {
            "canonical_id": best_canonical,
            "confidence": conf,
            "matched_term": best_term,
        }
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
    """
    Optional LLM fallback over a constrained shortlist of known lookup terms.
    """
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
        "Choose the single best candidate term for ontology mapping.\n"
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


def resolve_environment_factor(raw_term: str, context_text: str = "") -> Dict[str, Any]:
    raw = normalize(raw_term)
    canonical = resolve_from_lookup(raw, ENV_LOOKUP_MAP)
    if canonical:
        return {
            "raw_term": raw,
            "canonical_id": canonical,
            "canonical_name": canonical,
            "confidence": 1.0,
            "match_type": "lookup_exact",
            "resolved": True,
        }

    if callable(resolve_environment):
        try:
            for variant in candidate_variants(raw):
                resolved = resolve_environment(variant, fuzzy_threshold=0.82)
                if resolved:
                    return {
                        "raw_term": raw,
                        "canonical_id": str(resolved.get("tag_id", "")),
                        "canonical_name": str(resolved.get("canonical_name", resolved.get("tag_id", raw))),
                        "confidence": float(resolved.get("confidence", 0.0)),
                        "match_type": f"resolver_{resolved.get('match_type', 'fuzzy')}",
                        "resolved": True,
                    }
        except Exception:
            pass

    if callable(resolve_or_queue_environment):
        try:
            resolved, _queued = resolve_or_queue_environment(raw)
            if resolved:
                return {
                    "raw_term": raw,
                    "canonical_id": str(resolved.get("tag_id", "")),
                    "canonical_name": str(resolved.get("canonical_name", resolved.get("tag_id", raw))),
                    "confidence": float(resolved.get("confidence", 0.0)),
                    "match_type": f"resolver_{resolved.get('match_type', 'queued')}",
                    "resolved": True,
                }
        except Exception:
            pass

    llm_guess = llm_lookup_fallback(raw, context_text, ENV_LOOKUP_MAP)
    if llm_guess["canonical_id"]:
        return {
            "raw_term": raw,
            "canonical_id": llm_guess["canonical_id"],
            "canonical_name": llm_guess["canonical_id"],
            "confidence": float(llm_guess["confidence"]),
            "match_type": "llm_lookup_fallback",
            "resolved": True,
        }

    semantic = semantic_lookup_fallback(raw, context_text, ENV_LOOKUP_MAP)
    if semantic["canonical_id"]:
        return {
            "raw_term": raw,
            "canonical_id": semantic["canonical_id"],
            "canonical_name": semantic["canonical_id"],
            "confidence": float(semantic["confidence"]),
            "match_type": "semantic_lookup_fallback",
            "resolved": True,
        }

    generic = detect_generic_class(f"{raw} {context_text}", GENERIC_ENV_KEYWORDS)
    if generic:
        return {
            "raw_term": raw,
            "canonical_id": f"env.generic.{generic}",
            "canonical_name": f"generic_{generic}",
            "confidence": 0.35,
            "match_type": "generic_keyword",
            "resolved": True,
        }

    try:
        queue_unresolved_environment(raw)
    except Exception:
        pass

    return {
        "raw_term": raw,
        "canonical_id": f"UNRESOLVED:environment:{safe_node_component(raw)[:48]}",
        "canonical_name": raw,
        "confidence": 0.0,
        "match_type": "unresolved",
        "resolved": False,
    }


def resolve_outcome_factor(raw_term: str, paper_id: str, context_text: str = "") -> Dict[str, Any]:
    raw = normalize(raw_term)
    canonical = resolve_from_lookup(raw, OUTCOME_LOOKUP_MAP)
    if canonical:
        return {
            "raw_term": raw,
            "canonical_id": canonical,
            "canonical_name": canonical,
            "confidence": 1.0,
            "match_type": "lookup_exact",
            "resolved": True,
        }

    if callable(resolve_outcome):
        try:
            for variant in candidate_variants(raw):
                resolved = resolve_outcome(variant, fuzzy_threshold=0.82)
                if resolved:
                    return {
                        "raw_term": raw,
                        "canonical_id": str(resolved.get("canonical_id", "")),
                        "canonical_name": str(resolved.get("name", raw)),
                        "confidence": float(resolved.get("confidence", 0.0)),
                        "match_type": f"resolver_{resolved.get('match_type', 'fuzzy')}",
                        "resolved": True,
                    }
        except Exception:
            pass

    queued_unresolved = False
    if callable(resolve_or_queue):
        try:
            queued = resolve_or_queue(raw, paper_id=paper_id)
            if queued:
                canonical_id = str(queued.get("canonical_id", ""))
                unresolved = canonical_id.startswith("UNRESOLVED:")
                if not unresolved:
                    return {
                        "raw_term": raw,
                        "canonical_id": canonical_id,
                        "canonical_name": queued.get("name", raw),
                        "confidence": float(queued.get("confidence", 0.0)),
                        "match_type": str(queued.get("match_type", "resolver_queued")),
                        "resolved": True,
                    }
                queued_unresolved = True
        except Exception:
            pass

    llm_guess = llm_lookup_fallback(raw, context_text, OUTCOME_LOOKUP_MAP)
    if llm_guess["canonical_id"]:
        return {
            "raw_term": raw,
            "canonical_id": llm_guess["canonical_id"],
            "canonical_name": llm_guess["canonical_id"],
            "confidence": float(llm_guess["confidence"]),
            "match_type": "llm_lookup_fallback",
            "resolved": True,
        }

    semantic = semantic_lookup_fallback(raw, context_text, OUTCOME_LOOKUP_MAP)
    if semantic["canonical_id"]:
        return {
            "raw_term": raw,
            "canonical_id": semantic["canonical_id"],
            "canonical_name": semantic["canonical_id"],
            "confidence": float(semantic["confidence"]),
            "match_type": "semantic_lookup_fallback",
            "resolved": True,
        }

    generic = detect_generic_class(f"{raw} {context_text}", GENERIC_OUTCOME_KEYWORDS)
    if generic:
        return {
            "raw_term": raw,
            "canonical_id": f"out.generic.{generic}",
            "canonical_name": f"generic_{generic}",
            "confidence": 0.35,
            "match_type": "generic_keyword",
            "resolved": True,
        }

    if not queued_unresolved and callable(queue_unknown_outcome):
        try:
            queue_unknown_outcome(raw, paper_id=paper_id, context=context_text[:500] if context_text else None)
        except Exception:
            pass

    return {
        "raw_term": raw,
        "canonical_id": f"UNRESOLVED:outcome:{safe_node_component(raw)[:48]}",
        "canonical_name": raw,
        "confidence": 0.0,
        "match_type": "unresolved",
        "resolved": False,
    }


def infer_env_out_terms(title: str, abstract: str) -> Tuple[str, List[str], str, List[str]]:
    combined = normalize(f"{title} {abstract}")
    env_terms = extract_lookup_matches(combined, ENV_LOOKUP_TERMS)
    out_terms = extract_lookup_matches(combined, OUTCOME_LOOKUP_TERMS)

    env_raw = env_terms[0] if env_terms else ""
    out_raw = out_terms[0] if out_terms else ""

    if not env_raw or not out_raw:
        left, right = extract_of_on_pair(combined)
        if left and not env_raw:
            env_raw = left
        if right and not out_raw:
            out_raw = right

    if not env_raw:
        env_raw = fallback_term(normalize(title), "unspecified_environment")
    if not out_raw:
        out_raw = fallback_term(normalize(title), "unspecified_outcome")

    if env_raw not in env_terms:
        env_terms = [env_raw] + env_terms
    if out_raw not in out_terms:
        out_terms = [out_raw] + out_terms

    return env_raw, env_terms[:8], out_raw, out_terms[:8]


def detect_effect_direction(text: str) -> str:
    if any(term in text for term in NULL_TERMS):
        return "null"
    pos = any(term in text for term in POSITIVE_TERMS)
    neg = any(term in text for term in NEGATIVE_TERMS)
    if pos and neg:
        return "mixed"
    if pos:
        return "positive"
    if neg:
        return "negative"
    return "unknown"


def extract_sample_n(text: str) -> str:
    match = re.search(r"\bn\s*=\s*(\d+)\b", text)
    return match.group(1) if match else ""


def safe_var_name(name: str) -> str:
    return re.sub(r"[^a-z0-9_]+", "_", normalize(name))


def polarity_for_effect(effect_direction: str) -> str:
    if effect_direction in {"positive", "negative", "null", "u_shaped"}:
        return effect_direction
    if effect_direction == "mixed":
        return "unknown"
    return "unknown"


def confidence_for_effect(effect_direction: str, sample_n: str) -> float:
    score = 0.35
    if effect_direction in {"positive", "negative", "null", "mixed"}:
        score += 0.15
    if sample_n:
        score += 0.10
    return min(score, 0.75)


def evaluate_abstract_rule_gate(article_type_family: str, family_meta: Dict[str, Any]) -> Dict[str, Any]:
    confidence = float(family_meta.get("confidence", 0.0) or 0.0)
    margin = float(family_meta.get("margin", 0.0) or 0.0)
    needs_review = bool(family_meta.get("needs_review", False))

    if article_type_family not in EMPIRICAL_ABSTRACT_RULE_FAMILIES:
        return {
            "eligible": False,
            "policy": "defer_non_empirical_abstract_causal_rule",
            "reason": f"family_not_empirical:{article_type_family or 'unknown'}",
        }
    if needs_review:
        return {
            "eligible": False,
            "policy": "defer_uncertain_type_abstract_causal_rule",
            "reason": "article_type_needs_review",
        }
    if confidence < 0.60:
        return {
            "eligible": False,
            "policy": "defer_uncertain_type_abstract_causal_rule",
            "reason": f"low_article_type_confidence:{confidence:.2f}",
        }
    if margin < 0.25:
        return {
            "eligible": False,
            "policy": "defer_uncertain_type_abstract_causal_rule",
            "reason": f"low_article_type_margin:{margin:.2f}",
        }
    return {
        "eligible": True,
        "policy": "emit_empirical_abstract_causal_rule",
        "reason": "",
    }


def classify_abstract_relation(effect_direction: str, abstract_text: str) -> Tuple[str, float, str]:
    text = normalize(abstract_text or "")
    if effect_direction in {"negative", "null"}:
        return ("contradicts", 0.58, "argument:abstract_negative_or_null")
    if any(k in text for k in ("mechanism", "mediat", "pathway", "moderat", "boundary condition")):
        return ("explains", 0.50, "argument:abstract_mechanism_or_boundary")
    if effect_direction in {"mixed", "unknown"}:
        return ("explains", 0.42, "argument:abstract_ambiguous_context")
    return ("supports", 0.48, "argument:abstract_positive_effect")


def make_constraint_id(source_id: str, target_id: str, ctype: str, provenance: str) -> str:
    raw = f"{source_id}|{target_id}|{ctype}|{provenance}"
    digest = hashlib.sha1(raw.encode("utf-8")).hexdigest()[:20]
    return f"c:abs:{digest}"


def primary_paper_id_from_json(raw: str) -> str:
    try:
        vals = json.loads(raw or "[]")
        if isinstance(vals, list) and vals:
            return str(vals[0])
    except Exception:
        pass
    return ""


def fetch_peer_belief_ids(
    db_path: Path,
    environment_id: str,
    outcome_id: str,
    exclude_belief_ids: List[str],
    limit: int = 2,
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


def ensure_web_persistence_epistemic_v2(db_path: Path) -> None:
    """
    Ensure V24 column exists in beliefs table.

    Some existing local DBs predate ARCH-4 column additions.
    """
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    try:
        cols = [r[1] for r in conn.execute("PRAGMA table_info(beliefs)").fetchall()]
        if cols and "epistemic_v2" not in cols:
            conn.execute("ALTER TABLE beliefs ADD COLUMN epistemic_v2 TEXT")
            conn.commit()
    finally:
        conn.close()


def query_new_papers(conn: sqlite3.Connection, state: IntakeState, min_abstract_len: int, limit: int) -> List[sqlite3.Row]:
    query = """
    SELECT
      paper_id,
      doi,
      title,
      year,
      venue,
      abstract,
      pdf_path,
      COALESCE(created_at, retrieved_at, updated_at, '') AS event_ts
    FROM papers
    WHERE abstract IS NOT NULL
      AND LENGTH(abstract) >= ?
      AND (off_topic_flag IS NULL OR off_topic_flag = 0)
      AND (
        COALESCE(created_at, retrieved_at, updated_at, '') > ?
        OR (
          COALESCE(created_at, retrieved_at, updated_at, '') = ?
          AND paper_id > ?
        )
      )
    ORDER BY event_ts ASC, paper_id ASC
    LIMIT ?
    """
    params = [min_abstract_len, state.last_event_ts, state.last_event_ts, state.last_paper_id, limit]
    cur = conn.execute(query, params)
    return cur.fetchall()


def load_existing_pdf_queue_ids(path: Path) -> set[str]:
    if not path.exists():
        return set()
    with path.open(encoding="utf-8", newline="") as f:
        return {row.get("paper_id", "") for row in csv.DictReader(f)}


def append_jsonl(path: Path, records: List[Dict[str, Any]]) -> None:
    if not records:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec) + "\n")


def write_pdf_queue(path: Path, existing_rows: List[Dict[str, Any]], new_rows: List[Dict[str, Any]]) -> None:
    if not new_rows and path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = existing_rows + new_rows
    fieldnames = [
        "paper_id",
        "doi",
        "title",
        "year",
        "venue",
        "pdf_path",
        "status",
        "queued_at",
        "reason",
        "source",
    ]
    extra = sorted({k for row in rows for k in row.keys() if k not in fieldnames})
    fieldnames.extend(extra)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def load_pdf_queue_rows(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def main() -> int:
    args = parse_args()
    state_path = Path(args.state_file)
    tables_path = Path(args.tables_jsonl)
    rules_path = Path(args.rules_jsonl)
    pdf_queue_path = Path(args.pdf_queue_csv)
    now_iso = datetime.now(timezone.utc).isoformat()

    state = load_state(state_path)

    conn = sqlite3.connect(args.db)
    conn.row_factory = sqlite3.Row
    papers = query_new_papers(conn, state, args.min_abstract_len, args.limit)
    conn.close()

    table_records: List[Dict[str, Any]] = []
    rule_records: List[Dict[str, Any]] = []

    existing_queue_rows = load_pdf_queue_rows(pdf_queue_path)
    existing_pdf_queue_ids = {row.get("paper_id", "") for row in existing_queue_rows}
    new_pdf_queue_rows: List[Dict[str, Any]] = []

    last_ts = state.last_event_ts
    last_paper_id = state.last_paper_id

    for p in papers:
        paper_id = p["paper_id"]
        abstract_text = normalize(p["abstract"] or "")
        title_text = p["title"] or ""
        family_meta = classify_template_family_with_diagnostics(
            title=title_text,
            abstract=p["abstract"] or "",
            venue=p["venue"] or "",
        )
        article_type_family = family_meta["family"]
        rule_gate = evaluate_abstract_rule_gate(article_type_family, family_meta)
        env_var, env_candidates, out_var, out_candidates = infer_env_out_terms(title_text, abstract_text)
        context_text = normalize(f"{title_text} {abstract_text}")
        env_resolution = resolve_environment_factor(env_var, context_text=context_text)
        out_resolution = resolve_outcome_factor(out_var, paper_id=paper_id, context_text=context_text)
        env_node_id = to_node_id("env", env_resolution["canonical_id"], env_resolution["raw_term"])
        out_node_id = to_node_id("out", out_resolution["canonical_id"], out_resolution["raw_term"])
        effect = detect_effect_direction(abstract_text)
        sample_n = extract_sample_n(abstract_text)
        has_pdf = bool((p["pdf_path"] or "").strip())
        event_ts = p["event_ts"] or ""

        snippet = (p["abstract"] or "").strip()
        if len(snippet) > 320:
            snippet = snippet[:317] + "..."

        table_records.append(
            {
                "record_type": "table_record",
                "table_kind": "abstract_reduced_table",
                "paper_id": paper_id,
                "doi": p["doi"] or "",
                "title": p["title"] or "",
                "year": p["year"] or "",
                "venue": p["venue"] or "",
                "article_type_family": article_type_family,
                "article_type_predicted_family": family_meta["predicted_family"],
                "article_type_confidence": family_meta["confidence"],
                "article_type_runner_up": family_meta["runner_up"],
                "article_type_margin": family_meta["margin"],
                "article_type_needs_review": family_meta["needs_review"],
                "article_type_signals": family_meta["signals"],
                "article_type_diagnostics": family_meta["diagnostics"],
                "article_type_classifier_version": family_meta["classifier_version"],
                "node_type": infer_node_type_for_family(article_type_family, snippet),
                "statement": snippet,
                "ae_confidence": round(confidence_for_effect(effect, sample_n), 2),
                "environment_variable": env_var,
                "outcome_variable": out_var,
                "environment_candidates": env_candidates,
                "outcome_candidates": out_candidates,
                "environment_canonical_id": env_resolution["canonical_id"],
                "outcome_canonical_id": out_resolution["canonical_id"],
                "environment_resolution_confidence": round(float(env_resolution["confidence"]), 4),
                "outcome_resolution_confidence": round(float(out_resolution["confidence"]), 4),
                "environment_resolution_match_type": env_resolution["match_type"],
                "outcome_resolution_match_type": out_resolution["match_type"],
                "environment_node_id": env_node_id,
                "outcome_node_id": out_node_id,
                "effect_direction": effect,
                "sample_n": sample_n,
                "abstract_snippet": snippet,
                "pdf_available": "yes" if has_pdf else "no",
                "evidence_level": "abstract_only_reduced_table",
                "provenance_tier": "abstract_provisional",
                "requires_pdf_confirmation": True,
                "abstract_rule_eligible": bool(rule_gate["eligible"]),
                "abstract_rule_policy": rule_gate["policy"],
                "abstract_rule_deferred_reason": rule_gate["reason"],
                "template_version": "unknown_with_reason:abstract_only_intake",
                "argument_scheme": "causal_argument",
                "causal_level": "association",
                "source_zone": "abstract",
                "extraction_difficulty": "easy",
                "event_ts": event_ts,
                "generated_at": now_iso,
            }
        )

        lhs_var = env_node_id
        rhs_var = out_node_id
        if rule_gate["eligible"]:
            rule_records.append(
                {
                    "schema": "ae.rule.v2",
                    "rule_id": f"{paper_id}#rt01",
                    "paper_id": paper_id,
                    "rule_type": "edge",
                    "article_type_family": article_type_family,
                    "article_type_predicted_family": family_meta["predicted_family"],
                    "article_type_confidence": family_meta["confidence"],
                    "article_type_runner_up": family_meta["runner_up"],
                    "article_type_margin": family_meta["margin"],
                    "article_type_needs_review": family_meta["needs_review"],
                    "article_type_signals": family_meta["signals"],
                    "article_type_diagnostics": family_meta["diagnostics"],
                    "article_type_classifier_version": family_meta["classifier_version"],
                    "node_type": infer_node_type_for_family(
                        article_type_family,
                        f"{env_var} -> {out_var}",
                    ),
                    "edge_type": "COHERENCE_SUPPORT",
                    "lhs": [{"var": lhs_var, "state": "present"}],
                    "rhs": [{"var": rhs_var, "state": "affected"}],
                    "polarity": polarity_for_effect(effect),
                    "strength": {"kind": "qualitative"},
                    "ae_confidence": round(confidence_for_effect(effect, sample_n), 2),
                    "causal_level": "association",
                    "applicability": {"population": [], "setting": [], "boundary_conditions": []},
                    "bn_mapping": {"node_suggestions": [lhs_var, rhs_var], "discretization_hint": "low/med/high"},
                    "evidence_level": "abstract_finding_rule",
                    "provenance_tier": "abstract_provisional",
                    "requires_pdf_confirmation": True,
                    "evidence_basis": "implicit_connection",
                    "needs_verification": True,
                    "status": "provisional",
                    "generated_at": now_iso,
                }
            )
        else:
            rule_records.append(
                {
                    "schema": "ae.rule.v2",
                    "rule_id": f"{paper_id}#rt01:deferred",
                    "paper_id": paper_id,
                    "rule_type": "deferred_edge",
                    "article_type_family": article_type_family,
                    "article_type_predicted_family": family_meta["predicted_family"],
                    "article_type_confidence": family_meta["confidence"],
                    "article_type_runner_up": family_meta["runner_up"],
                    "article_type_margin": family_meta["margin"],
                    "article_type_needs_review": family_meta["needs_review"],
                    "article_type_signals": family_meta["signals"],
                    "article_type_diagnostics": family_meta["diagnostics"],
                    "article_type_classifier_version": family_meta["classifier_version"],
                    "node_type": infer_node_type_for_family(
                        article_type_family,
                        f"{env_var} -> {out_var}",
                    ),
                    "edge_type": "COHERENCE_SUPPORT",
                    "bn_mapping": {"node_suggestions": [lhs_var, rhs_var], "discretization_hint": "low/med/high"},
                    "evidence_level": "abstract_deferred_rule",
                    "provenance_tier": "abstract_provisional",
                    "requires_pdf_confirmation": True,
                    "needs_verification": True,
                    "status": "deferred_article_type_review",
                    "deferred_reason": rule_gate["reason"],
                    "generated_at": now_iso,
                }
            )

        if has_pdf and paper_id not in existing_pdf_queue_ids:
            new_pdf_queue_rows.append(
                {
                    "paper_id": paper_id,
                    "doi": p["doi"] or "",
                    "title": p["title"] or "",
                    "year": p["year"] or "",
                    "venue": p["venue"] or "",
                    "pdf_path": p["pdf_path"] or "",
                    "status": "queued_pending_pdf_table_rule_completion",
                    "article_type_family": article_type_family,
                    "article_type_predicted_family": family_meta["predicted_family"],
                    "article_type_confidence": family_meta["confidence"],
                    "article_type_runner_up": family_meta["runner_up"],
                    "article_type_margin": family_meta["margin"],
                    "article_type_needs_review": family_meta["needs_review"],
                    "article_type_signals": family_meta["signals"],
                    "article_type_diagnostics": family_meta["diagnostics"],
                    "article_type_classifier_version": family_meta["classifier_version"],
                    "queued_at": now_iso,
                    "reason": "has_pdf_from_ingest",
                    "source": "run_realtime_table_rule_intake",
                }
            )
            existing_pdf_queue_ids.add(paper_id)

        last_ts = event_ts
        last_paper_id = paper_id

    if args.dry_run:
        deferred_rules = sum(1 for r in rule_records if r.get("rule_type") == "deferred_edge")
        print(f"Would process new papers: {len(papers)}")
        print(f"Would append table records: {len(table_records)}")
        print(f"Would append rule records: {len(rule_records)}")
        print(f"Would defer abstract causal edge rules: {deferred_rules}")
        print(f"Would enqueue PDF completion rows: {len(new_pdf_queue_rows)}")
        if papers:
            print(f"Next watermark: event_ts={last_ts}, paper_id={last_paper_id}")
        return 0

    append_jsonl(tables_path, table_records)
    append_jsonl(rules_path, rule_records)
    write_pdf_queue(pdf_queue_path, existing_queue_rows, new_pdf_queue_rows)

    web_integrated = 0
    bn_updated = 0
    bridges_integrated = 0
    if table_records and (args.integrate_web or args.update_bn):
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

        for rec in table_records:
            if not bool(rec.get("abstract_rule_eligible", False)):
                continue
            paper_id = rec["paper_id"]
            env_var = rec["environment_variable"]
            out_var = rec["outcome_variable"]
            env_node_id = rec.get("environment_node_id", f"env.{safe_var_name(env_var)}")
            out_node_id = rec.get("outcome_node_id", f"out.{safe_var_name(out_var)}")
            effect = rec["effect_direction"]
            sample_n = rec["sample_n"]
            cred_val = confidence_for_effect(effect, sample_n)

            belief = Belief(
                belief_id=f"rt:{paper_id}:abstract_rule",
                content=f"Abstract-provisional: {env_var} -> {out_var} ({effect})",
                level=EpistemicLevel.EMPIRICAL,
                status=BeliefStatus.TENTATIVE,
                credence=Credence(value=cred_val, uncertainty=0.45),
                paper_ids=[paper_id],
                domain="realtime_abstract",
                tags=[
                    "source:abstract",
                    "provenance:abstract_provisional",
                    "requires_pdf_confirmation:true",
                    f"effect_direction:{effect}",
                ],
                environment_id=env_node_id,
                outcome_id=out_node_id,
                source_depth=SourceDepth.ABSTRACT,
            )

            if args.integrate_web:
                bridge_registry = BridgeRegistry()
                web = create_neuroarchitecture_web()
                web.beliefs.clear()
                web.constraints.clear()
                web.add_belief(belief)
                rel_type, rel_strength, rel_prov = classify_abstract_relation(effect, rec.get("abstract_snippet", ""))

                peer_refs = fetch_peer_belief_ids(
                    DEFAULT_WEB_DB,
                    environment_id=env_node_id,
                    outcome_id=out_node_id,
                    exclude_belief_ids=[belief.belief_id],
                    limit=2,
                )
                for ref in peer_refs:
                    peer_id = ref["belief_id"]
                    c = Constraint(
                        constraint_id=make_constraint_id(
                            belief.belief_id,
                            peer_id,
                            rel_type,
                            f"cross_paper:abstract_shared_env_out|{rel_prov}",
                        ),
                        source_id=belief.belief_id,
                        target_id=peer_id,
                        constraint_type=ConstraintType(rel_type),
                        strength=rel_strength,
                        bidirectional=False,
                        evidence_ids=[paper_id],
                    )
                    c.warrant_type = "abstract_relation"  # type: ignore[attr-defined]
                    c.provenance = f"cross_paper:abstract_shared_env_out|{rel_prov}"  # type: ignore[attr-defined]
                    web.add_constraint(c)

                claim = {
                    "claim_id": f"rt:{paper_id}:abstract_rule",
                    "statement": belief.content,
                    "constructs": {
                        "outcomes": [{"id": out_node_id}],
                        "inputs": [{"id": env_node_id}],
                    },
                }
                bridge = detect_bridge_from_claim(claim, target_domain="architectural_perception")
                if bridge:
                    if belief.belief_id not in bridge.target_beliefs:
                        bridge.target_beliefs.append(belief.belief_id)
                    bridge_registry.add(bridge)

                accumulator.integrate_paper(web, paper_id=paper_id, bridge_registry=bridge_registry)
                bridges_integrated += len(bridge_registry.all())
                web_integrated += 1

            if args.update_bn and bn_builder is not None:
                bn_builder.observe_belief(belief, weight=float(args.bn_abstract_weight))
                bn_updated += 1

        if args.update_bn and bn_builder is not None:
            bn_builder.save_state(Path(args.bn_state_path))

    if papers:
        save_state(state_path, IntakeState(last_event_ts=last_ts, last_paper_id=last_paper_id))

    print(f"Processed new papers: {len(papers)}")
    print(f"Appended table records: {len(table_records)} -> {tables_path}")
    print(f"Appended rule records: {len(rule_records)} -> {rules_path}")
    print(f"Deferred abstract causal edge rules: {sum(1 for r in rule_records if r.get('rule_type') == 'deferred_edge')}")
    print(f"Enqueued PDF completion rows: {len(new_pdf_queue_rows)} -> {pdf_queue_path}")
    if args.integrate_web:
        print(f"Integrated provisional abstract beliefs into web: {web_integrated}")
        print(f"Bridge warrants integrated from abstracts: {bridges_integrated}")
    if args.update_bn:
        print(f"Updated incremental BN from provisional abstract beliefs: {bn_updated}")
    if papers:
        print(f"Updated watermark: event_ts={last_ts}, paper_id={last_paper_id}")
    else:
        print("No new papers found after current watermark.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
