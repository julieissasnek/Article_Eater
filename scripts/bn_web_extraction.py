#!/usr/bin/env python3
"""
BN/Web-Optimized Extraction Pipeline

Design based on what the Bayesian Network and Web of Belief actually need:

FIELD IMPORTANCE (for BN edge weights and Web coherence):

CRITICAL (extraction fails without these):
  - antecedent: environmental feature (IV)
  - consequent: human response (DV)
  - direction: increase/decrease/no_effect
  - theory_links: which T1 frameworks predict this

HIGH (needed for edge weight calculation):
  - p_value: statistical significance
  - effect_size + type: Cohen_d, r, eta_squared, beta, OR
  - sample_size: N
  - claim_type: mechanistic/causal/associational/moderated/null

MEDIUM (for credence/uncertainty):
  - mechanism: theoretical explanation
  - study_design: experiment/survey/field_study
  - measure_type: physiological/behavioral/self_report/cognitive/performance
  - domains: A1-A10 classification

LOW (supplementary):
  - quote: source attribution
  - limitations: stated caveats
  - confidence_interval: if available

RETRY LOGIC:
- If CRITICAL fields missing after first pass, retry with focused prompt
- If HIGH fields missing, retry asking specifically for statistics
"""

import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from google import genai
from google.genai import types
from scripts.gemini_extraction_queue import PRICING

# Paths
AF_ROOT = Path("/Users/davidusa/REPOS/Article_Finder_v3_2_3")
PDF_DIR = AF_ROOT / "data" / "pdfs"
OUTPUT_DIR = PROJECT_ROOT / "data" / "extractions"
MODEL = "gemini-2.5-flash"

# T1 Frameworks (from CLAUDE.md)
T1_FRAMEWORKS = """
T1 THEORETICAL FRAMEWORKS (identify which predict findings):
1. PP - Predictive Processing (prediction error, precision, active inference)
2. SN - Spatial Navigation / Cognitive Mapping (place cells, grid cells, hippocampus)
3. DP - Dual-Process Evaluation (System 1/2, fluency, aesthetic response)
4. DT - DMN/TPN Dynamics (default mode, task-positive, mind-wandering)
5. NM - Neuromodulatory Systems (dopamine, cortisol, serotonin, oxytocin)
6. IC - Interoceptive / Constructionist Affect (Barrett, body-budget, allostasis)
7. MS - Memory Systems (episodic, semantic, procedural, working memory)
8. EC - Embodied Cognition (enactivism, affordances, motor simulation)
9. CB - Chronobiological Regulation (circadian, ultradian, melatonin, light)
10. MSI - Multisensory Integration (binding, crossmodal, spatial attention)

Also consider domain theories:
- ART - Attention Restoration Theory (Kaplan)
- SRT - Stress Recovery Theory (Ulrich)
- Biophilia (Wilson, Kellert)
- Prospect-Refuge (Appleton)
- Privacy Regulation (Altman)
"""

# CNFA Domains
DOMAINS = """
CNFA DOMAINS (classify the environmental features):
- A1_Materials: wood, concrete, stone, texture, surface, biophilic materials
- A2_Spatial_Scale: ceiling height, volume, proportion, spaciousness
- A3_Spatial_Config: layout, wayfinding, circulation, space syntax
- A4_Light: daylight, illuminance, circadian, glare, window views
- A5_Acoustic: noise, reverberation, soundscape, speech privacy
- A6_Visual_Form: color, pattern, fractal, curvature, aesthetic
- A7_Haptic_Thermal: temperature, comfort, touch, HVAC
- A8_Social: privacy, collaboration, density, personal space
- A9_Task_Cognition: attention, memory, creativity, performance
- A10_Temporal: exposure duration, adaptation, circadian timing
"""

EMPIRICAL_PROMPT = f"""You are extracting structured findings for a Bayesian Network of architectural effects on humans.

{T1_FRAMEWORKS}

{DOMAINS}

Extract ALL statistical findings from this empirical paper.

Return ONLY valid JSON (no markdown):
{{
  "article_type": "empirical",
  "title": "paper title",
  "n_participants": number,
  "study_design": "experiment|survey|field_study|observational|mixed",
  "findings": [
    {{
      "id": 1,
      "antecedent": "environmental feature (be specific, e.g., 'ceiling height > 3m' not just 'ceiling height')",
      "consequent": "human response (be specific, e.g., 'creative ideation scores' not just 'creativity')",
      "direction": "increase|decrease|no_effect",
      "claim_type": "causal|associational|moderated|null",

      "p_value": "exact (e.g., 0.003) or threshold (e.g., <0.05)",
      "effect_size": number or null,
      "effect_size_type": "Cohen_d|r|eta_squared|beta|OR|RR|null",
      "sample_size": number,
      "confidence_interval": [lower, upper] or null,

      "measure_type": "physiological|behavioral|self_report|cognitive|performance",
      "mechanism": "theoretical explanation if mentioned",
      "theory_links": ["PP", "SN", "DP", "DT", "NM", "IC", "MS", "EC", "CB", "MSI", "ART", "SRT", "Biophilia"],

      "source": "Table X / Figure Y / text p.N",
      "quote": "exact supporting quote (max 100 chars)"
    }}
  ],
  "domains": ["A1_Materials", "A4_Light", etc.],
  "overall_theory_links": ["frameworks that guide this paper's hypotheses"]
}}

CRITICAL RULES:
1. Extract EVERY finding including null results (direction="no_effect", claim_type="null")
2. p_value and effect_size are CRITICAL - search tables, figures, and text carefully
3. theory_links MUST be populated - which frameworks predict this effect?
4. For regression: predictors = antecedent, criterion = consequent
5. For correlation matrices: each significant cell is a separate finding
6. For ANOVA: each significant main effect and interaction is a finding
7. Be specific with antecedent/consequent - include levels, thresholds, operationalizations
"""

# Focused retry prompts for missing fields
STATISTICS_RETRY_PROMPT = """The previous extraction is missing statistical details.

Look SPECIFICALLY for:
1. p-values: search Results section, tables, figure captions
2. Effect sizes: Cohen's d, r, eta-squared, beta, odds ratios
3. Sample sizes for each analysis
4. Confidence intervals
5. Test statistics: F, t, chi-square values

Return updated findings with these fields filled:
{
  "findings": [
    {
      "id": [same as before],
      "p_value": "exact value or threshold",
      "effect_size": number,
      "effect_size_type": "type",
      "sample_size": number,
      "test_statistic": "F(df1,df2)=X.XX or t(df)=X.XX"
    }
  ]
}
"""

THEORY_RETRY_PROMPT = f"""The previous extraction is missing theory links.

{T1_FRAMEWORKS}

For each finding, identify which theoretical frameworks would predict this effect:
- Does this relate to attention/restoration? → ART
- Does this involve stress/physiology? → SRT, NM, IC
- Does this involve spatial cognition? → SN, EC
- Does this involve aesthetic response? → DP
- Does this involve circadian/light? → CB
- Does this involve prediction/expectation? → PP

Return theory assignments:
{{
  "findings": [
    {{
      "id": [same as before],
      "theory_links": ["framework codes"],
      "theory_rationale": "brief explanation of why these frameworks apply"
    }}
  ]
}}
"""


def get_client():
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Set GOOGLE_API_KEY or GEMINI_API_KEY")
    return genai.Client(api_key=api_key)


def classify_article_type(client: genai.Client, pdf_path: Path) -> str:
    """Classify article type with simple one-word response."""
    prompt = """Classify this paper. Return ONE word only:
empirical
meta_analysis
systematic_review
narrative_review
theoretical
qualitative
methods"""

    try:
        with open(pdf_path, "rb") as f:
            uploaded = client.files.upload(file=f, config={"mime_type": "application/pdf"})

        response = client.models.generate_content(
            model=MODEL,
            contents=[uploaded, prompt],
            config=types.GenerateContentConfig(temperature=0.0, max_output_tokens=50),
        )

        client.files.delete(name=uploaded.name)

        text = response.text.strip().lower()
        valid_types = ["empirical", "meta_analysis", "systematic_review",
                       "narrative_review", "theoretical", "qualitative", "methods"]

        for t in valid_types:
            if t in text:
                return t

        # Handle variations
        if "meta" in text: return "meta_analysis"
        if "systematic" in text: return "systematic_review"
        if "narrative" in text or "review" in text: return "narrative_review"

        return "empirical"  # Default for unknown

    except Exception as e:
        return "empirical"  # Safe default


def extract_findings(client: genai.Client, pdf_path: Path, article_type: str) -> dict:
    """Extract findings with the appropriate prompt."""

    # Select prompt based on article type
    if article_type == "empirical":
        prompt = EMPIRICAL_PROMPT
    else:
        # For now, use empirical prompt for all types
        # TODO: Add meta_analysis, systematic_review prompts
        prompt = EMPIRICAL_PROMPT

    try:
        with open(pdf_path, "rb") as f:
            uploaded = client.files.upload(file=f, config={"mime_type": "application/pdf"})

        response = client.models.generate_content(
            model=MODEL,
            contents=[uploaded, prompt],
            config=types.GenerateContentConfig(temperature=0.1, max_output_tokens=65536),
        )

        text = response.text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])

        result = json.loads(text)

        # Calculate cost
        cost = 0.0
        if response.usage_metadata:
            m = response.usage_metadata
            pricing = PRICING.get(MODEL, PRICING["gemini-2.5-flash"])
            cost = (m.prompt_token_count * pricing["input"] +
                   m.candidates_token_count * pricing["output"]) / 1_000_000

        # Keep file for potential retry
        return {"success": True, "data": result, "cost": cost, "uploaded": uploaded}

    except json.JSONDecodeError as e:
        return {"success": False, "error": f"JSON parse: {str(e)[:50]}"}
    except Exception as e:
        return {"success": False, "error": f"{type(e).__name__}: {str(e)[:80]}"}


def check_field_quality(findings: list) -> dict:
    """Check which critical/high fields are missing."""
    missing = {
        "critical": [],  # antecedent, consequent, direction, theory_links
        "high": [],      # p_value, effect_size, sample_size, claim_type
    }

    for f in findings:
        fid = f.get("id", "?")

        # Critical fields
        if not f.get("antecedent"): missing["critical"].append(f"F{fid}:antecedent")
        if not f.get("consequent"): missing["critical"].append(f"F{fid}:consequent")
        if not f.get("direction"): missing["critical"].append(f"F{fid}:direction")
        if not f.get("theory_links"): missing["critical"].append(f"F{fid}:theory_links")

        # High priority fields
        if not f.get("p_value"): missing["high"].append(f"F{fid}:p_value")
        if not f.get("effect_size"): missing["high"].append(f"F{fid}:effect_size")
        if not f.get("sample_size"): missing["high"].append(f"F{fid}:sample_size")

    return missing


def retry_for_statistics(client: genai.Client, uploaded, original_data: dict) -> dict:
    """Retry extraction focusing on missing statistics."""
    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=[uploaded, STATISTICS_RETRY_PROMPT],
            config=types.GenerateContentConfig(temperature=0.0, max_output_tokens=16000),
        )

        text = response.text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])

        stats_data = json.loads(text)

        # Merge statistics into original findings
        stats_by_id = {f["id"]: f for f in stats_data.get("findings", [])}

        for finding in original_data.get("findings", []):
            fid = finding.get("id")
            if fid in stats_by_id:
                stats = stats_by_id[fid]
                # Only update if new value is non-null
                for field in ["p_value", "effect_size", "effect_size_type", "sample_size", "test_statistic"]:
                    if stats.get(field) and not finding.get(field):
                        finding[field] = stats[field]

        return {"success": True, "data": original_data}

    except Exception as e:
        return {"success": False, "error": str(e)[:80]}


def retry_for_theory(client: genai.Client, uploaded, original_data: dict) -> dict:
    """Retry extraction focusing on missing theory links."""
    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=[uploaded, THEORY_RETRY_PROMPT],
            config=types.GenerateContentConfig(temperature=0.0, max_output_tokens=8000),
        )

        text = response.text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])

        theory_data = json.loads(text)

        # Merge theory links into original findings
        theory_by_id = {f["id"]: f for f in theory_data.get("findings", [])}

        for finding in original_data.get("findings", []):
            fid = finding.get("id")
            if fid in theory_by_id:
                theory = theory_by_id[fid]
                if theory.get("theory_links") and not finding.get("theory_links"):
                    finding["theory_links"] = theory["theory_links"]
                if theory.get("theory_rationale"):
                    finding["theory_rationale"] = theory["theory_rationale"]

        return {"success": True, "data": original_data}

    except Exception as e:
        return {"success": False, "error": str(e)[:80]}


def process_paper(doi: str, client: genai.Client = None) -> dict:
    """Process a single paper with quality checks and retries."""
    if client is None:
        client = get_client()

    pdf_path = PDF_DIR / (doi.replace("/", "_") + ".pdf")

    if not pdf_path.exists():
        return {"doi": doi, "status": "failed", "error": "PDF not found"}

    total_cost = 0.0

    # Step 1: Classify article type
    article_type = classify_article_type(client, pdf_path)

    # Step 2: Extract findings
    result = extract_findings(client, pdf_path, article_type)

    if not result["success"]:
        return {"doi": doi, "status": "failed", "error": result["error"], "article_type": article_type}

    data = result["data"]
    total_cost += result.get("cost", 0)
    uploaded = result.get("uploaded")

    # Step 3: Check field quality
    findings = data.get("findings", [])
    missing = check_field_quality(findings)

    # Step 4: Retry for missing high-priority fields (statistics)
    if missing["high"] and uploaded:
        stats_result = retry_for_statistics(client, uploaded, data)
        if stats_result["success"]:
            data = stats_result["data"]

    # Step 5: Retry for missing critical fields (theory links)
    if missing["critical"] and uploaded:
        # Only retry if theory_links are missing
        theory_missing = [m for m in missing["critical"] if "theory_links" in m]
        if theory_missing:
            theory_result = retry_for_theory(client, uploaded, data)
            if theory_result["success"]:
                data = theory_result["data"]

    # Cleanup uploaded file
    if uploaded:
        try:
            client.files.delete(name=uploaded.name)
        except:
            pass

    # Final quality assessment
    final_findings = data.get("findings", [])
    final_missing = check_field_quality(final_findings)

    quality_score = 1.0
    if final_missing["critical"]:
        quality_score -= 0.3 * len(final_missing["critical"]) / max(len(final_findings), 1)
    if final_missing["high"]:
        quality_score -= 0.1 * len(final_missing["high"]) / max(len(final_findings), 1)
    quality_score = max(0, quality_score)

    return {
        "doi": doi,
        "status": "completed",
        "article_type": article_type,
        "n_findings": len(final_findings),
        "quality_score": round(quality_score, 2),
        "missing_fields": final_missing,
        "final_result": data,
        "cost": round(total_cost, 6)
    }


def main():
    import argparse

    parser = argparse.ArgumentParser(description="BN/Web-optimized extraction")
    parser.add_argument("--test", type=str, help="Test single DOI")
    parser.add_argument("--test-batch", type=int, default=0, help="Test N papers")
    parser.add_argument("--run", action="store_true", help="Run full extraction")
    args = parser.parse_args()

    if args.test:
        client = get_client()
        result = process_paper(args.test, client)
        print(json.dumps(result, indent=2, default=str))

    elif args.test_batch > 0:
        # Get unknown papers
        extraction_files = sorted(OUTPUT_DIR.glob("full_extraction_*.json"))
        if extraction_files:
            with open(extraction_files[-1]) as f:
                data = json.load(f)
            dois = [r["doi"] for r in data.get("results", [])
                    if r.get("article_type") == "unknown"][:args.test_batch]
        else:
            print("No extraction file found")
            return

        print(f"Testing {len(dois)} papers...")
        client = get_client()

        for doi in dois:
            print(f"\n{'='*60}")
            print(f"Processing: {doi}")
            result = process_paper(doi, client)
            print(f"Type: {result.get('article_type')}")
            print(f"Findings: {result.get('n_findings', 0)}")
            print(f"Quality: {result.get('quality_score', 0)}")
            print(f"Missing: {result.get('missing_fields', {})}")
            time.sleep(1)

    elif args.run:
        print("Full extraction mode - implement with batching...")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
