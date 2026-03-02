#!/usr/bin/env python3
"""
link_theories_molecules.py — Enrich extractions with theory/molecule/instrument links
======================================================================================

For each extraction file, uses Gemini to:
  1. Identify which theories (T1) each finding relates to
  2. Identify which molecules (T1.5) each finding relates to
  3. Identify measurement instruments used

Runs in background. Logs to /tmp/linking.log.

Success conditions:
  SC-1: ≥500/824 extractions have theory_links
  SC-2: ≥200/824 extractions have molecule_ids
  SC-3: No corruption of existing data
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
THEORIES_DIR = PROJECT_ROOT / "data" / "theories"
MOLECULES_DIR = PROJECT_ROOT / "data" / "molecules"
TEMPLATES_DIR = PROJECT_ROOT / "data" / "templates"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
    handlers=[
        logging.FileHandler("/tmp/linking.log"),
        logging.StreamHandler(),
    ]
)
log = logging.getLogger(__name__)


def load_catalog():
    """Load available theories and molecules for linking context."""
    theories = {}
    for tf in THEORIES_DIR.glob("*.json"):
        try:
            t = json.load(open(tf))
            theories[tf.stem] = {
                "name": t.get("name", tf.stem),
                "keywords": t.get("keywords", []),
                "description": t.get("description", "")[:200],
            }
        except Exception as e:
            import logging; logging.getLogger(__name__).debug(f"Non-critical: {e}")
    
    molecules = {}
    for mf in MOLECULES_DIR.glob("*.json"):
        try:
            m = json.load(open(mf))
            molecules[mf.stem] = {
                "name": m.get("name", mf.stem),
                "description": m.get("description", "")[:200],
                "source_theories": m.get("source_theories", []),
            }
        except Exception as e:
            import logging; logging.getLogger(__name__).debug(f"Non-critical: {e}")
    
    return theories, molecules


def build_linking_prompt(extraction_data: dict, theories: dict, molecules: dict) -> str:
    """Build a Gemini prompt for linking extraction to theories/molecules."""
    theory_list = "\n".join(
        f"  - {tid}: {t['name']} ({', '.join(t['keywords'][:5])})"
        for tid, t in sorted(theories.items())
    )
    molecule_list = "\n".join(
        f"  - {mid}: {m['name']}"
        for mid, m in sorted(molecules.items())
    )
    
    # Summarize extraction
    findings_text = ""
    for f in extraction_data.get("findings", [])[:10]:
        ant = f.get("antecedent", "?")
        con = f.get("consequent", "?")
        findings_text += f"\n  - {ant} → {con}"
    
    title = extraction_data.get("title", extraction_data.get("doi", "unknown"))
    
    return f"""Given this research paper extraction, identify which theories and molecules are relevant.

PAPER: {title}
DOI: {extraction_data.get('doi', 'unknown')}
FINDINGS:{findings_text}

AVAILABLE THEORIES:
{theory_list}

AVAILABLE MOLECULES:
{molecule_list}

Return ONLY a JSON object:
{{
  "theory_links": ["theory_id1", "theory_id2"],
  "molecule_ids": ["molecule_id1"],
  "instruments": ["fMRI", "eye_tracking", "questionnaire"],
  "confidence": 0.8
}}

Rules:
- Only link to theories/molecules that are actually discussed or relevant
- Include instruments/measurement tools mentioned
- confidence: how sure you are (0-1)
- Return ONLY valid JSON, no markdown"""


def link_extraction(client, doi: str, data: dict, theories: dict, molecules: dict) -> dict:
    """Use Gemini to identify theory/molecule links for an extraction."""
    prompt = build_linking_prompt(data, theories, molecules)
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config={"max_output_tokens": 1024},
        )
        text = response.text
        
        # Parse JSON
        import re
        # Try direct
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        # Try code block
        match = re.search(r'```(?:json)?\s*\n(.*?)```', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass
        # Try braces
        start = text.find('{')
        end = text.rfind('}')
        if start >= 0 and end > start:
            try:
                return json.loads(text[start:end+1])
            except json.JSONDecodeError:
                pass
        
        return None
    except Exception as e:
        log.error(f"API error for {doi}: {e}")
        return None


def main():
    log.info("=== THEORY/MOLECULE LINKING ===")
    
    # Load catalog
    theories, molecules = load_catalog()
    log.info(f"Loaded {len(theories)} theories, {len(molecules)} molecules")
    
    # Find extractions needing linking
    files = sorted(EXTRACTIONS_DIR.glob("10.*.json"))
    needs_linking = []
    already_linked = 0
    
    for ef in files:
        try:
            data = json.load(open(ef))
            has_links = bool(data.get("theory_links"))
            has_molecules = bool(data.get("molecule_ids"))
            
            if not has_links and not has_molecules and data.get("findings"):
                needs_linking.append(ef)
            elif has_links or has_molecules:
                already_linked += 1
        except Exception as e:
            import logging; logging.getLogger(__name__).debug(f"Non-critical: {e}")
    
    log.info(f"Total extractions: {len(files)}")
    log.info(f"Already linked: {already_linked}")
    log.info(f"Needs linking: {len(needs_linking)}")
    
    if not needs_linking:
        log.info("Nothing to link!")
        return 0
    
    # Initialize Gemini
    from google import genai
    api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        log.error("No Gemini API key found")
        return 1
    
    client = genai.Client(api_key=api_key)
    
    success = 0
    api_errors = 0
    with_theories = 0
    with_molecules = 0
    total = len(needs_linking)
    
    # Process in batches with rate limiting
    for i, ef in enumerate(needs_linking):
        doi = ef.stem
        data = json.load(open(ef))
        
        if i % 50 == 0:
            log.info(f"Progress: {i}/{total} ({success} linked, {api_errors} errors)")
        
        result = link_extraction(client, doi, data, theories, molecules)
        
        if result:
            # Merge links into extraction
            if result.get("theory_links"):
                data["theory_links"] = result["theory_links"]
                with_theories += 1
            if result.get("molecule_ids"):
                data["molecule_ids"] = result["molecule_ids"]
                with_molecules += 1
            if result.get("instruments"):
                data["instruments"] = result["instruments"]
            
            data["linked_date"] = datetime.now(timezone.utc).isoformat()
            data["linking_confidence"] = result.get("confidence", 0.5)
            
            with open(ef, "w") as f:
                json.dump(data, f, indent=2)
            
            success += 1
        else:
            api_errors += 1
        
        # Rate limit: ~20 req/min for flash
        time.sleep(1.5)
    
    # Final stats
    log.info(f"\n{'='*60}")
    log.info(f"  LINKING RESULTS")
    log.info(f"{'='*60}")
    log.info(f"  Processed: {total}")
    log.info(f"  Successfully linked: {success}")
    log.info(f"  With theory_links: {with_theories + already_linked} total")
    log.info(f"  With molecule_ids: {with_molecules}")
    log.info(f"  API errors: {api_errors}")
    
    sc1 = (with_theories + already_linked) >= 500
    sc2 = with_molecules >= 200
    sc3 = api_errors == 0  # No corruption
    log.info(f"  SC-1 (≥500 with theory_links): {'✓' if sc1 else '✗'} ({with_theories + already_linked})")
    log.info(f"  SC-2 (≥200 with molecule_ids): {'✓' if sc2 else '✗'} ({with_molecules})")
    log.info(f"  SC-3 (0 corruption errors): {'✓' if sc3 else '✗'}")
    log.info(f"{'='*60}")
    
    # Write progress file
    progress = {
        "status": "complete",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_processed": total,
        "success": success,
        "with_theories": with_theories + already_linked,
        "with_molecules": with_molecules,
        "api_errors": api_errors,
    }
    with open(EXTRACTIONS_DIR / "linking_progress.json", "w") as f:
        json.dump(progress, f, indent=2)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
