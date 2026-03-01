#!/usr/bin/env python3
"""
CMR PDF Extraction Test — Gemini API with Native PDF Vision
============================================================
Tests whether Gemini's native PDF processing produces better structured
extraction than text-based approaches for academic papers.

Usage:
    export GEMINI_API_KEY='your-key-here'
    python3 test_gemini_pdf_extraction.py path/to/paper.pdf

    # Or test with a specific model:
    python3 test_gemini_pdf_extraction.py path/to/paper.pdf --model gemini-2.5-pro-preview-05-06

    # Quick mode (just findings, no mechanism chain):
    python3 test_gemini_pdf_extraction.py path/to/paper.pdf --quick

Output:
    Writes JSON to ./extraction_output/{filename}_extracted.json
    Writes a human-readable summary to stdout

Requirements:
    pip install google-genai pydantic
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# ---------------------------------------------------------------------------
# Check dependencies before anything else
# ---------------------------------------------------------------------------
try:
    from google import genai
    from google.genai import types
except ImportError:
    print("ERROR: google-genai not installed.")
    print("Run:  pip install google-genai")
    sys.exit(1)

try:
    from pydantic import BaseModel, Field
    from typing import Optional
except ImportError:
    print("ERROR: pydantic not installed.")
    print("Run:  pip install pydantic")
    sys.exit(1)


# ===========================================================================
# CMR EXTRACTION SCHEMA
# ===========================================================================
# This defines what we want Gemini to extract from each paper.
# It mirrors the canonical template structure from schemas/template_canonical.json
# but is scoped to what a SINGLE PAPER can provide (not the full panel-calibrated
# template, which requires cross-paper synthesis).

class EmpiricalFinding(BaseModel):
    """One empirical finding reported in the paper."""
    finding: str = Field(description="Plain-language statement of what was found")
    paradigm: str = Field(description="Experimental paradigm or method used")
    effect_size: Optional[str] = Field(
        default=None,
        description="Effect size if reported (e.g., 'd = 0.45', 'r = 0.38', 'R² = 0.35', 'η² = 0.12'). Include the statistic type."
    )
    sample_size: Optional[int] = Field(
        default=None,
        description="N (number of participants/observations). Integer only."
    )
    design: Optional[str] = Field(
        default=None,
        description="Study design (e.g., 'within-subjects', 'between-subjects', 'meta-analysis', 'cross-sectional survey', 'fMRI within-subjects')"
    )
    population: Optional[str] = Field(
        default=None,
        description="Population studied (e.g., 'university undergraduates', 'office workers in Denmark', 'adults aged 18-65')"
    )
    confidence_interval: Optional[str] = Field(
        default=None,
        description="95% CI if reported (e.g., '[0.32, 0.58]')"
    )
    p_value: Optional[str] = Field(
        default=None,
        description="p-value if reported (e.g., 'p < .001', 'p = .03')"
    )


class MechanismStep(BaseModel):
    """One step in a proposed causal mechanism chain."""
    step_number: int = Field(description="Sequential step number (1, 2, 3...)")
    from_variable: str = Field(description="The input/cause variable for this step")
    to_variable: str = Field(description="The output/effect variable for this step")
    description: str = Field(description="Description of the causal process connecting from → to")
    evidence_strength: Optional[str] = Field(
        default=None,
        description="How well-supported is this step? One of: strong_direct_evidence, moderate_evidence, indirect_or_analogical, theoretical_only"
    )


class ArchitecturalImplication(BaseModel):
    """A specific implication for architectural/built environment design."""
    design_parameter: str = Field(description="The architectural variable (e.g., 'ceiling height', 'window-to-wall ratio', 'ambient temperature setpoint')")
    direction: str = Field(description="How the parameter should be set (e.g., 'higher ceilings promote divergent thinking', 'natural ventilation improves thermal satisfaction')")
    effect_magnitude: Optional[str] = Field(
        default=None,
        description="Quantified effect if available (e.g., '2-4°C higher setpoint acceptable in naturally ventilated buildings')"
    )
    evidence_basis: Optional[str] = Field(
        default=None,
        description="What evidence supports this implication (e.g., 'field study of 21,000 observations', 'laboratory experiment N=60')"
    )


class PaperExtraction(BaseModel):
    """Complete structured extraction from a single academic paper."""

    # --- Bibliographic ---
    title: str = Field(description="Full title of the paper")
    authors: list[str] = Field(description="List of author names (last, first initial format preferred)")
    year: Optional[int] = Field(default=None, description="Publication year")
    journal: Optional[str] = Field(default=None, description="Journal name")
    doi: Optional[str] = Field(default=None, description="DOI if present in the paper")

    # --- Classification ---
    primary_domain: str = Field(
        description="Primary research domain. One of: thermal_comfort, visual_perception, "
        "auditory_acoustics, spatial_cognition, lighting, stress_physiology, social_space, "
        "memory_place, multisensory, neuromodulation, circadian, creativity, emotion, "
        "biophilia, prospect_refuge, other"
    )
    t1_frameworks: list[str] = Field(
        description="Which CMR Tier 1 frameworks does this paper provide evidence for? "
        "Choose from: PP (Predictive Processing), SN (Salience Network), DP (Default/Place), "
        "DT (Dual-Task/Cognitive Load), NM (Neuromodulation), IC (Interoception), "
        "MS (Multisensory Integration), EC (Embodied Cognition), CB (Circadian Biology), "
        "MSI (Motor-Sensory Integration). List all that apply."
    )

    # --- Content ---
    abstract_summary: str = Field(description="2-3 sentence summary of the paper's main contribution")
    empirical_findings: list[EmpiricalFinding] = Field(
        description="All quantitative empirical findings reported in the paper. "
        "Include effect sizes, sample sizes, and statistical details wherever reported. "
        "Extract EVERY finding with a reported effect size or statistical test."
    )
    mechanism_chain: Optional[list[MechanismStep]] = Field(
        default=None,
        description="If the paper proposes a causal mechanism, extract the step-by-step chain. "
        "Each step should specify from_variable → to_variable with the connecting process."
    )
    architectural_implications: Optional[list[ArchitecturalImplication]] = Field(
        default=None,
        description="If the paper discusses implications for built environment design, "
        "extract each specific implication with its evidence basis."
    )

    # --- Quality indicators ---
    study_type: str = Field(
        description="Primary study type. One of: empirical_experiment, field_study, "
        "meta_analysis, systematic_review, theoretical, computational_model, case_study"
    )
    is_meta_analysis: bool = Field(description="True if this is a meta-analysis or systematic review")
    total_sample_size: Optional[int] = Field(
        default=None,
        description="Total N across all studies/experiments reported (or total N for meta-analyses)"
    )
    limitations_noted: Optional[list[str]] = Field(
        default=None,
        description="Key limitations acknowledged by the authors"
    )

    # --- Relevance ---
    cmr_relevance_score: int = Field(
        description="How relevant is this paper to the CMR system (built environment + neuroscience)? "
        "1 = tangentially relevant, 2 = moderately relevant (provides background theory), "
        "3 = directly relevant (empirical findings applicable to architectural parameters), "
        "4 = highly relevant (provides mechanism chain with effect sizes for built environment variables), "
        "5 = essential (directly calibrates a CMR template parameter)"
    )
    relevant_templates: Optional[list[str]] = Field(
        default=None,
        description="If you can identify which CMR templates this paper is relevant to, list them. "
        "Use template IDs like IC_THERMAL_COMFORT_001, THERMAL_ADAPTIVE_PE_001, "
        "PP_SPECTRAL_MATCH_001, etc. Leave null if uncertain."
    )


class QuickExtraction(BaseModel):
    """Abbreviated extraction — just the key findings."""
    title: str
    authors: list[str]
    year: Optional[int] = None
    journal: Optional[str] = None
    primary_domain: str
    t1_frameworks: list[str]
    abstract_summary: str
    empirical_findings: list[EmpiricalFinding]
    study_type: str
    is_meta_analysis: bool
    total_sample_size: Optional[int] = None
    cmr_relevance_score: int


# ===========================================================================
# EXTRACTION PROMPT
# ===========================================================================

SYSTEM_INSTRUCTION = """You are a research extraction specialist for the CMR
(Compositional Mechanistic Reasoning) system — a computational framework that
evaluates how cognitive neuroscience findings translate to architectural design
implications.

Your task is to read academic papers and extract structured data with maximum
precision. The extracted data will be used to calibrate computational models
linking neuroscience mechanisms to built environment parameters.

CRITICAL RULES:
1. Extract ONLY what is explicitly stated in the paper. Never infer or fabricate
   effect sizes, sample sizes, or statistical results.
2. If a value is not reported, use null — never guess.
3. For effect sizes, always include the statistic type (d, r, R², η², etc.).
4. For mechanism chains, each step must have a clear from → to relationship
   with a described process connecting them.
5. Be conservative with the cmr_relevance_score — most basic neuroscience papers
   without architectural implications score 1-2.
6. Extract ALL empirical findings with reported statistics, not just the main one.
   A paper with 5 experiments should yield at least 5 findings.
"""

EXTRACTION_PROMPT = """Extract all structured information from this academic paper
according to the schema provided. Be thorough — extract every empirical finding
with a reported effect size or statistical test. Pay special attention to:

- Tables of results (these often contain the most precise effect sizes)
- Supplementary analyses mentioned in the text
- Interaction effects and moderators
- Sample characteristics and study design details

If the paper reports multiple experiments or studies, extract findings from ALL of them."""

QUICK_PROMPT = """Extract the key bibliographic information and empirical findings
from this academic paper. Focus on findings with reported effect sizes and
statistical tests. Be thorough with the findings — extract every result with
a reported statistic."""


# ===========================================================================
# MAIN EXTRACTION FUNCTION
# ===========================================================================

def extract_paper(
    pdf_path: str,
    model_id: str = "gemini-2.0-flash",
    quick: bool = False,
    verbose: bool = True
) -> dict:
    """
    Extract structured CMR data from a PDF using Gemini's native PDF vision.

    Args:
        pdf_path: Path to the PDF file
        model_id: Gemini model to use
        quick: If True, use abbreviated schema (faster, cheaper)
        verbose: If True, print progress to stdout

    Returns:
        dict: Extracted data matching PaperExtraction or QuickExtraction schema
    """

    # --- Validate API key ---
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY environment variable not set.\n"
            "Run: export GEMINI_API_KEY='your-key-here'"
        )

    # --- Read PDF ---
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    file_size_mb = pdf_path.stat().st_size / (1024 * 1024)
    if file_size_mb > 50:
        raise ValueError(f"PDF is {file_size_mb:.1f} MB — Gemini limit is 50 MB. Split or compress first.")

    if verbose:
        print(f"Reading: {pdf_path.name} ({file_size_mb:.1f} MB)")

    with open(pdf_path, "rb") as f:
        pdf_data = f.read()

    # --- Choose schema and prompt ---
    if quick:
        schema = QuickExtraction
        prompt = QUICK_PROMPT
    else:
        schema = PaperExtraction
        prompt = EXTRACTION_PROMPT

    # --- Build the Gemini client ---
    client = genai.Client(api_key=api_key)

    if verbose:
        print(f"Model:  {model_id}")
        print(f"Schema: {'QuickExtraction' if quick else 'PaperExtraction'}")
        print(f"Sending to Gemini API (native PDF vision)...")

    # --- Call the API ---
    # The PDF is sent as raw bytes — Gemini renders each page visually.
    # This is the key difference from text-extraction approaches.
    response = client.models.generate_content(
        model=model_id,
        contents=[
            types.Part.from_bytes(data=pdf_data, mime_type="application/pdf"),
            prompt,
        ],
        config=genai.types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=0.0,  # deterministic extraction
            response_mime_type="application/json",
            response_schema=schema,
        ),
    )

    # --- Parse response ---
    if verbose:
        print(f"Response received. Parsing...")

    try:
        result = json.loads(response.text)
    except json.JSONDecodeError as e:
        print(f"WARNING: JSON parse failed, attempting cleanup. Error: {e}")
        # Sometimes the response has markdown fencing
        import re
        cleaned = re.sub(r"```(?:json)?\n?", "", response.text).strip()
        result = json.loads(cleaned)

    # --- Add metadata ---
    result["_extraction_metadata"] = {
        "source_file": pdf_path.name,
        "model": model_id,
        "schema": "QuickExtraction" if quick else "PaperExtraction",
        "extracted_at": datetime.now().isoformat(),
        "provenance": "extraction_derived",  # NOT panel_calibrated
        "file_size_mb": round(file_size_mb, 2),
    }

    if verbose:
        _print_summary(result, quick)

    return result


def _print_summary(result: dict, quick: bool):
    """Print a human-readable summary of the extraction."""
    print("\n" + "=" * 70)
    print(f"TITLE: {result.get('title', 'Unknown')}")
    print(f"AUTHORS: {', '.join(result.get('authors', []))}")
    print(f"YEAR: {result.get('year', '?')}  |  JOURNAL: {result.get('journal', '?')}")
    print(f"DOMAIN: {result.get('primary_domain', '?')}")
    print(f"T1 FRAMEWORKS: {', '.join(result.get('t1_frameworks', []))}")
    print(f"CMR RELEVANCE: {result.get('cmr_relevance_score', '?')}/5")
    print(f"STUDY TYPE: {result.get('study_type', '?')}")
    print(f"TOTAL N: {result.get('total_sample_size', '?')}")
    print("-" * 70)

    findings = result.get("empirical_findings", [])
    print(f"\nEMPIRICAL FINDINGS EXTRACTED: {len(findings)}")
    for i, f in enumerate(findings, 1):
        effect = f.get("effect_size", "not reported")
        n = f.get("sample_size", "?")
        p = f.get("p_value", "")
        print(f"\n  [{i}] {f.get('finding', '')[:120]}")
        print(f"      Effect: {effect}  |  N: {n}  |  {p}")
        print(f"      Design: {f.get('design', '?')}  |  Paradigm: {f.get('paradigm', '?')[:80]}")

    if not quick:
        chain = result.get("mechanism_chain") or []
        if chain:
            print(f"\nMECHANISM CHAIN: {len(chain)} steps")
            for step in chain:
                print(f"  Step {step.get('step_number', '?')}: "
                      f"{step.get('from_variable', '?')} → {step.get('to_variable', '?')}")
                print(f"    {step.get('description', '')[:100]}")

        implications = result.get("architectural_implications") or []
        if implications:
            print(f"\nARCHITECTURAL IMPLICATIONS: {len(implications)}")
            for imp in implications:
                print(f"  • {imp.get('design_parameter', '?')}: {imp.get('direction', '?')[:80]}")

        templates = result.get("relevant_templates") or []
        if templates:
            print(f"\nRELEVANT CMR TEMPLATES: {', '.join(templates)}")

    print("\n" + "=" * 70)


# ===========================================================================
# CLI ENTRY POINT
# ===========================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Extract structured CMR data from a PDF using Gemini native PDF vision"
    )
    parser.add_argument("pdf", help="Path to the PDF file")
    parser.add_argument(
        "--model", default="gemini-2.0-flash",
        help="Gemini model (default: gemini-2.0-flash; try gemini-2.5-pro-preview-05-06 for higher quality)"
    )
    parser.add_argument(
        "--quick", action="store_true",
        help="Use abbreviated schema (faster, cheaper, fewer fields)"
    )
    parser.add_argument(
        "--output-dir", default="./extraction_output",
        help="Output directory for JSON files (default: ./extraction_output)"
    )

    args = parser.parse_args()

    # --- Run extraction ---
    result = extract_paper(args.pdf, model_id=args.model, quick=args.quick)

    # --- Save output ---
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    stem = Path(args.pdf).stem
    output_path = output_dir / f"{stem}_extracted.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"\nSaved to: {output_path}")


if __name__ == "__main__":
    main()
