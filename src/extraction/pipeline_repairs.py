#!/usr/bin/env python3
"""
PIPELINE REPAIRS
================

Drop-in replacement methods and new functions for pdf_extraction_module.py.

Contains:
1. _classify_paper_v2()       — Lightweight classification using intro + conclusion pages only
2. _normalize_extraction()    — Maps pooled_effects/themes/propositions → findings
3. _save_partial_extraction() — Saves salvageable extractions before requeue/fail
4. _repair_extraction()       — Targeted repair of partial extractions
5. _evaluate_quality_v2()     — Revised quality evaluation with partial credit
6. _extract_images_fixed()    — Bug fix for image extraction (scoping error)
7. process_one_v2()           — Revised main processing loop using all the above

INTEGRATION:
    These methods can replace their counterparts in ExtractionPipeline.
    The revised prompts are imported from revised_prompts_v2.py.
    Article types are now 15 sub-types in 5 families per article_type_contract.py.

Author: Opus (Architecture)
Date: 2026-02-24
Sprint: Pipeline Repair
"""

from __future__ import annotations

import json
import time
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Any

# These imports assume the original module's types are available
# When integrating, these come from the same file
# from pdf_extraction_module import (
#     ExtractionPipeline, ExtractionResult, QueueItem, QueueStatus,
#     ArticleType, QualityReport, FIELD_WEIGHTS
# )


# ---------------------------------------------------------------------------
# REVISED QUALITY THRESHOLDS
# ---------------------------------------------------------------------------
# Key change: lower thresholds + partial-credit scoring replaces binary pass/fail
# Papers that extract SOMETHING useful are never discarded

QUALITY_THRESHOLDS_V2 = {
    # ── EMPIRICAL FAMILY ──
    # empirical_v2, observational_field, case_study, mixed_methods
    "empirical": {
        "min_findings": 1,
        "require_statistics": 0.3,     # Reduced from 0.5 — many valid studies lack effect sizes
        "require_direction": 0.8,      # Reduced from 0.9
        "min_score_accept": 0.5,       # Accept if above this
        "min_score_repair": 0.2,       # Attempt repair if above this (was just requeue)
        "min_score_fail": 0.0,         # Below repair threshold → fail
    },
    # ── SYNTHESIS FAMILY ──
    # meta_analysis, systematic_review, narrative_review
    "synthesis_meta": {
        "min_findings": 1,
        "require_statistics": 0.6,     # Meta-analyses should have pooled stats
        "require_direction": 0.8,
        "min_score_accept": 0.5,
        "min_score_repair": 0.2,
        "min_score_fail": 0.0,
    },
    "synthesis_other": {
        "min_findings": 1,
        "require_statistics": 0.0,     # Sys reviews / narrative reviews often lack stats
        "require_direction": 0.5,
        "min_score_accept": 0.4,
        "min_score_repair": 0.15,
        "min_score_fail": 0.0,
    },
    # ── THEORETICAL FAMILY ──
    # theoretical, conceptual_framework, thought_piece
    "theoretical": {
        "min_findings": 0,
        "require_statistics": 0.0,
        "require_direction": 0.2,
        "min_score_accept": 0.25,
        "min_score_repair": 0.1,
        "min_score_fail": 0.0,
    },
    # ── QUALITATIVE FAMILY ──
    # interview_study, ethnographic, grounded_theory, phenomenological
    "qualitative": {
        "min_findings": 1,
        "require_statistics": 0.0,
        "require_direction": 0.3,
        "min_score_accept": 0.3,
        "min_score_repair": 0.1,
        "min_score_fail": 0.0,
    },
    # ── METHODS (treated as empirical family in contract) ──
    "methods": {
        "min_findings": 0,
        "require_statistics": 0.0,
        "require_direction": 0.0,
        "min_score_accept": 0.2,
        "min_score_repair": 0.05,
        "min_score_fail": 0.0,
    },
    "default": {
        "min_findings": 0,
        "require_statistics": 0.0,
        "require_direction": 0.3,
        "min_score_accept": 0.3,
        "min_score_repair": 0.1,
        "min_score_fail": 0.0,
    },
}

# Maps all 15 sub-types + legacy names to quality threshold keys
_SUBTYPE_TO_THRESHOLD = {
    "empirical_v2": "empirical",
    "observational_field": "empirical",
    "case_study": "empirical",
    "mixed_methods": "empirical",
    "empirical": "empirical",
    "meta_analysis": "synthesis_meta",
    "systematic_review": "synthesis_other",
    "narrative_review": "synthesis_other",
    "theoretical": "theoretical",
    "conceptual_framework": "theoretical",
    "thought_piece": "theoretical",
    "interview_study": "qualitative",
    "ethnographic": "qualitative",
    "grounded_theory": "qualitative",
    "phenomenological": "qualitative",
    "qualitative": "qualitative",
    "methods": "methods",
    "unknown": "default",
}

def _get_threshold(article_type_val: str) -> dict:
    """Map any article sub-type to its quality threshold dict."""
    key = _SUBTYPE_TO_THRESHOLD.get(article_type_val.lower().strip(), "default")
    return QUALITY_THRESHOLDS_V2.get(key, QUALITY_THRESHOLDS_V2["default"])


# ---------------------------------------------------------------------------
# REVISED FIELD WEIGHTS
# ---------------------------------------------------------------------------
# Added template_ids; reduced penalty for missing statistics

FIELD_WEIGHTS_V2 = {
    # CRITICAL — extraction fails without these
    "antecedent": 0.15,
    "consequent": 0.15,
    "direction": 0.12,

    # HIGH — needed for BN edge weights
    "p_value": 0.08,            # Reduced from 0.10 — many valid papers lack exact p
    "effect_size": 0.07,        # Reduced from 0.10
    "sample_size": 0.04,

    # MEDIUM — for theory linking
    "theory_links": 0.10,
    "template_ids": 0.05,       # NEW — template matching
    "mechanism": 0.05,

    # SUPPORTING
    "quote": 0.08,
    "source": 0.06,
    "test_statistic": 0.05,     # NEW — captures F-stats, t-stats, etc.
}


# ---------------------------------------------------------------------------
# 1. REVISED CLASSIFICATION — uses intro + conclusion pages only
# ---------------------------------------------------------------------------

def classify_paper_v2(self, item) -> tuple:
    """
    Classify article type using only first 3 + last 2 pages.

    Returns:
        (ArticleType, confidence: float, signals: list[str])

    Saves ~60% of classification API cost vs uploading full PDF.
    """
    from google.genai import types
    from google.genai.errors import APIError

    # Import the lightweight classification prompt
    from src.extraction.revised_prompts_v2 import CLASSIFICATION_PROMPT

    try:
        import fitz
    except ImportError:
        # Fall back to full PDF classification if PyMuPDF not available
        return self._classify_paper(item), 0.5, ["fallback: PyMuPDF not available"]

    pdf_path = Path(item.pdf_path)
    if not pdf_path.exists():
        return ArticleType.UNKNOWN, 0.0, ["PDF not found"]

    # Extract intro (first 3 pages) + conclusion (last 2 pages)
    try:
        with fitz.open(str(pdf_path)) as doc:
            n_pages = doc.page_count
            if n_pages <= 5:
                # Short paper — just use whole thing
                pages_to_keep = list(range(n_pages))
            else:
                # First 3 + last 2 pages
                pages_to_keep = [0, 1, 2, n_pages - 2, n_pages - 1]

            # Create a temporary PDF with just those pages
            subset_doc = fitz.open()
            for pg in pages_to_keep:
                subset_doc.insert_pdf(doc, from_page=pg, to_page=pg)

            subset_bytes = subset_doc.tobytes()
            subset_doc.close()

    except Exception as e:
        item.last_error = f"Classification page extraction: {str(e)[:100]}"
        return ArticleType.UNKNOWN, 0.0, [f"fitz error: {str(e)[:50]}"]

    # Send subset to Gemini
    try:
        from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

        @retry(
            retry=retry_if_exception_type((APIError, Exception)),
            wait=wait_exponential(multiplier=1, min=4, max=60),
            stop=stop_after_attempt(3),
        )
        def _call_gemini_classify_v2():
            import io
            uploaded = self.client.files.upload(
                file=io.BytesIO(subset_bytes),
                config={"mime_type": "application/pdf"},
            )
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=[uploaded, CLASSIFICATION_PROMPT],
                    config=types.GenerateContentConfig(
                        temperature=0.0,
                        max_output_tokens=500,
                    ),
                )
                return response.text
            finally:
                try:
                    self.client.files.delete(name=uploaded.name)
                except Exception as e:
                    import logging; logging.getLogger(__name__).debug(f"Non-critical: {e}")

        text = _call_gemini_classify_v2()

        if not text:
            return ArticleType.UNKNOWN, 0.0, ["empty API response"]

        # Parse JSON response
        text = text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])

        data = json.loads(text)

        article_type_str = data.get("article_type", "unknown").lower().strip()
        confidence = float(data.get("confidence", 0.5))
        signals = data.get("signals", [])

        # Map to ArticleType enum — handle all 15 sub-types
        # Falls back gracefully: sub-types map to their parent enum values
        type_map = {
            # Empirical family
            "empirical": ArticleType.EMPIRICAL,
            "empirical_v2": ArticleType.EMPIRICAL,
            "observational_field": ArticleType.EMPIRICAL,
            "case_study": ArticleType.EMPIRICAL,
            "mixed_methods": ArticleType.EMPIRICAL,
            # Synthesis family
            "meta_analysis": ArticleType.META_ANALYSIS,
            "systematic_review": ArticleType.SYSTEMATIC_REVIEW,
            "narrative_review": ArticleType.NARRATIVE_REVIEW,
            # Theoretical family
            "theoretical": ArticleType.THEORETICAL,
            "conceptual_framework": ArticleType.THEORETICAL,
            "thought_piece": ArticleType.THEORETICAL,
            # Qualitative family
            "qualitative": ArticleType.QUALITATIVE,
            "interview_study": ArticleType.QUALITATIVE,
            "ethnographic": ArticleType.QUALITATIVE,
            "grounded_theory": ArticleType.QUALITATIVE,
            "phenomenological": ArticleType.QUALITATIVE,
            # Methods
            "methods": ArticleType.METHODS,
        }

        article_type = type_map.get(article_type_str, ArticleType.UNKNOWN)

        # Store classification metadata on the item
        item.classification_confidence = confidence
        # Store the fine-grained sub-type (e.g., "observational_field")
        # even though ArticleType enum collapses it to EMPIRICAL
        item.article_type_sub = article_type_str
        item.article_family = data.get("article_family", "unknown")

        return article_type, confidence, signals

    except json.JSONDecodeError as e:
        return ArticleType.UNKNOWN, 0.0, [f"JSON parse error: {str(e)[:50]}"]
    except Exception as e:
        item.last_error = f"Classification v2: {str(e)[:100]}"
        return ArticleType.UNKNOWN, 0.0, [f"API error: {str(e)[:50]}"]


# ---------------------------------------------------------------------------
# 2. NORMALIZE EXTRACTION — maps variant keys to canonical "findings"
# ---------------------------------------------------------------------------

def normalize_extraction(data: dict) -> dict:
    """
    Ensure all article types use 'findings' as the canonical key.

    Maps:
        pooled_effects → findings  (meta-analysis)
        themes         → findings  (qualitative)
        propositions   → findings  (theoretical)
        key_claims     → findings  (unknown)

    Also normalizes each finding to have all expected fields with null defaults.
    """
    # Map variant keys to 'findings'
    variant_keys = ["pooled_effects", "themes", "propositions", "key_claims",
                    "synthesis_conclusions_array", "themes_or_constructs_findings"]
    if "findings" not in data or not data["findings"]:
        for key in variant_keys:
            if key in data and data[key]:
                data["findings"] = data[key]
                # Keep original key too for provenance
                break

    # Ensure findings exists
    if "findings" not in data:
        data["findings"] = []

    # Normalize each finding to have expected fields
    canonical_fields = {
        "id": None,
        "antecedent": None,
        "consequent": None,
        "direction": None,
        "claim_type": None,
        "measure_type": None,
        "p_value": None,
        "effect_size": None,
        "effect_size_type": None,
        "sample_size": None,
        "confidence_interval": None,
        "test_statistic": None,
        "theory_links": [],
        "template_ids": [],
        "mechanism": None,
        "moderators_reported": [],
        "provenance_depth": None,
        "source": None,
        "quote": None,
    }

    normalized_findings = []
    for i, finding in enumerate(data["findings"]):
        if not isinstance(finding, dict):
            continue
        normalized = {**canonical_fields, **finding}
        if normalized["id"] is None:
            normalized["id"] = i + 1
        normalized_findings.append(normalized)

    data["findings"] = normalized_findings

    # --- Also normalize qualitative themes that were mapped to findings ---
    # If they have 'theme_name' but no 'antecedent', use theme_name as antecedent
    for f in data["findings"]:
        if f.get("theme_name") and not f.get("antecedent"):
            f["antecedent"] = f["theme_name"]
        if f.get("description") and not f.get("consequent"):
            f["consequent"] = f["description"]
        # Map 'evidence_strength' or 'evidence_basis' to claim_type if missing
        if not f.get("claim_type"):
            if f.get("evidence_strength"):
                f["claim_type"] = f"synthesized ({f['evidence_strength']})"
            elif f.get("evidence_basis"):
                f["claim_type"] = f["evidence_basis"]
            elif f.get("evidence_type"):
                f["claim_type"] = f["evidence_type"]

    return data


# ---------------------------------------------------------------------------
# 3. SAVE PARTIAL EXTRACTION
# ---------------------------------------------------------------------------

def save_partial_extraction(self, item, extraction_data: dict) -> Path:
    """
    Save a partial extraction to the partial_extractions directory.

    Called when quality score is above repair threshold but below accept threshold.
    These can be repaired later by targeted follow-up prompts.

    Returns path to saved partial file.
    """
    partials_dir = self.output_dir / "partial_extractions"
    partials_dir.mkdir(exist_ok=True)

    doi_safe = item.doi.replace("/", "_")
    partial_file = partials_dir / f"{doi_safe}.json"

    # Annotate each finding with what's missing
    findings = extraction_data.get("findings", [])
    repair_manifest = []

    for i, f in enumerate(findings):
        missing = []
        if not f.get("antecedent"):
            missing.append("antecedent")
        if not f.get("consequent"):
            missing.append("consequent")
        if not f.get("direction"):
            missing.append("direction")
        if not f.get("p_value") and not f.get("effect_size"):
            missing.append("statistics")
        if not f.get("theory_links"):
            missing.append("theory_links")
        if not f.get("quote"):
            missing.append("quote")

        if missing:
            repair_manifest.append({
                "finding_id": f.get("id", i + 1),
                "missing_fields": missing,
                "source_hint": f.get("source"),  # Where to look in the paper
                "has_antecedent_consequent": bool(f.get("antecedent") and f.get("consequent")),
            })

    partial_record = {
        "doi": item.doi,
        "article_type": item.article_type.value if item.article_type else "unknown",
        "saved_at": datetime.now(timezone.utc).isoformat(),
        "attempt": item.attempts,
        "extraction_data": extraction_data,
        "repair_manifest": repair_manifest,
        "n_findings": len(findings),
        "n_findings_need_repair": len(repair_manifest),
        "quality_score": item.quality_report.get("overall_score") if item.quality_report else None,
    }

    with open(partial_file, "w") as f:
        json.dump(partial_record, f, indent=2)

    return partial_file


# ---------------------------------------------------------------------------
# 4. REPAIR EXTRACTION — targeted follow-up for missing fields
# ---------------------------------------------------------------------------

REPAIR_STATISTICS_PROMPT = """You are repairing a partial extraction from a scientific paper.

I have already extracted findings from this paper, but some findings are MISSING STATISTICS (p-values, effect sizes, sample sizes, test statistics).

Here are the findings that need repair:

{findings_to_repair}

For EACH finding listed above:
1. Search the paper for the relevant statistics. Check TABLES first, then text, then figure captions.
2. The "source_hint" tells you approximately where to look.
3. Return ONLY the repaired statistics — do not change the antecedent, consequent, or direction.

Return this JSON:
{{
  "repairs": [
    {{
      "finding_id": 1,
      "p_value": "exact value or threshold or null if truly not reported",
      "effect_size": number or null,
      "effect_size_type": "Cohen_d|r|eta_squared|partial_eta_squared|beta|R_squared|OR|null",
      "confidence_interval": [lower, upper] or null,
      "test_statistic": "e.g., F(2,45)=3.21 or t(98)=2.45 or null",
      "sample_size": number or null,
      "found_in": "Table 3 row 5 | text p.12 para 3 | Figure 4 caption | NOT FOUND"
    }}
  ]
}}

If a statistic is truly not reported anywhere in the paper, use null and found_in: "NOT FOUND".
Do NOT invent values.
"""

REPAIR_SPECIFICITY_PROMPT = """You are repairing a partial extraction from a scientific paper.

I have already extracted findings, but some have VAGUE antecedents or consequents that need to be made more specific.

Here are the findings that need specificity repair:

{findings_to_repair}

For EACH finding, make the antecedent and consequent MORE SPECIFIC based on what the paper actually reports.

Example: "spatial configuration" → "open-plan office (>6 workstations) vs. cellular office (private rooms)"
Example: "creativity" → "Remote Associates Test (RAT) score"
Example: "stress" → "salivary cortisol (nmol/L) 30 min post-exposure"

Return this JSON:
{{
  "repairs": [
    {{
      "finding_id": 1,
      "antecedent_revised": "more specific antecedent or null if already specific enough",
      "consequent_revised": "more specific consequent or null if already specific enough",
      "measure_type": "physiological|behavioral|self_report|cognitive|performance|neural|observational|null"
    }}
  ]
}}
"""


def repair_extraction(self, item, partial_data: dict) -> dict:
    """
    Attempt targeted repair of a partial extraction.

    Strategy:
    1. For findings missing statistics → send focused statistics prompt with full PDF
    2. For findings with vague antecedent/consequent → send specificity prompt
    3. Merge repairs back into the extraction

    Returns the repaired extraction data dict.
    """
    from google.genai import types
    from google.genai.errors import APIError

    findings = partial_data.get("findings", [])
    manifest = partial_data.get("repair_manifest", [])

    if not manifest:
        return partial_data.get("extraction_data", partial_data)

    extraction_data = partial_data.get("extraction_data", partial_data)
    repaired_data = json.loads(json.dumps(extraction_data))  # Deep copy

    # --- Repair 1: Missing statistics ---
    stats_repairs_needed = [
        m for m in manifest
        if "statistics" in m.get("missing_fields", [])
        and m.get("has_antecedent_consequent")
    ]

    if stats_repairs_needed:
        # Build the findings list for the prompt
        findings_for_prompt = []
        for m in stats_repairs_needed[:10]:  # Cap at 10 to control token usage
            fid = m["finding_id"]
            finding = next((f for f in findings if f.get("id") == fid), None)
            if finding:
                findings_for_prompt.append({
                    "finding_id": fid,
                    "antecedent": finding.get("antecedent"),
                    "consequent": finding.get("consequent"),
                    "direction": finding.get("direction"),
                    "source_hint": finding.get("source", "unknown"),
                })

        if findings_for_prompt:
            prompt = REPAIR_STATISTICS_PROMPT.format(
                findings_to_repair=json.dumps(findings_for_prompt, indent=2)
            )

            try:
                repairs = self._call_repair_prompt(item, prompt)
                if repairs and "repairs" in repairs:
                    # Merge statistics repairs
                    for repair in repairs["repairs"]:
                        fid = repair.get("finding_id")
                        target = next(
                            (f for f in repaired_data.get("findings", []) if f.get("id") == fid),
                            None
                        )
                        if target:
                            for field in ["p_value", "effect_size", "effect_size_type",
                                          "confidence_interval", "test_statistic", "sample_size"]:
                                if repair.get(field) is not None:
                                    target[field] = repair[field]

            except Exception as e:
                # Repair failed — continue with what we have
                item.error_history.append(f"Stats repair failed: {str(e)[:80]}")

    # --- Repair 2: Vague antecedent/consequent ---
    specificity_repairs_needed = [
        m for m in manifest
        if ("antecedent" in m.get("missing_fields", []) or
            "consequent" in m.get("missing_fields", []))
    ]

    # Also check for suspiciously short/vague descriptions
    for f in findings:
        ant = f.get("antecedent", "") or ""
        con = f.get("consequent", "") or ""
        if (len(ant.split()) <= 2 and ant) or (len(con.split()) <= 2 and con):
            fid = f.get("id")
            if not any(m["finding_id"] == fid for m in specificity_repairs_needed):
                specificity_repairs_needed.append({
                    "finding_id": fid,
                    "missing_fields": ["specificity"],
                    "has_antecedent_consequent": True,
                })

    if specificity_repairs_needed:
        findings_for_prompt = []
        for m in specificity_repairs_needed[:10]:
            fid = m["finding_id"]
            finding = next((f for f in findings if f.get("id") == fid), None)
            if finding:
                findings_for_prompt.append({
                    "finding_id": fid,
                    "antecedent": finding.get("antecedent"),
                    "consequent": finding.get("consequent"),
                    "source_hint": finding.get("source", "unknown"),
                })

        if findings_for_prompt:
            prompt = REPAIR_SPECIFICITY_PROMPT.format(
                findings_to_repair=json.dumps(findings_for_prompt, indent=2)
            )

            try:
                repairs = self._call_repair_prompt(item, prompt)
                if repairs and "repairs" in repairs:
                    for repair in repairs["repairs"]:
                        fid = repair.get("finding_id")
                        target = next(
                            (f for f in repaired_data.get("findings", []) if f.get("id") == fid),
                            None
                        )
                        if target:
                            if repair.get("antecedent_revised"):
                                target["antecedent"] = repair["antecedent_revised"]
                            if repair.get("consequent_revised"):
                                target["consequent"] = repair["consequent_revised"]
                            if repair.get("measure_type"):
                                target["measure_type"] = repair["measure_type"]

            except Exception as e:
                item.error_history.append(f"Specificity repair failed: {str(e)[:80]}")

    return repaired_data


def _call_repair_prompt(self, item, prompt: str) -> Optional[dict]:
    """
    Send a repair prompt to Gemini with the full PDF.
    Returns parsed JSON or None.
    """
    from google.genai import types

    try:
        with open(item.pdf_path, "rb") as f:
            uploaded = self.client.files.upload(
                file=f, config={"mime_type": "application/pdf"}
            )

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=[uploaded, prompt],
                config=types.GenerateContentConfig(
                    temperature=0.0,
                    max_output_tokens=4096,
                ),
            )

            text = response.text
            if not text:
                return None

            text = text.strip()
            if text.startswith("```"):
                lines = text.split("\n")
                text = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])

            return json.loads(text)

        finally:
            try:
                self.client.files.delete(name=uploaded.name)
            except Exception as e:
                import logging; logging.getLogger(__name__).debug(f"Non-critical: {e}")

    except Exception as e:
        return None


# ---------------------------------------------------------------------------
# 5. REVISED QUALITY EVALUATION — partial credit scoring
# ---------------------------------------------------------------------------

def evaluate_quality_v2(self, result) -> dict:
    """
    Evaluate extraction quality with partial credit and repair routing.

    Returns a QualityReport-compatible dict with additional fields:
        - action: "accept" | "repair" | "requeue" | "fail"
        - repair_candidates: list of finding IDs that could be repaired
        - confidence_tier: "high" | "medium" | "low" | "minimal"
    """
    findings = result.findings if hasattr(result, 'findings') else result.get("findings", [])
    n = len(findings) if findings else 0

    article_type_val = (
        result.article_type.value
        if hasattr(result, 'article_type') and hasattr(result.article_type, 'value')
        else str(result.get("article_type", "default"))
    )

    thresholds = _get_threshold(article_type_val)

    if n == 0:
        # No findings at all
        if article_type_val in ("theoretical", "methods"):
            # These article types might legitimately have no extractable findings
            # Check if we got other useful data
            has_concepts = bool(result.concepts if hasattr(result, 'concepts') else
                              result.get("concepts") or result.get("components"))
            if has_concepts:
                return {
                    "doi": result.doi if hasattr(result, 'doi') else result.get("doi"),
                    "passed": True,
                    "overall_score": 0.3,
                    "has_antecedent_consequent": 0.0,
                    "has_direction": 0.0,
                    "has_statistics": 0.0,
                    "has_theory_links": 0.0,
                    "has_quotes": 0.0,
                    "issues": ["No findings but has concepts/components"],
                    "action": "accept",
                    "confidence_tier": "low",
                    "repair_candidates": [],
                }

        return {
            "doi": result.doi if hasattr(result, 'doi') else result.get("doi"),
            "passed": False,
            "overall_score": 0.0,
            "has_antecedent_consequent": 0.0,
            "has_direction": 0.0,
            "has_statistics": 0.0,
            "has_theory_links": 0.0,
            "has_quotes": 0.0,
            "issues": ["No findings extracted"],
            "action": "requeue",
            "confidence_tier": "minimal",
            "repair_candidates": [],
        }

    # Calculate field coverage
    has_ac = sum(1 for f in findings if f.get("antecedent") and f.get("consequent")) / n
    has_dir = sum(1 for f in findings if f.get("direction")) / n
    has_stats = sum(1 for f in findings if f.get("p_value") or f.get("effect_size")) / n
    has_theory = sum(1 for f in findings if f.get("theory_links")) / n
    has_quote = sum(1 for f in findings if f.get("quote")) / n
    has_template = sum(1 for f in findings if f.get("template_ids")) / n
    has_source = sum(1 for f in findings if f.get("source")) / n
    has_test_stat = sum(1 for f in findings if f.get("test_statistic")) / n

    # Calculate weighted score
    w = FIELD_WEIGHTS_V2
    score = (
        w["antecedent"] * has_ac +
        w["consequent"] * has_ac +
        w["direction"] * has_dir +
        w["p_value"] * has_stats +
        w["effect_size"] * has_stats +
        w["sample_size"] * (sum(1 for f in findings if f.get("sample_size")) / n) +
        w["theory_links"] * has_theory +
        w["template_ids"] * has_template +
        w["mechanism"] * (sum(1 for f in findings if f.get("mechanism")) / n) +
        w["quote"] * has_quote +
        w["source"] * has_source +
        w["test_statistic"] * has_test_stat
    )

    max_score = sum(w.values())
    score = score / max_score

    # Identify repair candidates
    repair_candidates = []
    for f in findings:
        needs_repair = False
        if f.get("antecedent") and f.get("consequent"):
            # Has core structure — check what's missing
            if not f.get("p_value") and not f.get("effect_size"):
                needs_repair = True
            if not f.get("theory_links"):
                needs_repair = True
        if needs_repair:
            repair_candidates.append(f.get("id"))

    # Check issues
    issues = []
    if has_ac < 0.7:
        issues.append(f"Low antecedent/consequent coverage: {has_ac:.0%}")
    if has_dir < thresholds["require_direction"]:
        issues.append(f"Low direction coverage: {has_dir:.0%}")
    if has_stats < thresholds["require_statistics"]:
        issues.append(f"Low statistics coverage: {has_stats:.0%}")

    # Determine action with 4-tier routing
    if score >= thresholds["min_score_accept"] and len(issues) <= 1:
        action = "accept"
        confidence_tier = "high" if score >= 0.7 else "medium"
    elif score >= thresholds["min_score_repair"] and repair_candidates:
        action = "repair"
        confidence_tier = "low"
    elif score >= thresholds["min_score_repair"]:
        action = "requeue"
        confidence_tier = "low"
    else:
        action = "fail"
        confidence_tier = "minimal"

    doi = result.doi if hasattr(result, 'doi') else result.get("doi")

    return {
        "doi": doi,
        "passed": action == "accept",
        "overall_score": round(score, 3),
        "has_antecedent_consequent": round(has_ac, 3),
        "has_direction": round(has_dir, 3),
        "has_statistics": round(has_stats, 3),
        "has_theory_links": round(has_theory, 3),
        "has_quotes": round(has_quote, 3),
        "has_template_ids": round(has_template, 3),
        "n_findings": n,
        "issues": issues,
        "action": action,
        "confidence_tier": confidence_tier,
        "repair_candidates": repair_candidates,
    }


# ---------------------------------------------------------------------------
# 6. FIXED IMAGE EXTRACTION — scoping bug corrected
# ---------------------------------------------------------------------------

def extract_images_fixed(self, item, min_size: int = 8000) -> list:
    """
    Extract images from PDF using PyMuPDF.

    BUG FIX: Original had image_list = page.get_images() OUTSIDE the for loop,
    so it only processed images from the last page. Now processes all pages.
    """
    try:
        import fitz
    except ImportError:
        return []

    pdf_path = Path(item.pdf_path)
    if not pdf_path.exists():
        return []

    doi_safe = pdf_path.stem
    extracted = []

    try:
        with fitz.open(str(pdf_path)) as doc:
            for page_num in range(len(doc)):
                page = doc[page_num]
                image_list = page.get_images(full=True)  # FIX: now inside the loop

                for img_index, img in enumerate(image_list):
                    xref = img[0]
                    try:
                        base_image = doc.extract_image(xref)
                        image_bytes = base_image["image"]

                        if len(image_bytes) < min_size:
                            continue

                        img_filename = (
                            f"{doi_safe}_p{page_num + 1:02d}"
                            f"_img{img_index + 1:02d}.{base_image['ext']}"
                        )
                        img_path = self.images_dir / img_filename

                        with open(img_path, "wb") as f:
                            f.write(image_bytes)

                        extracted.append({
                            "page": page_num + 1,
                            "filename": img_filename,
                            "size_bytes": len(image_bytes),
                            "width": base_image.get("width"),
                            "height": base_image.get("height"),
                        })
                    except Exception as e:
                        import logging; logging.getLogger(__name__).debug(f"Non-critical: {e}")

    except Exception as e:
        import logging; logging.getLogger(__name__).debug(f"Non-critical: {e}")

    return extracted


# ---------------------------------------------------------------------------
# 7. REVISED process_one — integrates all repairs
# ---------------------------------------------------------------------------

def process_one_v2(self, item, extract_images: bool = True) -> Any:
    """
    Process a single paper through the revised pipeline.

    Changes from original:
    1. Uses classify_paper_v2 (intro+conclusion pages only)
    2. Normalizes extraction output (pooled_effects → findings etc.)
    3. Uses evaluate_quality_v2 with 4-tier routing
    4. Saves partial extractions for papers that score above repair threshold
    5. Attempts targeted repair before requeuing
    6. Uses fixed image extraction
    """
    # These imports are from the original module
    from src.extraction.pdf_extraction_module import (
        QueueStatus, QueueItem, ExtractionResult, ArticleType
    )

    item.attempts += 1
    item.updated_at = datetime.now(timezone.utc).isoformat()

    # PRE-FLIGHT CHECK
    try:
        import fitz
        with fitz.open(item.pdf_path) as doc:
            if doc.page_count == 0:
                item.last_error = "PDF has 0 pages or is corrupted"
                item.status = QueueStatus.FAILED
                self._save_queue()
                return item
    except ImportError:
        pass
    except Exception as e:
        item.last_error = f"PDF corruption check failed: {str(e)}"
        item.status = QueueStatus.FAILED
        self._save_queue()
        return item

    try:
        # ── Step 1: Classify (using intro + conclusion pages) ──
        item.status = QueueStatus.CLASSIFYING
        self._save_queue()

        article_type, confidence, signals = classify_paper_v2(self, item)
        item.article_type = article_type
        item.classification_confidence = confidence

        # Determine sub-type string for prompt selection
        # article_type_sub was set in classify_paper_v2; fall back to enum value
        sub_type = getattr(item, 'article_type_sub', article_type.value)
        family = getattr(item, 'article_family', 'unknown')

        # Log classification
        print(f"    Classified as: {sub_type} (family={family}, conf={confidence:.2f})")

        # ── Step 2: Extract ──
        item.status = QueueStatus.EXTRACTING
        self._save_queue()

        result = self._extract_paper(item)

        # ── Step 2b: Normalize extraction ──
        # Convert ExtractionResult to dict for normalization
        result_dict = asdict(result) if hasattr(result, '__dataclass_fields__') else result
        result_dict = normalize_extraction(result_dict)
        # Ensure article_type reflects the fine-grained sub-type for quality eval
        result_dict["article_type"] = sub_type
        result_dict["article_family"] = family

        item.extraction_result = result_dict
        item.total_cost += result.extraction_cost if hasattr(result, 'extraction_cost') else 0

        # ── Step 2c: Extract images (fixed version) ──
        if extract_images:
            images = extract_images_fixed(self, item)
            item.extraction_result["extracted_images"] = images

        # ── Step 3: Evaluate quality (v2 with partial credit) ──
        item.status = QueueStatus.EVALUATING
        self._save_queue()

        quality = evaluate_quality_v2(self, result_dict)
        item.quality_report = quality

        # ── Step 4: Route based on quality ──
        action = quality["action"]

        if action == "accept":
            item.status = QueueStatus.ACCEPTED
            item.completed_at = datetime.now(timezone.utc).isoformat()

            # Save result
            result_file = self.results_dir / f"{item.doi.replace('/', '_')}.json"
            with open(result_file, "w") as f:
                json.dump(item.extraction_result, f, indent=2)

            print(f"    ✓ ACCEPTED (score={quality['overall_score']:.3f}, "
                  f"n_findings={quality['n_findings']}, "
                  f"tier={quality['confidence_tier']})")

        elif action == "repair":
            # Save partial extraction first
            partial_file = save_partial_extraction(self, item, item.extraction_result)
            print(f"    ⚒ REPAIR needed (score={quality['overall_score']:.3f}, "
                  f"{len(quality['repair_candidates'])} findings to repair)")

            # Attempt repair
            partial_data = json.loads(open(partial_file).read())
            repaired = repair_extraction(self, item, partial_data)

            # Re-evaluate after repair
            quality_post = evaluate_quality_v2(self, repaired)
            item.extraction_result = repaired
            item.quality_report = quality_post

            if quality_post["action"] == "accept":
                item.status = QueueStatus.ACCEPTED
                item.completed_at = datetime.now(timezone.utc).isoformat()

                result_file = self.results_dir / f"{item.doi.replace('/', '_')}.json"
                with open(result_file, "w") as f:
                    json.dump(item.extraction_result, f, indent=2)

                print(f"    ✓ REPAIRED → ACCEPTED (score={quality_post['overall_score']:.3f})")
            elif item.attempts < item.max_retries:
                item.status = QueueStatus.REQUEUED
                item.error_history.append(
                    f"Attempt {item.attempts}: repair insufficient "
                    f"(score {quality_post['overall_score']:.3f})"
                )
                print(f"    ↻ REPAIRED but still insufficient → REQUEUED")
            else:
                # Accept with low confidence rather than fail
                # The partial data is still valuable
                item.status = QueueStatus.ACCEPTED
                item.completed_at = datetime.now(timezone.utc).isoformat()
                item.quality_report["confidence_tier"] = "minimal"

                result_file = self.results_dir / f"{item.doi.replace('/', '_')}.json"
                with open(result_file, "w") as f:
                    json.dump(item.extraction_result, f, indent=2)

                print(f"    ⚠ MAX RETRIES → ACCEPTED with LOW confidence "
                      f"(score={quality_post['overall_score']:.3f})")

        elif action == "requeue" and item.attempts < item.max_retries:
            # Save partial anyway
            save_partial_extraction(self, item, item.extraction_result)
            item.status = QueueStatus.REQUEUED
            item.error_history.append(
                f"Attempt {item.attempts}: {quality['issues']}"
            )
            print(f"    ↻ REQUEUED (score={quality['overall_score']:.3f})")

        else:
            # Failed — but still save partial if anything was extracted
            if quality.get("n_findings", 0) > 0:
                save_partial_extraction(self, item, item.extraction_result)
            item.status = QueueStatus.FAILED
            item.completed_at = datetime.now(timezone.utc).isoformat()
            print(f"    ✗ FAILED (score={quality['overall_score']:.3f})")

    except Exception as e:
        item.error_history.append(f"Attempt {item.attempts}: {str(e)[:100]}")

        if item.attempts < item.max_retries:
            item.status = QueueStatus.REQUEUED
            print(f"    ↻ ERROR → REQUEUED ({str(e)[:60]})")
        else:
            item.status = QueueStatus.FAILED
            item.completed_at = datetime.now(timezone.utc).isoformat()
            print(f"    ✗ ERROR → FAILED ({str(e)[:60]})")

    self._save_queue()
    return item


# ---------------------------------------------------------------------------
# INTEGRATION HELPER
# ---------------------------------------------------------------------------

def patch_pipeline(pipeline_instance):
    """
    Monkey-patch an existing ExtractionPipeline instance with the v2 methods.

    Usage:
        from src.extraction.pipeline_repairs import patch_pipeline
        from src.extraction.pdf_extraction_module import ExtractionPipeline

        pipeline = ExtractionPipeline(pdf_dir=..., output_dir=...)
        patch_pipeline(pipeline)

        # Now pipeline.process_one() uses the v2 logic
        pipeline.process_batch(batch_size=50)
    """
    import types as builtin_types

    # Replace the PROMPT_MAP import target
    import src.extraction.revised_prompts_v2 as ep_v2
    import scripts.gemini_extraction_queue as geq
    geq.PROMPT_MAP = ep_v2.PROMPT_MAP

    # Bind v2 methods to the instance
    pipeline_instance.process_one = builtin_types.MethodType(process_one_v2, pipeline_instance)
    pipeline_instance._extract_images = builtin_types.MethodType(extract_images_fixed, pipeline_instance)
    pipeline_instance._call_repair_prompt = builtin_types.MethodType(_call_repair_prompt, pipeline_instance)

    # Create partials directory
    partials_dir = pipeline_instance.output_dir / "partial_extractions"
    partials_dir.mkdir(exist_ok=True)

    print(f"Pipeline patched with v2 methods (repair, classification, quality)")
    print(f"Partial extractions will be saved to: {partials_dir}")

    return pipeline_instance
