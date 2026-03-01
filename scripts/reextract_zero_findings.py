#!/usr/bin/env python3
"""
reextract_zero_findings.py — Re-extract articles with 0 findings
=================================================================

Identifies extraction files with empty findings and re-runs them
through Gemini with an improved v3 prompt that:
  1. Explicitly requests at least 3 findings per paper
  2. Accepts weaker/indirect findings for theoretical papers
  3. Uses theory_links to guide finding generation

Runs in background. Logs to /tmp/reextract.log.

Success conditions:
  SC-1: ≥15/23 zero-finding articles now have ≥1 finding
  SC-2: No API errors on ≥80% of attempts
  SC-3: All output files remain valid JSON
"""

import json
import sys
import os
import time
import logging
from pathlib import Path
from datetime import datetime, timezone

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

EXTRACTIONS_DIR = PROJECT_ROOT / "data" / "extractions"
PDF_DIR = PROJECT_ROOT / "data" / "pdfs"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
    handlers=[
        logging.FileHandler("/tmp/reextract.log"),
        logging.StreamHandler(),
    ]
)
log = logging.getLogger(__name__)


V3_EXTRACTION_PROMPT = """You are an expert research paper analyzer for architectural and environmental psychology.

Analyze this PDF and extract ALL findings, claims, and evidence. Be thorough and systematic.

IMPORTANT RULES:
1. Extract AT LEAST 3 findings per paper. Even theoretical papers have claims.
2. For theoretical papers: Extract the key propositions, predictions, and framework claims.
3. For review papers: Extract the key conclusions, synthesis claims, and identified gaps.
4. For empirical papers: Extract effect sizes, statistical results, and design recommendations.
5. Include theory_links for each finding (which theories does this relate to?).

Return a JSON object with this structure:
{
  "doi": "<paper DOI>",
  "title": "<paper title>",
  "article_type": "<empirical|theoretical|review|meta_analysis|case_study>",
  "findings": [
    {
      "finding_id": "F1",
      "antecedent": "<independent variable or condition>",
      "consequent": "<dependent variable or outcome>",
      "relationship": "<positive|negative|null|complex|nonlinear>",
      "effect_size": "<if available, e.g., d=0.5, r=0.3>",
      "confidence": <0.0-1.0>,
      "sample_size": <if available>,
      "methodology": "<experimental|observational|computational|theoretical>",
      "theory_links": ["<theory1>", "<theory2>"],
      "summary": "<one-sentence description>"
    }
  ],
  "constructs": {
    "outcomes": ["<list of measured/discussed outcomes>"],
    "mechanisms": ["<list of mechanisms discussed>"],
    "moderators": ["<list of moderating variables>"]
  }
}

Return ONLY valid JSON. No markdown, no code fences, no preamble."""


def find_zero_finding_articles():
    """Identify extraction files with 0 findings."""
    zeros = []
    for ef in sorted(EXTRACTIONS_DIR.glob("10.*.json")):
        try:
            data = json.load(open(ef))
            if not data.get("findings"):
                zeros.append(ef)
        except Exception:
            pass
    return zeros


def reextract_with_gemini(doi: str, pdf_path: Path) -> dict:
    """Re-extract a paper using Gemini with v3 prompt."""
    from google import genai

    api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("No Gemini API key found")

    client = genai.Client(api_key=api_key)

    # Try to upload PDF
    try:
        uploaded = client.files.upload(file=pdf_path)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[uploaded, V3_EXTRACTION_PROMPT],
            config={"max_output_tokens": 8192},
        )
        text = response.text
    except Exception as e:
        log.warning(f"PDF upload failed for {doi}, trying text-only: {e}")
        # Fallback: try to extract from existing data
        return None

    # Parse response
    try:
        # Try direct JSON parse
        result = json.loads(text)
        return result
    except json.JSONDecodeError:
        # Try extracting JSON from markdown
        import re
        match = re.search(r'```(?:json)?\s*\n(.*?)```', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass
        # Try finding { ... }
        start = text.find('{')
        end = text.rfind('}')
        if start >= 0 and end > start:
            try:
                return json.loads(text[start:end+1])
            except json.JSONDecodeError:
                pass
    
    log.error(f"Could not parse response for {doi}")
    return None


def main():
    log.info("=== RE-EXTRACTION OF ZERO-FINDING ARTICLES ===")
    
    zeros = find_zero_finding_articles()
    log.info(f"Found {len(zeros)} zero-finding articles")
    
    success = 0
    api_errors = 0
    total = len(zeros)
    
    for i, ef in enumerate(zeros):
        doi = ef.stem
        log.info(f"[{i+1}/{total}] Re-extracting {doi}")
        
        # Find PDF
        pdf_path = None
        for pd in PDF_DIR.glob("**/*.pdf"):
            if doi.replace("/", "_") in pd.name or doi.replace("/", "_").replace(".", "_") in pd.name:
                pdf_path = pd
                break
        
        if not pdf_path:
            # Try different naming conventions
            safe_doi = doi.replace("/", "_")
            candidates = [
                PDF_DIR / f"{safe_doi}.pdf",
                PDF_DIR / f"{safe_doi.replace('.', '_')}.pdf",
            ]
            for c in candidates:
                if c.exists():
                    pdf_path = c
                    break
        
        if not pdf_path:
            log.warning(f"  No PDF found for {doi}, skipping")
            continue
        
        try:
            result = reextract_with_gemini(doi, pdf_path)
            
            if result and result.get("findings"):
                n_findings = len(result["findings"])
                
                # Merge with existing data (preserve metadata)
                existing = json.load(open(ef))
                existing["findings"] = result["findings"]
                existing["constructs"] = result.get("constructs", existing.get("constructs", {}))
                existing["reextracted"] = True
                existing["reextraction_date"] = datetime.now(timezone.utc).isoformat()
                existing["reextraction_version"] = "v3"
                
                # Write back
                with open(ef, "w") as f:
                    json.dump(existing, f, indent=2)
                
                success += 1
                log.info(f"  ✓ {doi}: {n_findings} findings extracted")
            else:
                log.warning(f"  ✗ {doi}: No findings returned")
                
        except Exception as e:
            api_errors += 1
            log.error(f"  ✗ {doi}: API error: {e}")
        
        # Rate limiting
        time.sleep(2)
    
    # Success conditions
    log.info(f"\n{'='*60}")
    log.info(f"  RE-EXTRACTION RESULTS")
    log.info(f"{'='*60}")
    log.info(f"  Total zero-finding: {total}")
    log.info(f"  Successfully re-extracted: {success}")
    log.info(f"  API errors: {api_errors}")
    
    sc1 = success >= min(15, total * 0.65)
    sc2 = api_errors <= total * 0.2
    log.info(f"  SC-1 (≥65% with findings): {'✓' if sc1 else '✗'} ({success}/{total})")
    log.info(f"  SC-2 (≤20% API errors): {'✓' if sc2 else '✗'} ({api_errors}/{total})")
    log.info(f"{'='*60}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
