#!/usr/bin/env python3
"""
generate_annotations_llm.py — LLM-Based Annotation Generation (A10-A18)
========================================================================

Runs in BACKGROUND. Generates annotations requiring LLM calls:
  A10 (design_implication): From mechanism + theory data
  A11 (dispute):            From contradictory findings  
  A15 (cross_domain):       From cross-theory pattern analysis
  A16 (historical_context): From theory originator/year data
  A17 (narrative_hook):     From theory summaries
  A18 (unanswered_question): From gap analysis

Uses gemini-2.5-flash. Saves progress incrementally.

Usage:
    PYTHONPATH=. /tmp/panel_venv/bin/python3 scripts/generate_annotations_llm.py &
    # Monitor: tail -f /tmp/llm_gen.log

Success Conditions:
  SC-1: A10 ≥ 20 design implications
  SC-2: A17 ≥ 10 narrative hooks
  SC-3: A18 ≥ 10 unanswered questions
  SC-4: A11 ≥ 5 disputes
  SC-5: A15 ≥ 5 cross-domain connections
  SC-6: A16 ≥ 10 historical contexts

Added: 2026-02-28 (V6 remediation)
"""

import json
import logging
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

EXTRACTIONS_DIR = PROJECT_ROOT / "data" / "extractions"
THEORIES_DIR = PROJECT_ROOT / "data" / "theories"
OUTPUT_DIR = PROJECT_ROOT / "data" / "annotations"
PROGRESS_FILE = OUTPUT_DIR / "llm_generation_progress.json"

# Import validation reflexes
try:
    from src.utils.validation_reflexes import validate_annotation_item, warn
    HAS_REFLEXES = True
except ImportError:
    HAS_REFLEXES = False


def parse_json_response(text):
    """Robustly extract JSON array from LLM response.
    
    Handles: direct JSON, ```json blocks, text preamble, trailing text.
    
    Success condition (inline reflex):
    - Returns list or None, never crashes
    - Logs the failing text snippet on failure for diagnosis
    """
    if not text:
        return None
    text = text.strip()
    
    # Strategy 1: Direct parse
    try:
        r = json.loads(text)
        if isinstance(r, list):
            return r
    except Exception as e:
        logger.debug(f"Non-critical: {e}")
    
    # Strategy 2: Code block extraction (multiple patterns)
    # Handle: ```json\n...\n```, ```\n...\n```, ```json  \n...\n```
    for pat in [r'```json\s*\n(.*?)```', r'```\s*\n(.*?)```']:
        m = re.search(pat, text, re.DOTALL)
        if m:
            candidate = m.group(1).strip()
            try:
                r = json.loads(candidate)
                if isinstance(r, list):
                    return r
            except Exception as e:
                logger.debug(f"Non-critical: {e}")
    
    # Strategy 3: Bracket extraction (find outermost [...])
    start = text.find('[')
    end = text.rfind(']')
    if start >= 0 and end > start:
        try:
            r = json.loads(text[start:end+1])
            if isinstance(r, list):
                return r
        except Exception as e:
            logger.debug(f"Non-critical: {e}")
    
    # Strategy 4: Try after removing common Gemini artifacts
    for prefix in ['Here is the JSON', 'Here are the', 'Below is']:
        if text.lower().startswith(prefix.lower()):
            cleaned = text[text.find('['):]
            if cleaned:
                try:
                    r = json.loads(cleaned[:cleaned.rfind(']')+1])
                    if isinstance(r, list):
                        return r
                except Exception as e:
                    logger.debug(f"Non-critical: {e}")
    
    return None


def call_gemini(prompt, max_retries=3):
    """Call Gemini with retries. Returns raw text."""
    try:
        from google import genai
    except ImportError:
        try:
            import google.genai as genai
        except ImportError:
            logger.error("google-genai not installed")
            return ""
    client = genai.Client()
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config={"temperature": 0.3, "max_output_tokens": 8000}
            )
            return response.text
        except Exception as e:
            wait = 2 ** attempt
            logger.warning(f"Gemini attempt {attempt+1} failed: {e}. Wait {wait}s")
            time.sleep(wait)
    return ""


def save_progress(progress):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f, indent=2)


def load_progress():
    if PROGRESS_FILE.exists():
        try:
            return json.load(open(PROGRESS_FILE))
        except Exception as e:
            logger.debug(f"Non-critical: {e}")
    return {"a10": [], "a11": [], "a15": [], "a16": [], "a17": [], "a18": [],
            "status": "starting"}


def _validate_and_filter(items, annotation_type):
    """Reflex: validate items, return only valid ones."""
    if not HAS_REFLEXES:
        return items
    valid = []
    for item in items:
        ok, msg = validate_annotation_item(item, annotation_type)
        if ok:
            valid.append(item)
        else:
            logger.warning(f"{annotation_type} item rejected: {msg}")
    return valid


def _generate_and_parse(prompt, annotation_type, type_field, progress):
    """Generic: call LLM, parse, validate, save. Returns items added."""
    response = call_gemini(prompt)
    items = parse_json_response(response)
    if items:
        for item in items:
            item["type"] = type_field
        items = _validate_and_filter(items, annotation_type)
        progress.setdefault(annotation_type, []).extend(items)
        logger.info(f"{annotation_type}: {len(items)} items generated")
    else:
        logger.warning(f"{annotation_type} parse failed. Preview: {(response or '')[:200]}")
        items = []
    save_progress(progress)
    return items


# ═══════════════════════════════════════════════════════════════════
# A17: Narrative Hooks
# ═══════════════════════════════════════════════════════════════════

def generate_a17(progress):
    if len(progress.get("a17", [])) > 20:
        logger.info("A17 already done"); return

    theories = []
    for tf in sorted(THEORIES_DIR.glob("*.json")):
        try:
            t = json.load(open(tf))
            name = t.get("name", tf.stem)
            orig = t.get("originator", "")
            constructs = [c.get("construct_name", str(c)) if isinstance(c, dict) else str(c) 
                         for c in t.get("constructs", [])[:3]]
            theories.append(f"- {name} ({orig}): {', '.join(constructs)}")
        except Exception as e:
            logger.debug(f"Non-critical: {e}")

    prompt = f"""You are a science communicator writing for architects.
For each theory, create a compelling narrative hook.

Theories:
{chr(10).join(theories)}

Return a JSON array. Each element:
{{"theory": "name", "hook_type": "counterintuitive_fact|design_failure|human_cost|surprising_connection", "hook": "2-3 vivid sentences", "target_audience": "architect|designer|researcher"}}

IMPORTANT: Return ONLY a valid JSON array starting with [ and ending with ]. No markdown, no code fences, no explanation."""

    _generate_and_parse(prompt, "a17", "narrative_hook", progress)


# ═══════════════════════════════════════════════════════════════════
# A18: Unanswered Questions
# ═══════════════════════════════════════════════════════════════════

def generate_a18(progress):
    if len(progress.get("a18", [])) > 20:
        logger.info("A18 already done"); return

    theories = []
    for tf in sorted(THEORIES_DIR.glob("*.json"))[:15]:
        try:
            theories.append(json.load(open(tf)).get("name", tf.stem))
        except Exception as e:
            logger.debug(f"Non-critical: {e}")

    sample = []
    for ef in sorted(EXTRACTIONS_DIR.glob("10.*.json"))[:30]:
        try:
            for f in json.load(open(ef)).get("findings", [])[:1]:
                sample.append(f"{f.get('antecedent','')[:50]} → {f.get('consequent','')[:50]}")
        except Exception as e:
            logger.debug(f"Non-critical: {e}")

    prompt = f"""You are a research strategist for an architectural cognition lab.
Theories: {', '.join(theories)}
Sample findings: {'; '.join(sample[:15])}

Identify 20 UNANSWERED research questions about built environments and human cognition/emotion.

Return a JSON array. Each element:
{{"question": "one sentence", "estimated_difficulty": "feasible_now|needs_new_methods|decade_scale", "why_important": "one sentence", "what_would_it_take": "one sentence", "related_theories": ["theory1", "theory2"]}}

IMPORTANT: Return ONLY a valid JSON array starting with [ and ending with ]. No markdown, no code fences, no explanation."""

    _generate_and_parse(prompt, "a18", "unanswered_question", progress)


# ═══════════════════════════════════════════════════════════════════
# A11: Disputes
# ═══════════════════════════════════════════════════════════════════

def generate_a11(progress):
    if len(progress.get("a11", [])) > 10:
        logger.info("A11 already done"); return

    a9_path = OUTPUT_DIR / "a9_surprise_flags.json"
    if not a9_path.exists():
        logger.warning("No A9 data"); return

    surprises = json.load(open(a9_path))[:15]
    surprise_text = "\n".join(
        f"- Contradicts majority: {s.get('actual_finding','')[:120]}"
        for s in surprises
    )

    prompt = f"""You are a philosophy of science analyst. These findings contradict majority views:

{surprise_text}

For each genuine disagreement, create a dispute entry.

Return a JSON array. Each element:
{{"claim": "contested claim", "positions": [{{"position": "view A", "proponents": ["Name1", "Name2"]}}, {{"position": "view B", "proponents": ["Name3", "Name4"]}}], "status": "active|emerging|resolving", "what_would_resolve": "one sentence", "implications_for_design": "one sentence"}}

IMPORTANT: Return ONLY a valid JSON array starting with [ and ending with ]. No markdown, no code fences, no explanation."""

    _generate_and_parse(prompt, "a11", "dispute", progress)


# ═══════════════════════════════════════════════════════════════════
# A15: Cross-Domain Connections
# ═══════════════════════════════════════════════════════════════════

def generate_a15(progress):
    """Generate cross-domain analogies from cross-theory patterns."""
    if len(progress.get("a15", [])) > 10:
        logger.info("A15 already done"); return

    # Build theory + construct data
    theory_data = []
    for tf in sorted(THEORIES_DIR.glob("*.json")):
        try:
            t = json.load(open(tf))
            name = t.get("name", tf.stem)
            constructs = [c.get("construct_name", str(c)) if isinstance(c, dict) else str(c) 
                         for c in t.get("constructs", [])[:5]]
            ff = t.get("function_form", {})
            equation = ff.get("function_form", "") if isinstance(ff, dict) else ""
            theory_data.append(f"- {name}: constructs={', '.join(constructs)}; equation={equation[:80]}")
        except Exception as e:
            logger.debug(f"Non-critical: {e}")

    prompt = f"""You are an interdisciplinary research analyst. These theories are all about how built environments affect humans:

{chr(10).join(theory_data)}

Find cross-domain connections — places where mechanisms from one field illuminate another.
Examples: acoustics ↔ thermal comfort, wayfinding ↔ stress, lighting ↔ circadian ↔ productivity.

Return a JSON array of 15 connections. Each element:
{{"domain_a": "theory/field name", "domain_b": "theory/field name", "connection_type": "shared_mechanism|analogous_math|complementary_effects|competing_predictions", "description": "2-3 sentences explaining the connection", "design_implication": "one sentence about what this means for architects", "confidence": "high|medium|low"}}

IMPORTANT: Return ONLY a valid JSON array starting with [ and ending with ]. No markdown, no code fences, no explanation."""

    _generate_and_parse(prompt, "a15", "cross_domain_connection", progress)


# ═══════════════════════════════════════════════════════════════════
# A16: Historical Context
# ═══════════════════════════════════════════════════════════════════

def generate_a16(progress):
    """Generate historical context for each theory."""
    if len(progress.get("a16", [])) > 10:
        logger.info("A16 already done"); return

    theories = []
    for tf in sorted(THEORIES_DIR.glob("*.json")):
        try:
            t = json.load(open(tf))
            theories.append({
                "name": t.get("name", tf.stem),
                "originator": t.get("originator", "unknown"),
                "year": t.get("year", "unknown"),
            })
        except Exception as e:
            logger.debug(f"Non-critical: {e}")

    theory_text = "\n".join(
        f"- {t['name']} by {t['originator']} ({t['year']})"
        for t in theories
    )

    prompt = f"""You are a historian of environmental psychology and architectural science.
For each theory below, provide historical context: what problem it solved, what it replaced, 
and how it influenced practice.

Theories:
{theory_text}

Return a JSON array. Each element:
{{"theory": "name", "historical_problem": "what gap/debate led to this theory (1-2 sentences)", "predecessor": "what theory/view it replaced or extended", "year_range": "decade when most influential", "key_turning_point": "specific study or event that established the theory", "legacy": "how it changed architectural practice (1 sentence)", "current_status": "foundational|actively_debated|being_superseded|niche"}}

IMPORTANT: Return ONLY a valid JSON array starting with [ and ending with ]. No markdown, no code fences, no explanation."""

    _generate_and_parse(prompt, "a16", "historical_context", progress)


# ═══════════════════════════════════════════════════════════════════
# A10: Design Implications
# ═══════════════════════════════════════════════════════════════════

def generate_a10(progress):
    if len(progress.get("a10", [])) > 50:
        logger.info("A10 already done"); return

    mechanisms = []
    for ef in sorted(EXTRACTIONS_DIR.glob("10.*.json"))[:200]:
        try:
            for f in json.load(open(ef)).get("findings", []):
                mech = f.get("mechanism")
                if mech and isinstance(mech, str) and len(mech) > 20:
                    mechanisms.append({
                        "mechanism": mech[:200],
                        "antecedent": f.get("antecedent", "")[:80],
                        "consequent": f.get("consequent", "")[:80],
                        "paper_id": ef.stem,
                    })
        except Exception as e:
            logger.debug(f"Non-critical: {e}")

    if not mechanisms:
        logger.warning("No mechanisms for A10"); return

    a10_results = progress.get("a10", [])
    for i in range(0, min(len(mechanisms), 100), 10):
        batch = mechanisms[i:i+10]
        mech_text = "\n".join(
            f"{j+1}. {m['mechanism'][:150]} (Finding: {m['antecedent']} → {m['consequent']})"
            for j, m in enumerate(batch)
        )

        prompt = f"""You are an architectural design consultant. For each mechanism, generate a design implication.

Mechanisms:
{mech_text}

Return a JSON array. Each element:
{{"parameter": "measurable_parameter", "value": "recommended_value", "unit": "measurement_unit", "context": "when this applies (max 50 words)", "confidence": "high|medium|low", "mechanism_summary": "one sentence (max 30 words)"}}

IMPORTANT: Return ONLY a valid JSON array starting with [ and ending with ]. No markdown, no code fences, no explanation."""

        response = call_gemini(prompt)
        items = parse_json_response(response)
        if items:
            for item in items:
                item["type"] = "design_implication"
                item["paper_id"] = batch[0]["paper_id"] if batch else ""
            items = _validate_and_filter(items, "a10")
            a10_results.extend(items)
            logger.info(f"A10 batch {i}: {len(items)} items")
        else:
            logger.warning(f"A10 batch {i} parse failed")

        progress["a10"] = a10_results
        save_progress(progress)
        time.sleep(1)

    logger.info(f"A10 total: {len(a10_results)}")


# ═══════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════

def main():
    logger.info("Starting A10-A18 LLM generation (enhanced)")
    progress = load_progress()
    progress["status"] = "running"
    progress["started_at"] = datetime.now(timezone.utc).isoformat()
    save_progress(progress)

    try:
        generate_a17(progress)     # Smallest — quick win
        generate_a18(progress)     # Gap analysis
        generate_a15(progress)     # Cross-domain (NEW)
        generate_a16(progress)     # Historical context (NEW)
        generate_a11(progress)     # Disputes
        generate_a10(progress)     # Largest — many batches
    except Exception as e:
        logger.error(f"Fatal: {e}", exc_info=True)
        progress["status"] = "error"
        progress["error"] = str(e)
        save_progress(progress)
        return 1

    progress["status"] = "complete"
    progress["completed_at"] = datetime.now(timezone.utc).isoformat()

    sc = [
        ("A10 ≥ 20", len(progress.get("a10", [])) >= 20, len(progress.get("a10", []))),
        ("A17 ≥ 10", len(progress.get("a17", [])) >= 10, len(progress.get("a17", []))),
        ("A18 ≥ 10", len(progress.get("a18", [])) >= 10, len(progress.get("a18", []))),
        ("A11 ≥ 5",  len(progress.get("a11", [])) >= 5,  len(progress.get("a11", []))),
        ("A15 ≥ 5",  len(progress.get("a15", [])) >= 5,  len(progress.get("a15", []))),
        ("A16 ≥ 10", len(progress.get("a16", [])) >= 10, len(progress.get("a16", []))),
    ]

    all_pass = all(p for _, p, _ in sc)
    progress["success_conditions"] = {n: {"passed": p, "count": c} for n, p, c in sc}
    progress["all_conditions_met"] = all_pass

    # Save individual annotation files
    type_names = {
        "a10": "design_implications", "a11": "disputes", 
        "a15": "cross_domain_connections", "a16": "historical_contexts",
        "a17": "narrative_hooks", "a18": "unanswered_questions",
    }
    for atype, fname in type_names.items():
        data = progress.get(atype, [])
        if data:
            with open(OUTPUT_DIR / f"{atype}_{fname}.json", "w") as f:
                json.dump(data, f, indent=2)

    save_progress(progress)
    logger.info("=" * 60)
    logger.info("  A10-A18 LLM GENERATION COMPLETE")
    for n, p, c in sc:
        logger.info(f"  {'✓' if p else '✗'} {n}: {c}")
    logger.info(f"  {'✅ ALL PASS' if all_pass else '⚠️ SOME FAILED'}")
    logger.info("=" * 60)
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
